// LAYAR RINGKASAN — GAMBAR & GERAK. R2 "Cincin Bersarang" (dikunci owner 13 Sep 2026); angka & geometri di ringkasan-logika.js.
//
// Permintaan owner (13 Sep): "pergerakan setiap detik, menit, jam, hari, minggu, bulan, tahun … lebih interaktif lagi dan lebih
// hidup lagi dan ada animasi motionnya dibanding sistem lama". Karena itu layar ini TIDAK digambar ulang tiap perubahan:
// kerangkanya dibangun sekali dan elemen-elemennya HIDUP TERUS, sehingga perubahan bisa BERGERAK —
//   · ganti skala  → ketujuh cincin bergeser masuk/keluar (transisi jari-jari), angka bergulir ke nilai barunya, kilau menyapu;
//   · tiap detik   → jarum detik berdetak, jam berjalan; tiap menit sel berjalan & jendela 60 menit bergeser;
//   · nota baru    → tetes emas terbang dari tombol Jual ke angka, kartu "mendarat", chip +Rp naik, baris umpan masuk hangat;
//   · interaktif   → ketuk sel cincin untuk melihat nilainya, ketuk lapis untuk pindah skala, geser kiri/kanan ganti skala.
// Aturan gerak papan R2: gerak = kejadian (tidak ada animasi berputar tanpa henti), kurva tenggelam cubic-bezier(.2,.8,.2,1),
// tempo SENTUH 160 · DATA 480 · SKALA 560 ms; prefers-reduced-motion dihormati (CSS). BACA SAJA.
import { nanti, segera } from '../inti/jadwal.js';   // owner 29 Sep: bunyi data/status digabung sekali per bingkai (lag & freeze)
import { esc } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { RP } from '../inti/format.js';
import * as R from './ringkasan-logika.js';
import { sumberData, dengarkan, kunciLuarCache, ingatPerVersi } from '../data/toko.js';
import { pjPerhatian } from './pajak-logika.js';
import { kpPerhatian, kpPerhatianPerangkat } from './kunci-periode-logika.js';
import { bkPerhatian } from './tutup-buku-logika.js';
import { kkBeranda } from '../data/katalog-kasir.js';
import { hariIniIso } from '../inti/format.js';
import { susunDasbor, dbKelompok, DB_PANAS } from './dasbor-logika.js';   // putaran 40: dasbor owner (saklar Dasbor | Cincin, owner 2 Okt)
import { pasangDasbor } from './dasbor.js';
// paket Dasbor sensus (owner 26 Nov 2026, sensus ulang 1c + desain ulang tata letak): kisi widget Dasbor (dasbor.js + dasbor-kisi.js) — kartu ringkas, widget yang
// owner atur sendiri, headline & saringan tanggal sebagai widget tambahan, cap "data per HH.MM"
import { dbTambahan, dbCapData, dbKunciTambahan, dbSaring } from './dasbor-logika.js';   // B94 (owner 27 Nov 2026): satu saringan untuk semua kartu
import { susunAturDasbor } from './dasbor-widget-logika.js';
import { tulisDokumen, kabarKiriman } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_SKALA = 'miqbal_baru_skala';
const KUNCI_TAMPILAN = 'miqbal_baru_ringkasan_tampilan';   // putaran 40: 'dasbor' | 'cincin' — pilihan terakhir owner diingat per perangkat
const NS = 'http://www.w3.org/2000/svg';
const p2 = (n) => String(n).padStart(2, '0');
const tenggelam = (t) => 1 - Math.pow(1 - t, 3);

