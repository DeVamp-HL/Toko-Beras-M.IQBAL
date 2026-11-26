// LAYAR MENU — GAMBAR & KETUKAN. Rangka laci N1 (dikunci owner 16 Sep 2026: "pertahankan desain UI di layar N1") dipakai apa adanya:
// kepala kelompok yang bisa dibuka-tutup, tiap baris = ikon + judul + sub + angka + keterangan. Laci PALING ATAS = pita jam (N9),
// di bawahnya laci yang tidak pernah berpindah tempat. Dasar penyusunan lain (N2 Tanya · N5 Jam · N6 Orang · N8 Tertutup) = tab.
// Baris Sistem (Perangkat · Peran · Cadangan · Lokasi · Pengingat, desain SS1–SS5 dikunci 19 Sep) dibuka sebagai LEMBAR di dalam Menu.
// Layar dimorf (elemen hidup terus): laci membuka dengan transisi, angka bergulir, baris masuk bergiliran.
import { nanti, segera } from '../inti/jadwal.js';   // owner 29 Sep: bunyi data/status digabung sekali per bingkai (lag & freeze)
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { pasangIsian } from '../inti/isian.js';
import { RP, ANGKA, tanggalPendek, hariIniIso, jamKini, jamSetempat, waktuSetempat } from '../inti/format.js';
import * as M from './menu-logika.js';
import * as S from './sistem-logika.js';
import { kartuTitipan, aksiTitipan, TP_DRAF_KOSONG } from './titipan-panel.js';
import { kartuUsulBanding, aksiUsulBanding, UB_DRAF_KOSONG } from './banding-panel.js';   // paket Banding pemasok (owner 26 Nov 2026, rules v21): usul harga tawaran / acuan dari tablet
import { kartuTutupTablet, aksiTutupTablet, hlTampil, HL_DRAF_KOSONG } from './tutup-tablet-panel.js';   // owner 22 Nov 2026 (paket ④): tutup hari dari tablet   // owner 21 Nov 2026: uang keluar & pesan dari tablet
// owner 21 Nov 2026: Ringkas hari ini di tablet — kartu paling atas Menu akun tablet, hanya saat orang pilihan owner jaga (rules v14: data uang)
import { kartuRingkas, aksiRingkas } from './ringkas-tablet-panel.js';
import * as SJ from './sidik-logika.js';
// owner 26 Nov 2026: lokasi langit & cuaca gerbang (atur Perangkat) — cari tempat lewat Open-Meteo
import { lgUrlCari, lgBacaCari, lgLokasiSah } from '../inti/langit-logika.js';
import * as OW from './owner-tablet-logika.js';   // owner 22 Nov 2026: sidik jari owner di tablet (Tahap A)
import * as RU from './riwayat-uang-logika.js';   // owner 22 Nov 2026: riwayat & batal — tahap 1 uang
import * as RB from './riwayat-barang-logika.js';   // owner 22 Nov 2026: riwayat & batal — tahap 2 barang
import * as RS from './riwayat-setelan-logika.js';   // owner 22 Nov 2026: riwayat & batal — tahap 3 setelan & harga (lihat saja)
import * as RT from './ringkas-tablet-logika.js';
import * as TB from './tablet-logika.js';
import * as KL from './kpi-laba-logika.js';   // paket KPI laba (owner 24 Nov 2026): lembar Target & ambang
import { nhDukung, nhTersimpan, nhIzin, nhNyalakan, nhMatikan, nhVapidSah } from '../data/notif-hp.js';
import { ntAplikasi, ntDukung, ntTersimpan, ntNyalakan, ntMatikan } from '../data/notif-tablet.js';   // owner 23 Nov 2026: push aplikasi tablet (FCM Android)
import { infoPerangkat, layarPenuhAda, setelLayarPenuh } from '../inti/perangkat.js';   // owner 23 Nov 2026: layar penuh Android   // owner 21 Nov 2026: notifikasi HP saat aplikasi tertutup   // putaran T1 langkah 3 (owner 16 Nov 2026): orang di tablet + PIN
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, dokDiCache, bertahapTertunda, lanjutkanBertahap, buangBertahap, kabarKiriman, kunciLuarCache , ingatPerVersi, cacheMentah } from '../data/toko.js';
import { kpAlasanDitolak, kpKeHariIni } from './kunci-periode-logika.js';
// owner 26 Nov 2026 (kalender kepatuhan, rules v22): butir kalender di Pengingat → kartu "sudah dikerjakan" (owner & Penjaga laci)
import * as PT from './patuh-logika.js';
import { kartuCentang, aksiPanelPatuh } from './patuh-panel.js';
// owner 19 Nov 2026 (lag di Android): kelancaran PERANGKAT INI — dicatat perangkat sendiri, dibaca di Sistem › Perangkat
import { ukurMulusRingkas, ukurMulusSalin, ukurMulusKosongkan } from '../inti/ukur-mulus.js';
// owner 7 Okt (sisa pensiun #103): tab "Kasir & PIN" (25c) DICABUT dari layar — setelan operator kasir (pengaturan/aksesKasir) tidak dibaca aplikasi
// yang tayang sejak kasir.html & sistem lama pensiun 3 Okt (kasir darurat tidak pernah membacanya). PIN owner (pengaturan/keamanan) juga tidak dibaca
// aplikasi yang tayang; satu-satunya pembacanya = gerbang sistem lama kalau prosedur pulih darurat menjalankannya dari tag di komputer
// (docs/prosedur-pulih-darurat.md, langkah 0 & 2). Datanya TIDAK dihapus; logikanya tetap di akses-kasir-logika.js (dijaga uji_operator_pin.py).

const IKON_MODE = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
// Ikon per baris — tiap pintu memakai ikon BENDANYA (perintah owner 17 Sep: gambar sesuai namanya), kosakata ikon_menu.mjs kanvas Menu
const IK = {
  truk: '<path d="M3 7h11v9H3z"/><path d="M14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/>', orang: '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19c1.3-3 3.7-4.5 6.5-4.5s5.2 1.5 6.5 4.5"/>',
  dokumen: '<path d="M6 3h7l5 5v13H6z"/><path d="M13 3v5h5"/><path d="M9 13h6M9 17h4"/>', label: '<path d="M3 12V5.5A1.5 1.5 0 0 1 4.5 4H11l9 9-7 7z"/><circle cx="7.5" cy="7.5" r="1.2"/>',
  papan: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2.6h6V4"/><path d="M9 11h6M9 15h4"/>', kotak: '<path d="M4 8.5 12 4l8 4.5v8L12 21l-8-4.5z"/><path d="M4 8.5 12 13l8-4.5M12 13v8"/>',
  buku: '<path d="M5 5a2 2 0 0 1 2-2h11v16H7a2 2 0 0 0-2 2z"/><path d="M5 19a2 2 0 0 1 2-2h11"/>', perangkat: '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
  kunci: '<circle cx="9" cy="12" r="3.5"/><path d="M12.5 12H21l-1.8 2.2M17 12v3"/>', arsip: '<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
  peta: '<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/>', lonceng: '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
  keranjang: '<path d="M3 5h2l2.2 10h10.6L20 8H6.4"/><circle cx="9" cy="19" r="1.5"/><circle cx="16" cy="19" r="1.5"/>', karcis: '<path d="M4 7h16v3a2 2 0 0 0 0 4v3H4v-3a2 2 0 0 0 0-4z"/><path d="M12 7v10" stroke-dasharray="2 2"/>',
  bulan: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>', dompet: '<rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 10h18"/><circle cx="16.5" cy="14.5" r="1.2"/>',
  kalender: '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M8 3v4M16 3v4"/>', naik: '<path d="M4 17l5-5 4 4 7-8"/><path d="M14 8h6v6"/>', timbangan: '<path d="M12 4v16M5 20h14M6 7h12"/><path d="M3 13l3-6 3 6a3 3 0 0 1-6 0zM15 13l3-6 3 6a3 3 0 0 1-6 0z"/>',
  jam: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3.2 2"/>', pena: '<path d="M4 20l4-1L19 8l-3-3L5 16z"/><path d="M13.5 7.5l3 3"/>', tanya: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7"/><circle cx="12" cy="17" r=".6"/>',
  kartu: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="11" r="2"/><path d="M13 10h5M13 13h4M5.5 16c.6-1.5 1.7-2.2 3-2.2s2.4.7 3 2.2"/>', hapus: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>', rantai: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  cari: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
};
const ik = (n, w) => mentah('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="width:' + (w || 17) + 'px;height:' + (w || 17) + 'px;">' + (IK[n] || IK.tanya) + '</svg>');
const KUNCI_TAB = 'miqbal_baru_menu_tab', KUNCI_LACI = 'miqbal_baru_menu_laci';
const bacaLokal = (k) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } }; const simpanLokal = (k, v) => { try { if (v) localStorage.setItem(k, JSON.stringify(v)); else localStorage.removeItem(k); } catch (e) { /* abaikan */ } };
// owner 7 Okt 2026: tab Hemat baca di Sistem › Perangkat (tab Kasir & PIN dicabut paket dokumen & sisa, #108)
const TAB_SISTEM = { perangkat: [['perangkat', 'Perangkat'], ['antrean', 'Antrean kirim'], ['jejak', 'Jejak pencatat'], ['hemat', 'Hemat baca']], peran: [['peran', 'Peran & hak'], ['minta', 'Persetujuan'], ['tablet', 'Orang di tablet']], cadangan: [], lokasi: [['lokasi', 'Lokasi'], ['pindah', 'Pindah stok'], ['lapor', 'Laporan']], pengingat: [['kal', 'Kalender'], ['aturan', 'Aturan']], riwayat: [['uang', 'Uang'], ['barang', 'Barang'], ['setelan', 'Setelan & harga'], ['batal', 'Dibatalkan']], target: [], pegangan: [] };   // owner 22 Nov 2026: riwayat & batal (tahap 1 uang)
const JUDUL_SISTEM = { perangkat: 'Perangkat & antrean', peran: 'Peran & persetujuan', cadangan: 'Cadangan & simpanan', lokasi: 'Lokasi', pengingat: 'Pengingat', riwayat: 'Riwayat & batal', target: 'Target & ambang', pegangan: 'Buku pegangan' };   // paket KPI laba (owner 24 Nov 2026): target omzet harian & ambang kas minimum

