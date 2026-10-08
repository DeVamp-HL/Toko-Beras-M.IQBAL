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
import { hitungStokKarungPerMerk, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungHppMerkDalamBatch, hitungUtangPemasok } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, kunciKemasan, merkPunyaKarungBerat, batchDiutang, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilUtangPemasokMutasi, ambilHargaKarung, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, ambilWadahLiteran, cacheMentah, tolakKunci, tolakKunciTanggal, stokMerekSaja, petaStokWadah, petaBukuWadah, ambilProduksiBerlaku, kunciUkuran, petaUkuran, indukTerpisah, ukuranDigabung, namaSistemPemasok, ingatStokKarung, ingatStokKemasan } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { hppKeluarPerKg, nilaiSelisihKg } from '../mesin/modal-fifo.js';
import { hitunganFisik, tumpukanGudang, aturWadah, pindahNama, semuaKarungTerbuka, karungUntukWadah, karungBelakang, beratKarungBuka, ckCocokTerakhir, ckKalimatMundur, kolamDitutup } from './jual-logika.js';
import { wbKomposisi, wbBagianMerk, wbKomposisiBaru, wbKomposisiTurunanKg, wbModalPerKg, wbRasio, wbNamaKelas, wbDokLahir, wbDokPindah, wbLiteranLangsung, wbKarungTertinggal, wbSertakanKarungBekas } from './wadah-bernama-logika.js';
import { vrPerluTanya, vrNama, vrDokJenis, vrAda, vrGerakBuku, VR_BATAS_BAWAAN } from './varian-logika.js';
import { arBeras, arKunciBeras, arDokPulihBanyak, arPeta } from './arsip-logika.js';
// putaran 30: kelas mutu merek (harga lalu per kelas, merek baru → kelas, kelas tanpa wadah)
import { kmKelasMerk, kmKelasSendiri, kmCalonKelas, kmHargaLaluKelas, kmHargaLaluMerk, kmArah, kmKalimatKelas, kmDokKelas } from './kelas-merek-logika.js';

// paket brief 9 Okt (butir 7): ambang mutu saat terima — kadar air maks 14 % & butir patah maks 25 % = angka bawaan (perkiraan), owner mengubahnya di Atur Barang masuk
export const ATUR_CATAT_BAWAAN = { minKarung: 60, tempoHari: 21, batasSelisih: 3, ambangSusutPositif: 250000, jendelaGandaMenit: 10, batasVarian: VR_BATAS_BAWAAN, kadarAirMaks: 14, patahMaks: 25 };
// angka ketikan toko: "13.200" = tiga belas ribu dua ratus (titik ribuan), "76,6" = koma desimal; "76.6" (papan tombol HP) = desimal juga — titik dianggap
// ribuan hanya bila polanya persis kelompok tiga digit
const ckAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const ckB2 = (n) => Math.round(n * 100) / 100;
const ckKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const ckKosong = (v) => v === undefined || v === null || String(v).trim() === '';
// modal FIFO (owner 9 Okt 2026): rupiah selisih tumpukan merek karung = irisan karung terlama (mesin/modal-fifo.js); saklar mati = selisih × modal (rumus lama)
const ckRpKarung = (merk, selisih, modal) => { const st = ingatStokKarung()[merk]; return st && st.metode === 'fifo' ? Math.round(nilaiSelisihKg(st, selisih)) : Math.round(selisih * modal); };
const ckMenit = (jam) => { const m = /^(\d{1,2})[:.](\d{2})/.exec(String(jam || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };

// paket brief 9 Okt (butir 7): syarat ambang mutu — kadar air maks lebih dari 0 sampai 100 %, butir patah maks 0–100 %
const TM_SYARAT = { kadarAirMaks: (n) => n > 0 && n <= 100, patahMaks: (n) => n >= 0 && n <= 100 };
/** Angka kebijakan owner untuk pencatatan stok (aturanToko/catatStok); belum diatur → bawaan sistem berjalan (60 karung, 21 hari, 3 %, Rp250.000). */
export function aturCatat() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'catatStok') || null;
  const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : ATUR_CATAT_BAWAAN[k]);
  // paket brief 9 Okt (butir 7): ambang mutu dibaca per kolom; mutuBawaan = kolom yang belum pernah disimpan owner (layar menyebutnya "angka bawaan, perkiraan")
  const milik = (k, syarat) => !!a && a[k] !== undefined && a[k] !== null && String(a[k]).trim() !== '' && isFinite(Number(a[k])) && syarat(Number(a[k]));
  const airMilik = milik('kadarAirMaks', TM_SYARAT.kadarAirMaks); const patahMilik = milik('patahMaks', TM_SYARAT.patahMaks);
  return { minKarung: ambil('minKarung', (n) => n >= 0), tempoHari: ambil('tempoHari', (n) => n >= 0), batasSelisih: ambil('batasSelisih', (n) => n >= 0 && n <= 100),
    ambangSusutPositif: ambil('ambangSusutPositif', (n) => n >= 0), jendelaGandaMenit: ATUR_CATAT_BAWAAN.jendelaGandaMenit, batasVarian: ambil('batasVarian', (n) => n >= 0 && n <= 100), dariOwner: !!a, sejak: a ? (a.tanggal || '') : '',
    kadarAirMaks: airMilik ? Number(a.kadarAirMaks) : ATUR_CATAT_BAWAAN.kadarAirMaks, patahMaks: patahMilik ? Number(a.patahMaks) : ATUR_CATAT_BAWAAN.patahMaks, mutuBawaan: { kadarAirMaks: !airMilik, patahMaks: !patahMilik } };
}
export function susunAturCatat(isi, w) {
  const kini = aturCatat(); const baca = (k, syarat, teks) => { if (ckKosong(isi[k])) return { nilai: kini[k] }; const n = ckAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const m = baca('minKarung', (n) => n >= 0 && n <= 1000, 'Minimal karung per mobil harus 0–1000'); if (m.tolak) return { tolak: m.tolak };
  const t = baca('tempoHari', (n) => n >= 0 && n <= 365, 'Tempo bon pemasok harus 0–365 hari'); if (t.tolak) return { tolak: t.tolak };
  const b = baca('batasSelisih', (n) => n >= 0 && n <= 100, 'Batas selisih wajar harus 0–100 %'); if (b.tolak) return { tolak: b.tolak };
  const s = baca('ambangSusutPositif', (n) => n >= 0, 'Ambang stok bertambah tanpa pembelian harus 0 atau lebih'); if (s.tolak) return { tolak: s.tolak };
  const v = baca('batasVarian', (n) => n >= 0 && n <= 100, 'Batas beda harga beli (varian) harus 0–100 %'); if (v.tolak) return { tolak: v.tolak };
  // paket brief 9 Okt (butir 7): ambang mutu saat terima — ketikan bukan angka ditolak (bukan dianggap 0)
  const bacaMutu = (k, teks) => { if (ckKosong(isi[k])) return { nilai: kini[k] }; const n = tmAngka(isi[k]); return n !== null && TM_SYARAT[k](n) ? { nilai: ckB2(n) } : { tolak: teks }; };
  const ka = bacaMutu('kadarAirMaks', 'Kadar air maksimal saat terima harus lebih dari 0 sampai 100 %'); if (ka.tolak) return { tolak: ka.tolak };
  const bp = bacaMutu('patahMaks', 'Butir patah maksimal saat terima harus 0–100 %'); if (bp.tolak) return { tolak: bp.tolak };
  // dokumen catatStok juga memegang saklar modal FIFO (modalFifoMulai + riwayatModalFifo, Stok › HPP): kolom lain DISALIN utuh, yang diatur di sini ditimpa
  const lama = cacheMentah('aturan').find((d) => String(d.id) === 'catatStok') || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, minKarung: m.nilai, tempoHari: t.nilai, batasSelisih: b.nilai, ambangSusutPositif: s.nilai, batasVarian: v.nilai, kadarAirMaks: ka.nilai, patahMaks: bp.nilai }) }],
    patch: { kabar: 'Aturan pencatatan disimpan — satu mobil minimal ' + m.nilai + ' karung · tempo bon ' + t.nilai + ' hari · selisih wajar ' + b.nilai + ' % · stok bertambah > ' + RP(s.nilai) + ' ditanya · harga beli beda > ' + v.nilai + ' % ditanya "sama barangnya / beda mutu"'
      + ' · mutu saat terima: kadar air > ' + tmD(ka.nilai) + ' % atau butir patah > ' + tmD(bp.nilai) + ' % ditandai AWAS', kabarAwas: false } };
}

// ====================== BARANG MASUK (ST1) ======================
export const BERAT_KARUNG_PILIHAN = [50, 25];
// paket brief 9 Okt: + isian timbang & mutu (opsional, kosong = belum ditimbang / tidak dicek)
export function barisMasukKosong() { return { merk: '', jumlahKarung: '', beratKarung: 50, hargaPerKg: '', timbangKg: '', kadarAir: '', kutu: '', bau: '', butirPatah: '' }; }
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
  const wadahStok = petaBukuWadah(); const ukuran = petaUkuran();   // putaran 28: buku khusus & buku per ukuran ('Merek 25 kg' dipilih otomatis) bukan nama barang masuk
  return Object.keys(hitung).filter((m) => !arsip[arKunciBeras(m)] && !kelas[m] && !wadahStok[m] && !ukuran[m]).sort((a, b) => akhir[b].localeCompare(akhir[a]) || hitung[b] - hitung[a] || a.localeCompare(b));
}
/**
 * PETUNJUK SATU KETUKAN (audit 39b no. 43, keputusan owner 30 Sep): nama yang diketik tanpa " · " padahal barang itu sudah dicatat sebagai VARIAN
 * ("TH" diketik, bukunya "TH · House") → daftar varian itu (yang bukunya paling berisi dulu), supaya Barang masuk bertanya "pakai itu?" — satu ketukan
 * mengganti baris ke nama varian, jadi stok tidak terbelah ke buku baru. Bukan penolakan: kalau memang barang lain, baris tetap jadi nama baru.
 * Huruf besar/kecil & spasi ganda tidak dibedakan; nama arsip, buku khusus wadah, dan buku per ukuran tidak ditawarkan.
 * Tinjauan 30 Sep: nama yang SAMA kecuali huruf/spasi ("kumala" padahal bukunya "Kumala", "th · house" padahal "TH · House") juga ditawarkan
 * dan SELALU paling depan — tanpa itu pita hanya menawarkan varian dan satu ketukan memasukkan karung biasa ke buku varian.
 */
export function ckSaranVarian(merkKetik) {
  const t = String(merkKetik || '').trim(); if (!t) return []; const berVarian = t.indexOf('\u00b7') >= 0;
  const kunci = (x) => String(x).trim().replace(/\s+/g, ' ').toLowerCase(); const k = kunci(t);
  const st = ingatStokKarung(); const nama = {}; Object.keys(st).forEach((m) => { nama[m] = true; }); ambilHargaKarung().forEach((h) => { if (h && h.merk) nama[String(h.merk)] = true; });
  const arsip = arPeta(); const bw = petaBukuWadah(); const uk = petaUkuran();
  const sama = (m) => m !== t && kunci(m) === k;                                                     // nama yang sama, beda huruf/spasi
  const variannya = (m) => !berVarian && m.indexOf(' \u00b7 ') > 0 && kunci(m.split(' \u00b7 ')[0]) === k;   // varian berinduk nama itu
  return Object.keys(nama).filter((m) => (sama(m) || variannya(m)) && !arsip[arKunciBeras(m)] && !bw[m] && !uk[m])
    .map((m) => ({ nama: m, bukuKg: ckB2(((st[m] || {}).sisaKg) || 0), s: sama(m) ? 1 : 0 })).sort((a, b) => b.s - a.s || b.bukuKg - a.bukuKg || a.nama.localeCompare(b.nama))
    .map((x) => ({ nama: x.nama, bukuKg: x.bukuKg }));
}
/** Harga beli per kg terakhir nama itu (dari buku) — pembanding saat mengetik harga. */
export function hargaSebelumnya(merk) { const s = ingatStokKarung()[merk]; return s ? (s.hargaTerakhirPerKg || 0) : 0; }
// ---------- TIMBANG & MUTU SAAT TERIMA (paket brief 9 Okt, butir 6 & 7 — keputusan owner: isian OPSIONAL, catatan tetap bisa disimpan) ----------
// Per baris merek kedatangan: berat timbang = hasil timbang SELURUH baris itu; kg nota = jumlahKarung × beratKarung (totalKg); selisih = timbang − nota.
// Cek mutu: kadar air (%), kutu (ada/tidak), bau (normal/apek/lain), butir patah (%). Kosong = "belum ditimbang" / "tidak dicek" — BUKAN selisih 0 / mutu baik.
// CATATAN PEMERIKSAAN SAJA: totalKg, stok, modal, HPP, dan bon tetap menurut nota (mesin beku tidak membaca kolom ini). Ditulis ke baris merkList HANYA bila
// diisi (kedatangan tanpa isian = bentuk lama persis): timbangKg, kadarAir, kutu, bau, butirPatah. Tanda AWAS dihitung saat dibaca dari ambang owner
// (aturanToko/catatStok kadarAirMaks · patahMaks) — ambang diubah → tanda kedatangan lama ikut berubah.
export const TM_KUTU = [['tidak', 'tidak ada'], ['ada', 'ada kutu']];
export const TM_BAU = [['normal', 'normal'], ['apek', 'apek'], ['lain', 'bau lain']];
export const TM_KOLOM = ['timbangKg', 'kadarAir', 'kutu', 'bau', 'butirPatah'];
// angka isian: kosong → null; angka tersimpan apa adanya; ketikan pakai aturan ckAngka (titik ribuan, koma desimal); selain angka → NaN (ditolak, bukan dianggap 0)
const tmAngka = (v) => { if (typeof v === 'number') return isFinite(v) ? v : NaN; if (ckKosong(v)) return null; const t = String(v).trim(); return /^[\d.,]*\d[\d.,]*$/.test(t) ? ckAngka(t) : NaN; };
const tmD = (n) => String(Math.round(n * 10) / 10).replace('.', ',');
const tmTeks = (v) => (typeof v === 'number' && isFinite(v) ? String(v).replace('.', ',') : ckKosong(v) ? '' : String(v));
/**
 * Baca isian timbang & mutu satu baris — draf (teks ketikan) atau baris merkList tersimpan (angka). kgNota = totalKg baris, harga = harga beli per kg baris.
 * → { ada, masalah, timbangKg|null, kgNota, selisihKg|null, selisihPersen|null, kgKurang, kgLebih, nilaiKurang, timbangTeks,
 *     kadarAir|null, kutu, bau, butirPatah|null, dicek, mutuTeks, awas[], kolom{} (yang ditulis ke baris merkList: hanya yang diisi) }
 */
