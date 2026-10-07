// SISTEM BARU — pintu masuk. Putaran 1 (19 Sep 2026): layar JUAL membaca data toko yang sama dengan index.html.
// Sumber data: Firestore toko (bawaan) atau berkas cadangan (?cadangan=…/backup-batch-….json, untuk mencoba di komputer).
import { pasangLayarJual } from './layar/jual.js';
import { pasangLayarRingkasan } from './layar/ringkasan.js';
import { pasangLayarStok } from './layar/stok.js';
import { pasangLayarPelanggan } from './layar/pelanggan.js';
import { pasangLayarMenu } from './layar/menu.js';
import { pasangLayarHarga } from './layar/harga.js';
import { pasangLayarUang } from './layar/uang.js';
import { pasangLayarLaporan } from './layar/laporan.js';
import * as fb from './data/firebase.js';
import { muatCadangan } from './data/cadangan.js';
import { dengarkan, sumberData } from './data/toko.js';
import { bolehLayar, bisaBekerja, teksMasukSebagai } from './data/akses.js';
import { ssAtur } from './layar/sistem-logika.js';
// owner 7 Okt (JS2-C): jatah nego akun yang masuk ikut ke penjaga kiriman
import { ngJatah } from './layar/nego-logika.js';
import { terkunci, setelKunci } from './inti/kunci.js';
import { kalimatKeranjangKeluar } from './layar/jual-logika.js';
import { kalimatIsianKeluar } from './inti/isian.js';
import { pjSumberPengingat } from './layar/pajak-logika.js';
import { nanti, setelMuat } from './inti/jadwal.js';
import { pasangGerbang } from './inti/gerbang.js';   // gerbang masuk G4 (dikunci owner 29 Sep 2026)   // owner 29 Sep: lag & freeze — gambar ulang digabung sekali per bingkai

const q = new URLSearchParams(location.search);
const KUNCI_MODE = 'miqbal_baru_mode';
let mode = (() => { try { return localStorage.getItem(KUNCI_MODE) || 'terang'; } catch (e) { return 'terang'; } })();
let versi = 0;
let statusFb = { masuk: false, akun: null, koleksiSiap: 0, koleksiTotal: 0, offline: false, galat: '', ditolak: [], lokal: { belum: 0, ditolak: 0 } };
// akun yang masuk (putaran 23). Mode cadangan tidak masuk ke Firebase: dianggap owner (tulisan cuma simulasi di memori).
const akunKini = () => (sumberData().jenis === 'cadangan' ? { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: '' } : statusFb.akun);
fb.setelSumberHak(() => { const a = statusFb.akun; if (!a || !a.peran || a.peran === 'owner') return {}; try { return Object.assign({}, (ssAtur('peran').hak || {})[a.peran] || {}, { jatahNego: ngJatah(a) }); } catch (e) { return {}; } });

// Kelas gelap juga di <html>: Safari iOS 26/27 mewarnai daerah poni/jam dari warna dasar & color-scheme elemen akar,
// bukan dari theme-color — tanpa ini poninya putih di mode gelap. theme-color ikut diganti untuk peramban lain.
function terapkanMode() {
  const gelap = mode === 'gelap';
  document.body.classList.toggle('gelap', gelap);
  document.documentElement.classList.toggle('gelap', gelap);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = gelap ? '#111516' : '#eef1f4';
}
function gantiMode() { mode = mode === 'gelap' ? 'terang' : 'gelap'; try { localStorage.setItem(KUNCI_MODE, mode); } catch (e) { /* abaikan */ } terapkanMode(); layar.gambar(); ringkasan.gambar(); stok.gambar(); pelanggan.gambar(); menu.gambar(); harga.gambar(); uang.gambar(); }
function statusTeks() {
  const s = sumberData();
  if (s.jenis === 'cadangan') return 'membaca cadangan (bukan data hidup)';
  if (!statusFb.masuk) return 'belum masuk';
  if (statusFb.ditolak && statusFb.ditolak.length) return 'koleksi ditolak server: ' + statusFb.ditolak.join(', ');
  if (statusFb.galat) return 'ada yang ditolak: ' + statusFb.galat;
  if (statusFb.koleksiSiap < statusFb.koleksiTotal) return 'memuat ' + statusFb.koleksiSiap + '/' + statusFb.koleksiTotal + ' koleksi';
  if (statusFb.menunggu > 0) return 'menunggu server mengaku ' + statusFb.menunggu + ' catatan';
  return statusFb.offline ? 'TANPA INTERNET — angka dari simpanan perangkat, catatan mengantre' : 'tersambung · ' + statusFb.koleksiTotal + ' koleksi';
}

// Jual (rapi-rapi 29 Sep): pita peringatan di bawah judul hanya untuk keadaan yang harus terlihat — tanpa internet atau koleksi ditolak server.
// Normal, memuat, dan menunggu server mengaku (sekejap tiap mencatat) cukup di teks kepala: pita yang muncul-hilang menggeser seluruh layar.
function statusAwas() {
  if (sumberData().jenis !== 'firestore' || !statusFb.masuk) return '';
  if ((statusFb.ditolak && statusFb.ditolak.length) || statusFb.galat) return statusTeks();
  return statusFb.offline ? 'TANPA INTERNET — angka dari simpanan perangkat, catatan mengantre' : '';
}
// Pil di kepala tiap layar (owner 24 Sep: bilah "Masuk sebagai … · Keluar" di atas layar dicabut, pindah ke pil ini; "DATA TOKO" → nama akun).
// Isinya: akun yang masuk (OWNER / nama orang), ditambah keadaan kiriman bila tidak normal. Ketuk = lembar akun (Masuk sebagai + Keluar).
const labelAkun = () => { const a = akunKini(); return !a || !bisaBekerja(a) ? 'DATA TOKO' : a.jenis === 'owner' ? 'OWNER' : String(a.nama || a.email || '').toUpperCase(); };
// Nama yang masuk SELALU di depan (owner 24 Sep) — juga saat memuat; keadaan tambahan menyusul di belakangnya (terpotong duluan kalau sempit).
function statusRingkas() {
  const belum = (statusFb.lokal || {}).belum || 0; const tolak = (statusFb.lokal || {}).ditolak || 0;   // 39b no. 28: kiriman yang ditolak server tampil di pil SETIAP layar
  const kirim = statusFb.offline ? ' · tanpa internet' : statusFb.menunggu > 0 ? ' · menunggu server' : belum ? ' · ' + belum + ' belum terkirim' : '';
  // hemat baca nyala (owner 7 Okt): statusFb.hematPil menyebut data yang belum terperiksa dengan server / tab yang harus dimuat ulang; mati = tidak ada (pil sama)
  const tambah = statusFb.koleksiSiap < statusFb.koleksiTotal && !statusFb.offline ? ' · memuat…' : (tolak ? ' · ' + tolak + ' DITOLAK server' : '') + kirim + (statusFb.hematPil || '');
  return labelAkun() + tambah;
}

