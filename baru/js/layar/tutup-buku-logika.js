// LAYAR UANG — K6 TUTUP BUKU tahunan (dikunci owner 18 Sep 2026: C · Berita Acara). Logika tanpa DOM; pembantu berawalan bk.
// Tujuh langkah BERURUT (tak bisa diloncati): periksa · cadangan sebelum · arsip · susun saldo pembuka · paraf dua orang · kunci (dua ketukan) · cadangan sesudah & selesai.
// Mode LATIHAN (bawaan: ritualnya tidak menulis apa pun — kecuali "Simpan putusan" per tanggal di langkah 1, yang tersimpan sungguhan) vs SUNGGUHAN
// (hanya bila tahunnya sudah lewat 31 Desember).
// 12 baris menyeberang — harta DAN utang — + 2 baris ikut dibandingkan (modal owner, upah belum dibayar; siap 2027) — tiap baris SEBELUM vs SESUDAH; beda satu rupiah pun tahun tidak boleh dikunci.
//
// Beda dengan sistem lama (tulisSaldoPembuka + hapusDokumenTahun): dokumen tahun lama TIDAK DIHAPUS — dipindah ke koleksi arsipTahun (kolom asli utuh) dan
// bisa dikembalikan lewat "Batalkan tutup buku" (sampai berita acaranya selesai). Saldo pembuka = dokumen yang PERSIS sama dengan sistem lama (batch stokAwal,
// produksi beliJadi, bahan saldoAwal, piutang/kasbon/utang saldoAwal, amplop setor, utangOwner saldoAwal; semuanya bertanda tutupBuku + tahunDari), ditulis
// SAAT KUNCI (bukan di langkah 4) supaya tidak ada jendela di mana stok & piutang terhitung dua kali (mesin lama membaca semua dokumen). Langkah 4 menyusunnya
// dan membandingkan sebelum vs sesudah dari susunan itu; sesudah kunci dibandingkan lagi dari mesin (hidup). Titik kas ditulis ulang di 31 Des dari saldo per tempat.
//
// SIAP 2027 (owner 7 Okt 2026, paket A): hari berjualan tanpa tutup hari diputus PER TANGGAL "tidak ditutup — diterima apa adanya" + alasan (aturanToko/putusanHari,
// juga putusan kunci bulan yang sudah ada) · gerbang g6 stok minus & kelebihan bayar · saldo pembuka membawa tanda buku (25 kg, adukan, merek pemasok, buku berstok 0)
// & modal owner · upah yang belum dibayar tercatat menyeberang · ringkasan tahun untuk KR1 / laju / pelanggan · perkiraan kuota · catatan susulan sesudah penanda.
//
// TUTUP BUKU TAHUN YANG BULANNYA SUDAH DIKUNCI (owner 7 Okt 2026, K8 "pengecualian sempit"; rules v7): kunci bulan berbentuk awalan, jadi mulai 2027 tahun
// yang ditutup selalu punya bulan terkunci — dan arsip memindah SEMUA catatan ≤ 31 Des (juga tahun-tahun sebelumnya). Ritual membuka PINTU TUTUP BUKU
// (pengaturan/pintuBuku = { tahun, status 'berjalan', sampai ≤ 72 jam }) di kiriman pertamanya; selama terbuka, server menerima PERSIS: saldo pembuka tahun
// itu (juga yang bertanggal utang tertua / bon lama / 31 Des), arsip catatan bulan terkunci yang salinannya ditulis di batch yang sama, pengembalian arsip
// saat Batalkan (isi sama), dan titik kas 31 Des / titikSebelum. Catatan bulan terkunci lainnya tetap tidak bisa diubah / ditambah. Pintu ditutup saat selesai /
// dibatalkan; dibuka lagi bila tinggal < 12 jam saat arsip dilanjutkan, kiriman lanjutan, atau pembatalan dimulai / dilanjutkan. Tanpa bulan terkunci (tutup
// buku 2026) = tanpa pintu, sama seperti sebelum v7.
// Sanggahan rules 7 Okt: server membaca berita acara SEBELUM kiriman yang membuka pintu (get) — jadi bila ada bulan terkunci, berita acara 'berjalan' dikirim
// SENDIRIAN dulu (kiriman 1), pintu baru dibuka di kiriman sesudahnya; pembatalan lanjutan dari 'dibatalkan' juga menulis 'membatalkan' sendirian dulu. Berita
// acara 'selesai' / 'dibatalkan' selalu satu kiriman dengan pintu yang ditutup (server menolaknya bila pintu tahun itu masih terbuka).
import { hitungSaldoTutup, tbDaftarKoleksi, hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungPiutang, hitungKasbon, hitungUtangPemasok, hitungUtangOwner, saldoAmplop } from '../mesin/beku.js';
import { tbCutoff, tbPunyaBerat, kunciPelanggan, merkPunyaKarungBerat, labelBahan, pesananBelumTuntas, KOLEKSI_PESANAN } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilPesanan, ambilSemuaBatch, ambilTutupHari, ambilTutupBukuAcara, ambilTitikKas, cacheMentah, kunciSampai, pintuBuku, pintuDari, petaStokWadah, petaBukuWadah, petaUkuran, ukuranDigabung, dokDiCache, dokTertunda, pembukaBerlaku, koleksiDariCache, hapusTertunda, CACHE_PEMBUKA, eraBuku, ringkasKreditLaju, kunciNota, versiCache, ingatStokKarung, ingatStokKemasan, denganCacheSaring } from '../data/toko.js';
import { KOLEKSI } from '../data/koleksi.js';
import { KP_BATAS_GET, kpPotong, kpNilaiKiriman, kpBulanDok, kpBebas, kpIdx, kpWib, kpNamaBulan, KP_ID_PINTU, KP_PINTU_JAM, KP_PINTU_SISA_JAM, kpPecahBiaya } from '../data/kunci-periode.js';
import { RP, ANGKA, KG, hariIniIso, jamKini, tanggalPendek, lebihBayarDari, kalimatLebih } from '../inti/format.js';
import { NAMA_KASBON_OWNER, ugAturDok, ugKiniDari, saldoKantong, modalTertanam } from './uang-logika.js';
import { aturUpah, hitungUpah, mulaiUpah } from './upah-logika.js';
import { ringkasPelangganTahun } from './pelanggan-logika.js';
import { susunPotret, ringkasPotret } from './potret-logika.js';
import { lpBonTerbuka } from './laporan-logika.js';
import { ringkasPemasokTahun, ringkasPesananTahun } from './bon-pemasok-logika.js';
import { hbKalimatBelum } from '../data/hemat-baca.js';

export const LANGKAH_BUKU = [['periksa', 'Periksa dulu'], ['cadangan1', 'Cadangan sebelum mulai'], ['arsip', 'Simpan arsip'], ['saldo', 'Susun saldo pembuka'], ['paraf', 'Paraf dua orang'], ['kunci', 'Kunci tahun'], ['cadangan2', 'Cadangan sesudahnya & selesai']];
const bkTutupBuku = (x) => !!(x && x.tutupBuku);
/** Era tutup buku = tahun saldo pembuka terakhir (sama dengan ssEraTutupBuku / eraTutupBuku sistem lama). Satu tempat: toko.js eraBuku (siap 2027: upah ikut membacanya). */
export function bkEra() { return eraBuku(); }
export function aturBuku() {
  const a = ugAturDok('tutupBuku') || {}; const saksi = Array.isArray(a.saksi) ? a.saksi.map((x) => String(x || '').trim()).filter(Boolean) : [];
  return { saksi: saksi.length ? saksi : aturUpah().orang.map((o) => o.nama), saksiTerukur: !saksi.length, dariOwner: !!ugAturDok('tutupBuku') };
}
export function susunAturBuku(isi, w) {
  const saksi = (Array.isArray(isi.saksi) ? isi.saksi : []).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8); if (!saksi.length) return { tolak: 'Saksi tidak boleh kosong — tutup buku butuh dua paraf' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'tutupBuku', tanggal: w.tanggal, jam: w.jam, saksi } }], patch: { aturB2: null, kabar: 'Daftar saksi disimpan — ' + saksi.join(', '), kabarAwas: false } };
}
// ---- A1 · PUTUSAN PER TANGGAL (owner 7 Okt: K2) — hari berjualan tanpa tutup hari tidak bisa ditutup mundur; owner memutus tiap tanggal "tidak ditutup — diterima
// apa adanya" dengan alasan (≥ 5 huruf), pola yang sama dengan kunci bulan. Disimpan sebagai DOKUMEN aturanToko/putusanHari (owner saja, rules sudah ada; bukan
// koleksi bertanggal) supaya bisa diisi kapan saja — juga dari latihan Desember — dan terbaca kunci bulan. Putusan hari di riwayat kunci bulan dipakai ulang.
export const BK_ID_PUTUSAN = 'putusanHari';
const bkAlasanCukup = (a) => String(a || '').trim().length >= 5;
/** { 'YYYY-MM-DD': { jenis: 'diterima', alasan, dari } } — putusan tersimpan (dokumen putusanHari menang atas riwayat kunci bulan). */
export function putusanHari() {
  const out = {}; const atur = cacheMentah('aturan');
  const kp = atur.find((d) => d && String(d.id) === 'kunciPeriode');
  ((kp && Array.isArray(kp.riwayat)) ? kp.riwayat : []).forEach((r) => { if (r && r.aksi === 'kunci') (r.hari || []).forEach((x) => { if (x && x.iso && x.jenis === 'diterima' && bkAlasanCukup(x.alasan)) out[x.iso] = { jenis: 'diterima', alasan: String(x.alasan).trim(), dari: 'kunci bulan' }; }); });
  const D = atur.find((d) => d && String(d.id) === BK_ID_PUTUSAN); const hari = (D && D.hari && typeof D.hari === 'object') ? D.hari : {};
  Object.keys(hari).forEach((t) => { const x = hari[t]; if (x && x.jenis === 'diterima' && bkAlasanCukup(x.alasan)) out[t] = { jenis: 'diterima', alasan: String(x.alasan).trim(), dari: 'tutup buku', tanggal: x.tanggal || '' }; });
  return out;
}
/** Simpan putusan. isi = { 'YYYY-MM-DD': alasan } (alasan kosong = putusan tanggal itu dicabut). Hanya tanggal hari berjualan tanpa tutup hari yang diterima. */
export function susunPutusanHari(isi, w) {
  const D = cacheMentah('aturan').find((d) => d && String(d.id) === BK_ID_PUTUSAN); const hari = Object.assign({}, (D && D.hari) || {});
  const tutup = {}; ambilTutupHari().forEach((t) => { tutup[t.tanggal] = true; }); const jual = {}; ambilPenjualan().forEach((p) => { if (p.tanggal) jual[p.tanggal] = true; });
  const pendek = [], bukan = []; let n = 0, cabut = 0;
  Object.keys(isi || {}).sort().forEach((t) => { if (!/^\d{4}-\d{2}-\d{2}$/.test(t)) return; const a = String(isi[t] || '').trim();
    if (!a) { if (hari[t]) { delete hari[t]; cabut += 1; } return; }
    if (tutup[t] || !jual[t]) { bukan.push(t); return; } if (!bkAlasanCukup(a)) { pendek.push(t); return; }
    hari[t] = { jenis: 'diterima', alasan: a.slice(0, 120), tanggal: w.tanggal, jam: w.jam }; n += 1; });
  if (pendek.length) return { tolak: 'Alasan minimal 5 huruf: ' + pendek.map(tanggalPendek).join(', ') };
  if (bukan.length) return { tolak: tanggalPendek(bukan[0]) + ' bukan hari berjualan tanpa tutup hari — tidak perlu diputus' };
  if (!n && !cabut) return { tolak: 'Tulis alasannya dulu (minimal 5 huruf) untuk tanggal yang tidak ditutup' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: BK_ID_PUTUSAN, hari, tanggal: w.tanggal, jam: w.jam } }],
    patch: { bkPutus: {}, kabar: (n ? n + ' hari dicatat "tidak ditutup — diterima apa adanya"' : '') + (n && cabut ? ' · ' : '') + (cabut ? cabut + ' putusan dicabut' : '') + '. Uang laci hari itu tetap tidak bisa dihitung ulang; alasannya ikut berita acara.', kabarAwas: false } };
}
/** Hari berjualan tahun itu (≤ sampai) yang tidak punya tutup hari, dengan jumlah nota & putusannya. */
function bkHariTanpaTutup(tahun, sampai) {
  const tutup = {}; ambilTutupHari().forEach((t) => { tutup[t.tanggal] = true; }); const nota = {};
  ambilPenjualan().forEach((p) => { if (p.tanggal && p.tanggal.slice(0, 4) === String(tahun) && p.tanggal <= sampai && !tutup[p.tanggal]) (nota[p.tanggal] = nota[p.tanggal] || new Set()).add(kunciNota(p)); });
  const P = putusanHari(); return Object.keys(nota).sort().map((t) => ({ iso: t, nNota: nota[t].size, putusan: P[t] || null }));
}
/** Tahun yang bisa ditutup: sesudah era terakhir, mulai dari catatan pertama. Sungguhan hanya bila hari ini sudah lewat 31 Des tahun itu. */
export function tahunBuku(kini) {
  const iso = hariIniIso(kini); const era = bkEra(); let pertama = '';
  ambilPenjualanSemua().concat(ambilSemuaBatch().filter((b) => !b.stokAwal && !b.tutupBuku)).forEach((d) => { if (d.tanggal && (!pertama || d.tanggal < pertama)) pertama = d.tanggal; });
  const awal = era !== null ? era + 1 : (pertama ? Number(pertama.slice(0, 4)) : Number(iso.slice(0, 4))); const tahun = Math.min(awal, Number(iso.slice(0, 4)));
  // K1 (owner 25 Sep 2026): catatan bulan TERKUNCI tidak bisa diubah / dihapus. Keputusan owner 1 Okt (A): tutup buku 2026 tanpa bulan terkunci (kunci bulan
  // mulai 2027 & menunggu tutup buku tahun lalu — siap 2027 A2). Keputusan owner 7 Okt (K8, pengecualian sempit, rules v7): tahun yang bulannya terkunci
  // ditutup lewat PINTU TUTUP BUKU (lihat kepala berkas) — jadi tutup buku 2027 di Januari 2028 tidak buntu. Catatan dasar disimpan 10 tahun (UU KUP Pasal 28
  // ayat 11): berkas arsip dan cadangan SEBELUM. perluPintu = ada bulan terkunci mana pun (arsip memindah semua catatan ≤ 31 Des, juga tahun-tahun lalu).
  const sampai = kunciSampai(); const adaKunci = !!sampai && sampai >= tahun + '-01'; const perluPintu = !!sampai;
  const bolehSungguhan = iso > tbCutoff(tahun); const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null;
  return { tahun, era, pertama, bolehSungguhan, adaKunci, perluPintu, sampaiKunci: sampai || '', cutoff: tbCutoff(tahun), tglBuka: (tahun + 1) + '-01-01', acara,
    teks: !bolehSungguhan ? 'Tahun ' + tahun + ' belum lewat 31 Desember — sekarang cuma bisa LATIHAN'
      : perluPintu ? 'Tahun ' + tahun + ' sudah lewat — bisa ditutup sungguhan. Bulan sampai ' + kpNamaBulan(sampai) + ' sudah dikunci: tutup buku membuka "pintu tutup buku" sebentar (hanya saldo pembuka, arsip & Batalkan; catatan bulan terkunci lainnya tetap tidak bisa diubah)'
      : 'Tahun ' + tahun + ' sudah lewat — bisa ditutup sungguhan' };
}
// ---- PINTU TUTUP BUKU (rules v7) — dokumen pengaturan/pintuBuku; kunci-periode.js kpPintu / kpLewatPintu = inti yang sama dengan rules
/** Dokumen pintu yang dibuka (umur KP_PINTU_JAM menurut jam perangkat; rules menerima ≤ 72 jam dari jam server). */
const bkJam = (w) => new Date(Date.parse(w && w.kini) || Date.now());   // jam SEBENARNYA kiriman (ugKiniDari = tengah hari tanggalnya — bukan untuk umur pintu)
function bkPintuDok(tahun, w) {
  const t = bkJam(w).getTime();
  return { koleksi: 'pengaturan', data: { id: KP_ID_PINTU, tahun, status: 'berjalan', sampai: new Date(t + KP_PINTU_JAM * 3600000), dibuka: w.kini, tanggal: w.tanggal, jam: w.jam } };
}
/** Pintu tahun itu yang terbuka di cache dan masih ≥ 12 jam lagi (null = perlu dibuka / diperbarui). */
function bkPintuSegar(tahun, kini) { const P = pintuBuku(); const t = kini ? kini.getTime() : Date.now(); return P && P.tahun === tahun && P.sampai - t >= KP_PINTU_SISA_JAM * 3600000 ? P : null; }
/**
 * Pintu sebelum arsip (uang.js bukaPintu), di kiriman lanjutan pertama (lanjutBuku) & kiriman pembatalan pertama (susunBatal): { dokumen: [pintu] } bila tahun itu
 * perlu pintu (ada bulan terkunci) dan pintunya belum terbuka atau tinggal
 * < 12 jam; {} bila tidak perlu. Server hanya menerimanya selama berita acara tahun itu berjalan / terkunci / membatalkan (rules pintuSah).
 */
