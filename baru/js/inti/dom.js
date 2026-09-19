// Penggambar layar tanpa kerangka kerja: keadaan → HTML (string) → dipasang ke akar.
// Ketukan lewat DELEGASI atribut data-aksi — bukan onclick berisi id sebagai kode
// (memori: onclick-json-tiga-keluarga — id yang menjadi kode adalah keluarga cacat lama).
export const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

/** Template bertanda `h`: nilai yang disisipkan di-escape; sisipkan HTML mentah lewat mentah(). */
export function h(bagian, ...nilai) {
  let out = '';
  bagian.forEach((b, i) => {
    out += b;
    if (i < nilai.length) {
      const v = nilai[i];
      if (v && v.__mentah) out += v.html;
      else if (Array.isArray(v)) out += v.map((x) => (x && x.__mentah ? x.html : esc(x))).join('');
      else out += esc(v);
    }
  });
  return { __mentah: true, html: out };
}
export const mentah = (html) => ({ __mentah: true, html: String(html) });
export const gabung = (daftar) => mentah(daftar.map((x) => (x && x.__mentah ? x.html : esc(x))).join(''));

/** Tempel HTML ke akar; kotak isian yang sedang fokus dipertahankan (id + posisi kursor). */
export function pasang(akar, isi) {
  const aktif = document.activeElement;
  const idFokus = aktif && akar.contains(aktif) && aktif.id ? aktif.id : null;
  const posisi = idFokus && typeof aktif.selectionStart === 'number' ? aktif.selectionStart : null;
  akar.innerHTML = isi && isi.__mentah ? isi.html : String(isi || '');
  if (idFokus) {
    const el = document.getElementById(idFokus);
    if (el) { el.focus(); if (posisi !== null && typeof el.setSelectionRange === 'function') { try { el.setSelectionRange(posisi, posisi); } catch (e) { /* jenis input tanpa kursor */ } } }
  }
}

/**
 * Delegasi ketukan & ketikan: elemen ber-atribut data-aksi="nama" (+ data-* lain sebagai argumen).
 * penangan = { nama: (arg, el, ev) => … }. Dipasang SEKALI di akar; isi boleh diganti kapan saja.
 */
export function delegasi(akar, penangan) {
  akar.addEventListener('click', (ev) => {
    const el = ev.target.closest('[data-aksi]');
    if (!el || !akar.contains(el)) return;
    const f = penangan[el.dataset.aksi];
    if (!f) return;
    ev.preventDefault();
    f(Object.assign({}, el.dataset), el, ev);
  });
  akar.addEventListener('input', (ev) => {
    const el = ev.target.closest('[data-ketik]');
    if (!el) return;
    const f = penangan[el.dataset.ketik];
    if (f) f(el.value, el, ev);
  });
  akar.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Enter') return;
    const el = ev.target.closest('[data-enter]');
    if (!el) return;
    const f = penangan[el.dataset.enter];
    if (f) { ev.preventDefault(); f(el.value, el, ev); }
  });
}
