// LAYAR STOK — MENCATAT (tanpa DOM): BARANG MASUK (ST1 Kedatangan) dan COCOKKAN (ST3 Opname). Dijaga alat-uji/uji_stok_baru.py.
//
// Bentuk dokumen PERSIS sistem berjalan supaya kedua sistem membaca angka yang sama (mesin beku tidak disentuh):
//   · batchMasuk  {id, tanggal, pemasok, biayaBongkar, caraBayar tunai|utang, merkList[{id, merk, satuan 'karung', jumlahKarung, beratKarung, totalKg,
//                  hargaPerKg, subtotalHarga}]} — simpanKedatangan index.html 12294; upah bongkar dialokasikan ke HPP per kg menurut kg (hitungHppMerkDalamBatch);
//                  'utang' = bon pemasok (hitungUtangPemasok), 'tunai' = keluar laci hari ini; batch fondasi (stokAwal / tutupBuku) tidak diubah/dihapus.
//   · penyesuaianStok     {id, tanggal, jam, merk, kgSistem, kgFisik, selisihKg, alasan, nilaiRp, hppPerKgSaatOpname}         — simpanPenyesuaianStok 29919
//   · penyesuaianKemasan  {id, tanggal, jam, namaProduk, ukuranKemasan, unitSistem, unitFisik, selisihUnit, alasan, nilaiRp, hppPerUnitSaatOpname}
//   · stokBahanKemasan / stokBahanLiteran {id, tipe 'opname', jenis, jumlah (= selisih), hargaTotal 0, tanggal, pcsSistem, pcsFisik, catatan, nilaiRp, hargaPerPcsSaatOpname}
// Nilai rupiah DIKUNCI saat menulis (selisih × modal saat itu) — sejak 1 Sep 2026 selisih KURANG memotong laba lewat baris "Susut & selisih stok",
// selisih LEBIH menaikkan stok tanpa mengubah modal (memori opname-tanpa-rupiah, susut-laba).
// Koleksi BARU milik sistem baru: aturanToko (angka kebijakan owner, id tetap) dan bukuHapus (jejak kedatangan yang dihapus, beralasan).
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungHppMerkDalamBatch } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, kunciKemasan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, cacheMentah, tolakKunci, tolakKunciTanggal } from '../data/toko.js';
import { RP } from '../inti/format.js';
import { hitunganFisik, tumpukanGudang, aturWadah } from './jual-logika.js';

export const ATUR_CATAT_BAWAAN = { minKarung: 60, tempoHari: 21, batasSelisih: 3, ambangSusutPositif: 250000, jendelaGandaMenit: 10 };
// angka ketikan toko: "13.200" = tiga belas ribu dua ratus (titik ribuan), "76,6" = koma desimal; "76.6" (papan tombol HP) = desimal juga — titik dianggap
// ribuan hanya bila polanya persis kelompok tiga digit
const ckAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const ckB2 = (n) => Math.round(n * 100) / 100;
const ckKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const ckKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const ckMenit = (jam) => { const m = /^(\d{1,2})[:.](\d{2})/.exec(String(jam || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };

/** Angka kebijakan owner untuk pencatatan stok (aturanToko/catatStok); belum diatur → bawaan sistem berjalan (60 karung, 21 hari, 3 %, Rp250.000). */
export function aturCatat() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'catatStok') || null;
  const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : ATUR_CATAT_BAWAAN[k]);
  return { minKarung: ambil('minKarung', (n) => n >= 0), tempoHari: ambil('tempoHari', (n) => n >= 0), batasSelisih: ambil('batasSelisih', (n) => n >= 0 && n <= 100),
    ambangSusutPositif: ambil('ambangSusutPositif', (n) => n >= 0), jendelaGandaMenit: ATUR_CATAT_BAWAAN.jendelaGandaMenit, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
export function susunAturCatat(isi, w) {
  const kini = aturCatat(); const baca = (k, syarat, teks) => { if (ckKosong(isi[k])) return { nilai: kini[k] }; const n = ckAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const m = baca('minKarung', (n) => n >= 0 && n <= 1000, 'Minimal karung per mobil harus 0–1000'); if (m.tolak) return { tolak: m.tolak };
  const t = baca('tempoHari', (n) => n >= 0 && n <= 365, 'Tempo bon pemasok harus 0–365 hari'); if (t.tolak) return { tolak: t.tolak };
  const b = baca('batasSelisih', (n) => n >= 0 && n <= 100, 'Batas selisih wajar harus 0–100 %'); if (b.tolak) return { tolak: b.tolak };
  const s = baca('ambangSusutPositif', (n) => n >= 0, 'Ambang stok bertambah tanpa pembelian harus 0 atau lebih'); if (s.tolak) return { tolak: s.tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, minKarung: m.nilai, tempoHari: t.nilai, batasSelisih: b.nilai, ambangSusutPositif: s.nilai } }],
    patch: { kabar: 'Aturan pencatatan disimpan — satu mobil minimal ' + m.nilai + ' karung · tempo bon ' + t.nilai + ' hari · selisih wajar ' + b.nilai + ' % · stok bertambah > ' + RP(s.nilai) + ' ditanya', kabarAwas: false } };
}

