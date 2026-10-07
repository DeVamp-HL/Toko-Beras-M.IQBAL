// PEMERIKSAAN SESUDAH TUTUP BUKU (Paket C siap 2027, 8 Okt 2026) — tanpa DOM; pembantu berawalan `pst` (bundel uji jsc satu lingkup).
// Dulu rencana tutup buku 2026 memuat butir "cadangan SESUDAH diperiksa (hanya baca): semua baris perbandingan + modal, buku 25 kg di rak Jual, pajak 2026
// dari potret, tidak ada minus" yang dikerjakan di luar aplikasi. Sesudah 13 Okt 2026 tidak ada lagi yang mengerjakannya, jadi aplikasi memeriksanya sendiri
// dan owner cukup membaca kartunya (Uang › Tutup buku). HANYA MEMBACA cache yang sudah dimuat — tidak ada baca server tambahan dan tidak ada yang ditulis.
// Data yang dibutuhkan tidak ada di perangkat → baris "belum bisa diperiksa" + sebabnya, BUKAN lulus. Tiga keadaan per baris: sama (✓), beda (✗, dua
// angkanya), belum bisa diperiksa (?). Angka dihitung fungsi yang SAMA dengan yang dipakai ritual & layar — tidak ada rumus baru:
//   1. baris perbandingan  = tutup-buku-logika bkPeriksaDipakai (hasil periksa ulang yang dibekukan saat arsip habis; belum ada → periksaUlangBuku)
//   2. modal owner         = modalTertanam(31 Des) sesudah ritual (= saldo pembuka modal) vs modal di neraca 31 Des potret (potret-logika, Paket B)
//   3. saldo pembuka & rak = dokumen pembuka di buku vs berita acara (rencana kiriman + sesudahDariPembuka = rumus langkah 4); ringkasan saldo pembuka yang
//                            dibekukan di berita acara (ringkasPembuka) vs buku mesin & susunRak (jual-logika) saat buku tahun baru DIBUKA: catatan gerak
//                            (koleksi yang diarsip tutup buku, tbDaftarKoleksi) disaring sementara tinggal saldo pembuka (toko.js denganCacheSaring)
//   4. pajak               = potret tahun (12 bulan) vs pjTahun (layar Laporan › Pajak) tahun itu
//   5. stok minus          = minusBuku (gerbang g6 tutup buku) atas saldo pembuka yang dibaca mesin
//   6. utang & piutang     = baris perbandingan no. 1 yang sama (tidak dihitung dua kali — barisnya pindah ke kelompok ini)
// Kartu tampil sesudah tahun dikunci & arsipnya habis (sampai "selesai"), lalu sepanjang Januari–Februari tahun berikutnya (atau 30 hari sesudah selesai bila
// ritualnya telat). Tahun = berita acara terkunci / selesai TERAKHIR di sistem ini (bukan era). Dijaga alat-uji/uji_periksa_sesudah.py.
import { hitungStokKarungPerMerk, hitungStokKemasan, tbDaftarKoleksi } from '../mesin/beku.js';
import { tbCutoff, kunciKemasan, hargaKarungUtuh } from '../mesin/pembantu.js';
import { ambilTutupBukuAcara, cacheMentah, dokDiCache, pembukaBerlaku, petaUkuran, petaStokWadah, petaBukuWadah, indukTerpisah, ukuranDigabung,
  CACHE_PEMBUKA, denganCacheSaring, versiCache, dokTertunda } from '../data/toko.js';
import { RP, ANGKA, KG, hariIniIso, tanggalPendek } from '../inti/format.js';
import { bkPeriksaDipakai, bkArsipHabis, arsipBuku, minusBuku, kemajuanBuku, sesudahDariPembuka } from './tutup-buku-logika.js';
import { modalTertanam } from './uang-logika.js';
import { pjTahun, pjDaftarTahun } from './pajak-logika.js';
import { keadaanAwal, susunRak } from './jual-logika.js';
import { arPeta, arBeras } from './arsip-logika.js';

export const PST_VERSI = 1;
const PST_UTANG = ['piutang', 'utangP', 'utangO'];
const PST_KOLEKSI_PEMBUKA = {}; Object.keys(CACHE_PEMBUKA).forEach((c) => { PST_KOLEKSI_PEMBUKA[CACHE_PEMBUKA[c]] = c; });
const pstGeser = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const pstAkhirFeb = (y) => new Date(Date.UTC(Number(y), 2, 0)).toISOString().slice(0, 10);
const pstNama = (s) => String(s || '').split(' · ')[0];
const pstAngka = (n, satuan) => (n === null || n === undefined || !isFinite(n) ? '—' : satuan === 'kg' ? KG(n) : satuan === 'unit' ? ANGKA(n) + ' kantong' : satuan === 'dok' ? ANGKA(n) + ' dokumen' : satuan === 'bulan' ? ANGKA(n) + ' bulan' : RP(n));
const pstBaris = (o) => Object.assign({ status: 'sama', a: null, b: null, satuan: 'rp', ket: '', sebab: '', rincian: [], jalan: '' }, o);
/** Potret tahun itu LANGSUNG dari berita acaranya (bukan potretTahun di toko.js, yang ikut era: kalau penanda tutup buku hilang, era mundur dan potret tidak
 *  dibaca layar — justru itu yang harus berbunyi di baris Pajak, bukan "tanpa potret"). Bentuk = aturan pembaca toko.js (bulan ada, tahun sama). */
const pstPotret = (a, tahun) => (a && a.potret && a.potret.bulan && Number(a.potret.tahun) === tahun ? a.potret : null);
/** Pembuka yang dipakai mesin: dokumen saldo pembuka `tahun` (bertanda tutupBuku) — juga yang tersembunyi (cacheMentah), untuk pembanding. */
const pstPembukaMentah = (cache, tahun) => cacheMentah(cache).filter((d) => d && d.tutupBuku && Number(d.tahunDari) === tahun);

