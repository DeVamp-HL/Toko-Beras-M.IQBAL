// LAYAR RINGKASAN — DASBOR OWNER: GAMBAR (putaran 40). Angka dari dasbor-logika.js (satu sumber); di sini cuma geometri SVG, kata & ketukan.
//
// Grafik = SVG sendiri (tanpa pustaka, tanpa build, Chrome 80). Batang & bilah memakai preserveAspectRatio="none" dengan label HTML di luarnya,
// jadi tulisan tidak ikut tergencet di HP. Tiap bagian yang bisa diketuk membawa data-db → kartu kecil berisi angka di baliknya + tombol ke layar
// sumbernya. Ketuk pertama = tooltip (iPad/HP), ketuk kedua di tempat yang sama = pindah ke layar sumbernya; di Mac tooltip muncul saat kursor lewat
// dan klik langsung pindah. Animasi masuk ringan hanya saat dasbor dibuka / rentang diganti (data yang berubah tidak memutar ulang animasinya);
// prefers-reduced-motion dihormati (ringkasan.css). Warna dari token identitas.css → mode gelap ikut sendiri. BACA SAJA.
// owner 24 Nov 2026: grosir vs ecer per jenis barang
import * as GE from './grosir-ecer-logika.js';
import { esc } from '../inti/dom.js';
import { RP, DESIMAL, tanggalPendek } from '../inti/format.js';
import { DB_RENTANG } from './dasbor-logika.js';
import { SH_RENTANG_BELI } from './susut-harga-logika.js';   // B68 (owner 27 Nov 2026): pita Hari · Minggu · Bulan kartu Pembelian
// owner 26 Nov 2026: kisi panel berpegangan (dasbor-kisi.js) — kartu di bawah ini = isi panel, ukuran & tempat diatur owner
import { pasangKisi } from './dasbor-kisi.js';

const KUNCI_RENTANG = 'miqbal_baru_dasbor_rentang';
const KUNCI_BELI = 'miqbal_baru_dasbor_beli';
const KUNCI_RAPOR = 'miqbal_baru_dasbor_rapor';   // P2 (owner 27 Nov 2026): saklar Laba | Kas kartu Rapor bulan, diingat per perangkat (bawaan Laba)   // B68: rentang grafik pembelian, diingat per perangkat (bawaan Bulan)
const dbRpPendek = (n) => { const a = Math.abs(n || 0); const s = n < 0 ? '−' : ''; return a >= 1e6 ? s + DESIMAL(Math.round(a / 1e5) / 10) + ' jt' : a >= 1e3 ? s + Math.round(a / 1e3) + ' rb' : s + Math.round(a); };
const dbKg = (n) => (n < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(n || 0) * 10) / 10) + ' kg';
const dbTgl = (iso) => (iso ? tanggalPendek(iso).replace(/ \d{4}$/, '') : '');
const dbJam = (j) => String(j || '').replace(':', '.');
const dbHari = (h) => (h === null || h === undefined ? 'laju belum terukur' : h < 1 ? 'habis < 1 hari' : '±' + DESIMAL(Math.round(h * 10) / 10) + ' hari');
const dbPersen = (v, maks) => (maks > 0 ? Math.max(0, Math.min(100, v / maks * 100)) : 0);
const DB_KATA_LAMPU = { merah: 'lewat', amber: 'mendekati batas', hijau: 'aman', tanpa: 'tanpa anggaran' };

