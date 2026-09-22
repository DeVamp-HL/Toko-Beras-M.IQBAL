// LAYAR STOK — MENCATAT (tanpa DOM): ADUKAN (ST2 "Timbangan Adukan", dikunci owner 19 Sep). Dijaga alat-uji/uji_stok_baru.py.
//
// Satu adukan = SATU KESATUAN BIAYA (sistem berjalan, 23 Agu 2026): biaya = nilai bahan (kg × modal rata-rata nama itu, atau unit × modal kemasan jadi
// yang dibongkar) + kantong (lembar × modal per lembar) + upah kemas, dibagi ke tiap baris hasil MENURUT KG; sisa pembulatan jatuh ke baris terakhir supaya
// Σ (modal per unit × unit) = biaya PERSIS (mesin beku `bagiBiayaAdukan`). Susut terserap sendiri: kg jadi < kg masuk → modal per kg hasil naik.
// Bentuk dokumen PERSIS `simpanProduksi` index.html 20583 (koleksi produksiKemasan; sumberList/kgDipakai/sumberKemasanList/kgKemasanDipakai/upahRepacking
// HANYA di dokumen pertama seadukan — hitungStokKarungPerMerk & hitungStokKemasan memotong dari tiap dokumen yang membawanya), pasangan pemakaian kantong
// `stokBahanKemasan` {id = id produksi + 1, tipe 'pakai'} (hapusProduksi mencabut id + 1). Kolom tambahan sistem baru: `jam`.
// Koreksi = mengubah TOTAL biaya adukan lalu dibagi ulang ke semua barisnya (simpanKoreksiHpp 20976): dokumen pengganti ber-koreksiDari, dokumen lama
// ditandai dikoreksiOleh (tetap terbaca di riwayat, tidak lagi dihitung mesin). Hapus = SELURUH adukan dicabut bersama (hapusProduksi 20866) — DITOLAK bila
// hasilnya sudah terjual/terpakai sehingga stok kemasan jadi minus; jejaknya ke bukuHapus. Adukan "menunggu owner" dari tablet menyusul bersama layar tablet.
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, bagiBiayaAdukan } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, JENIS_BAHAN_KEMASAN, kunciKemasan } from '../mesin/pembantu.js';
import { ambilProduksi, ambilHargaKemasan } from '../data/toko.js';
import { RP } from '../inti/format.js';

export const UKURAN_BAHAN_KEMASAN = [50, 25];          // kemasan jadi yang boleh dibongkar lagi (UKURAN_KEMASAN_BOLEH_JADI_BAHAN index.html)
export const UKURAN_HASIL_PILIHAN = [5, 10, 20, 25, 50];
export const KG_KARUNG_ADUKAN = 50;                     // satu ketukan "+1 karung" di baris bahan
export const BATAS_SUSUT_ADUKAN = 0.15;                 // selisih kg masuk vs jadi > 15 % ditanya (simpanProduksi)
const adAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const adB3 = (n) => Math.round(n * 1000) / 1000;      // tiga desimal di satu pintu masuk (bacaSumberProduksi) — penjumlahan pecahan tidak berekor
const adKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const adKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const adLabelKantong = (j) => LABEL_BAHAN_KEMASAN[j] || j;
const adUkuranTeks = (u) => String(u).replace('.', ',');

export function barisBahanKosong() { return { merk: '', kg: '' }; }
export function barisBahanKemasanKosong() { return { kunci: '', unit: '' }; }
export function barisHasilKosong() { return { nama: '', ukuran: '', unit: '', kantongJenis: '', kantongJumlah: '' }; }
export function drafAdukanKosong(w) { return { tanggal: w.tanggal, bahan: [barisBahanKosong()], bahanKemasan: [], hasil: [barisHasilKosong()], upah: '' }; }

