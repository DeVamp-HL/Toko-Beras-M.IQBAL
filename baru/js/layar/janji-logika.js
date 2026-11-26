// TANGGAL JANJI — paket tanggal janji (owner 27 Nov 2026; sensus ulang 26 Nov: B55 B58 B60 B61 B65). Logika TANPA DOM, nama berawalan jn (bundel uji jsc satu
// lingkup). Dijaga alat-uji/uji_tanggal_janji.py (jsc + statis + kontrol) dan alat-uji/periksa_rules.py (kolom janji pemasok = rules v24).
//
// Sebelum paket ini sistem tidak pernah menyimpan KAPAN barang dijanjikan datang (dari pemasok) atau sampai (ke pelanggan) — lima butir sensus tidak bisa dihitung.
// Keputusan owner 27 Nov 2026 (satu AskUserQuestion):
//  1. JANJI DATANG PEMASOK — owner (Harga › Belanja: waktu kirim pesanan, atau sesudah pemasok membalas) + Penjaga laci dari tablet (Barang masuk). Rules v24
//     stafJanjiPemasok: Penjaga laci membaca pesananPemasok & mengubah kolom JN_KOLOM_JANJI saja (= akses.js KOLOM_JANJI_PEMASOK).
//  2. JANJI ANTAR — "Tanggal kirim" pesanan pelanggan (pesanan.tanggalKirim, owner & Penjaga laci sejak rules v11) + isian "dijanjikan sampai" di Bayar › Antar
//     (kolom janjiTanggal surat jalan, ditulis saat surat jalan lahir — rules v10 stafBuatSJ tidak membatasi kolom baru). Bawaan isian = janji pesanannya,
//     atau hari itu.
//  3. TOLERANSI telat bawaan 0 hari — setelan owner, terpisah untuk pemasok & antar (aturanToko/janji).
//  4. UTUH = jumlah karung / barang yang datang ≥ yang dipesan. Kurang timbang per karung TIDAK membuat "sebagian" (sudah dicatat di klaim Barang masuk).
// Pilihan saya sendiri (ditulis di BACA-DULU):
//  - Janji yang DIHITUNG = janji PERTAMA. Dibetulkan di hari yang sama = salah ketik, bukan geser. Geser sesudahnya tercatat & disebut, tidak menghapus telatnya.
//  - Data lama tanpa janji = "belum ada tanggal janji" — DISEBUT jumlahnya, tidak masuk tepat / telat.
//  - Telat (hari) = tanggal datang / sampai − janji pertama; tepat = telat ≤ toleransi. Rata-rata keterlambatan = rata-rata hari telat semua yang berjanji & sudah
//    datang (yang lebih cepat = 0 hari), terlama ikut disebut. Gagal antar = tidak tepat janji.
//  - Barang dari pemasok yang "memenuhi" satu pesanan = kedatangan pemasok itu di HARI datangnya (aturan datang = Belanja, bpPesananDatang), sesudah pesanan,
//    yang belum dipakai pesanan lain (tertua dulu). Pesanan yang ditandai datang tanpa Barang masuk / kedatangannya sudah diarsip = isinya "tidak terukur".
//  - Barang ke pelanggan dicocokkan per baris katalog pesanan dengan baris nota yang berlaku (karung = merek & berat, kemasan = nama & ukuran, literan = merek /
//    wadah). Pesanan teks lama = "tidak terukur". Antar tanpa pesanan tidak punya pembanding isi (yang dikirim = notanya sendiri).
//  - Jendela hitungan: N hari terakhir menurut tanggal pesanan / surat jalan dibuat (bawaan 90). Daftar "lewat janji" = semua yang masih ditunggu, tanpa jendela.
// MESIN UANG TIDAK DISENTUH — semua baca saja kecuali jnSusunAtur (setelan owner) & jnSusunJanjiPemasok (kolom janji pesanan ke pemasok).
import { ambilPesananPemasok, ambilPesanan, ambilSuratJalan, ambilSemuaBatch, ambilPenjualanSemua, cacheMentah, ingatPerVersi, ringkasArsip } from '../data/toko.js';
import { kunciPelanggan, kunciKemasan, penjualanMasihBerlaku } from '../mesin/pembantu.js';
import { hariIniIso, tanggalPendek } from '../inti/format.js';
import { pemasokSungguhan, bpPesananDatang } from './bon-pemasok-logika.js';
import { poBarisSah, poKunciBaris } from './pesanan-logika.js';

