// UANG & LAPORAN — KAS & REKENING (owner 26 Nov 2026, sensus ulang 26 Nov bagian 1c: A35 · A55 · A84 · A134 · B86 · B128). Logika tanpa DOM; awalan
// kh (buku kas harian semua tempat, pengingat setor & cocok) · cr (cocok rekening) — bundel uji jsc satu lingkup.
//
// SATU KEBENARAN UANG tetap saldoKantong() (uang-logika). Buku kas harian TIDAK punya rumus kas sendiri: posisi akhir hari = patokan terbaru pada/sebelum hari
// itu (isi tempat uang SESUDAH tutup hari — kolom `titik` dokumen tutupHari — atau titik kas sekarang, yang terbaru menang) + gerakan sesudahnya menurut
// saldoKantong + catatan bertanggal hari patokan yang dicatat SESUDAH patokan dipasang (aturan ugSesudahTitik, sama dengan rumus laci tutup hari). Gerakan
// satu hari per tempat = gerakan kas mesin (tempat menurut kantongGerakan) + amplop laba + pindah uang. Beda = akhir − (awal + gerakan) = hitungan fisik /
// patokan yang disetel ulang hari itu — DISEBUT per tempat, tidak disembunyikan, jadi tiap tempat menutup persis.
//
// COCOK REKENING (owner 26 Nov: "bangun keduanya, lalu sesuaikan, agar gua tidak perlu ngoding lagi"; nama bank di layar → "rekening usaha"): tiap uang yang lewat
// rekening dicentang "ada di mutasi" — dengan tangan ATAU dari berkas mutasi yang diunggah / ditempel (bentuk kolomnya diatur owner & diingat per bentuk
// kepala berkas). Hasil cocok (saldo bank, saldo buku, selisih, penjelasannya) DISIMPAN per bulan; titik kas TIDAK ditimpa — yang mau menyetel buku memakai
// Pindah uang › Catat isi rekening (pintunya sendiri). Rekening toko masih satu dengan uang pribadi owner: baris mutasi yang tidak ada di buku diberi jenis
// (uang pribadi · biaya bank · …, daftar owner) sebagai penjelasan. Tanpa rules baru: aturanToko/rekening (setelan & bentuk berkas, ikut riwayat setelan) +
// aturanToko/cocokRek-YYYY-MM (centang & hasil satu bulan — catatan, dilewati riwayat setelan). Pola penyimpanan = tinjauan bulanan (aturanToko/pondasi).
import { caraBayarKunci } from '../mesin/pembantu.js';
import { ambilTutupHari, ambilTitikKas, ambilAmplopLaba, ambilPindahUang, ambilPenjualan, ambilPiutangMutasi, ambilKasbonMutasi, ambilPengeluaranHarian, ingatGerakanKas, cacheMentah, kunciNota } from '../data/toko.js';
import { RP, hariIniIso, jamKini, tanggalPendek } from '../inti/format.js';
import { saldoKantong, ugTambahHari, ugHariKe, ugSesudahTitik, kantongGerakan, ugAmplopLawan, ugNamaTempat, ugAngka, ugKosong, ugAturDok, adalahMdr, ugSetor, ugSusulan } from './uang-logika.js';

export const KH_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];
export const CR_NAMA = 'Rekening usaha';
const khN = (v) => Number(v) || 0;
const khIsoSah = (t) => /^\d{4}-\d\d-\d\d$/.test(String(t || ''));
const khNol = () => ({ laci: 0, brankas: 0, rekening: 0, amplop: 0 });

// ==================== BUKU KAS HARIAN · SEMUA TEMPAT (A55) ====================
/** Patokan terbaru pada/sebelum iso: isi tempat uang sesudah tutup hari (tutupHari.titik) atau titik kas sekarang — tanggal terbaru, lalu jam pasang terbaru. */
export function khPatokan(iso) {
  const ada = [];
  ambilTutupHari().forEach((d) => { if (!d || !d.titik || !khIsoSah(d.tanggal) || d.tanggal > iso) return;
    ada.push({ tanggal: d.tanggal, laci: khN(d.titik.laci), brankas: khN(d.titik.brankas), rekening: khN(d.titik.rekening), amplop: khN(d.titik.amplop), diubahPada: String(d.diubahPada || ''), sumber: 'hitungan tutup hari ' + tanggalPendek(d.tanggal) }); });
  const t = ambilTitikKas();
  if (t && khIsoSah(t.tanggal) && t.tanggal <= iso) ada.push({ tanggal: t.tanggal, laci: khN(t.laci), brankas: khN(t.brankas), rekening: khN(t.rekening), amplop: khN(t.amplop), diubahPada: String(t.diubahPada || ''), dipasangPada: String(t.dipasangPada || ''), sumber: 'patokan kas ' + tanggalPendek(t.tanggal) });
  ada.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.diubahPada.localeCompare(b.diubahPada));
  return ada.length ? ada[ada.length - 1] : null;
}
/** Catatan bertanggal hari patokan yang dicatat SESUDAH patokan dipasang — per tempat (gerakan kas + amplop laba + pindah uang; sisihan & amankan tutup itu
 *  sendiri tidak). Satu aturan dengan tutup hari & Catat isi tempat: ugSusulan (uang-logika, owner 26 Nov 2026 — paket brankas & catatan susulan). */