// ====================== BARANG MASUK (ST1) ======================
export const BERAT_KARUNG_PILIHAN = [50, 25];
export function barisMasukKosong() { return { merk: '', jumlahKarung: '', beratKarung: 50, hargaPerKg: '' }; }
export function drafMasukKosong(w) { return { id: null, tanggal: w.tanggal, pemasok: '', caraBayar: 'tunai', bongkar: '', baris: [barisMasukKosong()], alasan: '' }; }
const ccFondasi = (b) => !!(b && (b.stokAwal || b.tutupBuku));
/** Nama pemasok yang pernah dipakai, yang terbaru dulu (stok awal / tutup buku tidak ikut). */
export function calonPemasok() {
  const urut = ambilSemuaBatch().slice().sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || ''))); const out = [];
  urut.forEach((b) => { const p = String(b.pemasok || '').trim(); if (p && !ccFondasi(b) && out.indexOf(p) < 0) out.push(p); });
  return out;
}
/** Nama beras yang pernah masuk gudang (sering dulu), untuk pilihan baris — nama baru tetap boleh diketik. */
export function calonMerkMasuk() {
  const hitung = {}; const akhir = {};
  ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (!m.merk || m.bentuk === 'bal') return; hitung[m.merk] = (hitung[m.merk] || 0) + 1; if (!akhir[m.merk] || String(b.tanggal || '') > akhir[m.merk]) akhir[m.merk] = String(b.tanggal || ''); }));
  return Object.keys(hitung).sort((a, b) => akhir[b].localeCompare(akhir[a]) || hitung[b] - hitung[a] || a.localeCompare(b));
}
/** Harga beli per kg terakhir nama itu (dari buku) — pembanding saat mengetik harga. */
export function hargaSebelumnya(merk) { const s = hitungStokKarungPerMerk()[merk]; return s ? (s.hargaTerakhirPerKg || 0) : 0; }
/** Hitung draf: tiap baris kg, subtotal, alokasi bongkar & HPP per kg (rumus hitungHppMerkDalamBatch sistem berjalan) + masalah per baris. */
export function hitungMasuk(draf) {
  const bongkar = ckAngka(draf.bongkar); const baris = (draf.baris || []).map((b, i) => {
    const jumlah = ckAngka(b.jumlahKarung); const berat = ckAngka(b.beratKarung) || 50; const harga = ckAngka(b.hargaPerKg); const merk = String(b.merk || '').trim();
    const terisi = !!merk || jumlah > 0 || harga > 0; const masalah = !terisi ? '' : !merk ? 'nama berasnya belum dipilih' : !(jumlah > 0) ? 'jumlah karungnya belum diisi' : !(harga > 0) ? 'harga beli per kg belum diisi' : '';
    return { ke: i + 1, merk, jumlahKarung: jumlah, beratKarung: berat, hargaPerKg: harga, totalKg: ckB2(jumlah * berat), subtotalHarga: Math.round(jumlah * berat * harga), terisi, masalah, sah: terisi && !masalah,
      hargaLalu: merk ? hargaSebelumnya(merk) : 0 }; });
  const sah = baris.filter((b) => b.sah);
  const hpp = hitungHppMerkDalamBatch(sah.map((b) => ({ merk: b.merk, totalKg: b.totalKg, subtotalHarga: b.subtotalHarga })), bongkar);
  sah.forEach((b, i) => { b.alokasiBongkar = Math.round(hpp[i].alokasiBongkar); b.hppPerKg = hpp[i].hppPerKg; });
  const karung = sah.reduce((a, b) => a + b.jumlahKarung, 0); const kg = ckB2(sah.reduce((a, b) => a + b.totalKg, 0)); const nilaiBeras = sah.reduce((a, b) => a + b.subtotalHarga, 0);
  return { baris, sah, bongkar, karung, kg, nilaiBeras, total: nilaiBeras + bongkar, bermasalah: baris.filter((b) => b.terisi && b.masalah) };
}
/** Susun dokumen kedatangan (baru, atau koreksi bila draf.id menunjuk batch yang ada). yakin = sudah ditanya soal karung sedikit. */
export function susunSimpanMasuk(draf, w, yakin) {
  const atur = aturCatat(); const h = hitungMasuk(draf); const pemasok = String(draf.pemasok || '').trim();
  const lama = draf.id ? ambilSemuaBatch().find((b) => String(b.id) === String(draf.id)) : null;
  if (draf.id && !lama) return { tolak: 'Kedatangan yang dikoreksi sudah tidak ada' };
  if (ccFondasi(lama)) return { tolak: 'Batch fondasi (stok awal / saldo pembuka) menopang seluruh stok & modal — tidak diubah dari sini' };
  if (!pemasok) return { tolak: 'Nama pemasoknya belum diisi' };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(draf.tanggal || ''))) return { tolak: 'Tanggal datangnya belum benar' };
  if (h.bermasalah.length) return { tolak: 'Baris ' + h.bermasalah.map((b) => b.ke + (b.merk ? ' (' + b.merk + ')' : '')).join(', ') + ': ' + h.bermasalah[0].masalah + ' — lengkapi atau kosongkan barisnya' };
  if (!h.sah.length) return { tolak: 'Isi minimal satu baris: nama beras, jumlah karung, dan harga per kg' };
  if (h.bongkar < 0) return { tolak: 'Upah bongkar tidak boleh minus' };
  const kembar = h.sah.find((b, i) => h.sah.findIndex((x) => x.merk === b.merk && x.beratKarung === b.beratKarung) !== i);
  if (kembar) return { tolak: kembar.merk + ' ' + kembar.beratKarung + ' kg tertulis dua kali — gabungkan jadi satu baris' };
  if (h.karung < atur.minKarung && !yakin) return { tolak: 'Cuma ' + h.karung + ' karung — biasanya satu mobil minimal ' + atur.minKarung + ' karung. Ketuk sekali lagi kalau memang benar', perluYakin: true };
  if (lama && ckKosong(draf.alasan)) return { tolak: 'Koreksi kedatangan butuh alasan (mis. salah ketik harga)' };
  // putaran 25: kedatangan bulan terkunci tidak bisa dikoreksi (K2); kedatangan baru tidak boleh bertanggal bulan terkunci
  const kunci = (lama && tolakKunci('batchMasuk', lama, 'kedatangan ini tidak bisa dikoreksi. Jumlah kg yang salah: Stok › Cocokkan HARI INI. harga modal kedatangan bulan terkunci tidak bisa dikoreksi; selisihnya terbawa ke HPP penjualan sisa stoknya (keputusan owner K2)')) || tolakKunciTanggal(draf.tanggal, 'kedatangan tidak bisa dicatat di bulan itu; catat dengan tanggal hari ini dan sebut tanggal aslinya di alasan');
  if (kunci) return { tolak: kunci, pembalik: lama ? 'cocok' : '' };
  const cara = draf.caraBayar === 'utang' ? 'utang' : 'tunai';
  const data = { id: lama ? lama.id : w.idUnik(), tanggal: draf.tanggal, pemasok, biayaBongkar: h.bongkar, caraBayar: cara,
    merkList: h.sah.map((b, i) => ({ id: String(i + 1), merk: b.merk, satuan: 'karung', jumlahKarung: b.jumlahKarung, beratKarung: b.beratKarung, totalKg: b.totalKg, hargaPerKg: b.hargaPerKg, subtotalHarga: b.subtotalHarga })) };
  if (lama) { data.jam = lama.jam || w.jam; data.alasanKoreksi = String(draf.alasan).trim(); data.riwayat = (Array.isArray(lama.riwayat) ? lama.riwayat : []).concat([{ teks: 'dikoreksi: ' + String(draf.alasan).trim(), tanggal: w.tanggal, jam: w.jam }]); Object.keys(lama).forEach((k) => { if (data[k] === undefined && ['oleh', 'perangkat', 'catatan'].indexOf(k) >= 0) data[k] = lama[k]; }); }
  else data.jam = w.jam;
  const tempo = cara === 'utang' && atur.tempoHari > 0 ? ' · jatuh tempo ' + atur.tempoHari + ' hari' : '';
  return { dokumen: [{ koleksi: 'batchMasuk', data }], hitung: h,
    patch: { kabar: (lama ? 'Koreksi tersimpan: ' : 'Barang masuk tersimpan: ') + pemasok + ' · ' + h.karung + ' karung · ' + ckKG(h.kg) + ' · beras ' + RP(h.nilaiBeras) + (h.bongkar ? ' + bongkar ' + RP(h.bongkar) : '')
      + (cara === 'utang' ? ' — jadi bon pemasok' + tempo : ' — tunai, keluar dari laci hari ini') + (h.bongkar ? '; bongkar selalu tunai' : '') + '. Stok & modal tiap nama ikut berubah.', kabarAwas: false } };
}
/** Buku kedatangan: terbaru dulu. */
export function daftarKedatangan(n) {
  const semua = ambilSemuaBatch().slice().sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0));
  return semua.slice(0, n || 30).map((b) => { const baris = (b.merkList || []); const karung = baris.reduce((a, m) => a + (m.satuan === 'karung' ? (Number(m.jumlahKarung) || 0) : 0), 0); const kg = ckB2(baris.reduce((a, m) => a + (Number(m.totalKg) || 0), 0));
    const nilai = baris.reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0);
    return { id: b.id, tanggal: b.tanggal || '', jam: b.jam || '', pemasok: b.pemasok || (b.stokAwal ? 'stok awal' : b.tutupBuku ? 'saldo pembuka' : '—'), karung, kg, nilai, cara: b.caraBayar === 'utang' ? 'utang' : 'tunai', fondasi: ccFondasi(b), adaBal: baris.some((m) => m.bentuk === 'bal'),
      ringkas: baris.map((m) => m.merk + ' ' + (m.bentuk === 'bal' ? (m.jumlahBal || 0) + ' bal' : (m.jumlahKarung || 0) + '×' + (m.beratKarung || '?'))).join(' · '), dikoreksi: !!b.alasanKoreksi, riwayat: Array.isArray(b.riwayat) ? b.riwayat : [] }; });
}
/** Draf koreksi dari batch tersimpan (hanya baris karung; baris bal tidak diubah dari sini). */
export function drafDariKedatangan(id) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return null;
  return { id: b.id, tanggal: b.tanggal || '', pemasok: b.pemasok || '', caraBayar: b.caraBayar === 'utang' ? 'utang' : 'tunai', bongkar: String(b.biayaBongkar || 0),
    baris: (b.merkList || []).filter((m) => m.bentuk !== 'bal').map((m) => ({ merk: m.merk || '', jumlahKarung: String(m.jumlahKarung || ''), beratKarung: Number(m.beratKarung) || 50, hargaPerKg: String(m.hargaPerKg || '') })), alasan: '', fondasi: ccFondasi(b), adaBal: (b.merkList || []).some((m) => m.bentuk === 'bal') };
}
/** Hapus kedatangan: batch + pasangan produksi beli-jadi (dariBatch) dicabut bersama (hapusBatch index.html), jejaknya ke bukuHapus. */
export function susunHapusKedatangan(id, alasan, w) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return { tolak: 'Kedatangan itu sudah tidak ada' };
  if (ccFondasi(b)) return { tolak: 'Batch fondasi (' + (b.tutupBuku ? 'saldo pembuka tutup buku' : 'stok awal') + ') menopang seluruh stok & modal — tidak bisa dihapus dari sini' };
  const kunci = tolakKunci('batchMasuk', b, 'kedatangan ini tidak bisa dihapus. Barang yang tidak pernah ada: Stok › Cocokkan HARI INI (kg turun). Utang/uang yang terlanjur tercatat tidak punya pembetul (K2)'); if (kunci) return { tolak: kunci, pembalik: 'cocok' };   // putaran 25
  if (ckKosong(alasan)) return { tolak: 'Hapus kedatangan butuh alasan — supaya jejaknya bisa dibaca nanti' };
  const pasangan = ambilProduksi().filter((p) => String(p.dariBatch || '') === String(id));
  const k = daftarKedatangan(1e9).find((x) => String(x.id) === String(id));
  return { hapus: [{ koleksi: 'batchMasuk', id: b.id }].concat(pasangan.map((p) => ({ koleksi: 'produksiKemasan', id: p.id }))),
    dokumen: [{ koleksi: 'bukuHapus', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, koleksi: 'batchMasuk', idDok: String(b.id), tanggalDok: b.tanggal || '', pemasok: b.pemasok || '', ringkas: k ? k.ringkas + ' · ' + RP(k.nilai) : '', alasan: String(alasan).trim(), pasangan: pasangan.length } }],
    patch: { kabar: 'Kedatangan ' + (b.pemasok || '') + ' ' + (b.tanggal || '') + ' dihapus (' + String(alasan).trim() + ')' + (pasangan.length ? ' bersama ' + pasangan.length + ' catatan beli-jadi pasangannya' : '') + ' — stok & modal dihitung ulang tanpa kedatangan ini; jejaknya tetap di buku hapus', kabarAwas: false } };
}
export function bukuHapus(n) { return cacheMentah('bukuHapus').slice().sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 10); }

