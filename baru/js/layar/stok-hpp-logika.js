// LAYAR STOK — HPP / MODAL (ST6-A+B, dikunci owner 19 Sep 2026): kartu modal per nama beras + garis waktu + koreksi (satu nama / massal).
// Kejujuran mesin: MODAL yang dipakai laba & neraca = RATA-RATA TERTIMBANG seluruh kedatangan (hitungStokKarungPerMerk.hppTerakhirPerKg — namanya menyesatkan,
// isinya rata-rata). Aturan owner 13 Sep "penilaian = harga beli TERBARU" belum diterapkan ke mesin (keputusan owner; mengubahnya menggeser laba historis) →
// kartu memajang KEDUANYA berlabel. HPP tidak disimpan sebagai angka sendiri: ia TURUNAN kedatangan. Maka "koreksi HPP" di sini = mengoreksi HARGA BELI PER KG
// pada kedatangan TERAKHIR nama itu (dokumen batchMasuk yang sama, lewat susunSimpanMasuk: alasan wajib, riwayat tercatat) — bukan menimpa angka di tempat lain.
// Angka aneh DITOLAK dengan kalimat (bukan dipotong diam-diam); lonjakan > batas ditanya; di atas harga jual boleh tapi diperingatkan RUGI; margin Rp0 = "disengaja?" (ambang `>`).
// Tiap koreksi menulis perubahan nilai rak (Δ modal rata-rata × sisa kg) ke koleksi baru koreksiHpp. Massal = semua-atau-tidak-sama-sekali (satu writeBatch).
import { hitungStokKarungPerMerk, hitungHppMerkDalamBatch } from '../mesin/beku.js';
import { cariHargaKarungPerKg } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilProduksiBerlaku, cacheMentah, tolakKunciTanggal, stokMerekSaja, petaUkuran, ingatStokKarung, denganCacheSementara } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { MF_DOK, MF_KOLOM, mfMulaiDari, hppKeluarPerKg } from '../mesin/modal-fifo.js';
import { drafDariKedatangan, susunSimpanMasuk, ckBayarBonId } from './stok-catat-logika.js';

export const ATUR_HPP_BAWAAN = { batasLonjak: 10, lantaiHpp: 5000, kaliMaks: 3 };
export const TAB_HPP = [['kartu', 'Kartu modal'], ['garis', 'Garis waktu'], ['kelas', 'Per kelas'], ['massal', 'Koreksi massal']];   // putaran 30: harga beli per kelas mutu
const hpAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const hpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const hpKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const hpFondasi = (b) => !!(b && (b.stokAwal || b.tutupBuku));
const hpUrutLama = (a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || (Number(a.id) || 0) - (Number(b.id) || 0);

export function aturHpp() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'hpp') || null;
  const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : ATUR_HPP_BAWAAN[k]);
  return { batasLonjak: ambil('batasLonjak', (n) => n >= 0 && n <= 100), lantaiHpp: ambil('lantaiHpp', (n) => n >= 0), kaliMaks: ATUR_HPP_BAWAAN.kaliMaks, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
export function susunAturHpp(isi, w) {
  const kini = aturHpp(); const baca = (k, syarat, teks) => { if (hpKosong(isi[k])) return { nilai: kini[k] }; const n = hpAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const l = baca('batasLonjak', (n) => n >= 0 && n <= 100, 'Batas lonjakan HPP harus 0–100 %'); if (l.tolak) return { tolak: l.tolak };
  const t = baca('lantaiHpp', (n) => n >= 0 && n <= 1000000, 'Lantai HPP per kg harus 0–1.000.000'); if (t.tolak) return { tolak: t.tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'hpp', tanggal: w.tanggal, jam: w.jam, batasLonjak: l.nilai, lantaiHpp: t.nilai } }],
    patch: { aturHp: null, kabar: 'Aturan HPP disimpan — koreksi yang mengubah modal > ' + l.nilai + ' % ditanya · HPP di bawah ' + RP(t.nilai) + '/kg ditolak', kabarAwas: false } };
}

