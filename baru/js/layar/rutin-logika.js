// DAFTAR CENTANG RUTIN · harian · mingguan · bulanan (owner 27 Nov 2026, sensus ulang A143 — paket P6). Tanpa DOM, awalan rn.
// Keputusan owner: SATU daftar rutin yang dicentang (dan siapa yang mencentang), yang boleh mencentang = OWNER + PENJAGA LACI + KARYAWAN → rules v25:
//   · daftar butir = aturanToko/rutin (owner menulis; v25: Penjaga laci & karyawan MEMBACA dokumen itu). Belum ada dokumen = RN_BAWAAN (disusun Claude dari
//     ritual yang sudah ada di sistem + yang lazim di toko beras; owner boleh ubah / matikan / hapus / tambah — sumber 30 butir dokumen riset owner tidak ada di repo).
//   · centang = koleksi rutinCek, TAMBAH-SAJA, satu dokumen per centang { id, tanggal, jam, butir, periode, catatan } + atribusi penulis (v25: owner ||
//     stafCekRutin(ben, karyawan), kolom dibatasi; ubah & hapus owner). Bukan uang, bukan stok. Dua centang untuk butir & putaran yang sama = yang PERTAMA dihitung.
//   · butir OTOMATIS = ritual yang sudah tercatat di layarnya sendiri (tidak dicentang ulang, satu sumber): hitung laci tablet (persetujuan hitungLaci), tutup hari
//     (tutupHari), cek wadah (wbCekHari), karcis darurat (daftarKarcis), cek mingguan gudang (gdCekGudang), cadangan berkas (cadanganCatatan), opname rutin
//     (gdOpname), cek aturan bulanan (kalender kepatuhan, kelompok 'aturan'). Yang tidak terbaca akun itu (mis. tutup hari untuk karyawan) disebut, bukan ditebak.
//   · putaran: harian = tanggal · mingguan = tanggal SENIN minggu itu · bulanan = 'YYYY-MM'. Jatuh: harian hari itu · mingguan pada `hari` (1 = Senin … 7 = Minggu) ·
//     bulanan pada tanggal `hari` (0 = akhir bulan). Sebelum jatuh = "nanti" (boleh dicentang lebih awal); sesudah jatuh belum = "lewat". Putaran sebelum RN_MULAI
//     tidak ditagih.
import { cacheMentah, ambilTutupHari } from '../data/toko.js';
import { hariIniIso, tanggalPendek } from '../inti/format.js';
import { gdCekGudang, gdOpname } from './gudang-logika.js';
import { wbCekHari } from './wadah-bernama-logika.js';
import { ptKalender } from './patuh-logika.js';
import { daftarKarcis } from './karcis-logika.js';

