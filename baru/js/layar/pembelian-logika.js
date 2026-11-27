// PAKET P4 · PEMBELIAN, PEMASOK & UTANG (owner 27 Nov 2026; sensus ulang 27 Nov b: A5 A25 A57 B40 B57 B62 B63 B64 B78 B134). Logika TANPA DOM, awalan pb
// (bundel uji jsc satu lingkup). Dijaga alat-uji/uji_pembelian_p4.py (jsc kotak pasir + statis + kontrol + asap cadangan).
//
// Keputusan owner (AskUserQuestion 27 Nov 2026):
//  1. A25 — kuli bongkar = orang pasar (bukan dari pemasok, bukan karyawan). Tarif TERTULIS satu untuk toko, PER KARUNG, sama untuk semua kuli; karung 50 kg & 25 kg
//     boleh beda angka. Tiap Barang masuk dihitung otomatis (karung × tarif) dan DITANDAI kalau upah bongkar yang diketik beda — cuma tanda, tetap boleh disimpan.
//     Disimpan di aturanToko/catatStok.tarifBongkar (dokumen yang sudah dibaca tablet Penjaga laci → tanpa rules baru), berlaku sejak tanggal `mulai` supaya
//     kedatangan lama dicek dengan tarif yang berlaku DI HARINYA. Upah bongkar yang dibaca mesin tetap biayaBongkar kedatangan itu (tidak diubah di sini).
//  2. Upah BORONGAN karyawan: tidak perlu (SATUAN_UPAH tetap hari · minggu · bulan). Mesin beku memang tidak membaca satuan upah (hanya total gaji yang dibayar).
//  3. B40 · B78 — umur utang ke pemasok: bawaan ≤ 7 · 8–30 · 1–3 bulan · > 3 bulan sejak barang datang, per pemasok, + "lewat tempo berapa lama"
//     (1–7 · 8–30 · > 30 hari lewat). Batasnya setelan owner (aturanToko/umurUtang, owner saja).
//  4. A57 buku pembelian & B57 beban gudang 7 hari: tampil di DASBOR saja (kartu yang dipasang owner lewat Atur › + Tambah kartu).
// Keputusan yang saya ambil sendiri (ditulis di BACA-DULU):
//  - B62 · B134 · B63 · B64 ikut Dasbor (kartu "Pembelian per pemasok"), sebelah kartu Pembelian #230/B68; angka = shPembelian (satu aturan rupiah per kedatangan).
//  - Bulan berjalan dibanding bulan lalu SAMPAI TANGGAL YANG SAMA (pembanding adil); bulan lalu penuh tetap disebut.
//  - Rata-rata per pesanan = perkiraan rupiah pesanan saat dibuat (pesananPemasok.rp) ÷ pesanan yang tidak batal, menurut tanggal pesanan dibuat.
//  - A5: piutang per nota (bon-logika pnNota, aturan jatuh tempo yang sama dengan Pelanggan) dipasang di garis Jatuh tempo Bon pemasok sebagai UANG MASUK
//    "kalau dibayar tepat waktu". Yang sudah lewat jatuh tempo TIDAK dihitung (belum tentu masuk) — disebut jumlahnya. Penanda lama "uang toko habis di sini"
//    (kas saja) tetap; penanda kedua memakai kas + piutang yang jatuh tempo.
//  - B57: masuk = pesanan ke pemasok yang masih ditunggu, di tanggal janji TERAKHIR (sesudah digeser); keluar = laju pakai harian beras karung (mesin, jendela
//    yang sama dengan Belanja) + pesanan pelanggan yang terjadwal (pesanan-logika poKebutuhan, jalur karung). Lewat janji & tanpa janji disebut terpisah.
// MESIN UANG TIDAK DISENTUH — semua baca saja kecuali pbSusunTarif (aturanToko/catatStok, kolom tarifBongkar saja) & pbSusunAturUmur (aturanToko/umurUtang).
import { hitungUtangPemasok, hitungLajuPakai } from '../mesin/beku.js';
import { kunciPelanggan, akhirBulanIso, JENDELA_LAJU_HARI } from '../mesin/pembantu.js';
import { ambilSemuaBatch, cacheMentah, ingatPerVersi, ingatStokKarung, stokMerekSaja, lajuLintas, ambilPesananPemasok } from '../data/toko.js';
import { RP, KG, DESIMAL, hariIniIso, tanggalPendek } from '../inti/format.js';
// bon-logika juga punya susunBon (piutang) — yang pemasok diimpor bernama bpSusunBon (pola dasbor-logika & pondasi-logika; bundel jsc memisahkan namanya)
import { susunBon as bpSusunBon } from './bon-pemasok-logika.js';
import { shNilaiKedatangan, shPembelian } from './susut-harga-logika.js';
import { pesananSemua } from './belanja-logika.js';
import { jnPemasokSemua } from './janji-logika.js';
import { pnNota, kelompokUmur } from './bon-logika.js';
import { poKebutuhan } from './pesanan-logika.js';

const pbHariKe = (iso) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || '')); return m ? Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000) : null; };
const pbIso = (n) => new Date(n * 86400000).toISOString().slice(0, 10);
const pbTambah = (iso, n) => pbIso(pbHariKe(iso) + n);
const pbTglSah = (iso) => { const n = pbHariKe(iso); return n !== null && pbIso(n) === String(iso); };
const pbTgl = (iso) => (iso ? tanggalPendek(iso).replace(/ \d{4}$/, '') : 'tanpa tanggal');
const pbKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const pbAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return NaN;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : NaN; };
const pbBulat = (n) => Math.round((Number(n) || 0) * 100) / 100;
const pbKini = (kini) => (kini instanceof Date ? kini : new Date(kini || Date.now()));
const pbNama = (nm) => String(nm || '').trim() || '(tanpa nama pemasok)';
const pbPct = (a, b) => (b > 0 ? (a / b - 1) * 100 : null);
const PB_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const pbHariNama = (iso) => PB_HARI[((((pbHariKe(iso) + 4) % 7) + 7) % 7)];
const pbBulanGeser = (key, n) => { const t = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const y = t + Math.floor(m / 12), mm = ((m % 12) + 12) % 12; return y + '-' + String(mm + 1).padStart(2, '0'); };
const PB_NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
const pbNamaBulan = (key) => PB_NAMA_BULAN[Number(key.slice(5, 7)) - 1] + ' ' + key.slice(0, 4);
const pbAturDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;

