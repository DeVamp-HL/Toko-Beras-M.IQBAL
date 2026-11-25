// TITIPAN UANG KELUAR & PESAN UNTUK OWNER dari tablet (owner 21 Nov 2026). Logika tanpa DOM; awalan tp.
// Owner: "karyawan mencatat uang keluar + catatan untuk owner di tablet (siap kirim & cetak, owner mengoreksi)". Keputusan 21 Nov:
//  1. MENUNGGU OWNER. Orang yang jaga tablet menulis TITIPAN ke koleksi persetujuan (tindakan 'uangKeluar', status 'menunggu'). Laci di buku BELUM
//     berkurang. Owner menyetujui dari HP/Mac (boleh membetulkan nominal, keterangan, jenis, nama) → dokumen uangnya ditulis di kiriman yang sama;
//     atau menolak dengan alasan. Akun tablet tidak pernah menulis dokumen uang (rules v13 hanya membuka bentuk "menunggu" ini).
//  2. TIGA JENIS: belanja toko (pengeluaranHarian kategori toko, untuk 'toko') · untuk karyawan (rokok/makan/kopi — kategori toko, untuk 'karyawan',
//     bagian upah yang dibebankan ke pengeluaran harian) · kasbon karyawan (kasbonMutasi tipe 'ambil' atas nama orangnya). Semuanya dari LACI.
//  3. TANGGAL UANG = tanggal & jam TITIPAN, bukan tanggal disetujui: uangnya keluar dari laci saat itu. Titik kas per tanggal (kasPada) membuat ini
//     benar dua-duanya: disetujui sebelum tutup hari → ikut buku hari itu; sesudah tutup hari → hitungan fisik laci sudah memuatnya, kas tidak
//     dikurangi dua kali, laba tetap memuat biayanya. Tutup hari menyebut titipan yang masih menunggu supaya selisih laci terbaca sebabnya.
//  4. PESAN: tulisan bebas atas nama orang yang jaga (tindakan 'pesan'). Owner menandai "dibaca" dan boleh membalas singkat; balasannya terbaca di
//     tablet. Pesan bukan uang dan tidak pernah ikut "setujui semua yang kecil".
//  5. SATU PINTU memutus: Uang › titipan dan papan Persetujuan (Menu) sama-sama lewat tpSusunPutus — dulu papan Persetujuan menandai titipan uang
//     "disetujui" TANPA menulis uangnya (cacat terpendam, belum pernah terjadi karena server belum membuka titipan dari tablet).
//  6. BARANG MASUK (owner 22 Nov 2026, rules v15): dua jenis titipan lagi — UPAH BONGKAR (menunjuk kedatangannya; disetujui = upah bongkar ditulis ke
//     kedatangan itu, jadi modal barang & kas keluar laci bertanggal datangnya, sama seperti owner mencatatnya sendiri) dan BAYAR BON PEMASOK lewat supir
//     (tablet cukup nominal + pemasok; owner MEMILIH bonnya saat menyetujui, bawaan = bon kedatangan titipan itu bila masih terbuka). Plus KABAR barang
//     masuk (tindakan 'barangMasuk'): bukan uang, owner menandainya "sudah diperiksa" — seperti pesan.
import { cacheMentah, ambilPengeluaranHarian, ambilKasbonMutasi, ambilSemuaBatch, ambilUtangPemasokMutasi, tolakKunci, tolakKunciTanggal } from '../data/toko.js';
import { kunciPelanggan } from '../mesin/pembantu.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { hitungBayar } from './bon-pemasok-logika.js';

