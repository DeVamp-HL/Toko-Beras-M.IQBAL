// Panel TANDA TERIMA BARANG MASUK di layar Stok (owner 21 Nov 2026): kartu satu kedatangan (cetak 2 lembar · WhatsApp) dan lembar daftar
// kedatangan terakhir untuk akun yang tidak membuka lembar Barang masuk (akun tablet — printer struknya ada di sana). Isi dan angka lembar di
// terima-barang-logika.js; panel ini hanya menggambar dan meneruskan ketukan. TIDAK menulis apa pun ke buku.
import { h } from '../inti/dom.js';
import { RP, KG, tanggalPendek } from '../inti/format.js';
import * as TBM from './terima-barang-logika.js';
import * as C from './stok-catat-logika.js';
import * as ST from './struk-logika.js';
import * as PR from '../inti/printer.js';
import { epSusun } from '../inti/escpos.js';
import { hasilTakDiketahui, masihMencetak, printerSibuk, KALIMAT_MASIH_MENCETAK, asliAda } from '../inti/perangkat.js';
import { bukanOwner, akunMembaca } from './akses-layar.js';
import { cacheMentah } from '../data/toko.js';

const KOLEKSI_BAYAR = 'utangPemasokMutasi';

/** Isi tanda terima kedatangan `id` untuk akun ini: { d } atau { tolak }. Pembayaran bon dibaca hanya bila akun ini membacanya. */
export function isiTerima(id, akun) {
  const batch = C.batchKedatangan(id); const tolak = TBM.tbmTolak(batch); if (tolak) return { tolak };
  const terbaca = akunMembaca(akun, KOLEKSI_BAYAR); const bb = terbaca ? C.ckBayarBon(batch) : null;
  return { d: TBM.tbmData(batch, { terbaca, dibayar: bb ? bb.dibayarMesin : 0, rinci: bb ? bb.bayar : [], titipSupir: titipSupir(batch, terbaca) }) };
}
/**
 * owner 22 Nov 2026 (paket ③): uang yang dibayar ke supir lewat TITIPAN tablet untuk kedatangan ini (bayar bon pemasok, menunjuk batchId). Yang masih menunggu
 * owner selalu disebut (belum ada di buku bon); yang sudah disetujui disebut hanya bila akun ini tidak membaca buku bon (di akun owner ia sudah jadi pembayaran).
 */
function titipSupir(batch, terbaca) {
  return Math.round(cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'uangKeluar' && m.jenis === 'bayarBon' && String(m.batchId || '') === String(batch.id)
    && ((m.status || 'menunggu') === 'menunggu' || (!terbaca && m.status === 'disetujui'))).reduce((a, m) => a + (Number(m.nominal) || 0), 0));
}

const sebutJumlah = (j) => [j.karung ? j.karung + ' karung' : '', j.bal ? j.bal + ' bal' : '', KG(j.kg)].filter(Boolean).join(' · ');
// modal tidak tampil di layar akun bukan-owner (keputusan 16 Nov: modal boleh di tablet asal tersembunyi) — di kertasnya nilai nota tetap ada
const sebutBayarLayar = (d, staf) => (staf ? (d.bon ? 'bon' : 'tunai') : 'nilai nota ' + RP(d.nilai) + ' · ' + TBM.tbmKalimatBayar(d));

/**
 * Kartu tanda terima satu kedatangan. opsi = { akun, tutup: true = tombol tutup (kartu yang dibuka sendiri, bukan bagian koreksi) }.
 * id kosong / kedatangan tidak bisa dibuatkan tanda terima → kalimat sebabnya, tanpa tombol cetak.
 */
