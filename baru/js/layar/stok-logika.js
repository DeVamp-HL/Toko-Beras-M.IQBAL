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
import { hitungLajuPakai } from '../mesin/beku.js';
import { merkPunyaKarungBerat, JENDELA_LAJU_HARI, AMBANG_HARI_KRITIS } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilSemuaBatch, ambilProduksiBerlaku, ambilRetur, ambilKarantina, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilWadahLiteran, petaStokWadah, stokMerekSaja, petaBukuWadah, lajuLintas, ingatStokKarung, ingatStokKemasan } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';
import { tinggiWadah, aturWadah, resepWadah, karungBelakang, karungUntukWadah, wadahPemegang, semuaKarungTerbuka, tumpukanGudang, pindahNama, hitunganFisik, notaTembusBelumCocok, beratKarungBuka } from './jual-logika.js';
// putaran 27: isi wadah per merek asal
import { wbBagianMerk, wbKomposisi, wbMerkAsal, wbWadahBerisi, WB_CEK } from './wadah-bernama-logika.js';
// paket brief 9 Okt (butir 2): tab Umur & putaran — kedatangan per merek dari riwayat modal Stok › HPP (satu sumber), laju harian & buku per tanggal dari toko.js
import { riwayatModal } from './stok-hpp-logika.js';
import { lajuHarian, catatanPertama, tahunDiarsip, cacheMentah, ingatPerVersi } from '../data/toko.js';
import { KG, tanggalPendek } from '../inti/format.js';

export const HARI_TARGET = 7;      // "isi untuk tujuh hari" — angka papan S9; kebijakan owner
export const HARI_MANDEK = 30;     // sisa cukup untuk lebih dari ini = modal diam
export const HARI_COCOK_AWAS = 7;  // belum dicocokkan selama ini = perlu dihitung lagi
export const TAB_STOK = [['gudang', 'Gudang'], ['wadah', 'Wadah literan'], ['kapur', 'Papan Kapur'], ['karantina', 'Karantina'], ['umur', 'Umur & putaran']];   // paket brief 9 Okt: tab umur stok FIFO & perputaran

const skKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const skHari = (n) => String(Math.round(n * 10) / 10).replace('.', ',');
const skSelisihHari = (dariIso, keIso) => Math.round((new Date(keIso + 'T00:00:00') - new Date(dariIso + 'T00:00:00')) / 86400000);

/** Daftar barang gudang: tiap merek karung & tiap kemasan, dengan sisa, laju, hari-habis, nilai. */
export function daftarBarang() {
  const stokK = ingatStokKarung(); const stokM = ingatStokKemasan(); const laju = lajuLintas(hitungLajuPakai()); const out = []; const wadahStok = petaBukuWadah();
  Object.keys(stokK).sort().forEach((m) => {
    const sisa = stokK[m].sisaKg || 0; const l = (laju.kgMerk || {})[m] || 0; const hpp = stokK[m].hppTerakhirPerKg || 0;
    const terbaru = stokK[m].hargaTerakhirPerKg || 0;
    out.push({ jenis: 'karung', kunci: m, nama: m, satuan: 'kg', sisa, laju: l, hariHabis: l > 0 ? sisa / l : null, hpp, nilai: sisa * hpp, bisaDinilai: hpp > 0, hargaTerbaru: terbaru, nilaiTerbaru: sisa * (terbaru || hpp),
      beratKarung: merkPunyaKarungBerat(m, 50) ? 50 : (merkPunyaKarungBerat(m, 25) ? 25 : 50), wadahStok: !!wadahStok[m] });   // putaran 28: buku stok wadah ikut dinilai, tidak ikut daftar belanja
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
    if (b.wadahStok) return;   // stok wadah diisi dari karung di belakangnya, bukan dibeli
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
  const terakhir = {}; const catat = (k, t) => { if (t && (!terakhir[k] || t > terakhir[k])) terakhir[k] = t; }; const bw = petaBukuWadah();
  // putaran 27: cocokkan WADAH cuma menghitung bagian nama itu di wadah — tumpukannya belum dihitung, jadi tidak mengubah umur cocokkan nama itu.
  // 39b no. 15: buku KHUSUS (buku wadah, karung di belakang, karung sisihan — petaBukuWadah) justru dihitung UTUH oleh cocokkan wadah → umurnya ikut
  // 39b no. 5 tinjauan S6: buku ADUKAN tidak disegarkan penyesuaian bagian wadah (itu selisih ISI wadah yang kebagian adukan, karungnya belum tentu ditimbang)
  ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p) || (p.bagian === 'wadah' && (!bw[p.merk] || bw[p.merk].jenis === 'adukan'))) return; catat('karung|' + p.merk, p.tanggal); });   // rework karantina bukan hitungan gudang
  // cocokkan wadah yang PAS (tanpa selisih) tidak menulis penyesuaian — titik samakan isi (stokWadah) & isi karung terbuka bertanda dariCocok juga hitungan buku khusus itu
  ambilWadahLiteran().forEach((x) => { if (!x || !x.dariCocok) return; if (x.tipe === 'isi' && x.stokWadah && bw[x.stokWadah]) catat('karung|' + x.stokWadah, x.tanggal); if (x.tipe === 'karungIsi' && x.merk && bw[x.merk]) catat('karung|' + x.merk, x.tanggal); });
  // 39b no. 5 (tinjauan G5): buku ADUKAN yang sebagian isinya di wadah BELUM aktif baru dihitung utuh bila tiap wadah pemegangnya juga sudah dihitung —
  // umurnya = yang paling lama di antara karungnya & wadah-wadah itu (satu belum pernah → belum pernah)
  const isiW = {}; ambilWadahLiteran().forEach((x) => { if (x && x.tipe === 'isi' && x.wadah && !x.pindahAwal && !x.gantiNamaDari && x.tanggal && (!isiW[x.wadah] || x.tanggal > isiW[x.wadah])) isiW[x.wadah] = x.tanggal; });
  Object.keys(bw).forEach((k) => { if (bw[k].jenis !== 'adukan' || !terakhir['karung|' + k]) return; const pegang = wbWadahBerisi(k); if (!pegang.length) return;
    pegang.forEach((W) => { if (!terakhir['karung|' + k]) return; if (!isiW[W]) delete terakhir['karung|' + k]; else if (isiW[W] < terakhir['karung|' + k]) terakhir['karung|' + k] = isiW[W]; }); });
  ambilPenyesuaianKemasan().forEach((p) => { const k = 'kemasan|' + p.namaProduk + '|' + p.ukuranKemasan; if (p.tanggal && (!terakhir[k] || p.tanggal > terakhir[k])) terakhir[k] = p.tanggal; });
  const out = barang.filter((b) => b.sisa > 0 || b.laju > 0).map((b) => {
    const tgl = terakhir[b.jenis + '|' + b.kunci] || null; const umur = tgl ? Math.max(0, skSelisihHari(tgl, hari)) : null;
    return { kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: umur === null ? 'belum pernah' : umur + ' hari', nKet: umur === null ? 'dicocokkan' : 'sejak cocok', awas: umur === null || umur >= HARI_COCOK_AWAS, umur: umur === null ? 1e6 : umur,
      ket: tgl ? 'cocok terakhir ' + tgl : 'belum ada hitungan gudang yang tercatat', isi: umur === null ? 1 : Math.min(1, umur / 30) };
  }).sort((a, b) => b.umur - a.umur);
  // putaran 31b: nota "jual dulu, tandai untuk dicocokkan" yang belum tuntas — paling atas, per nama
  const TB = notaTembusBelumCocok(); const tembus = TB.nama.map((x) => ({ kunci: 'tembus|' + x.nama, nama: x.nama, n: skKG(x.kg) + ' tembus', nKet: 'belum dicocokkan', awas: true, umur: 1e7, ket: x.n + ' nota dijual melampaui buku — cocokkan nama ini (tanda tuntas sendiri saat cocokkan bertanggal ≥ notanya)', isi: 1 }));
  return { baris: tembus.concat(out), rumus: 'umur = hari sejak hitungan gudang terakhir dicocokkan dengan catatan (≥ ' + HARI_COCOK_AWAS + ' hari = perlu dihitung lagi); "tembus" = nota jual-dulu yang belum dicocokkan', kosong: 'Belum ada barang di gudang.', takTeks: '' };
}

