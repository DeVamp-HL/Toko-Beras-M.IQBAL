// LAYAR MENU — GAMBAR & KETUKAN. Rangka laci N1 (dikunci owner 16 Sep 2026: "pertahankan desain UI di layar N1") dipakai apa adanya:
// kepala kelompok yang bisa dibuka-tutup, tiap baris = ikon + judul + sub + angka + keterangan. Laci PALING ATAS = pita jam (N9),
// di bawahnya laci yang tidak pernah berpindah tempat. Dasar penyusunan lain (N2 Tanya · N5 Jam · N6 Orang · N8 Tertutup) = tab.
// Baris Sistem (Perangkat · Peran · Cadangan · Lokasi · Pengingat, desain SS1–SS5 dikunci 19 Sep) dibuka sebagai LEMBAR di dalam Menu.
// Layar dimorf (elemen hidup terus): laci membuka dengan transisi, angka bergulir, baris masuk bergiliran.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { pasangIsian } from '../inti/isian.js';
import { RP, ANGKA, tanggalPendek, hariIniIso, jamKini, jamSetempat, waktuSetempat } from '../inti/format.js';
import * as M from './menu-logika.js';
import * as S from './sistem-logika.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, dokDiCache, bertahapTertunda, lanjutkanBertahap, buangBertahap } from '../data/toko.js';
import { kpAlasanDitolak, kpKeHariIni } from './kunci-periode-logika.js';

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
const HALAMAN_LAMA = { Pemasok: 'Menu → Pemasok', Harga: 'Menu → Harga', Laba: 'Menu → Laba', Setelan: 'Menu → Setelan', 'Tutup Hari': 'Menu → Tutup Hari', Harian: 'Menu → Harian', Bulanan: 'Menu → Bulanan', Jual: 'Jual' };
const TAB_SISTEM = { perangkat: [['perangkat', 'Perangkat'], ['antrean', 'Antrean kirim'], ['jejak', 'Jejak pencatat']], peran: [['peran', 'Peran & hak'], ['minta', 'Persetujuan']], cadangan: [], lokasi: [['lokasi', 'Lokasi'], ['pindah', 'Pindah stok'], ['lapor', 'Laporan']], pengingat: [['kal', 'Kalender'], ['aturan', 'Aturan']] };
const JUDUL_SISTEM = { perangkat: 'Perangkat & antrean', peran: 'Peran & persetujuan', cadangan: 'Cadangan & simpanan', lokasi: 'Lokasi', pengingat: 'Pengingat' };

