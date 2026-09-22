// STRUK (JS3-A + JS3-C, dikunci owner 18 Sep 2026) — logika tanpa DOM. Struk hanya MENYUSUN nota yang sudah tersimpan: tidak ada
// angka baru. Satu penyusun untuk kertas 58/80 mm dan WhatsApp (dua wujud, satu isi). Kop, kalimat kaki, lebar kertas, yang
// disertakan, dan aturan otomatis (cetak / WA sesudah nota tersimpan, per cara bayar & per pelanggan) = setelan owner di
// aturanToko/struk. Kirim WA = wa.me TANPA nomor (WhatsApp yang bertanya ke siapa) — nomor pembeli tidak disimpan, sama dengan
// sistem lama (kirimStrukTrx). Tiap struk yang keluar dicatat di koleksi baru `strukKeluar`.
// Yang dicetak = teks yang sama lewat dialog cetak perangkat (printer struk tertanam baru ada di tablet karyawan, belum dibangun).
import { ambilPenjualanSemua, ambilRetur, ambilStrukKeluar, cacheMentah } from '../data/toko.js';
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, bakuCaraBayar, formatTanggal, isoKeTanggal, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { RP } from '../inti/format.js';

export const ST_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
export const ST_KOLOM = { 58: 30, 80: 42 };
export const ST_OTO_CETAK = [['tidak', 'tidak'], ['tunai', 'tunai saja'], ['semua', 'semua nota']];
export const ST_OTO_WA = [['tidak', 'tidak'], ['bon', 'bon saja'], ['semua', 'semua nota']];
export const ST_PILIHAN_ORANG = [['ikut', 'ikut aturan'], ['wa', 'selalu WA'], ['cetak', 'selalu cetak'], ['tidak', 'tidak perlu']];
export const ST_SERTAKAN = [['rincian', 'rincian barang'], ['bon', 'sisa bon'], ['kaki', 'kalimat kaki'], ['pelayan', 'siapa yang melayani']];
// bawaan: aturan otomatis MATI dua-duanya (printer tertanam belum ada; WA yang dibuka sendiri sering ditahan peramban HP)
export const ST_ATUR_BAWAAN = { kop: { nama: 'Toko Beras M.IQBAL', alamat: '', telp: '' }, kaki: 'Terima kasih 🙏', kertas: 58,
  sertakan: { rincian: true, bon: true, kaki: true, pelayan: true }, oto: { cetak: 'tidak', wa: 'tidak' }, perOrang: {} };

