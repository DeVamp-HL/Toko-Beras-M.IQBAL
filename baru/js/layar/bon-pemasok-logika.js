// LAYAR HARGA & PEMASOK — H2 BON PEMASOK (dikunci owner 18 Sep 2026: gabungan Tusukan Bon · Garis Jatuh Tempo · Buku Bon). Logika tanpa DOM, awalan bp.
// Angka bon dari MESIN BEKU hitungUtangPemasok: sisa = nilai − Σ bayar, bon yang dibayar sebagian TETAP di daftar (memori sisa-bon-dianggap-lunas).
// Satu pembayaran = satu bon (bonId), tidak boleh melebihi sisa bon itu; bon tertua cuma SARAN (RODA MAS tertua dulu, SEJATI terbaru dulu — owner yang memilih).
// Dokumen = simpanBayarBon / simpanSaldoAwalUtang index.html: utangPemasokMutasi {id, tanggal, jam, tipe 'bayar', pemasok, nominal, catatan, bonId, bonTanggal}
// (+ kolom baru sistem baru: dari = laci/brankas/rekening, biayaAdmin, adminNama) dan {tipe 'saldoAwal', pemasok, nominal, catatan, bonTanggal} untuk bon lama.
// Biaya admin transfer = BIAYA TOKO → dokumen pengeluaranHarian {kategori 'toko'} dalam batch yang sama (laba berkurang segitu; bayar bonnya sendiri tidak menyentuh laba).
// Tempo tidak tertulis di dokumen mana pun (memori tempo-bon-pemasok): tempo = isian owner di KARTU pemasok (pemasokCatatan.tempo); tanpa tempo kartu dipakai tempo umum
// aturanToko/catatStok.tempoHari (yang dipakai Menu & Pengingat sejak putaran 14) — dan disebut sumbernya; tanpa keduanya jatuh tempo TIDAK diramal.
// Uang toko: sistem lama tidak punya saldo per kantong, yang bisa dijaga TOTAL kas (kasPada; null bila titik kas belum disetel) — "dari mana uangnya" dicatat sebagai kolom.
import { hitungUtangPemasok, kasPada } from '../mesin/beku.js';
import { batchDiutang, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilUtangPemasokMutasi, ambilPemasokCatatan, ambilPengeluaranHarian, ambilTutupHari, ambilPesananPemasok, cacheMentah, kunciSampai, namaSistemPemasok, tolakKunci, denganCacheSementara, ingatKasPada, ringkasArsip } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const ATUR_BON_BAWAAN = { dekatHari: 7, admin: [{ nama: 'BI-FAST', n: 2500 }, { nama: 'Transfer antarbank', n: 6500 }] };
export const TEMPAT_UANG = [['laci', 'Laci'], ['brankas', 'Brankas'], ['rekening', 'Rekening']];
export const TAB_BON = [['tusuk', 'Tusukan bon'], ['garis', 'Jatuh tempo'], ['buku', 'Buku bon']];
export const TEMPO_PILIHAN = [0, 7, 14, 21, 30];
const bpAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const bpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const bpHariKe = (iso) => Math.round(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10)) / 86400000);
export const bpTambahHari = (iso, n) => new Date((bpHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
// 39b no. 11: nama yang DIPAKAI SISTEM (saldo awal, tutup buku, batch lahir buku khusus) bukan pemasok — tidak masuk daftar, Buku bon, pil Bon lama, Rekap Bon
// namaSistemPemasok tinggal di data/toko.js (satu aturan untuk Buku bon & Barang masuk; tinjauan rantai laporan)
export const pemasokSungguhan = (nama) => { const n = String(nama || '').trim(); return n !== '' && !namaSistemPemasok(n); };
const namaTempat = (id) => (TEMPAT_UANG.find((t) => t[0] === id) || [id, id])[1];

export function aturBon() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'bonPemasok') || null;
  const dekat = a && isFinite(Number(a.dekatHari)) && Number(a.dekatHari) >= 0 && Number(a.dekatHari) <= 60 ? Number(a.dekatHari) : ATUR_BON_BAWAAN.dekatHari;
  const admin = a && Array.isArray(a.admin) ? a.admin.filter((x) => x && String(x.nama || '').trim()).map((x) => ({ nama: String(x.nama).trim(), n: Math.max(0, Math.round(Number(x.n) || 0)) })) : ATUR_BON_BAWAAN.admin.map((x) => Object.assign({}, x));
  return { dekatHari: dekat, admin, dariOwner: !!a };
}
export function susunAturBon(isi, w) {
  const kini = aturBon(); let dekat = kini.dekatHari; if (!bpKosong(isi.dekatHari)) { dekat = Math.round(bpAngka(isi.dekatHari)); if (!(dekat >= 0 && dekat <= 60)) return { tolak: 'Bon dianggap dekat: 0–60 hari' }; }
  const admin = []; for (const x of (isi.admin || [])) { const nm = String(x.nama || '').trim(); const n = Math.round(bpAngka(x.n)); if (!nm && !(n > 0)) continue; if (!nm) return { tolak: 'Biaya admin ' + RP(n) + ' belum diberi nama' }; if (!(n >= 0)) return { tolak: 'Biaya admin ' + nm + ' tidak boleh minus' }; admin.push({ nama: nm.slice(0, 40), n }); }
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'bonPemasok', tanggal: w.tanggal, jam: w.jam, dekatHari: dekat, admin } }], patch: { aturB: null, kabar: 'Aturan bon pemasok disimpan — dekat = ' + dekat + ' hari · ' + (admin.length ? admin.map((x) => x.nama + ' ' + RP(x.n)).join(', ') : 'tanpa pilihan biaya admin'), kabarAwas: false } };
}
/** Tempo umum = aturanToko/catatStok.tempoHari (angka owner di Stok → Barang masuk → Atur); bawaannya 21 hari = angka yang sama dengan lembar Atur itu
 *  (ATUR_CATAT bawaan; median bon RODA MAS yang terukur — memori tempo-bon-pemasok). Dipakai Menu & Pengingat sejak putaran 14, jadi tidak boleh berbeda di sini. */
export const TEMPO_UMUM_BAWAAN = 21;
export function tempoUmum() { const d = cacheMentah('aturan').find((x) => String(x.id) === 'catatStok'); const n = d ? Number(d.tempoHari) : NaN; return { hari: isFinite(n) && n > 0 ? n : TEMPO_UMUM_BAWAAN, dariOwner: isFinite(n) && n > 0 }; }

