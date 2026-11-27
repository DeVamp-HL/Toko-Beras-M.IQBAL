// DASBOR OWNER — KISI KARTU BERPEGANGAN (owner 26 Nov 2026: sensus ulang 1c B88–B91 B95 B109 + tata letak). Dipasang dasbor.js di akar yang sama; angka dari
// dasbor-logika.js & dasbor-widget-logika.js (satu sumber). Di sini cuma kisi, pegangan, ketukan & gerak.
//
// Keputusan owner (kata owner): "besar kecilnya kartu bisa gua sesuaikan seperti screenshot 3 (kotak berpegangan). Jadi fleksibel gua menyesuaikan ruang.
// Bukan hanya klik jadi besar atau kecil." · "Merapat otomatis" · "HP satu kolom".
//   · Tiap kartu Dasbor (kartu lama utuh) & widget tambahan = PANEL di kisi 12 kolom (baris 8 px). Lebar w kolom, tinggi h baris (null = setinggi isinya — diukur
//     sesudah digambar, ResizeObserver menjaga). Kisi CSS grid `dense` → panel merapat sendiri mengisi celah.
//   · Mode atur (tekan lama / tombol Atur): pegangan KANAN (lebar), BAWAH (tinggi), SUDUT (dua-duanya) — ditarik, mengunci ke kisi, ukurannya tampil; seret badan
//     panel = pindah (geser FLIP); × hapus; "tinggi otomatis" = kembali setinggi isi; "+ Tambah" (Kartu Dasbor · Kartu tambahan · Angka); Kembalikan bawaan; Batal.
//     "Selesai" menyimpan SEKALI (opsi.simpanWidget → aturanToko/dasbor, owner saja, ikut ke semua perangkat owner).
//   · HP (< 720 px): satu kolom, urutan sama, tinggi ikut isi (ukuran tarikan hanya Mac / tablet). Perlu perhatian disembunyikan dari Dasbor (owner: "ganggu").
// prefers-reduced-motion dihormati (ringkasan.css). Satu-satunya tulisan: susunan lewat opsi.simpanWidget. Angka yang berubah berkilau lewat Web Animations
// (markup tidak berubah → gambar yang hidup = gambar segar).
import { esc } from '../inti/dom.js';
import { RP, DESIMAL, tanggalPendek, hariIniIso } from '../inti/format.js';
import { DB_PERIODE, dbHeadline, dbPeriode, dbSaring, DB_SARING_TETAP } from './dasbor-logika.js';
import { WG_KOLOM, WG_BARIS_PX, WG_BAWAAN, wgAtur, wgSusun, wgPindah, wgHapus, wgTambah, wgUkur, wgTinggiOtomatis, wgBelumDipasang, wgSama } from './dasbor-widget-logika.js';

const KUNCI_PERIODE = 'miqbal_baru_dasbor_periode';
const TEKAN_LAMA = 520;   // ms: tekan lama = mode atur (seperti layar HP)
const GESER_BATAL = 9;    // px: jari bergeser sebelum tekan lama = menggulir, bukan mengatur
const JARAK = 10;         // px: jarak antar panel (margin bawah panel; kolom memakai column-gap yang sama)
const dkPct = (x) => (x === null || x === undefined || !isFinite(x) ? '' : (x < 0 ? '−' : x > 0 ? '+' : '') + DESIMAL(Math.round(Math.abs(x) * 10) / 10) + '%');
const gerakDiam = () => { try { return document.hidden || matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return true; } };
const sempit = () => { try { return matchMedia('(max-width: 719px)').matches; } catch (e) { return false; } };

