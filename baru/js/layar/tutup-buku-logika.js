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
import { ambilPenjualan, ambilPenjualanSemua, ambilSemuaBatch, ambilTutupHari, ambilTutupBukuAcara, ambilTitikKas, cacheMentah, kunciSampai, butuhGet } from '../data/toko.js';
import { KP_BATAS_GET } from '../data/kunci-periode.js';
import { RP, ANGKA, KG, hariIniIso, tanggalPendek } from '../inti/format.js';
import { NAMA_KASBON_OWNER, ugAturDok, ugKiniDari, saldoKantong, modalTertanam } from './uang-logika.js';
import { aturUpah } from './upah-logika.js';

export const LANGKAH_BUKU = [['periksa', 'Periksa dulu'], ['cadangan1', 'Cadangan sebelum mulai'], ['arsip', 'Simpan arsip'], ['saldo', 'Susun saldo pembuka'], ['paraf', 'Paraf dua orang'], ['kunci', 'Kunci tahun'], ['cadangan2', 'Cadangan sesudahnya & selesai']];
const bkTutupBuku = (x) => !!(x && x.tutupBuku);
/** Era tutup buku = tahun saldo pembuka terakhir (sama dengan ssEraTutupBuku / eraTutupBuku sistem lama). */
export function bkEra() { let t = null; ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'].forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }
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
export function barisBuku(sampai, sampaiKas) {
  const stokK = hitungStokKarungPerMerk(sampai); let kg = 0, rpK = 0, nK = 0; Object.keys(stokK).forEach((m) => { const s = stokK[m]; if (Math.abs(s.sisaKg) < 0.01) return; nK += 1; kg += s.sisaKg; rpK += Math.round(s.sisaKg * (s.hppTerakhirPerKg || 0)); });
  const stokM = hitungStokKemasan(sampai); let unit = 0, rpM = 0; Object.keys(stokM).forEach((k) => { const s = stokM[k]; if (!(s.sisaUnit > 0)) return; unit += s.sisaUnit; rpM += s.sisaUnit * (s.hppRataRataPerUnit || 0); });
  const bk = hitungStokBahanKemasan(sampai), bl = hitungStokBahanLiteran(sampai); let pcs = 0, rpB = 0; Object.keys(bk).forEach((j) => { if (bk[j].sisaPcs > 0) { pcs += bk[j].sisaPcs; rpB += Math.round(bk[j].sisaPcs * (bk[j].hppPerPcs || 0)); } }); Object.keys(bl).forEach((j) => { if (bl[j].sisaPcs > 0) { pcs += bl[j].sisaPcs; rpB += Math.round(bl[j].sisaPcs * (bl[j].hargaPerPcs || 0)); } });
  const piutang = hitungPiutang(sampai).filter((x) => x.sisa > 0); const kasbon = hitungKasbon(sampai).filter((x) => x.sisa > 0); const kO = kunciPelanggan(NAMA_KASBON_OWNER);
  const kasbonK = kasbon.filter((x) => x.kunci !== kO).reduce((a, x) => a + x.sisa, 0); const kasbonO = kasbon.filter((x) => x.kunci === kO).reduce((a, x) => a + x.sisa, 0);
  const K = saldoKantong(sampaiKas || sampai); const amplop = saldoAmplop(sampai); const up = hitungUtangPemasok(sampai); const utangP = up.reduce((a, x) => a + x.totalUtang, 0), nBon = up.reduce((a, x) => a + x.bon.length, 0); const uo = hitungUtangOwner(sampai);
  const kas = (k) => (K.ada ? Math.round(K[k]) : null);
  const harta = [{ id: 'beras', nama: 'Stok beras · ' + KG(Math.round(kg * 10) / 10) + ' · ' + nK + ' merek', n: rpK }, { id: 'kemasan', nama: 'Kemasan jadi · ' + ANGKA(unit) + ' kantong', n: Math.round(rpM) }, { id: 'bahan', nama: 'Kantong kosong & paper bag · ' + ANGKA(pcs) + ' lembar', n: rpB },
    { id: 'piutang', nama: 'Piutang pelanggan · ' + piutang.length + ' orang', n: piutang.reduce((a, x) => a + x.sisa, 0) }, { id: 'kasbonK', nama: 'Kasbon karyawan', n: kasbonK }, { id: 'kasbonO', nama: 'Kasbon owner', n: kasbonO },
    // amplop = UANG di amplop (titik kas + sisihan), bukan Σ dokumen amplopLaba (saldoAmplop): kasPada menghitung titik.amplop, dan dokumen pembuka amplop (sistem lama) tetap ditulis dari saldoAmplop
    { id: 'laci', nama: 'Uang di laci', n: kas('laci') }, { id: 'brankas', nama: 'Uang di brankas', n: kas('brankas') }, { id: 'rekening', nama: 'Uang di rekening', n: kas('rekening') }, { id: 'amplop', nama: 'Amplop laba (uang)', n: kas('amplop') }];
  const utang = [{ id: 'utangP', nama: 'Utang ke pemasok · ' + nBon + ' bon', n: Math.round(utangP) }, { id: 'utangO', nama: 'Toko berutang ke owner', n: Math.round(uo.sisa) }];
  const hartaJml = harta.reduce((a, h) => a + (h.n || 0), 0), utangJml = utang.reduce((a, u) => a + (u.n || 0), 0); const modal = modalTertanam(sampai);
  return { harta, utang, hartaJml, utangJml, modal, labaTinggal: hartaJml - utangJml - modal, kasAda: K.ada, K, amplopDok: Math.round(amplop), n: harta.length + utang.length, neracaTeks: 'Harta ' + RP(hartaJml) + ' = utang ' + RP(utangJml) + ' + modal owner ' + RP(modal) + ' + laba yang tinggal di toko ' + RP(hartaJml - utangJml - modal) + (K.ada ? '' : ' · uang per tempat belum bisa dihitung (titik kas)') };
}
/** Dokumen saldo pembuka = persis tulisSaldoPembuka index.html (id dari w.idUnik). */
export function pembukaBuku(tahun, w) {
  const saldo = hitungSaldoTutup(tahun); const tglBuka = (tahun + 1) + '-01-01'; const d = []; const tb = { tutupBuku: true, tahunDari: tahun };
  const merkList = []; saldo.karung.forEach((x) => { const beratUtama = x.punya25 && !x.punya50 ? 25 : 50; merkList.push({ merk: x.merk, satuan: 'karung', beratKarung: beratUtama, jumlahKarung: Math.floor(x.sisaKg / beratUtama), totalKg: x.sisaKg, hargaPerKg: x.hppPerKg, subtotalHarga: Math.round(x.sisaKg * x.hppPerKg) });
    const beratLain = beratUtama === 50 ? 25 : 50; if ((beratLain === 25 && x.punya25) || (beratLain === 50 && x.punya50)) merkList.push({ merk: x.merk, satuan: 'karung', beratKarung: beratLain, jumlahKarung: 0, totalKg: 0, hargaPerKg: x.hppPerKg, subtotalHarga: 0 }); });
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
  const baris = sebelum.harta.concat(sebelum.utang).map((b) => { const s = sesudah ? (sesudah[b.id] === undefined ? null : sesudah[b.id]) : null; const ada = !!sesudah; const sama = !ada || (b.n === null && s === null) || (b.n !== null && s !== null && Math.abs(b.n - s) < 0.5);
    return { id: b.id, nama: b.nama, a: b.n, b: ada ? s : null, ada, sama, tanda: !ada ? '' : sama ? '✓' : '≠' }; });
  const beda = baris.filter((b) => !b.sama); return { baris, semuaSama: !beda.length, beda, ringkas: !sesudah ? baris.length + ' baris akan menyeberang — harta DAN utang' : beda.length ? 'ADA ' + beda.length + ' BARIS YANG TIDAK SAMA — tahun tidak boleh dikunci' : 'Semua ' + baris.length + ' baris sama persis di kedua sisi' };
}
/** Sesudah HIDUP (dari mesin) sesudah tahun dikunci: dievaluasi pada 1 Jan tahun+1. */
export function sesudahHidup(tahun) { const B = barisBuku((tahun + 1) + '-01-01', (tahun + 1) + '-01-01'); const o = {}; B.harta.concat(B.utang).forEach((b) => { o[b.id] = b.n; }); return o; }
/** Yang diarsipkan saat kunci: seluruh dokumen tahun itu menurut tbDaftarKoleksi (sama dengan yang dihapus sistem lama). */
export function arsipBuku(tahun) { const d = tbDaftarKoleksi(tahun); const daftar = []; d.forEach((k) => k.dok.forEach((dok) => daftar.push({ koleksi: k.koleksi, id: k.koleksi === 'biayaBulanan' ? (dok.bulan || dok.id) : dok.id, data: dok }))); return { daftar, perKoleksi: d.map((k) => ({ koleksi: k.koleksi, label: k.label, n: k.dok.length })).filter((k) => k.n), n: daftar.length }; }
/** Berkas arsip tahun (JSON) untuk diunduh di langkah 3. */
export function berkasArsip(tahun, kini) { const A = arsipBuku(tahun); const isi = { versi: 5, arsipTahun: tahun, diunduhPada: kini.toISOString(), sumber: 'sistem baru · arsip tutup buku' }; A.perKoleksi.forEach((k) => { isi[k.koleksi] = A.daftar.filter((x) => x.koleksi === k.koleksi).map((x) => x.data); }); return { isi, n: A.n, nama: 'arsip-tahun-' + tahun + '-miqbal.json', perKoleksi: A.perKoleksi }; }
/**
 * Susun KUNCI (sungguhan): dokumen pembuka + titik kas 31 Des + berita acara + era, dan daftar arsip. D = { paraf: {owner, saksi}, saksi, cadangan1, arsipNama, langkah }.
 * Ditolak bila baris tidak sama, paraf belum lengkap, atau tahunnya belum lewat.
 */
export function susunKunci(tahun, D, w) {
  const T = tahunBuku(ugKiniDari(w)); if (!T.bolehSungguhan) return { tolak: T.adaKunci ? T.teks : 'Tahun ' + tahun + ' belum lewat 31 Desember — hanya bisa latihan' };
  if (!D.paraf || !D.paraf.owner || !D.paraf.saksi) return { tolak: 'Paraf owner dan saksi dulu' };
  const sebelum = barisBuku(T.cutoff, T.cutoff); const P = pembukaBuku(tahun, w); const B = bandingBuku(sebelum, sesudahDariPembuka(P, sebelum));
  if (!B.semuaSama) return { tolak: B.ringkas + ': ' + B.beda.map((b) => b.nama).join(', ') };
  const A = arsipBuku(tahun); const dokumen = P.dokumen.slice(); const K = sebelum.K;
  if (K.ada) dokumen.push({ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: T.cutoff, laci: Math.round(K.laci), rekening: Math.round(K.rekening), amplop: Math.round(K.amplop), brankas: Math.round(K.brankas), diubahPada: w.kini } });
  dokumen.push({ koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: tahun, padaTanggal: w.tanggal } });
  // putaran 25 (diukur, owner 25 Sep): pembuka piutang bertanggal utang tertuanya & bon lama pemasok bertanggal bonnya → tiap satu diperiksa kunci di server.
  // Lebih dari KP_BATAS_GET = satu kiriman pasti ditolak; ditolak di sini dengan kalimatnya, sebelum apa pun dikirim. Rancang ulang tutup buku: wajib sebelum Desember 2026.
  const g = butuhGet(dokumen, []);
  if (g > KP_BATAS_GET) return { tolak: 'Saldo pembuka menyentuh ' + g + ' catatan bertanggal lama (piutang mengikuti tanggal utang tertuanya, bon pemasok mengikuti tanggal bonnya) — server hanya sanggup memeriksa ' + KP_BATAS_GET + ' sekali kirim. Tidak ada yang dikirim. Tutup buku sungguhan menunggu rancangan baru (wajib selesai sebelum Desember 2026); latihan tetap bisa.' };
  const acara = Object.assign({}, T.acara || {}, { id: String(tahun), tahun, mode: 'sungguhan', status: 'terkunci', saksi: D.saksi || '', paraf: { owner: true, saksi: true, pada: w.kini }, langkah: Object.assign({}, D.langkah || {}, { kunci: w.kini }), cadangan1: D.cadangan1 || '', arsipNama: D.arsipNama || '', nArsip: A.n, arsipPerKoleksi: A.perKoleksi, nPembuka: P.dokumen.length,
    sebelum: B.baris.map((b) => ({ id: b.id, nama: b.nama, n: b.a })), modal: sebelum.modal, labaTinggal: sebelum.labaTinggal, tanggal: w.tanggal, jam: w.jam, titikDitulis: K.ada, titikSebelum: ambilTitikKas() || null });
  dokumen.push({ koleksi: 'tutupBukuAcara', data: acara });
  return { dokumen, arsip: A.daftar, acara, sebelum, banding: B, titik: K.ada ? { tanggal: T.cutoff, laci: Math.round(K.laci), rekening: Math.round(K.rekening), amplop: Math.round(K.amplop), brankas: Math.round(K.brankas) } : null,
    patch: { kabar: 'Tahun ' + tahun + ' DIKUNCI: ' + P.dokumen.length + ' dokumen saldo pembuka ditulis, ' + ANGKA(A.n) + ' dokumen tahun ' + tahun + ' dipindah ke arsip (tidak dihapus). Selesaikan dengan cadangan sesudahnya.', kabarAwas: false } };
}
/** Batalkan tutup buku (sesudah kunci, sebelum selesai): kembalikan arsip, cabut saldo pembuka, era mundur. arsipDok = hasil bacaArsipTahun. */
export function susunBatal(tahun, arsipDok, w) {
  const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null; if (!acara || acara.status !== 'terkunci') return { tolak: 'Tahun ' + tahun + ' tidak sedang terkunci — tidak ada yang dibatalkan' };
  const hapus = []; ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'].forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x) && Number(x.tahunDari) === tahun) hapus.push({ koleksi: KOLEKSI_CACHE[c], id: x.id }); }));
  const eraLama = bkEraTanpa(tahun);
  const dokumen = [{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara, { status: 'dibatalkan', dibatalkanPada: w.kini, dibatalkanTanggal: w.tanggal }) }, { koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: eraLama === null ? 0 : eraLama, padaTanggal: w.tanggal, dibatalkan: tahun } }];
  const titik = acara.titikSebelum && acara.titikSebelum.tanggal ? Object.assign({}, acara.titikSebelum, { id: 'titikKas', diubahPada: w.kini }) : null; if (titik) dokumen.push({ koleksi: 'pengaturan', data: titik });
  return { dokumen, hapus, titik, pulih: (arsipDok || []).map((a) => ({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok })), patch: { kabar: 'Tutup buku ' + tahun + ' dibatalkan — ' + ANGKA((arsipDok || []).length) + ' dokumen dikembalikan dari arsip, ' + hapus.length + ' saldo pembuka ditarik. Tahun ' + tahun + ' terbuka lagi.', kabarAwas: false } };
}
const KOLEKSI_CACHE = { batch: 'batchMasuk', piutang: 'piutangMutasi', kasbon: 'kasbonMutasi', produksi: 'produksiKemasan', bahanKemasan: 'stokBahanKemasan', bahanLiteran: 'stokBahanLiteran', utangPemasok: 'utangPemasokMutasi', utangOwner: 'utangOwnerMutasi', amplop: 'amplopLaba' };
function bkEraTanpa(tahun) { let t = null; Object.keys(KOLEKSI_CACHE).forEach((c) => cacheMentah(c).forEach((x) => { if (bkTutupBuku(x) && Number(x.tahunDari) !== tahun) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }
/** Selesai: cadangan sesudah tercatat → berita acara selesai (tidak bisa dibatalkan lagi). */
export function susunSelesai(tahun, namaCadangan2, w) {
  const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null; if (!acara || acara.status !== 'terkunci') return { tolak: 'Kunci tahunnya dulu' };
  return { dokumen: [{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara, { status: 'selesai', cadangan2: namaCadangan2 || '', selesaiPada: w.kini, selesaiTanggal: w.tanggal, langkah: Object.assign({}, acara.langkah || {}, { cadangan2: w.kini }) }) }], patch: { kabar: 'Tahun ' + tahun + ' selesai ditutup. Simpan kedua berkas cadangan di luar HP.', kabarAwas: false } };
}
/** Teks berita acara (cetak/WA). */
export function teksAcara(tahun, D, B, sebelum, saksi, w) {
  const L = ['TOKO BERAS M.IQBAL', 'BERITA ACARA TUTUP BUKU ' + tahun, tanggalPendek(w.tanggal) + ' · ' + w.jam + (D.latihan ? ' · LATIHAN' : ''), '', 'Harta toko akhir ' + tahun + ':'];
  B.baris.forEach((b) => L.push('  ' + (b.nama + '                                    ').slice(0, 38) + (b.a === null ? 'tidak bisa dihitung' : RP(b.a)) + (b.ada ? (b.sama ? '  ✓' : '  ≠ ' + RP(b.b)) : '')));
  L.push('', 'Jumlah harta   ' + RP(sebelum.hartaJml), 'Jumlah utang   ' + RP(sebelum.utangJml), 'Modal owner    ' + RP(sebelum.modal), 'Laba tinggal   ' + RP(sebelum.labaTinggal), '', 'Paraf: owner ' + (D.paraf && D.paraf.owner ? '✓' : '—') + ' · ' + (saksi || 'saksi') + ' ' + (D.paraf && D.paraf.saksi ? '✓' : '—'));
  return L.join('\n');
}
export { RP as bkRP };