/** opsi: gantiMode, mode, sekarang, statusRingkas, pindah(tujuan), bukaStok(lembar|tab), bukaPelanggan(keluarga, orang), lokal() → { antre, idPerangkat, pemegang, lokasi, namaPerangkat, koleksiSiap, koleksiTotal, offline }, periksaSambungan(), setelLokasi, namaiPerangkat, akun(), antreLokal(), buangDitolak(id), tulisUlangDitolak(id) */
export function pasangLayarMenu(akar, opsi) {
  const tabAwal = bacaLokal(KUNCI_TAB) || {}; const laciAwal = bacaLokal(KUNCI_LACI) || {};
  // putaran 23d: keadaan awal sebagai FUNGSI — dipanggil ulang saat ganti orang (inti/isian.js)
  const awal = () => ({ susunan: M.MN_SUSUNAN.some((t) => t[0] === tabAwal.susunan) ? tabAwal.susunan : 'laci', tutup: laciAwal.tutup || {}, bagian: null, cari: '', buka: null, kabar: '', kabarAwas: false,
    sistem: null, tabS: {}, pilihP: null, saring: '', peran: 'ben', akunPilih: {}, yakinAkun: null, alasanAkses: '', yakinBuang: null, mintaKe: null, alasan: '', hariC: null, hariP: 0, pilihG: null, catatanG: '', yakinWa: false, atur: null, pindah: { merk: '', dari: '', ke: '', kg: '', pengantar: '' }, lokasiPilih: null, sambungTeks: '', lsKb: null, usageKb: null, quotaKb: null, autoTanggal: null });
  const K = buatKeadaan(awal());
  const ISIAN = pasangIsian(K, awal, ['pindah', 'alasan', 'alasanAkses', 'atur', 'catatanG', 'akunPilih', ['namaBaru', (v) => !!String(v || '').trim()]], []);
  const set = (p) => K.setel(p); const st = () => K.baca(); let tampil = false;
  const kini = () => opsi.sekarang() || new Date();
  const waktu = () => { const d = kini(); return { tanggal: hariIniIso(d), jam: jamKini(d), kini: new Date().toISOString(), idUnik: () => Date.now() + Math.random() }; };
  const lokal = () => Object.assign({}, opsi.lokal ? opsi.lokal() : {}, { lsKb: st().lsKb, usageKb: st().usageKb, quotaKb: st().quotaKb, autoTanggal: st().autoTanggal });
  const ingat = () => { simpanLokal(KUNCI_TAB, { susunan: st().susunan }); simpanLokal(KUNCI_LACI, { tutup: st().tutup }); };
  async function tulis(r) {
    if (!r || r.tolak) { set({ kabar: (r && r.tolak) || 'Tidak ada yang ditulis', kabarAwas: true }); return false; }
    try { const x = await tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus }); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch || {}, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch && r.patch.kabar) || 'Tersimpan') })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  // ukuran simpanan lokal dibaca dari peramban (bukan ditebak); tidak terbaca → null → layar bilang tidak bisa dibaca
  function ukurSimpanan() {
    let ls = null; try { let b = 0; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); b += (k.length + String(localStorage.getItem(k) || '').length) * 2; } ls = Math.round(b / 1024); } catch (e) { ls = null; }
    let auto = null; try { auto = localStorage.getItem('miqbal_backup_auto_tanggal') || null; } catch (e) { auto = null; }
    set({ lsKb: ls, autoTanggal: auto });
    try { if (navigator.storage && navigator.storage.estimate) navigator.storage.estimate().then((e) => set({ usageKb: Math.round((e.usage || 0) / 1024), quotaKb: Math.round((e.quota || 0) / 1024) })).catch(() => {}); } catch (e) { /* abaikan */ }
  }
  // ---- tujuan tiap baris: layar sistem baru, lembar Sistem di dalam Menu, atau sistem lama (mengaku) ----
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
    if (t.ke === 'lama') { set({ kabar: 'Layar ini belum ada di sistem baru — di sistem lama: ' + (HALAMAN_LAMA[t.halaman] || t.halaman) + '. ', kabarAwas: false, bukaLama: t.halaman }); return; }
    set({ kabar: 'Belum ada layarnya di sistem baru.', kabarAwas: true });
  }
  const AKSI = {
    susunan: ({ s }) => { set({ susunan: s, buka: null, kabar: '' }); ingat(); }, mode: () => opsi.gantiMode(), tutupKabar: () => set({ kabar: '', bukaLama: null }),
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
    lanjutBertahap: async () => { const r = await lanjutkanBertahap(); set({ kabar: r && r.gagal ? 'BERHENTI: ' + r.pesan : 'Kiriman bertahap selesai (' + (r.total || 0) + ' tahap)', kabarAwas: !!(r && r.gagal) }); },
    buangBertahap: () => { if (st().yakinBuang !== 'bertahap') return set({ yakinBuang: 'bertahap', kabar: 'Ketuk sekali lagi: sisa kiriman bertahap TIDAK dikirim (yang sudah masuk tetap masuk)', kabarAwas: true }); buangBertahap(); set({ yakinBuang: null, kabar: 'Sisa kiriman bertahap dibuang', kabarAwas: false }); },
    buangDitolak: ({ id }) => { if (!opsi.buangDitolak) return; if (st().yakinBuang !== id) return set({ yakinBuang: id, kabar: 'Ketuk sekali lagi untuk membuang kiriman itu — isinya tidak akan pernah masuk data toko', kabarAwas: true }); opsi.buangDitolak(id); set({ yakinBuang: null, kabar: 'Kiriman yang ditolak dibuang', kabarAwas: false }); },
    namaiPerangkat: (v) => set({ namaBaru: String(v).slice(0, 30) }), namaiSimpan: () => { if (!opsi.namaiPerangkat) return; opsi.namaiPerangkat(st().namaBaru || ''); set({ kabar: 'Perangkat ini kini bernama ' + (st().namaBaru || '(tanpa nama)') + ' — jejak & denyut memakai nama itu', kabarAwas: false, namaBaru: '' }); },
    peran: ({ id }) => set({ peran: id, kabar: '' }), putarHak: async ({ peran, t }) => { await tulis(S.susunPutarHak(peran, t, waktu())); },
    mintaKe: ({ id }) => set({ mintaKe: st().mintaKe === id ? null : id, alasan: '' }), alasan: (v) => set({ alasan: String(v).slice(0, 80) }),
    setujui: async () => { if (await tulis(S.susunPutusPersetujuan(st().mintaKe, true, '', waktu()))) set({ mintaKe: null }); }, tolak: async () => { if (await tulis(S.susunPutusPersetujuan(st().mintaKe, false, st().alasan, waktu()))) set({ mintaKe: null, alasan: '' }); },
    setujuiKecil: async () => { await tulis(S.susunSetujuiKecil(waktu())); },
    hariC: ({ iso }) => set({ hariC: iso }),
    unduhCadangan: async () => { const b = S.ssBerkasCadangan(kini()); const teks = JSON.stringify(b.isi, null, 2); let bytes = teks.length;
      try { const blob = new Blob([teks], { type: 'application/json' }); bytes = blob.size; const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = b.nama; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(url), 2000); }
      catch (e) { set({ kabar: 'Peramban ini tidak bisa mengunduh berkas: ' + (e && e.message ? e.message : e), kabarAwas: true }); return; }
      await tulis(S.susunCatatCadangan(b, bytes, waktu(), (opsi.lokal ? opsi.lokal() : {}).namaPerangkat || '')); ukurSimpanan(); },
    lokasiPilih: ({ id }) => set({ lokasiPilih: id }), lokasiIni: ({ id }) => { if (!opsi.setelLokasi) return; opsi.setelLokasi(id); set({ kabar: 'Perangkat ini kini mencatat di ' + (S.ssLokasi().daftar.find((l) => l.id === id) || { nama: id }).nama + ' — catatan berikutnya membawa lokasi itu', kabarAwas: false }); },
    jadikanUtama: async ({ id }) => { await tulis(S.susunJadikanUtama(id, waktu())); },
    pindahIsi: (v, el) => { const p = Object.assign({}, st().pindah); p[el.dataset.kolom] = String(v).slice(0, 10); set({ pindah: p }); }, pindahPilih: ({ kolom, nilai }) => { const p = Object.assign({}, st().pindah); p[kolom] = p[kolom] === nilai ? '' : nilai; set({ pindah: p, kabar: '' }); },
    pindahSimpan: async () => { const p = st().pindah; if (await tulis(S.susunPindahStok(p.merk, p.dari, p.ke, p.kg, p.pengantar, waktu()))) set({ pindah: { merk: '', dari: '', ke: '', kg: '', pengantar: '' } }); },
    hariP: ({ h }) => set({ hariP: Number(h), pilihG: null }), pilihG: ({ id }) => set({ pilihG: st().pilihG === id ? null : id, catatanG: '', yakinWa: false }), catatanG: (v) => set({ catatanG: String(v).slice(0, 80) }),
    selesaiG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); if (await tulis(S.susunSelesaiPengingat(p, st().catatanG, waktu()))) set({ pilihG: null, catatanG: '' }); },
    tundaG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); if (await tulis(S.susunTundaPengingat(p, waktu()))) set({ pilihG: null }); },
    waG: async () => { const p = S.ssPengingat(kini(), lokal()).sumber.find((x) => x.id === st().pilihG); const r = S.susunWaPengingat(kini(), p, waktu(), st().yakinWa); if (r.perluYakin) return set({ yakinWa: true, kabar: r.tolak, kabarAwas: true }); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); try { window.open(r.url, '_blank'); } catch (e) { /* abaikan */ } if (await tulis(r)) set({ yakinWa: false }); },
    saklarG: async ({ jenis }) => { await tulis(S.susunSaklarPengingat(jenis, waktu())); }, keG: async ({ jenis, nama }) => { await tulis(S.susunKePengingat(jenis, nama, waktu())); },
    // ---- ATUR SENDIRI per lembar Sistem (angka & daftar owner)
    bukaAtur: () => { if (st().atur) return set({ atur: null }); const id = st().sistem; const a = S.ssAtur(id); const d = { id };
      if (id === 'perangkat') Object.assign(d, { batasAntre: String(a.batasAntre), batasDenyut: String(a.batasDenyut), pemegang: a.pemegang.slice() });
      if (id === 'peran') Object.assign(d, { batasSekaligus: String(a.batasSekaligus), jatahBen: String(a.jatahBen) });
      if (id === 'cadangan') Object.assign(d, { simpanHari: String(a.simpanHari), ambangKuota: String(a.ambangKuota), cadanganTiap: String(a.cadanganTiap) });
      if (id === 'lokasi') Object.assign(d, { daftar: a.daftar.map((l) => Object.assign({}, l)), pengantar: a.pengantar.slice() });
      if (id === 'pengingat') Object.assign(d, { hariBon: String(a.hariBon), hariJanji: String(a.hariJanji), hariKantong: String(a.hariKantong), hariOpname: String(a.hariOpname), hariCadangan: String(a.hariCadangan), tundaHari: String(a.tundaHari), maksTunda: String(a.maksTunda), opnameTiap: String(a.opnameTiap) });
      set({ atur: d, kabar: '' }); },
    aturKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().atur)); const k = el.dataset.kolom, i = el.dataset.i, sub = el.dataset.sub; if (i === undefined) a[k] = String(v).slice(0, 12); else if (sub) a[k][Number(i)][sub] = String(v).slice(0, 60); else a[k][Number(i)] = String(v).slice(0, 40); set({ atur: a }); },
    aturTambah: ({ daftar: k }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].push(k === 'daftar' ? { id: 'lk' + Date.now().toString(36), nama: '', alamat: '', utama: false } : ''); set({ atur: a }); },
    aturLepas: ({ daftar: k, i }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].splice(Number(i), 1); set({ atur: a }); },
    aturUtama: ({ i }) => { const a = JSON.parse(JSON.stringify(st().atur)); a.daftar.forEach((l, j) => { l.utama = j === Number(i); }); set({ atur: a }); },
    simpanAtur: async () => { const a = st().atur; if (!a) return; const isi = Object.assign({}, a); delete isi.id; if (await tulis(S.susunAturSistem(a.id, isi, waktu()))) set({ atur: null }); },
  };
  delegasi(akar, AKSI);

  // ---------- GAMBAR ----------
  function gambar() {
    if (!tampil || terkunci()) return;
    const s = st(); const sumber = sumberData(); const d = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="label">Menu</div><div class="serif" style="font-size: 24px;">${s.sistem ? JUDUL_SISTEM[s.sistem] : s.susunan === 'laci' ? 'Pita jam di atas laci' : s.susunan === 'tanya' ? 'Menu yang bertanya' : s.susunan === 'jam' ? 'Menu yang tahu jam' : s.susunan === 'orang' ? 'Menu menurut orang' : 'Menu yang menolak'}</div>
          <div class="ket">${tanggalPendek(hariIniIso(d))} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil pil-akun ${sumber.jenis === 'firestore' ? '' : 'kedip'}" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON_MODE[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}${s.bukaLama ? h` <a href="../index.html" class="mn-tautan" data-k="tautan-lama">Buka sistem lama ›</a>` : ''}</div>` : ''}
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
    const cari = M.susunCari(d, s.cari); const L = lokal();
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
  function gambarStaf(s, d, akunM) {
    const namaP = (S.SS_PERAN.find((p) => p.id === akunM.peran) || {}).nama || akunM.peran; const L = lokal();
    const AL = opsi.antreLokal ? opsi.antreLokal() : { belum: [], ditolak: [] };
    return h`<section class="mn-staf" data-k="staf" style="display: flex; flex-direction: column; gap: 10px;">
      <div class="kartu" data-k="staf-akun" style="gap: 4px;"><div class="label">Masuk sebagai</div><div class="serif" style="font-size: 20px;">${akunM.nama}</div><div class="k2">${namaP} · ${L.namaPerangkat || 'perangkat ini'}</div></div>
      <div class="tombol-baris" data-k="staf-layar">${[['jual', 'Jual'], ['pelanggan', 'Pelanggan'], ['stok', 'Stok']].map(([t, n]) => h`<div class="kaca-btn aktif" data-aksi="stafKe" data-t="${t}">${n}</div>`)}</div>
      <div class="kartu" data-k="staf-antre" style="gap: 4px;"><div class="label">Catatan dari perangkat ini</div>
        <div class="k2">${(L.antre || []).length ? (L.antre || []).length + ' menunggu server' : 'semua sudah sampai server'} · ${AL.ditolak.length ? AL.ditolak.length + ' DITOLAK server — menunggu owner memutuskan' : 'tidak ada yang ditolak'}</div></div>
      <div class="pita-info" data-k="staf-ket">Laci menu owner (uang, laporan, harga, setelan) tidak termasuk hak ${namaP}. Server menegakkan: baca & catat baru; koreksi, hapus, dan "minta owner" tertutup sampai alur persetujuan ada.</div>
    </section>`;
  }
  function gambarLaci(s, d, L) {
    const pita = M.susunPita(d, s.bagian); const laci = M.susunLaci(d, L);
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
    return h`<div class="mn-grup" data-k="g-tanya">${M.susunTanya(d).map((t) => h`<div class="mn-tanya ${s.buka === t.id ? 'buka' : ''}" data-k="t-${t.id}" data-aksi="baris" data-id="${t.id}">
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
      ${s.atur ? gambarAtur(s) : s.sistem === 'perangkat' ? gambarPerangkat(s, d, tab) : s.sistem === 'peran' ? gambarPeran(s, d, tab) : s.sistem === 'cadangan' ? gambarCadangan(s, d) : s.sistem === 'lokasi' ? gambarLokasi(s, d, tab) : gambarPengingat(s, d, tab)}
    </section>`;
  }
  const pintuAtur = (judul, ringkas) => h`<div class="at-pintu" data-k="pintu-atur" data-aksi="bukaAtur"><div><div style="font-weight: 600;">${judul}</div><div class="ket" style="font-size: 10.5px;">${ringkas}</div></div><div class="ket">ubah ›</div></div>`;
  function gambarPerangkat(s, d, tab) {
    const L = lokal(); const P = S.ssPerangkat(d, L.antre, L.idPerangkat); const pilih = P.daftar.find((x) => x.id === s.pilihP) || P.daftar.find((x) => x.ini) || null;
    if (tab === 'antrean') return h`<div class="kartu" data-k="antre" style="gap: 6px;"><div style="font-weight: 700;">${P.nAntre ? P.nAntre + ' catatan perangkat ini menunggu server' : 'Antrean perangkat ini kosong'}</div>
        ${P.antre.map((q) => h`<div class="pr-antre ${q.terlalu ? 'lama' : ''}" data-k="q-${q.koleksi}-${q.id}"><span class="j">${q.jam}</span><span>${q.nama}${q.ringkas ? ' · ' + q.ringkas : ''} <span class="pr-cap ${q.terlalu ? 'awas' : ''}">${q.terlalu ? q.lama + ' menit' : 'menunggu'}</span></span></div>`)}
        <div class="ket">Catatan yang belum sampai disimpan Firestore di perangkat ini dan dikirim SENDIRI begitu tersambung — tidak ada tombol kirim yang perlu ditekan, dan tidak ada yang bisa dibuang dari sini. Dua perangkat menulis catatan yang sama: yang terakhir ditulis yang dipakai; keduanya tercatat di Jejak.</div>
        <div class="kaca-btn aktif" data-aksi="periksaSambung">${s.sambungTeks || 'Periksa: sudah sampai semua?'}</div>
        ${P.lainAntre ? h`<div class="ket awas-teks">${P.lainAntre} catatan menunggu di perangkat LAIN menurut denyut terakhirnya — hanya perangkat itu yang bisa mengirimnya.</div>` : ''}</div>
      ${(() => { const AL = opsi.antreLokal ? opsi.antreLokal() : { belum: [], ditolak: [] }; const owner = !opsi.akun || !opsi.akun() || opsi.akun().jenis === 'owner';
        return h`<div class="kartu ${AL.ditolak.length ? 'awas' : ''}" data-k="ditolak-server" style="gap: 6px;"><div style="font-weight: 700;">${AL.ditolak.length ? AL.ditolak.length + ' kiriman DITOLAK SERVER' : 'Tidak ada kiriman yang ditolak server'}</div>
          <div class="k2">Salinan tiap kiriman disimpan di perangkat ini sampai server mengaku (${AL.belum.length} masih menunggu). Yang ditolak (mis. akunnya dinonaktifkan saat perangkat offline) tidak hilang — tampil di sini sampai owner memutuskan.</div>
          ${AL.ditolak.map((x) => { const kp = kpAlasanDitolak(x, (k, i) => !!dokDiCache(k, i)); return h`<div class="pr-antre lama" data-k="dt-${x.id}"><span class="j">${jamSetempat(x.padaTolak || x.pada)}</span><span>${x.akunNama} (${x.peran || '?'}) · ${(x.dokumen || []).map((d) => d.koleksi).join(', ')} <div class="k2">${(x.dokumen || []).length} dokumen · alasan: ${kp ? kp.kalimat : (x.alasan || '-')}</div>
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
      ${!P.daftar.length ? h`<div class="ket">Denyut ditulis tiap perangkat yang masuk (sistem lama & baru) paling cepat sekali per menit. Kalau daftar ini kosong padahal HP sedang dipakai, aturan Firestore untuk koleksi perangkatStatus belum terpasang.</div>` : ''}</div>
      ${pilih && pilih.ini ? h`<div class="kartu" data-k="panel-ini" style="gap: 6px;"><div style="font-weight: 700;">Perangkat ini</div>
        <div class="label">Nama perangkat ini</div><div style="display: flex; gap: 6px;"><input class="ketik-nama" type="text" placeholder="${L.namaPerangkat || 'mis. iPhone owner, Mac toko'}" value="${s.namaBaru || ''}" data-ketik="namaiPerangkat"><div class="kaca-btn aktif" style="min-width: 84px;" data-aksi="namaiSimpan">simpan</div></div>
        <div class="label">Yang mencatat di perangkat ini</div><div class="pita-info" data-k="masuk-sebagai">Masuk sebagai: <b>${(() => { const a = opsi.akun ? opsi.akun() : null; return a ? (a.jenis === 'owner' ? 'Owner' : a.nama + ' (' + ((S.SS_PERAN.find((p) => p.id === a.peran) || {}).nama || a.peran) + ')') : 'Owner'; })()}</b></div>
        <div class="k2">Catatan membawa nama & uid akun yang MASUK — bukan pilihan di perangkat. Ganti orang = Keluar lalu masuk dengan akunnya sendiri (tombol Keluar di pojok atas).</div></div>` : pilih ? h`<div class="kartu" data-k="panel-lain" style="gap: 4px;"><div style="font-weight: 700;">${pilih.nama}</div><div class="k2">${pilih.denyutTeks} · ${pilih.aplikasi}</div><div class="k2">Antrean & pemegang perangkat lain hanya bisa diubah dari perangkat itu sendiri.</div></div>` : ''}
      ${pintuAtur('Atur batas antrean, denyut & pencatat', 'antrean lama ' + P.atur.batasAntre + ' menit · denyut lama ' + P.atur.batasDenyut + ' menit · ' + P.atur.pemegang.length + ' pencatat')}`;
  }
  function gambarPeran(s, d, tab) {
    const P = S.ssPeran();
    if (tab === 'minta') { const Q = S.ssPersetujuan(d); const m = Q.menunggu.find((x) => x.id === s.mintaKe) || null; return h`<div class="ket" data-k="judul-minta" style="font-size: 11.5px;">${Q.judul}</div>
      <div style="display: flex; flex-direction: column; gap: 6px;" data-k="minta">${Q.menunggu.map((x) => h`<div class="pn-minta ${m && m.id === x.id ? 'aktif' : ''}" data-k="m-${x.id}" data-aksi="mintaKe" data-id="${x.id}"><div style="display: flex; justify-content: space-between; gap: 8px;"><b style="font-size: 12.5px;">${x.dari} · ${x.jam}</b><span class="n">${x.n ? RP(x.n) : ''}</span></div><div style="font-size: 12px;">${x.teks}</div><div class="k2">${x.modul} · ${x.namaTindakan}</div></div>`)}</div>
      ${m ? h`<div class="kartu" data-k="putus" style="gap: 6px;"><div class="k2">${m.saran}</div><input class="ketik-nama" type="text" placeholder="Alasan kalau menolak (wajib)" value="${s.alasan}" data-ketik="alasan"><div class="pn-dua"><div class="kaca-btn aktif emas" data-aksi="setujui">SETUJUI</div><div class="kaca-btn awas" data-aksi="tolak">tolak</div></div></div>` : ''}
      ${Q.menunggu.length ? h`<div class="kaca-btn" data-k="kecil" data-aksi="setujuiKecil">setujui semua yang kecil (≤ ${RP(Q.batas)}) · ${Q.kecil}</div>` : ''}
      ${Q.riwayat.length ? h`<div class="kartu" data-k="riwayat" style="gap: 2px;"><div class="label">Keputusan sebelumnya</div>${Q.riwayat.map((x) => h`<div class="k2" data-k="r-${x.id}">${tanggalPendek(x.diputusTanggal)} · ${x.status.toUpperCase()}: ${x.teks} (${x.dari})${x.alasanTolak ? ' · ' + x.alasanTolak : ''}</div>`)}</div>` : ''}
      ${pintuAtur('Atur batas setujui sekaligus & jatah nego', 'sekaligus ≤ ' + RP(P.batasSekaligus) + ' · jatah nego Ben ' + P.jatahBen + '% margin')}`; }
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
      <div class="ket" data-k="ket-peran" style="font-size: 11px;">Tiga peran: owner (semua), Ben (penjaga laci), karyawan. "Tidak boleh" = tombolnya mati di tablet; "minta owner" = masuk papan persetujuan (alurnya belum ada, jadi sekarang tertutup); menolak wajib alasan. "Tertutup server" = di kisi lu bilang boleh, tapi aturan server (firestore.rules) belum membukanya untuk peran itu — sebabnya tertulis di bawah nama tindakan.</div>
      ${pintuAtur('Atur batas setujui sekaligus & jatah nego', 'sekaligus ≤ ' + RP(P.batasSekaligus) + ' · jatah nego Ben ' + P.jatahBen + '% margin')}`;
  }
  function gambarCadangan(s, d) {
    const C = S.ssCadangan(d, lokal(), s.hariC);
    return h`<div class="kartu" data-k="kuota" style="gap: 6px;"><div class="label">Simpanan lokal di perangkat ini</div>
        ${C.kuota.adaAngka ? h`<div class="cd-bar ${C.kuota.awas ? 'awas' : ''}"><div style="width: ${Math.min(100, C.kuota.pct)}%;"></div></div>` : ''}<div class="k2">${C.kuota.teks}${C.kuota.ket ? ' · ' + C.kuota.ket : ''}</div>${C.kuota.awasTeks ? h`<div class="pita-info ${C.kuota.awas ? 'awas' : ''}" style="font-size: 11.5px;">${C.kuota.awasTeks}</div>` : ''}
        ${C.simpanan.adaAngka ? h`<div class="k2">Simpanan Firestore di perangkat (IndexedDB): ${ANGKA(C.simpanan.kb)} KB${C.simpanan.quotaKb ? ' dari jatah peramban ' + ANGKA(Math.round(C.simpanan.quotaKb / 1024)) + ' MB (' + C.simpanan.pct + '%)' : ''} — dibersihkan Firestore sendiri, tidak perlu dirapikan.</div>` : ''}
        <div class="cd-angka">${C.sehat.map((x) => h`<div data-k="s-${x.t}">${x.t}<b>${x.n}</b></div>`)}</div></div>
      <div class="ket" data-k="ringkas-c" style="font-size: 11.5px;">${C.ringkas}</div>
      <div class="utama" data-k="unduh" data-aksi="unduhCadangan">UNDUH CADANGAN SEKARANG</div>
      <div class="ket" data-k="ket-unduh" style="font-size: 11px;">Berkas JSON yang sama bentuknya dengan cadangan sistem lama (versi 5) + koleksi sistem baru, bercap era tutup buku${C.era ? ' (tahun ' + C.era + ')' : ' (belum pernah tutup buku)'}. Yang diunduh adalah salinan di perangkat ini — kalau ada catatan yang belum sampai server, isinya tetap ikut.</div>
      <div class="kartu" data-k="kal" style="gap: 6px; padding: 10px 12px;"><div class="cd-kal">${C.kalender.map((k) => h`<div class="cd-hari ${k.aktif ? 'aktif' : ''} ${k.ini ? 'ini' : ''}" data-k="k-${k.iso}" data-aksi="hariC" data-iso="${k.iso}"><span class="nm">${k.nm}</span><b>${k.tgl}</b><span class="t ${k.keadaan}"></span></div>`)}</div><div class="k2">● emas = ada cadangan hari itu · kosong = tidak ada</div></div>
      <div class="kartu" data-k="hari-c" style="gap: 2px;"><div class="label">${C.hariJudul}</div>${C.hariDaftar.map((c) => h`<div class="cd-baris" data-k="c-${c.id}"><div><div style="font-weight: 600;">${c.jam ? c.jam + ' · ' : ''}${c.nama}</div><div class="k2">${c.sumber}${c.perangkat ? ' · ' + c.perangkat : ''}${c.kb ? ' · ' + ANGKA(c.kb) + ' KB · ' + ANGKA(c.dokumen) + ' catatan' : ''}</div></div><span class="cd-cap ${c.ok ? 'ok' : 'awas'}">${c.jenis}</span></div>`)}</div>
      <div class="ket" data-k="ket-c" style="font-size: 11px;">Sistem baru tidak memakai cadangan localStorage; jalan tanpa internet ditanggung simpanan Firestore. Angka kuota di atas mengukur simpanan lokal SISTEM LAMA di alamat yang sama — memenuhinya membuat layar sistem lama diam. Memulihkan dari berkas tetap lewat Setelan sistem lama (keputusan owner, dua kali cadangan).</div>
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
        <div class="lk-lapor"><div>stok<b>${l.kg ? ANGKA(Math.round(l.kg)) + ' kg' : '—'}</b></div><div>nilai rak<b>${l.kg ? RP(l.nilai) : '—'}</b></div><div>omzet hari ini<b>${l.omzetHari ? RP(l.omzetHari) : 'belum ada'}</b></div><div>nota hari ini<b>${l.notaHari}</b></div><div>omzet bulan ini<b>${l.omzetBulan ? RP(l.omzetBulan) : 'belum ada'}</b></div><div>perangkat<b>${l.perangkat.length ? l.perangkat.join(', ') : '—'}</b></div></div>
        ${l.merek.slice(0, 8).map((m) => h`<div style="display: flex; justify-content: space-between; font-size: 12px;" data-k="lm-${m.nama}"><span>${m.nama}</span><span class="k2">${ANGKA(Math.round(m.kg))} kg</span></div>`)}${l.kosong ? h`<div class="k2">belum ada catatan di lokasi ini</div>` : ''}</div>`)}`;
    const pilih = LK.daftar.find((l) => l.id === s.lokasiPilih) || LK.utama;
    return h`<div style="display: flex; flex-direction: column; gap: 6px;" data-k="kartu-l">${LK.daftar.map((l) => { const lp = lapor.lapor.find((x) => x.id === l.id) || {}; return h`<div class="lk-kartu ${pilih.id === l.id ? 'aktif' : ''}" data-k="l-${l.id}" data-aksi="lokasiPilih" data-id="${l.id}"><b>${l.nama}${l.utama ? h`<span class="lk-cap">utama</span>` : ''}${(L.lokasi || LK.utama.id) === l.id ? h`<span class="lk-cap">perangkat ini</span>` : ''}</b><div class="k2">${l.alamat || 'alamat belum diisi (Atur)'}</div><div class="k2">${lp.kg ? ANGKA(Math.round(lp.kg)) + ' kg · ' + RP(lp.nilai) : 'belum ada stok'} · ${lp.perangkat && lp.perangkat.length ? lp.perangkat.join(', ') : 'tidak ada perangkat berdenyut di sini'}</div></div>`; })}</div>
      <div class="kartu" data-k="panel-l" style="gap: 6px;"><div style="font-weight: 700;">${pilih.nama}</div>
        <div class="kaca-btn ${(L.lokasi || LK.utama.id) === pilih.id ? 'aktif' : ''}" data-aksi="lokasiIni" data-id="${pilih.id}">${(L.lokasi || LK.utama.id) === pilih.id ? 'perangkat ini mencatat di sini' : 'perangkat ini mencatat di sini →'}</div>
        <div class="kaca-btn ${pilih.utama ? 'mati' : 'aktif'}" data-aksi="jadikanUtama" data-id="${pilih.id}">${pilih.utama ? 'lokasi utama' : 'jadikan lokasi utama'}</div>
        <div class="k2">Fondasi: tiap catatan membawa lokasi perangkat yang mencatatnya (kolom lokasi). Catatan lama tanpa kolom itu dihitung di lokasi utama. Mesin stok & laba belum memisahkan per lokasi — laporan per lokasi membaca kolom itu.</div></div>
      ${pintuAtur('Atur daftar lokasi & pengantar', LK.daftar.length + ' lokasi · ' + LK.pengantar.length + ' pengantar')}`;
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
      ${p ? h`<div class="kartu" data-k="panel-g" style="gap: 6px;"><div style="font-weight: 700;">${p.teks} · ${p.sisaTeks}${p.n ? ' · ' + RP(p.n) : ''}</div>${p.selesai ? h`<div class="k2">Sudah selesai${p.catatan ? ' · ' + p.catatan : ''}</div>` : h`<input class="ketik-nama" type="text" placeholder="Catatan (wajib kalau sudah lewat)" value="${s.catatanG}" data-ketik="catatanG"><div class="k2">${p.tundaKali >= G.atur.maksTunda ? 'Sudah ditunda ' + p.tundaKali + ' kali (batas ' + G.atur.maksTunda + ') — harus ditindak' : 'Tunda ' + G.atur.tundaHari + ' hari (' + p.tundaKali + ' dari ' + G.atur.maksTunda + ' kali)'}</div>
        <div class="pg-tiga"><div class="kaca-btn aktif emas" data-aksi="selesaiG">SELESAI</div><div class="kaca-btn" data-aksi="tundaG">tunda</div>${p.jenis === 'janji' ? h`<div class="kaca-btn ${s.yakinWa ? 'awas' : 'aktif'}" data-aksi="waG">${s.yakinWa ? 'YAKIN kirim lagi' : 'kirim WA'}</div>` : ''}</div>`}</div>` : ''}
      <div class="ket" data-k="ket-kal" style="font-size: 11px;">Yang lewat tidak bisa dihapus — diselesaikan dengan catatan, atau ditunda sampai batasnya. "Selesai" di sini tidak mencatat uangnya: bayar bon pemasok tetap di sistem lama, bayar pelanggan di Pelanggan → Bon.</div>
      ${pintuAtur('Atur hari sebelum, lama & batas tunda', 'tunda ' + G.atur.tundaHari + ' hari × ' + G.atur.maksTunda + ' kali · opname tiap ' + G.atur.opnameTiap + ' hari')}`;
  }
  function gambarAtur(s) {
    const a = s.atur; const angka = (k, label, satuan) => h`<div class="at-baris" data-k="at-${k}"><div>${label}</div><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${a[k]}" data-ketik="aturKetik" data-kolom="${k}"><span class="k2">${satuan}</span></div>`;
    const daftar = (k, label, contoh) => h`<div class="label" style="margin-top: 4px;">${label}</div>${a[k].map((x, i) => h`<div class="at-baris" data-k="at-${k}-${i}"><input class="ketik-nama" type="text" placeholder="${contoh}" value="${x}" data-ketik="aturKetik" data-kolom="${k}" data-i="${i}"><span class="mn-x" data-aksi="aturLepas" data-daftar="${k}" data-i="${i}">×</span></div>`)}<div class="kaca-btn putus" data-aksi="aturTambah" data-daftar="${k}">＋ tambah</div>`;
    return h`<div class="kartu" data-k="atur-${a.id}" style="gap: 8px;"><div class="serif" style="font-size: 18px;">Atur sendiri · ${JUDUL_SISTEM[a.id]}</div>
      ${a.id === 'perangkat' ? [angka('batasAntre', 'Antrean dianggap lama', 'menit'), angka('batasDenyut', 'Denyut dianggap lama', 'menit'), daftar('pemegang', 'Boleh mencatat di perangkat (Owner tak terhapus)', 'nama orang')]
      : a.id === 'peran' ? [angka('batasSekaligus', 'Batas setujui sekaligus', 'rupiah'), angka('jatahBen', 'Jatah nego Ben', '% margin')]
      : a.id === 'cadangan' ? [angka('cadanganTiap', 'Ingatkan cadangan tiap', 'hari'), angka('simpanHari', 'Simpan catatan cadangan', 'hari'), angka('ambangKuota', 'Ambang kuota simpanan lokal', '%')]
      : a.id === 'lokasi' ? [h`<div class="label">Lokasi (tepat satu utama)</div>`, a.daftar.map((l, i) => h`<div class="at-lokasi" data-k="at-l-${i}"><input class="ketik-nama" type="text" placeholder="nama lokasi (cabang, gudang)" value="${l.nama}" data-ketik="aturKetik" data-kolom="daftar" data-i="${i}" data-sub="nama"><input class="ketik-nama" type="text" placeholder="alamat (boleh kosong)" value="${l.alamat}" data-ketik="aturKetik" data-kolom="daftar" data-i="${i}" data-sub="alamat"><div class="seg ${l.utama ? 'aktif' : ''}" data-aksi="aturUtama" data-i="${i}">${l.utama ? 'utama' : 'jadikan utama'}</div><span class="mn-x" data-aksi="aturLepas" data-daftar="daftar" data-i="${i}">×</span></div>`), h`<div class="kaca-btn putus" data-aksi="aturTambah" data-daftar="daftar">＋ tambah lokasi</div>`, daftar('pengantar', 'Pengantar pindah stok', 'nama pengantar')]
      : [angka('hariBon', 'Bon pemasok: ingatkan', 'hari sebelum'), angka('hariJanji', 'Janji bayar: ingatkan', 'hari sebelum'), angka('hariKantong', 'Kantong: ingatkan', 'hari sebelum habis'), angka('hariOpname', 'Opname: ingatkan', 'hari sebelum'), angka('opnameTiap', 'Opname rutin tiap', 'hari'), angka('hariCadangan', 'Cadangan: ingatkan', 'hari sebelum'), angka('tundaHari', 'Lama tunda', 'hari'), angka('maksTunda', 'Batas tunda', 'kali')]}
      <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN ATURAN</div></div></div>`;
  }

  K.dengar(gambar);
  dengarkan(() => gambar());
  return { keadaan: K, belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan, gambar, buka: (sistem, tab) => { set({ sistem: sistem || null, tabS: Object.assign({}, st().tabS, sistem && tab ? { [sistem]: tab } : {}), kabar: '' }); if (sistem) ukurSimpanan(); },
    tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); ukurSimpanan(); } if (tampil) gambar(); } };
}