/** Nama karung yang bersisa di gudang (buku), sisa terbanyak dulu — bahan adukan. */
export function calonBahan() {
  const st = hitungStokKarungPerMerk();
  return Object.keys(st).filter((m) => (st[m].sisaKg || 0) > 0).sort((a, b) => st[b].sisaKg - st[a].sisaKg).map((m) => ({ merk: m, sisaKg: Math.round(st[m].sisaKg * 100) / 100, hpp: st[m].hppTerakhirPerKg || 0 }));
}
/** Kemasan jadi 50/25 kg yang bersisa — boleh dibongkar jadi bahan. */
export function calonKemasanBahan() {
  const st = hitungStokKemasan();
  return Object.keys(st).filter((k) => UKURAN_BAHAN_KEMASAN.indexOf(Number(st[k].ukuranKemasan)) >= 0 && (st[k].sisaUnit || 0) > 0)
    .map((k) => ({ kunci: k, namaProduk: st[k].namaProduk, ukuranKemasan: Number(st[k].ukuranKemasan), sisaUnit: st[k].sisaUnit, hpp: st[k].hppRataRataPerUnit || 0 }))
    .sort((a, b) => a.namaProduk.localeCompare(b.namaProduk) || b.ukuranKemasan - a.ukuranKemasan);
}
/** Nama hasil yang pernah diaduk (sering dulu) + nama di katalog harga kemasan; nama baru tetap boleh diketik. */
export function calonNamaHasil() {
  const hitung = {}; ambilProduksi().forEach((p) => { if (p.namaProduk && !p.beliJadi && !p.dariTakar && !p.jadiKarungUtuh) hitung[p.namaProduk] = (hitung[p.namaProduk] || 0) + 1; });
  ambilHargaKemasan().forEach((k) => { if (k.merk && hitung[k.merk] === undefined) hitung[k.merk] = 0; });
  return Object.keys(hitung).sort((a, b) => hitung[b] - hitung[a] || a.localeCompare(b));
}
/** Jenis kantong untuk ukuran hasil itu (5/10/20/25 kg) + sisa & modal per lembar; 50 kg = tanpa kantong. */
export function kantongUntuk(ukuran) {
  const st = hitungStokBahanKemasan(); const awalan = String(Number(ukuran)) + 'kg_';
  return JENIS_BAHAN_KEMASAN.filter((j) => j.indexOf(awalan) === 0).map((j) => ({ jenis: j, label: adLabelKantong(j), sisaPcs: (st[j] || {}).sisaPcs || 0, hppPerPcs: (st[j] || {}).hppPerPcs || 0 }));
}
const adJenisProduksi = (p) => (p.beliJadi || p.stokAwal || p.dariBatch ? 'beliJadi' : p.dariTakar ? 'pindahBuku' : p.jadiKarungUtuh ? 'gabungKarung' : /rework dari karantina/i.test(String(p.catatan || '')) ? 'rework' : 'adukan');

