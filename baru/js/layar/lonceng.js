// LONCENG KABAR & PESAN (owner 23 Nov 2026: "ada ikon notifikasi untuk pesan di aplikasi sistem mac/hp/tablet" — "Lonceng + balas langsung").
// Ikon lonceng di kepala tiap layar (Mac, HP, tablet) + lembar daftar kabar. Isi & angka dari kabar-baru-logika (kbLonceng): owner = permintaan yang
// menunggu, akun tablet = permintaannya sendiri + jawaban owner. Owner menandai PESAN / kabar barang masuk dibaca + membalas langsung dari sini — lewat
// tpSusunPutus, pintu yang sama dengan Uang › titipan (tidak ada jalan tulis baru). Titipan uang, nego, harga, bon: tombol membuka layarnya.
// Lembar dibuka = semua kabar yang tampil dianggap sudah dibuka (angka kembali nol); peta "sudah dibuka" per akun di perangkat ini (localStorage).
// owner 23 Nov 2026 ("bisa balas pesan … seperti WhatsApp … chattingan" → "Obrolan di lonceng"): lembar punya dua tab — OBROLAN (utas owner ↔ tablet:
// gelembung kiri-kanan, label hari, centang, kotak ketik di bawah) dan KABAR (titipan, barang masuk, nego, harga, bon). Owner membuka Obrolan = pesan tablet
// yang menunggu ditandai DIBACA (tpSusunPutus tanpa balasan → tablet melihat ✓✓, tanpa notifikasi); balasan = pesan owner baru (kbSusunPesanOwner).
// Tablet menulis lewat tpSusunPesan (pintu yang sama dengan Menu › pesan untuk owner). Tidak ada koleksi atau rules baru.
import { h, mentah, pasang } from '../inti/dom.js';
import { tulisDokumen, kabarKiriman } from '../data/toko.js';
import { kbLonceng, kbTandai, kbBacaLihat, kbTulisLihat, kbSusunPesanOwner, kbSusunTugasOwner, KB_LIHAT, KB_NAMA_LAYAR } from './kabar-baru-logika.js';
import { tpSusunPutus, tpSusunPesan, TP_BATAS } from './titipan-logika.js';
import { waktuSekarang } from './jual-logika.js';

let _lcN = 0; let _lcIsi = null; let _lcAkun = null; let _lcBuka = false; let _lcSibuk = ''; let _lcKabar = null;
const _lcBalas = {}; let _lcTulis = ''; let _lcJenis = 'pesan';   // owner 28 Nov 2026 (rules v27): kiriman owner = pesan / tugas / tugas wajib foto   // _lcTulis = pesan obrolan yang sedang diketik (owner & tablet)
let _lcTab = 'obrolan'; let _lcKeBawah = false; const _lcMenandai = new Set();   // tab yang tampil · gulir ke pesan terbaru · id yang sedang ditandai dibaca
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
const lcWaktu = () => waktuSekarang(_lcOpsi.sekarang() || undefined);
// owner 26 Nov 2026 ("pasang notifikasi"): pengingat jatuh — sumbernya & pintu bukanya dipasang app.js lewat loncengPengingat
let _lcPg = { ambil: () => [], buka: null };
export function loncengPengingat(o) { _lcPg = Object.assign({}, _lcPg, o || {}); }
const lcPengingat = () => { try { return _lcPg.ambil(_lcAkun) || []; } catch (e) { return []; } };
const lcHitung = (L) => kbLonceng(_lcAkun, null, L, lcWaktu().tanggal, lcPengingat());
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
 * Lembar terbuka di tab Obrolan = pesan yang datang langsung terbaca (gulir ikut turun bila sedang di bawah).
 */
export function loncengSegarkan(akun) {
  const ganti = !_lcAkun || !akun || _lcAkun.uid !== akun.uid || _lcAkun.jenis !== akun.jenis; _lcAkun = akun || null;
  if (!_lcAkun) { _lcN = 0; _lcIsi = null; lcTutup(); lcPerbaruiIkon(false); return; }
  let L = lcBacaLihat(); const awal = lcHitung(L || {});
  if (!L) { L = kbTandai(awal); lcSimpanLihat(L); }
  _lcIsi = lcHitung(L);
  const tadi = _lcN; _lcN = _lcIsi.n; lcPerbaruiIkon(!ganti && _lcN > tadi);
  if (_lcBuka) { if (_lcTab === 'obrolan' && lcDiBawah()) _lcKeBawah = true; lcTandaiDibuka(); lcGambar(); }
}