/**
 * RANTAI STOK per nama beras (kg, bukan rupiah): di TUMPUKAN gudang berapa karung, di KARUNG TERBUKA di belakang wadah berapa, di WADAH berapa.
 * Angkanya dari tumpukanGudang() — tumpukan = beras nama itu di toko − karung terbuka − isi wadah, jadi membuka satu karung langsung menurunkan tumpukan.
 */
export function susunLokasi() {
  const siap = { stok: ingatStokKarung(), pindah: pindahNama(), kolam: semuaKarungTerbuka(), bagian: wbBagianMerk() };
  return Object.keys(stokMerekSaja(siap.stok)).sort().map((m) => tumpukanGudang(m, siap)).filter((t) => t.adaBuku && (Math.abs(t.bukuKg) > 0.004 || Math.abs(t.diBelakangKg) > 0.004 || Math.abs(t.diWadahKg) > 0.004 || t.pindahKeluarKg || t.pindahMasukKg));
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
  const siap = { stok: ingatStokKarung(), pindah: pindahNama(), kolam: semuaKarungTerbuka(), bagian: wbBagianMerk() };
  // putaran 39: karung di belakang wadah aktif bernama kunci bukunya — tumpukan & nama tampil memakai MEREK ASALNYA
  // putaran 39c: slot KOSONG (karung terakhir dikembalikan / habis dihapus) → kartu wadah menggambar karung "?" garis putus, bukan kolam lama yang sudah ditutup
  const daftar = atur.daftar.map((m, i) => { const kn = karungUntukWadah(m); const asal = wbMerkAsal(kn.merk); const kr = kn.kosong ? { merk: kn.merk, lokasi: m, diketahui: false, penuhKg: beratKarungBuka(asal), wadah: '', yatim: false, kosong: true, alasanKosong: kn.alasanKosong, terakhirMerk: kn.terakhirMerk } : karungBelakang(kn.merk, m);
    return Object.assign({ no: 'W' + (i + 1), nama: m, resep: resepWadah(m), karungNama: kn.merk, karungAsal: asal, karungDicatat: kn.dariCatatan, karung: kr, tumpukan: tumpukanGudang(asal, siap) }, tinggiWadah(m, s)); });
  // karung terbuka lain: kolam yang tidak dipegang wadah mana pun (bahan campuran, atau YATIM: wadahnya kini memegang karung lain) + nama yang disebut
  // campuran/takar tapi belum pernah ditandai (supaya owner bisa membukanya dari sini) — tidak termasuk nama yang sedang dipegang sebuah wadah
  const lain = []; const ada = {};
  const bw = petaBukuWadah();   // putaran 28: karung sisihan / bongkaran wadah ikut tampil, bertanda wadahnya (tidak "dibuka dari gudang")
  siap.kolam.forEach((k) => { if (k.wadah) return; ada[k.merk + '|' + k.lokasi] = 1; if (k.sisaMentahKg <= 0.0001) return; lain.push({ nama: k.merk, lokasi: k.lokasi, karung: k, tumpukan: tumpukanGudang(k.merk, siap), karungWadah: bw[k.merk] ? bw[k.merk].wadah : '' }); });   // yang sudah kosong / dikembalikan ke tumpukan tidak tampil
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
  ambilSemuaBatch().forEach((b) => { if (b.tanggal !== hari || b.lahirBuku) return; (b.merkList || []).forEach((x, i) => out.push({ k: 'b' + b.id + i, jam: b.jam || '', isi: 'Barang masuk ' + x.merk + (x.jumlahKarung ? ' ' + x.jumlahKarung + ' karung' : '') + (b.pemasok ? ' · ' + b.pemasok : ''), n: '+' + skKG(x.totalKg || 0), jenis: 'masuk' })); });
  const petaW = petaBukuWadah();
  ambilProduksiBerlaku().forEach((p) => { if (p.tanggal !== hari) return;
    if (p.bukaKemasan) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Kemasan ' + (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg hasil adukan dibuka jadi karung terbuka — buku karung ' + (p.merkTujuan || '') + ' naik, stok kemasan −1', n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    else if (p.dariTakar && petaW[p.merkTujuan]) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: (p.bukaKarung ? (p.pindahAwalWadah ? 'Pindahan awal stok wadah ' + p.pindahAwalWadah + ': karung terbuka di belakangnya jadi buku sendiri' : 'Karung ' + (p.merkAsal || '') + ' dibuka di belakang wadah ' + p.bukaKarung + ' — tumpukan gudang turun di buku') : p.pindahAwalWadah ? 'Pindahan awal stok wadah ' + p.pindahAwalWadah : p.gantiNamaWadah ? 'Stok wadah ikut ganti nama' : p.sisihWadah ? 'Disisihkan dari wadah ' + p.sisihWadah + ' ke karung wadahnya'
      : p.tuangBalikWadah ? 'Karung sisihan dituang balik ke wadah ' + p.tuangBalikWadah : p.bongkarWadah ? 'Wadah ' + p.bongkarWadah + ' dibongkar ke karung wadahnya' : 'Takar ke stok wadah') + ': ' + (p.sumberList || []).map((x) => x.merk + ' ' + skKG(x.kg || 0)).join(' + ') + ' → ' + (p.merkTujuan || '') + ' (modal ikut)' + (p.perluCocokkan ? ' · buku sumber KURANG ' + skKG(p.selisihKg || 0) + ', DITANDAI untuk dicocokkan' : ''), n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    // tinjauan L7: pengembalian karung ke tumpukan (dan pembetulan buku yang tertinggal) bukan "takar wadah"
    else if (p.kembaliTumpukan !== undefined && p.kembaliTumpukan !== null) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: (p.betulkanTertinggal ? 'Betulkan buku karung tertinggal (sisa pengembalian lama)' : 'Karung dikembalikan ke tumpukan dari belakang wadah ' + p.kembaliTumpukan) + ': '
      + (p.sumberList || []).map((x) => x.merk + ' ' + skKG(x.kg || 0)).join(' + ') + ' → ' + (p.merkTujuan || '') + ' (modal ikut)', n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    else if (p.pisahUkuran) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Buku ' + p.pisahUkuran.induk + ' dipisah per ukuran: ' + (p.pisahUkuran.karung || 0) + ' karung ' + p.pisahUkuran.berat + ' kg → ' + (p.merkTujuan || '') + ' (modal ikut)', n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    else if (p.dariTakar) out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Pindah nama di buku (takar wadah): ' + (p.sumberList || []).map((x) => x.merk + ' ' + skKG(x.kg || 0)).join(' + ') + ' → ' + (p.merkTujuan || ''), n: '↔ ' + skKG(p.kgDipakai || 0), jenis: 'wadah' });
    else out.push({ k: 'p' + p.id, jam: p.jam || '', isi: 'Adukan → ' + (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg', n: '+' + (p.jumlahUnit || 0) + ' unit', jenis: 'masuk' }); });
  // putaran 27: cocokkan TUMPUKAN dan cocokkan WADAH = dua kejadian berbeda (owner 27 Sep); catatan lama satu angka per nama tetap "Cocokkan <nama>"
  ambilPenyesuaianStok().forEach((p) => { if (p.tanggal !== hari) return; const sel = ((p.selisihKg || 0) > 0 ? '+' : '') + skKG(p.selisihKg || 0);
    if (p.bagian === 'tumpukan') out.push({ k: 'o' + p.id, jam: p.jam || '', isi: 'Cocokkan tumpukan gudang ' + (p.merk || '') + ' · tercatat ' + skKG(p.bagianSistemKg || 0) + ' → dihitung ' + skKG(p.bagianFisikKg || 0) + ' · buku ' + skKG(p.kgSistem || 0) + ' → ' + skKG(p.kgFisik || 0), n: sel, jenis: 'opname' });
    else if (p.bagian === 'wadah') out.push({ k: 'o' + p.id, jam: p.jam || '', isi: 'Cocokkan wadah ' + (p.wadah || '') + ' → buku ' + (p.merk || '') + ' ' + skKG(p.kgSistem || 0) + ' → ' + skKG(p.kgFisik || 0) + (p.alasan ? ' · ' + p.alasan : ''), n: sel, jenis: 'wadah' });
    else out.push({ k: 'o' + p.id, jam: p.jam || '', isi: 'Cocokkan ' + (p.merk || '') + ' · sistem ' + skKG(p.kgSistem || 0) + ' → hitungan ' + skKG(p.kgFisik || 0), n: sel, jenis: 'opname' }); });
  ambilPenyesuaianKemasan().forEach((p) => { if (p.tanggal !== hari) return; out.push({ k: 'ok' + p.id, jam: p.jam || '', isi: 'Cocokkan ' + (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg', n: ((p.selisihUnit || 0) > 0 ? '+' : '') + (p.selisihUnit || 0) + ' unit', jenis: 'opname' }); });
  ambilRetur().forEach((r) => { if (r.tanggal !== hari) return; out.push({ k: 'r' + r.id, jam: r.jam || '', isi: 'Barang kembali ' + (r.merkSumber || r.namaProduk || '') + (r.kondisi === 'tidak_utuh' ? ' → Karantina' : ' → stok jual'), n: '+' + skKG(r.totalKg || 0), jenis: r.kondisi === 'tidak_utuh' ? 'opname' : 'masuk' }); });
  ambilWadahLiteran().forEach((w) => { if (w.tanggal !== hari) return;
    if (w.tipe === 'takar' && w.tuangBalik) return;   // putaran 28: tuang balik karung sisihan (baris pindah buku di atas)
    if (w.tipe === 'takar') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Wadah ' + (w.wadah || '') + ' diisi ulang ' + (w.takar || 0) + ' takar dari karung ' + (w.sumber || []).map((x) => x.merk + ((w.sumber || []).length > 1 ? ' ' + x.takar : '')).join(' + ') + ' — karung terbuka turun, wadah naik' + (w.bukuAsal ? ' (buku tetap milik merek karungnya)' : w.stokWadah ? ' (buku pindah ke stok wadah)' : ''), n: '+' + skKG(w.kg || 0), jenis: 'wadah' });
    else if (w.tipe === 'atur' && w.gantiNama) out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Wadah ' + (w.gantiNama.dari || '') + ' berganti nama jadi ' + (w.gantiNama.ke || '') + ' — isi, karung di belakangnya & harga liternya ikut', n: '', jenis: 'wadah' });
    else if ((w.tipe === 'isi' || w.tipe === 'karungIsi') && w.gantiNamaDari) return;   // bagian dari ganti nama wadah (satu baris di atas)
    else if (((w.tipe === 'isi' || w.tipe === 'karungIsi') && (w.pindahAwal || w.bongkar)) || (w.tipe === 'takar' && w.tuangBalik) || (w.tipe === 'karung' && (w.asal === 'wadah' || w.bukuBelakang))) return;   // putaran 28/39: bagian dari aktivasi / bongkar / sisihkan / tuang balik / buka karung berbuku (baris pindah buku di atas)
    else if (w.tipe === 'cek') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Cek wadah ' + (w.wadah || '') + ' tutup toko: ' + ((WB_CEK.find((x) => x[0] === w.hasil) || ['', w.hasil || ''])[1]).toLowerCase() + (w.oleh ? ' · oleh ' + w.oleh : ''), n: '±' + skKG(w.bukuKg || 0), jenis: 'wadah' });   // putaran 39 (e)
    else if (w.tipe === 'isi') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: w.dariCocok ? 'Cocokkan wadah ' + (w.wadah || '') + ': isinya dihitung' + (w.komposisi && Object.keys(w.komposisi).length ? ' (' + Object.keys(w.komposisi).map((m) => m + ' ' + skKG(w.komposisi[m])).join(' + ') + ')' : '') : 'Wadah ' + (w.wadah || '') + ' disamakan dengan kenyataan', n: '±' + skKG(w.isiKg || 0), jenis: 'wadah' });
    else if (w.tipe === 'karung') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: 'Karung ' + (w.merk || '') + (w.asal === 'masuk' ? ' yang baru datang dari pemasok' : w.asal === 'adukan' ? ' (kemasan hasil adukan)' : ' diambil dari tumpukan gudang') + ', dibuka ' + (w.wadah ? 'di belakang wadah ' + w.wadah : w.lepas ? 'sebagai bahan campuran' : 'di belakang wadah') + (w.otomatis ? ' (otomatis — karung sebelumnya habis)' : ''), n: 'gudang −' + skKG(w.kg || 0), jenis: 'wadah' });
    else if (w.tipe === 'karungIsi') out.push({ k: 'w' + w.id, jam: w.jam || '', isi: w.dikembalikan ? 'Karung terbuka ' + (w.merk || '') + ' dikembalikan ke tumpukan gudang' : w.selesai ? 'Karung ' + wbMerkAsal(w.merk || '') + (w.wadah ? ' di belakang wadah ' + w.wadah : '') + ' habis — dihapus dari deretan' : 'Karung terbuka ' + (w.merk || '') + ' disamakan dengan kenyataan', n: w.dikembalikan ? '+' + skKG(w.sisaSebelumKg || 0) : w.selesai ? 'habis' : '±' + skKG(w.isiKg || 0), jenis: 'wadah' }); });
  // putaran 27 (Bagian 5): literan WADAH dikelompokkan per wadah (satu takaran = satu baris) dan menyebut buku merek asal yang dipotong
  const jual = {}; const takaran = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== hari) return; const nm = p.jenis === 'kemasan' ? (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg' : p.dariWadah ? 'literan wadah ' + p.dariWadah : (p.merkSumber || p.namaProduk || ''); const k = (p.jam || '').slice(0, 2) + '|' + nm;
    const o = jual[k] || (jual[k] = { jam: (p.jam || '').slice(0, 2) + '.00', nm, kg: 0, unit: 0, n: 0, buku: [] }); if (!p.takaranId || !takaran[p.takaranId]) o.n += 1; if (p.takaranId) takaran[p.takaranId] = 1;
    if (p.dariWadah && p.merkSumber && o.buku.indexOf(p.merkSumber) < 0) o.buku.push(p.merkSumber);
    if (p.jenis === 'kemasan') o.unit += p.jumlahUnit || 0; else o.kg += p.totalKg || 0; if ((p.jam || '') > o.jam) o.jamAkhir = p.jam; });
  Object.keys(jual).forEach((k) => { const o = jual[k]; out.push({ k: 'j' + k, jam: o.jamAkhir || o.jam, isi: 'Terjual ' + o.nm + (o.buku.length ? ' (buku ' + o.buku.slice().sort().join(' + ') + ')' : '') + ' · ' + o.n + ' baris', n: '−' + (o.unit ? o.unit + ' unit' : skKG(o.kg)), jenis: 'keluar' }); });
  out.sort((a, b) => (b.jam || '').localeCompare(a.jam || ''));
  return { hari, baris: out.slice(0, 60), banyak: out.length };
}

/** Karantina: barang kembali yang belum diputuskan (baca saja di putaran ini). */
export function susunKarantina() {
  const baris = ambilKarantina().filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan')
    .map((k) => ({ k: String(k.id), nama: k.merkSumber || ((k.namaProduk || '') + ' ' + (k.ukuranKemasan || '') + ' kg'), kg: k.totalKg || 0, tanggal: k.tanggal || '', catatan: k.catatan || '' }));
  return { baris, totalKg: baris.reduce((a, x) => a + x.kg, 0) };
}

// ---------- UMUR & PUTARAN (paket brief 9 Okt, butir 2) — tab sendiri; papan S9 di atas tidak disentuh ----------
// BERAT (kg), bukan rupiah: HPP per nota & nilai stok tetap rata-rata mesin beku (keputusan uang FIFO dikerjakan terpisah, owner).
// Sisa kg tiap buku = SUMBER YANG SAMA dengan tab Gudang (daftarBarang → ingatStokKarung) — umur & putaran tidak menghitung sisa sendiri.
//  · KARUNG per merek (owner: "pakai metode FIFO bukan average — barang yang dijual duluan itu barang yang lama dulu"): sisa = lapisan kedatangan TERBARU.
//    Sisa diisikan ke kedatangan dari yang terbaru mundur; umur stok = umur lapisan tertua yang masih tersisa (+ rata-rata ditimbang kg). Sisa yang melebihi
//    semua kedatangan tercatat (stok awal / saldo pembuka / pindah buku / adukan jadi karung / retur / selisih cocokkan) = TANPA TANGGAL MASUK: belum bisa
//    dihitung, tampil terpisah — bukan umur 0.
//  · Karung terbuka di belakang wadah & kemasan adukan yang dibuka (buku khusus berisi karung): FIFO juga, lapisannya = tiap karung yang masuk ke buku itu
//    (umur SEJAK DIBUKA, bukan sejak datang dari pemasok — disebut di layar).
//  · WADAH kotak literan & karung sisihannya (owner 9 Okt: "terkecuali wadah kotak literan yang dicampur memakai average"): umur RATA-RATA ditimbang kg sejak
//    dituang — yang keluar mengambil merata (rata-rata tanggal tidak bergeser), tuangan baru menimbang tanggalnya. Jejaknya membaca buku mesin per tanggal
//    (ingatStokKarung(tanggal), sumber yang sama); kenaikan tanpa catatan tuang (pindahan awal, ganti nama, cocokkan plus) = bagian tanpa tanggal, ikut keluar merata.
//  · Hari stok = sisa ÷ laju keluar 14 hari yang SAMA dengan papan Gudang (tak ada gerak → "belum ada laju", bukan 0). Perputaran periode = kg keluar (saringan
//    laju yang sama: terjual + diaduk + dipindah ke wadah — lajuHarian) ÷ rata-rata sisa akhir hari periode itu; rata-rata tinggal di rak = periode ÷ perputaran.
//  · Lambat laku = umur stok > ambang ATAU hari stok > ambang (sisa tanpa gerak keluar 14 hari = lebih dari ambang apa pun). Ambang & periode = aturanToko/stokUmur.
export const UM_ATUR_BAWAAN = { ambangUmurHari: 30, ambangHariStok: 30, periodeHari: 30 };   // angka bawaan (perkiraan) — bisa diubah di Atur
export const UM_BATAS = { ambangUmurHari: [1, 365], ambangHariStok: [1, 365], periodeHari: [7, 120] };
export const UM_JEJAK_HARI = 60;   // jejak rata-rata wadah paling jauh 60 hari (isi wadah berputar dalam hitungan hari); isi yang sudah ada sebelumnya = tanpa tanggal
export const TAB_UMUR = [['lambat', 'Apa yang lambat laku?'], ['umur', 'Stok mana yang paling lama?'], ['putaran', 'Berapa cepat stok berputar?'], ['tanpa', 'Mana yang belum bertanggal?']];
const UM_NAMA_ATUR = { ambangUmurHari: 'Ambang umur stok', ambangHariStok: 'Ambang hari stok', periodeHari: 'Periode perputaran' };
const umSen = (n) => Math.round((Number(n) || 0) * 100);   // kg → seperseratus kg (bilangan bulat: bagian-bagian menutup persis)
const umHariGeser = (iso, n) => hariIniIso(new Date(new Date(iso + 'T12:00:00').getTime() + n * 86400000));
const umTgl = (iso) => tanggalPendek(iso).replace(/ \d{4}$/, '');
const umKali = (n) => String(Math.round(n * 10) / 10).replace('.', ',');

/** Ambang & periode owner (aturanToko/stokUmur); belum diatur / di luar batas → angka bawaan. */
export function umAtur() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'stokUmur') || null; const o = {};
  Object.keys(UM_ATUR_BAWAAN).forEach((k) => { const n = a ? Number(a[k]) : NaN; const b = UM_BATAS[k]; o[k] = isFinite(n) && n >= b[0] && n <= b[1] ? Math.round(n) : UM_ATUR_BAWAAN[k]; });
  return Object.assign(o, { dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' });
}
/** Simpan ambang & periode. Kosong = angka sekarang; pecahan / di luar batas DITOLAK dengan kalimat (tidak dibulatkan diam-diam). */
export function susunAturUmur(isi, w) {
  const kini = umAtur(); const o = {}; let tolak = '';
  Object.keys(UM_ATUR_BAWAAN).forEach((k) => { if (tolak) return; const t = String(isi && isi[k] !== undefined && isi[k] !== null ? isi[k] : '').trim().replace(',', '.'); const b = UM_BATAS[k];
    if (!t) { o[k] = kini[k]; return; } const n = Number(t);
    if (!isFinite(n) || Math.round(n) !== n || n < b[0] || n > b[1]) tolak = UM_NAMA_ATUR[k] + ' harus bilangan bulat ' + b[0] + '–' + b[1] + ' hari'; else o[k] = n; });
  if (tolak) return { tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({ id: 'stokUmur', tanggal: w.tanggal, jam: w.jam }, o) }],
    patch: { aturUm: null, kabar: 'Ambang disimpan — lambat laku: umur stok > ' + o.ambangUmurHari + ' hari atau hari stok > ' + o.ambangHariStok + ' hari · perputaran ' + o.periodeHari + ' hari', kabarAwas: false } };
}