/** opsi: { kini(), ingat(kunci, f), simpanWidget(daftar) → { ok, kabar }, keTujuan(t), daftar(id, isi) → atribut tooltip Dasbor, kartuPenuh(id) → html, gambarUlang() } */
export function pasangKisi(akar, opsi) {
  let pil = (() => { try { const x = JSON.parse(localStorage.getItem(KUNCI_PERIODE) || 'null'); return x && DB_PERIODE.some((p) => p[0] === x.id) ? x : { id: 'hari' }; } catch (e) { return { id: 'hari' }; } })();
  let D = null, perhatian = [], cap = null, atur = null, tambahBuka = false, simpanJalan = false, kabar = '', kabarAwas = false;
  const nilaiLama = {}; let tekan = null, seret = null, tarik = null, pengamat = null; let ujung = {};
  const daftarAktif = () => (atur ? atur.daftar : wgAtur().daftar);

  // ---------- kepala & bilah atur ----------
  const htmlCap = () => (cap ? '<span class="db-cap' + (cap.awas ? ' awas' : '') + (cap.hidup ? ' hidup' : '') + '" title="' + esc(cap.judul || '') + '"><i></i>' + esc(cap.teks) + '</span>' : '');
  function htmlKepala() {
    const A = wgAtur();
    return '<div class="wg-kepala" data-k="wg-kepala"><div class="label">Dasbor</div><div class="ket">' + esc(atur ? 'tarik pegangan kanan / bawah / sudut untuk mengubah ukuran · seret kartu untuk memindah · × hapus' : (A.dariOwner ? 'susunan lu' : 'susunan bawaan') + ' · tekan lama kartu (atau Atur) untuk mengubah ukuran & tempat')
      + '</div>' + (atur ? '' : htmlCap()) + (atur ? '' : '<div class="kaca-btn kecil" data-da-aksi="cetak" data-k="wg-tombol-cetak" title="Cetak Dasbor · A4 tegak">Cetak</div>')   // P3 B104 (owner 27 Nov 2026: A4 tegak)
      + '<div class="kaca-btn kecil' + (atur ? ' aktif emas' : '') + '" data-da-aksi="' + (atur ? 'selesai' : 'atur') + '" data-k="wg-tombol-atur">' + (atur ? (simpanJalan ? 'menyimpan…' : 'Selesai') : 'Atur') + '</div></div>';
  }
  function htmlBilahAtur() {
    if (!atur) return kabar ? '<div class="ket' + (kabarAwas ? ' awas-teks' : '') + '" data-k="wg-kabar">' + esc(kabar) + '</div>' : '';
    const belum = wgBelumDipasang(atur.daftar); const kelompok = [['lama', 'Kartu Dasbor'], ['kartu', 'Kartu tambahan'], ['angka', 'Angka']];
    return '<div class="wg-bilah-atur" data-k="wg-bilah-atur"><div class="kaca-btn kecil' + (tambahBuka ? ' aktif' : '') + '" data-da-aksi="tambah">+ Tambah kartu</div><div class="kaca-btn kecil" data-da-aksi="bawaan">Kembalikan bawaan</div>'
      + '<div class="kaca-btn kecil" data-da-aksi="batal">Batal</div></div>' + (kabar ? '<div class="ket' + (kabarAwas ? ' awas-teks' : '') + '">' + esc(kabar) + '</div>' : '')
      + (tambahBuka ? '<div class="wg-katalog-wadah" data-k="wg-katalog">' + (belum.length ? kelompok.map(([j, nm]) => { const isi = belum.filter((k) => k.jenis === j); return isi.length ? '<div class="db-sub">' + esc(nm) + '</div><div class="wg-katalog">'
        + isi.map((k, i) => '<div class="wg-katalog-isi" data-wg-tambah="' + esc(k.id) + '" style="--i:' + i + '"><b>' + esc(k.nama) + '</b><span>' + k.w + ' dari ' + WG_KOLOM + ' kolom · ketuk untuk menambah</span></div>').join('') + '</div>' : ''; }).join('')
        : '<div class="menolak">Semua kartu sudah terpasang.</div>') + '</div>' : '');
  }

  // ---------- isi panel ----------
  function htmlTren(T) {
    const n = T.length; if (!n) return ''; const ada = T.filter((x) => x.n !== null); const maks = Math.max(1, ...ada.map((x) => Math.abs(x.n))); const minus = ada.some((x) => x.n < 0);
    const nol = minus ? 50 : 100; const sk = minus ? 48 : 96;
    return '<svg class="wg-tren" viewBox="0 0 ' + (n * 10) + ' 100" preserveAspectRatio="none" aria-hidden="true"><line class="db-dasar" x1="0" y1="' + nol + '" x2="' + (n * 10) + '" y2="' + nol + '"></line>'
      + T.map((x, i) => { if (x.n === null) return '<rect class="db-rel" x="' + (i * 10 + 2) + '" y="' + (nol - 1) + '" width="6" height="1"></rect>'; const hh = Math.max(1.5, Math.abs(x.n) / maks * sk);
        return '<rect class="db-tumbuh-y ' + (x.n < 0 ? 'wg-minus' : 'wg-plus') + (x.berjalan ? ' berjalan' : '') + '" style="--i:' + i + '" x="' + (i * 10 + 1.5) + '" y="' + (x.n < 0 ? nol : nol - hh).toFixed(2) + '" width="7" height="' + hh.toFixed(2) + '"></rect>'; }).join('')
      + '</svg><div class="wg-sumbu">' + T.map((x) => '<span class="' + (x.berjalan ? 'aktif' : '') + '">' + esc(x.label) + '</span>').join('') + '</div>';
  }
  /** Widget-angka & kartu tambahan ringkas (Perlu perhatian): angka besar + keterangan (+ bilah, tren & baris kalau panelnya lebar). */
  function htmlRingkas(w) {
    const lebar = w.w >= 5 || sempit(); const tip = w.jenis === 'angka' && !atur ? opsi.daftar('wg:' + w.id, { judul: w.nama, baris: (w.rinci || []).slice(0, 8).concat(w.rinci && w.rinci.length ? [] : [['', w.ket || '']]), tujuan: w.tujuan, ke: 'layar sumbernya' }) : '';
    const baris = w.jenis === 'kartu' ? (w.baris || []) : lebar ? (w.rinci || []).slice(0, 5) : [];
    return '<div class="wg' + (w.awas ? ' awas' : '') + (w.lampu ? ' lampu-' + esc(w.lampu) : '') + '"' + tip + '>'
      + '<div class="wg-nama">' + (w.lampu ? '<i class="db-lampu ' + esc(w.lampu) + '"></i>' : '') + esc(w.nama) + '</div>'
      + '<div class="wg-nilai angka' + (w.awas ? ' awas-teks' : '') + '">' + esc(w.nilai) + '</div>' + (w.ket ? '<div class="wg-ket">' + esc(w.ket) + '</div>' : '')
      + (w.bilah !== undefined && w.bilah !== null ? '<div class="wg-bilah"><i class="db-tumbuh-x" style="width: ' + (w.bilah * 100).toFixed(1) + '%;"></i></div>' : '')
      + (w.tren && lebar ? htmlTren(w.tren) : '') + (baris.length ? '<div class="wg-rinci">' + baris.map((r) => '<div><span>' + esc(r[0]) + '</span><b>' + esc(r[1]) + '</b></div>').join('') + '</div>' : '') + '</div>';
  }
  function htmlIsi(w) {
    if (w.id === 'kHeadline') return htmlHeadline();
    if (w.id === 'kPeriode') return htmlPeriode();
    if (w.jenis === 'lama' || w.id === 'kEnam') { const k = opsi.kartuPenuh(w.id); return k || '<div class="kartu db-kartu"><div class="label">' + esc(w.nama) + '</div><div class="menolak">Kartu ini sedang tidak punya isi.</div></div>'; }
    return htmlRingkas(w);
  }
  function htmlPanel(w, i) {
    const gaya = 'grid-column: span ' + w.w + ';' + (w.h ? ' grid-row-end: span ' + w.h + ';' : '');
    const pegangan = atur ? '<div class="pn-tarik pn-kanan" data-pn-tarik="w" data-i="' + i + '" aria-label="Tarik untuk mengubah lebar"></div><div class="pn-tarik pn-bawah" data-pn-tarik="h" data-i="' + i + '" aria-label="Tarik untuk mengubah tinggi"></div>'
      + '<div class="pn-tarik pn-sudut" data-pn-tarik="wh" data-i="' + i + '" aria-label="Tarik untuk mengubah lebar & tinggi"></div>'
      + '<div class="wg-x" data-wg-hapus="' + i + '" role="button" aria-label="Hapus ' + esc(w.nama) + '">×</div>'
      + '<div class="pn-ukuran" data-k="pn-ukuran-' + esc(w.id) + '">' + w.w + '/' + WG_KOLOM + ' · ' + (w.h ? Math.round(w.h * WG_BARIS_PX) + ' px' : 'tinggi otomatis') + '</div>'
      + (w.h ? '<div class="pn-otomatis" data-pn-otomatis="' + i + '" role="button">tinggi otomatis</div>' : '') : '';
    return '<div class="pn pn-' + esc(w.jenis) + (w.h ? ' pn-tetap' : ' pn-auto') + '" data-pn="' + esc(w.id) + '" data-i="' + i + '" data-nilai="' + esc(w.nilai || '') + '" style="' + gaya + ' --i:' + i + '" data-k="pn-' + esc(w.id) + '">'
      + htmlIsi(w) + pegangan + '</div>';
  }

  // ---------- B94 (owner 27 Nov 2026): SATU SARINGAN di atas kisi — berlaku ke semua kartu yang bisa disaring (dasbor-logika dbSaring) ----------
  // Pita & tanggalnya pindah dari kartu Periode ke sini (satu ingatan perangkat, kunci yang sama). Ganti pilihan = Dasbor dihitung ulang (opsi.gantiSaring).
  function htmlSaring() {
    const k = opsi.kini(); const iso = hariIniIso(k); let S; try { S = dbSaring(pil, k); } catch (e) { S = { bawaan: true, tolak: String((e && e.message) || e) }; }
    const pita = '<div class="pita db-periode-pita db-saring-pita" data-k="db-saring-pita">' + DB_PERIODE.map(([id, nm]) => '<div class="seg' + (id === pil.id ? ' aktif' : '') + '" data-da-periode="' + id + '">' + esc(nm) + '</div>').join('') + '</div>';
    const tgl = pil.id === 'pilih' ? '<div class="db-periode-tgl"><label><span class="ket">dari</span><input type="date" class="ketik-nama" data-da-tgl="dari" max="' + iso + '" value="' + esc(pil.dari || '') + '"></label>'
      + '<label><span class="ket">sampai</span><input type="date" class="ketik-nama" data-da-tgl="sampai" max="' + iso + '" value="' + esc(pil.sampai || '') + '"></label></div>' : '';
    const ket = S.tolak ? '<div class="ket awas-teks" data-k="db-saring-tolak">' + esc(S.tolak) + ' — kartu menampilkan Hari ini</div>'
      : S.bawaan ? '<div class="ket" data-k="db-saring-ket">Saringan: Hari ini (bulan ini untuk kartu bulanan) — pilih periode lain untuk menyaring semua kartu sekaligus</div>'
        : '<div class="ket" data-k="db-saring-ket"><b>Saringan ' + esc(S.nama + (S.dari !== S.sampai ? ' · ' + tanggalPendek(S.dari) + ' – ' + tanggalPendek(S.sampai) : '')) + '</b>' + (S.bulanKet ? ' · ' + esc(S.bulanKet) : '') + '</div><div class="ket db-saring-tetap" data-k="db-saring-tetap">' + esc(DB_SARING_TETAP) + '</div>';
    return '<div class="db-saring" data-k="db-saring">' + pita + tgl + ket + '</div>';
  }

  // ---------- headline (B91) & periode (B95) ----------
  function htmlHeadline() {
    const H = dbHeadline(D || {}, perhatian);
    return '<div class="kartu db-kartu db-headline' + (H.awas ? ' awas' : '') + '" data-k="db-headline"><div class="db-kepala"><div class="label">Ringkas hari ini</div><div class="db-periode"></div></div>'
      + '<div class="db-hl-teks">' + H.bagian.map((b, i) => { const t = i === 0 ? b.teks.charAt(0).toUpperCase() + b.teks.slice(1) : b.teks; ujung['hl:' + b.id] = b.id === 'perhatian' ? { perhatian: true } : { tujuan: b.tujuan };
        return '<span class="db-hl-bag db-ketuk' + (b.awas ? ' awas-teks' : '') + '" data-da-ke="hl:' + esc(b.id) + '">' + esc(t) + '</span>'; }).join('<span class="db-hl-titik"> · </span>') + '.</div></div>';
  }
  function htmlPeriode() {
    const k = opsi.kini(); const iso = hariIniIso(k);
    const kunci = 'periode|' + pil.id + '|' + (pil.dari || '') + '|' + (pil.sampai || '') + (pil.id === 'hari' ? '|' + Math.floor((k.getHours() * 60 + k.getMinutes()) / 5) : '');
    let P; try { P = opsi.ingat ? opsi.ingat(kunci, () => dbPeriode(pil, k)) : dbPeriode(pil, k); } catch (e) { P = { galat: String((e && e.message) || e) }; }
    // B94 (owner 27 Nov 2026): pita & tanggal pindah ke saringan di atas kisi (htmlSaring) — kartu ini membaca pilihan yang sama
    const pita = '<div class="ket" data-k="db-periode-pita">ikut saringan di atas Dasbor</div>'; const tgl = ''; void iso;
    let isi;
    if (P.galat) isi = '<div class="menolak awas-teks">Periode gagal dihitung (' + esc(P.galat) + ').</div>';
    else if (P.tolak) isi = '<div class="menolak">' + esc(P.tolak) + '</div>';
    else {
      const Bd = P.banding; const pc = (x) => (x === null ? '' : ' <span class="db-naik ' + (x < 0 ? 'turun' : 'naik') + '">' + esc(dkPct(x)) + '</span>');
      const baris = (id, nama, nilai, banding, pct, tujuan, awas) => '<div class="db-baris db-ketuk' + (awas ? ' awas-teks' : '') + '"' + opsi.daftar('pr:' + id, { judul: nama + ' · ' + P.nama, baris: [[P.nama, nilai]].concat(banding ? [[Bd.nama, banding]] : []), tujuan, ke: P.sumber })
        + '><span class="db-nama">' + esc(nama) + '</span><span class="ket">' + esc(banding ? 'vs ' + banding : '') + '</span><span class="db-nilai angka">' + esc(nilai) + pc(pct) + '</span></div>';
      isi = '<div class="db-angka-baris"><span class="angka db-angka-sedang">' + esc(RP(P.omzet)) + '</span>' + pc(P.pctOmzet) + '<span class="ket">' + esc('omzet ' + P.nama + (Bd.ada ? ' · ' + Bd.nama + ' ' + RP(Bd.omzet) : ' · ' + Bd.nama + ': ' + Bd.ket)) + '</span></div>'
        + baris('margin', 'Laba kotor', RP(P.margin), Bd.ada && Bd.margin !== null && Bd.margin !== undefined ? RP(Bd.margin) : '', null, P.tujuan, P.margin < 0)
        + baris('nota', 'Nota', String(P.nota), Bd.ada ? String(Bd.nota) : '', P.pctNota, P.tujuan)
        + baris('rata', 'Rata-rata nilai nota', P.rata === null ? '—' : RP(Math.round(P.rata)), Bd.ada && Bd.rata ? RP(Math.round(Bd.rata)) : '', P.pctRata, P.tujuan)
        + (P.retur ? baris('retur', 'Retur & refund', RP(P.retur), '', null, P.tujuan) : '')
        + (P.laba ? baris('laba', 'Laba bersih' + (P.laba.berjalan ? ' (tagihan sebulan penuh)' : ''), RP(P.laba.labaBersih), '', null, P.laba.tujuan, P.laba.labaBersih < 0) + baris('biaya', 'Biaya', RP(P.laba.semuaBiaya), '', null, P.laba.tujuan) : '<div class="ket">' + esc(P.labaKet) + '</div>')
        + (P.tanpaHpp ? '<div class="ket">' + esc(P.tanpaHpp + ' baris tanpa modal tidak ikut laba kotor') + '</div>' : '') + (P.ket ? '<div class="ket">' + esc(P.ket) + '</div>' : '');
    }
    if (P && P.tujuan) ujung['pr:sumber'] = { tujuan: P.tujuan };
    const sumber = P && !P.galat && !P.tolak ? '<span class="db-sumber" data-da-ke="pr:sumber" title="Buka ' + esc(P.sumber) + '">' + esc(P.sumber) + ' ›</span>' : '';
    return '<div class="kartu db-kartu db-periode-kartu" data-k="db-periode"><div class="db-kepala"><div class="label">Periode</div><div class="db-periode">' + esc(P && P.nama ? P.nama + (P.dari && P.sampai && P.dari !== P.sampai ? ' · ' + tanggalPendek(P.dari) + ' – ' + tanggalPendek(P.sampai) : '') : '') + '</div>' + sumber + '</div>' + pita + tgl + isi + '</div>';
  }

  // ---------- seluruh kisi ----------
  function html(hasil, perh, c) {
    if (hasil) D = hasil; if (perh) perhatian = perh; if (c) cap = c; ujung = {};
    const W = wgSusun(daftarAktif(), Object.assign({}, D || {}, { perhatian }));
    const isi = W.length ? W.map(htmlPanel).join('') : '<div class="menolak wg-kosong">Dasbor kosong — ' + (atur ? 'tambah kartu dari katalog di bawah.' : 'ketuk Atur untuk menambah kartu.') + '</div>';
    return htmlKepala() + (atur ? '' : htmlSaring()) + '<div class="wg-kisi pn-kisi' + (atur ? ' pn-atur' : '') + '" data-k="wg-kisi">' + isi + '</div>' + htmlBilahAtur();
  }
  /** Tinggi otomatis: panel tanpa tinggi tarikan diberi rentang baris = tinggi isinya (+ jarak). Diukur sesudah digambar & tiap isinya berubah ukuran. */
  function ukurTinggi() {
    if (sempit()) return;
    akar.querySelectorAll('.pn-kisi > .pn.pn-auto').forEach((el) => { const isi = el.firstElementChild; if (!isi) return; const t = isi.getBoundingClientRect().height; if (!(t > 0)) return;
      const n = Math.max(1, Math.ceil((t + JARAK) / WG_BARIS_PX)); const v = 'span ' + n; if (el.style.gridRowEnd !== v) el.style.gridRowEnd = v; });
  }
  function sesudah() {
    ukurTinggi();
    if (pengamat) { try { pengamat.disconnect(); } catch (e) { /* abaikan */ } pengamat = null; }
    if (typeof ResizeObserver === 'function') { pengamat = new ResizeObserver(() => ukurTinggi()); akar.querySelectorAll('.pn-kisi > .pn.pn-auto > :first-child').forEach((el) => pengamat.observe(el)); }
    const diam = gerakDiam();
    akar.querySelectorAll('.pn-kisi > .pn[data-nilai]').forEach((el) => { const id = el.dataset.pn, v = el.dataset.nilai; const lama = nilaiLama[id]; nilaiLama[id] = v;
      const n = el.querySelector('.wg-nilai'); if (diam || !v || lama === undefined || lama === v || !n || typeof n.animate !== 'function') return;
      n.animate([{ color: 'var(--emas-garis)', transform: 'translateY(-3px)' }, { transform: 'none' }], { duration: 820, easing: 'cubic-bezier(.2,.8,.2,1)' }); });
  }
  if (typeof window !== 'undefined' && window.addEventListener) window.addEventListener('resize', () => ukurTinggi());
  /** Gambar ulang (lewat dasbor.js) dengan geser FLIP: tiap panel meluncur dari tempat lamanya ke tempat barunya. */
  function gambarGeser() {
    const lama = {}; akar.querySelectorAll('.pn-kisi > .pn').forEach((el) => { lama[el.dataset.pn] = el.getBoundingClientRect(); });
    opsi.gambarUlang(); if (gerakDiam()) return;
    akar.querySelectorAll('.pn-kisi > .pn').forEach((el) => { const a = lama[el.dataset.pn]; if (!a || (seret && el.dataset.pn === seret.id)) return; const b = el.getBoundingClientRect(); const dx = a.left - b.left, dy = a.top - b.top;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return; el.style.transition = 'none'; el.style.transform = 'translate(' + dx + 'px,' + dy + 'px)'; void el.offsetWidth;
      el.style.transition = 'transform 260ms cubic-bezier(.2,.8,.2,1)'; el.style.transform = ''; setTimeout(() => { el.style.transition = ''; }, 300); });
  }

  // ---------- mode atur ----------
  function mulaiAtur(id) {
    if (atur) return; atur = { daftar: wgAtur().daftar.map((x) => Object.assign({}, x)) }; tambahBuka = false; kabar = '';
    try { if (navigator.vibrate) navigator.vibrate(12); } catch (e) { /* abaikan */ }
    gambarGeser(); const el = id ? akar.querySelector('.pn[data-pn="' + id + '"]') : null; if (el && !gerakDiam()) { el.classList.add('wg-angkat'); setTimeout(() => el.classList.remove('wg-angkat'), 380); }
  }
  async function selesaiAtur() {
    if (!atur || simpanJalan) return;
    if (wgSama(atur.daftar, wgAtur().daftar) && wgAtur().dariOwner) { atur = null; tambahBuka = false; gambarGeser(); return; }
    simpanJalan = true; opsi.gambarUlang(); const hasil = await opsi.simpanWidget(atur.daftar); simpanJalan = false;
    if (hasil && hasil.ok) { atur = null; tambahBuka = false; kabar = hasil.kabar || ''; kabarAwas = false; gambarGeser(); setTimeout(() => { if (!atur && kabar) { kabar = ''; opsi.gambarUlang(); } }, 4000); }
    else { kabar = (hasil && hasil.kabar) || 'Susunan belum tersimpan'; kabarAwas = true; opsi.gambarUlang(); }
  }
  function ubahDraf(baru) { if (!atur) return; atur.daftar = baru; gambarGeser(); }

  // ---------- ketukan (dipanggil dulu oleh penangan klik dasbor.js; true = sudah ditangani) ----------
  function klik(ev) {
    if (akar._tekanLama) { akar._tekanLama = false; return true; }   // klik yang menyusul jari diangkat sesudah tekan lama / tarik bukan ketukan
    const ds = (sel, k) => { const el = ev.target.closest(sel); return el && el.dataset && el.dataset[k] !== undefined ? el : null; };   // elemen yang benar-benar membawa atributnya
    const a = ds('[data-da-aksi]', 'daAksi');
    if (a) { const x = a.dataset.daAksi;
      if (x === 'cetak') { const h = opsi.cetak ? opsi.cetak() : { ok: false, kabar: 'Cetak belum terpasang di sini' }; if (h && !h.ok) { kabar = h.kabar; kabarAwas = true; opsi.gambarUlang(); } return true; }   // P3 B104
      if (x === 'atur') mulaiAtur(null); else if (x === 'selesai') selesaiAtur(); else if (x === 'batal') { atur = null; tambahBuka = false; kabar = ''; gambarGeser(); }
      else if (x === 'tambah') { tambahBuka = !tambahBuka; opsi.gambarUlang(); } else if (x === 'bawaan') ubahDraf(WG_BAWAAN.map((w) => Object.assign({}, w)));
      return true; }
    if (atur) { const hps = ds('[data-wg-hapus]', 'wgHapus'); if (hps) { ubahDraf(wgHapus(atur.daftar, Number(hps.dataset.wgHapus))); return true; }
      const ot = ds('[data-pn-otomatis]', 'pnOtomatis'); if (ot) { ubahDraf(wgTinggiOtomatis(atur.daftar, Number(ot.dataset.pnOtomatis))); return true; }
      const tb = ds('[data-wg-tambah]', 'wgTambah'); if (tb) { ubahDraf(wgTambah(atur.daftar, tb.dataset.wgTambah)); return true; }
      return !!ev.target.closest('.pn-kisi'); }
    const pr = ds('[data-da-periode]', 'daPeriode'); if (pr) { pil = Object.assign({}, pil, { id: pr.dataset.daPeriode }); if (pil.id === 'pilih' && !pil.dari) { const iso = hariIniIso(opsi.kini()); pil.dari = iso.slice(0, 8) + '01'; pil.sampai = iso; } simpanPil(); saringBerubah(); return true; }
    const ke = ds('[data-da-ke]', 'daKe'); if (ke) { const u = ujung[ke.dataset.daKe];
      if (u && u.perhatian) { const el = akar.querySelector('.pn[data-pn="kPerhatian"]'); if (el) { if (el.scrollIntoView) el.scrollIntoView({ block: 'nearest', behavior: gerakDiam() ? 'auto' : 'smooth' }); }
        else { kabar = 'Perlu perhatian disembunyikan dari Dasbor (owner 26 Nov 2026) — tambahkan lagi lewat Atur › + Tambah kartu, atau lihat di Cincin.'; kabarAwas = false; opsi.gambarUlang(); } }
      else if (u && u.tujuan) opsi.keTujuan(u.tujuan); return true; }
    return false;
  }
  akar.addEventListener('change', (ev) => { const t = ev.target.closest('[data-da-tgl]'); if (!t) return; pil = Object.assign({}, pil, { [t.dataset.daTgl]: t.value }); simpanPil(); saringBerubah(); });
  // B94: saringan berubah = semua kartu yang ikut dihitung ulang (Ringkasan menyusun Dasbor dengan saringan baru); tanpa jalur itu cukup digambar ulang
  const saringBerubah = () => (opsi.gantiSaring ? opsi.gantiSaring() : opsi.gambarUlang());
  const simpanPil = () => { try { localStorage.setItem(KUNCI_PERIODE, JSON.stringify(pil)); } catch (e) { /* abaikan */ } };

  // ---------- tekan lama · seret (pindah) · tarik pegangan (ukuran) ----------
  akar.addEventListener('contextmenu', (ev) => { if (ev.target.closest('.pn-kisi.pn-atur')) ev.preventDefault(); });
  akar.addEventListener('pointerdown', (ev) => {
    if (ev.button > 0) return; const el = ev.target.closest('.pn-kisi > .pn'); const kisi = ev.target.closest('.pn-kisi');
    if (!atur) { if (!kisi || ev.target.closest('input, [data-db-rentang], [data-da-periode], [data-db], .db-ketuk, [data-db-ke]')) return;
      tekan = { x: ev.clientX, y: ev.clientY, t: setTimeout(() => { tekan = null; akar._tekanLama = true; setTimeout(() => { akar._tekanLama = false; }, 1500); mulaiAtur(el ? el.dataset.pn : null); }, TEKAN_LAMA) }; return; }
    const pg = ev.target.closest('[data-pn-tarik]');
    if (pg && el) { const r = el.getBoundingClientRect(); const K = akar.querySelector('.pn-kisi').getBoundingClientRect(); const i = Number(pg.dataset.i); const w0 = atur.daftar[i];
      tarik = { i, id: el.dataset.pn, arah: pg.dataset.pnTarik, kiri: r.left, atas: r.top, kolom: (K.width - (WG_KOLOM - 1) * JARAK) / WG_KOLOM, w: w0.w, h: w0.h || Math.max(1, Math.round((r.height + JARAK) / WG_BARIS_PX)), pid: ev.pointerId };
      el.classList.add('pn-ditarik'); try { pg.setPointerCapture(ev.pointerId); } catch (e) { /* abaikan */ } ev.preventDefault(); return; }
    if (!el || ev.target.closest('[data-wg-hapus], [data-pn-otomatis]')) return;
    const r = el.getBoundingClientRect(); seret = { id: el.dataset.pn, dx: ev.clientX - r.left, dy: ev.clientY - r.top, x0: ev.clientX, y0: ev.clientY, gerak: false, pid: ev.pointerId };
    try { el.setPointerCapture(ev.pointerId); } catch (e) { /* abaikan */ }
  });
  const ikut = (el, ev, s) => { el.style.transform = 'none'; const r = el.getBoundingClientRect(); el.style.transform = 'translate(' + (ev.clientX - s.dx - r.left) + 'px,' + (ev.clientY - s.dy - r.top) + 'px) scale(1.02)'; };
  akar.addEventListener('pointermove', (ev) => {
    if (tekan && (Math.abs(ev.clientX - tekan.x) > GESER_BATAL || Math.abs(ev.clientY - tekan.y) > GESER_BATAL)) { clearTimeout(tekan.t); tekan = null; }
    if (tarik && ev.pointerId === tarik.pid) {   // tarik pegangan: lebar mengunci ke kolom, tinggi ke baris 8 px — tampak langsung, disimpan ke draf saat dilepas
      const el = akar.querySelector('.pn[data-pn="' + tarik.id + '"]'); if (!el) return;
      if (tarik.arah.indexOf('w') >= 0) { tarik.w = Math.max(2, Math.min(WG_KOLOM, Math.round((ev.clientX - tarik.kiri + JARAK) / (tarik.kolom + JARAK)))); el.style.gridColumn = 'span ' + tarik.w; }
      if (tarik.arah.indexOf('h') >= 0) { tarik.h = Math.max(10, Math.round((ev.clientY - tarik.atas + JARAK) / WG_BARIS_PX)); el.style.gridRowEnd = 'span ' + tarik.h; el.classList.remove('pn-auto'); el.classList.add('pn-tetap'); }
      const u = el.querySelector('.pn-ukuran'); if (u) u.textContent = tarik.w + '/' + WG_KOLOM + ' · ' + (tarik.arah.indexOf('h') >= 0 || (atur.daftar[tarik.i] || {}).h ? Math.round(tarik.h * WG_BARIS_PX) + ' px' : 'tinggi otomatis');
      return; }
    if (!seret || ev.pointerId !== seret.pid) return;
    if (!seret.gerak && Math.abs(ev.clientX - seret.x0) + Math.abs(ev.clientY - seret.y0) < 6) return;
    const el = akar.querySelector('.pn[data-pn="' + seret.id + '"]'); if (!el) return;
    if (!seret.gerak) { seret.gerak = true; el.classList.add('wg-diseret'); }
    ikut(el, ev, seret);
    el.style.pointerEvents = 'none'; const bawah = document.elementFromPoint(ev.clientX, ev.clientY); el.style.pointerEvents = '';
    const sasar = bawah && bawah.closest ? bawah.closest('.pn-kisi > .pn') : null; if (!sasar || sasar === el) return;
    const dari = atur.daftar.findIndex((w) => w.id === seret.id), ke = Number(sasar.dataset.i); if (dari < 0 || dari === ke) return;
    atur.daftar = wgPindah(atur.daftar, dari, ke); const s = seret; gambarGeser();
    const el2 = akar.querySelector('.pn[data-pn="' + s.id + '"]'); if (el2) { el2.classList.add('wg-diseret'); ikut(el2, ev, s); try { el2.setPointerCapture(s.pid); } catch (e) { /* abaikan */ } }
  });
  const lepas = (ev) => {
    if (tekan) { clearTimeout(tekan.t); tekan = null; }
    if (tarik && (!ev || ev.pointerId === tarik.pid)) { const t = tarik; tarik = null; akar._tekanLama = true; setTimeout(() => { akar._tekanLama = false; }, 50);
      const sb = atur.daftar[t.i] || {}; ubahDraf(wgUkur(atur.daftar, t.i, t.w, t.arah.indexOf('h') >= 0 ? t.h : sb.h)); return; }
    if (akar._tekanLama && !seret) setTimeout(() => { akar._tekanLama = false; }, 0);   // klik yang menyusul jari diangkat sesudah tekan lama ditelan, ketukan berikutnya tidak
    if (!seret || (ev && ev.pointerId !== seret.pid)) return; const s = seret; seret = null;
    const el = akar.querySelector('.pn[data-pn="' + s.id + '"]'); if (!el) return; el.classList.remove('wg-diseret');
    if (!s.gerak) { el.style.transform = ''; return; }
    akar._tekanLama = true; setTimeout(() => { akar._tekanLama = false; }, 50);
    if (gerakDiam()) { el.style.transform = ''; return; }
    el.style.transition = 'transform 220ms cubic-bezier(.2,.8,.2,1)'; el.style.transform = ''; setTimeout(() => { el.style.transition = ''; }, 260);
  };
  akar.addEventListener('pointerup', lepas); akar.addEventListener('pointercancel', lepas);

  return { html, sesudah, klik, pil: () => Object.assign({}, pil), sedangAtur: () => !!atur || !!seret || !!tarik, menyeret: () => !!seret || !!tarik, adaWidget: (id) => daftarAktif().some((w) => w.id === id) };
}
