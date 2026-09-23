// PANEL ISI ULANG WADAH — dipakai layar Jual (lembar literan) & layar Stok (rincian wadah). Logika & angka di jual-logika.js.
// Praktik toko (owner 13–14 Sep, dikoreksi 19 Sep): wadah diisi TAKAR demi TAKAR (serok 1,8 kg) dari karung terbuka di belakangnya,
// boleh dicampur beberapa karung; rata bibir kotak = 50 kg, menggunung sampai ±60 kg. Tombol − / + = satu takar; "CATAT" baru menulis.
// Owner 21 Sep: tiap karung di belakang wadah BERNAMA (diambil dari karung sumber di gudang) — baris takar menyebut nama karungnya,
// dan karung yang habis mengambil satu karung baru dari TUMPUKAN GUDANG nama itu (tumpukannya disebut turun dari berapa ke berapa).
import { h, mentah } from '../inti/dom.js';
import { DESIMAL, tanggalPendek } from '../inti/format.js';
import * as L from './jual-logika.js';
import { gambarWadah, gambarKarungStok } from './gambar.js';

const wpKG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
/** Draf isian satu wadah: baris campuran bawaan wadah itu, semuanya masih 0 takar. */
export function drafIsi(merk) { return { wadah: merk, baris: L.resepWadah(merk).map((x) => ({ merk: x.merk, takar: 0 })), pilihMerek: false, samakan: false, ketik: '', buka: false }; }
const drafUntuk = (st, merk) => (st.isiW && st.isiW.wadah === merk ? st.isiW : drafIsi(merk));

