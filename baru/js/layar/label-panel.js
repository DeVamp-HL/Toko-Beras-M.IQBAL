// Panel CETAK LABEL (owner 26 Nov 2026, paket label & kedaluwarsa): kartu yang muncul SESUDAH adukan disimpan (label kemasan lengkap: kelas mutu, berat bersih,
// nama & alamat toko, tanggal kemas, baik dipakai sebelum, QR toko) dan SESUDAH Barang masuk disimpan (label tanggal masuk per tumpukan merek). Isi label =
// label-logika.js; panel ini hanya menggambar, meneruskan ketukan, dan mengirim ke printer perangkat ini (printer.js cetakLabel — jalur & mode kertas dari setelan
// Perangkat). Satu-satunya tulisan: kode label toko BARU (tandaKenal, pintu yang sama dengan Jual › Label & kartu, rules v12) — kode lama dipakai lagi.
import { h } from '../inti/dom.js';
import { ANGKA, tanggalPendek } from '../inti/format.js';
import { lbAtur, lbBarisKedatangan, lbIsiKemasan, lbIsiTumpukan, lbKop } from './label-logika.js';
import { TK_LABEL_MAKS, tkIsiLabel, tkJumlahLabel, tkSiapkanLabel } from './tanda-kenal-logika.js';
import * as PR from '../inti/printer.js';
import * as PK from '../inti/perangkat.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { ambilTandaKenal, ambilProduksi, ambilSemuaBatch } from '../data/toko.js';

export const LBP_MAKS = TK_LABEL_MAKS;
const lbpJumlah = (v, bawaan) => { const n = tkJumlahLabel(v === undefined || v === null || v === '' ? bawaan : v); return n; };
/** Hasil adukan satu batch (dokumen produksi bernomor batch itu, bukan pindahan ke karung utuh): [{ kunci, nama, ukuran, unit, tanggal }]. */
export function lbpHasilAdukan(batch) {
  const d = ambilProduksi().filter((p) => p && String(p.batchProduksi || p.id) === String(batch) && !p.jadiKarungUtuh && (Number(p.jumlahUnit) || 0) > 0);
  return d.map((p) => ({ kunci: kunciKemasan(p.namaProduk, p.ukuranKemasan), nama: String(p.namaProduk || ''), ukuran: Number(p.ukuranKemasan) || 0, unit: Number(p.jumlahUnit) || 0, tanggal: String(p.tanggal || '') }));
}
const chipKemasan = (x) => ({ jalur: 'kemasan', kunci: x.kunci, nama: x.nama, ukuran: String(x.ukuran).replace('.', ',') + ' kg' });
/** Peringatan tinggi stiker: label lengkap butuh ≥ 40 mm di stiker bercelah (TSPL) supaya baris kecilnya tidak terpotong. */
function peringatanTinggi() { try { const a = PR.prAtur(); return a.labelCara === 'tspl' && Number(a.labelTinggi) < 40 ? 'Stiker ' + a.labelLebar + '×' + a.labelTinggi + ' mm: baris bawah label lengkap bisa terpotong — pakai stiker setinggi ≥ 40 mm (Jual › Label & kartu › Printer tablet ini)' : ''; } catch (e) { return ''; } }