export function tmBaris(isi, kgNota, harga, atur) {
  const A = atur || aturCatat(); const x = isi || {};
  const tb = tmAngka(x.timbangKg), air = tmAngka(x.kadarAir), pt = tmAngka(x.butirPatah); const kutu = String(x.kutu || '').trim(), bau = String(x.bau || '').trim();
  const ada = tb !== null || air !== null || pt !== null || !!kutu || !!bau;
  const masalah = tb !== null && !(tb > 0) ? 'berat timbang harus angka lebih dari 0 kg — kosongkan kalau belum ditimbang'
    : air !== null && !(air >= 0 && air <= 100) ? 'kadar air harus angka 0–100 % — kosongkan kalau tidak dicek'
      : pt !== null && !(pt >= 0 && pt <= 100) ? 'butir patah harus angka 0–100 % — kosongkan kalau tidak dicek'
        : kutu && !TM_KUTU.some((k) => k[0] === kutu) ? 'pilihan kutu "' + kutu + '" tidak dikenal' : bau && !TM_BAU.some((k) => k[0] === bau) ? 'pilihan bau "' + bau + '" tidak dikenal' : '';
  const nota = ckB2(Number(kgNota) || 0); const hasil = { ada, masalah, kgNota: nota, timbangKg: null, selisihKg: null, selisihPersen: null, kgKurang: 0, kgLebih: 0, nilaiKurang: 0,
    kadarAir: null, kutu: '', bau: '', butirPatah: null, dicek: false, awas: [], kolom: {} };
  if (masalah) return Object.assign(hasil, { timbangTeks: masalah, mutuTeks: masalah });
  const timbang = tb !== null ? ckB2(tb) : null;
  if (timbang !== null) hasil.timbangKg = timbang;
  if (timbang !== null && nota > 0) { const s = ckB2(timbang - nota); hasil.selisihKg = s; hasil.selisihPersen = Math.round(s / nota * 1000) / 10;
    hasil.kgKurang = s < 0 ? -s : 0; hasil.kgLebih = s > 0 ? s : 0; hasil.nilaiKurang = Math.round(hasil.kgKurang * (Number(harga) || 0)); }
  hasil.timbangTeks = timbang === null ? 'belum ditimbang' : hasil.selisihKg === null ? 'timbang ' + tmD(timbang) + ' kg — kg notanya belum ada'
    : 'timbang ' + tmD(timbang) + ' kg · nota ' + tmD(nota) + ' kg → ' + (hasil.selisihKg === 0 ? 'pas' : (hasil.selisihKg < 0 ? 'KURANG ' : 'lebih ') + tmD(Math.abs(hasil.selisihKg)) + ' kg (' + (hasil.selisihKg > 0 ? '+' : '−') + tmD(Math.abs(hasil.selisihPersen)) + ' %)');
  hasil.kadarAir = air !== null ? ckB2(air) : null; hasil.butirPatah = pt !== null ? ckB2(pt) : null; hasil.kutu = kutu; hasil.bau = bau;
  hasil.dicek = hasil.kadarAir !== null || hasil.butirPatah !== null || !!kutu || !!bau;
  if (hasil.kadarAir !== null && hasil.kadarAir > A.kadarAirMaks) hasil.awas.push('kadar air ' + tmD(hasil.kadarAir) + ' % > maks ' + tmD(A.kadarAirMaks) + ' %');
  if (kutu === 'ada') hasil.awas.push('ada kutu');
  if (bau === 'apek') hasil.awas.push('bau apek');
  if (bau === 'lain') hasil.awas.push('bau tidak normal');
  if (hasil.butirPatah !== null && hasil.butirPatah > A.patahMaks) hasil.awas.push('butir patah ' + tmD(hasil.butirPatah) + ' % > maks ' + tmD(A.patahMaks) + ' %');
  const nm = (daftar, id) => (daftar.find((k) => k[0] === id) || ['', id])[1];
  hasil.mutuTeks = !hasil.dicek ? 'tidak dicek' : [hasil.kadarAir !== null ? 'kadar air ' + tmD(hasil.kadarAir) + ' %' : 'kadar air tidak dicek', kutu ? 'kutu ' + nm(TM_KUTU, kutu) : 'kutu tidak dicek',
    bau ? 'bau ' + nm(TM_BAU, bau) : 'bau tidak dicek', hasil.butirPatah !== null ? 'butir patah ' + tmD(hasil.butirPatah) + ' %' : 'butir patah tidak dicek'].join(' · ');
  if (timbang !== null) hasil.kolom.timbangKg = timbang;
  if (hasil.kadarAir !== null) hasil.kolom.kadarAir = hasil.kadarAir;
  if (kutu) hasil.kolom.kutu = kutu;
  if (bau) hasil.kolom.bau = bau;
  if (hasil.butirPatah !== null) hasil.kolom.butirPatah = hasil.butirPatah;
  return hasil;
}
/** Isian draf (teks) dari baris merkList tersimpan — koreksi kedatangan membawa & bisa mengubah isian timbang & mutu; baris lama tanpa isian = kosong. */
export function tmDraf(m) { const o = {}; TM_KOLOM.forEach((k) => { o[k] = tmTeks(m ? m[k] : ''); }); return o; }
/** Ringkasan satu kedatangan tersimpan: baris karung (bal tidak ikut), berapa yang ditimbang / dicek, selisih, dan tanda awas mutu per baris. */
export function tmKedatangan(b, atur) {
  const A = atur || aturCatat(); const rows = ((b && b.merkList) || []).filter((m) => m && m.bentuk !== 'bal' && m.merk && (Number(m.totalKg) || 0) > 0);
  const baris = rows.map((m) => Object.assign({ merk: String(m.merk), merkPemasok: m.merkPemasok ? String(m.merkPemasok) : '', hargaPerKg: Number(m.hargaPerKg) || 0 }, tmBaris(m, Number(m.totalKg) || 0, Number(m.hargaPerKg) || 0, A)));
  const t = baris.filter((x) => x.timbangKg !== null); const c = baris.filter((x) => x.dicek);
  const selisihKg = ckB2(t.reduce((a, x) => a + (x.selisihKg || 0), 0));
  return { baris, nBaris: baris.length, ditimbang: t.length, dicek: c.length, kgNota: ckB2(t.reduce((a, x) => a + x.kgNota, 0)), kgTimbang: ckB2(t.reduce((a, x) => a + x.timbangKg, 0)), selisihKg,
    kgKurang: ckB2(t.reduce((a, x) => a + x.kgKurang, 0)), kgLebih: ckB2(t.reduce((a, x) => a + x.kgLebih, 0)), nilaiKurang: t.reduce((a, x) => a + x.nilaiKurang, 0),
    awas: baris.filter((x) => x.awas.length).map((x) => ({ merk: x.merk, alasan: x.awas.slice() })),
    teks: (t.length ? 'ditimbang' + (t.length < baris.length ? ' ' + t.length + '/' + baris.length + ' baris' : '') + ' ' + (selisihKg === 0 ? 'pas' : (selisihKg > 0 ? '+' : '−') + tmD(Math.abs(selisihKg)) + ' kg') : '')
      + (c.length ? (t.length ? ' · ' : '') + (baris.some((x) => x.awas.length) ? 'mutu AWAS' : 'mutu dicek') : '') };
}
/**
 * REKAP TIMBANG & MUTU PER PEMASOK (paket brief 9 Okt) — dipasang di Stok › Barang masuk, kelak juga di kartu pemasok Harga & Pemasok.
 * opsi: { pemasok (nama persis, satu pemasok saja), dari, sampai (YYYY-MM-DD) }. Kedatangan = batchMasuk ber-baris karung (stok awal / saldo pembuka / lahir
 * buku bukan kedatangan; kedatangan yang isinya baris bal saja dihitung di `lewatBal`); tanpa nama pemasok = kelompok "(tanpa nama pemasok)".
 * Per pemasok: kedatangan = ditimbang (semua baris) + sebagian + belumTimbang; selisihKg = kgLebih − kgKurang (hanya baris yang ditimbang);
 * persenRata = selisihKg / kgNota baris yang ditimbang × 100 (tertimbang kg; null bila belum ada yang ditimbang); nilaiKurang = Σ kg kurang × harga beli
 * per kg barisnya — PERKIRAAN NILAI, TIDAK DIBUKUKAN; awas = baris yang melewati ambang owner / ada kutu / bau tidak normal. total = Σ semua pemasok.
 */
