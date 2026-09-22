// LAYAR HARGA & PEMASOK — H3 BELANJA (dikunci owner 18 Sep 2026: gabungan Isi Truk · Kapan Habis · Daftar di Kertas). Logika tanpa DOM, awalan bl.
// Aturan dari sistem berjalan (hitungSaranBelanja index.html): disarankan bila habis ≤ AMBANG hari (7), butuh = laju × TARGET hari (14) − sisa, dibulatkan KE ATAS ke karung
// yang biasa dipakai merek itu (merkPunyaKarungBerat); laju = mesin beku hitungLajuPakai (14 hari). Tanpa laju → TIDAK menebak (disebut).
// Owner memesan MUATAN, bukan uang (memori muatan-tiga-ton-tetap): muatan truk bawaan = median berat kedatangan nyata (TERUKUR, disebut), owner boleh mengubahnya di Atur.
// Tiap pemasok membawa mereknya sendiri (harga terakhir per pemasok dari kedatangan, tanggalnya selalu ditulis); RODA MAS biasa BON, SEJATI biasa TUNAI → perkiraan uangnya dibaca beda.
// Pesanan yang dikirim = koleksi BARU pesananPemasok (menunggu datang / batal); "sudah datang" dibaca dari kedatangan pemasok itu SESUDAH pesanan (tidak ditebak dari stok).
import { hitungStokKarungPerMerk, hitungLajuPakai, kasPada } from '../mesin/beku.js';
import { merkPunyaKarungBerat, JENDELA_LAJU_HARI } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilPesananPemasok, cacheMentah } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { daftarPemasok, tempoPemasok, nomorWa, bpTambahHari, pemasokSungguhan } from './bon-pemasok-logika.js';

export const ATUR_BELANJA_BAWAAN = { ambangHari: 7, targetHari: 14, muatanKg: 0 };
export const TAB_BELANJA = [['truk', 'Isi truk'], ['hari', 'Kapan habis'], ['kertas', 'Daftar']];
const blAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const blKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const blKG = (n) => ANGKA(n) + ' kg';

/** Muatan truk yang TERUKUR: median kg dari 12 kedatangan nyata terakhir, dibulatkan ke 25 kg. 0 = belum ada kedatangan. */
export function muatanTerukur() {
  const kg = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok)).sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, 12)
    .map((b) => (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0)).filter((x) => x > 0).sort((a, b) => a - b);
  if (!kg.length) return 0; const m = kg.length % 2 ? kg[(kg.length - 1) / 2] : (kg[kg.length / 2 - 1] + kg[kg.length / 2]) / 2; return Math.round(m / 25) * 25;
}
export function aturBelanja() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'belanja') || null; const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : null);
  const muat = ambil('muatanKg', (n) => n > 0);
  return { ambangHari: ambil('ambangHari', (n) => n >= 0 && n <= 60) ?? ATUR_BELANJA_BAWAAN.ambangHari, targetHari: ambil('targetHari', (n) => n > 0 && n <= 90) ?? ATUR_BELANJA_BAWAAN.targetHari, muatanKg: muat === null ? muatanTerukur() : muat, muatanTerukur: muat === null, dariOwner: !!a };
}
export function susunAturBelanja(isi, w) {
  const kini = aturBelanja(); const data = { id: 'belanja', tanggal: w.tanggal, jam: w.jam };
  const baca = (k, syarat, teks) => { if (blKosong(isi[k])) { data[k] = kini[k]; return ''; } const n = Math.round(blAngka(isi[k])); if (!syarat(n)) return teks; data[k] = n; return ''; };
  const salah = baca('ambangHari', (n) => n >= 0 && n <= 60, 'Disarankan kalau habis dalam: 0–60 hari') || baca('targetHari', (n) => n > 0 && n <= 90, 'Belanja untuk berapa hari: 1–90 (tidak boleh nol)') || baca('muatanKg', (n) => n > 0 && n <= 30000, 'Muatan satu truk: 1–30.000 kg (tidak boleh nol)');
  if (salah) return { tolak: salah };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { aturL: null, kabar: 'Aturan belanja disimpan — disarankan bila habis ≤ ' + data.ambangHari + ' hari · belanja untuk ' + data.targetHari + ' hari · muatan truk ' + blKG(data.muatanKg), kabarAwas: false } };
}
export const hariHabis = (sisa, laju) => (!(sisa > 0) || !(laju > 0) ? null : Math.floor(sisa / laju + 1e-9));
export const kataHabis = (h) => (h === null ? 'belum ada gerak ' + JENDELA_LAJU_HARI + ' hari — tidak ditebak' : h <= 0 ? 'habis hari ini' : '±' + h + ' hari lagi');

