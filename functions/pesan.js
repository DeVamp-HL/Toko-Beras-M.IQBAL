// Isi notifikasi HP owner dari satu dokumen persetujuan (permintaan dari tablet). Murni: tanpa Firebase, tanpa jaringan — diuji di jsc oleh
// alat-uji/uji_titipan.py (+ pesanPutus / kirimanTablet: alat-uji/uji_tablet_tampilan.py). Dipakai functions/index.js. Kalimatnya sengaja pendek: notifikasi tampil di layar kunci HP.
'use strict';

const JUDUL = { uangKeluar: 'Titipan uang keluar', pesan: 'Pesan dari tablet', barangMasuk: 'Barang masuk', hitungLaci: 'Hitungan laci', nego: 'Minta nego harga', hargaPelanggan: 'Usul harga pelanggan', kredit: 'Minta bon lewat batas kredit', hargaBanding: 'Usul harga tawaran / acuan',
  hargaJual: 'Usul harga jual', belanja: 'Daftar belanja dari tablet', kabarToko: 'Kabar toko', tugasSelesai: 'Tugas selesai' };   // + banding pemasok (owner 26 Nov 2026, rules v21) · + tablet saat owner pergi (owner 28 Nov 2026, rules v27)
const KABAR_TOKO = { habis: 'Barang habis', menipis: 'Perlu dipesan', bawahModal: 'Jual di bawah modal' };   // persetujuan kabarToko.jenis (tablet, rules v27)
const JENIS = { toko: 'Belanja toko', karyawan: 'Untuk karyawan', kasbon: 'Kasbon karyawan', bongkar: 'Upah bongkar', bayarBon: 'Bayar bon pemasok' };   // + barang masuk dari tablet (owner 22 Nov 2026, rules v15)
const BATAS_ISI = 160;

