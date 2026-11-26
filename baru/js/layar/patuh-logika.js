// KALENDER KEPATUHAN · CEK ATURAN BULANAN · BENTUK USAHA (owner 26 Nov 2026, sensus ulang 1c: A16 A38 A45). Tanpa DOM, awalan pt.
// Keputusan owner: isi kalender "centang semuanya … tambahkan isi apa saja yang perlu … yang paling masuk akal" (semua bisa ditambah/ubah/hapus owner), yang boleh
// menandai "sudah dikerjakan" = OWNER + BEN dari tablet (rules v22), dan "pasang notifikasi" (push pagi lewat fungsi server functions/patuh.js + lonceng/pengingat).
//   · daftar butir & bentuk usaha = aturanToko/kepatuhan (owner menulis; v22: Penjaga laci MEMBACA dokumen itu). Belum ada dokumen = PT_BAWAAN.
//   · "sudah dikerjakan" = koleksi kepatuhanCek, TAMBAH-SAJA, satu dokumen per butir per putaran { id, tanggal, jam, butir, periode, catatan } + atribusi penulis
//     (v22: owner || stafCekPatuh(ben), kolom dibatasi; ubah & hapus owner). Bukan uang, bukan stok.
//   · putaran (okurensi) per butir: bulanan 'DD' · triwulan 'DD' (Jan/Apr/Jul/Okt) · tahunan 'MM-DD' · sekali 'YYYY-MM-DD'. Putaran yang dipakai = putaran TERAKHIR
//     yang sudah jatuh (≤ hari ini, tidak sebelum `mulai`) bila belum dikerjakan — lewat / hari ini; selain itu putaran BERIKUTNYA yang belum dikerjakan (boleh
//     dikerjakan lebih awal). Putaran bulanan/triwulan yang terlewat tidak menumpuk: putaran baru menggantikannya (cek aturan bulan ini mencakup bulan lalu).
//   · SPT Tahunan tanpa tanggal = ikut bentuk usaha: orang pribadi 31 Maret, badan 30 April. Butir tanpa tanggal (izin, tera ulang, THR) = "isi tanggalnya", tidak
//     mengingatkan. Tidak ada nasihat hukum/pajak: keterangan menyebut di mana mengeceknya; yang belum dibaca langsung di sumber resmi bertanda [BELUM TERVERIFIKASI].
// SATU RUMUS dengan functions/patuh.js (push pagi): uji_gudang_label_patuh menjalankan keduanya atas tanggal & data yang sama dan mewajibkan hasilnya sama.
import { cacheMentah } from '../data/toko.js';
import { hariIniIso, tanggalPendek } from '../inti/format.js';

export const PT_ID = 'kepatuhan';
export const PT_KOLEKSI = 'kepatuhanCek';
export const PT_MULAI = '2026-11-26';   // hari kalender lahir: putaran sebelum ini tidak ditagih (SPT 2025 sudah dilapor sebelum sistem ini)
export const PT_ULANG = [['bulanan', 'Tiap bulan'], ['triwulan', 'Tiap 3 bulan'], ['tahunan', 'Tiap tahun'], ['sekali', 'Sekali (tanggal tertentu)']].map((x) => ({ id: x[0], nama: x[1] }));
export const PT_BELUM = '[BELUM TERVERIFIKASI]';
export const PT_BATAS = { nama: 60, ket: 200, catatan: 160, hariSebelum: [0, 120], butir: 30 };
export const PT_CEK_KOLOM = ['id', 'tanggal', 'jam', 'butir', 'periode', 'catatan'];   // = kolom isi stafCekPatuh rules v22 (+ kolom atribusi penulis pusat)
export const PT_BENTUK = [['', 'Belum diisi', ''], ['perorangan', 'Usaha perorangan (orang pribadi)', 'op'], ['ptPerorangan', 'PT Perorangan', 'badan'], ['cv', 'CV', 'badan'], ['firma', 'Firma', 'badan'],
  ['koperasi', 'Koperasi', 'badan'], ['pt', 'PT', 'badan']].map((x) => ({ id: x[0], nama: x[1], wp: x[2] }));
