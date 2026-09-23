// RETUR — LOGIKA (tanpa DOM). Putaran 4 (19 Sep 2026): retur yang MENUNJUK NOTA, refund atau tukar.
//
// Aturan yang dipegang (semua sudah live di index.html; di sini diikuti, bukan diciptakan ulang):
//  - nilai retur dihitung dari NOTA-nya lewat rtDasarNota() yang DIPINDAH VERBATIM (pembantu.js): hargaTotal − pembulatan,
//    potongan nota diprorata, dibagi banyaknya; sisa yang boleh kembali = nota − yang sudah diretur di seluruh rantai koreksi;
//  - hanya karung & kemasan; nota KREDIT, nota ber-bonus, nota perlu-koreksi DITOLAK di sini (di sistem lama ada jalan
//    ketik-tangan; di sistem baru belum — layar menyuruh ke sistem lama, tidak menebak nilainya);
//  - alasan WAJIB (KR3), kondisi WAJIB: layak dijual lagi → kembali ke stok; rusak/diragukan → Gudang Karantina
//    (dokumen karantina ber-id sama, bentuk tulisReturDanKarantina 16864);
//  - refund: uang keluar sebesar hitungan; boleh DITIMPA hanya ke BAWAH dengan alasan (nominalSistem + alasanTimpaNominal);
//  - tukar: TIDAK ditulis di sini — disusun lengkap lalu DIIKAT ke keranjang Jual (tukarModel 'kreditBarangGabung');
//    retur + penjualan penggantinya lahir dalam SATU tulisan saat nota dicatat (jual-logika.js susunNotaDokumen).
import { rtDasarNota, rtKalimatLebih, rtKunciNota, kunciPelanggan, bakuCaraBayar, formatTanggal, merkPunyaKarungBerat, kunciKemasan, namaSingkatTrx, tkApakahYatim, tkSetTertaut, tkTargetPengganti, tkPenjualanHidup } from '../mesin/pembantu.js';
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { ambilPenjualan, ambilRetur } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';

export const ALASAN_RETUR = ['salah beli', 'kualitas kurang', 'kelebihan', 'kemasan rusak'];
export const returAwal = () => ({ rtCari: '', rtNotaId: null, rtKondisi: null, rtPenyelesaian: 'refund', rtAlasan: '', rtTimpa: false, rtNominal: '', rtAlasanTimpa: '',
  // PUTARAN 20: retur TANPA nota (ketik tangan) & tukar yatim
  rtJenis: 'karung', rtBarang: '', rtBerat: 50, rtSelisih: '', rtYakin: false, rtPengganti: null });

const angka = (teks) => parseFloat(String(teks || '').replace(',', '.')) || 0;
const rupiah = (teks) => Math.round(Number(String(teks || '').replace(/[^\d]/g, '')) || 0);
function geser(iso, n) { const d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return hariIniIso(d); }
function teksBarang(t) {
  return t.jenis === 'kemasan' ? (t.namaProduk || '') + ' ' + (t.ukuranKemasan || '') + ' kg × ' + (t.jumlahUnit || 0)
    : (t.merkSumber || '') + ' ' + (t.beratKarungAcuan || 50) + ' kg × ' + (t.jumlahKarung || 0) + ' karung';
}

/** Nota yang bisa ditunjuk: baris karung/kemasan yang masih berlaku, 60 hari terakhir, terbaru dulu. */
export function daftarNotaRetur(s) {
  const hari = hariIniIso(s.sekarang); const batas = geser(hari, -60);
  const c = String(s.rtCari || '').trim().toLowerCase();
  return ambilPenjualan().filter((t) => (t.jenis === 'karung' || t.jenis === 'kemasan') && (t.tanggal || '') >= batas && !t.penggantiRetur)
    .filter((t) => !c || (String(t.namaPelanggan || '') + ' ' + teksBarang(t)).toLowerCase().indexOf(c) >= 0)
    .sort((a, b) => ((b.tanggal || '') + (b.jam || '')).localeCompare((a.tanggal || '') + (a.jam || ''))).slice(0, 40)
    .map((t) => { const d = rtDasarNota(t); return { id: String(t.id), tanggal: t.tanggal || '', jam: t.jam || '', nama: t.namaPelanggan || '', teks: teksBarang(t),
      hargaTotal: t.hargaTotal || 0, cara: bakuCaraBayar(t.caraBayar), bisa: !!d.ok, sebab: d.ok ? '' : d.sebab, cadangan: !d.ok && !!d.cadangan, sisa: d.ok ? d.sisa : 0, satuan: d.ok ? d.satuan : '' }; });
}