export function rekapTimbangMutu(opsi) {
  const o = opsi || {}; const A = aturCatat(); const per = {}; let lewatBal = 0;
  const pilih = o.pemasok !== undefined && o.pemasok !== null ? String(o.pemasok).trim() : null;
  ambilSemuaBatch().forEach((b) => {
    if (!b || ccFondasi(b) || b.lahirBuku) return; const pem = String(b.pemasok || '').trim() || '(tanpa nama pemasok)'; const tgl = String(b.tanggal || '');
    if (pilih !== null && pem !== pilih) return; if (o.dari && tgl < o.dari) return; if (o.sampai && tgl > o.sampai) return;
    const K = tmKedatangan(b, A); if (!K.nBaris) { if ((b.merkList || []).some((m) => m && m.bentuk === 'bal')) lewatBal += 1; return; }
    const p = per[pem] || (per[pem] = { pemasok: pem, kedatangan: 0, ditimbang: 0, sebagian: 0, belumTimbang: 0, barisSemua: 0, barisTimbang: 0, kgNota: 0, kgTimbang: 0, selisihKg: 0, kgKurang: 0, kgLebih: 0,
      nilaiKurang: 0, dicek: 0, barisDicek: 0, kedatanganAwas: 0, awas: [], terakhir: '' });
    p.kedatangan += 1; if (K.ditimbang === K.nBaris) p.ditimbang += 1; else if (K.ditimbang > 0) p.sebagian += 1; else p.belumTimbang += 1;
    p.barisSemua += K.nBaris; p.barisTimbang += K.ditimbang; p.kgNota = ckB2(p.kgNota + K.kgNota); p.kgTimbang = ckB2(p.kgTimbang + K.kgTimbang); p.selisihKg = ckB2(p.selisihKg + K.selisihKg);
    p.kgKurang = ckB2(p.kgKurang + K.kgKurang); p.kgLebih = ckB2(p.kgLebih + K.kgLebih); p.nilaiKurang += K.nilaiKurang; if (K.dicek) p.dicek += 1; p.barisDicek += K.dicek;
    if (K.awas.length) { p.kedatanganAwas += 1; K.awas.forEach((x) => p.awas.push({ batchId: b.id, tanggal: tgl, merk: x.merk, alasan: x.alasan })); }
    if (tgl > p.terakhir) p.terakhir = tgl; });
  const daftar = Object.keys(per).map((k) => per[k]);
  daftar.forEach((p) => { p.persenRata = p.kgNota > 0 ? Math.round(p.selisihKg / p.kgNota * 1000) / 10 : null; p.awas.sort((x, y) => y.tanggal.localeCompare(x.tanggal) || x.merk.localeCompare(y.merk)); });
  // urutan: yang punya AWAS dulu, lalu kedatangan terbanyak; kelompok "(tanpa nama pemasok)" selalu paling bawah
  const tanpaNama = (p) => (p.pemasok === '(tanpa nama pemasok)' ? 1 : 0);
  daftar.sort((x, y) => tanpaNama(x) - tanpaNama(y) || y.kedatanganAwas - x.kedatanganAwas || y.kedatangan - x.kedatangan || x.pemasok.localeCompare(y.pemasok));
  const total = { kedatangan: 0, ditimbang: 0, sebagian: 0, belumTimbang: 0, barisSemua: 0, barisTimbang: 0, kgNota: 0, kgTimbang: 0, selisihKg: 0, kgKurang: 0, kgLebih: 0, nilaiKurang: 0, dicek: 0, barisDicek: 0, kedatanganAwas: 0 };
  daftar.forEach((p) => Object.keys(total).forEach((k) => { total[k] = ['kgNota', 'kgTimbang', 'selisihKg', 'kgKurang', 'kgLebih'].indexOf(k) >= 0 ? ckB2(total[k] + p[k]) : total[k] + p[k]; }));
  total.persenRata = total.kgNota > 0 ? Math.round(total.selisihKg / total.kgNota * 1000) / 10 : null;
  return { pemasok: daftar, total, lewatBal, atur: { kadarAirMaks: A.kadarAirMaks, patahMaks: A.patahMaks, mutuBawaan: A.mutuBawaan } };
}
// audit 39b no. 30: baris BAL (beli jadi, sistem lama) kedatangan yang dikoreksi TIDAK diubah dari sini — ikut tertulis APA ADANYA (hanya nomor barisnya).
// Nilainya bagian bon / belanja kedatangan itu, dan bongkar tetap dibagi ke SEMUA baris termasuk bal (porsinya sudah di modal per bag pasangan beli-jadi) — sama dengan mesin.
const ckBarisBal = (batch) => ((batch && batch.merkList) || []).filter((m) => m && m.bentuk === 'bal');
/** Hitung draf: tiap baris kg, subtotal, alokasi bongkar & HPP per kg (rumus hitungHppMerkDalamBatch sistem berjalan) + masalah per baris. */
export function hitungMasuk(draf) {
  // putaran 27 (Bagian 5, owner 27 Sep): nama WADAH / kelas mutu (IR64 Apex dkk.) tidak pernah lagi dibukukan lewat barang masuk — kecuali nama wadah yang
  // sekaligus merek karung pemasok (Aturan wadah). Koreksi kedatangan lama boleh tetap memakai nama yang sudah tertulis di kedatangan itu.
  const kelas = wbNamaKelas(); const wadahStok = petaBukuWadah(); const lamaB = draf.id ? ambilSemuaBatch().find((x) => String(x.id) === String(draf.id)) : null;
  const namaLama = {}; ((lamaB && lamaB.merkList) || []).forEach((m) => { if (m.merk) namaLama[m.merk] = true; });
  // putaran 28 (owner 28 Sep): karung 25 kg merek yang datang DUA ukuran dibukukan ke buku sendiri 'Merek 25 kg' (buku merek = karung 50 kg)
  const ukuran = petaUkuran(); const terpisah = indukTerpisah();
  const ada50 = {}; (draf.baris || []).forEach((b) => { if ((ckAngka(b.beratKarung) || 50) === 50) ada50[String(b.merk || '').trim()] = true; });
  // audit 39b no. 35 (owner 30 Sep): merek yang dijual per liter langsung / kelas sendiri TIDAK punya buku per ukuran — karung 25 kg-nya masuk buku induk seperti dulu
  const tanpaUkuran = ckTanpaBukuUkuran();
  const duaUkuran = (m) => !!m && !ukuran[m] && !namaLama[m] && !tanpaUkuran[m] && (!!(terpisah[m] && terpisah[m][25]) || merkPunyaKarungBerat(m, 50) || !!ada50[m]);
  // putaran 30 (owner 28 Sep): merek BARU (belum punya buku / katalog) → kelas mutu. Kelas BERWADAH: buku tetap atas nama merek + peta merek → kelas (lapisan baca).
  // Kelas TANPA WADAH (kelasSendiri): baris dibukukan ATAS NAMA KELAS, merek pemasok jadi keterangan `merkPemasok`. Koreksi kedatangan lama: kelas tidak ditanya.
  const sendiri = kmKelasSendiri(); const calonKelas = kmCalonKelas(); const bolehKelas = {}; calonKelas.forEach((c) => { bolehKelas[c.nama] = true; });
  const pemasokDraf = String(draf.pemasok || '').trim();
  const aturMutu = aturCatat();   // paket brief 9 Okt: ambang mutu owner, sekali per hitungan
  const bongkar = ckAngka(draf.bongkar); const baris = (draf.baris || []).map((b, i) => {
    const jumlah = ckAngka(b.jumlahKarung); const berat = ckAngka(b.beratKarung) || 50; const harga = ckAngka(b.hargaPerKg); const merkKetik = String(b.merk || '').trim();
    // paket brief 9 Okt (butir 6 & 7): isian timbang & mutu baris ini — catatan pemeriksaan, tidak mengubah kg / modal / bon
    const cek = tmBaris(b, jumlah * berat, harga, aturMutu);
    const baru = !draf.id && !!merkKetik && !vrAda(merkKetik) && !kelas[merkKetik.split(' \u00b7 ')[0]] && !wadahStok[merkKetik] && !ukuran[merkKetik] && !sendiri[merkKetik];
    const tebak = baru ? kmKelasMerk(merkKetik) : { kelas: '', asal: '' };
    const saranVarian = baru ? ckSaranVarian(merkKetik) : [];   // audit 39b no. 43: "TH" padahal bukunya "TH · House" → layar bertanya "pakai itu?"
    const kelasPilih = !!b.kelasPilih; const kelasKetik = String(b.kelas || '').trim();
    const kelasBaris = !baru ? '' : kelasPilih ? (bolehKelas[kelasKetik] ? kelasKetik : '') : (tebak.asal === 'tebakan' && bolehKelas[tebak.kelas] ? tebak.kelas : '');
    const kelasAsal = !baru || !kelasBaris ? (baru && kelasPilih ? 'owner' : '') : kelasPilih ? 'owner' : 'tebakan';
    const keSendiri = !!(kelasBaris && sendiri[kelasBaris]);
    // perbaikan 28 Sep: KOREKSI kedatangan yang mengganti nama baris ke kelas tanpa wadah (mis. CM → Ketan Putih) membawa nama asli baris sebagai merkPemasok
    // (draf koreksi mengingat merkAsal tiap baris; merkPemasok yang sudah ada tidak ditimpa)
    const asalKoreksi = draf.id ? String(b.merkAsal || '').trim() : ''; const lamaPemasok = draf.id ? String(b.merkPemasok || '').trim() : '';
    const bawaAsal = !!asalKoreksi && !!merkKetik && merkKetik !== asalKoreksi && !!sendiri[merkKetik] && !sendiri[asalKoreksi] && !lamaPemasok;
    const merk = keSendiri ? kelasBaris : merkKetik; const merkPemasok = keSendiri ? merkKetik : bawaAsal ? asalKoreksi : lamaPemasok;
    // paket brief 9 Okt: baris yang cuma berisi timbang / cek mutu tetap dianggap terisi (ditanya namanya, tidak dibuang diam-diam)
    const terisi = !!merk || jumlah > 0 || harga > 0 || cek.ada; const masalah = !terisi ? '' : !merk ? 'nama berasnya belum dipilih' : ukuran[merk] && !namaLama[merk] ? merk + ' itu buku karung ' + ukuran[merk].berat + ' kg ' + ukuran[merk].induk + ' — tulis "' + ukuran[merk].induk + '" dengan ukuran ' + ukuran[merk].berat + ' kg, bukunya dipilih otomatis' : wadahStok[merk] ? merk + ' itu buku KHUSUS (isi wadah / karung sisihan wadah / kemasan adukan yang dibuka), bukan merek pemasok — tulis merek yang tertera di karungnya' : kelas[merk.split(' \u00b7 ')[0]] && !namaLama[merk] ? merk + ' itu nama WADAH / kelas mutu, bukan merek karung — tulis merek yang tertera di karungnya'
      : !(jumlah > 0) ? 'jumlah karungnya belum diisi' : !(harga > 0) ? 'harga beli per kg belum diisi' : cek.masalah;
    // putaran 27 (Bagian 2): nama yang sudah punya buku & harga beli beda > batas dari modal berjalan → "sama barangnya / beda mutu?" (koreksi tidak ditanya)
    const vr = !draf.id && terisi && !masalah ? vrPerluTanya(merk, harga) : { perlu: false };
    // putaran 27 (Bagian 3): nama yang DIARSIPKAN datang lagi → wajib dijawab: pulihkan (sama barangnya) atau jadi varian
    const diArsip = !draf.id && terisi && !masalah && arBeras(merk); if (diArsip) vr.arsip = true;
    const pilih = b.varian === 'sama' || b.varian === 'beda' ? b.varian : ''; const merkVarian = pilih === 'beda' ? vrNama(merk, b.namaMutu, draf.tanggal) : merk;
    const keUkuran = berat === 25 && duaUkuran(merkVarian); const merkSimpan = keUkuran ? kunciUkuran(merkVarian, 25) : merkVarian;
    const indukUkuran = keUkuran ? merkVarian : ukuran[merkSimpan] ? ukuran[merkSimpan].induk : '';
    // harga lalu: merek dikenal = mesin (+ tanggal & pemasok dari riwayat); merek baru berkelas = kedatangan terakhir KELAS itu (pemasok yang dipilih diutamakan)
    const lalu = merk && !masalah ? kmHargaLaluMerk(merk, draf.id) : null; const laluKelas = baru && kelasBaris && !keSendiri ? kmHargaLaluKelas(kelasBaris, pemasokDraf, null) : null;
    const arah = kmArah(harga, lalu ? lalu.harga : laluKelas ? laluKelas.harga : 0); const kelasTanya = baru && !keSendiri && laluKelas ? kmKalimatKelas(harga, laluKelas) : '';
    // owner 7 Okt (FJN berbuku + FJN · Imperial di katalog): nama yang SUDAH berbuku tapi punya varian → pita "yang datang ini yang mana?" — bukan penolakan,
    // supaya karung yang dimaksud varian tidak masuk buku induk diam-diam. Koreksi kedatangan, baris yang sudah dijawab sama/beda mutu: tidak ditawari.
    const varianInduk = !draf.id && !baru && !!merk && !pilih && merk.indexOf('·') < 0 && !wadahStok[merk] && !ukuran[merk] && !kelas[merk] && !sendiri[merk] ? ckSaranVarian(merk).filter((v) => v.nama.indexOf(' · ') > 0) : [];
    return { ke: i + 1, merk, merkSimpan, indukUkuran, merkAsal: asalKoreksi, varian: pilih, namaMutu: String(b.namaMutu || ''), vr, jumlahKarung: jumlah, beratKarung: berat, hargaPerKg: harga, totalKg: ckB2(jumlah * berat), subtotalHarga: Math.round(jumlah * berat * harga), terisi, masalah, sah: terisi && !masalah,
      hargaLalu: merk ? hargaSebelumnya(merk) : 0,
      merkKetik, baru, saranVarian, varianInduk, kelas: kelasBaris, kelasAsal, kelasPilih, keSendiri, merkPemasok, lalu, laluKelas, arah, kelasTanya, calonKelas: baru ? calonKelas : [], cek }; });
  const sah = baris.filter((b) => b.sah);
  const bal = ckBarisBal(lamaB); const nilaiBal = bal.reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0);
  const hpp = hitungHppMerkDalamBatch(sah.map((b) => ({ merk: b.merkSimpan, totalKg: b.totalKg, subtotalHarga: b.subtotalHarga })).concat(bal.map((m) => ({ merk: m.merk, totalKg: Number(m.totalKg) || 0, subtotalHarga: Number(m.subtotalHarga) || 0 }))), bongkar);
  sah.forEach((b, i) => { b.alokasiBongkar = Math.round(hpp[i].alokasiBongkar); b.hppPerKg = hpp[i].hppPerKg; });
  const karung = sah.reduce((a, b) => a + b.jumlahKarung, 0); const kg = ckB2(sah.reduce((a, b) => a + b.totalKg, 0)); const nilaiBeras = sah.reduce((a, b) => a + b.subtotalHarga, 0);
  // paket brief 9 Okt: ringkasan timbang & mutu draf (baris sah saja) — pembanding, bukan angka buku
  const tb = sah.filter((b) => b.cek.timbangKg !== null);
  const timbang = { baris: sah.length, ditimbang: tb.length, kgNota: ckB2(tb.reduce((a, b) => a + b.totalKg, 0)), selisihKg: ckB2(tb.reduce((a, b) => a + (b.cek.selisihKg || 0), 0)),
    nilaiKurang: tb.reduce((a, b) => a + b.cek.nilaiKurang, 0), dicek: sah.filter((b) => b.cek.dicek).length, awas: sah.filter((b) => b.cek.awas.length).length };
  timbang.persen = timbang.kgNota > 0 ? Math.round(timbang.selisihKg / timbang.kgNota * 1000) / 10 : null;
  return { baris, sah, bongkar, karung, kg, nilaiBeras, nilaiBal, total: nilaiBeras + nilaiBal + bongkar, bermasalah: baris.filter((b) => b.terisi && b.masalah), tanyaVarian: sah.filter((b) => (b.vr.perlu || b.vr.arsip) && !b.varian), timbang };
}
/** Susun dokumen kedatangan (baru, atau koreksi bila draf.id menunjuk batch yang ada). yakin = sudah ditanya soal karung sedikit / tanggal mundur. */
// ---------- BON KEDATANGAN YANG SUDAH DIBAYAR (audit 39b no. 2) ----------
// Pembayaran bon pemasok menempel ke bonnya lewat bonId (= id kedatangan) + nama pemasok PERSIS. Mesin utang pemasok (beku, tidak diubah)
// mengalirkan pembayaran yang bonnya hilang / berganti ke bon TERTUA pemasok itu, dan per tanggal membuangnya — jadi koreksi cara bayar, nama
// pemasok, tanggal sesudah bayar, nilai di bawah yang dibayar, atau hapus kedatangan membuat bon LAIN tampak lunas tanpa uang dan kas keluar
// terhitung dua kali. Dijaga di SATU pintu: susunSimpanMasuk (juga dipakai koreksi HPP) & susunHapusKedatangan.
/**
 * Uang yang DITUJUKAN ke bon kedatangan ini: pembayaran yang menunjuknya (bonId = id kedatangan, nama pemasok persis sama), tanggal tertua dulu.
 * dibayar = Σ nominalnya, paling banyak nilai bon (Σ subtotalHarga) — kelebihannya sudah mengalir ke bon lain dan bukan milik bon ini. Uang yang
 * mengalir TANPA tujuan (pembayaran lama tanpa bonId, kelebihan bayar yang terserap) tidak mengunci: aturan mesin (FIFO) memang memindahkannya,
 * dan kedatangan salah catat yang menyerap kelebihan bayar tetap bisa dihapus (tinjauan 30 Sep). dibayarMesin = nilai − sisa di hitungUtangPemasok
 * (pembanding). Kedatangan tunai / stok awal / tanpa pemasok → 0.
 */