export function susunPintu(tahun, w) {
  if (!kunciSampai() || bkPintuSegar(tahun, bkJam(w))) return {};
  return { dokumen: [bkPintuDok(tahun, w)] };
}
/** Menutup pintu (selesai / dibatalkan): dokumen 'tutup' bila pintu tahun itu terbuka di cache (atau `baru` = baru dibuka di kiriman ini); [] bila tidak ada. */
function bkTutupPintu(tahun, w, baru) {
  const d = dokDiCache('pengaturan', KP_ID_PINTU); if (!baru && (!d || d.status !== 'berjalan' || Number(d.tahun) !== tahun)) return [];
  return [{ koleksi: 'pengaturan', data: { id: KP_ID_PINTU, tahun, status: 'tutup', sampai: bkJam(w), ditutup: w.kini, tanggal: w.tanggal, jam: w.jam } }];
}
/** Pintu yang berlaku untuk menyusun kiriman (yang akan ditulis di kiriman pertama, atau yang sudah terbuka). */
const bkPintuPakai = (dok, w) => (dok ? pintuDari(dok.data, bkJam(w)) : pintuBuku());
/** Gerbang sebelum mulai. lokal = { antre, menunggu, offline, idPerangkat }; lewati = { g3: true } untuk yang owner nyatakan sudah beres. */
export function gerbangBuku(tahun, kini, lokal, lewati) {
  const L = lokal || {}; const V = lewati || {}; const iso = hariIniIso(kini); const cutoff = tbCutoff(tahun); const sampai = iso < cutoff ? iso : cutoff;
  // A1 (siap 2027): hari tanpa tutup hari LOLOS hanya dengan putusan per tanggal ("tidak ditutup — diterima apa adanya" + alasan); tanpa putusan tetap memblokir
  const hariG1 = bkHariTanpaTutup(tahun, sampai); const belumTutup = hariG1.map((h) => h.iso); const belumPutus = hariG1.filter((h) => !h.putusan).map((h) => h.iso);
  const t = kini.getTime(); const lain = cacheMentah('perangkat').filter((d) => String(d.id) !== String(L.idPerangkat || '') && d.pada && t - new Date(d.pada).getTime() < 15 * 60000).map((d) => d.nama || d.id);
  const karcis = ambilPenjualan().filter((p) => p.tanggal && p.tanggal.slice(0, 4) === String(tahun) && (p.jenis === 'kasir_darurat_nominal' || p.perluKoreksi)).length;   // yang masih berlaku saja — persis daftarDaruratBelumRinci & daftarPerluRapikan
  const nAntre = (L.antre || []).length + (Number(L.menunggu) || 0);
  const M = minusBuku(sampai);
  const g = [
    { id: 'g1', teks: 'Semua hari berjualan tahun ' + tahun + ' sudah ditutup — atau diputus "tidak ditutup — diterima apa adanya"', ok: belumPutus.length === 0,
      ket: !belumTutup.length ? 'semua hari berjualan punya penutupan' : belumPutus.length ? belumPutus.length + ' hari belum ditutup & belum diputus: ' + belumPutus.slice(0, 3).map(tanggalPendek).join(', ') + (belumPutus.length > 3 ? ' …' : '') + (belumTutup.length > belumPutus.length ? ' · ' + (belumTutup.length - belumPutus.length) + ' hari sudah diputus' : '')
        : belumTutup.length + ' hari tanpa tutup hari, semuanya sudah diputus "diterima apa adanya" (alasannya ikut berita acara)',
      aksi: belumPutus.length ? 'Tutup hari tidak bisa dibuat mundur — putuskan tiap tanggal di bawah: tidak ditutup, diterima apa adanya, dengan alasan' : '', bisaLewati: false, hari: hariG1 },
    { id: 'g2', teks: 'Tidak ada catatan yang menunggu terkirim', ok: nAntre === 0, ket: nAntre ? nAntre + ' catatan perangkat ini belum diakui server' : 'semua sudah sampai', aksi: nAntre ? 'Tunggu sinyal sampai antrean kosong' : '', bisaLewati: false },
    { id: 'g3', teks: 'Perangkat lain sudah berhenti dipakai', ok: lain.length === 0 || !!V.g3, ket: lain.length ? (V.g3 ? 'owner menyatakan sudah dimatikan (' + lain.join(', ') + ')' : lain.join(', ') + ' masih berdenyut 15 menit terakhir') : 'tidak ada perangkat lain yang berdenyut', aksi: lain.length && !V.g3 ? 'Sudah dimatikan' : '', bisaLewati: true },
    { id: 'g4', teks: 'Tidak ada karcis kasir yang belum dirinci / dirapikan', ok: karcis === 0, ket: karcis ? karcis + ' nota menunggu dirinci atau dirapikan' : 'tidak ada', aksi: karcis ? 'Rinci di Jual → Karcis' : '', bisaLewati: false },
    { id: 'g5', teks: 'Internet tersambung', ok: !L.offline, ket: L.offline ? 'tanpa internet — ritual ini langsung ke server' : 'tersambung', aksi: '', bisaLewati: false },
    // A5 (siap 2027): saldo pembuka hanya membawa yang bersisa — stok minus & kelebihan bayar per 31 Des LENYAP saat tahun ditutup (mesin beku tidak diubah)
    { id: 'g6', teks: 'Tidak ada stok minus atau kelebihan bayar per ' + tanggalPendek(sampai), ok: !M.n,
      ket: M.n ? M.n + ' hal — ' + M.daftar.slice(0, 3).map((x) => x.teks).join(' · ') + (M.n > 3 ? ' · …' : '') + '. Kalau dibiarkan, angkanya hilang dari buku saat tahun ditutup.' : 'tidak ada buku yang minus, tidak ada yang dibayar lebih',
      aksi: M.n ? 'Bereskan satu per satu (jalannya di tiap baris)' : '', bisaLewati: false, rincian: M.daftar },
  ];
  // owner 7 Okt (hemat baca nyala): tutup buku (setahun sekali) dimulai hanya sesudah perangkat ini membaca penuh SEMUA koleksi di sesi ini — angka 31 Des tidak
  // boleh dari simpanan yang belum terperiksa. Hemat baca mati: butir ini tidak ada (daftar sama dengan sebelumnya).
  // #111 × Paket C: juga SATU sumber kelengkapan (hemat-baca.js hbBelumLengkap) — dibaca penuh sesi ini tapi batu nisan / ubahan belum dicocokkan lagi = belum
  if (L.hemat && L.hemat.nyala) { const hb = hbKalimatBelum(L.hemat.belumLengkap, null); const ok7 = !!L.hemat.totalSesiIni && !hb;
    g.push({ id: 'g7', teks: 'Perangkat ini sudah membaca penuh semua catatan sesi ini (hemat baca)', ok: ok7,
      ket: ok7 ? 'semua jenis catatan dibaca penuh & cocok dengan server' : !L.hemat.totalSesiIni ? 'hemat baca nyala — angka dari simpanan perangkat belum dibaca penuh sesi ini' : hb, aksi: ok7 ? '' : 'Baca penuh dulu: Menu › Sistem › Perangkat › Hemat baca', bisaLewati: false }); }
  return { daftar: g, semuaOk: g.every((x) => x.ok), belum: g.filter((x) => !x.ok).length, belumTutup, belumPutus, hari: hariG1 };
}
/**
 * A5 · yang MINUS atau DIBAYAR LEBIH pada `sampai` (31 Des) — per buku / nama, dengan kalimat toko & jalan beresnya. Saldo pembuka (hitungSaldoTutup) hanya
 * membawa sisa > 0: kemasan & kantong minus dibuang diam-diam, beras minus jadi baris pembuka bermodal 0, kelebihan bayar pelanggan / ke pemasok / ke owner &
 * kasbon yang dibayar lebih lenyap bersama catatan pembayarannya. Ambang sama dengan mesin (0,01 kg; 0,5 rupiah).
 */
export function minusBuku(sampai) {
  const d = []; const tambah = (jenis, teks, jalan) => d.push({ jenis, teks, jalan });
  const K = ingatStokKarung(sampai); Object.keys(K).sort().forEach((m) => { const s = K[m].sisaKg; if (s <= -0.01) tambah('beras', 'Buku ' + m + ' minus ' + KG(-s), 'hitung isinya di Stok › Cocokkan (opname), atau catat kedatangan / pindah buku yang terlupa'); });
  const KM = ingatStokKemasan(sampai); Object.keys(KM).sort().forEach((k) => { const s = KM[k]; if (s.sisaUnit < -0.001) tambah('kemasan', s.namaProduk + ' ' + String(s.ukuranKemasan).replace('.', ',') + ' kg minus ' + ANGKA(-s.sisaUnit) + ' kantong', 'hitung kemasannya di Stok › Cocokkan › kemasan, atau catat adukan yang terlupa'); });
  const BK = hitungStokBahanKemasan(sampai), BL = hitungStokBahanLiteran(sampai);
  [[BK, 'kantong kemasan'], [BL, 'kantong literan']].forEach(([peta, jenis]) => Object.keys(peta).sort().forEach((j) => { if (peta[j].sisaPcs < -0.001) tambah('kantong', labelBahan(j) + ' minus ' + ANGKA(-peta[j].sisaPcs) + ' lembar', 'hitung ' + jenis + ' di Stok › Kantong, atau catat pembelian kantong yang terlupa'); }));
  lebihBayarDari(hitungPiutang(sampai)).orang.forEach((o) => tambah('pelanggan', o.nama + ': ' + kalimatLebih(o), o.uang > 0.5 ? 'kembalikan uangnya atau catat bon yang terlupa (Pelanggan)' : 'balik hapus bukunya (Pelanggan)'));
  hitungUtangPemasok(sampai).forEach((px) => { if ((px.tekor || 0) > 0.5) tambah('pemasok', 'Bayar ke ' + px.pemasok + ' lebih ' + RP(px.tekor) + ' dari semua bon yang tercatat', 'catat bon / kedatangan berutang yang terlupa (Harga & Pemasok), atau catat uang yang dikembalikan pemasok'); });
  const uo = hitungUtangOwner(sampai); if ((uo.tekor || 0) > 0.5) tambah('owner', 'Toko membayar owner lebih ' + RP(uo.tekor) + ' dari utang yang pernah tercatat', 'catat belanja toko yang dibayar dompet owner tapi terlupa (Uang › Owner & toko)');
  hitungKasbon(sampai).forEach((x) => { if (x.sisa < -0.5) tambah('kasbon', 'Kasbon ' + x.nama + ' dibayar lebih ' + RP(-x.sisa), 'catat kasbon yang terlupa, atau kembalikan kelebihannya (Uang › Orang & upah)'); });
  return { daftar: d, n: d.length };
}
/** Semua baris yang dibandingkan: harta · utang · lain (modal owner & upah belum dibayar — siap 2027). */
const bkBaris = (B) => B.harta.concat(B.utang, B.lain || []);
const bkTambahHari = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
/**
 * A6 · UPAH yang sudah jadi hak tapi belum dibayar per `sampai` (hari kerja terisi sejak terakhir dibayar, hitungUpah — satu tempat). `lama` = tanggal terakhir
 * yang tertutup gaji SISTEM LAMA (biayaBulanan, ikut diarsip tutup buku): dibawa berita acara supaya "sejak terakhir dibayar" tidak mundur sesudah arsip.
 */