export function pasangDasbor(akar, opsi) {
  let rentang = (() => { try { return localStorage.getItem(KUNCI_RENTANG) || 'hari'; } catch (e) { return 'hari'; } })();
  if (!DB_RENTANG.some((r) => r[0] === rentang)) rentang = 'hari';
  let reg = {}; let pilih = null; let D = null;
  let rentangBeli = (() => { try { return localStorage.getItem(KUNCI_BELI) || 'bulan'; } catch (e) { return 'bulan'; } })(); if (!SH_RENTANG_BELI.some((r) => r[0] === rentangBeli)) rentangBeli = 'bulan';
  let modeRapor = (() => { try { return localStorage.getItem(KUNCI_RAPOR) === 'kas' ? 'kas' : 'laba'; } catch (e) { return 'laba'; } })();
  // P2 (B110 B124): lampu target owner untuk angka kartu lama — dari kelompok rapor (rbAmbangDasbor); tanpa target owner = '' (kartu seperti dulu)
  const ambangDb = (k) => { const A = D && D.rapor && !D.rapor.galat && D.rapor.ambang && !D.rapor.ambang.galat ? D.rapor.ambang[k] : null; return A || null; };
  const lampuDb = (k) => { const A = ambangDb(k); return A ? '<i class="db-lampu ' + esc(A.lampu) + '" title="' + esc(A.teks) + '"></i>' : ''; };
  // B94 (owner 27 Nov 2026): saringan Dasbor aktif (bukan Hari ini) → kartu yang TIDAK ikut diberi cap "sekarang · tidak ikut saringan" (bukan diam-diam)
  const saringAktif = () => !!(D && D.saring && !D.saring.bawaan);
  const tetap = (teks) => (saringAktif() ? '<span class="db-tetap" data-k="db-tetap">' + esc(teks || 'sekarang · tidak ikut saringan') + '</span>' : '');
  // daftarkan satu bagian yang bisa diketuk: { judul, baris: [[kata, nilai]], tujuan, ke (nama layar), catatan }
  const daftar = (id, isi) => { reg[id] = isi; return ' data-db="' + esc(id) + '"'; };
  const kepala = (judul, periode, idSumber, sumber, tujuan, cap) => { reg[idSumber] = { judul: sumber, baris: [], tujuan, ke: sumber };
    return '<div class="db-kepala"><div class="label">' + esc(judul) + '</div><div class="db-periode">' + esc(periode) + '</div>' + (cap || '')
      + '<span class="db-sumber" data-db-ke="' + esc(idSumber) + '" title="Buka ' + esc(sumber) + '">' + esc(sumber) + ' ›</span></div>'; };
  const galat = (x) => '<div class="menolak awas-teks">Bagian ini gagal dihitung (' + esc(x.galat) + ') — kelompok lain tetap. Buka layar sumbernya untuk angka yang sama.</div>';

  // ---------- HARI INI ----------
  function kartuHari(H) {
    if (H.galat) return '<div class="kartu hero db-kartu db-hari">' + galat(H) + '</div>';
    const kas = H.kas; const pos = kas.ada ? kas.tempat.filter((t) => t.n > 0) : []; const totalPos = pos.reduce((a, t) => a + t.n, 0); let x = 0;
    const segmen = pos.map((t, i) => { const w = dbPersen(t.n, totalPos); const s = '<rect class="db-tumbuh-x db-kas-' + esc(t.id) + '" style="--i:' + i + '" x="' + x.toFixed(3) + '" y="0" width="' + w.toFixed(3) + '" height="10"' + daftar('kas:' + t.id, { judul: t.nama + ' · ' + H.periode, baris: [['Isi menurut buku', RP(t.n)], ['Semua tempat', RP(kas.total)], ['Dihitung dari', kas.titik]], tujuan: H.kasTujuan, ke: H.kasSumber }) + '></rect>'; x += w; return s; }).join('');
    const KC = H.karcis;
    return '<div class="kartu hero db-kartu db-hari' + (H.saring ? ' db-hari-saring' : '') + '">' + kepala(H.judul || 'Hari ini', H.periode, 'sumber:hari', H.sumber, H.tujuan)
      + '<div class="db-dua"><div' + daftar('hari:omzet', { judul: 'Omzet · ' + H.periode, baris: [['Omzet (sesudah retur)', RP(H.omzet)], ['Nota', String(H.nota)]].concat(H.retur ? [['Retur & refund', RP(H.retur)]] : []).concat((H.tunai === null ? [['Uang per cara bayar', 'ikut arsip tutup buku']] : [['Tunai', RP(H.tunai)], ['QRIS', RP(H.qris)]].concat(H.transfer ? [['Transfer', RP(H.transfer)]] : []).concat([['Bon', RP(H.kredit) + ' · ' + H.nKredit + ' nota']]))).concat(H.jenis ? GE.geBaris(H.jenis, RP) : []), tujuan: H.tujuan, ke: H.sumber }) + ' class="db-ketuk"><div class="label" style="color: var(--hero-label);">Omzet</div>'
      + '<div class="angka dagang db-angka-besar">' + esc(RP(H.omzet)) + '</div><div class="ket">' + esc(H.nota + ' nota' + (H.retur ? ' · sudah dikurangi retur ' + RP(H.retur) : '')) + '</div></div>'
      + '<div' + daftar('hari:laba', { judul: 'Laba kotor · ' + H.periode, baris: [['Laba kotor (margin)', RP(H.margin)]].concat(H.tanpaHpp ? [['Baris tanpa modal', H.tanpaHpp + ' baris — tidak ikut dihitung']] : []), tujuan: H.tujuan, ke: H.sumber }) + ' class="db-ketuk"><div class="label" style="color: var(--hero-label);">' + lampuDb('labaHari') + 'Laba kotor</div>'
      + '<div class="angka db-angka-sedang">' + esc(RP(H.margin)) + '</div><div class="ket">' + esc(H.tanpaHpp ? H.tanpaHpp + ' baris tanpa modal tidak ikut' : 'semua baris bermodal') + '</div></div></div>'
      + barisBandingHari()
      + '<div class="db-sub">Kas per tempat' + (kas.ada ? ' · ' + esc(RP(kas.total)) + ' · ' + esc(kas.titik) : '') + (H.saring ? ' · sekarang, tidak ikut saringan' : '') + '</div>'
      + (kas.ada ? '<svg class="db-bilah db-bilah-kas" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" aria-label="Kas per tempat">' + (segmen || '<rect class="db-rel" x="0" y="4" width="100" height="2"></rect>') + '</svg>'
        + '<div class="db-legenda">' + kas.tempat.map((t) => '<span' + daftar('kasL:' + t.id, { judul: t.nama + ' · ' + H.periode, baris: [['Isi menurut buku', RP(t.n)], ['Dihitung dari', kas.titik]], tujuan: H.kasTujuan, ke: H.kasSumber }) + ' class="db-ketuk' + (t.n < -0.5 ? ' awas-teks' : '') + '"><i class="db-titik db-kas-' + esc(t.id) + '"></i>' + esc(t.nama) + ' <b class="angka">' + esc(RP(t.n)) + '</b></span>').join('') + '</div>'
        + (kas.minus.length ? '<div class="ket awas-teks">' + esc(kas.minus.map((k) => kas.tempat.find((t) => t.id === k).nama).join(', ')) + ' MINUS menurut buku — ada pindah/keluar yang belum dicatat?</div>' : '')
        + (kas.cocok ? '' : '<div class="ket awas-teks">Jumlah per tempat tidak sama dengan kas mesin — laporkan.</div>')
        : '<div class="menolak">Titik kas belum ada — Tutup hari malam ini (Uang › Tutup hari) menyetelnya. Tanpa itu isi tiap tempat tidak ditebak.</div>')
      // owner 26 Nov 2026: awal hari (akhir kemarin) · kas kecil · setor ke bank · cocok rekening — kalimat dari layar sumbernya, ketuk = buka layarnya
      + (H.awalHari && !H.awalHari.galat ? '<div class="ket db-ketuk" data-k="db-awal-hari"' + daftar('hari:awal', { judul: 'Uang toko awal hari · ' + H.periode, baris: H.awalHari.ada ? [['Akhir kemarin (semua tempat)', RP(H.awalHari.total)], ['Sekarang', kas.ada ? RP(kas.total) : '—'], ['Dihitung dari', H.awalHari.sumber]] : [['Awal hari', 'belum bisa dihitung'], ['Sebab', H.awalHari.sebab]], tujuan: H.awalTujuan, ke: H.awalSumber }) + '>' + esc(H.awalHari.ada ? (H.saring ? 'Uang toko akhir ' + dbTgl(H.awalHari.iso) + ' (sebelum periode) ' : 'Awal hari ') + RP(H.awalHari.total) + (kas.ada ? ' → sekarang ' + RP(kas.total) : '') : (H.saring ? 'Uang toko sebelum periode' : 'Awal hari') + ' belum bisa dihitung') + ' ›</div>' : '')
      + (H.kasKecil && !H.kasKecil.galat ? '<div class="ket db-ketuk' + (H.kasKecil.lewat || H.kasKecil.nNotaKurang ? ' awas-teks' : '') + '" data-k="db-kas-kecil"' + daftar('hari:kasKecil', { judul: 'Kas kecil · ' + H.periode, baris: [['Terpakai', RP(H.kasKecil.terpakai) + ' · ' + H.kasKecil.n + ' catatan'], ['Batas sehari', H.kasKecil.batas > 0 ? RP(H.kasKecil.batas) : 'mati'], ['Sisa', H.kasKecil.sisa === null ? '—' : RP(H.kasKecil.sisa)], ['Nota belum beres', String(H.kasKecil.nNotaKurang)]], tujuan: H.kasKecilTujuan, ke: 'Uang › Uang keluar' }) + '>' + esc(H.kasKecil.teks) + ' ›</div>' : '')
      + (H.setor && !H.setor.galat && H.setor.lewat ? '<div class="ket db-ketuk awas-teks" data-k="db-setor"' + daftar('hari:setor', { judul: 'Setor ke bank', baris: [['Brankas', RP(H.setor.brankas)], ['Batas', RP(H.setor.batas)], ['Setor', RP(H.setor.n)], ['Sisakan', RP(H.setor.sisakan)]], tujuan: H.setorTujuan, ke: 'Uang › Pindah uang' }) + '>' + esc(H.setor.teks) + ' ›</div>' : '')
      + (H.rekening && !H.rekening.galat ? '<div class="ket db-ketuk' + (H.rekening.nBelum ? ' awas-teks' : '') + '" data-k="db-rekening"' + daftar('hari:rekening', { judul: 'Rekening usaha', baris: [['Menurut buku', H.rekening.bukuSekarang === null ? '—' : RP(H.rekening.bukuSekarang)], ['Belum dicek', H.rekening.nBelum + ' transaksi sejak ' + dbTgl(H.rekening.dari)], ['Cocok terakhir', H.rekening.akhir ? dbTgl(H.rekening.akhir.tanggal) : 'belum pernah']], tujuan: H.rekeningTujuan, ke: 'Uang › Rekening' }) + '>' + esc(H.rekening.teks) + ' ›</div>' : '')
      + '<div class="db-karcis db-ketuk' + (KC.n ? ' awas-teks' : '') + '"' + daftar('hari:karcis', { judul: 'Karcis kasir', baris: [['Karcis belum dirinci', KC.n + (KC.n ? ' · ' + RP(KC.rp) : '')], ['Nota jumlahnya belum pasti', String(KC.rapikan)], ['Karcis bertanggal hari ini', String(KC.hariIni)]], tujuan: H.karcisTujuan, ke: H.karcisSumber, catatan: 'Karcis = nota kasir yang baru nominalnya; barangnya belum dirinci, jadi modal & stoknya belum ikut.' }) + '>'
      + lampuDb('karcis') + esc(KC.n ? KC.n + ' karcis kasir belum dirinci · ' + RP(KC.rp) : 'Tidak ada karcis kasir yang menunggu dirinci') + (KC.rapikan ? ' · ' + esc(KC.rapikan + ' nota perlu dirapikan') : '') + ' ›</div>'
      + '</div>';
  }

  // owner 26 Nov 2026 (B1 · B113): omzet hari ini vs kemarin & hari yang sama minggu lalu, SAMPAI JAM YANG SAMA (D.banding = dasbor-logika dbBanding, rumus Cincin)
  function barisBandingHari() {
    // B94: kartu disaring → pembanding = periode sebelumnya (angka kartu Periode, dbPeriode); "jam segini" hanya untuk Hari ini
    const Hs = D && D.hari && D.hari.saring; if (Hs) { const X = Hs.banding; if (!X) return ''; const Bd = X.banding; const pc = X.pctOmzet;
      return '<div class="ket db-banding' + (pc !== null && pc < 0 ? ' awas-teks' : '') + '" data-k="db-banding-hari">' + esc(!Bd.ada ? Bd.nama + ': ' + Bd.ket : 'vs ' + Bd.nama + ' ' + RP(Bd.omzet) + (pc === null ? '' : ' (' + (pc > 0 ? '+' : pc < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(pc) * 10) / 10) + '%)') + ' · ' + Bd.nota + ' nota') + '</div>'; }
    const B = D && D.banding; if (!B || B.galat) return '';
    const satu = (x, id) => { const t = !x.ada ? x.nama + ': ' + x.ket : x.nama + ' jam segini ' + RP(x.omzet) + (x.pct === null ? '' : ' (' + (x.pct > 0 ? '+' : x.pct < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(x.pct) * 10) / 10) + '%)');
      return '<span class="db-ketuk' + (x.ada && x.pct !== null && x.pct < 0 ? ' awas-teks' : '') + '"' + daftar('hari:' + id, { judul: 'Omzet sampai ' + B.jam + ' · ' + x.nama, baris: x.ada ? [['Hari ini sampai ' + B.jam, RP(B.omzet) + ' · ' + B.nota + ' nota'], [x.nama + ' sampai ' + B.jam, RP(x.omzet) + ' · ' + x.nota + ' nota'], ['Selisih', RP(x.selisih)]] : [['Keadaan', x.ket]], tujuan: x.tujuan, ke: 'Laporan › Harian', catatan: 'Dihitung sampai jam yang sama (nota sesudah jam itu belum ikut) — rumus yang sama dengan Cincin.' }) + '>' + esc(t) + '</span>'; };
    return '<div class="ket db-banding" data-k="db-banding-hari">' + satu(B.kemarin, 'kemarin') + ' · ' + satu(B.mingguLalu, 'minggu') + (B.rata !== null ? ' · rata-rata ' + esc(RP(Math.round(B.rata))) + '/nota' : '') + '</div>';
  }
  // owner 26 Nov 2026 (B9 · B113): bulan ini vs bulan lalu SAMPAI TANGGAL YANG SAMA (D.banding.bulan = lpRataNota)
  function barisBandingBulan() {
    const M = D && D.banding && !D.banding.galat ? D.banding.bulan : null; if (!M) return '';
    if (D.bulan && D.bulan.key && M.key && D.bulan.key !== M.key) return '';   // B94: kartu Bulan disaring ke bulan lain — banding "sampai tanggal yang sama" milik bulan berjalan
    const pc = (x) => (x === null ? '' : ' (' + (x > 0 ? '+' : x < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(x) * 10) / 10) + '%)');
    const isi = M.lalu.ada ? { judul: M.nama + ' vs ' + M.namaLalu + ' s.d. tanggal ' + Number(M.sampaiLalu.slice(8, 10)), baris: [['Omzet', RP(M.ini.omzet) + ' vs ' + RP(M.lalu.omzet)], ['Nota', M.ini.nota + ' vs ' + M.lalu.nota], ['Rata-rata nilai nota', (M.ini.rata === null ? '—' : RP(Math.round(M.ini.rata))) + ' vs ' + (M.lalu.rata ? RP(Math.round(M.lalu.rata)) : '—')]], tujuan: M.tujuanLalu, ke: 'Laporan › Bulanan' }
      : { judul: 'Bulan lalu', baris: [['Keadaan', M.lalu.ket]], tujuan: M.tujuan, ke: 'Laporan › Bulanan' };
    return '<div class="ket db-ketuk db-banding' + (M.pctOmzet !== null && M.pctOmzet < 0 ? ' awas-teks' : '') + '" data-k="db-banding-bulan"' + daftar('bulan:banding', isi) + '>' + esc(M.lalu.ada ? 'Omzet ' + RP(M.ini.omzet) + pc(M.pctOmzet) + ' vs ' + M.namaLalu.split(' ')[0] + ' s.d. tanggal ' + Number(M.sampaiLalu.slice(8, 10)) + ' · rata-rata ' + (M.ini.rata === null ? '—' : RP(Math.round(M.ini.rata))) + '/nota' + pc(M.pctRata) : 'Bulan lalu: ' + M.lalu.ket) + ' ›</div>';
  }

  // ---------- TREN ----------
  function kartuTren(T) {
    const pita = '<div class="pita db-rentang">' + DB_RENTANG.map(([id, nm]) => '<div class="seg' + (id === rentang ? ' aktif' : '') + '" data-db-rentang="' + id + '">' + esc(nm) + '</div>').join('') + '</div>';
    if (T.galat) return '<div class="kartu db-kartu db-tren">' + pita + galat(T) + '</div>';
    // dua grafik, satu sumbu waktu: laba kotor ±2–5 % dari omzet → di skala omzet batangnya hilang; maka laba kotor punya skala SENDIRI (tertingginya disebut)
    const n = T.batang.length; const W = n * 100; const maksM = Math.max(1, ...T.batang.map((b) => (b.absen ? 0 : Math.max(0, b.margin))));
    const kolom = (b, i, isi, tinggi, kelas) => '<g class="db-kol' + (b.berjalan ? ' berjalan' : '') + (b.absen ? ' absen' : '') + '"' + daftar(kelas + ':' + b.id, isi) + '>'
      + '<rect class="db-kena" x="' + (i * 100) + '" y="0" width="100" height="100"></rect>'
      + (b.absen ? '<rect class="db-rel" x="' + (i * 100 + 20) + '" y="99" width="60" height="1"></rect>' : '<rect class="' + kelas + ' db-tumbuh-y" style="--i:' + i + '" x="' + (i * 100 + 14) + '" y="' + (100 - tinggi).toFixed(2) + '" width="72" height="' + tinggi.toFixed(2) + '"></rect>') + '</g>';
    const isiDari = (b) => ({ judul: b.panjang, baris: b.absen ? [['Keadaan', 'sebelum toko mulai mencatat']] : [['Omzet (sesudah retur)', RP(b.omzet)], ['Laba kotor', RP(b.margin)], ['Nota', String(b.nota)]].concat(b.tanpaHpp ? [['Baris tanpa modal', b.tanpaHpp + ' — tidak ikut laba kotor']] : []).concat(b.retur ? [['Retur & refund', RP(b.retur)]] : []).concat(b.berjalan ? [['', 'masih berjalan']] : []), tujuan: b.absen ? null : b.tujuan, ke: T.sumber });
    const kolO = T.batang.map((b, i) => kolom(b, i, isiDari(b), b.absen ? 0 : Math.max(b.omzet > 0 ? 0.6 : 0, dbPersen(Math.max(0, b.omzet), T.maks) * 0.94), 'db-omzet')).join('');
    const kolM = T.batang.map((b, i) => kolom(b, i, isiDari(b), b.absen ? 0 : dbPersen(Math.max(0, b.margin), maksM) * 0.94, 'db-margin')).join('');
    const label = '<div class="db-sumbu">' + T.batang.map((b) => '<span class="' + (b.berjalan ? 'aktif' : '') + '">' + esc(b.label) + '</span>').join('') + '</div>';
    const minus = T.batang.filter((b) => !b.absen && b.omzet < 0);
    return '<div class="kartu db-kartu db-tren">' + kepala('Omzet & laba kotor', T.periode, 'sumber:tren', T.sumber, { ke: 'laporan', keluarga: T.rentang === 'hari' ? 'harian' : T.rentang === 'minggu' ? 'mingguan' : 'bulanan' }, tetap('pilihan sendiri · tidak ikut saringan')) + pita
      + '<div class="db-legenda"><span><i class="db-titik db-omzet"></i>Omzet</span><span class="ket">tertinggi ' + esc(RP(T.maks)) + '</span></div>'
      + '<svg class="db-grafik" viewBox="0 0 ' + W + ' 100" preserveAspectRatio="none" role="img" aria-label="Omzet ' + esc(T.periode) + '"><line class="db-dasar" x1="0" y1="100" x2="' + W + '" y2="100"></line>' + kolO + '</svg>'
      + '<div class="db-legenda"><span><i class="db-titik db-margin"></i>Laba kotor · skala sendiri</span><span class="ket">tertinggi ' + esc(RP(maksM)) + '</span></div>'
      + '<svg class="db-grafik db-grafik-pendek" viewBox="0 0 ' + W + ' 100" preserveAspectRatio="none" role="img" aria-label="Laba kotor ' + esc(T.periode) + '"><line class="db-dasar" x1="0" y1="100" x2="' + W + '" y2="100"></line>' + kolM + '</svg>' + label
      + (minus.length ? '<div class="ket">' + esc(minus.map((b) => b.panjang).join(', ')) + ': omzet MINUS (retur lebih besar dari penjualan) — batangnya kosong, angkanya di tooltip.</div>' : '')
      + '<div class="ket db-pandu">Ketuk batang untuk angkanya · ketuk lagi untuk membuka ' + esc(T.sumber) + '</div></div>';
  }

  // ---------- BULAN INI ----------
  function kartuBulan(B) {
    if (B.galat) return '<div class="kartu db-kartu db-bulan">' + galat(B) + '</div>';
    const top = kepala(B.judul || 'Bulan ini', B.periode, 'sumber:bulan', B.sumber, B.tujuan);
    if (B.tanpaCatatan) return '<div class="kartu db-kartu db-bulan">' + top + '<div class="menolak">Belum ada satu catatan pun di ' + esc(B.nama) + ' — angka bulan ini mulai terisi sesudah nota & biaya pertama.</div></div>';
    const I = B.impas; const skala = Math.max(B.omzetHitung, I.omzetImpas || 0, 1);
    const impas = I.omzetImpas === null ? '<div class="menolak">' + esc(I.teks) + '</div>'
      : '<svg class="db-bilah db-bilah-impas" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" aria-label="Omzet menuju titik impas"' + daftar('bulan:impas', { judul: 'Titik impas · ' + B.periode, baris: [['Omzet ber-modal bulan ini', RP(B.omzetHitung)], ['Omzet titik impas sebulan', RP(I.omzetImpas) + ' (' + RP(I.omzetImpasHari) + '/hari)'], ['Rata-rata omzet per hari', RP(I.omzetHari)], ['Laba bersih sampai ' + dbTgl(I.sampai), RP(I.labaSampai)]], tujuan: B.tujuan, ke: B.sumber, catatan: I.teks }) + '>'
        + '<rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x ' + (I.menutup ? 'db-cukup' : 'db-kurang') + '" x="0" y="1" width="' + dbPersen(B.omzetHitung, skala).toFixed(2) + '" height="8"></rect>'
        + '<line class="db-patok" x1="' + dbPersen(I.omzetImpas, skala).toFixed(2) + '" y1="0" x2="' + dbPersen(I.omzetImpas, skala).toFixed(2) + '" y2="10"></line></svg>'
        + '<div class="ket' + (I.menutup ? '' : ' awas-teks') + '">' + esc(I.kiniTeks) + '</div>';
    const maksB = Math.max(1, ...B.biaya.map((r) => Math.max(r.n, r.dasar || 0)));
    const biaya = B.biaya.length ? B.biaya.map((r, i) => '<div class="db-baris db-ketuk"' + daftar('biaya:' + r.id, { judul: r.nama + ' · ' + B.periode, baris: [['Terpakai', RP(r.n) + (r.menggantung ? ' (termasuk upah belum dibayar ' + RP(r.menggantung) + ')' : '')], ['Lampu', DB_KATA_LAMPU[r.lampu] + (r.lampu === 'tanpa' ? '' : ' · ' + r.lampuTeks)]].concat(r.proyeksi !== null ? [['Perkiraan sebulan', RP(r.proyeksi)]] : []).concat([['Bulan lalu', RP(r.nLalu)]]), tujuan: B.tujuan, ke: B.sumber }) + '>'
        + '<span class="db-nama"><i class="db-lampu ' + esc(r.lampu) + '"></i>' + esc(r.nama) + '</span>'
        + '<svg class="db-bilah" viewBox="0 0 100 10" preserveAspectRatio="none"><rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x db-lampu-isi ' + esc(r.lampu) + '" style="--i:' + i + '" x="0" y="1.5" width="' + dbPersen(r.n, maksB).toFixed(2) + '" height="7"></rect>'
        + (r.dasar ? '<line class="db-patok" x1="' + dbPersen(r.dasar, maksB).toFixed(2) + '" y1="0" x2="' + dbPersen(r.dasar, maksB).toFixed(2) + '" y2="10"></line>' : '') + '</svg>'
        + '<span class="db-nilai angka">' + esc(dbRpPendek(r.n)) + '</span></div>').join('') : '<div class="menolak">Belum ada biaya tercatat bulan ini.</div>';
    const lampu = B.nLampu ? [B.merah ? B.merah + ' lewat' : '', B.amber ? B.amber + ' mendekati batas' : '', B.hijau ? B.hijau + ' aman' : ''].filter(Boolean).join(' · ') : 'anggaran belum diatur';
    const lampuPanjang = B.nLampu ? lampu : 'anggaran belum diatur (Laporan › Biaya › Atur) — lampu belum menyala';
    return '<div class="kartu db-kartu db-bulan">' + top
      + '<div class="db-tiga">'
      + '<div class="db-ketuk"' + daftar('bulan:margin', { judul: 'Laba kotor · ' + B.periode, baris: [['Omzet (sesudah retur)', RP(B.omzet)], ['Omzet ber-modal', RP(B.omzetHitung)], ['Laba kotor', RP(B.margin) + ' · ' + B.rasioTeks + ' dari omzet ber-modal']].concat(B.tanpaHpp ? [['Baris tanpa modal', B.tanpaHpp + ' — tidak ikut']] : []), tujuan: B.labaTujuan, ke: 'Laporan › Laba' }) + '><div class="label">Laba kotor</div><div class="angka db-angka-kecil">' + esc(RP(B.margin)) + '</div><div class="ket">' + esc(B.rasioTeks + ' dari omzet ber-modal') + '</div></div>'
      + '<div class="db-ketuk"' + daftar('bulan:biaya', { judul: 'Biaya · ' + B.periode, baris: [['Semua biaya di bawah laba kotor', RP(B.semuaBiaya)], ['Lampu', lampuPanjang]], tujuan: B.tujuan, ke: B.sumber }) + '><div class="label">Biaya</div><div class="angka db-angka-kecil">' + esc(RP(B.semuaBiaya)) + '</div><div class="ket">' + esc(lampu) + '</div></div>'
      + '<div class="db-ketuk' + (B.labaBersih < 0 ? ' awas-teks' : '') + '"' + daftar('bulan:bersih', { judul: 'Laba bersih · ' + B.periode, baris: [['Laba bersih bulan ini', RP(B.labaBersih)], ['Sampai ' + dbTgl(I.sampai), RP(I.labaSampai)]], tujuan: B.labaTujuan, ke: 'Laporan › Laba', catatan: B.berjalan ? 'Angka bulan ini sudah memotong jatah tagihan bulanan sebulan penuh (sama dengan Laporan › Laba); "sampai hari ini" hanya memotong jatah sampai hari ini.' : '' }) + '><div class="label">Laba bersih</div><div class="angka db-angka-kecil">' + esc(RP(B.labaBersih)) + '</div><div class="ket">' + esc('sampai ' + dbTgl(I.sampai) + ' ' + RP(I.labaSampai)) + '</div></div>'
      + '</div>'
      + barisBandingBulan()
      + '<div class="db-sub">Menuju titik impas</div>' + impas
      + '<div class="db-sub">Biaya per jenis · garis = jatah anggaran</div>' + biaya
      + barisPph(B.pph)
      + '<div class="db-baris db-ketuk' + (B.susut > 0 ? ' awas-teks' : '') + '"' + daftar('bulan:susut', { judul: 'Susut & selisih stok · ' + B.periode, baris: [['Susut & selisih', RP(B.susut)], ['Baris', String(B.nSusut)]], tujuan: B.susutTujuan, ke: 'Stok › Cocokkan', catatan: 'Biaya yang tidak keluar dari laci — sudah ikut di biaya & laba bersih di atas.' }) + '><span class="db-nama">Susut & selisih stok</span><span></span><span class="db-nilai angka">' + esc(RP(B.susut)) + ' ›</span></div>'
      + (B.menutup ? '' : '<div class="ket awas-teks">Pemilahan biaya TIDAK MENUTUP ke mesin laba bulan ini — jangan dipakai memutuskan; laporkan.</div>')
      + '</div>';
  }

  // A47 (owner 27 Nov 2026): PPh final (perkiraan) = POS ANGGARAN SENDIRI — di luar "Semua biaya", laba bersih & titik impas (pos sisihan). D.bulan.pph = kpi-laba klPph.
  function barisPph(X) {
    if (!X) return ''; if (X.galat && !X.keadaan) return '<div class="ket awas-teks" data-k="db-pph">PPh final gagal dihitung: ' + esc(X.galat) + '</div>';
    const isi = { judul: X.nama + ' · ' + (D.bulan ? D.bulan.nama : ''), baris: [['Perkiraan', X.n === null ? 'belum bisa dihitung' : RP(X.n)], ['Anggaran', X.anggaran > 0 ? RP(X.anggaran) + ' sebulan' : 'belum diatur (Laporan › Biaya › Atur)'], ['Lampu', DB_KATA_LAMPU[X.lampu] + (X.lampu === 'tanpa' ? '' : ' · ' + X.lampuTeks)]]
      .concat(X.proyeksi !== null ? [['Perkiraan sebulan', RP(X.proyeksi)]] : []).concat([['Sudah disetor', RP(X.setor)], ['Sisihkan', X.sisihkan === null ? '—' : RP(X.sisihkan)]]).concat(X.diBiaya ? [['Sudah dicatat di uang keluar', RP(X.diBiaya) + ' (sudah ikut biaya toko)']] : []),
      tujuan: X.tujuan, ke: 'Laporan › Pajak', catatan: X.label + ' · ' + X.ket };
    return '<div class="db-sub" data-k="db-pph-sub">Pos sisihan · di luar biaya & laba bersih</div><div class="db-baris db-ketuk' + (X.lampu === 'merah' ? ' awas-teks' : '') + '" data-k="db-pph"' + daftar('bulan:pph', isi) + '><span class="db-nama"><i class="db-lampu ' + esc(X.lampu) + '"></i>' + esc(X.nama) + '</span><span class="ket">'
      + esc(X.n === null ? 'belum bisa diperkirakan' : 'sisihkan ' + RP(X.sisihkan)) + '</span><span class="db-nilai angka">' + esc(X.n === null ? '—' : dbRpPendek(X.n)) + ' ›</span></div>';
  }

  // ---------- PEMICU ----------
  function kartuPemicu(B) {
    if (B.galat) return '';
    const isi = B.pemicu.length ? B.pemicu.map((r) => '<div class="db-baris db-ketuk awas-teks"' + daftar('pemicu:' + r.id, { judul: r.nama, baris: [['Bulan ini', r.teks], ['Bulan lalu (' + B.pendekLalu + ')', r.teksLalu], ['Perubahan', r.deltaTeks]], tujuan: r.tujuan, ke: 'layarnya', catatan: 'Cara hitung: ' + r.sumberRumus }) + '><span class="db-nama">' + esc(r.nama) + '</span><span class="ket">' + esc(r.teksLalu + ' → ' + r.teks) + '</span><span class="db-nilai">' + esc(r.deltaTeks.split(' vs ')[0]) + ' ›</span></div>').join('')
      : '<div class="menolak">Tidak ada biaya per satuan yang naik lebih dari ' + esc(B.ambangPemicu) + '% dibanding ' + esc(B.pendekLalu) + ' (' + esc(B.nPemicu) + ' pemicu bisa dihitung).</div>';
    return '<div class="kartu db-kartu db-pemicu">' + kepala('Pemicu biaya yang naik', B.periode + ' vs ' + B.pendekLalu + ' · ambang ' + B.ambangPemicu + '%', 'sumber:pemicu', B.sumber, B.tujuan) + isi + '</div>';
  }

  // ---------- STOK ----------
  function kartuStok(S) {
    if (S.galat) return '<div class="kartu db-kartu db-stok">' + galat(S) + '</div>';
    // dua kelompok supaya 10 detik cukup: yang HAMPIR HABIS dulu (hari tersisa tersedikit), lalu yang TERBANYAK di gudang; bilah satu skala kg
    const awas = S.merek.filter((m) => m.awas).sort((a, b) => a.urut - b.urut || a.kg - b.kg).slice(0, 6);   // owner 26 Nov 2026 (B127): di bawah stok minimum per barang
    const banyak = S.merek.filter((m) => awas.indexOf(m) < 0).slice(0, 6);
    const maks = Math.max(1, ...awas.concat(banyak).map((m) => Math.max(0, m.kg)));
    const sisa = S.merek.length - awas.length - banyak.length;
    const baris = (m, i) => '<div class="db-baris db-ketuk' + (m.awas ? ' awas-teks' : '') + '"' + daftar('stok:' + m.nama, { judul: m.nama, baris: [['Sisa menurut buku', dbKg(m.kg)], ['Laju jual', m.laju > 0 ? dbKg(m.laju) + '/hari' : 'tidak ada gerak keluar']].concat([['Perkiraan', m.minus ? 'buku MINUS — cocokkan' : dbHari(m.hari)]]).concat(m.batasTeks ? [['Stok minimum', m.batasTeks]] : []), tujuan: S.tujuan, ke: S.sumber }) + '>'
      + '<span class="db-nama">' + esc(m.nama) + '</span><svg class="db-bilah" viewBox="0 0 100 10" preserveAspectRatio="none"><rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x db-stok-isi' + (m.awas ? ' awas' : '') + '" style="--i:' + i + '" x="0" y="1.5" width="' + dbPersen(Math.max(0, m.kg), maks).toFixed(2) + '" height="7"></rect></svg>'
      + '<span class="db-nilai">' + esc(dbKg(m.kg) + ' · ' + (m.minus ? 'minus' : dbHari(m.hari))) + '</span></div>';
    const isi = !S.merek.length ? '<div class="menolak">Belum ada beras karung di buku gudang.</div>'
      : (awas.length ? '<div class="db-sub awas-teks">Di bawah stok minimum · ' + esc(S.batasTeks || ('≤ ' + S.ambangHari + ' hari')) + ' · atau buku minus</div>' + awas.map(baris).join('') : '<div class="ket">Tidak ada merek di bawah stok minimum (' + esc(S.batasTeks || ('≤ ' + S.ambangHari + ' hari')) + ').</div>')
        + (banyak.length ? '<div class="db-sub">Terbanyak di gudang</div>' + banyak.map((m, i) => baris(m, i + awas.length)).join('') : '');
    return '<div class="kartu db-kartu db-stok">' + kepala('Stok per merek', S.periode, 'sumber:stok', S.sumber, S.tujuan, tetap()) + isi
      + (sisa > 0 ? '<div class="ket db-ketuk" data-db-ke="sumber:stok">' + esc('+' + sisa + ' merek lain di Stok › Gudang') + ' ›</div>' : '')
      + (S.smTujuan ? (reg['sumber:stokMin'] = { judul: 'Stok minimum', baris: [], tujuan: S.smTujuan, ke: 'Stok › Gudang' }, '<div class="ket db-ketuk" data-db-ke="sumber:stokMin" data-k="db-atur-stokmin">Atur stok minimum per barang (hari atau kg) ›</div>') : '')
      + barisGudang(S.gudang) + '</div>';
  }

  // owner 26 Nov 2026 (B49 B50 B53 B54 A62): GUDANG — buku minus (semua jenis buku, dengan rupiah), tugas terbuka, kemasan bertanggal, beras hilang bulan ini.
  // DL.dbStok.gudang = gudang-logika gdDasbor apa adanya (angka yang sama dengan Stok › Tugas gudang); tiap baris diketuk = rincian, ketuk lagi = layarnya.
  function barisGudang(G) {
    if (!G) return ''; if (G.galat) return '<div class="ket awas-teks" data-k="db-gudang-galat">Tugas gudang gagal dihitung: ' + esc(G.galat) + '</div>';
    const r = (id, nama, nilai, awas, isi) => '<div class="db-baris db-ketuk' + (awas ? ' awas-teks' : '') + '"' + daftar('gudang:' + id, isi) + '><span class="db-nama">' + esc(nama) + '</span><span class="db-nilai">' + esc(nilai) + '</span></div>';
    const ke = 'Stok › Tugas gudang'; const M = G.minus, T = G.tugas, K = G.kemasan, B = G.buang;
    return '<div class="db-sub" data-k="db-gudang">Gudang</div>'
      + r('minus', 'Buku minus', M.n ? M.n + ' · ' + RP(M.rp) : 'tidak ada', M.n > 0, { judul: 'Buku stok minus', baris: M.top.map((x) => [x.nama, x.teks + (x.dinilai ? ' · ' + RP(x.rp) : ' · belum bisa dinilai')]).concat([['Ringkas', M.kalimat]]), tujuan: G.tujuan, ke })
      + r('tugas', 'Tugas gudang terbuka', T.n ? T.n + ' di ' + T.nJenis + ' jenis' : 'beres', T.awas, { judul: 'Tugas gudang yang terbuka', baris: T.terbuka.length ? T.terbuka.map((x) => [x.nama, x.n + ' · ' + x.ket]) : [['Keadaan', 'semua beres']], tujuan: G.tujuan, ke })
      + r('kemasan', 'Kemasan bertanggal', K.lewat ? K.lewat + ' lewat' + (K.dekat ? ' · ' + K.dekat + ' dekat' : '') : K.dekat ? K.dekat + ' ≤ ' + K.ambang + ' hari' : 'aman', K.lewat > 0, { judul: 'Kemasan · baik dipakai sebelum', baris: K.nama.length ? K.nama.map((n) => [n, '']) : [['Keadaan', 'tidak ada yang dekat']], tujuan: G.tujuan, ke })
      + (B.diarsip ? '' : r('hilang', 'Beras hilang ' + B.nama, dbKg(B.hilangKg) + ' · ' + RP(-B.hilangRp), B.menutup === false, { judul: 'Beras hilang & rusak per jenis · ' + B.nama, baris: B.jenis.map((x) => [x.jenis, dbKg(x.kg) + ' · ' + RP(-x.rp) + (x.rusakKg ? ' · rusak ' + dbKg(x.rusakKg) : '')]).concat([['Ringkas', B.kalimat]]), tujuan: G.tujuan, ke }));
  }

  // ---------- WADAH ----------
  function kartuWadah(S) {
    if (S.galat) return '';
    const isi = S.wadah.length ? '<div class="db-wadah">' + S.wadah.map((w, i) => {
      const t = w.diketahui ? Math.max(0, Math.min(1, w.bagian)) * 40 : 0;
      const cek = !w.aktif ? 'belum aktif' : w.dicek ? '✓ ' + w.hasilTeks + (w.jamCek ? ' ' + dbJam(w.jamCek) : '') : 'belum dicek';
      return '<div class="db-wadah-sel db-ketuk' + (w.perluIsi ? ' awas-teks' : '') + '"' + daftar('wadah:' + w.nama, { judul: w.no + ' · ' + w.nama, baris: [['Merek', w.merek || '—']].concat(w.banding ? [['Banding takar', w.banding]] : []).concat([['Isi', w.diketahui ? '±' + dbKg(w.isiKg) + ' dari ' + dbKg(w.penuhKg) + (w.perluIsi ? ' · perlu diisi ulang' : '') : 'belum diketahui'], ['Terakhir diisi', w.terakhirTanggal ? dbTgl(w.terakhirTanggal) + ' ' + dbJam(w.terakhirJam) : '—'], ['Cek tutup ' + dbTgl(S.hariCek), cek]]), tujuan: S.wadahTujuan, ke: S.wadahSumber }) + '>'
        + '<svg class="db-gelas" viewBox="0 0 30 46" role="img" aria-label="' + esc(w.nama) + '"><rect class="db-gelas-badan" x="1" y="1" width="28" height="44" rx="4"></rect>'
        + (w.diketahui ? '<rect class="db-tumbuh-y db-gelas-isi' + (w.perluIsi ? ' awas' : '') + '" style="--i:' + i + '" x="3" y="' + (43 - t).toFixed(2) + '" width="24" height="' + t.toFixed(2) + '" rx="2"></rect>' : '<text x="15" y="28" text-anchor="middle" class="db-gelas-tanya">?</text>')
        + '</svg><div class="db-wadah-teks"><b>' + esc(w.no) + '</b> ' + esc(w.nama) + '</div>'
        + (w.merek && w.merek !== w.nama ? '<div class="db-wadah-teks ket">' + esc(w.merek) + '</div>' : '')
        + (w.banding ? '<div class="db-wadah-teks ket">' + esc(w.banding) + '</div>' : '')
        + '<div class="db-wadah-teks angka">' + esc(w.diketahui ? '±' + dbKg(w.isiKg) : '? kg') + '</div>'
        + '<div class="db-wadah-teks ket">isi ' + esc(w.terakhirTanggal ? dbTgl(w.terakhirTanggal) + ' ' + dbJam(w.terakhirJam) : '—') + '</div>'
        + '<div class="db-wadah-teks ket' + (w.aktif && !w.dicek ? ' awas-teks' : '') + '">' + esc(cek) + '</div></div>';
    }).join('') + '</div>' : '<div class="menolak">Belum ada wadah literan yang diatur.</div>';
    return '<div class="kartu db-kartu db-wadah-kartu">' + kepala('Wadah literan', 'cek tutup ' + dbTgl(S.hariCek) + ': ' + S.nDicek + ' dari ' + S.nAktif + ' wadah aktif' + (S.perluIsi ? ' · ' + S.perluIsi + ' perlu diisi' : ''), 'sumber:wadah', S.wadahSumber, S.wadahTujuan, tetap()) + isi + '</div>';
  }

  // ---------- PIUTANG & UTANG PEMASOK ----------
  function kartuTagihan(G) {
    if (G.galat) return '<div class="kartu db-kartu db-tagihan">' + galat(G) + '</div>';
    const P = G.piutang, U = G.pemasok;
    const tumpuk = (bagian, total, awalan) => { let x = 0; return '<svg class="db-bilah db-bilah-tumpuk" viewBox="0 0 100 10" preserveAspectRatio="none">' + (total > 0 ? bagian.filter((b) => b.rp > 0).map((b, i) => { const w = dbPersen(b.rp, total); const s = '<rect class="db-tumbuh-x ' + esc(b.kelas) + '" style="--i:' + i + '" x="' + x.toFixed(3) + '" y="0" width="' + w.toFixed(3) + '" height="10"' + daftar(awalan + b.id, b.isi) + '></rect>'; x += w; return s; }).join('') : '<rect class="db-rel" x="0" y="4" width="100" height="2"></rect>') + '</svg>'; };
    const bagP = P.perStatus.map((s) => ({ id: s.status, rp: s.rp, kelas: 'db-st-' + s.status, isi: { judul: 'Bon pelanggan · ' + s.kata, baris: [['Orang', String(s.n)], ['Sisa bon', RP(s.rp)]], tujuan: P.tujuan, ke: P.sumber } }));
    const bagU = [{ id: 'lewat', rp: U.rpLewat, kelas: 'db-st-janjiLewat', isi: { judul: 'Bon pemasok lewat tempo', baris: [['Bon', String(U.lewat.length)], ['Sisa', RP(U.rpLewat)]], tujuan: U.tujuan, ke: U.sumber } },
      { id: 'dekat', rp: U.rpDekat, kelas: 'db-st-perluTagih', isi: { judul: 'Bon pemasok jatuh tempo ≤ ' + U.dekatHari + ' hari', baris: [['Bon', String(U.dekat.length)], ['Sisa', RP(U.rpDekat)]], tujuan: U.tujuan, ke: U.sumber } },
      { id: 'jauh', rp: U.rpJauh, kelas: 'db-st-baru', isi: { judul: 'Bon pemasok, tempo masih jauh', baris: [['Bon', String(U.nJauh)], ['Sisa', RP(U.rpJauh)]], tujuan: U.tujuan, ke: U.sumber } },
      { id: 'tanpa', rp: U.rpTanpaTempo, kelas: 'db-st-menunggu', isi: { judul: 'Bon pemasok tanpa tempo', baris: [['Bon', String(U.nTanpaTempo)], ['Sisa', RP(U.rpTanpaTempo)]], tujuan: U.tujuan, ke: U.sumber, catatan: 'Tempo belum disepakati — jatuh temponya tidak diramal.' } }];
    const baris = (d, id) => '<div class="db-baris db-ketuk' + (d.awas ? ' awas-teks' : '') + '"' + daftar(id, d.isi) + '><span class="db-nama">' + esc(d.nama) + '</span><span class="ket">' + esc(d.ket) + '</span><span class="db-nilai angka">' + esc(RP(d.rp)) + ' ›</span></div>';
    const jatuhP = P.jatuh.slice(0, 4).map((b) => baris({ nama: b.nama, ket: b.kata, rp: b.sisa, awas: true, isi: { judul: b.nama, baris: [['Sisa bon', RP(b.sisa)], ['Keadaan', b.kata], ['', b.ket]], tujuan: b.tujuan, ke: P.sumber } }, 'piutang:' + b.kunci)).join('');
    const jatuhU = U.lewat.concat(U.dekat).slice(0, 4).map((b) => baris({ nama: b.pemasok, ket: b.tempoTeks, rp: b.sisa, awas: U.lewat.indexOf(b) >= 0, isi: { judul: b.pemasok + ' · bon ' + dbTgl(b.tanggal), baris: [['Sisa', RP(b.sisa)], ['Tempo', b.tempoTeks]], tujuan: b.tujuan, ke: U.sumber } }, 'pemasok:' + b.id)).join('');
    return '<div class="kartu db-kartu db-tagihan">' + kepala('Piutang pelanggan', G.periode, 'sumber:piutang', P.sumber, P.tujuan, tetap())
      + '<div class="db-angka-baris">' + lampuDb('piutang') + '<span class="angka db-angka-kecil">' + esc(RP(P.total)) + '</span><span class="ket">' + esc(P.n + ' nama' + (P.nota && !P.nota.galat ? ' · per nota: lewat jatuh tempo ' + RP(P.nota.lewat) : ' · jatuh tempo ' + P.nJatuh + ' nama ' + RP(P.rpJatuh))) + '</span></div>'
      // owner 26 Nov 2026 (B29 · B30 · B31): jatuh tempo PER NOTA — bon kemarin tidak lagi ikut "jatuh tempo" hanya karena bon tertua orangnya sudah tua
      + (P.nota && !P.nota.galat ? '<div class="ket db-ketuk' + (P.nota.lewat > 0 ? ' awas-teks' : '') + '" data-k="db-per-nota"' + daftar('piutang:nota', { judul: 'Piutang per nota', baris: [['Lewat jatuh tempo', RP(P.nota.lewat) + ' · ' + P.nota.nLewat + ' nota · ' + P.nota.orangLewat + ' orang'], ['Jatuh tempo hari ini', RP(P.nota.hariIni)], ['Jatuh tempo 7 hari ke depan', RP(P.nota.minggu)], ['Belum jatuh tempo', RP(P.nota.nanti)]].concat(P.nota.tanpa ? [['Tanpa tanggal', RP(P.nota.tanpa)]] : []).concat(P.nota.menutup ? [] : [['TIDAK MENUTUP', 'selisih ' + RP(P.nota.selisih) + ' — laporkan']]), tujuan: P.notaTujuan, ke: 'Pelanggan › Bon › Jatuh tempo' }) + '>'
        + esc('Jatuh tempo hari ini ' + RP(P.nota.hariIni) + ' · 7 hari ke depan ' + RP(P.nota.minggu) + (P.nota.menutup ? '' : ' · per nota TIDAK MENUTUP')) + ' ›</div>' : '')
      + (P.hariTagih && !P.hariTagih.galat && P.hariTagih.nyala ? '<div class="ket' + (P.hariTagih.hariIni && P.hariTagih.n ? ' awas-teks' : '') + '" data-k="db-hari-tagih">' + esc(P.hariTagih.teks) + '</div>' : '')
      + (P.kg && P.kg.teks ? '<div class="ket" data-k="db-bon-kg">' + esc(P.kg.teks) + '</div>' : '')
      // B35 (owner 27 Nov 2026): bon belum jatuh tempo milik pelanggan yang 2 dari 3 bon terakhirnya lunas lewat jatuh tempo — tagih lebih awal
      + (P.telat && !P.telat.galat ? '<div class="ket db-ketuk' + (P.telat.n ? ' awas-teks' : '') + '" data-k="db-telat"' + daftar('piutang:telat', { judul: 'Diperkirakan telat bayar', baris: (P.telat.daftar.length ? P.telat.daftar.map((o) => [o.nama, RP(o.rp) + ' · ' + o.kalimat]) : [['Keadaan', P.telat.kalimat]])
        .concat(P.telat.nLewat ? [['Sudah lewat jatuh tempo (orang yang biasanya telat)', P.telat.nLewat + ' nota · ' + RP(P.telat.rpLewat)]] : []).concat(P.telat.nTanpa ? [['Belum bisa diperkirakan', P.telat.nTanpa + ' pelanggan (belum pernah melunasi bon)']] : []), tujuan: P.telatTujuan, ke: 'Pelanggan › Bon › Jatuh tempo', catatan: P.telat.rumus }) + '>'
        + esc(P.telat.n ? 'Diperkirakan telat: ' + P.telat.n + ' orang · ' + RP(P.telat.rp) + ' belum jatuh tempo' : 'Diperkirakan telat: tidak ada') + ' ›</div>' : '')
      + tumpuk(bagP, P.total, 'piutangS:') + '<div class="db-legenda">' + P.perStatus.filter((s) => s.n).map((s) => '<span><i class="db-titik db-st-' + esc(s.status) + '"></i>' + esc(s.kata + ' ' + s.n) + '</span>').join('') + '</div>'
      + (jatuhP || '<div class="menolak">Tidak ada bon pelanggan yang lewat janji, waktunya ditagih, atau macet.</div>')
      + (P.nJatuh > 4 ? '<div class="ket db-ketuk" data-db-ke="sumber:piutang">+' + esc(P.nJatuh - 4) + ' nama lain ›</div>' : '')
      // B3 (owner 18 Nov 2026): bayar di tempat yang uangnya belum disetor — MERAH, atas nama pengantarnya; lewat hari = kini bon biasa
      + (G.antar && G.antar.cod && G.antar.cod.length ? '<div class="ket awas-teks" data-k="db-cod">' + esc(G.antar.kalimat) + '</div>'
        + G.antar.cod.slice(0, 4).map((x) => baris({ nama: x.noSJ + ' · ' + x.nama, ket: (x.pengantar || 'pengantar') + ' · ' + tanggalPendek(x.tanggal) + (x.lewat ? ' · lewat hari, kini bon biasa' : ' · hari ini'), rp: x.sisa, awas: true,
          isi: { judul: 'Bayar di tempat ' + x.noSJ, baris: [['Pembeli', x.nama], ['Pengantar', x.pengantar || '—'], ['Belum disetor', RP(x.sisa)]], tujuan: x.tujuan, ke: G.antar.sumber } }, 'cod:' + x.noSJ)).join('') : '')
      // B2 (owner 17 Nov 2026): faktur pelanggan usaha lewat / segera jatuh tempo (≤ 3 hari)
      + (G.faktur && G.faktur.n ? '<div class="ket" data-k="db-faktur">Faktur jatuh tempo · ' + esc(G.faktur.nLewat + ' lewat ' + RP(G.faktur.rpLewat) + ' · ' + (G.faktur.n - G.faktur.nLewat) + ' segera ' + RP(G.faktur.rpSegera)) + '</div>'
        + G.faktur.daftar.map((f) => baris({ nama: f.no + ' · ' + f.nama, ket: f.ket, rp: f.sisa, awas: f.awas, isi: { judul: 'Faktur ' + f.no, baris: [['Pembeli', f.nama], ['Sisa', RP(f.sisa)], ['', f.ket]], tujuan: f.tujuan, ke: G.faktur.sumber } }, 'faktur:' + f.no)).join('') : '')
      // B4 (owner 18 Nov 2026): order rutin yang perlu dibuat & pesanan yang dikirim ≤ 2 hari lagi; stok yang kurang untuk pesanan (merah)
      + (G.pesanan && (G.pesanan.nIngat || G.pesanan.nDekat || G.pesanan.stok.length) ? '<div class="ket" data-k="db-pesanan">Pesanan · ' + esc((G.pesanan.nIngat ? G.pesanan.nIngat + ' order rutin perlu dibuat · ' : '') + G.pesanan.nDekat + ' dikirim ≤ 2 hari') + '</div>'
        + G.pesanan.ingat.map((x) => '<div class="db-baris db-ketuk' + (x.awas ? ' awas-teks' : '') + '"' + daftar('psi:' + x.id, { judul: 'Order rutin ' + x.nama, baris: [['Kirim', tanggalPendek(x.tanggal)], ['', x.ket]], tujuan: x.tujuan, ke: G.pesanan.sumber })
          + '><span class="db-nama">' + esc(x.nama) + '</span><span class="ket">' + esc(x.ket) + '</span><span class="db-nilai">buat ›</span></div>').join('')
        + G.pesanan.dekat.map((x) => baris({ nama: x.nama, ket: x.ket, rp: x.rp, awas: false, isi: { judul: 'Pesanan ' + x.nama, baris: [['', x.ket], ['Perkiraan', RP(x.rp)]], tujuan: x.tujuan, ke: G.pesanan.sumber } }, 'psd:' + x.id)).join('')
        + G.pesanan.stok.map((t, i) => '<div class="ket awas-teks" data-k="db-ps-stok-' + i + '">' + esc(t) + '</div>').join('') : '')
      + kepala('Utang ke pemasok', U.nBon + ' bon · ' + U.nPemasok + ' pemasok', 'sumber:pemasok', U.sumber, U.tujuan)
      + '<div class="db-angka-baris"><span class="angka db-angka-kecil">' + esc(RP(U.total)) + '</span><span class="ket">' + esc(U.lewat.length + ' lewat tempo · ' + U.dekat.length + ' jatuh ≤ ' + U.dekatHari + ' hari · ' + U.nTanpaTempo + ' tanpa tempo') + '</span></div>'
      + tumpuk(bagU, U.total, 'pemasokS:')
      + (jatuhU || '<div class="menolak">Tidak ada bon pemasok yang lewat atau dekat jatuh tempo.</div>')
      + '<div class="ket' + (U.kurang ? ' awas-teks' : '') + '">' + esc(U.cukupTeks) + '</div></div>';
  }

  // ---------- tooltip ----------
  const tip = () => akar.querySelector('.db-tip');
  // ---------- MUTU USAHA (paket brief awal 9 Okt) — lima KPI, tiap baris diketuk = rincian, ketuk lagi = layar sumbernya ----------
  function kartuMutu(Q) {
    if (!Q) return '';
    if (Q.galat) return '<div class="kartu db-kartu db-mutu">' + galat(Q) + '</div>';
    const pc = (x) => (x === null || x === undefined ? '—' : DESIMAL(Math.round(x * 10) / 10) + '%');
    const baris = (id, nama, nilai, awas, isi) => '<div class="db-baris db-ketuk' + (awas ? ' awas-teks' : '') + '"' + daftar('mutu:' + id, isi) + '><span class="db-nama">' + esc(nama) + '</span><span class="db-nilai">' + esc(nilai) + '</span></div>';
    const salah = (id, nama, x) => baris(id, nama, 'gagal dihitung', true, { judul: nama, baris: [['Galat', x.galat]], tujuan: null, ke: '' });
    const T = Q.tertagih, U = Q.umur, M = Q.merek, H = Q.het, R = Q.mutu; const out = [];
    out.push(T.galat ? salah('tertagih', 'Bon tertagih', T) : baris('tertagih', 'Rata-rata bon tertagih', T.rataTeks, false, { judul: 'Rata-rata hari bon tertagih', baris: [['Periode', T.periodeTeks || T.hari + ' hari terakhir'], ['Rata-rata', T.rataTeks], ['Keterangan', T.teks]], tujuan: T.tujuan, ke: 'Pelanggan › Bon' }));
    out.push(U.galat ? salah('umur', 'Umur stok', U) : baris('umur', 'Lambat laku', (U.lambat ? U.lambat + ' barang' : 'tidak ada') + (U.lewatSimpan ? ' · ' + U.lewatSimpan + ' lewat batas simpan' : ''), U.lambat > 0 || U.lewatSimpan > 0, { judul: 'Umur & putaran stok', baris: [['Lambat laku', U.lambat ? U.lambat + ' barang' + (U.namaLambat.length ? ' (' + U.namaLambat.join(', ') + (U.lambat > 3 ? ', …' : '') + ')' : '') : 'tidak ada'], ['Lewat batas simpan ' + U.batasSimpan + ' hari', U.lewatSimpan ? U.lewatSimpan + ' barang · ' + DESIMAL(Math.round(U.kgLewat)) + ' kg' : 'tidak ada'], ['Stok tertua', U.tertua ? U.tertua.nama + ' · ' + U.tertua.hari + ' hari' : 'belum bisa dihitung'], ['Perputaran merek', U.putaran === null ? 'belum bisa dihitung' : DESIMAL(Math.round(U.putaran * 10) / 10) + '× / ' + U.periodeHari + ' hari']], tujuan: U.tujuan, ke: 'Stok › Umur & putaran' }));
    if (M.galat) out.push(salah('merek', 'Per merek', M));
    else if (M.arsip) out.push(baris('merek', 'Merek teratas ' + M.nama, 'rincian ikut arsip', false, { judul: 'Per merek ' + M.nama, baris: [['Keadaan', 'bulan sudah ditutup buku']], tujuan: M.tujuan, ke: 'Laporan › Laba' }));
    else {
      const top = M.teratas[0];
      out.push(baris('merek', 'Margin teratas ' + M.nama, top ? top.merek + ' ' + dbRpPendek(top.margin) : 'belum ada jualan', M.menutup === false, { judul: 'Merek teratas menurut margin · ' + M.nama, baris: M.teratas.map((x, i) => [(i + 1) + '. ' + x.merek, RP(Math.round(x.margin)) + ' · ' + pc(x.pct)]).concat(M.menutup === false ? [['Peringatan', 'per merek TIDAK menutup ke laba kotor Laporan — buka Laporan']] : []), tujuan: M.tujuan, ke: 'Laporan › Laba › Per merek' }));
      // paket Susut (owner 26 Nov 2026): susut bulan ini vs target, merek kuning / merah, opname bulan ini — DL.dbMutu (susut-harga-logika) apa adanya
      const SS = Q.susut;
      if (SS && SS.galat) out.push(salah('susut', 'Susut beras', SS));
      else if (SS) {
        const st = SS.status === 'diAtas' ? 'di atas target ' + pc(SS.target) : SS.status === 'diBawah' ? 'target ' + pc(SS.target) : 'target —';
        out.push(baris('susut', 'Susut beras ' + M.nama, pc(SS.pct) + ' · ' + st + (SS.merah.length ? ' · ' + SS.merah.length + ' merah' : '') + (SS.kuning.length ? ' · ' + SS.kuning.length + ' kuning' : ''), SS.status === 'diAtas' || SS.merah.length > 0,
          { judul: 'Susut % se-toko · ' + M.nama, baris: [['Susut bulan ini', pc(SS.pct)], ['Target', pc(SS.target) + (SS.targetDariOwner ? ' (owner)' : ' (' + SS.targetAsal + ')')], ['Merah (di atas ' + pc(SS.ambangMerah) + ')', SS.merah.length ? SS.merah.slice(0, 6).join(', ') + (SS.merah.length > 6 ? ', …' : '') : 'tidak ada'], ['Kuning (di atas ' + pc(SS.ambangKuning) + ')', SS.kuning.length ? SS.kuning.slice(0, 6).join(', ') + (SS.kuning.length > 6 ? ', …' : '') : 'tidak ada']], tujuan: SS.tujuan, ke: 'Laporan › Laba › Susut' }));
        const O = SS.opname; out.push(baris('opname', 'Opname ' + M.nama, O.n ? O.nDihitung + ' dari ' + O.n + ' dihitung' : 'tidak ada stok', O.nBelum > 0, { judul: 'Opname bulan ini', baris: [['Sudah dihitung', O.nDihitung + ' dari ' + O.n + ' barang'], ['Belum', O.belum.length ? O.belum.join(', ') + (O.nBelum > O.belum.length ? ', …' : '') : 'tidak ada'], ['Keterangan', O.kalimat]], tujuan: SS.opnameTujuan, ke: 'Stok › Cocokkan' }));
      } else out.push(baris('susut', 'Susut beras ' + M.nama, pc(M.susutPct) + (M.susutTinggi ? ' · ' + M.susutTinggi + ' merek tinggi' : ''), M.susutTinggi > 0, { judul: 'Susut % se-toko · ' + M.nama, baris: [['Susut', pc(M.susutPct)], ['Merek di atas ambang', String(M.susutTinggi || 0)]], tujuan: M.tujuan, ke: 'Laporan › Laba › Per merek' }));
    }
    out.push(H.galat ? salah('het', 'HET', H) : baris('het', 'Harga di atas HET', H.keadaan === 'belum' || H.keadaan === 'kosong' ? 'belum dipetakan' : String(H.nAtas || 0), (H.nAtas || 0) > 0, { judul: 'HET beras', baris: [['Keadaan', H.judul]], tujuan: H.tujuan, ke: 'Harga › Katalog' }));
    // paket HPP & harga minimum (owner 26 Nov 2026): harga yang DIPAKAI KASIR di bawah harga minimum + modal & biaya per kg dekat / lewat HET
    const HM = Q.harga;
    if (HM && HM.galat) out.push(salah('minimum', 'Harga minimum', HM));
    else if (HM) {
      out.push(baris('minimum', 'Harga di bawah minimum', HM.keadaanMin === 'tanpaBiaya' ? 'belum bisa dihitung' : String(HM.nBawah), HM.nBawah > 0, { judul: 'Harga kasir di bawah harga minimum', baris: [['Biaya toko per kg', HM.biayaKg === null ? 'belum bisa dihitung' : RP(Math.round(HM.biayaKg))]].concat(HM.bawah.map((x) => [x.judul, RP(x.n) + ' < ' + RP(x.minimum)])).concat([['Keterangan', HM.kalimatMin]]), tujuan: HM.tujuan, ke: 'Harga › Katalog' }));
      out.push(baris('dekatHet', 'Modal + biaya dekat HET', HM.keadaanHet === 'ada' ? (HM.nLewat ? HM.nLewat + ' lewat · ' : '') + HM.nDekat + ' dekat' : HM.keadaanHet === 'belumDipetakan' ? 'belum dipetakan' : 'belum bisa dihitung', HM.nLewat + HM.nDekat > 0, { judul: 'Modal + biaya per kg vs HET', baris: HM.alarm.map((x) => [x.merk + ' · ' + x.kategori, RP(Math.round(x.biayaKg)) + '/kg · HET ' + RP(x.het) + (x.status === 'lewat' ? ' · LEWAT' : '')]).concat([['Keterangan', HM.kalimatHet]]), tujuan: HM.tujuan, ke: 'Harga › Katalog › Harga minimum & HET' }));
    }
    // paket Stok minus, label & kepatuhan (owner 26 Nov 2026): kalender kepatuhan & cek aturan bulanan (patuh-logika ptDasbor apa adanya)
    const P = Q.patuh;
    if (P && P.galat) out.push(salah('patuh', 'Kalender kepatuhan', P));
    else if (P) out.push(baris('patuh', 'Kalender kepatuhan', P.n ? P.n + ' urusan' + (P.lewat ? ' · ' + P.lewat + ' lewat' : '') : P.basi.length ? 'cek aturan belum' : 'tidak ada yang dekat', P.lewat > 0 || P.basi.length > 0,
      { judul: 'Kalender kepatuhan', baris: (P.daftar.length ? P.daftar.map((x) => [x.nama, x.teks]) : [['Keadaan', P.kalimat]]).concat(P.basi.length ? [['Cek aturan > 30 hari / belum pernah', P.basi.join(', ')]] : []), tujuan: P.tujuan, ke: 'Laporan › Pajak › Kalender' }));
    out.push(R.galat ? salah('mutu', 'Mutu kedatangan', R) : baris('mutu', 'Kedatangan mutu AWAS', R.awas ? R.awas + ' kedatangan' : R.ditimbang || R.awas ? '0' : 'belum dicek', R.awas > 0, { judul: 'Timbang & mutu kedatangan', baris: [['Ditimbang', R.ditimbang + ' dari ' + R.kedatangan + ' kedatangan'], ['Kurang timbang', dbKg(R.kgKurang)], ['Mutu AWAS', String(R.awas)]], tujuan: R.tujuan, ke: 'Stok › Barang masuk' }));
    return '<div class="kartu db-kartu db-mutu">' + kepala('Mutu usaha', Q.periode, 'sumber:mutu', Q.sumber, Q.tujuan) + out.join('') + '</div>';
  }
  // B5 (owner 18 Nov 2026): PELANGGAN USAHA bulan ini — porsi laba kotor & omzet, tiga teratas, faktur lewat tempo. Angka apa adanya dari DL.dbB2b (= Laporan › Laba › Per pelanggan)
  function kartuB2b(Q) {
    if (!Q) return '';
    if (Q.galat) return '<div class="kartu db-kartu db-b2b">' + galat(Q) + '</div>';
    const pc = (x) => (x === null || x === undefined ? '—' : DESIMAL(Math.round(x * 10) / 10) + '%');
    const baris = (id, nama, nilai, awas, isi) => '<div class="db-baris db-ketuk' + (awas ? ' awas-teks' : '') + '"' + daftar('b2b:' + id, isi) + '><span class="db-nama">' + esc(nama) + '</span><span class="db-nilai">' + esc(nilai) + '</span></div>';
    const ke = 'Laporan › Laba › Per pelanggan'; const out = [];
    if (Q.arsip) out.push('<div class="ket">' + esc(Q.kalimat) + '</div>');
    else if (!Q.ada) out.push('<div class="ket">Belum ada pelanggan usaha (bertingkat harga) yang belanja ' + esc(Q.nama) + '. Pasang tingkat di Pelanggan › Harga pelanggan.</div>');
    else {
      out.push(baris('porsi', 'Porsi laba kotor', pc(Q.porsiLaba) + ' · ' + dbRpPendek(Q.laba || 0), Q.menutup === false, { judul: 'Pelanggan usaha · ' + Q.nama, baris: [['Laba kotor pelanggan usaha', RP(Math.round(Q.laba || 0)) + ' (' + pc(Q.porsiLaba) + ')'], ['Omzet barang', RP(Math.round(Q.omzet)) + ' (' + pc(Q.porsiOmzet) + ')'], ['Pelanggan usaha belanja', String(Q.nOrang)]]
        .concat(Q.tingkat.map((t) => [t.nama, (t.laba === null ? 'laba belum bisa dihitung' : RP(Math.round(t.laba)) + ' · ' + pc(t.porsiLaba)) + ' · ' + t.nOrang + ' pelanggan'])).concat(Q.menutup === false ? [['Peringatan', 'per pelanggan TIDAK menutup ke laba kotor Laporan — buka Laporan']] : []), tujuan: Q.tujuan, ke }));
      out.push('<div class="db-pita-b2b" title="porsi laba kotor pelanggan usaha"><i style="width: ' + Math.max(0, Math.min(100, Q.porsiLaba || 0)).toFixed(1) + '%;"></i></div>');
      const top = Q.teratas[0];
      out.push(baris('teratas', 'Teratas', top ? top.nama + ' ' + dbRpPendek(top.laba) : 'laba belum bisa dihitung', false, { judul: 'Pelanggan usaha teratas menurut laba kotor · ' + Q.nama, baris: Q.teratas.map((x, i) => [(i + 1) + '. ' + x.nama + ' (' + x.tingkat + ')', RP(Math.round(x.laba)) + ' · margin ' + pc(x.pct) + ' · bon dibayar ' + x.rata]), tujuan: Q.tujuan, ke }));
    }
    if (!Q.arsip) out.push(baris('lewat', 'Faktur lewat tempo', Q.lewat.n ? Q.lewat.n + ' · ' + dbRpPendek(Q.lewat.rp) : 'tidak ada', Q.lewat.n > 0, { judul: 'Faktur lewat jatuh tempo', baris: [['Jumlah', Q.lewat.n + ' faktur'], ['Sisa', RP(Math.round(Q.lewat.rp))], ['Pelanggan usaha bayar bon', 'rata-rata ' + Q.rataUsaha]], tujuan: { ke: 'pelanggan', keluarga: 'bon' }, ke: 'Pelanggan › Bon' }));
    return '<div class="kartu db-kartu db-b2b" data-k="db-b2b">' + kepala('Pelanggan usaha', Q.periode, 'sumber:b2b', Q.sumber, Q.tujuan) + out.join('') + '</div>';
  }

  // PONDASI TOKO (owner 24 Nov 2026): delapan lampu — utang dibanding harta, bon 30 hari, kas cukup berapa hari, hasil atas harta, ambil pribadi, laju tumbuh,
  // ketergantungan pemasok, prakiraan 30 hari. Angka apa adanya dari DL.dbPondasi (= pondasi-logika → fungsi sumber layar lain); ketuk baris = rincian & sumbernya.
  function kartuPondasi(Q) {
    if (!Q) return '';
    if (Q.galat) return '<div class="kartu db-kartu db-pondasi">' + galat(Q) + '</div>';
    const warna = { merah: 'merah', amber: 'kuning', hijau: 'hijau', tanpa: '' };
    const out = Q.lampu.map((l) => '<div class="db-baris db-ketuk db-pd-baris' + (l.lampu === 'merah' || l.keadaan === 'galat' ? ' awas-teks' : '') + '"'
      + daftar('pondasi:' + l.id, { judul: l.nama, baris: l.rinci.concat([['Keadaan', l.kalimat]]), tujuan: l.tujuan, ke: l.sumber, catatan: l.ambang ? 'Warna: ' + l.ambang : '' })
      + '><span class="db-nama"><i class="db-lampu ' + warna[l.lampu] + '"></i>' + esc(l.nama) + '</span><span class="db-nilai">' + esc(l.nilai) + '</span></div>');
    return '<div class="kartu db-kartu db-pondasi" data-k="db-pondasi">' + kepala('Pondasi toko', Q.periode, 'sumber:pondasi', Q.sumber, Q.tujuan, tetap()) + out.join('') + '<div class="ket">' + esc(Q.kalimat) + '</div></div>';
  }

  // PAKET KPI LABA (owner 24 Nov 2026): target harian (lampu laju jam), kas minimum, tiga margin + mark-up + BPS, siklus uang, 3 nota terbesar hari ini,
  // kedatangan lewat batas HPP, lama pemenuhan pesanan. Angka apa adanya dari DL.dbKpi (= kpi-laba-logika → fungsi sumber layar lain).
  function kartuKpi(Q) {
    if (!Q) return '';
    if (Q.galat) return '<div class="kartu db-kartu db-kpi">' + galat(Q) + '</div>';
    const pc = (x) => (x === null || x === undefined || !isFinite(x) ? '—' : (x < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(x) * 10) / 10) + '%');
    const baris = (id, nama, nilai, awas, isi, kelas) => '<div class="db-baris db-ketuk' + (awas ? ' awas-teks' : '') + (kelas ? ' ' + kelas : '') + '"' + daftar('kpi:' + id, isi) + '><span class="db-nama">' + nama + '</span><span class="db-nilai">' + esc(nilai) + '</span></div>';
    const salah = (id, nama, x) => baris(id, esc(nama), 'gagal dihitung', true, { judul: nama, baris: [['Galat', x.galat]], tujuan: null, ke: '' });
    const out = []; const T = Q.target, K = Q.kas, M = Q.margin, S = Q.siklus, N = Q.nota, H = Q.hpp, P = Q.pesanan;
    if (T.galat) out.push(salah('target', 'Target harian', T));
    else if (T.lampu === 'tanpa') out.push(baris('target', 'Target omzet hari ini', 'belum ada', false, { judul: 'Target omzet harian', baris: [['Keadaan', T.teks]], tujuan: T.tujuan, ke: T.sumber }));
    else {
      const w = dbPersen(T.omzet, T.target); const lj = dbPersen(T.laju, T.target);
      out.push('<div class="db-kpi-target db-ketuk"' + daftar('kpi:target', { judul: 'Omzet hari ini vs target', baris: [['Omzet', RP(T.omzet)], ['Target', RP(T.target) + ' (' + T.targetTeks + ')'], ['Seharusnya sampai jam ini', RP(T.laju)], ['Keadaan', T.teks]], tujuan: T.tujuan, ke: T.sumber, catatan: 'Hijau = target tercapai · kuning = sesuai laju jam toko (' + 'buka–tutup cincin jam Ringkasan) · merah = di bawah laju.' })
        + '><div class="db-kpi-kepala"><i class="db-lampu ' + esc(T.lampu) + '"></i><span class="db-nama">Target omzet hari ini' + (saringAktif() ? ' <span class="db-tetap" title="tidak ikut saringan">hari ini</span>' : '') + '</span><span class="db-nilai angka">' + esc(dbRpPendek(T.omzet) + ' / ' + dbRpPendek(T.target)) + '</span></div>'
        + '<svg class="db-bilah db-bilah-target" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" aria-label="Omzet dibanding target"><rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x db-target-' + esc(T.lampu) + '" x="0" y="0" width="' + w.toFixed(2) + '" height="10"></rect><rect class="db-laju" x="' + Math.max(0, lj - 0.4).toFixed(2) + '" y="0" width="0.8" height="10"></rect></svg>'
        + '<div class="ket' + (T.lampu === 'merah' ? ' awas-teks' : '') + '">' + esc(T.teks) + '</div></div>');
    }
    if (K.galat) out.push(salah('kas', 'Kas minimum', K));
    else if (K.nyala) out.push(baris('kas', 'Kas vs ambang minimum', K.kas === null ? 'belum bisa' : (K.bawah ? 'KURANG ' + dbRpPendek(K.kurang) : 'aman · ' + dbRpPendek(K.kas)), !!K.bawah, { judul: 'Ambang kas minimum', baris: [['Kas (4 tempat)', K.kas === null ? 'titik kas belum disetel' : RP(K.kas)], ['Ambang owner', RP(K.batas)]].concat(K.tempat.map((x) => [x.nama, x.n === null ? '—' : RP(x.n)])).concat([['Keadaan', K.teks]]), tujuan: K.tujuan || null, ke: K.sumber }));
    if (M.galat) out.push(salah('margin', 'Margin bulan ini', M));
    else {
      const tg = (id) => M.tangga.find((x) => x.id === id) || { pct: null, rp: null, markup: null };
      out.push(baris('margin', lampuDb('margin') + 'Margin ' + esc(M.nama) + ' · kotor / usaha / bersih', pc(tg('kotor').pct) + ' / ' + pc(tg('usaha').pct) + ' / ' + pc(tg('bersih').pct), M.menutup === false || (tg('bersih').rp !== null && tg('bersih').rp < 0),
        { judul: 'Margin & mark-up · ' + M.nama, baris: M.tangga.map((r) => [r.nama, (r.rp === null ? '—' : RP(Math.round(r.rp))) + ' · ' + pc(r.pct) + ' · mark-up ' + pc(r.markup)])
          .concat(M.jenis.map((g) => ['· ' + g.nama, g.pct === null ? (g.keadaan === 'kosong' ? 'tidak ada jualan' : 'belum bisa dihitung') : pc(g.pct) + ' · mark-up ' + pc(g.markup)]))
          .concat([['Grosir toko · BPS', pc(M.bps.tokoGrosir) + ' · ' + pc(M.bps.grosir)], ['Ecer toko · BPS', pc(M.bps.tokoEcer) + ' · ' + pc(M.bps.eceran)]]).concat(M.menutup === false ? [['Peringatan', 'angka margin TIDAK menutup ke Laporan — buka Laporan']] : []),
          tujuan: Q.tujuan, ke: 'Laporan › Laba', catatan: 'Penyebut sama: omzet ber-HPP. BPS: ' + M.bps.sumber + ' — konteks, bukan target.' }));
      out.push('<div class="ket" data-k="db-kpi-bps">Pembanding ' + esc(M.bps.pendek) + ': grosir toko ' + esc(pc(M.bps.tokoGrosir)) + ' vs BPS ' + esc(pc(M.bps.grosir)) + ' · ecer toko ' + esc(pc(M.bps.tokoEcer)) + ' vs BPS ' + esc(pc(M.bps.eceran)) + '</div>');
    }
    // P1 A112 (owner 27 Nov 2026: untung per kg = baris TETAP di kartu ini): bulan itu vs bulan lalu & target untung per kg (setelan Harga) — kpi-laba klKgBulan apa adanya
    const G = Q.kg;
    if (G && G.galat) out.push(salah('kg', 'Untung per kg', G));
    else if (G && G.marginKg !== null && G.marginKg !== undefined) out.push(baris('kg', 'Untung per kg <span class="ket">' + (G.lalu && G.lalu.marginKg !== null ? esc(G.lalu.pendek) + ' ' + RP(Math.round(G.lalu.marginKg)) : esc(G.nama)) + '</span>', RP(Math.round(G.marginKg)) + '/kg', G.target.rp > 0 && G.marginKg < G.target.rp,
      { judul: 'Untung per kg · ' + G.nama, baris: [['Untung per kg', RP(Math.round(G.marginKg)) + '/kg'], ['HPP per kg', RP(Math.round(G.hppKg)) + '/kg'], ['Harga jual per kg', RP(Math.round(G.jualKg)) + '/kg'], ['Target untung', G.target.teks]]
        .concat(G.lalu ? [[G.lalu.nama, G.lalu.marginKg === null ? '—' : RP(Math.round(G.lalu.marginKg)) + '/kg']] : []).concat(G.target.rp > 0 ? [['Merek di bawah target', G.nBawah + ' dari ' + (G.nBawah + G.nCapai)]] : []).concat(G.bawah.slice(0, 5).map((x) => ['· ' + x.merek, RP(Math.round(x.marginKg)) + '/kg'])),
        tujuan: G.tujuan, ke: 'Laporan › Laba › Per merek', catatan: 'Untung per kg = laba kotor ÷ kg nota yang modalnya tercatat (sesudah nego & retur) — sama dengan Laporan › Biaya.' }));
    if (S.galat) out.push(salah('siklus', 'Siklus uang', S));
    else out.push(baris('siklus', 'Siklus uang' + (saringAktif() ? ' <span class="db-tetap" title="tidak ikut saringan">90 hari</span>' : ''), S.hari === null ? 'belum bisa' : '±' + DESIMAL(Math.round(S.hari * 10) / 10) + ' hari', false, { judul: 'Siklus uang (hari)', baris: S.bagian.map((x) => [(x.tanda < 0 ? '− ' : '+ ') + x.nama, (x.hari === null ? '—' : DESIMAL(Math.round(x.hari * 10) / 10) + ' hari') + ' · ' + x.ket]).concat([['Keadaan', S.kalimat]]), tujuan: (S.bagian[0] || {}).tujuan || null, ke: 'Stok › Umur & putaran' }));
    // A121 (owner 27 Nov 2026): modal tertahan di stok dalam rupiah + biaya modalnya (bunga setelan owner, bawaan 6 % per tahun) — kpi-laba klModalTertahan apa adanya
    const MT = Q.modal;
    if (MT && MT.galat) out.push(salah('modal', 'Modal tertahan di stok', MT));
    else if (MT && MT.rata !== null) out.push(baris('modal', 'Modal tertahan di stok <span class="ket">' + esc(dbTgl(MT.dari) + (MT.dari !== MT.sampai ? '–' + dbTgl(MT.sampai) : '')) + '</span>', dbRpPendek(MT.rata) + (MT.bunga > 0 ? ' · biaya ' + dbRpPendek(MT.biaya) : ''), false,
      { judul: 'Modal tertahan di stok · ' + dbTgl(MT.dari) + ' – ' + dbTgl(MT.sampai), baris: [['Rata-rata nilai stok', RP(Math.round(MT.rata))], ['Nilai stok ' + dbTgl(MT.sampai), RP(Math.round(MT.kini))], ['Bunga modal', MT.bunga > 0 ? DESIMAL(MT.bunga) + '% per tahun' + (MT.dariOwner ? '' : ' (bawaan)') : 'mati'],
        ['Biaya modal ' + MT.nHari + ' hari', RP(Math.round(MT.biaya))], ['± sebulan', RP(Math.round(MT.sebulan))]].concat(MT.buku.slice(0, 4).map((x) => ['· ' + x.nama, RP(Math.round(x.rata)) + (MT.bunga > 0 ? ' · biaya ' + RP(Math.round(x.biaya)) : '')])),
        tujuan: { ke: 'sistem', sistem: 'target' }, ke: 'Menu › Toko ini › Target & ambang', catatan: MT.rumus + '. Bukan uang keluar — tidak memotong laba bersih.' }));
    if (P && !P.galat && P.keadaan === 'ada') out.push(baris('pesanan', 'Pesanan dipenuhi', P.nota.teks + ' → nota', false, { judul: 'Lama pemenuhan pesanan · ' + P.hari + ' hari terakhir', baris: [['Dipesan → diantar', P.antar.teks + ' · ' + P.antar.n + ' pesanan'], ['Dipesan → jadi nota', P.nota.teks + ' · ' + P.nota.n + ' pesanan']], tujuan: { ke: 'jual', lembar: 'pesanan' }, ke: 'Jual › Pesanan' }));
    // paket tanggal janji (owner 27 Nov 2026, sensus B55 B58 B60 B61 B65): tepat janji dua arah + yang lewat janji — janji-logika jnRingkas apa adanya
    const JN = Q.janji;
    if (JN && JN.galat) out.push(salah('janji', 'Tepat janji', JN));
    else if (JN && JN.keadaan === 'ada') {
      const nil = (r) => (r.n ? pc(r.pct) : '—'); const kosong = !JN.pemasok.n && !JN.antar.n;
      out.push(baris('janji', 'Tepat janji · pemasok / antar', (kosong ? 'belum ada tanggal janji' : nil(JN.pemasok) + ' / ' + nil(JN.antar)) + (JN.lewat.length ? ' · ' + JN.lewat.length + ' lewat' : ''), JN.lewat.length > 0,
        { judul: 'Tepat janji · ' + JN.hari + ' hari terakhir', baris: [['Dari pemasok', JN.kalimatPemasok], ['Antar ke pelanggan', JN.kalimatAntar]].concat(JN.lewat.slice(0, 6).map((x) => ['Lewat janji', x.teks]))
          .concat([['Toleransi telat', 'pemasok ' + JN.tol.pemasok + ' hari · antar ' + JN.tol.antar + ' hari (setelan owner)']]), tujuan: JN.tujuan, ke: JN.sumber, catatan: 'Dihitung dari janji PERTAMA; yang belum punya tanggal janji disebut, tidak dianggap tepat waktu.' }));
    }
    if (H && !H.galat && H.ada && H.daftar.length) out.push(baris('hpp', 'Kedatangan lewat batas HPP', H.daftar.length + ' baris', true, { judul: 'HPP per kg lewat batas · ' + H.nama, baris: H.daftar.slice(0, 6).map((x) => [x.merk + ' ' + dbTgl(x.tanggal), RP(Math.round(x.hppPerKg)) + '/kg · batas ' + RP(x.batas)]), tujuan: { ke: 'stok', lembar: 'masuk' }, ke: 'Stok › Barang masuk' }));
    if (N && !N.galat && N.daftar.length) { out.push('<div class="db-sub">Nota terbesar ' + esc(N.judul || 'hari ini') + '</div>'); N.daftar.forEach((o, i) => out.push(baris('nota' + i, esc((i + 1) + '. ' + (o.nama || 'tanpa nama')) + ' <span class="ket">' + esc(dbJam(o.jam) + ' · ' + o.caraTeks) + '</span>', RP(o.total) + ' ›', false, { judul: 'Nota ' + (o.nama || 'tanpa nama'), baris: [['Total', RP(o.total)], ['Jam', dbJam(o.jam)], ['Cara bayar', o.caraTeks], ['Baris', String(o.nBaris)]], tujuan: o.tujuan, ke: 'Jual › Riwayat' }))); }
    return '<div class="kartu db-kartu db-kpi" data-k="db-kpi">' + kepala('Margin & target', Q.periode, 'sumber:kpi', Q.sumber, Q.tujuan) + out.join('') + '</div>';
  }

  // owner 26 Nov 2026 (B113): ENAM BULAN — laba bersih & biaya per bulan (Laporan › Biaya) · kas, piutang, stok per akhir bulan (Laporan › Pondasi). D.enam = dasbor-logika dbEnam.
  function kartuEnam(E) {
    if (!E) return ''; if (E.galat) return '<div class="kartu db-kartu db-enam">' + galat(E) + '</div>';
    const grafik = (id, nilai, kelas, judul, tujuanDari, kata) => { const W = nilai.length * 100; const ada = nilai.filter((v) => v !== null); const maks = Math.max(1, ...ada.map((v) => Math.abs(v))); const minus = ada.some((v) => v < 0); const nol = minus ? 50 : 100; const sk = minus ? 46 : 94;
      return '<div class="db-enam-satu"><div class="db-legenda"><span><i class="db-titik ' + kelas + '"></i>' + esc(judul) + '</span><span class="ket">' + esc(ada.length ? 'tertinggi ' + RP(Math.max(...ada.map((v) => Math.abs(v)))) : 'belum bisa dihitung') + '</span></div>'
        + '<svg class="db-grafik db-grafik-pendek" viewBox="0 0 ' + W + ' 100" preserveAspectRatio="none" role="img" aria-label="' + esc(judul) + '"><line class="db-dasar" x1="0" y1="' + nol + '" x2="' + W + '" y2="' + nol + '"></line>'
        + nilai.map((v, i) => { const isi = { judul: judul + ' · ' + kata(i), baris: [[judul, v === null ? 'belum bisa dihitung' : RP(v)]], tujuan: tujuanDari(i), ke: id === 'laba' || id === 'biaya' ? E.sumber : E.posisiSumber };
          const h = v === null ? 0 : Math.max(0.8, Math.abs(v) / maks * sk);
          return '<g class="db-kol"' + daftar('enam:' + id + ':' + i, isi) + '><rect class="db-kena" x="' + (i * 100) + '" y="0" width="100" height="100"></rect>' + (v === null ? '<rect class="db-rel" x="' + (i * 100 + 20) + '" y="' + (nol - 1) + '" width="60" height="1"></rect>'
            : '<rect class="db-tumbuh-y ' + kelas + (v < 0 ? ' db-enam-minus' : '') + '" style="--i:' + i + '" x="' + (i * 100 + 14) + '" y="' + (v < 0 ? nol : nol - h).toFixed(2) + '" width="72" height="' + h.toFixed(2) + '"></rect>') + '</g>'; }).join('') + '</svg></div>'; };
    const kata = (i) => E.bulan[i].pendek + (E.bulan[i].berjalan ? ' (berjalan)' : ''); const tuj = (i) => E.bulan[i].tujuan;
    const P = E.posisi; const kataP = (i) => (P[i] ? P[i].nama + (P[i].berjalan ? ' (sekarang)' : ' (akhir bulan)') : ''); const tujP = () => E.posisiTujuan;
    const sumbu = (daftar2) => '<div class="db-sumbu">' + daftar2.map((x) => '<span class="' + (x.berjalan ? 'aktif' : '') + '">' + esc(x.pendek || x.nama) + '</span>').join('') + '</div>';
    return '<div class="kartu db-kartu db-enam" data-k="db-enam">' + kepala('Enam bulan', E.periode, 'sumber:enam', E.sumber, E.tujuan, tetap('rentang sendiri · tidak ikut saringan'))
      + '<div class="db-enam-kisi"><div>' + grafik('laba', E.bulan.map((b) => (b.tanpaCatatan ? null : b.labaBersih)), 'db-margin', 'Laba bersih', tuj, kata) + grafik('biaya', E.bulan.map((b) => (b.tanpaCatatan ? null : b.semuaBiaya)), 'db-omzet', 'Biaya', tuj, kata) + sumbu(E.bulan) + '</div>'
      + (P.length ? '<div>' + grafik('kas', P.map((p) => p.kas), 'db-enam-kas', 'Kas (4 tempat)', tujP, kataP) + grafik('piu', P.map((p) => p.piutang), 'db-enam-piu', 'Piutang pelanggan', tujP, kataP)
        + grafik('stk', P.map((p) => p.stok), 'db-enam-stk', 'Stok (nilai modal)', tujP, kataP) + sumbu(P) + (P.some((p) => !p.ada) ? '<div class="ket">' + esc('Bulan tanpa batang: ' + (P.find((p) => !p.ada) || {}).kenapa) + '</div>' : '') + '</div>' : '')
      + '</div>' + (E.sebelumBuku ? '<div class="ket">' + esc(E.sebelumBuku) + '</div>' : '') + '<div class="ket db-pandu">Ketuk batang untuk angkanya · ketuk lagi untuk membuka layarnya</div></div>';
  }
  // owner 26 Nov 2026 (B109): cap "data per HH.MM" — satu keadaan data untuk semua kartu (satu sumber data); diganti tiap menit tanpa menggambar ulang
  // B68 (owner 27 Nov 2026): PEMBELIAN per hari · minggu · bulan dari kedatangan barang (D.beli = dasbor-logika dbBeli → susut-harga-logika shTrenBeli / shPembelian).
  // Batang bertumpuk: BON (dibayar nanti) di bawah, dibayar langsung di atas; batang bulan = "+ Pembelian" HPP periode Laporan › Bulanan. Ketuk batang = angka, lagi = layarnya.
  function kartuBeli(Bl) {
    if (!Bl) return ''; if (Bl.galat) return '<div class="kartu db-kartu db-beli">' + galat(Bl) + '</div>';
    const T = Bl.tren[rentangBeli] || Bl.tren.bulan; const n = T.batang.length; const W = n * 100;
    const pita = '<div class="pita db-rentang" data-k="db-beli-pita">' + SH_RENTANG_BELI.map(([id, nm]) => '<div class="seg' + (id === T.rentang ? ' aktif' : '') + '" data-db-beli="' + id + '">' + esc(nm) + '</div>').join('') + '</div>';
    const kol = T.batang.map((b, i) => { const hb = b.absen ? 0 : dbPersen(Math.max(0, b.bon), T.maks) * 0.94; const hl = b.absen ? 0 : dbPersen(Math.max(0, b.langsung), T.maks) * 0.94;
      const isi = { judul: 'Pembelian · ' + b.panjang, baris: b.absen ? [['Keadaan', 'sebelum toko mencatat / ikut arsip tutup buku']] : [['Pembelian', RP(b.rp) + ' · ' + b.n + ' kedatangan'], ['Bon (dibayar nanti)', RP(b.bon) + ' · ' + b.nBon + ' kedatangan'], ['Dibayar langsung', RP(b.langsung)], ['Beras datang', dbKg(b.kg)]].concat(b.berjalan ? [['', 'masih berjalan']] : []), tujuan: b.absen ? null : b.tujuan, ke: T.rentang === 'bulan' ? 'Laporan › Bulanan' : 'Stok › Barang masuk', catatan: T.rumus };
      return '<g class="db-kol' + (b.berjalan ? ' berjalan' : '') + (b.absen ? ' absen' : '') + '"' + daftar('beli:' + b.id, isi) + '><rect class="db-kena" x="' + (i * 100) + '" y="0" width="100" height="100"></rect>'
        + (b.absen ? '<rect class="db-rel" x="' + (i * 100 + 20) + '" y="99" width="60" height="1"></rect>' : '<rect class="db-beli-bon db-tumbuh-y" style="--i:' + i + '" x="' + (i * 100 + 14) + '" y="' + (100 - hb).toFixed(2) + '" width="72" height="' + hb.toFixed(2) + '"></rect>'
          + '<rect class="db-beli-langsung db-tumbuh-y" style="--i:' + i + '" x="' + (i * 100 + 14) + '" y="' + (100 - hb - hl).toFixed(2) + '" width="72" height="' + hl.toFixed(2) + '"></rect>') + '</g>'; }).join('');
    const sumbu = '<div class="db-sumbu">' + T.batang.map((b) => '<span class="' + (b.berjalan ? 'aktif' : '') + '">' + esc(b.label) + '</span>').join('') + '</div>';
    const P = Bl.saring; const M = Bl.bulan;
    const angka = (id, nama, X) => '<div class="db-baris db-ketuk" data-k="db-beli-' + id + '"' + daftar('beli:' + id, { judul: 'Pembelian · ' + nama, baris: [['Pembelian', RP(X.rp) + ' · ' + X.n + ' kedatangan'], ['Bon (dibayar nanti)', RP(X.bon.rp) + ' · ' + X.bon.n], ['Dibayar langsung', RP(X.langsung.rp) + ' · ' + X.langsung.n], ['Beras datang', dbKg(X.kg)]]
      .concat(X.pemasok.slice(0, 3).map((g) => ['· ' + g.pemasok, RP(g.rp) + ' · ' + g.n + ' kedatangan'])).concat(X.dicatat ? [['Stok awal / saldo pembuka (bukan belanja)', RP(X.dicatat)]] : []), tujuan: Bl.tujuan, ke: Bl.sumber, catatan: Bl.rumus })
      + '><span class="db-nama">' + esc(nama) + '</span><span class="ket">' + esc(X.n + ' kedatangan · bon ' + dbRpPendek(X.bon.rp)) + '</span><span class="db-nilai angka">' + esc(RP(X.rp)) + ' ›</span></div>';
    return '<div class="kartu db-kartu db-beli" data-k="db-beli">' + kepala('Pembelian', T.periode + ' · ' + Bl.periode, 'sumber:beli', Bl.sumber, Bl.tujuan) + pita
      + '<div class="db-legenda"><span><i class="db-titik db-beli-bon"></i>Bon (dibayar nanti)</span><span><i class="db-titik db-beli-langsung"></i>Dibayar langsung</span><span class="ket">tertinggi ' + esc(RP(T.maks)) + '</span></div>'
      + '<svg class="db-grafik db-grafik-beli" viewBox="0 0 ' + W + ' 100" preserveAspectRatio="none" role="img" aria-label="Pembelian ' + esc(T.periode) + '"><line class="db-dasar" x1="0" y1="100" x2="' + W + '" y2="100"></line>' + kol + '</svg>' + sumbu
      + (P ? angka('periode', Bl.periodeNama, P) : '') + (M ? angka('bulan', Bl.bulanNama, M) : '')
      + '<div class="ket db-pandu">Ketuk batang untuk angkanya · ketuk lagi untuk membuka ' + esc(T.rentang === 'bulan' ? 'Laporan › Bulanan' : 'Stok › Barang masuk') + '</div></div>';
  }
  // P2 (owner 27 Nov 2026: A136 B112 B26): RAPOR BULAN — bulan ini vs bulan lalu vs target owner, % ubah & lampu; saklar Laba | Kas ("Dua-duanya"). D.rapor =
  // dasbor-logika dbRapor → rapor-bulan-logika rbRapor apa adanya. Bulan berjalan: angka yang menumpuk dibanding lewat perkiraan sebulan (disebut di kalimat).
  function kartuRapor(Q) {
    if (!Q) return ''; if (Q.galat) return '<div class="kartu db-kartu db-rapor">' + galat(Q) + '</div>';
    const R = modeRapor === 'kas' && Q.kas && !Q.kas.galat ? Q.kas : Q.laba;
    const pita = '<div class="pita db-rentang" data-k="db-rapor-pita">' + [['laba', 'Laba'], ['kas', 'Kas']].map(([id, nm]) => '<div class="seg' + (id === R.mode ? ' aktif' : '') + '" data-db-rapor="' + id + '">' + nm + '</div>').join('') + '</div>';
    const baris = R.baris.concat(R.mode === 'laba' ? R.sekarang : []).map((b) => {
      const arah = b.membaik === null || b.membaik === undefined ? '' : b.membaik ? ' db-naik' : ' db-turun';
      const isi = { judul: b.nama + ' · ' + R.nama, baris: [[R.nama + (b.perkiraan ? ' (sampai hari ini)' : ''), b.iniTeks]].concat(b.perkiraan ? [['Perkiraan sebulan', b.perkiraanTeks]] : []).concat(b.laluTeks !== undefined ? [[R.namaLalu, b.laluTeks], ['Perubahan', b.ubahTeks || '—']] : [])
        .concat(b.rpTeks ? [['Rupiah', b.rpTeks]] : []).concat(b.targetTeks ? [['Target owner', b.targetTeks + (b.lampuKata ? ' · ' + b.lampuKata : '')]] : [])
        .concat(b.catatan ? [['Sebab', b.catatan.sebab || '—'], ['Tindakan', b.catatan.tindakan || '—']] : []), tujuan: b.tujuan || R.tujuan, ke: b.tujuan ? 'layarnya' : R.sumber, catatan: b.ket || '' };
      return '<div class="db-baris db-ketuk db-rapor-baris' + (b.lampu === 'merah' ? ' awas-teks' : '') + '"' + daftar('rapor:' + R.mode + ':' + b.id, isi) + '><span class="db-nama">' + (b.lampu && b.lampu !== 'tanpa' ? '<i class="db-lampu ' + esc(b.lampu) + '"></i>' : '') + esc(b.nama) + '</span>'
        + '<span class="db-nilai angka">' + esc(b.iniTeks) + '</span><span class="ket db-rapor-ubah' + arah + '">' + esc(b.ubahTeks === undefined ? 'sekarang' : b.ubahTeks) + '</span></div>'; }).join('');
    return '<div class="kartu db-kartu db-rapor" data-k="db-rapor">' + kepala(Q.judul || 'Rapor bulan', Q.periode, 'sumber:rapor', Q.sumber, Q.tujuan) + pita
      + '<div class="db-rapor-kepala ket"><span>angka ' + esc(R.pendek) + '</span><span>vs ' + esc(R.pendekLalu) + '</span></div>' + baris
      + '<div class="ket db-pandu">' + esc(R.kalimat) + ' Ketuk baris untuk angka bulan lalu, target & sebabnya.</div></div>';
  }
  // P2 (owner 27 Nov 2026, B26): ARUS KAS BULAN INI — uang masuk, keluar, kas bersih vs bulan lalu + pembanding laba bersih (rbArusKas: intiBulan + rincian arus kas mesin)
  function kartuArusKas(Q) {
    if (!Q) return ''; if (Q.galat) return '<div class="kartu db-kartu db-arus">' + galat(Q) + '</div>'; const A = Q.arus; if (!A || A.galat) return '<div class="kartu db-kartu db-arus">' + galat(A || { galat: 'arus kas tidak ada' }) + '</div>';
    const W = Math.max(1, Math.abs(A.masuk), Math.abs(A.keluar));
    const bilah = (id, nama, n, lalu, kelas, rinci) => '<div class="db-baris db-ketuk"' + daftar('arus:' + id, { judul: nama + ' · ' + A.nama, baris: [[A.nama, RP(n)], [A.namaLalu, RP(lalu)]].concat((rinci || []).slice(0, 8).map((r) => ['· ' + r.nama, RP(r.n)])), tujuan: A.tujuan, ke: A.sumber })
      + '><span class="db-nama">' + esc(nama) + '</span><svg class="db-bilah" viewBox="0 0 100 10" preserveAspectRatio="none"><rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x ' + kelas + '" x="0" y="0" width="' + dbPersen(Math.abs(n), W).toFixed(2) + '" height="10"></rect></svg><span class="db-nilai angka">' + esc(RP(n)) + '</span></div>';
    return '<div class="kartu db-kartu db-arus" data-k="db-arus">' + kepala(A.berjalan ? 'Arus kas bulan ini' : 'Arus kas ' + A.nama, A.nama + (A.berjalan ? ' · sampai hari ini' : '') + ' vs ' + A.namaLalu, 'sumber:arus', A.sumber, A.tujuan)
      + '<div class="db-angka-baris"><span class="angka db-angka-kecil' + (A.bersih < 0 ? ' awas-teks' : '') + '">' + esc(RP(A.bersih)) + '</span><span class="ket">kas bersih' + esc(A.ubahBersih !== null ? ' · ' + (A.ubahBersih > 0 ? '▲ ' : '▼ ') + DESIMAL(Math.round(Math.abs(A.ubahBersih) * 10) / 10) + '% vs ' + A.namaLalu.split(' ')[0] : '') + '</span></div>'
      + bilah('masuk', 'Uang masuk', A.masuk, A.laluMasuk, 'db-arus-masuk', A.rinciMasuk) + bilah('keluar', 'Uang keluar', A.keluar, A.laluKeluar, 'db-arus-keluar', A.rinciKeluar)
      + '<div class="db-baris db-ketuk"' + daftar('arus:laba', { judul: 'Kas bersih vs laba bersih · ' + A.nama, baris: [['Kas bersih', RP(A.bersih)], ['Laba bersih', RP(A.labaBersih)], ['Beda', A.beda === null ? '—' : RP(A.beda)], ['Jual bon (laba, belum uang)', RP(A.bon)]], tujuan: A.tujuan, ke: A.sumber, catatan: 'Laba bersih ikut jual bon & tidak menghitung belanja stok; kas bersih menghitung uang yang benar-benar masuk dan keluar.' })
      + '><span class="db-nama">Laba bersih (pembanding)</span><span class="ket">' + esc(A.beda === null ? '' : 'beda ' + (A.beda >= 0 ? '+' : '−') + dbRpPendek(Math.abs(A.beda))) + '</span><span class="db-nilai angka">' + esc(RP(A.labaBersih)) + ' ›</span></div></div>';
  }
  let capKini = null;
  function pasangCap() { if (!capKini) return; akar.querySelectorAll('.db-kepala').forEach((k) => { if (!k.querySelector('.db-cap')) k.insertAdjacentHTML('beforeend', '<span class="db-cap"><i></i>' + esc(capKini.teks) + '</span>'); }); setelCap(capKini); }
  function setelCap(c) { capKini = c; akar.querySelectorAll('.db-cap').forEach((el) => { el.lastChild.textContent = c.teks; el.classList.toggle('awas', !!c.awas); el.classList.toggle('hidup', !!c.hidup); el.title = c.judul || ''; }); }

  function tutupTip() { pilih = null; const t = tip(); if (t) t.hidden = true; akar.querySelectorAll('.db-dipilih').forEach((el) => el.classList.remove('db-dipilih')); }
  function tampilTip(id, el) {
    const isi = reg[id]; const t = tip(); if (!isi || !t) return;
    akar.querySelectorAll('.db-dipilih').forEach((x) => x.classList.remove('db-dipilih')); el.classList.add('db-dipilih'); pilih = id;
    t.innerHTML = '<div class="label">' + esc(isi.judul) + '</div>' + isi.baris.map((b) => '<div class="db-tip-baris"><span>' + esc(b[0]) + '</span><b>' + esc(b[1]) + '</b></div>').join('')
      + (isi.catatan ? '<div class="ket">' + esc(isi.catatan) + '</div>' : '') + (isi.tujuan ? '<div class="db-tip-ke" data-db-ke="' + esc(id) + '">Buka ' + esc(isi.ke === 'layarnya' ? 'layarnya' : isi.ke) + ' ›</div>' : '');
    t.hidden = false;
    const a = akar.getBoundingClientRect(), r = el.getBoundingClientRect(); const lebar = t.offsetWidth;
    const kiri = Math.max(4, Math.min(a.width - lebar - 4, r.left - a.left + r.width / 2 - lebar / 2));
    t.style.left = Math.round(kiri) + 'px'; t.style.top = Math.round(r.bottom - a.top + 6) + 'px';
  }
  akar.addEventListener('click', (ev) => {
    if (kisi.klik(ev)) { tutupTip(); return; }   // desain ulang 26 Nov 2026: mode atur, buka/tutup rincian, saringan tanggal, headline
    const rg = ev.target.closest('[data-db-rentang]'); if (rg) { gantiRentang(rg.dataset.dbRentang); return; }
    const rr = ev.target.closest('[data-db-rapor]'); if (rr) { const m = rr.dataset.dbRapor === 'kas' ? 'kas' : 'laba'; if (m !== modeRapor) { modeRapor = m; try { localStorage.setItem(KUNCI_RAPOR, m); } catch (e) { /* abaikan */ } tutupTip(); gambar(null, false); } return; }
    const rb = ev.target.closest('[data-db-beli]'); if (rb) { const r = rb.dataset.dbBeli; if (r !== rentangBeli && SH_RENTANG_BELI.some((x) => x[0] === r)) { rentangBeli = r; try { localStorage.setItem(KUNCI_BELI, r); } catch (e) { /* abaikan */ } tutupTip(); gambar(null, false); } return; }
    const ke = ev.target.closest('[data-db-ke]'); if (ke) { const isi = reg[ke.dataset.dbKe]; tutupTip(); if (isi && isi.tujuan) opsi.keTujuan(isi.tujuan); return; }
    const el = ev.target.closest('[data-db]'); if (el) { const id = el.dataset.db; if (pilih === id) { const isi = reg[id]; tutupTip(); if (isi && isi.tujuan) opsi.keTujuan(isi.tujuan); } else tampilTip(id, el); return; }
    if (!ev.target.closest('.db-tip')) tutupTip();
  });
  akar.addEventListener('pointerover', (ev) => { if (ev.pointerType !== 'mouse' || kisi.sedangAtur()) return; const el = ev.target.closest('[data-db]'); if (el && el.dataset.db !== pilih) tampilTip(el.dataset.db, el); });

  // ---------- pasang ----------
  function gantiRentang(r) { if (r === rentang || !DB_RENTANG.some((x) => x[0] === r)) return; rentang = r; try { localStorage.setItem(KUNCI_RENTANG, r); } catch (e) { /* abaikan */ } opsi.mintaRentang(r); }
  /** Gambar seluruh dasbor dari hasil susunDasbor. masuk = animasi masuk ringan (buka dasbor / ganti rentang), bukan tiap data berubah.
   *  ekstra = { perhatian, cap } dari Ringkasan (headline & widget Perlu perhatian, cap "data per HH.MM"). */
  let perhatianKini = [];
  function gambar(hasil, masuk, ekstra) {
    if (hasil) D = hasil; if (ekstra && ekstra.perhatian) perhatianKini = ekstra.perhatian; if (ekstra && ekstra.cap) capKini = ekstra.cap;
    if (!D || kisi.menyeret()) return;
    const tadi = pilih; reg = {};
    // owner 26 Nov 2026: "besar kecilnya kartu bisa gua sesuaikan … fleksibel gua menyesuaikan ruang" — kartu lama UTUH, tiap kartu = panel berpegangan di kisi
    // 12 kolom yang merapat sendiri (dasbor-kisi.js; isi kartu lewat kartuPenuh). Dulu dua .db-lajur tetap (owner 3 Okt: bukan CSS columns — Safari/WebKit tidak
    // menggambar kartu beranimasi di dalam columns); kisi panel = CSS grid, jadi aturan itu tetap terjaga. Bawaan = urutan kartu lama.
    akar.innerHTML = kisi.html(D, perhatianKini, capKini) + '<div class="db-tip kartu" hidden></div>';
    pasangCap();   // owner 26 Nov 2026 (B109): cap "data per HH.MM" di kepala tiap kartu utuh
    kisi.sesudah();
    pilih = null; if (tadi && reg[tadi]) { const el = akar.querySelector('[data-db="' + (window.CSS && CSS.escape ? CSS.escape(tadi) : tadi) + '"]'); if (el) tampilTip(tadi, el); }
    if (masuk) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1400); }
  }
  /** Isi panel kartu: kartu lama Dasbor apa adanya (+ Enam bulan, kartu tambahan). */
  function kartuPenuh(id) {
    const P = { kHari: () => kartuHari(D.hari), kKpi: () => kartuKpi(D.kpi), kTren: () => kartuTren(D.tren), kBulan: () => kartuBulan(D.bulan), kPemicu: () => kartuPemicu(D.bulan), kStok: () => kartuStok(D.stok),
      kPondasi: () => kartuPondasi(D.pondasi), kWadah: () => kartuWadah(D.stok), kTagihan: () => kartuTagihan(D.tagihan), kMutu: () => kartuMutu(D.mutu), kB2b: () => kartuB2b(D.b2b), kEnam: () => kartuEnam(D.enam), kBeli: () => kartuBeli(D.beli), kRapor: () => kartuRapor(D.rapor), kArusKas: () => kartuArusKas(D.rapor) };
    return D && P[id] ? P[id]() : '';
  }
  const kisi = pasangKisi(akar, { kini: () => (opsi.kini ? opsi.kini() : new Date()), ingat: opsi.ingat, gantiSaring: () => { tutupTip(); if (opsi.mintaRentang) opsi.mintaRentang(rentang); else gambar(null, false); }, /* B94: Ringkasan menyusun ulang dengan saringan baru */ simpanWidget: opsi.simpanWidget || (async () => ({ ok: false, kabar: 'Tidak bisa menyimpan dari sini' })),
    keTujuan: (t) => opsi.keTujuan(t), kePerhatian: () => (opsi.kePerhatian ? opsi.kePerhatian() : null), daftar, kartuPenuh, gambarUlang: () => gambar(null, false) });
  return { gambar, rentang: () => rentang, saring: () => kisi.pil(), tutupTip, sedangAtur: () => kisi.sedangAtur(), adaWidget: (id) => kisi.adaWidget(id), cap: (c) => { const ada = !!capKini; capKini = c; if (!ada) pasangCap(); else setelCap(c); } };
}