export const JN_KOLOM_JANJI = ['janjiTanggal', 'janjiRiwayat'];   // = akses.js KOLOM_JANJI_PEMASOK = rules v24 stafJanjiPemasok (+ atribusi)
export const JN_RIWAYAT_MAKS = 30;                                // = rules v24 janjiRiwayat.size() <= 30
export const JN_ATUR_BAWAAN = { tolPemasok: 0, tolAntar: 0 };      // owner 27 Nov 2026: bawaan 0 hari
export const JN_TOL_MAKS = 14;
export const JN_HARI_BAWAAN = 90;
export const JN_HARI_PILIHAN = [30, 90, 180];
export const JN_KEADAAN = { tepat: 'tepat janji', telat: 'telat', gagal: 'gagal antar', lewat: 'lewat janji', menunggu: 'menunggu', tanpaJanji: 'belum ada tanggal janji', batal: 'batal' };

// ---------- tanggal ----------
const jnHariKe = (iso) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || '')); return m ? Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000) : null; };
const jnIso = (n) => new Date(n * 86400000).toISOString().slice(0, 10);
export const jnTanggalSah = (iso) => { const n = jnHariKe(iso); return n !== null && jnIso(n) === String(iso); };
export const jnTambahHari = (iso, n) => jnIso(jnHariKe(iso) + n);
export const jnSelisih = (a, b) => jnHariKe(a) - jnHariKe(b);
const jnMs = (x) => { if (typeof x === 'number' && isFinite(x)) return x; const t = Date.parse(String(x || '')); return isFinite(t) ? t : null; };
/** Cap waktu tersimpan (ISO UTC / ms) → tanggal SETEMPAT (WIB di perangkat toko; memori waktu lokal vs UTC). Cacat → ''. */
const jnHariDari = (pada) => { const t = jnMs(pada); return t === null ? '' : hariIniIso(new Date(t)); };
const jnIsoKini = (kini) => hariIniIso(kini instanceof Date ? kini : new Date(kini || Date.now()));
/** Saat dokumen dibuat (tanggal + jam WIB tersimpan) → ISO, null bila tanggalnya tidak ada. */
const jnPadaDibuat = (d) => (/^\d{4}-\d{2}-\d{2}$/.test(String((d && d.tanggal) || '')) ? d.tanggal + 'T' + (/^\d{2}:\d{2}/.test(String(d.jam || '')) ? String(d.jam).slice(0, 5) : '00:00') + ':00+07:00' : null);
const jnTgl = (iso) => (iso ? tanggalPendek(iso).replace(/ \d{4}$/, '') : '');
export const jnHariTeks = (h) => (h === null || h === undefined || !isFinite(h) ? '—' : h < 0.05 ? '0 hari' : '±' + String(Math.round(h * 10) / 10).replace('.', ',') + ' hari');

// ---------- setelan owner ----------
export function jnAtur() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'janji') || null;
  const ambil = (k) => { const n = a ? Number(a[k]) : NaN; return a && a[k] !== '' && a[k] !== null && a[k] !== undefined && isFinite(n) && Math.round(n) === n && n >= 0 && n <= JN_TOL_MAKS ? n : null; };
  const tp = ambil('tolPemasok'); const ta = ambil('tolAntar');
  return { tolPemasok: tp === null ? JN_ATUR_BAWAAN.tolPemasok : tp, tolAntar: ta === null ? JN_ATUR_BAWAAN.tolAntar : ta, dariOwner: { pemasok: tp !== null, antar: ta !== null } };
}
/** isi = { tolPemasok, tolAntar } (teks; kosong = tetap). → { dokumen, patch } atau { tolak }. Owner saja (aturanToko). */
export function jnSusunAtur(isi, w) {
  const kini = jnAtur(); const o = isi || {}; const data = { id: 'janji', tanggal: w.tanggal, jam: w.jam };
  for (const [k, nama] of [['tolPemasok', 'Toleransi pemasok'], ['tolAntar', 'Toleransi antar']]) {
    const t = String(o[k] === undefined || o[k] === null ? '' : o[k]).trim();
    if (!t) { data[k] = kini[k]; continue; }
    if (!/^\d{1,2}$/.test(t) || Number(t) > JN_TOL_MAKS) return { tolak: nama + ': 0–' + JN_TOL_MAKS + ' hari, angka bulat' };
    data[k] = Number(t);
  }
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { aturJn: null, kabar: 'Toleransi telat disimpan — pemasok ' + data.tolPemasok + ' hari · antar ' + data.tolAntar + ' hari', kabarAwas: false } };
}

// ---------- janji pertama ----------
/**
 * seq = [{ nilai: 'YYYY-MM-DD' | '', pada }] — janji yang berlaku SEJAK `pada` ('' = dikosongkan). → { awal, akhir, sejak, geser: [{ dari, ke, hari }] }.
 * awal = janji PERTAMA yang dihitung: yang berlaku di akhir hari saat janji pertama kali diisi (dibetulkan di hari yang sama = salah ketik, bukan geser).
 * geser = perubahan sesudah hari itu (dibetulkan lagi di hari yang sama = satu geser). akhir = janji yang tersimpan sekarang.
 */