/** Hitung draf: tiap baris + masalahnya, kg masuk/jadi, nilai bahan, kantong, upah, total, modal per unit tiap hasil (rumus sistem berjalan), susut. */
export function hitungAdukan(draf) {
  const stokK = hitungStokKarungPerMerk(); const stokM = hitungStokKemasan(); const stokB = hitungStokBahanKemasan();
  const bahan = (draf.bahan || []).map((b, i) => { const merk = String(b.merk || '').trim(); const kg = adB3(adAngka(b.kg)); const terisi = !!merk || kg > 0; const st = stokK[merk];
    const masalah = !terisi ? '' : !merk ? 'nama karungnya belum dipilih' : !(kg > 0) ? 'berapa kg yang dipakai belum diisi' : !st ? merk + ' tidak ada di buku gudang' : '';
    return { ke: i + 1, merk, kg, terisi, masalah, sah: terisi && !masalah, sisaKg: st ? Math.round((st.sisaKg || 0) * 100) / 100 : null, hpp: st ? (st.hppTerakhirPerKg || 0) : 0, nilai: st ? (st.hppTerakhirPerKg || 0) * kg : 0 }; });
  const bahanKemasan = (draf.bahanKemasan || []).map((b, i) => { const kunci = String(b.kunci || ''); const unit = adAngka(b.unit); const terisi = !!kunci || unit > 0; const st = stokM[kunci];
    const masalah = !terisi ? '' : !kunci ? 'kemasan yang dibongkar belum dipilih' : !(unit > 0) ? 'berapa unit yang dibongkar belum diisi' : !st ? 'kemasan itu tidak dikenal' : UKURAN_BAHAN_KEMASAN.indexOf(Number(st.ukuranKemasan)) < 0 ? 'hanya kemasan 50 / 25 kg yang boleh dibongkar' : '';
    return { ke: i + 1, kunci, unit, terisi, masalah, sah: terisi && !masalah, namaProduk: st ? st.namaProduk : '', ukuranKemasan: st ? Number(st.ukuranKemasan) : 0, sisaUnit: st ? (st.sisaUnit || 0) : null, hpp: st ? (st.hppRataRataPerUnit || 0) : 0,
      kg: st ? adB3(Number(st.ukuranKemasan) * unit) : 0, nilai: st ? (st.hppRataRataPerUnit || 0) * unit : 0 }; });
  const hasil = (draf.hasil || []).map((h, i) => { const nama = String(h.nama || '').trim(); const ukuran = adB3(adAngka(h.ukuran)); const unit = adAngka(h.unit); const kantongJenis = String(h.kantongJenis || ''); const kantongJumlah = adAngka(h.kantongJumlah);
    const terisi = !!nama || ukuran > 0 || unit > 0; const masalah = !terisi ? '' : !nama ? 'nama hasilnya belum diisi' : !(ukuran > 0) ? 'ukurannya belum dipilih' : !(unit > 0) ? 'jumlah unitnya belum diisi' : kantongJenis && !JENIS_BAHAN_KEMASAN.some((j) => j === kantongJenis) ? 'jenis kantongnya tidak dikenal' : '';
    const pakaiKantong = !!kantongJenis && kantongJumlah > 0; const biayaKantong = pakaiKantong ? Math.round(((stokB[kantongJenis] || {}).hppPerPcs || 0) * kantongJumlah) : 0;
    return { ke: i + 1, nama, ukuran, unit, kantongJenis, kantongJumlah, terisi, masalah, sah: terisi && !masalah, kg: adB3(ukuran * unit), biayaKantong, kantongTanpaCacah: !!kantongJenis && !(kantongJumlah > 0),
      kantongLabel: kantongJenis ? adLabelKantong(kantongJenis) : 'tanpa kantong', kantongSisa: kantongJenis ? ((stokB[kantongJenis] || {}).sisaPcs || 0) : null, kunci: kunciKemasan(nama, ukuran) }; });
  const sahB = bahan.filter((b) => b.sah); const sahBK = bahanKemasan.filter((b) => b.sah); const sahH = hasil.filter((h) => h.sah);
  const kgDipakai = adB3(sahB.reduce((a, b) => a + b.kg, 0)); const kgKemasanDipakai = adB3(sahBK.reduce((a, b) => a + b.kg, 0)); const kgMasuk = adB3(kgDipakai + kgKemasanDipakai); const kgJadi = adB3(sahH.reduce((a, h) => a + h.kg, 0));
  const nilaiKarung = sahB.reduce((a, b) => a + b.nilai, 0); const nilaiKemasanBahan = sahBK.reduce((a, b) => a + b.nilai, 0); const nilaiBahan = nilaiKarung + nilaiKemasanBahan;
  const hppSumberPerKg = kgMasuk > 0 ? nilaiBahan / kgMasuk : 0; const biayaKantong = sahH.reduce((a, h) => a + h.biayaKantong, 0); const upah = adAngka(draf.upah); const total = nilaiBahan + upah + biayaKantong;
  const bagi = bagiBiayaAdukan(sahH.map((h) => ({ ukuranKemasan: h.ukuran, jumlahUnit: h.unit })), total) || [];
  sahH.forEach((h, i) => { h.hppPerUnit = bagi[i]; h.bagian = (bagi[i] || 0) * h.unit; h.hppPerKg = h.ukuran > 0 ? (bagi[i] || 0) / h.ukuran : 0; });
  const butuhKantong = {}; sahH.forEach((h) => { if (h.kantongJenis && h.kantongJumlah > 0) butuhKantong[h.kantongJenis] = (butuhKantong[h.kantongJenis] || 0) + h.kantongJumlah; });
  const kurangKantong = Object.keys(butuhKantong).filter((j) => ((stokB[j] || {}).sisaPcs || 0) < butuhKantong[j]).map((j) => ({ jenis: j, label: adLabelKantong(j), butuh: butuhKantong[j], sisa: (stokB[j] || {}).sisaPcs || 0 }));
  const butuhBahan = {}; sahB.forEach((b) => { butuhBahan[b.merk] = adB3((butuhBahan[b.merk] || 0) + b.kg); }); const kurangBahan = Object.keys(butuhBahan).filter((m) => (stokK[m].sisaKg || 0) < butuhBahan[m]).map((m) => ({ merk: m, butuh: butuhBahan[m], sisa: Math.round((stokK[m].sisaKg || 0) * 100) / 100 }));
  const butuhKemasan = {}; sahBK.forEach((b) => { butuhKemasan[b.kunci] = (butuhKemasan[b.kunci] || 0) + b.unit; }); const kurangKemasan = Object.keys(butuhKemasan).filter((k) => ((stokM[k] || {}).sisaUnit || 0) < butuhKemasan[k]).map((k) => ({ kunci: k, nama: stokM[k].namaProduk + ' ' + adUkuranTeks(stokM[k].ukuranKemasan) + ' kg', butuh: butuhKemasan[k], sisa: stokM[k].sisaUnit || 0 }));
  const lingkaran = sahBK.map((sk) => sahH.find((h) => h.kunci === kunciKemasan(sk.namaProduk, sk.ukuranKemasan))).filter(Boolean);
  const merkSumber = sahB.length === 0 ? (sahBK.length ? 'DARI KEMASAN JADI: ' + sahBK.map((k) => k.namaProduk + ' ' + k.ukuranKemasan + 'kg').join(' + ') : null) : (sahB.length === 1 ? sahB[0].merk : 'CAMPURAN: ' + sahB.map((s) => s.merk).join(' + '));
  const susutKg = adB3(kgMasuk - kgJadi); const susutPersen = kgMasuk > 0 ? susutKg / kgMasuk * 100 : 0;
  return { bahan, bahanKemasan, hasil, sahB, sahBK, sahH, kgDipakai, kgKemasanDipakai, kgMasuk, kgJadi, nilaiKarung, nilaiKemasanBahan, nilaiBahan, hppSumberPerKg, biayaKantong, upah, total, susutKg, susutPersen, merkSumber,
    bermasalah: bahan.concat(bahanKemasan, hasil).filter((x) => x.terisi && x.masalah), kurangBahan, kurangKemasan, kurangKantong, kantongTanpaCacah: sahH.filter((h) => h.kantongTanpaCacah), lingkaran,
    teksBahan: sahB.map((b) => adKG(b.kg) + ' ' + b.merk).concat(sahBK.map((k) => k.unit + ' × ' + k.namaProduk + ' ' + adUkuranTeks(k.ukuranKemasan) + ' kg')).join(' + '),
    teksHasil: sahH.map((h) => h.unit + ' × ' + h.nama + ' ' + adUkuranTeks(h.ukuran) + ' kg').join(' + ') };
}
/** Susun dokumen adukan. yakin = {bahan, kemasan, kantongKosong, kantong, susut} — pertanyaan yang sudah dijawab "ya" (dua ketukan), urutan sama dengan simpanProduksi. */
export function susunSimpanAdukan(draf, w, yakin) {
  const Y = yakin || {}; const h = hitungAdukan(draf);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(draf.tanggal || ''))) return { tolak: 'Tanggal adukannya belum benar' };
  if (h.bermasalah.length) { const x = h.bermasalah[0]; return { tolak: 'Baris ' + x.ke + (x.merk || x.nama || x.namaProduk ? ' (' + (x.merk || x.nama || x.namaProduk) + ')' : '') + ': ' + x.masalah + ' — lengkapi atau kosongkan barisnya' }; }
  if (!h.sahB.length && !h.sahBK.length) return { tolak: 'Isi minimal satu bahan — karung dari gudang (nama + kg) atau kemasan jadi yang dibongkar' };
  if (!h.sahH.length) return { tolak: 'Isi minimal satu baris hasil: nama, ukuran, dan jumlah unit' };
  if (h.lingkaran.length) { const x = h.lingkaran[0]; return { tolak: 'Ditolak: ' + x.nama + ' ' + adUkuranTeks(x.ukuran) + ' kg dipakai sebagai BAHAN sekaligus jadi HASIL — itu memutar stok tanpa arti. Ukuran yang berbeda boleh' }; }
  if (h.upah < 0) return { tolak: 'Upah kemas tidak boleh minus' };
  if (!(h.kgJadi > 0)) return { tolak: 'Total kg hasil nol — biayanya tidak bisa dibagi per baris' };
  if (h.kurangBahan.length && !Y.bahan) { const x = h.kurangBahan[0]; return { tolak: 'Stok ' + x.merk + ' menurut buku cuma ' + adKG(x.sisa) + ', adukan ini pakai ' + adKG(x.butuh) + ' — ketuk sekali lagi kalau tetap disimpan (stok bisa jadi minus)', perluYakin: 'bahan' }; }
  if (h.kurangKemasan.length && !Y.kemasan) { const x = h.kurangKemasan[0]; return { tolak: 'Stok ' + x.nama + ' cuma sisa ' + x.sisa + ' unit, adukan ini membongkar ' + x.butuh + ' unit — ketuk sekali lagi kalau tetap disimpan (stok bisa jadi minus)', perluYakin: 'kemasan' }; }
  if (h.kantongTanpaCacah.length && !Y.kantongKosong) { const x = h.kantongTanpaCacah[0]; return { tolak: 'Baris ' + x.ke + ' (' + x.nama + ' ' + adUkuranTeks(x.ukuran) + ' kg) memilih kantong ' + x.kantongLabel + ' tapi jumlah lembarnya kosong — kalau disimpan begini kantongnya terhitung GRATIS: biayanya tidak masuk modal, stoknya tidak turun, dan margin adukan ini terbaca lebih baik dari kenyataan. Isi lembarnya, pilih "tanpa kantong", atau ketuk sekali lagi', perluYakin: 'kantongKosong' }; }
  if (h.kurangKantong.length && !Y.kantong) { const x = h.kurangKantong[0]; return { tolak: 'Stok kantong ' + x.label + ' cuma sisa ' + x.sisa + ' lembar, adukan ini butuh ' + x.butuh + ' — ketuk sekali lagi kalau tetap disimpan (stok kantong bisa minus, catat belanja kantongnya nanti)', perluYakin: 'kantong' }; }
  if (h.kgMasuk > 0 && Math.abs(h.kgJadi - h.kgMasuk) > h.kgMasuk * BATAS_SUSUT_ADUKAN && !Y.susut) return { tolak: 'Bahan ' + adKG(h.kgMasuk) + ' tapi hasil ' + adKG(h.kgJadi) + ' (selisih lebih dari ' + Math.round(BATAS_SUSUT_ADUKAN * 100) + ' % — susut besar atau salah ketik). Ketuk sekali lagi kalau memang begitu', perluYakin: 'susut' };
  const batchId = w.idUnik(); const dokumen = [];
  h.sahH.forEach((x, i) => {
    const id = i === 0 ? batchId : w.idUnik();
    dokumen.push({ koleksi: 'produksiKemasan', data: { id, tanggal: draf.tanggal, jam: w.jam, merkSumber: h.merkSumber, namaProduk: x.nama, ukuranKemasan: x.ukuran, jumlahUnit: x.unit,
      biayaKemasan: x.biayaKantong, upahRepacking: i === 0 ? h.upah : 0, kantongJenis: x.kantongJenis || null, kantongJumlah: x.kantongJumlah || 0, hppSumberPerKgDipakai: h.hppSumberPerKg, hppPerUnit: x.hppPerUnit,
      sumberList: i === 0 ? h.sahB.map((b) => ({ merk: b.merk, kg: b.kg })) : [], kgDipakai: i === 0 ? h.kgDipakai : 0,
      sumberKemasanList: i === 0 ? h.sahBK.map((k) => ({ namaProduk: k.namaProduk, ukuranKemasan: k.ukuranKemasan, unit: k.unit, hppPerUnitSaatDipakai: Math.round(k.hpp) })) : [], kgKemasanDipakai: i === 0 ? h.kgKemasanDipakai : 0,
      batchProduksi: batchId, barisKe: i + 1, jumlahBaris: h.sahH.length, jadiKarungUtuh: false, merkTujuan: null } });
    if (x.kantongJenis && x.kantongJumlah > 0) dokumen.push({ koleksi: 'stokBahanKemasan', data: { id: id + 1, tipe: 'pakai', jenis: x.kantongJenis, jumlah: x.kantongJumlah, hargaTotal: 0, tanggal: draf.tanggal, catatan: 'Otomatis dari produksi id ' + id } });
  });
  const modalTeks = h.sahH.map((x) => x.nama + ' ' + adUkuranTeks(x.ukuran) + ' kg ' + RP(Math.round(x.hppPerUnit)) + '/unit').join(' · ');
  return { dokumen, hitung: h, batchId, patch: { kabar: 'Adukan tersimpan: ' + h.teksBahan + ' → ' + h.teksHasil + ' · biaya ' + RP(Math.round(h.total)) + ' (bahan ' + RP(Math.round(h.nilaiBahan)) + (h.biayaKantong ? ' + kantong ' + RP(h.biayaKantong) : '') + (h.upah ? ' + upah ' + RP(h.upah) : '') + ') → modal ' + modalTeks
    + (h.susutKg > 0 ? ' · susut ' + adKG(h.susutKg) + ' terserap ke modal hasil' : '') + '. Stok karung/kemasan asal turun, stok kemasan jadi naik' + (h.biayaKantong ? ', stok kantong turun' : '') + '. Kas tidak bergerak.', kabarAwas: false } };
}

