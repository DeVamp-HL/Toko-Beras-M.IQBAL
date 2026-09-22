// LAYAR STOK — LOGIKA (tanpa DOM). Beranda Stok S9 (dikunci owner) di atas DATA TOKO + tab Wadah literan (S15, bagian alat ukur).
//
// Empat pertanyaan papan S9, dijawab dari mesin yang sama dengan sistem lama:
//   1. Apa yang harus dibeli hari ini?   → laju jual 14 hari (hitungLajuPakai) × HARI_TARGET − sisa, dibulatkan ke karung penuh
//   2. Modal saya tidur di mana?         → NILAI DI BUKU = sisa × modal rata-rata mesin lama (hppTerakhirPerKg — namanya menyesatkan, isinya rata-rata
//      tertimbang; angka yang sama dengan Neraca sistem lama). Aturan owner 13 Sep "penilaian = harga beli TERBARU" ditampilkan sebagai
//      PEMBANDING berlabel (hargaTerakhirPerKg), bukan menggantikan — mengganti penilaian = mengubah mesin beku & laba historis = keputusan owner.
//   3. Apa yang tidak bergerak?          → tak ada gerak keluar 14 hari (TIDAK TERUKUR, bukan nol) atau cukup > 30 hari
//   4. Mana yang belum dicocokkan?       → hari sejak hitungan gudang terakhir (penyesuaianStok / penyesuaianKemasan)
//   5. Berasnya ada di mana? (owner 21 Sep) → RANTAI STOK: tumpukan gudang → karung terbuka di belakang wadah → kotak wadah. Buka karung
//      menurunkan TUMPUKAN saat itu juga; takar menurunkan karung & menaikkan wadah; literan terjual menurunkan wadah & buku. Jumlahnya menutup.
// Kejujuran: yang tidak bisa dihitung DISEBUT (tak ada laju, belum bisa dinilai, belum pernah dicocokkan) — tidak digambar nol.
// BACA SAJA kecuali tab Wadah (takar isi ulang, karung terbuka di belakang wadah, susunan & angka kebijakan → koleksi wadahLiteran, alat ukur bukan buku stok).
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungLajuPakai } from '../mesin/beku.js';
import { merkPunyaKarungBerat, JENDELA_LAJU_HARI, AMBANG_HARI_KRITIS } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilSemuaBatch, ambilProduksiBerlaku, ambilRetur, ambilKarantina, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilWadahLiteran } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';
import { tinggiWadah, aturWadah, resepWadah, karungBelakang, karungUntukWadah, wadahPemegang, semuaKarungTerbuka, tumpukanGudang, pindahNama, hitunganFisik } from './jual-logika.js';

export const HARI_TARGET = 7;      // "isi untuk tujuh hari" — angka papan S9; kebijakan owner
export const HARI_MANDEK = 30;     // sisa cukup untuk lebih dari ini = modal diam
export const HARI_COCOK_AWAS = 7;  // belum dicocokkan selama ini = perlu dihitung lagi
export const TAB_STOK = [['gudang', 'Gudang'], ['wadah', 'Wadah literan'], ['kapur', 'Papan Kapur'], ['karantina', 'Karantina']];

const skKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const skHari = (n) => String(Math.round(n * 10) / 10).replace('.', ',');
const skSelisihHari = (dariIso, keIso) => Math.round((new Date(keIso + 'T00:00:00') - new Date(dariIso + 'T00:00:00')) / 86400000);