export const PT_CATAT = [['', 'Belum diisi'], ['pencatatan', 'Pencatatan (omzet & beli)'], ['pembukuan', 'Pembukuan (neraca & laba rugi)']].map((x) => ({ id: x[0], nama: x[1] }));
// bawaan: urut tampil. kelompok 'aturan' = cek aturan tiap bulan (A16) — tiga butir, satu kartu.
export const PT_BAWAAN = [
  { id: 'spt', nama: 'Lapor SPT Tahunan', ulang: 'tahunan', tanggal: '', hariSebelum: 30, ket: 'tahun pajak lalu, lewat Coretax · orang pribadi paling lambat 31 Maret, badan 30 April (UU KUP Pasal 3 ayat 3) — tanggal kosong = ikut bentuk usaha' },
  { id: 'cek-het', nama: 'Cek HET beras', kelompok: 'aturan', ulang: 'bulanan', tanggal: '01', hariSebelum: 0, ket: 'situs Badan Pangan Nasional — kalau berubah, ubah di Harga & Pemasok › Katalog › HET' },
  { id: 'cek-qris', nama: 'Cek potongan QRIS', kelompok: 'aturan', ulang: 'bulanan', tanggal: '01', hariSebelum: 0, ket: 'tarif potongan GoPay Merchant & ketentuan Bank Indonesia — kalau berubah, catat di Uang keluar bertanda potongan QRIS' },
  { id: 'cek-pajak', nama: 'Cek aturan pajak UMKM', kelompok: 'aturan', ulang: 'bulanan', tanggal: '01', hariSebelum: 0, ket: 'situs DJP — tarif PPh final & batas omzet; aturan yang dipakai hitungan ada di Laporan › Pajak' },
  { id: 'izin', nama: 'Izin & legalitas usaha', ulang: 'sekali', tanggal: '', hariSebelum: 60, ket: 'NIB, izin edar beras kemasan, sertifikat lain — isi tanggal habis berlakunya; satu baris per izin (Tambah butir)' },
  { id: 'label', nama: 'Periksa label kemasan', ulang: 'triwulan', tanggal: '01', hariSebelum: 7, ket: 'kelas mutu, berat bersih, alamat & umur simpan di Jual › Label & kartu masih benar' },
  { id: 'tera', nama: 'Tera ulang timbangan', ulang: 'tahunan', tanggal: '', hariSebelum: 30, ket: 'timbangan untuk jual-beli wajib ditera ulang berkala (UU Metrologi Legal) — jadwalnya tanya UPTD Metrologi daerah, lalu isi tanggalnya' },
  { id: 'thr', nama: 'THR karyawan', ulang: 'sekali', tanggal: '', hariSebelum: 14, ket: 'paling lambat 7 hari sebelum Lebaran — tanggal Lebaran berganti tiap tahun, isi ulang tiap tahun' },
  { id: 'tutup', nama: 'Tutup buku akhir tahun', ulang: 'tahunan', tanggal: '12-31', hariSebelum: 14, ket: 'Uang › Tutup buku — cadangan berkas dulu, lalu ritualnya' },
];

const ptHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const ptIso = (y, m, d) => { const akhir = new Date(Date.UTC(y, m, 0)).getUTCDate(); return y + '-' + String(m).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0'); };
const ptTeks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
/** Tanggal butir sah untuk ulangnya? bulanan/triwulan 'DD' 01–31 · tahunan 'MM-DD' · sekali 'YYYY-MM-DD' · '' (belum diisi) selalu sah. */
export function ptTanggalSah(ulang, t) {
  const s = String(t || ''); if (!s) return true;
  if (ulang === 'bulanan' || ulang === 'triwulan') return /^\d{2}$/.test(s) && Number(s) >= 1 && Number(s) <= 31;
  if (ulang === 'tahunan') { if (!/^\d{2}-\d{2}$/.test(s)) return false; const m = Number(s.slice(0, 2)), d = Number(s.slice(3)); return m >= 1 && m <= 12 && d >= 1 && d <= new Date(Date.UTC(2024, m, 0)).getUTCDate(); }
  if (ulang === 'sekali') return /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + 'T00:00:00Z').getTime()) && new Date(s + 'T00:00:00Z').toISOString().slice(0, 10) === s;
  return false;
}
/** Kunci putaran dari tanggal jatuhnya: bulanan 'YYYY-MM' · triwulan 'YYYY-Kn' · tahunan 'YYYY' · sekali tanggal itu sendiri. */
export function ptPeriode(ulang, jatuh) {
  const y = jatuh.slice(0, 4), m = Number(jatuh.slice(5, 7));
  return ulang === 'bulanan' ? jatuh.slice(0, 7) : ulang === 'triwulan' ? y + '-K' + (Math.floor((m - 1) / 3) + 1) : ulang === 'tahunan' ? y : jatuh;
}
/** Tanggal jatuh putaran ke-k sesudah/sebelum (k = 0 = siklus yang memuat `iso`). */
function ptJatuhSiklus(ulang, tgl, iso, k) {
  const y = Number(iso.slice(0, 4)), m = Number(iso.slice(5, 7));
  if (ulang === 'bulanan') { const t = y * 12 + (m - 1) + k; return ptIso(Math.floor(t / 12), t % 12 + 1, Number(tgl)); }
  if (ulang === 'triwulan') { const q = y * 4 + Math.floor((m - 1) / 3) + k; return ptIso(Math.floor(q / 4), (q % 4) * 3 + 1, Number(tgl)); }
  return ptIso(y + k, Number(tgl.slice(0, 2)), Number(tgl.slice(3)));
}
/** Tanggal yang berlaku untuk butir (SPT tanpa tanggal ikut bentuk usaha: badan 04-30, selain itu 03-31). */
export function ptTanggalBerlaku(b, wp) { return b.id === 'spt' && !b.tanggal ? (wp === 'badan' ? '04-30' : '03-31') : String(b.tanggal || ''); }
/**
 * Putaran yang sedang berlaku untuk satu butir. sudah(periode) → true bila putaran itu sudah dikerjakan. → { jatuh, periode, sisa (hari; < 0 = lewat) } atau
 * { tanpaTanggal: true } (butir belum diberi tanggal) atau { selesai: true, periode } (sekali, sudah dikerjakan).
 */
export function ptPutaran(b, iso, sudah, wp) {
  const tgl = ptTanggalBerlaku(b, wp); if (!tgl || !ptTanggalSah(b.ulang, tgl)) return { tanpaTanggal: true };
  if (b.ulang === 'sekali') { const p = ptPeriode('sekali', tgl); return sudah(p) ? { selesai: true, periode: p, jatuh: tgl } : { jatuh: tgl, periode: p, sisa: ptHariKe(tgl) - ptHariKe(iso) }; }
  const mulai = b.mulai && /^\d{4}-\d{2}-\d{2}$/.test(String(b.mulai)) ? String(b.mulai) : PT_MULAI;
  let lalu = ptJatuhSiklus(b.ulang, tgl, iso, 0); if (lalu > iso) lalu = ptJatuhSiklus(b.ulang, tgl, iso, -1);
  if (lalu >= mulai && !sudah(ptPeriode(b.ulang, lalu))) return { jatuh: lalu, periode: ptPeriode(b.ulang, lalu), sisa: ptHariKe(lalu) - ptHariKe(iso) };
  for (let k = 0; k <= 3; k++) { const j = ptJatuhSiklus(b.ulang, tgl, iso, k); if (j <= iso) continue; if (!sudah(ptPeriode(b.ulang, j))) return { jatuh: j, periode: ptPeriode(b.ulang, j), sisa: ptHariKe(j) - ptHariKe(iso) }; }
  return { tanpaTanggal: true };
}

