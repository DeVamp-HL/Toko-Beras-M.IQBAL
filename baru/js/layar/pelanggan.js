// LAYAR PELANGGAN — GAMBAR & KETUKAN. Tiga keluarga (dikunci owner 18 Sep): KENALI (Sketsa · Tampah · Belanja · Jam · Minggu · Benang · Hafalan),
// BON (Buku · Papan · Umur, lembar orang: tagih / bayar / hapus buku), THR (Daftar · Meja · Amplop). Logika & angka di pelanggan-logika.js dan bon-logika.js.
// Layar dimorf (elemen hidup terus): polaroid muncul bergiliran, butir tampah bergeser, jarum jam berputar, batang bon tumbuh.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { pasangIsian } from '../inti/isian.js';
import { RP, DESIMAL, tanggalPendek, hariIniIso, jamKini } from '../inti/format.js';
import * as P from './pelanggan-logika.js';
import * as B from './bon-logika.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, tulisBertahap, perbaruiKolom } from '../data/toko.js';
import { bukanOwner } from './akses-layar.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const IKON_L = { motor: '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-6h5l3 6M10 10l-1-3H7"/>', kaki: '<circle cx="12" cy="5" r="2"/><path d="M12 7v7M12 14l-3 6M12 14l3 6M8 11l4-2 4 2"/>', bak: '<path d="M2 8h11v8H2zM13 11h5l3 3v2h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
  becak: '<circle cx="5" cy="17" r="3"/><circle cx="12" cy="17" r="3"/><circle cx="20" cy="17" r="2.5"/><path d="M3 12h10V7H6z"/>', gerobak: '<path d="M3 8h14l-2 8H5zM17 8l4-3"/><circle cx="10" cy="19" r="2.5"/>', karung: '<path d="M7 6q-2-3 1-4q2 2 4 2t4-2q3 1 1 4q3 8 1 14H6q-2-6 1-14z"/>', kemasan: '<path d="M6 8h12l1 13H5zM9 8V6a3 3 0 0 1 6 0v2"/>', liter: '<path d="M6 6h11v13a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2zM17 9h2a2 2 0 0 1 0 5h-2"/>' };
/** Potret dari cip (Sketsa dari Ciri): tanpa foto pun tiap orang punya gambarnya; ubah cirinya, gambarnya ikut. */
function svgSketsa(sk, kelas) {
  const lencana = (x, ikon) => '<g transform="translate(' + x + ' 48)"><circle class="lencana" r="8"/><g class="lencana-ikon" transform="translate(-6 -6) scale(0.5)">' + IKON_L[ikon] + '</g></g>';
  // perawakan: bahu lebih lebar (gemuk) / sempit (kurus); kepala lebih tinggi (tinggi) / rendah (pendek) — owner 23 Sep: serinci mungkin
  const rx = sk.gemuk ? 29 : sk.kurus ? 19 : 24; const dy = sk.tinggi ? -4 : sk.pendek ? 4 : 0; const cy = 34 + dy;
  const kepala = (sk.kerudung ? '<path class="kerudung" d="M14 58 Q12 18 32 14 Q52 18 50 58 Z"/><ellipse class="kepala" cx="32" cy="' + cy + '" rx="10" ry="12"/>' : '<ellipse class="kepala" cx="32" cy="' + cy + '" rx="12" ry="14"/>'
      + (sk.rambut && !sk.uban ? (sk.keriting ? '<path class="rambut" d="M18 ' + (cy - 4) + ' q-2 -8 4 -10 q1 -7 8 -6 q3 -6 9 -2 q6 -3 8 4 q6 1 4 8 q3 5 -2 6 Q40 ' + (cy - 12) + ' 30 ' + (cy - 11) + ' Q22 ' + (cy - 10) + ' 18 ' + (cy - 4) + ' Z"/>' : sk.muda ? '<path class="rambut" d="M19 ' + (cy - 4) + ' Q20 ' + (cy - 20) + ' 34 ' + (cy - 19) + ' Q47 ' + (cy - 18) + ' 45 ' + (cy - 4) + ' Q40 ' + (cy - 12) + ' 30 ' + (cy - 11) + ' Q22 ' + (cy - 10) + ' 19 ' + (cy - 4) + ' Z"/>' : '<path class="rambut" d="M19 ' + (cy - 4) + ' Q20 ' + (cy - 18) + ' 32 ' + (cy - 18) + ' Q44 ' + (cy - 18) + ' 45 ' + (cy - 4) + ' Q38 ' + (cy - 10) + ' 26 ' + (cy - 10) + ' Q21 ' + (cy - 9) + ' 19 ' + (cy - 4) + ' Z"/>') : '')
      + (sk.rambut && sk.panjang ? '<path class="rambut ' + (sk.uban ? 'uban' : '') + '" d="M19 ' + (cy - 4) + ' Q16 ' + (cy + 14) + ' 18 ' + (cy + 24) + ' L23 ' + (cy + 24) + ' Q21 ' + (cy + 8) + ' 22 ' + (cy - 2) + ' Z M45 ' + (cy - 4) + ' Q48 ' + (cy + 14) + ' 46 ' + (cy + 24) + ' L41 ' + (cy + 24) + ' Q43 ' + (cy + 8) + ' 42 ' + (cy - 2) + ' Z"/>' : '')
      + (sk.rambut && sk.uban ? '<path class="uban" d="M19 ' + (cy - 4) + ' Q20 ' + (cy - 18) + ' 32 ' + (cy - 18) + ' Q44 ' + (cy - 18) + ' 45 ' + (cy - 4) + ' Q38 ' + (cy - 10) + ' 26 ' + (cy - 10) + ' Q21 ' + (cy - 9) + ' 19 ' + (cy - 4) + ' Z"/>' : '')
      + (sk.peci ? '<path class="peci" d="M19 ' + (cy - 10) + ' L20 ' + (cy - 19) + ' Q32 ' + (cy - 23) + ' 44 ' + (cy - 19) + ' L45 ' + (cy - 10) + ' Z"/>' : '') + (sk.topi ? '<path class="peci topi" d="M20 ' + (cy - 10) + ' Q32 ' + (cy - 24) + ' 44 ' + (cy - 10) + ' Z M14 ' + (cy - 9) + ' h36 v3 h-36 z"/>' : ''))
    + (sk.cadar ? '<path class="kerudung cadar" d="M21 ' + (cy + 1) + ' h22 v9 q-11 6 -22 0 z"/>' : '')
    + (sk.kumis ? '<path class="kumis" d="M25 ' + (cy + 6) + ' q7 -3 14 0 q-7 3 -14 0 z"/>' : '') + (sk.janggut ? '<path class="kumis janggut" d="M22 ' + (cy + 6) + ' q10 16 20 0 q-2 12 -10 13 q-8 -1 -10 -13 z"/>' : '')
    + (sk.tahiLalat ? '<circle class="tahi-lalat" cx="38" cy="' + (cy + 8) + '" r="1.3"/>' : '') + (sk.kacamata ? '<g class="kacamata"><circle cx="26" cy="' + (cy + 1) + '" r="4.5"/><circle cx="38" cy="' + (cy + 1) + '" r="4.5"/><path d="M30.5 ' + (cy + 1) + 'h3"/></g>' : '');
  const isi = sk.kosong ? '<rect class="tepi-putus" x="3" y="3" width="58" height="58" rx="3"/><text class="tanya" x="32" y="42" text-anchor="middle">?</text>'
    : '<ellipse class="bahu" cx="32" cy="66" rx="' + rx + '" ry="18"/>' + kepala + (sk.naik ? lencana(12, sk.naik) : '') + (sk.beli ? lencana(52, sk.beli) : '');
  return '<svg class="sk w' + (sk.warna || 0) + ' ' + (kelas || '') + '" viewBox="0 0 64 64" aria-hidden="true"><rect class="latar" width="64" height="64" rx="4"/>' + isi + '</svg>';
}
const KUNCI_TAB = 'miqbal_baru_pelanggan_tab'; const KUNCI_HAFAL = 'miqbal_baru_hafal';
const bacaLokal = (k) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } }; const simpanLokal = (k, v) => { try { if (v) localStorage.setItem(k, JSON.stringify(v)); else localStorage.removeItem(k); } catch (e) { /* abaikan */ } };
const KELUARGA = [['kenali', 'Kenali'], ['bon', 'Bon'], ['thr', 'THR']];
const TAB_K = [['wajah', 'Wajah'], ['tampah', 'Tampah'], ['belanja', 'Belanja'], ['jam', 'Jam'], ['minggu', 'Minggu'], ['benang', 'Benang'], ['hafal', 'Hafalan']];
const TAB_B = [['buku', 'Buku bon'], ['papan', 'Papan tagih'], ['umur', 'Garis umur']]; const TAB_T = [['daftar', 'Daftar setia'], ['meja', 'Meja bingkisan'], ['amplop', 'Amplop']];
const kuisKosong = (hanya, putaran) => ({ putaran: putaran || 1, no: 0, jawab: null, benar: 0, salah: [], hanya: hanya || null });