export const RN_ID = 'rutin';
export const RN_KOLEKSI = 'rutinCek';
export const RN_MULAI = '2026-11-27';   // hari daftar rutin lahir: putaran sebelum ini tidak ditagih
export const RN_HL = 'hitungLaci';       // = HL_TINDAKAN tutup-hari-logika (uji_rutin_staf membandingkannya)
export const RN_ULANG = [['harian', 'Tiap hari'], ['mingguan', 'Tiap minggu'], ['bulanan', 'Tiap bulan']].map((x) => ({ id: x[0], nama: x[1] }));
export const RN_UNTUK = [['semua', 'Semua yang jaga'], ['penjaga', 'Penjaga laci'], ['owner', 'Owner']].map((x) => ({ id: x[0], nama: x[1] }));
export const RN_HARI = ['', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
export const RN_BATAS = { nama: 60, ket: 160, catatan: 160, butir: 40 };
export const RN_CEK_KOLOM = ['id', 'tanggal', 'jam', 'butir', 'periode', 'catatan'];   // = kolom isi stafCekRutin rules v25 (+ kolom atribusi penulis pusat)
// sumber butir otomatis: kunci → { nama sumber, tujuan }. Dibaca rnOtomatis.
export const RN_OTOMATIS = { hitungLaci: 'kartu Tutup hari di tablet', tutup: 'Uang › Tutup hari', cekWadah: 'Tutup hari › Cek wadah', karcis: 'Jual › Karcis kasir',
  cekGudang: 'kartu Cek mingguan gudang', cadangan: 'Menu › Toko ini › Cadangan & simpanan', opname: 'Stok › Cocokkan', aturan: 'Laporan › Pajak › Kalender' };
// bawaan: urut tampil per kelompok. untuk: siapa yang mengerjakan (owner melihat & boleh mencentang semuanya).
export const RN_BAWAAN = [
  // ---- harian: buka toko
  { id: 'buka-timbang', nama: 'Nol-kan & cek timbangan sebelum buka', ulang: 'harian', untuk: 'semua', ket: 'taruh beban yang beratnya pasti (mis. kantong 5 kg) — angkanya harus pas' },
  { id: 'buka-kembalian', nama: 'Siapkan uang kembalian di laci', ulang: 'harian', untuk: 'penjaga', ket: 'pecahan kecil cukup untuk sehari' },
  { id: 'buka-harga', nama: 'Papan harga sama dengan harga di kasir', ulang: 'harian', untuk: 'penjaga', ket: 'kalau beda, kabari owner — harga diubah owner di Harga & Pemasok' },
  { id: 'buka-wadah', nama: 'Isi wadah literan yang tipis sebelum ramai', ulang: 'harian', untuk: 'semua', ket: 'tuangannya dicatat di Stok › Wadah literan' },
  { id: 'bersih', nama: 'Sapu & rapikan toko, buang karung bekas', ulang: 'harian', untuk: 'semua', ket: '' },
  { id: 'palet', nama: 'Karung di atas palet, tidak menempel dinding', ulang: 'harian', untuk: 'semua', ket: 'karung yang menempel lantai / dinding cepat lembap' },
  // ---- harian: sepanjang hari & tutup
  { id: 'nota', nama: 'Semua jualan masuk kasir (tanpa nota tulisan tangan)', ulang: 'harian', untuk: 'semua', ket: 'kalau terpaksa pakai karcis, rinci hari itu juga' },
  { id: 'karcis', nama: 'Karcis darurat hari ini sudah dirinci', ulang: 'harian', untuk: 'penjaga', otomatis: 'karcis', ket: 'terbaca dari Jual › Karcis kasir' },
  { id: 'uang-keluar', nama: 'Uang keluar hari ini sudah dicatat semua', ulang: 'harian', untuk: 'penjaga', ket: 'bensin, makan, plastik — dari tablet jadi titipan ke owner' },
  { id: 'cek-wadah', nama: 'Cek wadah literan saat tutup', ulang: 'harian', untuk: 'semua', otomatis: 'cekWadah', ket: 'terbaca dari Cek wadah (sesuai · lupa isi ulang · dikosongkan)' },
  { id: 'hitung-laci', nama: 'Hitung laci & kirim ke owner', ulang: 'harian', untuk: 'penjaga', otomatis: 'hitungLaci', ket: 'terbaca dari kartu Tutup hari di tablet' },
  { id: 'tutup-hari', nama: 'Tutup hari (cek QRIS, sisihkan laba)', ulang: 'harian', untuk: 'owner', otomatis: 'tutup', ket: 'terbaca dari Uang › Tutup hari' },
  { id: 'kunci', nama: 'Kunci brankas & pintu, matikan listrik yang tidak perlu', ulang: 'harian', untuk: 'semua', ket: '' },
  // ---- mingguan
  { id: 'cek-gudang', nama: 'Cek timbangan & gudang (palet, bocor, lembap, kutu)', ulang: 'mingguan', hari: 1, untuk: 'penjaga', otomatis: 'cekGudang', ket: 'terbaca dari Cek mingguan gudang' },
  { id: 'putar-karung', nama: 'Putar tumpukan: karung lama di depan', ulang: 'mingguan', hari: 1, untuk: 'semua', ket: 'yang masuk duluan keluar duluan' },
  { id: 'stok-tipis', nama: 'Cek stok tipis & kabari owner untuk pesan', ulang: 'mingguan', hari: 1, untuk: 'penjaga', ket: 'lihat Stok › Gudang (perkiraan hari tersisa)' },
  { id: 'tagih-bon', nama: 'Tagih bon pelanggan yang lewat janji', ulang: 'mingguan', hari: 2, untuk: 'penjaga', ket: 'Pelanggan › Bon › Papan tagih' },
  { id: 'kantong', nama: 'Hitung sisa kantong, label & benang jahit', ulang: 'mingguan', hari: 4, untuk: 'penjaga', ket: 'kalau menipis, kabari owner' },
  { id: 'bersih-gudang', nama: 'Bersihkan gudang & lap wadah literan', ulang: 'mingguan', hari: 6, untuk: 'semua', ket: '' },
  { id: 'banding', nama: 'Tanya harga ke pemasok (banding)', ulang: 'mingguan', hari: 5, untuk: 'owner', ket: 'Harga & Pemasok › Banding' },
  { id: 'cadangan', nama: 'Unduh cadangan berkas', ulang: 'mingguan', hari: 7, untuk: 'owner', otomatis: 'cadangan', ket: 'terbaca dari Menu › Toko ini › Cadangan & simpanan' },
  // ---- bulanan
  { id: 'cek-aturan', nama: 'Cek aturan bulanan (HET, potongan QRIS, pajak)', ulang: 'bulanan', hari: 1, untuk: 'owner', otomatis: 'aturan', ket: 'terbaca dari kalender kepatuhan' },
  { id: 'alat', nama: 'Cek alat: timbangan, printer, tablet, mesin jahit karung', ulang: 'bulanan', hari: 1, untuk: 'penjaga', ket: 'yang rusak kabari owner' },
  { id: 'opname', nama: 'Opname rutin sesuai jadwal', ulang: 'bulanan', hari: 15, untuk: 'owner', otomatis: 'opname', ket: 'terbaca dari Stok › Cocokkan (jadwal di Atur pengingat)' },
  { id: 'pajak', nama: 'Setor PPh final bulan lalu', ulang: 'bulanan', hari: 15, untuk: 'owner', ket: 'Laporan › Pajak' },
  { id: 'tagihan', nama: 'Bayar listrik, internet & tagihan tetap', ulang: 'bulanan', hari: 20, untuk: 'owner', ket: 'Uang › Tagihan' },
  { id: 'upah', nama: 'Hitung hari kerja & upah karyawan', ulang: 'bulanan', hari: 0, untuk: 'owner', ket: 'Uang › Upah' },
  { id: 'rekening', nama: 'Cocokkan saldo rekening usaha', ulang: 'bulanan', hari: 0, untuk: 'owner', ket: 'Uang › Rekening' },
  { id: 'rapor', nama: 'Baca rapor bulan ini & pasang target bulan depan', ulang: 'bulanan', hari: 0, untuk: 'owner', ket: 'Laporan › Rapor' },
  { id: 'tinjau-rutin', nama: 'Tinjau daftar rutin ini (tambah / buang)', ulang: 'bulanan', hari: 0, untuk: 'owner', ket: 'Menu › Toko ini › Rutin › Atur daftar' },
];

const rnHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const rnTambah = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const rnTeks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
/** Hari ke-berapa dalam minggu (1 = Senin … 7 = Minggu). */
export const rnHariMinggu = (iso) => { const g = new Date(String(iso) + 'T00:00:00Z').getUTCDay(); return g === 0 ? 7 : g; };
/** Senin minggu yang memuat `iso`. */
export const rnSenin = (iso) => rnTambah(iso, 1 - rnHariMinggu(iso));
const rnAkhirBulan = (key) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)); return key + '-' + String(new Date(Date.UTC(y, m, 0)).getUTCDate()).padStart(2, '0'); };
/** Kunci putaran butir pada hari `iso`. */
export function rnPeriode(ulang, iso) { return ulang === 'harian' ? iso : ulang === 'mingguan' ? rnSenin(iso) : iso.slice(0, 7); }
/** Tanggal jatuh putaran yang memuat `iso`. */
export function rnJatuh(b, iso) {
  if (b.ulang === 'harian') return iso;
  if (b.ulang === 'mingguan') return rnTambah(rnSenin(iso), Math.max(1, Math.min(7, Number(b.hari) || 1)) - 1);
  const key = iso.slice(0, 7); const akhir = rnAkhirBulan(key); const h = Math.round(Number(b.hari) || 0); return h >= 1 && h <= 28 ? key + '-' + String(h).padStart(2, '0') : akhir;
}
/** Teks jadwal satu butir ("tiap hari" · "tiap Senin" · "tiap tgl 15" · "tiap akhir bulan"). */
export function rnJadwal(b) { return b.ulang === 'harian' ? 'tiap hari' : b.ulang === 'mingguan' ? 'tiap ' + RN_HARI[Math.max(1, Math.min(7, Number(b.hari) || 1))] : Number(b.hari) >= 1 && Number(b.hari) <= 28 ? 'tiap tgl ' + Number(b.hari) : 'tiap akhir bulan'; }

