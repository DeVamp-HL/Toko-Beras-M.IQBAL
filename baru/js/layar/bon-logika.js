// LAYAR PELANGGAN — BON PELANGGAN (PL2, dikunci owner 18 Sep = Buku Bon · Papan Tagih · Garis Umur; tanpa DOM). Dijaga alat-uji/uji_pelanggan_baru.py.
//
// Angka bon dibaca dari MESIN BEKU `hitungPiutang` (sisa, umur FIFO — sama dengan sistem lama); rincian yang belum lunas mengikuti rincianBelumLunas index.html
// 29599 (pembayaran & hapus buku memadamkan bon TERTUA dulu; bon pertama yang tak habis disebut sisanya). Kosakata dikunci: "pembayaran" (bukan pelunasan) —
// LUNAS hanya kalau sisanya benar-benar nol. Dokumen PERSIS sistem lama: pembayaran = piutangMutasi {tipe 'bayar', namaPelanggan, nominal, tanggal, jam,
// caraBayar Tunai|QRIS, catatan, dicatatDi 'sistem'} (simpanBayarPiutang 29667; kolom tambahan: dibawaOleh = pengantar, memori tangan-yang-membayar);
// hapus buku = {tipe 'hapusBuku', namaPelanggan, nominal, alasan, tanggal, jam, dicatatDi} (simpanHapusBuku 29645) — BUKAN uang masuk, kerugian bulan itu,
// permanen → alasan wajib + dua ketukan. Tagihan WhatsApp = kalimat kirimTagihanPiutang 29612 (salamnya setelan owner) + janji bayar DICATAT di koleksi baru
// `tagihPelanggan` supaya besok layar tahu janji siapa yang lewat. Macet = bon tertua lebih tua dari N hari DAN tidak ada pembayaran selama itu (usul saja).
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, formatTanggal } from '../mesin/pembantu.js';
import { cacheMentah, ambilTutupHari, ambilPiutangMutasi, eraBuku } from '../data/toko.js';
import { RP, hariIniIso, LEBIH_AMBANG, kalimatLebih, pecahLebih } from '../inti/format.js';
import { aturPelanggan, kartuTersimpan, hariKe } from './pelanggan-logika.js';

const bnAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const bnKosong = (v) => v === undefined || v === null || String(v).trim() === '';
/** Umur dalam kata — persis umurKeKata index.html 29121 (dipakai di pesan WhatsApp). */
export function umurKata(hari) { if (hari === null || hari === undefined) return 'baru'; if (hari <= 0) return 'hari ini'; if (hari < 60) return hari + ' hari'; if (hari < 365) return Math.round(hari / 30) + ' bulan'; const th = Math.floor(hari / 365), bln = Math.round((hari % 365) / 30); return th + ' tahun' + (bln > 0 ? ' ' + bln + ' bln' : ''); }
/** Rincian bon yang BELUM tertutup (FIFO) — rincianBelumLunas index.html 29599; audit 39b no. 37 (tinjauan MM1): barang yang diretur dari nota bon memadamkan
 *  NOTA ASALNYA dulu (mesin hitungPiutang mencatatnya di utang itu: `diretur`), sisanya ikut bon tertua bersama pembayaran & hapus buku — sama dengan mesin. */