export function upahPada(sampai) {
  const [y, m, d] = String(sampai).split('-').map(Number); const kini = new Date(y, m - 1, d, 12, 0, 0);
  const orang = aturUpah().orang.map((o) => { const H = hitungUpah(o.nama, kini, 'tidak'); const M = mulaiUpah(o.nama, sampai);
    return { nama: o.nama, kunci: kunciPelanggan(o.nama), upah: Math.round(H.upah || 0), mulai: H.mulai, sampai: H.akhir, penuh: H.penuh, setengah: H.setengah, kosong: H.kosong, sumber: M.sumber, lama: M.sumber === 'lama' ? bkTambahHari(M.mulai, -1) : '' }; });
  return { orang, jumlah: orang.reduce((a, o) => a + o.upah, 0) };
}
/** 12 baris yang menyeberang (+ baris lain: modal owner dan upah belum dibayar), dihitung mesin pada tanggal `sampai`; kas per tempat dari saldoKantong(sampaiKas). Rupiah stok dibulatkan PER MEREK (sama dengan yang ditulis di saldo pembuka). */
export function barisBuku(sampai, sampaiKas, titikPakai) {
  const stokK = ingatStokKarung(sampai); let kg = 0, rpK = 0, nK = 0; Object.keys(stokK).forEach((m) => { const s = stokK[m]; if (Math.abs(s.sisaKg) < 0.01) return; nK += 1; kg += s.sisaKg; rpK += Math.round(s.sisaKg * (s.hppTerakhirPerKg || 0)); });
  // A5 (siap 2027): baris TIDAK LAGI BUTA MINUS — kemasan, kantong, piutang, kasbon yang minus / dibayar lebih ikut dijumlah, dan kelebihan bayar ke pemasok &
  // owner mengurangi utangnya. Saldo pembuka hanya membawa yang bersisa, jadi sisi "sesudah" berbeda (≠) selama itu belum dibereskan (gerbang g6).
  const stokM = ingatStokKemasan(sampai); let unit = 0, rpM = 0, minM = 0; Object.keys(stokM).forEach((k) => { const s = stokM[k]; if (!(Math.abs(s.sisaUnit) > 1e-9)) return; unit += s.sisaUnit; rpM += s.sisaUnit * (s.hppRataRataPerUnit || 0); if (s.sisaUnit < 0) minM += 1; });
  const bk = hitungStokBahanKemasan(sampai), bl = hitungStokBahanLiteran(sampai); let pcs = 0, rpB = 0, minB = 0; Object.keys(bk).forEach((j) => { if (Math.abs(bk[j].sisaPcs) > 1e-9) { pcs += bk[j].sisaPcs; rpB += Math.round(bk[j].sisaPcs * (bk[j].hppPerPcs || 0)); if (bk[j].sisaPcs < 0) minB += 1; } }); Object.keys(bl).forEach((j) => { if (Math.abs(bl[j].sisaPcs) > 1e-9) { pcs += bl[j].sisaPcs; rpB += Math.round(bl[j].sisaPcs * (bl[j].hargaPerPcs || 0)); if (bl[j].sisaPcs < 0) minB += 1; } });
  const semuaPiutang = hitungPiutang(sampai); const piutang = semuaPiutang.filter((x) => x.sisa > 0); const lebihP = semuaPiutang.filter((x) => x.sisa < -0.5); const kasbon = hitungKasbon(sampai).filter((x) => Math.abs(x.sisa) >= 0.5); const kO = kunciPelanggan(NAMA_KASBON_OWNER);
  // no. 4: saldo pembuka mesin (hitungSaldoTutup) hanya membawa piutang sisa > 0 dan dokumen pembayarannya diarsipkan → kelebihan bayar pelanggan lenyap dari buku
  // saat tahun dikunci (uangnya tetap di kas). Mesin tidak diubah; di sini hanya BERBUNYI. Menahan tutup buku karenanya = keputusan owner.
  const lebih = lebihBayarDari(semuaPiutang); const kataLebih = !lebih.n ? '' : (lebih.hapus.n ? 'Sisa bon di bawah nol ' : 'Kelebihan bayar pelanggan ') + RP(lebih.jumlah) + ' ('
    + lebih.orang.map((x) => x.nama + ' ' + RP(x.lebih) + (x.hapus > 0.5 ? (x.uang > 0.5 ? ', sebagian hapus buku yang ternyata dibayar' : ', hapus buku yang ternyata dibayar') : '')).join('; ')
    + ') TIDAK ikut menyeberang: saldo pembuka hanya membawa bon yang bersisa dan catatan pembayarannya diarsipkan, jadi sesudah tahun dikunci jejaknya hilang dari buku'
    + (lebih.uang.n ? ' — uangnya tetap di kas.' : '.') + (lebih.hapus.n ? ' Hapus buku yang ternyata dibayar perlu dibalik sebelum tahun dikunci.' : '');
  const kasbonK = kasbon.filter((x) => x.kunci !== kO).reduce((a, x) => a + x.sisa, 0); const kasbonO = kasbon.filter((x) => x.kunci === kO).reduce((a, x) => a + x.sisa, 0);
  const K = saldoKantong(sampaiKas || sampai, titikPakai); const amplop = saldoAmplop(sampai); const up = hitungUtangPemasok(sampai); const tekorP = up.reduce((a, x) => a + (x.tekor || 0), 0); const utangP = up.reduce((a, x) => a + x.totalUtang, 0) - tekorP, nBon = up.reduce((a, x) => a + x.bon.length, 0); const uo = hitungUtangOwner(sampai);
  const kas = (k) => (K.ada ? Math.round(K[k]) : null); const kataMin = (n) => (n ? ' · ' + n + ' MINUS' : '');
  const harta = [{ id: 'beras', nama: 'Stok beras · ' + KG(Math.round(kg * 10) / 10) + ' · ' + nK + ' merek', n: rpK }, { id: 'kemasan', nama: 'Kemasan jadi · ' + ANGKA(unit) + ' kantong' + kataMin(minM), n: Math.round(rpM) }, { id: 'bahan', nama: 'Kantong kosong & paper bag · ' + ANGKA(pcs) + ' lembar' + kataMin(minB), n: rpB },
    { id: 'piutang', nama: 'Piutang pelanggan · ' + piutang.length + ' orang' + (lebihP.length ? ' · ' + lebihP.length + ' dibayar LEBIH' : ''), n: semuaPiutang.reduce((a, x) => a + (Math.abs(x.sisa) >= 0.5 ? x.sisa : 0), 0) }, { id: 'kasbonK', nama: 'Kasbon karyawan', n: kasbonK }, { id: 'kasbonO', nama: 'Kasbon owner', n: kasbonO },
    // amplop = UANG di amplop (titik kas + sisihan), bukan Σ dokumen amplopLaba (saldoAmplop): kasPada menghitung titik.amplop, dan dokumen pembuka amplop (sistem lama) tetap ditulis dari saldoAmplop
    { id: 'laci', nama: 'Uang di laci', n: kas('laci') }, { id: 'brankas', nama: 'Uang di brankas', n: kas('brankas') }, { id: 'rekening', nama: 'Uang di rekening', n: kas('rekening') }, { id: 'amplop', nama: 'Amplop laba (uang)', n: kas('amplop') }];
  const utang = [{ id: 'utangP', nama: 'Utang ke pemasok · ' + nBon + ' bon' + (tekorP > 0.5 ? ' · dibayar LEBIH ' + RP(tekorP) : ''), n: Math.round(utangP) }, { id: 'utangO', nama: 'Toko berutang ke owner' + ((uo.tekor || 0) > 0.5 ? ' · dibayar LEBIH ' + RP(uo.tekor) : ''), n: Math.round(uo.sisa - (uo.tekor || 0)) }];
  // 39b no. 12: uang per tempat yang TIDAK BISA dihitung (titik kas terakhir lebih muda dari tanggal ini — mesin tidak menghitung mundur) bukan nol: jumlah harta
  // & laba yang tinggal ikut "belum bisa dihitung" (dulu dijumlah nol → berita acara menulis harta kurang seukuran kas)
  const hartaJml = K.ada ? harta.reduce((a, h) => a + (h.n || 0), 0) : null, utangJml = utang.reduce((a, u) => a + (u.n || 0), 0); const modal = modalTertanam(sampai);
  // A4 & A6 (siap 2027): baris LAIN yang ikut dibandingkan sebelum/sesudah tapi tidak masuk jumlah harta/utang — modal owner (setoran, bukan pinjaman) dan upah
  // karyawan yang sudah jadi hak tapi belum dibayar (dibayar sesudah tahun ditutup = biaya bulan pembayaran, aturan K5; dicatat supaya tidak lenyap)
  const UP = upahPada(sampai);
  const lain = [{ id: 'modal', nama: 'Modal owner di toko (setoran, bukan pinjaman)', n: Math.round(modal) }, { id: 'upah', nama: 'Upah karyawan yang belum dibayar · ' + UP.orang.filter((o) => o.upah > 0).length + ' orang', n: UP.jumlah }];
  const labaTinggal = hartaJml === null ? null : hartaJml - utangJml - modal; const tk = ambilTitikKas();
  return { harta, utang, lain, hartaJml, utangJml, modal, labaTinggal, kasAda: K.ada, K, amplopDok: Math.round(amplop), n: harta.length + utang.length + lain.length, lebih, kataLebih, upah: UP,
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
    // siap 2027: "punya karung 50 kg" juga dari produksi jadi karung utuh (merkPunyaKarungBerat) — produksinya ikut diarsip, jadi barisnya dibawa ke sini
    const beratLain = beratUtama === 50 ? 25 : 50; if ((beratLain === 25 && x.punya25) || (beratLain === 50 && (x.punya50 || merkPunyaKarungBerat(x.merk, 50)))) merkList.push({ merk: x.merk, satuan: 'karung', beratKarung: beratLain, jumlahKarung: 0, totalKg: 0, hargaPerKg: x.hppPerKg, subtotalHarga: 0 }); });
  // putaran 28: buku STOK WADAH tetap dikenali sesudah tutup buku — barisnya membawa tanda stokWadah; yang sisanya nol ikut lahir lagi (baris 0 kg), karena
  // mesin beku hanya memotong penjualan dari nama yang lahir lewat batch (tanpa wadah berstok sendiri = dokumen persis index.html)
  // putaran 39: karung belakang membawa tandanya sendiri (karungBelakang + merkAsal) supaya sesudah tutup buku tetap dikenali buku karung belakang, bukan karung wadah
  // A3 (siap 2027): SEMUA buku yang dikenal pada 31 Des lahir lagi — yang berstok 0 jadi baris 0 kg dengan ukuran karung yang sama (rak Jual sama: chip "habis"
  // tetap ada) — dan tiap baris membawa tanda bukunya: buku karung 25 kg (indukUkuran, + digabungKe bila sudah digabung balik), kemasan adukan yang dibuka
  // (bukuAdukan — dulu salah jadi karungWadah), merek pemasok kelas (merkPemasok). Pembaca tanda di toko.js tidak berubah: sebelum = sesudah ritual.
  const c = tbCutoff(tahun); const stokK = hitungStokKarungPerMerk(c); const pw = petaStokWadah(); const bw = petaBukuWadah();
  Object.keys(stokK).concat(Object.keys(pw)).sort().forEach((k) => { if (merkList.some((r) => r.merk === k)) return; const hpp = stokK[k] ? stokK[k].hppTerakhirPerKg || 0 : 0;
    const berat = [50, 25].filter((b) => tbPunyaBerat(k, b, c) || merkPunyaKarungBerat(k, b));
    if (berat.length) berat.forEach((b) => merkList.push({ merk: k, satuan: 'karung', beratKarung: b, jumlahKarung: 0, totalKg: 0, hargaPerKg: hpp, subtotalHarga: 0 }));
    else merkList.push({ merk: k, satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0 }); });
  const asliAdukan = {}, pemasokKelas = {}; ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (!m || !m.merk) return; if (m.bukuAdukan && !m.stokWadah && !m.karungWadah) asliAdukan[m.merk] = m.bukuAdukan; if (m.merkPemasok) pemasokKelas[m.merk] = m.merkPemasok; }));
  const pu = petaUkuran(); const ug = ukuranDigabung();
  merkList.forEach((r) => { if (pw[r.merk]) r.stokWadah = pw[r.merk]; else if (bw[r.merk] && bw[r.merk].jenis === 'belakang') { r.karungBelakang = bw[r.merk].wadah; r.merkAsal = bw[r.merk].merk; }
    else if (bw[r.merk] && bw[r.merk].jenis === 'adukan') r.bukuAdukan = asliAdukan[r.merk] || bw[r.merk].wadah; else if (bw[r.merk]) r.karungWadah = bw[r.merk].wadah;
    if (pemasokKelas[r.merk]) r.merkPemasok = pemasokKelas[r.merk]; if (ug[r.merk]) r.digabungKe = ug[r.merk]; });
  // petaUkuran membaca berat dari baris yang membawa indukUkuran (baris terakhir menang) → tanda hanya di baris berukuran buku itu
  Object.keys(pu).forEach((k) => { const baris = merkList.filter((r) => r.merk === k); const pas = baris.filter((r) => (Number(r.beratKarung) || 25) === pu[k].berat); (pas.length ? pas : baris.slice(0, 1)).forEach((r) => { r.indukUkuran = pu[k].induk; }); });
  if (merkList.length) d.push({ koleksi: 'batchMasuk', data: Object.assign({ id: w.idUnik(), tanggal: tglBuka, pemasok: 'TUTUP BUKU ' + tahun, biayaBongkar: 0, stokAwal: true, merkList }, tb) });
  // hppPerUnit TIDAK dibulatkan (sistem lama membulatkan) supaya nilai kemasan sesudah = sebelum sampai rupiahnya; mesin menerima pecahan
  saldo.kemasan.forEach((x) => d.push({ koleksi: 'produksiKemasan', data: Object.assign({ id: w.idUnik(), tanggal: tglBuka, namaProduk: x.namaProduk, ukuranKemasan: x.ukuran, jumlahUnit: x.sisaUnit, hppPerUnit: x.hppPerUnit, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true, stokAwal: true }, tb) }));
  // A3 (siap 2027): kemasan jadi berstok 0 ikut lahir lagi (0 kantong, bernilai 0) — rak Jual tetap punya chip "habis"-nya (dulu chipnya hilang sesudah ritual)
  const stokM0 = hitungStokKemasan(c); Object.keys(stokM0).sort().forEach((k) => { const s = stokM0[k]; if (Math.abs(s.sisaUnit) > 1e-9) return;
    d.push({ koleksi: 'produksiKemasan', data: Object.assign({ id: w.idUnik(), tanggal: tglBuka, namaProduk: s.namaProduk, ukuranKemasan: s.ukuranKemasan, jumlahUnit: 0, hppPerUnit: 0, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true, stokAwal: true }, tb) }); });
  saldo.bahanK.forEach((x) => d.push({ koleksi: 'stokBahanKemasan', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', jenis: x.jenis, jumlah: x.sisaPcs, hargaTotal: Math.round(x.sisaPcs * x.hargaRata), tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun }, tb) }));
  saldo.bahanL.forEach((x) => d.push({ koleksi: 'stokBahanLiteran', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', jenis: x.jenis, jumlah: x.sisaPcs, hargaTotal: Math.round(x.sisaPcs * x.hargaRata), tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun }, tb) }));
  // Paket B (sanggahan): saldo awal piutang MEMBAWA bon-bon yang masih terbuka (sisa, nilai & margin asli, nota — lpBonTerbuka, urutan potong buku bon), supaya
  // margin bon tahun ini yang dibayar sesudah ritual kembali ke "diterima tunai" bulan bayarnya persis seperti sebelum ritual. Σ sisa ≠ saldo → tidak dibawa.
  const bonBuka = lpBonTerbuka(c);
  saldo.piutang.forEach((x) => { const mb = bonBuka[kunciPelanggan(x.nama)] || []; const cocok = mb.length && Math.abs(mb.reduce((a, b) => a + b.sisa, 0) - x.sisa) < 1;
    d.push({ koleksi: 'piutangMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', namaPelanggan: x.nama, nominal: x.sisa, tanggal: x.tanggalTertua, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — tanggal mengikuti utang tertuanya supaya umurnya jujur' }, cocok ? { marginBon: mb } : {}, tb) }); });
  saldo.kasbon.forEach((x) => d.push({ koleksi: 'kasbonMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', namaPegawai: x.nama, nominal: x.sisa, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun }, kunciPelanggan(x.nama) === kunciPelanggan(NAMA_KASBON_OWNER) ? { owner: true } : {}, tb) }));
  saldo.utangPemasok.forEach((px) => px.bon.forEach((b) => d.push({ koleksi: 'utangPemasokMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', pemasok: px.pemasok, nominal: b.sisa, bonTanggal: b.bonTanggal, tanggal: tglBuka, catatan: 'Saldo pembuka tutup buku ' + tahun + (b.catatan ? ' — ' + b.catatan : '') }, tb) })));
  if (saldo.amplop > 0) d.push({ koleksi: 'amplopLaba', data: Object.assign({ id: w.idUnik(), tipe: 'setor', nominal: saldo.amplop, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — isi amplop laba yang menyeberang tahun' }, tb) });
  if (saldo.utangOwner > 0) d.push({ koleksi: 'utangOwnerMutasi', data: Object.assign({ id: w.idUnik(), tipe: 'saldoAwal', nominal: saldo.utangOwner, tanggal: tglBuka, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — belanja toko yang dibayar dompet owner dan belum dilunasi' }, tb) });
  // A4 (siap 2027): MODAL OWNER menyeberang — setoran & tarikan modal (modalOwner, setoranKas lama) ikut diarsip, jadi satu dokumen pembuka membawa jumlahnya.
  // Bertanggal 31 Des, BUKAN 1 Jan: mesin kas menghitung tiap 'setor' sebagai uang MASUK sesudah titik kas; titik kas tahun baru = 31 Des, jadi dokumen ini tidak
  // pernah terbaca sebagai uang masuk (jam 00.00: juga bukan "catatan sesudah tutup" hari itu). Pinjaman owner tidak dihitung modal (utangnya menyeberang sendiri).
  const modal = modalTertanam(c);
  if (Math.abs(modal) >= 0.5) d.push({ koleksi: 'modalOwner', data: Object.assign({ id: w.idUnik(), tipe: modal > 0 ? 'setor' : 'tarik', nominal: Math.round(Math.abs(modal)), tanggal: c, jam: '00:00', catatan: 'Saldo pembuka tutup buku ' + tahun + ' — modal owner yang tertanam s.d. 31 Des (bukan uang masuk)' }, tb) });
  return { dokumen: d, saldo, tglBuka, upah: upahPada(c) };
}
/**
 * Paket C (8 Okt 2026): RINGKASAN saldo pembuka di berita acara saat kunci — pembanding kartu "Pemeriksaan sesudah tutup buku" (periksa-sesudah-logika.js):
 *  - `beras` / `kemasan`: baris yang DITULIS (dokumen pembuka pembukaBuku: merek, satuan, berat, kg, tanda buku; kemasan per produk) — tanda buku & rak Jual
 *    tetap punya pembanding walau dokumennya kelak berubah / tandanya terlepas;
 *  - `sebelum` (sanggahan Paket C, "penjaga yang mewarisi kekuatannya"): dihitung dari CATATAN HIDUP 31 Des sebelum apa pun ditulis — bukan dari dokumen pembuka —
 *    sisa kg per merek, sisa per produk kemasan, sisa bon per pelanggan, kasbon per orang, utang per pemasok. Ritual yang memindah isi antar-merek / antar-orang
 *    dengan total rupiah sama (lolos baris perbandingan) berbunyi di kartu. Tanpa `tahun` (pemanggil lama) = tanpa `sebelum`.
 * Bentuknya diterima Firestore (larik objek, tanpa larik di dalam larik).
 */
const BK_TANDA_BUKU = ['indukUkuran', 'stokWadah', 'karungWadah', 'bukuAdukan', 'karungBelakang', 'merkAsal', 'digabungKe', 'merkPemasok'];
export function ringkasPembuka(dokumen, tahun) {
  const beras = [], kemasan = [];
  (dokumen || []).forEach(({ koleksi, data }) => {
    if (koleksi === 'batchMasuk') (data.merkList || []).forEach((m) => { if (!m || !m.merk) return; const r = { merk: String(m.merk), satuan: String(m.satuan || ''), berat: Number(m.beratKarung) || 0, kg: Number(m.totalKg) || 0 };
      BK_TANDA_BUKU.forEach((t) => { if (m[t] !== undefined && m[t] !== null && m[t] !== '') r[t] = m[t]; }); beras.push(r); });
    else if (koleksi === 'produksiKemasan') kemasan.push({ nama: String(data.namaProduk || ''), ukuran: data.ukuranKemasan, unit: Number(data.jumlahUnit) || 0 });
  });
  const R = { versi: tahun === undefined || tahun === null ? 1 : 2, beras, kemasan };
  if (R.versi === 2) R.sebelum = bkPembandingSebelum(tbCutoff(Number(tahun)));
  return R;
}
/** Pembanding yang berdiri sendiri (catatan hidup per `c`, fungsi mesin yang sama dengan hitungSaldoTutup) — lihat ringkasPembuka. Nol / di bawah ambang tidak dibawa. */
function bkPembandingSebelum(c) {
  const merek = []; const K = hitungStokKarungPerMerk(c); Object.keys(K).sort().forEach((m) => { const kg = Number(K[m].sisaKg) || 0; if (Math.abs(kg) >= 0.01) merek.push({ merk: m, kg }); });
  const kemasan = []; const KM = hitungStokKemasan(c); Object.keys(KM).sort().forEach((k) => { const x = KM[k]; if (Math.abs(Number(x.sisaUnit) || 0) > 0.001) kemasan.push({ kunci: k, nama: String(x.namaProduk || ''), ukuran: x.ukuranKemasan, unit: Number(x.sisaUnit) || 0 }); });
  const orang = (L) => L.filter((x) => Math.abs(Number(x.sisa) || 0) >= 0.5).map((x) => ({ kunci: String(x.kunci), nama: String(x.nama || ''), sisa: Math.round(Number(x.sisa) || 0) }));
  const utangP = hitungUtangPemasok(c).map((px) => ({ pemasok: String(px.pemasok || ''), sisa: Math.round((Number(px.totalUtang) || 0) - (Number(px.tekor) || 0)) })).filter((x) => Math.abs(x.sisa) >= 0.5);
  return { merek, kemasan, piutang: orang(hitungPiutang(c)), kasbon: orang(hitungKasbon(c)), utangP };
}
/**
 * A7 · ringkasan tahun yang akan diarsip, disusun dari catatan hidup SEBELUM kunci: KR1 per pelanggan per hari (90 hari terakhir), laju pakai per hari (14),
 * riwayat pelanggan. Versi 2 (siap 2027 · P4, audit 8 Okt): + `pemasok` (jumlah kedatangan, 12 kedatangan terakhir, harga beli terakhir per merek — Belanja,
 * kartu & daftar pemasok) dan `pesananDatang` (pesanan belanja yang barangnya sudah datang ≤ 31 Des), keduanya dari bon-pemasok-logika (fungsi yang sama dengan
 * daftarPemasok / pesananSemua). Ringkasan versi 1 tanpa keduanya tetap terbaca (catatan hidup saja).
 */
export function ringkasTahun(tahun) { const c = tbCutoff(tahun); return Object.assign({ versi: 2, tahun, cutoff: c }, ringkasKreditLaju(c), { pelanggan: ringkasPelangganTahun(c), pemasok: ringkasPemasokTahun(c), pesananDatang: ringkasPesananTahun(c) }); }
/** Paket B · potret tahun dari catatan hidup TANPA menulis apa pun — langkah Kunci di LATIHAN menyusunnya juga, supaya kalau gagal ketahuan sebelum ritual. */
export function potretLatihan(tahun, kini) { try { const Pt = susunPotret(tahun, kini); return { ok: true, teks: ringkasPotret(Pt), ukuran: JSON.stringify(Pt).length }; } catch (e) { return { ok: false, teks: 'Potret ' + tahun + ' GAGAL disusun: ' + String((e && e.message) || e).slice(0, 160) + ' — kunci sungguhan akan DITOLAK. ' + bkKalimatTanpaPotret(tahun) }; } }
/** Paket C (8 Okt): yang bisa dikerjakan owner sendiri bila potret gagal disusun (sesudah 13 Okt tidak ada orang luar yang membetulkan kodenya). */
function bkKalimatTanpaPotret(tahun) {
  return 'Tutup lalu buka lagi aplikasinya dan ulangi sekali. Kalau tetap gagal: jangan dipaksakan — toko tetap boleh berjualan dengan buku ' + tahun + ' terbuka (Laporan & Pajak ' + tahun
    + ' tetap membaca catatannya); unduh cadangan (Menu › Sistem) dan simpan PDF Rekap pajak & Laporan Tahunan ' + tahun + ' untuk SPT. Kunci bulan ' + (tahun + 1) + ' menunggu sampai tutup buku ' + tahun + ' selesai.';
}
/** "Sesudah" dari susunan pembuka (belum ditulis): tiap baris dijumlah dari dokumennya; kas per tempat = titik yang akan ditulis. */
export function sesudahDariPembuka(P, sebelum) {
  const j = { beras: 0, kemasan: 0, bahan: 0, piutang: 0, kasbonK: 0, kasbonO: 0, amplop: 0, utangP: 0, utangO: 0, modal: 0, upah: 0 }; const kO = kunciPelanggan(NAMA_KASBON_OWNER);
  // A5 (siap 2027): baris pembuka beras yang MINUS dinilai mesin dengan modal 0 (hitungHppMerkDalamBatch: totalKg ≤ 0 → hpp 0) — sesudahnya bernilai 0, bukan minus
  P.dokumen.forEach(({ koleksi, data }) => { if (koleksi === 'batchMasuk') (data.merkList || []).forEach((m) => { j.beras += Number(m.totalKg) > 0 ? Number(m.subtotalHarga) || 0 : 0; }); else if (koleksi === 'produksiKemasan') j.kemasan += (Number(data.jumlahUnit) || 0) * (Number(data.hppPerUnit) || 0);
    else if (koleksi === 'modalOwner') j.modal += (data.tipe === 'setor' ? 1 : -1) * (Number(data.nominal) || 0);
    else if (koleksi === 'stokBahanKemasan' || koleksi === 'stokBahanLiteran') j.bahan += Number(data.hargaTotal) || 0; else if (koleksi === 'piutangMutasi') j.piutang += Number(data.nominal) || 0; else if (koleksi === 'kasbonMutasi') { if (kunciPelanggan(data.namaPegawai) === kO) j.kasbonO += Number(data.nominal) || 0; else j.kasbonK += Number(data.nominal) || 0; }
    else if (koleksi === 'amplopLaba') j.amplop += Number(data.nominal) || 0; else if (koleksi === 'utangPemasokMutasi') j.utangP += Number(data.nominal) || 0; else if (koleksi === 'utangOwnerMutasi') j.utangO += Number(data.nominal) || 0; });
  j.kemasan = Math.round(j.kemasan); j.amplopDok = j.amplop; ['laci', 'brankas', 'rekening', 'amplop'].forEach((k) => { j[k] = sebelum.kasAda ? Math.round(sebelum.K[k]) : null; });   // uang per tempat dibawa titik kas 31 Des, bukan dokumen
  // A6: upah yang belum dibayar dibawa hari kerja (absenKaryawan, tidak diarsip) + patokan "terakhir dibayar" di berita acara — sesudahnya dihitung ulang mesin upah
  j.modal = Math.round(j.modal); j.upah = P.upah ? P.upah.jumlah : null;
  return j;
}
/** Bandingkan sebelum vs sesudah baris demi baris; sama = tidak ada beda satu rupiah pun (kas yang tidak bisa dihitung dibandingkan null = null). */
export function bandingBuku(sebelum, sesudah) {
  // 39b no. 12: baris yang tidak bisa dihitung (uang per tempat, titik kas lebih muda dari 31 Des) BUKAN "sama" — dulu null = null lolos sebagai ✓
  const baris = bkBaris(sebelum).map((b) => { const s = sesudah ? (sesudah[b.id] === undefined ? null : sesudah[b.id]) : null; const ada = !!sesudah; const tahu = b.n !== null;
    const sama = !ada || (tahu && s !== null && Math.abs(b.n - s) < 0.5);
    // putaran 4 P4-5: sisi MESIN yang tidak bisa dihitung (periksa ulang sesudah kunci, titik kas sudah maju) juga '?' — belum bisa dihitung, bukan '≠'
    return { id: b.id, nama: b.nama, a: b.n, b: ada ? s : null, ada, sama, tahu, tanda: !ada ? '' : !tahu || s === null ? '?' : sama ? '✓' : '≠' }; });
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
  const S = bkSesudahKunci(tahun, H); const hitung = () => barisBuku(H.tanggal, H.tanggal);
  const B = S.susulan || S.sesudahKunci ? denganCacheSaring(S.nama, S.lolos, hitung) : hitung(); const o = {}; bkBaris(B).forEach((b) => { o[b.id] = b.n; });
  return Object.assign(bandingBuku({ harta: H.baris, utang: [] }, o), { susulan: S.susulan, sesudahKunci: S.sesudahKunci });
}
/**
 * Sanggahan Paket C (A9): patokan "hari ini" saat kunci / Lanjutkan — 14 baris pada hari itu + jam patokan + `ada` = catatan bertanggal 1 Jan … hari itu yang
 * SUDAH ada di perangkat (kunci 'koleksi|id'), supaya periksa ulang tahu mana yang baru masuk sesudahnya (karcis HP penjaga yang tertahan tanpa sinyal).
 */
function bkKoleksiHari(tahun) { return tbDaftarKoleksi(tahun).map((k) => k.koleksi).concat(['pindahUang', 'slipUpah']); }
const bkIdHari = (k, d) => k + '|' + String(k === 'biayaBulanan' ? (d.bulan || d.id) : d.id);
function bkHariIni(tahun, hari, jam) {
  const c = tbCutoff(tahun); const ada = [];
  bkKoleksiHari(tahun).forEach((k) => { const K = KOLEKSI.find((x) => x.nama === k); if (!K) return; cacheMentah(K.cache).forEach((d) => { const t = String((d && d.tanggal) || ''); if (d && !d.tutupBuku && t > c && t <= hari) ada.push(bkIdHari(k, d)); }); });
  return { tanggal: hari, jam: String(jam || ''), baris: bkBaris(barisBuku(hari, hari)).map((b) => ({ id: b.id, nama: b.nama, n: b.n })), ada: ada.sort() };
}
/**
 * Sanggahan Paket C (A9): catatan yang BUKAN bagian ritual tidak ikut sisi "sesudah" periksa ulang — dulu ikut terhitung, jadi "Stok beras TIDAK SAMA" dan kartu
 * pemeriksaan menyuruh membatalkan ritual yang benar (bertentangan dengan pita susulan):
 *   (1) SUSULAN — catatan bertanggal ≤ 31 Des yang masih di buku hidup (= yang disebut arsipBuku sesudah arsip; saldo pembuka tahun itu & pesanan yang belum
 *       tuntas tidak termasuk). Stok & bonnya sudah benar di buku tahun baru; pita susulan yang mengurusnya.
 *   (2) catatan bertanggal 1 Jan … hari patokan yang BELUM ada saat patokan diambil (`hariIni.ada`) dan jamnya SEBELUM jam patokan (ditulis sebelum kunci, baru
 *       masuk sesudahnya). Yang ditulis SESUDAH jam patokan tetap terhitung (berjualan selama arsip berjalan = dilarang daftar periksa). Tanpa `ada` (berita
 *       acara lama) = tidak disaring.
 * Hasil: { nama (koleksi), lolos (pakai denganCacheSaring), susulan, sesudahKunci } — jumlahnya dibawa hasil periksa (dibekukan) dan disebut kartu.
 */
function bkSesudahKunci(tahun, H) {
  const c = tbCutoff(tahun); const susul = {}; arsipBuku(tahun).daftar.forEach((x) => { susul[x.koleksi + '|' + String(x.id)] = true; });
  const ada = Array.isArray(H.ada) ? {} : null; if (ada) H.ada.forEach((k) => { ada[String(k)] = true; }); const jamP = String(H.jam || '');
  const sebab = (d, k) => { if (!d || (d.tutupBuku && Number(d.tahunDari) === Number(tahun))) return ''; const id = bkIdHari(k, d); if (susul[id]) return 'susulan';
    const t = String(d.tanggal || ''); if (!ada || ada[id] || !(t > c && t <= H.tanggal)) return '';
    return t < H.tanggal || (jamP && String(d.jam || '') < jamP) ? 'sesudahKunci' : ''; };
  const nama = bkKoleksiHari(tahun); const n = { susulan: 0, sesudahKunci: 0 };
  nama.forEach((k) => { const K = KOLEKSI.find((x) => x.nama === k); if (K) cacheMentah(K.cache).forEach((d) => { const s = sebab(d, k); if (s) n[s] += 1; }); });
  return { nama, lolos: (d, k) => !sebab(d, k), susulan: n.susulan, sesudahKunci: n.sesudahKunci };
}
/**
 * Putaran 3 UTBU-1: hasil periksa ulang DIBEKUKAN saat arsip habis (patokan & angka mesin per baris). "Selesai" & pita memakai hasil itu; dulu dihitung ulang
 * tiap kali terhadap patokan pagi, jadi penjualan Januari biasa sesudah arsip terbaca "TIDAK SAMA" dan tercatat permanen.
 * dokumen hanya bila berita acara masih 'terkunci', arsip sudah habis, dan (putaran 4 P4-1) perangkat ini pemegangnya (L = lokal() layar).
 * Putaran 4 P4-4: hasilnya dokumen TERSENDIRI tanpa kolom status — pengaturan/periksaArsip<tahun> (rules: owner saja, bukan titikKas = tidak dikunci; dibaca
 * hanya di sini) — bertanda percobaan. Dulu berita acara UTUH berstatus 'terkunci' ikut ditulis: kalau mendarat telat (sinyal putus) sesudah 'dibatalkan' /
 * 'selesai', statusnya mundur jadi 'terkunci' dan pita menyuruh meneruskan arsip.
 */
// tanda percobaan = jam paraf/kunci percobaan ini: sama di 'berjalan' & 'terkunci', baru tiap mulai lagi
const bkPercobaan = (a) => (a && a.paraf && a.paraf.pada ? String(a.paraf.pada) : '');
// A9 (siap 2027): `habis` = daftar arsip yang disusun saat mulai SUDAH pindah semua (uang.js jalankanBuku). Catatan bertanggal tahun itu yang masih ada sesudahnya
// datang SESUDAH daftar disusun (karcis HP yang tertahan offline) — bukan sisa arsip: hasil beku tetap ditulis, jumlahnya dicatat (`susulan`), dan catatan itu
// TIDAK ikut diarsip (stok & bonnya sudah benar di buku tahun baru; lihat susulanBuku).
export function susunPeriksaArsip(tahun, w, L, habis) {
  const PU = periksaUlangBuku(tahun); const a = bkAcara(tahun); const sisa = arsipBuku(tahun).n;
  if (!PU || !a || a.status !== 'terkunci' || (sisa && !habis) || bkBukanPemegang(tahun, L) || !bkPercobaan(a)) return { PU };
  const periksaArsip = { id: 'periksaArsip' + tahun, tahun, percobaan: bkPercobaan(a), pada: w.kini, tanggal: w.tanggal, baris: PU.baris.map((b) => ({ id: b.id, nama: b.nama, a: b.a, b: b.b })), susulan: sisa,
    tertinggal: bkTertinggalKini(tahun), sesudahKunci: PU.sesudahKunci || 0 };
  return { PU, dokumen: [{ koleksi: 'pengaturan', data: periksaArsip }] };
}
/** Arsip percobaan ini sudah habis sekali (hasil periksa ulang dibekukan, pengaturan/periksaArsip<tahun>) — catatan tahun itu yang tersisa = susulan. */
export function bkArsipHabis(tahun) { const a = bkAcara(tahun); const P = dokDiCache('pengaturan', 'periksaArsip' + tahun); return !!(a && P && bkPercobaan(a) && String(P.percobaan || '') === bkPercobaan(a)); }
/**
 * A9 (sanggahan paket A): catatan bertanggal tahun itu yang SENGAJA tidak diarsip — pesanan yang belum tuntas (tbDaftarKoleksi menyaringnya: masih berjalan,
 * bukan riwayat). Begitu tuntas (dibayar Januari / batal) ia masuk daftar arsip tahun itu; itu BUKAN catatan susulan — pesanan bukan uang & bukan stok sampai
 * notanya dicatat (notanya bertanggal hari bayar). Dicatat saat arsip habis (periksaArsip) dan saat selesai (berita acara); kunci = 'koleksi|id' seperti arsipBuku.
 */
const bkTertinggalKini = (tahun) => { const c = tbCutoff(tahun); return (ambilPesanan() || []).filter((p) => p && (p.tanggal || '') <= c && pesananBelumTuntas(p)).map((p) => KOLEKSI_PESANAN + '|' + p.id); };
function bkTertinggal(tahun) {
  const a = bkAcara(tahun); const P = dokDiCache('pengaturan', 'periksaArsip' + tahun); const o = {};
  const dariP = P && a && bkPercobaan(a) && String(P.percobaan || '') === bkPercobaan(a) && Array.isArray(P.tertinggal) ? P.tertinggal : [];
  dariP.concat(a && Array.isArray(a.tertinggal) ? a.tertinggal : []).forEach((k) => { o[String(k)] = true; }); return o;
}
/**
 * Hasil periksa ulang yang dipakai "selesai" & pita: yang dibekukan saat arsip habis PADA PERCOBAAN INI (tanda percobaan sama); belum ada / milik percobaan lain
 * (dibatalkan lalu dimulai lagi — LP3-Z1) = dihitung ulang sekarang.
 */
// Paket C (8 Okt): diekspor untuk kartu "Pemeriksaan sesudah tutup buku" (periksa-sesudah-logika.js) — hasil yang dibekukan membawa `beku` (tanggal & jam dibekukan)
export function bkPeriksaDipakai(tahun) {
  const a = bkAcara(tahun); const P = dokDiCache('pengaturan', 'periksaArsip' + tahun);
  if (!P || !Array.isArray(P.baris) || !bkPercobaan(a) || String(P.percobaan || '') !== bkPercobaan(a)) return periksaUlangBuku(tahun);
  const o = {}; P.baris.forEach((b) => { o[b.id] = b.b; }); return Object.assign(bandingBuku({ harta: P.baris.map((b) => ({ id: b.id, nama: b.nama, n: b.a })), utang: [] }, o), { beku: { tanggal: String(P.tanggal || ''), pada: String(P.pada || ''), susulan: Number(P.susulan) || 0, sesudahKunci: Number(P.sesudahKunci) || 0 } });
}
/** Yang diarsipkan saat kunci: seluruh dokumen tahun itu menurut tbDaftarKoleksi (sama dengan yang dihapus sistem lama). */
export function arsipBuku(tahun) { const d = tbDaftarKoleksi(tahun); const semua = []; d.forEach((k) => k.dok.forEach((dok) => semua.push({ koleksi: k.koleksi, id: k.koleksi === 'biayaBulanan' ? (dok.bulan || dok.id) : dok.id, data: dok })));
  // putaran 3 AAL2: batch PENANDA tutup buku tahun lalu (penandaBuku) diarsipkan PALING AKHIR — selama ia ada, pembuka bertahap tahun itu terlihat & ikut daftar.
  // Dulu ia bisa terarsip lebih dulu: arsip yang putus lalu dilanjutkan tidak melihat sisa pembukanya lagi → tertinggal di koleksi hidup selamanya.
  const tanda = (x) => !!(x.data && x.data.penandaBuku); const daftar = semua.filter((x) => !tanda(x)).concat(semua.filter(tanda));
  return { daftar, perKoleksi: d.map((k) => ({ koleksi: k.koleksi, label: k.label, n: k.dok.length })).filter((k) => k.n), n: daftar.length }; }
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
 * L = lokal() layar ({ idPerangkat, namaPerangkat }) — putaran 4 P4-1: berita acara mencatat perangkat ini sebagai pemegang.
 */
export function susunKunci(tahun, D, w, L) {
  const T = tahunBuku(ugKiniDari(w)); if (!T.bolehSungguhan) return { tolak: 'Tahun ' + tahun + ' belum lewat 31 Desember — hanya bisa latihan' };
  if (!D.paraf || !D.paraf.owner || !D.paraf.saksi) return { tolak: 'Paraf owner dan saksi dulu' };
  const tg = bkTertunda(tahun); if (tg) return { tolak: tg };
  // siap 2027 (pintu masuk, bukan hanya layar): hari tanpa tutup hari yang belum diputus (g1) dan stok minus / kelebihan bayar (g6) menolak kunci SUNGGUHAN.
  // Sanggahan 8 Okt (#111): kelengkapan hemat baca (g7) juga di PINTU — sesudah unduh cadangan, arsip, saldo & paraf berdua, potret & saldo pembuka disusun
  // dari seluruh buku perangkat ini; layar langkah 1 saja tidak cukup. L = lokal() layar (membawa `hemat` saat nyala); mati / tanpa L: g7 tidak ada (sama dulu)
  const G = gerbangBuku(tahun, ugKiniDari(w), L || {}, {}); const gTolak = G.daftar.filter((g) => (g.id === 'g1' || g.id === 'g6' || g.id === 'g7') && !g.ok);
  if (gTolak.length) return { tolak: 'Periksa dulu belum beres — ' + gTolak.map((g) => g.teks + ': ' + g.ket).join(' · ') };
  const T0 = titikTahun(tahun); const sebelum = barisBuku(T.cutoff, T.cutoff, T0); const P = pembukaBuku(tahun, w); const B = bandingBuku(sebelum, sesudahDariPembuka(P, sebelum));
  if (!B.semuaSama) return { tolak: B.ringkas + ': ' + B.beda.map((b) => b.nama).join(', ') };
  const A = arsipBuku(tahun); const K = sebelum.K; const hariIni = hariIniIso(ugKiniDari(w)); const HI = bkHariIni(tahun, hariIni, w.jam);
  // (d) titik kas tahun baru = hitungan 31 Des. Ditulis hanya bila patokan sekarang belum melewati 31 Des; kalau tutup hari Januari sudah memajukannya, titik itu
  // (hitungan fisik yang lebih baru) dipertahankan — gerakan ≤ 31 Des yang diarsipkan tidak menyentuhnya.
  const titik = K.ada && T0 && T0.dari === 'titikKas' ? { id: 'titikKas', tanggal: T.cutoff, laci: Math.round(K.laci), rekening: Math.round(K.rekening), amplop: Math.round(K.amplop), brankas: Math.round(K.brankas), diubahPada: w.kini } : null;
  const acara = Object.assign({}, T.acara || {}, { id: String(tahun), tahun, mode: 'sungguhan', status: 'terkunci', saksi: D.saksi || '', paraf: { owner: true, saksi: true, pada: w.kini }, langkah: Object.assign({}, D.langkah || {}, { kunci: w.kini }), cadangan1: D.cadangan1 || '', arsipNama: D.arsipNama || '', nArsip: A.n, arsipPerKoleksi: A.perKoleksi, nPembuka: P.dokumen.length,
    sebelum: B.baris.map((b) => ({ id: b.id, nama: b.nama, n: b.a })), modal: sebelum.modal, labaTinggal: sebelum.labaTinggal, tanggal: w.tanggal, jam: w.jam, titikDitulis: !!titik, titikSebelum: ambilTitikKas() || null,
    titikTahun: T0, hariIni: HI,
    // siap 2027: putusan hari tanpa tutup hari (A1) · upah yang belum dibayar per 31 Des & patokan "terakhir dibayar" sistem lama (A6) ikut berita acara
    putusanHari: G.hari.map((h) => ({ iso: h.iso, nNota: h.nNota, alasan: h.putusan ? String(h.putusan.alasan).slice(0, 120) : '' })),
    upah: P.upah.orang.map((o) => ({ nama: o.nama, kunci: o.kunci, upah: o.upah, mulai: o.mulai, penuh: o.penuh, setengah: o.setengah, lama: o.lama })) });
  // §8 no. 8: berita acara percobaan yang dibatalkan dipakai ulang — tanggal pembatalan lamanya dibuang, supaya pembatalan berikutnya mencatat tanggalnya sendiri
  delete acara.pembuka; delete acara.penanda; delete acara.dariStatus; delete acara.dibatalkanPada; delete acara.dibatalkanTanggal;
  // putaran 4 P4-1: PEMEGANG = perangkat yang memulai percobaan ini (juga percobaan ulang sesudah dibatalkan) — pemegang & ambil alih (P4-2) percobaan lama tidak terbawa
  delete acara.pemegang;
  delete acara.pemegangLama; delete acara.diambilAlihPada; delete acara.diambilAlihTanggal; delete acara.diambilAlihJam;
  const pg = bkPerangkatIni(L); if (pg) acara.pemegang = pg;
  const penanda = (titik ? [{ koleksi: 'pengaturan', data: titik }] : []).concat([{ koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: tahun, padaTanggal: w.tanggal } }]);
  // §8 no. 1: semua pembuka ber-`bertahap`; PENANDA yang terbaca HP staf = batch pembuka ber-`penandaBuku` (toko.js pembukaBerlaku). Tanpa stok beras → batch
  // kosong (merkList []) khusus penanda, supaya pembuka lain tetap punya penanda.
  P.dokumen.forEach((x) => { x.data.bertahap = true; });
  let tanda = P.dokumen.find((x) => x.koleksi === 'batchMasuk');
  if (!tanda) { tanda = { koleksi: 'batchMasuk', data: { id: w.idUnik(), tanggal: P.tglBuka, pemasok: 'TUTUP BUKU ' + tahun, biayaBongkar: 0, stokAwal: true, merkList: [], tutupBuku: true, tahunDari: tahun, bertahap: true } }; P.dokumen.push(tanda); acara.nPembuka = P.dokumen.length; }
  tanda.data.penandaBuku = true;
  // A7 (siap 2027): ringkasan tahun ini (KR1 90 hari, laju pakai 14 hari, riwayat per pelanggan; P4: pemasok & pesanan belanja) menumpang batch penanda —
  // terlihat bersamaan dengan saldo pembuka di semua perangkat (toko.js ringkasArsip), hilang bersama penanda bila dibatalkan
  tanda.data.ringkasTahun = ringkasTahun(tahun);
  // PAKET C (8 Okt): ringkasan saldo pembuka per buku & kemasan di berita acara — pembanding kartu "Pemeriksaan sesudah tutup buku"
  acara.pembukaRingkas = ringkasPembuka(P.dokumen, tahun);
  // PAKET B (siap 2027): POTRET tahun ini (pajak & omzet, laba-rugi, biaya per jenis, arus kas, neraca akhir bulan per bulan; omzet per hari) di berita acara —
  // Laporan, Pajak & Dasbor membacanya sesudah arsip (toko.js potretBulan). Gagal disusun = kunci DITOLAK: tanpa potret, layar tahun ini jadi Rp0 bertanda FINAL.
  try { acara.potret = susunPotret(tahun, ugKiniDari(w)); } catch (e) { return { tolak: 'Potret ' + tahun + ' gagal disusun (' + String((e && e.message) || e).slice(0, 160) + ') — tahun TIDAK dikunci, supaya Laporan & Pajak ' + tahun + ' tidak jadi Rp0 sesudah arsip. Tidak ada yang ditulis. ' + bkKalimatTanpaPotret(tahun) }; }
  // (a) tiap dokumen pembuka satu kelompok (urutan pembukaBuku); batch penanda + penanda + berita acara terkunci = kelompok TERAKHIR, jadi selalu di kiriman terakhir
  // v7 (K8): ada bulan terkunci → PINTU dibuka di kiriman PERTAMA (rules menilai pintu sesudah batch, bersama berita acaranya); biaya pintu ikut dihitung
  const pintu = T.perluPintu ? bkPintuDok(tahun, w) : null;
  const Pt = kpPotong((pintu ? [{ dokumen: [pintu] }] : []).concat(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] })), [{ dokumen: [tanda].concat(penanda, [{ koleksi: 'tutupBukuAcara', data: acara }]) }]), dokDiCache, ugKiniDari(w),
    { sampai: kunciSampai(), pintu: bkPintuPakai(pintu, w) });
  if (Pt.tolak) return { tolak: Pt.tolak };
  acara.rencana = { dibuat: w.kini, n: Pt.potongan.length, kiriman: Pt.potongan.map((p, i) => ({ ke: i + 1, get: p.get, dok: p.dokumen.map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })) })) };
  // sanggahan rules 7 Okt: pintu hanya dibuka di atas berita acara yang SUDAH ada di server → berita acara 'berjalan' dikirim sendirian lebih dulu
  if (pintu) acara.rencana.acaraDulu = true;
  const berjalan = Object.assign({}, acara, { status: 'berjalan', pembuka: P.dokumen, penanda });
  const kiriman = bkKirimanDari(berjalan, pintu ? [pintu] : []);
  return { kiriman, dokumen: [].concat.apply([], kiriman.map((k) => k.dokumen)), arsip: A.daftar, acara, sebelum, banding: B, titik, titikTahun: T0,
    patch: { kabar: 'Tahun ' + tahun + ' DIKUNCI: ' + P.dokumen.length + ' dokumen saldo pembuka ditulis dalam ' + kiriman.length + ' kiriman, ' + ANGKA(A.n) + ' dokumen tahun ' + tahun + ' dipindah ke arsip (tidak dihapus); potret ' + tahun + ' tersimpan di berita acara. Selesaikan dengan cadangan sesudahnya.', kabarAwas: false } };
}
const bkAcara = (tahun) => ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null;
/** Access call server per catatan arsip, termasuk salinannya (0 bulan bebas / 2 bulan lampau / 5 lewat pintu — kunci-periode.js; pintu dianggap terbuka bila ada bulan terkunci) — dasar perkiraan kiriman & kuota. */
function bkBiayaArsip(daftar, ops, kini, tahun) { const s = kunciSampai(); const P = s ? { tahun, sampai: Infinity } : null; return daftar.map((x) => kpNilaiKiriman([ops(x)], s, kini, P).perluGet); }
const bkKirimanArsip = (tahun, daftar) => kpPecahBiaya(bkBiayaArsip(daftar, (x) => ({ koleksi: x.koleksi, id: x.id, lama: x.data, hapus: true, arsip: true }), new Date(Date.now()), tahun), KP_BATAS_GET, KP_BATAS_GET).length;
/** (b) Kiriman dari berita acara 'berjalan' — sama persis dengan yang disusun saat mulai (id tetap), jadi bisa dilanjutkan dari perangkat mana pun.
 *  rencana.acaraDulu (ada bulan terkunci): kiriman 1 = berita acara 'berjalan' SENDIRIAN, rencana kiriman sesudahnya (pintu di yang pertama). */
function bkKirimanDari(a, ekstra) {
  const peta = {}; (a.pembuka || []).concat(a.penanda || [], ekstra || []).forEach((x) => { peta[x.koleksi + '|' + String(x.data.id)] = x; });
  const kunci = Object.assign({}, a, { status: 'terkunci' }); delete kunci.pembuka; delete kunci.penanda; const n = a.rencana.kiriman.length;
  const dulu = !!a.rencana.acaraDulu; const N = n + (dulu ? 1 : 0);
  const out = a.rencana.kiriman.map((k, i) => {
    const dokumen = k.dok.map((d) => (d.koleksi === 'tutupBukuAcara' ? { koleksi: 'tutupBukuAcara', data: kunci } : peta[d.koleksi + '|' + d.id]));
    if (i === 0 && n > 1 && !dulu) dokumen.unshift({ koleksi: 'tutupBukuAcara', data: a });
    return { ke: i + 1 + (dulu ? 1 : 0), total: N, get: k.get, dokumen, pembuka: dokumen.filter((x) => x.data && x.data.tutupBuku).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })), penanda: k.dok.some((d) => d.koleksi === 'tutupBukuAcara') };
  });
  return dulu ? [{ ke: 1, total: N, get: 0, dokumen: [{ koleksi: 'tutupBukuAcara', data: a }], pembuka: [], penanda: false, acaraDulu: true }].concat(out) : out;
}
/**
 * §8 no. 4: catatan tutup buku tahun itu yang masih MENUNGGU SERVER di perangkat ini (toko.js dokTertunda) — berita acara, saldo pembuka, penanda (titik kas,
 * pengaturan/tutupBuku). Selama ada, kemajuan = fase 'tunggu' (bukan "n dari N masuk" / "terkunci"), Lanjutkan & Batalkan menolak: server bisa menolaknya nanti.
 */
function bkTunda(tahun) {
  const a = bkAcara(tahun); let n = a && dokTertunda('tutupBukuAcara', String(a.id || tahun)) ? 1 : 0;
  bkPembukaTahun(tahun).forEach((x) => { if (dokTertunda(x.koleksi, x.id)) n += 1; }); ['titikKas', 'tutupBuku'].forEach((id) => { if (dokTertunda('pengaturan', id)) n += 1; });
  // putaran 3 AAL5: hapus yang menunggu server (tarik saldo pembuka saat pembatalan) — dokumennya sudah tak ada di cache, dihitung dari kiriman perangkat ini
  Object.keys(KOLEKSI_CACHE).forEach((c) => { n += hapusTertunda(KOLEKSI_CACHE[c]); });
  return n;
}
/**
 * Putaran 3 AAL4: Lanjutkan & Batalkan hanya dari data SERVER. Tanpa internet, atau berita acara / pengaturan masih salinan perangkat (belum dijawab server),
 * kiriman disusun dari keadaan basi lalu mendarat belakangan (dulu: 'selesai' mundur jadi 'terkunci', titik kas Januari ditimpa di semua HP). L = lokal() layar. '' = boleh.
 */
export function bkSambungan(L) {
  const basi = ['tutupBukuAcara', 'pengaturan'].some((k) => koleksiDariCache(k));
  // #111 hemat baca nyala: sisa arsip, saldo pembuka & pengembalian disusun dari SELURUH buku — selama tutup buku berjalan semua koleksi didengar penuh, dan
  // sampai pendengar penuh itu terkini (mis. aplikasi baru dibuka di tengah ritual) bukunya masih simpanan perangkat. SATU sumber: hemat-baca.js. Mati: tidak ada
  const hb = !(L && L.offline) && !basi && L && L.hemat && L.hemat.nyala ? hbKalimatBelum(L.hemat.belumLengkap, null) : '';
  if (hb) return 'Tutup buku: ' + hb + ' — Lanjutkan atau Batalkan sesudah datanya lengkap.';
  if (!(L && L.offline) && !basi) return '';
  return 'Tutup buku: ' + (L && L.offline ? 'perangkat ini tanpa internet' : 'data tutup buku di perangkat ini belum dijawab server (bisa basi)') + ' — sambungkan internet dulu, tunggu data terbaru, baru Lanjutkan atau Batalkan.';
}
/**
 * Putaran 4 P4-1 (owner 1 Okt: SATU PERANGKAT SAJA): tutup buku yang 'berjalan' / 'terkunci' / 'membatalkan' hanya DITULIS dari pemegangnya — perangkat yang
 * memulainya (berita acara `pemegang` = { id, nama }). Dulu kiriman yang tertahan di perangkat A mendarat sesudah perangkat B membatalkan / menyelesaikan /
 * melanjutkan, lalu menimpanya. L = lokal() layar ({ idPerangkat, namaPerangkat }). '' = boleh. Berita acara tanpa pemegang (uji / latihan lama) = boleh dari mana saja.
 */
export function bkBukanPemegang(tahun, L) {
  const a = bkAcara(tahun); const p = a && a.pemegang; if (!p || !p.id || ['berjalan', 'terkunci', 'membatalkan'].indexOf(a.status) < 0) return '';
  if (L && L.idPerangkat && String(L.idPerangkat) === String(p.id)) return '';
  return 'Tutup buku ' + tahun + ' sedang dikerjakan di ' + (p.nama || p.id) + '. Lanjutkan atau batalkan dari perangkat itu.';
}
const bkPerangkatIni = (L) => (L && L.idPerangkat ? { id: String(L.idPerangkat), nama: String(L.namaPerangkat || L.idPerangkat) } : null);
/**
 * Putaran 4 P4-2: AMBIL ALIH — jalan keluar bila perangkat pemegang rusak / hilang / datanya terhapus (idPerangkat disimpan di localStorage: hapus data peramban =
 * id baru). Hanya bila SEMUA: perangkat ini tersambung & data tutup buku (juga denyut perangkat) dari server, antrean perangkat ini kosong, berita acara tidak
 * berubah ≥ 60 menit, dan pemegang tidak berdenyut 15 menit terakhir. Dua ketukan: yang pertama = kalimat peringatan (yakin = ketukan kedua).
 * Hasil: berita acara yang sama dengan pemegang baru + pemegangLama & jam ambil alih — perangkat lama sesudahnya ditolak seperti perangkat lain.
 */
export function susunAmbilAlih(tahun, L, w, yakin) {
  const a = bkAcara(tahun); const p = a && a.pemegang; const ini = bkPerangkatIni(L); const nm = p ? String(p.nama || p.id) : '';
  if (!p || !p.id || ['berjalan', 'terkunci', 'membatalkan'].indexOf(a.status) < 0) return { tolak: 'Tidak ada tutup buku ' + tahun + ' yang dipegang perangkat lain' };
  if (!ini) return { tolak: 'Perangkat ini belum dikenali — muat ulang aplikasi, lalu coba lagi' };
  if (ini.id === String(p.id)) return { tolak: 'Tutup buku ' + tahun + ' memang dipegang perangkat ini — tidak ada yang diambil alih' };
  const sb = bkSambungan(L); if (sb) return { tolak: sb };
  if (koleksiDariCache('perangkatStatus')) return { tolak: 'Ambil alih: denyut perangkat di perangkat ini belum dijawab server (bisa basi) — tunggu data terbaru dulu.' };
  const nA = ((L && L.antre) || []).length + (Number(L && L.menunggu) || 0);
  if (nA) return { tolak: 'Ambil alih ditolak: ' + nA + ' catatan perangkat ini belum diakui server — tunggu antrean kosong dulu (Menu › Sistem › Perangkat).' };
  const t = Date.parse(w.kini); const ubah = Date.parse(a.diubahPada || ''); const menit = isFinite(ubah) ? Math.floor((t - ubah) / 60000) : null;
  if (menit === null || menit < 60) return { tolak: 'Ambil alih ditolak: berita acara tutup buku ' + tahun + (menit === null ? ' tidak mencatat kapan terakhir berubah' : ' baru berubah ' + Math.max(0, menit) + ' menit lalu') + ' — ' + nm + ' mungkin masih bekerja. Tunggu sampai 60 menit tanpa perubahan.' };
  const dy = cacheMentah('perangkat').filter((d) => d && (String(d.id) === String(p.id) || String(d.id).indexOf(String(p.id) + '~') === 0)).map((d) => Date.parse(d.pada || '')).filter((x) => isFinite(x));
  const terakhir = dy.length ? Math.max.apply(null, dy) : null;
  if (terakhir !== null && t - terakhir < 15 * 60000) return { tolak: 'Ambil alih ditolak: ' + nm + ' masih berdenyut ' + Math.max(0, Math.round((t - terakhir) / 60000)) + ' menit lalu — lanjutkan atau batalkan dari perangkat itu.' };
  if (!yakin) return { perluYakin: true, tolak: 'Ambil alih tutup buku ' + tahun + ' dari ' + nm + '? Kalau HP lama masih menyimpan kiriman yang belum terkirim, kiriman itu bisa masuk belakangan — pastikan HP lama mati / datanya dihapus. Ketuk "ambil alih" sekali lagi.' };
  const baru = Object.assign({}, a, { pemegang: ini, pemegangLama: { id: String(p.id), nama: nm }, diambilAlihPada: w.kini, diambilAlihTanggal: w.tanggal, diambilAlihJam: w.jam });
  return { dokumen: [{ koleksi: 'tutupBukuAcara', data: baru }], patch: { kabar: 'Tutup buku ' + tahun + ' sekarang dipegang perangkat ini (' + ini.nama + '). ' + nm + ' tidak bisa melanjutkan atau membatalkan lagi.', kabarAwas: false } };
}
const bkKalimatTunda = (tahun, n) => 'Tutup buku ' + tahun + ': ' + n + ' catatan di perangkat ini masih menunggu server (belum diakui, belum dihitung masuk). Jangan tutup aplikasi; tunggu sinyal sampai antrean kosong (Menu › Sistem › Perangkat), baru Lanjutkan atau Batalkan.';
/** Tahun lama berubah sejak rencana dibuat? (pembuka yang sudah masuk tidak terlihat mesin → 31 Des dihitung ulang dari catatan asli dengan patokan kas yang sama) */
function bkBerubah(a) {
  const c = tbCutoff(Number(a.tahun)); const S = barisBuku(c, c, a.titikTahun || null); const lama = {}; (a.sebelum || []).forEach((b) => { lama[b.id] = b.n; });
  const beda = bkBaris(S).filter((b) => b.id in lama).filter((b) => (lama[b.id] === null || lama[b.id] === undefined) !== (b.n === null) || (b.n !== null && Math.abs(b.n - lama[b.id]) >= 0.5));
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
export function lanjutBuku(tahun, L) {
  const a = bkAcara(tahun); if (!a || a.status !== 'berjalan' || !a.rencana || !Array.isArray(a.pembuka)) return { tolak: 'Tidak ada tutup buku ' + tahun + ' yang sedang berjalan' };
  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };
  const nT = bkTunda(tahun); if (nT) return { tolak: bkKalimatTunda(tahun, nT) };
  const ub = bkBerubah(a); if (ub) return { tolak: ub };
  const masuk = a.pembuka.filter((x) => !!dokDiCache(x.koleksi, x.data.id)).length;
  // §8 no. 5: patokan pemeriksaan ulang (12 baris HARI INI, pembuka masih tersembunyi) diambil tepat sebelum kiriman pertama sesi ini — dulu saat mulai, jadi
  // penjualan di antara kiriman 1 dan Lanjutkan (hari yang sama) membuat periksa ulang berbunyi palsu
  const hari = hariIniIso(new Date(Date.now())); const HI = bkHariIni(tahun, hari, jamKini(new Date(Date.now())));
  const kunci = Object.assign({}, a, { status: 'terkunci', hariIni: HI }); delete kunci.pembuka; delete kunci.penanda;
  const tanda = a.pembuka.filter((x) => x.data && x.data.penandaBuku); const belumAda = a.pembuka.filter((x) => tanda.indexOf(x) < 0 && !dokDiCache(x.koleksi, x.data.id));
  const akhir = bkTitikKini({ dokumen: tanda.concat(a.penanda || [], [{ koleksi: 'tutupBukuAcara', data: kunci }]) }, tahun);
  // v7: pintu yang belum terbuka / tinggal < 12 jam dibuka lagi di kiriman lanjutan PERTAMA
  const wP = { kini: new Date(Date.now()).toISOString(), tanggal: hari, jam: '' }; const pintu = (susunPintu(tahun, wP).dokumen || [])[0] || null;
  const Pt = kpPotong((pintu ? [{ dokumen: [pintu] }] : []).concat(belumAda.map((x) => ({ dokumen: [x] })), [akhir]), dokDiCache, new Date(Date.now()), { sampai: kunciSampai(), pintu: bkPintuPakai(pintu, wP) }); if (Pt.tolak) return { tolak: Pt.tolak };
  // putaran 3 AAL7: satu satuan — kiriman LANJUTAN dinomori 1..n menurut pecahan SEKARANG (nomor rencana saat mulai tidak cocok lagi sesudah pecah ulang);
  // tiap kiriman membawa jumlah saldo pembuka yang sudah masuk sebelum ia (pita juga menghitung saldo pembuka, bukan kiriman)
  let m = masuk; const belum = Pt.potongan.map((p, i) => { const pembuka = p.dokumen.filter((x) => x.data && x.data.tutupBuku).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) }));
    const k = { ke: i + 1, total: Pt.potongan.length, lanjutan: true, masuk: m, dari: a.pembuka.length, get: p.get, dokumen: p.dokumen, pembuka, penanda: i === Pt.potongan.length - 1 }; m += pembuka.length; return k; });
  const titik = akhir.dokumen.find((x) => x.koleksi === 'pengaturan' && String(x.data.id) === 'titikKas');
  return { kiriman: belum, sudah: masuk, total: a.pembuka.length, titik: titik ? titik.data : null };
}
/**
 * Putaran 3 AAL1: arsip yang sedang berjalan (daftarnya dihitung sekali) berhenti di antara potongan bila berita acara tahun itu di cache bukan lagi 'terkunci'
 * — mis. dibatalkan dari perangkat lain; dulu sisa catatan tahun itu tetap tersapu ke arsip SESUDAH "dibatalkan", tanpa pita. '' = boleh lanjut.
 * Putaran 4 P4-1: juga berhenti bila perangkat ini bukan (lagi) pemegangnya (L = lokal() layar) — mis. sesudah diambil alih perangkat lain.
 */
