// LAYAR UANG — K2 ORANG & UPAH (dikunci owner 17 Sep 2026: C · Buku Upah). Logika tanpa DOM; pembantu berawalan up.
// Upah dihitung SEJAK TERAKHIR DIBAYAR (owner membayar saat karyawan pulang kampung, bukan per bulan kalender); setengah hari = separuh tarif;
// hari yang BELUM DIISI bukan "tidak masuk" (tiga keadaan kosong) → upah tidak bisa dibayar sebelum diisi (hari ini sendiri boleh kosong).
//
// Dokumen = mesin uang lama, tanpa mesin baru:
//  - hari kerja  → absenKaryawan {id: kunci|bulan, nama, bulan, hari: {iso: 1 | 0,5 | 0}} (koleksi baru; tidak menyentuh uang).
//  - kasbon      → kasbonMutasi {tipe ambil} persis simpanKasbonAmbil + jam & dari (laci).
//  - bayar upah  → biayaBulanan bulan-bulan yang tercakup: SATU baris rincianGaji per pembayaran dengan kunci "Nama · tanggal bayar" (bukan nama polos),
//                  tanggalBayarGaji[kunci] = tanggal bayar. Kenapa bukan nama polos: mesin lama mengalokasikan SEMUA potongan kasbon "Potong gaji" ke baris
//                  gaji paling awal yang masih punya ruang, jadi baris baru bernama polos bisa ikut dipotong potongan bulan lalu dan kas hari bayar bergeser;
//                  kunci bertanggal juga membuat dua pembayaran dalam satu bulan tidak saling menimpa tanggalnya. Laba: gaji penuh dibagi rata per hari sebulan
//                  (jatahBiayaBulananHari); kas: gaji penuh keluar pada tanggal bayar.
//  - potong kasbon → kasbonMutasi {tipe bayar, caraBayar 'Dipotong upah'} = kas MASUK sebesar potongan pada hari yang sama, sehingga kas bersih hari itu =
//                  yang diterima karyawan (upah − potongan). Sengaja BUKAN 'Potong gaji' (lihat di atas).
//  - slip        → slipUpah (koleksi baru) = jejak tiap pembayaran: rentang hari, hitungan, potongan, teks slip. "Sejak terakhir dibayar" dibaca dari sini.
import { hitungKasbon } from '../mesin/beku.js';
import { kunciPelanggan, akhirBulanIso, POS_BIAYA_BULANAN } from '../mesin/pembantu.js';
import { ambilBiayaBulanan, ambilKasbonMutasi, ambilAbsenKaryawan, ambilSlipUpah, cacheMentah, tolakKunciTanggal } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { NAMA_KASBON_OWNER, ugAngka, ugKosong, ugAturDok, ugTambahHari, ugHariKe, ugKiniDari, saldoKantong, ugCukup } from './uang-logika.js';

export const ATUR_UPAH_BAWAAN = { tarif: 60000, orang: [], alasan: ['Keperluan keluarga', 'Pulang kampung', 'Berobat', 'Lain-lain'] };
const UP_ORANG_UMUM = [];   // dulu daftar nama pegawai sistem lama; dicabut 28 Sep 2026 (repo publik tanpa nama orang) — tanpa data, daftar karyawan kosong dan layar menyebutnya
export const NILAI_HARI = [[1, 'Penuh'], [0.5, 'Setengah'], [0, 'Tidak masuk']];
const upKunci = (nama) => kunciPelanggan(nama);
const upBukanOwner = (nama) => upKunci(nama) !== upKunci(NAMA_KASBON_OWNER);
/** Karyawan yang TERUKUR dari catatan: nama di rincian gaji, kasbon, atau absen (Owner bukan karyawan). */
export function orangTerukur() {
  const peta = {}; const isi = (nm) => { const k = upKunci(nm); if (!k || !upBukanOwner(nm)) return; if (!peta[k]) peta[k] = String(nm).trim(); };
  ambilBiayaBulanan().forEach((b) => (b.rincianGaji || []).forEach((r) => { if (Number(r.hari) > 0 || Number(r.gaji) > 0) isi(String(r.nama || '').replace(/ · .*$/, '')); }));
  ambilKasbonMutasi().forEach((m) => isi(m.namaPegawai)); ambilAbsenKaryawan().forEach((a) => isi(a.nama));
  const daftar = Object.keys(peta).map((k) => peta[k]); return daftar.length ? daftar : UP_ORANG_UMUM.slice();
}
export const STATUS_KARYAWAN = [['aktif', 'Aktif'], ['berhenti', 'Berhenti']];
const upIso = (v) => (/^\d{4}-\d{2}-\d{2}$/.test(String(v || '').trim()) ? String(v).trim() : '');
/** Satu baris karyawan dibaca ke bentuk tetap: nama, peran, status aktif|berhenti, masuk, berhenti, mulaiHitung (owner: "hitung upah sejak"), catatan. */
// putaran 29 (Bagian 2, owner 27 Sep 2026): UPAH PER ORANG di dokumen bersama yang sama — tiap baris orang[] membawa daftar upah[] {mulai, satuan, tarif}
// (satuan hari · minggu · bulan, ditentukan owner), berlaku sejak `mulai`. Tarif per hari suatu tanggal = entri terbaru yang mulai ≤ tanggal; tanpa entri →
// `tarif` bersama (bawaan lama). Minggu ÷ 7, bulan ÷ jumlah hari bulan itu, DIBULATKAN ke rupiah dulu supaya slip bisa dihitung ulang pembaca. Slip yang sudah
// tertulis adalah dokumen — perubahan upah tidak menulis ulang riwayat; gajian sesudah tanggal berlaku memakai angka baru, gajian yang melintasinya merinci keduanya.
export const SATUAN_UPAH = [['hari', 'per hari'], ['minggu', 'per minggu'], ['bulan', 'per bulan']];
const upSatuanBaku = (s) => (s === 'minggu' || s === 'bulan' ? s : 'hari');
const upDaftarUpah = (arr) => (Array.isArray(arr) ? arr : []).map((u) => ({ mulai: upIso(u && u.mulai), satuan: upSatuanBaku(u && u.satuan), tarif: Math.round(Number(u && u.tarif) || 0) })).filter((u) => u.mulai && u.tarif > 0).sort((a, b) => a.mulai.localeCompare(b.mulai));
const upOrangBaku = (o) => ({ nama: String((o && o.nama) || '').trim(), peran: String((o && o.peran) || '').trim(), status: o && o.status === 'berhenti' ? 'berhenti' : 'aktif',
  masuk: upIso(o && o.masuk), berhenti: o && o.status === 'berhenti' ? upIso(o.berhenti) : '', mulaiHitung: upIso(o && o.mulaiHitung), catatan: String((o && o.catatan) || '').trim(), upah: upDaftarUpah(o && o.upah) });