export function jnJanjiDariUrutan(seq) {
  const s = (seq || []).filter((x) => x && jnMs(x.pada) !== null).slice().sort((a, b) => jnMs(a.pada) - jnMs(b.pada));
  const nilai = (x) => (jnTanggalSah(x.nilai) ? String(x.nilai) : '');
  let awal = '', sejak = '', i = 0;
  for (; i < s.length; i++) {
    const v = nilai(s[i]); const hari = jnHariDari(s[i].pada);
    if (!awal) { if (v) { awal = v; sejak = hari; } continue; }
    if (hari === sejak) { awal = v; if (!v) sejak = ''; continue; }
    break;
  }
  const geser = []; let kini = awal;
  // geser yang dibetulkan lagi di hari yang sama = satu geser (dari janji sebelum hari itu ke tanggal terakhir hari itu); balik ke janji semula = batal geser
  for (; i < s.length; i++) { const v = nilai(s[i]); const hari = jnHariDari(s[i].pada); if (!v || v === kini) continue; const t = geser[geser.length - 1];
    if (t && t.hari === hari) { if (v === t.dari) geser.pop(); else t.ke = v; } else geser.push({ dari: kini, ke: v, hari }); kini = v; }
  return { awal, akhir: s.length ? (nilai(s[s.length - 1]) || kini) : '', sejak, geser };
}
/** Janji datang satu pesanan ke pemasok (janjiRiwayat; dokumen tanpa riwayat tapi bertanggal janji = diisi saat dibuat). */
export function jnJanjiPemasok(p) {
  const r = Array.isArray(p && p.janjiRiwayat) ? p.janjiRiwayat : [];
  const seq = r.map((x) => ({ nilai: x && x.tanggal, pada: x && x.pada }));
  if (!seq.length && p && jnTanggalSah(p.janjiTanggal)) seq.push({ nilai: p.janjiTanggal, pada: jnPadaDibuat(p) });
  return jnJanjiDariUrutan(seq);
}
/**
 * Janji kirim satu pesanan pelanggan. Sejak paket ini ubahan tanggal kirim membawa kirimDari / kirimKe di baris riwayatStatus ubahnya (pesanan-logika
 * poSusunPesanan — riwayatStatus sudah di kolom ubah Penjaga laci rules v11). Pesanan yang diubah sebelum paket ini: tanggal kirim sekarang = janji sejak dibuat.
 */
export function jnJanjiPesanan(ps) {
  const rr = (Array.isArray(ps && ps.riwayatStatus) ? ps.riwayatStatus : []).filter((x) => x && x.ubah && x.kirimKe !== undefined);
  const kini = ps && jnTanggalSah(ps.tanggalKirim) ? String(ps.tanggalKirim) : '';
  const mula = rr.length ? (jnTanggalSah(rr[0].kirimDari) ? String(rr[0].kirimDari) : '') : kini;
  return jnJanjiDariUrutan([{ nilai: mula, pada: jnPadaDibuat(ps) }].concat(rr.map((x) => ({ nilai: x.kirimKe, pada: x.pada }))));
}
/** "janji 28 Nov" · "janji 28 Nov (digeser ke 30 Nov)" · "belum ada tanggal janji". */
export function jnKataJanji(J) {
  if (!J || !J.awal) return 'belum ada tanggal janji';
  return 'janji ' + jnTgl(J.awal) + (J.geser && J.geser.length ? ' (digeser ke ' + jnTgl(J.geser[J.geser.length - 1].ke) + ')' : '');
}

// ---------- satu baris (pesanan ke pemasok / kiriman ke pelanggan) ----------
function jnBaris(o, iso, tol) {
  const J = o.janji; let keadaan, telat = null;
  if (o.batal) keadaan = 'batal';
  else if (!J.awal) keadaan = 'tanpaJanji';
  else if (o.gagal) { keadaan = 'gagal'; telat = Math.max(0, jnSelisih(o.gagalHari || iso, J.awal)); }
  else if (o.sampai) { telat = jnSelisih(o.sampai, J.awal); keadaan = telat <= tol ? 'tepat' : 'telat'; }
  else { telat = Math.max(0, jnSelisih(iso, J.awal)); keadaan = jnSelisih(iso, J.awal) > tol ? 'lewat' : 'menunggu'; }
  // isi: hanya yang PUNYA pembanding (pesanan) — antar tanpa pesanan = '' (yang dikirim = notanya sendiri); ada pesanan tapi tak bisa dicocokkan = tidak terukur
  const isi = o.batal ? '' : o.pesan > 0 && o.datang !== null && o.datang !== undefined ? (o.datang >= o.pesan ? 'utuh' : 'sebagian') : o.isiTanpaUkur ? 'tidakTerukur' : '';
  return Object.assign({}, o, { keadaan, telat, isi, tol });
}
/** Kalimat satu baris: "tepat janji" · "telat 2 hari" · "lewat janji 1 hari — masih ditunggu" · "menunggu, janji 28 Nov" · "belum ada tanggal janji". */
export function jnKataBaris(x) {
  if (!x) return '';
  const j = jnKataJanji(x.janji); const isi = x.isi === 'utuh' ? ' · utuh' : x.isi === 'sebagian' ? ' · sebagian (' + x.datang + ' dari ' + x.pesan + ' ' + x.satuan + ')' : '';
  if (x.keadaan === 'tepat') return (x.telat < 0 ? 'lebih cepat ' + (-x.telat) + ' hari' : x.telat > 0 ? 'telat ' + x.telat + ' hari, masih dalam toleransi' : 'tepat janji') + ' · ' + j + isi;
  if (x.keadaan === 'telat') return 'telat ' + x.telat + ' hari · ' + j + isi;
  if (x.keadaan === 'gagal') return 'gagal antar · ' + j;
  if (x.keadaan === 'lewat') return 'lewat janji ' + x.telat + ' hari — masih ditunggu · ' + j;
  if (x.keadaan === 'menunggu') return 'menunggu · ' + j;
  if (x.keadaan === 'batal') return 'dibatalkan';
  return 'belum ada tanggal janji' + isi;
}