terapkanMode();
const akar = document.getElementById('layar');
const layar = pasangLayarJual(akar, { akun: () => akunKini(), gantiMode, mode: () => mode, statusTeks, statusAwas, statusRingkas, versiData: () => versi, pemegang: () => fb.pemegangPerangkat(),
  bukaStok: (lembar, tab, isi) => { pindah('stok'); stok.buka(lembar, tab, isi); } });   // putaran 25: pembalik karcis bulan terkunci → Stok › Cocokkan · 27: Isi barang habis
dengarkan(() => { versi += 1; });

// ---- perpindahan layar: tiap layar punya <main> sendiri yang disembunyikan, supaya keranjang Jual tidak hilang saat pindah ----
const KUNCI_TAB = 'miqbal_baru_tab';
let sekarangCadangan = null;   // mode cadangan: "sekarang" = saat cadangan diunduh
const ringkasan = pasangLayarRingkasan(document.getElementById('layarRingkasan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t),
  keTujuan: (t) => keTujuan(t) });   // putaran 40: ketukan dasbor owner → layar sumber angkanya (keTujuan didefinisikan di bawah; dipanggil sesudah semua layar terpasang)
const stok = pasangLayarStok(document.getElementById('layarStok'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, versiData: () => versi, keranjangJual: () => layar.keadaan.baca(), bukaHarga: (keluarga) => { pindah('harga'); harga.buka(keluarga); } });
const pelanggan = pasangLayarPelanggan(document.getElementById('layarPelanggan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t),
  keTujuan: (t) => keTujuan(t) });   // owner 7 Okt: lembar bon → Kartu piutang berkop di Laporan (keTujuan didefinisikan di bawah; dipanggil saat ketukan)
// Menu (putaran 14): laci N1 + pita jam + Sistem (SS1–SS5). Tujuan baris = layar lain lewat pintu yang sama dengan ketukan di layar itu.
const menu = pasangLayarMenu(document.getElementById('layarMenu'), { gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t),
  bukaStok: (lembar, tab) => { pindah('stok'); stok.buka(lembar, tab); }, bukaPelanggan: (keluarga, orang) => { pindah('pelanggan'); pelanggan.buka(keluarga, orang); }, bukaHarga: (keluarga, t) => { pindah('harga'); harga.buka(keluarga, t); }, bukaUang: (keluarga, t) => { pindah('uang'); uang.buka(keluarga, t); }, bukaLaporan: (keluarga, t) => { pindah('laporan'); laporan.buka(keluarga, t); }, bukaJual: (lembar) => { pindah('jual'); layar.keadaan.setel({ lembar, kabar: '' }); },
  lokal: () => ({ antre: statusFb.antre || [], idPerangkat: fb.idPerangkat(), namaPerangkat: fb.perangkatRingkas(), pemegang: fb.pemegangPerangkat(), lokasi: fb.lokasiPerangkat(), koleksiSiap: statusFb.koleksiSiap, koleksiTotal: statusFb.koleksiTotal, offline: statusFb.offline,
    pajak: (() => { const a = akunKini(); if (!a || a.jenis !== 'owner') return []; try { return pjSumberPengingat(sekarangCadangan || new Date()); } catch (e) { console.error('pengingat pajak', e); return []; } })() }),   // putaran 24: pengingat pajak, owner saja
  periksaSambungan: () => fb.periksaSambungan(4000), setelLokasi: (id) => fb.setelLokasi(id), namaiPerangkat: (n) => fb.namaiPerangkat(n),
  akun: akunKini, antreLokal: () => fb.antreLokal(), buangDitolak: (id) => fb.buangDitolak(id), tulisUlangDitolak: (id, ubah) => fb.tulisUlangDitolak(id, ubah),
  // hemat baca (owner 7 Okt 2026): Menu › Toko ini › Perangkat & antrean › Hemat baca — keadaan, daftar siap-nyala, saklar perangkat ini, tombol baca penuh
  hemat: () => fb.hematKeadaan(), hematSiap: () => fb.hematSiapNyala(), setelSaklarHemat: (v) => fb.setelSaklarHemat(v), hematBacaPenuh: (sebab) => fb.hematBacaPenuh(sebab),
  hematMintaSemua: () => fb.hematMintaSemua(), muatUlang: () => location.reload() });
// Harga & Pemasok (putaran 17): layar keenam, dibuka dari Menu (baris Pemasok & utang · Katalog harga · cari) dan Stok → Gudang → "Apa yang harus dibeli"; di Mac ada di menu samping.
const harga = pasangLayarHarga(document.getElementById('layarHarga'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t),
  bukaStok: (lembar, tab, isi) => { pindah('stok'); stok.buka(lembar, tab, isi); },   // putaran 27: Isi barang habis dari katalog
  // owner 7 Okt: foto bon pemasok — koleksi fotoBon dibaca sekali saat bon dibuka (tidak didengar); di mode cadangan = simulasi di memori layar
  foto: { ada: () => sumberData().jenis === 'firestore', baca: (idBon) => fb.bacaFotoBon(idBon), simpan: (d) => fb.simpanFotoBon(d), hapus: (id, idBon) => fb.hapusFotoBon(id, idBon) },
  keTujuan: (t) => keTujuan(t) });   // putaran 29: "catat isi rekening dulu" dari lembar bayar bon → Uang › Pindah uang (keTujuan didefinisikan di bawah; dipanggil saat ketukan)
