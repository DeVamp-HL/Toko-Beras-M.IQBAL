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

const q = new URLSearchParams(location.search);
const KUNCI_MODE = 'miqbal_baru_mode';
let mode = (() => { try { return localStorage.getItem(KUNCI_MODE) || 'terang'; } catch (e) { return 'terang'; } })();
let versi = 0;
let statusFb = { masuk: false, akun: null, koleksiSiap: 0, koleksiTotal: 0, offline: false, galat: '', ditolak: [], lokal: { belum: 0, ditolak: 0 } };
// akun yang masuk (putaran 23). Mode cadangan tidak masuk ke Firebase: dianggap owner (tulisan cuma simulasi di memori).
const akunKini = () => (sumberData().jenis === 'cadangan' ? { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: '' } : statusFb.akun);
fb.setelSumberHak(() => { const a = statusFb.akun; if (!a || !a.peran || a.peran === 'owner') return {}; try { return (ssAtur('peran').hak || {})[a.peran] || {}; } catch (e) { return {}; } });

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

terapkanMode();
const akar = document.getElementById('layar');
const layar = pasangLayarJual(akar, { akun: () => akunKini(), gantiMode, mode: () => mode, statusTeks, versiData: () => versi, pemegang: () => fb.pemegangPerangkat() });
dengarkan(() => { versi += 1; });

