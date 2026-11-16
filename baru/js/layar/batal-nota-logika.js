// BATAL NOTA DARI RIWAYAT (owner 17 Nov 2026, butir 2: "bisa batal transaksi di sistem utama mode owner karena salah catat / uji coba") — logika tanpa DOM, awalan bn.
// Dulu hanya "Batalkan nota barusan" 90 detik (jual-logika susunPembatalan) yang tautannya (pelunasan saat beli, pesanan, retur tukar) masih di memori.
// Di sini tautan itu DISUSUN ULANG DARI DATA lalu diserahkan ke susunPembatalan yang SAMA — satu jalur pembatalan untuk 90 detik maupun Riwayat:
//   baris ditandai dibatalkan (tidak dihapus) · kantong literan / wadah id+1 dicabut · pemecah ½ karung dicabut · pelunasan saat beli dicabut ·
//   pesanan kembali ke status sebelum dibayar · retur tukar yang LAHIR BERSAMA nota ini (+ karantinanya) dicabut.
// Karcis kasir darurat → susunBatalKarcis (karcis-logika); nota hasil rinci / rapikan → tarik balik susunUrungRinci. Owner saja (layar memeriksa akunnya).
// DITOLAK dengan sebabnya: nota sudah tidak berlaku · bulan terkunci (tolakKunci) · barang nota ini sudah diretur · retur bon (tolakBatalReturBon) ·
// nota bon yang membuat sisa bon orangnya minus (bon itu sudah dibayar).
// HARI YANG SUDAH DITUTUP: uang tunai nota ini ikut "laci seharusnya" malam itu. Membatalkannya = laci seharusnya turun sebesar uang tunainya, jadi selisih
// malam itu NAIK sebesar itu (fisik − seharusnya). Tanpa ini laba kena dua kali: margin nota hilang DAN "kurang kas" malam itu tetap (uji coba yang tak pernah
// dibayar dulu tampil sebagai kurang kas). Yang dibetulkan = penutupan PERTAMA yang jamnya ≥ jam nota (tutup ulang menyimpan penutupan lama di riwayat,
// tiap penutupan memasang titik kas sendiri — ugLebihKurangKas menjumlah selisih semuanya). Nota yang dicatat sesudah penutupan terakhir hari itu tidak
// menyentuh penutupan mana pun. Titik kas tidak berubah (hitungan fisik tetap). QRIS: rekening hitungan sistem tidak dihitung ulang — disebut.
import { ambilPenjualanSemua, ambilRetur, ambilKarantina, ambilPesanan, ambilTutupHari, tolakKunci } from '../data/toko.js';
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { RP, tanggalPendek, LEBIH_AMBANG } from '../inti/format.js';
import { susunPembatalan } from './jual-logika.js';
import { notaDari, bayarSaatBeli } from './struk-logika.js';
import { kcDariDarurat, susunBatalKarcis, susunUrungRinci } from './karcis-logika.js';
import { tolakBatalReturBon } from './retur-logika.js';

export const BN_ALASAN = [['salah', 'Salah catat'], ['uji', 'Uji coba']];
const BN_TERKUNCI = 'nota di bulan itu tidak bisa dibatalkan lagi — barang yang kembali dicatat sebagai retur hari ini';
const bnJam = (j) => String(j || '').slice(0, 5);

