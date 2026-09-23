// LAYAR HARGA & PEMASOK — GAMBAR & KETUKAN. Tiga keluarga dalam satu layar: KATALOG (H1: Papan · Kalimat · Dampak · Pasar · Belah · Label),
// BON PEMASOK (H2: Tusukan bon · Jatuh tempo · Buku bon), BELANJA (H3: Isi truk · Kapan habis · Daftar). Angka & dokumen di harga-logika.js,
// bon-pemasok-logika.js, belanja-logika.js (tanpa DOM, dijaga uji_harga_baru.py). Satu markup tiga lebar: HP = tab; Tablet = benda utama menetap + tab; Mac = kolom.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, ANGKA, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as HG from './harga-logika.js';
import * as BP from './bon-pemasok-logika.js';
import * as BL from './belanja-logika.js';
import { waktuSekarang } from './jual-logika.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, hapusDokumen } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
  truk: '<svg viewBox="0 0 358 118" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" preserveAspectRatio="none"><path d="M8 12 V78 H252 V12"/><path d="M8 78 H252" stroke-width="2.4"/><path d="M258 78 V34 H300 L338 58 V78 Z"/><path d="M268 42 H296 L318 58 H268 Z" opacity="0.55"/><path d="M4 84 H346" opacity="0.5"/><circle cx="62" cy="94" r="13"/><circle cx="62" cy="94" r="4.5"/><circle cx="108" cy="94" r="13"/><circle cx="108" cy="94" r="4.5"/><circle cx="298" cy="94" r="13"/><circle cx="298" cy="94" r="4.5"/><path d="M340 72 h8"/></svg>',
  karung: '<svg class="kr-garis" viewBox="0 0 150 200" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M22 26 Q10 12 20 5 Q28 14 40 16 H110 Q122 14 130 5 Q140 12 128 26 Q140 100 132 176 Q130 194 114 196 H36 Q20 194 18 176 Q10 100 22 26 Z"/><path d="M26 27 H124" stroke-dasharray="4 4"/><path d="M24 22 l-6 -9 M126 22 l6 -9" opacity="0.6"/></svg>',
  kaleng: '<svg class="kr-garis" viewBox="0 0 150 200" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M30 40 H120 V178 Q120 192 106 192 H44 Q30 192 30 178 Z"/><path d="M26 40 H124"/><path d="M30 58 H120 M30 170 H120" opacity="0.45"/><path d="M120 70 q22 4 18 34 q-2 14 -18 16"/></svg>',
};
const KUNCI_KELUARGA = 'miqbal_baru_harga_keluarga', KUNCI_TAB = 'miqbal_baru_harga_tab', KUNCI_DRAF_BELANJA = 'miqbal_baru_draf_belanja';
const simpanLokal = (k, v) => { try { if (v !== null && v !== undefined) localStorage.setItem(k, typeof v === 'string' ? v : JSON.stringify(v)); else localStorage.removeItem(k); } catch (e) { /* abaikan */ } };
const bacaLokal = (k, json) => { try { const v = localStorage.getItem(k); return v === null ? null : json ? JSON.parse(v) : v; } catch (e) { return null; } };
const KELUARGA = [['katalog', 'Katalog harga'], ['bon', 'Bon pemasok'], ['belanja', 'Belanja']];

