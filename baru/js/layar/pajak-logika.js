// LOGIKA MODUL PAJAK (putaran 24, 24 Sep 2026), tanpa DOM — khusus owner (layar Laporan › Pajak; rules: pajakOmzetLuar & pajakSetoran owner saja).
// Sistem TAHU posisi pajaknya sendiri: menghitung perkiraan PPh final per bulan, mengingatkan, menyimpan bukti setoran. TIDAK membayar, TIDAK melapor,
// TIDAK memberi nasihat pajak — setiap angka berlabel PJ_LABEL. Dijaga alat-uji/uji_pajak_baru.py. Sumber aturan: docs/sumber-aturan-pajak.md.
//   · omzet sistem per bulan = mesin laba (hitungLabaRentang → omzetPenuh), SATU sumber — DK3 (rekapOmzet) memanggil pjOmzetSistem yang sama;
//   · profil wajib pajak = field TAMBAHAN di aturanToko/rekapOmzet; SEMUA penulis dokumen itu lewat pjGabungRekap (membawa semua field, termasuk yang tidak dikenalnya);
//   · omzet di luar sistem (pajakOmzetLuar) = ketikan owner, tampil beda dari hitungan; kosong ≠ nol;
//   · setoran (pajakSetoran) memotret omzet & perkiraan saat dicatat → angka yang berubah sesudahnya DISEBUT, tidak diam.
// Nama pembantu diprefiks `pj` (bundel uji jsc satu lingkup).
// PAKET B (siap 2027, owner 7 Okt 2026): tahun yang sudah ditutup buku dibaca dari POTRET di berita acaranya (toko.js potretBulan — catatannya sudah diarsip):
//   · omzet sistem, nota & potongan per bulan = angka potret (fungsi di bawah ini juga yang menyusunnya saat kunci) → Pajak 2026 sesudah ritual = sebelum ritual;
//   · omzet di luar sistem & setoran TIDAK diarsip (koleksinya sendiri) — tetap dibaca hidup, jadi masa Desember 2026 bisa dicatat di Januari 2027;
//   · layar memilih TAHUN (pjDaftarTahun / pjTahunBawaan): tahun berjalan + tahun lalu yang punya omzet/isian/setoran/potret; Jan–Mar menawarkan tahun lalu
//     selama masih ada masa terutang; · Beranda & pengingat menyebut semua masa lewat tempo (juga yang datanya belum lengkap, "paling sedikit") termasuk tahun lalu;
//   · "awal sistem" = nota pertama sepanjang masa (potret), dan tahun SESUDAH tutup buku tercatat sejak 1 Januari — Januari tidak dicap "belum lengkap";
//   · omzet tahun lalu per TAHUN (omzetTahunan) & aturan berlabel tahun pajak yang diperiksa.
import { hitungLabaRentang } from '../mesin/beku.js';
import { bulanDari, namaBulanPanjang } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, cacheMentah, kunciSampai, jumlahNota, potretBulan, potretTahun, tahunDitutup, tahunDiarsip, awalPotret, eraBerAcara } from '../data/toko.js';
import { lpHariRentang } from './laporan-logika.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong } from './uang-logika.js';
import { KP_KUNCI_MULAI } from '../data/kunci-periode.js';

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
export function pjOmzetSistem(key) {
  const Pt = potretBulan(key); if (Pt) return { omzet: Number(Pt.omzet) || 0, n: Number(Pt.n) || 0 };   // Paket B: bulan di tahun yang sudah ditutup buku
  const L = hitungLabaRentang((t) => !!t && bulanDari(t) === key); return { omzet: L.omzetPenuh, n: jumlahNota((t) => !!t && bulanDari(t) === key) }; }   // n = nota, bukan baris (39b no. 20)
/** Tanggal nota pertama di sistem (penjualan apa pun) — bulan sebelumnya TIDAK ada di sistem; bulan pertama bisa terisi sebagian.
 *  Paket B (R4): nota tahun yang sudah ditutup buku sudah diarsip → nota pertama sepanjang masa dari potret. Tahun SESUDAH tutup buku yang dikerjakan di sistem
 *  ini tercatat sejak 1 Januari (tanpa potret pun) — nota pertama 2 Jan tidak membuat Januari "sebagian / belum lengkap". */
export function pjAwalSistem() {
  let p = ''; ambilPenjualanSemua().forEach((d) => { if (d.tanggal && (!p || d.tanggal < p)) p = d.tanggal; });
  const q = awalPotret('awalSistem'); if (q && (!p || q < p)) p = q;
  const era = eraBerAcara(); if (era !== null && (!p || p > era + '-12-31')) p = (era + 1) + '-01-01';
  return p;
}

