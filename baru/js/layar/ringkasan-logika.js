// LAYAR RINGKASAN — LOGIKA (tanpa DOM). R2 "Cincin Bersarang" (dikunci owner 13 Sep 2026) di atas DATA TOKO.
//
// Aturan yang dipegang (permintaan owner 13 Sep: "pergerakan setiap detik, menit, jam, hari, minggu, bulan, tahun"):
//  - tujuh skala; tiap skala memajang tiga lapis cincin (luar · induk · kakek) dan satu angka besar;
//  - angka uang & margin dibaca dari MESIN yang sama dengan sistem lama (hitungLabaRentang, hitungPiutang, kasPada, …);
//    margin = MARGIN KOTOR (keputusan K1, 16 Sep) dan layar menyebut kalau ada baris tanpa modal yang tidak ikut dihitung;
//  - pembanding selalu "sampai titik yang sama" (kemarin jam segini, minggu lalu sampai hari & jam yang sama, bulan lalu sampai
//    tanggal yang sama) — dan layar MENOLAK membandingkan kalau jendela pembandingnya mendahului catatan pertama toko;
//  - periode berjalan digambar bertepi putus (kelas 'berjalan'), yang belum terjadi tipis ('rel'), yang sebelum ada catatan 'absen';
//  - BACA SAJA: layar ini tidak menulis apa pun.
import { hitungLabaRentang, hitungPiutang, hitungUtangPemasok, hitungStokKarungPerMerk, hitungStokKemasan, hitungLajuPakai, kasPada } from '../mesin/beku.js';
import { bakuCaraBayar, daftarGerakanKas, pesananBelumTuntas, namaBulanPanjang, AMBANG_HARI_KRITIS } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPesanan, ambilTitikKas } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';

export const SKALA = [['langsung', 'Langsung'], ['menit', 'Menit'], ['jam', 'Jam'], ['hari', 'Hari'], ['minggu', 'Minggu'], ['bulan', 'Bulan'], ['tahun', 'Tahun']];
const LAPISAN = { langsung: ['m15', 'menit', 'jam'], menit: ['menit', 'jam', 'hari'], jam: ['jam', 'hari', 'bulan'], hari: ['hari', 'minggu', 'bulan'], minggu: ['minggu', 'bulan', 'tahun'], bulan: ['bulan', 'tahun', null], tahun: ['tahun', null, null] };
const SEMUA_LAPIS = ['m15', 'menit', 'jam', 'hari', 'minggu', 'bulan', 'tahun'];
const RK_NAMA_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const JAM_BUKA = 5, JAM_TUTUP = 21;   // rentang cincin jam; nota di luar rentang tetap masuk angka, hanya tidak punya sel