export const TP_TINDAKAN = 'uangKeluar';
export const TP_PESAN = 'pesan';
export const TP_KABAR = 'barangMasuk';
/** Jenis yang dipilih di kartu tablet. Upah bongkar TIDAK di sini: ia lahir dari form barang masuk (selalu menunjuk kedatangannya). */
export const TP_JENIS = [['toko', 'Belanja toko'], ['karyawan', 'Untuk karyawan'], ['kasbon', 'Kasbon karyawan'], ['bayarBon', 'Bayar bon pemasok']];
export const TP_JENIS_SEMUA = TP_JENIS.concat([['bongkar', 'Upah bongkar']]);
export const TP_STATUS = { menunggu: 'menunggu owner', disetujui: 'disetujui', ditolak: 'ditolak', dibaca: 'dibaca owner' };
export const TP_BATAS = { teks: 80, nama: 40, pesan: 500, balasan: 200, alasan: 80 };
const KOSONG = (v) => v === undefined || v === null || String(v).trim() === '';
const tpPotong = (v, n) => String(v === undefined || v === null ? '' : v).trim().slice(0, n);
/** Teks rupiah yang diketik → bilangan bulat (titik ribuan & "Rp" boleh). Bukan angka / pecahan → NaN. */
export function tpAngka(v) {
  const t = String(v === undefined || v === null ? '' : v).replace(/rp/i, '').replace(/\s/g, '').replace(/\./g, '');
  if (!/^\d+$/.test(t)) return NaN;
  return Number(t);
}
export const tpNamaJenis = (j) => (TP_JENIS_SEMUA.find((x) => x[0] === j) || [j, j])[1];
const sah = (j) => TP_JENIS_SEMUA.some((x) => x[0] === j);
/** Jenis titipan; titipan lama tanpa kolom jenis (bentuk sebelum 21 Nov 2026) = belanja toko. */
export const tpJenis = (m) => (m && m.jenis ? String(m.jenis) : 'toko');
const tpPemasokTitip = (m) => tpPotong(m && m.pemasok, 60);

/** Kalimat satu titipan untuk layar & cetak: "Belanja toko · kantong 5 kg · Rp50.000" / "Kasbon karyawan · Hasan · Rp100.000". */
export function tpTeks(m) {
  const b = [tpJenis(m) === 'bongkar' && m.ongkir === true ? 'Ongkos kirim' : tpNamaJenis(tpJenis(m))];
  if (tpJenis(m) === 'kasbon' && m.namaPegawai) b.push(m.namaPegawai);
  if ((tpJenis(m) === 'bayarBon' || tpJenis(m) === 'bongkar') && tpPemasokTitip(m) && String(m.teks || '').indexOf(tpPemasokTitip(m)) < 0) b.push(tpPemasokTitip(m));
  if (m.teks) b.push(m.teks);
  if (tpJenis(m) === 'karyawan' && m.namaPegawai) b.push('untuk ' + m.namaPegawai);
  b.push(RP(Number(m.nominal) || 0));
  return b.join(' · ');
}

// ---------- tablet: menulis titipan & pesan ----------
const milik = (m, akun) => !!akun && String(m.mintaUid || '') === String(akun.uid || '');
/**
 * Titipan uang keluar dari tablet. draf = { jenis, nominal (teks), teks, nama }; akun = orang yang jaga (uid akun tablet).
 * Hasil { dokumen, patch } atau { tolak }. Bentuk = rules v13 stafMintaKeluar: status 'menunggu', mintaUid = penulis, jenis sah, nominal bulat > 0,
 * tanpa kolom keputusan.
 */