/** Dokumen aturanToko/kepatuhan (owner & Penjaga laci membaca, owner menulis). */
const ptDok = () => cacheMentah('aturan').find((d) => String(d.id) === PT_ID) || null;
/** Butir yang berlaku + bentuk usaha. Dokumen belum ada → bawaan (dariOwner false). Butir rusak dari dokumen dilewati (tidak menjatuhkan kalender). */
export function ptAtur() {
  const d = ptDok(); const daftar = d && Array.isArray(d.butir) ? d.butir : PT_BAWAAN; const seen = {};
  const butir = daftar.filter((b) => b && typeof b === 'object' && /^[a-z0-9-]{1,40}$/.test(String(b.id || '')) && PT_ULANG.some((u) => u.id === b.ulang) && !seen[b.id] && (seen[b.id] = 1))
    .map((b) => ({ id: String(b.id), nama: ptTeks(b.nama).slice(0, PT_BATAS.nama) || String(b.id), ulang: b.ulang, tanggal: ptTanggalSah(b.ulang, b.tanggal) ? String(b.tanggal || '') : '',
      hariSebelum: Math.max(PT_BATAS.hariSebelum[0], Math.min(PT_BATAS.hariSebelum[1], Math.round(Number(b.hariSebelum) || 0))), ket: ptTeks(b.ket).slice(0, PT_BATAS.ket), nyala: b.nyala !== false,
      kelompok: b.kelompok === 'aturan' ? 'aturan' : '', mulai: /^\d{4}-\d{2}-\d{2}$/.test(String(b.mulai || '')) ? String(b.mulai) : '' }));
  const u = d && d.usaha && typeof d.usaha === 'object' ? d.usaha : {};
  const bentuk = PT_BENTUK.some((x) => x.id === u.bentuk) ? String(u.bentuk || '') : ''; const catat = PT_CATAT.some((x) => x.id === u.catat) ? String(u.catat || '') : '';
  const konf = u.konfirmasi && typeof u.konfirmasi === 'object' ? { tanggal: /^\d{4}-\d{2}-\d{2}$/.test(String(u.konfirmasi.tanggal || '')) ? String(u.konfirmasi.tanggal) : '', ke: ptTeks(u.konfirmasi.ke).slice(0, 60), catatan: ptTeks(u.konfirmasi.catatan).slice(0, 200) } : { tanggal: '', ke: '', catatan: '' };
  return { butir, usaha: { bentuk, catat, konfirmasi: konf, wp: (PT_BENTUK.find((x) => x.id === bentuk) || {}).wp || '' }, dariOwner: !!d, sejak: d ? String(d.tanggal || '') : '' };
}
/** Catatan "sudah dikerjakan" (kepatuhanCek) per butir: { butirId: [ { id, tanggal, jam, periode, catatan, oleh } ] } terbaru dulu. */
export function ptCek() {
  const out = {}; cacheMentah(PT_KOLEKSI).filter((d) => d && typeof d.butir === 'string' && typeof d.periode === 'string').slice()
    .sort((a, b) => String(b.tanggal + ' ' + (b.jam || '')).localeCompare(String(a.tanggal + ' ' + (a.jam || ''))) || String(b.id).localeCompare(String(a.id)))
    .forEach((d) => { (out[d.butir] = out[d.butir] || []).push({ id: String(d.id), tanggal: String(d.tanggal || ''), jam: String(d.jam || ''), periode: d.periode, catatan: String(d.catatan || ''), oleh: String(d.oleh || '') }); });
  return out;
}