// ==================== A25 · TARIF BONGKAR KULI PER KARUNG ====================
export const PB_TARIF_KOLOM = 'tarifBongkar';           // aturanToko/catatStok.tarifBongkar = [{ mulai, berat, rp }] (owner saja menulis; tablet membaca)
export const PB_TARIF_MAKS = 100000;                    // Rp per karung — penjaga salah ketik, bukan kebijakan
export const PB_TARIF_BARIS_MAKS = 60;                  // riwayat tarif yang disimpan (yang paling lama dibuang)
const pbBeratKunci = (n) => String(pbBulat(n));
/** Semua tarif tertulis (urut mulai lalu berat). Baris tidak sah dibuang. */
export function pbTarifDaftar() {
  const a = pbAturDok('catatStok'); const L = a && Array.isArray(a[PB_TARIF_KOLOM]) ? a[PB_TARIF_KOLOM] : [];
  return L.map((x) => ({ mulai: String((x && x.mulai) || ''), berat: pbBulat(x && x.berat), rp: Math.round(Number(x && x.rp)) }))
    .filter((x) => pbTglSah(x.mulai) && x.berat > 0 && isFinite(x.rp) && x.rp >= 0 && x.rp <= PB_TARIF_MAKS)
    .sort((a, b) => a.mulai.localeCompare(b.mulai) || a.berat - b.berat);
}
/** Tarif yang berlaku untuk karung `berat` kg pada tanggal `iso` (yang mulai paling akhir ≤ iso) → { rp, mulai } atau null (belum ditulis). */
export function pbTarifPada(berat, iso, daftar) {
  let t = null; const b = pbBulat(berat); (daftar || pbTarifDaftar()).forEach((x) => { if (x.berat === b && x.mulai <= String(iso || '')) t = x; });
  return t ? { rp: t.rp, mulai: t.mulai } : null;
}
/** Tarif yang berlaku hari ini per ukuran karung (ukuran = isi karung yang bisa dipilih di Barang masuk + ukuran yang pernah diberi tarif). */
export function pbTarifKini(iso, ukuran) {
  const D = pbTarifDaftar(); const set = {}; (ukuran || []).forEach((n) => { if (Number(n) > 0) set[pbBeratKunci(n)] = pbBulat(n); }); D.forEach((x) => { set[pbBeratKunci(x.berat)] = x.berat; });
  const baris = Object.keys(set).map((k) => set[k]).sort((a, b) => b - a).map((berat) => { const T = pbTarifPada(berat, iso, D); const lain = D.filter((x) => x.berat === berat && x.mulai > iso);
    return { berat, rp: T ? T.rp : null, mulai: T ? T.mulai : '', nanti: lain.length ? lain[0] : null }; });
  return { baris, ada: D.length > 0, dariOwner: D.length > 0, riwayat: D.slice().reverse().slice(0, 12) };
}
/**
 * Upah bongkar MENURUT TARIF untuk satu kedatangan (draf Barang masuk atau merkList tersimpan): Σ karung × tarif ukuran karungnya pada `tanggal`. Baris bal &
 * kemasan jadi tidak dihitung (tarif per karung). bongkar = upah bongkar yang diketik / tersimpan (tanpa ongkos kirim). → { keadaan, harap, beda, teks, … }
 * keadaan: tanpaTarif (belum ditulis) · tanpaKarung · cocok · lebih · kurang · kosong (belum diisi) · sebagian (ada ukuran tanpa tarif — tidak dicek).
 */
