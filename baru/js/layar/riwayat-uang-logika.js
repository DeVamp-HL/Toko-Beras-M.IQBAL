// RIWAYAT & BATAL — UANG (owner 22 Nov 2026, paket riwayat & pembatalan tahap 1). Logika tanpa DOM & tanpa Firebase; awalan ru. Dijaga alat-uji/uji_riwayat_uang.py.
// Owner: "gua mau ada fitur batal, urungkan, dan hapus di sistem utama akun owner (untuk yang belum) — gua sering salah catat … pilih yang paling masuk akal".
// Keputusan 22 Nov: owner saja · yang dibatalkan TETAP KELIHATAN (daftar "dibatalkan", alasan, siapa, jam; tidak dihitung lagi) · bisa DIPULIHKAN (urungkan) ·
// bisa DIHAPUS PERMANEN kapan saja.
//
// BENTUK: membatalkan = catatan aslinya DIHAPUS dari buku (mesin uang beku tidak diubah: yang tidak ada tidak dihitung) dan SALINAN UTUHNYA disimpan di
// koleksi bukuHapus (sudah ada, owner saja — dipakai hapus kedatangan/kantong/adukan) bersama alasan & koreksi yang ikut ditulis. Pulihkan = salinan ditulis
// kembali dengan id yang sama, koreksinya dibalik, baris bukuHapus dihapus. Hapus permanen = baris bukuHapus dihapus (catatan sudah tidak di buku).
//
// KELOMPOK — dibatalkan / dipulihkan BERSAMA: uang keluar + biaya admin pindah uang (dariPindah) · catatan + ambilan amplop laba pembiayaannya ('amk-'+id) ·
// pinjaman owner (modalOwner setor pinjaman + utangOwnerMutasi saldoAwal, kolom pasangan) · saling lunaskan (kasbon owner + utang toko ke owner, satu jam).
// TITIPAN tablet (dariPersetujuan): titipannya ikut ditandai "dibatalkan owner" (status ditolak + alasan) — tablet melihatnya; pulihkan = titipan kembali.
//
// HARI YANG SUDAH DITUTUP (pola batal nota bnTutup): catatan yang menyentuh LACI di hari yang ada penutupan berjam ≥ jam catatannya mengubah "laci seharusnya"
// malam itu. Membatalkannya: seharusnya bergeser −L (L = pengaruh catatan ke laci; uang keluar L < 0), jadi selisih malam itu += L (fisik tetap) — tanpa ini
// laba kena dua kali (biaya hilang DAN lebih/kurang kas tetap). Jejaknya di tutupHari.koreksiBatal. Tempat yang TIDAK dihitung fisik (rekening, brankas,
// amplop) ada di titik kas: catatan yang sudah termuat titik kas (bertanggal sebelum titik, atau hari titik tapi sebelum titik dipasang) → titik[tempat] −= E.
// Pulihkan = kebalikannya, dinilai dari keadaan SEKARANG (titik / penutupan yang lahir sesudah pembatalan ikut benar).
//
// TIDAK lewat sini (disebut sebabnya di baris): catatan buatan tutup hari (MDR, amankan, sisihan, setoran nol, titik kas) → tutup ulang; pembayaran bon yang
// lahir bersama nota → batal nota (Jual › Riwayat); saldo pembuka tutup buku; upah & biaya bulanan (slip, gaji, listrik — dokumen per bulan) → tahap berikut.
// Bulan terkunci = ditolak (tolakKunci).
import { cacheMentah, ambilPengeluaranHarian, ambilKasbonMutasi, ambilModalOwner, ambilUtangOwnerMutasi, ambilAmplopLaba, ambilPindahUang, ambilUtangPemasokMutasi,
  ambilPiutangMutasi, ambilTutupHari, ambilTitikKas, ambilSlipUpah, ingatGerakanKas, tolakKunci } from '../data/toko.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { kantongGerakan, ugAmplopLawan, ugSesudahTitik, ugNamaTempat } from './uang-logika.js';
import { kunciPelanggan } from '../mesin/pembantu.js';

