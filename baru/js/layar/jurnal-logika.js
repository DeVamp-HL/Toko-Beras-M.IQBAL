// JURNAL BERPASANGAN (modul ERP no. 69, owner 26 Nov 2026 — sensus ulang 26 Nov bagian 2). Logika tanpa DOM; nama pembantu berawalan `jr` (bundel uji jsc satu lingkup).
//
// Keputusan owner (satu AskUserQuestion, 26 Nov 2026): jurnal = TURUNAN + KOREKSI OWNER. Tiap kejadian yang sudah dicatat (nota, bon, retur, kasbon, modal, kedatangan
// beras, bayar bon, upah & biaya bulanan, uang keluar, pindah uang, amplop laba, tutup hari, susut, aset tetap) DIBACA lalu dituliskan sebagai satu entri dua sisi
// (Σ debit = Σ kredit). Mesin beku tidak disentuh dan tidak ada catatan baru yang ditulis — kecuali entri koreksi yang owner ketik sendiri (aturanToko/jurnalKoreksi,
// owner saja, tanpa rules baru). Koreksi ikut neraca & laba JURNAL, bukan laba Laporan.
//
// Aturan yang membuat jurnal ini sama dengan Laporan, bukan rumus tandingan:
//  - uang per tempat: baris kas tiap kejadian diletakkan di tempatnya dengan penentu yang SAMA dengan saldoKantong (kantongGerakan); di akhir hari yang punya patokan
//    (isi tempat uang sesudah tutup hari / titik kas — khPatokan) uang disetel ke patokan itu, bedanya = akun "uang dihitung ulang" (bukan laba). Jadi saldo akun uang =
//    saldoKantong pada tanggal yang sama, persis.
//  - laba: pendapatan & beban dipetakan dari predikat mesin laba (hppTercatat, uangKembaliRetur, hppTaksiranRetur, toko + tokoDompet, jatah biaya bulanan per hari,
//    hapus buku, barisSusutStok, selisih laci tutup hari, penyusutan & uang keluar yang jadi aset) → Σ laba jurnal rentang mana pun = ugLabaBersih rentang itu.
//  - neraca: piutang, kasbon, utang pemasok, utang ke owner, modal, piutang ke pemasok dibangun dari kejadiannya lalu DICOCOKKAN ke buku pembantu mesin di akhir
//    periode. Yang memang berbeda arti ditulis sebagai baris khusus jurnal (kelebihan bayar pelanggan/kasbon/pemasok/owner, upah & biaya bulanan yang belum dibayar,
//    bon tanpa nama); stok dinilai ulang ke nilai Neraca (harga modal terakhir) dengan akun "selisih nilai persediaan" (bukan laba). Sisa yang tidak bisa dijelaskan
//    = "beda buku pembantu" — disebut, tidak disembunyikan. Beda "belum terjelaskan buku" di Neraca terurai jadi baris-baris bernama itu.
// Tahun yang sudah ditutup buku: catatannya diarsip, jurnalnya tidak bisa disusun (sama dengan neraca tanggal lampau) — ditolak dengan sebabnya.
import { hitungPiutang, hitungKasbon, hitungUtangPemasok, hitungUtangOwner, bayaranBiayaBulanan, barisSusutStok, hitungStokKarungPerMerk, hitungStokKemasan, jatahBiayaBulananHari } from '../mesin/beku.js';
import { caraBayarKunci, hppTercatat, uangKembaliRetur, hppTaksiranRetur, batchDiutang, daftarModalOwner, kasbonPotongGaji, kunciPelanggan, namaSingkatTrx, namaBulanPanjang, akhirBulanIso, TANGGAL_STOK_AWAL, LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPiutangMutasi, ambilKasbonMutasi, ambilSemuaBatch, ambilUtangPemasokMutasi, ambilPengeluaranHarian, ambilUtangOwnerMutasi, ambilRetur, ambilBahanKemasan, ambilBahanLiteran, ambilTutupHari, ambilTitikKas, ambilAmplopLaba, ambilPindahUang, cacheMentah, ingatPerVersi, ingatNeraca, potonganTerpakai, piutangPemasokPada, eraBuku, kunciSampai, catatanPertama, tahunDiarsip } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { kantongGerakan, saldoKantong, ugLabaBersih, ugAmplopLawan, ugAngka, ugKosong, priveRentang } from './uang-logika.js';
import { neracaTanggal, lpFinal, lpNamaBulan, aturLaporan } from './laporan-logika.js';
import { khPatokan } from './kas-rekening-logika.js';
import { astAtur, astSusut, astDariBiaya, astGeser, astTambahBulan, astAkhirBulan } from './aset-tetap-logika.js';

// ==================== bagan akun ====================
// kel: harta · kewajiban · modal · laba (pendapatan & beban). khusus = baris yang HANYA ada di jurnal (bukan baris Neraca Laporan) · penyesuaian = penjelas beda
// "belum terjelaskan buku" · koreksi = boleh dipakai entri koreksi owner.
export const JR_AKUN = [
  ['laci', 'Uang di laci', 'harta'], ['brankas', 'Uang di brankas', 'harta'], ['rekening', 'Uang di rekening usaha', 'harta'], ['amplop', 'Amplop laba', 'harta'],
  ['piutang', 'Piutang pelanggan (bon)', 'harta'], ['kasbon', 'Kasbon pegawai & owner', 'harta'], ['piutangPemasok', 'Piutang ke pemasok (potongan menunggu)', 'harta'],
  ['persediaan', 'Persediaan beras, kemasan, kantong & bahan', 'harta'], ['asetTetap', 'Aset tetap — harga beli', 'harta'], ['susutTerkumpul', 'Penyusutan terkumpul (pengurang aset tetap)', 'harta'],
  ['bonTanpaNama', 'Bon / kasbon tanpa nama (di luar buku pembantu)', 'harta', 'khusus'], ['lebihPemasok', 'Uang lebih dibayar ke pemasok', 'harta', 'khusus'],
  ['lebihOwner', 'Uang lebih dibayar ke owner', 'harta', 'khusus'], ['hartaLain', 'Harta lain (koreksi owner)', 'harta', 'koreksi'],
  ['utangPemasok', 'Utang ke pemasok', 'kewajiban'], ['utangOwner', 'Utang toko ke owner', 'kewajiban'],
  ['biayaBelum', 'Biaya bulanan & upah yang belum dibayar', 'kewajiban', 'khusus'], ['lebihPelanggan', 'Kelebihan bayar pelanggan', 'kewajiban', 'khusus'],
  ['lebihKasbon', 'Kasbon yang dibayar lebih', 'kewajiban', 'khusus'], ['antara', 'Akun antara (pasangan dua catatan — harus nol)', 'kewajiban', 'khusus'], ['utangLain', 'Utang lain (koreksi owner)', 'kewajiban', 'koreksi'],
  ['modal', 'Modal owner disetor', 'modal'], ['prive', 'Ambil pribadi owner (dari laci)', 'modal'],
  ['saldoAwal', 'Saldo awal & posisi awal (stok awal, bon lama, saldo pembuka)', 'modal', 'penyesuaian'], ['kasDihitung', 'Uang dihitung ulang (patokan kas · selisih titik)', 'modal', 'penyesuaian'],
  ['nilaiStok', 'Selisih nilai persediaan (stok dinilai harga modal terakhir)', 'modal', 'penyesuaian'], ['jualTanpaModal', 'Penjualan tanpa harga modal (di luar laba)', 'modal', 'penyesuaian'],
  ['tukarTambah', 'Tambahan uang tukar barang (di luar laba)', 'modal', 'penyesuaian'], ['asetBawaan', 'Aset tetap dibawa owner / sebelum sistem', 'modal', 'penyesuaian'],
  ['susutSebelum', 'Penyusutan sebelum tanggal mulai (tidak memotong laba)', 'modal', 'penyesuaian'], ['priveKasbon', 'Kasbon owner dijadikan ambil pribadi', 'modal', 'penyesuaian'],
  ['bedaBuku', 'Beda buku pembantu (belum terjelaskan)', 'modal', 'penyesuaian'], ['modalKoreksi', 'Koreksi modal (owner)', 'modal', 'koreksi'],
  ['penjualan', 'Penjualan (nota ber-modal)', 'laba'], ['retur', 'Retur & uang kembali', 'laba'], ['hpp', 'Harga modal barang terjual', 'laba'], ['hppKembali', 'Modal barang retur yang kembali ke stok', 'laba'],
  ['biayaHarian', 'Biaya toko harian (laci & dompet owner)', 'laba'], ['biayaBulanan', 'Biaya bulanan & upah (dibagi per hari)', 'laba'], ['hapusBuku', 'Hapus buku piutang', 'laba'],
  ['susut', 'Susut & selisih stok', 'laba'], ['lebihKurang', 'Lebih/kurang kas tutup hari', 'laba'], ['penyusutan', 'Penyusutan aset tetap', 'laba'],
  ['biayaJadiAset', 'Uang keluar dipindah jadi aset tetap', 'laba'], ['labaKoreksi', 'Pendapatan / biaya lain (koreksi owner)', 'laba', 'koreksi'],
].map((x, i) => ({ id: x[0], nama: x[1], kel: x[2], sifat: x[3] || '', urut: i, normal: x[2] === 'harta' || ['hpp', 'biayaHarian', 'biayaBulanan', 'hapusBuku', 'susut', 'penyusutan', 'retur'].indexOf(x[0]) >= 0 ? 'D' : 'K' }));
const JR_PETA = {}; JR_AKUN.forEach((a) => { JR_PETA[a.id] = a; });
export const jrAkun = (id) => JR_PETA[id] || null;
export const JR_UANG = ['laci', 'brankas', 'rekening', 'amplop'];
export const JR_KEL = [['harta', 'Harta'], ['kewajiban', 'Kewajiban'], ['modal', 'Modal & penyesuaian'], ['laba', 'Pendapatan & beban']];
const jrIso = (t) => /^\d{4}-\d\d-\d\d$/.test(String(t || ''));
const jrBulat = (n) => Math.round(Number(n) * 100) / 100;
const jrN = (v) => Number(v) || 0;
// satu entri: { t (tanggal, '' = tanpa tanggal = paling tua), j (jam), k (jenis), id (catatan sumber), ket, b: [[akun, n]] } — n > 0 debit, n < 0 kredit; Σ n = 0
const jrE = (t, j, k, id, ket, b) => ({ t: t || '', j: j || '', k, id: id === undefined || id === null ? '' : String(id), ket, b: b.filter((x) => x[1] && Math.abs(x[1]) >= 0.005) });

