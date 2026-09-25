// KUNCI BULAN (putaran 25, owner 25 Sep 2026) — Uang › Tutup buku, kartu "Kunci bulan". Logika tanpa DOM, pembantu berawalan kp (bundel uji = satu lingkup).
// Daftar periksa: butir ⛔ memblokir; butir lain dicentang owner (atau beres sendiri kalau tidak ada yang perlu disebut). Kunci = dua ketukan; buka = hanya bulan
// terakhir, satu langkah mundur, alasan ≥ 10 huruf; bulan yang punya setoran pajak minta nama bulannya diketik ulang. Server (firestore.rules v4) menegakkan
// hal yang sama: sampaiBulan hanya naik satu bulan (atau pertama kali dari kosong), turun tepat satu dengan alasan, dan tidak pernah bulan yang masih dalam
// tenggang minimal. Keputusan owner K1–K6 & syarat 25b: docs/peta-kunci-periode.md.
import { KP_ID, KP_ID_ATUR, KP_TENGGANG_MIN, KP_SIAP_25B, kpWib, kpIdx, kpBulanStr, kpGeser, kpNamaBulan, kpAkhirBulan, kpBolehDikunci, kpDok, kpBulanDok, kpKalimat } from '../data/kunci-periode.js';
import { cacheMentah, dokDiCache, ambilPenjualan, ambilPenjualanSemua, ambilTutupHari, ambilSemuaBatch, ambilProduksi, ambilUtangPemasokMutasi, ambilPiutangMutasi, kunciSampai, kunciTenggang } from '../data/toko.js';
import { hitungLabaBersihRentang, hitungNeraca } from '../mesin/beku.js';
import { kunciPelanggan } from '../mesin/pembantu.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { semuaOrang, pasanganKembar } from './pelanggan-logika.js';
import { aturUpah, hitungUpah } from './upah-logika.js';
import { pjTahun } from './pajak-logika.js';

export const KP_DENYUT_MS = 24 * 3600000;   // ⛔ perangkat yang tidak berdenyut 24 jam terakhir (owner 25 Sep)
const kpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const kpTgl = (iso) => (iso && iso.length >= 10 ? tanggalPendek(iso) : iso || '—');

