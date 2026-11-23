// FAKTUR BERTEMPO & BATAS KREDIT — putaran B2 (keputusan owner 17 Nov 2026). Logika TANPA DOM, nama berawalan fk (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_faktur.py (jsc + kontrol).
//
// Keputusan owner 17 Nov 2026:
//  - FAKTUR = nota BON pelanggan usaha (pelanggan yang punya tingkat harga B1), OTOMATIS saat dicatat — termasuk bayar kurang yang sisanya jadi bon.
//    Nota lain (tunai juga) bisa DIJADIKAN faktur oleh owner dari lembar Struk kalau pembelinya minta.
//  - TEMPO bawaan diatur owner sendiri dari layar (Pelanggan › Atur); tempo di kartu pelanggan menang atas bawaan. Jatuh tempo = tanggal nota + tempo.
//  - BATAS KREDIT = angka owner di kartu pelanggan; kosong = rumus lama KR1 (2 × rata-rata belanja bulanan 90 hari). Lewat batas → MINTA PERSETUJUAN
//    OWNER (koleksi persetujuan, tindakan 'kredit'), bukan ditolak mati. Bayar kurang (sisanya jadi bon) IKUT batas yang sama.
//  - PELUNASAN: faktur tertua dulu (sama dengan buku bon), atau faktur tertentu dipilih saat bayar (piutangMutasi.untukFaktur).
//  - FAKTUR PAJAK disiapkan walau belum terpakai: hanya berlaku kalau profil pajak = PKP. Faktur pajaknya sendiri dibuat di Coretax DJP — di sini
//    hanya datanya (NPWP pembeli, DPP) dan rekapnya, berlabel "perkiraan — bukan nasihat pajak".
// Nomor faktur aman TANPA INTERNET: F + 2 angka tahun + kode perangkat (3 tanda dari id perangkat) + urut 4 angka per perangkat per tahun — F26-K7Q-0001.
// Dua perangkat tidak memakai awalan yang sama; satu perangkat membaca tulisannya sendiri (termasuk yang masih antre) jadi urutnya tidak berulang.
// MESIN UANG TIDAK DISENTUH: faktur hanyalah KOLOM di baris penjualan (noFaktur, jatuhTempo, tempoHari) dan di pembayaran (untukFaktur); sisa bon tetap
// dari mesin beku hitungPiutang — pembagian ke faktur cuma membagi sisa yang sama.
import { cacheMentah, ambilPenjualanSemua, ambilPelangganCatatan, ambilPiutangMutasi, kreditLintas, tolakKunci, ingatPerVersi, ambilPesanan } from '../data/toko.js';
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, infoKreditPelanggan, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { htTingkatOrang } from './harga-tingkat-logika.js';

export const FK_TINDAKAN = 'kredit';
export const FK_TEMPO_BAWAAN = 14;          // bawaan sampai owner mengaturnya (sama dengan "waktunya ditagih" bawaan Pelanggan)
export const FK_TEMPO_MAKS = 365;
export const FK_BATAS_MAKS = 10000000000;   // Rp10 miliar — penjaga salah ketik, bukan kebijakan
export const FK_DEKAT_HARI = 3;             // pengingat Dasbor: jatuh tempo dalam 3 hari
export const FK_KOLOM_NOTA = ['noFaktur', 'jatuhTempo', 'tempoHari'];
export const FK_LABEL = { lunas: 'lunas', belum: 'belum jatuh tempo', dekat: 'segera jatuh tempo', hariIni: 'jatuh tempo hari ini', lewat: 'lewat jatuh tempo', batal: 'dibatalkan', tunai: 'dibayar' };