// ==================== kejadian (semua catatan, satu kali per versi data) ====================
const jrStokRetur = () => ingatPerVersi('jrStokRetur', () => ({ krg: hitungStokKarungPerMerk(), kem: hitungStokKemasan() }));
/** Semua entri kejadian (tanpa jatah biaya bulanan, penyusutan, setel patokan uang & penilaian akhir) — terurut tanggal. */
export function jrKejadian() {
  return ingatPerVersi('jrKejadian', () => {
    const out = []; const tempat = kantongGerakan(); const kas = (id, label, masuk, keluar, kantong) => tempat({ id: id || 0, label: label || '', masuk: masuk || 0, keluar: keluar || 0, kantong: keluar > 0 ? 'laci' : (kantong || 'laci') });
    const kantongBayar = (x) => (caraBayarKunci(x) === 'qris' || caraBayarKunci(x) === 'transfer' ? 'rekening' : 'laci');
    // penjualan (hanya yang masih berlaku — ambilPenjualan, sama dengan mesin)
    ambilPenjualan().forEach((p) => { const n = jrN(p.hargaTotal); const ber = hppTercatat(p); const akunJual = ber ? 'penjualan' : 'jualTanpaModal'; const kunci = caraBayarKunci(p); const b = [];
      if (kunci === 'kredit') b.push([p.caraBayar === 'Kredit' && kunciPelanggan(p.namaPelanggan) ? 'piutang' : 'bonTanpaNama', n]);
      else if (n > 0) b.push([kas(p.id, '', n, 0, kantongBayar(p)), n]); else b.push(['bedaBuku', n]);
      b.push([akunJual, -n]); if (ber) { const h = jrN(p.hppTotalSaatJual); b.push(['hpp', h], ['persediaan', -h]); }
      out.push(jrE(p.tanggal, p.jam, 'jual', p.id, 'Nota ' + (kunci === 'kredit' ? 'bon' : kunci === 'qris' ? 'QRIS' : kunci === 'transfer' ? 'transfer' : 'tunai') + ' — ' + namaSingkatTrx(p) + (ber ? '' : ' · tanpa modal'), b)); });
    // bon pelanggan
    ambilPiutangMutasi().forEach((m) => { const n = jrN(m.nominal); const akun = kunciPelanggan(m.namaPelanggan) ? 'piutang' : 'bonTanpaNama'; const nm = String(m.namaPelanggan || '').trim();
      if (m.tipe === 'bayar') out.push(jrE(m.tanggal, m.jam, 'bon', m.id, 'Bon dibayar — ' + nm, [[n > 0 ? kas(m.id, '', n, 0, kantongBayar(m)) : 'bedaBuku', n], [akun, -n]]));
      else if (m.tipe === 'saldoAwal') out.push(jrE(m.tanggal, m.jam, 'bon', m.id, 'Saldo awal bon — ' + nm, [[akun, n], ['saldoAwal', -n]]));
      else if (m.tipe === 'hapusBuku') out.push(jrE(m.tanggal, m.jam, 'bon', m.id, 'Bon dihapus buku — ' + nm, [['hapusBuku', n], [akun, -n]]));
      else if (m.tipe === 'retur') out.push(jrE(m.tanggal, m.jam, 'bon', m.id, 'Retur memotong bon — ' + nm, [['antara', n], [akun, -n]])); });
    // retur
    const R = ambilRetur(); const S = R.some((r) => r.kondisi === 'utuh') ? jrStokRetur() : null;
    R.forEach((r) => { const ru = uangKembaliRetur(r); const refund = jrN(r.nominalRefund); const sel = jrN(r.selisihHargaTukar); const pb = jrN(r.potongBon); const nama = r.merkSumber || r.namaProduk || '';
      const b = [['retur', ru]]; if (refund > 0) b.push([kas(r.id, '', 0, refund), -refund]); if (sel > 0) b.push([kas(r.id, '', 0, sel), -sel]); if (pb) b.push(['antara', -pb]);
      if (sel < 0) b.push([kas(r.id, '', -sel, 0), -sel], ['tukarTambah', sel]);
      if (r.kondisi === 'utuh' && S) { const hk = hppTaksiranRetur(r, S.krg, S.kem); b.push(['persediaan', hk], ['hppKembali', -hk]); }
      out.push(jrE(r.tanggal, r.jam, 'retur', r.id, 'Retur — ' + nama + (r.kondisi === 'utuh' ? ' (utuh, kembali ke stok)' : ''), b)); });
    // kasbon
    ambilKasbonMutasi().forEach((m) => { const n = jrN(m.nominal); const akun = kunciPelanggan(m.namaPegawai) ? 'kasbon' : 'bonTanpaNama'; const nm = String(m.namaPegawai || '').trim();
      if (m.tipe === 'bayar') {
        if (kasbonPotongGaji(m)) { const ke = m.alih === 'prive' ? 'priveKasbon' : m.alih === 'salingLunas' ? 'antara' : 'biayaBelum';
          out.push(jrE(m.tanggal, m.jam, 'kasbon', m.id, (m.alih === 'prive' ? 'Kasbon owner dijadikan ambil pribadi' : m.alih === 'salingLunas' ? 'Kasbon owner saling lunas dengan utang toko' : 'Kasbon dipotong gaji — ' + nm), [[ke, n], [akun, -n]])); }
        else out.push(jrE(m.tanggal, m.jam, 'kasbon', m.id, 'Kasbon kembali — ' + nm, [[n > 0 ? kas(m.id, '', n, 0, kantongBayar(m)) : 'bedaBuku', n], [akun, -n]]));
      } else if (m.tipe === 'saldoAwal') out.push(jrE(m.tanggal, m.jam, 'kasbon', m.id, 'Saldo awal kasbon — ' + nm, [[akun, n], ['saldoAwal', -n]]));
      else if (m.tipe === 'ambil') out.push(jrE(m.tanggal, m.jam, 'kasbon', m.id, 'Kasbon — ' + nm, [[akun, n], [n > 0 ? kas(m.id, '', 0, n) : 'bedaBuku', -n]]));
      else out.push(jrE(m.tanggal, m.jam, 'kasbon', m.id, 'Kasbon jenis tak dikenal — ' + nm, [[akun, n], ['bedaBuku', -n]])); });
    // modal owner (setoranKas lama ikut lewat daftarModalOwner, sama dengan mesin)
    daftarModalOwner().forEach((x) => { const n = jrN(x.nominal); const setor = x.tipe === 'setor';
      if (x.tutupBuku) out.push(jrE(x.tanggal, x.jam, 'modal', x.id, 'Modal owner dibawa dari tahun lalu', setor ? [['saldoAwal', n], ['modal', -n]] : [['modal', n], ['saldoAwal', -n]]));
      else if (x.pinjaman) out.push(jrE(x.tanggal, x.jam, 'modal', x.id, 'Pinjaman owner masuk', setor ? [[kas(x.id, '', n, 0), n], ['antara', -n]] : [['antara', n], [kas(x.id, '', 0, n), -n]]));
      else if (setor) out.push(jrE(x.tanggal, x.jam, 'modal', x.id, 'Setor modal owner' + (x.catatan ? ' — ' + x.catatan : ''), [[n > 0 ? kas(x.id, '', n, 0) : 'bedaBuku', n], ['modal', -n]]));
      else out.push(jrE(x.tanggal, x.jam, 'modal', x.id, (x.dariSetoranLama || x.dariSetoran ? 'Setoran ke owner' : 'Tarik modal owner') + (x.catatan ? ' — ' + x.catatan : ''), [['modal', n], [n > 0 ? kas(x.id, '', 0, n) : 'bedaBuku', -n]])); });
    // kedatangan beras + potongan pemasok yang menunggu (piutang ke pemasok)
    const pk = potonganTerpakai();
    ambilSemuaBatch().forEach((k) => { const nilai = (k.merkList || []).reduce((x, m) => x + jrN(m.subtotalHarga), 0); const bongkar = jrN(k.biayaBongkar); const pm = String(k.pemasok || '').trim();
      if (k.stokAwal) out.push(jrE(k.tanggal, '', 'beli', k.id, 'Stok awal — ' + (pm || 'tanpa nama'), [['persediaan', nilai], ['saldoAwal', -nilai]]));
      else if (batchDiutang(k)) out.push(jrE(k.tanggal, '', 'beli', k.id, 'Beras datang, bon — ' + pm + (bongkar ? ' · bongkar tunai' : ''), [['persediaan', nilai + bongkar], [pm ? 'utangPemasok' : 'bedaBuku', -nilai]].concat(bongkar > 0 ? [[kas(k.id, '', 0, bongkar), -bongkar]] : [])));
      else { const t = nilai + bongkar; out.push(jrE(k.tanggal, '', 'beli', k.id, 'Beras datang, tunai — ' + pm, [['persediaan', t], [t > 0 ? kas(k.id, '', 0, t) : 'bedaBuku', -t]])); }
      if (Array.isArray(k.potongan)) k.potongan.forEach((x, i) => { if (!x || x.tempat !== 'berikut' || !(jrN(x.tunggu) > 0)) return; const rp = Math.round(jrN(x.tunggu)); const u = pk[String(k.id) + '|' + i];
        out.push(jrE(k.tanggal, '', 'beli', k.id + '|' + i, 'Potongan pemasok menunggu — ' + pm, [['piutangPemasok', rp], ['persediaan', -rp]]));
        const selesai = x.dipakai ? String((x.dipakai && x.dipakai.tanggal) || '') : u ? String(u.selesai || u.tanggal || '') : null;
        if (selesai !== null) out.push(jrE(selesai, '', 'beli', k.id + '|' + i + '|selesai', 'Potongan pemasok terpakai / diterima — ' + pm, [['persediaan', rp], ['piutangPemasok', -rp]])); }); });
    // bon pemasok
    ambilUtangPemasokMutasi().forEach((m) => { const n = jrN(m.nominal); const pm = String(m.pemasok || '').trim();
      if (m.tipe === 'saldoAwal') out.push(jrE(m.bonTanggal || '', m.jam, 'pemasok', m.id, 'Bon pemasok lama — ' + pm, [['saldoAwal', n], [pm ? 'utangPemasok' : 'bedaBuku', -n]]));
      else if (m.tipe === 'bayar') out.push(jrE(m.tanggal, m.jam, 'pemasok', m.id, 'Bayar bon — ' + pm, [['utangPemasok', n], [n > 0 ? kas(m.id, '', 0, n) : 'bedaBuku', -n]])); });
    // biaya bulanan & upah: yang DIBAYAR (jatahnya ke laba dibagi per hari — jrJatah)
    bayaranBiayaBulanan().forEach((x) => { if (!x.tanggal || !(x.nominal > 0)) return;
      out.push(jrE(x.tanggal, '', 'bulanan', 'bb|' + x.bulan + '|' + x.pos, 'Bayar ' + x.label + ' — ' + namaBulanPanjang(x.bulan + '-01'), [['biayaBelum', x.nominal], [kas(0, x.label + ' — biaya ' + namaBulanPanjang(x.bulan + '-01'), 0, x.nominal), -x.nominal]])); });
    // uang keluar
    ambilPengeluaranHarian().forEach((h) => { const n = jrN(h.nominal); const ket = String(h.keterangan || '').trim() || '(tanpa keterangan)';
      if (h.kategori === 'owner') out.push(jrE(h.tanggal, h.jam, 'keluar', h.id, 'Ambil pribadi — ' + ket, [['prive', n], [n > 0 ? kas(h.id, '', 0, n) : 'bedaBuku', -n]]));
      else if (h.kategori === 'toko') out.push(jrE(h.tanggal, h.jam, 'keluar', h.id, 'Uang keluar toko — ' + ket, [['biayaHarian', n], [n > 0 ? kas(h.id, '', 0, n) : 'bedaBuku', -n]]));
      else if (h.kategori === 'tokoDompet') out.push(jrE(h.tanggal, h.jam, 'keluar', h.id, 'Belanja toko pakai dompet owner — ' + ket, [['biayaHarian', n], ['utangOwner', -n]])); });
    // utang toko ke owner
    ambilUtangOwnerMutasi().forEach((m) => { const n = jrN(m.nominal);
      if (m.tipe === 'bayar') out.push(jrE(m.tanggal, m.jam, 'owner', m.id, 'Bayar utang ke owner' + (m.catatan ? ' — ' + m.catatan : ''), [['utangOwner', n], [n > 0 ? kas(m.id, '', 0, n) : 'bedaBuku', -n]]));
      else if (m.tipe === 'saldoAwal') out.push(jrE(m.tanggal, m.jam, 'owner', m.id, m.pinjaman ? 'Pinjaman owner (utang toko)' : m.alih === 'salingLunas' ? 'Utang toko ke owner berkurang (saling lunas)' : 'Saldo awal utang toko ke owner', [[m.pinjaman || m.alih === 'salingLunas' ? 'antara' : 'saldoAwal', n], ['utangOwner', -n]])); });
    // kantong & bahan
    ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((b) => { if (b.tipe !== 'beli') return; const n = jrN(b.hargaTotal); const nm = LABEL_BAHAN_KEMASAN[b.jenis] || LABEL_BAHAN_LITERAN[b.jenis] || b.jenis;
      out.push(jrE(b.tanggal, '', 'bahan', b.id, 'Beli kantong / bahan — ' + nm + (b.tanggal === TANGGAL_STOK_AWAL ? ' (stok awal)' : ''), b.tanggal === TANGGAL_STOK_AWAL ? [['persediaan', n], ['saldoAwal', -n]] : [['persediaan', n], [n > 0 ? kas(b.id, '', 0, n) : 'bedaBuku', -n]])); });
    // susut & selisih stok (baris mesin yang sama dengan laba)
    barisSusutStok(() => true).forEach((x, i) => { const n = jrN(x.nilaiRp); out.push(jrE(x.tanggal, x.jam, 'susut', 'su|' + i, (n < 0 ? 'Susut / selisih kurang — ' : 'Selisih lebih — ') + x.nama, [['susut', -n], ['persediaan', n]])); });
    // lebih/kurang laci tutup hari (aturan ugLebihKurangKas: selisih catatan + riwayat tutup ulang)
    const sel = (x) => Number((x && (x.selisihLaci || x.selisih)) || 0);
    ambilTutupHari().forEach((t) => { if (!t || !jrIso(t.tanggal)) return; const s = (Array.isArray(t.riwayat) ? t.riwayat : []).reduce((a, x) => a + sel(x), sel(t)); if (!s) return;
      out.push(jrE(t.tanggal, t.jam || '23:59', 'tutup', 'th|' + t.tanggal, s > 0 ? 'Laci lebih saat tutup hari' : 'Laci kurang saat tutup hari', [['laci', s], ['lebihKurang', -s]])); });
    // amplop laba & pindah uang (pindah tempat — tidak menyentuh laba)
    ambilAmplopLaba().forEach((a) => { if (a.tutupBuku) return; const n = jrN(a.nominal); if (!n) return; const lawan = ugAmplopLawan(a);
      out.push(jrE(a.tanggal, a.jam, 'pindah', a.id, a.tipe === 'ambil' ? 'Ambil dari amplop laba' : 'Sisihkan ke amplop laba', a.tipe === 'ambil' ? [[lawan, n], ['amplop', -n]] : [['amplop', n], [lawan, -n]])); });
    ambilPindahUang().forEach((p) => { const n = jrN(p.nominal); if (!n) return; const sah = (x) => JR_UANG.indexOf(x) >= 0 && x !== 'amplop';
      out.push(jrE(p.tanggal, p.jam, 'pindah', p.id, 'Pindah uang' + (p.alasan ? ' — ' + p.alasan : ''), [[sah(p.ke) ? p.ke : 'bedaBuku', n], [sah(p.dari) ? p.dari : 'bedaBuku', -n]])); });
    // aset tetap: perolehan (penyusutan = jrSusutAset, per periode)
    const tunjuk = {}; astDariBiaya().forEach((x) => { if (x.ada) tunjuk[x.aset] = x; });
    astAtur().aset.forEach((a) => { const T = tunjuk[a.id]; const dari = T ? Math.min(a.harga, T.n) : 0;
      out.push(jrE(T ? T.tanggal : a.tanggalBeli, '', 'aset', a.id, 'Aset tetap — ' + a.nama + (T ? ' (dari uang keluar ' + tanggalPendek(T.tanggal) + ')' : ' (dibawa owner / sebelum sistem)'), [['asetTetap', a.harga], ['biayaJadiAset', -dari], ['asetBawaan', -(a.harga - dari)]])); });
    // isian lama satu angka (aturanToko/laporan.asetTetap) — dipakai Neraca selama daftar aset kosong: barang tanpa catatan asal, dicatat di hari pertama buku
    const AL = aturLaporan(); if (!astAtur().aset.length && AL.asetTetap > 0) out.push(jrE(catatanPertama() || '', '', 'aset', 'isianLama', 'Aset tetap isian lama owner' + (AL.asetKet ? ' — ' + AL.asetKet : '') + ' (tanpa tanggal beli & tanpa penyusutan)', [['asetTetap', AL.asetTetap], ['asetBawaan', -AL.asetTetap]]));
    // koreksi owner
    jrKoreksi().entri.forEach((x) => out.push(jrE(x.tanggal, '', 'koreksi', x.id, 'Koreksi owner — ' + x.ket, x.baris.map((r) => [r.akun, r.n]))));
    return out.sort((a, b) => a.t.localeCompare(b.t) || a.j.localeCompare(b.j));
  });
}

