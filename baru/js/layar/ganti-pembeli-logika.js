// GANTI PEMBELI SATU NOTA (owner 24 Nov 2026: "Gua ada salah catat" — satu nota tercatat atas nama orang yang salah). Logika tanpa DOM & tanpa Firebase;
// awalan gp. Owner saja (layar memeriksa akunnya). Hapus nama yang salah ketik SUDAH ADA di kartu pelanggan (pelanggan-logika susunHapusNama) — ini untuk
// nota yang namanya benar-benar orang lain.
//
// Yang ditulis ulang: baris penjualan nota itu (namaPelanggan baru + jejak namaSebelum / gantiPembeliPada / gantiPembeliAlasan) dan pelunasan saat beli nota itu
// (piutangMutasi bayarSaatBeli). Mesin piutang membaca nama di baris-baris itu, jadi bon nota itu ikut pindah. Rupiah, harga, stok, dan uang TIDAK berubah
// (harga tingkat pelanggan lama tidak dihitung ulang — disebut). Tutup hari tidak tersentuh (uangnya sama).
// DITOLAK dengan sebabnya: nota tidak berlaku / sebagian batal · bulan terkunci · tahun yang sudah ditutup buku · barangnya sudah diretur · nota tukar ·
// nota pesanan · nota bersurat jalan · nota bon tanpa nama baru · bon pembeli lama yang sudah dibayar lewat pelunasan terpisah (sisanya jadi minus).
import { ambilRetur, ambilPesanan, tolakKunci, tolakBukuDitutup, cacheMentah } from '../data/toko.js';
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { RP, tanggalPendek, LEBIH_AMBANG } from '../inti/format.js';
import { notaDari, bayarSaatBeli } from './struk-logika.js';
import { ajUntukNota } from './antar-logika.js';

export const GP_ALASAN = [['salah', 'Salah orang'], ['ketik', 'Salah ketik nama']];
const gpBersih = (nm) => String(nm || '').replace(/\s+/g, ' ').trim().slice(0, 60);

