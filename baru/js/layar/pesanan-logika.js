// PESANAN, PO & ORDER RUTIN — putaran B4 (keputusan owner 18 Nov 2026). Logika TANPA DOM, nama berawalan po (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_pesanan.py (jsc + statis + kontrol).
//
// Keputusan owner 18 Nov 2026 (semua "Recommended"):
//  1. SIAPA: owner + Ben membuat & mengubah pesanan, PO, dan jadwal rutin — juga dari tablet (akun peran Ben). Rules v11: pesanan create/ubah Ben
//     (stafBuatPesanan, stafAturPesanan) + koleksi orderRutin. Karyawan cuma melihat (catat jual pesanan tetap seperti dulu).
//  2. UANG MUKA (DP) = uang pelanggan DIPEGANG toko, BUKAN omzet. Dicatat sebagai satu pembayaran bon (piutangMutasi bayar) ber-`untukPesanan` SEBELUM
//     notanya lahir — mesin beku membacanya apa adanya: kas naik, sisa bon orang itu turun (atau jadi "kelebihan bayar" kalau ia tidak punya bon). Nota
//     pesanannya kelak = nota bon yang DIPOTONG DP itu (jual-logika): yang dibayar saat itu = total − DP, sisa bon orang itu kembali nol.
//     BATAL (owner: pilih per kasus): DP jadi SALDO pelanggan (tidak ada catatan uang baru — tetap kelebihan bayar, memotong belanja berikutnya) ATAU
//     DIKEMBALIKAN tunai dari laci — owner saja (uang keluar dari laci), satu pembayaran bernilai MINUS (mesin menjumlah nominal apa adanya: kas turun,
//     kelebihannya hilang; laba tidak tersentuh — pola hapus buku minus Paket F2).
//  3. JADWAL RUTIN = PENGINGAT: N hari sebelum tanggal kirimnya (diatur owner di Pelanggan › Atur) muncul di Pesanan & Dasbor sebagai "belum dibuat";
//     diketuk → form pesanan terisi (isi bisa diubah dulu). TIDAK ada pesanan yang lahir sendiri. "Lewati sekali" dicatat di jadwalnya.
//  4. ISI PESANAN dari KATALOG: baris { jalur karung | kemasan | literan, kunci, berat / ukuran, jumlah } → cek stok vs laju jual & keranjang terisi sendiri
//     saat "catat jual". Pesanan lama (teks bebas) tetap terbaca apa adanya.
// Nomor PO = nomor dari PELANGGAN (instansi / catering) — dicetak di nota, faktur & surat jalan; toko tidak membuatnya.
// MESIN UANG TIDAK DISENTUH.
import { ambilPesanan, ambilPiutangMutasi, ambilOrderRutin, cacheMentah } from '../data/toko.js';
import { kunciPelanggan, pesananBelumTuntas } from '../mesin/pembantu.js';
import { RP, tanggalPendek } from '../inti/format.js';

export const PO_KOLEKSI_RUTIN = 'orderRutin';
export const PO_MAKS_BARIS = 12;
export const PO_NO_MAKS = 30;
export const PO_CATATAN_MAKS = 120;
export const PO_DP_MAKS = 100000000;          // Rp100 juta — penjaga salah ketik uang muka, bukan kebijakan
export const PO_HARI_INGAT_BAWAAN = 2;
export const PO_HARI_INGAT_MAKS = 14;
export const PO_TERLEWAT_HARI = 7;            // pengingat yang tanggal kirimnya sudah lewat tetap tampil seminggu ("terlewat")
export const PO_JENDELA_STOK_HARI = 14;       // cek stok membaca pesanan & jadwal sampai 14 hari ke depan
export const PO_ULANG = { mingguan: 'tiap minggu', duaMinggu: 'tiap 2 minggu', bulanan: 'tiap bulan' };
export const PO_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
export const PO_JALUR = ['karung', 'kemasan', 'literan'];
export const PO_NASIB = { saldo: 'jadi saldo pelanggan', kembali: 'dikembalikan tunai' };
// kolom pesanan yang boleh diubah Ben (rules v11 stafAturPesanan — daftar yang SAMA, dijaga uji statis)
export const PO_KOLOM_ATUR = ['status', 'riwayatStatus', 'baris', 'isi', 'noPO', 'tanggalKirim', 'alamat', 'nilaiPerkiraan', 'catatan', 'alasanBatal', 'nasibUangMuka'];
// kolom jadwal rutin yang boleh diubah Ben (rules v11 stafUbahRutin — daftar yang SAMA)
export const PO_KOLOM_RUTIN = ['namaPelanggan', 'baris', 'isi', 'alamat', 'noPO', 'catatan', 'ulang', 'hari', 'tanggalBulan', 'mulai', 'aktif', 'lewati'];

const poKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const poTeks = (v, n) => (poKosong(v) ? '' : String(v).trim().slice(0, n || 200));
const poBulat = (n) => Math.round(Number(n) || 0);
const poJumlahTeks = (n) => String(Math.round((Number(n) || 0) * 100) / 100).replace('.', ',');

// ---------- tanggal (hari ke-N sejak 1970-01-01 UTC; tanpa jam dinding) ----------
export function poHariKe(iso) { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || '')); return m ? Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000) : null; }
export function poIso(n) { return new Date(n * 86400000).toISOString().slice(0, 10); }
export function poTanggalSah(iso) { const n = poHariKe(iso); return n !== null && poIso(n) === String(iso); }
/** 0 = Minggu … 6 = Sabtu (1 Jan 1970 = Kamis). */
export function poHariMinggu(iso) { const n = poHariKe(iso); return n === null ? null : (((n + 4) % 7) + 7) % 7; }
const poTanggalBulan = (iso) => Number(String(iso).slice(8, 10));