// Uang (putaran 18): layar ketujuh — Uang keluar · Orang & upah · Owner & toko · Pindah uang · Tutup hari · Tutup buku. Dibuka dari Menu; di Mac ada di menu samping.
// putaran 25: daftar periksa Kunci bulan membaca kiriman tertahan/ditolak di perangkat ini + nota yang diparkir di Jual (keadaan lokal, bukan server)
const parkirJual = () => { try { const k = layar.keadaan.baca(); return (k.antrean || []).filter((a) => a.id !== k.aktifId).map((a) => ({ pada: (a.beku || {}).pada || null, pelanggan: (a.beku || {}).pelanggan || '', n: (((a.beku || {}).items) || []).length })); } catch (e) { return []; } };
const lokalPerangkat = () => ({ antre: statusFb.antre || [], menunggu: statusFb.menunggu || 0, idPerangkat: fb.idPerangkat(), namaPerangkat: fb.perangkatRingkas(), pemegang: fb.pemegangPerangkat(), offline: statusFb.offline,
  // Paket C (7 Okt): kartu "Pemeriksaan sesudah tutup buku" — koleksi yang belum dimuat / ditolak server = "belum bisa diperiksa", bukan lulus
  koleksiSiap: statusFb.koleksiSiap, koleksiTotal: statusFb.koleksiTotal, ditolak: statusFb.ditolak || [],
  antreLokal: (() => { try { return fb.antreLokal(); } catch (e) { return { belum: [], ditolak: [] }; } })(), parkir: parkirJual(),
  // owner 7 Okt: tutup buku butuh baca penuh sesi ini saat hemat baca nyala. #111 × Paket C: `hemat.belumLengkap` (SATU sumber hemat-baca.js hbBelumLengkap) →
  // uang.js muatData → pstKurang (kartu pemeriksaan sesudah tutup buku "?"), daftar periksa kunci bulan, perkiraan kuota, Lanjutkan/Batalkan tutup buku
  hemat: (() => { try { return fb.hematKeadaan(); } catch (e) { return { nyala: false }; } })() });
const uang = pasangLayarUang(document.getElementById('layarUang'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t), lokal: lokalPerangkat,
  bukaStok: (lembar, tab, isi) => { pindah('stok'); stok.buka(lembar, tab, isi); } });   // putaran 39: kartu Cek wadah K5 → Stok › Wadah literan
// Laporan & Dokumen (putaran 19): layar kedelapan — Laba · Harian · Bulanan · Neraca · Dokumen (berkop, paket bank, dokumen kecil) · Setelan (kop & identitas). Dibuka dari Menu; di Mac ada di menu samping.
// keTujuan = satu pintu ke layar lain dengan bentuk tujuan yang sama dengan baris Menu ({ ke, keluarga, tab, lembar, sistem }).
const keTujuan = (t) => { if (!t) return; if (t.ke === 'stok') { pindah('stok'); stok.buka(t.lembar || null, t.tab || null); } else if (t.ke === 'pelanggan') { pindah('pelanggan'); pelanggan.buka(t.keluarga || 'kenali', t.orang || null); } else if (t.ke === 'harga') { pindah('harga'); harga.buka(t.keluarga || 'katalog', t); } else if (t.ke === 'uang') { pindah('uang'); uang.buka(t.keluarga || 'keluar', t); } else if (t.ke === 'laporan') { pindah('laporan'); laporan.buka(t.keluarga || 'laba', t); } else if (t.ke === 'sistem') { pindah('menu'); menu.buka && menu.buka(t.sistem || 'perangkat', t.tab || null); } else if (t.ke === 'jual' && t.lembar) { pindah('jual'); layar.keadaan.setel({ lembar: t.lembar, kabar: '' }); } else pindah(t.ke); };
// hemat baca nyala (#111): Laporan › Pajak menahan rekap konsultan & catat setoran selama data pajak di perangkat ini belum lengkap (SATU sumber firebase.js hematKeadaan)
const laporan = pasangLayarLaporan(document.getElementById('layarLaporan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t), keTujuan,
  hemat: () => { try { return fb.hematKeadaan(); } catch (e) { return { nyala: false }; } } });
const LAYAR_ADA = { jual: akar, ringkasan: document.getElementById('layarRingkasan'), stok: document.getElementById('layarStok'), pelanggan: document.getElementById('layarPelanggan'), menu: document.getElementById('layarMenu'), harga: document.getElementById('layarHarga'), uang: document.getElementById('layarUang'), laporan: document.getElementById('layarLaporan') };
// GERAK PINDAH LAYAR (owner 29 Sep: "lebih hidup, lebih intuitif — dari segi motion terutama"): layar baru datang dari ARAH tab yang dituju
// (kanan = tab sesudahnya, kiri = sebelumnya) dan penanda menu meluncur ke tab aktif — orang merasa di mana ia berada.
const URUT_TAB = ['ringkasan', 'stok', 'jual', 'pelanggan', 'menu', 'harga', 'uang', 'laporan'];
let tabKini = null;
// Web Animations pada ANAK <main> (lihat gerak.css §1): animasi CSS dasar anak tidak disentuh, jadi tidak ada yang terputar ulang sesudahnya.
const DATANG_KECUALI = '.latar-bola, .jual-keranjang, .lembar, .tetes-terbang, input';
function datangkan(el, dari, ke) {
  if (!el || dari === ke || !dari || typeof el.animate !== 'function') return;
  if (typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const geser = URUT_TAB.indexOf(ke) > URUT_TAB.indexOf(dari) ? 26 : -26; let i = 0;
  Array.from(el.children).forEach((c) => {
    if (c.matches(DATANG_KECUALI)) return;
    c.animate([{ opacity: 0, transform: 'translateX(' + geser + 'px)' }, { opacity: 1, transform: 'none' }], { duration: 380, delay: Math.min(120, i * 30), easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'backwards' });
    i += 1;
  });
}
/** Penanda (pil emas) di bawah petak aktif: menu bawah (HP/tablet) & menu samping (Mac). Diukur dari petaknya → ikut lebar layar. */
function geserPenanda() {
  const nav = document.querySelector('.nav'); const side = document.querySelector('.side');
  const pasangDi = (wadah, aktif, sumbu) => {
    if (!wadah) return; let p = wadah.querySelector(':scope > .penanda');
    if (!p) { p = document.createElement('span'); p.className = 'penanda'; p.setAttribute('aria-hidden', 'true'); wadah.prepend(p); }
    if (!aktif || aktif.hidden || !aktif.offsetParent) { p.classList.remove('ada'); return; }
    const sasaran = sumbu === 'y' ? (aktif.querySelector('.ikon') || aktif) : aktif;
    const wr = wadah.getBoundingClientRect(); const r = sasaran.getBoundingClientRect();
    p.style.setProperty('--x', Math.round(r.left - wr.left + (wadah.scrollLeft || 0)) + 'px'); p.style.setProperty('--y', Math.round(r.top - wr.top + (wadah.scrollTop || 0)) + 'px');
    p.style.setProperty('--w', Math.round(r.width) + 'px'); p.style.setProperty('--h', Math.round(r.height) + 'px');
    if (!p.classList.contains('ada')) { p.classList.add('diam'); void p.offsetWidth; p.classList.add('ada'); requestAnimationFrame(() => p.classList.remove('diam')); }
  };
  pasangDi(nav, nav && nav.querySelector('[data-tujuan].aktif'), 'x');
  pasangDi(side, side && side.querySelector('.item[data-tujuan].aktif'), 'y');
}
window.addEventListener('resize', () => nanti(geserPenanda));
function pindah(tujuan) {
  if (!LAYAR_ADA[tujuan]) return false;
  const a = akunKini(); if (a && bisaBekerja(a) && !bolehLayar(a, tujuan)) { kabarSebentar('Layar ini tidak termasuk hak ' + teksMasukSebagai(a) + '.'); return true; }
  const dari = tabKini; tabKini = tujuan;
  Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].hidden = k !== tujuan; });
  document.querySelectorAll('[data-tujuan]').forEach((el) => el.classList.toggle('aktif', el.dataset.tujuan === tujuan || ((tujuan === 'harga' || tujuan === 'uang' || tujuan === 'laporan') && el.dataset.tujuan === 'menu' && el.closest('nav'))));   // Harga & Pemasok / Uang tidak punya petak di nav bawah: petak Menu yang menyala (pintunya)
  document.body.classList.toggle('di-jual', tujuan === 'jual');
  layar.tampilkan(tujuan === 'jual'); ringkasan.tampilkan(tujuan === 'ringkasan'); stok.tampilkan(tujuan === 'stok'); pelanggan.tampilkan(tujuan === 'pelanggan'); menu.tampilkan(tujuan === 'menu'); harga.tampilkan(tujuan === 'harga'); uang.tampilkan(tujuan === 'uang'); laporan.tampilkan(tujuan === 'laporan');
  try { localStorage.setItem(KUNCI_TAB, tujuan); } catch (e) { /* abaikan */ }
  window.scrollTo(0, 0);
  datangkan(LAYAR_ADA[tujuan], dari, tujuan); requestAnimationFrame(geserPenanda);
  return true;
}