// ---------- SAKLAR MODAL FIFO (owner 9 Okt 2026: "Bangun, saklar di lu") ----------
// aturanToko/catatStok.modalFifoMulai = hari pertama FIFO (mesin/modal-fifo.js). Hari mulai SELALU sesudah hari ini (besok atau 1 Jan): bulan yang sudah
// lewat tidak berubah, dan HP karyawan sempat menerima setelannya sebelum hari itu. Sudah berjalan → hanya bisa dimatikan (nota yang sudah tercatat tetap).
// Menulis dokumen catatStok UTUH (kolom Aturan Barang masuk ikut disalin) + riwayat saklar.
const teksLapisan = (st) => { const L = st.lapisan || []; const P = st.posKeluar || 0; let awal = 0; for (let i = 0; i < L.length; i++) { const akhir = awal + L[i].kg; if (P < akhir) {
  const sisaLap = Math.min(akhir - Math.max(P, awal), L[i].kg); return 'keluar berikutnya: ' + (L[i].asal === 'buka' ? 'sisa sebelum FIFO (modal rata-rata saat itu)' : (L[i].asal === 'adukan' ? 'adukan ' : 'kedatangan ') + tanggalPendek(L[i].tanggal)) + ' · ' + hpKG(sisaLap) + ' @' + RP(Math.round(L[i].harga)) + '/kg'; } awal = akhir; }
  return 'keluar berikutnya: belum ada kedatangan yang tersisa (stok habis/minus) — dinilai kedatangan terakhir ' + RP(Math.round(st.hppKeluarPerKg || 0)) + '/kg'; };
const hpBesok = (hari) => { const d = new Date(hari + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + 1); return d.toISOString().slice(0, 10); };
export function saklarFifo(kini) {
  const hari = hariIniIso(kini || new Date(Date.now())); const dok = cacheMentah('aturan').find((d) => String(d.id) === MF_DOK) || null; const mulai = mfMulaiDari(dok ? [dok] : []);
  const besok = hpBesok(hari); const tahunBaru = String(Number(hari.slice(0, 4)) + 1) + '-01-01';
  const pilihan = [{ tanggal: besok, label: 'mulai besok (' + tanggalPendek(besok) + ')' }].concat(tahunBaru !== besok ? [{ tanggal: tahunBaru, label: 'mulai 1 Jan ' + tahunBaru.slice(0, 4) + ' (tahun buku baru)' }] : []);
  const keadaan = !mulai ? 'mati' : mulai > hari ? 'rencana' : 'nyala';
  return { hari, mulai, keadaan, pilihan, riwayat: (dok && Array.isArray(dok.riwayatModalFifo) ? dok.riwayatModalFifo : []).slice().reverse(),
    teks: keadaan === 'mati' ? 'Modal sekarang: RATA-RATA semua kedatangan. Saklar FIFO mati.' : keadaan === 'rencana' ? 'FIFO dijadwalkan mulai ' + tanggalPendek(mulai) + ' — sampai hari itu modal masih rata-rata.' : 'Modal FIFO sejak ' + tanggalPendek(mulai) + ': karung yang paling lama keluar duluan; wadah literan campuran tetap rata-rata.' };
}
/** aksi 'nyala' (tanggal = salah satu pilihan saklarFifo) | 'mati'. Dua ketukan (yakin). */
export function susunSaklarFifo(aksi, tanggal, w, yakin) {
  const S = saklarFifo(new Date(w.tanggal + 'T12:00:00')); const dok = cacheMentah('aturan').find((d) => String(d.id) === MF_DOK) || null;
  let mulai = '';
  if (aksi === 'nyala') { if (!S.pilihan.some((p) => p.tanggal === tanggal)) return { tolak: 'Pilih hari mulai: besok atau 1 Januari — tanggal yang sudah lewat tidak bisa (laba bulan lalu akan berubah)' };
    if (S.keadaan === 'nyala') return { tolak: 'FIFO sudah berjalan sejak ' + tanggalPendek(S.mulai) };
    mulai = tanggal; }
  else if (aksi !== 'mati' || S.keadaan === 'mati') return { tolak: 'Saklar FIFO memang sudah mati' };
  if (!yakin) return { tolak: aksi === 'nyala' ? 'Ketuk sekali lagi: mulai ' + tanggalPendek(mulai) + ' modal tiap nota = harga kedatangan TERLAMA yang masih ada; nota sebelumnya tidak berubah' : 'Ketuk sekali lagi: modal kembali ke RATA-RATA semua kedatangan; nota yang sudah tercatat dengan modal FIFO tidak berubah', perluYakin: aksi };
  const riw = (dok && Array.isArray(dok.riwayatModalFifo) ? dok.riwayatModalFifo : []).concat([{ aksi: aksi === 'nyala' ? (S.keadaan === 'rencana' ? 'ganti' : 'nyala') : 'mati', mulai, sebelumnya: S.mulai || '', tanggal: w.tanggal, jam: w.jam }]);
  const data = Object.assign({ id: MF_DOK, tanggal: w.tanggal, jam: w.jam }, dok || {}, { [MF_KOLOM]: mulai, riwayatModalFifo: riw });
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { kabar: aksi === 'nyala' ? 'Modal FIFO dijadwalkan mulai ' + tanggalPendek(mulai) + ' — semua perangkat ikut sesudah tersambung' : 'Saklar FIFO dimatikan — modal kembali rata-rata', kabarAwas: false } };
}

