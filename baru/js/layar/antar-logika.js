// SURAT JALAN & ANTAR — putaran B3 (keputusan owner 18 Nov 2026). Logika TANPA DOM, nama berawalan aj (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_antar.py (jsc + statis + kontrol).
//
// Keputusan owner 18 Nov 2026:
//  - ONGKIR = baris terpisah di nota (struk menyebutnya sendiri), terpisah dari jualan beras, boleh Rp0. Tarif bawaan diatur owner sendiri (Pelanggan › Atur).
//    Bensin tetap biaya "Bensin & angkut" di kendali biaya.
//  - BAYAR DI TEMPAT = nota dicatat waktu barang berangkat (stok keluar), sementara BON atas nama pembeli, BEBAS batas kredit hari itu; lunas waktu uang
//    dibawa pulang (pelunasan piutang ber-untukSJ, dibawaOleh = pengantar). Belum disetor sampai tutup hari → peringatan merah atas nama pengantarnya;
//    sesudah hari itu sisanya bon biasa (ikut batas untuk bon berikutnya).
//  - SIAPA: owner + Ben membuat surat jalan (bersama notanya); pengantar (Ben / karyawan) menandai diterima / gagal antar. Rules v10.
//  - BUKTI TERIMA: tanda tangan penerima di layar (wajib) + foto (boleh dilewati) — koleksi buktiTerima, TIDAK didengar, dibaca saat surat jalan dibuka.
//  - SUSULAN owner 18 Nov (perangkat kasir cuma satu, tablet tidak ikut mengantar): cara UTAMA = TANDA TANGAN DI KERTAS. Surat jalan dicetak 2 lembar
//    (LEMBAR PEMBELI ditinggal, LEMBAR TOKO ditandatangani penerima & dibawa pulang); di toko pengantar menandai diterima + FOTO lembar toko (WAJIB —
//    satu-satunya bukti di sistem, kertas termal memudar). Kotak tanda tangan di layar tetap ada (kalau tablet / HP ikut). Rules v10 TIDAK berubah:
//    buktiTtd kosong + buktiFoto berisi, keterangan cara ada di riwayatStatus & dokumen bukti (isiBukti: 'kertas').
// Nomor surat jalan aman tanpa internet: SJ<yy>-<kode perangkat>-<urut 4> (kode perangkat = nomor faktur B2; dua perangkat tidak berbagi awalan).
//
// ONGKIR DISIMPAN SEBAGAI KOLOM `ongkirAntar` YANG MELEKAT DI SATU BARIS NOTA (ikut hargaTotal — pola upahRepack & pembulatan). Baris jenis baru ber-HPP 0
// akan masuk "tanpa HPP" di mesin laba beku (hppTercatat: HPP 0 + harga > 0 = belum tercatat) dan hilang dari laba; menempel = kas, bon, laba, pajak dibaca
// mesin beku apa adanya. Yang memisahkannya dari jualan beras = lapisan TAK beku: Laporan per merek (baris luar 'ongkir'), nilai retur (ajDasarRetur),
// struk & riwayat. Baris pembawa = baris bermodal tercatat yang nilainya terbesar (laba ongkir ikut terhitung), selain itu baris terakhir yang bernilai.
// MESIN UANG TIDAK DISENTUH.
import { cacheMentah, ambilPenjualan, ambilPenjualanSemua, ambilPiutangMutasi, ambilSuratJalan } from '../data/toko.js';
import { kunciPelanggan, hppTercatat, twSatuanDibayar, rtKunciNota } from '../mesin/pembantu.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { fkKodePerangkat, fkKartu } from './faktur-logika.js';

export const AJ_KOLEKSI = 'suratJalan';
export const AJ_BUKTI = 'buktiTerima';
export const AJ_TARIF_MAKS = 5000000;          // Rp5 juta — penjaga salah ketik ongkir, bukan kebijakan
export const AJ_PENGANTAR_BAWAAN = ['Ben'];
export const AJ_STATUS = { berangkat: 'di jalan', diterima: 'diterima', gagal: 'gagal antar', batal: 'dibatalkan' };
// kolom yang boleh diubah pengantar bukan-owner saat menandai (rules v10 stafTandaiSJ — daftar yang SAMA, dijaga uji statis)
export const AJ_KOLOM_TANDAI = ['status', 'riwayatStatus', 'penerima', 'diterimaPada', 'diterimaTanggal', 'diterimaJam', 'catatanTerima', 'buktiTtd', 'buktiFoto',
  'uangDiterima', 'caraUang', 'pelunasanId', 'alasanGagal', 'ditandaiOleh'];
// kolom keputusan yang TIDAK boleh ada di surat jalan baru buatan bukan-owner (rules v10 stafBuatSJ)
export const AJ_KOLOM_BUKAN_BARU = ['penerima', 'diterimaPada', 'diterimaTanggal', 'diterimaJam', 'buktiTtd', 'buktiFoto', 'uangDiterima', 'pelunasanId', 'alasanGagal', 'batalPada', 'alasanBatal'];
// bukti: foto memakai pengecil foto bon (≤ 700 KB); tanda tangan = PNG goresan hitam di kanvas putih (kecil)
export const AJ_BUKTI_BATAS = 700 * 1024;
export const AJ_JENIS_BUKTI = ['image/jpeg', 'image/png', 'image/webp'];
// cara tanda terima: 'kertas' (bawaan layar Terima — tanda tangan di lembar toko, difoto di toko) | 'layar' (kotak tanda tangan di perangkat yang ikut)
export const AJ_CARA_TERIMA = { kertas: 'tanda tangan di kertas', layar: 'tanda tangan di layar' };

const ajKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const ajBulat = (n) => Math.round(Number(n) || 0);

// ---------- atur (Pelanggan › Atur — aturanToko/pelanggan, dokumen yang juga dibaca tablet Ben) ----------
const ajAturMentah = () => cacheMentah('aturan').find((d) => String(d.id) === 'pelanggan') || null;
/** Rupiah ongkir yang sah: bilangan bulat 0 – Rp5 juta (titik ribuan boleh); kosong = 0; salah = null. */
export function ajRupiahSah(v) {
  if (ajKosong(v)) return 0;
  const t = String(v).trim().replace(/^rp\s*/i, '').replace(/\./g, '').replace(/\s/g, '');
  if (!/^\d+$/.test(t)) return null;
  const n = Number(t); return n >= 0 && n <= AJ_TARIF_MAKS ? n : null;
}
const ajDaftarNama = (d) => (Array.isArray(d) ? d.map((x) => String(x || '').trim().slice(0, 30)).filter(Boolean) : null);
/** Setelan antar: { tarif, pengantar[], kendaraan[] }. Belum diatur = tarif 0, pengantar [Ben], kendaraan kosong. */
export function ajAtur() {
  const a = ajAturMentah();
  const tarif = a ? ajRupiahSah(a.tarifOngkir) : 0;
  const p = a ? ajDaftarNama(a.pengantarAntar) : null; const k = a ? ajDaftarNama(a.kendaraanAntar) : null;
  return { tarif: tarif === null ? 0 : tarif, pengantar: p && p.length ? p : AJ_PENGANTAR_BAWAAN.slice(), kendaraan: k || [] };
}
/** Bagian aturanToko/pelanggan milik antar (dipanggil susunAturPelanggan): {tarifOngkir, pengantarAntar, kendaraanAntar} atau {tolak}. isi = teks Atur. */
export function ajBacaAtur(isi) {
  const A = ajAtur(); const x = isi || {};
  const tarif = x.tarifOngkir === undefined ? A.tarif : ajRupiahSah(x.tarifOngkir);
  if (tarif === null) return { tolak: 'Tarif ongkir bawaan: angka rupiah 0 – ' + RP(AJ_TARIF_MAKS) };
  const p = x.pengantarAntar === undefined ? A.pengantar : ajDaftarNama(x.pengantarAntar) || [];
  if (!p.length) return { tolak: 'Daftar yang bisa mengantar tidak boleh kosong — minimal satu nama' };
  const k = x.kendaraanAntar === undefined ? A.kendaraan : ajDaftarNama(x.kendaraanAntar) || [];
  const dobel = (d) => d.find((n, i) => d.findIndex((m) => m.toLowerCase() === n.toLowerCase()) !== i);
  if (dobel(p)) return { tolak: 'Nama pengantar "' + dobel(p) + '" tertulis dua kali' };
  if (dobel(k)) return { tolak: 'Kendaraan "' + dobel(k) + '" tertulis dua kali' };
  return { tarifOngkir: tarif, pengantarAntar: p, kendaraanAntar: k };
}

/** Berapa hari nama pengantar dari luar daftar (kurir lepas) tetap muncul sebagai pilihan di Bayar › Antar. */
export const AJ_PENGANTAR_INGAT_HARI = 60;
/**
 * Pilihan "yang mengantar" di Bayar › Antar (owner 18 Nov: yang mengantar sekarang BUKAN pegawai tetap): { tetap: daftar Pelanggan › Atur,
 * lain: nama yang pernah mengantar tapi tidak di daftar — surat jalan AJ_PENGANTAR_INGAT_HARI hari terakhir, terbaru dulu, paling banyak 6 }.
 * Nama baru diketik lewat "+ orang lain" (kurir lepas tidak perlu akun — tanda terimanya ditandai di toko, lembar toko difoto).
 */
export function ajPilihanPengantar(hariIso) {
  const A = ajAtur(); const kenal = {}; A.pengantar.forEach((n) => { kenal[kunciPelanggan(n)] = 1; });
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(hariIso || '')); const batas = m ? new Date(Date.UTC(+m[1], +m[2] - 1, +m[3] - AJ_PENGANTAR_INGAT_HARI)).toISOString().slice(0, 10) : '';
  const lain = [];
  (ambilSuratJalan() || []).filter((x) => x && !ajKosong(x.pengantar) && String(x.tanggal || '') >= batas)
    .sort((a, b) => (String(b.tanggal || '') + String(b.jam || '')).localeCompare(String(a.tanggal || '') + String(a.jam || '')))
    .forEach((x) => { const n = String(x.pengantar).trim().slice(0, 30); const k = kunciPelanggan(n); if (!kenal[k] && lain.length < 6) { kenal[k] = 1; lain.push(n); } });
  return { tetap: A.pengantar, lain };
}

