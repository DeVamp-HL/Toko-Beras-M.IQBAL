// LONCENG KABAR & PESAN (owner 23 Nov 2026: "ada ikon notifikasi untuk pesan di aplikasi sistem mac/hp/tablet" — "Lonceng + balas langsung").
// Ikon lonceng di kepala tiap layar (Mac, HP, tablet) + lembar daftar kabar. Isi & angka dari kabar-baru-logika (kbLonceng): owner = permintaan yang
// menunggu, akun tablet = permintaannya sendiri + jawaban owner. Owner menandai PESAN / kabar barang masuk dibaca + membalas langsung dari sini — lewat
// tpSusunPutus, pintu yang sama dengan Uang › titipan (tidak ada jalan tulis baru). Titipan uang, nego, harga, bon: tombol membuka layarnya.
// Lembar dibuka = semua kabar yang tampil dianggap sudah dibuka (angka kembali nol); peta "sudah dibuka" per akun di perangkat ini (localStorage).
import { h, mentah, pasang } from '../inti/dom.js';
import { tulisDokumen, kabarKiriman } from '../data/toko.js';
import { kbLonceng, kbTandai, kbBacaLihat, kbTulisLihat, KB_LIHAT, KB_NAMA_LAYAR } from './kabar-baru-logika.js';
import { tpSusunPutus, TP_BATAS } from './titipan-logika.js';
import { waktuSekarang } from './jual-logika.js';

let _n = 0; let _isi = null; let _akun = null; let _buka = false; let _sibuk = ''; let _kabar = null; let _goyang = 0;
const _balas = {};
let _opsi = { pindah: () => {}, sekarang: () => null, berbunyi: () => {} };

/** Angka di lonceng sekarang (kabar belum dibuka di perangkat ini). */
export const loncengAngka = () => _n;
const teksAngka = (n) => (n > 99 ? '99+' : n ? String(n) : '');
/** Ikon lonceng untuk kepala layar (HTML mentah). Satu bentuk di semua layar; angkanya diperbarui app.js tanpa menggambar ulang layarnya. */
export function pintuLonceng() {
  return '<button type="button" class="lonceng' + (_n ? ' ada' : '') + '" data-lonceng data-k="lonceng" aria-label="Kabar &amp; pesan' + (_n ? ' · ' + _n + ' baru' : '') + '" title="Kabar &amp; pesan">'
    + '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="lc-badan" d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.6 2.1H4.4z"/><path class="lc-anting" d="M10 20.6a2.1 2.1 0 0 0 4 0"/></svg>'
    + '<span class="lonceng-n" data-lonceng-n>' + teksAngka(_n) + '</span></button>';
}
export const loncengMentah = () => mentah(pintuLonceng());

const uidKini = () => String((_akun && _akun.uid) || '');
function bacaLihat() { try { return kbBacaLihat(localStorage.getItem(KB_LIHAT), uidKini()); } catch (e) { return null; } }
function simpanLihat(peta) { try { localStorage.setItem(KB_LIHAT, kbTulisLihat(localStorage.getItem(KB_LIHAT), uidKini(), peta)); } catch (e) { /* perangkat menolak: angka kembali muncul sesudah dimuat ulang */ } }

/** Perbarui semua ikon lonceng yang tergambar (angka, kelas, goyang bila bertambah). */
function perbaruiIkon(naik) {
  document.querySelectorAll('[data-lonceng]').forEach((b) => {
    b.classList.toggle('ada', _n > 0); b.setAttribute('aria-label', 'Kabar & pesan' + (_n ? ' · ' + _n + ' baru' : ''));
    const s = b.querySelector('[data-lonceng-n]'); if (s && s.textContent !== teksAngka(_n)) { s.textContent = teksAngka(_n); s.classList.remove('letup'); void s.offsetWidth; s.classList.add('letup'); }
    if (naik) { b.classList.remove('goyang'); void b.offsetWidth; b.classList.add('goyang'); }
  });
}

/**
 * Hitung ulang dari data (app.js: tiap data / akun berubah). akun = akun yang dipakai layar. Kabar baru sejak tadi = lonceng bergoyang.
 * Perangkat yang belum pernah menyimpan peta untuk akun ini: semua yang ada sekarang dianggap sudah dibuka (angka tidak meledak di pemakaian pertama).
 */
export function loncengSegarkan(akun) {
  const ganti = !_akun || !akun || _akun.uid !== akun.uid || _akun.jenis !== akun.jenis; _akun = akun || null;
  if (!_akun) { _n = 0; _isi = null; tutup(); perbaruiIkon(false); return; }
  let L = bacaLihat(); const awal = kbLonceng(_akun, null, L || {});
  if (!L) { L = kbTandai(awal); simpanLihat(L); }
  _isi = kbLonceng(_akun, null, L);
  const tadi = _n; _n = _isi.n; perbaruiIkon(!ganti && _n > tadi);
  if (_buka) { tandaiDibuka(); gambar(); }
}