export function khSusulan(t) { return ugSusulan(t); }
/** Isi tiap tempat uang pada AKHIR hari iso. ada=false + sebab bila tidak ada patokan pada/sebelum hari itu (tidak ditebak). */
export function khPosisi(iso) {
  const t = khPatokan(iso); if (!t) return { ada: false, iso, sebab: 'belum ada hitungan tutup hari atau patokan kas pada atau sebelum ' + tanggalPendek(iso) };
  const S = saldoKantong(iso, t); if (!S.ada) return { ada: false, iso, sebab: 'patokan ' + t.sumber + ' tidak bisa dipakai' };
  const su = khSusulan(t); const out = { ada: true, iso, patokan: t, susulan: su, nSusulan: KH_TEMPAT.filter((k) => Math.abs(su[k]) >= 0.5).length,
    sumber: t.sumber + (t.tanggal < iso ? ' + catatan uang sesudahnya sampai ' + tanggalPendek(iso) : '') };
  KH_TEMPAT.forEach((k) => { out[k] = S[k] + su[k]; }); out.total = KH_TEMPAT.reduce((a, k) => a + out[k], 0); return out;
}
/** Gerakan satu hari per tempat: masuk/keluar (gerakan kas mesin) + pindah masuk/keluar (amplop laba & pindah uang). */
export function khGerakHari(iso) {
  const G = {}; KH_TEMPAT.forEach((k) => { G[k] = { masuk: 0, keluar: 0, pindahMasuk: 0, pindahKeluar: 0, n: 0 }; }); const tempat = kantongGerakan();
  ingatGerakanKas().forEach((r) => { if (r.t !== iso) return; const k = tempat(r); if (!G[k]) return; if (r.masuk > 0) G[k].masuk += r.masuk; if (r.keluar > 0) G[k].keluar += r.keluar; G[k].n += 1; });
  ambilAmplopLaba().forEach((a) => { if (a.tutupBuku || a.tanggal !== iso) return; const n = khN(a.nominal); if (!(n > 0)) return; const lain = ugAmplopLawan(a);
    if (a.tipe === 'ambil') { G.amplop.pindahKeluar += n; G[lain].pindahMasuk += n; } else { G[lain].pindahKeluar += n; G.amplop.pindahMasuk += n; } G.amplop.n += 1; G[lain].n += 1; });
  ambilPindahUang().forEach((p) => { if (p.tanggal !== iso) return; const n = khN(p.nominal); if (!(n > 0)) return; if (G[p.dari]) { G[p.dari].pindahKeluar += n; G[p.dari].n += 1; } if (G[p.ke]) { G[p.ke].pindahMasuk += n; G[p.ke].n += 1; } });
  return G;
}
/**
 * BUKU KAS HARIAN hari iso: per tempat (laci · brankas · rekening · amplop) awal (akhir kemarin) → masuk − keluar ± pindah → beda → akhir; jumlah empat tempat.
 * Beda ≠ 0 = hitungan fisik tutup hari / patokan yang disetel ulang hari itu (disebut dengan sebabnya bila dikenali). Hari ini: akhir = isi sekarang.
 */
export function khBukuHari(iso, kini) {
  const kemarin = ugTambahHari(iso, -1); const A = khPosisi(kemarin), Z = khPosisi(iso); const G = khGerakHari(iso);
  const T = ambilTutupHari().find((d) => d && d.tanggal === iso) || null; const selLaci = T ? Number(T.selisihLaci !== undefined && T.selisihLaci !== null ? T.selisihLaci : T.selisih) || 0 : 0;
  const tempat = KH_TEMPAT.map((k) => { const g = G[k]; const awal = A.ada ? A[k] : null; const akhir = Z.ada ? Z[k] : null; const gerak = g.masuk - g.keluar + g.pindahMasuk - g.pindahKeluar;
    const beda = awal !== null && akhir !== null ? Math.round(akhir - awal - gerak) : null;
    const sebab = beda === null ? (awal === null ? 'awal hari belum bisa dihitung — ' + A.sebab : 'akhir hari belum bisa dihitung — ' + Z.sebab) : beda === 0 ? '' :
      k === 'laci' && T && Math.round(selLaci) === beda ? 'selisih hitungan laci tutup hari ' + (T.jam || '') :
      T ? 'hitungan tutup hari ' + (T.jam || '') + ' / patokan disetel ulang' : 'patokan kas disetel ulang hari ini';
    return { id: k, nama: ugNamaTempat(k), awal, masuk: g.masuk, keluar: g.keluar, pindahMasuk: g.pindahMasuk, pindahKeluar: g.pindahKeluar, gerak, beda, akhir, n: g.n, sebab }; });
  const jml = (f) => (tempat.some((x) => x[f] === null) ? null : tempat.reduce((a, x) => a + x[f], 0));
  const hariIni = iso === hariIniIso(kini || new Date());
  // penjaga identitas: hari ini, empat tempat (tanpa catatan susulan) = kas mesin (kasPada) — kalau tidak, laporkan (tidak dibetulkan di sini)
  let cocokMesin = null; if (hariIni && Z.ada) { const S = saldoKantong(); if (S.ada && S.mesin !== null && S.mesin !== undefined) { const su = KH_TEMPAT.reduce((a, k) => a + Z.susulan[k], 0); cocokMesin = Math.abs(Z.total - su - S.mesin) < 0.5; } }
  return { iso, hariIni, awal: A, akhir: Z, tempat, total: { awal: jml('awal'), masuk: jml('masuk'), keluar: jml('keluar'), pindah: tempat.reduce((a, x) => a + x.pindahMasuk - x.pindahKeluar, 0), beda: jml('beda'), akhir: jml('akhir') },
    tutup: T ? { jam: T.jam || '', selisihLaci: Math.round(selLaci) } : null, cocokMesin,
    kosong: tempat.every((x) => x.n === 0) && !T, teksAwal: A.ada ? A.sumber : A.sebab, teksAkhir: Z.ada ? Z.sumber : Z.sebab };
}

// ==================== COCOK REKENING (A35 · A134 · B86 · B128) ====================
export const CR_ATUR_ID = 'rekening';
export const CR_DOK = (bulan) => 'cocokRek-' + String(bulan).slice(0, 7);
export const CR_JENIS_BAWAAN = ['Uang pribadi owner', 'Biaya bank / admin', 'Bunga / jasa', 'Belum dicatat di buku', 'Lain-lain'];
export const CR_ATUR_BAWAAN = { toleransiHari: 3, toleransiRp: 0, jenis: CR_JENIS_BAWAAN, bentuk: [] };
export const CR_BULAN_MAKS_BARIS = 300;   // penjaga ukuran dokumen satu bulan (baris mutasi yang disimpan bersama hasil)
export function crAtur() {
  const a = ugAturDok(CR_ATUR_ID) || {}; const angka = (k, maks) => (isFinite(Number(a[k])) && Number(a[k]) >= 0 && Number(a[k]) <= maks && a[k] !== null && a[k] !== '' ? Math.round(Number(a[k])) : CR_ATUR_BAWAAN[k]);
  return { toleransiHari: angka('toleransiHari', 31), toleransiRp: angka('toleransiRp', 100000), jenis: Array.isArray(a.jenis) && a.jenis.length ? a.jenis.map(String) : CR_JENIS_BAWAAN.slice(),
    bentuk: Array.isArray(a.bentuk) ? a.bentuk.filter((b) => b && typeof b === 'object') : [], dariOwner: !!ugAturDok(CR_ATUR_ID) };
}
/** Simpan setelan cocok rekening (toleransi hari & rupiah, jenis penjelasan). Bentuk berkas tersimpan dibawa. */
export function crSusunAtur(isi, w) {
  const A = crAtur(); const baca = (k, maks, nama) => { const v = isi[k]; if (v === undefined || ugKosong(v)) return { n: A[k] }; const n = ugAngka(v); return Number.isInteger(n) && n >= 0 && n <= maks ? { n } : { tolak: nama + ' harus bilangan bulat 0–' + maks }; };
  const h = baca('toleransiHari', 31, 'Selisih hari mutasi'), r = baca('toleransiRp', 100000, 'Selisih rupiah'); if (h.tolak || r.tolak) return { tolak: h.tolak || r.tolak };
  const jenis = (Array.isArray(isi.jenis) ? isi.jenis : A.jenis).map((x) => String(x || '').trim()).filter(Boolean).filter((x, i, s) => s.indexOf(x) === i).slice(0, 12); if (!jenis.length) return { tolak: 'Daftar jenis penjelasan tidak boleh kosong' };
  const lama = ugAturDok(CR_ATUR_ID) || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: CR_ATUR_ID, tanggal: w.tanggal, jam: w.jam, toleransiHari: h.n, toleransiRp: r.n, jenis, bentuk: A.bentuk }) }],
    patch: { aturCr: null, kabar: 'Aturan cocok rekening disimpan — mutasi boleh beda ' + h.n + ' hari' + (r.n ? ' & ' + RP(r.n) : ', rupiah harus persis') + ' · ' + jenis.length + ' jenis penjelasan', kabarAwas: false } };
}