/** Gambar panel. s = keadaan layar (punya isiW; boleh punya keranjang/antrean supaya literan di keranjang ikut dihitung). */
export function panelIsiUlang(merk, s, keranjang, opsi) {
  const d = drafUntuk(s, merk); const lipat = !!(opsi && opsi.lipat) && !d.buka; const hit = L.hitungTakar(merk, d.baris, keranjang); const atur = L.aturWadah();
  const w = L.tinggiWadah(merk, keranjang, hit.kg); const nyata = L.tinggiWadah(merk, keranjang);
  const resep = L.resepWadah(merk); const campuran = resep.length > 1;
  const calon = d.pilihMerek ? L.calonCampur(d.baris.map((x) => x.merk)) : []; const DR = nyata.diketahui && !lipat ? L.deretanKarung() : [];
  return h`<div class="panel-wadah" data-k="panel-wadah-${merk}">
    <div class="baris-wadah"><div class="gambar-chip besar">${mentah(gambarWadah(w))}</div>
      <div><div class="ket">${!nyata.diketahui ? 'Isi wadah ini belum pernah disamakan dengan kenyataan, jadi belum bisa digambar. Tandai dulu isinya sekarang ↓'
        : 'Isi wadah ±' + wpKG(nyata.sisaNyataKg) + (hit.kg ? ' → ±' + wpKG(hit.isiBaru) : '') + ' · rata ' + DESIMAL(atur.penuhKg) + ' kg · menggunung sampai ' + DESIMAL(atur.puncakKg) + ' kg'
          + (nyata.lewat ? ' · sudah terjual ' + wpKG(nyata.lewat) + ' LEBIH dari isinya — lupa mencatat isi ulang?' : '')}</div>
        ${nyata.diketahui ? h`<div class="ket">${nyata.perluIsi ? 'SAATNYA ISI ULANG · ' : ''}isi terakhir ${tanggalPendek(nyata.isiTerakhirTanggal)} ${nyata.isiTerakhirJam}</div>` : ''}</div></div>
    ${opsi && opsi.lipat ? h`<div class="kaca-btn ${lipat && (!nyata.diketahui || nyata.perluIsi) ? 'aktif' : ''}" data-aksi="wdBuka" data-wadah="${merk}">${lipat ? (nyata.diketahui ? (nyata.perluIsi ? 'ISI ULANG WADAH — takar demi takar' : 'Isi ulang wadah (− / + takar)') : 'Tandai isi wadah sekarang') : 'tutup isi ulang'}</div>` : ''}
    ${lipat ? '' : h`${nyata.diketahui ? h`
      <div class="deretan-karung" data-k="deretan-${merk}"><div class="label" style="font-size: 9px;">Deretan karung terbuka di belakang · ketuk = +1 takar dari karung itu</div>
        <div class="deretan-isi">${DR.map((k) => { const dipakai = d.baris.filter((x) => x.merk === k.merk && (x.dari !== undefined ? String(x.dari) : L.lokasiSumber(x.merk, merk)) === k.lokasi).reduce((a, x) => a + x.takar, 0);
          return h`<div class="karung-deret ${dipakai ? 'dipakai' : ''} ${k.lokasi === merk ? 'sendiri' : ''}" data-k="dk-${k.merk}|${k.lokasi}" data-aksi="wdDariKarung" data-wadah="${merk}" data-merk="${k.merk}" data-dari="${k.lokasi}" title="${k.letak}"><div class="gambar-chip">${mentah(gambarKarungStok(k))}</div><div class="nm">${k.merk}</div><div class="ket">${k.no ? k.no + ' · ' : ''}${k.diketahui ? '±' + wpKG(k.sisaKg) : 'belum ditandai'}</div>${dipakai ? h`<div class="pil kecil">${dipakai} takar</div>` : ''}</div>`; })}${DR.length ? '' : h`<div class="ket">Belum ada karung terbuka yang ditandai — buka karung di Stok → Wadah literan.</div>`}</div></div>
      ${d.baris.map((x, i) => { const k = hit.sumber.find((y) => y.merk === x.merk && (x.dari === undefined || y.dari === String(x.dari))); const kr = k ? k.karung : L.karungBelakang(x.merk, x.dari !== undefined ? x.dari : L.lokasiSumber(x.merk, merk)); const tg = k && k.bukaKarung ? L.tumpukanGudang(x.merk) : null;
        const letak = kr.lokasi === merk ? 'karung di belakang wadah ini' : kr.lokasi ? 'karung di belakang wadah ' + kr.lokasi + (kr.yatim ? ' (dulu)' : '') : 'karung bahan campuran';
        return h`<div class="baris-takar" data-k="takar-${x.merk}-${x.dari === undefined ? 'oto' : x.dari}">
          <span class="kiri"><span class="nm">${x.merk}</span></span>
          <span class="langkah"><div class="kaca-btn" data-aksi="wdKurang" data-wadah="${merk}" data-i="${i}">−</div><span class="n">${x.takar} <span class="ket">takar</span></span><div class="kaca-btn aktif" data-aksi="wdTambah" data-wadah="${merk}" data-i="${i}">+</div></span>
          <span class="n kg">${wpKG(x.takar * atur.takarKg)}</span>
          <span class="bawah"><span class="w ${k && k.bukaKarung ? 'awas-teks' : ''}">${letak + ' · '}${kr.diketahui ? 'sisa ±' + wpKG(kr.sisaKg) + (k && k.bukaKarung ? ' — HABIS, ' + k.bukaKarung + ' karung baru diambil dari tumpukan gudang' + (tg && tg.adaBuku ? ' (' + wpKG(tg.kg) + ' → ' + wpKG(tg.kg - k.bukaKarung * tg.beratKarung) + ')' : '') : '') : 'belum ditandai dibuka — buka/samakan di Stok → Wadah literan'}</span>${d.baris.length > 1 ? h`<span class="ket buang" data-aksi="wdBuangBaris" data-wadah="${merk}" data-i="${i}">lepas</span>` : ''}</span></div>`; })}
      <div class="tombol-baris rapat">
        ${campuran ? h`<div class="kaca-btn" data-aksi="wdPutaran" data-wadah="${merk}">+ 1 putaran (${resep.map((x) => x.takar).join(' : ')})</div>` : ''}
        <div class="kaca-btn" data-aksi="wdSampai" data-wadah="${merk}" data-target="rata">sampai rata</div>
        <div class="kaca-btn" data-aksi="wdSampai" data-wadah="${merk}" data-target="puncak">sampai menggunung</div>
        ${d.baris.length < L.WADAH_MAKS_RESEP ? h`<div class="kaca-btn putus" data-aksi="wdCampur" data-wadah="${merk}">${d.pilihMerek ? 'batal campur' : '+ campur karung lain'}</div>` : ''}
      </div>
      ${d.pilihMerek ? h`<div class="tombol-baris rapat" data-k="calon-campur">${calon.length ? calon.map((m) => h`<div class="kaca-btn" data-aksi="wdPilihMerek" data-wadah="${merk}" data-merk="${m}">${m}</div>`) : h`<div class="ket">Tidak ada karung lain yang masih punya stok di gudang.</div>`}</div>` : ''}
      ${hit.takar ? h`<div class="ket ${hit.lewat ? 'awas-teks' : ''}">${hit.takar} takar × ${DESIMAL(atur.takarKg)} kg = ${wpKG(hit.kg)}${hit.banding ? ' · perbandingan ' + hit.banding : ''}${hit.lewat ? ' — MELEBIHI ' + wpKG(atur.puncakKg) + ' yang muat, kurangi takarnya' : ''}</div>` : ''}
      <div class="kaca-btn ${hit.takar && !hit.lewat ? 'aktif emas' : 'mati'}" data-aksi="wdCatat" data-wadah="${merk}">${hit.takar ? 'ISI ULANG · CATAT ' + hit.takar + ' TAKAR' : 'ISI ULANG — ketuk + tiap takar yang dituang'}</div>` : ''}
    <div class="ket tautan" data-aksi="wdSamakanBuka" data-wadah="${merk}">${d.samakan ? 'tutup' : nyata.diketahui ? 'angkanya tidak cocok dengan kotaknya? samakan' : 'tandai isi wadah sekarang'}</div>
    ${d.samakan || !nyata.diketahui ? h`<div class="tombol-baris rapat" data-k="samakan-wadah">
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="${atur.penuhKg}">rata (${DESIMAL(atur.penuhKg)} kg)</div>
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="${atur.puncakKg}">menggunung (${DESIMAL(atur.puncakKg)} kg)</div>
      <input class="ketik-nama sempit" id="wdKetik-${merk}" type="text" inputmode="decimal" placeholder="kg" value="${d.ketik}" data-ketik="wdKetik" data-wadah="${merk}">
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="ketik">pakai angka ini</div></div>` : ''}`}
  </div>`;
}