export function arsipBerhentiBuku(tahun, L) {
  const a = bkAcara(tahun); if (a && a.status === 'terkunci') return bkBukanPemegang(tahun, L);
  const kata = { membatalkan: 'sedang dibatalkan', dibatalkan: 'sudah dibatalkan', selesai: 'sudah selesai' }[a && a.status] || 'tidak terkunci lagi';
  return 'Arsip ' + tahun + ' dihentikan: tutup buku ' + tahun + ' ' + kata + ' (dari perangkat lain) — catatan ' + tahun + ' yang tersisa tidak dipindah ke arsip. Ikuti pita tutup buku.';
}
/**
 * Putaran 3 AAL1 (susulan): potongan arsip yang sudah terkirim sebelum pembatalan terlihat bisa mendarat SESUDAH perangkat lain membaca arsipnya untuk
 * dikembalikan → perangkat yang mengarsip mengembalikan potongan terakhirnya sendiri, HANYA bila tahun itu sedang / sudah dibatalkan (selesai = tidak).
 * daftar = potongan arsipBuku ({ koleksi, id, data }) → bentuk pulihkanArsip.
 */
export function arsipBalikBuku(tahun, daftar) { const a = bkAcara(tahun); if (!a || (a.status !== 'membatalkan' && a.status !== 'dibatalkan')) return [];
  return (daftar || []).map((x) => ({ koleksi: x.koleksi, idAsli: x.id, dok: x.data })); }
