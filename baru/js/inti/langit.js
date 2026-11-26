// LANGIT GERBANG — penggambar (owner 26 Nov 2026: langit ikut jam & cuaca sungguhan, "mewah", "terbaik tapi optimal"). Angka & warna: langit-logika.js.
//
// Lapisan di BELAKANG pintu kaca (.gm-latar), bawah → atas: warna langit · bintang (dua kelompok berkelip) · bulan (sesuai fasenya hari itu) · matahari +
// berkas cahaya fajar/senja · [bola cahaya & cahaya cakrawala lama] · awan jauh & dekat · kabut · hujan jauh & dekat · cahaya kilat. Di kaca pintu: titik
// embun hujan + tetes yang meluncur. Di atas pintu: kilasan kilat tipis.
// OPTIMAL: semua gerak yang berjalan terus hanya transform / opacity (dikomposit kartu grafis, utas utama tidak menggambar ulang tiap bingkai); bintang, awan,
// embun & garis hujan digambar SEKALI saat gerbang dipasang. Warna & letak matahari/bulan dihitung sekali per MENIT (bukan per bingkai) dan hanya ditulis
// bila berubah. Lapisan yang tidak dipakai cuaca saat ini display: none. Gerbang tersembunyi = tidak ada yang berjalan (jam & ambil cuaca berhenti).
// prefers-reduced-motion: langit & cuaca tetap tampil, tanpa gerak. Tidak ada data toko yang dikirim ke mana pun — hanya koordinat lokasi ke Open-Meteo.
import * as L from './langit-logika.js';

const NS = 'http://www.w3.org/2000/svg';
const benih = (n) => { let s = n >>> 0; return () => { s = (Math.imul(s ^ (s >>> 15), 2246822507) + 0x9e3779b9) >>> 0; s ^= s >>> 13; return (s >>> 0) / 4294967296; }; };
const baca = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const tulis = (k, v) => { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { /* simpanan perangkat penuh / dilarang: langit tetap ikut jam */ } };
const diam = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Lokasi toko dari setelan (Menu › Sistem › Perangkat › Atur) → simpanan perangkat, supaya gerbang SEBELUM masuk akun tahu cuaca di mana. Dipanggil app.js
 *  tiap data berubah; menulis hanya bila berbeda. null = owner mencabut lokasi → cuaca berhenti diambil. */
export function langitSimpanLokasi(lok) {
  const l = L.lgLokasiSah(lok); const baru = l ? JSON.stringify(l) : null;
  if (baca(L.LG_KUNCI_LOKASI) !== baru) { tulis(L.LG_KUNCI_LOKASI, baru); if (!l) tulis(L.LG_KUNCI_CUACA, null); }
}