/** Pindah buku MASUK ke satu buku khusus (produksi berlaku jadiKarungUtuh → merkTujuan; kg = ukuran × unit, rumus mesin). Pindahan awal / ganti nama = isinya
 *  sudah ada sebelum buku ini → tanpa tanggal. */
function umPindahMasuk(kunci) {
  return ambilProduksiBerlaku().filter((p) => p.jadiKarungUtuh && p.merkTujuan === kunci).map((p) => ({ tanggal: p.tanggal || '', jam: p.jam || '', id: p.id, kg: (Number(p.ukuranKemasan) || 0) * (Number(p.jumlahUnit) || 0),
    asal: p.bukaKarung || p.bukaKemasan ? 'dibuka' : p.sisihWadah || p.bongkarWadah ? 'disisihkan' : p.kembaliTumpukan !== undefined && p.kembaliTumpukan !== null ? 'dikembalikan' : 'dituang',
    tanpaTanggal: !p.tanggal || !!p.pindahAwalWadah || !!p.gantiNamaWadah })).filter((x) => umSen(x.kg) > 0);
}
/** Lapisan FIFO satu buku: merek = kedatangan sungguhan (riwayatModal Stok › HPP, bukan fondasi); karung belakang / adukan dibuka = tiap karung yang masuk. */
function umLapisan(kunci, jenis) {
  if (!jenis) return riwayatModal(kunci).filter((r) => r.jenis === 'kedatangan' && !r.fondasi).map((r) => ({ tanggal: r.tanggal, jam: r.jam, id: r.batchId, kg: r.totalKg, asal: 'kedatangan', pemasok: r.pemasok }));
  return umPindahMasuk(kunci).filter((x) => !x.tanpaTanggal);
}