// ==================== jatah biaya bulanan & penyusutan (per bagian bulan di dalam rentang) ====================
const jrBulanBerikut = (k) => astTambahBulan(k + '-01', 1).slice(0, 7);
/** Jatah biaya bulanan rentang [a, b] (mesin: jatahBiayaBulananHari per hari, gaji KOTOR) per bulan → [{ bulan, dari, sampai, n }]. */
function jrJatah(a, b) {
  const B = bayaranBiayaBulanan(); const bulan = {}; B.forEach((x) => { bulan[x.bulan] = true; }); const out = [];
  Object.keys(bulan).sort().forEach((k) => { const d = (a > k + '-01' ? a : k + '-01'), s = (b < akhirBulanIso(k) ? b : akhirBulanIso(k)); if (d > s) return; let n = 0; for (let t = d; t <= s; t = astGeser(t, 1)) n += jatahBiayaBulananHari(t, B); if (n) out.push({ bulan: k, dari: d, sampai: s, n }); });
  return out;
}
/** Penyusutan rentang [a, b] per bulan → [{ bulan, dari, sampai, laba (hari ≥ mulai), sebelum }]. */
function jrSusutAset(a, b) {
  const A = astAtur(); if (!A.aset.length) return []; const out = []; const awal = A.aset.reduce((m, x) => (x.tanggalBeli < m ? x.tanggalBeli : m), b); let k = (a > awal ? a : awal).slice(0, 7);
  for (let i = 0; i < 1200 && k <= b.slice(0, 7); i++, k = jrBulanBerikut(k)) { const d = a > k + '-01' ? a : k + '-01', s = b < astAkhirBulan(k) ? b : astAkhirBulan(k); if (d > s) continue;
    const seb = s < A.mulai ? s : astGeser(A.mulai, -1); let laba = 0, sebelum = 0;
    A.aset.forEach((x) => { const tot = astSusut(x, s) - astSusut(x, astGeser(d, -1)); const pre = d <= seb ? astSusut(x, seb) - astSusut(x, astGeser(d, -1)) : 0; sebelum += pre; laba += tot - pre; });
    if (laba || sebelum) out.push({ bulan: k, dari: d, sampai: s, laba, sebelum }); }
  return out;
}