export function pbCekBongkar(baris, bongkar, tanggal, daftar) {
  const D = daftar || pbTarifDaftar(); const iso = pbTglSah(tanggal) ? String(tanggal) : ''; const per = {};
  (baris || []).forEach((r) => { if (!r || r.bentuk === 'bal' || r.masuk === 'kemasan' || r.ditolak) return; const n = Math.round(Number(pbAngka(r.jumlahKarung)) || 0); const be = pbBulat(Number(r.beratKarung) || 50);
    if (!(n > 0)) return; const k = pbBeratKunci(be); const g = per[k] || (per[k] = { berat: be, n: 0, rp: null, jumlah: 0 }); g.n += n; });
  const rinci = Object.keys(per).map((k) => per[k]).sort((a, b) => b.berat - a.berat); let harap = 0; const tanpa = [];
  rinci.forEach((g) => { const T = iso ? pbTarifPada(g.berat, iso, D) : null; if (T) { g.rp = T.rp; g.jumlah = g.n * T.rp; harap += g.jumlah; } else tanpa.push(g.berat); });
  const karung = rinci.reduce((a, g) => a + g.n, 0); const ketik = pbAngka(bongkar); const b = isFinite(ketik) ? Math.round(ketik) : 0; const kosong = pbKosong(bongkar) || b === 0;
  const rumus = rinci.filter((g) => g.rp !== null).map((g) => g.n + ' karung ' + DESIMAL(g.berat) + ' kg × ' + RP(g.rp)).join(' + ');
  const out = { harap, bongkar: b, beda: b - harap, karung, rinci, tanpaTarif: tanpa, rumus, ada: D.length > 0 };
  if (!D.length) return Object.assign(out, { keadaan: 'tanpaTarif', awas: false, teks: 'Tarif bongkar kuli belum ditulis — upah bongkar tidak dicek' });
  if (!karung) return Object.assign(out, { keadaan: 'tanpaKarung', awas: false, teks: 'Tidak ada karung di kedatangan ini — tarif per karung tidak dipakai' });
  if (tanpa.length) return Object.assign(out, { keadaan: 'sebagian', awas: false, teks: 'Karung ' + tanpa.map((n) => DESIMAL(n) + ' kg').join(' · ') + ' belum ada tarifnya — upah bongkar tidak dicek' + (harap ? ' (yang bertarif: ' + rumus + ' = ' + RP(harap) + ')' : '') });
  if (kosong && harap > 0) return Object.assign(out, { keadaan: 'kosong', awas: true, teks: 'Upah bongkar belum diisi — menurut tarif ' + rumus + ' = ' + RP(harap) });
  if (Math.abs(b - harap) < 0.5) return Object.assign(out, { keadaan: 'cocok', awas: false, teks: 'Sesuai tarif: ' + rumus + ' = ' + RP(harap) });
  return Object.assign(out, { keadaan: b > harap ? 'lebih' : 'kurang', awas: true, teks: 'Upah bongkar ' + RP(b) + ' ' + (b > harap ? 'LEBIH ' : 'KURANG ') + RP(Math.abs(b - harap)) + ' dari tarif (' + rumus + ' = ' + RP(harap) + ') — tetap boleh disimpan' });
}
/** Cek satu kedatangan tersimpan: upah bongkar = biayaBongkar − ongkos kirim (sama dengan Stok › Barang masuk). Kedatangan tablet yang upahnya masih titipan disebut. */
export function pbCekKedatangan(b, daftar) {
  const semua = Math.round(Number(b && b.biayaBongkar) || 0); const ongkir = Math.max(0, Math.min(Math.round(Number(b && b.ongkosKirim) || 0), semua)); const bongkar = semua - ongkir;
  const C = pbCekBongkar((b && b.merkList) || [], String(bongkar), b && b.tanggal, daftar);
  if (b && b.dariTablet && !bongkar && C.keadaan === 'kosong') return Object.assign({}, C, { keadaan: 'titip', awas: false, teks: 'Dicatat dari tablet — upah bongkar lewat titipan (dicek sesudah owner menyetujui) · menurut tarif ' + RP(C.harap) });
  return C;
}
/** Simpan tarif (owner): isi = { mulai: 'YYYY-MM-DD', baris: [{ berat, rp (teks) }] } — baris kosong tidak diubah; rp 0 = tanpa upah. Kolom lain catatStok disalin utuh. */
export function pbSusunTarif(isi, w) {
  const I = isi || {}; const mulai = pbKosong(I.mulai) ? w.tanggal : String(I.mulai).trim(); if (!pbTglSah(mulai)) return { tolak: 'Tanggal mulai berlaku tidak sah' };
  const baru = []; for (const r of (I.baris || [])) { if (!r || pbKosong(r.rp)) continue; const berat = pbBulat(r.berat); const n = pbAngka(r.rp);
    if (!(berat > 0)) return { tolak: 'Ukuran karung tidak sah' }; if (!isFinite(n) || n < 0 || n > PB_TARIF_MAKS || Math.round(n) !== n) return { tolak: 'Tarif karung ' + DESIMAL(berat) + ' kg harus angka bulat 0–' + RP(PB_TARIF_MAKS) };
    baru.push({ mulai, berat, rp: n }); }
  if (!baru.length) return { tolak: 'Ketik tarif per karung dulu (kosong = tidak diubah)' };
  const lama = pbAturDok('catatStok') || { id: 'catatStok' }; const kunci = {}; baru.forEach((x) => { kunci[x.mulai + '|' + pbBeratKunci(x.berat)] = 1; });
  const daftar = pbTarifDaftar().filter((x) => !kunci[x.mulai + '|' + pbBeratKunci(x.berat)]).concat(baru).sort((a, b) => a.mulai.localeCompare(b.mulai) || a.berat - b.berat).slice(-PB_TARIF_BARIS_MAKS);
  const data = Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam }); data[PB_TARIF_KOLOM] = daftar;
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { tbBuka: false, tbKetik: {}, tbMulai: '', kabar: 'Tarif bongkar kuli disimpan — ' + baru.map((x) => 'karung ' + DESIMAL(x.berat) + ' kg ' + RP(x.rp)).join(' · ') + ', berlaku sejak ' + tanggalPendek(mulai) + '. Barang masuk mencocokkan upah bongkar dengan tarif ini (cuma tanda).', kabarAwas: false } };
}

// ==================== A57 · BUKU PEMBELIAN PER PERIODE (+ B63 rata-rata) ====================
export const PB_BUKU_MAKS = 80;   // baris yang digambar kartu; jumlah & total tetap seluruh periode
/** Sisa tiap bon pemasok SEKARANG (mesin beku hitungUtangPemasok): { id kedatangan / bon lama: { sisa, nilai } } — bon yang tidak ada = lunas. */
function pbSisaBon() { const out = {}; hitungUtangPemasok().forEach((px) => (px.bon || []).forEach((b) => { out[String(b.id)] = { sisa: Math.round(b.sisa || 0), nilai: Math.round(b.nilai || 0) }; })); return out; }
const pbRingkasMerek = (b) => (b.merkList || []).map((m) => m.merk + (m.bentuk === 'bal' ? ' ' + (m.jumlahBal || 0) + ' bal' : ' ' + (m.jumlahKarung || 0) + '×' + DESIMAL(Number(m.beratKarung) || 50))).slice(0, 5).join(' · ') + ((b.merkList || []).length > 5 ? ' …' : '');
/**
 * Buku pembelian [dari, sampai]: SEMUA kedatangan (bon + dibayar langsung) dengan status bayar SEKARANG per kedatangan — langsung · LUNAS · sisa Rp — dan
 * cek tarif bongkar. Rupiah per kedatangan = shNilaiKedatangan (aturan yang sama dengan kartu Pembelian & "+ Pembelian" HPP periode) → Σ = shPembelian.
 */
