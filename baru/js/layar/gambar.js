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
// ---------- TUMPUKAN REBAH (owner 2 Okt: "gambar tumpukan beras yang ada di foto … jangan seperti sekarang cuma 1 karung berdiri") ----------
// Karung & kemasan digambar REBAH bertumpuk seperti di gudang: bantal panjang berlapis, sedikit selang-seling, telinga & jahitan di ujung karung.
// Selalu ada TUMPUK_N lapis di DOM; yang tampak mengikuti sisa di kelompoknya (penuh = tumpukan tinggi, tinggal satu = satu di lantai,
// habis = lantai bergaris putus + bekas tempatnya). Lapis yang pergi diangkat & memudar lewat kelas .pergi (transform + opacity):
// bentuk elemennya tetap sama antar gambar, jadi morf mempertahankannya dan transisinya berjalan.
const TUMPUK_N = 6;
const LANTAI = 61.5;
const n1 = (x) => Math.round(x * 10) / 10;
/**
 * Banyak lapis yang tampak: naik-turun mengikuti isi (0–1), paling sedikit satu selama masih ada, tidak pernah lebih dari jumlah barang
 * yang sebenarnya. Skalanya akar dari isi: di rak yang terbanyak 40 karung, sisa 3 dan sisa 14 masih tergambar beda (2 vs 4 lapis) —
 * skala lurus membuat semua yang di bawah 7 karung sama-sama satu lapis.
 */
function lapisTampak(isi, jumlah) {
  const j = Number(jumlah); const adaJumlah = jumlah !== undefined && jumlah !== null && isFinite(j);
  if (!(isi > 0) || (adaJumlah && !(j > 0))) return 0;
  const k = Math.max(1, Math.round(Math.sqrt(bulat2(isi)) * TUMPUK_N));
  return Math.min(TUMPUK_N, adaJumlah ? Math.min(k, Math.ceil(j - 1e-9)) : k);
}
/**
 * Lapis ke-i (0 = paling bawah) di posisi x,y (boleh sedikit miring, derajat, berporos di tengah lapis selebar L setebal T); lapis di atas
 * jumlah tampak diberi .pergi. --i = urutan naik (yang datang, bawah duluan), --j = urutan turun (yang pergi, atas duluan) — dihitung dari
 * TUMPUK_N di sini supaya CSS tidak menyimpan salinan angkanya.
 */
const lapis = (i, k, x, y, isi, miring, L, T) => `<g class="lapis${i < k ? '' : ' pergi'}" style="--i: ${i}; --j: ${TUMPUK_N - 1 - i};"><g transform="translate(${n1(x)} ${n1(y)})${miring ? ` rotate(${miring} ${n1(L / 2)} ${n1(T / 2)})` : ''}">${isi}</g></g>`;
/** Karung rebah (tampak samping) selebar L, setebal T: sisi atas-bawah menggembung, ujung kiri-kanan tertarik ke dalam dengan telinga di sudutnya. */
function bantal(L, T) {
  return `M1.7 1.3 Q${n1(L / 2)} -1.3 ${n1(L - 1.7)} 1.3 L${n1(L + 1.2)} 0 Q${n1(L - 0.8)} ${n1(T / 2)} ${n1(L + 1.2)} ${n1(T)} L${n1(L - 1.7)} ${n1(T - 1.1)} Q${n1(L / 2)} ${n1(T + 0.9)} 1.7 ${n1(T - 1.1)} L-1.2 ${n1(T)} Q0.8 ${n1(T / 2)} -1.2 0 Z`;
}
/** Jahitan zig-zag di ujung kanan karung + ekor benang yang menjuntai dari telinga bawah. */
function jahitan(L, T) {
  let d = `M${n1(L - 3.2)} 1.9`; let y = 1.9; let kiri = true;
  while (y + 1.2 <= T - 1.7) { y += 1.2; kiri = !kiri; d += ` L${n1(kiri ? L - 3.2 : L - 1.9)} ${n1(y)}`; }
  return d + ` M${n1(L + 1.2)} ${n1(T)} l0.9 1.6`;
}
/**
 * Papan angka kecil di kaki tumpukan (kiri bawah, x 0,5–18,5): berat karung / ukuran kemasan tetap terbaca walau tumpukannya habis.
 * Papannya sempit supaya tidak menutup telinga karung terbawah; huruf mengecil tiga tingkat (2 huruf 12 px, "2,5" 10,5 px, "0,25" 8,5 px)
 * dan garis dasarnya ikut turun supaya angka tetap di tengah papan.
 */
