// CEK BON DARI HP (owner 26 Nov 2026, paket QR kedua, rules v23: "bangun bareng"). Logika TANPA DOM, nama berawalan bp. Dijaga alat-uji/uji_ambil_bon.py.
//
// Alurnya (dijelaskan ke owner 26 Nov): tiap pelanggan ber-bon bisa diberi KODE ACAK 22 huruf (± 131 bit — tidak bisa ditebak). Firestore menyimpan SATU dokumen
// ringkas bonPublik/<kode>: nama panggilan, sisa bon, nota yang belum lunas (tanggal · sisa · jatuh tempo), jam diperbarui. Rules v23: siapa pun boleh MEMBACA
// satu dokumen asal tahu kodenya (halaman baru/bon.html, tanpa login), tidak ada yang bisa MENDAFTAR kodenya, yang menulis & mencabut hanya OWNER.
// Isi ringkasan = angka penyusun yang sudah ada (semuaBon & pnNota bon-logika — menutup ke mesin), bukan hitungan baru. Ringkasan ditulis ulang oleh HP/Mac owner
// begitu bonnya berubah (bpPerluTulis — app.js, sesudah semua data terbaca); jam "diperbarui" ikut tampil supaya pelanggan tahu kalau ringkasannya belum segar.
import { cacheMentah } from '../data/toko.js';
import { semuaBon, pnNota } from './bon-logika.js';
import { kunciPelanggan } from '../mesin/pembantu.js';

export const BP_KOLEKSI = 'bonPublik';
export const BP_PANJANG = 22;
export const BP_NOTA_MAKS = 30;
const BP_HURUF = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
/** Kode acak 22 huruf [A-Za-z0-9] dari pembangkit acak KRIPTOGRAFIS (crypto.getRandomValues; byte ≥ 248 dibuang supaya merata). acak(n) = Uint8Array (uji). */
export function bpKodeBaru(acak) {
  const ambil = acak || ((n) => { const b = new Uint8Array(n); crypto.getRandomValues(b); return b; });
  let k = '';
  while (k.length < BP_PANJANG) { const b = ambil(BP_PANJANG * 2); for (let i = 0; i < b.length && k.length < BP_PANJANG; i++) if (b[i] < 248) k += BP_HURUF[b[i] % 62]; }
  return k;
}
export const bpKodeSah = (k) => /^[A-Za-z0-9]{20,64}$/.test(String(k || ''));
/** Semua dokumen cek bon yang tercatat (owner saja yang mendengarnya). */
export const bpSemua = () => (cacheMentah('bonPublik') || []).filter((d) => d && bpKodeSah(d.id));
/** Dokumen cek bon satu pelanggan (kunci pelanggan), yang tertua kalau dobel. */
export function bpUntuk(nama) { const k = kunciPelanggan(nama); return k ? bpSemua().filter((d) => d.kunci === k).sort((a, b) => String(a.id).localeCompare(String(b.id)))[0] || null : null; }
/** Ringkasan bon satu pelanggan (tanpa jam — supaya bisa dibandingkan). null = nama tidak ada di buku bon. */
export function bpRingkas(nama, kini) {
  const k = kunciPelanggan(nama); if (!k) return null;
  const B = semuaBon(kini); const b = B.find((x) => x.kunci === k); if (!b) return null;
  const P = pnNota(kini, B);
  const nota = P.nota.filter((x) => x.orang === k).sort((a, c) => String(a.tanggal).localeCompare(String(c.tanggal)))
    .map((x) => ({ tanggal: String(x.tanggal || ''), sisa: Math.round(x.sisa), jatuhTempo: String(x.jatuhTempo || ''), faktur: String(x.faktur || '') })).slice(0, BP_NOTA_MAKS);
  return { kunci: k, nama: String(b.nama || nama).trim().slice(0, 60), sisa: Math.max(0, Math.round(b.sisa)), nota, toko: 'Toko Beras M.IQBAL' };
}
const bpSama = (d, R) => !!d && !!R && d.nama === R.nama && d.sisa === R.sisa && d.toko === R.toko && JSON.stringify(d.nota || []) === JSON.stringify(R.nota);
/** Buat tautan cek bon untuk satu pelanggan (owner). acak = pembangkit untuk uji. */
export function bpSusunBuat(nama, kini, w, acak) {
  if (bpUntuk(nama)) return { tolak: 'Tautan cek bon ' + nama + ' sudah ada — cabut dulu kalau mau diganti' };
  const R = bpRingkas(nama, kini); if (!R) return { tolak: nama + ' tidak punya catatan bon' };
  const kode = bpKodeBaru(acak);
  return { dokumen: [{ koleksi: BP_KOLEKSI, data: Object.assign({ id: kode }, R, { diperbarui: w.kini }) }], kode,
    patch: { kabar: 'Tautan cek bon ' + R.nama + ' dibuat — kirim lewat WhatsApp; siapa pun yang memegang tautan itu bisa melihat sisa bonnya', kabarAwas: false } };
}
/** Cabut tautan cek bon (owner): dokumennya dihapus — tautan lama mati. */
export function bpSusunCabut(nama) {
  const k = kunciPelanggan(nama); const ds = bpSemua().filter((d) => d.kunci === k); if (!ds.length) return { tolak: 'Belum ada tautan cek bon untuk ' + nama };
  return { dokumen: [], hapus: ds.map((d) => ({ koleksi: BP_KOLEKSI, id: String(d.id) })), patch: { kabar: 'Tautan cek bon ' + nama + ' DICABUT — tautan lama tidak bisa dibuka lagi', kabarAwas: false } };
}
/** Ringkasan yang perlu ditulis ulang (owner, sesudah data berubah): dokumen yang isinya beda dari bon sekarang. Orang yang bonnya sudah tidak ada di buku → sisa 0. */
export function bpPerluTulis(kini, w) {
  return bpSemua().map((d) => { const R = bpRingkas(d.nama || d.kunci, kini) || { kunci: d.kunci, nama: d.nama, sisa: 0, nota: [], toko: 'Toko Beras M.IQBAL' };
    return bpSama(d, R) ? null : { koleksi: BP_KOLEKSI, data: Object.assign({ id: String(d.id) }, R, { diperbarui: w.kini }) }; }).filter(Boolean);
}
/** Tautan halaman cek bon. dasar = alamat folder /baru/ (mis. new URL('.', location.href).href); proyek lain dari toko ikut disebut (p=). */
export function bpTautan(kode, dasar, proyek) {
  return String(dasar || '') + 'bon.html#k=' + kode + (proyek && proyek !== 'toko-beras-m-iqbal' ? '&p=' + encodeURIComponent(proyek) : '');
}
/** Pesan WhatsApp untuk pelanggan: tautan cek bon. */
export function bpPesanWa(nama, tautan) {
  return 'Halo ' + String(nama || '').trim() + ', ini tautan untuk cek sisa bon di Toko Beras M.IQBAL kapan saja:\n' + tautan + '\nTautan ini khusus untuk Anda — jangan dibagikan.';
}