/**
 * Tahun yang diperiksa kartu ini, atau null (kartu tidak tampil). Tahun = tahun TERAKHIR yang berita acaranya di sistem ini terkunci / selesai — dibaca dari berita
 * acara, BUKAN dari era (saldo pembuka yang terlihat mesin): kalau penanda tutup buku hilang, era mundur, padahal justru itu yang harus berbunyi di kartu.
 * 'terkunci' tampil hanya bila arsipnya habis (fase selesaikan — sama dengan kemajuanBuku: hasil periksa dibekukan, atau tidak ada lagi catatan tahun itu yang
 * belum pindah); 'selesai' sampai akhir Februari tahun berikutnya, atau 30 hari sesudah tanggal selesai bila ritualnya telat.
 */
export function pstTahun(kini) {
  const a = ambilTutupBukuAcara().filter((x) => x && isFinite(Number(x.tahun)) && (x.status === 'terkunci' || x.status === 'selesai')).sort((p, q) => Number(q.tahun) - Number(p.tahun))[0] || null;
  if (!a) return null; const tahun = Number(a.tahun);
  if (a.status === 'terkunci') return bkArsipHabis(tahun) || !arsipBuku(tahun).n ? { tahun, acara: a, fase: 'selesaikan' } : null;
  const iso = hariIniIso(kini); const s30 = a.selesaiTanggal ? pstGeser(a.selesaiTanggal, 30) : '';
  return iso <= pstAkhirFeb(tahun + 1) || (s30 && iso <= s30) ? { tahun, acara: a, fase: 'selesai' } : null;
}

/** Data di perangkat ini cukup? M = { siap, siapN, total, ditolak: [nama koleksi], sebagian: [nama] } dari layar. perlu = nama koleksi Firestore ('*' = semua). '' = cukup. */
function pstKurang(M, perlu, tunggu) {
  if (tunggu) return 'catatan tutup buku di perangkat ini masih menunggu server — tunggu sampai antrean kosong (Menu › Sistem › Perangkat)';
  const m = M || {}; if (m.siap === false) return 'data toko belum selesai dimuat di perangkat ini' + (m.total ? ' (' + ANGKA(m.siapN || 0) + ' dari ' + ANGKA(m.total) + ' koleksi)' : '');
  const kena = (daftar) => (daftar || []).map((x) => String(x).split('/')[0]).filter((x, i, arr) => arr.indexOf(x) === i && (perlu.indexOf('*') >= 0 || perlu.indexOf(x) >= 0));
  const tolak = kena(m.ditolak); if (tolak.length) return 'koleksi ' + tolak.join(', ') + ' ditolak server di perangkat ini — angkanya tidak ada';
  const sebagian = kena(m.sebagian); if (sebagian.length) return 'koleksi ' + sebagian.join(', ') + ' hanya dimuat sebagian di perangkat ini';
  return '';
}
const PST_PERLU_STOK = ['batchMasuk', 'produksiKemasan', 'stokBahanKemasan', 'stokBahanLiteran', 'tutupBukuAcara', 'katalogHargaKarung', 'katalogHargaKemasan', 'aturanToko'];

/** Jalan keluar per keadaan berita acara (tanpa orang luar): belum selesai = batalkan & ulangi; selesai = catatan HARI INI / jalan pulang darurat. */
function pstJalan(fase) {
  return fase === 'selesaikan'
    ? 'Tutup buku ini BELUM diselesaikan — jangan ketuk "selesai". Ketuk "batalkan" di pita tutup buku (dua ketukan, dari perangkat yang memulai), tunggu sampai tuntas, lalu ulangi ritualnya dari langkah 1.'
    : 'Tutup buku ini sudah selesai (tidak ada tombol batal). Beda kecil: betulkan dengan catatan HARI INI (Stok › Cocokkan, bayar bon / catat bon yang terlupa). Beda besar: ikuti jalan pulang darurat di catatan "Prosedur pulih darurat" (bab Jalan mundur tutup buku).';
}

// ---- 1 & 6 · baris perbandingan (sebelum = sesudah ritual), dari bkPeriksaDipakai — SATU sumber untuk kedua kelompok ----
function pstBanding(T, M, tunggu) {
  const tahun = T.tahun, a = T.acara; const PU = bkPeriksaDipakai(tahun); const H = a.hariIni || null;
  const beku = !!(PU && PU.beku); const kurang = pstKurang(M, beku ? ['tutupBukuAcara', 'pengaturan'] : ['*'], tunggu);
  const sumber = beku ? 'hasil periksa ulang yang dibekukan saat arsip habis' + (PU.beku.tanggal ? ' (' + tanggalPendek(PU.beku.tanggal) + ')' : '')
    : PU ? 'dihitung ulang sekarang dari buku (hasil yang dibekukan saat arsip habis tidak ada di perangkat ini)' : '';
  const jalan = pstJalan(T.fase);
  if (!PU) {
    const dasar = Array.isArray(a.sebelum) && a.sebelum.length ? a.sebelum : [{ id: 'semua', nama: 'Baris perbandingan', n: null }];
    return { sumber, baris: dasar.map((b) => pstBaris({ id: b.id, judul: pstNama(b.nama), status: 'belum', a: b.n === undefined ? null : b.n, sebab: kurang || 'berita acara ' + tahun + ' tidak menyimpan patokan hari tutup buku — perbandingan sesudah ritual tidak bisa diulang' })) };
  }
  const baris = PU.baris.map((b) => {
    const judul = pstNama(b.nama); const ket = b.nama.indexOf(' · ') >= 0 ? b.nama.slice(b.nama.indexOf(' · ') + 3) : '';
    if (kurang) return pstBaris({ id: b.id, judul, ket, status: 'belum', a: b.a, b: b.b, sebab: kurang });
    if (b.tanda === '✓') return pstBaris({ id: b.id, judul, ket, status: 'sama', a: b.a, b: b.b });
    if (b.tanda === '≠') return pstBaris({ id: b.id, judul, ket, status: 'beda', a: b.a, b: b.b, jalan });
    const sebab = b.a === null ? 'angka sebelum ritual tidak bisa dihitung (uang per tempat pada ' + tanggalPendek((H && H.tanggal) || '') + ')'
      : 'angka sesudah ritual tidak bisa dihitung mundur — titik kas sudah maju melewati ' + tanggalPendek((H && H.tanggal) || '') + '. Sebelum ritual: ' + RP(b.a) + '; cocokkan dengan hitungan tutup hari tanggal itu (Uang › Tutup hari)';
    return pstBaris({ id: b.id, judul, ket, status: 'belum', a: b.a, b: b.b, sebab });
  });
  return { sumber, baris };
}

