// WADAH DIJUAL — logika (tanpa DOM). Keputusan owner 17 Sep 2026: di layar Jual, kantong kemasan & karung bekas adalah BARANG
// DAGANGAN — tiap lembar jadi baris nota dengan harga jualnya sendiri dan menambah omzet; di Produksi ia tetap BIAYA (HPP).
// Sistem lama mencatat wadah HANYA sebagai biaya (biayaKemasanLiteran → hppTotalSaatJual), nol yang pernah ditagih.
//
// Yang dipegang di sini:
//  - jenis wadah = kunci koleksi bahan sistem lama (stokBahanKemasan: '5kg_kembangbmw' …; stokBahanLiteran: paperbag5l/10l, karungbekas),
//    supaya stok & modalnya dibaca mesin beku yang sama (hitungStokBahanKemasan / hitungStokBahanLiteran) dan penjualannya
//    mengurangi buku kantong lewat dokumen `pakai` — pola yang sama dengan kantong literan (id nota + 1);
//  - HARGA JUAL per lembar = katalog BARU `hargaWadah` (id = jenis) yang diatur owner; yang belum punya harga TIDAK tampil di rak
//    (bukan tampil Rp0); lantai Rp100/lembar karena pernah Rp1.000/1.000 lembar tercatat jadi Rp1 per lembar;
//  - modal per lembar dibaca dari buku: kantong = rata-rata beli; paper bag/karung bekas = harga efektif yang sama dengan biaya
//    literan (hargaBahanLiteranEfektif). Wadah yang belum pernah dibeli TIDAK punya modal Rp0 — ia tidak punya modal, jadi baris
//    notanya ditulis TANPA hppTotalSaatJual dan mesin laba menaruhnya di "tanpa HPP" (bukan margin 100 %);
//  - karung bekas = HASIL SAMPING (tidak pernah dibeli, lahir dari literan & adukan): tidak dibatasi buku, bukunya tetap dipotong.
import { hitungStokBahanKemasan, hitungStokBahanLiteran } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, JENIS_BAHAN_KEMASAN, HARGA_AWAL_BAHAN_LITERAN, hargaBahanLiteranEfektif } from '../mesin/pembantu.js';
import { ambilHargaWadah } from '../data/toko.js';
import { RP } from '../inti/format.js';

export const WJ_LANTAI_LEMBAR = 100;                 // harga per LEMBAR di bawah ini hampir pasti salah satuan (kejadian Rp1/lembar)
export const WJ_HASIL_SAMPING = ['karungbekas'];     // tidak pernah dibeli — tidak dibatasi buku
const MUAT_LITERAN = { paperbag5l: 4, paperbag10l: 8, karungbekas: 25 };   // kg beras yang muat, untuk saran lembar repack (25 kg karung bekas = aturan owner 15 Sep)

/** Semua jenis wadah yang dikenal buku sistem lama, berurutan menurut muatannya. */
export function daftarJenisWadah() {
  const out = [];
  JENIS_BAHAN_KEMASAN.forEach((j) => {
    const m = /^(\d+)kg_/.exec(j); const uk = m ? Number(m[1]) : 0;
    const merk = String(LABEL_BAHAN_KEMASAN[j] || j).replace(/^\d+\s*kg\s*—\s*/, '');
    out.push({ jenis: j, koleksi: 'stokBahanKemasan', ukuranKg: uk, nama: 'Kantong ' + merk, ukuran: uk + ' kg', label: 'Kantong ' + merk + ' ' + uk + ' kg', hasilSamping: false });
  });
  Object.keys(HARGA_AWAL_BAHAN_LITERAN).forEach((j) => {
    const nama = LABEL_BAHAN_LITERAN[j] || j; const uk = MUAT_LITERAN[j] || 0;
    out.push({ jenis: j, koleksi: 'stokBahanLiteran', ukuranKg: uk, nama, ukuran: j === 'karungbekas' ? '25–50 kg' : '±' + uk + ' kg', label: nama, hasilSamping: WJ_HASIL_SAMPING.indexOf(j) >= 0 });
  });
  return out.sort((a, b) => a.ukuranKg - b.ukuranKg || a.nama.localeCompare(b.nama));
}
export function jenisWadah(jenis) { return daftarJenisWadah().find((d) => d.jenis === jenis) || null; }
export function koleksiWadah(jenis) { const d = jenisWadah(jenis); return d ? d.koleksi : 'stokBahanKemasan'; }