/** Daftar barang gudang: tiap merek karung & tiap kemasan, dengan sisa, laju, hari-habis, nilai. */
export function daftarBarang() {
  const stokK = hitungStokKarungPerMerk(); const stokM = hitungStokKemasan(); const laju = hitungLajuPakai(); const out = [];
  Object.keys(stokK).sort().forEach((m) => {
    const sisa = stokK[m].sisaKg || 0; const l = (laju.kgMerk || {})[m] || 0; const hpp = stokK[m].hppTerakhirPerKg || 0;
    const terbaru = stokK[m].hargaTerakhirPerKg || 0;
    out.push({ jenis: 'karung', kunci: m, nama: m, satuan: 'kg', sisa, laju: l, hariHabis: l > 0 ? sisa / l : null, hpp, nilai: sisa * hpp, bisaDinilai: hpp > 0, hargaTerbaru: terbaru, nilaiTerbaru: sisa * (terbaru || hpp),
      beratKarung: merkPunyaKarungBerat(m, 50) ? 50 : (merkPunyaKarungBerat(m, 25) ? 25 : 50) });
  });
  Object.keys(stokM).sort().forEach((k) => {
    const st = stokM[k]; const sisa = st.sisaUnit || 0; const l = (laju.unitKemasan || {})[k] || 0; const hpp = st.hppRataRataPerUnit || 0;
    out.push({ jenis: 'kemasan', kunci: k, nama: st.namaProduk + ' ' + String(st.ukuranKemasan).replace('.', ',') + ' kg', satuan: 'unit', sisa, laju: l, hariHabis: l > 0 ? sisa / l : null, hpp, nilai: sisa * hpp, bisaDinilai: hpp > 0, hargaTerbaru: 0, nilaiTerbaru: sisa * hpp, ukuranKg: Number(st.ukuranKemasan) });
  });
  return out;
}