/** Tab yang tampil = sudah dibuka (peta perangkat). Owner di tab Obrolan: pesan tablet yang menunggu ditandai dibaca di server. */
function lcTandaiDibuka() {
  if (!_lcIsi) return; const L = kbTandai(_lcIsi, _lcTab); lcSimpanLihat(L); _lcIsi = lcHitung(L); _lcN = _lcIsi.n; lcPerbaruiIkon(false);
  if (_lcTab === 'obrolan' && _lcIsi.owner && !document.hidden) lcBacaSemua();
}
const lcLembar = () => document.getElementById('lembarLonceng');
const lcGulir = () => { const el = lcLembar(); return el ? el.querySelector('[data-lo-gulir]') : null; };
const lcDiBawah = () => { const g = lcGulir(); return !g || g.scrollHeight - g.scrollTop - g.clientHeight < 90; };
function lcBuka() {
  const el = lcLembar(); if (!el || !_lcAkun) return; _lcBuka = true; _lcKabar = null; _lcMenandai.clear();
  if (_lcIsi) _lcTab = _lcIsi.nObrolan ? 'obrolan' : _lcIsi.nKabar ? 'kabar' : _lcTab;   // yang baru dibuka dulu; tidak ada yang baru = tab terakhir
  _lcKeBawah = true; lcTandaiDibuka(); lcGambar(); el.hidden = false; el.classList.remove('masuk'); void el.offsetWidth; el.classList.add('masuk'); lcGulirBawah();
}
function lcTutup() { const el = lcLembar(); _lcBuka = false; if (el) el.hidden = true; }
function lcPilihTab(tab) { if (tab !== 'obrolan' && tab !== 'kabar') return; _lcTab = tab; _lcKabar = null; _lcKeBawah = tab === 'obrolan'; lcTandaiDibuka(); lcGambar(); lcGulirBawah(); }
function lcGulirBawah() { if (!_lcKeBawah) return; const g = lcGulir(); if (!g || !g.clientHeight) return; _lcKeBawah = false; g.scrollTop = g.scrollHeight; }   // lembar masih tersembunyi = tunda sampai tampil