const rnDok = () => cacheMentah('aturan').find((d) => String(d.id) === RN_ID) || null;
/** Butir yang berlaku. Dokumen belum ada → bawaan (dariOwner false). Butir rusak dilewati (tidak menjatuhkan daftar). */
export function rnAtur() {
  const d = rnDok(); const daftar = d && Array.isArray(d.butir) ? d.butir : RN_BAWAAN; const seen = {};
  const butir = daftar.filter((b) => b && typeof b === 'object' && /^[a-z0-9-]{1,40}$/.test(String(b.id || '')) && RN_ULANG.some((u) => u.id === b.ulang) && !seen[b.id] && (seen[b.id] = 1))
    .map((b) => ({ id: String(b.id), nama: rnTeks(b.nama).slice(0, RN_BATAS.nama) || String(b.id), ulang: b.ulang, hari: b.ulang === 'mingguan' ? Math.max(1, Math.min(7, Math.round(Number(b.hari) || 1))) : b.ulang === 'bulanan' ? Math.max(0, Math.min(28, Math.round(Number(b.hari) || 0))) : 0,
      untuk: RN_UNTUK.some((u) => u.id === b.untuk) ? b.untuk : 'semua', ket: rnTeks(b.ket).slice(0, RN_BATAS.ket), otomatis: RN_OTOMATIS[b.otomatis] ? String(b.otomatis) : '', nyala: b.nyala !== false }));
  return { butir, dariOwner: !!d, sejak: d ? String(d.tanggal || '') : '' };
}
/** Centang per butir per putaran: { butirId: { periode: { id, tanggal, jam, oleh, catatan } } } — yang PERTAMA ditulis dihitung (dua orang mencentang bersamaan). */
export function rnCek() {
  const out = {}; cacheMentah(RN_KOLEKSI).filter((d) => d && typeof d.butir === 'string' && typeof d.periode === 'string').slice()
    .sort((a, b) => String(a.tanggal + ' ' + (a.jam || '')).localeCompare(String(b.tanggal + ' ' + (b.jam || ''))) || String(a.id).localeCompare(String(b.id)))
    .forEach((d) => { const p = (out[d.butir] = out[d.butir] || {}); if (!p[d.periode]) p[d.periode] = { id: String(d.id), tanggal: String(d.tanggal || ''), jam: String(d.jam || ''), oleh: String(d.oleh || ''), catatan: String(d.catatan || '') }; });
  return out;
}
/** Siapa akun ini dalam daftar rutin: 'owner' · 'penjaga' (ben) · 'semua' (karyawan) · '' (tidak bekerja). */
export const rnPeran = (akun) => (!akun ? '' : akun.jenis === 'owner' ? 'owner' : akun.jenis === 'aktif' ? (akun.peran === 'ben' ? 'penjaga' : 'semua') : '');
/** Butir terlihat oleh peran itu (owner semua; Penjaga laci = semua + penjaga; karyawan = semua). */
export const rnTerlihat = (b, peran) => peran === 'owner' || b.untuk === 'semua' || (peran === 'penjaga' && b.untuk === 'penjaga');