export function pasangLayarRingkasan(akar, opsi) {
  // putaran 24: satu baris pajak di Perlu perhatian — owner saja; modul pajak yang galat tidak boleh mematikan beranda
  // putaran 25: satu baris Kunci bulan (owner saja) kalau bulan lalu sudah lewat tenggang dan belum dikunci
  const perhatianKunci = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return kpPerhatian(k); } catch (e) { console.error('perhatian kunci', e); return []; } };
  // putaran 25b: HP kasir menurut denyutnya — antrean, karcis DITOLAK server, versi sebelum 25b (owner saja)
  const perhatianKasir = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return kpPerhatianPerangkat(k); } catch (e) { console.error('perhatian kasir', e); return []; } };
  // putaran 25c: katalog HP kasir — kapan diperbarui, perubahan yang belum sampai, HP kasir yang masih memegang katalog lama (owner saja)
  const katalogKasir = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return null; try { return kkBeranda(k); } catch (e) { console.error('katalog kasir', e); return null; } };
  const perhatianPajak = (k) => ingatRk('pajak', k, () => perhatianPajakHitung(k));   // 19 Nov 2026: diingat per versi + kunci luar + menit + peran (lihat ingatRk)
  const perhatianPajakHitung = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return pjPerhatian(k); } catch (e) { console.error('perhatian pajak', e); return []; } };
  // siap 2027 (owner 7 Okt): tutup buku tahun lalu yang belum selesai sesudah 1 Jan & catatan susulan sesudah penanda (owner saja; galat tidak mematikan beranda)
  const perhatianBuku = (k) => ingatRk('buku', k, () => perhatianBukuHitung(k));
  const perhatianBukuHitung = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return bkPerhatian(k); } catch (e) { console.error('perhatian tutup buku', e); return []; } };
  // putaran 40: DASBOR hanya untuk peran owner (mode cadangan = owner, app.js). Akun lain tidak mendapat saklar maupun dasbornya: Ringkasan apa adanya.
  const pemilik = () => { const a = opsi.akun ? opsi.akun() : null; return !!a && a.jenis === 'owner'; };
  let tampilan = (() => { try { return localStorage.getItem(KUNCI_TAMPILAN) === 'cincin' ? 'cincin' : 'dasbor'; } catch (e) { return 'dasbor'; } })();
  const modeDasbor = () => tampilan === 'dasbor' && pemilik();
  // dbHasil dihitung ulang hanya saat data berubah atau dbKunci berganti; ganti rentang cuma menghitung tren (dbRentang).
  // dbKunci = kunciLuarCache (sanggahan 7 Okt): hari · hari tutup aktif · titik kas yang terbaca — "cek tutup" wadah berganti jam 12 siang dan kas per tempat
  // membaca salinan titik kas perangkat; keduanya tidak menaikkan versi data, jadi denyut HP / ganti rentang / detak menit dulu memajang angka lama.
  let dasbor = null, dbHasil = null, dbKunci = '', dbRentang = '', dbSaringKunci = 'hari';
  // paket Dasbor sensus: daftar Perlu perhatian terakhir (headline & widget Perlu perhatian), kunci "jam segini" 5 menit (banding bergeser walau tanpa catatan baru)
  let perhatianKini = [], dbKunciJam = '';
  const capKini = (k) => dbCapData(opsi.dataPer ? opsi.dataPer() : { jenis: sumberData().jenis }, k);
  /** Simpan susunan widget (owner): satu dokumen aturanToko/dasbor. Hasil { ok, kabar } untuk puncak Dasbor. */
  async function simpanWidget(daftar) {
    const k = kini(); const r = susunAturDasbor(daftar, { tanggal: hariIniIso(k), jam: p2(k.getHours()) + ':' + p2(k.getMinutes()) });
    if (r.tolak) return { ok: false, kabar: r.tolak };
    try { const x = await tulisDokumen(r.dokumen, [], {}); if (x && x.gagal) return { ok: false, kabar: 'DITOLAK: ' + x.pesan }; return { ok: true, kabar: kabarKiriman(x, r.patch.kabar) }; }
    catch (e) { return { ok: false, kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e) }; }
  }
  let skala = (() => { try { return localStorage.getItem(KUNCI_SKALA) || 'jam'; } catch (e) { return 'jam'; } })();
  if (!R.SKALA.some((s) => s[0] === skala)) skala = 'jam';
  let ix = null, ixTahun = '', tampil = false, menitLama = -1, kunciNotaLama = null, angkaTampil = null, rafAngka = 0, sektorKini = [], pilihId = null, jamPilih = 0, detikTotal = 0, jagaAngka = 0;
  const lingkar = new Map();   // id sel → <circle> yang hidup terus
  const kini = () => opsi.sekarang() || new Date();
  const $ = (id) => akar.querySelector('#' + id);

  // ---------- kerangka: dibangun saat tirai terbuka (putaran 23c: selama belum masuk, <main> ini KOSONG) ----------
  // rapi-rapi 29 Sep (kelompok 2): kas, perhatian & catatan katalog dikumpulkan di <aside class="rk-samping"> (dulu tiga sel lepas yang menyisakan lubang
  // di kolom kanan). Urutan tampil diatur ringkasan.css: HP = hero · nota · samping; tablet = nota | samping; Mac = hero & nota kiri, samping kanan menempel.
  function bangun() {
  lingkar.clear(); angkaTampil = null; kunciNotaLama = null; sektorKini = []; pilihId = null;
  akar.innerHTML = `
    <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
    <div class="tetes-terbang" id="rkTetes"></div>
    <header class="kepala-jual kepala-ringkasan">
      <div><div class="label"><span id="rkTanggal"></span> · <span id="rkJam" style="letter-spacing: 0.1em;"></span></div><div class="serif" style="font-size: 22px;" id="rkSalam"></div></div>
      <div style="display: flex; gap: 8px; align-items: center;">${opsi.lonceng ? opsi.lonceng() : ''}<div class="pil pil-akun" id="rkPil" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar"></div><div class="tombol-mode" id="rkMode"></div></div>
    </header>
    <div id="rkSumber"></div>
    <div class="pita rk-saklar" id="rkSaklar" hidden><div class="seg" data-tampil="dasbor">Dasbor</div><div class="seg" data-tampil="cincin">Cincin</div></div>
    <div class="kartu hero" id="rkHero"><div class="kilau" id="rkKilau"></div>
      <div class="label" style="color: var(--hero-label);" id="rkJudul"></div>
      <div class="angka dagang angka-besar" id="rkAngka" style="font-size: clamp(28px, 8vw, 44px);"></div>
      <div class="ket" id="rkSub"></div>
      <div class="ket" style="font-size: 12px;" id="rkBanding"></div>
      <div class="chip-naik" id="rkChip"></div>
      <div class="badan-hero">
        <div class="lapis" id="rkLapis"></div>
        <div class="cincin-wadah"><div class="cincin-kotak"><svg class="cincin" id="rkCincin" viewBox="-6 -6 212 212">
          <g id="rkSektorG"></g>
          <line class="jarum" x1="100" y1="60" x2="100" y2="4"></line>
          <text class="pusat-jam" id="rkPusatJam" x="100" y="98" text-anchor="middle"></text>
          <text class="pusat-ket" id="rkPusatKet" x="100" y="112" text-anchor="middle"></text>
          <text class="pusat-ket" id="rkPusatKet2" x="100" y="124" text-anchor="middle"></text>
        </svg><svg class="rk-detik" id="rkDetik" viewBox="-6 -6 212 212" aria-hidden="true"><line x1="100" y1="34" x2="100" y2="24"></line></svg></div></div>
      </div>
      <div class="rk-detail" id="rkDetail"></div>
      <div class="pita" id="rkSkala"></div>
    </div>
    <section class="rk-dasbor" id="rkDasbor" hidden></section>
    <aside class="rk-samping">
      <div class="dua" id="rkKas"></div>
      <div class="kartu" style="gap: 6px;" id="rkPerhatian"></div>
      <div class="ket" style="font-size: 11.5px; padding: 0 4px;" id="rkKatalog"></div>
    </aside>
    <div class="kartu rk-nota" style="gap: 4px; padding: 10px 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Nota hari ini</div><div class="ket" style="font-size: 11.5px;" id="rkSejak"></div></div>
      <div class="umpan" id="rkUmpan"></div>
      <div class="ket" style="text-align: right; cursor: pointer; text-decoration: underline;" id="rkKeJual">catat nota →</div>
    </div>`;
  $('rkSkala').innerHTML = R.SKALA.map(([id, nm]) => `<div class="seg" data-k="${id}">${esc(nm)}</div>`).join('');

  $('rkSkala').addEventListener('click', (ev) => { const el = ev.target.closest('[data-k]'); if (el) gantiSkala(el.dataset.k); });
  $('rkLapis').addEventListener('click', (ev) => { const el = ev.target.closest('[data-lapis]'); if (el) gantiSkala(R.SKALA_DARI_LAPIS[el.dataset.lapis]); });
  $('rkMode').addEventListener('click', () => opsi.gantiMode());
  $('rkSaklar').addEventListener('click', (ev) => { const el = ev.target.closest('[data-tampil]'); if (el) gantiTampilan(el.dataset.tampil); });
  dasbor = pasangDasbor($('rkDasbor'), { keTujuan: (t) => (opsi.keTujuan ? opsi.keTujuan(t) : opsi.pindah(t.ke)), mintaRentang: () => gambarDasbor(true),   // B94: ganti saringan memakai jalur yang sama (gambarDasbor membaca dasbor.saring())
    // desain ulang (owner 26 Nov 2026): kisi widget menyimpan susunannya sendiri, memakai ingatan dasbor & tahu jalan ke Perlu perhatian
    kini, ingat: (kunci, f) => ingatDb(kini())(kunci, f), simpanWidget,
    kePerhatian: () => { const el = $('rkPerhatian'); if (!el || !el.offsetParent) return; try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { el.scrollIntoView(); } sekali(el, 'rk-sorot', 1400); } });
  dbHasil = null;
  $('rkKeJual').addEventListener('click', () => opsi.pindah('jual'));
  $('rkCincin').addEventListener('click', (ev) => {
    const kotak = $('rkCincin').getBoundingClientRect(); const skalaPx = 212 / kotak.width;
    const x = (ev.clientX - kotak.left) * skalaPx - 6 - 100, y = (ev.clientY - kotak.top) * skalaPx - 6 - 100;
    const jarak = Math.sqrt(x * x + y * y); const sudut = Math.atan2(x, -y) * 180 / Math.PI;   // searah jarum jam dari jam 12
    const s = R.selDariKetukan(sektorKini, jarak, sudut);
    pilihId = s && s.id !== pilihId ? s.id : null; jamPilih = Date.now(); gambarPilihan();
  });
  // geser kiri/kanan di kartu besar = skala berikut/sebelumnya
  $('rkHero').addEventListener('touchstart', (ev) => { const t = ev.touches[0]; sentuhX = t.clientX; sentuhY = t.clientY; }, { passive: true });
  $('rkHero').addEventListener('touchend', (ev) => {
    if (sentuhX === null) return; const t = ev.changedTouches[0]; const dx = t.clientX - sentuhX, dy = t.clientY - sentuhY; sentuhX = null;
    if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy) * 1.5 || ev.target.closest('#rkSkala')) return;
    const i = R.SKALA.findIndex((s) => s[0] === skala); const j = Math.max(0, Math.min(R.SKALA.length - 1, i + (dx < 0 ? 1 : -1))); gantiSkala(R.SKALA[j][0]);
  }, { passive: true });

  }
  let sentuhX = null, sentuhY = null;
  // ---------- interaksi ----------
  function gantiTampilan(m) { if (m === tampilan || (m !== 'dasbor' && m !== 'cincin')) return; tampilan = m; try { localStorage.setItem(KUNCI_TAMPILAN, m); } catch (e) { /* abaikan */ } angkaTampil = null; kunciNotaLama = null; perbarui('tampil'); }
  /** Dasbor owner: hitung (kalau basi) lalu gambar. masuk = animasi masuk ringan (buka dasbor, ganti rentang). */
  function gambarDasbor(masuk) {
    if (!dasbor || !$('rkDasbor')) return;
    const k = kini(); const kunci = kunciLuarCache(k); const r = dasbor.rentang(); const S = saringKini(k); const sk = S ? S.kunci : 'hari';
    if (!dbHasil || dbKunci !== kunci || dbSaringKunci !== sk) { dbHasil = susunDasbor(k, r, null, ingatDb(k), S); dbKunci = kunci; dbRentang = r; dbSaringKunci = sk; }
    else if (dbRentang !== r) { dbHasil = susunDasbor(k, r, dbHasil, ingatDb(k), S); dbRentang = r; }
    lukisDasbor(k, masuk);
  }
  /** B94: saringan Dasbor yang berlaku (pilihan pita di atas kisi, diingat perangkat) — null bila belum terpasang / gagal (= Hari ini, Dasbor seperti dulu). */
  function saringKini(k) { try { return dasbor && dasbor.saring ? dbSaring(dasbor.saring(), k) : null; } catch (e) { return null; } }
  /** paket Dasbor sensus: kelompok tambahan (banding · stok minimum · enam bulan, diingat per kelompok) + cap, lalu kartu & puncak Dasbor digambar. */
  function lukisDasbor(k, masuk) {
    dbTambahan(dbHasil, k, ingatDb(k)); dbKunciJam = dbKunciTambahan('banding', k);
    const c = capKini(k); dasbor.gambar(dbHasil, masuk, { perhatian: perhatianKini, cap: c }); dasbor.cap(c);
  }
  function gantiSkala(k) { if (k === skala || !R.SKALA.some((s) => s[0] === k)) return; skala = k; pilihId = null; try { localStorage.setItem(KUNCI_SKALA, k); } catch (e) { /* abaikan */ } perbarui('skala'); }
  if (!terkunci()) bangun();

  function gambarPilihan() {
    const s = pilihId ? sektorKini.find((x) => x.id === pilihId && x.op === 1) : null;
    lingkar.forEach((el, id) => el.classList.toggle('dipilih', !!s && id === s.id));
    $('rkCincin').classList.toggle('memilih', !!s);
    const d = $('rkDetail');
    if (!s) { d.classList.remove('tampil'); d.textContent = 'ketuk sel cincin untuk melihat nilainya · geser kiri/kanan ganti skala'; return; }
    d.textContent = s.label + ' · ' + (s.keadaan === 'absen' ? 'sebelum toko mulai mencatat' : s.keadaan === 'rel' ? (s.nilai === 'rel' ? 'belum terjadi' : 'tidak ada nota') : s.nilai === null ? 'ada nota' : RP(s.nilai) + (s.keadaan === 'berjalan' ? ' · masih berjalan' : ''));
    d.classList.add('tampil');
  }

  // ---------- gerak ----------
  function gulirAngka(ke, lama) {
    cancelAnimationFrame(rafAngka);
    const el = $('rkAngka'); const dari = angkaTampil === null ? 0 : angkaTampil; const mulai = performance.now();
    const tulis = (n) => { el.innerHTML = R.kelompokAngka(n).map((t) => '<span class="klp">' + esc(t) + '</span>').join(''); };
    clearTimeout(jagaAngka);
    // tab tersembunyi = requestAnimationFrame tidak pernah jalan → angka tidak boleh tertahan di nilai lama: tulis langsung
    if (dari === ke || document.hidden || matchMedia('(prefers-reduced-motion: reduce)').matches) { angkaTampil = ke; tulis(ke); return; }
    const langkah = (kinim) => { const t = Math.max(0, Math.min(1, (kinim - mulai) / lama)); const n = Math.round(dari + (ke - dari) * tenggelam(t)); angkaTampil = n; tulis(n); if (t < 1) rafAngka = requestAnimationFrame(langkah); };
    rafAngka = requestAnimationFrame(langkah);
    jagaAngka = setTimeout(() => { if (angkaTampil !== ke) { cancelAnimationFrame(rafAngka); angkaTampil = ke; tulis(ke); } }, lama + 200);   // penjaga: nilai AKHIR selalu benar
  }
  function sekali(el, kelas, lamaMs) { el.classList.remove(kelas); void el.offsetWidth; el.classList.add(kelas); setTimeout(() => el.classList.remove(kelas), lamaMs); }
  function terbangkanTetes() {
    const dari = document.querySelector('.nav [data-tujuan="jual"], .side [data-tujuan="jual"]'); const ke = $('rkAngka'); const t = $('rkTetes'); if (!dari || !ke) return;
    const a = dari.getBoundingClientRect(), b = ke.getBoundingClientRect();
    t.style.left = (a.left + a.width / 2 - 5) + 'px'; t.style.top = (a.top + a.height / 2 - 5) + 'px';
    t.style.setProperty('--tx', (b.left + 40 - (a.left + a.width / 2)) + 'px'); t.style.setProperty('--ty', (b.top + b.height / 2 - (a.top + a.height / 2)) + 'px');
    sekali(t, 'terbang', 620);
  }
  function pasangSektor(daftar, pertama) {
    const g = $('rkSektorG'); const ada = new Set();
    daftar.forEach((s) => {
      ada.add(s.id); let el = lingkar.get(s.id);
      if (!el) {
        el = document.createElementNS(NS, 'circle'); el.setAttribute('cx', '100'); el.setAttribute('cy', '100'); el.setAttribute('transform', 'rotate(-90 100 100)');
        // lahir tanpa panjang & tak terlihat → target dipasang di frame berikutnya, jadi cincin MENGGAMBAR DIRINYA
        el.style.r = s.r + 'px'; el.style.strokeWidth = s.w + 'px'; el.style.strokeDasharray = '0 ' + (2 * Math.PI * s.r).toFixed(2); el.style.strokeDashoffset = s.do + 'px'; el.style.opacity = '0';
        g.appendChild(el); lingkar.set(s.id, el);
      }
      const tetapSembunyi = el.style.opacity === '0' && s.op === 0 && !pertama;   // tersembunyi → tersembunyi: pindah tanpa transisi (hemat ±90 transisi per ganti skala)
      const kelas = 'sektor ' + s.kelas + (s.id === pilihId ? ' dipilih' : '') + (tetapSembunyi ? ' diam' : '');
      if (el.getAttribute('class') !== kelas) el.setAttribute('class', kelas);
      // mulus Android paket 3: sel yang target gambarnya TIDAK berubah (detak menit menggeser sebagian kecil sel) tidak disentuh — dulu ±90 lingkaran diberi
      // gaya ulang tiap pembaruan, dan tiap sentuhan = gaya & cat ulang SVG di utas utama tablet
      const sidik = s.r + '|' + s.w + '|' + s.da + '|' + s.do + '|' + s.op;
      if (!pertama && el._sidik === sidik) return;
      el._sidik = sidik;
      const pasang = () => { el.style.r = s.r + 'px'; el.style.strokeWidth = s.w + 'px'; el.style.strokeDasharray = s.da; el.style.strokeDashoffset = s.do + 'px'; el.style.opacity = String(s.op); };
      if (pertama && !document.hidden) { el.style.transitionDelay = (s.op ? Math.min(420, s.i * 9) : 0) + 'ms'; setTimeout(pasang, 40); setTimeout(() => { el.style.transitionDelay = ''; }, 1400); } else pasang();
    });
    lingkar.forEach((el, id) => { if (!ada.has(id)) { el.remove(); lingkar.delete(id); } });   // mis. lapis tahun bertambah sel
  }

  // ---------- pembaruan: mengisi elemen yang sudah hidup ----------
  // owner 19 Nov 2026 (kartu Kelancaran tablet: Ringkasan › Cincin tersendat tiap ketuk skala): daftar perhatian, susunan satu skala & kartu kas dulu dihitung
  // ulang TIAP perbarui — laba rentang dari mesin, bon, utang, buku stok — padahal isinya hanya data + jam (menit) + kunci luar (hari, hari tutup, titik kas
  // perangkat) + siapa yang masuk. Kini diingat per versi data dengan kunci itu: skala yang baru saja dilihat kembali seketika, detak menit tetap menghitung
  // segar. Katalog kasir & denyut HP kasir TIDAK ikut (keduanya membaca keadaan di luar cache). Hasil DIPAKAI BERSAMA — penggambar hanya membaca.
  // mulus Android paket 3 (owner 23 Nov 2026, kartu CPad: Ringkasan › Cincin 481 kali tersendat ±0,4 dtk = SATU KALI TIAP MENIT selama ±8 jam layar ini
  // terbuka): kunci menit dulu dipasang di SEMUA hitungan, jadi tiap detak menit bon, utang pemasok, laju & stok menipis, kas, pajak dihitung ulang dari nol.
  // Yang benar-benar membaca jam-menit hanya SUSUNAN cincin (sel berjalan, jendela 60 menit, "nota terakhir N mnt lalu"); perhatian, kas, pajak & tutup buku
  // membaca HARI (sudah di kunciLuarCache) — kini kuncinya per hari. menit = true hanya untuk susunan.
  const ingatRk = (nama, k, f, menit) => ingatPerVersi('rk|' + nama + '|' + kunciLuarCache(k) + '|' + (menit ? Math.floor(k.getTime() / 60000) : '') + '|' + (((opsi.akun ? opsi.akun() : null) || {}).jenis || ''), f);
  // Dasbor: tiap kelompok diingat per versi data + kunci luar (hari, hari tutup aktif, titik kas perangkat) — kunci yang sama dengan dbKunci di bawah
  const ingatDb = (k) => (kunci, f) => ingatPerVersi('db|' + kunci + '|' + kunciLuarCache(k), f);
  // tulis isi elemen HANYA bila berubah — detak menit yang isinya sama tidak memaksa peramban menata & mengecat ulang kartunya
  const isi = (el, html) => { if (el && el._isi !== html) { el.innerHTML = html; el._isi = html; } };
  function perbarui(sebab) {
    if (!tampil || terkunci()) return;
    if (!$('rkHero')) bangun();   // tirai baru terbuka: kerangka dibangun ulang
    const k = kini(); const KK = katalogKasir(k); const perhatian = ingatRk('perhatian', k, () => R.susunPerhatian()).concat(perhatianKasir(k), KK ? KK.perhatian : [], perhatianPajak(k), perhatianBuku(k), perhatianKunci(k)); const sumber = sumberData();
    // putaran 40: saklar Dasbor | Cincin hanya untuk owner; mode dasbor menyembunyikan cincin, nota & kartu kas (angkanya ada di dasbor) — perhatian tetap
    const dsb = modeDasbor(); akar.classList.toggle('mode-dasbor', dsb); $('rkSaklar').hidden = !pemilik(); $('rkDasbor').hidden = !dsb;
    perhatianKini = perhatian;
    akar.querySelectorAll('#rkSaklar .seg').forEach((el) => el.classList.toggle('aktif', el.dataset.tampil === (dsb ? 'dasbor' : 'cincin')));
    $('rkTanggal').textContent = R.tanggalPanjang(k); $('rkSalam').textContent = R.salam(k) + ', Owner';
    const pil = $('rkPil'); pil.textContent = sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'; pil.classList.toggle('kedip', sumber.jenis !== 'firestore');
    isi($('rkMode'), IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap']);
    isi($('rkSumber'), sumber.jenis === 'cadangan' ? '<div class="pita-info emas">Angka dari ' + esc(sumber.keterangan) + ' — "sekarang" dianggap saat cadangan itu diunduh.</div>' : sumber.jenis !== 'firestore' ? '<div class="pita-info awas">Belum tersambung ke data toko — masuk dulu sebagai owner (layar Jual).</div>' : '');
    isi($('rkPerhatian'), '<div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Perlu perhatian</div><span class="pil" style="' + (perhatian.some((x) => x.awas) ? 'color: var(--awas);' : '') + '">' + (perhatian.length ? perhatian.length + ' hal' : 'aman') + '</span></div>'
      + (perhatian.map((x, i) => '<div class="baris ' + (i === perhatian.length - 1 ? 'akhir' : '') + '"><span>' + esc(x.teks) + '</span><span class="angka ' + (x.awas ? 'awas' : '') + '" style="font-size: 14px; white-space: nowrap;">' + esc(x.nilai) + '</span></div>').join('')
        || '<div class="menolak">Tidak ada bon, utang pemasok, stok menipis, atau pesanan yang menunggu.</div>'));
    if ($('rkKatalog')) { $('rkKatalog').textContent = KK ? KK.status : ''; $('rkKatalog').style.color = KK && KK.awas ? 'var(--awas)' : ''; }
    if (dsb) {
      menitLama = k.getHours() * 60 + k.getMinutes();
      // tiap menit: digambar ulang hanya kalau kunci dasbor basi (hari, jam 12 siang, titik kas perangkat); data baru & buka layar selalu
      if (sebab !== 'menit' || !dbHasil || dbKunci !== kunciLuarCache(k) || dbRentang !== dasbor.rentang()) gambarDasbor(sebab === 'tampil');
      else if (dbKunciJam !== dbKunciTambahan('banding', k) && !dasbor.sedangAtur()) lukisDasbor(k, false);   // tiap 5 menit: "jam segini" bergeser
      else dasbor.cap(capKini(k));   // tiap menit: cap "data per HH.MM" saja, tanpa menggambar ulang
      detak(true); return;
    }
    // indeks cincin hanya membaca cache + TAHUN jam sekarang (potret hari tahun yang ditutup buku, bangunIndeks) — tahun ikut kunci: tanpa data baru (denyut HP
    // tidak lagi membasikan indeks) pergantian tahun tetap membangunnya ulang
    const thIx = hariIniIso(new Date(Date.now())).slice(0, 4); if (!ix || ixTahun !== thIx) { ix = R.bangunIndeks(); ixTahun = thIx; }
    const r = ingatRk('susun|' + skala, k, () => R.susunRingkasan(skala, ix, k), true); const kas = ingatRk('kas', k, () => R.susunKas(k));
    menitLama = k.getHours() * 60 + k.getMinutes(); sektorKini = r.sektor;
    const pertama = sebab === 'tampil'; const gantiSk = sebab === 'skala';
    const kunciBaru = r.umpan.length ? r.umpan[0].k : ''; const mendarat = !pertama && kunciNotaLama !== null && !!kunciBaru && kunciBaru !== kunciNotaLama; kunciNotaLama = kunciBaru;
    const naik = !pertama && !gantiSk && angkaTampil !== null ? r.angka - angkaTampil : 0;

    $('rkJudul').textContent = r.judul; $('rkSub').textContent = r.sub; $('rkBanding').textContent = r.banding;
    if (gantiSk) { sekali($('rkAngka'), 'ganti', 260); sekali($('rkKilau'), 'sapu', 1150); [$('rkJudul'), $('rkSub'), $('rkBanding'), $('rkLapis')].forEach((el) => sekali(el, 'ganti-teks', 420)); }
    gulirAngka(r.angka, pertama ? 900 : gantiSk ? 560 : 640);
    if (naik > 0) { const c = $('rkChip'); c.textContent = '+' + RP(naik); sekali(c, 'tampil', 1250); }
    if (mendarat) { terbangkanTetes(); setTimeout(() => { sekali($('rkHero'), 'mendarat', 1400); sekali($('rkKilau'), 'sapu', 1150); }, 420); }
    isi($('rkLapis'), r.lapisan.map((l) => '<div data-lapis="' + esc(l.lapis) + '"><div class="label">' + esc(l.nama) + '</div><div class="angka">' + esc(l.nilai) + '</div><div class="ket">' + esc(l.ket) + '</div></div>').join('')
      + (r.lapisan.length < 3 ? '<div class="menolak">' + (r.lapisan.length === 2 ? 'Belum ada lapisan di bawah tahun.' : 'Belum ada lapisan induk maupun kakek.') + '</div>' : ''));
    pasangSektor(r.sektor, pertama);
    $('rkPusatJam').textContent = p2(k.getHours()) + '.' + p2(k.getMinutes()); $('rkPusatKet').textContent = r.notaHariIni + ' NOTA'; $('rkPusatKet2').textContent = 'hari ini';
    akar.querySelectorAll('#rkSkala .seg').forEach((el) => el.classList.toggle('aktif', el.dataset.k === skala));
    const aktif = akar.querySelector('#rkSkala .seg.aktif'); if (aktif && gantiSk && aktif.scrollIntoView) aktif.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    gambarPilihan();
    const sj = r.sejakNotaMenit; $('rkSejak').textContent = sj === null ? 'belum ada nota hari ini' : sj < 1 ? 'nota terakhir baru saja' : 'nota terakhir ' + (sj < 60 ? sj + ' mnt lalu' : Math.floor(sj / 60) + ' jam ' + (sj % 60) + ' mnt lalu');
    isi($('rkUmpan'), r.umpan.slice(0, skala === 'langsung' ? 8 : 4).map((u, i) => '<div class="u ' + (mendarat && i === 0 ? 'baru' : '') + '"><span class="w">' + esc(u.jam) + '</span><span style="min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">' + esc(u.isi) + '</span><span class="angka" style="font-size: 13px;">' + esc(RP(u.rp)) + '</span></div>').join('')
      || '<div class="menolak" style="padding: 8px 0;">Belum ada nota hari ini.</div>');
    isi($('rkKas'), '<div class="kartu platina"><div class="label">Kas tercatat · semua kantong</div>' + (kas.adaTitik ? '<div class="angka kas" style="font-size: 20px;">' + esc(RP(kas.total)) + '</div><div class="ket" style="font-size: 11.5px;">dihitung dari titik kas ' + esc(kas.titikTanggal) + '</div>'
      : '<div class="menolak">Titik kas belum ada — Tutup hari malam ini (Uang › Tutup hari) menyetelnya untuk semua perangkat. Tanpa itu saldo tidak ditebak.</div>') + '</div>'
      + '<div class="kartu platina"><div class="label">Uang hari ini</div><div class="angka kas" style="font-size: 20px;">+ ' + esc(RP(kas.masukLaci + kas.masukRek)) + '</div><div class="ket" style="font-size: 11.5px;">laci ' + esc(RP(kas.masukLaci)) + ' · rekening ' + esc(RP(kas.masukRek)) + (kas.keluar ? ' · keluar ' + esc(RP(kas.keluar)) : '') + '</div></div>');
    detak(true);
  }

  // detak tiap detik: jam & jarum detik BERGERAK tanpa menggambar ulang; ganti menit → jendela & sel berjalan bergeser
  function detak(paksa) {
    if (!tampil || terkunci() || !$('rkJam')) return;
    const k = kini(); const hidup = !opsi.sekarang();
    $('rkJam').textContent = p2(k.getHours()) + '.' + p2(k.getMinutes()) + '.' + p2(k.getSeconds());
    detikTotal += ((k.getSeconds() - (detikTotal % 60)) + 60) % 60;   // sudut selalu MAJU — dari detik 59 ke 0 jarum tidak berputar balik
    // jarum detik = <svg> lapisan sendiri di atas cincin (mulus Android paket 3): yang diputar KOTAKNYA (transform dikomposit kartu grafis), bukan garis di
    // dalam SVG cincin — dulu tiap detik 420 ms gaya & cat ulang seluruh cincin di utas utama tablet
    const dt = $('rkDetik'); const putar = 'rotate(' + (detikTotal * 6) + 'deg)'; if (dt.style.transform !== putar) dt.style.transform = putar;
    const op = hidup ? '' : '0.25'; if (dt.style.opacity !== op) dt.style.opacity = op;
    if (pilihId && Date.now() - jamPilih > 8000) { pilihId = null; gambarPilihan(); }
    if (!paksa && k.getHours() * 60 + k.getMinutes() !== menitLama) perbarui('menit');
  }
  setInterval(() => detak(false), 1000);
  const perbaruiData = () => perbarui('data');
  const perbaruiTampil = () => perbarui('tampil');   // owner 29 Sep: dulu digambar langsung di ketukan (±80 ms menahan pindah layar)
  const basiSemua = () => { ix = null; dbHasil = null; };
  let _panas = 0, _sentuhAkhir = 0;
  document.addEventListener('pointerdown', () => { _sentuhAkhir = Date.now(); }, { capture: true, passive: true });
  const luang = (f) => (typeof requestIdleCallback === 'function' ? requestIdleCallback(f, { timeout: 5000 }) : setTimeout(f, 250));   // indeks cincin & hasil dasbor dihitung ulang di gambar berikutnya
  // owner 3 Okt (patah-patah): denyut HP (perangkatStatus, tiap ±5 menit per perangkat) & jejak tulisan (logAktivitas) tidak dibaca dasbor maupun indeks cincin
  // (pola BUKAN_RAK di Jual) — keduanya tidak membasikan hasil itu; Perlu perhatian (denyut kasir, antrean) tetap dihitung ulang di perbarui()
  const BUKAN_DASBOR = new Set(['perangkatStatus', 'logAktivitas']);
  const basiPanaskan = () => { basiSemua(); panaskanDasbor(); };
  dengarkan((nama) => { if (!BUKAN_DASBOR.has(nama)) basiPanaskan(); nanti(perbaruiData); });

  // PEMANASAN DASBOR DI LATAR (mulus Android paket 3, owner 23 Nov 2026; sisa paket 2: "Dasbor dibuka sesudah data berubah ±230 ms Mac, ±2 dtk tablet").
  // Data berubah selagi Dasbor TIDAK tampil → kelompoknya dihitung SATU PER SATU di waktu luang peramban (requestIdleCallback; Safari: jeda pendek), hanya untuk
  // owner yang memilih Dasbor, dan ditunda selama jari masih bekerja (≤ 1,5 dtk sejak sentuhan terakhir). Kuncinya SAMA dengan yang dipakai gambarDasbor →
  // Dasbor yang dibuka sesudahnya tinggal menggambar. Data berubah lagi di tengah jalan = rantai lama berhenti, rantai baru mulai (hasil tetap per versi data).
  function panaskanDasbor() {
    if (!pemilik() || tampilan !== 'dasbor' || (tampil && modeDasbor()) || terkunci() || !dasbor) return;   // Dasbor yang sedang tampil dihitung perbarui()
    const token = ++_panas; let i = 0;
    const langkah = () => {
      if (token !== _panas || !dasbor || (tampil && modeDasbor())) return;
      if (Date.now() - _sentuhAkhir < 1500) { luang(langkah); return; }
      const k = kini(); dbKelompok(DB_PANAS[i], k, dasbor.rentang(), ingatDb(k), saringKini(k)); i += 1;
      if (i < DB_PANAS.length) luang(langkah);
    };
    setTimeout(() => luang(langkah), 1200);
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) perbarui('data'); });   // kembali ke depan → angka & cincin diselaraskan

  // putaran 23d: Beranda tidak punya kolom isian — tidak ada yang ditanyakan atau dikosongkan saat ganti orang (tirai sudah mengosongkan tampilannya)
  return {
    belumDisimpan: () => false, lupakanOrang: () => {},
    gambar: perbaruiData,   // fungsi yang SAMA dengan pendengar data → penjadwal menggabungnya (tinjauan 29 Sep: dulu digambar dua kali per bingkai)
    tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { angkaTampil = null; kunciNotaLama = null; akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); segera(perbaruiTampil); } },
  };
}
