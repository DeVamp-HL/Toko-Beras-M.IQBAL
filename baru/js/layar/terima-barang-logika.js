// TANDA TERIMA BARANG MASUK — lembar untuk supir pemasok (owner 21 Nov 2026).
// Owner: "ketika mencatat barang masuk ada surat terimanya? Guna bukti pembayaran toko tunai / bayar sebagian untuk dikirim ke pemilik
// pemasok melalui supir pemasok."
//
//  1. HANYA MEMBACA. Bahannya kedatangan yang sudah tersimpan (batchMasuk) dan pembayaran bon pemasok yang sudah tercatat. Tidak ada angka
//     uang yang ditulis dari sini; mencetak tanda terima tidak mengubah stok, modal, bon, atau laci.
//  2. NILAI NOTA = jumlah subtotal baris kedatangan, TANPA upah bongkar (upah bongkar ongkos toko, bukan tagihan pemasok).
//  3. PEMBAYARAN. Tunai → lunas saat datang. Bon → "sudah dibayar" dan "sisa" menurut buku utang pemasok (angka yang sama dengan sisa bon di
//     Harga & Pemasok). Akun yang TIDAK membaca pembayaran pemasok (akun tablet) tidak boleh mencetak "sisa = nilai nota" seolah belum
//     dibayar sama sekali: barisnya dikosongkan untuk ditulis tangan dan diparaf, dan lembarnya berkata begitu.
//  4. TANPA harga per kg. Yang dibuktikan = barang yang diterima dan uang yang dibayar; rincian harga ada di nota pemasok sendiri.
//  5. KEADAAN BAYAR BERUBAH sesudah lembar dicetak (bon dicicil), jadi lembar memuat kapan ia dicetak. Nomornya turunan id kedatangan, bukan
//     pencacah baru: dicetak ulang kapan pun nomornya sama.
//  6. DUA LEMBAR: LEMBAR PEMASOK (dibawa supir) · LEMBAR TOKO (arsip, ditandatangani supir).
//  7. CATATAN UNTUK PEMASOK ikut di kedua lembar (owner 28 Nov 2026: "cetak 2 lembar ... ada catatannya yang di tulis/catat di barang masuk"; tombol
//     cetak catatan terpisah DIHAPUS — surat berkop tetap di Laporan › Dokumen › Dokumen kecil). Isinya = penyusun surat yang sama (cpIsiSurat), HANYA
//     yang ditulis toko: catatan toko, ditolak, sudah dibukukan, catatan bebas, permintaan toko. Bagian "yang tertulis di nota" (harga per kg) tidak
//     ikut (butir 4); usul dari timbang yang belum disimpan tidak ikut.
//  8. TIAP BARIS BERTANDA `jenis` berawalan 'tt' (owner 28 Nov 2026: "jauh lebih rapi dan lebih profesional termasuk adakan logo"): printer tablet /
//     pratinjau menggambarnya sebagai dokumen berlogo (inti/struk-model.js stModelTandaTerima + inti/struk-kanvas.js gambarTandaTerima). Gaya teks &
//     WhatsApp memakai baris yang sama apa adanya — isi & angka satu sumber.
// Bentuk garis = garis struk ({ kiri, kanan, tebal, tengah } / { garis: true }), dicetak gaya teks oleh inti/printer.js.
import { RP, KG, DESIMAL, tanggalPendek } from '../inti/format.js';

const bil = (v) => Number(v) || 0;
// pembungkus kata printer merapatkan spasi beruntun, jadi titik-titik isian tangan ditaruh di sisi KANAN baris (rata tepi kanan kertas)
const TITIK = '..................';

