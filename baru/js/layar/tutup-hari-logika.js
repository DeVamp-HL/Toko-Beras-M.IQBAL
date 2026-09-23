// LAYAR UANG — K5 TUTUP HARI (dikunci owner 18 Sep 2026: C · Lembar Tutup — rekapnya ADALAH formulirnya). Logika tanpa DOM; pembantu berawalan td.
// Enam langkah: hitung uang di laci (SATU-SATUNYA yang wajib) · cek uang QRIS · sisihkan laba · timbang cepat · amankan laci · rekap & tutup.
// Yang dilewati DIAKUI di rekap; selisih di luar "yang dimaafkan" wajib beralasan; sesudah ditutup, perubahan hanya lewat tutup ulang (koreksi, jejaknya ke riwayat).
// "Setoran ke owner" sistem lama TIDAK dibawa (20 dokumennya nol) — diganti langkah Amankan laci (laci → brankas, pindah tempat).
//
// Semua langkah DITULIS SEKALIGUS saat "Tutup hari" (satu writeBatch), bentuk sistem lama + kolom sistem baru:
//  - tutupHari {id = tanggal, omzet, jumlahTransaksi, kasSeharusnya, kasFisikLaci/Rekening/Amplop/Brankas, selisih, alasanSelisih, setoranOwner 0, kasAwalBesokLaci,
//    menggantung, diubahPada, riwayat[]} persis simpanTutupHari + {sistemBaru, langkah, mdr, sisihJadi, amankanJadi, timbang, dihitung}. Tempat yang tidak dihitung diisi
//    angka CATATAN (dianggap sesuai) dan itu ditulis di `dihitung`, jadi selisih dokumen = selisih laci.
//  - amplopLaba {id 'am-'+tanggal, setor} = sisihan (nol pun ditulis, seperti sistem lama — tutup ulang menimpa, bukan menumpuk).
//  - pengeluaranHarian {id 'mdr-'+tanggal, kategori toko, dari rekening, mdr true} = potongan QRIS (MDR): perkiraan (tarif Atur harga) atau SEBENARNYA (qris − yang masuk).
//    Uang QRIS yang masuk rekening sudah dipotong penyedia; sistem lama mencatat QRIS penuh dan nol MDR — di sini potongannya jadi biaya toko hari itu.
//  - penyesuaianStok (dariTutup = tanggal) untuk timbang cepat yang beda; pindahUang {id 'pd-'+tanggal} laci → brankas untuk amankan laci.
//  - setoranKas 'st-' & modalOwner 'mo-st-' bernominal 0 (kompatibilitas: tutup ulang dari sistem lama menimpa id yang sama).
//  - pengaturan/titikKas = isi tempat uang SESUDAH tutup (laci akhir, rekening, amplop + sisihan, brankas + amankan) — patokan kas maju, inti ritualnya.
import { kasPada, hitungLabaBersihRentang, hitungStokKarungPerMerk, thDorongRiwayat } from '../mesin/beku.js';
import { daftarGerakanKas, caraBayarKunci } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPiutangMutasi, ambilPengeluaranHarian, ambilTutupHari, ambilPenyesuaianStok, ambilAmplopLaba, ambilPindahUang, ambilTitikKas } from '../data/toko.js';
import { RP, ANGKA, KG, hariIniIso, tanggalPendek } from '../inti/format.js';
import { aturHarga, hgPct } from './harga-logika.js';
import { ugAngka, ugKosong, ugAturDok, ugTambahHari, ugKiniDari, saldoKantong, ugNamaTempat } from './uang-logika.js';

