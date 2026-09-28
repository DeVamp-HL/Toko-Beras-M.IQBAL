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
//  - PUTARAN 15 (wadah DIJUAL, keputusan owner 17 Sep): jalur Wadah = kantong kemasan & karung bekas sebagai BARANG (jenis 'wadah', baris nota
//    sendiri, menambah omzet, buku kantong dipotong lewat dokumen `pakai` id+1); di Repack wadahnya dipilih (merek → ukuran), lembarnya bebas,
//    DIJUAL (baris sendiri) atau DITANGGUNG toko (masuk HPP baris repack seperti biayaKemasanLiteran), upah repack per nota melekat ke baris
//    repack (upahRepack, ikut hargaTotal seperti pembulatan). Logikanya di wadah-jual-logika.js; struknya di struk-logika.js.
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanLiteran, hitungPiutang, stokMaksJalur, pembulatanTunai } from '../mesin/beku.js';
import { kunciKemasan, kunciPelanggan, bulatKeAtas500, bakuCaraBayar, merkPunyaKarungBerat, hargaKarungUtuh, cariHargaKarungPerKg,
  tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan,
  pesananBelumTuntas, RASIO_KONVERSI, RASIO_DEFAULT, NEGO_LANTAI } from '../mesin/pembantu.js';
import { ambilHargaKemasan, ambilHargaLiteran, ambilPenjualan, ambilPenjualanSemua, ambilPelangganCatatan, ambilPesanan, ambilRetur, ambilWadahLiteran, ambilPenyesuaianStok, ambilProduksiBerlaku, setelKeranjang,
  wzDiKeranjangParkir, sumberData, cacheMentah, ambilSemuaBatch, stokMerekSaja, petaBukuWadah, kunciBukuAdukan, petaUkuran, indukTerpisah, ambilPenyesuaianKemasan } from '../data/toko.js';
import { hariIniIso, RP, tanggalPendek } from '../inti/format.js';
import { returAwal, cekDrafTukar, dokumenKarantina, cekSusulan } from './retur-logika.js';
import { tkSetTertaut } from '../mesin/pembantu.js';
import { susunRakWadah, bangunBarisWadah, biayaWadahRepack, koleksiWadah, jenisWadah, bebasWadah } from './wadah-jual-logika.js';
// putaran 27: wadah bernama, isi per merek asal
import { wbDariWadah, wbPecahanBaris, wbBagianMerk, wbKomposisi, wbPecah, wbModalPerKg, wbRasio, wbMerkCadangan, wbLiteranLangsung, MEREK_KARUNG_BAWAAN } from './wadah-bernama-logika.js';
// putaran 28: wadah punya stok sendiri
import { wbAktif, wbKunci, wbDokLahir, wbDokPindah } from './wadah-bernama-logika.js';
import { arPeta, arBeras, arKemasan } from './arsip-logika.js';
import { skChip, skTrxPegang, skPecah, skHapusPemecah } from './setengah-logika.js';
import { gabungTakaran } from './struk-logika.js';

export const JALUR = [['sering', 'Sering'], ['literan', 'Literan'], ['kemasan', 'Kemasan'], ['karung', 'Karung'], ['wadah', 'Wadah'], ['repack', 'Repack'], ['retur', 'Retur'], ['riwayat', 'Riwayat']];   // riwayat: owner 28 Sep
export const JALUR_NANTI = [];   // semua jalur desain sudah hidup (wadah: putaran 15)
export const PECAHAN = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500];
// ---------- WADAH LITERAN (kotak kayu) — praktik lapangan, keterangan owner 13–14 Sep & koreksi 19 Sep 2026 ----------
// Rantai berasnya di toko:  TUMPUKAN karung 50 kg di gudang → satu KARUNG TERBUKA di belakang wadah ("stok wadah") → KOTAK WADAH → dijual per liter.
// Wadah diisi ulang TAKAR demi TAKAR (serok 1,8 kg) dari karung terbuka; boleh dicampur beberapa merek dengan perbandingan (2:1, 1:1, …).
// Rata sejajar bibir kotak = 50 kg; di atas itu MENGGUNUNG sampai ±60 kg; diisi ulang begitu berkurang ±40 kg.
// Literan lain (ketan dll.) diserok langsung dari karung → bukan wadah.
// Semua angka di bawah adalah KEBIJAKAN owner — bawaan saja; yang berlaku diatur owner dari layar Stok → Wadah literan.
export const DAFTAR_WADAH = ['Angsa', 'IR64 Elevate', 'Perahu Layar', 'IR64 Apex', 'IR42 Select', 'IR42 Value', 'Pandan Wangi', 'IR64 Ascent'];
export const WADAH_PENUH_KG = 50;        // beras RATA sejajar bibir kotak
export const WADAH_PUNCAK_KG = 60;       // batas menggunung — lebih dari ini tidak muat
export const WADAH_ISI_ULANG_KG = 10;    // tersisa segini (sudah berkurang ±40 kg) → saatnya isi ulang
export const WADAH_TAKAR_KG = 1.8;       // satu serok logam
export const KARUNG_BELAKANG_KG = 50;    // satu karung utuh yang dibuka di belakang wadah
export const WADAH_MAKS_RESEP = 6;       // paling banyak enam karung berbeda dalam satu campuran
export const WADAH_SISIH_KG = 10;       // putaran 28 (owner 28 Sep): tutup toko → ±10 kg dari yang menggunung disisihkan ke karung wadah (diatur owner)
export const WADAH_SUSUT_WAJAR_KG = 1;   // putaran 27 (owner 27 Sep): susut takar wajar per wadah per hari saat dicocokkan — di atasnya wajib alasan (diatur owner)
export const STATUS_PESANAN = { dipesan: 'DIPESAN', diantar: 'DIANTAR', dibayar: 'DIBAYAR', batal: 'BATAL' };

