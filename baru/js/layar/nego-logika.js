// BATAS NEGO PER ORANG (JS2-C "Buku Nego", dikunci owner 18 Sep 2026; dibangun owner 7 Okt) — tanpa DOM, dijaga alat-uji/uji_jual_nego.py di jsc.
// Aturan rancangan (angkanya SETELAN owner di Menu › Sistem › Peran › Atur, bawaan dari rancangan):
//  - jatah tiap orang = sekian PERSEN dari MARGIN barang (harga katalog − modal): owner 100 % (sampai modal), Ben 50 %, karyawan giliran 0 % (tidak boleh nego);
//    owner boleh mengatur jatah per peran dan per akun (akun yang diatur sendiri menang atas perannya);
//  - batas harga = katalog − margin × jatah, dibulatkan ke LANGKAH (bawaan Rp500) ke ATAS supaya tidak melewati jatah; tidak pernah di atas katalog;
//  - di bawah jatah → MINTA OWNER lewat koleksi persetujuan (papan yang sama dengan Menu › Sistem › Peran › Persetujuan); harga nota TIDAK berubah
//    sampai owner menyetujui (rancangan: "harga notanya belum berubah sampai disetujui");
//  - di bawah MODAL → hanya orang yang diizinkan (bawaan: owner) DAN dengan alasan tertulis; bukan-owner tetap lewat persetujuan owner;
//  - modal belum tercatat → batas belum bisa dihitung: owner boleh (diberi tahu), bukan-owner minta owner (paling aman untuk uang);
//  - tiap nego tercatat di baris nota: siapa (atribusi oleh/olehUid), barang, harga katalog (hargaAsliSatuan), selisih (negoSelisih) + negoStatus,
//    negoBatas, negoJatah, negoAlasan, negoSetujuId. Owner melihat / menyetujui / menolak di Buku Nego (layar Jual).
// Nama diprefiks `ng` karena bundel uji jsc satu lingkup.
import { cacheMentah, ambilPenjualan, ambilHargaKemasan, ambilHargaLiteran, petaUkuran } from '../data/toko.js';
import { NEGO_LANTAI, kunciKemasan, hargaKarungUtuh, cariHargaKarungPerKg } from '../mesin/pembantu.js';
import { RP } from '../inti/format.js';
// owner 23 Nov 2026: bonus +1 staf masuk jatah nego — rumus batasnya satu dengan penjaga kiriman
import { bonusDalamBatas } from '../data/akses.js';
// B1: nego di atas harga pelanggan bertingkat
import { htHarga, htKgBarang } from './harga-tingkat-logika.js';

// owner 7 Okt: bawaan = angka rancangan JS2 (owner 100 tetap, Ben 50, karyawan giliran 0, owner boleh di bawah modal dengan alasan, langkah Rp500)
export const NG_BAWAAN = { ben: 50, karyawan: 0, langkah: 500, bawahModal: ['owner'] };
export const NG_JATAH_OWNER = 100;
// kolom nego yang dibawa baris keranjang & ditulis ke dokumen penjualan (selain nego + negoSelisih yang sudah ada sejak putaran 2)
export const NG_KOLOM = ['negoStatus', 'negoBatas', 'negoJatah', 'negoAlasan', 'negoSetujuId'];
// owner 23 Nov 2026: tanda bonus +1 di baris keranjang & nota — status ('owner' · 'jatah' · 'disetujui'), jatah yang dipakai, persetujuan owner (sekali pakai),
// nilai bonus (harga katalog unit gratis) untuk Buku Nego
export const NG_KOLOM_BONUS = ['bonusStatus', 'bonusJatah', 'bonusSetujuId', 'bonusNilai'];
export const NG_LABEL = { jatah: 'dalam jatah', naik: 'di atas harga katalog', disetujui: 'disetujui owner', bawahModal: 'di bawah modal', lama: 'nego (sebelum ada batas nego)',
  menunggu: 'menunggu owner', ditolak: 'ditolak owner', dipakai: 'disetujui owner · sudah dipakai',
  bonusOwner: 'bonus dari owner', bonusJatah: 'bonus dalam jatah', bonusDisetujui: 'bonus disetujui owner', bonusLama: 'bonus (sebelum ada batas)' };

