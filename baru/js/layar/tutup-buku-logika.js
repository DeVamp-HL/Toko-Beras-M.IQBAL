// LAYAR UANG — K6 TUTUP BUKU tahunan (dikunci owner 18 Sep 2026: C · Berita Acara). Logika tanpa DOM; pembantu berawalan bk.
// Tujuh langkah BERURUT (tak bisa diloncati): periksa · cadangan sebelum · arsip · susun saldo pembuka · paraf dua orang · kunci (dua ketukan) · cadangan sesudah & selesai.
// Mode LATIHAN (bawaan: tidak ada satu pun yang ditulis) vs SUNGGUHAN (hanya bila tahunnya sudah lewat 31 Desember).
// 12 baris menyeberang — harta DAN utang — tiap baris SEBELUM vs SESUDAH; beda satu rupiah pun tahun tidak boleh dikunci.
//
// Beda dengan sistem lama (tulisSaldoPembuka + hapusDokumenTahun): dokumen tahun lama TIDAK DIHAPUS — dipindah ke koleksi arsipTahun (kolom asli utuh) dan
// bisa dikembalikan lewat "Batalkan tutup buku" (sampai berita acaranya selesai). Saldo pembuka = dokumen yang PERSIS sama dengan sistem lama (batch stokAwal,
// produksi beliJadi, bahan saldoAwal, piutang/kasbon/utang saldoAwal, amplop setor, utangOwner saldoAwal; semuanya bertanda tutupBuku + tahunDari), ditulis
// SAAT KUNCI (bukan di langkah 4) supaya tidak ada jendela di mana stok & piutang terhitung dua kali (mesin lama membaca semua dokumen). Langkah 4 menyusunnya
// dan membandingkan sebelum vs sesudah dari susunan itu; sesudah kunci dibandingkan lagi dari mesin (hidup). Titik kas ditulis ulang di 31 Des dari saldo per tempat.
import { hitungSaldoTutup, tbDaftarKoleksi, hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungPiutang, hitungKasbon, hitungUtangPemasok, hitungUtangOwner, saldoAmplop } from '../mesin/beku.js';
import { tbCutoff, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilSemuaBatch, ambilTutupHari, ambilTutupBukuAcara, ambilTitikKas, cacheMentah, kunciSampai, petaStokWadah, petaBukuWadah, dokDiCache, dokTertunda, pembukaBerlaku } from '../data/toko.js';
import { KP_BATAS_GET, kpPotong } from '../data/kunci-periode.js';
import { RP, ANGKA, KG, hariIniIso, tanggalPendek, lebihBayarDari } from '../inti/format.js';
import { NAMA_KASBON_OWNER, ugAturDok, ugKiniDari, saldoKantong, modalTertanam } from './uang-logika.js';
import { aturUpah } from './upah-logika.js';