// ---------- atur (Pelanggan › Atur — aturanToko/pelanggan, dokumen yang juga dibaca tablet Ben) ----------
const poAturMentah = () => cacheMentah('aturan').find((d) => String(d.id) === 'pelanggan') || null;
const poHariIngatSah = (v) => { const n = Number(String(v === undefined || v === null ? '' : v).trim()); return String(v).trim() !== '' && Number.isInteger(n) && n >= 0 && n <= PO_HARI_INGAT_MAKS ? n : null; };
/** Berapa hari sebelum tanggal kirim pengingat jadwal rutin muncul (owner; bawaan 2). */
export function poHariIngat() { const a = poAturMentah(); const n = a ? poHariIngatSah(a.hariIngatRutin) : null; return n === null ? PO_HARI_INGAT_BAWAAN : n; }
/** Bagian aturanToko/pelanggan milik B4 (dipanggil susunAturPelanggan): { hariIngatRutin } atau { tolak }. teks undefined = tetap. */
export function poBacaAtur(teks) {
  if (teks === undefined || poKosong(teks)) return { hariIngatRutin: poHariIngat() };
  const n = poHariIngatSah(teks); return n === null ? { tolak: 'Pengingat order rutin: 0–' + PO_HARI_INGAT_MAKS + ' hari sebelum tanggal kirim (bilangan bulat)' } : { hariIngatRutin: n };
}

// ---------- baris pesanan dari katalog ----------
/** Angka jumlah yang diketik ("1,5", "2") → bilangan, atau NaN. */
export function poAngka(v) { const t = String(v === undefined || v === null ? '' : v).trim().replace(',', '.'); return /^\d+(\.\d+)?$/.test(t) ? Number(t) : NaN; }
/** Uang yang diketik bebas ("Rp 1.500.000") → bilangan bulat ≥ 0. */
export function poRupiah(v) { return Math.round(Number(String(v === undefined || v === null ? '' : v).replace(/[^\d]/g, '')) || 0); }
/**
 * Satu baris pesanan dari chip rak Jual (jalur karung / kemasan / literan) + jumlah. → { baris } atau { tolak }.
 * baris = { jalur, kunci, berat (karung), ukuranKg (kemasan), rasio (literan, kg/L), wadah (literan wadah), nama, jumlah, satuan, kg }.
 */
export function poBarisDariChip(chip, jumlah) {
  if (!chip || PO_JALUR.indexOf(chip.jalur) < 0) return { tolak: 'Pesanan memakai barang karung, kemasan, atau literan dari katalog' };
  const j = poAngka(jumlah); if (!(j > 0)) return { tolak: 'Isi jumlah ' + (chip.nama || 'barangnya') };
  if (chip.jalur === 'karung') {
    if ((j * 2) % 1 !== 0) return { tolak: 'Karung dipesan utuh atau setengah (0,5 · 1 · 1,5 …)' };
    const berat = Number(chip.berat) || 0; if (!(berat > 0)) return { tolak: 'Berat karung ' + chip.nama + ' tidak terbaca' };
    return { baris: { jalur: 'karung', kunci: String(chip.kunci), berat, nama: chip.nama + ' ' + berat + ' kg', jumlah: j, satuan: 'karung', kg: j * berat } };
  }
  if (chip.jalur === 'kemasan') {
    if (j % 1 !== 0) return { tolak: 'Kemasan dipesan per unit' };
    const uk = Number(chip.ukuranKg) || 0;
    return { baris: { jalur: 'kemasan', kunci: String(chip.kunci), ukuranKg: uk, nama: chip.nama + ' ' + String(uk).replace('.', ',') + ' kg', jumlah: j, satuan: 'kemasan', kg: j * uk } };
  }
  const rasio = Number(chip.rasio) || 0;
  const b = { jalur: 'literan', kunci: String(chip.kunci), rasio, nama: chip.nama + ' literan', jumlah: j, satuan: 'L', kg: Math.round(j * rasio * 100) / 100 };
  if (chip.wadahLiteran) b.wadah = true;
  return { baris: b };
}
/** Baris tersimpan dibersihkan (dokumen lama / ketikan rusak dibuang). */
export function poBarisSah(daftar) {
  return (Array.isArray(daftar) ? daftar : []).filter((b) => b && PO_JALUR.indexOf(b.jalur) >= 0 && !poKosong(b.kunci) && Number(b.jumlah) > 0).slice(0, PO_MAKS_BARIS)
    .map((b) => { const o = { jalur: b.jalur, kunci: String(b.kunci), nama: poTeks(b.nama, 80) || String(b.kunci), jumlah: Number(b.jumlah), satuan: poTeks(b.satuan, 12) || (b.jalur === 'literan' ? 'L' : b.jalur), kg: Number(b.kg) || 0 };
      if (b.jalur === 'karung') o.berat = Number(b.berat) || 0; if (b.jalur === 'kemasan') o.ukuranKg = Number(b.ukuranKg) || 0;
      if (b.jalur === 'literan') { o.rasio = Number(b.rasio) || 0; if (b.wadah) o.wadah = true; }
      return o; });
}
/** Teks isi (kolom `isi` dokumen lama — daftar, struk, ikatan keranjang): "2 karung IR64 Elevate 50 kg · 10 kemasan Angsa 5 kg". */
export function poIsiTeks(baris) {
  return poBarisSah(baris).map((b) => poJumlahTeks(b.jumlah) + ' ' + (b.jalur === 'literan' ? 'L' : b.satuan) + ' ' + b.nama.replace(/ literan$/, '')).join(' · ');
}
/** Kunci satu baris (karung berbeda berat = baris berbeda). */
export const poKunciBaris = (b) => b.jalur + '|' + b.kunci + (b.jalur === 'karung' ? '|' + (Number(b.berat) || 0) : '');
/** Chip rak yang cocok dengan satu baris pesanan, atau null (barang sudah tidak di rak / harganya kosong). */
export function poChipCocok(rak, b) {
  const daftar = (rak && rak[b.jalur]) || [];
  return daftar.find((c) => String(c.kunci) === String(b.kunci) && (b.jalur !== 'karung' || Number(c.berat) === Number(b.berat))) || null;
}
/** Tambah / ganti baris di draf (barang yang sama dijumlah ulang = diganti). */
export function poTaruhBaris(daftar, b) {
  const k = poKunciBaris(b); const ada = (daftar || []).findIndex((x) => poKunciBaris(x) === k);
  if (ada >= 0) { const d = daftar.slice(); d[ada] = b; return { baris: d }; }
  if ((daftar || []).length >= PO_MAKS_BARIS) return { tolak: 'Satu pesanan paling banyak ' + PO_MAKS_BARIS + ' barang — sisanya jadi pesanan kedua' };
  return { baris: (daftar || []).concat([b]) };
}

