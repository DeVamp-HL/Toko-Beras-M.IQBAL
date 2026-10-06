// FOTO BON PEMASOK (owner 7 Okt 2026: "buatkan fitur foto BON kalo bisa") — logika tanpa DOM, awalan fbn (bundel uji satu lingkup).
// Kertas bon pemasok difoto (kamera HP) atau dipilih dari galeri, DIKECILKAN DI PERANGKAT (kanvas: sisi panjang ≤ 1600 px, JPEG mutu ±0,6, target ≤ 300 KB;
// kalau masih besar mutu diturunkan, lalu ukurannya) dan disimpan sebagai satu dokumen per foto di koleksi Firestore TERPISAH `fotoBon`
// { id, idBon, pemasok, tanggal, jam, jenis 'image/jpeg', base64, lebar, tinggi, byte } (+ oleh/olehUid/perangkat dari penulis). Firebase Storage TIDAK
// dipakai (paket Spark). Koleksi ini TIDAK didengar terus-menerus: dibaca sekali saat lembar bon dibuka (tidak menambah baca penuh harian), tidak ikut
// cache TOKO aplikasi (toko.js) maupun cadangan berkas (foto ±300 KB per lembar — cadangan & baca penuh harian WAJIB melewatinya). JUJURNYA: Firestore
// sendiri memakai persistentLocalCache (firebase.js), jadi foto yang pernah DIBACA dan foto yang MENUNGGU dikirim tetap tersimpan di IndexedDB perangkat
// (dibersihkan Firestore sendiri sesuai batas cache bawaannya, ±40 MB). Foto yang menunggu server (kiriman belum diakui) dibatasi FBN_ANTRE_MAKS dan
// TIDAK disebut tersimpan sampai server mengakuinya (atau menolaknya — fotonya lalu dibuang dari daftar dengan kabar). Owner saja (Harga & Pemasok = layar owner).
// Alat gambar (kanvas peramban) DISERAHKAN pemanggil (`alat`), supaya pengecil & penyimpan diuji di jsc dengan kanvas tiruan.
import { tanggalPendek } from '../inti/format.js';

export const FBN_KOLEKSI = 'fotoBon';
export const FBN_SISI = 1600;                       // sisi panjang paling besar (px)
export const FBN_MUTU = [0.6, 0.5, 0.42, 0.35];     // mutu JPEG yang dicoba berurutan
export const FBN_SKALA = [1, 0.8, 0.64, 0.5];       // sesudah mutu terendah masih besar: sisi panjang dikecilkan lagi
export const FBN_TARGET = 300 * 1024;               // sasaran ukuran satu foto (byte JPEG)
export const FBN_BATAS = 700 * 1024;                // batas keras: base64 ±933 KB < 1 MiB dokumen Firestore
export const FBN_PALING_BANYAK = 6;                 // foto per bon
export const FBN_ANTRE_MAKS = 1;                    // foto yang boleh MENUNGGU server sekaligus (sinyal lambat) — yang berikutnya ditolak sampai yang ini diakui
const fbnB = (n) => Math.round(n);
/** Ukuran sesudah dikecilkan: sisi panjang ≤ sisi (tidak pernah dibesarkan). */
export function fbnUkuran(lebar, tinggi, sisi) {
  const L = Math.max(1, fbnB(Number(lebar) || 0)); const T = Math.max(1, fbnB(Number(tinggi) || 0)); const S = Math.max(1, fbnB(Number(sisi) || FBN_SISI));
  const panjang = Math.max(L, T); const skala = panjang > S ? S / panjang : 1;
  return { lebar: Math.max(1, fbnB(L * skala)), tinggi: Math.max(1, fbnB(T * skala)), skala };
}
/** Byte sebenarnya dari isi base64 (tanpa awalan data:). */
export function fbnByte(b64) { const s = String(b64 || ''); if (!s) return 0; const pad = s.endsWith('==') ? 2 : s.endsWith('=') ? 1 : 0; return Math.floor(s.length * 3 / 4) - pad; }
/** Pisah data URL → { jenis, base64 } (null bila bukan data URL base64 gambar). */
export function fbnPisahDataUrl(url) {
  const m = /^data:(image\/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)$/.exec(String(url || '')); return m ? { jenis: m[1], base64: m[2] } : null;
}
export const fbnKB = (byte) => String(Math.round((Number(byte) || 0) / 102.4) / 10).replace('.', ',') + ' KB';
export const fbnSrc = (d) => 'data:' + (d && d.jenis ? d.jenis : 'image/jpeg') + ';base64,' + (d && d.base64 ? d.base64 : '');
/**
 * Kecilkan satu gambar. alat = { buka(sumber) → Promise<{ lebar, tinggi, gambar }>, jpeg(gambar, lebar, tinggi, mutu) → data URL (string) }.
 * Mencoba mutu FBN_MUTU dulu di ukuran FBN_SISI, lalu skala FBN_SKALA; berhenti di yang pertama ≤ FBN_TARGET. Tidak ada yang ≤ target tapi yang terkecil
 * ≤ FBN_BATAS → dipakai (lebihTarget). Masih di atas batas → { tolak }. → { jenis, base64, byte, lebar, tinggi, mutu, coba, lebihTarget }.
 */