/**
 * FIFO murni (diekspor untuk uji & dasbor): sisaKg diisikan ke lapisan dari yang TERBARU mundur (tanggal, jam, id). Hasil MENUTUP persis (seperseratus kg):
 * Σ kg lapisan tersisa + tanpaTanggalKg = sisaKg. umurTertua = umur lapisan tertua yang masih tersisa; umurRata = rata-rata ditimbang kg bagian bertanggal.
 */
export function umFifo(lapisan, sisaKg, hari) {
  const urut = (lapisan || []).filter((x) => x && x.tanggal && umSen(x.kg) > 0).slice()
    .sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || String(b.jam || '').localeCompare(String(a.jam || '')) || String(b.id).localeCompare(String(a.id), undefined, { numeric: true }));
  const total = umSen(sisaKg); let sisa = total; const tersisa = [];
  urut.forEach((x) => { if (sisa <= 0) return; const m = umSen(x.kg); const ambil = sisa < m ? sisa : m; sisa -= ambil;
    tersisa.push(Object.assign({}, x, { kgMasuk: m / 100, kg: ambil / 100, utuh: ambil === m, umur: skSelisihHari(x.tanggal, hari) })); });
  const bertanggal = tersisa.reduce((a, x) => a + umSen(x.kg), 0); const tua = tersisa.length ? tersisa[tersisa.length - 1] : null;
  return { cara: 'fifo', lapisan: tersisa, bertanggalKg: bertanggal / 100, tanpaTanggalKg: total > 0 ? (total - bertanggal) / 100 : 0, umurTertua: tua ? tua.umur : null, tanggalTertua: tua ? tua.tanggal : '',
    umurRata: bertanggal > 0 ? tersisa.reduce((a, x) => a + umSen(x.kg) * x.umur, 0) / bertanggal : null };
}