export const ATUR_TUTUP_BAWAAN = { persenSisih: 10, kembalian: 500000, maafSelisih: 2000, alasan: ['Salah kasih kembalian', 'Ada pengeluaran belum dicatat', 'Ada penjualan belum dicatat', 'Belum tahu — dicari besok'], pecahan: [100000, 50000, 20000, 10000, 5000, 2000, 1000] };
export const LANGKAH_TUTUP = [['laci', 'Uang di laci'], ['rekening', 'Uang QRIS'], ['sisih', 'Sisihkan laba'], ['timbang', 'Timbang cepat'], ['amankan', 'Amankan laci'], ['rekap', 'Rekap & tutup']];
const tdB1 = (x) => Math.round(x * 10) / 10;
export function aturTutup() {
  const a = ugAturDok('tutupHari') || {}; const angka = (k, min, maks) => (isFinite(Number(a[k])) && Number(a[k]) >= min && Number(a[k]) <= maks ? Math.round(Number(a[k])) : ATUR_TUTUP_BAWAAN[k]); const H = aturHarga();
  return { persenSisih: angka('persenSisih', 0, 100), kembalian: angka('kembalian', 0, 100000000), maafSelisih: angka('maafSelisih', 0, 10000000), alasan: Array.isArray(a.alasan) && a.alasan.length ? a.alasan.map(String) : ATUR_TUTUP_BAWAAN.alasan.slice(), pecahan: ATUR_TUTUP_BAWAAN.pecahan.slice(),
    mdrPersen: H.mdrPersen, mdrBatas: H.mdrBatas, mdrTeks: 'Potongan ' + hgPct(H.mdrPersen) + ' untuk pembayaran di atas ' + RP(H.mdrBatas) + ' (Atur harga) — perkiraan, cocokkan dengan aplikasi QRIS', dariOwner: !!ugAturDok('tutupHari') };
}
export function susunAturTutup(isi, w) {
  const A = aturTutup(); const baca = (k, min, maks, teks) => { if (ugKosong(isi[k])) return A[k]; const n = ugAngka(isi[k]); if (n < min || n > maks) throw new Error(teks); return Math.round(n); };
  try { const persenSisih = baca('persenSisih', 0, 100, 'Persen laba disisihkan harus 0–100'); const kembalian = baca('kembalian', 0, 100000000, 'Uang kembalian harus 0–100.000.000'); const maafSelisih = baca('maafSelisih', 0, 10000000, 'Selisih yang dimaafkan harus 0–10.000.000');
    const alasan = (Array.isArray(isi.alasan) ? isi.alasan : A.alasan).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8); if (!alasan.length) return { tolak: 'Pilihan alasan selisih tidak boleh kosong' };
    return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tutupHari', tanggal: w.tanggal, jam: w.jam, persenSisih, kembalian, maafSelisih, alasan } }], patch: { aturT: null, kabar: 'Aturan tutup hari disimpan — sisihkan ' + persenSisih + ' % laba · kembalian ' + RP(kembalian) + ' · selisih dimaafkan sampai ' + RP(maafSelisih) + ' · potongan QRIS diatur di Atur harga', kabarAwas: false } };
  } catch (e) { return { tolak: e.message }; }
}
export const mdrSatu = (n, A) => (n > A.mdrBatas ? Math.round(n * A.mdrPersen / 10000) : 0);
/** Ringkasan hari `iso`: omzet per cara bayar, nota QRIS + potongannya, bon dibayar, laba, yang menggantung, penutupan yang sudah ada. */
export function ringkasHari(iso) {
  const A = aturTutup(); const jual = ambilPenjualan().filter((p) => p.tanggal === iso); const qrisNota = jual.filter((p) => caraBayarKunci(p) === 'qris').map((p) => ({ id: String(p.id), jam: p.jam || '', n: Number(p.hargaTotal) || 0, mdr: mdrSatu(Number(p.hargaTotal) || 0, A) }));
  const tunai = jual.filter((p) => caraBayarKunci(p) !== 'qris' && caraBayarKunci(p) !== 'kredit').reduce((a, p) => a + (Number(p.hargaTotal) || 0), 0); const qris = qrisNota.reduce((a, q) => a + q.n, 0); const kredit = jual.filter((p) => caraBayarKunci(p) === 'kredit').reduce((a, p) => a + (Number(p.hargaTotal) || 0), 0);
  const bonDibayar = ambilPiutangMutasi().filter((m) => m.tipe === 'bayar' && m.tanggal === iso && caraBayarKunci(m) !== 'qris').reduce((a, m) => a + (Number(m.nominal) || 0), 0);
  const mdrDok = ambilPengeluaranHarian().find((h) => String(h.id) === 'mdr-' + iso) || null; const mdrTercatat = mdrDok ? Number(mdrDok.nominal) || 0 : 0;
  const L = hitungLabaBersihRentang(iso, iso); const labaSebelumMdr = L.labaBersih + mdrTercatat;
  const semua = ambilPenjualan(); const rapikan = semua.filter((p) => p.perluKoreksi).length; const darurat = semua.filter((p) => p.jenis === 'kasir_darurat_nominal').length;
  return { iso, nota: jual.length, tunai, qris, qrisNota, kredit, omzet: tunai + qris + kredit, bonDibayar, mdrKira: qrisNota.reduce((a, q) => a + q.mdr, 0), mdrTercatat, labaSebelumMdr, laba: L, rapikan, darurat, sudah: ambilTutupHari().find((t) => t.tanggal === iso) || null, atur: A };
}
/** Tiga merek yang paling banyak keluar hari ini (kg) untuk ditimbang cepat, dengan angka catatan (kg di buku). */
export function barangTimbang(iso) {
  const kg = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== iso || !p.merkSumber) return; kg[p.merkSumber] = (kg[p.merkSumber] || 0) + (Number(p.totalKg) || 0); });
  const stok = hitungStokKarungPerMerk(iso); return Object.keys(kg).sort((a, b) => kg[b] - kg[a]).slice(0, 3).map((m) => ({ merk: m, keluar: tdB1(kg[m]), sistem: tdB1((stok[m] || {}).sisaKg || 0), hpp: (stok[m] || {}).hppTerakhirPerKg || 0 }));
}
const TD_KELOMPOK = [[/^Pelunasan piutang/, 'Bon dibayar tunai', 1], [/^Kasbon kembali/, 'Kasbon dikembalikan', 1], [/^Modal owner disetor|^Pinjaman/, 'Uang owner masuk', 1], [/nambah\)/, 'Tukar — pelanggan menambah', 1],
  [/^Harian — /, 'Uang keluar toko', -1], [/^Prive owner/, 'Ambil pribadi', -1], [/^Gaji /, 'Upah', -1], [/^Bayar bon /, 'Bayar bon pemasok', -1], [/^Kasbon — /, 'Kasbon karyawan/owner', -1], [/^Belanja beras|^Bongkar/, 'Belanja beras & bongkar', -1], [/^Setoran ke owner|^Modal owner ditarik/, 'Tarik modal / setoran', -1], [/^Bayar utang ke owner/, 'Bayar utang ke owner', -1], [/^Refund|^Selisih tukar|^Tukar/, 'Retur & tukar', -1], [/^Beli /, 'Beli kantong & bahan', -1], [/ — biaya /, 'Biaya bulanan', -1]];