export function aturUpah() {
  const a = ugAturDok('upah') || {}; const tarif = isFinite(Number(a.tarif)) && Number(a.tarif) > 0 ? Math.round(Number(a.tarif)) : ATUR_UPAH_BAWAAN.tarif;
  const orangOwner = Array.isArray(a.orang) ? a.orang.filter((o) => o && String(o.nama || '').trim()).map(upOrangBaku) : [];
  const orang = orangOwner.length ? orangOwner : orangTerukur().map((nama) => upOrangBaku({ nama }));
  return { tarif, orang, aktif: orang.filter((o) => o.status === 'aktif'), berhenti: orang.filter((o) => o.status !== 'aktif'), orangTerukur: !orangOwner.length, alasan: Array.isArray(a.alasan) && a.alasan.length ? a.alasan.map(String) : ATUR_UPAH_BAWAAN.alasan.slice(), dariOwner: !!ugAturDok('upah') };
}
/** Pembagi satuan → per hari: hari 1 · minggu 7 · bulan = jumlah hari kalender bulan tanggal itu. */
export const upPembagi = (satuan, iso) => (satuan === 'minggu' ? 7 : satuan === 'bulan' ? Number(akhirBulanIso(String(iso).slice(0, 7)).slice(8, 10)) : 1);
export const teksSatuanUpah = (satuan) => (SATUAN_UPAH.find((s) => s[0] === satuan) || SATUAN_UPAH[0])[1];
/** Tarif per hari yang berlaku untuk `nama` pada tanggal `iso`, berikut sumbernya (entri per orang atau tarif bersama). */
export function tarifHariPada(nama, iso, A) {
  const AU = A || aturUpah(); const O = AU.orang.find((o) => upKunci(o.nama) === upKunci(nama)) || null; let u = null;
  (O ? O.upah : []).forEach((x) => { if (x.mulai <= iso) u = x; });
  if (!u) return { tarifHari: AU.tarif, satuan: 'hari', tarif: AU.tarif, mulai: '', sumber: 'bersama', pembagi: 1, teks: RP(AU.tarif) + ' sehari (upah bawaan bersama)' };
  const pembagi = upPembagi(u.satuan, iso); const tarifHari = Math.round(u.tarif / pembagi);
  return { tarifHari, satuan: u.satuan, tarif: u.tarif, mulai: u.mulai, sumber: 'orang', pembagi, teks: u.satuan === 'hari' ? RP(u.tarif) + ' sehari' : RP(u.tarif) + ' ' + (u.satuan === 'minggu' ? 'seminggu' : 'sebulan') + ' ÷ ' + pembagi + ' hari = ' + RP(tarifHari) + ' sehari' };
}
/** Rupiah satu hari kerja: penuh = tarif harian, setengah = separuhnya dibulatkan ke rupiah (satu aturan untuk hitungan, buku, slip, dan baris gaji). */
const upNilaiHari = (x, th) => (x === 1 ? th : x === 0.5 ? Math.round(th / 2) : 0);
/** Baris karyawan menurut nama (baku), atau baris kosong bila tidak terdaftar. */
export function orangUpah(nama) { const k = upKunci(nama); return aturUpah().orang.find((o) => upKunci(o.nama) === k) || upOrangBaku({ nama }); }
export function susunAturUpah(isi, w) {
  const A = aturUpah(); const tarif = ugKosong(isi.tarif) ? A.tarif : ugAngka(isi.tarif); if (!(tarif > 0) || tarif > 10000000) return { tolak: 'Upah sehari harus 1–10.000.000' };
  const mentah = Array.isArray(isi.orang) ? isi.orang : A.orang;
  // putaran 29: daftar upah per orang diperiksa SEBELUM dibakukan (entri yang cacat harus ditolak, bukan dibuang diam-diam)
  for (const o of mentah) { const nm = String((o && o.nama) || '').trim(); if (!nm) continue; const daftar = Array.isArray(o.upah) ? o.upah : []; const mulaiSemua = [];
    for (const u of daftar) { const kosongSemua = !u || (ugKosong(u.mulai) && ugKosong(u.tarif)); if (kosongSemua) continue; const mulai = upIso(u.mulai); const n = Math.round(ugAngka(u.tarif)); const satuan = String(u.satuan || 'hari');
      if (!mulai) return { tolak: nm + ': upah ' + (n > 0 ? RP(n) : '') + ' belum punya tanggal mulai berlaku' }; if (!(n > 0) || n > 100000000) return { tolak: nm + ': upah ' + teksSatuanUpah(upSatuanBaku(satuan)) + ' harus 1–100.000.000' };
      if (satuan !== 'hari' && satuan !== 'minggu' && satuan !== 'bulan') return { tolak: nm + ': satuan upah tidak dikenal (hari · minggu · bulan)' };
      if (mulaiSemua.indexOf(mulai) >= 0) return { tolak: nm + ': dua upah mulai berlaku tanggal yang sama (' + tanggalPendek(mulai) + ')' }; mulaiSemua.push(mulai); } }
  const orang = mentah.map((o) => upOrangBaku(Object.assign({}, o, { nama: String((o && o.nama) || '').slice(0, 40), peran: String((o && o.peran) || '').slice(0, 40), catatan: String((o && o.catatan) || '').slice(0, 80), upah: (Array.isArray(o && o.upah) ? o.upah : []).filter((u) => u && !(ugKosong(u.mulai) && ugKosong(u.tarif))).map((u) => ({ mulai: u.mulai, satuan: u.satuan, tarif: Math.round(ugAngka(u.tarif)) })) }))).filter((o) => o.nama);
  if (!orang.length) return { tolak: 'Daftar karyawan tidak boleh kosong' };
  const kembar = orang.map((o) => upKunci(o.nama)).filter((k, i, arr) => arr.indexOf(k) !== i); if (kembar.length) return { tolak: 'Nama kembar: ' + kembar[0] };
  for (const o of orang) {
    if (o.status === 'berhenti' && !o.berhenti) return { tolak: o.nama + ' ditandai berhenti — isi tanggal berhentinya' };
    if (o.berhenti && o.berhenti > w.tanggal) return { tolak: 'Tanggal berhenti ' + o.nama + ' belum datang — tandai nanti saja' };
    if (o.masuk && o.berhenti && o.masuk > o.berhenti) return { tolak: o.nama + ': tanggal masuk sesudah tanggal berhenti' };
    if (o.mulaiHitung && o.mulaiHitung > w.tanggal) return { tolak: o.nama + ': "hitung upah sejak" tidak boleh di masa depan' };
  }
  // yang masih punya upah belum dibayar atau kasbon belum lunas tidak boleh dihapus
  const hilang = A.orang.filter((o) => !orang.some((x) => upKunci(x.nama) === upKunci(o.nama)));
  for (const o of hilang) { const H = hitungUpah(o.nama, ugKiniDari(w), 'tidak'); if (H.upah > 0 || H.sisaKasbon > 0) return { tolak: o.nama + ' masih punya ' + (H.upah > 0 ? 'upah ' + RP(H.upah) + ' yang belum dibayar' : 'kasbon ' + RP(H.sisaKasbon)) + ' — bayar atau lunasi dulu sebelum dihapus' }; }
  const alasan = (Array.isArray(isi.alasan) ? isi.alasan : A.alasan).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8);
  const nBerhenti = orang.filter((o) => o.status === 'berhenti').length; const nSendiri = orang.filter((o) => o.upah.length).length;
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'upah', tanggal: w.tanggal, jam: w.jam, tarif: Math.round(tarif), orang, alasan: alasan.length ? alasan : ATUR_UPAH_BAWAAN.alasan } }],
    patch: { aturU: null, karyawanDraf: null, kabar: 'Aturan upah disimpan — bawaan ' + RP(tarif) + ' sehari (' + RP(tarif / 2) + ' setengah hari)' + (nSendiri ? ' · ' + nSendiri + ' orang punya upah sendiri' : '') + ' · ' + (orang.length - nBerhenti) + ' karyawan aktif' + (nBerhenti ? ' · ' + nBerhenti + ' berhenti' : '') + ' · berlaku untuk hari yang BELUM dibayar sejak tanggal berlakunya; slip lama tidak berubah', kabarAwas: false } };
}
/** Kelola karyawan (HR): hanya daftar orangnya yang berubah — tarif & alasan kasbon tetap. */
export function susunKaryawan(daftar, w) { const A = aturUpah(); return susunAturUpah({ tarif: String(A.tarif), orang: daftar, alasan: A.alasan }, w); }
/** Peta hari kerja satu orang: { iso: 1 | 0.5 | 0 } dari semua dokumen absennya. */
export function hariKerja(nama) { const k = upKunci(nama); const o = {}; ambilAbsenKaryawan().forEach((a) => { if (upKunci(a.nama) !== k) return; Object.keys(a.hari || {}).forEach((t) => { const v = Number(a.hari[t]); if (v === 1 || v === 0.5 || v === 0) o[t] = v; }); }); return o; }
/** Sistem LAMA (per bulan): hari yang sudah tertutup gaji = sampai min(tanggal bayar, akhir bulan gajinya). Gaji Agu dibayar 18 Sep menutup sampai 31 Agu;
 *  gaji Sep dibayar 18 Sep (3 hari) menutup sampai 18 Sep — hari 19 Sep dst. TERBUKA (owner 23 Sep: "tanggal 18 gajian, tanggal 19 lanjut kerja"). */
