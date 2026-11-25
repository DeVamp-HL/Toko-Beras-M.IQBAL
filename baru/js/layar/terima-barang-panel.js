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

const sebutJumlah = (j) => [j.karung ? j.karung + ' karung' : '', j.kemasan ? j.kemasan + ' kemasan' : '', j.bal ? j.bal + ' bal' : '', KG(j.kg)].filter(Boolean).join(' · ');
// modal tidak tampil di layar akun bukan-owner (keputusan 16 Nov: modal boleh di tablet asal tersembunyi) — di kertasnya nilai nota tetap ada
const sebutBayarLayar = (d, staf) => (staf ? (d.bon ? 'bon' : 'tunai') : 'nilai nota ' + RP(d.nilai) + ' · ' + TBM.tbmKalimatBayar(d));

/**
 * Tahap 5 (owner 26 Nov 2026): tombol cetak CATATAN UNTUK PEMASOK kedatangan itu langsung dari kartu tanda terima — hanya bila kedatangannya punya catatan
 * (catatan / klaim / catatan bebas / baris ditolak / potongan) atau usul dari timbang & mutu. Isinya = cpIsiSurat (penyusun yang sama dengan Dokumen kecil).
 */
function catatanKartu(id) {
  const S = C.cpIsiSurat(id); if (!S || !S.bisaCetak) return '';
  const n = S.C.catatan.length + (S.C.bebas.trim() ? 1 : 0) + S.C.ditolak.length + S.C.potongan.length;
  return h`<div data-k="tbm-catatan" style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--kaca-tepi); padding-top: 6px;">
    <div class="ket">Catatan untuk pemasok · ${n ? n + ' catatan' + (S.C.klaim ? ' · ' + S.C.klaim.caraNama.toLowerCase() : '') : 'belum ditulis — ' + S.C.usul.length + ' hal dari hasil timbang & cek mutu'}</div>
    <div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="tbmCatatan" data-id="${id}" data-k="tbm-catatan-cetak">CETAK CATATAN PEMASOK</div>${asliAda() ? '' : h`<div class="kaca-btn" data-aksi="tbmCatatanWa" data-id="${id}" data-k="tbm-catatan-wa">WhatsApp</div>`}</div></div>`;
}

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
    ${catatanKartu(id)}
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
    ${o.bawah || ''}
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
  // Tahap 5: struk catatan untuk pemasok — satu lembar, garisnya dari tbmGarisCatatan (isi cpIsiSurat)
  const garisCatatan = (id) => { const S = C.cpIsiSurat(id); if (!S || !S.bisaCetak) return { tolak: 'Kedatangan ini tidak punya catatan untuk pemasok, dan timbang / cek mutunya tidak menemukan yang perlu dicatat' };
    const batch = C.batchKedatangan(id); const w = waktu(); const a = ak(); return { S, no: batch ? TBM.tbmNomor(batch) : '', garis: TBM.tbmGarisCatatan(S, ST.stAtur().kop, batch ? TBM.tbmNomor(batch) : '', { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }) }; };
  function cetak(id) {
    const r = isiTerima(id, ak()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    kirim(lembarCetak(r.d), { nama: 'Tanda terima', sebut: 'tanda terima ' + r.d.no, selesai: 'Tanda terima ' + r.d.no + ' dicetak 2 lembar: LEMBAR PEMASOK dibawa supir, LEMBAR TOKO ditandatangani supir lalu disimpan' });
  }
  function cetakCatatan(id) {
    const G = garisCatatan(id); if (G.tolak) return set({ kabar: G.tolak, kabarAwas: true });
    kirim([G.garis], { nama: 'Catatan untuk pemasok', sebut: 'catatan untuk pemasok' + (G.no ? ' ' + G.no : ''), selesai: 'Catatan untuk pemasok dicetak 1 lembar — dibawa supir untuk pemilik ' + (G.S.C.pemasok || 'pemasok') + '. Butuh arsip toko? Cetak sekali lagi' });
  }
  /** Kirim lembar-lembar struk ke jalur cetak perangkat ini (printer tablet / jaringan, atau dialog cetak peramban = bisa disimpan PDF). T = { nama, sebut, selesai }. */
  function kirim(lembar, T) {
    const kertas = Number(ST.stAtur().kertas) === 58 ? 58 : 80;
    // di aplikasi tablet dialog cetak hanya berkelebat lalu hilang (uji owner 20 Nov 2026): katakan terus terang lembarnya tidak keluar
    const dialog = () => { if (asliAda()) return set({ kabar: T.nama + ' TIDAK tercetak: di tablet ini hanya keluar lewat printer tablet — periksa di Jual › Struk › "Printer tablet ini", lalu cetak lagi', kabarAwas: true });
      const el = document.getElementById('cetakStruk'); if (!el) return set({ kabar: 'Dialog cetak tidak tersedia di layar ini', kabarAwas: true });
      el.textContent = lembar.map((g) => epSusun(g, { kertas, potong: 'tidak', umpan: 0 }).teks.join('\n')).join('\n\n' + '- - potong di sini - -' + '\n\n'); el.className = 'cetak-struk k' + kertas;
      try { window.print(); } catch (e) { set({ kabar: 'Dialog cetak tidak bisa dibuka: ' + (e && e.message ? e.message : e), kabarAwas: true }); } };
    // satu cetakan pada satu waktu: selama cetakan lain belum dikabari printer, tidak ada yang dikirim
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    PR.jalurCetak().then((j) => {
      if (j === 'dialog') return dialog();
      set({ kabar: 'Mencetak ' + T.sebut + '…', kabarAwas: false });
      // dua lembar berurutan, masing-masing dipotong printer: lembar pemasok dulu, lalu lembar toko
      let n = 0;
      return lembar.reduce((p, g) => p.then(() => PR.susunCetak(g, { gaya: 'teks' }, { qr: '' })).then((x) => PR.kirimCetak(x.byte, j)).then(() => { n += 1; }), Promise.resolve())
        .then(() => set({ kabar: T.selesai, kabarAwas: false }))
        .catch((e) => {
          // printer diam sesudah data dikirim = hasil lembar itu TIDAK DIKETAHUI, bukan "gagal": kertasnya dilihat dulu, tidak dikirim ulang sendiri
          if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK + (n ? ' — ' + n + ' lembar sudah keluar' : ''), kabarAwas: true });
          if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-' + (n + 1) + ' dari ' + lembar.length + ' — lihat kertasnya dulu; kalau ada yang tidak keluar, cetak lagi ' + T.nama.toLowerCase() + '-nya', kabarAwas: true });
          const gagal = PR.sebutPrinter(j) + ' gagal' + (n ? ' sesudah ' + n + ' lembar' : '') + ' (' + (e && e.message ? e.message : e) + ') — ';
          if (asliAda()) return set({ kabar: gagal + T.nama.toLowerCase() + ' TIDAK tercetak' + (n ? ' lengkap' : '') + '. Bereskan printernya, lalu cetak lagi', kabarAwas: true });
          set({ kabar: gagal + 'dialog cetak dibuka sebagai gantinya', kabarAwas: true }); dialog();
        });
    }).catch(() => dialog());
  }
  function wa(id, catatan) {
    let garis;
    if (catatan) { const G = garisCatatan(id); if (G.tolak) return set({ kabar: G.tolak, kabarAwas: true }); garis = G.garis; }
    else { const r = isiTerima(id, ak()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); const w = waktu(); const a = ak(); garis = TBM.tbmGaris(r.d, ST.stAtur().kop, '', { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }); }
    const teks = epSusun(garis, { kertas: 58, potong: 'tidak', umpan: 0 }).teks.join('\n');
    try { const j = window.open(ST.tautanWa(teks), '_blank'); if (j) { try { j.opener = null; } catch (e) { /* jendela sudah pindah asal */ } } else set({ kabar: 'WhatsApp ditahan peramban — izinkan jendela baru untuk halaman ini', kabarAwas: true }); }
    catch (e) { set({ kabar: 'WhatsApp tidak bisa dibuka', kabarAwas: true }); }
  }
  return {
    bukaTerima: () => set({ lembar: 'terima', tbm: null, kabar: '' }),
    tbmPilih: ({ id }) => set({ tbm: { id: String(id) }, kabar: '' }),
    tbmTutup: () => set({ tbm: null }),
    tbmCetak: ({ id }) => cetak(id),
    tbmWa: ({ id }) => wa(id),
    tbmCatatan: ({ id }) => cetakCatatan(id),
    tbmCatatanWa: ({ id }) => wa(id, true),
  };
}