function jwbBeli(barang) {
  const baris = [], tak = [];
  barang.forEach((b) => {
    if (b.sisa <= 0 && b.laju <= 0) return;
    if (b.laju <= 0) { if (b.sisa > 0) tak.push(b.nama); return; }
    if (b.hariHabis > HARI_TARGET) return;
    const kurang = Math.max(0, b.laju * HARI_TARGET - b.sisa);
    const n = b.jenis === 'karung' ? Math.ceil(kurang / b.beratKarung) + ' karung' : 'aduk ' + Math.ceil(kurang) + ' unit';
    baris.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n, nKet: b.jenis === 'karung' ? b.beratKarung + ' kg' : 'kemasan', awas: b.hariHabis <= AMBANG_HARI_KRITIS,
      hari: Math.max(0, b.hariHabis), ket: 'sisa ' + (b.jenis === 'karung' ? skKG(b.sisa) : b.sisa + ' unit') + ' · laju ' + (b.jenis === 'karung' ? skKG(b.laju) : skHari(b.laju) + ' unit') + '/hari → habis ' + skHari(Math.max(0, b.hariHabis)) + ' hari',
      isi: Math.max(0, Math.min(1, b.hariHabis / HARI_TARGET)) });
  });
  baris.sort((a, b) => a.hari - b.hari);
  return { baris, rumus: 'isi untuk ' + HARI_TARGET + ' hari: (laju ' + JENDELA_LAJU_HARI + ' hari × ' + HARI_TARGET + ') − sisa, dibulatkan ke atas ke karung penuh', kosong: 'Tidak ada yang perlu dibeli untuk ' + HARI_TARGET + ' hari ke depan.',
    takTeks: tak.length ? tak.slice(0, 6).join(', ') + (tak.length > 6 ? ' …' : '') + ' tidak bisa dijawab — tak ada gerak keluar ' + JENDELA_LAJU_HARI + ' hari, lajunya belum bisa dihitung.' : '' };
}
function jwbModal(barang) {
  const berisi = barang.filter((b) => b.sisa > 0); const bisa = berisi.filter((b) => b.bisaDinilai); const total = bisa.reduce((a, b) => a + b.nilai, 0);
  const tak = berisi.filter((b) => !b.bisaDinilai).map((b) => b.nama); const maks = Math.max(1, ...bisa.map((b) => b.nilai));
  const totalTerbaru = bisa.reduce((a, b) => a + b.nilaiTerbaru, 0);
  return { total, totalTerbaru, baris: bisa.slice().sort((a, b) => b.nilai - a.nilai).map((b) => ({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: RP(b.nilai), nKet: total ? Math.round(b.nilai / total * 100) + '%' : '—', awas: false,
      ket: (b.jenis === 'karung' ? skKG(b.sisa) + ' × modal rata-rata ' + RP(b.hpp) + '/kg' + (b.hargaTerbaru ? ' · harga beli terbaru ' + RP(b.hargaTerbaru) : '') : b.sisa + ' unit × modal rata-rata ' + RP(b.hpp)), isi: b.nilai / maks })),
    rumus: 'nilai di buku = sisa × modal rata-rata (sama dengan Neraca sistem lama): ' + RP(total) + ' · bila dinilai HARGA BELI TERBARU: ' + RP(totalTerbaru) + ' (' + (totalTerbaru >= total ? '+' : '−') + RP(Math.abs(totalTerbaru - total)) + ')', kosong: 'Tidak ada stok yang bisa dinilai.',
    takTeks: tak.length ? tak.slice(0, 6).join(', ') + ' berisi barang tapi belum bisa dinilai — belum ada harga beli tercatat.' : '' };
}
function jwbMandek(barang) {
  const out = [];
  barang.forEach((b) => {
    if (b.sisa <= 0) return;
    if (b.laju <= 0) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai ? RP(b.nilai) : 'belum dinilai', nKet: 'modal diam', awas: true, urut: 1e9 + b.nilai, isi: 1,
      ket: (b.jenis === 'karung' ? skKG(b.sisa) : b.sisa + ' unit') + ' · tak ada gerak keluar ' + JENDELA_LAJU_HARI + ' hari — bukan nol, memang tidak terukur' });
    else if (b.hariHabis > HARI_MANDEK) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai ? RP(b.nilai) : 'belum dinilai', nKet: 'modal diam', awas: false, urut: b.nilai, isi: Math.min(1, b.hariHabis / 90),
      ket: (b.jenis === 'karung' ? skKG(b.sisa) : b.sisa + ' unit') + ' · cukup untuk ' + Math.floor(b.hariHabis) + ' hari dengan laju sekarang' });
  });
  out.sort((a, b) => b.urut - a.urut);
  return { baris: out, rumus: 'mandek = tak ada gerak keluar ' + JENDELA_LAJU_HARI + ' hari, atau sisa cukup untuk lebih dari ' + HARI_MANDEK + ' hari', kosong: 'Semua barang bergerak dalam ' + JENDELA_LAJU_HARI + ' hari terakhir.', takTeks: '' };
}
function jwbCocok(barang, hari) {
  const terakhir = {};
  ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p)) return; const k = 'karung|' + p.merk; if (p.tanggal && (!terakhir[k] || p.tanggal > terakhir[k])) terakhir[k] = p.tanggal; });   // rework karantina bukan hitungan gudang
  ambilPenyesuaianKemasan().forEach((p) => { const k = 'kemasan|' + p.namaProduk + '|' + p.ukuranKemasan; if (p.tanggal && (!terakhir[k] || p.tanggal > terakhir[k])) terakhir[k] = p.tanggal; });
  const out = barang.filter((b) => b.sisa > 0 || b.laju > 0).map((b) => {
    const tgl = terakhir[b.jenis + '|' + b.kunci] || null; const umur = tgl ? Math.max(0, skSelisihHari(tgl, hari)) : null;
    return { kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: umur === null ? 'belum pernah' : umur + ' hari', nKet: umur === null ? 'dicocokkan' : 'sejak cocok', awas: umur === null || umur >= HARI_COCOK_AWAS, umur: umur === null ? 1e6 : umur,
      ket: tgl ? 'cocok terakhir ' + tgl : 'belum ada hitungan gudang yang tercatat', isi: umur === null ? 1 : Math.min(1, umur / 30) };
  }).sort((a, b) => b.umur - a.umur);
  return { baris: out, rumus: 'umur = hari sejak hitungan gudang terakhir dicocokkan dengan catatan (≥ ' + HARI_COCOK_AWAS + ' hari = perlu dihitung lagi)', kosong: 'Belum ada barang di gudang.', takTeks: '' };
}

/**
 * RANTAI STOK per nama beras (kg, bukan rupiah): di TUMPUKAN gudang berapa karung, di KARUNG TERBUKA di belakang wadah berapa, di WADAH berapa.
 * Angkanya dari tumpukanGudang() — tumpukan = beras nama itu di toko − karung terbuka − isi wadah, jadi membuka satu karung langsung menurunkan tumpukan.
 */