function upBulanLamaTerakhir(nama) {
  let bulan = ''; let sampai = ''; let belum = null;
  ambilBiayaBulanan().forEach((b) => { const r = (b.rincianGaji || []).find((x) => String(x.nama || '').trim() === String(nama).trim()); if (!r || !(Number(r.gaji) > 0)) return;
    const tgl = (b.tanggalBayarGaji && b.tanggalBayarGaji[r.nama]) || (b.tanggalBayarPos ? b.tanggalBayarPos.gaji || '' : '') || b.tanggalBayar || '';
    if (tgl) { if (b.bulan > bulan) bulan = b.bulan; const akhir = akhirBulanIso(b.bulan); const tutup = tgl < akhir ? tgl : akhir; if (tutup > sampai) sampai = tutup; }
    else if (!belum || b.bulan > belum.bulan) belum = { bulan: b.bulan, hari: Number(r.hari) || 0, gaji: Number(r.gaji) || 0 }; });
  return { bulan, sampai, belum };
}
/** Sejak kapan hari kerja belum dibayar: slip terakhir + 1 → tanggal bayar terakhir sistem lama + 1 → hari kerja pertama yang tercatat → hari ini;
 *  lalu dinaikkan oleh setelan owner per orang: "hitung upah sejak" / tanggal masuk (tidak pernah mundur ke hari yang sudah dibayar). */
