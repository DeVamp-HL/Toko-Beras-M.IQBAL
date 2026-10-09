// LAYAR RINGKASAN — DASBOR OWNER: GAMBAR (putaran 40). Angka dari dasbor-logika.js (satu sumber); di sini cuma geometri SVG, kata & ketukan.
//
// Grafik = SVG sendiri (tanpa pustaka, tanpa build, Chrome 80). Batang & bilah memakai preserveAspectRatio="none" dengan label HTML di luarnya,
// jadi tulisan tidak ikut tergencet di HP. Tiap bagian yang bisa diketuk membawa data-db → kartu kecil berisi angka di baliknya + tombol ke layar
// sumbernya. Ketuk pertama = tooltip (iPad/HP), ketuk kedua di tempat yang sama = pindah ke layar sumbernya; di Mac tooltip muncul saat kursor lewat
// dan klik langsung pindah. Animasi masuk ringan hanya saat dasbor dibuka / rentang diganti (data yang berubah tidak memutar ulang animasinya);
// prefers-reduced-motion dihormati (ringkasan.css). Warna dari token identitas.css → mode gelap ikut sendiri. BACA SAJA.
import { esc } from '../inti/dom.js';
import { RP, DESIMAL, tanggalPendek } from '../inti/format.js';
import { DB_RENTANG } from './dasbor-logika.js';