const salin = (o) => JSON.parse(JSON.stringify(o));
/** Setelan struk: bawaan ditimpa yang tersimpan (aturanToko/struk). */
export function stAtur() {
  const B = salin(ST_ATUR_BAWAAN); const d = cacheMentah('aturan').find((x) => String(x.id) === 'struk'); if (!d) return B;
  if (d.kop) Object.keys(B.kop).forEach((k) => { if (d.kop[k] !== undefined && d.kop[k] !== null) B.kop[k] = String(d.kop[k]); });
  if (d.kaki !== undefined && d.kaki !== null) B.kaki = String(d.kaki);
  if (ST_KOLOM[d.kertas]) B.kertas = Number(d.kertas);
  if (d.sertakan) Object.keys(B.sertakan).forEach((k) => { if (typeof d.sertakan[k] === 'boolean') B.sertakan[k] = d.sertakan[k]; });
  if (d.oto) { if (ST_OTO_CETAK.some((x) => x[0] === d.oto.cetak)) B.oto.cetak = d.oto.cetak; if (ST_OTO_WA.some((x) => x[0] === d.oto.wa)) B.oto.wa = d.oto.wa; }
  if (d.perOrang) Object.keys(d.perOrang).forEach((k) => { if (ST_PILIHAN_ORANG.some((x) => x[0] === d.perOrang[k]) && d.perOrang[k] !== 'ikut') B.perOrang[k] = d.perOrang[k]; });
  return B;
}
/** Simpan setelan struk (isi = bentuk stAtur). Ditolak: nama kop kosong, kertas bukan 58/80, pilihan aturan yang tidak dikenal. */
export function susunAturStruk(isi, w) {
  const a = isi || {}; const kop = a.kop || {};
  const nama = String(kop.nama || '').trim(); if (!nama) return { tolak: 'Nama toko di kop tidak boleh kosong' };
  const kertas = Number(a.kertas); if (!ST_KOLOM[kertas]) return { tolak: 'Lebar kertas hanya 58 atau 80 mm' };
  const oto = a.oto || {};
  if (!ST_OTO_CETAK.some((x) => x[0] === oto.cetak)) return { tolak: 'Pilihan cetak otomatis tidak dikenal' };
  if (!ST_OTO_WA.some((x) => x[0] === oto.wa)) return { tolak: 'Pilihan WhatsApp otomatis tidak dikenal' };
  const perOrang = {}; Object.keys(a.perOrang || {}).forEach((k) => { const v = a.perOrang[k]; if (ST_PILIHAN_ORANG.some((x) => x[0] === v) && v !== 'ikut' && kunciPelanggan(k)) perOrang[kunciPelanggan(k)] = v; });
  const sertakan = {}; Object.keys(ST_ATUR_BAWAAN.sertakan).forEach((k) => { sertakan[k] = a.sertakan && typeof a.sertakan[k] === 'boolean' ? a.sertakan[k] : ST_ATUR_BAWAAN.sertakan[k]; });
  const data = { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: { nama: nama.slice(0, 40), alamat: String(kop.alamat || '').trim().slice(0, 80), telp: String(kop.telp || '').trim().slice(0, 30) },
    kaki: String(a.kaki || '').trim().slice(0, 80), kertas, sertakan, oto: { cetak: oto.cetak, wa: oto.wa }, perOrang };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { lembar: 'struk', aturStruk: null, kabar: 'Setelan struk tersimpan — kop, kertas ' + kertas + ' mm, cetak otomatis: ' + oto.cetak + ', WhatsApp otomatis: ' + oto.wa, kabarAwas: false } };
}

