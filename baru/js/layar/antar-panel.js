// PANEL ANTAR — B3 surat jalan & antar (owner 18 Nov 2026). Dipakai layar Jual: bagian Antar di lembar Bayar, lembar daftar Antar, lembar Terima (tanda
// tangan di KERTAS + foto lembar toko — cara utama, tablet tetap di toko — ATAU tanda tangan di layar + foto boleh dilewati; + uang bayar di tempat).
// Cetak surat jalan = 2 lembar (LEMBAR PEMBELI · LEMBAR TOKO). Logika & angka di antar-logika.js (tanpa DOM) — panel ini hanya menggambar & meneruskan ketukan.
// Gambar tanda tangan & foto TIDAK masuk keadaan layar (bisa ratusan KB): disimpan di memori panel sampai SIMPAN, lalu dikirim ke koleksi buktiTerima.
import { h } from '../inti/dom.js';
import { RP, tanggalPendek, hariIniIso } from '../inti/format.js';
import * as AJ from './antar-logika.js';
import * as ST from './struk-logika.js';
import * as PR from '../inti/printer.js';
import { hasilTakDiketahui, masihMencetak, printerSibuk, KALIMAT_MASIH_MENCETAK, asliAda } from '../inti/perangkat.js';
import { fbnKecilkan, fbnSrc, fbnKB } from './foto-bon-logika.js';
import { tombolAkun, bukanOwner } from './akses-layar.js';
import { tulisDokumen, kabarKiriman, ambilPenjualanSemua } from '../data/toko.js';

const KABAR_PERMISI = 'Server belum membuka tempat surat jalan / bukti terima (rules v10 — diterbitkan owner di Firebase Console). Sesudah terbit, coba lagi.';
const isiRingkas = (x) => (x.isi || []).map((b) => b.nama + ' ' + String(b.jumlah).replace('.', ',') + ' ' + b.satuan).join(' · ');

/**
 * ctx = { set, S (keadaan Jual), akun() (akun yang masuk), waktu() ({ tanggal, jam, kini, idUnik }), bukti ({ ada(), baca(idSJ), simpan(daftar) } — app.js),
 *         tunjukNota(id) (buka Retur atas satu baris nota) }.
 */