// ---------- draf antar di keranjang Jual ----------
/** Draf baru untuk keranjang: alamat dari kartu pelanggan, ongkir = tarif bawaan, pengantar & kendaraan pertama. */
export function ajDrafBaru(nama) {
  const A = ajAtur(); const k = ajKosong(nama) ? null : fkKartu(nama);
  return { alamat: String((k && k.alamat) || '').trim().slice(0, 160), ongkir: A.tarif ? String(A.tarif) : '', pengantar: A.pengantar[0] || '', kendaraan: A.kendaraan[0] || '', cod: false, catatan: '' };
}
/** Ongkir draf dalam rupiah (salah ketik = 0; penolakannya di ajAlasanTolak). */
export function ajOngkir(antar) { if (!antar) return 0; const n = ajRupiahSah(antar.ongkir); return n === null ? 0 : n; }
/** Alasan draf antar belum bisa dicatat ('' = sah). s = keadaan Jual. */
export function ajAlasanTolak(s) {
  const a = s && s.antar; if (!a) return '';
  if (s.tukar) return 'Tukar tidak bisa sekaligus diantar — catat tukarnya dulu, lalu nota antarnya';
  if (s.karcis) return 'Rincian karcis tidak bisa diantar';
  if (ajRupiahSah(a.ongkir) === null) return 'Ongkir: ketik angka rupiah 0 – ' + RP(AJ_TARIF_MAKS);
  if (ajKosong(a.pengantar)) return a.pengantarKetik ? 'Ketik nama yang mengantar (orang lain / kurir lepas)' : 'Pilih siapa yang mengantar';
  if (a.cod && ajKosong(s.pelanggan)) return 'Bayar di tempat = bon sementara — isi nama pembelinya';
  if (a.cod && s.cara !== 'Kredit') return 'Bayar di tempat dicatat sebagai bon sementara — ketuk "Bayar di tempat" lagi';
  if (String(a.alamat || '').length > 160) return 'Alamat antar terlalu panjang (maks. 160 huruf)';
  return '';
}
/** Patch Jual saat "bayar di tempat" dinyalakan / dimatikan. Nyala = nota bon sementara (cara Kredit, tanpa uang diterima). */
export function ajSetelCod(s, nyala) {
  if (!s.antar) return {};
  if (nyala) return { antar: Object.assign({}, s.antar, { cod: true }), cara: 'Kredit', uang: 0 };
  return { antar: Object.assign({}, s.antar, { cod: false }), cara: s.cara === 'Kredit' ? 'Tunai' : s.cara };
}

// ---------- nomor surat jalan (aman tanpa internet) ----------
export function ajAwalan(tanggal, kode) { return 'SJ' + String(tanggal || '').slice(2, 4) + '-' + (kode || fkKodePerangkat()) + '-'; }
/** Nomor berikutnya untuk perangkat ini di tahun tanggal itu: urut terbesar yang sudah tertulis (termasuk yang batal) + 1 — tidak pernah dipakai ulang. */
export function ajNomorBaru(tanggal, kode) {
  const aw = ajAwalan(tanggal, kode); let maks = 0;
  const lihat = (n) => { const t = String(n || ''); if (t.indexOf(aw) === 0) { const u = Number(t.slice(aw.length)); if (Number.isInteger(u) && u > maks) maks = u; } };
  (ambilSuratJalan() || []).forEach((d) => lihat(d.noSJ));
  (ambilPenjualanSemua() || []).forEach((p) => lihat(p.noSJ));   // nota yang suratnya belum sampai cache (antre) tetap memegang nomornya
  return aw + ('0000' + (maks + 1)).slice(-Math.max(4, String(maks + 1).length));
}

// ---------- ongkir menempel di baris nota ----------
/** Indeks baris pembawa ongkir: baris bermodal tercatat (hppTercatat) bernilai terbesar; tidak ada → baris terakhir yang bernilai; -1 = tidak ada. */
export function ajBarisPembawa(items) {
  let pilih = -1, nilai = -1;
  (items || []).forEach((t, i) => { if ((t.hargaTotal || 0) > 0 && hppTercatat(t) && t.hargaTotal > nilai) { pilih = i; nilai = t.hargaTotal; } });
  if (pilih >= 0) return pilih;
  for (let i = (items || []).length - 1; i >= 0; i--) { if ((items[i].hargaTotal || 0) > 0) return i; }
  return (items || []).length ? items.length - 1 : -1;
}
/** Ongkir satu nota (jumlah kolom ongkirAntar di baris-barisnya). */
export function ajOngkirNota(baris) { return (baris || []).reduce((a, p) => a + ajBulat(p.ongkirAntar), 0); }
/** Isi surat jalan dari keranjang (TANPA harga): [{ nama, jumlah, satuan }]. */
export function ajIsiKeranjang(keranjang) {
  return (keranjang || []).map((b) => { const t = b.trx || b; return { nama: String(t.label || t.namaProduk || '').slice(0, 60), jumlah: Number(t.jumlah) || 0, satuan: String(t.satuan || '') }; }).filter((x) => x.nama);
}
/**
 * Dokumen surat jalan untuk nota yang dicatat bersamaan. c = { trxId, nama, total, ongkir, noFaktur, keranjang, noSJ, uangMuka, noPO }.
 * tagihRp = yang ditagih di tempat (bayar di tempat = total nota − uang muka pesanan (B4); selain itu 0).
 */
