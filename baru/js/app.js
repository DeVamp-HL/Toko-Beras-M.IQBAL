// SISTEM BARU — pintu masuk. Putaran 1 (19 Sep 2026): layar JUAL membaca data toko yang sama dengan index.html.
// Sumber data: Firestore toko (bawaan) atau berkas cadangan (?cadangan=…/backup-batch-….json, untuk mencoba di komputer).
import { pasangLayarJual } from './layar/jual.js';
import { pasangLayarRingkasan } from './layar/ringkasan.js';
import { pasangLayarStok } from './layar/stok.js';
import { pasangLayarPelanggan } from './layar/pelanggan.js';
import * as fb from './data/firebase.js';
import { muatCadangan } from './data/cadangan.js';
import { dengarkan, sumberData } from './data/toko.js';

const q = new URLSearchParams(location.search);
const KUNCI_MODE = 'miqbal_baru_mode';
let mode = (() => { try { return localStorage.getItem(KUNCI_MODE) || 'terang'; } catch (e) { return 'terang'; } })();
let versi = 0;
let statusFb = { masuk: false, koleksiSiap: 0, koleksiTotal: 0, offline: false, galat: '' };

// Kelas gelap juga di <html>: Safari iOS 26/27 mewarnai daerah poni/jam dari warna dasar & color-scheme elemen akar,
// bukan dari theme-color — tanpa ini poninya putih di mode gelap. theme-color ikut diganti untuk peramban lain.
function terapkanMode() {
  const gelap = mode === 'gelap';
  document.body.classList.toggle('gelap', gelap);
  document.documentElement.classList.toggle('gelap', gelap);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = gelap ? '#111516' : '#eef1f4';
}
function gantiMode() { mode = mode === 'gelap' ? 'terang' : 'gelap'; try { localStorage.setItem(KUNCI_MODE, mode); } catch (e) { /* abaikan */ } terapkanMode(); layar.gambar(); ringkasan.gambar(); stok.gambar(); pelanggan.gambar(); }
function statusTeks() {
  const s = sumberData();
  if (s.jenis === 'cadangan') return 'membaca cadangan (bukan data hidup)';
  if (!statusFb.masuk) return 'belum masuk';
  if (statusFb.galat) return 'ada koleksi yang ditolak: ' + statusFb.galat;
  if (statusFb.koleksiSiap < statusFb.koleksiTotal) return 'memuat ' + statusFb.koleksiSiap + '/' + statusFb.koleksiTotal + ' koleksi';
  if (statusFb.menunggu > 0) return 'menunggu server mengaku ' + statusFb.menunggu + ' catatan';
  return statusFb.offline ? 'TANPA INTERNET — angka dari simpanan perangkat, catatan mengantre' : 'tersambung · ' + statusFb.koleksiTotal + ' koleksi';
}

terapkanMode();
const akar = document.getElementById('layar');
const layar = pasangLayarJual(akar, { gantiMode, mode: () => mode, statusTeks, versiData: () => versi });
dengarkan(() => { versi += 1; });

// ---- perpindahan layar: tiap layar punya <main> sendiri yang disembunyikan, supaya keranjang Jual tidak hilang saat pindah ----
const KUNCI_TAB = 'miqbal_baru_tab';
let sekarangCadangan = null;   // mode cadangan: "sekarang" = saat cadangan diunduh
const statusRingkas = () => (statusFb.offline ? 'tanpa internet' : statusFb.menunggu > 0 ? 'menunggu server' : statusFb.koleksiSiap < statusFb.koleksiTotal ? 'memuat…' : 'data toko');
const ringkasan = pasangLayarRingkasan(document.getElementById('layarRingkasan'), { gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t) });
const stok = pasangLayarStok(document.getElementById('layarStok'), { gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, keranjangJual: () => layar.keadaan.baca() });
const pelanggan = pasangLayarPelanggan(document.getElementById('layarPelanggan'), { gantiMode, mode: () => mode, sekarang: () => sekarangCadangan, statusRingkas, pindah: (t) => pindah(t) });
const LAYAR_ADA = { jual: akar, ringkasan: document.getElementById('layarRingkasan'), stok: document.getElementById('layarStok'), pelanggan: document.getElementById('layarPelanggan') };
function pindah(tujuan) {
  if (!LAYAR_ADA[tujuan]) return false;
  Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].hidden = k !== tujuan; });
  document.querySelectorAll('[data-tujuan]').forEach((el) => el.classList.toggle('aktif', el.dataset.tujuan === tujuan));
  document.body.classList.toggle('di-jual', tujuan === 'jual');
  ringkasan.tampilkan(tujuan === 'ringkasan'); stok.tampilkan(tujuan === 'stok'); pelanggan.tampilkan(tujuan === 'pelanggan');
  try { localStorage.setItem(KUNCI_TAB, tujuan); } catch (e) { /* abaikan */ }
  window.scrollTo(0, 0);
  return true;
}