/** Keadaan kunci sekarang: bulan terkunci terakhir, riwayat (terbaru dulu), tenggang. */
export function kpKeadaan() {
  const d = kpDok(cacheMentah('aturan')); const riwayat = d && Array.isArray(d.riwayat) ? d.riwayat.slice() : [];
  return { sampai: kunciSampai(), tenggang: kunciTenggang(), riwayat: riwayat.slice().reverse(), nRiwayat: riwayat.length, dok: d };
}
/** Bulan berikutnya yang bisa dikunci: sesudah bulan terkunci terakhir, atau (belum pernah) bulan lalu. null = semua bulan yang sudah lewat sudah terkunci. */
export function kpCalon(kini) {
  const W = kpWib(kini); const s = kunciSampai(); const c = s ? kpGeser(s, 1) : kpBulanStr(W.idx - 1);
  return kpIdx(c) <= W.idx - 1 ? c : null;
}
/** Tanggal pertama yang boleh mengunci bulan M menurut tenggang layar. */
export const kpMulaiBoleh = (bulan, tenggang) => kpGeser(bulan, 1) + '-' + String(Math.max(KP_TENGGANG_MIN, tenggang) + 1).padStart(2, '0');
/** Catatan pertama toko (nota atau kedatangan sungguhan) — hari sebelum itu bukan "hari buka". Sama dengan lpPertama laporan. */
function kpPertama() { let p = ''; ambilPenjualanSemua().forEach((d) => { if (d.tanggal && (!p || d.tanggal < p)) p = d.tanggal; }); ambilSemuaBatch().forEach((b) => { if (!b.stokAwal && !b.tutupBuku && b.tanggal && (!p || b.tanggal < p)) p = b.tanggal; }); return p; }
function kpTambahHari(iso, n) { const d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
/** Rentang yang ikut terkunci bila M dikunci: sesudah bulan terkunci terakhir sampai M (kunci pertama = semua bulan sampai M). */
function kpRentang(bulan) { const s = kunciSampai(); return { dari: s ? kpGeser(s, 1) : '0000-00', sampai: bulan }; }
const kpDalam = (tgl, R) => { const b = String(tgl || '').slice(0, 7); return !!tgl && b >= R.dari && b <= R.sampai; };

/** Hari berjualan / hari dalam rentang tanpa tutup hari. */
export function kpHariTanpaTutup(bulan, kini, putusan) {
  const R = kpRentang(bulan); const P = putusan || {}; const pertama = kpPertama(); if (!pertama) return [];
  const tutup = {}; ambilTutupHari().forEach((t) => { tutup[t.tanggal] = true; });
  const jual = {}; ambilPenjualan().forEach((p) => { if (p.tanggal && kpDalam(p.tanggal, R)) jual[p.tanggal] = (jual[p.tanggal] || 0) + 1; });
  const out = []; let t = pertama > R.dari + '-01' ? pertama : (R.dari === '0000-00' ? pertama : R.dari + '-01'); const akhir = kpAkhirBulan(bulan); const kemarin = kpTambahHari(kpWib(kini).iso, -1);
  for (; t <= akhir && t <= kemarin; t = kpTambahHari(t, 1)) {
    if (tutup[t]) continue; const x = P[t] || null;
    out.push({ iso: t, nNota: jual[t] || 0, adaJual: !!jual[t], putusan: x && (x.jenis === 'diterima' ? !kpKosong(x.alasan) && String(x.alasan).trim().length >= 5 : x.jenis === 'libur' && !jual[t]) ? x : null, pilihan: jual[t] ? ['diterima'] : ['libur', 'diterima'] });
  }
  return out;
}
/**
 * Daftar periksa bulan M. K = { lokal: { antreLokal: { belum, ditolak }, antre: [{ koleksi, id }] }, parkir: [{ pada, pelanggan, n }], putusanHari: { iso: { jenis, alasan } },
 * centang: { id: true }, siap25b? (uji saja) }. Kembali { bulan, butir, hari, boleh, belum }.
 */
export function kpDaftarPeriksa(bulan, kini, K) {
  K = K || {}; const L = K.lokal || {}; const R = kpRentang(bulan); const W = kpWib(kini); const nama = kpNamaBulan(bulan); const tenggang = kunciTenggang(); const C = K.centang || {};
  const dokDalam = (koleksi, d) => { const b = kpBulanDok(koleksi, d); return b !== null && b <= kpIdx(bulan); };
  const butir = [];
  const tambah = (x) => butir.push(Object.assign({ blokir: false, perluCentang: false, rincian: [], aksi: [] }, x));
  // ---- ⛔
  const siap = KP_SIAP_25B || !!K.siap25b;
  tambah({ id: 'siap25b', blokir: true, ok: siap, teks: 'Sistem lama & kasir darurat siap menghadapi bulan terkunci (putaran 25b)', ket: siap ? 'siap' : 'BELUM — sampai putaran 25b, satu nota kasir yang tertahan offline lalu tiba sesudah bulannya terkunci membuat antrean tablet itu MACET (nota sesudahnya ikut tertahan), dan index.html memunculkan "Database terkunci" berulang. Kunci pertama menunggu 25b (keputusan owner 25 Sep).' });
  const bolehT = kpBolehDikunci(bulan, kini, tenggang);
  tambah({ id: 'tenggang', blokir: true, ok: bolehT, teks: 'Sudah lewat masa tenggang (' + tenggang + ' hari)', ket: bolehT ? 'hari ini ' + kpTgl(W.iso) : nama + ' baru bisa dikunci mulai ' + kpTgl(kpMulaiBoleh(bulan, tenggang)) + ' — catatan yang telat masuk masih diberi waktu' });
  const AL = L.antreLokal || { belum: [], ditolak: [] }; const tertahan = [];
  (AL.belum || []).concat(AL.ditolak || []).forEach((e) => { const kena = (e.dokumen || []).filter((d) => dokDalam(d.koleksi, d.data)); if (kena.length) tertahan.push((e.keadaan === 'ditolak' ? 'ditolak server' : 'belum terkirim') + ' · ' + (e.akunNama || '?') + ' · ' + kena.length + ' catatan ' + kpNamaBulan(kpBulanStr(kpBulanDok(kena[0].koleksi, kena[0].data)))); });
  (L.antre || []).forEach((q) => { const dok = dokDiCache(q.koleksi, q.id); if (dok && dokDalam(q.koleksi, dok)) tertahan.push('menunggu server · ' + q.koleksi + ' ' + (dok.tanggal || dok.bulan || '')); });   // tulisan Firestore yang belum diakui server (hasPendingWrites)
  tambah({ id: 'antreIni', blokir: true, ok: !tertahan.length, teks: 'Tidak ada catatan ' + nama + ' yang tertahan / ditolak server di perangkat ini', ket: tertahan.length ? tertahan.length + ' kiriman — kirim dulu (sambungkan internet) atau putuskan di Menu › Sistem › Perangkat' : 'bersih', rincian: tertahan.slice(0, 6) });
  const parkir = (K.parkir || []).filter((p) => !p.pada || kpWib(new Date(p.pada)).idx <= kpIdx(bulan));
  tambah({ id: 'parkir', blokir: true, ok: !parkir.length, teks: 'Tidak ada nota parkir dari ' + nama, ket: parkir.length ? parkir.length + ' nota diparkir — catat atau buang di Jual dulu' : 'bersih', rincian: parkir.map((p) => (p.pelanggan || 'tanpa nama') + ' · ' + (p.n || 0) + ' baris · ' + (p.pada ? 'diparkir ' + kpTgl(kpWib(new Date(p.pada)).iso) : 'tanggal parkirnya tidak tercatat (diparkir sebelum pembaruan ini)')) });
  const perangkat = cacheMentah('perangkat'); const t = kini.getTime();
  const antreLain = perangkat.filter((p) => (Number(p.antrean) || 0) > 0);
  tambah({ id: 'perangkatAntre', blokir: true, ok: !antreLain.length, teks: 'Tidak ada perangkat yang masih menyimpan antrean', ket: antreLain.length ? 'tulisan offline dari perangkat ini untuk ' + nama + ' akan ditolak sesudah dikunci' : 'semua perangkat melaporkan antrean kosong',
    rincian: antreLain.map((p) => (p.nama || p.id) + ' · ' + p.antrean + ' antre' + (p.aplikasi ? ' · ' + p.aplikasi : '') + (p.pada ? ' · denyut ' + kpTgl(kpWib(new Date(p.pada)).iso) : '')) });
  const diam = perangkat.filter((p) => { const x = p.pada ? new Date(p.pada).getTime() : NaN; return !isFinite(x) || t - x > KP_DENYUT_MS; });
  tambah({ id: 'perangkatDenyut', blokir: true, ok: !diam.length, teks: 'Semua perangkat berdenyut dalam 24 jam terakhir', ket: diam.length ? 'tulisan offline dari perangkat ini untuk ' + nama + ' akan ditolak sesudah dikunci — nyalakan & sambungkan, atau nyatakan sudah tidak dipakai' : 'semua berdenyut',
    rincian: diam.map((p) => (p.nama || p.id) + ' · ' + (p.pada ? 'terakhir ' + kpTgl(kpWib(new Date(p.pada)).iso) : 'tanpa denyut') + (p.aplikasi ? ' · ' + p.aplikasi : '')),
    aksi: diam.filter((p) => !(Number(p.antrean) > 0) && !(Number(p.gagal) > 0)).map((p) => ({ id: String(p.id), label: (p.nama || p.id) + ' sudah tidak dipakai' })) });
  // ---- centang / keputusan
  const hari = kpHariTanpaTutup(bulan, kini, K.putusanHari);
  tambah({ id: 'hari', ok: hari.every((h) => !!h.putusan), teks: hari.length ? hari.length + ' hari tanpa tutup hari' : 'Tiap hari buka punya tutup hari',
    ket: hari.length ? 'tiap tanggal: libur (hanya hari tanpa nota) atau "tidak ditutup — diterima apa adanya" dengan alasan. Tutup hari TIDAK dibuat mundur — uang laci hari itu tidak bisa dihitung ulang.' : 'semua hari berjualan sudah ditutup', rincian: hari.map((h) => kpTgl(h.iso) + (h.adaJual ? ' · ' + h.nNota + ' nota' : ' · tanpa nota')) });
  const karcis = ambilPenjualan().filter((p) => (p.jenis === 'kasir_darurat_nominal' || p.perluKoreksi) && kpDalam(p.tanggal, R));
  tambah({ id: 'karcis', perluCentang: karcis.length > 0, ok: !karcis.length || !!C.karcis, teks: karcis.length ? karcis.length + ' karcis / nota rapikan belum dirinci' : 'Tidak ada karcis yang belum dirinci', ket: karcis.length ? 'sesudah dikunci, karcis ini tidak bisa dirinci lagi (' + RP(karcis.reduce((a, p) => a + (p.hargaTotal || 0), 0)) + ')' : 'bersih' });
  const bulanPajak = []; for (let i = Math.max(kpIdx(R.dari), kpIdx((kpPertama() || bulan).slice(0, 7))); i <= kpIdx(bulan); i++) bulanPajak.push(kpBulanStr(i));
  const belumLuar = bulanPajak.filter((k) => { try { const T = pjTahun(Number(k.slice(0, 4)), kini); const b = T.daftar.find((x) => x.key === k); return b && !b.lengkap; } catch (e) { return false; } });
  tambah({ id: 'omzetLuar', perluCentang: belumLuar.length > 0, ok: !belumLuar.length || !!C.omzetLuar, teks: 'Omzet di luar sistem ' + nama + ': ' + (belumLuar.length ? 'BELUM diisi' : 'sudah diisi / tidak perlu'), ket: belumLuar.length ? 'angka pajak ' + belumLuar.map(kpNamaBulan).join(', ') + ' belum lengkap — isi di Laporan › Pajak, atau centang untuk mengunci apa adanya' : 'lengkap' });
  const batch = ambilSemuaBatch().filter((b) => !b.stokAwal && !b.tutupBuku && kpDalam(b.tanggal, R)); const aduk = {}; ambilProduksi().forEach((p) => { if (!p.beliJadi && kpDalam(p.tanggal, R)) aduk[String(p.batchProduksi || p.id)] = true; });
  const bon = ambilUtangPemasokMutasi().filter((m) => kpDalam(m.tanggal, R) || (m.tipe === 'saldoAwal' && kpDalam(m.bonTanggal, R)));
  const nPem = batch.length + Object.keys(aduk).length + bon.length;
  tambah({ id: 'pembelian', perluCentang: nPem > 0, ok: !nPem || !!C.pembelian, teks: 'Periksa ulang kedatangan, adukan, dan utang pemasok ' + nama, ket: nPem ? batch.length + ' kedatangan · ' + Object.keys(aduk).length + ' adukan · ' + bon.length + ' catatan bon pemasok — sesudah dikunci tidak bisa dibetulkan (harga modal & utangnya tetap seperti tercatat)' : 'tidak ada' });
  const berbon = {}; ambilPenjualan().forEach((p) => { if (p.caraBayar === 'Kredit' && kpDalam(p.tanggal, R)) berbon[kunciPelanggan(p.namaPelanggan)] = true; }); ambilPiutangMutasi().forEach((m) => { if (kpDalam(m.tanggal, R)) berbon[kunciPelanggan(m.namaPelanggan)] = true; });
  let mirip = []; try { mirip = pasanganKembar(semuaOrang(kini)).filter((x) => berbon[x.a.kunci] || berbon[x.b.kunci]); } catch (e) { mirip = []; }
  tambah({ id: 'namaMirip', perluCentang: mirip.length > 0, ok: !mirip.length || !!C.namaMirip, teks: mirip.length ? mirip.length + ' pasang nama mirip punya bon di ' + nama : 'Tidak ada nama mirip yang berbon', ket: mirip.length ? 'satukan dulu sebelum dikunci — sesudahnya bon bulan ini tidak bisa pindah nama' : 'bersih', rincian: mirip.map((x) => '"' + x.a.nama + '" dan "' + x.b.nama + '"') });
  const akhirM = kpAkhirBulan(bulan); let upah = []; try { upah = aturUpah().aktif.map((o) => { const H = hitungUpah(o.nama, kini, 'semua'); const n = H.hariList.filter((d) => d.iso <= akhirM && d.nilai !== 0).length; return n ? { nama: o.nama, n, dari: H.mulai } : null; }).filter(Boolean); } catch (e) { upah = []; }
  tambah({ id: 'upah', perluCentang: upah.length > 0, ok: !upah.length || !!C.upah, teks: upah.length ? 'Upah ' + nama + ' belum dibayar semua' : 'Upah ' + nama + ' sudah dibayar dan dicatat', ket: upah.length ? 'kalau dibayar sesudah dikunci, biaya upahnya masuk bulan pembayaran (bukan ' + nama + ')' : 'bersih', rincian: upah.map((u) => u.nama + ' · ' + u.n + ' hari sejak ' + kpTgl(u.dari)) });
  const belum = butir.filter((b) => !b.ok);
  return { bulan, nama, rentang: R, butir, hari, boleh: !belum.length, belum: belum.length, blokir: belum.filter((b) => b.blokir).length };
}
/** Potret angka bulan M saat dikunci (disimpan di riwayat; mesin tidak membacanya): kas akhir bulan hilang begitu titik kas maju (peta R3). */
export function kpPotret(bulan) {
  const r = (n) => (n === null || n === undefined || !isFinite(n) ? null : Math.round(n)); const L = hitungLabaBersihRentang(bulan + '-01', kpAkhirBulan(bulan)); const N = hitungNeraca(kpAkhirBulan(bulan));
  return { omzet: r(L.omzetPenuh), marginKotor: r(L.margin), labaBersih: r(L.labaBersih), kas: r(N.kas), stok: r(N.stok), piutang: r(N.piutang), kasbon: r(N.kasbon), utangPemasok: r(N.utangPemasok), utangOwner: r(N.utangOwner), kekayaan: r(N.total) };
}
/** Kunci bulan M (dua ketukan di layar). akun = akun yang masuk (owner). */
export function susunKunciBulan(bulan, K, w, akun, kini) {
  if (!akun || akun.jenis !== 'owner') return { tolak: 'Hanya owner yang bisa mengunci bulan' };
  const c = kpCalon(kini); if (bulan !== c) return { tolak: c ? 'Yang bisa dikunci sekarang ' + kpNamaBulan(c) + ' — satu bulan sekali, berurutan' : 'Semua bulan yang sudah lewat sudah terkunci' };
  const D = kpDaftarPeriksa(bulan, kini, K); if (!D.boleh) return { tolak: D.belum + ' butir daftar periksa belum beres' + (D.blokir ? ' (' + D.blokir + ' memblokir)' : '') };
  const Kd = kpKeadaan(); const riwayat = Kd.dok && Array.isArray(Kd.dok.riwayat) ? Kd.dok.riwayat.slice() : [];
  const entri = { aksi: 'kunci', bulan, pada: w.kini, olehUid: akun.uid, alasan: '', periksa: D.butir.map((b) => ({ id: b.id, ok: b.ok, teks: String(b.teks).slice(0, 120), ket: String(b.ket).slice(0, 200) })), hari: D.hari.map((h) => ({ iso: h.iso, jenis: h.putusan.jenis, alasan: String(h.putusan.alasan || '').trim().slice(0, 120), nNota: h.nNota })), potret: kpPotret(bulan) };
  const data = Object.assign({}, Kd.dok || {}, { id: KP_ID, sampaiBulan: bulan, riwayat: riwayat.concat([entri]), tanggal: w.tanggal, jam: w.jam });
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { kabar: kpNamaBulan(bulan) + ' DIKUNCI. Catatan bertanggal ' + kpNamaBulan(bulan) + (Kd.sampai ? '' : ' dan sebelumnya') + ' tidak bisa ditambah, diubah, atau dihapus lagi — kesalahan dibetulkan dengan catatan hari ini.', kabarAwas: false, kpSiap: false } };
}
/** Buka kunci bulan terakhir: satu langkah mundur, alasan ≥ 10 huruf; bulan bersetoran pajak minta nama bulannya diketik ulang. */
export function kpSetoranBulan(bulan) { return cacheMentah('pajakSetoran').filter((s) => s.masaPajak === bulan); }
export function susunBukaBulan(alasan, ketikUlang, w, akun) {
  if (!akun || akun.jenis !== 'owner') return { tolak: 'Hanya owner yang bisa membuka kunci' };
  const Kd = kpKeadaan(); if (!Kd.sampai) return { tolak: 'Belum ada bulan yang terkunci' }; const bulan = Kd.sampai;
  const a = String(alasan || '').trim(); if (a.length < 10) return { tolak: 'Alasan membuka kunci wajib, minimal 10 huruf — jejak ini dibaca lagi nanti' };
  const setor = kpSetoranBulan(bulan);
  if (setor.length && String(ketikUlang || '').trim().toLowerCase() !== kpNamaBulan(bulan).toLowerCase()) return { tolak: 'AWAS: ' + kpNamaBulan(bulan) + ' sudah punya ' + setor.length + ' setoran pajak — angka yang sudah dilaporkan bisa bergeser. Ketik "' + kpNamaBulan(bulan) + '" untuk tetap membuka', perluKetik: kpNamaBulan(bulan) };
  const riwayat = Array.isArray(Kd.dok.riwayat) ? Kd.dok.riwayat.slice() : [];
  const data = Object.assign({}, Kd.dok, { id: KP_ID, sampaiBulan: kpGeser(bulan, -1), riwayat: riwayat.concat([{ aksi: 'buka', bulan, pada: w.kini, olehUid: akun.uid, alasan: a.slice(0, 200), setoranPajak: setor.length }]), tanggal: w.tanggal, jam: w.jam });
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { kabar: kpNamaBulan(bulan) + ' DIBUKA lagi (' + a + '). Yang masih terkunci: ' + kpNamaBulan(kpGeser(bulan, -1)) + ' dan sebelumnya.', kabarAwas: true, kpBuka: null } };
}
/** Tenggang layar (hari, ≥ minimal rules). */
export function susunAturKunci(tenggang, w) {
  const n = Math.round(Number(String(tenggang || '').replace(/\D/g, ''))); if (!(n >= KP_TENGGANG_MIN) || n > 20) return { tolak: 'Tenggang ' + KP_TENGGANG_MIN + '–20 hari' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: KP_ID_ATUR, tenggang: n, tanggal: w.tanggal, jam: w.jam } }], patch: { kabar: 'Tenggang kunci ' + n + ' hari — bulan lalu bisa dikunci mulai tanggal ' + (n + 1), kabarAwas: false, kpAtur: null } };
}
/** Perangkat lama yang sudah tidak dipakai: catatan denyutnya dihapus (kalau perangkatnya hidup lagi, denyutnya tercatat ulang sendiri). */
export function susunLupakanPerangkat(id, yakin) {
  const p = cacheMentah('perangkat').find((x) => String(x.id) === String(id)); if (!p) return { tolak: 'Perangkat itu sudah tidak ada di daftar' };
  if (Number(p.antrean) > 0 || Number(p.gagal) > 0) return { tolak: (p.nama || p.id) + ' terakhir melaporkan ' + (Number(p.antrean) || 0) + ' antrean / ' + (Number(p.gagal) || 0) + ' ditolak — nyalakan & kirim dulu, tidak bisa dilupakan' };
  if (!yakin) return { tolak: 'Nyatakan ' + (p.nama || p.id) + ' sudah tidak dipakai? Kalau ternyata masih dipakai dan menyimpan nota offline, nota bulan terkunci darinya akan ditolak. Ketuk sekali lagi', perluYakin: true };
  return { hapus: [{ koleksi: 'perangkatStatus', id: p.id }], patch: { kabar: (p.nama || p.id) + ' dikeluarkan dari daftar denyut', kabarAwas: false, kpYakinLupa: null } };
}
/** Beranda › Perlu perhatian (owner): satu baris kalau bulan lalu sudah lewat tenggang dan belum dikunci. Diam selama kunci belum bisa dipakai (25b). */
export function kpPerhatian(kini, uji) {
  if (!KP_SIAP_25B && !(uji && uji.siap25b)) return [];
  const c = kpCalon(kini); if (!c || !kpBolehDikunci(c, kini, kunciTenggang())) return [];
  const W = kpWib(kini); const telat = kpIdx(c) < W.idx - 1;
  return [{ teks: 'Kunci bulan: ' + kpNamaBulan(c) + ' belum dikunci' + (telat ? ' (sudah lebih dari sebulan)' : ''), nilai: 'Uang › Tutup buku', awas: telat }];
}
/** Status satu bulan untuk layar lain (laporan, pajak). */
export const kpStatusBulan = (bulan) => { const s = kunciSampai(); return s && kpIdx(bulan) <= kpIdx(s) ? 'terkunci' : 'terbuka'; };

