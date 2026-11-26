// Panel STOK MINIMUM PER BARANG (owner 26 Nov 2026, sensus ulang 1c B127 — "Hari + kg per barang"): lembar di Stok › Gudang. Isi & aturan = stok-minimum-logika.js;
// panel ini hanya menggambar, meneruskan ketukan, dan mengirim SATU setelan (aturanToko/stokMinimum, owner saja). Bawaan semua barang = angka hari Belanja.
// Keadaan tiap baris dihitung dari angka yang SEDANG diketik (pratinjau), jadi owner melihat barang mana yang akan masuk "di bawah stok minimum" sebelum menyimpan.
import { h } from '../inti/dom.js';
import { DESIMAL } from '../inti/format.js';
import * as SMN from './stok-minimum-logika.js';
import { daftarBarang } from './stok-logika.js';

const smpPetaDraf = (draf, bawaan) => { const P = {}; Object.keys(draf || {}).forEach((k) => { const x = draf[k] || {}; const n = Number(String(x.n || '').replace(/\./g, '').replace(',', '.'));
  if (x.cara === 'hari' && isFinite(n) && n >= 0 && n <= SMN.SM_HARI_MAKS && String(x.n).trim() !== '') P[k] = { hari: Math.round(n) }; else if (x.cara === 'min' && isFinite(n) && n > 0) P[k] = { min: n }; }); return P; };

/** Lembar Stok minimum (s.smDraf = ketikan; null = setelan tersimpan). */
export function kartuStokMinimum(s) {
  const A = SMN.smAtur(); const draf = s.smDraf || SMN.smDraf(A.peta); const P = smpPetaDraf(draf, A.bawaan); const cari = String(s.smCari || '').trim().toLowerCase();
  const barang = daftarBarang().filter((b) => ((b.jenis === 'karung' && !b.wadahStok) || b.jenis === 'kemasan') && (Math.abs(b.sisa) > 0.004 || b.laju > 0 || draf[SMN.smKunci(b.jenis, b.kunci)]))
    .map((b) => { const kunci = SMN.smKunci(b.jenis, b.kunci); const C = SMN.smCek({ kunci, sisa: b.sisa, laju: b.laju }, P, A.bawaan); return { b, kunci, C, d: draf[kunci] || { cara: 'bawaan', n: '' } }; })
    .filter((x) => !cari || x.b.nama.toLowerCase().indexOf(cari) >= 0)
    .sort((x, y) => (y.C.bawah ? 1 : 0) - (x.C.bawah ? 1 : 0) || x.b.nama.localeCompare(y.b.nama));
  const nBawah = barang.filter((x) => x.C.bawah).length; const berubah = JSON.stringify(SMN.smDraf(A.peta)) !== JSON.stringify(Object.keys(draf).reduce((o, k) => { if (draf[k].cara !== 'bawaan') o[k] = draf[k]; return o; }, {}));
  const sat = (x) => (x.b.jenis === 'kemasan' ? 'bungkus' : 'kg');
  return h`<section class="stok-minimum" data-k="stok-minimum">
    <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Stok minimum per barang</div><div class="ket">Bawaan semua barang: di bawah minimum kalau cukup ≤ ${A.bawaan} hari menurut laju jual (angka "Disarankan kalau habis dalam" di Harga & Pemasok › Belanja › Atur). Per barang boleh hari lain, atau minimum jumlah. Dipakai Dasbor, Perlu perhatian & Belanja.</div></div><div class="kaca-btn" data-aksi="smTutup">tutup</div></div>
    <div class="kartu" style="gap: 6px;" data-k="sm-daftar">
      <div class="sm-kepala"><div class="label">${nBawah} dari ${barang.length} barang di bawah minimum${cari ? ' (disaring)' : ''}</div><input class="ketik-nama" id="smCari" type="text" value="${s.smCari || ''}" data-ketik="smCari" placeholder="cari nama barang"></div>
      ${barang.length ? barang.map((x, i) => h`<div class="sm-baris ${x.C.bawah ? 'awas' : ''}" data-k="sm-${x.kunci}" style="--urut: ${Math.min(i, 16)};">
        <div class="sm-nama"><b>${x.b.nama}</b><span class="ket ${x.C.bawah ? 'awas-teks' : ''}">sisa ${DESIMAL(Math.round(x.b.sisa * 10) / 10)} ${sat(x)}${x.b.laju > 0 ? ' · laku ' + DESIMAL(Math.round(x.b.laju * 10) / 10) + ' ' + sat(x) + '/hari' : ''} · ${SMN.smKata(x.C)}</span></div>
        <div class="sm-cara">${SMN.SM_CARA.map(([id, nm]) => h`<div class="seg ${x.d.cara === id ? 'aktif' : ''}" data-aksi="smCara" data-kunci="${x.kunci}" data-cara="${id}">${id === 'min' ? 'minimum ' + sat(x) : nm}</div>`)}</div>
        ${x.d.cara === 'bawaan' ? h`<div class="ket sm-isi">≤ ${A.bawaan} hari</div>` : h`<input class="ketik-nama sempit sm-isi" id="sm-n-${x.kunci}" type="text" inputmode="decimal" value="${x.d.n || ''}" data-ketik="smKetik" data-kunci="${x.kunci}" placeholder="${x.d.cara === 'hari' ? 'hari' : sat(x)}" aria-label="${x.d.cara === 'hari' ? 'Batas hari ' : 'Minimum '}${x.b.nama}">`}
      </div>`) : h`<div class="menolak">Tidak ada barang yang cocok.</div>`}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="smBatal">batal</div><div class="kaca-btn aktif emas ${berubah ? '' : 'redup'}" data-aksi="smSimpan">SIMPAN STOK MINIMUM</div></div>
      <div class="ket">${A.dariOwner ? 'Terakhir disimpan ' + A.tanggal + ' ' + A.jam + '. ' : ''}Tablet penjaga tetap memakai "habis ≤ 4 hari" (tablet tidak membaca setelan ini).</div>
    </div></section>`;
}

/** Ketukan lembar Stok minimum. */
export function aksiPanelStokMinimum({ set, st, tulis, waktu }) {
  const draf = () => Object.assign({}, st().smDraf || SMN.smDraf());
  return {
    smBuka: () => set({ lembar: 'stokMin', smDraf: null, smCari: '', kabar: '' }),
    smTutup: () => set({ lembar: null, smDraf: null }),
    smBatal: () => set({ smDraf: null }),
    smCara: ({ kunci, cara }) => { const d = draf(); d[kunci] = { cara, n: cara === 'bawaan' ? '' : (d[kunci] || {}).cara === cara ? d[kunci].n : '' }; set({ smDraf: d }); },
    smKetik: (v, el) => { const d = draf(); const k = el.dataset.kunci; d[k] = { cara: (d[k] || {}).cara || 'hari', n: String(v).slice(0, 10) }; set({ smDraf: d }); },
    smCari: (v) => set({ smCari: String(v).slice(0, 40) }),
    smSimpan: async () => { if (await tulis(SMN.susunAturStokMinimum(draf(), waktu()))) set({ smDraf: null }); },
  };
}