// ---------- pesanan ----------
export function poAmbil(id) { return (ambilPesanan() || []).find((p) => String(p.id) === String(id)) || null; }
/** Pesanan baru / yang diubah dicatat sebagai draf layar: { id ('' = baru), nama, noPO, tanggalKirim, alamat, catatan, baris[], jadwal, dariJadwal }. */
export function poDrafBaru(nama, alamat) {
  return { id: '', nama: poTeks(nama, 40), noPO: '', tanggalKirim: '', alamat: poTeks(alamat, 120), catatan: '', baris: [], jadwal: null, dariJadwal: null };
}
export function poDrafDariPesanan(ps) {
  return { id: String(ps.id), nama: poTeks(ps.namaPelanggan, 40), noPO: poTeks(ps.noPO, PO_NO_MAKS), tanggalKirim: poTanggalSah(ps.tanggalKirim) ? String(ps.tanggalKirim) : '',
    alamat: poTeks(ps.alamat, 120), catatan: poTeks(ps.catatan, PO_CATATAN_MAKS), baris: poBarisSah(ps.baris), jadwal: null, dariJadwal: null, isiLama: Array.isArray(ps.baris) && ps.baris.length ? '' : poTeks(ps.isi, 200) };
}
/**
 * Susun dokumen pesanan dari draf. w = { tanggal, jam, kini, idUnik }. opsi.harga(baris) → rupiah perkiraan satu baris (harga pembeli itu: eceran / tingkat).
 * Baru: status dipesan (rules v11 stafBuatPesanan). Ubah: hanya kolom PO_KOLOM_ATUR, pesanan yang belum jadi nota / batal; nama pemesan tidak bisa
 * diganti (uang muka & bon atas nama itu) — batalkan lalu buat baru.
 */
export function poSusunPesanan(draf, w, opsi) {
  const o = opsi || {}; const d = draf || {}; const nama = poTeks(d.nama, 40);
  if (!nama) return { tolak: 'Isi nama pemesannya' };
  const baris = poBarisSah(d.baris); if (!baris.length) return { tolak: 'Pilih barangnya dari katalog (minimal satu)' };
  const noPO = poTeks(d.noPO, PO_NO_MAKS + 1); if (noPO.length > PO_NO_MAKS) return { tolak: 'Nomor PO paling panjang ' + PO_NO_MAKS + ' huruf' };
  const tk = poKosong(d.tanggalKirim) ? '' : String(d.tanggalKirim).trim(); if (tk && !poTanggalSah(tk)) return { tolak: 'Tanggal kirim tidak terbaca' };
  if (tk && !d.id && poHariKe(tk) < poHariKe(w.tanggal)) return { tolak: 'Tanggal kirim sudah lewat — kosongkan atau pilih hari ini / sesudahnya' };
  const isi = poIsiTeks(baris); const nilai = typeof o.harga === 'function' ? baris.reduce((a, b) => a + poBulat(o.harga(b)), 0) : 0;
  const kolom = { baris, isi, noPO, tanggalKirim: tk, alamat: poTeks(d.alamat, 120), catatan: poTeks(d.catatan, PO_CATATAN_MAKS), nilaiPerkiraan: nilai };
  const dokumen = []; let ps;
  if (d.id) {
    const lama = poAmbil(d.id); if (!lama) return { tolak: 'Pesanan tidak ditemukan' };
    if (!pesananBelumTuntas(lama)) return { tolak: 'Pesanan ini sudah ' + (lama.status === 'batal' ? 'dibatalkan' : 'jadi nota') + ' — tidak bisa diubah' };
    if (kunciPelanggan(lama.namaPelanggan) !== kunciPelanggan(nama)) return { tolak: 'Nama pemesan tidak bisa diganti (uang muka & bon atas nama ' + lama.namaPelanggan + ') — batalkan lalu buat pesanan baru' };
    ps = Object.assign({}, lama, kolom, { riwayatStatus: (lama.riwayatStatus || []).concat([{ status: lama.status || 'dipesan', pada: w.kini, ubah: true }]) });
  } else {
    ps = Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, namaPelanggan: nama }, kolom, { status: 'dipesan', trxIdJual: null, riwayatStatus: [{ status: 'dipesan', pada: w.kini }] });
    if (d.dariJadwal && d.dariJadwal.id) { ps.jadwalId = String(d.dariJadwal.id); ps.jadwalTanggal = String(d.dariJadwal.tanggal || ''); }
  }
  dokumen.push({ koleksi: 'pesanan', data: ps });
  // jadwal rutin baru dari form yang sama: tanggal kirim pesanan ini = kejadian pertamanya (pesanan diikat ke kejadian itu → tidak jadi pengingat lagi)
  let jadwal = null;
  if (!d.id && d.jadwal && d.jadwal.nyala) {
    const J = poSusunJadwal(Object.assign({}, d.jadwal, { nama, baris, alamat: kolom.alamat, noPO, catatan: kolom.catatan, mulai: d.jadwal.mulai || tk || w.tanggal }), w);
    if (J.tolak) return { tolak: 'Jadwal rutin: ' + J.tolak };
    jadwal = J.dokumen[0].data; dokumen.push(J.dokumen[0]);
    if (tk && poKejadian(jadwal, tk, tk).length) { ps.jadwalId = String(jadwal.id); ps.jadwalTanggal = tk; }
  }
  const kata = (d.id ? 'Pesanan ' + nama + ' diubah' : 'Pesanan ' + nama + ' dicatat') + ' — ' + isi + (tk ? ' · kirim ' + tanggalPendek(tk) : '') + (noPO ? ' · PO ' + noPO : '')
    + (nilai ? ' · perkiraan ' + RP(nilai) : '') + (jadwal ? ' · jadwal ' + poKataJadwal(jadwal) : '') + '. Belum uang, belum stok: jadi nota begitu notanya dicatat.';
  return { dokumen, pesanan: ps, jadwal, patch: { kabar: kata, kabarAwas: false } };
}

