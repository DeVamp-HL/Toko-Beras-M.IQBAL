// LOGIKA MODUL PAJAK (putaran 24, 24 Sep 2026), tanpa DOM — khusus owner (layar Laporan › Pajak; rules: pajakOmzetLuar & pajakSetoran owner saja).
// Sistem TAHU posisi pajaknya sendiri: menghitung perkiraan PPh final per bulan, mengingatkan, menyimpan bukti setoran. TIDAK membayar, TIDAK melapor,
// TIDAK memberi nasihat pajak — setiap angka berlabel PJ_LABEL. Dijaga alat-uji/uji_pajak_baru.py. Sumber aturan: docs/sumber-aturan-pajak.md.
//   · omzet sistem per bulan = mesin laba (hitungLabaRentang → omzetPenuh), SATU sumber — DK3 (rekapOmzet) memanggil pjOmzetSistem yang sama;
//   · profil wajib pajak = field TAMBAHAN di aturanToko/rekapOmzet; SEMUA penulis dokumen itu lewat pjGabungRekap (membawa semua field, termasuk yang tidak dikenalnya);
//   · omzet di luar sistem (pajakOmzetLuar) = ketikan owner, tampil beda dari hitungan; kosong ≠ nol;
//   · setoran (pajakSetoran) memotret omzet & perkiraan saat dicatat → angka yang berubah sesudahnya DISEBUT, tidak diam.
// Nama pembantu diprefiks `pj` (bundel uji jsc satu lingkup).
import { hitungLabaRentang } from '../mesin/beku.js';
import { bulanDari, namaBulanPanjang } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, cacheMentah, kunciSampai } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong } from './uang-logika.js';

export const PJ_LABEL = 'perkiraan — bukan nasihat pajak';
export const PJ_ANGGAPAN_OP = 'hitungan dengan anggapan orang pribadi (jenis wajib pajak belum diketahui — tanya pemilik lama)';
export const PJ_JENIS_WP = [['belumDiketahui', 'Belum diketahui (tanya pemilik lama)'], ['orangPribadi', 'Orang pribadi'], ['badan', 'Badan']].map((x) => ({ id: x[0], nama: x[1] }));
export const PJ_STATUS_PKP = [['belumDiketahui', 'Belum diketahui'], ['bukan', 'Bukan PKP'], ['pkp', 'PKP']].map((x) => ({ id: x[0], nama: x[1] }));
// sumber omzet ketikan: catatanLama = bulan sebelum sistem ini ada; usahaLain = usaha lain milik wajib pajak YANG SAMA (ikut PPh & ambang);
// usahaPasangan = usaha pasangan — ikutnya menurut statusPasangan di profil (pjAturanPasangan): PH/MT = batas Rp500 juta masing-masing, jadi hanya ikut ambang
// Rp4,8 miliar; satu kesatuan / belum diketahui = ikut PPh (satu batas Rp500 juta berdua) DAN ambang.
export const PJ_SUMBER_LUAR = [['catatanLama', 'Catatan lama (sebelum sistem ini)', 'ikut PPh & ambang'], ['usahaLain', 'Usaha lain wajib pajak yang sama', 'ikut PPh & ambang'], ['usahaPasangan', 'Usaha pasangan', 'ikut menurut status pasangan di profil']].map((x) => ({ id: x[0], nama: x[1], ket: x[2] }));
// ---- STATUS PASANGAN (owner 24 Sep). PMK 164/2023 Pasal 6 ayat (5), teks dibaca: bagian Rp500 juta yang tidak dikenai "diberlakukan untuk masing-masing suami
// dan istri" HANYA bila (a) perjanjian pemisahan harta & penghasilan tertulis (PH) atau (b) istri memilih menjalankan hak & kewajiban pajaknya sendiri (MT);
// Lampiran contoh 4 (MT) memberi masing-masing Rp500 juta. Satu kesatuan TIDAK disebut → usaha pasangan ikut batas Rp500 juta yang SAMA. Batas Rp4,8 miliar:
// omzet suami-istri DIGABUNG, termasuk PH & MT (PP 20/2026 Pasal 58 ayat 2–3, artikel DJP 8 Jun 2026). Belum diketahui → anggapan paling hati-hati: satu batas berdua.
export const PJ_STATUS_PASANGAN = [['belumDiketahui', 'Belum diketahui'], ['satuKesatuan', 'Satu kesatuan'], ['pisahHarta', 'Pisah harta tertulis (PH)'], ['memilihTerpisah', 'Istri memilih sendiri (MT)']].map((x) => ({ id: x[0], nama: x[1] }));
export const PJ_TANDA_BELUM = '[BELUM TERVERIFIKASI]';
/** → { batasSendiri: usaha pasangan punya batas Rp500 juta sendiri (hanya ikut ambang), teks, anggapan, belumTerverifikasi }. */
export function pjAturanPasangan(status) {
  if (status === 'pisahHarta' || status === 'memilihTerpisah') return { batasSendiri: true, anggapan: false, belumTerverifikasi: '',
    teks: (status === 'pisahHarta' ? 'Pisah harta tertulis' : 'Istri memilih sendiri') + ': batas Rp500 juta berlaku masing-masing (PMK 164/2023 Pasal 6 ayat 5) — usaha pasangan tidak ikut PPh di sini, hanya ikut batas Rp4,8 miliar (digabung, PP 20/2026 Pasal 58)' };
  if (status === 'satuKesatuan') return { batasSendiri: false, anggapan: false, belumTerverifikasi: 'dasar penggabungan satu kesatuan (UU PPh Pasal 8 ayat 1) belum dibaca langsung; Pasal 6 ayat 5 hanya memberi batas masing-masing untuk PH & MT',
    teks: 'Satu kesatuan: Pasal 6 ayat 5 tidak berlaku — usaha pasangan ikut omzet & SATU batas Rp500 juta berdua, dan ikut batas Rp4,8 miliar' };
  return { batasSendiri: false, anggapan: true, belumTerverifikasi: '',
    teks: 'Status pasangan belum diketahui — hitungan memakai anggapan paling hati-hati: satu batas Rp500 juta berdua (usaha pasangan ikut PPh & batas Rp4,8 miliar)' };
}
export const PJ_AMBANG = [70, 85, 95, 100];
// Aturan yang diisi tombol "Pakai aturan PP 55/2022 jo. PP 20/2026" — hanya bila owner menekannya; bawaan = belum diatur.
export const PJ_ATURAN = { tarifPerMil: 5, batasBebas: 500000000, batasOmzet: 4800000000,
  teks: 'PP 55/2022 jo. PP 20/2026 (ditetapkan & berlaku 22 Apr 2026): tarif 0,5 %; bagian omzet s.d. Rp500 juta setahun tidak dikenai (orang pribadi, PMK 164/2023 Pasal 6 ayat 3–4); batas omzet Rp4,8 miliar setahun' };
