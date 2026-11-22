// TUTUP HARI DARI TABLET (owner 22 Nov 2026, paket ④ urutan layar tablet). Logika tanpa DOM; awalan hl. Dijaga alat-uji/uji_tutup_tablet.py.
// Keputusan owner 22 Nov 2026 (ditanya di depan):
//  1. Penjaga laci MENGHITUNG laci per pecahan di tablet lalu MENGIRIM hitungannya ke owner (persetujuan tindakan 'hitungLaci', rules v16 stafHitungLaci).
//     Akun tablet tidak pernah menulis tutupHari / titik kas / amplop / pindah uang / penyesuaian stok — itu ditulis OWNER saat menutup hari.
//  2. HITUNG BUTA: tablet tidak menampilkan angka "seharusnya", selisih, maupun alasan selisih. Owner melihatnya di HP; kalau perlu, owner MINTA HITUNG ULANG
//     (ditolak dengan alasan → terbaca di tablet).
//  3. Langkah lain di tablet: TIMBANG CEPAT (tiga beras karung yang paling banyak keluar — kg fisiknya ikut hitungan, penyesuaian stok ditulis owner),
//     CEK WADAH literan (sudah ada: wadahLiteran tipe 'cek', rules v5 — ditulis saat itu juga), AMANKAN LACI (tablet menyebut "pindahkan Rp… ke brankas" =
//     hitungan − uang kembalian setelan owner aturanToko/tutupHari, terbaca Penjaga laci sejak rules v16; Ben menandai sudah / tidak dipindah). Cek QRIS &
//     sisihkan laba tetap owner.
//  4. Owner MENYELESAIKAN LEMBAR: "Pakai hitungan ini" (hlTerapkan) mengisi lembar Tutup hari (laci, timbang, amankan); owner cek QRIS / lewati lalu Tutup →
//     hitungannya disetujui di kiriman yang sama (tutup-hari-logika susunTutup).
import { cacheMentah } from '../data/toko.js';
import { RP, KG, tanggalPendek, tanggalTutupAktif, hariIniIso } from '../inti/format.js';
import { aturTutup, barangTimbang, tdKiniDari, HL_TINDAKAN } from './tutup-hari-logika.js';
import { ugAngka } from './uang-logika.js';
import { wbCekHari } from './wadah-bernama-logika.js';

export { HL_TINDAKAN };
export const HL_STATUS = { menunggu: 'menunggu owner', disetujui: 'hari ditutup owner', ditolak: 'owner minta hitung ulang', dibaca: 'tidak dipakai owner' };
export const HL_BATAS = { alasan: 80, lembar: 100000 };
export const HL_DRAF_KOSONG = () => ({ buka: false, lembar: {}, receh: '', timbang: {}, amankan: '' });
const hlKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const hlB1 = (x) => Math.round(x * 10) / 10;
/** Rupiah bulat yang diketik (titik ribuan & "Rp" boleh); kosong = 0; bukan angka = NaN. */
export function hlRp(v) {
  if (hlKosong(v)) return 0; const t = String(v).replace(/rp/i, '').replace(/\s/g, '').replace(/\./g, '');
  return /^\d+$/.test(t) ? Number(t) : NaN;
}
const hlMilik = (m, akun) => !!akun && String(m.mintaUid || '') === String(akun.uid || '');
const hlUrut = (a, b) => String(b.pada || (b.tanggal + ' ' + b.jam) || '').localeCompare(String(a.pada || (a.tanggal + ' ' + a.jam) || ''));

/**
 * Lembar tablet dari draf d (HL_DRAF_KOSONG) pada saat `kini`. TANPA angka seharusnya / selisih (hitung buta).
 * → { iso, A, pecahan: [{ p, n, jumlah }], receh, hitung, tolakHitung, kembalian, amankanBisa, pindah, tinggal, timbang: [{ merk, sistem, fisik, teks }],
 *     tolakTimbang, cek: { aktif, dicek, belum } }
 */