export function ckBayarBon(batch) {
  const kosong = { dibayar: 0, dibayarMesin: 0, nilai: 0, bayar: [], bayarPertama: '' };
  const pem = String((batch && batch.pemasok) || '').trim();
  if (!batch || batch.stokAwal || !batchDiutang(batch) || !pem) return kosong;
  const id = String(batch.id); const nilai = (batch.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0);
  const bayar = ambilUtangPemasokMutasi().filter((m) => m && m.tipe === 'bayar' && String(m.bonId || '') === id && String(m.pemasok || '').trim() === pem)
    .map((m) => ({ id: m.id, tanggal: String(m.tanggal || ''), nominal: Number(m.nominal) || 0 })).sort((x, y) => x.tanggal.localeCompare(y.tanggal));
  const tunjuk = bayar.reduce((a, x) => a + x.nominal, 0); const dibayar = Math.round(Math.min(nilai, tunjuk));   // batas atas = nilai bon (bukan penjepit diam: kelebihannya bukan milik bon ini)
  const px = hitungUtangPemasok().find((p) => p.pemasok === pem); const bon = px ? px.bon.find((x) => String(x.id) === id) : null;
  return { dibayar: dibayar > 0.5 ? dibayar : 0, dibayarMesin: Math.round(nilai - (bon ? bon.sisa : 0)), nilai, bayar, bayarPertama: bayar.length ? bayar[0].tanggal : '' };
}
export const ckBayarBonId = (id) => ckBayarBon(ambilSemuaBatch().find((b) => String(b.id) === String(id)) || null);
const ckKalimatBayar = (bb) => 'Bon kedatangan ini sudah dibayar ' + RP(bb.dibayar) + (bb.bayar.length ? ' (' + bb.bayar.map((x) => x.tanggal ? tanggalPendek(x.tanggal) : 'tanpa tanggal').join(', ') + ')' : '');
const CK_BETUL_BAYAR = ' Pembetulan pembayaran bon belum ada di sistem baru.';
const CK_PINDAH = 'Pembayaran yang ditujukan ke bon ini akan pindah ke bon lain pemasok ini yang masih terbuka (atau jadi kelebihan bayar, atau hilang dari buku bon kalau pemasok ini tidak punya bon lain sama sekali)';
/**
 * Ejaan pemasok: mesin utang mengelompokkan per nama PERSIS, layar per huruf kecil — "roda mas" yang diketik jadi pemasok terpisah di mesin.
 * Nama yang sama kecuali huruf/spasi → ejaan yang sudah dipakai (kedatangan terbaru dulu, lalu pembayaran/bon lama). Nama persis yang sudah
 * dipakai, atau pemasok baru, apa adanya. kecualiId = kedatangan yang sedang dikoreksi (ejaan lamanya sendiri tidak memaksa).
 */