// Klaim → sumber resmi → tanggal lihat. Yang belum terverifikasi tampil [BELUM TERVERIFIKASI] di layar & cetakan, bukan sebagai fakta.
export const PJ_SUMBER = [
  ['PP 20/2026 ditetapkan, diundangkan & berlaku 22 April 2026', 'https://peraturan.bpk.go.id/Details/349415/pp-no-20-tahun-2026', true],
  ['Jangka waktu tertentu tarif 0,5 % untuk orang pribadi dihapus (Pasal 59 dihapus)', 'https://pajak.go.id/sites/default/files/2026-06/Peraturan%20Pemerintah%20nomor%2020%20Tahun%202026.pdf', true],
  ['Batas omzet Rp4,8 miliar setahun; omzet suami-istri digabung untuk batas ini, termasuk pisah harta (PH) & istri memilih sendiri (MT) — PP 20/2026 Pasal 58 ayat (2)–(3)', 'https://pajak.go.id/en/node/119991', true],
  ['Bagian peredaran bruto s.d. Rp500 juta setahun tidak dikenai, dihitung kumulatif sejak masa pajak pertama, seluruh tempat usaha — PMK 164/2023 Pasal 6 ayat (3)–(4)', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', true],
  ['Batas Rp500 juta berlaku masing-masing suami & istri HANYA bila pisah harta tertulis (PH) atau istri memilih sendiri (MT) — PMK 164/2023 Pasal 6 ayat (5) huruf a–b; Lampiran contoh 4', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', true],
  ['Suami-istri satu kesatuan: usaha pasangan ikut wajib pajak yang sama → satu batas Rp500 juta berdua (UU PPh Pasal 8 ayat 1 belum dibaca langsung; hitungan memakai anggapan paling hati-hati)', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', false],
  ['Peredaran bruto = imbalan SEBELUM dikurangi potongan penjualan, potongan tunai, dan/atau potongan sejenis — PMK 164/2023 Pasal 6 ayat (2)', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', true],
  ['Setor paling lambat tanggal 15 bulan berikutnya — PMK 164/2023 Pasal 7 ayat (2)', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', true],
  ['Setoran bervalidasi NTPN dianggap SPT Masa PPh Unifikasi, per tanggal validasi — PMK 164/2023 Pasal 7 ayat (5)', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', true],
  ['Kode billing lewat Coretax: KAP-KJS 411128-420 (PPh Final UMKM bayar sendiri)', 'https://www.pajak.go.id/en/node/116821', true],
  ['NTPN = 16 karakter gabungan angka & huruf (artikel DJP 2020, sebelum Coretax)', 'https://pajak.go.id/en/node/111191', false],
  ['Pembulatan PPh final tidak ditemukan di PMK 164/2023 — sistem membulatkan ke BAWAH ke rupiah penuh', 'https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf', false],
].map((x) => ({ klaim: x[0], url: x[1], lihat: '2026-09-24', terverifikasi: x[2] }));

const PJ_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const pjKey = (iso) => String(iso).slice(0, 7);
const pjGeser = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; return new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)).toISOString().slice(0, 7); };
const pjHariKe = (iso) => Math.round(new Date(iso + 'T00:00:00Z').getTime() / 86400000);
const pjTambahHari = (iso, n) => new Date((pjHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
const pjPendek = (key) => PJ_BLN[Number(key.slice(5, 7)) - 1];
const pjAngkaAtauNull = (v) => (v === undefined || v === null || v === '' || !isFinite(Number(v)) ? null : Math.round(Number(v)));
/** Teks bebas tidak boleh memuat NIK / NPWP / nomor rekening (keputusan owner): deretan ≥ 10 angka yang bukan rupiah bertitik ribuan → ditolak. */
export function pjAdaNomorPribadi(teks) {
  return (String(teks || '').match(/[\d][\d.\-\s]{8,}[\d]/g) || []).some((t) => { const x = t.trim(); if (/^\d{1,3}(\.\d{3})+$/.test(x)) return false; return x.replace(/\D/g, '').length >= 10; });
}
const PJ_TOLAK_NOMOR = 'Jangan menyimpan NIK, NPWP, atau nomor rekening di sini — cukup nama. (Deretan 10 angka atau lebih ditolak.)';

// ==================== omzet sistem: SATU sumber ====================
/** Omzet satu bulan dari mesin laba (penjualan yang masih berlaku, dikurangi retur). Dipakai layar Pajak DAN DK3. */
export function pjOmzetSistem(key) { const L = hitungLabaRentang((t) => !!t && bulanDari(t) === key); return { omzet: L.omzetPenuh, n: L.jumlahTrx }; }
/** Tanggal nota pertama di sistem (penjualan apa pun) — bulan sebelumnya TIDAK ada di sistem; bulan pertama bisa terisi sebagian. */
export function pjAwalSistem() { let p = ''; ambilPenjualanSemua().forEach((d) => { if (d.tanggal && (!p || d.tanggal < p)) p = d.tanggal; }); return p; }

// ==================== profil (field tambahan di aturanToko/rekapOmzet) ====================
export const pjDokRekap = () => ugAturDok('rekapOmzet');
/** Profil & aturan pajak terbaca. batasOmzet (lama) = BATAS ATAS Rp4,8 miliar — satu angka, tidak ada batasAtas terpisah (lihat BACA-DULU). */
export function pjProfil() {
  const d = pjDokRekap() || {}; const jenis = PJ_JENIS_WP.some((j) => j.id === d.jenisWp) ? d.jenisWp : 'belumDiketahui'; const pkp = PJ_STATUS_PKP.some((j) => j.id === d.statusPkp) ? d.statusPkp : 'belumDiketahui';
  const ang = (v) => { const n = pjAngkaAtauNull(v); return n !== null && n >= 0 ? n : null; };
  const pasangan = PJ_STATUS_PASANGAN.some((j) => j.id === d.statusPasangan) ? d.statusPasangan : 'belumDiketahui';
  return { wpAtasNama: String(d.wpAtasNama || ''), jenisWp: jenis, statusPkp: pkp, statusPasangan: pasangan, tahunMulaiTarifFinal: ang(d.tahunMulaiTarifFinal), omzetTahunLalu: ang(d.omzetTahunLalu), batasBebas: ang(d.batasBebas),
    batasOmzet: ang(d.batasOmzet) || 0, tarifPerMil: ang(d.tarifPerMil) || 0, tanggalLapor: isFinite(Number(d.tanggalLapor)) && Number(d.tanggalLapor) >= 1 && Number(d.tanggalLapor) <= 28 ? Math.round(Number(d.tanggalLapor)) : 15,
    sumberAturan: d.sumberAturan && typeof d.sumberAturan === 'object' ? { teks: String(d.sumberAturan.teks || ''), tanggal: String(d.sumberAturan.tanggal || '') } : null, ada: !!pjDokRekap() };
}
/**
 * SATU-SATUNYA cara menyusun isi aturanToko/rekapOmzet (DK3 susunAturRekap & susunTandaLapor, profil, tombol aturan): dokumen yang ada disalin UTUH
 * (termasuk field yang tidak dikenal penulisnya), lalu hanya `ubah` yang ditimpa. Tanpa ini tiap penulis lama menghapus profil diam-diam.
 */
export function pjGabungRekap(ubah, w) {
  const lama = pjDokRekap() || {}; const d = Object.assign({}, lama, ubah || {}, { id: 'rekapOmzet', tanggal: w.tanggal, jam: w.jam });
  if (!d.lapor || typeof d.lapor !== 'object') d.lapor = {}; Object.keys(d).forEach((k) => { if (d[k] === undefined) delete d[k]; }); return d;
}
export function susunProfilPajak(isi, w) {
  const P = pjProfil(); const u = {};
  if (isi.wpAtasNama !== undefined) { const n = String(isi.wpAtasNama || '').trim().slice(0, 60); if (pjAdaNomorPribadi(n)) return { tolak: PJ_TOLAK_NOMOR }; u.wpAtasNama = n; }
  if (isi.jenisWp !== undefined) { if (!PJ_JENIS_WP.some((j) => j.id === isi.jenisWp)) return { tolak: 'Jenis wajib pajak tidak dikenal' }; u.jenisWp = isi.jenisWp; }
  if (isi.statusPkp !== undefined) { if (!PJ_STATUS_PKP.some((j) => j.id === isi.statusPkp)) return { tolak: 'Status PKP tidak dikenal' }; u.statusPkp = isi.statusPkp; }
  if (isi.statusPasangan !== undefined) { if (!PJ_STATUS_PASANGAN.some((j) => j.id === isi.statusPasangan)) return { tolak: 'Status pasangan tidak dikenal' }; u.statusPasangan = isi.statusPasangan; }
  const th = Number(String(w.tanggal).slice(0, 4));
  const angka = (k, min, maks, nama) => { if (isi[k] === undefined) return ''; if (ugKosong(isi[k])) { u[k] = null; return ''; } const n = ugAngka(isi[k]); if (!(n >= min && n <= maks)) return nama; u[k] = Math.round(n); return ''; };
  const salah = angka('tahunMulaiTarifFinal', 2000, th, 'Tahun mulai tarif final: 2000–' + th + ' (kosongkan kalau tidak tahu)') || angka('omzetTahunLalu', 0, 1e13, 'Omzet tahun lalu tidak boleh minus (kosongkan kalau tidak tahu — kosong ≠ nol)')
    || angka('batasBebas', 0, 1e13, 'Batas bebas tidak boleh minus') || angka('batasOmzet', 0, 1e13, 'Batas omzet tidak boleh minus') || angka('tarifPerMil', 0, 1000, 'Tarif ditulis per seribu: 0–1000 (5 = 0,5 %)');
  if (salah) return { tolak: salah };
  if (u.batasOmzet === null) u.batasOmzet = 0; if (u.tarifPerMil === null) u.tarifPerMil = 0;   // field lama DK3: 0 = belum diatur (bentuk lama dipertahankan)
  const jenis = u.jenisWp || P.jenisWp;
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap(u, w) }], patch: { kabar: 'Profil pajak tersimpan' + (jenis === 'belumDiketahui' ? ' — ' + PJ_ANGGAPAN_OP : jenis === 'badan' ? ' — badan: kolom PPh tidak dihitung, tanyakan konsultan' : '') + '. ' + PJ_LABEL + '.', kabarAwas: false, drafPj: null } };
}
/** Tombol "Pakai aturan PP 55/2022 jo. PP 20/2026": tarif 5‰, batas bebas Rp500 juta, batas atas Rp4,8 miliar + catatan sumbernya. Tiap angka tetap bisa diubah. */
export function susunPakaiAturan(w) {
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: PJ_ATURAN.tarifPerMil, batasBebas: PJ_ATURAN.batasBebas, batasOmzet: PJ_ATURAN.batasOmzet, sumberAturan: { teks: PJ_ATURAN.teks, tanggal: w.tanggal } }, w) }],
    patch: { kabar: 'Aturan terisi: tarif 0,5 %, bebas s.d. ' + RP(PJ_ATURAN.batasBebas) + ', batas ' + RP(PJ_ATURAN.batasOmzet) + ' — sumbernya tercatat. Tiap angka bisa lu ubah. ' + PJ_LABEL + '.', kabarAwas: false } };
}