// ---------- baris buku rekening ----------
/**
 * Semua uang yang lewat REKENING dalam [dari, sampai] — dari sumber yang sama dengan saldoKantong: gerakan kas mesin bertempat rekening (kantongGerakan) +
 * pindah uang ke/dari rekening + amplop laba berlawan rekening. Penjualan QRIS / transfer satu NOTA = satu baris (satu kali pindai / satu kali transfer).
 * → [{ kunci, t, jam, jenis: qris|transfer|mdr|pindah|amplop|masuk|keluar, ket, masuk, keluar, arah, n }] urut tanggal-jam. Σ (masuk − keluar) = gerakan rekening.
 */
export function crBaris(dari, sampai) {
  const tempat = kantongGerakan(); const jual = {}; ambilPenjualan().forEach((p) => { jual[String(p.id)] = p; });
  const cara = {}; ambilPiutangMutasi().forEach((m) => { if (m && m.tipe === 'bayar') cara[String(m.id)] = { cara: caraBayarKunci(m), ket: 'Bayar bon · ' + String(m.namaPelanggan || '').trim() }; });
  ambilKasbonMutasi().forEach((m) => { if (m && m.tipe === 'bayar') cara[String(m.id)] = { cara: caraBayarKunci(m), ket: 'Kasbon kembali · ' + String(m.namaPegawai || '').trim() }; });
  const mdr = {}; ambilPengeluaranHarian().forEach((h) => { if (adalahMdr(h)) mdr[String(h.id)] = true; });
  const peta = {}; const urut = [];
  const dorong = (kunci, t, jam, jenis, ket, masuk, keluar) => { let x = peta[kunci]; if (!x) { x = peta[kunci] = { kunci, t, jam: String(jam || ''), jenis, ket, masuk: 0, keluar: 0 }; urut.push(x); } x.masuk += masuk; x.keluar += keluar; };
  const dlm = (t) => khIsoSah(t) && t >= dari && t <= sampai;
  ingatGerakanKas().forEach((r) => { if (!dlm(r.t) || tempat(r) !== 'rekening') return; const p = jual[String(r.id)];
    if (p && r.masuk > 0) { const j = caraBayarKunci(p) === 'transfer' ? 'transfer' : 'qris'; dorong('n:' + kunciNota(p), r.t, r.jam, j, 'Jual ' + (j === 'qris' ? 'QRIS' : 'transfer') + (String(p.namaPelanggan || '').trim() ? ' · ' + String(p.namaPelanggan).trim() : ''), r.masuk, 0); return; }
    const c = cara[String(r.id)]; const jenis = mdr[String(r.id)] && r.keluar > 0 ? 'mdr' : c && r.masuk > 0 ? (c.cara === 'transfer' ? 'transfer' : 'qris') : r.masuk > 0 ? 'masuk' : 'keluar';
    dorong('g:' + r.id + ':' + (r.masuk > 0 ? 'm' : 'k'), r.t, r.jam, jenis, c && r.masuk > 0 ? c.ket + (c.cara === 'qris' ? ' · QRIS' : c.cara === 'transfer' ? ' · transfer' : '') : String(r.label || ''), r.masuk || 0, r.keluar || 0); });
  ambilPindahUang().forEach((p) => { if (!dlm(p.tanggal)) return; const n = khN(p.nominal); if (!(n > 0)) return;
    if (p.dari === 'rekening') dorong('p:' + p.id + ':k', p.tanggal, p.jam, 'pindah', 'Pindah ke ' + ugNamaTempat(p.ke).toLowerCase() + (p.alasan ? ' · ' + p.alasan : ''), 0, n);
    if (p.ke === 'rekening') dorong('p:' + p.id + ':m', p.tanggal, p.jam, 'pindah', 'Dari ' + ugNamaTempat(p.dari).toLowerCase() + (p.alasan ? ' · ' + p.alasan : ''), n, 0); });
  ambilAmplopLaba().forEach((a) => { if (a.tutupBuku || !dlm(a.tanggal) || ugAmplopLawan(a) !== 'rekening') return; const n = khN(a.nominal); if (!(n > 0)) return;
    if (a.tipe === 'ambil') dorong('a:' + a.id, a.tanggal, a.jam, 'amplop', 'Dari amplop laba' + (a.catatan ? ' · ' + a.catatan : ''), n, 0); else dorong('a:' + a.id, a.tanggal, a.jam, 'amplop', 'Ke amplop laba' + (a.catatan ? ' · ' + a.catatan : ''), 0, n); });
  urut.forEach((x) => { const net = x.masuk - x.keluar; x.arah = net >= 0 ? 'masuk' : 'keluar'; x.n = Math.round(Math.abs(net) * 100) / 100; });
  return urut.filter((x) => x.n > 0).sort((a, b) => a.t.localeCompare(b.t) || a.jam.localeCompare(b.jam) || a.kunci.localeCompare(b.kunci));
}
/** Dokumen cocok satu bulan (aturanToko/cocokRek-YYYY-MM) atau null. */
export const crDokBulan = (bulan) => cacheMentah('aturan').find((d) => String(d.id) === CR_DOK(bulan)) || null;
/** Semua centang: { kunci: { t (tanggal dicentang), cara: tangan|berkas, m (tanggal mutasi) } } dari dokumen bulan-bulan. */
export function crCek() {
  const out = {}; cacheMentah('aturan').forEach((d) => { if (!d || String(d.id).indexOf('cocokRek-') !== 0 || !d.cek || typeof d.cek !== 'object') return; Object.keys(d.cek).forEach((k) => { if (d.cek[k]) out[k] = d.cek[k]; }); });
  return out;
}
/** Baris rekening [dari, sampai] + tanda centangnya. */
export function crBarisCek(dari, sampai) { const C = crCek(); return crBaris(dari, sampai).map((x) => Object.assign(x, { cek: C[x.kunci] || null })); }
/**
 * Centang / lepas sekumpulan baris (objek dari crBaris). Satu dokumen per BULAN tanggal barisnya; kolom lain dokumen itu dibawa. nyala=false melepas.
 * cara = 'tangan' | 'berkas'; m = { kunci: tanggal mutasi } (pilihan, dari berkas).
 */