export async function fbnKecilkan(sumber, alat) {
  if (!alat || typeof alat.buka !== 'function' || typeof alat.jpeg !== 'function') return { tolak: 'Alat pengecil gambar tidak tersedia di perangkat ini' };
  let asal; try { asal = await alat.buka(sumber); } catch (e) { return { tolak: 'Berkas itu tidak bisa dibuka sebagai gambar' + (e && e.message ? ' (' + e.message + ')' : '') }; }
  if (!asal || !(Number(asal.lebar) > 0) || !(Number(asal.tinggi) > 0)) return { tolak: 'Berkas itu tidak bisa dibuka sebagai gambar' };
  let terkecil = null; let coba = 0;
  for (const sk of FBN_SKALA) {
    const U = fbnUkuran(asal.lebar, asal.tinggi, FBN_SISI * sk);
    for (const q of FBN_MUTU) {
      coba += 1; const p = fbnPisahDataUrl(alat.jpeg(asal.gambar, U.lebar, U.tinggi, q)); if (!p) continue;
      const hasil = { jenis: p.jenis, base64: p.base64, byte: fbnByte(p.base64), lebar: U.lebar, tinggi: U.tinggi, mutu: q, coba, asalLebar: fbnB(asal.lebar), asalTinggi: fbnB(asal.tinggi) };
      if (hasil.byte <= FBN_TARGET) return Object.assign(hasil, { lebihTarget: false });
      if (!terkecil || hasil.byte < terkecil.byte) terkecil = hasil;
    }
  }
  if (terkecil && terkecil.byte <= FBN_BATAS) return Object.assign(terkecil, { coba, lebihTarget: true });
  return { tolak: 'Foto masih ' + fbnKB(terkecil ? terkecil.byte : 0) + ' sesudah dikecilkan — lebih dari ' + fbnKB(FBN_BATAS) + '. Foto ulang lebih dekat / tanpa latar' };
}
/** Dokumen satu foto bon. ada = foto bon itu yang sudah tersimpan (untuk batas jumlah); antre = jumlah foto yang masih menunggu server di perangkat ini. */
export function fbnSusunSimpan(bon, hasil, w, ada, antre) {
  if (!bon || !bon.id) return { tolak: 'Pilih bonnya dulu' };
  if (!hasil || hasil.tolak) return { tolak: (hasil && hasil.tolak) || 'Belum ada foto' };
  if (!/^image\/(jpeg|png|webp)$/.test(String(hasil.jenis || '')) || !hasil.base64) return { tolak: 'Foto tidak terbaca' };
  const byte = fbnByte(hasil.base64); if (byte > FBN_BATAS) return { tolak: 'Foto ' + fbnKB(byte) + ' lebih dari ' + fbnKB(FBN_BATAS) + ' — kecilkan dulu' };
  if ((ada || []).length >= FBN_PALING_BANYAK) return { tolak: 'Bon ini sudah punya ' + FBN_PALING_BANYAK + ' foto — hapus yang tidak perlu dulu' };
  if ((Number(antre) || 0) >= FBN_ANTRE_MAKS) return { tolak: 'Foto sebelumnya BELUM sampai server (sinyal lambat) — tunggu kabar "sampai di server" dulu, baru tambah foto lagi' };
  const data = { id: String(w.idUnik()), idBon: String(bon.id), pemasok: String(bon.pemasok || ''), tanggalBon: String(bon.tanggal || ''), noBon: String(bon.noBon || ''), tanggal: w.tanggal, jam: w.jam,
    jenis: hasil.jenis, base64: hasil.base64, byte, lebar: fbnB(hasil.lebar) || 0, tinggi: fbnB(hasil.tinggi) || 0 };
  return { data, patch: { kabar: 'Foto bon ' + (bon.tanggal ? tanggalPendek(bon.tanggal) + ' ' : '') + String(bon.pemasok || '') + ' tersimpan (' + fbnKB(byte) + ', ' + data.lebar + '×' + data.tinggi + ' px' + (hasil.lebihTarget ? ' — di atas sasaran ' + fbnKB(FBN_TARGET) + ', tetap di bawah batas' : '') + ')', kabarAwas: false } };
}
/** Urut foto: terbaru dulu; hanya milik bon itu. */
export function fbnUrut(daftar, idBon) {
  return (daftar || []).filter((d) => d && String(d.idBon) === String(idBon) && d.base64).sort((a, b) => String(b.tanggal + ' ' + b.jam).localeCompare(String(a.tanggal + ' ' + a.jam)) || (Number(b.id) || 0) - (Number(a.id) || 0));
}
/** Kalimat jujur untuk foto yang kirimannya belum diakui server: BELUM tersimpan di server, sementara ada di perangkat ini (cache Firestore). */
export function fbnKabarAntre(data) {
  return 'Foto bon ' + (data && data.tanggalBon ? tanggalPendek(data.tanggalBon) + ' ' : '') + String((data && data.pemasok) || '') + ' BELUM sampai server (sinyal lambat) — sementara hanya ada di perangkat ini; kabar menyusul saat server menerima atau menolaknya. Buka lagi bon ini nanti untuk memastikan.';
}