// ==================== patokan uang ====================
/** Tanggal patokan (hitungan tutup hari / titik kas) s.d. b, tiap tanggal satu patokan (khPatokan hari itu). */
function jrPatokan(a, b) {
  const tg = {}; ambilTutupHari().forEach((d) => { if (d && d.titik && jrIso(d.tanggal)) tg[d.tanggal] = true; }); const T = ambilTitikKas(); if (T && jrIso(T.tanggal)) tg[T.tanggal] = true;
  return Object.keys(tg).filter((t) => t >= a && t <= b).sort().map((t) => khPatokan(t));
}

// ==================== saldo per tanggal ====================
const jrTambah = (S, b) => b.forEach((x) => { S[x[0]] = (S[x[0]] || 0) + x[1]; });
const jrNol = () => { const S = {}; JR_AKUN.forEach((a) => { S[a.id] = 0; }); return S; };
/** Laba (pendapatan − beban) dari peta saldo: Σ akun laba dengan tanda kredit. */
export const jrLabaDari = (S) => JR_AKUN.filter((a) => a.kel === 'laba').reduce((x, a) => x - (S[a.id] || 0), 0);
/**
 * Penilaian akhir per tanggal s (bukan kejadian; berubah tiap tanggal): persediaan ke nilai Neraca, saldo minus buku pembantu ke baris khusus, sisa ke beda buku.
 * S = saldo kejadian + jatah + penyusutan + uang (sudah disetel ke patokan). → { b: baris entri, rinci: { … } }
 */
