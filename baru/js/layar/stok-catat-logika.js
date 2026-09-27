// LAYAR STOK — MENCATAT (tanpa DOM): BARANG MASUK (ST1 Kedatangan) dan COCOKKAN (ST3 Opname). Dijaga alat-uji/uji_stok_baru.py.
//
// Bentuk dokumen PERSIS sistem berjalan supaya kedua sistem membaca angka yang sama (mesin beku tidak disentuh):
//   · batchMasuk  {id, tanggal, pemasok, biayaBongkar, caraBayar tunai|utang, merkList[{id, merk, satuan 'karung', jumlahKarung, beratKarung, totalKg,
//                  hargaPerKg, subtotalHarga}]} — simpanKedatangan index.html 12294; upah bongkar dialokasikan ke HPP per kg menurut kg (hitungHppMerkDalamBatch);
//                  'utang' = bon pemasok (hitungUtangPemasok), 'tunai' = keluar laci hari ini; batch fondasi (stokAwal / tutupBuku) tidak diubah/dihapus.
//   · penyesuaianStok     {id, tanggal, jam, merk, kgSistem, kgFisik, selisihKg, alasan, nilaiRp, hppPerKgSaatOpname}         — simpanPenyesuaianStok 29919
//                         putaran 27 (cocokkan DIPISAH, owner 27 Sep: "masing-masing stok punya aturannya sendiri"): + bagian 'tumpukan'|'wadah', wadah,
//                         bagianSistemKg, bagianFisikKg — yang dihitung cuma SATU bagian rantai stok; kgSistem/kgFisik tetap angka buku sebelum/sesudah.
//                         Tumpukan gudang = karung utuh (50 / 25) per nama; wadah literan = isi kotak (takar/liter → kg) + karung terbuka di belakangnya,
//                         selisih wadah dibagi ke MEREK ASAL menurut komposisi tercatat (wadah-bernama-logika.js); susut di bawah batas owner = wajar.
//   · penyesuaianKemasan  {id, tanggal, jam, namaProduk, ukuranKemasan, unitSistem, unitFisik, selisihUnit, alasan, nilaiRp, hppPerUnitSaatOpname}
//   · stokBahanKemasan / stokBahanLiteran {id, tipe 'opname', jenis, jumlah (= selisih), hargaTotal 0, tanggal, pcsSistem, pcsFisik, catatan, nilaiRp, hargaPerPcsSaatOpname}
// Nilai rupiah DIKUNCI saat menulis (selisih × modal saat itu) — sejak 1 Sep 2026 selisih KURANG memotong laba lewat baris "Susut & selisih stok",
// selisih LEBIH menaikkan stok tanpa mengubah modal (memori opname-tanpa-rupiah, susut-laba).
// Koleksi BARU milik sistem baru: aturanToko (angka kebijakan owner, id tetap) dan bukuHapus (jejak kedatangan yang dihapus, beralasan).
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungHppMerkDalamBatch } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, kunciKemasan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilHargaKarung, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, ambilWadahLiteran, cacheMentah, tolakKunci, tolakKunciTanggal } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';
import { hitunganFisik, tumpukanGudang, aturWadah, pindahNama, semuaKarungTerbuka, karungUntukWadah, karungBelakang, beratKarungBuka } from './jual-logika.js';
import { wbKomposisi, wbBagianMerk, wbKomposisiBaru, wbModalPerKg, wbRasio, wbNamaKelas } from './wadah-bernama-logika.js';
import { vrPerluTanya, vrNama, vrDokJenis, vrAda, VR_BATAS_BAWAAN } from './varian-logika.js';
import { arBeras, arKunciBeras, arDokPulihBanyak, arPeta } from './arsip-logika.js';

export const ATUR_CATAT_BAWAAN = { minKarung: 60, tempoHari: 21, batasSelisih: 3, ambangSusutPositif: 250000, jendelaGandaMenit: 10, batasVarian: VR_BATAS_BAWAAN };
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
    ambangSusutPositif: ambil('ambangSusutPositif', (n) => n >= 0), jendelaGandaMenit: ATUR_CATAT_BAWAAN.jendelaGandaMenit, batasVarian: ambil('batasVarian', (n) => n >= 0 && n <= 100), dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