export const RU_ALASAN = [['salah', 'Salah catat'], ['dobel', 'Tercatat dua kali'], ['uji', 'Uji coba']];
export const RU_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];
const ruJam = (j) => String(j || '').slice(0, 5);
const ruN = (x) => Math.round(Number(x) || 0);
const ruKosong = () => ({ laci: 0, brankas: 0, rekening: 0, amplop: 0 });
// titik kas dibaca dari dokumen HANYA bila diubahPada-nya lebih baru dari salinan perangkat (toko.js ambilTitikKas) — koreksi menaikkan 1 milidetik: dokumen menang
// di semua perangkat, sedangkan jam titik dipasang (menit, ugSesudahTitik) tidak bergeser. Titik tanpa diubahPada (bentuk lama) dibiarkan.
const ruMajuSedikit = (iso) => { const t = Date.parse(String(iso || '')); return isFinite(t) ? new Date(t + 1).toISOString() : iso; };

// ---------- sumber: semua catatan uang yang bisa (atau tidak bisa) dibatalkan di sini ----------
const RU_SUMBER = [
  ['pengeluaranHarian', () => ambilPengeluaranHarian()], ['kasbonMutasi', () => ambilKasbonMutasi()], ['modalOwner', () => ambilModalOwner()],
  ['utangOwnerMutasi', () => ambilUtangOwnerMutasi()], ['amplopLaba', () => ambilAmplopLaba()], ['pindahUang', () => ambilPindahUang()],
  ['utangPemasokMutasi', () => ambilUtangPemasokMutasi()], ['piutangMutasi', () => ambilPiutangMutasi()],
];
const ruCari = (koleksi, id) => { const s = RU_SUMBER.find((x) => x[0] === koleksi); return s ? (s[1]() || []).find((d) => String(d.id) === String(id)) || null : null; };