// ---- masuk PER ORANG (putaran 23). Sandi diketik lalu diteruskan ke Firebase, tidak disimpan & tidak pernah diisi otomatis
//      (readonly sampai diketuk = pengisi-otomatis peramban tidak menempelkan sandi tersimpan; sisanya setelan peramban tablet — putaran tablet). ----
const KUNCI_EMAIL = 'miqbal_baru_email_terakhir';
const modal = document.getElementById('modalMasuk');
const gerbang = pasangGerbang({ gantiMode: () => gantiMode() });
const formMasuk = document.getElementById('formMasuk'), panelAkun = document.getElementById('panelAkun');
const pesanMasuk = document.getElementById('pesanMasuk');
const salahMasuk = document.getElementById('salahMasuk');
const isianEmail = document.getElementById('isianEmail'), isianSandi = document.getElementById('isianSandi'), ingatEmail = document.getElementById('ingatEmail');
const bacaEmail = () => { try { return localStorage.getItem(KUNCI_EMAIL) || ''; } catch (e) { return ''; } };
function kabarSebentar(t) { const k = document.getElementById('kabarNav'); if (k.classList.contains('awas') && !k.hidden) return; k.textContent = t; k.hidden = false; clearTimeout(k._t); k._t = setTimeout(() => { k.hidden = true; }, 3600); }
// 30 Sep: tombol yang jatuh (dom.js delegasi → 'galat-aksi') tidak lagi diam — pita merah bertahan sampai diketuk
// Pita bertahan 20 detik (atau sampai diketuk) — tidak menutupi bilah keranjang selamanya; kabar sebentar lain tidak menimpanya selama tampil.
const pitaGalat = (pesan) => { const k = document.getElementById('kabarNav'); if (!k) return;
  k.textContent = 'Tadi ada yang GAGAL dijalankan (' + (pesan || 'galat') + '). Periksa dulu apakah catatannya sudah masuk sebelum mengulang — ketuk pesan ini untuk menutup.';
  const tutup = () => { k.hidden = true; k.classList.remove('awas'); k.onclick = null; };
  k.classList.add('awas'); k.hidden = false; clearTimeout(k._t); k._t = setTimeout(tutup, 20000); k.onclick = tutup; };