export function ajDokumenSJ(s, w, c) {
  const a = s.antar; const cod = !!a.cod;
  const d = { id: w.idUnik(), noSJ: c.noSJ, tanggal: w.tanggal, jam: w.jam, trxIdJual: String(c.trxId), namaPelanggan: String(c.nama || '').trim(),
    alamat: String(a.alamat || '').trim().slice(0, 160), pengantar: String(a.pengantar || '').trim().slice(0, 30), kendaraan: String(a.kendaraan || '').trim().slice(0, 30),
    catatan: String(a.catatan || '').trim().slice(0, 160), isi: ajIsiKeranjang(c.keranjang), nilaiNota: ajBulat(c.total), ongkir: ajBulat(c.ongkir),
    bayarDiTempat: cod, tagihRp: cod ? Math.max(0, ajBulat(c.total) - ajBulat(c.uangMuka)) : 0, noFaktur: String(c.noFaktur || ''),
    status: 'berangkat', riwayatStatus: [{ status: 'berangkat', pada: w.kini || new Date().toISOString() }] };
  // B4 (owner 18 Nov 2026): nomor PO pelanggan & uang muka yang sudah masuk ikut dicetak (kolom tambahan saat dibuat — rules v10 stafBuatSJ tidak membatasinya)
  if (String(c.noPO || '').trim()) d.noPO = String(c.noPO).trim().slice(0, 30);
  if (ajBulat(c.uangMuka) > 0) d.uangMuka = ajBulat(c.uangMuka);
  return d;
}

// ---------- daftar & keadaan surat jalan ----------
/** Pelunasan yang menunjuk surat jalan itu (untukSJ) — uang bayar di tempat yang sudah dibawa pulang. */
export function ajPelunasan(noSJ) { const n = String(noSJ || ''); return n ? (ambilPiutangMutasi() || []).filter((m) => m && m.tipe === 'bayar' && String(m.untukSJ || '') === n) : []; }
/** Nota surat jalan masih berlaku? (semua baris notanya belum dibatalkan / dikoreksi) — null = barisnya tidak ada di cache. */
function ajNotaBerlaku(trxId) {
  const b = (ambilPenjualanSemua() || []).filter((p) => String(p.trxId || '') === String(trxId || '')); if (!b.length) return null;
  return !b.some((p) => p.dibatalkan || p.dikoreksiOleh);
}
/** Satu surat jalan + keadaan turunannya. hariIni = 'YYYY-MM-DD'. */
export function ajKeadaan(sj, hariIni) {
  const dibayar = ajPelunasan(sj.noSJ).reduce((a, m) => a + ajBulat(m.nominal), 0);
  const sisa = sj.bayarDiTempat && sj.status !== 'batal' ? Math.max(0, ajBulat(sj.tagihRp) - dibayar) : 0;
  const nota = ajNotaBerlaku(sj.trxIdJual);
  const lewat = sisa > 0 && String(sj.tanggal || '') < String(hariIni || '');
  return Object.assign({}, sj, { dibayar, sisaTagih: sisa, lewatHari: lewat, notaBerlaku: nota, statusTeks: AJ_STATUS[sj.status] || sj.status,
    notaBatalSuratJalan: nota === false && sj.status !== 'batal', gagalBelumBeres: sj.status === 'gagal' && nota !== false });
}
const ajUrut = (a, b) => String(b.tanggal + ' ' + (b.jam || '')).localeCompare(String(a.tanggal + ' ' + (a.jam || ''))) || (Number(b.id) || 0) - (Number(a.id) || 0);
/**
 * Daftar Antar (Jual › Antar): { jalan (masih di jalan), selesaiHariIni (diterima / gagal / batal hari ini), codBelum (bayar di tempat yang uangnya belum
 * pulang, semua hari), gagal (gagal antar yang notanya belum dibatalkan / diretur) }. saring = nama pembeli / no. surat jalan / pengantar.
 */
export function ajDaftar(hariIni, saring) {
  const k = String(saring || '').trim().toLowerCase();
  const cocok = (x) => !k || [x.namaPelanggan, x.noSJ, x.pengantar, x.alamat].some((v) => String(v || '').toLowerCase().indexOf(k) >= 0);
  const semua = (ambilSuratJalan() || []).map((x) => ajKeadaan(x, hariIni)).filter(cocok).sort(ajUrut);
  return { jalan: semua.filter((x) => x.status === 'berangkat'), selesaiHariIni: semua.filter((x) => x.status !== 'berangkat' && String(x.tanggal) === String(hariIni)),
    codBelum: semua.filter((x) => x.sisaTagih > 0 && x.status !== 'berangkat'), gagal: semua.filter((x) => x.gagalBelumBeres), semua };
}
/** Satu surat jalan menurut id. */
export function ajCari(id) { return (ambilSuratJalan() || []).find((x) => String(x.id) === String(id)) || null; }
/** Surat jalan milik satu nota (trxId) — dipakai struk & pembatalan nota. */
export function ajUntukNota(trxId) { return (ambilSuratJalan() || []).filter((x) => String(x.trxIdJual || '') === String(trxId || '')); }
/**
 * Bayar di tempat yang uangnya BELUM pulang untuk tanggal itu (tutup hari) / sampai tanggal itu (Dasbor): [{ noSJ, nama, pengantar, sisa, tanggal, lewat }].
 * sampai = true → semua tanggal ≤ tanggal itu.
 */