const ngPersen = (v, cadang) => { const n = Number(v); return v !== undefined && v !== null && v !== '' && isFinite(n) && n >= 0 && n <= 100 ? n : cadang; };
const ngOwner = (akun) => !akun || akun.jenis === 'owner';
/** Setelan nego yang berlaku: dokumen aturanToko/peran (Menu › Sistem › Peran › Atur) ditimpakan ke bawaan rancangan. */
export function ngAtur() {
  const d = cacheMentah('aturan').find((x) => String(x.id) === 'peran') || {};
  const jatahAkun = {};
  if (d.jatahAkun && typeof d.jatahAkun === 'object') Object.keys(d.jatahAkun).forEach((u) => { const n = ngPersen(d.jatahAkun[u], null); if (n !== null) jatahAkun[u] = n; });
  return { jatah: { owner: NG_JATAH_OWNER, ben: ngPersen(d.jatahBen, NG_BAWAAN.ben), karyawan: ngPersen(d.jatahKaryawan, NG_BAWAAN.karyawan) }, jatahAkun,
    bawahModal: Array.isArray(d.bawahModal) ? d.bawahModal.map(String) : NG_BAWAAN.bawahModal.slice(),
    langkah: Number(d.langkahNego) > 0 ? Math.round(Number(d.langkahNego)) : NG_BAWAAN.langkah };
}
/** Jatah nego (persen margin) akun ini: owner 100; akun yang diatur sendiri; selain itu menurut perannya. */
export function ngJatah(akun, A) {
  const a = A || ngAtur(); if (ngOwner(akun)) return NG_JATAH_OWNER;
  const u = String(akun.uid || ''); if (u && a.jatahAkun[u] !== undefined) return a.jatahAkun[u];
  return a.jatah[akun.peran] !== undefined ? a.jatah[akun.peran] : 0;
}
/** Boleh menjual di bawah modal (dengan alasan)? Daftar setelan: 'owner', id peran, atau 'uid:<uid>'. */
export function ngBolehBawahModal(akun, A) {
  const L = (A || ngAtur()).bawahModal;
  return ngOwner(akun) ? L.indexOf('owner') >= 0 : L.indexOf('uid:' + String(akun.uid || '')) >= 0 || L.indexOf(String(akun.peran || '')) >= 0;
}
const ngNama = (akun) => (ngOwner(akun) ? 'owner' : String(akun.nama || 'akun ini'));
/** Modal per satuan BAYAR (modal baris ÷ satuan yang dibayar pembeli). Kemasan berbonus: modal unit bonus ikut ditanggung unit yang dibayar — tinjauan 7 Okt:
 *  dulu dibagi unit + bonus, sehingga nego "dalam jatah" lalu bonus +1 membuat uang baris di bawah modalnya tanpa izin. Tanpa bonus = modal per unit seperti dulu.
 *  null = modal belum tercatat. */
export function ngModalSatuan(t) {
  const hpp = Number(t && t.hppTotalSaatJual); const j = Number(t && t.jumlah) || 0;
  return hpp > 0 && j > 0 ? hpp / j : null;
}
/** Harga paling rendah dalam jatah: katalog − margin × jatah, naik ke kelipatan langkah, tidak di atas katalog. null = modal belum tercatat. */
export function ngBatas(harga, modal, jatah, langkah) {
  if (!(harga > 0) || modal === null || !(modal > 0)) return null;
  const margin = harga - modal; if (margin <= 0) return harga;
  if ((Number(jatah) || 0) >= 100) return Math.min(harga, Math.ceil(modal - 1e-9));   // jatah penuh = sampai modal (rupiah bulat ke atas), tanpa langkah
  const L = langkah > 0 ? langkah : 1; const x = Math.round((harga - margin * (Number(jatah) || 0) / 100) * 100) / 100;
  return Math.min(harga, Math.ceil(x / L - 1e-9) * L);
}
/** Kunci barang satu baris keranjang / penjualan — sama dengan kunci Sering di jual-logika (satu rumus). */
export function ngKunciBarang(p) {
  if (!p) return null;
  if (p.jenis === 'kemasan') return 'kemasan|' + kunciKemasan(p.namaProduk, p.ukuranKemasan);
  if (p.jenis === 'karung') return 'karung|' + p.merkSumber + '|' + (p.beratKarungAcuan || 50);
  if (p.jenis === 'literan') return 'literan|' + (p.dariWadah || p.merkSumber);
  if (p.jenis === 'repacking') return 'repack|' + p.merkSumber;
  if (p.jenis === 'wadah') return 'wadah|' + p.jenisWadah;
  return null;
}
/** Tombol nego untuk akun ini: owner selalu; bukan-owner bila punya jatah ATAU kisi nego bukan "tidak boleh" (nego lebih dalam = minta owner).
 *  bisaMinta === false (server belum membuka permintaan ke owner): tanpa jatah tidak ada yang bisa dipakai → tombol mati dengan jalan keluarnya. */