// SIAP 2027 · P4 (audit 8 Okt): sesudah tutup buku, kedatangan ≤ 31 Des pindah ke arsip — dulu Belanja kehilangan SEMUA pemasok & harga beli terakhir (truk
// kosong, muatan 0, "Pakai saran" 0 karung) sampai tiap pemasok mengirim lagi. Saat tahun dikunci, ringkasan tahun di batch penanda (toko.js ringkasArsip)
// membawa `pemasok` (ringkasPemasokTahun) yang disusun bpKumpul — fungsi yang SAMA dengan daftarPemasok. Pembaca menggabungkan ringkasan dengan catatan hidup:
//   · jumlah (kedatangan, belanja, kg) = ringkasan + kedatangan hidup yang tidak dihitungnya (`ids`) → sebelum ritual, selama arsip, dan sesudahnya sama;
//   · 12 kedatangan terakhir (kg, bon/tunai) & harga beli terakhir per merek = yang paling baru dari keduanya (kedatangan 2027 menang per merek).
// Ringkasan lama tanpa `pemasok` = catatan hidup saja (seperti sebelum P4). Dibatalkan = penandanya ikut hilang = catatan hidup lagi.
export const BP_AKHIR = 12;   // kedatangan terakhir yang dibawa ringkasan per pemasok: muatan truk (median 12 terakhir) & kebiasaan bayar (3 terakhir)
const bpUrutBaru = (a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || (Number(b.id) || 0) - (Number(a.id) || 0);
/**
 * SATU tempat yang membaca kedatangan nyata per pemasok (daftarPemasok & ringkasPemasokTahun). sampai = tanggal terakhir yang dibaca ('' = semua);
 * R = ringkasan tahun yang diarsip (toko.js ringkasArsip) atau null. → { peta: { kunci: pemasok }, pastikan }.
 */
function bpKumpul(sampai, R) {
  const peta = {};
  const pastikan = (nama) => { const nm = String(nama || '').trim(); if (!pemasokSungguhan(nm)) return null; const k = kunciPelanggan(nm); if (!peta[k]) peta[k] = { kunci: k, nama: nm, urutNama: 0, kedatangan: 0, belanja: 0, totalKg: 0, terakhir: '', hargaPerMerk: {}, batch: [], ids: [] }; return peta[k]; };
  const RP0 = R && R.pemasok && typeof R.pemasok === 'object' ? R.pemasok : null; const dihitung = {};
  if (RP0) Object.keys(RP0).forEach((k) => ((RP0[k] || {}).ids || []).forEach((id) => { dihitung[String(id)] = true; }));
  ambilSemuaBatch().forEach((b) => { if (sampai && (b.tanggal || '') > sampai) return; const s = pastikan(b.pemasok); if (!s || b.stokAwal) return; if ((Number(b.id) || 0) >= s.urutNama) { s.nama = String(b.pemasok).trim(); s.urutNama = Number(b.id) || 0; }
    // kedatangan yang sudah dihitung ringkasan (arsip belum selesai / sebelum arsip) tidak dihitung dua kali; daftar & harga tetap membacanya (yang terbaru menang)
    const hitung = !dihitung[String(b.id)];
    const nilai = (b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0); if (hitung) { s.kedatangan += 1; s.belanja += nilai; s.ids.push(b.id); } if ((b.tanggal || '') > s.terakhir) s.terakhir = b.tanggal || '';
    s.batch.push({ id: b.id, tanggal: b.tanggal || '', jam: b.jam || '', nMerk: (b.merkList || []).length, nilai, utang: batchDiutang(b), kg: (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0) });
    (b.merkList || []).forEach((m) => { if (!m.merk || !(Number(m.hargaPerKg) > 0)) return; if (hitung) s.totalKg += Number(m.totalKg) || 0; const h = s.hargaPerMerk[m.merk] = s.hargaPerMerk[m.merk] || { riwayat: [] }; h.riwayat.push({ tanggal: b.tanggal || '', id: Number(b.id) || 0, hargaPerKg: Number(m.hargaPerKg), kg: Number(m.totalKg) || 0, merkPemasok: String(m.merkPemasok || '').trim() }); }); });   // tinjauan E1: merek pemasok (baris kelas tanpa wadah) untuk "merek lalu" di pesanan belanja
  if (RP0) Object.keys(RP0).forEach((k) => { const r = RP0[k] || {}; const s = pastikan(r.nama); if (!s) return;
    if ((Number(r.urut) || 0) >= s.urutNama) { s.nama = String(r.nama).trim(); s.urutNama = Number(r.urut) || 0; }
    s.kedatangan += Number(r.kedatangan) || 0; s.belanja += Number(r.belanja) || 0; s.totalKg += Number(r.totalKg) || 0; if (String(r.terakhir || '') > s.terakhir) s.terakhir = String(r.terakhir);
    const ada = {}; s.batch.forEach((x) => { ada[String(x.id)] = true; });
    (Array.isArray(r.akhir) ? r.akhir : []).forEach((x) => { if (!x || ada[String(x.id)]) return; ada[String(x.id)] = true; s.batch.push({ id: x.id, tanggal: String(x.tanggal || ''), jam: '', nMerk: 0, nilai: 0, utang: !!x.utang, kg: Number(x.kg) || 0, arsip: true }); });
    Object.keys(r.hargaPerMerk || {}).forEach((m) => { const t = r.hargaPerMerk[m] || {}; if (!m || !(Number(t.hargaPerKg) > 0)) return; const h = s.hargaPerMerk[m] = s.hargaPerMerk[m] || { riwayat: [] };
      h.riwayat.push({ tanggal: String(t.tanggal || ''), id: Number(t.id) || 0, hargaPerKg: Number(t.hargaPerKg), kg: Number(t.kg) || 0, merkPemasok: String(t.merkPemasok || '').trim(), arsip: true }); }); });
  return { peta, pastikan };
}
/** Urutan & yang terakhir: riwayat harga per merek (terbaru dulu → terakhir), kedatangan (terbaru dulu), kebiasaan bayar dari 3 kedatangan terakhir. */
function bpRapikan(s) {
  Object.keys(s.hargaPerMerk).forEach((m) => { const h = s.hargaPerMerk[m]; h.riwayat.sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || b.id - a.id); h.terakhir = h.riwayat[0]; });
  s.batch.sort(bpUrutBaru);
  const tiga = s.batch.slice(0, 3); const nBon = tiga.filter((x) => x.utang).length; s.caraBiasa = !tiga.length ? '' : nBon * 2 > tiga.length ? 'bon' : 'tunai'; s.caraTeks = !tiga.length ? 'belum pernah ada kedatangan' : (s.caraBiasa === 'bon' ? 'biasanya BON' : 'biasanya TUNAI') + ' (' + nBon + ' dari ' + tiga.length + ' kedatangan terakhir bon)';
  return s;
}
/**
 * Semua pemasok yang pernah ada: kedatangan nyata (+ ringkasan tahun yang diarsip) + bon lama + kartu. Kartu = pemasokCatatan {id = kunci, nama, kontak, catatan}
 * + kolom baru orang, tempo. batch = kedatangan terbaru dulu (yang dari ringkasan ber-`arsip`, tanpa jam & nilai).
 */
export function daftarPemasok() {
  const kartu = {}; ambilPemasokCatatan().forEach((c) => { kartu[String(c.id)] = c; });
  const { peta, pastikan } = bpKumpul('', ringkasArsip());
  ambilUtangPemasokMutasi().forEach((m) => { const s = pastikan(m.pemasok); if (s && !s.urutNama) s.nama = String(m.pemasok).trim(); });
  Object.values(kartu).forEach((c) => { const s = pastikan(c.nama || c.id); if (s && !s.urutNama && c.nama) s.nama = String(c.nama).trim(); });
  return Object.keys(peta).map((k) => { const s = bpRapikan(peta[k]); delete s.ids;
    const c = kartu[k] || {}; s.kontak = String(c.kontak || '').trim(); s.catatan = String(c.catatan || '').trim(); s.orang = String(c.orang || '').trim(); s.tempo = isFinite(Number(c.tempo)) && Number(c.tempo) > 0 ? Math.round(Number(c.tempo)) : 0; s.adaKartu = !!kartu[k]; s.bonLamaBergulir = c.bonLamaBergulir === true;
    return s; }).sort((a, b) => String(b.terakhir).localeCompare(String(a.terakhir)) || a.nama.localeCompare(b.nama));
}
/**
 * SIAP 2027 · P4: ringkasan pemasok per `cutoff` (31 Des tahun yang dikunci) untuk batch penanda — bpKumpul yang sama dengan daftarPemasok, atas catatan hidup
 * ≤ cutoff + ringkasan era sebelumnya (tahun berikutnya tetap membawa pemasok yang hanya mengirim di tahun-tahun lalu). Per kunci pemasok: nama (ejaan terbaru,
 * urut), jumlah kedatangan / belanja / kg, terakhir, 12 kedatangan terakhir { id, tanggal, kg, utang }, harga beli terakhir per merek { tanggal, id, hargaPerKg,
 * kg, merkPemasok }, ids = kedatangan hidup yang dihitung (pembaca tidak menghitungnya dua kali). Bentuk yang diterima Firestore (peta & larik objek).
 */
export function ringkasPemasokTahun(cutoff) {
  const R = ringkasArsip(); const { peta } = bpKumpul(cutoff, R && String(R.cutoff || '') < String(cutoff) ? R : null); const out = {};
  Object.keys(peta).forEach((k) => { const s = bpRapikan(peta[k]); const harga = {};
    Object.keys(s.hargaPerMerk).forEach((m) => { const t = s.hargaPerMerk[m].terakhir; harga[m] = { tanggal: t.tanggal, id: t.id, hargaPerKg: t.hargaPerKg, kg: t.kg, merkPemasok: t.merkPemasok }; });
    out[k] = { nama: s.nama, urut: s.urutNama, kedatangan: s.kedatangan, belanja: s.belanja, totalKg: s.totalKg, terakhir: s.terakhir, akhir: s.batch.slice(0, BP_AKHIR).map((x) => ({ id: x.id, tanggal: x.tanggal, kg: x.kg, utang: !!x.utang })), hargaPerMerk: harga, ids: s.ids }; });
  return out;
}
/**
 * "Sudah datang"-nya SATU pesanan dari kedatangan (batch = kedatangan nyata yang dibaca) + ringkasan tahun yang diarsip (R.pesananDatang) — satu aturan untuk
 * Belanja (pesananSemua) & ringkasan tahun: datang = ada kedatangan pemasok itu SESUDAH pesanannya (tanggal lebih besar, atau sama & jam lebih besar).
 * → { datang, tanggal } (tanggal = kedatangan pertama sesudahnya). Status tersimpan (batal / datang) dibaca pemanggil.
 */
