// Panel UANG KELUAR & PESAN UNTUK OWNER di tablet (owner 21 Nov 2026: kartu paling atas Menu akun tablet). Logika & bentuk dokumen di titipan-logika.js;
// panel ini hanya menggambar, meneruskan ketukan, dan mencetak slip. Yang ditulis HANYA titipan / pesan berstatus "menunggu" — dokumen uangnya ditulis
// owner saat menyetujui.
import { h } from '../inti/dom.js';
import { RP, tanggalPendek } from '../inti/format.js';
import * as TP from './titipan-logika.js';
import * as ST from './struk-logika.js';
import * as PR from '../inti/printer.js';
import { asliAda, printerSibuk, masihMencetak, hasilTakDiketahui, KALIMAT_MASIH_MENCETAK, KALIMAT_TAK_DIKABARI } from '../inti/perangkat.js';
import { hakAkun } from './akses-layar.js';
import { calonPemasok } from './stok-catat-logika.js';   // owner 22 Nov 2026: bayar bon pemasok lewat supir — nama pemasok yang pernah dipakai

export const TP_DRAF_KOSONG = () => ({ tab: 'uang', jenis: 'toko', nominal: '', teks: '', nama: '', pemasok: '', pesan: '' });
const kelasStatus = (st) => (st === 'disetujui' || st === 'dibaca' ? 'lunas' : st === 'ditolak' ? 'awas' : 'tunggu');

/** Kartu panel. s.tp = draf (TP_DRAF_KOSONG); opsi = { akun, orang: [nama orang di tablet], kiniIso }. */
export function kartuTitipan(s, opsi) {
  const o = opsi || {}; const a = o.akun; const d = s.tp || TP_DRAF_KOSONG(); const hak = hakAkun(a, 'uangKeluar');
  const saya = TP.tpMilikSaya(a, o.kiniIso || '', 7); const tunggu = saya.filter((b) => b.status === 'menunggu' && !b.pesan);
  const n = TP.tpAngka(d.nominal); const namaPilih = (o.orang || []).filter((x, i, A) => x && A.indexOf(x) === i);
  const formUang = hak === 'tidak'
    ? h`<div class="kaca-btn mati" data-aksi="tpMati" data-k="tp-mati">Catat uang keluar · tidak termasuk hak ${a ? a.nama : 'akun ini'}</div>`
    : h`<div class="tombol-baris rapat" data-k="tp-jenis">${TP.TP_JENIS.map(([j, nm]) => h`<div class="kaca-btn kecil ${d.jenis === j ? 'aktif' : ''}" data-aksi="tpJenis" data-j="${j}">${nm}</div>`)}</div>
      <div style="display: flex; gap: 6px;"><input class="ketik-nama" type="text" inputmode="numeric" placeholder="nominal (Rp)" value="${d.nominal}" data-ketik="tpKetik" data-kolom="nominal" style="max-width: 160px;">
        <input class="ketik-nama" type="text" placeholder="${d.jenis === 'kasbon' ? 'keperluan (boleh kosong)' : d.jenis === 'karyawan' ? 'mis. makan siang, rokok, kopi' : d.jenis === 'bayarBon' ? 'keterangan (boleh kosong), mis. bon lama' : 'mis. kantong 5 kg, bensin, kuli'}" value="${d.teks}" data-ketik="tpKetik" data-kolom="teks"></div>
      ${d.jenis === 'bayarBon' ? h`<input class="ketik-nama" type="text" placeholder="nama pemasok" value="${d.pemasok}" data-ketik="tpKetik" data-kolom="pemasok" maxlength="60">
        <div class="tombol-baris rapat" data-k="tp-pemasok">${calonPemasok().slice(0, 6).map((p) => h`<div class="kaca-btn kecil ${d.pemasok === p ? 'aktif' : ''}" data-aksi="tpPemasok" data-p="${p}">${p}</div>`)}</div>
        <div class="ket" style="font-size: 11px;">Uang yang dibawa supir untuk bon pemasok. Owner yang memilih bon mana yang dibayar saat menyetujui.</div>` : ''}
      ${d.jenis === 'kasbon' || d.jenis === 'karyawan' ? h`<div class="tombol-baris rapat" data-k="tp-nama">${namaPilih.map((nm) => h`<div class="kaca-btn kecil ${d.nama === nm ? 'aktif' : ''}" data-aksi="tpNama" data-n="${nm}">${nm}</div>`)}</div>` : ''}
      <div class="kaca-btn aktif emas" data-aksi="tpKirim" data-k="tp-kirim">KIRIM KE OWNER${n > 0 ? ' · ' + RP(n) : ''}</div>
      <div class="ket" style="font-size: 11px;">Uangnya boleh diambil dari laci sekarang; laci di buku baru berkurang sesudah owner menyetujui. Owner bisa membetulkan angka atau menolak dengan alasan.</div>`;
  const formPesan = h`<textarea class="ketik-nama" rows="3" maxlength="${TP.TP_BATAS.pesan}" placeholder="tulis pesan untuk owner (mis. kantong 5 kg tinggal 20 lembar)" data-ketik="tpKetik" data-kolom="pesan">${d.pesan}</textarea>
      <div class="kaca-btn aktif emas" data-aksi="tpKirimPesan" data-k="tp-kirim-pesan">KIRIM PESAN</div>`;
  const baris = (b) => h`<div class="tp-baris ${kelasStatus(b.status)}" data-k="tp-${b.id}"><div style="min-width: 0;"><div>${b.kabar ? 'Kabar barang masuk: ' + b.teks : b.pesan ? 'Pesan: ' + b.teks : b.ringkas}</div>
      <div class="k2">${tanggalPendek(b.tanggal)} ${b.jam} · ${b.dari} · <b>${b.namaStatus}</b>${b.diputus ? ' ' + b.diputus : ''}${b.dikoreksi ? ' · dibetulkan owner (diketik ' + RP(b.asli.nominal) + ')' : ''}</div>
      ${b.alasan ? h`<div class="k2 awas-teks">Alasan owner: ${b.alasan}</div>` : ''}${b.balasan ? h`<div class="k2">Balasan owner: ${b.balasan}</div>` : ''}</div>
      <div class="kaca-btn kecil tp-cetak" data-aksi="tpCetak" data-id="${b.id}">Cetak</div></div>`;
  return h`<div class="kartu" data-k="tp-kartu" style="gap: 8px;"><div class="label">Uang keluar & pesan untuk owner${tunggu.length ? ' · ' + tunggu.length + ' menunggu ' + RP(tunggu.reduce((x, b) => x + b.nominal, 0)) : ''}</div>
    <div class="tombol-baris" data-k="tp-tab"><div class="kaca-btn ${d.tab === 'uang' ? 'aktif' : ''}" data-aksi="tpTab" data-t="uang">Uang keluar</div><div class="kaca-btn ${d.tab === 'pesan' ? 'aktif' : ''}" data-aksi="tpTab" data-t="pesan">Pesan</div></div>
    ${d.tab === 'pesan' ? formPesan : formUang}
    ${saya.length ? h`<div class="label" data-k="tp-daftar">Dari tablet ini · 7 hari</div>${saya.map(baris)}<div class="kaca-btn" data-aksi="tpCetakRekap" style="align-self: flex-start;">Cetak rekap hari ini</div>` : h`<div class="ket" data-k="tp-kosong">Belum ada titipan atau pesan dari tablet ini dalam 7 hari.</div>`}</div>`;
}