export function pbBukuPembelian(dari, sampai, kini) {
  const iso = hariIniIso(pbKini(kini)); return ingatPerVersi('pbBuku|' + dari + '|' + sampai + '|' + iso, () => pbBukuHitung(String(dari), String(sampai), iso));
}
function pbBukuHitung(dari, sampai, iso) {
  const S = pbSisaBon(); const D = pbTarifDaftar(); const baris = []; let dicatat = 0, nDicatat = 0;
  ambilSemuaBatch().forEach((b) => { const t = String((b && b.tanggal) || ''); if (!t || t < dari || t > sampai) return; const V = shNilaiKedatangan(b); if (V.jenis === 'lewat') return;
    if (V.jenis === 'dicatat') { dicatat += V.rp; nDicatat += 1; return; }
    const beras = Math.round((b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0)); const sb = S[String(b.id)] || null;
    const sisa = V.bon ? (sb ? sb.sisa : 0) : 0; const nilaiBon = V.bon ? (sb ? sb.nilai : beras) : 0; const status = !V.bon ? 'langsung' : sisa > 0 ? 'sisa' : 'lunas';
    const T = pbCekKedatangan(b, D); const karung = (b.merkList || []).reduce((a, m) => a + (m.bentuk === 'bal' ? 0 : Number(m.jumlahKarung) || 0), 0);
    baris.push({ id: String(b.id), tanggal: t, jam: String(b.jam || ''), pemasok: pbNama(b.pemasok), rp: V.rp, beras, bongkarSemua: Math.round(Number(b.biayaBongkar) || 0), kg: pbBulat(V.kg), karung, bon: V.bon, status, sisa, nilaiBon, dibayar: V.bon ? Math.max(0, nilaiBon - sisa) : V.rp,
      noBon: String(b.noBon || ''), merek: pbRingkasMerek(b), tarif: T, dariTablet: !!b.dariTablet,
      statusTeks: status === 'langsung' ? 'dibayar langsung' : status === 'lunas' ? 'bon LUNAS' : 'bon sisa ' + RP(sisa) + (nilaiBon > sisa ? ' dari ' + RP(nilaiBon) : ''),
      tujuan: V.bon ? { ke: 'harga', keluarga: 'bon', pemasok: pbNama(b.pemasok) } : { ke: 'stok', lembar: 'masuk' } }); });
  baris.sort((a, b) => b.tanggal.localeCompare(a.tanggal) || b.jam.localeCompare(a.jam) || (Number(b.id) || 0) - (Number(a.id) || 0));
  const jml = (d, k) => d.reduce((a, x) => a + (Number(x[k]) || 0), 0); const bon = baris.filter((x) => x.bon), langsung = baris.filter((x) => !x.bon);
  const rp = jml(baris, 'rp'); const n = baris.length; const bedaTarif = baris.filter((x) => x.tarif.awas);
  // B63 per pesanan: pesanan ke pemasok yang DIBUAT di periode ini (status sekarang), perkiraan rupiah saat dibuat
  const ps = pesananSemua().filter((p) => { const t = String(p.tanggal || ''); return t >= dari && t <= sampai; }); const psHidup = ps.filter((p) => p.status !== 'batal');
  const psRp = psHidup.reduce((a, p) => a + (Number(p.rp) || 0), 0); const psHarga = psHidup.filter((p) => Number(p.rp) > 0);
  const P = shPembelian(dari, sampai);
  return { dari, sampai, iso, baris, n, rp, kg: pbBulat(jml(baris, 'kg')), rata: n ? rp / n : null, karung: jml(baris, 'karung'),
    bon: { n: bon.length, rp: jml(bon, 'rp'), sisa: jml(bon, 'sisa'), nSisa: bon.filter((x) => x.status === 'sisa').length, nLunas: bon.filter((x) => x.status === 'lunas').length },
    langsung: { n: langsung.length, rp: jml(langsung, 'rp') }, dicatat, nDicatat, bedaTarif: { n: bedaTarif.length, rp: bedaTarif.reduce((a, x) => a + x.tarif.beda, 0) }, tarifAda: D.length > 0,
    pesanan: { n: psHidup.length, nBatal: ps.length - psHidup.length, rp: psRp, rata: psHarga.length ? psHarga.reduce((a, p) => a + Number(p.rp), 0) / psHarga.length : null, tanpaHarga: psHidup.length - psHarga.length },
    menutup: Math.abs(rp - P.rp) < 0.5 && n === P.n, diarsip: !!P.diarsip, terpotong: n > PB_BUKU_MAKS, maks: PB_BUKU_MAKS,
    rumus: 'Tiap kedatangan = Σ harga beras di nota pemasok + bongkar (sama dengan kartu Pembelian & "+ Pembelian" HPP periode). Status bayar = keadaan bon SEKARANG (Harga & Pemasok › Bon pemasok). Rata-rata = total ÷ jumlah kedatangan.',
    sumber: 'Stok › Barang masuk · Bon pemasok', tujuan: { ke: 'stok', lembar: 'masuk' } };
}