/**
 * Isi wadah CAMPURAN — rata-rata (owner 9 Okt), diekspor untuk uji & dasbor. masuk = pindah buku masuk ({ tanggal, kg, tanpaTanggal }); sisaKini = sisa buku sekarang
 * (sumber Gudang); sisaPada(iso) = sisa buku itu di akhir tanggal iso (mesin yang sama). Mulai sehari sebelum tuangan pertama di jejak (isi yang sudah ada =
 * tanpa tanggal), lalu TIAP HARI: tuangan hari itu ditimbang umurnya → akhir hari dibaca dari buku: turun = keluar merata, naik tanpa catatan tuang = tanpa
 * tanggal, 0 = wadah kosong (mulai lagi). Hari ini memakai sisaKini. Hasil menutup: bertanggal + tanpa tanggal = sisaKini.
 */
export function umRataCampuran(masuk, sisaKini, hari, sisaPada) {
  const dari = umHariGeser(hari, -(UM_JEJAK_HARI - 1)); const perHari = {};
  (masuk || []).forEach((x) => { const t = x.tanggal; if (!t || t < dari || t > hari) return; const o = perHari[t] || (perHari[t] = { d: 0, u: 0 }); if (x.tanpaTanggal) o.u += umSen(x.kg); else o.d += umSen(x.kg); });
  let D = 0, U = 0, A = 0;   // D seperseratus kg bertanggal dengan umur rata-rata A (hari, dihitung pada `hari`); U seperseratus kg tanpa tanggal
  const geser = (Sk) => { const tot = D + U; if (Sk <= 0) { D = 0; U = 0; A = 0; return; } if (Sk >= tot) { U += Sk - tot; return; } const f = Sk / tot; D *= f; U *= f; };
  const tuang = (d) => { const q = perHari[d]; if (!q) return; if (q.d > 0) { const um = skSelisihHari(d, hari); A = (D * A + q.d * um) / (D + q.d); D += q.d; } U += q.u; };
  const hariTuang = Object.keys(perHari).sort();
  if (hariTuang.length) { geser(umSen(sisaPada(umHariGeser(hariTuang[0], -1))));
    for (let d = hariTuang[0]; d < hari; d = umHariGeser(d, 1)) { tuang(d); geser(umSen(sisaPada(d))); } }
  const total = umSen(sisaKini); tuang(hari); geser(total);
  const Dk = total > 0 ? Math.round(D) : 0; const dTuang = hariTuang.filter((d) => perHari[d].d > 0);
  return { cara: 'rata', lapisan: [], bertanggalKg: Dk / 100, tanpaTanggalKg: total > 0 ? (total - Dk) / 100 : 0, umurRata: Dk > 0 ? A : null, umurTertua: null, tanggalTertua: '',
    jejakDari: dari, hariTuang: dTuang.length, tuangTerakhir: dTuang.length ? dTuang[dTuang.length - 1] : '' };
}

/** Periode perputaran: `periodeHari` hari sampai hari ini — dipendekkan bila catatan toko baru mulai sesudahnya atau tahunnya sudah diarsip tutup buku. */
function umPeriode(hari, P) {
  let dari = umHariGeser(hari, -(P - 1)); let catat = ''; const pertama = catatanPertama();
  if (pertama && pertama > dari) { dari = pertama; catat = 'catatan toko baru mulai ' + umTgl(pertama); }
  while (dari <= hari && tahunDiarsip(dari)) { dari = String(Number(dari.slice(0, 4)) + 1) + '-01-01'; catat = 'tahun ' + (Number(dari.slice(0, 4)) - 1) + ' sudah diarsip tutup buku'; }
  const n = dari <= hari ? skSelisihHari(dari, hari) + 1 : 0;
  return { dari, sampai: hari, n, P, catat };
}

/**
 * FUNGSI SUMBER (dasbor kelak): tiap buku karung di Gudang — umur stok (FIFO / rata-rata wadah), hari stok, perputaran periode, lambat laku. Diingat per versi
 * data + hari. Baris: sisa ≠ 0 atau ada gerak keluar di periode. Hasilnya JANGAN diubah di tempat (dibagi bersama).
 */