// ---- catatan antre yang DITOLAK server (Menu › Sistem › Perangkat): alasan "bulan terkunci" + tawaran mencatat ulang bertanggal hari ini ----
// Dicatat ulang hari ini HANYA untuk kiriman yang semuanya dokumen BARU di koleksi yang tanggalnya memang boleh bergeser ke hari ini (nota, bayar bon, kantong,
// kasbon, belanja harian, cocokkan, amplop, setoran, modal, utang owner, pindah uang, retur, adukan). Tutup hari, biaya bulanan, kedatangan, slip, titik kas,
// dan bon pemasok TIDAK — tanggalnya bagian dari artinya. Tanggal aslinya ditulis di field teks yang SUDAH ADA di koleksi itu.
const KP_HARI_INI = { penjualan: 'alasanKoreksi', piutangMutasi: 'catatan', stokBahanLiteran: 'catatan', stokBahanKemasan: 'catatan', kasbonMutasi: 'catatan', pengeluaranHarian: 'keterangan',
  penyesuaianStok: 'alasan', penyesuaianKemasan: 'alasan', amplopLaba: 'catatan', modalOwner: 'catatan', setoranKas: 'catatan', utangOwnerMutasi: 'catatan', pindahUang: 'alasan', retur: 'catatan', produksiKemasan: 'keterangan' };
