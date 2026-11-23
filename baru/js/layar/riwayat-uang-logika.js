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
// lahir bersama nota → batal nota (Jual › Riwayat); saldo pembuka tutup buku; gaji yang dibayar di sistem lama (tanpa slip) — lihat saja.
// UPAH & TAGIHAN BULANAN (owner 23 Nov 2026, "Dua-duanya bisa"): lihat bagian "upah & tagihan bulanan" di bawah — dokumen biayaBulanan dipakai bersama, jadi
// yang dibatalkan hanya BAGIANNYA (baris gaji satu slip / satu pos tagihan) dan pulihkan menggabungkannya lagi ke dokumen sekarang.
// Bulan terkunci = ditolak (tolakKunci). Tahun yang sudah ditutup buku = ditolak juga, batal & pulihkan (tolakBukuDitutup; keputusan owner K-B 23 Nov 2026).
import { cacheMentah, ambilPengeluaranHarian, ambilKasbonMutasi, ambilModalOwner, ambilUtangOwnerMutasi, ambilAmplopLaba, ambilPindahUang, ambilUtangPemasokMutasi,
  ambilPiutangMutasi, ambilTutupHari, ambilTitikKas, ambilSlipUpah, ambilBiayaBulanan, ingatGerakanKas, tolakKunci, tolakKunciTanggal, tolakBukuDitutup } from '../data/toko.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { kantongGerakan, ugAmplopLawan, ugSesudahTitik, ugNamaTempat } from './uang-logika.js';
import { kunciPelanggan, POS_BIAYA_BULANAN, namaBulanPanjang } from '../mesin/pembantu.js';