export function ckEjaanPemasok(nama, kecualiId) {
  const t = String(nama || '').trim(); const k = kunciPelanggan(t); if (!k) return t;
  const calon = [];
  ambilSemuaBatch().forEach((b) => { if (!b || b.stokAwal || b.lahirBuku || (kecualiId !== undefined && kecualiId !== null && String(b.id) === String(kecualiId))) return;
    const e = String(b.pemasok || '').trim(); if (e && kunciPelanggan(e) === k) calon.push([e, Number(b.id) || 0]); });
  ambilUtangPemasokMutasi().forEach((m) => { const e = String((m && m.pemasok) || '').trim(); if (e && kunciPelanggan(e) === k) calon.push([e, -1]); });
  if (!calon.length || calon.some((c) => c[0] === t)) return t;
  calon.sort((a, b) => b[1] - a[1]); return calon[0][0];
}
export function susunSimpanMasuk(draf, w, yakin) {
  const atur = aturCatat(); const h = hitungMasuk(draf); const pemasokKetik = String(draf.pemasok || '').trim();
  const lama = draf.id ? ambilSemuaBatch().find((b) => String(b.id) === String(draf.id)) : null;
  const pemasok = ckEjaanPemasok(pemasokKetik, lama ? lama.id : null);   // audit 39b no. 2: satu ejaan per pemasok (mesin utang memisah per ejaan)
  if (draf.id && !lama) return { tolak: 'Kedatangan yang dikoreksi sudah tidak ada' };
  if (ccFondasi(lama)) return { tolak: 'Batch fondasi (stok awal / saldo pembuka) menopang seluruh stok & modal — tidak diubah dari sini' };
  if (!pemasok) return { tolak: 'Nama pemasoknya belum diisi' };
  // tinjauan rantai laporan (no. 11): nama sistem (stok awal / tutup buku / lahir buku) bukan pemasok — bonnya akan menggantung tanpa kartu pemasok
  if (namaSistemPemasok(pemasok)) return { tolak: '"' + pemasok + '" nama yang dipakai sistem, bukan pemasok — ketik nama pemasok yang mengirim barangnya' };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(draf.tanggal || ''))) return { tolak: 'Tanggal datangnya belum benar' };
  if (h.bermasalah.length) return { tolak: 'Baris ' + h.bermasalah.map((b) => b.ke + (b.merk ? ' (' + b.merk + ')' : '')).join(', ') + ': ' + h.bermasalah[0].masalah + ' — lengkapi atau kosongkan barisnya' };
  if (!h.sah.length) return { tolak: 'Isi minimal satu baris: nama beras, jumlah karung, dan harga per kg' };
  if (h.bongkar < 0) return { tolak: 'Upah bongkar tidak boleh minus' };
  if (h.tanyaVarian.length && h.tanyaVarian[0].vr.arsip) { const x = h.tanyaVarian[0]; return { tolak: 'Baris ' + x.ke + ': ' + x.merk + ' sudah DIARSIPKAN — pilih dulu: PULIHKAN ' + x.merk + ' (sama barangnya, namanya tampil lagi) atau BEDA MUTU (jadi varian sendiri)', perluVarian: x.ke }; }
  if (h.tanyaVarian.length) { const x = h.tanyaVarian[0]; return { tolak: 'Baris ' + x.ke + ' (' + x.merk + '): harga beli ' + RP(x.hargaPerKg) + '/kg beda ' + String(x.vr.beda).replace('.', ',') + ' % dari modal ' + x.merk + ' ' + RP(Math.round(x.vr.modal)) + '/kg (batas ' + x.vr.batas + ' %) — pilih dulu: SAMA barangnya (gabung, modal dirata-rata) atau BEDA MUTU (jadi varian sendiri)', perluVarian: x.ke }; }
  const beda = h.sah.filter((b) => b.varian === 'beda');
  const salahMutu = beda.find((b) => String(b.namaMutu || '').indexOf('\u00b7') >= 0); if (salahMutu) return { tolak: 'Baris ' + salahMutu.ke + ': nama mutu tidak boleh memakai titik tengah' };
  const kembar = h.sah.find((b, i) => h.sah.findIndex((x) => x.merkSimpan === b.merkSimpan && x.beratKarung === b.beratKarung && x.merkPemasok === b.merkPemasok) !== i);   // putaran 30: dua merek pemasok satu kelas tanpa wadah = dua baris sah
  if (kembar) return { tolak: kembar.merkSimpan + (kembar.merkPemasok ? ' (' + kembar.merkPemasok + ')' : '') + ' ' + kembar.beratKarung + ' kg tertulis dua kali — gabungkan jadi satu baris' };
  const kelasSalah = h.sah.find((b) => b.baru && b.kelasPilih && String(draf.baris[b.ke - 1].kelas || '').trim() && !b.kelas);
  if (kelasSalah) return { tolak: 'Baris ' + kelasSalah.ke + ' (' + kelasSalah.merkKetik + '): kelas "' + String(draf.baris[kelasSalah.ke - 1].kelas).trim() + '" tidak dikenal — pilih dari pil kelas, atau "tanpa kelas"' };
  if (h.karung < atur.minKarung && !yakin) return { tolak: 'Cuma ' + h.karung + ' karung — biasanya satu mobil minimal ' + atur.minKarung + ' karung. Ketuk sekali lagi kalau memang benar', perluYakin: true };
  // putaran 31.3: kedatangan BARU bertanggal sebelum cocokkan terakhir nama itu → dua ketukan (koreksi kedatangan lama tidak ditanya: tanggalnya sudah ada)
  const mundur = lama ? '' : ckKalimatMundur(draf.tanggal, h.sah.map((b) => ({ nama: b.merkSimpan, cocok: ckCocokTerakhir(b.merkSimpan) })), 'datang');
  if (mundur && !yakin) return { tolak: mundur, perluYakin: true };
  if (lama && ckKosong(draf.alasan)) return { tolak: 'Koreksi kedatangan butuh alasan (mis. salah ketik harga)' };
  // putaran 25: kedatangan bulan terkunci tidak bisa dikoreksi (K2); kedatangan baru tidak boleh bertanggal bulan terkunci
  const kunci = (lama && tolakKunci('batchMasuk', lama, 'kedatangan ini tidak bisa dikoreksi. Jumlah kg yang salah: Stok › Cocokkan HARI INI. harga modal kedatangan bulan terkunci tidak bisa dikoreksi; selisihnya terbawa ke HPP penjualan sisa stoknya (keputusan owner K2)')) || tolakKunciTanggal(draf.tanggal, 'kedatangan tidak bisa dicatat di bulan itu; catat dengan tanggal hari ini dan sebut tanggal aslinya di alasan');
  if (kunci) return { tolak: kunci, pembalik: lama ? 'cocok' : '' };
  // tinjauan E1 (no. 3): koreksi yang memindah kg antar nama di buku yang sudah bergerak → ditolak + jalan lain (pindah buku / Cocokkan); tidak boleh stok hantu
  const geser = lama ? ckGeserKoreksi(lama, ckBarisGeser(h)) : null;
  if (geser && geser.tolak) return { tolak: geser.tolak, pembalik: geser.pindah.length ? 'pindahNama' : 'cocok', pindahTeks: geser.pindahTeks };
  const cara = draf.caraBayar === 'utang' ? 'utang' : 'tunai';
  const bb = lama ? ckBayarBon(lama) : null;   // audit 39b no. 2: bon yang sudah dibayar (pembayaran bertunjuk) — cara bayar, pemasok, tanggal & nilai minimal dikunci
  if (bb && bb.dibayar <= 0 && bb.dibayarMesin > 0 && String(draf.tanggal) !== String(lama.tanggal || '')) return { tolak: 'Bon kedatangan ini sudah terbayar ' + RP(bb.dibayarMesin) + ' menurut buku bon (aliran pembayaran pemasok ini) — tanggal datangnya (' + tanggalPendek(lama.tanggal) + ') tidak bisa diubah: urutan bon tertua & neraca per tanggal ikut bergeser.' + CK_BETUL_BAYAR };
  if (bb && bb.dibayar > 0) {
    if (cara !== 'utang') return { tolak: ckKalimatBayar(bb) + ' — tidak bisa diubah jadi tunai. ' + CK_PINDAH + ', dan kas keluarnya terhitung dua kali (belanja tunai + bayar bon).' + CK_BETUL_BAYAR };
    if (pemasok !== String(lama.pemasok || '').trim()) return { tolak: ckKalimatBayar(bb) + ' atas nama ' + String(lama.pemasok || '').trim() + ' — nama pemasoknya tidak bisa diganti. Pembayarannya tetap atas nama ' + String(lama.pemasok || '').trim() + ' dan akan pindah ke bon ' + String(lama.pemasok || '').trim() + ' lain yang masih terbuka (atau jadi kelebihan bayar, atau hilang dari buku bon kalau tidak ada bon lain sama sekali).' + CK_BETUL_BAYAR };
    if (String(draf.tanggal) !== String(lama.tanggal || '')) return { tolak: ckKalimatBayar(bb) + ' — tanggal datangnya (' + tanggalPendek(lama.tanggal) + ') tidak bisa diubah: pembayarannya menunjuk bon bertanggal itu (buku bon & neraca per tanggal ikut bergeser).' + CK_BETUL_BAYAR };
    // nilai bon yang TERTULIS = baris karung draf + baris bal lama yang ikut tertulis apa adanya (audit 39b no. 30)
    if (h.nilaiBeras + h.nilaiBal + 0.5 < bb.dibayar) return { tolak: ckKalimatBayar(bb) + ' — nilai bon sesudah koreksi ' + RP(h.nilaiBeras + h.nilaiBal) + ' lebih kecil; kelebihan ' + RP(bb.dibayar - h.nilaiBeras - h.nilaiBal) + ' akan pindah ke bon lain yang masih terbuka (atau jadi kelebihan bayar) tanpa uang baru. Periksa harga & jumlahnya (nilai bon boleh naik, tidak boleh di bawah yang sudah dibayar).' };
  }
  const data = { id: lama ? lama.id : w.idUnik(), tanggal: draf.tanggal, pemasok, biayaBongkar: h.bongkar, caraBayar: cara,
    merkList: h.sah.map((b, i) => Object.assign({ id: String(i + 1), merk: b.merkSimpan, satuan: 'karung', jumlahKarung: b.jumlahKarung, beratKarung: b.beratKarung, totalKg: b.totalKg, hargaPerKg: b.hargaPerKg, subtotalHarga: b.subtotalHarga },
      b.indukUkuran ? { indukUkuran: b.indukUkuran } : {}, b.merkPemasok ? { merkPemasok: b.merkPemasok } : {}))
      // paket brief 9 Okt: kolom timbang & mutu hanya yang diisi (kosong = tidak ditulis → kedatangan tanpa isian berbentuk lama persis)
      .map((r, i) => Object.assign(r, h.sah[i].cek.kolom))
      .concat(ckBarisBal(lama).map((m, j) => Object.assign({}, m, { id: String(h.sah.length + j + 1) }))) };   // putaran 30: merkPemasok = keterangan merek pemasok pada kelas tanpa wadah; audit 39b no. 30: baris bal di belakang, apa adanya
  // owner 7 Okt: nomor bon pemasok (noBon, pembetulan bon) ikut terbawa saat kedatangan dikoreksi
  if (lama) { data.jam = lama.jam || w.jam; data.alasanKoreksi = String(draf.alasan).trim(); data.riwayat = (Array.isArray(lama.riwayat) ? lama.riwayat : []).concat([{ teks: 'dikoreksi: ' + String(draf.alasan).trim(), tanggal: w.tanggal, jam: w.jam }]); Object.keys(lama).forEach((k) => { if (data[k] === undefined && ['oleh', 'perangkat', 'catatan', 'noBon'].indexOf(k) >= 0) data[k] = lama[k]; }); }
  else data.jam = w.jam;
  const tempo = cara === 'utang' && atur.tempoHari > 0 ? ' · jatuh tempo ' + atur.tempoHari + ' hari' : '';
  // varian: jenis beras ikut induknya (satu kunci baru di peta yang sama); harga jualnya ditawarkan layar sesudah tersimpan
  const dokumen = [{ koleksi: 'batchMasuk', data }]; const dj = vrDokJenis(beda.map((b) => ({ varian: b.merkSimpan, induk: b.merk })), w); if (dj) dokumen.push(dj);
  // nama arsip yang dijawab "sama barangnya" dipulihkan di kiriman yang sama (juga varian yang pernah diarsipkan lalu datang lagi)
  const arsip = arPeta(); const pulih = h.sah.filter((b) => arsip[arKunciBeras(b.merkSimpan)]).map((b) => arKunciBeras(b.merkSimpan)); const dp = arDokPulihBanyak(pulih, w); if (dp) dokumen.push(dp);
  const varianBaru = beda.filter((b, i) => beda.findIndex((x) => x.merkSimpan === b.merkSimpan) === i).map((b) => ({ merk: b.merkSimpan, induk: b.merk, hargaBeli: b.hargaPerKg, modalKg: b.hppPerKg, baru: !vrAda(b.merkSimpan) }));
  // putaran 30: kelas merek baru (berwadah / merek-kelas) ditulis DALAM kiriman yang sama — tebakan yang dibiarkan ditulis sebagai tebakan, pilihan owner sebagai owner
  const kelasBaru = h.sah.filter((b) => b.baru && !b.keSendiri && (b.kelas || b.kelasPilih)).map((b) => ({ merk: b.merkKetik, kelas: b.kelas, asal: b.kelasAsal }));
  const dk = kmDokKelas(kelasBaru, w); if (dk) dokumen.push(dk);
  const ketKelas = h.sah.filter((b) => b.baru && (b.kelas || b.keSendiri)).map((b) => b.keSendiri ? b.merkKetik + ' dibukukan sebagai ' + b.merk + ' (merek pemasok dicatat)' : b.merkKetik + ' → kelas ' + b.kelas + (b.kelasAsal === 'tebakan' ? ' (tebakan)' : ''));
  return { dokumen, hitung: h, varianBaru,
    patch: { varianTawar: varianBaru.length ? varianBaru : null, kabar: (lama ? 'Koreksi tersimpan: ' : 'Barang masuk tersimpan: ') + pemasok + (pemasok !== pemasokKetik ? ' (ditulis dengan ejaan yang sudah dipakai, bukan "' + pemasokKetik + '")' : '') + ' · ' + h.karung + ' karung · ' + ckKG(h.kg) + ' · beras ' + RP(h.nilaiBeras) + (h.nilaiBal ? ' + baris bal ' + RP(h.nilaiBal) + ' (tidak diubah)' : '') + (h.bongkar ? ' + bongkar ' + RP(h.bongkar) : '')
      + (cara === 'utang' ? ' — jadi bon pemasok' + tempo : ' — tunai, keluar dari laci hari ini') + (h.bongkar ? '; bongkar selalu tunai' : '') + '. Stok & modal tiap nama ikut berubah.'
      + (varianBaru.length ? ' Varian: ' + varianBaru.map((x) => x.merk + (x.baru ? ' (nama baru, jenis beras ikut ' + x.induk + ')' : ' (gabung ke varian yang sudah ada)')).join(', ') + ' — kolam lama tidak disentuh.' : '')
      + (dp ? ' Dipulihkan dari arsip: ' + pulih.map((k) => k.slice(2)).join(', ') + '.' : '') + (ketKelas.length ? ' Kelas: ' + ketKelas.join('; ') + '.' : ''), kabarAwas: false } };
}
// ---------- KOREKSI YANG MEMINDAH KG ANTAR NAMA (tinjauan E1 no. 3) ----------
const ckKgPerNama = (rows) => { const o = {}; (rows || []).forEach((m) => { if (!m || m.bentuk === 'bal' || !m.merk) return; o[m.merk] = ckB2((o[m.merk] || 0) + (Number(m.totalKg) || 0)); }); return o; };
/** Baris karung draf koreksi untuk ckGeserKoreksi: nama buku sesudah koreksi, kg, dan nama yang tertulis sebelumnya (merkAsal draf). */
const ckBarisGeser = (h) => h.sah.map((b) => ({ merk: b.merkSimpan, totalKg: b.totalKg, merkAsal: b.merkAsal || '' }));
/**
 * Koreksi / hapus kedatangan yang MENGGESER kg antar NAMA buku. lama = kedatangan tersimpan; baruRows = baris karung sesudahnya ([] = dihapus).
 *  · (a) kg pindah nama (ganti nama baris, atau satu nama turun sementara nama lain naik) padahal buku nama lama SUDAH BERGERAK sejak tanggal kedatangan itu
 *    (terjual / diaduk / dipindah / diretur / dicocokkan — vrGerakBuku): karungnya mungkin sudah keluar atas nama lama, buku nama baru akan berisi karung yang
 *    sudah tidak ada dan nama lama minus. Jalan lain: kedatangan dibiarkan, SISA buku nama lama pindah buku ke nama baru (pindah, modal ikut) — ckSusunPindahKoreksi.
 *  · (b) nama lama HILANG dari semua kedatangan padahal bukunya pernah bergerak: mesin beku melewatkan catatan atas nama tanpa baris batch → catatan itu lepas
 *    dari buku dan stoknya muncul lagi (stok HANTU; contoh kotak pasir: total 1.250 → 1.300 kg). Jalan lain: Cocokkan, atau pindah buku bila namanya yang salah.
 * Nama yang bukunya belum bergerak (atau hanya bergerak SEBELUM kedatangan ini dan masih punya kedatangan lain) boleh diganti seperti biasa.
 * → { tolak: '' | kalimat, pindah: [{ dari, ke, kg }], pindahTeks }
 */