export function keadaanAwal() {
  return {
    jalur: 'sering', lembar: null, pilih: null, ketik: '', satuanKarung: 50, namaRepack: '',
    rwCari: '', rwPeriode: 'semua', rwJenis: '', rwCara: '', rwBatal: false, rwN: 50, rwBuka: null,   // RIWAYAT PENJUALAN (owner 28 Sep): saringan tab Riwayat (riwayat-logika.js)
    keranjang: [], negoId: null, potongan: 0, penggantiTanya: null,
    pelanggan: '', cariPelanggan: '', cara: 'Tunai', uang: 0,
    antrean: [], aktifId: 1, idBerikut: 2, urutBaris: 0,
    kreditDibuka: false, notaTerakhir: null,
    pesananId: null, psNama: '', psIsi: '', psAlamat: '', psNilai: '', psSaring: '',
    tukar: null,   // PUTARAN 4: { returDraf, kredit, ringkas } — retur tukar yang diikat ke keranjang ini (_tukarKeJual index.html 16838); PUTARAN 20: { susulanReturId, kredit 0, … } = pengganti tukar yatim
    karcis: null,  // PUTARAN 20: karcis kasir darurat / nota perlu-dirapikan yang sedang dirinci lewat keranjang ini (karcis-logika.js)
    tembusTanya: null, tembusYakin: false,   // PUTARAN 31b: jual dulu, tandai untuk dicocokkan (owner, ketukan kedua)
    kcPilih: null, // PUTARAN 31.1: tebakan karcis yang namanya seharga dan sedang ditanyakan (karcis-logika kelompokkanTebakan)
    kcBatal: null, // PUTARAN 25b: { id, alasan } — karcis kasir darurat yang sedang dibatalkan dari lembar Karcis (karcis-logika susunBatalKarcis)
    // PUTARAN 15: isian repack (wadah dipilih, lembar, dijual/ditanggung, upah) & struk (nota yang dibuka, timpaan kertas/sertakan, draf setelan)
    rpWadah: '', rpLembar: '', rpDijual: true, rpUpah: '', setengahHarga: '', arYakin: '',
    strukKunci: null, strukKertas: null, strukSertakan: null, aturStruk: null, aturWadah: null,
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
  const rak = { karung: [], kemasan: [], literan: [], repack: [], wadah: [] };
  const arsip = arPeta();   // putaran 27 (Bagian 3): nama yang diarsipkan owner tidak tampil di rak (baris saring jenis & Sering ikut, karena turunan rak)
  const wadahDaftar = aturWadah().daftar; const literanLangsung = wbLiteranLangsung().daftar;
  // putaran 27 (Bagian 5): WADAH = tempat bernama; harga per liter melekat pada wadah (katalogHargaLiteran ber-id nama wadah); isinya boleh dari beberapa
  // merek — terjual → buku merek-merek asal dipotong sebanding komposisi; modal per kg = rata-rata tertimbang isi wadah
  wadahDaftar.forEach((W) => { const hl = hargaLiteran.find((x) => x.merk === W); if (!hl || !(hl.hargaPerLiter > 0)) return; const rasio = wbRasio(W); const sisaL = bebasLiterWadah(W, rasio, s);
    rak.literan.push({ jalur: 'literan', kunci: W, nama: W, ukuran: 'per liter · wadah', harga: hl.hargaPerLiter, satuan: 'L', rasio, sisa: sisaL, sisaTeks: '±' + sisaL.toString().replace('.', ',') + ' L', hppPerKg: wbModalPerKg(W, s),
      wadahLiteran: true, dipegang: 0 }); });
  // putaran 28: buku stok WADAH bukan merek karung — tidak dijual per karung / repack / literan langsung (literannya lewat chip wadah di atas)
  // putaran 28 (owner 28 Sep): karung 25 kg merek dua ukuran dijual dari bukunya sendiri 'Merek 25 kg' (harga = katalog merek induk ukuran itu);
  // buku merek induk yang sudah dipisah tidak lagi menawarkan ukuran itu
  const ukuran = petaUkuran(); const terpisah = indukTerpisah();
  Object.keys(stokMerekSaja(stokKarung)).sort().forEach((merk) => {
    if (arBeras(merk, arsip)) return;
    const uk = ukuran[merk]; const hgNama = uk ? uk.induk : merk;
    [50, 25].forEach((berat) => {
      if (uk ? berat !== uk.berat : !!(terpisah[merk] && terpisah[merk][berat])) return;
      if (!merkPunyaKarungBerat(merk, berat)) return;
      const hg = hargaKarungUtuh(hgNama, berat);
      if (!hg || !hg.perUnit) return;
      setelBeratDom(berat);
      const maks = stokMaksJalur('karung', merk);   // sudah dikurangi keranjang aktif + yang diparkir
      rak.karung.push({ jalur: 'karung', kunci: merk, nama: hgNama, ukuran: berat + ' kg', harga: hg.perUnit, satuan: 'karung', indukUkuran: uk ? uk.induk : '',
        berat, sisa: maks === null ? 0 : maks, sisaTeks: (maks === null ? 0 : maks) + ' karung', hppPerKg: stokKarung[merk].hppTerakhirPerKg || 0,
        dipegang: wzDiKeranjangParkir('karung', merk) });
    });
    // putaran 27 (Bagian 5): literan per MEREK hanya untuk merek yang dijual literan LANGSUNG dari karungnya; literan wadah = chip per wadah (di bawah)
    const hl = literanLangsung.indexOf(merk) >= 0 ? hargaLiteran.find((x) => x.merk === merk) : null;
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
    const st = stokKemasan[kunci]; if (arKemasan(st.namaProduk, st.ukuranKemasan, arsip)) return;
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
  // WADAH sebagai barang (putaran 15): hanya jenis berharga jual; sisa = buku − lembar yang dipegang keranjang aktif & struk parkir
  rak.wadah = susunRakWadah((j) => wadahDipegang(j), (j) => wadahDipegangParkir(j));
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
  if (p.jenis === 'literan') return 'literan|' + (p.dariWadah || p.merkSumber);   // putaran 27: literan wadah dikenali dari wadahnya
  if (p.jenis === 'repacking') return 'repack|' + p.merkSumber;
  if (p.jenis === 'wadah') return 'wadah|' + p.jenisWadah;
  return null;
}
function susunSering(s, rak) {
  const semua = [].concat(rak.karung.map((c) => Object.assign({}, c, { id: 'karung|' + c.kunci + '|' + c.berat })),
    rak.kemasan.map((c) => Object.assign({}, c, { id: 'kemasan|' + c.kunci })),
    rak.literan.map((c) => Object.assign({}, c, { id: 'literan|' + c.kunci })),
    rak.repack.map((c) => Object.assign({}, c, { id: 'repack|' + c.kunci })),
    rak.wadah.map((c) => Object.assign({}, c, { id: 'wadah|' + c.kunci })));
  const peta = {}; semua.forEach((c) => { peta[c.id] = c; });
  const k = kunciPelanggan(s.pelanggan);
  const hari = hariIniIso(s.sekarang);
  const batas = geser(hari, k ? -90 : -28);
  const hitung = {}; const takaran = {};
  ambilPenjualan().forEach((p) => {
    if ((p.tanggal || '') < batas) return;
    if (k && kunciPelanggan(p.namaPelanggan) !== k) return;
    if (p.takaranId) { if (takaran[p.takaranId]) return; takaran[p.takaranId] = 1; }   // putaran 27: baris internal satu takaran dihitung sekali
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
    // putaran 27 (Bagian 4): ½ karung — 1 × 25 kg dipecah dari kemasan 50 kg saat nota dicatat (modal = ½ modal 50 kg, pasti dihitung penyusun adukan)
    if (chip.setengahDari) { if (bonus || j !== 1) return null; t.setengahDari = chip.setengahDari; if (chip.setengahHargaBaru > 0) t.setengahHargaBaru = chip.setengahHargaBaru; t.label = chip.nama + ' 25 kg (½ dari 50 kg)'; }
  } else if (chip.jalur === 'literan') {
    const rasio = chip.rasio || rasioMerk(chip.kunci);
    const totalKg = Math.round(j * rasio * 1000) / 1000;
    const jenisK = tentukanKemasanLiteran(j); const nK = jenisK ? jumlahKemasanLiteran(j) : 0;
    const biayaK = jenisK ? hargaBahanLiteranEfektif(jenisK, hitungStokBahanLiteran()) * nK : 0;
    t = { jenis: 'literan', merkSumber: chip.kunci, namaProduk: chip.kunci, jumlahLiter: j, rasioPakai: rasio, totalKg,
      hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg) + biayaK, kemasanLiteran: jenisK, biayaKemasanLiteran: biayaK,
      jumlahKemasanLiteranDipakai: nK, label: chip.nama + ' literan', satuan: 'L' };
    // putaran 27 (Bagian 5): literan dari WADAH — nama tampil = wadah, buku dipotong dari merek asal sebanding komposisi SAAT INI (pecahan = perkiraan untuk
    // langit-langit stok; pemecahan pastinya dihitung ulang saat nota dicatat), modal = Σ kg tiap merek asal × modalnya
    if (chip.wadahLiteran) { const pc = wbPecah(chip.kunci, totalKg, s && s.keranjang ? s : null); const stok = hitungStokKarungPerMerk();
      t.dariWadah = chip.kunci; t.pecahan = pc.bagian; t.merkSumber = pc.bagian.length ? pc.bagian[0].merk : wbMerkCadangan(chip.kunci);
      t.hppTotalSaatJual = Math.round(pc.bagian.reduce((a, x) => a + x.kg * ((stok[x.merk] || {}).hppTerakhirPerKg || 0), 0)) + biayaK; }
  } else if (chip.jalur === 'repack') {
    const nama = String(e.namaProduk !== undefined ? e.namaProduk : (s && s.namaRepack) || '').trim() || chip.nama;
    t = { jenis: 'repacking', merkSumber: chip.kunci, namaProduk: nama, totalKg: j, hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * j),
      label: 'Repack ' + nama, satuan: 'kg' };
    // wadah DITANGGUNG toko: biayanya masuk HPP baris ini (pola biayaKemasanLiteran), bukunya dipotong saat nota dicatat (dokumen pakai id+1)
    if (e.kemasanRepack && e.jumlahKemasanRepack > 0 && jenisWadah(e.kemasanRepack)) {
      const b = biayaWadahRepack(e.kemasanRepack, e.jumlahKemasanRepack);
      t.kemasanRepack = e.kemasanRepack; t.jumlahKemasanRepackDipakai = b.lembar; t.biayaKemasanRepack = b.biaya; t.hppTotalSaatJual += b.biaya;
    }
    // upah repack per nota (owner 16 Sep: fleksibel, boleh nol) — melekat ke baris repack & ikut hargaTotal, seperti pembulatan
    if (Math.round(Number(e.upahRepack) || 0) > 0) t.upahRepack = Math.round(Number(e.upahRepack));
  } else if (chip.jalur === 'wadah') {
    if (j % 1 !== 0) return null;
    t = bangunBarisWadah(chip, j);
  }
  if (!t) return null;
  t.jumlah = j; t.hargaAsli = chip.harga; t.hargaSatuan = e.nego ? e.hargaSatuan : chip.harga; if (e.nego) t.nego = true;
  return selesaikanHarga(t, !!e.penggantiRetur);
}
/** Uang baris dari harga satuan × jumlah bayar; pengganti retur → nilai jadi jejak, hargaTotal 0. */
function selesaikanHarga(t, penggantiRetur) {
  const nilai = Math.round(t.hargaSatuan * t.jumlah) + (t.upahRepack || 0);
  if (penggantiRetur) { t.penggantiRetur = true; t.nilaiBarangPengganti = nilai; t.hargaTotal = 0; }
  else { delete t.penggantiRetur; delete t.nilaiBarangPengganti; t.hargaTotal = nilai; }
  return t;
}
const benderaBaris = (t) => ({ bonusUnit: t.bonusUnit || 0, penggantiRetur: !!t.penggantiRetur, namaProduk: t.jenis === 'repacking' ? t.namaProduk : undefined, hargaSatuan: t.hargaSatuan, nego: !!t.nego,
  kemasanRepack: t.kemasanRepack, jumlahKemasanRepack: t.jumlahKemasanRepackDipakai, upahRepack: t.upahRepack });
/** Yang harus tersedia di stok untuk baris ini (kemasan: unit bayar + bonus). */
const butuhStok = (t) => t.jenis === 'kemasan' ? t.jumlah + (t.bonusUnit || 0) : t.jumlah;

/** Langit-langit stok untuk chip ini SEKARANG (keranjang aktif + parkir sudah dikurangi oleh mesin). */
export function maksUntuk(chip) {
  if (chip.jalur === 'karung') { setelBeratDom(chip.berat); return stokMaksJalur('karung', chip.kunci); }
  if (chip.jalur === 'kemasan') return stokMaksJalur('kemasan', chip.kunci);
  if (chip.jalur === 'literan') return chip.wadahLiteran ? bebasLiterWadah(chip.kunci, chip.rasio, { keranjang: _keranjangKini, antrean: _antreanKini }) : bebasLiter(chip.kunci, chip.rasio || rasioMerk(chip.kunci));
  if (chip.jalur === 'repack') return bebasKg(chip.kunci);
  if (chip.jalur === 'wadah') return bebasWadah(chip.kunci, wadahDipegang(chip.kunci));   // null = hasil samping, tidak dibatasi buku
  return null;
}
/** Liter yang bebas dijual: kolam kg merek itu dikurangi yang dipegang struk parkir & keranjang aktif (kolam yang sama dengan karung). */
function bebasLiter(merk, rasio) {
  const sisaKg = (hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0;
  const dipakai = wzDiKeranjangParkir('karung', merk) + jumlahAktifKg(merk);
  return Math.max(0, Math.floor((sisaKg - dipakai) / rasio * 10) / 10);
}
/**
 * putaran 27: liter yang bebas dijual dari WADAH W — tiap liter memotong buku merek asal sebanding komposisi isi (bagian positif), jadi yang membatasi = merek
 * yang bukunya paling cepat habis dibanding bagiannya: kg ≤ min(buku bebas merek ÷ porsinya). Isi belum diketahui / kosong → buku karung di belakangnya.
 */
function bebasLiterWadah(W, rasio, s) {
  const K = wbKomposisi(W, s && s.keranjang ? s : null); const stok = hitungStokKarungPerMerk(); const bebasBuku = (m) => ((stok[m] || {}).sisaKg || 0) - wzDiKeranjangParkir('karung', m) - jumlahAktifKg(m);
  const tot = K.positif.reduce((a, x) => a + x.kg, 0);
  const kg = tot > 0 ? Math.min.apply(null, K.positif.map((x) => bebasBuku(x.merk) / (x.kg / tot))) : bebasBuku(wbMerkCadangan(W));
  return Math.max(0, Math.floor(kg / (rasio || RASIO_DEFAULT) * 10) / 10);
}
/** Kg yang bebas dijual lepas (repacking) dari kolam yang sama. */
function bebasKg(merk) {
  const sisaKg = (hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0;
  return Math.max(0, Math.floor((sisaKg - wzDiKeranjangParkir('karung', merk) - jumlahAktifKg(merk)) * 100) / 100);
}
const DESIMAL2 = (n) => String(Math.round(n * 100) / 100).replace('.', ',');
let _keranjangKini = [], _antreanKini = [];
function jumlahAktifKg(merk) { return _keranjangKini.reduce((a, b) => a + trxPegang(b.trx).reduce((c, t) => c + ((t.merkSumber === merk && (t.jenis === 'karung' || t.jenis === 'literan' || t.jenis === 'repacking')) ? (t.totalKg || 0) : 0), 0), 0); }
/** putaran 27: bentuk "dipegang" satu baris keranjang untuk langit-langit stok — literan WADAH dipegang per merek asal (pecahan), ½ karung = 1 × 50 kg. */
function trxPegang(t) { if (t && t.jenis === 'literan' && t.dariWadah && Array.isArray(t.pecahan) && t.pecahan.length) return t.pecahan.map((x) => ({ jenis: 'literan', merkSumber: x.merk, totalKg: x.kg })); return [skTrxPegang(t)]; }
const barisPegang = (daftar) => (daftar || []).reduce((a, b) => a.concat(trxPegang(b.trx).map((t) => ({ trx: t }))), []);

// lembar wadah yang dipegang satu baris: dijual sebagai barang (jenis wadah) ATAU ditanggung toko di baris repack
const lembarWadahBaris = (b, jenis) => (b.trx.jenis === 'wadah' && b.trx.jenisWadah === jenis ? (b.trx.jumlahUnit || 0) : 0) + (b.trx.kemasanRepack === jenis ? (b.trx.jumlahKemasanRepackDipakai || 0) : 0);
function wadahDipegangParkir(jenis) { return _antreanKini.reduce((a, x) => a + (((x.beku || {}).items) || []).reduce((c, b) => c + lembarWadahBaris(b, jenis), 0), 0); }
function wadahDipegang(jenis, tanpaId) { return _keranjangKini.filter((b) => b.id !== tanpaId).reduce((a, b) => a + lembarWadahBaris(b, jenis), 0) + wadahDipegangParkir(jenis); }
/** Sinkronkan keranjang aktif & parkir ke lapisan data (dibaca stokMaksJalur lewat wzDiKeranjang). */
export function sinkronKeranjang(s) {
  _keranjangKini = s.keranjang; _antreanKini = s.antrean || [];
  // putaran 27: baris ½ karung memegang 1 unit kemasan 50 kg (bukan 25 kg) di langit-langit stok mesin beku
  // putaran 27: literan wadah dipegang per MEREK ASAL (pecahannya) — mesin beku wzDiKeranjang menjumlah merkSumber tiap baris
  setelKeranjang(barisPegang(s.keranjang), s.antrean.map((a) => ({ beku: { items: barisPegang(a.beku.items), nama: a.beku.pelanggan } })));
}

// ---------- tagihan ----------
/** Pembulatan Rp500 ke atas untuk Tunai DAN Bon (keputusan owner 17 Sep 2026); QRIS persis. */
export function pembulatanTagihan(total, cara) {
  const c = bakuCaraBayar(cara);
  return (c === 'Tunai' || c === 'Kredit') && total > 0 ? bulatKeAtas500(total) - Math.round(total) : 0;
}
/** Pembulatan keranjang ini. SUSULAN tukar GABUNG (tkBulat 17051): pembulatan dihitung atas selisih yang dulu diterima (pengganti − nilai retur), dikurangi pembulatan yang masih menempel di penjualan tertaut; susulan model lama: atas harga penuh. */
export function bulatKeranjang(s, bersih) {
  const tk = s.tukar;
  if (tk && tk.susulanReturId && tk.model === 'kreditBarangGabung') { const a = tkSetTertaut().get(String(tk.susulanReturId)) || { rp: 0, bulat: 0 }; return Math.max(0, pembulatanTunai(a.rp - a.bulat + bersih - (tk.nilaiRetur || 0), s.cara) - a.bulat); }
  return pembulatanTagihan(bersih, s.cara);
}
export function hitungTagihan(s) {
  const subtotal = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0);
  const potongan = Math.min(Math.max(0, Math.round(s.potongan || 0)), subtotal);
  // TUKAR: nilai barang yang kembali dipotong SEBELUM pembulatan — pembulatan dihitung atas selisih bersih (wzTagihan 17680)
  const kredit = s.tukar ? Math.round(s.tukar.kredit || 0) : 0;
  const bersih = subtotal - potongan - kredit;
  const bulat = bulatKeranjang(s, bersih);
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
// Kunci SATU nota — sama dengan plKunciNota (pelanggan-logika): grupNota → trxId (keranjang index.html & sistem baru, tanpa grupNota) → baris tunggal.
const jlKunciNota = (p) => String(p.grupNota || p.trxId || p.id);
export function hariIni(s) {
  const iso = hariIniIso(s.sekarang);
  const baris = ambilPenjualan().filter((p) => p.tanggal === iso);
  const nota = new Set(baris.map(jlKunciNota)).size;
  const omzet = baris.reduce((a, p) => a + (p.hargaTotal || 0), 0);
  const perCara = {}; baris.forEach((p) => { const c = bakuCaraBayar(p.caraBayar); perCara[c] = (perCara[c] || 0) + (p.hargaTotal || 0); });
  const terakhir = gabungTakaran(baris).slice(0, 6).map((p) => ({ jam: p.jam || '', nama: p.namaPelanggan || '', teks: ringkasBaris(p), n: p.hargaTotal || 0, cara: bakuCaraBayar(p.caraBayar), id: p.id, trxId: p.trxId || '', grupNota: p.grupNota || '' }));
  return { iso, nota, baris: baris.length, omzet, perCara, terakhir, kg: baris.reduce((a, p) => a + (p.totalKg || 0), 0) };
}
function ringkasBaris(p) {
  if (p.jenis === 'kemasan') return (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg × ' + (p.jumlahUnit || '');
  if (p.jenis === 'karung') return (p.merkSumber || '') + ' ' + (p.beratKarungAcuan || 50) + ' kg × ' + (p.jumlahKarung || '');
  if (p.jenis === 'literan') return (p.dariWadah || p.merkSumber || '') + ' ' + (p.jumlahLiter || 0) + ' L';
  if (p.jenis === 'repacking') return 'Repack ' + (p.namaProduk || '') + ' ' + (p.totalKg || 0) + ' kg';
  if (p.jenis === 'wadah') return (p.namaProduk || 'Wadah') + ' × ' + (p.jumlahUnit || 0) + ' lembar';
  return p.namaProduk || p.jenis || '';
}

// ---------- tindakan (mengembalikan patch keadaan; tidak menyentuh DOM) ----------
export function ketukChip(s, chip) {
  return { pilih: chip, lembar: 'jumlah', ketik: '', kabar: '' };
}
export function tekanTuts(s, t) {
  if (t === '⌫') return { ketik: s.ketik.slice(0, -1) };
  // koma: literan (liter pecahan), repack (kg), dan KARUNG (setengah karung, mis. 1,5 — owner 22 Sep: 25 kg dituang ke karung bekas); kemasan tidak
  if (t === ',') { if (s.ketik.indexOf(',') >= 0 || (s.pilih && (s.pilih.jalur === 'kemasan' || s.pilih.jalur === 'wadah'))) return {}; return { ketik: (s.ketik || '0') + ',' }; }
  if (!/^\d+$/.test(t)) return {};
  if (s.ketik === '' && t === '0') return {};
  if ((s.ketik + t).replace(',', '').length > 9) return {};
  return { ketik: s.ketik + t };
}
export const angkaKetik = (teks) => parseFloat(String(teks || '').replace(',', '.')) || 0;
/** Rupiah yang diketik bebas ("1.380.000", "1380000", "Rp 1.380.000") → bilangan bulat. */
export const angkaRupiah = (teks) => Math.round(Number(String(teks || '').replace(/[^\d]/g, '')) || 0);

/**
 * Putaran 23c (owner 24 Sep): akun bukan-owner — satu nota paling banyak s.batasBaris baris (layar mengisinya dari akses.js; 0 = owner, tanpa batas).
 * Sebabnya batas sekali kirim ke server (access call, sisa 2): alat-uji/peta_akses.py --kiriman. '' = masih muat.
 */
export function alasanBatasBaris(s, nBaris) {
  const b = Number(s.batasBaris) || 0;
  return b > 0 && nBaris > b ? 'Satu nota paling banyak ' + b + ' baris untuk akun bukan-owner — batas sekali kirim ke server. Simpan nota ini dulu, sisanya jadi nota kedua.' : '';
}
/** Masukkan chip terpilih ke keranjang sejumlah ketikan/preset; ditolak kalau melampaui langit-langit. */
export function masukkan(s, jumlah) {
  const chip = s.pilih; if (!chip) return { kabar: 'Pilih barangnya dulu', kabarAwas: true };
  const j = Number(jumlah) || angkaKetik(s.ketik);
  if (j <= 0) return { kabar: 'Isi jumlahnya dulu', kabarAwas: true };
  if (chip.jalur === 'karung' && (j * 2) % 1 !== 0) return { kabar: 'Karung dijual utuh atau setengah (0,5 · 1 · 1,5 …)', kabarAwas: true };
  if (chip.jalur === 'kemasan' && j % 1 !== 0) return { kabar: 'Kemasan dijual per unit', kabarAwas: true };
  if (chip.setengahDari && j !== 1) return { kabar: '½ karung dimasukkan satu-satu (1 × 25 kg); dua ½ = jual 50 kg-nya utuh', kabarAwas: true };
  if (chip.setengahDari && chip.setengahHargaBaru > 0 && Number(s.batasBaris) > 0) return { kabar: 'Harga ' + chip.nama + ' 25 kg belum ada di katalog — minta owner menyetelnya dulu (akun bukan-owner tidak menulis katalog)', kabarAwas: true };
  if (chip.jalur === 'wadah' && j % 1 !== 0) return { kabar: 'Wadah dijual per lembar', kabarAwas: true };
  sinkronKeranjang(s);
  const maks = maksUntuk(chip);
  if (maks !== null && j > maks) {
    const dipegang = chip.jalur === 'kemasan' ? wzDiKeranjangParkir('kemasan', chip.kunci) : chip.jalur === 'wadah' ? wadahDipegangParkir(chip.kunci) : wzDiKeranjangParkir('karung', chip.kunci);
    const siapa = siapaParkir(s, chip);
    return { kabar: 'Yang bebas dijual sekarang ' + tulisJumlah(maks, chip) + ', diminta ' + tulisJumlah(j, chip)
      + (dipegang > 0 ? ' — ' + (siapa || 'struk lain') + ' masih memegang ' + tulisKg(dipegang, chip) : '') + '.', kabarAwas: true };
  }
  // REPACK (putaran 15): wadah yang dipilih ikut — DIJUAL jadi baris nota sendiri, DITANGGUNG masuk HPP baris repack; upah per nota melekat
  let ekstra; let barisWadah = null; let ketWadah = '';
  if (chip.jalur === 'repack') {
    const jenis = String(s.rpWadah || ''); const lembar = Math.max(0, Math.round(angkaKetik(s.rpLembar))); const upah = angkaRupiah(s.rpUpah);
    ekstra = { upahRepack: upah };
    if (jenis && lembar > 0) {
      const dw = jenisWadah(jenis); if (!dw) return { kabar: 'Wadah itu tidak dikenal buku kantong', kabarAwas: true };
      const bebas = bebasWadah(jenis, wadahDipegang(jenis));
      if (bebas !== null && lembar > bebas) return { kabar: dw.label + ': yang ada di buku ' + bebas + ' lembar, diminta ' + lembar + '. Beli / catat kantongnya dulu (kantong yang belum ada dibeli dulu — owner).', kabarAwas: true };
      if (s.rpDijual) {
        const cw = susunRakWadah((x) => wadahDipegang(x), (x) => wadahDipegangParkir(x)).find((c) => c.kunci === jenis);
        if (!cw) return { kabar: dw.label + ' belum punya harga jual — layar menolak menagihnya. Setel harganya di jalur Wadah, atau pilih "ditanggung toko".', kabarAwas: true };
        barisWadah = bangunBaris(cw, lembar, s); ketWadah = ' + ' + lembar + ' lembar ' + dw.label + ' (dijual ' + RP(barisWadah.hargaTotal) + ')';
      } else { ekstra.kemasanRepack = jenis; ekstra.jumlahKemasanRepack = lembar; ketWadah = ' · ' + lembar + ' lembar ' + dw.label + ' ditanggung toko (masuk HPP)'; }
    }
    if (upah > 0) ketWadah += ' · upah repack ' + RP(upah);
  }
  const baris = bangunBaris(chip, j, s, ekstra); if (!baris) return { kabar: 'Jenis barang belum dikenal', kabarAwas: true };
  let urut = s.urutBaris; const tambah = [{ id: 'b' + (++urut), trx: baris }];
  if (barisWadah) tambah.push({ id: 'b' + (++urut), trx: barisWadah });
  const keranjang = s.keranjang.concat(tambah);
  const lewat = alasanBatasBaris(s, keranjang.length); if (lewat) return { kabar: lewat, kabarAwas: true };
  return { keranjang, urutBaris: urut, pilih: null, lembar: null, ketik: '', namaRepack: '', rpWadah: '', rpLembar: '', rpDijual: true, rpUpah: '',
    kabar: baris.label + ' × ' + tulisJumlah(j, chip) + ketWadah + ' masuk', kabarAwas: false };
}
function tulisJumlah(n, chip) { return String(n).replace('.', ',') + ' ' + (chip.satuan === 'L' ? 'L' : chip.satuan); }
function tulisKg(kg, chip) { return chip.jalur === 'kemasan' ? kg + ' unit' : chip.jalur === 'wadah' ? kg + ' lembar' : String(Math.round(kg * 100) / 100).replace('.', ',') + ' kg'; }
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
  if (b.trx.setengahDari) return { kabar: '½ karung tidak bisa diberi bonus', kabarAwas: true };
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
  const nama = s.antrean.filter((a) => a.beku.items.some((b) => (chip.jalur === 'kemasan' ? b.trx.jenis === 'kemasan' && kunciKemasan(b.trx.namaProduk, b.trx.ukuranKemasan) === chip.kunci : chip.jalur === 'wadah' ? lembarWadahBaris(b, chip.kunci) > 0 : b.trx.merkSumber === chip.kunci)))
    .map((a, i) => (a.beku.pelanggan || '').trim() || ('pembeli ke-' + (i + 1)));
  return nama.length === 1 ? nama[0] : (nama.length ? nama.length + ' struk diparkir' : '');
}
export function hapusBaris(s, id) { return { keranjang: s.keranjang.filter((b) => b.id !== id), negoId: null, kabar: '' }; }
export function ubahJumlahBaris(s, id, selisih) {
  const b = s.keranjang.find((x) => x.id === id); if (!b) return {};
  if (b.trx.setengahDari && selisih > 0) return { kabar: '½ karung satu-satu — dua ½ = jual 50 kg-nya utuh', kabarAwas: true };
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
  if (t.jenis === 'kemasan' && t.setengahDari) { const c50 = rak.kemasan.find((c) => c.kunci === t.setengahDari); return c50 ? skChip(c50, t.setengahHargaBaru || t.hargaAsli) : null; }
  if (t.jenis === 'kemasan') return rak.kemasan.find((c) => c.kunci === kunciKemasan(t.namaProduk, t.ukuranKemasan)) || null;
  if (t.jenis === 'literan') return rak.literan.find((c) => c.kunci === (t.dariWadah || t.merkSumber)) || null;
  if (t.jenis === 'repacking') return rak.repack.find((c) => c.kunci === t.merkSumber) || null;
  if (t.jenis === 'wadah') return rak.wadah.find((c) => c.kunci === t.jenisWadah) || null;
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
  if (s.karcis) return { kabar: 'Keranjang sedang merinci karcis — simpan rinciannya atau lepas karcisnya dulu, baru parkir', kabarAwas: true };
  if (!s.keranjang.length) return { kabar: 'Keranjang kosong — tidak ada yang diparkir', kabarAwas: true };
  // ikatan pesanan ikut diparkir (wzBekuKeranjang 17453) — kalau tidak, ia pindah ke pembeli berikutnya
  // pada = saat diparkir (putaran 25: daftar periksa kunci bulan menolak mengunci bulan yang masih punya nota parkir)
  const beku = { items: s.keranjang, pelanggan: s.pelanggan, cara: s.cara, uang: s.uang, potongan: s.potongan, pesananId: s.pesananId || null, tukar: s.tukar || null, pada: new Date(Date.now()).toISOString() };
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

// ---------- GANTI ORANG (putaran 23c, owner 24 Sep): keranjang TIDAK boleh terbawa ke akun berikutnya ----------
/** Baris yang belum disimpan = keranjang yang sedang jalan + keranjang yang diparkir. */
export function barisBelumDisimpan(s) {
  const aktif = (s.keranjang || []).length;
  const parkir = (s.antrean || []).filter((a) => a.id !== s.aktifId).reduce((n, a) => n + (((a.beku || {}).items) || []).length, 0);
  return { aktif, parkir, total: aktif + parkir };
}
export const kalimatKeranjangKeluar = (n) => 'Keranjang berisi ' + n + ' baris belum disimpan — simpan atau kosongkan?';
// putaran 23d: isian Jual SELAIN keranjang — pesanan yang sedang diketik, retur (tanpa/dengan nota), repack, setelan struk/wadah yang terbuka, karcis yang dirinci, tukar
const ISIAN_JUAL_LAIN = ['psNama', 'psIsi', 'psAlamat', 'psNilai', 'aturStruk', 'aturWadah', 'karcis', 'kcBatal', 'tukar', 'namaRepack', 'rpWadah', 'rpLembar', 'rpUpah', 'setengahHarga',
  'rtNotaId', 'rtAlasan', 'rtNominal', 'rtAlasanTimpa', 'rtBarang', 'rtSelisih', 'rtPengganti'];
export function adaIsianLain(s) { const a = keadaanAwal(); return ISIAN_JUAL_LAIN.some((k) => JSON.stringify(s[k] === undefined ? null : s[k]) !== JSON.stringify(a[k] === undefined ? null : a[k])); }
/** Keadaan Jual untuk orang berikutnya: keranjang, parkir, nama pembeli, potongan, retur tukar, karcis, pesanan, isian — dibuang semua; yang tinggal cuma
 *  "sekarang" (mode cadangan). Kunci yang tidak ada di keadaanAwal ikut dikosongkan. Cermin keranjang di lapisan data (stok yang dipegang) ikut dilepas. */
export function keadaanOrangBerikutnya(s) {
  const baru = Object.assign(keadaanAwal(), { sekarang: (s && s.sekarang) || null });
  Object.keys(s || {}).forEach((k) => { if (!(k in baru)) baru[k] = undefined; });
  sinkronKeranjang(baru);
  return baru;
}

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
    // wadah yang ditanggung toko di baris repack juga memakai buku kantong
    if (b.trx.kemasanRepack) { const bebas = bebasWadah(b.trx.kemasanRepack, wadahDipegang(b.trx.kemasanRepack, b.id)); if (bebas !== null && (b.trx.jumlahKemasanRepackDipakai || 0) > bebas) return b.trx.label + ': wadah yang ditanggung toko (' + b.trx.jumlahKemasanRepackDipakai + ' lembar) melebihi buku kantong ' + bebas + ' lembar'; }
  }
  return '';
}
// PUTARAN 31b (keputusan owner 28 Sep, docs/peta-jual-tandai-cocok.md §6): "jual dulu, tandai untuk dicocokkan". Pemeriksaan ulang stok TIDAK berubah;
// kalau gagal dan yang masuk OWNER, ketukan kedua mencatat nota apa adanya: baris yang melampaui buku diberi kolom `perluCocokkan: true` + `selisihKg`,
// buku dibiarkan minus. Tanda tuntas = Cocokkan nama itu bertanggal ≥ tanggal nota. Akun staf tetap ditahan.
const kgTembus = (t, chip, sel) => (chip.jalur === 'karung' ? sel * (chip.berat || Number(t.beratKarungAcuan) || 50) : chip.jalur === 'kemasan' ? sel * (Number(t.ukuranKemasan) || 0) : chip.jalur === 'literan' ? sel * rasioMerk(t.merkSumber || chip.kunci) : sel);
/** Baris keranjang yang melampaui langit-langit buku (bukan kantong repack), dengan selisih dalam satuan chip dan kg. */
export function barisTembus(s) {
  const out = [];
  for (const b of s.keranjang) {
    const chip = chipDariBaris(b.trx); if (!chip) continue; const maks = maksTanpaBaris(s, b.id, chip); const butuh = butuhStok(b.trx);
    if (maks === null || butuh <= maks) continue; const sel = Math.round((butuh - maks) * 100) / 100;
    out.push({ id: b.id, label: b.trx.label, kunci: chip.kunci, nama: b.trx.jenis === 'kemasan' ? String(b.trx.namaProduk) + ' ' + String(b.trx.ukuranKemasan).replace('.', ',') + ' kg' : String(b.trx.merkSumber || chip.kunci), jalur: chip.jalur, maks, butuh, selisih: sel, selisihKg: Math.round(kgTembus(b.trx, chip, sel) * 100) / 100,
      teks: b.trx.label + ': yang bebas dijual tinggal ' + tulisJumlah(maks, chip) + ', di keranjang ' + tulisJumlah(butuh, chip) + (b.trx.bonusUnit ? ' (termasuk bonus)' : '') });
  }
  return out;
}
const kgTeks = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
/** Nota bertanda `perluCocokkan` yang belum tuntas: belum ada cocokkan nama itu bertanggal ≥ tanggal nota (karung/literan/repack: penyesuaianStok bukan rework; kemasan: penyesuaianKemasan). */
export function notaTembusBelumCocok() {
  const PS = ambilPenyesuaianStok().filter((q) => !q.dariRework); const PK = ambilPenyesuaianKemasan(); const out = [];
  ambilPenjualan().forEach((p) => { if (!p.perluCocokkan) return; const tgl = String(p.tanggal || '');
    const nama = p.jenis === 'kemasan' ? String(p.namaProduk) + ' ' + String(p.ukuranKemasan).replace('.', ',') + ' kg' : String(p.merkSumber || '');
    const tuntas = p.jenis === 'kemasan' ? PK.some((q) => String(q.namaProduk) === String(p.namaProduk) && Number(q.ukuranKemasan) === Number(p.ukuranKemasan) && String(q.tanggal || '') >= tgl) : PS.some((q) => String(q.merk) === String(p.merkSumber) && String(q.tanggal || '') >= tgl);
    if (!tuntas) out.push({ id: p.id, trxId: p.trxId, tanggal: tgl, jam: String(p.jam || ''), nama, jenis: p.jenis, selisihKg: Number(p.selisihKg) || 0, namaPelanggan: String(p.namaPelanggan || '') }); });
  const per = {}; out.forEach((x) => { per[x.nama] = per[x.nama] || { nama: x.nama, kg: 0, n: 0 }; per[x.nama].kg = Math.round((per[x.nama].kg + x.selisihKg) * 100) / 100; per[x.nama].n += 1; });
  const nama = Object.keys(per).sort((a, b) => a.localeCompare(b)).map((k) => per[k]);
  const trx = {}; out.forEach((x) => { trx[String(x.trxId)] = 1; });
  return { baris: out.sort((a, b) => String(a.tanggal + a.jam).localeCompare(String(b.tanggal + b.jam))), nama, n: Object.keys(trx).length, ringkas: nama.map((x) => x.nama + ' ' + kgTeks(x.kg)).join(', ') };
}
/** Alasan nota belum bisa dicatat — '' kalau sah. */
export function alasanTolak(s) {
  if (s.karcis) return 'Keranjang ini sedang merinci karcis — pakai SIMPAN RINCIAN (atau lepas karcisnya)';
  if (!s.keranjang.length) return 'Keranjang kosong';
  const lewat = alasanBatasBaris(s, s.keranjang.length); if (lewat) return lewat;   // keranjang dari antrean / ulangi nota juga tertangkap di sini
  const t = hitungTagihan(s);
  const nama = kunciPelanggan(s.pelanggan);
  if (s.tukar && s.tukar.susulanReturId) {   // PUTARAN 20: susulan pengganti tukar yatim (tkCekSusulan, tkLebihSusulanBoleh)
    if (s.cara === 'Kredit') return 'Susulan tukar tidak bisa BON — uangnya sudah diterima saat tukar';
    if (t.uang > 0 && t.uang < t.total) return 'Susulan tukar tidak bisa dibayar sebagian';
    const cek = cekSusulan(s.tukar.susulanReturId, t.subtotal - t.potongan, !!s.tukar.yakinLebih); if (cek) return cek;
  } else if (s.tukar) {   // simpanKeranjangJual 19103–19123
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
  const items = pecahItemsWadah(s.keranjang.map((b) => Object.assign({}, b.trx)), s);   // putaran 27: satu takaran wadah → baris internal per merek asal
  const nama = String(s.pelanggan || '').trim();
  const subtotal = items.reduce((a, t) => a + t.hargaTotal, 0);
  const pot = Math.max(0, Math.round(s.potongan || 0));
  const potDipakai = Math.min(pot, subtotal);
  const totalSetelahPot = subtotal - potDipakai;
  let cara = bakuCaraBayar(s.cara); const caraAsli = cara;
  const tk = s.tukar || null; const kreditTukar = tk ? Math.round(tk.kredit || 0) : 0;
  const bulatNota = bulatKeranjang(Object.assign({}, s, { cara }), totalSetelahPot - kreditTukar);   // atas SELISIH BERSIH bila tukar; susulan gabung punya rumusnya sendiri
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
  const dokumen = []; let tolakPecah = ''; const takaranPertama = {};
  items.forEach((t) => {
    const d = Object.assign({}, t);
    ['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego', 'setengahDari', 'setengahHargaBaru', 'pecahan', '_takaran'].forEach((k) => { delete d[k]; });
    // putaran 27 (Bagian 4): ½ karung — 1 × 50 kg dipecah jadi 2 × 25 kg (penyusun Adukan) di kiriman yang sama; modal baris = modal 25 kg hasil pecahan
    if (t.setengahDari) { const pc = skPecah(t, w); if (pc.tolak) tolakPecah = tolakPecah || pc.tolak; else { d.dariSetengah = pc.idProduksi; d.hppTotalSaatJual = Math.round(pc.hppPerUnit); pc.dokumen.forEach((x) => dokumen.push(x)); } }
    d.id = w.idUnik(); d.trxId = trxId; d.tanggal = w.tanggal; d.jam = w.jam; d.caraBayar = cara; d.namaPelanggan = nama;
    if (t._takaran) d.takaranId = takaranPertama[t._takaran] || (takaranPertama[t._takaran] = String(d.id));   // pengikat baris internal satu takaran (struk menggabung)
    d.hargaAsliSatuan = t.hargaAsli;                                   // harga daftar sebelum tawar (kebal riwayat)
    if (t.nego) d.negoSelisih = t.hargaSatuan - t.hargaAsli;          // jejak tawar (NG1)
    if (tk) d.tukarReturId = String(tk.susulanReturId || tk.returDraf.id);   // tautan ke retur tukarnya (19175); susulan menunjuk retur yatim yang sudah ada
    if (cara === 'Kredit' && s.kreditDibuka) d.kreditDibukaOwner = true;
    if (uang > 0 && cara === 'Tunai') { d.uangDiterima = uang; d.kembalian = Math.max(0, uang - (totalBayar - kreditTukar)); }
    dokumen.push({ koleksi: 'penjualan', data: d });
    if (d.kemasanLiteran && d.jumlahKemasanLiteranDipakai > 0) {
      dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: d.id + 1, tipe: 'pakai', jenis: d.kemasanLiteran, jumlah: d.jumlahKemasanLiteranDipakai,
        hargaTotal: 0, tanggal: w.tanggal, catatan: 'Otomatis dari penjualan literan id ' + d.id } });
    }
    // PUTARAN 15: wadah yang DIJUAL memotong buku kantong/karung bekas (pola yang sama: dokumen pakai id+1 di koleksi bahannya)
    if (d.jenis === 'wadah' && d.jenisWadah && d.jumlahUnit > 0) {
      dokumen.push({ koleksi: koleksiWadah(d.jenisWadah), data: { id: d.id + 1, tipe: 'pakai', jenis: d.jenisWadah, jumlah: d.jumlahUnit,
        hargaTotal: 0, tanggal: w.tanggal, catatan: 'Dijual sebagai barang di nota id ' + d.id } });
    }
    // wadah yang DITANGGUNG toko pada repack: biayanya sudah di hppTotalSaatJual baris repack, bukunya dipotong di sini
    if (d.kemasanRepack && d.jumlahKemasanRepackDipakai > 0) {
      dokumen.push({ koleksi: koleksiWadah(d.kemasanRepack), data: { id: d.id + 1, tipe: 'pakai', jenis: d.kemasanRepack, jumlah: d.jumlahKemasanRepackDipakai,
        hargaTotal: 0, tanggal: w.tanggal, catatan: 'Otomatis dari repack id ' + d.id + ' (wadah ditanggung toko)' } });
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
  if (tk && !tk.susulanReturId) {
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
  const nBarang = items.filter((t, i) => !t._takaran || items.findIndex((x) => x._takaran === t._takaran) === i).length;   // satu takaran wadah = satu barang
  const ket = [nBarang + ' barang · ' + RP(totalBayar)];
  if (nPengganti) ket.push(nPengganti + ' pengganti retur Rp0');
  const lembarWadah = items.reduce((a, t) => a + (t.jenis === 'wadah' ? (t.jumlahUnit || 0) : 0), 0); if (lembarWadah) ket.push(lembarWadah + ' lembar wadah dijual');
  const tanggung = items.reduce((a, t) => a + (t.jumlahKemasanRepackDipakai || 0), 0); if (tanggung) ket.push(tanggung + ' lembar wadah ditanggung toko');
  const upahSemua = items.reduce((a, t) => a + (t.upahRepack || 0), 0); if (upahSemua) ket.push('upah repack ' + RP(upahSemua));
  if (potDipakai > 0) ket.push('potongan ' + RP(potDipakai));
  if (bulatNota > 0) ket.push('dibulatkan +' + RP(bulatNota));
  if (bayarSebagian > 0) ket.push('dibayar ' + RP(bayarSebagian) + ' · BON ' + RP(totalBayar - bayarSebagian) + ' atas nama ' + nama);
  else if (cara === 'Kredit') ket.push('BON atas nama ' + nama);
  else if (uang > totalBayar - kreditTukar) ket.push('kembalian ' + RP(uang - (totalBayar - kreditTukar)));
  if (tk && tk.susulanReturId) ket.push(tk.ringkas + ' — dicatat penuh, retur tidak ditulis lagi'); else if (tk) ket.push('TUKAR: barang kembali ' + RP(kreditTukar) + ' · pembeli bayar ' + RP(tagihan));
  if (pesanan) ket.push('pesanan ' + pesanan.nama + ' DIBAYAR');
  const nSetengah = items.filter((t) => t.setengahDari).length; if (nSetengah) ket.push(nSetengah + ' × ½ karung (dipecah dari 50 kg)');
  return { tolak: tolakPecah, dokumen, trxId, totalBayar, tagihan, bulatNota, potDipakai, bayarSebagian, cara, ringkas: ket.join(' · '),
    idPenjualan: dokumen.filter((x) => x.koleksi === 'penjualan').map((x) => x.data.id), piutangId, pesanan, retur };
}

/**
 * putaran 27 (Bagian 5): tiap baris literan WADAH dipecah jadi baris internal SATU PER MEREK ASAL menurut komposisi wadah SAAT DICATAT (baris sebelumnya di
 * nota ini & struk yang diparkir ikut dikurangi): kg & liter & rupiah dibagi sebanding kg, sisa pembulatan ke baris terakhir (Σ persis); modal tiap baris =
 * kg × modal merek asalnya; kantong literan hanya di baris pertama. Nama tampil tetap nama wadah (namaProduk), dariWadah = wadah, _takaran = pengikat sementara.
 * Baris lain dikembalikan apa adanya. Dipakai nota Jual dan rinci karcis kasir.
 */
export function pecahItemsWadah(items, s) {
  const out = []; const stok = hitungStokKarungPerMerk(); const sudah = []; const antrean = (s && s.antrean) || [];
  items.forEach((t, i) => {
    if (!(t.jenis === 'literan' && t.dariWadah)) { out.push(t); return; }
    const pc = wbPecah(t.dariWadah, t.totalKg || 0, { keranjang: sudah, antrean }); const bag = pc.bagian.length ? pc.bagian : [{ merk: wbMerkCadangan(t.dariWadah), kg: t.totalKg || 0 }];
    const kgTot = bag.reduce((a, x) => a + x.kg, 0) || 1; const n = bag.length; let rp = 0, lt = 0, nb = 0;
    bag.forEach((x, k) => { const akhir = k === n - 1; const r = Object.assign({}, t);
      r.merkSumber = x.merk; r.totalKg = x.kg;
      r.hargaTotal = akhir ? t.hargaTotal - rp : Math.round(t.hargaTotal * x.kg / kgTot); rp += r.hargaTotal;
      r.jumlahLiter = akhir ? Math.round((t.jumlahLiter - lt) * 1000) / 1000 : Math.round(t.jumlahLiter * x.kg / kgTot * 1000) / 1000; lt += r.jumlahLiter;
      if (t.nilaiBarangPengganti !== undefined) { r.nilaiBarangPengganti = akhir ? t.nilaiBarangPengganti - nb : Math.round(t.nilaiBarangPengganti * x.kg / kgTot); nb += r.nilaiBarangPengganti; }
      r.hppTotalSaatJual = Math.round(x.kg * ((stok[x.merk] || {}).hppTerakhirPerKg || 0)) + (k === 0 ? (t.biayaKemasanLiteran || 0) : 0);
      if (k > 0) { delete r.kemasanLiteran; delete r.biayaKemasanLiteran; delete r.jumlahKemasanLiteranDipakai; }
      r._takaran = 't' + i;
      out.push(r); });
    sudah.push({ trx: { jenis: 'literan', dariWadah: t.dariWadah, pecahan: bag } });
  });
  return out;
}
/** Jam dinding untuk mencatat (dipisah supaya uji bisa memberi jam tetap). */
let _idTerakhir = 0;
/** Id unik yang MENAIK: dalam satu milidetik pecahan acaknya bisa membalik urutan baris — struk & riwayat mengurutkan baris nota menurut id. */
export function idUnikMenaik() { let v = Date.now() + Math.random(); if (v <= _idTerakhir) v = _idTerakhir + 0.001; _idTerakhir = v; return v; }
export function waktuSekarang(d) {
  d = d || new Date();
  return { tanggal: hariIniIso(d), jam: d.toTimeString().slice(0, 5), kini: new Date().toISOString(), idUnik: idUnikMenaik };
}

/** Siapkan pencatatan: {tolak} atau {dokumen, patch, ringkas}. Menulisnya urusan layar (lewat toko.tulisDokumen). */
export function simpanNota(s, w) {
  const tolak0 = alasanTolak(s); if (tolak0) return { tolak: tolak0 };
  const stok = periksaStokKeranjang(s); let tembus = [];   // pemeriksaan ulang TIDAK berubah (31b)
  if (stok) {
    tembus = s.tembusBoleh ? barisTembus(s) : [];
    if (!tembus.length || tembus[0].teks !== stok) return { tolak: stok };   // staf, atau masalahnya bukan langit-langit buku (kantong repack)
    if (!s.tembusYakin) return { tolak: stok + '. Buku ' + tembus.map((t) => t.nama + ' kurang ' + kgTeks(t.selisihKg)).join(', ') + ' — jual dulu, tandai untuk dicocokkan? Buku dibiarkan minus sampai dicocokkan', perluTembus: tembus };
  }
  const ids = {}; tembus.forEach((t) => { ids[t.id] = t; });
  const s2 = tembus.length ? Object.assign({}, s, { keranjang: s.keranjang.map((b) => (ids[b.id] ? Object.assign({}, b, { trx: Object.assign({}, b.trx, { perluCocokkan: true, selisihKg: ids[b.id].selisihKg }) }) : b)) }) : s;
  const n = susunNotaDokumen(s2, w || waktuSekarang(s.sekarang || undefined));
  if (n.tolak) return { tolak: n.tolak };
  const patch = { keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, ketik: '', kreditDibuka: false, pesananId: null, penggantiTanya: null, tukar: null, tembusTanya: null, tembusYakin: false,
    notaTerakhir: { trxId: n.trxId, idPenjualan: n.idPenjualan, piutangId: n.piutangId, pesanan: n.pesanan, retur: n.retur, pada: Date.now(), ringkas: n.ringkas, nama: String(s.pelanggan || '').trim() },
    kabar: 'Tersimpan — ' + n.ringkas + (tembus.length ? ' · TEMBUS STOK, tandai dicocokkan: ' + tembus.map((t) => t.nama + ' ' + kgTeks(t.selisihKg)).join(', ') : ''), kabarAwas: false };
  return { dokumen: n.dokumen, patch, ringkas: n.ringkas, nota: n, tembus };
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
  // wadah yang dijual / ditanggung toko: dokumen pakai id+1 ikut dicabut supaya buku kantongnya pulih
  baris.forEach((p) => { if (p.jenis === 'wadah' && p.jenisWadah) hapus.push({ koleksi: koleksiWadah(p.jenisWadah), id: p.id + 1 }); if (p.kemasanRepack && p.jumlahKemasanRepackDipakai > 0) hapus.push({ koleksi: koleksiWadah(p.kemasanRepack), id: p.id + 1 }); });
  if (notaTerakhir.piutangId) hapus.push({ koleksi: 'piutangMutasi', id: notaTerakhir.piutangId });
  skHapusPemecah(baris).forEach((x) => hapus.push(x));   // putaran 27: ½ karung — pemecah 50 → 2 × 25 ikut dicabut bila sisanya belum terpakai
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
export function batalTukar(s) { return s.tukar ? { tukar: null, kabar: s.tukar.susulanReturId ? 'Ikatan susulan dilepas — retur yatimnya tetap menunggu pengganti; barang di keranjang tetap' : 'Tukar dibatalkan — returnya TIDAK tercatat; barang di keranjang tetap', kabarAwas: false } : {}; }
export function yakinLebihSusulan(s) { return s.tukar && s.tukar.susulanReturId ? { tukar: Object.assign({}, s.tukar, { yakinLebih: true }), kabar: 'Dicatat: nilai pengganti memang berubah — keranjang boleh melebihi yang belum tercatat', kabarAwas: false } : {}; }

// ---------- wadah literan: tinggi isi, takar isi ulang, karung terbuka di belakangnya ----------
const cap = (p) => (p.tanggal || '') + ' ' + (p.jam || '');
const wdAngka = (v) => Math.round(Number(String(v === undefined || v === null ? '' : v).replace(',', '.')) * 100) / 100;
const wdKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const wdB2 = (n) => Math.round(n * 100) / 100;
/** Urutan dua catatan wadah: tanggal+jam dulu; semenit yang sama → id (id = jam mesin saat ditulis, jadi naik terus). */
export function wdSesudah(x, y) {
  const c = cap(x).localeCompare(cap(y)); if (c) return c > 0;
  const nx = Number(x.id); const ny = Number(y.id);
  return isFinite(nx) && isFinite(ny) ? nx > ny : String(x.id) > String(y.id);
}
export const wdTerbaru = (daftar) => daftar.reduce((a, x) => (!a || wdSesudah(x, a) ? x : a), null);

/**
 * Angka kebijakan wadah yang BERLAKU: dokumen wadahLiteran bertipe 'atur' yang terbaru (diatur owner dari layar Stok → Wadah literan);
 * belum pernah diatur → bawaan dari keterangan owner (rata 50 kg · menggunung sampai 60 kg · isi ulang saat sisa 10 kg · takar 1,8 kg · delapan wadah).
 * daftar = URUTAN posisi kotak di toko (W1, W2, …); resep[wadah] = campuran bawaan wadah itu (kosong = merek itu sendiri).
 */
export function aturWadah() {
  const a = wdTerbaru(ambilWadahLiteran().filter((w) => w.tipe === 'atur'));
  const penuhKg = a && Number(a.penuhKg) > 0 ? Number(a.penuhKg) : WADAH_PENUH_KG;
  // aturan lama (sebelum koreksi 19 Sep) belum punya batas menggunung → sebanding bawaan (60/50 dari isi rata)
  const puncakKg = a && Number(a.puncakKg) >= penuhKg ? Number(a.puncakKg) : (a ? Math.round(penuhKg * (WADAH_PUNCAK_KG / WADAH_PENUH_KG) * 10) / 10 : WADAH_PUNCAK_KG);
  const isiUlangKg = a && Number(a.isiUlangKg) >= 0 && Number(a.isiUlangKg) < penuhKg ? Number(a.isiUlangKg) : Math.min(WADAH_ISI_ULANG_KG, penuhKg - 1);
  const takarKg = a && Number(a.takarKg) > 0 ? Number(a.takarKg) : WADAH_TAKAR_KG;
  const daftar = a && Array.isArray(a.daftar) && a.daftar.length ? a.daftar.map(String) : DAFTAR_WADAH.slice();
  const resep = {}; const mentah = (a && a.resep && typeof a.resep === 'object') ? a.resep : {};
  daftar.forEach((m) => { const r = Array.isArray(mentah[m]) ? mentah[m].filter((x) => x && x.merk && Number(x.takar) > 0).map((x) => ({ merk: String(x.merk), takar: Math.round(Number(x.takar)) })) : []; if (r.length) resep[m] = r; });
  const susutWajarKg = a && a.susutWajarKg !== undefined && a.susutWajarKg !== null && Number(a.susutWajarKg) >= 0 ? Number(a.susutWajarKg) : WADAH_SUSUT_WAJAR_KG;
  // putaran 27: nama wadah yang SEKALIGUS merek karung pemasok (boleh di barang masuk); nama wadah lain = kelas mutu, ditolak barang masuk
  const merekKarung = a && Array.isArray(a.merekKarung) ? a.merekKarung.map(String) : MEREK_KARUNG_BAWAAN.slice();
  // putaran 27: merek yang dijual literan LANGSUNG dari karungnya (bukan lewat wadah); null = belum pernah ditandai owner (wbLiteranLangsung menurunkan bawaannya)
  const literanLangsung = a && Array.isArray(a.literanLangsung) ? a.literanLangsung.map(String) : null;
  const sisihKg = a && Number(a.sisihKg) > 0 ? Number(a.sisihKg) : WADAH_SISIH_KG;
  return { penuhKg, puncakKg, isiUlangKg, takarKg, susutWajarKg, sisihKg, merekKarung, literanLangsung, daftar, resep, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
/**
 * KARUNG di belakang wadah punya NAMA dan TEMPAT (owner 21 Sep): nama = nama barang di buku gudang (Tawon, Kumala, IR64 Apex, …; "IR64 Elevate" dkk.
 * itu jenis + kelas mutu = nama JUAL wadahnya, bukan merek); tempat = di belakang wadah mana ('' = karung bahan campuran, tidak di belakang wadah mana pun).
 * Satu tempat memegang satu kolam karung per nama; dua wadah boleh sama-sama memegang karung bernama sama — dihitung TERPISAH (temuan tinjau 22 Sep).
 * Catatan sebelum 21 Sep (tanpa kolom wadah/lepas) dianggap di belakang wadah senama bila namanya nama wadah, selain itu bahan campuran.
 */
const wdLokasiDoc = (d, daftar) => (d.wadah ? String(d.wadah) : d.lepas ? '' : (daftar.indexOf(String(d.merk)) >= 0 ? String(d.merk) : ''));
const wdLokasiSumber = (x, daftar) => (x.dari !== undefined && x.dari !== null ? String(x.dari) : (daftar.indexOf(String(x.merk)) >= 0 ? String(x.merk) : ''));
/** Karung yang sedang berdiri di belakang satu wadah = catatan 'karung'/'karungIsi' TERBARU di tempat itu. Belum ada → nama wadahnya sendiri (dariCatatan:false). */
export function karungUntukWadah(wadah) {
  const daftar = aturWadah().daftar;
  const a = wdTerbaru(ambilWadahLiteran().filter((k) => (k.tipe === 'karung' || k.tipe === 'karungIsi') && !k.dikembalikan && k.merk && wdLokasiDoc(k, daftar) === wadah));
  return { wadah, merk: a ? String(a.merk) : wadah, dariCatatan: !!a };
}
/** Wadah-wadah yang karung di belakangnya bernama ini — yang TERCATAT dulu, lalu yang cuma senama (belum dicatat). */
export function wadahPemegang(merk) { const d = aturWadah().daftar.map((w) => karungUntukWadah(w)).filter((x) => x.merk === merk); return d.filter((x) => x.dariCatatan).concat(d.filter((x) => !x.dariCatatan)).map((x) => x.wadah); }
export function wadahUntukKarung(merk) { return wadahPemegang(merk)[0] || ''; }
/** Campuran bawaan satu wadah: yang disimpan owner, atau 1 takar dari KARUNG DI BELAKANGNYA. */
export function resepWadah(merk) { const r = aturWadah().resep[merk]; return r && r.length ? r.map((x) => ({ merk: x.merk, takar: x.takar })) : [{ merk: karungUntukWadah(merk).merk, takar: 1 }]; }

/** Owner mengubah aturan wadah — dokumen baru bertipe 'atur' berisi SELURUH aturan (riwayatnya tersimpan; yang terbaru berlaku). */
export function susunAturWadah(isi, w) {
  const kini = aturWadah(); const ada = (v) => v !== undefined && v !== null && String(v).trim() !== '';
  const penuh = Math.round(wdAngka(isi.penuhKg) * 10) / 10;
  const puncak = ada(isi.puncakKg) ? Math.round(wdAngka(isi.puncakKg) * 10) / 10 : Math.max(penuh, kini.puncakKg);
  const ulang = Math.round(wdAngka(isi.isiUlangKg) * 10) / 10;
  const takar = ada(isi.takarKg) ? wdAngka(isi.takarKg) : kini.takarKg;
  const susut = ada(isi.susutWajarKg) ? Math.round(wdAngka(isi.susutWajarKg) * 10) / 10 : kini.susutWajarKg;
  const sisih = ada(isi.sisihKg) ? Math.round(wdAngka(isi.sisihKg) * 10) / 10 : kini.sisihKg;
  if (!(penuh > 0)) return { tolak: 'Isi wadah saat rata harus lebih dari 0 kg' };
  if (!(puncak >= penuh)) return { tolak: 'Batas menggunung tidak boleh di bawah isi rata (' + wdKG(penuh) + ')' };
  if (!(ulang >= 0) || ulang >= penuh) return { tolak: 'Batas isi ulang harus di antara 0 dan ' + String(penuh).replace('.', ',') + ' kg' };
  if (!(takar > 0) || takar > puncak) return { tolak: 'Isi satu takar harus lebih dari 0 kg dan tidak melebihi isi wadah' };
  if (!(susut >= 0) || susut > 10) return { tolak: 'Susut wajar per wadah per hari harus 0–10 kg' };
  if (!(sisih > 0) || sisih > puncak) return { tolak: 'Yang disisihkan saat tutup toko harus lebih dari 0 kg dan tidak melebihi isi wadah' };
  const daftar = (isi.daftar || []).map((x) => String(x).trim()).filter(Boolean);
  if (!daftar.length) return { tolak: 'Daftar wadah tidak boleh kosong' };
  const kembar = daftar.find((m, i) => daftar.indexOf(m) !== i);
  if (kembar) return { tolak: kembar + ' tertulis dua kali — satu beras satu wadah' };
  // putaran 28: wadah berstok sendiri yang dilepas / diganti berasnya — stoknya akan yatim di buku; pakai "ganti nama wadah" (stoknya ikut) atau kosongkan dulu
  const yatim = kini.daftar.filter((m) => daftar.indexOf(m) < 0 && wbAktif(m) && Math.abs(wbKomposisi(m).totalKg) > 0.004);
  if (yatim.length) return { tolak: 'Wadah ' + yatim.map((m) => m + ' (stok ±' + wdKG(wbKomposisi(m).totalKg) + ')').join(', ') + ' masih punya stok sendiri — ganti namanya lewat "ganti nama wadah" supaya stoknya ikut, atau BONGKAR dulu (isinya pindah ke karung wadahnya)' };
  const resep = {}; const asal = isi.resep === undefined ? kini.resep : (isi.resep || {});
  for (const m of daftar) {
    const r = (asal[m] || []).filter((x) => x && x.merk && Number(x.takar) > 0).map((x) => ({ merk: String(x.merk), takar: Math.round(Number(x.takar)) }));
    if (r.length > WADAH_MAKS_RESEP) return { tolak: 'Campuran ' + m + ' paling banyak ' + WADAH_MAKS_RESEP + ' karung berbeda' };
    if (r.some((x, i) => r.findIndex((y) => y.merk === x.merk) !== i)) return { tolak: 'Campuran ' + m + ' menyebut satu karung dua kali' };
    // satu baris "1 takar karung di belakang wadah" (nama wadah ATAU nama karung yang sedang terbuka) = bawaan → tidak disimpan, supaya ikut karung yang berganti
    const bawaan = karungUntukWadah(m).merk;
    if (r.length && !(r.length === 1 && (r[0].merk === m || r[0].merk === bawaan) && r[0].takar === 1)) resep[m] = r;
  }
  return { dokumen: [{ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'atur', penuhKg: penuh, puncakKg: puncak, isiUlangKg: ulang, takarKg: takar, susutWajarKg: susut, sisihKg: sisih, merekKarung: Array.isArray(isi.merekKarung) ? isi.merekKarung.map(String) : kini.merekKarung,
    ...(Array.isArray(isi.literanLangsung) ? { literanLangsung: isi.literanLangsung.map(String) } : kini.literanLangsung ? { literanLangsung: kini.literanLangsung } : {}), daftar, resep } }],
    patch: { kabar: 'Aturan wadah disimpan — rata ' + wdKG(penuh) + ' · menggunung sampai ' + wdKG(puncak) + ' · isi ulang saat sisa ' + wdKG(ulang) + ' · 1 takar ' + String(takar).replace('.', ',') + ' kg · susut wajar ≤ ' + String(susut).replace('.', ',') + ' kg/wadah/hari · sisihkan ' + String(sisih).replace('.', ',') + ' kg saat tutup · ' + daftar.length + ' wadah', kabarAwas: false } };
}
/** Susunan posisi kotak (murni, tanpa menulis): geser satu langkah, ganti beras di satu posisi, tambah, lepas. */
export function geserWadah(daftar, i, arah) { const d = daftar.slice(); const j = i + arah; if (i < 0 || j < 0 || i >= d.length || j >= d.length) return d; const t = d[i]; d[i] = d[j]; d[j] = t; return d; }
export function gantiBerasWadah(daftar, i, merk) { if (!merk || daftar.indexOf(merk) >= 0 || i < 0 || i > daftar.length) return daftar.slice(); const d = daftar.slice(); d[i] = merk; return d; }
export function lepasWadah(daftar, i) { return daftar.filter((_, k) => k !== i); }

/**
 * Tinggi isi satu wadah SEKARANG = isi saat terakhir DISAMAKAN dengan kenyataan (dokumen 'isi') + semua TAKAR yang dituang sesudahnya
 * − literan merek itu yang terjual sesudahnya − literan merek itu yang sedang di keranjang / struk parkir (+ tambahKg = pratinjau takar yang belum dicatat).
 * null = merek ini bukan wadah (diserok dari karung). diketahui:false = belum pernah disamakan → layar MENOLAK menggambar isi.
 * Gambar: dalam 0..1 = isi di dalam kotak (1 = RATA sejajar bibir, penuhKg); gunung 0..1 = bagian di atas bibir (1 = puncakKg).
 */
export function tinggiWadah(merk, s, tambahKg) {
  const atur = aturWadah(); const WADAH_PENUH = atur.penuhKg; const WADAH_PUNCAK = atur.puncakKg; const WADAH_ULANG = atur.isiUlangKg;
  if (atur.daftar.indexOf(merk) < 0) return null;
  const semua = ambilWadahLiteran();
  const tanda = wdTerbaru(semua.filter((w) => w.wadah === merk && w.tipe === 'isi'));
  const aktif = wbAktif(merk);   // putaran 28: stok wadah sendiri — isi = buku kunci wadah (satu kebenaran), catatan isi/takar cuma jam
  if (!tanda && !aktif) return { wadah: true, diketahui: false, penuhKg: WADAH_PENUH, puncakKg: WADAH_PUNCAK, takarKg: atur.takarKg };
  // urutan nota vs tanda: tanggal+jam lalu id (wdSesudah) — SAMA dengan takar; kalau cuma menit, nota di menit yang sama sesudah samakan lolos (tinjau 22 Sep)
  // putaran 27: baris literan dari wadah = model baru (dariWadah = wadah ini, satu takaran dipecah per merek asal) ATAU model lama (merkSumber = nama wadah)
  const sejak = (x) => !tanda || wdSesudah(x, tanda);
  const terjual = aktif ? 0 : ambilPenjualan().reduce((a, p) => a + (wbDariWadah(p, merk) && wdSesudah(p, tanda) ? (p.totalKg || 0) : 0), 0);
  const dituang = semua.reduce((a, t) => a + (t.tipe === 'takar' && t.wadah === merk && sejak(t) ? (Number(t.kg) || 0) : 0), 0);
  const takarAkhir = wdTerbaru(semua.filter((t) => t.tipe === 'takar' && t.wadah === merk && sejak(t)));
  const literKeranjang = (daftar) => (daftar || []).reduce((a, b) => a + wbPecahanBaris(b.trx, merk).reduce((c, x) => c + x.kg, 0), 0);
  const dipegang = literKeranjang(s && s.keranjang) + ((s && s.antrean) || []).reduce((a, x) => a + literKeranjang(x.beku.items), 0);
  const isi = !tanda ? 0 : Number(tanda.isiKg) >= 0 && tanda.isiKg !== undefined && tanda.isiKg !== null ? Number(tanda.isiKg) : WADAH_PENUH;
  const nyata = aktif ? wdB2(((hitungStokKarungPerMerk()[wbKunci(merk)] || {}).sisaKg || 0) - dipegang) : wdB2(isi + dituang - terjual - dipegang);   // tanpa pratinjau — dasar keputusan "perlu isi ulang"
  const sisaKg = wdB2(nyata + (Number(tambahKg) || 0));
  return { wadah: true, diketahui: true, penuhKg: WADAH_PENUH, puncakKg: WADAH_PUNCAK, takarKg: atur.takarKg, sisaKg: Math.max(0, sisaKg), sisaNyataKg: Math.max(0, nyata), nyataMentahKg: nyata, lewat: sisaKg < 0 ? wdB2(-sisaKg) : 0,
    bagian: Math.max(0, Math.min(1, sisaKg / WADAH_PENUH)), dalam: Math.max(0, Math.min(1, sisaKg / WADAH_PENUH)),
    gunung: WADAH_PUNCAK > WADAH_PENUH ? Math.max(0, Math.min(1, (sisaKg - WADAH_PENUH) / (WADAH_PUNCAK - WADAH_PENUH))) : 0,
    muatKg: Math.max(0, wdB2(WADAH_PUNCAK - Math.max(0, nyata))), perluIsi: nyata <= WADAH_ULANG,
    sejakTanggal: tanda ? tanda.tanggal || '' : '', sejakJam: tanda ? tanda.jam || '' : '', isiTerakhirTanggal: (takarAkhir || tanda || {}).tanggal || '', isiTerakhirJam: (takarAkhir || tanda || {}).jam || '', dituangKg: wdB2(dituang),
    stokSendiri: aktif, kunciStok: aktif ? wbKunci(merk) : '' };
}
/** SAMAKAN dengan kenyataan: isi wadah sekarang memang segini (bawaan: rata). Titik hitung baru — takar & penjualan sebelum ini tidak dihitung lagi. */
export function susunIsiUlangWadah(merk, w, isiKg) {
  const atur = aturWadah();
  if (atur.daftar.indexOf(merk) < 0) return { tolak: merk + ' bukan wadah kotak — literannya diserok langsung dari karung' };
  const kg = isiKg === undefined || isiKg === null || isiKg === '' ? atur.penuhKg : Math.round(wdAngka(isiKg) * 10) / 10;
  if (!(kg >= 0) || kg > atur.puncakKg) return { tolak: 'Isi wadah harus di antara 0 dan ' + wdKG(atur.puncakKg) + ' (batas menggunung)' };
  // putaran 28: wadah berstok sendiri — menyamakan isi = menyesuaikan BUKU wadah (susut/lebih masuk laba), jadi lewat satu pintu yang minta alasan
  if (wbAktif(merk)) return { tolak: 'Wadah ' + merk + ' punya stok sendiri — samakan isinya di Stok › Cocokkan › Wadah literan (selisihnya jadi susut wadah itu, di atas susut wajar wajib alasan)' };
  return { dokumen: [{ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: merk, tipe: 'isi', isiKg: kg } }],
    patch: { kabar: 'Wadah ' + merk + ' disamakan: isinya sekarang ±' + wdKG(kg) + (kg > atur.penuhKg ? ' (menggunung)' : kg === atur.penuhKg ? ' (rata bibir kotak)' : '') + ' — dihitung naik dari takar dan turun dari literan berikutnya', kabarAwas: false } };
}

/**
 * KARUNG TERBUKA ("stok wadah") di satu TEMPAT untuk satu NAMA: sisa = titik samakan terakhir ('karungIsi' di tempat itu) + isi tiap karung nama itu yang
 * dibuka di tempat itu sesudahnya − semua takar nama itu yang diambil DARI tempat itu sesudahnya. Belum pernah dibuka/disamakan → diketahui:false (tidak ditebak).
 * lokasi tidak diberikan → tempat utama nama itu (wadah yang memegangnya, atau bahan campuran). sisaMentahKg = tanpa jepitan (untuk hitungan tumpukan).
 * wadah = wadah yang SEKARANG memegang karung ini ('' bila tidak); yatim = tercatat di belakang wadah yang kini memegang karung lain.
 */
export function karungBelakang(merk, lokasi) {
  const daftar = aturWadah().daftar; const L = lokasi === undefined || lokasi === null ? (wadahUntukKarung(merk) || '') : String(lokasi);
  const semua = ambilWadahLiteran(); const diSini = (k) => k.merk === merk && wdLokasiDoc(k, daftar) === L;
  const dasar = wdTerbaru(semua.filter((k) => k.tipe === 'karungIsi' && diSini(k)));
  const buka = semua.filter((k) => k.tipe === 'karung' && diSini(k) && (!dasar || wdSesudah(k, dasar)));
  const pegang = L ? karungUntukWadah(L).merk === merk : false;
  if (!dasar && !buka.length) return { merk, lokasi: L, diketahui: false, penuhKg: beratKarungBuka(merk), wadah: pegang ? L : '', yatim: false };
  const mulai = dasar || buka.reduce((a, x) => (!a || wdSesudah(a, x) ? x : a), null);
  const masuk = (dasar ? Number(dasar.isiKg) || 0 : 0) + buka.reduce((a, k) => a + (Number(k.kg) || KARUNG_BELAKANG_KG), 0);
  const diambil = semua.reduce((a, t) => a + (t.tipe === 'takar' && wdSesudah(t, mulai) ? (t.sumber || []).reduce((b, x) => b + (x.merk === merk && wdLokasiSumber(x, daftar) === L ? (Number(x.kg) || 0) : 0), 0) : 0), 0);
  const sisa = wdB2(masuk - diambil); const akhir = wdTerbaru(buka.concat(dasar ? [dasar] : [])); const penuh = buka.length ? (Number(wdTerbaru(buka).kg) || KARUNG_BELAKANG_KG) : beratKarungBuka(merk);
  return { merk, lokasi: L, diketahui: true, penuhKg: penuh, sisaKg: Math.max(0, sisa), sisaMentahKg: sisa, lewat: sisa < 0 ? wdB2(-sisa) : 0, bagian: Math.max(0, Math.min(1, sisa / penuh)),
    dibuka: buka.length, sejakTanggal: akhir.tanggal || '', sejakJam: akhir.jam || '', wadah: pegang ? L : '', yatim: !!L && !pegang };
}
/** Semua kolam karung terbuka yang DIKETAHUI (nama × tempat), dari catatan karung/karungIsi. */
export function semuaKarungTerbuka() {
  const daftar = aturWadah().daftar; const kunci = {};
  ambilWadahLiteran().forEach((d) => { if ((d.tipe === 'karung' || d.tipe === 'karungIsi') && d.merk) kunci[String(d.merk) + '|#|' + wdLokasiDoc(d, daftar)] = 1; });
  return Object.keys(kunci).sort().map((k) => { const i = k.indexOf('|#|'); return karungBelakang(k.slice(0, i), k.slice(i + 3)); }).filter((x) => x.diketahui);
}
/**
 * Dari karung MANA takar bernama `merk` untuk wadah `wadah` diambil: (1) karung di belakang wadah itu bila namanya sama (termasuk wadah senama yang belum
 * dicatat — karungnya nanti dibuka di situ); (2) karung bahan campuran nama itu yang masih berisi; (3) karung senama di belakang wadah lain yang masih berisi;
 * (4) bahan campuran (belum ada → tidak ditebak; ada tapi habis → dibuka baru).
 */
export function lokasiSumber(merk, wadah) {
  if (karungUntukWadah(wadah).merk === merk) return wadah;
  const lepas = karungBelakang(merk, ''); if (lepas.diketahui && lepas.sisaKg > 0) return '';
  const lain = wadahPemegang(merk).filter((w) => w !== wadah).find((w) => { const k = karungBelakang(merk, w); return k.diketahui && k.sisaKg > 0; });
  return lain || '';
}
/** Isi satu karung utuh nama itu di gudang: 50 kg; nama yang HANYA pernah masuk sebagai karung 25 kg → 25. */
export function beratKarungBuka(merk) { const u = petaUkuran()[merk]; if (u) return u.berat; return !merkPunyaKarungBerat(merk, 50) && merkPunyaKarungBerat(merk, 25) ? 25 : KARUNG_BELAKANG_KG; }   // putaran 28: buku per ukuran = ukurannya
/**
 * BUKA KARUNG: satu karung utuh bernama `merk` diambil dari TUMPUKAN GUDANG, dibuka di belakang `wadah` (kosong = karung bahan campuran, tanpa wadah).
 * Jalur pertama rantai stok: tumpukan gudang nama itu turun satu karung SAAT INI JUGA (lihat tumpukanGudang). Buku mesin lama tidak ditulis —
 * berasnya belum keluar dari toko; buku baru berkurang saat literannya TERJUAL, jadi beras yang sama tidak dipotong dua kali.
 * Nama yang tidak ada di buku gudang DITOLAK (karung di belakang wadah selalu berasal dari karung sumber di gudang).
 */
export function susunBukaKarung(merk, w, wadah, asal) {
  if (!merk) return { tolak: 'Pilih dulu karung apa yang dibuka' };
  const atur = aturWadah(); const di = wadah && atur.daftar.indexOf(wadah) >= 0 ? wadah : '';
  if (asal && asal.jenis === 'adukan') return susunBukaKemasan(asal.namaProduk || merk, asal.ukuran, w, di);
  if (asal && asal.jenis === 'masuk') { const b = ambilSemuaBatch().find((x) => String(x.id) === String(asal.batchId));
    if (!b || b.stokAwal || b.tutupBuku || !(b.merkList || []).some((m) => m.merk === merk && m.satuan === 'karung')) return { tolak: 'Kedatangan itu tidak memuat karung ' + merk + ' — pilih dari daftar "baru datang"' }; }
  const t = tumpukanGudang(merk);
  if (!t.adaBuku) return { tolak: merk + ' tidak ada di buku gudang — karung di belakang wadah diambil dari karung yang tercatat masuk gudang' };
  const kg = beratKarungBuka(merk); const sesudah = wdB2(t.kg - kg); const masuk = asal && asal.jenis === 'masuk';
  // putaran 28 (tiga pintu, owner 28 Sep): karung yang BARU DATANG dari pemasok = karung gudang yang sama di buku (kedatangannya sudah dicatat di Barang masuk);
  // asal & batchId dicatat di catatan karung sebagai jejak, bukunya tetap buku merek itu
  return { dokumen: [{ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karung', merk, kg }, di ? { wadah: di } : { lepas: true }, masuk ? { asal: 'masuk', batchId: asal.batchId } : {}) }],
    gudang: { merk, kgKarung: kg, dariKg: t.kg, keKg: sesudah, dariKarung: t.karung, keKarung: Math.max(0, Math.floor((sesudah + 0.0001) / kg)) },
    patch: { kabar: 'Satu karung ' + merk + ' ' + kg + ' kg ' + (masuk ? 'yang baru datang dari pemasok' : 'diambil dari tumpukan gudang') + (di ? ', dibuka di belakang wadah ' + di : ' (karung bahan campuran)') + ' — tumpukan ' + merk + ': ' + wdKG(t.kg) + ' → ' + wdKG(sesudah)
      + (sesudah < -0.0001 ? '. MENURUT BUKU tumpukannya tidak sampai satu karung — tetap dicatat; cocokkan stok ' + merk : ''), kabarAwas: sesudah < -0.0001 } };
}
/**
 * Pintu ketiga (owner 28 Sep "hasil produksi"): satu KEMASAN JADI hasil adukan (25 / 50 kg) dibuka di belakang wadah. Stok kemasan turun 1 unit dan
 * berasnya masuk ke BUKU SENDIRI 'Adukan <nama> <ukuran> kg' (owner 28 Sep: hasil produksi beda dari beli pemasok — tidak dicampur ke buku merek pemasok),
 * modal = modal kemasan itu — satu dokumen produksiKemasan jadi-karung-utuh dengan sumberKemasanList (pola "kemasan jadi dibongkar" 26 Agu yang sudah
 * dibaca mesin beku). Karung terbukanya bernama buku itu; takarnya nanti memindah buku itu ke stok wadah.
 */
export function susunBukaKemasan(nama, ukuran, w, wadah) {
  const N = String(nama || '').trim(); const uk = Number(ukuran) || 0; const di = wadah && aturWadah().daftar.indexOf(wadah) >= 0 ? wadah : '';
  if (!N || !(uk > 0)) return { tolak: 'Pilih dulu kemasan hasil adukan yang dibuka' };
  const km = hitungStokKemasan()[kunciKemasan(N, uk)];
  if (!km || !((km.sisaUnit || 0) >= 1)) return { tolak: N + ' ' + uk + ' kg tidak ada di stok kemasan jadi — catat adukannya dulu' };
  const hppU = km.hppRataRataPerUnit || 0; const B = kunciBukuAdukan(N, uk); const dokumen = []; const lahir = wbDokLahir([{ merk: B, bukuAdukan: kunciKemasan(N, uk) }], w); if (lahir) dokumen.push(lahir);
  const idP = w.idUnik();
  dokumen.push({ koleksi: 'produksiKemasan', data: { id: idP, tanggal: w.tanggal, jam: w.jam, merkSumber: '', namaProduk: N, ukuranKemasan: uk, jumlahUnit: 1, biayaKemasan: 0, upahRepacking: 0, kantongJenis: null, kantongJumlah: 0,
    hppSumberPerKgDipakai: hppU / uk, hppPerUnit: hppU, sumberList: [], kgDipakai: uk, sumberKemasanList: [{ namaProduk: N, ukuranKemasan: uk, unit: 1 }], kgKemasanDipakai: uk,
    batchProduksi: idP, barisKe: 1, jumlahBaris: 1, jadiKarungUtuh: true, merkTujuan: B, bukaKemasan: true, keterangan: 'Buka 1 ' + N + ' ' + uk + ' kg hasil adukan ' + (di ? 'di belakang wadah ' + di : 'jadi karung bahan campuran') } });
  dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karung', merk: B, kg: uk }, di ? { wadah: di } : { lepas: true }, { asal: 'adukan', produksiId: idP }) });
  const n0 = km.sisaUnit || 0;
  return { dokumen, merk: B, gudang: { merk: B, kgKarung: uk, dariKg: n0 * uk, keKg: (n0 - 1) * uk, dariKarung: n0, keKarung: n0 - 1 }, patch: { kabar: 'Satu kemasan ' + N + ' ' + uk + ' kg hasil adukan dibuka' + (di ? ' di belakang wadah ' + di : ' (karung bahan campuran)') + ' — stok kemasan ' + N + ' ' + uk + ' kg: ' + (km.sisaUnit || 0) + ' → ' + ((km.sisaUnit || 0) - 1)
    + ' unit, berasnya pindah ke buku sendiri ' + B + ' (modal ikut, laba tidak berubah; tidak dicampur ke buku merek pemasok)', kabarAwas: false } };
}
/** Tiga pintu karung di belakang wadah: tumpukan gudang · baru datang dari pemasok (kedatangan `hari` hari terakhir) · kemasan jadi hasil adukan (≥ 25 kg). */
export function calonBukaKarung(hari) {
  const batas = hariIniIso(new Date(Date.now() - (Number(hari) || 14) * 86400000)); const masuk = [];
  ambilSemuaBatch().forEach((b) => { if (b.stokAwal || b.tutupBuku || (b.tanggal || '') < batas) return;
    (b.merkList || []).forEach((m) => { if (m.satuan !== 'karung' || !(Number(m.jumlahKarung) > 0)) return;
      masuk.push({ batchId: b.id, tanggal: b.tanggal || '', jam: b.jam || '', pemasok: b.pemasok || '', merk: String(m.merk), berat: Number(m.beratKarung) || 50, karung: Number(m.jumlahKarung) || 0 }); }); });
  masuk.sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam) || a.merk.localeCompare(b.merk));
  const km = hitungStokKemasan(); const adukan = Object.keys(km).map((k) => km[k]).filter((x) => (x.sisaUnit || 0) >= 1 && Number(x.ukuranKemasan) >= 25)
    .map((x) => ({ namaProduk: x.namaProduk, ukuran: Number(x.ukuranKemasan), unit: x.sisaUnit, modal: x.hppRataRataPerUnit || 0 })).sort((a, b) => a.namaProduk.localeCompare(b.namaProduk) || b.ukuran - a.ukuran);
  return { tumpukan: calonKarung(), masuk, adukan };
}
/** SAMAKAN karung terbuka dengan kenyataan: sisanya memang segini. wadah = di belakang wadah mana karung itu berada (menetapkan nama karung wadah itu). */
export function susunSamakanKarung(merk, isiKg, w, wadah) {
  const kg = Math.round(wdAngka(isiKg) * 10) / 10;
  if (!merk) return { tolak: 'Pilih dulu karung apa yang terbuka' };
  if (String(isiKg === undefined || isiKg === null ? '' : isiKg).trim() === '') return { tolak: 'Ketik dulu sisa karungnya (kg) — kotak isiannya masih kosong' };
  const penuh = beratKarungBuka(merk);
  if (!(kg >= 0) || kg > penuh) return { tolak: 'Sisa karung harus di antara 0 dan ' + penuh + ' kg' };
  const di = wadah && aturWadah().daftar.indexOf(wadah) >= 0 ? wadah : '';
  return { dokumen: [{ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk, isiKg: kg }, di ? { wadah: di } : (wadah === '' ? { lepas: true } : {})) }],
    patch: { kabar: 'Karung terbuka ' + merk + (di ? ' di belakang wadah ' + di : '') + ' disamakan: sisanya ±' + wdKG(kg), kabarAwas: false } };
}

/** Beras yang boleh ditaruh di satu kotak wadah: yang punya harga literan dan belum punya wadah. */
export function calonBerasWadah(daftar) { return ambilHargaLiteran().map((x) => String(x.merk || '')).filter((m, i, a) => m && a.indexOf(m) === i && (daftar || []).indexOf(m) < 0).sort(); }
/** Karung yang boleh dicampurkan ke wadah: yang menurut buku masih punya beras, di luar yang sudah ada di campuran. */
export function calonCampur(sudahAda) {
  const stok = stokMerekSaja(hitungStokKarungPerMerk()); const ada = sudahAda || [];
  return Object.keys(stok).filter((m) => stok[m].sisaKg > 0 && ada.indexOf(m) < 0).sort();
}
/** Karung sumber di GUDANG yang bisa dibuka di belakang wadah: tiap nama di buku yang tumpukannya masih ada, dengan banyak karungnya. */
export function calonKarung() {
  const siap = { stok: hitungStokKarungPerMerk(), pindah: pindahNama(), kolam: semuaKarungTerbuka(), bagian: wbBagianMerk() };
  return Object.keys(stokMerekSaja(siap.stok)).sort().map((m) => tumpukanGudang(m, siap)).filter((t) => t.adaBuku && t.kg > 0);
}
/**
 * Beras yang PINDAH NAMA lewat takar: takar dari karung K yang dituang ke wadah N (K ≠ N) dijual — dan dipotong dari buku — sebagai N.
 * Sejak keputusan owner A (22 Sep) takar lintas nama juga MEMINDAHKAN BUKU (dokumen produksiKemasan 'jadi karung utuh', lihat susunTakarWadah) —
 * takar yang punya `produksiId` dan dokumennya ada TIDAK dihitung lagi di sini (sudah ada di buku). Yang dihitung hanya catatan LAMA (sebelum
 * pindah buku) dan hanya yang SESUDAH hitungan gudang ("cocokkan") terakhir nama itu — hitungan fisik menyamakan buku dengan kenyataan, jadi
 * pindahan sebelum itu sudah termasuk di dalamnya (menghitungnya lagi = dipotong dua kali).
 */
/** Dokumen penyesuaianStok yang benar-benar HITUNGAN FISIK: index.html juga menulis rework karantina ke koleksi ini ({dariRework, kgFisik null}) — itu cuma menambah buku, bukan menyamakan buku dengan gudang. */
export const hitunganFisik = (o) => !!o && !o.dariRework && o.kgFisik !== null && o.kgFisik !== undefined;
// putaran 31.3 (serah terima 28 Sep, aturan kerja): catatan BERTANGGAL MUNDUR (barang masuk / adukan) yang tanggalnya sebelum cocokkan terakhir nama itu
// memotong buku dua kali — hitungan fisik hari itu sudah memuat karungnya, lalu kg catatan ini ditambahkan lagi. Penjaga dua ketukan, kalimat menyebut tanggal
// cocokkan terakhir. Isi ulang wadah & pindah stok selalu bertanggal hari ini (tidak bisa mundur). Sumber tanggal = pola putaran 11 (hitunganFisik, bukan wadah).
/** Cocokkan terakhir satu nama karung (hitungan fisik tumpukan; rework & cocokkan wadah tidak ikut) → { tanggal, jam } | null. */
export function ckCocokTerakhir(merk) {
  let t = null; ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p) || p.bagian === 'wadah' || String(p.merk) !== String(merk) || !p.tanggal) return; if (!t || String(p.tanggal) > t.tanggal || (String(p.tanggal) === t.tanggal && String(p.jam || '') > t.jam)) t = { tanggal: String(p.tanggal), jam: String(p.jam || '') }; });
  return t;
}
/** Cocokkan terakhir satu kemasan jadi (nama + ukuran) → { tanggal, jam } | null. */
export function ckCocokTerakhirKemasan(nama, ukuran) {
  let t = null; ambilPenyesuaianKemasan().forEach((p) => { if (String(p.namaProduk) !== String(nama) || Number(p.ukuranKemasan) !== Number(ukuran) || !p.tanggal) return; if (!t || String(p.tanggal) > t.tanggal || (String(p.tanggal) === t.tanggal && String(p.jam || '') > t.jam)) t = { tanggal: String(p.tanggal), jam: String(p.jam || '') }; });
  return t;
}
/** Kalimat penjaga tanggal mundur untuk daftar {nama, cocok} yang tanggal catatannya < cocok.tanggal; '' = tidak ada. */
export function ckKalimatMundur(tanggal, daftar, apa) {
  const m = (daftar || []).filter((x) => x.cocok && String(x.cocok.tanggal) > String(tanggal)); if (!m.length) return '';
  return 'Tanggal ' + apa + ' ' + tanggal + ' lebih AWAL dari cocokkan terakhir ' + m.map((x) => x.nama + ' (' + x.cocok.tanggal + (x.cocok.jam ? ' ' + x.cocok.jam : '') + ')').join(', ') + ' — hitungan fisik hari itu sudah memuat barangnya, jadi buku akan terpotong dua kali. Ketuk sekali lagi kalau memang benar; biasanya catat bertanggal hari ini';
}