export function kartuTerima(id, opsi) {
  if (id === undefined || id === null || id === '') return '';
  const o = opsi || {}; const staf = bukanOwner(o.akun); const r = isiTerima(id, o.akun);
  if (r.tolak) return h`<div class="kartu" data-k="tbm-kartu" style="gap: 6px;"><div class="label">Tanda terima untuk supir</div><div class="ket">${r.tolak}</div>${o.tutup ? h`<div class="kaca-btn putus" data-aksi="tbmTutup" style="align-self: flex-start;">tutup</div>` : ''}</div>`;
  const d = r.d;
  return h`<div class="kartu" data-k="tbm-kartu" style="gap: 6px;"><div class="label">Tanda terima untuk supir · ${d.no}</div>
    <div><b>${d.pemasok}</b> · ${tanggalPendek(d.tanggal)}${d.jam ? ' ' + d.jam : ''}</div>
    <div class="ket" data-k="tbm-ringkas">${sebutJumlah(d.jumlah)} · ${sebutBayarLayar(d, staf)}</div>
    ${d.bayar.keadaan === 'takTerbaca' ? h`<div class="ket awas-teks" data-k="tbm-tangan">Pembayaran ke pemasok hanya terbaca di akun owner. Di lembar ini baris "Dibayar" dan "Sisa" dikosongkan — tulis tangan, lalu diparaf toko dan supir.</div>` : ''}
    <div class="tombol-baris rapat"><div class="kaca-btn aktif emas" data-aksi="tbmCetak" data-id="${id}">CETAK 2 LEMBAR</div>${asliAda() ? '' : h`<div class="kaca-btn" data-aksi="tbmWa" data-id="${id}">WhatsApp</div>`}${o.tutup ? h`<div class="kaca-btn putus" data-aksi="tbmTutup">tutup</div>` : ''}</div>
    <div class="ket" style="font-size: 11px;">Lembar pemasok dibawa supir; lembar toko ditandatangani supir lalu disimpan. Mencetak tidak mengubah catatan apa pun.</div></div>`;
}

/** Lembar daftar kedatangan terakhir (akun tablet): pilih satu, kartunya muncul di atas daftar. */
export function lembarTerima(s, opsi) {
  const o = opsi || {}; const pilih = s.tbm && s.tbm.id !== undefined ? String(s.tbm.id) : '';
  const daftar = C.daftarKedatangan(12).filter((k) => !k.fondasi && k.pemasok && k.pemasok !== '—');
  return h`<section class="stok-masuk" data-k="terima">
    <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Tanda terima barang masuk</div><div class="ket">kedatangan yang sudah dicatat · pilih satu, cetak untuk supir pemasok</div></div>
      <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
    ${pilih ? kartuTerima(pilih, { akun: o.akun, tutup: true }) : ''}
    <div class="kartu" data-k="tbm-daftar" style="gap: 6px;"><div class="label">Kedatangan terakhir</div>
      ${daftar.length ? daftar.map((k) => h`<div class="jawab ${pilih === String(k.id) ? 'dipilih' : ''}" data-k="tbm-${k.id}" data-aksi="tbmPilih" data-id="${k.id}"><span class="kiri"><span class="nm">${k.pemasok} <span class="w">· ${tanggalPendek(k.tanggal)}${k.jam ? ' ' + k.jam : ''}</span></span><span class="w">${k.ringkas}</span></span>
        <span class="kanan"><span class="n">${k.karung} karung</span><span class="w">${k.cara === 'utang' ? 'bon' : 'tunai'}</span></span></div>`)
    : h`<div class="ket" data-k="tbm-kosong">Belum ada kedatangan yang tercatat. Begitu barang masuk tersimpan (Stok › Barang masuk), kedatangannya muncul di sini.</div>`}</div>
  </section>`;
}