const IKON_KIRIM = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12 19.5 4.8l-3.6 14.6-4.3-5.2z"/><path d="M11.6 14.2 19.5 4.8"/></svg>';
function lcGambarObrolan(I) {
  const owner = I.owner;
  const gel = (x, i) => { const saya = owner ? x.dari === 'owner' : x.dari === 'tablet';
    return h`${x.pisah ? h`<div class="lo-hari" data-k="loh-${x.kunci}"><span>${x.pisah}</span></div>` : ''}<div class="lo-gel ${saya ? 'saya' : 'dia'} ${x.baru ? 'baru' : ''} ${x.namaTampil ? 'awal' : ''}" data-k="lo-${x.kunci}" style="--urut: ${Math.min(Math.max(0, I.obrolan.length - 1 - i), 8)};">
      ${!saya && x.namaTampil ? h`<div class="lo-nama">${x.nama}</div>` : ''}<div class="lo-teks">${x.teks}</div>
      <div class="lo-kaki">${x.jam}${saya ? h`<span class="lo-centang ${x.centang === 2 ? 'dibaca' : ''}" title="${x.centang === 2 ? 'dibaca owner' : 'terkirim'}">${x.centang === 2 ? '✓✓' : '✓'}</span>` : ''}</div></div>`; };
  return h`<div class="lo-wadah" data-k="lo-wadah">
    <div class="lo-gulir" data-lo-gulir data-k="lo-gulir">
      ${I.lebihObrolan ? h`<div class="ket lo-lama" data-k="lo-lama">+ ${I.lebihObrolan} pesan lebih lama</div>` : ''}
      ${I.obrolan.length ? I.obrolan.map(gel) : h`<div class="lo-kosong" data-k="lo-kosong"><b>Belum ada obrolan</b><span class="ket">${owner ? 'Tulis pesan untuk tablet di bawah — balasan tablet muncul di sini.' : 'Tulis pesan untuk owner di bawah — balasan owner muncul di sini.'}</span></div>`}
    </div>
    ${owner ? h`<div class="jalur bungkus rapat" data-k="lo-jenis" style="padding: 0 2px 4px;">${[['pesan', 'Pesan'], ['tugas', 'Tugas'], ['tugasFoto', 'Tugas + wajib foto']].map(([k, n]) => h`<div class="seg ${_lcJenis === k ? 'aktif' : ''}" data-ll="jenis" data-jenis="${k}">${n}</div>`)}</div>` : ''}
    <div class="lo-tulis" data-k="lo-tulis"><textarea class="ketik-nama" rows="1" maxlength="${TP_BATAS.pesan}" placeholder="${owner ? (_lcJenis === 'pesan' ? 'Tulis pesan untuk tablet…' : _lcJenis === 'tugas' ? 'Tulis tugas untuk penjaga — dijawab Selesai di tablet…' : 'Tulis tugas — penjaga menjawab dengan FOTO…') : 'Tulis pesan untuk owner…'}" aria-label="Tulis pesan" data-ll-tulis="1">${_lcTulis}</textarea>
      <button type="button" class="lo-kirim ${_lcSibuk === 'kirim' ? 'sibuk' : ''}" data-ll="kirim" aria-label="Kirim" title="Kirim">${mentah(IKON_KIRIM)}</button></div>
    <div class="ket lo-tip" data-k="lo-tip">${owner ? (_lcJenis === 'pesan' ? 'sampai di lonceng & bilah notifikasi tablet' : 'tugas muncul di Menu tablet sampai dijawab' + (_lcJenis === 'tugasFoto' ? ' — dengan foto (tablet memotret hanya untuk tugas ini)' : '')) : 'sampai di lonceng & notifikasi HP / Mac owner'} · paling banyak ${TP_BATAS.pesan} huruf</div></div>`;
}
function lcGambarKabar(I) {
  const owner = I.owner;
  const baris = (x, i) => h`<div class="ll-baris ${x.status} ${x.baru ? 'baru' : ''}" data-k="ll-${x.id}" style="--urut: ${Math.min(i, 12)};">
      <div class="ll-atas"><b>${x.judul}</b><span class="ket">${x.waktu}</span></div>
      <div class="ll-isi">${x.isi}</div>
      ${x.alasan ? h`<div class="ket awas-teks">Alasan: ${x.alasan}</div>` : ''}
      ${x.balasan ? h`<div class="ll-balasan">Balasan owner: ${x.balasan}</div>` : ''}
      ${owner && x.bisaBalas ? h`<div class="ll-balas"><input class="ketik-nama" type="text" maxlength="${TP_BATAS.balasan}" placeholder="Balasan untuk tablet (boleh kosong)" value="${_lcBalas[x.id] || ''}" data-ll-ketik="${x.id}">
        <div class="kaca-btn aktif emas" data-ll="baca" data-id="${x.id}">${_lcSibuk === x.id ? 'menyimpan…' : 'Sudah diperiksa'}</div></div>` : ''}
      <div class="ll-kaki"><span class="tautan" data-ll="buka" data-layar="${x.layar}">Buka di ${KB_NAMA_LAYAR[x.layar] || x.layar} ›</span></div></div>`;
  return h`<div class="ll-daftar" data-k="ll-daftar">${I.daftar.length ? I.daftar.map(baris) : h`<div class="ket" data-k="ll-kosong" style="padding: 10px 2px;">${owner ? 'Tidak ada titipan atau permintaan yang menunggu.' : 'Belum ada permintaan dari akun ini.'}</div>`}</div>
    ${I.lebih ? h`<div class="ket" data-k="ll-lebih">+ ${I.lebih} kabar lebih lama — lihat di ${owner ? 'Uang › titipan dan Menu › Toko ini › Peran & persetujuan › Persetujuan' : 'Menu'}</div>` : ''}`;
}
function lcGambar() {
  const el = lcLembar(); if (!el || !_lcIsi) return; const I = _lcIsi; const owner = I.owner; const ob = _lcTab === 'obrolan';
  el.classList.toggle('tab-obrolan', ob);
  const tab = (k, nama, n) => h`<button type="button" class="ll-tab ${_lcTab === k ? 'pilih' : ''}" role="tab" aria-selected="${_lcTab === k ? 'true' : 'false'}" data-ll="tab" data-tab="${k}">${nama}${n ? h`<span class="ll-tab-n">${n > 99 ? '99+' : n}</span>` : ''}</button>`;
  pasang(el, h`<div class="ll-kepala"><div><b class="serif" style="font-size: 18px;">${ob ? (owner ? 'Obrolan dengan tablet' : 'Obrolan dengan owner') : 'Kabar'}</b><div class="ket">${ob ? (owner ? 'pesan tablet terbaca saat obrolan ini dibuka' : '✓ terkirim · ✓✓ dibaca owner') : owner ? (I.menunggu ? I.menunggu + ' menunggu keputusan owner' : 'tidak ada yang menunggu') : 'permintaan dari akun ini & jawaban owner'}</div></div>
      <button type="button" class="ll-tutup" data-ll="tutup" aria-label="Tutup">×</button></div>
    <div class="ll-tabs" role="tablist" data-k="ll-tabs" style="--x: ${ob ? 0 : 1};">${tab('obrolan', 'Obrolan', I.nObrolan)}${tab('kabar', 'Kabar', I.nKabar)}<span class="ll-tab-garis" aria-hidden="true"></span></div>
    ${_lcKabar ? h`<div class="pita-info ${_lcKabar.awas ? 'awas' : 'emas'}" data-k="ll-kabar">${_lcKabar.teks}</div>` : ''}
    ${ob ? lcGambarObrolan(I) : lcGambarKabar(I)}`);
  lcGulirBawah();
}