export const RU_ALASAN = [['salah', 'Salah catat'], ['dobel', 'Tercatat dua kali'], ['uji', 'Uji coba']];
export const RU_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];
const RU_DIPOTONG = 'Dipotong upah';   // caraBayar kasbon yang ditulis susunBayarUpah (upah-logika.js) — BUKAN 'Potong gaji' sistem lama
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
  if (koleksi === 'kasbonMutasi' && String(d.caraBayar || '') === RU_DIPOTONG) return 'potongan kasbon dari slip upah — ikut batal bersama slip upahnya (baris Upah di hari bayarnya)';
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
  const sebab = ruBukanTangan(koleksi, d) || tolakBukuDitutup(d, 'tidak dibatalkan lagi'); const K = sebab ? [{ koleksi, data: d }] : ruKelompok(koleksi, d.id); const e = K.reduce((a, x) => ruJumlah(a, ruEfek(x.koleksi, x.data)), ruKosong());
  const nominal = ruN(d.nominal);
  return { kunci: koleksi + '|' + String(d.id), koleksi, id: String(d.id), tanggal: String(d.tanggal || ''), jam: ruJam(d.jam), oleh: String(d.oleh || d.diubahOleh || ''), jenis: ruJenis(koleksi, d),
    ket: String(d.keterangan || d.catatan || d.alasan || '').slice(0, 80), nominal, efek: e, teksEfek: ruTeksEfek(e), anggota: K.length - 1, titipan: K.some((x) => x.data.dariPersetujuan),
    bisa: !sebab, sebab };
}
/** Riwayat uang hari `iso` (terbaru di atas). saring = nama orang ('' = semua). Pendamping kelompok tidak tampil sendiri. */
export function ruDaftar(iso, saring) {
  const out = []; const potSlip = {}; (ambilSlipUpah() || []).forEach((s) => { const m = ruPotonganSlip(s); if (m) potSlip[String(m.id)] = true; });
  RU_SUMBER.forEach(([koleksi, ambil]) => (ambil() || []).forEach((d) => {
    if (String(d.tanggal || '') !== iso) return; if (!ruBukanTangan(koleksi, d) && ruKepala(koleksi, d)) return;
    if (koleksi === 'kasbonMutasi' && potSlip[String(d.id)]) return;   // potongan kasbon slip = pendamping baris Upah-nya
    const b = ruBaris(koleksi, d); if (saring && b.oleh !== saring) return; out.push(b);
  }));
  // upah & bonus (slip) + tagihan bulanan yang dibayar hari ini (owner 23 Nov 2026)
  (ambilSlipUpah() || []).forEach((s) => { if (String(s.tanggal || '') !== iso) return; const b = ruBarisSlip(s); if (!saring || b.oleh === saring) out.push(b); });
  (ambilBiayaBulanan() || []).forEach((d) => POS_BIAYA_BULANAN.forEach((P) => { if (!(ruN(d[P.kunci]) > 0) || ruTglPos(d, P.kunci) !== iso) return; const T = ruCariPos(d.bulan + '|' + P.kunci);
    if (!T) return; const b = ruBarisPos(T); if (!saring || b.oleh === saring) out.push(b); }));
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
function ruKoreksi(K, arah, idBatal, kini) { return ruKoreksiDari(K[0].data, K.reduce((a, x) => ruJumlah(a, ruEfek(x.koleksi, x.data)), ruKosong()), arah, idBatal, kini); }
/** Sama dengan ruKoreksi, dengan pengaruh `e` yang sudah dihitung (upah & tagihan: baris gaji/pos mesin tidak ber-id) dan `kepala` = { tanggal, jam, id } catatannya. */
function ruKoreksiDari(kepala, e, arah, idBatal, kini) {
  const dokumen = []; const akibat = [];
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
  if (koleksi === 'slipUpah') return ruPeriksaSlip(id); if (koleksi === 'biayaBulanan') return ruPeriksaPos(id);
  const d = ruCari(koleksi, id); if (!d) return { tolak: 'Catatan ini tidak ada (sudah dibatalkan / dihapus?)' };
  const sebab = ruBukanTangan(koleksi, d); if (sebab) return { tolak: 'Tidak dibatalkan di sini: ' + sebab };
  const K = ruKelompok(koleksi, id); if (!K.length) return { tolak: 'Catatan ini tidak ada' };
  for (const x of K) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — catatan tidak bisa dibatalkan lagi') || tolakBukuDitutup(x.data, 'catatan tidak dibatalkan lagi'); if (k) return { tolak: k }; }
  // kasbon: membatalkan AMBIL tidak boleh membuat sisa kasbon orangnya minus (cicilannya sudah dicatat)
  const kb = K.find((x) => x.koleksi === 'kasbonMutasi' && x.data.tipe === 'ambil');
  if (kb) { const kunci = kunciPelanggan(kb.data.namaPegawai); const sisa = ambilKasbonMutasi().filter((m) => kunciPelanggan(m.namaPegawai) === kunci).reduce((a, m) => a + (m.tipe === 'ambil' || m.tipe === 'saldoAwal' ? ruN(m.nominal) : -ruN(m.nominal)), 0);
    if (sisa - ruN(kb.data.nominal) < -0.5) return { tolak: 'Kasbon ' + kb.data.namaPegawai + ' ini sudah dicicil / dikembalikan — batalkan dulu pembayarannya, supaya sisa kasbonnya tidak minus' }; }
  const R = ruKoreksi(K, -1, 'cek', '');
  // koreksi yang menyentuh tahun yang sudah ditutup (tutup hari / patokan kas 31 Des = kas pembuka tahun baru) juga ditolak
  for (const x of R.dokumen) { const k = tolakBukuDitutup(x.data, 'tutup hari & patokan kas ' + String(x.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (k) return { tolak: k }; }
  const akibat = ['Dibatalkan: ' + K.map((x) => ruJenis(x.koleksi, x.data) + ' ' + RP(ruN(x.data.nominal))).join(' + ') + ' — tidak dihitung lagi, salinannya tetap di daftar Dibatalkan'];
  if (R.efek && ruTeksEfek(R.efek)) akibat.push('Uang yang tercatat berbalik: ' + ruTeksEfek(Object.fromEntries(RU_TEMPAT.map((k) => [k, -R.efek[k]]))));
  if (K.some((x) => x.data.dariPersetujuan)) akibat.push('Titipan tablet asalnya ikut ditandai dibatalkan owner (terbaca di tablet)');
  return { K, akibat: akibat.concat(R.akibat) };
}
/** Batalkan kelompok catatan `koleksi|id` dengan alasan. → { dokumen, hapus, patch } | { tolak } */
export function ruSusunBatal(koleksi, id, alasan, w) {
  const a = String(alasan || '').trim().slice(0, 120); if (!a) return { tolak: 'Membatalkan butuh alasan' };
  if (koleksi === 'slipUpah') return ruSusunBatalSlip(id, a, w); if (koleksi === 'biayaBulanan') return ruSusunBatalPos(id, a, w);
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

// ---------- upah & tagihan bulanan (owner 23 Nov 2026: "Dua-duanya bisa") ----------
// UPAH = SATU pembayaran utuh: slipUpah + baris gaji berkunci "Nama · tanggal" (slip.kunci) di biayaBulanan tiap bulan yang dicakup (slip.bulanan) + kasbon
// "Dipotong upah" yang lahir bersamanya. susunBayarUpah tidak menulis kolom penghubung ke kasbon itu → dikenali dari tanggal, jam, nama, dan nominal = slip.potong.
// Hanya slip upah TERAKHIR tiap orang: mulaiUpah membaca "sampai" terbesar, jadi membatalkan slip lama selagi ada slip sesudahnya = hari-hari itu tetap tertutup
// padahal uangnya hilang. Slip bonus (tanpa hari kerja) bebas. Hari kerja (absenKaryawan) tidak disentuh — kembali "belum dibayar" dengan sendirinya.
// TAGIHAN = satu pos (listrik / akses / keamanan / internet) satu bulan: nominal pos jadi 0 + tanggal & tempat bayarnya dihapus → "belum dibayar" di Uang ›
// Tagihan, pos lain & gaji di dokumen bulan itu tidak tersentuh. Tagihan tambahan owner = belanja harian "(bulanan)" → sudah lewat catatan uang keluar biasa.
// Dokumen biayaBulanan per bulan dipakai bersama → arsip menyimpan BAGIANNYA (`bagian`), bukan dokumen utuh; pulihkan menggabungkannya ke dokumen SEKARANG.
// Pengaruh ke tempat uang dibaca dari baris gerakan kas mesin (bayaranBiayaBulanan: ber-id 0, dikenali dari tanggal + label "… — biaya <Bulan Tahun>"),
// tempatnya menurut kantongGerakan (dariPos) — persis yang dibaca laci, saldo tempat, dan tutup hari.
const ruLabelBulan = (bulan) => ' — biaya ' + namaBulanPanjang(bulan + '-01');
function ruEfekBiaya(cocok) {
  const e = ruKosong(); const tempatnya = kantongGerakan();
  ingatGerakanKas().forEach((r) => { if (r.id || !cocok(r)) return; const k = tempatnya(r); if (e[k] === undefined) return; if (r.keluar > 0) e[k] -= r.keluar; if (r.masuk > 0) e[k] += r.masuk; });
  return e;
}
/** Dokumen bulan dengan peta tanggal per pos (dokumen lama bertanggal tunggal: semua pos yang bernilai dibawa tanggalnya — aturan susunBayarTagihan). */
function ruPetaPos(dok) {
  const d = Object.assign({}, dok || {}); const peta = Object.assign({}, d.tanggalBayarPos || {});
  if (!d.tanggalBayarPos && d.tanggalBayar) { POS_BIAYA_BULANAN.forEach((q) => { if (Number(d[q.kunci]) > 0) peta[q.kunci] = d.tanggalBayar; }); if (Number(d.gaji) > 0) peta.gaji = d.tanggalBayar; }
  d.tanggalBayarPos = peta; ['akses', 'keamanan', 'listrik', 'internet'].forEach((k) => { if (d[k] === undefined) d[k] = 0; });
  if (d.gaji === undefined) d.gaji = 0; if (d.gajiHariOrang === undefined) d.gajiHariOrang = 0; if (!Array.isArray(d.rincianGaji)) d.rincianGaji = [];
  return d;
}
const ruHitungGaji = (d) => { d.gaji = d.rincianGaji.reduce((a, r) => a + (Number(r.gaji) || 0), 0); d.gajiHariOrang = d.rincianGaji.reduce((a, r) => a + (Number(r.hari) || 0), 0); return d; };
const ruDokBulan = (bulan) => (ambilBiayaBulanan() || []).find((b) => String(b.bulan) === String(bulan)) || null;
const ruJenisSlip = (s) => (s.jenis === 'bonus' ? 'Bonus · ' : 'Upah · ') + String(s.nama || '');

/** Kasbon "Dipotong upah" milik slip `s` (null bila slip tanpa potongan / tidak ketemu). */
function ruPotonganSlip(s) {
  if (!s || !(ruN(s.potong) > 0)) return null;
  return ambilKasbonMutasi().find((m) => m.tipe === 'bayar' && String(m.caraBayar || '') === RU_DIPOTONG && String(m.tanggal || '') === String(s.tanggal || '') && ruJam(m.jam) === ruJam(s.jam)
    && kunciPelanggan(m.namaPegawai) === kunciPelanggan(s.nama) && ruN(m.nominal) === ruN(s.potong)) || null;
}
/** Bagian slip di biaya bulanan: tiap bulan tercakup → dokumennya, baris gajinya, tanggal & tempat bayarnya. */
function ruBagianSlip(s) {
  const kunci = String(s.kunci || ''); const bulan = (Array.isArray(s.bulanan) ? s.bulanan : []).map((b) => String((b && b.bulan) || '')).filter((b, i, a) => b && a.indexOf(b) === i);
  return bulan.map((bl) => { const dok = ruDokBulan(bl); const urutan = dok ? (dok.rincianGaji || []).findIndex((r) => r && r.nama === kunci) : -1; const baris = urutan >= 0 ? dok.rincianGaji[urutan] : null;
    return { bulan: bl, dok, baris, urutan, tanggalBayar: dok && dok.tanggalBayarGaji ? String(dok.tanggalBayarGaji[kunci] || '') : '', dari: dok && dok.dariPos ? String(dok.dariPos['gaji:' + kunci] || '') : '' }; });
}
/** Pengaruh satu slip ke tempat uang: baris gaji mesin (keluar) + potongan kasbonnya (masuk) — bersihnya = yang diterima karyawan. */
function ruEfekSlip(s, B, kb) {
  const kunci = String(s.kunci || '');
  const e = ruEfekBiaya((r) => { const l = String(r.label || ''); return B.some((b) => { const ekor = ruLabelBulan(b.bulan); return r.t === b.tanggalBayar && (l === 'Gaji ' + kunci + ekor || (l.indexOf('Gaji ' + kunci + ' (kotor') === 0 && l.slice(-ekor.length) === ekor)); }); });
  return kb ? ruJumlah(e, ruEfek('kasbonMutasi', kb)) : e;
}
/** Sebab slip ini tidak dibatalkan di sini ('' = boleh). */
function ruSebabSlip(s) {
  if (s.jenis !== 'bonus') {
    const k = kunciPelanggan(s.nama); const tua = String(s.tanggal || '') + ruJam(s.jam);
    const sesudah = ambilSlipUpah().filter((x) => x && x.jenis !== 'bonus' && String(x.id) !== String(s.id) && kunciPelanggan(x.nama) === k
      && (String(x.sampai || '') > String(s.sampai || '') || (String(x.sampai || '') === String(s.sampai || '') && String(x.tanggal || '') + ruJam(x.jam) > tua)))
      .sort((a, b) => String(b.sampai || '').localeCompare(String(a.sampai || '')))[0];
    if (sesudah) return 'ada slip upah ' + String(s.nama || '') + ' sesudahnya (dibayar ' + tanggalPendek(sesudah.tanggal) + ') — batalkan dulu yang itu';
  }
  if (!s.kunci || !Array.isArray(s.bulanan) || !s.bulanan.length) return 'slip lama tanpa baris gaji berkunci — tidak dibatalkan di sini';
  const hilang = ruBagianSlip(s).find((b) => !b.baris); if (hilang) return 'baris gajinya di biaya bulan ' + hilang.bulan + ' tidak ditemukan — tidak dibatalkan di sini';
  if (ruN(s.potong) > 0 && !ruPotonganSlip(s)) return 'potongan kasbon slip ini tidak ditemukan — tidak dibatalkan di sini';
  return '';
}
const ruSlipDitutup = (s, apa) => tolakBukuDitutup(s, apa) || ruBagianSlip(s).map((b) => tolakBukuDitutup({ bulan: b.bulan }, apa)).find(Boolean) || '';
function ruBarisSlip(s) {
  // tahun ditutup dulu: sesudah ritual biayaBulanan tahun itu sudah diarsip (slipUpah tidak) — sebab yang benar "tahun sudah ditutup", bukan "baris tidak ditemukan"
  const sebab = ruSlipDitutup(s, 'tidak dibatalkan lagi') || ruSebabSlip(s); const B = sebab ? [] : ruBagianSlip(s); const kb = sebab ? null : ruPotonganSlip(s);
  const e = sebab ? ruKosong() : ruEfekSlip(s, B, kb);
  const ket = s.jenis === 'bonus' ? String(s.alasanBonus || '') : 'hari ' + tanggalPendek(s.dari) + ' – ' + tanggalPendek(s.sampai) + (ruN(s.potong) > 0 ? ' · potong kasbon ' + RP(ruN(s.potong)) : '');
  return { kunci: 'slipUpah|' + String(s.id), koleksi: 'slipUpah', id: String(s.id), tanggal: String(s.tanggal || ''), jam: ruJam(s.jam), oleh: String(s.oleh || s.diubahOleh || ''), jenis: ruJenisSlip(s), ket,
    nominal: ruN(s.diterima || s.bonus || s.upah), efek: e, teksEfek: ruTeksEfek(e), anggota: B.length + (kb ? 1 : 0), titipan: false, bisa: !sebab, sebab };
}
function ruPeriksaSlip(id) {
  const s = ambilSlipUpah().find((x) => String(x.id) === String(id)); if (!s) return { tolak: 'Slip upah ini tidak ada (sudah dibatalkan?)' };
  const tutup = ruSlipDitutup(s, 'upahnya tidak dibatalkan lagi'); if (tutup) return { tolak: tutup };
  const sebab = ruSebabSlip(s); if (sebab) return { tolak: 'Tidak dibatalkan di sini: ' + sebab };
  const B = ruBagianSlip(s); const kb = ruPotonganSlip(s);
  const cek = [{ koleksi: 'slipUpah', data: s }].concat(kb ? [{ koleksi: 'kasbonMutasi', data: kb }] : [], B.map((b) => ({ koleksi: 'biayaBulanan', data: { bulan: b.bulan } })));
  for (const x of cek) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — upah tidak bisa dibatalkan lagi') || tolakBukuDitutup(x.data, 'upahnya tidak dibatalkan lagi'); if (k) return { tolak: k }; }
  const e = ruEfekSlip(s, B, kb); const R = ruKoreksiDari(s, e, -1, 'cek', '');
  for (const x of R.dokumen) { const k = tolakBukuDitutup(x.data, 'tutup hari & patokan kas ' + String(x.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (k) return { tolak: k }; }
  const akibat = ['Dibatalkan: ' + ruJenisSlip(s) + ' ' + RP(ruN(s.diterima)) + ' — slip, biaya gaji ' + B.map((b) => b.bulan).join(' & ') + (kb ? ', dan potongan kasbon ' + RP(ruN(kb.nominal)) : '') + ' keluar dari buku bersama; salinannya tetap di daftar Dibatalkan'];
  if (s.jenis !== 'bonus') akibat.push('Hari kerja ' + tanggalPendek(s.dari) + ' – ' + tanggalPendek(s.sampai) + ' kembali "belum dibayar" di Uang › Upah');
  if (kb) akibat.push('Sisa kasbon ' + String(s.nama || '') + ' naik lagi ' + RP(ruN(kb.nominal)));
  if (ruTeksEfek(e)) akibat.push('Uang yang tercatat berbalik: ' + ruTeksEfek(Object.fromEntries(RU_TEMPAT.map((k) => [k, -e[k]]))));
  return { s, B, kb, e, akibat: akibat.concat(R.akibat) };
}
/** Dokumen bulan tanpa baris gaji `kunci` (gaji & hari dijumlah ulang; tanggal & tempat bayar baris itu ikut hilang). */
function ruTanpaBarisGaji(dok, kunci) {
  const d = ruPetaPos(dok); d.rincianGaji = d.rincianGaji.filter((r) => r.nama !== kunci); ruHitungGaji(d);
  const t = Object.assign({}, d.tanggalBayarGaji || {}); delete t[kunci]; d.tanggalBayarGaji = t; const dp = Object.assign({}, d.dariPos || {}); delete dp['gaji:' + kunci]; d.dariPos = dp;
  return d;
}
function ruSusunBatalSlip(id, a, w) {
  const P = ruPeriksaSlip(id); if (P.tolak) return P; const { s, B, kb, e } = P; const idBatal = 'bt-' + w.idUnik(); const R = ruKoreksiDari(s, e, -1, idBatal, w.kini); const kunci = String(s.kunci);
  const arsip = { id: idBatal, tanggal: w.tanggal, jam: w.jam, koleksi: 'slipUpah', idDok: String(s.id), tanggalDok: String(s.tanggal || ''), pemasok: '',
    ringkas: ruJenisSlip(s) + ' · ' + RP(ruN(s.diterima)) + ' (+' + (B.length + (kb ? 1 : 0)) + ' pendamping)', alasan: a, jenisBatal: 'uang', bentuk: 'upah',
    dokumen: [{ koleksi: 'slipUpah', data: s }].concat(kb ? [{ koleksi: 'kasbonMutasi', data: kb }] : []), bagian: B.map((b) => ({ bulan: b.bulan, baris: b.baris, urutan: b.urutan, tanggalBayar: b.tanggalBayar, dari: b.dari })),
    efek: e, koreksi: { tutup: R.tutup, titik: R.titik } };
  return { dokumen: [{ koleksi: 'bukuHapus', data: arsip }].concat(B.map((b) => ({ koleksi: 'biayaBulanan', data: ruTanpaBarisGaji(b.dok, kunci) })), R.dokumen),
    hapus: [{ koleksi: 'slipUpah', id: String(s.id) }].concat(kb ? [{ koleksi: 'kasbonMutasi', id: String(kb.id) }] : []), jejakHapus: 'Batal: ' + arsip.ringkas + ' — ' + a,
    patch: { kabar: 'Dibatalkan — ' + arsip.ringkas + '. ' + (s.jenis !== 'bonus' ? 'Hari kerja ' + tanggalPendek(s.dari) + ' – ' + tanggalPendek(s.sampai) + ' kembali belum dibayar · ' : '') + R.akibat.join(' · ') + (R.akibat.length ? ' · ' : '') + 'Salinannya di daftar Dibatalkan (bisa dipulihkan).', kabarAwas: false } };
}
function ruPulihSlip(x, w) {
  const dok = Array.isArray(x.dokumen) ? x.dokumen : []; const s = (dok.find((d) => d && d.koleksi === 'slipUpah') || {}).data; const kb = (dok.find((d) => d && d.koleksi === 'kasbonMutasi') || {}).data || null;
  const bagian = Array.isArray(x.bagian) ? x.bagian : []; if (!s || !bagian.length) return { tolak: 'Salinan upah ini tidak lengkap — tidak bisa dipulihkan dari sini' };
  const cek = [{ koleksi: 'slipUpah', data: s }].concat(kb ? [{ koleksi: 'kasbonMutasi', data: kb }] : [], bagian.map((b) => ({ koleksi: 'biayaBulanan', data: { bulan: b.bulan } })));
  for (const c of cek) { const k = tolakKunci(c.koleksi, c.data, 'bulan itu sudah dikunci — tidak bisa dipulihkan') || tolakBukuDitutup(c.data, 'catatannya tidak dipulihkan lagi'); if (k) return { tolak: k }; }
  if (ambilSlipUpah().some((y) => String(y.id) === String(s.id))) return { tolak: 'Slip upah dengan nomor yang sama sudah ada lagi — tidak dipulihkan dua kali' };
  if (kb && ruCari('kasbonMutasi', kb.id)) return { tolak: 'Potongan kasbon dengan nomor yang sama sudah ada lagi — tidak dipulihkan dua kali' };
  if (s.jenis !== 'bonus') { const k = kunciPelanggan(s.nama); const lain = ambilSlipUpah().find((y) => y && y.jenis !== 'bonus' && kunciPelanggan(y.nama) === k && String(y.sampai || '') >= String(s.dari || ''));
    if (lain) return { tolak: 'Hari kerja ' + String(s.nama || '') + ' di rentang slip ini sudah dibayar lagi (slip ' + tanggalPendek(lain.tanggal) + ') — tidak dipulihkan supaya tidak dibayar dua kali' }; }
  const kunci = String(s.kunci || '');
  for (const b of bagian) { const kini = ruDokBulan(b.bulan); if (kini && (kini.rincianGaji || []).some((r) => r && r.nama === kunci)) return { tolak: 'Baris gaji ' + kunci + ' di biaya bulan ' + b.bulan + ' sudah ada lagi — tidak dipulihkan dua kali' }; }
  const dokB = bagian.map((b) => { const d = ruPetaPos(ruDokBulan(b.bulan) || { id: b.bulan, bulan: b.bulan }); d.id = b.bulan; d.bulan = b.bulan;
    // baris kembali ke urutan semula (urutan rincianGaji = urutan baris gaji mesin)
    const sisa = d.rincianGaji.filter((r) => r.nama !== kunci); const i = Math.min(Math.max(Number(b.urutan) || 0, 0), sisa.length); d.rincianGaji = sisa.slice(0, i).concat([b.baris], sisa.slice(i)); ruHitungGaji(d);
    d.tanggalBayarGaji = Object.assign({}, d.tanggalBayarGaji || {}, { [kunci]: b.tanggalBayar }); if (b.dari) d.dariPos = Object.assign({}, d.dariPos || {}, { ['gaji:' + kunci]: b.dari });
    return { koleksi: 'biayaBulanan', data: d }; });
  const R = ruKoreksiPulih([{ koleksi: 'slipUpah', data: s }], x, w.kini);
  for (const d of R.dokumen) { const k = tolakBukuDitutup(d.data, 'tutup hari & patokan kas ' + String(d.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (k) return { tolak: k }; }
  return { dokumen: [{ koleksi: 'slipUpah', data: s }].concat(kb ? [{ koleksi: 'kasbonMutasi', data: kb }] : [], dokB, R.dokumen), hapus: [{ koleksi: 'bukuHapus', id: String(x.id) }],
    jejakHapus: 'Pulihkan: ' + String(x.ringkas || ''), patch: { kabar: 'Dipulihkan — ' + String(x.ringkas || '') + ' kembali di buku (slip, biaya gaji' + (kb ? ', potongan kasbon' : '') + ')' + (R.akibat.length ? '. ' + R.akibat.join(' · ') : ''), kabarAwas: false } };
}

// tagihan: id = "<bulan>|<pos>"
const ruTglPos = (d, pos) => String((d && (d.tanggalBayarPos ? d.tanggalBayarPos[pos] : d.tanggalBayar)) || '');
function ruCariPos(id) {
  const i = String(id).indexOf('|'); const bulan = String(id).slice(0, i); const pos = String(id).slice(i + 1); const P = POS_BIAYA_BULANAN.find((q) => q.kunci === pos) || null; const dok = ruDokBulan(bulan);
  if (i < 0 || !P || !dok) return null; const n = ruN(dok[pos]); const tanggal = ruTglPos(dok, pos); if (!(n > 0) || !tanggal) return null;
  return { bulan, pos, P, dok, n, tanggal, jam: ruJam((dok.jamBayarPos || {})[pos]), dari: String((dok.dariPos || {})[pos] || '') };
}
const ruJenisPos = (T) => 'Tagihan ' + T.P.label + ' · ' + namaBulanPanjang(T.bulan + '-01');
const ruEfekPos = (T) => ruEfekBiaya((r) => r.t === T.tanggal && String(r.label || '') === T.P.label + ruLabelBulan(T.bulan));
// jam bayar tagihan baru dicatat sejak 23 Nov 2026 (jamBayarPos); tagihan lama tanpa jam dianggap dibayar sebelum tutup hari itu (siang hari, bukan sesudah tutup)
const ruKepalaPos = (T) => ({ tanggal: T.tanggal, jam: T.jam, id: 0 });
const ruPosDitutup = (bulan, tanggal, apa) => tolakBukuDitutup({ bulan }, apa) || tolakBukuDitutup({ tanggal }, apa);
function ruBarisPos(T) {
  const sebab = ruPosDitutup(T.bulan, T.tanggal, 'tidak dibatalkan lagi'); const e = ruEfekPos(T);
  return { kunci: 'biayaBulanan|' + T.bulan + '|' + T.pos, koleksi: 'biayaBulanan', id: T.bulan + '|' + T.pos, tanggal: T.tanggal, jam: T.jam, oleh: '', jenis: ruJenisPos(T),
    ket: T.dari ? 'dibayar dari ' + ugNamaTempat(T.dari).toLowerCase() : '', nominal: T.n, efek: e, teksEfek: ruTeksEfek(e), anggota: 0, titipan: false, bisa: !sebab, sebab };
}
function ruPeriksaPos(id) {
  const T = ruCariPos(id); if (!T) return { tolak: 'Tagihan ini tidak ada atau belum dibayar' };
  const k = tolakKunci('biayaBulanan', { bulan: T.bulan }, 'bulan itu sudah dikunci — tagihan tidak bisa dibatalkan lagi') || tolakKunciTanggal(T.tanggal, 'bulan itu sudah dikunci — tagihan tidak bisa dibatalkan lagi')
    || ruPosDitutup(T.bulan, T.tanggal, 'tagihannya tidak dibatalkan lagi'); if (k) return { tolak: k };
  const e = ruEfekPos(T); const R = ruKoreksiDari(ruKepalaPos(T), e, -1, 'cek', '');
  for (const x of R.dokumen) { const kk = tolakBukuDitutup(x.data, 'tutup hari & patokan kas ' + String(x.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (kk) return { tolak: kk }; }
  const akibat = ['Dibatalkan: ' + ruJenisPos(T) + ' ' + RP(T.n) + ' — kembali "belum dibayar" di Uang › Tagihan (bisa dibayar ulang); tagihan lain & gaji bulan itu tidak tersentuh; biaya bulan itu di laba turun ' + RP(T.n)];
  if (ruTeksEfek(e)) akibat.push('Uang yang tercatat berbalik: ' + ruTeksEfek(Object.fromEntries(RU_TEMPAT.map((q) => [q, -e[q]]))));
  if (!T.jam && R.tutup) akibat.push('Jam bayarnya tidak tercatat (tagihan sebelum 23 Nov 2026) — dianggap dibayar sebelum tutup hari itu');
  return { T, e, akibat: akibat.concat(R.akibat) };
}
function ruSusunBatalPos(id, a, w) {
  const P = ruPeriksaPos(id); if (P.tolak) return P; const { T, e } = P; const idBatal = 'bt-' + w.idUnik(); const R = ruKoreksiDari(ruKepalaPos(T), e, -1, idBatal, w.kini);
  const d = ruPetaPos(T.dok); d[T.pos] = 0; const peta = Object.assign({}, d.tanggalBayarPos); delete peta[T.pos]; d.tanggalBayarPos = peta;
  if (d.dariPos) { const dp = Object.assign({}, d.dariPos); delete dp[T.pos]; d.dariPos = dp; } if (d.jamBayarPos) { const jp = Object.assign({}, d.jamBayarPos); delete jp[T.pos]; d.jamBayarPos = jp; }
  const arsip = { id: idBatal, tanggal: w.tanggal, jam: w.jam, koleksi: 'biayaBulanan', idDok: T.bulan + '|' + T.pos, tanggalDok: T.tanggal, pemasok: '', ringkas: ruJenisPos(T) + ' · ' + RP(T.n), alasan: a,
    jenisBatal: 'uang', bentuk: 'tagihan', dokumen: [], bagian: [{ bulan: T.bulan, pos: T.pos, nominal: T.n, tanggalBayar: T.tanggal, dari: T.dari, jam: T.jam }], efek: e, koreksi: { tutup: R.tutup, titik: R.titik } };
  return { dokumen: [{ koleksi: 'bukuHapus', data: arsip }, { koleksi: 'biayaBulanan', data: d }].concat(R.dokumen), hapus: [], jejakHapus: 'Batal: ' + arsip.ringkas + ' — ' + a,
    patch: { kabar: 'Dibatalkan — ' + arsip.ringkas + ' kembali belum dibayar. ' + R.akibat.join(' · ') + (R.akibat.length ? ' · ' : '') + 'Salinannya di daftar Dibatalkan (bisa dipulihkan).', kabarAwas: false } };
}
function ruPulihPos(x, w) {
  const b = Array.isArray(x.bagian) ? x.bagian[0] : null; const P = b ? POS_BIAYA_BULANAN.find((q) => q.kunci === b.pos) : null; if (!b || !P || !(ruN(b.nominal) > 0) || !b.tanggalBayar) return { tolak: 'Salinan tagihan ini tidak lengkap — tidak bisa dipulihkan dari sini' };
  const k = tolakKunci('biayaBulanan', { bulan: b.bulan }, 'bulan itu sudah dikunci — tidak bisa dipulihkan') || tolakKunciTanggal(b.tanggalBayar, 'bulan itu sudah dikunci — tidak bisa dipulihkan') || ruPosDitutup(b.bulan, b.tanggalBayar, 'catatannya tidak dipulihkan lagi');
  if (k) return { tolak: k };
  const kini = ruDokBulan(b.bulan); if (kini && ruN(kini[b.pos]) > 0 && ruTglPos(kini, b.pos)) return { tolak: P.label + ' ' + namaBulanPanjang(b.bulan + '-01') + ' sudah dibayar lagi (' + tanggalPendek(ruTglPos(kini, b.pos)) + ') — tidak dipulihkan supaya tidak dihitung dua kali' };
  const d = ruPetaPos(kini || { id: b.bulan, bulan: b.bulan }); d.id = b.bulan; d.bulan = b.bulan; d[b.pos] = ruN(b.nominal); d.tanggalBayarPos = Object.assign({}, d.tanggalBayarPos, { [b.pos]: b.tanggalBayar });
  if (b.dari) d.dariPos = Object.assign({}, d.dariPos || {}, { [b.pos]: b.dari }); if (b.jam) d.jamBayarPos = Object.assign({}, d.jamBayarPos || {}, { [b.pos]: b.jam });
  const R = ruKoreksiPulih([{ koleksi: 'biayaBulanan', data: { tanggal: b.tanggalBayar, jam: b.jam || '', id: 0 } }], x, w.kini);
  for (const t of R.dokumen) { const kk = tolakBukuDitutup(t.data, 'tutup hari & patokan kas ' + String(t.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (kk) return { tolak: kk }; }
  return { dokumen: [{ koleksi: 'biayaBulanan', data: d }].concat(R.dokumen), hapus: [{ koleksi: 'bukuHapus', id: String(x.id) }], jejakHapus: 'Pulihkan: ' + String(x.ringkas || ''),
    patch: { kabar: 'Dipulihkan — ' + String(x.ringkas || '') + ' kembali dibayar ' + tanggalPendek(b.tanggalBayar) + (R.akibat.length ? '. ' + R.akibat.join(' · ') : ''), kabarAwas: false } };
}

// ---------- daftar dibatalkan, pulihkan, hapus permanen ----------
/** Baris daftar Dibatalkan (semua isi bukuHapus: uang tahap 1, barang tahap 2 + hapus kedatangan / kantong / adukan lama), terbaru di atas. */
export function ruDibatalkan() {
  return cacheMentah('bukuHapus').slice().sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || ruJam(b.jam).localeCompare(ruJam(a.jam)))
    .map((x) => {
      // K-B (23 Nov 2026): salinan catatan bertanggal tahun yang sudah ditutup buku tidak dipulihkan lagi — tombolnya tidak tampil, sebabnya ditulis
      // upah & tagihan (23 Nov 2026): bagian dokumen biayaBulanan disimpan di `bagian` — bulannya & tanggal bayarnya ikut diperiksa
      const bagian = Array.isArray(x.bagian) ? x.bagian : [];
      const ditutup = (Array.isArray(x.dokumen) ? x.dokumen.map((d) => tolakBukuDitutup(d && d.data, 'catatannya tidak dipulihkan lagi')).find(Boolean) || '' : '')
        || bagian.map((b) => tolakBukuDitutup({ bulan: b && b.bulan }, 'catatannya tidak dipulihkan lagi') || tolakBukuDitutup({ tanggal: b && b.tanggalBayar }, 'catatannya tidak dipulihkan lagi')).find(Boolean) || '';
      const salinan = (x.jenisBatal === 'uang' || x.jenisBatal === 'barang') && ((Array.isArray(x.dokumen) && x.dokumen.length > 0) || bagian.length > 0);   // barang: tahap 2 (riwayat-barang-logika.js rbSusunPulih)
      return { id: String(x.id), tanggal: String(x.tanggal || ''), jam: ruJam(x.jam), oleh: String(x.oleh || ''), koleksi: String(x.koleksi || ''), tanggalDok: String(x.tanggalDok || ''),
        ringkas: String(x.ringkas || ''), alasan: String(x.alasan || ''), jenisBatal: String(x.jenisBatal || ''), bisaPulih: salinan && !ditutup,
        sebabTidakPulih: !salinan ? 'dihapus lewat layarnya sendiri (tanpa salinan utuh) — tidak bisa dipulihkan dari sini' : ditutup };
    });
}
/** Pulihkan pembatalan uang `idBatal`: catatan ditulis kembali (id sama), koreksi dibalik menurut keadaan SEKARANG, titipan kembali, baris Dibatalkan dihapus. */
export function ruSusunPulih(idBatal, w) {
  const x = cacheMentah('bukuHapus').find((b) => String(b.id) === String(idBatal)); if (!x) return { tolak: 'Catatan dibatalkan itu tidak ditemukan' };
  if (x.jenisBatal === 'uang' && x.bentuk === 'upah') return ruPulihSlip(x, w); if (x.jenisBatal === 'uang' && x.bentuk === 'tagihan') return ruPulihPos(x, w);
  if (x.jenisBatal !== 'uang' || !Array.isArray(x.dokumen) || !x.dokumen.length) return { tolak: 'Yang ini dihapus lewat layarnya sendiri, tanpa salinan utuh — tidak bisa dipulihkan dari sini' };
  for (const d of x.dokumen) {
    if (ruCari(d.koleksi, d.data.id)) return { tolak: 'Catatan ' + d.koleksi + ' dengan nomor yang sama sudah ada lagi — tidak dipulihkan dua kali' };
    const k = tolakKunci(d.koleksi, d.data, 'bulan itu sudah dikunci — tidak bisa dipulihkan') || tolakBukuDitutup(d.data, 'catatannya tidak dipulihkan lagi'); if (k) return { tolak: k };
  }
  const K = x.dokumen.map((d) => ({ koleksi: d.koleksi, data: d.data }));
  // pengaruh catatan dihitung dari salinannya (catatannya sedang tidak ada di buku): efek tersimpan saat dibatalkan
  const R = ruKoreksiPulih(K, x, w.kini);
  for (const d of R.dokumen) { const k = tolakBukuDitutup(d.data, 'tutup hari & patokan kas ' + String(d.data.tanggal || '').slice(0, 4) + ' tidak diubah lagi'); if (k) return { tolak: k }; }
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