export function buatPanelAntar(ctx) {
  const set = ctx.set; const S = ctx.S; const akun = () => (ctx.akun ? ctx.akun() : null);
  // ---- memori panel: goresan tanda tangan, foto yang sudah dikecilkan, bukti yang dibaca, bukti simulasi (mode cadangan)
  let gores = []; let goresKini = null; let ttdUntuk = ''; let foto = null; let fotoProses = false;
  let lihat = { id: '', muat: '', daftar: [], pesan: '' }; const sim = {};
  const nTitik = () => gores.reduce((a, g) => a + g.length, 0);
  const buktiServer = () => !!(ctx.bukti && ctx.bukti.ada && ctx.bukti.ada());
  const hari = () => hariIniIso(S().sekarang || new Date());

  // ---------- tanda tangan di kanvas ----------
  function gambarTtd(c) {
    if (!c || !c.getContext) return; const x = c.getContext('2d'); if (!x) return;
    x.fillStyle = '#ffffff'; x.fillRect(0, 0, c.width, c.height);
    x.strokeStyle = '#111111'; x.lineWidth = 3.2; x.lineCap = 'round'; x.lineJoin = 'round';
    gores.forEach((g) => { if (!g.length) return; x.beginPath(); x.moveTo(g[0][0], g[0][1]); if (g.length === 1) x.lineTo(g[0][0] + 0.1, g[0][1] + 0.1); g.slice(1).forEach((p) => x.lineTo(p[0], p[1])); x.stroke(); });
  }
  const titik = (c, ev) => { const r = c.getBoundingClientRect(); return [Math.round((ev.clientX - r.left) * (c.width / (r.width || 1))), Math.round((ev.clientY - r.top) * (c.height / (r.height || 1)))]; };
  function pasang(akar) {
    akar.addEventListener('pointerdown', (ev) => { const c = ev.target && ev.target.closest ? ev.target.closest('canvas[data-ttd]') : null; if (!c) return;
      ev.preventDefault(); try { c.setPointerCapture(ev.pointerId); } catch (e) { /* abaikan */ } goresKini = [titik(c, ev)]; gores.push(goresKini); gambarTtd(c); });
    akar.addEventListener('pointermove', (ev) => { if (!goresKini) return; const c = akar.querySelector('canvas[data-ttd]'); if (!c) return; ev.preventDefault(); goresKini.push(titik(c, ev)); gambarTtd(c); });
    const selesai = () => { if (!goresKini) return; goresKini = null; set({ ajTtdN: nTitik() }); };
    akar.addEventListener('pointerup', selesai); akar.addEventListener('pointercancel', selesai);
    // foto penerima / barang — peristiwa 'change' (Safari iOS menembakkannya untuk input berkas)
    akar.addEventListener('change', (ev) => { const el = ev.target && ev.target.closest ? ev.target.closest('[data-aj-foto]') : null; if (!el) return;
      fotoDipilih(el).catch((e) => set({ kabar: 'Foto gagal diproses: ' + (e && e.message ? e.message : e), kabarAwas: true })); });
  }
  /** Dipanggil jual.js sesudah tiap gambar: kanvas yang baru dipasang digambar ulang dari goresan yang diingat. */
  function sesudahGambar(akar) { const c = akar.querySelector('canvas[data-ttd]'); if (c) gambarTtd(c); }
  const alatFoto = () => ({
    buka: async (berkas) => {
      if (typeof createImageBitmap === 'function') { try { const g = await createImageBitmap(berkas, { imageOrientation: 'from-image' }); return { lebar: g.width, tinggi: g.height, gambar: g }; } catch (e) { /* jatuh ke <img> */ } }
      const url = URL.createObjectURL(berkas);
      try { const img = await new Promise((jadi, gagal) => { const i = new Image(); i.addEventListener('load', () => jadi(i)); i.addEventListener('error', () => gagal(new Error('gambar tidak terbaca'))); i.src = url; }); return { lebar: img.naturalWidth, tinggi: img.naturalHeight, gambar: img }; }
      finally { setTimeout(() => URL.revokeObjectURL(url), 30000); }
    },
    jpeg: (g, w, t, mutu) => { const c = document.createElement('canvas'); c.width = w; c.height = t; const x = c.getContext('2d'); x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, t); x.drawImage(g, 0, 0, w, t); return c.toDataURL('image/jpeg', mutu); },
  });
  async function fotoDipilih(el) {
    const berkas = (el && el.files && el.files[0]) || null; if (el) el.value = ''; if (!berkas || fotoProses) return;
    fotoProses = true; set({ kabar: 'Mengecilkan foto…', kabarAwas: false });
    try { const hasil = await fbnKecilkan(berkas, alatFoto()); if (hasil.tolak) return set({ kabar: hasil.tolak, kabarAwas: true }); foto = hasil; set({ ajFotoN: (S().ajFotoN || 0) + 1, kabar: 'Foto siap (' + fbnKB(hasil.byte) + ') — tersimpan bersama tanda terima', kabarAwas: false }); }
    finally { fotoProses = false; }
  }

  // ---------- cetak & WhatsApp surat jalan ----------
  function cetakSJ(sj) {
    const atur = ST.stAtur(); const lembar = AJ.ajLembarCetak(sj, atur.kop); const kertas = Number(atur.kertas) === 58 ? 58 : 80;
    // di aplikasi tablet dialog cetak hanya berkelebat lalu hilang (uji owner 20 Nov 2026): katakan terus terang surat jalannya tidak keluar
    const dialog = () => { if (asliAda()) return set({ kabar: 'Surat jalan TIDAK tercetak: di tablet ini hanya keluar lewat printer tablet — periksa di Jual › Struk › "Printer tablet ini", lalu cetak lagi', kabarAwas: true });
      const el = document.getElementById('cetakStruk'); if (!el) return set({ kabar: 'Dialog cetak tidak tersedia di layar ini', kabarAwas: true });
      el.textContent = lembar.map((g) => AJ.ajTeksCetak(g, kertas === 58 ? 32 : 48)).join('\n\n' + '- - potong di sini - -' + '\n\n'); el.className = 'cetak-struk k' + kertas;
      try { window.print(); } catch (e) { set({ kabar: 'Dialog cetak tidak bisa dibuka: ' + (e && e.message ? e.message : e), kabarAwas: true }); } };
    // satu cetakan pada satu waktu: selama cetakan lain belum dikabari printer, surat jalan tidak dikirim (ketukan kedua dulu memutus yang pertama)
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    PR.jalurCetak().then((j) => {
      if (j === 'dialog') return dialog();
      // dua lembar berurutan, masing-masing dipotong printer: lembar pembeli dulu, lalu lembar toko (yang ditandatangani & dibawa pulang)
      let n = 0;
      return lembar.reduce((p, g) => p.then(() => PR.susunCetak(g, { gaya: 'teks' })).then((x) => PR.kirimCetak(x.byte, j)).then(() => { n += 1; }), Promise.resolve())
        .then(() => set({ kabar: 'Surat jalan ' + sj.noSJ + ' dicetak 2 lembar: LEMBAR PEMBELI ditinggal, LEMBAR TOKO ditandatangani penerima & dibawa pulang', kabarAwas: false }))
        .catch((e) => {
          // uji owner 20 Nov 2026: printer diam sesudah data dikirim = hasil lembar itu TIDAK DIKETAHUI, bukan "gagal". Kertasnya dilihat dulu;
          // dialog cetak tidak dibuka sendiri — tombol "cetak" surat jalan tetap ada untuk mengulang.
          if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK + (n ? ' — ' + n + ' lembar sudah keluar' : ''), kabarAwas: true });
          if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-' + (n + 1) + ' dari ' + lembar.length + ' — lihat kertasnya dulu; kalau ada yang tidak keluar, cetak lagi surat jalannya', kabarAwas: true });
          const gagal = PR.sebutPrinter(j) + ' gagal' + (n ? ' sesudah ' + n + ' lembar' : '') + ' (' + (e && e.message ? e.message : e) + ') — ';
          if (asliAda()) return set({ kabar: gagal + 'surat jalan TIDAK tercetak' + (n ? ' lengkap' : '') + '. Bereskan printernya, lalu cetak lagi', kabarAwas: true });
          set({ kabar: gagal + 'dialog cetak dibuka sebagai gantinya', kabarAwas: true }); dialog();
        });
    }).catch(() => dialog());
  }
  function waSJ(sj) {
    const teks = AJ.ajTeksCetak(AJ.ajGarisCetak(sj, ST.stAtur().kop), 32);
    try { const w = window.open(ST.tautanWa(teks), '_blank'); if (w) { try { w.opener = null; } catch (e) { /* abaikan */ } } else set({ kabar: 'WhatsApp ditahan peramban — izinkan jendela baru untuk halaman ini', kabarAwas: true }); }
    catch (e) { set({ kabar: 'WhatsApp tidak bisa dibuka', kabarAwas: true }); }
  }

  // ---------- tulis ----------
  async function tulis(r, sesudah) {
    if (!r || r.tolak) return set({ kabar: (r && r.tolak) || 'Tidak ada yang ditulis', kabarAwas: true });
    try {
      const x = await tulisDokumen(r.dokumen || []);
      if (x && x.gagal) return set({ kabar: 'DITOLAK: ' + (/permission/i.test(x.pesan || '') ? KABAR_PERMISI : x.pesan), kabarAwas: true });
      set(Object.assign({}, r.patch, sesudah || {}, { kabar: kabarKiriman(x, r.patch.kabar), kabarAwas: !!r.patch.kabarAwas }));
    } catch (e) { set({ kabar: 'GAGAL menulis: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  const namaAkun = () => { const a = akun(); return a ? String(a.nama || (a.jenis === 'owner' ? 'Owner' : '')) : ''; };

  const aksi = {
    // ---- draf antar di Bayar
    ajBuat: () => { const tb = tombolAkun(akun(), 'antar'); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true }); set({ antar: AJ.ajDrafBaru(S().pelanggan), kabar: '' }); },
    ajLepas: () => { const s = S(); set({ antar: null, cara: s.antar && s.antar.cod ? 'Tunai' : s.cara, kabar: 'Tidak jadi diantar — nota ini nota biasa', kabarAwas: false }); },
    ajKetik: (v, el) => { const s = S(); if (!s.antar) return; const k = el.dataset.kolom; if (['alamat', 'ongkir', 'catatan'].indexOf(k) < 0 && !(k === 'pengantar' && s.antar.pengantarKetik)) return;
      const o = {}; o[k] = String(v || '').slice(0, k === 'ongkir' ? 12 : k === 'pengantar' ? 30 : 160); set({ antar: Object.assign({}, s.antar, o) }); },
    ajPilih: ({ kolom, n }) => { const s = S(); if (!s.antar || ['pengantar', 'kendaraan'].indexOf(kolom) < 0) return; const o = {}; o[kolom] = s.antar[kolom] === n && kolom === 'kendaraan' ? '' : String(n || ''); if (kolom === 'pengantar') o.pengantarKetik = false; set({ antar: Object.assign({}, s.antar, o) }); },
    // yang mengantar bukan dari daftar (kurir lepas / bukan pegawai tetap): ketik namanya
    ajPengantarLain: () => { const s = S(); if (!s.antar || s.antar.pengantarKetik) return; set({ antar: Object.assign({}, s.antar, { pengantar: '', pengantarKetik: true }), kabar: '' }); },
    ajTarif: () => { const s = S(); if (!s.antar) return; set({ antar: Object.assign({}, s.antar, { ongkir: String(AJ.ajAtur().tarif || '') }) }); },
    ajCod: () => { const s = S(); if (!s.antar) return; if (!s.antar.cod) { const tb = tombolAkun(akun(), 'jualBon'); if (!tb.boleh) return set({ kabar: 'Bayar di tempat dicatat sebagai bon sementara — ' + tb.kalimat, kabarAwas: true }); }
      set(Object.assign(AJ.ajSetelCod(s, !s.antar.cod), { kabar: '' })); },
    // ---- daftar antar
    ajBukaDaftar: () => set({ lembar: 'antar', ajSaring: '', ajAlasan: null, ajSetor: null, kabar: '' }),
    ajSaring: (v) => set({ ajSaring: String(v || '').slice(0, 40) }),
    ajCetak: ({ id }) => { const sj = AJ.ajCari(id); if (sj) cetakSJ(sj); },
    ajWa: ({ id }) => { const sj = AJ.ajCari(id); if (sj) waSJ(sj); },
    // ---- terima
    ajTerimaBuka: ({ id }) => { const tb = tombolAkun(akun(), 'terimaAntar'); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true }); const sj = AJ.ajCari(id); if (!sj) return;
      if (ttdUntuk !== String(id)) { gores = []; foto = null; ttdUntuk = String(id); }
      const K = AJ.ajKeadaan(sj, hari()); set({ lembar: 'antarTerima', ajBuka: String(id), ajTerima: { penerima: '', catatan: '', uang: K.sisaTagih ? String(K.sisaTagih) : '', caraUang: 'Tunai', cara: 'kertas' }, ajTtdN: nTitik(), kabar: '' }); },
    ajCaraTerima: ({ c }) => { const s = S(); if (s.ajTerima) set({ ajTerima: Object.assign({}, s.ajTerima, { cara: c === 'layar' ? 'layar' : 'kertas' }), kabar: '' }); },
    ajTerimaKetik: (v, el) => { const s = S(); const k = el.dataset.kolom; if (!s.ajTerima || ['penerima', 'catatan', 'uang'].indexOf(k) < 0) return; const o = {}; o[k] = String(v || '').slice(0, k === 'uang' ? 12 : 160); set({ ajTerima: Object.assign({}, s.ajTerima, o) }); },
    ajCaraUang: ({ c }) => { const s = S(); if (s.ajTerima) set({ ajTerima: Object.assign({}, s.ajTerima, { caraUang: c === 'QRIS' ? 'QRIS' : 'Tunai' }) }); },
    ajTtdHapus: () => { gores = []; set({ ajTtdN: 0 }); },
    ajFotoHapus: () => { foto = null; set({ ajFotoN: (S().ajFotoN || 0) + 1, kabar: 'Foto dilepas', kabarAwas: false }); },
    ajKembali: () => set({ lembar: 'antar', ajBuka: null, kabar: '' }),
    ajTerimaSimpan: async (d, el) => {
      const s = S(); const sj = AJ.ajCari(s.ajBuka); if (!sj) return set({ kabar: 'Surat jalan tidak ditemukan', kabarAwas: true });
      const kertas = !s.ajTerima || s.ajTerima.cara !== 'layar'; const w = ctx.waktu(); let rt = null;
      if (kertas) { if (!foto) return set({ kabar: 'Foto dulu LEMBAR TOKO yang sudah ditandatangani penerima', kabarAwas: true }); }
      else {
        if (!AJ.ajTtdCukup(nTitik())) return set({ kabar: 'Minta tanda tangan penerima dulu di kotak putih', kabarAwas: true });
        const c = el && el.closest ? (el.closest('.lembar') || document).querySelector('canvas[data-ttd]') : document.querySelector('canvas[data-ttd]');
        if (!c) return set({ kabar: 'Kotak tanda tangan tidak terbaca — buka lagi lembarnya', kabarAwas: true });
        const p = AJ.ajPisahDataUrl(c.toDataURL('image/png'));
        rt = AJ.ajSusunBukti(sj, 'ttd', Object.assign({ lebar: c.width, tinggi: c.height }, p || {}), w); if (rt.tolak) return set({ kabar: rt.tolak, kabarAwas: true });
      }
      const rf = foto ? AJ.ajSusunBukti(sj, 'foto', foto, w, kertas ? 'kertas' : '') : null; if (rf && rf.tolak) return set({ kabar: rf.tolak, kabarAwas: true });
      // uang & bentuk tanda terima diperiksa DULU (sebelum bukti dikirim) — bukti tanpa tanda terima tidak pernah dikirim untuk isian yang pasti ditolak
      const isi = Object.assign({}, s.ajTerima || {}, { cara: kertas ? 'kertas' : 'layar', ttdId: rt ? rt.data.id : '', fotoId: rf ? rf.data.id : '', oleh: namaAkun() });
      const r = AJ.ajSusunTerima(sj, isi, w); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      const daftar = (rt ? [rt.data] : []).concat(rf ? [rf.data] : []);
      set({ kabar: 'Menyimpan ' + (kertas ? 'foto lembar bertanda tangan' : 'tanda tangan' + (rf ? ' & foto' : '')) + '…', kabarAwas: false });
      const x = buktiServer() ? await ctx.bukti.simpan(daftar) : { ok: true, simulasi: true };
      if (x && x.gagal) return set({ kabar: 'Tanda terima TIDAK tersimpan: ' + (/permission/i.test(x.pesan || '') ? KABAR_PERMISI : x.pesan), kabarAwas: true });
      if (x && x.simulasi) sim[sj.id] = (sim[sj.id] || []).concat(daftar);
      gores = []; foto = null; ttdUntuk = '';
      await tulis(r, { lembar: 'antar', ajBuka: null, ajTerima: null, ajTtdN: 0 });
      if (x && x.antre) set({ kabar: S().kabar + ' · ' + (kertas ? 'foto lembar' : 'tanda tangan' + (rf ? ' & foto' : '')) + ' BELUM sampai server (sinyal lambat) — terkirim sendiri begitu tersambung', kabarAwas: true });
    },
    // ---- gagal antar · batal (owner) · setor menyusul
    ajAlasanBuka: ({ id, jenis }) => { const tb = jenis === 'batal' ? (bukanOwner(akun()) ? { boleh: false, kalimat: 'Membatalkan surat jalan = owner' } : { boleh: true }) : tombolAkun(akun(), 'terimaAntar');
      if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true }); set({ ajAlasan: { id: String(id), jenis: jenis === 'batal' ? 'batal' : 'gagal', teks: '' }, ajSetor: null }); },
    ajAlasanKetik: (v) => { const s = S(); if (s.ajAlasan) set({ ajAlasan: Object.assign({}, s.ajAlasan, { teks: String(v || '').slice(0, 160) }) }); },
    ajAlasanTutup: () => set({ ajAlasan: null }),
    ajAlasanSimpan: () => { const s = S(); const A = s.ajAlasan; if (!A) return; const sj = AJ.ajCari(A.id); const w = ctx.waktu();
      tulis(A.jenis === 'batal' ? AJ.ajSusunBatal(sj, A.teks, w) : AJ.ajSusunGagal(sj, A.teks, w, namaAkun()), { ajAlasan: null }); },
    ajSetorBuka: ({ id }) => { const tb = tombolAkun(akun(), 'terimaBon'); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true }); const sj = AJ.ajCari(id); if (!sj) return;
      set({ ajSetor: { id: String(id), uang: String(AJ.ajKeadaan(sj, hari()).sisaTagih || ''), caraUang: 'Tunai' }, ajAlasan: null }); },
    ajSetorKetik: (v) => { const s = S(); if (s.ajSetor) set({ ajSetor: Object.assign({}, s.ajSetor, { uang: String(v || '').slice(0, 12) }) }); },
    ajSetorCara: ({ c }) => { const s = S(); if (s.ajSetor) set({ ajSetor: Object.assign({}, s.ajSetor, { caraUang: c === 'QRIS' ? 'QRIS' : 'Tunai' }) }); },
    ajSetorTutup: () => set({ ajSetor: null }),
    ajSetorSimpan: () => { const s = S(); const X = s.ajSetor; if (!X) return; tulis(AJ.ajSusunSetor(AJ.ajCari(X.id), X, ctx.waktu()), { ajSetor: null }); },
    // gagal antar → owner membatalkan nota (Riwayat) atau mencatat retur: buka Retur atas baris pertama notanya
    ajKeRetur: ({ id }) => { const sj = AJ.ajCari(id); if (!sj) return; const b = (ambilPenjualanSemua() || []).find((p) => String(p.trxId || '') === String(sj.trxIdJual) && !p.dibatalkan);
      if (!b) return set({ kabar: 'Baris nota surat jalan ini tidak ditemukan (sudah dibatalkan?)', kabarAwas: true }); if (ctx.tunjukNota) ctx.tunjukNota(b.id); },
    // ---- lihat bukti (dibaca sekali dari server)
    ajBuktiBuka: async ({ id }) => {
      if (lihat.id === String(id) && lihat.muat !== 'galat') { lihat = { id: '', muat: '', daftar: [], pesan: '' }; return set({ ajFotoN: (S().ajFotoN || 0) + 1 }); }
      lihat = { id: String(id), muat: 'baca', daftar: [], pesan: '' }; set({ ajFotoN: (S().ajFotoN || 0) + 1 });
      if (!buktiServer()) { lihat = { id: String(id), muat: 'ada', daftar: sim[id] || [], pesan: 'SIMULASI — bukti hanya di memori layar ini' }; return set({ ajFotoN: (S().ajFotoN || 0) + 1 }); }
      try { const d = await ctx.bukti.baca(id); if (lihat.id !== String(id)) return; lihat = { id: String(id), muat: 'ada', daftar: d || [], pesan: '' }; }
      catch (e) { const k = String((e && (e.code || e.message)) || e); lihat = { id: String(id), muat: 'galat', daftar: [], pesan: /permission/i.test(k) ? KABAR_PERMISI : 'Bukti belum bisa dibaca: ' + k }; }
      set({ ajFotoN: (S().ajFotoN || 0) + 1 });
    },
  };

  // ---------- gambar ----------
  /** Bagian Antar di lembar Bayar (draf antar milik keranjang ini). t = hitungTagihan. */
  function gambarBayar(s, t) {
    if (s.karcis || s.tukar) return '';
    const a = s.antar; const tb = tombolAkun(akun(), 'antar');
    if (!a) return tb.boleh ? h`<div class="kaca-btn putus" data-aksi="ajBuat" data-k="aj-buat">Antar ke pembeli · surat jalan</div>` : '';
    const A = AJ.ajAtur(); const ongkirSah = AJ.ajRupiahSah(a.ongkir) !== null;
    const pil = (kolom, daftar) => h`<div class="bendera">${daftar.map((nm) => h`<span class="pil ${a[kolom] === nm ? 'nyala' : ''}" data-aksi="ajPilih" data-kolom="${kolom}" data-n="${nm}" data-k="aj-${kolom}-${nm}">${nm}</span>`)}</div>`;
    return h`<div class="kartu" data-k="aj-bayar" style="gap: 6px;">
      <div style="display: flex; justify-content: space-between; align-items: baseline; gap: 8px;"><span class="label">Diantar · surat jalan lahir bersama nota ini</span><span class="ket tautan" data-aksi="ajLepas">tidak jadi antar</span></div>
      <input class="ketik-nama" type="text" value="${a.alamat}" data-ketik="ajKetik" data-kolom="alamat" data-k="aj-alamat" placeholder="Alamat antar${s.pelanggan ? '' : ' (pilih nama pembeli → alamat kartunya terisi)'}">
      <div class="ps-form dua">
        <div><div class="ket">Ongkir (Rp) · 0 = gratis${A.tarif ? h` · <span class="tautan" data-aksi="ajTarif">tarif ${RP(A.tarif)}</span>` : ''}</div><input class="ketik-nama" type="text" inputmode="numeric" value="${a.ongkir}" data-ketik="ajKetik" data-kolom="ongkir" data-k="aj-ongkir" placeholder="0"></div>
        <div><div class="ket">Catatan untuk pengantar</div><input class="ketik-nama" type="text" value="${a.catatan}" data-ketik="ajKetik" data-kolom="catatan" data-k="aj-catatan" placeholder="mis. taruh di dapur"></div>
      </div>
      ${ongkirSah ? (t.ongkir ? h`<div class="ket">ongkir ${RP(t.ongkir)} masuk nota sebagai baris sendiri (bukan jualan beras)</div>` : '') : h`<div class="ket awas-teks">Ongkir: ketik angka rupiah (0 – ${RP(AJ.AJ_TARIF_MAKS)})</div>`}
      <div class="label">Yang mengantar</div>${gambarPengantar(a, A)}
      ${A.kendaraan.length ? h`<div class="label">Kendaraan</div>${pil('kendaraan', A.kendaraan)}` : ''}
      <div class="tombol-baris"><div class="kaca-btn ${a.cod ? 'aktif emas' : ''}" data-aksi="ajCod" data-k="aj-cod">${a.cod ? '✓ Bayar di tempat' : 'Bayar di tempat'}</div></div>
      ${a.cod ? h`<div class="pita-info emas" data-k="aj-cod-pita">BAYAR DI TEMPAT — nota dicatat sekarang sebagai bon sementara atas nama ${s.pelanggan || '… (pilih nama pembelinya)'}; ${a.pengantar || 'pengantar'} menagih ${RP(Math.max(0, t.total))} dan membawa uangnya pulang. Bebas batas kredit hari ini; kalau sampai tutup hari uangnya belum disetor, Dasbor & tutup hari memerah.</div>` : ''}
    </div>`;
  }
  /** Pilihan yang mengantar: daftar Atur + yang pernah mengantar (kurir lepas) + "orang lain" (ketik nama). */
  function gambarPengantar(a, A) {
    const P = AJ.ajPilihanPengantar(hari()); const ketik = !!a.pengantarKetik;
    const pilN = (nm) => h`<span class="pil ${!ketik && a.pengantar === nm ? 'nyala' : ''}" data-aksi="ajPilih" data-kolom="pengantar" data-n="${nm}" data-k="aj-pengantar-${nm}">${nm}</span>`;
    const luar = !ketik && a.pengantar && A.pengantar.indexOf(a.pengantar) < 0;
    return h`<div class="bendera">${P.tetap.map(pilN)}${P.lain.map(pilN)}<span class="pil ${ketik ? 'nyala' : ''}" data-aksi="ajPengantarLain" data-k="aj-pengantar-lain">+ orang lain</span></div>
      ${ketik ? h`<input class="ketik-nama" type="text" value="${a.pengantar}" data-ketik="ajKetik" data-kolom="pengantar" data-k="aj-pengantar-ketik" maxlength="30" placeholder="Nama yang mengantar (kurir lepas / bukan pegawai tetap)">` : ''}
      ${ketik || luar ? h`<div class="ket">bukan pegawai tetap — tidak perlu akun: tanda terimanya ditandai di toko (lembar toko difoto)${a.cod ? '; uang bayar di tempat tercatat dibawa ' + (a.pengantar || 'dia') : ''}. Nama ini muncul lagi sebagai pilihan selama ${AJ.AJ_PENGANTAR_INGAT_HARI} hari.</div>` : ''}`;
  }
  /** Tombol daftar Antar di bilah Jual: jumlah yang masih di jalan + bayar di tempat yang belum pulang. */
  function tombolDaftar() {
    const D = AJ.ajDaftar(hari(), ''); const n = D.jalan.length; const cod = D.codBelum.length;
    return h`<div class="kaca-btn ${n || cod ? 'aktif' : ''} ${cod ? 'awas' : ''}" data-aksi="ajBukaDaftar" data-k="aj-tombol">Antar${n ? ' · ' + n : ''}${cod ? ' · ' + cod + ' belum setor' : ''}</div>`;
  }
  function kartuSJ(s, x, owner, bolehTandai) {
    const al = s.ajAlasan && s.ajAlasan.id === String(x.id) ? s.ajAlasan : null; const se = s.ajSetor && s.ajSetor.id === String(x.id) ? s.ajSetor : null;
    const L = lihat.id === String(x.id) ? lihat : null;
    return h`<div class="ps-kartu" data-k="aj-${x.id}">
      <div class="atas"><b>${x.namaPelanggan || 'tanpa nama'}</b><span class="pil ${x.status === 'berangkat' ? 'status-diantar' : x.status === 'gagal' ? 'status-diantar ng-awas' : ''}">${x.noSJ} · ${x.statusTeks}</span></div>
      <div class="isi">${isiRingkas(x)}</div>
      <div class="ket">${x.alamat || 'tanpa alamat'} · ${x.pengantar || '—'}${x.kendaraan ? ' · ' + x.kendaraan : ''} · ${tanggalPendek(x.tanggal)} ${x.jam || ''}${x.ongkir ? ' · ongkir ' + RP(x.ongkir) : ''}${x.catatan ? ' · ' + x.catatan : ''}</div>
      ${x.bayarDiTempat ? h`<div class="ket ${x.sisaTagih > 0 ? 'awas-teks' : ''}">bayar di tempat ${RP(x.tagihRp)}${x.dibayar ? ' · sudah ' + RP(x.dibayar) : ''}${x.sisaTagih > 0 ? ' · BELUM SETOR ' + RP(x.sisaTagih) + (x.lewatHari ? ' (lewat hari — kini bon biasa)' : '') : ' · lunas'}</div>` : ''}
      ${x.status === 'diterima' ? h`<div class="ket">diterima ${x.penerima ? x.penerima + ' · ' : ''}${tanggalPendek(x.diterimaTanggal || x.tanggal)} ${x.diterimaJam || ''}${x.ditandaiOleh ? ' · ditandai ' + x.ditandaiOleh : ''}${AJ.ajCaraTerima(x) === 'kertas' ? ' · tanda tangan di kertas (foto lembar)' : (x.buktiFoto || []).length ? '' : ' · tanpa foto'}${x.catatanTerima ? ' · ' + x.catatanTerima : ''}</div>` : ''}
      ${x.status === 'gagal' ? h`<div class="ket awas-teks">gagal antar: ${x.alasanGagal || '—'}${x.gagalBelumBeres ? ' — notanya masih berlaku: owner membatalkan nota (hari ini) atau mencatat retur' : ''}</div>` : ''}
      ${x.status === 'batal' ? h`<div class="ket">dibatalkan${x.alasanBatal ? ': ' + x.alasanBatal : ''}</div>` : ''}
      ${x.notaBatalSuratJalan ? h`<div class="ket awas-teks">notanya sudah dibatalkan — surat jalan ini ikut dibatalkan owner</div>` : ''}
      <div class="aksi">
        ${x.status === 'berangkat' && bolehTandai ? h`<span class="pil utamaKecil" data-aksi="ajTerimaBuka" data-id="${x.id}">diterima →</span><span class="pil" data-aksi="ajAlasanBuka" data-id="${x.id}" data-jenis="gagal">gagal antar</span>` : ''}
        ${x.sisaTagih > 0 && x.status !== 'berangkat' ? h`<span class="pil utamaKecil" data-aksi="ajSetorBuka" data-id="${x.id}">uang disetor →</span>` : ''}
        ${x.status === 'gagal' && x.gagalBelumBeres && owner ? h`<span class="pil" data-aksi="ajKeRetur" data-id="${x.id}">catat retur</span>` : ''}
        ${x.status === 'diterima' ? h`<span class="pil" data-aksi="ajBuktiBuka" data-id="${x.id}">${L ? 'tutup bukti' : 'lihat bukti'}</span>` : ''}
        <span class="pil" data-aksi="ajCetak" data-id="${x.id}">cetak</span><span class="pil" data-aksi="ajWa" data-id="${x.id}">WA</span>
        ${owner && x.status !== 'batal' ? h`<span class="pil" data-aksi="ajAlasanBuka" data-id="${x.id}" data-jenis="batal">batalkan</span>` : ''}
      </div>
      ${al ? h`<div class="ps-form" data-k="aj-alasan-${x.id}"><input class="ketik-nama" type="text" value="${al.teks}" data-ketik="ajAlasanKetik" placeholder="${al.jenis === 'batal' ? 'Alasan membatalkan surat jalan (nota tidak berubah)' : 'Kenapa gagal? (mis. toko tutup, alamat tidak ketemu)'}">
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="ajAlasanTutup">tidak jadi</div><div class="kaca-btn ${al.jenis === 'batal' ? 'awas' : 'aktif'}" data-aksi="ajAlasanSimpan">${al.jenis === 'batal' ? 'BATALKAN SURAT JALAN' : 'CATAT GAGAL ANTAR'}</div></div></div>` : ''}
      ${se ? h`<div class="ps-form" data-k="aj-setor-${x.id}"><div class="ket">Uang bayar di tempat yang dibawa pulang ${x.pengantar || 'pengantar'}</div><input class="ketik-nama" type="text" inputmode="numeric" value="${se.uang}" data-ketik="ajSetorKetik" placeholder="Rp">
        <div class="tombol-baris">${['Tunai', 'QRIS'].map((c) => h`<div class="kaca-btn ${se.caraUang === c ? 'aktif' : ''}" data-aksi="ajSetorCara" data-c="${c}">${c}</div>`)}</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="ajSetorTutup">tidak jadi</div><div class="kaca-btn aktif" data-aksi="ajSetorSimpan">CATAT UANG MASUK</div></div></div>` : ''}
      ${L ? h`<div class="aj-bukti" data-k="aj-bukti-${x.id}">${L.muat === 'baca' ? h`<div class="ket">membaca bukti…</div>` : L.muat === 'galat' ? h`<div class="ket awas-teks">${L.pesan}</div>`
        : L.daftar.length ? L.daftar.map((d) => h`<div class="ket">${d.jenisBukti === 'ttd' ? 'tanda tangan' : d.isiBukti === 'kertas' ? 'foto lembar bertanda tangan' : 'foto'} · ${d.jam || ''}</div><img alt="${d.jenisBukti === 'ttd' ? 'tanda tangan penerima' : d.isiBukti === 'kertas' ? 'foto lembar surat jalan bertanda tangan' : 'foto antar'}" src="${fbnSrc(d)}" style="max-width: 100%; border-radius: 8px; background: #fff;">`) : h`<div class="ket">Belum ada bukti di server${L.pesan ? ' · ' + L.pesan : ''}</div>`}</div>` : ''}
    </div>`;
  }
  /** Lembar daftar Antar & lembar Terima. kepala(judul, ket), L1 = tirai. */
  function gambarLembar(s, muncul, kepala, L1) {
    const a = akun(); const owner = !bukanOwner(a); const bolehTandai = tombolAkun(a, 'terimaAntar').boleh;
    if (s.lembar === 'antar') {
      const D = AJ.ajDaftar(hari(), s.ajSaring);
      const bagian = (judul, daftar, kosong) => h`<div class="label">${judul}</div><div class="daftar-nama">${daftar.map((x) => kartuSJ(s, x, owner, bolehTandai))}${daftar.length ? '' : h`<div class="ket" style="padding: 6px 4px;">${kosong}</div>`}</div>`;
      const gagal = D.gagal.filter((x) => D.jalan.indexOf(x) < 0); const cod = D.codBelum.filter((x) => gagal.indexOf(x) < 0);
      const selesai = D.selesaiHariIni.filter((x) => cod.indexOf(x) < 0 && gagal.indexOf(x) < 0);
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-antar">
        ${kepala('Antar', D.jalan.length + ' di jalan' + (D.codBelum.length ? ' · ' + D.codBelum.length + ' bayar di tempat belum setor' : '') + ' · surat jalan lahir bersama notanya (Bayar › Antar)')}
        <input class="ketik-nama" type="text" value="${s.ajSaring || ''}" data-ketik="ajSaring" placeholder="saring nama pembeli / no. surat jalan / pengantar">
        ${AJ.ajKalimatCod(AJ.ajCodBelumSetor(hari(), true)) ? h`<div class="pita-info awas" data-k="aj-cod-merah">${AJ.ajKalimatCod(AJ.ajCodBelumSetor(hari(), true))}</div>` : ''}
        ${bagian('Di jalan', D.jalan, 'Tidak ada yang sedang diantar.')}
        ${cod.length ? bagian('Bayar di tempat — uangnya belum pulang', cod, '') : ''}
        ${gagal.length ? bagian('Gagal antar — perlu dibereskan owner', gagal, '') : ''}
        ${bagian('Selesai hari ini', selesai, 'Belum ada.')}
      </div>`;
    }
    if (s.lembar === 'antarTerima') {
      const sj = AJ.ajCari(s.ajBuka);
      if (!sj) return h`${L1}<div class="lembar ${muncul}" data-k="lembar-antarTerima">${kepala('Tanda terima', '')}<div class="ket">Surat jalan tidak ditemukan.</div><div class="kaca-btn" data-aksi="ajKembali">kembali ke daftar Antar</div></div>`;
      const K = AJ.ajKeadaan(sj, hari()); const T = s.ajTerima || { penerima: '', catatan: '', uang: '', caraUang: 'Tunai', cara: 'kertas' }; const kertas = T.cara !== 'layar';
      const cukup = kertas ? !!foto : AJ.ajTtdCukup(s.ajTtdN || 0);
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-antarTerima">
        ${kepala('Tanda terima · ' + sj.noSJ, (sj.namaPelanggan || 'tanpa nama') + (sj.alamat ? ' · ' + sj.alamat : ''))}
        <div class="ket">${isiRingkas(sj)}</div>
        <input class="ketik-nama" type="text" value="${T.penerima}" data-ketik="ajTerimaKetik" data-kolom="penerima" placeholder="Nama yang menerima (boleh kosong)">
        <div class="label">Tanda tangan penerima</div>
        <div class="tombol-baris">${Object.keys(AJ.AJ_CARA_TERIMA).map((c) => h`<div class="kaca-btn ${(c === 'layar') === !kertas ? 'aktif' : ''}" data-aksi="ajCaraTerima" data-c="${c}" data-k="aj-cara-${c}">${c === 'kertas' ? 'di kertas (dibawa pulang)' : 'di layar ini'}</div>`)}</div>
        ${kertas ? h`<div class="ket ${foto ? '' : 'awas-teks'}" data-k="aj-kertas">${foto ? 'foto lembar siap' : 'foto LEMBAR TOKO yang sudah ditandatangani penerima — wajib, kertas termal bisa pudar'}</div>
          <div class="tombol-baris"><label class="kaca-btn ${foto ? '' : 'aktif'}" for="ajFotoKamera">${foto ? 'ganti foto lembar' : 'foto lembar bertanda tangan'}</label>${foto ? h`<div class="kaca-btn putus" data-aksi="ajFotoHapus">lepas foto (${fbnKB(foto.byte)})</div>` : ''}</div>`
        : h`<div style="display: flex; justify-content: flex-end;"><span class="ket tautan" data-aksi="ajTtdHapus">hapus, ulangi</span></div>
        <canvas class="ttd-kanvas" data-ttd="1" data-k="ttd-${sj.id}" width="640" height="240" style="width: 100%; height: 180px; touch-action: none; background: #ffffff; border-radius: 10px; display: block;"></canvas>
        <div class="ket ${cukup ? '' : 'awas-teks'}">${cukup ? 'tanda tangan siap' : 'minta penerima tanda tangan di kotak putih (jari / pena)'}</div>
        <div class="label">Foto (boleh dilewati)</div>
        <div class="tombol-baris"><label class="kaca-btn" for="ajFotoKamera">${foto ? 'ganti foto' : 'foto barang / penerima'}</label>${foto ? h`<div class="kaca-btn putus" data-aksi="ajFotoHapus">lepas foto (${fbnKB(foto.byte)})</div>` : ''}</div>`}
        <input id="ajFotoKamera" type="file" accept="image/*" capture="environment" data-aj-foto="1" hidden>
        ${sj.bayarDiTempat ? h`<div class="label">Uang bayar di tempat · ditagih ${RP(K.sisaTagih)}</div>
          <input class="ketik-nama" type="text" inputmode="numeric" value="${T.uang}" data-ketik="ajTerimaKetik" data-kolom="uang" placeholder="Rp (0 = belum dibayar, tetap bon)">
          <div class="tombol-baris">${['Tunai', 'QRIS'].map((c) => h`<div class="kaca-btn ${T.caraUang === c ? 'aktif' : ''}" data-aksi="ajCaraUang" data-c="${c}">${c}</div>`)}</div>` : ''}
        <input class="ketik-nama" type="text" value="${T.catatan}" data-ketik="ajTerimaKetik" data-kolom="catatan" placeholder="Catatan (mis. ada 1 karung kembali — owner mencatat retur)">
        <div class="utama ${cukup ? '' : 'redup'}" data-aksi="ajTerimaSimpan">${cukup ? 'SIMPAN · DITERIMA' : kertas ? 'Foto lembar dulu' : 'Tanda tangan dulu'}</div>
        <div class="kaca-btn" data-aksi="ajKembali">kembali ke daftar Antar</div>
      </div>`;
    }
    return '';
  }
  return { aksi, pasang, sesudahGambar, gambarBayar, gambarLembar, tombolDaftar };
}