// ==================== profil (field tambahan di aturanToko/rekapOmzet) ====================
export const pjDokRekap = () => ugAturDok('rekapOmzet');
// ---- Paket B (sanggahan, owner 7 Okt): ATURAN PER TAHUN PAJAK. Kolom lama dokumen = aturan TERBARU (tahun berjalan; DK3 & pembaca lama membacanya). `aturanTahun`
// { 'YYYY': { …PJ_KOLOM_TAHUN } } = aturan tahun LALU: dibekukan dengan nilai lamanya begitu aturan terbaru diubah (pjGabungRekap), atau diubah dari layar Pajak
// tahun itu sendiri. Tahun tanpa entri = aturan terbaru (belum pernah ada yang berubah sejak tahun itu). Jadi tarif/batas/status 2027 yang diubah tidak menghitung
// ulang PPh 2026 (rekap SPT 2026, status setoran Desember) diam-diam. Nama WP, tahun mulai tarif final & omzet per tahun tetap satu untuk semua tahun.
export const PJ_KOLOM_TAHUN = ['jenisWp', 'statusPkp', 'statusPasangan', 'tarifPerMil', 'batasBebas', 'batasOmzet', 'sumberAturan'];
const pjPetaTahun = (d) => (d && d.aturanTahun && typeof d.aturanTahun === 'object' ? d.aturanTahun : {});
/** Kolom aturan dari `o` — yang tidak ada = null (tersimpan tegas: "belum diatur" ikut dibekukan, tidak jatuh ke aturan terbaru). */
const pjKolomAturan = (o) => { const out = {}; PJ_KOLOM_TAHUN.forEach((k) => { out[k] = o && o[k] !== undefined ? o[k] : null; }); return out; };
/** Profil & aturan pajak terbaca untuk `tahun` (kosong = aturan terbaru). batasOmzet (lama) = BATAS ATAS Rp4,8 miliar — satu angka, tidak ada batasAtas terpisah (lihat BACA-DULU). */
export function pjProfil(tahun) {
  const d0 = pjDokRekap() || {}; const e = tahun ? pjPetaTahun(d0)[String(Number(tahun))] : null; const ov = {}; if (e && typeof e === 'object') PJ_KOLOM_TAHUN.forEach((k) => { if (k in e) ov[k] = e[k]; });
  const d = Object.assign({}, d0, ov); const jenis = PJ_JENIS_WP.some((j) => j.id === d.jenisWp) ? d.jenisWp : 'belumDiketahui'; const pkp = PJ_STATUS_PKP.some((j) => j.id === d.statusPkp) ? d.statusPkp : 'belumDiketahui';
  const ang = (v) => { const n = pjAngkaAtauNull(v); return n !== null && n >= 0 ? n : null; };
  const pasangan = PJ_STATUS_PASANGAN.some((j) => j.id === d.statusPasangan) ? d.statusPasangan : 'belumDiketahui';
  // Paket B: omzet tahun lalu PER TAHUN (omzetTahunan { 'YYYY': n }); kolom lama omzetTahunLalu = tahun omzetTahunLaluTahun (bawaan 2025 — modul pajak lahir Sep 2026)
  const omzetTahunan = {}; if (d.omzetTahunan && typeof d.omzetTahunan === 'object') Object.keys(d.omzetTahunan).forEach((y) => { const n = ang(d.omzetTahunan[y]); if (/^\d{4}$/.test(y) && n !== null) omzetTahunan[y] = n; });
  const lama = ang(d.omzetTahunLalu); if (lama !== null && !(d.omzetTahunan && typeof d.omzetTahunan === 'object')) omzetTahunan[String(ang(d.omzetTahunLaluTahun) || PJ_SUMBER_TAHUN - 1)] = lama;   // dokumen sebelum Paket B
  return { wpAtasNama: String(d.wpAtasNama || ''), jenisWp: jenis, statusPkp: pkp, statusPasangan: pasangan, tahunMulaiTarifFinal: ang(d.tahunMulaiTarifFinal), omzetTahunLalu: lama, omzetTahunan, batasBebas: ang(d.batasBebas),
    batasOmzet: ang(d.batasOmzet) || 0, tarifPerMil: ang(d.tarifPerMil) || 0, tanggalLapor: isFinite(Number(d.tanggalLapor)) && Number(d.tanggalLapor) >= 1 && Number(d.tanggalLapor) <= 28 ? Math.round(Number(d.tanggalLapor)) : 15,
    sumberAturan: d.sumberAturan && typeof d.sumberAturan === 'object' ? Object.assign({ teks: String(d.sumberAturan.teks || ''), tanggal: String(d.sumberAturan.tanggal || '') }, ang(d.sumberAturan.tahun) ? { tahun: ang(d.sumberAturan.tahun) } : {}) : null, ada: !!pjDokRekap(),
    tahunAturan: Object.keys(ov).length ? Number(tahun) : null };   // tahunAturan = aturan yang dibaca tersimpan khusus tahun itu
}
/**
 * SATU-SATUNYA cara menyusun isi aturanToko/rekapOmzet (DK3 susunAturRekap & susunTandaLapor, profil, tombol aturan): dokumen yang ada disalin UTUH
 * (termasuk field yang tidak dikenal penulisnya), lalu hanya `ubah` yang ditimpa. Tanpa ini tiap penulis lama menghapus profil diam-diam.
 */
