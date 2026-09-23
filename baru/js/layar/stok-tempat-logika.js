// LAYAR STOK — TEMPAT SIMPAN (ST5-A "Denah Toko", dikunci owner 19 Sep 2026): di mana tiap beras & kemasan disimpan.
// Peta = dokumen pengaturan/tempatSimpan {peta: {kunci → nama tempat}} — dokumen yang SAMA dengan sistem lama (simpanTempatSimpan index.html 33143,
// kunci = jenis + ':' + id, jenis 'K' = karung), jadi kedua sistem membaca tempat yang sama. Peta BOLEH kosong dan barang boleh tanpa tempat (toko kecil hafal).
// Pindah = cuma catatan tempat — stok & HPP tidak berubah; tiap pindahan dicatat di koleksi baru pindahTempat.
// Daftar tempat + kotaknya di denah + batas "menumpuk" = setelan owner (aturanToko/tempat); tempat yang masih berisi tidak bisa dihapus.
// Menumpuk: tempat yang memegang nilai rak di atas batas % (memori rak-menumpuk-satu-merek: 42 % nilai di satu merek).
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { tumpukanGudang } from './jual-logika.js';
import { cacheMentah } from '../data/toko.js';
import { RP, ANGKA } from '../inti/format.js';

export const ATUR_TEMPAT_BAWAAN = { batasTumpuk: 50 };
/* DENAH dari foto toko 23 Sep (ruko memanjang; pintu depan = jalan di BAWAH denah, pintu belakang/rumah di ATAS): lorong ubin di tengah, tumpukan karung di kiri & kanan
   (kanan belakang paling tinggi), kotak wadah literan di mulut toko dengan deretan karung terbuka di belakangnya, pajangan kemasan 5–10 kg di kanan depan,
   meja & kursi di kanan, timbangan & troli di kiri depan, bangku di kedua sisi pintu. Kotak = persen dari lebar × tinggi denah (portrait 3 : 4). */
export const POSISI_DENAH = [['', 'tanpa kotak'], ['belakang', 'belakang · pintu rumah'], ['kiri-belakang', 'kiri belakang'], ['kanan-belakang', 'kanan belakang · tumpukan tinggi'], ['kiri-tengah', 'kiri tengah'], ['kanan-tengah', 'kanan tengah'],
  ['kiri-depan', 'kiri depan · timbangan & troli'], ['kanan-depan', 'kanan depan'], ['karung-terbuka', 'karung terbuka di belakang wadah'], ['pajangan', 'pajangan kemasan (kanan depan)'], ['wadah', 'kotak wadah literan (mulut toko)'], ['kasir', 'kasir · meja owner (kiri pintu)'], ['bangku-kanan', 'bangku kanan pintu']];
const KOTAK_DENAH = { belakang: { x: 3, y: 2, w: 94, h: 9 }, 'kiri-belakang': { x: 3, y: 13, w: 30, h: 19 }, 'kanan-belakang': { x: 67, y: 13, w: 30, h: 19 }, 'kiri-tengah': { x: 3, y: 34, w: 30, h: 19 }, 'kanan-tengah': { x: 67, y: 34, w: 30, h: 19 },
  'kiri-depan': { x: 3, y: 55, w: 30, h: 15 }, 'kanan-depan': { x: 67, y: 55, w: 30, h: 15 }, 'karung-terbuka': { x: 22, y: 72, w: 43, h: 8 }, pajangan: { x: 67, y: 72, w: 30, h: 17 }, wadah: { x: 22, y: 81.5, w: 43, h: 8 }, kasir: { x: 3, y: 72, w: 17, h: 17.5 }, 'bangku-kanan': { x: 82, y: 91, w: 15, h: 6 } };