export function ajCodBelumSetor(tanggal, sampai) {
  return (ambilSuratJalan() || []).filter((x) => x.bayarDiTempat && x.status !== 'batal' && (sampai ? String(x.tanggal) <= String(tanggal) : String(x.tanggal) === String(tanggal)))
    .map((x) => ajKeadaan(x, tanggal)).filter((x) => x.sisaTagih > 0 && x.notaBerlaku !== false)
    .map((x) => ({ id: x.id, noSJ: x.noSJ, nama: x.namaPelanggan, pengantar: x.pengantar, sisa: x.sisaTagih, tanggal: x.tanggal, lewat: String(x.tanggal) < String(tanggal), status: x.status }))
    .sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)));
}
/** Kalimat peringatan tutup hari / Dasbor (merah) — '' bila tidak ada. Atas nama pengantarnya. */
export function ajKalimatCod(daftar) {
  const d = daftar || []; if (!d.length) return '';
  const per = {}; d.forEach((x) => { const p = x.pengantar || 'pengantar'; per[p] = (per[p] || 0) + x.sisa; });
  return 'Bayar di tempat belum disetor: ' + Object.keys(per).map((p) => p + ' ' + RP(per[p])).join(' · ') + ' (' + d.length + ' surat jalan: ' + d.slice(0, 3).map((x) => x.noSJ + ' ' + x.nama).join(', ') + (d.length > 3 ? ', …' : '') + ')';
}

// ---------- tandai diterima / gagal / batal ----------
const ajRiwayat = (sj, status, w, tambah) => (Array.isArray(sj.riwayatStatus) ? sj.riwayatStatus : []).concat([Object.assign({ status, pada: w.kini || new Date().toISOString() }, tambah || {})]);
/** Cara tanda terima surat jalan yang sudah diterima: 'kertas' | 'layar' | '' (belum diterima). Kertas = tanpa tanda tangan layar, ada foto lembar. */
export function ajCaraTerima(sj) {
  if (!sj || sj.status !== 'diterima') return '';
  const r = (Array.isArray(sj.riwayatStatus) ? sj.riwayatStatus : []).filter((x) => x && x.status === 'diterima').pop();
  if (r && (r.bukti === 'kertas' || r.bukti === 'layar')) return r.bukti;
  return (sj.buktiTtd || []).length ? 'layar' : 'kertas';
}
/**
 * Tandai DITERIMA. isi = { penerima, catatan, uang (teks rupiah — bayar di tempat), caraUang 'Tunai'|'QRIS', ttdId (id bukti tanda tangan, WAJIB),
 * fotoId (boleh kosong), oleh (nama yang menandai) }. Bayar di tempat & uang > 0 → satu pelunasan piutang (untukSJ, untukFaktur, dibawaOleh pengantar).
 * → { dokumen, patch } atau { tolak }.
 */