/** Keadaan butir OTOMATIS untuk hari `iso` & putaran `periode`: { sudah, tidakTerbaca, teks, oleh, jam } — dari layar sumbernya, tidak ditebak. */
export function rnOtomatis(kunci, b, iso, periode, kini, peran) {
  const P = (x) => Object.assign({ sudah: false, tidakTerbaca: false, teks: '', oleh: '', jam: '' }, x);
  if (kunci === 'hitungLaci') { const d = cacheMentah('persetujuan').filter((m) => m && m.tindakan === RN_HL && String(m.tanggal || '') === iso && (m.status || 'menunggu') !== 'ditolak').sort((a, c) => String(a.jam || '').localeCompare(String(c.jam || '')));
    const T = ambilTutupHari().find((t) => t && t.tanggal === iso && t.dariTablet);
    return d.length ? P({ sudah: true, oleh: String(d[0].dari || ''), jam: String(d[0].jam || ''), teks: 'dikirim ' + (d[0].dari || 'tablet') + ' ' + (d[0].jam || '') }) : T ? P({ sudah: true, oleh: String(T.dariTablet.oleh || ''), jam: String(T.dariTablet.jam || ''), teks: 'dihitung ' + (T.dariTablet.oleh || 'tablet') + ' ' + (T.dariTablet.jam || '') }) : P({ teks: 'belum ada hitungan laci hari ini' }); }
  if (kunci === 'tutup') { if (peran !== 'owner' && !cacheMentah('tutup').length) return P({ tidakTerbaca: true, teks: 'ditutup owner di Uang › Tutup hari' });
    const T = ambilTutupHari().find((t) => t && t.tanggal === iso); return T ? P({ sudah: true, oleh: String(T.oleh || ''), jam: String(T.jam || ''), teks: 'ditutup ' + (T.jam || '') }) : P({ teks: 'hari ini belum ditutup' }); }
  if (kunci === 'cekWadah') { const C = wbCekHari(iso); return !C.nAktif ? P({ sudah: true, teks: 'belum ada wadah yang punya buku sendiri' }) : !C.belum.length ? P({ sudah: true, teks: 'semua ' + C.nAktif + ' wadah dicek' }) : P({ teks: 'belum dicek: ' + C.belum.join(', ') }); }
  if (kunci === 'karcis') { const K = daftarKarcis(kini); const n = K.daftar.filter((x) => x.jenisAsal === 'karcis' && x.hariIni).length; return n ? P({ teks: n + ' karcis hari ini belum dirinci' }) : P({ sudah: true, teks: K.nKarcis ? 'hari ini beres · ' + K.nKarcis + ' karcis lama masih menunggu' : 'tidak ada karcis yang menunggu' }); }
  if (kunci === 'cekGudang') { const G = gdCekGudang(kini); const sudah = !!G.terakhir && G.terakhir >= periode; return sudah ? P({ sudah: true, teks: 'dicek ' + tanggalPendek(G.terakhir) }) : P({ teks: G.teks }); }
  if (kunci === 'cadangan') { if (peran !== 'owner') return P({ tidakTerbaca: true, teks: 'diunduh owner' }); let akhir = ''; cacheMentah('cadangan').forEach((c) => { if (c && c.ok !== false && String(c.tanggal || '') > akhir) akhir = String(c.tanggal); });
    return akhir && akhir >= periode ? P({ sudah: true, teks: 'diunduh ' + tanggalPendek(akhir) }) : P({ teks: akhir ? 'terakhir ' + tanggalPendek(akhir) : 'belum pernah' }); }
  if (kunci === 'opname') { const O = gdOpname(kini); return !O.perlu ? P({ sudah: true, teks: 'terakhir ' + tanggalPendek(O.akhir) + ' · berikutnya ' + tanggalPendek(O.jatuh) }) : P({ teks: O.akhir ? 'sudah waktunya (terakhir ' + tanggalPendek(O.akhir) + ')' : 'belum pernah dicocokkan' }); }
  if (kunci === 'aturan') { if (peran === 'semua') return P({ tidakTerbaca: true, teks: 'dicek owner' }); const K = ptKalender(kini); const a = K.aturan.filter((x) => x.nyala);
    const belum = a.filter((x) => !(x.riwayat || []).some((r) => r.periode === periode)); return !a.length ? P({ sudah: true, teks: 'tidak ada cek aturan yang menyala' }) : belum.length ? P({ teks: 'belum: ' + belum.map((x) => x.nama).join(', ') }) : P({ sudah: true, teks: 'semua ' + a.length + ' sudah dicek bulan ini' }); }
  return P({ tidakTerbaca: true, teks: 'sumbernya tidak dikenal' });
}

