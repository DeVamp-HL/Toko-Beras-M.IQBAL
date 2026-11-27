// TAUTAN BEKU DASBOR untuk pihak luar (paket P8, owner 27 Nov 2026 — sensus B103). Logika TANPA DOM, nama berawalan dpb. Dijaga alat-uji/uji_arsip_audit_p8.py.
//
// Keputusan owner 27 Nov 2026: OWNER SAJA yang membuat & mencabut; tiap tautan owner MENCENTANG bagian yang ikut (bawaan: omzet & nota, kg terjual, laba kotor &
// margin); nama pelanggan / pemasok / staf TIDAK PERNAH ikut (isinya angka saja); berlaku 1 · 7 · 30 · 90 hari (bawaan 7) — lewat batasnya SERVER sendiri yang menolak
// (rules v26 dasborPublik: get hanya bila jam server < `sampai`; tulis hanya bila `sampai` ≤ jam server + 91 hari).
// "BEKU" = angka DIHITUNG SEKALI saat tautan dibuat dan tidak pernah diperbarui (berbeda dengan cek bon yang ditulis ulang) — halaman menyebut jam bekunya.
// Satu dokumen dasborPublik/<kode acak 22 huruf> (kode = bpKodeBaru cek bon: pembangkit acak kriptografis, tidak bisa ditebak, tidak bisa didaftar — list owner saja).
// Angka = fungsi yang SUDAH dipakai Dasbor / Laporan (tanpa rumus baru): omzet & nota = lpRekapRentang (Laporan › Harian/rentang), kg = klKgBulan (Dasbor › Margin & target),
// laba kotor / margin / laba bersih = klMarginBulan (Laporan › Laba), stok nilai · piutang · utang pemasok = neracaPada (Laporan › Neraca), stok kg = daftarBarang (Stok ›
// Gudang), kas = saldoKantong (Uang › Pindah uang). Satu bagian yang galat tidak menggagalkan yang lain (disebut "belum bisa dihitung").
import { cacheMentah } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';
import { akhirBulanIso } from '../mesin/pembantu.js';
import { lpRekapRentang, neracaPada } from './laporan-logika.js';
import { klKgBulan, klMarginBulan } from './kpi-laba-logika.js';
import { saldoKantong } from './uang-logika.js';
import { daftarBarang } from './stok-logika.js';
import { bpKodeBaru, bpKodeSah } from './bon-publik-logika.js';

export const DPB_KOLEKSI = 'dasborPublik';
export const DPB_TOKO = 'Toko Beras M.IQBAL';
// [id, nama di layar, ikut bawaan, kalimat di halaman tamu]
export const DPB_BAGIAN = [
  ['omzet', 'Omzet & jumlah nota', true], ['kg', 'Kg beras terjual', true], ['laba', 'Laba kotor & margin', true], ['bersih', 'Laba bersih', false],
  ['stok', 'Stok (kg & nilai modal)', false], ['piutang', 'Total piutang pelanggan', false], ['utang', 'Total utang ke pemasok', false], ['kas', 'Kas & rekening', false]];