export function crSusunCentang(baris, nyala, w, cara, m) {
  const daftar = (Array.isArray(baris) ? baris : []).filter((x) => x && x.kunci && khIsoSah(x.t)); if (!daftar.length) return { tolak: 'Tidak ada baris yang dipilih' };
  const per = {}; daftar.forEach((x) => { const b = x.t.slice(0, 7); (per[b] = per[b] || []).push(x); });
  const dokumen = Object.keys(per).sort().map((b) => { const lama = crDokBulan(b) || {}; const cek = Object.assign({}, lama.cek || {});
    per[b].forEach((x) => { if (nyala) cek[x.kunci] = Object.assign({ t: w.tanggal, cara: cara === 'berkas' ? 'berkas' : 'tangan' }, m && m[x.kunci] ? { m: String(m[x.kunci]) } : {}); else delete cek[x.kunci]; });
    return { koleksi: 'aturanToko', data: Object.assign({}, lama, { id: CR_DOK(b), bulan: b, tanggal: w.tanggal, jam: w.jam, cek }) }; });
  const rp = daftar.reduce((a, x) => a + (x.arah === 'masuk' ? x.n : -x.n), 0);
  return { dokumen, patch: { kabar: daftar.length + ' baris rekening ' + (nyala ? 'ditandai ADA di mutasi' : 'dilepas tandanya') + (cara === 'berkas' ? ' (dari berkas mutasi)' : '') + ' · ' + (rp < 0 ? '−' : '') + RP(Math.abs(rp)), kabarAwas: false } };
}

// ---------- membaca berkas mutasi (CSV / TSV / teks tempelan) ----------
const CR_BULAN = { jan: 1, feb: 2, mar: 3, apr: 4, mei: 5, may: 5, jun: 6, jul: 7, agu: 8, agt: 8, aug: 8, sep: 9, okt: 10, oct: 10, nov: 11, des: 12, dec: 12 };
/** Tanggal dari teks: yyyy-mm-dd · dd/mm/yyyy · dd-mm-yy · dd/mm (tahun bawaan) · "26 Nov 2026" · "26-Nov-26". urut 'dmy' (bawaan) | 'mdy' | 'ymd'. → iso | ''. */
export function crTanggal(teks, urut, tahunBawaan) {
  const s = String(teks || '').trim(); if (!s) return ''; const th = (y) => (y === undefined || y === null || y === '' ? Number(tahunBawaan) || 0 : String(y).length === 2 ? 2000 + Number(y) : Number(y));
  const jadi = (y, m, d) => { y = Number(y); m = Number(m); d = Number(d); if (!(y >= 2000 && y <= 2100 && m >= 1 && m <= 12 && d >= 1 && d <= 31)) return ''; const iso = y + '-' + String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0');
    const x = new Date(iso + 'T00:00:00Z'); return isFinite(x.getTime()) && x.toISOString().slice(0, 10) === iso ? iso : ''; };
  let m = s.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/); if (m) return jadi(m[1], m[2], m[3]);
  m = s.match(/^(\d{1,2})[\s\-/.]+([A-Za-z]{3,})[a-z]*\.?[\s\-/.,]*(\d{2,4})?/); if (m && CR_BULAN[m[2].slice(0, 3).toLowerCase()]) return jadi(th(m[3]), CR_BULAN[m[2].slice(0, 3).toLowerCase()], m[1]);
  m = s.match(/^(\d{1,2})[-/.](\d{1,2})(?:[-/.](\d{2,4}))?(?!\d)/);
  if (m) return urut === 'mdy' ? jadi(th(m[3]), m[1], m[2]) : urut === 'ymd' ? '' : jadi(th(m[3]), m[2], m[1]);
  return '';
}
/** Rupiah dari teks: "1.234.567,00" · "1,234,567.00" · "Rp 50.000" · "(25.000)" · "-25000" · "25.000 DB" / "CR". desimal ',' | '.' | '' (tebak). → { n, tanda: -1|1|0 } | null. */
export function crAngka(teks, desimal) {
  let s = String(teks === undefined || teks === null ? '' : teks).trim(); if (!s) return null; let tanda = 0;
  if (/\b(DB|D|DEBET|DEBIT)\s*$/i.test(s)) { tanda = -1; s = s.replace(/\b(DB|D|DEBET|DEBIT)\s*$/i, ''); } else if (/\b(CR|K|KR|KREDIT|CREDIT)\s*$/i.test(s)) { tanda = 1; s = s.replace(/\b(CR|K|KR|KREDIT|CREDIT)\s*$/i, ''); }
  s = s.replace(/rp\.?/ig, '').replace(/\s+/g, ''); if (/^\(.*\)$/.test(s)) { tanda = -1; s = s.slice(1, -1); } if (/^-/.test(s)) { tanda = -1; s = s.slice(1); } else if (/^\+/.test(s)) { tanda = 1; s = s.slice(1); } if (/-$/.test(s)) { tanda = -1; s = s.slice(0, -1); }
  if (!/^[\d.,]+$/.test(s) || !/\d/.test(s)) return null;
  let d = desimal; if (d !== ',' && d !== '.') d = /^\d{1,3}(\.\d{3})+(,\d{1,2})?$/.test(s) || /^\d+,\d{1,2}$/.test(s) ? ',' : /^\d{1,3}(,\d{3})+(\.\d{1,2})?$/.test(s) || /^\d+\.\d{1,2}$/.test(s) ? '.' : s.indexOf(',') >= 0 && s.indexOf('.') < 0 && !/,\d{3}$/.test(s) ? ',' : '.';
  const t = d === ',' ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, ''); const n = Number(t); return isFinite(n) ? { n: Math.round(n * 100) / 100, tanda } : null;
}
/** Pemisah kolom yang paling ajek di baris-baris awal (',', ';', TAB, '|'); '' = teks bebas (mis. disalin dari PDF). */
export function crPemisah(baris) {
  const contoh = baris.filter((b) => b.trim()).slice(0, 12); let pilih = '', skor = 0;
  [',', ';', '\t', '|'].forEach((p) => { const n = contoh.map((b) => crPecahSel(b, p).length); const hit = {}; n.forEach((x) => { hit[x] = (hit[x] || 0) + 1; });
    const modus = Number(Object.keys(hit).sort((a, b) => hit[b] - hit[a] || b - a)[0]); const ajek = n.filter((x) => x >= 3 && x === modus).length;
    // koma desimal tanpa tanda kutip (teks disalin dari PDF: "750.000,00 3.096.000,00") memecah angka — potongan "00 …" di awal sel = bukan pemisah kolom
    if (p === ',' && contoh.filter((b) => crPecahSel(b, ',').some((c, i) => i > 0 && /^\d{1,2}(\s|$)/.test(c))).length >= contoh.length * 0.3) return;
    if (ajek > skor) { skor = ajek; pilih = p; } });
  return skor >= Math.max(2, Math.ceil(contoh.length * 0.6)) ? pilih : '';
}
/** Pecah satu baris CSV dengan tanda kutip ("a, b" tetap satu sel). */
export function crPecahSel(baris, p) {
  const out = []; let sel = '', kutip = false; const s = String(baris);
  for (let i = 0; i < s.length; i++) { const c = s[i]; if (kutip) { if (c === '"' && s[i + 1] === '"') { sel += '"'; i++; } else if (c === '"') kutip = false; else sel += c; } else if (c === '"') kutip = true; else if (c === p) { out.push(sel.trim()); sel = ''; } else sel += c; }
  out.push(sel.trim()); return out;
}
const CR_KEPALA = [['tanggal', /tanggal|tgl|date|waktu|posting/i], ['ket', /keterangan|deskripsi|uraian|descr|remark|berita|detail|transaksi/i], ['keluar', /debet|debit|keluar|penarikan|\bdb\b|withdraw/i],
  ['masuk', /kredit|credit|masuk|setoran|\bcr\b|deposit/i], ['arah', /^(db\s*\/\s*cr|cr\s*\/\s*db|d\s*\/\s*k|k\s*\/\s*d|jenis|tipe|type)$/i], ['saldo', /saldo|balance/i], ['nominal', /mutasi|jumlah|nominal|amount|nilai/i]];