export function umBarang(kini) { const hari = hariIniIso(kini); return ingatPerVersi('umBarang|' + hari, () => umBarangHitung(hari)); }
function umBarangHitung(hari) {
  const A = umAtur(); const bw = petaBukuWadah(); const P = umPeriode(hari, A.periodeHari); const SB = {};
  const bukuPada = (iso) => SB[iso] || (SB[iso] = ingatStokKarung(iso));
  const keluar = {}; const terjual = {};
  if (P.n > 0) {
    const L = lajuHarian(P.dari, hari); Object.keys(L).forEach((t) => Object.keys(L[t].kg).forEach((k) => { keluar[k] = (keluar[k] || 0) + L[t].kg[k]; }));
    // bagian TERJUAL dari kg keluar (saringan penjualan yang sama dengan lajuHarian) — sisanya diaduk / dipindah ke wadah
    ambilPenjualan().forEach((p) => { const t = p.tanggal || ''; if (t < P.dari || t > hari) return; if ((p.jenis === 'karung' || p.jenis === 'repacking' || p.jenis === 'literan') && p.merkSumber) terjual[p.merkSumber] = (terjual[p.merkSumber] || 0) + (p.totalKg || 0); });
  }
  const hariP = []; for (let i = 0; i < P.n; i++) hariP.push(umHariGeser(P.dari, i));
  return daftarBarang().filter((b) => b.jenis === 'karung').map((b) => {
    const k = b.kunci; const jb = bw[k] ? bw[k].jenis : ''; const cara = jb === 'wadah' || jb === 'karung' ? 'rata' : 'fifo';
    const kelompok = !jb ? 'merek' : cara === 'rata' ? 'wadah' : 'belakang';
    const ada = umSen(b.sisa) > 0; const minus = umSen(b.sisa) < 0;
    const U = !ada ? null : cara === 'rata' ? umRataCampuran(umPindahMasuk(k), b.sisa, hari, (iso) => { const x = bukuPada(iso)[k]; return x ? x.sisaKg : 0; }) : umFifo(umLapisan(k, jb), b.sisa, hari);
    const umurAcuan = !U ? null : cara === 'rata' ? U.umurRata : U.umurTertua;
    const hariStok = ada && b.laju > 0 ? b.sisa / b.laju : null;
    const keluarKg = keluar[k] || 0; const terjualKg = terjual[k] || 0;
    const rataSisa = P.n > 0 ? hariP.reduce((a, t) => { const x = bukuPada(t)[k]; return a + (x ? x.sisaKg : 0); }, 0) / P.n : null;
    const putaran = keluarKg > 0 && rataSisa !== null && rataSisa > 0 ? keluarKg / rataSisa : null;
    const alasan = [];
    if (umurAcuan !== null && umurAcuan > A.ambangUmurHari) alasan.push('umur');
    if (ada && !(b.laju > 0)) alasan.push('diam'); else if (hariStok !== null && hariStok > A.ambangHariStok) alasan.push('hari');
    return { kunci: k, nama: b.nama, kelompok, cara, wadah: bw[k] ? bw[k].wadah : '', sisa: b.sisa, ada, minus, umur: U, umurAcuan, laju: b.laju, hariStok, keluarKg, terjualKg, rataSisa, putaran,
      tinggal: putaran ? P.n / putaran : null, lambat: alasan.length > 0, alasan };
  }).filter((r) => r.ada || r.minus || r.keluarKg > 0);
}

/** Ringkas untuk dasbor kelak: lambat laku, 5 merek tertua, kg bertanggal / tanpa tanggal / minus (menutup ke Σ sisa positif), putaran tumpukan merek. */
export function umRingkas(kini) {
  const R = umBarang(kini); const berisi = R.filter((r) => r.ada); const A = umAtur();
  const bt = berisi.reduce((a, r) => a + umSen(r.umur.bertanggalKg), 0); const tt = berisi.reduce((a, r) => a + umSen(r.umur.tanpaTanggalKg), 0);
  const merek = R.filter((r) => r.kelompok === 'merek');
  const kel = merek.reduce((a, r) => a + r.keluarKg, 0); const rs = merek.reduce((a, r) => a + (r.rataSisa > 0 ? r.rataSisa : 0), 0);
  return { atur: A, periode: umPeriode(hariIniIso(kini), A.periodeHari), lambat: R.filter((r) => r.lambat),
    tertua: merek.filter((r) => r.umurAcuan !== null).sort((a, b) => b.umurAcuan - a.umurAcuan || a.nama.localeCompare(b.nama)).slice(0, 5),
    sisaKg: berisi.reduce((a, r) => a + umSen(r.sisa), 0) / 100, bertanggalKg: bt / 100, tanpaTanggalKg: tt / 100, minus: R.filter((r) => r.minus),
    putaranMerek: kel > 0 && rs > 0 ? kel / rs : null, keluarMerek: kel, rataSisaMerek: rs };
}

const UM_LABEL_KELOMPOK = { merek: 'Karung & tumpukan per merek · FIFO — yang tersisa = kedatangan terbaru', belakang: 'Karung terbuka di belakang wadah · FIFO — umur sejak karung dibuka (bukan sejak datang)', wadah: 'Wadah literan · wadah campuran: umur rata-rata sejak dituang' };
const umTeksUmur = (r) => (r.minus ? 'buku minus' : !r.ada ? 'kosong' : r.umurAcuan === null ? 'tanpa tanggal' : r.cara === 'rata' ? 'rata ' + umKali(r.umurAcuan) + ' hari' : r.umurAcuan + ' hari');
const umTeksHariStok = (r) => (!r.ada ? '' : r.hariStok === null ? 'belum ada laju' : 'hari stok ' + umKali(r.hariStok));
const umTeksPutaran = (r, P) => (r.putaran !== null ? 'putaran ' + P.n + ' hari ' + umKali(r.putaran) + '× · tinggal ±' + umKali(r.tinggal) + ' hari' : r.keluarKg > 0 ? 'putaran belum bisa dihitung (sisa rata-rata tidak positif)' : 'putaran: belum ada laju');
const umTeksAlasan = (r, A) => r.alasan.map((x) => (x === 'umur' ? (r.cara === 'rata' ? 'umur rata-rata ' + umKali(r.umurAcuan) : 'umur stok ' + r.umurAcuan) + ' hari > ' + A.ambangUmurHari
  : x === 'hari' ? 'hari stok ' + umKali(r.hariStok) + ' > ' + A.ambangHariStok : 'tak ada gerak keluar ' + JENDELA_LAJU_HARI + ' hari (laju belum terukur)')).join(' · ');