export function pindahNama() {
  const cocokAkhir = {}; ambilPenyesuaianStok().forEach((o) => { if (o.merk && hitunganFisik(o) && (!cocokAkhir[o.merk] || wdSesudah(o, cocokAkhir[o.merk]))) cocokAkhir[o.merk] = o; });
  const keluar = {}; const masuk = {}; const diBuku = {}; ambilProduksiBerlaku().forEach((p) => { if (p.dariTakar) diBuku[String(p.id)] = 1; });
  ambilWadahLiteran().forEach((t) => { if (t.tipe !== 'takar' || !t.wadah) return;
    if (t.produksiId !== undefined && t.produksiId !== null && diBuku[String(t.produksiId)]) return;   // sudah pindah di BUKU
    if (t.bukuAsal) return;   // putaran 27: takar model baru tidak memindah nama — kg-nya milik merek asal di komposisi wadah (wadah-bernama-logika.js)
    (t.sumber || []).forEach((x) => { const kg = Number(x.kg) || 0; if (!x.merk || x.merk === t.wadah || !(kg > 0)) return;
      if (!cocokAkhir[x.merk] || wdSesudah(t, cocokAkhir[x.merk])) keluar[x.merk] = wdB2((keluar[x.merk] || 0) + kg);
      if (!cocokAkhir[t.wadah] || wdSesudah(t, cocokAkhir[t.wadah])) masuk[t.wadah] = wdB2((masuk[t.wadah] || 0) + kg); }); });
  return { keluar, masuk };
}
/**
 * RANTAI STOK satu nama beras — tiap tingkat berkurang lewat jalurnya sendiri, dan jumlahnya selalu menutup:
 *     TUMPUKAN GUDANG  = beras nama itu di toko − karung terbuka − isi wadah
 *     beras nama itu   = BUKU mesin lama − yang pindah nama keluar + yang pindah nama masuk (takar campuran, lihat pindahNama)
 *   buka karung → tumpukan −1 karung, karung terbuka +1 karung · takar → karung terbuka turun, wadah naik · literan TERJUAL → wadah & buku turun.
 * Dipakai angka MENTAH (tanpa jepitan nol): lupa mencatat isi ulang membuat wadah "minus" dan karung "kelebihan" sebesar itu juga — saling menutup,
 * jadi tumpukan tidak ikut bergeser diam-diam. Yang belum pernah ditandai DISEBUT (lengkap:false), tidak ditebak.
 */