export function susunAturCatat(isi, w) {
  const kini = aturCatat(); const baca = (k, syarat, teks) => { if (ckKosong(isi[k])) return { nilai: kini[k] }; const n = ckAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const m = baca('minKarung', (n) => n >= 0 && n <= 1000, 'Minimal karung per mobil harus 0–1000'); if (m.tolak) return { tolak: m.tolak };
  const t = baca('tempoHari', (n) => n >= 0 && n <= 365, 'Tempo bon pemasok harus 0–365 hari'); if (t.tolak) return { tolak: t.tolak };
  const b = baca('batasSelisih', (n) => n >= 0 && n <= 100, 'Batas selisih wajar harus 0–100 %'); if (b.tolak) return { tolak: b.tolak };
  const s = baca('ambangSusutPositif', (n) => n >= 0, 'Ambang stok bertambah tanpa pembelian harus 0 atau lebih'); if (s.tolak) return { tolak: s.tolak };
  const v = baca('batasVarian', (n) => n >= 0 && n <= 100, 'Batas beda harga beli (varian) harus 0–100 %'); if (v.tolak) return { tolak: v.tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, minKarung: m.nilai, tempoHari: t.nilai, batasSelisih: b.nilai, ambangSusutPositif: s.nilai, batasVarian: v.nilai } }],
    patch: { kabar: 'Aturan pencatatan disimpan — satu mobil minimal ' + m.nilai + ' karung · tempo bon ' + t.nilai + ' hari · selisih wajar ' + b.nilai + ' % · stok bertambah > ' + RP(s.nilai) + ' ditanya · harga beli beda > ' + v.nilai + ' % ditanya "sama barangnya / beda mutu"', kabarAwas: false } };
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
  // putaran 27: varian yang dibuat dari Harga & Pemasok sebelum barangnya datang (katalog per kg tanpa kedatangan) ikut ditawarkan
  ambilHargaKarung().forEach((h) => { if (h.merk && hitung[h.merk] === undefined && String(h.merk).indexOf('\u00b7') >= 0) { hitung[h.merk] = 0; akhir[h.merk] = ''; } });
  const arsip = arPeta();   // putaran 27: nama yang diarsipkan tidak ditawarkan (tetap boleh diketik — layar lalu bertanya pulihkan / varian)
  const kelas = wbNamaKelas();   // putaran 27 (Bagian 5): nama wadah / kelas mutu tidak ditawarkan — barang masuk dibukukan per merek karung
  return Object.keys(hitung).filter((m) => !arsip[arKunciBeras(m)] && !kelas[m]).sort((a, b) => akhir[b].localeCompare(akhir[a]) || hitung[b] - hitung[a] || a.localeCompare(b));
}
/** Harga beli per kg terakhir nama itu (dari buku) — pembanding saat mengetik harga. */
export function hargaSebelumnya(merk) { const s = hitungStokKarungPerMerk()[merk]; return s ? (s.hargaTerakhirPerKg || 0) : 0; }
/** Hitung draf: tiap baris kg, subtotal, alokasi bongkar & HPP per kg (rumus hitungHppMerkDalamBatch sistem berjalan) + masalah per baris. */
export function hitungMasuk(draf) {
  // putaran 27 (Bagian 5, owner 27 Sep): nama WADAH / kelas mutu (IR64 Apex dkk.) tidak pernah lagi dibukukan lewat barang masuk — kecuali nama wadah yang
  // sekaligus merek karung pemasok (Aturan wadah). Koreksi kedatangan lama boleh tetap memakai nama yang sudah tertulis di kedatangan itu.
  const kelas = wbNamaKelas(); const lamaB = draf.id ? ambilSemuaBatch().find((x) => String(x.id) === String(draf.id)) : null;
  const namaLama = {}; ((lamaB && lamaB.merkList) || []).forEach((m) => { if (m.merk) namaLama[m.merk] = true; });
  const bongkar = ckAngka(draf.bongkar); const baris = (draf.baris || []).map((b, i) => {
    const jumlah = ckAngka(b.jumlahKarung); const berat = ckAngka(b.beratKarung) || 50; const harga = ckAngka(b.hargaPerKg); const merk = String(b.merk || '').trim();
    const terisi = !!merk || jumlah > 0 || harga > 0; const masalah = !terisi ? '' : !merk ? 'nama berasnya belum dipilih' : kelas[merk.split(' \u00b7 ')[0]] && !namaLama[merk] ? merk + ' itu nama WADAH / kelas mutu, bukan merek karung — tulis merek yang tertera di karungnya'
      : !(jumlah > 0) ? 'jumlah karungnya belum diisi' : !(harga > 0) ? 'harga beli per kg belum diisi' : '';
    // putaran 27 (Bagian 2): nama yang sudah punya buku & harga beli beda > batas dari modal berjalan → "sama barangnya / beda mutu?" (koreksi tidak ditanya)
    const vr = !draf.id && terisi && !masalah ? vrPerluTanya(merk, harga) : { perlu: false };
    // putaran 27 (Bagian 3): nama yang DIARSIPKAN datang lagi → wajib dijawab: pulihkan (sama barangnya) atau jadi varian
    const diArsip = !draf.id && terisi && !masalah && arBeras(merk); if (diArsip) vr.arsip = true;
    const pilih = b.varian === 'sama' || b.varian === 'beda' ? b.varian : ''; const merkSimpan = pilih === 'beda' ? vrNama(merk, b.namaMutu, draf.tanggal) : merk;
    return { ke: i + 1, merk, merkSimpan, varian: pilih, namaMutu: String(b.namaMutu || ''), vr, jumlahKarung: jumlah, beratKarung: berat, hargaPerKg: harga, totalKg: ckB2(jumlah * berat), subtotalHarga: Math.round(jumlah * berat * harga), terisi, masalah, sah: terisi && !masalah,
      hargaLalu: merk ? hargaSebelumnya(merk) : 0 }; });
  const sah = baris.filter((b) => b.sah);
  const hpp = hitungHppMerkDalamBatch(sah.map((b) => ({ merk: b.merkSimpan, totalKg: b.totalKg, subtotalHarga: b.subtotalHarga })), bongkar);
  sah.forEach((b, i) => { b.alokasiBongkar = Math.round(hpp[i].alokasiBongkar); b.hppPerKg = hpp[i].hppPerKg; });
  const karung = sah.reduce((a, b) => a + b.jumlahKarung, 0); const kg = ckB2(sah.reduce((a, b) => a + b.totalKg, 0)); const nilaiBeras = sah.reduce((a, b) => a + b.subtotalHarga, 0);
  return { baris, sah, bongkar, karung, kg, nilaiBeras, total: nilaiBeras + bongkar, bermasalah: baris.filter((b) => b.terisi && b.masalah), tanyaVarian: sah.filter((b) => (b.vr.perlu || b.vr.arsip) && !b.varian) };
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
  if (h.tanyaVarian.length && h.tanyaVarian[0].vr.arsip) { const x = h.tanyaVarian[0]; return { tolak: 'Baris ' + x.ke + ': ' + x.merk + ' sudah DIARSIPKAN — pilih dulu: PULIHKAN ' + x.merk + ' (sama barangnya, namanya tampil lagi) atau BEDA MUTU (jadi varian sendiri)', perluVarian: x.ke }; }
  if (h.tanyaVarian.length) { const x = h.tanyaVarian[0]; return { tolak: 'Baris ' + x.ke + ' (' + x.merk + '): harga beli ' + RP(x.hargaPerKg) + '/kg beda ' + String(x.vr.beda).replace('.', ',') + ' % dari modal ' + x.merk + ' ' + RP(Math.round(x.vr.modal)) + '/kg (batas ' + x.vr.batas + ' %) — pilih dulu: SAMA barangnya (gabung, modal dirata-rata) atau BEDA MUTU (jadi varian sendiri)', perluVarian: x.ke }; }
  const beda = h.sah.filter((b) => b.varian === 'beda');
  const salahMutu = beda.find((b) => String(b.namaMutu || '').indexOf('\u00b7') >= 0); if (salahMutu) return { tolak: 'Baris ' + salahMutu.ke + ': nama mutu tidak boleh memakai titik tengah' };
  const kembar = h.sah.find((b, i) => h.sah.findIndex((x) => x.merkSimpan === b.merkSimpan && x.beratKarung === b.beratKarung) !== i);
  if (kembar) return { tolak: kembar.merkSimpan + ' ' + kembar.beratKarung + ' kg tertulis dua kali — gabungkan jadi satu baris' };
  if (h.karung < atur.minKarung && !yakin) return { tolak: 'Cuma ' + h.karung + ' karung — biasanya satu mobil minimal ' + atur.minKarung + ' karung. Ketuk sekali lagi kalau memang benar', perluYakin: true };
  if (lama && ckKosong(draf.alasan)) return { tolak: 'Koreksi kedatangan butuh alasan (mis. salah ketik harga)' };
  // putaran 25: kedatangan bulan terkunci tidak bisa dikoreksi (K2); kedatangan baru tidak boleh bertanggal bulan terkunci
  const kunci = (lama && tolakKunci('batchMasuk', lama, 'kedatangan ini tidak bisa dikoreksi. Jumlah kg yang salah: Stok › Cocokkan HARI INI. harga modal kedatangan bulan terkunci tidak bisa dikoreksi; selisihnya terbawa ke HPP penjualan sisa stoknya (keputusan owner K2)')) || tolakKunciTanggal(draf.tanggal, 'kedatangan tidak bisa dicatat di bulan itu; catat dengan tanggal hari ini dan sebut tanggal aslinya di alasan');
  if (kunci) return { tolak: kunci, pembalik: lama ? 'cocok' : '' };
  const cara = draf.caraBayar === 'utang' ? 'utang' : 'tunai';
  const data = { id: lama ? lama.id : w.idUnik(), tanggal: draf.tanggal, pemasok, biayaBongkar: h.bongkar, caraBayar: cara,
    merkList: h.sah.map((b, i) => ({ id: String(i + 1), merk: b.merkSimpan, satuan: 'karung', jumlahKarung: b.jumlahKarung, beratKarung: b.beratKarung, totalKg: b.totalKg, hargaPerKg: b.hargaPerKg, subtotalHarga: b.subtotalHarga })) };
  if (lama) { data.jam = lama.jam || w.jam; data.alasanKoreksi = String(draf.alasan).trim(); data.riwayat = (Array.isArray(lama.riwayat) ? lama.riwayat : []).concat([{ teks: 'dikoreksi: ' + String(draf.alasan).trim(), tanggal: w.tanggal, jam: w.jam }]); Object.keys(lama).forEach((k) => { if (data[k] === undefined && ['oleh', 'perangkat', 'catatan'].indexOf(k) >= 0) data[k] = lama[k]; }); }
  else data.jam = w.jam;
  const tempo = cara === 'utang' && atur.tempoHari > 0 ? ' · jatuh tempo ' + atur.tempoHari + ' hari' : '';
  // varian: jenis beras ikut induknya (satu kunci baru di peta yang sama); harga jualnya ditawarkan layar sesudah tersimpan
  const dokumen = [{ koleksi: 'batchMasuk', data }]; const dj = vrDokJenis(beda.map((b) => ({ varian: b.merkSimpan, induk: b.merk })), w); if (dj) dokumen.push(dj);
  // nama arsip yang dijawab "sama barangnya" dipulihkan di kiriman yang sama (juga varian yang pernah diarsipkan lalu datang lagi)
  const arsip = arPeta(); const pulih = h.sah.filter((b) => arsip[arKunciBeras(b.merkSimpan)]).map((b) => arKunciBeras(b.merkSimpan)); const dp = arDokPulihBanyak(pulih, w); if (dp) dokumen.push(dp);
  const varianBaru = beda.filter((b, i) => beda.findIndex((x) => x.merkSimpan === b.merkSimpan) === i).map((b) => ({ merk: b.merkSimpan, induk: b.merk, hargaBeli: b.hargaPerKg, modalKg: b.hppPerKg, baru: !vrAda(b.merkSimpan) }));
  return { dokumen, hitung: h, varianBaru,
    patch: { varianTawar: varianBaru.length ? varianBaru : null, kabar: (lama ? 'Koreksi tersimpan: ' : 'Barang masuk tersimpan: ') + pemasok + ' · ' + h.karung + ' karung · ' + ckKG(h.kg) + ' · beras ' + RP(h.nilaiBeras) + (h.bongkar ? ' + bongkar ' + RP(h.bongkar) : '')
      + (cara === 'utang' ? ' — jadi bon pemasok' + tempo : ' — tunai, keluar dari laci hari ini') + (h.bongkar ? '; bongkar selalu tunai' : '') + '. Stok & modal tiap nama ikut berubah.'
      + (varianBaru.length ? ' Varian: ' + varianBaru.map((x) => x.merk + (x.baru ? ' (nama baru, jenis beras ikut ' + x.induk + ')' : ' (gabung ke varian yang sudah ada)')).join(', ') + ' — kolam lama tidak disentuh.' : '')
      + (dp ? ' Dipulihkan dari arsip: ' + pulih.map((k) => k.slice(2)).join(', ') + '.' : ''), kabarAwas: false } };
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
export const TAB_COCOK = [['tumpukan', 'Tumpukan gudang'], ['wadah', 'Wadah literan'], ['kemasan', 'Kemasan jadi'], ['kantong', 'Kantong']];
/** Draf hitungan lama (tab 'beras', satu angka per nama untuk tumpukan + karung terbuka + wadah sekaligus) dibuka di tab tumpukan; angka lamanya tidak dipakai. */
export const tabCocokSah = (tab) => (TAB_COCOK.some((x) => x[0] === tab) ? tab : 'tumpukan');
const ccLabelBahan = (j) => LABEL_BAHAN_KEMASAN[j] || LABEL_BAHAN_LITERAN[j] || j;
/** Tanggal+jam hitungan fisik terakhir per kunci (rework karantina bukan hitungan). */
function cocokAkhirPeta() {
  const peta = {}; const catat = (k, d) => { const cap = (d.tanggal || '') + ' ' + (d.jam || ''); if (!peta[k] || cap > peta[k].cap) peta[k] = { cap, tanggal: d.tanggal || '', jam: d.jam || '' }; };
  // putaran 27: hitungan tumpukan (dan hitungan lama satu angka per nama) per nama; hitungan wadah = titik samakan wadah itu (dokumen 'isi')
  ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d) && d.merk && d.bagian !== 'wadah') catat('tumpukan|' + d.merk, d); });
  ambilWadahLiteran().forEach((d) => { if (d.tipe === 'isi' && d.wadah) catat('wadah|' + d.wadah, d); });
  ambilPenyesuaianKemasan().forEach((d) => { if (d.namaProduk) catat('kemasan|' + kunciKemasan(d.namaProduk, d.ukuranKemasan), d); });
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && d.jenis) catat('kantong|' + d.jenis, d); });
  return peta;
}
/** Semua barang yang bisa dicocokkan, per tab: {kunci, nama, satuan, sistem, modal, …}. */
export function barangCocok(tab) {
  const out = [];
  if (tab === 'tumpukan') { const st = hitungStokKarungPerMerk(); const siap = { stok: st, pindah: pindahNama(), kolam: semuaKarungTerbuka(), bagian: wbBagianMerk() };
    // TUMPUKAN GUDANG: yang dihitung cuma karung utuh (50 / 25 kg) per nama. Tercatat = buku − karung terbuka − bagian nama ini di wadah (rantai stok).
    Object.keys(st).sort().forEach((m) => { const t = tumpukanGudang(m, siap);
      const rincian = 'buku ' + ckKG(st[m].sisaKg || 0) + (Math.abs(t.diBelakangKg) > 0.004 ? ' − karung terbuka ' + ckKG(t.diBelakangKg) : '') + (Math.abs(t.diWadahKg) > 0.004 ? ' − di wadah ' + ckKG(t.diWadahKg) : '')
        + (t.pindahKeluarKg ? ' − pindah nama ' + ckKG(t.pindahKeluarKg) : '') + (t.pindahMasukKg ? ' + pindah nama ' + ckKG(t.pindahMasukKg) : '') + ' = tumpukan ' + ckKG(t.kg) + ' (±' + t.karung + ' karung ' + t.beratKarung + ' kg)'
        + (t.lengkap ? '' : ' · perkiraan: ada wadah / karung terbuka yang belum ditandai');
      out.push({ kunci: 'tumpukan|' + m, tab, nama: m, satuan: 'kg', sistem: ckB2(t.kg), buku: ckB2(st[m].sisaKg || 0), modal: st[m].hppTerakhirPerKg || 0, rincian, lengkap: t.lengkap,
        beratKarung: t.beratKarung, karungSistem: t.karung }); }); }
  else if (tab === 'wadah') { const atur = aturWadah();
    // WADAH LITERAN: per petak W1–W8 — isi kotak + karung terbuka di belakangnya. Tercatat isi = Σ komposisi (merek asal); belum pernah disamakan = null (tidak ditebak).
    atur.daftar.forEach((W, i) => { const K = wbKomposisi(W); const kn = karungUntukWadah(W); const kb = karungBelakang(kn.merk, W);
      const isiSistem = K.diketahui ? ckB2(K.totalKg) : null; const karungSistem = kb.diketahui ? ckB2(kb.sisaMentahKg) : null;
      out.push({ kunci: 'wadah|' + W, kunciKarung: 'wadahKarung|' + W, tab, nama: W, no: 'W' + (i + 1), satuan: 'kg', isiSistem, karungNama: kn.merk, karungDicatat: kn.dariCatatan, karungSistem,
        karungPenuh: kb.penuhKg || beratKarungBuka(kn.merk), komposisi: K.positif, sejak: K.sejak, sistem: ckB2((isiSistem || 0) + (karungSistem || 0)), modal: wbModalPerKg(W),
        takarKg: atur.takarKg, rasio: wbRasio(W), puncakKg: atur.puncakKg, susutWajarKg: atur.susutWajarKg }); }); }
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
  if (tab === 'wadah') return ccSusunWadah(hitung, alasan, yakin);
  const atur = aturCatat(); const peta = cocokAkhirPeta(); const H = hitung || {}; const A = alasan || {}; const Y = yakin || {};
  const baris = barangCocok(tab).map((b) => { const ada = H[b.kunci] !== undefined && H[b.kunci] !== null && H[b.kunci] !== ''; const dihitung = ada ? ckB2(ckAngka(H[b.kunci])) : null;
    const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = ada ? Math.round(selisih * b.modal) : 0; const akhir = peta[b.kunci] || null;
    const besar = ada && selisih !== 0 && (b.sistem > 0 ? Math.abs(selisih) / b.sistem * 100 > atur.batasSelisih : Math.abs(selisih) > 0);
    const aneh = ada && dihitung > Math.max(0, b.sistem) * 2 + 10;
    return Object.assign({}, b, { ada, dihitung, selisih, rp, besar, aneh, alasan: String(A[b.kunci] || ''), perluAlasan: besar && !String(A[b.kunci] || '').trim(), cocokAkhir: akhir ? akhir.tanggal + (akhir.jam ? ' ' + akhir.jam : '') : '' }); });
  const dihit = baris.filter((b) => b.ada); const belum = baris.filter((b) => !b.ada); const susutRp = dihit.reduce((a, b) => a + (b.rp < 0 ? b.rp : 0), 0); const lebihRp = dihit.reduce((a, b) => a + (b.rp > 0 ? b.rp : 0), 0);
  const kurangAlasan = dihit.filter((b) => b.perluAlasan); const anehDaftar = dihit.filter((b) => b.aneh); const berubah = dihit.filter((b) => b.selisih !== 0);
  const p = ccPenjaga(atur, dihit, kurangAlasan, anehDaftar, lebihRp, belum, Y, kurangAlasan.map((b) => b.nama).join(', ') + ': selisihnya lebih dari ' + atur.batasSelisih + ' % — isi alasannya dulu', '(lebih dari dua kali tercatat)');
  return { tab, baris, dihitung: dihit.length, semua: baris.length, belum: belum.length, berubah: berubah.length, susutRp, lebihRp, totalRp: susutRp + lebihRp, tolak: p.tolak, perluYakin: p.perluYakin, batasSelisih: atur.batasSelisih };
}
/** Urutan penjaga simpan cocokkan (sama untuk semua tab): kosong → alasan → angka aneh → stok bertambah > ambang → sebagian. */
function ccPenjaga(atur, dihit, kurangAlasan, anehDaftar, lebihRp, belum, Y, teksAlasan, teksAneh) {
  let tolak = ''; let perluYakin = '';
  if (!dihit.length) tolak = 'Belum ada yang dihitung — ketuk barangnya lalu isi hasil hitungannya';
  else if (kurangAlasan.length) tolak = teksAlasan;
  else if (anehDaftar.length && !Y.aneh) { tolak = 'Angka aneh di ' + anehDaftar.map((b) => b.nama).join(', ') + ' ' + teksAneh + ' — ketuk sekali lagi kalau memang benar'; perluYakin = 'aneh'; }
  else if (lebihRp > atur.ambangSusutPositif && !Y.susutPositif) { tolak = 'Stok bertambah ' + RP(lebihRp) + ' tanpa pembelian — beras tidak tumbuh sendiri; biasanya timbangan atau catatan masuk yang perlu diperiksa. Ketuk sekali lagi kalau memang benar'; perluYakin = 'susutPositif'; }
  else if (belum.length && !Y.sebagian) { tolak = belum.length + ' barang belum dihitung — simpan yang sudah saja? Ketuk sekali lagi'; perluYakin = 'sebagian'; }
  return { tolak, perluYakin };
}
const ccAda = (v) => v !== undefined && v !== null && String(v).trim() !== '';
const ccHariAntara = (dari, ke) => (dari && ke ? Math.round((new Date(ke + 'T00:00:00') - new Date(dari + 'T00:00:00')) / 86400000) : 0);
/**
 * TAB WADAH: tiap petak = isi kotak (kg; layar mengubah takar/liter ke kg) + karung terbuka di belakangnya (kg sisa). Selisih isi dibagi ke merek asal
 * menurut komposisi tercatat (wbKomposisiBaru), selisih karung = merek karung itu. SUSUT WAJAR = batas owner (Aturan wadah) × hari sejak wadah ini
 * terakhir disamakan (paling sedikit 1 hari): selisih kurang di dalamnya tidak minta alasan; di atasnya (kurang ATAU lebih) wajib alasan.
 * Isi ulang yang lupa dicatat (wadah lebih + karung kurang, atau wadah tercatat minus) DITAWARKAN dicatat sebagai takar dulu.
 * Yang belum pernah ditandai (tercatat null) = hitungan pertama: tanpa selisih, cuma jadi titik awal.
 */