export const LANGKAH_BUKU = [['periksa', 'Periksa dulu'], ['cadangan1', 'Cadangan sebelum mulai'], ['arsip', 'Simpan arsip'], ['saldo', 'Susun saldo pembuka'], ['paraf', 'Paraf dua orang'], ['kunci', 'Kunci tahun'], ['cadangan2', 'Cadangan sesudahnya & selesai']];
const bkTutupBuku = (x) => !!(x && x.tutupBuku);
/** Era tutup buku = tahun saldo pembuka terakhir (sama dengan ssEraTutupBuku / eraTutupBuku sistem lama). */
export function bkEra() { let t = null; ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'].forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x) && pembukaBerlaku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }
export function aturBuku() {
  const a = ugAturDok('tutupBuku') || {}; const saksi = Array.isArray(a.saksi) ? a.saksi.map((x) => String(x || '').trim()).filter(Boolean) : [];
  return { saksi: saksi.length ? saksi : aturUpah().orang.map((o) => o.nama), saksiTerukur: !saksi.length, dariOwner: !!ugAturDok('tutupBuku') };
}
export function susunAturBuku(isi, w) {
  const saksi = (Array.isArray(isi.saksi) ? isi.saksi : []).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8); if (!saksi.length) return { tolak: 'Saksi tidak boleh kosong — tutup buku butuh dua paraf' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tutupBuku', tanggal: w.tanggal, jam: w.jam, saksi } }], patch: { aturB2: null, kabar: 'Daftar saksi disimpan — ' + saksi.join(', '), kabarAwas: false } };
}
/** Tahun yang bisa ditutup: sesudah era terakhir, mulai dari catatan pertama. Sungguhan hanya bila hari ini sudah lewat 31 Des tahun itu. */
export function tahunBuku(kini) {
  const iso = hariIniIso(kini); const era = bkEra(); let pertama = '';
  ambilPenjualanSemua().concat(ambilSemuaBatch().filter((b) => !b.stokAwal && !b.tutupBuku)).forEach((d) => { if (d.tanggal && (!pertama || d.tanggal < pertama)) pertama = d.tanggal; });
  const awal = era !== null ? era + 1 : (pertama ? Number(pertama.slice(0, 4)) : Number(iso.slice(0, 4))); const tahun = Math.min(awal, Number(iso.slice(0, 4)));
  // K1 (owner 25 Sep 2026): selama ada bulan TERKUNCI di tahun itu, tutup buku sungguhan ditolak — arsipnya memindah (menghapus) catatan bulan terkunci.
  // Dirancang ulang sebelum Januari 2027: arsip = salinan + penanda, tidak menghapus; catatan dasar disimpan 10 tahun (UU KUP Pasal 28 ayat 11).
  const sampai = kunciSampai(); const adaKunci = !!sampai && sampai >= tahun + '-01';
  const bolehSungguhan = iso > tbCutoff(tahun) && !adaKunci; const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null;
  return { tahun, era, pertama, bolehSungguhan, adaKunci, cutoff: tbCutoff(tahun), tglBuka: (tahun + 1) + '-01-01', acara,
    teks: adaKunci ? 'Tahun ' + tahun + ' punya bulan terkunci (sampai ' + sampai + ') — tutup buku sungguhan ditolak sampai dirancang ulang (arsip tidak boleh menghapus catatan). Sekarang cuma bisa LATIHAN'
      : bolehSungguhan ? 'Tahun ' + tahun + ' sudah lewat — bisa ditutup sungguhan' : 'Tahun ' + tahun + ' belum lewat 31 Desember — sekarang cuma bisa LATIHAN' };
}
/** Gerbang sebelum mulai. lokal = { antre, menunggu, offline, idPerangkat }; lewati = { g3: true } untuk yang owner nyatakan sudah beres. */
export function gerbangBuku(tahun, kini, lokal, lewati) {
  const L = lokal || {}; const V = lewati || {}; const iso = hariIniIso(kini); const cutoff = tbCutoff(tahun); const sampai = iso < cutoff ? iso : cutoff;
  const tutup = {}; ambilTutupHari().forEach((t) => { tutup[t.tanggal] = true; }); const hariJual = {}; ambilPenjualan().forEach((p) => { if (p.tanggal && p.tanggal.slice(0, 4) === String(tahun) && p.tanggal <= sampai) hariJual[p.tanggal] = true; });
  const belumTutup = Object.keys(hariJual).filter((t) => !tutup[t]).sort();
  const t = kini.getTime(); const lain = cacheMentah('perangkat').filter((d) => String(d.id) !== String(L.idPerangkat || '') && d.pada && t - new Date(d.pada).getTime() < 15 * 60000).map((d) => d.nama || d.id);
  const karcis = ambilPenjualan().filter((p) => p.tanggal && p.tanggal.slice(0, 4) === String(tahun) && (p.jenis === 'kasir_darurat_nominal' || p.perluKoreksi)).length;   // yang masih berlaku saja — persis daftarDaruratBelumRinci & daftarPerluRapikan
  const nAntre = (L.antre || []).length + (Number(L.menunggu) || 0);
  const g = [
    { id: 'g1', teks: 'Semua hari berjualan tahun ' + tahun + ' sudah ditutup', ok: belumTutup.length === 0, ket: belumTutup.length ? belumTutup.length + ' hari belum ditutup: ' + belumTutup.slice(0, 3).map(tanggalPendek).join(', ') + (belumTutup.length > 3 ? ' …' : '') : 'semua hari berjualan punya penutupan', aksi: belumTutup.length ? 'Tutup hari-hari itu dulu (Tutup hari)' : '', bisaLewati: false },
    { id: 'g2', teks: 'Tidak ada catatan yang menunggu terkirim', ok: nAntre === 0, ket: nAntre ? nAntre + ' catatan perangkat ini belum diakui server' : 'semua sudah sampai', aksi: nAntre ? 'Tunggu sinyal sampai antrean kosong' : '', bisaLewati: false },
    { id: 'g3', teks: 'Perangkat lain sudah berhenti dipakai', ok: lain.length === 0 || !!V.g3, ket: lain.length ? (V.g3 ? 'owner menyatakan sudah dimatikan (' + lain.join(', ') + ')' : lain.join(', ') + ' masih berdenyut 15 menit terakhir') : 'tidak ada perangkat lain yang berdenyut', aksi: lain.length && !V.g3 ? 'Sudah dimatikan' : '', bisaLewati: true },
    { id: 'g4', teks: 'Tidak ada karcis kasir yang belum dirinci / dirapikan', ok: karcis === 0, ket: karcis ? karcis + ' nota menunggu dirinci atau dirapikan' : 'tidak ada', aksi: karcis ? 'Rinci di Jual → Karcis' : '', bisaLewati: false },
    { id: 'g5', teks: 'Internet tersambung', ok: !L.offline, ket: L.offline ? 'tanpa internet — ritual ini langsung ke server' : 'tersambung', aksi: '', bisaLewati: false },
  ];
  return { daftar: g, semuaOk: g.every((x) => x.ok), belum: g.filter((x) => !x.ok).length, belumTutup };
}
/** 12 baris yang menyeberang, dihitung mesin pada tanggal `sampai`; kas per tempat dari saldoKantong(sampaiKas). Rupiah stok dibulatkan PER MEREK (sama dengan yang ditulis di saldo pembuka). */
export function barisBuku(sampai, sampaiKas, titikPakai) {
  const stokK = hitungStokKarungPerMerk(sampai); let kg = 0, rpK = 0, nK = 0; Object.keys(stokK).forEach((m) => { const s = stokK[m]; if (Math.abs(s.sisaKg) < 0.01) return; nK += 1; kg += s.sisaKg; rpK += Math.round(s.sisaKg * (s.hppTerakhirPerKg || 0)); });
  const stokM = hitungStokKemasan(sampai); let unit = 0, rpM = 0; Object.keys(stokM).forEach((k) => { const s = stokM[k]; if (!(s.sisaUnit > 0)) return; unit += s.sisaUnit; rpM += s.sisaUnit * (s.hppRataRataPerUnit || 0); });
  const bk = hitungStokBahanKemasan(sampai), bl = hitungStokBahanLiteran(sampai); let pcs = 0, rpB = 0; Object.keys(bk).forEach((j) => { if (bk[j].sisaPcs > 0) { pcs += bk[j].sisaPcs; rpB += Math.round(bk[j].sisaPcs * (bk[j].hppPerPcs || 0)); } }); Object.keys(bl).forEach((j) => { if (bl[j].sisaPcs > 0) { pcs += bl[j].sisaPcs; rpB += Math.round(bl[j].sisaPcs * (bl[j].hargaPerPcs || 0)); } });
  const semuaPiutang = hitungPiutang(sampai); const piutang = semuaPiutang.filter((x) => x.sisa > 0); const kasbon = hitungKasbon(sampai).filter((x) => x.sisa > 0); const kO = kunciPelanggan(NAMA_KASBON_OWNER);
  // no. 4: saldo pembuka mesin (hitungSaldoTutup) hanya membawa piutang sisa > 0 dan dokumen pembayarannya diarsipkan → kelebihan bayar pelanggan lenyap dari buku
  // saat tahun dikunci (uangnya tetap di kas). Mesin tidak diubah; di sini hanya BERBUNYI. Menahan tutup buku karenanya = keputusan owner.
  const lebih = lebihBayarDari(semuaPiutang); const kataLebih = !lebih.n ? '' : (lebih.hapus.n ? 'Sisa bon di bawah nol ' : 'Kelebihan bayar pelanggan ') + RP(lebih.jumlah) + ' ('
    + lebih.orang.map((x) => x.nama + ' ' + RP(x.lebih) + (x.hapus > 0.5 ? (x.uang > 0.5 ? ', sebagian hapus buku yang ternyata dibayar' : ', hapus buku yang ternyata dibayar') : '')).join('; ')
    + ') TIDAK ikut menyeberang: saldo pembuka hanya membawa bon yang bersisa dan catatan pembayarannya diarsipkan, jadi sesudah tahun dikunci jejaknya hilang dari buku'
    + (lebih.uang.n ? ' — uangnya tetap di kas.' : '.') + (lebih.hapus.n ? ' Hapus buku yang ternyata dibayar perlu dibalik sebelum tahun dikunci.' : '');
  const kasbonK = kasbon.filter((x) => x.kunci !== kO).reduce((a, x) => a + x.sisa, 0); const kasbonO = kasbon.filter((x) => x.kunci === kO).reduce((a, x) => a + x.sisa, 0);
  const K = saldoKantong(sampaiKas || sampai, titikPakai); const amplop = saldoAmplop(sampai); const up = hitungUtangPemasok(sampai); const utangP = up.reduce((a, x) => a + x.totalUtang, 0), nBon = up.reduce((a, x) => a + x.bon.length, 0); const uo = hitungUtangOwner(sampai);
  const kas = (k) => (K.ada ? Math.round(K[k]) : null);
  const harta = [{ id: 'beras', nama: 'Stok beras · ' + KG(Math.round(kg * 10) / 10) + ' · ' + nK + ' merek', n: rpK }, { id: 'kemasan', nama: 'Kemasan jadi · ' + ANGKA(unit) + ' kantong', n: Math.round(rpM) }, { id: 'bahan', nama: 'Kantong kosong & paper bag · ' + ANGKA(pcs) + ' lembar', n: rpB },
    { id: 'piutang', nama: 'Piutang pelanggan · ' + piutang.length + ' orang', n: piutang.reduce((a, x) => a + x.sisa, 0) }, { id: 'kasbonK', nama: 'Kasbon karyawan', n: kasbonK }, { id: 'kasbonO', nama: 'Kasbon owner', n: kasbonO },
    // amplop = UANG di amplop (titik kas + sisihan), bukan Σ dokumen amplopLaba (saldoAmplop): kasPada menghitung titik.amplop, dan dokumen pembuka amplop (sistem lama) tetap ditulis dari saldoAmplop
    { id: 'laci', nama: 'Uang di laci', n: kas('laci') }, { id: 'brankas', nama: 'Uang di brankas', n: kas('brankas') }, { id: 'rekening', nama: 'Uang di rekening', n: kas('rekening') }, { id: 'amplop', nama: 'Amplop laba (uang)', n: kas('amplop') }];
  const utang = [{ id: 'utangP', nama: 'Utang ke pemasok · ' + nBon + ' bon', n: Math.round(utangP) }, { id: 'utangO', nama: 'Toko berutang ke owner', n: Math.round(uo.sisa) }];
  // 39b no. 12: uang per tempat yang TIDAK BISA dihitung (titik kas terakhir lebih muda dari tanggal ini — mesin tidak menghitung mundur) bukan nol: jumlah harta
  // & laba yang tinggal ikut "belum bisa dihitung" (dulu dijumlah nol → berita acara menulis harta kurang seukuran kas)
  const hartaJml = K.ada ? harta.reduce((a, h) => a + (h.n || 0), 0) : null, utangJml = utang.reduce((a, u) => a + (u.n || 0), 0); const modal = modalTertanam(sampai);
  const labaTinggal = hartaJml === null ? null : hartaJml - utangJml - modal; const tk = ambilTitikKas();
  return { harta, utang, hartaJml, utangJml, modal, labaTinggal, kasAda: K.ada, K, amplopDok: Math.round(amplop), n: harta.length + utang.length, lebih, kataLebih,
    neracaTeks: K.ada ? 'Harta ' + RP(hartaJml) + ' = utang ' + RP(utangJml) + ' + modal owner ' + RP(modal) + ' + laba yang tinggal di toko ' + RP(labaTinggal)
      : 'Harta belum bisa dijumlah: uang di laci, brankas, rekening, dan amplop pada ' + tanggalPendek(sampaiKas || sampai) + ' tidak bisa dihitung' + (tk && tk.tanggal ? ' — titik kas terakhir ' + tanggalPendek(tk.tanggal) + ' lebih muda dari tanggal itu (mesin tidak menghitung mundur)' : ' — titik kas belum disetel') + '. Stok, piutang, dan utang sudah terhitung.' };
}
/**
 * (d) TITIK KAS TAHUN: patokan uang per tempat untuk 31 Des. Titik kas sekarang bila belum melewati 31 Des; kalau tutup hari Januari sudah memajukannya,
 * hitungan tutup hari TERAKHIR ≤ 31 Des (kolom `titik` di dokumen tutupHari — isi tempat uang sesudah tutup malam itu). null = tidak ada patokan.
 */
export function titikTahun(tahun) {
  const c = tbCutoff(tahun); const t = ambilTitikKas();
  if (t && t.tanggal && t.tanggal <= c) return { tanggal: t.tanggal, laci: Number(t.laci) || 0, rekening: Number(t.rekening) || 0, amplop: Number(t.amplop) || 0, brankas: Number(t.brankas) || 0, dari: 'titikKas' };
  const th = ambilTutupHari().filter((d) => d && d.tanggal && d.tanggal <= c && d.titik).sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)))[0];
  return th ? { tanggal: th.tanggal, laci: Number(th.titik.laci) || 0, rekening: Number(th.titik.rekening) || 0, amplop: Number(th.titik.amplop) || 0, brankas: Number(th.titik.brankas) || 0, dari: 'tutupHari' } : null;
}
/** 12 baris pada 31 Des tahun itu dengan titik kas tahun (layar K6, berita acara, susunKunci). */
export function barisTahun(tahun) { const c = tbCutoff(tahun); return barisBuku(c, c, titikTahun(tahun)); }
/** Dokumen saldo pembuka = persis tulisSaldoPembuka index.html (id dari w.idUnik). */
export function pembukaBuku(tahun, w) {
  const saldo = hitungSaldoTutup(tahun); const tglBuka = (tahun + 1) + '-01-01'; const d = []; const tb = { tutupBuku: true, tahunDari: tahun };
  const merkList = []; saldo.karung.forEach((x) => { const beratUtama = x.punya25 && !x.punya50 ? 25 : 50; merkList.push({ merk: x.merk, satuan: 'karung', beratKarung: beratUtama, jumlahKarung: Math.floor(x.sisaKg / beratUtama), totalKg: x.sisaKg, hargaPerKg: x.hppPerKg, subtotalHarga: Math.round(x.sisaKg * x.hppPerKg) });
    const beratLain = beratUtama === 50 ? 25 : 50; if ((beratLain === 25 && x.punya25) || (beratLain === 50 && x.punya50)) merkList.push({ merk: x.merk, satuan: 'karung', beratKarung: beratLain, jumlahKarung: 0, totalKg: 0, hargaPerKg: x.hppPerKg, subtotalHarga: 0 }); });
  // putaran 28: buku STOK WADAH tetap dikenali sesudah tutup buku — barisnya membawa tanda stokWadah; yang sisanya nol ikut lahir lagi (baris 0 kg), karena
  // mesin beku hanya memotong penjualan dari nama yang lahir lewat batch (tanpa wadah berstok sendiri = dokumen persis index.html)
  // putaran 39: karung belakang membawa tandanya sendiri (karungBelakang + merkAsal) supaya sesudah tutup buku tetap dikenali buku karung belakang, bukan karung wadah
  const pw = petaStokWadah(); const bw = petaBukuWadah(); merkList.forEach((r) => { if (pw[r.merk]) r.stokWadah = pw[r.merk]; else if (bw[r.merk] && bw[r.merk].jenis === 'belakang') { r.karungBelakang = bw[r.merk].wadah; r.merkAsal = bw[r.merk].merk; } else if (bw[r.merk]) r.karungWadah = bw[r.merk].wadah; });
  Object.keys(pw).sort().forEach((k) => { if (!merkList.some((r) => r.merk === k)) merkList.push({ merk: k, satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, stokWadah: pw[k] }); });
  if (merkList.length) d.push({ koleksi: 'batchMasuk', data: Object.assign({ id: w.idUnik(), tanggal: tglBuka, pemasok: 'TUTUP BUKU ' + tahun, biayaBongkar: 0, stokAwal: true, merkList }, tb) });
  // hppPerUnit TIDAK dibulatkan (sistem lama membulatkan) supaya nilai kemasan sesudah = sebelum sampai rupiahnya; mesin menerima pecahan
  saldo.kemasan.forEach((x) => d.push({ koleksi: 'produksiKemasan', data: Object.assign({ id: w.idUnik(), tanggal: tglBuka, namaProduk: x.namaProduk, ukuranKemasan: x.ukuran, jumlahUnit: x.sisaUnit, hppPerUnit: x.hppPerUnit, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true, stokAwal: true }, tb) }));
  saldo.bahanK.forEach((x) => d.push({ koleksi: 'stokBahanKemasan', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', jenis: x.jenis, jumlah: x.sisaPcs, hargaTotal: Math.round(x.sisaPcs * x.hargaRata), tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun }, tb) }));
  saldo.bahanL.forEach((x) => d.push({ koleksi: 'stokBahanLiteran', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', jenis: x.jenis, jumlah: x.sisaPcs, hargaTotal: Math.round(x.sisaPcs * x.hargaRata), tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun }, tb) }));
  saldo.piutang.forEach((x) => d.push({ koleksi: 'piutangMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', namaPelanggan: x.nama, nominal: x.sisa, tanggal: x.tanggalTertua, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — tanggal mengikuti utang tertuanya supaya umurnya jujur' }, tb) }));
  saldo.kasbon.forEach((x) => d.push({ koleksi: 'kasbonMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', namaPegawai: x.nama, nominal: x.sisa, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun }, kunciPelanggan(x.nama) === kunciPelanggan(NAMA_KASBON_OWNER) ? { owner: true } : {}, tb) }));
  saldo.utangPemasok.forEach((px) => px.bon.forEach((b) => d.push({ koleksi: 'utangPemasokMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', pemasok: px.pemasok, nominal: b.sisa, bonTanggal: b.bonTanggal, tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun + (b.catatan ? ' — ' + b.catatan : '') }, tb) })));
  if (saldo.amplop > 0) d.push({ koleksi: 'amplopLaba', data: Object.assign({ id: w.idUnik(), tipe: 'setor', nominal: saldo.amplop, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — isi amplop laba yang menyeberang tahun' }, tb) });
  if (saldo.utangOwner > 0) d.push({ koleksi: 'utangOwnerMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', nominal: saldo.utangOwner, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — belanja toko yang dibayar dompet owner dan belum dilunasi' }, tb) });
  return { dokumen: d, saldo, tglBuka };
}
/** "Sesudah" dari susunan pembuka (belum ditulis): tiap baris dijumlah dari dokumennya; kas per tempat = titik yang akan ditulis. */
export function sesudahDariPembuka(P, sebelum) {
  const j = { beras: 0, kemasan: 0, bahan: 0, piutang: 0, kasbonK: 0, kasbonO: 0, amplop: 0, utangP: 0, utangO: 0 }; const kO = kunciPelanggan(NAMA_KASBON_OWNER);
  P.dokumen.forEach(({ koleksi, data }) => { if (koleksi === 'batchMasuk') (data.merkList || []).forEach((m) => { j.beras += Number(m.subtotalHarga) || 0; }); else if (koleksi === 'produksiKemasan') j.kemasan += (Number(data.jumlahUnit) || 0) * (Number(data.hppPerUnit) || 0);
    else if (koleksi === 'stokBahanKemasan' || koleksi === 'stokBahanLiteran') j.bahan += Number(data.hargaTotal) || 0; else if (koleksi === 'piutangMutasi') j.piutang += Number(data.nominal) || 0; else if (koleksi === 'kasbonMutasi') { if (kunciPelanggan(data.namaPegawai) === kO) j.kasbonO += Number(data.nominal) || 0; else j.kasbonK += Number(data.nominal) || 0; }
    else if (koleksi === 'amplopLaba') j.amplop += Number(data.nominal) || 0; else if (koleksi === 'utangPemasokMutasi') j.utangP += Number(data.nominal) || 0; else if (koleksi === 'utangOwnerMutasi') j.utangO += Number(data.nominal) || 0; });
  j.kemasan = Math.round(j.kemasan); j.amplopDok = j.amplop; ['laci', 'brankas', 'rekening', 'amplop'].forEach((k) => { j[k] = sebelum.kasAda ? Math.round(sebelum.K[k]) : null; });   // uang per tempat dibawa titik kas 31 Des, bukan dokumen
  return j;
}
/** Bandingkan sebelum vs sesudah baris demi baris; sama = tidak ada beda satu rupiah pun (kas yang tidak bisa dihitung dibandingkan null = null). */
export function bandingBuku(sebelum, sesudah) {
  // 39b no. 12: baris yang tidak bisa dihitung (uang per tempat, titik kas lebih muda dari 31 Des) BUKAN "sama" — dulu null = null lolos sebagai ✓
  const baris = sebelum.harta.concat(sebelum.utang).map((b) => { const s = sesudah ? (sesudah[b.id] === undefined ? null : sesudah[b.id]) : null; const ada = !!sesudah; const tahu = b.n !== null;
    const sama = !ada || (tahu && s !== null && Math.abs(b.n - s) < 0.5);
    return { id: b.id, nama: b.nama, a: b.n, b: ada ? s : null, ada, sama, tahu, tanda: !ada ? '' : !tahu ? '?' : sama ? '✓' : '≠' }; });
  const beda = baris.filter((b) => !b.sama); const tidakTahu = baris.filter((b) => !b.tahu);
  return { baris, semuaSama: !beda.length && !tidakTahu.length, beda: beda.concat(tidakTahu.filter((b) => b.sama)), tidakTahu, ringkas: tidakTahu.length ? tidakTahu.length + ' baris uang BELUM BISA DIHITUNG pada 31 Des (' + tidakTahu.map((b) => b.nama).join(', ') + ') — tahun tidak boleh dikunci; titik kas terakhir lebih muda dari 31 Des'
    : !sesudah ? baris.length + ' baris akan menyeberang — harta DAN utang' : beda.length ? 'ADA ' + beda.length + ' BARIS YANG TIDAK SAMA — tahun tidak boleh dikunci' : 'Semua ' + baris.length + ' baris sama persis di kedua sisi' };
}
/**
 * Pemeriksaan ulang dari MESIN sesudah kunci & arsip: 12 baris pada HARI tutup buku dimulai (disimpan di berita acara) harus sama dengan sebelum apa pun dikirim.
 * Dulu dievaluasi pada 1 Jan dan dibandingkan dengan 31 Des — penjualan 1 Jan membuat stok & laci "tidak sama" padahal benar (rancangan Okt 2026, S5).
 */
export function periksaUlangBuku(tahun) {
  const a = ambilTutupBukuAcara().find((x) => Number(x.tahun) === tahun) || null; const H = a && a.hariIni; if (!H || !Array.isArray(H.baris)) return null;
  const B = barisBuku(H.tanggal, H.tanggal); const o = {}; B.harta.concat(B.utang).forEach((b) => { o[b.id] = b.n; });
  return bandingBuku({ harta: H.baris, utang: [] }, o);
}
/** Yang diarsipkan saat kunci: seluruh dokumen tahun itu menurut tbDaftarKoleksi (sama dengan yang dihapus sistem lama). */
export function arsipBuku(tahun) { const d = tbDaftarKoleksi(tahun); const daftar = []; d.forEach((k) => k.dok.forEach((dok) => daftar.push({ koleksi: k.koleksi, id: k.koleksi === 'biayaBulanan' ? (dok.bulan || dok.id) : dok.id, data: dok }))); return { daftar, perKoleksi: d.map((k) => ({ koleksi: k.koleksi, label: k.label, n: k.dok.length })).filter((k) => k.n), n: daftar.length }; }
/** Berkas arsip tahun (JSON) untuk diunduh di langkah 3. */
export function berkasArsip(tahun, kini) { const A = arsipBuku(tahun); const isi = { versi: 5, arsipTahun: tahun, diunduhPada: kini.toISOString(), sumber: 'sistem baru · arsip tutup buku' }; A.perKoleksi.forEach((k) => { isi[k.koleksi] = A.daftar.filter((x) => x.koleksi === k.koleksi).map((x) => x.data); }); return { isi, n: A.n, nama: 'arsip-tahun-' + tahun + '-miqbal.json', perKoleksi: A.perKoleksi }; }
/**
 * Susun KUNCI (sungguhan) — BERTAHAP (rancangan Okt 2026; owner 1 Okt: batas 18 pemeriksaan per kiriman tetap). D = { paraf: {owner, saksi}, saksi, cadangan1, arsipNama, langkah }.
 * Ditolak bila baris tidak sama, paraf belum lengkap, tahunnya belum lewat, atau ada tutup buku / pembatalan yang belum selesai.
 * Hasil: kiriman[] — tiap kiriman ≤ KP_BATAS_GET pemeriksaan kunci di server (dihitung kpPotong dengan aturan yang sama dengan penjaga pusat):
 *   kiriman 1      = berita acara 'berjalan' (rencana lengkap + dokumen pembuka; tanpa pemeriksaan) + potongan pembuka pertama
 *   kiriman 2..N   = potongan pembuka berikutnya
 *   kiriman N      = + PENANDA: titik kas 31 Des (bila patokannya belum maju) · pengaturan/tutupBuku · berita acara 'terkunci'
 * Selama 'berjalan' saldo pembuka yang sudah masuk TIDAK terlihat mesin & era (toko.js pembukaBerlaku) → tahun lama utuh; penanda membalik semuanya sekaligus.
 * Satu kiriman saja (≤ 18) = sama dengan dulu: tanpa 'berjalan'.
 */
export function susunKunci(tahun, D, w) {
  const T = tahunBuku(ugKiniDari(w)); if (!T.bolehSungguhan) return { tolak: T.adaKunci ? T.teks : 'Tahun ' + tahun + ' belum lewat 31 Desember — hanya bisa latihan' };
  if (!D.paraf || !D.paraf.owner || !D.paraf.saksi) return { tolak: 'Paraf owner dan saksi dulu' };
  const tg = bkTertunda(tahun); if (tg) return { tolak: tg };
  const T0 = titikTahun(tahun); const sebelum = barisBuku(T.cutoff, T.cutoff, T0); const P = pembukaBuku(tahun, w); const B = bandingBuku(sebelum, sesudahDariPembuka(P, sebelum));
  if (!B.semuaSama) return { tolak: B.ringkas + ': ' + B.beda.map((b) => b.nama).join(', ') };
  const A = arsipBuku(tahun); const K = sebelum.K; const hariIni = hariIniIso(ugKiniDari(w)); const HI = barisBuku(hariIni, hariIni);
  // (d) titik kas tahun baru = hitungan 31 Des. Ditulis hanya bila patokan sekarang belum melewati 31 Des; kalau tutup hari Januari sudah memajukannya, titik itu
  // (hitungan fisik yang lebih baru) dipertahankan — gerakan ≤ 31 Des yang diarsipkan tidak menyentuhnya.
  const titik = K.ada && T0 && T0.dari === 'titikKas' ? { id: 'titikKas', tanggal: T.cutoff, laci: Math.round(K.laci), rekening: Math.round(K.rekening), amplop: Math.round(K.amplop), brankas: Math.round(K.brankas), diubahPada: w.kini } : null;
  const acara = Object.assign({}, T.acara || {}, { id: String(tahun), tahun, mode: 'sungguhan', status: 'terkunci', saksi: D.saksi || '', paraf: { owner: true, saksi: true, pada: w.kini }, langkah: Object.assign({}, D.langkah || {}, { kunci: w.kini }), cadangan1: D.cadangan1 || '', arsipNama: D.arsipNama || '', nArsip: A.n, arsipPerKoleksi: A.perKoleksi, nPembuka: P.dokumen.length,
    sebelum: B.baris.map((b) => ({ id: b.id, nama: b.nama, n: b.a })), modal: sebelum.modal, labaTinggal: sebelum.labaTinggal, tanggal: w.tanggal, jam: w.jam, titikDitulis: !!titik, titikSebelum: ambilTitikKas() || null,
    titikTahun: T0, hariIni: { tanggal: hariIni, baris: HI.harta.concat(HI.utang).map((b) => ({ id: b.id, nama: b.nama, n: b.n })) } });
  delete acara.pembuka; delete acara.penanda; delete acara.dariStatus;
  const penanda = (titik ? [{ koleksi: 'pengaturan', data: titik }] : []).concat([{ koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: tahun, padaTanggal: w.tanggal } }]);
  // §8 no. 1: semua pembuka ber-`bertahap`; PENANDA yang terbaca HP staf = batch pembuka ber-`penandaBuku` (toko.js pembukaBerlaku). Tanpa stok beras → batch
  // kosong (merkList []) khusus penanda, supaya pembuka lain tetap punya penanda.
  P.dokumen.forEach((x) => { x.data.bertahap = true; });
  let tanda = P.dokumen.find((x) => x.koleksi === 'batchMasuk');
  if (!tanda) { tanda = { koleksi: 'batchMasuk', data: { id: w.idUnik(), tanggal: P.tglBuka, pemasok: 'TUTUP BUKU ' + tahun, biayaBongkar: 0, stokAwal: true, merkList: [], tutupBuku: true, tahunDari: tahun, bertahap: true } }; P.dokumen.push(tanda); acara.nPembuka = P.dokumen.length; }
  tanda.data.penandaBuku = true;
  // (a) tiap dokumen pembuka satu kelompok (urutan pembukaBuku); batch penanda + penanda + berita acara terkunci = kelompok TERAKHIR, jadi selalu di kiriman terakhir
  const Pt = kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] })).concat([{ dokumen: [tanda].concat(penanda, [{ koleksi: 'tutupBukuAcara', data: acara }]) }]), dokDiCache, ugKiniDari(w));
  if (Pt.tolak) return { tolak: Pt.tolak };
  acara.rencana = { dibuat: w.kini, n: Pt.potongan.length, kiriman: Pt.potongan.map((p, i) => ({ ke: i + 1, get: p.get, dok: p.dokumen.map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })) })) };
  const berjalan = Object.assign({}, acara, { status: 'berjalan', pembuka: P.dokumen, penanda });
  const kiriman = bkKirimanDari(berjalan);
  return { kiriman, dokumen: [].concat.apply([], kiriman.map((k) => k.dokumen)), arsip: A.daftar, acara, sebelum, banding: B, titik, titikTahun: T0,
    patch: { kabar: 'Tahun ' + tahun + ' DIKUNCI: ' + P.dokumen.length + ' dokumen saldo pembuka ditulis dalam ' + kiriman.length + ' kiriman, ' + ANGKA(A.n) + ' dokumen tahun ' + tahun + ' dipindah ke arsip (tidak dihapus). Selesaikan dengan cadangan sesudahnya.', kabarAwas: false } };
}
const bkAcara = (tahun) => ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null;
/** (b) Kiriman dari berita acara 'berjalan' — sama persis dengan yang disusun saat mulai (id tetap), jadi bisa dilanjutkan dari perangkat mana pun. */
function bkKirimanDari(a) {
  const peta = {}; (a.pembuka || []).concat(a.penanda || []).forEach((x) => { peta[x.koleksi + '|' + String(x.data.id)] = x; });
  const kunci = Object.assign({}, a, { status: 'terkunci' }); delete kunci.pembuka; delete kunci.penanda; const n = a.rencana.kiriman.length;
  return a.rencana.kiriman.map((k, i) => {
    const dokumen = k.dok.map((d) => (d.koleksi === 'tutupBukuAcara' ? { koleksi: 'tutupBukuAcara', data: kunci } : peta[d.koleksi + '|' + d.id]));
    if (i === 0 && n > 1) dokumen.unshift({ koleksi: 'tutupBukuAcara', data: a });
    return { ke: i + 1, total: n, get: k.get, dokumen, pembuka: dokumen.filter((x) => x.data && x.data.tutupBuku).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })), penanda: k.dok.some((d) => d.koleksi === 'tutupBukuAcara') };
  });
}
/** Satu kiriman sudah masuk? Batch atomik: dokumen pembukanya ada (cache mentah — tersembunyi dari mesin tapi ada); kiriman penanda = berita acara sudah 'terkunci'. */
function bkMasuk(k, a) { if (k.pembuka.length) return k.pembuka.every((x) => !!dokDiCache(x.koleksi, x.id)); return !!a && (a.status === 'terkunci' || a.status === 'selesai'); }
/**
 * §8 no. 4: catatan tutup buku tahun itu yang masih MENUNGGU SERVER di perangkat ini (toko.js dokTertunda) — berita acara, saldo pembuka, penanda (titik kas,
 * pengaturan/tutupBuku). Selama ada, kemajuan = fase 'tunggu' (bukan "n dari N masuk" / "terkunci"), Lanjutkan & Batalkan menolak: server bisa menolaknya nanti.
 */