const KUNCI_RENTANG = 'miqbal_baru_dasbor_rentang';
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
  // daftarkan satu bagian yang bisa diketuk: { judul, baris: [[kata, nilai]], tujuan, ke (nama layar), catatan }
  const daftar = (id, isi) => { reg[id] = isi; return ' data-db="' + esc(id) + '"'; };
  const kepala = (judul, periode, idSumber, sumber, tujuan) => { reg[idSumber] = { judul: sumber, baris: [], tujuan, ke: sumber };
    return '<div class="db-kepala"><div class="label">' + esc(judul) + '</div><div class="db-periode">' + esc(periode) + '</div>'
      + '<span class="db-sumber" data-db-ke="' + esc(idSumber) + '" title="Buka ' + esc(sumber) + '">' + esc(sumber) + ' ›</span></div>'; };
  const galat = (x) => '<div class="menolak awas-teks">Bagian ini gagal dihitung (' + esc(x.galat) + ') — kelompok lain tetap. Buka layar sumbernya untuk angka yang sama.</div>';

  // ---------- HARI INI ----------
  function kartuHari(H) {
    if (H.galat) return '<div class="kartu hero db-kartu db-hari">' + galat(H) + '</div>';
    const kas = H.kas; const pos = kas.ada ? kas.tempat.filter((t) => t.n > 0) : []; const totalPos = pos.reduce((a, t) => a + t.n, 0); let x = 0;
    const segmen = pos.map((t, i) => { const w = dbPersen(t.n, totalPos); const s = '<rect class="db-tumbuh-x db-kas-' + esc(t.id) + '" style="--i:' + i + '" x="' + x.toFixed(3) + '" y="0" width="' + w.toFixed(3) + '" height="10"' + daftar('kas:' + t.id, { judul: t.nama + ' · ' + H.periode, baris: [['Isi menurut buku', RP(t.n)], ['Semua tempat', RP(kas.total)], ['Dihitung dari', kas.titik]], tujuan: H.kasTujuan, ke: H.kasSumber }) + '></rect>'; x += w; return s; }).join('');
    const KC = H.karcis;
    return '<div class="kartu hero db-kartu db-hari">' + kepala('Hari ini', H.periode, 'sumber:hari', H.sumber, H.tujuan)
      + '<div class="db-dua"><div' + daftar('hari:omzet', { judul: 'Omzet · ' + H.periode, baris: [['Omzet (sesudah retur)', RP(H.omzet)], ['Nota', String(H.nota)]].concat(H.retur ? [['Retur & refund', RP(H.retur)]] : []).concat([['Tunai', RP(H.tunai)], ['QRIS', RP(H.qris)], ['Bon', RP(H.kredit) + ' · ' + H.nKredit + ' nota']]), tujuan: H.tujuan, ke: H.sumber }) + ' class="db-ketuk"><div class="label" style="color: var(--hero-label);">Omzet</div>'
      + '<div class="angka dagang db-angka-besar">' + esc(RP(H.omzet)) + '</div><div class="ket">' + esc(H.nota + ' nota' + (H.retur ? ' · sudah dikurangi retur ' + RP(H.retur) : '')) + '</div></div>'
      + '<div' + daftar('hari:laba', { judul: 'Laba kotor · ' + H.periode, baris: [['Laba kotor (margin)', RP(H.margin)]].concat(H.tanpaHpp ? [['Baris tanpa modal', H.tanpaHpp + ' baris — tidak ikut dihitung']] : []), tujuan: H.tujuan, ke: H.sumber }) + ' class="db-ketuk"><div class="label" style="color: var(--hero-label);">Laba kotor</div>'
      + '<div class="angka db-angka-sedang">' + esc(RP(H.margin)) + '</div><div class="ket">' + esc(H.tanpaHpp ? H.tanpaHpp + ' baris tanpa modal tidak ikut' : 'semua baris bermodal') + '</div></div></div>'
      + '<div class="db-sub">Kas per tempat' + (kas.ada ? ' · ' + esc(RP(kas.total)) + ' · ' + esc(kas.titik) : '') + '</div>'
      + (kas.ada ? '<svg class="db-bilah db-bilah-kas" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" aria-label="Kas per tempat">' + (segmen || '<rect class="db-rel" x="0" y="4" width="100" height="2"></rect>') + '</svg>'
        + '<div class="db-legenda">' + kas.tempat.map((t) => '<span' + daftar('kasL:' + t.id, { judul: t.nama + ' · ' + H.periode, baris: [['Isi menurut buku', RP(t.n)], ['Dihitung dari', kas.titik]], tujuan: H.kasTujuan, ke: H.kasSumber }) + ' class="db-ketuk' + (t.n < -0.5 ? ' awas-teks' : '') + '"><i class="db-titik db-kas-' + esc(t.id) + '"></i>' + esc(t.nama) + ' <b class="angka">' + esc(RP(t.n)) + '</b></span>').join('') + '</div>'
        + (kas.minus.length ? '<div class="ket awas-teks">' + esc(kas.minus.map((k) => kas.tempat.find((t) => t.id === k).nama).join(', ')) + ' MINUS menurut buku — ada pindah/keluar yang belum dicatat?</div>' : '')
        + (kas.cocok ? '' : '<div class="ket awas-teks">Jumlah per tempat tidak sama dengan kas mesin — laporkan.</div>')
        : '<div class="menolak">Titik kas belum ada — Tutup hari malam ini (Uang › Tutup hari) menyetelnya. Tanpa itu isi tiap tempat tidak ditebak.</div>')
      + '<div class="db-karcis db-ketuk' + (KC.n ? ' awas-teks' : '') + '"' + daftar('hari:karcis', { judul: 'Karcis kasir', baris: [['Karcis belum dirinci', KC.n + (KC.n ? ' · ' + RP(KC.rp) : '')], ['Nota jumlahnya belum pasti', String(KC.rapikan)], ['Karcis bertanggal hari ini', String(KC.hariIni)]], tujuan: H.karcisTujuan, ke: H.karcisSumber, catatan: 'Karcis = nota kasir yang baru nominalnya; barangnya belum dirinci, jadi modal & stoknya belum ikut.' }) + '>'
      + esc(KC.n ? KC.n + ' karcis kasir belum dirinci · ' + RP(KC.rp) : 'Tidak ada karcis kasir yang menunggu dirinci') + (KC.rapikan ? ' · ' + esc(KC.rapikan + ' nota perlu dirapikan') : '') + ' ›</div>'
      + '</div>';
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
    return '<div class="kartu db-kartu db-tren">' + kepala('Omzet & laba kotor', T.periode, 'sumber:tren', T.sumber, { ke: 'laporan', keluarga: T.rentang === 'hari' ? 'harian' : T.rentang === 'minggu' ? 'mingguan' : 'bulanan' }) + pita
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
    const top = kepala('Bulan ini', B.periode, 'sumber:bulan', B.sumber, B.tujuan);
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
      + '<div class="db-sub">Menuju titik impas</div>' + impas
      + '<div class="db-sub">Biaya per jenis · garis = jatah anggaran</div>' + biaya
      + '<div class="db-baris db-ketuk' + (B.susut > 0 ? ' awas-teks' : '') + '"' + daftar('bulan:susut', { judul: 'Susut & selisih stok · ' + B.periode, baris: [['Susut & selisih', RP(B.susut)], ['Baris', String(B.nSusut)]], tujuan: B.susutTujuan, ke: 'Stok › Cocokkan', catatan: 'Biaya yang tidak keluar dari laci — sudah ikut di biaya & laba bersih di atas.' }) + '><span class="db-nama">Susut & selisih stok</span><span></span><span class="db-nilai angka">' + esc(RP(B.susut)) + ' ›</span></div>'
      + (B.menutup ? '' : '<div class="ket awas-teks">Pemilahan biaya TIDAK MENUTUP ke mesin laba bulan ini — jangan dipakai memutuskan; laporkan.</div>')
      + '</div>';
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
    const awas = S.merek.filter((m) => m.awas).sort((a, b) => (a.minus ? -1 : a.hari) - (b.minus ? -1 : b.hari)).slice(0, 6);
    const banyak = S.merek.filter((m) => awas.indexOf(m) < 0).slice(0, 6);
    const maks = Math.max(1, ...awas.concat(banyak).map((m) => Math.max(0, m.kg)));
    const sisa = S.merek.length - awas.length - banyak.length;
    const baris = (m, i) => '<div class="db-baris db-ketuk' + (m.awas ? ' awas-teks' : '') + '"' + daftar('stok:' + m.nama, { judul: m.nama, baris: [['Sisa menurut buku', dbKg(m.kg)], ['Laju jual', m.laju > 0 ? dbKg(m.laju) + '/hari' : 'tidak ada gerak keluar']].concat([['Perkiraan', m.minus ? 'buku MINUS — cocokkan' : dbHari(m.hari)]]), tujuan: S.tujuan, ke: S.sumber }) + '>'
      + '<span class="db-nama">' + esc(m.nama) + '</span><svg class="db-bilah" viewBox="0 0 100 10" preserveAspectRatio="none"><rect class="db-rel" x="0" y="4" width="100" height="2"></rect><rect class="db-tumbuh-x db-stok-isi' + (m.awas ? ' awas' : '') + '" style="--i:' + i + '" x="0" y="1.5" width="' + dbPersen(Math.max(0, m.kg), maks).toFixed(2) + '" height="7"></rect></svg>'
      + '<span class="db-nilai">' + esc(dbKg(m.kg) + ' · ' + (m.minus ? 'minus' : dbHari(m.hari))) + '</span></div>';
    const isi = !S.merek.length ? '<div class="menolak">Belum ada beras karung di buku gudang.</div>'
      : (awas.length ? '<div class="db-sub awas-teks">Hampir habis · ≤ ' + esc(S.ambangHari) + ' hari atau buku minus</div>' + awas.map(baris).join('') : '<div class="ket">Tidak ada merek yang habis dalam ' + esc(S.ambangHari) + ' hari menurut laju jual.</div>')
        + (banyak.length ? '<div class="db-sub">Terbanyak di gudang</div>' + banyak.map((m, i) => baris(m, i + awas.length)).join('') : '');
    return '<div class="kartu db-kartu db-stok">' + kepala('Stok per merek', S.periode, 'sumber:stok', S.sumber, S.tujuan) + isi
      + (sisa > 0 ? '<div class="ket db-ketuk" data-db-ke="sumber:stok">' + esc('+' + sisa + ' merek lain di Stok › Gudang') + ' ›</div>' : '')
      + '</div>';
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
    return '<div class="kartu db-kartu db-wadah-kartu">' + kepala('Wadah literan', 'cek tutup ' + dbTgl(S.hariCek) + ': ' + S.nDicek + ' dari ' + S.nAktif + ' wadah aktif' + (S.perluIsi ? ' · ' + S.perluIsi + ' perlu diisi' : ''), 'sumber:wadah', S.wadahSumber, S.wadahTujuan) + isi + '</div>';
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
    return '<div class="kartu db-kartu db-tagihan">' + kepala('Piutang pelanggan', G.periode, 'sumber:piutang', P.sumber, P.tujuan)
      + '<div class="db-angka-baris"><span class="angka db-angka-kecil">' + esc(RP(P.total)) + '</span><span class="ket">' + esc(P.n + ' nama · jatuh tempo ' + P.nJatuh + ' nama ' + RP(P.rpJatuh)) + '</span></div>'
      + tumpuk(bagP, P.total, 'piutangS:') + '<div class="db-legenda">' + P.perStatus.filter((s) => s.n).map((s) => '<span><i class="db-titik db-st-' + esc(s.status) + '"></i>' + esc(s.kata + ' ' + s.n) + '</span>').join('') + '</div>'
      + (jatuhP || '<div class="menolak">Tidak ada bon pelanggan yang lewat janji, waktunya ditagih, atau macet.</div>')
      + (P.nJatuh > 4 ? '<div class="ket db-ketuk" data-db-ke="sumber:piutang">+' + esc(P.nJatuh - 4) + ' nama lain ›</div>' : '')
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
    out.push(U.galat ? salah('umur', 'Umur stok', U) : baris('umur', 'Lambat laku', U.lambat ? U.lambat + ' barang' : 'tidak ada', U.lambat > 0, { judul: 'Umur & putaran stok', baris: [['Lambat laku', U.lambat ? U.lambat + ' barang' + (U.namaLambat.length ? ' (' + U.namaLambat.join(', ') + (U.lambat > 3 ? ', …' : '') + ')' : '') : 'tidak ada'], ['Stok tertua', U.tertua ? U.tertua.nama + ' · ' + U.tertua.hari + ' hari' : 'belum bisa dihitung'], ['Perputaran merek', U.putaran === null ? 'belum bisa dihitung' : DESIMAL(Math.round(U.putaran * 10) / 10) + '× / ' + U.periodeHari + ' hari']], tujuan: U.tujuan, ke: 'Stok › Umur & putaran' }));
    if (M.galat) out.push(salah('merek', 'Per merek', M));
    else if (M.arsip) out.push(baris('merek', 'Merek teratas ' + M.nama, 'rincian ikut arsip', false, { judul: 'Per merek ' + M.nama, baris: [['Keadaan', 'bulan sudah ditutup buku']], tujuan: M.tujuan, ke: 'Laporan › Laba' }));
    else {
      const top = M.teratas[0];
      out.push(baris('merek', 'Margin teratas ' + M.nama, top ? top.merek + ' ' + dbRpPendek(top.margin) : 'belum ada jualan', M.menutup === false, { judul: 'Merek teratas menurut margin · ' + M.nama, baris: M.teratas.map((x, i) => [(i + 1) + '. ' + x.merek, RP(Math.round(x.margin)) + ' · ' + pc(x.pct)]).concat(M.menutup === false ? [['Peringatan', 'per merek TIDAK menutup ke laba kotor Laporan — buka Laporan']] : []), tujuan: M.tujuan, ke: 'Laporan › Laba › Per merek' }));
      out.push(baris('susut', 'Susut beras ' + M.nama, pc(M.susutPct) + (M.susutTinggi ? ' · ' + M.susutTinggi + ' merek tinggi' : ''), M.susutTinggi > 0, { judul: 'Susut % se-toko · ' + M.nama, baris: [['Susut', pc(M.susutPct)], ['Merek di atas ambang', String(M.susutTinggi || 0)]], tujuan: M.tujuan, ke: 'Laporan › Laba › Per merek' }));
    }
    out.push(H.galat ? salah('het', 'HET', H) : baris('het', 'Harga di atas HET', H.keadaan === 'belum' || H.keadaan === 'kosong' ? 'belum dipetakan' : String(H.nAtas || 0), (H.nAtas || 0) > 0, { judul: 'HET beras', baris: [['Keadaan', H.judul]], tujuan: H.tujuan, ke: 'Harga › Katalog' }));
    out.push(R.galat ? salah('mutu', 'Mutu kedatangan', R) : baris('mutu', 'Kedatangan mutu AWAS', R.awas ? R.awas + ' kedatangan' : R.ditimbang || R.awas ? '0' : 'belum dicek', R.awas > 0, { judul: 'Timbang & mutu kedatangan', baris: [['Ditimbang', R.ditimbang + ' dari ' + R.kedatangan + ' kedatangan'], ['Kurang timbang', dbKg(R.kgKurang)], ['Mutu AWAS', String(R.awas)]], tujuan: R.tujuan, ke: 'Stok › Barang masuk' }));
    return '<div class="kartu db-kartu db-mutu">' + kepala('Mutu usaha', Q.periode, 'sumber:mutu', Q.sumber, Q.tujuan) + out.join('') + '</div>';
  }

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
    const rg = ev.target.closest('[data-db-rentang]'); if (rg) { gantiRentang(rg.dataset.dbRentang); return; }
    const ke = ev.target.closest('[data-db-ke]'); if (ke) { const isi = reg[ke.dataset.dbKe]; tutupTip(); if (isi && isi.tujuan) opsi.keTujuan(isi.tujuan); return; }
    const el = ev.target.closest('[data-db]'); if (el) { const id = el.dataset.db; if (pilih === id) { const isi = reg[id]; tutupTip(); if (isi && isi.tujuan) opsi.keTujuan(isi.tujuan); } else tampilTip(id, el); return; }
    if (!ev.target.closest('.db-tip')) tutupTip();
  });
  akar.addEventListener('pointerover', (ev) => { if (ev.pointerType !== 'mouse') return; const el = ev.target.closest('[data-db]'); if (el && el.dataset.db !== pilih) tampilTip(el.dataset.db, el); });

  // ---------- pasang ----------
  function gantiRentang(r) { if (r === rentang || !DB_RENTANG.some((x) => x[0] === r)) return; rentang = r; try { localStorage.setItem(KUNCI_RENTANG, r); } catch (e) { /* abaikan */ } opsi.mintaRentang(r); }
  /** Gambar seluruh dasbor dari hasil susunDasbor. masuk = animasi masuk ringan (buka dasbor / ganti rentang), bukan tiap data berubah. */
  function gambar(hasil, masuk) {
    D = hasil; const tadi = pilih; reg = {};
    // owner 3 Okt: dua lajur DISUSUN DI SINI, bukan CSS columns — Safari/WebKit tidak menggambar kartu beranimasi di dalam columns (kartu Bulan ini kosong
    // sampai ada yang diketuk, sisa kartu nyangkut di atas Hari ini). Lajur kiri Bulan ini · pemicu · stok, kanan wadah · piutang (= pembagian columns dulu).
    akar.innerHTML = kartuHari(D.hari) + kartuTren(D.tren) + '<div class="db-lajur">' + kartuBulan(D.bulan) + kartuPemicu(D.bulan) + kartuStok(D.stok) + '</div>'
      + '<div class="db-lajur">' + kartuWadah(D.stok) + kartuTagihan(D.tagihan) + kartuMutu(D.mutu) + '</div>' + '<div class="db-tip kartu" hidden></div>';
    pilih = null; if (tadi && reg[tadi]) { const el = akar.querySelector('[data-db="' + (window.CSS && CSS.escape ? CSS.escape(tadi) : tadi) + '"]'); if (el) tampilTip(tadi, el); }
    if (masuk) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1400); }
  }
  return { gambar, rentang: () => rentang, tutupTip };
}