export function pasangLayarHarga(akar, opsi) {
  const tabLokal = bacaLokal(KUNCI_TAB, true) || {};
  const K = buatKeadaan({ keluarga: ['katalog', 'bon', 'belanja'].indexOf(bacaLokal(KUNCI_KELUARGA)) >= 0 ? bacaLokal(KUNCI_KELUARGA) : 'katalog', kabar: '', kabarAwas: false,
    tabH: tabLokal.h || 'papan', ubah: null, ketik: '', ketikApa: 'jual', terbit: false, yakinRugi: false, kal: { arah: 'naik', merek: 'semua', satuan: 'semua', rp: 100 }, papanSisi: 'owner', wa: false, bedah: { merek: '', satuan: '', bayar: 'tunai' }, aturH: null,
    tabB: tabLokal.b || 'tusuk', bukuNama: '', bayar: null, lama: null, kartu: null, urung: null, aturB: null,
    tabL: tabLokal.l || 'truk', pesan: bacaLokal(KUNCI_DRAF_BELANJA, true) || {}, pemasokBelanja: '', wa2: null, waHarga: false, aturL: null });
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; const kini = () => opsi.sekarang() || new Date(); const waktu = () => waktuSekarang(opsi.sekarang() || undefined);
  const lebar = () => (window.matchMedia('(min-width: 1100px)').matches ? 'mac' : window.matchMedia('(min-width: 720px)').matches ? 'tablet' : 'hp');
  const ingatTab = () => simpanLokal(KUNCI_TAB, { h: st().tabH, b: st().tabB, l: st().tabL });

  async function tulis(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }
    try {
      if (r.hapus && r.hapus.length) { const x0 = await hapusDokumen(r.hapus); if (x0 && x0.gagal) { set({ kabar: 'DITOLAK: ' + x0.pesan, kabarAwas: true }); return false; } }
      let x = null; if (r.dokumen && r.dokumen.length) { x = await tulisDokumen(r.dokumen); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; } }
      set(Object.assign({}, r.patch || {}, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch || {}).kabar || ''), kabarAwas: !!(r.patch || {}).kabarAwas })); return true;
    } catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  const bukaWa = (tautan) => { try { return window.open(tautan, '_blank', 'noopener'); } catch (e) { return null; } };
  const keAtas = () => { try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); } };   // lembar digambar di atas daftar — ketukan dari bawah wajib melihat lembarnya
  const ubahPesan = (p) => { simpanLokal(KUNCI_DRAF_BELANJA, Object.keys(p).length ? p : null); set({ pesan: p }); };
  const S1 = () => HG.hgSemua(kini());

  const AKSI = {
    keluarga: ({ nama }) => { const k = nama; simpanLokal(KUNCI_KELUARGA, k); set({ keluarga: k, kabar: '', ubah: null, terbit: false, bayar: null, lama: null, kartu: null, wa: false, wa2: null }); },
    mode: () => opsi.gantiMode(), tutupKabar: () => set({ kabar: '' }), keMenu: () => opsi.pindah && opsi.pindah('menu'),
    // ---- H1 KATALOG
    tabH: ({ t }) => { set({ tabH: t, kabar: '' }); ingatTab(); },
    hgUbah: ({ kunci }) => { set({ ubah: st().ubah === kunci ? null : kunci, ketik: '', ketikApa: 'jual', kabar: '', terbit: false }); keAtas(); },
    hgTutupUbah: () => set({ ubah: null, ketik: '', ketikApa: 'jual' }),
    hgKetik: (v) => set({ ketik: String(v).slice(0, 12) }),
    hgKetikApa: ({ apa }) => set({ ketikApa: apa, ketik: '' }),
    hgIsi: ({ n }) => set({ ketik: String(n) }),
    hgSimpanUbah: async () => { const s = st(); if (!s.ubah) return; if (await tulis(HG.susunUbah(s.ubah, s.ketik, s.ketikApa, waktu()))) sekali(akar.querySelector('.hg-ubah'), 'pegas', 520); },
    hgHapusPasar: async () => { const s = st(); if (s.ubah) await tulis(HG.susunHapusPasar(s.ubah, waktu())); },
    hgBuangDraf: async ({ kunci }) => { await tulis(HG.susunBuangDraf(kunci || null, waktu())); },
    hgSengaja: async () => { const s = st(); if (s.ubah) await tulis(HG.susunSengaja(s.ubah, waktu())); },
    hgBelahIni: ({ kunci }) => { const b = HG.cariBaris(S1(), kunci); if (!b) return; set({ bedah: { merek: b.merk, satuan: b.st.id, bayar: st().bedah.bayar }, tabH: 'belah', ubah: null, ketik: '', kabar: '' }); ingatTab(); },
    hgUsulSemua: async () => { await tulis(HG.susunUsulSemua(waktu())); },
    hgPakaiUsul: async ({ kunci }) => { await tulis(HG.susunPakaiUsul(kunci, waktu())); },
    hgBukaTerbit: () => { set({ terbit: !st().terbit, yakinRugi: false, ubah: null, kabar: '' }); keAtas(); },
    hgTerbitkan: async () => { const r = HG.susunTerbit(waktu(), st().yakinRugi); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, yakinRugi: !!r.perluYakin }); if (await tulis(r)) sekali(akar.querySelector('.hg-bilah'), 'pegas', 520); },
    kalPilih: ({ kolom, v }) => set({ kal: Object.assign({}, st().kal, { [kolom]: v }), kabar: '' }),
    kalRp: ({ arah }) => { const l = HG.aturHarga().langkahRp; set({ kal: Object.assign({}, st().kal, { rp: Math.max(l, (Number(st().kal.rp) || 0) + Number(arah) * l) }) }); },
    kalKetik: (v) => set({ kal: Object.assign({}, st().kal, { rp: String(v).slice(0, 7) }) }),
    kalPakai: async () => { await tulis(HG.susunKalimatDraf(st().kal, waktu())); },
    labelSelesai: async ({ kunci }) => { await tulis(HG.susunLabelSelesai(kunci, waktu())); },
    papanSisi: ({ s }) => set({ papanSisi: s }),
    hgWa: () => { set({ wa: !st().wa, ubah: null }); keAtas(); },
    hgKirimWa: () => { const t = HG.teksWaHarga(S1(), tanggalPendek(waktu().tanggal)); const w = bukaWa(t.tautan); set({ wa: false, kabar: w ? 'WhatsApp dibuka dengan daftar harga yang sedang berlaku' : 'Peramban menahan jendela WhatsApp — ketuk lagi tombolnya', kabarAwas: !w }); },
    bdPilih: ({ kolom, v }) => set({ bedah: Object.assign({}, st().bedah, { [kolom]: v }) }),
    bukaAturH: () => { const a = HG.aturHarga(); set({ aturH: st().aturH ? null : { targetPerKg: String(a.targetPerKg), bulatLiter: String(a.bulatLiter), bulatKemasan: String(a.bulatKemasan), bulatKarung: String(a.bulatKarung), langkahRp: String(a.langkahRp), ambangDampak: String(a.ambangDampak), bongkarKg: String(a.bongkarKg), mdrPersen: String(a.mdrPersen), mdrBatas: String(a.mdrBatas) } }); },
    hgKetikAtur: (v, el) => { const a = Object.assign({}, st().aturH || {}); a[el.dataset.kolom] = String(v).slice(0, 10); set({ aturH: a }); },
    simpanAturH: async () => { const a = st().aturH; if (a) await tulis(HG.susunAturHarga(a, waktu())); },
    // ---- H2 BON PEMASOK
    tabB: ({ t }) => { set({ tabB: t, kabar: '' }); ingatTab(); },
    bukuNama: ({ nama }) => set({ bukuNama: nama }),
    bpBayarBuka: ({ pemasok, bon }) => { const B = BP.susunBon(kini()); const d = B.bon.filter((b) => b.pemasok === pemasok).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal))); const b0 = d.find((b) => b.id === String(bon)) || d[0]; if (!b0) return set({ kabar: 'Tidak ada bon terbuka untuk ' + pemasok, kabarAwas: true });
      set({ bayar: { pemasok, bonId: b0.id, ketik: String(b0.sisa), dari: '', adminI: -1, catatan: '' }, lama: null, kartu: null, kabar: '' }); keAtas(); },
    bpBayarBon: ({ bon }) => { const B = BP.susunBon(kini()); const b0 = B.bon.find((b) => b.id === String(bon)); set({ bayar: Object.assign({}, st().bayar, { bonId: String(bon), ketik: b0 ? String(b0.sisa) : '' }) }); },
    bpKetik: (v, el) => { const b = Object.assign({}, st().bayar || {}); b[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 80 : 14); set({ bayar: b }); },
    bpDari: ({ d }) => set({ bayar: Object.assign({}, st().bayar, { dari: d, adminI: d === 'rekening' ? st().bayar.adminI : -1 }) }),
    bpAdmin: ({ i }) => set({ bayar: Object.assign({}, st().bayar, { adminI: Number(i) }) }),
    bpLunas: () => { const H = BP.hitungBayar(st().bayar, kini()); if (H.bon) set({ bayar: Object.assign({}, st().bayar, { ketik: String(H.bon.sisa) }) }); },
    bpSimpanBayar: async () => { const r = BP.susunBayar(st().bayar, waktu()); if (await tulis(r)) sekali(akar.querySelector('.bn-hero'), 'pegas', 520); },
    bpTutup: () => set({ bayar: null, lama: null, kartu: null, kabar: '' }),
    bpUrung: async () => { const u = st().urung; if (!u) return; if (Date.now() > u.sampai) return set({ urung: null, kabar: 'Sudah lewat 90 detik — pembayaran tadi tetap tercatat; kalau salah, catat pembetulannya lewat sistem lama', kabarAwas: true }); await tulis(BP.susunUrungBayar(u.id)); },
    bpLamaBuka: () => { set({ lama: st().lama ? null : { pemasok: '', nama: '', tgl: '', ketik: '', catatan: '' }, bayar: null, kartu: null, kabar: '' }); keAtas(); },
    bpLamaPemasok: ({ p }) => set({ lama: Object.assign({}, st().lama, { pemasok: st().lama.pemasok === p ? '' : p, nama: '' }) }),
    bpLamaKetik: (v, el) => { const l = Object.assign({}, st().lama || {}); l[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 120 : el.dataset.kolom === 'nama' ? 60 : 14); if (el.dataset.kolom === 'nama') l.pemasok = ''; set({ lama: l }); },
    bpSimpanLama: async () => { await tulis(BP.susunBonLama(st().lama, waktu())); },
    bpKartuBuka: ({ nama }) => { const p = BP.cariPemasok(nama) || { nama, orang: '', kontak: '', tempo: 0, catatan: '' }; set({ kartu: st().kartu && st().kartu.nama === p.nama ? null : { nama: p.nama, orang: p.orang, kontak: p.kontak, tempo: p.tempo ? String(p.tempo) : '', catatan: p.catatan }, bayar: null, lama: null, kabar: '' }); keAtas(); },
    bpKartuKetik: (v, el) => { const k = Object.assign({}, st().kartu || {}); k[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 160 : 40); set({ kartu: k }); },
    bpKartuTempo: ({ t }) => set({ kartu: Object.assign({}, st().kartu, { tempo: String(t) }) }),
    bpSimpanKartu: async () => { const k = st().kartu; if (k) await tulis(BP.susunKartu(k.nama, k, waktu())); },
    bukaAturB: () => { const a = BP.aturBon(); set({ aturB: st().aturB ? null : { dekatHari: String(a.dekatHari), admin: a.admin.map((x) => ({ nama: x.nama, n: String(x.n) })) } }); },
    bpAturKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().aturB || { dekatHari: '', admin: [] })); if (el.dataset.i !== undefined) a.admin[Number(el.dataset.i)][el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'nama' ? 40 : 9); else a[el.dataset.kolom] = String(v).slice(0, 4); set({ aturB: a }); },
    bpAturTambah: () => { const a = JSON.parse(JSON.stringify(st().aturB)); a.admin.push({ nama: '', n: '' }); set({ aturB: a }); },
    bpAturLepas: ({ i }) => { const a = JSON.parse(JSON.stringify(st().aturB)); a.admin.splice(Number(i), 1); set({ aturB: a }); },
    simpanAturB: async () => { const a = st().aturB; if (a) await tulis(BP.susunAturBon(a, waktu())); },
    // ---- H3 BELANJA
    tabL: ({ t }) => { set({ tabL: t, kabar: '' }); ingatTab(); },
    blPemasok: ({ p }) => set({ pemasokBelanja: p, kabar: '' }),
    blUbah: ({ merk, arah }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); if (!b || !b.sumber) return; ubahPesan(BL.tulisPesan(st().pesan, merk, b.sumber.pemasok, Math.max(0, b.k + Number(arah)))); },
    blPakai: ({ merk }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); if (!b || !b.termurah) return set({ kabar: merk + ' belum pernah dibeli — pemasok & harganya belum diketahui, catat kedatangannya dulu di Barang masuk', kabarAwas: true }); if (b.dipesan) return; ubahPesan(BL.tulisPesan(st().pesan, merk, (b.sumber || b.termurah).pemasok, Math.max(1, b.saranK))); },
    blKetuk: ({ merk }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); if (!b || b.dipesan) return; if (b.k > 0) ubahPesan(BL.tulisPesan(st().pesan, merk, b.sumber.pemasok, 0)); else AKSI.blPakai({ merk }); },
    blGanti: ({ merk }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); const daftar = b ? H.D.merk.find((x) => x.merk === merk).sumber : []; if (!b || daftar.length < 2) return; const i = daftar.findIndex((x) => x.pemasok === b.sumber.pemasok); const n = daftar[(i + 1) % daftar.length]; ubahPesan(BL.tulisPesan(st().pesan, merk, n.pemasok, Math.max(1, b.k || b.saranK))); },
    blSaranPa: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const R = H.perP.find((r) => r.pemasok === p); if (!R || !R.saran.length) return; let o = Object.assign({}, st().pesan); R.saran.forEach((b) => { o = BL.tulisPesan(o, b.merk, p, b.saranK); }); ubahPesan(o); set({ kabar: R.saran.length + ' merek masuk daftar ' + p, kabarAwas: false }); },
    blPenuhi: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const r = BL.penuhiTruk(H, p, st().pesan); ubahPesan(r.pesan); set({ kabar: r.tambahan ? r.tambahan + ' karung ditambahkan — dibagi ke merek yang paling cepat habis' : H.atur.muatanKg > 0 ? 'Truknya sudah penuh' : 'Muatan truk belum diketahui — isi di Atur', kabarAwas: false }); },
    blKosongkan: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const R = H.perP.find((r) => r.pemasok === p); const o = Object.assign({}, st().pesan); (R ? R.d : []).forEach((b) => { delete o[b.merk]; }); ubahPesan(o); set({ kabar: 'Daftar ' + p + ' dikosongkan', kabarAwas: false }); },
    blSaranSemua: () => { const H = BL.hitungBelanja(st().pesan, kini()); if (!H.perluSemua.length) return; let o = Object.assign({}, st().pesan); H.perluSemua.forEach((b) => { o = BL.tulisPesan(o, b.merk, b.termurah.pemasok, b.saranK); }); ubahPesan(o); set({ kabar: H.perluSemua.length + ' merek masuk daftar belanja', kabarAwas: false }); },
    blWaBuka: ({ p }) => { set({ wa2: st().wa2 === p ? null : p, kabar: '' }); keAtas(); },
    blWaHarga: () => set({ waHarga: !st().waHarga }),
    blKirim: async () => { const p = st().wa2; if (!p) return; const r = BL.susunPesanan(st().pesan, p, waktu(), st().waHarga); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); const w = bukaWa(r.tautan); if (await tulis(r)) { ubahPesan(r.pesanSisa); if (!w) set({ kabar: 'Pesanan dicatat, tapi peramban menahan jendela WhatsApp — buka lagi dari "Pesanan yang menunggu datang"', kabarAwas: true }); } },
    blBukaLagi: ({ id }) => { const p = BL.pesananSemua().find((x) => String(x.id) === String(id)); if (!p) return; bukaWa('https://wa.me/' + (p.keNomor || '') + '?text=' + encodeURIComponent(p.teks || '')); },
    blPesanan: async ({ id, status }) => { await tulis(BL.susunUbahPesanan(id, status, waktu())); },
    bukaAturL: () => { const a = BL.aturBelanja(); set({ aturL: st().aturL ? null : { ambangHari: String(a.ambangHari), targetHari: String(a.targetHari), muatanKg: String(a.muatanKg) } }); },
    blAturKetik: (v, el) => { const a = Object.assign({}, st().aturL || {}); a[el.dataset.kolom] = String(v).slice(0, 7); set({ aturL: a }); },
    simpanAturL: async () => { const a = st().aturL; if (a) await tulis(BL.susunAturBelanja(a, waktu())); },
  };
  delegasi(akar, AKSI);

  // ====================== GAMBAR ======================
  function gambar() {
    if (!tampil) return; const s = st(); const sumber = sumberData(); const L = lebar();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Harga & Pemasok</div><div class="ket">${tanggalPendek(waktu().tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'DATA TOKO' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="kaca-btn kecil" data-aksi="keMenu">‹ Menu</div><div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      <div class="jalur rapat" data-k="keluarga">${KELUARGA.map(([id, nm]) => h`<div class="seg ${s.keluarga === id ? 'aktif' : ''}" data-aksi="keluarga" data-nama="${id}" data-k="kg-${id}">${nm}</div>`)}</div>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      ${s.keluarga === 'katalog' ? gambarKatalog(s, L) : s.keluarga === 'bon' ? gambarBon(s, L) : gambarBelanja(s, L)}
    `);
    gulirkan(akar, RP);
  }
  const tabBaris = (daftar, aktif, aksi, kls) => h`<div class="hg-tab ${kls || ''}" data-k="tab-${aksi}">${daftar.map(([id, nm]) => h`<div class="seg ${aktif === id ? 'aktif' : ''}" data-aksi="${aksi}" data-t="${id}" data-k="t-${id}">${nm}</div>`)}</div>`;
  const cap = (teks, kelas) => (teks ? h`<span class="hg-cap ${kelas || ''}">${teks}</span>` : '');
  const kapKelas = (b) => (b.adaDraf ? 'draf' : b.sengaja ? '' : b.status);

  // ---------- H1 KATALOG ----------
  function gambarKatalog(s, L) {
    const S = HG.hgSemua(kini()); const semuaTab = HG.TAB_HARGA; const tetapKiri = L !== 'hp'; const tetapKanan = L === 'mac';
    const tabAda = semuaTab.filter(([id]) => !(id === 'papan' && tetapKiri) && !(id === 'label' && tetapKanan)); const tab = tabAda.some(([id]) => id === s.tabH) ? s.tabH : tabAda[0][0];
    const lbl = HG.susunLabelTugas(S); const nama = (id) => (id === 'label' && lbl.tugas.length ? 'Label · ' + lbl.tugas.length : id === 'dampak' && S.perlu.length ? 'Dampak · ' + S.perlu.length : semuaTab.find((t) => t[0] === id)[1]);
    const panel = (id) => (id === 'papan' ? gambarPapan(s, S) : id === 'kalimat' ? gambarKalimat(s, S) : id === 'dampak' ? gambarDampak(S) : id === 'pasar' ? gambarPasar(S) : id === 'belah' ? gambarBelah(s, S) : gambarLabel(S, lbl));
    const tengah = h`<div class="hg-kolom" data-k="hg-tengah">${tabBaris(tabAda.map(([id]) => [id, nama(id)]), tab, 'tabH', L === 'hp' ? 'enam' : '')}${panel(tab)}</div>`;
    return h`<section class="hg-katalog" data-k="katalog">
      <div class="hg-ringkas" data-k="ringkas">${S.ringkas.map((r) => h`<div class="${r.nyala ? 'nyala' : ''}" data-k="r-${r.id}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      ${s.ubah ? gambarUbah(s, S) : ''}${s.terbit ? gambarTerbit(s, S) : ''}${s.wa ? gambarWaHarga(S) : ''}
      <div class="hg-grid ${L}" data-k="grid">${tetapKiri ? h`<div class="hg-kolom" data-k="hg-kiri">${gambarPapan(s, S)}</div>` : ''}${tengah}${tetapKanan ? h`<div class="hg-kolom" data-k="hg-kanan">${gambarLabel(S, lbl)}</div>` : ''}</div>
      ${S.nDraf ? h`<div class="hg-bilah" data-k="bilah"><div><div style="font-weight: 600;">${S.nDraf} harga berubah — kasir belum tahu</div><div class="ket">draf tidak sampai ke kasir sebelum diterbitkan</div></div><div class="kaca-btn aktif" data-aksi="hgBukaTerbit">Periksa & terbitkan</div></div>` : ''}
      ${gambarRiwayat()}${gambarAturH(s, S)}
      <div class="ket" style="font-size: 11px;">Katalog ini = katalog yang dibaca kasir (harga karung per kg, kemasan per kantong, literan per liter — koleksi yang sama dengan sistem lama). Perubahan jadi DRAF dulu; terbit = semuanya berganti sekaligus. Modal = modal rata-rata di buku (sama dengan laba, neraca & layar HPP); harga beli terbaru dibawa sebagai pembanding. ${S.atur.targetDariRata ? 'Target untung ' + RP(S.target) + '/kg = rata-rata untung katalog karung yang sedang berlaku (belum diatur owner).' : 'Target untung ' + RP(S.target) + '/kg diatur owner.'}${S.tanpaModal ? ' ' + S.tanpaModal + ' harga belum bisa dinilai karena modalnya belum tercatat.' : ''}</div>
    </section>`;
  }
  function gambarPapan(s, S) {
    const P = HG.susunPapan(S, s.papanSisi);
    return h`<div class="kartu kp-bingkai" data-k="papan"><div class="jalur rapat" data-k="sisi"><div class="seg ${P.owner ? 'aktif' : ''}" data-aksi="papanSisi" data-s="owner">Yang lu lihat</div><div class="seg ${!P.owner ? 'aktif' : ''}" data-aksi="papanSisi" data-s="pembeli">Yang pembeli lihat</div></div>
      <div class="kp-papan"><div class="kp-judul">Harga Beras Hari Ini</div><div class="kp-sub">${P.sub}</div>
        ${P.baris.map((m) => h`<div class="kp-baris" data-k="kp-${m.merk}"><div class="kp-mr">${m.merk}${P.owner && m.modal ? h`<small>modal ${RP(m.modal)}/kg</small>` : ''}</div><div class="kp-sel-baris">${m.sel.map((c) => h`<div class="kp-sel ${c.kelas}" data-k="kps-${c.k}" data-aksi="hgUbah" data-kunci="${c.k}"><span class="l">${c.lama ? ANGKA(c.lama) : ''}</span><span class="h">${typeof c.harga === 'number' ? ANGKA(c.harga) : c.harga}</span><span class="u">${c.satuan}${c.untung ? ' · ' + c.untung : ''}</span></div>`)}</div></div>`)}
        <div class="kp-kapur"><i></i><i></i><i></i></div></div>
      <div class="ket" style="font-size: 11px;">Ketuk angkanya untuk menulis ulang — tulisan baru jadi draf dulu (kapur kuning); papan pembeli baru berganti sesudah diterbitkan.</div>
      <div class="tombol-baris rapat"><div class="kaca-btn ${S.perlu.some((b) => b.usul > 0) ? '' : 'mati'}" data-aksi="hgUsulSemua">Pakai usul untuk ${S.perlu.filter((b) => b.usul > 0).length} harga — jadi draf dulu</div><div class="kaca-btn" data-aksi="hgWa">Kirim daftar harga ke WhatsApp</div></div></div>`;
  }
  function gambarUbah(s, S) {
    const U = HG.hitungUbah(S, s.ubah, s.ketik, s.ketikApa); if (U.tolak && !U.b) return h`<div class="pita-info awas" data-k="ubah-tolak">${U.tolak}</div>`; const b = U.b; const modeP = s.ketikApa === 'pasar';
    return h`<div class="kartu hg-ubah" data-k="ubah"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${b.judul}</div><div class="ket">${U.modalTeks}</div></div><div class="kaca-btn" data-aksi="hgTutupUbah">tutup</div></div>
      <div class="hg-dua-kolom"><span>Harga yang berlaku</span><span class="n">${b.lamaN ? RP(b.lamaN) + (b.setelTanggal ? ' · disetel ' + tanggalPendek(b.setelTanggal) : '') : 'belum ada'}</span>${b.adaDraf ? h`<span>Draf sekarang</span><span class="n">${RP(b.n)}</span>` : ''}<span>Harga pasar (catatan lu)</span><span class="n">${b.pasar ? RP(b.pasar.harga) + ' · ' + tanggalPendek(b.pasar.tanggal) : 'belum diisi'}</span>${b.laku ? h`<span>Terjual 30 hari</span><span class="n">${DESIMAL(b.laku)} ${b.st.per}</span>` : ''}</div>
      ${b.naik ? h`<div class="pita-info awas">${b.naikTeks}</div>` : ''}${b.sengaja ? h`<div class="pita-info">Sedang sengaja dibiarkan — layar tidak menagihnya sampai modal atau harganya berubah.</div>` : ''}
      <div class="jalur rapat" data-k="apa"><div class="seg ${!modeP ? 'aktif' : ''}" data-aksi="hgKetikApa" data-apa="jual">Harga jual lu</div><div class="seg ${modeP ? 'aktif' : ''}" data-aksi="hgKetikApa" data-apa="pasar">Harga pasar</div></div>
      <div class="hg-ketik-baris"><input class="ketik-nama" id="hgKetik" type="text" inputmode="numeric" placeholder="${modeP ? 'harga di toko lain' : 'harga baru per ' + b.st.per}" value="${s.ketik}" data-ketik="hgKetik">
        ${!modeP && b.usul ? h`<div class="kaca-btn aktif" data-aksi="hgIsi" data-n="${b.usul}"><span>pakai usul</span><b>${RP(b.usul)}</b></div>` : ''}${modeP && b.pasar ? h`<div class="kaca-btn" data-aksi="hgIsi" data-n="${b.pasar.harga}">samakan</div>` : ''}</div>
      <div class="ket">${modeP ? 'Harga pasar = catatan lu tentang harga toko lain. Tidak pernah jadi draf, tidak pernah sampai ke kasir.' : 'usul = ' + U.usulTeks}</div>
      ${U.arti ? h`<div class="${U.awas ? 'pita-info awas' : 'pita-info'}" data-k="arti">${U.arti}</div>` : ''}
      <div class="utama ${U.tolak ? 'redup' : ''}" data-aksi="hgSimpanUbah">${U.label}</div>
      <div class="tombol-baris rapat">${b.adaDraf ? h`<div class="kaca-btn putus" data-aksi="hgBuangDraf" data-kunci="${b.k}" data-k="buang">Buang draf harga ini</div>` : ''}
        ${!modeP && (b.sengaja || (!b.adaDraf && HG.HG_PERLU.indexOf(b.status) >= 0)) ? h`<div class="kaca-btn putus" data-aksi="hgSengaja" data-k="sengaja">${b.sengaja ? 'Tagih lagi harga ini' : b.status === 'lubang' ? 'Memang tidak dijual — jangan ditagih' : 'Biarkan — ini sengaja'}</div>` : ''}
        ${modeP && b.pasar ? h`<div class="kaca-btn putus" data-aksi="hgHapusPasar" data-k="hapus-pasar">Hapus catatan pasar</div>` : ''}<div class="kaca-btn" data-aksi="hgBelahIni" data-kunci="${b.k}" data-k="belah">Belah harga ini ›</div></div></div>`;
  }
  function gambarTerbit(s, S) {
    const P = HG.pratinjauTerbit(S);
    return h`<div class="kartu hg-terbit" data-k="terbit"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Periksa sebelum terbit</div><div class="ket">${P.n} harga berganti dalam SATU kali terbit — kasir tidak pernah melihat katalog separuh baru separuh lama</div></div><div class="kaca-btn" data-aksi="hgBukaTerbit">tutup</div></div>
      ${P.daftar.map((d) => h`<div class="hg-daftar" data-k="tb-${d.k}"><span>${d.judul}<br><span class="ket ${d.rugi ? 'awas-teks' : ''}">${d.ket}</span></span><span class="n lm">${d.lama ? RP(d.lama) : 'belum ada'}</span><span class="panah">→</span><span class="n">${RP(d.baru)}</span></div>`)}
      ${P.adaRugi ? h`<div class="pita-info awas">Ada harga di bawah modal. Boleh — tapi ini keputusan, bukan kebetulan. Ketuk terbitkan DUA kali.</div>` : ''}
      <div class="utama" data-aksi="hgTerbitkan">${P.adaRugi && !s.yakinRugi ? 'TERBITKAN ' + P.n + ' HARGA · ada yang rugi' : P.adaRugi ? 'KETUK SEKALI LAGI · terbitkan ' + P.n + ' harga' : 'TERBITKAN ' + P.n + ' HARGA SEKALIGUS'}</div>
      <div class="kaca-btn putus" data-aksi="hgBuangDraf">Buang semua draf</div></div>`;
  }
  function gambarWaHarga(S) {
    const t = HG.teksWaHarga(S, tanggalPendek(waktu().tanggal));
    return h`<div class="kartu" data-k="wa-harga" style="gap: 8px;"><div class="kepala-lembar"><div class="serif" style="font-size: 20px;">Daftar harga untuk WhatsApp</div><div class="kaca-btn" data-aksi="hgWa">tutup</div></div>
      <div class="hg-wa">${t.baris.map((x, i) => h`<div data-k="w-${i}">${i === 0 ? h`<b>${x.replace(/\*/g, '')}</b>` : x}</div>`)}</div><div class="pita-info">${t.arti}</div><div class="utama" data-aksi="hgKirimWa">KIRIM KE WHATSAPP</div></div>`;
  }
  function gambarKalimat(s, S) {
    const KL = HG.hitungKalimat(S, s.kal); const K = KL.K;
    const pil = (label, kolom, daftar) => h`<div class="hg-pil-l">${label}</div><div class="jalur bungkus" data-k="pil-${kolom}">${daftar.map(([v, nm]) => h`<div class="seg ${String(K[kolom]) === String(v) ? 'aktif' : ''}" data-aksi="kalPilih" data-kolom="${kolom}" data-v="${v}" data-k="p-${v}">${nm}</div>`)}</div>`;
    return h`<div class="kartu" data-k="kalimat" style="gap: 8px;"><div class="hg-kal">${KL.kalimat}</div>
      ${pil('Perintahnya', 'arah', [['naik', 'Naikkan'], ['turun', 'Turunkan']])}${pil('Mereknya', 'merek', [['semua', 'semua merek']].concat(S.merk.map((m) => [m, m])))}${pil('Ukurannya', 'satuan', [['semua', 'semua ukuran'], ['L', 'literan'], ['K', 'kemasan'], ['S', 'karung per kg']])}
      <div class="hg-ketik-baris"><div class="hg-pil-l" style="margin: 0;">Sebesar (per kg)</div><span class="step"><span data-aksi="kalRp" data-arah="-1">−</span><input class="ketik-nama sempit" id="kalRp" type="text" inputmode="numeric" value="${K.rp}" data-ketik="kalKetik" style="width: 90px; text-align: center;"><span data-aksi="kalRp" data-arah="1">+</span></span></div>
      <div class="label" style="padding-top: 4px;">Yang akan berubah</div>
      ${KL.hasil.length ? KL.hasil.map((d) => h`<div class="hg-daftar" data-k="kl-${d.k}"><span>${d.judul}<br><span class="ket ${d.rugi ? 'awas-teks' : ''}">${d.ket}</span></span><span class="n lm">${RP(d.lama)}</span><span class="panah">→</span><span class="n">${RP(d.baru)}</span></div>`) : h`<div class="pita-info" style="border-style: dashed;">${KL.kosongTeks}</div>`}
      <div class="ket">${KL.lewat}</div>
      <div class="utama ${KL.hasil.length ? '' : 'redup'}" data-aksi="kalPakai">${KL.hasil.length ? 'JADIKAN DRAF · ' + KL.hasil.length + ' harga' : 'Tidak ada yang berubah'}</div></div>`;
  }
  function gambarDampak(S) {
    const D = HG.susunDampak(S);
    return h`<div class="hg-kolom" data-k="dampak"><div class="kartu hero" style="gap: 3px;"><div class="hg-besar" data-gulir="${D.totalTinggal}">${RP(D.totalTinggal)}</div><div style="font-weight: 600;">${D.label}</div>${S.nDraf ? h`<div style="font-weight: 600; color: var(--aktif);">Draf lu: ${D.totalDraf > 0 ? '+' : ''}${RP(D.totalDraf)} per bulan kalau diterbitkan</div>` : ''}<div class="ket">Untung kotor sebulan dari harga sekarang ≈ ${RP(D.untungBulan)}</div></div>
      <div class="kartu" style="gap: 0;">${D.kelompok.map((g) => h`<div data-k="dk-${g.judul}"><div class="hg-kepala"><span class="nm">${g.judul}</span><span class="md ${g.awas ? 'naik' : ''}">${g.ket}</span></div>
        ${g.isi.map((b) => h`<div class="hg-dampak" data-k="d-${b.k}" data-aksi="hgUbah" data-kunci="${b.k}"><div><div>${b.judul}${cap(b.cap, b.cap === 'draf' ? 'draf' : b.cap === 'sengaja' ? '' : b.status)}</div><div class="ket">${b.sub}</div></div><div class="n">${b.angka}<small>${b.kecil}</small></div>${b.adaPakai ? h`<div class="bt"><i style="width: ${b.lebar}%;"></i></div><div class="kaca-btn kecil" data-aksi="hgPakaiUsul" data-kunci="${b.k}">usul ${RP(b.usul)}</div>` : ''}</div>`)}</div>`)}</div>
      <div class="pita-info" style="border-style: dashed; font-size: 11px;">${D.syarat}</div></div>`;
  }
  function gambarPasar(S) {
    const P = HG.susunPasar(S); let merkLalu = '';
    return h`<div class="hg-kolom" data-k="pasar"><div class="hg-legenda"><span>▏ modal</span><span>┊ target</span><span style="color: var(--aktif); font-weight: 600;">▍ harga pasar</span><span>● harga lu</span><span>pita emas = ruang gerak</span></div>
      <div class="hg-ringkas" data-k="ringkas-pasar">${P.ringkas.map((r) => h`<div class="${r.nyala ? 'nyala' : ''}" data-k="rp-${r.id}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      <div class="kartu" style="gap: 0;">${P.baris.map((b) => { const kepala = b.merk !== merkLalu; merkLalu = b.merk; return h`${kepala ? h`<div class="hg-kepala" data-k="pk-${b.merk}"><span class="nm">${b.merk}</span></div>` : ''}
        <div class="hg-anak" data-k="ps-${b.k}" data-aksi="hgUbah" data-kunci="${b.k}"><span>${b.satuan}</span><div><div class="hg-rel2">${b.adaModal ? h`<u style="left: ${b.zKiri}%; width: ${b.zLebar}%;"></u><b style="left: ${b.pM}%;"></b><b class="t" style="left: ${b.pT}%;"></b>` : ''}${b.adaPasar ? h`<b class="p" style="left: ${b.pP}%;"></b>` : ''}${b.adaTitik ? h`<i class="${b.status === 'rugi' || b.ps === 'atas' ? 'awas' : ''}" style="left: ${b.pN}%;"></i>` : ''}</div><div class="ket ${b.awas ? 'awas-teks' : ''}" style="font-size: 10.5px;">${b.teks}${cap(b.cap, b.cap === 'draf' ? 'draf' : b.status)}</div></div><span class="n">${b.n ? RP(b.n) : 'isi'}</span></div>`; })}</div>
      <div class="pita-info" style="border-style: dashed; font-size: 11px;">Harga pasar itu CATATAN lu tentang harga toko lain — ketuk barisnya, pilih "Harga pasar", ketik. Tidak pernah sampai ke kasir.</div></div>`;
  }
  function gambarBelah(s, S) {
    const B = HG.susunBelah(S, s.bedah); if (!B.b) return h`<div class="pita-info" data-k="belah-kosong">${B.kosongTeks}</div>`; const b = B.b;
    return h`<div class="kartu" data-k="belah" style="gap: 8px;"><div class="jalur bungkus" data-k="bd-merek">${S.merk.map((m) => h`<div class="seg ${b.merk === m ? 'aktif' : ''}" data-aksi="bdPilih" data-kolom="merek" data-v="${m}" data-k="m-${m}">${m}</div>`)}</div>
      <div class="jalur bungkus" data-k="bd-satuan">${B.satuan.map((x) => h`<div class="seg ${x.aktif ? 'aktif' : ''}" data-aksi="bdPilih" data-kolom="satuan" data-v="${x.id}" data-k="s-${x.id}">${x.nama}</div>`)}</div>
      ${B.ada ? h`<div data-k="bd-isi"><div class="ket">${B.judul}</div><div class="hg-besar ${B.sisa < 0 ? 'awas-teks' : ''}" data-gulir="${B.sisa}">${RP(B.sisa)}</div><div class="ket">${B.sisaTeks}</div></div>
        <div class="kr-dua"><div class="kr-kotak"><div class="kr-benda" style="transform: scale(${B.skala});"><div class="kr-isi ${B.kaleng ? 'kaleng' : 'karung'}"><div class="sisa" style="flex: ${B.fSisa} 0 0px; min-height: ${B.sisa > 0 ? 2 : 0}px;"></div><div class="makan" style="flex: ${B.fMakan} 0 0px;"></div><div class="pemasok" style="flex: ${B.fPemasok} 0 0px;"></div></div>${mentah(B.kaleng ? IKON.kaleng : IKON.karung)}<div class="kr-tulis">${b.merk.toUpperCase()}<small>${b.st.id === 'L' ? '1 liter' : b.st.id === 'S' ? '1 kg' : DESIMAL(b.st.kg) + ' kg'}</small></div></div></div>
          <div class="kr-rinci">${B.rinci.map((r, i) => h`<span class="kr-titik ${r.jenis}" data-k="rt-${i}"></span><span data-k="rn-${i}">${r.nama}</span><span class="n" data-k="rr-${i}">${r.n ? '−' + RP(r.n) : RP(0)}</span><span class="kt" data-k="rk-${i}">${r.persen ? r.persen + ' · ' : ''}${r.ket}</span>`)}<span class="kr-titik sisa"></span><span style="font-weight: 600;">tinggal di toko</span><span class="n" style="font-weight: 600;">${RP(B.sisa)}</span><span class="kt">${B.persen}</span></div></div>
        ${B.kotor > 0 ? h`<div><div class="ket" style="padding-bottom: 3px;">Selisih harga jual dan harga beli berasnya ${RP(B.kotor)}, dibesarkan: bergaris = ongkos · emas = tinggal di toko</div><div class="kr-kaca"><div class="makan" style="flex: ${B.bongkar} 0 0px;"></div><div class="makan" style="flex: ${B.wadah} 0 0px;"></div><div class="makan" style="flex: ${B.mdr} 0 0px;"></div><div class="sisa" style="flex: ${Math.max(0, B.sisa)} 0 0px;"></div></div></div>` : ''}
        ${B.awas ? h`<div class="pita-info awas">${B.awasTeks}</div>` : ''}${B.tanpaModal ? h`<div class="pita-info awas">Modal ${b.judul} belum tercatat — bagian "ke pemasok" belum bisa dibelah.</div>` : ''}
        <div class="jalur rapat" data-k="bd-bayar"><div class="seg ${B.bayar === 'tunai' ? 'aktif' : ''}" data-aksi="bdPilih" data-kolom="bayar" data-v="tunai">Dibayar tunai</div><div class="seg ${B.bayar === 'qris' ? 'aktif' : ''}" data-aksi="bdPilih" data-kolom="bayar" data-v="qris">Dibayar QRIS</div></div>`
        : h`<div class="pita-info" style="border-style: dashed;">${B.kosongTeks}</div>`}
      <div class="kaca-btn aktif" data-aksi="hgUbah" data-kunci="${b.k}">${B.ada ? 'Ubah harga ini' : 'Isi harganya'}</div>
      <div class="ket" style="font-size: 10.5px;">Gambar karungnya sesuai ukuran: tebal pita emas = bagian harga yang benar-benar tinggal. Gaji dan biaya toko lain belum dipotong di sini. Ongkos bongkar per kg & potongan QRIS diatur di Atur.</div></div>`;
  }
  function gambarLabel(S, lbl) {
    return h`<div class="hg-kolom" data-k="label">${lbl.ada ? h`<div class="kartu" style="gap: 6px; border-color: var(--awas);"><div style="font-weight: 600;">${lbl.judul}</div>
        ${lbl.tugas.map((t) => h`<div class="hg-tugas" data-k="lt-${t.k}"><div><div>${t.judul} → tulis <b class="serif" style="font-size: 15px;">${RP(t.tulis)}</b></div><div class="ket">di label masih ${t.lama ? RP(t.lama) : 'kosong'} · terbit ${tanggalPendek(t.tanggal)}</div></div><div class="kaca-btn aktif kecil" data-aksi="labelSelesai" data-kunci="${t.k}">sudah diganti</div></div>`)}
        <div class="ket">${lbl.arti}</div><div class="kaca-btn putus" data-aksi="labelSelesai" data-kunci="semua">Semua sudah diganti</div></div>` : h`<div class="pita-info" data-k="label-beres">Semua label di toko sudah sama dengan katalog.</div>`}
      <div class="hg-tag2">${S.merk.map((m) => h`<div class="hg-tag" data-k="tag-${m}"><div class="nm">${m}</div>${S.baris.filter((b) => b.merk === m).map((b) => h`<div class="hg-lbl ${b.status === 'lubang' ? 'lubang' : b.adaDraf ? 'draf' : b.labelBasi ? 'basi' : ''}" data-k="lb-${b.k}" data-aksi="hgUbah" data-kunci="${b.k}"><span>${b.st.pendek}</span><span class="h">${b.status === 'lubang' ? 'isi harga' : ANGKA(b.n)}</span></div>`)}</div>`)}</div></div>`;
  }
  function gambarRiwayat() {
    const r = HG.riwayatTerbit(10); if (!r.length) return '';
    return h`<div class="kartu platina" data-k="riwayat" style="gap: 2px;"><div class="label">Harga yang berubah (terbit dari sistem baru)</div>${r.map((x, i) => h`<div class="hg-daftar tiga" data-k="rw-${i}"><span class="ket">${tanggalPendek(x.tanggal)} ${x.jam}</span><span>${x.nama}<br><span class="ket">${x.arah}</span></span><span class="n">${RP(x.baru)}</span></div>`)}</div>`;
  }
  function gambarAturH(s, S) {
    const A = S.atur; const isian = [['targetPerKg', 'Target untung per kg (Rp)'], ['bulatLiter', 'Bulatkan usul literan ke (Rp)'], ['bulatKemasan', 'Bulatkan usul kemasan ke (Rp)'], ['bulatKarung', 'Bulatkan usul per kg ke (Rp)'], ['langkahRp', 'Langkah naik-turun per kg (Rp)'], ['ambangDampak', 'Batas "tidak seberapa" sebulan (Rp)'], ['bongkarKg', 'Ongkos bongkar per kg (Rp)'], ['mdrPersen', 'Potongan QRIS (30 = 0,30 %)'], ['mdrBatas', 'Bebas potongan QRIS sampai (Rp)']];
    return s.aturH ? h`<div class="kartu" data-k="atur-h" style="gap: 8px;"><div class="label">Aturan harga · angka owner</div><div class="ps-form tiga">${isian.map(([k, nm]) => h`<div data-k="ah-${k}"><div class="ket">${nm}</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturH[k]}" data-ketik="hgKetikAtur" data-kolom="${k}"></div>`)}</div>
        <div class="ket">Target untung dipakai untuk usulan & tanda "di bawah target" — mulai dari untung rata-rata yang sekarang berlaku supaya layar tidak menyalakan alarm di semua baris. Ongkos bongkar bawaan = terukur dari kedatangan (Σ upah bongkar ÷ Σ kg). Potongan QRIS: samakan dengan rincian aplikasi QRIS toko.</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturH">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturH">SIMPAN ATURAN</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturH" style="align-self: flex-start;">Atur target untung, pembulatan, langkah, ongkos bongkar & potongan QRIS · ${A.dariOwner ? 'diatur owner' : 'bawaan'} ›</div>`;
  }

  // ---------- H2 BON PEMASOK ----------
  function gambarBon(s, L) {
    const B = BP.susunBon(kini()); const tabAda = BP.TAB_BON.filter(([id]) => !(id === 'tusuk' && L !== 'hp')); const tab = tabAda.some(([id]) => id === s.tabB) ? s.tabB : tabAda[0][0];
    const nama = (id, nm) => (id === 'garis' && B.lewat.length ? nm + ' · ' + B.lewat.length : nm);
    const panel = (id) => (id === 'tusuk' ? gambarTusukan(s, B) : id === 'garis' ? gambarGaris(B) : gambarBuku(s, B));
    const urung = s.urung && Date.now() <= s.urung.sampai ? h`<div class="kaca-btn putus" data-k="urung" data-aksi="bpUrung">${s.urung.teks}</div>` : '';
    return h`<section class="hg-bon" data-k="bon">
      <div class="kartu hero bn-hero" data-k="hero" style="gap: 2px;"><div class="label" style="color: var(--hero-label);">Utang ke pemasok</div><div class="hg-besar" data-gulir="${B.total}">${RP(B.total)}</div><div style="font-weight: 600;">${B.nBon} bon · ${B.nPemasok} pemasok${B.tekor ? ' · kelebihan bayar ' + RP(B.tekor) + ' (ada kedatangan yang bonnya belum masuk buku)' : ''}</div><div class="ket">${B.kasTeks}</div></div>
      ${s.bayar ? gambarBayar(s, B) : ''}${s.lama ? gambarBonLama(s) : ''}${s.kartu ? gambarKartu(s) : ''}${urung}
      ${L === 'mac' ? h`<div class="hg-grid mac tiga" data-k="grid-bon"><div class="hg-kolom" data-k="k1">${gambarTusukan(s, B)}</div><div class="hg-kolom" data-k="k2">${gambarGaris(B)}</div><div class="hg-kolom" data-k="k3">${gambarBuku(s, B)}</div></div>`
        : L === 'tablet' ? h`<div class="hg-grid tablet" data-k="grid-bon"><div class="hg-kolom" data-k="k1">${gambarTusukan(s, B)}</div><div class="hg-kolom" data-k="k2">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabB')}${panel(tab)}</div></div>`
        : h`<div class="hg-kolom" data-k="grid-bon">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabB')}${panel(tab)}</div>`}
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="bpLamaBuka">＋ Catat bon lama (sebelum sistem)</div>${gambarAturB(s, B)}</div>
      <div class="ket" style="font-size: 11px;">Sisa bon = nilai − yang sudah dibayar (mesin yang sama dengan sistem lama); bon yang dibayar sebagian TETAP di daftar. Satu pembayaran = satu bon; bon tertua cuma saran — lu yang memilih. Jatuh tempo = tanggal barang datang + tempo di kartu pemasok (atau tempo umum di Atur Barang masuk) — ramalan, bukan janji tertulis. Membayar bon tidak mengubah laba; biaya admin transfer masuk biaya toko.</div>
    </section>`;
  }
  const bonSlip = (b, i, kelas) => h`<div class="bn-tusuk" data-k="slip-${b.id}"><div class="bn-slip ${i % 2 ? 'genap' : ''} ${b.jenis === 'saldoAwal' ? 'lama' : ''} ${kelas || ''}" data-aksi="bpBayarBuka" data-pemasok="${b.pemasok}" data-bon="${b.id}"><div><div class="tg">Bon ${b.tanggal ? tanggalPendek(b.tanggal) : '(tanpa tanggal)'}${b.cap ? h`<span class="bn-cap ${b.jenis === 'saldoAwal' ? 'redup' : ''}">${b.cap}</span>` : ''}${b.saran ? h`<span class="bn-cap saran">saran: ini dulu</span>` : ''}</div><div class="kt">${b.ket}</div><div class="kt ${b.status === 'lewat' ? 'awas' : ''}">${b.tempoTeks}</div>${b.isi ? h`<div class="kt">${b.isi}</div>` : ''}</div><div class="n">${RP(b.sisa)}</div></div></div>`;
  function gambarTusukan(s, B) {
    return h`<div class="kartu" data-k="tusukan" style="gap: 0; padding-top: 4px;">${B.tusukan.length ? B.tusukan.map((t) => h`<div data-k="tk-${t.pemasok}"><div class="bn-kepala" data-aksi="bpKartuBuka" data-nama="${t.pemasok}"><div><div class="nm">${t.pemasok}</div><div class="ket">${t.bon.length} bon · ${t.tempo.teks} · kartu ›</div></div><div class="n">${RP(t.total)}</div></div>
        ${t.bon.map((b, i) => bonSlip(b, i))}${t.tekor ? h`<div class="pita-info awas" style="margin: 6px 0;">Kelebihan bayar ${RP(t.tekor)} — ada kedatangan yang bonnya belum masuk buku.</div>` : ''}<div class="bn-dasar"></div></div>`) : h`<div class="menolak" style="padding: 10px 0;">Tidak ada bon yang masih terbuka.</div>`}
      <div class="ket" style="padding-top: 6px;">Ketuk kertas bonnya untuk membayar. Ketuk nama pemasok untuk kartunya (orang, nomor, tempo).</div></div>`;
  }
  function gambarGaris(B) {
    return h`<div class="hg-kolom" data-k="garis"><div class="hg-ringkas tiga" data-k="ringkas-bon">${B.ringkas.map((r, i) => h`<div class="${r.nyala ? 'nyala' : ''}" data-k="rb-${i}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      <div class="pita-info ${B.kurang ? 'awas' : ''}">${B.cukupTeks}</div>
      <div class="kartu" style="gap: 0;"><div class="bn-garis">${B.garis.length ? B.garis.map((g, i) => (g.tanda ? h`<div class="bn-tanda ${g.kelas}" data-k="gt-${i}">${g.teks}</div>` : h`<div class="bn-titik ${g.status}" data-k="gb-${g.id}" data-aksi="bpBayarBuka" data-pemasok="${g.pemasok}" data-bon="${g.id}"><div><div>${g.pemasok} · Bon ${g.tanggal ? tanggalPendek(g.tanggal) : '(tanpa tanggal)'}${g.cap ? h`<span class="bn-cap ${g.jenis === 'saldoAwal' ? 'redup' : ''}">${g.cap}</span>` : ''}</div><div class="ket ${g.status === 'lewat' ? 'awas-teks' : ''}">${g.tempoTeks}</div></div><div class="n">${RP(g.sisa)}</div></div>`)) : h`<div class="menolak" style="padding: 10px 0;">Tidak ada bon yang masih terbuka.</div>`}</div></div>
      <div class="ket">Jatuh tempo = tanggal barang datang + tempo pemasoknya. Penanda "uang toko habis di sini" memakai total kas dari titik kas — kalau titik kas belum disetel, penanda itu tidak digambar.</div></div>`;
  }
  function gambarBuku(s, B) {
    const pem = BP.daftarPemasok(); const nm = pem.some((p) => p.nama === s.bukuNama) ? s.bukuNama : (B.tusukan[0] ? B.tusukan[0].pemasok : (pem[0] ? pem[0].nama : '')); const P = BP.cariPemasok(nm); const buku = nm ? BP.bukuBon(nm) : { baris: [], saldo: 0 }; const terbuka = B.bon.filter((b) => b.pemasok === nm);
    const T = nm ? BP.tempoPemasok(nm) : { teks: '' };
    return h`<div class="hg-kolom" data-k="buku"><div class="jalur bungkus" data-k="buku-tab">${pem.map((p) => h`<div class="seg ${p.nama === nm ? 'aktif' : ''}" data-aksi="bukuNama" data-nama="${p.nama}" data-k="bt-${p.kunci}">${p.nama}</div>`)}</div>
      ${P ? h`<div class="kartu" data-k="kartu-ringkas" style="gap: 4px;" ><div style="display: flex; justify-content: space-between; align-items: baseline;"><div class="label">Kartu pemasok</div><div class="ket" data-aksi="bpKartuBuka" data-nama="${P.nama}" style="cursor: pointer; text-decoration: underline;">ubah ›</div></div>
        <div class="bn-kartu"><span class="l">Orangnya</span><span class="${P.orang ? '' : 'kosong'}">${P.orang || 'belum diisi'}</span><span class="l">Kontak</span><span class="${P.kontak ? '' : 'kosong'}">${P.kontak || 'belum diisi'}</span><span class="l">Tempo</span><span class="${T.hari ? '' : 'kosong'}">${T.teks}</span><span class="l">Kebiasaan</span><span>${P.caraTeks}</span><span class="l">Catatan</span><span class="${P.catatan ? '' : 'kosong'}">${P.catatan || 'belum ada'}</span><span class="l">Kedatangan</span><span>${P.kedatangan} kali · ${RP(P.belanja)}${P.terakhir ? ' · terakhir ' + tanggalPendek(P.terakhir) : ''}</span></div></div>` : ''}
      <div class="kartu" style="gap: 0;"><div class="bn-buku hd"><span>tgl</span><span>kejadian</span><span style="text-align: right;">naik / turun</span><span class="sd" style="text-align: right;">utang jadi</span></div>
        ${buku.baris.length ? buku.baris.map((e, i) => h`<div class="bn-buku" data-k="bb-${i}"><span class="ket">${e.t ? tanggalPendek(e.t) : 'tanpa tgl'}</span><span>${e.teks}<br><span class="ket">${e.ket}</span></span><span class="n">${(e.n > 0 ? '+' : '−') + RP(Math.abs(e.n)).replace('Rp', '')}</span><span class="n sd">${RP(e.saldo).replace('Rp', '')}</span></div>`) : h`<div class="menolak" style="padding: 8px 0;">Belum ada bon atau pembayaran atas nama ini.</div>`}
        <div style="display: flex; justify-content: space-between; align-items: baseline; padding: 8px 0 4px;"><span style="font-weight: 600;">Utang sekarang · ${terbuka.length} bon masih terbuka</span><span class="serif" style="font-size: 19px;">${RP(terbuka.reduce((a, b) => a + b.sisa, 0))}</span></div></div>
      ${terbuka.length ? h`<div class="utama" data-aksi="bpBayarBuka" data-pemasok="${nm}">BAYAR BON ${nm}</div>` : ''}</div>`;
  }
  function gambarBayar(s, B) {
    const H = BP.hitungBayar(s.bayar, kini()); const d = s.bayar;
    return h`<div class="kartu hg-lembar" data-k="bayar" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Bayar bon ${d.pemasok}</div><div class="ket">satu pembayaran = satu bon · pilih bonnya, ketik yang dibayar, uangnya dari mana</div></div><div class="kaca-btn" data-aksi="bpTutup">tutup</div></div>
      <div class="jalur bungkus" data-k="pilih-bon">${H.bonP.map((b) => h`<div class="seg ${b.id === d.bonId ? 'aktif' : ''}" data-aksi="bpBayarBon" data-bon="${b.id}" data-k="pb-${b.id}">${b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tgl'} · ${RP(b.sisa).replace('Rp', '')}</div>`)}</div>
      <div class="hg-ketik-baris"><input class="ketik-nama" id="bpKetik" type="text" inputmode="numeric" placeholder="jumlah yang dibayar" value="${d.ketik}" data-ketik="bpKetik" data-kolom="ketik"><div class="kaca-btn aktif" data-aksi="bpLunas">lunas ${H.bon ? RP(H.bon.sisa).replace('Rp', '') : ''}</div></div>
      <div class="ket">${H.bon ? 'Sisa bon ini ' + RP(H.bon.sisa) + (H.bon.dibayar > 0 ? ' · sudah dibayar ' + RP(H.bon.dibayar) : '') : 'Pilih bonnya'}</div>
      <div class="ket">Uangnya dari mana? ${B.adaKas ? '(yang dijaga total uang toko ' + RP(B.kas) + ' — sistem lama tidak memisahkan saldo per kantong)' : '(uang toko belum bisa dihitung — titik kas belum disetel)'}</div>
      <div class="tombol-baris rapat" data-k="dari">${BP.TEMPAT_UANG.map(([id, nm]) => h`<div class="kaca-btn ${d.dari === id ? 'aktif' : ''}" data-aksi="bpDari" data-d="${id}" data-k="dr-${id}">${nm}</div>`)}</div>
      ${d.dari === 'rekening' ? h`<div class="jalur bungkus" data-k="admin"><div class="seg ${d.adminI < 0 ? 'aktif' : ''}" data-aksi="bpAdmin" data-i="-1">tanpa biaya admin</div>${H.B.atur.admin.map((a, i) => h`<div class="seg ${d.adminI === i ? 'aktif' : ''}" data-aksi="bpAdmin" data-i="${i}" data-k="ad-${i}">${a.nama} ${RP(a.n)}</div>`)}</div>` : ''}
      <input class="ketik-nama" id="bpCatatan" type="text" placeholder="Catatan (boleh kosong)" value="${d.catatan}" data-ketik="bpKetik" data-kolom="catatan">
      ${H.arti ? h`<div class="bn-arti" data-k="arti"><b>${H.arti.a}</b><span>${H.arti.b}</span><span>${H.arti.c}</span></div>` : ''}
      <div class="utama ${H.tolak ? 'redup' : ''}" data-aksi="bpSimpanBayar">${H.label}</div></div>`;
  }
  function gambarBonLama(s) {
    const H = BP.hitungBonLama(s.lama); const pem = BP.daftarPemasok();
    return h`<div class="kartu hg-lembar" data-k="lama" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Bon lama, sebelum sistem</div><div class="ket">utang bertambah; uang, stok, dan laba TIDAK berubah</div></div><div class="kaca-btn" data-aksi="bpTutup">tutup</div></div>
      <div class="jalur bungkus" data-k="lama-pem">${pem.map((p) => h`<div class="seg ${s.lama.pemasok === p.nama ? 'aktif' : ''}" data-aksi="bpLamaPemasok" data-p="${p.nama}" data-k="lp-${p.kunci}">${p.nama}</div>`)}</div>
      <input class="ketik-nama" id="bpLamaNama" type="text" placeholder="…atau ketik nama pemasok baru" value="${s.lama.nama}" data-ketik="bpLamaKetik" data-kolom="nama">${H.kembar ? h`<div class="ket">"${H.kembar}" sudah ada — dipakai nama itu.</div>` : ''}
      <div class="ps-form dua"><div><div class="ket">Nilai bon (Rp)</div><input class="ketik-nama" id="bpLamaKetik" type="text" inputmode="numeric" value="${s.lama.ketik}" data-ketik="bpLamaKetik" data-kolom="ketik"></div><div><div class="ket">Tanggal bon (kosong = tidak tahu)</div><input class="ketik-nama" id="bpLamaTgl" type="date" value="${s.lama.tgl}" data-ketik="bpLamaKetik" data-kolom="tgl"></div></div>
      <input class="ketik-nama" id="bpLamaCatatan" type="text" placeholder="Catatan, mis. dari ingatan / dari nota kuning" value="${s.lama.catatan}" data-ketik="bpLamaKetik" data-kolom="catatan">
      ${H.arti ? h`<div class="bn-arti" data-k="arti-lama"><span>${H.arti}</span></div>` : ''}
      <div class="utama ${H.tolak ? 'redup' : ''}" data-aksi="bpSimpanLama">${H.label}</div></div>`;
  }
  function gambarKartu(s) {
    const k = s.kartu; const u = BP.tempoUmum().hari;
    return h`<div class="kartu hg-lembar" data-k="kartu" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Kartu ${k.nama}</div><div class="ket">orang, nomor, tempo, catatan — isian lu (tidak tertulis di dokumen mana pun)</div></div><div class="kaca-btn" data-aksi="bpTutup">tutup</div></div>
      <div class="ps-form dua"><div><div class="ket">Orang yang dihubungi</div><input class="ketik-nama" id="bpKOrang" type="text" value="${k.orang}" data-ketik="bpKartuKetik" data-kolom="orang" placeholder="nama orangnya"></div><div><div class="ket">Nomor WhatsApp / telepon</div><input class="ketik-nama" id="bpKKontak" type="text" inputmode="tel" value="${k.kontak}" data-ketik="bpKartuKetik" data-kolom="kontak" placeholder="08…"></div></div>
      <div class="ket">Tempo bon · dibayar sesudah berapa hari barang datang</div>
      <div class="hg-ketik-baris"><input class="ketik-nama sempit" id="bpKTempo" type="text" inputmode="numeric" value="${k.tempo}" data-ketik="bpKartuKetik" data-kolom="tempo" placeholder="0" style="width: 90px;"><div class="jalur bungkus" data-k="tempo-pil">${BP.TEMPO_PILIHAN.map((t) => h`<div class="seg ${String(k.tempo || 0) === String(t) ? 'aktif' : ''}" data-aksi="bpKartuTempo" data-t="${t}" data-k="tp-${t}">${t ? t + ' hari' : 'belum disepakati'}</div>`)}</div></div>
      <div class="ket">${Number(k.tempo) > 0 ? 'Tiap bon ' + k.nama + ' diramal jatuh tempo ' + Number(k.tempo) + ' hari sesudah barangnya datang.' : 'Tempo kartu kosong → dipakai tempo umum ' + u + ' hari (Stok → Barang masuk → Atur).'}</div>
      <input class="ketik-nama" id="bpKCatatan" type="text" value="${k.catatan}" data-ketik="bpKartuKetik" data-kolom="catatan" placeholder="mis. antar tiap Senin, minta transfer">
      <div class="utama" data-aksi="bpSimpanKartu">SIMPAN KARTU</div></div>`;
  }
  function gambarAturB(s, B) {
    return s.aturB ? h`<div class="kartu" data-k="atur-b" style="gap: 8px; grid-column: 1 / -1;"><div class="label">Aturan bon pemasok · angka owner</div>
        <div class="ps-form dua"><div><div class="ket">Bon dianggap dekat (hari)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturB.dekatHari}" data-ketik="bpAturKetik" data-kolom="dekatHari"></div></div>
        <div class="ket">Biaya admin transfer — dipilih waktu bon dibayar dari rekening. Tiap bank beda: ubah, tambah, atau hapus.</div>
        ${s.aturB.admin.map((a, i) => h`<div class="hg-ketik-baris" data-k="adm-${i}"><input class="ketik-nama" type="text" value="${a.nama}" data-ketik="bpAturKetik" data-kolom="nama" data-i="${i}" placeholder="mis. BI-FAST"><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${a.n}" data-ketik="bpAturKetik" data-kolom="n" data-i="${i}" placeholder="Rp" style="width: 110px;"><div class="kaca-btn kecil" data-aksi="bpAturLepas" data-i="${i}">hapus</div></div>`)}
        <div class="kaca-btn kecil" data-aksi="bpAturTambah" style="align-self: flex-start;">＋ tambah biaya admin</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturB">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturB">SIMPAN ATURAN</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturB">Atur biaya admin transfer & tanda "dekat" · ${B.atur.dariOwner ? 'diatur owner' : 'bawaan'} ›</div>`;
  }

  // ---------- H3 BELANJA ----------
  function gambarBelanja(s, L) {
    const H = BL.hitungBelanja(s.pesan, kini()); const pem = H.perP; const pa = pem.some((p) => p.pemasok === s.pemasokBelanja) ? s.pemasokBelanja : (pem[0] ? pem[0].pemasok : '');
    const tabAda = BL.TAB_BELANJA.filter(([id]) => !(id === 'truk' && L !== 'hp')); const tab = tabAda.some(([id]) => id === s.tabL) ? s.tabL : tabAda[0][0]; const nPerlu = H.perluSemua.length;
    const nama = (id, nm) => (id === 'hari' && nPerlu ? nm + ' · ' + nPerlu : nm); const panel = (id) => (id === 'truk' ? gambarTruk(s, H, pa) : id === 'hari' ? gambarHari(H) : gambarKertas(s, H));
    const bilah = H.totKarung ? h`<div class="hg-bilah" data-k="bilah-belanja"><div><div style="font-weight: 600;">${H.pesanTeks}</div><div class="ket">${H.pesanKet}</div></div><div class="kaca-btn aktif" data-aksi="blWaBuka" data-p="${pem.find((r) => r.karung) ? pem.find((r) => r.karung).pemasok : ''}">Kirim pesanan</div></div>` : '';
    return h`<section class="hg-belanja" data-k="belanja">
      ${s.wa2 ? gambarWaPesanan(s, H) : ''}
      ${L === 'mac' ? h`<div class="hg-grid mac tiga" data-k="grid-bl"><div class="hg-kolom" data-k="k1">${gambarTruk(s, H, pa)}</div><div class="hg-kolom" data-k="k2">${gambarHari(H)}</div><div class="hg-kolom" data-k="k3">${gambarKertas(s, H)}</div></div>`
        : L === 'tablet' ? h`<div class="hg-grid tablet" data-k="grid-bl"><div class="hg-kolom" data-k="k1">${gambarTruk(s, H, pa)}</div><div class="hg-kolom" data-k="k2">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabL')}${panel(tab)}</div></div>`
        : h`<div class="hg-kolom" data-k="grid-bl">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabL')}${panel(tab)}</div>`}
      ${bilah}${gambarPesanan(H)}${gambarAturL(s, H)}
      <div class="ket" style="font-size: 11px;">Saran = merek yang habis ≤ ${H.atur.ambangHari} hari menurut laju penjualan 14 hari; jumlahnya supaya cukup ${H.atur.targetHari} hari, dibulatkan ke karung penuh (rumus yang sama dengan sistem lama). Merek tanpa penjualan 14 hari tidak ditebak. Harga = harga terakhir tiap pemasok dari kedatangan nyata (tanggalnya selalu ditulis). Muatan truk ${H.atur.muatanTerukur ? 'terukur dari kedatangan nyata (median)' : 'diatur owner'}. Pesanan yang dikirim dicatat & dicocokkan dengan kedatangannya di Barang masuk.${H.D.tanpaPemasok.length ? ' Belum tahu pemasoknya: ' + H.D.tanpaPemasok.join(', ') + ' (belum pernah tercatat datang dari pemasok).' : ''}</div>
    </section>`;
  }
  const barisBelanja = (b, gaya) => h`<div class="bl-baris ${gaya || ''}" data-k="bl-${b.merk}"><div><div class="nm ${b.kritis ? 'awas-teks' : ''}">${b.merk}</div><div class="ket">${b.sisaTeks}</div></div>
    <div>${b.dipesan ? h`<span class="ket">dipesan</span>` : b.k > 0 ? h`<span class="step"><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="-1">−</span><span class="n" style="min-width: 74px; font-size: 12.5px;">${b.k} karung</span><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="1">+</span></span>` : h`<div class="kaca-btn kecil ${b.adaHarga ? '' : 'mati'}" data-aksi="blPakai" data-merk="${b.merk}">${b.saranTeks}</div>`}</div>
    ${b.k > 0 ? h`<div class="sd" data-aksi="blGanti" data-merk="${b.merk}" style="${b.sumber && b.sumber.length > 1 ? 'cursor: pointer;' : ''}">${b.hargaTeks} · ${BL.blKG(b.kg)} · ±${RP(b.rp)}${b.sesudahTeks ? ' · ' + b.sesudahTeks : ''}</div>` : b.k === 0 && !b.dipesan ? h`<div class="sd">${b.hargaTeks}</div>` : ''}${b.dipesan ? h`<div class="sd">${b.dipesanTeks}</div>` : ''}</div>`;
  function gambarTruk(s, H, pa) {
    const T = BL.susunTruk(H, pa); if (!T) return h`<div class="pita-info" data-k="truk-kosong">Belum ada pemasok yang pernah mengirim barang — catat kedatangan pertama di Stok → Barang masuk.</div>`; const R = T.R;
    const milik = R.milik.filter((b) => !b.k || (b.sumber && b.sumber.pemasok === pa)).sort((a, b) => (a.hari === null ? 999 : a.hari) - (b.hari === null ? 999 : b.hari));
    return h`<div class="hg-kolom" data-k="truk"><div class="jalur bungkus" data-k="pem-tab">${H.perP.map((p) => h`<div class="seg ${p.pemasok === pa ? 'aktif' : ''}" data-aksi="blPemasok" data-p="${p.pemasok}" data-k="pt-${p.kunci}">${p.pemasok}${p.karung ? ' · ' + p.karung : ''}</div>`)}</div>
      <div class="kartu" style="gap: 6px;"><div class="bl-truk">${mentah(IKON.truk)}<div class="bl-bak">${T.bak.map((k, i) => h`<div class="${k.kelas}" data-k="bak-${k.merk || 'kosong'}" style="flex: ${k.flex} 0 0px;">${k.t}</div>`)}${T.lebih ? h`<div class="lebih" style="flex: 0 0 14px;"></div>` : ''}</div></div>
        <div class="bl-muat"><span><b>${T.muatAngka}</b> ${T.muatDari}</span><span class="ket ${T.lebih ? 'awas-teks' : ''}" style="text-align: right;">${T.muatSisa}</span></div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${R.saran.length ? '' : 'mati'}" data-aksi="blSaranPa" data-p="${pa}">${T.saranTeks}</div><div class="kaca-btn aktif ${T.bisaPenuhi ? '' : 'mati'}" data-aksi="blPenuhi" data-p="${pa}">Penuhi truknya</div><div class="kaca-btn putus ${R.karung ? '' : 'mati'}" data-aksi="blKosongkan" data-p="${pa}">Kosongkan</div></div>
        <div class="ket">${R.caraTeks}${R.tempo.hari ? ' · ' + R.tempo.teks : ''}${R.kontak ? ' · ' + R.kontak : ' · nomor belum ada di kartu'}</div></div>
      ${R.uangTeks ? h`<div class="pita-info ${R.uangAwas ? 'awas' : ''}" data-k="uang">${R.uangTeks}</div>` : ''}
      <div class="kartu" style="gap: 0;">${milik.map((b) => barisBelanja(b))}</div>
      ${R.karung ? h`<div class="utama" data-aksi="blWaBuka" data-p="${pa}">KIRIM PESANAN ${pa} · ${R.karung} karung</div>` : ''}</div>`;
  }
  function gambarHari(H) {
    return h`<div class="hg-kolom" data-k="hari"><div class="hg-ringkas tiga" data-k="ringkas-bl">${H.ringkas.map((r, i) => h`<div class="${r.nyala && r.a ? 'nyala' : ''}" data-k="rl-${i}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      ${H.perluSemua.length ? h`<div class="kaca-btn putus" data-aksi="blSaranSemua">Pakai saran untuk ${H.perluSemua.length} merek</div>` : ''}
      <div class="kartu" style="gap: 0;">${H.kelompok.map((g) => h`<div data-k="hk-${g.judul}"><div class="hg-kepala"><span class="nm">${g.judul}</span><span class="md ${g.awas ? 'naik' : ''}">${g.ket}</span></div>
        ${g.isi.map((b) => h`<div class="bl-hari" data-k="bh-${b.merk}"><div class="atas"><span class="${b.kritis ? 'awas-teks' : ''}" style="font-weight: 600;">${b.merk}</span><span class="ket">${b.hari === null ? '—' : (b.hari > 30 ? '30+' : b.hari) + ' hr'}</span></div>
          <div class="bl-rel"><i class="${b.hari !== null && b.hari <= H.atur.ambangHari ? 'kritis' : ''}" style="width: ${b.hari === null ? 0 : Math.min(100, Math.round(b.hari / 30 * 100))}%;"></i><u style="left: ${b.hari === null ? 0 : Math.min(100, Math.round(b.hari / 30 * 100))}%; width: ${b.k && b.hariSesudah !== null ? Math.max(0, Math.min(100, Math.round(b.hariSesudah / 30 * 100)) - Math.min(100, Math.round((b.hari || 0) / 30 * 100))) : 0}%;"></u><b style="left: ${Math.round(H.atur.ambangHari / 30 * 100)}%;"></b></div>
          ${barisBelanja(b, 'rapat')}</div>`)}</div>`)}<div class="ket" style="padding-top: 6px;">${H.legenda}</div></div></div>`;
  }
  function gambarKertas(s, H) {
    return h`<div class="hg-kolom" data-k="kertas">${H.perluSemua.length ? h`<div class="kaca-btn putus" data-aksi="blSaranSemua">Pakai saran untuk ${H.perluSemua.length} merek</div>` : ''}
      ${H.kertas.length ? '' : h`<div class="pita-info">Tidak ada yang perlu dibeli — semua stok cukup lebih dari ${H.atur.ambangHari} hari atau sudah dipesan.</div>`}
      <div class="bl-kertas"><div class="ket" style="line-height: 28px; text-transform: uppercase; letter-spacing: 0.08em;">Daftar belanja · ${tanggalPendek(waktu().tanggal)}</div>
        ${H.kertas.map((r) => h`<div data-k="kr-${r.kunci}"><div class="jd">${r.pemasok} <span class="ket" style="font-size: 10.5px;">${r.karung ? r.karung + ' karung · ' + BL.blKG(r.kg) : 'belum ada yang dipilih'}</span></div>
          ${r.isi.map((b) => h`<div class="bl-tulis" data-k="kt-${b.merk}"><div class="bl-centang ${b.k > 0 ? 'ya' : ''}" data-aksi="blKetuk" data-merk="${b.merk}">${b.k > 0 ? '✓' : ''}</div><div data-aksi="blKetuk" data-merk="${b.merk}"><div style="font-weight: 600;">${b.merk}</div><div class="ket" style="font-size: 10px;">${b.sisaTeks}</div>${b.k > 0 ? h`<div class="ket" style="font-size: 10px;">±${RP(b.rp)}${b.sesudahTeks ? ' · ' + b.sesudahTeks : ''}</div>` : ''}</div>
            <div>${b.k > 0 ? h`<span class="step"><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="-1">−</span><span class="n" style="min-width: 66px; font-size: 12.5px;">${b.k} krg</span><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="1">+</span></span>` : h`<span class="ket" style="font-size: 10.5px;">${b.saranTeks}</span>`}</div></div>`)}
          <div class="bl-kaki"><div><div class="serif" style="font-size: 15px;">${r.karung ? '±' + RP(r.rp) : ''}</div><div class="ket" style="font-size: 10px;">${r.karung && r.muatanKg ? (r.lebih ? 'kelebihan ' + BL.blKG(r.lebih) + ' dari satu truk' : 'truk masih muat ' + BL.blKG(r.sisaMuat)) : ''}</div></div>${r.karung ? h`<div class="kaca-btn kecil gelap" data-aksi="blWaBuka" data-p="${r.pemasok}">kirim ke WA</div>` : ''}</div></div>`)}</div>
      ${H.lainnya.length ? h`<div class="kartu" style="gap: 0;"><div class="label" style="padding-top: 2px;">Belum perlu — tapi boleh ditambah</div>${H.lainnya.map((b) => h`<div class="bl-baris" data-k="ln-${b.merk}"><div><div class="nm">${b.merk}</div><div class="ket">${b.sisaTeks}</div></div><div class="kaca-btn kecil" data-aksi="blPakai" data-merk="${b.merk}">tambah</div></div>`)}</div>` : ''}</div>`;
  }
  function gambarWaPesanan(s, H) {
    const R = H.perP.find((r) => r.pemasok === s.wa2); if (!R || !R.karung) return h`<div class="pita-info awas" data-k="wa-kosong">Belum ada karung untuk ${s.wa2} di daftar. <span data-aksi="blWaBuka" data-p="${s.wa2}" style="text-decoration: underline; cursor: pointer;">tutup</span></div>`;
    const P = BL.susunPesanan(s.pesan, s.wa2, waktu(), s.waHarga);
    return h`<div class="kartu hg-lembar" data-k="wa-pesanan" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Pesanan untuk ${R.pemasok}</div><div class="ket">${R.kontak ? 'WhatsApp ke ' + R.kontak : 'nomor belum ada di kartu — WhatsApp menanyakan tujuannya'}</div></div><div class="kaca-btn" data-aksi="blWaBuka" data-p="${s.wa2}">tutup</div></div>
      <div class="jalur bungkus" data-k="wa-pem">${H.perP.filter((r) => r.karung).map((r) => h`<div class="seg ${r.pemasok === s.wa2 ? 'aktif' : ''}" data-aksi="blWaBuka" data-p="${r.pemasok}" data-k="wp-${r.kunci}">${r.pemasok}</div>`)}</div>
      <div class="hg-wa">${(P.baris || []).map((t, i) => h`<div data-k="wb-${i}">${i === 0 ? h`<b>${t.replace(/\*/g, '')}</b>` : t}</div>`)}</div>
      <div class="jalur rapat"><div class="seg ${s.waHarga ? 'aktif' : ''}" data-aksi="blWaHarga">${s.waHarga ? '✓ perkiraan harga ikut dikirim' : 'perkiraan harga TIDAK ikut dikirim'}</div></div>
      ${P.lebihTeks ? h`<div class="pita-info awas">${P.lebihTeks}</div>` : ''}${P.uangTeks ? h`<div class="pita-info">${P.uangTeks}</div>` : ''}
      <div class="utama" data-aksi="blKirim">KIRIM KE WHATSAPP · catat sebagai pesanan</div></div>`;
  }
  function gambarPesanan(H) {
    const semua = BL.pesananSemua().slice(0, 8); if (!semua.length) return '';
    return h`<div class="kartu platina" data-k="pesanan" style="gap: 2px;"><div class="label">Pesanan ke pemasok</div>${semua.map((p) => h`<div class="hg-tugas" data-k="ps-${p.id}"><div><div>${p.pemasok} · dipesan ${tanggalPendek(p.tanggal)} ${p.jam || ''} · <b>${p.status === 'menunggu' ? 'menunggu datang' : p.status === 'datang' ? 'sudah datang' + (p.datangTanggal ? ' ' + tanggalPendek(p.datangTanggal) : '') : 'dibatalkan'}</b></div><div class="ket">${(p.baris || []).map((b) => b.merk + ' ' + b.karung).join(' · ')} · ${p.karung} karung · ${BL.blKG(p.kg)} · ±${RP(p.rp)}</div></div>
      ${p.status === 'menunggu' ? h`<div class="hg-aksi-kecil"><div class="kaca-btn kecil" data-aksi="blBukaLagi" data-id="${p.id}">WA lagi</div><div class="kaca-btn kecil" data-aksi="blPesanan" data-id="${p.id}" data-status="datang">sudah datang</div><div class="kaca-btn kecil putus" data-aksi="blPesanan" data-id="${p.id}" data-status="batal">batalkan</div></div>` : ''}</div>`)}
      <div class="ket" style="padding-top: 4px;">"Sudah datang" dibaca sendiri dari kedatangan pemasok itu sesudah pesanan (Stok → Barang masuk); tombolnya untuk kedatangan yang dicatat di sistem lama.</div></div>`;
  }
  function gambarAturL(s, H) {
    return s.aturL ? h`<div class="kartu" data-k="atur-l" style="gap: 8px;"><div class="label">Aturan belanja · angka owner</div><div class="ps-form tiga">
        <div><div class="ket">Disarankan kalau habis dalam (hari)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturL.ambangHari}" data-ketik="blAturKetik" data-kolom="ambangHari"></div>
        <div><div class="ket">Belanja untuk berapa hari</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturL.targetHari}" data-ketik="blAturKetik" data-kolom="targetHari"></div>
        <div><div class="ket">Muatan satu truk (kg)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturL.muatanKg}" data-ketik="blAturKetik" data-kolom="muatanKg"></div></div>
        <div class="ket">Muatan truk bawaan = median berat 12 kedatangan terakhir (${BL.blKG(BL.muatanTerukur())}) — angka terukur, bukan tebakan; ganti kalau truknya beda.</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturL">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturL">SIMPAN ATURAN</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturL" style="align-self: flex-start;">Atur kapan disarankan, target hari & muatan truk · ${H.atur.dariOwner ? 'diatur owner' : 'bawaan'} ›</div>`;
  }

  K.dengar(gambar); dengarkan(() => gambar());
  let tundaUkur = null; window.addEventListener('resize', () => { clearTimeout(tundaUkur); tundaUkur = setTimeout(gambar, 160); });
  // dipanggil layar Menu / Stok: buka keluarga (katalog | bon | belanja) — lewat penangan yang sama dengan ketukan; pemasok = buka bukunya
  const buka = (keluarga, t) => { AKSI.keluarga({ nama: ['katalog', 'bon', 'belanja'].indexOf(keluarga) >= 0 ? keluarga : 'katalog' }); if (t && t.pemasok) set({ bukuNama: t.pemasok, tabB: 'buku' }); if (t && t.tab) set(keluarga === 'katalog' ? { tabH: t.tab } : keluarga === 'bon' ? { tabB: t.tab } : { tabL: t.tab }); };
  return { gambar, buka, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil) gambar(); } };
}