// ---- masuk (sandi diketik owner; kode ini cuma meneruskannya ke Firebase, tidak menyimpan) ----
const modal = document.getElementById('modalMasuk');
const pesanMasuk = document.getElementById('pesanMasuk');
const salahMasuk = document.getElementById('salahMasuk');
const isianSandi = document.getElementById('isianSandi');
function bukaMasuk(pesan) { pesanMasuk.textContent = pesan; salahMasuk.hidden = true; modal.classList.add('tampil'); setTimeout(() => isianSandi.focus(), 50); }
document.getElementById('formMasuk').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const sandi = isianSandi.value; if (!sandi) return;
  const tombol = document.getElementById('tombolMasuk'); tombol.disabled = true; tombol.textContent = 'Memeriksa…';
  const r = await fb.masuk(sandi); isianSandi.value = '';
  tombol.disabled = false; tombol.textContent = 'Masuk';
  if (r.ok) modal.classList.remove('tampil'); else { salahMasuk.textContent = r.pesan; salahMasuk.hidden = false; }
});

if (q.get('cadangan')) {
  muatCadangan(q.get('cadangan')).then((r) => {
    // "hari ini" di cadangan = hari cadangan itu diunduh, bukan hari komputer ini — supaya kartu Hari ini tidak kosong menyesatkan
    sekarangCadangan = r.diunduhPada ? new Date(r.diunduhPada) : null;
    layar.keadaan.setel({ sekarang: sekarangCadangan }); ringkasan.gambar(); stok.gambar();
    console.log('cadangan dimuat:', r.koleksi, 'koleksi'); })
    .catch((e) => { const p = document.createElement('div'); p.className = 'pita-info awas'; p.textContent = 'Cadangan tidak terbaca: ' + String(e.message); akar.prepend(p); });
} else {
  fb.dengarkanStatus((st) => { statusFb = st; if (st.masuk) modal.classList.remove('tampil'); layar.gambar(); ringkasan.gambar(); stok.gambar(); });
  fb.mulai(bukaMasuk);
}

// nav bawah / samping: hanya Jual yang hidup di putaran ini — tujuan lain mengaku belum ada
document.querySelectorAll('[data-tujuan]').forEach((el) => el.addEventListener('click', () => {
  const t = el.dataset.tujuan;
  if (pindah(t)) return;
  const kabar = document.getElementById('kabarNav'); kabar.textContent = 'Layar ' + el.textContent.trim() + ' belum ada di sistem baru — masih di sistem lama (index.html).'; kabar.hidden = false;
  clearTimeout(kabar._t); kabar._t = setTimeout(() => { kabar.hidden = true; }, 3200);
}));

// layar pembuka: yang terakhir dipakai di perangkat ini (bawaan: Jual)
pindah((() => { try { return localStorage.getItem(KUNCI_TAB) || 'jual'; } catch (e) { return 'jual'; } })()) || pindah('jual');
try { sessionStorage.removeItem('miqbal_muat_ulang_modul'); } catch (e) { /* abaikan */ }   // aplikasi berhasil dimuat utuh → penjaga muat-ulang disiapkan lagi