// ---- 2 · modal owner: saldo pembuka (dibaca mesin) = modal di neraca 31 Des yang dibekukan ----
function pstModal(T, M, tunggu) {
  const tahun = T.tahun, a = T.acara; const c = tbCutoff(tahun); const kurang = pstKurang(M, ['tutupBukuAcara', 'modalOwner'], tunggu);
  const Pt = pstPotret(a, tahun); const N = Pt && Pt.bulan && Pt.bulan[tahun + '-12'] ? Pt.bulan[tahun + '-12'].neraca : null;
  const beku = N && N.modal !== null && N.modal !== undefined && isFinite(Number(N.modal)) ? { n: Math.round(Number(N.modal)), dari: 'neraca 31 Des di potret' }
    : a.modal !== null && a.modal !== undefined && isFinite(Number(a.modal)) ? { n: Math.round(Number(a.modal)), dari: 'berita acara (tanpa potret)' } : null;
  const dok = pstPembukaMentah('modal', tahun); const terlihat = dok.filter(pembukaBerlaku);
  const sesudah = Math.round(modalTertanam(c)); const judul = 'Modal owner: saldo pembuka = neraca 31 Des ' + tahun;
  if (kurang) return pstBaris({ id: 'modalPembuka', judul, status: 'belum', a: beku ? beku.n : null, b: sesudah, sebab: kurang });
  if (!beku) return pstBaris({ id: 'modalPembuka', judul, status: 'belum', b: sesudah, sebab: 'berita acara ' + tahun + ' tidak menyimpan modal 31 Des (tanpa potret, tanpa angka modal) — tidak ada pembanding' });
  const ket = 'pembanding: ' + beku.dari + ' · saldo pembuka modal ' + (terlihat.length ? terlihat.length + ' dokumen' : 'TIDAK ADA di buku') + (dok.length > terlihat.length ? ' (' + (dok.length - terlihat.length) + ' tersembunyi dari mesin)' : '');
  const hilang = Math.abs(beku.n) >= 0.5 && !terlihat.length;
  const sama = !hilang && Math.abs(sesudah - beku.n) < 0.5;
  return pstBaris({ id: 'modalPembuka', judul, status: sama ? 'sama' : 'beda', a: beku.n, b: sesudah, ket,
    jalan: sama ? '' : 'Modal owner di buku ' + (tahun + 1) + ' tidak sama dengan modal di neraca 31 Des. ' + pstJalan(T.fase) });
}