export function tpSusunMinta(draf, akun, w) {
  const d = draf || {}; const jenis = String(d.jenis || ''); const n = tpAngka(d.nominal); const nama = tpPotong(d.nama, TP_BATAS.nama); const pemasok = tpPotong(d.pemasok, 60);
  const teks = tpPotong(d.teks, TP_BATAS.teks) || (jenis === 'bayarBon' ? 'Bayar lewat supir' : '');
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — titipan butuh orang yang jaga' };
  if (jenis === 'bongkar' && !String(d.batchId || '')) return { tolak: 'Upah bongkar dicatat lewat Stok › Barang masuk (ikut kedatangannya)' };
  if (!sah(jenis)) return { tolak: 'Pilih jenisnya dulu: belanja toko, untuk karyawan, kasbon, atau bayar bon pemasok' };
  if (!(n > 0)) return { tolak: KOSONG(d.nominal) ? 'Isi nominalnya dulu' : 'Nominal hanya angka rupiah bulat (mis. 50000 atau 50.000)' };
  if (jenis === 'kasbon' && !nama) return { tolak: 'Kasbon untuk siapa? Pilih namanya dulu' };
  if (jenis === 'bayarBon' && !pemasok) return { tolak: 'Bayar bon pemasok mana? Pilih atau ketik nama pemasoknya' };
  if (jenis !== 'kasbon' && !teks) return { tolak: 'Tulis untuk apa uangnya (mis. kantong 5 kg, bensin, makan siang)' };
  const ada = cacheMentah('persetujuan').find((m) => m.tindakan === TP_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && milik(m, akun) && m.jenis === jenis && Number(m.nominal) === n
    && String(m.teks || '') === teks && String(m.namaPegawai || '') === nama && String(m.pemasok || '') === pemasok && String(m.batchId || '') === String(d.batchId || ''));
  if (ada) return { tolak: 'Titipan yang sama (' + tpTeks(ada) + ', jam ' + (ada.jam || '?') + ') masih menunggu owner — tidak dikirim dua kali' };
  const data = { id: w.idUnik(), tindakan: TP_TINDAKAN, status: 'menunggu', jenis, nominal: n, teks, dariTempat: 'laci', mintaUid: String(akun.uid),
    dari: String(akun.nama || ''), peran: String(akun.peran || ''), tanggal: w.tanggal, jam: w.jam, pada: w.kini };
  if (nama && (jenis === 'kasbon' || jenis === 'karyawan')) data.namaPegawai = nama;
  if (pemasok && (jenis === 'bayarBon' || jenis === 'bongkar')) data.pemasok = pemasok;
  if (d.batchId && (jenis === 'bayarBon' || jenis === 'bongkar')) data.batchId = String(d.batchId);
  // Tahap 3 (owner 26 Nov 2026): ONGKOS KIRIM supir pemasok dari tablet = titipan berjenis 'bongkar' (bentuk rules v15, wajib kedatangannya) bertanda ongkir —
  // disetujui owner = masuk modal kedatangan itu sebagai ongkos kirim (biayaBongkar + ongkosKirim), bukan upah bongkar
  if (d.ongkir && jenis === 'bongkar') data.ongkir = true;
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Titipan terkirim ke owner — ' + tpTeks(data) + '. Laci di buku belum berkurang sampai owner menyetujui.', kabarAwas: false } };
}
/** Kabar barang masuk untuk owner (rules v15 stafKabarMasuk): bukan uang — owner menandainya "sudah diperiksa". isi = { batchId, teks, nominal, hargaBeda }. */
export function tpDokKabarMasuk(isi, akun, w) {
  const o = isi || {};
  const data = { id: w.idUnik(), tindakan: TP_KABAR, status: 'menunggu', batchId: String(o.batchId || ''), teks: tpPotong(o.teks, TP_BATAS.pesan), nominal: Math.round(Number(o.nominal) || 0),
    mintaUid: String(akun.uid), dari: String(akun.nama || ''), peran: String(akun.peran || ''), tanggal: w.tanggal, jam: w.jam, pada: w.kini };
  if (o.pemasok) data.pemasok = tpPotong(o.pemasok, 60);
  if (Array.isArray(o.hargaBeda) && o.hargaBeda.length) data.hargaBeda = o.hargaBeda.slice(0, 20);
  return { koleksi: 'persetujuan', data };
}
/** Pesan untuk owner (tulisan bebas, bukan uang). Bentuk = rules v13 stafKirimPesan. */
export function tpSusunPesan(teks, akun, w) {
  const t = String(teks === undefined || teks === null ? '' : teks).replace(/\r/g, '').trim();
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — pesan butuh orang yang jaga' };
  if (!t) return { tolak: 'Tulis pesannya dulu' };
  if (t.length > TP_BATAS.pesan) return { tolak: 'Pesan paling panjang ' + TP_BATAS.pesan + ' huruf (sekarang ' + t.length + ') — pecah jadi dua pesan' };
  const data = { id: w.idUnik(), tindakan: TP_PESAN, status: 'menunggu', teks: t, mintaUid: String(akun.uid), dari: String(akun.nama || ''), peran: String(akun.peran || ''),
    tanggal: w.tanggal, jam: w.jam, pada: w.kini };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Pesan terkirim ke owner', kabarAwas: false } };
}
/** Titipan & pesan dari akun ini: yang masih menunggu (semua) + yang sudah diputus dalam `hari` hari terakhir, terbaru di atas. */
export function tpMilikSaya(akun, kiniIso, hari) {
  const batas = tpMundur(kiniIso, hari === undefined ? 7 : hari);
  return cacheMentah('persetujuan').filter((m) => (m.tindakan === TP_TINDAKAN || m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) && milik(m, akun)
    && ((m.status || 'menunggu') === 'menunggu' || String(m.tanggal || '') >= batas)).sort(urutTerbaru).map(tpBaris);
}
function tpMundur(iso, hari) {
  const t = new Date(String(iso || '').slice(0, 10) + 'T00:00:00Z'); if (!isFinite(t.getTime())) return '';
  t.setUTCDate(t.getUTCDate() - hari); return t.toISOString().slice(0, 10);
}
const urutTerbaru = (a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || ''));
/** Satu baris tampilan (tablet & owner). */
export function tpBaris(m) {
  // kabar barang masuk diperlakukan seperti pesan (bukan uang; owner menandainya diperiksa) — kabar: true membedakannya di layar
  const kabar = m.tindakan === TP_KABAR; const pesan = m.tindakan === TP_PESAN || kabar; const st = m.status || 'menunggu';
  return { id: String(m.id), pesan, kabar, jenis: pesan ? '' : tpJenis(m), namaJenis: kabar ? 'Kabar barang masuk' : pesan ? 'Pesan' : tpNamaJenis(tpJenis(m)), nominal: pesan ? 0 : Math.round(Number(m.nominal) || 0),
    pemasok: tpPemasokTitip(m), batchId: String(m.batchId || ''), bonId: String(m.bonId || ''), hargaBeda: kabar && Array.isArray(m.hargaBeda) ? m.hargaBeda : [],
    teks: String(m.teks || ''), nama: String(m.namaPegawai || ''), dari: String(m.dari || '?'), tanggal: String(m.tanggal || ''), jam: String(m.jam || ''), status: st, namaStatus: TP_STATUS[st] || st,
    alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || ''), diputus: m.diputusTanggal ? tanggalPendek(m.diputusTanggal) + (m.diputusJam ? ' ' + m.diputusJam : '') : '',
    dikoreksi: !!m.koreksiOwner, asli: m.koreksiOwner ? { nominal: Number(m.nominalAsli) || 0, teks: String(m.teksAsli || ''), jenis: String(m.jenisAsli || ''), nama: String(m.namaAsli || '') } : null,
    ringkas: pesan ? String(m.teks || '') : tpTeks(m) };
}