/**
 * Daftar rutin untuk satu hari & satu akun. → { iso, senin, bulan, peran, kelompok: [{ ulang, nama, baris, n, nSudah }], n, nSudah, nBelum, nLewat, kalimat }.
 * baris = { id, nama, ulang, untuk, ket, otomatis, periode, jatuh, keadaan (sudah · belum · nanti · lewat · tidakTerbaca), sudah, oleh, jam, catatan, teks, jadwal, bisaCentang, sumber }.
 */
export function rnHari(kini, akun) {
  const iso = hariIniIso(kini); const peran = rnPeran(akun); const A = rnAtur(); const C = rnCek();
  const baris = A.butir.filter((b) => b.nyala && rnTerlihat(b, peran)).map((b) => {
    const periode = rnPeriode(b.ulang, iso); const jatuh = rnJatuh(b, iso); const c = (C[b.id] || {})[periode] || null;
    const O = b.otomatis ? rnOtomatis(b.otomatis, b, iso, periode, kini, peran) : null;
    const sudah = O ? O.sudah : !!c; const tidakTerbaca = !!(O && O.tidakTerbaca);
    const keadaan = tidakTerbaca ? 'tidakTerbaca' : sudah ? 'sudah' : jatuh > iso ? 'nanti' : jatuh < iso && jatuh >= RN_MULAI ? 'lewat' : 'belum';
    const bisaCentang = !b.otomatis && !sudah && (peran === 'owner' || (peran === 'penjaga' ? b.untuk !== 'owner' : b.untuk === 'semua'));
    return Object.assign({}, b, { periode, jatuh, keadaan, sudah, oleh: O ? O.oleh : c ? c.oleh : '', jam: O ? O.jam : c ? c.jam : '', catatan: c ? c.catatan : '', cekId: c ? c.id : '', jadwal: rnJadwal(b), bisaCentang,
      teks: O ? O.teks : c ? 'dicentang ' + (c.oleh || 'tanpa nama') + ' ' + (c.tanggal !== iso ? tanggalPendek(c.tanggal) + ' ' : '') + c.jam : keadaan === 'nanti' ? 'jatuh ' + tanggalPendek(jatuh) : keadaan === 'lewat' ? 'lewat sejak ' + tanggalPendek(jatuh) : 'belum',
      sumber: b.otomatis ? RN_OTOMATIS[b.otomatis] : '' });
  });
  const kelompok = RN_ULANG.map((u) => { const xs = baris.filter((x) => x.ulang === u.id); return { ulang: u.id, nama: u.nama, baris: xs, n: xs.filter((x) => x.keadaan !== 'tidakTerbaca').length, nSudah: xs.filter((x) => x.sudah).length }; }).filter((k) => k.baris.length);
  const dihitung = baris.filter((x) => x.keadaan !== 'tidakTerbaca'); const nSudah = dihitung.filter((x) => x.sudah).length; const nLewat = dihitung.filter((x) => x.keadaan === 'lewat').length;
  const harian = dihitung.filter((x) => x.ulang === 'harian');
  return { iso, senin: rnSenin(iso), bulan: iso.slice(0, 7), peran, dariOwner: A.dariOwner, kelompok, baris, n: dihitung.length, nSudah, nBelum: dihitung.length - nSudah, nLewat,
    nHarian: harian.length, nHarianSudah: harian.filter((x) => x.sudah).length,
    kalimat: !dihitung.length ? 'Belum ada rutin untuk peran ini' : 'Hari ini ' + harian.filter((x) => x.sudah).length + ' dari ' + harian.length + ' rutin harian' + (nLewat ? ' · ' + nLewat + ' lewat' : ''),
    sumber: 'Menu › Toko ini › Rutin', tujuan: { ke: 'sistem', sistem: 'rutin' } };
}

