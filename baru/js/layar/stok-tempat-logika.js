// LAYAR STOK — TEMPAT SIMPAN (ST5-A "Denah Toko", dikunci owner 19 Sep 2026): di mana tiap beras & kemasan disimpan.
// Peta = dokumen pengaturan/tempatSimpan {peta: {kunci → nama tempat}} — dokumen yang SAMA dengan sistem lama (simpanTempatSimpan index.html 33143,
// kunci = jenis + ':' + id, jenis 'K' = karung), jadi kedua sistem membaca tempat yang sama. Peta BOLEH kosong dan barang boleh tanpa tempat (toko kecil hafal).
// Pindah = cuma catatan tempat — stok & HPP tidak berubah; tiap pindahan dicatat di koleksi baru pindahTempat.
// Daftar tempat + kotaknya di denah + batas "menumpuk" = setelan owner (aturanToko/tempat); tempat yang masih berisi tidak bisa dihapus.
// Menumpuk: tempat yang memegang nilai rak di atas batas % (memori rak-menumpuk-satu-merek: 42 % nilai di satu merek).
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { cacheMentah } from '../data/toko.js';
import { RP, ANGKA } from '../inti/format.js';

export const ATUR_TEMPAT_BAWAAN = { batasTumpuk: 50 };
export const POSISI_DENAH = [['', 'tanpa kotak'], ['atas', 'atas, lebar penuh'], ['kiri-atas', 'kiri atas'], ['kanan-atas', 'kanan atas'], ['kiri-bawah', 'kiri bawah'], ['tengah-bawah', 'tengah bawah'], ['kanan-bawah', 'kanan bawah'], ['bawah', 'bawah, lebar penuh']];
const KOTAK_DENAH = { atas: { x: 3, y: 3, w: 94, h: 42 }, 'kiri-atas': { x: 3, y: 3, w: 46, h: 42 }, 'kanan-atas': { x: 51, y: 3, w: 46, h: 42 }, 'kiri-bawah': { x: 3, y: 50, w: 30, h: 42 }, 'tengah-bawah': { x: 35, y: 50, w: 30, h: 42 }, 'kanan-bawah': { x: 67, y: 50, w: 30, h: 42 }, bawah: { x: 3, y: 50, w: 94, h: 42 } };
export const kunciTempat = (jenis, id) => String(jenis || 'K') + ':' + String(id || '');   // = kunciTempat index.html 33118
const tpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const tpKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';