function jrNilaiAkhir(S, s) {
  const N = ingatNeraca(s); const b = []; const r = {};
  r.stok = Math.round(N.stok - (S.persediaan || 0)); b.push(['persediaan', r.stok], ['nilaiStok', -r.stok]);
  const sub = (akun, daftar, lebih) => { const pos = daftar.filter((x) => x.sisa > 0).reduce((a, x) => a + x.sisa, 0), neg = daftar.filter((x) => x.sisa < 0).reduce((a, x) => a + x.sisa, 0);
    const beda = jrBulat((S[akun] || 0) - (pos + neg)); b.push([akun, -neg], [lebih, neg]); if (Math.abs(beda) >= 0.005) b.push([akun, -beda], ['bedaBuku', beda]); r[akun] = { pos: jrBulat(pos), neg: jrBulat(neg), beda }; };
  sub('piutang', hitungPiutang(s), 'lebihPelanggan'); sub('kasbon', hitungKasbon(s), 'lebihKasbon');
  const UP = hitungUtangPemasok(s); const u = UP.reduce((a, x) => a + x.totalUtang, 0), tk = UP.reduce((a, x) => a + (x.tekor || 0), 0); const ku = -(S.utangPemasok || 0);
  const bu = jrBulat(u - ku - tk); b.push(['lebihPemasok', tk], ['utangPemasok', -tk]); if (Math.abs(bu) >= 0.005) b.push(['utangPemasok', -bu], ['bedaBuku', bu]); r.utangPemasok = { utang: u, tekor: tk, beda: bu };
  const UO = hitungUtangOwner(s); const ko = -(S.utangOwner || 0); const bo = jrBulat(UO.sisa - ko - UO.tekor); b.push(['lebihOwner', UO.tekor], ['utangOwner', -UO.tekor]); if (Math.abs(bo) >= 0.005) b.push(['utangOwner', -bo], ['bedaBuku', bo]); r.utangOwner = { utang: UO.sisa, tekor: UO.tekor, beda: bo };
  const pp = piutangPemasokPada(s).rp; const bp = jrBulat(pp - (S.piutangPemasok || 0)); if (Math.abs(bp) >= 0.005) b.push(['piutangPemasok', bp], ['bedaBuku', -bp]); r.piutangPemasok = { rp: pp, beda: bp };
  return { b: b.filter((x) => x[1] && Math.abs(x[1]) >= 0.005), rinci: r };
}
/** Tolak bila rentang menyentuh tahun yang sudah ditutup buku (catatannya diarsip). */
export function jrTolakArsip(dari, sampai) {
  const era = eraBuku(); if (era === null) return ''; const a = Number(String(dari || '0000').slice(0, 4)), b = Number(String(sampai).slice(0, 4));
  for (let y = a; y <= b; y++) if (tahunDiarsip(y)) return 'Catatan ' + y + ' sudah diarsip (tutup buku ' + y + ') — jurnalnya ada di berkas arsip; jurnal di sini mulai 1 Jan ' + (era + 1);
  return '';
}
/**
 * Saldo semua akun pada AKHIR hari s: kejadian ≤ s + jatah biaya bulanan + penyusutan s.d. s + uang disetel ke patokan terakhir ≤ s + penilaian akhir.
 * → { s, saldo: { akun: n (debit +) }, uangAda, patokan, akhir: rinci penilaian, kasMesin: Σ baris uang kejadian sesudah patokan }
 */
export function jrSaldo(s) {
  return ingatPerVersi('jrSaldo|' + s + '|' + JSON.stringify(ambilTitikKas()), () => {   // titik kas perangkat (localStorage) tidak menaikkan versi data — ikut kunci, sama dengan ingatNeraca
    const S = jrNol(); const awalJatah = '0000-01-01'; const L = {}, sesudah = {}; JR_UANG.forEach((k) => { L[k] = 0; sesudah[k] = 0; });
    const P = jrPatokan(awalJatah, s).slice(-1)[0] || null;
    jrKejadian().forEach((e) => { if (e.t > s) return; e.b.forEach((x) => { if (JR_UANG.indexOf(x[0]) >= 0) { L[x[0]] += x[1]; if (!P || e.t > P.tanggal) sesudah[x[0]] += x[1]; } else S[x[0]] += x[1]; }); });
    jrJatah(awalJatah, s).forEach((x) => { S.biayaBulanan += x.n; S.biayaBelum -= x.n; });
    jrSusutAset(awalJatah, s).forEach((x) => { S.penyusutan += x.laba; S.susutSebelum += x.sebelum; S.susutTerkumpul -= x.laba + x.sebelum; });
    // uang = patokan terakhir ≤ s + baris uang kejadian sesudahnya (= saldoKantong dengan patokan itu); selisihnya dengan Σ semua baris uang = uang dihitung ulang
    JR_UANG.forEach((k) => { S[k] = (P ? jrN(P[k]) : 0) + sesudah[k]; S.kasDihitung += L[k] - S[k]; });
    const A = jrNilaiAkhir(S, s); jrTambah(S, A.b);
    Object.keys(S).forEach((k) => { S[k] = jrBulat(S[k]); });
    return { s, saldo: S, uangAda: !!P, patokan: P, akhir: A.rinci, bAkhir: A.b };
  });
}

// ==================== satu periode: saldo awal + entri + saldo akhir ====================
const jrSalin = (e) => ({ t: e.t, j: e.j, k: e.k, id: e.id, ket: e.ket, b: e.b.map((x) => [x[0], x[1]]) });
/**
 * Jurnal rentang [dari, sampai]: saldo awal (akhir hari sebelum dari), entri kejadian + jatah biaya bulanan + penyusutan per bulan + setel uang ke patokan +
 * penilaian akhir (selisih nilai di akhir rentang − di awal), saldo akhir, neraca saldo per akun. Penjaga: tiap entri Σ debit = Σ kredit; saldo awal + entri =
 * saldo akhir per akun (`menutup`).
 */