// ---------- tempo ----------
const fkAturMentah = () => cacheMentah('aturan').find((d) => String(d.id) === 'pelanggan') || null;
/** Hari tempo yang sah (bilangan bulat 0–365); kosong / salah = null. */
export function fkHariSah(v) { if (v === undefined || v === null || String(v).trim() === '') return null; const n = Number(String(v).trim()); return Number.isInteger(n) && n >= 0 && n <= FK_TEMPO_MAKS ? n : null; }
/** Tempo bawaan toko (aturanToko/pelanggan.tempoBawaan), belum diatur = 14 hari. */
export function fkTempoBawaan() { const a = fkAturMentah(); const n = a ? fkHariSah(a.tempoBawaan) : null; return n === null ? FK_TEMPO_BAWAAN : n; }
// ---------- STOP BON (owner 24 Nov 2026, keputusan 9 Okt): bon tertua belum lunas > N hari → bon baru ditahan ----------
// N = aturanToko/pelanggan.stopBonHari, diatur owner di Pelanggan › Atur; belum diatur = 30; 0 = stop bon mati. Penahannya lewat gerbang kredit yang SAMA
// dengan batas kredit B2 (kunciKr1 di jual-logika.js): karyawan minta persetujuan owner, owner di HP/Mac membuka sekali (dua ketukan).
export const FK_STOP_BAWAAN = 30;
/** Hari stop bon yang berlaku (0 = mati). */
export function fkStopBonHari() { const a = fkAturMentah(); const n = a ? fkHariSah(a.stopBonHari) : null; return n === null ? FK_STOP_BAWAAN : n; }
/** Stop bon kena untuk `nama`? → { hari (N), umur, tanggal (bon tertua belum lunas), sisa } | null. Umur = mesin piutang (FIFO: bayar menutup bon tertua dulu). */
export function fkStopBon(nama) {
  const N = fkStopBonHari(); if (!(N > 0) || !String(nama || '').trim()) return null;
  const r = hitungPiutang().find((x) => x.kunci === kunciPelanggan(nama)); const tgl = r ? String(r.tanggalTertua || '') : '';
  if (!r || !(Number(r.sisa) > 0.5) || !/^\d{4}-\d\d-\d\d$/.test(tgl)) return null;
  // umur dihitung dari hari ini perangkat (Date.now — sama dengan jam Jual), bukan umurHari mesin (jam lain): tanggalTertua = bon tertua yang belum tertutup FIFO
  const umur = Math.round((Date.parse(hariIniIso(new Date(Date.now())) + 'T00:00:00Z') - Date.parse(tgl + 'T00:00:00Z')) / 86400000);
  if (!(umur > N)) return null;
  return { hari: N, umur, tanggal: tgl, sisa: Math.round(Number(r.sisa) || 0) };
}
export const fkStopBonTeks = (nama, S) => 'Stop bon: bon tertua ' + nama + ' belum lunas sejak ' + tanggalPendek(S.tanggal) + ' (' + S.umur + ' hari, batas ' + S.hari + ' hari; sisa bon ' + RP(S.sisa) + ')';
/** Kartu pelanggan mentah (pelangganCatatan) menurut kunci nama. */
export function fkKartu(nama) { const k = kunciPelanggan(nama); if (!k) return null; return (ambilPelangganCatatan() || []).find((c) => kunciPelanggan(c.nama || c.id) === k) || null; }
/** Tempo yang berlaku untuk seorang pelanggan: kartunya → bawaan toko. */
export function fkTempo(nama) { const c = fkKartu(nama); const n = c ? fkHariSah(c.tempoHari) : null; return n === null ? { hari: fkTempoBawaan(), sumber: 'bawaan' } : { hari: n, sumber: 'kartu' }; }
export const fkTempoTeks = (T) => (T.hari === 0 ? 'hari itu juga' : T.hari + ' hari') + (T.sumber === 'kartu' ? ' · dari kartu pelanggan' : ' · bawaan toko');

// ---------- batas kredit ----------
/** Rupiah batas yang sah: > 0 dan ≤ Rp10 miliar; kosong / salah = null. */
export function fkRupiahSah(v) { if (v === undefined || v === null || String(v).trim() === '') return null; const n = Number(String(v).trim()); return isFinite(n) && n > 0 && n <= FK_BATAS_MAKS ? Math.round(n) : null; }
/** Batas kredit yang diisi owner di kartu; null = belum diisi (rumus lama yang berlaku). */
export function fkBatasOwner(nama) { const c = fkKartu(nama); return c ? fkRupiahSah(c.batasKredit) : null; }
/**
 * KR1 + batas owner (keputusan 17 Nov): { ada, terdaftar, sisa, batas, rataBulanan, sumber 'owner' | 'rumus' }. Batas kosong = rumus lama (mesin beku
 * infoKreditPelanggan, lintas tahun lewat kreditLintas). Angka owner di kartu = owner sudah mengenal orangnya → dianggap terdaftar.
 */
