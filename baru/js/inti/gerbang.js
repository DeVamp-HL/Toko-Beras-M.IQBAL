// GERBANG MASUK G4 — dikunci owner 29 Sep 2026 (kanvas "Gerbang Masuk", artifact 7gGfZ2e4…): pintu kaca G3, kotak logo & kotak Masuk G1,
// cincin kunci G2, golden hour + siluet sawah + makhluk hidup. Berkas ini hanya GERAK & GAMBAR gerbang; siapa yang boleh masuk tetap
// diputuskan app.js (gambarAkun → bisaBekerja) dan tirai 23c (body.terkunci) — gerbang tidak pernah memuat angka toko.
//
// Keadaan (kelas t-… di #modalMasuk):
//   menunggu  Firebase belum menjawab siapa yang masuk → gerbang tertutup TANPA formulir (tidak ada layar kosong saat membuka aplikasi)
//   masuk / memeriksa / salah (+goyang) / belum / terkirim / nonaktif / kasir
//   membuka   sesudah masuk: cincin sejajar → lubang kunci berputar → cincin mekar → pintu bergeser (±2 dtk); 'cepat' = sesi yang dipulihkan (±0,9 dtk)
//   menutup   sesudah keluar: pintu merapat memantul, cincin kembali
// Kelas 'tampil' TETAP arti lamanya (gerbang menghalangi layar); animasi membuka memakai kelas 'membuka' tanpa menghalangi ketukan.
import { GM_SAWAH, GM_PADI } from './gerbang-hiasan.js';

const HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
const dua = (n) => (n < 10 ? '0' : '') + n;
const KEL = { detik: 2 * Math.PI * 138, email: 2 * Math.PI * 116, sandi: 2 * Math.PI * 94, kunci: 2 * Math.PI * 72 };
const LAMA = { buka: 2050, bukaCepat: 900, tutup: 1700, fase2: 850 };
const emailSah = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(e || '').trim());
const kelipatan = (x) => Math.ceil(x / 360) * 360;
const diam = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
const IKON_STATUS = {
  belum: '<circle cx="10" cy="8" r="3.5"/><path d="M3.5 19.5c.7-3.6 3.3-5.5 6.5-5.5 1.6 0 3 .4 4.1 1.2"/><path d="M18 14v6M15 17h6"/>',
  terkirim: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  nonaktif: '<rect x="5" y="10.5" width="14" height="9.5" rx="2"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/><path d="M4 4l16 16"/>',
  kasir: '<path d="M6.5 3.5h11v17l-2.2-1.4-2.2 1.4-2.1-1.4-2.2 1.4-2.3-1.4z"/><path d="M9.5 8h5M9.5 11.5h5M9.5 15h3"/>',
};

