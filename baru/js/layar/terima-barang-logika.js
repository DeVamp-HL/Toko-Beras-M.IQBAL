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
export function tbmData(batch, bayar) {
  const B = bayar || {};
  const baris = (batch.merkList || []).map((m) => { const bal = m.bentuk === 'bal';
    return { nama: String(m.merk || ''), namaPemasok: String(m.merkPemasok || ''), bal, kemasan: bal && !!m.kemasanJadi, jumlah: bal ? bil(m.jumlahBal) : bil(m.jumlahKarung), berat: bal ? (m.kemasanJadi ? bil(m.ukuranBag) : 0) : bil(m.beratKarung), kg: bil(m.totalKg), nilai: bil(m.subtotalHarga) }; });
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
  return { no: tbmNomor(batch), tanggal: String(batch.tanggal || ''), jam: String(batch.jam || ''), pemasok: String(batch.pemasok || '').trim(), baris, jumlah, nilai, bon, bayar: hasil };
}

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
 * dicetak = { tanggal, jam, oleh } — kapan lembar ini dibuat (keadaan bayar berlaku pada saat itu).
 */
export function tbmGaris(d, kop, lembar, dicetak) {
  const g = []; const b = (kiri, kanan, o) => g.push(Object.assign({ kiri: String(kiri || ''), kanan: kanan === undefined || kanan === null ? '' : String(kanan) }, o || {}));
  const K = kop || {}; const C = dicetak || {};
  if (K.nama) b(String(K.nama).toUpperCase(), '', { tebal: true, tengah: true }); if (K.alamat) b(K.alamat, '', { tengah: true }); if (K.telp) b('Telp ' + K.telp, '', { tengah: true });
  g.push({ garis: true }); b('TANDA TERIMA BARANG', '', { tebal: true, tengah: true }); b('No. ' + d.no, '', { tengah: true });
  if (lembar === 'pemasok') b('LEMBAR PEMASOK', '', { tebal: true, tengah: true }); else if (lembar === 'toko') b('LEMBAR TOKO', '', { tebal: true, tengah: true });
  g.push({ garis: true });
  b('Datang: ' + tanggalPendek(d.tanggal) + (d.jam ? ' ' + d.jam : ''));
  b('Dari: ' + d.pemasok, '', { tebal: true });
  g.push({ garis: true });
  d.baris.forEach((x) => b(x.nama + (x.namaPemasok ? ' (' + x.namaPemasok + ')' : ''), x.kemasan ? x.jumlah + ' kemasan x ' + DESIMAL(x.berat) + ' = ' + KG(x.kg) : x.bal ? x.jumlah + ' bal' + (x.kg ? ' = ' + KG(x.kg) : '') : x.jumlah + ' x ' + DESIMAL(x.berat) + ' = ' + KG(x.kg)));
  g.push({ garis: true });
  b('JUMLAH', sebutJumlah(d.jumlah), { tebal: true });
  b('Nilai nota', RP(d.nilai), { tebal: true });
  g.push({ garis: true });
  const y = d.bayar;
  if (y.potongan > 0) b('Potongan klaim / retur lalu', RP(y.potongan));
  if (y.keadaan === 'tunai') { b('Cara bayar', 'TUNAI'); b('DIBAYAR', RP(d.nilai - (y.potongan || 0)), { tebal: true }); b('Sisa', 'LUNAS', { tebal: true }); }
  else if (y.keadaan === 'takTerbaca') { b('Cara bayar', 'BON');
    if (y.titipSupir > 0) { b('Dibayar ke supir', RP(y.titipSupir), { tebal: true }); b('Sisa: Rp', TITIK); b('Bayar ke supir dicatat ke bon oleh pemilik toko. Sisa ditulis tangan, diparaf toko dan supir.'); }
    else { b('Dibayar: Rp', TITIK); b('Sisa: Rp', TITIK); b('Angka bayar ditulis tangan, diparaf toko dan supir.'); } }
  else {
    b('Cara bayar', y.keadaan === 'sebagian' ? 'BON, dibayar sebagian' : 'BON');
    y.rinci.forEach((x) => b('Bayar ' + (x.tanggal ? tanggalPendek(x.tanggal) : 'tanpa tanggal'), RP(x.nominal)));
    if (y.rinci.length !== 1) b('Sudah dibayar', RP(y.dibayar));
    if (y.titipSupir > 0) b('Dibayar ke supir (belum dicatat)', RP(y.titipSupir));
    b('SISA BON', y.keadaan === 'lunas' ? 'LUNAS' : RP(y.sisa), { tebal: true });
  }
  if (C.tanggal) b('Keadaan per ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', dicetak ' + C.oleh : ''));
  g.push({ garis: true });
  b('Diterima toko,', 'Supir / pengirim,'); b(''); b(''); b('(............)', '(............)');
  if (lembar === 'toko') { b('Nama terang supir dan jam:'); b(''); b('(.............................)'); g.push({ garis: true }); b('Arsip toko.', '', { tengah: true }); }
  else if (lembar === 'pemasok') { g.push({ garis: true }); b('Dibawa supir untuk pemilik ' + d.pemasok + '.', '', { tengah: true }); }
  return g;
}

/** Dua lembar cetak: [LEMBAR PEMASOK, LEMBAR TOKO]. */
export function tbmLembar(d, kop, dicetak) { return [tbmGaris(d, kop, 'pemasok', dicetak), tbmGaris(d, kop, 'toko', dicetak)]; }

/**
 * Tahap 5 (owner 26 Nov 2026: "catatan bisa juga dicetak lewat tanda terima, tidak hanya melewati dokumen"): garis cetak STRUK "Catatan untuk pemasok" satu
 * kedatangan. S = hasil cpIsiSurat (stok-catat-logika) — isi yang SAMA dengan Laporan › Dokumen kecil › Catatan untuk pemasok; di sini hanya ditata untuk kertas
 * struk: judul kelompok = garis + huruf besar, baris berangka = angka di kanan (potongan yang sudah dibukukan bertanda minus). no = nomor tanda terimanya.
 */
export function tbmGarisCatatan(S, kop, no, dicetak) {
  const g = []; const b = (kiri, kanan, o) => g.push(Object.assign({ kiri: String(kiri || ''), kanan: kanan === undefined || kanan === null ? '' : String(kanan) }, o || {}));
  const K = kop || {}; const C = dicetak || {};
  if (K.nama) b(String(K.nama).toUpperCase(), '', { tebal: true, tengah: true }); if (K.alamat) b(K.alamat, '', { tengah: true }); if (K.telp) b('Telp ' + K.telp, '', { tengah: true });
  g.push({ garis: true }); b('CATATAN UNTUK PEMASOK', '', { tebal: true, tengah: true }); if (no) b('Tanda terima No. ' + no, '', { tengah: true });
  g.push({ garis: true }); String(S.sub || '').split(' \u00b7 ').filter(Boolean).forEach((t, i) => b(i === 0 ? 'Kepada: ' + t : t, '', i === 0 ? { tebal: true } : {}));
  (S.baris || []).forEach((x) => { const adaN = x.n !== '' && x.n !== null && x.n !== undefined;
    if (x.kelas === 'kel') { g.push({ garis: true }); b(String(x.nama).toUpperCase(), '', { tebal: true }); return; }
    b(String(x.nama).replace(/^\s+/, '  '), adaN ? (x.n < 0 ? '-' + RP(-x.n) : RP(x.n)) : '', x.kelas === 'jumlah' ? { tebal: true } : {}); });
  g.push({ garis: true }); b(S.identitas || '');
  if (C.tanggal) b('Dicetak ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', ' + C.oleh : ''));
  g.push({ garis: true }); b('Dari toko,', 'Diterima pemasok / supir,'); b(''); b(''); b('(............)', '(............)');
  return g;
}
