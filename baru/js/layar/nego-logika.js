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
import { cacheMentah, ambilPenjualan } from '../data/toko.js';
import { NEGO_LANTAI, kunciKemasan } from '../mesin/pembantu.js';
import { RP } from '../inti/format.js';

// owner 7 Okt: bawaan = angka rancangan JS2 (owner 100 tetap, Ben 50, karyawan giliran 0, owner boleh di bawah modal dengan alasan, langkah Rp500)
export const NG_BAWAAN = { ben: 50, karyawan: 0, langkah: 500, bawahModal: ['owner'] };
export const NG_JATAH_OWNER = 100;
// kolom nego yang dibawa baris keranjang & ditulis ke dokumen penjualan (selain nego + negoSelisih yang sudah ada sejak putaran 2)
export const NG_KOLOM = ['negoStatus', 'negoBatas', 'negoJatah', 'negoAlasan', 'negoSetujuId'];
export const NG_LABEL = { jatah: 'dalam jatah', naik: 'di atas harga katalog', disetujui: 'disetujui owner', bawahModal: 'di bawah modal', lama: 'nego (sebelum ada batas nego)',
  menunggu: 'menunggu owner', ditolak: 'ditolak owner', dipakai: 'disetujui owner · sudah dipakai' };

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
/** Modal per satuan barang (modal baris ÷ satuan yang keluar dari stok — kemasan: unit bayar + bonus; rumus yang sama dengan kabar "DI BAWAH MODAL" sebelum
 *  owner 7 Okt); null = modal belum tercatat. */
export function ngModalSatuan(t) {
  const hpp = Number(t && t.hppTotalSaatJual); const j = (Number(t && t.jumlah) || 0) + (t && t.jenis === 'kemasan' ? Number(t.bonusUnit) || 0 : 0);
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
/** Tombol nego untuk akun ini: owner selalu; bukan-owner bila punya jatah ATAU kisi nego bukan "tidak boleh" (nego lebih dalam = minta owner). */
export function ngBolehNego(akun, hakNego, A) {
  if (ngOwner(akun)) return { boleh: true, kalimat: '' };
  if (ngJatah(akun, A) > 0 || (hakNego && hakNego !== 'tidak')) return { boleh: true, kalimat: '' };
  return { boleh: false, kalimat: ngNama(akun) + ' tidak punya jatah nego (0 % margin) — owner yang mengatur di Menu › Sistem › Peran › Atur' };
}
/** Persetujuan owner yang SUDAH dipakai nota yang berlaku (sekali pakai) + yang sedang dipegang keranjang / struk parkir perangkat ini. */
function ngSetujuTerpakai(dipakai) {
  const o = {}; ambilPenjualan().forEach((p) => { if (p.negoSetujuId) o[String(p.negoSetujuId)] = 1; });
  (dipakai || []).forEach((id) => { if (id) o[String(id)] = 1; });
  return o;
}
/** Persetujuan nego dari owner yang cocok untuk baris ini: milik akun ini, barang sama, harga disetujui ≤ harga yang diketik, jumlah ≤ yang diminta, belum dipakai. */
export function ngSetujuUntuk(t, harga, akun, opsi) {
  if (ngOwner(akun) || !t) return null;
  const o = opsi || {}; const k = ngKunciBarang(t);
  const calon = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && m.status === 'disetujui' && String(m.negoUid || m.olehUid || '') === String(akun.uid || '')
    && m.barang === k && Number(m.hargaMinta) <= Number(harga) && Number(m.jumlah) >= Number(t.jumlah) && (!o.tanggal || m.tanggal === o.tanggal));
  if (!calon.length) return null;   // layar menanyakannya tiap gambar — nota berlaku baru dibaca kalau memang ada persetujuan yang cocok
  const pakai = ngSetujuTerpakai(o.dipakai);
  return calon.filter((m) => !pakai[String(m.id)]).sort((a, b) => Number(b.hargaMinta) - Number(a.hargaMinta) || String(b.id).localeCompare(String(a.id)))[0] || null;
}
/**
 * Putusan satu harga nego untuk baris t oleh akun. opsi = { alasan, hakNego ('sendiri'|'owner'|'tidak' — kisi SS2 bukan-owner), setuju (persetujuan cocok), atur }.
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
  const pakai = ngSetujuTerpakai();
  const minta = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'nego' && (m.tanggal === tanggal || (m.status || 'menunggu') === 'menunggu')).map((m) => {
    const st = m.status || 'menunggu';
    return { jenis: 'minta', id: String(m.id), jam: String(m.jam || ''), tanggal: String(m.tanggal || ''), oleh: String(m.dari || ''), barang: String(m.label || ''), hargaAsli: Number(m.hargaAsli) || 0, harga: Number(m.hargaMinta) || 0,
      selisih: (Number(m.hargaMinta) || 0) - (Number(m.hargaAsli) || 0), jumlah: Number(m.jumlah) || 0, totalSelisih: -(Number(m.nominal) || 0), alasan: String(m.alasan || ''), batas: m.batas, jatah: m.jatah,
      status: st === 'disetujui' && pakai[String(m.id)] ? 'dipakai' : st, alasanTolak: String(m.alasanTolak || '') };
  });
  const baris = nota.concat(minta).sort((a, b) => String(b.jam).localeCompare(String(a.jam)) || (a.jenis === 'minta' ? -1 : 1));
  const turun = nota.filter((x) => x.selisih < 0); const potongan = -turun.reduce((a, x) => a + x.totalSelisih, 0);
  const menunggu = minta.filter((x) => x.status === 'menunggu').length;
  return { baris, nNota: nota.length, menunggu, potongan, judul: nota.length + ' nego tercatat · ' + menunggu + ' menunggu owner · potongan ' + RP(potongan) };
}