export function pasangGerbang(opsi) {
  const g = document.getElementById('modalMasuk');
  const $ = (id) => document.getElementById(id);
  const cincin = { e: g.querySelector('.gm-c-email'), s: g.querySelector('.gm-c-sandi'), k: g.querySelector('.gm-c-kunci'),
    isiE: g.querySelector('.gm-c-email .gm-isi-c'), isiS: g.querySelector('.gm-c-sandi .gm-isi-c'), detik: g.querySelector('.gm-detik'), kunci: g.querySelector('.gm-kunci') };
  // hiasan kaca (siluet sawah + padi merunduk) disalin ke KEDUA daun — satu pemandangan yang menyambung di sambungan & ikut terbelah
  g.querySelectorAll('.gm-hiasan').forEach((el) => { el.innerHTML = GM_SAWAH + '<div class="gm-bingkai"><span class="a"></span><span class="b"></span><span class="c"></span><span class="d"></span></div>' + GM_PADI; });

  let tahap = 'awal', rot = { e: 210, s: 128, k: 160 }, jamDetik = null, jamTahap = [], goyang = 0;
  const bersihTahap = () => { jamTahap.forEach((t) => clearTimeout(t)); jamTahap = []; };
  const nanti = (ms, f) => { jamTahap.push(setTimeout(f, ms)); };

  function kelas(t) {
    // kelas getar 'ditolak' hanya hidup selama keadaan salah (tinjauan 29 Sep: dulu menempel → pintu bergetar lagi saat formulir muncul sesudah Keluar)
    Array.from(g.classList).filter((c) => /^t-|^f2$|^cepat$/.test(c) || (t !== 'salah' && /^goyang[12]$/.test(c))).forEach((c) => g.classList.remove(c));
    g.classList.add('t-' + t); tahap = t;
  }
  function putarCincin() {
    const n = Math.min(String(($('isianSandi') || {}).value || '').length, 24); const email = String(($('isianEmail') || {}).value || '');
    const buka = tahap === 'membuka';
    const tunggu = ['belum', 'terkirim', 'nonaktif', 'kasir'].indexOf(tahap) >= 0;
    const isiE = emailSah(email) ? 1 : Math.min(0.9, email.length / 26);
    if (cincin.e) cincin.e.style.transform = 'rotate(' + rot.e + 'deg)';
    if (cincin.s) cincin.s.style.transform = 'rotate(' + (rot.s + 30 * n) + 'deg)';
    if (cincin.k) cincin.k.style.transform = 'rotate(' + rot.k + 'deg)';
    if (cincin.isiE) cincin.isiE.style.strokeDasharray = (KEL.email * isiE).toFixed(1) + ' ' + KEL.email.toFixed(1);
    if (cincin.isiS) cincin.isiS.style.strokeDasharray = (KEL.sandi * (buka ? 1 : Math.min(1, n / 8))).toFixed(1) + ' ' + KEL.sandi.toFixed(1);
    if (cincin.kunci) { cincin.kunci.style.strokeDasharray = tunggu ? '2 10' : (KEL.kunci * 0.84).toFixed(1) + ' ' + (KEL.kunci * 0.16).toFixed(1);
      cincin.kunci.style.strokeDashoffset = tunggu ? '0' : (-KEL.kunci * 0.08).toFixed(1); }
  }
  function jam() {
    const d = new Date();
    const tp = HARI[d.getDay()] + ', ' + d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + d.getFullYear();
    const tr = HARI[d.getDay()] + ', ' + d.getDate() + ' ' + BULAN[d.getMonth()].slice(0, 3) + ' ' + d.getFullYear();
    if ($('gmTanggal') && $('gmTanggal').textContent !== tp) $('gmTanggal').textContent = tp;
    if ($('gmTanggalRingkas') && $('gmTanggalRingkas').textContent !== tr) $('gmTanggalRingkas').textContent = tr;
    const j = dua(d.getHours()) + '.' + dua(d.getMinutes()); if ($('gmJam') && $('gmJam').textContent !== j) $('gmJam').textContent = j;
    if (cincin.detik) { const s = d.getSeconds(); cincin.detik.classList.toggle('lompat', s === 0); cincin.detik.style.strokeDasharray = (KEL.detik * (s + 1) / 60).toFixed(1) + ' ' + KEL.detik.toFixed(1); }
  }
  function nyalakanJam(ya) { clearInterval(jamDetik); jamDetik = null; if (ya) { jam(); jamDetik = setInterval(jam, 1000); } }
  function ikonAkun(jenis) { const el = $('ikonAkun'); if (!el) return; el.className = 'gm-status' + (jenis === 'belum' || jenis === 'nonaktif' ? ' awas' : '');
    el.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true">' + (IKON_STATUS[jenis] || IKON_STATUS.belum) + '</svg>'; }

  /** Tampilkan gerbang TERTUTUP dalam keadaan t. Kalau gerbang sedang terbuka (orang baru saja keluar), pintu merapat dulu.
   *  Kembali: ms sampai formulir terlihat (app.js menunda fokus kolom sebanyak itu — kolom yang tak terlihat tidak bisa difokus). */
  function tutupKe(t) {
    bersihTahap(); nyalakanJam(true);
    const dariTerbuka = tahap === 'terbuka' || tahap === 'membuka';   // orang baru saja keluar dari aplikasi yang sedang terbuka
    g.classList.remove('membuka', 'cepat', 'f2'); g.classList.add('tampil');
    if (dariTerbuka && !diam()) {
      rot = { e: rot.e + 210, s: rot.s + 128, k: rot.k + 160 };
      kelas('menutup'); putarCincin();
      nanti(LAMA.tutup, () => { kelas(t); putarCincin(); });
      return LAMA.tutup;
    }
    kelas(t); putarCincin(); return 0;
  }
  function buka(cepat) {
    bersihTahap();
    if (diam() || !g.classList.contains('tampil')) { g.classList.remove('tampil', 'membuka'); kelas('terbuka'); nyalakanJam(false); return; }
    const n = Math.min(String(($('isianSandi') || {}).value || '').length, 24);
    rot = { e: kelipatan(rot.e) + 360, s: kelipatan(rot.s + 30 * n), k: kelipatan(rot.k) + 360 };
    g.classList.remove('tampil'); g.classList.add('membuka');   // 'tampil' dicabut SEKARANG: layar di belakang sudah boleh diketuk
    kelas('membuka'); if (cepat) g.classList.add('cepat'); putarCincin();
    if (!cepat) nanti(LAMA.fase2, () => g.classList.add('f2'));
    nanti(cepat ? LAMA.bukaCepat : LAMA.buka, () => { g.classList.remove('membuka', 'cepat', 'f2'); kelas('terbuka'); nyalakanJam(false); });
  }

  // ketikan menggerakkan cincin (G2): email mengisi cincinnya, tiap huruf sandi memutar satu takik
  ['isianEmail', 'isianSandi'].forEach((id) => { const el = $(id); if (el) el.addEventListener('input', () => { if (tahap === 'salah') { kelas('masuk'); } putarCincin(); }); });
  const tm = $('gmMode'); if (tm) tm.addEventListener('click', () => opsi.gantiMode());

  return {
    /** Sebelum Firebase menjawab: gerbang tertutup tanpa formulir. */
    mulai() { g.classList.add('tampil'); kelas('menunggu'); nyalakanJam(true); putarCincin(); },
    /** Dipanggil gambarAkun (app.js) tiap keadaan akun berubah. bisa = boleh bekerja (owner / aktif). */
    akun(akun, bisa) {
      const jenis = akun ? akun.jenis : 'keluar';
      if (bisa) { if (g.classList.contains('tampil')) buka(tahap === 'menunggu'); return 0; }
      const t = jenis === 'belum' || jenis === 'nonaktif' || jenis === 'kasir' ? jenis : 'masuk';
      if (t !== 'masuk') ikonAkun(t);
      if (tahap === 'terkirim' && t === 'belum') return 0;   // permintaan sudah terkirim, akun masih menunggu owner
      if (tahap === t && g.classList.contains('tampil')) return 0;   // keadaan akun dibunyikan ulang tanpa berubah — jangan mengulang geraknya
      return tutupKe(t);
    },
    memeriksa() { bersihTahap(); rot.k += 360; kelas('memeriksa'); putarCincin(); },
    /** Ditolak (sandi salah / jaringan): pintu bergetar, cincin kunci berkedip, cincin sandi berputar balik (sandinya sudah dikosongkan). */
    ditolak() { kelas('salah'); goyang += 1; g.classList.remove('goyang1', 'goyang2'); void g.offsetWidth; g.classList.add(goyang % 2 ? 'goyang1' : 'goyang2'); putarCincin(); },
    /** Sandi kosong saat Masuk ditekan: kolom sandi berdenyut (owner 29 Sep: boleh). */
    mintaSandi() { const el = $('isianSandi'); if (!el) return; el.classList.remove('gm-minta'); void el.offsetWidth; el.classList.add('gm-minta');
      el.addEventListener('animationend', () => el.classList.remove('gm-minta'), { once: true }); el.focus(); },
    terkirim() { ikonAkun('terkirim'); kelas('terkirim'); putarCincin(); },
    kembaliMasuk() { if (tahap === 'memeriksa') { kelas('masuk'); putarCincin(); } },
  };
}
