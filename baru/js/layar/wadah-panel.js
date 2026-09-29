// PANEL ISI ULANG WADAH — dipakai layar Jual (lembar literan) & layar Stok (rincian wadah). Logika & angka di jual-logika.js + wadah-bernama-logika.js.
// Praktik toko (owner 13–14 Sep, dikoreksi 19 Sep): wadah diisi TAKAR demi TAKAR (serok 1,8 kg) dari karung terbuka di belakangnya,
// boleh dicampur beberapa karung; rata bibir kotak = 50 kg, menggunung sampai ±60 kg. Tombol − / + = satu takar; "CATAT" baru menulis.
// Owner 21 Sep: tiap karung di belakang wadah BERNAMA (diambil dari karung sumber di gudang) — baris takar menyebut nama karungnya,
// dan karung yang habis mengambil satu karung baru dari TUMPUKAN GUDANG nama itu (tumpukannya disebut turun dari berapa ke berapa).
// Putaran 39 (owner 29 Sep b · d · f): wadah yang sudah punya BUKU SENDIRI diisi lewat TIGA KETUKAN — (1) beras apa dari rak (karung yang sudah
// terbuka di belakang wadah, lalu tumpukan gudang), (2) takarannya (1 karung / ½ karung / kg lewat tuts angka), (3) ISI ULANG. Satu kiriman = buka
// karung bila perlu + takar + pindah buku (wbSusunIsiUlangTiga). Panel − / + takar lama tetap ada di bawahnya sebagai "Takaran lain". Buku merek asal
// kurang → tidak menulis diam-diam: pita dengan dua pintu — catat barang masuk dulu, atau TANDAI UNTUK DICOCOKKAN (ketukan kedua).
import { h, mentah } from '../inti/dom.js';
import { DESIMAL, tanggalPendek, hariIniIso } from '../inti/format.js';
import * as L from './jual-logika.js';
import * as WB from './wadah-bernama-logika.js';
import { tombolAkun } from './akses-layar.js';
import { gambarWadah, gambarKarungStok } from './gambar.js';

const wpKG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
const TUTS_TIGA = ['1', '2', '3', '⌫', '4', '5', '6', ',', '7', '8', '9', '0'];   // pola tuts jual.js — menulis ke draf panel (isiW.kgTiga), bukan s.ketik
/** Ketikan kg lewat tuts: paling banyak 5 angka, satu koma, dua angka di belakang koma. */
const tekanTutsKg = (ketik, t) => { const k = String(ketik || ''); if (t === '⌫') return k.slice(0, -1); if (t === ',') return k.indexOf(',') >= 0 ? k : (k || '0') + ',';
  if (!/^\d$/.test(t) || (k === '' && t === '0')) return k; if ((k + t).replace(',', '').length > 5) return k;
  const belakang = k.indexOf(',') >= 0 ? k.length - k.indexOf(',') - 1 : 0; return belakang >= 2 ? k : k + t; };
/** Draf isian satu wadah: baris campuran bawaan wadah itu, semuanya masih 0 takar; + tiga ketukan (merek asal, takaran, kg tuts) & pita tandai. */
export function drafIsi(merk) { return { wadah: merk, baris: L.resepWadah(merk).map((x) => ({ merk: x.merk, takar: 0 })), pilihMerek: false, samakan: false, ketik: '', buka: false, merkTiga: '', takaranTiga: '', kgTiga: '', tandai: null, yakinBuka: false }; }
const drafUntuk = (st, merk) => (st.isiW && st.isiW.wadah === merk ? Object.assign(drafIsi(merk), st.isiW) : drafIsi(merk));
/** Takaran tiga ketukan dari draf → { jenis, kg? } untuk wbSusunIsiUlangTiga. */
const takaranDraf = (d) => (d.takaranTiga === 'karung' ? { jenis: 'karung' } : d.takaranTiga === 'setengah' ? { jenis: 'setengah' } : { jenis: 'kg', kg: d.kgTiga });

