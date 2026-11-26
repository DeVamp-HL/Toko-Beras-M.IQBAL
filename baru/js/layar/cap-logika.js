// CAP LANGGANAN (owner 26 Nov 2026, paket QR kedua: "adakan aja dulu, gua belum kepikiran" soal hadiahnya). Logika TANPA DOM. Dijaga alat-uji/uji_cap_langganan.py.
//
// Tiap NOTA atas nama pelanggan (nama dipilih / kartu NFC ditempel) sejak tanggal MULAI = satu cap — tanpa scan, tanpa koleksi baru. Tiap `penuh` cap = satu
// hadiah. Bentuk & besar hadiahnya BELUM diputuskan owner: setelan menyimpan keterangan hadiah (teks bebas, mis. "potongan Rp5.000") dan kasir memberikannya
// lewat jalan yang sudah ada (Potongan / bonus), lalu menandai nota itu "hadiah cap diberikan" (kolom capDitukar di baris nota — penjualan staf boleh membawa
// kolom tambahan, rules tidak berubah). Hadiah tersedia = cap penuh − hadiah yang sudah ditandai. Mesin uang tidak membaca kolom ini.
// Setelan: aturanToko/pelanggan › cap { mulai 'YYYY-MM-DD' ('' = belum dimulai), minRp (belanja minimal satu nota supaya dapat cap; 0 = semua nota), penuh
// (cap per hadiah), hadiah (keterangan) } — dokumen yang SUDAH dibaca tablet. Batas: cap dihitung dari nota di buku berjalan; sesudah tutup buku nota tahun
// lalu diarsip → cap mulai lagi dari nol (disebut di layar setelan).
import { cacheMentah, ambilPenjualan, kunciNota } from '../data/toko.js';
import { kunciPelanggan, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { RP } from '../inti/format.js';

export const CAP_BAWAAN = { mulai: '', minRp: 0, penuh: 10, hadiah: '' };
export const CAP_PENUH_BATAS = [2, 100];
const capIso = (t) => /^\d{4}-\d\d-\d\d$/.test(String(t || ''));
/** Setelan cap yang berlaku (bawaan ditimpa yang tersimpan & sah). */
export function capAtur() {
  const d = cacheMentah('aturan').find((x) => String(x.id) === 'pelanggan'); const c = d && d.cap && typeof d.cap === 'object' ? d.cap : {};
  const penuh = Number(c.penuh); const min = Number(c.minRp);
  return { mulai: capIso(c.mulai) ? String(c.mulai) : '', minRp: isFinite(min) && min >= 0 ? Math.round(min) : CAP_BAWAAN.minRp,
    penuh: Number.isInteger(penuh) && penuh >= CAP_PENUH_BATAS[0] && penuh <= CAP_PENUH_BATAS[1] ? penuh : CAP_BAWAAN.penuh, hadiah: String(c.hadiah || '').trim().slice(0, 80) };
}
/**
 * Cap satu pelanggan. null = cap belum dimulai / tanpa nama. Hasil { nama, n (cap), penuh, menuju (cap di putaran sekarang, 0…penuh-1), dapat (hadiah yang
 * sudah diraih), ditukar (hadiah yang sudah ditandai diberikan), tersedia (dapat − ditukar, ≥ 0), hadiah (keterangan owner) }. A = capAtur() bila sudah dibaca.
 */
export function capHitung(nama, A) {
  const S = A || capAtur(); const k = kunciPelanggan(nama); if (!S.mulai || !k) return null;
  const per = {};
  (ambilPenjualan() || []).forEach((p) => { if (!p || kunciPelanggan(p.namaPelanggan) !== k || String(p.tanggal || '') < S.mulai || !penjualanMasihBerlaku(p)) return;
    const g = kunciNota(p); const x = per[g] || (per[g] = { total: 0, ditukar: 0 }); x.total += Number(p.hargaTotal) || 0; x.ditukar = Math.max(x.ditukar, Math.round(Number(p.capDitukar) || 0)); });
  const nota = Object.keys(per).map((g) => per[g]);
  const n = nota.filter((x) => x.total > 0 && x.total >= S.minRp).length; const ditukar = nota.reduce((a, x) => a + x.ditukar, 0);
  const dapat = Math.floor(n / S.penuh);
  return { nama: String(nama).trim(), n, penuh: S.penuh, menuju: n % S.penuh, dapat, ditukar, tersedia: Math.max(0, dapat - ditukar), hadiah: S.hadiah };
}
/** Kalimat cap untuk layar & struk: "Cap langganan 7/10" (+ hadiah tersedia). '' = tidak ada. */
export function capTeks(C) {
  if (!C) return '';
  return 'Cap langganan ' + C.menuju + '/' + C.penuh + (C.tersedia > 0 ? ' · ' + C.tersedia + ' hadiah belum diberikan' + (C.hadiah ? ' (' + C.hadiah + ')' : '') : '');
}
/** Kalimat untuk lembar Bayar: cap sesudah nota ini tercatat (nota ini dihitung bila memenuhi belanja minimal). */
export function capTeksBayar(C, totalNota, A) {
  if (!C) return ''; const S = A || capAtur(); const dapatCap = totalNota > 0 && totalNota >= S.minRp;
  const n2 = C.n + (dapatCap ? 1 : 0); const sesudah = n2 % C.penuh; const penuhKini = dapatCap && sesudah === 0;
  return 'Cap ' + C.nama + ': ' + C.menuju + '/' + C.penuh + (dapatCap ? ' → nota ini jadi ' + (penuhKini ? C.penuh + '/' + C.penuh + ' — CAP PENUH, dapat hadiah' : sesudah + '/' + C.penuh)
    : ' · nota ini belum dapat cap (belanja minimal ' + RP(S.minRp) + ')');
}
/** Simpan setelan cap (owner, Pelanggan › Atur). isi = { mulai ('hari ini' iso / '' = berhenti), minRp (teks), penuh (teks), hadiah (teks) }.
 *  Dokumen aturanToko/pelanggan ditulis UTUH (kolom lain tetap) + cap. */
export function susunAturCap(isi, w) {
  const a = isi || {}; const kini = capAtur();
  const mulai = a.mulai === undefined ? kini.mulai : String(a.mulai || ''); if (mulai && !capIso(mulai)) return { tolak: 'Tanggal mulai cap tidak terbaca' };
  const angka = (v) => Number(String(v === undefined || v === null ? '' : v).replace(/[^\d]/g, ''));
  const minRp = String(a.minRp === undefined ? '' : a.minRp).trim() === '' ? kini.minRp : angka(a.minRp);
  const penuh = String(a.penuh === undefined ? '' : a.penuh).trim() === '' ? kini.penuh : angka(a.penuh);
  if (!(Number.isInteger(penuh) && penuh >= CAP_PENUH_BATAS[0] && penuh <= CAP_PENUH_BATAS[1])) return { tolak: 'Cap penuh: ' + CAP_PENUH_BATAS[0] + '–' + CAP_PENUH_BATAS[1] + ' cap per hadiah' };
  const hadiah = a.hadiah === undefined ? kini.hadiah : String(a.hadiah || '').trim().slice(0, 80);
  const d = cacheMentah('aturan').find((x) => String(x.id) === 'pelanggan');
  const data = Object.assign({}, d || { id: 'pelanggan' }, { id: 'pelanggan', tanggal: w.tanggal, jam: w.jam, cap: { mulai, minRp, penuh, hadiah } });
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { kabar: mulai ? 'Cap langganan berjalan sejak ' + mulai + ' · ' + penuh + ' cap = 1 hadiah' + (minRp > 0 ? ' · nota ≥ ' + RP(minRp) : '') + (hadiah ? ' · hadiah: ' + hadiah : ' · hadiah belum ditentukan') : 'Cap langganan dihentikan (cap yang sudah ada tidak dihapus)', kabarAwas: false } };
}