// ---------- gambar sekali ----------
function svg(viewBox, kelas, aspek) { const s = document.createElementNS(NS, 'svg'); s.setAttribute('viewBox', viewBox); s.setAttribute('preserveAspectRatio', aspek || 'xMidYMid slice'); if (kelas) s.setAttribute('class', kelas); s.setAttribute('aria-hidden', 'true'); return s; }
function bintang() {
  const w = document.createElement('div'); w.className = 'lg-bintang';
  [['a', 11], ['b', 29], ['c', 47]].forEach(([k, n]) => {
    const r = benih(n * 7919); const s = svg('0 0 1000 620', 'lg-bintang-' + k); let isi = '';
    for (let i = 0; i < (k === 'c' ? 24 : 70); i++) { const x = r() * 1000, y = Math.pow(r(), 1.5) * 560, ukur = k === 'c' ? 1.5 + r() * 1.3 : 0.55 + r() * 1.05;
      isi += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + ukur.toFixed(2) + '" opacity="' + (0.45 + r() * 0.55).toFixed(2) + '"/>'; }
    s.innerHTML = isi; w.appendChild(s);
  });
  return w;
}
function bulan() {
  const w = document.createElement('div'); w.className = 'lg-bulan';
  w.innerHTML = '<div class="lg-bulan-pendar"></div><svg viewBox="-50 -50 100 100" aria-hidden="true"><defs><radialGradient id="lgBulanIsi" cx="0.42" cy="0.38" r="0.7">'
    + '<stop offset="0" stop-color="#fffbea"/><stop offset="0.7" stop-color="#efe6c8"/><stop offset="1" stop-color="#d8cca6"/></radialGradient>'
    + '<mask id="lgBulanTopeng"><rect x="-50" y="-50" width="100" height="100" fill="#000"/><circle r="18" fill="#fff"/><circle class="lg-bayang" r="18.6" fill="#000"/></mask></defs>'
    + '<circle r="18" fill="rgba(255,250,230,0.08)"/><g mask="url(#lgBulanTopeng)"><circle r="18" fill="url(#lgBulanIsi)"/>'
    + '<circle cx="-5" cy="-4" r="3.2" fill="rgba(150,140,110,0.22)"/><circle cx="6" cy="5" r="4.4" fill="rgba(150,140,110,0.18)"/><circle cx="2" cy="-9" r="2" fill="rgba(150,140,110,0.2)"/></g></svg>';
  return w;
}
// matahari DI BELAKANG kaca: berkas fajar/senja (lg-sinar), silau terik siang, pendar, inti — di Mac/iPhone kaca pintu buram 26 px jadi semua ini melebur
function surya() { const w = document.createElement('div'); w.className = 'lg-surya';
  w.innerHTML = '<div class="lg-sinar"></div><div class="lg-terik"><div class="lg-silau"></div></div><div class="lg-pendar"></div><div class="lg-inti"></div>'; return w; }
// matahari DI DEPAN kaca (owner 26 Nov 2026: "matahari sama sekali gak muncul beserta pancarannya" — di balik kaca buram cakram & pancaran hilang): cakram tajam
// + TERIK siang tropis (pancaran berputar, kilau). Di lapis makhluk hidup (.gm-hidup): di bawah burung, ikut pudar saat pintu bergerak.
function suryaDepan() { const w = document.createElement('div'); w.className = 'lg-surya-depan';
  w.innerHTML = '<div class="lg-terik-depan"><div class="lg-pancar"></div><div class="lg-kilau"></div></div><div class="lg-inti"></div>'; return w; }