export function ngBolehNego(akun, hakNego, A, bisaMinta) {
  if (ngOwner(akun)) return { boleh: true, kalimat: '' };
  if (ngJatah(akun, A) > 0) return { boleh: true, kalimat: '' };
  if (hakNego && hakNego !== 'tidak' && bisaMinta !== false) return { boleh: true, kalimat: '' };
  return { boleh: false, kalimat: ngNama(akun) + ' tidak punya jatah nego (0 % margin)' + (hakNego && hakNego !== 'tidak' ? ' dan minta owner dari perangkat ini belum bisa — jual di harga katalog, parkir struk ini sampai owner datang, atau owner yang mencatat nota ini' : ' — owner yang mengatur di Menu › Toko ini › Peran & persetujuan › Atur') };
}
/** Persetujuan owner yang SUDAH dipakai nota yang berlaku (sekali pakai) + yang sedang dipegang keranjang / struk parkir perangkat ini. */
function ngSetujuTerpakai(dipakai) {
  const o = {}; ambilPenjualan().forEach((p) => { if (p.negoSetujuId) o[String(p.negoSetujuId)] = 1; if (p.bonusSetujuId) o[String(p.bonusSetujuId)] = 1; });
  (dipakai || []).forEach((id) => { if (id) o[String(id)] = 1; });
  return o;
}
/** Persetujuan nego dari owner yang cocok untuk baris ini: milik akun ini, barang sama, harga disetujui ≤ harga yang diketik, jumlah ≤ yang diminta, belum dipakai. */
export function ngSetujuUntuk(t, harga, akun, opsi) {
  if (ngOwner(akun) || !t) return null;
  const o = opsi || {}; const k = ngKunciBarang(t);
  const calon = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && !m.bonus && m.status === 'disetujui' && String(m.negoUid || m.olehUid || '') === String(akun.uid || '')
    && m.barang === k && Number(m.hargaMinta) <= Number(harga) && Number(m.jumlah) >= Number(t.jumlah) && (!o.tanggal || m.tanggal === o.tanggal));
  if (!calon.length) return null;   // layar menanyakannya tiap gambar — nota berlaku baru dibaca kalau memang ada persetujuan yang cocok
  const pakai = ngSetujuTerpakai(o.dipakai);
  return calon.filter((m) => !pakai[String(m.id)]).sort((a, b) => Number(b.hargaMinta) - Number(a.hargaMinta) || String(b.id).localeCompare(String(a.id)))[0] || null;
}
/**
 * Putusan satu harga nego untuk baris t oleh akun. opsi = { alasan, hakNego ('sendiri'|'owner'|'tidak' — kisi SS2 bukan-owner), setuju (persetujuan cocok), atur,
 * bisaMinta (false = server belum membuka permintaan ke owner untuk akun ini: kalimat 'minta' menyebut jalan keluar yang SUNGGUH ada) }.
 * status: 'tolak' · 'katalog' (sama dengan katalog — nego dilepas) · 'naik' · 'jatah' · 'disetujui' · 'bawahModal' (owner + alasan) · 'perluAlasan' · 'minta'.
 */