// ====================== BUKU ADUKAN: rincian, koreksi, hapus ======================
const adKelompok = () => { const kel = {}; ambilProduksi().forEach((p) => { const k = String(p.batchProduksi || p.id); if (!kel[k]) kel[k] = []; kel[k].push(p); }); return kel; };
const adBerlaku = (semua) => semua.filter((p) => !p.dikoreksiOleh).sort((a, b) => (a.barisKe || 0) - (b.barisKe || 0) || (Number(a.id) || 0) - (Number(b.id) || 0));
const adPertama = (baris) => baris.find((p) => (Array.isArray(p.sumberList) && p.sumberList.length) || (Array.isArray(p.sumberKemasanList) && p.sumberKemasanList.length) || p.kgDipakai > 0) || baris[0];
const adTeksBahan = (p) => { if (!p) return ''; const a = (Array.isArray(p.sumberList) && p.sumberList.length ? p.sumberList.map((s) => adKG(s.kg || 0) + ' ' + s.merk) : (p.merkSumber && !/^(CAMPURAN|DARI KEMASAN JADI)/.test(p.merkSumber) && p.kgDipakai > 0 ? [adKG(p.kgDipakai) + ' ' + p.merkSumber] : []))
  .concat((p.sumberKemasanList || []).map((k) => (k.unit || 0) + ' × ' + k.namaProduk + ' ' + adUkuranTeks(k.ukuranKemasan) + ' kg')); return a.join(' + ') || (p.merkSumber || '—'); };