export function pjGabungRekap(ubah, w, tahunPajak) {
  const lama = pjDokRekap() || {}; const u = Object.assign({}, ubah || {}); const th = Number(String(w.tanggal).slice(0, 4));
  // Paket B: aturan per tahun pajak (PJ_KOLOM_TAHUN) — dijaga DI SINI, satu-satunya penulis dokumen ini
  const thP = isFinite(Number(tahunPajak)) && Number(tahunPajak) >= 2000 && Number(tahunPajak) < th ? Math.round(Number(tahunPajak)) : th;
  const kolom = PJ_KOLOM_TAHUN.filter((k) => k in u); const peta = Object.assign({}, pjPetaTahun(lama)); let petaUbah = false; const pilih = (o) => { const x = {}; kolom.forEach((k) => { x[k] = o[k] === undefined ? null : o[k]; }); return x; };
  if (kolom.length && thP < th) {   // dari layar tahun LALU: hanya aturan tahun itu yang berubah; aturan terbaru (tahun berjalan & DK3) tidak tersentuh
    peta[String(thP)] = Object.assign(pjKolomAturan(Object.assign({}, lama, peta[String(thP)] || {})), pilih(u)); kolom.forEach((k) => { delete u[k]; }); petaUbah = true;
  } else if (kolom.length) {
    const sama = (a, b) => JSON.stringify(a === undefined ? null : a) === JSON.stringify(b === undefined ? null : b);
    // aturan TERBARU berubah → tahun lalu yang belum punya entri DIBEKUKAN dulu dengan aturan lamanya (tahun lalu tidak ikut berubah)
    if (kolom.some((k) => !sama(u[k], lama[k]))) pjTahunLalu(th).forEach((y) => { if (!peta[String(y)]) { peta[String(y)] = pjKolomAturan(lama); petaUbah = true; } });
    if (peta[String(th)]) { peta[String(th)] = Object.assign({}, peta[String(th)], pilih(u)); petaUbah = true; }
  }
  if (petaUbah) u.aturanTahun = peta;
  const d = Object.assign({}, lama, u, { id: 'rekapOmzet', tanggal: w.tanggal, jam: w.jam });
  if (!d.lapor || typeof d.lapor !== 'object') d.lapor = {}; Object.keys(d).forEach((k) => { if (d[k] === undefined) delete d[k]; }); return d;
}
export function susunProfilPajak(isi, w) {
  const u = {};
  if (isi.wpAtasNama !== undefined) { const n = String(isi.wpAtasNama || '').trim().slice(0, 60); if (pjAdaNomorPribadi(n)) return { tolak: PJ_TOLAK_NOMOR }; u.wpAtasNama = n; }
  if (isi.jenisWp !== undefined) { if (!PJ_JENIS_WP.some((j) => j.id === isi.jenisWp)) return { tolak: 'Jenis wajib pajak tidak dikenal' }; u.jenisWp = isi.jenisWp; }
  if (isi.statusPkp !== undefined) { if (!PJ_STATUS_PKP.some((j) => j.id === isi.statusPkp)) return { tolak: 'Status PKP tidak dikenal' }; u.statusPkp = isi.statusPkp; }
  if (isi.statusPasangan !== undefined) { if (!PJ_STATUS_PASANGAN.some((j) => j.id === isi.statusPasangan)) return { tolak: 'Status pasangan tidak dikenal' }; u.statusPasangan = isi.statusPasangan; }
  const th = Number(String(w.tanggal).slice(0, 4));
  // Paket B: "omzet tahun lalu" = omzet tahun (tahunPajak − 1) — tahunPajak = tahun yang sedang dibuka di layar Pajak (bawaan tahun berjalan)
  const thPajak = isFinite(Number(isi.tahunPajak)) && Number(isi.tahunPajak) >= 2000 && Number(isi.tahunPajak) <= th ? Math.round(Number(isi.tahunPajak)) : th;
  const angka = (k, min, maks, nama) => { if (isi[k] === undefined) return ''; if (ugKosong(isi[k])) { u[k] = null; return ''; } const n = ugAngka(isi[k]); if (!(n >= min && n <= maks)) return nama; u[k] = Math.round(n); return ''; };
  const salah = angka('tahunMulaiTarifFinal', 2000, th, 'Tahun mulai tarif final: 2000–' + th + ' (kosongkan kalau tidak tahu)') || angka('omzetTahunLalu', 0, 1e13, 'Omzet tahun ' + (thPajak - 1) + ' tidak boleh minus (kosongkan kalau tidak tahu — kosong ≠ nol)')
    || angka('batasBebas', 0, 1e13, 'Batas bebas tidak boleh minus') || angka('batasOmzet', 0, 1e13, 'Batas omzet tidak boleh minus') || angka('tarifPerMil', 0, 1000, 'Tarif ditulis per seribu: 0–1000 (5 = 0,5 %)');
  if (salah) return { tolak: salah };
  const P = pjProfil(thPajak);
  if (u.omzetTahunLalu !== undefined) { const peta = Object.assign({}, P.omzetTahunan); const y = String(thPajak - 1); if (u.omzetTahunLalu === null) delete peta[y]; else peta[y] = u.omzetTahunLalu; u.omzetTahunan = peta;
    u.omzetTahunLaluTahun = thPajak - 1; }   // kolom lama = isian terakhir + tahunnya (pembaca lama); pembaca baru memakai peta per tahun
  if (u.batasOmzet === null) u.batasOmzet = 0; if (u.tarifPerMil === null) u.tarifPerMil = 0;   // field lama DK3: 0 = belum diatur (bentuk lama dipertahankan)
  const jenis = u.jenisWp || P.jenisWp; const lalu = thPajak < th && PJ_KOLOM_TAHUN.some((k) => k in u);
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap(u, w, thPajak) }], patch: { kabar: 'Profil pajak tersimpan' + (lalu ? ' — aturan tahun ' + thPajak + ' saja; tahun lain tidak berubah' : '') + (jenis === 'belumDiketahui' ? ' — ' + PJ_ANGGAPAN_OP : jenis === 'badan' ? ' — badan: kolom PPh tidak dihitung, tanyakan konsultan' : '') + '. ' + PJ_LABEL + '.', kabarAwas: false, drafPj: null } };
}
/** Tombol "Pakai aturan PP 55/2022 jo. PP 20/2026": tarif 5‰, batas bebas Rp500 juta, batas atas Rp4,8 miliar + catatan sumbernya. Tiap angka tetap bisa diubah. */
export function susunPakaiAturan(w, tahunPajak) {
  // Paket B: aturan dicap TAHUN PAJAK yang diperiksa (tahun yang dibuka di layar Pajak; bawaan tahun berjalan) — tahun sesudahnya diberi peringatan (pjAturanTahun)
  const thW = Number(String(w.tanggal).slice(0, 4)); const thP = isFinite(Number(tahunPajak)) && Number(tahunPajak) >= 2000 && Number(tahunPajak) <= thW ? Math.round(Number(tahunPajak)) : thW;
  // tahun lalu: aturan khusus tahun itu (dicap tahun itu); tahun berjalan: aturan terbaru (tahun lalu yang belum punya aturan sendiri dibekukan — pjGabungRekap)
  const tahun = thP < thW ? thP : Math.max(thP, Number((pjProfil().sumberAturan || {}).tahun) || 0);
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: PJ_ATURAN.tarifPerMil, batasBebas: PJ_ATURAN.batasBebas, batasOmzet: PJ_ATURAN.batasOmzet, sumberAturan: { teks: PJ_ATURAN.teks, tanggal: w.tanggal, tahun } }, w, thP) }],
    patch: { kabar: 'Aturan ' + (thP < thW ? 'tahun pajak ' + thP + ' (tahun itu saja) ' : '') + 'terisi: tarif 0,5 %, bebas s.d. ' + RP(PJ_ATURAN.batasBebas) + ', batas ' + RP(PJ_ATURAN.batasOmzet) + ' — sumbernya tercatat. Tiap angka bisa lu ubah. ' + PJ_LABEL + '.', kabarAwas: false } };
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
  const Pt = potretBulan(key); if (Pt && Pt.potongan) return Object.assign({}, Pt.potongan);   // Paket B: tahun yang sudah ditutup buku
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
  const iso = hariIniIso(kini || new Date(Date.now())); const kiniKey = pjKey(iso); const th = Number(tahun || kiniKey.slice(0, 4)); const P = pjProfil(th);
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
      tempo, berjalan, setor, jumlahSetor, ntpn: setor.map((s) => s.ntpn).filter(Boolean), berubah, terkunci: pjTerkunci(key), ditutup: tahunDitutup(key) };   // putaran 25: keadaan kunci bulan · Paket B: tahun sudah tutup buku
    // Paket B: bulan di tahun yang sudah ditutup buku — angka sistemnya dari potret (dariPotret) atau, tanpa potret, hanya di berkas arsip (tanpaPotret)
    if (tahunDiarsip(key)) { B.diarsip = true; B.dariPotret = !!potretBulan(key); B.tanpaPotret = !B.dariPotret; }
    B.status = pjStatus(B, P, iso, hitung); daftar.push(B);
  }
  const ditutup = tahunDitutup(th), adaPotret = !!potretTahun(th), diarsip = tahunDiarsip(th);
  return { tahun: th, daftar, P, hitung, anggapanOp: P.jenisWp === 'belumDiketahui', pasangan: AP, kum, kumGabung,
    totalSistem: daftar.reduce((a, b) => a + (b.sistem || 0), 0), totalSebelumPotongan: daftar.reduce((a, b) => a + (b.sebelumPotongan || 0), 0), kosong, lengkap: kosong === 0, awalSistem: awal, totalPph: hitung ? daftar.reduce((a, b) => a + (b.pph || 0), 0) : null,
    totalSetor: daftar.reduce((a, b) => a + b.jumlahSetor, 0), kumTeks: pjKumTeks(kum, kosong), ambang: pjAmbang(kumGabung, P, th, iso), peringatanTahunLalu: pjPeringatanTahunLalu(P, th),
    berjalan: th === Number(kiniKey.slice(0, 4)), ditutup, diarsip, potret: adaPotret, tanpaPotret: diarsip && !adaPotret, omzetTahunLalu: pjOmzetTahunLalu(P, th), aturanTahun: pjAturanTahun(P, th, hitung),
    aturanSejakTutup: pjAturanSejakTutup(P, th) };
}
/** Paket B (sanggahan): aturan tahun ber-potret dibandingkan dengan aturan SAAT TAHUN ITU DIKUNCI (potret.pajak.profil). Beda → disebut di layar & rekap konsultan
 *  (PPh tahun itu dihitung dengan aturan yang sekarang tersimpan untuk tahun itu — bisa karena owner membetulkannya sesudah tutup buku). '' = sama / tanpa potret. */