function bkTunda(tahun) {
  const a = bkAcara(tahun); let n = a && dokTertunda('tutupBukuAcara', String(a.id || tahun)) ? 1 : 0;
  bkPembukaTahun(tahun).forEach((x) => { if (dokTertunda(x.koleksi, x.id)) n += 1; }); ['titikKas', 'tutupBuku'].forEach((id) => { if (dokTertunda('pengaturan', id)) n += 1; });
  return n;
}
const bkKalimatTunda = (tahun, n) => 'Tutup buku ' + tahun + ': ' + n + ' catatan di perangkat ini masih menunggu server (belum diakui, belum dihitung masuk). Jangan tutup aplikasi; tunggu sinyal sampai antrean kosong (Menu › Sistem › Perangkat), baru Lanjutkan atau Batalkan.';
/** Tahun lama berubah sejak rencana dibuat? (pembuka yang sudah masuk tidak terlihat mesin → 31 Des dihitung ulang dari catatan asli dengan patokan kas yang sama) */
function bkBerubah(a) {
  const c = tbCutoff(Number(a.tahun)); const S = barisBuku(c, c, a.titikTahun || null); const lama = {}; (a.sebelum || []).forEach((b) => { lama[b.id] = b.n; });
  const beda = S.harta.concat(S.utang).filter((b) => (lama[b.id] === null || lama[b.id] === undefined) !== (b.n === null) || (b.n !== null && Math.abs(b.n - lama[b.id]) >= 0.5));
  return beda.length ? 'Catatan tahun ' + a.tahun + ' berubah sejak tutup buku dimulai (' + beda.map((b) => b.nama.split(' · ')[0]).join(', ') + ') — tidak dilanjutkan. Batalkan, lalu mulai lagi.' : '';
}
/**
 * §8 no. 2: aturan titik kas (d) dinilai saat KIRIM, bukan saat mulai — kalau titik kas sekarang sudah lewat 31 Des (tutup hari Januari sesudah tutup buku
 * dimulai), titik 31 Des yang disusun saat mulai TIDAK ditulis (hitungan fisik Januari dipertahankan) dan berita acara terkunci mencatat titikDitulis false.
 */