// ---------- owner: memutus ----------
/** Titipan uang & pesan yang menunggu owner (Uang & papan Persetujuan), terbaru di atas. */
export function tpMenunggu() {
  return cacheMentah('persetujuan').filter((m) => (m.tindakan === TP_TINDAKAN || m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) && (m.status || 'menunggu') === 'menunggu').sort(urutTerbaru).map(tpBaris);
}
const samaPemasok = (a, b) => !!String(a || '').trim() && kunciPelanggan(a) === kunciPelanggan(b);
/**
 * Bon yang bisa dibayar titipan "bayar bon pemasok" ini (owner memilih saat menyetujui): bon pemasok itu yang masih bersisa, tertua dulu; bawaan = bon
 * kedatangan titipan itu (batchId) bila masih bersisa, selain itu bon tertua. → { bon: [{ id, tanggal, sisa, nilai, isi }], bawaan: id | '' }.
 */
export function tpBonPilihan(id, kini) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id)); if (!m) return { bon: [], bawaan: '' };
  const H = hitungBayar({ pemasok: '' }, kini || new Date());
  const bon = H.B.bon.filter((b) => samaPemasok(b.pemasok, m.pemasok) && b.sisa > 0).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)))
    .map((b) => ({ id: b.id, pemasok: b.pemasok, tanggal: b.tanggal, sisa: b.sisa, nilai: b.nilai, isi: b.isi || '' }));
  const sendiri = bon.find((b) => String(b.id) === String(m.batchId || ''));
  return { bon, bawaan: sendiri ? sendiri.id : bon.length ? bon[0].id : '' };
}
/** Jumlah rupiah titipan uang yang menunggu, tanggal ≤ iso (tutup hari: laci fisik sudah berkurang, buku belum). */
export function tpMenungguSampai(iso) {
  const x = cacheMentah('persetujuan').filter((m) => m.tindakan === TP_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && (!iso || String(m.tanggal || '') <= iso));
  return { n: x.length, rp: x.reduce((a, m) => a + Math.round(Number(m.nominal) || 0), 0), kalimat: x.length ? x.length + ' titipan uang keluar dari tablet masih menunggu persetujuan (' + RP(x.reduce((a, m) => a + Math.round(Number(m.nominal) || 0), 0)) + ') — uangnya sudah keluar dari laci, buku belum. Putus dulu di Uang › Uang keluar supaya laci tidak tampak kurang.' : '' };
}
/** Uang yang sudah ditulis untuk titipan ini (penjaga dobel): pengeluaranHarian / kasbonMutasi / bayar bon ber-dariPersetujuan = id, upah bongkar di kedatangan. */
const sudahDitulis = (id) => ambilPengeluaranHarian().some((h) => String(h.dariPersetujuan || '') === String(id)) || ambilKasbonMutasi().some((k) => String(k.dariPersetujuan || '') === String(id))
  || ambilUtangPemasokMutasi().some((u) => String(u.dariPersetujuan || '') === String(id)) || ambilSemuaBatch().some((b) => Array.isArray(b.bongkarTitipan) && b.bongkarTitipan.indexOf(String(id)) >= 0);