/** Status penutupan hari nota: penutupan yang memuat nota ini (atau null) + uang tunai yang ikut laci seharusnya malam itu. */
function bnTutup(nota, tunai) {
  const td = ambilTutupHari().find((t) => t && t.tanggal === nota.tanggal); if (!td) return null;
  const urut = (Array.isArray(td.riwayat) ? td.riwayat.map((x, i) => ({ dok: x, i })) : []).concat([{ dok: td, i: -1 }]).sort((a, b) => bnJam(a.dok.jam).localeCompare(bnJam(b.dok.jam)));
  const kena = urut.find((x) => bnJam(x.dok.jam) >= bnJam(nota.jam)) || null;
  const angka = kena && typeof kena.dok.selisih === 'number' ? kena.dok.selisih : kena && typeof kena.dok.selisihLaci === 'number' ? kena.dok.selisihLaci : null;
  return { td, kena, tunai, selisihLama: angka, selisihBaru: angka === null ? null : angka + tunai };
}
/** Dokumen tutupHari sesudah dibetulkan (selisih naik, laci seharusnya turun sebesar uang tunai nota) — jejaknya di koreksiBatalNota. */
function bnDokTutup(T, trxId, kini) {
  const geser = (x) => { const d = Object.assign({}, x); ['selisih', 'selisihLaci'].forEach((k) => { if (typeof d[k] === 'number') d[k] = d[k] + T.tunai; }); if (typeof d.kasSeharusnya === 'number') d.kasSeharusnya = d.kasSeharusnya - T.tunai; return d; };
  let d = Object.assign({}, T.td);
  if (T.kena.i < 0) d = geser(d); else d.riwayat = d.riwayat.map((x, i) => (i === T.kena.i ? geser(x) : x));
  d.koreksiBatalNota = (Array.isArray(T.td.koreksiBatalNota) ? T.td.koreksiBatalNota : []).concat([{ trxId: String(trxId), tunai: T.tunai, jamTutup: bnJam(T.kena.dok.jam), pada: kini }]);
  return { koleksi: 'tutupHari', data: d };
}

/**
 * Periksa satu nota Riwayat sebelum dibatalkan. kunci = { trxId, grupNota, id } (baris Riwayat).
 * Hasil: { tolak } | { jalur: 'nota'|'karcis'|'rinci', nota, akibat: [kalimat], tautan (jalur nota), tutup (penutupan yang dibetulkan / null), rinci, karcisId }.
 */
