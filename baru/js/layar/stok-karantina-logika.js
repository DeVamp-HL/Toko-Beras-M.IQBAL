// LAYAR STOK — MENCATAT (tanpa DOM): KEPUTUSAN KARANTINA. Dijaga alat-uji/uji_stok_baru.py.
//
// Barang retur yang tidak layak dijual masuk karantina (dokumen `karantina` ber-id sama dengan returnya) dan menunggu SATU keputusan owner
// (putuskanKarantina index.html 22152 + returJadiLayakJual 16066):
//   · ternyata layak jual → returnya dikoreksi kondisi 'utuh' (arti mesin: kembali ke stok jual, modalnya dibatalkan → laba tanggal retur naik) + kartu 'layak_jual';
//     TIDAK ada dokumen stok — hitungStokKarungPerMerk / hitungStokKemasan / hitungLabaRentang membaca retur 'utuh' sendiri
//   · rework → stok: kemasan = dokumen produksiKemasan tanpa bahan (modal per unit = rata-rata produk itu SAAT INI); karung = penyesuaianStok dariRework
//     (nilaiRp 0, seragam dengan rework kemasan — keputusan owner 9 Sep 2026) — barangnya DULU, statusnya belakangan (satu writeBatch)
//   · balik ke pemasok / buang → hanya status berubah. Kerugiannya SUDAH tercatat saat retur dicatat (retur tidak-utuh tidak membalik modal), jadi
//     membuang TIDAK mengubah laba lagi — kalimatnya jujur soal itu (memori: status yang berbohong soal uang).
// Penjaga yang sama dipakai untuk MENAMPILKAN pilihan dan untuk MENULIS (kqPeriksa) supaya keduanya tidak berselisih (memori: dijaga di satu tempat).
// Beda dari sistem lama: koreksi layak jual ditulis lewat writeBatch dari salinan perangkat ini (bukan transaksi yang membaca ulang server) — putuskan dari
// SATU perangkat; penolakan "sudah dikoreksi" tetap berlaku dari salinan itu.
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { ambilKarantina, ambilRetur, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan } from '../data/toko.js';
import { RP } from '../inti/format.js';

