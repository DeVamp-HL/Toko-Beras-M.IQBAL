// HALAMAN PELANGGAN — SATU halaman per orang (paket P7, owner 27 Nov 2026; sensus ulang 27 Nov B18). Logika tanpa DOM, BACA SAJA, nama berawalan hn (bundel uji
// jsc satu lingkup). Dijaga alat-uji/uji_pelanggan_het_p7.py.
//
// Dulu tersebar: kartu bon per orang (Pelanggan › Bon), kartu piutang & faktur (Usaha), laba per orang (Laporan › Laba › Per pelanggan). Sekarang satu bagian di atas
// kartu orang itu (Pelanggan › Kenali › ketuk namanya; tombol "halaman pelanggan" di lembar bon): nota terakhir · belanja per bulan (12 bulan) & per tahun · pesanan
// & jadwal rutin yang masih terbuka · bon (sisa, nota terbuka & jatuh tempo, kebiasaan bayar, batas yang berlaku, stop/henti) · laba kotor dari orang itu.
// Keputusan owner 27 Nov 2026: OWNER melihat lengkap; STAF (Ben & karyawan) melihat semuanya KECUALI laba & modal — hnHalaman(…, { laba: false }) tidak
// mengembalikan angka laba sama sekali (bukan cuma disembunyikan di layar). Semua koleksi yang dibaca memang terbaca staf (penjualan, pesanan, orderRutin,
// piutangMutasi, pelangganCatatan, aturanToko/pelanggan); setelan HET/laba owner tidak disentuh.
// TIDAK ADA RUMUS BARU: belanja & laba per bulan = pgOrangBulan (aturan pelangganBulan Laporan, diuji sama per bulan), bon = semuaBon / pnNota / pnKebiasaanBayar
// (buku bon mesin), batas = fkInfoKredit, pesanan = pesananBelumTuntas (mesin) + poUangMuka. Tahun yang sudah tutup buku: belanja tahunannya dari ringkasan tutup
// buku (ringkasArsip pelanggan.tahun — Σ nota, tanpa potongan retur; disebut).
import { kunciPelanggan, pesananBelumTuntas, namaSingkatTrx } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPesanan, kunciNota, ringkasArsip } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { pgOrangBulan } from './laba-pelanggan-logika.js';
import { fkInfoKredit, fkSumberBatas, fkStopBon, fkHentiBon, fkTerbukaOrang } from './faktur-logika.js';
import { semuaBon, pnNota, pnKebiasaanBayar } from './bon-logika.js';
import { poUangMuka, poJadwalSemua, poKataJadwal, poIsiTeks } from './pesanan-logika.js';

export const HN_NOTA = 5;
export const HN_BULAN = 12;
const hnCara = (c) => { const k = String(c || '').toLowerCase(); return k === 'kredit' ? 'bon' : k === 'qris' ? 'QRIS' : k === 'transfer' ? 'transfer' : 'tunai'; };
const hnJumlah = (daftar, f) => daftar.reduce((a, x) => a + (Number(x[f]) || 0), 0);

/** Nota orang ini, terbaru dulu (satu nota = grupNota / trxId). → { nota: [{ kunci, tanggal, jam, isi, total, cara, faktur, nBaris }], n, pertama, terakhir }. */
export function hnNota(kunci, n) {
  const g = {}; ambilPenjualan().forEach((p) => { if (!kunci || kunciPelanggan(p.namaPelanggan) !== kunci) return; const k = kunciNota(p);
    const x = g[k] || (g[k] = { kunci: k, tanggal: String(p.tanggal || ''), jam: String(p.jam || ''), isi: [], total: 0, cara: hnCara(p.caraBayar), faktur: String(p.noFaktur || ''), nBaris: 0, id: Number(p.id) || 0 });
    x.isi.push(namaSingkatTrx(p)); x.total += Number(p.hargaTotal) || 0; x.nBaris += 1; if ((Number(p.id) || 0) > x.id) x.id = Number(p.id) || 0; if (p.noFaktur) x.faktur = String(p.noFaktur); });
  const semua = Object.keys(g).map((k) => g[k]).sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam) || b.id - a.id);
  return { nota: semua.slice(0, n || HN_NOTA), n: semua.length, pertama: semua.length ? semua[semua.length - 1].tanggal : '', terakhir: semua.length ? semua[0].tanggal : '' };
}

/**
 * Halaman satu orang. opsi.laba = true hanya untuk owner.
 * → { kunci, nama, nota, bulan [12 bulan pgOrangBulan], tahun [{ tahun, omzet, sumber 'nota' | 'arsip' }], belanja12 { omzet, kg, nNota }, pesanan [...], rutin [...],
 *     bon { sisa, status, ket, nNota, lewat, jatuhTerdekat, kebiasaan, batas, sumberBatas, henti, stop, faktur }, laba (owner saja) { bulan1, bulan3, bulan12 } }.
 */