/** Aksi panel — digabung ke AKSI layar Menu. tulis(r) = penulis layar (kabar ikut); waktu() = { tanggal, jam, kini, idUnik }. */
export function aksiTitipan({ set, st, tulis, akun, waktu }) {
  const draf = () => Object.assign(TP_DRAF_KOSONG(), st().tp || {});
  const ubah = (p) => set({ tp: Object.assign(draf(), p) });
  const ak = () => (akun ? akun() : null);
  function cetak(teks, nama) {
    if (!asliAda()) { const pre = document.getElementById('cetakStruk'); if (pre) { pre.textContent = teks; pre.className = 'cetak-struk k' + (Number(ST.stAtur().kertas) === 58 ? 58 : 80); } try { window.print(); } catch (e) { /* abaikan */ } return; }
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    set({ kabar: 'Mencetak ' + nama.toLowerCase() + '…', kabarAwas: false });
    PR.cetakTeks(teks).then((r) => set({ kabar: nama + ' tercetak lewat ' + PR.namaJalur(r.jalur) + (r.cadanganDari ? ' — jalur yang dipilih tidak jalan (' + r.cadanganDari + ')' : ''), kabarAwas: !!r.cadanganDari }))
      .catch((e) => {
        if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
        if (hasilTakDiketahui(e)) return set({ kabar: KALIMAT_TAK_DIKABARI, kabarAwas: true });
        set({ kabar: nama + ' TIDAK tercetak: ' + (e && e.message ? e.message : e), kabarAwas: true });
      });
  }
  const dicetak = () => { const w = waktu(); const a = ak(); return { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }; };
  return {
    tpTab: ({ t }) => ubah({ tab: t === 'pesan' ? 'pesan' : 'uang' }),
    tpJenis: ({ j }) => ubah({ jenis: j, nama: j === 'kasbon' || j === 'karyawan' ? draf().nama || ((ak() && ak().nama) || '') : '' }),
    tpPemasok: ({ p }) => ubah({ pemasok: draf().pemasok === p ? '' : p }),
    tpNama: ({ n }) => ubah({ nama: draf().nama === n ? '' : n }),
    tpKetik: (v, el) => { const k = el.dataset.kolom; ubah({ [k]: String(v).slice(0, k === 'pesan' ? TP.TP_BATAS.pesan : k === 'nominal' ? 14 : k === 'pemasok' ? 60 : TP.TP_BATAS.teks) }); },
    tpMati: () => set({ kabar: 'Peran ' + ((ak() && ak().nama) || 'ini') + ' tidak boleh mencatat uang keluar — owner bisa mengubahnya di Menu › Toko ini › Peran & persetujuan', kabarAwas: true }),
    tpKirim: async () => { const d = draf(); if (await tulis(TP.tpSusunMinta(d, ak(), waktu()))) set({ tp: Object.assign(TP_DRAF_KOSONG(), { jenis: d.jenis }) }); },
    tpKirimPesan: async () => { const d = draf(); if (await tulis(TP.tpSusunPesan(d.pesan, ak(), waktu()))) set({ tp: Object.assign(TP_DRAF_KOSONG(), { tab: 'pesan' }) }); },
    tpCetak: ({ id }) => { const b = TP.tpMilikSaya(ak(), waktu().tanggal, 7).find((x) => x.id === String(id)); if (!b) return set({ kabar: 'Catatannya tidak ditemukan', kabarAwas: true });
      cetak(TP.tpTeksCetak(b, ST.stAtur().kop, dicetak()), b.pesan ? 'Pesan' : 'Titipan'); },
    tpCetakRekap: () => { const w = waktu(); cetak(TP.tpTeksRekap(TP.tpMilikSaya(ak(), w.tanggal, 1), w.tanggal, ST.stAtur().kop, dicetak()), 'Rekap titipan'); },
  };
}