/** Aksi panel — digabung ke AKSI layar Stok. waktu() = jam setempat (tanggal, jam); akun() = akun yang masuk. */
export function aksiPanelTerima({ set, akun, waktu }) {
  const ak = () => (akun ? akun() : null);
  const lembarCetak = (d) => { const w = waktu(); const a = ak(); return TBM.tbmLembar(d, ST.stAtur().kop, { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }); };
  function cetak(id) {
    const r = isiTerima(id, ak()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    const d = r.d; const lembar = lembarCetak(d); const kertas = Number(ST.stAtur().kertas) === 58 ? 58 : 80;
    // di aplikasi tablet dialog cetak hanya berkelebat lalu hilang (uji owner 20 Nov 2026): katakan terus terang lembarnya tidak keluar
    const dialog = () => { if (asliAda()) return set({ kabar: 'Tanda terima TIDAK tercetak: di tablet ini hanya keluar lewat printer tablet — periksa di Jual › Struk › "Printer tablet ini", lalu cetak lagi', kabarAwas: true });
      const el = document.getElementById('cetakStruk'); if (!el) return set({ kabar: 'Dialog cetak tidak tersedia di layar ini', kabarAwas: true });
      el.textContent = lembar.map((g) => epSusun(g, { kertas, potong: 'tidak', umpan: 0 }).teks.join('\n')).join('\n\n' + '- - potong di sini - -' + '\n\n'); el.className = 'cetak-struk k' + kertas;
      try { window.print(); } catch (e) { set({ kabar: 'Dialog cetak tidak bisa dibuka: ' + (e && e.message ? e.message : e), kabarAwas: true }); } };
    // satu cetakan pada satu waktu: selama cetakan lain belum dikabari printer, tidak ada yang dikirim
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    PR.jalurCetak().then((j) => {
      if (j === 'dialog') return dialog();
      set({ kabar: 'Mencetak tanda terima ' + d.no + '…', kabarAwas: false });
      // dua lembar berurutan, masing-masing dipotong printer: lembar pemasok dulu, lalu lembar toko
      let n = 0;
      return lembar.reduce((p, g) => p.then(() => PR.susunCetak(g, { gaya: 'teks' }, { qr: '' })).then((x) => PR.kirimCetak(x.byte, j)).then(() => { n += 1; }), Promise.resolve())
        .then(() => set({ kabar: 'Tanda terima ' + d.no + ' dicetak 2 lembar: LEMBAR PEMASOK dibawa supir, LEMBAR TOKO ditandatangani supir lalu disimpan', kabarAwas: false }))
        .catch((e) => {
          // printer diam sesudah data dikirim = hasil lembar itu TIDAK DIKETAHUI, bukan "gagal": kertasnya dilihat dulu, tidak dikirim ulang sendiri
          if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK + (n ? ' — ' + n + ' lembar sudah keluar' : ''), kabarAwas: true });
          if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-' + (n + 1) + ' dari ' + lembar.length + ' — lihat kertasnya dulu; kalau ada yang tidak keluar, cetak lagi tanda terimanya', kabarAwas: true });
          const gagal = PR.sebutPrinter(j) + ' gagal' + (n ? ' sesudah ' + n + ' lembar' : '') + ' (' + (e && e.message ? e.message : e) + ') — ';
          if (asliAda()) return set({ kabar: gagal + 'tanda terima TIDAK tercetak' + (n ? ' lengkap' : '') + '. Bereskan printernya, lalu cetak lagi', kabarAwas: true });
          set({ kabar: gagal + 'dialog cetak dibuka sebagai gantinya', kabarAwas: true }); dialog();
        });
    }).catch(() => dialog());
  }
  function wa(id) {
    const r = isiTerima(id, ak()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    const w = waktu(); const a = ak();
    const teks = epSusun(TBM.tbmGaris(r.d, ST.stAtur().kop, '', { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }), { kertas: 58, potong: 'tidak', umpan: 0 }).teks.join('\n');
    try { const j = window.open(ST.tautanWa(teks), '_blank'); if (j) { try { j.opener = null; } catch (e) { /* jendela sudah pindah asal */ } } else set({ kabar: 'WhatsApp ditahan peramban — izinkan jendela baru untuk halaman ini', kabarAwas: true }); }
    catch (e) { set({ kabar: 'WhatsApp tidak bisa dibuka', kabarAwas: true }); }
  }
  return {
    bukaTerima: () => set({ lembar: 'terima', tbm: null, kabar: '' }),
    tbmPilih: ({ id }) => set({ tbm: { id: String(id) }, kabar: '' }),
    tbmTutup: () => set({ tbm: null }),
    tbmCetak: ({ id }) => cetak(id),
    tbmWa: ({ id }) => wa(id),
  };
}
