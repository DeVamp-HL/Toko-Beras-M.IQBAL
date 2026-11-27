// FOTO NOTA & ARSIP FOTO (paket P8, owner 27 Nov 2026 — sensus A94). Logika TANPA DOM, nama berawalan af. Dijaga alat-uji/uji_arsip_audit_p8.py.
//
// Keputusan owner 27 Nov 2026: nota kedatangan TUNAI ikut difoto (dulu cuma bon pemasok & nota kas kecil), dari HP/Mac owner DAN tablet Penjaga laci (rules v26
// stafFotoNota); foto TETAP di Firestore (koleksi fotoBon, ±300 KB per lembar, dibaca saat dibuka) — cadangan berkas tidak ikut berat; arsipnya diunduh TERPISAH
// per bulan (berkas HTML yang bisa dibuka tanpa internet). Dasbor menghitung kedatangan & nota yang BELUM berfoto.
// Supaya hitungan itu tidak membaca foto (berat), tiap foto ditulis bersama TANDA ringan di koleksi fotoTanda (id = id foto; idBon, jenis, tanggal, byte — tanpa
// gambar; firebase.js simpanFotoBon, satu kiriman). Foto lama (sebelum P8) belum bertanda: tandanya ditulis sekali saat owner mengunduh arsip bulan itu
// (afSusunTandaKurang) — sampai itu, kedatangan berfoto lama terhitung "belum berfoto" dan kalimatnya MENYEBUT kemungkinan itu.
// Nota kas kecil sudah menyimpan id fotonya sendiri (pengeluaranHarian.fotoNota) — hitungannya dari situ, bukan dari tanda.
import { ambilSemuaBatch, ambilPengeluaranHarian, ambilUtangPemasokMutasi, cacheMentah } from '../data/toko.js';
import { batchDiutang } from '../mesin/pembantu.js';
import { hariIniIso, tanggalPendek, waktuSetempat } from '../inti/format.js';

export const AF_KOLEKSI = 'fotoTanda';
export const AF_HARI = 30;              // jendela hitungan "belum berfoto" (Dasbor) — kedatangan & nota 30 hari terakhir
export const AF_BULAN = 6;              // bulan yang tampil di panel arsip foto
export const AF_TANDA_MAKS = 200;       // tanda foto lama yang ditulis sekali kirim (2 tulisan per tanda: tanda + baris jejak; batas Firestore 500)
export const AF_KB_PERKIRAAN = 300;     // perkiraan ukuran satu foto (sasaran pengecil foto-bon-logika FBN_TARGET) — untuk kalimat sebelum unduh
const AF_ID_KEDATANGAN = /^[0-9]{10,16}(\.[0-9]{1,6})?$/;   // = rules v26 stafFotoNota / stafTandaFoto (idBon kedatangan)
const AF_TANDA_KOLOM = ['id', 'idBon', 'jenis', 'pemasok', 'tanggalBon', 'tanggal', 'jam', 'byte'];
const afTambahHari = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const afGeserBulan = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; return new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)).toISOString().slice(0, 7); };
const AF_NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
export const afNamaBulan = (key) => AF_NAMA_BULAN[Number(String(key).slice(5, 7)) - 1] + ' ' + String(key).slice(0, 4);
export const afKB = (byte) => Math.round((Number(byte) || 0) / 1024);
/** Kedatangan NYATA: bukan stok awal / lahir buku / saldo pembuka tutup buku, dan ada barang yang datang. */
export const afKedatanganNyata = (b) => !!b && !b.stokAwal && !b.lahirBuku && !b.tutupBuku && String(b.pemasok || '').trim() !== '' && String(b.pemasok) !== 'LAHIR BUKU'
  && (b.merkList || []).some((m) => (Number(m.totalKg) || 0) > 0 || (Number(m.jumlahKarung) || 0) > 0 || (Number(m.subtotalHarga) || 0) > 0);