document.addEventListener('galat-aksi', (e) => { const d = (e && e.detail) || {}; pitaGalat(d.pesan); });
// galat yang lahir SESUDAH ketukan (menggambar terjadwal, janji tanpa penangkap) dari modul /baru/ sendiri juga tidak boleh diam
const dariModulKita = (x) => /\/baru\/js\//.test(String((x && (x.stack || x.fileName)) || ''));
window.addEventListener('unhandledrejection', (e) => { if (dariModulKita(e && e.reason)) pitaGalat(String((e.reason && e.reason.message) || e.reason)); });
window.addEventListener('error', (e) => { if (e && (dariModulKita(e.error) || /\/baru\/js\//.test(String(e.filename || '')))) pitaGalat(String(e.message || 'galat')); });
isianSandi.addEventListener('focus', () => { isianSandi.readOnly = false; });
// owner 3 Okt (Safari Mac & iPhone): readonly juga dilepas di pointerdown — jalan SEBELUM fokus, jadi WebKit iOS sudah melihat kolom yang bisa diketik saat
// menimbang papan ketik; 'focus' tetap untuk Tab & fokus lewat kode.
isianSandi.addEventListener('pointerdown', () => { isianSandi.readOnly = false; });
// owner 3 Okt: readonly dipasang lagi HANYA kalau kolom sedang tidak fokus. Mengetuk / mengklik kolom yang sudah fokus tidak memicu 'focus' lagi, jadi
// sesudah sandi salah dikirim lewat Enter (Mac) / Go (iPhone) kolomnya dulu terkunci — ketikan berikutnya tidak masuk sampai pindah kolom lalu kembali.
const kunciSandi = () => { if (document.activeElement !== isianSandi) isianSandi.readOnly = true; };
// owner 3 Okt (iPhone/iPad): tanpa satu pun pendengar sentuh, WebKit iOS mengirim ketukan sebagai klik tiruan — :active (efek membal, gerak.css)
// dipasang lalu dicabut sebelum sempat tergambar. Pendengar pasif: gulir tidak tertahan, perilaku klik tidak berubah. Lewat JS, bukan ontouchstart (CSP).
document.addEventListener('touchstart', () => {}, { passive: true });
document.getElementById('lupakanEmail').addEventListener('click', () => { try { localStorage.removeItem(KUNCI_EMAIL); } catch (e) { /* abaikan */ } isianEmail.value = ''; ingatEmail.hidden = true; isianEmail.focus(); });
/** Gambar layar masuk menurut keadaan akun: keluar → formulir; belum terdaftar / dinonaktifkan / kasir@ → lembar akun; owner / aktif → aplikasi. */
// ---- TIRAI (putaran 23c, owner 24 Sep): belum masuk / belum disetujui / nonaktif / kasir@ → layar di belakang formulir Masuk KOSONG.
//      Setiap <main> dikosongkan dan tidak digambar (layar memeriksa terkunci()); nav & menu samping disembunyikan. Tidak ada angka, nama, atau kartu
//      yang digambar dari cache — termasuk penyimpanan lokal peramban (titik kas, keranjang). Terbuka hanya untuk owner / akun aktif, atau mode cadangan.
const SEMUA_LAYAR = () => [ringkasan, stok, pelanggan, menu, harga, uang, laporan];
function terapkanKunci(akun) {
  const kunci = !q.get('cadangan') && !bisaBekerja(akun); const tadi = terkunci();
  setelKunci(kunci); document.body.classList.toggle('terkunci', kunci);
  // tinjauan 29 Sep: tampilkan(false) dulu dipanggil di SETIAP perubahan akun — akun karyawan yang aksesnya diubah owner saat bekerja (masih boleh
  // bekerja, tadi=false) membuat layar yang sedang dibuka berhenti menggambar sampai pindah tab. Kini hanya saat MENGUNCI.
  // Lapisan uang di luar <main> (pil/koin/panggung omzet, di atas gerbang z 20) ikut dicabut: tirai 23c = nol angka rupiah sesudah Keluar.
  if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; }); SEMUA_LAYAR().forEach((l) => l.tampilkan(false)); layar.tampilkan(false);
    ['omzetPil', 'omzetToast', 'omzetNaik', 'koinOmzet', 'cincinOmzet', 'kilauOmzet', 'panggung'].forEach((id) => { const el = document.getElementById(id); if (el) el.remove(); });
    document.getElementById('lembarAkun').classList.remove('buka'); return; }
  if (tadi) { pindah((() => { try { return localStorage.getItem(KUNCI_TAB) || 'jual'; } catch (e) { return 'jual'; } })()) || pindah('jual'); layar.gambar(); }
}
// ---- GANTI ORANG (23c keranjang → 23d SEMUA isian lokal, owner 24 Sep): isian yang belum disimpan — keranjang Jual, form & lembar atur di Stok, Pelanggan,
//      Harga, Uang, Laporan, Menu, draf lokal (belanja, barang masuk, cocok, adukan, tutup hari) — TIDAK terbawa ke akun berikutnya. Keluar lewat pil = SATU
//      pertanyaan yang menyebut layarnya (keluarAkun); keluar dari tab lain, sesi dicabut, akun nonaktif / belum disetujui, atau akun lain masuk = dikosongkan tanpa ditanya.
//      Draf di SERVER (aturanToko/hargaDraf = draf katalog harga) milik toko — tidak disentuh. Beranda tidak punya isian.
const LAYAR_ISIAN = () => [['Jual', 'jual', layar], ['Stok', 'stok', stok], ['Pelanggan', 'pelanggan', pelanggan], ['Harga', 'harga', harga], ['Uang', 'uang', uang], ['Laporan', 'laporan', laporan], ['Menu', 'menu', menu]];
function isianBelum() {
  const B = layar.belumDisimpan(); const out = [];
  LAYAR_ISIAN().forEach(([nama, tujuan, l]) => {
    if (tujuan === 'jual') { if (B.total > 0) out.push({ nama: 'Jual (keranjang ' + B.total + ' baris)', tujuan }); else if (layar.adaIsianLain()) out.push({ nama, tujuan }); return; }
    if (l.belumDisimpan()) out.push({ nama, tujuan });
  });
  return out;
}
function lupakanSemua() { LAYAR_ISIAN().forEach(([, , l]) => l.lupakanOrang()); }
let uidKeranjang = '';   // akun pemilik isian yang sedang ada di layar
function jagaIsian(akun) {
  if (q.get('cadangan')) return;
  if (!akun || akun.jenis === 'keluar' || !bisaBekerja(akun)) { lupakanSemua(); uidKeranjang = ''; return; }   // keluar / nonaktif / belum disetujui / kasir@
  if (uidKeranjang && uidKeranjang !== akun.uid) lupakanSemua();
  uidKeranjang = akun.uid;
}
// audit P2 (T6): uid yang permintaannya sudah SAMPAI di server sesi ini. Server (rules v7) tidak menerima permintaan kedua dari akun yang sama, jadi sesudah
// terkirim tombol "Minta didaftarkan" tidak ditawarkan lagi — juga bila keadaan akun dibunyikan ulang (gambarAkun dipanggil lagi tanpa berubah)
let _mintaTerkirim = ''; let _akunGerbang = null;
function gambarAkun(akun) {
  jagaIsian(akun);
  terapkanKunci(akun);
  _akunGerbang = akun || null;
  // owner 7 Okt (J2): keranjang & struk parkir akun ini yang tersimpan di tab ini (hari ini) dipulihkan sesudah halaman dimuat ulang — sesudah tirai dibuka
  if (!q.get('cadangan') && akun && bisaBekerja(akun)) layar.pulihkanKeranjang(akun);
  const bisa = bisaBekerja(akun);
  const tundaFokus = gerbang.akun(akun, bisa) || 0;   // 'tampil' = gerbang menghalangi layar (arti lama); membuka/menutup = gerak di js/inti/gerbang.js
  if (bisa) { isianSandi.value = ''; return; }
  const keluarSaja = !akun || akun.jenis === 'keluar';
  formMasuk.hidden = !keluarSaja; panelAkun.hidden = keluarSaja;
  if (keluarSaja) {
    const e = bacaEmail(); isianEmail.value = e; ingatEmail.hidden = !e; isianSandi.value = ''; kunciSandi(); salahMasuk.hidden = true;
    pesanMasuk.textContent = 'Masuk dengan akun lu sendiri. Akun dibuat owner.';
    setTimeout(() => (e ? isianSandi : isianEmail).focus(), tundaFokus + 50); return;   // sesudah pintu merapat: kolom baru terlihat & bisa difokus
  }
  document.getElementById('judulAkun').textContent = akun.kalimat || 'Akun ini belum bisa dipakai';
  const terkirim = akun.jenis === 'belum' && !!_mintaTerkirim && _mintaTerkirim === String(akun.uid || '');
  document.getElementById('pesanAkun').textContent = akun.jenis === 'belum' ? 'Masuk sebagai ' + akun.email + '. ' + (terkirim ? 'Permintaan sudah terkirim — tunggu owner menyetujuinya di Menu › Toko ini › Peran & persetujuan; layar ini terbuka sendiri begitu akun lu didaftarkan.'
    : 'Owner perlu mendaftarkan akun ini dulu — tulis nama lu lalu minta didaftarkan; owner menyetujuinya di Menu › Toko ini › Peran & persetujuan.')
    : akun.jenis === 'nonaktif' ? 'Masuk sebagai ' + akun.email + '. Tidak ada data toko yang dibuka di perangkat ini selama akun ini nonaktif.' : '';
  document.getElementById('mintaAkun').hidden = akun.jenis !== 'belum' || terkirim;
  document.getElementById('hasilAkun').hidden = true;
}
formMasuk.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const email = isianEmail.value.trim(), sandi = isianSandi.value;
  if (!email) { salahMasuk.textContent = 'Ketik email akun lu.'; salahMasuk.hidden = false; gerbang.ditolak(); isianEmail.focus(); return; }
  if (!sandi) { gerbang.mintaSandi(); return; }   // owner 29 Sep: dulu diam saja — kini kolom sandi berdenyut
  const tombol = document.getElementById('tombolMasuk'); tombol.disabled = true; tombol.textContent = 'Memeriksa…'; salahMasuk.hidden = true; gerbang.memeriksa();
  const r = await fb.masuk(email, sandi); isianSandi.value = ''; kunciSandi();
  tombol.disabled = false; tombol.textContent = 'Masuk';
  if (r.ok) { try { localStorage.setItem(KUNCI_EMAIL, email.toLowerCase()); } catch (e) { /* abaikan */ } } else { salahMasuk.textContent = r.pesan; salahMasuk.hidden = false; gerbang.ditolak(); }
});
document.getElementById('tombolMinta').addEventListener('click', async () => {
  const hasil = document.getElementById('hasilAkun'); const r = await fb.mintaDidaftarkan(document.getElementById('isianNamaAkun').value);
  hasil.hidden = false; hasil.classList.toggle('awas', !!r.gagal);
  hasil.textContent = r.gagal ? r.pesan : 'Permintaan terkirim. Tunggu owner menyetujui — layar ini terbuka sendiri begitu akun lu didaftarkan.';
  // tombol & kolom nama disembunyikan (#mintaAkun — .utama ber-display sendiri, atribut hidden pada tombolnya tidak menyembunyikan)
  if (!r.gagal) { gerbang.terkirim(); _mintaTerkirim = String((_akunGerbang && _akunGerbang.uid) || ''); document.getElementById('mintaAkun').hidden = true; }
});
/** Keluar = ganti orang. Masih ada catatan belum terkirim → ditanya dulu; salinannya TIDAK dihapus (terkirim saat akun ini masuk lagi). */
/** Keranjang Jual berisi → ditanya "simpan atau kosongkan?" (putaran 23c). Simpan = batal keluar, kembali ke keranjang. Kosongkan = dilupakan SESUDAH semua pertanyaan lolos. */
/** SATU pertanyaan saat Keluar (23d): cuma keranjang → kalimat keranjang (23c); ada isian lain → "Ada isian belum disimpan di: …". */
function tanyaIsian(daftar, b, hanyaKeranjang) {
  const bg = document.getElementById('modalKeranjang');
  document.getElementById('judulKeranjang').textContent = hanyaKeranjang ? kalimatKeranjangKeluar(b.total) : kalimatIsianKeluar(daftar.map((x) => x.nama));
  document.getElementById('ketKeranjang').textContent = (b.parkir ? b.aktif + ' di keranjang, ' + b.parkir + ' di keranjang yang diparkir. ' : '') + 'Belum ada yang tercatat. Kalau dikosongkan, orang berikutnya mulai dari '
    + (hanyaKeranjang ? 'keranjang kosong.' : 'layar kosong. Draf katalog harga yang tersimpan di server tidak ikut dikosongkan.');
  document.getElementById('keranjangSimpan').textContent = hanyaKeranjang ? 'Simpan dulu' : 'Kembali untuk menyimpan';
  document.getElementById('keranjangKosongkan').textContent = hanyaKeranjang ? 'Kosongkan lalu keluar' : 'Kosongkan semua lalu keluar';
  bg.classList.add('tampil');
  return new Promise((jawab) => {
    const selesai = (v) => { bg.classList.remove('tampil'); bg.onclick = null; jawab(v); };
    document.getElementById('keranjangSimpan').onclick = () => selesai('simpan');
    document.getElementById('keranjangKosongkan').onclick = () => selesai('kosongkan');
    bg.onclick = (ev) => { if (ev.target === bg) selesai('simpan'); };
  });
}
async function keluarAkun() {
  const a = akunKini(); const B = layar.belumDisimpan(); const daftar = a && bisaBekerja(a) ? isianBelum() : [];
  const hanyaKeranjang = daftar.length === 1 && daftar[0].tujuan === 'jual' && B.total > 0 && !layar.adaIsianLain();
  if (daftar.length && (await tanyaIsian(daftar, B, hanyaKeranjang)) !== 'kosongkan') { const t = daftar[0].tujuan; pindah(t); if (t === 'jual' && B.aktif) layar.keadaan.setel({ lembar: 'keranjang', kabar: '' }); return; }
  const L = statusFb.lokal || { belum: 0 };
  if (L.belum > 0 && !window.confirm('Ada ' + L.belum + ' catatan belum terkirim dari akun ini. Kalau keluar sekarang, catatannya tetap tersimpan di perangkat dan terkirim saat akun ini masuk lagi. Keluar tetap?')) return;
  lupakanSemua(); uidKeranjang = '';
  await fb.keluar();
}
document.getElementById('tombolKeluar').addEventListener('click', () => { tutupLembarAkun(); keluarAkun(); });
document.getElementById('tombolKeluarAkun').addEventListener('click', keluarAkun);
// ---- lembar akun: dibuka dari pil di kepala layar mana pun (delegasi di dokumen, karena tiap layar menggambar ulang kepalanya sendiri) ----
const lembarAkun = document.getElementById('lembarAkun');
function isiLembarAkun() {
  const a = akunKini(); const cad = sumberData().jenis === 'cadangan'; const kerja = !!a && bisaBekerja(a) && !cad;
  document.getElementById('lembarAkunNama').textContent = cad ? 'Membaca cadangan' : kerja ? teksMasukSebagai(a) : 'Belum masuk';
  const n = (statusFb.lokal || {}).belum || 0;
  document.getElementById('lembarAkunKet').textContent = cad ? 'Angka dari berkas cadangan, bukan data toko hari ini. Tidak ada akun yang masuk, tulisan cuma simulasi.'
    : (a && a.email ? a.email + ' · ' : '') + statusTeks() + (n ? ' · ' + n + ' catatan belum terkirim dari akun ini' : '');
  document.getElementById('tombolKeluar').hidden = !kerja;
}
function tutupLembarAkun() { lembarAkun.classList.remove('buka'); }
document.addEventListener('click', (ev) => {
  const pil = ev.target.closest && ev.target.closest('[data-pil-akun]');
  if (pil) { if (lembarAkun.classList.contains('buka')) return tutupLembarAkun(); isiLembarAkun(); const r = pil.getBoundingClientRect(); lembarAkun.style.top = Math.round(r.bottom + 8) + 'px'; const w = lembarAkun.offsetWidth || 320; lembarAkun.style.right = Math.max(12, Math.min(Math.round(innerWidth - r.right), innerWidth - w - 12)) + 'px'; lembarAkun.classList.add('buka'); return; }
  if (!lembarAkun.contains(ev.target)) tutupLembarAkun();
});
document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') tutupLembarAkun(); });
/** Menu/nav menyembunyikan layar yang bukan hak peran itu (nama & peran tampil di pil kepala tiap layar). */
function gambarChipDanNav() {
  const a = akunKini();
  if (lembarAkun.classList.contains('buka')) isiLembarAkun();
  document.querySelectorAll('[data-tujuan]').forEach((el) => { el.hidden = !!a && !bolehLayar(a, el.dataset.tujuan); });
  const tab = (() => { try { return localStorage.getItem(KUNCI_TAB) || 'jual'; } catch (e) { return 'jual'; } })();
  if (a && bisaBekerja(a) && !bolehLayar(a, tab)) pindah('jual');
}

