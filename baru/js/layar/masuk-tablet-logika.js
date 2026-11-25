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
// TAHAP 5 (owner 26 Nov 2026: "Adakan juga di tablet" · "Semua tentang barang masuk adakan di tablet"), TANPA rules baru:
//  6. KEMASAN JADI dari pemasok — baris `masuk: 'kemasan'` seperti lembar owner: baris kedatangan berbentuk bal + SATU dokumen produksiKemasan beli-jadi
//     (akun tablet sudah boleh membuat produksiKemasan sejak rules v3, atas namanya sendiri). Harga jualnya tetap diatur owner.
//  7. CATATAN UNTUK PEMASOK & KLAIM saat mencatat — baris kurang / lebih / tertinggal / mutu + cara klaim (status "sudah disampaikan") ikut tersimpan di
//     kedatangannya (kolom catatanPemasok & klaim; catatan saja — stok & bon tidak berubah), supaya suratnya bisa langsung dicetak dari kartu tanda terima.
//  8. POTONGAN YANG MENUNGGU — "potong di kedatangan ini" dari tablet = USUL (kolom usulPakaiPotong): bon tetap penuh, owner yang menyetujui dari HP
//     (stok-catat-logika susunSetujuPakaiPotong). Akun tablet tidak pernah menulis patokan kas atau bayar bon.
//  9. KEDATANGAN YANG SUDAH TERSIMPAN (catatan & klaim belakangan, retur ke pemasok, pembetulan, hapus) = USUL ke owner lewat kabar barang masuk yang membawa
//     kolom `usul` (mtSusunUsul; bentuk rules v15 stafKabarMasuk). Owner membukanya di Koreksi kedatangan: usul catatan / retur mengisi lembarnya, owner yang
//     menyimpan. Uang kembali, potong bon, patokan kas, dan hapus kedatangan tetap keputusan owner.
// Satu kiriman: batchMasuk + (titipan bongkar) + (titipan bayar supir) + kabar barang masuk — semuanya bentuk rules v15, diperiksa periksaKiriman (akses.js).
import { hitungMasuk, susunSimpanMasuk, drafMasukKosong, cpPeriksaBaris, cpBarisTerisi, cpKedatangan, hitungReturPemasok, KLAIM_CARA, KLAIM_STATUS, CP_JENIS, CP_MAKS } from './stok-catat-logika.js';
import { cacheMentah } from '../data/toko.js';
import { tpSusunMinta, tpDokKabarMasuk, tpAngka } from './titipan-logika.js';
import { RP, tanggalPendek } from '../inti/format.js';

// kemasan: tiap baris kemasan jadi = satu dokumen beli-jadi tambahan di kiriman yang sama (kedatangan + titipan + kabar) — dibatasi supaya kiriman tablet
// tetap jauh di bawah batas pemeriksaan server per kiriman (alat-uji/peta_akses.py mengukurnya)
export const MT_BATAS = { pemasok: 60, baris: 20, kemasan: 8 };
const mtKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const mtKg = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';

/** Draf kosong tablet: tanggal hari ini, selalu bon, + upah bongkar & bayar ke supir (titipan). */
export function mtDrafKosong(w) { return Object.assign(drafMasukKosong(w), { caraBayar: 'utang', bongkar: '', ongkir: '', bayarSupir: '', catatan: [], klaimCara: '', pakaiPotong: '' }); }

/** Rupiah titipan dari isian (kosong = 0; bukan angka = NaN). */
const mtRp = (v) => (mtKosong(v) ? 0 : tpAngka(v));