function rp(n) {
  const v = Math.round(Math.abs(Number(n) || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return (Number(n) < 0 ? '-' : '') + 'Rp' + v;
}
const teks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const pendek = (s) => (s.length > BATAS_ISI ? s.slice(0, BATAS_ISI - 1) + '…' : s);

/**
 * d = isi dokumen persetujuan, id = id dokumennya. Hasil { judul, isi, tag, layar } — semuanya teks (data pesan FCM wajib teks) — atau null bila tidak
 * perlu dikabarkan (bukan permintaan yang menunggu). tambah = { rp, nota } omzet hari itu (hanya untuk hitungan laci; null = tidak disebut).
 */
function pesanNotif(d, id, tambah) {
  if (!d || typeof d !== 'object') return null;
  if (d.tindakan === 'pesanOwner' || d.tindakan === 'tugasOwner') return null;   // pesan / tugas owner KE tablet — bukan kabar untuk HP owner (kabarDariOwner)   // owner 23 Nov 2026: pesan owner KE tablet — bukan kabar untuk HP owner (kabarDariOwner)
  if ((d.status || 'menunggu') !== 'menunggu') return null;
  const t = String(d.tindakan || '');
  const dari = teks(d.dari) || 'Tablet';
  let isi;
  if (t === 'uangKeluar') {
    const j = JENIS[d.jenis] || JENIS.toko;
    isi = [j, d.jenis === 'kasbon' ? teks(d.namaPegawai) : '', teks(d.teks), d.jenis === 'karyawan' && d.namaPegawai ? 'untuk ' + teks(d.namaPegawai) : '', rp(d.nominal)].filter(Boolean).join(' · ');
  } else if (t === 'pesan' || t === 'barangMasuk') {
    isi = teks(d.teks);
  } else if (t === 'hitungLaci') {   // owner 22 Nov 2026 (paket ④, rules v16): tutup hari dari tablet — owner menutup hari di Uang › Tutup hari
    isi = 'Laci ' + teks(d.tanggal) + ' dihitung ' + rp(d.hitung) + (Number(d.amankan) > 0 ? ' · ' + rp(d.amankan) + ' ke brankas' : '')
      + (tambah && Number(tambah.nota) > 0 ? ' · omzet ' + rp(tambah.rp) + ' dari ' + Math.round(Number(tambah.nota)) + ' nota' : '') + ' · tutup hari di HP';   // owner 28 Nov 2026: omzet kotor (retur belum dikurangi)
  } else if (t === 'kabarToko') {   // owner 28 Nov 2026 (rules v27): kabar otomatis tablet sesudah nota tersimpan
    return { judul: (KABAR_TOKO[d.jenis] || 'Kabar toko') + ' · ' + dari, isi: pendek(teks(d.teks)), tag: 'persetujuan-' + String(id || ''), layar: 'menu' };
  } else {
    const n = Math.round(Number(d.nominal) || 0); const k = teks(d.teks);
    isi = (k || JUDUL[t] || 'Permintaan') + (n > 0 && !/Rp/.test(k) ? ' · ' + rp(n) : '');
  }
  return { judul: (JUDUL[t] || 'Permintaan dari tablet') + ' · ' + dari, isi: pendek(isi), tag: 'persetujuan-' + String(id || ''), layar: t === 'uangKeluar' || t === 'pesan' || t === 'barangMasuk' || t === 'hitungLaci' ? 'uang' : 'menu' };
}

// ---- PUSH APLIKASI TABLET (owner 23 Nov 2026: "Push penuh lewat Google") — jawaban owner atas permintaan dari tablet, untuk akun yang memintanya ----
const JUDUL_TABLET = { uangKeluar: 'Titipan uang keluar', pesan: 'Pesan', barangMasuk: 'Kabar barang masuk', hitungLaci: 'Hitungan laci', nego: 'Minta nego harga', hargaPelanggan: 'Usul harga pelanggan', kredit: 'Minta bon', hargaBanding: 'Usul harga tawaran / acuan',
  hargaJual: 'Usul harga jual', belanja: 'Daftar belanja', kabarToko: 'Kabar toko', tugasSelesai: 'Jawaban tugas' };   // + owner 28 Nov 2026 (rules v27)
const PUTUS_TABLET = { disetujui: 'disetujui owner', ditolak: 'DITOLAK owner', dibaca: 'dibaca owner' };
const SALURAN_TABLET = 'kabar';   // saluran "Kabar toko" yang dibuat aplikasi tablet (MainActivity)

/**
 * Isi push untuk tablet dari satu PERUBAHAN dokumen persetujuan (sebelum → sesudah). Hanya saat permintaan yang tadinya menunggu diputus owner
 * (disetujui / ditolak / dibaca). Hasil { uid peminta, judul, isi, tag, layar } — semuanya teks — atau null (tidak perlu dikabarkan).
 */
function pesanPutus(sebelum, sesudah, id) {
  if (!sebelum || !sesudah || typeof sebelum !== 'object' || typeof sesudah !== 'object') return null;
  if ((sebelum.status || 'menunggu') !== 'menunggu') return null;
  const st = sesudah.status || 'menunggu'; if (st === 'menunggu' || !PUTUS_TABLET[st]) return null;
  const uid = teks(sesudah.mintaUid || sesudah.negoUid || sesudah.usulUid); if (!uid) return null;
  const t = String(sesudah.tindakan || '');
  // owner 23 Nov 2026 (obrolan di lonceng, "seperti WhatsApp"): owner MEMBUKA obrolan = pesan tablet ditandai dibaca tanpa balasan → cukup centang dua
  // di tablet, BUKAN notifikasi (balasan owner = pesan owner baru → kabarDariOwner). Dibaca DENGAN balasan (jalur lama Uang › titipan) tetap dikabarkan.
  if ((t === 'pesan' || t === 'kabarToko') && st === 'dibaca' && !teks(sesudah.balasan)) return null;   // + kabar toko (owner 28 Nov 2026): ditandai dibaca tanpa balasan = tanpa push
  let pokok;
  if (t === 'uangKeluar') pokok = [JENIS[sesudah.jenis] || JENIS.toko, teks(sesudah.teks), rp(sesudah.nominal)].filter(Boolean).join(' · ');
  else if (t === 'hitungLaci') pokok = 'Laci ' + teks(sesudah.tanggal) + ' ' + rp(sesudah.hitung);
  else { const n = Math.round(Number(sesudah.nominal) || 0); const k = teks(sesudah.teks); pokok = (k || JUDUL_TABLET[t] || 'Permintaan') + (n > 0 && !/Rp/.test(k) ? ' · ' + rp(n) : ''); }
  const tambah = st === 'ditolak' && teks(sesudah.alasanTolak) ? 'Alasan: ' + teks(sesudah.alasanTolak) + ' — ' : st === 'dibaca' && teks(sesudah.balasan) ? 'Balasan owner: ' + teks(sesudah.balasan) + ' — ' : '';
  return { uid, judul: (JUDUL_TABLET[t] || 'Permintaan') + ' ' + PUTUS_TABLET[st], isi: pendek(tambah + pokok), tag: 'putus-' + String(id || ''), layar: 'menu' };
}

/**
 * Owner 23 Nov 2026 ("gimana gua kirim pesan lewat mac/HP ke tablet?"): isi push untuk PESAN OWNER yang baru ditulis (persetujuan bertindakan
 * 'pesanOwner'). Hasil { judul, isi, tag, layar, untukUid } atau null (bukan pesan owner / kosong). untukUid kosong = semua tablet yang menyalakan notifikasi.
 */
function pesanDariOwner(d, id) {
  if (!d || typeof d !== 'object' || (d.tindakan !== 'pesanOwner' && d.tindakan !== 'tugasOwner')) return null;   // + tugas owner (owner 28 Nov 2026, rules v27)
  const isi = teks(d.teks); if (!isi) return null;
  const tugas = d.tindakan === 'tugasOwner';
  return { judul: tugas ? 'Tugas dari owner' + (d.wajibFoto ? ' · wajib foto' : '') : 'Pesan dari owner', isi: pendek(isi), tag: 'owner-' + String(id || ''), layar: 'menu', untukUid: teks(d.untukUid) };
}

/** Kiriman FCM untuk aplikasi tablet (Android): notifikasi sistem (tampil walau aplikasi ditutup) di saluran "Kabar toko", data layar tujuan. */
function kirimanTablet(p, tokens) {
  return { tokens: tokens.slice(), notification: { title: p.judul, body: p.isi },
    android: { priority: 'high', notification: { channelId: SALURAN_TABLET, tag: p.tag, sound: 'default', defaultVibrateTimings: true } },
    data: { layar: p.layar, tag: p.tag } };
}

/** Kode galat FCM yang berarti tokennya sudah mati (aplikasi dihapus, izin dicabut) — dokumennya dibuang supaya tidak dikirimi terus. */
const TOKEN_MATI = ['messaging/registration-token-not-registered', 'messaging/invalid-registration-token', 'messaging/invalid-argument'];
function tokenMati(kode) { return TOKEN_MATI.indexOf(String(kode || '')) >= 0; }

/** Lokasi fungsi dari lokasi database Firestore: multi-region nam5 → us-central1, eur3 → europe-west1, selebihnya sama persis. */
function lokasiFungsi(lokasiDb) {
  const l = String(lokasiDb || '').trim().toLowerCase();
  if (!l) return '';
  if (l === 'nam5' || l === 'us') return 'us-central1';
  if (l === 'eur3' || l === 'eu') return 'europe-west1';
  return l;
}

module.exports = { pesanNotif, pesanPutus, pesanDariOwner, kirimanTablet, tokenMati, lokasiFungsi, rp, JUDUL, JENIS, JUDUL_TABLET, SALURAN_TABLET, TOKEN_MATI, BATAS_ISI, KABAR_TOKO };