/** Pesanan yang masih menunggu datang: status 'batal'/'datang' tersimpan menang; kalau tidak, DATANG bila ada kedatangan pemasok itu sesudah pesanan. */
export function pesananSemua() {
  const batch = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok));
  return ambilPesananPemasok().map((p) => { const sesudah = batch.filter((b) => String(b.pemasok || '').trim() === p.pemasok && ((b.tanggal || '') > (p.tanggal || '') || ((b.tanggal || '') === (p.tanggal || '') && (b.jam || '') > (p.jam || '')))).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.jam || '').localeCompare(String(b.jam || '')));
    const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : sesudah.length ? 'datang' : 'menunggu';
    return Object.assign({}, p, { status, datangTanggal: status === 'datang' ? (p.datangTanggal || (sesudah[0] ? sesudah[0].tanggal : '')) : '' }); }).sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0));
}
export const pesananMenunggu = () => pesananSemua().filter((p) => p.status === 'menunggu');

/** Tiap merek yang bisa dibeli: sisa & laju dari mesin, saran karung, harga terakhir per pemasok. */
export function daftarBelanja(kini) {
  const atur = aturBelanja(); const stok = hitungStokKarungPerMerk(); const laju = hitungLajuPakai().kgMerk || {}; const pem = daftarPemasok(); const menunggu = pesananMenunggu();
  const merks = new Set(Object.keys(stok)); pem.forEach((p) => Object.keys(p.hargaPerMerk).forEach((m) => merks.add(m)));
  const merk = Array.from(merks).map((m) => { const sisa = (stok[m] || {}).sisaKg || 0; const l = laju[m] || 0; const hari = hariHabis(sisa, l); const berat = merkPunyaKarungBerat(m, 50) ? 50 : merkPunyaKarungBerat(m, 25) ? 25 : 50;
    const butuh = l > 0 ? Math.max(0, l * atur.targetHari - sisa) : 0; const saranK = Math.ceil(butuh / berat);
    const sumber = pem.filter((p) => p.hargaPerMerk[m]).map((p) => ({ pemasok: p.nama, harga: p.hargaPerMerk[m].terakhir.hargaPerKg, tanggal: p.hargaPerMerk[m].terakhir.tanggal })).sort((a, b) => a.harga - b.harga);
    const dipesan = menunggu.find((p) => (p.baris || []).some((b) => b.merk === m)) || null;
    return { merk: m, sisa: Math.round(sisa * 100) / 100, laju: l, lajuTeks: String(Math.round(l * 10) / 10).replace('.', ','), hari, berat, saranK, perlu: hari !== null && hari <= atur.ambangHari && saranK > 0 && !dipesan, sumber, termurah: sumber[0] || null, dipesan, kritis: hari !== null && hari <= 2,
      sisaTeks: 'sisa ' + blKG(Math.round(sisa)) + (l > 0 ? ' · laku ' + String(Math.round(l * 10) / 10).replace('.', ',') + ' kg/hari' : '') + ' · ' + kataHabis(hari) }; })
    .filter((x) => x.sisa > 0 || x.laju > 0 || x.sumber.length);
  return { merk, pemasok: pem.filter((p) => p.kedatangan > 0).map((p) => ({ nama: p.nama, kunci: p.kunci, cara: p.caraBiasa, caraTeks: p.caraTeks, tempo: tempoPemasok(p.nama), kontak: p.kontak, orang: p.orang })), atur, tanpaPemasok: merk.filter((x) => !x.sumber.length).map((x) => x.merk), menunggu };
}
/** Daftar belanja yang sedang disusun: pesan = { merk: { p: pemasok, k: karung } }. Per pemasok: muatan, karung, perkiraan uang; truk; kertas; kalimat uang (bon vs tunai). */
export function hitungBelanja(pesan, kini) {
  const D = daftarBelanja(kini); const atur = D.atur; const P = pesan || {}; const kas = kasPada();
  const baris = D.merk.map((x) => { const o = P[x.merk] || null; const k = o && o.k > 0 ? Math.round(o.k) : 0; const sumber = (o && x.sumber.find((s) => s.pemasok === o.p)) || x.termurah || null;
    const kg = k * x.berat; const rp = sumber ? kg * sumber.harga : 0;
    return Object.assign({}, x, { k, kg, rp, sumber, adaHarga: !!sumber, hariSesudah: x.laju > 0 ? Math.floor((x.sisa + kg) / x.laju + 1e-9) : null,
      hargaTeks: sumber ? sumber.pemasok + ' · ' + RP(sumber.harga) + '/kg (harga ' + tanggalPendek(sumber.tanggal) + ')' + (x.sumber.length > 1 ? ' · ganti ›' : '') : 'belum pernah dibeli — pemasok & harganya belum diketahui',
      saranTeks: x.saranK > 0 ? 'saran ' + x.saranK + ' karung' : 'tambah', sesudahTeks: k && x.hariSesudah !== null ? 'jadi cukup ±' + x.hariSesudah + ' hari' : '', dipesanTeks: x.dipesan ? 'sudah dipesan ' + tanggalPendek(x.dipesan.tanggal) + ' — menunggu datang' : '' }); });
  const perP = D.pemasok.map((p) => { const d = baris.filter((b) => b.k > 0 && b.sumber && b.sumber.pemasok === p.nama); const kg = d.reduce((a, b) => a + b.kg, 0), rp = d.reduce((a, b) => a + b.rp, 0), karung = d.reduce((a, b) => a + b.k, 0);
    const uang = !karung ? '' : p.cara === 'bon' ? 'Biasanya BON — jadi utang ±' + RP(rp) + (p.tempo.hari > 0 ? ', jatuh tempo ±' + tanggalPendek(bpTambahHari(hariIniIso(kini || new Date()), p.tempo.hari)) + ' kalau datang hari ini' : ', tempo belum disepakati') + '. Yang tunai cuma ongkos bongkar.'
      : p.cara === 'tunai' ? 'Biasanya TUNAI — perlu ±' + RP(rp) + ' waktu barang datang. ' + (kas === null ? 'Uang toko belum bisa dihitung (titik kas belum disetel).' : 'Uang toko sekarang ' + RP(kas) + (rp > kas ? ' — KURANG ' + RP(rp - kas) + '.' : ' — cukup.')) : 'Belum ada kedatangan dari pemasok ini, jadi belum tahu biasanya bon atau tunai. Perkiraan ±' + RP(rp) + '.';
    return { pemasok: p.nama, kunci: p.kunci, cara: p.cara, caraTeks: p.caraTeks, tempo: p.tempo, kontak: p.kontak, d, kg, rp, karung, sisaMuat: atur.muatanKg > 0 ? atur.muatanKg - kg : 0, lebih: atur.muatanKg > 0 ? Math.max(0, kg - atur.muatanKg) : 0, uangTeks: uang, uangAwas: p.cara === 'tunai' && kas !== null && rp > kas,
      milik: baris.filter((b) => b.sumber && b.sumber.pemasok === p.nama), saran: baris.filter((b) => b.perlu && !b.k && b.sumber && b.sumber.pemasok === p.nama) }; });
  const totKarung = perP.reduce((a, r) => a + r.karung, 0), totKg = perP.reduce((a, r) => a + r.kg, 0), totRp = perP.reduce((a, r) => a + r.rp, 0);
  const perluSemua = baris.filter((b) => b.perlu && !b.k && b.termurah);
  const urutHari = (a, b) => (a.hari === null ? 999 : a.hari) - (b.hari === null ? 999 : b.hari);
  const kelompok = []; const tambah = (judul, ket, awas, d) => { if (d.length) kelompok.push({ judul, ket, awas, isi: d.slice().sort(urutHari) }); };
  tambah('Habis dalam ' + atur.ambangHari + ' hari', 'perlu dipesan', true, baris.filter((b) => !b.dipesan && b.hari !== null && b.hari <= atur.ambangHari));
  tambah('Masih aman', 'lebih dari ' + atur.ambangHari + ' hari', false, baris.filter((b) => !b.dipesan && b.hari !== null && b.hari > atur.ambangHari));
  tambah('Belum bisa dihitung', 'belum ada penjualan ' + JENDELA_LAJU_HARI + ' hari ini', false, baris.filter((b) => !b.dipesan && b.hari === null));
  tambah('Sudah dipesan', 'menunggu datang', false, baris.filter((b) => !!b.dipesan));
  const kertas = perP.map((r) => ({ pemasok: r.pemasok, kunci: r.kunci, karung: r.karung, kg: r.kg, rp: r.rp, lebih: r.lebih, sisaMuat: r.sisaMuat, muatanKg: atur.muatanKg,
    isi: baris.filter((b) => !b.dipesan && ((b.k > 0 && b.sumber && b.sumber.pemasok === r.pemasok) || (b.k === 0 && b.perlu && b.termurah && b.termurah.pemasok === r.pemasok))).sort(urutHari) })).filter((r) => r.isi.length);
  const lainnya = baris.filter((b) => !b.dipesan && b.k === 0 && !b.perlu && b.termurah).sort(urutHari);
  return { D, atur, baris, perP, totKarung, totKg, totRp, perluSemua, kelompok, kertas, lainnya, kas, ringkas: [{ a: baris.filter((b) => !b.dipesan && b.hari !== null && b.hari <= 2).length, l: 'habis ≤ 2 hari', nyala: true }, { a: baris.filter((b) => b.perlu).length, l: 'perlu dipesan', nyala: false }, { a: baris.filter((b) => b.dipesan).length, l: 'sudah dipesan', nyala: false }],
    legenda: 'Batang abu = stok cukup sampai hari ke berapa (penuh = 30 hari) · garis = ' + atur.ambangHari + ' hari · emas = tambahan dari pesanan', pesanTeks: totKarung ? totKarung + ' karung · ' + blKG(totKg) + ' · ±' + RP(totRp) : '', pesanKet: perP.filter((r) => r.karung).map((r) => r.pemasok + ' ' + r.karung).join(' · ') };
}
/** Truk satu pemasok: potongan bak berwarna per merek (label hanya bila tumpukannya cukup lebar). */
export function susunTruk(H, pemasok) {
  const R = H.perP.find((r) => r.pemasok === pemasok) || H.perP[0] || null; if (!R) return null; const muat = H.atur.muatanKg; const dasar = Math.max(muat, R.kg, 1);
  const bak = R.d.map((b, i) => { const bagian = b.kg / dasar; return { kelas: 'w' + (i % 6), t: bagian >= 0.2 ? b.merk.split(' ')[0].toUpperCase() + ' ' + b.k : bagian >= 0.07 ? String(b.k) : '', flex: Math.min(b.kg, muat || b.kg), merk: b.merk }; });
  if (!R.lebih && muat > 0) bak.push({ kelas: 'kosongbak', t: '', flex: Math.max(0, muat - Math.min(R.kg, muat)) });
  return { R, bak, lebih: R.lebih > 0, muatAngka: blKG(R.kg), muatDari: muat > 0 ? 'dari ' + blKG(muat) : '(muatan truk belum diketahui — isi di Atur)', muatSisa: muat <= 0 ? '' : R.lebih ? 'KELEBIHAN ' + blKG(R.lebih) + ' — tidak muat satu truk' : R.sisaMuat === 0 ? 'truknya penuh' : 'masih muat ' + blKG(R.sisaMuat) + ' · ' + Math.floor(R.sisaMuat / 50) + ' karung',
    bisaPenuhi: muat > 0 && R.sisaMuat >= 25 && R.milik.some((b) => b.laju > 0 && !b.dipesan), saranTeks: R.saran.length ? 'Pakai saran ' + R.saran.length + ' merek' : 'Tidak ada saran lagi' };
}
export const tulisPesan = (pesan, merk, p, k) => { const o = Object.assign({}, pesan || {}); if (k > 0) o[merk] = { p, k }; else delete o[merk]; return o; };
/** Penuhi truk: tambah karung satu-satu ke merek yang PALING CEPAT habis sesudah pesanan, sampai truknya penuh. Merek tanpa laju tidak ikut. */
export function penuhiTruk(H, pemasok, pesan) {
  const R = H.perP.find((r) => r.pemasok === pemasok); if (!R || !(H.atur.muatanKg > 0)) return { pesan: pesan || {}, tambahan: 0 };
  let o = Object.assign({}, pesan || {}); let kg = R.kg; const calon = R.milik.filter((b) => b.laju > 0 && !b.dipesan && (!o[b.merk] || o[b.merk].p === pemasok)).map((b) => ({ b, k: b.k })); let tambahan = 0;
  for (let i = 0; i < 400; i++) { const muat = calon.filter((c) => kg + c.b.berat <= H.atur.muatanKg); if (!muat.length) break; muat.sort((x, y) => (x.b.sisa + x.k * x.b.berat) / x.b.laju - (y.b.sisa + y.k * y.b.berat) / y.b.laju); muat[0].k += 1; kg += muat[0].b.berat; tambahan += 1; }
  calon.forEach((c) => { if (c.k > 0) o = tulisPesan(o, c.b.merk, pemasok, c.k); }); return { pesan: o, tambahan };
}
/** Pesan WhatsApp satu pemasok + dokumen pesananPemasok. Nomor dari kartu pemasok (0812… → 62812…); tanpa nomor WhatsApp yang bertanya ke siapa. */
export function susunPesanan(pesan, pemasok, w, waHarga) {
  const H = hitungBelanja(pesan, new Date(w.kini)); const R = H.perP.find((r) => r.pemasok === pemasok); if (!R) return { tolak: 'Pemasok itu tidak dikenal' }; if (!R.karung) return { tolak: 'Belum ada karung untuk ' + pemasok + ' di daftar' };
  const baris = ['*Pesanan Toko Beras M.IQBAL*', tanggalPendek(w.tanggal) + ' · untuk ' + R.pemasok].concat(R.d.map((b) => '• ' + b.merk + ' — ' + b.k + ' karung × ' + b.berat + ' kg')).concat(['Jumlah ' + R.karung + ' karung · ' + blKG(R.kg)]).concat(waHarga ? ['Perkiraan ' + RP(R.rp)] : []);
  const nomor = nomorWa(R.kontak); const tautan = 'https://wa.me/' + nomor + '?text=' + encodeURIComponent(baris.join('\n'));
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, pemasok: R.pemasok, baris: R.d.map((b) => ({ merk: b.merk, karung: b.k, berat: b.berat, kg: b.kg, hargaPerKg: b.sumber.harga })), karung: R.karung, kg: R.kg, rp: R.rp, status: 'menunggu', teks: baris.join('\n'), keNomor: nomor };
  const sisa = Object.assign({}, pesan || {}); R.d.forEach((b) => { delete sisa[b.merk]; });
  return { dokumen: [{ koleksi: 'pesananPemasok', data }], tautan, baris, pesanSisa: sisa, lebihTeks: R.lebih ? 'Pesanan ini ' + blKG(R.kg) + ' — lebih ' + blKG(R.lebih) + ' dari satu truk (' + blKG(H.atur.muatanKg) + '). Boleh, tapi berarti lebih dari satu kali antar.' : '', uangTeks: R.uangTeks,
    patch: { wa: null, kabar: 'Pesanan ' + R.pemasok + ' (' + R.karung + ' karung) dicatat sebagai menunggu datang' + (nomor ? ' · WhatsApp ke ' + R.kontak : ' · nomor pemasok belum ada di kartu — WhatsApp menanyakan tujuannya') + '. Dicocokkan dengan kedatangannya di Barang masuk.', kabarAwas: false } };
}
export function susunUbahPesanan(id, status, w) {
  const p = ambilPesananPemasok().find((x) => String(x.id) === String(id)); if (!p) return { tolak: 'Pesanan itu sudah tidak ada' }; if (status !== 'batal' && status !== 'datang') return { tolak: 'Keadaan tidak dikenal' };
  const data = Object.assign({}, p, { status, diubahTanggal: w.tanggal, diubahJam: w.jam }); if (status === 'datang') data.datangTanggal = w.tanggal;
  return { dokumen: [{ koleksi: 'pesananPemasok', data }], patch: { kabar: status === 'batal' ? 'Pesanan ' + p.pemasok + ' dibatalkan — mereknya bisa disarankan lagi' : 'Pesanan ' + p.pemasok + ' ditandai sudah datang', kabarAwas: false } };
}
