// LAYAR RINGKASAN — GAMBAR. R2 "Cincin Bersarang" (dikunci owner 13 Sep 2026); logika & angka di ringkasan-logika.js.
// BACA SAJA. Jam berdetak tiap detik tanpa menggambar ulang; layar digambar ulang saat data berubah, skala diganti,
// atau menit berganti (detik-an hanya untuk skala Langsung/Menit yang memang bergeser per menit).
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { RP } from '../inti/format.js';
import * as R from './ringkasan-logika.js';
import { sumberData, dengarkan } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_SKALA = 'miqbal_baru_skala';
const p2 = (n) => String(n).padStart(2, '0');

export function pasangLayarRingkasan(akar, opsi) {
  let skala = (() => { try { return localStorage.getItem(KUNCI_SKALA) || 'jam'; } catch (e) { return 'jam'; } })();
  if (!R.SKALA.some((s) => s[0] === skala)) skala = 'jam';
  let ix = null, kunciNotaLama = null, angkaLama = null, tampil = false, menitLama = -1;
  const kini = () => opsi.sekarang() || new Date();

  delegasi(akar, {
    skala: ({ k }) => { skala = k; try { localStorage.setItem(KUNCI_SKALA, k); } catch (e) { /* abaikan */ } gambar(true); },
    mode: () => opsi.gantiMode(),
    keJual: () => opsi.pindah('jual'),
  });

  function gambar(gantiSkala) {
    if (!tampil) return;
    if (!ix) ix = R.bangunIndeks();
    const k = kini(); const r = R.susunRingkasan(skala, ix, k); const kas = R.susunKas(k); const perhatian = R.susunPerhatian(); const sumber = sumberData();
    // nota baru mendarat: kunci nota terbaru berubah sejak gambar terakhir (bukan saat pertama kali tampil)
    const kunciBaru = r.umpan.length ? r.umpan[0].k : ''; const mendarat = kunciNotaLama !== null && kunciBaru && kunciBaru !== kunciNotaLama; kunciNotaLama = kunciBaru;
    const kel = R.kelompokAngka(r.angka); const kelLama = angkaLama === null ? kel : R.kelompokAngka(angkaLama);
    const selisih = angkaLama !== null && !gantiSkala ? r.angka - angkaLama : 0; angkaLama = r.angka;
    menitLama = k.getHours() * 60 + k.getMinutes();
    const sejak = r.sejakNotaMenit === null ? 'belum ada nota hari ini' : r.sejakNotaMenit < 1 ? 'nota terakhir baru saja' : 'nota terakhir ' + (r.sejakNotaMenit < 60 ? r.sejakNotaMenit + ' mnt lalu' : Math.floor(r.sejakNotaMenit / 60) + ' jam ' + (r.sejakNotaMenit % 60) + ' mnt lalu');
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual kepala-ringkasan">
        <div><div class="label">${R.tanggalPanjang(k)} · <span id="rkJam" style="letter-spacing: 0.1em;">${p2(k.getHours())}.${p2(k.getMinutes())}.${p2(k.getSeconds())}</span></div>
          <div class="serif" style="font-size: 22px;">${R.salam(k)}, owner</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div>
        </div>
      </header>
      ${sumber.jenis === 'cadangan' ? h`<div class="pita-info emas">Angka dari ${sumber.keterangan} — "sekarang" dianggap saat cadangan itu diunduh.</div>` : sumber.jenis !== 'firestore' ? h`<div class="pita-info awas">Belum tersambung ke data toko — masuk dulu sebagai owner (layar Jual).</div>` : ''}
      <div class="kartu hero ${mendarat ? 'mendarat' : ''}"><div class="kilau"></div>
        <div class="label" style="color: var(--hero-label);">${r.judul}</div>
        <div class="angka dagang angka-besar ${gantiSkala ? 'ganti' : ''}" style="font-size: clamp(28px, 8vw, 44px);">${kel.map((t, i) => h`<span class="klp ${!gantiSkala && kelLama[i] !== t ? 'ubah' : ''}">${t}</span>`)}</div>
        <div class="ket">${r.sub}</div>
        <div class="ket" style="font-size: 12px;">${r.banding}</div>
        <div class="chip-naik ${selisih > 0 ? 'tampil' : ''}">${selisih > 0 ? '+' + RP(selisih) : ''}</div>
        <div class="badan-hero">
          <div class="lapis">${r.lapisan.map((l) => h`<div><div class="label">${l.nama}</div><div class="angka">${l.nilai}</div><div class="ket">${l.ket}</div></div>`)}
            ${r.lapisan.length < 3 ? h`<div class="menolak">${r.lapisan.length === 2 ? 'Belum ada lapisan di bawah tahun.' : 'Belum ada lapisan induk maupun kakek.'}</div>` : ''}</div>
          <div class="cincin-wadah"><svg class="cincin" viewBox="-6 -6 212 212">
            ${r.sektor.map((s) => mentah(`<circle class="sektor ${s.kelas}" cx="100" cy="100" r="${s.r}" transform="rotate(-90 100 100)" style="stroke-width: ${s.w}px; stroke-dasharray: ${s.da}; stroke-dashoffset: ${s.do}px;"></circle>`))}
            <line class="jarum" x1="100" y1="60" x2="100" y2="4"></line>
            <text class="pusat-jam" id="rkPusatJam" x="100" y="98" text-anchor="middle">${p2(k.getHours())}.${p2(k.getMinutes())}</text>
            <text class="pusat-ket" x="100" y="112" text-anchor="middle">${r.notaHariIni} NOTA</text>
            <text class="pusat-ket" x="100" y="124" text-anchor="middle">hari ini</text>
          </svg></div>
        </div>
        <div class="pita">${R.SKALA.map(([id, nm]) => h`<div class="seg ${skala === id ? 'aktif' : ''}" data-aksi="skala" data-k="${id}">${nm}</div>`)}</div>
      </div>
      <div class="kartu" style="gap: 4px; padding: 10px 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Nota hari ini</div><div class="ket" style="font-size: 11.5px;">${sejak}</div></div>
        <div class="umpan">${r.umpan.slice(0, skala === 'langsung' ? 8 : 4).map((u, i) => h`<div class="u ${mendarat && i === 0 ? 'baru' : ''}"><span class="w">${u.jam}</span><span style="min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${u.isi}</span><span class="angka" style="font-size: 13px;">${RP(u.rp)}</span></div>`)}
          ${r.umpan.length ? '' : h`<div class="menolak" style="padding: 8px 0;">Belum ada nota hari ini.</div>`}</div>
        <div class="ket" style="text-align: right; cursor: pointer; text-decoration: underline;" data-aksi="keJual">catat nota →</div>
      </div>
      <div class="dua">
        <div class="kartu platina"><div class="label">Kas tercatat · semua kantong</div>
          ${kas.adaTitik ? h`<div class="angka kas" style="font-size: 20px;">${RP(kas.total)}</div><div class="ket" style="font-size: 11.5px;">dihitung dari titik kas ${kas.titikTanggal}</div>`
            : h`<div class="menolak">Titik kas belum disetel di perangkat ini — setel di sistem lama (Uang). Tanpa itu saldo tidak ditebak.</div>`}</div>
        <div class="kartu platina"><div class="label">Uang hari ini</div>
          <div class="angka kas" style="font-size: 20px;">+ ${RP(kas.masukLaci + kas.masukRek)}</div>
          <div class="ket" style="font-size: 11.5px;">laci ${RP(kas.masukLaci)} · rekening ${RP(kas.masukRek)}${kas.keluar ? ' · keluar ' + RP(kas.keluar) : ''}</div></div>
      </div>
      <div class="kartu" style="gap: 6px;">
        <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Perlu perhatian</div><span class="pil" style="${perhatian.some((x) => x.awas) ? 'color: var(--awas);' : ''}">${perhatian.length ? perhatian.length + ' hal' : 'aman'}</span></div>
        ${perhatian.map((x, i) => h`<div class="baris ${i === perhatian.length - 1 ? 'akhir' : ''}"><span>${x.teks}</span><span class="angka ${x.awas ? 'awas' : ''}" style="font-size: 14px; white-space: nowrap;">${x.nilai}</span></div>`)}
        ${perhatian.length ? '' : h`<div class="menolak">Tidak ada bon, utang pemasok, stok menipis, atau pesanan yang menunggu.</div>`}
      </div>
    `);
  }

  // detak: jam berjalan tanpa menggambar ulang; ganti menit → gambar ulang (jendela 60 menit & sel berjalan bergeser)
  setInterval(() => {
    if (!tampil) return;
    const k = kini(); const a = document.getElementById('rkJam'); const b = document.getElementById('rkPusatJam');
    if (a) a.textContent = p2(k.getHours()) + '.' + p2(k.getMinutes()) + '.' + p2(k.getSeconds());
    if (b) b.textContent = p2(k.getHours()) + '.' + p2(k.getMinutes());
    if (k.getHours() * 60 + k.getMinutes() !== menitLama) gambar(false);
  }, 1000);
  dengarkan(() => { ix = null; gambar(false); });

  return { gambar: () => gambar(false), tampilkan: (ya) => { tampil = !!ya; if (tampil) { angkaLama = null; gambar(true); } } };
}