/** Kedatangan ini bisa dibuatkan tanda terima? '' = bisa; selain itu kalimat sebabnya. */
export function tbmTolak(batch) {
  if (!batch) return 'Kedatangan itu sudah tidak ada';
  if (batch.stokAwal || batch.tutupBuku || batch.lahirBuku) return 'Catatan ini bukan barang datang dari pemasok (stok awal, saldo pembuka, atau buku baru) — tidak ada tanda terimanya';
  if (!String(batch.pemasok || '').trim()) return 'Kedatangan ini belum bernama pemasok — isi dulu nama pemasoknya lewat koreksi kedatangan';
  if (!(batch.merkList || []).length) return 'Kedatangan ini tidak punya baris barang';
  return '';
}

/** Nomor tanda terima: TT-<tahun bulan hari>-<4 angka terakhir id kedatangan>. */
export function tbmNomor(batch) {
  const t = String((batch && batch.tanggal) || '').replace(/[^0-9]/g, '').slice(2, 8);
  const id = batch && batch.id !== undefined && batch.id !== null ? batch.id : '';
  const ekor = String(id).replace(/[^0-9A-Za-z]/g, '').slice(-4).toUpperCase();
  return 'TT-' + (t || '000000') + '-' + (ekor || '0000');
}

/**
 * Isi tanda terima satu kedatangan.
 * bayar = { terbaca, dibayar, rinci }:
 *   terbaca — akun ini membaca pembayaran pemasok? false = angka bayar bon TIDAK diketahui di perangkat ini (bukan nol).
 *   dibayar — uang yang sudah masuk ke bon ini menurut buku utang pemasok (ckBayarBon().dibayarMesin).
 *   rinci   — pembayaran yang menunjuk bon ini [{ tanggal, nominal }]; dipakai hanya bila jumlahnya persis = dibayar.
 * Hasil.bayar.keadaan: 'tunai' | 'belum' | 'sebagian' | 'lunas' | 'takTerbaca'.
 */
export function tbmData(batch, bayar, catatan) {
  const B = bayar || {};
  const baris = (batch.merkList || []).map((m) => { const bal = m.bentuk === 'bal';
    return { nama: String(m.merk || ''), namaPemasok: String(m.merkPemasok || ''), bal, kemasan: bal && !!m.kemasanJadi, jumlah: bal ? bil(m.jumlahBal) : bil(m.jumlahKarung), berat: bal ? (m.kemasanJadi ? bil(m.ukuranBag) : 0) : bil(m.beratKarung), kg: bil(m.totalKg), nilai: bil(m.subtotalHarga),
      // Tahap 6 (owner 25 Nov 2026): baris "stok ikut timbang" — kg yang dibukukan = hasil timbang; nota tetap jumlah × isi karung (uang dari nota)
      ikut: !bal && bil(m.kgTerima) > 0, kgNota: bal ? bil(m.totalKg) : Math.round(bil(m.jumlahKarung) * bil(m.beratKarung) * 100) / 100 }; });
  const nilai = Math.round(baris.reduce((a, x) => a + x.nilai, 0));
  const jumlah = { karung: baris.reduce((a, x) => a + (x.bal ? 0 : x.jumlah), 0), bal: baris.reduce((a, x) => a + (x.bal && !x.kemasan ? x.jumlah : 0), 0), kemasan: baris.reduce((a, x) => a + (x.kemasan ? x.jumlah : 0), 0), kg: Math.round(baris.reduce((a, x) => a + x.kg, 0) * 100) / 100 };
  const bon = batch.caraBayar === 'utang';
  let hasil;
  // kedatangan yang memakai potongan pemasok (klaim / retur sebelumnya): yang dibayar = nilai nota − potongan
  const potongan = Math.max(0, Math.min(nilai, Math.round(bil(batch.potonganPakai && batch.potonganPakai.rp))));
  if (!bon) hasil = { keadaan: 'tunai', dibayar: nilai - potongan, sisa: 0, rinci: [] };
  else if (!B.terbaca) hasil = { keadaan: 'takTerbaca', dibayar: null, sisa: null, rinci: [] };
  else {
    // batas 0…nilai bukan penjepit diam: uang di atas nilai bon sudah mengalir ke bon lain dan bukan milik lembar ini (aturan ckBayarBon)
    const dibayar = Math.max(0, Math.min(nilai, Math.round(bil(B.dibayar))));
    const rinci = (B.rinci || []).map((x) => ({ tanggal: String(x.tanggal || ''), nominal: Math.round(bil(x.nominal)) })).filter((x) => x.nominal > 0);
    const cocok = rinci.length > 0 && rinci.reduce((a, x) => a + x.nominal, 0) === dibayar;
    hasil = { keadaan: dibayar <= 0 ? 'belum' : dibayar >= nilai ? 'lunas' : 'sebagian', dibayar, sisa: nilai - dibayar, rinci: cocok ? rinci : [] };
  }
  // owner 22 Nov 2026 (paket ③): uang yang dibayar ke supir lewat titipan tablet (belum / tidak terbaca di buku bon perangkat ini) — disebut apa adanya
  hasil.titipSupir = bon ? Math.max(0, Math.round(bil(B.titipSupir))) : 0;
  hasil.potongan = potongan;
  return { no: tbmNomor(batch), tanggal: String(batch.tanggal || ''), jam: String(batch.jam || ''), pemasok: String(batch.pemasok || '').trim(), baris, jumlah, nilai, bon, bayar: hasil,
    catatan: Array.isArray(catatan) ? catatan : [] };
}