/** Tanda pengenal kepala berkas (untuk mengingat bentuknya): sel kepala dirapikan & digabung. */
export const crTandaKepala = (sel) => (sel || []).map((x) => String(x || '').toLowerCase().replace(/[^a-z0-9]/g, '')).join('|');
/** Tebak bentuk dari sel-sel tabel: baris kepala (sel teks bernama tanggal…), kolom per arti; tanpa kepala → dari isinya. */
export function crTebakBentuk(tabel, tahun) {
  let kepala = -1; for (let i = 0; i < Math.min(tabel.length, 15); i++) { if (tabel[i].some((c) => CR_KEPALA[0][1].test(c)) && tabel[i].filter((c) => /[a-z]/i.test(c)).length >= 2) { kepala = i; break; } }
  const kol = { tanggal: -1, ket: -1, nominal: -1, masuk: -1, keluar: -1, arah: -1, saldo: -1 };
  if (kepala >= 0) { tabel[kepala].forEach((c, i) => { const x = CR_KEPALA.find((k) => k[1].test(String(c).trim())); if (x && kol[x[0]] < 0) kol[x[0]] = i; }); }
  const isi = tabel.slice(kepala + 1).filter((r) => r.some((c) => c)).slice(0, 30); const lebar = isi.reduce((a, r) => Math.max(a, r.length), 0);
  const rasio = (i, uji) => (isi.length ? isi.filter((r) => uji(r[i])).length / isi.length : 0);
  if (kol.tanggal < 0) for (let i = 0; i < lebar; i++) if (rasio(i, (c) => !!crTanggal(c, 'dmy', tahun)) >= 0.6) { kol.tanggal = i; break; }
  const angkaKol = []; for (let i = 0; i < lebar; i++) if (i !== kol.tanggal && rasio(i, (c) => !ugKosong(c) && crAngka(c, '') !== null) >= 0.3) angkaKol.push(i);
  if (kol.nominal < 0 && kol.masuk < 0 && kol.keluar < 0) { const bebas = angkaKol.filter((i) => i !== kol.saldo); if (bebas.length) kol.nominal = bebas[0]; if (kol.saldo < 0 && bebas.length >= 2) kol.saldo = bebas[bebas.length - 1]; }
  if (kol.ket < 0) { let best = -1, panjang = 0; for (let i = 0; i < lebar; i++) { if (i === kol.tanggal || angkaKol.indexOf(i) >= 0) continue; const p = isi.reduce((a, r) => a + String(r[i] || '').length, 0); if (p > panjang) { panjang = p; best = i; } } kol.ket = best; }
  return { kepala, kolom: kol, urut: 'dmy', desimal: '', nama: '' };
}
/** Arah dari sel arah (DB/CR …). */
const crArahSel = (c) => (/^(cr|k|kr|kredit|credit|masuk|in)\b/i.test(String(c || '').trim()) ? 1 : /^(db|d|debet|debit|keluar|out)\b/i.test(String(c || '').trim()) ? -1 : 0);
/**
 * Baca isi berkas / tempelan. bentuk (pilihan) = { kepala, kolom: { tanggal, ket, nominal, masuk, keluar, arah, saldo }, urut, desimal }; kosong = bentuk tersimpan
 * yang tanda kepalanya sama, kalau tidak ada = tebakan. Teks tanpa pemisah kolom = baris bebas (tanggal di depan, angka rupiah; DB/CR atau tanda minus = arah;
 * dua angka atau lebih = nominal lalu saldo). → { mode, bentuk, dikenali (bentuk tersimpan), sel (kepala), contoh, baris: [{ no, tanggal, ket, n, arah, saldo }], lewat: [{ no, teks, sebab }] }
 */