/** Rumus "seharusnya ada di laci": laci semalam + yang masuk laci hari ini − yang keluar laci hari ini (dari gerakan kas mesin, tempat menurut saldoKantong) + pindah tempat hari ini. */
export function rumusLaci(iso) {
  const S1 = saldoKantong(iso); const t = ambilTitikKas(); if (!S1.ada) return { ada: false, seharusnya: null, baris: [], teks: 'titik kas belum disetel — laci yang seharusnya tidak bisa dihitung' };
  const kemarin = ugTambahHari(iso, -1); const S0 = t.tanggal < iso ? saldoKantong(kemarin) : null;
  const grup = {}; const dorong = (nama, arah, n) => { if (!(n > 0)) return; const k = nama; if (!grup[k]) grup[k] = { nama, arah, n: 0 }; grup[k].n += n; };
  // gerakan laci hari ini = selisih saldoKantong(iso) − saldoKantong(kemarin) dijelaskan per kelompok (kelompoknya dari label mesin)
  daftarGerakanKas().forEach((r) => { if (r.t !== iso || !(r.t > t.tanggal)) return; const k = TD_KELOMPOK.find((x) => x[0].test(r.label)); const kantong = r.keluar > 0 ? 'laci' : (r.kantong || 'laci');
    if (r.masuk > 0 && kantong === 'laci') dorong(k ? k[1] : 'Jual tunai', 1, r.masuk); if (r.keluar > 0) dorong(k ? k[1] : 'Keluar lain', -1, r.keluar); });
  ambilAmplopLaba().forEach((a) => { if (a.tutupBuku || a.tanggal !== iso || !(iso > t.tanggal)) return; dorong(a.tipe === 'ambil' ? 'Diambil dari amplop laba' : 'Disisihkan ke amplop laba', a.tipe === 'ambil' ? 1 : -1, Number(a.nominal) || 0); });
  ambilPindahUang().forEach((p) => { if (p.tanggal !== iso || !(iso > t.tanggal)) return; if (p.dari === 'laci') dorong('Dipindah ke ' + ugNamaTempat(p.ke).toLowerCase(), -1, Number(p.nominal) || 0); if (p.ke === 'laci') dorong('Diisi dari ' + ugNamaTempat(p.dari).toLowerCase(), 1, Number(p.nominal) || 0); });
  const baris = [{ nama: S0 ? 'Laci semalam (' + tanggalPendek(kemarin) + ')' : 'Patokan kas hari ini (' + tanggalPendek(t.tanggal) + ')', arah: 0, n: S0 ? S0.laci : Number(t.laci) || 0 }].concat(Object.keys(grup).map((k) => grup[k]).sort((a, b) => b.arah - a.arah || b.n - a.n));
  // dokumen yang tempatnya disebut bukan laci (mis. bayar bon dari rekening) tidak muncul di sini — persis: hanya yang menyentuh laci
  return { ada: true, seharusnya: S1.laci, baris, teks: 'seharusnya ' + RP(S1.laci), kasTotal: S1.total, S1, awal: baris[0].n, masuk: baris.filter((b) => b.arah === 1).reduce((a, b) => a + b.n, 0), keluar: baris.filter((b) => b.arah === -1).reduce((a, b) => a + b.n, 0) };
}
/**
 * Hitung seluruh lembar dari draf D = { lembar: {pecahan: lembar}, receh, alasan, rekPilih (sudah|belum|beda|''), rekNyata, sisih (null = saran), timbang: {merk: kg},
 * status: {laci|rekening|sisih|timbang|amankan: belum|beres|lewat} }. Satu tempat — dibaca kertas, rekap, dan penulis dokumennya.
 */