export function susunLokasi() {
  const siap = { stok: hitungStokKarungPerMerk(), pindah: pindahNama(), kolam: semuaKarungTerbuka() };
  return Object.keys(siap.stok).sort().map((m) => tumpukanGudang(m, siap)).filter((t) => t.adaBuku && (Math.abs(t.bukuKg) > 0.004 || Math.abs(t.diBelakangKg) > 0.004 || Math.abs(t.diWadahKg) > 0.004 || t.pindahKeluarKg || t.pindahMasukKg));
}
function jwbLokasi() {
  const semua = susunLokasi(); const maks = Math.max(1, ...semua.map((t) => Math.max(0, t.kg)));
  const baris = semua.slice().sort((a, b) => b.kg - a.kg).map((t) => {
    const rantai = t.punyaWadah || t.karungDiWadah || Math.abs(t.diBelakangKg) > 0.004;
    const pindah = (t.pindahKeluarKg ? ' · ' + skKG(t.pindahKeluarKg) + ' sudah ditakar ke wadah nama lain' : '') + (t.pindahMasukKg ? ' · ' + skKG(t.pindahMasukKg) + ' masuk dari karung nama lain' : '');
    return { kunci: 'lokasi|' + t.merk, nama: t.merk, karung: t.minus ? 0 : t.karung, n: t.minus ? 'kurang' : t.karung + ' karung', nKet: t.minus ? 'cocokkan' : 'di tumpukan', awas: t.minus, isi: Math.max(0, t.kg) / maks,
      ket: (t.minus ? 'buku KURANG ' + skKG(-t.kg) + ' dari yang sudah di karung terbuka & wadah — cocokkan stok' : 'tumpukan ' + skKG(t.kg))
        + (rantai ? ' · karung terbuka ' + (t.karungDiketahui ? skKG(t.diBelakangKg) : t.karungDiWadah ? '? (belum ditandai)' : '—') + (t.punyaWadah ? ' · wadah ' + (t.wadahDiketahui ? skKG(t.diWadahKg) : '? (belum ditandai)') : '') : ' · semuanya di tumpukan')
        + ' · buku ' + skKG(t.bukuKg) + pindah + (t.lengkap ? '' : ' · perkiraan, ada yang belum ditandai') };
  });
  const karung = semua.reduce((a, t) => a + t.karung, 0);
  return { karung, baris, rumus: 'tumpukan gudang = beras nama itu di buku − karung terbuka di belakang wadah − isi wadah. Buka karung → tumpukan turun satu karung · takar → karung terbuka turun, wadah naik · literan terjual → wadah & buku turun. Hitungan gudang (cocokkan) = tumpukan + karung terbuka + isi wadah.',
    kosong: 'Belum ada beras karung di buku gudang.', takTeks: '' };
}

/** Tab Gudang: kartu pertanyaan + jawaban yang sedang dibuka. */
export function susunGudang(tanya, kini) {
  const hari = hariIniIso(kini); const barang = daftarBarang();
  const j = { beli: jwbBeli(barang), modal: jwbModal(barang), mandek: jwbMandek(barang), cocok: jwbCocok(barang, hari), lokasi: jwbLokasi() };
  const nCocok = j.cocok.baris.filter((x) => x.awas).length;
  const kartu = [
    { id: 'beli', q: 'Apa yang harus dibeli hari ini?', a: j.beli.baris.length ? j.beli.baris.length + ' barang' : 'tidak ada', awas: j.beli.baris.length > 0 },
    { id: 'modal', q: 'Modal saya tidur di mana?', a: RP(j.modal.total), angka: j.modal.total, awas: false },
    { id: 'mandek', q: 'Apa yang tidak bergerak?', a: j.mandek.baris.length ? j.mandek.baris.length + ' barang' : 'tidak ada', awas: j.mandek.baris.length > 0 },
    { id: 'cocok', q: 'Mana yang belum dicocokkan?', a: nCocok + ' barang', awas: nCocok > 0 },
    { id: 'lokasi', q: 'Berasnya ada di mana?', a: j.lokasi.karung + ' karung di tumpukan', awas: j.lokasi.baris.some((x) => x.awas) },
  ];
  const aktif = kartu.some((k) => k.id === tanya) ? tanya : 'beli';
  return { kartu, aktif, judul: kartu.find((k) => k.id === aktif).q, jawab: j[aktif], banyakBarang: barang.filter((b) => b.sisa > 0).length, totalNilai: j.modal.total };
}

