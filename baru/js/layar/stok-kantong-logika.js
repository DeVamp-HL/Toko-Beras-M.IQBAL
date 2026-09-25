// LAYAR STOK — KANTONG (ST4-B+C, dikunci owner 19 Sep 2026): beli kantong kosong & paper bag PER BATCH (jenis · jumlah · harga per LEMBAR),
// rak kantong (tinggi tumpukan = sisa; merah bila cukupnya < hari aman menurut laju pemakaian), buku beli (hapus beralasan), riwayat harga per lembar (▲▼ lonjakan).
// Dokumen = simpanBeliBahanKemasan / simpanBeliBahanLiteran index.html: {id, tipe 'beli', jenis, jumlah, hargaTotal, tanggal} di stokBahanKemasan / stokBahanLiteran
// (+ kolom baru sistem baru: hargaPerPcs — harga per lembar yang DIKETIK, jam, toko). Harga satuan TIDAK PERNAH diambil dari total ÷ jumlah saat mengetik
// (kejadian Rp1.000 untuk 1.000 lembar → Rp1/lembar di nota DAN neraca — memori harga-wadah-satu-digit): harga di bawah lantai ditanya "per LEMBAR?".
// Tunai saja: mesin arus kas sistem berjalan menghitung tiap dokumen tipe 'beli' sebagai uang keluar laci hari itu — bon kantong belum punya buku di mesin mana pun.
// Karung bekas tidak ada di sini: hasil samping, tidak pernah dibeli (memori karung-bekas-hasil-samping). Angka kebijakan owner: aturanToko/kantong.
import { hitungStokBahanKemasan, hitungStokBahanLiteran, hitungLajuPakai } from '../mesin/beku.js';
import { JENDELA_LAJU_HARI } from '../mesin/pembantu.js';
import { ambilBahanKemasan, ambilBahanLiteran, cacheMentah, tolakKunci } from '../data/toko.js';
import { RP, ANGKA } from '../inti/format.js';
import { daftarJenisWadah, jenisWadah, koleksiWadah, WJ_LANTAI_LEMBAR } from './wadah-jual-logika.js';

export const ATUR_KANTONG_BAWAAN = { lonjakan: 15, hariAman: 7, lantaiHarga: WJ_LANTAI_LEMBAR };
export const TAB_KANTONG = [['rak', 'Rak & beli'], ['riwayat', 'Riwayat harga']];
const ktAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const ktKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const ktUrut = (a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0);

export function aturKantong() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'kantong') || null;
  const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : ATUR_KANTONG_BAWAAN[k]);
  return { lonjakan: ambil('lonjakan', (n) => n >= 0 && n <= 100), hariAman: ambil('hariAman', (n) => n >= 0 && n <= 365), lantaiHarga: ambil('lantaiHarga', (n) => n >= 0), dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
export function susunAturKantong(isi, w) {
  const kini = aturKantong(); const baca = (k, syarat, teks) => { if (ktKosong(isi[k])) return { nilai: kini[k] }; const n = ktAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const l = baca('lonjakan', (n) => n >= 0 && n <= 100, 'Batas lonjakan harga harus 0–100 %'); if (l.tolak) return { tolak: l.tolak };
  const h = baca('hariAman', (n) => n >= 0 && n <= 365, 'Stok aman harus 0–365 hari'); if (h.tolak) return { tolak: h.tolak };
  const t = baca('lantaiHarga', (n) => n >= 0 && n <= 100000, 'Lantai harga per lembar harus 0–100.000'); if (t.tolak) return { tolak: t.tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'kantong', tanggal: w.tanggal, jam: w.jam, lonjakan: l.nilai, hariAman: h.nilai, lantaiHarga: t.nilai } }],
    patch: { aturKt: null, kabar: 'Aturan kantong disimpan — lonjakan > ' + l.nilai + ' % ditanya · stok aman ' + h.nilai + ' hari · harga per lembar < ' + RP(t.nilai) + ' ditanya', kabarAwas: false } };
}