// ---- 3 & 5 · saat buku tahun baru DIBUKA: catatan gerak disaring sementara tinggal saldo pembuka tahun itu ----
/** fn dijalankan di atas cache yang koleksi geraknya (yang diarsip tutup buku — tbDaftarKoleksi) hanya berisi saldo pembuka `tahun`. Cache dikembalikan sesudahnya. */
export function pstSaatBuka(tahun, fn) {
  const t = Number(tahun); const nama = tbDaftarKoleksi(t).map((k) => k.koleksi);
  return denganCacheSaring(nama, (d) => !!(d && d.tutupBuku && Number(d.tahunDari) === t), fn);
}
/** Rak Jual (susunRak identitas — chip, nama, ukuran; sisa tidak dihitung). Isian berat karung Jual (#jualKarungBerat) dikembalikan sesudahnya. */
function pstRakJual() {
  const el = typeof document !== 'undefined' && document.getElementById ? document.getElementById('jualKarungBerat') : null; const v0 = el ? el.value : null;
  try { return susunRak(keadaanAwal(), { identitas: true }); } finally { if (el) el.value = v0; }
}
const PST_JENIS_STOK = { beras: true, kemasan: true, kantong: true };
// baris saldo pembuka per buku: ringkasan yang DIBEKUKAN di berita acara saat kunci (ringkasPembuka), atau — berita acara tanpa ringkasan — dokumen pembukanya
const PST_TANDA = ['indukUkuran', 'stokWadah', 'karungWadah', 'bukuAdukan', 'karungBelakang', 'merkAsal', 'digabungKe', 'merkPemasok'];
function pstBarisPembuka(a, tahun) {
  const R = a.pembukaRingkas && Array.isArray(a.pembukaRingkas.beras) && Array.isArray(a.pembukaRingkas.kemasan) ? a.pembukaRingkas : null;
  if (R) return { dari: 'ringkasan saldo pembuka di berita acara', beras: R.beras.map((r) => Object.assign({}, r)), kemasan: R.kemasan.map((k) => Object.assign({}, k)) };
  const beras = []; pstPembukaMentah('batch', tahun).forEach((b) => (b.merkList || []).forEach((m) => { if (!m || !m.merk) return; const r = { merk: String(m.merk), satuan: String(m.satuan || ''), berat: Number(m.beratKarung) || 0, kg: Number(m.totalKg) || 0 };
    PST_TANDA.forEach((t) => { if (m[t] !== undefined && m[t] !== null && m[t] !== '') r[t] = m[t]; }); beras.push(r); }));
  const kemasan = pstPembukaMentah('produksi', tahun).map((p) => ({ nama: String(p.namaProduk || ''), ukuran: p.ukuranKemasan, unit: Number(p.jumlahUnit) || 0 }));
  return { dari: 'dokumen saldo pembuka (berita acara tanpa ringkasan per buku)', beras, kemasan };
}
// baris berita acara yang dijumlah lagi dari dokumen pembuka (rumus langkah 4: sesudahDariPembuka). Uang per tempat (titik kas) & upah bukan dokumen pembuka.
const PST_BANDING_DOK = ['beras', 'kemasan', 'bahan', 'piutang', 'kasbonK', 'kasbonO', 'utangP', 'utangO', 'modal'];
function pstStok(T, M, tunggu, kini) {
  const tahun = T.tahun, a = T.acara; const tglBuka = (tahun + 1) + '-01-01'; const kurang = pstKurang(M, PST_PERLU_STOK, tunggu); const jalan = pstJalan(T.fase);
  // c0 · saldo pembuka di buku = berita acara 31 Des: (a) dokumen yang direncanakan berita acara ada & terlihat mesin, (b) dijumlah per baris dengan rumus
  //      langkah 4 ritual (sesudahDariPembuka) = sisi "sebelum" berita acara — dokumen pembuka yang kelak hilang / berubah tetap ketahuan
  const rencana = (a.rencana && Array.isArray(a.rencana.kiriman) ? a.rencana.kiriman : []).reduce((o, k) => o.concat(k.dok || []), []).filter((d) => d && PST_KOLEKSI_PEMBUKA[d.koleksi]);
  let n = rencana.length, ada = 0, sembunyi = 0; const hilang = {};
  if (n) rencana.forEach((d) => { const x = dokDiCache(d.koleksi, d.id); if (!x) hilang[d.koleksi] = (hilang[d.koleksi] || 0) + 1; else if (!pembukaBerlaku(x)) sembunyi += 1; else ada += 1; });
  else { n = Number(a.nPembuka) || 0; Object.keys(CACHE_PEMBUKA).forEach((c) => pstPembukaMentah(c, tahun).forEach((x) => { if (pembukaBerlaku(x)) ada += 1; else sembunyi += 1; })); }
  const dokKini = []; Object.keys(CACHE_PEMBUKA).forEach((c) => pstPembukaMentah(c, tahun).forEach((x) => dokKini.push({ koleksi: CACHE_PEMBUKA[c], data: x })));
  const J0 = sesudahDariPembuka({ dokumen: dokKini, upah: null }, { kasAda: false, K: {} }); const bedaJ = [];
  (Array.isArray(a.sebelum) ? a.sebelum : []).forEach((b) => { if (PST_BANDING_DOK.indexOf(b.id) < 0 || b.n === null || b.n === undefined) return; const x = J0[b.id];
    if (x === undefined || x === null || Math.abs(Number(b.n) - Number(x)) >= 0.5) bedaJ.push(pstNama(b.nama) + ': berita acara ' + RP(b.n) + ' → saldo pembuka di buku ' + (x === undefined || x === null ? '—' : RP(x))); });
  const j0 = 'Saldo pembuka ' + (tahun + 1) + ' di buku = berita acara 31 Des';
  const okC0 = n > 0 && ada === n && !bedaJ.length;
  const c0 = kurang ? pstBaris({ id: 'pembuka', judul: j0, status: 'belum', satuan: 'dok', a: n || null, b: ada, sebab: kurang })
    : !n ? pstBaris({ id: 'pembuka', judul: j0, status: 'belum', satuan: 'dok', b: ada, sebab: 'berita acara ' + tahun + ' tidak menyebut berapa saldo pembukanya — tidak ada pembanding' })
      : pstBaris({ id: 'pembuka', judul: j0, status: okC0 ? 'sama' : 'beda', satuan: 'dok', a: n, b: ada,
        ket: (a.rencana ? 'jumlah dokumen menurut rencana kiriman di berita acara' : 'jumlah dokumen menurut berita acara') + '; rupiah stok, piutang, kasbon, utang & modal dijumlah lagi dari dokumennya',
        rincian: Object.keys(hilang).map((k) => hilang[k] + ' dokumen hilang dari ' + k).concat(sembunyi ? [sembunyi + ' dokumen ada tapi tersembunyi dari mesin (penanda tutup buku tidak terbaca)'] : [], bedaJ),
        jalan: okC0 ? '' : 'Saldo pembuka di buku tidak sama dengan berita acara — stok, piutang, atau utang ' + (tahun + 1) + ' salah. Jangan berjualan/menagih dulu. ' + jalan });
  // pembanding per buku (beku di berita acara) & buku mesin saat tahun baru DIBUKA (catatan gerak disaring tinggal saldo pembuka)
  const BP = pstBarisPembuka(a, tahun); const exp = {}; BP.beras.forEach((r) => { exp[r.merk] = (exp[r.merk] || 0) + (Number(r.kg) || 0); });
  const expK = {}, namaK = {}; BP.kemasan.forEach((p) => { const k = kunciKemasan(p.nama, p.ukuran); expK[k] = (expK[k] || 0) + (Number(p.unit) || 0); namaK[k] = p.nama + ' ' + String(p.ukuran).replace('.', ',') + ' kg'; });
  const V = pstSaatBuka(tahun, () => {
    const stok = hitungStokKarungPerMerk(); const kem = hitungStokKemasan(); const rak = pstRakJual(); const ctx = { uk: petaUkuran(), sw: petaStokWadah(), bw: petaBukuWadah(), tp: indukTerpisah(), ug: ukuranDigabung(), arsip: arPeta() };
    const minus = minusBuku(tglBuka).daftar.filter((x) => PST_JENIS_STOK[x.jenis]);
    const harga = BP.beras.map((r) => { const uk = ctx.uk[r.merk]; return hargaKarungUtuh(uk ? uk.induk : r.merk, Number(r.berat) || 0); });
    return { stok, kem, rak, ctx, minus, harga };
  });
  // c1 · buku beras per merek (juga buku wadah, karung wadah, adukan, karung belakang): kg di buku saat dibuka = kg saldo pembuka
  const bedaM = []; let kgA = 0, kgB = 0; Object.keys(exp).concat(Object.keys(V.stok).filter((m) => !(m in exp) && Math.abs(V.stok[m].sisaKg) >= 0.01)).filter((m, i, arr) => arr.indexOf(m) === i).sort().forEach((m) => {
    const e = exp[m] || 0; const s = V.stok[m] ? V.stok[m].sisaKg : null; kgA += e; kgB += s || 0;
    if (s === null) bedaM.push(m + ': saldo pembuka ' + KG(e) + ' → TIDAK ADA di buku'); else if (!(m in exp)) bedaM.push(m + ': tidak ada di saldo pembuka → buku ' + KG(s)); else if (Math.abs(s - e) >= 0.01) bedaM.push(m + ': saldo pembuka ' + KG(e) + ' → buku ' + KG(s)); });
  const nM = Object.keys(exp).length; const j1 = 'Buku beras per merek saat ' + (tahun + 1) + ' dibuka = saldo pembuka';
  const c1 = kurang ? pstBaris({ id: 'bukuMerek', judul: j1, status: 'belum', satuan: 'kg', sebab: kurang })
    : pstBaris({ id: 'bukuMerek', judul: j1, status: bedaM.length ? 'beda' : 'sama', satuan: 'kg', a: kgA, b: kgB, rincian: bedaM.slice(0, 12).concat(bedaM.length > 12 ? ['… dan ' + (bedaM.length - 12) + ' lagi'] : []),
      ket: (nM ? nM + ' buku (merek, wadah, karung wadah, adukan, karung belakang)' : 'saldo pembuka tanpa buku beras') + ' · pembanding: ' + BP.dari,
      jalan: bedaM.length ? 'Stok beras yang dibaca mesin sesudah ritual tidak sama dengan saldo pembukanya — jangan jual merek yang disebut dulu. ' + jalan : '' });
  // c2 · kemasan jadi per produk & ukuran
  const bedaK = []; let uA = 0, uB = 0; Object.keys(expK).concat(Object.keys(V.kem).filter((k) => !(k in expK) && Math.abs(V.kem[k].sisaUnit) > 0.001)).filter((k, i, arr) => arr.indexOf(k) === i).sort().forEach((k) => {
    const e = expK[k] || 0; const s = V.kem[k] ? V.kem[k].sisaUnit : null; uA += e; uB += s || 0; const nm = namaK[k] || (V.kem[k] ? V.kem[k].namaProduk + ' ' + String(V.kem[k].ukuranKemasan).replace('.', ',') + ' kg' : k);
    if (s === null) bedaK.push(nm + ': saldo pembuka ' + ANGKA(e) + ' → TIDAK ADA di buku'); else if (Math.abs(s - e) > 0.001) bedaK.push(nm + ': saldo pembuka ' + ANGKA(e) + ' → buku ' + ANGKA(s)); });
  const j2 = 'Kemasan jadi per produk saat ' + (tahun + 1) + ' dibuka = saldo pembuka';
  const c2 = kurang ? pstBaris({ id: 'bukuKemasan', judul: j2, status: 'belum', satuan: 'unit', sebab: kurang })
    : pstBaris({ id: 'bukuKemasan', judul: j2, status: bedaK.length ? 'beda' : 'sama', satuan: 'unit', a: uA, b: uB, rincian: bedaK.slice(0, 12).concat(bedaK.length > 12 ? ['… dan ' + (bedaK.length - 12) + ' lagi'] : []),
      ket: Object.keys(expK).length ? Object.keys(expK).length + ' produk' : 'tidak ada kemasan jadi di saldo pembuka',
      jalan: bedaK.length ? 'Kemasan jadi yang dibaca mesin sesudah ritual tidak sama dengan saldo pembukanya. ' + jalan : '' });
  // c3 · tanda buku dibaca lagi & rak Jual: buku 25 kg tampil atas nama induknya, buku khusus bukan chip karung, merek berharga tidak hilang dari rak
  const C = V.ctx; const salah = []; const catatan = []; let nTanda = 0, nChip = 0, nTanpaHarga = 0, nArsip = 0;
  const chip = (m, b) => V.rak.karung.find((x) => x.kunci === m && Number(x.berat) === b) || null;
  BP.beras.forEach((r, i) => {
    const m = r.merk; const b = Number(r.berat) || 0;
    if (r.indukUkuran) { nTanda += 1; const u = C.uk[m]; if (!u || u.induk !== String(r.indukUkuran) || (b && u.berat !== b)) salah.push(m + ': tanda buku ' + (b || 25) + ' kg (induk ' + r.indukUkuran + ') tidak terbaca'); }
    if (r.stokWadah) { nTanda += 1; if (C.sw[m] !== String(r.stokWadah)) salah.push(m + ': tanda buku wadah ' + r.stokWadah + ' tidak terbaca'); }
    if (r.karungWadah) { nTanda += 1; if (!C.bw[m] || C.bw[m].jenis !== 'karung') salah.push(m + ': tanda karung wadah tidak terbaca'); }
    if (r.bukuAdukan) { nTanda += 1; if (!C.bw[m] || C.bw[m].jenis !== 'adukan') salah.push(m + ': tanda buku adukan tidak terbaca'); }
    if (r.karungBelakang) { nTanda += 1; if (!C.bw[m] || C.bw[m].jenis !== 'belakang' || C.bw[m].merk !== String(r.merkAsal || '')) salah.push(m + ': tanda karung belakang (merek asal ' + (r.merkAsal || '?') + ') tidak terbaca'); }
    if (r.digabungKe) { nTanda += 1; if (C.ug[m] !== String(r.digabungKe)) salah.push(m + ': tanda "digabung ke ' + r.digabungKe + '" tidak terbaca'); }
    if (r.satuan !== 'karung' || !b) return;
    const ch = chip(m, b);
    if (C.bw[m]) { if (ch) salah.push(m + ': buku khusus tampil di rak Jual sebagai karung ' + b + ' kg'); return; }
    const u = C.uk[m]; const nama = u ? u.induk : m;
    if (arBeras(m, C.arsip)) { nArsip += 1; return; }
    if (u ? b !== u.berat : !!(C.tp[m] && C.tp[m][b])) return;
    if (!V.harga[i]) { nTanpaHarga += 1; return; }
    if (!ch) salah.push(nama + ' ' + b + ' kg (buku ' + m + '): tidak tampil di rak Jual'); else { nChip += 1; if (ch.nama !== nama) salah.push(m + ': tampil di rak Jual sebagai "' + ch.nama + '", bukan "' + nama + '"'); }
  });
  if (nTanpaHarga) catatan.push(nTanpaHarga + ' baris tanpa harga di katalog — memang tidak tampil di rak (bukan karena tutup buku)');
  if (nArsip) catatan.push(nArsip + ' baris diarsipkan owner — memang tidak tampil di rak');
  const j3 = 'Rak Jual & buku 25 kg membaca saldo pembuka';
  const c3 = kurang ? pstBaris({ id: 'rakJual', judul: j3, status: 'belum', satuan: 'teks', sebab: kurang })
    : pstBaris({ id: 'rakJual', judul: j3, status: salah.length ? 'beda' : 'sama', satuan: 'teks', a: BP.beras.length ? nChip + ' karung di rak · ' + nTanda + ' tanda buku' : null,
      ket: [BP.beras.length ? nChip + ' chip karung di rak Jual, ' + nTanda + ' tanda buku (25 kg, wadah, adukan, karung belakang, digabung) terbaca' : 'saldo pembuka tanpa buku beras'].concat(catatan).join(' · '),
      rincian: salah.slice(0, 12).concat(salah.length > 12 ? ['… dan ' + (salah.length - 12) + ' lagi'] : []),
      jalan: salah.length ? 'Ada buku yang hilang dari rak Jual atau tandanya tidak terbaca sesudah ritual — merek itu bisa terjual dari buku yang salah. ' + jalan : '' });
  // 5 · stok minus pada saldo pembuka (merek, wadah, kemasan, kantong) — minusBuku = gerbang g6; yang minus HARI INI karena catatan sesudahnya hanya disebut
  const minusKini = minusBuku(hariIniIso(kini)).daftar.filter((x) => PST_JENIS_STOK[x.jenis]);
  const j5 = 'Tidak ada stok minus di saldo pembuka ' + (tahun + 1);
  const kataKini = minusKini.length ? 'CATATAN: hari ini ' + minusKini.length + ' buku minus karena catatan sesudah tutup buku (' + minusKini.slice(0, 3).map((x) => x.teks).join(' · ') + (minusKini.length > 3 ? ' · …' : '') + ') — hitung isinya di Stok › Cocokkan' : '';
  const e1 = kurang ? pstBaris({ id: 'minus', judul: j5, status: 'belum', satuan: 'teks', sebab: kurang })
    : pstBaris({ id: 'minus', judul: j5, status: V.minus.length ? 'beda' : 'sama', satuan: 'teks', a: V.minus.length ? V.minus.length + ' buku minus' : null,
      ket: [V.minus.length ? '' : 'merek, wadah, kemasan, kantong — tidak ada yang minus', kataKini].filter(Boolean).join(' · '),
      rincian: V.minus.slice(0, 12).map((x) => x.teks + ' — ' + x.jalan),
      jalan: V.minus.length ? 'Saldo pembuka membawa stok minus — angka stok ' + (tahun + 1) + ' salah sejak awal. ' + jalan : '' });
  return { c0, c1, c2, c3, e1 };
}