/** Blok ISI ULANG TIGA KETUKAN (wadah aktif). */
function blokTiga(merk, d, nyata, atur, tb) {
  const KB = WB.wbKarungBelakangWadah(merk).filter((k) => k.bukuKg > 0.004); const ada = {}; KB.forEach((k) => { ada[k.merk] = 1; });
  const gudang = L.calonKarung().filter((t) => !ada[t.merk]); const KW = WB.wbKarungWadah(merk);
  const M = d.merkTiga; const berat = M ? L.beratKarungBuka(M) : 0;
  const kg = !M ? 0 : d.takaranTiga === 'karung' ? berat : d.takaranTiga === 'setengah' ? Math.round(berat / 2 * 100) / 100 : d.takaranTiga === 'kg' ? L.angkaKetik(d.kgTiga) : 0;
  const isiBaru = kg > 0 ? Math.round((nyata.sisaNyataKg + kg) * 100) / 100 : 0; const lewat = isiBaru > atur.puncakKg + 0.0001;
  const takaranTeks = d.takaranTiga === 'karung' ? '1 karung' : d.takaranTiga === 'setengah' ? '½ karung' : kg > 0 ? wpKG(kg) : 'kg';
  const siap = !!(M && d.takaranTiga && kg > 0 && !lewat);
  const KBk = KB.find((k) => k.merk === M); const TG = M ? L.tumpukanGudang(M) : null;
  const butuhBuka = kg > 0 ? Math.max(0, Math.round((kg - (KBk ? KBk.bukuKg : 0)) * 100) / 100) : 0; const nBuka = butuhBuka > 0.004 ? Math.ceil((butuhBuka - 0.0001) / berat) : 0;
  // putaran 39c (owner 30 Sep): karung di belakang habis / kosong → PERINGATAN + dua ketukan sebelum karung baru dibuka dari tumpukan gudang; beras berganti merek disebut
  const slot = L.karungUntukWadah(merk); const berganti = !!(M && !KBk && slot.terakhirMerk && slot.terakhirMerk !== M);
  const slotAsal = slot.dariCatatan ? WB.wbMerkAsal(slot.merk) : '';   // merek asal karung yang SEDANG berdiri di belakang wadah ini ('' bila slot kosong)
  const awasBuka = !nBuka ? '' : (KBk ? 'Karung ' + M + ' di belakang wadah ' + merk + ' tinggal ±' + wpKG(KBk.bukuKg) + ', kurang ' + wpKG(butuhBuka)
    : slot.kosong ? 'Tidak ada karung di belakang wadah ' + merk + ' (' + slot.alasanKosong + ')' : slotAsal && slotAsal !== M ? 'Tidak ada karung ' + M + ' di belakang wadah ' + merk + ' (yang berdiri di situ: ' + slotAsal + ')' : slot.dariCatatan ? 'Karung ' + M + ' di belakang wadah ' + merk + ' habis' : 'Belum ada karung di belakang wadah ' + merk) + ' — ' + nBuka + ' karung baru diambil dari tumpukan gudang'
    + (TG && TG.adaBuku ? ' (' + wpKG(TG.kg) + ' → ' + wpKG(TG.kg - nBuka * berat) + (TG.kg - nBuka * berat < -0.004 ? ', KURANG — nanti ditanya' : '') + ')' : '') + (berganti ? ' · beras di belakang ' + merk + ' berganti: ' + slot.terakhirMerk + ' → ' + M : '') + '. Ketuk ISI ULANG sekali lagi untuk membuka & mengisi.';
  const pratinjau = !kg ? '' : lewat ? 'Kalau dituang ' + wpKG(kg) + ' wadah jadi ±' + wpKG(isiBaru) + ' — MELEBIHI ' + wpKG(atur.puncakKg) + ' yang muat; paling banyak ±' + wpKG(Math.max(0, atur.puncakKg - nyata.sisaNyataKg)) + ' (pilih takaran kg)'
    : '→ isi wadah jadi ±' + wpKG(isiBaru) + (KBk ? ' · dari karung ' + M + ' di belakang (sisa ±' + wpKG(KBk.bukuKg) + ')' : '')
      + (nBuka ? ' · ' + nBuka + ' karung ' + M + ' dibuka dari tumpukan gudang' + (TG && TG.adaBuku ? ' (' + wpKG(TG.kg) + ' → ' + wpKG(TG.kg - nBuka * berat) + (TG.kg - nBuka * berat < -0.004 ? ', KURANG — nanti ditanya' : '') + ')' : '') : '');
  return h`<div class="isi-tiga" data-k="isi-tiga-${merk}">
    <div class="label">1 · Beras apa yang dituang</div>
    <div class="rak-merek" data-k="rak-merek-${merk}">
      ${KB.map((k) => h`<div class="kaca-btn merek ${M === k.merk ? 'aktif' : ''}" data-k="mt-kb-${k.merk}" data-aksi="wdMerkTiga" data-wadah="${merk}" data-merk="${k.merk}"><span>${k.merk}</span><span class="ket">karung di belakang · sisa ±${wpKG(k.bukuKg)}</span></div>`)}
      ${gudang.map((t) => h`<div class="kaca-btn merek ${M === t.merk ? 'aktif' : ''}" data-k="mt-gd-${t.merk}" data-aksi="wdMerkTiga" data-wadah="${merk}" data-merk="${t.merk}"><span>${t.merk}</span><span class="ket">tumpukan gudang ${wpKG(t.kg)}${t.karung ? ' · ' + t.karung + ' karung' : ''}</span></div>`)}
      ${KW.bukuKg > 0.004 ? h`<div class="kaca-btn merek putus" data-k="mt-kw-${merk}" data-aksi="wdKeKarungWadah" data-wadah="${merk}"><span>Karung wadah ${merk}</span><span class="ket">sisihan ±${wpKG(KW.bukuKg)} · tuang balik lewat Stok › Wadah literan</span></div>` : ''}
      ${!KB.length && !gudang.length ? h`<div class="ket">Tidak ada karung yang bisa dituang — tumpukan gudang kosong di buku. Catat barang masuknya dulu.</div>` : ''}
    </div>
    ${M ? h`<div class="label">2 · Takarannya</div>
      <div class="tombol-baris rapat" data-k="takaran-${merk}">${WB.WB_TAKARAN.map(([id, nm]) => h`<div class="kaca-btn ${d.takaranTiga === id ? 'aktif' : ''}" data-aksi="wdTakaranTiga" data-wadah="${merk}" data-t="${id}">${nm}${id === 'karung' ? ' (' + wpKG(berat) + ')' : id === 'setengah' ? ' (' + wpKG(berat / 2) + ')' : ''}</div>`)}</div>
      ${d.takaranTiga === 'kg' ? h`<div class="angka" data-k="angka-tiga-${merk}">${d.kgTiga || '0'} <span class="ket">kg</span></div>
        <div class="tuts" data-k="tuts-tiga-${merk}">${TUTS_TIGA.map((k) => h`<div class="k ${/^\d$/.test(k) ? '' : 'f'}" data-aksi="wdTutsTiga" data-wadah="${merk}" data-t="${k}">${k}</div>`)}</div>` : ''}
      ${pratinjau ? h`<div class="ket ${lewat ? 'awas-teks' : ''}" data-k="pratinjau-tiga-${merk}">${pratinjau}</div>` : ''}
      ${siap && nBuka ? h`<div class="pita-info ${d.yakinBuka ? 'awas' : 'emas'}" data-k="awas-buka-${merk}">${awasBuka}</div>` : ''}` : ''}
    ${M && d.takaranTiga ? (tb.boleh ? h`<div class="kaca-btn ${siap ? (nBuka && d.yakinBuka ? 'awas' : 'aktif emas') : 'mati'}" data-k="tombol-tiga-${merk}" data-aksi="wdIsiTiga" data-wadah="${merk}">${siap ? (nBuka ? (d.yakinBuka ? 'YAKIN — buka ' + nBuka + ' karung ' + M + ' dari tumpukan & ISI ULANG' : 'ISI ULANG · ' + takaranTeks + ' ' + M + ' — buka ' + nBuka + ' karung dari tumpukan?') : 'ISI ULANG · ' + takaranTeks + ' ' + M) : d.takaranTiga === 'kg' && !(kg > 0) ? 'ISI ULANG — ketik dulu berapa kg' : 'ISI ULANG — kurangi takarannya'}</div>`
      : h`<div class="kaca-btn mati" data-k="tombol-tiga-${merk}" data-aksi="tombolMati" data-kal="${tb.kalimat}">ISI ULANG · ${takaranTeks} ${M}</div>`) : ''}
  </div>`;
}