export function ajSusunTerima(sj, isi, w) {
  if (!sj) return { tolak: 'Surat jalan tidak ditemukan' };
  if (sj.status !== 'berangkat') return { tolak: 'Surat jalan ini sudah ' + (AJ_STATUS[sj.status] || sj.status) };
  const x = isi || {}; const kertas = x.cara === 'kertas';
  if (kertas && ajKosong(x.fotoId)) return { tolak: 'Foto dulu LEMBAR TOKO yang sudah ditandatangani penerima (tanda tangan di kertas)' };
  if (!kertas && ajKosong(x.ttdId)) return { tolak: 'Minta tanda tangan penerima dulu (kotak tanda tangan)' };
  const penerima = String(x.penerima || '').trim().slice(0, 40);
  const K = ajKeadaan(sj, w.tanggal);
  let uang = 0;
  if (sj.bayarDiTempat) {
    const n = ajRupiahSah(x.uang); if (n === null) return { tolak: 'Uang yang diterima: ketik angka rupiah' };
    if (n > K.sisaTagih) return { tolak: 'Uang yang diterima ' + RP(n) + ' lebih besar dari yang ditagih ' + RP(K.sisaTagih) + ' — betulkan angkanya' };
    uang = n;
  }
  const cara = x.caraUang === 'QRIS' ? 'QRIS' : 'Tunai';
  const dokumen = []; let pelunasanId = null;
  if (uang > 0) {
    pelunasanId = w.idUnik();
    const m = { id: pelunasanId, tipe: 'bayar', namaPelanggan: sj.namaPelanggan, nominal: uang, tanggal: w.tanggal, jam: w.jam, caraBayar: cara, dicatatDi: 'antar',
      untukSJ: String(sj.noSJ), catatan: 'Bayar di tempat — surat jalan ' + sj.noSJ };
    if (!ajKosong(sj.pengantar) && kunciPelanggan(sj.pengantar) !== kunciPelanggan(sj.namaPelanggan)) m.dibawaOleh = String(sj.pengantar).trim();
    if (sj.noFaktur) m.untukFaktur = [String(sj.noFaktur)];
    dokumen.push({ koleksi: 'piutangMutasi', data: m });
  }
  const d = Object.assign({}, sj, { status: 'diterima', riwayatStatus: ajRiwayat(sj, 'diterima', w, { bukti: kertas ? 'kertas' : 'layar' }), penerima, diterimaPada: w.kini || new Date().toISOString(), diterimaTanggal: w.tanggal, diterimaJam: w.jam,
    catatanTerima: String(x.catatan || '').trim().slice(0, 160), buktiTtd: kertas ? [] : [String(x.ttdId)], buktiFoto: ajKosong(x.fotoId) ? [] : [String(x.fotoId)], ditandaiOleh: String(x.oleh || '').slice(0, 40) });
  if (sj.bayarDiTempat) { d.uangDiterima = uang; d.caraUang = cara; if (pelunasanId) d.pelunasanId = pelunasanId; }
  dokumen.push({ koleksi: AJ_KOLEKSI, data: d });
  const sisa = K.sisaTagih - uang;
  const kabar = 'Surat jalan ' + sj.noSJ + ' DITERIMA' + (penerima ? ' oleh ' + penerima : '') + (kertas ? ' · tanda tangan di kertas, foto lembar tersimpan' : ajKosong(x.fotoId) ? ' · tanpa foto' : ' · foto tersimpan')
    + (sj.bayarDiTempat ? (uang > 0 ? ' · uang ' + RP(uang) + ' dibawa ' + (sj.pengantar || 'pengantar') + (sisa > 0 ? ' · masih kurang ' + RP(sisa) + ' (bon)' : ' · LUNAS') : ' · uang BELUM diterima — tetap bon ' + RP(K.sisaTagih)) : '');
  return { dokumen, patch: { kabar, kabarAwas: sj.bayarDiTempat && sisa > 0 } };
}
/** Uang bayar di tempat yang menyusul (surat jalan sudah diterima, uangnya baru dibawa pulang). */
export function ajSusunSetor(sj, isi, w) {
  if (!sj) return { tolak: 'Surat jalan tidak ditemukan' };
  if (!sj.bayarDiTempat) return { tolak: 'Surat jalan ini tidak bayar di tempat' };
  const K = ajKeadaan(sj, w.tanggal); if (!(K.sisaTagih > 0)) return { tolak: 'Tagihan surat jalan ini sudah lunas' };
  const n = ajRupiahSah((isi || {}).uang); if (!n) return { tolak: 'Uang yang disetor: ketik angka rupiah lebih dari 0' };
  if (n > K.sisaTagih) return { tolak: 'Uang ' + RP(n) + ' lebih besar dari sisa tagihan ' + RP(K.sisaTagih) };
  const m = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: sj.namaPelanggan, nominal: n, tanggal: w.tanggal, jam: w.jam, caraBayar: (isi || {}).caraUang === 'QRIS' ? 'QRIS' : 'Tunai',
    dicatatDi: 'antar', untukSJ: String(sj.noSJ), catatan: 'Bayar di tempat (menyusul) — surat jalan ' + sj.noSJ };
  if (!ajKosong(sj.pengantar) && kunciPelanggan(sj.pengantar) !== kunciPelanggan(sj.namaPelanggan)) m.dibawaOleh = String(sj.pengantar).trim();
  if (sj.noFaktur) m.untukFaktur = [String(sj.noFaktur)];
  return { dokumen: [{ koleksi: 'piutangMutasi', data: m }], patch: { kabar: 'Uang ' + RP(n) + ' dari ' + sj.namaPelanggan + ' (surat jalan ' + sj.noSJ + ') dicatat' + (K.sisaTagih - n > 0 ? ' · masih kurang ' + RP(K.sisaTagih - n) : ' · LUNAS'), kabarAwas: false } };
}
/** Tandai GAGAL ANTAR (barang kembali ke toko). Notanya TIDAK diubah di sini — owner membatalkan nota (hari itu) atau mencatat retur. */
export function ajSusunGagal(sj, alasan, w, oleh) {
  if (!sj) return { tolak: 'Surat jalan tidak ditemukan' };
  if (sj.status !== 'berangkat') return { tolak: 'Surat jalan ini sudah ' + (AJ_STATUS[sj.status] || sj.status) };
  const a = String(alasan || '').trim(); if (a.length < 4) return { tolak: 'Tulis alasannya (mis. toko tutup, alamat tidak ketemu)' };
  const d = Object.assign({}, sj, { status: 'gagal', riwayatStatus: ajRiwayat(sj, 'gagal', w), alasanGagal: a.slice(0, 160), ditandaiOleh: String(oleh || '').slice(0, 40) });
  return { dokumen: [{ koleksi: AJ_KOLEKSI, data: d }], patch: { kabar: 'Surat jalan ' + sj.noSJ + ' GAGAL ANTAR — barangnya kembali. Owner: batalkan notanya (hari ini) atau catat retur.', kabarAwas: true } };
}
/** Owner membatalkan surat jalan (nota tetap; mis. pembeli mengambil sendiri). Pembatalan nota memakai ajBatalUntukNota di batch yang sama. */
export function ajSusunBatal(sj, alasan, w) {
  if (!sj) return { tolak: 'Surat jalan tidak ditemukan' };
  if (sj.status === 'batal') return { tolak: 'Surat jalan ini sudah dibatalkan' };
  const a = String(alasan || '').trim(); if (a.length < 4) return { tolak: 'Tulis alasan membatalkan surat jalan' };
  return { dokumen: [{ koleksi: AJ_KOLEKSI, data: Object.assign({}, sj, { status: 'batal', riwayatStatus: ajRiwayat(sj, 'batal', w), batalPada: w.kini || new Date().toISOString(), alasanBatal: a.slice(0, 160) }) }],
    patch: { kabar: 'Surat jalan ' + sj.noSJ + ' dibatalkan — notanya tidak berubah', kabarAwas: false } };
}
/** Surat jalan nota yang dibatalkan ikut batal (dokumen tambahan untuk batch pembatalan nota). */
export function ajBatalUntukNota(trxId, w) {
  return ajUntukNota(trxId).filter((x) => x.status !== 'batal').map((sj) => ({ koleksi: AJ_KOLEKSI, data: Object.assign({}, sj, { status: 'batal', riwayatStatus: ajRiwayat(sj, 'batal', w),
    batalPada: w.kini || new Date().toISOString(), alasanBatal: 'notanya dibatalkan' }) }));
}