export function bnPeriksa(kunci) {
  const nota = notaDari(kunci || {}); if (!nota) return { tolak: 'Nota ini tidak ada di data perangkat ini' };
  const rows = nota.baris; const hidup = rows.filter(penjualanMasihBerlaku);
  if (!hidup.length) return { tolak: 'Nota ini sudah ' + (rows.some((x) => x.dibatalkan) ? 'dibatalkan' : 'dirinci jadi nota lain') + ' — tidak ada yang bisa dibatalkan lagi' };
  if (hidup.length !== rows.length) return { tolak: 'Sebagian baris nota ini sudah dibatalkan / dikoreksi — bereskan lewat jalurnya masing-masing, supaya tidak dobel' };
  const kunciBulan = rows.map((p) => tolakKunci('penjualan', p, BN_TERKUNCI)).find(Boolean); if (kunciBulan) return { tolak: kunciBulan };
  // rinci / rapikan karcis → tarik balik (karcis kembali ke antrean)
  const rinci = rows.find((p) => p.asalDarurat || p.rinciDari || (p.koreksiDari && p.grupNota));
  if (rinci) return { jalur: 'rinci', nota, rinci: { grupNota: String(rinci.grupNota), asliId: String(rinci.rinciDari || rinci.koreksiDari) },
    akibat: ['Rincian ini ditarik balik: ' + rows.length + ' baris ditandai dibatalkan, karcis asalnya kembali ke antrean (bisa dibatalkan juga dari sana)'] };
  if (rows.length === 1 && kcDariDarurat(rows[0])) return { jalur: 'karcis', nota, karcisId: String(rows[0].id),
    akibat: ['Karcis kasir darurat ' + RP(nota.total) + ' ditandai dibatalkan (tidak dihapus)', 'Omzet ' + tanggalPendek(nota.tanggal) + ' turun ' + RP(nota.total)] };
  // nota biasa
  const ids = rows.map((p) => String(p.id));
  const tolakRb = tolakBatalReturBon(ids); if (tolakRb) return { tolak: tolakRb };
  const sudahRetur = (ambilRetur() || []).filter((r) => ids.indexOf(String(r.notaAsalId)) >= 0);
  if (sudahRetur.length) return { tolak: 'Barang dari nota ini sudah diretur ' + tanggalPendek(sudahRetur[0].tanggal) + ' (' + RP(sudahRetur.reduce((a, r) => a + (Number(r.nominalRefund) || 0), 0)) + ') — membatalkannya membuat barang itu tercatat kembali dua kali. Kalau notanya memang salah, catat sisanya lewat retur.' };
  const trxId = nota.trxId || nota.grupNota || nota.id;
  const bb = bayarSaatBeli(nota);
  const terima = (cara) => (nota.cara === cara ? nota.total : bb && bb.cara === cara ? bb.nominal : 0);
  const tunai = terima('Tunai'); const qris = terima('QRIS');
  // retur tukar yang lahir BERSAMA nota ini (tukarModel kreditBarangGabung, penggantinya nota ini) ikut dicabut; susulan untuk retur lama tidak
  const tkId = rows.map((p) => p.tukarReturId).filter(Boolean)[0] || null; const rT = tkId ? (ambilRetur() || []).find((r) => String(r.id) === String(tkId)) : null;
  const returLahir = rT && rT.tukarModel === 'kreditBarangGabung' && String(rT.penjualanPenggantiTrxId) === String(trxId) ? rT : null;
  const pesanan = (ambilPesanan() || []).find((ps) => ps && ps.status === 'dibayar' && String(ps.trxIdJual || '') === String(trxId)) || null;
  const statusSebelum = (() => { if (!pesanan) return null; const r = (pesanan.riwayatStatus || []).map((x) => x && x.status).filter(Boolean); for (let i = r.length - 1; i >= 0; i--) if (r[i] !== 'dibayar') return r[i]; return 'diantar'; })();
  // bon: membatalkan nota bon yang sudah dibayar membuat sisa bon orangnya minus — ditolak
  const bonBerkurang = nota.cara === 'Kredit' ? nota.total - (bb ? bb.nominal : 0) : 0;
  if (bonBerkurang > 0 && nota.nama) {
    const r = hitungPiutang().find((x) => x.kunci === kunciPelanggan(nota.nama)); const sisa = r ? r.sisa : 0;
    if (sisa - bonBerkurang < LEBIH_AMBANG) return { tolak: 'Bon ' + nota.nama + ' tinggal ' + RP(Math.max(0, sisa)) + ' — nota ini (' + RP(bonBerkurang) + ' bon) sudah ikut dibayar. Membatalkannya membuat bon ' + nota.nama + ' minus seolah toko memegang uangnya. Kalau barangnya kembali, catat lewat retur.' };
  }
  const T = tunai > 0 ? bnTutup(nota, tunai) : null;
  if (T && T.kena && returLahir) return { tolak: 'Nota tukar di hari yang sudah ditutup (' + tanggalPendek(nota.tanggal) + ') tidak bisa dibatalkan dari sini — selisih laci malam itu tidak bisa dihitung ulang dengan aman. Catat retur hari ini.' };
  const akibat = [rows.length + ' baris ditandai dibatalkan (tidak dihapus) · stok barangnya kembali', 'Omzet ' + tanggalPendek(nota.tanggal) + ' turun ' + RP(nota.total)];
  if (tunai > 0) akibat.push('Uang laci yang seharusnya ' + tanggalPendek(nota.tanggal) + ' turun ' + RP(tunai));
  if (qris > 0) akibat.push('Uang QRIS ' + tanggalPendek(nota.tanggal) + ' turun ' + RP(qris) + (ambilTutupHari().some((t) => t && t.tanggal === nota.tanggal) ? ' · isi rekening hitungan sistem tidak dihitung ulang — samakan lewat Uang › Catat isi rekening kalau perlu' : ''));
  if (bonBerkurang > 0) akibat.push('Bon ' + (nota.nama || 'pembeli') + ' berkurang ' + RP(bonBerkurang));
  if (bb) akibat.push('Pelunasan saat beli ' + RP(bb.nominal) + ' ikut dicabut');
  if (pesanan) akibat.push('Pesanan ' + (pesanan.namaPelanggan || '') + ' kembali ke ' + statusSebelum);
  if (returLahir) akibat.push('Retur tukar yang dicatat bersama nota ini ikut dicabut');
  if (tkId && !returLahir) akibat.push('Retur lama yang penggantinya nota ini kembali menunggu pengganti');
  if (T && T.kena) akibat.push('Hari ' + tanggalPendek(nota.tanggal) + ' sudah ditutup jam ' + bnJam(T.kena.dok.jam) + ': ' + (T.selisihLama === null ? 'selisih laci malam itu memang tidak bisa dihitung — tidak diubah' : 'selisih laci malam itu dibetulkan ' + (T.selisihLama < 0 ? 'kurang ' : T.selisihLama > 0 ? 'lebih ' : '') + RP(Math.abs(T.selisihLama)) + ' → ' + (T.selisihBaru < 0 ? 'kurang ' : T.selisihBaru > 0 ? 'lebih ' : 'pas ') + (T.selisihBaru ? RP(Math.abs(T.selisihBaru)) : '')));
  else if (T && !T.kena) akibat.push('Hari ' + tanggalPendek(nota.tanggal) + ' ditutup sebelum nota ini dicatat — penutupan malam itu tidak tersentuh');
  return { jalur: 'nota', nota, akibat, tutup: T && T.kena && T.selisihLama !== null ? T : null,
    tautan: { trxId, idPenjualan: ids, piutangId: bb ? bb.id : null, pesanan: pesanan ? { id: String(pesanan.id), statusSebelum } : null,
      retur: returLahir ? { id: String(returLahir.id), karantina: (ambilKarantina() || []).some((k) => String(k.id) === String(returLahir.id)) } : null } };
}