export function bpPesananDatang(p, batch, R) {
  const sesudah = batch.filter((b) => String(b.pemasok || '').trim() === p.pemasok && ((b.tanggal || '') > (p.tanggal || '') || ((b.tanggal || '') === (p.tanggal || '') && (b.jam || '') > (p.jam || '')))).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.jam || '').localeCompare(String(b.jam || '')));
  const hidup = sesudah[0] ? sesudah[0].tanggal : ''; const D = R && R.pesananDatang && typeof R.pesananDatang === 'object' ? R.pesananDatang : {}; const r = Object.prototype.hasOwnProperty.call(D, String(p.id)) ? String(D[String(p.id)] || '') : null;
  return { datang: sesudah.length > 0 || r !== null, tanggal: r !== null && (!sesudah.length || r < String(hidup || '')) ? r : hidup };
}
/** SIAP 2027 · P4: pesanan ≤ cutoff yang statusnya belum tersimpan dan sudah ada kedatangan sesudahnya (≤ cutoff, + ringkasan era sebelumnya) → { id: tanggal datang }. */
export function ringkasPesananTahun(cutoff) {
  const R = ringkasArsip(); const R0 = R && String(R.cutoff || '') < String(cutoff) ? R : null; const out = {};
  const batch = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok) && (b.tanggal || '') <= cutoff);
  ambilPesananPemasok().forEach((p) => { if ((p.tanggal || '') > cutoff || p.status === 'batal' || p.status === 'datang') return; const D = bpPesananDatang(p, batch, R0); if (D.datang) out[String(p.id)] = String(D.tanggal || ''); });
  return out;
}
export const cariPemasok = (nama) => daftarPemasok().find((p) => p.kunci === kunciPelanggan(nama)) || null;
/**
 * Paket F1 (owner 8 Okt 2026, dikonfirmasi pemasok): utang lama ke pemasok yang BERGULIR — tanggalnya selalu tanggal pembelian terakhir. Kartu pemasok
 * `bonLamaBergulir` (pilihan "bon lama ikut kedatangan terakhir"). petaGulir() = { kunci pemasok: tanggal kedatangan terakhir } untuk pemasok berkartu begitu
 * (kedatangan terakhir dari daftarPemasok — ikut ringkasan tahun yang diarsip sejak P4, jadi tetap benar sesudah tutup buku). gulirBon(G, pemasok, b) = tanggal
 * yang menggantikan tanggal bon lama (saldoAwal) untuk umur & jatuh tempo, '' = tidak bergulir. SATU aturan untuk Bon pemasok, Menu, dan Pengingat.
 */
export function petaGulir() { const out = {}; daftarPemasok().forEach((p) => { if (p.bonLamaBergulir && p.terakhir) out[p.kunci] = p.terakhir; }); return out; }
export const gulirBon = (G, pemasok, b) => { const g = (G && G[kunciPelanggan(pemasok)]) || ''; return b && b.jenis === 'saldoAwal' && g && g > String(b.tanggal || '') ? g : ''; };
/** Tempo yang dipakai untuk meramal jatuh tempo bon pemasok ini, berikut SUMBERNYA. hari 0 = tidak diramal. */
export function tempoPemasok(nama) {
  const p = cariPemasok(nama); if (p && p.tempo > 0) return { hari: p.tempo, sumber: 'kartu', teks: 'tempo ' + p.tempo + ' hari (kartu pemasok)' };
  const u = tempoUmum(); if (u.hari > 0) return { hari: u.hari, sumber: 'umum', teks: 'tempo umum ' + u.hari + ' hari' + (u.dariOwner ? ' (Atur Barang masuk)' : ' (bawaan — ubah di Atur Barang masuk atau di kartu pemasok)') };
  return { hari: 0, sumber: '', teks: 'tempo belum disepakati — jatuh tempo tidak diramal' };
}
export const nomorWa = (kontak) => { const d = String(kontak || '').replace(/\D/g, ''); if (!d) return ''; return d.startsWith('0') ? '62' + d.slice(1) : d.startsWith('62') ? d : d; };

/** Semua bon terbuka (mesin beku) + tempo, status, urutan tusukan & garis jatuh tempo. */
export function susunBon(kini) {
  const iso = hariIniIso(kini || new Date()); const atur = aturBon(); const kas = ingatKasPada(); const up = hitungUtangPemasok();
  // Paket F1: bon lama yang BERGULIR memakai tanggal kedatangan terakhir pemasoknya untuk umur, jatuh tempo & status (petaGulir / gulirBon di bawah). Tanggal bon di
  // dokumen, nilai, sisa, dan total TIDAK berubah (b.tanggal tetap tanggal bonnya — dipakai pembayaran sebagai bonTanggal). gulir = '' bila tidak bergulir.
  const G = petaGulir();
  const bon = []; up.forEach((px) => { const T = tempoPemasok(px.pemasok);
    (px.bon || []).forEach((b) => { const gulir = gulirBon(G, px.pemasok, b); const dasar = gulir || b.tanggal;
    const jatuh = T.hari > 0 && dasar ? bpTambahHari(dasar, T.hari) : ''; const sisaHari = jatuh ? bpHariKe(jatuh) - bpHariKe(iso) : null;
    bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', gulir, nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0), umur: gulir ? Math.max(0, bpHariKe(iso) - bpHariKe(gulir)) : b.umurHari, jenis: b.jenis, catatan: b.catatan || '', jatuh, sisaHari, tempo: T,
      status: !jatuh ? 'tanpaTempo' : sisaHari < 0 ? 'lewat' : sisaHari <= atur.dekatHari ? 'dekat' : 'jauh' }); }); });
  bon.forEach((b) => { b.tempoTeks = b.status === 'tanpaTempo' ? 'tempo belum disepakati' : b.status === 'lewat' ? 'LEWAT ' + (-b.sisaHari) + ' hari (jatuh tempo ' + tanggalPendek(b.jatuh) + ')' : b.sisaHari === 0 ? 'jatuh tempo HARI INI' : 'jatuh tempo ' + tanggalPendek(b.jatuh) + ' · ' + b.sisaHari + ' hari lagi';
    b.ket = (b.umur === null || b.umur === undefined ? 'umur tidak diketahui' : 'umur ' + b.umur + ' hari') + (b.dibayar > 0 ? ' · sudah dibayar ' + RP(b.dibayar) + ' dari ' + RP(b.nilai) : '')
      + (b.gulir ? ' · bon bergulir — ikut kedatangan terakhir ' + tanggalPendek(b.gulir) + ' (bon asli ' + (b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tanggal') + ')' : b.jenis === 'saldoAwal' ? ' · bon lama (sebelum sistem)' : '');
    b.cap = b.gulir ? 'bon bergulir' : b.jenis === 'saldoAwal' ? 'bon lama' : b.dibayar > 0 ? 'sebagian' : ''; b.isi = b.jenis === 'saldoAwal' ? (b.catatan || 'bon lama sebelum sistem') : bpIsiBatch(b.id); b.noBon = bpNoBon(b.id); });
  const urutTua = (a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || (Number(a.id) || 0) - (Number(b.id) || 0);
  const total = bon.reduce((a, b) => a + b.sisa, 0); const tekor = up.reduce((a, x) => a + (x.tekor || 0), 0);
  const tusukan = up.map((px) => { const d = bon.filter((b) => b.pemasok === px.pemasok).sort(urutTua); const T = tempoPemasok(px.pemasok); return { pemasok: px.pemasok, tempo: T, tekor: px.tekor || 0, total: d.reduce((a, b) => a + b.sisa, 0), bon: d.map((b, i) => Object.assign({}, b, { saran: i === 0 && d.length > 1 })) }; }).filter((t) => t.bon.length || t.tekor > 0);
  const berTempo = bon.filter((b) => b.jatuh).sort((a, b) => a.jatuh.localeCompare(b.jatuh) || urutTua(a, b)), tanpaTempo = bon.filter((b) => !b.jatuh).sort(urutTua);
  const garis = []; let jalan = 0, kiniSudah = false, habisSudah = false; const tanda = (teks, kelas) => garis.push({ tanda: true, teks, kelas });
  berTempo.forEach((b) => { if (!kiniSudah && b.sisaHari >= 0) { tanda('hari ini · ' + tanggalPendek(iso), 'kini'); kiniSudah = true; }
    if (kas !== null && !habisSudah && jalan + b.sisa > kas) { tanda('uang toko ' + RP(kas) + ' habis di sini — bon berikut kurang ' + RP(jalan + b.sisa - kas), 'habis'); habisSudah = true; } jalan += b.sisa; garis.push(Object.assign({ tanda: false }, b)); });
  if (!kiniSudah && berTempo.length) tanda('hari ini · ' + tanggalPendek(iso), 'kini');
  if (tanpaTempo.length) { tanda('tempo belum disepakati — tidak diramal. Isi di kartu pemasoknya.', ''); tanpaTempo.forEach((b) => garis.push(Object.assign({ tanda: false }, b))); }
  const lewat = berTempo.filter((b) => b.status === 'lewat'), dekat = berTempo.filter((b) => b.status === 'dekat'); const jml = (d) => d.reduce((a, b) => a + b.sisa, 0);
  return { bon, total, nBon: bon.length, nPemasok: tusukan.filter((t) => t.bon.length).length, kas, adaKas: kas !== null, tekor, tusukan, garis, lewat, dekat, tanpaTempo, atur, iso,
    kasTeks: kas === null ? 'uang toko belum bisa dihitung — titik kas belum ada; Tutup hari malam ini (Uang › Tutup hari) menyetelnya' : 'uang toko sekarang ' + RP(kas) + ' (semua kantong, dari titik kas + gerakan sesudahnya)',
    ringkas: [{ a: String(lewat.length), l: 'lewat tempo', nyala: lewat.length > 0 }, { a: RP(jml(lewat) + jml(dekat)), l: 'jatuh ≤ ' + atur.dekatHari + ' hari', nyala: false }, { a: String(tanpaTempo.length), l: 'tanpa tempo', nyala: false }],
    cukupTeks: !berTempo.length ? 'Belum ada bon yang bisa diramal jatuh temponya.' : kas === null ? 'Uang toko belum bisa dihitung, jadi belum bisa dibandingkan dengan bon yang jatuh tempo.' : habisSudah ? 'Uang toko TIDAK cukup untuk semua bon yang sudah punya tempo.' : 'Uang toko cukup untuk semua bon yang sudah punya tempo.', kurang: habisSudah };
}
/** Nomor bon pemasok (owner 7 Okt: pembetulan bon) — kolom noBon di kedatangan / bon lama; '' = belum dicatat. */
function bpNoBon(id) { const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)) || ambilUtangPemasokMutasi().find((x) => String(x.id) === String(id) && x.tipe === 'saldoAwal'); return b && b.noBon ? String(b.noBon) : ''; }
function bpIsiBatch(id) { const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return ''; const ml = b.merkList || []; const kg = ml.reduce((a, m) => a + (Number(m.totalKg) || 0), 0); return ml.map((m) => m.merk).filter(Boolean).slice(0, 4).join(', ') + (ml.length > 4 ? ' …' : '') + (kg ? ' · ' + Math.round(kg).toLocaleString('id-ID') + ' kg' : ''); }