const bnDiretur = (utang) => utang.reduce((a, u) => a + (u.diretur || 0), 0);
export function rincianBelumLunas(d) {
  const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
  let tertutup = d.bayar + d.dihapus + (d.retur || 0) - bnDiretur(utang); const hasil = [];
  for (const u of utang) { const nom = u.nominal - (u.diretur || 0); if (tertutup >= nom) { tertutup -= nom; continue; } hasil.push({ tanggal: u.tanggal, ket: u.ket, nominal: u.nominal, sisa: nom - tertutup, idTrx: u.idTrx || null, idMutasi: u.idMutasi || null }); tertutup = 0; }
  return hasil;
}
export const KATA_STATUS = { macet: 'macet — usul hapus', janjiLewat: 'janjinya lewat', menunggu: 'menunggu janji', perluTagih: 'waktunya ditagih', baru: 'masih baru', lunas: 'lunas', lebih: 'kelebihan bayar' };
export const JANJI_PILIHAN = [[0, 'tanpa janji'], [3, '3 hari lagi'], [7, 'seminggu lagi'], [14, 'dua minggu lagi']];
const capLebih = (p) => (p.uang > 0.5 && p.hapus > 0.5 ? 'kelebihan bayar & hapus buku terbayar' : p.uang > 0.5 ? KATA_STATUS.lebih : 'hapus buku terbayar');
const tambahHari = (iso, n) => new Date((hariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
/** Paket F2: catatan hapus buku BERNILAI MINUS = hapus buku yang dibalik (dibayar sesudah dihapus) — susunBayarSesudahHapus. */
const bnBalik = (m) => m.jenis === 'hapusBuku' && (Number(m.nominal) || 0) < 0;
/** Semua orang di buku bon (mesin beku) + status menurut aturan owner + tagihan terakhir. */
export function semuaBon(kini) {
  const iso = hariIniIso(kini); const atur = aturPelanggan(); const tagihSemua = cacheMentah('tagih');
  return hitungPiutang().map((d, no) => { const buka = rincianBelumLunas(d); const sisa = d.sisa || 0; const umur = sisa > 0 ? d.umurHari : null;
    const bayarAkhir = d.mutasi.filter((m) => m.jenis === 'bayar').sort((a, b) => String(b.tanggal + (b.jam || '')).localeCompare(String(a.tanggal + (a.jam || ''))))[0] || null;
    const tagih = tagihSemua.filter((t) => t.kunci === d.kunci).sort((a, b) => String(b.tanggal + (b.jam || '')).localeCompare(String(a.tanggal + (a.jam || ''))))[0] || null;
    const janjiLewat = !!tagih && !!tagih.janji && tagih.janji < iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal); const menunggu = !!tagih && !!tagih.janji && tagih.janji >= iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal);
    const diamSejak = bayarAkhir ? hariKe(iso) - hariKe(bayarAkhir.tanggal) : umur; const macet = sisa > 0 && umur !== null && umur > atur.macetHari && (diamSejak === null || diamSejak > atur.macetHari);
    const status = sisa < LEBIH_AMBANG ? 'lebih' : sisa <= 0 ? 'lunas' : macet ? 'macet' : janjiLewat ? 'janjiLewat' : menunggu ? 'menunggu' : umur !== null && umur >= atur.tagihHari ? 'perluTagih' : 'baru'; const kartu = kartuTersimpan(d.kunci);
    const ket = status === 'janjiLewat' ? 'janji bayar ' + formatTanggal(tagih.janji) + ' — lewat ' + (hariKe(iso) - hariKe(tagih.janji)) + ' hari' : status === 'menunggu' ? 'janji bayar ' + formatTanggal(tagih.janji) : status === 'macet' ? 'bon tertua ' + umurKata(umur) + ', tidak ada pembayaran selama itu'
      : status === 'perluTagih' ? 'bon tertua ' + umurKata(umur) + (tagih ? ' · terakhir ditagih ' + formatTanggal(tagih.tanggal) : ' · belum pernah ditagih') : status === 'lebih' ? kalimatLebih(pecahLebih(d)) : status === 'lunas' ? 'tidak ada bon yang terbuka' :'bon tertua ' + umurKata(umur);
    return { kunci: d.kunci, nama: d.nama, no, sisa, umur, buka, bayar: d.bayar, dihapus: d.dihapus, retur: d.retur || 0, total: d.total, mutasi: d.mutasi, bayarAkhir, tagih, diamSejak, status, ket, cap: status === 'lebih' ? capLebih(pecahLebih(d)) : KATA_STATUS[status], lebihUang: pecahLebih(d).uang, lebihHapus: pecahLebih(d).hapus, kontak: kartu ? kartu.kontak : '', dikenali: !!(kartu && kartu.dikenali), tanggalJanggal: !!d.tanggalJanggal }; });
}
// ==================== PAKET BRIEF 9 OKT (butir 1): KELOMPOK UMUR DIATUR OWNER + RATA-RATA HARI BON TERTAGIH ====================
/** Kata untuk satu batas hari: kelipatan 365 = tahun, kelipatan 30 = bulan, selain itu hari. */
const kataHariBon = (n) => (n % 365 === 0 ? n / 365 + ' tahun' : n % 30 === 0 ? n / 30 + ' bulan' : n + ' hari');
/** Rentang (lo, hi] dalam kata — "8–30 hari", "1–3 bulan" (dua ujungnya kelipatan 30), "1–2 tahun". */
const rentangHariBon = (lo, hi) => (lo % 365 === 0 && hi % 365 === 0 ? lo / 365 + '–' + hi / 365 + ' tahun' : lo % 30 === 0 && hi % 30 === 0 ? lo / 30 + '–' + hi / 30 + ' bulan' : lo + 1 === hi ? hi + ' hari' : (lo + 1) + '–' + hi + ' hari');
/** Empat kelompok umur dari tiga batas hari (setelan owner aturPelanggan().umurBatas). Bawaan [7, 30, 90] = PERSIS label garis umur yang dikunci owner 18 Sep:
 *  ≤ 7 hari · 8–30 hari · 1–3 bulan · > 3 bulan. Label ikut angka setelan. */
export function kelompokUmur(batas) {
  const [a, b, c] = batas;
  return [{ id: 'e1', label: '≤ ' + kataHariBon(a), dari: 0, sampai: a }, { id: 'e2', label: rentangHariBon(a, b), dari: a + 1, sampai: b },
    { id: 'e3', label: rentangHariBon(b, c), dari: b + 1, sampai: c }, { id: 'e4', label: '> ' + kataHariBon(c), dari: c + 1, sampai: Infinity }];
}
/** Sebaran sisa bon per kelompok umur (umur = bon tertua yang belum tertutup, mesin beku). Bon yang umurnya tidak bisa dihitung (bon tanpa tanggal) jadi
 *  kelompok sendiri "tanpa tanggal" — tidak dibuang diam-diam; Σ jumlah semua kelompok = sisa semuanya. Fungsi sumber tab Garis umur (dan dasbor kelak). */
export function sebaranUmurBon(kini, semua) {
  const berutang = (semua || semuaBon(kini)).filter((b) => b.sisa > 0);
  const kel = kelompokUmur(aturPelanggan().umurBatas).map((e) => Object.assign(e, { cocok: (b) => b.umur !== null && b.umur >= e.dari && b.umur <= e.sampai }));
  if (berutang.some((b) => b.umur === null)) kel.push({ id: 'e0', label: 'tanpa tanggal', dari: null, sampai: null, cocok: (b) => b.umur === null });
  return kel.map((e) => { const isi = berutang.filter(e.cocok); return { id: e.id, label: e.label, dari: e.dari, sampai: e.sampai, n: isi.length, jumlah: isi.reduce((x, b) => x + b.sisa, 0), isi, tua: e.id === 'e4' }; });
}
const tglSahBon = (t) => /^\d{4}-\d{2}-\d{2}$/.test(String(t || ''));
/** Uang yang dibayar DI MEJA saat beli (uang kurang: semua baris nota jadi Kredit + satu pembayaran sebesar uang yang diterima — jual-logika susunNotaDokumen,
 *  index.html sama). Dikenali seperti struk-logika bayarSaatBeli: notaTrxId (sejak 30 Sep) atau catatan ST_CATATAN_BAYAR_BELI (teks yang SAMA, dijaga uji). */
const BN_BAYAR_SAAT_BELI = 'Dibayar langsung saat beli';
const bnSaatBeli = () => new Set(ambilPiutangMutasi().filter((m) => m && m.tipe === 'bayar' && ((m.notaTrxId !== undefined && m.notaTrxId !== null && String(m.notaTrxId) !== '')
  || String(m.catatan || '').indexOf(BN_BAYAR_SAAT_BELI) === 0)).map((m) => String(m.id)));