// ---- 4 · pajak tahun itu dibaca dari potret ----
function pstPajak(T, M, tunggu, kini) {
  const tahun = T.tahun, a = T.acara; const kurang = pstKurang(M, ['tutupBukuAcara', 'pajakSetoran', 'pajakOmzetLuar', 'aturanToko'], tunggu);
  const Pt = pstPotret(a, tahun); const PJ = Pt && Pt.pajak ? Pt.pajak : null; const bulan = Pt && Pt.bulan ? Pt.bulan : {};
  const kunciBulan = []; for (let m = 1; m <= 12; m++) kunciBulan.push(tahun + '-' + String(m).padStart(2, '0'));
  const jalan = 'Laporan › Pajak ' + tahun + ' tidak membaca potret tutup buku. Untuk setoran Desember & SPT Tahunan pakai PDF Rekap pajak & Laporan Tahunan ' + tahun + ' yang disimpan sebelum ritual (atau berkas cadangan SEBELUM). ' + pstJalan(T.fase);
  const b = (o) => pstBaris(Object.assign(kurang ? { status: 'belum', sebab: kurang } : {}, o, kurang ? { status: 'belum', sebab: kurang } : {}));
  if (!Pt) {
    const sebab = 'berita acara ' + tahun + ' tidak menyimpan potret — tidak ada angka pembanding';
    return [b({ id: 'pajakPotret', judul: 'Potret ' + tahun + ': 12 bulan lengkap', status: 'beda', satuan: 'bulan', a: 12, b: 0, ket: 'tanpa potret, Laporan & Pajak ' + tahun + ' hanya ada di berkas arsip & cadangan SEBELUM', jalan }),
      b({ id: 'pajakOmzet', judul: 'Omzet ' + tahun + ' di Laporan › Pajak = potret', status: 'belum', sebab }), b({ id: 'pajakSetor', judul: 'Setoran PPh ' + tahun + ' = potret', status: 'belum', sebab }),
      b({ id: 'pajakLayar', judul: 'Laporan › Pajak ' + tahun + ' bertanda tutup buku', status: 'belum', sebab })];
  }
  const kosongB = kunciBulan.filter((k) => !bulan[k] || bulan[k].omzet === null || bulan[k].omzet === undefined || !isFinite(Number(bulan[k].omzet)));
  const d1 = b({ id: 'pajakPotret', judul: 'Potret ' + tahun + ': 12 bulan lengkap', status: kosongB.length ? 'beda' : 'sama', satuan: 'bulan', a: 12, b: 12 - kosongB.length, rincian: kosongB.map((k) => k + ' tidak ada di potret'), jalan: kosongB.length ? jalan : '' });
  const TJ = pjTahun(tahun, kini); const ptOmzet = PJ && isFinite(Number(PJ.totalSistem)) ? Math.round(Number(PJ.totalSistem)) : kunciBulan.reduce((s, k) => s + (Number(bulan[k] && bulan[k].omzet) || 0), 0);
  const d2 = b({ id: 'pajakOmzet', judul: 'Omzet ' + tahun + ' di Laporan › Pajak = potret', status: Math.abs(Math.round(TJ.totalSistem) - ptOmzet) < 0.5 ? 'sama' : 'beda', a: ptOmzet, b: Math.round(TJ.totalSistem),
    ket: 'omzet mesin setahun (dasar perkiraan PPh)', jalan: Math.abs(Math.round(TJ.totalSistem) - ptOmzet) < 0.5 ? '' : jalan });
  // setoran: yang tercatat SAAT tahun dikunci (potret) harus tetap ada; yang dicatat sejak hari kunci (mis. masa Desember di Januari) boleh menambah
  const sejak = String(a.tanggal || ''); let ptSetor = 0, kini0 = 0, tambah = 0; const bedaS = [];
  TJ.daftar.forEach((x) => { const p = PJ && Array.isArray(PJ.daftar) ? PJ.daftar.find((y) => y.key === x.key) : null; const ps = p ? Number(p.jumlahSetor) || 0 : 0;
    const baru = x.setor.filter((s) => sejak && String(s.dicatatPada || '') >= sejak).reduce((s, y) => s + (Number(y.jumlah) || 0), 0);
    ptSetor += ps; kini0 += x.jumlahSetor; tambah += baru; if (!(x.jumlahSetor - baru - 0.5 <= ps && ps <= x.jumlahSetor + 0.5)) bedaS.push(x.key + ': potret ' + RP(ps) + ' → sekarang ' + RP(x.jumlahSetor) + (baru ? ' (termasuk ' + RP(baru) + ' dicatat pada/sesudah hari tutup buku)' : '')); });
  const d3 = b({ id: 'pajakSetor', judul: 'Setoran PPh ' + tahun + ' = potret', status: !PJ ? 'belum' : bedaS.length ? 'beda' : 'sama', sebab: PJ ? '' : 'potret ' + tahun + ' tanpa rekap pajak', a: PJ ? Math.round(ptSetor) : null, b: Math.round(kini0),
    ket: tambah ? 'sekarang termasuk ' + RP(tambah) + ' yang dicatat pada/sesudah hari tutup buku (' + tanggalPendek(sejak) + ')' : '', rincian: bedaS,
    jalan: bedaS.length ? 'Ada setoran ' + tahun + ' yang tercatat saat tahun dikunci tetapi sekarang berubah atau hilang — cocokkan dengan bukti setor (NTPN) di Laporan › Pajak.' : '' });
  const tanpa = TJ.daftar.filter((x) => !x.ditutup || (x.diarsip && !x.dariPotret)).map((x) => x.key); const pilih = pjDaftarTahun(kini).some((x) => x.tahun === tahun);
  const okL = TJ.daftar.length === 12 && !tanpa.length && pilih && TJ.ditutup;
  const d4 = b({ id: 'pajakLayar', judul: 'Laporan › Pajak ' + tahun + ' bertanda tutup buku', status: okL ? 'sama' : 'beda', satuan: 'bulan', a: 12, b: TJ.daftar.length - tanpa.length,
    ket: pilih ? '12 masa bertanda "tutup buku", angka sistem dari potret' : 'tahun ' + tahun + ' tidak ada di pilihan tahun layar Pajak',
    rincian: tanpa.map((k) => k + ' tidak bertanda tutup buku / tidak dari potret').concat(pilih ? [] : ['tahun ' + tahun + ' tidak bisa dipilih di Laporan › Pajak']), jalan: okL ? '' : jalan });
  return [d1, d2, d3, d4];
}