export function tumpukanGudang(merk, siap) {
  const buku = ((siap && siap.stok) || hitungStokKarungPerMerk())[merk]; if (!buku) return { merk, adaBuku: false };
  const kolam = ((siap && siap.kolam) || semuaKarungTerbuka()).filter((k) => k.merk === merk); const w = tinggiWadah(merk, null); const p = (siap && siap.pindah) || pindahNama();
  const keluarKg = p.keluar[merk] || 0; const masukKg = p.masuk[merk] || 0; const pemegang = wadahPemegang(merk);
  // putaran 27: beras nama ini di WADAH = bagiannya di komposisi SEMUA wadah (model lama: isi wadah senama seluruhnya milik nama wadah — angka yang sama)
  const bagian = (siap && siap.bagian) || wbBagianMerk();
  const diBelakang = wdB2(kolam.reduce((a, k) => a + k.sisaMentahKg, 0)); const diWadah = wdB2(bagian[merk] || 0);
  const namaKg = wdB2(buku.sisaKg - keluarKg + masukKg); const kg = wdB2(namaKg - diBelakang - diWadah); const berat = beratKarungBuka(merk);
  return { merk, adaBuku: true, bukuKg: buku.sisaKg, pindahKeluarKg: keluarKg, pindahMasukKg: masukKg, namaKg, diBelakangKg: diBelakang, diWadahKg: diWadah, kg, beratKarung: berat,
    karung: Math.max(0, Math.floor((kg + 0.0001) / berat)), punyaWadah: !!w || Math.abs(diWadah) > 0.0005, wadahDiketahui: !w || !!w.diketahui, karungDiketahui: kolam.length > 0, karungDiWadah: pemegang[0] || '', kolam: kolam.length, dipegang: pemegang.filter((x) => karungUntukWadah(x).dariCatatan),
    // lengkap = isi wadahnya diketahui, dan tiap wadah yang memegang karung nama ini sudah menandai karungnya (belum ditandai → angka ini perkiraan)
    lengkap: (!w || w.diketahui) && pemegang.every((x) => kolam.some((k) => k.lokasi === x)), minus: kg < -0.0001 };
}
/** Hitung satu isian takar (belum menulis): kg tiap merek, isi wadah jadinya, karung yang perlu dibuka. */
export function hitungTakar(merk, baris, s) {
  const atur = aturWadah(); const w = tinggiWadah(merk, s);
  const bersih = (baris || []).filter((x) => x && x.merk && Number(x.takar) > 0).map((x) => Object.assign({ merk: String(x.merk), takar: Math.round(Number(x.takar)) }, x.dari !== undefined && x.dari !== null ? { dari: String(x.dari) } : {}));
  // baris boleh menyebut karung MANA di deretan yang diambil (dari = di belakang wadah mana / '' = karung lepas) — owner 23 Sep: satu takar dari E, satu dari D
  const sumber = bersih.map((x) => { const kg = wdB2(x.takar * atur.takarKg); const dari = x.dari !== undefined && x.dari !== null ? String(x.dari) : lokasiSumber(x.merk, merk); const k = karungBelakang(x.merk, dari);
    const kurang = k.diketahui ? kg - k.sisaKg : 0;   // karung yang belum pernah ditandai TIDAK dibuka diam-diam — sisanya memang belum diketahui
    const buka = kurang > 0.0001 ? Math.ceil((kurang - 0.0001) / beratKarungBuka(x.merk)) : 0;
    return { merk: x.merk, takar: x.takar, kg, dari, karung: k, bukaKarung: buka }; });
  const takar = sumber.reduce((a, x) => a + x.takar, 0); const kg = wdB2(sumber.reduce((a, x) => a + x.kg, 0));
  const isiBaru = w && w.diketahui ? wdB2(w.sisaNyataKg + kg) : null;
  return { wadah: w, sumber, takar, kg, isiBaru, lewat: isiBaru !== null && isiBaru > atur.puncakKg + 0.0001, takarKg: atur.takarKg, puncakKg: atur.puncakKg, penuhKg: atur.penuhKg,
    banding: sumber.length > 1 ? sumber.map((x) => x.takar).join(' : ') : '' };
}
/** Berapa kali campuran ini harus diulang supaya wadah sampai targetKg (rata / menggunung) — dibulatkan ke BAWAH, tidak pernah melewati target. */
export function takarSampai(merk, baris, targetKg, s) {
  const atur = aturWadah(); const w = tinggiWadah(merk, s); if (!w || !w.diketahui) return null;
  const dasar = (baris && baris.length ? baris : resepWadah(merk)).filter((x) => Number(x.takar) > 0); const satu = dasar.reduce((a, x) => a + Number(x.takar), 0);
  if (!satu) return null;
  // perbandingan dasar = resep dibagi FPB-nya, supaya "2:1 × 8 putaran" tetap 2:1
  const fpb = (a, b) => (b ? fpb(b, a % b) : a); const g = dasar.reduce((a, x) => fpb(a, Math.round(Number(x.takar))), 0) || 1;
  const pola = dasar.map((x) => ({ merk: x.merk, takar: Math.round(Number(x.takar)) / g })); const polaTakar = pola.reduce((a, x) => a + x.takar, 0);
  const putaran = Math.max(0, Math.floor((targetKg - w.sisaNyataKg + 0.0001) / (polaTakar * atur.takarKg)));
  return pola.map((x) => ({ merk: x.merk, takar: x.takar * putaran }));
}
/**
 * CATAT ISI ULANG: takar-takar ini dituang ke wadah. Satu dokumen 'takar' (sumber[].dari = tempat karung asalnya) + dokumen 'karung' lebih dulu bila karung di tempat itu tidak cukup.
 * Takar dari karung SENAMA: alat ukur saja — buku tidak disentuh (literan tetap memotong buku saat TERJUAL; memotongnya lagi = dipotong dua kali).
 * Takar dari karung NAMA LAIN (keputusan owner A, 22 Sep): berasnya berpindah nama di BUKU — keluar dari karung asalnya, masuk ke nama wadah dengan
 * MODAL karung asalnya. Ditulis sebagai satu dokumen produksiKemasan 'jadi karung utuh' (sumberList = karung asal, merkTujuan = nama wadah): jalur
 * yang sudah dibaca hitungStokKarungPerMerk di DUA sistem (mesin beku tidak disentuh; pembuatannya dari layar Adukan dicabut 23 Agu, pembacaannya tetap).
 * Semua dokumen satu catat masuk satu writeBatch — ada semua atau tidak sama sekali.
 */