// ==================== omzet di luar sistem (pajakOmzetLuar) ====================
export const pjOmzetLuarSemua = () => cacheMentah('pajakOmzetLuar');
export function pjOmzetLuar(key, sumber) { const d = pjOmzetLuarSemua().find((x) => String(x.id) === key + '|' + sumber); return d ? pjAngkaAtauNull(d.jumlah) : null; }
export function susunOmzetLuar(isi, w) {
  const bulan = String(isi.bulan || ''); const sumber = String(isi.sumber || ''); const kini = pjKey(w.tanggal); const ket = String(isi.keterangan || '').trim().slice(0, 120);
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(bulan)) return { tolak: 'Pilih bulannya dulu' }; if (bulan > kini) return { tolak: 'Bulan depan belum ada omzetnya' };
  if (!PJ_SUMBER_LUAR.some((s) => s.id === sumber)) return { tolak: 'Pilih sumbernya: catatan lama, usaha lain, atau usaha pasangan' };
  if (ugKosong(isi.jumlah)) return { tolak: 'Ketik jumlahnya — kosong artinya belum diisi, bukan nol. Kalau memang nol, ketik 0' };
  const n = ugAngka(isi.jumlah); if (!(n >= 0)) return { tolak: 'Omzet tidak boleh minus' }; if (pjAdaNomorPribadi(ket)) return { tolak: PJ_TOLAK_NOMOR };
  if (sumber === 'catatanLama') {
    const awal = pjAwalSistem(); const kAwal = awal ? pjKey(awal) : null;
    if (kAwal && bulan > kAwal) return { tolak: pjNama(bulan) + ' sudah punya penjualan di sistem — catatan lama ditolak supaya omzet tidak terhitung dua kali' };
    if (kAwal && bulan === kAwal) { if (awal.slice(8, 10) === '01') return { tolak: pjNama(bulan) + ' tercatat di sistem sejak tanggal 1 — catatan lama ditolak supaya omzet tidak terhitung dua kali' };
      if (!ket) return { tolak: 'Sistem baru mencatat ' + pjNama(bulan) + ' mulai ' + tanggalPendek(awal) + '. Catatan lama bulan ini HANYA untuk tanggal 1–' + (Number(awal.slice(8, 10)) - 1) + ' — tulis itu di keterangan' }; }
  }
  return { dokumen: [{ koleksi: 'pajakOmzetLuar', data: { id: bulan + '|' + sumber, bulan, sumber, jumlah: Math.round(n), keterangan: ket } }],
    patch: { kabar: pjNama(bulan) + ' · ' + (PJ_SUMBER_LUAR.find((s) => s.id === sumber) || {}).nama + ': ' + RP(Math.round(n)) + ' diketik owner — tampil terpisah dari hitungan sistem', kabarAwas: false, drafLuar: null } };
}
export function susunHapusOmzetLuar(id, yakin) {
  const d = pjOmzetLuarSemua().find((x) => String(x.id) === String(id)); if (!d) return { tolak: 'Isian itu sudah tidak ada' };
  if (!yakin) return { tolak: 'Hapus isian ' + pjNama(d.bulan) + ' ' + RP(d.jumlah) + '? Bulan itu kembali "—" (belum diisi). Ketuk sekali lagi', perluYakin: true };
  return { dokumen: [], hapus: [{ koleksi: 'pajakOmzetLuar', id: String(id) }], patch: { kabar: 'Isian ' + pjNama(d.bulan) + ' dihapus — bulan itu kembali belum diisi', kabarAwas: false, yakinPj: null } };
}
const pjNama = (key) => namaBulanPanjang(key + '-01');

