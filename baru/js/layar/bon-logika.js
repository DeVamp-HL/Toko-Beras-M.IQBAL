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
import { cacheMentah } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';
import { aturPelanggan, kartuTersimpan, hariKe } from './pelanggan-logika.js';

const bnAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const bnKosong = (v) => v === undefined || v === null || String(v).trim() === '';
/** Umur dalam kata — persis umurKeKata index.html 29121 (dipakai di pesan WhatsApp). */
export function umurKata(hari) { if (hari === null || hari === undefined) return 'baru'; if (hari <= 0) return 'hari ini'; if (hari < 60) return hari + ' hari'; if (hari < 365) return Math.round(hari / 30) + ' bulan'; const th = Math.floor(hari / 365), bln = Math.round((hari % 365) / 30); return th + ' tahun' + (bln > 0 ? ' ' + bln + ' bln' : ''); }
/** Rincian bon yang BELUM tertutup (FIFO) — rincianBelumLunas index.html 29599, apa adanya. */
export function rincianBelumLunas(d) {
  const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
  let tertutup = d.bayar + d.dihapus; const hasil = [];
  for (const u of utang) { if (tertutup >= u.nominal) { tertutup -= u.nominal; continue; } hasil.push({ tanggal: u.tanggal, ket: u.ket, nominal: u.nominal, sisa: u.nominal - tertutup, idTrx: u.idTrx || null, idMutasi: u.idMutasi || null }); tertutup = 0; }
  return hasil;
}
export const KATA_STATUS = { macet: 'macet — usul hapus', janjiLewat: 'janjinya lewat', menunggu: 'menunggu janji', perluTagih: 'waktunya ditagih', baru: 'masih baru', lunas: 'lunas' };
export const JANJI_PILIHAN = [[0, 'tanpa janji'], [3, '3 hari lagi'], [7, 'seminggu lagi'], [14, 'dua minggu lagi']];
const tambahHari = (iso, n) => new Date((hariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
/** Semua orang di buku bon (mesin beku) + status menurut aturan owner + tagihan terakhir. */
export function semuaBon(kini) {
  const iso = hariIniIso(kini); const atur = aturPelanggan(); const tagihSemua = cacheMentah('tagih');
  return hitungPiutang().map((d, no) => { const buka = rincianBelumLunas(d); const sisa = d.sisa || 0; const umur = sisa > 0 ? d.umurHari : null;
    const bayarAkhir = d.mutasi.filter((m) => m.jenis === 'bayar').sort((a, b) => String(b.tanggal + (b.jam || '')).localeCompare(String(a.tanggal + (a.jam || ''))))[0] || null;
    const tagih = tagihSemua.filter((t) => t.kunci === d.kunci).sort((a, b) => String(b.tanggal + (b.jam || '')).localeCompare(String(a.tanggal + (a.jam || ''))))[0] || null;
    const janjiLewat = !!tagih && !!tagih.janji && tagih.janji < iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal); const menunggu = !!tagih && !!tagih.janji && tagih.janji >= iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal);
    const diamSejak = bayarAkhir ? hariKe(iso) - hariKe(bayarAkhir.tanggal) : umur; const macet = sisa > 0 && umur !== null && umur > atur.macetHari && (diamSejak === null || diamSejak > atur.macetHari);
    const status = sisa <= 0 ? 'lunas' : macet ? 'macet' : janjiLewat ? 'janjiLewat' : menunggu ? 'menunggu' : umur !== null && umur >= atur.tagihHari ? 'perluTagih' : 'baru'; const kartu = kartuTersimpan(d.kunci);
    const ket = status === 'janjiLewat' ? 'janji bayar ' + formatTanggal(tagih.janji) + ' — lewat ' + (hariKe(iso) - hariKe(tagih.janji)) + ' hari' : status === 'menunggu' ? 'janji bayar ' + formatTanggal(tagih.janji) : status === 'macet' ? 'bon tertua ' + umurKata(umur) + ', tidak ada pembayaran selama itu'
      : status === 'perluTagih' ? 'bon tertua ' + umurKata(umur) + (tagih ? ' · terakhir ditagih ' + formatTanggal(tagih.tanggal) : ' · belum pernah ditagih') : status === 'lunas' ? 'tidak ada bon yang terbuka' : 'bon tertua ' + umurKata(umur);
    return { kunci: d.kunci, nama: d.nama, no, sisa, umur, buka, bayar: d.bayar, dihapus: d.dihapus, total: d.total, mutasi: d.mutasi, bayarAkhir, tagih, diamSejak, status, ket, cap: KATA_STATUS[status], kontak: kartu ? kartu.kontak : '', dikenali: !!(kartu && kartu.dikenali), tanggalJanggal: !!d.tanggalJanggal }; });
}
const EMBER = [['e1', '≤ 7 hari', 0, 7], ['e2', '8–30 hari', 8, 30], ['e3', '1–3 bulan', 31, 90], ['e4', '> 3 bulan', 91, 99999]];
/** Susun ketiga tab: buku (satu orang satu halaman), papan (tiga lajur menurut yang harus dilakukan), umur (ember). */
export function susunBon(kini, bukuKunci, ember) {
  const semua = semuaBon(kini); const berutang = semua.filter((b) => b.sisa > 0); const total = berutang.reduce((a, b) => a + b.sisa, 0); const maks = Math.max(1, ...berutang.map((b) => b.sisa));
  const gambar = (b) => Object.assign({}, b, { nBon: b.buka.length + ' bon' + (b.bayar > 0 ? ' · sudah membayar ' + RP(b.bayar) : ''), lebar: Math.max(3, Math.round(b.sisa / maks * 100)) });
  const Pa = berutang.find((b) => b.kunci === bukuKunci) || berutang.slice().sort((a, b) => b.sisa - a.sisa)[0] || null;
  const halaman = []; if (Pa) { const utang = Pa.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || ''))); let tertutup = Pa.bayar + Pa.dihapus;
    utang.forEach((u) => { const lunas = tertutup >= u.nominal; tertutup = Math.max(0, tertutup - u.nominal); halaman.push({ t: u.tanggal || '', u: 0, tgl: formatTanggal(u.tanggal), teks: u.ket || 'Belanja', n: u.nominal, jenis: lunas ? 'coret' : 'bon' }); });
    Pa.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku').forEach((m) => halaman.push({ t: m.tanggal || '', u: 1, tgl: formatTanggal(m.tanggal), teks: m.jenis === 'bayar' ? m.ket.replace(/^Bayar/, 'bayar') : m.ket.replace(/^Hapus buku/, 'DIHAPUS'), n: -m.nominal, jenis: m.jenis })); halaman.sort((a, b) => a.t.localeCompare(b.t) || a.u - b.u); }
  const papan = []; const lajur = (judul, awas, d) => { papan.push({ lajur: true, judul, awas, jumlah: d.reduce((a, b) => a + b.sisa, 0), n: d.length }); d.slice().sort((a, b) => b.sisa - a.sisa).forEach((b) => papan.push(gambar(b))); };
  lajur('Tagih hari ini', true, berutang.filter((b) => b.status === 'janjiLewat' || b.status === 'perluTagih')); lajur('Tunggu dulu', false, berutang.filter((b) => b.status === 'menunggu' || b.status === 'baru')); lajur('Macet — usul hapus bon', false, berutang.filter((b) => b.status === 'macet'));
  const diEmber = (e) => berutang.filter((b) => b.umur !== null && b.umur >= e[2] && b.umur <= e[3]); const eP = EMBER.find((e) => e[0] === ember) || null;
  return { total, berutang: berutang.length, buku: Pa ? { kunci: Pa.kunci, nama: Pa.nama, sisa: Pa.sisa, ket: Pa.ket, status: Pa.status, halaman } : null, namaBuku: berutang.slice().sort((a, b) => b.sisa - a.sisa).map((b) => ({ kunci: b.kunci, nama: b.nama, aktif: !!Pa && Pa.kunci === b.kunci })), papan,
    ember: EMBER.map((e) => ({ id: e[0], label: e[1], n: diEmber(e).length, jumlah: diEmber(e).reduce((a, b) => a + b.sisa, 0), aktif: !!eP && eP[0] === e[0], tua: e[0] === 'e4' })), perUmur: (eP ? diEmber(eP) : berutang.slice()).sort((a, b) => (b.umur || 0) - (a.umur || 0)).map(gambar), umurTeks: eP ? 'Hanya bon yang tertuanya ' + eP[1] + ' — ketuk lagi kotaknya untuk melihat semua' : 'Yang paling lama tidur ada di atas', atur: aturPelanggan() };
}
/** Lembar satu orang: rincian bon terbuka + riwayat (pembayaran, hapus buku, tagihan). */
export function lembarBon(kini, kunci) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return null;
  const riwayat = b.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku').map((m) => ({ t: (m.tanggal || '') + ' ' + (m.jam || ''), tgl: formatTanggal(m.tanggal), teks: m.jenis === 'bayar' ? m.ket.replace(/^Bayar/, 'membayar') : m.ket.replace(/^Hapus buku/, 'DIHAPUS dari buku'), n: -m.nominal }))
    .concat(cacheMentah('tagih').filter((t) => t.kunci === kunci).map((t) => ({ t: (t.tanggal || '') + ' ' + (t.jam || ''), tgl: formatTanggal(t.tanggal), teks: 'ditagih' + (t.janji ? ' · janji ' + formatTanggal(t.janji) : ' · tanpa janji'), n: null }))).sort((a, b) => b.t.localeCompare(a.t));
  return Object.assign({}, b, { rinci: b.buka.map((r) => ({ tgl: formatTanggal(r.tanggal), teks: (r.ket || 'Belanja') + (r.sisa < r.nominal ? ' (dari ' + RP(r.nominal) + ')' : ''), n: r.sisa })), riwayat, alasanPilihan: aturPelanggan().alasanHapus });
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
export function susunBayarBon(kini, kunci, nominal, cara, catatan, pengantar, w) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return { tolak: 'Nama itu tidak ada di buku bon' }; const n = Math.round(bnAngka(nominal));
  if (!(n > 0)) return { tolak: 'Ketik jumlah yang dibayar' }; if (n > b.sisa) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya (' + RP(b.sisa) + ') — kalau memang lebih, catat sisanya sebagai penjualan biasa, bukan pembayaran bon' };
  const c = cara === 'QRIS' ? 'QRIS' : 'Tunai'; const data = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: b.nama, nominal: n, tanggal: w.tanggal, jam: w.jam, caraBayar: c, catatan: String(catatan || '').trim(), dicatatDi: 'sistem' };
  if (!bnKosong(pengantar) && kunciPelanggan(pengantar) !== kunci) data.dibawaOleh = String(pengantar).trim();
  const sisaBaru = b.sisa - n; return { dokumen: [{ koleksi: 'piutangMutasi', data }], sisaBaru, patch: { kabar: (sisaBaru <= 0 ? b.nama + ' LUNAS. Pembayaran ' + RP(n) + ' dicatat' : 'Pembayaran ' + RP(n) + ' dicatat — sisa bon ' + b.nama + ' sekarang ' + RP(sisaBaru) + ', belum lunas') + ' · ' + (c === 'QRIS' ? 'rekening' : 'laci') + ' bertambah, laba tidak berubah (sudah dihitung waktu berasnya dijual)' + (data.dibawaOleh ? ' · dibawa ' + data.dibawaOleh : '') + '.', kabarAwas: false } };
}
/** Hapus buku — bukan uang masuk, kerugian bulan ini, permanen: alasan wajib + dua ketukan. */
export function susunHapusBon(kini, kunci, nominal, alasan, w, yakin) {
  const b = semuaBon(kini).find((x) => x.kunci === kunci); if (!b) return { tolak: 'Nama itu tidak ada di buku bon' }; const n = Math.round(bnAngka(nominal));
  if (!(n > 0)) return { tolak: 'Ketik jumlah yang dihapus dari buku' }; if (n > b.sisa) return { tolak: 'Hapus buku ' + RP(n) + ' melebihi sisa bonnya (' + RP(b.sisa) + ') — maksimal sebesar sisanya' }; if (bnKosong(alasan)) return { tolak: 'Alasannya wajib — jejak ini permanen dan dibaca lagi bertahun-tahun ke depan' };
  if (!yakin) return { tolak: 'Hapus ' + RP(n) + ' dari buku a.n. ' + b.nama + '? BUKAN uang masuk — kas tidak berubah; dicatat sebagai KERUGIAN bulan ini dan tidak bisa dibatalkan. Ketuk sekali lagi', perluYakin: true };
  const data = { id: w.idUnik(), tipe: 'hapusBuku', namaPelanggan: b.nama, nominal: n, alasan: String(alasan).trim(), tanggal: w.tanggal, jam: w.jam, dicatatDi: 'sistem' };
  return { dokumen: [{ koleksi: 'piutangMutasi', data }], patch: { kabar: 'Dihapus dari buku ' + RP(n) + ' a.n. ' + b.nama + ' (' + data.alasan + '). Kas tidak berubah; kerugiannya masuk laporan bulan ini.' + (b.sisa - n <= 0 ? ' Bonnya kini nol.' : ' Sisa bon ' + RP(b.sisa - n) + '.'), kabarAwas: false } };
}