// ====================== COCOKKAN / HITUNG GUDANG (ST3) ======================
export const TAB_COCOK = [['beras', 'Beras (kg)'], ['kemasan', 'Kemasan jadi'], ['kantong', 'Kantong']];
const ccLabelBahan = (j) => LABEL_BAHAN_KEMASAN[j] || LABEL_BAHAN_LITERAN[j] || j;
/** Tanggal+jam hitungan fisik terakhir per kunci (rework karantina bukan hitungan). */
function cocokAkhirPeta() {
  const peta = {}; const catat = (k, d) => { const cap = (d.tanggal || '') + ' ' + (d.jam || ''); if (!peta[k] || cap > peta[k].cap) peta[k] = { cap, tanggal: d.tanggal || '', jam: d.jam || '' }; };
  ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d) && d.merk) catat('beras|' + d.merk, d); });
  ambilPenyesuaianKemasan().forEach((d) => { if (d.namaProduk) catat('kemasan|' + kunciKemasan(d.namaProduk, d.ukuranKemasan), d); });
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && d.jenis) catat('kantong|' + d.jenis, d); });
  return peta;
}
/** Semua barang yang bisa dicocokkan, per tab: {kunci, nama, satuan, sistem, modal, …}. */
export function barangCocok(tab) {
  const out = [];
  if (tab === 'beras') { const st = hitungStokKarungPerMerk(); const atur = aturWadah(); const siap = { stok: st };
    Object.keys(st).sort().forEach((m) => { const t = tumpukanGudang(m, siap); const rincian = t.adaBuku && (t.punyaWadah || t.karungDiketahui) ? 'menurut layar: tumpukan ' + ckKG(t.kg) + ' + karung terbuka ' + ckKG(t.diBelakangKg) + (t.punyaWadah ? ' + wadah ' + ckKG(t.diWadahKg) : '') + ' = ' + ckKG(t.namaKg) : '';
      out.push({ kunci: 'beras|' + m, tab, nama: m, satuan: 'kg', sistem: ckB2(st[m].sisaKg || 0), modal: st[m].hppTerakhirPerKg || 0, rincian, wadah: atur.daftar.indexOf(m) >= 0 }); }); }
  else if (tab === 'kemasan') { const st = hitungStokKemasan(); Object.keys(st).sort().forEach((k) => { const s = st[k]; out.push({ kunci: 'kemasan|' + k, tab, nama: s.namaProduk + ' ' + String(s.ukuranKemasan).replace('.', ',') + ' kg', satuan: 'unit', sistem: s.sisaUnit || 0, modal: s.hppRataRataPerUnit || 0, namaProduk: s.namaProduk, ukuranKemasan: s.ukuranKemasan }); }); }
  else { const k = hitungStokBahanKemasan(); const l = hitungStokBahanLiteran();
    Object.keys(k).sort().forEach((j) => out.push({ kunci: 'kantong|' + j, tab, nama: ccLabelBahan(j), satuan: 'lembar', sistem: k[j].sisaPcs || 0, modal: k[j].hppPerPcs || 0, jenis: j, koleksi: 'stokBahanKemasan' }));
    Object.keys(l).sort().forEach((j) => out.push({ kunci: 'kantong|' + j, tab, nama: ccLabelBahan(j), satuan: 'lembar', sistem: l[j].sisaPcs || 0, modal: l[j].hargaPerPcs || l[j].hppPerPcs || 0, jenis: j, koleksi: 'stokBahanLiteran' })); }
  return out.filter((b) => Math.abs(b.sistem) > 0.004 || b.tab !== 'kantong');
}
/**
 * Susun tab cocokkan: tiap baris dengan hitungan yang sudah dimasukkan (hitung[kunci] = angka) — selisih kg/unit DAN rupiah; tanda besar (> batas % dari sistem,
 * wajib alasan), aneh (lebih dari dua kali tercatat + 10), hitungan fisik terakhir; ringkasan susut/lebih; alasan penolakan simpan.
 */