/** Kelompok surat yang TIDAK ikut tanda terima: baris nota ber-harga per kg (butir 4) — barang & hasil timbang sudah ada di lembar ini. */
const TBM_BUKAN_CATATAN = /^yang tertulis di nota/i;
/**
 * Catatan untuk pemasok yang ikut tanda terima (butir 7). S = hasil cpIsiSurat(id) (stok-catat-logika) atau null. Hanya bila kedatangan itu PUNYA
 * catatan tersimpan (S.ada) — usul dari timbang yang belum disimpan tidak dicetak. → [{ judul, baris: [{ teks, n ('' = tanpa angka), tebal }] }].
 */
export function tbmCatatan(S) {
  if (!S || !S.ada || !Array.isArray(S.baris)) return [];
  const out = []; let kini = null;
  S.baris.forEach((x) => { if (!x) return; const nama = String(x.nama || '').trim();
    if (x.kelas === 'kel') { kini = TBM_BUKAN_CATATAN.test(nama) ? null : { judul: nama, baris: [] }; if (kini) out.push(kini); return; }
    if (!kini || !nama) return; const adaN = x.n !== '' && x.n !== null && x.n !== undefined && isFinite(Number(x.n));
    kini.baris.push({ teks: nama, n: adaN ? Math.round(Number(x.n)) : '', tebal: x.kelas === 'jumlah' }); });
  return out.filter((k) => k.baris.length);
}
const tbmRpCatatan = (n) => (n === '' ? '' : n < 0 ? '-' + RP(-n) : RP(n));

/** Kalimat pendek keadaan bayar — untuk layar (kartu tanda terima), bukan untuk kertas. */
export function tbmKalimatBayar(d) {
  const b = d.bayar;
  if (b.keadaan === 'tunai') return 'tunai, lunas';
  if (b.keadaan === 'takTerbaca') return b.titipSupir > 0 ? 'bon, dibayar ke supir ' + RP(b.titipSupir) + ' (titipan ke owner)' : 'bon, angka bayarnya tidak terbaca di akun ini';
  if (b.keadaan === 'belum') return 'bon, belum dibayar';
  if (b.keadaan === 'lunas') return 'bon, sudah lunas';
  return 'bon, sudah dibayar ' + RP(b.dibayar) + ', sisa ' + RP(b.sisa);
}

const sebutJumlah = (j) => [j.karung ? j.karung + ' karung' : '', j.kemasan ? j.kemasan + ' kemasan' : '', j.bal ? j.bal + ' bal' : '', KG(j.kg)].filter(Boolean).join(', ');