/** Kalimat lapisan: "tersisa dari kedatangan 30 Sep · 120 kg" (lapisan tertua yang masih tersisa) + berapa lapisan lebih baru + tanpa tanggal. */
function umTeksLapisan(r) {
  const U = r.umur; if (!U) return '';
  if (r.cara === 'rata') return 'wadah campuran: umur rata-rata' + (U.umurRata === null ? ' belum bisa dihitung' : ' ' + umKali(U.umurRata) + ' hari sejak dituang') + (U.tanpaTanggalKg > 0 ? ' · ' + KG(U.tanpaTanggalKg) + ' tanpa tanggal' : '');
  const tua = U.lapisan[U.lapisan.length - 1]; const kata = r.kelompok === 'belakang' ? 'dibuka' : 'kedatangan';
  return (tua ? 'tersisa dari ' + kata + ' ' + umTgl(tua.tanggal) + ' · ' + (tua.utuh ? KG(tua.kg) : KG(tua.kg) + ' dari ' + KG(tua.kgMasuk)) + (U.lapisan.length > 1 ? ' + ' + (U.lapisan.length - 1) + ' ' + kata + ' lebih baru' : '') : '')
    + (U.tanpaTanggalKg > 0 ? (tua ? ' · ' : '') + KG(U.tanpaTanggalKg) + ' tanpa tanggal masuk' : '');
}
/** Asal bagian tanpa tanggal (merek: riwayat modal — stok awal / saldo pembuka / pindah buku) — disebut, tidak ditebak mana yang tersisa. */
function umAsalTanpa(r) {
  if (r.kelompok !== 'merek') return r.cara === 'rata' ? 'isi yang sudah di wadah sebelum tuangan tercatat pertama (jejak ' + UM_JEJAK_HARI + ' hari), pindahan awal / ganti nama wadah, atau kenaikan tanpa catatan tuang (cocokkan plus)' : 'pindahan awal saat buku wadah lahir, atau kenaikan tanpa catatan buka (cocokkan plus)';
  const o = {}; riwayatModal(r.kunci).forEach((x) => { if (x.jenis === 'kedatangan' && !x.fondasi) return; const nm = x.jenis === 'pindah' ? x.sumber : /saldo pembuka/.test(x.sumber) ? 'saldo pembuka' : 'stok awal'; o[nm] = (o[nm] || 0) + (x.totalKg || 0); });
  const t = Object.keys(o).sort().map((nm) => nm + ' ' + KG(o[nm]));
  return (t.length ? t.join(', ') + ', ' : '') + 'atau retur utuh / selisih cocokkan';
}
/** Baris rinci satu buku (detail merek di tab Umur & putaran). */
function umRinci(r, P) {
  const out = []; const U = r.umur; const kata = r.kelompok === 'belakang' ? 'dibuka' : 'kedatangan';
  if (r.minus) out.push({ teks: 'Buku ' + r.nama + ' MINUS ' + KG(-r.sisa) + ' — tidak berumur; cocokkan stok dulu.', awas: true });
  else if (!r.ada) out.push({ teks: 'Sisa 0 kg — tidak ada stok yang berumur.', awas: false });
  if (U && r.cara === 'fifo') {
    U.lapisan.forEach((x) => out.push({ teks: kata + ' ' + umTgl(x.tanggal) + (x.pemasok ? ' (' + x.pemasok + ')' : '') + ' · ' + (x.utuh ? KG(x.kg) + ' utuh' : KG(x.kg) + ' dari ' + KG(x.kgMasuk)) + ' · umur ' + x.umur + ' hari', awas: false }));
    if (U.tanpaTanggalKg > 0) out.push({ teks: KG(U.tanpaTanggalKg) + ' TANPA TANGGAL MASUK — sisa melebihi semua ' + (r.kelompok === 'belakang' ? 'karung yang tercatat dibuka' : 'kedatangan tercatat') + '; asalnya: ' + umAsalTanpa(r) + '. Belum bisa dihitung umurnya.', awas: true });
    out.push({ teks: U.umurTertua === null ? 'Umur stok belum bisa dihitung — tidak ada lapisan bertanggal yang tersisa.' : 'Umur stok = lapisan tertua yang masih tersisa: ' + U.umurTertua + ' hari (' + kata + ' ' + umTgl(U.tanggalTertua) + ') · rata-rata ditimbang kg ' + umKali(U.umurRata) + ' hari' + (U.tanpaTanggalKg > 0 ? ' (bagian bertanggal ' + KG(U.bertanggalKg) + ')' : ''), awas: false });
  }
  if (U && r.cara === 'rata') {
    out.push({ teks: 'Wadah campuran: umur rata-rata ditimbang kg sejak dituang ' + (U.umurRata === null ? 'belum bisa dihitung' : umKali(U.umurRata) + ' hari') + ' · bertanggal ' + KG(U.bertanggalKg) + (U.tanpaTanggalKg > 0 ? ' + tanpa tanggal ' + KG(U.tanpaTanggalKg) : '') + ' = ' + KG(r.sisa), awas: false });
    if (U.tanpaTanggalKg > 0) out.push({ teks: 'Tanpa tanggal: ' + umAsalTanpa(r) + '.', awas: false });
    out.push({ teks: (U.hariTuang ? U.hariTuang + ' hari bertuang dalam ' + UM_JEJAK_HARI + ' hari terakhir, tuang terakhir ' + umTgl(U.tuangTerakhir) : 'Tidak ada tuangan tercatat dalam ' + UM_JEJAK_HARI + ' hari terakhir') + '. Yang keluar mengambil merata dari isi (bukan FIFO).', awas: false });
  }
  if (r.ada) out.push({ teks: r.hariStok === null ? 'Hari stok: belum ada laju — tak ada gerak keluar ' + JENDELA_LAJU_HARI + ' hari (bukan 0).' : 'Hari stok: sisa ' + KG(r.sisa) + ' ÷ laju ' + JENDELA_LAJU_HARI + ' hari ' + KG(r.laju) + '/hari = ' + umKali(r.hariStok) + ' hari', awas: false });
  out.push({ teks: P.n <= 0 ? 'Perputaran: periode kosong.' : 'Periode ' + P.n + ' hari (' + umTgl(P.dari) + ' – ' + umTgl(P.sampai) + ')' + (P.catat ? ' · ' + P.catat : '') + ': keluar ' + KG(r.keluarKg) + ' (terjual ' + KG(r.terjualKg) + ' · diaduk / dipindah ' + KG(r.keluarKg - r.terjualKg) + ')'
    + (r.putaran !== null ? ' ÷ rata-rata sisa akhir hari ' + KG(r.rataSisa) + ' = putaran ' + umKali(r.putaran) + '× · rata-rata tinggal di rak ' + umKali(r.tinggal) + ' hari' : r.keluarKg > 0 ? ' · rata-rata sisa ' + KG(r.rataSisa || 0) + ' tidak positif — putaran belum bisa dihitung' : ' — belum ada laju, putaran tidak dihitung (bukan 0)'), awas: false });
  return out;
}