export function pjAturanSejakTutup(P, th) {
  const Pt = potretTahun(th); const pp = Pt && Pt.pajak && Pt.pajak.profil; if (!pp) return '';
  const nama = { jenisWp: 'jenis wajib pajak', statusPasangan: 'status pasangan', tarifPerMil: 'tarif', batasBebas: 'batas bebas', batasOmzet: 'batas atas' };
  const beda = Object.keys(nama).filter((k) => JSON.stringify(pp[k] === undefined ? null : pp[k]) !== JSON.stringify(P[k] === undefined ? null : P[k]));
  if (!beda.length) return '';
  const tarif = (n) => (Number(n) > 0 ? (Number(n) / 10).toFixed(1).replace('.', ',') + ' %' : 'belum diatur');
  return 'Aturan pajak ' + th + ' diubah sesudah tutup buku (' + beda.map((k) => nama[k]).join(', ') + '). Saat tahun dikunci: tarif ' + tarif(pp.tarifPerMil) + ', batas bebas ' + (pp.batasBebas === null || pp.batasBebas === undefined ? 'belum diisi' : RP(pp.batasBebas))
    + ', perkiraan PPh setahun ' + (pp && Pt.pajak.totalPph !== null && Pt.pajak.totalPph !== undefined ? RP(Pt.pajak.totalPph) : 'tidak dihitung') + ' — PPh ' + th + ' di sini dihitung dengan aturan yang sekarang tersimpan untuk ' + th + '.';
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
  let proyeksi = null; if (th === Number(iso.slice(0, 4))) { const mulai = pjTambahHari(iso, -29); const L = lpHariRentang(mulai, iso); const rata = L.omzetPenuh / 30;   /* Paket B: hari di tahun yang ditutup (awal Januari) dari potret hari */ const sisa = pjHariKe(th + '-12-31') - pjHariKe(iso);
    proyeksi = { rata: Math.round(rata), sisaHari: sisa, n: Math.round(kumGabung + rata * sisa), pct: (kumGabung + rata * sisa) / P.batasOmzet * 100 }; }
  const akibat = level >= 85 || (proyeksi && proyeksi.pct >= 85) ? 'Yang perlu ditanyakan ke konsultan: tarif 0,5 % tahun depan, kewajiban pembukuan, dan kemungkinan wajib PKP.' : '';
  return { ada: true, pct, level, proyeksi, akibat, sisa: P.batasOmzet - kumGabung,
    teks: RP(kumGabung) + ' = ' + pct.toFixed(1).replace('.', ',') + ' % dari batas ' + RP(P.batasOmzet) + (level ? ' · lewat tanda ' + level + ' %' : '') + (proyeksi ? ' · proyeksi akhir tahun ' + RP(proyeksi.n) + ' (' + proyeksi.pct.toFixed(0) + ' %) [PERKIRAAN]' : '') };
}
// ---- Paket B (rapi-rapi audit): omzet tahun lalu PER TAHUN & aturan berlabel tahun pajak ----
/** Omzet tahun (th − 1) yang diisi owner (profil omzetTahunan), atau null = tidak diketahui (kosong ≠ nol). */
export function pjOmzetTahunLalu(P, th) { const v = P.omzetTahunan ? P.omzetTahunan[String(Number(th) - 1)] : undefined; return v === undefined ? null : v; }
function pjPeringatanTahunLalu(P, th) { const o = pjOmzetTahunLalu(P, th); return o !== null && P.batasOmzet > 0 && o > P.batasOmzet ? 'Omzet tahun ' + (Number(th) - 1) + ' melewati batas — tarif 0,5 % kemungkinan tidak berlaku tahun ' + th + '. Tanyakan konsultan.' : ''; }
/** Sumber aturan PJ_SUMBER dibaca untuk tahun pajak ini; aturan yang diisi tombol membawa tahun pajaknya sendiri. */
export const PJ_SUMBER_TAHUN = 2026;
/** Tahun pajak yang aturannya sudah diperiksa (tahun diisi lewat tombol / profil; bawaan tahun sumber dilihat) — tahun sesudahnya diberi peringatan, bukan dianggap sama. */
export function pjAturanTahun(P, th, hitung) {
  const diisi = P.sumberAturan ? Number(P.sumberAturan.tahun || String(P.sumberAturan.tanggal || '').slice(0, 4)) || PJ_SUMBER_TAHUN : PJ_SUMBER_TAHUN; const sumber = Math.max(diisi, PJ_SUMBER_TAHUN);
  const belum = !!hitung && Number(th) > diisi;
  return { diisi, sumber, belum, teks: belum ? 'Aturan pajak (tarif ' + (P.tarifPerMil / 10).toFixed(1).replace('.', ',') + ' %, batas bebas & batas atas) diisi untuk tahun ' + diisi + ' — tahun ' + th + ' belum diperiksa. Tanyakan konsultan; kalau sama, tekan "Pakai aturan" lagi dari layar tahun ' + th + '.' : '' };
}
/** Perkiraan PPh satu bulan (dipakai DK3 supaya dua layar memberi angka yang sama). null = tidak dihitung. */
export function pjPerkiraanBulan(key, kini) { const T = pjTahun(Number(key.slice(0, 4)), kini); const b = T.daftar.find((x) => x.key === key); return b ? { pph: b.pph, lengkap: b.lengkapSejauhIni } : { pph: null, lengkap: false }; }