/** Centang satu butir manual untuk putaran hari ini. Satu dokumen rutinCek; butir otomatis, butir di luar peran, dan putaran yang sudah dicentang ditolak. */
export function susunCentangRutin(butirId, catatan, w, akun, kini) {
  const R = rnHari(kini || new Date(w.kini), akun); const b = R.baris.find((x) => x.id === String(butirId));
  if (!R.peran) return { tolak: 'Belum masuk — centang butuh orang yang jaga' };
  if (!b) { const ada = rnAtur().butir.find((x) => x.id === String(butirId)); return { tolak: ada ? (ada.nyala ? ada.nama + ' bukan tugas ' + (R.peran === 'semua' ? 'karyawan' : 'Penjaga laci') : ada.nama + ' sedang dimatikan owner') : 'Butir rutin itu tidak ada lagi — muat ulang' }; }
  if (b.otomatis) return { tolak: b.nama + ' tercatat sendiri dari ' + b.sumber + ' — kerjakan di sana' };
  if (b.sudah) return { tolak: b.nama + ' sudah dicentang ' + (b.oleh || '') + ' ' + b.jam };
  if (!b.bisaCentang) return { tolak: b.nama + ' dicentang owner' };
  const cat = rnTeks(catatan); if (cat.length > RN_BATAS.catatan) return { tolak: 'Catatan paling panjang ' + RN_BATAS.catatan + ' huruf' };
  const data = { id: 'rc-' + w.tanggal + '-' + String(w.idUnik()).replace(/[^0-9a-z]/gi, '').slice(-10), tanggal: w.tanggal, jam: w.jam, butir: b.id, periode: b.periode, catatan: cat };
  return { dokumen: [{ koleksi: 'rutinCek', data }], patch: { rnCatat: null, kabarAwas: false, kabar: '✓ ' + b.nama + (b.ulang === 'harian' ? '' : ' (' + (b.ulang === 'mingguan' ? 'minggu ini' : 'bulan ini') + ')') } };
}
/** Owner membatalkan satu centang yang salah (hapus dokumennya — tambah-saja untuk staf, hapus owner saja). */
export function susunBatalRutin(cekId, akun) {
  if (rnPeran(akun) !== 'owner') return { tolak: 'Membatalkan centang hanya owner' };
  const d = cacheMentah(RN_KOLEKSI).find((x) => String(x.id) === String(cekId)); if (!d) return { tolak: 'Centangnya tidak ditemukan' };
  const b = rnAtur().butir.find((x) => x.id === d.butir);
  return { dokumen: [], hapus: [{ koleksi: 'rutinCek', id: String(d.id) }], patch: { kabarAwas: false, kabar: 'Centang ' + (b ? b.nama : d.butir) + ' (' + (d.oleh || 'tanpa nama') + ' ' + (d.jam || '') + ') dibatalkan' } };
}