export function hnHalaman(kini, kunci, nama, opsi) {
  const o = opsi || {}; const iso = hariIniIso(kini); const k = String(kunci || ''); const nm = String(nama || k);
  const N = hnNota(k, HN_NOTA);
  // 12 bulan untuk grafik + bulan tahun lalu untuk "per tahun" (paling banyak 24 bulan, satu hitungan)
  const bulanIni = Number(iso.slice(5, 7)); const nBulan = Math.max(HN_BULAN, Math.min(24, 12 + bulanIni));
  const semuaBulan = pgOrangBulan(k, kini, nBulan); const bulan = semuaBulan.slice(-HN_BULAN);
  const tahunIni = Number(iso.slice(0, 4)); const arsip = ringkasArsip(); const ra = arsip && arsip.pelanggan ? arsip.pelanggan[k] : null;
  const tahun = [tahunIni, tahunIni - 1].map((th) => { const bl = semuaBulan.filter((b) => Number(b.key.slice(0, 4)) === th); const hidup = bl.filter((b) => !b.diarsip);
    const lengkapHidup = th === tahunIni || bl.length === 12;
    if (bl.length && hidup.length === bl.length && lengkapHidup) return { tahun: th, omzet: hnJumlah(hidup, 'omzet'), kg: hnJumlah(hidup, 'kg'), nNota: hnJumlah(hidup, 'nNota'), sumber: 'nota' };
    const dariArsip = ra && ra.tahun && ra.tahun[String(th)] !== undefined ? Number(ra.tahun[String(th)]) || 0 : null;
    if (dariArsip !== null) return { tahun: th, omzet: dariArsip, kg: null, nNota: null, sumber: 'arsip' };
    return hidup.length ? { tahun: th, omzet: hnJumlah(hidup, 'omzet'), kg: hnJumlah(hidup, 'kg'), nNota: hnJumlah(hidup, 'nNota'), sumber: 'sebagian' } : { tahun: th, omzet: 0, kg: 0, nNota: 0, sumber: 'kosong' }; });
  const hidup12 = bulan.filter((b) => !b.diarsip);
  const belanja12 = { omzet: hnJumlah(hidup12, 'omzet'), kg: hnJumlah(hidup12, 'kg'), nNota: hnJumlah(hidup12, 'nNota'), nBulanAda: hidup12.filter((b) => b.nNota > 0).length };
  // pesanan & jadwal rutin yang masih terbuka
  const pesanan = (ambilPesanan() || []).filter((p) => kunciPelanggan(p.namaPelanggan) === k && pesananBelumTuntas(p)).map((p) => ({ id: String(p.id), tanggal: String(p.tanggal || ''),
    kirim: String(p.tanggalKirim || ''), status: String(p.status || 'dipesan'), isi: String(p.isi || '').trim() || poIsiTeks(p.baris), nilai: Math.round(Number(p.nilaiPerkiraan) || 0), dp: poUangMuka(p.id).total, noPO: String(p.noPO || '') }))
    .sort((a, b) => (a.kirim || a.tanggal).localeCompare(b.kirim || b.tanggal));
  const rutin = poJadwalSemua().filter((j) => j.aktif && kunciPelanggan(j.nama) === k).map((j) => ({ id: j.id, kata: poKataJadwal(j), isi: j.isi }));
  // bon
  const B = semuaBon(kini); const b = B.find((x) => x.kunci === k) || null; const PN = pnNota(kini, B).nota.filter((x) => x.orang === k); const KB = pnKebiasaanBayar(kini)[k] || null;
  const info = fkInfoKredit(nm) || {}; const lewat = PN.filter((x) => x.status === 'lewat');
  const bon = { sisa: b ? Math.max(0, b.sisa || 0) : 0, lebih: b && b.sisa < 0 ? -b.sisa : 0, status: b ? b.status : 'lunas', ket: b ? b.ket : 'belum pernah bon', nNota: PN.length,
    nLewat: lewat.length, rpLewat: Math.round(hnJumlah(lewat, 'sisa')), jatuhTerdekat: PN.filter((x) => x.jatuhTempo).map((x) => x.jatuhTempo).sort()[0] || '',
    kebiasaan: KB && KB.n ? { n: KB.n, nTelat: KB.nTelat, rataTelat: KB.rataTelat, biasaTelat: KB.biasaTelat } : null,
    batas: Number(info.batas) > 0 ? Math.round(Number(info.batas)) : 0, sumberBatas: info.ada ? fkSumberBatas(info) : '', terdaftar: !!info.terdaftar,
    henti: fkHentiBon(nm), stop: fkStopBon(nm), faktur: fkTerbukaOrang(kini, k).map((f) => ({ no: f.no, sisa: Math.round(f.sisa), jatuhTempo: f.jatuhTempo, status: f.status })) };
  const out = { kunci: k, nama: nm, iso, nota: N, bulan, tahun, belanja12, pesanan, rutin, bon, adaLaba: !!o.laba };
  if (o.laba) {
    const jum = (n) => { const bl = bulan.slice(-n).filter((x) => !x.diarsip); const ada = bl.filter((x) => x.labaKotor !== null); return { n, omzet: hnJumlah(bl, 'omzet'), labaKotor: ada.length ? hnJumlah(ada, 'labaKotor') : null, nTanpaHpp: hnJumlah(bl, 'nTanpaHpp'), diarsip: bulan.slice(-n).some((x) => x.diarsip) }; };
    out.laba = { bulan1: jum(1), bulan3: jum(3), bulan12: jum(12) };
  } else {
    out.bulan = bulan.map((x) => ({ key: x.key, nama: x.nama, diarsip: x.diarsip, berjalan: x.berjalan, omzet: x.omzet, kg: x.kg, nNota: x.nNota }));   // staf: tanpa laba & persen untung
  }
  return out;
}
/** Kalimat ringkas di kepala halaman (layar & uji memakai yang sama). */
export function hnRingkas(H) {
  const n = H.nota; if (!n.n) return 'Belum ada nota atas nama ini.';
  return n.n + ' nota sejak ' + tanggalPendek(n.pertama) + ' · terakhir ' + tanggalPendek(n.terakhir) + ' · 12 bulan: ' + RP(Math.round(H.belanja12.omzet)) + (H.belanja12.nBulanAda ? ' (' + H.belanja12.nBulanAda + ' bulan ada belanja)' : '');
}