// ==================== omzet SEBELUM potongan nota (tampilan saja — mesin beku tidak disentuh) ====================
/**
 * PMK 164/2023 Pasal 6 ayat (2): peredaran bruto = SEBELUM potongan penjualan. Omzet mesin = sesudah potongan nota & retur. Per bulan, dari baris penjualan yang
 * masih berlaku (baris yang sama yang dihitung mesin): potongan nota (potonganTransaksi) + tawar di BAWAH harga daftar (hargaAsliSatuan + negoSelisih < 0;
 * satuannya beda per jalur, jadi dihitung lewat RASIO harga daftar / harga jadi). Tawar ke atas bukan potongan. Retur tetap mengurangi kedua angka; unit bonus tidak dihitung.
 */
export function pjPotonganBulan(key) {
  let nota = 0, tawar = 0, n = 0, tanpaDaftar = 0;
  ambilPenjualan().forEach((p) => {
    if (!p.tanggal || bulanDari(p.tanggal) !== key || p.penggantiRetur) return;
    const pot = Math.max(0, Math.round(Number(p.potonganTransaksi) || 0)); const dasar = (Number(p.hargaTotal) || 0) - (Number(p.pembulatan) || 0) + pot;
    const asli = Number(p.hargaAsliSatuan) || 0, sel = Number(p.negoSelisih) || 0; if (!(asli > 0)) tanpaDaftar += 1;
    const tw = asli > 0 && sel < 0 && asli + sel > 0 && dasar > 0 ? Math.round(dasar * -sel / (asli + sel)) : 0;
    if (pot || tw) n += 1; nota += pot; tawar += tw;
  });
  return { nota, tawar, jumlah: nota + tawar, n, tanpaDaftar };
}