/** opsi: gantiMode, mode, sekarang, statusRingkas, pindah(tujuan), bukaStok(lembar|tab), bukaPelanggan(keluarga, orang), lokal() → { antre, idPerangkat, pemegang, lokasi, namaPerangkat, koleksiSiap, koleksiTotal, offline }, periksaSambungan(), setelLokasi, namaiPerangkat, akun(), antreLokal(), buangDitolak(id), tulisUlangDitolak(id) */
export function pasangLayarMenu(akar, opsi) {
  const tabAwal = bacaLokal(KUNCI_TAB) || {}; const laciAwal = bacaLokal(KUNCI_LACI) || {};
  // putaran 23d: keadaan awal sebagai FUNGSI — dipanggil ulang saat ganti orang (inti/isian.js)
  const awal = () => ({ susunan: M.MN_SUSUNAN.some((t) => t[0] === tabAwal.susunan) ? tabAwal.susunan : 'laci', tutup: laciAwal.tutup || {}, bagian: null, cari: '', buka: null, kabar: '', kabarAwas: false,
    sistem: null, tabS: {}, pilihP: null, saring: '', peran: 'ben', akunPilih: {}, yakinAkun: null, alasanAkses: '', yakinBuang: null, mintaKe: null, alasan: '', hariC: null, hariP: 0, pilihG: null, catatanG: '', yakinWa: false, atur: null, aturKpi: null, bpgDraf: null, yakinBpg: null, bpgBuka: {}, cekG: null, pindah: { merk: '', dari: '', ke: '', kg: '', pengantar: '' }, lokasiPilih: null, sambungTeks: '', lsKb: null, usageKb: null, quotaKb: null, autoTanggal: null, lamaInfo: null, lamaBerkas: '', lamaDiunduh: false, yakinHemat: null,
    tb: { nama: '', peran: 'karyawan', pin: '', pin2: '' }, tbGanti: null, tbPinBaru: { pin: '', pin2: '' }, yakinTb: null, tbSibuk: false, tp: TP_DRAF_KOSONG(), ub: UB_DRAF_KOSONG(), hl: HL_DRAF_KOSONG(), hlCekYakin: null, sjSibuk: false, owBukaNyala: false, owSandi: '', owSibuk: false, owTolak: null, owAlasan: '', yakinOw: false, ruHari: '', ruSaring: '', ruBuka: null, ruAlasan: '', yakinRu: null, rsSaring: '', rsN: 40, nhVapid: '', nhSibuk: false, ntSibuk: false, ntInfo: null, lpSibuk: false, rtRinci: false, yakinRt: null, cuacaCari: '', cuacaHasil: [], cuacaSibuk: false, cuacaKabar: '' });   // T1-3: orang di tablet
  const K = buatKeadaan(awal());
  const ISIAN = pasangIsian(K, awal, ['pindah', 'alasan', 'alasanAkses', 'atur', 'aturKpi', 'bpgDraf', 'tgsDraf', ['ptCatatan', (v) => !!String(v || '').trim()], ['cekG', (v) => !!(v && (Object.keys(v.cek || {}).length || String(v.catatan || '').trim()))], 'catatanG', 'akunPilih', ['namaBaru', (v) => !!String(v || '').trim()], 'tb', 'tbPinBaru', 'nhVapid', ['tp', (v) => !!(v && (String(v.nominal || '').trim() || String(v.teks || '').trim() || String(v.pesan || '').trim()))], ['ub', (v) => !!(v && (String(v.hargaPerKg || '').trim() || String(v.pemasok || '').trim()))], ['ruAlasan', (v) => !!String(v || '').trim() && !RU.RU_ALASAN.some((x) => x[1] === v)]], []);   // ruAlasan: hanya alasan yang DIKETIK (pil bawaan bukan isian)
  const set = (p) => K.setel(p); const st = () => K.baca(); let tampil = false; let _kotor = true;   /* owner 29 Sep (lag): permintaan gambar saat tersembunyi cukup MENANDAI; saat dibuka digambar hanya kalau kotor */
  const kini = () => opsi.sekarang() || new Date();
  const waktu = () => { const d = kini(); return { tanggal: hariIniIso(d), jam: jamKini(d), kini: new Date().toISOString(), idUnik: () => Date.now() + Math.random() }; };
  // owner 3 Okt (patah-patah): Menu yang dibuka lagi TANPA data baru tidak digambar ulang. Sanggahan 7 Okt: isinya juga membaca tanggal (kepala, jatuh tempo
  // bon, pengingat pajak), pita jam (Pagi / Malam …) dan titik kas perangkat — semuanya tidak menaikkan versi data. Kunci gambar terakhir = kunciLuarCache
  // + pita jam (+ menit selagi Sistem › Perangkat terbuka: "denyut N menit lalu", antrean lama); dibuka lagi dengan kunci lain = digambar ulang.
  let _kunciGambar = '';
  const kunciGambar = () => { const d = kini(); return kunciLuarCache(d) + '|' + M.mnBagianDari(d.getHours()) + (st().sistem === 'perangkat' ? '|' + Math.floor(d.getTime() / 60000) : ''); };
  // owner 19 Nov 2026 (kartu Kelancaran tablet: Menu › Laci tersendat tiap huruf cari, tiap ketuk baris): susunan Menu (laci, pita jam, tanya, daftar orang
  // untuk cari) dulu dihitung ulang TIAP gambar — laba bulan ini, buku stok, utang, bon, pengingat. Kini diingat per versi data + KUNCI GAMBAR yang sama
  // dengan aturan "dibuka lagi tanpa data baru tidak digambar" (hari, hari tutup, titik kas, pita jam, menit selagi Perangkat terbuka) + masukan luarnya
  // (isi perangkat: antrean, simpanan). Hasil DIPAKAI BERSAMA: penggambar hanya membaca / memetakan salinan.
  const ingatMenu = (nama, luar, f) => ingatPerVersi('mn|' + nama + '|' + _kunciGambar + '|' + luar, f);
  const lamaAda = () => { const I = st().lamaInfo; return I && I.ada ? I : null; };   // null = belum dihitung / tidak terbaca
  const lokal = () => Object.assign({}, opsi.lokal ? opsi.lokal() : {}, { lsKb: st().lsKb, usageKb: st().usageKb, quotaKb: st().quotaKb, autoTanggal: st().autoTanggal,
    lamaKb: lamaAda() ? lamaAda().kb : null, lamaN: lamaAda() ? lamaAda().ada.length : null });
  // owner 7 Okt (sisa pensiun #103): baca HANYA kunci sistem lama yang dibekukan di S.SS_KUNCI_LAMA — kunci /baru/ & kasir darurat tidak pernah dibaca/dihapus
  const bacaLama = () => { const o = {}; S.SS_KUNCI_LAMA.forEach((k) => { try { o[k] = localStorage.getItem(k); } catch (e) { o[k] = null; } }); return o; };
  // owner 7 Okt (tinjauan, lag iPhone/iPad): sisa sistem lama DIHITUNG di sini saja — saat lembar Sistem dibuka/Menu tampil (ukurSimpanan) dan sesudah
  // unduh/nyatakan tersimpan/bersihkan — lalu disimpan di keadaan (lamaInfo). Gambar hanya membaca keadaan: tidak ada 50× getItem (cache lama bisa
  // ber-MB) tiap Menu digambar ulang. localStorage tak terbaca → { takTerbaca } (beda dari "tidak ada sisa").
  const hitungLama = () => { try { void localStorage.length; return S.ssSimpananLama(bacaLama(), st().lamaDiunduh); } catch (e) { return { takTerbaca: true }; } };
  const ingat = () => { simpanLokal(KUNCI_TAB, { susunan: st().susunan }); simpanLokal(KUNCI_LACI, { tutup: st().tutup }); };
  async function tulis(r) {
    if (!r || r.tolak) { set({ kabar: (r && r.tolak) || 'Tidak ada yang ditulis', kabarAwas: true }); return false; }
    try { const x = await tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus }); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch || {}, { kabar: kabarKiriman(x, (r.patch && r.patch.kabar) || 'Tersimpan') })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  // ukuran simpanan lokal dibaca dari peramban (bukan ditebak); tidak terbaca → null → layar bilang tidak bisa dibaca
  function ukurSimpanan() {
    let ls = null; try { let b = 0; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); b += (k.length + String(localStorage.getItem(k) || '').length) * 2; } ls = Math.round(b / 1024); } catch (e) { ls = null; }
    let auto = null; try { auto = localStorage.getItem('miqbal_backup_auto_tanggal') || null; } catch (e) { auto = null; }
    // owner 3 Okt (Menu patah-patah): keadaan hanya disetel bila angkanya BERUBAH — tiap setel menggambar ulang Menu, dan buka Menu dulu menggambar 2–3 kali
    const beda = (p) => { const s = st(); const u = {}; Object.keys(p).forEach((k) => { if (JSON.stringify(s[k]) !== JSON.stringify(p[k])) u[k] = p[k]; }); if (Object.keys(u).length) set(u); };
    beda({ lsKb: ls, autoTanggal: auto, lamaInfo: hitungLama() });
    try { if (navigator.storage && navigator.storage.estimate) navigator.storage.estimate().then((e) => beda({ usageKb: Math.round((e.usage || 0) / 1024), quotaKb: Math.round((e.quota || 0) / 1024) })).catch(() => {}); } catch (e) { /* abaikan */ }
  }
  // ---- tujuan tiap baris: layar sistem baru atau lembar Sistem di dalam Menu. Tujuan 'lama' (tautan ke sistem lama) dibuang 3 Okt 2026: sistem
  // lama pensiun (owner) dan menu-logika.js sudah tidak punya baris yang menunjuknya ----
  function pergi(t) {
    if (!t) return;
    if (t.ke === 'sistem') { set({ sistem: t.sistem, kabar: '', buka: null, tabS: Object.assign({}, st().tabS, t.tab ? { [t.sistem]: t.tab } : {}) }); ukurSimpanan(); return; }
    if (t.ke === 'stok') { opsi.bukaStok && opsi.bukaStok(t.lembar || null, t.tab || null); return; }
    if (t.ke === 'pelanggan') { opsi.bukaPelanggan && opsi.bukaPelanggan(t.keluarga || 'kenali', t.orang || null); return; }
    if (t.ke === 'harga') { opsi.bukaHarga && opsi.bukaHarga(t.keluarga || 'katalog', t); return; }   // putaran 17: Harga & Pemasok
    if (t.ke === 'uang') { opsi.bukaUang && opsi.bukaUang(t.keluarga || 'keluar', t); return; }   // putaran 18: Uang (K1–K6)
    if (t.ke === 'laporan') { opsi.bukaLaporan && opsi.bukaLaporan(t.keluarga || 'laba', t); return; }   // putaran 19: Laporan & Dokumen
    if (t.ke === 'jual' && t.lembar) { opsi.bukaJual ? opsi.bukaJual(t.lembar) : opsi.pindah('jual'); return; }   // putaran 20: Jual → Karcis
    if (t.ke === 'jual' || t.ke === 'ringkasan') { opsi.pindah(t.ke); return; }
    set({ kabar: 'Belum ada layarnya di sistem baru.', kabarAwas: true });
  }
  const AKSI = Object.assign({
    susunan: ({ s }) => { set({ susunan: s, buka: null, kabar: '' }); ingat(); }, mode: () => opsi.gantiMode(), tutupKabar: () => set({ kabar: '' }),
    // laci N1 terbuka sejak lahir; laci "Ganti bagian hari" TERTUTUP sejak lahir (tidak makan tempat) — keduanya diingat per perangkat
    laci: ({ id }) => { const t = Object.assign({}, st().tutup); t[id] = id === 'ganti' ? !(t.ganti === true) : !t[id]; set({ tutup: t }); ingat(); },
    cari: (v) => set({ cari: String(v).slice(0, 40) }), cariHapus: () => set({ cari: '' }),
    baris: ({ id }) => set({ buka: st().buka === id ? null : id }),
    pergi: ({ tujuan }) => { try { pergi(JSON.parse(tujuan)); } catch (e) { /* abaikan */ } },
    bagian: ({ b }) => set({ bagian: Number(b) }),
    // ---- SISTEM
    sistem: ({ s }) => { set({ sistem: s || null, kabar: '', atur: null, pilihP: null, mintaKe: null, pilihG: null }); if (s) ukurSimpanan(); }, tabS: ({ t }) => set({ tabS: Object.assign({}, st().tabS, { [st().sistem]: t }), kabar: '', atur: null }),
    pilihP: ({ id }) => set({ pilihP: st().pilihP === id ? null : id }), saring: ({ nama }) => set({ saring: st().saring === nama ? '' : nama }),
    stafKe: ({ t }) => opsi.pindah(t),
    periksaSambung: async () => { set({ sambungTeks: 'memeriksa…' }); const r = opsi.periksaSambungan ? await opsi.periksaSambungan() : { teks: 'tidak tersedia di mode ini' }; set({ sambungTeks: r.teks, kabar: r.teks, kabarAwas: r.hasil === 'gagal' }); },
    // putaran 23: akun per orang — owner mendaftarkan / menolak permintaan, mengubah peran, menonaktifkan (dua ketukan)
    akunPilihPeran: ({ uid, peran }) => { const a = Object.assign({}, st().akunPilih); a[uid] = peran; set({ akunPilih: a }); },
    daftarkan: ({ uid }) => tulis(S.susunDaftarkan(uid, st().akunPilih[uid], waktu())),
    alasanAkses: (v) => set({ alasanAkses: String(v).slice(0, 120) }),
    tolakAkses: ({ uid }) => tulis(S.susunTolakAkses(uid, st().alasanAkses, waktu())),
    ubahPeranAkun: ({ uid, peran }) => tulis(S.susunUbahAkun(uid, { peran }, waktu(), false)),
    saklarAkun: async ({ uid, aktif }) => { const kunci = uid + ':' + aktif; const r = S.susunUbahAkun(uid, { aktif: aktif === '1' }, waktu(), st().yakinAkun === kunci); if (r.perluYakin) return set({ yakinAkun: kunci, kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    // putaran 23 (7b): kiriman yang ditolak server — owner memutuskan: tulis ulang atas namanya, atau buang (dua ketukan)
    tulisUlangDitolak: async ({ id }) => { if (!opsi.tulisUlangDitolak) return; const r = await opsi.tulisUlangDitolak(id); set({ kabar: r && r.gagal ? 'DITOLAK: ' + r.pesan : 'Ditulis ulang atas nama owner' + (r && r.antre ? ' (masuk antrean)' : ''), kabarAwas: !!(r && r.gagal) }); },
    // putaran 25: kiriman yang ditolak karena BULAN TERKUNCI → dicatat ulang bertanggal HARI INI (tanggal aslinya ditulis di catatannya)
    tulisUlangHariIni: async ({ id }) => { if (!opsi.tulisUlangDitolak) return; const r = await opsi.tulisUlangDitolak(id, (dok) => kpKeHariIni(dok, waktu())); set({ kabar: r && r.gagal ? 'DITOLAK: ' + r.pesan : 'Dicatat ulang bertanggal hari ini atas nama owner' + (r && r.antre ? ' (masuk antrean)' : ''), kabarAwas: !!(r && r.gagal) }); },
    // putaran 25: kiriman BERTAHAP yang terputus (SATUKAN, hapus nama, tarik balik rincian, adukan) — lanjutkan dari potongan yang belum, atau buang sisanya
    lanjutBertahap: async () => { const r = await lanjutkanBertahap(); set({ kabar: r && r.gagal ? 'BERHENTI: ' + r.pesan : kabarKiriman(r, 'Kiriman bertahap selesai (' + (r.total || 0) + ' tahap)'), kabarAwas: !!(r && r.gagal) }); },
    buangBertahap: () => { if (st().yakinBuang !== 'bertahap') return set({ yakinBuang: 'bertahap', kabar: 'Ketuk sekali lagi: sisa kiriman bertahap TIDAK dikirim (yang sudah masuk tetap masuk)', kabarAwas: true }); buangBertahap(); set({ yakinBuang: null, kabar: 'Sisa kiriman bertahap dibuang', kabarAwas: false }); },
    // owner 3 Okt: salinan kiriman ditolak/menunggu di perangkat ini bisa diunduh — bahan memeriksa tanpa Web Inspector (web app Safari tidak punya menu Develop)
    unduhDitolak: () => { const AL = opsi.antreLokal ? opsi.antreLokal() : { belum: [], ditolak: [] }; const L = opsi.lokal ? opsi.lokal() : {};
      const teks = JSON.stringify({ diunduhPada: new Date().toISOString(), perangkat: L.namaPerangkat || '', idPerangkat: L.idPerangkat || '', ditolak: AL.ditolak, belum: AL.belum }, null, 2);
      try { const blob = new Blob([teks], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'kiriman-ditolak-' + hariIniIso(kini()) + '.json'; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(url), 2000); }
      catch (e) { set({ kabar: 'Peramban ini tidak bisa mengunduh berkas: ' + (e && e.message ? e.message : e), kabarAwas: true }); } },
    buangDitolak: ({ id }) => { if (!opsi.buangDitolak) return; if (st().yakinBuang !== id) return set({ yakinBuang: id, kabar: 'Ketuk sekali lagi untuk membuang kiriman itu — isinya tidak akan pernah masuk data toko', kabarAwas: true }); opsi.buangDitolak(id); set({ yakinBuang: null, kabar: 'Kiriman yang ditolak dibuang', kabarAwas: false }); },
    // owner 19 Nov 2026: kelancaran perangkat ini (inti/ukur-mulus.js) — lihat / salin rincian, mulai dari nol
    lcBuka: () => set({ lcBuka: !st().lcBuka }),
    lcSalin: async () => { const teks = ukurMulusSalin(infoLancar());
      try { await navigator.clipboard.writeText(teks); set({ kabar: 'Rincian kelancaran disalin — tinggal ditempel', kabarAwas: false }); }
      catch (e) { set({ lcBuka: true, kabar: 'Perangkat ini tidak mengizinkan menyalin otomatis — rinciannya ditampilkan di bawah; tekan lama untuk menyalin, atau potret layarnya', kabarAwas: true }); } },
    lcNol: () => { ukurMulusKosongkan(); set({ lcBuka: false, kabar: 'Catatan kelancaran dimulai dari nol', kabarAwas: false }); },
    namaiPerangkat: (v) => set({ namaBaru: String(v).slice(0, 30) }), namaiSimpan: () => { if (!opsi.namaiPerangkat) return; opsi.namaiPerangkat(st().namaBaru || ''); set({ kabar: 'Perangkat ini kini bernama ' + (st().namaBaru || '(tanpa nama)') + ' — jejak & denyut memakai nama itu', kabarAwas: false, namaBaru: '' }); },
    peran: ({ id }) => set({ peran: id, kabar: '' }), putarHak: async ({ peran, t }) => { await tulis(S.susunPutarHak(peran, t, waktu())); },
    mintaKe: ({ id }) => set({ mintaKe: st().mintaKe === id ? null : id, alasan: '' }), alasan: (v) => set({ alasan: String(v).slice(0, 80) }),
    setujui: async () => { if (await tulis(S.susunPutusPersetujuan(st().mintaKe, true, '', waktu()))) set({ mintaKe: null }); }, tolak: async () => { if (await tulis(S.susunPutusPersetujuan(st().mintaKe, false, st().alasan, waktu()))) set({ mintaKe: null, alasan: '' }); },
    setujuiKecil: async () => { await tulis(S.susunSetujuiKecil(waktu())); },
    hariC: ({ iso }) => set({ hariC: iso }),
    // ---- hemat baca (owner 7 Okt 2026, siap 2027): saklar PER PERANGKAT dua ketukan (lalu aplikasi dimuat ulang), baca penuh, Console, semua perangkat
    hematSaklar: ({ ke }) => {
      if (st().yakinHemat !== ke) return set({ yakinHemat: ke, kabar: ke === 'nyala' ? 'Ketuk sekali lagi: hemat baca menyala di perangkat ini, aplikasi dimuat ulang (perangkat ini membaca penuh sekali)' : 'Ketuk sekali lagi: hemat baca mati di perangkat ini, aplikasi dimuat ulang (kembali baca semua tiap buka)', kabarAwas: true });
      if (!opsi.setelSaklarHemat || !opsi.setelSaklarHemat(ke === 'nyala')) return set({ yakinHemat: null, kabar: 'Saklar tidak bisa disimpan di peramban ini (penyimpanan diblokir) — hemat baca tetap mati', kabarAwas: true });
      set({ yakinHemat: null, kabar: 'Memuat ulang…', kabarAwas: false }); if (opsi.muatUlang) opsi.muatUlang();
    },
    hematBaca: () => { const ok = !!(opsi.hematBacaPenuh && opsi.hematBacaPenuh('tombol "Baca penuh sekarang"', false)); set({ kabar: ok ? 'Perangkat ini membaca penuh semua catatan toko sekarang' : 'Hemat baca belum berjalan di perangkat ini', kabarAwas: !ok }); },
    hematConsole: () => { const ok = !!(opsi.hematBacaPenuh && opsi.hematBacaPenuh('owner mengubah data lewat Console', true)); set({ kabar: ok ? 'Perangkat ini membaca penuh dan menandai catatan yang berubah tanpa cap — perangkat lain menerimanya lewat ubahan' : 'Hemat baca belum berjalan di perangkat ini', kabarAwas: !ok }); },
    hematSemua: async () => { if (st().yakinHemat !== 'semua') return set({ yakinHemat: 'semua', kabar: 'Ketuk sekali lagi: SEMUA perangkat owner yang hemat baca membaca penuh sekali (±3 × 9 rb baca)', kabarAwas: true });
      const r = opsi.hematMintaSemua ? await opsi.hematMintaSemua() : { gagal: true, pesan: 'tidak tersedia' }; set({ yakinHemat: null, kabar: r && r.gagal ? 'Gagal: ' + r.pesan : 'Semua perangkat owner diminta membaca penuh', kabarAwas: !!(r && r.gagal) }); },
    unduhCadangan: async () => { const b = S.ssBerkasCadangan(kini(), opsi.hemat ? opsi.hemat() : null); const teks = JSON.stringify(b.isi, null, 2); let bytes = teks.length;
      try { const blob = new Blob([teks], { type: 'application/json' }); bytes = blob.size; const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = b.nama; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(url), 2000); }
      catch (e) { set({ kabar: 'Peramban ini tidak bisa mengunduh berkas: ' + (e && e.message ? e.message : e), kabarAwas: true }); return; }
      await tulis(S.susunCatatCadangan(b, bytes, waktu(), (opsi.lokal ? opsi.lokal() : {}).namaPerangkat || '')); ukurSimpanan(); },
    // owner 7 Okt (sisa pensiun #103): sisa simpanan sistem lama di perangkat ini — unduh salinannya (apa adanya, TANPA salinan PIN owner), lalu bersihkan
    // dengan DUA ketukan. Antrean lama yang masih berisi (catatan yang tidak pernah sampai server) ikut dibersihkan HANYA sesudah owner MENYATAKAN berkas
    // salinannya tersimpan (tinjauan: a.click() tidak memberi tahu apa pun — iOS bisa membatalkan lembar unduhan — jadi unduhan sendiri tidak memasang
    // penanda lamaDiunduh; tombol "berkasnya sudah tersimpan" yang memasangnya).
    lamaUnduh: () => { const o = bacaLama(); const B = S.ssSalinanLama(o); const Ld = S.ssSimpananLama(o, false); const L = opsi.lokal ? opsi.lokal() : {}; const nama = 'simpanan-sistem-lama-' + hariIniIso(kini()) + '.json';
      const teks = JSON.stringify({ diunduhPada: new Date().toISOString(), perangkat: L.namaPerangkat || '', idPerangkat: L.idPerangkat || '', simpananSistemLama: B.isi }, null, 2);
      try { const blob = new Blob([teks], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = nama; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(url), 2000); }
      catch (e) { set({ kabar: 'Peramban ini tidak bisa mengunduh berkas: ' + (e && e.message ? e.message : e), kabarAwas: true }); return; }
      set({ lamaBerkas: nama, yakinBuang: null, lamaInfo: hitungLama(), kabar: 'Berkas ' + nama + ' (' + B.n + ' simpanan' + (B.dibuang.length ? ', salinan PIN owner tidak ikut' : '') + ') dikirim ke Unduhan'
        + (Ld.dijaga.length && !st().lamaDiunduh ? ' — buka Unduhan/Files, pastikan berkasnya ada, lalu ketuk "berkasnya sudah tersimpan"; antrean lama ' + Ld.nCatatan + ' catatan baru ikut dibersihkan sesudah itu' : ' — periksa berkasnya di Unduhan/Files'), kabarAwas: false }); },
    lamaTersimpan: () => { if (!st().lamaBerkas) return set({ kabar: 'Unduh salinannya dulu', kabarAwas: true });
      set({ lamaDiunduh: true, yakinBuang: null, kabar: 'Dicatat: berkas ' + st().lamaBerkas + ' tersimpan — antrean lama yang berisi kini ikut BERSIHKAN (tetap dua ketukan)', kabarAwas: false }); set({ lamaInfo: hitungLama() }); },
    lamaBersih: () => { const L = S.ssSimpananLama(bacaLama(), st().lamaDiunduh); if (!L.dibersihkan.length) return set({ yakinBuang: null, kabar: L.dijaga.length ? 'Yang tersisa cuma antrean lama yang masih berisi ' + L.nCatatan + ' catatan — unduh salinannya dulu, lalu nyatakan berkasnya tersimpan' : 'Tidak ada sisa simpanan sistem lama di perangkat ini', kabarAwas: !!L.dijaga.length });
      const ikut = L.ada.filter((x) => x.antrean && x.n > 0 && L.dibersihkan.indexOf(x.kunci) >= 0).reduce((n, x) => n + x.n, 0);   // antrean berisi yang ikut (salinannya dinyatakan tersimpan)
      if (st().yakinBuang !== 'lama') return set({ yakinBuang: 'lama', kabar: 'Ketuk BERSIHKAN sekali lagi: ' + L.dibersihkan.length + ' simpanan sistem lama (±' + ANGKA(Math.round(L.kbBersih)) + ' KB) dihapus dari perangkat ini — data toko di server tidak tersentuh' + (L.dijaga.length ? '; antrean lama berisi ' + L.nCatatan + ' catatan TETAP disimpan sampai salinannya diunduh & dinyatakan tersimpan' : '') + (ikut ? '; termasuk antrean lama berisi ' + ikut + ' catatan — satu-satunya salinannya di berkas ' + (st().lamaBerkas || 'yang diunduh') : ''), kabarAwas: true });
      let n = 0; L.dibersihkan.forEach((k) => { try { localStorage.removeItem(k); n += 1; } catch (e) { /* terkunci */ } });
      set({ yakinBuang: null, kabar: n + ' simpanan sistem lama dibersihkan (±' + ANGKA(Math.round(L.kbBersih)) + ' KB)' + (n < L.dibersihkan.length ? ' — ' + (L.dibersihkan.length - n) + ' gagal dihapus peramban' : '') + (L.dijaga.length ? '; antrean lama berisi ' + L.nCatatan + ' catatan masih disimpan' : ''), kabarAwas: n < L.dibersihkan.length }); ukurSimpanan(); },
    lokasiPilih: ({ id }) => set({ lokasiPilih: id }), lokasiIni: ({ id }) => { if (!opsi.setelLokasi) return; opsi.setelLokasi(id); set({ kabar: 'Perangkat ini kini mencatat di ' + (S.ssLokasi().daftar.find((l) => l.id === id) || { nama: id }).nama + ' — catatan berikutnya membawa lokasi itu', kabarAwas: false }); },
    jadikanUtama: async ({ id }) => { await tulis(S.susunJadikanUtama(id, waktu())); },
    pindahIsi: (v, el) => { const p = Object.assign({}, st().pindah); p[el.dataset.kolom] = String(v).slice(0, 10); set({ pindah: p }); }, pindahPilih: ({ kolom, nilai }) => { const p = Object.assign({}, st().pindah); p[kolom] = p[kolom] === nilai ? '' : nilai; set({ pindah: p, kabar: '' }); },
    pindahSimpan: async () => { const p = st().pindah; if (await tulis(S.susunPindahStok(p.merk, p.dari, p.ke, p.kg, p.pengantar, waktu()))) set({ pindah: { merk: '', dari: '', ke: '', kg: '', pengantar: '' } }); },
    // paket KPI laba: Target & ambang (aturanToko/kpiLaba)
    kpiKetik: (v, el) => { const A = KL.klAtur(); const a = Object.assign({ targetHarian: A.targetHarian ? String(A.targetHarian) : '', kasMinimum: A.kasMinimum ? String(A.kasMinimum) : '', bungaModal: A.bungaDariOwner ? String(A.bungaModal).replace('.', ',') : '' }, st().aturKpi || {}); a[el.dataset.kolom] = String(v).slice(0, 16); set({ aturKpi: a }); },
    // paket KPI laba (butir 14): cek mingguan gudang — jawab hal, catatan, simpan (owner & Penjaga laci)
    cgHal: ({ hal, v }) => { const a = Object.assign({ cek: {}, catatan: '' }, st().cekG || {}); a.cek = Object.assign({}, a.cek, { [hal]: v === '1' }); set({ cekG: a }); },
    cgCatatan: (v) => { const a = Object.assign({ cek: {}, catatan: '' }, st().cekG || {}); a.catatan = String(v).slice(0, 160); set({ cekG: a }); },
    cgSimpan: async () => { const a = st().cekG || { cek: {}, catatan: '' }; await tulis(S.susunCekGudang(a.cek, a.catatan, waktu(), kini())); },
    // Pondasi paket kedua C (owner 24 Nov 2026, rules v20): buku pegangan — owner menulis / mengubah / menghapus / menggeser bab; staf hanya membuka-tutup bab
    bpgBaru: () => set({ bpgDraf: S.ssDrafBab(''), yakinBpg: null, kabar: '' }), bpgUbah: ({ id }) => set({ bpgDraf: S.ssDrafBab(id), yakinBpg: null, kabar: '' }), bpgBatal: () => set({ bpgDraf: null }),
    bpgKetik: (v, el) => { const a = Object.assign({}, st().bpgDraf || S.ssDrafBab('')); a[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'isi' ? S.SS_PEGANGAN_MAKS.isi + 200 : S.SS_PEGANGAN_MAKS.judul + 20); set({ bpgDraf: a }); },
    bpgUntuk: ({ u }) => set({ bpgDraf: Object.assign({}, st().bpgDraf || S.ssDrafBab(''), { untuk: u }) }),
    bpgSimpan: () => tulis(S.susunBabPegangan(st().bpgDraf || {}, waktu())),
    bpgHapus: ({ id }) => (st().yakinBpg === id ? tulis(S.susunHapusBab(id, waktu())) : set({ yakinBpg: id, kabar: '' })),
    bpgGeser: ({ id, arah }) => tulis(S.susunGeserBab(id, Number(arah), waktu())),
    bpgBuka: ({ id }) => { const o = Object.assign({}, st().bpgBuka); o[id] = !o[id]; set({ bpgBuka: o }); },
    // Pondasi paket keempat (owner 25 Nov 2026): pembagian tugas — siapa pegang apa & penggantinya; owner menulis, staf membaca
    tgsBaru: () => set({ tgsDraf: S.ssDrafTugas(''), yakinTgs: null, kabar: '' }), tgsUbah: ({ id }) => set({ tgsDraf: S.ssDrafTugas(id), yakinTgs: null, kabar: '' }), tgsBatal: () => set({ tgsDraf: null }),
    tgsKetik: (v, el) => { const a = Object.assign({}, st().tgsDraf || S.ssDrafTugas('')); a[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'urusan' ? S.SS_TUGAS_MAKS.urusan + 10 : S.SS_TUGAS_MAKS.nama + 10); set({ tgsDraf: a }); },
    tgsSimpan: () => tulis(S.susunTugas(st().tgsDraf || {}, waktu())),
    tgsHapus: ({ id }) => (st().yakinTgs === id ? tulis(S.susunHapusTugas(id, waktu())) : set({ yakinTgs: id, kabar: '' })),
    kpiBatal: () => set({ aturKpi: null }), kpiSimpan: async () => { const a = st().aturKpi; if (!a) return set({ kabar: 'Belum ada yang diubah', kabarAwas: false }); if (await tulis(KL.susunAturKpi(a, waktu()))) set({ aturKpi: null }); },
    hariP: ({ h }) => set({ hariP: Number(h), pilihG: null }), pilihG: ({ id }) => set({ pilihG: st().pilihG === id ? null : id, catatanG: '', yakinWa: false }), catatanG: (v) => set({ catatanG: String(v).slice(0, 80) }),
    selesaiG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); if (await tulis(S.susunSelesaiPengingat(p, st().catatanG, waktu()))) set({ pilihG: null, catatanG: '' }); },
    tundaG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); if (await tulis(S.susunTundaPengingat(p, waktu()))) set({ pilihG: null }); },
    waG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); const r = S.susunWaPengingat(kini(), p, waktu(), st().yakinWa); if (r.perluYakin) return set({ yakinWa: true, kabar: r.tolak, kabarAwas: true }); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); try { window.open(r.url, '_blank'); } catch (e) { /* abaikan */ } if (await tulis(r)) set({ yakinWa: false }); },
    saklarG: async ({ jenis }) => { await tulis(S.susunSaklarPengingat(jenis, waktu())); }, keG: async ({ jenis, nama }) => { await tulis(S.susunKePengingat(jenis, nama, waktu())); },
    // ---- ATUR SENDIRI per lembar Sistem (angka & daftar owner)
    bukaAtur: () => { if (st().atur) return set({ atur: null }); const id = st().sistem; const a = S.ssAtur(id); const d = { id };
      if (id === 'perangkat') Object.assign(d, { batasAntre: String(a.batasAntre), batasDenyut: String(a.batasDenyut), pemegang: a.pemegang.slice(), cuaca: a.cuaca ? Object.assign({}, a.cuaca) : null });
      // owner 7 Okt (JS2-C): batas nego per orang — jatah per peran & per akun (kosong = ikut peran), siapa boleh di bawah modal, langkah harga
      if (id === 'peran') { const ja = {}; Object.keys(a.jatahAkun || {}).forEach((u) => { ja[u] = String(a.jatahAkun[u]); });
        Object.assign(d, { batasSekaligus: String(a.batasSekaligus), jatahBen: String(a.jatahBen), jatahKaryawan: String(a.jatahKaryawan), langkahNego: String(a.langkahNego), jatahAkun: ja, bawahModal: (a.bawahModal || []).slice() }); }
      if (id === 'cadangan') Object.assign(d, { simpanHari: String(a.simpanHari), ambangKuota: String(a.ambangKuota), cadanganTiap: String(a.cadanganTiap) });
      if (id === 'lokasi') Object.assign(d, { daftar: a.daftar.map((l) => Object.assign({}, l)), pengantar: a.pengantar.slice() });
      if (id === 'pengingat') Object.assign(d, { hariBon: String(a.hariBon), hariJanji: String(a.hariJanji), hariKantong: String(a.hariKantong), hariOpname: String(a.hariOpname), hariCadangan: String(a.hariCadangan), tundaHari: String(a.tundaHari), maksTunda: String(a.maksTunda), opnameTiap: String(a.opnameTiap) });
      set({ atur: d, kabar: '' }); },
    aturKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().atur)); const k = el.dataset.kolom, i = el.dataset.i, sub = el.dataset.sub; if (i === undefined) a[k] = String(v).slice(0, 12); else if (sub) a[k][Number(i)][sub] = String(v).slice(0, 60); else a[k][Number(i)] = String(v).slice(0, 40); set({ atur: a }); },
    aturTambah: ({ daftar: k }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].push(k === 'daftar' ? { id: 'lk' + Date.now().toString(36), nama: '', alamat: '', utama: false } : ''); set({ atur: a }); },
    aturLepas: ({ daftar: k, i }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].splice(Number(i), 1); set({ atur: a }); },
    aturUtama: ({ i }) => { const a = JSON.parse(JSON.stringify(st().atur)); a.daftar.forEach((l, j) => { l.utama = j === Number(i); }); set({ atur: a }); },
    // owner 7 Okt (JS2-C): jatah nego per akun (kosong = ikut perannya) & saklar "boleh di bawah modal" per orang / peran
    // ---- T1-3 (owner 16 Nov): orang di tablet — PIN diketik di sini, yang ditulis hanya hasil PBKDF2 bergaram (tablet-logika.js) ----
    tbIsi: (v, el) => { const t = Object.assign({}, st().tb); const k = el.dataset.kolom; t[k] = k === 'nama' ? String(v).slice(0, 30) : String(v).replace(/[^\d]/g, '').slice(0, 6); set({ tb: t }); },
    tbPeran: ({ peran }) => set({ tb: Object.assign({}, st().tb, { peran }) }),
    tbTambah: async () => { if (st().tbSibuk) return; set({ tbSibuk: true, kabar: 'Menyimpan…', kabarAwas: false }); let r;
      try { r = await TB.tbSusunTambah(st().tb, waktu()); } catch (e) { r = { tolak: String((e && e.message) || e) }; }
      set({ tbSibuk: false }); if (await tulis(r)) set({ tb: { nama: '', peran: st().tb.peran, pin: '', pin2: '' } }); },
    tbGanti: ({ id }) => set({ tbGanti: st().tbGanti === id ? null : id, tbPinBaru: { pin: '', pin2: '' }, yakinTb: null, kabar: '' }),
    tbPinIsi: (v, el) => { const t = Object.assign({}, st().tbPinBaru); t[el.dataset.kolom] = String(v).replace(/[^\d]/g, '').slice(0, 6); set({ tbPinBaru: t }); },
    tbGantiSimpan: async () => { const id = st().tbGanti; if (!id || st().tbSibuk) return; set({ tbSibuk: true }); let r;
      try { r = await TB.tbSusunGantiPin(id, st().tbPinBaru.pin, st().tbPinBaru.pin2, waktu()); } catch (e) { r = { tolak: String((e && e.message) || e) }; }
      set({ tbSibuk: false }); if (await tulis(r)) set({ tbGanti: null, tbPinBaru: { pin: '', pin2: '' } }); },
    tbAktif: async ({ id, aktif }) => { await tulis(TB.tbSusunAktif(id, aktif === '1', waktu())); },
    tbPeranUbah: async ({ id, peran }) => { await tulis(TB.tbSusunPeran(id, peran, waktu())); },
    tbHapus: async ({ id }) => { if (st().yakinTb !== id) { const o = TB.tbDaftar().find((x) => x.id === id); return set({ yakinTb: id, kabar: 'Ketuk HAPUS sekali lagi: ' + (o ? o.nama : 'orang ini') + ' tidak bisa masuk di tablet lagi. Catatan lamanya tetap atas namanya.', kabarAwas: true }); }
      set({ yakinTb: null }); await tulis(TB.tbSusunHapus(id, waktu())); },
    aturJatahAkun: (v, el) => { const a = JSON.parse(JSON.stringify(st().atur)); a.jatahAkun = a.jatahAkun || {}; a.jatahAkun[el.dataset.uid] = String(v).replace(/[^\d]/g, '').slice(0, 3); set({ atur: a }); },
    aturBawahModal: ({ kunci }) => { const a = JSON.parse(JSON.stringify(st().atur)); const L = a.bawahModal || []; const i = L.indexOf(kunci); if (i >= 0) L.splice(i, 1); else L.push(kunci); a.bawahModal = L; set({ atur: a }); },
    // owner 26 Nov 2026: lokasi langit & cuaca gerbang — ketik nama tempat, cari (Open-Meteo, Indonesia saja), pilih; tersimpan bersama SIMPAN ATURAN
    cuacaCariKetik: (v) => set({ cuacaCari: String(v).slice(0, 60) }),
    cuacaCari: async () => {
      const url = lgUrlCari(st().cuacaCari); if (!url) return set({ cuacaKabar: 'Ketik paling sedikit 3 huruf nama kelurahan, kecamatan, atau kota', cuacaHasil: [] });
      set({ cuacaSibuk: true, cuacaKabar: '' });
      try { const r = await fetch(url, { cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' }); const hasil = r.ok ? lgBacaCari(await r.json()) : [];
        set({ cuacaSibuk: false, cuacaHasil: hasil, cuacaKabar: r.ok ? (hasil.length ? '' : 'Tidak ketemu — coba nama kecamatan atau kota') : 'Pencarian ditolak (' + r.status + ') — coba lagi nanti' }); }
      catch (e) { set({ cuacaSibuk: false, cuacaKabar: 'Tidak bisa mencari tempat (internet?) — coba lagi nanti' }); }
    },
    cuacaPilih: ({ i }) => { const r = st().cuacaHasil[Number(i)]; const l = r ? lgLokasiSah({ nama: r.nama + (r.wilayah ? ', ' + r.wilayah.split(', ').slice(-2).join(', ') : ''), lat: r.lat, lon: r.lon }) : null;
      if (!l) return; set({ atur: Object.assign({}, st().atur, { cuaca: l }), cuacaHasil: [], cuacaCari: '', cuacaKabar: '' }); },
    cuacaCabut: () => set({ atur: Object.assign({}, st().atur, { cuaca: null }), cuacaHasil: [], cuacaKabar: '' }),
    simpanAtur: async () => { const a = st().atur; if (!a) return; const isi = Object.assign({}, a); delete isi.id; if (await tulis(S.susunAturSistem(a.id, isi, waktu()))) set({ atur: null }); },
    // owner 21 Nov 2026: notifikasi HP / Mac owner saat aplikasi tertutup. Kunci publik web push proyek (aturanToko/notif) ditempel owner SEKALI;
    // tiap perangkat lalu menyalakan sendiri (izin diminta langsung dari ketukan — Safari menolak bila tidak).
    nhKetik: (v) => set({ nhVapid: String(v).trim().slice(0, 140) }),
    nhSimpanKunci: async () => { const v = st().nhVapid; if (!nhVapidSah(v)) return set({ kabar: 'Kunci ini bukan kunci publik web push (base64url ±87 huruf, diawali B) — salin dari Console › Project settings › Cloud Messaging › Web Push certificates › Key pair', kabarAwas: true });
      const w = waktu(); if (await tulis({ dokumen: [{ koleksi: 'aturanToko', data: { id: 'notif', vapid: v, tanggal: w.tanggal, jam: w.jam } }], patch: { kabar: 'Kunci notifikasi tersimpan — sekarang tekan Nyalakan di tiap HP / Mac owner', kabarAwas: false } })) set({ nhVapid: '' }); },
    nhNyala: async () => { if (st().nhSibuk) return; const p = nhNyalakan(vapidToko()); set({ nhSibuk: true, kabar: 'Menyalakan notifikasi…', kabarAwas: false }); const r = await p;
      set({ nhSibuk: false, kabar: r.ok ? 'Notifikasi menyala di perangkat ini — titipan, pesan & permintaan dari tablet muncul walau aplikasi tertutup' : 'Notifikasi BELUM menyala: ' + r.pesan, kabarAwas: !r.ok }); },
    // owner 23 Nov 2026: push aplikasi tablet — izin Android diminta langsung dari ketukan; token atas nama akun yang masuk di tablet
    ntNyala: async () => { if (st().ntSibuk) return; const p = ntNyalakan(); set({ ntSibuk: true, kabar: 'Menyalakan notifikasi tablet…', kabarAwas: false }); const r = await p;
      set({ ntSibuk: false, kabar: r.ok ? 'Notifikasi tablet menyala — jawaban owner muncul di bilah notifikasi tablet walau aplikasinya ditutup' : 'Notifikasi tablet BELUM menyala: ' + r.pesan, kabarAwas: !r.ok }); },
    ntMati: async () => { if (st().ntSibuk) return; set({ ntSibuk: true }); const r = await ntMatikan(); set({ ntSibuk: false, kabar: r.ok ? 'Notifikasi tablet dimatikan' : 'Gagal mematikan: ' + r.pesan, kabarAwas: !r.ok }); },
    // owner 23 Nov 2026: layar penuh Android (bilah jam & tombol kembali/beranda disembunyikan) — disimpan aplikasi tablet sendiri
    lpSetel: async ({ n }) => { if (st().lpSibuk) return; const nyala = n === '1'; set({ lpSibuk: true });
      try { const r = await setelLayarPenuh(nyala); set({ lpSibuk: false, ntInfo: Object.assign({}, st().ntInfo || {}, { layarPenuh: !!(r && r.layarPenuh) }), kabar: nyala ? 'Layar penuh menyala — geser dari tepi bawah layar untuk memunculkan tombol Android sebentar' : 'Layar penuh dimatikan — bilah jam & tombol Android tampil lagi', kabarAwas: false }); }
      catch (e) { set({ lpSibuk: false, kabar: 'Layar penuh gagal: ' + String((e && (e.message || e.code)) || e), kabarAwas: true }); } },
    nhMati: async () => { if (st().nhSibuk) return; set({ nhSibuk: true }); const r = await nhMatikan(); set({ nhSibuk: false, kabar: r.ok ? 'Notifikasi dimatikan di perangkat ini' : 'Gagal mematikan: ' + r.pesan, kabarAwas: !r.ok }); },
    // owner 21 Nov 2026: Ringkas hari ini di tablet — owner memilih SATU orang di tablet yang membukanya, dan menandai akun tablet yang membaca data uang
    rtPilihOrang: ({ id }) => tulis(S.susunAturSistem('peran', { ringkasOrang: id === '-' ? '' : id }, waktu())),
    // owner 23 Nov 2026 (sidik jari Tahap B)
    owBukaNyala: () => set({ owBukaNyala: !st().owBukaNyala, owSandi: '' }),
    owSandiKetik: (v) => set({ owSandi: String(v).slice(0, 128) }),
    owNyalakan: async () => { const X = ow(); if (!X || st().owSibuk) return; const sandi = st().owSandi; set({ owSibuk: true, owSandi: '' }); const r = await X.nyalakan(sandi);
      set({ owSibuk: false, owBukaNyala: !r.ok, kabar: r.kalimat, kabarAwas: !r.ok }); },
    owMatikan: () => { const X = ow(); if (!X) return; if (!st().yakinOw) return set({ yakinOw: true, kabar: 'Ketuk sekali lagi: sandi owner yang terkunci dihapus dari tablet ini', kabarAwas: true });
      const r = X.matikan(); set({ yakinOw: false, kabar: r.kalimat, kabarAwas: false }); },
    owBukaTolak: ({ id }) => set({ owTolak: st().owTolak === id ? null : id, owAlasan: '' }),
    owAlasanKetik: (v) => set({ owAlasan: String(v).slice(0, 80) }),
    owPutus: async ({ id, a }) => { const X = ow(); if (!X || st().owSibuk) return; set({ owSibuk: true }); const r = await X.putus(id, a, a === 'tolak' ? st().owAlasan : '');
      set({ owSibuk: false, owTolak: r.ok ? null : st().owTolak, owAlasan: r.ok ? '' : st().owAlasan, kabar: r.kalimat, kabarAwas: !r.ok }); },
    sjNyalakan: async () => { const X = sj(); if (!X || st().sjSibuk) return; set({ sjSibuk: true }); const r = await X.nyalakan(); set({ sjSibuk: false, kabar: r.kalimat, kabarAwas: !r.ok }); },
    sjMatikan: async () => { const X = sj(); if (!X || st().sjSibuk) return; set({ sjSibuk: true }); const r = await X.matikan(); set({ sjSibuk: false, kabar: r.kalimat, kabarAwas: !r.ok }); },
    sjIntip: async () => { const X = sj(); if (!X || st().sjSibuk) return; set({ sjSibuk: true }); const r = await X.mintaIntip(); set({ sjSibuk: false, kabar: r.kalimat, kabarAwas: !r.ok }); },
    sjTutupIntip: () => { const X = sj(); if (X) X.tutupIntip(); set({ kabar: 'Intip uang ditutup — data uang dikosongkan dari tablet', kabarAwas: false }); },
    // owner 22 Nov 2026: riwayat & batal (tahap 1 uang)
    rsSaring: ({ g }) => set({ rsSaring: g || '', rsN: 40 }),
    rsLagi: () => set({ rsN: (Number(st().rsN) || 40) + 40 }),
    ruGeser: ({ d }) => { const n = Number(d); const kiniIso = hariIniIso(kini()); const dasar = st().ruHari || kiniIso; const t = new Date(dasar + 'T12:00:00'); t.setDate(t.getDate() + n);
      set({ ruHari: n === 0 ? kiniIso : hariIniIso(t), ruBuka: null, yakinRu: null, ruAlasan: '' }); },
    ruSaring: ({ o }) => set({ ruSaring: o || '', ruBuka: null, yakinRu: null }),
    ruBuka: (_, el) => { const k = el.dataset.kRu; set({ ruBuka: st().ruBuka === k ? null : k, ruAlasan: '', yakinRu: null, kabar: '' }); },
    ruAlasan: ({ a }) => set({ ruAlasan: a, yakinRu: null }),
    ruAlasanKetik: (v) => set({ ruAlasan: String(v).slice(0, 120), yakinRu: null }),
    ruBatal: async () => { const k0 = st().ruBuka; if (!k0) return; const brg = /^barang\|/.test(k0); const k1 = brg ? k0.slice(7) : k0; const koleksi = k1.slice(0, k1.indexOf('|')); const id = k1.slice(k1.indexOf('|') + 1); const k = k0;
      if (!String(st().ruAlasan || '').trim()) return set({ kabar: 'Pilih atau ketik alasannya dulu', kabarAwas: true });
      if (st().yakinRu !== 'b:' + k) return set({ yakinRu: 'b:' + k, kabar: 'Ketuk sekali lagi untuk membatalkan — akibatnya tertulis di atas tombol', kabarAwas: true });
      if (await tulis((brg ? RB.rbSusunBatal : RU.ruSusunBatal)(koleksi, id, st().ruAlasan, waktu()))) set({ ruBuka: null, ruAlasan: '', yakinRu: null }); else set({ yakinRu: null }); },
    ruPulih: async ({ id }) => { if (st().yakinRu !== 'p:' + id) return set({ yakinRu: 'p:' + id, kabar: 'Ketuk sekali lagi: catatan kembali ke buku persis seperti semula', kabarAwas: true });
      set({ yakinRu: null }); const x = RU.ruDibatalkan().find((b) => b.id === String(id)); await tulis((x && x.jenisBatal === 'barang' ? RB.rbSusunPulih : RU.ruSusunPulih)(id, waktu())); },
    ruHapus: async ({ id }) => { if (st().yakinRu !== 'h:' + id) return set({ yakinRu: 'h:' + id, kabar: 'Ketuk sekali lagi: salinannya hilang selamanya dari daftar Dibatalkan', kabarAwas: true });
      set({ yakinRu: null }); await tulis(RU.ruSusunHapusPermanen(id)); },
    rtIntip: ({ d }) => tulis(S.susunAturSistem('peran', { intipDetik: Number(d) }, waktu())),   // owner 22 Nov 2026: lama intip uang (detik)
    rtBacaUang: async ({ uid, nyala }) => { const kunci = uid + ':' + nyala; const r = S.susunUbahAkun(uid, { bacaUang: nyala === '1' }, waktu(), st().yakinRt === kunci);
      if (r.perluYakin) return set({ yakinRt: kunci, kabar: r.tolak, kabarAwas: true }); set({ yakinRt: null }); await tulis(r); },
  }, aksiTitipan({ set, st, tulis, akun: opsi.akun, waktu }), aksiUsulBanding({ set, st, tulis, akun: opsi.akun, waktu }), aksiTutupTablet({ set, st, tulis, akun: opsi.akun, waktu }), aksiRingkas({ set, st, akun: opsi.akun, uang: opsi.statusUang, waktu, kini }));
  const vapidToko = () => { const d = cacheMentah('aturan').find((x) => String(x.id) === 'notif'); return d && d.vapid ? String(d.vapid) : ''; };
  Object.assign(AKSI, aksiPanelPatuh({ set, st, tulis, waktu, kini }));   // owner 26 Nov 2026: kalender kepatuhan — tanda "sudah dikerjakan" dari Pengingat
  delegasi(akar, AKSI);

  // ---------- GAMBAR ----------
  function gambar() {
    if (!tampil || terkunci()) { _kotor = true; return; } _kotor = false;
    _kunciGambar = kunciGambar();
    const s = st(); const sumber = sumberData(); const d = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="label">Menu</div><div class="serif" style="font-size: 24px;">${s.sistem ? JUDUL_SISTEM[s.sistem] : s.susunan === 'laci' ? 'Pita jam di atas laci' : s.susunan === 'tanya' ? 'Menu yang bertanya' : s.susunan === 'jam' ? 'Menu yang tahu jam' : s.susunan === 'orang' ? 'Menu menurut orang' : 'Menu yang menolak'}</div>
          <div class="ket">${tanggalPendek(hariIniIso(d))} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">${opsi.lonceng ? mentah(opsi.lonceng()) : ''}<div class="pil pil-akun ${sumber.jenis === 'firestore' ? '' : 'kedip'}" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON_MODE[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      ${s.sistem ? gambarSistem(s, d) : gambarMenu(s, d)}
    `);
    gulirkan(akar, RP);
  }
  const barisLaci = (b, terbuka) => h`<div class="mn-baris ${b.awas ? 'awas' : ''} ${terbuka ? 'buka' : ''}" data-k="b-${b.id}" data-aksi="baris" data-id="${b.id}">
      <div class="mn-ikon">${ik(b.ikon)}</div>
      <div style="min-width: 0;"><div class="mn-judul">${b.judul}</div><div class="mn-sub">${b.sub}</div></div>
      <div class="mn-kanan"><div class="mn-n ${b.awas ? 'awas' : ''}">${b.angka}</div><div class="mn-cap">${b.cap}</div></div>
      ${terbuka ? h`<div class="mn-j" data-k="j">${b.jawab ? h`<div>${b.jawab}</div>` : ''}<div class="mn-ke" data-aksi="pergi" data-tujuan="${JSON.stringify(b.tujuan)}">${b.tujuan.teks} ›</div></div>` : ''}
    </div>`;
  const grup = (g, s, kelasK) => h`<div class="mn-grup ${s.tutup[g.id] ? 'tutup' : ''} ${kelasK || ''}" data-k="g-${g.id}">
      <div class="mn-kepala" data-aksi="laci" data-id="${g.id}"><div class="label">${g.nama}</div><div class="ket" style="font-size: 10px;">${g.ket}</div><div class="mn-panah">›</div></div>
      <div class="mn-isi">${s.tutup[g.id] ? '' : g.isi.map((b) => barisLaci(b, s.buka === b.id))}</div>
    </div>`;
  function gambarMenu(s, d) {
    // putaran 23 (Tahap 3 tipis): bukan-owner tidak melihat laci owner — barisnya memajang angka uang dari koleksi yang tidak didengarkannya
    const akunM = opsi.akun ? opsi.akun() : null;
    if (akunM && akunM.jenis === 'aktif') return gambarStaf(s, d, akunM);
    const cari = M.susunCari(d, s.cari, () => ingatMenu('orang', '', () => M.mnSemuaOrang(d))); const L = lokal();
    return h`<section class="mn-gulir" data-k="menu">
      <div class="jalur kisi5" data-k="susunan">${M.MN_SUSUNAN.map(([id, nm]) => h`<div class="seg ${s.susunan === id ? 'aktif' : ''}" data-aksi="susunan" data-s="${id}">${nm}</div>`)}</div>
      <label class="mn-cari" data-k="cari">${ik('cari', 16)}<input type="text" placeholder="Cari layar, merek, atau nama orang" value="${s.cari}" data-ketik="cari">${s.cari ? h`<span class="mn-x" data-aksi="cariHapus">×</span>` : ''}</label>
      ${s.cari.length >= 2 ? h`<div class="mn-grup" data-k="g-cari"><div class="mn-kepala"><div class="label">Hasil cari</div><div class="ket" style="font-size: 10px;">${cari.kosong ? 'tidak ada yang cocok' : cari.hasil.length + ' cocok' + (cari.lebih ? ' · ' + cari.lebih + ' lagi tidak ditampilkan' : '')}</div></div>
        <div class="mn-isi">${cari.hasil.map((r, i) => h`<div class="mn-baris" data-k="c-${i}" data-aksi="pergi" data-tujuan="${JSON.stringify(r.tujuan)}"><div class="mn-ikon">${ik(r.jenis === 'orang' ? 'orang' : r.jenis === 'merek' ? 'kotak' : 'dokumen')}</div><div style="min-width: 0;"><div class="mn-judul">${r.judul}</div><div class="mn-sub">${r.sub}</div></div><div class="mn-kanan"><div class="mn-cap">${r.tujuan.teks} ›</div></div></div>`)}</div></div>` : ''}
      ${s.susunan === 'laci' ? gambarLaci(s, d, L) : s.susunan === 'tanya' ? gambarTanya(s, d) : s.susunan === 'jam' ? M.susunMenurutJam(d).map((g) => grup(g, s, g.sekarang ? 'sekarang' : '')) : s.susunan === 'orang' ? M.susunMenurutOrang(d).map((g) => grup(g, s)) : M.susunTertutup(d).map((g) => grup(g, s))}
      <div class="mn-kaki" data-k="kaki">${s.susunan === 'laci' ? 'Laci paling atas berubah menurut bagian hari; sepuluh laci di bawahnya (dan dua baris Sistem) tidak pernah berpindah tempat — menu yang isinya berpindah-pindah wajib dibaca ulang tiap kali dibuka, dan jempol tidak pernah hafal. Lencana merah = barisnya menyimpan sesuatu yang belum beres, bukan sekadar besar.'
        : s.susunan === 'tanya' ? 'Tiap baris satu pertanyaan, dan jawabannya sudah kelihatan sebelum diketuk. Yang belum bisa dihitung ditulis begitu — tidak ditebak.' : s.susunan === 'jam' ? 'Jam diambil dari tulisan yang jamnya terbaca; tulisan tanpa jam tidak dihitung dan disebut jumlahnya.' : s.susunan === 'orang' ? 'Satu nama, seluruh buku yang menyentuhnya — sistem lama menyusun semuanya menurut BUKU, tidak ada satu tempat pun menurut orang.' : 'Pintu yang tertutup dibiarkan tampak, berikut sebabnya dan apa yang membukanya. Pintu yang sudah terbuka ditulis terbuka.'}
        ${sumberData().jenis === 'cadangan' ? ' Angka di layar ini dari CADANGAN yang sedang dibaca, bukan data toko hari ini.' : ' Semua angka dari data toko lewat mesin yang sama dengan sistem lama; tidak ada angka yang lahir di layar Menu.'}</div>
    </section>`;
  }
  // owner 22 Nov 2026 (sidik jari Tahap A): opsi.sidik = { lokal(), ada(), intip(), mintaIntip(), tutupIntip(), nyalakan(), matikan() } dari app.js
  const sj = () => opsi.sidik || null;
  const intipNyala = () => !!(sj() && sj().intip());
  function kartuSidik(s, akunM) {
    const X = sj(); if (!X) return '';
    const asli = X.akunAsli ? X.akunAsli() : null; const L = X.lokal(); const orang = SJ.sjOrang();
    if (String(akunM.operatorId || '') === orang && orang) {   // orang pilihan owner yang jaga: nyalakan / matikan di tablet ini
      const K = SJ.sjKeadaan(L, asli, orang, X.ada());
      return h`<div class="kartu" data-k="sj-kartu" style="gap: 6px;"><div class="label">Sidik jari owner di tablet ini</div>
        <div class="pita-info ${K.st === 'nyala' ? 'emas' : K.st === 'hangus' ? 'awas' : ''}" data-k="sj-st">${K.teks}</div>
        ${K.st === 'tidak' ? '' : K.st === 'nyala' ? h`<div class="kaca-btn" data-aksi="sjMatikan" data-k="sj-matikan">${s.sjSibuk ? '…' : 'Matikan sidik jari'}</div>`
          : h`<div class="kaca-btn aktif emas" data-aksi="sjNyalakan" data-k="sj-nyalakan">${s.sjSibuk ? 'tempel jari…' : 'NYALAKAN · tempel jari owner'}</div>
            <div class="ket" style="font-size: 11px;">Sebelum menyalakan: buka Setelan tablet › Keamanan › Sidik jari — pastikan HANYA jari lu yang terdaftar. Jari yang sudah terdaftar sebelum dinyalakan tidak terdeteksi.</div>`}</div>`;
    }
    if (intipNyala()) return h`<div class="kaca-btn kecil" data-aksi="sjTutupIntip" data-k="sj-tutup-intip" style="align-self: flex-start;">Tutup intip uang</div>`;
    return SJ.sjBolehIntip(akunM, L, asli, orang) ? h`<div class="kaca-btn kecil" data-aksi="sjIntip" data-k="sj-intip" style="align-self: flex-start;">${s.sjSibuk ? 'tempel jari…' : 'Intip uang · sidik jari owner'}</div>` : '';
  }
  // owner 23 Nov 2026 (sidik jari Tahap B): opsi.ownerTablet = { keadaan(), daftar(), nyalakan(sandi), matikan(), putus(id, aksi, alasan) } dari app.js.
  // Tiap putusan = tempel jari owner. Sandi owner hanya diketik waktu menyalakan (kolom sandi, tidak pernah disimpan sebagai isian / draf).
  const ow = () => opsi.ownerTablet || null;
  function kartuOwnerTablet(s) {
    const X = ow(); if (!X) return '';
    const K = X.keadaan(); if (K.st === 'tidak') return '';
    if (K.st !== 'nyala') return h`<div class="kartu" data-k="ow-kartu" style="gap: 6px;"><div class="label">Putusan owner di tablet</div><div class="pita-info" data-k="ow-st">${K.teks}</div>
      ${s.owBukaNyala ? h`<input class="ketik-nama" type="password" autocomplete="off" placeholder="sandi akun owner" value="${s.owSandi || ''}" data-ketik="owSandiKetik" maxlength="128">
        <div class="kaca-btn aktif emas" data-aksi="owNyalakan" data-k="ow-nyalakan">${s.owSibuk ? 'memeriksa sandi · tempel jari…' : 'NYALAKAN · tempel jari owner'}</div>
        <div class="ket" style="font-size: 11px;">Sandi diperiksa ke server, lalu dikunci sidik jari di tablet ini — tidak tersimpan terbuka. Pastikan HANYA jari lu yang terdaftar di Setelan tablet.</div>`
        : h`<div class="kaca-btn kecil" data-aksi="owBukaNyala" data-k="ow-buka" style="align-self: flex-start;">Nyalakan (owner)</div>`}</div>`;
    const D = X.daftar();
    return h`<div class="kartu" data-k="ow-kartu" style="gap: 6px;"><div class="label">Putusan owner · ${D.length ? D.length + ' menunggu' : 'tidak ada yang menunggu'}</div>
      ${D.map((m) => h`<div class="ug-baris dua" data-k="ow-${m.id}"><div style="min-width: 0;"><div>${m.dari} · ${m.namaTindakan || m.tindakan}${m.n ? h` · <b>${RP(m.n)}</b>` : ''}</div><div class="k2">${m.teks}</div>
          ${m.hanyaHp ? h`<div class="k2">${m.hanyaHp}</div>` : ''}
          ${s.owTolak === m.id ? h`<div style="display: flex; gap: 6px; margin-top: 6px;"><input class="ketik-nama" type="text" placeholder="alasan menolak (wajib)" value="${s.owAlasan || ''}" data-ketik="owAlasanKetik" maxlength="80">
            <div class="kaca-btn aktif awas" data-aksi="owPutus" data-id="${m.id}" data-a="tolak">${s.owSibuk ? 'tempel jari…' : 'TOLAK · jari'}</div></div>` : ''}</div>
        <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-end;">
          ${m.boleh.setuju ? h`<div class="kaca-btn kecil aktif emas" data-aksi="owPutus" data-id="${m.id}" data-a="setuju">${s.owSibuk ? '…' : 'Setujui · jari'}</div>` : ''}
          ${m.boleh.dibaca ? h`<div class="kaca-btn kecil aktif" data-aksi="owPutus" data-id="${m.id}" data-a="dibaca">${s.owSibuk ? '…' : 'Dibaca · jari'}</div>` : ''}
          ${m.boleh.tolak ? h`<div class="kaca-btn kecil ${s.owTolak === m.id ? 'aktif' : ''}" data-aksi="owBukaTolak" data-id="${m.id}">${s.owTolak === m.id ? 'tutup' : 'Tolak'}</div>` : ''}</div></div>`)}
      <div class="pita-info emas" data-k="ow-st" style="font-size: 12px;">${K.teks}</div>
      <div class="kaca-btn kecil" data-aksi="owMatikan" data-k="ow-matikan" style="align-self: flex-start;">${s.yakinOw ? 'KETUK LAGI · matikan' : 'Matikan putusan owner'}</div></div>`;
  }
  function gambarStaf(s, d, akunM) {
    const namaP = (S.SS_PERAN.find((p) => p.id === akunM.peran) || {}).nama || akunM.peran; const L = lokal();
    const AL = opsi.antreLokal ? opsi.antreLokal() : { belum: [], ditolak: [] };
    const orang = TB.tbDaftar().filter((o) => o.aktif).map((o) => o.nama);
    return h`<section class="mn-staf" data-k="staf" style="display: flex; flex-direction: column; gap: 10px;">
      ${RT.rtTampil(akunM) || intipNyala() ? kartuRingkas(s, { akun: akunM, uang: opsi.statusUang ? opsi.statusUang() : null, kini: kini(), intip: intipNyala() ? SJ.sjIntipDetik() : 0 }) : ''}
      ${kartuSidik(s, akunM)}
      ${kartuOwnerTablet(s)}
      ${kartuTitipan(s, { akun: akunM, orang, kiniIso: hariIniIso(kini()) })}
      ${hlTampil(akunM) ? kartuTutupTablet(s, { akun: akunM, kini: kini() }) : ''}
      <div class="kartu" data-k="staf-akun" style="gap: 4px;"><div class="label">Masuk sebagai</div><div class="serif" style="font-size: 20px;">${akunM.nama}</div><div class="k2">${namaP} · ${L.namaPerangkat || 'perangkat ini'}</div></div>
      ${akunM.peran === 'ben' ? kartuCekGudang(s, d) : ''}
      ${akunM.peran === 'ben' ? kartuUsulBanding(s, { akun: akunM }) : ''}
      ${kartuPegangan(s, akunM)}
      <div class="tombol-baris" data-k="staf-layar">${[['jual', 'Jual'], ['pelanggan', 'Pelanggan'], ['stok', 'Stok']].map(([t, n]) => h`<div class="kaca-btn aktif" data-aksi="stafKe" data-t="${t}">${n}</div>`)}</div>
      <div class="kartu" data-k="staf-antre" style="gap: 4px;"><div class="label">Catatan dari perangkat ini</div>
        <div class="k2">${(L.antre || []).length ? (L.antre || []).length + ' menunggu server' : 'semua sudah sampai server'} · ${AL.ditolak.length ? AL.ditolak.length + ' DITOLAK server — menunggu owner memutuskan' : 'tidak ada yang ditolak'}</div></div>
      ${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}
      ${gambarLancar(s)}
      <div class="pita-info" data-k="staf-ket">Laci menu owner (uang, laporan, harga, setelan) tidak termasuk hak ${namaP}. Server menegakkan: baca & catat baru; uang keluar dari tablet jadi titipan yang disetujui owner; koreksi & hapus tetap owner.</div>
    </section>`;
  }
  function gambarLaci(s, d, L) {
    const pita = ingatMenu('pita', String(s.bagian), () => M.susunPita(d, s.bagian)); const laci = ingatMenu('laci', JSON.stringify(L), () => M.susunLaci(d, L));
    const gPita = { id: 'pita', nama: pita.kepala, ket: pita.ket, isi: pita.isi.map((b) => Object.assign({}, b, { id: 'pita-' + b.id })) };
    const gGanti = { id: 'ganti', nama: 'Ganti bagian hari', ket: 'lima laci ini urutannya tidak pernah bergeser', isi: [] };
    return [grup(gPita, s, 'pita'),
      h`<div class="mn-grup ${s.tutup.ganti === true ? '' : 'tutup'}" data-k="g-ganti">
        <div class="mn-kepala" data-aksi="laci" data-id="ganti"><div class="label">${gGanti.nama}</div><div class="ket" style="font-size: 10px;">${gGanti.ket}</div><div class="mn-panah">›</div></div>
        <div class="mn-isi">${s.tutup.ganti !== true ? '' : pita.daftarBagian.map((b) => h`<div class="mn-baris ${b.terbuka ? 'buka' : ''}" data-k="bg-${b.id}" data-aksi="bagian" data-b="${b.id}"><div class="mn-ikon">${ik(['bulan', 'keranjang', 'jam', 'naik', 'bulan'][b.id])}</div><div style="min-width: 0;"><div class="mn-judul">${b.nama} ${b.jam}</div><div class="mn-sub">${b.pokok}${b.sekarang ? ' · sekarang' : ''}${b.terbuka ? ' · sedang terbuka' : ''}</div></div><div class="mn-kanan"><div class="mn-n">${ANGKA(b.jumlah)}</div><div class="mn-cap">tulisan masuk buku</div></div></div>`)}</div>
      </div>`,
    ].concat(laci.map((g) => grup(g, s)));
  }
  function gambarTanya(s, d) {
    return h`<div class="mn-grup" data-k="g-tanya">${ingatMenu('tanya', '', () => M.susunTanya(d)).map((t) => h`<div class="mn-tanya ${s.buka === t.id ? 'buka' : ''}" data-k="t-${t.id}" data-aksi="baris" data-id="${t.id}">
        <div class="mn-t-atas"><div class="mn-t">${t.judul}</div><div class="mn-t-n ${t.awas ? 'awas' : ''}">${t.angka}</div></div>
        <div class="mn-j">${t.sub}</div>
        ${s.buka === t.id ? h`<div class="mn-ke" data-aksi="pergi" data-tujuan="${JSON.stringify(t.tujuan)}">${t.tujuan.teks} ›</div>` : h`<div class="mn-ke redup">${t.cap}</div>`}
      </div>`)}</div>`;
  }

  // ---------- SISTEM (lembar di dalam Menu) ----------
  function gambarSistem(s, d) {
    const tabs = TAB_SISTEM[s.sistem]; const tab = tabs.some((t) => t[0] === s.tabS[s.sistem]) ? s.tabS[s.sistem] : (tabs[0] || [''])[0];
    return h`<section class="mn-gulir ss" data-k="sistem-${s.sistem}">
      <div class="mn-kembali" data-aksi="sistem" data-s="">‹ Menu</div>
      ${tabs.length ? h`<div class="jalur kisi${tabs.length}" data-k="tabS">${tabs.map(([id, nm]) => h`<div class="seg ${tab === id ? 'aktif' : ''}" data-aksi="tabS" data-t="${id}">${nm}</div>`)}</div>` : ''}
      ${s.atur ? gambarAtur(s) : s.sistem === 'perangkat' ? gambarPerangkat(s, d, tab) : s.sistem === 'peran' ? gambarPeran(s, d, tab) : s.sistem === 'cadangan' ? gambarCadangan(s, d) : s.sistem === 'lokasi' ? gambarLokasi(s, d, tab) : s.sistem === 'riwayat' ? gambarRiwayat(s, tab) : s.sistem === 'target' ? gambarTarget(s, d) : s.sistem === 'pegangan' ? gambarPegangan(s) : gambarPengingat(s, d, tab)}
    </section>`;
  }
  const pintuAtur = (judul, ringkas) => h`<div class="at-pintu" data-k="pintu-atur" data-aksi="bukaAtur"><div><div style="font-weight: 600;">${judul}</div><div class="ket" style="font-size: 10.5px;">${ringkas}</div></div><div class="ket">ubah ›</div></div>`;
  // hemat baca (owner 7 Okt 2026): keadaan nyala/mati, baca penuh terakhir, per koleksi, daftar siap-nyala, saklar perangkat ini (owner saja)
  function gambarHemat(s) {
    const a = opsi.akun ? opsi.akun() : null; if (a && a.jenis !== 'owner') return h`<div class="kartu" data-k="hemat-staf"><div class="ket">Hemat baca hanya untuk perangkat owner — akun ini selalu membaca penuh.</div></div>`;
    const HB = S.ssHemat(opsi.hemat ? opsi.hemat() : null, opsi.hematSiap ? opsi.hematSiap() : []); const jamMs = (ms) => (ms ? waktuSetempat(new Date(ms).toISOString()) : 'belum pernah');
    return h`<div class="kartu ${HB.kabar.length ? 'awas' : ''}" data-k="hemat" style="gap: 6px;"><div style="font-weight: 700;">${HB.judul}</div><div class="k2">${HB.ket}</div>
        ${HB.kabar.map((t, i) => h`<div class="pita-info awas" data-k="hb-kabar-${i}">${t}</div>`)}
        ${HB.nyala ? h`<div class="k2" data-k="hb-terakhir">Baca penuh terakhir di perangkat ini: ${HB.terbaru ? jamMs(HB.terbaru) : 'belum pernah'}${HB.tertua && HB.tertua !== HB.terbaru ? ' (koleksi paling lama: ' + jamMs(HB.tertua) + ')' : ''} · ${HB.harian}${HB.klaimKabar ? ' · ' + HB.klaimKabar : ''}</div>
          <div class="k2" data-k="hb-baca">Perkiraan baca hari ini: perangkat ini ±${ANGKA(HB.baca ? HB.baca.perangkat : 0)} · toko ±${ANGKA(HB.baca ? HB.baca.toko : 0)} dari kuota 50.000</div>` : ''}
        ${HB.saklar ? h`<div class="kaca-btn ${s.yakinHemat === 'mati' ? 'aktif' : ''}" data-k="hb-mati" data-aksi="hematSaklar" data-ke="mati">${s.yakinHemat === 'mati' ? 'ketuk lagi: matikan & muat ulang' : 'matikan hemat baca di perangkat ini'}</div>`
          : HB.bolehNyala ? h`<div class="kaca-btn ${s.yakinHemat === 'nyala' ? 'aktif' : ''}" data-k="hb-nyala" data-aksi="hematSaklar" data-ke="nyala">${s.yakinHemat === 'nyala' ? 'ketuk lagi: nyalakan & muat ulang' : 'nyalakan hemat baca di perangkat ini'}</div>` : h`<div class="ket" data-k="hb-tidak">${HB.alasanTidak}</div>`}</div>
      <div class="kartu ${HB.siapOk ? '' : 'awas'}" data-k="hemat-siap" style="gap: 4px;"><div class="label">Daftar siap-nyala — hijau 3 hari berturut-turut sebelum menyalakan</div>
        ${HB.siap.map((x) => h`<div class="hb-baris" data-k="hb-siap-${x.id}"><span>${x.teks}</span><span class="k2">${x.ket}</span><span class="pr-cap ${x.ok ? 'ok' : 'awas'}">${x.ok ? 'siap' : 'belum'}</span></div>`)}</div>
      ${HB.nyala ? h`<div class="kartu" data-k="hemat-koleksi" style="gap: 2px;"><div class="label">${HB.nBelum ? HB.nBelum + ' koleksi belum terperiksa dengan server' : 'Semua koleksi cocok dengan server'}</div>
          ${HB.harianBelum ? h`<div class="pita-info emas" data-k="hb-harian">${HB.harianBelum}</div>` : ''}
          ${HB.koleksi.map((x) => h`<div class="hb-baris" data-k="hb-k-${x.k}"><span>${x.nama}<div class="k2">${x.mode}</div></span><span class="k2">${x.ket}<div>dibaca penuh ${jamMs(x.totalPada)}</div></span><span class="pr-cap ${x.ok ? 'ok' : 'awas'}">${x.ok ? 'cocok' : 'belum'}</span></div>`)}
          <div class="hg-pil" data-k="hb-tombol"><div class="seg" data-aksi="hematBaca">baca penuh sekarang</div><div class="seg" data-aksi="hematConsole">saya baru mengubah data lewat Console</div><div class="seg ${s.yakinHemat === 'semua' ? 'aktif' : ''}" data-aksi="hematSemua">${s.yakinHemat === 'semua' ? 'yakin: semua perangkat baca penuh' : 'minta semua perangkat baca penuh'}</div></div></div>` : ''}`;
  }
  // owner 19 Nov 2026 ("masih berat di Android, terutama tablet"): kelancaran PERANGKAT INI — yang mencatat perangkat itu sendiri (inti/ukur-mulus.js),
  // supaya yang diperbaiki berikutnya adalah yang benar-benar tersendat di tablet. Tidak ada isi nota / rupiah, tidak dikirim ke server.
  const infoLancar = () => { const L = lokal(); let ua = '', px = ''; try { ua = String(navigator.userAgent || '').slice(0, 220); px = window.innerWidth + '×' + window.innerHeight + ' @' + (window.devicePixelRatio || 1); } catch (e) { /* bukan peramban */ }
    return { perangkat: L.namaPerangkat || '', peramban: ua, layarPx: px }; };
  function gambarLancar(s) {
    const R = ukurMulusRingkas();
    return h`<div class="kartu" data-k="lancar" style="gap: 6px;"><div style="font-weight: 700;">Kelancaran perangkat ini</div>
      <div data-k="lc-judul">${R.judul}</div>
      ${R.baris.map((b, i) => h`<div class="k2" data-k="lc-b${i}">${b}</div>`)}
      ${R.tempat.length ? h`<div class="label" data-k="lc-berat">Paling berat di</div>${R.tempat.map((x, i) => h`<div class="k2" data-k="lc-t${i}"><b>${x.nama}</b> — ${x.teks}</div>`)}` : ''}
      <div class="k2" data-k="lc-ket">Perangkat ini mencatat sendiri tiap kali layarnya tersendat: berapa lama dan di layar mana. Isi nota, nama, dan rupiah tidak ikut dicatat, dan tidak ada yang dikirim ke server. Mulai dari nol tiap hari.</div>
      <div class="hg-pil" data-k="lc-tombol"><div class="seg ${s.lcBuka ? 'aktif' : ''}" data-k="lc-buka" data-aksi="lcBuka">${s.lcBuka ? 'tutup rincian' : 'lihat rincian'}</div>${R.adaIsi ? h`<div class="seg" data-k="lc-salin" data-aksi="lcSalin">salin rincian</div><div class="seg" data-k="lc-nol" data-aksi="lcNol">mulai dari nol</div>` : ''}</div>
      ${s.lcBuka ? h`<div class="k2" data-k="lc-teks" style="white-space: pre-wrap; font-family: ui-monospace, monospace; font-size: 11px; user-select: text; -webkit-user-select: text;">${ukurMulusSalin(infoLancar())}</div>` : ''}</div>`;
  }
  function gambarPerangkat(s, d, tab) {
    if (tab === 'hemat') return gambarHemat(s);
    const L = lokal(); const P = S.ssPerangkat(d, L.antre, L.idPerangkat); const pilih = P.daftar.find((x) => x.id === s.pilihP) || P.daftar.find((x) => x.ini) || null;
    if (tab === 'antrean') return h`<div class="kartu" data-k="antre" style="gap: 6px;"><div style="font-weight: 700;">${P.nAntre ? P.nAntre + ' catatan perangkat ini menunggu server' : 'Antrean perangkat ini kosong'}</div>
        ${P.antre.map((q) => h`<div class="pr-antre ${q.terlalu ? 'lama' : ''}" data-k="q-${q.koleksi}-${q.id}"><span class="j">${q.jam}</span><span>${q.nama}${q.ringkas ? ' · ' + q.ringkas : ''} <span class="pr-cap ${q.terlalu ? 'awas' : ''}">${q.terlalu ? q.lama + ' menit' : 'menunggu'}</span></span></div>`)}
        <div class="ket">Catatan yang belum sampai disimpan Firestore di perangkat ini dan dikirim SENDIRI begitu tersambung — tidak ada tombol kirim yang perlu ditekan, dan tidak ada yang bisa dibuang dari sini. Dua perangkat menulis catatan yang sama: yang terakhir ditulis yang dipakai; keduanya tercatat di Jejak.</div>
        <div class="kaca-btn aktif" data-aksi="periksaSambung">${s.sambungTeks || 'Periksa: sudah sampai semua?'}</div>
        ${P.lainAntre ? h`<div class="ket awas-teks">${P.lainAntre} catatan menunggu di perangkat LAIN menurut denyut terakhirnya — hanya perangkat itu yang bisa mengirimnya.</div>` : ''}</div>
      ${(() => { const AL = opsi.antreLokal ? opsi.antreLokal() : { belum: [], ditolak: [] }; const owner = !opsi.akun || !opsi.akun() || opsi.akun().jenis === 'owner';
        return h`<div class="kartu ${AL.ditolak.length ? 'awas' : ''}" data-k="ditolak-server" style="gap: 6px;"><div style="font-weight: 700;">${AL.ditolak.length ? AL.ditolak.length + ' kiriman DITOLAK SERVER' : 'Tidak ada kiriman yang ditolak server'}</div>
          <div class="k2">Salinan tiap kiriman disimpan di perangkat ini sampai server mengaku (${AL.belum.length} masih menunggu). Yang ditolak (mis. akunnya dinonaktifkan saat perangkat offline) tidak hilang — tampil di sini sampai owner memutuskan.</div>
          ${AL.ditolak.length || AL.belum.length ? h`<div class="hg-pil"><div class="seg" data-k="unduh-ditolak" data-aksi="unduhDitolak">unduh salinan (JSON)</div></div>` : ''}
          ${AL.ditolak.map((x) => { const kp = kpAlasanDitolak(x, (k, i) => !!dokDiCache(k, i));
            // owner 3 Okt: berapa dokumen kiriman ini SUDAH ada di data toko (sama atau lebih baru) — "ditolak saat sinkron" bisa saja sudah masuk
            const nDok = (x.dokumen || []).length; const nAda = (x.dokumen || []).filter((d) => { const c = dokDiCache(d.koleksi, d.data && d.data.id); return !!c && String(c.diubahPada || '') >= String((d.data && d.data.diubahPada) || ''); }).length;
            return h`<div class="pr-antre lama" data-k="dt-${x.id}"><span class="j">${jamSetempat(x.padaTolak || x.pada)}</span><span>${x.akunNama} (${x.peran || '?'}) · ${(x.dokumen || []).map((d) => d.koleksi).join(', ')} <div class="k2">${(x.dokumen || []).length} dokumen · alasan: ${kp ? kp.kalimat : (x.alasan || '-')}</div><div class="k2" data-k="dt-ada-${x.id}">sudah ada di data toko: ${nAda} dari ${nDok} dokumen${nDok && nAda === nDok ? ' — isinya sudah masuk' : ''}</div>
            ${owner && kp && kp.bisaHariIni ? h`<div class="hg-pil"><div class="seg aktif" data-aksi="tulisUlangHariIni" data-id="${x.id}">catat ulang bertanggal hari ini</div></div>` : ''}
            ${owner ? h`<div class="hg-pil">${kp ? '' : h`<div class="seg" data-aksi="tulisUlangDitolak" data-id="${x.id}">tulis ulang atas nama owner</div>`}<div class="seg ${s.yakinBuang === x.id ? 'aktif' : ''}" data-aksi="buangDitolak" data-id="${x.id}">${s.yakinBuang === x.id ? 'yakin buang' : 'buang'}</div></div>` : h`<div class="k2">Menunggu owner memutuskan.</div>`}</span></div>`; })}</div>`; })()}
      ${(() => { const BT = bertahapTertunda(); return BT ? h`<div class="kartu awas" data-k="bertahap" style="gap: 6px;"><div style="font-weight: 700;">Kiriman bertahap belum selesai: ${BT.judul}</div><div class="k2">${BT.sudah} dari ${BT.total} kiriman sudah masuk (mulai ${waktuSetempat(BT.pada)}). Yang sudah masuk tidak dikirim ulang.</div>
        <div class="hg-pil"><div class="seg aktif" data-aksi="lanjutBertahap">lanjutkan</div><div class="seg ${s.yakinBuang === 'bertahap' ? 'aktif' : ''}" data-aksi="buangBertahap">${s.yakinBuang === 'bertahap' ? 'yakin buang sisanya' : 'buang sisanya'}</div></div></div>` : ''; })()}
      <div class="ket" data-k="ket-antre" style="font-size: 11px;">Batas "lama" ${P.atur.batasAntre} menit (Atur).</div>${pintuAtur('Atur batas antrean, denyut & pencatat', 'antrean lama ' + P.atur.batasAntre + ' menit · denyut lama ' + P.atur.batasDenyut + ' menit · ' + P.atur.pemegang.length + ' pencatat')}`;
    if (tab === 'jejak') { const J = S.ssJejak(d, L.antre, s.saring); return h`<div class="hg-pil" data-k="saring"><div class="seg ${!s.saring ? 'aktif' : ''}" data-aksi="saring" data-nama="">Semua</div>${J.perOrang.map((o) => h`<div class="seg ${s.saring === o.nama ? 'aktif' : ''}" data-aksi="saring" data-nama="${o.nama}">${o.nama}</div>`)}</div>
      <div class="kartu" data-k="jejak" style="gap: 2px;"><div class="label">${J.hariIni} catatan hari ini${s.saring ? ' · saring ' + s.saring : ''} · ${J.belumSampai} belum sampai</div>
        ${J.tampil.length ? J.tampil.map((l) => h`<div class="pr-jejak" data-k="l-${l.id}"><span class="j">${l.tanggal === hariIniIso(d) ? l.jam : tanggalPendek(l.tanggal)}</span><span>${l.teks}<div class="k2">${l.oleh} · ${l.perangkat}</div></span><span class="pr-cap ${l.sampai ? 'ok' : 'awas'}">${l.sampai ? 'sampai' : 'belum'}</span></div>`) : h`<div class="ket">Belum ada jejak yang terbaca${sumberData().jenis === 'cadangan' ? ' — cadangan sistem lama tidak memuat jejak' : ''}.</div>`}
        ${J.terbatas ? h`<div class="ket">Hanya ${J.batas} tulisan terakhir yang dibaca — bukan seluruh riwayat.</div>` : ''}</div>
      <div class="kartu" data-k="perorang" style="gap: 2px;"><div class="label">Per orang</div>${J.perOrang.map((o) => h`<div style="display: flex; justify-content: space-between; font-size: 12px; padding: 2px 0;" data-k="o-${o.nama}"><span>${o.nama}</span><span class="k2">${o.n} tulisan · hari ini ${o.hariIni}${o.belum ? ' · ' + o.belum + ' belum sampai' : ''}</span></div>`)}</div>
      ${pintuAtur('Atur batas antrean, denyut & pencatat', 'antrean lama ' + P.atur.batasAntre + ' menit · denyut lama ' + P.atur.batasDenyut + ' menit · ' + P.atur.pemegang.length + ' pencatat')}`; }
    return h`<div class="ket" data-k="ringkas" style="font-size: 11.5px;">${P.ringkas}</div>
      <div style="display: flex; flex-direction: column; gap: 6px;" data-k="kartu-p">${P.daftar.map((p) => h`<div class="pr-kartu ${pilih && pilih.id === p.id ? 'aktif' : ''} ${p.hidup ? '' : 'diam'}" data-k="p-${p.id}" data-aksi="pilihP" data-id="${p.id}">
        <div class="pr-kepala"><b><span class="pr-titik ${p.hidup ? '' : p.hariIni ? 'lama' : 'putus'}"></span>${p.nama}${p.ini ? ' · perangkat ini' : ''}</b><span class="pr-n ${p.antrean || p.ditolak ? '' : 'k2'}">${p.antrean ? p.antrean + ' belum sampai' : 'semua sampai'}${p.ditolak ? ' · ' + p.ditolak + ' ditolak server' : ''}</span></div>
        <div class="k2">${p.aplikasi}${p.versi && p.versi !== 'baru' ? ' · ' + p.versi : ''}${p.pemegang ? ' · dipegang ' + p.pemegang : ''}${p.lokasi ? ' · di ' + ((S.ssLokasi().daftar.find((l) => l.id === p.lokasi) || {}).nama || p.lokasi) : ''}</div><div class="k2">${p.denyutTeks}${p.akun ? ' · ' + p.akun : ''}</div></div>`)}
      ${!P.daftar.length ? h`<div class="ket">Denyut ditulis tiap perangkat yang masuk (sistem baru & kasir darurat) paling cepat sekali per menit. Kalau daftar ini kosong padahal HP sedang dipakai, aturan Firestore untuk koleksi perangkatStatus belum terpasang.</div>` : ''}</div>
      ${pilih && pilih.ini ? h`<div class="kartu" data-k="panel-ini" style="gap: 6px;"><div style="font-weight: 700;">Perangkat ini</div>
        <div class="label">Nama perangkat ini</div><div style="display: flex; gap: 6px;"><input class="ketik-nama" type="text" placeholder="${L.namaPerangkat || 'mis. iPhone owner, Mac toko'}" value="${s.namaBaru || ''}" data-ketik="namaiPerangkat"><div class="kaca-btn aktif" style="min-width: 84px;" data-aksi="namaiSimpan">simpan</div></div>
        <div class="label">Yang mencatat di perangkat ini</div><div class="pita-info" data-k="masuk-sebagai">Masuk sebagai: <b>${(() => { const a = opsi.akun ? opsi.akun() : null; return a ? (a.jenis === 'owner' ? 'Owner' : a.nama + ' (' + ((S.SS_PERAN.find((p) => p.id === a.peran) || {}).nama || a.peran) + ')') : 'Owner'; })()}</b></div>
        <div class="k2">Catatan membawa nama & uid akun yang MASUK — bukan pilihan di perangkat. Ganti orang = Keluar lalu masuk dengan akunnya sendiri (tombol Keluar di pojok atas).</div></div>` : pilih ? h`<div class="kartu" data-k="panel-lain" style="gap: 4px;"><div style="font-weight: 700;">${pilih.nama}</div><div class="k2">${pilih.denyutTeks} · ${pilih.aplikasi}</div><div class="k2">Antrean & pemegang perangkat lain hanya bisa diubah dari perangkat itu sendiri.</div></div>` : ''}
      ${gambarNotifHp(s)}
      ${gambarLancar(s)}
      ${pintuAtur('Atur batas antrean, denyut & pencatat', 'antrean lama ' + P.atur.batasAntre + ' menit · denyut lama ' + P.atur.batasDenyut + ' menit · ' + P.atur.pemegang.length + ' pencatat')}`;
  }
  // owner 21 Nov 2026: notifikasi HP / Mac owner saat aplikasi tertutup (push lewat fungsi server functions/ — dipasang owner sekali di Cloud Shell)
  function gambarNotifHp(s) {
    if (ntAplikasi()) return h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}`;   // owner 23 Nov 2026: aplikasi tablet = push Android, bukan push peramban
    const a = opsi.akun ? opsi.akun() : null; if (a && a.jenis !== 'owner') return '';
    const D = nhDukung(); const T = nhTersimpan(); const izin = nhIzin(); const kunci = vapidToko();
    const status = !D.ok ? D.sebab : T && izin === 'granted' ? 'MENYALA di perangkat ini sejak ' + waktuSetempat(T.pada) : izin === 'denied' ? 'Izin notifikasi DITOLAK di perangkat ini — izinkan dulu di setelan peramban / iPhone' : 'Belum menyala di perangkat ini';
    return h`<div class="kartu" data-k="notif-hp" style="gap: 6px;"><div style="font-weight: 700;">Notifikasi di perangkat ini</div>
      <div class="k2">Titipan uang keluar, pesan, dan permintaan lain dari tablet muncul di HP / Mac ini walau aplikasinya tertutup.</div>
      <div class="pita-info ${T && izin === 'granted' ? 'emas' : D.ok ? '' : 'awas'}" data-k="nh-status">${status}</div>
      ${kunci ? '' : h`<div class="label">Kunci notifikasi proyek (sekali saja)</div><div style="display: flex; gap: 6px;"><input class="ketik-nama" type="text" placeholder="kunci publik web push (diawali B…)" value="${s.nhVapid}" data-ketik="nhKetik"><div class="kaca-btn" data-aksi="nhSimpanKunci">Simpan</div></div>
        <div class="k2">Console Firebase › Project settings › Cloud Messaging › Web Push certificates › Generate key pair, lalu salin "Key pair"-nya ke sini.</div>`}
      ${D.ok ? h`<div class="tombol-baris rapat">${T && izin === 'granted' ? h`<div class="kaca-btn" data-aksi="nhNyala">${s.nhSibuk ? 'menunggu…' : 'Perbarui'}</div><div class="kaca-btn putus" data-aksi="nhMati">Matikan</div>` : h`<div class="kaca-btn aktif emas ${kunci ? '' : 'mati'}" data-aksi="nhNyala">${s.nhSibuk ? 'menunggu…' : 'Nyalakan notifikasi'}</div>`}</div>` : ''}
      <div class="k2" style="font-size: 11px;">Butuh fungsi server notifikasi terpasang (sekali, oleh owner — docs/notifikasi-hp.md). Isi notifikasi lewat layanan push Google / Apple.</div></div>`;
  }
  // owner 23 Nov 2026 ("di aplikasi tablet belum bisa"): push lewat Google untuk aplikasi tablet — semua akun yang masuk di tablet (owner yang jaga juga).
  // Kartu perangkat (pushSiap, layarPenuh) ditanya ke aplikasi sekali per layar.
  let _ntInfoMinta = false;   // ditanya sekali; jawabannya datang SESUDAH gambar ini (tidak menulis keadaan di tengah menggambar)
  function mintaInfoTablet() { if (_ntInfoMinta) return; _ntInfoMinta = true; infoPerangkat().then((i) => set({ ntInfo: i || {} })).catch(() => set({ ntInfo: { gagal: true } })); }
  function gambarNotifTablet(s) {
    mintaInfoTablet();
    const a = opsi.akun ? opsi.akun() : null; const D = ntDukung(s.ntInfo || {}); const T = ntTersimpan(a && a.uid ? a.uid : '');
    const status = !D.ok ? D.sebab : T ? 'MENYALA di tablet ini sejak ' + waktuSetempat(T.pada) : 'Belum menyala di tablet ini';
    return h`<div class="kartu" data-k="notif-tablet" style="gap: 6px;"><div style="font-weight: 700;">Notifikasi di tablet ini</div>
      <div class="k2">Jawaban owner atas titipan, pesan, dan permintaan dari tablet ini (disetujui, ditolak, balasan) muncul di bilah notifikasi tablet walau aplikasinya ditutup. Saat aplikasi terbuka kabarnya tetap lewat pita & lonceng.</div>
      <div class="pita-info ${T && D.ok ? 'emas' : D.ok ? '' : 'awas'}" data-k="nt-status">${status}</div>
      ${D.ok ? h`<div class="tombol-baris rapat">${T ? h`<div class="kaca-btn" data-aksi="ntNyala">${s.ntSibuk ? 'menunggu…' : 'Perbarui'}</div><div class="kaca-btn putus" data-aksi="ntMati">Matikan</div>` : h`<div class="kaca-btn aktif emas" data-aksi="ntNyala">${s.ntSibuk ? 'menunggu…' : 'Nyalakan notifikasi tablet'}</div>`}</div>` : ''}
      <div class="k2" style="font-size: 11px;">Butuh rules v17 terbit & fungsi server kabarTablet terpasang (sekali, oleh owner — docs/notifikasi-tablet.md). Isi notifikasi lewat layanan push Google.</div></div>`;
  }
  function gambarLayarPenuh(s) {
    const ada = layarPenuhAda(); const nyala = !!(s.ntInfo && s.ntInfo.layarPenuh);
    return h`<div class="kartu" data-k="layar-penuh" style="gap: 6px;"><div style="font-weight: 700;">Layar penuh</div>
      <div class="k2">Bilah jam/baterai dan tombol kembali/beranda Android disembunyikan, rak & keranjang memakai seluruh layar. Geser dari tepi bawah (atau atas) layar = tombol Android muncul sebentar lalu hilang lagi. Menu bawah bisa dilipat lewat pegangan kecil di atasnya.</div>
      ${ada === false ? h`<div class="pita-info awas" data-k="lp-status">APK di tablet ini belum bisa layar penuh — pasang APK terbaru (docs/notifikasi-tablet.md)</div>`
        : h`<div class="pita-info ${nyala ? 'emas' : ''}" data-k="lp-status">${nyala ? 'MENYALA di tablet ini' : 'Mati — bilah jam & tombol Android tampil'}</div>
      <div class="tombol-baris rapat">${nyala ? h`<div class="kaca-btn putus" data-aksi="lpSetel" data-n="0">${s.lpSibuk ? 'menunggu…' : 'Matikan layar penuh'}</div>` : h`<div class="kaca-btn aktif emas" data-aksi="lpSetel" data-n="1">${s.lpSibuk ? 'menunggu…' : 'Nyalakan layar penuh'}</div>`}</div>`}</div>`;
  }
  function gambarPeran(s, d, tab) {
    const P = S.ssPeran();
    if (tab === 'tablet') return gambarTablet(s);
    if (tab === 'minta') { const Q = S.ssPersetujuan(d); const m = Q.menunggu.find((x) => x.id === s.mintaKe) || null; return h`<div class="ket" data-k="judul-minta" style="font-size: 11.5px;">${Q.judul}</div>
      <div style="display: flex; flex-direction: column; gap: 6px;" data-k="minta">${Q.menunggu.map((x) => h`<div class="pn-minta ${m && m.id === x.id ? 'aktif' : ''}" data-k="m-${x.id}" data-aksi="mintaKe" data-id="${x.id}"><div style="display: flex; justify-content: space-between; gap: 8px;"><b style="font-size: 12.5px;">${x.dari} · ${x.jam}</b><span class="n">${x.n ? RP(x.n) : ''}</span></div><div style="font-size: 12px;">${x.teks}</div><div class="k2">${x.modul} · ${x.namaTindakan}</div></div>`)}</div>
      ${m ? h`<div class="kartu" data-k="putus" style="gap: 6px;"><div class="k2">${m.saran}</div><input class="ketik-nama" type="text" placeholder="Alasan kalau menolak (wajib)" value="${s.alasan}" data-ketik="alasan"><div class="pn-dua"><div class="kaca-btn aktif emas" data-aksi="setujui">SETUJUI</div><div class="kaca-btn awas" data-aksi="tolak">tolak</div></div></div>` : ''}
      ${Q.menunggu.length ? h`<div class="kaca-btn" data-k="kecil" data-aksi="setujuiKecil">setujui semua yang kecil (≤ ${RP(Q.batas)}) · ${Q.kecil}</div>` : ''}
      ${Q.riwayat.length ? h`<div class="kartu" data-k="riwayat" style="gap: 2px;"><div class="label">Keputusan sebelumnya</div>${Q.riwayat.map((x) => h`<div class="k2" data-k="r-${x.id}">${tanggalPendek(x.diputusTanggal)} · ${x.status.toUpperCase()}: ${x.teks} (${x.dari})${x.alasanTolak ? ' · ' + x.alasanTolak : ''}</div>`)}</div>` : ''}
      ${pintuAtur('Atur batas setujui sekaligus & jatah nego', 'sekaligus ≤ ' + RP(P.batasSekaligus) + ' · jatah nego Ben ' + P.jatahBen + '% · karyawan ' + P.jatahKaryawan + '% margin')}`; }
    const PR = S.SS_PERAN.find((p) => p.id === s.peran) || S.SS_PERAN[1];
    const A = S.ssAkun(); const ownerKini = !opsi.akun || !opsi.akun() || opsi.akun().jenis === 'owner';
    const kartuAkun = !ownerKini ? '' : h`<div class="kartu" data-k="minta-akses" style="gap: 6px;"><div class="label">Permintaan akses · ${A.minta.length}</div>
        ${A.minta.length ? A.minta.map((m) => h`<div class="pn-minta" data-k="ma-${m.uid}"><b style="font-size: 12.5px;">${m.nama || '(tanpa nama)'}</b> <span class="k2">${m.email} · ${waktuSetempat(m.pada)}</span>
          <div class="hg-pil">${S.SS_PERAN_AKUN.map((p) => h`<div class="seg ${s.akunPilih[m.uid] === p.id ? 'aktif' : ''}" data-aksi="akunPilihPeran" data-uid="${m.uid}" data-peran="${p.id}">${p.nama}</div>`)}</div>
          <div class="pn-dua"><div class="kaca-btn aktif emas" data-aksi="daftarkan" data-uid="${m.uid}">DAFTARKAN</div><div class="kaca-btn awas" data-aksi="tolakAkses" data-uid="${m.uid}">TOLAK</div></div></div>`) : h`<div class="k2">Tidak ada. Orang baru masuk dengan akun yang lu buat di Firebase Console, lalu menekan "Minta didaftarkan".</div>`}
        ${A.minta.length ? h`<input class="ketik-nama" type="text" placeholder="Alasan kalau menolak (wajib)" value="${s.alasanAkses}" data-ketik="alasanAkses">` : ''}</div>
      <div class="kartu" data-k="akun-terdaftar" style="gap: 6px;"><div class="label">Akun terdaftar</div>
        <div class="pn-orang" data-k="ak-owner"><b>Owner</b><div class="k2">dikenali lewat email owner · semua boleh · tidak diubah dari sini</div></div>
        ${A.akun.map((a) => h`<div class="pn-orang ${a.aktif ? '' : 'diam'}" data-k="ak-${a.uid}"><b>${a.nama || a.email}</b> <span class="k2">${a.email} · ${a.namaPeran} · ${a.aktif ? 'aktif' : 'NONAKTIF'}</span>
          <div class="hg-pil">${S.SS_PERAN_AKUN.map((p) => h`<div class="seg ${a.peran === p.id ? 'aktif' : ''}" data-aksi="ubahPeranAkun" data-uid="${a.uid}" data-peran="${p.id}">${p.nama}</div>`)}
            <div class="seg ${s.yakinAkun === a.uid + ':' + (a.aktif ? '0' : '1') ? 'aktif' : ''}" data-aksi="saklarAkun" data-uid="${a.uid}" data-aktif="${a.aktif ? '0' : '1'}">${a.aktif ? 'nonaktifkan' : 'aktifkan'}</div></div></div>`)}</div>`;
    return h`<div class="pita-info" data-k="kalimat-server">${S.SS_KALIMAT_SERVER}</div>${kartuAkun}<div style="display: flex; flex-direction: column; gap: 6px;" data-k="peran">${P.peran.map((p) => h`<div class="pn-orang ${PR.id === p.id ? 'aktif' : ''}" data-k="pr-${p.id}" data-aksi="peran" data-id="${p.id}"><b>${p.nama}</b><div class="k2">${p.ket}</div></div>`)}</div>
      <div class="kartu" data-k="hak" style="gap: 0;"><div class="label" style="padding-top: 2px;">Hak ${PR.nama} — ketuk untuk memutar</div>
        ${P.tindakan.map((t) => { const x = P.tampil(PR.id, t.id); return h`<div class="pn-hak" data-k="h-${t.id}" data-aksi="putarHak" data-peran="${PR.id}" data-t="${t.id}"><div><div style="font-weight: 600;">${t.nama}</div><div class="k2">${t.modul}${x.ket ? ' · ' + x.ket : ''}</div></div><span class="pn-nilai ${x.nilai} ${PR.id === 'owner' ? 'kunci' : ''}">${x.label}</span></div>`; })}</div>
      ${P.jejak.length ? h`<div class="kartu" data-k="jejak-hak" style="gap: 2px;"><div class="label">Perubahan hak terakhir</div>${P.jejak.map((j, i) => h`<div class="k2" data-k="jh-${i}">${tanggalPendek(j.tanggal)} ${j.jam} · ${j.teks}</div>`)}</div>` : ''}
      <div class="ket" data-k="ket-peran" style="font-size: 11px;">Tiga peran: owner (semua), penjaga laci, karyawan. "Tidak boleh" = tombolnya mati di tablet; "minta owner" = masuk papan persetujuan (alurnya belum ada, jadi sekarang tertutup); menolak wajib alasan. "Tertutup server" = di kisi lu bilang boleh, tapi aturan server (firestore.rules) belum membukanya untuk peran itu — sebabnya tertulis di bawah nama tindakan.</div>
      ${pintuAtur('Atur batas setujui sekaligus & jatah nego', 'sekaligus ≤ ' + RP(P.batasSekaligus) + ' · jatah nego Ben ' + P.jatahBen + '% · karyawan ' + P.jatahKaryawan + '% margin')}`;
  }
  // T1-3 (owner 16 Nov 2026): satu akun tablet + PIN per orang. Owner saja yang mengatur; akun tablet = akun staf yang didaftarkan di tab Peran & hak.
  function gambarTablet(s) {
    const a = opsi.akun ? opsi.akun() : null; if (a && a.jenis !== 'owner') return h`<div class="kartu" data-k="tb-staf"><div class="ket">Hanya owner yang mengatur orang di tablet.</div></div>`;
    const D = TB.tbDaftar(); const t = s.tb; const pinIn = (kolom, nilai, ketik, ph) => h`<input class="ketik-nama" type="password" inputmode="numeric" autocomplete="off" maxlength="6" placeholder="${ph}" value="${nilai}" data-ketik="${ketik}" data-kolom="${kolom}">`;
    return h`<div class="pita-info" data-k="tb-cara">Tablet kasir masuk dengan SATU akun staf (didaftarkan di tab Peran & hak, peran Penjaga laci). Begitu daftar di bawah berisi, akun itu menampilkan "Siapa yang jaga?" — tiap orang mengetuk namanya lalu memasukkan PIN. Nota & catatan tersimpan atas nama orang yang jaga. Salah PIN ${TB.TB_BATAS_SALAH} kali = nama itu terkunci ${TB.TB_LAMA_KUNCI_MS / 60000} menit; tidak disentuh ${TB.TB_LAMA_DIAM_MS / 60000} menit = kembali ke "Siapa yang jaga?".</div>
      <div class="kartu" data-k="tb-daftar" style="gap: 6px;"><div class="label">Orang di tablet · ${D.length}</div>
        ${D.length ? D.map((o) => h`<div class="pn-orang ${o.aktif ? '' : 'diam'}" data-k="tb-${o.id}"><b>${o.nama}</b> <span class="k2">${o.namaPeran} · ${o.aktif ? 'aktif' : 'LIBUR'}${o.diubah ? ' · diubah ' + waktuSetempat(o.diubah) : ''}</span>
          <div class="hg-pil">${TB.TB_PERAN.map((p) => h`<div class="seg ${o.peran === p.id ? 'aktif' : ''}" data-aksi="tbPeranUbah" data-id="${o.id}" data-peran="${p.id}">${p.nama}</div>`)}
            <div class="seg ${s.tbGanti === o.id ? 'aktif' : ''}" data-aksi="tbGanti" data-id="${o.id}">ganti PIN</div>
            <div class="seg" data-aksi="tbAktif" data-id="${o.id}" data-aktif="${o.aktif ? '0' : '1'}">${o.aktif ? 'liburkan' : 'aktifkan'}</div>
            <div class="seg ${s.yakinTb === o.id ? 'aktif' : ''}" data-aksi="tbHapus" data-id="${o.id}">${s.yakinTb === o.id ? 'YAKIN — HAPUS' : 'hapus'}</div></div>
          ${s.tbGanti === o.id ? h`<div class="kartu" data-k="tb-ganti-${o.id}" style="gap: 6px;"><div class="k2">PIN baru ${o.nama} (4–6 angka)</div>${pinIn('pin', s.tbPinBaru.pin, 'tbPinIsi', 'PIN baru')}${pinIn('pin2', s.tbPinBaru.pin2, 'tbPinIsi', 'ulangi PIN baru')}
            <div class="kaca-btn aktif" data-aksi="tbGantiSimpan">${s.tbSibuk ? 'menyimpan…' : 'SIMPAN PIN BARU'}</div></div>` : ''}</div>`)
        : h`<div class="k2">Belum ada. Selama kosong, akun tablet bekerja seperti akun staf biasa (tanpa PIN).</div>`}</div>
      ${gambarRingkasOwner(s, D)}
      <div class="kartu" data-k="tb-tambah" style="gap: 6px;"><div class="label">Tambah orang</div>
        <input class="ketik-nama" type="text" placeholder="Nama (tampil di tablet & di nota)" value="${t.nama}" data-ketik="tbIsi" data-kolom="nama" maxlength="30" autocomplete="off">
        <div class="hg-pil">${TB.TB_PERAN.map((p) => h`<div class="seg ${t.peran === p.id ? 'aktif' : ''}" data-aksi="tbPeran" data-peran="${p.id}">${p.nama}</div>`)}</div>
        ${pinIn('pin', t.pin, 'tbIsi', 'PIN 4–6 angka')}${pinIn('pin2', t.pin2, 'tbIsi', 'ulangi PIN')}
        <div class="kaca-btn aktif emas" data-aksi="tbTambah">${s.tbSibuk ? 'menyimpan…' : 'TAMBAH'}</div>
        <div class="k2">PIN tidak disimpan apa adanya — yang tersimpan hanya sidik acaknya. Owner juga bisa dimasukkan sebagai orang di tablet untuk jualan (urusan owner tetap di HP/Mac owner). Hak tiap orang = kisi perannya di tab Peran & hak, tidak pernah melebihi peran akun tablet.</div></div>`;
  }
  // owner 21 Nov 2026: Ringkas hari ini di tablet — siapa yang membukanya (SATU orang di daftar tablet) + akun tablet mana yang membaca data uang (rules v14)
  function gambarRingkasOwner(s, D) {
    const pilih = RT.rtOrang(); const akunBen = S.ssAkun().akun.filter((a) => a.peran === 'ben');
    const op = D.find((o) => o.id === pilih); const adaTanda = akunBen.some((a) => a.bacaUang);
    return h`<div class="kartu" data-k="rt-owner" style="gap: 6px;"><div class="label">Ringkas hari ini di tablet</div>
      <div class="k2">Kartu paling atas Menu tablet: omzet, tunai / QRIS / bon, perkiraan isi laci, uang keluar, per orang, terlaris, stok tipis, pesanan & antar — bisa dicetak. Tampil HANYA saat orang yang lu pilih jaga (lewat PIN-nya).</div>
      <div class="k2" style="font-weight: 600;">Dibuka oleh</div>
      <div class="hg-pil" data-k="rt-orang"><div class="seg ${pilih ? '' : 'aktif'}" data-aksi="rtPilihOrang" data-id="-">mati</div>${D.map((o) => h`<div class="seg ${pilih === o.id ? 'aktif' : ''}" data-aksi="rtPilihOrang" data-id="${o.id}">${o.nama}</div>`)}</div>
      <div class="k2" style="font-weight: 600;">Sidik jari owner di tablet (orang ini, jari owner saja) · intip uang tertutup sendiri sesudah tidak disentuh</div>
      <div class="hg-pil" data-k="rt-intip">${[30, 60, 120, 300].map((d) => h`<div class="seg ${SJ.sjIntipDetik() === d ? 'aktif' : ''}" data-aksi="rtIntip" data-d="${d}">${d < 60 ? d + ' dtk' : d / 60 + ' mnt'}</div>`)}</div>
      <div class="k2">Sidik jari dinyalakan DI TABLET oleh orang ini sesudah masuk dengan PIN (Menu tablet › Sidik jari owner). Hanya menyala bila penanda jari baru terpasang: ada jari baru didaftarkan di Setelan tablet = mati sendiri + lu dikabari.</div>
      <div class="k2" style="font-weight: 600;">Akun tablet yang membaca data uang (laci & uang keluar)</div>
      ${akunBen.length ? akunBen.map((a) => h`<div class="pn-orang" data-k="rt-ak-${a.uid}"><b>Akun tablet</b> <span class="k2">${a.email} · ${a.bacaUang ? 'MEMBACA data uang' : 'tidak membaca data uang'}</span>
        <div class="hg-pil"><div class="seg ${a.bacaUang ? 'aktif' : ''} ${s.yakinRt === a.uid + ':1' ? 'aktif' : ''}" data-aksi="rtBacaUang" data-uid="${a.uid}" data-nyala="1">${s.yakinRt === a.uid + ':1' ? 'YAKIN — buka data uang' : 'baca data uang'}</div>
          <div class="seg ${a.bacaUang ? '' : 'aktif'}" data-aksi="rtBacaUang" data-uid="${a.uid}" data-nyala="0">tidak</div></div></div>`) : h`<div class="k2">Belum ada akun Penjaga laci terdaftar.</div>`}
      <div class="pita-info ${pilih && adaTanda ? 'emas' : ''}" data-k="rt-status">${!pilih ? 'Mati — tidak ada kartu Ringkas di tablet.' : !adaTanda ? 'Kartu tampil untuk ' + (op ? op.nama : 'orang terpilih') + ', tapi laci & uang keluar tidak dihitung sampai akun tablet ditandai membaca data uang.' : 'Kartu tampil untuk ' + (op ? op.nama : 'orang terpilih') + ' dengan laci & uang keluar. Data uang dimuat ke tablet hanya selama ' + (op ? op.nama : 'orang itu') + ' jaga, dan dibuang dari layar begitu orang lain jaga.'} Butuh aturan server v14 (docs/uji-rules-v14.md).</div></div>`;
  }
  function gambarCadangan(s, d) {
    const C = S.ssCadangan(d, lokal(), s.hariC);
    return h`<div class="kartu" data-k="kuota" style="gap: 6px;"><div class="label">Simpanan lokal di perangkat ini</div>
        ${C.kuota.adaAngka ? h`<div class="cd-bar ${C.kuota.awas ? 'awas' : ''}"><div style="width: ${Math.min(100, C.kuota.pct)}%;"></div></div>` : ''}<div class="k2">${C.kuota.teks}${C.kuota.ket ? ' · ' + C.kuota.ket : ''}</div>${C.kuota.awasTeks ? h`<div class="pita-info ${C.kuota.awas ? 'awas' : ''}" style="font-size: 11.5px;">${C.kuota.awasTeks}</div>` : ''}
        ${C.simpanan.adaAngka ? h`<div class="k2">Simpanan Firestore di perangkat (IndexedDB): ${ANGKA(C.simpanan.kb)} KB${C.simpanan.quotaKb ? ' dari jatah peramban ' + ANGKA(Math.round(C.simpanan.quotaKb / 1024)) + ' MB (' + C.simpanan.pct + '%)' : ''} — dibersihkan Firestore sendiri, tidak perlu dirapikan.</div>` : ''}
        <div class="cd-angka">${C.sehat.map((x) => h`<div data-k="s-${x.t}">${x.t}<b>${x.n}</b></div>`)}</div></div>
      ${(() => { const LM = s.lamaInfo;
        if (!LM) return h`<div class="k2" data-k="sisa-lama-belum">Sisa simpanan sistem lama belum dihitung — dihitung saat lembar ini dibuka.</div>`;
        if (LM.takTerbaca) return h`<div class="k2" data-k="sisa-lama-tak-terbaca">Sisa simpanan sistem lama tidak bisa dibaca di peramban ini — belum tentu kosong.</div>`;
        return LM.ada.length ? h`<div class="kartu" data-k="sisa-lama" style="gap: 6px;"><div class="label">Sisa sistem lama di perangkat ini · ${LM.ada.length} simpanan · ${LM.kb < 0.5 ? 'kurang dari 1' : '±' + ANGKA(Math.round(LM.kb))} KB</div><div class="k2">${LM.teks}</div>
        ${LM.dijaga.length ? h`<div class="pita-info awas" data-k="lama-dijaga">Antrean lama masih berisi ${LM.nCatatan} catatan yang tidak pernah sampai server — tidak ikut dibersihkan sampai salinannya diunduh dan berkasnya dinyatakan tersimpan.</div>` : ''}
        <div class="pn-dua"><div class="kaca-btn" data-aksi="lamaUnduh">${s.lamaBerkas ? 'unduh lagi' : 'unduh salinannya'}</div><div class="kaca-btn awas" data-aksi="lamaBersih">${s.yakinBuang === 'lama' ? 'YAKIN — BERSIHKAN' : 'BERSIHKAN · ' + LM.dibersihkan.length}</div></div>
        ${s.lamaBerkas && !s.lamaDiunduh && LM.dijaga.length ? h`<div class="pita-info" data-k="lama-periksa">Buka Unduhan/Files dan pastikan berkas ${s.lamaBerkas} ada — isinya satu-satunya salinan ${LM.nCatatan} catatan itu. Unduhan bisa batal diam-diam (terutama di iPhone/iPad).</div>
          <div class="kaca-btn aktif emas" data-aksi="lamaTersimpan" data-k="lama-tersimpan">berkasnya sudah tersimpan</div>` : ''}
        ${s.lamaDiunduh ? h`<div class="k2" data-k="lama-dinyatakan">Berkas ${s.lamaBerkas} dinyatakan tersimpan — antrean lama yang berisi ikut dibersihkan.</div>` : ''}</div>`
        : h`<div class="k2" data-k="sisa-lama-kosong">Tidak ada sisa simpanan sistem lama di perangkat ini.</div>`; })()}
      <div class="ket" data-k="ringkas-c" style="font-size: 11.5px;">${C.ringkas}</div>
      <div class="utama" data-k="unduh" data-aksi="unduhCadangan">UNDUH CADANGAN SEKARANG</div>
      <div class="ket" data-k="ket-unduh" style="font-size: 11px;">Berkas JSON yang sama bentuknya dengan cadangan sistem lama (versi 5) + koleksi sistem baru, bercap era tutup buku${C.era ? ' (tahun ' + C.era + ')' : ' (belum pernah tutup buku)'}. Yang diunduh adalah salinan di perangkat ini — kalau ada catatan yang belum sampai server, isinya tetap ikut.</div>
      <div class="kartu" data-k="kal" style="gap: 6px; padding: 10px 12px;"><div class="cd-kal">${C.kalender.map((k) => h`<div class="cd-hari ${k.aktif ? 'aktif' : ''} ${k.ini ? 'ini' : ''}" data-k="k-${k.iso}" data-aksi="hariC" data-iso="${k.iso}"><span class="nm">${k.nm}</span><b>${k.tgl}</b><span class="t ${k.keadaan}"></span></div>`)}</div><div class="k2">● emas = ada cadangan hari itu · kosong = tidak ada</div></div>
      <div class="kartu" data-k="hari-c" style="gap: 2px;"><div class="label">${C.hariJudul}</div>${C.hariDaftar.map((c) => h`<div class="cd-baris" data-k="c-${c.id}"><div><div style="font-weight: 600;">${c.jam ? c.jam + ' · ' : ''}${c.nama}</div><div class="k2">${c.sumber}${c.perangkat ? ' · ' + c.perangkat : ''}${c.kb ? ' · ' + ANGKA(c.kb) + ' KB · ' + ANGKA(c.dokumen) + ' catatan' : ''}</div></div><span class="cd-cap ${c.ok ? 'ok' : 'awas'}">${c.jenis}</span></div>`)}</div>
      <div class="ket" data-k="ket-c" style="font-size: 11px;">Sistem baru tidak memakai cadangan localStorage; jalan tanpa internet ditanggung simpanan Firestore.${lamaAda() && lamaAda().ada.length ? ' Angka kuota di atas sebagian masih dipakai salinan lama dari sistem yang sudah pensiun (3 Okt 2026) — bersihkan di kartu "Sisa sistem lama".' : ''} Memulihkan data dari berkas cadangan dikerjakan di komputer, bukan di situs ini — langkahnya tertulis di catatan "Prosedur pulih darurat" yang disimpan bersama kode aplikasi toko di GitHub; unduh cadangan dua kali.</div>
      ${pintuAtur('Atur jadwal cadangan, masa simpan & ambang kuota', 'tiap ' + C.atur.cadanganTiap + ' hari · simpan ' + C.atur.simpanHari + ' hari · ambang ' + C.atur.ambangKuota + '%')}`;
  }
  function gambarLokasi(s, d, tab) {
    const LK = S.ssLokasi(); const L = lokal(); const lapor = S.ssLaporLokasi(d);
    if (tab === 'pindah') { const p = s.pindah; const stok = S.ssStokLokasi(); const merek = Object.keys(stok).sort(); const dari = p.dari || LK.utama.id; const ke = p.ke || ((LK.daftar.find((l) => l.id !== dari) || {}).id || '');
      return h`<div class="kartu" data-k="pindah" style="gap: 6px;"><div class="label">Pindah stok antarlokasi</div>
        ${LK.daftar.length < 2 ? h`<div class="pita-info awas">Belum ada lokasi lain — tambahkan di Atur. Sampai itu, pindah stok tidak bisa dicatat.</div>` : ''}
        <div class="hg-pil">${merek.map((m) => h`<div class="seg ${p.merk === m ? 'aktif' : ''}" data-aksi="pindahPilih" data-kolom="merk" data-nilai="${m}">${m} · ${ANGKA(Math.round(Object.keys(stok[m]).reduce((a, k) => a + stok[m][k], 0)))} kg</div>`)}</div>
        <div class="lk-panah"><div class="sisi"><div class="label">dari</div>${LK.daftar.map((l) => h`<div class="seg ${dari === l.id ? 'aktif' : ''}" data-aksi="pindahPilih" data-kolom="dari" data-nilai="${l.id}">${l.nama}${p.merk ? ' · ' + ANGKA(Math.round((stok[p.merk] || {})[l.id] || 0)) + ' kg' : ''}</div>`)}</div><span style="text-align: center; font-size: 18px;">→</span><div class="sisi"><div class="label">ke</div>${LK.daftar.filter((l) => l.id !== dari).map((l) => h`<div class="seg ${ke === l.id ? 'aktif' : ''}" data-aksi="pindahPilih" data-kolom="ke" data-nilai="${l.id}">${l.nama}</div>`)}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><input class="ketik-nama" type="text" inputmode="decimal" placeholder="berapa kg" value="${p.kg}" data-ketik="pindahIsi" data-kolom="kg"><span class="k2">kg</span></div>
        <div class="label">Diantar oleh</div><div class="hg-pil">${LK.pengantar.map((n) => h`<div class="seg ${p.pengantar === n ? 'aktif' : ''}" data-aksi="pindahPilih" data-kolom="pengantar" data-nilai="${n}">${n}</div>`)}</div>
        <div class="utama ${LK.daftar.length < 2 ? 'mati' : ''}" data-aksi="pindahSimpan">PINDAHKAN${p.merk && p.kg ? ' ' + p.kg + ' kg ' + p.merk : ''}</div>
        <div class="k2">Dua catatan (KELUAR dari asal, MASUK ke tujuan), bukan penjualan: buku toko & modal tetap; pengantarnya tercatat.</div></div>`; }
    if (tab === 'lapor') return h`<div class="ket" data-k="ket-lapor" style="font-size: 11.5px;">${lapor.ket}</div>${lapor.lapor.map((l) => h`<div class="kartu" data-k="lp-${l.id}" style="gap: 6px;"><div style="font-weight: 700;">${l.nama}${l.utama ? ' · utama' : ''}</div>
        <div class="lk-lapor"><div>stok<b>${l.kg ? ANGKA(Math.round(l.kg)) + ' kg' : '—'}</b></div><div>nilai rak<b>${l.kg ? RP(l.nilai) : '—'}</b></div><div>omzet hari ini<b>${l.notaHari || l.omzetHari ? RP(l.omzetHari) : 'belum ada'}</b></div><div>nota hari ini<b>${l.notaHari}</b></div><div>omzet bulan ini<b>${l.notaBulan || l.omzetBulan ? RP(l.omzetBulan) : 'belum ada'}</b></div><div>perangkat<b>${l.perangkat.length ? l.perangkat.join(', ') : '—'}</b></div></div>
        ${l.merek.slice(0, 8).map((m) => h`<div style="display: flex; justify-content: space-between; font-size: 12px;" data-k="lm-${m.nama}"><span>${m.nama}</span><span class="k2">${ANGKA(Math.round(m.kg))} kg</span></div>`)}${l.kosong ? h`<div class="k2">belum ada catatan di lokasi ini</div>` : ''}</div>`)}`;
    const pilih = LK.daftar.find((l) => l.id === s.lokasiPilih) || LK.utama;
    return h`<div style="display: flex; flex-direction: column; gap: 6px;" data-k="kartu-l">${LK.daftar.map((l) => { const lp = lapor.lapor.find((x) => x.id === l.id) || {}; return h`<div class="lk-kartu ${pilih.id === l.id ? 'aktif' : ''}" data-k="l-${l.id}" data-aksi="lokasiPilih" data-id="${l.id}"><b>${l.nama}${l.utama ? h`<span class="lk-cap">utama</span>` : ''}${(L.lokasi || LK.utama.id) === l.id ? h`<span class="lk-cap">perangkat ini</span>` : ''}</b><div class="k2">${l.alamat || 'alamat belum diisi (Atur)'}</div><div class="k2">${lp.kg ? ANGKA(Math.round(lp.kg)) + ' kg · ' + RP(lp.nilai) : 'belum ada stok'} · ${lp.perangkat && lp.perangkat.length ? lp.perangkat.join(', ') : 'tidak ada perangkat berdenyut di sini'}</div></div>`; })}</div>
      <div class="kartu" data-k="panel-l" style="gap: 6px;"><div style="font-weight: 700;">${pilih.nama}</div>
        <div class="kaca-btn ${(L.lokasi || LK.utama.id) === pilih.id ? 'aktif' : ''}" data-aksi="lokasiIni" data-id="${pilih.id}">${(L.lokasi || LK.utama.id) === pilih.id ? 'perangkat ini mencatat di sini' : 'perangkat ini mencatat di sini →'}</div>
        <div class="kaca-btn ${pilih.utama ? 'mati' : 'aktif'}" data-aksi="jadikanUtama" data-id="${pilih.id}">${pilih.utama ? 'lokasi utama' : 'jadikan lokasi utama'}</div>
        <div class="k2">Fondasi: tiap catatan membawa lokasi perangkat yang mencatatnya (kolom lokasi). Catatan lama tanpa kolom itu dihitung di lokasi utama. Mesin stok & laba belum memisahkan per lokasi — laporan per lokasi membaca kolom itu.</div></div>
      ${pintuAtur('Atur daftar lokasi & pengantar', LK.daftar.length + ' lokasi · ' + LK.pengantar.length + ' pengantar')}`;
  }
  // owner 22 Nov 2026 (paket riwayat & pembatalan, tahap 1 UANG): catatan uang per hari & per orang · batalkan (alasan, ketukan kedua) · daftar Dibatalkan:
  // pulihkan / hapus permanen. Logika & koreksi hari tertutup / patokan kas di riwayat-uang-logika.js.
  function gambarRiwayat(s, tab) {
    // tahap 3 (owner 22 Nov 2026): setelan & harga — LIHAT SAJA, terbaru di atas, saring harga / setelan, muat 40 lagi
    if (tab === 'setelan') {
      const R = RS.rsDaftar(s.rsSaring || '', s.rsN || 40);
      return h`<div class="kartu" data-k="rs-saring" style="gap: 6px;"><div class="hg-pil">${RS.RS_SARING.map(([g, nm]) => h`<div class="seg ${(s.rsSaring || '') === g ? 'aktif' : ''}" data-aksi="rsSaring" data-g="${g}">${nm}</div>`)}</div></div>
        <div class="kartu" data-k="rs-daftar" style="gap: 2px;"><div class="label">${R.total ? R.total + ' perubahan' : 'Belum ada riwayat'}</div>
          ${R.baris.map((r) => h`<div class="ug-baris dua ${r.akhir ? 'redup' : ''}" data-k="rs-${r.id}"><div style="min-width: 0;"><div>${tanggalPendek(r.tanggal)}${r.jam ? ' ' + r.jam : ''} · ${r.judul}</div>
            <div class="k2">${r.oleh || '—'}</div>${r.rinci.map((t) => h`<div class="k2">· ${t}</div>`)}</div></div>`)}
          ${R.total > R.baris.length ? h`<div class="kaca-btn kecil" data-aksi="rsLagi">tampilkan ${Math.min(40, R.total - R.baris.length)} lagi</div>` : ''}</div>
        <div class="ket" style="font-size: 11px;">Lihat saja — setelan & harga dibetulkan di layarnya masing-masing. Harga katalog: tiap terbit (sejak 26 Sep 2026). Setelan dicatat dari → ke mulai ${tanggalPendek(RS.RS_MULAI)} (30 perubahan terakhir per setelan); sebelum itu hanya kapan terakhir disimpan.</div>`;
    }
    if (tab === 'batal') {
      const D = RU.ruDibatalkan();
      return h`<div class="kartu" data-k="ru-batal" style="gap: 2px;"><div class="label">${D.length ? D.length + ' catatan dibatalkan' : 'Belum ada yang dibatalkan'}</div>
        ${D.map((x) => h`<div class="ug-baris dua" data-k="rb-${x.id}"><div style="min-width: 0;"><div>${x.ringkas}</div>
            <div class="k2">dibatalkan ${tanggalPendek(x.tanggal)} ${x.jam}${x.oleh ? ' · ' + x.oleh : ''}${x.tanggalDok ? ' · catatan ' + tanggalPendek(x.tanggalDok) : ''}${x.alasan ? ' · alasan: ' + x.alasan : ''}</div>
            ${x.bisaPulih ? '' : h`<div class="k2">${x.sebabTidakPulih}</div>`}</div>
          <div style="display: flex; gap: 6px; align-items: flex-start;">${x.bisaPulih ? h`<div class="kaca-btn kecil ${s.yakinRu === 'p:' + x.id ? 'aktif emas' : ''}" data-aksi="ruPulih" data-id="${x.id}">${s.yakinRu === 'p:' + x.id ? 'KETUK LAGI · pulihkan' : 'Pulihkan'}</div>` : ''}
            <div class="kaca-btn kecil ${s.yakinRu === 'h:' + x.id ? 'awas' : ''}" data-aksi="ruHapus" data-id="${x.id}">${s.yakinRu === 'h:' + x.id ? 'KETUK LAGI · hapus permanen' : 'Hapus permanen'}</div></div></div>`)}</div>
        <div class="ket" style="font-size: 11px;">Pulihkan = catatan kembali ke buku persis seperti semula (koreksi tutup hari, patokan kas & hitungan sesudahnya dibalik). Hapus permanen = salinannya hilang dari daftar ini; catatannya sendiri sudah tidak dihitung sejak dibatalkan.</div>`;
    }
    // tab Barang (tahap 2) memakai bentuk baris yang sama; kunci baris barang berawalan 'barang|' (ruBatal memilih logikanya dari situ)
    const brg = tab === 'barang'; const L = brg ? { daftar: RB.rbDaftar, orang: RB.rbOrang, periksa: RB.rbPeriksa } : { daftar: RU.ruDaftar, orang: RU.ruOrang, periksa: RU.ruPeriksa };
    const iso = s.ruHari || hariIniIso(kini()); const D = L.daftar(iso, s.ruSaring || ''); const orang = L.orang(iso);
    const buka = s.ruBuka ? D.find((b) => b.kunci === s.ruBuka) : null; const P = buka && buka.bisa ? L.periksa(buka.koleksi, buka.id) : null;
    const baris = (b) => h`<div class="ug-baris dua ${b.bisa ? '' : 'redup'}" data-k="ru-${b.id}"><div style="min-width: 0;"><div>${b.jam ? b.jam + ' · ' : ''}${b.jenis}${brg ? '' : h` · <b>${RP(b.nominal)}</b>`}${b.anggota ? h` <span class="k2">(+${b.anggota} ${brg ? 'catatan satu ketukan' : 'pendamping'})</span>` : ''}</div>
        <div class="k2">${b.oleh || '—'}${b.teksEfek ? ' · ' + b.teksEfek : ''}${b.ket ? ' · ' + b.ket : ''}${b.titipan ? ' · dari titipan tablet' : ''}</div>${b.bisa ? '' : h`<div class="k2">${b.sebab}</div>`}
        ${buka && buka.kunci === b.kunci ? h`<div data-k="ru-buka" style="display: flex; flex-direction: column; gap: 6px; margin-top: 6px;">
          ${P && P.tolak ? h`<div class="pita-info awas">${P.tolak}</div>` : h`<div class="hg-pil" data-k="ru-alasan">${RU.RU_ALASAN.map(([id, nm]) => h`<div class="seg ${s.ruAlasan === nm ? 'aktif' : ''}" data-aksi="ruAlasan" data-a="${nm}">${nm}</div>`)}</div>
            <input class="ketik-nama" type="text" placeholder="alasan lain (wajib salah satu)" value="${RU.RU_ALASAN.some((x) => x[1] === s.ruAlasan) ? '' : s.ruAlasan || ''}" data-ketik="ruAlasanKetik" maxlength="120">
            ${(P && P.akibat ? P.akibat : []).map((t) => h`<div class="k2">· ${t}</div>`)}
            <div class="kaca-btn ${s.yakinRu === 'b:' + b.kunci ? 'aktif awas' : 'aktif'}" data-aksi="ruBatal">${s.yakinRu === 'b:' + b.kunci ? 'KETUK LAGI · BATALKAN' : 'BATALKAN'}</div>`}</div>` : ''}</div>
      ${b.bisa ? h`<div class="kaca-btn kecil ${buka && buka.kunci === b.kunci ? 'aktif' : ''}" data-aksi="ruBuka" data-k-ru="${b.kunci}">${buka && buka.kunci === b.kunci ? 'tutup' : 'Batalkan'}</div>` : ''}</div>`;
    return h`<div class="kartu" data-k="ru-hari" style="gap: 6px;"><div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
        <div class="kaca-btn kecil" data-aksi="ruGeser" data-d="-1">‹</div><div class="serif" style="font-size: 18px;">${tanggalPendek(iso)}</div><div class="kaca-btn kecil" data-aksi="ruGeser" data-d="1">›</div>
        ${iso !== hariIniIso(kini()) ? h`<div class="kaca-btn kecil" data-aksi="ruGeser" data-d="0">hari ini</div>` : ''}</div>
      ${orang.length > 1 ? h`<div class="hg-pil" data-k="ru-orang"><div class="seg ${s.ruSaring ? '' : 'aktif'}" data-aksi="ruSaring" data-o="">semua</div>${orang.map((o) => h`<div class="seg ${s.ruSaring === o ? 'aktif' : ''}" data-aksi="ruSaring" data-o="${o}">${o}</div>`)}</div>` : ''}</div>
      <div class="kartu" data-k="ru-daftar" style="gap: 2px;"><div class="label">${D.length ? D.length + (brg ? ' catatan barang' : ' catatan uang') : brg ? 'Tidak ada catatan barang di hari ini' : 'Tidak ada catatan uang di hari ini'}</div>${D.map(baris)}</div>
      ${brg ? h`<div class="ket" style="font-size: 11px;">Batalkan = seluruh catatan satu ketukan keluar dari buku (isi ulang: karung yang dibuka balik ke tumpukan, karung bekasnya ikut), salinannya tetap di tab Dibatalkan dan bisa dipulihkan. Sudah dihitung sesudahnya (cocokkan, timbang tutup hari, bongkar): selisih hitungan berikutnya dibetulkan otomatis — stok tetap = hitungan fisik. Cocokkan dibatalkan per barang. Kedatangan & adukan: di layarnya sendiri. Bulan terkunci tidak bisa.</div>` : h`<div class="ket" style="font-size: 11px;">Batalkan = catatan keluar dari buku (laci, laba, laporan tidak menghitungnya), salinannya tetap di tab Dibatalkan dan bisa dipulihkan. Catatan yang dibuat bersamaan (biaya admin, ambilan amplop, pasangan pinjaman) ikut. Hari yang sudah ditutup: selisih laci malam itu dibetulkan otomatis; rekening / brankas / amplop: patokan kasnya. Bulan terkunci tidak bisa. Nota penjualan: Jual › Riwayat. Upah = satu pembayaran utuh (slip, biaya gaji, potongan kasbon dari slip itu), hanya slip terakhir tiap orang — hari kerjanya kembali belum dibayar. Tagihan bulanan = satu tagihan kembali belum dibayar, yang lain tidak tersentuh.</div>`}`;
  }
  // Pondasi paket kedua C (owner 24 Nov 2026, rules v20): BUKU PEGANGAN — aturan kerja tertulis toko. Owner menulis di sini (satu dokumen aturanToko/bukuPegangan,
  // S.susunBabPegangan / susunHapusBab / susunGeserBab); staf membacanya di tablet (kartuPegangan — hanya bab untuk perannya, tanpa tombol tulis).
  const isiBab = (t) => h`<div class="mn-bpg-isi">${String(t || '').split('\n').map((x) => h`<div>${x || ' '}</div>`)}</div>`;
  function gambarPegangan(s) {
    const P = S.ssPegangan(); const d = s.bpgDraf; const M = S.SS_PEGANGAN_MAKS;
    const lembar = d ? h`<div class="kartu" data-k="bpg-tulis" style="gap: 8px;"><div class="serif" style="font-size: 18px;">${d.id ? 'Ubah bab' : 'Bab baru'}</div>
        <input class="ketik-nama" type="text" maxlength="${M.judul}" placeholder="Judul bab — mis. Buka toko pagi" value="${d.judul}" data-ketik="bpgKetik" data-kolom="judul">
        <textarea class="ketik-nama" rows="8" maxlength="${M.isi}" placeholder="Tulis langkahnya satu per baris: siapa mengerjakan apa, kapan, dan apa yang dilakukan kalau ada yang tidak beres." data-ketik="bpgKetik" data-kolom="isi">${d.isi}</textarea>
        <div class="label">Bab ini untuk</div><div class="jalur kisi3" data-k="bpg-untuk">${S.SS_PEGANGAN_UNTUK.map(([id, nm]) => h`<div class="seg ${d.untuk === id ? 'aktif' : ''}" data-aksi="bpgUntuk" data-u="${id}">${nm}</div>`)}</div>
        <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="bpgBatal">batal</div><div class="kaca-btn aktif emas" data-aksi="bpgSimpan" data-k="bpg-simpan">SIMPAN</div></div>
        <div class="k2">Judul paling panjang ${M.judul} huruf, isi ${ANGKA(M.isi)} huruf. Tersimpan = langsung terbaca di tablet orang yang dituju.</div></div>` : '';
    const daftar = h`<div class="kartu" data-k="bpg-daftar" style="gap: 6px;"><div class="label">Buku pegangan · ${P.teks}</div>
      ${P.ada ? P.bab.map((b, i) => h`<div class="mn-bpg-bab" data-k="bpg-${b.id}"><div class="mn-bpg-kepala" data-aksi="bpgBuka" data-id="${b.id}"><span class="no">${i + 1}</span><span class="judul">${b.judul}</span><span class="pg-cap">${b.untukNama}</span></div>
          ${s.bpgBuka[b.id] ? h`${isiBab(b.isi)}<div class="mn-bpg-tombol"><div class="kaca-btn kecil" data-aksi="bpgUbah" data-id="${b.id}">ubah</div><div class="kaca-btn kecil" data-aksi="bpgGeser" data-id="${b.id}" data-arah="-1">naik</div><div class="kaca-btn kecil" data-aksi="bpgGeser" data-id="${b.id}" data-arah="1">turun</div>
            <div class="kaca-btn kecil ${s.yakinBpg === b.id ? 'aktif awas' : ''}" data-aksi="bpgHapus" data-id="${b.id}">${s.yakinBpg === b.id ? 'KETUK LAGI · hapus' : 'hapus'}</div></div>` : ''}</div>`)
        : h`<div class="k2">Belum ada bab. Mulai dari yang paling sering ditanyakan: buka toko, terima barang dari supir, memberi bon, tutup hari.</div>`}
      ${d ? '' : h`<div class="kaca-btn aktif" data-aksi="bpgBaru" data-k="bpg-baru" style="min-height: 40px;">+ Tulis bab baru</div>`}</div>`;
    const T = S.ssTugas(); const t = s.tgsDraf; const MT = S.SS_TUGAS_MAKS;
    const lembarT = t ? h`<div class="kartu" data-k="tgs-tulis" style="gap: 8px;"><div class="serif" style="font-size: 18px;">${t.id ? 'Ubah urusan' : 'Urusan baru'}</div>
        <input class="ketik-nama" type="text" maxlength="${MT.urusan}" placeholder="Urusannya — mis. Terima barang dari supir" value="${t.urusan}" data-ketik="tgsKetik" data-kolom="urusan">
        <input class="ketik-nama" type="text" maxlength="${MT.nama}" placeholder="Dipegang siapa" value="${t.pegang}" data-ketik="tgsKetik" data-kolom="pegang">
        <input class="ketik-nama" type="text" maxlength="${MT.nama}" placeholder="Penggantinya kalau ia tidak masuk — kosongkan bila belum ada" value="${t.ganti}" data-ketik="tgsKetik" data-kolom="ganti">
        <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="tgsBatal">batal</div><div class="kaca-btn aktif emas" data-aksi="tgsSimpan" data-k="tgs-simpan">SIMPAN</div></div></div>` : '';
    const tugas = h`<div class="kartu" data-k="tgs-daftar" style="gap: 6px;"><div class="label">Siapa pegang apa · ${T.teks}</div>
      ${T.ada ? T.baris.map((x, i) => h`<div class="mn-bpg-bab" data-k="tgs-${x.id}"><div class="mn-bpg-kepala"><span class="no">${i + 1}</span><span class="judul">${x.urusan}</span><span class="pg-cap">${x.pegang}</span></div>
          <div class="mn-bpg-isi"><div class="${x.ganti ? '' : 'awas-teks'}">${x.ganti ? 'Pengganti: ' + x.ganti : 'Belum ada pengganti'}</div></div>
          <div class="mn-bpg-tombol"><div class="kaca-btn kecil" data-aksi="tgsUbah" data-id="${x.id}">ubah</div><div class="kaca-btn kecil ${s.yakinTgs === x.id ? 'aktif awas' : ''}" data-aksi="tgsHapus" data-id="${x.id}">${s.yakinTgs === x.id ? 'KETUK LAGI · hapus' : 'hapus'}</div></div></div>`)
        : h`<div class="k2">Belum ada. Tulis urusan yang kalau orangnya tidak masuk toko jadi macet: pegang laci, terima barang, timbang & takar, antar, tagih bon, tutup hari.</div>`}
      ${t ? '' : h`<div class="kaca-btn aktif" data-aksi="tgsBaru" data-k="tgs-baru" style="min-height: 40px;">+ Tulis urusan baru</div>`}
      <div class="k2">Ini catatan pembagian kerja, bukan hak akses — siapa boleh membuka layar apa tetap diatur di Peran.</div></div>`;
    return h`${lembar}${daftar}${lembarT}${tugas}<div class="k2" data-k="bpg-kaki">Ditulis owner; Penjaga laci & karyawan hanya membaca (rules v20). Bab "Semua" tampil di semua tablet; bab untuk satu peran hanya di tablet peran itu. Ketuk judul bab untuk membuka isinya.</div>`;
  }
  /** Tablet / HP staf: buku pegangan untuk perannya — baca saja. Belum ada bab untuk peran ini = satu kalimat (bukan kartu kosong). */
  function kartuPegangan(s, akunM) {
    const B = S.ssPeganganUntuk(akunM.peran);
    return h`<div class="kartu" data-k="staf-pegangan" style="gap: 6px;"><div class="label">Buku pegangan · ${B.length ? B.length + ' bab' : 'belum ada'}</div>
      ${B.length ? B.map((b, i) => h`<div class="mn-bpg-bab" data-k="sbpg-${b.id}"><div class="mn-bpg-kepala" data-aksi="bpgBuka" data-id="${b.id}"><span class="no">${i + 1}</span><span class="judul">${b.judul}</span><span class="pg-cap">${s.bpgBuka[b.id] ? 'tutup' : 'baca'}</span></div>${s.bpgBuka[b.id] ? isiBab(b.isi) : ''}</div>`)
        : h`<div class="k2">Owner belum menulis aturan kerja untuk peran ini.</div>`}</div>${kartuTugas()}`;
  }
  /** Tablet / HP staf: siapa pegang apa — baca saja; belum ditulis = tidak ada kartu. */
  function kartuTugas() {
    const T = S.ssTugas(); if (!T.ada) return '';
    return h`<div class="kartu" data-k="staf-tugas" style="gap: 6px;"><div class="label">Siapa pegang apa · ${T.n} urusan</div>
      ${T.baris.map((x, i) => h`<div class="mn-bpg-bab" data-k="stgs-${x.id}"><div class="mn-bpg-kepala" style="cursor: default;"><span class="no">${i + 1}</span><span class="judul">${x.urusan}</span><span class="pg-cap">${x.pegang}</span></div>
        <div class="mn-bpg-isi"><div>${x.ganti ? 'Pengganti: ' + x.ganti : 'Belum ada pengganti — tanya owner'}</div></div></div>`)}</div>`;
  }
  // paket KPI laba (owner 24 Nov 2026, butir 8 · 9): target omzet harian (kosong = omzet impas per hari, Laporan › Biaya) & ambang kas minimum (kosong = mati).
  // Satu dokumen aturanToko/kpiLaba (KL.susunAturKpi — kolom yang tidak dikirim, mis. target margin dari Harga, tidak ikut tertimpa).
  function gambarTarget(s, d) {
    const A = KL.klAtur(); const T = KL.klTargetHari(d); const C = KL.klKasMinimum(); const a = s.aturKpi;
    const nilai = (n) => (n > 0 ? String(n) : '');
    const isian = (k, label, ket, ph, satuan, isiAwal) => h`<div class="at-baris" data-k="kpi-${k}"><div>${label}<div class="k2">${ket}</div></div><input class="ketik-nama" type="text" inputmode="${satuan ? 'decimal' : 'numeric'}" placeholder="${ph}" value="${a ? a[k] : isiAwal !== undefined ? isiAwal : nilai(A[k])}" data-ketik="kpiKetik" data-kolom="${k}"><span class="k2">${satuan || 'rupiah'}</span></div>`;
    // A121 (owner 27 Nov 2026): bunga modal stok — kosong = bawaan 6 % setahun, 0 = mati; Dasbor › Margin & target menghitung biaya modal yang tertahan di stok
    const MT = (() => { try { return KL.klModalTertahan(d, null, null); } catch (e) { return null; } })();
    return h`<div class="kartu" data-k="kpi-keadaan" style="gap: 6px;"><div class="label">Sekarang</div>
        <div class="pg-baris" data-k="kpi-t"><div><div style="font-weight: 600;">Omzet hari ini ${RP(T.omzet)}${T.target ? ' dari ' + RP(T.target) : ''}</div><div class="k2">${T.teks}</div></div><div class="n"><span class="pg-cap ${T.lampu === 'merah' ? 'awas' : ''}">${T.lampu === 'tanpa' ? 'tanpa target' : T.lampu}</span></div></div>
        <div class="pg-baris" data-k="kpi-k"><div><div style="font-weight: 600;">${C.nyala ? 'Kas ' + (C.kas === null ? '—' : RP(C.kas)) + ' · ambang ' + RP(C.batas) : 'Ambang kas minimum mati'}</div><div class="k2">${C.teks}</div></div><div class="n">${C.bawah ? h`<span class="pg-cap awas">kurang</span>` : ''}</div></div>
        ${MT && MT.rata !== null ? h`<div class="pg-baris" data-k="kpi-m"><div><div style="font-weight: 600;">Modal tertahan di stok ${RP(Math.round(MT.rata))} rata-rata · bunga ${KL.klPctTeks(MT.bunga)}${MT.dariOwner ? '' : ' (bawaan)'}</div><div class="k2">${MT.kalimat}</div></div></div>` : ''}</div>
      <div class="kartu" data-k="kpi-atur" style="gap: 8px;"><div class="serif" style="font-size: 18px;">Atur sendiri · Target & ambang</div>
        ${isian('targetHarian', 'Target omzet harian', T.bawaan ? 'kosong = omzet impas per hari ' + RP(T.bawaan) + ' (Laporan › Biaya)' : 'kosong = omzet impas per hari (belum bisa dihitung)', T.bawaan ? 'impas ' + RP(T.bawaan) : 'impas')}
        ${isian('kasMinimum', 'Ambang kas minimum', 'Dasbor memperingatkan bila laci + brankas + rekening + amplop di bawah angka ini · kosong = mati', 'mati')}
        ${isian('bungaModal', 'Bunga modal stok', 'biaya modal yang tertahan di stok = rata-rata nilai stok × bunga ini · kosong = bawaan ' + KL.KL_BUNGA_BAWAAN + ' % setahun · 0 = mati · bukan biaya di laba bersih', 'bawaan ' + KL.KL_BUNGA_BAWAAN, '% setahun', A.bungaDariOwner ? String(A.bungaModal).replace('.', ',') : '')}
        <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="kpiBatal">batal</div><div class="kaca-btn aktif emas" data-aksi="kpiSimpan">SIMPAN</div></div>
        <div class="k2">Target margin per jenis diatur di Harga & Pemasok › Katalog (saran harga). Batas HPP per kg per merek diatur di Stok › Barang masuk. Lampu target: hijau = tercapai · kuning = sesuai laju jam toko · merah = di bawah laju.</div></div>`;
  }
  // paket KPI laba (owner 24 Nov 2026, butir 14): CEK MINGGUAN timbangan & gudang — lima hal beres / ada masalah + catatan. Owner (Pengingat) & Penjaga laci
  // (tablet; rules v19). Satu dokumen cekGudang per cek (S.susunCekGudang); jadwal berikutnya = cek terakhir + tiap N hari (Atur pengingat).
  function kartuCekGudang(s, d) {
    const G = S.ssCekGudang(d); const a = s.cekG || { cek: {}, catatan: '' }; const masalah = S.SS_CEK_GUDANG.filter((x) => a.cek[x.id] === false).length;
    return h`<div class="kartu mn-cek-gudang ${G.perlu ? 'perlu' : ''}" data-k="cek-gudang" style="gap: 6px;"><div class="label">Cek mingguan timbangan & gudang</div>
      <div class="${G.sisa < 0 ? 'pita-info awas' : 'k2'}" data-k="cg-jadwal">${G.teks}${G.terakhir && G.terakhir.oleh ? ' · terakhir oleh ' + G.terakhir.oleh : ''}</div>
      ${S.SS_CEK_GUDANG.map((x) => h`<div class="cg-hal" data-k="cg-${x.id}"><div><div style="font-weight: 600;">${x.nama}</div>${x.ket ? h`<div class="k2">${x.ket}</div>` : ''}</div>
        <div class="hg-pil"><span class="seg ${a.cek[x.id] === true ? 'aktif' : ''}" data-aksi="cgHal" data-hal="${x.id}" data-v="1">beres</span><span class="seg ${a.cek[x.id] === false ? 'aktif awas' : ''}" data-aksi="cgHal" data-hal="${x.id}" data-v="0">ada masalah</span></div></div>`)}
      <input class="ketik-nama" type="text" placeholder="${masalah ? 'Catatan WAJIB: apa & di mana' : 'Catatan (boleh kosong kalau semua beres)'}" value="${a.catatan}" data-ketik="cgCatatan">
      <div class="kaca-btn aktif emas" data-aksi="cgSimpan" data-k="cg-simpan">SIMPAN CEK</div>
      ${G.riwayat.length ? h`<div class="k2" data-k="cg-riwayat">${G.riwayat.slice(0, 4).map((r) => tanggalPendek(r.tanggal) + (r.masalah.length ? ' · masalah: ' + r.masalah.join(', ') : ' · beres')).join(' — ')}</div>` : ''}</div>`;
  }
  function gambarPengingat(s, d, tab) {
    const G = S.ssPengingat(d, lokal(), s.hariP);
    if (tab === 'aturan') return h`<div style="display: flex; flex-direction: column; gap: 6px;" data-k="aturan-g">${G.aturan.map((a) => h`<div class="pg-aturan ${a.nyala ? '' : 'mati'}" data-k="a-${a.id}"><div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;"><b>${a.nama}</b><span class="pg-saklar ${a.nyala ? 'nyala' : ''}" data-aksi="saklarG" data-jenis="${a.id}"></span></div><div class="k2">${a.ket} · ${a.sumber} sumber</div><div class="hg-pil">${S.SS_PENERIMA.map((n) => h`<div class="seg ${a.ke.indexOf(n) >= 0 ? 'aktif' : ''}" style="padding: 4px 9px; font-size: 11px;" data-aksi="keG" data-jenis="${a.id}" data-nama="${n}">${n}</div>`)}</div></div>`)}</div>
      <div class="ket" data-k="ket-g" style="font-size: 11px;">Lima sumber: bon pemasok (tempo dari Atur pencatatan stok), janji bayar (tagihan di Pelanggan → Bon), kantong menipis (laju pakai 14 hari), opname rutin, cadangan berkas. Mematikan jenis tidak menghapus yang lewat.${G.bonTanpaTanggal ? ' ' + G.bonTanpaTanggal + ' bon pemasok tanpa tanggal tidak bisa diingatkan.' : ''}</div>
      ${pintuAtur('Atur hari sebelum, lama & batas tunda', 'tunda ' + G.atur.tundaHari + ' hari × ' + G.atur.maksTunda + ' kali · opname tiap ' + G.atur.opnameTiap + ' hari')}`;
    const p = G.sumber.find((x) => x.id === s.pilihG) || null;
    const baris = (x) => h`<div class="pg-baris ${p && p.id === x.id ? 'aktif' : ''} ${x.sisa < 0 ? 'lewat' : ''}" data-k="g-${x.id}" data-aksi="pilihG" data-id="${x.id}"><div><div style="font-weight: 600;">${x.teks}${x.tunda ? h`<span class="pg-cap ${x.tundaKali >= G.atur.maksTunda ? 'awas' : ''}">ditunda</span>` : ''}</div><div class="k2">${tanggalPendek(x.jatuhEfektif)} · ${x.sisaTeks} · ke ${x.ke.join(' & ')} · ${x.ket}</div></div><div class="n">${x.n ? RP(x.n) : ''}</div></div>`;
    return h`<div class="pil ${G.lewat.length ? 'kedip' : ''}" data-k="pil-g">${G.ringkas}</div>
      <div class="kartu" data-k="kal-g" style="gap: 6px; padding: 10px 12px;"><div class="pg-kal">${G.kalender.map((k) => h`<div class="pg-hari ${k.aktif ? 'aktif' : ''} ${k.ini ? 'ini' : ''}" data-k="h-${k.iso}" data-aksi="hariP" data-h="${k.h}"><span class="nm">${k.nm}</span><b>${k.tgl}</b><span class="c ${k.lewat ? 'awas' : ''}">${k.n || ''}</span></div>`)}</div><div class="k2">angka = jumlah pengingat hari itu · merah = sudah lewat</div></div>
      <div class="kartu" data-k="hari-g" style="gap: 0; padding: 8px 10px;"><div class="label" style="padding-top: 2px;">${G.hariJudul}</div>${G.hariDaftar.map(baris)}</div>
      ${G.hariKe === 0 && G.lewat.length ? h`<div class="kartu" data-k="lewat-g" style="gap: 0; padding: 8px 10px;"><div class="label awas-teks" style="padding-top: 2px;">Sudah lewat · ${G.lewat.length}</div>${G.lewat.map(baris)}</div>` : ''}
      ${G.hariKe === 0 && G.segera.length ? h`<div class="kartu" data-k="segera-g" style="gap: 0; padding: 8px 10px;"><div class="label" style="padding-top: 2px;">Segera · ${G.segera.length}</div>${G.segera.map(baris)}</div>` : ''}
      ${p && p.jenis === 'gudang' ? kartuCekGudang(s, d) : ''}
      ${p && p.jenis === 'patuh' ? kartuCentang(PT.ptKalender(d).baris.find((b) => b.id === p.butir) || null, s) : ''}
      ${p && p.jenis !== 'gudang' && p.jenis !== 'patuh' ? h`<div class="kartu" data-k="panel-g" style="gap: 6px;"><div style="font-weight: 700;">${p.teks} · ${p.sisaTeks}${p.n ? ' · ' + RP(p.n) : ''}</div>${p.selesai ? h`<div class="k2">Sudah selesai${p.catatan ? ' · ' + p.catatan : ''}</div>` : h`<input class="ketik-nama" type="text" placeholder="Catatan (wajib kalau sudah lewat)" value="${s.catatanG}" data-ketik="catatanG"><div class="k2">${p.tundaKali >= G.atur.maksTunda ? 'Sudah ditunda ' + p.tundaKali + ' kali (batas ' + G.atur.maksTunda + ') — harus ditindak' : 'Tunda ' + G.atur.tundaHari + ' hari (' + p.tundaKali + ' dari ' + G.atur.maksTunda + ' kali)'}</div>
        <div class="pg-tiga"><div class="kaca-btn aktif emas" data-aksi="selesaiG">SELESAI</div><div class="kaca-btn" data-aksi="tundaG">tunda</div>${p.jenis === 'janji' ? h`<div class="kaca-btn ${s.yakinWa ? 'awas' : 'aktif'}" data-aksi="waG">${s.yakinWa ? 'YAKIN kirim lagi' : 'kirim WA'}</div>` : ''}</div>`}</div>` : ''}
      <div class="ket" data-k="ket-kal" style="font-size: 11px;">Yang lewat tidak bisa dihapus — diselesaikan dengan catatan, atau ditunda sampai batasnya. "Selesai" di sini tidak mencatat uangnya: bayar bon pemasok di Harga & Pemasok → Bon pemasok, bayar pelanggan di Pelanggan → Bon.</div>
      ${pintuAtur('Atur hari sebelum, lama & batas tunda', 'tunda ' + G.atur.tundaHari + ' hari × ' + G.atur.maksTunda + ' kali · opname tiap ' + G.atur.opnameTiap + ' hari')}`;
  }
  // owner 7 Okt (JS2-C): jatah nego per akun terdaftar (kosong = ikut perannya) + siapa boleh menjual di bawah modal (wajib alasan, tercatat di nota)
  function aturNegoOrang(a) {
    const akun = S.ssAkun().akun.filter((x) => x.aktif); const bm = a.bawahModal || [];
    const pil = (kunci, nama) => h`<div class="seg ${bm.indexOf(kunci) >= 0 ? 'aktif' : ''}" data-aksi="aturBawahModal" data-kunci="${kunci}">${nama}</div>`;
    return h`<div class="label" style="margin-top: 4px;">Jatah nego per orang (kosong = ikut perannya · owner selalu sampai modal)</div>
      ${akun.length ? akun.map((x) => h`<div class="at-baris" data-k="at-ja-${x.uid}"><div>${x.nama || x.email} <span class="k2">${x.namaPeran}</span></div><input class="ketik-nama sempit" type="text" inputmode="numeric" placeholder="ikut peran" value="${(a.jatahAkun || {})[x.uid] || ''}" data-ketik="aturJatahAkun" data-uid="${x.uid}"><span class="k2">% margin</span></div>`) : h`<div class="k2">Belum ada akun karyawan terdaftar — jatahnya mengikuti peran di atas.</div>`}
      <div class="label" style="margin-top: 4px;">Boleh jual di bawah modal (wajib alasan; bukan-owner tetap minta owner)</div>
      <div class="hg-pil" data-k="at-bawah-modal">${pil('owner', 'Owner')}${S.SS_PERAN_AKUN.map((p) => pil(p.id, p.nama))}${akun.map((x) => pil('uid:' + x.uid, x.nama || x.email))}</div>`;
  }
  // owner 26 Nov 2026: langit gerbang ikut jam & cuaca sungguhan di lokasi toko — lokasi dipilih di sini (tingkat kelurahan/kota, tanpa GPS perangkat)
  function aturCuaca(s, a) {
    return h`<div class="label" style="margin-top: 4px;" data-k="at-cuaca">Langit & cuaca di gerbang</div>
      <div class="k2" data-k="at-cuaca-kini">${a.cuaca ? 'Lokasi: ' + a.cuaca.nama : 'Belum ada lokasi — langit gerbang ikut jam saja (fajar, siang, senja, malam)'}</div>
      <div class="at-baris" data-k="at-cuaca-cari"><input class="ketik-nama" type="text" placeholder="nama kelurahan / kecamatan / kota" value="${s.cuacaCari}" data-ketik="cuacaCariKetik" maxlength="60">
        <div class="kaca-btn kecil" data-aksi="cuacaCari">${s.cuacaSibuk ? '…' : 'cari'}</div></div>
      ${s.cuacaKabar ? h`<div class="pita-info awas" data-k="at-cuaca-kabar">${s.cuacaKabar}</div>` : ''}
      ${s.cuacaHasil.length ? h`<div class="hg-pil" data-k="at-cuaca-hasil">${s.cuacaHasil.map((r, i) => h`<div class="seg" data-aksi="cuacaPilih" data-i="${i}">${r.nama}${r.wilayah ? ' · ' + r.wilayah : ''}</div>`)}</div>` : ''}
      ${a.cuaca ? h`<div class="hg-pil" data-k="at-cuaca-cabut"><div class="seg" data-aksi="cuacaCabut">cabut lokasi</div></div>` : ''}
      <div class="k2" data-k="at-cuaca-ket">Cuaca diambil dari Open-Meteo (gratis) paling sering tiap 30 menit, hanya memakai titik lokasi ini — tidak ada data toko yang dikirim. Berlaku di semua perangkat sesudah SIMPAN ATURAN.</div>`;
  }
  function gambarAtur(s) {
    const a = s.atur; const angka = (k, label, satuan) => h`<div class="at-baris" data-k="at-${k}"><div>${label}</div><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${a[k]}" data-ketik="aturKetik" data-kolom="${k}"><span class="k2">${satuan}</span></div>`;
    const daftar = (k, label, contoh) => h`<div class="label" style="margin-top: 4px;">${label}</div>${a[k].map((x, i) => h`<div class="at-baris" data-k="at-${k}-${i}"><input class="ketik-nama" type="text" placeholder="${contoh}" value="${x}" data-ketik="aturKetik" data-kolom="${k}" data-i="${i}"><span class="mn-x" data-aksi="aturLepas" data-daftar="${k}" data-i="${i}">×</span></div>`)}<div class="kaca-btn putus" data-aksi="aturTambah" data-daftar="${k}">＋ tambah</div>`;
    return h`<div class="kartu" data-k="atur-${a.id}" style="gap: 8px;"><div class="serif" style="font-size: 18px;">Atur sendiri · ${JUDUL_SISTEM[a.id]}</div>
      ${a.id === 'perangkat' ? [angka('batasAntre', 'Antrean dianggap lama', 'menit'), angka('batasDenyut', 'Denyut dianggap lama', 'menit'), aturCuaca(s, a), daftar('pemegang', 'Boleh mencatat di perangkat (Owner tak terhapus)', 'nama orang')]
      : a.id === 'peran' ? [angka('batasSekaligus', 'Batas setujui sekaligus', 'rupiah'), angka('jatahBen', 'Jatah nego Ben', '% margin'), angka('jatahKaryawan', 'Jatah nego karyawan', '% margin'), angka('langkahNego', 'Langkah harga nego', 'rupiah'), aturNegoOrang(a)]
      : a.id === 'cadangan' ? [angka('cadanganTiap', 'Ingatkan cadangan tiap', 'hari'), angka('simpanHari', 'Simpan catatan cadangan', 'hari'), angka('ambangKuota', 'Ambang kuota simpanan lokal', '%')]
      : a.id === 'lokasi' ? [h`<div class="label">Lokasi (tepat satu utama)</div>`, a.daftar.map((l, i) => h`<div class="at-lokasi" data-k="at-l-${i}"><input class="ketik-nama" type="text" placeholder="nama lokasi (cabang, gudang)" value="${l.nama}" data-ketik="aturKetik" data-kolom="daftar" data-i="${i}" data-sub="nama"><input class="ketik-nama" type="text" placeholder="alamat (boleh kosong)" value="${l.alamat}" data-ketik="aturKetik" data-kolom="daftar" data-i="${i}" data-sub="alamat"><div class="seg ${l.utama ? 'aktif' : ''}" data-aksi="aturUtama" data-i="${i}">${l.utama ? 'utama' : 'jadikan utama'}</div><span class="mn-x" data-aksi="aturLepas" data-daftar="daftar" data-i="${i}">×</span></div>`), h`<div class="kaca-btn putus" data-aksi="aturTambah" data-daftar="daftar">＋ tambah lokasi</div>`, daftar('pengantar', 'Pengantar pindah stok', 'nama pengantar')]
      : [angka('hariBon', 'Bon pemasok: ingatkan', 'hari sebelum'), angka('hariJanji', 'Janji bayar: ingatkan', 'hari sebelum'), angka('hariKantong', 'Kantong: ingatkan', 'hari sebelum habis'), angka('hariOpname', 'Opname: ingatkan', 'hari sebelum'), angka('opnameTiap', 'Opname rutin tiap', 'hari'), angka('hariCadangan', 'Cadangan: ingatkan', 'hari sebelum'), angka('tundaHari', 'Lama tunda', 'hari'), angka('maksTunda', 'Batas tunda', 'kali')]}
      <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN ATURAN</div></div></div>`;
  }

  K.dengar(gambar);
  dengarkan(() => nanti(gambar));
  return { keadaan: K, belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan, gambar, buka: (sistem, tab) => { set({ sistem: sistem || null, tabS: Object.assign({}, st().tabS, sistem && tab ? { [sistem]: tab } : {}), kabar: '' }); if (sistem) ukurSimpanan(); },
    tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); ukurSimpanan(); } if (tampil && (_kotor || !akar.firstElementChild || _kunciGambar !== kunciGambar())) segera(gambar); } };
}