/** Gambar panel. s = keadaan layar (punya isiW; boleh punya keranjang/antrean supaya literan di keranjang ikut dihitung). opsi: { lipat?, akun? } */
export function panelIsiUlang(merk, s, keranjang, opsi) {
  const d = drafUntuk(s, merk); const lipat = !!(opsi && opsi.lipat) && !d.buka; const hit = L.hitungTakar(merk, d.baris, keranjang); const atur = L.aturWadah();
  const w = L.tinggiWadah(merk, keranjang, hit.kg); const nyata = L.tinggiWadah(merk, keranjang);
  const resep = L.resepWadah(merk); const campuran = resep.length > 1;
  const calon = d.pilihMerek ? L.calonCampur(d.baris.map((x) => x.merk)) : []; const DR = nyata.diketahui && !lipat ? L.deretanKarung() : [];
  // putaran 39: wadah AKTIF = satu buku — isi wadah = buku (satu angka), komposisi & jam/siapa turunan isi ulang, selisih catatan karung belakang vs buku disebut
  const aktif = WB.wbAktif(merk); const KT = aktif ? WB.wbKomposisiTurunan(merk, keranjang) : null; const SEL = aktif ? WB.wbSelisihWadah(merk, keranjang) : null;
  const hari = hariIniIso((keranjang && keranjang.sekarang) || new Date()); const tb = tombolAkun(opsi && opsi.akun ? opsi.akun : null, 'isiUlang');
  const pitaTandai = d.tandai ? h`<div class="pita-info emas pita-tandai" data-k="pita-tandai-${merk}"><div>${d.tandai.kalimat}</div>
      <div class="tombol-baris rapat"><div class="kaca-btn" data-aksi="wdKeStok" data-wadah="${merk}" data-merk="${d.tandai.merk}">Catat barang masuk dulu</div><div class="kaca-btn awas" data-aksi="${d.tandai.jalur === 'tiga' ? 'wdIsiTiga' : 'wdCatat'}" data-wadah="${merk}" data-tandai="1">TANDAI UNTUK DICOCOKKAN</div></div>
      <div class="ket tautan" data-aksi="wdTandaiBatal" data-wadah="${merk}">tidak jadi</div></div>` : '';
  return h`<div class="panel-wadah" data-k="panel-wadah-${merk}">
    <div class="baris-wadah"><div class="gambar-chip besar">${mentah(gambarWadah(w))}</div>
      <div><div class="ket">${!nyata.diketahui ? 'Isi wadah ini belum pernah disamakan dengan kenyataan, jadi belum bisa digambar. Tandai dulu isinya sekarang ↓'
        : (aktif ? 'Isi wadah = buku ±' : 'Isi wadah ±') + wpKG(nyata.sisaNyataKg) + (hit.kg ? ' → ±' + wpKG(hit.isiBaru) : '') + ' · rata ' + DESIMAL(atur.penuhKg) + ' kg · menggunung sampai ' + DESIMAL(atur.puncakKg) + ' kg'
          + (nyata.lewat ? ' · sudah terjual ' + wpKG(nyata.lewat) + ' LEBIH dari isinya — lupa mencatat isi ulang?' : '')}</div>
        ${aktif ? h`<div class="ket" data-k="komposisi-${merk}">${nyata.perluIsi ? 'SAATNYA ISI ULANG · ' : ''}${KT.teks}${KT.terakhir && KT.terakhir.tanggal && KT.terakhir.tanggal !== hari ? ' (' + tanggalPendek(KT.terakhir.tanggal) + ')' : ''}</div>${SEL.ada ? h`<div class="ket awas-teks" data-k="selisih-${merk}">${SEL.teks}</div>` : ''}`
          : h`${nyata.diketahui ? h`<div class="ket">${nyata.perluIsi ? 'SAATNYA ISI ULANG · ' : ''}isi terakhir ${tanggalPendek(nyata.isiTerakhirTanggal)} ${nyata.isiTerakhirJam}</div>` : ''}<div class="ket" data-k="belum-aktif-${merk}">Buku wadah belum aktif — aktifkan di Stok › Wadah literan</div>`}</div></div>
    ${opsi && opsi.lipat ? h`<div class="kaca-btn ${lipat && (!nyata.diketahui || nyata.perluIsi) ? 'aktif' : ''}" data-aksi="wdBuka" data-wadah="${merk}">${lipat ? (nyata.diketahui ? (aktif ? (nyata.perluIsi ? 'ISI ULANG WADAH — pilih beras & takarannya' : 'Isi ulang wadah (tiga ketukan)') : (nyata.perluIsi ? 'ISI ULANG WADAH — takar demi takar' : 'Isi ulang wadah (− / + takar)')) : 'Tandai isi wadah sekarang') : 'tutup isi ulang'}</div>` : ''}
    ${lipat ? '' : h`${pitaTandai}${aktif ? blokTiga(merk, d, nyata, atur, tb) : ''}${nyata.diketahui ? h`
      ${aktif ? h`<div class="label" data-k="takaran-lain-${merk}">Takaran lain (− / + takar)</div>` : ''}
      <div class="deretan-karung" data-k="deretan-${merk}"><div class="label" style="font-size: 9px;">Deretan karung terbuka di belakang · ketuk = +1 takar dari karung itu</div>
        <div class="deretan-isi">${DR.map((k) => { const dipakai = d.baris.filter((x) => x.merk === k.merk && (x.dari !== undefined ? String(x.dari) : L.lokasiSumber(x.merk, merk)) === k.lokasi).reduce((a, x) => a + x.takar, 0);
          return h`<div class="karung-deret ${dipakai ? 'dipakai' : ''} ${k.lokasi === merk ? 'sendiri' : ''}" data-k="dk-${k.merk}|${k.lokasi}" data-aksi="wdDariKarung" data-wadah="${merk}" data-merk="${k.merk}" data-dari="${k.lokasi}" title="${k.letak}"><div class="gambar-chip">${mentah(gambarKarungStok(k))}</div><div class="nm">${k.merkAsal || k.merk}</div><div class="ket">${k.no ? k.no + ' · ' : ''}${k.diketahui ? '±' + wpKG(k.sisaKg) : 'belum ditandai'}</div>${dipakai ? h`<div class="pil kecil">${dipakai} takar</div>` : ''}</div>`; })}${DR.length ? '' : h`<div class="ket">Belum ada karung terbuka yang ditandai — buka karung di Stok → Wadah literan.</div>`}</div></div>
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
      ${(() => { const nb = hit.sumber.reduce((a, x) => a + (x.bukaKarung || 0), 0); return tb.boleh ? h`${hit.takar && !hit.lewat && nb ? h`<div class="pita-info ${d.yakinBuka ? 'awas' : 'emas'}" data-k="awas-buka-catat-${merk}">Karung di belakang habis / kurang — ${nb} karung baru diambil dari tumpukan gudang (${hit.sumber.filter((x) => x.bukaKarung).map((x) => x.bukaKarung + ' ' + (x.merkAsal || x.merk)).join(', ')}). Ketuk CATAT sekali lagi untuk membuka & mencatat.</div>` : ''}<div class="kaca-btn ${hit.takar && !hit.lewat ? (nb && d.yakinBuka ? 'awas' : 'aktif emas') : 'mati'}" data-aksi="wdCatat" data-wadah="${merk}">${hit.takar ? (nb ? (d.yakinBuka ? 'YAKIN — buka ' + nb + ' karung dari tumpukan & CATAT ' + hit.takar + ' TAKAR' : 'ISI ULANG · CATAT ' + hit.takar + ' TAKAR — buka ' + nb + ' karung dari tumpukan?') : 'ISI ULANG · CATAT ' + hit.takar + ' TAKAR') : 'ISI ULANG — ketuk + tiap takar yang dituang'}</div>`
        : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${tb.kalimat}">${hit.takar ? 'ISI ULANG · CATAT ' + hit.takar + ' TAKAR' : 'ISI ULANG — ketuk + tiap takar yang dituang'}</div>`; })()}` : ''}`}
    <div class="ket tautan" data-aksi="wdSamakanBuka" data-wadah="${merk}">${d.samakan ? 'tutup' : nyata.diketahui ? 'angkanya tidak cocok dengan kotaknya? samakan' : 'tandai isi wadah sekarang'}</div>
    ${d.samakan || !nyata.diketahui ? h`<div class="tombol-baris rapat" data-k="samakan-wadah">
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="${atur.penuhKg}">rata (${DESIMAL(atur.penuhKg)} kg)</div>
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="${atur.puncakKg}">menggunung (${DESIMAL(atur.puncakKg)} kg)</div>
      <input class="ketik-nama sempit" id="wdKetik-${merk}" type="text" inputmode="decimal" placeholder="kg" value="${d.ketik}" data-ketik="wdKetik" data-wadah="${merk}">
      <div class="kaca-btn" data-aksi="wdSamakan" data-wadah="${merk}" data-kg="ketik">pakai angka ini</div></div>` : ''}
  </div>`;
}

/**
 * Penangan ketukan panel — dipasang ke delegasi layar. set/st = keadaan layar; tulis(r) = tulis dokumen lalu kabari (false bila gagal); keranjang() = keadaan
 * keranjang Jual; bukaStok(lembar, tab, isi) = pintu ke layar Stok bila layar ini punya (Jual); tanpa itu, kabar yang menyebut jalannya.
 */
export function aksiPanelWadah({ set, st, tulis, keranjang, waktu, sesudahCatat, bukaStok }) {
  const draf = (merk) => { const d = drafUntuk(st(), merk); return Object.assign({}, d, { baris: d.baris.map((x) => Object.assign({ merk: x.merk, takar: x.takar }, x.dari !== undefined ? { dari: x.dari } : {})), tandai: d.tandai ? Object.assign({}, d.tandai) : null }); };
  const ubah = (merk, f) => { const d = draf(merk); f(d); set({ isiW: d }); };
  // putaran 39 (owner d): buku merek asal kurang → ketukan pertama menyimpan daftarnya ke draf & menggambar pita (kalimat r.tolak + dua tombol); ketukan kedua menulis
  const tandaiDulu = (merk, r, jalur) => { const d = draf(merk); d.tandai = { jalur, kalimat: r.tolak, merk: String(((r.perluTandai || [])[0] || {}).merk || ''), daftar: r.perluTandai }; set({ isiW: d, kabar: r.tolak, kabarAwas: true }); };
  const selesai = (merk, d, r, el) => { set({ isiW: Object.assign(drafIsi(merk), { buka: d.buka }) }); if (sesudahCatat) sesudahCatat(merk, r, el); };
  return {
    tombolMati: ({ kal }) => set({ kabar: kal, kabarAwas: true }),   // tombol yang tidak boleh untuk akun ini MATI dengan kalimat sebabnya
    wdBuka: ({ wadah }) => ubah(wadah, (d) => { d.buka = !d.buka; }),
    wdTambah: ({ wadah, i }) => ubah(wadah, (d) => { d.yakinBuka = false; d.baris[Number(i)].takar += 1; }),
    wdKurang: ({ wadah, i }) => ubah(wadah, (d) => { d.yakinBuka = false; d.baris[Number(i)].takar = Math.max(0, d.baris[Number(i)].takar - 1); }),
    wdPutaran: ({ wadah }) => ubah(wadah, (d) => { d.yakinBuka = false; L.resepWadah(wadah).forEach((r) => { const b = d.baris.find((x) => x.merk === r.merk); if (b) b.takar += r.takar; else if (d.baris.length < L.WADAH_MAKS_RESEP) d.baris.push({ merk: r.merk, takar: r.takar }); }); }),
    wdSampai: ({ wadah, target }) => { const a = L.aturWadah(); const d = draf(wadah); d.yakinBuka = false; const pola = d.baris.some((x) => x.takar > 0) ? d.baris.filter((x) => x.takar > 0) : L.resepWadah(wadah);
      const r = L.takarSampai(wadah, pola, target === 'puncak' ? a.puncakKg : a.penuhKg, keranjang());
      if (!r) return set({ kabar: 'Isi wadah ' + wadah + ' belum pernah disamakan — tandai dulu isinya sekarang', kabarAwas: true });
      if (!r.some((x) => x.takar > 0)) return set({ kabar: 'Wadah ' + wadah + ' sudah ' + (target === 'puncak' ? 'menggunung penuh' : 'rata atau lebih') + ' — tidak muat satu putaran lagi', kabarAwas: false });
      d.baris = d.baris.map((x) => { const y = r.find((z) => z.merk === x.merk); return { merk: x.merk, takar: y ? y.takar : 0 }; }); r.forEach((y) => { if (!d.baris.some((x) => x.merk === y.merk)) d.baris.push(y); }); set({ isiW: d }); },
    wdCampur: ({ wadah }) => ubah(wadah, (d) => { d.yakinBuka = false; d.pilihMerek = !d.pilihMerek; }),
    wdPilihMerek: ({ wadah, merk }) => ubah(wadah, (d) => { d.yakinBuka = false; if (!d.baris.some((x) => x.merk === merk) && d.baris.length < L.WADAH_MAKS_RESEP) d.baris.push({ merk, takar: 1 }); d.pilihMerek = false; }),
    wdBuangBaris: ({ wadah, i }) => ubah(wadah, (d) => { if (d.baris.length > 1) d.baris.splice(Number(i), 1); }),
    wdDariKarung: ({ wadah, merk, dari }) => ubah(wadah, (d) => { d.yakinBuka = false; d.baris = L.tambahTakarDari(d.baris, merk, dari); }),
    wdSamakanBuka: ({ wadah }) => ubah(wadah, (d) => { d.samakan = !d.samakan; }),
    wdKetik: (v, el) => { const merk = el && el.dataset.wadah; if (!merk) return; const d = draf(merk); d.ketik = String(v).slice(0, 6); set({ isiW: d }); },
    wdSamakan: async ({ wadah, kg }) => { const d = draf(wadah); if (kg === 'ketik' && !String(d.ketik || '').trim()) return set({ kabar: 'Ketik dulu isi wadahnya (kg) — kotak isiannya masih kosong', kabarAwas: true });
      const r = L.susunIsiUlangWadah(wadah, waktu(), kg === 'ketik' ? d.ketik : kg); const jadi = await tulis(r); if (!r.tolak && jadi !== false) set({ isiW: Object.assign(drafIsi(wadah), { buka: d.buka }) }); },
    // ---- putaran 39: TIGA KETUKAN — merek asal → takaran → ISI ULANG (satu kiriman: buka karung bila perlu + takar + pindah buku)
    wdMerkTiga: ({ wadah, merk }) => ubah(wadah, (d) => { const sama = d.merkTiga === merk; d.merkTiga = sama ? '' : String(merk || ''); d.takaranTiga = ''; d.kgTiga = ''; d.tandai = null; d.yakinBuka = false; }),
    wdTakaranTiga: ({ wadah, t }) => ubah(wadah, (d) => { d.takaranTiga = String(t || ''); if (d.takaranTiga !== 'kg') d.kgTiga = ''; d.tandai = null; d.yakinBuka = false; }),
    wdTutsTiga: ({ wadah, t }) => ubah(wadah, (d) => { d.kgTiga = tekanTutsKg(d.kgTiga, t); d.tandai = null; d.yakinBuka = false; }),
    wdIsiTiga: async ({ wadah, tandai }, el) => { const d = draf(wadah);
      if (!d.merkTiga) return set({ kabar: 'Pilih dulu beras apa yang dituang', kabarAwas: true });
      if (!d.takaranTiga) return set({ kabar: 'Pilih takarannya: 1 karung, ½ karung, atau kg', kabarAwas: true });
      const r = WB.wbSusunIsiUlangTiga(wadah, d.merkTiga, takaranDraf(d), waktu(), keranjang(), tandai === '1' ? { tandai: true } : {});
      if (r.perluTandai) return tandaiDulu(wadah, r, 'tiga');
      // putaran 39c: karung baru dari tumpukan tidak dibuka diam-diam — ketukan pertama cuma memperingatkan, ketukan kedua (yakinBuka) yang menulis
      if (!r.tolak && r.hitung && r.hitung.dibuka > 0 && !d.yakinBuka) { ubah(wadah, (x) => { x.yakinBuka = true; }); return set({ kabar: 'Karung ' + d.merkTiga + ' di belakang wadah ' + wadah + ' habis / kurang — ' + r.hitung.dibuka + ' karung baru akan dibuka dari tumpukan gudang. Ketuk ISI ULANG sekali lagi kalau memang begitu.', kabarAwas: true }); }
      const berhasil = await tulis(r); if (!r.tolak && berhasil !== false) selesai(wadah, d, r, el); },
    wdTandaiBatal: ({ wadah }) => { ubah(wadah, (d) => { d.tandai = null; }); set({ kabar: '' }); },
    wdKeStok: ({ wadah, merk }) => { if (bukaStok) return bukaStok('masuk', undefined, merk ? { merk } : undefined);
      set({ kabar: 'Catat barang masuknya di Stok › Barang masuk' + (merk ? ' untuk ' + merk : '') + ', lalu ulangi isi ulang wadah ' + wadah, kabarAwas: false }); },
    wdKeKarungWadah: ({ wadah }) => { set({ kabar: 'Karung wadah ' + wadah + ' dituang balik lewat Stok › Wadah literan › rincian wadah ' + wadah + ' (tombol "tuang balik")', kabarAwas: false }); if (bukaStok) bukaStok(null, 'wadah'); },
    wdCatat: async ({ wadah, tandai }, el) => { const d = draf(wadah); const r = L.susunTakarWadah(wadah, d.baris, waktu(), keranjang(), tandai === '1' ? { tandai: true } : {});
      if (r.perluTandai) return tandaiDulu(wadah, r, 'catat');
      const nb = !r.tolak && r.hitung ? r.hitung.sumber.reduce((a, x) => a + (x.bukaKarung || 0), 0) : 0;   // putaran 39c: sama seperti tiga ketukan — karung baru dari tumpukan minta ketukan kedua
      if (nb && !d.yakinBuka) { ubah(wadah, (x) => { x.yakinBuka = true; }); return set({ kabar: 'Karung di belakang wadah ' + wadah + ' habis / kurang — ' + nb + ' karung baru akan dibuka dari tumpukan gudang. Ketuk CATAT sekali lagi kalau memang begitu.', kabarAwas: true }); }
      const berhasil = await tulis(r); if (!r.tolak && berhasil !== false) selesai(wadah, d, r, el); },
  };
}