export function hlHitung(draf, kini) {
  const d = Object.assign(HL_DRAF_KOSONG(), draf || {}); const iso = tanggalTutupAktif(kini || new Date()); const A = aturTutup();
  const pecahan = A.pecahan.map((p) => { const n = Math.max(0, Math.floor(Number((d.lembar || {})[p]) || 0)); return { p, n, jumlah: p * n }; });
  const receh = hlRp(d.receh); const hitung = pecahan.reduce((a, x) => a + x.jumlah, 0) + (receh > 0 ? receh : 0);
  const tolakHitung = !isFinite(receh) || isNaN(receh) ? 'Koin & receh hanya angka rupiah bulat (mis. 7500 atau 7.500)' : pecahan.some((x) => x.n > HL_BATAS.lembar) ? 'Jumlah lembar terlalu besar — periksa lagi ketikannya'
    : !(hitung > 0) ? 'Hitung uangnya dulu — isi jumlah lembar tiap pecahan' : hitung > 1000000000 ? 'Hitungan di atas Rp1 miliar — periksa lagi ketikannya' : '';
  // amankan laci: uang kembalian = angka OWNER (aturanToko/tutupHari, terbaca Penjaga laci sejak rules v16). Belum terbaca = tidak ditebak dari angka bawaan.
  const amankanBisa = A.dariOwner; const kembalian = A.kembalian; const pindah = amankanBisa ? Math.max(0, hitung - kembalian) : 0;
  const timbang = barangTimbang(iso).map((m) => { const x = (d.timbang || {})[m.merk]; const ada = !hlKosong(x); const fisik = ada ? hlB1(ugAngka(x)) : null;
    return { merk: m.merk, sistem: m.sistem, keluar: m.keluar, fisik, salah: ada && !(fisik >= 0 && /\d/.test(String(x))), teks: fisik === null ? 'belum ditimbang' : KG(fisik) }; });
  const tolakTimbang = timbang.some((m) => m.salah) ? 'Berat timbang hanya angka kg (mis. 48,5)' : '';
  const CW = wbCekHari(iso); const aktif = CW.daftar.filter((x) => x.aktif);
  return { iso, A, pecahan, receh: receh > 0 ? receh : 0, hitung, tolakHitung, kembalian, amankanBisa, pindah, tinggal: hitung - (d.amankan === 'sudah' ? pindah : 0), timbang, tolakTimbang,
    cek: { aktif: aktif.length, dicek: aktif.filter((x) => x.dicek).length, belum: CW.belum.slice() }, kalimatTanggal: iso !== hariIniIso(kini || new Date()) ? 'Lewat tengah malam: yang dihitung = hari dagang ' + tanggalPendek(iso) + ' (kemarin). Sebelum jam 12 siang masih menutup hari kemarin.' : '' };
}

/**
 * Kirim hitungan laci ke owner. akun = orang yang jaga (uid akun tablet, peran). Bentuk = rules v16 stafHitungLaci: tindakan 'hitungLaci', status 'menunggu',
 * mintaUid = penulis, hitung bulat 1..1 M, amankan bulat 0..hitung, tanggal = HARI YANG DITUTUP (lewat tengah malam sebelum jam 12 = kemarin), tanpa keputusan.
 */
export function hlSusunKirim(draf, akun, w) {
  const d = Object.assign(HL_DRAF_KOSONG(), draf || {});
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — hitungan laci butuh orang yang jaga' };
  if (akun.peran !== 'ben') return { tolak: 'Hitungan laci dikirim Penjaga laci' };
  const H = hlHitung(d, tdKiniDari(w)); if (H.tolakHitung) return { tolak: H.tolakHitung }; if (H.tolakTimbang) return { tolak: H.tolakTimbang };
  if (H.amankanBisa && H.pindah > 0 && d.amankan !== 'sudah' && d.amankan !== 'tidak') return { tolak: 'Amankan laci: sudah dipindah ' + RP(H.pindah) + ' ke brankas? Pilih Sudah atau Tidak dipindah' };
  const amankan = H.amankanBisa && d.amankan === 'sudah' ? H.pindah : 0;
  const ada = cacheMentah('persetujuan').find((m) => m.tindakan === HL_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && hlMilik(m, akun) && String(m.tanggal || '') === H.iso && Number(m.hitung) === H.hitung && Number(m.amankan) === amankan);
  if (ada) return { tolak: 'Hitungan yang sama (' + RP(H.hitung) + ', jam ' + (ada.jam || '?') + ') masih menunggu owner — tidak dikirim dua kali' };
  const lembar = {}; H.pecahan.forEach((x) => { if (x.n > 0) lembar[String(x.p)] = x.n; });
  const data = { id: w.idUnik(), tindakan: HL_TINDAKAN, status: 'menunggu', tanggal: H.iso, jam: w.jam, tanggalTulis: w.tanggal, hitung: H.hitung, lembar, receh: H.receh, amankan,
    kembalian: H.amankanBisa ? H.kembalian : null, timbang: H.timbang.filter((m) => m.fisik !== null).map((m) => ({ merk: m.merk, fisik: m.fisik, sistem: m.sistem })),
    cekWadah: { dicek: H.cek.dicek, aktif: H.cek.aktif }, mintaUid: String(akun.uid), dari: String(akun.nama || ''), peran: String(akun.peran || ''), pada: w.kini };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Hitungan laci ' + tanggalPendek(H.iso) + ' terkirim ke owner — ' + RP(H.hitung) + (amankan ? ' · ' + RP(amankan) + ' dipindah ke brankas, laci tinggal ' + RP(H.hitung - amankan) : '') + '. Owner yang menutup hari di HP.', kabarAwas: false } };
}