export function fkInfoKredit(nama) {
  const info = kreditLintas(infoKreditPelanggan(nama), nama); if (!info || !info.ada) return info;
  const B = fkBatasOwner(nama);
  return B === null ? Object.assign({}, info, { sumber: 'rumus' }) : Object.assign({}, info, { batas: B, sumber: 'owner', terdaftar: true });
}
export const fkSumberBatas = (i) => (i && i.sumber === 'owner' ? 'angka owner' : '2× rata belanja bulanan');
/** Pelanggan usaha = punya tingkat harga (B1, aturanToko/hargaTingkat.orang). */
export function fkUsaha(nama) { return !!htTingkatOrang(nama); }

// ---------- nomor faktur ----------
let fkIdPerangkat = '';
/** app.js memasang id perangkat (firebase idPerangkat) sekali — logika tetap tanpa Firestore. */
export function fkPasangPerangkat(id) { fkIdPerangkat = String(id || ''); }
// abjad kode perangkat TANPA tanda yang mirip satu sama lain di kertas (0/O, 1/I/L) — nomor faktur dibaca & diketik orang
export const FK_ABJAD = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
/** Kode 3 tanda dari id perangkat (abjad FK_ABJAD) — tetap untuk perangkat yang sama. Tanpa id (uji) = "XXX". */
export function fkKodePerangkat(id) {
  const s = String(id === undefined ? fkIdPerangkat : id || ''); if (!s) return 'XXX';
  let h = 5381; for (let i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) >>> 0;
  let k = ''; for (let i = 0; i < 3; i++) { k += FK_ABJAD[h % FK_ABJAD.length]; h = Math.floor(h / FK_ABJAD.length); }
  return k;
}
export function fkAwalan(tanggal, kode) { return 'F' + String(tanggal || '').slice(2, 4) + '-' + (kode || fkKodePerangkat()) + '-'; }
/** Nomor berikutnya untuk perangkat ini di tahun tanggal itu: urut terbesar yang sudah tertulis (termasuk nota batal) + 1 — nomor tidak pernah dipakai ulang. */
export function fkNomorBaru(tanggal, kode) {
  const aw = fkAwalan(tanggal, kode); let maks = 0;
  (ambilPenjualanSemua() || []).forEach((p) => { const n = String(p.noFaktur || ''); if (n.indexOf(aw) === 0) { const u = Number(n.slice(aw.length)); if (Number.isInteger(u) && u > maks) maks = u; } });
  return aw + ('0000' + (maks + 1)).slice(-Math.max(4, String(maks + 1).length));
}
export function fkTambahHari(iso, n) { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + (Number(n) || 0)); return d.toISOString().slice(0, 10); }
const fkHariKe = (iso) => Math.round(Date.parse(String(iso) + 'T00:00:00Z') / 86400000);
/**
 * Kolom faktur untuk nota yang AKAN dicatat (dipanggil susunNotaDokumen). Hanya nota yang caraBayar akhirnya Kredit (bon, atau bayar kurang) DAN
 * pembelinya pelanggan usaha. null = bukan faktur.
 */
export function fkKolomNota(nama, cara, tanggal, kode) {
  if (cara !== 'Kredit' || !String(nama || '').trim() || !fkUsaha(nama)) return null;
  const T = fkTempo(nama);
  return { noFaktur: fkNomorBaru(tanggal, kode), jatuhTempo: fkTambahHari(tanggal, T.hari), tempoHari: T.hari };
}