// ---------- nota ----------
/** Jumlah & satuan satu baris (jumlahTrx sistem lama + jenis baru: wadah = lembar). null = tidak berjumlah. */
export function jumlahBaris(p) {
  if (p.jenis === 'kemasan') return { nilai: p.jumlahUnit || 0, satuan: 'kemasan' };
  if (p.jenis === 'karung') return { nilai: p.jumlahKarung || 0, satuan: 'karung' };
  if (p.jenis === 'literan') return { nilai: p.jumlahLiter || 0, satuan: 'L' };
  if (p.jenis === 'repacking') return { nilai: p.totalKg || 0, satuan: 'kg' };
  if (p.jenis === 'wadah') return { nilai: p.jumlahUnit || 0, satuan: 'lembar' };
  return null;
}
/** Nama baris untuk struk (namaSingkatTrx sistem lama, dengan jenis baru). */
export function namaBaris(p) {
  const nama = p.namaProduk || p.merkSumber || 'Penjualan';
  if (p.jenis === 'kemasan') return nama + (p.ukuranKemasan ? ' ' + String(p.ukuranKemasan).replace('.', ',') + ' kg' : '');
  if (p.jenis === 'karung') return nama.replace(/ \(karung utuh\)$/, '') + ' karung ' + (p.beratKarungAcuan || 50) + ' kg';
  if (p.jenis === 'literan') return nama + ' literan';
  if (p.jenis === 'repacking') return 'Repack ' + nama;
  return nama;
}
/** Susun nota dari baris-barisnya (satu nota = trxId yang sama; nota lama = grupNota; sebelum itu satu baris = satu nota). */
export function notaDariBaris(baris) {
  const rows = (baris || []).slice().sort((a, b) => (a.id > b.id ? 1 : a.id < b.id ? -1 : 0)); if (!rows.length) return null;
  const p = rows[0]; const berlaku = rows.filter(penjualanMasihBerlaku);
  const uang = rows.find((x) => (x.uangDiterima || x.kembalianUangDiterima) > 0) || null;
  return { baris: rows, trxId: p.trxId || null, grupNota: p.grupNota || null, id: p.id, tanggal: p.tanggal || '', jam: p.jam || '', nama: String(p.namaPelanggan || '').trim(),
    cara: bakuCaraBayar(p.caraBayar), oleh: p.oleh || '', total: rows.reduce((a, x) => a + (x.hargaTotal || 0), 0), berlaku: berlaku.length === rows.length,
    dibatalkan: rows.some((x) => x.dibatalkan), dikoreksi: rows.some((x) => x.dikoreksiOleh && !x.dibatalkan),
    uangDiterima: uang ? (uang.uangDiterima || uang.kembalianUangDiterima || 0) : 0, kembalian: uang ? (uang.kembalian || uang.kembalianNominal || 0) : 0,
    tukarReturId: rows.map((x) => x.tukarReturId).filter(Boolean)[0] || null, kreditDibukaOwner: rows.some((x) => x.kreditDibukaOwner) };
}
/** Cari nota: kunci = { trxId } | { grupNota } | { id }. */
export function notaDari(kunci) {
  const semua = ambilPenjualanSemua(); let rows = [];
  if (kunci && kunci.trxId) rows = semua.filter((x) => String(x.trxId) === String(kunci.trxId));
  if (!rows.length && kunci && kunci.grupNota) rows = semua.filter((x) => String(x.grupNota) === String(kunci.grupNota));
  if (!rows.length && kunci && kunci.id !== undefined && kunci.id !== null) { const p = semua.find((x) => String(x.id) === String(kunci.id)); if (p) rows = p.trxId ? semua.filter((x) => String(x.trxId) === String(p.trxId)) : p.grupNota ? semua.filter((x) => String(x.grupNota) === String(p.grupNota)) : [p]; }
  return notaDariBaris(rows);
}

// ---------- penyusun ----------
/** Nilai KOTOR satu baris (sebelum potongan nota, tanpa pembulatan & upah yang melekat) — supaya baris + potongan + pembulatan menutup ke TOTAL. */
export const kotorBaris = (p) => (p.hargaTotal || 0) + (p.potonganTransaksi || 0) - (p.pembulatan || 0) - (p.upahRepack || 0);
/**
 * Susun struk. atur = stAtur(); pilih = { kertas, sertakan } menimpa setelan untuk struk ini saja.
 * Hasil: { garis: [{kiri, kanan, tebal, tengah}], kertas: baris teks selebar kolom, teks, wa, total, lebar }.
 */