function ccSusunWadah(hitung, alasan, yakin) {
  const atur = aturCatat(); const peta = cocokAkhirPeta(); const H = hitung || {}; const A = alasan || {}; const Y = yakin || {}; const stok = hitungStokKarungPerMerk(); const hari = hariIniIso(new Date(Date.now()));
  const modal = (m) => (stok[m] || {}).hppTerakhirPerKg || 0;
  const baris = barangCocok('wadah').map((b) => {
    const adaIsi = ccAda(H[b.kunci]); const adaKr = ccAda(H[b.kunciKarung]); const ada = adaIsi || adaKr;
    const isiH = adaIsi ? ckB2(ckAngka(H[b.kunci])) : null; const krH = adaKr ? ckB2(ckAngka(H[b.kunciKarung])) : null;
    const alokasi = {}; const tambah = (m, kg) => { if (!m || !kg) return; alokasi[m] = ckB2((alokasi[m] || 0) + kg); };
    let komposisiBaru = null;
    if (adaIsi) { const kb = wbKomposisiBaru(b.nama, isiH); komposisiBaru = kb.komposisi; if (b.isiSistem !== null) Object.keys(kb.alokasi).forEach((m) => tambah(m, kb.alokasi[m])); }
    const dIsi = adaIsi && b.isiSistem !== null ? ckB2(isiH - b.isiSistem) : 0; const dKr = adaKr && b.karungSistem !== null ? ckB2(krH - b.karungSistem) : 0;
    if (dKr) tambah(b.karungNama, dKr);
    Object.keys(alokasi).forEach((m) => { if (Math.abs(alokasi[m]) < 0.005) delete alokasi[m]; });
    const selisih = ckB2(Object.keys(alokasi).reduce((a, m) => a + alokasi[m], 0)); const rp = Math.round(Object.keys(alokasi).reduce((a, m) => a + alokasi[m] * modal(m), 0));
    const lamaHari = Math.max(1, ccHariAntara(b.sejak, hari)); const wajarKg = ckB2(b.susutWajarKg * lamaHari);
    const besar = ada && Math.abs(selisih) > wajarKg + 0.0001; const wajar = ada && selisih < 0 && !besar;
    const aneh = ada && ((isiH !== null && isiH > b.puncakKg + 5) || (krH !== null && krH > b.karungPenuh + 1));
    let lupaKg = 0;
    if (b.isiSistem !== null && b.karungSistem !== null && adaIsi && adaKr && dIsi > b.takarKg / 2 && dKr < -b.takarKg / 2) lupaKg = Math.min(dIsi, -dKr);
    else if (b.isiSistem !== null && b.isiSistem < -0.0001) lupaKg = -b.isiSistem;
    const lupaTakar = lupaKg > 0 ? Math.max(1, Math.round(lupaKg / b.takarKg)) : 0;
    const pertama = (adaIsi && b.isiSistem === null) || (adaKr && b.karungSistem === null);
    const akhir = peta[b.kunci] || null;
    return Object.assign({}, b, { ada, isiH, krH, dihitung: ckB2((isiH !== null ? isiH : (b.isiSistem || 0)) + (krH !== null ? krH : (b.karungSistem || 0))), dIsi, dKr, alokasi, komposisiBaru, selisih, rp,
      besar, wajar, wajarKg, lamaHari, aneh, lupaKg: ckB2(lupaKg), lupaTakar, pertama, alasan: String(A[b.kunci] || ''), perluAlasan: besar && !String(A[b.kunci] || '').trim(), cocokAkhir: akhir ? akhir.tanggal + (akhir.jam ? ' ' + akhir.jam : '') : '' }); });
  const dihit = baris.filter((b) => b.ada); const belum = baris.filter((b) => !b.ada); const susutRp = dihit.reduce((a, b) => a + (b.rp < 0 ? b.rp : 0), 0); const lebihRp = dihit.reduce((a, b) => a + (b.rp > 0 ? b.rp : 0), 0);
  const kurangAlasan = dihit.filter((b) => b.perluAlasan); const anehDaftar = dihit.filter((b) => b.aneh);
  const p = ccPenjaga(atur, dihit, kurangAlasan, anehDaftar, lebihRp, belum, Y, kurangAlasan.map((b) => 'wadah ' + b.nama + ' selisih ' + ckKG(b.selisih) + ', di atas susut wajar ' + ckKG(b.wajarKg)).join('; ') + ' — isi alasannya dulu', '(melebihi isi kotak / isi karung)');
  return { tab: 'wadah', baris, dihitung: dihit.length, semua: baris.length, belum: belum.length, berubah: dihit.length, susutRp, lebihRp, totalRp: susutRp + lebihRp,
    tolak: p.tolak, perluYakin: p.perluYakin, batasSelisih: atur.batasSelisih };
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
  const berubah = c.baris.filter((b) => b.ada && (b.selisih !== 0 || tab === 'wadah'));   // wadah: hitungan yang cocok persis tetap jadi titik samakan
  const ganda = berubah.filter((b) => gandaBaruSaja(b.kunci, w, atur.jendelaGandaMenit));
  if (ganda.length && !(yakin || {}).ganda) return { tolak: ganda.map((b) => b.nama).join(', ') + ' baru saja dicocokkan kurang dari ' + atur.jendelaGandaMenit + ' menit lalu — angka sistemnya sudah termasuk hitungan itu. Ketuk sekali lagi kalau ini memang hitungan baru', perluYakin: 'ganda' };
  if (tab === 'wadah') return ccSimpanWadah(c, berubah, w);
  const dokumen = berubah.map((b) => { const al = String(b.alasan || '').trim() || 'Cocokkan stok';
    // putaran 27: yang dihitung cuma TUMPUKAN — kgSistem/kgFisik = buku sebelum/sesudah (mesin membaca selisihKg), bagian*Kg = tumpukan tercatat/dihitung
    if (b.tab === 'tumpukan') return { koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: b.nama, kgSistem: b.buku, kgFisik: ckB2(b.buku + b.selisih), selisihKg: b.selisih, alasan: al, nilaiRp: b.rp, hppPerKgSaatOpname: Math.round(b.modal),
      bagian: 'tumpukan', bagianSistemKg: b.sistem, bagianFisikKg: b.dihitung } };
    if (b.tab === 'kemasan') return { koleksi: 'penyesuaianKemasan', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, namaProduk: b.namaProduk, ukuranKemasan: isFinite(Number(b.ukuranKemasan)) ? Number(b.ukuranKemasan) : b.ukuranKemasan, unitSistem: b.sistem, unitFisik: b.dihitung, selisihUnit: b.selisih, alasan: al, nilaiRp: b.rp, hppPerUnitSaatOpname: Math.round(b.modal) } };
    return { koleksi: b.koleksi, data: { id: w.idUnik(), tipe: 'opname', jenis: b.jenis, jumlah: b.selisih, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: b.sistem, pcsFisik: b.dihitung, catatan: al, nilaiRp: b.rp, hargaPerPcsSaatOpname: Math.round(b.modal) } }; });
  const dampak = w.tanggal < MULAI_SUSUT_LABA ? 'Kas, laba, dan omzet tidak berubah.' : (c.susutRp ? 'Laba bulan ini turun ' + RP(-c.susutRp) + ' lewat baris "Susut & selisih stok". ' : '') + (c.lebihRp ? 'Stok naik ' + RP(c.lebihRp) + ' tanpa mengubah modal per kg. ' : '') + 'Kas dan omzet tidak bergerak.';
  return { dokumen, hitung: c, patch: { kabar: 'Cocokkan tersimpan: ' + c.dihitung + ' barang dihitung, ' + berubah.length + ' berubah' + (c.belum ? ', ' + c.belum + ' belum dihitung' : '') + (dokumen.length ? ' — ' + dampak + ' Stok tercatat kini = hasil hitungan.' : ' — semuanya cocok persis, tidak ada yang ditulis.'), kabarAwas: false } };
}
/** Simpan cocokkan wadah: penyesuaianStok per merek asal (bagian 'wadah') + titik samakan isi (komposisi baru) & karung terbuka, satu kiriman. */
function ccSimpanWadah(c, berubah, w) {
  const stok = hitungStokKarungPerMerk(); const jalan = {}; const dokumen = []; let nMerk = 0;
  berubah.forEach((b) => { const al = String(b.alasan || '').trim() || (b.wajar ? 'Susut takar wajar' : 'Cocokkan wadah');
    Object.keys(b.alokasi).sort().forEach((m) => { const sel = b.alokasi[m]; const st = stok[m]; if (!st || Math.abs(sel) < 0.005) return;
      const kgS = jalan[m] !== undefined ? jalan[m] : ckB2(st.sisaKg || 0); jalan[m] = ckB2(kgS + sel); nMerk += 1;
      dokumen.push({ koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: m, kgSistem: kgS, kgFisik: jalan[m], selisihKg: sel, alasan: al, nilaiRp: Math.round(sel * (st.hppTerakhirPerKg || 0)),
        hppPerKgSaatOpname: Math.round(st.hppTerakhirPerKg || 0), bagian: 'wadah', wadah: b.nama, bagianSistemKg: b.sistem, bagianFisikKg: b.dihitung } }); });
    if (b.isiH !== null) dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: b.nama, tipe: 'isi', isiKg: b.isiH, komposisi: b.komposisiBaru || {}, dariCocok: true } });
    if (b.krH !== null && b.karungNama) dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: b.karungNama, isiKg: b.krH, wadah: b.nama, dariCocok: true } }); });
  const dampak = w.tanggal < MULAI_SUSUT_LABA ? 'Kas, laba, dan omzet tidak berubah.' : (c.susutRp ? 'Laba bulan ini turun ' + RP(-c.susutRp) + ' lewat baris "Susut & selisih stok". ' : '') + (c.lebihRp ? 'Stok naik ' + RP(c.lebihRp) + ' tanpa mengubah modal per kg. ' : '') + 'Kas dan omzet tidak bergerak.';
  return { dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: ' + berubah.length + ' wadah dihitung' + (c.belum ? ', ' + c.belum + ' belum' : '') + ' — ' + (nMerk ? nMerk + ' buku merek asal disesuaikan. ' + dampak : 'tidak ada buku yang berubah (cocok, susut nol, atau hitungan pertama).') + ' Isi wadah & karung terbuka kini = hitungan.', kabarAwas: false } };
}
/** Hitungan fisik sebelumnya (semua jenis), dikelompokkan per tanggal+jam, terbaru dulu. */
export function riwayatCocok(n) {
  const semua = [];
  ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d)) semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.merk + (d.bagian === 'wadah' ? ' (wadah ' + (d.wadah || '') + ')' : d.bagian === 'tumpukan' ? ' (tumpukan)' : ''), teks: (d.selisihKg > 0 ? '+' : '') + String(Math.round((d.selisihKg || 0) * 100) / 100).replace('.', ',') + ' kg', rp: d.nilaiRp || 0, alasan: d.alasan || '' }); });
  ambilPenyesuaianKemasan().forEach((d) => semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.namaProduk + ' ' + String(d.ukuranKemasan).replace('.', ',') + ' kg', teks: (d.selisihUnit > 0 ? '+' : '') + (d.selisihUnit || 0) + ' unit', rp: d.nilaiRp || 0, alasan: d.alasan || '' }));
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname') semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: ccLabelBahan(d.jenis), teks: (d.jumlah > 0 ? '+' : '') + (d.jumlah || 0) + ' lembar', rp: d.nilaiRp || 0, alasan: d.catatan || '' }); });
  const kel = {}; semua.forEach((x) => { const k = x.tanggal + ' ' + x.jam; if (!kel[k]) kel[k] = { kunci: k, tanggal: x.tanggal, jam: x.jam, baris: [], rp: 0 }; kel[k].baris.push(x); kel[k].rp += x.rp; });
  return Object.keys(kel).sort().reverse().slice(0, n || 8).map((k) => kel[k]);
}