/**
 * Kalender kepatuhan untuk satu hari: tiap butir yang menyala dengan putaran berlakunya, keadaan (lewat · hariIni · segera (≤ hariSebelum) · nanti · tanpaTanggal ·
 * selesai), terakhir dikerjakan & oleh siapa. Cek aturan bulanan (A16): kuning bila terakhir dicek > 30 hari / belum pernah.
 */
export function ptKalender(kini) {
  const iso = hariIniIso(kini); const A = ptAtur(); const C = ptCek();
  const baris = A.butir.map((b) => { const riw = C[b.id] || []; const P = ptPutaran(b, iso, (p) => riw.some((x) => x.periode === p), A.usaha.wp); const akhir = riw[0] || null;
    const keadaan = !b.nyala ? 'mati' : P.tanpaTanggal ? 'tanpaTanggal' : P.selesai ? 'selesai' : P.sisa < 0 ? 'lewat' : P.sisa === 0 ? 'hariIni' : P.sisa <= b.hariSebelum ? 'segera' : 'nanti';
    // A16: kuning bila terakhir dicek > 30 hari lalu; belum pernah dicek = kuning hanya sesudah putaran pertamanya lewat (hari pertama kalender tidak langsung kuning)
    const basi = b.kelompok === 'aturan' && b.nyala !== false && (akhir ? ptHariKe(iso) - ptHariKe(akhir.tanggal) > 30 : keadaan === 'lewat');
    return Object.assign({}, b, P, { keadaan, akhir, riwayat: riw.slice(0, 6), basi, tanggalBerlaku: ptTanggalBerlaku(b, A.usaha.wp),
      teks: P.tanpaTanggal ? 'isi tanggalnya di Atur kalender' : P.selesai ? 'sudah dikerjakan ' + tanggalPendek(akhir ? akhir.tanggal : '') : tanggalPendek(P.jatuh) + ' · ' + (P.sisa < 0 ? 'lewat ' + (-P.sisa) + ' hari' : P.sisa === 0 ? 'hari ini' : P.sisa + ' hari lagi') }); });
  const perlu = baris.filter((x) => x.keadaan === 'lewat' || x.keadaan === 'hariIni' || x.keadaan === 'segera').sort((a, b) => a.sisa - b.sisa);
  const aturan = baris.filter((x) => x.kelompok === 'aturan');
  return { iso, baris, perlu, aturan, aturanBasi: aturan.filter((x) => x.basi && x.nyala), usaha: A.usaha, dariOwner: A.dariOwner,
    kalimat: perlu.length ? perlu.length + ' urusan: ' + perlu.slice(0, 3).map((x) => x.nama + ' (' + x.teks + ')').join(' · ') : 'Tidak ada urusan kepatuhan yang dekat', sumber: 'Laporan › Pajak › Kalender', tujuan: { ke: 'laporan', keluarga: 'pajak', tab: 'kalender' } };
}
/** Sumber pengingat jenis 'patuh' (app.js lewat lokal.patuh): butir menyala bertanggal yang belum dikerjakan — hariSebelum per butir. */
export function ptSumberPengingat(kini) {
  const K = ptKalender(kini);
  return K.baris.filter((x) => x.nyala && !x.tanpaTanggal && !x.selesai).map((x) => ({ id: 'patuh|' + x.id + '|' + x.periode, jenis: 'patuh', kunci: x.id, teks: x.nama, siapa: 'kepatuhan', jatuh: x.jatuh,
    hariSebelum: x.hariSebelum, n: 0, ket: x.ket, butir: x.id, periode: x.periode }));
}