// ==================== setoran (pajakSetoran) ====================
export const pjSetoranSemua = () => cacheMentah('pajakSetoran').slice().sort((a, b) => String(a.tanggalSetor || '').localeCompare(String(b.tanggalSetor || '')) || String(a.id).localeCompare(String(b.id)));
/** NTPN: 16 karakter angka/huruf menurut artikel DJP 2020 [BELUM TERVERIFIKASI untuk era Coretax] → hanya peringatan, tidak memblokir. */
/** putaran 25: bulan pajak terkunci? (sampaiBulan dokumen kunci) · peringatan untuk setoran bulan yang BELUM dikunci — angkanya masih bisa bergeser.
 *  Paket B (sanggahan): tahun yang sudah DITUTUP BUKU = final juga — toko.js tahunDitutup, pembaca yang sama dengan lpFinal Laporan. Kunci bulan 2026 ditunda (K1),
 *  jadi tanpa ini Pajak 2026 sesudah ritual menulis "belum dikunci" di 12 masa dan setoran Desember diberi pita "masih bisa bergeser" padahal angkanya beku di potret. */
export const pjTerkunci = (key) => { if (tahunDitutup(key)) return true; const s = kunciSampai(); return !!s && String(key) <= s; };
// keputusan owner 1 Okt (A): bulan sebelum KP_KUNCI_MULAI tidak dikunci — peringatannya menyebut tutup buku, bukan menyuruh mengunci
export function pjPeringatanKunci(key) { return pjTerkunci(key) ? '' : key < KP_KUNCI_MULAI ? 'Angka ' + pjNama(key) + ' masih bisa bergeser sampai tutup buku ' + key.slice(0, 4) + ' (kunci bulan ' + key.slice(0, 4) + ' ditunda — keputusan owner 1 Okt 2026)' : 'Kunci bulan ' + pjNama(key) + ' dulu supaya angkanya tidak bergeser (Uang › Tutup buku › Kunci bulan)'; }
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
/** Masa yang lewat tempo walau datanya belum lengkap (Paket B, R2): PPh "paling sedikit" > 0, bukan bulan berjalan, tempo terlewati, belum ada setoran. */
const pjLewatBelumLengkap = (b, iso) => b.status.kode === 'belumLengkap' && b.pph > 0 && !b.berjalan && iso > b.tempo && !b.setor.length;
/** Beranda › Perlu perhatian (owner saja): SATU baris kalau ada lewat tempo, kurang setor, angka berubah sejak disetor, atau ambang ≥ 85 %.
 *  Paket B (R2): masa lewat tempo yang datanya belum lengkap ikut disebut ("paling sedikit"), dan Januari–Maret masa TAHUN LALU ikut diperiksa (setoran Desember
 *  jatuh 15 Jan; SPT Tahunan 31 Mar) — dulu Beranda diam selama data belum lengkap, dan masa Desember lenyap begitu tahun berganti. */