/**
 * JALAN TUTUP satu buku bon (baris hitungPiutang): bon mana ditutup catatan apa, dan kapan. Bagian yang tertutup per bon = PERSIS mesin hitungPiutang /
 * rincianBelumLunas (retur memadamkan NOTA ASALNYA dulu; pembayaran, hapus buku & sisa retur memadamkan bon TERTUA dulu). Lalu tiap rupiah penutup dipasangkan
 * ke rupiah bon menurut waktu (dua antrean FIFO: rupiah pembayaran paling awal menutup rupiah bon paling tua; retur nota bon ke nota asalnya selama nota itu
 * masih terbuka saat retur, kalau tidak ke bon terbuka tertua — tinjauan no. 9). Hapus buku bernilai minus (Paket F2, dibalik)
 * menetralkan hapus buku SEBELUMNYA, yang terbaru dulu (sama dengan Laporan lpJalanBon). Uang yang datang sebelum bonnya lahir (kelebihan menunggu bon
 * berikutnya) menutup bon itu pada hari bon lahir — 0 hari, tidak pernah minus. `beli` (pilihan) = Set id pembayaran saat beli → potongannya bertanda `beli`.
 * → [{ jenis, tanggal, ket, nominal, saldoAwal, idTrx, idMutasi, sisa, lunas, lunasTanggal, potong: [{ jenis: bayar|hapusBuku|retur|lain, n, tanggal, hari, beli }] }] urut bon mesin
 */
export function jalanTutupBon(d, beli) {
  const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
  const bon = utang.map((u) => ({ u, retur: 0, potong: [] })); const ev = []; let urut = 0;
  const potong = (b, jenis, n, t, diMeja) => { const tb = String(b.u.tanggal || ''); const tg = !tglSahBon(t) ? '' : t > tb ? t : tb;
    b.potong.push({ jenis, n, tanggal: tg, hari: tglSahBon(tb) && tg ? hariKe(tg) - hariKe(tb) : null, beli: !!diMeja }); };
  d.mutasi.forEach((m) => {
    const n = Number(m.nominal) || 0; const t = String(m.tanggal || ''); const j = String(m.jam || '');
    if (m.jenis === 'bayar' || m.jenis === 'hapusBuku') ev.push({ jenis: m.jenis, n, tanggal: t, jam: j, urut: urut++, beli: !!(beli && m.jenis === 'bayar' && beli.has(String(m.idMutasi))) });
    else if (m.jenis === 'retur') {
      // retur nota bon: nota asalnya dulu (beku.js hitungPiutang, audit 39b no. 37 MM1) — bagian itu memotong nilai nota sejak lahir (bagian tertutup per bon
      // = mesin); sisanya ikut antrean. Tinjauan no. 9 (9 Okt): bagian nota asal juga ikut antrean WAKTU (`asal`) — lihat pasangan di bawah
      const b = m.notaAsalId == null ? null : bon.find((x) => x.u.jenis === 'jual' && String(x.u.idTrx) === String(m.notaAsalId));
      const x = b ? Math.max(0, Math.min(n, b.u.nominal - b.retur)) : 0;
      if (b && x > 0) { b.retur += x; ev.push({ jenis: 'retur', n: x, tanggal: t, jam: j, urut: urut++, asal: b }); }
      if (n - x !== 0) ev.push({ jenis: 'retur', n: n - x, tanggal: t, jam: j, urut: urut++ });
    }
  });
  // bagian tertutup per bon — loop rincianBelumLunas apa adanya (pool = pembayaran + hapus buku + sisa retur; bagian nota asal sudah memotong nilai notanya)
  let pool = ev.reduce((a, e) => a + (e.asal ? 0 : e.n), 0);
  bon.forEach((b) => { const nom = b.u.nominal - b.retur; if (pool >= nom) { b.tutup = nom; pool -= nom; } else { b.tutup = pool; pool = 0; } b.sisa = nom - b.tutup; });
  ev.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.jam.localeCompare(b.jam) || a.urut - b.urut);
  // hapus buku dibalik (minus) menetralkan hapus buku sebelumnya (terbaru dulu); kalau tidak ada, catatan penutup sebelumnya lalu sesudahnya — jumlah antrean = pool mesin
  // (bagian retur nota asal tidak ikut dinetralkan: rupiahnya milik nota itu, bukan pool)
  ev.forEach((e, i) => {
    if (e.n >= 0) return; let r = -e.n; e.n = 0; const kurangi = (k) => { const x = Math.min(r, ev[k].n); ev[k].n -= x; r -= x; };
    for (let k = i - 1; k >= 0 && r > 0; k--) if (ev[k].jenis === 'hapusBuku' && ev[k].n > 0) kurangi(k);
    for (let k = i - 1; k >= 0 && r > 0; k--) if (ev[k].n > 0 && !ev[k].asal) kurangi(k);
    for (let k = i + 1; k < ev.length && r > 0; k++) if (ev[k].n > 0 && !ev[k].asal) kurangi(k);
  });
  // pasangkan MENURUT WAKTU: tiap catatan penutup (urut waktu) menutup rupiah bon tertua yang bagian tertutupnya (mesin: tutup + retur nota asal) belum habis —
  // dua antrean FIFO; rupiah tertutup tanpa pasangan (bon bernilai minus di data) = 'lain'. Tinjauan no. 9 (9 Okt): retur nota bon menutup NOTA ASALNYA kalau
  // nota itu masih terbuka saat retur; kalau sudah ditutup pembayaran sebelumnya, returnya menutup bon terbuka tertua PADA TANGGAL RETUR (sama dengan Laporan
  // lpJalanBon). Dulu bagian nota asal dipotong lebih dulu, jadi pembayaran lama "pindah" mundur ke bon lain: bon 10 Agu tercatat dibayar 10 Agu (0 hari),
  // padahal terbuka sampai retur 15 Sep.
  bon.forEach((b) => { b.perlu = Math.max(0, b.tutup) + b.retur; });
  const isi = (b, e, x) => { potong(b, e.jenis, x, e.tanggal, e.beli); e.n -= x; b.perlu -= x; };
  let k = 0;
  ev.forEach((e) => {
    if (e.asal && e.asal.perlu > 1e-6 && e.n > 1e-6) isi(e.asal, e, Math.min(e.n, e.asal.perlu));
    while (e.n > 1e-6 && k < bon.length) { const b = bon[k]; if (!(b.perlu > 1e-6)) { k += 1; continue; } isi(b, e, Math.min(e.n, b.perlu)); }
  });
  bon.forEach((b) => { if (b.perlu > 1e-6) potong(b, 'lain', b.perlu, String(b.u.tanggal || '')); });
  return bon.map((b) => {
    const lunas = b.sisa <= 1e-6; const tgl = b.potong.map((p) => p.tanggal);
    const lunasTanggal = !lunas ? null : !b.potong.length ? (tglSahBon(b.u.tanggal) ? String(b.u.tanggal) : null) : tgl.some((t) => !t) ? null : tgl.sort().pop();
    return { jenis: b.u.jenis, tanggal: b.u.tanggal || '', ket: b.u.ket, nominal: b.u.nominal, saldoAwal: b.u.jenis === 'saldoAwal', idTrx: b.u.idTrx || null, idMutasi: b.u.idMutasi || null, sisa: b.sisa, lunas, lunasTanggal, potong: b.potong };
  });
}
/** Tinjauan no. 10 (9 Okt): saldo pembuka tutup buku dikenali dari dokumen mentahnya (tutupBuku · marginBon — sama dengan Laporan lpPecahSaldoAwal). Tanggalnya
 *  = tanggal bon tertua yang dibawanya (tutup-buku-logika pembukaBuku), jadi rupiah bon TERTUA itu (marginBon[0]: bon nota sungguhan, sisa saat dibuka) bertanggal
 *  pasti dan ikut rata-rata (FIFO: rupiah itulah yang dibayar duluan); tanggal bon-bon yang lebih muda tidak ikut dibawa ('pembuka', belum bisa dihitung).
 *  marginBon tidak ada / tidak cocok dengan nominalnya = seluruhnya 'pembuka'. → { id dokumen: rupiah bertanggal pasti } */