function papanUkuran(teks) {
  const t = String(teks == null ? '' : teks);
  const kelas = t.length > 3 ? ' empat-huruf' : t.length > 2 ? ' tiga-huruf' : '';
  const y = t.length > 3 ? 57 : t.length > 2 ? 57.7 : 58.2;
  return `<g class="papan-ukuran"><rect x="0.5" y="47" width="18" height="14" rx="3.2"/><text x="9.5" y="${y}" text-anchor="middle" class="ukuran${kelas}">${t}</text></g>`;
}
/**
 * Tumpukan karung rebah; isi = sisa relatif di kelompoknya, jumlah = karung yang benar-benar tersisa (tidak wajib). 25 kg lebih pendek & gemuk.
 * Rata kanan (ujung telinga kanan di x 63,2): lapis ganjil yang bergeser 1,5 ke kiri pun telinga kirinya masih di kanan papan angka.
 */
export function gambarKarung(id, isi, berat, jumlah) {
  const g = 'gk_' + idAman(id);
  const kecil = Number(berat) > 0 && Number(berat) <= 25;
  const L = kecil ? 29 : 40; const T = kecil ? 9.2 : 8.8; const P = T - 0.5; const x0 = 62 - L;
  const k = lapisTampak(isi, jumlah); const badan = bantal(L, T);
  const garis = `M3.6 ${n1(T * 0.36)} Q${n1(L / 2)} ${n1(T * 0.36 - 1.7)} ${n1(L - 4.6)} ${n1(T * 0.36)}`;
  const isiLapis = `<path class="badan" d="${badan}" fill="url(#${g})"/><path class="garis-warna" d="${garis}"/><path class="jahit" d="${jahitan(L, T)}"/>`;
  const semua = []; for (let i = 0; i < TUMPUK_N; i++) semua.push(lapis(i, k, x0 + (i % 2 ? -1.5 : 0), LANTAI - T - i * P, isiLapis));
  return `<svg class="gb karung tumpuk${k ? '' : ' tumpuk-habis'}" viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="${g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="kilap1"/><stop offset="0.55" class="kilap1"/><stop offset="1" class="kilap2"/></linearGradient></defs>
    <path class="lantai" d="M2 ${LANTAI}h60"/><path class="bekas" transform="translate(${x0} ${n1(LANTAI - T)})" d="${badan}"/>${semua.join('')}${papanUkuran(berat)}</svg>`;
}
/** Ukuran kantong rebah menurut isinya: makin berat makin panjang & tebal. */
function ukuranKantong(u) {
  const n = Number(u) || 0;
  if (n >= 40) return { L: 41, T: 9 };
  if (n >= 20) return { L: 39, T: 8.6 };
  if (n >= 10) return { L: 35, T: 8.2 };
  if (n >= 5) return { L: 31, T: 7.6 };
  return { L: 26, T: 7 };
}
/**
 * Kantong plastik rebah selebar L, setebal T, seperti bantal: dua ujungnya dipres jadi sirip segel setinggi kantong (T×0,08–T×0,92),
 * di antaranya badan menggembung — sudut membulat, sisi atas & bawah cembung sampai ±1,2 di luar sirip. Badan dari x 3 sampai L − 3.
 */