export function pjPerhatian(kini) {
  const iso = hariIniIso(kini || new Date(Date.now())); const T = pjTahun(null, kini); const thIni = T.tahun;
  const semua = (Number(iso.slice(5, 7)) <= 3 ? pjTahun(thIni - 1, kini).daftar : []).concat(T.daftar);
  const kode = (b) => (pjLewatBelumLengkap(b, iso) ? 'lewatTempo' : b.status.kode); const masalah = semua.filter((b) => ['lewatTempo', 'kurang', 'berubah'].indexOf(kode(b)) >= 0); const tinggi = T.ambang.ada && T.ambang.level >= 85;
  if (!masalah.length && !tinggi) return [];
  const nama = (b) => b.pendek + (Number(b.key.slice(0, 4)) !== thIni ? ' ' + b.key.slice(2, 4) : '') + (pjLewatBelumLengkap(b, iso) ? ' (paling sedikit ' + RP(b.pph) + ', data belum lengkap)' : '');
  const bagian = []; ['lewatTempo', 'kurang', 'berubah'].forEach((k) => { const x = masalah.filter((b) => kode(b) === k); if (x.length) bagian.push((k === 'lewatTempo' ? 'lewat tempo ' : k === 'kurang' ? 'kurang setor ' : 'angka berubah sejak disetor ') + x.map(nama).join(', ')); });
  if (tinggi) bagian.push('omzet ' + Math.floor(T.ambang.pct) + ' % dari batas');
  return [{ teks: 'Pajak (' + PJ_LABEL + '): ' + bagian.join(' · '), nilai: masalah.length ? masalah.length + ' bulan' : 'ambang ' + T.ambang.level + ' %', awas: true }];
}
/** Sumber pengingat jenis 'pajak': SETIAP masa tahun berjalan & tahun lalu yang terutang (PPh > 0, juga "paling sedikit" saat data belum lengkap), sudah lewat bulannya, dan
 *  belum ada setoran — Paket B (R2): dulu hanya bulan lalu, jadi masa Desember yang belum disetor hilang dari pengingat begitu Februari. Diteruskan ke sistem-logika lewat lokal.pajak. */
export function pjSumberPengingat(kini) {
  const iso = hariIniIso(kini || new Date(Date.now())); const th = Number(iso.slice(0, 4)); const out = [];
  [th - 1, th].forEach((y) => { const T = pjTahun(y, kini); if (!T.hitung) return;
    T.daftar.forEach((b) => { if (b.berjalan || !(b.pph > 0) || b.setor.length) return; const kurang = !b.lengkapSejauhIni;
      out.push({ id: 'pajak|' + b.key, jenis: 'pajak', kunci: b.key, teks: 'Setor PPh final ' + b.nama, siapa: 'pajak', jatuh: b.tempo, n: b.pph, ket: (kurang ? 'paling sedikit ' : 'perkiraan ') + RP(b.pph) + (kurang ? ' (data belum lengkap)' : '') + ' · KAP-KJS 411128-420 lewat Coretax · ' + PJ_LABEL }); }); });
  return out;
}