const bnPembuka = () => { const o = {}; ambilPiutangMutasi().forEach((m) => { if (!m || m.tipe !== 'saldoAwal' || !m.tutupBuku) return; const mb = Array.isArray(m.marginBon) ? m.marginBon : [];
  const t = mb.length && Math.abs(mb.reduce((a, b) => a + (Number(b && b.sisa) || 0), 0) - (Number(m.nominal) || 0)) < 1 ? mb[0] : null;
  o[String(m.id)] = t && t.nota !== undefined && t.nota !== null && String(t.nota) !== '' ? Math.max(0, Number(t.sisa) || 0) : 0; }); return o; };
const satuKoma = (x) => String(Math.round(x * 10) / 10).replace('.', ',');
/**
 * RATA-RATA HARI BON TERTAGIH (versi toko dari DSO) — fungsi sumber; dasbor cukup memanggil. Bon yang LUNAS dalam periode (bawaan 90 hari terakhir, setelan
 * owner aturPelanggan().tertagihHari, hari ini ikut dihitung), ditimbang rupiah: tiap rupiah yang DIBAYAR membawa hari dari bon lahir sampai pembayaran yang
 * menutupnya (jalanTutupBon). Rupiah yang ditutup HAPUS BUKU atau RETUR bukan tertagih — jumlahnya terpisah. Bon dari saldoAwal (catatan pra-sistem, tanggalnya
 * perkiraan) dikeluarkan dari rata-rata: "belum bisa dihitung: N bon saldo awal". Uang yang dibayar DI MEJA saat beli (uang kurang) yang menutup bon hari itu juga
 * bukan bon yang ditagih ("sisa RpX jadi piutang" — yang jadi bon cuma sisanya): dipajang terpisah (saatBeli); kalau FIFO memakainya untuk bon LAMA, itu tertagih
 * biasa. Σ rupiah semua kelompok = Σ nilai bon yang lunas dalam periode (lunas.rp).
 * Tiga keadaan: 'kosong' (tidak ada bon yang lunas di periode) · 'belum' (ada yang lunas, tapi tidak ada rupiah tertagih yang bisa dihitung) · 'ada' (rataHari,
 * boleh 0 = dibayar di hari bon lahir). `kunci` = satu pelanggan saja (rata-rata hari bayar orang itu).
 * Tinjauan no. 10 (9 Okt): saldo pembuka TUTUP BUKU bukan saldo awal catatan lama — kelompoknya sendiri ('pembuka', lihat bnPembuka), dan periode yang
 * menyeberang tanggal tutup buku disebut terpotong (`terpotong`, `periodeTeks`). Tinjauan no. 11: bon bernilai Rp0 / minus tidak dihitung "lunas".
 */