// Kirim satu pesan obrolan: owner → kbSusunPesanOwner (pesan owner ke tablet), akun tablet → tpSusunPesan (pesan ke owner). Lewat pintu tulis biasa.
async function lcKirim() {
  if (!_lcAkun || _lcSibuk) return;
  const w = lcWaktu(); const r = _lcAkun.jenis !== 'owner' ? tpSusunPesan(_lcTulis, _lcAkun, w) : _lcJenis === 'pesan' ? kbSusunPesanOwner(_lcTulis, w, _lcAkun) : kbSusunTugasOwner(_lcTulis, _lcJenis === 'tugasFoto', w, _lcAkun, '');
  if (r.tolak) { _lcKabar = { teks: r.tolak, awas: true }; lcGambar(); return; }
  _lcSibuk = 'kirim'; _lcKabar = null; lcGambar();
  try {
    const x = await tulisDokumen(r.dokumen || [], r.hapus);
    if (x && x.gagal) _lcKabar = { teks: 'DITOLAK: ' + x.pesan, awas: true };
    else { _lcTulis = ''; _lcKeBawah = true; const k = document.querySelector('[data-ll-tulis]'); if (k) { k.value = ''; k.style.height = ''; }
      if (x && x.antre) _lcKabar = { teks: kabarKiriman(x, 'Pesan tersimpan'), awas: false }; else if (_lcJenis !== 'pesan' && r.patch) _lcKabar = { teks: r.patch.kabar, awas: false }; }   // tanpa internet: menunggu dikirim (kalimat antrean biasa)
  } catch (e) { _lcKabar = { teks: 'GAGAL mengirim: ' + String((e && e.message) || e), awas: true }; }
  _lcSibuk = ''; loncengSegarkan(_lcAkun); lcGambar();
}

// Owner membuka Obrolan: semua pesan tablet yang menunggu → dibaca (tanpa balasan; satu kiriman). Id yang sedang / sudah dicoba tidak dikirim ulang
// sampai lembar dibuka lagi (ditolak server = tidak berputar).
async function lcBacaSemua() {
  if (!_lcAkun || _lcAkun.jenis !== 'owner' || !_lcIsi) return;
  const ids = _lcIsi.belumDibaca.filter((id) => !_lcMenandai.has(id)); if (!ids.length) return;
  const w = lcWaktu(); const dok = [];
  ids.forEach((id) => { _lcMenandai.add(id); const r = tpSusunPutus(id, 'dibaca', { balasan: '' }, w); if (!r.tolak) (r.dokumen || []).forEach((d) => dok.push(d)); });
  if (!dok.length) return;
  try { const x = await tulisDokumen(dok); if (x && x.gagal) { _lcKabar = { teks: 'Tanda dibaca DITOLAK: ' + x.pesan, awas: true }; if (_lcBuka) lcGambar(); } }
  catch (e) { _lcKabar = { teks: 'GAGAL menandai dibaca: ' + String((e && e.message) || e), awas: true }; if (_lcBuka) lcGambar(); }
}