/** Catatan buatan sistem (bukan tangan) — tidak dibatalkan di sini, dengan sebabnya ('' = boleh). */
function ruBukanTangan(koleksi, d) {
  const id = String(d.id || '');
  if (d.tutupBuku || /^Saldo pembuka/.test(String(d.catatan || ''))) return 'saldo pembuka tutup buku — tidak dibatalkan';
  if (koleksi === 'pengeluaranHarian' && (d.mdr || /^mdr-/.test(id))) return 'potongan QRIS dari tutup hari — betulkan lewat tutup ulang (Uang › Tutup hari)';
  if (koleksi === 'amplopLaba' && /^am-\d{4}-\d\d-\d\d$/.test(id)) return 'sisihan laba tutup hari — betulkan lewat tutup ulang';
  if (koleksi === 'pindahUang' && /^pd-\d{4}-\d\d-\d\d$/.test(id)) return 'amankan laci tutup hari — betulkan lewat tutup ulang';
  if (koleksi === 'modalOwner' && (/^mo-st-/.test(id) || d.dariSetoran || d.dariSetoranLama)) return 'catatan setoran tutup hari — tidak dibatalkan';
  if (koleksi === 'kasbonMutasi' && d.tipe === 'saldoAwal') return 'saldo pembuka kasbon — tidak dibatalkan';
  if (koleksi === 'kasbonMutasi' && String(d.caraBayar || '') === 'Dipotong upah') return 'potongan kasbon dari slip upah — ikut pembatalan upah (tahap berikut)';
  if (koleksi === 'utangOwnerMutasi' && d.tipe === 'saldoAwal' && !d.pinjaman && d.alih !== 'salingLunas') return 'saldo pembuka utang toko ke owner — tidak dibatalkan';
  if (koleksi === 'utangPemasokMutasi' && d.tipe !== 'bayar') return 'saldo / koreksi bon pemasok — betulkan di Harga & Pemasok › Bon pemasok';
  if (koleksi === 'piutangMutasi' && d.tipe !== 'bayar') return 'bukan pembayaran — bon & hapus buku dibetulkan di Pelanggan';
  if (koleksi === 'piutangMutasi' && (d.notaTrxId || d.dariNota)) return 'dibayar bersama nota — batalkan notanya di Jual › Riwayat';
  return '';
}
/** Kepala kelompok: catatan pendamping menunjuk kepalanya (admin → pindah, amplop 'amk-' → catatan yang dibiayai, pinjaman modal → utang owner). */
function ruKepala(koleksi, d) {
  if (koleksi === 'pengeluaranHarian' && d.dariPindah) return { koleksi: 'pindahUang', id: String(d.dariPindah) };
  if (koleksi === 'amplopLaba' && /^amk-/.test(String(d.id || '')) && d.untuk) { const u = String(d.untuk); const k = ruCari('pengeluaranHarian', u) ? 'pengeluaranHarian' : ruCari('kasbonMutasi', u) ? 'kasbonMutasi' : null; if (k) return { koleksi: k, id: u }; }
  if (koleksi === 'modalOwner' && d.pinjaman && d.pasangan) return { koleksi: 'utangOwnerMutasi', id: String(d.pasangan) };
  if (koleksi === 'utangOwnerMutasi' && d.alih === 'salingLunas') { const k = ambilKasbonMutasi().find((x) => x.alih === 'salingLunas' && x.tanggal === d.tanggal && ruJam(x.jam) === ruJam(d.jam)); if (k) return { koleksi: 'kasbonMutasi', id: String(k.id) }; }
  return null;
}
/** Semua anggota kelompok dari kepalanya (kepala dulu). */
export function ruKelompok(koleksi, id) {
  const k = ruCari(koleksi, id); if (!k) return [];
  const naik = ruKepala(koleksi, k); if (naik && ruCari(naik.koleksi, naik.id)) return ruKelompok(naik.koleksi, naik.id);
  const out = [{ koleksi, data: k }]; const sid = String(k.id);
  ambilPengeluaranHarian().forEach((h) => { if (koleksi === 'pindahUang' && String(h.dariPindah || '') === sid) out.push({ koleksi: 'pengeluaranHarian', data: h }); });
  ambilAmplopLaba().forEach((a) => { if (String(a.id) === 'amk-' + sid) out.push({ koleksi: 'amplopLaba', data: a }); });
  if (koleksi === 'utangOwnerMutasi' && k.pinjaman) ambilModalOwner().forEach((m) => { if (String(m.pasangan || '') === sid) out.push({ koleksi: 'modalOwner', data: m }); });
  if (koleksi === 'kasbonMutasi' && k.alih === 'salingLunas') ambilUtangOwnerMutasi().forEach((u) => { if (u.alih === 'salingLunas' && u.tanggal === k.tanggal && ruJam(u.jam) === ruJam(k.jam)) out.push({ koleksi: 'utangOwnerMutasi', data: u }); });
  return out;
}