/**
 * Tab Wadah literan (S15): kotak-kotak wadah MENURUT POSISINYA di toko (W1, W2, …), masing-masing dengan KARUNG TERBUKA BERNAMA di belakangnya
 * ("stok wadah" — owner 19 Sep; namanya diambil dari karung sumber di gudang — owner 21 Sep) dan TUMPUKAN karung nama itu di gudang.
 * lain = karung terbuka yang tidak di belakang wadah mana pun (bahan campuran, atau karung lama yang wadahnya sudah berganti karung).
 */
export function susunWadah(s) {
  const atur = aturWadah();
  const siap = { stok: hitungStokKarungPerMerk(), pindah: pindahNama(), kolam: semuaKarungTerbuka() };
  const daftar = atur.daftar.map((m, i) => { const kn = karungUntukWadah(m); return Object.assign({ no: 'W' + (i + 1), nama: m, resep: resepWadah(m), karungNama: kn.merk, karungDicatat: kn.dariCatatan, karung: karungBelakang(kn.merk, m), tumpukan: tumpukanGudang(kn.merk, siap) }, tinggiWadah(m, s)); });
  // karung terbuka lain: kolam yang tidak dipegang wadah mana pun (bahan campuran, atau YATIM: wadahnya kini memegang karung lain) + nama yang disebut
  // campuran/takar tapi belum pernah ditandai (supaya owner bisa membukanya dari sini) — tidak termasuk nama yang sedang dipegang sebuah wadah
  const lain = []; const ada = {};
  siap.kolam.forEach((k) => { if (k.wadah) return; ada[k.merk + '|' + k.lokasi] = 1; lain.push({ nama: k.merk, lokasi: k.lokasi, karung: k, tumpukan: tumpukanGudang(k.merk, siap) }); });
  const sebut = (m) => { if (!m || wadahPemegang(m).length || ada[m + '|']) return; ada[m + '|'] = 1; lain.push({ nama: m, lokasi: '', karung: karungBelakang(m, ''), tumpukan: tumpukanGudang(m, siap) }); };
  daftar.forEach((w) => w.resep.forEach((x) => sebut(x.merk)));
  ambilWadahLiteran().forEach((d) => { if (d.tipe === 'takar') (d.sumber || []).forEach((x) => sebut(x.merk)); });
  lain.sort((a, b) => a.nama.localeCompare(b.nama) || a.lokasi.localeCompare(b.lokasi));
  return { atur, daftar, lain, perluIsi: daftar.filter((w) => w.diketahui && w.perluIsi).length, belumDitandai: daftar.filter((w) => !w.diketahui).length,
    karungTipis: daftar.filter((w) => w.karung.diketahui && w.karung.sisaKg <= atur.takarKg * 3).length };
}