// ==================== Paket B · pilih TAHUN di layar Pajak ====================
/** Tahun yang bisa dibuka: tahun berjalan + tahun sebelumnya yang punya nota (hidup / potret tutup buku), isian omzet di luar sistem, atau setoran. Terbaru dulu. */
/** Tahun sebelum `th` yang tercatat: punya nota (hidup / potret), isian omzet di luar sistem, atau setoran. */
function pjTahunLalu(th) {
  const ada = {}; const awal = pjAwalSistem(); if (awal) for (let y = Number(awal.slice(0, 4)); y < th; y++) ada[y] = true;
  pjOmzetLuarSemua().forEach((d) => { const y = Number(String(d.bulan || '').slice(0, 4)); if (y >= 2000 && y < th) ada[y] = true; });
  pjSetoranSemua().forEach((s) => { const y = Number(String(s.masaPajak || '').slice(0, 4)); if (y >= 2000 && y < th) ada[y] = true; });
  return Object.keys(ada).map(Number);
}
export function pjDaftarTahun(kini) {
  const th = Number(hariIniIso(kini || new Date(Date.now())).slice(0, 4)); const ada = {}; ada[th] = true; pjTahunLalu(th).forEach((y) => { ada[y] = true; });
  return Object.keys(ada).map(Number).sort((a, b) => b - a).map((y) => ({ tahun: y, berjalan: y === th, ditutup: tahunDitutup(y), potret: !!potretTahun(y) }));
}
/** Masa yang masih harus disetor: PPh > 0 (juga "paling sedikit") dan setoran tercatat kurang dari itu. */
export const pjMasaTerutang = (b) => !b.berjalan && b.pph > 0 && b.jumlahSetor < b.pph;
/** Tahun yang dibuka bawaan: Januari–Maret = tahun lalu SELAMA masih ada masa terutang di sana (setoran Desember, SPT Tahunan 31 Mar); selain itu tahun berjalan. */
export function pjTahunBawaan(kini) {
  const iso = hariIniIso(kini || new Date(Date.now())); const th = Number(iso.slice(0, 4)); if (Number(iso.slice(5, 7)) > 3) return th;
  return pjDaftarTahun(kini).some((x) => x.tahun === th - 1) && pjTahun(th - 1, kini).daftar.some(pjMasaTerutang) ? th - 1 : th;
}
/** Tawaran "omzet tahun lalu" dari tahun yang tercatat di sistem (potret tutup buku / catatan hidup) + isian di luar sistem: kumulatif GABUNG tahun itu (dasar batas
 *  Rp4,8 miliar). null = tahun lalu tidak ada di sistem atau owner sudah mengisinya. Owner yang memutuskan memakainya (angka konsultan menang). */
export function pjTawarOmzetTahunLalu(th, kini) {
  const P = pjProfil(); const y = Number(th) - 1; if (pjOmzetTahunLalu(P, th) !== null || !pjDaftarTahun(kini).some((x) => x.tahun === y)) return null;
  const T = pjTahun(y, kini); if (!T.daftar.some((b) => b.sistem !== null || b.lama !== null)) return null;
  return { tahun: y, n: T.kumGabung, lengkap: T.lengkap, kosong: T.kosong, potret: T.potret, teks: 'Omzet ' + y + ' menurut sistem' + (T.potret ? ' (potret tutup buku)' : '') + ' + isian di luar sistem: ' + RP(T.kumGabung) + (T.lengkap ? '' : ' — ' + T.kosong + ' bulan belum diisi, bisa KURANG') };
}
export function susunOmzetTahunLaluDariSistem(th, w, kini) {
  const X = pjTawarOmzetTahunLalu(th, kini); if (!X) return { tolak: 'Tidak ada tawaran — omzet tahun ' + (Number(th) - 1) + ' sudah diisi atau tahun itu tidak tercatat di sistem' };
  const r = susunProfilPajak({ omzetTahunLalu: String(X.n), tahunPajak: th }, w); if (r.tolak) return r;
  r.patch = { kabar: 'Omzet tahun ' + X.tahun + ' diisi ' + RP(X.n) + ' dari sistem' + (X.lengkap ? '' : ' (BELUM lengkap — ' + X.kosong + ' bulan kosong)') + '. Kalau konsultan menyebut angka lain, ubah lewat "ubah profil". ' + PJ_LABEL + '.', kabarAwas: !X.lengkap, drafPj: null };
  return r;
}