// ---------- uang muka ----------
/** Uang muka satu pesanan: pembayaran bon ber-untukPesanan (termasuk pengembalian bernilai minus). → { total, masuk, kembali, daftar } */
export function poUangMuka(id) {
  const daftar = (ambilPiutangMutasi() || []).filter((m) => m && m.tipe === 'bayar' && String(m.untukPesanan || '') === String(id) && !m.notaTrxId)
    .map((m) => ({ id: String(m.id), nominal: Number(m.nominal) || 0, cara: m.caraBayar || 'Tunai', tanggal: m.tanggal || '', jam: m.jam || '', kembali: (Number(m.nominal) || 0) < 0 }))
    .sort((a, b) => String(a.tanggal + a.jam).localeCompare(String(b.tanggal + b.jam)));
  const masuk = daftar.filter((x) => x.nominal > 0).reduce((a, x) => a + x.nominal, 0); const kembali = daftar.filter((x) => x.nominal < 0).reduce((a, x) => a - x.nominal, 0);
  return { total: Math.max(0, masuk - kembali), masuk, kembali, daftar };
}
/** Catat uang muka (Tunai / QRIS) untuk pesanan yang belum jadi nota. Atas nama pemesan — mesin menjumlahnya ke buku bon orang itu. */
export function poSusunUangMuka(ps, nominal, cara, w) {
  if (!ps) return { tolak: 'Pesanan tidak ditemukan' };
  if (!pesananBelumTuntas(ps)) return { tolak: 'Pesanan ini sudah ' + (ps.status === 'batal' ? 'dibatalkan' : 'jadi nota') + ' — uang muka tidak bisa ditambah' };
  const nama = poTeks(ps.namaPelanggan, 40); if (!nama) return { tolak: 'Pesanan tanpa nama pemesan tidak bisa menerima uang muka' };
  const n = poRupiah(nominal); if (!(n > 0)) return { tolak: 'Ketik uang mukanya' };
  if (n > PO_DP_MAKS) return { tolak: 'Uang muka ' + RP(n) + ' melebihi ' + RP(PO_DP_MAKS) + ' — periksa ketikannya' };
  const c = cara === 'QRIS' ? 'QRIS' : 'Tunai';
  const data = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: nama, nominal: n, tanggal: w.tanggal, jam: w.jam, caraBayar: c, dicatatDi: 'sistem', untukPesanan: String(ps.id),
    catatan: 'Uang muka pesanan' + (ps.noPO ? ' PO ' + ps.noPO : '') + ' — ' + poTeks(ps.isi, 80) };
  const U = poUangMuka(ps.id);
  return { dokumen: [{ koleksi: 'piutangMutasi', data }], patch: { kabar: 'Uang muka ' + RP(n) + ' (' + c + ') dicatat untuk pesanan ' + nama + ' — total uang muka ' + RP(U.total + n)
    + '. Uang pelanggan dipegang toko, BUKAN omzet: notanya kelak dipotong sebesar ini.', kabarAwas: false } };
}
/**
 * Batalkan pesanan. Ada uang muka → pilihan WAJIB: 'saldo' (tetap tercatat sebagai kelebihan bayar orang itu, memotong belanja berikutnya) atau 'kembali'
 * (owner saja: uang keluar dari laci — satu pembayaran bernilai minus). opsi.owner = akun yang masuk owner.
 */