export function jrPeriode(dari, sampai) {
  return ingatPerVersi('jrPeriode|' + dari + '|' + sampai + '|' + JSON.stringify(ambilTitikKas()), () => {
    const tolak = jrTolakArsip(dari, sampai); if (tolak) return { dari, sampai, tolak };
    const A = jrSaldo(astGeser(dari, -1)), Z = jrSaldo(sampai);
    const E = jrKejadian().filter((e) => e.t >= dari && e.t <= sampai).map(jrSalin);
    jrJatah(dari, sampai).forEach((x) => E.push(jrE(x.sampai, '23:58', 'jatah', 'jt|' + x.bulan, 'Biaya bulanan & upah ' + lpNamaBulan(x.bulan) + ' — jatah ' + tanggalPendek(x.dari) + ' s.d. ' + tanggalPendek(x.sampai) + ' (dibagi rata per hari)', [['biayaBulanan', x.n], ['biayaBelum', -x.n]])));
    jrSusutAset(dari, sampai).forEach((x) => E.push(jrE(x.sampai, '23:58', 'penyusutan', 'ps|' + x.bulan, 'Penyusutan aset tetap ' + lpNamaBulan(x.bulan) + ' (' + tanggalPendek(x.dari) + ' s.d. ' + tanggalPendek(x.sampai) + ')' + (x.sebelum ? ' — sebagian sebelum tanggal mulai, tidak memotong laba' : ''), [['penyusutan', x.laba], ['susutSebelum', x.sebelum], ['susutTerkumpul', -(x.laba + x.sebelum)]])));
    // setel uang ke patokan: di akhir tiap hari berpatokan, uang = patokan; bedanya ke "uang dihitung ulang"
    const jalan = {}; JR_UANG.forEach((k) => { jalan[k] = A.saldo[k]; }); const P = jrPatokan(dari, sampai); let iP = 0;
    const urut = E.slice().sort((x, y) => x.t.localeCompare(y.t)); const setel = (p) => { const b = []; JR_UANG.forEach((k) => { const v = jrBulat(jrN(p[k]) - jalan[k]); if (v) b.push([k, v], ['kasDihitung', -v]); jalan[k] = jrN(p[k]); });
      if (b.length) E.push(jrE(p.tanggal, '99', 'patokan', 'pk|' + p.tanggal, 'Uang disetel ke ' + p.sumber + ' (beda = uang dihitung ulang, bukan laba)', b)); };
    urut.forEach((e) => { while (iP < P.length && P[iP].tanggal < e.t) setel(P[iP++]); e.b.forEach((x) => { if (JR_UANG.indexOf(x[0]) >= 0) jalan[x[0]] += x[1]; }); });
    while (iP < P.length) setel(P[iP++]);
    // penilaian akhir: selisih nilai di akhir rentang dikurangi yang sudah ada di saldo awal
    const nilai = {}; Z.bAkhir.forEach((x) => { nilai[x[0]] = (nilai[x[0]] || 0) + x[1]; }); A.bAkhir.forEach((x) => { nilai[x[0]] = (nilai[x[0]] || 0) - x[1]; });
    const bn = Object.keys(nilai).map((k) => [k, jrBulat(nilai[k])]).filter((x) => x[1]); if (bn.length) E.push(jrE(sampai, '99:9', 'nilai', 'na|' + sampai, 'Penilaian akhir ' + tanggalPendek(sampai) + ': stok ke nilai Neraca, saldo minus buku pembantu ke baris khusus', bn));
    E.sort((x, y) => x.t.localeCompare(y.t) || x.j.localeCompare(y.j));
    const mut = jrNol(); let nTak = 0; const tak = []; let D = 0, K = 0;
    E.forEach((e) => { const s0 = e.b.reduce((a, x) => a + x[1], 0); if (Math.abs(s0) >= 0.01) { nTak += 1; if (tak.length < 10) tak.push(e.ket + ' (' + RP(s0) + ')'); } e.b.forEach((x) => { mut[x[0]] = (mut[x[0]] || 0) + x[1]; if (x[1] > 0) D += x[1]; else K -= x[1]; }); });
    const tidakMenutup = JR_AKUN.filter((a) => Math.abs(jrBulat(A.saldo[a.id] + (mut[a.id] || 0) - Z.saldo[a.id])) >= 0.01).map((a) => a.nama + ': awal ' + RP(A.saldo[a.id]) + ' + mutasi ' + RP(mut[a.id] || 0) + ' ≠ akhir ' + RP(Z.saldo[a.id]));
    const baris = JR_AKUN.map((a) => { let d = 0, k = 0; E.forEach((e) => e.b.forEach((x) => { if (x[0] !== a.id) return; if (x[1] > 0) d += x[1]; else k -= x[1]; })); return { akun: a.id, nama: a.nama, kel: a.kel, sifat: a.sifat, normal: a.normal, awal: A.saldo[a.id], debit: jrBulat(d), kredit: jrBulat(k), akhir: Z.saldo[a.id] }; });
    return { dari, sampai, awal: A, akhir: Z, entri: E, baris, debit: jrBulat(D), kredit: jrBulat(K), seimbang: nTak === 0 && Math.abs(D - K) < 0.01, tidakSeimbang: tak, nTidakSeimbang: nTak, menutup: !tidakMenutup.length, tidakMenutup,
      awalNol: Math.abs(JR_AKUN.reduce((x, a) => x + A.saldo[a.id], 0)) < 0.01, akhirNol: Math.abs(JR_AKUN.reduce((x, a) => x + Z.saldo[a.id], 0)) < 0.01 };
  });
}
/** Laba rentang dari jurnal vs laba Laporan (ugLabaBersih) — beda hanya boleh koreksi owner pada akun laba (disebut). */
export function jrLaba(dari, sampai) {
  const J = jrPeriode(dari, sampai); if (J.tolak) return { tolak: J.tolak };
  const rinci = JR_AKUN.filter((a) => a.kel === 'laba').map((a) => ({ akun: a.id, nama: a.nama, n: -J.baris.find((x) => x.akun === a.id).debit + J.baris.find((x) => x.akun === a.id).kredit }));
  const laba = jrBulat(rinci.reduce((x, r) => x + r.n, 0)); const L = ugLabaBersih(dari, sampai); const koreksi = (rinci.find((r) => r.akun === 'labaKoreksi') || { n: 0 }).n;
  return { dari, sampai, laba, laporan: L.labaBersih, koreksi, beda: jrBulat(laba - L.labaBersih - koreksi), cocok: Math.abs(laba - L.labaBersih - koreksi) < 0.5, rinci };
}

// ==================== cocokkan ke Laporan (Neraca & uang per tempat) ====================
const jrKredit = (S, id) => -(S[id] || 0);
/**
 * Neraca jurnal per tanggal s vs Neraca Laporan (neracaTanggal) & saldoKantong. → baris bersama (jurnal = laporan), baris khusus jurnal, penyesuaian modal, dan
 * pecahan beda "belum terjelaskan buku": selisihBuku = kewajiban khusus − harta khusus + (modal jurnal − modal) + (laba kumulatif jurnal − mesin) − (ambil pribadi
 * jurnal − mesin) + Σ penyesuaian. `cocok` = semua baris bersama sama sampai rupiah & pecahan menutup.
 */