/** Nota yang sedang ditunjuk + dasar hitungnya, dibaca ULANG tiap kali (nota bisa dibatalkan/dikoreksi/diretur dari perangkat lain). */
export function notaDitunjuk(s) {
  if (!s.rtNotaId) return null;
  const t = ambilPenjualan().find((x) => String(x.id) === String(s.rtNotaId));
  if (!t) return { hilang: true };
  const d = rtDasarNota(t);
  const jml = angka(s.ketik);
  const nilai = d.ok && jml > 0 ? Math.round(jml * d.perSatuan) : 0;
  return { t, d, jml, nilai, teks: teksBarang(t) };
}

/** Susun draf retur dari isian; {tolak} atau {draf, nilai, d, t}. Bentuk = simpanRetur() index.html cabang _rtNota (15856). */
function susunDraf(s, w) {
  const n = notaDitunjuk(s);
  if (!n) return { tolak: 'Tunjuk dulu notanya' };
  if (n.hilang) return { tolak: 'Nota yang ditunjuk tidak ditemukan lagi — dibatalkan, dikoreksi, atau dihapus. Tunjuk nota yang berlaku.' };
  const { t, d, jml } = n;
  if (!d.ok) return { tolak: d.sebab };
  const catatan = String(s.rtAlasan || '').trim();
  if (!catatan) return { tolak: 'Pilih / isi alasan retur dulu (salah beli, kualitas, kelebihan, dll)' };
  if (s.rtKondisi !== 'utuh' && s.rtKondisi !== 'tidak_utuh') return { tolak: 'Jawab dulu: barang yang kembali BOLEH DIJUAL LAGI? Layak → kembali ke stok; rusak/diragukan → Karantina' };
  if (!(jml > 0)) return { tolak: 'Isi berapa ' + d.satuan + ' yang dikembalikan' };
  if (d.satuan === 'unit' && Math.round(jml) !== jml) return { tolak: 'Retur kemasan dihitung per UNIT utuh' };
  if (jml > d.sisa) return { tolak: rtKalimatLebih(d, jml) };
  const nilai = Math.round(jml * d.perSatuan);
  let draf;
  if (t.jenis === 'kemasan') {
    const uk = parseFloat(t.ukuranKemasan);
    draf = { jenisAsal: 'kemasan', namaProduk: t.namaProduk, ukuranKemasan: uk, jumlahUnit: jml, totalKg: uk * jml };
  } else {
    // karung sebagian (41,5 kg dari sack 50): totalKg = kg sungguhan, jumlahKarung = pecahannya — mesin stok membaca totalKg
    const berat = t.beratKarungAcuan || 50;
    draf = { jenisAsal: 'karung', merkSumber: t.merkSumber, jumlahKarung: Math.round(jml / berat * 1000) / 1000, beratKarungAcuan: berat, totalKg: jml };
  }
  Object.assign(draf, { notaAsalId: String(t.id), notaAsalTanggal: t.tanggal || '', notaAsalKunci: rtKunciNota(t), hargaPerSatuanNota: d.perSatuan,
    satuanNota: d.satuan, jumlahDikembalikan: jml, nilaiDikembalikan: nilai, dasarHargaNota: d.dasar,
    kondisi: s.rtKondisi, penyelesaian: s.rtPenyelesaian === 'tukar' ? 'tukar' : 'refund', catatan, id: w.idUnik(), tanggal: w.tanggal, jam: w.jam });
  return { draf, nilai, d, t };
}
const ringkasDraf = (draf) => (draf.merkSumber || draf.namaProduk || 'barang') + ' ' + String(draf.jumlahDikembalikan).replace('.', ',') + ' ' + (draf.satuanNota || '') + ' (nota ' + formatTanggal(draf.notaAsalTanggal || '') + ')';

/** Dokumen karantina untuk retur yang tidak layak dijual lagi — bentuk tulisReturDanKarantina() 16866. */
export function dokumenKarantina(doc) {
  return { koleksi: 'karantina', data: { id: doc.id, tanggal: doc.tanggal, asalRetur: true, jenisAsal: doc.jenisAsal, namaProduk: doc.namaProduk || null,
    ukuranKemasan: doc.ukuranKemasan || null, merkSumber: doc.merkSumber || null, totalKg: doc.totalKg, catatan: doc.catatan, statusTindakan: 'belum_diputuskan' } };
}