/** Kartu label kemasan untuk adukan yang baru disimpan / dibuka (s.lbN = jumlah lembar per kunci). */
export function kartuLabelAdukan(batch, s) {
  const H = lbpHasilAdukan(batch); if (!H.length) return '';
  const A = lbAtur(); const kop = lbKop(); const N = (s && s.lbN) || {}; const tinggi = peringatanTinggi();
  return h`<div class="kartu lbp-kartu" data-k="lbp-adukan-${batch}" style="gap: 6px;"><div class="label">Label kemasan · tempel di tiap kantong</div>
    ${H.map((x, i) => { const I = lbIsiKemasan({ kunci: x.kunci, nama: x.nama + ' ' + String(x.ukuran).replace('.', ',') + ' kg' }, 'MIQ:B:········', { tanggal: x.tanggal }, A, kop, '········');
      const n = N[x.kunci] !== undefined ? N[x.kunci] : String(Math.min(x.unit, LBP_MAKS));
      return h`<div class="lbp-baris" data-k="lbp-a-${i}" style="--urut: ${i};"><div><div style="font-weight: 600;">${x.nama} ${String(x.ukuran).replace('.', ',')} kg · ${ANGKA(x.unit)} kantong</div>
        <div class="k2">${I.baris.join(' · ')}</div>${I.kurang.length ? h`<div class="k2 awas-teks">Belum ada: ${I.kurang.join(', ')} — baris itu tidak dicetak</div>` : ''}</div>
        <div class="lbp-cetak"><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${n}" data-ketik="lbpN" data-kunci="${x.kunci}" aria-label="Jumlah label"><div class="kaca-btn aktif emas" data-aksi="lbpCetakAdukan" data-batch="${batch}" data-kunci="${x.kunci}">CETAK LABEL</div></div></div>`; })}
    <div class="k2">Baik dipakai sebelum = tanggal kemas + ${A.umurBulan} bulan${A.dariOwner ? '' : ' (bawaan)'}${A.kedaluwarsa ? '' : ' — tidak dicetak (Atur label)'} · kelas mutu & umur simpan diatur owner di Jual › Label & kartu › Atur label · paling banyak ${LBP_MAKS} lembar sekali cetak${tinggi ? ' · ' + tinggi : ''}</div></div>`;
}
/** Kartu label tanggal masuk untuk kedatangan yang baru disimpan (satu baris per merek; s.lbN = jumlah lembar = jumlah tumpukan). */
export function kartuLabelMasuk(id, s) {
  const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return '';
  const R = lbBarisKedatangan(b); if (!R.length) return ''; const N = (s && s.lbN) || {};
  return h`<div class="kartu lbp-kartu" data-k="lbp-masuk-${id}" style="gap: 6px;"><div class="label">Label tanggal masuk · satu per tumpukan</div>
    ${R.map((x, i) => { const I = lbIsiTumpukan(x.merk, b.tanggal, x); const n = N['m|' + x.merk] !== undefined ? N['m|' + x.merk] : '1';
      return h`<div class="lbp-baris" data-k="lbp-m-${i}" style="--urut: ${i};"><div><div style="font-weight: 600;">${x.merk}</div><div class="k2">${I.baris.join(' · ')}</div></div>
        <div class="lbp-cetak"><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${n}" data-ketik="lbpN" data-kunci="${'m|' + x.merk}" aria-label="Jumlah label"><div class="kaca-btn aktif emas" data-aksi="lbpCetakMasuk" data-id="${id}" data-merk="${x.merk}">CETAK LABEL</div></div></div>`; })}
    <div class="k2">Tempel di karung paling depan tiap tumpukan — karung yang tanggal masuknya lebih lama dikeluarkan duluan. Cetak ulang kapan saja dari Jual › Label & kartu › Buat label.</div></div>`;
}

/** Kirim satu isi label ke printer perangkat ini. Hasil kalimat untuk layar. dokumenBaru = kode label baru yang SUDAH tercatat (disebut bila cetak gagal). */
export async function lbpCetak(isi, n, dokumenBaru) {
  try {
    const r = await PR.cetakLabel(isi, n);
    return { kabar: n + ' label ' + isi.judul + ' dikirim ke printer' + (r.tanpaKabar ? ' — printer tidak mengabari hasil perintah label, lihat kertasnya' : '') + (r.peringatan ? ' · ' + r.peringatan : ''), kabarAwas: false, peringatan: !!r.peringatan };
  } catch (e) {
    const ekor = dokumenBaru ? ' — kodenya sudah tercatat, tinggal tekan Cetak label lagi' : '';
    if (PK.masihMencetak(e)) return { kabar: PK.KALIMAT_MASIH_MENCETAK + ekor, kabarAwas: true };
    if (PK.hasilTakDiketahui(e)) return { kabar: PK.KALIMAT_TAK_DIKABARI + ekor, kabarAwas: true, gagal: true };
    return { kabar: 'Label tidak tercetak: ' + (e && e.message ? e.message : e) + ekor, kabarAwas: true, gagal: true };
  }
}
/** Siapkan kode QR toko untuk kemasan (kode lama dipakai lagi; baru = dicatat dulu lewat tulisDokumen). → { kode, teksKode, baru } | { tolak }. */
export async function lbpKodeKemasan(chip, w, tulisDokumen) {
  const r = tkSiapkanLabel(ambilTandaKenal(), chip, w, Math.random); if (r.tolak) return { tolak: r.tolak };
  if (r.dokumen.length) {
    try { const hsl = await tulisDokumen(r.dokumen); if (hsl && hsl.gagal) return { tolak: 'DITOLAK, kode label tidak tercatat: ' + hsl.pesan }; }
    catch (e) { return { tolak: 'GAGAL mencatat kode label: ' + (e && e.message ? e.message : e) }; }
  }
  const I = tkIsiLabel(r.sasaran, r.kode); return { kode: r.kode, teksKode: I.teksKode, sasaran: r.sasaran, baru: r.dokumen.length > 0 };
}

/** Aksi panel untuk layar yang memasangnya. opsi = { set, st, waktu, tulisDokumen, lampu? }. */
export function aksiPanelLabel({ set, st, waktu, tulisDokumen, lampu }) {
  const nyala = (x) => { try { if (lampu) lampu(x); } catch (e) { /* lampu bukan syarat */ } };
  const adaPrinter = async () => { if (await PR.jalurCetak() === 'dialog') { set({ kabar: 'Tidak ada printer di perangkat ini — label dicetak dari tablet kasir', kabarAwas: true }); return false; } return true; };
  return {
    lbpN: (v, el) => { const N = Object.assign({}, st().lbN || {}); N[el.dataset.kunci] = String(v).replace(/[^0-9]/g, '').slice(0, 3); set({ lbN: N }); },
    lbpCetakAdukan: async ({ batch, kunci }) => {
      const x = lbpHasilAdukan(batch).find((y) => y.kunci === kunci); if (!x) return set({ kabar: 'Hasil adukan itu tidak ditemukan lagi', kabarAwas: true });
      const n = lbpJumlah((st().lbN || {})[kunci], Math.min(x.unit, LBP_MAKS)); if (!n) return set({ kabar: 'Jumlah label harus 1 sampai ' + LBP_MAKS + ' lembar', kabarAwas: true });
      if (!(await adaPrinter())) return;
      const K = await lbpKodeKemasan(chipKemasan(x), waktu(), tulisDokumen); if (K.tolak) return set({ kabar: K.tolak, kabarAwas: true });
      const isi = lbIsiKemasan({ kunci: x.kunci, nama: K.sasaran.nama }, K.kode, { tanggal: x.tanggal }, lbAtur(), lbKop(), K.teksKode);
      const r = await lbpCetak(isi, n, K.baru); if (r.peringatan) nyala('lampuKertas'); if (r.gagal) nyala('lampuGagal'); set({ kabar: r.kabar, kabarAwas: r.kabarAwas });
    },
    lbpCetakMasuk: async ({ id, merk }) => {
      const b = ambilSemuaBatch().find((y) => String(y.id) === String(id)); const x = b ? lbBarisKedatangan(b).find((y) => y.merk === merk) : null;
      if (!x) return set({ kabar: 'Baris ' + merk + ' di kedatangan itu tidak ditemukan lagi', kabarAwas: true });
      const n = lbpJumlah((st().lbN || {})['m|' + merk], 1); if (!n) return set({ kabar: 'Jumlah label harus 1 sampai ' + LBP_MAKS + ' lembar', kabarAwas: true });
      if (!(await adaPrinter())) return;
      const r = await lbpCetak(lbIsiTumpukan(merk, b.tanggal, x), n, false); if (r.peringatan) nyala('lampuKertas'); if (r.gagal) nyala('lampuGagal'); set({ kabar: r.kabar + ' · masuk ' + tanggalPendek(b.tanggal), kabarAwas: r.kabarAwas });
    },
  };
}