/** Periksa ganti pembeli nota `kunci` ({ trxId, grupNota, id }) ke `namaBaru` ('' = tanpa nama, hanya nota lunas). → { tolak } | { nota, lama, baru, akibat, bb, bonPindah } */
export function gpPeriksa(kunci, namaBaru) {
  const nota = notaDari(kunci || {}); if (!nota) return { tolak: 'Nota ini tidak ada di data perangkat ini' };
  const rows = nota.baris; const hidup = rows.filter(penjualanMasihBerlaku);
  if (!hidup.length || hidup.length !== rows.length) return { tolak: 'Nota ini sudah dibatalkan / dirinci (seluruhnya atau sebagian) — pembelinya tidak diganti dari sini' };
  const kunciBulan = rows.map((p) => tolakKunci('penjualan', p, 'nota di bulan itu tidak diubah lagi') || tolakBukuDitutup(p, 'notanya tidak diubah lagi')).find(Boolean); if (kunciBulan) return { tolak: kunciBulan };
  const lama = gpBersih(nota.nama); const baru = gpBersih(namaBaru);
  // nama yang persis sama ditolak; beda huruf besar / spasi saja BOLEH (membetulkan ejaan nama di nota itu)
  if (lama === baru) return { tolak: baru ? 'Nama pembelinya sudah "' + baru + '"' : 'Nota ini memang tanpa nama' };
  const ids = rows.map((p) => String(p.id)); const trxId = String(nota.trxId || nota.grupNota || nota.id);
  if ((ambilRetur() || []).some((r) => ids.indexOf(String(r.notaAsalId)) >= 0)) return { tolak: 'Barang dari nota ini sudah diretur — pembelinya tidak diganti dari sini (retur & bonnya ikut nama lama). Kalau salah orang, catat ulang lewat batal nota + nota baru.' };
  if (rows.some((p) => p.tukarReturId)) return { tolak: 'Nota tukar (pengganti retur) — pembelinya tidak diganti dari sini' };
  if ((ambilPesanan() || []).some((ps) => ps && String(ps.trxIdJual || '') === trxId) || rows.some((p) => p.pesananId)) return { tolak: 'Nota ini jadi dari pesanan — ganti nama pemesannya di pesanan, jangan di notanya saja' };
  if (ajUntukNota(trxId).length || rows.some((p) => p.noSJ)) return { tolak: 'Nota ini punya surat jalan — pembelinya tidak diganti dari sini (surat jalannya sudah tertulis nama lama)' };
  const bb = bayarSaatBeli(nota); const bon = nota.cara === 'Kredit' ? Math.max(0, nota.total - (bb ? bb.nominal : 0)) : 0;
  if (nota.cara === 'Kredit' && !baru) return { tolak: 'Nota bon wajib punya nama pembeli — tulis nama yang benar' };
  if (bon > 0 && lama) {
    const r = hitungPiutang().find((x) => x.kunci === kunciPelanggan(lama)); const sisa = r ? Number(r.sisa) || 0 : 0;
    if (sisa - bon < LEBIH_AMBANG) return { tolak: 'Bon ' + lama + ' tinggal ' + RP(Math.max(0, sisa)) + ' — nota ini (' + RP(bon) + ' bon) sudah ikut dibayar lewat pelunasan terpisah. Memindahkannya membuat bon ' + lama + ' minus. Betulkan pembayarannya dulu (Pelanggan › Bon).' };
  }
  const akibat = ['Nota ' + RP(nota.total) + ' (' + tanggalPendek(nota.tanggal) + (nota.jam ? ' ' + nota.jam : '') + ', ' + rows.length + ' baris) jadi atas nama ' + (baru ? '"' + baru + '"' : 'TANPA NAMA') + ' — dulu ' + (lama ? '"' + lama + '"' : 'tanpa nama') + '; nama lama disimpan di nota'];
  if (bon > 0) akibat.push('Bon ' + RP(bon) + ' ikut pindah: ' + (lama ? 'bon ' + lama + ' turun' : '') + (lama && baru ? ', ' : '') + (baru ? 'bon ' + baru + ' naik' : ''));
  if (bb) akibat.push('Pelunasan saat beli ' + RP(bb.nominal) + ' ikut pindah nama');
  if (rows.some((p) => p.hargaEceranSatuan !== undefined && p.hargaAsliSatuan !== undefined && Number(p.hargaEceranSatuan) !== Number(p.hargaAsliSatuan))) akibat.push('Harga di nota tetap (harga tingkat pembeli lama tidak dihitung ulang)');
  if (rows.some((p) => p.noFaktur)) akibat.push('Nomor faktur ' + rows.find((p) => p.noFaktur).noFaktur + ' tetap');
  akibat.push('Rupiah, stok, uang laci, dan tutup hari tidak berubah');
  return { nota, lama, baru, akibat, bb, bon, ids };
}

/** Susun ganti pembeli. alasan wajib (≥ 3 huruf). → { tolak } | { dokumen, patch } */
export function gpSusun(kunci, namaBaru, alasan, w) {
  const a = String(alasan || '').trim(); if (a.length < 3) return { tolak: 'Tulis alasannya dulu (mis. salah orang)' };
  const P = gpPeriksa(kunci, namaBaru); if (P.tolak) return P;
  const kini = (w && w.kini) || new Date().toISOString(); const jejak = { gantiPembeliPada: kini, gantiPembeliAlasan: a.slice(0, 100) };
  const dokumen = P.nota.baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { namaPelanggan: P.baru, namaSebelum: String(p.namaPelanggan || '') }, jejak) }));
  if (P.bb) { const m = (cacheMentah('piutang') || []).find((x) => String(x.id) === String(P.bb.id)); if (m) dokumen.push({ koleksi: 'piutangMutasi', data: Object.assign({}, m, { namaPelanggan: P.baru, namaSebelum: String(m.namaPelanggan || '') }, jejak) }); }
  return { dokumen, patch: { kabar: 'Pembeli nota ' + RP(P.nota.total) + ' (' + tanggalPendek(P.nota.tanggal) + ') diganti: ' + (P.lama || 'tanpa nama') + ' → ' + (P.baru || 'tanpa nama') + (P.bon > 0 ? ' · bon ' + RP(P.bon) + ' ikut pindah' : '') + '. Rupiah tidak berubah.', kabarAwas: false, gpBuka: null, rwBuka: null } };
}