/** Kunci kotak lama (denah 7 kotak putaran 16) dipetakan ke denah baru supaya setelan yang sudah tersimpan tidak hilang. */
const KOTAK_LAMA = { atas: 'belakang', 'kiri-atas': 'kiri-belakang', 'kanan-atas': 'kanan-belakang', 'kiri-bawah': 'kiri-depan', 'tengah-bawah': 'wadah', 'kanan-bawah': 'pajangan', bawah: 'karung-terbuka', meja: 'kanan-depan', 'bangku-kiri': 'kasir' };   // owner 23 Sep: kiri pintu = kasir & meja owner (foto 4687)
export const tpPosisi = (p) => { const k = String(p || ''); return KOTAK_DENAH[k] ? k : (KOTAK_LAMA[k] || ''); };
/** Daftar tempat BAWAAN (dari foto toko 23 Sep) — dipakai saat owner belum pernah menyimpan daftar tempat; owner bisa memakainya sebagai awal lewat Atur. */
export const TEMPAT_BAWAAN = [{ nama: 'Kiri belakang', posisi: 'kiri-belakang' }, { nama: 'Kanan belakang', posisi: 'kanan-belakang' }, { nama: 'Kiri tengah', posisi: 'kiri-tengah' }, { nama: 'Kanan tengah', posisi: 'kanan-tengah' },
  { nama: 'Kiri depan', posisi: 'kiri-depan' }, { nama: 'Kanan depan', posisi: 'kanan-depan' }, { nama: 'Karung terbuka', posisi: 'karung-terbuka' }, { nama: 'Pajangan kemasan', posisi: 'pajangan' }, { nama: 'Wadah literan', posisi: 'wadah' }, { nama: 'Belakang', posisi: 'belakang' }];
/** Perabot tetap yang digambar di denah (bukan tempat simpan): lorong, pintu depan & belakang, ubin. */
export const PERABOT_DENAH = [{ id: 'lorong', nama: 'lorong', x: 35, y: 13, w: 30, h: 57 }, { id: 'pintu-belakang', nama: 'pintu rumah', x: 40, y: 0, w: 20, h: 1.6 }, { id: 'pintu-depan', nama: 'PINTU DEPAN · JALAN', x: 22, y: 97.5, w: 56, h: 2.5 }, { id: 'teras', nama: 'teras', x: 3, y: 91, w: 76, h: 6 }];
export const kunciTempat = (jenis, id) => String(jenis || 'K') + ':' + String(id || '');   // = kunciTempat index.html 33118
const tpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const tpKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';

