// Kartu RINGKAS HARI INI di tablet (owner 21 Nov 2026: kartu paling atas Menu akun tablet, hanya saat orang pilihan owner jaga). Angka dari
// ringkas-tablet-logika.js; panel ini hanya menggambar, membuka rincian laci, dan mencetak. Tidak menulis apa pun.
import { h } from '../inti/dom.js';
import { RP, KG, ANGKA, tanggalPendek } from '../inti/format.js';
import * as RT from './ringkas-tablet-logika.js';
import * as ST from './struk-logika.js';
import * as PR from '../inti/printer.js';
import { asliAda, printerSibuk, masihMencetak, hasilTakDiketahui, KALIMAT_MASIH_MENCETAK, KALIMAT_TAK_DIKABARI } from '../inti/perangkat.js';

const rtHari = (x) => (x === null || x === undefined ? '' : '±' + String(x).replace('.', ',') + ' hari');

/** Kartu. opsi = { akun (efektif), uang (status.uang firebase.js), kini (Date) }. */
export function kartuRingkas(s, opsi) {
  const o = opsi || {}; const R = RT.rtHitung(o.kini || new Date(), o.akun, o.uang); const L = R.laci;
  const baris = (k, kiri, kanan, kelas) => h`<div class="rt-baris ${kelas || ''}" data-k="${k}"><span>${kiri}</span><b>${kanan}</b></div>`;
  const laci = L && L.ada
    ? h`<div class="k2">Perkiraan isi laci sekarang</div><div class="serif rt-besar" data-gulir="${Math.round(L.kira)}">${RP(L.kira)}</div>
        <div class="k2">semalam ${RP(L.awal)} + masuk ${RP(L.masuk)} − keluar ${RP(L.keluar)} = seharusnya ${RP(L.seharusnya)}${L.titipan ? ' − titipan belum diputus ' + RP(L.titipan) : ''}</div>
        <div class="kaca-btn kecil" data-aksi="rtRinci" style="align-self: flex-start;">${s.rtRinci ? 'tutup rincian laci' : 'rincian laci'}</div>`
    : L ? h`<div class="k2">Perkiraan isi laci</div><div class="pita-info awas" data-k="rt-laci-ket">${L.teks}</div>`
      : h`<div class="k2">Perkiraan isi laci</div><div class="pita-info ${R.uang.st === 'ditolak' ? 'awas' : ''}" data-k="rt-uang-ket">${R.uang.teks}</div>`;
  return h`<div class="kartu rt-kartu" data-k="rt-kartu" style="gap: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;"><div class="label">Ringkas hari ini · ${tanggalPendek(R.iso)} · hanya saat ${o.akun ? o.akun.nama : 'owner'} jaga</div>
      <div class="kaca-btn kecil" data-aksi="rtCetak" data-k="rt-cetak">Cetak</div></div>
    <div class="rt-dua" data-k="rt-dua">
      <div class="rt-kolom" data-k="rt-omzet"><div class="k2">Omzet · ${ANGKA(R.nota)} nota</div><div class="serif rt-besar" data-gulir="${Math.round(R.omzet)}">${RP(R.omzet)}</div>
        <div class="k2">tunai ${RP(R.tunai)} · QRIS ${RP(R.qris)} · bon baru ${RP(R.bon)}${R.retur ? ' · retur −' + RP(R.retur) : ''}</div>
        <div class="k2">bon dibayar tunai ${RP(R.bonTunai)}${R.bonQris ? ' · QRIS ' + RP(R.bonQris) : ''}</div></div>
      <div class="rt-kolom" data-k="rt-laci">${laci}</div>
    </div>
    ${s.rtRinci && L && L.ada ? h`<div class="rt-rinci" data-k="rt-rinci">${L.baris.map((b, i) => baris('rl-' + i, b.nama, (b.arah > 0 ? '+ ' : '− ') + RP(b.n)))}</div>` : ''}
    ${R.titipan.n ? h`<div class="pita-info awas" data-k="rt-titip">${R.titipan.n} titipan uang keluar dari tablet belum diputus · ${RP(R.titipan.rp)} — uangnya sudah keluar dari laci, buku belum</div>` : ''}
    ${R.keluar ? h`<div class="rt-blok" data-k="rt-keluar"><div class="label">Uang keluar hari ini · ${RP(R.keluar.total)}</div>
      ${R.keluar.daftar.length ? R.keluar.daftar.map((x, i) => baris('kl-' + i, x.nama + (x.n > 1 ? ' · ' + x.n + ' catatan' : ''), RP(x.rp))) : h`<div class="k2">Belum ada uang keluar tercatat hari ini.</div>`}</div>` : ''}
    <div class="rt-dua" data-k="rt-dua2">
      <div class="rt-blok" data-k="rt-orang"><div class="label">Per orang yang jaga</div>${R.perOrang.length ? R.perOrang.map((x, i) => baris('po-' + i, x.nama + ' · ' + x.nota + ' nota', RP(x.rp))) : h`<div class="k2">Belum ada nota hari ini.</div>`}</div>
      <div class="rt-blok" data-k="rt-laris"><div class="label">Terlaris hari ini</div>${R.terlaris.length ? R.terlaris.map((x, i) => baris('tl-' + i, x.nama, KG(x.kg))) : h`<div class="k2">Belum ada barang keluar.</div>`}</div>
    </div>
    <div class="rt-dua" data-k="rt-dua3">
      <div class="rt-blok" data-k="rt-tipis"><div class="label">Stok tipis</div>${R.tipis.map((x, i) => baris('st-' + i, x.nama, x.minus ? 'MINUS ' + RT.rtTeksSisa(x) : RT.rtTeksSisa(x) + ' · ' + rtHari(x.hari), x.minus ? 'awas' : ''))}
        ${R.habis.n ? h`<div class="k2" data-k="rt-habis">${RT.rtTeksHabis(R.habis)}</div>` : ''}
        ${!R.tipis.length && !R.habis.n ? h`<div class="k2">Tidak ada yang hampir habis.</div>` : ''}</div>
      <div class="rt-blok" data-k="rt-pesan"><div class="label">Pesanan & antar</div>
        ${R.pesanan.map((x, i) => baris('ps-' + i, x.nama + (x.isi ? ' · ' + x.isi : ''), x.lewat ? 'LEWAT ' + tanggalPendek(x.tanggal) : x.status === 'diantar' ? 'diantar' : 'hari ini', x.lewat ? 'awas' : ''))}
        ${R.jalan.length ? baris('sj', 'Surat jalan masih di jalan', ANGKA(R.jalan.length)) : ''}
        ${R.cod.map((x, i) => baris('cod-' + i, 'Bayar di tempat belum disetor · ' + x.pengantar, RP(x.rp), 'awas'))}
        ${!R.pesanan.length && !R.jalan.length && !R.cod.length ? h`<div class="k2">Tidak ada pesanan jatuh hari ini, tidak ada antaran di jalan.</div>` : ''}</div>
    </div>
  </div>`;
}