// ---------- alokasi pembayaran ke faktur ----------
const fkKunciNota = (p) => String(p.trxId || p.grupNota || p.id);
/** Peta bantu, diingat per versi data (dipakai bersama — jangan diubah di tempat): baris penjualan → noFaktur, nota → noFaktur, pembayaran → dokumennya. */
export function fkPeta() { return ingatPerVersi('fkPeta', fkPetaHitung); }   // B5: laba-pelanggan-logika (tempo) memakai peta yang sama
function fkPetaHitung() {
  const baris = {}, nota = {}, bayar = {}, trx = {}, ps = {};
  // B4 (owner 18 Nov 2026): baris → 'trx:<kunci nota>' (pembayaran ber-untukPesanan menutup baris nota pesanannya, bernomor faktur atau tidak)
  (ambilPenjualanSemua() || []).forEach((p) => { trx[String(p.id)] = 'trx:' + fkKunciNota(p); if (p.noFaktur) { baris[String(p.id)] = String(p.noFaktur); nota[fkKunciNota(p)] = String(p.noFaktur); } });
  (ambilPiutangMutasi() || []).forEach((m) => { if (m && m.tipe === 'bayar') bayar[String(m.id)] = m; });
  (ambilPesanan() || []).forEach((x) => { if (x && x.trxIdJual) ps[String(x.id)] = String(x.trxIdJual); });
  return { baris, nota, bayar, trx, ps };
}
/** Faktur yang DITUJU satu pembayaran: untukFaktur (dipilih saat bayar) → atau pembayaran saat beli sebuah faktur (notaTrxId nota bernomor). [] = tertua dulu. */
export function fkTujuanBayar(m, P) {
  if (!m) return [];
  if (Array.isArray(m.untukFaktur) && m.untukFaktur.length) return m.untukFaktur.map(String).filter(Boolean);
  // B4: uang muka pesanan (dan pelunasan saat nota pesanan ber-DP) → baris nota pesanan itu begitu notanya ada; sebelum itu tertua dulu (= mesin)
  if (m.untukPesanan !== undefined && m.untukPesanan !== null && String(m.untukPesanan) !== '') { const Q = P || fkPeta(); const t = Q.ps[String(m.untukPesanan)]; return t ? ['trx:' + t] : []; }
  const t = m.notaTrxId !== undefined && m.notaTrxId !== null ? (P || fkPeta()).nota[String(m.notaTrxId)] : null; return t ? [t] : [];
}
/**
 * Utang per baris satu orang (rekaman mesin hitungPiutang) dengan pembayaran BERALAMAT lebih dulu: tiap pembayaran yang menuju faktur tertentu menutup
 * baris faktur itu (sisanya, kalau berlebih, ikut ke yang lain); semua yang tersisa — pembayaran lain, hapus buku, retur — menutup TERTUA dulu PERSIS
 * rincianBelumLunas lama (bon-logika). Tanpa pembayaran beralamat hasilnya sama dengan rincianBelumLunas lama huruf demi huruf; jumlah sisa = sisa mesin.
 * → [{ u, sisa, buka }] urut tanggal (buka = baris yang dulu ikut daftar "belum lunas").
 */