/** Papan Kapur: perubahan stok HARI INI, terbaru dulu. */
export function susunKapur(kini) {
  const hari = hariIniIso(kini); const out = [];
  ambilSemuaBatch().forEach((b) => { if (b.tanggal !== hari) return; (b.merkList || []).forEach((x, i) => out.push({ k: 'b' + b.id + i, jam: b.jam || '', isi: 'Barang masuk ' + x.merk + (x.jumlahKarung ? ' ' + x.jumlahKarung + ' karung' : '') + (b.pemasok ? ' · ' + b.pemasok : ''), n: '+' + skKG(x.totalKg || 0), jenis: 'masuk' })); });
  ambilProduksiBerlaku().forEach((p) => { if (p.tanggal !== hari) return;
    if (p.dariTakar) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Pindah nama di buku (takar wadah): ' + (p.sumberList || []).map((x) => x.merk + ' ' + skKG(x.kg || 0)).join(' + ') + ' → ' + (p.merkTujuan || ''), n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    else out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Adukan → ' + (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg', n: '+' + (p.jumlahUnit || 0) + ' unit', jenis: 'masuk' }); });
  ambilPenyesuaianStok().forEach((p) => { if (p.tanggal !== hari) return; out.push({ k: 'o' + p.id, jam: p.jam || '', isi: 'Cocokkan ' + (p.merk || '') + ' · sistem ' + skKG(p.kgSistem || 0) + ' → hitungan ' + skKG(p.kgFisik || 0), n: ((p.selisihKg || 0) > 0 ? '+' : '') + skKG(p.selisihKg || 0), jenis: 'opname' }); });
  ambilPenyesuaianKemasan().forEach((p) => { if (p.tanggal !== hari) return; out.push({ k: 'ok' + p.id, jam: p.jam || '', isi: 'Cocokkan ' + (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg', n: ((p.selisihUnit || 0) > 0 ? '+' : '') + (p.selisihUnit || 0) + ' unit', jenis: 'opname' }); });
  ambilRetur().forEach((r) => { if (r.tanggal !== hari) return; out.push({ k: 'r' + r.id, jam: r.jam || '', isi: 'Barang kembali ' + (r.merkSumber || r.namaProduk || '') + (r.kondisi === 'tidak_utuh' ? ' → Karantina' : ' → stok jual'), n: '+' + skKG(r.totalKg || 0), jenis: r.kondisi === 'tidak_utuh' ? 'opname' : 'masuk' }); });
  ambilWadahLiteran().forEach((w) => { if (w.tanggal !== hari) return;
    if (w.tipe === 'takar') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Wadah ' + (w.wadah || '') + ' diisi ulang ' + (w.takar || 0) + ' takar dari karung ' + (w.sumber || []).map((x) => x.merk + ((w.sumber || []).length > 1 ? ' ' + x.takar : '')).join(' + ') + ' — karung terbuka turun, wadah naik', n: '+' + skKG(w.kg || 0), jenis: 'wadah' });
    else if (w.tipe === 'isi') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Wadah ' + (w.wadah || '') + ' disamakan dengan kenyataan', n: '±' + skKG(w.isiKg || 0), jenis: 'wadah' });
    else if (w.tipe === 'karung') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Karung ' + (w.merk || '') + ' diambil dari tumpukan gudang, dibuka ' + (w.wadah ? 'di belakang wadah ' + w.wadah : w.lepas ? 'sebagai bahan campuran' : 'di belakang wadah') + (w.otomatis ? ' (otomatis — karung sebelumnya habis)' : ''), n: 'gudang −' + skKG(w.kg || 0), jenis: 'wadah' });
    else if (w.tipe === 'karungIsi') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Karung terbuka ' + (w.merk || '') + ' disamakan dengan kenyataan', n: '±' + skKG(w.isiKg || 0), jenis: 'wadah' }); });
  const jual = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== hari) return; const nm = p.jenis === 'kemasan' ? (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg' : (p.merkSumber || p.namaProduk || ''); const k = (p.jam || '').slice(0, 2) + '|' + nm;
    const o = jual[k] || (jual[k] = { jam: (p.jam || '').slice(0, 2) + '.00', nm, kg: 0, unit: 0, n: 0 }); o.n += 1; if (p.jenis === 'kemasan') o.unit += p.jumlahUnit || 0; else o.kg += p.totalKg || 0; if ((p.jam || '') > o.jam) o.jamAkhir = p.jam; });
  Object.keys(jual).forEach((k) => { const o = jual[k]; out.push({ k: 'j' + k, jam: o.jamAkhir || o.jam, isi: 'Terjual ' + o.nm + ' · ' + o.n + ' baris', n: '−' + (o.unit ? o.unit + ' unit' : skKG(o.kg)), jenis: 'keluar' }); });
  out.sort((a, b) => (b.jam || '').localeCompare(a.jam || ''));
  return { hari, baris: out.slice(0, 60), banyak: out.length };
}

/** Karantina: barang kembali yang belum diputuskan (baca saja di putaran ini). */
export function susunKarantina() {
  const baris = ambilKarantina().filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan')
    .map((k) => ({ k: String(k.id), nama: k.merkSumber || ((k.namaProduk || '') + ' ' + (k.ukuranKemasan || '') + ' kg'), kg: k.totalKg || 0, tanggal: k.tanggal || '', catatan: k.catatan || '' }));
  return { baris, totalKg: baris.reduce((a, x) => a + x.kg, 0) };
}