/** Aksi kartu — digabung ke AKSI layar Menu. waktu() = { tanggal, jam }; akun() = akun efektif; uang() = status.uang. */
export function aksiRingkas({ set, st, akun, uang, waktu, kini }) {
  function cetak(teks) {
    if (!asliAda()) { const pre = document.getElementById('cetakStruk'); if (pre) { pre.textContent = teks; pre.className = 'cetak-struk k' + (Number(ST.stAtur().kertas) === 58 ? 58 : 80); } try { window.print(); } catch (e) { /* abaikan */ } return; }
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    set({ kabar: 'Mencetak ringkas hari ini…', kabarAwas: false });
    PR.cetakTeks(teks).then((r) => set({ kabar: 'Ringkas hari ini tercetak lewat ' + PR.namaJalur(r.jalur) + (r.cadanganDari ? ' — jalur yang dipilih tidak jalan (' + r.cadanganDari + ')' : ''), kabarAwas: !!r.cadanganDari }))
      .catch((e) => {
        if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
        if (hasilTakDiketahui(e)) return set({ kabar: KALIMAT_TAK_DIKABARI, kabarAwas: true });
        set({ kabar: 'Ringkas hari ini TIDAK tercetak: ' + (e && e.message ? e.message : e), kabarAwas: true });
      });
  }
  return {
    rtRinci: () => set({ rtRinci: !st().rtRinci }),
    rtCetak: () => { const a = akun ? akun() : null; if (!RT.rtTampil(a)) return set({ kabar: 'Ringkas hari ini hanya untuk orang pilihan owner', kabarAwas: true });
      const w = waktu(); cetak(RT.rtTeksCetak(RT.rtHitung(kini(), a, uang ? uang() : null), ST.stAtur().kop, { tanggal: w.tanggal, jam: w.jam, oleh: a.nama })); },
  };
}