/** Susun pembatalan. alasan wajib (≥ 3 huruf). Hasil: { tolak } | { jalur, dokumen, hapus, kelompok?, patch }. */
export function bnSusun(kunci, alasan, w) {
  const a = String(alasan || '').trim(); if (a.length < 3) return { tolak: 'Tulis alasannya dulu (mis. salah catat, uji coba)' };
  const P = bnPeriksa(kunci); if (P.tolak) return { tolak: P.tolak };
  const kini = (w && w.kini) || new Date().toISOString(); const n = P.nota; const label = (n.nama || 'tanpa nama') + ' ' + RP(n.total) + ' (' + tanggalPendek(n.tanggal) + (n.jam ? ' ' + n.jam : '') + ')';
  if (P.jalur === 'rinci') { const r = susunUrungRinci(P.rinci, w); return r.tolak ? r : Object.assign({}, r, { jalur: 'rinci' }); }
  if (P.jalur === 'karcis') { const r = susunBatalKarcis(P.karcisId, a, w); return r.tolak ? r : Object.assign({}, r, { jalur: 'karcis' }); }
  const r = susunPembatalan(P.tautan, 'Dibatalkan owner dari Riwayat: ' + a.slice(0, 100), w); if (!r) return { tolak: 'Tidak ada baris yang bisa dibatalkan' }; if (r.tolak) return r;
  const dokumen = r.dokumen.slice(); if (P.tutup) dokumen.push(bnDokTutup(P.tutup, P.tautan.trxId, kini));
  return { jalur: 'nota', dokumen, hapus: r.hapus, patch: { kabar: 'Nota ' + label + ' dibatalkan — ' + P.akibat.slice(1).join(' · '), kabarAwas: false, bnBuka: null, rwBuka: null } };
}