// ---------- bukti terima (tanda tangan & foto) ----------
/** Pisah data URL gambar base64 → { jenis, base64 } atau null. */
export function ajPisahDataUrl(url) { const m = /^data:(image\/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)$/.exec(String(url || '')); return m ? { jenis: m[1], base64: m[2] } : null; }
export function ajByte(b64) { const s = String(b64 || ''); if (!s) return 0; const pad = s.endsWith('==') ? 2 : s.endsWith('=') ? 1 : 0; return Math.floor(s.length * 3 / 4) - pad; }
/** Dokumen satu bukti: jenisBukti 'ttd' | 'foto'; gambar = { jenis, base64, lebar, tinggi } (foto: hasil pengecil foto bon; ttd: PNG kanvas). */
export function ajSusunBukti(sj, jenisBukti, gambar, w, isiBukti) {
  if (!sj || !sj.id) return { tolak: 'Surat jalan tidak ditemukan' };
  if (jenisBukti !== 'ttd' && jenisBukti !== 'foto') return { tolak: 'Jenis bukti tidak dikenal' };
  if (!gambar || gambar.tolak) return { tolak: (gambar && gambar.tolak) || 'Belum ada gambar' };
  if (AJ_JENIS_BUKTI.indexOf(String(gambar.jenis || '')) < 0 || !gambar.base64) return { tolak: 'Gambar tidak terbaca' };
  const byte = ajByte(gambar.base64); if (byte > AJ_BUKTI_BATAS) return { tolak: 'Gambar ' + Math.round(byte / 1024) + ' KB lebih dari ' + Math.round(AJ_BUKTI_BATAS / 1024) + ' KB — kecilkan dulu' };
  return { data: { id: String(w.idUnik()), idSJ: String(sj.id), noSJ: String(sj.noSJ || ''), jenisBukti, tanggal: w.tanggal, jam: w.jam, jenis: gambar.jenis, base64: gambar.base64, byte,
    lebar: ajBulat(gambar.lebar), tinggi: ajBulat(gambar.tinggi), isiBukti: isiBukti === 'kertas' && jenisBukti === 'foto' ? 'kertas' : jenisBukti === 'ttd' ? 'layar' : 'barang' } };
}
/** Goresan tanda tangan cukup? (titik goresan ≥ 12 — ketukan sekali bukan tanda tangan) */
export const ajTtdCukup = (nTitik) => (Number(nTitik) || 0) >= 12;

// ---------- retur: ongkir tidak ikut dikembalikan ----------
/**
 * Dasar retur satu baris nota yang notanya membawa ongkir (rtDasarNota beku menghitung (hargaTotal − pembulatan) ÷ jumlah dan memprorata potongan atas
 * subtotal yang MEMUAT ongkir). dasarFn = rtDasarNota (atau pembungkus bon-nya). Tanpa ongkir di nota itu → dasarFn apa adanya.
 */
export function ajDasarRetur(t, dasarFn) {
  if (!t) return dasarFn(t);
  const kunci = rtKunciNota(t); const senota = (ambilPenjualan() || []).filter((x) => rtKunciNota(x) === kunci);
  const ong = ajOngkirNota(senota); if (!ong) return dasarFn(t);
  const t2 = Object.assign({}, t, { hargaTotal: (t.hargaTotal || 0) - ajBulat(t.ongkirAntar) }); delete t2.ongkirAntar;
  const d = dasarFn(t2); if (!d || !d.ok) return d;
  const sub = senota.filter((x) => (x.hargaTotal || 0) > 0).reduce((a, x) => a + (x.hargaTotal || 0) - (x.pembulatan || 0), 0) - ong;
  const per = twSatuanDibayar(t2, d.potNota, sub); if (!(per > 0)) return d;
  return Object.assign({}, d, { perSatuan: per, ongkirNota: ong, dasar: String(d.dasar || '') + ' · ongkir antar ' + RP(ong) + ' tidak ikut' });
}