export function tertagihBon(kini, kunci) {
  const N = aturPelanggan().tertagihHari; const akhir = hariIniIso(kini); const awal = tambahHari(akhir, -(N - 1));
  const kosong = () => ({ n: 0, rp: 0 }); const T = { tertagih: { n: 0, rp: 0, rh: 0 }, saatBeli: kosong(), saldoAwal: kosong(), pembuka: kosong(), hapusBuku: kosong(), retur: kosong(), lain: kosong(), tanpaTanggal: kosong(), lunas: kosong() };
  const beli = bnSaatBeli(); const pembuka = bnPembuka();
  // tinjauan no. 10: sesudah tutup buku, catatan s.d. 31 Des tahun itu diarsip — bon yang lunas sebelum tanggal itu tidak ada lagi; periode yang menyeberanginya
  // TERPOTONG (disebut di kartu & lembar orang, bukan diam-diam)
  const era = eraBuku(); const potongBuku = era !== null && era + '-12-31' >= awal ? era : null; const mulai = potongBuku !== null ? (potongBuku + 1) + '-01-01' : awal;
  hitungPiutang().filter((d) => !kunci || d.kunci === kunci).forEach((d) => jalanTutupBon(d, beli).forEach((b) => {
    // tinjauan no. 11: bon bernilai Rp0 / minus tidak punya rupiah untuk ditagih — bukan "bon yang lunas" (dulu: "Belum bisa dihitung: ." tanpa sebab)
    if (!b.lunas || !(b.nominal > 1e-6) || !b.lunasTanggal || b.lunasTanggal < awal || b.lunasTanggal > akhir) return; const kena = {};
    const sa = b.saldoAwal && pembuka[String(b.idMutasi)] !== undefined ? 'pembuka' : 'saldoAwal'; let pasti = sa === 'pembuka' ? pembuka[String(b.idMutasi)] : 0;
    b.potong.forEach((p) => {
      // pembuka tutup buku: rupiah bon tertua yang dibawanya (bertanggal pasti) dihitung seperti bon biasa, sisanya kelompok 'pembuka'
      const tepat = Math.max(0, Math.min(p.n, pasti)); pasti -= p.n;
      [[tepat, false], [p.n - tepat, b.saldoAwal]].forEach(([n, bsa]) => { if (!(n > 1e-6)) return;
        const k = p.jenis !== 'bayar' ? p.jenis : bsa ? sa : p.hari === null ? 'tanpaTanggal' : p.beli && p.hari === 0 ? 'saatBeli' : 'tertagih';
        T[k].rp += n; if (k === 'tertagih') T.tertagih.rh += n * p.hari; kena[k] = true; T.lunas.rp += n; });
    });
    Object.keys(kena).forEach((k) => { T[k].n += 1; }); T.lunas.n += 1;
  }));
  const rataHari = T.tertagih.rp > 1e-6 ? T.tertagih.rh / T.tertagih.rp : null; const keadaan = T.lunas.n === 0 ? 'kosong' : rataHari === null ? 'belum' : 'ada';
  const sebab = [T.saldoAwal.n ? T.saldoAwal.n + ' bon saldo awal (tanggal lahirnya perkiraan)' : '', T.pembuka.n ? T.pembuka.n + ' saldo bawaan tutup buku (tanggal bon-bon mudanya tidak ikut dibawa)' : '',
    T.saatBeli.n ? RP(T.saatBeli.rp) + ' dibayar di meja saat beli (' + T.saatBeli.n + ' bon, bukan bon yang ditagih)' : '', T.hapusBuku.n ? T.hapusBuku.n + ' bon ditutup hapus buku ' + RP(T.hapusBuku.rp) : '',
    T.retur.n ? T.retur.n + ' bon ditutup retur ' + RP(T.retur.rp) : '', T.tanpaTanggal.n ? T.tanpaTanggal.n + ' bon tanpa tanggal' : '', T.lain.n ? T.lain.n + ' bon ditutup catatan lain ' + RP(T.lain.rp) : ''].filter(Boolean);
  const periodeKata = potongBuku !== null ? 'sejak ' + formatTanggal(mulai) + ' (tutup buku ' + potongBuku + ' memotong periode ' + N + ' hari — bon yang lunas sebelumnya ikut diarsip)' : 'dalam ' + N + ' hari terakhir';
  return Object.assign(T, { hari: N, awal, akhir, rataHari, keadaan, sebab, terpotong: potongBuku !== null ? { tahun: potongBuku, mulai } : null,
    periodeTeks: N + ' hari terakhir' + (potongBuku !== null ? ' · terpotong tutup buku ' + potongBuku + ', sejak ' + formatTanggal(mulai) : ''),
    rataTeks: keadaan === 'ada' ? satuKoma(rataHari) + ' hari' : keadaan === 'belum' ? 'belum bisa dihitung' : '—',
    teks: keadaan === 'kosong' ? 'Tidak ada bon yang lunas ' + periodeKata + '.' : keadaan === 'belum' ? 'Belum bisa dihitung: ' + sebab.join(' · ') + '.'
      : 'Dari ' + T.tertagih.n + ' bon (' + RP(T.tertagih.rp) + ' dibayar) yang lunas ' + periodeKata + (rataHari < 0.05 ? ' — dibayar di hari bon lahir' : '') + (sebab.length ? '. Tidak ikut dihitung: ' + sebab.join(' · ') : '') + '.' });
}
/** Susun ketiga tab: buku (satu orang satu halaman), papan (tiga lajur menurut yang harus dilakukan), umur (ember). */
export function susunBon(kini, bukuKunci, ember) {
  const semua = semuaBon(kini); const berutang = semua.filter((b) => b.sisa > 0); const total = berutang.reduce((a, b) => a + b.sisa, 0);
  const lebih = semua.filter((b) => b.status === 'lebih').sort((a, b) => a.sisa - b.sisa).map((b) => ({ kunci: b.kunci, nama: b.nama, lebih: -b.sisa, uang: b.lebihUang, hapus: b.lebihHapus })); const maks = Math.max(1, ...berutang.map((b) => b.sisa)); // no. 4: total bon TIDAK dikurangi — kelebihan bayar dipajang terpisah
  const gambar = (b) => Object.assign({}, b, { nBon: b.buka.length + ' bon' + (b.bayar > 0 ? ' · sudah membayar ' + RP(b.bayar) : ''), lebar: Math.max(3, Math.round(b.sisa / maks * 100)) });
  const Pa = berutang.find((b) => b.kunci === bukuKunci) || berutang.slice().sort((a, b) => b.sisa - a.sisa)[0] || null;
  const halaman = []; if (Pa) { const utang = Pa.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || ''))); let tertutup = Pa.bayar + Pa.dihapus + (Pa.retur || 0) - bnDiretur(utang);
    utang.forEach((u) => { const nom = u.nominal - (u.diretur || 0); const lunas = tertutup >= nom; tertutup = Math.max(0, tertutup - nom); halaman.push({ t: u.tanggal || '', u: 0, tgl: formatTanggal(u.tanggal), teks: u.ket || 'Belanja', n: u.nominal, jenis: lunas ? 'coret' : 'bon' }); });
    Pa.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur').forEach((m) => halaman.push({ t: m.tanggal || '', u: 1, tgl: formatTanggal(m.tanggal), teks: m.jenis === 'bayar' ? m.ket.replace(/^Bayar/, 'bayar') : m.jenis === 'retur' ? m.ket.replace(/^Retur barang/, 'barang kembali (retur)') : bnBalik(m) ? m.ket.replace(/^Hapus buku · /, '').replace(/^Hapus buku/, 'hapus buku dibalik') : m.ket.replace(/^Hapus buku/, 'DIHAPUS'), n: -m.nominal, jenis: m.jenis })); halaman.sort((a, b) => a.t.localeCompare(b.t) || a.u - b.u); }
  const papan = []; const lajur = (judul, awas, d) => { papan.push({ lajur: true, judul, awas, jumlah: d.reduce((a, b) => a + b.sisa, 0), n: d.length }); d.slice().sort((a, b) => b.sisa - a.sisa).forEach((b) => papan.push(gambar(b))); };
  lajur('Tagih hari ini', true, berutang.filter((b) => b.status === 'janjiLewat' || b.status === 'perluTagih')); lajur('Tunggu dulu', false, berutang.filter((b) => b.status === 'menunggu' || b.status === 'baru')); lajur('Macet — usul hapus bon', false, berutang.filter((b) => b.status === 'macet'));
  // paket brief 9 Okt: batas kelompok umur = setelan owner (bawaan 7 / 30 / 90 hari = garis umur yang dikunci); bon tanpa tanggal = kelompok sendiri
  const SU = sebaranUmurBon(kini, semua); const eP = SU.find((e) => e.id === ember) || null;
  // Paket F2 (owner 8 Okt 2026: "catatannya jangan dihapus — sewaktu-waktu ada yang mau bayar"): nama yang bonnya habis karena dihapus dari buku tidak ada di
  // daftar berutang — di sini jejaknya, dan pintu ke lembarnya (Dibayar sesudah dihapus buku). Nama yang masih punya sisa ada di daftar biasa.
  const dihapus = semua.filter((b) => b.dihapus > 0.5 && b.sisa <= 0 && b.status !== 'lebih').map((b) => ({ kunci: b.kunci, nama: b.nama, dihapus: Math.round(b.dihapus),
    tanggal: b.mutasi.filter((m) => m.jenis === 'hapusBuku' && !bnBalik(m)).map((m) => String(m.tanggal || '')).sort().pop() || '' })).sort((a, b) => b.dihapus - a.dihapus || a.nama.localeCompare(b.nama));
  return { total, berutang: berutang.length, dihapus, jumlahDihapus: dihapus.reduce((a, x) => a + x.dihapus, 0), lebih, jumlahLebih: lebih.reduce((a, x) => a + x.lebih, 0), jumlahLebihUang: lebih.reduce((a, x) => a + x.uang, 0), jumlahLebihHapus: lebih.reduce((a, x) => a + x.hapus, 0), buku: Pa ? { kunci: Pa.kunci, nama: Pa.nama, sisa: Pa.sisa, ket: Pa.ket, status: Pa.status, halaman } : null, namaBuku: berutang.slice().sort((a, b) => b.sisa - a.sisa).map((b) => ({ kunci: b.kunci, nama: b.nama, aktif: !!Pa && Pa.kunci === b.kunci })), papan,
    ember: SU.map((e) => ({ id: e.id, label: e.label, n: e.n, jumlah: e.jumlah, aktif: !!eP && eP.id === e.id, tua: e.tua })), perUmur: (eP ? eP.isi.slice() : berutang.slice()).sort((a, b) => (b.umur || 0) - (a.umur || 0)).map(gambar), umurTeks: eP ? (eP.id === 'e0' ? 'Hanya bon tanpa tanggal (umurnya tidak bisa dihitung)' : 'Hanya bon yang tertuanya ' + eP.label) + ' — ketuk lagi kotaknya untuk melihat semua' : 'Yang paling lama tidur ada di atas', atur: aturPelanggan(), tertagih: tertagihBon(kini) };
}
/** Lembar satu orang: rincian bon terbuka + riwayat (pembayaran, hapus buku, tagihan). */
export function lembarBon(kini, kunci) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return null;
  const riwayat = b.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur').map((m) => ({ t: (m.tanggal || '') + ' ' + (m.jam || ''), tgl: formatTanggal(m.tanggal), teks: m.jenis === 'bayar' ? m.ket.replace(/^Bayar/, 'membayar') : m.jenis === 'retur' ? m.ket.replace(/^Retur barang/, 'barang kembali (retur), bon dipotong') : bnBalik(m) ? m.ket.replace(/^Hapus buku · /, '').replace(/^Hapus buku/, 'hapus buku dibalik') : m.ket.replace(/^Hapus buku/, 'DIHAPUS dari buku'), n: -m.nominal }))
    .concat(cacheMentah('tagih').filter((t) => t.kunci === kunci).map((t) => ({ t: (t.tanggal || '') + ' ' + (t.jam || ''), tgl: formatTanggal(t.tanggal), teks: 'ditagih' + (t.janji ? ' · janji ' + formatTanggal(t.janji) : ' · tanpa janji'), n: null }))).sort((a, b) => b.t.localeCompare(a.t));
  return Object.assign({}, b, { rinci: b.buka.map((r) => ({ tgl: formatTanggal(r.tanggal), teks: (r.ket || 'Belanja') + (r.sisa < r.nominal ? ' (dari ' + RP(r.nominal) + ')' : ''), n: r.sisa })), riwayat, alasanPilihan: aturPelanggan().alasanHapus, tertagih: tertagihBon(kini, kunci) });
}
/** Pesan tagihan WhatsApp — kalimat kirimTagihanPiutang index.html (salam = setelan owner); nomor dari kartu kalau ada. */
export function pesanTagih(kini, kunci) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b || b.sisa <= 0) return null;
  const baris = ['*TOKO BERAS M.IQBAL*', 'Catatan belanja a.n. ' + b.nama, '', 'Belum lunas:'];
  b.buka.forEach((r) => baris.push('- ' + formatTanggal(r.tanggal) + ' · ' + (r.ket || 'Belanja') + ' — ' + RP(r.nominal) + (r.sisa < r.nominal ? ' (sisa ' + RP(r.sisa) + ')' : '')));
  baris.push(''); baris.push('*Total sisa: ' + RP(b.sisa) + '*'); if (b.umur !== null && b.umur > 0) baris.push('(tertunggak ' + umurKata(b.umur) + ')'); baris.push(''); baris.push(aturPelanggan().salamTagih);
  const digit = String(b.kontak || '').replace(/\D/g, ''); const nomor = !digit ? '' : digit.indexOf('0') === 0 ? '62' + digit.slice(1) : digit.indexOf('62') === 0 ? digit : digit.indexOf('8') === 0 ? '62' + digit : digit;
  return { baris, teks: baris.join('\n'), nomor, url: 'https://wa.me/' + nomor + '?text=' + encodeURIComponent(baris.join('\n')), tujuan: nomor ? 'Dikirim ke ' + b.kontak + ' (dari kartu pelanggan).' : 'Nomornya belum ada di kartu pelanggan — WhatsApp akan menanyakan tujuannya.', janjiPilihan: JANJI_PILIHAN.map((j) => ({ hari: j[0], nama: j[1] + (j[0] ? ' (' + formatTanggal(tambahHari(hariIniIso(kini), j[0])) + ')' : '') })) };
}
export function susunTagih(kini, kunci, janjiHari, w) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b || b.sisa <= 0) return { tolak: 'Tidak ada yang perlu ditagih' }; const janji = Number(janjiHari) > 0 ? tambahHari(w.tanggal, Number(janjiHari)) : null;
  return { dokumen: [{ koleksi: 'tagihPelanggan', data: { id: w.idUnik(), kunci, nama: b.nama, tanggal: w.tanggal, jam: w.jam, janji, sisa: b.sisa, lewat: 'whatsapp' } }], patch: { kabar: 'Tagihan ' + b.nama + ' ' + RP(b.sisa) + ' dicatat' + (janji ? ' · janji bayar ' + formatTanggal(janji) : ' · tanpa janji') + '. WhatsApp dibuka — pesannya masih bisa diubah sebelum dikirim.', kabarAwas: false } };
}
/** Pembayaran bon — dokumen persis simpanBayarPiutang; tidak boleh melebihi sisa; LUNAS hanya bila nol. */
/** audit 39b no. 3 (tinjauan T6): kalimat pembayaran bon yang jujur soal tutup hari. Titik kas tutup hari bertanggal hari itu, dan tempat uang hanya
 *  menghitung gerakan SESUDAH tanggal titik (uang-logika saldoKantong) — pembayaran yang dicatat sesudah hari itu ditutup baru ikut kas (dan potongan
 *  QRIS-nya baru dicatat) kalau tutup hari diulang. '' = tidak ada yang perlu dikatakan (tunai, hari belum ditutup). */