export function susunTakarWadah(merk, baris, w, s) {
  const atur = aturWadah();
  if (atur.daftar.indexOf(merk) < 0) return { tolak: merk + ' bukan wadah kotak — literannya diserok langsung dari karung' };
  const h = hitungTakar(merk, baris, s);
  if (!h.takar) return { tolak: 'Belum ada takar — ketuk + untuk tiap takar yang dituang' };
  if (!h.wadah.diketahui) return { tolak: 'Wadah ' + merk + ' belum pernah disamakan dengan kenyataan — tandai dulu isinya sekarang (rata / menggunung / angka), baru takarnya bisa dihitung' };
  if (h.lewat) return { tolak: 'Isian ini membuat wadah jadi ' + wdKG(h.isiBaru) + ', melebihi ' + wdKG(atur.puncakKg) + ' yang muat. Kurangi takarnya — layar tidak memotong diam-diam.' };
  if (h.sumber.length > WADAH_MAKS_RESEP) return { tolak: 'Campuran paling banyak ' + WADAH_MAKS_RESEP + ' karung berbeda' };
  const dokumen = [];
  const gudang = [];
  h.sumber.forEach((x) => { if (!x.bukaKarung) return; const berat = beratKarungBuka(x.merk); const t = tumpukanGudang(x.merk);
    for (let i = 0; i < x.bukaKarung; i++) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karung', merk: x.merk, kg: berat, otomatis: true }, x.dari ? { wadah: x.dari } : { lepas: true }) });
    if (t.adaBuku) gudang.push({ merk: x.merk, kgKarung: berat, dariKg: t.kg, keKg: wdB2(t.kg - berat * x.bukaKarung) }); });
  // putaran 28 (owner 28 Sep): wadah berstok sendiri — takar MEMINDAHKAN BUKU dari merek karung asalnya ke buku wadah (modal ikut), satu dokumen
  // pindah buku untuk semua karung dalam isian ini; literannya nanti cuma memotong buku wadah. Karung tanpa buku ditolak (berasnya tidak boleh muncul dari
  // udara di buku wadah).
  if (wbAktif(merk)) {
    const stokT = hitungStokKarungPerMerk(); const tanpa = h.sumber.filter((x) => !stokT[x.merk]);
    if (tanpa.length) return { tolak: 'Karung ' + tanpa.map((x) => x.merk).join(', ') + ' tidak punya buku di gudang — catat barang masuknya dulu, baru takarnya bisa memindah buku ke stok wadah' };
    const idT = w.idUnik(); const kunci = wbKunci(merk);
    const pindah = wbDokPindah(h.sumber.map((x) => ({ merk: x.merk, kg: x.kg })), kunci, w, { takarId: idT, keterangan: 'Takar wadah ' + merk + ': ' + h.sumber.map((x) => x.merk + ' ' + wdKG(x.kg)).join(' + ') + ' → ' + kunci });
    const lahir = wbDokLahir([{ merk: kunci, stokWadah: merk }], w); if (lahir) dokumen.push(lahir);
    dokumen.push({ koleksi: 'wadahLiteran', data: { id: idT, tanggal: w.tanggal, jam: w.jam, tipe: 'takar', wadah: merk, takar: h.takar, kgPerTakar: atur.takarKg, kg: h.kg,
      sumber: h.sumber.map((x) => ({ merk: x.merk, takar: x.takar, kg: x.kg, dari: x.dari })), stokWadah: kunci, produksiId: pindah.data.id } });
    dokumen.push(pindah);
    const dibukaA = h.sumber.filter((x) => x.bukaKarung); const butaA = h.sumber.filter((x) => !x.karung.diketahui);
    const minusA = h.sumber.filter((x) => ((stokT[x.merk] || {}).sisaKg || 0) - x.kg < -0.004);
    return { dokumen, hitung: h, gudang, pindahBuku: pindah.data,
      patch: { kabar: 'Wadah ' + merk + ' diisi ' + h.takar + ' takar = ' + wdKG(h.kg) + (h.sumber.length > 1 ? ' (' + h.sumber.map((x) => 'karung ' + x.merk + ' ' + x.takar).join(' + ') + ')' : ' dari karung ' + h.sumber[0].merk) + ' → isinya ±' + wdKG(h.isiBaru)
        + ' · BUKU: ' + h.sumber.map((x) => x.merk + ' −' + wdKG(x.kg)).join(', ') + ' → ' + kunci + ' +' + wdKG(h.kg) + ' (modal ikut)'
        + (dibukaA.length ? ' · karung di belakang habis: ' + dibukaA.map((x) => x.bukaKarung + ' karung ' + x.merk).join(', ') + ' diambil dari tumpukan' + (gudang.length ? ' gudang (' + gudang.map((g) => g.merk + ' ' + wdKG(g.dariKg) + ' → ' + wdKG(g.keKg)).join(', ') + ')' : '') : '')
        + (minusA.length ? ' · buku ' + minusA.map((x) => x.merk).join(', ') + ' jadi MINUS — cocokkan tumpukannya' : '')
        + (butaA.length ? ' · karung terbuka ' + butaA.map((x) => x.merk).join(', ') + ' belum pernah ditandai, jadi sisanya belum bisa digambar' : ''), kabarAwas: !!minusA.length } };
  }
  // putaran 27 (Bagian 5, owner 27 Sep): takar TIDAK lagi memindahkan buku ke nama wadah — kg tiap takar tetap milik MEREK ASAL karungnya (komposisi wadah);
  // literannya nanti memotong buku merek-merek asal itu saat terjual. Dokumen takar bertanda bukuAsal. (Pindah buku lama tetap terbaca untuk catatan lama.)
  // (catatan lama: dulu takar lintas nama menulis produksiKemasan jadi-karung-utuh + produksiId — tetap terbaca oleh pindahNama/komposisi.)
  const idTakar = w.idUnik();
  dokumen.push({ koleksi: 'wadahLiteran', data: { id: idTakar, tanggal: w.tanggal, jam: w.jam, tipe: 'takar', wadah: merk, takar: h.takar, kgPerTakar: atur.takarKg, kg: h.kg,
    sumber: h.sumber.map((x) => ({ merk: x.merk, takar: x.takar, kg: x.kg, dari: x.dari })), bukuAsal: true } });
  const dibuka = h.sumber.filter((x) => x.bukaKarung); const buta = h.sumber.filter((x) => !x.karung.diketahui);
  const lintas = h.sumber.some((x) => x.merk !== merk);
  return { dokumen, hitung: h, gudang, pindahBuku: null,
    patch: { kabar: 'Wadah ' + merk + ' diisi ' + h.takar + ' takar = ' + wdKG(h.kg) + (h.sumber.length > 1 || lintas ? ' (' + h.sumber.map((x) => 'karung ' + x.merk + ' ' + x.takar).join(' + ') + ')' : '') + ' → isinya ±' + wdKG(h.isiBaru)
      + (dibuka.length ? ' · karung di belakang habis: ' + dibuka.map((x) => x.bukaKarung + ' karung ' + x.merk).join(', ') + ' diambil dari tumpukan' + (gudang.length ? ' gudang (' + gudang.map((g) => g.merk + ' ' + wdKG(g.dariKg) + ' → ' + wdKG(g.keKg)).join(', ') + ')' : '') : '')
      + (lintas ? ' · buku tiap merek TIDAK dipindah — isinya tercatat per merek asal, literannya memotong buku merek asal saat terjual' : '')
      + (buta.length ? ' · karung terbuka ' + buta.map((x) => x.merk).join(', ') + ' belum pernah ditandai, jadi sisanya belum bisa digambar' : ''), kabarAwas: false } };
}