/**
 * Catat retur. REFUND → {dokumen, patch}; TUKAR → {ikat, patch} (tidak ada dokumen: lahir bersama nota penggantinya).
 */
export function susunRetur(s, w) {
  const r = susunDraf(s, w); if (r.tolak) return r;
  const { draf, nilai } = r;
  if (draf.penyelesaian === 'tukar') {
    draf.nominalRefund = nilai; draf.selisihHargaTukar = 0; draf.tukarModel = 'kreditBarangGabung';
    const ringkas = ringkasDraf(draf);
    return { ikat: { returDraf: draf, kredit: nilai, ringkas }, patch: Object.assign(returAwal(), { lembar: null, ketik: '', jalur: 'sering',
      kabar: 'Retur ' + ringkas + ' senilai ' + RP(nilai) + ' diikat ke keranjang — sekarang pilih barang PENGGANTINYA seperti menjual biasa. Retur + penjualan pengganti tercatat BERSAMA saat nota dicatat.', kabarAwas: false }) };
  }
  let nominal = nilai;
  if (s.rtTimpa) {
    nominal = rupiah(s.rtNominal);
    if (!(nominal > 0)) return { tolak: 'Isi nominal uang yang dikembalikan' };
    if (nominal > nilai) return { tolak: 'Nominal ' + RP(nominal) + ' melebihi nilai barang menurut nota (' + RP(nilai) + ') — menimpa hanya boleh MENURUNKAN' };
    const alasanTimpa = String(s.rtAlasanTimpa || '').trim();
    if (alasanTimpa.length < 4) return { tolak: 'Alasan menimpa wajib diisi — hitungan sistem ' + RP(nilai) + ' sedang ditimpa, jejaknya permanen' };
    if (nominal !== nilai) { draf.nominalSistem = nilai; draf.alasanTimpaNominal = alasanTimpa; }
  }
  draf.nominalRefund = nominal;
  const dokumen = [{ koleksi: 'retur', data: draf }];
  if (draf.kondisi === 'tidak_utuh') dokumen.push(dokumenKarantina(draf));
  return { dokumen, patch: Object.assign(returAwal(), { lembar: null, ketik: '',
    kabar: 'Retur dicatat — ' + ringkasDraf(draf) + ' · uang keluar ' + RP(nominal) + (draf.kondisi === 'utuh' ? ' · barang kembali ke stok jual' : ' · barang masuk Gudang Karantina'), kabarAwas: false }) };
}

/** Saat nota tukar dicatat: draf dibaca ULANG terhadap notanya (tkCekDraf 16891). null = masih sah. */
export function cekDrafTukar(draf) {
  const t = ambilPenjualan().find((x) => String(x.id) === String(draf.notaAsalId));
  if (!t) return 'Nota yang ditunjuk tukar ini tidak ditemukan lagi (dibatalkan/dikoreksi/dihapus). Batal tukar, lalu ulangi dari Retur.';
  const d = rtDasarNota(t);
  if (!d.ok) return d.sebab;
  if ((draf.jumlahDikembalikan || 0) > d.sisa) return rtKalimatLebih(d, draf.jumlahDikembalikan);
  return null;
}
export const kunciNama = kunciPelanggan;

