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

let _lcN = 0; let _lcIsi = null; let _lcAkun = null; let _lcBuka = false; let _lcSibuk = ''; let _lcKabar = null;
const _lcBalas = {};
let _lcOpsi = { pindah: () => {}, sekarang: () => null, berbunyi: () => {} };

/** Angka di lonceng sekarang (kabar belum dibuka di perangkat ini). */
export const loncengAngka = () => _lcN;
const lcTeksAngka = (n) => (n > 99 ? '99+' : n ? String(n) : '');
/** Ikon lonceng untuk kepala layar (HTML mentah). Satu bentuk di semua layar; angkanya diperbarui app.js tanpa menggambar ulang layarnya. */
export function pintuLonceng() {
  return '<button type="button" class="lonceng' + (_lcN ? ' ada' : '') + '" data-lonceng data-k="lonceng" aria-label="Kabar &amp; pesan' + (_lcN ? ' · ' + _lcN + ' baru' : '') + '" title="Kabar &amp; pesan">'
    + '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="lc-badan" d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.6 2.1H4.4z"/><path class="lc-anting" d="M10 20.6a2.1 2.1 0 0 0 4 0"/></svg>'
    + '<span class="lonceng-n" data-lonceng-n>' + lcTeksAngka(_lcN) + '</span></button>';
}
export const loncengMentah = () => mentah(pintuLonceng());

const lcUid = () => String((_lcAkun && _lcAkun.uid) || '');
function lcBacaLihat() { try { return kbBacaLihat(localStorage.getItem(KB_LIHAT), lcUid()); } catch (e) { return null; } }
function lcSimpanLihat(peta) { try { localStorage.setItem(KB_LIHAT, kbTulisLihat(localStorage.getItem(KB_LIHAT), lcUid(), peta)); } catch (e) { /* perangkat menolak: angka kembali muncul sesudah dimuat ulang */ } }

/** Perbarui semua ikon lonceng yang tergambar (angka, kelas, goyang bila bertambah). */
function lcPerbaruiIkon(naik) {
  document.querySelectorAll('[data-lonceng]').forEach((b) => {
    b.classList.toggle('ada', _lcN > 0); b.setAttribute('aria-label', 'Kabar & pesan' + (_lcN ? ' · ' + _lcN + ' baru' : ''));
    const s = b.querySelector('[data-lonceng-n]'); if (s && s.textContent !== lcTeksAngka(_lcN)) { s.textContent = lcTeksAngka(_lcN); s.classList.remove('letup'); void s.offsetWidth; s.classList.add('letup'); }
    if (naik) { b.classList.remove('goyang'); void b.offsetWidth; b.classList.add('goyang'); }
  });
}

/**
 * Hitung ulang dari data (app.js: tiap data / akun berubah). akun = akun yang dipakai layar. Kabar baru sejak tadi = lonceng bergoyang.
 * Perangkat yang belum pernah menyimpan peta untuk akun ini: semua yang ada sekarang dianggap sudah dibuka (angka tidak meledak di pemakaian pertama).
 */
export function loncengSegarkan(akun) {
  const ganti = !_lcAkun || !akun || _lcAkun.uid !== akun.uid || _lcAkun.jenis !== akun.jenis; _lcAkun = akun || null;
  if (!_lcAkun) { _lcN = 0; _lcIsi = null; lcTutup(); lcPerbaruiIkon(false); return; }
  let L = lcBacaLihat(); const awal = kbLonceng(_lcAkun, null, L || {});
  if (!L) { L = kbTandai(awal); lcSimpanLihat(L); }
  _lcIsi = kbLonceng(_lcAkun, null, L);
  const tadi = _lcN; _lcN = _lcIsi.n; lcPerbaruiIkon(!ganti && _lcN > tadi);
  if (_lcBuka) { lcTandaiDibuka(); lcGambar(); }
}

function lcTandaiDibuka() { if (!_lcIsi) return; lcSimpanLihat(kbTandai(_lcIsi)); _lcIsi = kbLonceng(_lcAkun, null, kbTandai(_lcIsi)); _lcN = 0; lcPerbaruiIkon(false); }
const lcLembar = () => document.getElementById('lembarLonceng');
function lcBuka() { const el = lcLembar(); if (!el || !_lcAkun) return; _lcBuka = true; _lcKabar = null; lcTandaiDibuka(); lcGambar(); el.hidden = false; el.classList.remove('masuk'); void el.offsetWidth; el.classList.add('masuk'); }
function lcTutup() { const el = lcLembar(); _lcBuka = false; if (el) el.hidden = true; }