export function hitungTutup(D, kini) {
  const iso = hariIniIso(kini); const A = aturTutup(); const R = ringkasHari(iso); const RL = rumusLaci(iso); const st = D.status || {}; const beres = (k) => st[k] === 'beres'; const lewat = (k) => st[k] === 'lewat';
  const lembar = D.lembar || {}; const hitung = A.pecahan.reduce((a, p) => a + p * (Number(lembar[p]) || 0), 0) + (Number(D.receh) || 0);
  const seharusnya = RL.seharusnya; const selisih = seharusnya === null ? null : hitung - seharusnya; const dimaafkan = selisih !== null && Math.abs(selisih) <= A.maafSelisih;
  const rekNyata = D.rekPilih === 'beda' && D.rekNyata !== null && D.rekNyata !== undefined && D.rekNyata !== '' ? Math.round(ugAngka(D.rekNyata)) : null;
  const mdrJadi = D.rekPilih === 'beda' && rekNyata !== null ? Math.max(0, R.qris - rekNyata) : D.rekPilih === 'sudah' ? R.mdrKira : 0;   // 'belum' & kosong: tidak dicatat (dicek besok)
  const labaHari = R.labaSebelumMdr - (D.rekPilih === 'belum' || !D.rekPilih ? R.mdrKira : mdrJadi);
  const saranSisih = Math.max(0, Math.round(labaHari * A.persenSisih / 100 / 1000) * 1000); const sisihN = D.sisih === null || D.sisih === undefined || D.sisih === '' ? saranSisih : Math.max(0, Math.round(ugAngka(D.sisih)));
  // TUTUP ULANG (koreksi): sisihan & amankan malam ini yang SUDAH ditulis tetap ada (uangnya sudah pindah); yang dikerjakan lagi sekarang MENAMBAH, laci akhir = hitungan sekarang − yang pindah sesudah hitungan ini.
  const sisihLama = R.sudah ? Number((ambilAmplopLaba().find((a) => String(a.id) === 'am-' + iso) || {}).nominal) || 0 : 0; const amankanLama = R.sudah ? Number((ambilPindahUang().find((p) => String(p.id) === 'pd-' + iso) || {}).nominal) || 0 : 0; const mdrLama = R.mdrTercatat;
  const sisihBaru = beres('sisih') ? sisihN : 0; const amankanN = Math.max(0, hitung - sisihBaru - A.kembalian); const amankanBaru = beres('amankan') ? amankanN : 0; const laciAkhir = hitung - sisihBaru - amankanBaru;
  const sisihJadi = sisihLama + sisihBaru, amankanJadi = amankanLama + amankanBaru;
  const timbang = barangTimbang(iso).map((m) => { const x = (D.timbang || {})[m.merk]; const nyata = x === undefined || x === null || x === '' ? null : tdB1(ugAngka(x)); const beda = nyata === null ? 0 : tdB1(nyata - m.sistem); return Object.assign({}, m, { nyata, beda, rp: Math.round(beda * m.hpp), teks: nyata === null ? 'belum' : beda === 0 ? 'cocok' : (beda > 0 ? 'lebih ' : 'kurang ') + KG(Math.abs(beda)) }); });
  const belumTimbang = timbang.filter((m) => m.nyata === null).length; const bedaTimbang = tdB1(timbang.reduce((a, m) => a + m.beda, 0));
  const tolakLaci = !(hitung > 0) ? 'Hitung dulu uangnya' : seharusnya === null ? '' : (!dimaafkan && !D.alasan ? 'Selisihnya di luar yang dimaafkan — pilih alasannya' : '');
  const tolakRek = D.rekPilih === 'beda' ? (!(rekNyata > 0) ? 'Ketik jumlah yang benar-benar masuk' : rekNyata > R.qris ? 'Lebih besar dari penjualan QRIS hari ini (' + RP(R.qris) + ') — uang lain yang ikut masuk dicatat di Pindah uang atau Owner & toko' : '') : '';
  const tolakSisih = !beres('laci') ? 'Hitung laci dulu' : sisihN > hitung ? 'Laci cuma ' + RP(hitung) : !(sisihN > 0) ? 'Nominalnya nol — lewati saja' : '';
  const tolakAman = !beres('laci') ? 'Hitung laci dulu' : !(amankanN > 0) ? 'Isi laci tidak lebih dari uang kembalian ' + RP(A.kembalian) : '';
  const dilewati = LANGKAH_TUTUP.filter((l) => l[0] !== 'rekap' && !beres(l[0])).map((l) => l[1]);
  const tolakTutup = !beres('laci') ? 'Hitung uang di laci dulu — cuma itu yang tidak boleh dilewati' : '';
  const S = RL.S1 || saldoKantong(iso);
  return { iso, A, R, RL, S, hitung, seharusnya, selisih, dimaafkan, perluAlasan: hitung > 0 && selisih !== null && !dimaafkan, tolakLaci, rekNyata, mdrJadi, mdrLama, mdrDicatat: D.rekPilih === 'sudah' || (D.rekPilih === 'beda' && rekNyata !== null), labaHari, saranSisih, sisihN, sisihLama, sisihBaru, sisihJadi, amankanN, amankanLama, amankanBaru, amankanJadi, laciAkhir, timbang, belumTimbang, bedaTimbang, tolakRek, tolakSisih, tolakAman, dilewati, tolakTutup, koreksi: !!R.sudah,
    selisihTeks: !(hitung > 0) ? 'belum dihitung' : seharusnya === null ? 'seharusnya tidak bisa dihitung (titik kas belum disetel) — selisih TIDAK BISA DITANYA, bukan berarti cocok' : selisih === 0 ? 'PAS — tidak ada selisih' : (selisih > 0 ? 'LEBIH ' : 'KURANG ') + RP(Math.abs(selisih)) + (dimaafkan ? ' · masih dimaafkan (sampai ' + RP(A.maafSelisih) + ')' : ''),
    rekCatatan: D.rekPilih === 'sudah' ? 'sudah masuk ' + RP(R.qris - R.mdrKira) + ' (potongan perkiraan ' + RP(R.mdrKira) + ')' : D.rekPilih === 'belum' ? 'BELUM masuk semua — dicek lagi besok, potongan belum dicatat' : D.rekPilih === 'beda' && rekNyata !== null ? 'masuk ' + RP(rekNyata) + ' · potongan sebenarnya ' + RP(R.qris - rekNyata) : 'QRIS ' + RP(R.qris) + ' · potongan kira-kira ' + RP(R.mdrKira),
    status: LANGKAH_TUTUP.map((l) => ({ id: l[0], judul: l[1], st: l[0] === 'rekap' ? (R.sudah ? 'beres' : 'belum') : beres(l[0]) ? 'beres' : lewat(l[0]) ? 'dilewati' : l[0] === 'laci' ? 'wajib' : 'belum' })) };
}
/** Baris rekap (dibaca kertas, teks WA, dan dokumen). */
export function rekapTutup(H) {
  const R = H.R; const rows = [['Omzet · ' + R.nota + ' nota', RP(R.omzet), ''], ['  tunai', RP(R.tunai), ''], ['  QRIS', RP(R.qris), ''], ['  bon baru', RP(R.kredit), ''], ['Bon dibayar tunai', RP(R.bonDibayar), ''],
    ['Potongan QRIS (MDR) · ' + (H.mdrDicatat ? (H.rekNyata !== null ? 'sebenarnya' : 'perkiraan') : 'perkiraan, belum dicatat'), '−' + RP(H.mdrDicatat ? H.mdrJadi : R.mdrKira), ''], ['Laba hari ini · sudah dipotong MDR', RP(H.labaHari), ''],
    ['Laci dihitung', H.hitung > 0 ? RP(H.hitung) : 'belum', H.hitung > 0 ? '' : 'awas'], ['Selisih laci', H.hitung > 0 ? (H.selisih === null ? 'tidak bisa dihitung' : H.selisih === 0 ? 'pas' : RP(H.selisih) + (H.perluAlasan && H.alasanJadi ? ' · ' + H.alasanJadi : '')) : '—', H.hitung > 0 && H.selisih !== 0 ? 'awas' : ''],
    ['Disisihkan ke amplop laba', H.sisihJadi > 0 ? RP(H.sisihJadi) : (H.status.find((s) => s.id === 'sisih').st === 'dilewati' ? 'dilewati' : 'belum'), ''], ['Diamankan ke brankas', H.amankanJadi > 0 ? RP(H.amankanJadi) : (H.status.find((s) => s.id === 'amankan').st === 'dilewati' ? 'dilewati' : 'belum'), ''],
    ['Timbang cepat', H.belumTimbang === 0 && H.timbang.length ? (H.bedaTimbang === 0 ? 'semua cocok' : (H.bedaTimbang < 0 ? 'kurang ' : 'lebih ') + KG(Math.abs(H.bedaTimbang)) + ' (masuk susut)') : (H.status.find((s) => s.id === 'timbang').st === 'dilewati' ? 'dilewati' : H.timbang.length ? 'belum' : 'tidak ada beras karung/literan keluar'), ''],
    ['Tinggal di laci', H.hitung > 0 ? RP(H.laciAkhir) : '—', 'jumlah']];
  return rows.map((r) => ({ a: r[0], b: r[1], kelas: r[2] }));
}
export function teksRekap(H, iso, jam) {
  const L = ['TOKO BERAS M.IQBAL', 'REKAP TUTUP HARI · ' + tanggalPendek(iso) + (jam ? ' ' + jam : ''), ''];
  rekapTutup(H).forEach((r) => L.push((r.a + '                              ').slice(0, 30) + r.b)); if (H.dilewati.length) L.push('', 'Tidak dikerjakan: ' + H.dilewati.join(' · '));
  return L.join('\n');
}
/** Susun SEMUA dokumen malam ini sekaligus. D seperti hitungTutup + alasan; yakinUlang wajib bila hari ini sudah pernah ditutup. */
export function susunTutup(D, w, yakinUlang) {
  const H = hitungTutup(D, ugKiniDari(w)); if (H.tolakTutup) return { tolak: H.tolakTutup }; if (H.tolakLaci) return { tolak: H.tolakLaci };
  if (D.rekPilih === 'beda' && H.tolakRek) return { tolak: H.tolakRek };
  if (H.R.sudah && !yakinUlang) return { tolak: 'Hari ini sudah pernah ditutup jam ' + (H.R.sudah.jam || '') + '. Menutup lagi menulis catatan baru; yang lama turun ke riwayat bertanggal, tidak hilang. Ketuk sekali lagi', perluYakin: 'ulang' };
  // kasFisik* = isi SAAT DIHITUNG (sebelum sisihan/amankan malam ini), supaya Σ fisik − seharusnya = selisih laci persis seperti dokumen lama; isi SESUDAH tutup ada di titik kas
  const iso = H.iso; const S = H.S; const mdrBaru = H.mdrDicatat ? H.mdrJadi : 0; const rekening = S.ada ? S.rekening : 0; const amplop = S.ada ? S.amplop : 0; const brankas = S.ada ? S.brankas : 0;
  const alasan = H.perluAlasan ? String(D.alasan || '').trim() : (H.selisih === null ? String(D.alasan || 'patokan kas belum bisa dihitung').trim() : '');
  const dokTutup = { id: iso, tanggal: iso, jam: w.jam, omzet: H.R.omzet, jumlahTransaksi: H.R.nota, kasSeharusnya: H.RL.kasTotal === undefined ? null : H.RL.kasTotal, kasFisikLaci: H.hitung, kasFisikRekening: rekening, kasFisikAmplop: amplop, kasFisikBrankas: brankas,
    selisih: H.selisih, alasanSelisih: alasan, setoranOwner: 0, kasAwalBesokLaci: H.laciAkhir, menggantung: { rapikanKasir: H.R.rapikan, daruratBelumRinci: H.R.darurat }, diubahPada: w.kini,
    sistemBaru: true, dihitung: { laci: true, rekening: !!D.rekPilih, amplop: false, brankas: false }, langkah: H.status.map((s) => s.id + ':' + s.st).join(' '), mdr: { kira: H.R.mdrKira, jadi: H.mdrDicatat ? H.mdrJadi : 0, nyata: H.rekNyata, pilih: D.rekPilih || '' }, sisihJadi: H.sisihJadi, amankanJadi: H.amankanJadi, timbang: H.timbang.filter((m) => m.nyata !== null).map((m) => ({ merk: m.merk, sistem: m.sistem, fisik: m.nyata })), selisihLaci: H.selisih, labaHari: H.labaHari, dilewati: H.dilewati };
  thDorongRiwayat(dokTutup, H.R.sudah);
  const dokumen = [{ koleksi: 'tutupHari', data: dokTutup }, { koleksi: 'amplopLaba', data: { id: 'am-' + iso, tanggal: iso, jam: w.jam, tipe: 'setor', nominal: H.sisihJadi, catatan: 'Sisihan tutup hari' } },
    { koleksi: 'setoranKas', data: { id: 'st-' + iso, tanggal: iso, jam: w.jam, nominal: 0, catatan: 'Tutup hari' } }, { koleksi: 'modalOwner', data: { id: 'mo-st-' + iso, tanggal: iso, jam: w.jam, tipe: 'tarik', nominal: 0, catatan: 'Setoran tutup hari', dariSetoran: 'st-' + iso } }];
  const hapus = [];
  if (H.mdrDicatat && H.mdrJadi > 0) dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: 'mdr-' + iso, kategori: 'toko', tanggal: iso, jam: w.jam, keterangan: 'Potongan QRIS (MDR) · ' + H.R.qrisNota.length + ' nota' + (H.rekNyata !== null ? ' · sebenarnya' : ' · perkiraan'), nominal: H.mdrJadi, dari: 'rekening', mdr: true } });
  else if (ambilPengeluaranHarian().some((h) => String(h.id) === 'mdr-' + iso)) hapus.push({ koleksi: 'pengeluaranHarian', id: 'mdr-' + iso });
  if (H.amankanJadi > 0) dokumen.push({ koleksi: 'pindahUang', data: { id: 'pd-' + iso, tanggal: iso, jam: w.jam, dari: 'laci', ke: 'brankas', nominal: H.amankanJadi, alasan: 'Amankan laci (tutup hari)', biayaAdmin: 0, adminNama: '' } });
  ambilPenyesuaianStok().forEach((x) => { if (x.dariTutup === iso) hapus.push({ koleksi: 'penyesuaianStok', id: x.id }); });
  if (D.status && D.status.timbang === 'beres') H.timbang.forEach((m) => { if (m.nyata === null || m.beda === 0) return; dokumen.push({ koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: iso, jam: w.jam, merk: m.merk, kgSistem: m.sistem, kgFisik: m.nyata, selisihKg: m.beda, alasan: 'Timbang cepat tutup hari', nilaiRp: m.rp, hppPerKgSaatOpname: Math.round(m.hpp), dariTutup: iso } }); });
  // titik = isi SESUDAH tutup: S sudah memuat sisihan/amankan/MDR yang ditulis malam ini sebelumnya (bila tutup ulang); yang baru ditambahkan, MDR diganti
  const titik = { id: 'titikKas', tanggal: iso, laci: H.laciAkhir, rekening: rekening + H.mdrLama - mdrBaru, amplop: amplop + H.sisihBaru, brankas: brankas + H.amankanBaru, diubahPada: w.kini };
  dokumen.push({ koleksi: 'pengaturan', data: titik });
  return { dokumen, hapus, titik, H, teks: teksRekap(H, iso, w.jam), patch: { kabar: 'Hari ' + tanggalPendek(iso) + ' ditutup. Laci ' + RP(H.hitung) + (H.selisih === null ? ' (selisih tidak bisa ditanya)' : H.selisih === 0 ? ' pas' : ' selisih ' + RP(H.selisih)) + (H.sisihJadi ? ' · amplop +' + RP(H.sisihJadi) : '') + (H.amankanJadi ? ' · brankas +' + RP(H.amankanJadi) : '') + (H.mdrDicatat && H.mdrJadi ? ' · potongan QRIS ' + RP(H.mdrJadi) + ' jadi biaya' : '') + (H.dilewati.length ? ' · tidak dikerjakan: ' + H.dilewati.join(', ') : '') + '. Patokan kas maju ke malam ini.', kabarAwas: false, tertutup: true, koreksi: false } };
}
/** Penutupan yang sudah ada untuk digambar sesudah tertutup (dari dokumen, bukan draf). */
export function bacaTutup(dok) {
  if (!dok) return null; const fisik = (Number(dok.kasFisikLaci) || 0) + (Number(dok.kasFisikRekening) || 0) + (Number(dok.kasFisikAmplop) || 0) + (Number(dok.kasFisikBrankas) || 0);
  return { jam: dok.jam || '', laci: Number(dok.kasFisikLaci) || 0, selisih: dok.selisihLaci !== undefined ? dok.selisihLaci : dok.selisih, alasan: dok.alasanSelisih || '', sisih: Number(dok.sisihJadi) || 0, amankan: Number(dok.amankanJadi) || 0, mdr: dok.mdr ? Number(dok.mdr.jadi) || 0 : 0, laba: dok.labaHari, dilewati: dok.dilewati || [], sistemBaru: !!dok.sistemBaru, fisik, seharusnya: dok.kasSeharusnya, nKoreksi: (dok.riwayat || []).length, oleh: dok.oleh || '', laciAkhir: Number(dok.kasAwalBesokLaci) || 0 };
}
/** Malam-malam terakhir (riwayat tutup hari). */
export function riwayatTutup(n) { return ambilTutupHari().slice().sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal))).slice(0, n || 7).map((d) => Object.assign({ tanggal: d.tanggal }, bacaTutup(d))); }
export { ANGKA as tdAngka };
