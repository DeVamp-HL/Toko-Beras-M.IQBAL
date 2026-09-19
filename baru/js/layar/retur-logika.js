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
import { rtDasarNota, rtKalimatLebih, rtKunciNota, kunciPelanggan, bakuCaraBayar, formatTanggal } from '../mesin/pembantu.js';
import { ambilPenjualan } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';

export const ALASAN_RETUR = ['salah beli', 'kualitas kurang', 'kelebihan', 'kemasan rusak'];
export const returAwal = () => ({ rtCari: '', rtNotaId: null, rtKondisi: null, rtPenyelesaian: 'refund', rtAlasan: '', rtTimpa: false, rtNominal: '', rtAlasanTimpa: '' });

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