function tandaiDibuka() { if (!_isi) return; simpanLihat(kbTandai(_isi)); _isi = kbLonceng(_akun, null, kbTandai(_isi)); _n = 0; perbaruiIkon(false); }
const lembar = () => document.getElementById('lembarLonceng');
function buka() { const el = lembar(); if (!el || !_akun) return; _buka = true; _kabar = null; tandaiDibuka(); gambar(); el.hidden = false; el.classList.remove('masuk'); void el.offsetWidth; el.classList.add('masuk'); }
function tutup() { const el = lembar(); _buka = false; if (el) el.hidden = true; }

function gambar() {
  const el = lembar(); if (!el || !_isi) return; const I = _isi; const owner = I.owner;
  const baris = (x, i) => h`<div class="ll-baris ${x.status} ${x.baru ? 'baru' : ''}" data-k="ll-${x.id}" style="--urut: ${Math.min(i, 12)};">
      <div class="ll-atas"><b>${x.judul}</b><span class="ket">${x.waktu}</span></div>
      <div class="ll-isi">${x.isi}</div>
      ${x.alasan ? h`<div class="ket awas-teks">Alasan: ${x.alasan}</div>` : ''}
      ${x.balasan ? h`<div class="ll-balasan">Balasan owner: ${x.balasan}</div>` : ''}
      ${owner && x.bisaBalas ? h`<div class="ll-balas"><input class="ketik-nama" type="text" maxlength="${TP_BATAS.balasan}" placeholder="Balasan untuk tablet (boleh kosong)" value="${_balas[x.id] || ''}" data-ll-ketik="${x.id}">
        <div class="kaca-btn aktif emas" data-ll="baca" data-id="${x.id}">${_sibuk === x.id ? 'menyimpan…' : x.tindakan === 'pesan' ? 'Tandai dibaca' : 'Sudah diperiksa'}</div></div>` : ''}
      <div class="ll-kaki"><span class="tautan" data-ll="buka" data-layar="${x.layar}">Buka di ${KB_NAMA_LAYAR[x.layar] || x.layar} ›</span></div></div>`;
  pasang(el, h`<div class="ll-kepala"><div><b class="serif" style="font-size: 18px;">Kabar & pesan</b><div class="ket">${owner ? (I.menunggu ? I.menunggu + ' menunggu keputusan owner' : 'tidak ada yang menunggu') : 'permintaan dari akun ini & jawaban owner'}</div></div>
      <button type="button" class="ll-tutup" data-ll="tutup" aria-label="Tutup">×</button></div>
    ${_kabar ? h`<div class="pita-info ${_kabar.awas ? 'awas' : 'emas'}" data-k="ll-kabar">${_kabar.teks}</div>` : ''}
    <div class="ll-daftar" data-k="ll-daftar">${I.daftar.length ? I.daftar.map(baris) : h`<div class="ket" data-k="ll-kosong" style="padding: 10px 2px;">${owner ? 'Belum ada pesan atau permintaan yang menunggu.' : 'Belum ada permintaan dari akun ini.'}</div>`}</div>
    ${I.lebih ? h`<div class="ket" data-k="ll-lebih">+ ${I.lebih} kabar lebih lama — lihat di ${owner ? 'Uang › titipan dan Menu › Toko ini › Peran & persetujuan › Persetujuan' : 'Menu'}</div>` : ''}`);
}

async function tandaiBaca(id) {
  if (!_akun || _akun.jenis !== 'owner' || _sibuk) return;
  const r = tpSusunPutus(id, 'dibaca', { balasan: _balas[id] || '' }, waktuSekarang(_opsi.sekarang() || undefined));
  if (r.tolak) { _kabar = { teks: r.tolak, awas: true }; gambar(); return; }
  _sibuk = id; gambar();
  try {
    const x = await tulisDokumen(r.dokumen || [], r.hapus);
    if (x && x.gagal) _kabar = { teks: 'DITOLAK: ' + x.pesan, awas: true };
    else { _kabar = { teks: kabarKiriman(x, (r.patch || {}).kabar || 'Tersimpan'), awas: false }; delete _balas[id]; }
  } catch (e) { _kabar = { teks: 'GAGAL menyimpan: ' + String((e && e.message) || e), awas: true }; }
  _sibuk = ''; loncengSegarkan(_akun); gambar();
}

/** Sekali dari app.js: { pindah(layar), sekarang() }. Ketukan lonceng di layar mana pun (delegasi dokumen), ketikan balasan, tutup di luar / Esc. */
export function pasangLonceng(opsi) {
  _opsi = Object.assign({}, _opsi, opsi || {});
  document.addEventListener('click', (ev) => {
    const t = ev.target; if (!t || !t.closest) return;
    if (t.closest('[data-lonceng]')) { ev.preventDefault(); if (_buka) tutup(); else buka(); return; }
    const a = t.closest('[data-ll]');
    if (a) {
      const k = a.dataset.ll;
      if (k === 'tutup') tutup();
      else if (k === 'buka') { tutup(); _opsi.pindah(a.dataset.layar || 'menu'); }
      else if (k === 'baca') tandaiBaca(a.dataset.id);
      return;
    }
    if (_buka && !t.closest('#lembarLonceng')) tutup();
  });
  document.addEventListener('input', (ev) => { const t = ev.target; if (t && t.dataset && t.dataset.llKetik) _balas[t.dataset.llKetik] = String(t.value || '').slice(0, TP_BATAS.balasan); });
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && _buka) tutup(); });
}