export function jrCocok(s, kini) {
  const tolak = jrTolakArsip(s, s); if (tolak) return { s, tolak };
  const Z = jrSaldo(s); const S = Z.saldo; const key = s.slice(0, 7); const NP = neracaTanggal(s, kini, lpFinal(key) && s === akhirBulanIso(key)); const N = NP.N || {};
  const P = Z.patokan; const T = ambilTitikKas(); const SK = P ? (T && P.tanggal === T.tanggal && /patokan kas/.test(P.sumber) ? saldoKantong(s) : saldoKantong(s, P)) : null;
  const uang = JR_UANG.map((k) => ({ id: k, nama: jrAkun(k).nama, jurnal: S[k], mesin: SK && SK.ada ? SK[k] : null, cocok: !!(SK && SK.ada) && Math.abs(S[k] - SK[k]) < 0.5 }));
  const kasJ = JR_UANG.reduce((a, k) => a + S[k], 0); const PP = Number(N.piutangPemasok) > 0 ? N.piutangPemasok : 0;
  const bersama = [['Uang (laci · brankas · rekening · amplop)', kasJ, N.kas], ['Persediaan (stok)', S.persediaan, N.stok], ['Piutang pelanggan', S.piutang, N.piutang], ['Kasbon pegawai & owner', S.kasbon, N.kasbon],
    ['Piutang ke pemasok', S.piutangPemasok, PP], ['Aset tetap (nilai buku)', S.asetTetap + S.susutTerkumpul, NP.asetTetap], ['Utang ke pemasok', jrKredit(S, 'utangPemasok'), N.utangPemasok],
    ['Utang toko ke owner', jrKredit(S, 'utangOwner'), N.utangOwner], ['Modal owner tertanam', jrKredit(S, 'modal'), NP.modal]]
    .map((r) => ({ nama: r[0], jurnal: jrBulat(r[1]), laporan: r[2] === null || r[2] === undefined ? null : jrBulat(r[2]), cocok: r[2] !== null && r[2] !== undefined && Math.abs(r[1] - r[2]) < 0.5 }));
  const khusus = JR_AKUN.filter((a) => (a.sifat === 'khusus' || a.sifat === 'koreksi') && (a.kel === 'harta' || a.kel === 'kewajiban')).map((a) => ({ akun: a.id, nama: a.nama, kel: a.kel, n: a.kel === 'harta' ? S[a.id] : jrKredit(S, a.id) })).filter((r) => Math.abs(r.n) >= 0.5);
  const penyesuaian = JR_AKUN.filter((a) => a.kel === 'modal' && (a.sifat === 'penyesuaian' || a.sifat === 'koreksi')).map((a) => ({ akun: a.id, nama: a.nama, n: jrKredit(S, a.id) })).filter((r) => Math.abs(r.n) >= 0.5);
  const labaKumJ = jrBulat(jrLabaDari(S)); const priveJ = S.prive; const kewX = khusus.filter((r) => r.kel === 'kewajiban').reduce((a, r) => a + r.n, 0), asetX = khusus.filter((r) => r.kel === 'harta').reduce((a, r) => a + r.n, 0);
  const adj = penyesuaian.reduce((a, r) => a + r.n, 0); const ada = NP.selisihBuku !== null && NP.selisihBuku !== undefined && NP.labaKum !== null;
  // uang dihitung ulang dipecah: patokan PERTAMA (sebelumnya uang dihitung dari nol — posisi uang yang sudah ada / tidak tercatat sampai hari itu) dan sesudahnya
  const P1 = jrPatokan('0000-01-01', s)[0] || null; let uangPertama = null;
  if (P1) { let L1 = 0; jrKejadian().forEach((e) => { if (e.t > P1.tanggal) return; e.b.forEach((x) => { if (JR_UANG.indexOf(x[0]) >= 0) L1 += x[1]; }); }); uangPertama = { tanggal: P1.tanggal, sumber: P1.sumber, n: jrBulat(JR_UANG.reduce((x, k) => x + jrN(P1[k]), 0) - L1) }; }
  const penjelas = []; penyesuaian.forEach((r) => { if (r.akun === 'kasDihitung' && uangPertama) { penjelas.push(['Uang saat patokan pertama ' + tanggalPendek(uangPertama.tanggal) + ' (' + uangPertama.sumber + ') dibanding catatan sejak mulai — posisi uang awal & yang tidak tercatat sebelumnya', uangPertama.n], ['Uang dihitung ulang sesudah ' + tanggalPendek(uangPertama.tanggal) + ' (selisih patokan, catatan sesudah tutup)', r.n - uangPertama.n]); } else penjelas.push([r.nama, r.n]); });
  const pecahan = ada ? [['Baris khusus jurnal: kewajiban', kewX], ['Baris khusus jurnal: harta (dikurangkan)', -asetX], ['Modal jurnal − modal Laporan', jrKredit(S, 'modal') - NP.modal], [eraBuku() === null ? 'Laba & biaya bertanggal sebelum catatan pertama ' + tanggalPendek(catatanPertama()) + ' (jatah biaya bulanan, uang keluar) — ikut jurnal, tidak ikut pembanding Neraca' : 'Laba kumulatif jurnal − laba kumulatif mesin (tahun yang sudah ditutup ada di saldo pembuka)', labaKumJ - NP.labaKum],
    ['Ambil pribadi mesin − jurnal', NP.prive - priveJ]].concat(penjelas).filter((r) => Math.abs(r[1]) >= 0.5).map((r) => ({ nama: r[0], n: jrBulat(r[1]) })) : [];
  const jumlah = jrBulat(pecahan.reduce((a, r) => a + r.n, 0)); const pecahCocok = ada && Math.abs(jumlah - NP.selisihBuku) < 1;
  const bedaBuku = jrKredit(S, 'bedaBuku'); const antara = jrKredit(S, 'antara');
  return { s, kini: hariIniIso(kini), NP, uang, uangAda: Z.uangAda, uangCocok: uang.every((u) => u.cocok), bersama, bersamaCocok: bersama.filter((r) => r.laporan !== null).every((r) => r.cocok), khusus, penyesuaian, pecahan,
    pecahanJumlah: jumlah, selisihBuku: ada ? NP.selisihBuku : null, pecahCocok, labaKum: { jurnal: labaKumJ, mesin: NP.labaKum }, prive: { jurnal: priveJ, mesin: NP.prive }, bedaBuku: jrBulat(bedaBuku), antara: jrBulat(antara),
    akhir: Z.akhir, uangPertama, seimbang: Math.abs(JR_AKUN.reduce((a, x) => a + S[x.id], 0)) < 0.01, cocok: uang.every((u) => u.cocok) && bersama.filter((r) => r.laporan !== null).every((r) => r.cocok) && (!ada || pecahCocok) };
}