export function ckGeserKoreksi(lama, baruRows) {
  const hasil = { tolak: '', pindah: [], pindahTeks: '' }; if (!lama) return hasil;
  const kL = ckKgPerNama(lama.merkList), kB = ckKgPerNama(baruRows);
  const turun = Object.keys(kL).filter((m) => (kB[m] || 0) < kL[m] - 0.004); const naik = Object.keys(kB).filter((m) => kB[m] > (kL[m] || 0) + 0.004);
  if (!turun.length) return hasil;
  const sejak = String(lama.tanggal || ''); const tgl = tanggalPendek(sejak) || 'tanpa tanggal';
  const lainAda = (m) => ambilSemuaBatch().some((b) => String(b.id) !== String(lama.id) && (b.merkList || []).some((x) => x && x.merk === m && x.bentuk !== 'bal'));
  const masalah = [];
  turun.forEach((m) => { const hilang = !((kB[m] || 0) > 0.004) && !lainAda(m); const gS = naik.length ? vrGerakBuku(m, sejak) : []; const gA = hilang ? vrGerakBuku(m, '') : [];
    if (gS.length || gA.length) masalah.push({ m, hilang, gerak: gS.length ? gS : gA, sejak: gS.length > 0 }); });
  if (!masalah.length) return hasil;
  // pasangan nama lama → nama baru: baris yang diganti namanya (merkAsal draf); tanpa itu, geseran satu-satu dari selisih kg
  const pasang = []; const tambah = (dari, ke, kg) => { if (!(kg > 0.004) || dari === ke) return; const ada = pasang.find((x) => x.dari === dari && x.ke === ke); if (ada) ada.kg = ckB2(ada.kg + kg); else pasang.push({ dari, ke, kg: ckB2(kg) }); };
  (baruRows || []).forEach((r) => { if (r && r.merkAsal && r.merkAsal !== r.merk && turun.indexOf(r.merkAsal) >= 0 && naik.indexOf(r.merk) >= 0) tambah(r.merkAsal, r.merk, Math.min(Number(r.totalKg) || 0, kB[r.merk] - (kL[r.merk] || 0))); });
  const gantiNama = pasang.length > 0;   // ada baris yang benar-benar diganti namanya (bukan jumlah satu nama turun + baris lain bertambah)
  if (!pasang.length && turun.length === 1 && naik.length === 1) tambah(turun[0], naik[0], Math.min(kL[turun[0]] - (kB[turun[0]] || 0), kB[naik[0]] - (kL[naik[0]] || 0)));
  // yang bisa dipindah buku = sisa buku nama lama yang SEKARANG ada (bagian yang sudah keluar tidak ikut), paling banyak kg yang digeser
  const stok = hitungStokKarungPerMerk(); const sisa = {};
  masalah.filter((x) => x.sejak).forEach((x) => { sisa[x.m] = Math.max(0, ckB2((stok[x.m] || {}).sisaKg || 0)); });
  pasang.forEach((p) => { if (sisa[p.dari] === undefined) return; const kg = ckB2(Math.min(p.kg, sisa[p.dari])); sisa[p.dari] = ckB2(sisa[p.dari] - kg); if (kg > 0.004) hasil.pindah.push({ dari: p.dari, ke: p.ke, kg }); });
  hasil.pindahTeks = hasil.pindah.map((x) => 'Pindah buku ' + ckKG(x.kg) + ' ' + x.dari + ' → ' + x.ke).join(' · ');
  hasil.tolak = masalah.map((x) => x.sejak
    ? x.m + ' di kedatangan ' + tgl + ' tidak bisa dipindah ke nama lain lewat koreksi: buku ' + x.m + ' sudah ' + x.gerak.join(' / ') + ' sejak kedatangan itu — karungnya mungkin sudah keluar atas nama ' + x.m + ', jadi nama baru akan berisi karung yang sudah tidak ada.'
      + (hasil.pindah.some((y) => y.dari === x.m) ? ' Jalan lain: nama di kedatangan ini dibiarkan, SISA buku ' + x.m + ' sekarang dipindah buku ke nama barunya (modal ikut, nilai stok & laba tetap) — tombol di bawah.' : ' Sisa buku ' + x.m + ' sekarang ' + ckKG(Math.max(0, (stok[x.m] || {}).sisaKg || 0)) + ' — tidak ada yang bisa dipindah buku; kalau karungnya masih ada di gudang, hitung lewat Stok › Cocokkan.')
    : x.m + ' hanya tertulis di kedatangan ' + tgl + ' dan bukunya sudah ' + x.gerak.join(' / ') + ': tanpa baris ini catatan itu lepas dari buku dan stoknya muncul lagi (stok hantu). Barang yang tidak pernah ada: Stok › Cocokkan HARI INI (kg turun); nama yang salah: ganti nama barisnya saja (jangan dihapus) supaya sisa bukunya bisa dipindah buku.').join(' ')
    + (!gantiNama && masalah.some((x) => x.sejak) ? ' Kalau maksudnya hanya membetulkan jumlah ' + masalah.filter((x) => x.sejak).map((x) => x.m).join(', ') + ' dan menambah baris lain, simpan sebagai dua koreksi terpisah.' : '');
  return hasil;
}
/**
 * JALAN LAIN koreksi nama yang ditolak (tinjauan E1 no. 3): kedatangan TIDAK diubah; sisa buku nama lama sekarang pindah buku ke nama baru — buku nama baru
 * lahir bila perlu (batch 0 kg) + produksiKemasan jadi-karung-utuh (modal rata-rata nama lama ikut; nilai stok & laba tetap). Dua ketukan.
 */
export function ckSusunPindahKoreksi(draf, w, yakin) {
  const lama = draf && draf.id ? ambilSemuaBatch().find((b) => String(b.id) === String(draf.id)) : null; if (!lama) return { tolak: 'Kedatangan yang dikoreksi sudah tidak ada' };
  const G = ckGeserKoreksi(lama, ckBarisGeser(hitungMasuk(draf))); if (!G.pindah.length) return { tolak: 'Tidak ada sisa buku yang bisa dipindah untuk koreksi ini' };
  const alasan = String(draf.alasan || '').trim(); const tgl = tanggalPendek(lama.tanggal);
  if (!yakin) return { tolak: G.pindahTeks + ' — modal ikut, nilai stok & laba tetap; kedatangan ' + tgl + ' tidak diubah. Ketuk sekali lagi', perluYakin: true };
  const dokumen = []; const lahir = wbDokLahir(G.pindah.map((x) => ({ merk: x.ke })), w); if (lahir) dokumen.push(lahir);
  const ambilG = {};
  G.pindah.forEach((x) => dokumen.push(wbDokPindah([{ merk: x.dari, kg: x.kg }], x.ke, w, { pindahNama: { dari: x.dari, ke: x.ke, kedatangan: String(lama.id) },
    keterangan: 'Pindah buku ' + ckKG(x.kg) + ' ' + x.dari + ' → ' + x.ke + ' (nama di kedatangan ' + tgl + ' salah' + (alasan ? ': ' + alasan : '') + ')' }, ambilG)));
  return { dokumen, patch: { kabar: G.pindahTeks + ' — tersimpan. Kedatangan ' + tgl + ' tetap atas nama lamanya; modal ikut, nilai stok & laba tidak berubah.', kabarAwas: false } };
}
// ---------- BUKU PER UKURAN (owner 28 Sep: karung 50 kg & 25 kg merek yang sama = buku masing-masing) ----------
/** Merek yang TIDAK memakai buku per ukuran (audit 39b no. 35, owner 30 Sep): dijual per liter langsung dari karungnya, atau kelas mutu tanpa wadah (kelas sendiri). */
export function ckTanpaBukuUkuran() { const out = {}; wbLiteranLangsung().daftar.forEach((m) => { out[m] = true; }); Object.keys(kmKelasSendiri()).forEach((m) => { out[m] = true; }); return out; }
/**
 * Buku per ukuran milik merek yang kini TIDAK memakai buku per ukuran (ckTanpaBukuUkuran) dan masih berisi → tawarkan GABUNG BALIK ke buku induk
 * (satu pindah buku, modal ikut, laba & neraca tidak berubah — bukan cocokkan). Sesudahnya induk kembali satu buku untuk semua ukuran.
 */
export function ckCalonGabungUkuran() {
  const st = ingatStokKarung(); const u = petaUkuran(); const g = ukuranDigabung(); const tanpa = ckTanpaBukuUkuran();
  return Object.keys(u).filter((k) => tanpa[u[k].induk] && !g[k] && st[k] && (st[k].sisaKg || 0) > 0.004).sort()
    .map((k) => ({ kunci: k, induk: u[k].induk, berat: u[k].berat, kg: ckB2(st[k].sisaKg || 0), indukKg: ckB2((st[u[k].induk] || {}).sisaKg || 0) }));
}
/** GABUNG BALIK satu buku per ukuran ke induknya (dua ketukan): seluruh isinya pindah buku → induk, modal ikut; bertanda gabungUkuran supaya induk tidak lagi terpisah. */
export function ckSusunGabungUkuran(kunci, w, yakin) {
  const K = String(kunci || ''); const c = ckCalonGabungUkuran().find((x) => x.kunci === K);
  if (!c) return { tolak: K + ' tidak perlu digabung (bukan buku per ukuran merek per liter / kelas sendiri, sudah digabung, atau kosong)' };
  if (!yakin) return { tolak: 'Gabungkan buku: ' + ckKG(c.kg) + ' di buku ' + K + ' pindah ke buku ' + c.induk + ' (' + ckKG(c.indukKg) + ' → ' + ckKG(ckB2(c.indukKg + c.kg)) + '), modal ikut, laba tidak berubah. Sesudah ini karung ' + c.berat + ' kg ' + c.induk + ' dibukukan & dijual dari buku ' + c.induk + ' lagi. Ketuk sekali lagi', perluYakin: 'gabung' };
  return { dokumen: [wbDokPindah([{ merk: K, kg: c.kg }], c.induk, w, { gabungUkuran: { dari: K, induk: c.induk, berat: c.berat }, keterangan: 'Gabung balik buku per ukuran: ' + ckKG(c.kg) + ' ' + K + ' → ' + c.induk + ' (merek per liter / kelas sendiri tidak memakai buku per ukuran)' })],
    patch: { kabar: 'Buku ' + K + ' digabung balik: ' + ckKG(c.kg) + ' sekarang di buku ' + c.induk + ' (' + ckKG(ckB2(c.indukKg + c.kg)) + '). Modal ikut, laba tidak berubah.', kabarAwas: false } };
}
/** Merek yang datang DUA ukuran (karung 50 & 25 kg tercatat atas namanya) dan stok lamanya belum dipisah. Merek per liter / kelas sendiri tidak ditawarkan (39b no. 35). */
export function ckCalonPisahUkuran() {
  const st = ingatStokKarung(); const u = petaUkuran(); const bw = petaBukuWadah(); const sudah = {}; const tanpa = ckTanpaBukuUkuran();
  ambilProduksiBerlaku().forEach((p) => { if (p.pisahUkuran && p.pisahUkuran.induk) sudah[p.pisahUkuran.induk] = true; });
  return Object.keys(st).filter((m) => !u[m] && !bw[m] && !sudah[m] && !tanpa[m] && merkPunyaKarungBerat(m, 50) && merkPunyaKarungBerat(m, 25)).sort()
    .map((m) => ({ merk: m, bukuKg: ckB2(st[m].sisaKg || 0), baru: kunciUkuran(m, 25) }));
}
/**
 * PISAHKAN stok lama (keputusan owner: "hitung karung 25 kg"): n karung 25 kg utuh yang dihitung di gudang pindah dari buku merek ke buku 'Merek 25 kg'
 * (modal rata-rata buku lama ikut — laba & neraca tetap); sisanya tetap di buku merek (karung 50 kg + yang sudah dibuka). Dua ketukan. Sesudahnya karung
 * 25 kg merek itu dijual, diretur, dan dicatat masuk dari bukunya sendiri.
 */