/** Simpan daftar butir (owner). isi = { butir: [ { id?, nama, ulang, hari, untuk, ket, otomatis, nyala } ] }. */
export function susunAturRutin(isi, w) {
  const a = isi || {}; const kini = rnAtur(); const daftar = Array.isArray(a.butir) ? a.butir : kini.butir; const seen = {}; const butir = []; let tolak = '';
  if (daftar.length > RN_BATAS.butir) return { tolak: 'Paling banyak ' + RN_BATAS.butir + ' butir' };
  daftar.forEach((b, i) => { if (tolak || !b) return; const nama = rnTeks(b.nama); const ulang = String(b.ulang || '');
    if (!nama) { tolak = 'Butir ke-' + (i + 1) + ': nama wajib diisi'; return; } if (nama.length > RN_BATAS.nama) { tolak = nama.slice(0, 20) + '…: nama paling panjang ' + RN_BATAS.nama + ' huruf'; return; }
    if (!RN_ULANG.some((u) => u.id === ulang)) { tolak = nama + ': pilih tiap hari / minggu / bulan'; return; }
    const h = Number(String(b.hari === undefined || b.hari === null ? '' : b.hari).trim() || (ulang === 'mingguan' ? 1 : 0));
    if (ulang === 'mingguan' && !(Number.isInteger(h) && h >= 1 && h <= 7)) { tolak = nama + ': pilih harinya (Senin–Minggu)'; return; }
    if (ulang === 'bulanan' && !(Number.isInteger(h) && h >= 0 && h <= 28)) { tolak = nama + ': tanggal 1–28, atau 0 = akhir bulan'; return; }
    const untuk = String(b.untuk || 'semua'); if (!RN_UNTUK.some((u) => u.id === untuk)) { tolak = nama + ': untuk siapa tidak dikenal'; return; }
    const ket = rnTeks(b.ket); if (ket.length > RN_BATAS.ket) { tolak = nama + ': keterangan paling panjang ' + RN_BATAS.ket + ' huruf'; return; }
    let id = String(b.id || ''); if (!/^[a-z0-9-]{1,40}$/.test(id)) id = 'r' + String(w.idUnik()).replace(/[^0-9a-z]/gi, '').slice(-10).toLowerCase(); if (seen[id]) { tolak = nama + ': kembar dengan butir lain'; return; } seen[id] = 1;
    butir.push(Object.assign({ id, nama, ulang, hari: ulang === 'harian' ? 0 : h, untuk, ket, nyala: b.nyala !== false }, RN_OTOMATIS[b.otomatis] ? { otomatis: String(b.otomatis) } : {})); });
  if (tolak) return { tolak };
  const lama = rnDok() || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: RN_ID, tanggal: w.tanggal, jam: w.jam, butir }) }],
    patch: { rnAtur: null, kabarAwas: false, kabar: 'Daftar rutin disimpan — ' + butir.filter((x) => x.nyala).length + ' butir menyala' } };
}