// ==================== entri koreksi owner (aturanToko/jurnalKoreksi) ====================
export const JR_KOREKSI_ID = 'jurnalKoreksi';
export const JR_KOREKSI_MAKS = 300;
export const JR_AKUN_KOREKSI = JR_AKUN.filter((a) => a.kel === 'laba' || a.sifat === 'koreksi').map((a) => a.id);
const jrBaruBaris = (r) => { const d = Math.round(jrN(r && r.d)), k = Math.round(jrN(r && r.k)); return { akun: String((r && r.akun) || ''), d: d > 0 ? d : 0, k: k > 0 ? k : 0 }; };
/** Entri koreksi owner: [{ id, tanggal, ket, baris: [{ akun, d, k, n = d − k }] }] — yang cacat (akun tak dikenal / tidak seimbang) dilewati & dihitung. */
export function jrKoreksi() {
  return ingatPerVersi('jrKoreksi', () => { const d = cacheMentah('aturan').find((x) => x && String(x.id) === JR_KOREKSI_ID) || null; const mentah = d && Array.isArray(d.entri) ? d.entri : [];
    const entri = mentah.map((x) => ({ id: String(x.id || ''), tanggal: String(x.tanggal || ''), ket: String(x.ket || '').slice(0, 120), oleh: String(x.oleh || ''), dicatat: String(x.dicatat || ''), baris: (Array.isArray(x.baris) ? x.baris : []).map(jrBaruBaris).map((r) => Object.assign(r, { n: r.d - r.k })) }))
      .filter((x) => x.id && jrIso(x.tanggal) && x.baris.length >= 2 && x.baris.every((r) => JR_AKUN_KOREKSI.indexOf(r.akun) >= 0 && (r.d > 0) !== (r.k > 0)) && x.baris.reduce((a, r) => a + r.n, 0) === 0);
    return { entri: entri.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.id.localeCompare(b.id)), dok: d, nBuang: mentah.length - entri.length }; });
}
const jrTerkunci = (t) => { const era = eraBuku(); if (era !== null && Number(String(t).slice(0, 4)) <= era) return true; const s = kunciSampai(); return !!s && String(t).slice(0, 7) <= s; };
/** Simpan satu entri koreksi (draf.id = ubah). draf: { id?, tanggal, ket, baris: [{ akun, d, k }] } (isian teks). */
export function susunKoreksi(draf, w, kini) {
  const D = draf || {}; const hari = hariIniIso(kini || new Date()); const t = String(D.tanggal || '');
  if (!jrIso(t) || t > hari) return { tolak: 'Tanggal koreksi belum benar (tidak boleh sesudah hari ini)' };
  if (jrTerkunci(t)) return { tolak: 'Bulan ' + lpNamaBulan(t.slice(0, 7)) + ' sudah dikunci / ditutup buku — tulis koreksinya bertanggal bulan yang masih terbuka' };
  const ket = String(D.ket || '').trim(); if (ket.length < 3) return { tolak: 'Tulis alasan koreksinya (mis. "upah lembur Okt yang lupa dicatat")' };
  const baris = (Array.isArray(D.baris) ? D.baris : []).map((r) => ({ akun: String((r && r.akun) || ''), d: ugKosong(r && r.d) ? 0 : ugAngka(r.d), k: ugKosong(r && r.k) ? 0 : ugAngka(r.k) })).filter((r) => r.akun || r.d || r.k);
  if (baris.length < 2) return { tolak: 'Koreksi butuh paling sedikit dua baris (satu sisi debit, satu sisi kredit)' };
  for (const r of baris) { if (JR_AKUN_KOREKSI.indexOf(r.akun) < 0) return { tolak: 'Akun "' + ((jrAkun(r.akun) || {}).nama || r.akun || '(kosong)') + '" tidak bisa dikoreksi — uang, stok, bon, utang & modal dicatat lewat layarnya sendiri' };
    if ([r.d, r.k].some((n) => !isFinite(n) || n < 0 || Math.round(n) !== n) || (r.d > 0) === (r.k > 0)) return { tolak: 'Tiap baris isi SATU sisi saja (debit atau kredit), rupiah bulat' }; }
  const sd = baris.reduce((a, r) => a + r.d, 0), sk = baris.reduce((a, r) => a + r.k, 0); if (sd !== sk) return { tolak: 'Belum seimbang: debit ' + RP(sd) + ' ≠ kredit ' + RP(sk) };
  const K = jrKoreksi(); const lama = D.id ? K.entri.find((x) => x.id === String(D.id)) : null; if (D.id && !lama) return { tolak: 'Entri koreksi itu sudah tidak ada' };
  if (lama && jrTerkunci(lama.tanggal)) return { tolak: 'Entri lama bertanggal bulan yang sudah dikunci — tidak bisa diubah' };
  if (!lama && K.entri.length >= JR_KOREKSI_MAKS) return { tolak: 'Sudah ' + JR_KOREKSI_MAKS + ' entri koreksi — minta konsultan merangkumnya' };
  const e = { id: lama ? lama.id : 'jk-' + w.idUnik(), tanggal: t, ket, baris: baris.map((r) => ({ akun: r.akun, d: r.d, k: r.k })), oleh: 'owner', dicatat: lama ? lama.dicatat : w.tanggal };
  const entri = (K.dok && Array.isArray(K.dok.entri) ? K.dok.entri : []).filter((x) => String(x.id) !== e.id).concat([e]);
  const laba = -baris.filter((r) => jrAkun(r.akun).kel === 'laba').reduce((a, r) => a + r.d - r.k, 0);
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, K.dok || {}, { id: JR_KOREKSI_ID, tanggal: w.tanggal, jam: w.jam, entri }) }],
    patch: { drafJk: null, kabar: 'Koreksi "' + ket + '" ' + (lama ? 'diubah' : 'dicatat') + ' (' + tanggalPendek(t) + ', ' + RP(sd) + ')' + (laba ? ' — laba JURNAL ' + lpNamaBulan(t.slice(0, 7)) + ' ' + (laba > 0 ? 'naik ' : 'turun ') + RP(Math.abs(laba)) + '; laba Laporan tidak berubah' : ' — tidak menyentuh laba'), kabarAwas: false } };
}
/** Hapus satu entri koreksi (ketukan kedua = yakin). */
export function susunHapusKoreksi(id, w, yakin) {
  const K = jrKoreksi(); const e = K.entri.find((x) => x.id === String(id)); if (!e) return { tolak: 'Entri koreksi itu sudah tidak ada' };
  if (jrTerkunci(e.tanggal)) return { tolak: 'Entri bertanggal bulan yang sudah dikunci — tidak bisa dihapus' };
  if (!yakin) return { perluYakin: true, tolak: 'Ketuk sekali lagi untuk menghapus koreksi "' + e.ket + '"' };
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, K.dok || {}, { id: JR_KOREKSI_ID, tanggal: w.tanggal, jam: w.jam, entri: (K.dok.entri || []).filter((x) => String(x.id) !== e.id) }) }], patch: { drafJk: null, yakinJk: null, kabar: 'Koreksi "' + e.ket + '" dihapus', kabarAwas: false } };
}

// ==================== bahan layar ====================
/** Buku besar satu akun dalam satu periode: saldo awal, baris (entri yang menyentuhnya) dengan saldo berjalan, saldo akhir. */
export function jrBukuBesar(akun, dari, sampai) {
  const J = jrPeriode(dari, sampai); if (J.tolak) return { tolak: J.tolak }; const a = jrAkun(akun) || JR_AKUN[0]; let s = J.awal.saldo[a.id]; const baris = [];
  J.entri.forEach((e) => { const n = e.b.filter((x) => x[0] === a.id).reduce((x, y) => x + y[1], 0); if (!n) return; s = jrBulat(s + n); baris.push({ t: e.t, j: e.j, k: e.k, ket: e.ket, debit: n > 0 ? n : 0, kredit: n < 0 ? -n : 0, saldo: s }); });
  return { akun: a, awal: J.awal.saldo[a.id], akhir: J.akhir.saldo[a.id], baris, cocok: Math.abs(s - J.akhir.saldo[a.id]) < 0.01 };
}
/** Satu entri untuk layar: baris debit dulu, nama akun, rupiah. */
export const jrBarisTampil = (e) => e.b.slice().sort((x, y) => y[1] - x[1]).map((x) => ({ akun: x[0], nama: (jrAkun(x[0]) || { nama: x[0] }).nama, debit: x[1] > 0 ? x[1] : 0, kredit: x[1] < 0 ? -x[1] : 0 }));
export const JR_JENIS = { jual: 'Nota', bon: 'Bon pelanggan', retur: 'Retur', kasbon: 'Kasbon', modal: 'Modal owner', beli: 'Barang masuk', pemasok: 'Bon pemasok', bulanan: 'Bayar biaya bulanan', keluar: 'Uang keluar',
  owner: 'Utang ke owner', bahan: 'Kantong & bahan', susut: 'Susut', tutup: 'Tutup hari', pindah: 'Pindah uang', aset: 'Aset tetap', koreksi: 'Koreksi owner', jatah: 'Jatah biaya bulanan', penyusutan: 'Penyusutan', patokan: 'Patokan uang', nilai: 'Penilaian akhir' };
/** Ringkasan satu bulan untuk Laporan › Jurnal (bulan berjalan: s.d. hari ini). */
export function jrBulan(key, kini) {
  const hari = hariIniIso(kini || new Date()); const dari = key + '-01'; const sampai = akhirBulanIso(key) < hari ? akhirBulanIso(key) : hari; const tolak = jrTolakArsip(dari, sampai); if (tolak) return { key, tolak };
  const J = jrPeriode(dari, sampai); const Lb = jrLaba(dari, sampai); const C = jrCocok(sampai, kini); const per = {}; J.entri.forEach((e) => { per[e.k] = (per[e.k] || 0) + 1; });
  return { key, nama: lpNamaBulan(key), dari, sampai, J, Lb, C, perJenis: Object.keys(per).map((k) => ({ k, nama: JR_JENIS[k] || k, n: per[k] })).sort((a, b) => b.n - a.n), nEntri: J.entri.length };
}