export function crBacaMutasi(teks, bentuk, kini) {
  const tahun = Number(hariIniIso(kini || new Date()).slice(0, 4)); const semua = String(teks || '').replace(/^\uFEFF/, '').split(/\r?\n/); const A = crAtur();
  const p = crPemisah(semua); const baris = [], lewat = [];
  if (!p) {   // teks bebas
    semua.forEach((b, i) => { const t = b.trim(); if (!t) return; const tg = crTanggal(t, (bentuk && bentuk.urut) || 'dmy', tahun); if (!tg) { if (/\d/.test(t)) lewat.push({ no: i + 1, teks: t.slice(0, 80), sebab: 'tanpa tanggal di depan' }); return; }
      const angka = (t.match(/[-(]?\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?\)?(?:\s*(?:CR|DB|D|K|KR))?|[-(]?\d+[.,]\d{2}\)?(?:\s*(?:CR|DB|D|K|KR))?/gi) || []).map((x) => ({ x, v: crAngka(x, (bentuk && bentuk.desimal) || '') })).filter((y) => y.v && y.v.n > 0);
      if (!angka.length) { lewat.push({ no: i + 1, teks: t.slice(0, 80), sebab: 'tanpa angka rupiah' }); return; }
      const nom = angka.length >= 2 ? angka[angka.length - 2] : angka[0]; const saldo = angka.length >= 2 ? angka[angka.length - 1].v.n : null;
      let arah = nom.v.tanda || (/\b(CR|KREDIT|MASUK)\b/i.test(t) ? 1 : /\b(DB|DEBET|DEBIT|KELUAR)\b/i.test(t) ? -1 : 0); if (!arah) { lewat.push({ no: i + 1, teks: t.slice(0, 80), sebab: 'arah tidak terbaca (tulis DB / CR)' }); return; }
      const ket = t.replace(nom.x, ' ').replace(/^\S+/, '').replace(/\s+/g, ' ').trim().slice(0, 80);
      baris.push({ no: i + 1, tanggal: tg, ket, n: nom.v.n, arah: arah > 0 ? 'masuk' : 'keluar', saldo }); });
    return { mode: 'teks', bentuk: { mode: 'teks', urut: (bentuk && bentuk.urut) || 'dmy', desimal: (bentuk && bentuk.desimal) || '' }, dikenali: null, sel: [], contoh: semua.filter((b) => b.trim()).slice(0, 5).map((b) => [b]), baris, lewat };
  }
  const tabel = semua.map((b) => crPecahSel(b, p)); const tebak = crTebakBentuk(tabel, tahun);
  const sel = tebak.kepala >= 0 ? tabel[tebak.kepala] : []; const tanda = crTandaKepala(sel);
  const ingat = !bentuk && tanda ? A.bentuk.find((b) => b.tanda === tanda) || null : null; const B = Object.assign({}, tebak, ingat || {}, bentuk || {}, { pemisah: p }); const K = Object.assign({}, tebak.kolom, (ingat && ingat.kolom) || {}, (bentuk && bentuk.kolom) || {});
  tabel.forEach((r, i) => { if (i <= B.kepala || !r.some((c) => c)) return; const tg = K.tanggal >= 0 ? crTanggal(r[K.tanggal], B.urut, tahun) : '';
    if (!tg) { if (r.some((c) => crAngka(c, B.desimal) !== null)) lewat.push({ no: i + 1, teks: r.join(' · ').slice(0, 80), sebab: 'tanggal tidak terbaca' }); return; }
    let n = 0, arah = 0;
    if (K.masuk >= 0 || K.keluar >= 0) { const m = K.masuk >= 0 ? crAngka(r[K.masuk], B.desimal) : null; const k = K.keluar >= 0 ? crAngka(r[K.keluar], B.desimal) : null;
      if (m && m.n > 0) { n = m.n; arah = 1; } else if (k && k.n > 0) { n = k.n; arah = -1; } }
    else if (K.nominal >= 0) { const v = crAngka(r[K.nominal], B.desimal); if (v && v.n > 0) { n = v.n; arah = (K.arah >= 0 ? crArahSel(r[K.arah]) : 0) || v.tanda; } }
    if (!(n > 0)) { lewat.push({ no: i + 1, teks: r.join(' · ').slice(0, 80), sebab: 'nominal kosong / nol' }); return; }
    if (!arah) { lewat.push({ no: i + 1, teks: r.join(' · ').slice(0, 80), sebab: 'arah masuk/keluar tidak terbaca — pilih kolom masuk & keluar atau kolom DB/CR' }); return; }
    const sv = K.saldo >= 0 ? crAngka(r[K.saldo], B.desimal) : null;
    baris.push({ no: i + 1, tanggal: tg, ket: K.ket >= 0 ? String(r[K.ket] || '').slice(0, 80) : '', n, arah: arah > 0 ? 'masuk' : 'keluar', saldo: sv ? sv.n * (sv.tanda < 0 ? -1 : 1) : null }); });
  return { mode: 'tabel', bentuk: Object.assign({}, B, { mode: 'tabel', kolom: K, tanda }), dikenali: ingat ? ingat.nama || 'bentuk tersimpan' : null, sel, contoh: tabel.filter((r) => r.some((c) => c)).slice(0, 6), baris, lewat };
}
/** Simpan bentuk berkas (kolom per arti) supaya berkas berkepala sama langsung terbaca berikutnya — setelan owner (aturanToko/rekening.bentuk, paling banyak 8). */
export function crSusunBentuk(B, nama, w) {
  if (!B || B.mode !== 'tabel' || !B.tanda) return { tolak: 'Bentuk ini tidak punya baris kepala — tidak bisa diingat (teks tempelan selalu dibaca baris bebas)' };
  const K = B.kolom || {}; if (!(K.tanggal >= 0)) return { tolak: 'Pilih kolom tanggal dulu' }; if (!(K.nominal >= 0 || K.masuk >= 0 || K.keluar >= 0)) return { tolak: 'Pilih kolom nominal, atau kolom masuk & keluar' };
  const A = crAtur(); const nm = String(nama || '').trim().slice(0, 40) || 'Berkas mutasi'; const satu = { nama: nm, tanda: B.tanda, kepala: B.kepala, kolom: { tanggal: K.tanggal, ket: K.ket, nominal: K.nominal, masuk: K.masuk, keluar: K.keluar, arah: K.arah, saldo: K.saldo }, urut: B.urut || 'dmy', desimal: B.desimal || '' };
  const bentuk = [satu].concat(A.bentuk.filter((b) => b.tanda !== B.tanda)).slice(0, 8); const lama = ugAturDok(CR_ATUR_ID) || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: CR_ATUR_ID, tanggal: w.tanggal, jam: w.jam, toleransiHari: A.toleransiHari, toleransiRp: A.toleransiRp, jenis: A.jenis, bentuk }) }],
    patch: { kabar: 'Bentuk berkas "' + nm + '" diingat — berkas berkepala sama berikutnya langsung terbaca', kabarAwas: false } };
}
export function crSusunLupakanBentuk(tanda, w) {
  const A = crAtur(); if (!A.bentuk.some((b) => b.tanda === tanda)) return { tolak: 'Bentuk itu tidak tersimpan' }; const lama = ugAturDok(CR_ATUR_ID) || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: CR_ATUR_ID, tanggal: w.tanggal, jam: w.jam, toleransiHari: A.toleransiHari, toleransiRp: A.toleransiRp, jenis: A.jenis, bentuk: A.bentuk.filter((b) => b.tanda !== tanda) }) }], patch: { kabar: 'Bentuk berkas dilupakan', kabarAwas: false } };
}

// ---------- mencocokkan mutasi dengan buku ----------
/**
 * mutasi = baris crBacaMutasi; buku = baris crBaris di rentang mutasi ± toleransi hari. Aturan (berurutan, tiap baris buku dipakai sekali):
 *  1. PERSIS: arah sama, |rupiah| ≤ toleransiRp, |hari| ≤ toleransiHari — yang harinya paling dekat.
 *  2. QRIS GABUNG (pencairan GoPay Merchant tiap jam = beberapa pindai sekaligus, sudah dipotong MDR): mutasi MASUK = Σ QRIS buku satu hari (belum terpakai),
 *     atau Σ itu − potongan QRIS yang tercatat hari itu, pada hari mutasi atau sebelumnya ≤ toleransiHari.
 * → { pasang: [{ m, kunci: [..], cara: 'persis'|'gabung' }], mutasiSaja: [m], bukuSaja: [kunci], rentang: { dari, sampai } }
 */