function kantong(L, T) {
  const a = 3; const b = n1(L - 3); const r = 1.4; const atas = n1(T * 0.08); const bawah = n1(T * 0.92); const tengah = n1(L / 2);
  return `M${a} ${n1(atas + r)} Q${a} ${atas} ${n1(a + r)} ${atas} Q${tengah} ${n1(atas - 2.4)} ${n1(b - r)} ${atas} Q${b} ${atas} ${b} ${n1(atas + r)}`
    + ` Q${n1(b + 0.5)} ${n1(T / 2)} ${b} ${n1(bawah - r)} Q${b} ${bawah} ${n1(b - r)} ${bawah} Q${tengah} ${n1(bawah + 2.4)} ${n1(a + r)} ${bawah}`
    + ` Q${a} ${bawah} ${a} ${n1(bawah - r)} Q${n1(a - 0.5)} ${n1(T / 2)} ${a} ${n1(atas + r)} Z`;
}
/**
 * Sirip segel penuh setinggi kantong di kedua ujung (M0,4 T×0,08 h3 v T×0,84 h−3 + cerminannya), tepi luarnya bergerigi seperti
 * potongan pisau segel. Plastik yang dipres panas: pipih & lebih bening dari badannya.
 */
function siripKantong(L, T) {
  const atas = T * 0.08; const bawah = T * 0.92; const gigi = Math.max(3, Math.round((bawah - atas) / 1.6)); const langkah = (bawah - atas) / gigi;
  let kiri = `M3.4 ${n1(atas)}H0.4`; let kanan = `M${n1(L - 3.4)} ${n1(atas)}H${n1(L - 0.4)}`;
  for (let i = 0; i < gigi; i++) {
    const yt = atas + (i + 0.5) * langkah; const yb = atas + (i + 1) * langkah;
    kiri += `L1.2 ${n1(yt)}L0.4 ${n1(yb)}`; kanan += `L${n1(L - 1.2)} ${n1(yt)}L${n1(L - 0.4)} ${n1(yb)}`;
  }
  return `${kiri}H3.4Z${kanan}H${n1(L - 3.4)}Z`;
}
/** Gurat pres di sirip: garis mendatar rapat — tekstur segel panas, beda dari tutup koin/kutub baterai. */
function guratSegel(L, T) {
  let d = ''; for (let y = T * 0.08 + 1; y < T * 0.92 - 0.5; y += 1.25) d += `M1.5 ${n1(y)}H3M${n1(L - 1.5)} ${n1(y)}H${n1(L - 3)}`;
  return d;
}
/**
 * Geser & miring tiap lapis kemasan (0 = paling bawah): kantong plastik lembek tidak bertumpuk rapi seperti koin — maju-mundur
 * dan miring tak beraturan. Tetap per lapis (bukan acak) supaya rangka SVG sama di semua tingkat sisa.
 */
const GESER_KANTONG = [0, -1.6, 1, -0.6, 1.4, -1.1];
const MIRING_KANTONG = [0, -2.2, 1.4, -0.8, 2.4, -1.6];
/**
 * Tumpukan kemasan rebah (kantong plastik bersegel kedua ujungnya, label cetak lebar di muka); isi & jumlah seperti karung.
 * Plastiknya platina (bukan emas karung): kantong 5/10 kg di toko bening/putih, yang mencolok labelnya. Alas berwarna latar di bawah
 * badan yang bening, supaya tepi kantong di bawahnya tidak tembus.
 */