// ---------- kalimat & pengaruh ke tempat uang ----------
function ruJenis(koleksi, d) {
  if (koleksi === 'pengeluaranHarian') return d.dariPindah ? 'Biaya admin pindah uang' : d.kategori === 'owner' ? 'Ambil pribadi' : d.untuk === 'karyawan' ? 'Untuk karyawan' : 'Uang keluar';
  if (koleksi === 'kasbonMutasi') return (d.tipe === 'ambil' ? 'Kasbon' : d.alih === 'prive' ? 'Kasbon jadi ambil pribadi' : d.alih === 'salingLunas' ? 'Saling lunaskan' : 'Kasbon kembali') + ' · ' + String(d.namaPegawai || '');
  if (koleksi === 'modalOwner') return d.pinjaman ? 'Pinjaman owner masuk' : d.tipe === 'setor' ? 'Modal owner disetor' : 'Modal owner ditarik';
  if (koleksi === 'utangOwnerMutasi') return d.tipe === 'bayar' ? 'Bayar pinjaman owner' : d.alih === 'salingLunas' ? 'Utang toko ke owner berkurang (saling lunas)' : 'Pinjaman owner (utang toko)';
  if (koleksi === 'amplopLaba') return d.tipe === 'ambil' ? 'Ambil dari amplop laba' : 'Masuk amplop laba';
  if (koleksi === 'pindahUang') return 'Pindah uang ' + ugNamaTempat(d.dari) + ' → ' + ugNamaTempat(d.ke);
  if (koleksi === 'utangPemasokMutasi') return 'Bayar bon pemasok · ' + String(d.pemasok || '');
  if (koleksi === 'piutangMutasi') return 'Bayar bon pelanggan · ' + String(d.namaPelanggan || '');
  return koleksi;
}
/** Pengaruh satu catatan ke tiap tempat uang (rumus layar Uang: gerakan kas mesin + tempatnya, amplop & pindah uang). */
export function ruEfek(koleksi, d) {
  const e = ruKosong(); const n = ruN(d.nominal);
  if (koleksi === 'amplopLaba') { const lain = ugAmplopLawan(d); if (d.tipe === 'ambil') { e.amplop -= n; e[lain] += n; } else { e[lain] -= n; e.amplop += n; } return e; }
  if (koleksi === 'pindahUang') { if (e[d.dari] !== undefined) e[d.dari] -= n; if (e[d.ke] !== undefined) e[d.ke] += n; return e; }
  const tempatnya = kantongGerakan(); const sid = String(d.id);
  ingatGerakanKas().forEach((r) => { if (String(r.id) !== sid || !r.id) return; const k = tempatnya(r); if (e[k] === undefined) return; if (r.masuk > 0) e[k] += r.masuk; if (r.keluar > 0) e[k] -= r.keluar; });
  return e;
}
const ruJumlah = (a, b) => { const o = ruKosong(); RU_TEMPAT.forEach((k) => { o[k] = (a[k] || 0) + (b[k] || 0); }); return o; };
const ruTeksEfek = (e) => RU_TEMPAT.filter((k) => e[k]).map((k) => ugNamaTempat(k) + ' ' + (e[k] > 0 ? '+' : '−') + RP(Math.abs(e[k]))).join(' · ');

/** Satu baris riwayat (kepala kelompok). */
function ruBaris(koleksi, d) {
  const sebab = ruBukanTangan(koleksi, d); const K = sebab ? [{ koleksi, data: d }] : ruKelompok(koleksi, d.id); const e = K.reduce((a, x) => ruJumlah(a, ruEfek(x.koleksi, x.data)), ruKosong());
  const nominal = ruN(d.nominal);
  return { kunci: koleksi + '|' + String(d.id), koleksi, id: String(d.id), tanggal: String(d.tanggal || ''), jam: ruJam(d.jam), oleh: String(d.oleh || d.diubahOleh || ''), jenis: ruJenis(koleksi, d),
    ket: String(d.keterangan || d.catatan || d.alasan || '').slice(0, 80), nominal, efek: e, teksEfek: ruTeksEfek(e), anggota: K.length - 1, titipan: K.some((x) => x.data.dariPersetujuan),
    bisa: !sebab, sebab };
}
/** Riwayat uang hari `iso` (terbaru di atas). saring = nama orang ('' = semua). Pendamping kelompok tidak tampil sendiri. */
export function ruDaftar(iso, saring) {
  const out = [];
  RU_SUMBER.forEach(([koleksi, ambil]) => (ambil() || []).forEach((d) => {
    if (String(d.tanggal || '') !== iso) return; if (!ruBukanTangan(koleksi, d) && ruKepala(koleksi, d)) return;
    const b = ruBaris(koleksi, d); if (saring && b.oleh !== saring) return; out.push(b);
  }));
  // upah & bonus (slip): tampil, belum bisa dibatalkan di sini
  (ambilSlipUpah() || []).forEach((s) => { if (String(s.tanggal || '') !== iso) return; const b = { kunci: 'slipUpah|' + s.id, koleksi: 'slipUpah', id: String(s.id), tanggal: iso, jam: ruJam(s.jam), oleh: String(s.oleh || ''),
    jenis: (s.jenis === 'bonus' ? 'Bonus · ' : 'Upah · ') + String(s.nama || ''), ket: '', nominal: ruN(s.diterima || s.bonus || s.upah), efek: ruKosong(), teksEfek: '', anggota: 0, titipan: false, bisa: false, sebab: 'upah & biaya bulanan — pembatalannya menyusul (tahap berikut)' };
    if (!saring || b.oleh === saring) out.push(b); });
  return out.sort((a, b) => b.jam.localeCompare(a.jam) || b.id.localeCompare(a.id));
}
/** Nama orang yang mencatat uang hari `iso` (untuk pil saring). */
export const ruOrang = (iso) => ruDaftar(iso, '').map((b) => b.oleh).filter((o, i, a) => o && a.indexOf(o) === i);