const rkP2 = (n) => String(n).padStart(2, '0');
const rkIso = (d) => hariIniIso(d);
const rkGeser = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const rkAwalMinggu = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; };   // Senin
const rkPersen = (a, b) => (b > 0 ? (a >= b ? '+' : '−') + String(Math.abs(Math.round((a / b - 1) * 1000) / 10)).replace('.', ',') + '%' : '');
const rkKunciNota = (p) => String(p.trxId || p.grupNota || p.id);
function rkTeksBaris(p) {
  if (p.jenis === 'kemasan') return (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg × ' + (p.jumlahUnit || '');
  if (p.jenis === 'karung') return (p.merkSumber || '') + ' ' + (p.beratKarungAcuan || 50) + ' kg × ' + (p.jumlahKarung || '');
  if (p.jenis === 'literan') return (p.merkSumber || '') + ' ' + String(p.jumlahLiter || 0).replace('.', ',') + ' L';
  if (p.jenis === 'repacking') return 'Repack ' + (p.namaProduk || '') + ' ' + String(p.totalKg || 0).replace('.', ',') + ' kg';
  return p.namaProduk || p.jenis || '';
}

/** Indeks penjualan berlaku: per hari, dan baris hari ini & kemarin dengan menit-ke-berapa. Dibangun sekali per perubahan data. */
export function bangunIndeks() {
  const perHari = {}; let mulai = '';
  ambilPenjualan().forEach((p) => {
    const t = p.tanggal || ''; if (!t) return;
    if (!mulai || t < mulai) mulai = t;
    const h = perHari[t] || (perHari[t] = { omzet: 0, nota: new Set(), baris: [] });
    h.omzet += p.hargaTotal || 0; h.nota.add(rkKunciNota(p)); h.baris.push(p);
  });
  return { perHari, mulai };
}
const rkMenitKe = (p) => { const m = /^(\d{1,2})[:.](\d{2})/.exec(p.jam || ''); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };
function rkJumlahRentang(ix, dariIso, sampaiIso, sampaiMenitHariAkhir) {
  let omzet = 0; const nota = new Set(); let hariBuka = 0;
  Object.keys(ix.perHari).forEach((t) => {
    if (t < dariIso || t > sampaiIso) return;
    const h = ix.perHari[t];
    if (t === sampaiIso && sampaiMenitHariAkhir != null) {
      let ada = false;
      h.baris.forEach((p) => { const m = rkMenitKe(p); if (m === null || m <= sampaiMenitHariAkhir) { omzet += p.hargaTotal || 0; nota.add(rkKunciNota(p)); ada = true; } });
      if (ada) hariBuka += 1;
    } else { omzet += h.omzet; h.nota.forEach((k) => nota.add(k)); hariBuka += 1; }
  });
  return { omzet, nota: nota.size, hariBuka };
}

/** Sel-sel satu lapis cincin: {sel:[{v, kelas}], jalan, vmax}. v null = sebelum ada catatan, 'rel' = belum terjadi. */
function rkDataLapis(nama, ix, kini) {
  const hari = rkIso(kini); const menitKini = kini.getHours() * 60 + kini.getMinutes();
  const barisHari = (ix.perHari[hari] || { baris: [] }).baris;
  const sel = []; let jalan = 0;
  if (nama === 'm15' || nama === 'menit') {
    const n = nama === 'm15' ? 15 : 60; const isi = new Array(n).fill(0);
    barisHari.forEach((p) => { const m = rkMenitKe(p); if (m === null) return; const lalu = menitKini - m; if (lalu >= 0 && lalu < n) isi[n - 1 - lalu] += p.hargaTotal || 0; });
    isi.forEach((v, i) => sel.push(i === n - 1 ? { v: v, kelas: 'berjalan' } : v > 0 ? { v: nama === 'm15' ? 1 : v, kelas: nama === 'm15' ? 'titik' : 'emas' } : { v: 'rel', kelas: 'rel' }));
    jalan = n - 1;
  } else if (nama === 'jam') {
    const isi = {}; barisHari.forEach((p) => { const m = rkMenitKe(p); if (m === null) return; const j = Math.floor(m / 60); isi[j] = (isi[j] || 0) + (p.hargaTotal || 0); });
    const jamKini = Math.min(JAM_TUTUP, Math.max(JAM_BUKA, kini.getHours()));
    for (let j = JAM_BUKA; j <= JAM_TUTUP; j++) sel.push(j === jamKini ? { v: isi[j] || 0, kelas: 'berjalan' } : j > jamKini ? { v: 'rel', kelas: 'rel' } : { v: isi[j] || 0, kelas: 'emas' });
    jalan = jamKini - JAM_BUKA;
  } else if (nama === 'hari') {
    for (let i = 29; i >= 0; i--) { const t = rkIso(rkGeser(kini, -i)); sel.push(t < ix.mulai || !ix.mulai ? { v: null, kelas: 'absen' } : i === 0 ? { v: (ix.perHari[t] || {}).omzet || 0, kelas: 'berjalan' } : { v: (ix.perHari[t] || {}).omzet || 0, kelas: 'emas' }); }
    jalan = 29;
  } else if (nama === 'minggu') {
    const awal = rkAwalMinggu(kini);
    for (let i = 11; i >= 0; i--) { const a = rkGeser(awal, -7 * i), z = rkGeser(a, 6); const v = rkJumlahRentang(ix, rkIso(a), rkIso(z)).omzet;
      sel.push(!ix.mulai || rkIso(z) < ix.mulai ? { v: null, kelas: 'absen' } : i === 0 ? { v, kelas: 'berjalan' } : { v, kelas: 'emas' }); }
    jalan = 11;
  } else if (nama === 'bulan') {
    const th = kini.getFullYear(), blnKini = kini.getMonth();
    for (let b = 0; b < 12; b++) { const a = th + '-' + rkP2(b + 1) + '-01', z = th + '-' + rkP2(b + 1) + '-31'; const v = rkJumlahRentang(ix, a, z).omzet;
      sel.push(b > blnKini ? { v: 'rel', kelas: 'rel' } : (!ix.mulai || z < ix.mulai) ? { v: null, kelas: 'absen' } : b === blnKini ? { v, kelas: 'berjalan' } : { v, kelas: 'emas' }); }
    jalan = blnKini;
  } else if (nama === 'tahun') {
    const thMulai = ix.mulai ? Number(ix.mulai.slice(0, 4)) : kini.getFullYear();
    for (let t = thMulai; t <= kini.getFullYear(); t++) sel.push({ v: rkJumlahRentang(ix, t + '-01-01', t + '-12-31').omzet, kelas: t === kini.getFullYear() ? 'berjalan' : 'emas' });
    jalan = sel.length - 1;
  }
  const vmax = Math.max(1, ...sel.map((c) => (typeof c.v === 'number' ? c.v : 0)));
  return { sel, jalan, vmax };
}

/** Geometri cincin — rumus papan R2 (sektorVals): jari-jari per peran, tebal ∝ akar nilai, sel berjalan di jam 12. */
export function susunSektor(skala, ix, kini) {
  const peran = LAPISAN[skala]; const R = [86, 66, 49], WMAX = [13, 11, 9]; const out = [];
  peran.forEach((nama, idx) => {
    if (!nama) return;
    const d = rkDataLapis(nama, ix, kini); const r = R[idx], wmax = WMAX[idx];
    const n = d.sel.length, C = 2 * Math.PI * r, span = C / n, gap = Math.min(2.2, span * 0.18), geser = (d.jalan + 0.5) * span;
    d.sel.forEach((c, i) => {
      let w = wmax, kelas = c.kelas, len = span - gap;
      if (c.v === null) { w = 1; kelas = 'absen'; len = span * 0.5; }
      else if (c.v === 'rel') { w = 1; kelas = 'rel'; }
      else if (c.kelas === 'titik') { w = 5; len = 2; }
      else { const v = typeof c.v === 'number' ? c.v : 0; w = Math.max(1.5, wmax * Math.sqrt(Math.min(1, v / d.vmax))); if (v === 0 && c.kelas !== 'berjalan') { w = 1; kelas = 'rel'; } }
      let start = i * span - geser; while (start < 0) start += C;
      out.push({ lapis: nama, r, w: Math.round(w * 100) / 100, da: len.toFixed(2) + ' ' + (C - len).toFixed(2), do: (-start).toFixed(2), kelas });
    });
  });
  return out;
}

function rkMarginTeks(cocok) {
  const l = hitungLabaRentang(cocok);
  if (!(l.omzetHitung > 0)) return { teks: '', l };
  const pct = String(Math.round(l.margin / l.omzetHitung * 1000) / 10).replace('.', ',');
  return { teks: 'margin kotor ' + RP(l.margin) + ' · ' + pct + '%' + (l.jumlahTanpaHpp ? ' (' + l.jumlahTanpaHpp + ' baris tanpa modal tidak ikut)' : ''), l };
}

/** Semua yang digambar layar Ringkasan untuk satu skala pada satu saat. */
export function susunRingkasan(skala, ix, kini) {
  const hari = rkIso(kini); const menitKini = kini.getHours() * 60 + kini.getMinutes();
  const kemarin = rkIso(rkGeser(kini, -1));
  const H = rkJumlahRentang(ix, hari, hari);
  const barisHari = (ix.perHari[hari] || { baris: [] }).baris;
  const M60 = (() => { let o = 0; const n = new Set(); barisHari.forEach((p) => { const m = rkMenitKe(p); if (m !== null && menitKini - m >= 0 && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } }); return { omzet: o, nota: n.size }; })();
  const M15 = (() => { let o = 0; const n = new Set(); barisHari.forEach((p) => { const m = rkMenitKe(p); if (m !== null && menitKini - m >= 0 && menitKini - m < 15) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } }); return { omzet: o, nota: n.size }; })();
  const aMg = rkAwalMinggu(kini); const MG = rkJumlahRentang(ix, rkIso(aMg), hari);
  const aBl = hari.slice(0, 8) + '01'; const BL = rkJumlahRentang(ix, aBl, hari);
  const aTh = hari.slice(0, 4) + '-01-01'; const TH = rkJumlahRentang(ix, aTh, hari);
  const adaSejak = (t) => !!ix.mulai && ix.mulai <= t;

  // pembanding "sampai titik yang sama"
  const kmrSegini = adaSejak(kemarin) ? rkJumlahRentang(ix, kemarin, kemarin, menitKini) : null;
  const aMgLalu = rkGeser(aMg, -7); const mgLalu = adaSejak(rkIso(aMgLalu)) ? rkJumlahRentang(ix, rkIso(aMgLalu), rkIso(rkGeser(kini, -7)), menitKini) : null;
  const blLaluAwal = (() => { const d = new Date(kini.getFullYear(), kini.getMonth() - 1, 1); return d; })();
  const blLaluAkhir = (() => { const akhir = new Date(kini.getFullYear(), kini.getMonth(), 0).getDate(); return new Date(kini.getFullYear(), kini.getMonth() - 1, Math.min(kini.getDate(), akhir)); })();
  const blLalu = adaSejak(rkIso(blLaluAwal)) ? rkJumlahRentang(ix, rkIso(blLaluAwal), rkIso(blLaluAkhir)) : null;
  const namaBlLalu = namaBulanPanjang(rkIso(blLaluAwal).slice(0, 7));

  const jamIsi = {}; barisHari.forEach((p) => { const m = rkMenitKe(p); if (m === null) return; const j = Math.floor(m / 60); const o = jamIsi[j] || (jamIsi[j] = { omzet: 0, nota: new Set() }); o.omzet += p.hargaTotal || 0; o.nota.add(rkKunciNota(p)); });
  const jamKini = kini.getHours(); const jamSibuk = Object.keys(jamIsi).sort((a, b) => jamIsi[b].omzet - jamIsi[a].omzet)[0];
  const mgHari = rkMarginTeks((t) => t === hari);

  const kepala = {
    langsung: { angka: H.omzet, judul: 'Omzet hari ini · hidup', sub: [mgHari.teks, H.nota + ' nota'].filter(Boolean).join(' · '),
      banding: 'Nota ke-' + H.nota + ' hari ini' + (kmrSegini ? ' · kemarin jam segini nota ke-' + kmrSegini.nota : ' · kemarin belum ada catatan') },
    menit: { angka: M60.omzet, judul: '60 menit terakhir · ' + rkP2(kini.getHours()) + '.' + rkP2(kini.getMinutes()), sub: M60.nota ? RP(Math.round(M60.omzet / M60.nota)) + '/nota · ' + M60.nota + ' nota' : 'belum ada nota dalam 60 menit ini',
      banding: (() => { if (!adaSejak(kemarin)) return 'kemarin belum ada catatan · belum bisa dibandingkan'; let o = 0; const n = new Set(); (ix.perHari[kemarin] || { baris: [] }).baris.forEach((p) => { const m = rkMenitKe(p); if (m !== null && menitKini - m >= 0 && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } }); return 'kemarin jendela ini ' + n.size + ' nota · ' + RP(o) + (o > 0 ? ' (' + rkPersen(M60.omzet, o) + ')' : ''); })() },
    jam: { angka: H.omzet, judul: 'Hari ini · per jam', sub: [mgHari.teks, H.nota + ' nota', H.nota ? RP(Math.round(H.omzet / H.nota)) + '/nota' : ''].filter(Boolean).join(' · '),
      banding: 'Jam ' + rkP2(jamKini) + ' berjalan ' + RP((jamIsi[jamKini] || { omzet: 0 }).omzet) + ' · ' + ((jamIsi[jamKini] || { nota: new Set() }).nota.size) + ' nota' + (jamSibuk != null ? ' · tersibuk ' + rkP2(jamSibuk) + ' · ' + RP(jamIsi[jamSibuk].omzet) : '') },
    hari: { angka: MG.omzet, judul: 'Minggu ini · per hari · berjalan', sub: [rkMarginTeks((t) => t >= rkIso(aMg) && t <= hari).teks, MG.nota + ' nota', MG.nota ? RP(Math.round(MG.omzet / MG.nota)) + '/nota' : ''].filter(Boolean).join(' · '),
      banding: mgLalu ? 'minggu lalu sampai ' + RK_NAMA_HARI[kini.getDay()] + ' jam segini: ' + RP(mgLalu.omzet) + (mgLalu.omzet > 0 ? ' (' + rkPersen(MG.omzet, mgLalu.omzet) + ')' : '') : 'minggu lalu belum lengkap tercatat · belum bisa dibandingkan' },
    bulan: { angka: BL.omzet, judul: namaBulanPanjang(hari.slice(0, 7)) + ' · berjalan', sub: [rkMarginTeks((t) => t >= aBl && t <= hari).teks, BL.hariBuka + ' hari buka · ' + BL.nota + ' nota'].filter(Boolean).join(' · '),
      banding: blLalu ? namaBlLalu + ' sampai tanggal ' + blLaluAkhir.getDate() + ': ' + RP(blLalu.omzet) + (blLalu.omzet > 0 ? ' (' + rkPersen(BL.omzet, blLalu.omzet) + ')' : '') : (ix.mulai && ix.mulai.slice(0, 7) === rkIso(blLaluAwal).slice(0, 7) ? namaBlLalu + ' hanya sejak tanggal ' + Number(ix.mulai.slice(8, 10)) + ' · belum bisa dibandingkan' : 'bulan lalu belum ada catatan · belum bisa dibandingkan') },
    tahun: { angka: TH.omzet, judul: hari.slice(0, 4) + (ix.mulai && ix.mulai > aTh ? ' · sejak ' + Number(ix.mulai.slice(8, 10)) + ' ' + namaBulanPanjang(ix.mulai.slice(0, 7)).split(' ')[0] : ''), sub: TH.hariBuka + ' hari buka · ' + TH.nota + ' nota' + (TH.hariBuka ? ' · rata-rata ' + RP(Math.round(TH.omzet / TH.hariBuka)) + '/hari buka' : ''),
      banding: ix.mulai && ix.mulai < aTh ? 'tahun lalu sampai tanggal yang sama: ' + RP(rkJumlahRentang(ix, (Number(hari.slice(0, 4)) - 1) + '-01-01', (Number(hari.slice(0, 4)) - 1) + hari.slice(4)).omzet) : 'Pembanding tahun lalu belum ada — catatan toko baru mulai ' + (ix.mulai ? Number(ix.mulai.slice(8, 10)) + ' ' + namaBulanPanjang(ix.mulai.slice(0, 7)) : 'hari ini') },
  };
  kepala.minggu = Object.assign({}, kepala.hari, { judul: 'Minggu ini · berjalan' });

  const nilaiLapis = {
    m15: ['15 menit terakhir', RP(M15.omzet), M15.nota + ' nota'],
    menit: ['60 menit terakhir', RP(M60.omzet), M60.nota + ' nota'],
    jam: ['Jam ' + rkP2(jamKini) + ' · berjalan', RP((jamIsi[jamKini] || { omzet: 0 }).omzet), ((jamIsi[jamKini] || { nota: new Set() }).nota.size) + ' nota' + (jamSibuk != null ? ' · tersibuk ' + rkP2(jamSibuk) : '')],
    hari: ['Hari ini', RP(H.omzet), H.nota + ' nota' + (kmrSegini ? ' · kemarin jam segini ' + RP(kmrSegini.omzet) : '')],
    minggu: ['Minggu ini', RP(MG.omzet), MG.nota + ' nota' + (mgLalu ? ' · minggu lalu ' + RP(mgLalu.omzet) : '')],
    bulan: [namaBulanPanjang(hari.slice(0, 7)).split(' ')[0], RP(BL.omzet), BL.nota + ' nota' + (blLalu ? ' · ' + namaBlLalu.split(' ')[0] + ' ' + RP(blLalu.omzet) : '')],
    tahun: [hari.slice(0, 4), RP(TH.omzet), TH.hariBuka + ' hari buka · ' + TH.nota + ' nota'],
  };
  const lapisan = LAPISAN[skala].filter(Boolean).map((p, i) => ({ nama: ['Luar', 'Induk', 'Kakek'][i] + ' · ' + nilaiLapis[p][0], nilai: nilaiLapis[p][1], ket: nilaiLapis[p][2] }));

  // umpan: nota hari ini, terbaru dulu
  const petaNota = {}; barisHari.forEach((p) => { const k = rkKunciNota(p); const o = petaNota[k] || (petaNota[k] = { k, jam: p.jam || '', rp: 0, isi: [], cara: bakuCaraBayar(p.caraBayar), nama: p.namaPelanggan || '' }); o.rp += p.hargaTotal || 0; o.isi.push(rkTeksBaris(p)); if ((p.jam || '') > o.jam) o.jam = p.jam; });
  const umpan = Object.values(petaNota).sort((a, b) => (b.jam || '').localeCompare(a.jam || '')).slice(0, 8)
    .map((o) => ({ k: o.k, jam: o.jam, isi: o.isi[0] + (o.isi.length > 1 ? ' +' + (o.isi.length - 1) : '') + (o.nama ? ' · ' + o.nama : '') + (o.cara !== 'Tunai' ? ' · ' + (o.cara === 'Kredit' ? 'BON' : o.cara) : ''), rp: o.rp }));
  const notaTerakhirMenit = barisHari.reduce((a, p) => { const m = rkMenitKe(p); return m !== null && m <= menitKini && m > a ? m : a; }, -1);   // nota berjam SESUDAH sekarang (jam perangkat lain maju) tidak dihitung

  return Object.assign({ skala, hari, jamKini, lapisan, umpan, notaHariIni: H.nota, sejakNotaMenit: notaTerakhirMenit >= 0 ? menitKini - notaTerakhirMenit : null,
    sektor: susunSektor(skala, ix, kini) }, kepala[skala]);
}