/** Riwayat modal satu nama, lama → baru: tiap kedatangan (baris karung) dengan harga/kg & HPP/kg (harga + bongkar), pindah buku dari takar. */
export function riwayatModal(merk) {
  const out = [];
  ambilSemuaBatch().slice().sort(hpUrutLama).forEach((k) => {
    // audit 39b no. 30: bongkar dibagi ke SEMUA baris seperti mesin (hitungStokKarungPerMerk) — porsi baris bal milik modal per bag beli-jadi; baris bal sendiri dilewati
    hitungHppMerkDalamBatch(k.merkList || [], Number(k.biayaBongkar) || 0).forEach((m) => { if (m.bentuk === 'bal' || m.merk !== merk || !(m.totalKg > 0)) return;
      out.push({ jenis: 'kedatangan', batchId: k.id, tanggal: k.tanggal || '', jam: k.jam || '', pemasok: k.pemasok || (k.stokAwal ? 'stok awal' : k.tutupBuku ? 'saldo pembuka' : '—'), fondasi: hpFondasi(k), dikoreksi: !!k.alasanKoreksi,
        hargaPerKg: Number(m.hargaPerKg) || 0, hppPerKg: m.hppPerKg, totalKg: m.totalKg, beratKarung: Number(m.beratKarung) || 50, merkPemasok: String(m.merkPemasok || ''),   // putaran 30: merek pemasok pada kedatangan kelas tanpa wadah
        sumber: (hpFondasi(k) ? (k.stokAwal ? 'stok awal (fondasi)' : 'saldo pembuka (fondasi)') : 'kedatangan ' + (k.pemasok || '')) + (m.merkPemasok ? ' · merek ' + m.merkPemasok : '') + (k.alasanKoreksi ? ' · dikoreksi' : '') }); });
  });
  ambilProduksiBerlaku().filter((p) => p.jadiKarungUtuh && p.merkTujuan === merk).sort(hpUrutLama).forEach((p) => { const kg = (p.ukuranKemasan || 0) * (p.jumlahUnit || 0); if (kg <= 0) return;
    out.push({ jenis: 'pindah', batchId: null, tanggal: p.tanggal || '', jam: p.jam || '', pemasok: '', fondasi: true, hargaPerKg: p.hppSumberPerKgDipakai || 0, hppPerKg: p.hppSumberPerKgDipakai || 0, totalKg: kg, sumber: p.dariTakar ? 'pindah buku dari takar wadah' : 'jadi karung utuh dari adukan' }); });
  return out.sort(hpUrutLama);
}
/** Σ kg masuk & Σ nilai masuk satu nama — rumus yang sama dengan hitungStokKarungPerMerk (rata-rata = nilai ÷ kg). Dijaga uji: hasilnya = mesin. */
export function totalMasuk(merk) { let kg = 0, nilai = 0; riwayatModal(merk).forEach((r) => { kg += r.totalKg; nilai += r.hppPerKg * r.totalKg; }); return { kg, nilai, rata: kg > 0 ? nilai / kg : 0 }; }
const teksMargin = (m) => (m === null ? 'harga jual per kg belum ada di katalog' : m < 0 ? 'RUGI ' + RP(-m) + '/kg' : m === 0 ? 'margin Rp0/kg (disengaja?)' : 'margin ' + RP(m) + '/kg');
const kelasMargin = (m) => (m === null ? 'tanpa' : m < 0 ? 'rugi' : m === 0 ? 'nol' : 'untung');
/** Kartu modal tiap nama beras yang bersisa (atau punya kedatangan): modal rata-rata (buku), harga beli terbaru (aturan owner, pembanding), harga jual, margin, nilai rak. */
export function kartuHpp() {
  const stok = ingatStokKarung(); const atur = aturHpp(); const uk = petaUkuran();
  // 39b no. 10: buku per ukuran ('Merek 25 kg') yang lahir dari PISAH stok tidak punya kedatangan sendiri — harga beli terbarunya = kedatangan terakhir
  // induknya (merek yang sama); tanpa pembanding sama sekali → dibanding modalnya sendiri (bukan 0: dulu kartu memajang penurunan modal palsu)
  const induk = (merk) => { const i = uk[merk] ? uk[merk].induk : ''; return i ? riwayatModal(i).filter((r) => r.jenis === 'kedatangan').slice(-1)[0] || null : null; };
  // putaran 28: buku stok wadah tidak punya kedatangan — modalnya ikut takar
  const kartu = Object.keys(stokMerekSaja(stok)).sort().map((merk) => { const st = stok[merk]; const riw = riwayatModal(merk); const akhir = riw.filter((r) => r.jenis === 'kedatangan').slice(-1)[0] || null; const bisa = riw.filter((r) => r.jenis === 'kedatangan' && !r.fondasi).slice(-1)[0] || null;
    const sisa = st.sisaKg || 0; const modal = st.hppTerakhirPerKg || 0; const modalKeluar = hppKeluarPerKg(st); const fifo = st.metode === 'fifo'; const jual = cariHargaKarungPerKg(merk); const margin = jual !== null && jual > 0 ? Math.round(jual - modalKeluar) : null; const ai = akhir ? null : induk(merk); const hppTerbaru = akhir ? akhir.hppPerKg : ai ? ai.hppPerKg : modal;
    const lonjak = riw.length > 1 && riw[riw.length - 2].hppPerKg > 0 ? Math.round((riw[riw.length - 1].hppPerKg - riw[riw.length - 2].hppPerKg) / riw[riw.length - 2].hppPerKg * 100) : 0;
    return { merk, sisa, modal, modalKeluar, fifo, teksFifo: fifo ? teksLapisan(st) : '', hargaTerbaru: akhir ? st.hargaTerakhirPerKg || 0 : ai ? ai.hargaPerKg : null, hppTerbaru, jual, margin, teksMargin: teksMargin(margin), kelasMargin: kelasMargin(margin), nilaiRak: Math.max(0, sisa) * modal, nilaiTerbaru: Math.max(0, sisa) * hppTerbaru,
      sumber: akhir ? akhir.sumber + ' · ' + akhir.tanggal : ai ? 'dipisah dari ' + uk[merk].induk + ' · harga beli terbaru induknya (' + ai.tanggal + ')' : 'belum ada kedatangan', nRiwayat: riw.length, bisaKoreksi: !!bisa, targetId: bisa ? bisa.batchId : null, bedaTerbaru: hppTerbaru - modal, lonjakTerakhir: Math.abs(lonjak) > atur.batasLonjak ? lonjak : 0, adaStok: sisa > 0.05 }; })
    .filter((k) => k.adaStok || k.nRiwayat);
  const berisi = kartu.filter((k) => k.adaStok);
  return { kartu, atur, ringkas: { nilai: berisi.reduce((a, k) => a + k.nilaiRak, 0), nilaiTerbaru: berisi.reduce((a, k) => a + k.nilaiTerbaru, 0), rugi: berisi.filter((k) => k.margin !== null && k.margin < 0).length, nol: berisi.filter((k) => k.margin === 0).length, tanpaJual: berisi.filter((k) => k.margin === null).length, n: berisi.length },
    ringkasTeks: 'Nilai rak (' + (berisi.some((k) => k.fifo) ? 'FIFO: sisa = kedatangan terbaru' : 'modal rata-rata') + ', = Neraca) ' + RP(Math.round(berisi.reduce((a, k) => a + k.nilaiRak, 0))) + ' · bila dinilai harga beli terbaru ' + RP(Math.round(berisi.reduce((a, k) => a + k.nilaiTerbaru, 0))) + ' · ' + (berisi.filter((k) => k.margin !== null && k.margin < 0).length ? berisi.filter((k) => k.margin !== null && k.margin < 0).length + ' nama RUGI' : 'tidak ada yang rugi') + (berisi.filter((k) => k.margin === 0).length ? ' · ' + berisi.filter((k) => k.margin === 0).length + ' margin nol' : '') };
}
/** Garis waktu HPP semua nama (bar relatif ke tertinggi), lonjakan > batas ditandai, koreksi diwarnai. */
export function garisWaktu() {
  const atur = aturHpp(); const stok = ingatStokKarung();
  return Object.keys(stokMerekSaja(stok)).sort().map((merk) => { const r = riwayatModal(merk); if (!r.length) return null; const maks = Math.max(...r.map((x) => x.hppPerKg), 1);
    return { merk, ket: r.length + ' catatan · modal rata-rata sekarang ' + RP(Math.round(stok[merk].hppTerakhirPerKg || 0)) + '/kg · terbaru ' + RP(Math.round(r[r.length - 1].hppPerKg)) + '/kg',
      baris: r.map((x, i) => { const lalu = i > 0 ? r[i - 1].hppPerKg : 0; const p = lalu > 0 ? Math.round((x.hppPerKg - lalu) / lalu * 100) : 0;
        return { tanggal: x.tanggal, lebar: Math.round(x.hppPerKg / maks * 1000) / 10, koreksi: x.dikoreksi, hpp: Math.round(x.hppPerKg), harga: Math.round(x.hargaPerKg), kg: x.totalKg, sumber: x.sumber, lonjak: i > 0 && Math.abs(p) > atur.batasLonjak ? (p > 0 ? '▲' : '▼') + Math.abs(p) + ' %' : '' }; }) }; }).filter(Boolean);
}
/** Nilai satu angka koreksi (harga beli per kg kedatangan terakhir nama itu): ditolak / lonjakan / rugi / Δ nilai rak — TANPA menulis apa pun. */
export function nilaiKoreksi(merk, hargaBaru) {
  const atur = aturHpp(); const K = kartuHpp().kartu.find((k) => k.merk === merk); if (!K) return { tolak: 'Nama beras itu tidak ada di buku' };
  const riw = riwayatModal(merk); const target = riw.filter((r) => r.jenis === 'kedatangan' && !r.fondasi).slice(-1)[0] || null;
  if (!target) return { tolak: merk + ' belum punya kedatangan yang bisa dikoreksi — modalnya dari stok awal / saldo pembuka (fondasi), tidak diubah dari sini' };
  const kunci = tolakKunciTanggal(target.tanggal, 'harga modal kedatangan bulan terkunci tidak bisa dikoreksi; selisihnya terbawa ke HPP penjualan sisa stoknya (keputusan owner K2)'); if (kunci) return { tolak: kunci };   // putaran 25
  const n = Math.round(hpAngka(hargaBaru)); if (!(n > 0)) return { tolak: 'Ketik harga beli per kg yang benar' };
  if (n < atur.lantaiHpp) return { tolak: RP(n) + '/kg di bawah lantai ' + RP(atur.lantaiHpp) + ' — tidak masuk akal untuk beras, ditolak (bukan dipotong diam-diam)' };
  if (K.modal > 0 && n > K.modal * atur.kaliMaks) return { tolak: RP(n) + ' lebih dari ' + atur.kaliMaks + '× modal sekarang (' + RP(Math.round(K.modal)) + ') — ditolak, cek angkanya' };
  // audit 39b no. 2 (tinjauan 30 Sep): kedatangan sasaran bon yang sudah dibayar — nilai bon sesudah harga baru tidak boleh di bawah yang dibayar.
  // Diperiksa DI SINI supaya kartu, pratinjau, dan koreksi massal menolak lebih dulu dengan nama berasnya (susunSimpanMasuk tetap pagar terakhir).
  const bt = ambilSemuaBatch().find((b) => String(b.id) === String(target.batchId)); const bb = bt ? ckBayarBonId(bt.id) : null;
  if (bb && bb.dibayar > 0) { const nilaiBon = (bt.merkList || []).reduce((a, m) => a + (m.bentuk === 'bal' ? (Number(m.subtotalHarga) || 0) : m.merk === merk ? (Number(m.totalKg) || 0) * n : (Number(m.subtotalHarga) || 0)), 0);   // baris bal ikut tertulis apa adanya, harganya tidak dikoreksi (audit 39b no. 30)
    if (nilaiBon + 0.5 < bb.dibayar) return { tolak: merk + ': kedatangan terakhirnya (' + target.pemasok + ' ' + target.tanggal + ') bon yang sudah dibayar ' + RP(bb.dibayar) + ' — harga ' + RP(n) + '/kg membuat nilai bonnya ' + RP(nilaiBon) + ', di bawah yang dibayar; kelebihannya akan pindah ke bon lain tanpa uang' }; }
  const bongkarPerKg = target.hppPerKg - target.hargaPerKg; const hppBaru = n + bongkarPerKg;
  const T = totalMasuk(merk); const nilaiBaru = T.nilai - target.hppPerKg * target.totalKg + hppBaru * target.totalKg; let modalBaru = T.kg > 0 ? nilaiBaru / T.kg : 0;
  // modal FIFO (owner 9 Okt): nilai rak sesudah koreksi dihitung MESIN atas kedatangan yang sudah dibetulkan (cache sementara) — lapisan yang sudah keluar
  // tidak ikut naik/turun. Saklar mati = rumus rata-rata di atas.
  if (K.fifo && bt) { const bt2 = Object.assign({}, bt, { merkList: (bt.merkList || []).map((m) => (m.bentuk !== 'bal' && m.merk === merk ? Object.assign({}, m, { hargaPerKg: n, subtotalHarga: Math.round((Number(m.totalKg) || 0) * n) }) : m)) });
    const st1 = denganCacheSementara([{ koleksi: 'batchMasuk', data: bt2 }], () => hitungStokKarungPerMerk()[merk]); modalBaru = st1 ? st1.hppTerakhirPerKg || 0 : modalBaru; }
  const pct = K.modal > 0 ? Math.round((modalBaru - K.modal) / K.modal * 100) : 0; const delta = (modalBaru - K.modal) * Math.max(0, K.sisa);
  return { tolak: '', merk, n, target, hppBaru, modalLama: K.modal, modalBaru, delta, sisa: K.sisa, sama: n === target.hargaPerKg,
    lonjak: Math.abs(pct) > atur.batasLonjak ? (K.fifo ? 'nilai rak per kg ' : 'modal rata-rata ') + (pct > 0 ? 'naik ' : 'turun ') + Math.abs(pct) + ' % (' + RP(Math.round(K.modal)) + ' → ' + RP(Math.round(modalBaru)) + ')' : '',
    rugi: K.jual !== null && K.jual > 0 ? (hppBaru > K.jual ? 'HPP kedatangan ini ' + RP(Math.round(hppBaru)) + ' di atas harga jual ' + RP(K.jual) + '/kg — tiap kg dijual RUGI ' + RP(Math.round(hppBaru - K.jual)) : Math.round(hppBaru) === K.jual ? 'sama dengan harga jual — margin Rp0 (disengaja?)' : '') : '',
    teksTarget: 'kedatangan ' + target.pemasok + ' ' + target.tanggal + ' · ' + hpKG(target.totalKg) + ' · harga ' + RP(target.hargaPerKg) + '/kg' + (bongkarPerKg ? ' + bongkar ' + RP(Math.round(bongkarPerKg)) + '/kg' : ''),
    teksDelta: 'Nilai rak ' + merk + ' ' + (delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(delta))) + ' (' + RP(Math.round(modalBaru - K.modal)) + '/kg × ' + hpKG(Math.max(0, K.sisa)) + ') — kekayaan toko ikut ' + (delta >= 0 ? 'naik' : 'turun') };
}
function hpDrafUntuk(peta, w) {
  // kelompokkan koreksi per batch: dua nama di kedatangan yang sama → SATU dokumen; baris nama itu (semua beratnya) diberi harga baru
  const perBatch = {}; Object.keys(peta).forEach((merk) => { const v = peta[merk]; if (!perBatch[v.target.batchId]) perBatch[v.target.batchId] = {}; perBatch[v.target.batchId][merk] = v.n; });
  const hasil = [];
  Object.keys(perBatch).forEach((id) => { const d = drafDariKedatangan(id); if (!d) { hasil.push({ tolak: 'Kedatangan ' + id + ' sudah tidak ada' }); return; }
    d.baris.forEach((b) => { if (perBatch[id][b.merk] !== undefined) b.hargaPerKg = String(perBatch[id][b.merk]); }); d.alasan = 'koreksi HPP: ' + w.alasan;
    hasil.push(susunSimpanMasuk(d, w, true)); });
  return hasil;
}
/** Koreksi satu nama. yakin = sudah ditanya soal lonjakan. */
export function susunKoreksiHpp(merk, hargaBaru, alasan, w, yakin) {
  const v = nilaiKoreksi(merk, hargaBaru); if (v.tolak) return { tolak: v.tolak };
  if (v.sama) return { tolak: 'Harga yang diketik sama dengan yang tercatat (' + RP(v.n) + '/kg) — tidak ada yang dikoreksi' };
  if (hpKosong(alasan)) return { tolak: 'Koreksi HPP butuh alasan (mis. bongkar belum masuk, salah ketik harga)' };
  if (v.lonjak && !yakin) return { tolak: 'HPP: ' + v.lonjak + ' — ketuk sekali lagi kalau memang benar', perluYakin: true };
  const peta = {}; peta[merk] = v; const r = hpDrafUntuk(peta, { tanggal: w.tanggal, jam: w.jam, idUnik: w.idUnik, alasan: String(alasan).trim() })[0]; if (r.tolak) return { tolak: r.tolak };
  const log = { koleksi: 'koreksiHpp', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk, batchId: String(v.target.batchId), hargaDari: v.target.hargaPerKg, hargaKe: v.n, modalDari: Math.round(v.modalLama * 100) / 100, modalKe: Math.round(v.modalBaru * 100) / 100, sisaKg: Math.round(v.sisa * 100) / 100, deltaNilai: Math.round(v.delta), alasan: String(alasan).trim() } };
  return { dokumen: r.dokumen.concat([log]), nilai: v, patch: { hp: { merk, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'kartu' }, kabar: merk + ': harga kedatangan ' + v.target.tanggal + ' ' + RP(v.target.hargaPerKg) + ' → ' + RP(v.n) + '/kg (' + String(alasan).trim() + '). Modal rata-rata ' + RP(Math.round(v.modalLama)) + ' → ' + RP(Math.round(v.modalBaru)) + '/kg; nilai rak ' + (v.delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(v.delta))) + '.', kabarAwas: false } };
}
/**
 * audit 39b no. 2 (tinjauan 30 Sep): beberapa nama yang kedatangan sasarannya SAMA dinilai BERSAMA — satu kedatangan = satu bon; lolos per nama belum
 * tentu lolos bersama. nilai = {merk: hasil nilaiKoreksi yang lolos}. Hasil {merk: kalimat tolak} untuk nama yang bonnya jatuh di bawah yang dibayar.
 */