// ---------- koreksi hari tertutup & titik kas ----------
/** Penutupan yang memuat catatan bertanggal `tgl` berjam `jam` (pola bnTutup): penutupan pertama hari itu yang jamnya ≥ jam catatan. */
function ruPenutupan(tgl, jam) {
  const td = ambilTutupHari().find((t) => t && t.tanggal === tgl); if (!td) return null;
  const urut = (Array.isArray(td.riwayat) ? td.riwayat.map((x, i) => ({ dok: x, i })) : []).concat([{ dok: td, i: -1 }]).sort((a, b) => ruJam(a.dok.jam).localeCompare(ruJam(b.dok.jam)));
  const kena = urut.find((x) => ruJam(x.dok.jam) >= ruJam(jam)) || null; return kena ? { td, kena } : null;
}
/** tutupHari sesudah selisih penutupan `T.kena` digeser +geser (dan kasSeharusnya −geser); jejak di koreksiBatal. */
function ruDokTutup(T, geser, jejak) {
  const ubah = (x) => { const d = Object.assign({}, x); ['selisih', 'selisihLaci'].forEach((k) => { if (typeof d[k] === 'number') d[k] = d[k] + geser; }); if (typeof d.kasSeharusnya === 'number') d.kasSeharusnya = d.kasSeharusnya - geser; return d; };
  let d = Object.assign({}, T.td); if (T.kena.i < 0) d = ubah(d); else d.riwayat = d.riwayat.map((x, i) => (i === T.kena.i ? ubah(x) : x));
  d.koreksiBatal = (Array.isArray(T.td.koreksiBatal) ? T.td.koreksiBatal : []).concat([jejak]);
  return { koleksi: 'tutupHari', data: d };
}
/** Catatan ini sudah termuat titik kas sekarang? (sebelum hari titik, atau hari titik tapi sebelum titik dipasang) */
function ruDalamTitik(d) {
  const t = ambilTitikKas(); if (!t || !t.tanggal) return false; const tgl = String(d.tanggal || '');
  if (tgl < t.tanggal) return true; if (tgl > t.tanggal) return false;
  return !ugSesudahTitik(t)({ t: tgl, jam: d.jam || '', id: d.id });
}
/**
 * Koreksi yang menyertai kelompok K bila DIBATALKAN (arah −1) atau DIPULIHKAN (+1): geser selisih penutupan (laci) & titik kas (tempat lain).
 * → { dokumen: [...], akibat: [kalimat], tutup: {tanggal, jam, geser} | null, titik: {tempat: Δ} | null }
 */