export function mulaiUpah(nama, iso) {
  const k = upKunci(nama); let sampai = ''; ambilSlipUpah().forEach((s) => { if (s.jenis === 'bonus') return; if (upKunci(s.nama) === k && (s.sampai || '') > sampai) sampai = s.sampai; });   // slip bonus tidak menutup hari kerja
  let M;
  if (sampai) M = { mulai: ugTambahHari(sampai, 1), sumber: 'slip', teks: 'sejak slip terakhir (' + tanggalPendek(sampai) + ')' };
  else {
    const L = upBulanLamaTerakhir(nama);
    if (L.sampai) M = { mulai: ugTambahHari(L.sampai, 1), sumber: 'lama', teks: L.sampai === akhirBulanIso(L.bulan) ? 'sejak gaji bulan ' + L.bulan + ' dibayar di sistem lama' : 'sejak gaji terakhir dibayar ' + tanggalPendek(L.sampai) + ' di sistem lama', belumLama: L.belum };
    else { const h = hariKerja(nama); const t = Object.keys(h).sort()[0] || ''; M = t && t <= iso ? { mulai: t, sumber: 'absen', teks: 'sejak hari kerja pertama yang tercatat', belumLama: L.belum } : { mulai: iso, sumber: 'kosong', teks: 'belum ada hari kerja yang tercatat', belumLama: L.belum }; }
  }
  // setelan per orang (lembar Karyawan): "hitung upah sejak" lalu tanggal masuk — tidak pernah membuka lagi hari yang sudah tertutup pembayaran (slip / gaji lama)
  const O = orangUpah(nama); const tertutup = M.sumber === 'slip' || M.sumber === 'lama' ? ugTambahHari(M.mulai, -1) : '';
  if (O.mulaiHitung && (!tertutup || O.mulaiHitung > tertutup)) M = Object.assign({}, M, { mulai: O.mulaiHitung, sumber: 'atur', teks: 'sejak ' + tanggalPendek(O.mulaiHitung) + ' (diatur owner di Karyawan)' });
  else if (O.masuk && (!tertutup || O.masuk > tertutup) && O.masuk !== M.mulai) M = Object.assign({}, M, { mulai: O.masuk, sumber: 'masuk', teks: 'sejak mulai kerja ' + tanggalPendek(O.masuk) });
  return M;
}
/** Potongan "Potong gaji" lama yang belum tertutup baris gaji bernama polos — mesin lama akan memotongnya ke baris gaji berikutnya bernama sama. Baris baru sistem baru kebal (kunci bertanggal). */
export function potongLamaMenggantung(nama) {
  const nm = String(nama).trim(); let potong = 0, kotor = 0;
  ambilKasbonMutasi().forEach((m) => { if (m.tipe === 'bayar' && String(m.namaPegawai || '').trim() === nm && String(m.caraBayar || '').trim().toLowerCase() === 'potong gaji') potong += Number(m.nominal) || 0; });
  ambilBiayaBulanan().forEach((b) => (b.rincianGaji || []).forEach((r) => { if (String(r.nama || '').trim() === nm && Number(r.gaji) > 0) kotor += Number(r.gaji) || 0; }));
  return Math.max(0, Math.round(potong - kotor));
}
export const ALASAN_BONUS = ['Rajin', 'Lembur', 'Hari raya', 'Bantu bongkar', 'Lain-lain'];
const upBonus = (b) => { const n = Math.round(ugAngka(b && b.ketik !== undefined ? b.ketik : b)); return n > 0 ? n : 0; };
/** Hitung satu orang — dibaca kartu, buku, panel bayar, dan slip (satu tempat). potongPilih = semua | separuh | tidak; bonus = {ketik, alasan} (owner 23 Sep: bonus karyawan) ikut DITERIMA & biaya gaji. */
export function hitungUpah(nama, kini, potongPilih, bonusIsi) {
  const iso = hariIniIso(kini); const A = aturUpah(); const M = mulaiUpah(nama, iso); const h = hariKerja(nama); const O = orangUpah(nama);
  // karyawan yang sudah berhenti: hari sesudah tanggal berhentinya tidak dihitung (upah yang tertinggal tetap bisa dibayar)
  const akhir = O.berhenti && O.berhenti < iso ? O.berhenti : iso;
  let penuh = 0, setengah = 0, absen = 0, kosong = 0, kosongLama = 0; const hariList = []; const rincianTarif = [];
  // putaran 29: tarif dibaca PER HARI (upah per orang bertanggal berlaku); hari yang tarifnya sama dirangkum jadi satu ruas rincian
  if (M.mulai <= akhir) for (let t = M.mulai; t <= akhir; t = ugTambahHari(t, 1)) { const x = h[t]; const T = tarifHariPada(nama, t, A); const rp = x === 1 || x === 0.5 ? upNilaiHari(x, T.tarifHari) : 0;
    hariList.push({ iso: t, nilai: x === undefined ? null : x, tarifHari: T.tarifHari, rp }); if (x === 1) penuh += 1; else if (x === 0.5) setengah += 1; else if (x === 0) absen += 1; else { kosong += 1; if (t < iso) kosongLama += 1; }
    let r = rincianTarif[rincianTarif.length - 1]; if (!r || r.tarifHari !== T.tarifHari || r.satuan !== T.satuan || r.tarif !== T.tarif || r.mulaiBerlaku !== T.mulai) { r = { mulai: t, sampai: t, penuh: 0, setengah: 0, upah: 0, tarifHari: T.tarifHari, satuan: T.satuan, tarif: T.tarif, pembagi: T.pembagi, mulaiBerlaku: T.mulai, sumber: T.sumber, teks: T.teks }; rincianTarif.push(r); }
    r.sampai = t; if (x === 1) r.penuh += 1; else if (x === 0.5) r.setengah += 1; r.upah += rp; }
  const upah = rincianTarif.reduce((a, r) => a + r.upah, 0); const TK = tarifHariPada(nama, iso, A);
  const kb = hitungKasbon().find((x) => x.kunci === upKunci(nama)); const sisaKasbon = kb ? Math.max(0, kb.sisa) : 0;
  const bonus = upBonus(bonusIsi); const alasanBonus = bonusIsi && bonusIsi.alasan ? String(bonusIsi.alasan) : '';
  const potong = potongPilih === 'tidak' ? 0 : Math.min(upah + bonus, potongPilih === 'separuh' ? Math.round(sisaKasbon / 2 / 1000) * 1000 : sisaKasbon);
  const nHari = hariList.length;
  return { nama, tarif: TK.tarifHari, satuan: TK.satuan, tarifAsli: TK.tarif, tarifTeks: TK.teks, sumberTarif: TK.sumber, rincianTarif, tarifBeragam: rincianTarif.length > 1, mulai: M.mulai, akhir, sumberMulai: M.sumber, mulaiTeks: M.teks, belumLama: M.belumLama || null, iso, nHari, hariList, penuh, setengah, absen, kosong, kosongLama, upah, bonus, alasanBonus, sisaKasbon, potong, diterima: upah + bonus - potong, bawaPulang: upah - Math.min(upah, sisaKasbon),
    status: O.status, berhenti: O.berhenti, peran: O.peran, masuk: O.masuk,
    rentang: M.mulai <= akhir ? tanggalPendek(M.mulai) + ' – ' + tanggalPendek(akhir) : 'tidak ada hari yang belum dibayar', hariTeks: teksHariUpah({ penuh, setengah, absen }), potongLama: potongLamaMenggantung(nama), kasbonMutasi: kb ? kb.mutasi : [] };
}
export function teksHariUpah(c) { const b = []; if (c.penuh) b.push(c.penuh + ' hari penuh'); if (c.setengah) b.push(c.setengah + ' setengah hari'); if (c.absen) b.push(c.absen + ' tidak masuk'); return b.length ? b.join(' · ') : 'belum ada hari kerja'; }
/** Semua karyawan + hitungannya (kartu). */
export function semuaUpah(kini) { const A = aturUpah(); return A.aktif.map((o) => Object.assign({ peran: o.peran }, hitungUpah(o.nama, kini, 'semua'))); }
/** Buku upah: hari kerja beruntun dirangkum, kasbon diselipkan menurut tanggal, saldo berjalan = kalau pulang hari ini. */
export function bukuUpah(nama, kini) {
  const H = hitungUpah(nama, kini, 'semua'); const rows = []; let jalan = 0; let a = null, nilai = null, th = 0;
  const kasbonAmbil = ambilKasbonMutasi().filter((m) => m.tipe === 'ambil' && upKunci(m.namaPegawai) === upKunci(nama) && (m.tanggal || '') >= H.mulai && (m.tanggal || '') <= H.iso);
  const tutup = (sampai) => { if (a === null) return; const jml = ugHariKe(sampai) - ugHariKe(a) + 1; const tgl = a === sampai ? tanggalPendek(a) : tanggalPendek(a) + ' – ' + tanggalPendek(sampai);
    if (nilai === 1 || nilai === 0.5) { const r = jml * upNilaiHari(nilai, th); jalan += r; rows.push({ tgl, ket: jml + (nilai === 1 ? ' hari penuh' : ' setengah hari') + ' × ' + RP(upNilaiHari(nilai, th)), n: r, s: jalan, jenis: 'kerja' }); }
    else if (nilai === 0) rows.push({ tgl, ket: jml + ' hari tidak masuk', n: 0, s: jalan, jenis: 'absen' });
    else rows.push({ tgl, ket: jml + ' hari BELUM DIISI', n: null, s: jalan, jenis: 'kosong' }); a = null; };
  H.hariList.forEach((d) => { const kb = kasbonAmbil.filter((m) => m.tanggal === d.iso); const x = d.nilai === null ? undefined : d.nilai;
    if (a !== null && (x !== nilai || d.tarifHari !== th)) tutup(ugTambahHari(d.iso, -1)); if (a === null) { a = d.iso; nilai = x; th = d.tarifHari; }
    if (kb.length) { tutup(d.iso); kb.forEach((m) => { jalan -= Number(m.nominal) || 0; rows.push({ tgl: tanggalPendek(m.tanggal), ket: 'kasbon · ' + (m.catatan || ''), n: -(Number(m.nominal) || 0), s: jalan, jenis: 'kasbon' }); }); } });
  if (H.hariList.length) tutup(H.iso);
  return { rows, jalan, H };
}
/** Tujuh hari terakhir & satu bulan untuk diketuk: nilai per tanggal + apakah boleh diubah (belum dibayar & tidak di masa depan). */
export function kalenderUpah(nama, kini, nHari) {
  const H = hitungUpah(nama, kini, 'semua'); const h = hariKerja(nama); const out = [];
  for (let i = (nHari || 7) - 1; i >= 0; i--) { const t = ugTambahHari(H.iso, -i); const x = h[t]; const bisa = t >= H.mulai && t <= H.akhir; const lewat = t > H.akhir; out.push({ iso: t, tgl: String(parseInt(t.slice(8, 10), 10)), hari: ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'][new Date(t + 'T00:00:00Z').getUTCDay()], nilai: x === undefined ? null : x, bisa, kelas: !bisa ? 'lunas' : x === undefined ? 'kosong' : x === 1 ? 'penuh' : x === 0.5 ? 'setengah' : 'absen', k: lewat ? 'stop' : !bisa ? 'lunas' : x === undefined ? 'isi' : x === 1 ? 'penuh' : x === 0.5 ? '½' : 'tdk', ini: t === H.iso }); }
  return out;
}
export const putarHari = (x) => (x === null || x === undefined ? 1 : x === 1 ? 0.5 : x === 0.5 ? 0 : null);   // kosong → penuh → setengah → tidak masuk → kosong
/** Tulis hari kerja satu tanggal (nilai null = kosongkan). Hari yang sudah dibayar (sebelum mulai) atau di masa depan ditolak. */
export function susunAbsen(nama, iso, nilai, w) {
  if (!nama) return { tolak: 'Pilih orangnya dulu' }; if (iso > w.tanggal) return { tolak: 'Hari itu belum datang' };
  const M = mulaiUpah(nama, w.tanggal); if (iso < M.mulai) return { tolak: tanggalPendek(iso) + ' sudah termasuk upah yang dibayar — tidak bisa diubah lagi' };
  const O = orangUpah(nama); if (O.berhenti && iso > O.berhenti) return { tolak: nama + ' sudah berhenti sejak ' + tanggalPendek(O.berhenti) + ' — aktifkan lagi di Karyawan kalau ia kembali bekerja' };
  if (nilai !== null && nilai !== 1 && nilai !== 0.5 && nilai !== 0) return { tolak: 'Nilai hari tidak dikenal' };
  const bulan = iso.slice(0, 7); const id = upKunci(nama) + '|' + bulan; const lama = ambilAbsenKaryawan().find((a) => String(a.id) === id) || { id, nama: String(nama).trim(), bulan, hari: {} };
  const hari = Object.assign({}, lama.hari || {}); if (nilai === null) delete hari[iso]; else hari[iso] = nilai;
  return { dokumen: [{ koleksi: 'absenKaryawan', data: { id, nama: lama.nama || String(nama).trim(), bulan, hari, diubahTanggal: w.tanggal, diubahJam: w.jam } }], patch: { kabar: '', kabarAwas: false } };
}
/** Kasbon karyawan dari laci: kasbonMutasi {tipe ambil} sistem lama + jam & dari. */
export function hitungKasbonKaryawan(nama, ketik, alasan) {
  const n = Math.round(ugAngka(ketik)); const S = saldoKantong(); let tolak = ''; let c = { boleh: true };
  if (!nama) tolak = 'Pilih orangnya dulu'; else if (!(n > 0)) tolak = 'Isi nominalnya dulu'; else if (!alasan) tolak = 'Pilih untuk apa'; else { c = ugCukup(S, 'laci', n); if (!c.boleh) tolak = c.teks; }
  const kb = hitungKasbon().find((x) => x.kunci === upKunci(nama)); const sisa = kb ? Math.max(0, kb.sisa) : 0;
  return { n, tolak, sisa, S, takTerperiksa: !!c.takTerperiksa, arti: 'Laci berkurang ' + RP(n) + ' · laba tidak berubah · ' + String(nama || '').split(' ')[0] + ' jadi berutang ' + RP(sisa + n) + ' ke toko' };
}
export function susunKasbonKaryawan(nama, ketik, alasan, w) {
  const H = hitungKasbonKaryawan(nama, ketik, alasan); if (H.tolak) return { tolak: H.tolak };
  const data = { id: w.idUnik(), tipe: 'ambil', namaPegawai: String(nama).trim(), nominal: H.n, tanggal: w.tanggal, jam: w.jam, catatan: String(alasan).slice(0, 60), dari: 'laci' };
  return { dokumen: [{ koleksi: 'kasbonMutasi', data }], urung: [{ koleksi: 'kasbonMutasi', id: data.id }], patch: { kabar: 'Kasbon ' + String(nama).split(' ')[0] + ' ' + RP(H.n) + ' tercatat · laci berkurang ' + RP(H.n) + (H.takTerperiksa ? ' · isi laci belum bisa dihitung, tidak diperiksa' : ''), kabarAwas: false, kasbonK: null } };
}
const UP_POTONG = [['semua', 'Potong semua'], ['separuh', 'Potong separuh'], ['tidak', 'Jangan dipotong']];
export { UP_POTONG as PILIHAN_POTONG };
/** Susun slip (teks) dari hitungan. */
export function teksSlip(H, tglBayar) {
  const L = ['TOKO BERAS M.IQBAL', 'Slip upah · ' + H.nama, H.rentang, ''];
  // putaran 29: tiap ruas tarif dirinci (upah per orang bisa berganti di tengah rentang; satuan minggu/bulan menyebut pembaginya)
  const ruas = (H.rincianTarif || []).filter((r) => r.penuh || r.setengah);
  ruas.forEach((r) => { if (ruas.length > 1 || r.satuan !== 'hari') L.push((ruas.length > 1 ? tanggalPendek(r.mulai) + ' – ' + tanggalPendek(r.sampai) + ' · ' : '') + (r.satuan === 'hari' ? RP(r.tarif) + ' sehari' : RP(r.tarif) + (r.satuan === 'minggu' ? ' seminggu' : ' sebulan') + ' ÷ ' + r.pembagi + ' hari = ' + RP(r.tarifHari) + ' sehari'));
    if (r.penuh) L.push(r.penuh + ' hari penuh × ' + RP(r.tarifHari) + ' = ' + RP(r.penuh * r.tarifHari));
    if (r.setengah) L.push(r.setengah + ' setengah hari × ' + RP(upNilaiHari(0.5, r.tarifHari)) + ' = ' + RP(r.setengah * upNilaiHari(0.5, r.tarifHari))); });
  if (H.absen) L.push(H.absen + ' hari tidak masuk');
  L.push('Upah               ' + RP(H.upah)); if (H.bonus) L.push('Bonus' + (H.alasanBonus ? ' (' + H.alasanBonus + ')' : '') + '   +' + RP(H.bonus)); if (H.potong) L.push('Potong kasbon     −' + RP(H.potong).replace('−', '')); L.push('DITERIMA           ' + RP(H.diterima)); L.push('Sisa kasbon        ' + RP(H.sisaKasbon - H.potong));
  L.push('', 'Dibayar ' + tanggalPendek(tglBayar) + ' dari laci toko'); return L.join('\n');
}
/** Bayar upah: biayaBulanan per bulan tercakup (baris berkunci "Nama · tanggal") + kasbon 'Dipotong upah' + slipUpah. Ditolak bila ada hari belum diisi, upah nol, atau laci kurang. */
export function susunBayarUpah(nama, potongPilih, w, bonusIsi) {
  const H = hitungUpah(nama, ugKiniDari(w), potongPilih || 'semua', bonusIsi);
  if (H.bonus > 10000000) return { tolak: 'Bonus paling banyak 10.000.000' }; if (H.bonus > 0 && !H.alasanBonus) return { tolak: 'Pilih alasan bonusnya' };
  if (!H.nHari) return { tolak: 'Tidak ada hari yang belum dibayar untuk ' + nama }; if (H.kosongLama > 0) return { tolak: H.kosongLama + ' hari belum diisi — ini BUKAN "tidak masuk". Isi dulu sebelum upah dibayar' };
  if (!(H.upah > 0)) return { tolak: 'Belum ada hari kerja yang bisa dibayar' };
  const S = saldoKantong(); const c = ugCukup(S, 'laci', H.diterima); if (!c.boleh) return { tolak: c.teks };
  // hari ini yang masih kosong TIDAK ikut dibayar — slip berhenti di hari terakhir yang terisi
  const terisi = H.hariList.filter((d) => d.nilai !== null); const sampai = terisi.length ? terisi[terisi.length - 1].iso : H.iso;
  const kunci = String(nama).trim() + ' · ' + tanggalPendek(w.tanggal); const perBulan = {};
  // putaran 29: rupiah per bulan dijumlah dari rupiah tiap hari (tarif per orang bisa berganti di tengah rentang) — Σ bulan = H.upah persis
  H.hariList.forEach((d) => { if (d.nilai === null || d.iso > sampai) return; const b = d.iso.slice(0, 7); if (!perBulan[b]) perBulan[b] = { hari: 0, penuh: 0, setengah: 0, absen: 0, upah: 0 }; perBulan[b].hari += d.nilai; perBulan[b].upah += d.rp; if (d.nilai === 1) perBulan[b].penuh += 1; else if (d.nilai === 0.5) perBulan[b].setengah += 1; else perBulan[b].absen += 1; });
  const dokumen = []; const bulanan = [];
  // putaran 25 (K5, owner 25 Sep): hari kerja di bulan TERKUNCI dibukukan ke biaya bulan PEMBAYARAN (bulan terkunci tidak bisa ditulis lagi); rincian gajinya
  // tetap membawa dari/sampai yang sebenarnya. Tanpa field baru.
  const bulanBayar = String(w.tanggal).slice(0, 7); const pindahBulan = [];
  Object.keys(perBulan).forEach((b) => { if (b === bulanBayar || !tolakKunciTanggal(b + '-01', '')) return; const t = perBulan[bulanBayar] = perBulan[bulanBayar] || { hari: 0, penuh: 0, setengah: 0, absen: 0, upah: 0 };
    ['hari', 'penuh', 'setengah', 'absen', 'upah'].forEach((k) => { t[k] += perBulan[b][k]; }); pindahBulan.push(b); delete perBulan[b]; });
  const bulanAkhir = Object.keys(perBulan).sort().slice(-1)[0];
  Object.keys(perBulan).sort().forEach((bulan) => { const p = perBulan[bulan]; const bonusIni = bulan === bulanAkhir ? H.bonus : 0; const gaji = Math.round(p.upah) + bonusIni; const lama = ambilBiayaBulanan().find((b) => b.bulan === bulan) || { id: bulan, bulan };
    const data = Object.assign({}, lama, { id: bulan, bulan }); const peta = Object.assign({}, lama.tanggalBayarPos || {}); if (!lama.tanggalBayarPos && lama.tanggalBayar) { POS_BIAYA_BULANAN.forEach((q) => { if (Number(lama[q.kunci]) > 0) peta[q.kunci] = lama.tanggalBayar; }); if (Number(lama.gaji) > 0) peta.gaji = lama.tanggalBayar; }
    data.tanggalBayarPos = peta; ['akses', 'keamanan', 'listrik', 'internet'].forEach((k) => { if (data[k] === undefined) data[k] = 0; });
    const rincian = (lama.rincianGaji || []).filter((r) => r.nama !== kunci).concat([Object.assign({ nama: kunci, hari: p.hari, gaji, orang: String(nama).trim(), dari: H.mulai, sampai, sistemBaru: true }, bonusIni ? { bonus: bonusIni, alasanBonus: H.alasanBonus } : {})]);
    data.rincianGaji = rincian; data.gaji = rincian.reduce((a, r) => a + (Number(r.gaji) || 0), 0); data.gajiHariOrang = rincian.reduce((a, r) => a + (Number(r.hari) || 0), 0);
    data.tanggalBayarGaji = Object.assign({}, lama.tanggalBayarGaji || {}, { [kunci]: w.tanggal }); data.dariPos = Object.assign({}, lama.dariPos || {}, { ['gaji:' + kunci]: 'laci' });
    dokumen.push({ koleksi: 'biayaBulanan', data }); bulanan.push({ bulan, hari: p.hari, gaji, kunci }); });
  if (H.potong > 0) dokumen.push({ koleksi: 'kasbonMutasi', data: { id: w.idUnik(), tipe: 'bayar', namaPegawai: String(nama).trim(), nominal: H.potong, tanggal: w.tanggal, jam: w.jam, caraBayar: 'Dipotong upah', catatan: 'dipotong dari upah ' + H.rentang, dari: 'laci' } });
  const rincianTarif = H.rincianTarif.filter((r) => r.mulai <= sampai).map((r) => ({ mulai: r.mulai, sampai: r.sampai < sampai ? r.sampai : sampai, penuh: r.penuh, setengah: r.setengah, upah: r.upah, tarifHari: r.tarifHari, satuan: r.satuan, tarif: r.tarif, pembagi: r.pembagi }));
  const HS = Object.assign({}, H, { rentang: tanggalPendek(H.mulai) + ' – ' + tanggalPendek(sampai), rincianTarif }); const slip = teksSlip(HS, w.tanggal);
  // slipUpah: `tarif` = tarif harian yang berlaku hari ini (bentuk lama); `satuan` & `rincianTarif` (putaran 29) merinci tiap ruas tarif dalam rentang yang dibayar
  const dokSlip = { id: w.idUnik(), nama: String(nama).trim(), dari: H.mulai, sampai, tanggal: w.tanggal, jam: w.jam, penuh: H.penuh, setengah: H.setengah, absen: H.absen, tarif: H.tarif, satuan: H.satuan, rincianTarif, upah: H.upah, bonus: H.bonus, alasanBonus: H.alasanBonus, potong: H.potong, diterima: H.diterima, sisaKasbon: H.sisaKasbon - H.potong, bulanan, kunci, teks: slip };
  dokumen.push({ koleksi: 'slipUpah', data: dokSlip });
  return { dokumen, slip: dokSlip, patch: { bonusU: { ketik: '', alasan: '' }, kabar: 'Upah ' + String(nama).split(' ')[0] + ' ' + RP(H.diterima) + ' dibayar dari laci' + (H.bonus ? ' · bonus ' + RP(H.bonus) + ' (' + H.alasanBonus + ')' : '') + (H.potong ? ' · kasbon dipotong ' + RP(H.potong) : '') + ' · laba: gaji penuh ' + RP(H.upah) + ' dibagi rata per hari bulannya' + (H.tarifBeragam ? ' · dua tarif dalam rentang ini, dirinci di slip' : '') + (c.takTerperiksa ? ' · isi laci belum bisa dihitung, tidak diperiksa' : '') + (pindahBulan.length ? ' · hari kerja ' + pindahBulan.join(', ') + ' (bulan terkunci) dibukukan ke biaya ' + bulanBayar : ''), kabarAwas: false, bayarU: null, lembarU: 'slip', slipTeks: slip } };
}
/** Slip yang sudah dibayar (sistem baru) + gaji bulanan sistem lama yang bertanggal, terbaru di atas. */
export function riwayatUpah(nama, n) {
  const k = nama ? upKunci(nama) : null; const rows = ambilSlipUpah().filter((s) => !k || upKunci(s.nama) === k).map((s) => ({ id: String(s.id), nama: s.nama, tanggal: s.tanggal, jam: s.jam || '', ket: s.jenis === 'bonus' ? 'bonus ' + tanggalPendek(s.tanggal) + (s.alasanBonus ? ' · ' + s.alasanBonus : '') + ' (tanpa hari kerja)' : 'dibayar ' + tanggalPendek(s.tanggal) + ' · ' + tanggalPendek(s.dari) + ' – ' + tanggalPendek(s.sampai) + ' · ' + s.penuh + ' penuh' + (s.setengah ? ' + ' + s.setengah + ' setengah' : '') + (s.bonus ? ' · bonus ' + RP(s.bonus) : '') + (s.potong ? ' · potong kasbon ' + RP(s.potong) : ''), n: Number(s.diterima) || 0, teks: s.teks || '', jenis: 'slip' }));
  ambilBiayaBulanan().forEach((b) => (b.rincianGaji || []).forEach((r) => { if (r.sistemBaru || !(Number(r.gaji) > 0)) return; if (k && upKunci(r.nama) !== k) return; const tgl = (b.tanggalBayarGaji && b.tanggalBayarGaji[r.nama]) || (b.tanggalBayarPos ? b.tanggalBayarPos.gaji || '' : '') || b.tanggalBayar || '';
    rows.push({ id: 'lama|' + b.bulan + '|' + r.nama, nama: r.nama, tanggal: tgl || b.bulan + '-99', jam: '', ket: (tgl ? 'dibayar ' + tanggalPendek(tgl) : 'BELUM dibayar') + ' · gaji bulan ' + b.bulan + ' · ' + (Number(r.hari) || 0) + ' hari (sistem lama)', n: Number(r.gaji) || 0, teks: '', jenis: tgl ? 'lama' : 'lamaBelum' }); }));
  rows.sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || String(b.jam).localeCompare(String(a.jam))); return rows.slice(0, n || 20);
}

/** Lembar KARYAWAN (HR, owner 23 Sep: salah satu karyawan giliran sepertinya sudah pensiun): tiap orang dengan status, sejak kapan, hari kerja bulan ini, upah belum dibayar, kasbon, total yang pernah dibayar. */
export function daftarKaryawan(kini) {
  const A = aturUpah(); const iso = hariIniIso(kini); const bulan = iso.slice(0, 7);
  const semuaSlip = ambilSlipUpah(); const bayarLama = {}; ambilBiayaBulanan().forEach((b) => (b.rincianGaji || []).forEach((r) => { if (r.sistemBaru || !(Number(r.gaji) > 0)) return; const k = upKunci(String(r.nama || '').replace(/ · .*$/, '')); bayarLama[k] = (bayarLama[k] || 0) + (Number(r.gaji) || 0); }));
  const baris = A.orang.map((o) => { const H = hitungUpah(o.nama, kini, 'semua'); const h = hariKerja(o.nama); const bulanIni = Object.keys(h).filter((t) => t.slice(0, 7) === bulan).reduce((a, t) => a + (h[t] > 0 ? 1 : 0), 0);
    const dibayar = semuaSlip.filter((x) => upKunci(x.nama) === upKunci(o.nama)).reduce((a, x) => a + (Number(x.diterima) || 0), 0) + (bayarLama[upKunci(o.nama)] || 0);
    const tercatat = Object.keys(h).sort(); const sejak = o.masuk || (tercatat[0] || '');
    return Object.assign({}, o, { aktif: o.status === 'aktif', upahBelum: H.upah, kasbon: H.sisaKasbon, hariBulanIni: bulanIni, dibayar, sejak, mulaiTeks: H.mulaiTeks, upahKini: tarifHariPada(o.nama, iso, A),
      ket: (o.status === 'aktif' ? (sejak ? 'sejak ' + tanggalPendek(sejak) : 'belum ada catatan') : 'berhenti ' + (o.berhenti ? tanggalPendek(o.berhenti) : '')) + (H.upah > 0 ? ' · upah belum dibayar ' + RP(H.upah) : '') + (H.sisaKasbon > 0 ? ' · kasbon ' + RP(H.sisaKasbon) : ''),
      awas: o.status !== 'aktif' && (H.upah > 0 || H.sisaKasbon > 0) }); });
  return { baris, aktif: baris.filter((b) => b.aktif), berhenti: baris.filter((b) => !b.aktif), tarif: A.tarif, dariOwner: A.dariOwner, orangTerukur: A.orangTerukur };
}
export const KOLOM_KARYAWAN = [['nama', 'Nama', 'text'], ['peran', 'Peran (tetap / giliran)', 'text'], ['masuk', 'Mulai kerja', 'date'], ['mulaiHitung', 'Hitung upah sejak (kosong = otomatis)', 'date'], ['catatan', 'Catatan', 'text']];

/** BONUS tanpa hari kerja (mis. hari raya, sesudah gajian): baris gaji bulan ini berkunci "Nama · bonus · tanggal", hari 0 — mesin lama membacanya sebagai biaya gaji (jatah per hari) & kas keluar di tanggal bayar; slipUpah jenis 'bonus'. */
export function susunBonus(nama, bonusIsi, w) {
  const bonus = upBonus(bonusIsi); const alasan = bonusIsi && bonusIsi.alasan ? String(bonusIsi.alasan) : '';
  if (!nama) return { tolak: 'Pilih orangnya dulu' }; if (!(bonus > 0)) return { tolak: 'Isi bonusnya dulu' }; if (bonus > 10000000) return { tolak: 'Bonus paling banyak 10.000.000' }; if (!alasan) return { tolak: 'Pilih alasan bonusnya' };
  const S = saldoKantong(); const c = ugCukup(S, 'laci', bonus); if (!c.boleh) return { tolak: c.teks };
  const bulan = w.tanggal.slice(0, 7); const kunci = String(nama).trim() + ' · bonus · ' + tanggalPendek(w.tanggal); const lama = ambilBiayaBulanan().find((b) => b.bulan === bulan) || { id: bulan, bulan };
  const data = Object.assign({}, lama, { id: bulan, bulan }); const peta = Object.assign({}, lama.tanggalBayarPos || {}); if (!lama.tanggalBayarPos && lama.tanggalBayar) { POS_BIAYA_BULANAN.forEach((q) => { if (Number(lama[q.kunci]) > 0) peta[q.kunci] = lama.tanggalBayar; }); if (Number(lama.gaji) > 0) peta.gaji = lama.tanggalBayar; }
  data.tanggalBayarPos = peta; ['akses', 'keamanan', 'listrik', 'internet'].forEach((k) => { if (data[k] === undefined) data[k] = 0; });
  const rincian = (lama.rincianGaji || []).filter((r) => r.nama !== kunci).concat([{ nama: kunci, hari: 0, gaji: bonus, bonus, alasanBonus: alasan, orang: String(nama).trim(), sistemBaru: true }]);
  data.rincianGaji = rincian; data.gaji = rincian.reduce((a, r) => a + (Number(r.gaji) || 0), 0); data.gajiHariOrang = rincian.reduce((a, r) => a + (Number(r.hari) || 0), 0);
  data.tanggalBayarGaji = Object.assign({}, lama.tanggalBayarGaji || {}, { [kunci]: w.tanggal }); data.dariPos = Object.assign({}, lama.dariPos || {}, { ['gaji:' + kunci]: 'laci' });
  const teks = ['TOKO BERAS M.IQBAL', 'Bonus · ' + String(nama).trim(), tanggalPendek(w.tanggal), '', 'Bonus (' + alasan + ')   ' + RP(bonus), 'DITERIMA           ' + RP(bonus), '', 'Dibayar ' + tanggalPendek(w.tanggal) + ' dari laci toko'].join('\n');
  const dokSlip = { id: w.idUnik(), jenis: 'bonus', nama: String(nama).trim(), dari: w.tanggal, sampai: w.tanggal, tanggal: w.tanggal, jam: w.jam, penuh: 0, setengah: 0, absen: 0, tarif: tarifHariPada(nama, w.tanggal).tarifHari, upah: 0, bonus, alasanBonus: alasan, potong: 0, diterima: bonus, sisaKasbon: 0, bulanan: [{ bulan, hari: 0, gaji: bonus, kunci }], kunci, teks };
  return { dokumen: [{ koleksi: 'biayaBulanan', data }, { koleksi: 'slipUpah', data: dokSlip }], slip: dokSlip,
    patch: { bonusU: { ketik: '', alasan: '' }, kabar: 'Bonus ' + String(nama).split(' ')[0] + ' ' + RP(bonus) + ' (' + alasan + ') dibayar dari laci · laba: masuk biaya gaji bulan ' + bulan + ' (mesin lama, dibagi rata per hari)' + (c.takTerperiksa ? ' · isi laci belum bisa dihitung, tidak diperiksa' : ''), kabarAwas: false, lembarU: 'slip', slipTeks: teks } };
}