function hpKunciBonGabung(nilai) {
  const per = {}; Object.keys(nilai).forEach((m) => { const id = String(nilai[m].target.batchId); (per[id] = per[id] || []).push(m); });
  const salah = {};
  Object.keys(per).forEach((id) => { const ms = per[id]; if (ms.length < 2) return; const bt = ambilSemuaBatch().find((b) => String(b.id) === id); const bb = bt ? ckBayarBonId(id) : null; if (!bb || !bb.dibayar) return;
    const nilaiBon = (bt.merkList || []).reduce((a, x) => a + (x.bentuk === 'bal' ? (Number(x.subtotalHarga) || 0) : ms.indexOf(x.merk) >= 0 ? (Number(x.totalKg) || 0) * nilai[x.merk].n : (Number(x.subtotalHarga) || 0)), 0);   // baris bal ikut tertulis apa adanya, harganya tidak dikoreksi (audit 39b no. 30)
    if (nilaiBon + 0.5 >= bb.dibayar) return; const tg = nilai[ms[0]].target;
    const t = ms.join(' + ') + ': kedatangan terakhirnya sama (' + tg.pemasok + ' ' + tg.tanggal + '), bon yang sudah dibayar ' + RP(bb.dibayar) + ' — harga baru BERSAMA membuat nilai bonnya ' + RP(nilaiBon) + ', di bawah yang dibayar; kelebihannya akan pindah ke bon lain tanpa uang';
    ms.forEach((m) => { salah[m] = t; }); });
  return salah;
}
/** Koreksi massal: peta {merk: harga}; SEMUA-ATAU-TIDAK — satu angka ditolak = tidak ada yang ditulis. Satu alasan. */
export function susunKoreksiMassal(petaHarga, alasan, w) {
  const merk = Object.keys(petaHarga || {}).filter((m) => !hpKosong(petaHarga[m]));
  if (!merk.length) return { tolak: 'Belum ada nama yang disiapkan' };
  const nilai = {}; const salah = [];
  merk.forEach((m) => { const v = nilaiKoreksi(m, petaHarga[m]); if (v.tolak) salah.push(v.tolak.indexOf(m + ':') === 0 ? v.tolak : m + ': ' + v.tolak); else if (v.sama) salah.push(m + ': sama dengan yang tercatat'); else nilai[m] = v; });
  if (!salah.length) { const gb = hpKunciBonGabung(nilai); const kal = []; Object.keys(gb).forEach((m) => { if (kal.indexOf(gb[m]) < 0) kal.push(gb[m]); }); kal.forEach((k) => salah.push(k)); }
  if (salah.length) return { tolak: salah.join(' · ') + ' — TIDAK ADA yang disimpan sampai semuanya beres', salah };
  if (hpKosong(alasan)) return { tolak: 'Koreksi massal butuh satu alasan untuk semua' };
  const hasil = hpDrafUntuk(nilai, { tanggal: w.tanggal, jam: w.jam, idUnik: w.idUnik, alasan: String(alasan).trim() }); const gagal = hasil.find((r) => r.tolak); if (gagal) return { tolak: gagal.tolak };
  const delta = Object.keys(nilai).reduce((a, m) => a + nilai[m].delta, 0);
  const dokumen = []; hasil.forEach((r) => r.dokumen.forEach((d) => dokumen.push(d)));
  Object.keys(nilai).forEach((m) => { const v = nilai[m]; dokumen.push({ koleksi: 'koreksiHpp', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: m, batchId: String(v.target.batchId), hargaDari: v.target.hargaPerKg, hargaKe: v.n, modalDari: Math.round(v.modalLama * 100) / 100, modalKe: Math.round(v.modalBaru * 100) / 100, sisaKg: Math.round(v.sisa * 100) / 100, deltaNilai: Math.round(v.delta), alasan: String(alasan).trim(), massal: merk.length } }); });
  return { dokumen, delta, n: merk.length, patch: { hp: { merk: null, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'massal' }, kabar: merk.length + ' nama dikoreksi sekaligus (' + String(alasan).trim() + ') — nilai rak ' + (delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(delta))) + '. Semuanya masuk atau tidak sama sekali.', kabarAwas: false } };
}
/** Pratinjau massal untuk layar: tiap nama yang disiapkan dinilai; label tombol & Δ total. */
export function pratinjauMassal(petaHarga) {
  const merk = Object.keys(petaHarga || {}).filter((m) => !hpKosong(petaHarga[m])); const baris = merk.map((m) => { const v = nilaiKoreksi(m, petaHarga[m]); const tk = v.tolak && v.tolak.indexOf(m + ': ') === 0 ? v.tolak.slice(m.length + 2) : v.tolak;   // baris pratinjau sudah berlabel nama berasnya
    return { merk: m, harga: Math.round(hpAngka(petaHarga[m])), tolak: tk || (v.sama ? 'sama dengan yang tercatat' : ''), ket: tk || (v.sama ? 'sama dengan yang tercatat' : v.rugi || v.lonjak || 'wajar'), delta: v.tolak ? 0 : v.delta, v: v.tolak || v.sama ? null : v }; });
  const lolos = {}; baris.forEach((b) => { if (!b.tolak && b.v) lolos[b.merk] = b.v; }); const gb = hpKunciBonGabung(lolos); baris.forEach((b) => { if (gb[b.merk]) { b.tolak = gb[b.merk]; b.ket = gb[b.merk]; b.delta = 0; } });   // audit 39b no. 2: nama sekedatangan dinilai bersama
  const bermasalah = baris.filter((b) => b.tolak); const delta = baris.reduce((a, b) => a + b.delta, 0);
  return { baris, n: merk.length, bermasalah, delta, siap: merk.length > 0 && !bermasalah.length,
    teks: !merk.length ? 'Ketuk nama, ketik harga beli/kg baru, "siapkan" — lalu terapkan sekaligus' : bermasalah.length ? bermasalah.map((b) => b.merk).join(', ') + ' angkanya ditolak — TIDAK ADA yang disimpan sampai semuanya beres' : 'Disiapkan ' + merk.length + ' nama · nilai rak berubah ' + (delta >= 0 ? '+' : '−') + RP(Math.round(Math.abs(delta))) };
}
export function logKoreksi(n) { return cacheMentah('koreksiHpp').slice().sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 10); }