/** Kas: total semua kantong dari mesin kasPada(); null = titik kas belum disetel di perangkat ini (layar menolak menebak). */
export function susunKas(kini) {
  const hari = rkIso(kini); const titik = ambilTitikKas(); const total = kasPada();
  let masukLaci = 0, masukRek = 0, keluar = 0;
  daftarGerakanKas().forEach((r) => { if (r.t !== hari) return; if (r.masuk > 0) { if (r.kantong === 'rekening') masukRek += r.masuk; else masukLaci += r.masuk; } keluar += r.keluar || 0; });
  return { adaTitik: !!titik && total !== null, total, titikTanggal: titik ? titik.tanggal : '', masukLaci, masukRek, keluar };
}

/** Perlu perhatian: bon, utang pemasok, stok menipis (aturan laju live: hari tersisa ≤ AMBANG_HARI_KRITIS), pesanan aktif. */
export function susunPerhatian() {
  const out = [];
  const piutang = hitungPiutang().filter((x) => (x.sisa || 0) > 0);
  if (piutang.length) { const tertua = Math.max(...piutang.map((x) => x.umurHari || 0)); out.push({ teks: 'Bon belum lunas · ' + piutang.length + ' nama' + (tertua ? ' · tertua ' + tertua + ' hari' : ''), nilai: RP(piutang.reduce((a, x) => a + x.sisa, 0)), awas: tertua >= 30 }); }
  const up = hitungUtangPemasok(); const totalUp = up.reduce((a, x) => a + (x.totalUtang || 0), 0);
  const bonTertua = Math.max(0, ...up.map((x) => Math.max(0, ...(x.bon || []).map((b) => b.umurHari || 0))));
  if (totalUp > 0) out.push({ teks: 'Utang ke pemasok · ' + up.filter((x) => x.totalUtang > 0).length + ' pemasok' + (bonTertua ? ' · bon tertua ' + bonTertua + ' hari' : ''), nilai: RP(totalUp), awas: false });
  const laju = hitungLajuPakai(); const stokK = hitungStokKarungPerMerk(); const stokM = hitungStokKemasan(); const tipis = [];
  Object.keys(stokK).forEach((m) => { const l = (laju.kgMerk || {})[m] || 0; const sisa = stokK[m].sisaKg || 0; if (l > 0 && sisa / l <= AMBANG_HARI_KRITIS) tipis.push({ nama: m, hari: Math.max(0, sisa / l) }); });
  Object.keys(stokM).forEach((k) => { const l = (laju.unitKemasan || {})[k] || 0; const sisa = stokM[k].sisaUnit || 0; if (l > 0 && sisa / l <= AMBANG_HARI_KRITIS) tipis.push({ nama: stokM[k].namaProduk + ' ' + stokM[k].ukuranKemasan + ' kg', hari: Math.max(0, sisa / l) }); });
  tipis.sort((a, b) => a.hari - b.hari);
  if (tipis.length) out.push({ teks: 'Menipis (≤ ' + AMBANG_HARI_KRITIS + ' hari menurut laju jual): ' + tipis.slice(0, 3).map((x) => x.nama).join(', ') + (tipis.length > 3 ? ' …' : ''), nilai: tipis.length + ' barang', awas: true });
  const ps = ambilPesanan().filter(pesananBelumTuntas);
  if (ps.length) out.push({ teks: 'Pesanan belum dibayar · ' + ps.filter((p) => p.status === 'diantar').length + ' sudah diantar', nilai: ps.length + ' pesanan', awas: false });
  return out;
}

export function salam(kini) { const j = kini.getHours(); return j < 11 ? 'Selamat pagi' : j < 15 ? 'Selamat siang' : j < 19 ? 'Selamat sore' : 'Selamat malam'; }
export function tanggalPanjang(kini) { return RK_NAMA_HARI[kini.getDay()] + ', ' + kini.getDate() + ' ' + namaBulanPanjang(rkIso(kini).slice(0, 7)); }
export const kelompokAngka = (n) => RP(n).replace(/^Rp\s?/, 'Rp ').split(/[ .]/).map((t, i) => (i >= 2 ? '.' + t : t));