export function ckSusunPisahUkuran(merk, nKetik, w, yakin) {
  const M = String(merk || ''); const c = ckCalonPisahUkuran().find((x) => x.merk === M);
  if (!c) return { tolak: M + ' tidak perlu dipisah (bukan merek dua ukuran, atau sudah dipisah)' };
  const t = String(nKetik === undefined || nKetik === null ? '' : nKetik).trim();
  if (t === '') return { tolak: 'Hitung dulu karung 25 kg ' + M + ' yang masih utuh di gudang, lalu tulis jumlahnya (0 kalau tidak ada)' };
  const n = Number(t.replace(',', '.')); if (!(n >= 0) || Math.round(n) !== n) return { tolak: 'Jumlah karung harus bilangan bulat 0 atau lebih' };
  const kg = n * 25; const B = kunciUkuran(M, 25);
  if (kg > c.bukuKg + 0.004) return { tolak: n + ' karung 25 kg = ' + kg + ' kg, lebih dari buku ' + M + ' (' + ckKG(c.bukuKg) + ') — cocokkan tumpukan ' + M + ' dulu' };
  if (!yakin) return { tolak: 'Pisahkan buku: ' + n + ' karung 25 kg (' + kg + ' kg) pindah dari buku ' + M + ' ke buku ' + B + ', modal rata-rata ikut. Sesudah ini karung 25 kg ' + M + ' punya bukunya sendiri. Ketuk sekali lagi', perluYakin: 'pisah' };
  const dokumen = []; const lahir = wbDokLahir([{ merk: B, indukUkuran: M, berat: 25 }], w); if (lahir) dokumen.push(lahir);
  dokumen.push(wbDokPindah([{ merk: M, kg }], B, w, { pisahUkuran: { induk: M, berat: 25, karung: n }, keterangan: 'Pisahkan buku per ukuran: ' + n + ' karung 25 kg ' + M + ' → ' + B }));
  return { dokumen, patch: { kabar: 'Buku ' + M + ' dipisah: ' + n + ' karung 25 kg (' + kg + ' kg) sekarang di buku ' + B + ' — buku ' + M + ' = karung 50 kg & yang sudah dibuka. Modal ikut, laba tidak berubah.', kabarAwas: false } };
}
/** Buku kedatangan: terbaru dulu. */
export function daftarKedatangan(n) {
  const A = aturCatat(); const semua = ambilSemuaBatch().filter((b) => !b.lahirBuku).sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0));
  return semua.slice(0, n || 30).map((b) => { const baris = (b.merkList || []); const karung = baris.reduce((a, m) => a + (m.satuan === 'karung' ? (Number(m.jumlahKarung) || 0) : 0), 0); const kg = ckB2(baris.reduce((a, m) => a + (Number(m.totalKg) || 0), 0));
    const nilai = baris.reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0);
    return { id: b.id, tanggal: b.tanggal || '', jam: b.jam || '', pemasok: b.pemasok || (b.stokAwal ? 'stok awal' : b.tutupBuku ? 'saldo pembuka' : '—'), karung, kg, nilai, cara: b.caraBayar === 'utang' ? 'utang' : 'tunai', fondasi: ccFondasi(b), adaBal: baris.some((m) => m.bentuk === 'bal'),
      ringkas: baris.map((m) => m.merk + (m.merkPemasok ? ' (' + m.merkPemasok + ')' : '') + ' ' + (m.bentuk === 'bal' ? (m.jumlahBal || 0) + ' bal' : (m.jumlahKarung || 0) + '×' + (m.beratKarung || '?'))).join(' · '), dikoreksi: !!b.alasanKoreksi, riwayat: Array.isArray(b.riwayat) ? b.riwayat : [],
      cek: tmKedatangan(b, A) }; });   // paket brief 9 Okt: ringkasan timbang & mutu kedatangan itu (cek.teks kosong = belum ditimbang & tidak dicek)
}
/** Draf koreksi dari batch tersimpan (hanya baris karung; baris bal tidak diubah dari sini). */
export function drafDariKedatangan(id) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return null;
  return { id: b.id, tanggal: b.tanggal || '', pemasok: b.pemasok || '', caraBayar: b.caraBayar === 'utang' ? 'utang' : 'tunai', bongkar: String(b.biayaBongkar || 0),
    baris: (b.merkList || []).filter((m) => m.bentuk !== 'bal').map((m) => Object.assign({ merk: m.merk || '', merkAsal: m.merk || '', jumlahKarung: String(m.jumlahKarung || ''), beratKarung: Number(m.beratKarung) || 50, hargaPerKg: String(m.hargaPerKg || '') }, m.merkPemasok ? { merkPemasok: String(m.merkPemasok) } : {}, tmDraf(m))), alasan: '', fondasi: ccFondasi(b), adaBal: (b.merkList || []).some((m) => m.bentuk === 'bal') };   // merkAsal: hanya di draf, tidak ditulis; paket brief 9 Okt: isian timbang & mutu ikut (tmDraf)
}
/** Hapus kedatangan: batch + pasangan produksi beli-jadi (dariBatch) dicabut bersama (hapusBatch index.html), jejaknya ke bukuHapus. */
export function susunHapusKedatangan(id, alasan, w) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return { tolak: 'Kedatangan itu sudah tidak ada' };
  if (ccFondasi(b)) return { tolak: 'Batch fondasi (' + (b.tutupBuku ? 'saldo pembuka tutup buku' : 'stok awal') + ') menopang seluruh stok & modal — tidak bisa dihapus dari sini' };
  const kunci = tolakKunci('batchMasuk', b, 'kedatangan ini tidak bisa dihapus. Barang yang tidak pernah ada: Stok › Cocokkan HARI INI (kg turun). Utang/uang yang terlanjur tercatat tidak punya pembetul (K2)'); if (kunci) return { tolak: kunci, pembalik: 'cocok' };   // putaran 25
  const bb = ckBayarBon(b); if (bb.dibayar > 0) return { tolak: ckKalimatBayar(bb) + ' — kedatangan ini tidak bisa dihapus: uangnya sudah keluar untuk bon ini. ' + CK_PINDAH + '.' + CK_BETUL_BAYAR };   // audit 39b no. 2
  // tinjauan E1 (no. 3): nama yang HANYA ada di kedatangan ini dan bukunya sudah bergerak → menghapusnya membuat catatan itu lepas dari buku (stok hantu)
  const lepas = ckGeserKoreksi(b, []); if (lepas.tolak) return { tolak: lepas.tolak, pembalik: 'cocok' };
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
  // putaran 28: titik pindahan awal stok wadah BUKAN hitungan (isinya angka tercatat, bukan kotak yang dihitung) — tidak menyetel "terakhir dicocokkan"
  ambilWadahLiteran().forEach((d) => { if (d.tipe === 'isi' && d.wadah && !d.pindahAwal) catat('wadah|' + d.wadah, d);
    if (d.tipe === 'karungIsi' && d.dariCocok && d.merk) catat('karungKhusus|' + d.merk + '|#|' + (d.wadah || ''), d); });   // audit 39b no. 5: karung berbuku sendiri
  ambilPenyesuaianKemasan().forEach((d) => { if (d.namaProduk) catat('kemasan|' + kunciKemasan(d.namaProduk, d.ukuranKemasan), d); });
  // owner 7 Okt: karung bekas yang LAHIR dari karung habis (opname ±1 bertanda lahirKarungBekas) & penyetel nilainya (nilaiKarungBekas) bukan hitungan fisik — tidak menyetel "terakhir dicocokkan"
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && d.jenis && !d.lahirKarungBekas && !d.nilaiKarungBekas) catat('kantong|' + d.jenis, d); });
  return peta;
}
/**
 * Buku KHUSUS karung (karung belakang / karung sisihan / kemasan adukan — petaBukuWadah, selain buku wadah) di SATU tempat = buku − catatan kolam kunci yang
 * sama di tempat lain (satu buku adukan bisa terbuka di dua tempat). Bukan buku khusus / bukunya belum lahir → null (pakai catatan kolam seperti dulu).
 */