export function crCocokkan(mutasi, buku, atur) {
  const A = atur || crAtur(); const pakai = {}; const pasang = []; const mutasiSaja = []; const tol = A.toleransiHari, tolRp = A.toleransiRp;
  const M = (mutasi || []).map((m, i) => Object.assign({ i }, m)).sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.i - b.i);
  M.forEach((m) => { const hm = ugHariKe(m.tanggal); let best = null, jarak = Infinity;
    buku.forEach((b) => { if (pakai[b.kunci] || b.arah !== m.arah || Math.abs(b.n - m.n) > tolRp + 0.001) return; const j = Math.abs(ugHariKe(b.t) - hm); if (j <= tol && j < jarak) { jarak = j; best = b; } });
    if (best) { pakai[best.kunci] = true; pasang.push({ m: m.i, kunci: [best.kunci], cara: 'persis' }); return; }
    if (m.arah === 'masuk') {
      for (let j = 0; j <= tol; j++) { const t = ugTambahHari(m.tanggal, -j); const q = buku.filter((b) => !pakai[b.kunci] && b.t === t && b.jenis === 'qris' && b.arah === 'masuk'); if (!q.length) continue;
        const d = buku.filter((b) => !pakai[b.kunci] && b.t === t && b.jenis === 'mdr'); const kotor = q.reduce((a, b) => a + b.n, 0); const pot = d.reduce((a, b) => a + b.n, 0);
        if (Math.abs(kotor - m.n) <= tolRp + 0.001 && (q.length > 1)) { q.forEach((b) => { pakai[b.kunci] = true; }); pasang.push({ m: m.i, kunci: q.map((b) => b.kunci), cara: 'gabung' }); return; }
        if (d.length && Math.abs(kotor - pot - m.n) <= tolRp + 0.001) { q.concat(d).forEach((b) => { pakai[b.kunci] = true; }); pasang.push({ m: m.i, kunci: q.concat(d).map((b) => b.kunci), cara: 'gabung' }); return; } }
    }
    mutasiSaja.push(m.i); });
  const dari = M.length ? M[0].tanggal : '', sampai = M.length ? M[M.length - 1].tanggal : '';
  return { pasang, mutasiSaja, bukuSaja: buku.filter((b) => !pakai[b.kunci] && (!dari || (b.t >= dari && b.t <= sampai))).map((b) => b.kunci), rentang: { dari, sampai } };
}
/** Rentang buku yang dibandingkan dengan sebuah berkas mutasi: tanggal pertama − toleransi … tanggal terakhir. */
export function crRentangBuku(mutasi, atur) { const A = atur || crAtur(); const t = (mutasi || []).map((m) => m.tanggal).filter(khIsoSah).sort(); return t.length ? { dari: ugTambahHari(t[0], -A.toleransiHari), sampai: t[t.length - 1] } : null; }

// ---------- hasil cocok saldo per bulan ----------
/** Semua hasil cocok yang tersimpan (terbaru dulu): { bulan, tanggal, saldoBank, saldoBuku, selisih, sisa, … }. */
export function crSemuaHasil() {
  const out = []; cacheMentah('aturan').forEach((d) => { if (!d || String(d.id).indexOf('cocokRek-') !== 0) return; [d.hasil].concat(Array.isArray(d.riwayatHasil) ? d.riwayatHasil : []).forEach((h) => { if (h && khIsoSah(h.tanggal)) out.push(Object.assign({ bulan: d.bulan || String(d.id).slice(9) }, h)); }); });
  return out.sort((a, b) => String(b.tanggal + ' ' + (b.jam || '')).localeCompare(String(a.tanggal + ' ' + (a.jam || ''))));
}
/** Hasil cocok terakhir sebelum tanggal T (untuk "bawaan dari cocok sebelumnya"). */
export const crHasilSebelum = (T) => crSemuaHasil().find((h) => h.tanggal < T) || null;
/**
 * Hitung cocok saldo pada tanggal T. D = { tanggal, saldoBank (teks), tambahan: [{ ket, n (teks; minus = keluar), jenis }] }. Persamaan:
 *   selisih (bank − buku) = bawaan (sisa cocok sebelumnya) + Σ baris mutasi yang tidak ada di buku (masuk +, keluar −) − Σ baris buku yang BELUM ada di mutasi
 * → sisa = selisih − bawaan − Σ tambahan + Σ belum dicek = yang belum terjelaskan. Baris buku = (tanggal cocok sebelumnya, T]; cocok pertama = sejak awal bulan T.
 */