/** Jenis kantong yang bisa dibeli: semua jenis buku kecuali hasil samping (karung bekas). */
export function jenisKantong() { return daftarJenisWadah().filter((d) => !d.hasilSamping); }
const ktSemuaDoc = () => ambilBahanKemasan().map((b) => Object.assign({ koleksi: 'stokBahanKemasan' }, b)).concat(ambilBahanLiteran().map((b) => Object.assign({ koleksi: 'stokBahanLiteran' }, b)));
/** Harga per lembar satu dokumen beli: yang DIKETIK bila ada (sistem baru), kalau tidak total ÷ jumlah (dokumen sistem lama). */
export const hargaDokBeli = (b) => (Number(b.hargaPerPcs) > 0 ? Math.round(Number(b.hargaPerPcs)) : (Number(b.jumlah) > 0 ? Math.round((Number(b.hargaTotal) || 0) / Number(b.jumlah)) : 0));
function ktBeliJenis(jenis) { return ktSemuaDoc().filter((b) => b.jenis === jenis && b.tipe === 'beli').sort(ktUrut); }
/** Harga beli terakhir per lembar (dokumen beli terbaru); tanpa dokumen beli → rata-rata buku (saldo awal), ditandai. */
export function hargaAkhirKantong(jenis) {
  const beli = ktBeliJenis(jenis); if (beli.length) return { harga: hargaDokBeli(beli[0]), sejak: beli[0].tanggal || '', dariRata: false, nBeli: beli.length };
  const d = jenisWadah(jenis); const st = d && d.koleksi === 'stokBahanLiteran' ? hitungStokBahanLiteran()[jenis] : hitungStokBahanKemasan()[jenis];
  const rata = st ? (st.hppPerPcs || st.hargaPerPcs || 0) : 0;
  return { harga: rata, sejak: '', dariRata: rata > 0, nBeli: 0 };
}
/** Rak kantong: sisa dari mesin, laju pemakaian 14 hari (pcs/hari), cukup berapa hari; awas bila < hari aman (setelan owner). */
export function rakKantong() {
  const atur = aturKantong(); const laju = hitungLajuPakai().pcsBahan || {}; const bK = hitungStokBahanKemasan(); const bL = hitungStokBahanLiteran();
  const daftar = jenisKantong().map((d) => {
    const st = (d.koleksi === 'stokBahanLiteran' ? bL : bK)[d.jenis] || {}; const sisa = st.sisaPcs || 0; const l = laju[d.jenis] || 0; const hariCukup = l > 0 ? sisa / l : null;
    const hk = hargaAkhirKantong(d.jenis);
    return Object.assign({}, d, { sisa, laju: l, hariCukup, awas: hariCukup !== null && hariCukup < atur.hariAman, hargaAkhir: hk.harga, hargaSejak: hk.sejak, dariRata: hk.dariRata, nBeli: hk.nBeli,
      teksHari: hariCukup === null ? (sisa > 0 ? 'tak ada pemakaian ' + JENDELA_LAJU_HARI + ' hari — lajunya belum bisa dihitung' : 'kosong') : 'cukup ' + Math.floor(hariCukup) + ' hari (laju ' + String(Math.round(l * 10) / 10).replace('.', ',') + '/hari)',
      teksHarga: hk.harga > 0 ? RP(hk.harga) + '/lembar' + (hk.dariRata ? ' (rata-rata buku, belum pernah beli)' : '') : 'belum ada harga' });
  });
  const maks = Math.max(1, ...daftar.map((x) => x.sisa)); daftar.forEach((x) => { x.tinggi = Math.max(0.06, Math.min(1, x.sisa / maks)); });
  const awas = daftar.filter((x) => x.awas);
  return { daftar, awas, maks, atur, rakKet: awas.length ? awas.map((x) => x.label + ' cukup ' + Math.floor(x.hariCukup) + ' hari').join(' · ') + ' — di bawah ' + atur.hariAman + ' hari (setelan owner)' : 'Semua jenis yang terpakai cukup lebih dari ' + atur.hariAman + ' hari' };
}
/** Hitung nota beli yang sedang diketik: total, lantai ("per LEMBAR?"), lonjakan vs beli terakhir. */
export function hitungBeli(draf) {
  const atur = aturKantong(); const d = jenisWadah(draf.jenis); const jumlah = Math.round(ktAngka(draf.jumlah)); const harga = Math.round(ktAngka(draf.harga)); const toko = String(draf.toko || '').trim();
  const hk = d ? hargaAkhirKantong(d.jenis) : { harga: 0 };
  const murah = harga > 0 && harga < atur.lantaiHarga;
  const lonjakPct = hk.harga > 0 && harga > 0 ? Math.round((harga - hk.harga) / hk.harga * 100) : 0; const lonjak = !!d && Math.abs(lonjakPct) > atur.lonjakan;
  return { d, jumlah, harga, toko, total: jumlah * harga, hargaAkhir: hk.harga, murah, lonjak, lonjakPct,
    murahTeks: murah ? RP(harga) + ' per LEMBAR? Di bawah ' + RP(atur.lantaiHarga) + ' — pastikan bukan harga per ikat/pak (sistem lama pernah mencatat Rp1/lembar)' : '',
    lonjakTeks: lonjak ? 'Harga ' + (lonjakPct > 0 ? 'naik ' : 'turun ') + Math.abs(lonjakPct) + ' % dari beli terakhir (' + RP(hk.harga) + ') — batas ' + atur.lonjakan + ' % (setelan owner)' : '',
    teks: d && jumlah > 0 && harga > 0 ? ANGKA(jumlah) + ' × ' + RP(harga) + ' = ' + RP(jumlah * harga) : '' };
}
/** Simpan satu batch beli. yakin = { murah, lonjak } — ketukan kedua. */
export function susunSimpanBeli(draf, w, yakin) {
  const h = hitungBeli(draf); const Y = yakin || {};
  if (!h.d) return { tolak: 'Pilih jenis kantongnya dulu' };
  if (!(h.jumlah > 0)) return { tolak: 'Ketik jumlah lembarnya' };
  if (!(h.harga > 0)) return { tolak: 'Ketik harga SATU lembar (bukan per ikat)' };
  if (h.murah && !Y.murah) return { tolak: h.murahTeks + '. Ketuk sekali lagi kalau memang per lembar', perluYakin: 'murah' };
  if (h.lonjak && !Y.lonjak) return { tolak: h.lonjakTeks + '. Ketuk sekali lagi kalau memang benar', perluYakin: 'lonjak' };
  const data = { id: w.idUnik(), tipe: 'beli', jenis: h.d.jenis, jumlah: h.jumlah, hargaTotal: Math.round(h.jumlah * h.harga), hargaPerPcs: h.harga, tanggal: w.tanggal, jam: w.jam };
  if (h.toko) data.toko = h.toko.slice(0, 60);
  return { dokumen: [{ koleksi: koleksiWadah(h.d.jenis), data }], hitung: h,
    patch: { kt: { jenis: h.d.jenis, jumlah: '', harga: '', toko: h.toko }, ktYakin: {}, kabar: 'Tersimpan: ' + ANGKA(h.jumlah) + ' lembar ' + h.d.label + ' ' + RP(data.hargaTotal) + ' — tunai, keluar dari laci hari ini' + (h.toko ? ' (' + h.toko + ')' : '') + '. Harga ' + RP(h.harga) + '/lembar jadi harga terakhir jenis ini; modal per lembar = rata-rata buku.', kabarAwas: false } };
}
/** Buku beli kantong, terbaru dulu (semua jenis). */
export function bukuBeli(n) {
  return ktSemuaDoc().filter((b) => b.tipe === 'beli').sort(ktUrut).slice(0, n || 30).map((b) => { const d = jenisWadah(b.jenis); const harga = hargaDokBeli(b);
    return { id: b.id, koleksi: b.koleksi, jenis: b.jenis, label: d ? d.label : b.jenis, tanggal: b.tanggal || '', jam: b.jam || '', jumlah: Number(b.jumlah) || 0, harga, total: Number(b.hargaTotal) || 0, toko: b.toko || '', murah: harga > 0 && harga < aturKantong().lantaiHarga, lama: !(Number(b.hargaPerPcs) > 0) }; });
}
/** Hapus satu batch beli: ditolak bila membuat buku jenis itu minus (lembarnya sudah terpakai), butuh alasan & dua ketukan; jejak ke bukuHapus. */
export function susunHapusBeli(id, alasan, w, yakin) {
  const b = ktSemuaDoc().find((x) => String(x.id) === String(id)); if (!b) return { tolak: 'Catatan beli itu sudah tidak ada' };
  if (b.tipe !== 'beli') return { tolak: 'Yang bisa dihapus dari sini hanya catatan BELI — saldo awal / opname / pemakaian punya jalannya sendiri' };
  const kunci = tolakKunci(b.koleksi, b, 'catatan beli ini tidak bisa dihapus. Lembar yang tidak pernah ada: Stok › Cocokkan HARI INI; uangnya tidak punya pembetul (K2)'); if (kunci) return { tolak: kunci, pembalik: 'cocok' };   // putaran 25
  const d = jenisWadah(b.jenis); const st = (d && d.koleksi === 'stokBahanLiteran' ? hitungStokBahanLiteran() : hitungStokBahanKemasan())[b.jenis] || {};
  const sisaSesudah = (st.sisaPcs || 0) - (Number(b.jumlah) || 0);
  if (sisaSesudah < 0) return { tolak: ANGKA(Math.abs(sisaSesudah)) + ' lembar dari batch ini sudah terpakai (adukan / literan / dijual) — dihapus, buku ' + (d ? d.label : b.jenis) + ' jadi minus. Koreksi lewat Cocokkan, bukan hapus.' };
  if (ktKosong(alasan)) return { tolak: 'Hapus butuh alasan — supaya jejaknya bisa dibaca nanti' };
  if (!yakin) return { tolak: 'Ketuk sekali lagi untuk menghapus: sisa ' + (d ? d.label : b.jenis) + ' turun ' + ANGKA(Number(b.jumlah) || 0) + ' lembar, uang ' + RP(Number(b.hargaTotal) || 0) + ' kembali ke laci hari itu, harga terakhir kembali ke beli sebelumnya', perluYakin: true };
  return { hapus: [{ koleksi: b.koleksi, id: b.id }],
    dokumen: [{ koleksi: 'bukuHapus', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, koleksi: b.koleksi, idDok: String(b.id), tanggalDok: b.tanggal || '', pemasok: b.toko || '', ringkas: 'beli ' + ANGKA(Number(b.jumlah) || 0) + ' lembar ' + (d ? d.label : b.jenis) + ' · ' + RP(Number(b.hargaTotal) || 0), alasan: String(alasan).trim(), pasangan: 0 } }],
    patch: { ktHapus: null, ktAlasan: '', ktYakinHapus: false, kabar: 'Batch beli dihapus (' + String(alasan).trim() + '): sisa & harga terakhir dihitung ulang tanpa batch ini; jejaknya di buku hapus', kabarAwas: false } };
}
/** Riwayat harga per lembar tiap jenis (beli saja, lama → baru), lonjakan di atas batas ditandai ▲▼. */
export function riwayatHarga() {
  const atur = aturKantong();
  return jenisKantong().map((d) => { const r = ktBeliJenis(d.jenis).slice().reverse();
    const baris = r.map((b, i) => { const harga = hargaDokBeli(b); const lalu = i > 0 ? hargaDokBeli(r[i - 1]) : 0; const p = lalu > 0 ? Math.round((harga - lalu) / lalu * 100) : 0;
      return { id: b.id, tanggal: b.tanggal || '', harga, jumlah: Number(b.jumlah) || 0, lonjak: i > 0 && Math.abs(p) > atur.lonjakan ? (p > 0 ? '▲ ' : '▼ ') + Math.abs(p) + ' %' : '', murah: harga > 0 && harga < atur.lantaiHarga }; });
    return { jenis: d.jenis, label: d.label, baris, ket: baris.length > 1 ? 'dari ' + RP(baris[0].harga) + ' jadi ' + RP(baris[baris.length - 1].harga) + ' (' + baris.length + ' kali beli)' : baris.length === 1 ? 'baru sekali beli' : 'belum pernah dibeli' }; });
}