/**
 * Putus satu titipan / pesan. keputusan: 'setuju' | 'tolak' | 'dibaca' (pesan). isi = { nominal, teks, jenis, nama } (setuju — betulan owner; kosong = apa
 * adanya) · { alasan } (tolak) · { balasan } (dibaca, boleh kosong). Hasil { dokumen, patch } atau { tolak }.
 */
export function tpSusunPutus(id, keputusan, isi, w) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id)); const o = isi || {};
  if (!m || (m.tindakan !== TP_TINDAKAN && m.tindakan !== TP_PESAN && m.tindakan !== TP_KABAR)) return { tolak: 'Titipan atau pesannya tidak ditemukan' };
  if (m.status && m.status !== 'menunggu') return { tolak: 'Sudah diputus ' + (m.diputusTanggal ? tanggalPendek(m.diputusTanggal) + ' ' + (m.diputusJam || '') : '') };
  const putus = { diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini };
  const siapa = m.dari || 'tablet';
  if (m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) {
    const kabar = m.tindakan === TP_KABAR;
    if (keputusan !== 'dibaca') return { tolak: kabar ? 'Kabar barang masuk hanya ditandai sudah diperiksa (boleh dengan balasan)' : 'Pesan hanya ditandai dibaca (boleh dengan balasan)' };
    const balas = tpPotong(o.balasan, TP_BATAS.balasan);
    return { dokumen: [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: 'dibaca', balasan: balas }, putus) }],
      patch: { kabar: (kabar ? 'Kabar barang masuk ' + siapa + ' ditandai sudah diperiksa' : 'Pesan ' + siapa + ' ditandai dibaca') + (balas ? ' — balasan terbaca di tablet' : ''), kabarAwas: false } };
  }
  if (keputusan === 'tolak') {
    const alasan = tpPotong(o.alasan, TP_BATAS.alasan); if (!alasan) return { tolak: 'Menolak butuh alasan — supaya ' + siapa + ' tahu sebabnya' };
    return { dokumen: [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: 'ditolak', alasanTolak: alasan }, putus) }],
      patch: { kabar: 'Titipan ' + siapa + ' ditolak (' + alasan + ') — uang toko tidak berubah; kalau uangnya memang sudah keluar dari laci, laci akan tampak kurang sebesar ' + RP(Number(m.nominal) || 0) + ' saat tutup hari', kabarAwas: false } };
  }
  if (keputusan !== 'setuju') return { tolak: 'Keputusan tidak dikenal' };
  // betulan owner: yang diketik menimpa, yang kosong = apa adanya
  const jenis = KOSONG(o.jenis) ? tpJenis(m) : String(o.jenis); const n = KOSONG(o.nominal) ? Math.round(Number(m.nominal) || 0) : tpAngka(o.nominal);
  const teks = KOSONG(o.teks) ? tpPotong(m.teks, TP_BATAS.teks) : tpPotong(o.teks, TP_BATAS.teks); const nama = KOSONG(o.nama) ? tpPotong(m.namaPegawai, TP_BATAS.nama) : tpPotong(o.nama, TP_BATAS.nama);
  if (!sah(jenis)) return { tolak: 'Jenis titipan tidak dikenal — pilih belanja toko, untuk karyawan, kasbon, atau bayar bon pemasok' };
  if (!(n > 0)) return { tolak: 'Nominal hanya angka rupiah bulat di atas nol' };
  if (jenis === 'kasbon' && !nama) return { tolak: 'Kasbon butuh nama orangnya' };
  if (jenis !== 'kasbon' && jenis !== 'bayarBon' && jenis !== 'bongkar' && !teks) return { tolak: 'Keterangan uang keluar tidak boleh kosong' };
  if (sudahDitulis(m.id)) return { tolak: 'Uang untuk titipan ini sudah pernah ditulis — tidak ditulis dua kali' };
  const tgl = String(m.tanggal || w.tanggal); const jam = String(m.jam || w.jam);
  const kunci = tolakKunciTanggal(tgl, ''); if (kunci) return { tolak: 'Titipan bertanggal ' + tanggalPendek(tgl) + ': ' + kunci };
  const oleh = siapa + ' (disetujui owner)';
  let uang; let arti;
  if (jenis === 'bongkar') {
    // upah bongkar → kedatangannya (modal barang + kas keluar laci bertanggal datang, rumus mesin yang sama dengan bongkar yang dicatat owner)
    const b = ambilSemuaBatch().find((x) => String(x.id) === String(m.batchId || ''));
    if (!b) return { tolak: 'Kedatangan untuk upah bongkar ini sudah tidak ada — Betulkan jenisnya jadi Belanja toko, atau tolak' };
    const kb = tolakKunci('batchMasuk', b, 'upah bongkarnya tidak bisa ditulis ke kedatangan itu'); if (kb) return { tolak: kb };
    const ok = m.ongkir === true; const nmB = ok ? 'ongkos kirim' : 'upah bongkar';
    const riwayat = (Array.isArray(b.riwayat) ? b.riwayat : []).concat([{ teks: nmB + ' ' + RP(n) + ' dari titipan tablet (' + siapa + ') disetujui owner', tanggal: w.tanggal, jam: w.jam }]);
    uang = { koleksi: 'batchMasuk', data: Object.assign({}, b, { biayaBongkar: (Number(b.biayaBongkar) || 0) + n, bongkarTitipan: (Array.isArray(b.bongkarTitipan) ? b.bongkarTitipan : []).concat([String(m.id)]), riwayat },
      ok ? { ongkosKirim: Math.round(Number(b.ongkosKirim) || 0) + n } : {}) };
    arti = nmB + ' ' + RP(n) + ' masuk modal kedatangan ' + String(b.pemasok || '') + ' ' + tanggalPendek(b.tanggal || tgl) + ' (dari laci)';
  } else if (jenis === 'bayarBon') {
    // bayar bon pemasok lewat supir → owner memilih bonnya (bawaan tpBonPilihan); satu pembayaran satu bon, tidak melebihi sisa (aturan Bon pemasok)
    const P = tpBonPilihan(m.id, new Date(w.kini)); const bonId = KOSONG(o.bonId) ? P.bawaan : String(o.bonId);
    if (!bonId) return { tolak: 'Tidak ada bon ' + (tpPemasokTitip(m) || 'pemasok itu') + ' yang masih bersisa — Betulkan jenisnya (mis. Belanja toko) atau tolak' };
    if (!P.bon.some((b) => String(b.id) === bonId)) return { tolak: 'Bon yang dipilih bukan bon ' + (tpPemasokTitip(m) || 'pemasok itu') + ' yang masih bersisa' };
    const H = hitungBayar({ pemasok: P.bon.find((b) => String(b.id) === bonId).pemasok, bonId, ketik: String(n), dari: 'laci' }, new Date(w.kini));
    if (H.tolak) return { tolak: 'Bayar bon: ' + H.tolak };
    uang = { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: tgl, jam, tipe: 'bayar', pemasok: H.bon.pemasok, nominal: n, catatan: ('Lewat supir · titipan ' + siapa + (teks && teks !== 'Bayar lewat supir' ? ' · ' + teks : '')).slice(0, 80),
      bonId: H.bon.id, bonTanggal: H.bon.tanggal || null, dari: 'laci', oleh, dariPersetujuan: String(m.id) } };
    arti = 'bon ' + H.bon.pemasok + ' ' + tanggalPendek(H.bon.tanggal) + (H.lunas ? ' LUNAS' : ' sisa ' + RP(H.bon.sisa - n));
    o.bonDipilih = H.bon.id;
  } else if (jenis === 'kasbon') {
    uang = { koleksi: 'kasbonMutasi', data: { id: w.idUnik(), tipe: 'ambil', namaPegawai: nama, nominal: n, tanggal: tgl, jam, catatan: teks || 'Kasbon dari tablet', dari: 'laci', oleh, dariPersetujuan: String(m.id) } };
    arti = nama + ' berutang ' + RP(n) + ' ke toko, laba tidak berubah';
  } else {
    uang = { koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', untuk: jenis === 'karyawan' ? 'karyawan' : 'toko', tanggal: tgl, jam, keterangan: (teks || tpNamaJenis(tpJenis(m))) + (jenis === 'karyawan' && nama ? ' · ' + nama : ''), nominal: n, dari: 'laci', oleh, dariPersetujuan: String(m.id) } };
    arti = 'biaya toko ' + RP(n) + (jenis === 'karyawan' ? ' (untuk karyawan)' : '');
  }
  const ubah = n !== Math.round(Number(m.nominal) || 0) || jenis !== tpJenis(m) || teks !== String(m.teks || '') || nama !== String(m.namaPegawai || '');
  const baru = Object.assign({}, m, { status: 'disetujui' }, putus);
  if (o.bonDipilih) baru.bonId = String(o.bonDipilih);
  if (ubah) Object.assign(baru, { koreksiOwner: true, nominalAsli: Math.round(Number(m.nominal) || 0), jenisAsli: tpJenis(m), teksAsli: String(m.teks || ''), namaAsli: String(m.namaPegawai || ''),
    nominal: n, jenis, teks, namaPegawai: nama });
  return { dokumen: [{ koleksi: 'persetujuan', data: baru }, uang],
    patch: { kabar: 'Titipan ' + siapa + ' disetujui' + (ubah ? ' dengan betulan' : '') + ' · laci berkurang ' + RP(n) + ' pada ' + tanggalPendek(tgl) + ' ' + jam + ' · ' + arti, kabarAwas: false } };
}