function bkTitikKini(k, tahun) {
  const tk = ambilTitikKas(); if (!(tk && tk.tanggal && tk.tanggal > tbCutoff(tahun))) return k;
  return Object.assign({}, k, { dokumen: k.dokumen.filter((x) => !(x.koleksi === 'pengaturan' && String(x.data.id) === 'titikKas'))
    .map((x) => (x.koleksi === 'tutupBukuAcara' && x.data.status === 'terkunci' ? { koleksi: x.koleksi, data: Object.assign({}, x.data, { titikDitulis: false }) } : x)) });
}
/**
 * (b) Lanjutkan tutup buku yang berhenti di tengah: dokumen yang BELUM ada saja, dengan id & isi yang sama dari berita acara. titik = titik kas 31 Des yang ikut (atau null).
 * §8 no. 3: sisa itu DIPECAH ULANG dengan jam SEKARANG (dulu kiriman yang disusun saat mulai dipakai apa adanya: mulai 1–3 Jan = masa tenggang, lanjut sesudah
 * tanggal 3 → kiriman tersimpan melebihi 18 pemeriksaan, ditolak selamanya). Batch penanda + penanda + berita acara terkunci tetap kelompok TERAKHIR.
 */
export function lanjutBuku(tahun) {
  const a = bkAcara(tahun); if (!a || a.status !== 'berjalan' || !a.rencana || !Array.isArray(a.pembuka)) return { tolak: 'Tidak ada tutup buku ' + tahun + ' yang sedang berjalan' };
  const nT = bkTunda(tahun); if (nT) return { tolak: bkKalimatTunda(tahun, nT) };
  const ub = bkBerubah(a); if (ub) return { tolak: ub };
  const K = bkKirimanDari(a); const sudah = K.filter((k) => bkMasuk(k, a)).length;
  // §8 no. 5: patokan pemeriksaan ulang (12 baris HARI INI, pembuka masih tersembunyi) diambil tepat sebelum kiriman pertama sesi ini — dulu saat mulai, jadi
  // penjualan di antara kiriman 1 dan Lanjutkan (hari yang sama) membuat periksa ulang berbunyi palsu
  const hari = hariIniIso(new Date(Date.now())); const HI = barisBuku(hari, hari);
  const kunci = Object.assign({}, a, { status: 'terkunci', hariIni: { tanggal: hari, baris: HI.harta.concat(HI.utang).map((b) => ({ id: b.id, nama: b.nama, n: b.n })) } }); delete kunci.pembuka; delete kunci.penanda;
  const tanda = a.pembuka.filter((x) => x.data && x.data.penandaBuku); const belumAda = a.pembuka.filter((x) => tanda.indexOf(x) < 0 && !dokDiCache(x.koleksi, x.data.id));
  const akhir = bkTitikKini({ dokumen: tanda.concat(a.penanda || [], [{ koleksi: 'tutupBukuAcara', data: kunci }]) }, tahun);
  const Pt = kpPotong(belumAda.map((x) => ({ dokumen: [x] })).concat([akhir]), dokDiCache, new Date(Date.now())); if (Pt.tolak) return { tolak: Pt.tolak };
  const belum = Pt.potongan.map((p, i) => ({ ke: sudah + i + 1, total: sudah + Pt.potongan.length, get: p.get, dokumen: p.dokumen,
    pembuka: p.dokumen.filter((x) => x.data && x.data.tutupBuku).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })), penanda: i === Pt.potongan.length - 1 }));
  const titik = akhir.dokumen.find((x) => x.koleksi === 'pengaturan' && String(x.data.id) === 'titikKas');
  return { kiriman: belum, sudah, total: sudah + belum.length, titik: titik ? titik.data : null };
}
/** Saldo pembuka tahun itu yang ada di cache (termasuk yang tersembunyi dari mesin). */
function bkPembukaTahun(tahun) { const out = []; Object.keys(KOLEKSI_CACHE).forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x) && Number(x.tahunDari) === tahun) out.push({ koleksi: KOLEKSI_CACHE[c], id: x.id }); })); return out; }
/** Mulai baru ditolak selama tutup buku / pembatalan tahun itu belum tuntas (pembuka percobaan lama yang tersisa akan ikut terlihat bersama yang baru). */
function bkTertunda(tahun) {
  const a = bkAcara(tahun); if (a && a.status === 'berjalan') return 'Tutup buku ' + tahun + ' sedang berjalan — lanjutkan atau batalkan dulu';
  if (a && a.status === 'membatalkan') return 'Pembatalan tutup buku ' + tahun + ' belum selesai — lanjutkan pembatalannya dulu';
  // pembuka tahun itu yang sudah ada (percobaan yang dibatalkan setengah, atau kiriman yang masuk tanpa berita acaranya terbaca) akan ikut terlihat bersama yang baru
  const n = bkPembukaTahun(tahun).length; if (n) return 'Sudah ada ' + n + ' saldo pembuka ' + tahun + ' dari percobaan sebelumnya — ' + (a && a.status === 'dibatalkan' ? 'lanjutkan pembatalannya dulu' : 'lanjutkan atau batalkan dulu');
  return '';
}
/** §8 no. 6: pita fase selesaikan menjalankan periksa ulang dan menyebut hasilnya. */
function bkTeksSelesaikan(tahun) {
  const kal = bkKalimatPeriksa(periksaUlangBuku(tahun));
  return 'Tahun ' + tahun + ' terkunci dan arsipnya habis. ' + (kal ? 'AWAS: ' + kal + ' — periksa dulu; "selesai" butuh ketukan kedua.' : 'Diperiksa ulang dari mesin: semua baris sama — unduh cadangan sesudahnya & selesai.');
}
/** (c) Kemajuan untuk layar K6 & Beranda: tutup buku / pembatalan yang belum tuntas (null = tidak ada). */
export function kemajuanBuku() {
  const a = ambilTutupBukuAcara().filter((x) => x && (x.status === 'berjalan' || x.status === 'membatalkan' || x.status === 'terkunci' || (x.status === 'dibatalkan' && bkPembukaTahun(Number(x.tahun)).length))).sort((p, q) => Number(q.tahun) - Number(p.tahun))[0];
  if (!a) return null; const tahun = Number(a.tahun);
  // §8 no. 4: ada kiriman yang belum diakui server di perangkat ini → bukan "n dari N masuk" / "terkunci" (berita acara di cache bisa versi yang belum diterima)
  const nT = bkTunda(tahun); if (nT) return { tahun, fase: 'tunggu', tunda: nT, teks: bkKalimatTunda(tahun, nT) };
  if (a.status === 'berjalan') { const K = bkKirimanDari(a); const sudah = K.filter((k) => bkMasuk(k, a)).length;
    return { tahun, fase: 'pembuka', sudah, total: K.length, teks: 'Tutup buku ' + tahun + ': ' + sudah + ' dari ' + K.length + ' kiriman saldo pembuka sudah masuk. Tahun ' + tahun + ' MASIH TERBUKA (saldo pembuka yang sudah masuk belum dihitung) sampai kiriman terakhir masuk — lanjutkan atau batalkan.' }; }
  if (a.status === 'terkunci') { const sisa = arsipBuku(tahun).n; const total = Number(a.nArsip) || sisa;
    return sisa ? { tahun, fase: 'arsip', sudah: total - sisa, total, sisa, teks: 'Tahun ' + tahun + ' terkunci; ' + ANGKA(sisa) + ' catatan ' + tahun + ' belum pindah ke arsip (' + Math.ceil(sisa / KP_BATAS_GET) + ' kiriman lagi). Sampai habis, stok, piutang & utang terhitung DOBEL — lanjutkan arsip atau batalkan.' }
      : { tahun, fase: 'selesaikan', sudah: total, total, sisa: 0, teks: bkTeksSelesaikan(tahun) }; }
  const sisaP = bkPembukaTahun(tahun).length;
  return { tahun, fase: 'batal', sisaPembuka: sisaP, teks: 'Pembatalan tutup buku ' + tahun + ' belum selesai: ' + sisaP + ' saldo pembuka belum ditarik' + (a.dariStatus === 'terkunci' ? ' dan arsip belum semua dikembalikan' : '') + ' — lanjutkan pembatalan.' };
}
/**
 * Batalkan tutup buku (berjalan, atau terkunci sebelum selesai): BERTAHAP juga — tarik saldo pembuka per ≤ 18 pemeriksaan, kembalikan arsip, era mundur.
 * kiriman 1 = berita acara 'membatalkan' (+ era & titik kas bila tahun sempat terkunci) + potongan tarik pertama — pembuka langsung tak terlihat mesin.
 * Sesudah semua kiriman & pengembalian arsip: `akhir` = berita acara 'dibatalkan'. Bisa diulang: yang sudah ditarik/dikembalikan tidak diulang.
 * arsipDok = hasil bacaArsipTahun (sisa yang belum dikembalikan).
 */