// ==================== PUTARAN 20 · RETUR TANPA NOTA (ketik tangan) ====================
// Cabang simpanRetur() index.html TANPA _rtNota (15905–15943): barang dipilih (karung merek+berat / kemasan), jumlah diketik, nominal uang kembali DIKETIK (tidak ada nota
// untuk menghitungnya), tukar = selisih diketik (positif = toko mengembalikan, negatif = pembeli menambah) dan penggantinya dijual sebagai baris "pengganti retur" (model A).
// Penjaga sistem lama: retur melebihi yang pernah terjual − sudah diretur → confirm; di sini = ketukan kedua (rtYakin). Dokumen = bentuk lama + kolom `tanpaNota: true`.
/** Barang yang bisa diretur tanpa nota: karung per merek & berat (yang pernah ada di buku), kemasan per produk; berikut yang pernah terjual & sudah diretur. */
export function daftarBarangRetur() {
  const jual = ambilPenjualan(); const retur = ambilRetur(); const karung = []; const kemasan = [];
  Object.keys(hitungStokKarungPerMerk()).sort().forEach((merk) => { [50, 25].forEach((b) => { if (!merkPunyaKarungBerat(merk, b)) return;
    const terjual = jual.filter((p) => p.jenis === 'karung' && p.merkSumber === merk && (p.beratKarungAcuan || 50) === b).reduce((a, p) => a + (p.jumlahKarung || 0), 0);
    const diretur = retur.filter((r) => r.jenisAsal === 'karung' && r.merkSumber === merk && (r.beratKarungAcuan || 50) === b).reduce((a, r) => a + (r.jumlahKarung || 0), 0);
    karung.push({ kunci: merk + '|' + b, merk, berat: b, nama: merk + ' ' + b + ' kg', terjual, diretur, satuan: 'karung' }); }); });
  const sk = hitungStokKemasan(); Object.keys(sk).sort().forEach((k) => { const x = sk[k]; const uk = parseFloat(x.ukuranKemasan);
    const terjual = jual.filter((p) => p.jenis === 'kemasan' && p.namaProduk === x.namaProduk && parseFloat(p.ukuranKemasan) === uk).reduce((a, p) => a + (p.jumlahUnit || 0), 0);
    const diretur = retur.filter((r) => r.jenisAsal === 'kemasan' && r.namaProduk === x.namaProduk && parseFloat(r.ukuranKemasan) === uk).reduce((a, r) => a + (r.jumlahUnit || 0), 0);
    kemasan.push({ kunci: k, namaProduk: x.namaProduk, ukuran: uk, nama: x.namaProduk + ' ' + uk + ' kg', terjual, diretur, satuan: 'unit' }); });
  return { karung, kemasan };
}
export function barangReturDipilih(s) { const D = daftarBarangRetur(); return s.rtJenis === 'kemasan' ? D.kemasan.find((x) => x.kunci === s.rtBarang) || null : D.karung.find((x) => x.kunci === s.rtBarang) || null; }
/** Catat retur tanpa nota: {tolak[, perluYakin]} atau {dokumen, patch}. */
export function susunReturTanpaNota(s, w) {
  const B = barangReturDipilih(s); if (!B) return { tolak: 'Pilih barang yang dikembalikan dulu' };
  const jml = angka(s.ketik); if (!(jml > 0)) return { tolak: 'Isi berapa ' + B.satuan + ' yang dikembalikan' };
  if (s.rtJenis === 'kemasan' && Math.round(jml) !== jml) return { tolak: 'Retur kemasan dihitung per UNIT utuh' };
  if (s.rtJenis !== 'kemasan' && (jml * 2) % 1 !== 0) return { tolak: 'Retur karung tanpa nota dihitung per karung utuh atau setengah' };
  const catatan = String(s.rtAlasan || '').trim(); if (!catatan) return { tolak: 'Pilih / isi alasan retur dulu (salah beli, kualitas, kelebihan, dll)' };
  if (s.rtKondisi !== 'utuh' && s.rtKondisi !== 'tidak_utuh') return { tolak: 'Jawab dulu: barang yang kembali BOLEH DIJUAL LAGI? Layak → kembali ke stok; rusak/diragukan → Karantina' };
  const bebas = B.terjual - B.diretur;
  if (jml > bebas && !s.rtYakin) return { tolak: B.nama + ' cuma pernah terjual ' + String(B.terjual).replace('.', ',') + ' ' + B.satuan + ' (sudah diretur ' + String(B.diretur).replace('.', ',') + ') — retur ' + String(jml).replace('.', ',') + ' melebihi itu, mungkin salah ketik. Ketuk sekali lagi kalau memang benar.', perluYakin: true };
  const draf = s.rtJenis === 'kemasan' ? { jenisAsal: 'kemasan', namaProduk: B.namaProduk, ukuranKemasan: B.ukuran, jumlahUnit: jml, totalKg: B.ukuran * jml } : { jenisAsal: 'karung', merkSumber: B.merk, jumlahKarung: jml, beratKarungAcuan: B.berat, totalKg: jml * B.berat };
  Object.assign(draf, { kondisi: s.rtKondisi, penyelesaian: s.rtPenyelesaian === 'tukar' ? 'tukar' : 'refund', catatan, id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tanpaNota: true });
  let uang = 0;
  if (draf.penyelesaian === 'refund') { const n = rupiah(s.rtNominal); if (!(n > 0)) return { tolak: 'Isi nominal uang yang dikembalikan — tanpa nota tidak ada yang bisa menghitungnya untukmu' }; draf.nominalRefund = n; uang = n; }
  else { const t = String(s.rtSelisih || '').trim(); if (t === '') return { tolak: 'Isi selisih tukarnya — ketik 0 kalau memang tidak ada selisih' }; const n = Math.round(Number(t.replace(/\./g, '').replace(',', '.'))); if (!isFinite(n)) return { tolak: 'Selisih tukar bukan angka' }; draf.selisihHargaTukar = n; uang = Math.max(0, n); }
  const dokumen = [{ koleksi: 'retur', data: draf }]; if (draf.kondisi === 'tidak_utuh') dokumen.push(dokumenKarantina(draf));
  const ringkas = B.nama + ' × ' + String(jml).replace('.', ',') + ' ' + B.satuan;
  return { dokumen, patch: Object.assign(returAwal(), { lembar: null, ketik: '', kabar: 'Retur TANPA NOTA dicatat — ' + ringkas + (draf.penyelesaian === 'refund' ? ' · uang keluar ' + RP(uang) : ' · tukar, selisih ' + (draf.selisihHargaTukar >= 0 ? 'toko mengembalikan ' : 'pembeli menambah ') + RP(Math.abs(draf.selisihHargaTukar)) + ' — jual penggantinya dengan pil "pengganti retur" supaya tidak dihitung omzet dua kali') + (draf.kondisi === 'utuh' ? ' · barang kembali ke stok jual' : ' · barang masuk Gudang Karantina'), kabarAwas: false }) };
}