// ==================== cetak: Rekap pajak untuk konsultan ====================
export function dokRekapPajak(T, kop) {
  const P = T.P; const baris = [{ nama: 'Profil wajib pajak', kelas: 'kel' }, { nama: 'Atas nama', teks: P.wpAtasNama || '(belum diisi)' },
    { nama: 'Jenis wajib pajak: ' + (PJ_JENIS_WP.find((j) => j.id === P.jenisWp) || {}).nama + (T.anggapanOp ? ' — ' + PJ_ANGGAPAN_OP : ''), teks: '' }, { nama: 'Status PKP', teks: (PJ_STATUS_PKP.find((j) => j.id === P.statusPkp) || {}).nama },
    { nama: 'Tahun mulai tarif final', teks: P.tahunMulaiTarifFinal === null ? 'tidak diketahui' : String(P.tahunMulaiTarifFinal) }, { nama: 'Omzet tahun ' + (T.tahun - 1), teks: T.omzetTahunLalu === null || T.omzetTahunLalu === undefined ? 'tidak diketahui' : RP(T.omzetTahunLalu) },
    { nama: 'Status pasangan: ' + (PJ_STATUS_PASANGAN.find((j) => j.id === P.statusPasangan) || {}).nama, teks: '' }, { nama: '  ' + (T.pasangan.belumTerverifikasi ? PJ_TANDA_BELUM + ' ' : '') + T.pasangan.teks, teks: '' },
    { nama: 'Tarif', teks: P.tarifPerMil ? (P.tarifPerMil / 10).toFixed(1).replace('.', ',') + ' %' : 'belum diatur' }, { nama: 'Batas bebas setahun', teks: P.batasBebas === null ? 'belum diisi' : RP(P.batasBebas) }, { nama: 'Batas atas setahun', teks: P.batasOmzet ? RP(P.batasOmzet) : 'belum diatur' },
    { nama: 'Dua angka omzet per bulan', kelas: 'kel' },
    { nama: 'Omzet mesin = dasar perkiraan PPh di rekap ini (penjualan berlaku, sesudah potongan nota & retur). Omzet sebelum potongan nota = omzet mesin + potongan nota + tawar di bawah harga daftar (dari hargaAsliSatuan), retur tetap dikurangi. PMK 164/2023 Pasal 6 ayat (2) menyebut peredaran bruto sebelum potongan penjualan.', teks: '' },
    { nama: 'Angka mana yang dipakai sebagai peredaran bruto DISERAHKAN KE KONSULTAN.', teks: '' },
    { nama: 'Per bulan ' + T.tahun + (T.potret ? ' · angka sistem dari potret tutup buku ' + T.tahun : T.tanpaPotret ? ' · sudah tutup buku TANPA potret — angka sistemnya hanya di berkas arsip' : ''), kelas: 'kel' }];
  T.daftar.forEach((b) => {
    const luar = [b.lama !== null ? 'catatan lama ' + RP(b.lama) : '', b.lain !== null ? 'usaha lain ' + RP(b.lain) : '', b.pasangan !== null ? 'usaha pasangan ' + RP(b.pasangan) + (b.pasanganIkutPph ? ' (ikut PPh' + (T.pasangan.anggapan ? ' — anggapan' : '') + ')' : ' (batas Rp4,8 miliar saja)') : ''].filter(Boolean).join(' · ');
    baris.push({ nama: b.nama + (b.sebagian ? ' (sistem mulai ' + tanggalPendek(b.awalSistem) + ')' : ''), teks: b.lengkap ? RP(b.omzet) : '—' });
    if (b.sistem !== null) baris.push({ nama: '  omzet mesin ' + RP(b.sistem) + ' · omzet sebelum potongan nota ' + RP(b.sebelumPotongan) + (b.potongan.jumlah ? ' (potongan nota ' + RP(b.potongan.nota) + (b.potongan.tawar ? ', tawar ' + RP(b.potongan.tawar) : '') + ' di ' + b.potongan.n + ' baris)' : ' (tidak ada potongan)'), teks: '' });
    baris.push({ nama: '  sistem ' + (b.sistem === null ? '—' : RP(b.sistem)) + (luar ? ' · diketik owner: ' + luar : '') + ' · kumulatif ' + RP(b.kum), teks: b.pph === null ? 'PPh tidak dihitung' : 'PPh ' + RP(b.pph) });
    baris.push({ nama: '  setoran ' + (b.setor.length ? RP(b.jumlahSetor) + (b.ntpn.length ? ' · NTPN ' + b.ntpn.join(', ') : ' · tanpa NTPN') : '—') + ' · ' + b.status.teks, teks: '' });
  });
  baris.push({ nama: 'Jumlah omzet mesin ' + T.tahun, teks: RP(T.totalSistem), kelas: 'jumlah' }, { nama: 'Jumlah omzet sebelum potongan nota ' + T.tahun, teks: RP(T.totalSebelumPotongan), kelas: 'jumlah' });
  baris.push({ nama: 'Jumlah perkiraan PPh ' + T.tahun, teks: T.totalPph === null ? 'tidak dihitung' : RP(T.totalPph), kelas: 'jumlah' }, { nama: 'Jumlah setoran tercatat', teks: RP(T.totalSetor), kelas: 'jumlah' });
  if (T.aturanSejakTutup) baris.push({ nama: '[DIUBAH SESUDAH TUTUP BUKU] ' + T.aturanSejakTutup, teks: '' });
  baris.push({ nama: 'Sumber aturan (dilihat 24 Sep 2026 · diperiksa untuk tahun pajak ' + PJ_SUMBER_TAHUN + ')', kelas: 'kel' }); if (T.aturanTahun && T.aturanTahun.belum) baris.push({ nama: '[BELUM DIPERIKSA UNTUK ' + T.tahun + '] ' + T.aturanTahun.teks, teks: '' });
  PJ_SUMBER.forEach((s) => baris.push({ nama: (s.terverifikasi ? '' : '[BELUM TERVERIFIKASI] ') + s.klaim, teks: '' }));
  return { jenis: 'pajak', kop, judul: 'Rekap Pajak untuk Konsultan', sub: 'Tahun ' + T.tahun + ' · ' + PJ_LABEL + (T.kosong ? ' · ' + T.kosong + ' bulan belum diisi' : ''), periode: String(T.tahun), baris, cap: T.kosong ? 'DATA BELUM LENGKAP' : '',
    catatan: 'Dua angka omzet per bulan (mesin & sebelum potongan nota) — pilihan angka yang dipakai diserahkan ke konsultan; perkiraan PPh di sini memakai omzet mesin. ' + T.kumTeks + '. ' + (T.ambang.ada ? 'Ambang: ' + T.ambang.teks + '. ' : '') + (T.peringatanTahunLalu ? T.peringatanTahunLalu + ' ' : '') + (P.sumberAturan ? 'Aturan: ' + P.sumberAturan.teks + ' (diisi ' + tanggalPendek(P.sumberAturan.tanggal) + ').' : 'Aturan belum diisi dari tombol.') };
}