/** Buku bon per pemasok: barang datang lewat bon (+), bon lama (+), bayar (−), utang jadi berapa (saldo berjalan). */
export function bukuBon(nama) {
  const k = kunciPelanggan(nama); const kej = [];
  ambilSemuaBatch().forEach((b) => { if (b.stokAwal || !batchDiutang(b) || kunciPelanggan(b.pemasok) !== k) return; kej.push({ t: b.tanggal || '', j: b.jam || '', u: 0, teks: 'Barang datang — bon' + (b.noBon ? ' No. ' + b.noBon : ''), ket: bpIsiBatch(b.id), n: Math.round((b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0)), bonId: String(b.id) }); });
  ambilUtangPemasokMutasi().forEach((m) => { if (kunciPelanggan(m.pemasok) !== k) return;
    if (m.tipe === 'saldoAwal') kej.push({ t: m.bonTanggal || '', j: '', u: 0, teks: 'Bon lama (sebelum sistem)' + (m.noBon ? ' No. ' + m.noBon : ''), ket: (m.catatan || (m.bonTanggal ? '' : 'tanggal bon tidak diketahui')) + (m.alasanKoreksi ? ' · dibetulkan: ' + m.alasanKoreksi : ''), n: Math.round(Number(m.nominal) || 0), bonId: String(m.id) });
    else if (m.tipe === 'bayar') kej.push({ t: m.tanggal || '', j: m.jam || '', u: 1, teks: 'Bayar bon' + (m.bonTanggal ? ' ' + tanggalPendek(m.bonTanggal) : '') + (m.dari === 'rekening' ? ' · transfer' : m.dari ? ' · tunai' : ''), cara: caraDari(m.dari), ket: (m.dari ? 'dari ' + namaTempat(m.dari) : 'kantong tidak dicatat (sistem lama)') + (Number(m.biayaAdmin) > 0 ? ' · admin ' + RP(m.biayaAdmin) + (m.adminNama ? ' ' + m.adminNama : '') + ' (biaya toko, bukan utang)' : '') + (m.catatan ? ' · ' + m.catatan : '') + (m.alasanKoreksi ? ' · DIBETULKAN: ' + ((m.riwayat || []).slice(-1)[0] || {}).teks : ''), n: -Math.round(Number(m.nominal) || 0), id: m.id, bonId: String(m.bonId || '') }); });
  kej.sort((a, b) => a.t.localeCompare(b.t) || a.u - b.u || a.j.localeCompare(b.j)); let sd = 0;
  const baris = kej.map((e) => { sd += e.n; return Object.assign({}, e, { saldo: sd }); });
  return { baris, saldo: sd };
}