export function susunBatal(tahun, arsipDok, w) {
  const acara = bkAcara(tahun); const hapus = bkPembukaTahun(tahun); const nT = bkTunda(tahun); if (nT) return { tolak: bkKalimatTunda(tahun, nT) };
  if (!acara || (['terkunci', 'berjalan', 'membatalkan'].indexOf(acara.status) < 0 && !(acara.status === 'dibatalkan' && hapus.length))) return { tolak: 'Tahun ' + tahun + ' tidak sedang terkunci — tidak ada yang dibatalkan' };
  const dari = acara.status === 'membatalkan' || acara.status === 'dibatalkan' ? (acara.dariStatus || 'terkunci') : acara.status;
  const batal = Object.assign({}, acara, { status: 'membatalkan', dariStatus: dari, dibatalkanPada: acara.dibatalkanPada || w.kini, dibatalkanTanggal: acara.dibatalkanTanggal || w.tanggal }); delete batal.pembuka; delete batal.penanda;
  const awal = [{ koleksi: 'tutupBukuAcara', data: batal }]; let titik = null;
  if (acara.status === 'terkunci') {
    const eraLama = bkEraTanpa(tahun); awal.push({ koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: eraLama === null ? 0 : eraLama, padaTanggal: w.tanggal, dibatalkan: tahun } });
    // titik kas dikembalikan HANYA bila titik sekarang masih yang ditulis tutup buku ini (31 Des) — kalau tutup hari sudah memajukannya, hitungan fisik itu dipertahankan
    const tk = ambilTitikKas(); if (acara.titikDitulis && acara.titikSebelum && acara.titikSebelum.tanggal && tk && tk.tanggal === tbCutoff(tahun)) { titik = Object.assign({}, acara.titikSebelum, { id: 'titikKas', diubahPada: w.kini }); awal.push({ koleksi: 'pengaturan', data: titik }); }
  }
  // §8 no. 1: batch penanda dihapus di kiriman PERTAMA — HP staf (tanpa berita acara) langsung tidak melihat pembuka lagi, sama dengan HP owner
  const tanda = hapus.filter((x) => { const d = x.koleksi === 'batchMasuk' ? dokDiCache(x.koleksi, x.id) : null; return !!(d && d.penandaBuku); }); const sisa = hapus.filter((x) => tanda.indexOf(x) < 0);
  const P = kpPotong([{ dokumen: awal, hapus: tanda }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] }))), dokDiCache, ugKiniDari(w)); if (P.tolak) return { tolak: P.tolak };
  const kiriman = P.potongan.map((p, i) => ({ ke: i + 1, total: P.potongan.length, get: p.get, dokumen: p.dokumen, hapus: p.hapus }));
  const akhir = { koleksi: 'tutupBukuAcara', data: Object.assign({}, batal, { status: 'dibatalkan' }) };
  return { kiriman, akhir, dokumen: [].concat.apply([], kiriman.map((k) => k.dokumen)), hapus, titik, pulih: (arsipDok || []).map((a) => ({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok })),
    patch: { kabar: 'Tutup buku ' + tahun + ' dibatalkan — ' + ANGKA((arsipDok || []).length) + ' dokumen dikembalikan dari arsip, ' + hapus.length + ' saldo pembuka ditarik dalam ' + kiriman.length + ' kiriman. Tahun ' + tahun + ' terbuka lagi.', kabarAwas: false } };
}
const KOLEKSI_CACHE = { batch: 'batchMasuk', piutang: 'piutangMutasi', kasbon: 'kasbonMutasi', produksi: 'produksiKemasan', bahanKemasan: 'stokBahanKemasan', bahanLiteran: 'stokBahanLiteran', utangPemasok: 'utangPemasokMutasi', utangOwner: 'utangOwnerMutasi', amplop: 'amplopLaba' };
function bkEraTanpa(tahun) { let t = null; Object.keys(KOLEKSI_CACHE).forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x) && pembukaBerlaku(x) && Number(x.tahunDari) !== tahun) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }
/** §8 no. 6: kalimat hasil pemeriksaan ulang untuk "selesaikan" ('' = semua sama). */
function bkKalimatPeriksa(PU) {
  if (!PU) return 'Pemeriksaan ulang tidak bisa dijalankan (patokan hari tutup buku tidak ada di berita acara)';
  if (PU.semuaSama) return ''; const nm = (d) => d.map((b) => b.nama.split(' · ')[0]).join(', '); const beda = PU.baris.filter((b) => b.tahu && !b.sama);
  return 'Pemeriksaan ulang dari mesin: ' + [beda.length ? beda.length + ' baris TIDAK SAMA (' + nm(beda) + ')' : '', PU.tidakTahu.length ? PU.tidakTahu.length + ' baris belum bisa dihitung (' + nm(PU.tidakTahu) + ')' : ''].filter(Boolean).join(' · ');
}
/**
 * Selesai: cadangan sesudah tercatat → berita acara selesai (tidak bisa dibatalkan lagi).
 * §8 no. 6: hanya sesudah arsip HABIS; pemeriksaan ulang dari mesin dijalankan di sini — beda / tidak bisa diperiksa = ditolak dengan barisnya (perluYakin),
 * baru diterima pada ketukan kedua (yakin) dan hasilnya dicatat di berita acara.
 */