// Kabar barang masuk (tab Kabar, owner): tandai sudah diperiksa + balasan — pintu yang sama dengan Uang › titipan.
async function lcTandaiBaca(id) {
  if (!_lcAkun || _lcAkun.jenis !== 'owner' || _lcSibuk) return;
  const r = tpSusunPutus(id, 'dibaca', { balasan: _lcBalas[id] || '' }, lcWaktu());
  if (r.tolak) { _lcKabar = { teks: r.tolak, awas: true }; lcGambar(); return; }
  _lcSibuk = id; lcGambar();
  try {
    const x = await tulisDokumen(r.dokumen || [], r.hapus);
    if (x && x.gagal) _lcKabar = { teks: 'DITOLAK: ' + x.pesan, awas: true };
    else { _lcKabar = { teks: kabarKiriman(x, (r.patch || {}).kabar || 'Tersimpan'), awas: false }; delete _lcBalas[id]; }
  } catch (e) { _lcKabar = { teks: 'GAGAL menyimpan: ' + String((e && e.message) || e), awas: true }; }
  _lcSibuk = ''; loncengSegarkan(_lcAkun); lcGambar();
}

const lcTinggi = (k) => { k.style.height = 'auto'; k.style.height = Math.min(k.scrollHeight, 132) + 'px'; };   // kotak ketik ikut tinggi tulisannya (paling 5 baris)
/** Sekali dari app.js: { pindah(layar), sekarang() }. Ketukan lonceng di layar mana pun (delegasi dokumen), ketikan, Enter = kirim (papan ketik fisik), tutup di luar / Esc. */
export function pasangLonceng(opsi) {
  _lcOpsi = Object.assign({}, _lcOpsi, opsi || {});
  document.addEventListener('click', (ev) => {
    const t = ev.target; if (!t || !t.closest) return;
    if (t.closest('[data-lonceng]')) { ev.preventDefault(); if (_lcBuka) lcTutup(); else lcBuka(); return; }
    const a = t.closest('[data-ll]');
    if (a) {
      const k = a.dataset.ll;
      if (k === 'tutup') lcTutup();
      else if (k === 'buka') { lcTutup(); if (a.dataset.layar === 'pengingat' && _lcPg.buka) _lcPg.buka(); else _lcOpsi.pindah(a.dataset.layar || 'menu'); }
      else if (k === 'baca') lcTandaiBaca(a.dataset.id);
      else if (k === 'kirim') { lcKirim(); const tk = document.querySelector('[data-ll-tulis]'); if (tk) tk.focus(); }
      else if (k === 'tab') lcPilihTab(a.dataset.tab);
      else if (k === 'jenis') { _lcJenis = ['pesan', 'tugas', 'tugasFoto'].indexOf(a.dataset.jenis) >= 0 ? a.dataset.jenis : 'pesan'; lcGambar(); }
      return;
    }
    if (_lcBuka && !t.closest('#lembarLonceng')) lcTutup();
  });
  document.addEventListener('input', (ev) => { const t = ev.target; if (!t || !t.dataset) return; if (t.dataset.llKetik) _lcBalas[t.dataset.llKetik] = String(t.value || '').slice(0, TP_BATAS.balasan);
    if (t.dataset.llTulis) { _lcTulis = String(t.value || '').slice(0, TP_BATAS.pesan); lcTinggi(t); } });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && _lcBuka) { lcTutup(); return; }
    const t = ev.target; if (!_lcBuka || !t || !t.dataset || !t.dataset.llTulis || ev.key !== 'Enter' || ev.shiftKey || ev.isComposing) return;
    let fisik = false; try { fisik = matchMedia('(pointer: fine)').matches; } catch (e) { /* anggap layar sentuh */ }
    if (fisik) { ev.preventDefault(); lcKirim(); }   // Mac / papan ketik fisik: Enter = kirim, Shift+Enter = baris baru; layar sentuh: Enter = baris baru
  });
  document.addEventListener('visibilitychange', () => { if (!document.hidden && _lcBuka && _lcTab === 'obrolan') lcTandaiDibuka(); });
}