/**
 * PEMERIKSAAN untuk kartu Uang › Tutup buku. kini = jam layar; M = keadaan muat data di perangkat ini (lihat pstKurang). null = kartu tidak tampil.
 * Hasil: { tahun, fase, status, kelompok: [{ id, judul, baris: [...] }], n, nSama, nBeda, nBelum, beres, ringkas, petunjuk: [teks], sumber, diperiksa }.
 * Diingat per versi cache + hari + muat (layar menggambar ulang tiap data berubah).
 */
let _pstMemo = null;
export function pstPeriksa(kini, M) {
  const T = pstTahun(kini); if (!T) return null;
  // kiriman tutup buku yang masih menunggu server (juga berita acara 'selesai' yang belum diakui — kemajuanBuku tidak melihatnya)
  const KM = kemajuanBuku(); const tunggu = !!(KM && KM.fase === 'tunggu') || dokTertunda('tutupBukuAcara', String(T.acara.id || T.tahun));
  const kunci = () => [T.tahun, T.acara.status, tunggu ? 1 : 0, versiCache(), hariIniIso(kini), JSON.stringify(M || {})].join('|');
  if (_pstMemo && _pstMemo.k === kunci()) return _pstMemo.h;
  const PB = pstBanding(T, M, tunggu); const utang = PB.baris.filter((x) => PST_UTANG.indexOf(x.id) >= 0); const lain = PB.baris.filter((x) => PST_UTANG.indexOf(x.id) < 0);
  const S = pstStok(T, M, tunggu, kini); const P = pstPajak(T, M, tunggu, kini);
  const kelompok = [
    { id: 'banding', judul: '1 · Baris perbandingan: sebelum = sesudah ritual', ket: PB.sumber, baris: lain },
    { id: 'modal', judul: '2 · Modal owner', baris: [pstModal(T, M, tunggu)] },
    { id: 'rak', judul: '3 · Saldo pembuka, buku 25 kg & rak Jual', baris: [S.c0, S.c1, S.c2, S.c3] },
    { id: 'pajak', judul: '4 · Pajak ' + T.tahun + ' dari potret', baris: P },
    { id: 'minus', judul: '5 · Stok minus', baris: [S.e1] },
    { id: 'utang', judul: '6 · Utang & piutang: sebelum = sesudah ritual', ket: 'baris yang sama dengan kelompok 1 (tidak dihitung dua kali)', baris: utang },
  ];
  const semua = kelompok.reduce((o, g) => o.concat(g.baris), []); const n = semua.length;
  const nBeda = semua.filter((x) => x.status === 'beda').length, nBelum = semua.filter((x) => x.status === 'belum').length, nSama = n - nBeda - nBelum;
  const beres = !nBeda && !nBelum && n > 0;
  const ringkas = nBeda ? nBeda + ' pemeriksaan beda — jangan jualan/menagih dulu, lihat barisnya' + (nBelum ? ' · ' + nBelum + ' belum bisa diperiksa' : '')
    : nBelum ? nBelum + ' dari ' + n + ' pemeriksaan belum bisa diperiksa — tutup buku ' + T.tahun + ' belum bisa dinyatakan beres; sebabnya di barisnya'
      : 'Semua ' + n + ' pemeriksaan sama — tutup buku ' + T.tahun + ' beres';
  const petunjuk = []; semua.forEach((x) => { if (x.status === 'beda' && x.jalan && petunjuk.indexOf(x.jalan) < 0) petunjuk.push(x.jalan); });
  if (nBelum && !nBeda) petunjuk.push('Baris "belum bisa diperiksa" bukan lulus: buka kartu ini lagi sesudah sebabnya hilang (data selesai dimuat, antrean kosong). Kalau sebabnya tetap: angka "sebelum" di baris itu dicocokkan sendiri dengan hitungan tutup hari tanggal itu (Uang › Tutup hari), dan cadangan SEBELUM & SESUDAH disimpan berdua.');
  if (beres) petunjuk.push(T.fase === 'selesaikan' ? 'Langkah berikutnya: ketuk "unduh cadangan sesudah · selesai", lalu "unduh hasil pemeriksaan" — simpan kedua berkas bersama (≥ 2 tempat di luar HP).'
    : 'Unduh hasil pemeriksaan dan simpan bersama cadangan SESUDAH (≥ 2 tempat di luar HP). Kunci bulan Januari ' + (T.tahun + 1) + ' boleh mulai 4 Feb.');
  const h = { versi: PST_VERSI, tahun: T.tahun, fase: T.fase, status: T.acara.status, kelompok, n, nSama, nBeda, nBelum, beres, ringkas, petunjuk, sumber: PB.sumber,
    diperiksa: hariIniIso(kini), selesai: T.acara.selesaiTanggal || '', dikunci: T.acara.tanggal || '' };
  // kunci diambil SESUDAH menghitung: saringan sementara (denganCacheSaring) menaikkan versi cache, isi cache-nya kembali sama
  _pstMemo = { k: kunci(), h }; return h;
}
/** Teks satu angka untuk layar & berkas (tiga keadaan: angka, '—' = belum bisa dihitung). */
export function pstTeks(n, satuan) { return satuan === 'teks' ? (n === null || n === undefined ? '' : String(n)) : pstAngka(n, satuan); }
/** Berkas "hasil pemeriksaan" (JSON) — disimpan owner bersama cadangan SESUDAH. */
export function pstBerkas(H, kini) {
  const tanda = { sama: 'sama', beda: 'BEDA', belum: 'belum bisa diperiksa' };
  return { nama: 'pemeriksaan-tutup-buku-' + H.tahun + '-miqbal.json', isi: { jenis: 'pemeriksaan sesudah tutup buku', versi: H.versi, tahun: H.tahun, diunduhPada: kini.toISOString(), diperiksa: H.diperiksa,
    beritaAcara: { status: H.status, dikunci: H.dikunci, selesai: H.selesai }, ringkasan: H.ringkas, n: H.n, sama: H.nSama, beda: H.nBeda, belumBisa: H.nBelum, sumberBaris: H.sumber,
    kelompok: H.kelompok.map((g) => ({ judul: g.judul, ket: g.ket || '', baris: g.baris.map((x) => ({ id: x.id, judul: x.judul, hasil: tanda[x.status], sebelum: x.a, sesudah: x.b, satuan: x.satuan, ket: x.ket, sebab: x.sebab, rincian: x.rincian })) })),
    petunjuk: H.petunjuk } };
}