export function kalimatBayarTutup(cara, tanggal) {
  const t = (ambilTutupHari() || []).find((x) => x && x.tanggal === tanggal);
  if (t) return 'hari ini SUDAH ditutup' + (t.jam ? ' jam ' + t.jam : '') + ' — uang ini' + (cara === 'QRIS' ? ' dan potongan QRIS (MDR)-nya' : '') + ' baru ikut hitungan kas kalau tutup hari diulang';
  return cara === 'QRIS' ? 'potongan QRIS (MDR)-nya, kalau ada, dicatat saat tutup hari' : '';
}
export function susunBayarBon(kini, kunci, nominal, cara, catatan, pengantar, w) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return { tolak: 'Nama itu tidak ada di buku bon' };
  if (b.status === 'lebih') return { tolak: b.nama + ': ' + kalimatLebih(pecahLebih(b)) + '. Tidak ada bon untuk dibayar.' }; const n = Math.round(bnAngka(nominal));
  if (!(n > 0)) return { tolak: 'Ketik jumlah yang dibayar' }; if (n > b.sisa) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya (' + RP(b.sisa) + ') — kalau memang lebih, catat sisanya sebagai penjualan biasa, bukan pembayaran bon' };
  const c = cara === 'QRIS' ? 'QRIS' : 'Tunai'; const data = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: b.nama, nominal: n, tanggal: w.tanggal, jam: w.jam, caraBayar: c, catatan: String(catatan || '').trim(), dicatatDi: 'sistem' };
  if (!bnKosong(pengantar) && kunciPelanggan(pengantar) !== kunci) data.dibawaOleh = String(pengantar).trim();
  const sisaBaru = b.sisa - n; return { dokumen: [{ koleksi: 'piutangMutasi', data }], sisaBaru, patch: { kabar: (sisaBaru <= 0 ? b.nama + ' LUNAS. Pembayaran ' + RP(n) + ' dicatat' : 'Pembayaran ' + RP(n) + ' dicatat — sisa bon ' + b.nama + ' sekarang ' + RP(sisaBaru) + ', belum lunas') + ' · ' + (c === 'QRIS' ? 'rekening' : 'laci') + ' bertambah, laba tidak berubah (sudah dihitung waktu berasnya dijual)' + (kalimatBayarTutup(c, data.tanggal) ? '; ' + kalimatBayarTutup(c, data.tanggal) : '') + (data.dibawaOleh ? ' · dibawa ' + data.dibawaOleh : '') + '.', kabarAwas: false } };
}
/**
 * Paket F2 (owner 8 Okt 2026): piutang yang sudah DIHAPUS dari buku ternyata dibayar. Hapus buku lama tidak disentuh (jejaknya permanen) — dibalik dengan catatan
 * hapus buku BERNILAI MINUS (mesin menjumlah nominal apa adanya: beku.js hitungPiutang `dihapus` & hitungLabaBersihRentang `hapusBuku`; Laporan lpJalanBon membuka
 * lagi bon yang ditutupnya) + pembayaran biasa, SATU kiriman: sisa bon tetap, kas bertambah, laba bulan ini naik sebesar itu (pemulihan piutang). Kalau
 * pembayarannya SUDAH tercatat (status 'lebih' — "dibayar padahal sudah dihapus", mis. dari HP kasir) cukup hapus bukunya yang dibalik, tanpa pembayaran kedua.
 */