const adTeksHasil = (baris) => baris.map((x) => (x.jumlahUnit || 0) + ' × ' + (x.namaProduk || '') + ' ' + adUkuranTeks(x.ukuranKemasan) + ' kg').join(' + ');
const adTotal = (baris) => baris.reduce((a, x) => a + (x.hppPerUnit || 0) * (x.jumlahUnit || 0), 0);
/** Buku adukan: satu kartu per adukan (baris seadukan digabung), terbaru dulu. Beli jadi dari kedatangan & pindah buku takar tidak ikut (milik layar lain). */
export function daftarAdukan(n) {
  const kel = adKelompok();
  const out = Object.keys(kel).map((k) => { const baris = adBerlaku(kel[k]); if (!baris.length) return null; const p1 = adPertama(baris); const jenis = adJenisProduksi(p1); if (jenis === 'beliJadi' || jenis === 'pindahBuku') return null;
    return { batch: k, tanggal: p1.tanggal || '', jam: p1.jam || '', jenis, bahanTeks: jenis === 'rework' ? 'dari karantina' : adTeksBahan(p1), hasilTeks: adTeksHasil(baris), total: Math.round(adTotal(baris)), baris: baris.length, dikoreksi: baris.some((x) => x.koreksiDari), kgMasuk: adB3((p1.kgDipakai || 0) + (p1.kgKemasanDipakai || 0)), kgJadi: adB3(baris.reduce((a, x) => a + (x.ukuranKemasan || 0) * (x.jumlahUnit || 0), 0)) }; }).filter(Boolean);
  return out.sort((a, b) => b.tanggal.localeCompare(a.tanggal) || b.jam.localeCompare(a.jam) || (Number(b.batch) || 0) - (Number(a.batch) || 0)).slice(0, n || 20);
}
/** Rincian satu adukan: biaya (bahan / kantong / upah / total tercatat), pembagian per hasil, timbangan kg, bisa dihapus atau tidak, riwayat koreksi. */
export function rincianAdukan(batch) {
  const semua = adKelompok()[String(batch)] || []; const baris = adBerlaku(semua); if (!baris.length) return null;
  const p1 = adPertama(baris); const jenis = adJenisProduksi(p1); const stokM = hitungStokKemasan();
  const kgMasuk = adB3((p1.kgDipakai || 0) + (p1.kgKemasanDipakai || 0)); const kgJadi = adB3(baris.reduce((a, x) => a + (x.ukuranKemasan || 0) * (x.jumlahUnit || 0), 0));
  const bahanRp = (p1.hppSumberPerKgDipakai || 0) * kgMasuk; const kantongRp = baris.reduce((a, x) => a + (x.biayaKemasan || 0), 0); const upahRp = baris.reduce((a, x) => a + (x.upahRepacking || 0), 0); const total = adTotal(baris);
  const hasil = baris.map((x) => { const st = stokM[kunciKemasan(x.namaProduk, x.ukuranKemasan)] || {}; const sisa = st.sisaUnit || 0; const kurang = Math.max(0, (x.jumlahUnit || 0) - sisa);
    return { id: x.id, nama: x.namaProduk || '', ukuran: x.ukuranKemasan, unit: x.jumlahUnit || 0, hppPerUnit: x.hppPerUnit || 0, bagian: (x.hppPerUnit || 0) * (x.jumlahUnit || 0), kantong: x.kantongJenis ? adLabelKantong(x.kantongJenis) + (x.kantongJumlah ? ' × ' + x.kantongJumlah : '') : 'tanpa kantong', sisaKini: sisa, kurangBilaDihapus: kurang }; });
  const tersangkut = hasil.filter((x) => x.kurangBilaDihapus > 0);
  const takBisa = jenis === 'rework' ? 'hasil rework dari karantina — keputusannya ada di tab Karantina, bukan di sini' : jenis === 'gabungKarung' ? 'catatan lama gabung-karung (Agu 2026) sengaja dibiarkan' : jenis !== 'adukan' ? 'bukan adukan' : '';
  const takBisaHapus = takBisa || (tersangkut.length ? tersangkut.map((x) => x.nama + ' ' + adUkuranTeks(x.ukuran) + ' kg: ' + x.kurangBilaDihapus + ' dari ' + x.unit + ' unit sudah terjual/terpakai').join('; ') + ' — kalau dihapus stok kemasan jadi minus; koreksi biayanya saja' : '');
  const riwayat = semua.filter((x) => x.koreksiDari || x.dikoreksiOleh).sort((a, b) => String(a.dikoreksiPada || '').localeCompare(String(b.dikoreksiPada || ''))).filter((x) => x.koreksiDari)
    .map((x) => ({ pada: String(x.dikoreksiPada || '').slice(0, 16).replace('T', ' '), alasan: x.alasanKoreksi || '', hppPerUnit: x.hppPerUnit || 0, nama: (x.namaProduk || '') + ' ' + adUkuranTeks(x.ukuranKemasan) + ' kg' }));
  return { batch: String(batch), tanggal: p1.tanggal || '', jam: p1.jam || '', jenis, bahanTeks: jenis === 'rework' ? 'dari karantina (' + (p1.catatan || '') + ')' : adTeksBahan(p1), hasilTeks: adTeksHasil(baris), jumlahBaris: p1.jumlahBaris || baris.length, barisBerlaku: baris.length,
    biaya: { bahan: bahanRp, kantong: kantongRp, upah: upahRp, total, terhitung: bahanRp + kantongRp + upahRp }, hasil, kgMasuk, kgJadi, susutKg: adB3(kgMasuk - kgJadi), bisaKoreksi: !takBisa, bisaHapus: !takBisaHapus, takBisaHapus, takBisaKoreksi: takBisa, riwayat, dikoreksi: baris.some((x) => x.koreksiDari) };
}
/** Koreksi SATU KESATUAN: total biaya yang benar → dibagi ulang ke semua baris (simpanKoreksiHpp cabang adukan); alasan wajib. */
export function susunKoreksiAdukan(batch, totalBaru, alasan, w) {
  const r = rincianAdukan(batch); if (!r) return { tolak: 'Adukan itu sudah tidak ada' };
  if (!r.bisaKoreksi) return { tolak: 'Koreksi ditolak: ' + r.takBisaKoreksi };
  const baris = adBerlaku(adKelompok()[String(batch)] || []);
  if (baris.length !== r.jumlahBaris) return { tolak: 'Koreksi ditolak: adukan ini seharusnya punya ' + r.jumlahBaris + ' baris hasil, yang masih berlaku cuma ' + baris.length + ' — sebagian sudah dikoreksi/dihapus sendiri-sendiri di sistem lama, biayanya tidak bisa dibagi ulang dengan benar. Hapus seluruh adukan lalu catat ulang' };
  if (adKosong(totalBaru)) return { tolak: 'Ketik total biaya adukan yang benar' };
  const total = adAngka(totalBaru); if (!(total >= 0)) return { tolak: 'Total biaya adukan tidak boleh minus' };
  if (adKosong(alasan)) return { tolak: 'Koreksi butuh alasan (mis. lupa upah kemas) — supaya jejaknya bisa dibaca nanti' };
  const bagi = bagiBiayaAdukan(baris, total); if (!bagi) return { tolak: 'Total kg hasil adukan ini nol — biayanya tidak bisa dibagi per baris' };
  const totalLama = Math.round(r.biaya.total); if (Math.round(total) === totalLama) return { tolak: 'Total biayanya sama dengan yang tercatat (' + RP(totalLama) + ') — tidak ada yang perlu dikoreksi' };
  const dokumen = [];
  baris.forEach((x, i) => { const idBaru = w.idUnik(); const pengganti = Object.assign({}, x, { id: idBaru, hppPerUnit: bagi[i], koreksiDari: x.id, alasanKoreksi: String(alasan).trim(), dikoreksiPada: w.kini }); delete pengganti.dikoreksiOleh;
    dokumen.push({ koleksi: 'produksiKemasan', data: pengganti }); dokumen.push({ koleksi: 'produksiKemasan', data: Object.assign({}, x, { dikoreksiOleh: idBaru, alasanKoreksi: String(alasan).trim() }) }); });
  const pratinjau = baris.map((x, i) => ({ nama: (x.namaProduk || '') + ' ' + adUkuranTeks(x.ukuranKemasan) + ' kg × ' + (x.jumlahUnit || 0), lama: x.hppPerUnit || 0, baru: bagi[i] }));
  return { dokumen, pratinjau, patch: { kabar: 'Adukan dikoreksi satu kesatuan: total biaya ' + RP(totalLama) + ' → ' + RP(Math.round(total)) + ' (' + String(alasan).trim() + '); modal per unit dibagi ulang: ' + pratinjau.map((p) => p.nama + ' ' + RP(Math.round(p.baru))).join(' · ') + '. Nilai stok kemasan & margin penjualan berikutnya ikut berubah; kas tidak.', kabarAwas: false } };
}
/** Pratinjau pembagian ulang untuk total yang sedang diketik (tanpa menulis). */
export function pratinjauKoreksiAdukan(batch, totalBaru) {
  const baris = adBerlaku(adKelompok()[String(batch)] || []); if (!baris.length || adKosong(totalBaru)) return [];
  const bagi = bagiBiayaAdukan(baris, adAngka(totalBaru)); if (!bagi) return [];
  return baris.map((x, i) => ({ nama: (x.namaProduk || '') + ' ' + adUkuranTeks(x.ukuranKemasan) + ' kg × ' + (x.jumlahUnit || 0), lama: x.hppPerUnit || 0, baru: bagi[i] }));
}
/** Hapus SELURUH adukan (semua dokumen seadukan + pasangan kantong id + 1), jejak ke bukuHapus; ditolak bila hasilnya sudah terjual/terpakai. */
export function susunHapusAdukan(batch, alasan, w) {
  const r = rincianAdukan(batch); if (!r) return { tolak: 'Adukan itu sudah tidak ada' };
  if (!r.bisaHapus) return { tolak: 'Hapus ditolak: ' + r.takBisaHapus };
  if (adKosong(alasan)) return { tolak: 'Hapus adukan butuh alasan — supaya jejaknya bisa dibaca nanti' };
  const semua = adKelompok()[String(batch)] || [];
  const hapus = []; semua.forEach((p) => { hapus.push({ koleksi: 'produksiKemasan', id: p.id }); hapus.push({ koleksi: 'stokBahanKemasan', id: p.id + 1 }); });
  return { hapus, dokumen: [{ koleksi: 'bukuHapus', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, koleksi: 'produksiKemasan', idDok: String(batch), tanggalDok: r.tanggal, pemasok: '', ringkas: 'adukan ' + r.bahanTeks + ' → ' + r.hasilTeks + ' · ' + RP(Math.round(r.biaya.total)), alasan: String(alasan).trim(), pasangan: semua.length } }],
    patch: { kabar: 'Adukan ' + r.tanggal + ' dihapus (' + String(alasan).trim() + '): ' + r.bahanTeks + ' kembali ke stok asal, ' + r.hasilTeks + ' dicabut dari stok kemasan' + (r.biaya.kantong ? ', kantongnya kembali' : '') + ' — jejaknya tetap di buku hapus', kabarAwas: false } };
}