function lcGambar() {
  const el = lcLembar(); if (!el || !_lcIsi) return; const I = _lcIsi; const owner = I.owner;
  const baris = (x, i) => h`<div class="ll-baris ${x.status} ${x.baru ? 'baru' : ''}" data-k="ll-${x.id}" style="--urut: ${Math.min(i, 12)};">
      <div class="ll-atas"><b>${x.judul}</b><span class="ket">${x.waktu}</span></div>
      <div class="ll-isi">${x.isi}</div>
      ${x.alasan ? h`<div class="ket awas-teks">Alasan: ${x.alasan}</div>` : ''}
      ${x.balasan ? h`<div class="ll-balasan">Balasan owner: ${x.balasan}</div>` : ''}
      ${owner && x.bisaBalas ? h`<div class="ll-balas"><input class="ketik-nama" type="text" maxlength="${TP_BATAS.balasan}" placeholder="Balasan untuk tablet (boleh kosong)" value="${_lcBalas[x.id] || ''}" data-ll-ketik="${x.id}">
        <div class="kaca-btn aktif emas" data-ll="baca" data-id="${x.id}">${_lcSibuk === x.id ? 'menyimpan…' : x.tindakan === 'pesan' ? 'Tandai dibaca' : 'Sudah diperiksa'}</div></div>` : ''}
      <div class="ll-kaki"><span class="tautan" data-ll="buka" data-layar="${x.layar}">Buka di ${KB_NAMA_LAYAR[x.layar] || x.layar} ›</span></div></div>`;
  pasang(el, h`<div class="ll-kepala"><div><b class="serif" style="font-size: 18px;">Kabar & pesan</b><div class="ket">${owner ? (I.menunggu ? I.menunggu + ' menunggu keputusan owner' : 'tidak ada yang menunggu') : 'permintaan dari akun ini & jawaban owner'}</div></div>
      <button type="button" class="ll-tutup" data-ll="tutup" aria-label="Tutup">×</button></div>
    ${_lcKabar ? h`<div class="pita-info ${_lcKabar.awas ? 'awas' : 'emas'}" data-k="ll-kabar">${_lcKabar.teks}</div>` : ''}
    <div class="ll-daftar" data-k="ll-daftar">${I.daftar.length ? I.daftar.map(baris) : h`<div class="ket" data-k="ll-kosong" style="padding: 10px 2px;">${owner ? 'Belum ada pesan atau permintaan yang menunggu.' : 'Belum ada permintaan dari akun ini.'}</div>`}</div>
    ${I.lebih ? h`<div class="ket" data-k="ll-lebih">+ ${I.lebih} kabar lebih lama — lihat di ${owner ? 'Uang › titipan dan Menu › Toko ini › Peran & persetujuan › Persetujuan' : 'Menu'}</div>` : ''}`);
}

async function lcTandaiBaca(id) {
  if (!_lcAkun || _lcAkun.jenis !== 'owner' || _lcSibuk) return;
  const r = tpSusunPutus(id, 'dibaca', { balasan: _lcBalas[id] || '' }, waktuSekarang(_lcOpsi.sekarang() || undefined));
  if (r.tolak) { _lcKabar = { teks: r.tolak, awas: true }; lcGambar(); return; }
  _lcSibuk = id; lcGambar();
  try {
    const x = await tulisDokumen(r.dokumen || [], r.hapus);
    if (x && x.gagal) _lcKabar = { teks: 'DITOLAK: ' + x.pesan, awas: true };
    else { _lcKabar = { teks: kabarKiriman(x, (r.patch || {}).kabar || 'Tersimpan'), awas: false }; delete _lcBalas[id]; }
  } catch (e) { _lcKabar = { teks: 'GAGAL menyimpan: ' + String((e && e.message) || e), awas: true }; }
  _lcSibuk = ''; loncengSegarkan(_lcAkun); lcGambar();
}

/** Sekali dari app.js: { pindah(layar), sekarang() }. Ketukan lonceng di layar mana pun (delegasi dokumen), ketikan balasan, tutup di luar / Esc. */
export function pasangLonceng(opsi) {
  _lcOpsi = Object.assign({}, _lcOpsi, opsi || {});
  document.addEventListener('click', (ev) => {
    const t = ev.target; if (!t || !t.closest) return;
    if (t.closest('[data-lonceng]')) { ev.preventDefault(); if (_lcBuka) lcTutup(); else lcBuka(); return; }
    const a = t.closest('[data-ll]');
    if (a) {
      const k = a.dataset.ll;
      if (k === 'tutup') lcTutup();
      else if (k === 'buka') { lcTutup(); _lcOpsi.pindah(a.dataset.layar || 'menu'); }
      else if (k === 'baca') lcTandaiBaca(a.dataset.id);
      return;
    }
    if (_lcBuka && !t.closest('#lembarLonceng')) lcTutup();
  });
  document.addEventListener('input', (ev) => { const t = ev.target; if (t && t.dataset && t.dataset.llKetik) _lcBalas[t.dataset.llKetik] = String(t.value || '').slice(0, TP_BATAS.balasan); });
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && _lcBuka) lcTutup(); });
}