/**
 * DERETAN karung terbuka di belakang deretan wadah (foto toko 23 Sep: karung 50 kg yang sudah dibuka berjajar di belakang kotak literan):
 * urut menurut posisi wadah W1..Wn (karung yang dipegang tiap wadah), lalu karung lepas / yatim. Satu wadah boleh diisi dari karung mana pun di deretan ini.
 */
export function deretanKarung() {
  const atur = aturWadah(); const out = []; const ada = {};
  atur.daftar.forEach((w, i) => { const kn = karungUntukWadah(w); if (!kn.merk) return; const k = karungBelakang(kn.merk, w); ada[k.merk + '|' + k.lokasi] = 1;
    out.push(Object.assign({}, k, { no: 'W' + (i + 1), letak: 'di belakang wadah ' + w, dicatat: kn.dariCatatan, label: k.merk + (k.diketahui ? ' ±' + wdKG(k.sisaKg) : ' ?') })); });
  const bw = petaBukuWadah();   // putaran 28: karung sisihan / bongkaran wadah = karung lepas bernama 'Karung wadah <nama>'
  semuaKarungTerbuka().forEach((k) => { if (ada[k.merk + '|' + k.lokasi] || k.sisaMentahKg <= 0.0001) return; ada[k.merk + '|' + k.lokasi] = 1;
    out.push(Object.assign({}, k, { no: '', letak: k.lokasi ? 'dulu di belakang wadah ' + k.lokasi : bw[k.merk] ? 'karung sisihan wadah ' + bw[k.merk].wadah : 'karung lepas (bahan campuran)', dicatat: true, label: k.merk + ' ±' + wdKG(k.sisaKg) })); });
  return out;
}
/** Tambah satu takar dari karung tertentu di deretan ke draf isian wadah (baris = merk + dari). */
export function tambahTakarDari(baris, merk, dari) {
  const d = (baris || []).map((x) => Object.assign({}, x)); const L = String(dari || '');
  const b = d.find((x) => x.merk === merk && String(x.dari === undefined || x.dari === null ? '' : x.dari) === L && x.dari !== undefined);
  if (b) b.takar += 1; else { const kosong = d.find((x) => x.merk === merk && x.dari === undefined && !(x.takar > 0)); if (kosong) { kosong.takar = 1; kosong.dari = L; } else d.push({ merk, takar: 1, dari: L }); }
  return d;
}