/** Draf yang benar-benar dihitung: tanggal hari ini, bon, tanpa bongkar (bongkar = titipan), pertanyaan varian dijawab "sama barangnya". */
function mtDrafHitung(draf, w) {
  const d = JSON.parse(JSON.stringify(Object.assign(mtDrafKosong(w), draf || {})));
  d.id = null; d.tanggal = w.tanggal; d.caraBayar = 'utang'; d.bongkar = ''; d.ongkir = ''; d.alasan = ''; d.tanpaTebakKelas = true;
  d.pakaiPotong = '';   // Tahap 5: dari tablet potongan yang menunggu hanya DIUSULKAN (mtSusunSimpan) — jalur owner (patokan kas + bayar bon) tidak pernah dipakai
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
  const nilai = h.nilaiBeras + h.nilaiKemasan; const usulPotong = !!(draf || {}).pakaiPotong && h.potongTunggu > 0;
  return Object.assign(h, { hargaBeda: mtHargaBeda(h), bongkarTitip: bongkar, supirTitip: supir, ongkirTitip: ongkir, bermasalahTablet: h.baris.filter((b) => b.masalahTablet), nilai, usulPotong });
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
  if (H.kemasan.length > MT_BATAS.kemasan) return { tolak: 'Paling banyak ' + MT_BATAS.kemasan + ' baris kemasan jadi satu kedatangan dari tablet — catat sisanya sebagai kedatangan kedua' };
  if (H.sah.length + H.kemasan.length > MT_BATAS.baris) return { tolak: 'Paling banyak ' + MT_BATAS.baris + ' baris satu kedatangan — catat sisanya sebagai kedatangan kedua' };
  const r = susunSimpanMasuk(d, w, yakin); if (r.tolak) return r;
  // Tahap 5: pasangan beli-jadi baris KEMASAN JADI boleh ikut (produksiKemasan beliJadi yang menunjuk kedatangan ini); dokumen lain = keputusan owner
  const idBaru = String(r.dokumen[0].data.id); const jadi = (r.dokumen || []).filter((x) => x.koleksi === 'produksiKemasan' && x.data && x.data.beliJadi === true && String(x.data.dariBatch) === idBaru);
  const lain = (r.dokumen || []).filter((x) => x.koleksi !== 'batchMasuk' && jadi.indexOf(x) < 0);
  if (lain.length) return { tolak: 'Kedatangan ini butuh keputusan owner (beda mutu / arsip) — owner yang mencatatnya dari HP' };
  const bm = Object.assign({}, r.dokumen[0].data, { dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' });
  const beda = mtHargaBeda(r.hitung); if (beda.length) bm.hargaBeda = beda;
  const gabung = r.hitung.sah.filter((b) => b.varian === 'sama' && b.vr && b.vr.perlu).map((b) => b.merkSimpan);
  if (gabung.length) bm.hargaJauh = gabung;
  const merekBaru = r.hitung.sah.filter((b) => b.baru).map((b) => b.merkSimpan).filter((m, i, a) => a.indexOf(m) === i);
  if (merekBaru.length) bm.merekBaru = merekBaru;
  const h = r.hitung; const nilai = h.nilaiBeras + h.nilaiKemasan;
  // Tahap 5: catatan untuk pemasok & klaim saat mencatat (catatan saja — stok & bon tidak berubah)
  const PB = cpPeriksaBaris(cpBarisTerisi(D.catatan)); if (PB.tolak) return { tolak: 'Catatan untuk pemasok — ' + PB.tolak };
  const cara = String(D.klaimCara || '');
  if (cara && !KLAIM_CARA.some((x) => x[0] === cara)) return { tolak: 'Cara klaim tidak dikenal' };
  if (cara && !PB.catatan.length) return { tolak: 'Klaim butuh minimal satu baris catatan (apa yang kurang, lebih, tertinggal, atau tidak sesuai)' };
  if (PB.catatan.length) bm.catatanPemasok = PB.catatan;
  if (cara) bm.klaim = { cara, status: 'diminta', nilai: cara === 'catat' ? 0 : h.timbang.nilaiKurang, nilaiDari: 'timbang', catatan: '', tanggal: w.tanggal, diubah: w.tanggal };
  // Tahap 5: potongan yang menunggu — dari tablet hanya USUL; bon tetap penuh sampai owner menyetujui
  const usul = !!D.pakaiPotong && h.potongTunggu > 0;
  if (usul && h.potongTunggu > nilai) return { tolak: 'Potongan ' + String(bm.pemasok) + ' yang menunggu ' + RP(h.potongTunggu) + ' lebih besar dari nilai barang kedatangan ini ' + RP(nilai) + ' — lepas "potong di kedatangan ini"' };
  if (usul) bm.usulPakaiPotong = { rp: h.potongTunggu, dari: h.tunggu.map((x) => ({ id: String(x.id), i: x.i, rp: x.rp, tanggal: x.tanggalDatang })) };
  const pemasok = String(bm.pemasok); const id = String(bm.id);
  const dokumen = [{ koleksi: 'batchMasuk', data: bm }].concat(jadi);
  const titip = (jenis, n, teks, ok) => { const t = tpSusunMinta({ jenis, nominal: String(n), teks, pemasok, batchId: id, ongkir: !!ok }, akun, w); if (t.tolak) return t; dokumen.push(t.dokumen[0]); return null; };
  if (bongkar > 0) { const g = titip('bongkar', bongkar, 'Upah bongkar · ' + pemasok); if (g) return g; }
  if (ongkir > 0) { const g = titip('bongkar', ongkir, 'Ongkos kirim · ' + pemasok, true); if (g) return g; }
  if (supir > 0) { const g = titip('bayarBon', supir, 'Bayar supir · ' + pemasok); if (g) return g; }
  // merek baru disebut di depan: teks kabar dipotong 500 huruf (TP_BATAS.pesan)
  const kms = h.kemasan.length ? ' + ' + h.kemasan.map((b) => b.jumlahKarung + ' kemasan ' + b.merk + ' ' + String(b.beratKarung).replace('.', ',') + ' kg').join(', ') : '';
  // Tahap 6 (owner 25 Nov 2026): stok ikut hasil timbang — kabar & kalimat menyebut kg nota dan kg yang dibukukan; bon tetap dari nota
  const ikutT = h.ikutTimbang && h.ikutTimbang.baris ? ' (nota ' + mtKg(h.ikutTimbang.kgNota) + ' → dibukukan hasil timbang)' : '';
  const teksKabar = pemasok + ' · ' + h.karung + ' karung · ' + mtKg(h.kg) + ikutT + kms + ' · ' + RP(nilai) + ' (bon)'
    + (usul ? ' · USUL: potong ' + RP(h.potongTunggu) + ' dari klaim / retur sebelumnya (bon jadi ' + RP(nilai - h.potongTunggu) + ') — setujui di Koreksi kedatangan' : '')
    + (h.kemasan.length ? ' · KEMASAN JADI masuk buku Kemasan — harga jualnya diatur owner' : '')
    + (PB.catatan.length ? ' · catatan untuk pemasok ' + PB.catatan.length + ' baris' + (cara ? ' (' + KLAIM_CARA.find((x) => x[0] === cara)[1].toLowerCase() + ')' : '') : '')
    + (merekBaru.length ? ' · MEREK BARU: ' + merekBaru.join(', ') + ' (buku baru tanpa kelas & harga jual — atur dari HP, atau koreksi / hapus kedatangan)' : '')
    + (beda.length ? ' · harga beda dari lalu: ' + beda.map((x) => x.merk + ' ' + RP(x.harga) + ' (lalu ' + RP(x.lalu) + ')').join(', ') : '')
    + (gabung.length ? ' · beda jauh dari modal, digabung: ' + gabung.join(', ') : '')
    + (h.potongKg > 0 ? ' · DIPOTONG ' + mtKg(h.potongKg) + ' (' + RP(h.potongRp) + ') karena kurang' : '') + (h.ditolak.length ? ' · DITOLAK: ' + h.ditolak.map((b) => (b.merkKetik || b.merk) + ' ' + b.jumlahKarung + ' karung').join(', ') : '')
    + (bongkar > 0 ? ' · bongkar ' + RP(bongkar) : '') + (ongkir > 0 ? ' · ongkos kirim ' + RP(ongkir) : '') + (supir > 0 ? ' · dibayar ke supir ' + RP(supir) : '');
  dokumen.push(tpDokKabarMasuk({ batchId: id, pemasok, nominal: nilai, teks: teksKabar, hargaBeda: beda }, akun, w));
  const kabar = 'Barang masuk tersimpan: ' + pemasok + ' · ' + h.karung + ' karung · ' + mtKg(h.kg) + ikutT + kms + ' · ' + RP(nilai) + ' — jadi BON pemasok (sesuai nota), stok langsung bertambah sebesar hasil timbang.'
    + (h.kemasan.length ? ' Kemasan jadi masuk buku Kemasan (dijual per kemasan); harga jualnya diatur owner.' : '')
    + (usul ? ' Potongan ' + RP(h.potongTunggu) + ' DIUSULKAN ke owner — bon dicatat penuh dulu, berkurang sesudah owner menyetujui.' : '')
    + (PB.catatan.length ? ' Catatan untuk pemasok tersimpan (' + PB.catatan.length + ' baris) — bisa dicetak dari kartu tanda terima.' : '')
    + (h.potongKg > 0 ? ' Sudah dipotong ' + mtKg(h.potongKg) + ' (' + RP(h.potongRp) + ') karena kurang — bon dicatat dari kg yang benar-benar datang.' : '') + (h.ditolak.length ? ' ' + h.ditolak.length + ' baris ditolak (tidak masuk stok & bon).' : '')
    + (bongkar > 0 || supir > 0 || ongkir > 0 ? ' Dititip ke owner: ' + [bongkar > 0 ? 'upah bongkar ' + RP(bongkar) : '', ongkir > 0 ? 'ongkos kirim ' + RP(ongkir) : '', supir > 0 ? 'bayar ke supir ' + RP(supir) : ''].filter(Boolean).join(' + ') + ' — laci di buku berkurang sesudah owner menyetujui.' : '')
    + (beda.length ? ' Harga beda dari harga lalu (' + beda.map((x) => x.merk).join(', ') + ') — owner dikabari.' : '')
    + (merekBaru.length ? ' Merek baru ' + merekBaru.join(', ') + ' dibuka bukunya — owner dikabari (kelas & harga jualnya diatur owner).' : '');
  return { dokumen, batchId: id, hitung: h, patch: { kabar, kabarAwas: false } };
}

// ---------- Tahap 5: USUL untuk kedatangan yang SUDAH tersimpan (owner yang memutuskan) ----------
export const MT_USUL = [['catatan', 'Catatan & klaim'], ['retur', 'Kembalikan ke pemasok'], ['koreksi', 'Ada yang salah catat'], ['hapus', 'Minta dihapus']];
export const MT_USUL_BATAS = { teks: 300 };
/** Draf usul kosong untuk kedatangan itu: catatan diisi yang sudah tersimpan, atau usul dari hasil timbang & cek mutu. */
export function mtUsulKosong(id, jenis) {
  const C = cpKedatangan(id); const dasar = C ? (C.catatan.length ? C.catatan : C.usul) : [];
  return { id: String(id), jenis: MT_USUL.some((x) => x[0] === jenis) ? jenis : 'catatan', baris: dasar.map((c) => ({ jenis: c.jenis, merk: c.merk, jumlah: c.jumlah ? String(c.jumlah).replace('.', ',') : '', satuan: c.satuan, ket: c.ket })),
    cara: C && C.klaim ? C.klaim.cara : '', status: C && C.klaim ? C.klaim.status : 'diminta', bebas: C ? C.bebas : '', merk: '', kg: '', alasan: '', teks: '' };
}
const mtSebutCatatan = (c) => (CP_JENIS.find((j) => j[0] === c.jenis) || ['', c.jenis])[1] + ' ' + c.merk + (c.jumlah ? ' ' + String(c.jumlah).replace('.', ',') + ' ' + c.satuan : '') + (c.ket ? ' (' + c.ket + ')' : '');
/**
 * Susun satu USUL dari tablet untuk kedatangan tersimpan → SATU dokumen kabar barang masuk (persetujuan, tindakan 'barangMasuk', menunggu, atas nama yang jaga)
 * berkolom `usul`. TIDAK mengubah kedatangan, stok, bon, atau uang — owner yang membukukan dari HP. isi = draf mtUsulKosong.
 */
export function mtSusunUsul(isi, akun, w) {
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — usul butuh orang yang jaga' };
  const D = isi || {}; const C = cpKedatangan(D.id); if (!C) return { tolak: 'Kedatangan itu tidak ditemukan' };
  if (C.kunci) return { tolak: C.kunci.split(' — ')[0] + ' — kedatangan ini tidak bisa diubah lagi' };
  const siapa = (C.pemasok || 'pemasok') + ' ' + tanggalPendek(C.tanggal); let usul, teks;
  if (D.jenis === 'catatan') {
    const PB = cpPeriksaBaris(cpBarisTerisi(D.baris)); if (PB.tolak) return { tolak: PB.tolak };
    const bebas = String(D.bebas || '').replace(/\r\n/g, '\n').trim(); if (bebas.length > CP_MAKS.bebas) return { tolak: 'Catatan bebas paling panjang ' + CP_MAKS.bebas + ' huruf' };
    const cara = String(D.cara || ''); if (cara && !KLAIM_CARA.some((x) => x[0] === cara)) return { tolak: 'Cara klaim tidak dikenal' };
    if (cara && !PB.catatan.length) return { tolak: 'Klaim butuh minimal satu baris catatan (apa yang kurang, lebih, tertinggal, atau tidak sesuai)' };
    if (!PB.catatan.length && !bebas) return { tolak: 'Tulis dulu catatannya — apa yang kurang, lebih, tertinggal, atau tidak sesuai' };
    const status = KLAIM_STATUS.some((x) => x[0] === D.status) ? D.status : 'diminta';
    usul = Object.assign({ jenis: 'catatan', baris: PB.catatan, bebas }, cara ? { cara, status } : {});
    teks = 'USUL catatan untuk pemasok · ' + siapa + ': ' + (PB.catatan.map(mtSebutCatatan).join('; ') || 'catatan bebas') + (cara ? ' · ' + KLAIM_CARA.find((x) => x[0] === cara)[1].toLowerCase() + ', ' + KLAIM_STATUS.find((x) => x[0] === status)[1].toLowerCase() : '') + (bebas ? ' · "' + bebas + '"' : '');
  } else if (D.jenis === 'retur') {
    const alasan = String(D.alasan || '').trim(); if (alasan.length < 5) return { tolak: 'Tulis alasan beras itu dikembalikan (paling sedikit 5 huruf)' };
    const H = hitungReturPemasok(D.id, { merk: D.merk, kg: D.kg, alasan }); if (H.tolak) return { tolak: H.tolak };
    usul = { jenis: 'retur', merk: String(H.baris[0].merk), kg: H.kg, alasan: alasan.slice(0, 160) };
    teks = 'USUL kembalikan ke pemasok · ' + siapa + ': ' + usul.merk + ' ' + mtKg(H.kg) + ' — ' + usul.alasan + '. Stok & bon belum berubah; owner yang membukukan.';
  } else if (D.jenis === 'koreksi' || D.jenis === 'hapus') {
    const t = String(D.teks || '').trim(); if (t.length < 5) return { tolak: D.jenis === 'hapus' ? 'Tulis alasannya kedatangan ini minta dihapus (paling sedikit 5 huruf)' : 'Tulis apa yang salah dan yang benarnya (paling sedikit 5 huruf)' };
    if (t.length > MT_USUL_BATAS.teks) return { tolak: 'Paling panjang ' + MT_USUL_BATAS.teks + ' huruf' };
    usul = { jenis: D.jenis, teks: t };
    teks = (D.jenis === 'hapus' ? 'USUL hapus kedatangan · ' : 'USUL pembetulan kedatangan · ') + siapa + ': ' + t;
  } else return { tolak: 'Pilih dulu jenis usulnya' };
  const dok = tpDokKabarMasuk({ batchId: String(D.id), pemasok: C.pemasok, nominal: 0, teks }, akun, w); dok.data.usul = usul;
  return { dokumen: [dok], patch: { kabar: 'Usul terkirim ke owner — ' + MT_USUL.find((x) => x[0] === usul.jenis)[1].toLowerCase() + ' · ' + siapa + '. Belum ada yang berubah di stok, bon, atau uang; owner yang memutuskan dari HP.', kabarAwas: false } };
}
/** Usul dari tablet untuk kedatangan itu yang belum diperiksa owner, tertua dulu: [{ pid, dari, tanggal, jam, teks, usul }]. */
export function mtUsulMenunggu(id) {
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'barangMasuk' && m.usul && typeof m.usul === 'object' && String(m.batchId || '') === String(id) && (m.status || 'menunggu') === 'menunggu')
    .sort((a, b) => String(a.pada || '').localeCompare(String(b.pada || ''))).map((m) => ({ pid: String(m.id), dari: String(m.dari || 'tablet'), tanggal: String(m.tanggal || ''), jam: String(m.jam || ''), teks: String(m.teks || ''), usul: m.usul }));
}
/** Draf lembar owner dari satu usul: catatan → draf lembar Catatan untuk pemasok; retur → draf Kembalikan ke pemasok. Owner memeriksa lalu menyimpan sendiri. */
export function mtDrafDariUsul(id, pid) {
  const u = mtUsulMenunggu(id).find((x) => x.pid === String(pid)); if (!u) return null; const U = u.usul;
  if (U.jenis === 'catatan') { const C = cpKedatangan(id);
    return { cpDraf: { id: C ? C.id : id, baris: (U.baris || []).map((c) => ({ jenis: c.jenis, merk: c.merk, jumlah: c.jumlah ? String(c.jumlah).replace('.', ',') : '', satuan: c.satuan, ket: c.ket || '' })), cara: U.cara || (C && C.klaim ? C.klaim.cara : ''), status: U.status || (C && C.klaim ? C.klaim.status : 'diminta'),
      nilai: C && C.klaim && C.klaim.nilai ? String(C.klaim.nilai) : '', catatan: C && C.klaim ? C.klaim.catatan : '', bebas: U.bebas !== undefined ? String(U.bebas) : (C ? C.bebas : ''), dariUsul: false, usulId: u.pid, usulDari: u.dari } }; }
  if (U.jenis === 'retur') return { rtDraf: { id: String(id), merk: String(U.merk || ''), kg: String(U.kg || '').replace('.', ','), alasan: String(U.alasan || ''), yakin: false, usulId: u.pid, usulDari: u.dari } };
  return null;
}