export function kpAlasanDitolak(entri, dokAda) {
  const s = kunciSampai(); const dok = (entri && entri.dokumen) || []; const kena = dok.filter((d) => { const b = kpBulanDok(d.koleksi, d.data); return s && b !== null && b <= kpIdx(s); });
  if (!kena.length) return null;
  const bulan = kpBulanStr(Math.max.apply(null, kena.map((d) => kpBulanDok(d.koleksi, d.data))));
  // hanya kiriman yang SEMUANYA dokumen baru; dokumen bertanggal hanya dari koleksi yang tanggalnya boleh bergeser ke hari ini
  const bisa = dok.every((d) => kpBulanDok(d.koleksi, d.data) === null || !!KP_HARI_INI[d.koleksi]) && !dok.some((d) => dokAda && dokAda(d.koleksi, d.data && d.data.id));
  return { bulan, kalimat: kpKalimat(bulan, bisa ? 'catat ulang bertanggal hari ini (tanggal aslinya ditulis di catatannya)' : 'kiriman ini tidak bisa dicatat ulang hari ini; buang, lalu betulkan dengan catatan hari ini'), bisaHariIni: bisa, n: kena.length };
}
/** Dokumen kiriman yang ditolak, dipindah ke hari ini. Kembali [{ koleksi, data }]. */
export function kpKeHariIni(dokumen, w) {
  return (dokumen || []).map((d) => {
    const data = Object.assign({}, d.data); const f = KP_HARI_INI[d.koleksi]; const b = kpBulanDok(d.koleksi, data);
    if (b === null || !f) return { koleksi: d.koleksi, data };
    const asli = (data.tanggal || '?') + (data.jam ? ' ' + data.jam : '');
    data.tanggal = w.tanggal; if (data.jam !== undefined) data.jam = w.jam;
    data[f] = (data[f] ? String(data[f]) + ' · ' : '') + 'tanggal asli ' + asli + ' (bulan terkunci, dicatat ulang ' + w.tanggal + ')';
    return { koleksi: d.koleksi, data };
  });
}
export { kpNamaBulan as kpNama, kpWib as kpWaktu };
