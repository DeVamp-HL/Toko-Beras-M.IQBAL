// Panel SERAH TERIMA LACI di tablet (owner 28 Nov 2026) — kartu PALING ATAS Menu tablet selama serah terima belum dikirim. Hitung buta per pecahan (tanpa angka
// "seharusnya"); kirim = persetujuan kabarToko jenis serahLaci (serah-laci-logika slSusunKirim). Sebelum terkirim, layar lain tertahan (app.js).
import { h } from '../inti/dom.js';
import { RP, tanggalPendek } from '../inti/format.js';
import * as SL from './serah-laci-logika.js';

/** Kartu serah terima. opsi = { wajib (SL_KUNCI_WAJIB yang masih berlaku) , kini }. Tidak ada serah terima = kartu tidak tampil. */
export function kartuSerahLaci(s, opsi) {
  const W = opsi && opsi.wajib; if (!W) return '';
  const d = Object.assign(SL.SL_DRAF_KOSONG(), s.sl || {}); const H = SL.slHitung(d, opsi.kini);
  return h`<div class="kartu" data-k="sl-kartu" style="gap: 8px; box-shadow: inset 0 0 0 1px var(--emas-garis);">
    <div class="label">Serah terima laci · ${tanggalPendek(W.tanggal)}</div>
    <div class="serif" style="font-size: 18px;">${W.dari || 'Penjaga sebelumnya'} → ${W.ke || 'yang jaga sekarang'}</div>
    <div class="ket" style="font-size: 11.5px;">Hitung uang di laci bersama ${W.dari || 'penjaga sebelumnya'} sebelum mulai jaga. Hitungannya dikirim ke owner; tablet bisa dipakai jual sesudah terkirim.</div>
    <div data-k="sl-pecahan">${H.pecahan.map((x) => h`<div class="th-pecah" data-k="sl-pc-${x.p}"><span>${RP(x.p)}</span><span class="step"><span data-aksi="slPecahan" data-p="${x.p}" data-arah="-1">−</span><input class="ketik-nama" type="text" inputmode="numeric" value="${x.n || ''}" placeholder="0" data-ketik="slPecahanKetik" data-p="${x.p}"><span data-aksi="slPecahan" data-p="${x.p}" data-arah="1">＋</span></span><span class="jm">${x.n ? RP(x.jumlah) : ''}</span></div>`)}
      <div class="th-pecah"><span>Koin & receh</span><input class="ketik-nama" type="text" inputmode="numeric" value="${d.receh}" placeholder="0" data-ketik="slReceh" style="width: 100px;"><span class="jm"></span></div>
      <div class="th-baris jumlah"><span>Dihitung</span><span class="n" style="font-size: 18px;" data-k="sl-jumlah">${RP(H.hitung)}</span></div></div>
    <div class="kaca-btn aktif emas" data-aksi="slKirim" data-k="sl-kirim">${s.slSibuk ? 'mengirim…' : H.tolak ? H.tolak : 'KIRIM SERAH TERIMA · ' + RP(H.hitung)}</div></div>`;
}

/** Aksi panel — digabung ke AKSI layar Menu. serah = { baca() → wajib | null, selesai() } (app.js, disimpan per perangkat). */
export function aksiSerahLaci({ set, st, tulis, akun, waktu, kini, serah }) {
  const draf = () => Object.assign(SL.SL_DRAF_KOSONG(), st().sl || {}); const ubah = (p) => set({ sl: Object.assign(draf(), p) });
  let sibuk = false;
  return {
    slPecahan: ({ p, arah }) => { const l = Object.assign({}, draf().lembar); l[p] = Math.max(0, (Number(l[p]) || 0) + Number(arah)); ubah({ lembar: l }); },
    slPecahanKetik: (v, el) => { const l = Object.assign({}, draf().lembar); l[el.dataset.p] = Math.max(0, Math.floor(Number(String(v).replace(/[^\d]/g, '')) || 0)); ubah({ lembar: l }); },
    slReceh: (v) => ubah({ receh: String(v).slice(0, 14) }),
    slKirim: async () => {
      if (sibuk) return; const W = serah && serah.baca ? serah.baca() : null;
      const r = SL.slSusunKirim(draf(), W, akun ? akun() : null, waktu(), kini ? kini() : new Date()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      sibuk = true; set({ slSibuk: true });
      try { if (await tulis(r) && serah && serah.selesai) serah.selesai(); } finally { sibuk = false; set({ slSibuk: false }); }
    },
  };
}