/** Jenis foto dari idBon: 'kas' (nota kas kecil uk-…), 'bon' / 'tunai' (kedatangan), 'saldoAwal' (bon lama sebelum sistem), '' (tidak dikenal). */
export function afJenis(idBon) {
  const id = String(idBon || ''); if (!id) return ''; if (id.indexOf('uk-') === 0) return 'kas';
  const b = ambilSemuaBatch().find((x) => String(x.id) === id); if (b) return batchDiutang(b) ? 'bon' : 'tunai';
  if (ambilUtangPemasokMutasi().some((m) => m && m.tipe === 'saldoAwal' && String(m.id) === id)) return 'saldoAwal';
  return '';
}
/** Dokumen TANDA satu foto (tanpa gambar) — id = id foto. null bila fotonya tidak berid / tanpa idBon. Jenis yang tidak dikenal ditulis 'lain' (owner saja). */
export function afTandaDari(foto) {
  if (!foto || foto.id === undefined || foto.id === null || foto.id === '' || !foto.idBon) return null;
  const t = { id: String(foto.id), idBon: String(foto.idBon), jenis: afJenis(foto.idBon) || 'lain', pemasok: String(foto.pemasok || '').slice(0, 60), tanggalBon: String(foto.tanggalBon || ''),
    tanggal: String(foto.tanggal || ''), jam: String(foto.jam || ''), byte: Math.max(0, Math.round(Number(foto.byte) || 0)) };
  Object.keys(t).forEach((k) => { if (AF_TANDA_KOLOM.indexOf(k) < 0) delete t[k]; });
  return t;
}
/** Kedatangan ini boleh difoto dari tablet (rules v26): id berbentuk id kedatangan. */
export const afIdKedatanganSah = (id) => AF_ID_KEDATANGAN.test(String(id || ''));
/** Peta idBon → jumlah foto bertanda (koleksi fotoTanda, owner). */
export function afBerfoto() {
  const m = {}; (cacheMentah(AF_KOLEKSI) || []).forEach((t) => { if (t && t.idBon) m[String(t.idBon)] = (m[String(t.idBon)] || 0) + 1; }); return m;
}
/** Satu kedatangan untuk kartu foto: { id, tanggal, pemasok, jenis bon|tunai, noBon, nFoto } atau null. */
export function afKedatangan(id) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b || !afKedatanganNyata(b)) return null;
  return { id: String(b.id), tanggal: String(b.tanggal || ''), jam: String(b.jam || ''), pemasok: String(b.pemasok || '').trim(), jenis: batchDiutang(b) ? 'bon' : 'tunai', noBon: String(b.noBon || ''),
    nFoto: afBerfoto()[String(b.id)] || 0 };
}
/**
 * BELUM BERFOTO (Dasbor & panel arsip): kedatangan nyata `hari` hari terakhir (bawaan AF_HARI) yang belum punya tanda foto (bon & tunai disebut terpisah) + nota kas kecil
 * bertanda "nota ada" yang belum difoto. Kedatangan dari tablet ikut (difoto Penjaga laci). Baca saja.
 */