// ---- perpindahan layar: tiap layar punya <main> sendiri yang disembunyikan, supaya keranjang Jual tidak hilang saat pindah ----
const KUNCI_TAB = 'miqbal_baru_tab';
let sekarangCadangan = null;   // mode cadangan: "sekarang" = saat cadangan diunduh
const statusRingkas = () => (statusFb.offline ? 'tanpa internet' : statusFb.menunggu > 0 ? 'menunggu server' : statusFb.koleksiSiap < statusFb.koleksiTotal ? 'memuat…' : 'DATA TOKO');
const ringkasan = pasangLayarRingkasan(document.getElementById('layarRingkasan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t) });
const stok = pasangLayarStok(document.getElementById('layarStok'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, keranjangJual: () => layar.keadaan.baca(), bukaHarga: (keluarga) => { pindah('harga'); harga.buka(keluarga); } });
const pelanggan = pasangLayarPelanggan(document.getElementById('layarPelanggan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t) });
// Menu (putaran 14): laci N1 + pita jam + Sistem (SS1–SS5). Tujuan baris = layar lain lewat pintu yang sama dengan ketukan di layar itu.
const menu = pasangLayarMenu(document.getElementById('layarMenu'), { gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t),
  bukaStok: (lembar, tab) => { pindah('stok'); stok.buka(lembar, tab); }, bukaPelanggan: (keluarga, orang) => { pindah('pelanggan'); pelanggan.buka(keluarga, orang); }, bukaHarga: (keluarga, t) => { pindah('harga'); harga.buka(keluarga, t); }, bukaUang: (keluarga, t) => { pindah('uang'); uang.buka(keluarga, t); }, bukaLaporan: (keluarga, t) => { pindah('laporan'); laporan.buka(keluarga, t); }, bukaJual: (lembar) => { pindah('jual'); layar.keadaan.setel({ lembar, kabar: '' }); },
  lokal: () => ({ antre: statusFb.antre || [], idPerangkat: fb.idPerangkat(), namaPerangkat: fb.perangkatRingkas(), pemegang: fb.pemegangPerangkat(), lokasi: fb.lokasiPerangkat(), koleksiSiap: statusFb.koleksiSiap, koleksiTotal: statusFb.koleksiTotal, offline: statusFb.offline }),
  periksaSambungan: () => fb.periksaSambungan(4000), setelLokasi: (id) => fb.setelLokasi(id), namaiPerangkat: (n) => fb.namaiPerangkat(n),
  akun: akunKini, antreLokal: () => fb.antreLokal(), buangDitolak: (id) => fb.buangDitolak(id), tulisUlangDitolak: (id) => fb.tulisUlangDitolak(id) });
// Harga & Pemasok (putaran 17): layar keenam, dibuka dari Menu (baris Pemasok & utang · Katalog harga · cari) dan Stok → Gudang → "Apa yang harus dibeli"; di Mac ada di menu samping.
const harga = pasangLayarHarga(document.getElementById('layarHarga'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t) });
// Uang (putaran 18): layar ketujuh — Uang keluar · Orang & upah · Owner & toko · Pindah uang · Tutup hari · Tutup buku. Dibuka dari Menu; di Mac ada di menu samping.
const lokalPerangkat = () => ({ antre: statusFb.antre || [], menunggu: statusFb.menunggu || 0, idPerangkat: fb.idPerangkat(), namaPerangkat: fb.perangkatRingkas(), pemegang: fb.pemegangPerangkat(), offline: statusFb.offline });
const uang = pasangLayarUang(document.getElementById('layarUang'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t), lokal: lokalPerangkat });
// Laporan & Dokumen (putaran 19): layar kedelapan — Laba · Harian · Bulanan · Neraca · Dokumen (berkop, paket bank, dokumen kecil) · Setelan (kop & identitas). Dibuka dari Menu; di Mac ada di menu samping.
// keTujuan = satu pintu ke layar lain dengan bentuk tujuan yang sama dengan baris Menu ({ ke, keluarga, tab, lembar, sistem }).
const keTujuan = (t) => { if (!t) return; if (t.ke === 'stok') { pindah('stok'); stok.buka(t.lembar || null, t.tab || null); } else if (t.ke === 'pelanggan') { pindah('pelanggan'); pelanggan.buka(t.keluarga || 'kenali', t.orang || null); } else if (t.ke === 'harga') { pindah('harga'); harga.buka(t.keluarga || 'katalog', t); } else if (t.ke === 'uang') { pindah('uang'); uang.buka(t.keluarga || 'keluar', t); } else if (t.ke === 'laporan') { pindah('laporan'); laporan.buka(t.keluarga || 'laba', t); } else if (t.ke === 'sistem') { pindah('menu'); menu.buka && menu.buka(t.sistem || 'perangkat', t.tab || null); } else if (t.ke === 'jual' && t.lembar) { pindah('jual'); layar.keadaan.setel({ lembar: t.lembar, kabar: '' }); } else pindah(t.ke); };
const laporan = pasangLayarLaporan(document.getElementById('layarLaporan'), { akun: () => akunKini(), gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t), keTujuan });
const LAYAR_ADA = { jual: akar, ringkasan: document.getElementById('layarRingkasan'), stok: document.getElementById('layarStok'), pelanggan: document.getElementById('layarPelanggan'), menu: document.getElementById('layarMenu'), harga: document.getElementById('layarHarga'), uang: document.getElementById('layarUang'), laporan: document.getElementById('layarLaporan') };
function pindah(tujuan) {
  if (!LAYAR_ADA[tujuan]) return false;
  const a = akunKini(); if (a && bisaBekerja(a) && !bolehLayar(a, tujuan)) { kabarSebentar('Layar ini tidak termasuk hak ' + teksMasukSebagai(a) + '.'); return true; }
  Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].hidden = k !== tujuan; });
  document.querySelectorAll('[data-tujuan]').forEach((el) => el.classList.toggle('aktif', el.dataset.tujuan === tujuan || ((tujuan === 'harga' || tujuan === 'uang' || tujuan === 'laporan') && el.dataset.tujuan === 'menu' && el.closest('nav'))));   // Harga & Pemasok / Uang tidak punya petak di nav bawah: petak Menu yang menyala (pintunya)
  document.body.classList.toggle('di-jual', tujuan === 'jual');
  ringkasan.tampilkan(tujuan === 'ringkasan'); stok.tampilkan(tujuan === 'stok'); pelanggan.tampilkan(tujuan === 'pelanggan'); menu.tampilkan(tujuan === 'menu'); harga.tampilkan(tujuan === 'harga'); uang.tampilkan(tujuan === 'uang'); laporan.tampilkan(tujuan === 'laporan');
  try { localStorage.setItem(KUNCI_TAB, tujuan); } catch (e) { /* abaikan */ }
  window.scrollTo(0, 0);
  return true;
}