/** Peta tempat (dokumen pengaturan/tempatSimpan); kosong = belum pernah diatur (bukan salah). */
export function petaTempat() { const d = cacheMentah('pengaturan').find((x) => String(x.id) === 'tempatSimpan'); return d && d.peta && typeof d.peta === 'object' ? Object.assign({}, d.peta) : {}; }
/** Daftar tempat = setelan owner (aturanToko/tempat) + nama yang sudah dipakai di peta (sistem lama: tempat cuma teks). */
export function aturTempat() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'tempat') || null;
  const daftar = (a && Array.isArray(a.daftar) ? a.daftar : []).map((t) => ({ nama: String(t.nama || '').trim(), posisi: tpPosisi(t.posisi) })).filter((t) => t.nama);
  if (!a) TEMPAT_BAWAAN.forEach((t) => { if (!daftar.some((x) => x.nama.toLowerCase() === t.nama.toLowerCase())) daftar.push({ nama: t.nama, posisi: t.posisi }); });   // belum diatur owner → denah bawaan dari foto toko
  Object.keys(petaTempat()).forEach((k) => { const nm = String(petaTempat()[k] || '').trim(); if (nm && !daftar.some((t) => t.nama === nm)) daftar.push({ nama: nm, posisi: '' }); });
  const batas = a && isFinite(Number(a.batasTumpuk)) && Number(a.batasTumpuk) > 0 && Number(a.batasTumpuk) <= 100 ? Number(a.batasTumpuk) : ATUR_TEMPAT_BAWAAN.batasTumpuk;
  const susunan = a && a.susunan && typeof a.susunan === 'object' ? a.susunan : {};
  return { daftar, batasTumpuk: batas, susunan, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
/** Barang yang punya tempat: tiap nama beras (karung) & kemasan jadi yang bersisa, atau yang sudah punya tempat di peta. */
export function barangTempat() {
  const peta = petaTempat(); const stokK = hitungStokKarungPerMerk(); const stokM = hitungStokKemasan(); const out = [];
  Object.keys(stokK).sort().forEach((m) => { const k = kunciTempat('K', m); const sisa = stokK[m].sisaKg || 0; if (sisa <= 0.05 && !peta[k]) return;
    out.push({ kunci: k, jenis: 'karung', nama: m, sisa, satuan: 'kg', teksSisa: tpKG(sisa), nilai: Math.max(0, sisa) * (stokK[m].hppTerakhirPerKg || 0), tempat: String(peta[k] || '') }); });
  Object.keys(stokM).sort().forEach((kk) => { const st = stokM[kk]; const k = kunciTempat('M', kunciKemasan(st.namaProduk, st.ukuranKemasan)); const sisa = st.sisaUnit || 0; if (sisa <= 0 && !peta[k]) return;
    out.push({ kunci: k, jenis: 'kemasan', nama: st.namaProduk + ' ' + String(st.ukuranKemasan).replace('.', ',') + ' kg', sisa, satuan: 'unit', teksSisa: ANGKA(sisa) + ' unit', nilai: Math.max(0, sisa) * (st.hppRataRataPerUnit || 0), tempat: String(peta[k] || '') }); });
  return out;
}
/** Susun denah & daftar tempat: isi tiap tempat, nilai & persen rak, menumpuk, yang tanpa kotak, yang tanpa tempat. */
export function susunTempat() {
  const atur = aturTempat(); const barang = barangTempat(); const nilaiSemua = barang.reduce((a, b) => a + b.nilai, 0);
  const tempat = atur.daftar.map((t) => { const isi = barang.filter((b) => b.tempat === t.nama); const nilai = isi.reduce((a, b) => a + b.nilai, 0); const pct = nilaiSemua > 0 ? Math.round(nilai / nilaiSemua * 100) : 0; const kg = isi.filter((b) => b.jenis === 'karung').reduce((a, b) => a + b.sisa, 0); const unit = isi.filter((b) => b.jenis === 'kemasan').reduce((a, b) => a + b.sisa, 0);
    const kotak = KOTAK_DENAH[tpPosisi(t.posisi)] || null;
    return { nama: t.nama, posisi: t.posisi, kotak, gaya: kotak ? 'left: ' + kotak.x + '%; top: ' + kotak.y + '%; width: ' + kotak.w + '%; height: ' + kotak.h + '%;' : '', isi, n: isi.length, kg, unit, nilai, pct, tumpuk: pct > atur.batasTumpuk,
      teksIsi: isi.length ? isi.map((b) => b.nama).join(', ') : 'kosong', teksJumlah: isi.length ? [kg > 0 ? tpKG(kg) : '', unit > 0 ? ANGKA(unit) + ' unit' : ''].filter(Boolean).join(' · ') : 'kosong', teksNilai: isi.length ? RP(Math.round(nilai)) + ' · ' + pct + ' % nilai rak' : '' }; });
  const tanpa = barang.filter((b) => !b.tempat || !atur.daftar.some((t) => t.nama === b.tempat));
  const tumpuk = tempat.filter((t) => t.tumpuk);
  return { atur, barang, tempat, zona: tempat.filter((t) => t.kotak), tanpaKotak: tempat.filter((t) => !t.kotak), nilaiSemua, tanpaTempat: { n: tanpa.length, isi: tanpa, teks: tanpa.length ? tanpa.map((b) => b.nama).join(', ') : '—' },
    tumpukKet: tumpuk.length ? tumpuk.map((t) => t.nama + ' ' + t.pct + ' %').join(', ') + ' memegang nilai rak di atas ' + atur.batasTumpuk + ' % (setelan owner) — menumpuk di satu tempat' : nilaiSemua > 0 ? 'Nilai rak tersebar, tidak ada tempat di atas ' + atur.batasTumpuk + ' %' : 'Belum ada nilai rak yang bertempat',
    kosong: !atur.daftar.length, perabot: PERABOT_DENAH,
    // kotak denah yang belum dipakai tempat mana pun: digambar samar sebagai petunjuk letak (bukan tempat simpan) — supaya denah tetap terbaca sebagai toko walau daftar owner baru satu-dua tempat
    kotakKosong: POSISI_DENAH.filter((p) => p[0] && !tempat.some((t) => tpPosisi(t.posisi) === p[0])).map((p) => { const k = KOTAK_DENAH[p[0]]; return { posisi: p[0], nama: p[1].split(' · ')[0], gaya: 'left: ' + k.x + '%; top: ' + k.y + '%; width: ' + k.w + '%; height: ' + k.h + '%;' }; }) };
}
/** Pindah satu barang ke tempat (nama) atau '' = tanpa tempat. Menulis peta yang sama dengan sistem lama + catatan pindahan. */
export function susunPindah(kunci, keNama, w) {
  const brg = barangTempat().find((b) => b.kunci === kunci); if (!brg) return { tolak: 'Barang itu tidak ada di buku' };
  const ke = String(keNama || '').trim(); const atur = aturTempat();
  if (ke && !atur.daftar.some((t) => t.nama === ke)) return { tolak: 'Tempat "' + ke + '" belum ada di daftar tempat — tambahkan lewat Atur' };
  if ((brg.tempat || '') === ke) return { tolak: brg.nama + ' memang sudah di ' + (ke || 'tanpa tempat') };
  const peta = petaTempat(); if (ke) peta[kunci] = ke; else delete peta[kunci];   // dikosongkan = kuncinya DIBUANG (index.html 33141)
  return { dokumen: [{ koleksi: 'pengaturan', data: { id: 'tempatSimpan', peta, diubahPada: w.kini || new Date().toISOString() } },
    { koleksi: 'pindahTempat', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, kunci, barang: brg.nama, dari: brg.tempat || '', ke } }],
    patch: { tp: { pilih: null, tempat: ke || '' }, kabar: brg.nama + ' dipindah: ' + (brg.tempat || 'tanpa tempat') + ' → ' + (ke || 'tanpa tempat') + ' — cuma catatan tempat, stok & modal tidak berubah', kabarAwas: false } };
}
/** Simpan daftar tempat (nama + kotak di denah) & batas menumpuk. Tempat yang masih berisi tidak bisa dihapus. */
export function susunAturTempat(isi, w) {
  const daftar = (Array.isArray(isi.daftar) ? isi.daftar : []).map((t) => ({ nama: String(t.nama || '').trim().slice(0, 40), posisi: tpPosisi(t.posisi) }));
  if (daftar.some((t) => !t.nama)) return { tolak: 'Nama tempat tidak boleh kosong — isi atau lepas barisnya' };
  const kembar = daftar.find((t, i) => daftar.findIndex((x) => x.nama.toLowerCase() === t.nama.toLowerCase()) !== i); if (kembar) return { tolak: 'Tempat "' + kembar.nama + '" tertulis dua kali' };
  const dobel = daftar.find((t, i) => t.posisi && daftar.findIndex((x) => x.posisi === t.posisi) !== i); if (dobel) return { tolak: 'Kotak "' + (POSISI_DENAH.find((p) => p[0] === dobel.posisi) || [])[1] + '" dipakai dua tempat — pilih kotak lain' };
  const berisi = barangTempat().filter((b) => b.tempat && !daftar.some((t) => t.nama === b.tempat));
  // tempat yang masih berisi: ketukan pertama DITANYA, ketukan kedua barangnya jadi TANPA TEMPAT (owner 23 Sep: tempat coba-coba "atas" harus bisa dihapus; stok & modal tidak berubah)
  if (berisi.length && !isi.yakin) { const nm = berisi[0].tempat; return { tolak: 'Tempat "' + nm + '" masih berisi ' + berisi.filter((b) => b.tempat === nm).length + ' barang (' + berisi.filter((b) => b.tempat === nm).map((b) => b.nama).slice(0, 3).join(', ') + ') — ketuk SIMPAN sekali lagi: barangnya jadi tanpa tempat (stok tidak berubah), atau pindahkan dulu', perluYakin: true }; }
  const batas = tpKosong(isi.batasTumpuk) ? aturTempat().batasTumpuk : Number(String(isi.batasTumpuk).replace(',', '.'));
  if (!(batas > 0 && batas <= 100)) return { tolak: 'Batas menumpuk harus 1–100 %' };
  const susunan = Object.assign({}, aturTempat().susunan, isi.susunan && typeof isi.susunan === 'object' ? isi.susunan : {});
  const dokumen = [{ koleksi: 'aturanToko', data: { id: 'tempat', tanggal: w.tanggal, jam: w.jam, daftar, batasTumpuk: batas, susunan } }];
  if (berisi.length) { const peta = petaTempat(); berisi.forEach((b) => { delete peta[b.kunci]; dokumen.push({ koleksi: 'pindahTempat', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, kunci: b.kunci, barang: b.nama, dari: b.tempat, ke: '', tempatDihapus: true } }); });
    dokumen.push({ koleksi: 'pengaturan', data: { id: 'tempatSimpan', peta, diubahPada: w.kini || new Date().toISOString() } }); }
  return { dokumen,
    patch: { aturTp: null, kabar: 'Daftar tempat disimpan — ' + daftar.length + ' tempat (' + daftar.filter((t) => t.posisi).length + ' berkotak di denah) · menumpuk di atas ' + batas + ' %' + (berisi.length ? ' · ' + berisi.length + ' barang jadi tanpa tempat' : ''), kabarAwas: false } };
}
/** Pindahan pada satu hari, terbaru dulu. */
export function riwayatPindah(iso, n) { return cacheMentah('pindahTempat').filter((x) => !iso || x.tanggal === iso).sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 12); }