// ==================== B62 · B134 · B63 · B64 · PEMBELIAN PER PEMASOK, BULAN INI VS BULAN LALU ====================
/** Satu bulan per pemasok: Rp, kg, kedatangan & rata-rata (shPembelian) + pesanan dibuat bulan itu: datang · menunggu · batal (status sekarang, pesananSemua). */
export function pbPemasokBulan(key, kini) {
  const iso = hariIniIso(pbKini(kini)); return ingatPerVersi('pbPemasokBulan|' + key + '|' + iso, () => pbPemasokHitung(String(key), iso));
}
function pbPemasokHitung(key, iso) {
  const berjalan = key === iso.slice(0, 7); const dari = key + '-01'; const sampai = berjalan ? iso : akhirBulanIso(key); const lalu = pbBulanGeser(key, -1); const laluDari = lalu + '-01'; const laluAkhir = akhirBulanIso(lalu);
  const laluSamaSampai = berjalan ? (lalu + iso.slice(7) <= laluAkhir ? lalu + iso.slice(7) : laluAkhir) : laluAkhir;
  const P = shPembelian(dari, sampai), L = shPembelian(laluDari, laluAkhir), LS = berjalan ? shPembelian(laluDari, laluSamaSampai) : L;
  const per = {}; const pas = (nm) => { const k = kunciPelanggan(nm) || pbNama(nm); return per[k] || (per[k] = { kunci: k, pemasok: pbNama(nm), ini: { rp: 0, kg: 0, n: 0 }, lalu: { rp: 0, kg: 0, n: 0 }, laluSama: { rp: 0, kg: 0, n: 0 }, pesanan: { n: 0, datang: 0, menunggu: 0, batal: 0, rp: 0, nHarga: 0 } }); };
  const isi = (X, k) => (X.pemasok || []).forEach((g) => { const o = pas(g.pemasok)[k]; o.rp += g.rp; o.kg += g.kg; o.n += g.n; });
  isi(P, 'ini'); isi(L, 'lalu'); isi(LS, 'laluSama');
  pesananSemua().forEach((p) => { const t = String(p.tanggal || ''); if (t < dari || t > sampai) return; const g = pas(p.pemasok).pesanan; g.n += 1; g[p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : 'menunggu'] += 1;
    if (p.status !== 'batal' && Number(p.rp) > 0) { g.rp += Number(p.rp); g.nHarga += 1; } });
  const rapi = (o) => { o.kg = pbBulat(o.kg); o.rata = o.n ? o.rp / o.n : null; return o; };
  const banding = berjalan ? 'laluSama' : 'lalu';
  const daftar = Object.keys(per).map((k) => per[k]).map((g) => { ['ini', 'lalu', 'laluSama'].forEach((x) => rapi(g[x])); g.pesanan.rata = g.pesanan.nHarga ? g.pesanan.rp / g.pesanan.nHarga : null;
    g.ubahPct = pbPct(g.ini.rp, g[banding].rp); g.ubahRp = g.ini.rp - g[banding].rp; g.baru = !g[banding].rp && g.ini.rp > 0; g.hilang = g[banding].rp > 0 && !g.ini.rp; return g; })
    .filter((g) => g.ini.rp || g.lalu.rp || g.laluSama.rp || g.pesanan.n)
    .sort((a, b) => b.ini.rp - a.ini.rp || b.lalu.rp - a.lalu.rp || a.pemasok.localeCompare(b.pemasok));
  const tot = (k) => rapi({ rp: daftar.reduce((a, g) => a + g[k].rp, 0), kg: daftar.reduce((a, g) => a + g[k].kg, 0), n: daftar.reduce((a, g) => a + g[k].n, 0) });
  const total = { ini: tot('ini'), lalu: tot('lalu'), laluSama: tot('laluSama'), pesanan: ['n', 'datang', 'menunggu', 'batal', 'rp', 'nHarga'].reduce((o, k) => { o[k] = daftar.reduce((a, g) => a + g.pesanan[k], 0); return o; }, {}) };
  total.pesanan.rata = total.pesanan.nHarga ? total.pesanan.rp / total.pesanan.nHarga : null; total.ubahPct = pbPct(total.ini.rp, total[banding].rp);
  const hariKe = Number(sampai.slice(8, 10)); const nHari = Number(akhirBulanIso(key).slice(8, 10));
  return { key, nama: pbNamaBulan(key), lalu, namaLalu: pbNamaBulan(lalu), berjalan, dari, sampai, laluSamaSampai, banding, daftar, total,
    menutup: Math.abs(total.ini.rp - P.rp) < 0.5 && Math.abs(total.lalu.rp - L.rp) < 0.5 && total.ini.n === P.n && total.lalu.n === L.n, diarsip: !!(P.diarsip || L.diarsip),
    pembandingTeks: berjalan ? pbNamaBulan(lalu) + ' s.d. tanggal ' + Number(laluSamaSampai.slice(8, 10)) + ' (hari ke-' + hariKe + ' dari ' + nHari + ')' : pbNamaBulan(lalu) + ' penuh',
    rumus: 'Rp per pemasok = Σ kedatangan bulan itu (harga beras + bongkar, sama dengan kartu Pembelian). Bulan berjalan dibanding bulan lalu sampai tanggal yang sama. Pesanan = pesanan ke pemasok yang dibuat bulan itu, keadaan sekarang; rata-rata per pesanan = perkiraan rupiah saat dipesan.',
    sumber: 'Stok › Barang masuk · Harga & Pemasok › Belanja', tujuan: { ke: 'harga', keluarga: 'banding' } };
}

// ==================== B40 · B78 · UMUR UTANG KE PEMASOK PER KELOMPOK ====================
export const PB_UMUR_ID = 'umurUtang';
export const PB_UMUR_BAWAAN = { umurBatas: [7, 30, 90], lewatBatas: [7, 30] };   // owner 27 Nov 2026: ≤ 7 · 8–30 · 1–3 bln · > 3 bln; lewat 1–7 · 8–30 · > 30 hari
const pbBatasSah = (x, n) => Array.isArray(x) && x.length === n && x.every((v) => Number.isInteger(v) && v >= 1 && v <= 3650) && x.every((v, i) => i === 0 || x[i - 1] < v);
export function pbAturUmur() {
  const a = pbAturDok(PB_UMUR_ID); const u = a && Array.isArray(a.umurBatas) ? a.umurBatas.map(Number) : null; const l = a && Array.isArray(a.lewatBatas) ? a.lewatBatas.map(Number) : null;
  return { umurBatas: pbBatasSah(u, 3) ? u : PB_UMUR_BAWAAN.umurBatas.slice(), lewatBatas: pbBatasSah(l, 2) ? l : PB_UMUR_BAWAAN.lewatBatas.slice(), dariOwner: !!a, umurMilik: pbBatasSah(u, 3), lewatMilik: pbBatasSah(l, 2) };
}
/** Simpan batas kelompok (owner): isi = { umur: [3 teks], lewat: [2 teks] } — kosong semua = bawaan. */
export function pbSusunAturUmur(isi, w) {
  const I = isi || {}; const baca = (arr, n, nama) => { const t = (arr || []).map((x) => String(x === undefined || x === null ? '' : x).trim()); if (t.every((x) => !x)) return { nilai: null };
    const v = t.map((x) => Number(x)); return pbBatasSah(v, n) ? { nilai: v } : { tolak: nama + ': ' + n + ' angka hari bulat 1–3650, makin besar (mis. ' + (n === 3 ? '7 · 30 · 90' : '7 · 30') + ')' }; };
  const u = baca(I.umur, 3, 'Kelompok umur'); if (u.tolak) return { tolak: u.tolak }; const l = baca(I.lewat, 2, 'Kelompok lewat tempo'); if (l.tolak) return { tolak: l.tolak };
  const data = { id: PB_UMUR_ID, tanggal: w.tanggal, jam: w.jam, umurBatas: u.nilai || PB_UMUR_BAWAAN.umurBatas.slice(), lewatBatas: l.nilai || PB_UMUR_BAWAAN.lewatBatas.slice() };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { umAtur: null, kabar: 'Kelompok umur utang pemasok disimpan — umur ' + pbKelompokUmur(data.umurBatas).map((e) => e.label).join(' · ') + '; lewat tempo ' + pbKelompokLewat(data.lewatBatas).map((e) => e.label).join(' · '), kabarAwas: false } };
}
/** Empat kelompok umur sejak barang datang (aturan & label yang sama dengan piutang pelanggan: bon-logika kelompokUmur). */
export const pbKelompokUmur = (batas) => kelompokUmur(batas);
/** Tiga kelompok lewat tempo dari dua batas: 1–a · (a+1)–b · > b hari lewat. */
export function pbKelompokLewat(batas) { const [a, b] = batas; return [{ id: 'l1', label: (a === 1 ? '1' : '1–' + a) + ' hari', dari: 1, sampai: a }, { id: 'l2', label: (a + 1 === b ? b : (a + 1) + '–' + b) + ' hari', dari: a + 1, sampai: b }, { id: 'l3', label: '> ' + b + ' hari', dari: b + 1, sampai: Infinity }]; }
/**
 * Sisa utang ke pemasok SEKARANG dipecah per pemasok: (1) umur sejak barang datang (bon bergulir = sejak kedatangan terakhir, aturan Bon pemasok) dan (2) keadaan
 * tempo: belum jatuh tempo · lewat 1–7 · 8–30 · > 30 hari · tempo belum disepakati. Satu sumber: susunBon (mesin beku hitungUtangPemasok). Σ tiap pecahan = sisa.
 */