export function ngPutus(t, hargaBaru, akun, opsi) {
  const o = opsi || {}; const A = o.atur || ngAtur(); const owner = ngOwner(akun); const nm = ngNama(akun);
  const harga = Math.round(Number(hargaBaru) || 0); const asli = Number(t && t.hargaAsli) || 0; const satuan = (t && t.satuan) || 'satuan';
  const jatah = ngJatah(akun, A); const modal = ngModalSatuan(t); const batas = ngBatas(asli, modal, jatah, A.langkah);
  const alasan = String(o.alasan || '').trim().slice(0, 80);
  const P = (status, teks, x) => Object.assign({ status, teks, harga, hargaAsli: asli, modal, batas, jatah, alasan: '', dibawahModal: modal !== null && harga < modal }, x || {});
  if (harga < NEGO_LANTAI) return P('tolak', 'Harga nego paling rendah ' + RP(NEGO_LANTAI));
  if (harga === asli) return P('katalog', 'kembali ke harga katalog ' + RP(asli));
  if (harga > asli) return P('naik', 'di atas harga katalog ' + RP(asli) + ' — bukan potongan');
  const setuju = !owner && o.setuju && Number(o.setuju.hargaMinta) <= harga ? o.setuju : null;
  const mintaAtauTolak = (teks, x) => {
    if (setuju) return P('disetujui', 'disetujui owner (' + RP(Number(setuju.hargaMinta)) + '/' + satuan + ')', Object.assign({ setujuId: String(setuju.id) }, x || {}));
    if ((o.hakNego || 'owner') === 'tidak') return P('tolak', 'Peran ' + nm + ' tidak boleh nego di bawah jatah margin — ' + teks);
    if (o.bisaMinta === false) return P('minta', teks + ' — perlu persetujuan owner, tapi minta owner dari perangkat ini belum bisa: ' + (batas !== null && batas < asli ? 'pakai batas ' + RP(batas) + ', ' : '') + 'parkir struk ini sampai owner datang, atau owner yang mencatat nota ini', x);
    return P('minta', teks + ' — minta owner', x);
  };
  if (modal === null) {
    if (owner) return P('jatah', 'modal barang ini belum tercatat — batas nego tidak bisa dihitung');
    return mintaAtauTolak('modal barang ini belum tercatat, jatah ' + nm + ' tidak bisa dihitung');
  }
  if (jatah > 0 && harga >= batas) return P('jatah', jatah >= 100 ? 'sampai modal — jatah ' + nm + ' penuh' : 'dalam jatah ' + nm + ' (' + jatah + ' % margin · paling rendah ' + RP(batas) + ')');
  if (harga >= modal) return mintaAtauTolak('di bawah jatah ' + nm + ' (' + jatah + ' % margin · paling rendah ' + RP(batas) + ')');
  // di bawah modal: modal hanya disebut ke owner
  const rugi = owner ? 'di bawah modal ' + RP(modal) + ', rugi ' + RP(modal - harga) + '/' + satuan : 'di bawah modal';
  if (!ngBolehBawahModal(akun, A)) return P('tolak', rugi + ' — ' + nm + ' tidak diizinkan menjual di bawah modal');
  if (!alasan) return P('perluAlasan', rugi + ' — tulis alasannya dulu (mis. karung sobek)');
  if (owner) return P('bawahModal', rugi + ' · alasan: ' + alasan, { alasan });
  return mintaAtauTolak(rugi + ' · alasan: ' + alasan, { alasan });
}
/** Kolom baris keranjang sesudah putusan yang BOLEH dipakai (katalog · naik · jatah · disetujui · bawahModal). */
export function ngTandai(t, p) {
  const x = Object.assign({}, t); NG_KOLOM.forEach((k) => { delete x[k]; });
  if (p.status === 'katalog') { x.hargaSatuan = p.hargaAsli; delete x.nego; return x; }
  x.hargaSatuan = p.harga; x.nego = true; x.negoStatus = p.status;
  if (p.batas !== null && p.batas !== undefined) x.negoBatas = p.batas;
  x.negoJatah = p.jatah;
  if (p.alasan) x.negoAlasan = p.alasan;
  if (p.setujuId) x.negoSetujuId = p.setujuId;
  return x;
}
export const ngBolehPakai = (p) => ['katalog', 'naik', 'jatah', 'disetujui', 'bawahModal'].indexOf(p && p.status) >= 0;
/** Baris nego yang dibangun ulang (jumlah / bonus berubah): putusannya dihitung ulang. '' = masih sah (kolom diperbarui lewat ngTandai), selain itu kalimat tolak. */
export function ngPutusUlang(t, akun, opsi) {
  if (!t || !t.nego) return { p: null, tolak: '' };
  const o = Object.assign({}, opsi || {}, { alasan: t.negoAlasan || '' });
  const st = t.negoSetujuId ? cacheMentah('persetujuan').find((m) => String(m.id) === String(t.negoSetujuId)) : null;
  if (st) o.setuju = st.status === 'disetujui' && Number(st.jumlah) >= Number(t.jumlah) ? st : null;
  const p = ngPutus(t, t.hargaSatuan, akun, o);
  if (ngBolehPakai(p)) return { p, tolak: '' };
  return { p, tolak: 'Harga nego ' + RP(t.hargaSatuan) + ' untuk ' + t.label + ' tidak berlaku lagi sesudah diubah: ' + p.teks + (st && Number(st.jumlah) < Number(t.jumlah) ? ' (persetujuan owner untuk ' + st.jumlah + ' ' + t.satuan + ')' : '') + ' — nego ulang dulu' };
}
/** Permintaan nego ke owner (koleksi persetujuan, tindakan 'nego'). Harga nota tidak berubah; yang meminta mengetik harga yang sama lagi sesudah disetujui. */
export function ngSusunMinta(t, p, akun, w) {
  if (!t || !p || p.status !== 'minta') return { tolak: 'Tidak ada yang perlu dimintakan ke owner' };
  if (ngOwner(akun)) return { tolak: 'Owner tidak perlu minta persetujuan' };
  const asli = p.hargaAsli; const jumlah = Number(t.jumlah) || 0;
  const data = { id: w.idUnik(), tindakan: 'nego', status: 'menunggu', tanggal: w.tanggal, jam: w.jam, pada: w.kini, dari: String(akun.nama || ''), peran: String(akun.peran || ''), negoUid: String(akun.uid || ''),
    teks: t.label + ': ' + RP(asli) + ' → ' + RP(p.harga) + '/' + t.satuan + ' × ' + String(jumlah).replace('.', ',') + (p.batas ? ' (batas jatah ' + RP(p.batas) + ')' : '') + (p.alasan ? ' · alasan: ' + p.alasan : ''),
    nominal: Math.round((asli - p.harga) * jumlah), barang: ngKunciBarang(t), label: t.label, satuan: t.satuan, jumlah, hargaAsli: asli, hargaMinta: p.harga, batas: p.batas, jatah: p.jatah, alasan: p.alasan || '' };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Permintaan nego ' + t.label + ' ' + RP(p.harga) + ' terkirim ke owner — harga nota tetap ' + RP(t.hargaSatuan) + ' sampai disetujui. Sesudah disetujui, ketik harga yang sama lagi.', kabarAwas: false } };
}
// ---- BONUS +1 KEMASAN (owner 23 Nov 2026: "masuk jatah nego", lewat batas → minta owner, tercatat di Buku Nego) ----
/** Angka bonus satu baris: harga katalog, harga bayar per unit, unit bayar, bonus, modal baris, yang diberikan & margin (rupiah). */
export function ngBonusAngka(t) {
  const asli = Number(t && t.hargaAsli) || 0; const harga = Number(t && t.hargaSatuan) || 0; const bayar = Number(t && t.jumlah) || 0; const bonus = Number(t && t.bonusUnit) || 0;
  const modal = Number(t && t.hppTotalSaatJual) || 0;
  return { asli, harga, bayar, bonus, modal: modal > 0 ? modal : null, diberi: Math.round(asli * (bayar + bonus) - harga * bayar), margin: modal > 0 ? Math.round(asli * (bayar + bonus) - modal) : null };
}
/** Persetujuan BONUS owner yang cocok untuk baris ini: milik akun ini, barang sama, jumlah bayar SAMA (bonus atas sedikit unit lebih berat), harga ≤ harga baris, belum dipakai. */
export function ngSetujuBonusUntuk(t, akun, opsi) {
  if (ngOwner(akun) || !t || !(Number(t.bonusUnit) > 0)) return null;
  const o = opsi || {}; const k = ngKunciBarang(t);
  const calon = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && m.bonus && m.status === 'disetujui' && String(m.negoUid || '') === String(akun.uid || '')
    && m.barang === k && Number(m.jumlah) === Number(t.jumlah) && Number(m.hargaMinta) <= Number(t.hargaSatuan) && (!o.tanggal || m.tanggal === o.tanggal));
  if (!calon.length) return null;
  const pakai = ngSetujuTerpakai(o.dipakai);
  return calon.filter((m) => !pakai[String(m.id)]).sort((a, b) => String(b.id).localeCompare(String(a.id)))[0] || null;
}
/**
 * Putusan bonus +1 untuk baris t oleh akun. opsi = { hakNego, bisaMinta, setuju (ngSetujuBonusUntuk), atur }.
 * status: 'tanpa' (baris tanpa bonus) · 'owner' · 'jatah' · 'disetujui' · 'minta' · 'tolak'. Bonus yang lewat jatah ATAU membuat baris rugi → minta owner.
 */