/**
 * TRV6-EKOR-1 (tinjauan rules v6): EKOR pembatalan — kembalikan arsip, baca arsip ulang, kembalikan sisanya, tulis 'dibatalkan' — hanya selama berita acara
 * tahun itu di cache masih 'membatalkan' PERCOBAAN INI (paraf.pada = percobaan, dari susunBatal) dan perangkat ini pemegangnya. Dulu penjaga pemegang hanya
 * per kiriman tarik: HP yang beku di tengah pengembalian lalu hidup lagi sesudah diambil alih (perangkat lain menuntaskan pembatalan, menutup buku lagi sampai
 * selesai) mengembalikan SELURUH arsip tahun itu ke buku hidup → angka DOBEL tanpa pita (v6 hanya menolak 'dibatalkan'-nya). L = lokal() layar. '' = boleh lanjut.
 */
export function pulihBerhentiBuku(tahun, L, percobaan) {
  const a = bkAcara(tahun); if (a && a.status === 'membatalkan' && bkPercobaan(a) === String(percobaan || '') && !bkBukanPemegang(tahun, L)) return '';
  const p = (a && a.pemegang) || {};
  const kata = { berjalan: 'sedang ditutup lagi', terkunci: 'sudah dikunci lagi', selesai: 'sudah ditutup lagi sampai selesai', dibatalkan: 'sudah dibatalkan tuntas', membatalkan: 'sedang dibatalkan' + (p.nama ? ' di ' + p.nama : '') }[a && a.status] || 'berubah';
  // tab / jendela lain di perangkat yang SAMA (pemegang = perangkat ini) bukan "perangkat lain" — jangan membuat owner mengira ada HP lain ikut campur
  const asal = p.id && L && String(L.idPerangkat || '') === String(p.id) ? 'jendela lain di perangkat ini' : 'perangkat lain';
  return 'Pembatalan tutup buku ' + tahun + ' dihentikan: tutup bukunya sudah diubah dari ' + asal + ' (' + kata + ') — sisa arsip ' + tahun + ' tidak dikembalikan dari perangkat ini. Ikuti pita tutup buku.';
}
/**
 * TRV6-EKOR-1: potongan pengembalian yang terlanjur mendarat saat ekor pembatalan berhenti diarsipkan LAGI hanya bila berita acara sekarang percobaan LAIN yang
 * terkunci / selesai (tahun itu sedang / sudah diarsip percobaan baru — catatan itu tempatnya di arsip). Percobaan yang sama, atau berjalan / membatalkan /
 * dibatalkan = tidak (catatan itu memang tempatnya di buku hidup). daftar = potongan bentuk pulihkanArsip ({ koleksi, idAsli, dok }) → bentuk arsipkanDokumen.
 */