// ---- PROYEK UJI (gerbang rules v3): setelan per perangkat, bilah merah di setiap layar selama aktif ----
(function () {
  const hasil = fb.aturProyekUjiDariAlamat(q);
  if (hasil === 'pasang' || hasil === 'lepas') { location.replace(location.pathname); return; }
  if (hasil) kabarSebentar(hasil);
  const uji = fb.proyekUji(); if (!uji) return;
  const bilah = document.createElement('div'); bilah.className = 'bilah-uji'; bilah.setAttribute('role', 'status');
  bilah.innerHTML = '<span>PROYEK UJI <b></b> — bukan data toko</span>'; bilah.querySelector('b').textContent = uji.projectId;
  const kembali = document.createElement('button'); kembali.type = 'button'; kembali.textContent = 'Kembali ke data toko';
  kembali.addEventListener('click', () => { try { localStorage.removeItem(fb.KUNCI_PROYEK_UJI); } catch (e) { /* abaikan */ } location.replace(location.pathname); });
  bilah.appendChild(kembali); document.body.appendChild(bilah); document.body.classList.add('proyek-uji');
})();
// ---- HEMAT BACA: /baru/?hemat=mati = saklar perangkat ini MATI tanpa membuka layar (jalan darurat owner 7 Okt; docs/prosedur-pulih-darurat.md) ----
const hematMatiDariAlamat = q.get('hemat') === 'mati';
if (hematMatiDariAlamat) { fb.setelSaklarHemat(false); location.replace(location.pathname); }
let _tiraiTab = null;   // tirai kunci tab / tab berhenti menerima data (hemat baca nyala) — dideklarasikan sebelum Firebase dimulai
// ---- SERVER TIRUAN (gladi tutup buku, 7 Okt 2026): hanya halaman localhost / 127.0.0.1 dengan ?emulator=… — bilah merah di setiap layar seperti proyek uji.
// Diminta tapi alamatnya ditolak: bilah "SERVER TIRUAN DITOLAK" yang menetap (firebase.js tidak tersambung ke mana pun — gagal-tertutup) ----
(function () {
  const tolak = fb.tolakServerTiruan(); const T = fb.serverTiruanAktif(); if (!tolak && !T) return;
  const bilah = document.createElement('div'); bilah.className = 'bilah-uji'; bilah.setAttribute('role', 'status');
  bilah.innerHTML = tolak ? '<span>SERVER TIRUAN DITOLAK — <b></b></span>' : '<span>SERVER TIRUAN <b></b> — emulator, bukan data toko</span>';
  bilah.querySelector('b').textContent = tolak || T.proyek;
  document.body.appendChild(bilah); document.body.classList.add('proyek-uji');
})();