// ---- LEMBAR BAYAR: satu pembayaran = satu bon; TUNAI (laci/brankas) atau TRANSFER (rekening, boleh berbiaya admin = biaya toko)
// putaran 29 (Bagian 4, owner 27 Sep): cara bayar dibaca dari `dari` (rekening = transfer) — tanpa kolom baru di utangPemasokMutasi. Kantong yang dipilih dijaga
// isinya bila layar menyerahkan saldo per tempat (S = saldoKantong() dari uang-logika; diserahkan oleh layar supaya modul ini tidak mengimpor balik uang-logika);
// tanpa S, yang dijaga tetap TOTAL kas seperti sebelumnya. Rekening yang belum pernah diisi (titik kas 0) DISEBUT dan ditawari "catat isi rekening".
export const CARA_BAYAR_BON = [['tunai', 'Tunai'], ['transfer', 'Transfer']];
export const caraDari = (dari) => (dari === 'rekening' ? 'transfer' : dari ? 'tunai' : '');
export function hitungBayar(d, kini, S) {
  const D = Object.assign({ pemasok: '', bonId: '', ketik: '', dari: '', adminI: -1, catatan: '' }, d || {}); const B = susunBon(kini); const atur = B.atur;
  const bonP = B.bon.filter((b) => b.pemasok === D.pemasok).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal))); const bon = bonP.find((b) => b.id === String(D.bonId)) || null;
  const n = Math.round(bpAngka(D.ketik)); const biaya = D.dari === 'rekening' && D.adminI >= 0 ? atur.admin[D.adminI] || null : null; const admin = biaya ? biaya.n : 0; const cara = caraDari(D.dari);
  const kantong = S && S.ada && D.dari && S[D.dari] !== undefined && S[D.dari] !== null ? S[D.dari] : null;
  const rekeningKosong = !!(S && S.ada && !(Number(S.titik.rekening) > 0));   // titik kas rekening 0 = belum pernah dicatat; hitungan yang ada cuma gerakan (QRIS) sejak titik
  let tolak = ''; if (!bon) tolak = 'Pilih bon yang dibayar'; else if (!(n > 0)) tolak = 'Ketik jumlah yang dibayar'; else if (n > bon.sisa) tolak = 'Melebihi sisa bon ini (' + RP(bon.sisa) + ') — satu pembayaran satu bon, bon lain dicatat terpisah supaya jejaknya jelas';
  else if (!D.dari) tolak = 'Uangnya dari mana — tunai (laci/brankas) atau transfer (rekening)?';
  else if (kantong !== null && n + admin > kantong + 0.5) tolak = namaTempat(D.dari) + ' cuma ' + RP(kantong) + ' — tidak cukup untuk ' + RP(n + admin) + (admin ? ' (termasuk biaya admin ' + RP(admin) + ')' : '') + (D.dari === 'rekening' && rekeningKosong ? '. Isi rekening di aplikasi belum pernah dicatat — catat isi rekening dulu di Uang › Pindah uang' : '');
  else if (B.adaKas && n + admin > B.kas) tolak = 'Uang toko cuma ' + RP(B.kas) + ' — tidak cukup' + (admin ? ' (termasuk biaya admin ' + RP(admin) + ')' : '');
  const lunas = !!bon && n === bon.sisa;
  return { D, B, bonP, bon, n, admin, biaya, tolak, lunas, cara, kantong, rekeningKosong, rekeningTeks: rekeningKosong ? 'Isi rekening belum pernah dicatat di titik kas — hitungan ' + RP(S.rekening) + ' cuma dari gerakan rekening sejak ' + S.teksTitik + '. Catat isi rekening menurut m-banking dulu di Uang › Pindah uang, supaya transfer bisa dijaga' : '',
    arti: bon && n > 0 && n <= bon.sisa ? { a: lunas ? 'Bon ' + tanggalPendek(bon.tanggal) + ' LUNAS — keluar dari daftar' : 'Dibayar SEBAGIAN — sisa bon jadi ' + RP(bon.sisa - n) + ', bonnya TETAP di daftar', b: (D.dari ? namaTempat(D.dari) : 'uang toko') + ' berkurang ' + RP(n + admin) + (cara === 'transfer' ? ' lewat transfer' : cara === 'tunai' ? ' tunai' : '') + (admin ? ' (termasuk admin ' + RP(admin) + ')' : ''), c: 'utang ke ' + bon.pemasok + ' berkurang ' + RP(n) + (admin ? ' (bukan ' + RP(n + admin) + ')' : '') + ' · laba TIDAK berubah — berasnya sudah dihitung waktu datang' + (admin ? ' · biaya admin ' + RP(admin) + ' masuk biaya toko, laba berkurang segitu' : '') } : null,
    label: tolak || (lunas ? 'BAYAR LUNAS ' + RP(n) : 'BAYAR SEBAGIAN ' + RP(n)) + (cara === 'transfer' ? ' · TRANSFER' : cara === 'tunai' ? ' · TUNAI' : '') };
}
export function susunBayar(d, w, S) {
  const H = hitungBayar(d, new Date(w.kini), S); if (H.tolak) return { tolak: H.tolak };
  const id = w.idUnik(); const catatan = String(H.D.catatan || '').trim().slice(0, 80);
  const bayar = { id, tanggal: w.tanggal, jam: w.jam, tipe: 'bayar', pemasok: H.bon.pemasok, nominal: H.n, catatan, bonId: H.bon.id, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };
  if (H.admin > 0) { bayar.biayaAdmin = H.admin; bayar.adminNama = H.biaya.nama; }
  const dokumen = [{ koleksi: 'utangPemasokMutasi', data: bayar }];
  // biaya admin = uang keluar "Untuk toko" (kategori biaya bank), bertanggal sama, satu kiriman, saling merujuk (dariBayarBon ↔ biayaAdmin/adminNama); dari rekening (putaran 29: dulu tanpa `dari` → dipotong dari laci di saldo per tempat)
  if (H.admin > 0) dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama + ' — bayar bon ' + H.bon.pemasok + (H.bon.tanggal ? ' ' + tanggalPendek(H.bon.tanggal) : ''), nominal: H.admin, dari: H.D.dari, dariBayarBon: id } });
  return { dokumen, bayarId: id, patch: { bayar: null, urung: { id, sampai: Date.now() + 90000, teks: 'Batalkan pembayaran ' + RP(H.n) + ' tadi' }, kabar: 'Bon ' + tanggalPendek(H.bon.tanggal) + ' ' + H.bon.pemasok + (H.lunas ? ' LUNAS' : ' dibayar sebagian, sisa ' + RP(H.bon.sisa - H.n)) + ' · ' + (H.cara === 'transfer' ? 'transfer, ' : 'tunai, ') + namaTempat(H.D.dari) + ' berkurang ' + RP(H.n + H.admin) + (H.admin ? ' (admin ' + RP(H.admin) + ' jadi biaya toko, utang turun ' + RP(H.n) + ')' : ''), kabarAwas: false } };
}
/** Batalkan pembayaran barusan (≤ 90 detik): hapus dokumen bayar + dokumen biaya adminnya. */
export function susunUrungBayar(id) {
  const m = ambilUtangPemasokMutasi().find((x) => String(x.id) === String(id) && x.tipe === 'bayar'); if (!m) return { tolak: 'Pembayaran itu sudah tidak ada' };
  const hapus = [{ koleksi: 'utangPemasokMutasi', id: m.id }]; ambilPengeluaranHarian().forEach((h) => { if (String(h.dariBayarBon || '') === String(id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });
  return { hapus, patch: { urung: null, kabar: 'Pembayaran ' + RP(m.nominal || 0) + ' dibatalkan — bon ' + m.pemasok + ' dan ' + namaTempat(m.dari || 'laci') + ' kembali seperti semula' + (hapus.length > 1 ? ' (biaya adminnya ikut dicabut)' : ''), kabarAwas: false } };
}
// ---- LEMBAR BON LAMA (sebelum sistem): utang bertambah; uang, stok, laba TIDAK berubah
export function hitungBonLama(d) {
  const D = Object.assign({ pemasok: '', nama: '', tgl: '', ketik: '', catatan: '' }, d || {}); const n = Math.round(bpAngka(D.ketik)); const namaBaru = String(D.nama || '').trim();
  const kembar = namaBaru ? daftarPemasok().find((p) => p.kunci === kunciPelanggan(namaBaru)) : null; const pemasok = D.pemasok || (kembar ? kembar.nama : namaBaru);
  let tolak = ''; if (!pemasok) tolak = 'Pilih atau ketik nama pemasoknya'; else if (namaSistemPemasok(pemasok)) tolak = '"' + pemasok + '" nama yang dipakai sistem, bukan pemasok — utang tidak bisa dicatat atas nama itu'; else if (!(n > 0)) tolak = 'Ketik nilai bonnya'; else if (D.tgl && !/^\d{4}-\d{2}-\d{2}$/.test(D.tgl)) tolak = 'Tanggal bon tidak terbaca';
  // putaran 25 (K4): mesin membaca umur bon lama dari bonTanggal — bon bertanggal bulan terkunci (atau tanpa tanggal, = paling tua) akan menggeser neraca bulan
  // yang sudah dikunci, jadi dicatat bertanggal HARI INI dan tanggal aslinya ditulis di catatan (field yang sudah ada)
  const sampai = kunciSampai(); const keHariIni = !!sampai && (!D.tgl || D.tgl.slice(0, 7) <= sampai);
  return { D, n, pemasok, keHariIni, kembar: kembar && !D.pemasok ? kembar.nama : '', tolak, arti: n > 0 ? 'Utang ke ' + (pemasok || 'pemasok') + ' bertambah ' + RP(n) + ' · uang toko, stok, dan laba TIDAK berubah — ini utang dari masa sebelum sistem.' + (keHariIni ? ' Tanggal bonnya ' + (D.tgl ? tanggalPendek(D.tgl) : 'tidak diketahui') + ' jatuh di bulan terkunci — dicatat bertanggal HARI INI, tanggal aslinya ditulis di catatan (umur bon di layar mulai hari ini).' : '') : '', label: tolak || 'CATAT BON LAMA ' + RP(n) };
}
export function susunBonLama(d, w) {
  const H = hitungBonLama(d); if (H.tolak) return { tolak: H.tolak };
  const asli = H.keHariIni ? 'tanggal bon asli ' + (H.D.tgl || 'tidak diketahui') + ' (bulan terkunci, dicatat ' + w.tanggal + ')' : '';
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'saldoAwal', pemasok: H.pemasok.slice(0, 60), nominal: H.n, catatan: [String(H.D.catatan || '').trim(), asli].filter(Boolean).join(' · ').slice(0, 160), bonTanggal: H.keHariIni ? w.tanggal : (H.D.tgl || null) };
  return { dokumen: [{ koleksi: 'utangPemasokMutasi', data }], patch: { lama: null, bukuNama: H.pemasok, kabar: 'Bon lama ' + RP(H.n) + ' ' + H.pemasok + ' dicatat' + (H.D.tgl ? ' (tanggal bon ' + tanggalPendek(H.D.tgl) + ')' : ' (tanggal bon tidak diketahui — dihitung paling tua)') + ' — uang toko, stok, dan laba tidak berubah', kabarAwas: false } };
}
// ---- KARTU PEMASOK: orang, kontak, tempo, catatan = isian owner (dokumen pemasokCatatan sistem lama + kolom baru orang & tempo)
export function susunKartu(nama, isi, w) {
  const nm = String(nama || '').trim(); if (!pemasokSungguhan(nm)) return { tolak: nm ? '"' + nm + '" nama yang dipakai sistem (saldo awal / tutup buku / buku khusus), bukan pemasok' : 'Nama pemasok kosong' }; const p = cariPemasok(nm);
  const tempo = bpKosong(isi.tempo) ? 0 : Math.round(bpAngka(isi.tempo)); if (!(tempo >= 0 && tempo <= 120)) return { tolak: 'Tempo bon: 0–120 hari (0 = belum disepakati)' };
  const data = { id: kunciPelanggan(nm), nama: p ? p.nama : nm, kontak: String(isi.kontak || '').trim().slice(0, 30), catatan: String(isi.catatan || '').trim().slice(0, 160), orang: String(isi.orang || '').trim().slice(0, 40), tempo, bonLamaBergulir: isi.bonLamaBergulir === true, diubahPada: w.kini };
  return { dokumen: [{ koleksi: 'pemasokCatatan', data }], patch: { kartu: null, kabar: 'Kartu ' + data.nama + ' tersimpan — ' + (tempo > 0 ? 'tiap bonnya diramal jatuh tempo ' + tempo + ' hari sesudah barang datang' : 'tempo kartu kosong, dipakai tempo umum ' + tempoUmum().hari + ' hari') + (data.bonLamaBergulir ? ' · bon lama ikut tanggal kedatangan terakhir' : ''), kabarAwas: false } };
}

// ---- PEMBETULAN BON (owner 7 Okt 2026) ----
// Owner 7 Okt: "Bon 31 Agustus sudah tidak ada. Adanya tanggal 18/28 September dan 05 Oktober. Sepertinya gua salah catat di sistem." Dulu pembayaran yang
// salah tunjuk hanya bisa diurungkan 90 detik. Pembetulan = OWNER saja (layar Harga & Pemasok owner saja; utangPemasokMutasi owner saja di rules), dengan ALASAN,
// menulis ulang dokumen yang sama dengan JEJAK — `riwayat` (nilai lama → baru, tanggal, jam, alasan) + `alasanKoreksi` (pola Koreksi kedatangan), bukan
// menimpa diam-diam. Angkanya tetap dari mesin beku hitungUtangPemasok (tidak disentuh):
//   · PINDAH pembayaran ke bon lain pemasok yang sama (bon itu sudah ada saat pembayaran dicatat): bonId & bonTanggal diganti. Utang total, kas, laba TIDAK
//     berubah — yang bergeser cuma bon mana yang lunas; kelebihan mengalir ke bon tertua yang belum lunas (aturan mesin) dan DISEBUT.
//   · JUMLAH pembayaran (salah ketik): utang & kas bergeser sebesar selisihnya (kas di tempat uang pembayaran itu), laba tetap.
//   · NOMOR bon pemasok (nomor di kertas bon): kolom `noBon` di dokumen bonnya (kedatangan / bon lama) — tanpa alasanKoreksi di kedatangan (bukan koreksi
//     barang: garis waktu HPP & harga lalu kelas tidak menandainya "dikoreksi"); Koreksi kedatangan membawanya.
//   · Bon LAMA (sebelum sistem): tanggal & nilai. Tanggal & nilai bon KEDATANGAN = tanggal & harga barangnya → Stok › Barang masuk › koreksi (satu kebenaran;
//     terkunci bila bon itu sudah dibayar — pindahkan dulu pembayarannya di sini).
// Bulan terkunci (kunci periode) DITOLAK dengan kalimatnya (tolakKunci; rules v4 menolak juga).
export const BP_ALASAN_MIN = 5;
const bpNama = (n) => String(n || '').trim();
const bpNilaiBatch = (b) => Math.round((b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0));
const bpUrutDok = (a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || String(a.jam || '').localeCompare(String(b.jam || '')) || (Number(a.id) || 0) - (Number(b.id) || 0);
export const bpLabelBon = (b) => (b ? 'bon ' + (b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tanggal') + (b.noBon ? ' No. ' + b.noBon : '') : 'bon yang tidak ada lagi');
const bpRiwayat = (lama, w, isi) => (Array.isArray(lama.riwayat) ? lama.riwayat : []).concat([Object.assign({ tanggal: w.tanggal, jam: w.jam }, isi)]);
const bpAlasan = (a) => String(a || '').trim().replace(/\s+/g, ' ').slice(0, 160);
/**
 * Semua bon SATU pemasok (nama persis seperti mesin), yang sudah lunas juga, urut tertua: { id, jenis 'batch' | 'saldoAwal', koleksi, tanggal, nilai, sisa,
 * dibayar (mesin: nilai − sisa), noBon, dok, bayar [pembayaran yang menunjuknya], dipindahDari [pembayaran yang dulu menunjuknya] }.
 */
export function bpSemuaBon(pemasok) {
  const P = bpNama(pemasok); const out = [];
  ambilSemuaBatch().forEach((b) => { if (b.stokAwal || !batchDiutang(b) || bpNama(b.pemasok) !== P) return; out.push({ id: String(b.id), jenis: 'batch', koleksi: 'batchMasuk', tanggal: b.tanggal || '', nilai: bpNilaiBatch(b), noBon: String(b.noBon || ''), dok: b, isi: bpIsiBatch(b.id) }); });
  ambilUtangPemasokMutasi().forEach((m) => { if (m.tipe !== 'saldoAwal' || bpNama(m.pemasok) !== P) return; out.push({ id: String(m.id), jenis: 'saldoAwal', koleksi: 'utangPemasokMutasi', tanggal: m.bonTanggal || '', nilai: Math.round(Number(m.nominal) || 0), noBon: String(m.noBon || ''), dok: m, isi: m.catatan || 'bon lama sebelum sistem' }); });
  const sisa = {}; hitungUtangPemasok().forEach((px) => { if (bpNama(px.pemasok) !== P) return; (px.bon || []).forEach((b) => { sisa[String(b.id)] = Math.round(b.sisa || 0); }); });
  const bayar = ambilUtangPemasokMutasi().filter((m) => m.tipe === 'bayar' && bpNama(m.pemasok) === P).sort(bpUrutDok);
  out.forEach((b) => { b.sisa = sisa[b.id] !== undefined ? sisa[b.id] : 0; b.dibayar = b.nilai - b.sisa; b.bayar = bayar.filter((m) => String(m.bonId || '') === b.id);
    b.dipindahDari = bayar.filter((m) => String(m.bonId || '') !== b.id && (m.riwayat || []).some((r) => r && r.jenis === 'pindahBon' && r.dari && String(r.dari.bonId || '') === b.id));
    b.riwayat = Array.isArray(b.dok.riwayat) ? b.dok.riwayat : []; b.label = bpLabelBon(b); });
  return out.sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || (Number(a.id) || 0) - (Number(b.id) || 0));
}
/** Rincian satu bon untuk lembar Betulkan bon: bon itu, semua bon pemasoknya, pembayaran yang tidak menunjuk bon yang ada (mengalir ke bon tertua). */
export function bpRincianBon(bonId, pemasok) {
  const semua = bpSemuaBon(pemasok); const bon = semua.find((b) => b.id === String(bonId)) || null; const ada = {}; semua.forEach((b) => { ada[b.id] = 1; });
  const tanpaTunjuk = ambilUtangPemasokMutasi().filter((m) => m.tipe === 'bayar' && bpNama(m.pemasok) === bpNama(pemasok) && !ada[String(m.bonId || '')]).sort(bpUrutDok);
  return { bon, semua, tanpaTunjuk, pemasok: bpNama(pemasok), total: semua.reduce((a, b) => a + b.sisa, 0) };
}
const bpCariBayar = (id) => ambilUtangPemasokMutasi().find((x) => String(x.id) === String(id) && x.tipe === 'bayar') || null;
const bpPerubahanSisa = (sebelum, sesudah) => sebelum.map((b) => { const s = sesudah.find((x) => x.id === b.id) || { sisa: 0 }; return { id: b.id, label: b.label, dari: b.sisa, ke: s.sisa }; }).filter((x) => x.dari !== x.ke);
/** PINDAH pembayaran bayarId ke bon keBonId (pemasok yang sama): hitungan sebelum ⇄ sesudah lewat mesin, kalimatnya, alasan penolakan. */
export function hitungPindahBayar(bayarId, keBonId) {
  const m = bpCariBayar(bayarId); if (!m) return { tolak: 'Pembayaran itu sudah tidak ada' };
  const P = bpNama(m.pemasok); const semua = bpSemuaBon(P); const dari = semua.find((b) => b.id === String(m.bonId || '')) || null; const ke = semua.find((b) => b.id === String(keBonId || '')) || null;
  let tolak = '';
  if (!ke) tolak = 'Pilih bon ' + P + ' yang sebenarnya dibayar';
  else if (dari && dari.id === ke.id) tolak = 'Pembayaran ini sudah menunjuk ' + ke.label;
  else if (ke.tanggal && m.tanggal && ke.tanggal > m.tanggal) tolak = 'Bon ' + tanggalPendek(ke.tanggal) + ' belum ada waktu pembayaran ' + tanggalPendek(m.tanggal) + ' dicatat — pembayaran tidak bisa menunjuk bon yang datang sesudahnya';
  else tolak = tolakKunci('utangPemasokMutasi', m, 'pembayaran bulan itu tidak bisa dipindah lagi');
  const baru = Object.assign({}, m, { bonId: ke ? ke.id : String(m.bonId || ''), bonTanggal: ke ? (ke.tanggal || null) : (m.bonTanggal || null) });
  const sesudah = ke ? denganCacheSementara([{ koleksi: 'utangPemasokMutasi', data: baru }], () => bpSemuaBon(P)) : semua;
  const ubah = bpPerubahanSisa(semua, sesudah); const lain = ubah.filter((x) => (!dari || x.id !== dari.id) && (!ke || x.id !== ke.id));
  const T0 = semua.reduce((a, b) => a + b.sisa, 0); const T1 = sesudah.reduce((a, b) => a + b.sisa, 0);
  // KELEBIHAN (sanggahan E2): pembayaran lebih besar dari sisa bon tujuan → sisanya mengalir ke bon tertua yang belum lunas (aturan mesin). Disebut berapa,
  // kenapa, dan bon mana yang menerimanya — termasuk bila itu bon ASAL (sisanya naik kurang dari nominal pembayaran: "bon 18 Sep sisa 44,625 jt, bukan 44,86 jt").
  const nom = Math.round(Number(m.nominal) || 0); const lebih = ke ? Math.max(0, nom - ke.sisa) : 0;
  const terima = !lebih || !dari ? [] : sesudah.map((b) => { const s0 = (semua.find((x) => x.id === b.id) || { sisa: 0 }).sisa; const harap = b.id === dari.id ? s0 + nom : s0; return { id: b.id, label: b.label, asal: b.id === dari.id, n: b.id === ke.id ? 0 : harap - b.sisa }; }).filter((x) => x.n > 0);
  const kataLebih = !lebih ? '' : ' · KELEBIHAN ' + RP(lebih) + ' (pembayaran ' + RP(nom) + ' > sisa ' + ke.label + ' ' + RP(ke.sisa) + ') mengalir ke bon tertua yang belum lunas'
    + (terima.length ? ': ' + terima.map((x) => x.label + (x.asal ? ' (bon asal pembayaran ini)' : '') + ' ' + RP(x.n)).join(', ') : ' (aturan mesin)');
  return { m, dari, ke, baru, sebelum: semua, sesudah, ubah, lain, lebih, terima, total: { dari: T0, ke: T1 }, tolak,
    arti: ke && !tolak ? 'Pembayaran ' + tanggalPendek(m.tanggal) + ' ' + RP(nom) + ': ' + bpLabelBon(dari) + ' → ' + ke.label + ' · '
      + ubah.map((x) => x.label + ' sisa ' + RP(x.dari) + ' → ' + RP(x.ke)).join(' · ') + kataLebih
      + (lain.length && !lebih ? ' (pembayaran lain yang mengalir ke bon tertua ikut bergeser — aturan mesin)' : '')
      + ' · utang ke ' + P + ' ' + (T0 === T1 ? 'tetap ' + RP(T1) : RP(T0) + ' → ' + RP(T1)) + ' · uang toko & laba TIDAK berubah' : '' };
}
export function susunPindahBayar(bayarId, keBonId, alasan, w) {
  const H = hitungPindahBayar(bayarId, keBonId); if (H.tolak) return { tolak: H.tolak };
  const al = bpAlasan(alasan); if (al.length < BP_ALASAN_MIN) return { tolak: 'Tulis alasannya dulu (mis. "pemasok: bon 31 Agu yang lunas, bukan 18 Sep") — jejaknya disimpan bersama pembayaran ini' };
  const data = Object.assign({}, H.baru, { alasanKoreksi: al, dikoreksiPada: w.kini,
    riwayat: bpRiwayat(H.m, w, { jenis: 'pindahBon', teks: 'dipindah dari ' + bpLabelBon(H.dari) + ' ke ' + H.ke.label + ': ' + al, dari: { bonId: String(H.m.bonId || ''), bonTanggal: H.m.bonTanggal || null }, ke: { bonId: H.ke.id, bonTanggal: H.ke.tanggal || null }, alasan: al }) });
  return { dokumen: [{ koleksi: 'utangPemasokMutasi', data }], patch: { betul: null, kabar: 'Pembetulan tersimpan — ' + H.arti + '. Nilai lama ada di riwayat pembayaran itu.', kabarAwas: !!H.lain.length || H.lebih > 0 } };
}
/**
 * Betulkan JUMLAH satu pembayaran (salah ketik): utang & kas bergeser sebesar selisihnya; laba tetap. PENJAGA BESARAN (sanggahan E2): selisih BESAR wajib
 * ketukan kedua dengan kalimat yang menyebut angka lama → baru — jumlah baru ≥ 2× / ≤ ½ yang lama (nol kelebihan / kurang satu), kenaikan melebihi sisa bon
 * yang ditunjuk (kelebihannya mengalir ke bon lain), uang toko jadi minus, atau pembayaran TUNAI dari laci di hari yang sudah DITUTUP (selisih laci malam
 * itu ikut bergeser — tutup hari tidak dihitung ulang otomatis).
 */
export function hitungNominalBayar(bayarId, ketik) {
  const m = bpCariBayar(bayarId); if (!m) return { tolak: 'Pembayaran itu sudah tidak ada' };
  const P = bpNama(m.pemasok); const n = Math.round(bpAngka(ketik)); const lama = Math.round(Number(m.nominal) || 0); let tolak = '';
  if (!(n > 0)) tolak = 'Ketik jumlah yang sebenarnya dibayar'; else if (n === lama) tolak = 'Jumlahnya sama dengan yang tercatat'; else tolak = tolakKunci('utangPemasokMutasi', m, 'jumlah pembayaran bulan itu tidak bisa diubah lagi');
  const baru = Object.assign({}, m, { nominal: n > 0 ? n : lama }); const semua = bpSemuaBon(P); const kas0 = kasPada();
  const sesudah = n > 0 ? denganCacheSementara([{ koleksi: 'utangPemasokMutasi', data: baru }], () => ({ bon: bpSemuaBon(P), kas: kasPada(), kasHari: m.tanggal ? kasPada(m.tanggal) : null })) : { bon: semua, kas: kas0, kasHari: null };
  const T0 = semua.reduce((a, b) => a + b.sisa, 0); const T1 = sesudah.bon.reduce((a, b) => a + b.sisa, 0); const d = n - lama; const tempat = namaTempat(m.dari || 'laci');
  const bonDitunjuk = semua.find((b) => b.id === String(m.bonId || '')) || null; const besar = [];
  if (n > 0 && !tolak) {
    if (lama > 0 && n >= lama * 2) besar.push(RP(lama) + ' → ' + RP(n) + ' = ' + String(Math.round(n / lama * 10) / 10).replace('.', ',') + '× lipat (nol kelebihan?)');
    else if (n * 2 <= lama) besar.push(RP(lama) + ' → ' + RP(n) + ' = tinggal ' + Math.round(n / lama * 100) + ' % (nol kurang satu?)');
    if (d > 0 && bonDitunjuk && d > bonDitunjuk.sisa) besar.push('naik ' + RP(d) + ', lebih dari sisa ' + bonDitunjuk.label + ' ' + RP(bonDitunjuk.sisa) + ' — kelebihannya mengalir ke bon lain');
    if (d > 0 && sesudah.kas !== null && sesudah.kas < 0) besar.push('uang toko jadi MINUS ' + RP(-sesudah.kas));
    else if (d > 0 && sesudah.kasHari !== null && sesudah.kasHari !== undefined && sesudah.kasHari < 0) besar.push('uang toko akhir hari ' + tanggalPendek(m.tanggal) + ' jadi MINUS ' + RP(-sesudah.kasHari));
    if ((m.dari || 'laci') === 'laci' && ambilTutupHari().some((x) => x && x.tanggal === m.tanggal)) besar.push('hari ' + tanggalPendek(m.tanggal) + ' sudah DITUTUP — selisih laci malam itu ikut bergeser (tutup hari tidak dihitung ulang)');
  }
  return { m, n, lama, baru, ubah: bpPerubahanSisa(semua, sesudah.bon), total: { dari: T0, ke: T1 }, kas: { dari: kas0, ke: sesudah.kas }, tolak, besar,
    besarTeks: besar.length ? 'Jumlah pembayaran ' + tanggalPendek(m.tanggal) + ' berubah BESAR: ' + RP(lama) + ' → ' + RP(n) + ' · ' + besar.join(' · ') : '',
    arti: !tolak ? 'Pembayaran ' + tanggalPendek(m.tanggal) + ' ' + RP(lama) + ' → ' + RP(n) + ' · utang ke ' + P + ' ' + RP(T0) + ' → ' + RP(T1) + ' · uang toko (' + (m.dari ? tempat : 'kantong tidak dicatat') + ') ' + (d > 0 ? 'berkurang ' : 'bertambah ') + RP(Math.abs(d))
      + (kas0 !== null && sesudah.kas !== null && kas0 === sesudah.kas ? ' di hari itu (titik kas sesudahnya sudah menyerapnya — kas sekarang tetap)' : '') + ' · laba TIDAK berubah' : '' };
}
export function susunNominalBayar(bayarId, ketik, alasan, w, yakin) {
  const H = hitungNominalBayar(bayarId, ketik); if (H.tolak) return { tolak: H.tolak };
  const al = bpAlasan(alasan); if (al.length < BP_ALASAN_MIN) return { tolak: 'Tulis alasannya dulu (mis. "salah ketik — yang diserahkan Rp…") — jejaknya disimpan bersama pembayaran ini' };
  if (H.besar.length && !yakin) return { tolak: H.besarTeks + '. Ketuk sekali lagi kalau memang benar.', perluYakin: true };
  const data = Object.assign({}, H.baru, { alasanKoreksi: al, dikoreksiPada: w.kini, riwayat: bpRiwayat(H.m, w, { jenis: 'nominalBayar', teks: 'jumlah ' + RP(H.lama) + ' → ' + RP(H.n) + ': ' + al, dari: H.lama, ke: H.n, alasan: al }) });
  return { dokumen: [{ koleksi: 'utangPemasokMutasi', data }], patch: { betul: null, kabar: 'Pembetulan tersimpan — ' + H.arti + '. Jumlah lama ada di riwayat pembayaran itu.', kabarAwas: false } };
}
/** NOMOR bon pemasok (nomor di kertas bon). Mengganti nomor yang sudah ada wajib beralasan; nomor yang sama di bon lain pemasok yang sama ditolak. */
export function susunNoBon(bonId, pemasok, no, alasan, w) {
  const semua = bpSemuaBon(pemasok); const b = semua.find((x) => x.id === String(bonId)); if (!b) return { tolak: 'Bon itu tidak ada' };
  const nb = String(no || '').trim().replace(/\s+/g, ' ').slice(0, 30); if (!nb) return { tolak: 'Ketik nomor bonnya (angka di kertas bon pemasok)' };
  if (nb === b.noBon) return { tolak: 'Nomor bon itu sudah tercatat' };
  const kembar = semua.find((x) => x.id !== b.id && x.noBon === nb); if (kembar) return { tolak: 'Nomor ' + nb + ' sudah dipakai ' + kembar.label + ' — satu kertas bon untuk satu kedatangan' };
  const al = bpAlasan(alasan); if (b.noBon && al.length < BP_ALASAN_MIN) return { tolak: 'Nomor lama ' + b.noBon + ' diganti — tulis alasannya dulu' };
  const kunci = tolakKunci(b.koleksi, b.dok, 'nomor bonnya tidak bisa ditulis lagi'); if (kunci) return { tolak: kunci };
  const data = Object.assign({}, b.dok, { noBon: nb, riwayat: bpRiwayat(b.dok, w, { jenis: 'noBon', teks: (b.noBon ? 'nomor bon ' + b.noBon + ' → ' + nb : 'nomor bon pemasok ' + nb) + (al ? ': ' + al : ''), dari: b.noBon || '', ke: nb, alasan: al }) });
  return { dokumen: [{ koleksi: b.koleksi, data }], patch: { kabar: 'Nomor bon ' + nb + ' dicatat di bon ' + (b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tanggal') + ' ' + bpNama(pemasok) + (b.noBon ? ' (dulu ' + b.noBon + ')' : '') + ' — utang, kas, dan laba tidak berubah', kabarAwas: false } };
}
/** Bon LAMA (sebelum sistem): tanggal & nilai dibetulkan. isi = { tgl ('' = tidak diketahui), ketik }. */
export function hitungBetulBonLama(bonId, isi) {
  const m = ambilUtangPemasokMutasi().find((x) => String(x.id) === String(bonId) && x.tipe === 'saldoAwal') || null; if (!m) return { tolak: 'Hanya bon LAMA (sebelum sistem) yang dibetulkan di sini — bon kedatangan lewat Stok › Barang masuk › koreksi' };
  const P = bpNama(m.pemasok); const I = Object.assign({ tgl: m.bonTanggal || '', ketik: String(m.nominal || '') }, isi || {}); const n = Math.round(bpAngka(I.ketik)); const tgl = String(I.tgl || '').trim();
  let tolak = '';
  if (!(n > 0)) tolak = 'Ketik nilai bonnya'; else if (tgl && !/^\d{4}-\d{2}-\d{2}$/.test(tgl)) tolak = 'Tanggal bon tidak terbaca';
  else if (n === Math.round(Number(m.nominal) || 0) && tgl === String(m.bonTanggal || '')) tolak = 'Tidak ada yang berubah';
  else tolak = tolakKunci('utangPemasokMutasi', m, 'bon lama bulan itu tidak bisa diubah lagi') || tolakKunci('utangPemasokMutasi', Object.assign({}, m, { bonTanggal: tgl || null }), 'tanggal baru jatuh di bulan terkunci');
  const baru = Object.assign({}, m, { nominal: n > 0 ? n : m.nominal, bonTanggal: tgl || null }); const semua = bpSemuaBon(P);
  const sesudah = n > 0 ? denganCacheSementara([{ koleksi: 'utangPemasokMutasi', data: baru }], () => bpSemuaBon(P)) : semua; const T0 = semua.reduce((a, b) => a + b.sisa, 0); const T1 = sesudah.reduce((a, b) => a + b.sisa, 0);
  return { m, n, tgl, baru, ubah: bpPerubahanSisa(semua, sesudah), total: { dari: T0, ke: T1 }, tolak,
    arti: !tolak ? 'Bon lama ' + P + ': nilai ' + RP(m.nominal || 0) + ' → ' + RP(n) + ', tanggal ' + (m.bonTanggal ? tanggalPendek(m.bonTanggal) : 'tidak diketahui') + ' → ' + (tgl ? tanggalPendek(tgl) : 'tidak diketahui') + ' · utang ke ' + P + ' ' + RP(T0) + ' → ' + RP(T1) + ' · uang toko, stok, dan laba TIDAK berubah' : '' };
}
export function susunBetulBonLama(bonId, isi, alasan, w) {
  const H = hitungBetulBonLama(bonId, isi); if (H.tolak) return { tolak: H.tolak };
  const al = bpAlasan(alasan); if (al.length < BP_ALASAN_MIN) return { tolak: 'Tulis alasannya dulu — jejaknya disimpan bersama bon ini' };
  const data = Object.assign({}, H.baru, { alasanKoreksi: al, dikoreksiPada: w.kini, riwayat: bpRiwayat(H.m, w, { jenis: 'bonLama', teks: 'nilai ' + RP(H.m.nominal || 0) + ' → ' + RP(H.n) + ', tanggal ' + (H.m.bonTanggal || '—') + ' → ' + (H.tgl || '—') + ': ' + al, dari: { nominal: H.m.nominal, bonTanggal: H.m.bonTanggal || null }, ke: { nominal: H.n, bonTanggal: H.tgl || null }, alasan: al }) });
  return { dokumen: [{ koleksi: 'utangPemasokMutasi', data }], patch: { betul: null, kabar: 'Pembetulan tersimpan — ' + H.arti + '. Nilai lama ada di riwayat bon itu.', kabarAwas: false } };
}