/** Harga jual per lembar dari katalog hargaWadah (id = jenis); harga 0 / tidak ada = tidak dijual. */
export function hargaJualWadah() {
  const peta = {};
  ambilHargaWadah().forEach((d) => { const h = Math.round(Number(d.harga) || 0); if (d.jenis && h > 0) peta[d.jenis] = { harga: h, tanggal: d.tanggal || '', jam: d.jam || '' }; });
  return peta;
}

/** Stok & modal satu jenis dari buku (mesin beku). modal null = belum ada harga beli. */
export function stokWadah(jenis) {
  const d = jenisWadah(jenis); if (!d) return null;
  if (d.koleksi === 'stokBahanKemasan') {
    const st = hitungStokBahanKemasan()[jenis] || {};
    const ada = (st.totalBeli || 0) > 0 && (st.hppPerPcs || 0) > 0;
    return { jenis, sisaBuku: st.sisaPcs || 0, modal: ada ? st.hppPerPcs : null, adaModal: ada, modalAneh: ada && st.hppPerPcs < WJ_LANTAI_LEMBAR, nBeli: st.totalBeli || 0 };
  }
  const semua = hitungStokBahanLiteran(); const st = semua[jenis] || {};
  const modal = hargaBahanLiteranEfektif(jenis, semua);   // sama dengan biaya kantong literan di nota literan
  const dariBuku = (st.hargaPerPcs || 0) > 0;
  return { jenis, sisaBuku: st.sisaPcs || 0, modal: modal > 0 ? modal : null, adaModal: modal > 0, modalAneh: dariBuku && st.hargaPerPcs < WJ_LANTAI_LEMBAR, dariBawaan: !dariBuku, nBeli: st.totalBeli || 0 };
}
/** Kalimat jujur soal modal untuk layar. */
export function teksModalWadah(st, harga) {
  if (!st || !st.adaModal) return 'modal belum ada — wadah ini belum pernah tercatat dibeli; labanya belum bisa disebut (baris nota ditulis tanpa HPP)';
  const dasar = 'modal ' + RP(st.modal) + '/lembar' + (st.dariBawaan ? ' (angka bawaan, belum pernah dibeli)' : '');
  const margin = harga ? ' · margin ' + (harga - st.modal === 0 ? 'Rp0 (dijual seharga modalnya)' : RP(harga - st.modal) + '/lembar') : '';
  const aneh = st.modalAneh ? ' — modal di buku di bawah Rp100/lembar: catatan belinya hampir pasti salah satuan (mis. Rp1.000 untuk 1.000 lembar); laba wadah ini akan tergambar terlalu besar sampai catatan belinya dibetulkan' : '';
  return dasar + margin + aneh;
}

/** Rak jalur Wadah: hanya jenis yang punya harga jual. dipegang(jenis) = lembar di keranjang aktif + struk parkir (dari jual-logika). */
export function susunRakWadah(dipegang, dipegangParkir) {
  const harga = hargaJualWadah();
  return daftarJenisWadah().filter((d) => harga[d.jenis]).map((d) => {
    const st = stokWadah(d.jenis); const dp = dipegang ? dipegang(d.jenis) : 0; const parkir = dipegangParkir ? dipegangParkir(d.jenis) : 0;
    const sisa = Math.max(0, st.sisaBuku - dp);
    return { jalur: 'wadah', kunci: d.jenis, nama: d.nama, ukuran: d.ukuran, ukuranKg: d.ukuranKg, label: d.label, harga: harga[d.jenis].harga, satuan: 'lembar',
      koleksi: d.koleksi, hasilSamping: d.hasilSamping, tanpaBatas: d.hasilSamping, sisaBuku: st.sisaBuku, sisa: d.hasilSamping ? Math.max(sisa, 0) : sisa,
      sisaTeks: d.hasilSamping ? 'buku ' + String(st.sisaBuku - dp).replace('.', ',') + ' lembar · hasil samping, tidak dibatasi buku' : sisa + ' lembar',
      modal: st.modal, adaModal: st.adaModal, modalAneh: st.modalAneh, teksModal: teksModalWadah(st, harga[d.jenis].harga), dipegang: parkir };
  }).sort((a, b) => a.ukuranKg - b.ukuranKg || a.harga - b.harga || a.nama.localeCompare(b.nama));
}
/** Lembar yang bebas dijual sekarang untuk jenis ini (null = tidak dibatasi: hasil samping). */
export function bebasWadah(jenis, dipegang) {
  const d = jenisWadah(jenis); if (!d) return 0;
  if (d.hasilSamping) return null;
  const st = stokWadah(jenis); return Math.max(0, st.sisaBuku - (dipegang || 0));
}