export const TINDAKAN_KARANTINA = [['layak_jual', 'Ternyata layak jual → kembali ke stok'], ['dirework', 'Rework → masuk stok lagi'], ['dikembalikan_pemasok', 'Balik ke pemasok'], ['dibuang', 'Buang']];
export const LABEL_TINDAKAN = { layak_jual: 'ternyata layak jual → stok', dirework: 'rework ke stok', dikembalikan_pemasok: 'balik ke pemasok', dibuang: 'dibuang', belum_diputuskan: 'menunggu' };
const kqUkuran = (u) => String(u === undefined || u === null ? '' : u).replace('.', ',');
const kqNama = (k) => (k.jenisAsal === 'kemasan' ? (k.namaProduk || '') + ' ' + kqUkuran(k.ukuranKemasan) + ' kg' : (k.merkSumber || ''));
const kqKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const kqRetur = (id) => ambilRetur().find((x) => String(x.id) === String(id)) || null;
const kqJejak = (id) => 'retur id ' + id + ')';
const kqSudahRework = (k) => (k.jenisAsal === 'kemasan' ? ambilProduksi() : ambilPenyesuaianStok().filter((x) => x.dariRework)).some((x) => String(x.alasan || x.catatan || '').indexOf(kqJejak(k.id)) >= 0);
const kqSesudah = (r) => { const jamR = r.jam || '00:00'; return (x) => (x.tanggal || '') > (r.tanggal || '') || ((x.tanggal || '') === (r.tanggal || '') && (x.jam || '99:99') >= jamR); };
/** Stok & modal barang karantina menurut mesin: karung per kg, kemasan per unit. */
function kqStok(k) {
  const karung = k.jenisAsal !== 'kemasan'; const kunci = karung ? k.merkSumber : kunciKemasan(k.namaProduk, k.ukuranKemasan);
  const st = kunci ? (karung ? hitungStokKarungPerMerk() : hitungStokKemasan())[kunci] : null; if (!st) return null;
  return { karung, kunci, sisa: karung ? st.sisaKg : st.sisaUnit, hpp: karung ? (st.hppTerakhirPerKg || 0) : (st.hppRataRataPerUnit || 0), satuan: karung ? 'kg' : 'unit' };
}
/** Jumlah yang kembali dalam satuan mesin: karung = kg, kemasan = unit (dari retur, atau dibulatkan dari kg karantina). */
function kqJumlah(k, r) { if (k.jenisAsal !== 'kemasan') return k.totalKg || 0; if (r && r.jumlahUnit) return r.jumlahUnit; const u = Number(k.ukuranKemasan) || 0; return u > 0 ? Math.round((k.totalKg || 0) / u) : 0; }
/** Satu penjaga untuk pilihan yang tampil DAN yang ditulis: '' = boleh, selain itu alasannya. */
function kqPeriksa(k, tindakan, w) {
  if (!k) return 'Kartu karantina itu sudah tidak ada';
  if ((k.statusTindakan || 'belum_diputuskan') !== 'belum_diputuskan') return 'Kartu ini sudah diputuskan (' + (LABEL_TINDAKAN[k.statusTindakan] || k.statusTindakan) + ')';
  const r = kqRetur(k.id);
  if (tindakan === 'layak_jual') {
    if (!k.asalRetur || !r) return 'Kartu ini tidak punya retur asal — tidak ada yang bisa dikoreksi; pilih rework, balik ke pemasok, atau buang';
    if (r.kondisi === 'utuh') return '';   // retur sudah 'utuh' → yang tersisa cuma menutup kartunya
    if (kqSudahRework(k)) return 'Retur ini SUDAH pernah di-rework ke stok (dokumen rework-nya ada) — barangnya sudah kembali; koreksi ditolak supaya stok tidak terhitung dua kali';
    if (!kqStok(k)) return 'Stok "' + kqNama(k) + '" tidak dikenal mesin — kalau dikoreksi tidak ada stok yang bertambah';
    if (w && String(r.tanggal || '').slice(0, 4) !== String(w.tanggal || '').slice(0, 4)) return 'Retur ' + r.tanggal + ' ada di tahun lain — arsip & saldo pembukanya dihitung dari kondisi lama; koreksi ditolak';
    return '';
  }
  if (r && r.kondisi === 'utuh') return 'Retur asal barang ini sudah dikoreksi LAYAK JUAL — barangnya sudah kembali ke stok; rework / buang / balik ditolak supaya tidak terhitung dua kali. Tutup kartunya lewat "ternyata layak jual"';
  if (tindakan === 'dirework') {
    if (kqSudahRework(k)) return 'Sudah pernah di-rework (dokumen rework-nya ada) — jangan dua kali';
    if (k.jenisAsal === 'kemasan' && !(Number(k.ukuranKemasan) > 0)) return 'Kemasan ini tidak menyimpan ukurannya — jumlah unitnya tidak bisa dihitung';
    if (k.jenisAsal !== 'kemasan' && !k.merkSumber) return 'Karung ini tidak menyimpan nama asalnya — sistem tidak tahu stok nama mana yang bertambah; catat lewat Barang masuk';
    return '';
  }
  if (tindakan === 'dibuang' || tindakan === 'dikembalikan_pemasok') return '';
  return 'Tindakan tidak dikenal';
}
/** Kalimat akibat tiap tindakan (jujur soal uang) — dipakai layar sebelum menulis. */
function kqAkibat(k, tindakan) {
  const st = kqStok(k); const r = kqRetur(k.id); const jml = kqJumlah(k, r); const nama = kqNama(k);
  if (tindakan === 'layak_jual') { if (r && r.kondisi === 'utuh') return 'Retur ini SUDAH tercatat kembali ke stok — yang ditutup cuma kartunya; stok tidak bertambah lagi.';
    const naik = st ? Math.round(jml * st.hpp) : 0;
    return 'stok ' + nama + ' +' + String(jml).replace('.', ',') + ' ' + (st ? st.satuan : '') + (st ? ' (sekarang ' + String(Math.round(st.sisa * 100) / 100).replace('.', ',') + ' ' + st.satuan + ')' : '') + ' · ' + (naik > 0 ? 'laba & margin tanggal retur naik ±' + RP(naik) + ' — modal barang ini dibatalkan (taksiran modal rata-rata saat ini)' : 'modal barang ini belum bisa ditaksir (Rp0) — laba belum ikut naik')
      + ' · nilai stok & kekayaan toko naik, kas tidak berubah' + (st && st.karung ? ' · barangnya karung TERBUKA: jual kiloan, bukan sack utuh' : ''); }
  if (tindakan === 'dirework') return k.jenisAsal === 'kemasan' ? 'stok ' + nama + ' +' + jml + ' unit dengan modal per unit = rata-rata produk itu sekarang (' + RP(Math.round(st ? st.hpp : 0)) + '); laba tidak berubah hari ini' : 'stok ' + nama + ' +' + String(k.totalKg || 0).replace('.', ',') + ' kg tanpa mengubah modal per kg (nilai Rp0, tidak menyentuh laba — seragam dengan rework kemasan)';
  if (tindakan === 'dibuang') return 'Kerugiannya SUDAH tercatat waktu returnya dicatat — barang ini nol di pembukuan sejak itu; membuangnya TIDAK mengubah laba. Yang berubah cuma antrean karantina.';
  return 'Barang TIDAK masuk stok jual; uangnya (kalau pemasok mengganti) dicatat terpisah. Laba tidak berubah — kerugiannya sudah tercatat saat retur.';
}
/** Antrean karantina + pilihan tindakan yang boleh (dengan alasan bila tidak), plus riwayat keputusan terakhir. */
export function daftarKarantina(w) {
  const antre = ambilKarantina().filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan').map((k) => { const r = kqRetur(k.id); const st = kqStok(k);
    const opname = r ? (k.jenisAsal !== 'kemasan' ? ambilPenyesuaianStok().filter((x) => x.merk === k.merkSumber && !x.dariRework && kqSesudah(r)(x)) : ambilPenyesuaianKemasan().filter((x) => kunciKemasan(x.namaProduk, x.ukuranKemasan) === kunciKemasan(k.namaProduk, k.ukuranKemasan) && kqSesudah(r)(x))) : [];
    return { id: String(k.id), nama: kqNama(k), kg: k.totalKg || 0, jumlah: kqJumlah(k, r), satuan: k.jenisAsal === 'kemasan' ? 'unit' : 'kg', tanggal: k.tanggal || '', catatan: k.catatan || '', jenisAsal: k.jenisAsal || 'karung', asalRetur: !!k.asalRetur, returUtuh: !!(r && r.kondisi === 'utuh'), stokDikenal: !!st,
      opnameSesudah: opname.map((x) => (x.tanggal || '') + (x.jam ? ' ' + x.jam : '')), pilihan: TINDAKAN_KARANTINA.map(([t, label]) => { const sebab = kqPeriksa(k, t, w); return { tindakan: t, label, bisa: !sebab, sebab, akibat: sebab ? '' : kqAkibat(k, t) }; }) }; })
    .sort((a, b) => a.tanggal.localeCompare(b.tanggal));
  return { antre, totalKg: antre.reduce((a, x) => a + x.kg, 0), riwayat: riwayatKarantina(8) };
}
export function riwayatKarantina(n) {
  return ambilKarantina().filter((k) => k.statusTindakan && k.statusTindakan !== 'belum_diputuskan').sort((a, b) => String(b.tanggalKeputusan || '').localeCompare(String(a.tanggalKeputusan || '')) || (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 8)
    .map((k) => ({ id: String(k.id), nama: kqNama(k), kg: k.totalKg || 0, tanggal: k.tanggal || '', tanggalKeputusan: k.tanggalKeputusan || '', tindakan: k.statusTindakan, label: LABEL_TINDAKAN[k.statusTindakan] || k.statusTindakan, catatan: k.catatanKeputusan || '' }));
}
/** Susun dokumen keputusan. alasan wajib untuk layak jual; yakin = tindakan yang sudah dijawab "ya" (buang / balik / layak jual saat ada opname sesudah retur). */
export function susunPutusKarantina(id, tindakan, alasan, w, yakin) {
  const k = ambilKarantina().find((x) => String(x.id) === String(id)) || null;
  const sebab = kqPeriksa(k, tindakan, w); if (sebab) return { tolak: sebab };
  const nama = kqNama(k); const status = { koleksi: 'karantina', data: Object.assign({}, k, { statusTindakan: tindakan, tanggalKeputusan: w.tanggal }) };
  if (tindakan === 'layak_jual') {
    const r = kqRetur(k.id);
    if (r.kondisi === 'utuh') { status.data.catatanKeputusan = 'kartu menyusul sesudah koreksi'; return { dokumen: [status], patch: { kabar: 'Kartu ' + nama + ' ditutup "ternyata layak jual" — returnya SUDAH tercatat kembali ke stok, stok tidak bertambah lagi.', kabarAwas: false } }; }
    if (kqKosong(alasan)) return { tolak: 'Koreksi layak jual butuh alasan (wajib) — supaya jejaknya bisa dibaca nanti' };
    const opname = k.jenisAsal !== 'kemasan' ? ambilPenyesuaianStok().filter((x) => x.merk === k.merkSumber && !x.dariRework && kqSesudah(r)(x)) : ambilPenyesuaianKemasan().filter((x) => kunciKemasan(x.namaProduk, x.ukuranKemasan) === kunciKemasan(k.namaProduk, k.ukuranKemasan) && kqSesudah(r)(x));
    if (opname.length && yakin !== 'layak_jual') return { tolak: 'Sesudah retur ini ada COCOKKAN ' + nama + ' (' + opname.map((x) => (x.tanggal || '') + (x.jam ? ' ' + x.jam : '')).join(', ') + '). Kalau hitungan itu MENIMBANG barang retur ini, stok & labanya sudah naik lewat cocokkan — koreksi ini menaikkannya dua kali. Ketuk sekali lagi hanya kalau barang ini disimpan terpisah dan tidak ikut dihitung', perluYakin: 'layak_jual' };
    const dokR = { koleksi: 'retur', data: Object.assign({}, r, { kondisi: 'utuh', koreksiKondisi: { dari: r.kondisi || null, pada: w.kini, alasan: String(alasan).trim(), oleh: 'Owner' } }) };
    status.data.catatanKeputusan = String(alasan).trim();
    return { dokumen: [dokR, status], patch: { kabar: 'Dikoreksi layak jual: ' + kqAkibat(k, 'layak_jual') + ' (' + String(alasan).trim() + ')', kabarAwas: false } };
  }
  if (tindakan === 'dirework') {
    const dokumen = [];
    if (k.jenisAsal === 'kemasan') { const kKem = kunciKemasan(k.namaProduk, k.ukuranKemasan); const hpp = (hitungStokKemasan()[kKem] || {}).hppRataRataPerUnit || 0;
      dokumen.push({ koleksi: 'produksiKemasan', data: { id: w.idUnik(), tanggal: w.tanggal, merkSumber: null, kgDipakai: 0, namaProduk: k.namaProduk, ukuranKemasan: k.ukuranKemasan, jumlahUnit: Math.round((k.totalKg || 0) / Number(k.ukuranKemasan)), biayaKemasan: 0, upahRepacking: 0, hppSumberPerKgDipakai: 0, hppPerUnit: hpp, catatan: 'Hasil rework dari karantina (retur id ' + k.id + ')' } }); }
    else dokumen.push({ koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: k.merkSumber, kgSistem: null, kgFisik: null, selisihKg: k.totalKg || 0, alasan: 'Rework dari karantina (retur id ' + k.id + ')', nilaiRp: 0, hppPerKgSaatOpname: 0, dariRework: true } });
    if (!kqKosong(alasan)) status.data.catatanKeputusan = String(alasan).trim();
    dokumen.push(status);   // barangnya dulu, statusnya belakangan — satu writeBatch, tidak ada yang tertinggal separuh
    return { dokumen, patch: { kabar: 'Rework tercatat: ' + kqAkibat(k, 'dirework') + '. Kartu karantina ditutup.', kabarAwas: false } };
  }
  if (yakin !== tindakan) return { tolak: (tindakan === 'dibuang' ? 'Buang ' + nama + '? ' : 'Balik ' + nama + ' ke pemasok? ') + kqAkibat(k, tindakan) + ' Ketuk sekali lagi', perluYakin: tindakan };
  if (!kqKosong(alasan)) status.data.catatanKeputusan = String(alasan).trim();
  return { dokumen: [status], patch: { kabar: nama + ' ' + (tindakan === 'dibuang' ? 'dibuang' : 'dikembalikan ke pemasok') + ' — antrean karantina berkurang satu; laba & kas tidak berubah (kerugiannya sudah tercatat saat retur).', kabarAwas: false } };
}