export function poSusunBatal(ps, pilihan, alasan, w, opsi) {
  const o = opsi || {};
  if (!ps) return { tolak: 'Pesanan tidak ditemukan' };
  if (!pesananBelumTuntas(ps)) return { tolak: 'Pesanan ini sudah ' + (ps.status === 'batal' ? 'dibatalkan' : 'jadi nota') };
  const U = poUangMuka(ps.id); const al = poTeks(alasan, 120);
  const d = Object.assign({}, ps, { status: 'batal', riwayatStatus: (ps.riwayatStatus || []).concat([{ status: 'batal', pada: w.kini }]) });
  if (al) d.alasanBatal = al;
  const dokumen = [];
  if (U.total > 0) {
    if (pilihan !== 'saldo' && pilihan !== 'kembali') return { tolak: 'Pesanan ini punya uang muka ' + RP(U.total) + ' — pilih dulu: jadi saldo pelanggan, atau dikembalikan tunai' };
    if (pilihan === 'kembali' && !o.owner) return { tolak: 'Mengembalikan uang muka = uang keluar dari laci — owner yang mencatatnya. Pilih "jadi saldo pelanggan", atau minta owner.' };
    d.nasibUangMuka = pilihan;
    if (pilihan === 'kembali') {
      dokumen.push({ koleksi: 'piutangMutasi', data: { id: w.idUnik(), tipe: 'bayar', namaPelanggan: poTeks(ps.namaPelanggan, 40), nominal: -U.total, tanggal: w.tanggal, jam: w.jam,
        caraBayar: 'Tunai', dicatatDi: 'sistem', untukPesanan: String(ps.id), kembaliUangMuka: true, catatan: 'Uang muka dikembalikan — pesanan batal' + (al ? ' (' + al + ')' : '') } });
    }
  }
  dokumen.unshift({ koleksi: 'pesanan', data: d });
  const kata = 'Pesanan ' + ps.namaPelanggan + ' dibatalkan' + (U.total > 0 ? (pilihan === 'kembali' ? ' — uang muka ' + RP(U.total) + ' dikembalikan TUNAI dari laci' : ' — uang muka ' + RP(U.total) + ' jadi SALDO ' + ps.namaPelanggan + ' (memotong belanja berikutnya)') : '') + '. Jejaknya tetap tersimpan.';
  return { dokumen, patch: { kabar: kata, kabarAwas: false } };
}

// ---------- jadwal rutin ----------
/** Jadwal tersimpan dibaca ke bentuk baku (dokumen rusak dibuang). */
export function poJadwalBaku(j) {
  if (!j || poKosong(j.id) || !PO_ULANG[j.ulang]) return null;
  const hari = Number(j.hari); const tb = Number(j.tanggalBulan);
  return { id: String(j.id), nama: poTeks(j.namaPelanggan, 40), baris: poBarisSah(j.baris), isi: poTeks(j.isi, 200) || poIsiTeks(j.baris), alamat: poTeks(j.alamat, 120), noPO: poTeks(j.noPO, PO_NO_MAKS),
    catatan: poTeks(j.catatan, PO_CATATAN_MAKS), ulang: j.ulang, hari: Number.isInteger(hari) && hari >= 0 && hari <= 6 ? hari : null, tanggalBulan: Number.isInteger(tb) && tb >= 1 && tb <= 28 ? tb : null,
    mulai: poTanggalSah(j.mulai) ? String(j.mulai) : '', aktif: j.aktif !== false, lewati: (Array.isArray(j.lewati) ? j.lewati : []).filter(poTanggalSah).map(String) };
}
export function poJadwalSemua() { return (ambilOrderRutin() || []).map(poJadwalBaku).filter(Boolean).sort((a, b) => a.nama.localeCompare(b.nama, 'id') || a.id.localeCompare(b.id)); }
export function poKataJadwal(j) {
  const J = j && j.ulang ? j : poJadwalBaku(j); if (!J) return '';
  return PO_ULANG[J.ulang] + (J.ulang === 'bulanan' ? ' tanggal ' + J.tanggalBulan : ' hari ' + PO_HARI[J.hari]);
}
/** Tanggal-tanggal kirim satu jadwal di [dari, sampai] (iso, inklusif), mulai dari `mulai`. */
export function poKejadian(j0, dari, sampai) {
  const j = j0 && 'nama' in j0 && 'lewati' in j0 ? j0 : poJadwalBaku(j0); if (!j || !j.mulai) return [];
  const a = Math.max(poHariKe(dari), poHariKe(j.mulai)); const b = poHariKe(sampai); if (a === null || b === null || a > b) return [];
  const out = [];
  if (j.ulang === 'bulanan') { if (j.tanggalBulan === null) return []; for (let n = a; n <= b; n++) if (poTanggalBulan(poIso(n)) === j.tanggalBulan) out.push(poIso(n)); return out; }
  if (j.hari === null) return [];
  let pertama = poHariKe(j.mulai); while (poHariMinggu(poIso(pertama)) !== j.hari) pertama += 1;
  const langkah = j.ulang === 'duaMinggu' ? 14 : 7;
  let n = pertama; if (n < a) n += Math.ceil((a - n) / langkah) * langkah;
  for (; n <= b; n += langkah) out.push(poIso(n));
  return out;
}
/** Sudah ada pesanan (status apa pun, juga batal) untuk satu kejadian jadwal? */
const poSudahDibuat = (jid, tgl) => (ambilPesanan() || []).some((p) => p && String(p.jadwalId || '') === String(jid) && String(p.jadwalTanggal || '') === String(tgl));
/**
 * PENGINGAT order rutin (owner 18 Nov 2026): kejadian jadwal aktif dari (hari − 7) sampai (hari + N) yang BELUM dibuat pesanannya & tidak dilewati.
 * → [{ jadwal, tanggal, hariLagi (negatif = terlewat), terlewat, kata }] urut tanggal.
 */