export function susunBayarSesudahHapus(kini, kunci, nominal, cara, catatan, w, yakin) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return { tolak: 'Nama itu tidak ada di buku bon' };
  const dihapus = Math.round(b.dihapus || 0); if (!(dihapus > 0)) return { tolak: 'Belum ada bon ' + b.nama + ' yang dihapus dari buku — catat pembayarannya seperti biasa' };
  const sudah = b.status === 'lebih' ? Math.round(b.lebihHapus || 0) : 0;
  if (b.status === 'lebih' && !(sudah > 0)) return { tolak: b.nama + ': ' + kalimatLebih(pecahLebih(b)) + '. Tidak ada hapus buku yang terbayar.' };
  const n = Math.round(bnAngka(nominal)); if (!(n > 0)) return { tolak: sudah > 0 ? 'Ketik jumlah hapus buku yang dibalik' : 'Ketik jumlah yang dibayar' };
  const maks = sudah > 0 ? Math.min(sudah, dihapus) : dihapus;
  if (n > maks) return { tolak: sudah > 0 ? 'Yang dibayar padahal sudah dihapus ' + RP(maks) + ' — paling banyak sebesar itu' : 'Yang pernah dihapus dari buku a.n. ' + b.nama + ' ' + RP(maks) + ' — paling banyak sebesar itu' + (b.sisa > 0 ? '; sisanya catat sebagai pembayaran bon biasa' : '') };
  const c = cara === 'QRIS' ? 'QRIS' : 'Tunai'; const ket = String(catatan || '').trim().slice(0, 60);
  if (!yakin) return { tolak: (sudah > 0 ? 'Balik hapus buku ' + RP(n) + ' a.n. ' + b.nama + ' (uangnya sudah tercatat)?' : RP(n) + ' dari bon ' + b.nama + ' yang dulu dihapus dibayar ' + (c === 'QRIS' ? 'lewat QRIS' : 'tunai') + '?')
    + ' Hapus buku lama TETAP ada; dibalik dengan catatan baru — laba bulan ini naik ' + RP(n) + '. Ketuk sekali lagi', perluYakin: true };
  const dokumen = [{ koleksi: 'piutangMutasi', data: { id: w.idUnik(), tipe: 'hapusBuku', namaPelanggan: b.nama, nominal: -n, alasan: 'hapus buku dibalik — dibayar sesudah dihapus' + (ket ? ' · ' + ket : ''), balikHapus: true, tanggal: w.tanggal, jam: w.jam, dicatatDi: 'sistem' } }];
  if (!(sudah > 0)) dokumen.push({ koleksi: 'piutangMutasi', data: { id: w.idUnik(), tipe: 'bayar', namaPelanggan: b.nama, nominal: n, tanggal: w.tanggal, jam: w.jam, caraBayar: c, catatan: 'dibayar sesudah dihapus buku' + (ket ? ' · ' + ket : ''), dicatatDi: 'sistem' } });
  const tutup = sudah > 0 ? '' : kalimatBayarTutup(c, w.tanggal);
  return { dokumen, patch: { kabar: (sudah > 0 ? 'Hapus buku ' + RP(n) + ' a.n. ' + b.nama + ' dibalik — uangnya sudah tercatat sebelumnya. ' : RP(n) + ' dari bon ' + b.nama + ' yang dulu dihapus diterima · ' + (c === 'QRIS' ? 'rekening' : 'laci') + ' bertambah. ')
    + 'Laba bulan ini naik ' + RP(n) + ' (hapus buku dibalik); catatan hapus buku lama tetap ada' + (tutup ? '; ' + tutup : '') + '.', kabarAwas: false } };
}
/** Hapus buku — bukan uang masuk, kerugian bulan ini, permanen: alasan wajib + dua ketukan. */
export function susunHapusBon(kini, kunci, nominal, alasan, w, yakin) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return { tolak: 'Nama itu tidak ada di buku bon' };
  if (b.status === 'lebih') return { tolak: b.nama + ': ' + kalimatLebih(pecahLebih(b)) + '. Tidak ada bon untuk dihapus dari buku.' }; const n = Math.round(bnAngka(nominal));
  if (!(n > 0)) return { tolak: 'Ketik jumlah yang dihapus dari buku' }; if (n > b.sisa) return { tolak: 'Hapus buku ' + RP(n) + ' melebihi sisa bonnya (' + RP(b.sisa) + ') — maksimal sebesar sisanya' }; if (bnKosong(alasan)) return { tolak: 'Alasannya wajib — jejak ini permanen dan dibaca lagi bertahun-tahun ke depan' };
  if (!yakin) return { tolak: 'Hapus ' + RP(n) + ' dari buku a.n. ' + b.nama + '? BUKAN uang masuk — kas tidak berubah; dicatat sebagai KERUGIAN bulan ini dan tidak bisa dibatalkan. Ketuk sekali lagi', perluYakin: true };
  const data = { id: w.idUnik(), tipe: 'hapusBuku', namaPelanggan: b.nama, nominal: n, alasan: String(alasan).trim(), tanggal: w.tanggal, jam: w.jam, dicatatDi: 'sistem' };
  return { dokumen: [{ koleksi: 'piutangMutasi', data }], patch: { kabar: 'Dihapus dari buku ' + RP(n) + ' a.n. ' + b.nama + ' (' + data.alasan + '). Kas tidak berubah; kerugiannya masuk laporan bulan ini.' + (b.sisa - n <= 0 ? ' Bonnya kini nol.' : ' Sisa bon ' + RP(b.sisa - n) + '.'), kabarAwas: false } };
}