/**
 * Baris nota untuk wadah yang DIJUAL: jenis 'wadah' (baru — mesin stok beras tidak menyentuhnya, mesin laba membacanya seperti baris lain:
 * omzet = hargaTotal, HPP = hppTotalSaatJual). Tanpa modal → tanpa hppTotalSaatJual (mesin laba: "tanpa HPP", bukan margin penuh).
 */
export function bangunBarisWadah(chip, j) {
  const t = { jenis: 'wadah', jenisWadah: chip.kunci, namaProduk: chip.label, jumlahUnit: j, totalKg: 0, label: chip.label, satuan: 'lembar' };
  if (chip.adaModal) t.hppTotalSaatJual = Math.round(chip.modal * j);
  return t;
}
/** Wadah yang DITANGGUNG toko pada repack: biayanya masuk HPP baris repack (seperti biayaKemasanLiteran), tidak ditagih. */
export function biayaWadahRepack(jenis, lembar) {
  const st = stokWadah(jenis); const n = Math.max(0, Math.round(Number(lembar) || 0));
  if (!st || !n) return { biaya: 0, ada: false, lembar: 0 };
  return { biaya: st.adaModal ? Math.round(st.modal * n) : 0, ada: !!st.adaModal, lembar: n };
}
/** Saran lembar untuk repack: kg dibagi muatan wadah, dibulatkan KE ATAS (25 kg hasil memotong wajib satu karung bekas — owner 15 Sep). */
export function saranLembar(kg, jenis) {
  const d = jenisWadah(jenis); const k = Number(kg) || 0;
  if (!d || !d.ukuranKg || k <= 0) return k > 0 ? 1 : 0;
  return Math.max(1, Math.ceil(Math.round(k / d.ukuranKg * 1000) / 1000));
}

/** Daftar untuk lembar Atur harga jual wadah: semua jenis, dengan stok, modal, harga jual sekarang. */
export function daftarAturWadah() {
  const harga = hargaJualWadah();
  return daftarJenisWadah().map((d) => { const st = stokWadah(d.jenis); return Object.assign({}, d, { sisaBuku: st.sisaBuku, modal: st.modal, adaModal: st.adaModal, modalAneh: st.modalAneh, harga: harga[d.jenis] ? harga[d.jenis].harga : 0, sejak: harga[d.jenis] ? harga[d.jenis].tanggal : '', teksModal: teksModalWadah(st, harga[d.jenis] ? harga[d.jenis].harga : 0) }); });
}
/**
 * Simpan harga jual wadah: isi = { jenis: teks rupiah }. Kosong / 0 = tidak dijual (dokumen harga 0, jejaknya tetap).
 * Ditolak: angka 1–99 (lantai Rp100/lembar — salah satuan), jenis yang tidak dikenal buku. Hanya yang berubah yang ditulis.
 */
export function susunAturHargaWadah(isi, w) {
  const harga = hargaJualWadah(); const dokumen = []; const salah = [];
  Object.keys(isi || {}).forEach((jenis) => {
    const d = jenisWadah(jenis); if (!d) return;
    const teks = String(isi[jenis] === undefined || isi[jenis] === null ? '' : isi[jenis]).trim();
    const n = Math.round(Number(teks.replace(/[^\d]/g, '')) || 0);
    if (n > 0 && n < WJ_LANTAI_LEMBAR) { salah.push(d.label + ': ' + RP(n) + ' per lembar'); return; }
    const lama = harga[jenis] ? harga[jenis].harga : 0;
    if (n === lama) return;
    dokumen.push({ koleksi: 'hargaWadah', data: { id: jenis, jenis, harga: n, hargaSebelum: lama, tanggal: w.tanggal, jam: w.jam } });
  });
  if (salah.length) return { tolak: 'Harga per LEMBAR di bawah ' + RP(WJ_LANTAI_LEMBAR) + ' hampir pasti salah satuan — ' + salah.join('; ') + '. Ketik harga SATU lembar.' };
  if (!dokumen.length) return { tolak: 'Tidak ada harga yang berubah' };
  const dijual = dokumen.filter((x) => x.data.harga > 0).length; const dicabut = dokumen.length - dijual;
  return { dokumen, patch: { lembar: null, aturWadah: null, kabar: 'Harga jual wadah tersimpan — ' + (dijual ? dijual + ' wadah bisa dijual dari rak' : '') + (dijual && dicabut ? ', ' : '') + (dicabut ? dicabut + ' dicabut dari rak' : '') + '. Hanya yang berharga yang tampil di jalur Wadah.', kabarAwas: false } };
}