export function fkAlokasi(d, P0) {
  const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
  let tertutup = d.bayar + d.dihapus + (d.retur || 0) - utang.reduce((a, u) => a + (u.diretur || 0), 0);
  const nom = utang.map((u) => u.nominal - (u.diretur || 0)); const kurang = utang.map(() => 0);
  const bayarBeralamat = d.mutasi.filter((m) => m.jenis === 'bayar' && m.idMutasi !== undefined);
  let P = null;
  if (bayarBeralamat.length) {
    P = P0 || fkPeta();
    bayarBeralamat.forEach((m) => {
      const tuju = fkTujuanBayar(P.bayar[String(m.idMutasi)], P); if (!tuju.length) return;
      let n = Math.min(Number(m.nominal) || 0, Math.max(0, tertutup));
      utang.forEach((u, i) => { if (n <= 0 || (tuju.indexOf(P.baris[String(u.idTrx)]) < 0 && tuju.indexOf(P.trx[String(u.idTrx)]) < 0)) return; const ambil = Math.min(Math.max(0, nom[i] - kurang[i]), n); kurang[i] += ambil; n -= ambil; tertutup -= ambil; });
    });
  }
  return utang.map((u, i) => {
    const sisaNom = nom[i] - kurang[i];
    if (kurang[i] > 0 && sisaNom <= 0) return { u, sisa: 0, buka: false };
    if (tertutup >= sisaNom) { tertutup -= sisaNom; return { u, sisa: 0, buka: false }; }
    const s = sisaNom - tertutup; tertutup = 0; return { u, sisa: s, buka: true };
  });
}
/** Rincian yang belum tertutup — bentuk rincianBelumLunas (bon-logika memakainya). */
export function fkRincian(d, P) {
  return fkAlokasi(d, P).filter((x) => x.buka).map((x) => ({ tanggal: x.u.tanggal, ket: x.u.ket, nominal: x.u.nominal, sisa: x.sisa, idTrx: x.u.idTrx || null, idMutasi: x.u.idMutasi || null }));
}
/** Ada pembayaran beralamat untuk orang ini (umur bon lalu dibaca dari rincian, bukan dari FIFO murni mesin). */
export function fkAdaAlamat(d, P0) { const P = P0 || fkPeta(); return d.mutasi.some((m) => m.jenis === 'bayar' && fkTujuanBayar(P.bayar[String(m.idMutasi)], P).length > 0); }

// ---------- daftar faktur ----------
function fkStatus(sisa, jt, iso, berlaku, kredit) {
  if (!berlaku) return 'batal';
  if (!kredit) return 'tunai';
  if (sisa <= 0.5) return 'lunas';
  const h = fkHariKe(jt) - fkHariKe(iso);
  return h < 0 ? 'lewat' : h === 0 ? 'hariIni' : h <= FK_DEKAT_HARI ? 'dekat' : 'belum';
}
/**
 * Semua faktur (satu per nota bernomor), terbaru dulu: { no, trxId, nama, kunci, tanggal, jam, jatuhTempo, tempoHari, total, sisa, dibayar, kredit, status,
 * label, hariLewat, berlaku, baris }. Sisa nota bon = bagian sisa mesin yang jatuh ke baris-baris nota itu (fkAlokasi); nota tunai yang dijadikan faktur = 0.
 */