/**
 * Riwayat centang `hari` hari terakhir (owner): per hari harian x dari y + siapa mencentang apa. Butir otomatis dihitung dari sumbernya hanya untuk hari ini
 * (riwayat sumber lain tetap di layarnya). → { hari: [{ iso, nSudah, n, oleh: { nama: jumlah }, terlewat: [nama] }] }.
 */
export function rnRiwayat(kini, hari) {
  const iso = hariIniIso(kini); const A = rnAtur(); const C = rnCek(); const harian = A.butir.filter((b) => b.nyala && b.ulang === 'harian' && !b.otomatis); const out = [];
  for (let k = 0; k < (hari || 7); k++) { const t = rnTambah(iso, -k); if (t < RN_MULAI) break; const oleh = {}; const terlewat = [];
    harian.forEach((b) => { const c = (C[b.id] || {})[t]; if (c) oleh[c.oleh || 'tanpa nama'] = (oleh[c.oleh || 'tanpa nama'] || 0) + 1; else terlewat.push(b.nama); });
    out.push({ iso: t, n: harian.length, nSudah: harian.length - terlewat.length, oleh, terlewat }); }
  return { hari: out, nManual: harian.length };
}

/** Dasbor (kelompok mutu, owner): rutin hari ini · minggu ini · bulan ini + harian manual yang terlewat KEMARIN — angka yang SAMA dengan Menu › Rutin. */
export function rnDasbor(kini) {
  const R = rnHari(kini, { jenis: 'owner' }); const iso = R.iso; const kemarin = rnTambah(iso, -1); const C = rnCek();
  const terlewat = kemarin < RN_MULAI ? [] : rnAtur().butir.filter((b) => b.nyala && b.ulang === 'harian' && !b.otomatis && !(C[b.id] || {})[kemarin]).map((b) => b.nama);
  const per = (u) => { const k = R.kelompok.find((x) => x.ulang === u); return k ? { n: k.n, nSudah: k.nSudah } : { n: 0, nSudah: 0 }; };
  return { harian: per('harian'), mingguan: per('mingguan'), bulanan: per('bulanan'), nLewat: R.nLewat, lewat: R.baris.filter((x) => x.keadaan === 'lewat').map((x) => x.nama).slice(0, 6),
    kemarin, terlewat, kalimat: R.kalimat, sumber: R.sumber, tujuan: R.tujuan };
}