// ==================== PUTARAN 20 · TUKAR YATIM (penggantinya belum tercatat) ====================
// tkReturYatim / tkSusul / tkSudahDijual index.html 17064–17135: retur tukar yang penjualan penggantinya tidak (atau belum cukup) tercatat.
// "catat penggantinya" = keranjang diikat sebagai SUSULAN: baris nota membawa tukarReturId, TIDAK ada retur baru; "pengganti sudah tercatat" = tanda penggantiDikonfirmasi di dokumen retur.
export function returYatim() {
  const T = tkSetTertaut();
  return ambilRetur().filter((r) => tkApakahYatim(r, T)).map((r) => { const target = tkTargetPengganti(r); const a = T.get(String(r.id)); const rp = a ? a.rp : 0;
    return { id: String(r.id), tanggal: r.tanggal || '', jam: r.jam || '', barang: r.merkSumber || r.namaProduk || '', nominal: r.nominalRefund || 0, model: r.tukarModel, target, tercatat: rp, kurang: target === null ? null : Math.max(0, target - rp),
      teks: target === null ? 'tukar lama (nilai pengganti tidak tercatat)' : rp > 0 ? 'pengganti tercatat ' + RP(rp) + ' dari ' + RP(target) + ' — kurang ' + RP(target - rp) : 'pengganti ' + RP(target) + ' tidak tercatat lagi' }; })
    .sort((a, b) => (b.tanggal + b.jam).localeCompare(a.tanggal + a.jam));
}
/** Ikat keranjang sebagai SUSULAN pengganti tukar yatim (tkSusul 17078). Hasil = ikatan untuk ikatTukar(): kredit 0 (uangnya sudah diterima saat tukar). */
export function ikatSusulan(id) {
  const y = returYatim().find((r) => r.id === String(id)); if (!y) return { tolak: 'Retur itu tidak ada lagi di daftar yatim — sudah punya pengganti tercatat' };
  const r = ambilRetur().find((x) => String(x.id) === String(id)); const hT = (r && r.hitunganTukarSistem) || {};
  return { ikat: { susulanReturId: y.id, kredit: 0, ringkas: 'SUSULAN tukar ' + formatTanggal(y.tanggal) + ' ' + y.jam + ' · ' + y.barang, model: y.model, kurang: y.kurang, nilaiRetur: y.nominal, caraTukar: hT.caraBayar || '' },
    kabar: 'Keranjang ini jadi PENGGANTI tukar ' + formatTanggal(y.tanggal) + ' ' + y.jam + (y.kurang !== null ? ' — catat HANYA yang belum: ' + RP(y.kurang) : '') + (hT.caraBayar ? ' · waktu tukar dibayar ' + hT.caraBayar + ', pilih cara bayar yang sama' : '') + '. Dicatat PENUH, uang tukarnya sudah diterima saat tukar; retur TIDAK ditulis lagi.' };
}
/** Dibaca ULANG saat nota dicatat (tkCekSusulan 17036). null = sah. */
export function cekSusulan(id, total, yakinLebih) {
  const r = ambilRetur().find((x) => String(x.id) === String(id)); if (!r) return 'Retur yang disusul keranjang ini tidak ditemukan lagi. Batal tukar dulu.';
  if (!tkApakahYatim(r, tkSetTertaut())) return 'Retur ' + formatTanggal(r.tanggal) + ' ' + (r.jam || '') + ' SUDAH punya pengganti tercatat — keranjang ini akan mencatatnya DUA KALI. Batal tukar; kalau barangnya untuk pembeli lain, jual biasa.';
  const target = tkTargetPengganti(r); if (target !== null) { const a = tkSetTertaut().get(String(r.id)); const kurang = Math.max(0, target - (a ? a.rp : 0)); if (total > kurang + 499 && !yakinLebih) return 'Keranjang ' + RP(total) + ' MELEBIHI yang belum tercatat untuk tukar ini (' + RP(kurang) + ') — barang yang sudah tercatat jangan dicatat lagi. Ketuk "nilainya memang berubah" kalau benar.'; }
  return null;
}
/** Calon penjualan yang bisa dianggap pengganti tukar yatim (tkSudahDijual 17093): sejak tanggal retur, bukan pengganti-retur, belum dipakai retur lain, terdekat jamnya dulu. */
export function calonPengganti(id, kini) {
  const r = ambilRetur().find((x) => String(x.id) === String(id)); if (!r) return [];
  const menit = (j) => { const m = /^(\d{1,2}):(\d{2})/.exec(j || ''); return m ? (+m[1]) * 60 + (+m[2]) : 0; };
  const dipakai = new Set(ambilRetur().map((x) => x.penggantiDikonfirmasi && tkPenjualanHidup(x.penggantiDikonfirmasi.penjualanId)).filter(Boolean).map((pj) => String(pj.id)));
  const iso = hariIniIso(kini);
  return ambilPenjualan().filter((pj) => pj.tanggal >= r.tanggal && pj.tanggal <= iso && (pj.hargaTotal || 0) > 0 && !pj.penggantiRetur && (!pj.tukarReturId || String(pj.tukarReturId) === String(r.id)) && !dipakai.has(String(pj.id)))
    .sort((a, b) => (a.tanggal === b.tanggal ? 0 : (a.tanggal < b.tanggal ? -1 : 1)) || Math.abs(menit(a.jam) - menit(r.jam)) - Math.abs(menit(b.jam) - menit(r.jam))).slice(0, 12)
    .map((pj) => ({ id: String(pj.id), tanggal: pj.tanggal, jam: pj.jam || '', teks: namaSingkatTrx(pj), nama: pj.namaPelanggan || '', hargaTotal: pj.hargaTotal || 0, sudahTertaut: String(pj.tukarReturId) === String(r.id) }));
}
/** Tandai penjualan sebagai pengganti tukar yatim: dokumen retur ditulis ulang dengan penggantiDikonfirmasi {penjualanId, pada}; penjualannya TIDAK diubah. */
export function susunPenggantiTercatat(id, penjualanId, w) {
  const r = ambilRetur().find((x) => String(x.id) === String(id)); if (!r) return { tolak: 'Retur itu tidak ditemukan lagi' };
  if (!tkApakahYatim(r, tkSetTertaut())) return { tolak: 'Retur itu sudah punya pengganti tercatat' };
  const c = calonPengganti(id, new Date(String(w.tanggal) + 'T12:00:00')).find((x) => x.id === String(penjualanId)); if (!c) return { tolak: 'Penjualan itu tidak ada di daftar calon pengganti' };
  return { dokumen: [{ koleksi: 'retur', data: Object.assign({}, r, { penggantiDikonfirmasi: { penjualanId: String(penjualanId), pada: w.kini || new Date().toISOString() } }) }],
    patch: { rtPengganti: null, lembar: null, kabar: 'Penjualan ' + c.jam + ' · ' + c.teks + ' · ' + RP(c.hargaTotal) + ' ditandai sebagai pengganti tukar ' + formatTanggal(r.tanggal) + ' — penjualannya tidak diubah, tandanya di dokumen retur', kabarAwas: false } };
}