export function fkSemua(kini) {
  const iso = hariIniIso(kini || new Date()); const grup = {};
  (ambilPenjualanSemua() || []).forEach((p) => { if (!p.noFaktur) return; const k = fkKunciNota(p); (grup[k] = grup[k] || []).push(p); });
  const kunciAda = Object.keys(grup); if (!kunciAda.length) return [];
  const P = fkPeta(); const sisaBaris = {}; const orang = {};
  kunciAda.forEach((k) => { grup[k].forEach((p) => { if (p.caraBayar === 'Kredit') orang[kunciPelanggan(p.namaPelanggan)] = true; }); });
  hitungPiutang().forEach((d) => { if (!orang[d.kunci]) return; fkAlokasi(d, P).forEach((x) => { if (x.u.jenis === 'jual') sisaBaris[String(x.u.idTrx)] = x.sisa; }); });
  return kunciAda.map((k) => {
    const rows = grup[k].slice().sort((a, b) => (a.id > b.id ? 1 : a.id < b.id ? -1 : 0)); const p = rows[0];
    const berlaku = rows.every(penjualanMasihBerlaku); const kredit = rows.some((x) => x.caraBayar === 'Kredit');
    const total = rows.reduce((a, x) => a + (x.hargaTotal || 0), 0);
    const sisa = berlaku && kredit ? Math.round(rows.reduce((a, x) => a + (sisaBaris[String(x.id)] || 0), 0)) : 0;
    const jt = String(p.jatuhTempo || p.tanggal || ''); const status = fkStatus(sisa, jt, iso, berlaku, kredit);
    return { no: String(p.noFaktur), trxId: k, nama: String(p.namaPelanggan || '').trim(), kunci: kunciPelanggan(p.namaPelanggan), tanggal: p.tanggal || '', jam: p.jam || '',
      jatuhTempo: jt, tempoHari: Number(p.tempoHari) || 0, total, sisa, dibayar: Math.max(0, total - sisa), kredit, status, label: FK_LABEL[status],
      hariLewat: status === 'lewat' ? fkHariKe(iso) - fkHariKe(jt) : 0, berlaku, baris: rows };
  }).sort((a, b) => String(b.tanggal + b.jam + b.no).localeCompare(String(a.tanggal + a.jam + a.no)));
}
/** Faktur satu orang yang masih terbuka (sisa > 0), TERTUA dulu — pilihan di lembar bayar bon. */
export function fkTerbukaOrang(kini, kunci) { return fkSemua(kini).filter((f) => f.kunci === kunci && f.sisa > 0.5).sort((a, b) => String(a.tanggal + a.jam + a.no).localeCompare(String(b.tanggal + b.jam + b.no))); }
/** Faktur satu nota (trxId / grupNota / id) — dipakai struk. */
export function fkNota(kunciNota, kini) { return fkSemua(kini).find((f) => f.trxId === String(kunciNota)) || null; }
/** Pengingat Dasbor: lewat jatuh tempo + jatuh tempo hari ini + dalam 3 hari, paling mendesak dulu. */
export function fkPengingat(kini) {
  const urut = { lewat: 0, hariIni: 1, dekat: 2 };
  const L = fkSemua(kini).filter((f) => urut[f.status] !== undefined).sort((a, b) => urut[a.status] - urut[b.status] || String(a.jatuhTempo).localeCompare(String(b.jatuhTempo)));
  return { daftar: L, lewat: L.filter((f) => f.status === 'lewat').reduce((a, f) => a + f.sisa, 0), segera: L.filter((f) => f.status !== 'lewat').reduce((a, f) => a + f.sisa, 0),
    kalimat: L.length ? L.length + ' faktur perlu ditagih · lewat ' + RP(L.filter((f) => f.status === 'lewat').reduce((a, f) => a + f.sisa, 0)) : '' };
}
export function fkTeksTempo(f) {
  if (!f) return '';
  return f.status === 'lewat' ? 'lewat ' + f.hariLewat + ' hari (jatuh tempo ' + tanggalPendek(f.jatuhTempo) + ')' : f.status === 'hariIni' ? 'jatuh tempo HARI INI'
    : f.status === 'lunas' || f.status === 'tunai' ? FK_LABEL[f.status] : 'jatuh tempo ' + tanggalPendek(f.jatuhTempo);
}

// ---------- jadikan faktur (owner, dari lembar Struk) ----------
/**
 * Nota yang sudah tersimpan dijadikan faktur: semua barisnya diberi noFaktur + jatuhTempo (tanggal nota + tempo pelanggan) + tempoHari. Hanya owner (rules:
 * mengubah penjualan = owner). Ditolak: nota batal / dikoreksi, sudah faktur, tanpa nama pembeli, bulan terkunci.
 */
export function fkSusunJadikan(nota, w, kode) {
  if (!nota || !nota.baris || !nota.baris.length) return { tolak: 'Nota ini tidak ditemukan di data perangkat ini' };
  if (nota.baris.some((p) => p.noFaktur)) return { tolak: 'Nota ini sudah faktur ' + (nota.baris.find((p) => p.noFaktur) || {}).noFaktur };
  if (!nota.baris.every(penjualanMasihBerlaku)) return { tolak: 'Nota yang sudah dibatalkan / dikoreksi tidak bisa dijadikan faktur' };
  if (!String(nota.nama || '').trim()) return { tolak: 'Faktur butuh nama pembeli — nota ini tanpa nama' };
  const kunci = nota.baris.map((p) => tolakKunci('penjualan', p, 'faktur untuk nota bulan itu tidak bisa dibuat lagi')).find(Boolean); if (kunci) return { tolak: kunci };
  const tgl = String(nota.tanggal || nota.baris[0].tanggal || ''); const T = fkTempo(nota.nama);
  const no = fkNomorBaru((w && w.tanggal) || tgl, kode); const jt = fkTambahHari(tgl, T.hari); const kini = (w && w.kini) || new Date().toISOString();
  const dokumen = nota.baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { noFaktur: no, jatuhTempo: jt, tempoHari: T.hari, fakturDibuatPada: kini }) }));
  return { dokumen, no, patch: { kabar: 'Jadi faktur ' + no + ' · jatuh tempo ' + tanggalPendek(jt) + ' · tempo ' + fkTempoTeks(T), kabarAwas: false } };
}