export function poPengingat(hariIso, nIngat) {
  const N = nIngat === undefined || nIngat === null ? poHariIngat() : nIngat; const h = poHariKe(hariIso); if (h === null) return [];
  const out = [];
  poJadwalSemua().filter((j) => j.aktif).forEach((j) => {
    poKejadian(j, poIso(h - PO_TERLEWAT_HARI), poIso(h + N)).forEach((t) => {
      if (j.lewati.indexOf(t) >= 0 || poSudahDibuat(j.id, t)) return;
      const lagi = poHariKe(t) - h;
      out.push({ jadwal: j, tanggal: t, hariLagi: lagi, terlewat: lagi < 0, kata: lagi < 0 ? 'terlewat ' + (-lagi) + ' hari' : lagi === 0 ? 'kirim HARI INI' : lagi === 1 ? 'kirim besok' : 'kirim ' + lagi + ' hari lagi' });
    });
  });
  return out.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.jadwal.nama.localeCompare(b.jadwal.nama, 'id'));
}
/** Draf form pesanan dari satu pengingat (isi bisa diubah dulu sebelum dicatat). */
export function poDrafDariJadwal(j, tanggal) {
  return { id: '', nama: j.nama, noPO: j.noPO, tanggalKirim: tanggal, alamat: j.alamat, catatan: j.catatan, baris: j.baris.slice(), jadwal: null, dariJadwal: { id: j.id, tanggal } };
}
/**
 * Jadwal baru / diubah. isi = { id ('' = baru), nama, baris[], alamat, noPO, catatan, ulang, hari, tanggalBulan, mulai, aktif }. → { dokumen } atau { tolak }.
 * Ubah oleh Ben = kolom PO_KOLOM_RUTIN saja (rules v11) — nama pembuat & tanggal dibuat tidak berubah.
 */
export function poSusunJadwal(isi, w) {
  const x = isi || {}; const nama = poTeks(x.nama, 40); if (!nama) return { tolak: 'Isi nama pemesannya' };
  const baris = poBarisSah(x.baris); if (!baris.length) return { tolak: 'Pilih barangnya dari katalog (minimal satu)' };
  if (!PO_ULANG[x.ulang]) return { tolak: 'Pilih ulangnya: tiap minggu, tiap 2 minggu, atau tiap bulan' };
  const mulai = poKosong(x.mulai) ? w.tanggal : String(x.mulai).trim(); if (!poTanggalSah(mulai)) return { tolak: 'Tanggal mulai tidak terbaca' };
  let hari = null; let tb = null;
  if (x.ulang === 'bulanan') { tb = poKosong(x.tanggalBulan) ? poTanggalBulan(mulai) : Number(x.tanggalBulan); if (!(Number.isInteger(tb) && tb >= 1 && tb <= 28)) return { tolak: 'Tanggal tiap bulan: 1–28 (tanggal 29–31 tidak ada di semua bulan)' }; }
  else { hari = poKosong(x.hari) ? poHariMinggu(mulai) : Number(x.hari); if (!(Number.isInteger(hari) && hari >= 0 && hari <= 6)) return { tolak: 'Pilih hari kirimnya' }; }
  const kolom = { namaPelanggan: nama, baris, isi: poIsiTeks(baris), alamat: poTeks(x.alamat, 120), noPO: poTeks(x.noPO, PO_NO_MAKS), catatan: poTeks(x.catatan, PO_CATATAN_MAKS),
    ulang: x.ulang, hari, tanggalBulan: tb, mulai, aktif: x.aktif !== false };
  if (x.id) {
    const lama = (ambilOrderRutin() || []).find((j) => String(j.id) === String(x.id)); if (!lama) return { tolak: 'Jadwal tidak ditemukan' };
    return { dokumen: [{ koleksi: PO_KOLEKSI_RUTIN, data: Object.assign({}, lama, kolom, { lewati: (poJadwalBaku(lama) || { lewati: [] }).lewati }) }],
      patch: { kabar: 'Jadwal ' + nama + ' diubah — ' + poKataJadwal(kolom) + ' · ' + kolom.isi, kabarAwas: false } };
  }
  const data = Object.assign({ id: w.idUnik(), dibuatTanggal: w.tanggal }, kolom, { lewati: [] });
  return { dokumen: [{ koleksi: PO_KOLEKSI_RUTIN, data }], patch: { kabar: 'Jadwal rutin ' + nama + ' dicatat — ' + poKataJadwal(data) + ' · ' + data.isi + '. Pengingat muncul ' + poHariIngat() + ' hari sebelumnya; pesanannya tetap dibuat dengan ketukan.', kabarAwas: false } };
}
/** Hentikan / jalankan lagi satu jadwal (tidak dihapus — jejak tetap). */
export function poSusunJadwalAktif(id, aktif, w) {
  const lama = (ambilOrderRutin() || []).find((j) => String(j.id) === String(id)); if (!lama) return { tolak: 'Jadwal tidak ditemukan' };
  const J = poJadwalBaku(lama);
  return { dokumen: [{ koleksi: PO_KOLEKSI_RUTIN, data: Object.assign({}, lama, { aktif: !!aktif }) }], patch: { kabar: 'Jadwal ' + (J ? J.nama : '') + (aktif ? ' jalan lagi' : ' dihentikan — pengingatnya tidak muncul lagi (bisa dijalankan lagi)'), kabarAwas: false } };
}
/** Lewati SEKALI satu tanggal kirim (mis. pelanggan libur minggu ini). Lewatan lebih dari 60 hari lalu dibuang supaya dokumennya tidak tumbuh terus. */
export function poSusunLewati(id, tanggal, w) {
  const lama = (ambilOrderRutin() || []).find((j) => String(j.id) === String(id)); if (!lama) return { tolak: 'Jadwal tidak ditemukan' };
  if (!poTanggalSah(tanggal)) return { tolak: 'Tanggal tidak terbaca' };
  const J = poJadwalBaku(lama); const batas = poHariKe(w.tanggal) - 60;
  const lewati = J.lewati.filter((t) => poHariKe(t) >= batas && t !== tanggal).concat([String(tanggal)]).sort();
  return { dokumen: [{ koleksi: PO_KOLEKSI_RUTIN, data: Object.assign({}, lama, { lewati }) }], patch: { kabar: 'Jadwal ' + J.nama + ' ' + tanggalPendek(tanggal) + ' dilewati sekali — jadwal berikutnya tetap jalan', kabarAwas: false } };
}