function ckBukuKarungDi(kunci, lokasi, bw, stok, kolam, bagianW) {
  const b = bw[kunci]; const st = stok[kunci]; if (!b || b.jenis === 'wadah' || !st) return null;
  const lain = kolam.reduce((a, k) => a + (k.merk === kunci && k.lokasi !== lokasi ? (k.sisaMentahKg || 0) : 0), 0);
  return ckB2((st.sisaKg || 0) - lain - ((bagianW || {})[kunci] || 0));   // tinjauan G5: bagian buku adukan yang sudah dituang ke wadah BELUM aktif bukan isi karungnya
}
/** Baris cocokkan untuk karung berbuku sendiri di luar slot wadah (tempatnya = catatan kolamnya; belum pernah dicatat → tempat asal bukunya). */
function ckKarungKhusus(atur, bw, stok, kolam, slot, bagianW) {
  const out = []; const letak = {}; const tertinggal = {}; wbKarungTertinggal().tertutup.forEach((x) => { tertinggal[x.kunci] = 1; });
  kolam.forEach((k) => { const b = bw[k.merk]; if (!b || b.jenis === 'wadah') return; (letak[k.merk] = letak[k.merk] || {})[k.lokasi] = k; });
  Object.keys(bw).sort().forEach((kunci) => { const b = bw[kunci]; if (b.jenis === 'wadah' || !stok[kunci]) return;
    // tinjauan H3: tempat yang kolamnya sudah DITUTUP (dikembalikan / dihapus habis) bukan tempat karung itu lagi — tidak dapat baris (menyimpannya menghidupkan
    // lagi karung itu di slot). Sisa bukunya (bila ada) dihitung di baris LEPAS; tanpa tempat hidup sama sekali → baris lepas juga.
    const L = letak[kunci] || {}; const tempat = Object.keys(L).filter((lok) => !kolamDitutup(kunci, lok)).sort();
    // tinjauan K2: buku karung yang sudah dikembalikan tapi masih memuat sisa pengembalian lama — beresnya lewat "Pindah balik" (Stok › Wadah literan), bukan
    // dihitung 0 di sini (itu membukukan berasnya yang ada di tumpukan sebagai susut)
    if (!tempat.length && tertinggal[kunci]) return;
    if (!tempat.length) tempat.push(b.jenis === 'belakang' && !Object.keys(L).length ? b.wadah : '');
    tempat.forEach((lok) => { if (slot[kunci + '|#|' + lok]) return; const kr = L[lok] || null; const sistem = ckBukuKarungDi(kunci, lok, bw, stok, kolam, bagianW);
      const karungCatatan = kr ? ckB2(kr.sisaMentahKg) : null; if (Math.abs(sistem) <= 0.004 && !(karungCatatan > 0.004)) return;
      const nama = b.jenis === 'belakang' ? 'karung ' + b.merk + ' di belakang ' + b.wadah : b.jenis === 'karung' ? 'karung sisihan wadah ' + b.wadah : kunci + (lok ? ' di belakang ' + lok : ' (lepas)');
      const k = 'karungKhusus|' + kunci + '|#|' + lok;
      out.push({ kunci: k, kunciKarung: k, tab: 'wadah', jenis: 'karung', nama, no: '', satuan: 'kg', isiSistem: null, karungNama: kunci, lokasi: lok, karungDicatat: !!kr, karungSistem: sistem, karungBuku: true, karungCatatan,
        karungPenuh: Math.max(beratKarungBuka(b.merk || kunci), sistem), komposisi: [], sejak: kr ? kr.sejakTanggal || '' : '', stokSendiri: false, kunciStok: '', sistem, modal: hppKeluarPerKg(stok[kunci]) || 0,
        takarKg: atur.takarKg, rasio: 0, puncakKg: atur.puncakKg, susutWajarKg: atur.susutWajarKg }); }); });
  return out;
}
/** Semua barang yang bisa dicocokkan, per tab: {kunci, nama, satuan, sistem, modal, …}. */
export function barangCocok(tab) {
  const out = [];
  if (tab === 'tumpukan') { const st = ingatStokKarung(); const siap = { stok: st, pindah: pindahNama(), kolam: semuaKarungTerbuka(), bagian: wbBagianMerk() };
    // TUMPUKAN GUDANG: yang dihitung cuma karung utuh (50 / 25 kg) per nama. Tercatat = buku − karung terbuka − bagian nama ini di wadah (rantai stok).
    Object.keys(stokMerekSaja(st)).sort().forEach((m) => { const t = tumpukanGudang(m, siap);   // putaran 28: buku stok wadah bukan tumpukan gudang
      const rincian = 'buku ' + ckKG(st[m].sisaKg || 0) + (Math.abs(t.diBelakangKg) > 0.004 ? ' − karung terbuka ' + ckKG(t.diBelakangKg) : '') + (Math.abs(t.diWadahKg) > 0.004 ? ' − di wadah ' + ckKG(t.diWadahKg) : '')
        + (t.pindahKeluarKg ? ' − pindah nama ' + ckKG(t.pindahKeluarKg) : '') + (t.pindahMasukKg ? ' + pindah nama ' + ckKG(t.pindahMasukKg) : '') + ' = tumpukan ' + ckKG(t.kg) + ' (±' + t.karung + ' karung ' + t.beratKarung + ' kg)'
        + (t.lengkap ? '' : ' · perkiraan: ada wadah / karung terbuka yang belum ditandai');
      out.push({ kunci: 'tumpukan|' + m, tab, nama: m, satuan: 'kg', sistem: ckB2(t.kg), buku: ckB2(st[m].sisaKg || 0), modal: hppKeluarPerKg(st[m]), rincian, lengkap: t.lengkap,
        beratKarung: t.beratKarung, karungSistem: t.karung }); }); }
  else if (tab === 'wadah') { const atur = aturWadah(); const bw = petaBukuWadah(); const stok = ingatStokKarung(); const kolam = semuaKarungTerbuka(); const bagianW = wbBagianMerk(); const slot = {};
    // WADAH LITERAN: per petak W1–W8 — isi kotak + karung terbuka di belakangnya. Tercatat isi = Σ komposisi (merek asal); belum pernah disamakan = null (tidak ditebak).
    // audit 39b no. 5 (G1): karung yang punya BUKU SENDIRI (karung belakang, kemasan adukan) — tercatat = BUKUNYA di tempat itu, bukan catatan kolam
    // (dulu dibanding catatan: buku yang sudah selisih tetap selisih sesudah dicocokkan). Catatannya tetap disebut bila berbeda.
    atur.daftar.forEach((W, i) => { const K = wbKomposisi(W); const kn = karungUntukWadah(W); const kb = karungBelakang(kn.merk, W);
      const bkr = kn.dariCatatan ? ckBukuKarungDi(kn.merk, W, bw, stok, kolam, bagianW) : null; if (kn.dariCatatan) slot[kn.merk + '|#|' + W] = 1;
      const isiSistem = K.diketahui ? ckB2(K.totalKg) : null; const karungCatatan = kb.diketahui ? ckB2(kb.sisaMentahKg) : null; const karungSistem = bkr !== null ? bkr : karungCatatan;
      out.push({ kunci: 'wadah|' + W, kunciKarung: 'wadahKarung|' + W, tab, nama: W, no: 'W' + (i + 1), satuan: 'kg', isiSistem, karungNama: kn.merk, karungDicatat: kn.dariCatatan, karungSistem, karungBuku: bkr !== null, karungCatatan,
        karungLabel: bw[kn.merk] && bw[kn.merk].jenis === 'belakang' && bw[kn.merk].merk ? bw[kn.merk].merk : kn.merk,
        karungPenuh: Math.max(kb.penuhKg || beratKarungBuka(kn.merk), bkr || 0), komposisi: K.positif, sejak: K.sejak, stokSendiri: !!K.stokSendiri, kunciStok: K.kunci || '', sistem: ckB2((isiSistem || 0) + (karungSistem || 0)), modal: wbModalPerKg(W),
        takarKg: atur.takarKg, rasio: wbRasio(W), puncakKg: atur.puncakKg, susutWajarKg: atur.susutWajarKg }); });
    // audit 39b no. 5 (G3 G4): karung berbuku sendiri yang BUKAN karung slot wadah — karung belakang kedua dst., karung sisihan wadah, kemasan adukan lepas
    ckKarungKhusus(atur, bw, stok, kolam, slot, bagianW).forEach((x) => out.push(x)); }
  else if (tab === 'kemasan') { const st = ingatStokKemasan(); Object.keys(st).sort().forEach((k) => { const s = st[k]; out.push({ kunci: 'kemasan|' + k, tab, nama: s.namaProduk + ' ' + String(s.ukuranKemasan).replace('.', ',') + ' kg', satuan: 'unit', sistem: s.sisaUnit || 0, modal: s.hppRataRataPerUnit || 0, namaProduk: s.namaProduk, ukuranKemasan: s.ukuranKemasan }); }); }
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
    const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = ada ? (b.tab === 'tumpukan' ? ckRpKarung(b.nama, selisih, b.modal) : Math.round(selisih * b.modal)) : 0; const akhir = peta[b.kunci] || null;
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
  const atur = aturCatat(); const peta = cocokAkhirPeta(); const H = hitung || {}; const A = alasan || {}; const Y = yakin || {}; const stok = ingatStokKarung(); const hari = hariIniIso(new Date(Date.now()));
  const modal = (m) => (stok[m] || {}).hppTerakhirPerKg || 0;
  // modal FIFO (owner 9 Okt): selisih merek karung = irisan karung terlama (mesin/modal-fifo.js); wadah & saklar mati = kg × modal rata-rata (rumus lama)
  const nilaiAlokasi = (m, kg) => { const st = stok[m]; return st && st.metode === 'fifo' ? nilaiSelisihKg(st, kg) : kg * modal(m); };
  // tinjauan H2: satu buku karung yang terbuka di beberapa tempat — tercatat tiap tempat = catatannya + selisih buku−catatan (e). Bila dua tempat dihitung
  // dalam satu simpan, e dipotong SEKALI (tempat pertama); tempat berikutnya dibanding catatannya sendiri.
  const kenaE = {};
  const baris = barangCocok('wadah').map((b) => {
    const adaIsi = b.jenis !== 'karung' && ccAda(H[b.kunci]); const adaKr = ccAda(H[b.kunciKarung]); const ada = adaIsi || adaKr;
    const isiH = adaIsi ? ckB2(ckAngka(H[b.kunci])) : null; const krH = adaKr ? ckB2(ckAngka(H[b.kunciKarung])) : null;
    const alokasi = {}; const tambah = (m, kg) => { if (!m || !kg) return; alokasi[m] = ckB2((alokasi[m] || 0) + kg); };
    let komposisiBaru = null;
    if (adaIsi) { const kb = wbKomposisiBaru(b.nama, isiH); komposisiBaru = kb.komposisi; if (b.isiSistem !== null) Object.keys(kb.alokasi).forEach((m) => tambah(m, kb.alokasi[m])); }
    const keduaE = adaKr && b.karungBuku && b.karungCatatan !== null && kenaE[b.karungNama]; if (adaKr && b.karungBuku) kenaE[b.karungNama] = true;
    const dIsi = adaIsi && b.isiSistem !== null ? ckB2(isiH - b.isiSistem) : 0; const dKr = adaKr && b.karungSistem !== null ? ckB2(krH - (keduaE ? b.karungCatatan : b.karungSistem)) : 0;
    if (dKr) tambah(b.karungNama, dKr);
    Object.keys(alokasi).forEach((m) => { if (Math.abs(alokasi[m]) < 0.005) delete alokasi[m]; });
    const selisih = ckB2(Object.keys(alokasi).reduce((a, m) => a + alokasi[m], 0)); const rp = Math.round(Object.keys(alokasi).reduce((a, m) => a + nilaiAlokasi(m, alokasi[m]), 0));
    // tinjauan H5: jatah susut wajar per hari milik WADAH (tumpah waktu menakar), tidak diberikan lagi ke tiap karung kedua / sisihan — baris karung memakai
    // batas selisih % owner (sama dengan tumpukan)
    const lamaHari = Math.max(1, ccHariAntara(b.sejak, hari)); const wajarKg = b.jenis === 'karung' ? ckB2(Math.abs(b.karungSistem || 0) * atur.batasSelisih / 100) : ckB2(b.susutWajarKg * lamaHari);
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
  // 39b no. 5 tinjauan S7: isi kotak / sisa karung yang ditimbang tidak mungkin minus (mis. "cocok persis" atas buku minus)
  const minusH = dihit.filter((b) => (b.isiH !== null && b.isiH < 0) || (b.krH !== null && b.krH < 0));
  // tinjauan L1: karung yang bukunya masih memuat sisa pengembalian lama — di sini sisa itu akan jadi susut; pindah balik lewat kartu "Buku karung yang tertinggal" dulu
  const TT = {}; wbKarungTertinggal().berdiri.forEach((x) => { TT[x.kunci] = x; }); const lamaH = dihit.filter((b) => b.krH !== null && TT[b.karungNama]);
  const p = minusH.length ? { tolak: minusH.map((b) => b.nama).join(', ') + ': hitungan tidak boleh minus — timbangan paling kecil 0 kg', perluYakin: '' }
    : lamaH.length ? { tolak: lamaH.map((b) => 'karung ' + TT[b.karungNama].merk + ' bukunya masih memuat sisa pengembalian lama ' + ckKG(TT[b.karungNama].lamaKg)).join('; ') + ' — pindah balik dulu (Stok › Wadah literan › Buku karung yang tertinggal), baru timbang di sini; kalau tidak, sisa itu jadi susut padahal berasnya di tumpukan', perluYakin: '' } : ccPenjaga(atur, dihit, kurangAlasan, anehDaftar, lebihRp, belum, Y, kurangAlasan.map((b) => 'wadah ' + b.nama + ' selisih ' + ckKG(b.selisih) + ', di atas susut wajar ' + ckKG(b.wajarKg)).join('; ') + ' — isi alasannya dulu', '(melebihi isi kotak / isi karung)');
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
  berubah.forEach((b) => { const al = String(b.alasan || '').trim() || (b.wajar ? (b.jenis === 'karung' ? 'Selisih timbang karung (dalam batas)' : 'Susut takar wajar') : 'Cocokkan wadah');
    Object.keys(b.alokasi).sort().forEach((m) => { const sel = b.alokasi[m]; const st = stok[m]; if (!st || Math.abs(sel) < 0.005) return;
      const kgS = jalan[m] !== undefined ? jalan[m] : ckB2(st.sisaKg || 0); jalan[m] = ckB2(kgS + sel); nMerk += 1;
      // modal FIFO (owner 9 Okt): merek karung = irisan karung terlama, berurutan dalam kiriman ini (keluar sebelumnya menggeser depan antrean)
      const fifo = st.metode === 'fifo'; const keluarDulu = ckB2((st.sisaKg || 0) - kgS); const rpSel = fifo ? Math.round(nilaiSelisihKg(st, sel, keluarDulu)) : Math.round(sel * (st.hppTerakhirPerKg || 0));
      dokumen.push({ koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: m, kgSistem: kgS, kgFisik: jalan[m], selisihKg: sel, alasan: al, nilaiRp: rpSel,
        hppPerKgSaatOpname: fifo ? Math.round(Math.abs(rpSel / sel)) : Math.round(st.hppTerakhirPerKg || 0), bagian: 'wadah', wadah: b.jenis === 'karung' ? b.lokasi : b.nama, bagianSistemKg: b.sistem, bagianFisikKg: b.dihitung } }); });
    // putaran 28: wadah berstok sendiri — titik samakan tanpa komposisi (isinya = buku wadah itu, selisihnya sudah jadi penyesuaian di atas)
    if (b.isiH !== null) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: b.nama, tipe: 'isi', isiKg: b.isiH }, b.stokSendiri ? Object.assign({ stokWadah: b.kunciStok }, ((k) => (Object.keys(k).length ? { komposisi: k } : {}))(wbKomposisiTurunanKg(b.nama, b.isiH))) : { komposisi: b.komposisiBaru || {} }, { dariCocok: true }) });   // 39b no. 16: komposisi turunan dibawa
    const di = b.jenis === 'karung' ? (b.lokasi ? { wadah: b.lokasi, diamSlot: true } : { lepas: true }) : { wadah: b.nama };   // karung kedua dst. tidak memindah karung terdepan
    if (b.krH !== null && b.karungNama) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: b.karungNama, isiKg: b.krH }, di, { dariCocok: true }) }); });
  const nW = berubah.filter((b) => b.jenis !== 'karung').length; const nK = berubah.length - nW;
  const dampak = w.tanggal < MULAI_SUSUT_LABA ? 'Kas, laba, dan omzet tidak berubah.' : (c.susutRp ? 'Laba bulan ini turun ' + RP(-c.susutRp) + ' lewat baris "Susut & selisih stok". ' : '') + (c.lebihRp ? 'Stok naik ' + RP(c.lebihRp) + ' tanpa mengubah modal per kg. ' : '') + 'Kas dan omzet tidak bergerak.';
  // owner 7 Okt: karung di belakang wadah yang ditimbang habis = karung bekas +1; karung bekas yang ternyata masih berisi → kelahirannya dicabut (Cocokkan = owner)
  return wbSertakanKarungBekas({ dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: ' + (nW ? nW + ' wadah' : '') + (nK ? (nW ? ' + ' : '') + nK + ' karung' : '') + ' dihitung' + (c.belum ? ', ' + c.belum + ' belum' : '') + ' — ' + (nMerk ? nMerk + ' buku disesuaikan. ' + dampak : 'tidak ada buku yang berubah (cocok, susut nol, atau hitungan pertama).') + ' Isi wadah & karung terbuka kini = hitungan.', kabarAwas: false } }, w);
}
/** Hitungan fisik sebelumnya (semua jenis), dikelompokkan per tanggal+jam, terbaru dulu. */
export function riwayatCocok(n) {
  const semua = [];
  ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d)) semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.merk + (d.bagian === 'wadah' ? (d.wadah ? ' (wadah ' + d.wadah + ')' : ' (karung lepas)') : d.bagian === 'tumpukan' ? ' (tumpukan)' : ''), teks: (d.selisihKg > 0 ? '+' : '') + String(Math.round((d.selisihKg || 0) * 100) / 100).replace('.', ',') + ' kg', rp: d.nilaiRp || 0, alasan: d.alasan || '' }); });
  ambilPenyesuaianKemasan().forEach((d) => semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: d.namaProduk + ' ' + String(d.ukuranKemasan).replace('.', ',') + ' kg', teks: (d.selisihUnit > 0 ? '+' : '') + (d.selisihUnit || 0) + ' unit', rp: d.nilaiRp || 0, alasan: d.alasan || '' }));
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && !d.lahirKarungBekas && !d.nilaiKarungBekas) semua.push({ tanggal: d.tanggal || '', jam: d.jam || '', nama: ccLabelBahan(d.jenis), teks: (d.jumlah > 0 ? '+' : '') + (d.jumlah || 0) + ' lembar', rp: d.nilaiRp || 0, alasan: d.catatan || '' }); });
  const kel = {}; semua.forEach((x) => { const k = x.tanggal + ' ' + x.jam; if (!kel[k]) kel[k] = { kunci: k, tanggal: x.tanggal, jam: x.jam, baris: [], rp: 0 }; kel[k].baris.push(x); kel[k].rp += x.rp; });
  return Object.keys(kel).sort().reverse().slice(0, n || 8).map((k) => kel[k]);
}