/** Satu baris tampilan hitungan laci (tablet & owner). */
export function hlBaris(m) {
  const st = m.status || 'menunggu'; const lembar = m.lembar || {};
  return { id: String(m.id), tanggal: String(m.tanggal || ''), jam: String(m.jam || ''), tanggalTulis: String(m.tanggalTulis || m.tanggal || ''), dari: String(m.dari || '?'),
    hitung: Math.round(Number(m.hitung) || 0), amankan: Math.round(Number(m.amankan) || 0), kembalian: m.kembalian === null || m.kembalian === undefined ? null : Number(m.kembalian) || 0,
    receh: Math.round(Number(m.receh) || 0), lembar: Object.keys(lembar).map((p) => ({ p: Number(p), n: Number(lembar[p]) || 0 })).filter((x) => x.p > 0 && x.n > 0).sort((a, b) => b.p - a.p),
    timbang: Array.isArray(m.timbang) ? m.timbang.map((t) => ({ merk: String(t.merk || ''), fisik: Number(t.fisik) || 0, sistem: Number(t.sistem) || 0 })) : [],
    cek: m.cekWadah ? { dicek: Number(m.cekWadah.dicek) || 0, aktif: Number(m.cekWadah.aktif) || 0 } : null,
    status: st, namaStatus: HL_STATUS[st] || st, alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || ''), tutupJam: String(m.tutupJam || ''),
    diputus: m.diputusTanggal ? tanggalPendek(m.diputusTanggal) + (m.diputusJam ? ' ' + m.diputusJam : '') : '' };
}
/** Hitungan laci dari akun ini: yang menunggu (semua) + yang sudah diputus dalam 7 hari, terbaru di atas. */
export function hlMilikSaya(akun, iso) {
  const batas = (() => { const t = new Date(String(iso || '').slice(0, 10) + 'T00:00:00Z'); if (!isFinite(t.getTime())) return ''; t.setUTCDate(t.getUTCDate() - 7); return t.toISOString().slice(0, 10); })();
  return cacheMentah('persetujuan').filter((m) => m.tindakan === HL_TINDAKAN && hlMilik(m, akun) && ((m.status || 'menunggu') === 'menunggu' || String(m.tanggal || '') >= batas)).sort(hlUrut).map(hlBaris);
}
/** Owner: hitungan laci yang menunggu untuk hari `iso` (terbaru di atas). */
export function hlMenungguHari(iso) {
  return cacheMentah('persetujuan').filter((m) => m.tindakan === HL_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && String(m.tanggal || '') === String(iso)).sort(hlUrut).map(hlBaris);
}
/** Owner: semua hitungan laci yang menunggu (hari mana pun) — untuk pita di Uang keluar & notifikasi. */
export function hlMenungguSemua() {
  return cacheMentah('persetujuan').filter((m) => m.tindakan === HL_TINDAKAN && (m.status || 'menunggu') === 'menunggu').sort(hlUrut).map(hlBaris);
}

/**
 * Owner "Pakai hitungan ini": patch draf Tutup hari dari hitungan tablet `id`. statusLama = draf.status yang sudah ada (cek QRIS / sisih tidak disentuh).
 * Laci = lembar & receh tablet (beres); timbang = kg tablet (beres bila semua barang lembar owner sudah ditimbang); amankan = angka tablet (beres) atau
 * DILEWATI (Ben tidak memindah — uangnya tetap di laci); dariHitung + jam & tanggal tulis = dasar uang laci yang tercatat sesudahnya.
 */