function ruKoreksi(K, arah, idBatal, kini) {
  const dokumen = []; const akibat = []; const kepala = K[0].data;
  const e = K.reduce((a, x) => ruJumlah(a, ruEfek(x.koleksi, x.data)), ruKosong());
  let tutup = null;
  if (e.laci) {
    const T = ruPenutupan(String(kepala.tanggal || ''), kepala.jam);
    if (T) {
      const geser = arah < 0 ? e.laci : -e.laci; const lama = typeof T.kena.dok.selisih === 'number' ? T.kena.dok.selisih : typeof T.kena.dok.selisihLaci === 'number' ? T.kena.dok.selisihLaci : null;
      dokumen.push(ruDokTutup(T, geser, { batal: String(idBatal), geser, jamTutup: ruJam(T.kena.dok.jam), arah: arah < 0 ? 'batal' : 'pulih', pada: kini }));
      tutup = { tanggal: T.td.tanggal, jam: ruJam(T.kena.dok.jam), geser };
      akibat.push('Tutup hari ' + tanggalPendek(T.td.tanggal) + ' ' + ruJam(T.kena.dok.jam) + ': selisih laci ' + (lama === null ? 'digeser ' + (geser > 0 ? '+' : '−') + RP(Math.abs(geser)) : RP(lama) + ' → ' + RP(lama + geser)) + ' (hitungan fisik tetap)');
    }
  }
  let titik = null;
  if (ruDalamTitik(kepala)) {
    const t = ambilTitikKas(); const ubah = {}; ['brankas', 'rekening', 'amplop'].forEach((k) => { if (e[k]) ubah[k] = arah < 0 ? -e[k] : e[k]; });
    if (Object.keys(ubah).length) {
      const baru = Object.assign({}, t, { id: 'titikKas' }, t.diubahPada ? { diubahPada: ruMajuSedikit(t.diubahPada) } : {}); Object.keys(ubah).forEach((k) => { baru[k] = (Number(t[k]) || 0) + ubah[k]; });
      dokumen.push({ koleksi: 'pengaturan', data: baru }); titik = ubah;
      akibat.push('Patokan kas ' + tanggalPendek(t.tanggal) + ': ' + Object.keys(ubah).map((k) => ugNamaTempat(k) + ' ' + (ubah[k] > 0 ? '+' : '−') + RP(Math.abs(ubah[k]))).join(' · ') + ' (tempat yang tidak dihitung fisik)');
    }
  }
  return { dokumen, akibat, tutup, titik, efek: e };
}

// ---------- batal ----------
/** Periksa sebelum membatalkan. → { tolak } | { K (kelompok), akibat: [kalimat] } */
export function ruPeriksa(koleksi, id) {
  const d = ruCari(koleksi, id); if (!d) return { tolak: 'Catatan ini tidak ada (sudah dibatalkan / dihapus?)' };
  const sebab = ruBukanTangan(koleksi, d); if (sebab) return { tolak: 'Tidak dibatalkan di sini: ' + sebab };
  const K = ruKelompok(koleksi, id); if (!K.length) return { tolak: 'Catatan ini tidak ada' };
  for (const x of K) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — catatan tidak bisa dibatalkan lagi'); if (k) return { tolak: k }; }
  // kasbon: membatalkan AMBIL tidak boleh membuat sisa kasbon orangnya minus (cicilannya sudah dicatat)
  const kb = K.find((x) => x.koleksi === 'kasbonMutasi' && x.data.tipe === 'ambil');
  if (kb) { const kunci = kunciPelanggan(kb.data.namaPegawai); const sisa = ambilKasbonMutasi().filter((m) => kunciPelanggan(m.namaPegawai) === kunci).reduce((a, m) => a + (m.tipe === 'ambil' || m.tipe === 'saldoAwal' ? ruN(m.nominal) : -ruN(m.nominal)), 0);
    if (sisa - ruN(kb.data.nominal) < -0.5) return { tolak: 'Kasbon ' + kb.data.namaPegawai + ' ini sudah dicicil / dikembalikan — batalkan dulu pembayarannya, supaya sisa kasbonnya tidak minus' }; }
  const R = ruKoreksi(K, -1, 'cek', '');
  const akibat = ['Dibatalkan: ' + K.map((x) => ruJenis(x.koleksi, x.data) + ' ' + RP(ruN(x.data.nominal))).join(' + ') + ' — tidak dihitung lagi, salinannya tetap di daftar Dibatalkan'];
  if (R.efek && ruTeksEfek(R.efek)) akibat.push('Uang yang tercatat berbalik: ' + ruTeksEfek(Object.fromEntries(RU_TEMPAT.map((k) => [k, -R.efek[k]]))));
  if (K.some((x) => x.data.dariPersetujuan)) akibat.push('Titipan tablet asalnya ikut ditandai dibatalkan owner (terbaca di tablet)');
  return { K, akibat: akibat.concat(R.akibat) };
}
/** Batalkan kelompok catatan `koleksi|id` dengan alasan. → { dokumen, hapus, patch } | { tolak } */
export function ruSusunBatal(koleksi, id, alasan, w) {
  const a = String(alasan || '').trim().slice(0, 120); if (!a) return { tolak: 'Membatalkan butuh alasan' };
  const P = ruPeriksa(koleksi, id); if (P.tolak) return P;
  const K = P.K; const idBatal = 'bt-' + w.idUnik(); const R = ruKoreksi(K, -1, idBatal, w.kini);
  const tt = []; K.forEach((x) => { const pid = x.data.dariPersetujuan; if (!pid) return; const p = cacheMentah('persetujuan').find((m) => String(m.id) === String(pid)); if (p) tt.push(p); });
  const kepala = K[0];
  const arsip = { id: idBatal, tanggal: w.tanggal, jam: w.jam, koleksi: kepala.koleksi, idDok: String(kepala.data.id), tanggalDok: String(kepala.data.tanggal || ''), pemasok: '',
    ringkas: ruJenis(kepala.koleksi, kepala.data) + ' · ' + RP(ruN(kepala.data.nominal)) + (K.length > 1 ? ' (+' + (K.length - 1) + ' pendamping)' : ''), alasan: a, jenisBatal: 'uang',
    dokumen: K.map((x) => ({ koleksi: x.koleksi, data: x.data })), titipan: tt, efek: R.efek, koreksi: { tutup: R.tutup, titik: R.titik } };
  const dokumen = [{ koleksi: 'bukuHapus', data: arsip }].concat(R.dokumen, tt.map((p) => ({ koleksi: 'persetujuan', data: Object.assign({}, p, { status: 'ditolak', alasanTolak: ('Dibatalkan owner: ' + a).slice(0, 80), batalOwner: idBatal,
    diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini }) })));
  return { dokumen, hapus: K.map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })), jejakHapus: 'Batal: ' + arsip.ringkas + ' — ' + a,
    patch: { kabar: 'Dibatalkan — ' + arsip.ringkas + '. ' + R.akibat.join(' · ') + (R.akibat.length ? ' · ' : '') + 'Salinannya di daftar Dibatalkan (bisa dipulihkan).', kabarAwas: false } };
}