// ---------- pesanan ke pemasok ----------
const jnUrutWaktu = (a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || String(a.jam || '').localeCompare(String(b.jam || '')) || (Number(a.id) || 0) - (Number(b.id) || 0);
const jnKarungBatch = (b) => (Array.isArray(b.merkList) ? b.merkList : []).reduce((a, r) => a + (Number(r && r.jumlahKarung) || 0), 0);
const jnKarungPesan = (p) => Number(p.karung) || (Array.isArray(p.baris) ? p.baris : []).reduce((a, b) => a + (Number(b && b.karung) || 0), 0);
/** Semua pesanan ke pemasok (tanpa jendela), tertua dulu, dengan keadaan janji & isi. Diingat per versi data + hari + toleransi. */
export function jnPemasokSemua(kini) {
  const iso = jnIsoKini(kini); const tol = jnAtur().tolPemasok;
  return ingatPerVersi('jnPemasokSemua|' + iso + '|' + tol, () => jnPemasokHitung(iso, tol));
}
function jnPemasokHitung(iso, tol) {
  const batch = ambilSemuaBatch().filter((b) => b && !b.stokAwal && !b.lahirBuku && pemasokSungguhan(b.pemasok)); const RA = ringkasArsip(); const pakai = {};
  return (ambilPesananPemasok() || []).filter((p) => p && pemasokSungguhan(p.pemasok)).slice().sort(jnUrutWaktu).map((p) => {
    const batal = p.status === 'batal';
    const D = batal ? { datang: false, tanggal: '' } : p.status === 'datang' && p.datangTanggal ? { datang: true, tanggal: String(p.datangTanggal), manual: true } : bpPesananDatang(p, batch, p.status === 'datang' ? null : RA);
    let datang = null; let nDatang = 0;
    if (D.datang && D.tanggal) {
      const nama = String(p.pemasok).trim();
      const kd = batch.filter((b) => String(b.pemasok || '').trim() === nama && String(b.tanggal || '') === String(D.tanggal) && !pakai[String(b.id)]
        && ((b.tanggal || '') > (p.tanggal || '') || ((b.tanggal || '') === (p.tanggal || '') && (b.jam || '') > (p.jam || ''))));
      if (kd.length) { kd.forEach((b) => { pakai[String(b.id)] = 1; }); datang = kd.reduce((a, b) => a + jnKarungBatch(b), 0); nDatang = kd.length; }
    }
    return jnBaris({ jenis: 'pemasok', id: String(p.id), nama: String(p.pemasok).trim(), kunci: kunciPelanggan(p.pemasok), dibuat: String(p.tanggal || ''), jam: String(p.jam || ''), batal,
      janji: jnJanjiPemasok(p), sampai: D.datang ? String(D.tanggal || '') : '', gagal: false, pesan: jnKarungPesan(p), datang, nKedatangan: nDatang, satuan: 'karung',
      manual: !!D.manual, isiTanpaUkur: !!D.datang, disimpanMenunggu: p.status === 'menunggu' }, iso, tol);
  });
}
/** Satu pesanan ke pemasok (bentuk jnBaris) menurut id, atau null. */
export const jnPesananPemasok = (id, kini) => jnPemasokSemua(kini).find((x) => x.id === String(id)) || null;

// ---------- kiriman ke pelanggan (surat jalan + pesanan tanpa surat jalan) ----------
/** Kunci satu baris nota = poKunciBaris baris pesanan (karung: merek & berat · kemasan: nama & ukuran · literan: merek / wadah) + jumlahnya. null = bukan barang pesanan. */
export function jnKunciNota(r) {
  if (!r) return null;
  if (r.jenis === 'karung') return { kunci: 'karung|' + String(r.merkSumber || '') + '|' + (Number(r.beratKarungAcuan) || 50), n: Number(r.jumlahKarung) || 0 };
  if (r.jenis === 'kemasan' && !r.setengahDari) return { kunci: 'kemasan|' + kunciKemasan(r.namaProduk, r.ukuranKemasan), n: Number(r.jumlahUnit) || 0 };
  if (r.jenis === 'literan') return { kunci: 'literan|' + String(r.dariWadah || r.merkSumber || ''), n: Number(r.jumlahLiter) || 0 };
  return null;
}
/** Isi pesanan pelanggan dibanding notanya: { pesan (barang di pesanan), datang (barang yang lengkap) } · null = tidak bisa dicocokkan. */
function jnIsiPesanan(ps, rows) {
  const baris = poBarisSah(ps && ps.baris); if (!baris.length || !rows || !rows.length) return null;
  const per = {}; rows.filter(penjualanMasihBerlaku).forEach((r) => { const k = jnKunciNota(r); if (k && k.n > 0) per[k.kunci] = (per[k.kunci] || 0) + k.n; });
  const lengkap = baris.filter((b) => (per[poKunciBaris(b)] || 0) + 1e-9 >= Number(b.jumlah)).length;
  return { pesan: baris.length, datang: lengkap };
}
/** Saat pertama / terakhir satu status di riwayat (jam ISO, bukan baris ubah) → ms, null bila tidak tercatat. */
function jnSaat(p, status, terakhir) {
  const rr = (Array.isArray(p.riwayatStatus) ? p.riwayatStatus : []).filter((x) => x && x.status === status && !x.ubah && jnMs(x.pada) !== null);
  const r = terakhir ? rr[rr.length - 1] : rr[0]; return r ? jnMs(r.pada) : null;
}
export function jnPelangganSemua(kini) {
  const iso = jnIsoKini(kini); const tol = jnAtur().tolAntar;
  return ingatPerVersi('jnPelangganSemua|' + iso + '|' + tol, () => jnPelangganHitung(iso, tol));
}
function jnPelangganHitung(iso, tol) {
  const SJ = (ambilSuratJalan() || []).filter(Boolean); const PS = (ambilPesanan() || []).filter(Boolean);
  const butuh = {}; SJ.forEach((s) => { if (s.trxIdJual) butuh[String(s.trxIdJual)] = 1; }); PS.forEach((p) => { if (p.trxIdJual) butuh[String(p.trxIdJual)] = 1; });
  const nota = {}; (ambilPenjualanSemua() || []).forEach((r) => { const t = r && String(r.trxId || ''); if (t && butuh[t]) (nota[t] = nota[t] || []).push(r); });
  const berlaku = (t) => { const b = nota[String(t || '')]; return b && b.length ? b.some(penjualanMasihBerlaku) : null; };
  const psPerTrx = {}; PS.forEach((p) => { if (p.trxIdJual && p.status !== 'batal') psPerTrx[String(p.trxIdJual)] = p; });
  const sjPerTrx = {}; const out = [];
  SJ.forEach((s) => {
    if (s.status === 'batal' || berlaku(s.trxIdJual) === false) return;   // surat jalan batal / notanya dibatalkan = bukan kiriman
    sjPerTrx[String(s.trxIdJual || '')] = 1;
    const ps = psPerTrx[String(s.trxIdJual || '')] || null; const Jp = ps ? jnJanjiPesanan(ps) : null;
    const padaSJ = (Array.isArray(s.riwayatStatus) && s.riwayatStatus[0] && s.riwayatStatus[0].pada) || jnPadaDibuat(s);
    let J = Jp && Jp.awal ? Jp : jnJanjiDariUrutan(jnTanggalSah(s.janjiTanggal) ? [{ nilai: s.janjiTanggal, pada: padaSJ }] : []);
    // janji pesanan lebih dulu tercatat; tanggal lain di surat jalannya = digeser saat berangkat
    if (Jp && Jp.awal && jnTanggalSah(s.janjiTanggal) && s.janjiTanggal !== (Jp.akhir || Jp.awal)) J = Object.assign({}, Jp, { akhir: s.janjiTanggal, geser: Jp.geser.concat([{ dari: Jp.akhir || Jp.awal, ke: s.janjiTanggal, hari: String(s.tanggal || ''), suratJalan: true }]) });
    const rGagal = (Array.isArray(s.riwayatStatus) ? s.riwayatStatus : []).filter((x) => x && x.status === 'gagal').pop();
    const sampai = s.status === 'diterima' ? (jnTanggalSah(s.diterimaTanggal) ? String(s.diterimaTanggal) : jnHariDari(s.diterimaPada) || String(s.tanggal || '')) : '';
    const I = ps ? jnIsiPesanan(ps, nota[String(s.trxIdJual || '')]) : null;
    out.push(jnBaris({ jenis: 'antar', id: String(s.id), nama: String(s.namaPelanggan || '').trim() || 'pembeli', kunci: kunciPelanggan(s.namaPelanggan), dibuat: String(s.tanggal || ''), jam: String(s.jam || ''),
      batal: false, janji: J, sampai, gagal: s.status === 'gagal', gagalHari: rGagal ? jnHariDari(rGagal.pada) : '', pesan: I ? I.pesan : 0, datang: I ? I.datang : null, satuan: 'barang',
      noSJ: String(s.noSJ || ''), pesananId: ps ? String(ps.id) : '', isiTanpaUkur: !!ps && !I }, iso, tol));
  });
  PS.forEach((p) => {
    if (p.status === 'batal' || (p.trxIdJual && sjPerTrx[String(p.trxIdJual)])) return;   // sudah dihitung lewat surat jalannya
    if (p.status === 'dibayar' && berlaku(p.trxIdJual) === false) return;
    const tA = jnSaat(p, 'diantar', false); const tN = p.status === 'dibayar' ? jnSaat(p, 'dibayar', true) : null;
    const ms = [tA, tN].filter((x) => x !== null); let sampai = ms.length ? jnHariDari(Math.min.apply(null, ms)) : '';
    if (!sampai && p.status === 'dibayar') { const b = nota[String(p.trxIdJual || '')]; sampai = b && b[0] ? String(b[0].tanggal || '') : ''; }
    if (!sampai && p.status === 'diantar') sampai = String(p.tanggal || '');
    const I = p.status === 'dibayar' ? jnIsiPesanan(p, nota[String(p.trxIdJual || '')]) : null;
    out.push(jnBaris({ jenis: 'pesanan', id: String(p.id), nama: String(p.namaPelanggan || '').trim() || 'pemesan', kunci: kunciPelanggan(p.namaPelanggan), dibuat: String(p.tanggal || ''), jam: String(p.jam || ''),
      batal: false, janji: jnJanjiPesanan(p), sampai, gagal: false, pesan: I ? I.pesan : 0, datang: I ? I.datang : null, satuan: 'barang', status: p.status || 'dipesan',
      isiTanpaUkur: p.status === 'dibayar' && !I }, iso, tol));
  });
  return out.sort(jnUrutWaktu);
}

// ---------- ringkasan ----------
export function jnRingkasBaris(rows) {
  const R = { tepat: 0, telat: 0, gagal: 0, menunggu: 0, lewat: 0, tanpaJanji: 0, digeser: 0, jumlahTelat: 0, nDatang: 0, maksTelat: 0, utuh: 0, sebagian: 0, tidakTerukur: 0, semua: 0 };
  (rows || []).forEach((x) => {
    if (!x || x.keadaan === 'batal') return; R.semua += 1; R[x.keadaan] += 1;
    if (x.keadaan === 'tepat' || x.keadaan === 'telat') { const t = Math.max(0, x.telat); R.nDatang += 1; R.jumlahTelat += t; if (t > R.maksTelat) R.maksTelat = t; }
    if (x.janji && x.janji.awal && x.janji.geser.length) R.digeser += 1;
    if (x.isi === 'utuh') R.utuh += 1; else if (x.isi === 'sebagian') R.sebagian += 1; else if (x.isi === 'tidakTerukur') R.tidakTerukur += 1;
  });
  R.n = R.tepat + R.telat + R.gagal; R.pct = R.n ? R.tepat / R.n * 100 : null; R.rataTelat = R.nDatang ? R.jumlahTelat / R.nDatang : null;
  R.nIsi = R.utuh + R.sebagian; R.pctUtuh = R.nIsi ? R.utuh / R.nIsi * 100 : null;
  return R;
}
const jnPct = (x) => (x === null || x === undefined ? '—' : String(Math.round(x * 10) / 10).replace('.', ',') + ' %');
function jnKalimat(R, kata, N) {
  const a = R.n ? R.tepat + ' dari ' + R.n + ' ' + kata.tepat + ' (' + jnPct(R.pct) + ')' + (R.nDatang ? ' · telat rata-rata ' + jnHariTeks(R.rataTelat) + (R.maksTelat ? ', terlama ' + R.maksTelat + ' hari' : '') : '') + (R.gagal ? ' · ' + R.gagal + ' gagal antar' : '')
    : 'belum ada ' + kata.benda + ' berjanji yang sudah ' + kata.selesai;
  const b = R.nIsi ? R.utuh + ' dari ' + R.nIsi + ' ' + kata.utuh + ' (' + jnPct(R.pctUtuh) + ')' + (R.sebagian ? ', ' + R.sebagian + ' sebagian' : '') : '';
  const c = [R.lewat ? R.lewat + ' lewat janji & masih ditunggu' : '', R.menunggu ? R.menunggu + ' menunggu (belum lewat janji)' : '', R.tanpaJanji ? R.tanpaJanji + ' belum ada tanggal janji (tidak dihitung)' : '',
    R.digeser ? R.digeser + ' janjinya digeser (dihitung dari janji pertama)' : '', R.tidakTerukur ? R.tidakTerukur + ' isinya tidak terukur' : ''].filter(Boolean);
  return kata.judul + ', ' + N + ' hari terakhir: ' + [a, b].filter(Boolean).join(' · ') + (c.length ? ' · ' + c.join(' · ') : '') + '.';
}
/** Ringkas satu kelompok (baris per pemasok di Pondasi): "4/5 tepat janji · telat ±0,4 hari · utuh 5/6 · 2 belum ada tanggal janji". */
export function jnKataRingkas(R) {
  if (!R || !R.semua) return 'belum ada pesanan';
  return [R.n ? R.tepat + '/' + R.n + ' tepat janji' : 'belum ada yang berjanji & sudah ' + (R.gagal ? 'selesai' : 'datang'), R.nDatang ? 'telat ' + jnHariTeks(R.rataTelat) + (R.maksTelat ? ' (terlama ' + R.maksTelat + ' hr)' : '') : '',
    R.nIsi ? 'utuh ' + R.utuh + '/' + R.nIsi : '', R.lewat ? R.lewat + ' lewat janji' : '', R.tanpaJanji ? R.tanpaJanji + ' belum ada tanggal janji' : ''].filter(Boolean).join(' · ');
}
export const jnPctTeks = jnPct;
const jnDalam = (x, awal, akhir) => x.dibuat >= awal && x.dibuat <= akhir;
const jnHariN = (hari) => Math.max(7, Math.min(365, Math.round(Number(hari) || JN_HARI_BAWAAN)));
/**
 * B58 · B60 · B65 — dari pemasok, N hari terakhir: tepat janji (total & per pemasok), rata-rata & terlama telat, utuh vs sebagian, lewat janji yang masih ditunggu.
 * → { hari, awal, akhir, tol, baris, ringkas, perPemasok: [{ kunci, nama, ringkas }], lewat, kalimat }
 */
export function jnPemasok(kini, hari) {
  const iso = jnIsoKini(kini); const N = jnHariN(hari); const awal = jnTambahHari(iso, -(N - 1)); const S = jnPemasokSemua(kini);
  const baris = S.filter((x) => jnDalam(x, awal, iso)); const per = {};
  baris.forEach((x) => { (per[x.kunci] = per[x.kunci] || { kunci: x.kunci, nama: x.nama, baris: [] }).baris.push(x); });
  const perPemasok = Object.keys(per).map((k) => Object.assign(per[k], { ringkas: jnRingkasBaris(per[k].baris) }))
    .sort((a, b) => b.ringkas.semua - a.ringkas.semua || a.nama.localeCompare(b.nama, 'id'));
  const R = jnRingkasBaris(baris);
  return { hari: N, awal, akhir: iso, tol: jnAtur().tolPemasok, baris, ringkas: R, perPemasok, lewat: S.filter((x) => x.keadaan === 'lewat'),
    kalimat: jnKalimat(R, { judul: 'Dari pemasok', tepat: 'pesanan datang tepat janji', benda: 'pesanan', selesai: 'datang', utuh: 'pesanan datang utuh' }, N) };
}
/** B60 · B61 · B58 — ke pelanggan (surat jalan + pesanan tanpa surat jalan), N hari terakhir. Bentuk = jnPemasok tanpa perPemasok. */
export function jnPelanggan(kini, hari) {
  const iso = jnIsoKini(kini); const N = jnHariN(hari); const awal = jnTambahHari(iso, -(N - 1)); const S = jnPelangganSemua(kini);
  const baris = S.filter((x) => jnDalam(x, awal, iso)); const R = jnRingkasBaris(baris);
  return { hari: N, awal, akhir: iso, tol: jnAtur().tolAntar, baris, ringkas: R, lewat: S.filter((x) => x.keadaan === 'lewat'),
    kalimat: jnKalimat(R, { judul: 'Antar ke pelanggan', tepat: 'kiriman sampai tepat janji', benda: 'kiriman', selesai: 'sampai', utuh: 'pesanan terpenuhi utuh' }, N) };
}
/**
 * B55 — operasi gudang terlambat: semua pesanan ke pemasok yang belum datang & kiriman ke pelanggan yang belum sampai, yang SUDAH lewat janji + toleransi
 * (tanpa jendela). Paling lama telat dulu. → [{ jenis, id, nama, janji, telat, teks, tujuan }]
 */
export function jnLewat(kini) {
  const P = jnPemasokSemua(kini).filter((x) => x.keadaan === 'lewat').map((x) => Object.assign({}, x, { teks: x.nama + ' — barang belum datang, ' + jnKataBaris(x), tujuan: { ke: 'harga', keluarga: 'belanja' } }));
  const A = jnPelangganSemua(kini).filter((x) => x.keadaan === 'lewat').map((x) => Object.assign({}, x, { teks: x.nama + ' — ' + (x.jenis === 'antar' ? 'surat jalan ' + x.noSJ + ' belum sampai' : 'pesanan belum dikirim') + ', ' + jnKataBaris(x),
    tujuan: { ke: 'jual', lembar: x.jenis === 'antar' ? 'antar' : 'pesanan' } }));
  return P.concat(A).sort((a, b) => b.telat - a.telat || String(a.janji.awal).localeCompare(String(b.janji.awal)) || a.nama.localeCompare(b.nama, 'id'));
}
/** Dasbor (KPI): angka pendek dua arah + daftar lewat janji. */
export function jnRingkas(kini) {
  const P = jnPemasok(kini); const A = jnPelanggan(kini); const L = jnLewat(kini);
  return { pemasok: P.ringkas, antar: A.ringkas, hari: P.hari, tol: { pemasok: P.tol, antar: A.tol }, lewat: L, kalimatPemasok: P.kalimat, kalimatAntar: A.kalimat,
    tujuan: { ke: 'laporan', keluarga: 'pondasi' }, sumber: 'Laporan › Pondasi › Tepat janji', keadaan: P.ringkas.semua || A.ringkas.semua ? 'ada' : 'kosong' };
}

// ---------- isi janji (Belanja owner & Barang masuk tablet) ----------
/** Pilihan cepat janji datang: belum tahu · hari ini · besok · lusa (tanggal lain lewat isian tanggal). */
export function jnPilihan(iso) { return [['', 'belum tahu'], [iso, 'hari ini'], [jnTambahHari(iso, 1), 'besok'], [jnTambahHari(iso, 2), 'lusa']]; }
/** Kolom janji untuk pesanan BARU (Belanja susunPesanan) — kosong / tidak sah = {} (belum ada janji). */
export function jnKolomJanjiBaru(tanggal, w, oleh) {
  const t = String(tanggal || '').trim(); if (!jnTanggalSah(t) || jnSelisih(t, w.tanggal) < 0) return {};
  return { janjiTanggal: t, janjiRiwayat: [{ tanggal: t, pada: w.kini, oleh: String(oleh || '').slice(0, 40) }] };
}
/**
 * Isi / geser janji datang satu pesanan ke pemasok yang MASIH MENUNGGU (owner, atau Penjaga laci lewat rules v24): kolom janjiTanggal & janjiRiwayat saja.
 * → { dokumen, patch } atau { tolak }.
 */
export function jnSusunJanjiPemasok(id, tanggal, w, oleh) {
  const p = (ambilPesananPemasok() || []).find((x) => x && String(x.id) === String(id)); if (!p) return { tolak: 'Pesanan itu sudah tidak ada' };
  if (p.status === 'batal') return { tolak: 'Pesanan ini sudah dibatalkan' };
  const X = jnPesananPemasok(id, new Date(Date.parse(w.kini) || Date.now()));
  if (p.status !== 'menunggu' || (X && X.sampai)) return { tolak: 'Barang pesanan ini sudah datang — janjinya tidak diubah lagi' };
  const t = String(tanggal || '').trim(); if (!jnTanggalSah(t)) return { tolak: 'Tanggal janji tidak terbaca' };
  if (jnSelisih(t, p.tanggal) < 0) return { tolak: 'Janji datang tidak bisa sebelum tanggal pesan (' + tanggalPendek(p.tanggal) + ')' };
  if (t === String(p.janjiTanggal || '')) return { tolak: 'Janjinya memang ' + tanggalPendek(t) };
  const riw = (Array.isArray(p.janjiRiwayat) ? p.janjiRiwayat : []).concat([{ tanggal: t, pada: w.kini, oleh: String(oleh || '').slice(0, 40) }]).slice(-JN_RIWAYAT_MAKS);
  const data = Object.assign({}, p, { janjiTanggal: t, janjiRiwayat: riw });
  const J0 = jnJanjiPemasok(p); const J1 = jnJanjiPemasok(data); const nm = String(p.pemasok || 'pemasok');
  const kabar = !J0.awal ? 'Janji datang ' + nm + ' dicatat: ' + tanggalPendek(t)
    : J1.geser.length > J0.geser.length ? 'Janji ' + nm + ' digeser ' + jnTgl(J0.akhir || J0.awal) + ' → ' + jnTgl(t) + '. Tepat waktu tetap dihitung dari janji pertama (' + jnTgl(J1.awal) + ').'
      : 'Janji ' + nm + ' dibetulkan jadi ' + tanggalPendek(t) + ' (di hari yang sama — salah ketik, bukan geser)';
  return { dokumen: [{ koleksi: 'pesananPemasok', data }], patch: { janjiP: null, kabar, kabarAwas: false } };
}
/** Pesanan ke pemasok yang masih menunggu datang (untuk Barang masuk tablet), terbaru dulu. */
export function jnMenungguPemasok(kini) {
  return jnPemasokSemua(kini).filter((x) => !x.batal && !x.sampai && x.disimpanMenunggu).slice().reverse();
}