// ==================== SUSUNAN TUMPUKAN 3D (owner 23 Sep: "3D tata letak tumpukan beras yang bisa diatur posisinya") ====================
// Denah yang sama digambar isometrik: tiap tempat = lantai, tiap barang di tempat itu = TUMPUKAN karung (tinggi = banyak karung menurut rantai stok:
// buku − karung terbuka − isi wadah = tumpukanGudang; kemasan = tumpukan per 5 unit). Urutan tumpukan di dalam satu tempat = setelan owner
// (aturanToko/tempat.susunan {kunci: urut}); pindah tempat = peta yang sama dengan denah. Angka dari mesin — layar hanya menyusun letaknya.
const TP_DALAM = 100 * 4 / 3;   // denah portrait 3 : 4 → dunia 100 × 133,3
export const TP_LAPIS_MAKS = 12;
export function susunTumpukan() {
  const T = susunTempat(); const urut = T.atur.susunan || {}; const stok = hitungStokKarungPerMerk();
  const tumpuk = (b) => { if (b.jenis !== 'karung') return Math.max(b.sisa > 0 ? 1 : 0, Math.ceil(b.sisa / 5)); const g = tumpukanGudang(b.nama); if (g.adaBuku) return Math.max(0, g.karung); const st = stok[b.nama]; return Math.max(0, Math.floor((b.sisa + 0.0001) / 50)); };
  let totalKarung = 0;
  const jadikan = (b, i, x, y) => { const n = tumpuk(b); if (b.jenis === 'karung') totalKarung += n; return { kunci: b.kunci, nama: b.nama, jenis: b.jenis, sisa: b.sisa, teksSisa: b.teksSisa, nilai: b.nilai, karung: n, lapis: Math.min(TP_LAPIS_MAKS, n), lebih: Math.max(0, n - TP_LAPIS_MAKS), kosong: n === 0, x, y, urut: i,
    teks: b.jenis === 'karung' ? (n ? n + ' karung' : 'kurang dari 1 karung') + ' · ' + b.teksSisa : b.teksSisa }; };
  const zona = T.tempat.filter((t) => t.kotak).map((t) => { const k = t.kotak; const kol = k.w >= 60 ? 6 : k.w >= 40 ? 4 : k.w >= 26 ? 3 : 2; const isi = t.isi.slice().sort((a, b) => ((urut[a.kunci] === undefined ? 999 : urut[a.kunci]) - (urut[b.kunci] === undefined ? 999 : urut[b.kunci])) || a.nama.localeCompare(b.nama));
    const baris = Math.max(1, Math.ceil(isi.length / kol)); const d = k.h * TP_DALAM / 100;
    const stacks = isi.map((b, i) => { const c = i % kol, r = Math.floor(i / kol); return jadikan(b, i, k.x + (c + 0.5) * k.w / kol, k.y * TP_DALAM / 100 + (r + 0.5) * d / baris); });
    return { nama: t.nama, posisi: tpPosisi(t.posisi), x: k.x, y: k.y * TP_DALAM / 100, w: k.w, d, n: isi.length, teksJumlah: t.teksJumlah, teksNilai: t.teksNilai, tumpuk: t.tumpuk, stacks, kol }; });
  const tanpa = T.tanpaTempat.isi.map((b, i) => jadikan(b, i, 0, 0));
  return { zona, tanpaTempat: tanpa, perabot: PERABOT_DENAH.map((f) => Object.assign({}, f, { y: f.y * TP_DALAM / 100, d: f.h * TP_DALAM / 100 })), lebar: 100, dalam: TP_DALAM, totalKarung, nilaiSemua: T.nilaiSemua, kosong: T.kosong, tumpukKet: T.tumpukKet };
}
/** Kotak denah yang belum jadi tempat (untuk digambar samar di 3D; ketuk = jadikan tempat). */
export function kotakBelumDipakai() { const T = susunTempat(); return T.kotakKosong.map((z) => { const k = KOTAK_DENAH[z.posisi]; return { posisi: z.posisi, nama: z.nama, x: k.x, y: k.y * TP_DALAM / 100, w: k.w, d: k.h * TP_DALAM / 100 }; }); }
/** Jadikan satu kotak denah sebagai tempat baru (nama = nama kotaknya, huruf besar di depan) — menambah daftar owner, sisanya tetap. */
export function susunTempatBaru(posisi, w) {
  const p = tpPosisi(posisi); if (!p) return { tolak: 'Kotak denah tidak dikenal' }; const A = aturTempat(); if (A.daftar.some((t) => tpPosisi(t.posisi) === p)) return { tolak: 'Kotak itu sudah dipakai tempat lain' };
  const label = (POSISI_DENAH.find((x) => x[0] === p) || [p, p])[1].split(' · ')[0]; let nama = label.charAt(0).toUpperCase() + label.slice(1); let n = 2; while (A.daftar.some((t) => t.nama.toLowerCase() === nama.toLowerCase())) nama = label + ' ' + (n++);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tempat', tanggal: w.tanggal, jam: w.jam, daftar: A.daftar.concat([{ nama, posisi: p }]), batasTumpuk: A.batasTumpuk, susunan: A.susunan } }], nama, patch: { kabar: 'Tempat baru "' + nama + '" dibuat dari kotak denah', kabarAwas: false } };
}
/** Geser satu tumpukan satu langkah (arah −1 / +1) di dalam tempatnya — menulis urutan seluruh isi tempat itu ke aturanToko/tempat.susunan. */
export function susunGeserTumpukan(kunci, arah, w) {
  const T3 = susunTumpukan(); const z = T3.zona.find((zz) => zz.stacks.some((st) => st.kunci === kunci)); if (!z) return { tolak: 'Tumpukan itu tidak berada di tempat berkotak' };
  const i = z.stacks.findIndex((st) => st.kunci === kunci); const j = i + (Number(arah) < 0 ? -1 : 1); if (j < 0 || j >= z.stacks.length) return { tolak: 'Sudah di ujung' };
  const daftar = z.stacks.map((st) => st.kunci); const t = daftar[i]; daftar[i] = daftar[j]; daftar[j] = t;
  const A = aturTempat(); const susunan = Object.assign({}, A.susunan); daftar.forEach((k, n) => { susunan[k] = n; });
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tempat', tanggal: w.tanggal, jam: w.jam, daftar: A.daftar, batasTumpuk: A.batasTumpuk, susunan } }], patch: { kabar: z.stacks[i].nama + ' digeser ' + (Number(arah) < 0 ? 'ke depan' : 'ke belakang') + ' di ' + z.nama + ' — cuma letak, stok tidak berubah', kabarAwas: false } };
}
/** Titik isometrik: x ke kanan-bawah, y (dalam) ke kiri-bawah, z ke atas. Dipakai layar untuk menggambar; ada di sini supaya bisa diuji. */
export const tpIso = (x, y, z) => ({ sx: Math.round((x - y) * 0.866 * 100) / 100, sy: Math.round(((x + y) * 0.5 - (z || 0)) * 100) / 100 });