export function crHitungHasil(D, kini) {
  const T = khIsoSah(D && D.tanggal) ? D.tanggal : hariIniIso(kini || new Date()); const P = khPosisi(T);
  if (ugKosong(D && D.saldoBank)) return { tolak: 'Ketik saldo ' + CR_NAMA.toLowerCase() + ' menurut bank pada ' + tanggalPendek(T), T };
  const vb = crAngka(D.saldoBank, ''); if (!vb) return { tolak: 'Saldo bank "' + String(D.saldoBank).slice(0, 20) + '" tidak terbaca sebagai rupiah', T }; const bank = vb.tanda < 0 ? -vb.n : vb.n;
  if (!P.ada) return { tolak: 'Saldo buku rekening pada ' + tanggalPendek(T) + ' belum bisa dihitung — ' + P.sebab, T };
  const prev = crHasilSebelum(T); const dari = prev ? ugTambahHari(prev.tanggal, 1) : T.slice(0, 7) + '-01';
  const baris = crBarisCek(dari, T); const belum = baris.filter((b) => !b.cek); const rpBelum = belum.reduce((a, b) => a + (b.arah === 'masuk' ? b.n : -b.n), 0);
  const tambahan = []; let salah = '';
  (Array.isArray(D.tambahan) ? D.tambahan : []).forEach((x, i) => { const ket = String((x && x.ket) || '').trim(); const v = x && !ugKosong(x.n) ? crAngka(x.n, '') : null; if (!ket && !v) return; if (!v || !(v.n > 0)) { salah = salah || 'Penjelasan ke-' + (i + 1) + ': nominalnya belum terbaca'; return; }
    tambahan.push({ ket: ket.slice(0, 60) || '(tanpa keterangan)', n: v.tanda < 0 || (x && x.arah === 'keluar') ? -v.n : v.n, jenis: String((x && x.jenis) || '').slice(0, 40), tanggal: khIsoSah(x && x.tanggal) ? x.tanggal : '' }); });
  if (salah) return { tolak: salah, T };
  const rpTambah = tambahan.reduce((a, x) => a + x.n, 0); const buku = Math.round(P.rekening * 100) / 100; const selisih = Math.round((bank - buku) * 100) / 100; const bawaan = prev ? Number(prev.sisa) || 0 : 0;
  const sisa = Math.round((selisih - bawaan - rpTambah + rpBelum) * 100) / 100;
  const perJenis = {}; tambahan.forEach((x) => { const j = x.jenis || 'tanpa jenis'; perJenis[j] = (perJenis[j] || 0) + x.n; });
  return { tolak: '', T, bank, buku, selisih, bawaan, prev, dari, baris, nBaris: baris.length, nCek: baris.length - belum.length, belum, rpBelum, tambahan, rpTambah, perJenis, sisa, pas: Math.abs(selisih) < 0.5, terjelaskan: Math.abs(sisa) < 0.5, sumberBuku: P.sumber };
}
/** Simpan hasil cocok ke dokumen bulan T (hasil sebelumnya di bulan yang sama turun ke riwayatHasil, paling banyak 5). Titik kas TIDAK disentuh. */
export function crSusunHasil(D, w, kini) {
  const H = crHitungHasil(D, kini); if (H.tolak) return { tolak: H.tolak };
  const b = H.T.slice(0, 7); const lama = crDokBulan(b) || {}; const ringkas = (x) => ({ kunci: x.kunci, t: x.t, ket: String(x.ket || '').slice(0, 60), n: x.n, arah: x.arah });
  const hasil = { tanggal: H.T, jam: w.jam, dicatat: w.tanggal, saldoBank: H.bank, saldoBuku: H.buku, selisih: H.selisih, bawaan: H.bawaan, dari: H.dari, nBaris: H.nBaris, nCek: H.nCek,
    belum: H.belum.slice(0, 60).map(ringkas), nBelum: H.belum.length, rpBelum: H.rpBelum, tambahan: H.tambahan.slice(0, 80), rpTambah: H.rpTambah, sisa: H.sisa, sumber: D && D.sumber === 'berkas' ? 'berkas' : 'ketik', berkas: D && D.berkas ? String(D.berkas).slice(0, 60) : '' };
  const riwayatHasil = (lama.hasil ? [lama.hasil] : []).concat(Array.isArray(lama.riwayatHasil) ? lama.riwayatHasil : []).slice(0, 5);
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: CR_DOK(b), bulan: b, tanggal: w.tanggal, jam: w.jam, hasil, riwayatHasil }) }], H,
    patch: { crDraf: null, kabar: 'Hasil cocok ' + CR_NAMA.toLowerCase() + ' ' + tanggalPendek(H.T) + ' disimpan — bank ' + RP(H.bank) + ' · buku ' + RP(H.buku) + ' · ' + (H.pas ? 'PAS' : 'selisih ' + (H.selisih < 0 ? '−' : '') + RP(Math.abs(H.selisih))) + (H.pas ? '' : H.terjelaskan ? ' · terjelaskan semua' : ' · belum terjelaskan ' + (H.sisa < 0 ? '−' : '') + RP(Math.abs(H.sisa))) + '. Patokan kas tidak diubah.', kabarAwas: !H.pas && !H.terjelaskan } };
}
/** Ringkasan untuk Dasbor & hero Uang: cocok terakhir, baris yang belum dicek sejak awal bulan lalu, buku rekening sekarang. */
export function crRingkas(kini) {
  const iso = hariIniIso(kini || new Date()); const awal = ugTambahHari(iso.slice(0, 7) + '-01', -1).slice(0, 7) + '-01'; const B = crBarisCek(awal, iso); const belum = B.filter((b) => !b.cek);
  const akhir = crSemuaHasil()[0] || null; const S = saldoKantong();
  return { iso, dari: awal, nBaris: B.length, nBelum: belum.length, rpBelumMasuk: belum.filter((b) => b.arah === 'masuk').reduce((a, b) => a + b.n, 0), rpBelumKeluar: belum.filter((b) => b.arah === 'keluar').reduce((a, b) => a + b.n, 0),
    akhir, bukuSekarang: S.ada ? S.rekening : null,
    teks: (akhir ? 'Terakhir dicocokkan ' + tanggalPendek(akhir.tanggal) + ' · ' + (Math.abs(akhir.selisih) < 0.5 ? 'pas' : 'selisih ' + (akhir.selisih < 0 ? '−' : '') + RP(Math.abs(akhir.selisih))) : 'Rekening belum pernah dicocokkan')
      + ' · ' + (belum.length ? belum.length + ' transaksi belum dicek sejak ' + tanggalPendek(awal) : 'semua transaksi sejak ' + tanggalPendek(awal) + ' sudah dicek') };
}

// ==================== PENGINGAT (diteruskan app.js lewat lokal.uang, seperti pajak; owner saja) ====================
/** Sumber pengingat uang: setor ke bank (brankas lewat batas) & cocok saldo rekening akhir bulan (bulan lalu yang belum dicocokkan + bulan ini). */
export function khSumberPengingat(kini) {
  const iso = hariIniIso(kini || new Date()); const out = [];
  const St = ugSetor(); if (St.nyala && St.ada && St.lewat) out.push({ id: 'setor|' + iso, jenis: 'setor', kunci: 'brankas', teks: 'Setor ke bank — brankas lewat batas', siapa: 'brankas', jatuh: iso, n: St.n, ket: St.teks + ' · Uang › Pindah uang › Setor ke bank' });
  if (!ambilTitikKas()) return out;   // rekening belum pernah dihitung — belum ada yang dicocokkan
  const bulanIni = iso.slice(0, 7); const lalu = ugTambahHari(bulanIni + '-01', -1); const H = crSemuaHasil(); const sudah = (b) => H.some((h) => String(h.tanggal).slice(0, 7) === b);
  const akhirBulan = (b) => { const d = new Date(Date.UTC(Number(b.slice(0, 4)), Number(b.slice(5, 7)), 0)); return d.toISOString().slice(0, 10); };
  if (!sudah(lalu.slice(0, 7))) out.push({ id: 'rekening|' + lalu.slice(0, 7), jenis: 'rekening', kunci: lalu.slice(0, 7), teks: 'Cocokkan saldo ' + CR_NAMA.toLowerCase() + ' akhir ' + lalu.slice(5, 7) + '/' + lalu.slice(0, 4), siapa: 'rekening', jatuh: lalu, n: 0, ket: 'ketik saldo bank ' + tanggalPendek(lalu) + ' — Uang › Rekening' });
  if (!sudah(bulanIni)) out.push({ id: 'rekening|' + bulanIni, jenis: 'rekening', kunci: bulanIni, teks: 'Cocokkan saldo ' + CR_NAMA.toLowerCase() + ' akhir ' + bulanIni.slice(5, 7) + '/' + bulanIni.slice(0, 4), siapa: 'rekening', jatuh: akhirBulan(bulanIni), n: 0, ket: 'ketik saldo bank akhir bulan — Uang › Rekening' });
  return out;
}
