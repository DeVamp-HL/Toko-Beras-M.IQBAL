// BARANG MASUK DARI TABLET (owner 22 Nov 2026, paket ③; rules v15). Logika tanpa DOM; awalan mt. Dijaga alat-uji/uji_masuk_tablet.py.
//
// Keputusan owner 22 Nov 2026 (ditanya di depan):
//  1. Kedatangan dari tablet LANGSUNG masuk stok + BON pemasok (caraBayar 'utang'). Uang yang keluar dari laci saat itu tetap TITIPAN ke owner.
//  2. HARGA per kg diketik yang jaga dari nota supir. Beda dari harga terakhir → kedatangan ditandai (hargaBeda) dan owner dikabari; owner membetulkan
//     dari HP (koreksi kedatangan seperti biasa).
//  3. PENCATAT = Penjaga laci saja (rules v15 stafCatatMasuk(['ben'])); karyawan tidak melihat tombolnya (SERVER_BUKA.kedatangan).
//  4. UPAH BONGKAR diisi di form yang sama → titipan "upah bongkar" yang menunjuk kedatangannya; disetujui owner = ditulis ke biayaBongkar kedatangan itu
//     (modal barang + kas keluar laci bertanggal datang, rumus mesin yang sama). Kedatangannya sendiri ditulis dengan biayaBongkar 0.
//  4b. ONGKOS KIRIM supir pemasok (Tahap 3, owner 26 Nov 2026: "di tablet juga adakan") → titipan berjenis 'bongkar' bertanda ongkir; disetujui owner =
//     masuk modal kedatangan itu sebagai ongkos kirim. TOLAK baris, KG DIPOTONG langsung (klaim saat datang), timbang sampel, mutu rinci & catatan bebas untuk
//     pemasok memakai hitungan yang sama dengan lembar owner (hitungMasuk) — bentuk dokumennya tetap rules v15 (kolom tambahan, bukan kolom terlarang).
//  5. BAYAR KE SUPIR → titipan "bayar bon pemasok" (nominal + pemasok + kedatangan ini); owner MEMILIH bonnya saat menyetujui (bawaan = bon kedatangan ini).
// Batas tablet (owner memutus mutu & buku): MEREK BARU dicatat (owner 22 Nov 2026: "jangan ditolak, nanti gua koreksi / hapus kedatangannya dari akun owner")
// — bukunya dibuka atas nama yang diketik, TANPA kelas (tebakan kelas tidak dipakai, peta kelas tidak ditulis), ditandai merekBaru & disebut di kabar; kelas,
// jenis beras & harga jual diatur owner dari HP. Nama yang DIARSIPKAN tetap owner (memulihkan = setelan owner). Harga beda jauh dari modal (pertanyaan
// "sama barangnya / beda mutu?") dicatat sebagai barang yang SAMA dan ikut kabar — beda mutu diputus owner.
// Satu kiriman: batchMasuk + (titipan bongkar) + (titipan bayar supir) + kabar barang masuk — semuanya bentuk rules v15, diperiksa periksaKiriman (akses.js).
import { hitungMasuk, susunSimpanMasuk, drafMasukKosong } from './stok-catat-logika.js';
import { tpSusunMinta, tpDokKabarMasuk, tpAngka } from './titipan-logika.js';
import { RP } from '../inti/format.js';

export const MT_BATAS = { pemasok: 60, baris: 20 };
const mtKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const mtKg = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';

/** Draf kosong tablet: tanggal hari ini, selalu bon, + upah bongkar & bayar ke supir (titipan). */
export function mtDrafKosong(w) { return Object.assign(drafMasukKosong(w), { caraBayar: 'utang', bongkar: '', ongkir: '', bayarSupir: '' }); }

/** Rupiah titipan dari isian (kosong = 0; bukan angka = NaN). */
const mtRp = (v) => (mtKosong(v) ? 0 : tpAngka(v));

/** Draf yang benar-benar dihitung: tanggal hari ini, bon, tanpa bongkar (bongkar = titipan), pertanyaan varian dijawab "sama barangnya". */
function mtDrafHitung(draf, w) {
  const d = JSON.parse(JSON.stringify(Object.assign(mtDrafKosong(w), draf || {})));
  d.id = null; d.tanggal = w.tanggal; d.caraBayar = 'utang'; d.bongkar = ''; d.ongkir = ''; d.alasan = ''; d.tanpaTebakKelas = true;
  (d.baris || []).forEach((b) => { b.varian = ''; b.namaMutu = ''; b.kelas = ''; b.kelasPilih = false; });
  const h0 = hitungMasuk(d);
  h0.baris.forEach((b) => { if (b.sah && b.vr && b.vr.perlu && !b.vr.arsip) d.baris[b.ke - 1].varian = 'sama'; });
  return d;
}