export function pbUmurUtang(kini) {
  const B = bpSusunBon(pbKini(kini)); const A = pbAturUmur(); const KU = pbKelompokUmur(A.umurBatas); const KL = pbKelompokLewat(A.lewatBatas);
  const kosong = () => ({ total: 0, n: 0, umur: KU.map((e) => ({ id: e.id, label: e.label, rp: 0, n: 0 })), tanpaUmur: { rp: 0, n: 0 }, lewat: KL.map((e) => ({ id: e.id, label: 'lewat ' + e.label, rp: 0, n: 0 })), belum: { rp: 0, n: 0 }, tanpaTempo: { rp: 0, n: 0 }, lewatTerlama: 0, tertua: null });
  const per = {}; const tot = kosong();
  B.bon.forEach((b) => { if (!(b.sisa > 0)) return; const g = per[b.pemasok] || (per[b.pemasok] = Object.assign({ pemasok: b.pemasok }, kosong()));
    [g, tot].forEach((o) => { o.total += b.sisa; o.n += 1;
      const u = b.umur === null || b.umur === undefined || !isFinite(b.umur) ? null : Number(b.umur); const ku = u === null ? -1 : KU.findIndex((e) => u >= e.dari && u <= e.sampai);
      if (ku < 0) { o.tanpaUmur.rp += b.sisa; o.tanpaUmur.n += 1; } else { o.umur[ku].rp += b.sisa; o.umur[ku].n += 1; if (o.tertua === null || u > o.tertua) o.tertua = u; }
      if (b.status === 'tanpaTempo') { o.tanpaTempo.rp += b.sisa; o.tanpaTempo.n += 1; }
      else if (b.status === 'lewat') { const h = -b.sisaHari; const kl = KL.findIndex((e) => h >= e.dari && h <= e.sampai); o.lewat[kl < 0 ? KL.length - 1 : kl].rp += b.sisa; o.lewat[kl < 0 ? KL.length - 1 : kl].n += 1; if (h > o.lewatTerlama) o.lewatTerlama = h; }
      else { o.belum.rp += b.sisa; o.belum.n += 1; } }); });
  const daftar = Object.keys(per).map((k) => per[k]).map((g) => Object.assign(g, { rpLewat: g.lewat.reduce((a, x) => a + x.rp, 0),
    lewatTeks: g.lewatTerlama > 0 ? 'lewat tempo paling lama ' + g.lewatTerlama + ' hari' : g.tanpaTempo.n === g.n ? 'tempo belum disepakati' : 'belum ada yang lewat tempo' }))
    .sort((a, b) => b.rpLewat - a.rpLewat || b.total - a.total || a.pemasok.localeCompare(b.pemasok));
  const sum = (o) => o.umur.reduce((a, x) => a + x.rp, 0) + o.tanpaUmur.rp; const sumT = (o) => o.lewat.reduce((a, x) => a + x.rp, 0) + o.belum.rp + o.tanpaTempo.rp;
  tot.rpLewat = tot.lewat.reduce((a, x) => a + x.rp, 0);
  return { iso: B.iso, atur: A, kelompok: KU, kelompokLewat: KL, daftar, total: tot, totalMesin: B.total,
    menutup: Math.abs(tot.total - B.total) < 0.5 && Math.abs(sum(tot) - tot.total) < 0.5 && Math.abs(sumT(tot) - tot.total) < 0.5 && daftar.every((g) => Math.abs(sum(g) - g.total) < 0.5 && Math.abs(sumT(g) - g.total) < 0.5),
    rumus: 'Umur = hari sejak barang datang (bon bergulir: sejak kedatangan terakhir). Lewat tempo = hari sesudah jatuh tempo (tanggal datang + tempo kartu pemasok / tempo umum). Sisa bon dari mesin yang sama dengan Bon pemasok.',
    sumber: 'Harga & Pemasok › Bon pemasok', tujuan: { ke: 'harga', keluarga: 'bon' } };
}