export function susunStruk(nota, atur, pilih) {
  if (!nota) return null;
  const A = atur || stAtur(); const kertas = pilih && ST_KOLOM[pilih.kertas] ? Number(pilih.kertas) : A.kertas;
  const S = Object.assign({}, A.sertakan, (pilih && pilih.sertakan) || {});
  const lebar = ST_KOLOM[kertas]; const g = [];
  const baris = (kiri, kanan, o) => g.push(Object.assign({ kiri: String(kiri || ''), kanan: kanan === undefined || kanan === null ? '' : String(kanan) }, o || {}));
  const garis = () => g.push({ garis: true });
  baris(A.kop.nama.toUpperCase(), '', { tebal: true, tengah: true });
  if (A.kop.alamat) baris(A.kop.alamat, '', { tengah: true });
  if (A.kop.telp) baris('Telp ' + A.kop.telp, '', { tengah: true });
  garis();
  const d = nota.tanggal ? isoKeTanggal(nota.tanggal) : null;
  baris((d ? ST_HARI[d.getDay()] + ', ' : '') + formatTanggal(nota.tanggal) + (nota.jam ? ' · ' + nota.jam : ''), '');
  baris(nota.nama || 'Tanpa nama', '');
  if (S.pelayan && nota.oleh && !/^\(/.test(nota.oleh)) baris('Dilayani ' + nota.oleh, '');   // kolom oleh berbentuk "(darurat tanpa nama)" bukan nama orang
  garis();
  let pot = 0, bulat = 0, upah = 0;
  nota.baris.forEach((p) => { pot += p.potonganTransaksi || 0; bulat += p.pembulatan || 0; upah += p.upahRepack || 0; });
  if (S.rincian) {
    nota.baris.forEach((p) => {
      const j = jumlahBaris(p); const kotor = kotorBaris(p);
      if (p.penggantiRetur) { baris(namaBaris(p), ''); baris('  ' + (j ? String(j.nilai).replace('.', ',') + ' ' + j.satuan + ' · ' : '') + 'pengganti retur', RP(0)); return; }
      const satuan = j && j.nilai > 0 ? kotor / j.nilai : null; const bulatSatuan = satuan !== null && Math.abs(satuan - Math.round(satuan)) < 0.001;
      baris(namaBaris(p), j && bulatSatuan ? '' : RP(kotor));
      if (j && bulatSatuan) baris('  ' + String(j.nilai).replace('.', ',') + ' ' + j.satuan + ' × ' + RP(Math.round(satuan)).replace(/^Rp/, ''), RP(kotor));
      else if (j) baris('  ' + String(j.nilai).replace('.', ',') + ' ' + j.satuan, '');
      if (p.negoSelisih) baris('  harga tawar ' + (p.negoSelisih < 0 ? '−' : '+') + RP(Math.abs(p.negoSelisih)) + '/' + (j ? j.satuan : 'satuan'), '');
      if (p.upahRepack) baris('  upah repack', RP(p.upahRepack));
      if (p.bonusUnit) baris('  +' + p.bonusUnit + ' bonus (gratis)', '');
    });
    if (pot > 0) baris('Potongan', '−' + RP(pot));
    if (bulat > 0) baris('Pembulatan Rp500', '+' + RP(bulat));
    garis();
  }
  baris('TOTAL', RP(nota.total), { tebal: true });
  // TUKAR: tanpa baris ini struk menyatakan pembeli membayar harga penuh (susunStrukTrx sistem lama)
  const rT = nota.tukarReturId ? ambilRetur().find((x) => String(x.id) === String(nota.tukarReturId)) : null;
  if (rT && rT.tukarModel === 'kreditBarangGabung') { const hT = rT.hitunganTukarSistem || {}; baris('Tukar: barang kembali', '−' + RP(rT.nominalRefund || 0)); if (hT.dibayarPembeli !== undefined && hT.dibayarPembeli !== null) baris('DIBAYAR PEMBELI', RP(hT.dibayarPembeli), { tebal: true }); }
  else if (rT) baris('Susulan pengganti tukar ' + formatTanggal(rT.tanggal) + ' ' + (rT.jam || ''), '');
  let sisaBon = null;
  if (nota.cara === 'Kredit') {
    baris('BON — belum dibayar', '', { tebal: true }); if (nota.nama) baris('a.n. ' + nota.nama, '');
    if (S.bon && nota.nama) { const r = hitungPiutang().find((x) => x.kunci === kunciPelanggan(nota.nama)); sisaBon = r ? Math.max(0, r.sisa) : 0; baris('Sisa bon ' + nota.nama, RP(sisaBon)); }
  } else {
    baris('Bayar: ' + nota.cara, '');
    if (nota.uangDiterima > 0) { baris('Uang diterima', RP(nota.uangDiterima)); if (nota.kembalian > 0) baris('Kembali', RP(nota.kembalian)); }
  }
  if (!nota.berlaku) baris('(catatan ini sudah ' + (nota.dibatalkan ? 'dibatalkan' : 'dikoreksi') + ')', '');
  if (S.kaki && A.kaki) { baris('', ''); baris(A.kaki, '', { tengah: true }); }
  // dua wujud satu isi. Kertas: angka rata kanan; yang tidak muat DIBUNGKUS ke baris berikutnya — tidak pernah dipotong (angka tidak boleh terpenggal).
  const kanan = (t) => ' '.repeat(Math.max(0, lebar - t.length)) + t;
  const kertasBaris = [];
  g.forEach((x) => {
    if (x.garis) { kertasBaris.push('-'.repeat(lebar)); return; }
    if (!x.kanan) { if (!x.tengah || x.kiri.length >= lebar) { kertasBaris.push(x.kiri); return; } kertasBaris.push(' '.repeat(Math.floor((lebar - x.kiri.length) / 2)) + x.kiri); return; }
    const sisa = lebar - x.kiri.length - x.kanan.length;
    if (sisa > 0) kertasBaris.push(x.kiri + ' '.repeat(sisa) + x.kanan); else { kertasBaris.push(x.kiri); kertasBaris.push(kanan(x.kanan)); }
  });
  const waBaris = g.map((x) => (x.garis ? '------------------------------' : x.kanan ? (x.tebal ? '*' + x.kiri + '   ' + x.kanan + '*' : x.kiri + '   ' + x.kanan) : x.tebal && x.kiri ? '*' + x.kiri + '*' : x.kiri));
  return { garis: g, kertas: kertasBaris, teks: kertasBaris.join('\n'), wa: waBaris.join('\n'), total: nota.total, lebar, kertasMm: kertas, sisaBon, pot, bulat, upah };
}
export const tautanWa = (teks) => 'https://wa.me/?text=' + encodeURIComponent(String(teks || ''));

// ---------- aturan otomatis (JS3-C) ----------
/** Apa yang dilakukan sendiri sesudah nota tersimpan: pilihan pelanggan mengalahkan aturan per cara bayar. */
export function putusOto(atur, nota) {
  const A = atur || stAtur(); if (!nota) return { cetak: false, wa: false, teks: 'tidak' };
  const k = kunciPelanggan(nota.nama); const p = k ? A.perOrang[k] : null;
  if (p === 'wa') return { cetak: false, wa: true, teks: 'WA (pilihan ' + nota.nama + ')' };
  if (p === 'cetak') return { cetak: true, wa: false, teks: 'cetak (pilihan ' + nota.nama + ')' };
  if (p === 'tidak') return { cetak: false, wa: false, teks: 'tidak (pilihan ' + nota.nama + ')' };
  const cetak = A.oto.cetak === 'semua' || (A.oto.cetak === 'tunai' && nota.cara === 'Tunai');
  const wa = A.oto.wa === 'semua' || (A.oto.wa === 'bon' && nota.cara === 'Kredit');
  return { cetak, wa, teks: cetak && wa ? 'cetak + WA' : cetak ? 'cetak' : wa ? 'WA' : 'tidak' };
}
/** Catatan satu struk yang keluar (koleksi baru strukKeluar). cara = 'wa' | 'cetak'. */
export function susunStrukKeluar(nota, cara, w, ket) {
  return { koleksi: 'strukKeluar', data: { id: w.idUnik(), trxId: nota.trxId || nota.grupNota || nota.id, tanggal: w.tanggal, jam: w.jam, cara, nama: nota.nama || '', total: nota.total, ket: ket || '' } };
}
export function riwayatStruk(iso) {
  return ambilStrukKeluar().filter((x) => x.tanggal === iso).sort((a, b) => (b.id > a.id ? 1 : b.id < a.id ? -1 : 0))
    .map((x) => ({ id: x.id, jam: x.jam || '', cara: x.cara === 'wa' ? 'WhatsApp' : 'Cetak', nama: x.nama || 'tanpa nama', total: x.total || 0, ket: x.ket || '' }));
}