export function ngPutusBonus(t, akun, opsi) {
  const o = opsi || {}; const A = o.atur || ngAtur(); const nm = ngNama(akun); const N = ngBonusAngka(t);
  const P = (status, teks, x) => Object.assign({ status, teks, jatah: ngJatah(akun, A), nilai: Math.round(N.asli * N.bonus), diberi: N.diberi }, x || {});
  if (!(N.bonus > 0)) return P('tanpa', '');
  if (ngOwner(akun)) return P('owner', 'bonus dari owner');
  const jatah = ngJatah(akun, A);
  if (N.modal !== null && jatah > 0 && bonusDalamBatas(N.asli, N.harga, N.bayar, N.bonus, N.modal, jatah)) return P('jatah', 'bonus dalam jatah ' + nm + ' (' + jatah + ' % margin)');
  if (o.setuju) return P('disetujui', 'bonus disetujui owner', { setujuId: String(o.setuju.id) });
  const sebab = N.modal === null ? 'modal barang ini belum tercatat, jatah ' + nm + ' tidak bisa dihitung' : jatah > 0 ? 'bonus ini lewat jatah ' + nm + ' (' + jatah + ' % margin)' : nm + ' tidak punya jatah nego (0 % margin)';
  if (o.hakNego === 'tidak') return P('tolak', 'Peran ' + nm + ' tidak boleh memberi bonus di luar jatah — ' + sebab);
  if (o.bisaMinta === false) return P('minta', sebab + ' — perlu persetujuan owner, tapi minta owner dari perangkat ini belum bisa: parkir struk ini sampai owner datang, atau owner yang mencatat nota ini');
  return P('minta', sebab + ' — minta owner');
}
/** Kolom bonus baris keranjang sesudah putusan yang boleh dipakai ('tanpa' membersihkan). */
export function ngTandaiBonus(t, p) {
  const x = Object.assign({}, t); NG_KOLOM_BONUS.forEach((k) => { delete x[k]; });
  if (!p || p.status === 'tanpa' || !(Number(x.bonusUnit) > 0)) return x;
  x.bonusStatus = p.status; x.bonusNilai = p.nilai;
  if (p.status === 'jatah') x.bonusJatah = p.jatah;
  if (p.setujuId) x.bonusSetujuId = p.setujuId;
  return x;
}
export const ngBonusBolehPakai = (p) => ['tanpa', 'owner', 'jatah', 'disetujui'].indexOf(p && p.status) >= 0;
/** Permintaan bonus ke owner: dokumen persetujuan tindakan 'nego' + bonus 1 (bentuk rules v7 stafMintaNego — rules tidak berubah). Baris keranjang tidak berubah. */
export function ngSusunMintaBonus(t, p, akun, w) {
  if (!t || !p || p.status !== 'minta') return { tolak: 'Tidak ada bonus yang perlu dimintakan ke owner' };
  if (ngOwner(akun)) return { tolak: 'Owner tidak perlu minta persetujuan' };
  const N = ngBonusAngka(t);
  const data = { id: w.idUnik(), tindakan: 'nego', bonus: 1, status: 'menunggu', tanggal: w.tanggal, jam: w.jam, pada: w.kini, dari: String(akun.nama || ''), peran: String(akun.peran || ''), negoUid: String(akun.uid || ''),
    teks: t.label + ': bonus +1 untuk ' + String(N.bayar).replace('.', ',') + ' ' + t.satuan + ' @ ' + RP(N.harga), nominal: N.diberi, barang: ngKunciBarang(t), label: t.label, satuan: t.satuan,
    jumlah: N.bayar, hargaAsli: N.asli, hargaMinta: N.harga, jatah: p.jatah, alasan: '' };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Permintaan bonus ' + t.label + ' terkirim ke owner — bonusnya belum dipasang. Sesudah disetujui, ketuk bonus lagi.', kabarAwas: false } };
}
// ---- PERIKSA ULANG di perangkat OWNER (sanggahan rules 7 Okt): rules tidak mengikat nominal / teks / batas / label kiriman staf ke harga barang, jadi papan
// persetujuan & Buku Nego menghitung angkanya sendiri dari kolom yang benar-benar dipakai persetujuan (ngSetujuUntuk: barang, hargaMinta, jumlah) + harga
// katalog SEKARANG (rumus rak Jual: karung = hargaKarungUtuh buku induknya, kemasan, literan per wadah / merek, repack per kg).
/** Harga katalog SEKARANG untuk kunci barang ngKunciBarang — null bila tidak dikenali (wadah, katalog kosong). */
export function ngHargaKatalog(barang) {
  const k = String(barang || ''); const i = k.indexOf('|'); if (i < 0) return null;
  const jenis = k.slice(0, i); const sisa = k.slice(i + 1); const ada = (v) => (Number(v) > 0 ? Number(v) : null);
  if (jenis === 'karung') { const j = sisa.lastIndexOf('|'); const merk = sisa.slice(0, j); const uk = (petaUkuran() || {})[merk]; const hg = j > 0 ? hargaKarungUtuh(uk ? uk.induk : merk, Number(sisa.slice(j + 1)) || 50) : null; return hg ? ada(hg.perUnit) : null; }
  if (jenis === 'kemasan') { const h = (ambilHargaKemasan() || []).find((x) => kunciKemasan(x.merk, x.ukuran) === sisa); return h ? ada(h.hargaPerUnit) : null; }
  if (jenis === 'literan') { const h = (ambilHargaLiteran() || []).find((x) => x.merk === sisa); return h ? ada(h.hargaPerLiter) : null; }
  if (jenis === 'repack') return ada(cariHargaKarungPerKg(sisa));
  return null;
}
/** Nama barang dari kunci ngKunciBarang (bukan label kiriman peminta). */
export function ngNamaBarang(barang) {
  const b = String(barang || '').split('|'); const isi = b.slice(1);
  if (b[0] === 'karung' && isi.length >= 2) return isi.slice(0, -1).join('|') + ' ' + isi[isi.length - 1] + ' kg';
  if (b[0] === 'kemasan' && isi.length >= 2) return isi.slice(0, -1).join('|') + ' ' + String(isi[isi.length - 1]).replace('.', ',') + ' kg';
  return b[0] === 'literan' ? isi.join('|') + ' literan' : b[0] === 'repack' ? 'Repack ' + isi.join('|') : b[0] === 'wadah' ? 'Wadah ' + isi.join('|') : 'barang tidak dikenali';
}
/** Permintaan nego m menurut periksa ulang owner → { nama, katalog, hargaMinta, jumlah, nominal (null = katalog tidak ditemukan), teks }. */
export function ngPeriksaMinta(m) {
  // bentuk lama (sebelum JS2-C, tanpa barang / harga minta): tidak pernah dipakai nota mana pun (ngSetujuUntuk butuh barang, hargaMinta, jumlah) — tanpa angka
  if (!(m && m.barang && Number(m.hargaMinta) > 0)) return { nama: '', katalog: null, hargaMinta: 0, jumlah: 0, nominal: null, teks: String((m && m.teks) || 'permintaan nego') + ' — bentuk lama tanpa barang & harga: tidak dipakai di nota mana pun' };
  const hargaMinta = Math.round(Number(m && m.hargaMinta) || 0); const jumlah = Number(m && m.jumlah) || 0; const eceran = ngHargaKatalog(m && m.barang);
  // B1 (owner 16 Nov 2026): nego di atas harga pelanggan bertingkat — dasar hitungnya harga pelanggan itu SEKARANG (bukan eceran), supaya potongannya tidak membesar
  const H = m && m.pelanggan && eceran !== null ? htHarga({ orang: m.pelanggan, barang: m.barang, eceran, kg: htKgBarang(m.barang) }) : null; const katalog = H ? H.harga : eceran;
  // owner 23 Nov 2026: permintaan BONUS +1 — yang diberikan = katalog × (jumlah + 1) − harga × jumlah (unit gratis + tawar, bila ada)
  const bon = !!(m && m.bonus);
  const nominal = katalog !== null && hargaMinta > 0 && jumlah > 0 ? Math.max(0, Math.round(bon ? katalog * (jumlah + 1) - hargaMinta * jumlah : (katalog - hargaMinta) * jumlah)) : null; const nama = ngNamaBarang(m && m.barang);
  const teks = nama + ': ' + (bon ? 'BONUS +1 · ' : '') + (katalog !== null ? (H ? 'harga ' + H.nama + ' ' : 'katalog ') + RP(katalog) + ' → ' : '') + RP(hargaMinta) + ' × ' + String(jumlah).replace('.', ',')
    + (bon ? ' + 1 gratis' : '') + (nominal !== null ? (bon ? ' = diberikan ' : ' = potongan ') + RP(nominal) : ' — harga katalog barang ini tidak ditemukan, periksa di rak dulu') + (m && m.alasan ? ' · alasan: ' + String(m.alasan).slice(0, 80) : '');
  return { nama, katalog, hargaMinta, jumlah, nominal, teks, bonus: bon };
}
/** Permintaan nego yang masih menunggu owner (terbaru dulu). */
export function ngMenunggu() {
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && (m.status || 'menunggu') === 'menunggu').sort((a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || '')));
}
// jumlah yang DIBAYAR satu baris penjualan (kemasan: unit tanpa bonus) & nama barangnya
const ngJumlahBayar = (p) => (p.jenis === 'karung' ? Number(p.jumlahKarung) || 0 : p.jenis === 'kemasan' ? (Number(p.jumlahUnit) || 0) - (Number(p.bonusUnit) || 0) : p.jenis === 'literan' ? Number(p.jumlahLiter) || 0 : p.jenis === 'repacking' ? Number(p.totalKg) || 0 : Number(p.jumlahUnit) || 0);
const ngNamaBaris = (p) => (p.jenis === 'kemasan' ? String(p.namaProduk || '') + ' ' + String(p.ukuranKemasan || '').replace('.', ',') + ' kg' : p.jenis === 'karung' ? String(p.merkSumber || '') + ' ' + (p.beratKarungAcuan || 50) + ' kg'
  : p.jenis === 'literan' ? String(p.dariWadah || p.merkSumber || '') + ' literan' : p.jenis === 'repacking' ? 'Repack ' + String(p.namaProduk || '') : String(p.namaProduk || p.jenis || ''));