// ==================== A5 · PIUTANG JATUH TEMPO DI GARIS JATUH TEMPO BON PEMASOK ====================
export const PB_GARIS_MIN_HARI = 7;   // garis membawa piutang sampai bon terakhir yang punya tempo, paling sedikit 7 hari ke depan
/**
 * Garis Jatuh tempo Bon pemasok + piutang per nota sebagai uang MASUK kalau dibayar tepat waktu (B = Bon pemasok susunBon(kini) yang SUDAH digambar layar). Bon & penanda
 * lama tidak diubah urutannya; baris piutang disisipkan menurut jatuh temponya (hari yang sama: bon dulu — hati-hati). Piutang lewat jatuh tempo tidak dihitung.
 */
export function pbGarisPiutang(B, kini) {
  const iso = B.iso; const N = pnNota(pbKini(kini)); const bonT = B.bon.filter((b) => b.jatuh); const akhirBon = bonT.reduce((a, b) => (b.jatuh > a ? b.jatuh : a), '');
  const batas = akhirBon && akhirBon > pbTambah(iso, PB_GARIS_MIN_HARI) ? akhirBon : pbTambah(iso, PB_GARIS_MIN_HARI);
  const masuk = N.nota.filter((x) => x.sisa > 0 && pbTglSah(x.jatuhTempo) && x.jatuhTempo >= iso && x.jatuhTempo <= batas)
    .map((x) => ({ tanda: false, piutang: true, id: 'p:' + x.kunci, nama: x.nama, orang: x.orang, tanggal: x.tanggal, jatuh: x.jatuhTempo, sisa: Math.round(x.sisa), faktur: x.faktur, ket: x.ket,
      tempoTeks: (x.jatuhTempo === iso ? 'jatuh tempo HARI INI' : 'jatuh tempo ' + pbTgl(x.jatuhTempo) + ' · ' + (pbHariKe(x.jatuhTempo) - pbHariKe(iso)) + ' hari lagi') + ' · masuk kalau dibayar tepat waktu' }))
    .sort((a, b) => a.jatuh.localeCompare(b.jatuh) || b.sisa - a.sisa);
  const lewat = N.nota.filter((x) => x.sisa > 0 && x.status === 'lewat'); const nanti = N.nota.filter((x) => x.sisa > 0 && pbTglSah(x.jatuhTempo) && x.jatuhTempo > batas);
  const rpLewat = Math.round(lewat.reduce((a, x) => a + x.sisa, 0)); const rpMasuk = masuk.reduce((a, x) => a + x.sisa, 0);
  // sisipkan baris piutang ke garis lama (bon bertempo urut jatuh tempo); bagian "tempo belum disepakati" tetap di ujung
  const garis = []; let i = 0; const ujung = B.garis.findIndex((g) => g.tanda && g.kelas === '' && /tempo belum disepakati/.test(g.teks)); const atas0 = ujung < 0 ? B.garis : B.garis.slice(0, ujung);
  // tanpa satu pun bon bertempo, garis lama tidak punya penanda hari ini — dipasang supaya piutang & yang lewat tetap punya tempat
  const atas = atas0.some((g) => g.tanda && g.kelas === 'kini') || !(masuk.length || lewat.length) ? atas0 : [{ tanda: true, teks: 'hari ini · ' + tanggalPendek(iso), kelas: 'kini' }].concat(atas0);
  atas.forEach((g) => { const tgl = g.tanda ? (g.kelas === 'kini' ? iso : null) : g.jatuh;
    if (tgl) while (i < masuk.length && masuk[i].jatuh < tgl) garis.push(masuk[i++]);
    garis.push(g);
    if (g.tanda && g.kelas === 'kini' && lewat.length) garis.push({ tanda: true, kelas: 'piutang-lewat', teks: 'piutang LEWAT jatuh tempo ' + RP(rpLewat) + ' (' + lewat.length + ' nota) — belum tentu masuk, tidak dihitung' }); });
  while (i < masuk.length) garis.push(masuk[i++]);
  if (ujung >= 0) B.garis.slice(ujung).forEach((g) => garis.push(g));
  // penanda kedua: kas + piutang yang masuk sampai tanggal itu − bon bertempo (urut garis)
  let jalan = B.kas === null ? null : B.kas; let habis = false; const out = [];
  garis.forEach((g) => { if (jalan !== null && !g.tanda && g.jatuh) { if (g.piutang) jalan += g.sisa; else { if (!habis && jalan - g.sisa < 0) { const t = out[out.length - 1];
        // penanda lama (kas saja) tepat di tempat yang sama = belum ada piutang yang masuk sebelum bon ini → satu penanda saja, teksnya ditambah (objek B.garis tidak diubah)
        if (t && t.tanda && t.kelas === 'habis') out[out.length - 1] = Object.assign({}, t, { teks: t.teks + ' · piutang yang jatuh tempo sebelumnya pun tidak menutup', gabung: true });
        else out.push({ tanda: true, kelas: 'habis2', teks: 'uang toko + piutang yang dibayar tepat waktu pun habis di sini — bon berikut kurang ' + RP(g.sisa - jalan) }); habis = true; } jalan -= g.sisa; } } out.push(g); });
  const cukup2 = !bonT.length ? '' : B.kas === null ? 'Uang toko belum bisa dihitung — piutang yang jatuh tempo ' + RP(rpMasuk) + ' tetap digambar.' : habis ? 'Ditambah piutang yang dibayar tepat waktu (' + RP(rpMasuk) + ') pun, uang toko TIDAK cukup untuk semua bon bertempo.' : B.kurang ? 'Kalau piutang yang jatuh tempo (' + RP(rpMasuk) + ') dibayar tepat waktu, uang toko CUKUP untuk semua bon bertempo.' : 'Uang toko cukup tanpa menunggu piutang (' + RP(rpMasuk) + ' jatuh tempo sampai ' + pbTgl(batas) + ').';
  return { garis: out, masuk, nMasuk: masuk.length, rpMasuk, lewat: { n: lewat.length, rp: rpLewat }, nanti: { n: nanti.length, rp: Math.round(nanti.reduce((a, x) => a + x.sisa, 0)) }, batas, kurang2: habis, cukupTeks2: cukup2,
    rumus: 'Piutang per nota = aturan jatuh tempo Pelanggan › Bon (tanggal nota + tempo kartu pelanggan; faktur = jatuh tempo fakturnya). Dihitung masuk hanya yang belum lewat jatuh tempo, sampai ' + pbTgl(batas) + '.' };
}