export function pulihBalikBuku(tahun, daftar, percobaan) { const a = bkAcara(tahun);
  if (!a || (a.status !== 'terkunci' && a.status !== 'selesai') || bkPercobaan(a) === String(percobaan || '')) return [];
  return (daftar || []).map((x) => ({ koleksi: x.koleksi, id: x.idAsli, data: x.dok })); }
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
  const kal = bkKalimatPeriksa(bkPeriksaDipakai(tahun)); const S = susulanBuku(tahun);
  return 'Tahun ' + tahun + ' terkunci dan arsipnya habis. ' + (kal ? 'AWAS: ' + kal + ' — periksa dulu; "selesai" butuh ketukan kedua.' : 'Diperiksa ulang dari mesin: semua baris sama — unduh cadangan sesudahnya & selesai.') + (S ? ' AWAS: ' + S.teks : '');
}
/** (c) Kemajuan untuk layar K6 & Beranda: tutup buku / pembatalan yang belum tuntas (null = tidak ada). */
export function kemajuanBuku() {
  const a = ambilTutupBukuAcara().filter((x) => x && (x.status === 'berjalan' || x.status === 'membatalkan' || x.status === 'terkunci' || (x.status === 'dibatalkan' && bkPembukaTahun(Number(x.tahun)).length))).sort((p, q) => Number(q.tahun) - Number(p.tahun))[0];
  if (!a) return null; const tahun = Number(a.tahun);
  // §8 no. 4: ada kiriman yang belum diakui server di perangkat ini → bukan "n dari N masuk" / "terkunci" (berita acara di cache bisa versi yang belum diterima)
  const nT = bkTunda(tahun); if (nT) return { tahun, fase: 'tunggu', tunda: nT, teks: bkKalimatTunda(tahun, nT) };
  // putaran 3 AAL7: pita menghitung SALDO PEMBUKA yang sudah masuk (dokumen), bukan kiriman rencana — sesudah pecah ulang nomornya tidak cocok lagi
  if (a.status === 'berjalan') { const P = a.pembuka || []; const sudah = P.filter((x) => !!dokDiCache(x.koleksi, x.data.id)).length;
    return { tahun, fase: 'pembuka', sudah, total: P.length, teks: 'Tutup buku ' + tahun + ': ' + sudah + ' dari ' + P.length + ' saldo pembuka sudah masuk. Tahun ' + tahun + ' MASIH TERBUKA (saldo pembuka yang sudah masuk belum dihitung) sampai kiriman terakhir masuk — lanjutkan atau batalkan.' }; }
  // putaran 3 AAL3: kiriman penanda yang tertahan di antrean perangkat lain bisa mendarat SESUDAH pembatalan tuntas → 'terkunci' lagi dengan saldo pembuka tidak
  // lengkap. Itu bukan "lanjutkan arsip" (catatan tahun itu akan dipindah, angka salah) — batalkan (susunBatal menarik sisanya), lalu mulai lagi.
  if (a.status === 'terkunci') { const adaP = bkPembukaTahun(tahun).length; if (adaP < Number(a.nPembuka) && bkEra() === tahun) return { tahun, fase: 'rusak', sisaPembuka: adaP, teks: 'Tutup buku ' + tahun + ' tidak utuh: berita acaranya terkunci, tapi saldo pembukanya cuma ' + adaP + ' dari ' + a.nPembuka + ' (ada kiriman yang ditolak server, atau masuk terlambat dari perangkat lain sesudah pembatalan). Angka toko SALAH sampai dibereskan — arsip JANGAN diteruskan; ketuk "batalkan", lalu mulai lagi.' }; }
  // A9 (siap 2027): sesudah arsip percobaan ini habis sekali, catatan tahun itu yang tersisa = SUSULAN (datang sesudah penanda) — bukan sisa arsip, tidak diarsip
  if (a.status === 'terkunci') { const A0 = bkArsipHabis(tahun) ? null : arsipBuku(tahun); const sisa = A0 ? A0.n : 0; const total = Number(a.nArsip) || sisa;
    return sisa ? { tahun, fase: 'arsip', sudah: total - sisa, total, sisa, teks: 'Tahun ' + tahun + ' terkunci; ' + ANGKA(sisa) + ' catatan ' + tahun + ' belum pindah ke arsip (' + bkKirimanArsip(tahun, A0.daftar) + ' kiriman lagi). Sampai habis, stok, piutang & utang terhitung DOBEL — lanjutkan arsip atau batalkan.' }
      : { tahun, fase: 'selesaikan', sudah: total, total, sisa: 0, teks: bkTeksSelesaikan(tahun) }; }
  const sisaP = bkPembukaTahun(tahun).length;
  return { tahun, fase: 'batal', sisaPembuka: sisaP, teks: 'Pembatalan tutup buku ' + tahun + ' belum selesai: ' + sisaP + ' saldo pembuka belum ditarik' + (a.dariStatus === 'terkunci' ? ' dan arsip belum semua dikembalikan' : '') + ' — lanjutkan pembatalan.' };
}
/**
 * Batalkan tutup buku (berjalan, atau terkunci sebelum selesai): BERTAHAP juga — tarik saldo pembuka per ≤ 18 pemeriksaan, kembalikan arsip, era mundur.
 * kiriman 1 = berita acara 'membatalkan' (+ era & titik kas bila tahun sempat terkunci) + potongan tarik pertama — pembuka langsung tak terlihat mesin.
 * Sesudah semua kiriman & pengembalian arsip: `akhir` = berita acara 'dibatalkan'. Bisa diulang: yang sudah ditarik/dikembalikan tidak diulang.
 * arsipDok = hasil bacaArsipTahun (sisa yang belum dikembalikan). L = lokal() layar (putaran 4 P4-1: hanya dari perangkat pemegang).
 */