/**
 * Garis cetak satu lembar. kop = { nama, alamat, telp } (setelan struk); lembar = 'pemasok' | 'toko' | '' (tanpa nama lembar: WhatsApp);
 * dicetak = { tanggal, jam, oleh } — kapan lembar ini dibuat (keadaan bayar berlaku pada saat itu). Tiap baris bertanda `jenis` 'tt…' (butir 8):
 * ttKop · ttAlamat · ttTelp · ttJudul · ttNo · ttLembar · ttDatang · ttDari · ttBarang (nilai = { nama, rinci, kg }) · ttTimbang · ttJumlah · ttNilai ·
 * ttBayar · ttBayarKet · ttKeadaan · ttCatKepala · ttCatJudul · ttCat · ttTtd · ttRuang · ttNamaSupir · ttKaki.
 */
export function tbmGaris(d, kop, lembar, dicetak) {
  const g = []; const b = (kiri, kanan, o) => g.push(Object.assign({ kiri: String(kiri || ''), kanan: kanan === undefined || kanan === null ? '' : String(kanan) }, o || {}));
  const K = kop || {}; const C = dicetak || {};
  if (K.nama) b(String(K.nama).toUpperCase(), '', { tebal: true, tengah: true, jenis: 'ttKop' }); if (K.alamat) b(K.alamat, '', { tengah: true, jenis: 'ttAlamat' });
  if (K.telp) b('Telp ' + K.telp, '', { tengah: true, jenis: 'ttTelp', nilai: String(K.telp) });
  g.push({ garis: true }); b('TANDA TERIMA BARANG', '', { tebal: true, tengah: true, jenis: 'ttJudul' }); b('No. ' + d.no, '', { tengah: true, jenis: 'ttNo', nilai: d.no });
  if (lembar === 'pemasok') b('LEMBAR PEMASOK', '', { tebal: true, tengah: true, jenis: 'ttLembar', nilai: 'pemasok' }); else if (lembar === 'toko') b('LEMBAR TOKO', '', { tebal: true, tengah: true, jenis: 'ttLembar', nilai: 'toko' });
  g.push({ garis: true });
  const datang = tanggalPendek(d.tanggal) + (d.jam ? ' ' + d.jam : '');
  b('Datang: ' + datang, '', { jenis: 'ttDatang', nilai: datang });
  b('Dari: ' + d.pemasok, '', { tebal: true, jenis: 'ttDari', nilai: d.pemasok });
  g.push({ garis: true });
  d.baris.forEach((x) => { const nama = x.nama + (x.namaPemasok ? ' (' + x.namaPemasok + ')' : '');
    const kgNota = x.ikut ? x.kgNota : x.kg;
    const kanan = x.kemasan ? x.jumlah + ' kemasan x ' + DESIMAL(x.berat) + ' = ' + KG(x.kg) : x.bal ? x.jumlah + ' bal' + (x.kg ? ' = ' + KG(x.kg) : '') : x.jumlah + ' x ' + DESIMAL(x.berat) + ' = ' + KG(kgNota);
    const rinci = x.kemasan ? x.jumlah + ' kemasan \u00d7 ' + DESIMAL(x.berat) + ' kg' : x.bal ? x.jumlah + ' bal' : x.jumlah + ' karung \u00d7 ' + DESIMAL(x.berat) + ' kg';
    b(nama, kanan, { jenis: 'ttBarang', nilai: { nama, rinci, kg: x.bal && !x.kemasan && !x.kg ? '' : KG(x.kemasan || x.bal ? x.kg : kgNota) } });
    if (x.ikut) b('  hasil timbang (dibukukan)', KG(x.kg), { jenis: 'ttTimbang' }); });   // Tahap 6: stok ikut timbang — kg nota & kg yang dibukukan sama-sama tertulis
  g.push({ garis: true });
  b('JUMLAH', sebutJumlah(d.jumlah), { tebal: true, jenis: 'ttJumlah' });
  b('Nilai nota', RP(d.nilai), { tebal: true, jenis: 'ttNilai' });
  g.push({ garis: true });
  const y = d.bayar; const by = (kiri, kanan, o) => b(kiri, kanan, Object.assign({ jenis: 'ttBayar' }, o || {})); const ket = (t) => b(t, '', { jenis: 'ttBayarKet' });
  if (y.potongan > 0) by('Potongan klaim / retur lalu', RP(y.potongan));
  if (y.keadaan === 'tunai') { by('Cara bayar', 'TUNAI'); by('DIBAYAR', RP(d.nilai - (y.potongan || 0)), { tebal: true }); by('Sisa', 'LUNAS', { tebal: true }); }
  else if (y.keadaan === 'takTerbaca') { by('Cara bayar', 'BON');
    if (y.titipSupir > 0) { by('Dibayar ke supir', RP(y.titipSupir), { tebal: true }); by('Sisa: Rp', TITIK); ket('Bayar ke supir dicatat ke bon oleh pemilik toko. Sisa ditulis tangan, diparaf toko dan supir.'); }
    else { by('Dibayar: Rp', TITIK); by('Sisa: Rp', TITIK); ket('Angka bayar ditulis tangan, diparaf toko dan supir.'); } }
  else {
    by('Cara bayar', y.keadaan === 'sebagian' ? 'BON, dibayar sebagian' : 'BON');
    y.rinci.forEach((x) => by('Bayar ' + (x.tanggal ? tanggalPendek(x.tanggal) : 'tanpa tanggal'), RP(x.nominal)));
    if (y.rinci.length !== 1) by('Sudah dibayar', RP(y.dibayar));
    if (y.titipSupir > 0) by('Dibayar ke supir (belum dicatat)', RP(y.titipSupir));
    by('SISA BON', y.keadaan === 'lunas' ? 'LUNAS' : RP(y.sisa), { tebal: true });
  }
  if (C.tanggal) b('Keadaan per ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', dicetak ' + C.oleh : ''), '', { jenis: 'ttKeadaan' });
  // butir 7: catatan untuk pemasok yang DITULIS toko di Barang masuk — di kedua lembar & WhatsApp, sebelum tanda tangan
  if ((d.catatan || []).length) {
    g.push({ garis: true }); b('CATATAN UNTUK PEMASOK', '', { tebal: true, tengah: true, jenis: 'ttCatKepala' });
    d.catatan.forEach((k) => { b(String(k.judul).toUpperCase(), '', { tebal: true, jenis: 'ttCatJudul' });
      k.baris.forEach((x) => b(x.teks, tbmRpCatatan(x.n), Object.assign({ jenis: 'ttCat' }, x.tebal ? { tebal: true } : {}))); });
  }
  g.push({ garis: true });
  b('Diterima toko,', 'Supir / pengirim,', { jenis: 'ttTtd' }); b('', '', { jenis: 'ttRuang' }); b('', '', { jenis: 'ttRuang' }); b('(............)', '(............)', { jenis: 'ttRuang' });
  if (lembar === 'toko') { b('Nama terang supir dan jam:', '', { jenis: 'ttNamaSupir' }); b('', '', { jenis: 'ttRuang' }); b('(.............................)', '', { jenis: 'ttRuang' }); g.push({ garis: true }); b('Arsip toko.', '', { tengah: true, jenis: 'ttKaki' }); }
  else if (lembar === 'pemasok') { g.push({ garis: true }); b('Dibawa supir untuk pemilik ' + d.pemasok + '.', '', { tengah: true, jenis: 'ttKaki' }); }
  return g;
}

/** Dua lembar cetak: [LEMBAR PEMASOK, LEMBAR TOKO]. */
export function tbmLembar(d, kop, dicetak) { return [tbmGaris(d, kop, 'pemasok', dicetak), tbmGaris(d, kop, 'toko', dicetak)]; }