/** Tandai satu putaran butir "sudah dikerjakan" (owner atau Penjaga laci). Satu dokumen kepatuhanCek; putaran yang sudah ditandai ditolak (tidak dobel). */
export function susunCentangPatuh(butirId, periode, catatan, w, kini) {
  const K = ptKalender(kini || new Date(w.kini)); const b = K.baris.find((x) => x.id === String(butirId));
  if (!b) return { tolak: 'Butir kalender itu tidak ada lagi — muat ulang' };
  if (b.tanpaTanggal) return { tolak: b.nama + ' belum punya tanggal — owner mengisinya dulu di Atur kalender' };
  const p = String(periode || b.periode || ''); if (!p) return { tolak: 'Putarannya tidak dikenal' };
  if ((b.riwayat || []).some((x) => x.periode === p) || (ptCek()[b.id] || []).some((x) => x.periode === p)) return { tolak: b.nama + ' putaran ini sudah ditandai dikerjakan' };
  const cat = ptTeks(catatan); if (cat.length > PT_BATAS.catatan) return { tolak: 'Catatan paling panjang ' + PT_BATAS.catatan + ' huruf' };
  if (b.keadaan === 'lewat' && cat.length < 3) return { tolak: 'Sudah lewat — tulis catatan singkat (mis. tanggal dikerjakan / nomor bukti)' };
  const data = { id: 'kp-' + w.tanggal + '-' + String(w.idUnik()).replace(/[^0-9a-z]/gi, '').slice(-10), tanggal: w.tanggal, jam: w.jam, butir: b.id, periode: p, catatan: cat };
  return { dokumen: [{ koleksi: 'kepatuhanCek', data }], patch: { ptBuka: null, ptCatatan: '', kabarAwas: false, kabar: b.nama + ' ditandai sudah dikerjakan (' + p + ')' + (b.ulang === 'sekali' ? '' : ' — berikutnya diingatkan lagi') } };
}

/** Simpan butir kalender + bentuk usaha (owner). isi = { butir: [ { id?, nama, ulang, tanggal, hariSebelum, ket, nyala, kelompok, mulai } ], usaha: { bentuk, catat, konfirmasi } }. */
export function susunAturPatuh(isi, w) {
  const a = isi || {}; const kini = ptAtur(); const daftar = Array.isArray(a.butir) ? a.butir : kini.butir; const seen = {}; const butir = []; let tolak = '';
  if (daftar.length > PT_BATAS.butir) return { tolak: 'Paling banyak ' + PT_BATAS.butir + ' butir' };
  daftar.forEach((b, i) => { if (tolak || !b) return; const nama = ptTeks(b.nama); const ulang = String(b.ulang || ''); const t = String(b.tanggal || '').trim();
    if (!nama) { tolak = 'Butir ke-' + (i + 1) + ': nama wajib diisi'; return; } if (nama.length > PT_BATAS.nama) { tolak = nama.slice(0, 20) + '…: nama paling panjang ' + PT_BATAS.nama + ' huruf'; return; }
    if (!PT_ULANG.some((u) => u.id === ulang)) { tolak = nama + ': pilih tiap bulan / 3 bulan / tahun / sekali'; return; }
    if (!ptTanggalSah(ulang, t)) { tolak = nama + ': tanggal ' + (ulang === 'tahunan' ? 'BB-HH (mis. 03-31)' : ulang === 'sekali' ? 'TTTT-BB-HH' : 'tanggal 01–31') + ' — atau kosongkan'; return; }
    const h = Number(String(b.hariSebelum === undefined ? 0 : b.hariSebelum).trim() || 0); if (!isFinite(h) || Math.round(h) !== h || h < PT_BATAS.hariSebelum[0] || h > PT_BATAS.hariSebelum[1]) { tolak = nama + ': ingatkan ' + PT_BATAS.hariSebelum[0] + '–' + PT_BATAS.hariSebelum[1] + ' hari sebelum (bilangan bulat)'; return; }
    const ket = ptTeks(b.ket); if (ket.length > PT_BATAS.ket) { tolak = nama + ': keterangan paling panjang ' + PT_BATAS.ket + ' huruf'; return; }
    let id = String(b.id || ''); if (!/^[a-z0-9-]{1,40}$/.test(id)) id = 'b' + String(w.idUnik()).replace(/[^0-9a-z]/gi, '').slice(-10).toLowerCase(); if (seen[id]) { tolak = nama + ': kembar dengan butir lain'; return; } seen[id] = 1;
    butir.push(Object.assign({ id, nama, ulang, tanggal: t, hariSebelum: h, ket, nyala: b.nyala !== false }, b.kelompok === 'aturan' ? { kelompok: 'aturan' } : {}, { mulai: /^\d{4}-\d{2}-\d{2}$/.test(String(b.mulai || '')) ? String(b.mulai) : (kini.butir.some((x) => x.id === id) ? '' : w.tanggal) })); });
  if (tolak) return { tolak };
  const u = a.usaha || kini.usaha; const bentuk = String(u.bentuk || ''); const catat = String(u.catat || ''); const k = u.konfirmasi || {};
  if (!PT_BENTUK.some((x) => x.id === bentuk)) return { tolak: 'Bentuk usaha tidak dikenal' }; if (!PT_CATAT.some((x) => x.id === catat)) return { tolak: 'Pencatatan / pembukuan tidak dikenal' };
  const kt = String(k.tanggal || ''); if (kt && !ptTanggalSah('sekali', kt)) return { tolak: 'Tanggal konfirmasi TTTT-BB-HH — atau kosongkan' };
  const usaha = { bentuk, catat, konfirmasi: { tanggal: kt, ke: ptTeks(k.ke).slice(0, 60), catatan: ptTeks(k.catatan).slice(0, 200) } };
  const lama = ptDok() || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: PT_ID, tanggal: w.tanggal, jam: w.jam, butir, usaha }) }],
    patch: { ptAtur: null, kabarAwas: false, kabar: 'Kalender kepatuhan disimpan — ' + butir.filter((x) => x.nyala).length + ' butir menyala' + (bentuk ? ' · ' + PT_BENTUK.find((x) => x.id === bentuk).nama : '') } };
}

