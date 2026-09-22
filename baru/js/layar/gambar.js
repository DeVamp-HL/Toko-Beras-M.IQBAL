// GAMBAR BARANG — dipakai layar Jual & Stok. SVG dengan ISI yang naik-turun lewat transform (bertransisi di semua peramban).
// ---------- GAMBAR BARANG (owner 19 Sep: "gambar sesuaikan sama nama") ----------
// Semua gambar punya ISI yang naik-turun lewat transform (bisa bertransisi di semua peramban; bentuk path tidak).
const idAman = (t) => String(t).replace(/[^a-zA-Z0-9]/g, '_');
const bulat2 = (n) => Math.round(Math.max(0, Math.min(1, n)) * 1000) / 1000;
/** Kotak wadah literan (potongan depan): isi di dalam kotak + GUNUNG beras di atas bibirnya. Belum ditandai → garis putus, tanpa isi. */
export function gambarWadah(w) {
  if (!w.diketahui) return `<svg class="gb wadah tak-diketahui" viewBox="0 0 64 64" aria-hidden="true"><path class="kotak" d="M8 28h48l-3 30H11z"/><text x="32" y="48" text-anchor="middle" class="tanya">?</text></svg>`;
  return `<svg class="gb wadah ${w.perluIsi ? 'perlu-isi' : ''}" viewBox="0 0 64 64" aria-hidden="true">
    <g class="gunung" style="transform: scaleY(${bulat2(w.gunung)});"><path d="M9 28 Q20 27 26 14 Q32 4 38 14 Q44 27 55 28 Z"/><circle cx="27" cy="21" r="0.9"/><circle cx="34" cy="16" r="0.9"/><circle cx="38" cy="23" r="0.9"/><circle cx="31" cy="25" r="0.9"/></g>
    <rect class="isi-dalam" x="10.5" y="28" width="43" height="29" style="transform: scaleY(${bulat2(w.dalam)});"/>
    <path class="kotak" d="M8 28h48l-3 30H11z"/><path class="bilah" d="M9.2 38h45.6M10.2 48h43.6"/>
  </svg>`;
}
/** Karung utuh (terikat di atas); isi = sisa stok relatif di kelompoknya. */
export function gambarKarung(id, isi, berat) {
  const c = 'ck_' + idAman(id);
  return `<svg class="gb karung" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><path d="M17 17 Q32 22 47 17 L51 24 Q55 42 51 59 Q32 63 13 59 Q9 42 13 24 Z"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="8" y="16" width="48" height="46" style="transform: scaleY(${bulat2(isi)});"/></g>
    <path class="kotak" d="M17 17 Q32 22 47 17 L51 24 Q55 42 51 59 Q32 63 13 59 Q9 42 13 24 Z"/><path class="ikat" d="M24 10 Q28 16 22 17M40 10 Q36 16 42 17M22 17 Q32 21 42 17"/>
    <text x="32" y="45" text-anchor="middle" class="ukuran">${berat}</text></svg>`;
}
/** Kemasan (kantong bersegel atas-bawah, berlabel angka ukurannya). */
export function gambarKemasan(id, isi, ukuran) {
  const c = 'cm_' + idAman(id);
  return `<svg class="gb kemasan" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><rect x="15" y="12" width="34" height="46" rx="5"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="15" y="12" width="34" height="46" style="transform: scaleY(${bulat2(isi)});"/></g>
    <rect class="kotak" x="15" y="12" width="34" height="46" rx="5"/><path class="bilah" d="M15 18h34M15 52h34"/><rect class="label-kantong" x="20" y="27" width="24" height="17" rx="3"/>
    <text x="32" y="40" text-anchor="middle" class="ukuran">${String(ukuran).replace('.', ',')}</text></svg>`;
}
/** Karung terbuka + serok: repack dadakan & literan yang diserok langsung dari karung. */
export function gambarKarungBuka(id, isi) {
  const c = 'cb_' + idAman(id);
  return `<svg class="gb karung buka" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><path d="M15 20 Q32 26 49 20 Q54 42 50 59 Q32 63 14 59 Q10 42 15 20 Z"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="8" y="20" width="48" height="42" style="transform: scaleY(${bulat2(isi)});"/></g>
    <path class="kotak" d="M15 20 Q32 26 49 20 Q54 42 50 59 Q32 63 14 59 Q10 42 15 20 Z"/><ellipse class="kotak" cx="32" cy="20" rx="17" ry="4.5"/>
    <path class="serok" d="M40 6 L47 20 M35 17 h14 l-2 8 h-10 z"/></svg>`;
}
/**
 * KARUNG TERBUKA di belakang wadah ("stok wadah", owner 19 Sep): mulut karung digulung ke bawah seperti di toko, isi turun tiap takar diambil.
 * Belum pernah ditandai → garis putus + "?" (tidak ditebak). Hampir habis → warna awas.
 */
export function gambarKarungStok(k) {
  const c = 'cs_' + idAman(k.merk || 'x');
  const badan = 'M14 24 Q32 29 50 24 Q55 43 51 59 Q32 63 13 59 Q9 43 14 24 Z';
  if (!k.diketahui) return `<svg class="gb karung stok tak-diketahui" viewBox="0 0 64 64" aria-hidden="true"><path class="kotak" d="${badan}"/><text x="32" y="48" text-anchor="middle" class="tanya">?</text></svg>`;
  return `<svg class="gb karung stok ${k.sisaKg <= 5 ? 'perlu-isi' : ''}" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><path d="${badan}"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="8" y="24" width="48" height="38" style="transform: scaleY(${bulat2(k.bagian)});"/></g>
    <path class="kotak" d="${badan}"/><path class="gulung" d="M12 24 Q32 31 52 24 Q54 19 50 17 Q32 23 14 17 Q10 19 12 24 Z"/><path class="bilah" d="M22 34v20M42 34v20"/>
    <text x="32" y="49" text-anchor="middle" class="ukuran">${Number(k.penuhKg) || 50}</text></svg>`;
}
export function gambarChipBarang(c, penuh) {
  const isi = (c.sisa || 0) / penuh; const id = c.jalur + '-' + c.kunci + '-' + (c.berat || '');
  if (c.jalur === 'literan') return c.wadah ? gambarWadah(c.wadah) : gambarKarungBuka(id, isi);
  if (c.jalur === 'karung') return gambarKarung(id, isi, c.berat);
  if (c.jalur === 'kemasan') return gambarKemasan(id, isi, c.ukuranKg);
  return gambarKarungBuka(id, isi);
}