export function susunBatal(tahun, arsipDok, w, L) {
  const acara = bkAcara(tahun); const hapus = bkPembukaTahun(tahun); const nT = bkTunda(tahun); if (nT) return { tolak: bkKalimatTunda(tahun, nT) };
  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };
  if (!acara || (['terkunci', 'berjalan', 'membatalkan'].indexOf(acara.status) < 0 && !(acara.status === 'dibatalkan' && hapus.length))) return { tolak: 'Tahun ' + tahun + ' tidak sedang terkunci — tidak ada yang dibatalkan' };
  const dari = acara.status === 'membatalkan' || acara.status === 'dibatalkan' ? (acara.dariStatus || 'terkunci') : acara.status;
  const batal = Object.assign({}, acara, { status: 'membatalkan', dariStatus: dari, dibatalkanPada: acara.dibatalkanPada || w.kini, dibatalkanTanggal: acara.dibatalkanTanggal || w.tanggal }); delete batal.pembuka; delete batal.penanda;
  // putaran 4 BP4R-2: pembatalan lanjutan dari 'dibatalkan' (sisa saldo pembuka mendarat belakangan; tidak dijaga pemegang) dipegang perangkat yang memulainya —
  // perangkat yang boleh memulai juga boleh menyelesaikan (dulu pemegang lama tersalin → perangkat ini ditolak dirinya sendiri di kiriman ke-2)
  if (acara.status === 'dibatalkan') { const pg = bkPerangkatIni(L); if (pg) batal.pemegang = pg; }
  const awal = [{ koleksi: 'tutupBukuAcara', data: batal }]; let titik = null;
  if (acara.status === 'terkunci') {
    const eraLama = bkEraTanpa(tahun); awal.push({ koleksi: 'pengaturan', data: { id: 'tutupBuku', tahunDitutup: eraLama === null ? 0 : eraLama, padaTanggal: w.tanggal, dibatalkan: tahun } });
    // titik kas dikembalikan HANYA bila titik sekarang masih yang ditulis tutup buku ini (31 Des) — kalau tutup hari sudah memajukannya, hitungan fisik itu dipertahankan
    const tk = ambilTitikKas(); if (acara.titikDitulis && acara.titikSebelum && acara.titikSebelum.tanggal && tk && tk.tanggal === tbCutoff(tahun)) { titik = Object.assign({}, acara.titikSebelum, { id: 'titikKas', diubahPada: w.kini }); awal.push({ koleksi: 'pengaturan', data: titik }); }
  }
  // v7 (K8): pintu (bila ada bulan terkunci) ikut kiriman PERTAMA — tarik saldo pembuka bertanggal lama, pengembalian arsip & titik kas lewat pintu
  const pintu = (susunPintu(tahun, w).dokumen || [])[0] || null; if (pintu) awal.push(pintu);
  // §8 no. 1: batch penanda dihapus di kiriman PERTAMA — HP staf (tanpa berita acara) langsung tidak melihat pembuka lagi, sama dengan HP owner
  const tanda = hapus.filter((x) => { const d = x.koleksi === 'batchMasuk' ? dokDiCache(x.koleksi, x.id) : null; return !!(d && d.penandaBuku); }); const sisa = hapus.filter((x) => tanda.indexOf(x) < 0);
  const P = kpPotong([{ dokumen: awal, hapus: tanda }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] }))), dokDiCache, ugKiniDari(w), { sampai: kunciSampai(), pintu: bkPintuPakai(pintu, w) }); if (P.tolak) return { tolak: P.tolak };
  // sanggahan rules 7 Okt: pintu hanya dibuka di atas berita acara yang di server SUDAH berjalan / terkunci / membatalkan — pembatalan lanjutan dari
  // 'dibatalkan' yang perlu pintu menulis 'membatalkan' sendirian dulu (kiriman 1), pintu & tarikan di kiriman sesudahnya
  const dulu = !!pintu && ['berjalan', 'terkunci', 'membatalkan'].indexOf(acara.status) < 0;
  const potong = dulu ? [{ dokumen: [awal[0]], hapus: [], get: 0 }].concat(P.potongan.map((p, i) => (i === 0 ? Object.assign({}, p, { dokumen: p.dokumen.filter((x) => x !== awal[0]) }) : p))) : P.potongan;
  const kiriman = potong.map((p, i) => ({ ke: i + 1, total: potong.length, get: p.get, dokumen: p.dokumen, hapus: p.hapus }));
  const akhir = { koleksi: 'tutupBukuAcara', data: Object.assign({}, batal, { status: 'dibatalkan' }) };
  // v7: pintu DITUTUP bersama berita acara 'dibatalkan' (kiriman terakhir pembatalan)
  return { kiriman, akhir, akhirDokumen: [akhir].concat(bkTutupPintu(tahun, w, !!pintu)), percobaan: bkPercobaan(batal), dokumen: [].concat.apply([], kiriman.map((k) => k.dokumen)), hapus, titik, pulih: (arsipDok || []).map((a) => ({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok })),
    patch: { kabar: 'Tutup buku ' + tahun + ' dibatalkan — ' + ANGKA((arsipDok || []).length) + ' dokumen dikembalikan dari arsip, ' + hapus.length + ' saldo pembuka ditarik dalam ' + kiriman.length + ' kiriman. Tahun ' + tahun + ' terbuka lagi.', kabarAwas: false } };
}
const KOLEKSI_CACHE = CACHE_PEMBUKA;   // siap 2027: satu daftar di toko.js (modalOwner ikut sejak modal owner punya saldo pembuka)
function bkEraTanpa(tahun) { return eraBuku(tahun); }
/** Putaran 3 UTBU-2: TIDAK SAMA = kedua sisi terhitung dan berbeda; sisi mana pun yang tidak bisa dihitung (patokan / mesin null, mis. titik kas sudah maju) = belum bisa dihitung. */
const bkPisahPeriksa = (PU) => ({ beda: PU.baris.filter((b) => b.tahu && b.b !== null && !b.sama), belum: PU.baris.filter((b) => !b.tahu || b.b === null) });
/** §8 no. 6: kalimat hasil pemeriksaan ulang untuk "selesaikan" ('' = semua sama). */
export function bkKalimatPeriksa(PU) {
  if (!PU) return 'Pemeriksaan ulang tidak bisa dijalankan (patokan hari tutup buku tidak ada di berita acara)';
  if (PU.semuaSama) return ''; const nm = (d) => d.map((b) => b.nama.split(' · ')[0]).join(', '); const P = bkPisahPeriksa(PU);
  return 'Pemeriksaan ulang dari mesin: ' + [P.beda.length ? P.beda.length + ' baris TIDAK SAMA (' + nm(P.beda) + ')' : '', P.belum.length ? P.belum.length + ' baris belum bisa dihitung (' + nm(P.belum) + ')' : ''].filter(Boolean).join(' · ');
}
/**
 * Selesai: cadangan sesudah tercatat → berita acara selesai (tidak bisa dibatalkan lagi).
 * §8 no. 6: hanya sesudah arsip HABIS; pemeriksaan ulang dari mesin dijalankan di sini — beda / tidak bisa diperiksa = ditolak dengan barisnya (perluYakin),
 * baru diterima pada ketukan kedua (yakin) dan hasilnya dicatat di berita acara. L = lokal() layar (putaran 4 P4-1: hanya dari perangkat pemegang).
 */
export function susunSelesai(tahun, namaCadangan2, w, yakin, L) {
  const acara = ambilTutupBukuAcara().find((a) => Number(a.tahun) === tahun) || null; if (!acara || acara.status !== 'terkunci') return { tolak: 'Kunci tahunnya dulu' };
  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };
  const sisa = bkArsipHabis(tahun) ? 0 : arsipBuku(tahun).n; if (sisa) return { tolak: ANGKA(sisa) + ' catatan ' + tahun + ' belum pindah ke arsip — lanjutkan arsip dulu; tahun ' + tahun + ' belum bisa diselesaikan' };
  const PU = bkPeriksaDipakai(tahun); const S = susulanBuku(tahun); const kal = [bkKalimatPeriksa(PU), S ? S.teks : ''].filter(Boolean).join(' · ');
  if (kal && !yakin) return { tolak: kal + '. Sesudah selesai, tutup buku ' + tahun + ' tidak bisa dibatalkan lagi — periksa dulu; kalau memang benar, ketuk sekali lagi.', perluYakin: true };
  const P = PU ? bkPisahPeriksa(PU) : null; const periksaUlang = { sama: !bkKalimatPeriksa(PU), beda: P ? P.beda.map((b) => b.nama) : ['tidak bisa diperiksa'], belumBisa: P ? P.belum.map((b) => b.nama) : [], pada: w.kini };
  // A9: catatan susulan yang ada saat selesai ikut tercatat di berita acara (jumlah, rupiah nota & pengeluaran, tanggalnya) — bukan diam
  const susulan = S ? { n: S.n, rupiahNota: S.rupiah, rupiahKeluar: S.rupiahKeluar, tanggal: S.tanggal.slice(0, 31) } : null;
  // pesanan yang sengaja tertinggal (belum tuntas) dicatat juga di berita acara — juga bila hasil periksa saat arsip habis tidak sempat tersimpan
  const tertinggal = Array.from(new Set(Object.keys(bkTertinggal(tahun)).concat(bkTertinggalKini(tahun))));
  // v7: pintu tutup buku DITUTUP bersama berita acara 'selesai'
  return { dokumen: [{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara, { status: 'selesai', cadangan2: namaCadangan2 || '', selesaiPada: w.kini, selesaiTanggal: w.tanggal, periksaUlang, susulan, tertinggal, langkah: Object.assign({}, acara.langkah || {}, { cadangan2: w.kini }) }) }].concat(bkTutupPintu(tahun, w)), patch: { kabar: 'Tahun ' + tahun + ' selesai ditutup. Simpan kedua berkas cadangan di luar HP.' + (S ? ' ' + S.n + ' catatan susulan ' + tahun + ' tercatat di berita acara — ikuti pitanya.' : ''), kabarAwas: !!S } };
}
/**
 * §8 no. 7: kalimat bila tutup buku / pembatalan BERHENTI di kiriman ke-`ke` — tombol yang disebut harus tombol yang benar-benar meneruskan hal itu.
 * Kiriman 1 tutup buku tidak masuk → belum ada berita acara 'berjalan', pita Lanjutkan tidak ada → "Kunci tahun" lagi. Kiriman 1 pembatalan tidak masuk → berita
 * acara masih 'berjalan' / 'terkunci', "Lanjutkan" justru meneruskan TUTUP BUKU / arsip → "Batalkan" lagi. Sesudahnya pita ada → "Lanjutkan".
 * h = hasil tulisDokumen ({ gagal, pesan } | { antre } | null). Belum diakui server (antre) → tunggu antrean kosong dulu, lalu langkah menurut pita.
 */
export function kabarBerhentiBuku(jenis, tahun, ke, total, h, info) {
  const sebab = h && h.pesan ? ' — ' + h.pesan : ' — server belum mengaku'; const antre = !!(h && h.antre && !h.gagal);
  const tunggu = ' Kiriman itu masih di perangkat ini, menunggu server — jangan tutup aplikasi; tunggu sampai antrean kosong. ';
  if (jenis === 'batal') {
    const awal = 'Pembatalan tutup buku ' + tahun + ' berhenti di kiriman ' + ke + ' dari ' + total + sebab + '.';
    if (antre) return awal + tunggu + (ke === 1 ? 'Sesudah itu: kalau pita menyebut "Pembatalan tutup buku ' + tahun + ' belum selesai", ketuk "Lanjutkan"; kalau tidak, ketuk "Batalkan" lagi.' : 'Sesudah itu ketuk "Lanjutkan" untuk meneruskan pembatalan.');
    return awal + (ke === 1 ? ' Kiriman ini tidak masuk — ketuk "Batalkan" lagi (selama pita belum menyebut pembatalan, "Lanjutkan" meneruskan tutup buku, bukan pembatalan).' : ' Ketuk "Lanjutkan" untuk meneruskan pembatalan — yang sudah ditarik tidak diulang.');
  }
  // putaran 3 AAL7: kiriman LANJUTAN (lanjutBuku; info = kirimannya) — berita acara 'berjalan' sudah ada, jadi selalu "Lanjutkan"; nomor = pecahan sekarang,
  // ditambah saldo pembuka yang sudah masuk (satuan pita)
  if (jenis === 'lanjut') { const I = info || {}; return 'Berhenti di kiriman lanjutan ' + ke + ' dari ' + total + sebab + '. Tahun ' + tahun + ' BELUM tertutup (' + (Number(I.masuk) || 0) + ' dari ' + (Number(I.dari) || 0) + ' saldo pembuka sudah masuk, belum dihitung).'
    + (antre ? tunggu + 'Sesudah itu ketuk "Lanjutkan"' : ' Ketuk "Lanjutkan"') + ' — yang sudah masuk tidak dikirim ulang — atau "Batalkan".'; }
  const awal = 'Berhenti di kiriman ' + ke + ' dari ' + total + sebab + '. Tahun ' + tahun + ' BELUM tertutup (yang sudah masuk belum dihitung).';
  // putaran 3 AAL6: SATU kiriman saja = kiriman itu sudah membawa penanda → begitu server mengaku, pitanya "Tahun … terkunci" (bukan "… sudah masuk")
  // dan tombol K6 sudah tahun berikutnya
  if (antre) return awal + tunggu + (ke === 1 ? 'Sesudah itu: kalau pita ' + (total === 1 ? '"Tahun ' + tahun + ' terkunci; …" muncul, ketuk "Lanjutkan" (arsip)' : '"Tutup buku ' + tahun + ': … sudah masuk" muncul, ketuk "Lanjutkan"') + '; kalau tidak, ketuk "Kunci tahun ' + tahun + '" lagi.' : 'Sesudah itu ketuk "Lanjutkan" — yang sudah masuk tidak dikirim ulang — atau "Batalkan".');
  return awal + (ke === 1 ? ' Tidak ada yang masuk — ketuk "Kunci tahun ' + tahun + '" lagi sesudah sebabnya dibereskan.' : ' Ketuk "Lanjutkan" — yang sudah masuk tidak dikirim ulang — atau "Batalkan".');
}
/** Teks berita acara (cetak/WA). */
export function teksAcara(tahun, D, B, sebelum, saksi, w) {
  const L = ['TOKO BERAS M.IQBAL', 'BERITA ACARA TUTUP BUKU ' + tahun, tanggalPendek(w.tanggal) + ' · ' + w.jam + (D.latihan ? ' · LATIHAN' : ''), '', 'Harta toko akhir ' + tahun + ':'];
  B.baris.forEach((b) => L.push('  ' + (b.nama + '                                    ').slice(0, 38) + (b.a === null ? 'tidak bisa dihitung' : RP(b.a)) + (b.ada ? (b.a === null ? '  ?' : b.sama ? '  ✓' : '  ≠ ' + RP(b.b)) : '')));
  const rpA = (n) => (n === null ? 'tidak bisa dihitung' : RP(n));   // 39b no. 12: bukan Rp0
  L.push('', 'Jumlah harta   ' + rpA(sebelum.hartaJml), 'Jumlah utang   ' + RP(sebelum.utangJml), 'Modal owner    ' + RP(sebelum.modal), 'Laba tinggal   ' + rpA(sebelum.labaTinggal), '');
  if (sebelum.kataLebih) L.push(sebelum.kataLebih, '');   // no. 4 B6
  // siap 2027: putusan hari tanpa tutup hari (A1), upah yang belum dibayar per orang (A6), catatan susulan (A9) ikut berita acara
  // sesudah kunci, nota tahun itu sudah di arsip → daftar hari diambil dari berita acara (putusanHari), bukan dihitung ulang dari buku hidup
  const AC = bkAcara(tahun); const H = AC && Array.isArray(AC.putusanHari) ? AC.putusanHari.map((x) => ({ iso: x.iso, nNota: x.nNota, putusan: x.alasan ? { alasan: x.alasan } : null })) : bkHariTanpaTutup(tahun, tbCutoff(tahun)); if (H.length) { L.push('Hari berjualan tanpa tutup hari (' + H.length + ') — tidak ditutup, diterima apa adanya:'); H.forEach((h) => L.push('  ' + tanggalPendek(h.iso) + ' · ' + h.nNota + ' nota · ' + (h.putusan ? h.putusan.alasan : 'BELUM DIPUTUS'))); L.push(''); }
  const U = (sebelum.upah && sebelum.upah.orang ? sebelum.upah.orang : []).filter((o) => o.upah > 0); if (U.length) { L.push('Upah karyawan yang belum dibayar s.d. ' + tanggalPendek(tbCutoff(tahun)) + ' (dibayar sesudahnya = biaya bulan pembayaran):'); U.forEach((o) => L.push('  ' + o.nama + ' · ' + tanggalPendek(o.mulai) + ' – ' + tanggalPendek(o.sampai) + ' · ' + RP(o.upah))); L.push(''); }
  const S = susulanBuku(tahun); if (S) L.push('SUSULAN: ' + S.teks, '');
  L.push('Paraf: owner ' + (D.paraf && D.paraf.owner ? '✓' : '—') + ' · ' + (saksi || 'saksi') + ' ' + (D.paraf && D.paraf.saksi ? '✓' : '—'));
  return L.join('\n');
}