/** Suar lensa saat terik: empat lingkaran samar di garis dari matahari menembus tengah layar (letak = CSS calc dari --lg-sx/--lg-sy, tanpa JS per bingkai). */
function suar() { const w = document.createElement('div'); w.className = 'lg-suar'; w.innerHTML = '<i></i><i></i><i></i><i></i>'; return w; }
function awan(kelas, n, besar, seed) {
  const w = document.createElement('div'); w.className = 'lg-awan ' + kelas; const r = benih(seed); const s = svg('0 0 2000 400', '', 'none');
  let defs = '<defs><radialGradient id="lgGumpal' + kelas + '" cx="0.5" cy="0.55" r="0.5"><stop offset="0" style="stop-color: var(--lg-awan-isi)"/><stop offset="0.62" style="stop-color: var(--lg-awan-isi); stop-opacity: 0.55"/>'
    + '<stop offset="1" style="stop-color: var(--lg-awan-isi); stop-opacity: 0"/></radialGradient></defs>'; let isi = '';
  const gumpal = []; for (let i = 0; i < n; i++) { const cx = (i + 0.2 + r() * 0.6) * (1000 / n), cy = 70 + r() * 220, lebar = besar * (0.7 + r() * 0.6);
    for (let j = 0; j < 6; j++) gumpal.push([cx + (j - 2.5) * lebar * 0.22 + (r() - 0.5) * lebar * 0.15, cy + (r() - 0.5) * lebar * 0.16 - Math.sin(j / 5 * Math.PI) * lebar * 0.12, lebar * (0.2 + r() * 0.16)]); }
  [0, 1000].forEach((geser) => gumpal.forEach(([x, y, rr]) => { isi += '<ellipse cx="' + (x + geser).toFixed(1) + '" cy="' + y.toFixed(1) + '" rx="' + (rr * 1.5).toFixed(1) + '" ry="' + rr.toFixed(1) + '" fill="url(#lgGumpal' + kelas + ')"/>'; }));
  s.innerHTML = defs + isi; w.appendChild(s); return w;
}
function kabut() { const w = document.createElement('div'); w.className = 'lg-kabut'; w.innerHTML = '<i class="a"></i><i class="b"></i>'; return w; }
/** Garis hujan satu ubin (digambar sekali per mode warna) → data URI untuk latar yang digeser. */
function ubinHujan(seed, n, panjang, tebal, warna) {
  const r = benih(seed); let isi = '';
  for (let i = 0; i < n; i++) { const x = r() * 240, y = r() * 360, p = panjang * (0.6 + r() * 0.8); isi += '<line x1="' + x.toFixed(1) + '" y1="' + y.toFixed(1) + '" x2="' + x.toFixed(1) + '" y2="' + (y + p).toFixed(1) + '" stroke-opacity="' + (0.35 + r() * 0.65).toFixed(2) + '"/>';
    if (y + p > 360) isi += '<line x1="' + x.toFixed(1) + '" y1="' + (y - 360).toFixed(1) + '" x2="' + x.toFixed(1) + '" y2="' + (y + p - 360).toFixed(1) + '" stroke-opacity="0.6"/>'; }
  return 'url("data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="360"><g stroke="' + warna + '" stroke-width="' + tebal + '" stroke-linecap="round">' + isi + '</g></svg>') + '")';
}
function embun(sisi) {
  const w = document.createElement('div'); w.className = 'lg-embun'; const r = benih(sisi === 'kiri' ? 4242 : 8484); const s = svg('0 0 500 1000', 'lg-titik', 'none');
  let isi = '<defs><radialGradient id="lgTetes' + sisi + '" cx="0.38" cy="0.32" r="0.7"><stop offset="0" stop-color="rgba(255,255,255,0.95)"/><stop offset="0.35" stop-color="rgba(255,255,255,0.28)"/>'
    + '<stop offset="0.8" stop-color="rgba(120,140,160,0.18)"/><stop offset="1" stop-color="rgba(60,70,80,0.35)"/></radialGradient></defs>';
  for (let i = 0; i < 46; i++) { const rr = 1.6 + Math.pow(r(), 2.2) * 6.5; isi += '<ellipse cx="' + (r() * 500).toFixed(1) + '" cy="' + (r() * 1000).toFixed(1) + '" rx="' + rr.toFixed(1) + '" ry="' + (rr * (1.05 + r() * 0.3)).toFixed(1) + '" fill="url(#lgTetes' + sisi + ')"/>'; }
  s.innerHTML = isi; w.appendChild(s);
  for (let i = 0; i < 4; i++) { const t = document.createElement('i'); t.className = 'lg-luncur'; t.style.left = (8 + r() * 84).toFixed(1) + '%'; t.style.top = (r() * 40).toFixed(1) + '%';
    t.style.animationDelay = (-r() * 12).toFixed(2) + 's'; t.style.animationDuration = (9 + r() * 7).toFixed(2) + 's'; w.appendChild(t); }
  return w;
}
// ---------- SUASANA (owner 26 Nov 2026): satwa menurut jam & cuaca (langit-logika lgSatwa). Tiap satwa = kotak HTML yang TERBANG (translate) berisi SVG
// yang MENGEPAK (scale) — dua-duanya transform, dikomposit kartu grafis. Burung, capung & kunang-kunang G4 tetap; ini tambahannya. ----------
const SATWA = {
  // kelelawar: sayap bergerigi, telinga runcing
  kelelawar: ['-16 -9 32 15', '<path d="M0 -3.4 L-1.3 -6.2 L-2.2 -3.6 C-4 -4.6 -6.2 -5.8 -9.4 -5.2 C-11.6 -4.8 -13.8 -3.4 -15.6 -1.6 C-13.4 -1.8 -12.2 -0.6 -11.6 1.2 C-10.2 -0.2 -8.6 -0.2 -7.6 1.4 C-6.4 0 -4.6 0 -3.4 1.6 C-2.4 0.6 -1.2 0.6 0 2.4 C1.2 0.6 2.4 0.6 3.4 1.6 C4.6 0 6.4 0 7.6 1.4 C8.6 -0.2 10.2 -0.2 11.6 1.2 C12.2 -0.6 13.4 -1.8 15.6 -1.6 C13.8 -3.4 11.6 -4.8 9.4 -5.2 C6.2 -5.8 4 -4.6 2.2 -3.6 L1.3 -6.2 Z"/>'],
  // kupu-kupu: dua pasang sayap bercorak + badan
  kupu: ['-11 -10 22 20', '<g class="lg-sayap-kupu"><path d="M0 -1 C-3 -9 -10 -10 -10 -4 C-10 0 -5 1 0 0 Z"/><path d="M0 0 C-4 1 -8 4 -7 7 C-6 9.5 -2 8 0 1 Z"/><path d="M0 -1 C3 -9 10 -10 10 -4 C10 0 5 1 0 0 Z"/><path d="M0 0 C4 1 8 4 7 7 C6 9.5 2 8 0 1 Z"/></g><circle class="lg-corak" cx="-6" cy="-4.4" r="1.4"/><circle class="lg-corak" cx="6" cy="-4.4" r="1.4"/><path class="lg-badan-kupu" d="M0 -3 L0 5"/>'],
  // elang: sayap lebar terbentang, ujung berjari, melayang
  elang: ['-22 -7 44 14', '<path d="M-21 -1.4 L-18.5 -2.6 L-17.6 -1.4 L-16 -3 L-14.6 -1.6 C-10 -3.6 -5.6 -3.2 -2.2 -0.8 L0 -2.4 L2.2 -0.8 C5.6 -3.2 10 -3.6 14.6 -1.6 L16 -3 L17.6 -1.4 L18.5 -2.6 L21 -1.4 C15 0.6 8 0.8 3 1.6 L1.6 5.4 L0 4 L-1.6 5.4 L-3 1.6 C-8 0.8 -15 0.6 -21 -1.4 Z"/>'],
  // bangau / kuntul putih: leher melipat, kaki menjulur ke belakang
  bangau: ['-26 -11 52 20', '<path class="lg-sayap-bangau" d="M-3 -1 C-8 -9 -16 -10 -22 -6 C-15 -5 -9 -3 -4 1 Z M3 -1 C6 -8 12 -9 17 -7 C12 -5 8 -3 4 1 Z"/><path d="M-6 0.6 C-1 -1.6 6 -1.6 10 0 C12 1 13.6 0.6 15 -0.4 L19.6 -1.2 L15.4 0.8 C13 2.6 9 3 5 2.6 C1 2.4 -3 2.2 -6 0.6 Z"/><path class="lg-kaki" d="M-5 1.4 L-17 3.4 M-5 1.8 L-16.6 4.4"/>'],
};
function satwa(jenis, n, seed) {
  const r = benih(seed); const [vb, isi] = SATWA[jenis]; const out = [];
  for (let i = 0; i < n; i++) {
    const w = document.createElement('div'); w.className = 'lg-' + jenis + ' lg-satwa';
    w.style.animationDelay = (-r() * 30).toFixed(2) + 's'; w.style.animationDuration = (jenis === 'kelelawar' ? 11 + r() * 7 : jenis === 'kupu' ? 22 + r() * 12 : jenis === 'bangau' ? 38 + r() * 16 : 52).toFixed(2) + 's';
    w.style.setProperty('--lg-tinggi', (jenis === 'kelelawar' ? 8 + r() * 30 : jenis === 'kupu' ? 0 + r() * 16 : jenis === 'bangau' ? 6 + r() * 14 : 0).toFixed(1));
    w.style.setProperty('--lg-ukur', (0.75 + r() * 0.5).toFixed(2));
    const s = svg(vb, 'lg-kepak', 'xMidYMid meet'); s.innerHTML = isi; s.style.animationDelay = (-r()).toFixed(2) + 's';
    if (jenis === 'elang') { const putar = document.createElement('div'); putar.className = 'lg-elang-putar'; putar.appendChild(s); w.appendChild(putar); } else w.appendChild(s);
    out.push(w);
  }
  return out;
}
function meteor() { const w = document.createElement('div'); w.className = 'lg-meteor'; return w; }
function kilat() { const w = document.createElement('div'); w.className = 'lg-kilat'; return w; }
/** Lapis sambaran: dua SVG (sambaran ganda) yang bentuknya diisi ulang tiap sambaran (lgPetirAcak) — inti putih + cahaya biru-ungu. */
function sambaran() {
  const w = document.createElement('div'); w.className = 'lg-sambar';
  for (let i = 0; i < 2; i++) { const s = svg('0 0 100 400', 'lg-petir', 'none'); s.innerHTML = '<g class="lg-petir-cahaya"></g><g class="lg-petir-inti"></g>'; w.appendChild(s); }
  return w;
}

