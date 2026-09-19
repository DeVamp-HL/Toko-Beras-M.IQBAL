// SISTEM BARU — pintu masuk. Putaran 1 (19 Sep 2026): layar JUAL membaca data toko yang sama dengan index.html.
// Sumber data: Firestore toko (bawaan) atau berkas cadangan (?cadangan=…/backup-batch-….json, untuk mencoba di komputer).
import { pasangLayarJual } from './layar/jual.js';
import * as fb from './data/firebase.js';
import { muatCadangan } from './data/cadangan.js';
import { dengarkan, sumberData } from './data/toko.js';

const q = new URLSearchParams(location.search);
const KUNCI_MODE = 'miqbal_baru_mode';
let mode = (() => { try { return localStorage.getItem(KUNCI_MODE) || 'terang'; } catch (e) { return 'terang'; } })();
let versi = 0;
let statusFb = { masuk: false, koleksiSiap: 0, koleksiTotal: 0, offline: false, galat: '' };

function terapkanMode() { document.body.classList.toggle('gelap', mode === 'gelap'); }
function gantiMode() { mode = mode === 'gelap' ? 'terang' : 'gelap'; try { localStorage.setItem(KUNCI_MODE, mode); } catch (e) { /* abaikan */ } terapkanMode(); layar.gambar(); }
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
    layar.keadaan.setel({ sekarang: r.diunduhPada ? new Date(r.diunduhPada) : null });
    console.log('cadangan dimuat:', r.koleksi, 'koleksi'); })
    .catch((e) => { const p = document.createElement('div'); p.className = 'pita-info awas'; p.textContent = 'Cadangan tidak terbaca: ' + String(e.message); akar.prepend(p); });
} else {
  fb.dengarkanStatus((st) => { statusFb = st; if (st.masuk) modal.classList.remove('tampil'); layar.gambar(); });
  fb.mulai(bukaMasuk);
}

// nav bawah / samping: hanya Jual yang hidup di putaran ini — tujuan lain mengaku belum ada
document.querySelectorAll('[data-tujuan]').forEach((el) => el.addEventListener('click', () => {
  const t = el.dataset.tujuan;
  if (t === 'jual') return;
  const kabar = document.getElementById('kabarNav'); kabar.textContent = 'Layar ' + el.textContent.trim() + ' belum ada di putaran ini — masih di sistem lama (index.html).'; kabar.hidden = false;
  clearTimeout(kabar._t); kabar._t = setTimeout(() => { kabar.hidden = true; }, 3200);
}));