// ---------- minta persetujuan owner saat batas kredit terlewati ----------
/** Kalimat permintaan, dihitung ULANG dari buku sekarang (papan owner tidak memakai teks kiriman). */
export function fkTeksMinta(m) {
  const nama = String((m && m.pelanggan) || ''); const n = Math.round(Number(m && m.nominal) || 0); const i = nama ? fkInfoKredit(nama) : null;
  if (!nama || !(n > 0)) return 'permintaan bon — bentuknya tidak lengkap (tanpa nama / nominal)';
  return 'Bon ' + nama + ': lama ' + RP(i ? i.sisa : 0) + ' + nota ini ' + RP(n) + ' = ' + RP((i ? i.sisa : 0) + n) + ' · batas ' + RP(i ? i.batas : 0) + ' (' + fkSumberBatas(i) + ')'
    + (m && m.sisaJadiBon ? ' · sisa bayar kurang' : '') + (m && m.alasan ? ' · alasan: ' + String(m.alasan).slice(0, 80) : '')
    + ((S) => (S ? ' · ' + fkStopBonTeks(nama, S) : ''))(fkStopBon(nama));
}
/** Dokumen persetujuan 'kredit' menunggu (rules v9 stafMintaKredit: status menunggu, mintaUid = olehUid = penulis, tanpa kolom keputusan). */
export function fkSusunMinta(akun, nama, nominal, w, opsi) {
  const nm = String(nama || '').trim(); const n = Math.round(Number(nominal) || 0); const o = opsi || {};
  if (!nm) return { tolak: 'Pilih nama pembelinya dulu' };
  if (!(n > 0)) return { tolak: 'Nominal bon nota ini nol' };
  if (fkMenungguSaya(akun, nm, n)) return { tolak: 'Permintaan untuk ' + nm + ' ' + RP(n) + ' sudah dikirim — tunggu owner' };
  const uid = akun && akun.uid ? String(akun.uid) : '';
  const data = { id: w.idUnik(), tindakan: FK_TINDAKAN, status: 'menunggu', mintaUid: uid, pelanggan: nm, nominal: n, sisaJadiBon: !!o.sisaJadiBon, alasan: String(o.alasan || '').trim().slice(0, 80),
    dari: (akun && akun.nama) || '', peran: (akun && akun.peran) || '', tanggal: w.tanggal, jam: w.jam, pada: w.kini };
  data.teks = fkTeksMinta(data);
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Permintaan bon dikirim ke owner — ' + nm + ' ' + RP(n) + '. Nota bisa dicatat begitu owner menyetujui.', kabarAwas: false } };
}
const fkMilik = (m, akun) => !akun || akun.jenis === 'owner' || !m.mintaUid || String(m.mintaUid) === String(akun.uid || '');
/** Permintaan yang sama (orang, nominal, akun) masih menunggu. */
export function fkMenungguSaya(akun, nama, nominal) {
  const k = kunciPelanggan(nama); const n = Math.round(Number(nominal) || 0);
  return cacheMentah('persetujuan').find((m) => m && m.tindakan === FK_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && kunciPelanggan(m.pelanggan) === k && Math.round(Number(m.nominal) || 0) === n && fkMilik(m, akun)) || null;
}
/** Persetujuan owner yang masih bisa dipakai untuk nota ini: tindakan kredit, DISETUJUI HARI INI, orang sama, nominal ≥ bon nota ini, milik akun ini, belum dipakai nota mana pun. */
export function fkSetujuUntuk(akun, nama, nominal, tanggal) {
  const k = kunciPelanggan(nama); const n = Math.round(Number(nominal) || 0); if (!k || !(n > 0)) return null;
  const dipakai = {}; (ambilPenjualanSemua() || []).forEach((p) => { if (p.kreditSetujuId !== undefined && p.kreditSetujuId !== null) dipakai[String(p.kreditSetujuId)] = true; });
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === FK_TINDAKAN && m.status === 'disetujui' && String(m.diputusTanggal || '') === String(tanggal) && kunciPelanggan(m.pelanggan) === k
    && Math.round(Number(m.nominal) || 0) >= n && fkMilik(m, akun) && !dipakai[String(m.id)]).sort((a, b) => (Number(a.nominal) || 0) - (Number(b.nominal) || 0))[0] || null;
}
/** Permintaan kredit terakhir akun ini untuk orang itu (pita di lembar bayar: menunggu / ditolak beserta alasannya). */
export function fkMintaTerakhir(akun, nama) {
  const k = kunciPelanggan(nama); if (!k) return null;
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === FK_TINDAKAN && kunciPelanggan(m.pelanggan) === k && fkMilik(m, akun))
    .sort((a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || '')))[0] || null;
}