export function pasangLayarPelanggan(akar, opsi) {
  const tabAwal = bacaLokal(KUNCI_TAB) || {};
  // putaran 23d: keadaan awal sebagai FUNGSI — dipanggil ulang saat ganti orang (inti/isian.js)
  const awal = () => ({ keluarga: KELUARGA.some((k) => k[0] === tabAwal.keluarga) ? tabAwal.keluarga : 'kenali', tabK: TAB_K.some((t) => t[0] === tabAwal.tabK) ? tabAwal.tabK : 'wajah', tabB: 'buku', tabT: 'daftar', kabar: '', kabarAwas: false,
    cari: '', tampi: [], notaKunci: null, keranjang: [], benangSiapa: null, titip: null, titipCari: '', kuis: kuisKosong(), hafal: bacaLokal(KUNCI_HAFAL) || null,
    kartu: null, yakinHapusNama: false, baru: null, gabung: null, bukuKunci: null, ember: '', orangBon: null, lembarBon: null, bayar: { nominal: '', cara: 'Tunai', catatan: '', pengantar: '' }, hapusIsi: { nominal: '', alasan: '' }, yakinHapus: false, janji: 7,
    tahun: (opsi.sekarang() || new Date()).getFullYear(), thrOrang: null, beri: { bentuk: '', lain: '', nilai: '' }, usulBentuk: null, atur: null, bersih: null });
  const K = buatKeadaan(awal());
  const ISIAN = pasangIsian(K, awal, ['kartu', 'baru', 'gabung', 'atur', 'bayar', 'hapusIsi', 'beri', 'titip'], []);
  const set = (p) => K.setel(p); const st = () => K.baca(); let tampil = false;
  const kini = () => opsi.sekarang() || new Date();
  const waktu = () => { const d = kini(); return { tanggal: hariIniIso(d), jam: jamKini(d), kini: new Date().toISOString(), idUnik: () => Date.now() + Math.random() }; };
  const ingatTab = () => simpanLokal(KUNCI_TAB, { keluarga: st().keluarga, tabK: st().tabK });
  // putaran 25: hapus + dokumen dalam SATU kiriman yang hasilnya diperiksa; SATUKAN / hapus nama yang menyebar ke bulan-bulan lalu (r.kelompok) dikirim BERTAHAP
  async function tulis(r) {
    if (!r || r.tolak) { set({ kabar: (r && r.tolak) || 'Tidak ada yang ditulis', kabarAwas: true }); return false; }
    try {
      const ada = (r.dokumen && r.dokumen.length) || (r.hapus && r.hapus.length); let sim = false, tahap = 0;
      if (ada) { const x = r.kelompok ? await tulisBertahap(r.judulBertahap || 'Pelanggan bertahap', r.kelompok) : await tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus });
        if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; } sim = !!(x && x.simulasi); tahap = (x && x.potongan) || 0; }
      set(Object.assign({}, r.patch || {}, { kabar: (sim ? 'SIMULASI — ' : '') + ((r.patch && r.patch.kabar) || 'Tersimpan') + (tahap > 1 ? ' (dikirim ' + tahap + ' tahap)' : '') })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }

  const ubahKartu = (f) => { const d = JSON.parse(JSON.stringify(st().kartu)); if (!d) return; f(d); set({ kartu: d }); };
  const bukaKartu = (kunci) => { const o = P.kartuOrang(kini(), kunci); if (!o) return set({ kabar: 'Orangnya tidak ditemukan', kabarAwas: true }); set({ kartu: { kunci, nama: o.nama, cip: o.cip.slice(), catatan: o.catatan, arah: o.arah, asli: o.asli, kontak: o.kontak, biasa: o.biasa }, baru: null, gabung: null, kabar: '' }); };
  const AKSI = {
    keluarga: ({ ke }) => { const k = ke; set({ keluarga: k, kabar: '', kartu: null, baru: null, gabung: null, orangBon: null, lembarBon: null, thrOrang: null, atur: null }); ingatTab(); },
    tabK: ({ t }) => { set({ tabK: t, kabar: '' }); ingatTab(); }, tabB: ({ t }) => set({ tabB: t, kabar: '' }), tabT: ({ t }) => set({ tabT: t, kabar: '' }),
    mode: () => opsi.gantiMode(), tutupKabar: () => set({ kabar: '' }),
    cari: (v) => set({ cari: String(v).slice(0, 30) }),
    // ---- kartu orang
    bukaKartu: ({ kunci }) => bukaKartu(kunci),
    kKetik: (v, el) => ubahKartu((d) => { d[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 140 : 40); }),
    kCip: ({ nama }) => ubahKartu((d) => { d.cip = d.cip.indexOf(nama) >= 0 ? d.cip.filter((x) => x !== nama) : d.cip.concat([nama]); }),
    kArah: ({ nama }) => ubahKartu((d) => { d.arah = d.arah === nama ? '' : nama; }),
    kSimpan: async () => { const d = st().kartu; if (!d) return; if (await tulis(P.susunSimpanKartu(kini(), d.kunci, d, waktu()))) set({ kartu: null }); },
    // putaran 22 (owner 23 Sep): nama salah ketik ("b", angka) dihapus — notanya jadi tanpa nama, ketukan kedua wajib
    kHapusNama: async () => { const d = st().kartu; if (!d) return; const r = P.susunHapusNama(kini(), d.kunci, waktu(), st().yakinHapusNama); if (r.perluYakin) return set({ yakinHapusNama: true, kabar: r.tolak, kabarAwas: true }); if (await tulis(r)) set({ yakinHapusNama: false, kartu: null }); },
    kTutup: () => set({ kartu: null, baru: null, kabar: '' }),
    keBon: ({ kunci }) => { set({ keluarga: 'bon', orangBon: kunci, lembarBon: null, kartu: null, kabar: '' }); ingatTab(); },
    // ---- orang baru
    bukaBaru: () => set({ baru: { nama: '' }, kartu: null, gabung: null, kabar: '' }), baruKetik: (v) => set({ baru: { nama: String(v).slice(0, 40) } }),
    baruSimpan: async () => { const r = P.susunOrangBaru(kini(), (st().baru || {}).nama, waktu()); if (await tulis(r)) { set({ baru: null }); bukaKartu(r.kunci); } },
    // ---- nama kembar
    bukaGabung: ({ pasangan, a }) => set({ gabung: { k: pasangan, pakai: a }, kartu: null, baru: null, kabar: '' }), gabungPakai: ({ kunci }) => set({ gabung: Object.assign({}, st().gabung, { pakai: kunci }) }),
    gabungkan: async () => { const g = st().gabung; if (!g) return; const [a, b] = g.k.split('+'); const lain = g.pakai === a ? b : a; if (await tulis(Object.assign({ judulBertahap: 'SATUKAN nama' }, P.susunGabung(kini(), g.pakai, lain, waktu())))) set({ gabung: null }); },
    bukanKembar: async () => { const g = st().gabung; if (!g) return; if (await tulis(P.susunBukanKembar(g.k, waktu()))) set({ gabung: null }); },
    gabungTutup: () => set({ gabung: null, kabar: '' }),
    // ---- tampah
    tampiJawab: ({ j }) => { const t = P.susunTampah(kini(), st().tampi); if (t.tanya) set({ tampi: st().tampi.concat([{ c: t.tanya.c, j }]) }); }, tampiMundur: () => set({ tampi: st().tampi.slice(0, -1) }), tampiUlang: () => set({ tampi: [] }),
    // ---- belanja
    notaPilih: ({ kunci }) => set({ notaKunci: st().notaKunci === kunci ? null : kunci, keranjang: [], kabar: '' }), barangPilih: ({ kunci }) => set({ notaKunci: null, keranjang: st().keranjang.indexOf(kunci) >= 0 ? st().keranjang.filter((k) => k !== kunci) : st().keranjang.concat([kunci]) }),
    iniDia: async ({ nota, kunci }) => { if (await tulis(P.susunIniDia(kini(), nota, kunci))) set({ notaKunci: null }); },
    // ---- benang
    benangSiapa: ({ kunci }) => set({ benangSiapa: st().benangSiapa === kunci ? null : kunci }),
    titipBuka: () => set({ titip: { dari: st().benangSiapa, untuk: null, apa: null }, titipCari: '', kabar: '' }), titipTutup: () => set({ titip: null, titipCari: '' }), titipCari: (v) => set({ titipCari: String(v || '').slice(0, 40) }),
    titipPilih: ({ kolom, kunci }) => { const t = Object.assign({}, st().titip || {}); t[kolom] = t[kolom] === kunci ? null : kunci; set({ titip: t }); },
    titipSimpan: async () => { const t = st().titip; if (!t) return; if (await tulis(P.susunTitip(t.dari, t.untuk, t.apa, waktu()))) set({ titip: null, benangSiapa: t.dari }); },
    titipLagi: async ({ id }) => { await tulis(P.susunTitipLagi(id, waktu())); }, titipBuang: async ({ id }) => { await tulis(P.susunBuangTitip(id)); },
    // ---- hafalan
    kuisPilih: ({ kunci }) => { const q = st().kuis; if (q.jawab) return; const hf = P.susunHafalan(kini(), q); if (!hf.kartu) return; const betul = kunci === hf.kartu.kunci; set({ kuis: Object.assign({}, q, { jawab: kunci, benar: q.benar + (betul ? 1 : 0), salah: betul ? q.salah : q.salah.concat([hf.kartu.kunci]) }) }); },
    kuisLanjut: () => { const q = st().kuis; if (!q.jawab) return set({ kabar: 'Tebak dulu namanya', kabarAwas: true }); const hf = P.susunHafalan(kini(), q); const habis = q.no + 1 >= hf.dek; let hafal = st().hafal; if (habis && !q.hanya) { hafal = { benar: q.benar, dari: q.benar + q.salah.length, tanggal: waktu().tanggal }; simpanLokal(KUNCI_HAFAL, hafal); } set({ kuis: Object.assign({}, q, { no: q.no + 1, jawab: null }), hafal, kabar: '' }); },
    kuisUlangSalah: () => { const q = st().kuis; const salah = q.salah.filter((x, i, a) => a.indexOf(x) === i); if (salah.length) set({ kuis: kuisKosong(salah, q.putaran + 1) }); }, kuisMulai: () => set({ kuis: kuisKosong(null, st().kuis.putaran + 1) }),
    // ---- bon
    bukaBuku: ({ kunci }) => set({ bukuKunci: kunci, tabB: 'buku' }), emberPilih: ({ id }) => set({ ember: st().ember === id ? '' : id }),
    bukaOrangBon: ({ kunci }) => set({ orangBon: st().orangBon === kunci ? null : kunci, lembarBon: null, yakinHapus: false, kabar: '' }), bonTutup: () => set({ orangBon: null, lembarBon: null, yakinHapus: false }),
    lembarBon: ({ l }) => { const o = st().orangBon; const b = o ? B.lembarBon(kini(), o) : null; set({ lembarBon: st().lembarBon === l ? null : l, yakinHapus: false, janji: 7, bayar: { nominal: '', cara: 'Tunai', catatan: '', pengantar: '' }, hapusIsi: { nominal: b ? String(b.sisa) : '', alasan: '' }, kabar: '' }); },
    janjiPilih: ({ hari }) => set({ janji: Number(hari) }),
    kirimTagih: async () => { const o = st().orangBon; const p = B.pesanTagih(kini(), o); if (!p) return set({ kabar: 'Tidak ada yang perlu ditagih', kabarAwas: true }); try { window.open(p.url, '_blank'); } catch (e) { /* abaikan */ } if (await tulis(B.susunTagih(kini(), o, st().janji, waktu()))) set({ lembarBon: null }); },
    bayarKetik: (v, el) => { const b = Object.assign({}, st().bayar); b[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'nominal' ? 14 : 60); set({ bayar: b }); }, bayarCara: ({ cara }) => set({ bayar: Object.assign({}, st().bayar, { cara }) }),
    bayarSemua: () => { const b = B.lembarBon(kini(), st().orangBon); if (b) set({ bayar: Object.assign({}, st().bayar, { nominal: String(b.sisa) }) }); },
    bayarSimpan: async () => { const b = st().bayar; if (await tulis(B.susunBayarBon(kini(), st().orangBon, b.nominal, b.cara, b.catatan, b.pengantar, waktu()))) set({ lembarBon: null, bayar: { nominal: '', cara: 'Tunai', catatan: '', pengantar: '' } }); },
    hapusKetik: (v, el) => { const x = Object.assign({}, st().hapusIsi); x[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'nominal' ? 14 : 80); set({ hapusIsi: x, yakinHapus: false }); }, hapusAlasan: ({ nama }) => set({ hapusIsi: Object.assign({}, st().hapusIsi, { alasan: nama }), yakinHapus: false }),
    hapusSimpan: async () => { const x = st().hapusIsi; const r = B.susunHapusBon(kini(), st().orangBon, x.nominal, x.alasan, waktu(), st().yakinHapus); if (r.perluYakin) return set({ yakinHapus: true, kabar: r.tolak, kabarAwas: true }); if (await tulis(r)) set({ lembarBon: null, yakinHapus: false, hapusIsi: { nominal: '', alasan: '' } }); },
    // ---- THR
    tahunGeser: ({ arah }) => set({ tahun: Math.min(2100, Math.max(2020, st().tahun + Number(arah))), thrOrang: null }),
    thrBuka: ({ kunci }) => set({ thrOrang: st().thrOrang === kunci ? null : kunci, beri: { bentuk: '', lain: '', nilai: '' }, kabar: '' }), thrTutup: () => set({ thrOrang: null }),
    beriBentuk: ({ nama, n }) => set({ beri: { bentuk: nama, lain: '', nilai: String(n || '') } }), beriKetik: (v, el) => { const b = Object.assign({}, st().beri); b[el.dataset.kolom] = String(v).slice(0, 40); if (el.dataset.kolom === 'lain') b.bentuk = ''; set({ beri: b }); },
    beriSimpan: async () => { const b = st().beri; if (await tulis(P.susunBeriThr(kini(), st().thrOrang, st().tahun, b.bentuk || b.lain, b.nilai, waktu()))) set({ thrOrang: null }); },
    thrSerah: async ({ id }) => { if (await tulis(P.susunSerahThr(id, waktu()))) set({ thrOrang: null }); }, thrHapus: async ({ id }) => { if (await tulis(P.susunHapusThr(id))) set({ thrOrang: null }); },
    usulBentuk: ({ nama }) => set({ usulBentuk: nama }), usulPakai: async () => { await tulis(P.susunUsulThr(kini(), st().tahun, st().usulBentuk, waktu())); },
    // ---- atur (angka & daftar kebijakan owner)
    bukaAtur: () => { if (st().atur) return set({ atur: null }); const a = P.aturPelanggan(); set({ atur: { kosongKali: String(a.kosongKali / 10).replace('.', ','), notaBesar: String(a.notaBesar), tagihHari: String(a.tagihHari), macetHari: String(a.macetHari), anggaranThr: String(a.anggaranThr), salamTagih: a.salamTagih, ciriDaftar: a.ciriDaftar.map((c) => Object.assign({}, c)), arahDaftar: a.arahDaftar.slice(), titipDaftar: a.titipDaftar.slice(), alasanHapus: a.alasanHapus.slice(), bentukThr: a.bentukThr.map((b) => Object.assign({}, b)) }, bersih: null, kabar: '' }); },
    aturKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().atur)); const k = el.dataset.kolom; const i = el.dataset.i; const sub = el.dataset.sub; if (i === undefined) a[k] = String(v).slice(0, k === 'salamTagih' ? 200 : 14); else if (sub) a[k][Number(i)][sub] = String(v).slice(0, 40); else a[k][Number(i)] = String(v).slice(0, 40); set({ atur: a }); },
    aturGrup: ({ i, grup }) => { const a = JSON.parse(JSON.stringify(st().atur)); a.ciriDaftar[Number(i)].grup = grup; set({ atur: a }); },
    aturTambah: ({ daftar: k }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].push(k === 'ciriDaftar' ? { nama: '', grup: 'lain' } : k === 'bentukThr' ? { nama: '', n: 0 } : ''); set({ atur: a }); },
    aturLepas: ({ daftar: k, i }) => { const a = JSON.parse(JSON.stringify(st().atur)); a[k].splice(Number(i), 1); set({ atur: a }); },
    // putaran 23b: Bersihkan ciri yang dicabut — pratinjau dulu (tanpa menulis), cadangan hari ini, dua ketukan; hasil per batch lalu lembarnya hilang di kunjungan berikut
    bsBersihkan: async () => { const b = st().bersih || {}; if (b.menulis) return; const r = P.susunBersihkanCiri(kini(), !!b.yakin);
      if (r.perluYakin) return set({ bersih: { yakin: true }, kabar: r.tolak, kabarAwas: true }); if (r.tolak) return set({ bersih: null, kabar: r.tolak, kabarAwas: true });
      set({ bersih: { menulis: true } });
      try { const x = await perbaruiKolom(r.ubahKolom, r.ringkas); const KATA = { ok: 'tersimpan', antre: 'masuk antrean (terkirim begitu tersambung)', gagal: 'DITOLAK', simulasi: 'SIMULASI' };
        const baris = (x.potongan || []).map((p, i) => 'Batch ' + (i + 1) + ' dari ' + r.ubahKolom.length + ': ' + p.n + ' dokumen — ' + (KATA[p.keadaan] || p.keadaan) + (p.pesan ? ' (' + p.pesan + ')' : ''));
        set({ bersih: { hasil: { baris, kartu: r.rincian.kartu.length, cip: r.rincian.cip, atur: r.rincian.atur, gagal: !!x.gagal } }, kabar: (x.simulasi ? 'SIMULASI — ' : '') + (x.gagal ? 'Pembersihan berhenti — ' + (x.pesan || 'ada batch yang ditolak') : 'Bersih: ' + r.rincian.kartu.length + ' kartu, ' + r.rincian.cip + ' cip dibuang' + (r.rincian.atur ? ', setelan cip ikut' : '') + '. Unduh cadangan baru sekarang.'), kabarAwas: !!x.gagal }); }
      catch (e) { set({ bersih: null, kabar: 'GAGAL membersihkan: ' + (e && e.message ? e.message : e), kabarAwas: true }); } },
    bsBukaKartu: ({ kunci }) => { set({ atur: null, bersih: null }); bukaKartu(kunci); },
    simpanAtur: async () => { const a = st().atur; if (!a) return; const isi = Object.assign({}, a, { kosongKali: String(Math.round((Number(String(a.kosongKali).replace(',', '.')) || 0) * 10)) }); if (await tulis(P.susunAturPelanggan(isi, waktu()))) set({ atur: null }); },
  };
  delegasi(akar, AKSI);

  function gambar() {
    if (!tampil || terkunci()) return;
    const s = st(); const sumber = sumberData(); const d = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Pelanggan</div><div class="ket">${tanggalPendek(hariIniIso(d))} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil pil-akun ${sumber.jenis === 'firestore' ? '' : 'kedip'}" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      <div class="jalur" data-k="keluarga">${KELUARGA.filter(([id]) => id !== 'thr' || !bukanOwner(opsi.akun ? opsi.akun() : null)).map(([id, nm]) => h`<div class="seg ${s.keluarga === id ? 'aktif' : ''}" data-aksi="keluarga" data-ke="${id}">${nm}</div>`)}</div>
      ${s.atur ? gambarAtur(s) : s.kartu ? gambarKartu(s) : s.baru ? gambarBaru(s) : s.gabung ? gambarGabung(s) : s.keluarga === 'bon' ? gambarBon(s, d) : s.keluarga === 'thr' && !bukanOwner(opsi.akun ? opsi.akun() : null) ? gambarThr(s, d) : gambarKenali(s, d)}
    `);
    gulirkan(akar, RP);
  }
  const sk = (o, kelas) => mentah(svgSketsa(o.sk || P.sketsa(o), kelas));
  const barisOrang = (o, ekstra) => h`<div class="jawab" data-k="o-${o.kunci}" data-aksi="bukaKartu" data-kunci="${o.kunci}"><span class="kiri">${sk(o)}<div><span class="nm">${o.nama}</span><span class="w">${o.sub || P.julukan(o)}</span>${o.datang ? h`<span class="w">${o.datang}</span>` : ''}</div></span><span class="kanan" style="text-align: right;">${ekstra || ''}${o.utang > 0 ? h`<span class="w awas-teks">bon ${RP(o.utang)}</span>` : ''}</span></div>`;

  // ---------- KENALI ----------
  function gambarKenali(s, d) {
    const W = P.susunWajah(d, s.cari);
    return h`<section class="pl-kenali" data-k="kenali">
      <div class="jalur kisi" data-k="tabK">${TAB_K.map(([id, nm]) => h`<div class="seg ${s.tabK === id ? 'aktif' : ''}" data-aksi="tabK" data-t="${id}">${nm}</div>`)}</div>
      ${s.tabK === 'wajah' ? gambarWajah(s, W) : s.tabK === 'tampah' ? gambarTampah(s, d) : s.tabK === 'belanja' ? gambarBelanja(s, d) : s.tabK === 'jam' ? gambarJam(d) : s.tabK === 'minggu' ? gambarMinggu(d) : s.tabK === 'benang' ? gambarBenang(s, d) : gambarHafal(s, d)}
      ${W.kembar.length ? h`<div class="kartu" data-k="kembar" style="gap: 6px;"><div class="label">Mungkin orang yang sama — ketuk untuk memeriksa (tidak pernah digabung sendiri)</div>${W.kembar.map((p) => h`<div class="jawab" data-k="kb-${p.k}" data-aksi="bukaGabung" data-pasangan="${p.k}" data-a="${p.a}"><span class="kiri"><div><span class="nm">${p.teks}</span></div></span><span class="ket">periksa ›</span></div>`)}</div>` : ''}
      ${W.belumJadi.length ? h`<div class="pita-info" data-k="belum-jadi" style="cursor: pointer;" data-aksi="bukaKartu" data-kunci="${W.belumJadi[0].kunci}">${W.belumJadi.length} nama belum jadi (mis. "${W.belumJadi[0].nama}") — ketuk untuk membetulkan</div>` : ''}
      <div class="tombol-baris"><div class="kaca-btn putus" data-aksi="bukaBaru">＋ Orang baru</div>${bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : h`<div class="kaca-btn" data-aksi="bukaAtur">Atur: cip ciri, arah, bangku kosong, tagihan, THR</div>`}</div>
    </section>`;
  }
  function gambarWajah(s, W) {
    return h`<div data-k="wajah" style="display: flex; flex-direction: column; gap: 10px;">
      <input class="ketik-nama" id="plCari" type="text" placeholder="Cari nama… atau lihat wajahnya di bawah" value="${s.cari}" data-ketik="cari">
      <div class="ket">${W.kiniTeks}. Gambar disusun dari ciri di kartu: perawakan, kumis/janggut, kerudung/peci/topi, kacamata, uban/botak/rambut panjang; kiri bawah = datang naik apa, kanan bawah = biasa beli apa.</div>
      ${W.daftar.length ? h`<div class="sk-dinding" data-k="dinding">${W.daftar.map((o, i) => h`<div class="polaroid" data-k="pf-${o.kunci}" data-aksi="bukaKartu" data-kunci="${o.kunci}" style="--urut: ${Math.min(i, 24)};">${o.titik ? h`<span class="titik ${o.titik === 'tadi' ? '' : 'awas'}">${o.titik}</span>` : ''}${sk(o)}<div class="cp">${o.nama}</div><div class="sb">${o.sub}</div></div>`)}</div>` : h`<div class="menolak">Tidak ada nama yang cocok.</div>`}
      <div class="ket">${W.tanpaCiri} dari ${W.semua} orang belum punya ciri — di tebakan mereka cuma bisa cocok lewat jam datangnya, dan kasir menolak bon barunya.</div>
    </div>`;
  }
  function gambarTampah(s, d) {
    const T = P.susunTampah(d, s.tampi);
    return h`<div data-k="tampah" style="display: flex; flex-direction: column; gap: 10px;">
      <div style="display: flex; justify-content: space-between; align-items: baseline; gap: 8px;"><span class="ket">${T.info}</span>${T.riwayat.length ? h`<span style="display: flex; gap: 12px;"><span class="ket tautan" data-aksi="tampiMundur">mundur satu</span><span class="ket tautan" data-aksi="tampiUlang">ulangi</span></span>` : ''}</div>
      ${T.tanya ? h`<div class="kartu" data-k="tanya" style="gap: 8px;"><div class="label">${T.label}</div><div class="tp-tanya">${T.tanya.c}?</div><div class="ket">${T.kalau}</div>
        <div class="tp-jawab"><div class="kaca-btn aktif emas" data-aksi="tampiJawab" data-j="ya">YA</div><div class="kaca-btn" data-aksi="tampiJawab" data-j="bukan">BUKAN</div></div><div class="kaca-btn putus" data-aksi="tampiJawab" data-j="entah">tidak kelihatan — tanya yang lain</div></div>` : ''}
      ${T.ketemu ? h`<div class="kartu" data-k="ketemu" style="display: grid; grid-template-columns: 76px minmax(0, 1fr); gap: 12px; align-items: center; cursor: pointer;" data-aksi="bukaKartu" data-kunci="${T.ketemu.kunci}">${sk(T.ketemu, 'besar')}<div><div class="ket">tinggal satu —</div><div class="tp-tanya" style="font-size: 23px;">${T.ketemu.nama}</div><div class="ket">${T.ketemu.datang}</div><div class="ket tautan">buka kartunya ›</div></div></div>` : ''}
      ${T.sama ? h`<div class="pita-info">${T.sisa.length} orang ini tidak bisa dibedakan lagi dari cirinya — cirinya sama, atau pembedanya tadi dijawab "tidak kelihatan". Yang jamnya cocok dengan sekarang di atas.</div><div class="kartu" style="gap: 0;">${T.sisa.map((o) => h`<div class="jawab" data-k="ts-${o.kunci}" data-aksi="bukaKartu" data-kunci="${o.kunci}"><span class="kiri"><div><span class="nm">${o.nama}</span><span class="w">${o.sub}</span></div></span><span class="w">${o.jamTeks}</span></div>`)}</div>` : ''}
      ${T.buntu ? h`<div class="pita-info awas">Tidak ada yang tersisa — mungkin orang baru, atau cirinya belum pernah diisi. Mundur satu atau ulangi.</div>` : ''}
      <div class="tp" data-k="tp">${T.orang.map((o) => h`<div class="tp-butir f${o.warna} ${o.sekarang ? 'kini' : ''} ${T.orang.length === 1 ? 'satu' : ''}" data-k="tb-${o.kunci}" style="left: ${o.kiri}%; top: ${o.atas}%;" data-aksi="bukaKartu" data-kunci="${o.kunci}">${P.inisial(o.nama)}</div>`)}</div>
      ${T.lebih ? h`<div class="ket">Tampah cuma memuat 25 orang; ${T.lebih} lagi belum tergambar — jawab satu pertanyaan lagi.</div>` : ''}
      ${T.riwayat.length ? h`<div class="jalur bungkus" data-k="riwayat-tampi">${T.riwayat.map((r) => h`<div class="seg aktif" style="cursor: default;">${r}</div>`)}</div>` : ''}
      ${T.lempar.length ? h`<div class="kartu" data-k="lempar" style="gap: 5px;"><div class="label">Terlempar dari tampah — masih bisa diketuk</div><div class="jalur bungkus">${T.lempar.map((x) => h`<div class="seg" data-aksi="bukaKartu" data-kunci="${x.kunci}">${x.nama} · ${x.sebab}</div>`)}</div></div>` : ''}
      <div class="ket">Layar memilih pertanyaan yang membelah sisa orang paling rata, jadi dua–empat jawaban biasanya cukup. Bertepi putih = jam biasanya datang cocok dengan sekarang. ${T.tanpaCiri} orang belum punya ciri — tidak bisa ditampi.</div>
    </div>`;
  }
  function gambarBelanja(s, d) {
    const L = P.susunBelanja(d, s.notaKunci, s.keranjang);
    return h`<div data-k="belanja" style="display: flex; flex-direction: column; gap: 10px;">
      ${L.nota.length ? h`<div class="kartu" data-k="nota-tanpa" style="gap: 5px;"><div class="label">${L.nota.length} nota besar hari ini belum bernama (≥ ${RP(L.notaBesar)})</div>
        ${L.nota.map((n) => h`<div class="jawab ${L.dipilih === n.kunci ? 'dipilih' : ''}" data-k="nt-${n.kunci}" data-aksi="notaPilih" data-kunci="${n.kunci}"><span class="kiri"><div><span class="nm">${n.jam} · ${n.teks}</span><span class="w">${n.baris} baris</span></div></span><span class="n">${RP(n.n)}</span></div>`)}
        ${L.kecil ? h`<div class="ket">${L.kecil} nota di bawah ${RP(L.notaBesar)} tidak ditagih namanya — menuliskannya cuma memperlambat antrean.</div>` : ''}</div>` : h`<div class="pita-info">Semua nota besar hari ini sudah bernama.${L.kecil ? ' ' + L.kecil + ' nota kecil dibiarkan tanpa nama.' : ''}</div>`}
      <div class="kartu" data-k="barang" style="gap: 6px;"><div class="label">Atau ketuk yang sedang dibelinya</div><div class="jalur bungkus">${L.barang.map((b) => h`<div class="seg ${b.aktif ? 'aktif' : ''}" data-aksi="barangPilih" data-kunci="${b.kunci}">${b.nama}</div>`)}</div></div>
      <div class="ket">${!L.adaIsi ? 'Pilih nota tanpa nama di atas — atau ketuk barang yang sedang dibelinya.' : L.tebak.length + ' orang biasa membeli ini' + (L.dipilih ? ' · nota ' + L.nota.find((n) => n.kunci === L.dipilih).jam : ' · jam sekarang (' + L.waktu + ')')}</div>
      ${L.adaIsi && !L.tebak.length ? h`<div class="pita-info">Belum ada yang biasa membeli ini. Mungkin orang baru.</div>` : ''}
      ${L.tebak.length ? h`<div class="kartu" data-k="tebak" style="gap: 0;">${L.tebak.map((o) => h`<div class="jawab" data-k="tb-${o.kunci}"><span class="kiri" data-aksi="bukaKartu" data-kunci="${o.kunci}">${sk(o)}<div><span class="nm">${o.nama} <span class="pil" style="font-size: 9px;">${o.yakin}</span></span><span class="w">${o.alasan}</span><span class="w">${P.julukan(o)}</span></div></span>
        ${L.dipilih ? h`<div class="kaca-btn aktif kecil" data-aksi="iniDia" data-nota="${L.dipilih}" data-kunci="${o.kunci}">ini dia</div>` : h`<span class="ket tautan" data-aksi="bukaKartu" data-kunci="${o.kunci}">kartu ›</span>`}</div>`)}</div>` : ''}
    </div>`;
  }
  function gambarJam(d) {
    const J = P.susunJam(d);
    return h`<div data-k="jam" style="display: flex; flex-direction: column; gap: 10px;">
      <div class="jd" data-k="jd">${J.angka.map((a) => h`<span class="jd-angka ${a.kini ? 'kini' : ''}" style="left: ${a.kiri}%; top: ${a.atas}%;">${a.t}</span>`)}<div class="jd-jarum" style="transform: rotate(${J.sudut}deg);"></div><div class="jd-pusat"></div>
        ${J.orang.map((o) => h`<div class="jd-orang f${o.warna} ${o.dekat ? 'dekat' : ''} ${o.diharap ? 'harap' : ''}" data-k="jo-${o.kunci}" style="left: ${o.kiri}%; top: ${o.atas}%;" data-aksi="bukaKartu" data-kunci="${o.kunci}">${P.inisial(o.nama)}</div>`)}</div>
      <div class="ket">Tiap orang duduk di jam biasanya ia datang (06–17). Jarum merah = sekarang. Bertepi emas = jamnya dekat dan belum datang hari ini; berpendar = memang sudah waktunya menurut selangnya.</div>
      <div class="kartu" data-k="sekitar" style="gap: 0;"><div class="label">${J.sekitarTeks}</div>${J.sekitar.length ? J.sekitar.map((o) => barisOrang(o, h`<span class="w">${o.jamTeks}</span>`)) : h`<div class="menolak" style="padding: 6px 0;">tidak ada</div>`}</div>
      <div class="ket">${J.tanpaJam} orang tidak duduk di jam ini: belum dikenali atau belum pernah tercatat jamnya.</div>
    </div>`;
  }
  function gambarMinggu(d) {
    const M = P.susunMinggu(d);
    return h`<div data-k="minggu" style="display: flex; flex-direction: column; gap: 10px;">
      <div class="pita-info">Hari ini ${M.hariNama}. Yang separuh lebih kedatangannya jatuh di hari ini: ${M.kuat.join(', ') || 'tidak ada'}.</div>
      <div class="kartu" data-k="km" style="gap: 0;"><div class="km"><span></span>${P.NAMA_HARI.map((n, i) => h`<span class="km-hd ${i === M.hariKe ? 'kini' : ''}">${n}</span>`)}</div>
        ${M.daftar.map((o) => h`<div class="km km-baris" data-k="kmb-${o.kunci}" data-aksi="bukaKartu" data-kunci="${o.kunci}"><div><div class="nm">${o.nama}</div><div class="ket" style="font-size: 9.5px;">${o.kali}</div></div>${o.sel.map((c) => h`<span class="km-sel ${c.kelas} ${c.kini ? 'kini' : ''}">${c.n || ''}</span>`)}</div>`)}</div>
      <div class="ket">Bulatan penuh = separuh lebih kedatangannya jatuh di hari itu. Angkanya = berapa kali. ${M.kurang} orang belum tiga kali datang — belum dibaca harinya.</div>
    </div>`;
  }
  function gambarBenang(s, d) {
    const N = P.susunBenang(d, s.benangSiapa); const t = s.titip; const nm = (k) => { const o = N.semua.find((x) => x.kunci === k); return o ? o.nama : k; };
    return h`<div data-k="benang" style="display: flex; flex-direction: column; gap: 10px;">
      <div class="bm" data-k="bm"><span class="bm-sisi" style="left: 8px;">yang datang</span><span class="bm-sisi" style="right: 8px;">yang punya urusan</span>
        ${N.tali.map((x, i) => h`<div class="bm-tali ${x.redup ? 'redup' : ''}" data-k="tl-${i}" style="left: ${x.kiri}%; top: ${x.atas}%; width: ${x.panjang}%; transform: rotate(${x.sudut}deg);"></div>`)}${N.tali.map((x, i) => h`<span class="bm-kali" data-k="tk-${i}" style="left: ${x.tkiri}%; top: ${x.tatas}%;">${x.kali}</span>`)}
        ${N.pin.map((o) => h`<div class="bm-pin ${o.aktif ? 'aktif' : ''}" data-k="bp-${o.kunci}" style="left: ${o.kiri}%; top: ${o.atas}%;" data-aksi="benangSiapa" data-kunci="${o.kunci}"><div class="ft f${o.warna}">${P.inisial(o.nama)}</div><div class="nm">${o.pendek}</div></div>`)}</div>
      ${!N.pin.length ? h`<div class="pita-info">Papannya masih kosong — belum ada catatan orang yang datang untuk orang lain.</div>` : ''}${N.sembunyi ? h`<div class="ket">Papan memuat 5 orang per sisi (yang paling sering didahulukan). ${N.sembunyi} benang lain tetap ada di daftar bawah.</div>` : ''}
      ${t ? h`<div class="kartu" data-k="titip-form" style="gap: 8px;"><div class="kepala-lembar"><div class="label">Yang datang bukan orangnya</div><div class="kaca-btn" data-aksi="titipTutup">tutup</div></div>
        ${(() => { const q = P.plPolos(s.titipCari) || String(s.titipCari || '').trim().toLowerCase(); const saring = (daftar) => { const cocok = q ? daftar.filter((o) => P.plPolos(o.nama).indexOf(q) >= 0 || o.nama.toLowerCase().indexOf(q) >= 0) : daftar; return { tampil: cocok.slice(0, 60), sisa: Math.max(0, cocok.length - 60), n: cocok.length }; };
          const D1 = saring(N.semua.filter((o) => o.kunci !== t.untuk && (!t.dari || o.kunci === t.dari))); const D2 = t.dari ? saring(N.semua.filter((o) => o.kunci !== t.dari && (!t.untuk || o.kunci === t.untuk))) : null;
          return h`<input class="ketik-nama" id="plTitipCari" type="text" placeholder="cari nama… (${N.semua.length} orang di buku)" value="${s.titipCari}" data-ketik="titipCari">
        <div class="ket">Siapa yang datang${t.dari ? ': ' + nm(t.dari) + ' (ketuk lagi untuk mengganti)' : ' · ' + D1.n + ' nama'}</div><div class="jalur bungkus">${D1.tampil.map((o) => h`<div class="seg ${t.dari === o.kunci ? 'aktif' : ''}" data-aksi="titipPilih" data-kolom="dari" data-kunci="${o.kunci}">${o.nama}</div>`)}${D1.sisa ? h`<div class="ket">+${D1.sisa} lagi — ketik namanya di kotak cari</div>` : ''}</div>
        ${D2 ? h`<div class="ket">Ia datang untuk siapa${t.untuk ? ': ' + nm(t.untuk) + ' (ketuk lagi untuk mengganti)' : ' · ' + D2.n + ' nama'}</div><div class="jalur bungkus">${D2.tampil.map((o) => h`<div class="seg ${t.untuk === o.kunci ? 'aktif' : ''}" data-aksi="titipPilih" data-kolom="untuk" data-kunci="${o.kunci}">${o.nama}</div>`)}${D2.sisa ? h`<div class="ket">+${D2.sisa} lagi — ketik namanya di kotak cari</div>` : ''}</div>` : ''}`; })()}
        ${t.untuk ? h`<div class="ket">Urusannya apa</div><div class="jalur bungkus">${N.jenis.map((j) => h`<div class="seg ${t.apa === j ? 'aktif' : ''}" data-aksi="titipPilih" data-kolom="apa" data-kunci="${j}">${j}</div>`)}</div>` : ''}
        <div class="ket">${t.dari && t.untuk ? nm(t.dari) + ' yang datang, tapi urusannya milik ' + nm(t.untuk) + '. Nota, bon, dan pembayarannya tetap dicatat atas nama ' + nm(t.untuk) + '.' : 'Ini BUKAN menyatukan nama: dua-duanya tetap orang yang berbeda. Yang dicatat cuma siapa biasa datang untuk siapa.'}</div>
        <div class="kaca-btn aktif emas" data-aksi="titipSimpan">CATAT</div></div>` : h`<div class="kaca-btn putus" data-aksi="titipBuka">＋ Yang datang bukan orangnya</div>`}
      <div class="kartu" data-k="benang-daftar" style="gap: 0;"><div class="label">${N.judul}</div>${N.baris.length ? N.baris.map((b) => h`<div class="jawab" data-k="bb-${b.id}" style="cursor: default;"><span class="kiri"><div><span class="nm">${b.teks}</span><span class="w">${b.ket}</span></div></span><span style="display: flex; gap: 6px; align-items: center;"><div class="kaca-btn aktif kecil" data-aksi="titipLagi" data-id="${b.id}">datang lagi</div><span class="ket tautan" data-aksi="titipBuang" data-id="${b.id}">buang</span></span></div>`) : h`<div class="menolak" style="padding: 6px 0;">tidak ada</div>`}</div>
      <div class="ket">Benang ditarik dari yang DATANG ke yang PUNYA urusan (ujung panah). Angkanya = sudah berapa kali. Ini bukan menyatukan nama: nota, bon, dan pembayaran tetap atas nama yang punya urusan.</div>
    </div>`;
  }
  function gambarHafal(s, d) {
    const H = P.susunHafalan(d, s.kuis); const q = s.kuis;
    return h`<div data-k="hafal" style="display: flex; flex-direction: column; gap: 10px;">
      ${H.kosong ? h`<div class="pita-info">Belum ada yang bisa dijadikan kartu hafalan — belum ada orang yang punya ciri.</div>` : ''}
      ${H.kartu ? h`<div class="ket">Kartu ${q.no + 1} dari ${H.dek}${q.hanya ? ' · mengulang yang salah' : ''} · betul ${q.benar}</div>
        <div class="kh-kartu" data-k="kh-${H.kartu.kunci}"><div class="atas">Kartu hafalan · siapa dia?</div><div class="kh-isi">${sk(H.kartu, 'besar')}<div><div class="tl">${H.kartu.tulisan}</div><div class="br">${H.kartu.ciriTeks}</div><div class="br">${H.kartu.jamBiasa}</div><div class="br">${H.kartu.beliBiasa}</div></div></div></div>
        ${H.pilihan.map((p) => h`<div class="kh-pilih ${H.sudah ? (p.benar ? 'benar' : p.dipilih ? 'salah' : 'redup') : ''}" data-k="kp-${p.kunci}" data-aksi="kuisPilih" data-kunci="${p.kunci}">${p.nama}</div>`)}
        ${H.sudah ? h`<div class="pita-info ${/^Bukan/.test(H.hasil) ? 'awas' : 'emas'}">${H.hasil}</div>` : ''}
        <div class="kaca-btn ${H.sudah ? 'aktif emas' : 'mati'}" data-aksi="kuisLanjut">${q.no + 1 >= H.dek ? 'LIHAT HASILNYA' : 'KARTU BERIKUTNYA'}</div>` : ''}
      ${H.selesai ? h`<div class="kartu" data-k="skor" style="gap: 8px;"><div class="kh-skor">Hafal ${q.benar} dari ${q.benar + q.salah.length}${q.hanya ? ' (putaran ulang — nilai yang disimpan tetap dari putaran penuh)' : ''}</div>
        ${H.salah.length ? h`<div class="label">Yang masih tertukar — ketuk untuk melihat kartunya</div>${H.salah.map((o) => barisOrang(o))}<div class="kaca-btn aktif" data-aksi="kuisUlangSalah">Ulangi ${H.salah.length} yang salah</div>` : ''}
        <div class="kaca-btn" data-aksi="kuisMulai">Mulai lagi dari awal</div></div>` : ''}
      <div class="ket">Nilai terakhir di HP ini: ${s.hafal ? s.hafal.benar + '/' + s.hafal.dari + ' (' + tanggalPendek(s.hafal.tanggal) + ')' : 'belum ada'}. Pengecohnya sengaja diambil dari orang yang cirinya paling mirip. Latihan ini tidak mengubah kartu siapa pun. ${H.tanpaCiri} orang belum punya ciri — belum bisa dijadikan kartu hafalan.</div>
    </div>`;
  }
  // ---------- KARTU / BARU / GABUNG ----------
  function gambarKartu(s) {
    const d = s.kartu; const o = P.kartuOrang(kini(), d.kunci); if (!o) return h`<div class="menolak">Orangnya tidak ditemukan.</div>`; const pratinjau = P.sketsa(Object.assign({}, o, { cip: d.cip })); const dikenali = !!(d.cip.length || String(d.catatan).trim() || String(d.arah).trim());
    return h`<section class="pl-kartu" data-k="kartu-${d.kunci}">
      <div class="kepala-lembar"><div style="display: grid; grid-template-columns: 76px minmax(0, 1fr); gap: 12px; align-items: center;">${mentah(svgSketsa(pratinjau, 'besar'))}<div><div class="serif" style="font-size: 20px;">${o.nama}</div><div class="ket">${o.ringkas}</div><div class="ket">${o.datang}</div>${o.polaTeks ? h`<div class="ket">biasa beli: ${o.polaTeks}</div>` : ''}</div></div><div class="kaca-btn" data-aksi="kTutup">tutup</div></div>
      <div class="kartu" style="gap: 8px;"><input class="ketik-nama" id="kNama" type="text" placeholder="Nama panggilan" value="${d.nama}" data-ketik="kKetik" data-kolom="nama">
        ${P.TANYA_CIRI.concat([['lain', 'Ciri lain']]).map(([g, judul]) => { const cip = o.ciriDaftar.filter((c) => (g === 'lain' ? !P.TANYA_CIRI.some((t) => t[0] === c.grup) : c.grup === g)); return cip.length ? h`<div class="ket" style="font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;">${judul}</div><div class="jalur bungkus">${cip.map((c) => h`<div class="seg ${d.cip.indexOf(c.nama) >= 0 ? 'aktif' : ''}" data-aksi="kCip" data-nama="${c.nama}">${c.nama}</div>`)}</div>` : ''; })}
        ${o.arahDaftar.length ? h`<div class="ket" style="font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;">Datang dari arah</div><div class="jalur bungkus">${o.arahDaftar.map((a) => h`<div class="seg ${d.arah === a ? 'aktif' : ''}" data-aksi="kArah" data-nama="${a}">${a}</div>`)}</div>` : ''}
        <input class="ketik-nama" id="kBiasa" type="text" placeholder="Yang biasa dibeli, mis. Angsa 50 kg tiap sore" value="${d.biasa}" data-ketik="kKetik" data-kolom="biasa">
        ${o.benang && o.benang.ada ? h`<div class="pita-info" data-k="kartu-benang"><b>Benang:</b> ${o.benang.untuk.map((x) => x.teks).concat(o.benang.dari.map((x) => x.teks)).join(' · ')} — nota & bon tetap atas nama yang punya urusan.</div>` : ''}
        <input class="ketik-nama" id="kCatatan" type="text" placeholder="Catatan bebas, mis. ojek, suka nitip uang" value="${d.catatan}" data-ketik="kKetik" data-kolom="catatan">
        <div class="ket catatan-larang" data-k="catatan-larang">Jangan tulis suku, agama, warna kulit, atau kesehatan.</div>
        <div class="ps-form dua"><input class="ketik-nama" id="kAsli" type="text" placeholder="Nama asli" value="${d.asli}" data-ketik="kKetik" data-kolom="asli"><input class="ketik-nama" id="kKontak" type="text" inputmode="tel" placeholder="Nomor WhatsApp" value="${d.kontak}" data-ketik="kKetik" data-kolom="kontak"></div>
        <div class="pita-info ${dikenali ? '' : 'awas'}">${dikenali ? 'Dikenali → kasir BOLEH mencatat bon baru atas namanya.' : 'Belum dikenali → kasir MENOLAK bon baru (aturan KR1). Isi salah satu: ciri, catatan, atau arah datangnya.'}</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="keBon" data-kunci="${d.kunci}">${o.utang > 0 ? 'buku bonnya · ' + RP(o.utang) : 'buku bon'}</div><div class="kaca-btn aktif emas" data-aksi="kSimpan">SIMPAN KARTU</div></div>
        ${(() => { const RH = P.rincianHapusNama(kini(), d.kunci); return h`<div class="ket tautan ${s.yakinHapusNama ? 'awas-teks' : ''}" data-aksi="kHapusNama" data-k="hapus-nama" style="align-self: flex-start;">${s.yakinHapusNama ? 'YAKIN — hapus nama "' + o.nama + '" (' + RH.arti + ')' : RH.tolak ? 'nama ini tidak bisa dihapus: ' + RH.tolak : 'nama salah ketik? hapus nama ini (' + o.nota + ' nota jadi tanpa nama, rupiah tetap)'}</div>`; })()}</div>
    </section>`;
  }
  function gambarBaru(s) {
    const nb = s.baru.nama; const mirip = P.orangMirip(kini(), nb);
    return h`<section data-k="baru"><div class="kepala-lembar"><div class="serif" style="font-size: 20px;">Orang baru</div><div class="kaca-btn" data-aksi="kTutup">tutup</div></div>
      <div class="kartu" style="gap: 8px;"><input class="ketik-nama" id="baruNama" type="text" placeholder="Nama panggilannya" value="${nb}" data-ketik="baruKetik">
        ${mirip.length ? h`<div class="pita-info">Sudah ada yang mirip — mungkin orangnya ini:</div>${mirip.map((o) => h`<div class="jawab" data-k="mr-${o.kunci}" data-aksi="bukaKartu" data-kunci="${o.kunci}"><span class="kiri"><div><span class="nm">${o.nama}</span><span class="w">${o.sub}</span></div></span><span class="ket">buka ›</span></div>`)}` : ''}
        <div class="kaca-btn ${String(nb).trim().length >= 2 ? 'aktif emas' : 'mati'}" data-aksi="baruSimpan">${mirip.length ? 'TETAP TAMBAH "' + nb + '" — orangnya lain' : 'TAMBAH' + (String(nb).trim() ? ' "' + nb + '"' : '')}</div></div>
    </section>`;
  }
  function gambarGabung(s) {
    const g = s.gabung; const [a, b] = g.k.split('+'); const lain = g.pakai === a ? b : a; const r = P.rincianGabung(kini(), g.pakai, lain); if (r.tolak) return h`<div class="pita-info awas" data-aksi="gabungTutup">${r.tolak}</div>`;
    const pil = (o) => h`<div class="jawab ${g.pakai === o.kunci ? 'dipilih' : ''}" data-k="gp-${o.kunci}" data-aksi="gabungPakai" data-kunci="${o.kunci}"><span class="kiri">${sk(o)}<div><span class="nm">${o.nama}</span><span class="w">${o.kunjungan} kali datang · belanja ${RP(o.total)}${o.utang > 0 ? ' · bon ' + RP(o.utang) : ''}${o.dikenali ? ' · ada cirinya' : ' · tanpa ciri'}</span></div></span><span class="ket">${g.pakai === o.kunci ? 'dipakai' : ''}</span></div>`;
    return h`<section data-k="gabung"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Orang yang sama?</div><div class="ket">Pilih nama yang dipakai seterusnya.</div></div><div class="kaca-btn" data-aksi="gabungTutup">tutup</div></div>
      <div class="kartu" style="gap: 6px;">${pil(r.pakai)}${pil(r.lain)}<div class="ket">${r.arti}</div>
        <div class="kaca-btn ${r.bisa ? 'aktif emas' : 'mati'}" data-aksi="gabungkan">SATUKAN</div><div class="kaca-btn putus" data-aksi="bukanKembar">Bukan — mereka dua orang yang berbeda</div></div>
    </section>`;
  }
  // ---------- BON ----------
  function gambarBon(s, d) {
    const Bn = B.susunBon(d, s.bukuKunci, s.ember); const O = s.orangBon ? B.lembarBon(d, s.orangBon) : null;
    const kartuBon = (b) => h`<div class="bp-kartu ${b.status === 'janjiLewat' ? 'lewat' : b.status === 'macet' ? 'macet' : ''}" data-k="bk-${b.kunci}" data-aksi="bukaOrangBon" data-kunci="${b.kunci}"><div><div class="nm" style="font-weight: 600;">${b.nama}</div><div class="ket ${b.status === 'janjiLewat' ? 'awas-teks' : ''}">${b.ket}</div><div class="ket">${b.nBon} · ${b.cap}</div></div><div class="n" ${mentah('data-gulir="' + Math.round(b.sisa) + '"')}>${RP(b.sisa)}</div><div class="batang"><i class="${b.status === 'macet' ? 'tua' : ''}" style="width: ${b.lebar}%;"></i></div></div>`;
    return h`<section class="pl-bon" data-k="bon">
      <div class="hero" data-k="hero"><div><div class="ket">Bon pelanggan · sisa semuanya</div><div class="besar" ${mentah('data-gulir="' + Math.round(Bn.total) + '"')}>${RP(Bn.total)}</div></div><div class="ket" style="text-align: right;">${Bn.berutang} orang masih punya bon<br>tagih sesudah ${Bn.atur.tagihHari} hari · macet sesudah ${Bn.atur.macetHari} hari</div></div>
      <div class="jalur" data-k="tabB">${TAB_B.map(([id, nm]) => h`<div class="seg ${s.tabB === id ? 'aktif' : ''}" data-aksi="tabB" data-t="${id}">${nm}</div>`)}</div>
      ${O ? gambarLembarBon(s, d, O) : ''}
      ${s.tabB === 'buku' ? h`<div data-k="buku" style="display: flex; flex-direction: column; gap: 10px;">${Bn.namaBuku.length ? h`<div class="jalur bungkus">${Bn.namaBuku.map((n) => h`<div class="seg ${n.aktif ? 'aktif' : ''}" data-aksi="bukaBuku" data-kunci="${n.kunci}">${n.nama}</div>`)}</div>` : ''}
        ${Bn.buku ? h`<div class="bp-buku" data-k="bb-${Bn.buku.kunci}"><div style="display: flex; justify-content: space-between; align-items: baseline;"><span class="judul">${Bn.buku.nama}</span><span class="sisa">${RP(Bn.buku.sisa)}</span></div><div class="ket" style="color: #6b6555; line-height: 26px;">${Bn.buku.ket}</div>
          ${Bn.buku.halaman.map((r, i) => h`<div class="bar ${r.jenis}" data-k="hb-${i}"><span>${r.tgl}</span><span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${r.teks}</span><span>${r.n < 0 ? '−' : ''}${RP(Math.abs(r.n)).replace('Rp', '')}</span></div>`)}
          <div class="tombol-baris" style="margin-top: 8px;"><div class="kaca-btn aktif" data-aksi="bukaOrangBon" data-kunci="${Bn.buku.kunci}">tagih · bayar · hapus</div></div></div>` : h`<div class="menolak">Tidak ada bon yang terbuka.</div>`}</div>` : ''}
      ${s.tabB === 'papan' ? h`<div data-k="papan" style="display: flex; flex-direction: column; gap: 8px;">${Bn.papan.map((p, i) => (p.lajur ? h`<div class="bp-lajur ${p.awas ? 'awas' : ''}" data-k="lj-${i}"><span class="judul">${p.judul} · ${p.n}</span><span class="n">${RP(p.jumlah)}</span></div>` : kartuBon(p)))}</div>` : ''}
      ${s.tabB === 'umur' ? h`<div data-k="umur" style="display: flex; flex-direction: column; gap: 10px;"><div class="ember" data-k="ember">${Bn.ember.map((e) => h`<div class="${e.aktif ? 'aktif' : ''} ${e.tua ? 'tua' : ''}" data-aksi="emberPilih" data-id="${e.id}"><b>${RP(e.jumlah).replace('Rp', '')}</b><span>${e.label} · ${e.n}</span></div>`)}</div><div class="ket">${Bn.umurTeks}</div>${Bn.perUmur.map(kartuBon)}</div>` : ''}
      ${bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : h`<div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">Atur: waktunya ditagih, macet, alasan hapus, salam tagihan</div></div>`}
    </section>`;
  }
  function gambarLembarBon(s, d, O) {
    const p = s.lembarBon === 'tagih' ? B.pesanTagih(d, O.kunci) : null; const by = s.bayar; const hp = s.hapusIsi;
    return h`<div class="kartu rincian-wadah" data-k="lembar-bon-${O.kunci}" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${O.nama}</div><div class="ket">${O.sisa > 0 ? RP(O.sisa) + ' · ' + O.ket : 'tidak ada bon yang terbuka'}${O.dikenali ? '' : ' · belum dikenali (kasir menolak bon baru)'}</div></div><div class="kaca-btn" data-aksi="bonTutup">tutup</div></div>
      ${O.rinci.map((r, i) => h`<div class="jawab" data-k="rb-${i}" style="cursor: default;"><span class="kiri"><div><span class="nm">${r.teks}</span><span class="w">${r.tgl}</span></div></span><span class="n">${RP(r.n)}</span></div>`)}
      ${O.sisa > 0 ? h`<div class="tombol-baris"><div class="kaca-btn ${s.lembarBon === 'tagih' ? 'aktif' : ''}" data-aksi="lembarBon" data-l="tagih">Tagih lewat WhatsApp</div><div class="kaca-btn ${s.lembarBon === 'bayar' ? 'aktif emas' : 'aktif'}" data-aksi="lembarBon" data-l="bayar">Catat pembayaran</div><div class="kaca-btn ${s.lembarBon === 'hapus' ? 'awas' : 'putus'}" data-aksi="lembarBon" data-l="hapus">Hapus dari buku</div></div>` : ''}
      ${p ? h`<div data-k="tagih" style="display: flex; flex-direction: column; gap: 8px;"><div class="wa-pesan">${p.teks}</div><div class="ket">${p.tujuan} Janji bayar dicatat supaya besok layar tahu janji siapa yang lewat.</div>
        <div class="jalur bungkus">${p.janjiPilihan.map((j) => h`<div class="seg ${s.janji === j.hari ? 'aktif' : ''}" data-aksi="janjiPilih" data-hari="${j.hari}">${j.nama}</div>`)}</div><div class="kaca-btn aktif emas" data-aksi="kirimTagih">BUKA WHATSAPP & CATAT TAGIHAN</div></div>` : ''}
      ${s.lembarBon === 'bayar' ? h`<div data-k="bayar" style="display: flex; flex-direction: column; gap: 8px;"><div class="ps-form dua"><div><div class="ket">Jumlah dibayar (Rp)</div><input class="ketik-nama" id="byNominal" type="text" inputmode="numeric" placeholder="0" value="${by.nominal}" data-ketik="bayarKetik" data-kolom="nominal"></div><div><div class="ket">&nbsp;</div><div class="kaca-btn" data-aksi="bayarSemua">semua · ${RP(O.sisa)}</div></div></div>
        <div class="jalur"><div class="seg ${by.cara !== 'QRIS' ? 'aktif' : ''}" data-aksi="bayarCara" data-cara="Tunai">Tunai → laci</div><div class="seg ${by.cara === 'QRIS' ? 'aktif' : ''}" data-aksi="bayarCara" data-cara="QRIS">QRIS → rekening</div></div>
        <div class="ps-form dua"><input class="ketik-nama" id="byCatatan" type="text" placeholder="catatan (boleh kosong)" value="${by.catatan}" data-ketik="bayarKetik" data-kolom="catatan"><input class="ketik-nama" id="byPengantar" type="text" placeholder="dibawa siapa? (kalau bukan dia)" value="${by.pengantar}" data-ketik="bayarKetik" data-kolom="pengantar"></div>
        <div class="ket">${(Number(String(by.nominal).replace(/\./g, '')) || 0) >= O.sisa && O.sisa > 0 ? O.nama + ' akan LUNAS' : 'Sisa bon sesudahnya ' + RP(Math.max(0, O.sisa - (Number(String(by.nominal).replace(/\./g, '')) || 0))) + ' — belum lunas'} · ${by.cara === 'QRIS' ? 'rekening' : 'laci'} bertambah, laba TIDAK berubah (sudah dihitung waktu berasnya dijual).</div>
        <div class="kaca-btn aktif emas" data-aksi="bayarSimpan">CATAT PEMBAYARAN</div></div>` : ''}
      ${s.lembarBon === 'hapus' ? h`<div data-k="hapus" style="display: flex; flex-direction: column; gap: 8px;"><div class="ps-form dua"><div><div class="ket">Jumlah dihapus (Rp)</div><input class="ketik-nama" id="hpNominal" type="text" inputmode="numeric" value="${hp.nominal}" data-ketik="hapusKetik" data-kolom="nominal"></div><div><div class="ket">Alasan (wajib)</div><input class="ketik-nama" id="hpAlasan" type="text" placeholder="mis. pindah rumah" value="${hp.alasan}" data-ketik="hapusKetik" data-kolom="alasan"></div></div>
        <div class="jalur bungkus">${O.alasanPilihan.map((a) => h`<div class="seg ${hp.alasan === a ? 'aktif' : ''}" data-aksi="hapusAlasan" data-nama="${a}">${a}</div>`)}</div>
        <div class="ket awas-teks">BUKAN uang masuk — uang toko tidak berubah. Dicatat sebagai KERUGIAN bulan ini: laba berkurang segitu. Tidak bisa dibatalkan.</div>
        <div class="kaca-btn ${s.yakinHapus ? 'awas' : 'putus'}" data-aksi="hapusSimpan">${s.yakinHapus ? 'KETUK SEKALI LAGI · hapus dari buku' : 'HAPUS DARI BUKU'}</div></div>` : ''}
      ${O.riwayat.length ? h`<div class="label">Riwayat</div>${O.riwayat.slice(0, 8).map((r, i) => h`<div class="ket" data-k="rw-${i}">${r.tgl} · ${r.teks}${r.n !== null ? ' · ' + RP(r.n) : ''}</div>`)}` : ''}
    </div>`;
  }
  // ---------- THR ----------
  function gambarThr(s, d) {
    const T = P.susunThr(d, s.tahun); const U = P.usulThr(d, s.tahun, s.usulBentuk); const O = s.thrOrang ? T.daftar.find((x) => x.kunci === s.thrOrang) : null; const b = s.beri;
    const baris = (x) => h`<div class="jawab ${s.thrOrang === x.kunci ? 'dipilih' : ''}" data-k="th-${x.kunci}" data-aksi="thrBuka" data-kunci="${x.kunci}"><span class="kiri"><span class="n" style="color: var(--redup); font-size: 15px; min-width: 22px; text-align: center;">${x.no}</span><div><span class="nm">${x.nama}</span><span class="w">${x.belanjaTeks}</span><span class="w">${x.laluTeks}</span></div></span><span style="text-align: right;">${x.ada ? h`<span class="nm" style="font-size: 12px;">${x.status}</span><span class="w">${x.nilai ? '±' + RP(x.nilai) : ''}</span>` : h`<span class="kaca-btn kecil">beri</span>`}</span></div>`;
    const meter = h`<div class="kartu" data-k="meter" style="gap: 4px;"><div style="display: flex; justify-content: space-between; align-items: baseline; gap: 8px;"><span class="serif" style="font-size: 20px;" ${mentah('data-gulir="' + Math.round(T.terpakai) + '"')}>${RP(T.terpakai)}</span><span class="ket">dari anggaran ${RP(T.anggaran)}</span></div><div class="th-meter ${T.sisa < 0 ? 'lebih' : ''}"><i style="width: ${T.meterIsi}%;"></i><u style="width: ${T.meterRencana}%;"></u></div><div style="display: flex; justify-content: space-between; gap: 8px;"><span class="ket">emas = sudah diserahkan · pudar = rencana</span><span class="ket ${T.sisa < 0 ? 'awas-teks' : ''}">${T.sisa >= 0 ? 'sisa ' + RP(T.sisa) : 'LEWAT anggaran ' + RP(-T.sisa)}</span></div></div>`;
    return h`<section class="pl-thr" data-k="thr">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;"><span class="ket">${T.ringkas}</span><span class="step"><div class="kaca-btn" data-aksi="tahunGeser" data-arah="-1">−</div><span class="serif" style="min-width: 88px; text-align: center;">THR ${T.tahun}</span><div class="kaca-btn" data-aksi="tahunGeser" data-arah="1">+</div></span></div>
      <div class="jalur" data-k="tabT">${TAB_T.map(([id, nm]) => h`<div class="seg ${s.tabT === id ? 'aktif' : ''}" data-aksi="tabT" data-t="${id}">${nm}</div>`)}</div>
      ${O ? h`<div class="kartu rincian-wadah" data-k="beri-${O.kunci}" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${O.nama}</div><div class="ket">${O.belanjaTeks} · ${O.laluTeks}</div></div><div class="kaca-btn" data-aksi="thrTutup">tutup</div></div>
        ${O.ada ? h`<div class="ket">THR ${T.tahun}: ${O.bentuk}${O.nilai ? ' · ±' + RP(O.nilai) : ''} · ${O.serah ? 'SUDAH diserahkan' : 'baru direncanakan'}</div><div class="tombol-baris"><div class="kaca-btn ${O.serah ? 'putus' : 'aktif emas'}" data-aksi="thrSerah" data-id="${O.id}">${O.serah ? 'Batalkan centang "sudah diserahkan"' : 'SUDAH DISERAHKAN'}</div><div class="kaca-btn awas" data-aksi="thrHapus" data-id="${O.id}">Hapus catatan ini (salah catat)</div></div>`
          : h`<div class="jalur bungkus">${T.bentuk.map((x) => h`<div class="seg ${b.bentuk === x.nama ? 'aktif' : ''}" data-aksi="beriBentuk" data-nama="${x.nama}" data-n="${x.n}">${x.nama} ${RP(x.n).replace('Rp', '')}</div>`)}</div>
            <div class="ps-form dua"><input class="ketik-nama" id="beriLain" type="text" placeholder="…atau ketik bentuk lain, mis. handuk" value="${b.lain}" data-ketik="beriKetik" data-kolom="lain"><input class="ketik-nama" id="beriNilai" type="text" inputmode="numeric" placeholder="perkiraan nilai (boleh kosong)" value="${b.nilai}" data-ketik="beriKetik" data-kolom="nilai"></div>
            <div class="kaca-btn ${(b.bentuk || String(b.lain).trim()) ? 'aktif emas' : 'mati'}" data-aksi="beriSimpan">RENCANAKAN ${(b.bentuk || b.lain || '').toUpperCase()} UNTUK ${O.nama.toUpperCase()}</div>`}</div>` : ''}
      ${s.tabT === 'daftar' ? h`<div data-k="daftar" style="display: flex; flex-direction: column; gap: 10px;">${meter}<div class="kartu" style="gap: 0;">${T.daftar.slice(0, 40).map(baris)}</div><div class="ket">Urutannya menurut belanja di tahun itu. "Tahun lalu" ditulis supaya tidak ada yang dapat sarung dua tahun berturut-turut tanpa lu sadari.</div></div>` : ''}
      ${s.tabT === 'meja' ? h`<div data-k="meja" style="display: flex; flex-direction: column; gap: 10px;">${meter}<div class="th-meja">${T.dapat.map((x) => h`<div class="th-kado ${x.serah ? '' : 'rencana'}" data-k="kado-${x.kunci}" data-aksi="thrBuka" data-kunci="${x.kunci}">${x.serah ? h`<span class="th-cap">diserahkan</span>` : ''}<span class="nm">${x.nama}</span><span class="bt">${x.bentuk}</span></div>`)}<div class="th-kado kosong" data-aksi="tabT" data-t="daftar">＋ bingkisan</div></div><div class="ket">Kotak bergaris putus = baru direncanakan · kotak berpita = sudah dibungkus dan diserahkan. Ketuk kotaknya untuk mencentang atau menghapus.</div></div>` : ''}
      ${s.tabT === 'amplop' ? h`<div data-k="amplop" style="display: flex; flex-direction: column; gap: 10px;"><div class="th-amplop"><div class="ket" style="font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.08em; color: #6b6555;">Amplop THR ${T.tahun}</div><div class="besar">${RP(T.terpakai)}</div><div class="k2" style="font-size: 12px;">dari anggaran ${RP(T.anggaran)} · <span class="${T.sisa < 0 ? 'awas-teks' : ''}">${T.sisa >= 0 ? 'sisa ' + RP(T.sisa) : 'LEWAT ' + RP(-T.sisa)}</span></div><div class="th-meter ${T.sisa < 0 ? 'lebih' : ''}" style="margin-top: 6px;"><i style="width: ${T.meterIsi}%;"></i><u style="width: ${T.meterRencana}%;"></u></div></div>
        <div class="kartu" style="gap: 6px;"><div class="label">Usulkan dari sisa amplop</div><div class="jalur bungkus">${T.bentuk.map((x) => h`<div class="seg ${(U.bentuk && U.bentuk.nama === x.nama) ? 'aktif' : ''}" data-aksi="usulBentuk" data-nama="${x.nama}">${x.nama} ${RP(x.n).replace('Rp', '')}</div>`)}</div><div class="ket">${U.teks}</div><div class="kaca-btn ${U.calon.length ? 'aktif emas' : 'mati'}" data-aksi="usulPakai">${U.calon.length ? 'RENCANAKAN ' + U.calon.length + ' ORANG · ' + RP(U.calon.length * (U.bentuk ? U.bentuk.n : 0)) : 'Tidak ada yang diusulkan'}</div></div>
        ${T.dapat.length ? h`<div class="kartu" style="gap: 0;">${T.dapat.map(baris)}</div>` : ''}</div>` : ''}
      <div class="pita-info" style="border-style: dashed;">Ini catatan SIAPA DAPAT APA — bukan catatan uang. Uang belanja bingkisannya dicatat di Catat Uang Keluar waktu barangnya dibeli.</div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">Atur: bentuk THR & anggaran setahun</div></div>
    </section>`;
  }
  // ---------- ATUR ----------
  /** Putaran 23b: lembar "Bersihkan ciri yang dicabut" — tampil hanya selama masih ada yang perlu dibersihkan (atau hasilnya baru saja keluar).
   *  Teks bebas yang memuat kata terlarang cuma DIDAFTAR (owner memutuskan per kartu); jejak log cuma dihitung. */
  function gambarBersihkan(s) {
    const b = s.bersih || {}; const R = P.rincianBersihkanCiri(kini()); const daftarNama = (xs) => xs.map((k) => k.nama).join(', ');
    const bebas = R.bebas.length ? h`<div class="bs-bebas" data-k="bs-bebas"><div class="ket">Teks bebas yang memuat kata terlarang — TIDAK diubah otomatis (kata "kulit" bisa berarti lain). Ketuk nama untuk membuka kartunya, putuskan sendiri:</div>
      ${R.bebas.map((x) => h`<div class="bs-baris tautan" data-aksi="bsBukaKartu" data-kunci="${x.kunci}" data-k="bs-bebas-${x.kunci}"><span>${x.nama}</span><span class="ket">${x.kolom.join(', ')}</span></div>`)}</div>` : '';
    const log = R.logKena ? h`<div class="ket" data-k="bs-log">Jejak aktivitas yang menyebut ciri itu: ${R.logKena} dari ${R.logDimuat} jejak terakhir yang dimuat. Jejak tidak diubah.</div>` : '';
    if (b.hasil) return h`<div class="kartu bs-lembar" data-k="bersihkan" style="gap: 6px;"><div class="label">Bersihkan ciri yang dicabut · selesai</div>
      <div class="pita-info ${b.hasil.gagal ? 'awas' : ''}">${b.hasil.kartu} kartu · ${b.hasil.cip} cip dibuang${b.hasil.atur ? ' · setelan cip ikut dibersihkan' : ''}. Langkah berikutnya: unduh cadangan BARU, lalu hapus berkas cadangan lama yang masih memuat ciri itu.</div>
      ${b.hasil.baris.map((t, i) => h`<div class="ket" data-k="bs-hasil-${i}">${t}</div>`)}${bebas}${log}</div>`;
    if (!R.ada) return R.bebas.length || R.logKena ? h`<div class="kartu bs-lembar tenang" data-k="bersihkan" style="gap: 6px;"><div class="label">Ciri yang dicabut · periksa sendiri</div><div class="ket">Kartu & setelan sudah bersih dari cip warna kulit dan suku/logat.</div>${bebas}${log}</div>` : '';
    const tombol = !R.cadangan ? h`<div class="kaca-btn mati" data-k="bs-tombol">Unduh cadangan dulu dari Sistem › Cadangan.</div>`
      : h`<div class="kaca-btn ${b.yakin ? 'awas' : 'aktif emas'}" data-aksi="bsBersihkan" data-k="bs-tombol">${b.menulis ? 'membersihkan…' : b.yakin ? 'KETUK SEKALI LAGI — BERSIHKAN (tidak bisa diurungkan)' : 'BERSIHKAN'}</div>`;
    return h`<div class="kartu bs-lembar" data-k="bersihkan" style="gap: 6px;"><div class="label">Bersihkan ciri yang dicabut</div>
      <div class="ket">Toko tidak lagi mencatat suku, ras, atau warna kulit pelanggan. Cip itu masih tersimpan di kartu lama — di bawah ini pratinjaunya; belum ada yang ditulis.</div>
      <div class="bs-angka"><div><div class="ket">Kartu yang memuat cip itu</div><div class="besar">${R.kartu.length}</div></div><div><div class="ket">Cip yang dibuang</div><div class="besar">${R.cip}</div></div><div><div class="ket">Sesudahnya tanpa cip sama sekali</div><div class="besar">${R.tanpaCip.length}</div></div></div>
      ${R.tanpaCip.length ? h`<div class="ket">Tanpa cip sesudahnya: ${daftarNama(R.tanpaCip)}.${R.belumDikenal.length ? ' Yang juga tanpa catatan & arah — di kasir sistem lama jadi "belum dikenal" (bon barunya ditolak) sampai kartunya diisi lagi: ' + daftarNama(R.belumDikenal) + '.' : ' Semuanya masih punya catatan atau arah, jadi tetap dikenal di kasir sistem lama.'}</div>` : ''}
      <div class="ket">Setelan cip owner: ${R.atur ? 'ikut dibersihkan (' + R.aturBuang + ' cip)' : 'tidak berubah'}. ${R.batch > 1 ? 'Ditulis dalam ' + R.batch + ' batch.' : ''} Kolom lain di kartu tidak disentuh.</div>
      <div class="tombol-baris">${tombol}</div>${bebas}${log}</div>`;
  }
  function gambarAtur(s) {
    const a = s.atur; const daftar = (k, judul, ket, tambah) => h`<div class="kartu" data-k="atur-${k}" style="gap: 6px;"><div class="label">${judul}</div><div class="ket">${ket}</div>
      ${a[k].map((x, i) => h`<div style="display: grid; grid-template-columns: minmax(0, 1fr) ${k === 'ciriDaftar' || k === 'bentukThr' ? 'auto' : ''} auto; gap: 6px; align-items: center;" data-k="${k}-${i}">
        <input class="ketik-nama" type="text" value="${typeof x === 'string' ? x : x.nama}" data-ketik="aturKetik" data-kolom="${k}" data-i="${i}" ${typeof x === 'string' ? '' : mentah('data-sub="nama"')}>
        ${k === 'ciriDaftar' ? h`<div class="jalur rapat">${P.TANYA_CIRI.concat([['lain', 'lain']]).map(([g, nm]) => h`<div class="seg ${x.grup === g ? 'aktif' : ''}" style="font-size: 10px; min-height: 30px; padding: 0 6px;" data-aksi="aturGrup" data-i="${i}" data-grup="${g}">${g === 'lain' ? 'lain' : nm.split(' ').slice(-1)[0]}</div>`)}</div>` : k === 'bentukThr' ? h`<input class="ketik-nama" type="text" inputmode="numeric" style="width: 96px;" value="${x.n}" data-ketik="aturKetik" data-kolom="${k}" data-i="${i}" data-sub="n">` : ''}
        <span class="ket tautan" data-aksi="aturLepas" data-daftar="${k}" data-i="${i}">lepas</span></div>`)}
      <div class="kaca-btn putus" data-aksi="aturTambah" data-daftar="${k}">${tambah}</div></div>`;
    return h`<section data-k="atur"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Atur pelanggan · angka & daftar milik owner</div><div class="ket">Semua yang di sini boleh lu ubah sendiri; layar membacanya saat itu juga.</div></div><div class="kaca-btn" data-aksi="bukaAtur">batal</div></div>
      ${gambarBersihkan(s)}
      <div class="kartu" style="gap: 8px;"><div class="ps-form dua">
        <div><div class="ket">Bangku kosong sesudah (× selangnya sendiri)</div><input class="ketik-nama" type="text" inputmode="decimal" value="${a.kosongKali}" data-ketik="aturKetik" data-kolom="kosongKali"></div>
        <div><div class="ket">Nota sebesar ini ke atas perlu nama (Rp)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${a.notaBesar}" data-ketik="aturKetik" data-kolom="notaBesar"></div>
        <div><div class="ket">Waktunya ditagih sesudah (hari)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${a.tagihHari}" data-ketik="aturKetik" data-kolom="tagihHari"></div>
        <div><div class="ket">Disebut macet sesudah (hari, tanpa pembayaran)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${a.macetHari}" data-ketik="aturKetik" data-kolom="macetHari"></div>
        <div><div class="ket">Anggaran THR setahun (Rp)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${a.anggaranThr}" data-ketik="aturKetik" data-kolom="anggaranThr"></div>
        <div><div class="ket">Salam penutup tagihan WhatsApp</div><input class="ketik-nama" type="text" value="${a.salamTagih}" data-ketik="aturKetik" data-kolom="salamTagih"></div></div></div>
      ${daftar('ciriDaftar', 'Cip ciri yang bisa diketuk', 'Di kartu dan di tebakan. Yang masih dipakai kartu orang tidak bisa dihapus atau diganti namanya.', '+ ciri')}
      ${daftar('arahDaftar', 'Arah datangnya', 'Pakai sebutan yang memang dipakai di toko, mis. gang masjid.', '+ arah')}
      ${daftar('titipDaftar', 'Urusan titipan', 'Pilihan "untuk apa" waktu yang datang bukan orangnya.', '+ urusan')}
      ${daftar('alasanHapus', 'Alasan hapus bon', 'Pilihan cepat di lembar hapus bon. Alasan tetap bisa diketik sendiri.', '+ alasan')}
      ${daftar('bentukThr', 'Bentuk THR & perkiraan harganya', 'Dipakai di lembar beri THR dan di usulan amplop.', '+ bentuk')}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN ATURAN</div></div>
    </section>`;
  }

  K.dengar(gambar);
  dengarkan(() => gambar());
  // dipanggil layar Menu: buka keluarga (kenali | bon | thr), dan kalau ada, kartu / bon satu orang — lewat penangan yang sama dengan ketukan
  const buka = (keluarga, orang) => { AKSI.keluarga({ ke: keluarga || 'kenali' }); if (orang && keluarga === 'bon') AKSI.bukaOrangBon({ kunci: orang }); else if (orang) AKSI.bukaKartu({ kunci: orang }); };
  return { keadaan: K, belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan, gambar, buka, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil) gambar(); } };
}
