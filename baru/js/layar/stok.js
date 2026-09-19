// LAYAR STOK — GAMBAR & KETUKAN. Beranda Stok S9 (dikunci owner) + tab Wadah literan. Logika & angka di stok-logika.js.
// Layar dimorf (elemen hidup terus) → batang isi, gunung wadah, dan angka bertransisi; baris masuk bergiliran saat lahir.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as S from './stok-logika.js';
import * as L from './jual-logika.js';
import { gambarWadah, gambarKarung, gambarKemasan } from './gambar.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_TAB = 'miqbal_baru_stok_tab';

export function pasangLayarStok(akar, opsi) {
  const tabAwal = (() => { try { return localStorage.getItem(KUNCI_TAB) || 'gudang'; } catch (e) { return 'gudang'; } })();
  const K = buatKeadaan({ tab: S.TAB_STOK.some((t) => t[0] === tabAwal) ? tabAwal : 'gudang', tanya: 'beli', kabar: '', kabarAwas: false, atur: false, aturPenuh: '', aturUlang: '', aturDaftar: '' });
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; const kini = () => opsi.sekarang() || new Date();
  const waktu = () => L.waktuSekarang(opsi.sekarang() || undefined);

  async function tulis(r) {
    if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    try { const x = await tulisDokumen(r.dokumen); if (x && x.gagal) return set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); set(Object.assign({}, r.patch, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  delegasi(akar, {
    tab: ({ t }) => { try { localStorage.setItem(KUNCI_TAB, t); } catch (e) { /* abaikan */ } set({ tab: t, kabar: '' }); },
    tanya: ({ id }) => set({ tanya: id }),
    mode: () => opsi.gantiMode(),
    tutupKabar: () => set({ kabar: '' }),
    isiUlang: ({ merk }, el) => { sekali(el.closest('.kartu-wadah'), 'pegas', 520); tulis(L.susunIsiUlangWadah(merk, waktu())); },
    bukaAtur: () => { const a = L.aturWadah(); set({ atur: !st().atur, aturPenuh: String(a.penuhKg).replace('.', ','), aturUlang: String(a.isiUlangKg).replace('.', ','), aturDaftar: a.daftar.join(', ') }); },
    aturPenuh: (v) => set({ aturPenuh: String(v).slice(0, 6) }), aturUlang: (v) => set({ aturUlang: String(v).slice(0, 6) }), aturDaftar: (v) => set({ aturDaftar: String(v).slice(0, 400) }),
    simpanAtur: async () => { const r = L.susunAturWadah({ penuhKg: st().aturPenuh, isiUlangKg: st().aturUlang, daftar: st().aturDaftar.split(',') }, waktu()); await tulis(r); if (!r.tolak) set({ atur: false }); },
    lama: () => set({ kabar: 'Mencatat barang masuk, adukan, dan cocokkan stok masih lewat sistem lama — menyusul di putaran Stok berikutnya.', kabarAwas: false }),
  });

  function gambar() {
    if (!tampil) return;
    const s = st(); const sumber = sumberData(); const k = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Stok</div><div class="ket">${tanggalPendek(L.waktuSekarang(k).tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'data toko' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      <div class="jalur" data-k="tab">${S.TAB_STOK.map(([id, nm]) => h`<div class="seg ${s.tab === id ? 'aktif' : ''}" data-aksi="tab" data-t="${id}">${nm}</div>`)}</div>
      ${s.tab === 'gudang' ? gambarGudang(s, k) : s.tab === 'wadah' ? gambarTabWadah(s) : s.tab === 'kapur' ? gambarKapur(k) : gambarKarantina()}
    `);
    gulirkan(akar, RP);
  }

  function gambarGudang(s, k) {
    const g = S.susunGudang(s.tanya, k); const j = g.jawab;
    return h`<section class="stok-gudang" data-k="gudang">
      <div class="tanya">${g.kartu.map((c) => h`<div class="kartu-t ${c.id === g.aktif ? 'aktif' : ''}" data-aksi="tanya" data-id="${c.id}"><div class="q">${c.q}</div>
        <div class="a ${c.awas ? 'awas' : ''}" ${c.angka !== undefined ? mentah('data-gulir="' + Math.round(c.angka) + '"') : ''}>${c.a}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="jawab-${g.aktif}">
        <div class="label">${g.judul}</div>
        ${j.baris.length ? h`<div class="daftar-jawab">${j.baris.map((b, i) => h`<div class="jawab" data-k="${g.aktif}-${b.kunci}" style="--urut: ${Math.min(i, 16)};">
          <span class="kiri"><span class="nm">${b.nama}</span><span class="w">${b.ket}</span><span class="batang"><span class="isi-batang ${b.awas ? 'awas' : ''}" style="transform: scaleX(${Math.round(Math.max(0.02, Math.min(1, b.isi)) * 1000) / 1000});"></span></span></span>
          <span class="kanan"><span class="n ${b.awas ? 'awas' : ''}">${b.n}</span><span class="w">${b.nKet}</span></span></div>`)}</div>`
          : h`<div class="menolak" style="padding: 12px 0;">${j.kosong}</div>`}
        <div class="rumus">${j.rumus}</div>
        ${j.takTeks ? h`<div class="ket" style="font-size: 11.5px;">${j.takTeks}</div>` : ''}
      </div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="lama">Barang masuk</div><div class="kaca-btn" data-aksi="lama">Adukan</div><div class="kaca-btn" data-aksi="lama">Cocokkan</div></div>
    </section>`;
  }

  function gambarTabWadah(s) {
    const w = S.susunWadah({ keranjang: opsi.keranjangJual().keranjang, antrean: opsi.keranjangJual().antrean });
    return h`<section class="stok-wadah" data-k="wadah">
      <div class="pita-info">Wadah kotak literan — gunungnya turun tiap ada literan terjual (termasuk yang masih di keranjang). ${w.perluIsi ? w.perluIsi + ' wadah minta diisi ulang. ' : ''}${w.belumDitandai ? w.belumDitandai + ' wadah belum pernah ditandai.' : ''} Ini alat ukur kapan harus isi ulang — stok beras tetap dihitung per merek.</div>
      <div class="rak-wadah">${w.daftar.map((x, i) => h`<div class="kartu kartu-wadah ${x.diketahui && x.perluIsi ? 'isi-ulang' : ''}" data-k="wadah-${x.nama}" style="--urut: ${i};">
        <div class="gambar-chip besar">${mentah(gambarWadah(x))}</div>
        <div class="nm">${x.nama}</div>
        <div class="ket">${!x.diketahui ? 'belum pernah ditandai diisi ulang' : '±' + DESIMAL(x.sisaKg) + ' kg dari ' + DESIMAL(x.penuhKg) + ' kg' + (x.lewat ? ' · terjual ' + DESIMAL(x.lewat) + ' kg LEBIH dari isinya — lupa menandai?' : '')}</div>
        ${x.diketahui ? h`<div class="ket">ditandai penuh ${tanggalPendek(x.sejakTanggal)} ${x.sejakJam}</div>` : ''}
        <div class="kaca-btn ${!x.diketahui || x.perluIsi ? 'aktif' : ''}" data-aksi="isiUlang" data-merk="${x.nama}">${x.diketahui && x.perluIsi ? 'ISI ULANG — tandai penuh' : 'Baru diisi ulang'}</div>
      </div>`)}</div>
      <div class="kartu" data-k="atur-wadah" style="gap: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline;"><div class="label">Aturan wadah ${w.atur.dariOwner ? '· diatur owner ' + tanggalPendek(w.atur.sejak) : '· bawaan'}</div><span class="ket" style="cursor: pointer; text-decoration: underline;" data-aksi="bukaAtur">${s.atur ? 'tutup' : 'ubah'}</span></div>
        <div class="ket">penuh (menggunung) ${DESIMAL(w.atur.penuhKg)} kg · minta isi ulang saat tersisa ${DESIMAL(w.atur.isiUlangKg)} kg · ${w.atur.daftar.length} wadah</div>
        ${s.atur ? h`<div class="ps-form">
          <div class="ket">Isi wadah tepat sesudah diisi ulang (kg)</div><input class="ketik-nama" id="aturPenuh" type="text" inputmode="decimal" value="${s.aturPenuh}" data-ketik="aturPenuh">
          <div class="ket">Minta isi ulang saat tersisa (kg)</div><input class="ketik-nama" id="aturUlang" type="text" inputmode="decimal" value="${s.aturUlang}" data-ketik="aturUlang">
          <div class="ket">Merek yang punya wadah kotak (pisahkan dengan koma) — yang lain dianggap diserok dari karung</div><input class="ketik-nama" id="aturDaftar" type="text" value="${s.aturDaftar}" data-ketik="aturDaftar">
          <div class="kaca-btn aktif" data-aksi="simpanAtur">SIMPAN ATURAN WADAH</div></div>` : ''}
      </div>
    </section>`;
  }

  function gambarKapur(k) {
    const p = S.susunKapur(k);
    return h`<section data-k="kapur"><div class="kartu" style="gap: 4px; padding: 10px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Papan Kapur · perubahan stok hari ini</div><div class="ket" style="font-size: 11px;">${p.banyak} catatan</div></div>
      ${p.baris.length ? p.baris.map((x, i) => h`<div class="kapur ${x.jenis}" data-k="kp-${x.k}" style="--urut: ${Math.min(i, 16)};"><span class="w">${x.jam}</span><span class="isi-kapur">${x.isi}</span><span class="n">${x.n}</span></div>`) : h`<div class="menolak" style="padding: 12px 0;">Belum ada perubahan stok hari ini.</div>`}
    </div></section>`;
  }

  function gambarKarantina() {
    const q = S.susunKarantina();
    return h`<section data-k="karantina"><div class="kartu" style="gap: 8px; padding: 12px 14px;">
      <div class="label">Karantina · barang kembali yang belum diputuskan</div>
      ${q.baris.length ? h`<div class="pita-info awas">${q.baris.length} barang · ${DESIMAL(q.totalKg)} kg menunggu keputusan (layak jual / rework / kembali ke pemasok / buang) — memutuskannya masih lewat sistem lama.</div>
        ${q.baris.map((x) => h`<div class="jawab" data-k="q-${x.k}"><span class="kiri"><span class="nm">${x.nama}</span><span class="w">${tanggalPendek(x.tanggal)} · ${x.catatan}</span></span><span class="kanan"><span class="n">${DESIMAL(x.kg)} kg</span></span></div>`)}`
        : h`<div class="menolak">Karantina kosong — tidak ada barang kembali yang menunggu diputuskan.</div>`}
    </div></section>`;
  }

  K.dengar(gambar);
  dengarkan(() => gambar());
  return { gambar, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil) gambar(); } };
}