// ---------- BELANJA TERAKHIR orang bernama (owner 23 Sep): di jalur Sering, ketuk untuk mengulang dengan harga HARI INI ----------
const jlHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
/** Nota-nota terakhir orang yang sedang tertulis di keranjang (n terbaru), tiap nota = baris-barisnya. Tanpa nama → kosong. */
export function pembelianTerakhir(s, n) {
  const k = kunciPelanggan(s.pelanggan); if (!k) return [];
  const per = {}; ambilPenjualan().forEach((p) => { if (kunciPelanggan(p.namaPelanggan) !== k) return; const g = jlKunciNota(p);
    if (!per[g]) per[g] = { grup: g, tanggal: p.tanggal || '', jam: '', cara: bakuCaraBayar(p.caraBayar), baris: [], total: 0 }; per[g].baris.push(p); per[g].total += p.hargaTotal || 0; if (String(p.jam || '') > per[g].jam) per[g].jam = String(p.jam || ''); });
  const kini = jlHariKe(hariIniIso(s.sekarang));
  return Object.keys(per).map((g) => per[g]).sort((a, b) => (b.tanggal + b.jam).localeCompare(a.tanggal + a.jam)).slice(0, n || 3)
    .map((x) => Object.assign(x, { teks: x.baris.map(ringkasBaris).join(' + '), hariLalu: x.tanggal ? kini - jlHariKe(x.tanggal) : null }));
}
/** Ulangi satu nota lama ke keranjang: tiap barisnya dicari di rak SEKARANG (harga hari ini); yang tidak ada / melampaui stok dilewati dan DISEBUT. */
export function ulangiPembelian(s, rak, grup) {
  const nota = pembelianTerakhir(s, 12).find((x) => x.grup === String(grup)); if (!nota) return { kabar: 'Nota itu tidak ketemu di catatan ' + s.pelanggan, kabarAwas: true };
  const peta = {}; [].concat(rak.karung.map((c) => Object.assign({}, c, { id: 'karung|' + c.kunci + '|' + c.berat })), rak.kemasan.map((c) => Object.assign({}, c, { id: 'kemasan|' + c.kunci })), rak.literan.map((c) => Object.assign({}, c, { id: 'literan|' + c.kunci })),
    rak.repack.map((c) => Object.assign({}, c, { id: 'repack|' + c.kunci })), rak.wadah.map((c) => Object.assign({}, c, { id: 'wadah|' + c.kunci }))).forEach((c) => { peta[c.id] = c; });
  let sn = Object.assign({}, s, { keranjang: s.keranjang.slice(), urutBaris: s.urutBaris, rpWadah: '', rpLembar: '', rpUpah: '', namaRepack: '' }); const masuk = [], lewat = [];
  gabungTakaran(nota.baris).forEach((p) => { const id = kunciBaris(p); const c = id ? peta[id] : null; if (!c) { lewat.push(ringkasBaris(p) + ' (tidak ada di rak sekarang)'); return; }
    if (p.penggantiRetur) { lewat.push(ringkasBaris(p) + ' (pengganti retur, tidak diulang)'); return; }
    const j = p.jenis === 'kemasan' ? (p.jumlahUnit || 0) - (p.bonusUnit || 0) : p.jenis === 'karung' ? (p.jumlahKarung || 0) : p.jenis === 'literan' ? (p.jumlahLiter || 0) : p.jenis === 'repacking' ? (p.totalKg || 0) : (p.jumlahUnit || 0);
    const r = masukkan(Object.assign(sn, { pilih: c, ketik: '', namaRepack: p.jenis === 'repacking' ? (p.namaProduk || '') : '' }), j);
    if (r.keranjang) { sn = Object.assign(sn, { keranjang: r.keranjang, urutBaris: r.urutBaris }); masuk.push(ringkasBaris(p)); } else lewat.push(ringkasBaris(p) + ' — ' + (r.kabar || 'ditolak')); });
  sinkronKeranjang(s);
  if (!masuk.length) return { kabar: 'Tidak ada yang bisa diulang dari nota ' + tanggalPendek(nota.tanggal) + ': ' + lewat.join('; '), kabarAwas: true };
  return { keranjang: sn.keranjang, urutBaris: sn.urutBaris, pilih: null, lembar: null, ketik: '', kabar: 'Belanja ' + tanggalPendek(nota.tanggal) + ' diulang: ' + masuk.join(', ') + (lewat.length ? ' · dilewati: ' + lewat.join('; ') : '') + ' — dihitung dengan harga hari ini, bukan harga waktu itu', kabarAwas: lewat.length > 0 };
}
// ---------- BENANG di meja (owner 23 Sep: ojek yang belanja untuk orang lain): nama yang tertulis biasanya datang untuk siapa ----------
/** Bila nama di keranjang tercatat "biasa datang untuk" orang lain (pelangganTitip), tawarkan mencatat atas nama yang punya urusan. */
export function saranBenang(nama) {
  const k = kunciPelanggan(nama); if (!k) return null;
  const titip = cacheMentah('titip').filter((t) => t.dari === k && t.untuk).sort((a, b) => (b.kali || 0) - (a.kali || 0) || String(b.tanggal || '').localeCompare(String(a.tanggal || ''))); if (!titip.length) return null;
  const t = titip[0]; const kartu = ambilPelangganCatatan().find((c) => kunciPelanggan(c.nama || c.id) === t.untuk);
  let namaUntuk = kartu ? String(kartu.nama || kartu.id) : ''; if (!namaUntuk) { let idT = 0; ambilPenjualan().forEach((p) => { if (kunciPelanggan(p.namaPelanggan) === t.untuk && (Number(p.id) || 0) >= idT) { idT = Number(p.id) || 0; namaUntuk = String(p.namaPelanggan).trim(); } }); }
  if (!namaUntuk || kunciPelanggan(namaUntuk) === k) return null;
  return { dari: String(nama).trim(), untuk: namaUntuk, apa: String(t.apa || ''), kali: Number(t.kali) || 1, teks: String(nama).trim() + ' biasanya datang untuk ' + namaUntuk + (t.apa ? ' (' + t.apa + ', ' + (Number(t.kali) || 1) + '×)' : '') };
}