// ---------- daftar dibatalkan, pulihkan, hapus permanen ----------
/** Baris daftar Dibatalkan (semua isi bukuHapus: uang tahap ini + hapus kedatangan / kantong / adukan lama), terbaru di atas. */
export function ruDibatalkan() {
  return cacheMentah('bukuHapus').slice().sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || ruJam(b.jam).localeCompare(ruJam(a.jam)))
    .map((x) => ({ id: String(x.id), tanggal: String(x.tanggal || ''), jam: ruJam(x.jam), oleh: String(x.oleh || ''), koleksi: String(x.koleksi || ''), tanggalDok: String(x.tanggalDok || ''),
      ringkas: String(x.ringkas || ''), alasan: String(x.alasan || ''), bisaPulih: x.jenisBatal === 'uang' && Array.isArray(x.dokumen) && x.dokumen.length > 0,
      sebabTidakPulih: x.jenisBatal === 'uang' ? '' : 'dihapus lewat layarnya sendiri (tanpa salinan utuh) — tidak bisa dipulihkan dari sini' }));
}
/** Pulihkan pembatalan uang `idBatal`: catatan ditulis kembali (id sama), koreksi dibalik menurut keadaan SEKARANG, titipan kembali, baris Dibatalkan dihapus. */
export function ruSusunPulih(idBatal, w) {
  const x = cacheMentah('bukuHapus').find((b) => String(b.id) === String(idBatal)); if (!x) return { tolak: 'Catatan dibatalkan itu tidak ditemukan' };
  if (x.jenisBatal !== 'uang' || !Array.isArray(x.dokumen) || !x.dokumen.length) return { tolak: 'Yang ini dihapus lewat layarnya sendiri, tanpa salinan utuh — tidak bisa dipulihkan dari sini' };
  for (const d of x.dokumen) {
    if (ruCari(d.koleksi, d.data.id)) return { tolak: 'Catatan ' + d.koleksi + ' dengan nomor yang sama sudah ada lagi — tidak dipulihkan dua kali' };
    const k = tolakKunci(d.koleksi, d.data, 'bulan itu sudah dikunci — tidak bisa dipulihkan'); if (k) return { tolak: k };
  }
  const K = x.dokumen.map((d) => ({ koleksi: d.koleksi, data: d.data }));
  // pengaruh catatan dihitung dari salinannya (catatannya sedang tidak ada di buku): efek tersimpan saat dibatalkan
  const R = ruKoreksiPulih(K, x, w.kini);
  const tt = (x.titipan || []).filter((p) => { const kini = cacheMentah('persetujuan').find((m) => String(m.id) === String(p.id)); return kini && kini.batalOwner === String(idBatal); });
  return { dokumen: K.map((d) => ({ koleksi: d.koleksi, data: d.data })).concat(R.dokumen, tt.map((p) => ({ koleksi: 'persetujuan', data: p }))), hapus: [{ koleksi: 'bukuHapus', id: String(idBatal) }],
    jejakHapus: 'Pulihkan: ' + String(x.ringkas || ''), patch: { kabar: 'Dipulihkan — ' + String(x.ringkas || '') + ' kembali di buku' + (R.akibat.length ? '. ' + R.akibat.join(' · ') : '') + (tt.length ? ' · titipan tablet kembali disetujui' : ''), kabarAwas: false } };
}
/** Koreksi saat memulihkan: efek kelompok = efek tersimpan (catatannya sedang tidak di buku, gerakan kas tidak memuatnya), sisanya sama dengan ruKoreksi arah +1. */
function ruKoreksiPulih(K, x, kini) {
  const e = Object.assign(ruKosong(), x.efek || {}); const kepala = K[0].data; const dokumen = []; const akibat = [];
  if (e.laci) {
    const T = ruPenutupan(String(kepala.tanggal || ''), kepala.jam);
    if (T) { const geser = -e.laci; dokumen.push(ruDokTutup(T, geser, { batal: String(x.id), geser, jamTutup: ruJam(T.kena.dok.jam), arah: 'pulih', pada: kini }));
      akibat.push('Tutup hari ' + tanggalPendek(T.td.tanggal) + ' ' + ruJam(T.kena.dok.jam) + ': selisih laci digeser ' + (geser > 0 ? '+' : '−') + RP(Math.abs(geser)) + ' kembali'); }
  }
  if (ruDalamTitik(kepala)) {
    const t = ambilTitikKas(); const ubah = {}; ['brankas', 'rekening', 'amplop'].forEach((k) => { if (e[k]) ubah[k] = e[k]; });
    if (Object.keys(ubah).length) { const baru = Object.assign({}, t, { id: 'titikKas' }, t.diubahPada ? { diubahPada: ruMajuSedikit(t.diubahPada) } : {}); Object.keys(ubah).forEach((k) => { baru[k] = (Number(t[k]) || 0) + ubah[k]; }); dokumen.push({ koleksi: 'pengaturan', data: baru });
      akibat.push('Patokan kas ' + tanggalPendek(t.tanggal) + ': ' + Object.keys(ubah).map((k) => ugNamaTempat(k) + ' ' + (ubah[k] > 0 ? '+' : '−') + RP(Math.abs(ubah[k]))).join(' · ')); }
  }
  return { dokumen, akibat };
}
/** Hapus permanen satu baris Dibatalkan (catatannya sudah tidak di buku — hanya salinannya yang hilang). */
export function ruSusunHapusPermanen(idBatal) {
  const x = cacheMentah('bukuHapus').find((b) => String(b.id) === String(idBatal)); if (!x) return { tolak: 'Catatan dibatalkan itu tidak ditemukan' };
  return { hapus: [{ koleksi: 'bukuHapus', id: String(idBatal) }], jejakHapus: 'Hapus permanen: ' + String(x.ringkas || ''), patch: { kabar: 'Dihapus permanen dari daftar Dibatalkan — ' + String(x.ringkas || ''), kabarAwas: false } };
}