export function gambarKemasan(id, isi, ukuran, jumlah) {
  const g = 'gm_' + idAman(id);
  const U = ukuranKantong(ukuran); const L = U.L; const T = U.T; const P = T - 0.2; const x0 = n1(62.4 - L);
  // perut kantong (cembung 1,2 di bawah sirip) yang menyentuh lantai, bukan siripnya — sirip terangkat sedikit seperti bantal rebah
  const y0 = n1(LANTAI - T * 0.92 - 0.9);
  const k = lapisTampak(isi, jumlah); const lw = n1(L * 0.56); const lx = n1((L - lw) / 2); const badan = kantong(L, T); const sirip = siripKantong(L, T);
  // kilap plastik: separuh kiri lengkung yang sejajar sisi atas badan (0,7 di bawahnya), berhenti di tengah kantong
  const kilap = `M4.8 ${n1(T * 0.08 + 0.7)} Q${n1((4.8 + L / 2) / 2)} ${n1(T * 0.08 - 0.5)} ${n1(L / 2)} ${n1(T * 0.08 - 0.5)}`;
  const cetak = `M${n1(lx + 1.8)} ${n1(T * 0.5)}h${n1(lw - 3.6)}`;
  const isiLapis = `<path class="sirip" d="${sirip}"/><path class="segel" d="${guratSegel(L, T)}"/><path class="alas" d="${badan}"/><path class="badan" d="${badan}" fill="url(#${g})"/>`
    + `<path class="kilap-plastik" d="${kilap}"/><rect class="label-kantong" x="${lx}" y="${n1(T * 0.2)}" width="${lw}" height="${n1(T * 0.6)}" rx="1.2"/><path class="cetak" d="${cetak}"/>`;
  const semua = []; for (let i = 0; i < TUMPUK_N; i++) semua.push(lapis(i, k, x0 + GESER_KANTONG[i], y0 - i * P, isiLapis, MIRING_KANTONG[i], L, T));
  return `<svg class="gb kemasan tumpuk${k ? '' : ' tumpuk-habis'}" viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="${g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="plastik1"/><stop offset="0.5" class="plastik1"/><stop offset="1" class="plastik2"/></linearGradient></defs>
    <path class="lantai" d="M2 ${LANTAI}h60"/><path class="bekas" transform="translate(${x0} ${y0})" d="${sirip}${badan}"/>${semua.join('')}${papanUkuran(String(ukuran == null ? '' : ukuran).replace('.', ','))}</svg>`;
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
/** Wadah KOSONG yang dijual sebagai barang (putaran 15): kantong terlipat tanpa isi (garis putus di dalam), berlabel muatannya; karung bekas = karung kempis. */
export function gambarWadahKosong(id, isi, ukuran, karung) {
  const c = 'cw_' + idAman(id);
  if (karung) return `<svg class="gb karung kosong" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><path d="M14 30 Q32 34 50 30 L52 58 Q32 62 12 58 Z"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="8" y="30" width="48" height="32" style="transform: scaleY(${bulat2(isi)});"/></g>
    <path class="kotak" d="M14 30 Q32 34 50 30 L52 58 Q32 62 12 58 Z"/><path class="ikat" d="M18 30 Q32 24 46 30M20 40h24M20 48h24"/><text x="32" y="55" text-anchor="middle" class="ukuran" style="font-size: 9px;">bekas</text></svg>`;
  return `<svg class="gb kemasan kosong" viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="${c}"><rect x="15" y="14" width="34" height="44" rx="5"/></clipPath></defs>
    <g clip-path="url(#${c})"><rect class="isi-dalam" x="15" y="14" width="34" height="44" style="transform: scaleY(${bulat2(isi)});"/></g>
    <rect class="kotak" x="15" y="14" width="34" height="44" rx="5" style="stroke-dasharray: 3 2;"/><path class="bilah" d="M15 20h34M22 30l20 18M42 30 22 48"/><rect class="label-kantong" x="20" y="27" width="24" height="17" rx="3"/>
    <text x="32" y="40" text-anchor="middle" class="ukuran">${String(ukuran || '').replace('.', ',')}</text></svg>`;
}
export function gambarChipBarang(c, penuh) {
  const isi = (c.sisa || 0) / penuh; const id = c.jalur + '-' + c.kunci + '-' + (c.berat || '');
  if (c.jalur === 'wadah') return gambarWadahKosong(id, isi, c.ukuranKg, c.hasilSamping);
  if (c.jalur === 'literan') return c.wadah ? gambarWadah(c.wadah) : gambarKarungBuka(id, isi);
  if (c.jalur === 'karung') return gambarKarung(id, isi, c.berat, c.sisa);
  if (c.jalur === 'kemasan') return gambarKemasan(id, isi, c.ukuranKg, c.sisa);
  return gambarKarungBuka(id, isi);
}