// ---------- daftar pesanan aktif (bentuk kartu layar) ----------
export function poDaftarAktif(saring) {
  const k = kunciPelanggan(saring);
  return (ambilPesanan() || []).filter((p) => p && pesananBelumTuntas(p) && (!k || kunciPelanggan(p.namaPelanggan).indexOf(k) >= 0))
    .map((p) => { const U = poUangMuka(p.id); const baris = poBarisSah(p.baris);
      return { id: String(p.id), nama: p.namaPelanggan || '', isi: baris.length ? poIsiTeks(baris) : (p.isi || ''), katalog: baris.length > 0, baris, alamat: p.alamat || '', noPO: p.noPO || '',
        tanggalKirim: poTanggalSah(p.tanggalKirim) ? String(p.tanggalKirim) : '', nilai: Number(p.nilaiPerkiraan) || 0, status: p.status || 'dipesan', tanggal: p.tanggal || '', jam: p.jam || '',
        catatan: p.catatan || '', dp: U.total, rutin: !!p.jadwalId }; })
    .sort((a, b) => String(a.tanggalKirim || '9999').localeCompare(String(b.tanggalKirim || '9999')) || String(b.id).localeCompare(String(a.id)));
}

// ---------- cek stok (laju jual + pesanan & jadwal yang akan dikirim) ----------
/** Barang stok yang dipakai satu baris: karung & literan langsung → buku kg merek; kemasan → buku unit; literan wadah → tidak dicek (diisi dari karung). */
const poKunciStok = (b) => (b.jalur === 'kemasan' ? { kunci: 'kemasan|' + b.kunci, n: Number(b.jumlah) || 0 } : b.jalur === 'karung' ? { kunci: 'karung|' + b.kunci, n: Number(b.kg) || 0 }
  : b.jalur === 'literan' && !b.wadah ? { kunci: 'karung|' + b.kunci, n: Number(b.kg) || 0 } : null);
/**
 * Kebutuhan stok 14 hari ke depan: pesanan aktif ber-katalog (tanggal kirim kosong = hari ini) + pengingat jadwal yang belum dibuat. → { kunci: [{ hari, n, siapa }] }
 */
export function poKebutuhan(hariIso) {
  const h = poHariKe(hariIso); const out = {}; const sampai = h + PO_JENDELA_STOK_HARI;
  const taruh = (baris, tgl, siapa) => { const hk = Math.max(h, tgl ? poHariKe(tgl) : h); if (hk > sampai) return;
    poBarisSah(baris).forEach((b) => { const s = poKunciStok(b); if (!s || !(s.n > 0)) return; (out[s.kunci] = out[s.kunci] || []).push({ hari: hk - h, n: s.n, siapa }); }); };
  (ambilPesanan() || []).forEach((p) => { if (p && pesananBelumTuntas(p)) taruh(p.baris, poTanggalSah(p.tanggalKirim) ? p.tanggalKirim : '', p.namaPelanggan || 'pesanan'); });
  poJadwalSemua().filter((j) => j.aktif).forEach((j) => poKejadian(j, hariIso, poIso(sampai)).forEach((t) => { if (j.lewati.indexOf(t) < 0 && !poSudahDibuat(j.id, t)) taruh(j.baris, t, j.nama + ' (rutin)'); }));
  return out;
}
/**
 * Peringatan stok untuk pesanan (owner 18 Nov 2026): barang = daftarBarang() layar Stok (sisa & laju jual per hari, kg / unit). Per barang, pada tiap tanggal
 * kirim: perkiraan sisa = sisa sekarang − laju × hari − pesanan sampai hari itu. Kurang = perkiraan terendah di bawah nol.
 * → [{ kunci, nama, satuan, butuh, sisa, laju, kurang, hari (hari kirim yang pertama kurang), siapa[], awas }] — yang kurang dulu, lalu yang cukup.
 */