export function hlTerapkan(id, statusLama) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id) && x.tindakan === HL_TINDAKAN);
  if (!m) return { tolak: 'Hitungan laci itu tidak ditemukan' };
  if ((m.status || 'menunggu') !== 'menunggu') return { tolak: 'Hitungan laci itu sudah ' + (HL_STATUS[m.status] || m.status) };
  const b = hlBaris(m); const lembar = {}; b.lembar.forEach((x) => { lembar[x.p] = x.n; });
  const timbang = {}; b.timbang.forEach((t) => { timbang[t.merk] = String(t.fisik).replace('.', ','); });
  const perlu = barangTimbang(b.tanggal).map((x) => x.merk); const semuaDitimbang = perlu.length > 0 && perlu.every((mk) => timbang[mk] !== undefined);
  const status = Object.assign({}, statusLama || {}, { laci: 'beres', amankan: b.amankan > 0 ? 'beres' : 'lewat' }); if (semuaDitimbang) status.timbang = 'beres';
  return { patch: { lembar, receh: b.receh, timbang, status, dariHitung: b.id, hitungTgl: b.tanggalTulis, hitungJam: b.jam, hitungOleh: b.dari, amankanTetap: b.amankan > 0 ? b.amankan : null },
    kabar: 'Hitungan ' + b.dari + ' jam ' + b.jam + ' dipakai — ' + RP(b.hitung) + (b.amankan ? ' · ' + RP(b.amankan) + ' sudah di brankas' : ' · tidak dipindah ke brankas') + (perlu.length && !semuaDitimbang ? ' · timbang belum lengkap' : '') + '. Cek QRIS (atau lewati), lalu Tutup.' };
}
/** Owner melepas hitungan tablet dari draf (kembali ke hitungan sendiri). */
export function hlLepas(statusLama) {
  return { lembar: {}, receh: 0, timbang: {}, status: Object.assign({}, statusLama || {}, { laci: 'belum', timbang: 'belum', amankan: 'belum' }), dariHitung: null, hitungTgl: null, hitungJam: null, hitungOleh: null, amankanTetap: null };
}
/** Owner minta hitung ulang = hitungan ditolak dengan alasan (terbaca di tablet). */
export function hlSusunTolak(id, alasan, w) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id) && x.tindakan === HL_TINDAKAN);
  if (!m) return { tolak: 'Hitungan laci itu tidak ditemukan' };
  if ((m.status || 'menunggu') !== 'menunggu') return { tolak: 'Hitungan laci itu sudah ' + (HL_STATUS[m.status] || m.status) };
  const a = String(alasan === undefined || alasan === null ? '' : alasan).trim().slice(0, HL_BATAS.alasan); if (!a) return { tolak: 'Minta hitung ulang butuh alasan — supaya ' + (m.dari || 'yang jaga') + ' tahu apa yang dicari' };
  return { dokumen: [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: 'ditolak', alasanTolak: a, diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini }) }],
    patch: { kabar: 'Hitungan laci ' + (m.dari || 'tablet') + ' jam ' + (m.jam || '') + ' dikembalikan: ' + a + ' — kabarnya terbaca di tablet; hari belum ditutup', kabarAwas: false } };
}

/** Slip hitungan laci (teks polos → printer tablet). kop = { nama }; dicetak = { tanggal, jam, oleh }. Baris "label  nilai" = dua spasi pemisah. */
export function hlTeksCetak(b, kop, dicetak) {
  const K = kop || {}; const C = dicetak || {}; const g = [];
  g.push('HITUNGAN LACI · TUTUP HARI'); if (K.nama) g.push(String(K.nama).toUpperCase()); g.push('');
  g.push('Hari  ' + tanggalPendek(b.tanggal)); g.push('Dihitung  ' + b.dari + ' ' + (b.tanggalTulis && b.tanggalTulis !== b.tanggal ? tanggalPendek(b.tanggalTulis) + ' ' : '') + b.jam); g.push('');
  b.lembar.forEach((x) => g.push(RP(x.p).replace('Rp', '') + ' x ' + x.n + '  ' + RP(x.p * x.n))); if (b.receh) g.push('Koin & receh  ' + RP(b.receh));
  g.push('JUMLAH DIHITUNG  ' + RP(b.hitung));
  if (b.amankan) { g.push('Dipindah ke brankas  ' + RP(b.amankan)); g.push('Tinggal di laci  ' + RP(b.hitung - b.amankan)); } else g.push('Brankas  tidak dipindah');
  if (b.timbang.length) { g.push(''); g.push('Timbang cepat:'); b.timbang.forEach((t) => g.push(t.merk + '  ' + KG(t.fisik))); }
  if (b.cek) g.push('Cek wadah  ' + b.cek.dicek + ' dari ' + b.cek.aktif);
  g.push(''); g.push('Status  ' + b.namaStatus + (b.diputus ? ' ' + b.diputus : '')); if (b.alasan) g.push('Owner: ' + b.alasan); if (b.balasan) g.push('Owner: ' + b.balasan);
  if (C.tanggal) g.push('Dicetak ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', ' + C.oleh : ''));
  g.push(''); g.push('Paraf yang menghitung:'); g.push(''); g.push('(.............)');
  return g.join('\n');
}