/** Bentuk usaha vs jenis wajib pajak di Laporan › Pajak (A45): kalimat bila keduanya terisi tapi tidak sejalan; PKP: PPN belum dicatat sistem. */
export function ptCocokPajak(usaha, jenisWp, statusPkp) {
  const out = []; const wp = (usaha && usaha.wp) || '';
  if (wp && jenisWp && jenisWp !== 'belumDiketahui' && ((wp === 'op') !== (jenisWp === 'orangPribadi'))) out.push('Bentuk usaha (' + (PT_BENTUK.find((x) => x.id === usaha.bentuk) || {}).nama + ') tidak sejalan dengan jenis wajib pajak di profil pajak (' + (jenisWp === 'badan' ? 'badan' : 'orang pribadi') + ') — samakan salah satunya.');
  if (!wp) out.push('Bentuk usaha belum diisi — tanggal SPT Tahunan dianggap orang pribadi (31 Maret).');
  if (statusPkp === 'pkp') out.push('Status PKP: PPN keluaran & masukan BELUM dicatat sistem ini — hitungan pajak di sini hanya PPh final. Konfirmasi ke KPP / konsultan.');
  if (usaha && usaha.bentuk && !usaha.konfirmasi.tanggal) out.push('Bentuk usaha & kewajiban catat belum pernah dikonfirmasi ke KPP / konsultan ' + PT_BELUM + '.');
  return out;
}

/** Dasbor (kelompok mutu): urusan yang dekat / lewat + cek aturan yang basi — angka yang SAMA dengan Laporan › Pajak › Kalender. */
export function ptDasbor(kini) {
  const K = ptKalender(kini);
  return { n: K.perlu.length, lewat: K.perlu.filter((x) => x.keadaan === 'lewat').length, daftar: K.perlu.slice(0, 3).map((x) => ({ nama: x.nama, teks: x.teks, awas: x.keadaan === 'lewat' })),
    basi: K.aturanBasi.map((x) => x.nama), kalimat: K.kalimat, tujuan: K.tujuan };
}