/**
 * KEMBALIKAN karung terbuka ke tumpukan (owner 23 Sep: karung lepas / yatim yang salah dibuka atau sudah dipindah lagi ke tumpukan).
 * Kalau sejak titik terakhir belum ada takar yang diambil dari karung itu dan yang ada cuma catatan "buka" → catatan bukanya DIHAPUS (tumpukan gudang pulih persis,
 * papan kapur tidak lagi menyebutnya). Kalau sudah ada takar / titik samakan → ditulis karungIsi 0 bertanda `dikembalikan` (sisanya kembali ke tumpukan lewat hitungan).
 * Ketukan kedua (yakin) wajib — ini mengubah angka tumpukan.
 */
export function susunKembalikanKarung(merk, lokasi, w, yakin) {
  const L = String(lokasi || ''); const k = karungBelakang(merk, L);
  if (!k.diketahui) return { tolak: 'Karung ' + merk + ' itu belum pernah ditandai — tidak ada yang perlu dikembalikan' };
  const daftar = aturWadah().daftar; const semua = ambilWadahLiteran(); const diSini = (d) => d.merk === merk && wdLokasiDoc(d, daftar) === L;
  const dasar = wdTerbaru(semua.filter((d) => d.tipe === 'karungIsi' && diSini(d))); const buka = semua.filter((d) => d.tipe === 'karung' && diSini(d) && (!dasar || wdSesudah(d, dasar)));
  const mulai = dasar || buka.reduce((a, x) => (!a || wdSesudah(a, x) ? x : a), null);
  const adaTakar = mulai && semua.some((t) => t.tipe === 'takar' && wdSesudah(t, mulai) && (t.sumber || []).some((x) => x.merk === merk && wdLokasiSumber(x, daftar) === L && Number(x.kg) > 0));
  const letak = L ? 'di belakang wadah ' + L : 'karung lepas';
  const bersih = !dasar && buka.length && !adaTakar;
  if (!yakin) return { tolak: 'Ketuk sekali lagi untuk mengembalikan karung ' + merk + ' (' + letak + ', sisa ±' + wdKG(k.sisaKg) + ') ke tumpukan gudang — ' + (bersih ? buka.length + ' catatan buka karungnya dihapus, tumpukan ' + merk + ' pulih ' + wdKG(buka.reduce((a, x) => a + (Number(x.kg) || KARUNG_BELAKANG_KG), 0)) : 'sisanya ' + wdKG(k.sisaKg) + ' dihitung kembali ke tumpukan'), perluYakin: true };
  if (bersih) return { hapus: buka.map((d) => ({ koleksi: 'wadahLiteran', id: d.id })), dokumen: [], patch: { kabar: 'Karung ' + merk + ' (' + letak + ') dikembalikan: ' + buka.length + ' catatan buka karung dihapus, tumpukan gudang ' + merk + ' pulih', kabarAwas: false, drPilih: null, krKetik: '' } };
  return { dokumen: [{ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk, isiKg: 0, dikembalikan: true, sisaSebelumKg: k.sisaKg }, L ? { wadah: L } : { lepas: true }) }],
    patch: { kabar: 'Karung ' + merk + ' (' + letak + ') dikembalikan ke tumpukan: sisa ±' + wdKG(k.sisaKg) + ' dihitung kembali ke tumpukan gudang ' + merk, kabarAwas: false, drPilih: null, krKetik: '' } };
}