// ==================== hitungan per bulan ====================
/**
 * Satu tahun pajak, Jan → bulan berjalan (tahun lalu: 12 bulan). Per bulan: omzet sistem / luar, kumulatif, bagian yang kena, perkiraan PPh, setoran, status.
 *   kum_sebelum = kumulatif s.d. akhir bulan sebelumnya · kum_sesudah = + bulan ini · kena = max(0, kum_sesudah − max(kum_sebelum, batasBebas)) · pph = ⌊kena × tarif / 1000⌋
 * Kumulatif PPh = sistem + catatan lama + usaha lain WP yang sama (+ usaha pasangan bila satu kesatuan / belum diketahui); ambang Rp4,8 miliar = itu + usaha pasangan.
 * sebelumPotongan = omzet mesin + potongan nota & tawar (pjPotonganBulan) — angka kedua untuk konsultan, tidak dipakai menghitung.
 */
export function pjTahun(tahun, kini) {
  const iso = hariIniIso(kini || new Date(Date.now())); const kiniKey = pjKey(iso); const th = Number(tahun || kiniKey.slice(0, 4)); const P = pjProfil();
  const awal = pjAwalSistem(); const kAwal = awal ? pjKey(awal) : null; const hitung = P.jenisWp !== 'badan' && P.tarifPerMil > 0; const bebas = P.batasBebas || 0; const AP = pjAturanPasangan(P.statusPasangan);
  const setoran = pjSetoranSemua(); const akhirBulan = th < Number(kiniKey.slice(0, 4)) ? 12 : th > Number(kiniKey.slice(0, 4)) ? 0 : Number(kiniKey.slice(5, 7));
  const daftar = []; let kum = 0, kumGabung = 0, lengkapSejauhIni = true, kosong = 0;
  for (let m = 1; m <= akhirBulan; m++) {
    const key = th + '-' + String(m).padStart(2, '0'); const adaSistem = !!kAwal && key >= kAwal; const S = adaSistem ? pjOmzetSistem(key) : { omzet: null, n: 0 };
    const sebagian = !!kAwal && key === kAwal && awal.slice(8, 10) !== '01';
    const lama = pjOmzetLuar(key, 'catatanLama'), lain = pjOmzetLuar(key, 'usahaLain'), pasangan = pjOmzetLuar(key, 'usahaPasangan');
    const lengkap = adaSistem ? (!sebagian || lama !== null) : lama !== null; if (!lengkap) { kosong += 1; lengkapSejauhIni = false; }
    const pasanganPph = AP.batasSendiri ? 0 : (pasangan || 0); const omzet = (S.omzet || 0) + (lama || 0) + (lain || 0) + pasanganPph; const gabung = omzet + (AP.batasSendiri ? (pasangan || 0) : 0);
    const PT = S.omzet === null ? null : pjPotonganBulan(key); const sebelumPotongan = S.omzet === null ? null : S.omzet + PT.jumlah;
    const kumSebelum = kum; kum += omzet; kumGabung += gabung; const kena = Math.max(0, kum - Math.max(kumSebelum, bebas));
    const pph = hitung ? Math.floor(kena * P.tarifPerMil / 1000) : null;
    const tempo = pjGeser(key, 1) + '-' + String(P.tanggalLapor).padStart(2, '0'); const berjalan = key === kiniKey;
    const setor = setoran.filter((s) => s.masaPajak === key); const jumlahSetor = setor.reduce((a, s) => a + (Number(s.jumlah) || 0), 0);
    const potret = setor.length ? setor[setor.length - 1] : null; const adaPotret = potret && potret.omzetSaatSetor !== null && potret.omzetSaatSetor !== undefined && Number.isFinite(Number(potret.omzetSaatSetor));
    const berubah = adaPotret && Math.round(Number(potret.omzetSaatSetor)) !== omzet
      ? { omzet: omzet - Math.round(Number(potret.omzetSaatSetor)), pph: pph === null || potret.pphPerkiraanSaatSetor === null || potret.pphPerkiraanSaatSetor === undefined ? null : pph - Math.round(Number(potret.pphPerkiraanSaatSetor)) } : null;
    const B = { key, nama: pjNama(key), pendek: pjPendek(key), sistem: S.omzet, nNota: S.n, sebelumPotongan, potongan: PT, sebagian, awalSistem: sebagian ? awal : null, lama, lain, pasangan, pasanganIkutPph: pasangan !== null && !AP.batasSendiri, lengkap, lengkapSejauhIni, omzet, gabung, kumSebelum, kum, kumGabung, kena, pph,
      tempo, berjalan, setor, jumlahSetor, ntpn: setor.map((s) => s.ntpn).filter(Boolean), berubah, terkunci: pjTerkunci(key) };   // putaran 25: keadaan kunci bulan
    B.status = pjStatus(B, P, iso, hitung); daftar.push(B);
  }
  return { tahun: th, daftar, P, hitung, anggapanOp: P.jenisWp === 'belumDiketahui', pasangan: AP, kum, kumGabung,
    totalSistem: daftar.reduce((a, b) => a + (b.sistem || 0), 0), totalSebelumPotongan: daftar.reduce((a, b) => a + (b.sebelumPotongan || 0), 0), kosong, lengkap: kosong === 0, awalSistem: awal, totalPph: hitung ? daftar.reduce((a, b) => a + (b.pph || 0), 0) : null,
    totalSetor: daftar.reduce((a, b) => a + b.jumlahSetor, 0), kumTeks: pjKumTeks(kum, kosong), ambang: pjAmbang(kumGabung, P, th, iso), peringatanTahunLalu: pjPeringatanTahunLalu(P) };
}
function pjKumTeks(kum, kosong) { return RP(kum) + (kosong ? ' — ' + kosong + ' bulan belum diisi, kumulatif KURANG dari sebenarnya' : ''); }
/** Status satu bulan. Urutan: badan → aturan belum diatur → ada setoran (berubah / kurang / lebih / disetor) → data belum lengkap → lewat tempo / terutang / nihil. */
export function pjStatus(B, P, iso, hitung) {
  if (P.jenisWp === 'badan') return { kode: 'badan', teks: 'tidak dihitung — tanyakan konsultan', awas: false };
  if (!hitung) return { kode: 'aturan', teks: 'aturan belum diatur', awas: false };
  if (B.setor.length) {
    if (B.berubah) return { kode: 'berubah', teks: 'angka berubah sejak disetor: omzet ' + (B.berubah.omzet > 0 ? '+' : '−') + RP(Math.abs(B.berubah.omzet)) + (B.berubah.pph ? ' · perkiraan PPh ' + (B.berubah.pph > 0 ? '+' : '−') + RP(Math.abs(B.berubah.pph)) : ''), awas: true };
    const d = B.jumlahSetor - B.pph; const kurangData = B.lengkapSejauhIni ? '' : ' (data belum lengkap — perkiraannya bisa lebih besar)';
    if (d < 0) return { kode: 'kurang', teks: 'kurang setor ' + RP(-d) + kurangData, awas: true };
    if (d > 0) return { kode: 'lebih', teks: 'lebih setor ' + RP(d) + kurangData, awas: false };
    return { kode: 'disetor', teks: 'disetor' + (B.ntpn.length ? ' · NTPN ' + B.ntpn.join(', ') : ' · tanpa NTPN') + kurangData, awas: false };
  }
  if (!B.lengkapSejauhIni) return { kode: 'belumLengkap', teks: 'data belum lengkap' + (B.pph > 0 ? ' — terutang paling sedikit ' + RP(B.pph) : ' — bisa jadi sudah terutang'), awas: true };
  if (B.pph > 0 && !B.berjalan && iso > B.tempo) return { kode: 'lewatTempo', teks: 'lewat tempo ' + tanggalPendek(B.tempo) + ' · terutang ' + RP(B.pph), awas: true };
  if (B.pph > 0) return { kode: 'terutang', teks: 'terutang ' + RP(B.pph) + (B.berjalan ? ' (bulan berjalan)' : ' · setor s.d. ' + tanggalPendek(B.tempo)), awas: false };
  return { kode: 'nihil', teks: B.kum <= (P.batasBebas || 0) ? 'nihil — belum melewati batas bebas' : 'nihil', awas: false };
}
/** Ambang atas (batasOmzet): tanda 70/85/95/100 % dari kumulatif GABUNG + proyeksi akhir tahun [PERKIRAAN] = kumulatif + rata-rata harian 30 hari terakhir × sisa hari. */
export function pjAmbang(kumGabung, P, th, iso) {
  if (!(P.batasOmzet > 0)) return { ada: false, teks: 'batas omzet belum diatur' };
  const pct = kumGabung / P.batasOmzet * 100; const level = PJ_AMBANG.filter((a) => pct >= a).pop() || 0;
  let proyeksi = null; if (th === Number(iso.slice(0, 4))) { const mulai = pjTambahHari(iso, -29); const L = hitungLabaRentang((t) => !!t && t >= mulai && t <= iso); const rata = L.omzetPenuh / 30; const sisa = pjHariKe(th + '-12-31') - pjHariKe(iso);
    proyeksi = { rata: Math.round(rata), sisaHari: sisa, n: Math.round(kumGabung + rata * sisa), pct: (kumGabung + rata * sisa) / P.batasOmzet * 100 }; }
  const akibat = level >= 85 || (proyeksi && proyeksi.pct >= 85) ? 'Yang perlu ditanyakan ke konsultan: tarif 0,5 % tahun depan, kewajiban pembukuan, dan kemungkinan wajib PKP.' : '';
  return { ada: true, pct, level, proyeksi, akibat, sisa: P.batasOmzet - kumGabung,
    teks: RP(kumGabung) + ' = ' + pct.toFixed(1).replace('.', ',') + ' % dari batas ' + RP(P.batasOmzet) + (level ? ' · lewat tanda ' + level + ' %' : '') + (proyeksi ? ' · proyeksi akhir tahun ' + RP(proyeksi.n) + ' (' + proyeksi.pct.toFixed(0) + ' %) [PERKIRAAN]' : '') };
}
function pjPeringatanTahunLalu(P) { return P.omzetTahunLalu !== null && P.batasOmzet > 0 && P.omzetTahunLalu > P.batasOmzet ? 'Omzet tahun lalu melewati batas — tarif 0,5 % kemungkinan tidak berlaku tahun ini. Tanyakan konsultan.' : ''; }
/** Perkiraan PPh satu bulan (dipakai DK3 supaya dua layar memberi angka yang sama). null = tidak dihitung. */
export function pjPerkiraanBulan(key, kini) { const T = pjTahun(Number(key.slice(0, 4)), kini); const b = T.daftar.find((x) => x.key === key); return b ? { pph: b.pph, lengkap: b.lengkapSejauhIni } : { pph: null, lengkap: false }; }