/** Peta tempat (dokumen pengaturan/tempatSimpan); kosong = belum pernah diatur (bukan salah). */
export function petaTempat() { const d = cacheMentah('pengaturan').find((x) => String(x.id) === 'tempatSimpan'); return d && d.peta && typeof d.peta === 'object' ? Object.assign({}, d.peta) : {}; }
/** Daftar tempat = setelan owner (aturanToko/tempat) + nama yang sudah dipakai di peta (sistem lama: tempat cuma teks). */
export function aturTempat() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'tempat') || null;
  const daftar = (a && Array.isArray(a.daftar) ? a.daftar : []).map((t) => ({ nama: String(t.nama || '').trim(), posisi: KOTAK_DENAH[t.posisi] ? t.posisi : '' })).filter((t) => t.nama);
  Object.keys(petaTempat()).forEach((k) => { const nm = String(petaTempat()[k] || '').trim(); if (nm && !daftar.some((t) => t.nama === nm)) daftar.push({ nama: nm, posisi: '' }); });
  const batas = a && isFinite(Number(a.batasTumpuk)) && Number(a.batasTumpuk) > 0 && Number(a.batasTumpuk) <= 100 ? Number(a.batasTumpuk) : ATUR_TEMPAT_BAWAAN.batasTumpuk;
  return { daftar, batasTumpuk: batas, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
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
    const kotak = KOTAK_DENAH[t.posisi] || null;
    return { nama: t.nama, posisi: t.posisi, kotak, gaya: kotak ? 'left: ' + kotak.x + '%; top: ' + kotak.y + '%; width: ' + kotak.w + '%; height: ' + kotak.h + '%;' : '', isi, n: isi.length, kg, unit, nilai, pct, tumpuk: pct > atur.batasTumpuk,
      teksIsi: isi.length ? isi.map((b) => b.nama).join(', ') : 'kosong', teksJumlah: isi.length ? [kg > 0 ? tpKG(kg) : '', unit > 0 ? ANGKA(unit) + ' unit' : ''].filter(Boolean).join(' · ') : 'kosong', teksNilai: isi.length ? RP(Math.round(nilai)) + ' · ' + pct + ' % nilai rak' : '' }; });
  const tanpa = barang.filter((b) => !b.tempat || !atur.daftar.some((t) => t.nama === b.tempat));
  const tumpuk = tempat.filter((t) => t.tumpuk);
  return { atur, barang, tempat, zona: tempat.filter((t) => t.kotak), tanpaKotak: tempat.filter((t) => !t.kotak), nilaiSemua, tanpaTempat: { n: tanpa.length, isi: tanpa, teks: tanpa.length ? tanpa.map((b) => b.nama).join(', ') : '—' },
    tumpukKet: tumpuk.length ? tumpuk.map((t) => t.nama + ' ' + t.pct + ' %').join(', ') + ' memegang nilai rak di atas ' + atur.batasTumpuk + ' % (setelan owner) — menumpuk di satu tempat' : nilaiSemua > 0 ? 'Nilai rak tersebar, tidak ada tempat di atas ' + atur.batasTumpuk + ' %' : 'Belum ada nilai rak yang bertempat',
    kosong: !atur.daftar.length };
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
  const daftar = (Array.isArray(isi.daftar) ? isi.daftar : []).map((t) => ({ nama: String(t.nama || '').trim().slice(0, 40), posisi: KOTAK_DENAH[t.posisi] ? t.posisi : '' }));
  if (daftar.some((t) => !t.nama)) return { tolak: 'Nama tempat tidak boleh kosong — isi atau lepas barisnya' };
  const kembar = daftar.find((t, i) => daftar.findIndex((x) => x.nama.toLowerCase() === t.nama.toLowerCase()) !== i); if (kembar) return { tolak: 'Tempat "' + kembar.nama + '" tertulis dua kali' };
  const dobel = daftar.find((t, i) => t.posisi && daftar.findIndex((x) => x.posisi === t.posisi) !== i); if (dobel) return { tolak: 'Kotak "' + (POSISI_DENAH.find((p) => p[0] === dobel.posisi) || [])[1] + '" dipakai dua tempat — pilih kotak lain' };
  const berisi = barangTempat().filter((b) => b.tempat && !daftar.some((t) => t.nama === b.tempat));
  if (berisi.length) { const nm = berisi[0].tempat; return { tolak: 'Tempat "' + nm + '" masih berisi ' + berisi.filter((b) => b.tempat === nm).length + ' barang (' + berisi.filter((b) => b.tempat === nm).map((b) => b.nama).slice(0, 3).join(', ') + ') — pindahkan dulu, baru hapus tempatnya' }; }
  const batas = tpKosong(isi.batasTumpuk) ? aturTempat().batasTumpuk : Number(String(isi.batasTumpuk).replace(',', '.'));
  if (!(batas > 0 && batas <= 100)) return { tolak: 'Batas menumpuk harus 1–100 %' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tempat', tanggal: w.tanggal, jam: w.jam, daftar, batasTumpuk: batas } }],
    patch: { aturTp: null, kabar: 'Daftar tempat disimpan — ' + daftar.length + ' tempat (' + daftar.filter((t) => t.posisi).length + ' berkotak di denah) · menumpuk di atas ' + batas + ' %', kabarAwas: false } };
}
/** Pindahan pada satu hari, terbaru dulu. */
export function riwayatPindah(iso, n) { return cacheMentah('pindahTempat').filter((x) => !iso || x.tanggal === iso).sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 12); }