export function afBelum(kini, hari) {
  const iso = hariIniIso(kini); const N = Math.max(1, Math.round(Number(hari) || AF_HARI)); const dari = afTambahHari(iso, -(N - 1)); const F = afBerfoto();
  const semua = ambilSemuaBatch().filter((b) => afKedatanganNyata(b) && String(b.tanggal || '') >= dari && String(b.tanggal || '') <= iso)
    .map((b) => ({ id: String(b.id), tanggal: String(b.tanggal || ''), jam: String(b.jam || ''), pemasok: String(b.pemasok || '').trim(), jenis: batchDiutang(b) ? 'bon' : 'tunai', nFoto: F[String(b.id)] || 0,
      nilai: Math.round((b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0)) }))
    .sort((a, b) => String(b.tanggal + ' ' + b.jam).localeCompare(String(a.tanggal + ' ' + a.jam)) || (Number(b.id) || 0) - (Number(a.id) || 0));
  const belum = semua.filter((x) => !x.nFoto);
  const kas = ambilPengeluaranHarian().filter((h) => h && h.nota === 'ada' && !h.dibatalkan && String(h.tanggal || '') >= dari && String(h.tanggal || '') <= iso && !(Array.isArray(h.fotoNota) && h.fotoNota.length))
    .map((h) => ({ id: String(h.id), tanggal: String(h.tanggal || ''), ket: String(h.keterangan || h.kategori || 'uang keluar').slice(0, 60), nominal: Math.round(Number(h.nominal) || 0) }))
    .sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)));
  const nBon = belum.filter((x) => x.jenis === 'bon').length; const nTunai = belum.length - nBon; const adaTanda = (cacheMentah(AF_KOLEKSI) || []).length > 0;
  const n = belum.length + kas.length;
  return { dari, sampai: iso, hari: N, kedatangan: semua.length, berfoto: semua.length - belum.length, belum, nBon, nTunai, kas, n,
    kalimat: !semua.length && !kas.length ? 'Belum ada kedatangan atau nota kas kecil ' + N + ' hari terakhir'
      : n === 0 ? 'Semua ' + semua.length + ' kedatangan' + (kas.length ? ' & nota kas kecil' : '') + ' ' + N + ' hari terakhir sudah berfoto'
      : belum.length + ' dari ' + semua.length + ' kedatangan belum berfoto' + (belum.length ? ' (' + nTunai + ' tunai · ' + nBon + ' bon)' : '') + (kas.length ? ' · ' + kas.length + ' nota kas kecil belum difoto' : ''),
    catatanLama: adaTanda ? '' : 'Foto yang diambil sebelum 27 Nov 2026 belum bertanda — unduh arsip foto bulan itu sekali (Menu › Toko ini › Cadangan & simpanan › Arsip foto) supaya ikut terhitung.',
    tujuan: { ke: 'sistem', sistem: 'cadangan', tab: 'foto' } };
}
/** Ringkasan per bulan untuk panel arsip foto: n bulan terakhir (bawaan AF_BULAN) — foto bertanda menurut TANGGAL FOTO, ukurannya, dan kedatangan bulan itu. */
export function afBulan(kini, n) {
  const iso = hariIniIso(kini); const N = Math.max(1, Math.round(Number(n) || AF_BULAN)); const T = cacheMentah(AF_KOLEKSI) || []; const B = ambilSemuaBatch().filter(afKedatanganNyata); const F = afBerfoto();
  const out = []; for (let i = 0; i < N; i++) { const key = afGeserBulan(iso.slice(0, 7), -i); const tk = T.filter((t) => String(t.tanggal || '').slice(0, 7) === key);
    const kd = B.filter((b) => String(b.tanggal || '').slice(0, 7) === key);
    out.push({ key, nama: afNamaBulan(key), foto: tk.length, kb: tk.reduce((a, t) => a + afKB(t.byte), 0), kedatangan: kd.length, berfoto: kd.filter((b) => F[String(b.id)]).length,
      perJenis: ['tunai', 'bon', 'kas', 'saldoAwal', 'lain'].map((j) => ({ jenis: j, n: tk.filter((t) => (t.jenis || 'lain') === j).length })).filter((x) => x.n) }); }
  return out;
}
/** Tanda foto lama yang belum ada (foto dari arsip yang baru dibaca) → dokumen fotoTanda, paling banyak AF_TANDA_MAKS sekali kirim. Owner (lewat penulis pusat). */
export function afSusunTandaKurang(fotos) {
  const ada = {}; (cacheMentah(AF_KOLEKSI) || []).forEach((t) => { if (t && t.id !== undefined) ada[String(t.id)] = true; });
  const dok = (fotos || []).filter((f) => f && f.id !== undefined && !ada[String(f.id)]).map(afTandaDari).filter(Boolean).slice(0, AF_TANDA_MAKS).map((t) => ({ koleksi: AF_KOLEKSI, data: t }));
  return dok.length ? { dokumen: dok, patch: { kabar: dok.length + ' foto lama didaftarkan — kini ikut hitungan "belum berfoto" di Dasbor', kabarAwas: false } } : { kosong: true };
}
const afEsc = (s) => String(s === undefined || s === null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const AF_NAMA_JENIS = { tunai: 'nota kedatangan tunai', bon: 'bon pemasok', kas: 'nota kas kecil', saldoAwal: 'bon lama', lain: 'foto' };
export const afNamaJenis = (j) => AF_NAMA_JENIS[j] || 'foto';
/**
 * Berkas ARSIP FOTO satu bulan: satu halaman HTML mandiri (foto tampil tanpa internet, bisa dicetak / disimpan PDF), urut tanggal foto. fotos = dokumen fotoBon bulan itu
 * (firebase.js bacaFotoBulan). Daftar ringkas (tanpa gambar) ikut sebagai JSON di dalam berkas. → { nama, isi, n, byte, tolak? }
 */
export function afBerkasArsip(fotos, key, kini) {
  const F = (fotos || []).filter((f) => f && f.base64 && /^image\/(jpeg|png|webp)$/.test(String(f.jenis || ''))).sort((a, b) => String(a.tanggal + ' ' + a.jam).localeCompare(String(b.tanggal + ' ' + b.jam)) || (Number(a.id) || 0) - (Number(b.id) || 0));
  if (!F.length) return { tolak: 'Belum ada foto yang diambil ' + afNamaBulan(key) };
  const daftar = F.map((f) => ({ id: String(f.id), idBon: String(f.idBon || ''), jenis: afJenis(f.idBon) || 'lain', pemasok: String(f.pemasok || ''), tanggalBon: String(f.tanggalBon || ''), noBon: String(f.noBon || ''),
    tanggal: String(f.tanggal || ''), jam: String(f.jam || ''), byte: Math.round(Number(f.byte) || 0), oleh: String(f.oleh || '') }));
  const byte = daftar.reduce((a, d) => a + d.byte, 0);
  const isi = '<!doctype html>\n<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Arsip foto ' + afEsc(afNamaBulan(key)) + ' · Toko Beras M.IQBAL</title>'
    + '<style>body{font:15px/1.4 system-ui,sans-serif;margin:16px;color:#222;background:#fff}h1{font-size:20px}.f{break-inside:avoid;margin:18px 0;border-top:1px solid #ccc;padding-top:10px}.k{color:#666;font-size:13px}img{max-width:100%;height:auto;display:block;margin-top:6px}</style></head><body>'
    + '<h1>Arsip foto nota & bon — ' + afEsc(afNamaBulan(key)) + '</h1><p class="k">Toko Beras M.IQBAL · ' + daftar.length + ' foto · ' + afKB(byte) + ' KB · diunduh ' + afEsc(waktuSetempat(kini.toISOString())) + ' dari Firestore (fotoBon). Simpan berkas ini di tempat lain (Drive / komputer).</p>'
    + F.map((f, i) => { const d = daftar[i]; return '<div class="f"><div><b>' + afEsc(afNamaJenis(d.jenis)) + '</b>' + (d.pemasok ? ' · ' + afEsc(d.pemasok) : '') + (d.tanggalBon ? ' · tanggal ' + afEsc(tanggalPendek(d.tanggalBon)) : '') + (d.noBon ? ' · no. ' + afEsc(d.noBon) : '')
      + '</div><div class="k">difoto ' + afEsc(tanggalPendek(d.tanggal)) + (d.jam ? ' ' + afEsc(d.jam) : '') + (d.oleh ? ' oleh ' + afEsc(d.oleh) : '') + ' · ' + afKB(d.byte) + ' KB · id ' + afEsc(d.id) + '</div><img alt="foto ' + afEsc(d.id) + '" src="data:' + afEsc(f.jenis) + ';base64,' + String(f.base64).replace(/[^A-Za-z0-9+/=]/g, '') + '"></div>'; }).join('')
    + '<script type="application/json" id="daftar-foto">' + JSON.stringify({ versi: 1, bulan: key, diunduhPada: kini.toISOString(), foto: daftar }).replace(/</g, '\\u003c') + '</script></body></html>';
  return { nama: 'arsip-foto-miqbal-' + key + '.html', isi, n: daftar.length, byte, kabar: 'Arsip foto ' + afNamaBulan(key) + ' diunduh: ' + daftar.length + ' foto (' + afKB(byte) + ' KB) — simpan juga di tempat lain (Drive / komputer)' };
}
/** Kalimat perkiraan sebelum unduh: berapa foto & KB yang akan dibaca dari server (dari tanda; foto lama tanpa tanda belum terhitung). */
export function afPerkiraanUnduh(B) {
  if (!B) return ''; return B.foto ? B.foto + ' foto bertanda (± ' + B.kb + ' KB) akan dibaca dari server — foto lama tanpa tanda ikut terbaca & didaftarkan' : 'Belum ada foto bertanda — foto lama (bila ada) tetap terbaca & didaftarkan; perkiraan ± ' + AF_KB_PERKIRAAN + ' KB per foto';
}