// ==================== setoran (pajakSetoran) ====================
export const pjSetoranSemua = () => cacheMentah('pajakSetoran').slice().sort((a, b) => String(a.tanggalSetor || '').localeCompare(String(b.tanggalSetor || '')) || String(a.id).localeCompare(String(b.id)));
/** NTPN: 16 karakter angka/huruf menurut artikel DJP 2020 [BELUM TERVERIFIKASI untuk era Coretax] → hanya peringatan, tidak memblokir. */
/** putaran 25: bulan pajak terkunci? (sampaiBulan dokumen kunci) · peringatan untuk setoran bulan yang BELUM dikunci — angkanya masih bisa bergeser. */
export const pjTerkunci = (key) => { const s = kunciSampai(); return !!s && String(key) <= s; };
export function pjPeringatanKunci(key) { return pjTerkunci(key) ? '' : 'Kunci bulan ' + pjNama(key) + ' dulu supaya angkanya tidak bergeser (Uang › Tutup buku › Kunci bulan)'; }
export function pjCekNtpn(ntpn) { const x = String(ntpn || '').replace(/\s/g, '').toUpperCase(); if (!x) return 'tanpa NTPN'; return /^[0-9A-Z]{16}$/.test(x) ? '' : 'NTPN biasanya 16 karakter angka/huruf (format belum terverifikasi untuk Coretax) — periksa lagi bukti setornya'; }
export function susunSetoran(isi, w, kini) {
  const masa = String(isi.masaPajak || ''); const tgl = String(isi.tanggalSetor || ''); const ntpn = String(isi.ntpn || '').replace(/\s/g, '').toUpperCase().slice(0, 32);
  const atas = String(isi.atasNama || '').trim().slice(0, 60); const cat = String(isi.catatan || '').trim().slice(0, 160);
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(masa)) return { tolak: 'Pilih masa pajaknya (bulan omzet yang disetori)' }; if (masa > pjKey(w.tanggal)) return { tolak: 'Masa pajak bulan depan belum ada' };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(tgl) || tgl > w.tanggal) return { tolak: 'Tanggal setor belum benar (tidak boleh sesudah hari ini)' };
  if (ugKosong(isi.jumlah)) return { tolak: 'Ketik jumlah yang disetor' }; const n = ugAngka(isi.jumlah); if (!(n > 0)) return { tolak: 'Jumlah setor harus lebih dari nol' };
  if (pjAdaNomorPribadi(atas) || pjAdaNomorPribadi(cat)) return { tolak: PJ_TOLAK_NOMOR };
  const mundur = pjHariKe(w.tanggal) - pjHariKe(tgl) > 7; if ((mundur || !ntpn) && !cat) return { tolak: mundur ? 'Setoran ini dicatat mundur (lebih dari 7 hari lalu) — catatan wajib diisi: dari mana angkanya (mis. cerita pemilik lama, bukti kertas)' : 'Tanpa NTPN, catatan wajib diisi (mis. "bukti setor belum ketemu")' };
  const T = pjTahun(Number(masa.slice(0, 4)), kini); const b = T.daftar.find((x) => x.key === masa); const peringatan = [pjCekNtpn(ntpn), pjPeringatanKunci(masa)].filter(Boolean).join(' · ');
  const data = { id: 'ps-' + w.idUnik(), masaPajak: masa, tanggalSetor: tgl, jumlah: Math.round(n), ntpn, atasNama: atas, catatan: cat, omzetSaatSetor: b ? b.omzet : null, pphPerkiraanSaatSetor: b ? b.pph : null, dicatatPada: w.tanggal };
  return { dokumen: [{ koleksi: 'pajakSetoran', data }], peringatan, patch: { kabar: 'Setoran ' + pjNama(masa) + ' ' + RP(Math.round(n)) + ' dicatat' + (b ? ' — omzet saat ini ' + RP(b.omzet) + ' dipotret; kalau berubah nanti, bulannya ditandai' : '') + (peringatan ? '. ' + peringatan : ''), kabarAwas: !!peringatan, drafSetor: null } };
}
export function susunHapusSetoran(id, yakin) {
  const d = cacheMentah('pajakSetoran').find((x) => String(x.id) === String(id)); if (!d) return { tolak: 'Setoran itu sudah tidak ada' };
  if (!yakin) return { tolak: 'Hapus catatan setoran ' + pjNama(d.masaPajak) + ' ' + RP(d.jumlah) + '? Hanya kalau salah catat — setoran sungguhan tetap ada di Coretax. Ketuk sekali lagi', perluYakin: true };
  return { dokumen: [], hapus: [{ koleksi: 'pajakSetoran', id: String(id) }], patch: { kabar: 'Catatan setoran ' + pjNama(d.masaPajak) + ' dihapus', kabarAwas: false, yakinPj: null } };
}