/** Harga beda dari harga terakhir nama itu (bahan kabar owner): [{ merk, harga, lalu, persen }]. */
export function mtHargaBeda(h) {
  return (h.sah || []).map((b) => { const lalu = Math.round((b.lalu && b.lalu.harga) || b.hargaLalu || 0);
    return lalu > 0 && Math.round(b.hargaPerKg) !== lalu ? { merk: b.merkSimpan, harga: Math.round(b.hargaPerKg), lalu, persen: Math.round((b.hargaPerKg - lalu) / lalu * 1000) / 10 } : null; })
    .filter(Boolean);
}

/** Hitungan layar tablet: hitungMasuk draf tablet + masalah khusus tablet per baris + harga beda + titipan. */
export function mtHitung(draf, w) {
  const d = mtDrafHitung(draf, w); const h = hitungMasuk(d);
  h.baris.forEach((b) => {
    if (b.terisi && !b.masalah && b.vr && b.vr.arsip) b.masalahTablet = b.merk + ' sudah DIARSIPKAN — owner yang memulihkannya dari HP';
    else b.masalahTablet = '';
    b.gabung = !!(b.sah && b.vr && b.vr.perlu && !b.vr.arsip);   // harga beda jauh dari modal → dicatat sebagai barang yang sama, owner dikabari
    b.merekBaru = !!(b.sah && b.baru);   // owner 22 Nov 2026: merek baru dicatat atas nama yang diketik, owner dikabari
  });
  const bongkar = mtRp((draf || {}).bongkar); const supir = mtRp((draf || {}).bayarSupir); const ongkir = mtRp((draf || {}).ongkir);
  return Object.assign(h, { hargaBeda: mtHargaBeda(h), bongkarTitip: bongkar, supirTitip: supir, ongkirTitip: ongkir, bermasalahTablet: h.baris.filter((b) => b.masalahTablet) });
}

/**
 * Simpan kedatangan dari tablet. akun = akun efektif (orang yang jaga; uid akun tablet); yakin = ketukan kedua (karung sedikit).
 * Hasil { dokumen, batchId, patch } atau { tolak } (+ perluYakin). TIDAK menulis apa pun sendiri.
 */