if (q.get('cadangan')) {
  muatCadangan(q.get('cadangan')).then((r) => {
    // "hari ini" di cadangan = hari cadangan itu diunduh, bukan hari komputer ini — supaya kartu Hari ini tidak kosong menyesatkan
    sekarangCadangan = r.diunduhPada ? new Date(r.diunduhPada) : null;
    layar.keadaan.setel({ sekarang: sekarangCadangan }); ringkasan.gambar(); stok.gambar(); pelanggan.gambar(); menu.gambar(); harga.gambar(); uang.gambar(); laporan.gambar();
    console.log('cadangan dimuat:', r.koleksi, 'koleksi'); })
    .catch((e) => { const p = document.createElement('div'); p.className = 'pita-info awas'; p.textContent = 'Cadangan tidak terbaca: ' + String(e.message); akar.prepend(p); });
} else {
  // owner 29 Sep (freeze saat refresh/buka): status berbunyi tiap koleksi datang (±108× saat buka) — dulu tiap bunyi = gambar ulang semua layar.
  // Kini: selama koleksi awal belum lengkap gambar dijarangkan (±3×/detik), sesudahnya sekali per bingkai.
  // Fungsi yang diantre = fungsi yang SAMA dengan pendengar data tiap layar (tinjauan 29 Sep: pembungkus gambarSemua lolos dari penggabung
  // → layar yang terlihat digambar dua kali per bingkai). nanti() SEBELUM setelMuat: selesai muat = antrean digambar sekali, tanpa bingkai tambahan.
  const GAMBAR_STATUS = [layar.gambarGulir, ringkasan.gambar, stok.gambar, pelanggan.gambar, menu.gambar, harga.gambar, uang.gambar, laporan.gambar];
  fb.dengarkanStatus((st) => { statusFb = st; gambarChipDanNav(); GAMBAR_STATUS.forEach(nanti); setelMuat(!!st.masuk && st.koleksiTotal > 0 && st.koleksiSiap < st.koleksiTotal); });
  // hemat baca nyala (owner 7 Okt): pendengar simpanan tab ini mati → tirai muat ulang (mati: hematMati tidak pernah ada)
  fb.dengarkanStatus((st) => { if (st.hematMati && !_tiraiTab) tiraiTab('Tab ini berhenti menerima data', 'Hemat baca: simpanan perangkat di tab ini tidak lagi diperbarui (biasanya karena tab lain peramban ini). Angka di layar bisa basi — muat ulang. Catatan yang belum terkirim tetap aman di perangkat.', 'Muat ulang', () => location.reload()); });
  gerbang.mulai();   // sebelum Firebase menjawab: gerbang tertutup tanpa formulir (dulu layar kosong); sudah masuk → pintu terbuka cepat
  if (!hematMatiDariAlamat) mulaiFirebase();
}