// ---------- cetak (teks polos → printer tablet gaya teks / dialog cetak) ----------
/** Slip satu titipan / pesan. kop = { nama } setelan struk; dicetak = { tanggal, jam, oleh }. Baris "label  nilai" = dua spasi pemisah (epGarisDariTeks). */
export function tpTeksCetak(b, kop, dicetak) {
  const K = kop || {}; const C = dicetak || {}; const g = [];
  g.push(b.kabar ? 'KABAR BARANG MASUK' : b.pesan ? 'PESAN UNTUK OWNER' : 'TITIPAN UANG KELUAR');
  if (K.nama) g.push(String(K.nama).toUpperCase());
  g.push('');
  g.push('Dari  ' + b.dari); g.push('Waktu  ' + tanggalPendek(b.tanggal) + (b.jam ? ' ' + b.jam : ''));
  if (b.pesan) { g.push(''); String(b.teks).split('\n').forEach((x) => g.push(x)); }
  else {
    g.push('Jenis  ' + b.namaJenis); if (b.nama) g.push((b.jenis === 'kasbon' ? 'Atas nama' : 'Untuk') + '  ' + b.nama); if (b.pemasok) g.push('Pemasok  ' + b.pemasok);
    if (b.teks) g.push('Untuk apa: ' + b.teks);
    g.push('NOMINAL  ' + RP(b.nominal));
    if (b.asli) g.push('Diketik  ' + RP(b.asli.nominal) + (b.asli.teks && b.asli.teks !== b.teks ? ' (' + b.asli.teks + ')' : ''));
  }
  g.push('');
  g.push('Status  ' + b.namaStatus + (b.diputus ? ' ' + b.diputus : ''));
  if (b.alasan) g.push('Alasan owner: ' + b.alasan);
  if (b.balasan) g.push('Balasan owner: ' + b.balasan);
  if (!b.pesan && b.status === 'menunggu') g.push('Laci di buku belum berkurang sampai owner menyetujui.');
  if (C.tanggal) g.push('Dicetak ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', ' + C.oleh : ''));
  if (!b.pesan) { g.push(''); g.push('Paraf yang jaga:'); g.push(''); g.push('(.............)'); }
  return g.join('\n');
}
/** Rekap titipan & pesan satu hari dari tablet ini (cetak "semua hari ini"). */
export function tpTeksRekap(baris, iso, kop, dicetak) {
  const K = kop || {}; const C = dicetak || {}; const hari = baris.filter((b) => b.tanggal === iso); const g = [];
  g.push('TITIPAN & PESAN ' + tanggalPendek(iso).toUpperCase()); if (K.nama) g.push(String(K.nama).toUpperCase()); g.push('');
  if (!hari.length) g.push('Tidak ada titipan atau pesan hari ini.');
  const uang = hari.filter((b) => !b.pesan); const pesan = hari.filter((b) => b.pesan);
  uang.forEach((b) => { g.push(b.jam + ' ' + b.dari + ' ' + b.namaJenis + (b.nama ? ' ' + b.nama : '') + '  ' + RP(b.nominal)); if (b.teks) g.push('  ' + b.teks); g.push('  ' + b.namaStatus + (b.alasan ? ': ' + b.alasan : '')); });
  if (uang.length) {
    const jml = (st) => uang.filter((b) => b.status === st).reduce((a, b) => a + b.nominal, 0);
    g.push(''); g.push('Disetujui  ' + RP(jml('disetujui'))); g.push('Menunggu  ' + RP(jml('menunggu'))); if (jml('ditolak')) g.push('Ditolak  ' + RP(jml('ditolak')));
  }
  if (pesan.length) { g.push(''); g.push('Pesan: ' + pesan.length); pesan.forEach((b) => { g.push(b.jam + ' ' + b.dari + ' (' + b.namaStatus + ')'); g.push('  ' + b.teks.replace(/\n/g, ' ')); if (b.balasan) g.push('  Balas: ' + b.balasan); }); }
  if (C.tanggal) { g.push(''); g.push('Dicetak ' + tanggalPendek(C.tanggal) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', ' + C.oleh : '')); }
  return g.join('\n');
}