// ---------- faktur pajak (disiapkan, belum terpakai) ----------
const fkRekapPajak = () => cacheMentah('aturan').find((d) => String(d.id) === 'rekapOmzet') || null;
/** Faktur pajak berlaku hanya kalau profil pajak toko = PKP (Laporan › Pajak › Profil). Dokumen itu hanya terbaca owner. */
export function fkPkp() { const r = fkRekapPajak(); return !!(r && r.statusPkp === 'pkp'); }
/** Status PKP apa adanya: 'pkp' | 'bukan' | 'belumDiketahui' (profil belum diisi). */
export function fkStatusPkp() { const r = fkRekapPajak(); return r && (r.statusPkp === 'pkp' || r.statusPkp === 'bukan') ? r.statusPkp : 'belumDiketahui'; }
export const FK_KALIMAT_PAJAK = 'Faktur pajak dibuat di Coretax DJP — sistem ini hanya menyiapkan datanya. Perkiraan, bukan nasihat pajak: perlakuan PPN beras ditanyakan ke konsultan.';
/**
 * Rekap faktur satu bulan (YYYY-MM) untuk dibawa ke Coretax / konsultan: per faktur berlaku — nomor, tanggal, pembeli, NPWP pembeli (dari kartu; kosong
 * = belum ada), alamat, nilai (DPP = total nota; PPN TIDAK dihitung di sini). Kalau toko bukan PKP, rekap tetap bisa dilihat tapi berlabel tidak diperlukan.
 */
export function fkRekapBulan(bulan, kini) {
  const L = fkSemua(kini).filter((f) => f.berlaku && String(f.tanggal).slice(0, 7) === String(bulan)).sort((a, b) => String(a.tanggal + a.no).localeCompare(String(b.tanggal + b.no)));
  const baris = L.map((f) => { const c = fkKartu(f.nama) || {}; return { no: f.no, tanggal: f.tanggal, nama: f.nama, npwp: String(c.npwp || ''), alamat: String(c.alamat || ''), dpp: f.total }; });
  const csv = ['No faktur;Tanggal;Pembeli;NPWP pembeli;Alamat;Nilai (DPP)'].concat(baris.map((b) => [b.no, b.tanggal, b.nama, b.npwp, b.alamat, b.dpp].map((x) => '"' + String(x).replace(/"/g, '""') + '"').join(';'))).join('\n');
  return { bulan, pkp: fkPkp(), baris, tanpaNpwp: baris.filter((b) => !b.npwp).length, jumlah: baris.reduce((a, b) => a + b.dpp, 0), csv, kalimat: fkPkp() ? FK_KALIMAT_PAJAK : fkStatusPkp() === 'bukan' ? 'Toko bukan PKP — faktur pajak belum diperlukan. Rekap ini disiapkan untuk kalau nanti PKP.'
    : 'Status PKP toko belum diisi (Laporan › Pajak › Profil) — selama itu faktur pajak dianggap belum diperlukan. Rekap ini disiapkan untuk kalau nanti PKP.' };
}
