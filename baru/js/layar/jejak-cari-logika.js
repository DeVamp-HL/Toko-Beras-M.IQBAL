// CARI LOG AKTIVITAS (paket P8, owner 27 Nov 2026 — sensus B81: "Cari per tanggal pas dibuka"). Logika TANPA DOM, nama berawalan jc. Dijaga alat-uji/uji_arsip_audit_p8.py.
//
// Pendengar tetap membaca 150 tulisan TERBARU (koleksi.js batas 150 — tidak berubah, tanpa baca tambahan). Owner bisa membaca log satu HARI lain (rentang `pada` satu hari
// WIB, ± 190 tulisan/hari perkiraan dari cadangan 25 Nov) atau RIWAYAT SATU CATATAN (idDok) — dibaca SEKALI saat diminta (firebase.js bacaLog; satu dokumen = satu baca,
// jatah gratis Blaze 50 rb baca/hari). Hasilnya bisa disaring per orang, jenis catatan, dan kata (teks / id catatan). Cadangan berkas membawa log 30 HARI terakhir
// (jcRentangCadangan; ± 5.700 baca tiap unduh) — kunci `logAktivitas` di berkas (isiDariCadangan memasoknya ke cache log saat cadangan dibuka; sistem lama tidak
// membacanya). Nama jenis catatan diberikan pemanggil (`nama`, = ssNamaKoleksi) supaya modul ini tetap daun tanpa impor layar.
export const JC_MAKS_HARI = 3000;        // paling banyak tulisan satu hari yang dibaca (hari tersibuk cadangan 25 Nov ± 300) — lebih = disebut "terpotong"
export const JC_MAKS_CATATAN = 300;      // riwayat satu catatan
export const JC_HARI_CADANGAN = 30;      // log yang ikut cadangan berkas (keputusan owner 27 Nov 2026)
export const JC_MAKS_CADANGAN = 20000;   // batas aman baca log cadangan (30 hari × ± 190 = ± 5.700)
export const JC_TAMPIL = 300;            // baris yang digambar sekali (sisanya disebut)
const jcDua = (n) => (n < 10 ? '0' : '') + n;
const jcIsoLokal = (d) => d.getFullYear() + '-' + jcDua(d.getMonth() + 1) + '-' + jcDua(d.getDate());
const jcJamLokal = (d) => jcDua(d.getHours()) + '.' + jcDua(d.getMinutes());
/** Tanggal YYYY-MM-DD sah. */
export const jcTanggalSah = (t) => /^\d{4}-\d{2}-\d{2}$/.test(String(t || '')) && !isNaN(new Date(String(t) + 'T00:00:00').getTime());
/** Rentang `pada` (ISO UTC) untuk satu hari SETEMPAT (jam perangkat = WIB toko): [00.00, 24.00). null bila tanggal tidak sah. */
export function jcRentangHari(tanggal) {
  if (!jcTanggalSah(tanggal)) return null; const [y, m, d] = String(tanggal).split('-').map(Number);
  return { dari: new Date(y, m - 1, d, 0, 0, 0, 0).toISOString(), sampai: new Date(y, m - 1, d + 1, 0, 0, 0, 0).toISOString(), tanggal: String(tanggal) };
}
/** Rentang log untuk cadangan berkas: mulai hari ke-`hari` ke belakang (00.00 setempat) sampai 1 menit sesudah kini. */
export function jcRentangCadangan(kini, hari) {
  const N = Math.max(1, Math.round(Number(hari) || JC_HARI_CADANGAN)); const k = new Date(kini.getTime());
  return { dari: new Date(k.getFullYear(), k.getMonth(), k.getDate() - (N - 1), 0, 0, 0, 0).toISOString(), sampai: new Date(k.getTime() + 60000).toISOString(), hari: N };
}
/** Satu baris log → bentuk tampil (sama dengan jejak 150 terbaru ssJejak). */
export function jcBaris(l, nama) {
  const nm = typeof nama === 'function' ? nama : (x) => x || 'catatan'; const d = l && l.pada ? new Date(l.pada) : null; const ada = !!d && isFinite(d.getTime());
  const staf = Array.isArray(l && l.dokumen) && l.dokumen.length;   // jejak kiriman bukan-owner: satu baris berisi daftar dokumen
  const kol = String((l && l.koleksi) || (staf ? l.dokumen.map((x) => x && x.koleksi).filter(Boolean)[0] || '' : ''));
  return { id: String((l && l.id) || ''), pada: String((l && l.pada) || ''), tanggal: ada ? jcIsoLokal(d) : '', jam: ada ? jcJamLokal(d) : '', oleh: String((l && l.oleh) || '—'), perangkat: String((l && l.perangkat) || '—'),
    aksi: String((l && l.aksi) || 'tulis'), koleksi: kol, idDok: String((l && l.idDok) || (staf ? (l.dokumen[0] || {}).id || '' : '')),
    teks: ((l && l.lewat) ? '[' + String(l.lewat) + '] ' : '') + (l && l.aksi === 'batalkan' ? 'BATAL · ' : l && l.aksi === 'tandai-koreksi' ? 'KOREKSI · ' : l && l.aksi === 'hapus' ? 'HAPUS · ' : l && l.aksi === 'ubah' ? 'UBAH · ' : '')
      + (staf ? l.dokumen.length + ' catatan: ' + Array.from(new Set(l.dokumen.map((x) => nm(x && x.koleksi)))).join(', ') : nm(kol)) + (l && l.ringkas ? ' · ' + String(l.ringkas) : ''),
    lama: !!(l && l.lama) };
}
const jcUrut = (a, b) => String(b.pada).localeCompare(String(a.pada)) || String(b.id).localeCompare(String(a.id));
/**
 * Saring hasil baca: S = { oleh, koleksi, kata } (kosong = semua). → { tampil (≤ JC_TAMPIL), n, nSemua, lebih, perOrang, perJenis, kalimat }.
 * kata dicocokkan ke teks, id catatan, orang & perangkat (huruf besar/kecil sama).
 */