// ==================== ke layar lain: beranda & pengingat ====================
/** Beranda › Perlu perhatian (owner saja): SATU baris kalau ada lewat tempo, kurang setor, angka berubah sejak disetor, atau ambang ≥ 85 %. */
export function pjPerhatian(kini) {
  const T = pjTahun(null, kini); const masalah = T.daftar.filter((b) => ['lewatTempo', 'kurang', 'berubah'].indexOf(b.status.kode) >= 0); const tinggi = T.ambang.ada && T.ambang.level >= 85;
  if (!masalah.length && !tinggi) return [];
  const bagian = []; ['lewatTempo', 'kurang', 'berubah'].forEach((k) => { const x = masalah.filter((b) => b.status.kode === k); if (x.length) bagian.push((k === 'lewatTempo' ? 'lewat tempo ' : k === 'kurang' ? 'kurang setor ' : 'angka berubah sejak disetor ') + x.map((b) => b.pendek).join(', ')); });
  if (tinggi) bagian.push('omzet ' + Math.floor(T.ambang.pct) + ' % dari batas');
  return [{ teks: 'Pajak (' + PJ_LABEL + '): ' + bagian.join(' · '), nilai: masalah.length ? masalah.length + ' bulan' : 'ambang ' + T.ambang.level + ' %', awas: true }];
}
/** Sumber pengingat jenis 'pajak' (tanggal setor bulan lalu): hanya kalau bulan lalu TERUTANG dan belum disetor. Diteruskan ke sistem-logika lewat lokal.pajak. */
export function pjSumberPengingat(kini) {
  const iso = hariIniIso(kini || new Date(Date.now())); const lalu = pjGeser(pjKey(iso), -1); const T = pjTahun(Number(lalu.slice(0, 4)), kini); const b = T.daftar.find((x) => x.key === lalu);
  if (!b || !T.hitung || !(b.pph > 0) || b.setor.length) return [];
  return [{ id: 'pajak|' + lalu, jenis: 'pajak', kunci: lalu, teks: 'Setor PPh final ' + b.nama, siapa: 'pajak', jatuh: b.tempo, n: b.pph, ket: 'perkiraan ' + RP(b.pph) + ' · KAP-KJS 411128-420 lewat Coretax · ' + PJ_LABEL }];
}