export function susunCocok(tab, hitung, alasan, yakin) {
  const atur = aturCatat(); const peta = cocokAkhirPeta(); const H = hitung || {}; const A = alasan || {}; const Y = yakin || {};
  const baris = barangCocok(tab).map((b) => { const ada = H[b.kunci] !== undefined && H[b.kunci] !== null && H[b.kunci] !== ''; const dihitung = ada ? ckB2(ckAngka(H[b.kunci])) : null;
    const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = ada ? Math.round(selisih * b.modal) : 0; const akhir = peta[b.kunci] || null;
    const besar = ada && selisih !== 0 && (b.sistem > 0 ? Math.abs(selisih) / b.sistem * 100 > atur.batasSelisih : Math.abs(selisih) > 0);
    const aneh = ada && dihitung > Math.max(0, b.sistem) * 2 + 10;
    return Object.assign({}, b, { ada, dihitung, selisih, rp, besar, aneh, alasan: String(A[b.kunci] || ''), perluAlasan: besar && !String(A[b.kunci] || '').trim(), cocokAkhir: akhir ? akhir.tanggal + (akhir.jam ? ' ' + akhir.jam : '') : '' }); });
  const dihit = baris.filter((b) => b.ada); const belum = baris.filter((b) => !b.ada); const susutRp = dihit.reduce((a, b) => a + (b.rp < 0 ? b.rp : 0), 0); const lebihRp = dihit.reduce((a, b) => a + (b.rp > 0 ? b.rp : 0), 0);
  const kurangAlasan = dihit.filter((b) => b.perluAlasan); const anehDaftar = dihit.filter((b) => b.aneh); const berubah = dihit.filter((b) => b.selisih !== 0);
  let tolak = ''; let perluYakin = '';
  if (!dihit.length) tolak = 'Belum ada yang dihitung — ketuk barangnya lalu isi hasil hitungannya';
  else if (kurangAlasan.length) tolak = kurangAlasan.map((b) => b.nama).join(', ') + ': selisihnya lebih dari ' + atur.batasSelisih + ' % — isi alasannya dulu';
  else if (anehDaftar.length && !Y.aneh) { tolak = 'Angka aneh di ' + anehDaftar.map((b) => b.nama).join(', ') + ' (lebih dari dua kali tercatat) — ketuk sekali lagi kalau memang benar'; perluYakin = 'aneh'; }
  else if (lebihRp > atur.ambangSusutPositif && !Y.susutPositif) { tolak = 'Stok bertambah ' + RP(lebihRp) + ' tanpa pembelian — beras tidak tumbuh sendiri; biasanya timbangan atau catatan masuk yang perlu diperiksa. Ketuk sekali lagi kalau memang benar'; perluYakin = 'susutPositif'; }
  else if (belum.length && !Y.sebagian) { tolak = belum.length + ' barang belum dihitung — simpan yang sudah saja? Ketuk sekali lagi'; perluYakin = 'sebagian'; }
  return { tab, baris, dihitung: dihit.length, semua: baris.length, belum: belum.length, berubah: berubah.length, susutRp, lebihRp, totalRp: susutRp + lebihRp, tolak, perluYakin, batasSelisih: atur.batasSelisih };
}
/** Hitungan fisik dua kali dalam jendela menit yang sama untuk barang yang sama (kejadian Perahu Layar 26 Agu: dua opname bertumpuk). */
function gandaBaruSaja(kunci, w, jendela) {
  const peta = cocokAkhirPeta(); const a = peta[kunci]; if (!a || a.tanggal !== w.tanggal) return false;
  const m1 = ckMenit(a.jam); const m2 = ckMenit(w.jam); return m1 !== null && m2 !== null && Math.abs(m2 - m1) <= jendela;
}
/** Susun dokumen cocokkan untuk semua baris yang dihitung dan selisihnya bukan nol. yakin = {aneh, susutPositif, sebagian, ganda}. */
export function susunSimpanCocok(tab, hitung, alasan, w, yakin) {
  const atur = aturCatat(); const c = susunCocok(tab, hitung, alasan, yakin);
  if (c.tolak) return { tolak: c.tolak, perluYakin: c.perluYakin };
  const berubah = c.baris.filter((b) => b.ada && b.selisih !== 0);
  const ganda = berubah.filter((b) => gandaBaruSaja(b.kunci, w, atur.jendelaGandaMenit));
  if (ganda.length && !(yakin || {}).ganda) return { tolak: ganda.map((b) => b.nama).join(', ') + ' baru saja dicocokkan kurang dari ' + atur.jendelaGandaMenit + ' menit lalu — angka sistemnya sudah termasuk hitungan itu. Ketuk sekali lagi kalau ini memang hitungan baru', perluYakin: 'ganda' };
  const dokumen = berubah.map((b) => { const al = String(b.alasan || '').trim() || 'Cocokkan stok';
    if (b.tab === 'beras') return { koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: b.nama, kgSistem: b.sistem, kgFisik: b.dihitung, selisihKg: b.selisih, alasan: al, nilaiRp: b.rp, hppPerKgSaatOpname: Math.round(b.modal) } };
    if (b.tab === 'kemasan') return { koleksi: 'penyesuaianKemasan', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, namaProduk: b.namaProduk, ukuranKemasan: isFinite(Number(b.ukuranKemasan)) ? Number(b.ukuranKemasan) : b.ukuranKemasan, unitSistem: b.sistem, unitFisik: b.dihitung, selisihUnit: b.selisih, alasan: al, nilaiRp: b.rp, hppPerUnitSaatOpname: Math.round(b.modal) } };
    return { koleksi: b.koleksi, data: { id: w.idUnik(), tipe: 'opname', jenis: b.jenis, jumlah: b.selisih, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: b.sistem, pcsFisik: b.dihitung, catatan: al, nilaiRp: b.rp, hargaPerPcsSaatOpname: Math.round(b.modal) } }; });
  const dampak = w.tanggal < MULAI_SUSUT_LABA ? 'Kas, laba, dan omzet tidak berubah.' : (c.susutRp ? 'Laba bulan ini turun ' + RP(-c.susutRp) + ' lewat baris "Susut & selisih stok". ' : '') + (c.lebihRp ? 'Stok naik ' + RP(c.lebihRp) + ' tanpa mengubah modal per kg. ' : '') + 'Kas dan omzet tidak bergerak.';
  return { dokumen, hitung: c, patch: { kabar: 'Cocokkan tersimpan: ' + c.dihitung + ' barang dihitung, ' + berubah.length + ' berubah' + (c.belum ? ', ' + c.belum + ' belum dihitung' : '') + (dokumen.length ? ' — ' + dampak + ' Stok tercatat kini = hasil hitungan.' : ' — semuanya cocok persis, tidak ada yang ditulis.'), kabarAwas: false } };
}
/** Hitungan fisik sebelumnya (semua jenis), dikelompokkan per tanggal+jam, terbaru dulu. */
export function riwayatCocok(n) {
  const semua = [];
  ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d)) semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.merk, teks: (d.selisihKg > 0 ? '+' : '') + String(Math.round((d.selisihKg || 0) * 100) / 100).replace('.', ',') + ' kg', rp: d.nilaiRp || 0, alasan: d.alasan || '' }); });
  ambilPenyesuaianKemasan().forEach((d) => semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.namaProduk + ' ' + String(d.ukuranKemasan).replace('.', ',') + ' kg', teks: (d.selisihUnit > 0 ? '+' : '') + (d.selisihUnit || 0) + ' unit', rp: d.nilaiRp || 0, alasan: d.alasan || '' }));
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname') semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: ccLabelBahan(d.jenis), teks: (d.jumlah > 0 ? '+' : '') + (d.jumlah || 0) + ' lembar', rp: d.nilaiRp || 0, alasan: d.catatan || '' }); });
  const kel = {}; semua.forEach((x) => { const k = x.tanggal + ' ' + x.jam; if (!kel[k]) kel[k] = { kunci: k, tanggal: x.tanggal, jam: x.jam, baris: [], rp: 0 }; kel[k].baris.push(x); kel[k].rp += x.rp; });
  return Object.keys(kel).sort().reverse().slice(0, n || 8).map((k) => kel[k]);
}