/**
 * Pasang langit di gerbang g (#modalMasuk). Kembali: { nyala(ya), detik(), perbarui() } — gerbang.js menyalakannya bersama jam gerbang.
 * opsi.mode() = 'terang' | 'gelap'; opsi.cari = location.search (pratinjau ?langitJam=…&langitCuaca=…).
 */
export function pasangLangit(g, opsi) {
  const latar = g.querySelector('.gm-latar'); if (!latar) return { nyala() {}, detik() {}, perbarui() {} };
  const paksa = L.lgPaksa(opsi && opsi.cari);
  const awal = latar.firstChild;
  const langit = document.createElement('div'); langit.className = 'lg-langit';
  [langit, bintang(), bulan(), surya()].forEach((el) => latar.insertBefore(el, awal));
  const hujanJauh = document.createElement('div'); hujanJauh.className = 'lg-hujan jauh';
  const hujanDekat = document.createElement('div'); hujanDekat.className = 'lg-hujan dekat';
  const bintangJatuh = meteor();
  [bintangJatuh, kilat(), awan('jauh', 5, 170, 101), awan('dekat', 3, 300, 202), kabut(), hujanJauh, hujanDekat].forEach((el) => latar.appendChild(el));
  // sambaran di DEPAN kaca (seperti burung & kunang): di belakang kaca buram (Mac/iPhone) garis 2 px ikut terburamkan sampai hilang; kilasan tetap di belakang
  const sambar = sambaran(); const hidupAda = g.querySelector('.gm-hidup'); if (hidupAda) g.insertBefore(sambar, hidupAda); else g.appendChild(sambar);
  const hidup = g.querySelector('.gm-hidup');
  if (hidup) { hidup.insertBefore(suar(), hidup.firstChild); hidup.insertBefore(suryaDepan(), hidup.firstChild); }   // di bawah semua makhluk
  if (hidup) satwa('bangau', 3, 31).concat(satwa('kupu', 3, 57), satwa('elang', 1, 83), satwa('kelelawar', 4, 97)).forEach((el) => hidup.appendChild(el));
  g.querySelectorAll('.gm-pintu').forEach((p) => { const h = p.querySelector('.gm-hiasan'); const e = embun(p.classList.contains('kiri') ? 'kiri' : 'kanan'); if (h && h.nextSibling) p.insertBefore(e, h.nextSibling); else p.appendChild(e); });
  const kilas = document.createElement('div'); kilas.className = 'lg-kilas'; g.appendChild(kilas);
  const cuacaTeks = document.getElementById('gmCuaca');
  const bayang = latar.querySelector('.lg-bayang');

  let nyalaKini = false, menitAkhir = -1, modeAkhir = '', jamKilat = 0, jamMeteor = 0, mengambil = false, gayaAkhir = {}, kelasAkhir = '';
  const lokasi = () => { let o = null; try { o = JSON.parse(baca(L.LG_KUNCI_LOKASI) || 'null'); } catch (e) { o = null; } return L.lgLokasiSah(o); };
  const cuaca = () => {
    if (paksa && paksa.kode !== null) return { lat: 0, lon: 0, pada: kini().getTime(), kode: paksa.kode, awan: null, hujanMm: 0, suhu: 29, terbit: null, terbenam: null, tanggal: '' };
    return L.lgCuacaTersimpan(baca(L.LG_KUNCI_CUACA));
  };
  const kini = () => { const d = new Date(); if (paksa && paksa.menit !== null) d.setHours(Math.floor(paksa.menit / 60), paksa.menit % 60, 0, 0); return d; };
  const setel = (k, v) => { if (gayaAkhir[k] !== v) { g.style.setProperty(k, v); gayaAkhir[k] = v; } };

  function perbarui() {
    const mode = opsi && opsi.mode ? opsi.mode() : 'terang'; const K = L.lgKeadaan(kini(), cuaca(), mode);
    setel('--lg-l1', K.warna.l1); setel('--lg-l2', K.warna.l2); setel('--lg-l3', K.warna.l3); setel('--gm-senja1', K.warna.cahaya);
    // letak dua versi: layar datar (x, y) & layar tegak (tx, ty) — langit.css memilih menurut tata letak gerbang (dua kolom atau bertumpuk)
    setel('--lg-surya-x', K.surya.x + '%'); setel('--lg-surya-y', K.surya.y + '%'); setel('--lg-surya-tx', K.surya.tx + '%'); setel('--lg-surya-ty', K.surya.ty + '%');
    setel('--lg-surya-op', String(K.surya.op)); setel('--lg-sinar-op', String(K.surya.sinar)); setel('--lg-surya-hangat', String(K.surya.hangat)); setel('--lg-terik', String(K.surya.terik));
    setel('--lg-bulan-x', K.bulan.x + '%'); setel('--lg-bulan-y', K.bulan.y + '%'); setel('--lg-bulan-tx', K.bulan.tx + '%'); setel('--lg-bulan-ty', K.bulan.ty + '%'); setel('--lg-bulan-op', String(K.bulan.op));
    setel('--lg-bintang', String(K.bintang)); setel('--lg-awan-op', String(Math.round(Math.max(0, K.awan - 0.08) * 1000) / 1000));
    // warna awan: putih cerah → kelabu saat mendung → abu gelap saat hujan; malam kebiruan
    const kelabu = K.hujan || K.mendung > 0.55;
    setel('--lg-awan-isi', mode === 'gelap' ? (K.hujan ? 'rgba(96,106,122,0.9)' : K.malam > 0.5 ? 'rgba(70,82,110,0.85)' : kelabu ? 'rgba(170,176,188,0.92)' : 'rgba(236,232,226,0.9)') : (K.hujan ? 'rgba(168,176,188,0.95)' : kelabu ? 'rgba(212,216,224,0.96)' : 'rgba(255,255,255,0.96)'));
    setel('--lg-kabut-op', String(K.kabut));
    // bulan: bayangan digeser menurut fase (purnama = bayangan habis keluar, bulan baru = menutup) — sabit muda terang di kanan, sabit tua di kiri
    const f = K.bulan.fase; const geser = (1 - Math.abs(f - 0.5) * 2) * 37 * (f < 0.5 ? -1 : 1);
    if (bayang && bayang.getAttribute('cx') !== geser.toFixed(1)) bayang.setAttribute('cx', geser.toFixed(1));
    const kelas = ['lg-hujan-' + K.hujan, K.petir ? 'lg-ada-petir' : '', K.kabut ? 'lg-berkabut' : '', K.awan > 0.12 ? 'lg-berawan' : '', K.burung ? '' : 'lg-tanpa-burung',
      K.capung ? '' : 'lg-tanpa-capung', K.kunang ? 'lg-kunang' : '', K.malam > 0.5 ? 'lg-malam' : '',
      K.bintang > 0.02 ? 'lg-ada-bintang' : '', K.bulan.op > 0.01 ? 'lg-ada-bulan' : '', K.surya.op > 0.01 ? 'lg-ada-surya' : '', K.surya.sinar > 0.02 ? 'lg-ada-sinar' : '', K.surya.terik > 0.02 ? 'lg-ada-terik' : '',
      K.satwa.kelelawar ? 'lg-ada-kelelawar' : '', K.satwa.kupu ? 'lg-ada-kupu' : '', K.satwa.elang ? 'lg-ada-elang' : '', K.satwa.bangau ? 'lg-ada-bangau' : ''].filter(Boolean).join(' ');
    if (kelas !== kelasAkhir) { (kelasAkhir ? kelasAkhir.split(' ') : []).forEach((c) => g.classList.remove(c)); kelas.split(' ').forEach((c) => g.classList.add(c)); kelasAkhir = kelas; }
    if (mode !== modeAkhir) {   // garis hujan: putih di langit gelap, biru keabuan di langit terang (warna lain tidak terlihat)
      const w = mode === 'gelap' ? 'rgb(214,226,244)' : 'rgb(96,116,148)';
      hujanJauh.style.backgroundImage = ubinHujan(77, 46, 26, 1, w); hujanDekat.style.backgroundImage = ubinHujan(991, 22, 46, 1.6, w); modeAkhir = mode;
    }
    if (cuacaTeks && cuacaTeks.textContent !== K.teks) { cuacaTeks.textContent = K.teks; cuacaTeks.hidden = !K.teks; }
    if (nyalaKini && K.petir && !jamKilat) aturKilat(); if (!K.petir && jamKilat) { clearTimeout(jamKilat); jamKilat = 0; }
    meteorBoleh = K.satwa.meteor; if (nyalaKini && meteorBoleh && !jamMeteor) aturMeteor(); if (!meteorBoleh && jamMeteor) { clearTimeout(jamMeteor); jamMeteor = 0; }
  }
  // PETIR (owner 26 Nov 2026: "coba garap" — dulu satu bentuk tetap yang putih di atas kilasan putih, nyaris tak terlihat). Tiap 4,5–13,5 dtk salah satu dari:
  //   · sambaran (±55%): jalur bercabang BARU (lgPetirAcak), inti putih + cahaya biru-ungu, menyala-padam-menyala; kilasan langit berpusat di titik sambaran
  //   · sambaran ganda (±20%): sambaran kedua 160–260 ms kemudian di dekatnya
  //   · kilat di balik awan (±25%): hanya langit & awan yang menyala, tanpa jalur
  // Semua Web Animations opacity (dikomposit); bentuk sambaran diisi sekali per sambaran — tanpa ganti kelas gerbang, tanpa memaksa tata letak.
  const KF_KILAT = [{ opacity: 0 }, { opacity: 0.9, offset: 0.05 }, { opacity: 0.12, offset: 0.12 }, { opacity: 0.75, offset: 0.2 }, { opacity: 0.06, offset: 0.55 }, { opacity: 0 }];
  const KF_KILAS = [{ opacity: 0 }, { opacity: 1, offset: 0.05 }, { opacity: 0, offset: 0.12 }, { opacity: 0.7, offset: 0.2 }, { opacity: 0, offset: 0.4 }, { opacity: 0 }];
  const KF_SAMBAR = [{ opacity: 0 }, { opacity: 1, offset: 0.03 }, { opacity: 0.15, offset: 0.1 }, { opacity: 1, offset: 0.16 }, { opacity: 0.85, offset: 0.32 }, { opacity: 0, offset: 0.62 }, { opacity: 0 }];
  function sambarSatu(petir, x, lebar) {
    const b = L.lgPetirAcak(); const isi = '<path d="' + b.utama + '"/>' + b.cabang.map((c) => '<path class="lg-cabang" d="' + c + '"/>').join('');
    petir.querySelector('.lg-petir-cahaya').innerHTML = isi; petir.querySelector('.lg-petir-inti').innerHTML = isi;
    petir.style.left = x.toFixed(1) + '%'; petir.style.width = lebar + 'px';
    if (typeof petir.animate === 'function') petir.animate(KF_SAMBAR, { duration: 760, easing: 'ease-out' });
  }
  function aturKilat() {
    if (diam()) return;
    jamKilat = setTimeout(() => {
      jamKilat = 0; if (!nyalaKini || !g.classList.contains('lg-ada-petir')) return;
      const jenis = Math.random(); const x = 10 + Math.random() * 74; const lebar = 90 + Math.round(Math.random() * 70);
      const lapis = latar.querySelector('.lg-kilat'); const petir = sambar.querySelectorAll('.lg-petir');
      if (lapis) lapis.style.setProperty('--lg-kilat-x', (x + 3).toFixed(1) + '%');
      if (lapis && typeof lapis.animate === 'function') lapis.animate(KF_KILAT, { duration: 1050, easing: 'ease-out' });
      if (kilas && typeof kilas.animate === 'function') kilas.animate(KF_KILAS, { duration: 1050, easing: 'ease-out' });
      if (jenis < 0.75 && petir[0]) sambarSatu(petir[0], x, lebar);
      if (jenis < 0.2 && petir[1]) setTimeout(() => { if (nyalaKini) sambarSatu(petir[1], jepitP(x + (Math.random() - 0.5) * 22), Math.round(lebar * 0.8)); }, 160 + Math.random() * 100);
      aturKilat();
    }, 4500 + Math.random() * 9000);
  }
  const jepitP = (x) => Math.max(4, Math.min(88, x));
  // bintang jatuh: sesekali (14–40 dtk) di langit malam cerah — satu garis cahaya, Web Animations (transform + opacity), letak & sudut acak
  let meteorBoleh = false;
  function aturMeteor() {
    if (diam()) return;
    jamMeteor = setTimeout(() => {
      jamMeteor = 0; if (!nyalaKini || !meteorBoleh) return;
      const x = 18 + Math.random() * 60, y = 4 + Math.random() * 26, sudut = 20 + Math.random() * 18, jauh = 160 + Math.random() * 180;
      bintangJatuh.style.left = x.toFixed(1) + '%'; bintangJatuh.style.top = y.toFixed(1) + '%';
      const rad = sudut * Math.PI / 180; const dx = -Math.cos(rad) * jauh, dy = Math.sin(rad) * jauh;
      if (typeof bintangJatuh.animate === 'function') bintangJatuh.animate([{ opacity: 0, transform: 'translate3d(0,0,0) rotate(' + (-sudut) + 'deg) scaleX(0.3)' },
        { opacity: 1, offset: 0.2, transform: 'translate3d(' + (dx * 0.2).toFixed(1) + 'px,' + (dy * 0.2).toFixed(1) + 'px,0) rotate(' + (-sudut) + 'deg) scaleX(1)' },
        { opacity: 0, transform: 'translate3d(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px,0) rotate(' + (-sudut) + 'deg) scaleX(0.6)' }], { duration: 950, easing: 'cubic-bezier(.2,.6,.4,1)' });
      aturMeteor();
    }, 14000 + Math.random() * 26000);
  }
  async function ambil() {
    const l = lokasi(); if (paksa || mengambil || !l || !L.lgPerluAmbil(L.lgCuacaTersimpan(baca(L.LG_KUNCI_CUACA)), l, Date.now())) return;
    if (typeof fetch !== 'function') return;
    mengambil = true; const henti = typeof AbortController === 'function' ? new AbortController() : null; const jam = setTimeout(() => henti && henti.abort(), 8000);
    try {
      const r = await fetch(L.lgUrlCuaca(l), { cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer', signal: henti ? henti.signal : undefined });
      if (r.ok) { const c = L.lgBacaCuaca(await r.json(), l, Date.now()); if (c) { tulis(L.LG_KUNCI_CUACA, JSON.stringify(c)); if (nyalaKini) perbarui(); } }
    } catch (e) { /* tanpa internet / ditolak: langit tetap ikut jam, dicoba lagi saat gerbang tampil berikutnya */ }
    finally { clearTimeout(jam); mengambil = false; }
  }
  return {
    /** Gerbang tampil (true) / pergi (false). */
    nyala(ya) {
      nyalaKini = !!ya; if (!ya) { clearTimeout(jamKilat); jamKilat = 0; clearTimeout(jamMeteor); jamMeteor = 0; return; }
      menitAkhir = -1; perbarui(); ambil();
    },
    /** Dipanggil jam gerbang tiap detik: langit dihitung ulang sekali per menit (dan cuaca diambil bila sudah 30 menit). */
    detik() {
      if (!nyalaKini) return; const d = new Date(); const m = d.getHours() * 60 + d.getMinutes(); if (m === menitAkhir) return;
      menitAkhir = m; perbarui(); ambil();
    },
    perbarui() { if (nyalaKini) perbarui(); },
  };
}