export function susunSelesai(tahun, namaCadangan2, w, yakin) {
  const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null; if (!acara || acara.status !== 'terkunci') return { tolak: 'Kunci tahunnya dulu' };
  const sisa = arsipBuku(tahun).n; if (sisa) return { tolak: ANGKA(sisa) + ' catatan ' + tahun + ' belum pindah ke arsip — lanjutkan arsip dulu; tahun ' + tahun + ' belum bisa diselesaikan' };
  const PU = periksaUlangBuku(tahun); const kal = bkKalimatPeriksa(PU);
  if (kal && !yakin) return { tolak: kal + '. Sesudah selesai, tutup buku ' + tahun + ' tidak bisa dibatalkan lagi — periksa dulu; kalau memang benar, ketuk sekali lagi.', perluYakin: true };
  const periksaUlang = { sama: !kal, beda: PU ? PU.beda.map((b) => b.nama) : ['tidak bisa diperiksa'], pada: w.kini };
  return { dokumen: [{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara, { status: 'selesai', cadangan2: namaCadangan2 || '', selesaiPada: w.kini, selesaiTanggal: w.tanggal, periksaUlang, langkah: Object.assign({}, acara.langkah || {}, { cadangan2: w.kini }) }) }], patch: { kabar: 'Tahun ' + tahun + ' selesai ditutup. Simpan kedua berkas cadangan di luar HP.', kabarAwas: false } };
}
/**
 * §8 no. 7: kalimat bila tutup buku / pembatalan BERHENTI di kiriman ke-`ke` — tombol yang disebut harus tombol yang benar-benar meneruskan hal itu.
 * Kiriman 1 tutup buku tidak masuk → belum ada berita acara 'berjalan', pita Lanjutkan tidak ada → "Kunci tahun" lagi. Kiriman 1 pembatalan tidak masuk → berita
 * acara masih 'berjalan' / 'terkunci', "Lanjutkan" justru meneruskan TUTUP BUKU / arsip → "Batalkan" lagi. Sesudahnya pita ada → "Lanjutkan".
 * h = hasil tulisDokumen ({ gagal, pesan } | { antre } | null). Belum diakui server (antre) → tunggu antrean kosong dulu, lalu langkah menurut pita.
 */
