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
import { esc } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { RP } from '../inti/format.js';
import * as R from './ringkasan-logika.js';
import { sumberData, dengarkan } from '../data/toko.js';
import { pjPerhatian } from './pajak-logika.js';
import { kpPerhatian } from './kunci-periode-logika.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_SKALA = 'miqbal_baru_skala';
const NS = 'http://www.w3.org/2000/svg';
const p2 = (n) => String(n).padStart(2, '0');
const tenggelam = (t) => 1 - Math.pow(1 - t, 3);

export function pasangLayarRingkasan(akar, opsi) {
  // putaran 24: satu baris pajak di Perlu perhatian — owner saja; modul pajak yang galat tidak boleh mematikan beranda
  // putaran 25: satu baris Kunci bulan (owner saja) kalau bulan lalu sudah lewat tenggang dan belum dikunci
  const perhatianKunci = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return kpPerhatian(k); } catch (e) { console.error('perhatian kunci', e); return []; } };
  const perhatianPajak = (k) => { const a = opsi.akun ? opsi.akun() : null; if (!a || a.jenis !== 'owner') return []; try { return pjPerhatian(k); } catch (e) { console.error('perhatian pajak', e); return []; } };
  let skala = (() => { try { return localStorage.getItem(KUNCI_SKALA) || 'jam'; } catch (e) { return 'jam'; } })();
  if (!R.SKALA.some((s) => s[0] === skala)) skala = 'jam';
  let ix = null, tampil = false, menitLama = -1, kunciNotaLama = null, angkaTampil = null, rafAngka = 0, sektorKini = [], pilihId = null, jamPilih = 0, detikTotal = 0, jagaAngka = 0;
  const lingkar = new Map();   // id sel → <circle> yang hidup terus
  const kini = () => opsi.sekarang() || new Date();
  const $ = (id) => akar.querySelector('#' + id);

  // ---------- kerangka: dibangun saat tirai terbuka (putaran 23c: selama belum masuk, <main> ini KOSONG) ----------
  function bangun() {
  lingkar.clear(); angkaTampil = null; kunciNotaLama = null; sektorKini = []; pilihId = null;
  akar.innerHTML = `
    <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
    <div class="tetes-terbang" id="rkTetes"></div>
    <header class="kepala-jual kepala-ringkasan">
      <div><div class="label"><span id="rkTanggal"></span> · <span id="rkJam" style="letter-spacing: 0.1em;"></span></div><div class="serif" style="font-size: 22px;" id="rkSalam"></div></div>
      <div style="display: flex; gap: 8px; align-items: center;"><div class="pil pil-akun" id="rkPil" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar"></div><div class="tombol-mode" id="rkMode"></div></div>
    </header>
    <div id="rkSumber"></div>
    <div class="kartu hero" id="rkHero"><div class="kilau" id="rkKilau"></div>
      <div class="label" style="color: var(--hero-label);" id="rkJudul"></div>
      <div class="angka dagang angka-besar" id="rkAngka" style="font-size: clamp(28px, 8vw, 44px);"></div>
      <div class="ket" id="rkSub"></div>
      <div class="ket" style="font-size: 12px;" id="rkBanding"></div>
      <div class="chip-naik" id="rkChip"></div>
      <div class="badan-hero">
        <div class="lapis" id="rkLapis"></div>
        <div class="cincin-wadah"><svg class="cincin" id="rkCincin" viewBox="-6 -6 212 212">
          <g id="rkSektorG"></g>
          <line class="jarum" x1="100" y1="60" x2="100" y2="4"></line>
          <line class="jarum-detik" id="rkDetik" x1="100" y1="34" x2="100" y2="24"></line>
          <text class="pusat-jam" id="rkPusatJam" x="100" y="98" text-anchor="middle"></text>
          <text class="pusat-ket" id="rkPusatKet" x="100" y="112" text-anchor="middle"></text>
          <text class="pusat-ket" id="rkPusatKet2" x="100" y="124" text-anchor="middle"></text>
        </svg></div>
      </div>
      <div class="rk-detail" id="rkDetail"></div>
      <div class="pita" id="rkSkala"></div>
    </div>
    <div class="kartu" style="gap: 4px; padding: 10px 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Nota hari ini</div><div class="ket" style="font-size: 11.5px;" id="rkSejak"></div></div>
      <div class="umpan" id="rkUmpan"></div>
      <div class="ket" style="text-align: right; cursor: pointer; text-decoration: underline;" id="rkKeJual">catat nota →</div>
    </div>
    <div class="dua" id="rkKas"></div>
    <div class="kartu" style="gap: 6px;" id="rkPerhatian"></div>`;
  $('rkSkala').innerHTML = R.SKALA.map(([id, nm]) => `<div class="seg" data-k="${id}">${esc(nm)}</div>`).join('');

  $('rkSkala').addEventListener('click', (ev) => { const el = ev.target.closest('[data-k]'); if (el) gantiSkala(el.dataset.k); });
  $('rkLapis').addEventListener('click', (ev) => { const el = ev.target.closest('[data-lapis]'); if (el) gantiSkala(R.SKALA_DARI_LAPIS[el.dataset.lapis]); });
  $('rkMode').addEventListener('click', () => opsi.gantiMode());
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
      el.setAttribute('class', 'sektor ' + s.kelas + (s.id === pilihId ? ' dipilih' : '') + (tetapSembunyi ? ' diam' : ''));
      const pasang = () => { el.style.r = s.r + 'px'; el.style.strokeWidth = s.w + 'px'; el.style.strokeDasharray = s.da; el.style.strokeDashoffset = s.do + 'px'; el.style.opacity = String(s.op); };
      if (pertama && !document.hidden) { el.style.transitionDelay = (s.op ? Math.min(420, s.i * 9) : 0) + 'ms'; setTimeout(pasang, 40); setTimeout(() => { el.style.transitionDelay = ''; }, 1400); } else pasang();
    });
    lingkar.forEach((el, id) => { if (!ada.has(id)) { el.remove(); lingkar.delete(id); } });   // mis. lapis tahun bertambah sel
  }

  // ---------- pembaruan: mengisi elemen yang sudah hidup ----------
  function perbarui(sebab) {
    if (!tampil || terkunci()) return;
    if (!$('rkHero')) bangun();   // tirai baru terbuka: kerangka dibangun ulang
    if (!ix) ix = R.bangunIndeks();
    const k = kini(); const r = R.susunRingkasan(skala, ix, k); const kas = R.susunKas(k); const perhatian = R.susunPerhatian().concat(perhatianPajak(k), perhatianKunci(k)); const sumber = sumberData();
    menitLama = k.getHours() * 60 + k.getMinutes(); sektorKini = r.sektor;
    const pertama = sebab === 'tampil'; const gantiSk = sebab === 'skala';
    const kunciBaru = r.umpan.length ? r.umpan[0].k : ''; const mendarat = !pertama && kunciNotaLama !== null && !!kunciBaru && kunciBaru !== kunciNotaLama; kunciNotaLama = kunciBaru;
    const naik = !pertama && !gantiSk && angkaTampil !== null ? r.angka - angkaTampil : 0;

    $('rkTanggal').textContent = R.tanggalPanjang(k); $('rkSalam').textContent = R.salam(k) + ', Owner';
    const pil = $('rkPil'); pil.textContent = sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'; pil.classList.toggle('kedip', sumber.jenis !== 'firestore');
    $('rkMode').innerHTML = IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'];
    $('rkSumber').innerHTML = sumber.jenis === 'cadangan' ? '<div class="pita-info emas">Angka dari ' + esc(sumber.keterangan) + ' — "sekarang" dianggap saat cadangan itu diunduh.</div>' : sumber.jenis !== 'firestore' ? '<div class="pita-info awas">Belum tersambung ke data toko — masuk dulu sebagai owner (layar Jual).</div>' : '';
    $('rkJudul').textContent = r.judul; $('rkSub').textContent = r.sub; $('rkBanding').textContent = r.banding;
    if (gantiSk) { sekali($('rkAngka'), 'ganti', 260); sekali($('rkKilau'), 'sapu', 1150); [$('rkJudul'), $('rkSub'), $('rkBanding'), $('rkLapis')].forEach((el) => sekali(el, 'ganti-teks', 420)); }
    gulirAngka(r.angka, pertama ? 900 : gantiSk ? 560 : 640);
    if (naik > 0) { const c = $('rkChip'); c.textContent = '+' + RP(naik); sekali(c, 'tampil', 1250); }
    if (mendarat) { terbangkanTetes(); setTimeout(() => { sekali($('rkHero'), 'mendarat', 1400); sekali($('rkKilau'), 'sapu', 1150); }, 420); }
    $('rkLapis').innerHTML = r.lapisan.map((l) => '<div data-lapis="' + esc(l.lapis) + '"><div class="label">' + esc(l.nama) + '</div><div class="angka">' + esc(l.nilai) + '</div><div class="ket">' + esc(l.ket) + '</div></div>').join('')
      + (r.lapisan.length < 3 ? '<div class="menolak">' + (r.lapisan.length === 2 ? 'Belum ada lapisan di bawah tahun.' : 'Belum ada lapisan induk maupun kakek.') + '</div>' : '');
    pasangSektor(r.sektor, pertama);
    $('rkPusatJam').textContent = p2(k.getHours()) + '.' + p2(k.getMinutes()); $('rkPusatKet').textContent = r.notaHariIni + ' NOTA'; $('rkPusatKet2').textContent = 'hari ini';
    akar.querySelectorAll('#rkSkala .seg').forEach((el) => el.classList.toggle('aktif', el.dataset.k === skala));
    const aktif = akar.querySelector('#rkSkala .seg.aktif'); if (aktif && gantiSk && aktif.scrollIntoView) aktif.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    gambarPilihan();
    const sj = r.sejakNotaMenit; $('rkSejak').textContent = sj === null ? 'belum ada nota hari ini' : sj < 1 ? 'nota terakhir baru saja' : 'nota terakhir ' + (sj < 60 ? sj + ' mnt lalu' : Math.floor(sj / 60) + ' jam ' + (sj % 60) + ' mnt lalu');
    $('rkUmpan').innerHTML = r.umpan.slice(0, skala === 'langsung' ? 8 : 4).map((u, i) => '<div class="u ' + (mendarat && i === 0 ? 'baru' : '') + '"><span class="w">' + esc(u.jam) + '</span><span style="min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">' + esc(u.isi) + '</span><span class="angka" style="font-size: 13px;">' + esc(RP(u.rp)) + '</span></div>').join('')
      || '<div class="menolak" style="padding: 8px 0;">Belum ada nota hari ini.</div>';
    $('rkKas').innerHTML = '<div class="kartu platina"><div class="label">Kas tercatat · semua kantong</div>' + (kas.adaTitik ? '<div class="angka kas" style="font-size: 20px;">' + esc(RP(kas.total)) + '</div><div class="ket" style="font-size: 11.5px;">dihitung dari titik kas ' + esc(kas.titikTanggal) + '</div>'
      : '<div class="menolak">Titik kas belum disetel di perangkat ini — setel di sistem lama (Uang). Tanpa itu saldo tidak ditebak.</div>') + '</div>'
      + '<div class="kartu platina"><div class="label">Uang hari ini</div><div class="angka kas" style="font-size: 20px;">+ ' + esc(RP(kas.masukLaci + kas.masukRek)) + '</div><div class="ket" style="font-size: 11.5px;">laci ' + esc(RP(kas.masukLaci)) + ' · rekening ' + esc(RP(kas.masukRek)) + (kas.keluar ? ' · keluar ' + esc(RP(kas.keluar)) : '') + '</div></div>';
    $('rkPerhatian').innerHTML = '<div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Perlu perhatian</div><span class="pil" style="' + (perhatian.some((x) => x.awas) ? 'color: var(--awas);' : '') + '">' + (perhatian.length ? perhatian.length + ' hal' : 'aman') + '</span></div>'
      + (perhatian.map((x, i) => '<div class="baris ' + (i === perhatian.length - 1 ? 'akhir' : '') + '"><span>' + esc(x.teks) + '</span><span class="angka ' + (x.awas ? 'awas' : '') + '" style="font-size: 14px; white-space: nowrap;">' + esc(x.nilai) + '</span></div>').join('')
        || '<div class="menolak">Tidak ada bon, utang pemasok, stok menipis, atau pesanan yang menunggu.</div>');
    detak(true);
  }

  // detak tiap detik: jam & jarum detik BERGERAK tanpa menggambar ulang; ganti menit → jendela & sel berjalan bergeser
  function detak(paksa) {
    if (!tampil || terkunci() || !$('rkJam')) return;
    const k = kini(); const hidup = !opsi.sekarang();
    $('rkJam').textContent = p2(k.getHours()) + '.' + p2(k.getMinutes()) + '.' + p2(k.getSeconds());
    detikTotal += ((k.getSeconds() - (detikTotal % 60)) + 60) % 60;   // sudut selalu MAJU — dari detik 59 ke 0 jarum tidak berputar balik
    $('rkDetik').style.transform = 'rotate(' + (detikTotal * 6) + 'deg)'; $('rkDetik').style.opacity = hidup ? '' : '0.25';
    if (pilihId && Date.now() - jamPilih > 8000) { pilihId = null; gambarPilihan(); }
    if (!paksa && k.getHours() * 60 + k.getMinutes() !== menitLama) perbarui('menit');
  }
  setInterval(() => detak(false), 1000);
  dengarkan(() => { ix = null; perbarui('data'); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) perbarui('data'); });   // kembali ke depan → angka & cincin diselaraskan

  // putaran 23d: Beranda tidak punya kolom isian — tidak ada yang ditanyakan atau dikosongkan saat ganti orang (tirai sudah mengosongkan tampilannya)
  return {
    belumDisimpan: () => false, lupakanOrang: () => {},
    gambar: () => perbarui('data'),
    tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { angkaTampil = null; kunciNotaLama = null; akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); perbarui('tampil'); } },
  };
}