// ---- A9 · CATATAN SUSULAN (siap 2027) — bertanggal tahun yang sudah ditutup, masuk SESUDAH penanda (karcis HP penjaga yang tertahan offline) ----
const bkSusulanSudah = (tahun) => { const d = dokDiCache('pengaturan', 'susulan' + tahun); const o = {}; ((d && Array.isArray(d.ids)) ? d.ids : []).forEach((k) => { o[String(k)] = true; }); return o; };
/**
 * Catatan bertanggal ≤ 31 Des `tahun` (default: era) yang masih ada di buku hidup sesudah arsip tahun itu HABIS (berita acara selesai, atau terkunci dengan hasil
 * periksa yang dibekukan). Tidak ikut saldo pembuka maupun berita acara; stok & bonnya sudah benar di buku tahun baru (dipotong/ditambah sekarang), uangnya
 * bertanggal sebelum titik kas 31 Des (tidak terhitung masuk/keluar laci). Yang sudah "dicatat" owner (pengaturan/susulan<tahun>) tidak disebut lagi, juga
 * pesanan yang SENGAJA tertinggal karena belum tuntas (bkTertinggal — dibayar Januari bukan susulan). Kalimat jalannya per jenis: nota (uang LEBIH, omzet
 * kurang), pengeluaran (uang KURANG, biaya kurang → laba terlihat lebih besar), catatan lain. null = tidak ada.
 */
export function susulanBuku(tahun) {
  const t = tahun !== undefined && tahun !== null ? Number(tahun) : eraBuku(); if (t === null || !isFinite(t)) return null; const a = bkAcara(t);
  if (!a || !(a.status === 'selesai' || (a.status === 'terkunci' && bkArsipHabis(t)))) return null;
  const sudah = bkSusulanSudah(t); const tinggal = bkTertinggal(t); const A = arsipBuku(t);
  const daftar = A.daftar.filter((x) => !sudah[x.koleksi + '|' + x.id] && !tinggal[x.koleksi + '|' + x.id]); if (!daftar.length) return null;
  const label = {}; A.perKoleksi.forEach((k) => { label[k.koleksi] = k.label; }); const per = {}; daftar.forEach((x) => { per[x.koleksi] = (per[x.koleksi] || 0) + 1; });
  const jumlah = (d, f) => d.reduce((s, x) => s + (Number(x.data[f]) || 0), 0);
  const jual = daftar.filter((x) => x.koleksi === 'penjualan' && !x.data.dibatalkan && !x.data.dikoreksiOleh); const rupiah = jumlah(jual, 'hargaTotal');
  // pengeluaran harian yang telat: uang keluarnya juga tidak terhitung; biaya toko (bukan ambil pribadi owner) yang hilang membuat laba tahun itu terlihat lebih besar
  const keluar = daftar.filter((x) => x.koleksi === 'pengeluaranHarian'); const rupiahKeluar = jumlah(keluar, 'nominal');
  const biaya = jumlah(keluar.filter((x) => x.data.kategori === 'toko' || x.data.kategori === 'tokoDompet'), 'nominal');
  const nLain = daftar.filter((x) => x.koleksi !== 'penjualan' && x.koleksi !== 'pengeluaranHarian').length;
  const tanggal = Array.from(new Set(daftar.map((x) => String(x.data.tanggal || x.data.bulan || '')).filter(Boolean))).sort();
  const teks = daftar.length + ' catatan bertanggal ' + t + ' masuk SESUDAH tutup buku ' + t + ' dikunci (' + Object.keys(per).map((k) => (label[k] || k) + ' ' + per[k]).join(', ') + (tanggal.length ? ' · ' + tanggal.slice(0, 4).map(tanggalPendek).join(', ') + (tanggal.length > 4 ? ' …' : '') : '')
    + (rupiah ? ' · nota ' + RP(rupiah) : '') + (rupiahKeluar ? ' · pengeluaran ' + RP(rupiahKeluar) : '') + ') — biasanya ' + (daftar.every((x) => x.koleksi === 'penjualan') ? 'karcis HP penjaga' : 'catatan HP') + ' yang tertahan tanpa sinyal.';
  const jalan = ['Catatan itu TIDAK ikut saldo pembuka maupun berita acara ' + t + '. Jangan dihapus: stok, bon, dan utangnya sudah benar di buku ' + (t + 1) + '.',
    jual.length ? 'Uang notanya tidak terhitung masuk (bertanggal sebelum titik kas 31 Des) — kalau uangnya ada di laci, tutup hari berikutnya mencatatnya LEBIH; itu memang uangnya.' + (rupiah ? ' Omzet ' + t + ' di berita acara kurang ' + RP(rupiah) + '.' : '') : '',
    keluar.length ? 'Uang pengeluarannya juga tidak terhitung keluar — kalau uangnya memang sudah keluar dari tempat uang toko, tutup hari berikutnya mencatatnya KURANG; itu memang pengeluarannya.' + (biaya ? ' Biaya ' + t + ' di berita acara kurang ' + RP(biaya) + ', jadi laba ' + t + ' terlihat lebih besar.' : '') : '',
    nLain ? 'Kalau catatan lainnya memindah uang (bayar bon, kedatangan tunai, setor atau tarik modal), uangnya juga tidak terhitung — selisihnya muncul di tutup hari berikutnya.' : '',
    rupiah || biaya ? 'Sampaikan ke yang mengurus pajak ' + t + '.' : '', 'Sesudah dicatat, ketuk "sudah dicatat".'].filter(Boolean).join(' ');
  return { tahun: t, n: daftar.length, daftar, perKoleksi: per, rupiah, rupiahKeluar, biaya, tanggal, teks, jalan };
}
/** "Sudah dicatat": id catatan susulan sekarang ditambahkan ke pengaturan/susulan<tahun> (owner saja; bukan titik kas — tidak dikunci bulan). */
export function susunCatatSusulan(tahun, w) {
  const S = susulanBuku(tahun); if (!S) return { tolak: 'Tidak ada catatan susulan yang belum dicatat' }; const lama = dokDiCache('pengaturan', 'susulan' + S.tahun) || {};
  const ids = Array.from(new Set(((Array.isArray(lama.ids) ? lama.ids : []).map(String)).concat(S.daftar.map((x) => x.koleksi + '|' + x.id))));
  const data = { id: 'susulan' + S.tahun, tahun: S.tahun, ids, n: ids.length, rupiahNota: (Number(lama.rupiahNota) || 0) + S.rupiah, rupiahKeluar: (Number(lama.rupiahKeluar) || 0) + S.rupiahKeluar, pada: w.kini, tanggal: w.tanggal, jam: w.jam };
  const isi = [S.rupiah ? 'nota ' + RP(S.rupiah) : '', S.rupiahKeluar ? 'pengeluaran ' + RP(S.rupiahKeluar) : ''].filter(Boolean).join(', ');
  return { dokumen: [{ koleksi: 'pengaturan', data }], patch: { kabar: S.n + ' catatan susulan ' + S.tahun + ' dicatat' + (isi ? ' (' + isi + ')' : '') + ' — catatannya tetap di buku, tidak dihapus.', kabarAwas: false } };
}

// ---- A2 · TUTUP BUKU TAHUN LALU SELESAI? (dibaca daftar periksa kunci bulan & Beranda) ----
/** { ok, teks } — tahun itu sudah ditutup sampai SELESAI, atau memang tanpa catatan. Berita acara terkunci / berjalan / dibatalkan = belum. */
export function bkTahunSelesai(tahun) {
  const a = bkAcara(tahun); const era = eraBuku();
  if (a && a.status === 'selesai') return { ok: true, teks: 'tutup buku ' + tahun + ' selesai ' + tanggalPendek(a.selesaiTanggal || a.tanggal || '') };
  if (era !== null && era > tahun) return { ok: true, teks: 'tahun ' + tahun + ' sudah lewat tutup buku' };
  if (!a && era !== null && era >= tahun) return { ok: true, teks: 'tahun ' + tahun + ' ditutup sistem lama' };
  let pertama = ''; ambilPenjualanSemua().concat(ambilSemuaBatch().filter((b) => !b.stokAwal && !b.tutupBuku)).forEach((d) => { if (d.tanggal && (!pertama || d.tanggal < pertama)) pertama = d.tanggal; });
  if (!pertama || Number(pertama.slice(0, 4)) > tahun) return { ok: true, teks: 'tahun ' + tahun + ' tanpa catatan' };
  return { ok: false, teks: 'Tutup buku ' + tahun + (a ? ' masih ' + ({ berjalan: 'berjalan', terkunci: 'terkunci, belum selesai', membatalkan: 'sedang dibatalkan', dibatalkan: 'dibatalkan' }[a.status] || a.status) : ' belum dikerjakan') };
}
/** Beranda › Perlu perhatian (owner): tutup buku tahun lalu yang belum selesai sesudah 1 Jan, dan catatan susulan yang belum dicatat. */
export function bkPerhatian(kini) {
  const out = []; const S = susulanBuku(); if (S) out.push({ teks: 'Tutup buku ' + S.tahun + ': ' + S.teks, nilai: 'Uang › Tutup buku', awas: true });
  const T = tahunBuku(kini); if (T.bolehSungguhan && !bkTahunSelesai(T.tahun).ok) { const KM = kemajuanBuku(); out.push({ teks: KM ? KM.teks : 'Tutup buku ' + T.tahun + ' belum dikerjakan — kunci bulan ' + (T.tahun + 1) + ' menunggu sampai selesai', nilai: 'Uang › Tutup buku', awas: !!KM }); }
  return out;
}

// ---- A8 · PERKIRAAN KUOTA FIRESTORE (owner 7 Okt: K1 tetap Spark) ----
export const BATAS_SPARK = { tulis: 20000, hapus: 20000, baca: 50000 };
/**
 * Jam (WIB) kuota harian Spark kembali penuh = tengah malam waktu Pasifik yang jatuh pada tanggal `iso` WIB: 14.00 bila tengah malam itu musim panas AS (PDT,
 * UTC−7), 15.00 bila PST (UTC−8). Dihitung dari zona America/Los_Angeles: pada hari pergantian jamnya pindah pukul 02.00 waktu Pasifik, jadi tengah malam
 * Minggu ke-2 Maret masih PST (15.00) dan tengah malam Minggu ke-1 November masih PDT (14.00) — dulu aturan tanggal meleset satu jam di dua hari itu.
 * Peramban tanpa data zona: aturan tanggal yang sama (pergantian sesudah tengah malam).
 */
export function jamResetKuota(iso) {
  const d = String(iso).slice(0, 10); const t = new Date(d + 'T07:00:00Z');   // 07.00 UTC = tengah malam PDT pada tanggal itu (= 23.00 PST sehari sebelumnya)
  try { const j = Number(new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', hour: '2-digit', hourCycle: 'h23' }).format(t)) % 24; if (j === 0) return 14; if (j === 23) return 15; } catch (e) { /* tanpa data zona */ }
  const y = Number(d.slice(0, 4)); const minggu = (bln, ke) => { const a = new Date(Date.UTC(y, bln, 1)); return new Date(Date.UTC(y, bln, 1 + ((7 - a.getUTCDay()) % 7) + (ke - 1) * 7)).toISOString().slice(0, 10); };
  return d > minggu(2, 2) && d <= minggu(10, 1) ? 14 : 15;
}
/**
 * Perkiraan tulis / hapus / baca Firestore untuk ritual SUNGGUHAN dan untuk BATALKAN sesudah arsip berjalan penuh, dari data di perangkat ini — dibandingkan
 * dengan batas Spark harian. Dihitung untuk jam mulai yang disarankan (1 Jan sesudah reset kuota, atau sekarang bila sudah lewat). Perkiraan, bukan Console:
 * tulisan lain hari itu (penjualan, tutup hari) dan muat ulang aplikasi menambah pemakaian. Owner menulis 1 baris jejak per dokumen; arsip 1 per potongan 18.
 */
let _kuotaMemo = null;
export function perkiraanKuota(tahun, kini) {
  const isoRencana = (tahun + 1) + '-01-01'; const jam = jamResetKuota(isoRencana);
  const rencana = new Date(Math.max(kini.getTime(), Date.parse(isoRencana + 'T' + String(jam).padStart(2, '0') + ':05:00+07:00'))); const W = kpWib(rencana);
  const kunciMemo = tahun + '|' + versiCache() + '|' + W.iso; if (_kuotaMemo && _kuotaMemo.k === kunciMemo) return _kuotaMemo.h;   // layar K6 menggambar ulang tiap data berubah
  let n = 0; const P = pembukaBuku(tahun, { idUnik: () => 'perkiraan-' + (n += 1) }); const A = arsipBuku(tahun);
  const nP = P.dokumen.length + (P.dokumen.some((x) => x.koleksi === 'batchMasuk') ? 0 : 1);
  // v7: bulan terkunci → jalur pintu (2–3 access call per catatan; tiap access call = 1 baca di tagihan Firestore) & potongan arsip lebih kecil
  const sK = kunciSampai(); const PP = sK ? { tahun, sampai: Infinity } : null;
  const getP = kpNilaiKiriman(P.dokumen.map((x) => ({ koleksi: x.koleksi, data: x.data })), sK, rencana, PP).perluGet + (PP ? 1 : 0); const nKirim = Math.max(1, Math.ceil(getP / KP_BATAS_GET));
  const bA = bkBiayaArsip(A.daftar, (x) => ({ koleksi: x.koleksi, id: x.id, lama: x.data, hapus: true, arsip: true }), rencana, tahun); const getA = bA.reduce((a, x) => a + x, 0);
  const getPulih = bkBiayaArsip(A.daftar, (x) => ({ koleksi: x.koleksi, data: x.data, pulih: true }), rencana, tahun).reduce((a, x) => a + x, 0);
  const potong = kpPecahBiaya(bA, KP_BATAS_GET, KP_BATAS_GET).length; const muat = KOLEKSI.reduce((s, k) => s + cacheMentah(k.cache).length, 0);
  // ritual: pembuka + jejaknya, penanda (pengaturan ×2, berita acara berjalan/terkunci), arsip (salinan + jejak per potongan), hasil periksa, 2 catatan cadangan
  const aturan = 4 + (nKirim > 1 ? 1 : 0);
  const ritual = { tulis: 2 * (nP + aturan) + A.n + potong + 2 + 4, hapus: A.n, baca: muat + getP + getA + nP + aturan + potong };
  // batalkan sesudah arsip penuh: baca seluruh arsip, kembalikan (pendengar membaca tiap catatan yang kembali), tarik saldo pembuka (hapus + jejak)
  const batal = { tulis: A.n + potong + nP + 6, hapus: A.n + nP, baca: 2 * A.n + getPulih + nP };
  const nilai = (x) => ['tulis', 'hapus', 'baca'].map((k) => ({ k, n: x[k], batas: BATAS_SPARK[k], persen: Math.round((x[k] / BATAS_SPARK[k]) * 100) }));
  const R = nilai(ritual), B = nilai(batal); const lewat = R.filter((x) => x.n > x.batas), mepet = R.filter((x) => x.n <= x.batas && x.n > 0.8 * x.batas);
  const kata = (x) => ANGKA(x.n) + ' ' + x.k + ' (' + x.persen + '% dari ' + ANGKA(x.batas) + ')';
  const kalimat = ['Mulai ' + tanggalPendek(W.iso) + ' sesudah pukul ' + jam + '.00 WIB (kuota harian Spark baru penuh lagi). Satu perangkat, jangan muat ulang aplikasi — sekali muat ±' + ANGKA(muat) + ' baca.',
    lewat.length ? 'TIDAK MUAT dalam kuota satu hari: ' + lewat.map(kata).join(' · ') + '. Arsip akan berhenti di tengah; sampai dilanjutkan sesudah reset berikutnya, stok, piutang & utang terhitung DOBEL — jangan berjualan/menagih selama itu.'
      : mepet.length ? 'MEPET: ' + mepet.map(kata).join(' · ') + '. Tulisan toko hari itu ikut menghabiskan kuota — kerjakan saat toko tutup.' : 'Muat dalam kuota satu hari.',
    'Batalkan sesudah arsip berjalan penuh butuh ±' + B.map(kata).join(' · ') + (B.some((x) => x.n > x.batas) || R.some((x) => x.n > 0.5 * x.batas) ? ' — tidak muat di hari yang sama dengan ritualnya: toko jangan berjualan sampai pembatalan tuntas sesudah reset berikutnya.' : '.'),
    'Kuota yang sudah terpakai hari itu tidak terlihat dari aplikasi — lihat Console › Firestore › Usage sebelum mulai.'];
  const h = { tahun, rencana: W.iso, jamReset: jam, muat, nPembuka: nP, nArsip: A.n, kiriman: nKirim, ritual, batal, R, B, lewat: lewat.length > 0, mepet: mepet.length > 0, kalimat };
  _kuotaMemo = { k: kunciMemo, h }; return h;
}
export { RP as bkRP };