// ---- masuk PER ORANG (putaran 23). Sandi diketik lalu diteruskan ke Firebase, tidak disimpan & tidak pernah diisi otomatis
//      (readonly sampai diketuk = pengisi-otomatis peramban tidak menempelkan sandi tersimpan; sisanya setelan peramban tablet — putaran tablet). ----
const KUNCI_EMAIL = 'miqbal_baru_email_terakhir';
const modal = document.getElementById('modalMasuk');
const formMasuk = document.getElementById('formMasuk'), panelAkun = document.getElementById('panelAkun');
const pesanMasuk = document.getElementById('pesanMasuk');
const salahMasuk = document.getElementById('salahMasuk');
const isianEmail = document.getElementById('isianEmail'), isianSandi = document.getElementById('isianSandi'), ingatEmail = document.getElementById('ingatEmail');
const bacaEmail = () => { try { return localStorage.getItem(KUNCI_EMAIL) || ''; } catch (e) { return ''; } };
function kabarSebentar(t) { const k = document.getElementById('kabarNav'); k.textContent = t; k.hidden = false; clearTimeout(k._t); k._t = setTimeout(() => { k.hidden = true; }, 3600); }
isianSandi.addEventListener('focus', () => { isianSandi.readOnly = false; });
document.getElementById('lupakanEmail').addEventListener('click', () => { try { localStorage.removeItem(KUNCI_EMAIL); } catch (e) { /* abaikan */ } isianEmail.value = ''; ingatEmail.hidden = true; isianEmail.focus(); });
/** Gambar layar masuk menurut keadaan akun: keluar → formulir; belum terdaftar / dinonaktifkan / kasir@ → lembar akun; owner / aktif → aplikasi. */
function gambarAkun(akun) {
  const bisa = bisaBekerja(akun);
  modal.classList.toggle('tampil', !bisa);
  if (bisa) { isianSandi.value = ''; return; }
  const keluarSaja = !akun || akun.jenis === 'keluar';
  formMasuk.hidden = !keluarSaja; panelAkun.hidden = keluarSaja;
  if (keluarSaja) {
    const e = bacaEmail(); isianEmail.value = e; ingatEmail.hidden = !e; isianSandi.value = ''; isianSandi.readOnly = true; salahMasuk.hidden = true;
    pesanMasuk.textContent = 'Masuk dengan akun lu sendiri. Akun dibuat owner.';
    setTimeout(() => (e ? isianSandi : isianEmail).focus(), 50); return;
  }
  document.getElementById('judulAkun').textContent = akun.kalimat || 'Akun ini belum bisa dipakai';
  document.getElementById('pesanAkun').textContent = akun.jenis === 'belum' ? 'Masuk sebagai ' + akun.email + '. Owner perlu mendaftarkan akun ini dulu — tulis nama lu lalu minta didaftarkan; owner menyetujuinya di Menu › Sistem › Peran.'
    : akun.jenis === 'nonaktif' ? 'Masuk sebagai ' + akun.email + '. Tidak ada data toko yang dibuka di perangkat ini selama akun ini nonaktif.' : '';
  document.getElementById('mintaAkun').hidden = akun.jenis !== 'belum';
  document.getElementById('hasilAkun').hidden = true;
}
formMasuk.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const email = isianEmail.value.trim(), sandi = isianSandi.value; if (!email || !sandi) return;
  const tombol = document.getElementById('tombolMasuk'); tombol.disabled = true; tombol.textContent = 'Memeriksa…';
  const r = await fb.masuk(email, sandi); isianSandi.value = ''; isianSandi.readOnly = true;
  tombol.disabled = false; tombol.textContent = 'Masuk';
  if (r.ok) { try { localStorage.setItem(KUNCI_EMAIL, email.toLowerCase()); } catch (e) { /* abaikan */ } } else { salahMasuk.textContent = r.pesan; salahMasuk.hidden = false; }
});
document.getElementById('tombolMinta').addEventListener('click', async () => {
  const hasil = document.getElementById('hasilAkun'); const r = await fb.mintaDidaftarkan(document.getElementById('isianNamaAkun').value);
  hasil.hidden = false; hasil.classList.toggle('awas', !!r.gagal);
  hasil.textContent = r.gagal ? r.pesan : 'Permintaan terkirim. Tunggu owner menyetujui — layar ini terbuka sendiri begitu akun lu didaftarkan.';
});
/** Keluar = ganti orang. Masih ada catatan belum terkirim → ditanya dulu; salinannya TIDAK dihapus (terkirim saat akun ini masuk lagi). */
async function keluarAkun() {
  const L = statusFb.lokal || { belum: 0 };
  if (L.belum > 0 && !window.confirm('Ada ' + L.belum + ' catatan belum terkirim dari akun ini. Kalau keluar sekarang, catatannya tetap tersimpan di perangkat dan terkirim saat akun ini masuk lagi. Keluar tetap?')) return;
  await fb.keluar();
}
document.getElementById('tombolKeluar').addEventListener('click', keluarAkun);
document.getElementById('tombolKeluarAkun').addEventListener('click', keluarAkun);
/** Nama & peran di setiap layar + menu/nav menyembunyikan layar yang bukan hak peran itu. */
function gambarChipDanNav() {
  const a = akunKini(); const chip = document.getElementById('chipAkun'); const kerja = !!a && bisaBekerja(a) && sumberData().jenis !== 'cadangan';
  chip.hidden = !kerja; document.body.classList.toggle('ada-akun', kerja);
  if (kerja) { document.getElementById('chipNama').textContent = 'Masuk sebagai: ' + teksMasukSebagai(a); const n = (statusFb.lokal || {}).belum || 0; const ca = document.getElementById('chipAntre'); ca.hidden = !n; ca.textContent = n ? n + ' belum terkirim' : ''; }
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

if (q.get('cadangan')) {
  muatCadangan(q.get('cadangan')).then((r) => {
    // "hari ini" di cadangan = hari cadangan itu diunduh, bukan hari komputer ini — supaya kartu Hari ini tidak kosong menyesatkan
    sekarangCadangan = r.diunduhPada ? new Date(r.diunduhPada) : null;
    layar.keadaan.setel({ sekarang: sekarangCadangan }); ringkasan.gambar(); stok.gambar(); pelanggan.gambar(); menu.gambar(); harga.gambar(); uang.gambar(); laporan.gambar();
    console.log('cadangan dimuat:', r.koleksi, 'koleksi'); })
    .catch((e) => { const p = document.createElement('div'); p.className = 'pita-info awas'; p.textContent = 'Cadangan tidak terbaca: ' + String(e.message); akar.prepend(p); });
} else {
  fb.dengarkanStatus((st) => { statusFb = st; gambarChipDanNav(); layar.gambar(); ringkasan.gambar(); stok.gambar(); menu.gambar(); harga.gambar(); uang.gambar(); laporan.gambar(); });
  fb.mulai(gambarAkun);
}

// nav bawah / samping: kelima petak hidup sejak putaran 14; petak yang layarnya belum ada (tidak ada lagi) mengaku
document.querySelectorAll('[data-tujuan]').forEach((el) => el.addEventListener('click', () => {
  const t = el.dataset.tujuan;
  if (pindah(t)) return;
  kabarSebentar('Layar ' + el.textContent.trim() + ' belum ada di sistem baru — masih di sistem lama (index.html).');
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

// layar pembuka: yang terakhir dipakai di perangkat ini (bawaan: Jual)
pindah((() => { try { return localStorage.getItem(KUNCI_TAB) || 'jual'; } catch (e) { return 'jual'; } })()) || pindah('jual');
try { sessionStorage.removeItem('miqbal_muat_ulang_modul'); } catch (e) { /* abaikan */ }   // aplikasi berhasil dimuat utuh → penjaga muat-ulang disiapkan lagi