export function jcSaring(daftar, S, nama) {
  const s = S || {}; const semua = (daftar || []).map((l) => jcBaris(l, nama)).sort(jcUrut); const kata = String(s.kata || '').trim().toLowerCase();
  const cocok = semua.filter((l) => (!s.oleh || l.oleh === s.oleh) && (!s.koleksi || l.koleksi === s.koleksi)
    && (!kata || (l.teks + ' ' + l.idDok + ' ' + l.oleh + ' ' + l.perangkat).toLowerCase().indexOf(kata) >= 0));
  const hitung = (f) => { const m = {}; semua.forEach((l) => { const k = f(l); m[k] = (m[k] || 0) + 1; }); return Object.keys(m).sort((a, b) => m[b] - m[a] || a.localeCompare(b)).map((k) => ({ nama: k, n: m[k] })); };
  const nm = typeof nama === 'function' ? nama : (x) => x || 'catatan';
  return { tampil: cocok.slice(0, JC_TAMPIL), n: cocok.length, nSemua: semua.length, lebih: Math.max(0, cocok.length - JC_TAMPIL), perOrang: hitung((l) => l.oleh),
    perJenis: hitung((l) => l.koleksi || '').map((x) => ({ id: x.nama, nama: nm(x.nama), n: x.n })),
    kalimat: !semua.length ? 'Tidak ada tulisan yang tercatat' : cocok.length === semua.length ? semua.length + ' tulisan' : cocok.length + ' dari ' + semua.length + ' tulisan cocok saringan' };
}
/** Kalimat jujur sesudah membaca: berapa baca dari server, terpotong atau tidak, dari cache. */
export function jcKalimatBaca(hasil, maks, apa) {
  const n = (hasil || []).length; return (apa || 'Log') + ': ' + n + ' tulisan dibaca' + (hasil && hasil.dariCache ? ' dari simpanan perangkat (server belum terjangkau)' : ' dari server (± ' + n + ' baca)')
    + (hasil && hasil.penuh ? ' — TERPOTONG di ' + maks + ' tulisan (sisanya tidak dibaca)' : '');
}
/** Berkas cadangan membawa log 30 hari: isi.logAktivitas + keterangan rentang; jumlah dokumen ikut bertambah. b = ssBerkasCadangan. log = hasil baca (null = tidak terbaca → disebut). */
export function jcSertakanLog(b, log, rentang, galat) {
  if (!b || !b.isi) return b; const isi = Object.assign({}, b.isi); const L = Array.isArray(log) ? log.slice() : null;
  if (L) { isi.logAktivitas = L; isi.logRentang = { dari: rentang ? rentang.dari : '', sampai: rentang ? rentang.sampai : '', hari: rentang ? rentang.hari : JC_HARI_CADANGAN, n: L.length, terpotong: !!(log && log.penuh) }; }
  else isi.logRentang = { gagal: String(galat || 'log tidak terbaca'), n: 0 };
  return Object.assign({}, b, { isi, dokumen: (b.dokumen || 0) + (L ? L.length : 0), log: L ? L.length : null });
}