export const DPB_HARI = [1, 7, 30, 90];
export const DPB_HARI_BAWAAN = 7;
export const DPB_BULAN = 4;               // bulan ini + 3 bulan sebelumnya
export const DPB_UNTUK_MAKS = 40;
export const dpbBagianBawaan = () => DPB_BAGIAN.filter((b) => b[2]).map((b) => b[0]);
export const dpbNamaBagian = (id) => (DPB_BAGIAN.find((b) => b[0] === id) || [id, id])[1];
const dpbGeserBulan = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; return new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)).toISOString().slice(0, 7); };
const DPB_NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
const dpbNamaBulan = (key) => DPB_NAMA_BULAN[Number(key.slice(5, 7)) - 1] + ' ' + key.slice(0, 4);
const dpbBulat = (n) => (n === null || n === undefined || !isFinite(Number(n)) ? null : Math.round(Number(n)));
const dpbSatuDesimal = (n) => (n === null || n === undefined || !isFinite(Number(n)) ? null : Math.round(Number(n) * 10) / 10);
/** Kg ringkas berpemisah ribuan & satu desimal ("18.198,3 kg"). */
export const dpbKgTeks = (n) => { if (n === null || n === undefined || !isFinite(Number(n))) return '—'; const s = String(Math.round(Number(n) * 10) / 10).split('.'); return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (s[1] ? ',' + s[1] : '') + ' kg'; };
const dpbCoba = (f) => { try { return f(); } catch (e) { return { galat: String((e && e.message) || e).slice(0, 120) }; } };
/** Jam `sampai` dokumen → milidetik (Timestamp Firestore · Date · {seconds} · teks ISO). NaN bila tidak terbaca. */
export function dpbMs(v) {
  if (v === null || v === undefined || v === '') return NaN;
  if (typeof v.toMillis === 'function') return v.toMillis(); if (v instanceof Date) return v.getTime();
  if (typeof v === 'object' && isFinite(Number(v.seconds))) return Number(v.seconds) * 1000 + Math.round((Number(v.nanoseconds) || 0) / 1e6);
  const t = new Date(String(v)).getTime(); return isFinite(t) ? t : NaN;
}
/** Pilihan owner yang sah: bagian (≥ 1, dikenal), hari (salah satu DPB_HARI), untuk (≤ 40 huruf, boleh kosong). → { tolak } atau { bagian, hari, untuk }. */
export function dpbPilihSah(pil) {
  const P = pil || {}; const ada = DPB_BAGIAN.map((b) => b[0]); const bagian = ada.filter((id) => (P.bagian || []).indexOf(id) >= 0);
  if (!bagian.length) return { tolak: 'Centang minimal satu bagian yang boleh terlihat' };
  const hari = Number(P.hari); if (DPB_HARI.indexOf(hari) < 0) return { tolak: 'Pilih berlaku berapa lama (1, 7, 30, atau 90 hari)' };
  const untuk = String(P.untuk || '').replace(/\s+/g, ' ').trim(); if (untuk.length > DPB_UNTUK_MAKS) return { tolak: 'Catatan "untuk siapa" paling panjang ' + DPB_UNTUK_MAKS + ' huruf' };
  return { bagian, hari, untuk };
}
/** Angka BEKU per bagian yang dicentang (hanya angka; tanpa nama orang). kini = jam pembekuan. */
export function dpbIsi(bagian, kini) {
  const B = bagian || []; const iso = hariIniIso(kini); const pakai = (id) => B.indexOf(id) >= 0; const out = {};
  const perBulan = pakai('omzet') || pakai('kg') || pakai('laba') || pakai('bersih');
  if (perBulan) {
    out.bulan = []; for (let i = 0; i < DPB_BULAN; i++) { const key = dpbGeserBulan(iso.slice(0, 7), -i); const akhir = akhirBulanIso(key); const sampai = akhir < iso ? akhir : iso; const x = { key, nama: dpbNamaBulan(key), berjalan: key === iso.slice(0, 7), sampaiTanggal: sampai };
      if (pakai('omzet')) { const R = dpbCoba(() => lpRekapRentang(key + '-01', sampai)); if (R.galat || R.diarsip && (R.omzet === null || R.omzet === undefined)) x.omzetGalat = true; else { x.omzet = dpbBulat(R.omzet); x.nota = dpbBulat(R.n); } }
      if (pakai('kg')) { const K = dpbCoba(() => klKgBulan(key, kini)); if (K.galat || K.diarsip) x.kgGalat = true; else x.kg = dpbSatuDesimal(K.kg); }
      if (pakai('laba') || pakai('bersih')) { const M = dpbCoba(() => klMarginBulan(key, kini)); const ok = !M.galat && !M.diarsip && !M.tanpaCatatan;
        if (pakai('laba')) { if (!ok) x.labaGalat = true; else { x.labaKotor = dpbBulat(M.labaKotor); x.marginPct = dpbSatuDesimal(((M.tangga || []).find((t) => t.id === 'kotor') || {}).pct); } }
        if (pakai('bersih')) { if (!ok) x.bersihGalat = true; else x.labaBersih = dpbBulat(M.labaBersih); } }
      out.bulan.push(x); }
  }
  if (pakai('stok') || pakai('piutang') || pakai('utang')) {
    const N = dpbCoba(() => neracaPada(null, kini).N);
    if (pakai('stok')) { const kg = dpbCoba(() => daftarBarang().filter((b) => b.jenis === 'karung' && !b.wadahStok && Math.abs(b.sisa) > 0.004).reduce((a, b) => a + b.sisa, 0));
      out.stok = { kg: typeof kg === 'number' ? dpbSatuDesimal(kg) : null, nilai: N.galat ? null : dpbBulat(N.stok) }; }
    if (pakai('piutang')) out.piutang = N.galat ? null : dpbBulat(N.piutang);
    if (pakai('utang')) out.utangPemasok = N.galat ? null : dpbBulat(N.utangPemasok);
  }
  if (pakai('kas')) { const S = dpbCoba(() => saldoKantong()); out.kas = S.galat || !S.ada ? { ada: false } : { ada: true, total: dpbBulat(S.total), laci: dpbBulat(S.laci), brankas: dpbBulat(S.brankas), rekening: dpbBulat(S.rekening) }; }
  return out;
}
/** Buat satu tautan beku (owner). pil = { bagian, hari, untuk }; w = { kini (ISO), tanggal, jam }; acak = pembangkit untuk uji. */
export function dpbSusunBuat(pil, kini, w, acak) {
  const P = dpbPilihSah(pil); if (P.tolak) return P;
  const kode = bpKodeBaru(acak); const sampai = new Date(kini.getTime() + P.hari * 86400000);
  const data = Object.assign({ id: kode, toko: DPB_TOKO, dibuat: String(w.kini), sampai, hari: P.hari, untuk: P.untuk, bagian: P.bagian.slice() }, dpbIsi(P.bagian, kini));
  return { dokumen: [{ koleksi: DPB_KOLEKSI, data }], kode, sampai,
    patch: { kabar: 'Tautan beku Dasbor dibuat — berlaku ' + P.hari + ' hari (sampai ' + dpbJamTeks(sampai.getTime()) + '); siapa pun yang memegang tautannya bisa melihat ' + P.bagian.map(dpbNamaBagian).join(', ').toLowerCase(), kabarAwas: false } };
}
const DPB_BULAN3 = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const dpbDua = (n) => (n < 10 ? '0' : '') + n;
/** Jam setempat ringkas "4 Des 2026 10.00". */
export function dpbJamTeks(ms) { const d = new Date(ms); if (!isFinite(d.getTime())) return '—'; return d.getDate() + ' ' + DPB_BULAN3[d.getMonth()] + ' ' + d.getFullYear() + ' ' + dpbDua(d.getHours()) + '.' + dpbDua(d.getMinutes()); }
/** Daftar tautan (kelola): aktif dulu (yang paling cepat habis dulu), lalu yang sudah lewat. */
export function dpbSemua(kini) {
  const t = kini.getTime();
  return (cacheMentah(DPB_KOLEKSI) || []).filter((d) => d && bpKodeSah(d.id)).map((d) => { const ms = dpbMs(d.sampai); const aktif = isFinite(ms) && ms > t;
    return { kode: String(d.id), untuk: String(d.untuk || ''), dibuat: String(d.dibuat || ''), sampaiMs: ms, sampaiTeks: dpbJamTeks(ms), aktif, hari: Number(d.hari) || null,
      sisaHari: aktif ? Math.ceil((ms - t) / 86400000) : 0, bagian: (d.bagian || []).map(dpbNamaBagian) }; })
    .sort((a, b) => (b.aktif ? 1 : 0) - (a.aktif ? 1 : 0) || (a.aktif ? a.sampaiMs - b.sampaiMs : b.sampaiMs - a.sampaiMs));
}
/** Cabut satu tautan (owner): dokumennya dihapus — tautannya langsung mati. */
export function dpbSusunCabut(kode) {
  const d = (cacheMentah(DPB_KOLEKSI) || []).find((x) => x && String(x.id) === String(kode)); if (!d) return { tolak: 'Tautan itu sudah tidak ada' };
  return { dokumen: [], hapus: [{ koleksi: DPB_KOLEKSI, id: String(kode) }], patch: { kabar: 'Tautan Dasbor' + (d.untuk ? ' untuk ' + d.untuk : '') + ' DICABUT — tautan itu tidak bisa dibuka lagi', kabarAwas: false } };
}
/** Bersihkan tautan yang sudah lewat (owner) — server sudah menolaknya; ini cuma merapikan daftar. */
export function dpbSusunBersihkan(kini) {
  const lewat = dpbSemua(kini).filter((x) => !x.aktif); if (!lewat.length) return { tolak: 'Tidak ada tautan yang sudah lewat' };
  return { dokumen: [], hapus: lewat.map((x) => ({ koleksi: DPB_KOLEKSI, id: x.kode })), patch: { kabar: lewat.length + ' tautan yang sudah lewat dihapus dari daftar', kabarAwas: false } };
}
/** Tautan halaman tamu: folder /baru/ + dasbor-publik.html#k=<kode>; proyek lain dari toko ikut disebut (p=). */
export function dpbTautan(kode, dasar, proyek) {
  return String(dasar || '') + 'dasbor-publik.html#k=' + kode + (proyek && proyek !== 'toko-beras-m-iqbal' ? '&p=' + encodeURIComponent(proyek) : '');
}
/** Pesan WhatsApp: tautan + sampai kapan berlaku. */
export function dpbPesanWa(untuk, tautan, sampaiMs) {
  return 'Halo' + (untuk ? ' ' + String(untuk).trim() : '') + ', ini ringkasan angka ' + DPB_TOKO + ' (angka dibekukan saat tautan dibuat):\n' + tautan + '\nBerlaku sampai ' + dpbJamTeks(sampaiMs) + '. Mohon tidak disebarkan.';
}
/** Pratinjau sebelum dibuat (owner): bagian & contoh angka bulan ini — angka sama dengan yang akan dibekukan. */
export function dpbPratinjau(bagian, kini) {
  const I = dpbIsi(bagian, kini); const b0 = (I.bulan || [])[0] || null;
  return { isi: I, baris: [].concat(b0 && b0.omzet !== undefined ? [['Omzet ' + b0.nama, RP(b0.omzet) + ' · ' + b0.nota + ' nota']] : [])
    .concat(b0 && b0.kg !== undefined && b0.kg !== null ? [['Kg terjual ' + b0.nama, dpbKgTeks(b0.kg)]] : [])
    .concat(b0 && b0.labaKotor !== undefined ? [['Laba kotor ' + b0.nama, RP(b0.labaKotor) + (b0.marginPct !== null && b0.marginPct !== undefined ? ' · margin ' + String(b0.marginPct).replace('.', ',') + ' %' : '')]] : [])
    .concat(b0 && b0.labaBersih !== undefined ? [['Laba bersih ' + b0.nama, RP(b0.labaBersih)]] : [])
    .concat(I.stok ? [['Stok', dpbKgTeks(I.stok.kg) + ' · ' + (I.stok.nilai === null ? '—' : RP(I.stok.nilai))]] : [])
    .concat(I.piutang !== undefined ? [['Total piutang', I.piutang === null ? '—' : RP(I.piutang)]] : []).concat(I.utangPemasok !== undefined ? [['Total utang ke pemasok', I.utangPemasok === null ? '—' : RP(I.utangPemasok)]] : [])
    .concat(I.kas ? [['Kas & rekening', I.kas.ada ? RP(I.kas.total) : 'belum ada titik kas']] : []) };
}