export function kabarBerhentiBuku(jenis, tahun, ke, total, h) {
  const sebab = h && h.pesan ? ' — ' + h.pesan : ' — server belum mengaku'; const antre = !!(h && h.antre && !h.gagal);
  const tunggu = ' Kiriman itu masih di perangkat ini, menunggu server — jangan tutup aplikasi; tunggu sampai antrean kosong. ';
  if (jenis === 'batal') {
    const awal = 'Pembatalan tutup buku ' + tahun + ' berhenti di kiriman ' + ke + ' dari ' + total + sebab + '.';
    if (antre) return awal + tunggu + (ke === 1 ? 'Sesudah itu: kalau pita menyebut "Pembatalan tutup buku ' + tahun + ' belum selesai", ketuk "Lanjutkan"; kalau tidak, ketuk "Batalkan" lagi.' : 'Sesudah itu ketuk "Lanjutkan" untuk meneruskan pembatalan.');
    return awal + (ke === 1 ? ' Belum ada yang ditarik — ketuk "Batalkan" lagi (tombol "Lanjutkan" di pita meneruskan TUTUP BUKU, bukan pembatalan).' : ' Ketuk "Lanjutkan" untuk meneruskan pembatalan — yang sudah ditarik tidak diulang.');
  }
  const awal = 'Berhenti di kiriman ' + ke + ' dari ' + total + sebab + '. Tahun ' + tahun + ' BELUM tertutup (yang sudah masuk belum dihitung).';
  if (antre) return awal + tunggu + (ke === 1 ? 'Sesudah itu: kalau pita "Tutup buku ' + tahun + ': … sudah masuk" muncul, ketuk "Lanjutkan"; kalau tidak, ketuk "Kunci tahun ' + tahun + '" lagi.' : 'Sesudah itu ketuk "Lanjutkan" — yang sudah masuk tidak dikirim ulang — atau "Batalkan".');
  return awal + (ke === 1 ? ' Tidak ada yang masuk — ketuk "Kunci tahun ' + tahun + '" lagi sesudah sebabnya dibereskan.' : ' Ketuk "Lanjutkan" — yang sudah masuk tidak dikirim ulang — atau "Batalkan".');
}
/** Teks berita acara (cetak/WA). */
export function teksAcara(tahun, D, B, sebelum, saksi, w) {
  const L = ['TOKO BERAS M.IQBAL', 'BERITA ACARA TUTUP BUKU ' + tahun, tanggalPendek(w.tanggal) + ' · ' + w.jam + (D.latihan ? ' · LATIHAN' : ''), '', 'Harta toko akhir ' + tahun + ':'];
  B.baris.forEach((b) => L.push('  ' + (b.nama + '                                    ').slice(0, 38) + (b.a === null ? 'tidak bisa dihitung' : RP(b.a)) + (b.ada ? (b.a === null ? '  ?' : b.sama ? '  ✓' : '  ≠ ' + RP(b.b)) : '')));
  const rpA = (n) => (n === null ? 'tidak bisa dihitung' : RP(n));   // 39b no. 12: bukan Rp0
  L.push('', 'Jumlah harta   ' + rpA(sebelum.hartaJml), 'Jumlah utang   ' + RP(sebelum.utangJml), 'Modal owner    ' + RP(sebelum.modal), 'Laba tinggal   ' + rpA(sebelum.labaTinggal), '');
  if (sebelum.kataLebih) L.push(sebelum.kataLebih, '');   // no. 4 B6
  L.push('Paraf: owner ' + (D.paraf && D.paraf.owner ? '✓' : '—') + ' · ' + (saksi || 'saksi') + ' ' + (D.paraf && D.paraf.saksi ? '✓' : '—'));
  return L.join('\n');
}
export { RP as bkRP };
