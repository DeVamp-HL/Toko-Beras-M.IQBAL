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

/**
 * Tempel HTML ke akar TANPA membuang elemen yang sudah ada (morf): pohon baru dibandingkan dengan yang hidup, lalu
 * atribut/teksnya diselaraskan di tempat. Elemen yang sama tetap HIDUP antar gambar, sehingga perubahan nilainya bisa
 * bertransisi (isi wadah turun, gunung beras mengecil, angka bergulir) dan animasi masuk hanya berjalan saat elemen itu
 * benar-benar baru. Anak dicocokkan lewat kunci (atribut data-k, atau id); tanpa kunci → lewat urutan + nama tag.
 * Kotak isian yang sedang diketik tidak ditimpa (nilai & kursornya milik pemakai).
 */
export function pasang(akar, isi) {
  const t = document.createElement('template');
  t.innerHTML = isi && isi.__mentah ? isi.html : String(isi || '');
  morfAnak(akar, t.content);
}
const kunciSimpul = (n) => (n.nodeType === 1 ? (n.getAttribute('data-k') || n.id || null) : null);
function samaJenis(a, b) { return a.nodeType === b.nodeType && (a.nodeType !== 1 || (a.nodeName === b.nodeName && kunciSimpul(a) === kunciSimpul(b))); }
function morfAnak(lama, baru) {
  const berkunci = new Map();
  Array.from(lama.childNodes).forEach((n) => { const k = kunciSimpul(n); if (k) berkunci.set(k, n); });
  let penunjuk = lama.firstChild;
  Array.from(baru.childNodes).forEach((nb) => {
    const k = kunciSimpul(nb);
    let cocok = null;
    if (k && berkunci.has(k) && berkunci.get(k).nodeName === nb.nodeName) cocok = berkunci.get(k);
    else if (!k) { let c = penunjuk; while (c && kunciSimpul(c)) c = c.nextSibling; if (c && samaJenis(c, nb)) cocok = c; }
    if (cocok) {
      if (cocok !== penunjuk) lama.insertBefore(cocok, penunjuk); else penunjuk = penunjuk.nextSibling;
      if (k) berkunci.delete(k);
      morfSimpul(cocok, nb);
    } else {
      lama.insertBefore(document.importNode(nb, true), penunjuk);   // elemen BARU → animasi masuknya berjalan sekali
    }
  });
  while (penunjuk) { const berikut = penunjuk.nextSibling; lama.removeChild(penunjuk); penunjuk = berikut; }
}
function morfSimpul(lama, baru) {
  if (lama.nodeType !== 1) { if (lama.nodeValue !== baru.nodeValue) lama.nodeValue = baru.nodeValue; return; }
  const fokus = document.activeElement === lama;
  Array.from(lama.attributes).forEach((a) => { if (!baru.hasAttribute(a.name)) lama.removeAttribute(a.name); });
  Array.from(baru.attributes).forEach((a) => { if (fokus && a.name === 'value') return; if (lama.getAttribute(a.name) !== a.value) lama.setAttribute(a.name, a.value); });
  if ((lama.nodeName === 'INPUT' || lama.nodeName === 'TEXTAREA') && !fokus) { const v = baru.getAttribute('value') || ''; if (lama.value !== v) lama.value = v; }
  morfAnak(lama, baru);
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