export function mtSusunSimpan(draf, akun, w, yakin) {
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — barang masuk butuh orang yang jaga' };
  const D = draf || {}; const bongkar = mtRp(D.bongkar); const supir = mtRp(D.bayarSupir); const ongkir = mtRp(D.ongkir);
  if (!(bongkar >= 0)) return { tolak: 'Upah bongkar hanya angka rupiah bulat (mis. 50000 atau 50.000), atau kosong' };
  if (!(ongkir >= 0)) return { tolak: 'Ongkos kirim hanya angka rupiah bulat, atau kosong' };
  if (!(supir >= 0)) return { tolak: 'Uang yang dibayar ke supir hanya angka rupiah bulat, atau kosong' };
  const d = mtDrafHitung(D, w); const H = mtHitung(D, w);
  if (String(d.pemasok || '').trim().length > MT_BATAS.pemasok) return { tolak: 'Nama pemasok paling panjang ' + MT_BATAS.pemasok + ' huruf' };
  if (H.bermasalahTablet.length) { const x = H.bermasalahTablet[0]; return { tolak: 'Baris ' + x.ke + ': ' + x.masalahTablet }; }
  if (H.sah.length > MT_BATAS.baris) return { tolak: 'Paling banyak ' + MT_BATAS.baris + ' baris satu kedatangan — catat sisanya sebagai kedatangan kedua' };
  const r = susunSimpanMasuk(d, w, yakin); if (r.tolak) return r;
  const lain = (r.dokumen || []).filter((x) => x.koleksi !== 'batchMasuk');
  if (lain.length) return { tolak: 'Kedatangan ini butuh keputusan owner (beda mutu / arsip) — owner yang mencatatnya dari HP' };
  const bm = Object.assign({}, r.dokumen[0].data, { dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' });
  const beda = mtHargaBeda(r.hitung); if (beda.length) bm.hargaBeda = beda;
  const gabung = r.hitung.sah.filter((b) => b.varian === 'sama' && b.vr && b.vr.perlu).map((b) => b.merkSimpan);
  if (gabung.length) bm.hargaJauh = gabung;
  const merekBaru = r.hitung.sah.filter((b) => b.baru).map((b) => b.merkSimpan).filter((m, i, a) => a.indexOf(m) === i);
  if (merekBaru.length) bm.merekBaru = merekBaru;
  const pemasok = String(bm.pemasok); const id = String(bm.id);
  const dokumen = [{ koleksi: 'batchMasuk', data: bm }];
  const titip = (jenis, n, teks, ok) => { const t = tpSusunMinta({ jenis, nominal: String(n), teks, pemasok, batchId: id, ongkir: !!ok }, akun, w); if (t.tolak) return t; dokumen.push(t.dokumen[0]); return null; };
  if (bongkar > 0) { const g = titip('bongkar', bongkar, 'Upah bongkar · ' + pemasok); if (g) return g; }
  if (ongkir > 0) { const g = titip('bongkar', ongkir, 'Ongkos kirim · ' + pemasok, true); if (g) return g; }
  if (supir > 0) { const g = titip('bayarBon', supir, 'Bayar supir · ' + pemasok); if (g) return g; }
  const h = r.hitung;
  // merek baru disebut di depan: teks kabar dipotong 500 huruf (TP_BATAS.pesan)
  const teksKabar = pemasok + ' · ' + h.karung + ' karung · ' + mtKg(h.kg) + ' · ' + RP(h.nilaiBeras) + ' (bon)'
    + (merekBaru.length ? ' · MEREK BARU: ' + merekBaru.join(', ') + ' (buku baru tanpa kelas & harga jual — atur dari HP, atau koreksi / hapus kedatangan)' : '')
    + (beda.length ? ' · harga beda dari lalu: ' + beda.map((x) => x.merk + ' ' + RP(x.harga) + ' (lalu ' + RP(x.lalu) + ')').join(', ') : '')
    + (gabung.length ? ' · beda jauh dari modal, digabung: ' + gabung.join(', ') : '')
    + (h.potongKg > 0 ? ' · DIPOTONG ' + mtKg(h.potongKg) + ' (' + RP(h.potongRp) + ') karena kurang' : '') + (h.ditolak.length ? ' · DITOLAK: ' + h.ditolak.map((b) => (b.merkKetik || b.merk) + ' ' + b.jumlahKarung + ' karung').join(', ') : '')
    + (bongkar > 0 ? ' · bongkar ' + RP(bongkar) : '') + (ongkir > 0 ? ' · ongkos kirim ' + RP(ongkir) : '') + (supir > 0 ? ' · dibayar ke supir ' + RP(supir) : '');
  dokumen.push(tpDokKabarMasuk({ batchId: id, pemasok, nominal: h.nilaiBeras, teks: teksKabar, hargaBeda: beda }, akun, w));
  const kabar = 'Barang masuk tersimpan: ' + pemasok + ' · ' + h.karung + ' karung · ' + mtKg(h.kg) + ' · ' + RP(h.nilaiBeras) + ' — jadi BON pemasok, stok langsung bertambah.'
    + (h.potongKg > 0 ? ' Sudah dipotong ' + mtKg(h.potongKg) + ' (' + RP(h.potongRp) + ') karena kurang — bon dicatat dari kg yang benar-benar datang.' : '') + (h.ditolak.length ? ' ' + h.ditolak.length + ' baris ditolak (tidak masuk stok & bon).' : '')
    + (bongkar > 0 || supir > 0 || ongkir > 0 ? ' Dititip ke owner: ' + [bongkar > 0 ? 'upah bongkar ' + RP(bongkar) : '', ongkir > 0 ? 'ongkos kirim ' + RP(ongkir) : '', supir > 0 ? 'bayar ke supir ' + RP(supir) : ''].filter(Boolean).join(' + ') + ' — laci di buku berkurang sesudah owner menyetujui.' : '')
    + (beda.length ? ' Harga beda dari harga lalu (' + beda.map((x) => x.merk).join(', ') + ') — owner dikabari.' : '')
    + (merekBaru.length ? ' Merek baru ' + merekBaru.join(', ') + ' dibuka bukunya — owner dikabari (kelas & harga jualnya diatur owner).' : '');
  return { dokumen, batchId: id, hitung: h, patch: { kabar, kabarAwas: false } };
}