/** Penangan ketukan panel — dipasang ke delegasi layar. set/st = keadaan layar; tulis(r) = tulis dokumen lalu kabari; keranjang() = keadaan keranjang Jual. */
export function aksiPanelWadah({ set, st, tulis, keranjang, waktu, sesudahCatat }) {
  const draf = (merk) => { const d = drafUntuk(st(), merk); return { wadah: d.wadah, baris: d.baris.map((x) => Object.assign({ merk: x.merk, takar: x.takar }, x.dari !== undefined ? { dari: x.dari } : {})), pilihMerek: d.pilihMerek, samakan: d.samakan, ketik: d.ketik, buka: d.buka }; };
  const ubah = (merk, f) => { const d = draf(merk); f(d); set({ isiW: d }); };
  return {
    wdBuka: ({ wadah }) => ubah(wadah, (d) => { d.buka = !d.buka; }),
    wdTambah: ({ wadah, i }) => ubah(wadah, (d) => { d.baris[Number(i)].takar += 1; }),
    wdKurang: ({ wadah, i }) => ubah(wadah, (d) => { d.baris[Number(i)].takar = Math.max(0, d.baris[Number(i)].takar - 1); }),
    wdPutaran: ({ wadah }) => ubah(wadah, (d) => { L.resepWadah(wadah).forEach((r) => { const b = d.baris.find((x) => x.merk === r.merk); if (b) b.takar += r.takar; else if (d.baris.length < L.WADAH_MAKS_RESEP) d.baris.push({ merk: r.merk, takar: r.takar }); }); }),
    wdSampai: ({ wadah, target }) => { const a = L.aturWadah(); const d = draf(wadah); const pola = d.baris.some((x) => x.takar > 0) ? d.baris.filter((x) => x.takar > 0) : L.resepWadah(wadah);
      const r = L.takarSampai(wadah, pola, target === 'puncak' ? a.puncakKg : a.penuhKg, keranjang());
      if (!r) return set({ kabar: 'Isi wadah ' + wadah + ' belum pernah disamakan — tandai dulu isinya sekarang', kabarAwas: true });
      if (!r.some((x) => x.takar > 0)) return set({ kabar: 'Wadah ' + wadah + ' sudah ' + (target === 'puncak' ? 'menggunung penuh' : 'rata atau lebih') + ' — tidak muat satu putaran lagi', kabarAwas: false });
      d.baris = d.baris.map((x) => { const y = r.find((z) => z.merk === x.merk); return { merk: x.merk, takar: y ? y.takar : 0 }; }); r.forEach((y) => { if (!d.baris.some((x) => x.merk === y.merk)) d.baris.push(y); }); set({ isiW: d }); },
    wdCampur: ({ wadah }) => ubah(wadah, (d) => { d.pilihMerek = !d.pilihMerek; }),
    wdPilihMerek: ({ wadah, merk }) => ubah(wadah, (d) => { if (!d.baris.some((x) => x.merk === merk) && d.baris.length < L.WADAH_MAKS_RESEP) d.baris.push({ merk, takar: 1 }); d.pilihMerek = false; }),
    wdBuangBaris: ({ wadah, i }) => ubah(wadah, (d) => { if (d.baris.length > 1) d.baris.splice(Number(i), 1); }),
    wdDariKarung: ({ wadah, merk, dari }) => ubah(wadah, (d) => { d.baris = L.tambahTakarDari(d.baris, merk, dari); }),
    wdSamakanBuka: ({ wadah }) => ubah(wadah, (d) => { d.samakan = !d.samakan; }),
    wdKetik: (v, el) => { const merk = el && el.dataset.wadah; if (!merk) return; const d = draf(merk); d.ketik = String(v).slice(0, 6); set({ isiW: d }); },
    wdSamakan: async ({ wadah, kg }) => { const d = draf(wadah); if (kg === 'ketik' && !String(d.ketik || '').trim()) return set({ kabar: 'Ketik dulu isi wadahnya (kg) — kotak isiannya masih kosong', kabarAwas: true });
      const r = L.susunIsiUlangWadah(wadah, waktu(), kg === 'ketik' ? d.ketik : kg); const jadi = await tulis(r); if (!r.tolak && jadi !== false) set({ isiW: Object.assign(drafIsi(wadah), { buka: d.buka }) }); },
    wdCatat: async ({ wadah }, el) => { const d = draf(wadah); const r = L.susunTakarWadah(wadah, d.baris, waktu(), keranjang()); const berhasil = await tulis(r);
      if (!r.tolak && berhasil !== false) { set({ isiW: Object.assign(drafIsi(wadah), { buka: d.buka }) }); if (sesudahCatat) sesudahCatat(wadah, r, el); } },
  };
}