// ==================== B57 · PRAKIRAAN BEBAN GUDANG 7 HARI ====================
export const PB_BEBAN_HARI = 7;
/**
 * Tujuh hari mulai hari ini: barang MASUK = pesanan ke pemasok yang masih ditunggu di tanggal janji terakhirnya (janji-logika); KELUAR = laju pakai harian beras
 * karung (mesin hitungLajuPakai, lintas arsip — jendela yang sama dengan Belanja) + pesanan pelanggan yang terjadwal hari itu (poKebutuhan, jalur karung);
 * isi gudang akhir hari = beras karung sekarang (buku kg, wadah literan tidak ikut) + masuk − keluar. Perkiraan — bukan catatan.
 */
export function pbBebanGudang(kini) {
  const iso = hariIniIso(pbKini(kini)); return ingatPerVersi('pbBeban|' + iso, () => pbBebanHitung(pbKini(kini), iso));
}
function pbBebanHitung(k, iso) {
  const stok = stokMerekSaja(ingatStokKarung()); const kgKini = pbBulat(Object.keys(stok).reduce((a, m) => a + Math.max(0, Number(stok[m] && stok[m].sisaKg) || 0), 0));
  const L = lajuLintas(hitungLajuPakai()) || {}; const laju = pbBulat(Object.keys(L.kgMerk || {}).reduce((a, m) => a + (Number(L.kgMerk[m]) || 0), 0));
  const hari = []; for (let i = 0; i < PB_BEBAN_HARI; i++) { const t = pbTambah(iso, i); hari.push({ i, iso: t, label: (i === 0 ? 'Hari ini' : i === 1 ? 'Besok' : pbHariNama(t)) + ' ' + pbTgl(t), masuk: { n: 0, kg: 0, karung: 0, rp: 0, pemasok: [] }, keluar: { laju, pesanan: 0, siapa: [], kg: 0 }, akhir: 0 }); }
  const dok = {}; (ambilPesananPemasok() || []).forEach((p) => { dok[String(p.id)] = p; });
  const lewatJanji = [], tanpaJanji = [], jauh = [];
  jnPemasokSemua(k).forEach((x) => { if (x.batal || x.sampai) return; const p = dok[x.id] || {}; const J = x.janji || {}; const tgl = J.akhir || J.awal || '';
    const o = { id: x.id, pemasok: x.nama, kg: pbBulat(p.kg), karung: Math.round(Number(p.karung) || x.pesan || 0), rp: Math.round(Number(p.rp) || 0), janji: tgl, dibuat: x.dibuat };
    if (!tgl) { tanpaJanji.push(o); return; } if (tgl < iso) { lewatJanji.push(Object.assign(o, { telat: pbHariKe(iso) - pbHariKe(tgl) })); return; }
    const i = pbHariKe(tgl) - pbHariKe(iso); if (i >= PB_BEBAN_HARI) { jauh.push(o); return; }
    const M = hari[i].masuk; M.n += 1; M.kg += o.kg; M.karung += o.karung; M.rp += o.rp; M.pemasok.push(o); });
  const K = poKebutuhan(iso); Object.keys(K).forEach((kunci) => { if (kunci.indexOf('karung|') !== 0) return; K[kunci].forEach((x) => { if (x.hari >= 0 && x.hari < PB_BEBAN_HARI) { const h = hari[x.hari]; h.keluar.pesanan += Number(x.n) || 0; if (h.keluar.siapa.indexOf(x.siapa) < 0) h.keluar.siapa.push(x.siapa); } }); });
  let jalan = kgKini; hari.forEach((h) => { h.masuk.kg = pbBulat(h.masuk.kg); h.keluar.pesanan = pbBulat(h.keluar.pesanan); h.keluar.kg = pbBulat(h.keluar.laju + h.keluar.pesanan); jalan = jalan + h.masuk.kg - h.keluar.kg; h.akhir = pbBulat(jalan); h.kurang = h.akhir < 0; });
  const masukKg = pbBulat(hari.reduce((a, h) => a + h.masuk.kg, 0)); const keluarKg = pbBulat(hari.reduce((a, h) => a + h.keluar.kg, 0)); const kurang = hari.find((h) => h.kurang) || null;
  const puncak = hari.reduce((a, h) => (h.masuk.kg > (a ? a.masuk.kg : 0) ? h : a), null);
  return { iso, hari, kgKini, laju, masukKg, keluarKg, akhir: hari[hari.length - 1].akhir, kurang, puncak, lewatJanji, tanpaJanji, jauh, nMasuk: hari.reduce((a, h) => a + h.masuk.n, 0),
    kalimat: (kurang ? 'Beras karung diperkirakan HABIS ' + kurang.label + ' (kurang ' + KG(-kurang.akhir) + ') kalau barang tidak datang lebih cepat. ' : '')
      + (puncak ? 'Kedatangan terbesar ' + puncak.label + ' (' + KG(puncak.masuk.kg) + ', ' + puncak.masuk.n + ' kedatangan). ' : 'Belum ada kedatangan berjanji dalam 7 hari. ')
      + (lewatJanji.length ? lewatJanji.length + ' pesanan lewat janji masih ditunggu. ' : '') + (tanpaJanji.length ? tanpaJanji.length + ' pesanan belum punya tanggal janji.' : ''),
    rumus: 'Masuk = pesanan ke pemasok yang ditunggu, di tanggal janji terakhirnya. Keluar = laju pakai beras karung ' + DESIMAL(laju) + ' kg/hari (rata-rata ' + JENDELA_LAJU_HARI + ' hari terakhir, sama dengan Belanja) + pesanan pelanggan terjadwal. Perkiraan, bukan catatan.',
    sumber: 'Harga & Pemasok › Belanja · Stok', tujuan: { ke: 'harga', keluarga: 'belanja' } };
}