/** Tab Umur & putaran: kartu pertanyaan + daftar jawaban yang dibuka + rincian buku yang diketuk (detail merek). */
export function umPapan(kini, tanya, pilih) {
  const R = umBarang(kini); const A = umAtur(); const P = umPeriode(hariIniIso(kini), A.periodeHari); const G = umRingkas(kini);
  const aktif = TAB_UMUR.some((t) => t[0] === tanya) ? tanya : 'lambat';
  const baris = (r, n, nKet, ket, awas, isi) => ({ kunci: r.kunci, nama: r.nama, n, nKet, ket, awas: !!awas, isi: Math.max(0.02, Math.min(1, isi || 0)), rinci: r.kunci === pilih ? umRinci(r, P) : null });
  const isiUmur = (r) => (r.umurAcuan === null ? 0 : r.umurAcuan / (A.ambangUmurHari * 2));
  const tuaDulu = (a, b) => (b.umurAcuan === null ? -1 : b.umurAcuan) - (a.umurAcuan === null ? -1 : a.umurAcuan) || a.nama.localeCompare(b.nama);
  const berisi = R.filter((r) => r.ada); let kelompok = [];
  const ketUmum = (r) => ['sisa ' + KG(r.sisa), umTeksLapisan(r), aktif === 'lambat' && r.alasan.indexOf('hari') >= 0 ? '' : umTeksHariStok(r), umTeksPutaran(r, P)].filter(Boolean).join(' · ');
  if (aktif === 'lambat') {
    kelompok = [{ id: 'lambat', label: '', baris: G.lambat.slice().sort(tuaDulu).map((r) => baris(r, umTeksUmur(r), r.alasan.indexOf('diam') >= 0 ? 'tak bergerak' : 'lambat laku', umTeksAlasan(r, A) + ' · ' + ketUmum(r), true,
      r.hariStok === null ? 1 : Math.max(isiUmur(r), r.hariStok / (A.ambangHariStok * 2)))) }];
  } else if (aktif === 'umur' || aktif === 'tanpa') {
    const pakai = aktif === 'tanpa' ? berisi.filter((r) => r.umur.tanpaTanggalKg > 0) : R.filter((r) => r.ada || r.minus);
    kelompok = ['merek', 'belakang', 'wadah'].map((g) => ({ id: g, label: UM_LABEL_KELOMPOK[g], baris: pakai.filter((r) => r.kelompok === g).sort(tuaDulu)
      .map((r) => baris(r, aktif === 'tanpa' ? KG(r.umur.tanpaTanggalKg) : umTeksUmur(r), aktif === 'tanpa' ? 'dari ' + KG(r.sisa) : r.minus ? 'cocokkan' : r.cara === 'rata' ? 'wadah campuran' : r.umurAcuan === null ? 'belum bisa dihitung' : r.umur.tanpaTanggalKg > 0 ? 'umur stok + tanpa tanggal' : 'umur stok',
        ketUmum(r), r.minus || r.lambat, aktif === 'tanpa' ? r.umur.tanpaTanggalKg / r.sisa : isiUmur(r))) })).filter((g) => g.baris.length);
  } else {
    const lambatDulu = (a, b) => (b.tinggal === null ? (b.ada ? 1e9 : -1) : b.tinggal) - (a.tinggal === null ? (a.ada ? 1e9 : -1) : a.tinggal) || a.nama.localeCompare(b.nama);
    kelompok = ['merek', 'belakang', 'wadah'].map((g) => ({ id: g, label: UM_LABEL_KELOMPOK[g].split(' · ')[0], baris: R.filter((r) => r.kelompok === g).sort(lambatDulu)
      // tinjauan no. 14 (9 Okt): putaran null karena sisa rata-rata akhir hari ≤ 0 padahal barangnya KELUAR (masuk & keluar di hari yang sama, buku sempat minus)
      // = "belum bisa dihitung", bukan "belum ada laju" — "belum ada laju" hanya bila tidak ada yang keluar di periode (sama dengan umTeksPutaran & umRinci)
      .map((r) => baris(r, r.putaran !== null ? umKali(r.putaran) + '×' : r.keluarKg > 0 ? 'belum bisa dihitung' : 'belum ada laju', r.putaran !== null ? 'tinggal ±' + umKali(r.tinggal) + ' hari' : r.keluarKg > 0 ? 'sisa rata-rata tidak positif' : 'tak ada gerak', ketUmum(r), r.putaran === null && r.ada, r.tinggal === null ? 1 : r.tinggal / (P.n * 2))) })).filter((g) => g.baris.length);
  }
  const tua = G.tertua[0] || null; const nTanpa = berisi.filter((r) => r.umur.tanpaTanggalKg > 0).length;
  const kartu = [
    { id: 'lambat', q: TAB_UMUR[0][1], a: G.lambat.length ? G.lambat.length + ' barang' : 'tidak ada', awas: G.lambat.length > 0 },
    { id: 'umur', q: TAB_UMUR[1][1], a: tua ? tua.umurAcuan + ' hari' : 'belum bisa dihitung', awas: !!tua && tua.umurAcuan > A.ambangUmurHari },
    { id: 'putaran', q: TAB_UMUR[2][1], a: G.putaranMerek !== null ? umKali(G.putaranMerek) + '× / ' + P.n + ' hari' : G.keluarMerek > 0 ? 'belum bisa dihitung' : 'belum ada laju', awas: false },
    { id: 'tanpa', q: TAB_UMUR[3][1], a: G.tanpaTanggalKg > 0 ? KG(G.tanpaTanggalKg) : 'tidak ada', awas: G.tanpaTanggalKg > 0 },
  ];
  const tutup = 'Sisa di buku yang positif ' + KG(G.sisaKg) + ' = bertanggal ' + KG(G.bertanggalKg) + ' + tanpa tanggal masuk ' + KG(G.tanpaTanggalKg)
    + (G.minus.length ? ' · buku MINUS (tidak berumur, cocokkan): ' + G.minus.map((r) => r.nama + ' ' + KG(r.sisa)).join(', ') : '');
  const rumus = {
    lambat: 'lambat laku = umur stok > ' + A.ambangUmurHari + ' hari ATAU hari stok (sisa ÷ laju ' + JENDELA_LAJU_HARI + ' hari) > ' + A.ambangHariStok + ' hari; sisa tanpa gerak keluar ' + JENDELA_LAJU_HARI + ' hari ikut (laju belum terukur, bukan 0)',
    umur: 'FIFO (owner): barang lama keluar duluan → sisa = kedatangan TERBARU; umur stok = lapisan tertua yang masih tersisa. Wadah literan campuran = umur rata-rata (owner 9 Okt). Sisa melebihi kedatangan tercatat = tanpa tanggal masuk, bukan umur 0.',
    putaran: 'putaran ' + P.n + ' hari = kg keluar (terjual + diaduk + dipindah ke wadah, saringan laju yang sama) ÷ rata-rata sisa akhir hari; rata-rata tinggal di rak = ' + P.n + ' hari ÷ putaran. Kartu = tumpukan merek saja (pindah antarbuku tidak dihitung dua kali).' + (P.catat ? ' Periode dipendekkan: ' + P.catat + '.' : ''),
    tanpa: 'tanpa tanggal masuk = sisa yang melebihi semua kedatangan tercatat (stok awal, saldo pembuka, pindah buku, adukan jadi karung, retur, selisih cocokkan) — umurnya belum bisa dihitung · ' + nTanpa + ' buku',
  }[aktif];
  const kosong = { lambat: 'Tidak ada yang lambat laku dengan ambang sekarang.', umur: 'Belum ada beras karung bersisa di buku.', putaran: 'Belum ada gerak keluar di periode ini.', tanpa: 'Semua sisa bertanggal masuk.' }[aktif];
  return { atur: A, periode: P, kartu, aktif, judul: TAB_UMUR.find((t) => t[0] === aktif)[1], kelompok, rumus, kosong, tutup, banyak: R.length };
}
/** Baris ringkas untuk detail merek di lembar lain (Stok › HPP / modal): '' bila buku itu tidak punya sisa atau gerak. */
export function umKalimat(kunci, kini) {
  const r = umBarang(kini).find((x) => x.kunci === kunci); if (!r) return '';
  const P = umPeriode(hariIniIso(kini), umAtur().periodeHari);
  return 'Umur stok ' + (r.cara === 'rata' ? '(wadah campuran, rata-rata) ' : '(FIFO) ') + umTeksUmur(r) + (umTeksLapisan(r) ? ' — ' + umTeksLapisan(r) : '') + (umTeksHariStok(r) ? ' · ' + umTeksHariStok(r) : '') + ' · ' + umTeksPutaran(r, P) + (r.lambat ? ' · LAMBAT LAKU' : '');
}