// ---- HEMAT BACA (owner 7 Okt 2026, siap 2027): saklar per perangkat, bawaan MATI. Mati = Firebase dimulai persis seperti sebelumnya.
// Nyala = SATU klien Firestore per peramban (temuan SDK: tab yang turun dari primer kehilangan pendengar simpanannya tanpa kabar) — kunci tab di
// localStorage; tab kedua bertanya "Pakai di sini"; tab yang kalah menghentikan Firestore-nya dan menyuruh muat ulang.
function mulaiFirebase() {
  if (!fb.hematNyala()) { fb.mulai(gambarAkun); return; }
  const kt = fb.kunciTabHemat();
  const pakai = () => { kt.ambil(); jagaKunciTab(kt); fb.mulai(gambarAkun); };
  if (kt.keadaan() !== 'lain') return pakai();
  tiraiTab('Aplikasi sudah terbuka di tab lain', 'Hemat baca menyala di perangkat ini: satu peramban hanya memakai aplikasi di SATU tab, supaya angka tidak basi diam-diam. Tutup tab yang lain, atau pakai di sini — tab yang lain berhenti dan catatan yang belum terkirim tetap aman.',
    'Pakai di sini', () => { tutupTiraiTab(); pakai(); });
}
function jagaKunciTab(kt) {
  let kalah = false, dilepas = false;
  const cek = () => {
    if (kalah || kt.milik()) return;
    if (dilepas && kt.keadaan() !== 'lain') { dilepas = false; kt.ambil(); return; }   // kembali dari halaman sebelumnya (bfcache), tidak ada tab lain yang mengambil
    kalah = true;
    fb.berhenti('Aplikasi dipakai di tab lain peramban ini — tab ini berhenti supaya angka tidak basi. Muat ulang untuk memakainya di sini.');
    tiraiTab('Dipakai di tab lain', 'Tab lain peramban ini mengambil alih aplikasi (hemat baca: satu tab per peramban). Catatan yang belum terkirim dari tab ini tetap aman di perangkat.', 'Pakai di sini (muat ulang)', () => location.reload());
  };
  setInterval(() => { if (!kalah && !dilepas && !kt.detak()) cek(); }, 4000);
  window.addEventListener('storage', (e) => { if (!e || e.key === null || e.key === 'miqbal_baru_kunci_tab_v1') cek(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) cek(); });
  window.addEventListener('pageshow', cek);
  window.addEventListener('pagehide', () => { if (!kalah) { dilepas = true; kt.lepas(); } });
}
function tiraiTab(judul, ket, tombol, aksi) {
  tutupTiraiTab();
  const bg = document.createElement('div'); bg.className = 'modal-bg tampil'; bg.style.zIndex = '40'; bg.setAttribute('role', 'dialog'); bg.setAttribute('aria-modal', 'true');
  const k = document.createElement('div'); k.className = 'modal kartu';
  const j = document.createElement('div'); j.className = 'serif'; j.style.fontSize = '20px'; j.textContent = judul;
  const t = document.createElement('div'); t.className = 'ket'; t.textContent = ket;
  const b = document.createElement('button'); b.type = 'button'; b.className = 'utama'; b.textContent = tombol; b.addEventListener('click', aksi);
  k.appendChild(j); k.appendChild(t); k.appendChild(b); bg.appendChild(k); document.body.appendChild(bg); _tiraiTab = bg;
}
function tutupTiraiTab() { if (_tiraiTab) { _tiraiTab.remove(); _tiraiTab = null; } }

// nav bawah / samping: kelima petak hidup sejak putaran 14; petak yang layarnya belum ada (tidak ada lagi) mengaku
document.querySelectorAll('[data-tujuan]').forEach((el) => el.addEventListener('click', () => {
  const t = el.dataset.tujuan;
  if (pindah(t)) return;
  kabarSebentar('Layar ' + el.textContent.trim() + ' belum ada di sistem baru.');
}));

// menu samping Mac (owner 23 Sep): sempit; membuka saat kursor menepi ke tepi kiri layar atau masuk ke menu, menutup saat kursor pergi;
// monogram IQ diketuk = buka/tutup (untuk layar sentuh lebar yang tidak punya kursor)
(function () {
  const side = document.querySelector('.side'); if (!side) return;
  let kunci = false;   // dibuka lewat ketukan → tidak ditutup oleh kursor yang pergi
  document.addEventListener('mousemove', (ev) => { if (kunci) return; if (ev.clientX <= 10) side.classList.add('buka'); else if (ev.clientX > 250) side.classList.remove('buka'); });
  side.addEventListener('mouseleave', () => { if (!kunci) side.classList.remove('buka'); });
  side.querySelector('[data-side="toggle"]').addEventListener('click', () => { kunci = !side.classList.contains('buka'); side.classList.toggle('buka', kunci); });
  side.querySelectorAll('.item').forEach((el) => el.addEventListener('click', () => { kunci = false; side.classList.remove('buka'); }));
})();

// layar pembuka: yang terakhir dipakai di perangkat ini (bawaan: Jual) — di balik tirai sampai Firebase menjawab siapa yang masuk (mode cadangan: langsung terbuka)
pindah((() => { try { return localStorage.getItem(KUNCI_TAB) || 'jual'; } catch (e) { return 'jual'; } })()) || pindah('jual');
terapkanKunci(null);
try { sessionStorage.removeItem('miqbal_muat_ulang_modul'); } catch (e) { /* abaikan */ }   // aplikasi berhasil dimuat utuh → penjaga muat-ulang disiapkan lagi