export function poCekStok(hariIso, barang) {
  const K = poKebutuhan(hariIso); const peta = {}; (barang || []).forEach((b) => { peta[b.jenis + '|' + b.kunci] = b; });
  return Object.keys(K).map((kunci) => {
    const B = peta[kunci] || null; const daftar = K[kunci].slice().sort((a, b) => a.hari - b.hari);
    const sisa = B ? Number(B.sisa) || 0 : 0; const laju = B ? Number(B.laju) || 0 : 0; let jalan = 0; let kurang = 0; let hariKurang = null;
    daftar.forEach((x) => { jalan += x.n; const sisaHari = sisa - laju * x.hari - jalan; if (sisaHari < -1e-6 && -sisaHari > kurang) { kurang = -sisaHari; if (hariKurang === null) hariKurang = x.hari; } });
    const satuan = kunci.indexOf('kemasan|') === 0 ? 'unit' : 'kg';
    const nama = B ? B.nama : kunci.split('|').slice(1).join(' ');
    return { kunci, nama, satuan, butuh: jalan, sisa, laju, kurang: Math.round(kurang * 10) / 10, hari: hariKurang, siapa: daftar.map((x) => x.siapa).filter((s, i, a) => a.indexOf(s) === i), awas: kurang > 0, dikenal: !!B };
  }).sort((a, b) => (b.awas ? 1 : 0) - (a.awas ? 1 : 0) || b.kurang - a.kurang || a.nama.localeCompare(b.nama, 'id'));
}
const poKgTeks = (n, satuan) => (satuan === 'unit' ? Math.ceil(n) + ' unit' : String(Math.round(n * 10) / 10).replace('.', ',') + ' kg');
export function poKataStok(x) {
  if (!x.dikenal) return x.nama + ': belum ada buku stoknya — pesanan ' + poKgTeks(x.butuh, x.satuan);
  const lajuK = x.laju > 0 ? ' · laju jual ' + poKgTeks(x.laju, x.satuan) + '/hari' : '';
  return x.awas ? x.nama + ': KURANG ±' + poKgTeks(x.kurang, x.satuan) + (x.hari === 0 ? ' hari ini' : ' dalam ' + x.hari + ' hari') + ' — pesanan ' + poKgTeks(x.butuh, x.satuan) + ', sisa ' + poKgTeks(x.sisa, x.satuan) + lajuK
    : x.nama + ': cukup — pesanan ' + poKgTeks(x.butuh, x.satuan) + ', sisa ' + poKgTeks(x.sisa, x.satuan) + lajuK;
}

// ==================== LAMA PEMENUHAN PESANAN (paket KPI laba, owner 24 Nov 2026, butir 15) ====================
const poJamKe = (x) => { const t = Date.parse(String(x || '')); return isFinite(t) ? t : null; };
/** Saat pertama sebuah status di riwayatStatus (jam ISO `pada`); 'dipesan' tanpa riwayat = tanggal + jam pesanan (WIB). null = tidak tercatat. */
function poSaat(p, status, terakhir) {
  const rr = (Array.isArray(p.riwayatStatus) ? p.riwayatStatus : []).filter((x) => x && x.status === status && !x.ubah && poJamKe(x.pada) !== null); const r = terakhir ? rr[rr.length - 1] : rr[0];
  if (r) return poJamKe(r.pada);
  if (status === 'dipesan' && /^\d{4}-\d{2}-\d{2}$/.test(String(p.tanggal || ''))) return poJamKe(p.tanggal + 'T' + (/^\d{2}:\d{2}/.test(String(p.jam || '')) ? String(p.jam).slice(0, 5) : '00:00') + ':00+07:00');
  return null;
}
/**
 * Rata-rata lama pesanan dipenuhi, dalam HARI (pecahan, dari jam di riwayat status pesanan): dipesan → DIANTAR dan dipesan → JADI NOTA, atas pesanan yang mencapai
 * status itu dalam N hari terakhir (hari ini ikut). Pesanan batal tidak dihitung; jadi nota = yang sekarang jadi nota (nota yang dibatalkan
 * mengembalikan statusnya), saat jadi nota yang terakhir; pesanan tanpa jam dipesan disebut (tanpaJam), bukan nol. Baca saja.
 */
export function poLamaPenuhi(kini, hari) {
  const akhir = new Date(kini || Date.now()).getTime(); const N = Math.max(7, Math.min(365, Math.round(Number(hari) || 90))); const awal = akhir - N * 86400000;
  const tahap = (status) => { const out = { n: 0, jumlahHari: 0, maks: null, tanpaJam: 0 };
    // jadi nota: hanya pesanan yang SEKARANG jadi nota (nota yang dibatalkan mengembalikan statusnya), saat jadi nota yang TERAKHIR
    ambilPesanan().forEach((p) => { if (!p || p.status === 'batal' || (status === 'dibayar' && p.status !== 'dibayar')) return; const t1 = poSaat(p, status, status === 'dibayar'); if (t1 === null || t1 < awal || t1 > akhir) return; const t0 = poSaat(p, 'dipesan');
      if (t0 === null || t1 < t0) { out.tanpaJam += 1; return; } const h = (t1 - t0) / 86400000; out.n += 1; out.jumlahHari += h; if (out.maks === null || h > out.maks) out.maks = h; });
    return Object.assign(out, { rata: out.n ? out.jumlahHari / out.n : null }); };
  const antar = tahap('diantar'), nota = tahap('dibayar');
  const teks = (x) => (x.rata === null ? '—' : x.rata < 1 / 24 ? 'kurang dari 1 jam' : x.rata < 1 ? '±' + Math.max(1, Math.round(x.rata * 24)) + ' jam' : '±' + String(Math.round(x.rata * 10) / 10).replace('.', ',') + ' hari');
  return { hari: N, antar: Object.assign(antar, { teks: teks(antar) }), nota: Object.assign(nota, { teks: teks(nota) }), keadaan: antar.n || nota.n ? 'ada' : 'kosong',
    kalimat: antar.n || nota.n ? 'Pesanan dipenuhi rata-rata: dipesan → diantar ' + teks(antar) + ' (' + antar.n + ' pesanan) · dipesan → jadi nota ' + teks(nota) + ' (' + nota.n + ' pesanan) — ' + N + ' hari terakhir'
      : 'Belum ada pesanan yang diantar atau jadi nota dalam ' + N + ' hari terakhir' };
}