/**
 * BUKU NEGO satu hari (JS2-C): nego yang sudah jadi nota (baris penjualan berlaku dengan negoSelisih ≠ 0; satu takaran wadah = satu baris) + permintaan nego
 * hari itu dan yang masih menunggu. Tiap baris: jam · siapa · barang · harga katalog → harga nego · selisih per satuan & total · status · alasan.
 */
export function ngBuku(tanggal) {
  const grup = {};
  ambilPenjualan().forEach((p) => {
    if (p.tanggal !== tanggal || !(Number(p.negoSelisih) || 0)) return;
    const k = String(p.takaranId || p.id); const g = grup[k];
    if (g) { g.jumlah = Math.round((g.jumlah + ngJumlahBayar(p)) * 1000) / 1000; g.totalSelisih += (Number(p.negoSelisih) || 0) * ngJumlahBayar(p); return; }
    grup[k] = { jenis: 'nota', id: k, trxId: String(p.trxId || p.grupNota || p.id), jam: String(p.jam || ''), oleh: String(p.oleh || ''), barang: ngNamaBaris(p), pembeli: String(p.namaPelanggan || ''),
      hargaAsli: Number(p.hargaAsliSatuan) || 0, harga: (Number(p.hargaAsliSatuan) || 0) + (Number(p.negoSelisih) || 0), selisih: Number(p.negoSelisih) || 0, jumlah: ngJumlahBayar(p),
      totalSelisih: (Number(p.negoSelisih) || 0) * ngJumlahBayar(p), status: p.negoStatus || 'lama', alasan: String(p.negoAlasan || ''), batas: p.negoBatas, jatah: p.negoJatah };
  });
  const nota = Object.keys(grup).map((k) => Object.assign(grup[k], { totalSelisih: Math.round(grup[k].totalSelisih) }));
  // owner 23 Nov 2026: bonus +1 yang sudah jadi nota — siapa · barang · nilai bonus (harga katalog unit gratis) · status jatah / disetujui / owner / lama
  const bonus = ambilPenjualan().filter((p) => p.tanggal === tanggal && (Number(p.bonusUnit) || 0) > 0).map((p) => {
    const n = Number(p.bonusUnit) || 0; const nilai = Number(p.bonusNilai) > 0 ? Number(p.bonusNilai) : Math.round((Number(p.hargaAsliSatuan) || 0) * n);
    return { jenis: 'bonus', id: 'bonus-' + String(p.id), trxId: String(p.trxId || p.grupNota || p.id), jam: String(p.jam || ''), oleh: String(p.oleh || ''), barang: ngNamaBaris(p), pembeli: String(p.namaPelanggan || ''),
      hargaAsli: Number(p.hargaAsliSatuan) || 0, harga: 0, selisih: 0, jumlah: n, totalSelisih: -nilai, nilai, status: p.bonusStatus ? 'bonus' + p.bonusStatus[0].toUpperCase() + p.bonusStatus.slice(1) : 'bonusLama', alasan: '' };
  });
  const pakai = ngSetujuTerpakai();
  const minta = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && (m.tanggal === tanggal || (m.status || 'menunggu') === 'menunggu')).map((m) => {
    const st = m.status || 'menunggu'; const Q = ngPeriksaMinta(m);   // sanggahan rules 7 Okt: angka dihitung ulang dari barang / hargaMinta / jumlah + katalog sekarang
    return { jenis: 'minta', id: String(m.id), jam: String(m.jam || ''), tanggal: String(m.tanggal || ''), oleh: String(m.dari || ''), barang: Q.nama, hargaAsli: Q.katalog !== null ? Q.katalog : 0, harga: Q.hargaMinta,
      selisih: Q.katalog !== null ? Q.hargaMinta - Q.katalog : 0, jumlah: Q.jumlah, totalSelisih: Q.nominal !== null ? -Q.nominal : 0, alasan: String(m.alasan || ''), batas: m.batas, jatah: m.jatah,
      periksa: Q.katalog === null ? 'harga katalog barang ini tidak ditemukan — periksa di rak dulu' : '', bonus: Q.bonus, status: st === 'disetujui' && pakai[String(m.id)] ? 'dipakai' : st, alasanTolak: String(m.alasanTolak || '') };
  });
  const baris = nota.concat(bonus, minta).sort((a, b) => String(b.jam).localeCompare(String(a.jam)) || (a.jenis === 'minta' ? -1 : 1));
  const turun = nota.filter((x) => x.selisih < 0); const potongan = -turun.reduce((a, x) => a + x.totalSelisih, 0);
  const menunggu = minta.filter((x) => x.status === 'menunggu').length; const nilaiBonus = bonus.reduce((a, x) => a + x.nilai, 0);
  return { baris, nNota: nota.length, menunggu, potongan, nBonus: bonus.length, nilaiBonus,
    judul: nota.length + ' nego tercatat · ' + menunggu + ' menunggu owner · potongan ' + RP(potongan) + (bonus.length ? ' · ' + bonus.length + ' bonus ' + RP(nilaiBonus) : '') };
}