// ==================== cetak: Rekap pajak untuk konsultan ====================
export function dokRekapPajak(T, kop) {
  const P = T.P; const baris = [{ nama: 'Profil wajib pajak', kelas: 'kel' }, { nama: 'Atas nama', teks: P.wpAtasNama || '(belum diisi)' },
    { nama: 'Jenis wajib pajak: ' + (PJ_JENIS_WP.find((j) => j.id === P.jenisWp) || {}).nama + (T.anggapanOp ? ' — ' + PJ_ANGGAPAN_OP : ''), teks: '' }, { nama: 'Status PKP', teks: (PJ_STATUS_PKP.find((j) => j.id === P.statusPkp) || {}).nama },
    { nama: 'Tahun mulai tarif final', teks: P.tahunMulaiTarifFinal === null ? 'tidak diketahui' : String(P.tahunMulaiTarifFinal) }, { nama: 'Omzet tahun lalu', teks: P.omzetTahunLalu === null ? 'tidak diketahui' : RP(P.omzetTahunLalu) },
    { nama: 'Status pasangan: ' + (PJ_STATUS_PASANGAN.find((j) => j.id === P.statusPasangan) || {}).nama, teks: '' }, { nama: '  ' + (T.pasangan.belumTerverifikasi ? PJ_TANDA_BELUM + ' ' : '') + T.pasangan.teks, teks: '' },
    { nama: 'Tarif', teks: P.tarifPerMil ? (P.tarifPerMil / 10).toFixed(1).replace('.', ',') + ' %' : 'belum diatur' }, { nama: 'Batas bebas setahun', teks: P.batasBebas === null ? 'belum diisi' : RP(P.batasBebas) }, { nama: 'Batas atas setahun', teks: P.batasOmzet ? RP(P.batasOmzet) : 'belum diatur' },
    { nama: 'Dua angka omzet per bulan', kelas: 'kel' },
    { nama: 'Omzet mesin = dasar perkiraan PPh di rekap ini (penjualan berlaku, sesudah potongan nota & retur). Omzet sebelum potongan nota = omzet mesin + potongan nota + tawar di bawah harga daftar (dari hargaAsliSatuan), retur tetap dikurangi. PMK 164/2023 Pasal 6 ayat (2) menyebut peredaran bruto sebelum potongan penjualan.', teks: '' },
    { nama: 'Angka mana yang dipakai sebagai peredaran bruto DISERAHKAN KE KONSULTAN.', teks: '' },
    { nama: 'Per bulan ' + T.tahun, kelas: 'kel' }];
  T.daftar.forEach((b) => {
    const luar = [b.lama !== null ? 'catatan lama ' + RP(b.lama) : '', b.lain !== null ? 'usaha lain ' + RP(b.lain) : '', b.pasangan !== null ? 'usaha pasangan ' + RP(b.pasangan) + (b.pasanganIkutPph ? ' (ikut PPh' + (T.pasangan.anggapan ? ' — anggapan' : '') + ')' : ' (batas Rp4,8 miliar saja)') : ''].filter(Boolean).join(' · ');
    baris.push({ nama: b.nama + (b.sebagian ? ' (sistem mulai ' + tanggalPendek(b.awalSistem) + ')' : ''), teks: b.lengkap ? RP(b.omzet) : '—' });
    if (b.sistem !== null) baris.push({ nama: '  omzet mesin ' + RP(b.sistem) + ' · omzet sebelum potongan nota ' + RP(b.sebelumPotongan) + (b.potongan.jumlah ? ' (potongan nota ' + RP(b.potongan.nota) + (b.potongan.tawar ? ', tawar ' + RP(b.potongan.tawar) : '') + ' di ' + b.potongan.n + ' baris)' : ' (tidak ada potongan)'), teks: '' });
    baris.push({ nama: '  sistem ' + (b.sistem === null ? '—' : RP(b.sistem)) + (luar ? ' · diketik owner: ' + luar : '') + ' · kumulatif ' + RP(b.kum), teks: b.pph === null ? 'PPh tidak dihitung' : 'PPh ' + RP(b.pph) });
    baris.push({ nama: '  setoran ' + (b.setor.length ? RP(b.jumlahSetor) + (b.ntpn.length ? ' · NTPN ' + b.ntpn.join(', ') : ' · tanpa NTPN') : '—') + ' · ' + b.status.teks, teks: '' });
  });
  baris.push({ nama: 'Jumlah omzet mesin ' + T.tahun, teks: RP(T.totalSistem), kelas: 'jumlah' }, { nama: 'Jumlah omzet sebelum potongan nota ' + T.tahun, teks: RP(T.totalSebelumPotongan), kelas: 'jumlah' });
  baris.push({ nama: 'Jumlah perkiraan PPh ' + T.tahun, teks: T.totalPph === null ? 'tidak dihitung' : RP(T.totalPph), kelas: 'jumlah' }, { nama: 'Jumlah setoran tercatat', teks: RP(T.totalSetor), kelas: 'jumlah' });
  baris.push({ nama: 'Sumber aturan (dilihat 24 Sep 2026)', kelas: 'kel' }); PJ_SUMBER.forEach((s) => baris.push({ nama: (s.terverifikasi ? '' : '[BELUM TERVERIFIKASI] ') + s.klaim, teks: '' }));
  return { jenis: 'pajak', kop, judul: 'Rekap Pajak untuk Konsultan', sub: 'Tahun ' + T.tahun + ' · ' + PJ_LABEL + (T.kosong ? ' · ' + T.kosong + ' bulan belum diisi' : ''), periode: String(T.tahun), baris, cap: T.kosong ? 'DATA BELUM LENGKAP' : '',
    catatan: 'Dua angka omzet per bulan (mesin & sebelum potongan nota) — pilihan angka yang dipakai diserahkan ke konsultan; perkiraan PPh di sini memakai omzet mesin. ' + T.kumTeks + '. ' + (T.ambang.ada ? 'Ambang: ' + T.ambang.teks + '. ' : '') + (T.peringatanTahunLalu ? T.peringatanTahunLalu + ' ' : '') + (P.sumberAturan ? 'Aturan: ' + P.sumberAturan.teks + ' (diisi ' + tanggalPendek(P.sumberAturan.tanggal) + ').' : 'Aturan belum diisi dari tombol.') };
}