// ---------- laporan & kendali biaya ----------
/** Ongkir yang ditagih di rentang tanggal [dari, sampai] (nota berlaku): { rp, nNota }. */
export function ajOngkirRentang(dari, sampai) {
  let rp = 0; const nota = {};
  (ambilPenjualan() || []).forEach((p) => { const o = ajBulat(p.ongkirAntar); if (!o || !p.tanggal || p.tanggal < dari || p.tanggal > sampai) return; rp += o; nota[String(p.trxId || p.id)] = 1; });
  return { rp, nNota: Object.keys(nota).length };
}
/** Ringkas satu surat jalan untuk baris daftar. */
export function ajRingkas(x) {
  return x.noSJ + ' · ' + (x.namaPelanggan || 'tanpa nama') + ' · ' + tanggalPendek(x.tanggal) + ' ' + (x.jam || '') + (x.pengantar ? ' · ' + x.pengantar : '') + (x.ongkir ? ' · ongkir ' + RP(x.ongkir) : '');
}

// ---------- cetak surat jalan ----------
/**
 * Garis cetak surat jalan TANPA harga barang (bentuk garis susunStruk: { kiri, kanan, tebal, tengah } / { garis: true }) — printer tablet gaya teks
 * (inti/printer.js) & dialog cetak memakai garis yang sama. kop = { nama, alamat, telp } (setelan struk).
 */
export function ajGarisCetak(sj, kop, lembar) {
  const g = []; const b = (kiri, kanan, o) => g.push(Object.assign({ kiri: String(kiri || ''), kanan: kanan === undefined || kanan === null ? '' : String(kanan) }, o || {}));
  const K = kop || {};
  if (K.nama) b(String(K.nama).toUpperCase(), '', { tebal: true, tengah: true }); if (K.alamat) b(K.alamat, '', { tengah: true }); if (K.telp) b('Telp ' + K.telp, '', { tengah: true });
  g.push({ garis: true }); b('SURAT JALAN', '', { tebal: true, tengah: true }); b('No. ' + sj.noSJ, '', { tengah: true });
  if (lembar === 'pembeli') b('LEMBAR PEMBELI', '', { tebal: true, tengah: true }); else if (lembar === 'toko') b('LEMBAR TOKO', '', { tebal: true, tengah: true });
  g.push({ garis: true });
  b('Tanggal: ' + tanggalPendek(sj.tanggal) + ' ' + (sj.jam || ''));
  b('Kepada : ' + (sj.namaPelanggan || '-'), '', { tebal: true });
  if (sj.alamat) b('Alamat : ' + sj.alamat);
  if (sj.pengantar) b('Antar  : ' + sj.pengantar + (sj.kendaraan ? ' · ' + sj.kendaraan : ''));
  if (sj.noFaktur) b('Faktur : ' + sj.noFaktur);
  if (sj.noPO) b('No. PO : ' + sj.noPO);
  g.push({ garis: true });
  (sj.isi || []).forEach((x) => b(x.nama, String(x.jumlah).replace('.', ',') + ' ' + x.satuan));
  g.push({ garis: true });
  if (sj.uangMuka > 0) b('Uang muka sudah masuk', RP(sj.uangMuka));
  if (sj.bayarDiTempat) b('TAGIH DI TEMPAT', RP(sj.tagihRp), { tebal: true }); else b('Sudah dibayar / bon di toko');
  if (sj.catatan) b('Catatan: ' + sj.catatan);
  g.push({ garis: true }); b('Diterima oleh,'); b(''); b(''); b('(.............................)');
  if (lembar === 'toko') { b('Nama terang & jam terima:'); b(''); b('(.............................)'); g.push({ garis: true });
    b('WAJIB ditandatangani penerima.', '', { tebal: true }); b('Bawa pulang ke toko, lalu foto'); b('di tablet: Antar > diterima.'); }
  else if (lembar === 'pembeli') { g.push({ garis: true }); b('Disimpan pembeli.', '', { tengah: true }); }
  return g;
}
/** Dua lembar cetak surat jalan (keputusan owner 18 Nov): [LEMBAR PEMBELI, LEMBAR TOKO]. WhatsApp tetap satu teks tanpa nama lembar. */
export function ajLembarCetak(sj, kop) {
  return [ajGarisCetak(sj, kop, 'pembeli'), ajGarisCetak(sj, kop, 'toko')];
}
/** Teks satu garis cetak selebar kolom kertas (32 = 58 mm, 48 = 80 mm) — dialog cetak & WhatsApp. Angka rata kanan, tidak pernah terpenggal. */
export function ajTeksCetak(garis, lebar) {
  const L = Number(lebar) || 32; const out = [];
  (garis || []).forEach((x) => {
    if (x.garis) { out.push('-'.repeat(L)); return; }
    if (!x.kanan) { out.push(x.tengah && x.kiri.length < L ? ' '.repeat(Math.floor((L - x.kiri.length) / 2)) + x.kiri : x.kiri); return; }
    const sisa = L - x.kiri.length - x.kanan.length;
    if (sisa > 0) out.push(x.kiri + ' '.repeat(sisa) + x.kanan); else { out.push(x.kiri); out.push(' '.repeat(Math.max(0, L - x.kanan.length)) + x.kanan); }
  });
  return out.join('\n');
}
