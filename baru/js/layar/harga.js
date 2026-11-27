// LAYAR HARGA & PEMASOK — GAMBAR & KETUKAN. Tiga keluarga dalam satu layar: KATALOG (H1: Papan · Kalimat · Dampak · Pasar · Belah · Label),
// BON PEMASOK (H2: Tusukan bon · Jatuh tempo · Buku bon), BELANJA (H3: Isi truk · Kapan habis · Daftar). Angka & dokumen di harga-logika.js,
// bon-pemasok-logika.js, belanja-logika.js (tanpa DOM, dijaga uji_harga_baru.py). Satu markup tiga lebar: HP = tab; Tablet = benda utama menetap + tab; Mac = kolom.
import { nanti, segera } from '../inti/jadwal.js';   // owner 29 Sep: bunyi data/status digabung sekali per bingkai (lag & freeze)
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { pasangIsian } from '../inti/isian.js';
import { RP, ANGKA, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as HG from './harga-logika.js';
import * as BP from './bon-pemasok-logika.js';
import * as KL from './kpi-laba-logika.js';   // paket KPI laba (owner 24 Nov 2026): saran harga & mark-up, target margin per jenis, pembanding BPS, hari bayar pemasok
// owner 7 Okt: foto kertas bon pemasok — dikecilkan di perangkat, satu dokumen per foto di koleksi fotoBon (dibaca saat bon dibuka)
import * as FB from './foto-bon-logika.js';
import * as BL from './belanja-logika.js';
import * as SG from './stok-pantau-logika.js';   // paket P5 (owner 27 Nov 2026, A20): rencana beli bulan depan (tanpa musim)
import * as JN from './janji-logika.js';   // paket tanggal janji (owner 27 Nov 2026): janji datang pesanan ke pemasok
import { waktuSekarang } from './jual-logika.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, kabarKiriman, ingatStokKemasan, kunciLuarCache, cacheMentah } from '../data/toko.js';
import { mfMasaBerlaku } from '../mesin/modal-fifo.js';
import { kkSertakanKiriman } from '../data/katalog-kasir.js';
import * as JB from './jenis-beras-logika.js';
import * as VR from './varian-logika.js';
import * as AR from './arsip-logika.js';
import * as WB from './wadah-bernama-logika.js';
// putaran 30: daftar Kelas mutu (merek pemasok → kelas)
import * as KM from './kelas-merek-logika.js';
// paket brief 9 Okt (butir 8): HET beras — setelan & pemetaan owner (aturanToko/het), tanda di papan, ringkasan, lembar ubah & sebelum terbit
import * as HET from './het-logika.js';
// paket HPP & harga minimum (owner 26 Nov 2026): harga minimum per baris katalog, alarm modal + biaya dekat HET, kalkulator sebelum beli (tidak menulis)
import * as SH from './susut-harga-logika.js';
import { kunciKemasan } from '../mesin/pembantu.js';   // 25c: setelan jenis beras pindah dari sistem lama
// putaran 29: bayar bon menjaga isi kantong yang dipilih (tunai laci/brankas · transfer rekening) — saldo per tempat dari uang-logika
import { saldoKantong } from './uang-logika.js';
// paket Banding pemasok (owner 26 Nov 2026): keluarga keempat — harga tawaran & acuan (catatan), banding bulanan, laporan mingguan, rapor pemasok, tren modal
import * as BC from './banding-catat-logika.js';
import * as BD from './banding-pemasok-logika.js';

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
const KELUARGA = [['katalog', 'Katalog harga'], ['bon', 'Bon pemasok'], ['belanja', 'Belanja'], ['banding', 'Banding pemasok']];
const KELUARGA_ID = KELUARGA.map((k) => k[0]);

export function pasangLayarHarga(akar, opsi) {
  const tabLokal = bacaLokal(KUNCI_TAB, true) || {};
  // putaran 23d: keadaan awal sebagai FUNGSI — dipanggil ulang saat ganti orang (inti/isian.js)
  const awal = () => ({ keluarga: KELUARGA_ID.indexOf(bacaLokal(KUNCI_KELUARGA)) >= 0 ? bacaLokal(KUNCI_KELUARGA) : 'katalog', kabar: '', kabarAwas: false,
    tabD: tabLokal.d || 'minggu', bdSenin: null, bdBulan: null, bdCatat: null, aturBd: null, bdYakinHapus: null, bdTandai: '',   // paket Banding pemasok
    tabH: tabLokal.h || 'papan', ubah: null, ketik: '', ketikApa: 'jual', terbit: false, yakinRugi: false, kal: { arah: 'naik', merek: 'semua', satuan: 'semua', rp: 100 }, papanSisi: 'owner', wa: false, bedah: { merek: '', satuan: '', bayar: 'tunai' }, aturH: null,
    aturTm: null,   // paket KPI laba: draf target margin per jenis
    aturMin: null, hb: null, minBuka: false,   // paket HPP & harga minimum: draf setelan (target laba, jarak HET) · ketikan kalkulator sebelum beli · daftar lengkap
    tabB: tabLokal.b || 'tusuk', bukuNama: '', bayar: null, lama: null, kartu: null, urung: null, aturB: null, betul: null, foto: null,
    tabL: tabLokal.l || 'truk', pesan: bacaLokal(KUNCI_DRAF_BELANJA, true) || {}, pemasokBelanja: '', wa2: null, waHarga: false, waJanji: '', janjiP: null, aturL: null, jbUbah: null, jbKetik: '', jbDaftar: false, kmUbah: null, kmDaftar: false, hetBuka: false, aturHet: null, vrBaru: null, vrYakin: false, arYakin: '', arBuka: false, ltYakin: '' });
  const K = buatKeadaan(awal());
  const ISIAN = pasangIsian(K, awal, ['ketik', 'aturH', 'aturHet', 'waJanji', ['janjiP', (v) => !!(v && v.tanggal)], 'aturTm', 'aturMin', 'hb', 'aturB', 'aturL', 'bayar', 'lama', 'kartu', 'betul', 'jbKetik', ['vrBaru', (v) => !!(v && (v.mutu || v.harga))], 'bdCatat', 'aturBd', ['bdTandai', (v) => !!String(v || '').trim()]], [KUNCI_DRAF_BELANJA]);
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; let _kotor = true;   /* owner 29 Sep (lag): permintaan gambar saat tersembunyi cukup MENANDAI; saat dibuka digambar hanya kalau kotor */ const kini = () => opsi.sekarang() || new Date(); const waktu = () => waktuSekarang(opsi.sekarang() || undefined);
  // sanggahan layar mulus 7 Okt: dibuka lagi tanpa data baru tetap digambar ulang bila hari, hari tutup aktif (jam 12 siang) atau titik kas perangkat
  // berubah sejak gambar terakhir (kunciLuarCache) — semuanya tidak menaikkan versi data
  let _kunciLuar = ''; const kunciLuar = () => kunciLuarCache(kini());
  const lebar = () => (window.matchMedia('(min-width: 1100px)').matches ? 'mac' : window.matchMedia('(min-width: 720px)').matches ? 'tablet' : 'hp');
  const ingatTab = () => simpanLokal(KUNCI_TAB, { h: st().tabH, b: st().tabB, l: st().tabL, d: st().tabD });

  const namaPencatat = () => { const a = opsi.akun ? opsi.akun() : null; return (a && a.nama) || 'Owner'; };
  async function tulis(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }
    try {
      // putaran 25: hapus + dokumen dalam SATU kiriman (atomik; dulu dua kiriman — hapus bisa masuk tanpa penggantinya)
      let x = null; if ((r.dokumen && r.dokumen.length) || (r.hapus && r.hapus.length)) { x = await tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus }); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; } }
      set(Object.assign({}, r.patch || {}, { kabar: kabarKiriman(x, (r.patch || {}).kabar || ''), kabarAwas: !!(r.patch || {}).kabarAwas })); return true;
    } catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  // owner 7 Okt (Safari, sisa #104): tanpa 'noopener' — window.open(…, 'noopener') SELALU mengembalikan null walau jendelanya terbuka, jadi kabar
  // "peramban menahan jendela WhatsApp" dulu muncul tiap kali. Pemutusan opener dilakukan sendiri sesudah jendela terbuka (pola laporan.js).
  const bukaWa = (tautan) => { try { const w = window.open(tautan, '_blank'); if (w) { try { w.opener = null; } catch (e) { /* jendela sudah pindah asal */ } } return w; } catch (e) { return null; } };
  const keAtas = () => { try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); } };   // lembar digambar di atas daftar — ketukan dari bawah wajib melihat lembarnya
  const ubahPesan = (p) => { simpanLokal(KUNCI_DRAF_BELANJA, Object.keys(p).length ? p : null); set({ pesan: p }); };
  const S1 = () => HG.hgSemua(kini());
  // ---- owner 7 Okt: FOTO BON. Firestore: opsi.foto (app.js → firebase.js, koleksi fotoBon dibaca sekali saat lembar bon dibuka). Mode cadangan: simulasi di memori
  // layar ini saja (tidak tertulis ke mana pun). Alat gambar peramban (kanvas) diserahkan ke foto-bon-logika.js (diuji di jsc dengan kanvas tiruan).
  // Foto yang kirimannya belum diakui server (persistentLocalCache Firestore menahannya di perangkat) dihitung di fotoAntre — dibatasi FB.FBN_ANTRE_MAKS, ditandai
  // `antre` di daftar, dan TIDAK disebut tersimpan sampai `selesai` (firebase.js) mengakui / menolaknya.
  const fotoSim = {}; let fotoAntre = 0; const KABAR_PERMISI_FOTO = 'server belum membuka tempat foto bon (rules v7 — owner menerbitkannya di Firebase Console)';
  const fotoFirestore = () => !!(opsi.foto && opsi.foto.ada && opsi.foto.ada());
  async function muatFoto(b) {
    if (!b) return; set({ foto: { idBon: b.id, muat: 'muat', daftar: [], pesan: '', besar: null, yakinHapus: null, proses: false } });
    if (!fotoFirestore()) return set({ foto: Object.assign({}, st().foto, { muat: 'ada', daftar: (fotoSim[b.id] || []).slice(), pesan: 'SIMULASI (cadangan): foto hanya disimpan di memori layar ini' }) });
    try { const d = await opsi.foto.baca(b.id); const F = st().foto; if (!F || F.idBon !== b.id) return; set({ foto: Object.assign({}, F, { muat: 'ada', daftar: d || [], pesan: d && d.dariCache ? 'dibaca dari cache perangkat (server belum terjangkau)' : '' }) }); }
    catch (e) { const F = st().foto; if (!F || F.idBon !== b.id) return; const kode = String((e && (e.code || e.message)) || e);
      set({ foto: Object.assign({}, F, { muat: 'galat', pesan: /permission/i.test(kode) ? 'Server belum membuka tempat foto bon (rules v7 — diterbitkan owner di Firebase Console). Sesudah terbit, foto bisa dibaca & disimpan.' : 'Foto belum bisa dibaca: ' + kode }) }); }
  }
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
    const berkas = Array.from((el && el.files) || []); if (el) el.value = ''; const d = st().betul; const F = st().foto; if (!berkas.length || !d || !F) return;
    const b = BP.bpRincianBon(d.bonId, d.pemasok).bon; if (!b || F.idBon !== b.id || F.proses) return;
    set({ foto: Object.assign({}, F, { proses: true }), kabar: 'Mengecilkan foto…', kabarAwas: false });
    for (const f of berkas) {
      const hasil = await FB.fbnKecilkan(f, alatFoto()); const r = FB.fbnSusunSimpan(Object.assign({ pemasok: d.pemasok }, b), hasil, waktu(), st().foto.daftar, fotoAntre);
      if (r.tolak) { set({ foto: Object.assign({}, st().foto, { proses: false }), kabar: r.tolak, kabarAwas: true }); return; }
      const x = fotoFirestore() ? await opsi.foto.simpan(r.data) : { ok: true, simulasi: true, data: r.data };
      if (x && x.gagal) { set({ foto: Object.assign({}, st().foto, { proses: false }), kabar: 'Foto TIDAK tersimpan: ' + (/permission/i.test(x.pesan) ? KABAR_PERMISI_FOTO : x.pesan), kabarAwas: true }); return; }
      if (x && x.simulasi) fotoSim[b.id] = (fotoSim[b.id] || []).concat([r.data]);
      if (x && x.antre) { fotoAntre += 1; ikutiAntre(x.selesai, String(r.data.id), b.id); }
      set({ foto: Object.assign({}, st().foto, { daftar: (st().foto.daftar || []).concat([Object.assign({}, x.data || r.data, x && x.antre ? { antre: true } : {})]) }),
        kabar: x && x.antre ? FB.fbnKabarAntre(r.data) : (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar, kabarAwas: !!(x && x.antre) });
    }
    set({ foto: Object.assign({}, st().foto, { proses: false }) });
  }
  // kiriman foto yang menunggu: diakui → tanda `antre` dilepas & dikabarkan; ditolak → fotonya DIBUANG dari daftar dengan kabar (tidak ada foto "tersimpan" yang hilang diam-diam)
  function ikutiAntre(selesai, id, idBon) {
    const urus = (y) => { fotoAntre = Math.max(0, fotoAntre - 1); const F2 = st().foto; const di = !!(F2 && F2.idBon === idBon);
      if (y && y.ok) return set(Object.assign(di ? { foto: Object.assign({}, F2, { daftar: (F2.daftar || []).map((z) => (String(z.id) === id ? Object.assign({}, z, { antre: false }) : z)) }) } : {}, { kabar: 'Foto bon yang tadi menunggu sudah SAMPAI di server', kabarAwas: false }));
      set(Object.assign(di ? { foto: Object.assign({}, F2, { daftar: (F2.daftar || []).filter((z) => String(z.id) !== id) }) } : {}, { kabar: 'Foto bon yang tadi menunggu DITOLAK server — TIDAK tersimpan: ' + (y && /permission/i.test(y.pesan || '') ? KABAR_PERMISI_FOTO : (y && y.pesan) || 'tanpa keterangan'), kabarAwas: true })); };
    if (selesai && typeof selesai.then === 'function') selesai.then(urus, (e) => urus({ gagal: true, pesan: String((e && e.message) || e) })); else urus({ gagal: true, pesan: 'kiriman foto tidak bisa diikuti' });
  }

  const AKSI = {
    keluarga: ({ nama }) => { const k = nama; simpanLokal(KUNCI_KELUARGA, k); set({ keluarga: k, kabar: '', ubah: null, terbit: false, bayar: null, lama: null, kartu: null, wa: false, wa2: null }); },
    mode: () => opsi.gantiMode(), tutupKabar: () => set({ kabar: '' }), keMenu: () => opsi.pindah && opsi.pindah('menu'),
    // ---- H1 KATALOG
    tabH: ({ t }) => { set({ tabH: t, kabar: '' }); ingatTab(); },
    ltLangsung: async ({ merk, nyala }) => { await tulis(WB.wbSusunLiteranLangsung(merk, nyala === '1', waktu())); },
    ltHapus: async ({ merk }) => { const r = HG.susunHapusLiter(merk, waktu(), st().ltYakin === merk); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, ltYakin: r.perluYakin ? merk : '' }); await tulis(r); },
    hgUbah: ({ kunci }) => { set({ ubah: st().ubah === kunci ? null : kunci, ketik: '', ketikApa: 'jual', kabar: '', terbit: false }); keAtas(); },
    hgTutupUbah: () => set({ ubah: null, ketik: '', ketikApa: 'jual' }),
    hgKetik: (v) => set({ ketik: String(v).slice(0, 12) }),
    hgKetikApa: ({ apa }) => set({ ketikApa: apa, ketik: '' }),
    hgIsi: ({ n }) => set({ ketik: String(n) }),
    // paket KPI laba (butir 4): target margin per jenis — draf → KL.susunAturKpi (aturanToko/kpiLaba.targetMargin; kolom lain dokumen itu tidak tertimpa)
    tmBuka: () => { const T = KL.klTargetMargin(kini()); const d = {}; KL.KL_JENIS.forEach((j) => { const x = T.jenis[j.id]; d[j.id] = x.dariOwner ? String(x.pct).replace('.', ',') : ''; }); set({ aturTm: st().aturTm ? null : d }); },
    tmKetik: (v, el) => { const a = Object.assign({}, st().aturTm || {}); a[el.dataset.jenis] = String(v).slice(0, 8); set({ aturTm: a }); },
    tmSimpan: async () => { const a = st().aturTm; if (a && await tulis(KL.susunAturKpi({ targetMargin: a }, waktu()))) set({ aturTm: null }); },
    // paket HPP & harga minimum (owner 26 Nov 2026): setelan target laba per kg & jarak alarm HET; kalkulator sebelum beli (ketikan saja, tidak menulis)
    minAtur: () => { const A = SH.shAtur(); set({ aturMin: st().aturMin ? null : { targetLabaPerKg: String(A.targetLabaPerKg), jarakHet: String(A.jarakHet) } }); },
    minKetik: (v, el) => { const a = Object.assign({}, st().aturMin || {}); a[el.dataset.kolom] = String(v).slice(0, 10); set({ aturMin: a }); },
    minSimpan: () => tulis(SH.susunAturMinimum(st().aturMin || {}, waktu())), minBuka: () => set({ minBuka: !st().minBuka }),
    hbKetik: (v, el) => { const a = Object.assign({}, st().hb || {}); a[el.dataset.kolom] = String(v).slice(0, 14); set({ hb: a }); },
    hbKelas: ({ kelas }) => { const a = Object.assign({}, st().hb || {}); a.kelas = a.kelas === kelas ? '' : kelas; set({ hb: a }); }, hbBersih: () => set({ hb: null }),
    hgSimpanUbah: async () => { const s = st(); if (!s.ubah) return; if (await tulis(HG.susunUbah(s.ubah, s.ketik, s.ketikApa, waktu()))) sekali(akar.querySelector('.hg-ubah'), 'pegas', 520); },
    hgHapusPasar: async () => { const s = st(); if (s.ubah) await tulis(HG.susunHapusPasar(s.ubah, waktu())); },
    hgBuangDraf: async ({ kunci }) => { await tulis(HG.susunBuangDraf(kunci || null, waktu())); },
    hgSengaja: async () => { const s = st(); if (s.ubah) await tulis(HG.susunSengaja(s.ubah, waktu())); },
    hgBelahIni: ({ kunci }) => { const b = HG.cariBaris(S1(), kunci); if (!b) return; set({ bedah: { merek: b.merk, satuan: b.st.id, bayar: st().bedah.bayar }, tabH: 'belah', ubah: null, ketik: '', kabar: '' }); ingatTab(); },
    hgUsulSemua: async () => { await tulis(HG.susunUsulSemua(waktu())); },
    hgPakaiUsul: async ({ kunci }) => { await tulis(HG.susunPakaiUsul(kunci, waktu())); },
    hgBukaTerbit: () => { set({ terbit: !st().terbit, yakinRugi: false, ubah: null, kabar: '' }); keAtas(); },
    // 25c: katalog HP kasir (ringkasanKasir) SESUDAH terbit ikut di kiriman yang SAMA — kasir tidak pernah membaca harga lama sesudah harga baru terbit
    hgTerbitkan: async () => { const r = HG.susunTerbit(waktu(), st().yakinRugi); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, yakinRugi: !!r.perluYakin }); if (await tulis(kkSertakanKiriman(r, waktu().kini))) sekali(akar.querySelector('.hg-bilah'), 'pegas', 520); },
    kalPilih: ({ kolom, v }) => set({ kal: Object.assign({}, st().kal, { [kolom]: v }), kabar: '' }),
    kalRp: ({ arah }) => { const l = HG.aturHarga().langkahRp; set({ kal: Object.assign({}, st().kal, { rp: Math.max(l, (Number(st().kal.rp) || 0) + Number(arah) * l) }) }); },
    kalKetik: (v) => set({ kal: Object.assign({}, st().kal, { rp: String(v).slice(0, 7) }) }),
    kalPakai: async () => { await tulis(HG.susunKalimatDraf(st().kal, waktu())); },
    labelSelesai: async ({ kunci }) => { await tulis(HG.susunLabelSelesai(kunci, waktu())); },
    papanSisi: ({ s }) => set({ papanSisi: s }),
    hgWa: () => { set({ wa: !st().wa, ubah: null }); keAtas(); },
    hgKirimWa: () => { const t = HG.teksWaHarga(S1(), tanggalPendek(waktu().tanggal)); const w = bukaWa(t.tautan); set({ wa: false, kabar: w ? 'WhatsApp dibuka dengan daftar harga yang sedang berlaku' : 'Peramban menahan jendela WhatsApp — ketuk lagi tombolnya', kabarAwas: !w }); },
    // owner 7 Okt: kertas berkop & bernomor untuk pelanggan (daftar harga · harga yang naik) tinggal di Laporan › Dokumen › Dokumen kecil
    hgKertas: ({ jenis }) => { set({ wa: false }); if (opsi.keTujuan) opsi.keTujuan({ ke: 'laporan', keluarga: 'dokumen', jenis: jenis === 'naik' ? 'naik' : 'harga' }); },
    bdPilih: ({ kolom, v }) => set({ bedah: Object.assign({}, st().bedah, { [kolom]: v }) }),
    bukaAturH: () => { const a = HG.aturHarga(); set({ aturH: st().aturH ? null : { targetPerKg: String(a.targetPerKg), bulatLiter: String(a.bulatLiter), bulatKemasan: String(a.bulatKemasan), bulatKarung: String(a.bulatKarung), langkahRp: String(a.langkahRp), ambangDampak: String(a.ambangDampak), bongkarKg: String(a.bongkarKg), mdrPersen: String(a.mdrPersen), mdrBatas: String(a.mdrBatas) } }); },
    hgKetikAtur: (v, el) => { const a = Object.assign({}, st().aturH || {}); a[el.dataset.kolom] = String(v).slice(0, 10); set({ aturH: a }); },
    simpanAturH: async () => { const a = st().aturH; if (a) await tulis(HG.susunAturHarga(a, waktu())); },
    // ---- JENIS BERAS (25c): satu nama beras → satu jenis; dokumen pengaturan/jenisBeras sama dengan sistem lama
    // ---- putaran 27 (Bagian 2): varian baru dari katalog, sebelum barangnya datang — nama "<induk> · <mutu>", harga per kg langsung terbit, jenis ikut induk
    vrBaruBuka: () => set({ vrBaru: st().vrBaru ? null : { induk: '', mutu: '', harga: '' }, vrYakin: false, kabar: '' }),
    vrInduk: ({ merk }) => set({ vrBaru: Object.assign({}, st().vrBaru, { induk: merk, bawa: '' }), vrYakin: false }),
    // owner 7 Okt: induk masih berstok → wajib dipilih: stoknya ikut jadi varian, atau varian kosong (tidak ada lagi stok bercabang diam-diam)
    vrBawa: ({ v }) => set({ vrBaru: Object.assign({}, st().vrBaru, { bawa: (st().vrBaru || {}).bawa === v ? '' : v }), vrYakin: false }),
    vrKetikBaru: (v, el) => { const b = Object.assign({}, st().vrBaru || {}); b[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'mutu' ? 30 : 12); set({ vrBaru: b, vrYakin: false }); },
    vrBuat: async ({ usul }) => { const b = st().vrBaru || {}; const r = VR.vrSusunBuatDariHarga(b.induk, b.mutu, b.harga !== undefined && b.harga !== '' ? b.harga : usul, waktu(), st().vrYakin, b.bawa);
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, vrYakin: !!r.perluYakin }); if (await tulis(kkSertakanKiriman(r, waktu().kini))) set({ vrBaru: null, vrYakin: false }); },
    // ---- putaran 27 (Bagian 3): arsip produk — Isi · Arsipkan · Hapus untuk barang habis; Produk arsip memulihkan
    arIsi: ({ kunci }) => { const u = AR.arUrai(kunci); set({ ubah: null, arYakin: '' }); if (opsi.bukaStok) opsi.bukaStok(u.jenis === 'kemasan' ? 'adukan' : 'masuk', undefined, u.jenis === 'kemasan' ? null : { merk: u.nama }); },
    arArsip: async ({ kunci }) => { const r = AR.arSusunArsip(kunci, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); if (await tulis(r)) set({ ubah: null, arYakin: '' }); },
    arHapus: async ({ kunci }) => { const r = AR.arSusunHapus(kunci, waktu(), st().arYakin === kunci); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, arYakin: r.perluYakin ? kunci : '' }); if (await tulis(r)) set({ ubah: null, arYakin: '' }); },
    arPulih: async ({ kunci }) => { await tulis(AR.arSusunPulih(kunci, waktu())); },
    arDaftarBuka: () => set({ arBuka: !st().arBuka }),
    jbBuka: ({ merk }) => { set({ jbUbah: st().jbUbah === merk ? null : merk, jbKetik: '', kabar: '', ubah: null, terbit: false }); keAtas(); },
    jbTutup: () => set({ jbUbah: null, jbKetik: '' }),
    jbDaftarBuka: () => set({ jbDaftar: !st().jbDaftar }),
    jbPilih: async ({ j }) => { const m = st().jbUbah; if (m) await tulis(JB.susunJenisBeras(m, j, waktu())); },
    jbKetik: (v) => set({ jbKetik: String(v).slice(0, JB.JB_BATAS) }),
    jbSimpanKetik: async () => { const m = st().jbUbah; if (!m) return; if (!String(st().jbKetik || '').trim()) return set({ kabar: 'Ketik nama jenisnya dulu — untuk mengosongkan pakai tombol "kosongkan"', kabarAwas: true }); await tulis(JB.susunJenisBeras(m, st().jbKetik, waktu())); },
    jbKosongkan: async () => { const m = st().jbUbah; if (m) await tulis(JB.susunJenisBeras(m, '', waktu())); },
    // ---- putaran 30: KELAS MUTU — merek pemasok → kelas (nama wadah / kelas tanpa wadah / merek berbuku); tebakan ditandai sampai owner mengonfirmasi
    kmDaftarBuka: () => set({ kmDaftar: !st().kmDaftar }),
    kmBuka: ({ merk }) => { set({ kmUbah: st().kmUbah === merk ? null : merk, kabar: '', ubah: null, terbit: false, jbUbah: null }); keAtas(); },
    kmTutup: () => set({ kmUbah: null }),
    kmPilih: async ({ kelas }) => { const m = st().kmUbah; if (m) await tulis(KM.susunKelasMerk(m, kelas || '', waktu())); },
    kmSendiri: async ({ nama, nyala }) => { await tulis(KM.susunKelasSendiri(nama, nyala === '1', waktu())); },
    // ---- paket brief 9 Okt (butir 8): HET beras — setelan (zona, medium, premium, sumber) + pemetaan kelas/merek → premium · medium · bukan beras HET
    hetBuka: () => { const A = HET.hetAtur(); const buka = !st().hetBuka; set({ hetBuka: buka, aturHet: buka ? { zona: A.zona, medium: String(A.medium), premium: String(A.premium), sumber: A.sumber } : null, kabar: '' }); },
    hetKetik: (v, el) => { const a = Object.assign({}, st().aturHet || {}); a[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'sumber' ? 80 : el.dataset.kolom === 'zona' ? 24 : 9); set({ aturHet: a }); },
    hetSimpan: async () => { const a = st().aturHet || {}; if (await tulis(HET.susunAturHet(a, waktu()))) sekali(akar.querySelector('.het-kartu'), 'pegas', 520); },
    hetPeta: async ({ unit, kat }) => { if (await tulis(HET.susunPetaHet(unit, kat || '', waktu()))) sekali(akar.querySelector('.het-kartu'), 'pegas', 520); },
    // ---- H2 BON PEMASOK
    tabB: ({ t }) => { set({ tabB: t, kabar: '' }); ingatTab(); },
    bukuNama: ({ nama }) => set({ bukuNama: nama }),
    bpBayarBuka: ({ pemasok, bon }) => { const B = BP.susunBon(kini()); const d = B.bon.filter((b) => b.pemasok === pemasok).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal))); const b0 = d.find((b) => b.id === String(bon)) || d[0]; if (!b0) return set({ kabar: 'Tidak ada bon terbuka untuk ' + pemasok, kabarAwas: true });
      set({ bayar: { pemasok, bonId: b0.id, ketik: String(b0.sisa), dari: '', adminI: -1, catatan: '' }, lama: null, kartu: null, kabar: '' }); keAtas(); },
    bpBayarBon: ({ bon }) => { const B = BP.susunBon(kini()); const b0 = B.bon.find((b) => b.id === String(bon)); set({ bayar: Object.assign({}, st().bayar, { bonId: String(bon), ketik: b0 ? String(b0.sisa) : '' }) }); },
    bpKetik: (v, el) => { const b = Object.assign({}, st().bayar || {}); b[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 80 : 14); set({ bayar: b }); },
    bpDari: ({ d }) => set({ bayar: Object.assign({}, st().bayar, { dari: d, adminI: d === 'rekening' ? st().bayar.adminI : -1 }) }),
    // putaran 29: TUNAI (laci/brankas) atau TRANSFER (rekening) — cara bayar dibaca dari `dari`, tanpa kolom baru
    bpCara: ({ c }) => { const b = st().bayar; set({ bayar: Object.assign({}, b, c === 'transfer' ? { dari: 'rekening' } : { dari: b.dari === 'rekening' || !b.dari ? 'laci' : b.dari, adminI: -1 }) }); },
    bpAdmin: ({ i }) => set({ bayar: Object.assign({}, st().bayar, { adminI: Number(i) }) }),
    bpLunas: () => { const H = BP.hitungBayar(st().bayar, kini(), saldoKantong()); if (H.bon) set({ bayar: Object.assign({}, st().bayar, { ketik: String(H.bon.sisa) }) }); },
    bpSimpanBayar: async () => { const r = BP.susunBayar(st().bayar, waktu(), saldoKantong()); if (await tulis(r)) sekali(akar.querySelector('.bn-hero'), 'pegas', 520); },
    bpKeRekening: () => { if (opsi.keTujuan) opsi.keTujuan({ ke: 'uang', keluarga: 'pindah', rek: true }); else if (opsi.pindah) opsi.pindah('uang'); },
    bpTutup: () => set({ bayar: null, lama: null, kartu: null, kabar: '' }),
    bpUrung: async () => { const u = st().urung; if (!u) return; if (Date.now() > u.sampai) return set({ urung: null, kabar: 'Sudah lewat 90 detik — pembayaran tadi tetap tercatat. Sistem baru belum punya tombol membatalkan pembayaran bon yang lebih lama dari 90 detik', kabarAwas: true }); await tulis(BP.susunUrungBayar(u.id)); },
    bpLamaBuka: () => { set({ lama: st().lama ? null : { pemasok: '', nama: '', tgl: '', ketik: '', catatan: '' }, bayar: null, kartu: null, kabar: '' }); keAtas(); },
    bpLamaPemasok: ({ p }) => set({ lama: Object.assign({}, st().lama, { pemasok: st().lama.pemasok === p ? '' : p, nama: '' }) }),
    bpLamaKetik: (v, el) => { const l = Object.assign({}, st().lama || {}); l[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 120 : el.dataset.kolom === 'nama' ? 60 : 14); if (el.dataset.kolom === 'nama') l.pemasok = ''; set({ lama: l }); },
    bpSimpanLama: async () => { await tulis(BP.susunBonLama(st().lama, waktu())); },
    bpKartuBuka: ({ nama }) => { const p = BP.cariPemasok(nama) || { nama, orang: '', kontak: '', tempo: 0, catatan: '', bonLamaBergulir: false }; set({ kartu: st().kartu && st().kartu.nama === p.nama ? null : { nama: p.nama, orang: p.orang, kontak: p.kontak, tempo: p.tempo ? String(p.tempo) : '', catatan: p.catatan, bonLamaBergulir: p.bonLamaBergulir === true }, bayar: null, lama: null, kabar: '' }); keAtas(); },
    bpKartuKetik: (v, el) => { const k = Object.assign({}, st().kartu || {}); k[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 160 : 40); set({ kartu: k }); },
    bpKartuTempo: ({ t }) => set({ kartu: Object.assign({}, st().kartu, { tempo: String(t) }) }),
    bpKartuGulir: ({ v }) => set({ kartu: Object.assign({}, st().kartu, { bonLamaBergulir: v === '1' }) }),
    bpSimpanKartu: async () => { const k = st().kartu; if (k) await tulis(BP.susunKartu(k.nama, k, waktu())); },
    bukaAturB: () => { const a = BP.aturBon(); set({ aturB: st().aturB ? null : { dekatHari: String(a.dekatHari), admin: a.admin.map((x) => ({ nama: x.nama, n: String(x.n) })) } }); },
    bpAturKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().aturB || { dekatHari: '', admin: [] })); if (el.dataset.i !== undefined) a.admin[Number(el.dataset.i)][el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'nama' ? 40 : 9); else a[el.dataset.kolom] = String(v).slice(0, 4); set({ aturB: a }); },
    bpAturTambah: () => { const a = JSON.parse(JSON.stringify(st().aturB)); a.admin.push({ nama: '', n: '' }); set({ aturB: a }); },
    bpAturLepas: ({ i }) => { const a = JSON.parse(JSON.stringify(st().aturB)); a.admin.splice(Number(i), 1); set({ aturB: a }); },
    simpanAturB: async () => { const a = st().aturB; if (a) await tulis(BP.susunAturBon(a, waktu())); },
    // ---- owner 7 Okt: PEMBETULAN BON (pindah / jumlah pembayaran, nomor bon, bon lama) + FOTO BON — lembar `betul`, foto dibaca sekali saat lembar dibuka
    bpBetulBuka: ({ pemasok, bon }) => { const R = BP.bpRincianBon(bon, pemasok); const b = R.bon; if (!b) return set({ kabar: 'Bon itu sudah tidak ada', kabarAwas: true });
      set({ betul: { pemasok, bonId: String(bon), bayarId: '', mode: '', keBon: '', ketik: '', alasan: '', no: b.noBon || '', tgl: b.jenis === 'saldoAwal' ? (b.tanggal || '') : '', lama: b.jenis === 'saldoAwal' ? String(b.nilai) : '' }, bayar: null, lama: null, kartu: null, kabar: '' }); keAtas(); muatFoto(b); },
    bpBetulTutup: () => set({ betul: null, foto: null }),
    bpBetulBayar: ({ id, mode }) => { const d = st().betul; const sama = d.bayarId === String(id) && d.mode === mode; set({ betul: Object.assign({}, d, { bayarId: sama ? '' : String(id), mode: sama ? '' : mode, keBon: '', ketik: '', yakinN: '' }) }); },
    bpBetulKe: ({ bon }) => set({ betul: Object.assign({}, st().betul, { keBon: String(bon) }) }),
    bpBetulKetik: (v, el) => { const d = Object.assign({}, st().betul || {}); const k = el.dataset.kolom; d[k] = String(v).slice(0, k === 'alasan' ? 160 : k === 'no' ? 30 : 14); if (k === 'ketik') d.yakinN = ''; set({ betul: d }); },
    bpBetulPindah: async () => { const d = st().betul; if (d) await tulis(BP.susunPindahBayar(d.bayarId, d.keBon, d.alasan, waktu())); },
    // sanggahan E2: selisih BESAR (≥ 2× / ≤ ½, melebihi sisa bon, kas minus, hari yang sudah ditutup) = ketukan kedua untuk angka yang SAMA; kalimatnya menyebut lama → baru
    bpBetulNominal: async () => { const d = st().betul; if (!d) return; const r = BP.susunNominalBayar(d.bayarId, d.ketik, d.alasan, waktu(), d.yakinN === String(d.ketik));
      if (r.perluYakin) return set({ betul: Object.assign({}, d, { yakinN: String(d.ketik) }), kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    bpBetulNo: async () => { const d = st().betul; if (d && await tulis(BP.susunNoBon(d.bonId, d.pemasok, d.no, d.alasan, waktu()))) set({ betul: Object.assign({}, st().betul, { alasan: '' }) }); },
    bpBetulLama: async () => { const d = st().betul; if (d) await tulis(BP.susunBetulBonLama(d.bonId, { tgl: d.tgl, ketik: d.lama }, d.alasan, waktu())); },
    bpKeKoreksiMasuk: () => { set({ betul: null, foto: null }); if (opsi.bukaStok) opsi.bukaStok('masuk'); else set({ kabar: 'Tanggal & nilai bon kedatangan dibetulkan di Stok › Barang masuk › Buku kedatangan › koreksi', kabarAwas: false }); },
    fotoAmbil: ({ cara }) => { const F = st().foto; if (F && F.proses) return set({ kabar: 'Foto sebelumnya masih diproses — tunggu sebentar', kabarAwas: true });
      if (fotoAntre >= FB.FBN_ANTRE_MAKS) return set({ kabar: 'Foto sebelumnya BELUM sampai server — tunggu kabar "sampai di server" dulu', kabarAwas: true });
      const el = akar.querySelector(cara === 'kamera' ? '#fotoBonKamera' : '#fotoBonGaleri'); if (el) el.click(); },
    fotoBesar: ({ id }) => set({ foto: Object.assign({}, st().foto, { besar: st().foto && st().foto.besar === id ? null : id }) }),
    fotoHapus: async ({ id }) => { const F = st().foto; if (!F) return; if (F.yakinHapus !== id) return set({ foto: Object.assign({}, F, { yakinHapus: id }), kabar: 'Ketuk sekali lagi untuk menghapus foto bon itu (tidak bisa dibatalkan)', kabarAwas: true });
      const r = opsi.foto && opsi.foto.ada() ? await opsi.foto.hapus(id, F.idBon) : { ok: true, simulasi: true }; if (r && r.gagal) return set({ kabar: 'Foto TIDAK terhapus: ' + r.pesan, kabarAwas: true });
      if (r && r.simulasi) fotoSim[F.idBon] = (fotoSim[F.idBon] || []).filter((x) => String(x.id) !== String(id));
      const kini2 = st().foto; set({ foto: Object.assign({}, kini2, { daftar: (kini2.daftar || []).filter((x) => String(x.id) !== String(id)), yakinHapus: null, besar: null }), kabar: r && r.antre ? 'Penghapusan foto BELUM sampai server (sinyal lambat) — fotonya disembunyikan di sini; buka lagi bon ini nanti untuk memastikan' : (r && r.simulasi ? 'SIMULASI — ' : '') + 'Foto bon dihapus', kabarAwas: !!(r && r.antre) }); },
    // ---- H3 BELANJA
    tabL: ({ t }) => { set({ tabL: t, kabar: '' }); ingatTab(); },
    blPemasok: ({ p }) => set({ pemasokBelanja: p, kabar: '' }),
    blUbah: ({ merk, arah }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); if (!b || !b.sumber) return; ubahPesan(BL.tulisPesan(st().pesan, merk, b.sumber.pemasok, Math.max(0, b.k + Number(arah)))); },
    blPakai: ({ merk }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); if (!b || !b.termurah) return set({ kabar: merk + ' belum pernah dibeli — pemasok & harganya belum diketahui, catat kedatangannya dulu di Barang masuk', kabarAwas: true }); if (b.dipesan) return; ubahPesan(BL.tulisPesan(st().pesan, merk, (b.sumber || b.termurah).pemasok, Math.max(1, b.saranK))); },
    blGanti: ({ merk }) => { const H = BL.hitungBelanja(st().pesan, kini()); const b = H.baris.find((x) => x.merk === merk); const daftar = b ? H.D.merk.find((x) => x.merk === merk).sumber : []; if (!b || daftar.length < 2) return; const i = daftar.findIndex((x) => x.pemasok === b.sumber.pemasok); const n = daftar[(i + 1) % daftar.length]; ubahPesan(BL.tulisPesan(st().pesan, merk, n.pemasok, Math.max(1, b.k || b.saranK))); },
    // tinjauan E1: saran = per BARIS HARGA (stok & laju gabungan merek seharga), dibagi ke mereknya — satu pintu di belanja-logika (pakaiSaran)
    blSaranPa: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const r = BL.pakaiSaran(H, st().pesan, p); if (!r.merk) return; ubahPesan(r.pesan); set({ kabar: r.baris + ' baris harga (' + r.karung + ' karung) masuk daftar ' + p, kabarAwas: false }); },
    blPenuhi: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const r = BL.penuhiTruk(H, p, st().pesan); ubahPesan(r.pesan); set({ kabar: r.tambahan ? r.tambahan + ' karung ditambahkan — dibagi ke baris harga yang paling cepat habis' : H.atur.muatanKg > 0 ? 'Truknya sudah penuh' : 'Muatan truk belum diketahui — isi di Atur', kabarAwas: false }); },
    rbBuka: () => set({ rbBuka: !st().rbBuka }),
    blKosongkan: ({ p }) => { const H = BL.hitungBelanja(st().pesan, kini()); const R = H.perP.find((r) => r.pemasok === p); const o = Object.assign({}, st().pesan); (R ? R.d : []).forEach((b) => { delete o[b.merk]; }); ubahPesan(o); set({ kabar: 'Daftar ' + p + ' dikosongkan', kabarAwas: false }); },
    blSaranSemua: () => { const H = BL.hitungBelanja(st().pesan, kini()); const r = BL.pakaiSaran(H, st().pesan, ''); if (!r.merk) return; ubahPesan(r.pesan); set({ kabar: r.baris + ' baris harga (' + r.karung + ' karung) masuk daftar belanja', kabarAwas: false }); },
    // owner 7 Okt: daftar & truk per HARGA — − / + / centang satu baris harga membagi karungnya ke merek di dalamnya (belanja-logika ubahKelompok / ketukKelompok)
    blUbahG: ({ p, g, arah }) => { const H = BL.hitungBelanja(st().pesan, kini()); ubahPesan(BL.ubahKelompok(H, p, g, Number(arah), st().pesan)); },
    blKetukG: ({ p, g }) => { const H = BL.hitungBelanja(st().pesan, kini()); ubahPesan(BL.ketukKelompok(H, p, g, st().pesan)); },
    blWaBuka: ({ p }) => { set({ wa2: st().wa2 === p ? null : p, kabar: '' }); keAtas(); },
    blWaHarga: () => set({ waHarga: !st().waHarga }),
    blKirim: async () => { const p = st().wa2; if (!p) return; const r = BL.susunPesanan(st().pesan, p, waktu(), st().waHarga, st().waJanji, namaPencatat()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); const w = bukaWa(r.tautan); if (await tulis(r)) { ubahPesan(r.pesanSisa); set({ waJanji: '' }); if (!w) set({ kabar: 'Pesanan dicatat, tapi peramban menahan jendela WhatsApp — buka lagi dari "Pesanan yang menunggu datang"', kabarAwas: true }); } },
    blBukaLagi: ({ id }) => { const p = BL.pesananSemua().find((x) => String(x.id) === String(id)); if (!p) return; bukaWa('https://wa.me/' + (p.keNomor || '') + '?text=' + encodeURIComponent(p.teks || '')); },
    blPesanan: async ({ id, status }) => { await tulis(BL.susunUbahPesanan(id, status, waktu())); },
    // paket tanggal janji (owner 27 Nov 2026): janji datang dipilih saat kirim WA, diisi / digeser sesudah pemasok membalas (janji pertama tetap dihitung)
    blWaJanji: ({ t }) => set({ waJanji: String(t || '') }),
    blWaJanjiKetik: (v) => set({ waJanji: String(v || '') }),
    blJanjiBuka: ({ id }) => { const x = JN.jnPesananPemasok(id, kini()); set({ janjiP: st().janjiP && st().janjiP.id === String(id) ? null : { id: String(id), tanggal: x && x.janji.akhir ? x.janji.akhir : '' }, kabar: '' }); },
    blJanjiPilih: ({ t }) => { const j = st().janjiP; if (j) set({ janjiP: Object.assign({}, j, { tanggal: String(t || '') }) }); },
    blJanjiKetik: (v) => { const j = st().janjiP; if (j) set({ janjiP: Object.assign({}, j, { tanggal: String(v || '') }) }); },
    blJanjiSimpan: async () => { const j = st().janjiP; if (!j) return; await tulis(JN.jnSusunJanjiPemasok(j.id, j.tanggal, waktu(), namaPencatat())); },
    bukaAturL: () => { const a = BL.aturBelanja(); set({ aturL: st().aturL ? null : { ambangHari: String(a.ambangHari), targetHari: String(a.targetHari), muatanKg: String(a.muatanKg) } }); },
    blAturKetik: (v, el) => { const a = Object.assign({}, st().aturL || {}); a[el.dataset.kolom] = String(v).slice(0, 7); set({ aturL: a }); },
    simpanAturL: async () => { const a = st().aturL; if (a) await tulis(BL.susunAturBelanja(a, waktu())); },
    // ---- H4 BANDING PEMASOK (owner 26 Nov 2026): catatan ditulis lewat banding-catat-logika (satu penjaga isian untuk owner, tablet & usul)
    tabD: ({ t }) => { set({ tabD: t, kabar: '' }); ingatTab(); },
    bdMinggu: ({ arah }) => { const ini = BC.bcSenin(waktu().tanggal); const n = BC.bcTambahHari(st().bdSenin || ini, 7 * Number(arah)); set({ bdSenin: n >= ini ? null : n }); },
    bdGeserBulan: ({ arah }) => { const ini = waktu().tanggal.slice(0, 7); const n = BC.bcBulanGeser(st().bdBulan || ini, Number(arah)); set({ bdBulan: n >= ini ? null : n, bdTandai: '' }); },
    bdBuka: ({ jenis }) => { const d = st().bdCatat; set({ bdCatat: d && d.jenis === jenis ? null : bdDrafBaru(jenis), kabar: '' }); keAtas(); },
    bdJenis: ({ jenis }) => set({ bdCatat: Object.assign(bdDrafBaru(jenis), st().bdCatat || {}, { jenis }) }),
    bdKetik: (v, el) => { const d = Object.assign({}, st().bdCatat || {}); const k = el.dataset.kolom; d[k] = String(v).slice(0, k === 'catatan' ? 160 : 60); set({ bdCatat: d }); },
    bdPilihKolom: ({ kolom, v }) => set({ bdCatat: Object.assign({}, st().bdCatat || {}, { [kolom]: v }) }),
    bdSampai: () => { const d = Object.assign({}, st().bdCatat || {}); d.sampaiToko = !d.sampaiToko; if (d.sampaiToko) d.ongkirPerKg = ''; set({ bdCatat: d }); },
    bdSimpan: async () => { const d = st().bdCatat; if (d) await tulis(BC.susunCatatBanding(d.jenis, d, waktu(), 'Owner')); },
    bdHapus: async ({ id }) => { if (st().bdYakinHapus !== id) return set({ bdYakinHapus: id, kabar: 'Ketuk "YAKIN — hapus" sekali lagi untuk menghapus catatan itu', kabarAwas: true }); await tulis(BC.susunHapusBanding(id, waktu())); },
    bdPakaiTarik: async ({ i }) => { const x = BC.bcTarik().harga[Number(i)]; if (!x) return;
      await tulis(BC.susunCatatBanding('acuan', { tanggal: x.tanggal, sumber: x.sumber, tingkat: x.tingkat, mutu: x.mutu, wilayah: x.wilayah, hargaPerKg: x.hargaPerKg, otomatis: true, catatan: x.nama }, waktu(), 'Owner · tarik otomatis')); },
    bdTandaiKetik: (v) => set({ bdTandai: String(v).slice(0, 160) }),
    bdTandaiSimpan: async ({ bulan }) => { await tulis(BC.susunTandaiBanding(bulan, st().bdTandai || '', waktu())); },
    bukaAturBd: () => { const a = BC.bcAtur(); const pm = {}; BC.BC_TANDA.forEach(([id]) => { pm[id] = a.potongMutu[id] ? String(a.potongMutu[id]) : ''; });
      set({ aturBd: st().aturBd ? null : { minPemasok: String(a.minPemasok), hariMinggu: a.hariMinggu, tanggalBulan: String(a.tanggalBulan), wilayah: a.wilayah, sumber: a.sumber.join(', '), potongMutu: pm } }); },
    bdAturKetik: (v, el) => { const a = Object.assign({}, st().aturBd || {}); const k = el.dataset.kolom;
      if (k.indexOf('pm.') === 0) a.potongMutu = Object.assign({}, a.potongMutu || {}, { [k.slice(3)]: String(v).slice(0, 7) }); else a[k] = String(v).slice(0, k === 'sumber' ? 500 : 60); set({ aturBd: a }); },
    bdAturHari: ({ h }) => set({ aturBd: Object.assign({}, st().aturBd || {}, { hariMinggu: Number(h) }) }),
    simpanAturBd: async () => { const a = st().aturBd; if (a) await tulis(BC.susunAturBanding(Object.assign({}, a, { sumber: String(a.sumber || '').split(/[,\n]/).map((x) => x.trim()).filter(Boolean) }), waktu())); },
  };
  delegasi(akar, AKSI);
  // owner 7 Okt: pilihan berkas foto bon — peristiwa 'change' (Safari iOS menembakkannya untuk input berkas); penangan yang jatuh tetap dikabarkan
  akar.addEventListener('change', (ev) => { const el = ev.target && ev.target.closest ? ev.target.closest('[data-foto-pilih]') : null;
    if (el) fotoDipilih(el).catch((e) => set({ foto: Object.assign({}, st().foto || {}, { proses: false }), kabar: 'Foto gagal diproses: ' + String((e && e.message) || e), kabarAwas: true })); });

  // ====================== GAMBAR ======================
  function gambar() {
    if (!tampil || terkunci()) { _kotor = true; return; } _kotor = false; _kunciLuar = kunciLuar(); const s = st(); const sumber = sumberData(); const L = lebar();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Harga & Pemasok</div><div class="ket">${tanggalPendek(waktu().tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">${opsi.lonceng ? mentah(opsi.lonceng()) : ''}<div class="pil pil-akun ${sumber.jenis === 'firestore' ? '' : 'kedip'}" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="kaca-btn kecil" data-aksi="keMenu">‹ Menu</div><div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      <div class="jalur rapat" data-k="keluarga">${KELUARGA.map(([id, nm]) => h`<div class="seg ${s.keluarga === id ? 'aktif' : ''}" data-aksi="keluarga" data-nama="${id}" data-k="kg-${id}">${nm}</div>`)}</div>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      ${s.keluarga === 'katalog' ? gambarKatalog(s, L) : s.keluarga === 'bon' ? gambarBon(s, L) : s.keluarga === 'banding' ? gambarBanding(s, L) : gambarBelanja(s, L)}
    `);
    gulirkan(akar, RP);
  }
  const tabBaris = (daftar, aktif, aksi, kls) => h`<div class="hg-tab ${kls || ''}" data-k="tab-${aksi}">${daftar.map(([id, nm]) => h`<div class="seg ${aktif === id ? 'aktif' : ''}" data-aksi="${aksi}" data-t="${id}" data-k="t-${id}">${nm}</div>`)}</div>`;
  const cap = (teks, kelas) => (teks ? h`<span class="hg-cap ${kelas || ''}">${teks}</span>` : '');
  const kapKelas = (b) => (b.adaDraf ? 'draf' : b.sengaja ? '' : b.status);

  // ---------- H1 KATALOG ----------
  function gambarKatalog(s, L) {
    const S = HG.hgSemua(kini()); const HT = HET.hetKatalog(S); const semuaTab = HG.TAB_HARGA; const tetapKiri = L !== 'hp'; const tetapKanan = L === 'mac';
    const tabAda = semuaTab.filter(([id]) => !(id === 'papan' && tetapKiri) && !(id === 'label' && tetapKanan)); const tab = tabAda.some(([id]) => id === s.tabH) ? s.tabH : tabAda[0][0];
    const lbl = HG.susunLabelTugas(S); const nama = (id) => (id === 'label' && lbl.tugas.length ? 'Label · ' + lbl.tugas.length : id === 'dampak' && S.perlu.length ? 'Dampak · ' + S.perlu.length : semuaTab.find((t) => t[0] === id)[1]);
    const panel = (id) => (id === 'papan' ? gambarPapan(s, S, HT) : id === 'literan' ? gambarLiteran(s, S) : id === 'kalimat' ? gambarKalimat(s, S) : id === 'dampak' ? gambarDampak(S) : id === 'pasar' ? gambarPasar(S) : id === 'belah' ? gambarBelah(s, S) : gambarLabel(S, lbl));
    const tengah = h`<div class="hg-kolom" data-k="hg-tengah">${tabBaris(tabAda.map(([id]) => [id, nama(id)]), tab, 'tabH', L === 'hp' ? 'enam' : '')}${panel(tab)}</div>`;
    return h`<section class="hg-katalog" data-k="katalog">
      <div class="hg-ringkas" data-k="ringkas">${S.ringkas.map((r) => h`<div class="${r.nyala ? 'nyala' : ''}" data-k="r-${r.id}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      ${s.jbUbah ? gambarJenisUbah(s) : ''}${s.kmUbah ? gambarKelasUbah(s) : ''}${s.ubah ? gambarUbah(s, S) : ''}${s.terbit ? gambarTerbit(s, S) : ''}${s.wa ? gambarWaHarga(S) : ''}
      <div class="hg-grid ${L}" data-k="grid">${tetapKiri ? h`<div class="hg-kolom" data-k="hg-kiri">${gambarPapan(s, S, HT)}</div>` : ''}${tengah}${tetapKanan ? h`<div class="hg-kolom" data-k="hg-kanan">${gambarLabel(S, lbl)}</div>` : ''}</div>
      ${gambarHet(s, HT)}${gambarMinimum(s, S)}${gambarTargetMargin(s)}
      ${S.nDraf ? h`<div class="hg-bilah" data-k="bilah"><div><div style="font-weight: 600;">${S.nDraf} harga berubah — kasir belum tahu</div><div class="ket">draf tidak sampai ke kasir sebelum diterbitkan</div></div><div class="kaca-btn aktif" data-aksi="hgBukaTerbit">Periksa & terbitkan</div></div>` : ''}
      ${gambarRiwayat()}${gambarAturH(s, S)}${gambarJenisDaftar(s)}${gambarKelasDaftar(s)}${gambarVarianBaru(s, S)}${gambarProdukArsip(s)}
      <div class="ket" style="font-size: 11px;">Katalog ini = katalog yang dibaca kasir (harga karung per kg, kemasan per kantong, literan per liter — koleksi yang sama dengan sistem lama). Perubahan jadi DRAF dulu; terbit = semuanya berganti sekaligus. ${mfMasaBerlaku(cacheMentah('aturan')) ? 'Modal = modal nota berikutnya (FIFO: karung terlama yang masih ada; nilai rak di HPP)' : 'Modal = modal rata-rata di buku (sama dengan laba, neraca & layar HPP)'}; harga beli terbaru dibawa sebagai pembanding. ${S.atur.targetDariRata ? 'Target untung ' + RP(S.target) + '/kg = rata-rata untung katalog karung yang sedang berlaku (belum diatur owner).' : 'Target untung ' + RP(S.target) + '/kg diatur owner.'}${S.tanpaModal ? ' ' + S.tanpaModal + ' harga belum bisa dinilai karena modalnya belum tercatat.' : ''}</div>
    </section>`;
  }
  function gambarPapan(s, S, HT) {
    const P = HG.susunPapan(S, s.papanSisi); const hetAtas = (k) => (P.owner && HT && HT.per[k] && HT.per[k].status === 'atas' ? HT.per[k] : null);
    return h`<div class="kartu kp-bingkai" data-k="papan"><div class="jalur rapat" data-k="sisi"><div class="seg ${P.owner ? 'aktif' : ''}" data-aksi="papanSisi" data-s="owner">Yang lu lihat</div><div class="seg ${!P.owner ? 'aktif' : ''}" data-aksi="papanSisi" data-s="pembeli">Yang pembeli lihat</div></div>
      <div class="kp-papan"><div class="kp-judul">Harga Beras Hari Ini</div><div class="kp-sub">${P.sub}</div>
        ${P.baris.map((m) => h`<div class="kp-baris" data-k="kp-${m.merk}"><div class="kp-mr">${m.merk}${P.owner && m.modal ? h`<small>modal ${RP(m.modal)}/kg</small>` : ''}${P.owner ? (() => { const j = JB.jbJenisMerk(m.merk); return h`<small class="hg-jenis ${j ? '' : 'kosong'}" data-aksi="jbBuka" data-merk="${m.merk}" data-k="jb-${m.merk}" style="cursor: pointer; text-decoration: underline dotted;">${j || 'jenis?'}</small>`; })() : ''}</div><div class="kp-sel-baris">${m.sel.map((c) => { const x = hetAtas(c.k); return h`<div class="kp-sel ${c.kelas}${x ? ' het-atas' : ''}" data-k="kps-${c.k}" data-aksi="hgUbah" data-kunci="${c.k}" title="${x ? x.teks : ''}"><span class="l">${c.lama ? ANGKA(c.lama) : ''}</span><span class="h">${typeof c.harga === 'number' ? ANGKA(c.harga) : c.harga}</span><span class="u">${c.satuan}${c.untung ? ' · ' + c.untung : ''}</span>${x ? h`<span class="het">▲ HET +${x.lebihTeks}</span>` : ''}</div>`; })}</div></div>`)}
        <div class="kp-kapur"><i></i><i></i><i></i></div></div>
      <div class="ket" style="font-size: 11px;">Ketuk angkanya untuk menulis ulang — tulisan baru jadi draf dulu (kapur kuning); papan pembeli baru berganti sesudah diterbitkan.${P.owner && HT && HT.nAtas ? ' ▲ HET = harga per kg di atas HET kelasnya (rincian di kartu HET).' : ''}</div>
      <div class="tombol-baris rapat"><div class="kaca-btn ${S.perlu.some((b) => b.usul > 0) ? '' : 'mati'}" data-aksi="hgUsulSemua">Pakai usul untuk ${S.perlu.filter((b) => b.usul > 0).length} harga — jadi draf dulu</div><div class="kaca-btn" data-aksi="hgWa">Kirim daftar harga ke WhatsApp</div></div></div>`;
  }
  // putaran 27 (Bagian 5): harga per LITER melekat pada WADAH (tempat bernama W1–W8); merek yang dijual literan langsung dari karungnya punya harga sendiri
  function gambarLiteran(s, S) {
    const LT = HG.hgLiteran(S); const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const baris = (k, kiri, kanan, aksi) => h`<div data-k="${k}" style="display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 6px 0; border-top: 1px solid var(--garis, rgba(255,255,255,.08));"><div style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">${kiri}</div><div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">${kanan}${aksi || ''}</div></div>`;
    const harga = (x) => h`<div class="kaca-btn kecil ${x.status === 'lubang' ? 'awas' : ''}" data-aksi="hgUbah" data-kunci="${x.k}">${x.harga ? RP(x.harga) + '/L' : 'belum ada harga'}</div>`;
    return h`<div class="kartu" data-k="literan" style="gap: 6px;"><div class="label">Literan · ${LT.wadah.length} wadah</div>
      <div class="ket">Harga per liter melekat pada WADAH, bukan merek. Isi wadah boleh dari beberapa merek karung; literan yang terjual memotong buku merek-merek itu sebanding isinya, modalnya = rata-rata isi wadah. Merek yang cuma masuk lewat wadah tidak butuh harga liter sendiri.</div>
      ${LT.wadah.map((x, i) => baris('lw-' + x.nama, h`<b>W${i + 1} · ${x.nama}</b><span class="ket">${!x.diketahui ? 'isi per merek belum diketahui — cocokkan wadahnya' : x.komposisi.length ? x.komposisi.map((c) => c.merk + ' ' + KG(c.kg) + (x.komposisi.length > 1 ? ' (' + DESIMAL(c.persen) + '%)' : '')).join(' + ') : 'kosong menurut buku'}</span>
        <span class="ket">${x.modalLiter > 0 ? 'modal ' + RP(Math.round(x.modalLiter)) + '/L (' + RP(Math.round(x.modalKg)) + '/kg × ' + DESIMAL(x.rasio) + ')' : 'modal belum bisa dihitung'}${x.untungLiter !== null ? ' · ' + (x.untungLiter < -0.5 ? 'RUGI ' + RP(Math.round(-x.untungLiter)) : 'untung ' + RP(Math.round(x.untungLiter))) + '/L' : ''}</span>`, harga(x)))}
      <div class="label" style="margin-top: 8px;">Literan langsung dari karung · ${LT.langsung.length}${LT.dariOwner ? '' : ' · perkiraan dari penjualan lama'}</div>
      <div class="ket">Merek yang diserok langsung dari karungnya (tidak lewat wadah) — butuh harga liter sendiri dan tampil di rak Literan dengan namanya.</div>
      ${LT.langsung.length ? LT.langsung.map((x) => baris('ll-' + x.merk, h`<b>${x.merk}</b><span class="ket">${x.modalLiter > 0 ? 'modal ' + RP(Math.round(x.modalLiter)) + '/L' : 'modal belum tercatat'}</span>`, harga(x), h`<div class="kaca-btn kecil putus" data-aksi="ltLangsung" data-merk="${x.merk}" data-nyala="0">lepas</div>`)) : h`<div class="ket">Belum ada.</div>`}
      ${LT.calon.length ? h`<div class="ket">Tandai merek literan langsung:</div><div class="jalur bungkus" data-k="lt-calon">${LT.calon.map((m) => h`<div class="seg" data-aksi="ltLangsung" data-merk="${m}" data-nyala="1" data-k="ltc-${m}">+ ${m}</div>`)}</div>` : ''}
      ${LT.tidakDipakai.length ? h`<div class="label" style="margin-top: 8px;">Harga liter yang tidak dipakai · ${LT.tidakDipakai.length}</div><div class="ket">Masih tersimpan di katalog (dan katalog HP kasir lama) tapi bukan wadah dan bukan literan langsung — tidak tampil di rak Jual. Hapus = dokumen harganya saja; riwayat terbit & nota lama tetap.</div>
      ${LT.tidakDipakai.map((x) => baris('lt-' + x.merk, h`<b>${x.merk}</b><span class="ket">${RP(x.harga)}/L${x.arsip ? ' · diarsipkan' : ''}</span>`, h`<div class="kaca-btn kecil ${s.ltYakin === x.merk ? 'awas' : 'putus'}" data-aksi="ltHapus" data-merk="${x.merk}">${s.ltYakin === x.merk ? 'YAKIN — hapus' : 'hapus'}</div>`))}` : ''}</div>`;
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
      ${modeP ? '' : gambarSaran(b, S)}
      ${U.arti ? h`<div class="${U.awas ? 'pita-info awas' : 'pita-info'}" data-k="arti">${U.arti}</div>` : ''}
      ${modeP ? '' : (() => { const X = HET.hetSatuHarga(b, U.n > 0 ? U.n : b.n); return !X ? '' : X.status === 'atas' ? h`<div class="pita-info awas" data-k="ubah-het">${X.teks} — boleh; owner yang memutuskan</div>` : h`<div class="ket" data-k="ubah-het">${X.status === 'belum' ? 'HET: ' + X.unit + ' belum dipetakan (kartu HET › Atur)' : 'HET: ' + X.teks}</div>`; })()}
      ${modeP ? '' : (() => { const X = SH.shMinimumKatalog({ baris: [b] }, kini(), 'tampil').per[b.k]; const n = U.n > 0 ? U.n : b.n; if (!X || X.minimum === null || X.minimum === undefined) return X && X.status === 'tanpaBiaya' ? h`<div class="ket" data-k="ubah-min">Harga minimum belum bisa dihitung — biaya toko per kg belum ada bulan selesainya.</div>` : '';
        const bawah = n > 0 && n + 0.5 < X.minimum; return h`<div class="${bawah ? 'pita-info awas' : 'ket'}" data-k="ubah-min">Harga minimum ${RP(X.minimumBulat)}${b.st.id === 'S' ? '/kg' : ' per ' + b.st.per} (modal ${RP(Math.round(X.rinci.modal * X.kg))} + biaya toko ${RP(Math.round(X.rinci.biaya * X.kg))}${X.rinci.laba ? ' + target laba ' + RP(Math.round(X.rinci.laba * X.kg)) : ''})${bawah ? ' — harga ini di bawahnya; boleh, owner yang memutuskan' : ''}</div>`; })()}
      <div class="utama ${U.tolak ? 'redup' : ''}" data-aksi="hgSimpanUbah">${U.label}</div>
      <div class="tombol-baris rapat">${b.adaDraf ? h`<div class="kaca-btn putus" data-aksi="hgBuangDraf" data-kunci="${b.k}" data-k="buang">Buang draf harga ini</div>` : ''}
        ${!modeP && (b.sengaja || (!b.adaDraf && HG.HG_PERLU.indexOf(b.status) >= 0)) ? h`<div class="kaca-btn putus" data-aksi="hgSengaja" data-k="sengaja">${b.sengaja ? 'Tagih lagi harga ini' : b.status === 'lubang' ? 'Memang tidak dijual — jangan ditagih' : 'Biarkan — ini sengaja'}</div>` : ''}
        ${modeP && b.pasar ? h`<div class="kaca-btn putus" data-aksi="hgHapusPasar" data-k="hapus-pasar">Hapus catatan pasar</div>` : ''}<div class="kaca-btn" data-aksi="hgBelahIni" data-kunci="${b.k}" data-k="belah">Belah harga ini ›</div></div>
      ${gambarArsipBarang(s, b)}</div>`;
  }
  function gambarTerbit(s, S) {
    const P = HG.pratinjauTerbit(S); const HD = HET.hetDraf(S); const hetX = (k) => (HD.per[k] && HD.per[k].status === 'atas' ? HD.per[k] : null);
    return h`<div class="kartu hg-terbit" data-k="terbit"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Periksa sebelum terbit</div><div class="ket">${P.n} harga berganti dalam SATU kali terbit — kasir tidak pernah melihat katalog separuh baru separuh lama</div></div><div class="kaca-btn" data-aksi="hgBukaTerbit">tutup</div></div>
      ${P.daftar.map((d) => h`<div class="hg-daftar" data-k="tb-${d.k}"><span>${d.judul}<br><span class="ket ${d.rugi ? 'awas-teks' : ''}">${d.ket}</span>${hetX(d.k) ? h`<br><span class="ket awas-teks" data-k="tbh-${d.k}">${hetX(d.k).teks}</span>` : ''}</span><span class="n lm">${d.lama ? RP(d.lama) : 'belum ada'}</span><span class="panah">→</span><span class="n">${RP(d.baru)}</span></div>`)}
      ${P.adaRugi ? h`<div class="pita-info awas">Ada harga di bawah modal. Boleh — tapi ini keputusan, bukan kebetulan. Ketuk terbitkan DUA kali.</div>` : ''}
      ${HD.teks ? h`<div class="pita-info ${HD.nAtas ? 'awas' : ''}" data-k="tb-het">${HD.teks}</div>` : ''}
      ${(() => { const MN = SH.shMinimumKatalog(S, kini(), 'tampil'); const d = MN.bawah.filter((x) => x.adaDraf); return d.length ? h`<div class="pita-info awas" data-k="tb-min">${d.length} harga draf di bawah harga minimum (${d.slice(0, 4).map((x) => x.judul + ' ' + RP(x.n) + ' < ' + RP(x.minimumBulat)).join(' · ')}) — boleh terbit; owner yang memutuskan.</div>` : ''; })()}
      <div class="utama" data-aksi="hgTerbitkan">${P.adaRugi && !s.yakinRugi ? 'TERBITKAN ' + P.n + ' HARGA · ada yang rugi' : P.adaRugi ? 'KETUK SEKALI LAGI · terbitkan ' + P.n + ' harga' : 'TERBITKAN ' + P.n + ' HARGA SEKALIGUS'}</div>
      <div class="kaca-btn putus" data-aksi="hgBuangDraf">Buang semua draf</div></div>`;
  }
  function gambarWaHarga(S) {
    const t = HG.teksWaHarga(S, tanggalPendek(waktu().tanggal));
    return h`<div class="kartu" data-k="wa-harga" style="gap: 8px;"><div class="kepala-lembar"><div class="serif" style="font-size: 20px;">Daftar harga untuk WhatsApp</div><div class="kaca-btn" data-aksi="hgWa">tutup</div></div>
      <div class="hg-wa">${t.baris.map((x, i) => h`<div data-k="w-${i}">${i === 0 ? h`<b>${x.replace(/\*/g, '')}</b>` : x}</div>`)}</div><div class="pita-info">${t.arti}</div><div class="utama" data-aksi="hgKirimWa">KIRIM KE WHATSAPP</div>
      <div class="tombol-baris" data-k="wa-kertas"><div class="kaca-btn" data-aksi="hgKertas" data-jenis="harga">Daftar harga berkop · cetak / PDF</div><div class="kaca-btn" data-aksi="hgKertas" data-jenis="naik">Harga yang naik · untuk pelanggan</div></div></div>`;
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
  // ---- JENIS BERAS (25c) — lembar pilih jenis satu nama beras & daftar semua nama
  function gambarJenisUbah(s) {
    const m = s.jbUbah; const kini = JB.jbJenisMerk(m); const D = JB.jbDaftar().baris.find((b) => b.merk === m) || { asal: '' };
    return h`<div class="kartu hg-ubah" data-k="jb-ubah"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Jenis beras · ${m}</div><div class="ket">Sekarang: ${kini || 'belum diisi'}${D.asal === 'tebakan' ? ' (tebakan dari namanya — belum pernah diisi owner)' : D.asal === 'kosong' ? ' (sengaja dikosongkan)' : ''}</div></div><div class="kaca-btn" data-aksi="jbTutup">tutup</div></div>
      <div class="jalur bungkus" data-k="jb-pilihan">${JB.jbPilihan().map((j) => h`<div class="seg ${kini === j ? 'aktif' : ''}" data-aksi="jbPilih" data-j="${j}" data-k="jbp-${j}">${j}</div>`)}</div>
      <div class="hg-ketik-baris"><input class="ketik-nama" type="text" placeholder="jenis lain — ketik namanya" value="${s.jbKetik}" data-ketik="jbKetik"><div class="kaca-btn aktif" data-aksi="jbSimpanKetik">simpan</div></div>
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="jbKosongkan">kosongkan — tidak masuk kelompok mana pun</div></div>
      <div class="ket" style="font-size: 11px;">Jenis mengelompokkan nama beras di Harga, Stok (total per jenis), dan Jual (saring rak). Salah jenis tidak mengubah harga, stok, atau uang.</div></div>`;
  }
  // putaran 27 (Bagian 3): barang di balik baris harga ini — kalau habis: Isi · Arsipkan · Hapus
  function gambarArsipBarang(s, b) {
    const u = b.st.id === 'S' || b.st.id === 'L' ? 0 : b.st.kg; const kem = u && ingatStokKemasan()[kunciKemasan(b.merk, u)]; const kunci = kem ? AR.arKunciKemasan(b.merk, u) : AR.arKunciBeras(b.merk); const K = AR.arKeadaan(kunci);
    if (!K.nol && K.pernah) return h`<div class="ket" data-k="ar-ket" style="font-size: 11px;">${K.judul}: sisa ${K.sisaTeks} menurut buku — arsip hanya untuk barang yang sudah habis.</div>`;
    return h`<div class="pita-info" data-k="ar-${kunci}">${K.judul} ${K.nol ? 'habis' : 'bersisa ' + K.sisaTeks}${K.pernah ? '' : ' · belum pernah bertransaksi'} — mau diapakan?
      <div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="arIsi" data-kunci="${kunci}">Isi — ${K.jenis === 'kemasan' ? 'adukan' : 'barang masuk'}</div>${K.nol ? h`<div class="kaca-btn" data-aksi="arArsip" data-kunci="${kunci}">Arsipkan</div>` : ''}${K.bisaHapus ? h`<div class="kaca-btn ${s.arYakin === kunci ? 'awas' : 'putus'}" data-aksi="arHapus" data-kunci="${kunci}">${s.arYakin === kunci ? 'YAKIN hapus' : 'Hapus'}</div>` : ''}</div>
      <div class="ket" style="font-size: 10.5px;">Arsipkan = hilang dari Jual, katalog harga, label, dan katalog HP kasir; riwayat, laporan, buku stok tetap. ${K.bisaHapus ? 'Hapus = belum pernah ada transaksinya: harga & setelannya dibuang.' : 'Pernah bertransaksi — tidak bisa dihapus.'}</div></div>`;
  }
  function gambarProdukArsip(s) {
    const D = AR.arRingkas(); if (!D.length && !s.arBuka) return '';
    if (!s.arBuka) return h`<div class="kaca-btn kecil" data-aksi="arDaftarBuka" data-k="ar-pintu" style="align-self: flex-start;">Produk arsip · ${D.length} ›</div>`;
    return h`<div class="kartu" data-k="ar-daftar" style="gap: 6px;"><div class="kepala-lembar"><div><div class="label">Produk arsip · ${D.length}</div><div class="ket">tidak tampil di Jual, katalog, label, dan katalog HP kasir · riwayat & laporan tetap · barang masuk atas nama ini akan menanyakan "pulihkan atau varian"</div></div><div class="kaca-btn kecil" data-aksi="arDaftarBuka">tutup</div></div>
      ${D.length ? D.map((x) => h`<div data-k="ard-${x.kunci}" style="display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 6px 0; border-top: 1px solid var(--garis, rgba(255,255,255,.08));"><div style="display: flex; flex-direction: column; gap: 2px;"><b>${x.judul}</b><span class="ket">diarsipkan ${tanggalPendek(x.sejak)} · ${AR.arTeksSisa(x)}</span></div><div class="kaca-btn kecil" data-aksi="arPulih" data-kunci="${x.kunci}">pulihkan</div></div>`) : h`<div class="ket">Belum ada yang diarsipkan.</div>`}</div>`;
  }
  // putaran 27 (Bagian 2): varian baru sebelum barangnya datang
  function gambarVarianBaru(s, S) {
    const b = s.vrBaru; if (!b) return h`<div class="kaca-btn kecil" data-aksi="vrBaruBuka" data-k="vr-pintu" style="align-self: flex-start;">+ Varian merek baru (mutu / harga berbeda, nama sama) ›</div>`;
    const induk = b.induk ? S.baris.find((x) => x.merk === b.induk) : null; const modal = induk ? induk.modalKg : 0; const usul = VR.vrUsulHarga(modal, S.atur); const nama = b.induk ? VR.vrNama(b.induk, b.mutu || '…', '') : '';
    // owner 7 Okt: induk berstok → pilihan wajib (kalimat dihitung sekali per gambar: membaca buku induk)
    // nama varian yang SUDAH ADA dengan buku kosong + induk berstok (stok bercabang yang terlanjur) → hanya pindah stok, harga katalog tidak diubah
    const adaNama = !!(b.induk && b.mutu) && VR.vrAda(nama); const keAda = adaNama && VR.vrBisaIkutKeAda(b.induk, nama);
    // tinjauan E1: kalimat & sorotan hanya untuk pilihan yang TERSEDIA sekarang — "kosong" yang tertinggal dari nama mutu sebelumnya (lalu diganti ke varian yang
    // sudah ada, yang hanya punya "Ya — stok ikut") tidak digambar seolah masih berlaku
    const pilihSah = adaNama ? (b.bawa === 'bawa' ? 'bawa' : '') : (b.bawa === 'bawa' || b.bawa === 'kosong' ? b.bawa : '');
    const kalBawa = b.induk && (!adaNama || keAda) ? VR.vrKalimatBawa(b.induk, nama, '') : ''; const bawaTanya = !!kalBawa; const kalPilih = bawaTanya && pilihSah ? VR.vrKalimatBawa(b.induk, nama, pilihSah) : '';
    const siap = !!(b.induk && b.mutu) && (adaNama ? keAda && pilihSah === 'bawa' : (!bawaTanya || !!pilihSah));
    return h`<div class="kartu" data-k="vr-baru" style="gap: 8px;"><div class="kepala-lembar"><div><div class="label">Varian merek baru</div><div class="ket">barang berbeda dengan nama pemasok yang sama → nama sendiri "&lt;merek&gt; · &lt;mutu&gt;": stok, modal, harga, label, dan tempatnya sendiri; stok induk yang masih ada ditanyakan: ikut jadi varian, atau tetap</div></div><div class="kaca-btn kecil" data-aksi="vrBaruBuka">tutup</div></div>
      <div class="ket">Merek induk:</div><div class="jalur bungkus" data-k="vr-induk">${VR.vrCalonInduk(S.merk).map((m) => h`<div class="seg ${b.induk === m ? 'aktif' : ''}" data-aksi="vrInduk" data-merk="${m}" data-k="vri-${m}">${m}</div>`)}</div>
      <div class="ps-form dua"><div><div class="ket">Nama mutu (wajib, mis. Premium)</div><input class="ketik-nama" id="vrMutu" type="text" value="${b.mutu || ''}" data-ketik="vrKetikBaru" data-kolom="mutu"></div>
        <div><div class="ket">Harga jual per kg${usul ? ' · usul ' + RP(usul) : ''}</div><input class="ketik-nama" id="vrHarga" type="text" inputmode="numeric" placeholder="${usul || ''}" value="${b.harga || ''}" data-ketik="vrKetikBaru" data-kolom="harga"></div></div>
      ${bawaTanya ? h`<div class="pita-info ${pilihSah ? '' : 'emas'}" data-k="vr-bawa"><div>${kalBawa}</div>
        <div class="tombol-baris rapat" data-k="vr-bawa-pil"><div class="kaca-btn ${pilihSah === 'bawa' ? 'aktif emas' : ''}" data-aksi="vrBawa" data-v="bawa">Ya — stok ${b.induk} ikut jadi varian ini</div>${adaNama ? '' : h`<div class="kaca-btn ${b.bawa === 'kosong' ? 'aktif' : ''}" data-aksi="vrBawa" data-v="kosong">Bukan — varian kosong, untuk kedatangan berikutnya</div>`}</div>
        ${kalPilih ? h`<div class="ket">${kalPilih}</div>` : ''}</div>` : ''}
      ${adaNama ? h`<div class="ket"><b>${nama}</b> sudah ada${keAda ? ' (bukunya kosong) — tidak dibuat ulang, harganya tidak diubah; yang dipindah hanya stok ' + b.induk : ' — ubah harganya di katalog seperti biasa'}</div>` : b.induk ? h`<div class="ket">jadi <b>${nama}</b> · jenis beras ikut ${b.induk}: ${JB.jbJenisMerk(b.induk) || 'belum diisi'}${modal ? ' · usul = modal ' + b.induk + ' ' + RP(Math.round(modal)) + '/kg + target ' + RP(S.target) : ''} · ${bawaTanya && b.bawa === 'bawa' ? 'stoknya = stok ' + b.induk + ' yang ikut' : 'stoknya mulai dari barang masuk atas nama ini'}</div>` : ''}
      <div class="kaca-btn aktif emas ${siap ? '' : 'mati'}" data-aksi="vrBuat" data-usul="${usul}">${adaNama ? (keAda ? 'PINDAHKAN STOK ' + b.induk + ' KE ' + nama : nama + ' SUDAH ADA') : s.vrYakin ? 'YAKIN — terbitkan di bawah modal' : 'BUAT VARIAN & TERBITKAN HARGA PER KG'}</div></div>`;
  }
  function gambarJenisDaftar(s) {
    const D = JB.jbDaftar();
    return s.jbDaftar ? h`<div class="kartu" data-k="jb-daftar" style="gap: 6px;"><div class="kepala-lembar"><div class="label">Jenis beras · ${D.terisi}/${D.total} terisi</div><div class="kaca-btn kecil" data-aksi="jbDaftarBuka">tutup</div></div>
        <div class="jalur bungkus" data-k="jb-semua">${D.baris.map((b) => h`<div class="seg ${b.jenis ? '' : 'aktif'}" data-aksi="jbBuka" data-merk="${b.merk}" data-k="jbd-${b.merk}">${b.merk} · ${b.jenis || 'jenis?'}${b.asal === 'tebakan' ? ' (tebakan)' : ''}</div>`)}</div>
        <div class="ket" style="font-size: 11px;">Ketuk nama beras untuk memilih jenisnya. Nama muncul sendiri begitu ada di stok atau katalog. "(tebakan)" = ditebak dari namanya, belum pernah diisi.</div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="jbDaftarBuka" data-k="jb-pintu" style="align-self: flex-start;">Jenis beras · ${D.terisi}/${D.total} terisi ›</div>`;
  }
  // ---- KELAS MUTU (putaran 30) — lembar pilih kelas satu merek & daftar semua merek berbuku
  function gambarKelasUbah(s) {
    const m = s.kmUbah; const D = KM.kmDaftar().baris.find((b) => b.merk === m) || { kelas: '', asal: '', sendiri: false, wadah: false, varian: false };
    const calon = KM.kmCalonKelas().filter((c) => c.nama !== m);
    return h`<div class="kartu hg-ubah" data-k="km-ubah"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Kelas mutu · ${m}</div><div class="ket">Sekarang: ${D.wadah ? 'nama wadah — kelasnya dirinya sendiri' : D.sendiri ? 'KELAS tanpa wadah (buku atas nama ini)' : D.asal === 'dipakai' ? 'dipakai sebagai kelas merek lain' : D.kelas ? D.kelas + (D.asal === 'tebakan' ? ' (tebakan — belum dikonfirmasi owner)' : '') : D.asal === 'owner' ? 'tanpa kelas (pilihan owner)' : 'belum dipilih'}${D.petunjuk ? ' · jenis beras ' + D.petunjuk : ''}</div></div><div class="kaca-btn" data-aksi="kmTutup">tutup</div></div>
      ${D.wadah || D.sendiri ? '' : h`<div class="jalur bungkus" data-k="km-pilihan">${calon.map((c) => h`<div class="seg ${D.kelas === c.nama && D.asal !== 'tebakan' ? 'aktif' : ''}" data-aksi="kmPilih" data-kelas="${c.nama}" data-k="kmp-${c.nama}">${c.nama}${c.jenis === 'sendiri' ? ' · buku' : ''}</div>`)}</div>
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="kmPilih" data-kelas="">tanpa kelas — harga lalu dari merek ini saja</div>${D.varian ? '' : h`<div class="kaca-btn putus" data-aksi="kmSendiri" data-nama="${m}" data-nyala="1">nama ini KELAS, bukan merek</div>`}</div>`}
      ${D.sendiri ? h`<div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="kmSendiri" data-nama="${m}" data-nyala="0">lepas tanda kelas</div></div>` : ''}
      <div class="ket" style="font-size: 11px;">Kelas hanya lapisan baca: harga lalu di Barang masuk dan kartu Per kelas di Stok › HPP. Buku stok, modal, laba tidak berubah. Kelas tanpa wadah = kedatangan merek pemasok apa pun dibukukan atas nama kelas itu, merek pemasoknya dicatat.</div></div>`;
  }
  function gambarKelasDaftar(s) {
    const D = KM.kmDaftar();
    return s.kmDaftar ? h`<div class="kartu" data-k="km-daftar" style="gap: 6px;"><div class="kepala-lembar"><div class="label">Kelas mutu · ${D.terisi}/${D.total} terisi</div><div class="kaca-btn kecil" data-aksi="kmDaftarBuka">tutup</div></div>
        <div class="jalur bungkus" data-k="km-semua">${D.baris.map((b) => h`<div class="seg ${KM.kmTerisi(b.asal) ? '' : 'aktif'}" data-aksi="kmBuka" data-merk="${b.merk}" data-k="kmd-${b.merk}">${b.merk} · ${b.wadah ? 'wadah' : b.sendiri ? 'KELAS' : b.asal === 'dipakai' ? 'kelas' : b.kelas ? b.kelas : b.asal === 'owner' ? 'tanpa kelas' : 'kelas?'}${b.asal === 'tebakan' ? ' (tebakan)' : ''}${!b.kelas && !b.wadah && !b.sendiri && b.asal !== 'dipakai' && b.asal !== 'owner' && b.petunjuk ? ' · ' + b.petunjuk + '?' : ''}</div>`)}</div>
        ${D.usulSendiri.length ? h`<div class="ket" data-k="km-usul">Usulan KELAS tanpa wadah (literan langsung, bukunya atas nama ini): ${D.usulSendiri.map((n, i) => h`${i ? ' · ' : ''}<span class="tautan" data-aksi="kmSendiri" data-nama="${n}" data-nyala="1">${n}</span>`)} — ketuk untuk menandai.</div>` : ''}
        <div class="ket" style="font-size: 11px;">Ketuk merek untuk memilih kelasnya. "(tebakan)" = dari karung di belakang wadah / resep, belum dikonfirmasi owner; "kelas?" = belum ada petunjuk (jenis beras hanya petunjuk). Kelas mengikat harga lalu di Barang masuk dan kartu Per kelas — bukan buku stok.</div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="kmDaftarBuka" data-k="km-pintu" style="align-self: flex-start;">Kelas mutu · ${D.terisi}/${D.total} terisi ›</div>`;
  }
  // ---- paket brief 9 Okt (butir 8): HET BERAS — ringkasan menutup (5 bagian = semua baris katalog), daftar harga di atas HET, Atur setelan & pemetaan
  function gambarHet(s, HT) {
    const A = HT.atur; const bagian = [['atas', 'di atas HET'], ['dalam', 'sama / di bawah'], ['belum', 'belum dipetakan'], ['bukan', 'bukan beras HET'], ['kosong', 'belum ada harga']];
    return h`<div class="kartu het-kartu" data-k="het" style="gap: 6px;">
      <div class="kepala-lembar"><div><div class="label">HET beras · ${A.zona}</div><div class="ket">medium ${RP(A.medium)}/kg · premium ${RP(A.premium)}/kg — ${A.sumberTeks}</div></div><div class="kaca-btn kecil" data-aksi="hetBuka" data-k="het-pintu">${s.hetBuka ? 'tutup' : 'Atur HET ›'}</div></div>
      <div class="pita-info ${HT.nAtas ? 'awas' : HT.keadaan === 'lengkap' ? '' : 'emas'}" data-k="het-judul">${HT.judul}</div>
      ${HT.total ? h`<div class="hg-ringkas lima" data-k="het-ringkas">${bagian.map(([id, nm]) => h`<div class="${id === 'atas' && HT.hit.atas ? 'nyala' : ''}" data-k="hr-${id}"><span class="a">${HT.hit[id]}</span><span class="l">${nm}</span></div>`)}</div>` : ''}
      ${HT.atas.map((x) => h`<div class="het-baris" data-k="ha-${x.k}" data-aksi="hgUbah" data-kunci="${x.k}"><span>${x.judul}${x.adaDraf ? h`<span class="hg-cap draf">draf</span>` : ''}<br><span class="ket">${x.hargaTeks} · ${x.unit !== x.merk ? 'kelas ' + x.unit + ' · ' : ''}${x.kategori}</span></span><span class="awas-teks">${x.teks}</span></div>`)}
      <div class="ket" style="font-size: 11px;">${HT.rincian ? HT.rincian + ' ' : ''}Harga per kg = cara katalog menghitung: per kg apa adanya, kemasan & karung utuh ÷ ukurannya, literan ÷ kg per liter. Draf ikut dinilai; tanda HET memperingatkan, tidak menahan terbit — owner yang memutuskan.${HT.keadaan === 'belum' || HT.keadaan === 'sebagian' ? ' Kelas/merek yang belum dipetakan tidak dibandingkan (bukan berarti aman).' : ''}</div>
      ${s.hetBuka ? gambarAturHet(s, HT) : ''}</div>`;
  }
  // ---------- paket HPP & harga minimum (owner 26 Nov 2026 — A64 · A97 · A98): harga minimum tiap baris katalog + alarm modal + biaya dekat HET. Angka dari SH
  // (susut-harga-logika: hgSemua · biaya toko per kg Laporan › Biaya · HET apa adanya, dijaga uji_susut_harga.py). Memperingatkan, tidak menahan terbit.
  function gambarMinimum(s, S) {
    const M = SH.shMinimumKatalog(S, kini(), 'tampil'); const H = SH.shDekatHet(S, kini()); const A = M.atur; const B = M.biaya; const T = M.target; const n = s.minBuka ? 40 : 6;
    const atur = s.aturMin ? h`<div data-k="min-atur" style="display: flex; flex-direction: column; gap: 8px; margin-top: 4px;"><div class="ps-form tiga">
        <div data-k="mf-laba"><div class="ket">Target laba per kg (Rp) · 0 = harga minimum = impas</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturMin.targetLabaPerKg}" data-ketik="minKetik" data-kolom="targetLabaPerKg"></div>
        <div data-k="mf-het"><div class="ket">Alarm HET menyala kalau tinggal (Rp/kg)</div><input class="ketik-nama" type="text" inputmode="numeric" value="${s.aturMin.jarakHet}" data-ketik="minKetik" data-kolom="jarakHet"></div></div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="minAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="minSimpan">SIMPAN</div></div><div class="ket">Satu dokumen aturanToko/hargaMinimum, milik toko — tidak mengubah harga mana pun.</div></div>` : '';
    return h`<div class="kartu sh-minimum" data-k="minimum" style="gap: 6px;">
      <div class="kepala-lembar"><div><div class="label">Harga minimum & HET</div><div class="ket">${SH.SH_RUMUS_MINIMUM}</div></div><div class="kaca-btn kecil" data-aksi="minAtur" data-k="min-pintu">${s.aturMin ? 'tutup' : 'Atur ›'}</div></div>
      <div class="hg-ringkas" data-k="min-ringkas"><div class="${M.nBawah ? 'nyala' : ''}" data-k="mr-bawah"><span class="a">${M.keadaan === 'tanpaBiaya' ? '—' : M.nBawah}</span><span class="l">di bawah minimum</span></div><div class="${H.nDekat ? 'nyala' : ''}" data-k="mr-dekat"><span class="a">${H.keadaan === 'ada' ? H.nDekat : '—'}</span><span class="l">dekat HET</span></div><div class="${H.nLewat ? 'nyala' : ''}" data-k="mr-lewat"><span class="a">${H.keadaan === 'ada' ? H.nLewat : '—'}</span><span class="l">lewat HET</span></div><div data-k="mr-biaya"><span class="a">${B.perKg === null ? '—' : RP(Math.round(B.perKg))}</span><span class="l">biaya toko /kg</span></div></div>
      <div class="ket" data-k="min-biaya">${B.teks} Target laba ${RP(A.targetLabaPerKg)}/kg${A.dariOwner ? ' (owner)' : ' (bawaan: impas)'}. ${T.teks}</div>
      ${M.bawah.slice(0, n).map((x) => h`<div class="het-baris" data-k="mn-${x.k}" data-aksi="hgUbah" data-kunci="${x.k}"><span>${x.judul}${x.adaDraf ? h`<span class="hg-cap draf">draf</span>` : ''}<br><span class="ket">modal ${RP(Math.round(x.rinci.modal * x.kg))} + biaya ${RP(Math.round(x.rinci.biaya * x.kg))}${x.rinci.laba ? ' + laba ' + RP(Math.round(x.rinci.laba * x.kg)) : ''}${x.beras && x.rinci.susutPct ? ' · kalau susut ' + DESIMAL(x.rinci.susutPct) + ' % ikut: ' + RP(Math.ceil(x.rinci.minimumSusut * x.kg)) : ''}</span></span><span class="awas-teks">${RP(x.n)} &lt; ${RP(x.minimumBulat)}</span></div>`)}
      ${M.bawah.length > 6 ? h`<div class="kaca-btn kecil" data-aksi="minBuka" data-k="min-semua" style="align-self: flex-start;">${s.minBuka ? 'ringkas' : 'lihat semua ' + M.bawah.length}</div>` : ''}
      <div class="pita-info ${H.alarm.length ? 'awas' : H.keadaan === 'ada' ? '' : 'emas'}" data-k="min-het">${H.kalimat}</div>
      ${H.alarm.map((x) => h`<div class="het-baris" data-k="mh-${x.k}" data-aksi="hgUbah" data-kunci="${x.k}"><span>${x.merk}<br><span class="ket">${x.kategori} · HET ${RP(x.het)}/kg · modal ${RP(Math.round(x.rinci.modal))} + biaya ${RP(Math.round(x.rinci.biaya))}${x.rinci.susutPct ? ' · HPP layak jual ' + RP(Math.round(x.rinci.layak)) : ''}</span></span><span class="awas-teks">${x.status === 'lewat' ? 'LEWAT HET ' + RP(Math.round(-x.jarak)) : 'sisa ' + RP(Math.round(x.jarak))}/kg</span></div>`)}
      ${H.alarm.length ? h`<div class="ket" data-k="min-saran">Yang bisa dilakukan: ${H.saran.join(' · ')}. Menaikkan harga tidak bisa melewati HET.</div>` : ''}
      <div class="ket" style="font-size: 11px;">${SH.SH_RUMUS_LAYAK}. Tanda memperingatkan, tidak menahan terbit — owner yang memutuskan.</div>${atur}</div>`;
  }
  // A65 · A66: KALKULATOR SEBELUM BELI — SH.shHitungBeli (tidak menulis apa pun; ketikan hilang saat ganti orang)
  function gambarHitungBeli(s) {
    const a = s.hb || {}; const bk = HG.aturHarga().bongkarKg; const X = SH.shHitungBeli(a, kini(), bk); const kol = (k, nm, ph) => h`<div data-k="hbf-${k}"><div class="ket">${nm}</div><input class="ketik-nama" type="text" inputmode="decimal" placeholder="${ph}" value="${a[k] || ''}" data-ketik="hbKetik" data-kolom="${k}"></div>`;
    const rp = (n) => (n === null || n === undefined ? '—' : (n < 0 ? '−' : '') + RP(Math.round(Math.abs(n)))); const kgT = (n) => (Math.abs(n % 1) > 0.004 ? DESIMAL(n) : ANGKA(Math.round(n))) + ' kg'; const plus = (n) => (n !== null && n !== undefined && n >= 0 ? '+' : '') + rp(n); const tanda = (n) => (n === null || n === undefined ? '' : n < -0.5 ? 'awas-teks' : '');
    const brs = (k, nm, n, ket, kelas) => h`<div class="hg-dua-kolom" data-k="hb-${k}"><span>${nm}${ket ? h`<br><span class="ket">${ket}</span>` : ''}</span><span class="n ${kelas || ''}">${n}</span></div>`;
    return h`<div class="kartu sh-hitung" data-k="hitung-beli" style="gap: 6px;"><div class="kepala-lembar"><div><div class="label">Hitung sebelum beli</div><div class="ket">Cuma hitungan — tidak menulis apa pun. Modal per kg dibagi kg TIMBANG kalau diisi (stok ikut timbang).</div></div>${s.hb ? h`<div class="kaca-btn kecil" data-aksi="hbBersih">kosongkan</div>` : ''}</div>
      <div class="ps-form tiga">${kol('hargaKg', 'Harga beli per kg (Rp)', 'mis. 12.500')}${kol('jumlahKarung', 'Jumlah karung', 'mis. 100')}${kol('isiKarung', 'Isi karung di nota (kg)', '50')}${kol('timbangKarung', 'Rata-rata timbang per karung (kg)', 'kosong = isi nota')}${kol('bongkarKg', 'Bongkar per kg (Rp)', bk ? String(bk) + ' (terukur)' : '0')}${kol('ongkir', 'Ongkos kirim supir (Rp seluruh muatan)', '0')}${kol('susut', 'Susut gudang (%)', (() => { const T = SH.shTarget(kini()); return T.pct !== null ? DESIMAL(Math.round(T.pct * 10) / 10) + ' (target)' : 'kosong = target'; })())}${kol('hargaJual', 'Harga jual rencana per kg (Rp)', 'boleh kosong')}</div>
      <div class="jalur rapat" data-k="hb-kelas">${[['medium', 'HET medium'], ['premium', 'HET premium']].map(([id, nm]) => h`<div class="seg ${a.kelas === id ? 'aktif' : ''}" data-aksi="hbKelas" data-kelas="${id}" data-k="hbk-${id}">${nm}</div>`)}</div>
      ${!X.siap ? h`<div class="ket" data-k="hb-belum">${X.kalimat}</div>` : h`<div data-k="hb-hasil" class="sh-hasil">
        ${brs('nota', 'Nilai nota', RP(Math.round(X.nilaiNota)), kgT(X.kgNota) + ' × harga')}${brs('datang', '+ Bongkar & ongkir', RP(Math.round(X.bongkar + X.ongkir)), 'bongkar ' + RP(Math.round(X.bongkarKg)) + '/kg')}
        ${brs('modal', 'Modal per kg sampai toko', RP(Math.round(X.modalKg)), X.ditimbang ? 'dibagi ' + kgT(X.kgBuku) + ' timbang' + (X.kurangKg > 0.004 ? ' (kurang ' + kgT(X.kurangKg) + ' dari nota)' : X.kurangKg < -0.004 ? ' (lebih ' + kgT(-X.kurangKg) + ' dari nota)' : '') : 'dibagi kg nota', 'emas-teks')}
        ${brs('karung', 'Modal per karung', RP(Math.round(X.perKarung)), DESIMAL(X.isiKarung) + ' kg per karung' + (X.ditimbang ? ' (timbang)' : ''))}
        ${brs('layak', 'HPP layak jual', RP(Math.round(X.layak)), 'kalau susut ' + DESIMAL(X.susutPct) + ' % ikut ditanggung')}
        ${brs('impas', 'Impas per kg', rp(X.impas), X.biayaKg === null ? 'biaya toko belum bisa dihitung' : '+ biaya toko ' + RP(Math.round(X.biayaKg)) + '/kg · ' + rp(X.impasSusut) + ' kalau susut ikut')}
        ${X.minimum !== null && X.labaKg ? brs('minimum', 'Harga minimum', rp(X.minimum), '+ target laba ' + RP(X.labaKg) + '/kg') : ''}
        ${X.het !== null ? brs('het', 'Dijual tepat HET ' + X.kelas + ' ' + RP(X.het) + '/kg', plus(X.untungHet) + '/kg', 'seluruh muatan ' + plus(X.untungHetTotal) + ' · kalau susut ikut: ' + plus(X.untungHetSusut) + '/kg', tanda(X.untungHet)) : ''}
        ${X.hargaJual !== null ? brs('jual', 'Dijual ' + RP(X.hargaJual) + '/kg', plus(X.untungJual) + '/kg', 'seluruh muatan ' + plus(X.untungJualTotal) + ' · kalau susut ikut: ' + plus(X.untungJualSusut) + '/kg', tanda(X.untungJual)) : ''}
        <div class="ket" data-k="hb-kalimat">${X.kalimat}</div></div>`}</div>`;
  }
  function gambarAturHet(s, HT) {
    const A = HT.atur; const a = s.aturHet || { zona: A.zona, medium: String(A.medium), premium: String(A.premium), sumber: A.sumber };
    const isian = [['zona', 'Zona', 'text'], ['medium', 'HET medium per kg (Rp)', 'numeric'], ['premium', 'HET premium per kg (Rp)', 'numeric'], ['sumber', 'Sumber angka (mis. nomor keputusan)', 'text']];
    const anggota = (u) => { const lain = u.anggota.filter((m) => m !== u.unit); return lain.length ? ' · ' + lain.join(', ') : ''; };
    return h`<div data-k="het-atur" style="display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
      <div class="label">Setelan HET · ${A.angkaOwner ? 'diatur owner' : 'angka bawaan'}</div>
      <div class="ps-form tiga">${isian.map(([k, nm, mode]) => h`<div data-k="hs-${k}"><div class="ket">${nm}</div><input class="ketik-nama" type="text" inputmode="${mode}" value="${a[k] === undefined ? '' : a[k]}" data-ketik="hetKetik" data-kolom="${k}"></div>`)}</div>
      <div class="ket">Angka bawaan dari dokumen owner (${HET.HET_BAWAAN.sumber}, ${HET.HET_BAWAAN.zona}): medium ${RP(HET.HET_BAWAAN.medium)}/kg, premium ${RP(HET.HET_BAWAAN.premium)}/kg. Ganti kalau aturannya berubah atau zonanya beda — tanda di katalog langsung ikut.</div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="hetBuka">batal</div><div class="kaca-btn aktif emas" data-aksi="hetSimpan">SIMPAN SETELAN HET</div></div>
      <div class="label" style="margin-top: 6px;">Pemetaan · ${HT.units.length - HT.unitBelum.length}/${HT.units.length} kelas/merek</div>
      <div class="ket">Tiap kelas toko dan merek tanpa kelas di katalog: premium, medium, atau bukan beras HET (ketan, beras khusus, …). Ketuk pilihan yang menyala untuk melepasnya. Kelas sebuah merek = kelas mutu yang sudah dikonfirmasi (Kelas mutu ›).</div>
      ${HT.units.map((u) => h`<div class="het-unit" data-k="hu-${u.unit}"><div style="min-width: 0;"><b>${u.unit}</b><br><span class="ket">${u.jenisTeks}${anggota(u)}${u.tebakan ? ' · kelas tebakan ' + u.tebakan + ' belum dikonfirmasi' : ''} · ${u.nBaris} harga${u.nAtas ? ' · ' + u.nAtas + ' di atas HET' : ''}</span></div>
        <div class="jalur rapat">${HET.HET_KATEGORI.map(([id, nm]) => h`<div class="seg ${u.kategori === id ? 'aktif' : ''}" data-aksi="hetPeta" data-unit="${u.unit}" data-kat="${u.kategori === id ? '' : id}" data-k="hp-${u.unit}-${id}">${nm}</div>`)}</div></div>`)}
      ${HT.tidakDipakai.length ? h`<div class="ket" data-k="het-yatim">Pemetaan yang tidak punya baris katalog lagi (nama berganti / diarsipkan): ${HT.tidakDipakai.map((u, i) => h`${i ? ' · ' : ''}<span class="tautan" data-aksi="hetPeta" data-unit="${u}" data-kat="">${u} (${A.peta[u]}) — lepas</span>`)}</div>` : ''}</div>`;
  }
  // paket KPI laba (owner 24 Nov 2026, butir 4 · 5): SARAN harga dari target margin per jenis — modal ÷ (1 − target), mark-up selalu di samping margin.
  // Hanya saran: ketuk "pakai saran" mengisi kotak ketik (jadi draf kalau lu simpan); harga tidak pernah berubah sendiri. Angka dari KL.klSaranBaris.
  function gambarSaran(b, S) {
    const T = KL.klTargetMargin(kini()); const X = KL.klSaranBaris(b, T, S); const P = KL.klPctTeks;
    if (X.tanpaModal) return h`<div class="ket" data-k="saran">Saran harga belum bisa — modalnya belum tercatat.</div>`;
    return h`<div class="hg-saran" data-k="saran"><div class="label">Margin & saran dari target</div>
      <div class="ket" data-k="saran-kini">Harga sekarang: margin ${P(X.pctKini)} · mark-up ${P(X.markupKini)} (modal ${RP(Math.round(X.modal))} per ${b.st.per})</div>
      ${X.saran.map((x) => h`<div class="hg-saran-baris" data-k="saran-${x.jenis}"><div><b>${x.nama}</b><div class="ket">target ${P(x.target)} (${x.dariOwner ? 'owner' : 'bawaan: margin 3 bulan'}) · mark-up ${P(x.markup)}${x.karungUtuh ? ' · karung 50 kg ' + RP(x.karungUtuh) : ''}</div></div>
        ${x.harga !== null ? h`<div class="kaca-btn kecil ${x.beda > 0 ? 'aktif' : ''}" data-aksi="hgIsi" data-n="${x.harga}"><span>pakai saran</span> <b>${RP(x.harga)}</b></div>` : h`<span class="ket">target belum ada</span>`}</div>`)}
      <div class="ket">Saran = modal ÷ (1 − target margin), dibulatkan ke atas seperti usul. Hanya saran — harga baru berlaku sesudah lu simpan & terbitkan.</div></div>`;
  }
  // paket KPI laba (butir 4 · 5): kartu target margin per jenis — bawaan = margin terwujud 3 bulan dari mesin (supaya tidak menyalakan alarm), owner bisa mengubah
  function gambarTargetMargin(s) {
    const T = KL.klTargetMargin(kini()); const P = KL.klPctTeks; const a = s.aturTm;
    return h`<div class="kartu" data-k="target-margin" style="gap: 6px;"><div class="label">Target margin per jenis · dasar saran harga</div>
      ${KL.KL_JENIS.map((j) => { const x = T.jenis[j.id]; return h`<div class="hg-dua-kolom" data-k="tm-${j.id}"><span>${j.nama}<br><span class="ket">${x.dariOwner ? 'diatur owner · ' + x.bawaanTeks : 'bawaan · ' + x.bawaanTeks}</span></span><span class="n">${P(x.pct)}<br><span class="ket">mark-up ${P(KL.klMarkup(x.pct))}</span></span></div>`; })}
      <div class="ket" data-k="tm-bps">Pembanding ${KL.KL_BPS.pendek}: pedagang besar ${P(KL.KL_BPS.grosir)} · pedagang eceran ${P(KL.KL_BPS.eceran)} — konteks, bukan target. Sumber: ${KL.KL_BPS.sumber}.</div>
      ${a ? h`<div class="ps-form tiga" data-k="tm-form">${KL.KL_JENIS.map((j) => h`<div data-k="tmf-${j.id}"><div class="ket">${j.nama} (%) · kosong = bawaan</div><input class="ketik-nama" type="text" inputmode="decimal" placeholder="${P(T.jenis[j.id].bawaan)}" value="${a[j.id] || ''}" data-ketik="tmKetik" data-jenis="${j.id}"></div>`)}</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="tmBuka">batal</div><div class="kaca-btn aktif emas" data-aksi="tmSimpan">SIMPAN TARGET</div></div>`
        : h`<div class="kaca-btn kecil" data-aksi="tmBuka" style="align-self: flex-start;">Atur target margin per jenis ›</div>`}</div>`;
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
      ${s.bayar ? gambarBayar(s, B) : ''}${s.lama ? gambarBonLama(s) : ''}${s.kartu ? gambarKartu(s) : ''}${s.betul ? gambarBetul(s) : ''}${urung}
      ${L === 'mac' ? h`<div class="hg-grid mac tiga" data-k="grid-bon"><div class="hg-kolom" data-k="k1">${gambarTusukan(s, B)}</div><div class="hg-kolom" data-k="k2">${gambarGaris(B)}</div><div class="hg-kolom" data-k="k3">${gambarBuku(s, B)}</div></div>`
        : L === 'tablet' ? h`<div class="hg-grid tablet" data-k="grid-bon"><div class="hg-kolom" data-k="k1">${gambarTusukan(s, B)}</div><div class="hg-kolom" data-k="k2">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabB')}${panel(tab)}</div></div>`
        : h`<div class="hg-kolom" data-k="grid-bon">${tabBaris(tabAda.map(([id, nm]) => [id, nama(id, nm)]), tab, 'tabB')}${panel(tab)}</div>`}
      ${gambarHariBayar()}
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="bpLamaBuka">＋ Catat bon lama (sebelum sistem)</div>${gambarAturB(s, B)}</div>
      <div class="ket" style="font-size: 11px;">Sisa bon = nilai − yang sudah dibayar (mesin yang sama dengan sistem lama); bon yang dibayar sebagian TETAP di daftar. Satu pembayaran = satu bon; bon tertua cuma saran — lu yang memilih. Jatuh tempo = tanggal barang datang + tempo di kartu pemasok (atau tempo umum di Atur Barang masuk) — ramalan, bukan janji tertulis. Membayar bon tidak mengubah laba; biaya admin transfer masuk biaya toko.</div>
    </section>`;
  }
  // paket KPI laba (owner 24 Nov 2026, butir 13): rata-rata hari bayar bon pemasok — per pemasok & total, dari pembayaran yang MENUNJUK bonnya (BP.bpHariBayar)
  function gambarHariBayar() {
    const R = BP.bpHariBayar(kini()); const maks = Math.max(1, ...R.pemasok.map((p) => p.rataHari || 0));
    return h`<div class="kartu" data-k="hari-bayar" style="gap: 4px;"><div class="label">Rata-rata hari bayar pemasok · ${R.hari} hari terakhir</div>
      <div style="font-weight: 600;" data-k="hb-total">${R.teks}</div>
      ${R.pemasok.map((p) => h`<div class="hg-dua-kolom" data-k="hb-${p.kunci}"><span>${p.nama}<br><span class="ket">${p.n} pembayaran · ${RP(p.rp)}</span><span class="hg-pita-hari"><i style="width: ${Math.max(0, Math.min(100, (p.rataHari || 0) / maks * 100)).toFixed(1)}%;"></i></span></span><span class="n">${BP.bpHariTeks(p.rataHari)}</span></div>`)}
      ${R.sebab.length ? h`<div class="ket" data-k="hb-sebab">Tidak dihitung: ${R.sebab.join(' · ')}.</div>` : ''}
      <div class="ket">Hari = tanggal bayar − tanggal bon (barang datang), ditimbang rupiah. Dipakai juga di siklus uang Dasbor.</div></div>`;
  }
  const bonSlip = (b, i, kelas) => h`<div class="bn-tusuk" data-k="slip-${b.id}"><div class="bn-slip ${i % 2 ? 'genap' : ''} ${b.jenis === 'saldoAwal' ? 'lama' : ''} ${kelas || ''}" data-aksi="bpBayarBuka" data-pemasok="${b.pemasok}" data-bon="${b.id}"><div><div class="tg">Bon ${b.gulir || b.tanggal ? tanggalPendek(b.gulir || b.tanggal) : '(tanpa tanggal)'}${b.cap ? h`<span class="bn-cap ${b.jenis === 'saldoAwal' ? 'redup' : ''}">${b.cap}</span>` : ''}${b.saran ? h`<span class="bn-cap saran">saran: ini dulu</span>` : ''}<span class="bn-cap betul" data-aksi="bpBetulBuka" data-pemasok="${b.pemasok}" data-bon="${b.id}">${b.noBon ? 'No. ' + b.noBon + ' · ' : ''}betulkan · foto</span></div><div class="kt">${b.ket}</div><div class="kt ${b.status === 'lewat' ? 'awas' : ''}">${b.tempoTeks}</div>${b.isi ? h`<div class="kt">${b.isi}</div>` : ''}</div><div class="n">${RP(b.sisa)}</div></div></div>`;
  function gambarTusukan(s, B) {
    return h`<div class="kartu" data-k="tusukan" style="gap: 0; padding-top: 4px;">${B.tusukan.length ? B.tusukan.map((t) => h`<div data-k="tk-${t.pemasok}"><div class="bn-kepala" data-aksi="bpKartuBuka" data-nama="${t.pemasok}"><div><div class="nm">${t.pemasok}</div><div class="ket">${t.bon.length} bon · ${t.tempo.teks} · kartu ›</div></div><div class="n">${RP(t.total)}</div></div>
        ${t.bon.map((b, i) => bonSlip(b, i))}${t.tekor ? h`<div class="pita-info awas" style="margin: 6px 0;">Kelebihan bayar ${RP(t.tekor)} — ada kedatangan yang bonnya belum masuk buku.</div>` : ''}<div class="bn-dasar"></div></div>`) : h`<div class="menolak" style="padding: 10px 0;">Tidak ada bon yang masih terbuka.</div>`}
      <div class="ket" style="padding-top: 6px;">Ketuk kertas bonnya untuk membayar. Ketuk nama pemasok untuk kartunya (orang, nomor, tempo).</div></div>`;
  }
  function gambarGaris(B) {
    return h`<div class="hg-kolom" data-k="garis"><div class="hg-ringkas tiga" data-k="ringkas-bon">${B.ringkas.map((r, i) => h`<div class="${r.nyala ? 'nyala' : ''}" data-k="rb-${i}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      <div class="pita-info ${B.kurang ? 'awas' : ''}">${B.cukupTeks}</div>
      <div class="kartu" style="gap: 0;"><div class="bn-garis">${B.garis.length ? B.garis.map((g, i) => (g.tanda ? h`<div class="bn-tanda ${g.kelas}" data-k="gt-${i}">${g.teks}</div>` : h`<div class="bn-titik ${g.status}" data-k="gb-${g.id}" data-aksi="bpBayarBuka" data-pemasok="${g.pemasok}" data-bon="${g.id}"><div><div>${g.pemasok} · Bon ${g.gulir || g.tanggal ? tanggalPendek(g.gulir || g.tanggal) : '(tanpa tanggal)'}${g.cap ? h`<span class="bn-cap ${g.jenis === 'saldoAwal' ? 'redup' : ''}">${g.cap}</span>` : ''}</div><div class="ket ${g.status === 'lewat' ? 'awas-teks' : ''}">${g.tempoTeks}</div></div><div class="n">${RP(g.sisa)}</div></div>`)) : h`<div class="menolak" style="padding: 10px 0;">Tidak ada bon yang masih terbuka.</div>`}</div></div>
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
      ${terbuka.length ? h`<div class="utama" data-aksi="bpBayarBuka" data-pemasok="${nm}">BAYAR BON ${nm}</div>` : ''}
      ${nm ? gambarSemuaBon(nm) : ''}</div>`;
  }
  // owner 7 Okt: tiap bon pemasok ini satu baris — yang LUNAS juga (pembayaran yang salah tunjuk sering melunasi bon yang keliru) — pintu Betulkan & Foto
  function gambarSemuaBon(nm) {
    const semua = BP.bpSemuaBon(nm); if (!semua.length) return '';
    return h`<div class="kartu" data-k="semua-bon" style="gap: 0;"><div class="label" style="padding-bottom: 4px;">Semua bon ${nm} · betulkan & foto</div>
      ${semua.slice().reverse().map((b) => h`<div class="bn-semua" data-k="sb-${b.id}" data-aksi="bpBetulBuka" data-pemasok="${nm}" data-bon="${b.id}"><span class="ket">${b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tgl'}</span><span>${b.noBon ? 'No. ' + b.noBon : h`<span class="ket">nomor belum dicatat</span>`}${b.jenis === 'saldoAwal' ? ' · bon lama' : ''}${b.riwayat.length || b.bayar.some((m) => m.alasanKoreksi) ? ' · dibetulkan' : ''}<br><span class="ket">${RP(b.nilai)} · ${b.sisa > 0 ? 'sisa ' + RP(b.sisa) : 'LUNAS'} · ${b.bayar.length} pembayaran</span></span><span class="n">betulkan ›</span></div>`)}</div>`;
  }
  // ---- owner 7 Okt: LEMBAR BETULKAN BON (pembetulan berjejak, owner saja) + FOTO BON
  function gambarBetul(s) {
    const d = s.betul; const R = BP.bpRincianBon(d.bonId, d.pemasok); const b = R.bon;
    if (!b) return h`<div class="kartu hg-lembar" data-k="betul"><div class="ket">Bon itu sudah tidak ada.</div><div class="kaca-btn" data-aksi="bpBetulTutup">tutup</div></div>`;
    const m = d.bayarId ? b.bayar.find((x) => String(x.id) === d.bayarId) || null : null;
    const H = m && d.mode === 'pindah' ? BP.hitungPindahBayar(m.id, d.keBon) : m && d.mode === 'nominal' ? BP.hitungNominalBayar(m.id, d.ketik) : null;
    const Hl = b.jenis === 'saldoAwal' && (d.tgl !== (b.tanggal || '') || String(d.lama) !== String(b.nilai)) ? BP.hitungBetulBonLama(b.id, { tgl: d.tgl, ketik: d.lama }) : null;
    const alasanIsian = (id) => h`<input class="ketik-nama" id="${id}" type="text" placeholder="Alasan (wajib) — mis. kata pemasok / nomor di kertas bon" value="${d.alasan}" data-ketik="bpBetulKetik" data-kolom="alasan">`;
    const baris = (x) => h`<div class="bn-semua tetap" data-k="by-${x.id}"><span class="ket">${tanggalPendek(x.tanggal)}${x.jam ? ' ' + x.jam : ''}</span><span>${RP(x.nominal || 0)}<br><span class="ket">${x.dari ? 'dari ' + x.dari : 'kantong tidak dicatat'}${x.alasanKoreksi ? ' · dibetulkan: ' + ((x.riwayat || []).slice(-1)[0] || {}).teks : ''}</span></span><span class="n"><span class="kaca-btn kecil ${d.bayarId === String(x.id) && d.mode === 'pindah' ? 'aktif' : ''}" data-aksi="bpBetulBayar" data-id="${x.id}" data-mode="pindah">pindah ke bon lain</span> <span class="kaca-btn kecil ${d.bayarId === String(x.id) && d.mode === 'nominal' ? 'aktif' : ''}" data-aksi="bpBetulBayar" data-id="${x.id}" data-mode="nominal">betulkan jumlah</span></span></div>`;
    return h`<div class="kartu hg-lembar" data-k="betul" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Betulkan ${b.label} · ${d.pemasok}</div><div class="ket">nilai ${RP(b.nilai)} · dibayar ${RP(b.dibayar)} · ${b.sisa > 0 ? 'sisa ' + RP(b.sisa) : 'LUNAS'}${b.isi ? ' · ' + b.isi : ''}</div></div><div class="kaca-btn kecil" data-aksi="bpBetulTutup">×</div></div>
      <div class="pita-info">Owner saja. Tiap pembetulan menulis ulang catatan yang sama dengan JEJAK (nilai lama, tanggal, jam, alasan) — tidak menimpa diam-diam. Bulan yang sudah dikunci ditolak.</div>
      <div class="label">Pembayaran yang menunjuk bon ini</div>
      ${b.bayar.length ? b.bayar.map(baris) : h`<div class="ket">Belum ada pembayaran yang menunjuk bon ini.${R.tanpaTunjuk.length ? ' ' + R.tanpaTunjuk.length + ' pembayaran ' + d.pemasok + ' tidak menunjuk bon yang ada — mengalir ke bon tertua.' : ''}</div>`}
      ${m && d.mode === 'pindah' ? h`<div class="jalur bungkus" data-k="pilih-ke">${R.semua.filter((x) => x.id !== b.id).map((x) => h`<div class="seg ${d.keBon === x.id ? 'aktif' : ''}" data-aksi="bpBetulKe" data-bon="${x.id}" data-k="ke-${x.id}">${x.label} · ${x.sisa > 0 ? 'sisa ' + RP(x.sisa) : 'lunas'}</div>`)}</div>
        <div class="pita-info ${H && H.tolak ? 'awas' : 'emas'}" data-k="arti-pindah">${H ? H.tolak || H.arti : ''}</div>${alasanIsian('bpBetulAlasanP')}
        <div class="utama ${!H || H.tolak ? 'redup' : ''}" data-aksi="bpBetulPindah">PINDAHKAN PEMBAYARAN ${RP(m.nominal || 0)}</div>` : ''}
      ${m && d.mode === 'nominal' ? h`<div class="hg-ketik-baris"><input class="ketik-nama" id="bpBetulKetik" type="text" inputmode="numeric" placeholder="jumlah yang sebenarnya dibayar" value="${d.ketik}" data-ketik="bpBetulKetik" data-kolom="ketik"></div>
        <div class="pita-info ${H && H.tolak ? 'awas' : 'emas'}" data-k="arti-nominal">${H ? H.tolak || H.arti : ''}</div>${alasanIsian('bpBetulAlasanN')}
        ${H && !H.tolak && H.besar.length ? h`<div class="pita-info awas" data-k="besar-nominal">${H.besarTeks}. Ketukan kedua yang menyimpan.</div>` : ''}
        <div class="utama ${!H || H.tolak ? 'redup' : ''}" data-aksi="bpBetulNominal">${H && !H.tolak && H.besar.length && d.yakinN === String(d.ketik) ? 'YAKIN — ' + RP(H.lama) + ' → ' + RP(H.n) : 'BETULKAN JUMLAH PEMBAYARAN'}</div>` : ''}
      ${b.dipindahDari.length ? h`<div class="ket" data-k="dipindah">Dulu menunjuk bon ini, sudah dipindah: ${b.dipindahDari.map((x) => tanggalPendek(x.tanggal) + ' ' + RP(x.nominal || 0) + ' → ' + (((x.riwayat || []).filter((r) => r && r.jenis === 'pindahBon').slice(-1)[0] || {}).teks || '')).join(' · ')}</div>` : ''}
      <div class="label">Nomor bon pemasok</div>
      <div class="hg-ketik-baris"><input class="ketik-nama" id="bpBetulNo" type="text" placeholder="nomor di kertas bon (mis. 12345)" value="${d.no}" data-ketik="bpBetulKetik" data-kolom="no"><div class="kaca-btn ${d.no && d.no !== b.noBon ? 'aktif emas' : ''}" data-aksi="bpBetulNo">${b.noBon ? 'ganti nomor' : 'simpan nomor'}</div></div>
      ${b.noBon && d.no !== b.noBon ? alasanIsian('bpBetulAlasanNo') : ''}
      <div class="label">Tanggal & nilai bon</div>
      ${b.jenis === 'saldoAwal' ? h`<div class="ps-form dua"><div><div class="ket">Nilai bon (Rp)</div><input class="ketik-nama" id="bpBetulLama" type="text" inputmode="numeric" value="${d.lama}" data-ketik="bpBetulKetik" data-kolom="lama"></div><div><div class="ket">Tanggal bon (kosong = tidak diketahui)</div><input class="ketik-nama" id="bpBetulTgl" type="date" value="${d.tgl}" data-ketik="bpBetulKetik" data-kolom="tgl"></div></div>
        ${Hl ? h`<div class="pita-info ${Hl.tolak ? 'awas' : 'emas'}" data-k="arti-lama">${Hl.tolak || Hl.arti}</div>${alasanIsian('bpBetulAlasanL')}<div class="utama ${Hl.tolak ? 'redup' : ''}" data-aksi="bpBetulLama">BETULKAN BON LAMA</div>` : ''}`
        : h`<div class="ket">Tanggal & nilai bon kedatangan = tanggal & harga barangnya — dibetulkan lewat Stok › Barang masuk › Buku kedatangan › koreksi (stok, modal, dan bonnya ikut).${b.bayar.length ? ' Bon ini sudah dibayar, jadi koreksi tanggal / nilai di bawah yang dibayar terkunci — pindahkan dulu pembayarannya di atas kalau memang salah tunjuk.' : ''}</div><div class="kaca-btn" data-aksi="bpKeKoreksiMasuk">Buka Barang masuk ›</div>`}
      ${b.riwayat.length ? h`<div class="label">Riwayat bon ini</div>${b.riwayat.slice(-8).reverse().map((r, i) => h`<div class="ket" data-k="rw-${i}">${r.tanggal ? tanggalPendek(r.tanggal) : ''}${r.jam ? ' ' + r.jam : ''} · ${r.teks || ''}</div>`)}` : ''}
      ${gambarFoto(s, b)}</div>`;
  }
  function gambarFoto(s, b) {
    const F = s.foto && s.foto.idBon === b.id ? s.foto : { muat: 'belum', daftar: [], pesan: '' }; const daftar = FB.fbnUrut(F.daftar, b.id); const besar = F.besar ? daftar.find((x) => String(x.id) === String(F.besar)) : null;
    const nAntre = daftar.filter((x) => x.antre).length; const tahan = !!F.proses || fotoAntre >= FB.FBN_ANTRE_MAKS;
    const status = F.muat === 'muat' ? 'Memuat foto bon ini…' : F.muat === 'galat' ? F.pesan : (daftar.length ? daftar.length + ' foto' + (nAntre ? ' (' + nAntre + ' BELUM sampai server)' : '') : 'Belum ada foto kertas bon ini') + (F.pesan ? ' · ' + F.pesan : '');
    return h`<div class="kartu fb-kartu" data-k="foto-bon" style="gap: 6px;"><div class="label">Foto kertas bon</div><div class="ket ${F.muat === 'galat' ? 'awas-teks' : ''}">${status}</div>
      <div class="tombol-baris rapat"><div class="kaca-btn ${tahan ? 'mati' : 'aktif'}" data-aksi="fotoAmbil" data-cara="kamera">${F.proses ? 'Memproses foto…' : 'Ambil foto'}</div><div class="kaca-btn ${tahan ? 'mati' : ''}" data-aksi="fotoAmbil" data-cara="galeri">Pilih dari galeri</div></div>
      <input id="fotoBonKamera" class="fb-berkas" type="file" accept="image/*" capture="environment" data-foto-pilih="kamera" hidden>
      <input id="fotoBonGaleri" class="fb-berkas" type="file" accept="image/*" multiple data-foto-pilih="galeri" hidden>
      <div class="ket" style="font-size: 10.5px;">Dikecilkan di HP ini dulu (sisi panjang ≤ ${FB.FBN_SISI} px, ±${FB.fbnKB(FB.FBN_TARGET)}), paling banyak ${FB.FBN_PALING_BANYAK} foto per bon. Foto dibaca hanya saat bon ini dibuka — tidak ikut dimuat tiap hari; yang pernah dibuka tersimpan sementara di cache Firestore perangkat ini.</div>
      ${besar ? h`<div class="fb-besar" data-k="fb-besar" data-aksi="fotoBesar" data-id="${besar.id}"><img src="${FB.fbnSrc(besar)}" alt="Foto bon besar"><div class="ket">ketuk untuk menutup</div></div>` : ''}
      ${daftar.length ? h`<div class="fb-kisi" data-k="fb-kisi">${daftar.map((f) => h`<div class="fb-foto" data-k="fb-${f.id}"><img src="${FB.fbnSrc(f)}" alt="Foto bon" data-aksi="fotoBesar" data-id="${f.id}"><div class="ket ${f.antre ? 'awas-teks' : ''}">${f.antre ? 'BELUM sampai server' : (f.tanggal ? tanggalPendek(f.tanggal) : '') + ' ' + (f.jam || '')} · ${FB.fbnKB(f.byte)}${f.oleh ? ' · ' + f.oleh : ''}</div><div class="kaca-btn kecil ${F.yakinHapus === String(f.id) ? 'awas' : ''}" data-aksi="fotoHapus" data-id="${f.id}">${F.yakinHapus === String(f.id) ? 'YAKIN hapus' : 'hapus'}</div></div>`)}</div>` : ''}
      </div>`;
  }
  function gambarBayar(s, B) {
    const S = saldoKantong(); const H = BP.hitungBayar(s.bayar, kini(), S); const d = s.bayar; const isiK = (id) => (S.ada ? RP(S[id]).replace('Rp', '') : '—');
    return h`<div class="kartu hg-lembar" data-k="bayar" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Bayar bon ${d.pemasok}</div><div class="ket">satu pembayaran = satu bon · pilih bonnya, ketik yang dibayar, tunai atau transfer</div></div><div class="kaca-btn" data-aksi="bpTutup">tutup</div></div>
      <div class="jalur bungkus" data-k="pilih-bon">${H.bonP.map((b) => h`<div class="seg ${b.id === d.bonId ? 'aktif' : ''}" data-aksi="bpBayarBon" data-bon="${b.id}" data-k="pb-${b.id}">${b.tanggal ? tanggalPendek(b.tanggal) : 'tanpa tgl'} · ${RP(b.sisa).replace('Rp', '')}</div>`)}</div>
      <div class="hg-ketik-baris"><input class="ketik-nama" id="bpKetik" type="text" inputmode="numeric" placeholder="jumlah yang dibayar" value="${d.ketik}" data-ketik="bpKetik" data-kolom="ketik"><div class="kaca-btn aktif" data-aksi="bpLunas">lunas ${H.bon ? RP(H.bon.sisa).replace('Rp', '') : ''}</div></div>
      <div class="ket">${H.bon ? 'Sisa bon ini ' + RP(H.bon.sisa) + (H.bon.dibayar > 0 ? ' · sudah dibayar ' + RP(H.bon.dibayar) : '') : 'Pilih bonnya'}</div>
      <div class="ket">Cara bayar · ${S.ada ? 'yang dijaga isi kantong yang dipilih (' + S.teksTitik + ')' : B.adaKas ? 'yang dijaga total uang toko ' + RP(B.kas) : 'uang toko belum bisa dihitung — titik kas belum disetel'}</div>
      <div class="tombol-baris rapat" data-k="cara">${BP.CARA_BAYAR_BON.map(([id, nm]) => h`<div class="kaca-btn ${H.cara === id ? 'aktif' : ''}" data-aksi="bpCara" data-c="${id}" data-k="cr-${id}">${nm}${id === 'transfer' ? h`<small style="display: block; font-size: 9.5px; font-weight: 400; color: var(--redup);">rekening ${isiK('rekening')}</small>` : h`<small style="display: block; font-size: 9.5px; font-weight: 400; color: var(--redup);">laci / brankas</small>`}</div>`)}</div>
      ${H.cara === 'tunai' ? h`<div class="tombol-baris rapat" data-k="dari">${BP.TEMPAT_UANG.filter(([id]) => id !== 'rekening').map(([id, nm]) => h`<div class="kaca-btn ${d.dari === id ? 'aktif' : ''}" data-aksi="bpDari" data-d="${id}" data-k="dr-${id}">${nm} <small style="font-weight: 400; color: var(--redup);">${isiK(id)}</small></div>`)}</div>` : ''}
      ${H.cara === 'transfer' ? h`<div class="jalur bungkus" data-k="admin"><div class="seg ${d.adminI < 0 ? 'aktif' : ''}" data-aksi="bpAdmin" data-i="-1">tanpa biaya admin</div>${H.B.atur.admin.map((a, i) => h`<div class="seg ${d.adminI === i ? 'aktif' : ''}" data-aksi="bpAdmin" data-i="${i}" data-k="ad-${i}">${a.nama} ${RP(a.n)}</div>`)}</div>
        ${H.rekeningKosong ? h`<div class="pita-info awas" data-k="rek-kosong" style="display: flex; flex-direction: column; gap: 6px;"><span>${H.rekeningTeks}</span><div class="kaca-btn kecil" data-aksi="bpKeRekening" style="align-self: flex-start;">catat isi rekening dulu ›</div></div>` : h`<div class="ket">Biaya admin dicatat terpisah sebagai uang keluar "Untuk toko" (biaya bank) bertanggal sama — utang pemasok turun sebesar yang dibayar, bukan sebesar yang keluar dari rekening.</div>`}` : ''}
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
      <div class="jalur bungkus" data-k="gulir-pil"><div class="seg ${k.bonLamaBergulir ? '' : 'aktif'}" data-aksi="bpKartuGulir" data-v="0" data-k="gl-tetap">bon lama: tanggal tetap</div><div class="seg ${k.bonLamaBergulir ? 'aktif' : ''}" data-aksi="bpKartuGulir" data-v="1" data-k="gl-gulir">bon lama ikut kedatangan terakhir</div></div>
      <div class="ket">${k.bonLamaBergulir ? 'Bon lama ' + k.nama + ' (sebelum sistem) dianggap bergulir: umur & jatuh temponya dihitung dari kedatangan ' + k.nama + ' yang terakhir. Nilai & sisa utangnya tidak berubah.' : 'Bon lama dihitung dari tanggal bonnya sendiri. Pilih "ikut kedatangan terakhir" kalau utang lama ke pemasok ini bergulir — tanggalnya selalu tanggal pembelian terbaru.'}</div>
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
      ${bilah}${gambarHitungBeli(s)}${gambarPesanan(H)}${gambarRencanaBulan(s)}${gambarAturL(s, H)}
      <div class="ket" style="font-size: 11px;">Saran = baris harga (merek seharga dari pemasok yang sama — barang yang sama di mata pemasok) yang stok GABUNGANNYA habis ≤ ${H.atur.ambangHari} hari menurut laju penjualan 14 hari; jumlahnya supaya cukup ${H.atur.targetHari} hari, dibulatkan ke karung penuh, lalu dibagi ke merek yang paling cepat habis. Tanpa penjualan 14 hari tidak ditebak; nama yang diarsipkan tidak dibeli. Harga = harga beli terakhir tiap pemasok dari kedatangan nyata (tanggalnya selalu ditulis; harga yang lebih tua dari kiriman terakhir pemasok itu ditulis umurnya, juga di WhatsApp). Merek berkelas mutu ikut harga kiriman terbaru kelas yang sama dari pemasok itu bila bedanya masih dalam batas "sama barangnya" (Barang masuk › Atur). Muatan truk ${H.atur.muatanTerukur ? 'terukur dari kedatangan nyata (median)' : 'diatur owner'}. Pesanan yang dikirim dicatat & dicocokkan dengan kedatangannya di Barang masuk.${H.D.tanpaPemasok.length ? ' Belum tahu pemasoknya: ' + H.D.tanpaPemasok.join(', ') + ' (belum pernah tercatat datang dari pemasok).' : ''}</div>
    </section>`;
  }
  // tinjauan E1: merek yang punya merek seharga (pemasok & harga sama) menyebut gabungannya — saran & "perlu" dihitung dari gabungan itu
  const barisBelanja = (b, gaya) => h`<div class="bl-baris ${gaya || ''}" data-k="bl-${b.merk}"><div><div class="nm ${b.kritis ? 'awas-teks' : ''}">${b.merk}</div><div class="ket">${b.sisaTeks}</div>${b.tutup || b.gabungTeks ? h`<div class="ket" data-k="blg-${b.merk}" style="font-size: 10.5px;">${b.tutup ? b.tutup + ' · ' : ''}${b.gabungTeks}</div>` : ''}</div>
    <div>${b.dipesan ? h`<span class="ket">dipesan</span>` : b.k > 0 ? h`<span class="step"><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="-1">−</span><span class="n" style="min-width: 74px; font-size: 12.5px;">${b.k} karung</span><span data-aksi="blUbah" data-merk="${b.merk}" data-arah="1">+</span></span>` : h`<div class="kaca-btn kecil ${b.adaHarga ? '' : 'mati'}" data-aksi="blPakai" data-merk="${b.merk}">${b.saranTeks}</div>`}</div>
    ${b.k > 0 ? h`<div class="sd" data-aksi="blGanti" data-merk="${b.merk}" style="${b.sumber && b.sumber.length > 1 ? 'cursor: pointer;' : ''}">${b.hargaTeks} · ${BL.blKG(b.kg)} · ±${RP(b.rp)}${b.sesudahTeks ? ' · ' + b.sesudahTeks : ''}</div>` : b.k === 0 && !b.dipesan ? h`<div class="sd">${b.hargaTeks}</div>` : ''}${b.dipesan ? h`<div class="sd">${b.dipesanTeks}</div>` : ''}</div>`;
  // owner 7 Okt: satu baris = satu HARGA beli terakhir dari pemasok ini (pemasok mengenal barangnya dari harga); merek-merek seharga jadi keterangan kecil.
  // Stok, laju & ganti pemasok tetap per merek di "Kapan habis".
  const barisHargaBelanja = (g, p) => h`<div class="bl-baris" data-k="blh-${g.kunci}"><div><div class="nm ${g.kritis ? 'awas-teks' : ''}">${g.label}</div>${g.merk.map((b) => h`<div class="ket" data-k="blhm-${b.merk}">${b.merk}${b.k ? ' · ' + b.k + ' krg' : ''} · ${b.sisaTeks}</div>`)}</div>
    <div>${g.k > 0 ? h`<span class="step"><span data-aksi="blUbahG" data-p="${p}" data-g="${g.kunci}" data-arah="-1">−</span><span class="n" style="min-width: 74px; font-size: 12.5px;">${g.k} karung</span><span data-aksi="blUbahG" data-p="${p}" data-g="${g.kunci}" data-arah="1">+</span></span>` : h`<div class="kaca-btn kecil" data-aksi="blKetukG" data-p="${p}" data-g="${g.kunci}">${g.saranTeks}</div>`}</div>
    <div class="sd">${g.hariTeks ? g.hariTeks + ' · ' : ''}${g.hargaTeks}${g.kodeTeks ? ' · ' + g.kodeTeks : ''}${g.k > 0 ? ' · ' + BL.blKG(g.kg) + ' · ±' + RP(g.rp) : ''}</div></div>`;
  // ---------- paket P5 (owner 27 Nov 2026, A20): RENCANA BELI BULAN DEPAN — total kg dari rata-rata pemakaian per bulan, tanpa musim ----------
  function gambarRencanaBulan(s) {
    const R = SG.sgRencanaBeli(kini()); const KGt = (n) => ANGKA(Math.round(n)) + ' kg'; const daftar = R.daftar.filter((x) => x.karung > 0);
    return h`<div class="kartu" data-k="rencana-bulan" style="gap: 4px;"><div class="hg-kepala"><span class="nm">Rencana beli ${R.namaDepan}</span><span class="md">${R.total.karung ? ANGKA(R.total.karung) + ' karung · ' + KGt(R.total.kg) : 'cukup'}</span></div>
      <div class="ket" data-k="rb-kal">${R.kalimat}. Butuh ${R.namaDepan} ±${KGt(R.total.butuh)} menurut rata-rata ${R.bulan.map((b) => b.nama.split(' ')[0]).join(', ')}.</div>
      <div class="pita-info" data-k="rb-musim">${R.musim}</div>
      ${s.rbBuka ? h`${daftar.map((x) => h`<div class="hg-daftar tiga" data-k="rb-${x.merk}"><span class="ket">${x.karung} krg</span><span><b>${x.merk}</b><span class="ket" style="display: block; font-size: 10.5px;">pakai ${x.perBulan.map((n) => ANGKA(Math.round(n))).join(' / ')} kg${x.arah ? ' · ' + (x.arah === 'naik' ? 'naik — pakai bulan terakhir' : 'turun — pakai bulan terakhir') : ''} · sisa ${KGt(x.sisa)} → 1 ${R.namaDepan.split(' ')[0]} ±${KGt(x.sisaAwal)} · cadangan ${R.targetHariMin} hari ${KGt(x.cadangan)}</span></span><span>${x.harga > 0 ? '±' + RP(x.rp) : 'harga ?'}</span></div>`)}
        ${R.berhenti.length ? h`<div class="ket" data-k="rb-henti" style="font-size: 10.5px;">Tidak diramal (bulan terakhir & bulan ini tanpa pemakaian — mis. nama lama yang sudah diganti): ${R.berhenti.slice(0, 10).map((x) => x.merk).join(', ')}${R.berhenti.length > 10 ? ' …' : ''}</div>` : ''}
        <div class="ket" style="font-size: 10.5px;" data-k="rb-rumus">${R.rumus}.${R.total.tanpaHarga ? ' ' + R.total.tanpaHarga + ' merek belum punya harga beli — rupiahnya tidak dihitung.' : ''}</div>` : ''}
      <div class="kaca-btn kecil" data-aksi="rbBuka" style="align-self: flex-start;">${s.rbBuka ? 'tutup rincian' : 'lihat per merek ›'}</div></div>`;
  }
  function gambarTruk(s, H, pa) {
    const T = BL.susunTruk(H, pa); if (!T) return h`<div class="pita-info" data-k="truk-kosong">Belum ada pemasok yang pernah mengirim barang — catat kedatangan pertama di Stok → Barang masuk.</div>`; const R = T.R;
    return h`<div class="hg-kolom" data-k="truk"><div class="jalur bungkus" data-k="pem-tab">${H.perP.map((p) => h`<div class="seg ${p.pemasok === pa ? 'aktif' : ''}" data-aksi="blPemasok" data-p="${p.pemasok}" data-k="pt-${p.kunci}">${p.pemasok}${p.karung ? ' · ' + p.karung : ''}</div>`)}</div>
      <div class="kartu" style="gap: 6px;"><div class="bl-truk">${mentah(IKON.truk)}<div class="bl-bak">${T.bak.map((k, i) => h`<div class="${k.kelas}" data-k="bak-${k.merk || 'kosong'}" style="flex: ${k.flex} 0 0px;">${k.t}</div>`)}${T.lebih ? h`<div class="lebih" style="flex: 0 0 14px;"></div>` : ''}</div></div>
        <div class="bl-muat"><span><b>${T.muatAngka}</b> ${T.muatDari}</span><span class="ket ${T.lebih ? 'awas-teks' : ''}" style="text-align: right;">${T.muatSisa}</span></div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${R.saran.length ? '' : 'mati'}" data-aksi="blSaranPa" data-p="${pa}">${T.saranTeks}</div><div class="kaca-btn aktif ${T.bisaPenuhi ? '' : 'mati'}" data-aksi="blPenuhi" data-p="${pa}">Penuhi truknya</div><div class="kaca-btn putus ${R.karung ? '' : 'mati'}" data-aksi="blKosongkan" data-p="${pa}">Kosongkan</div></div>
        <div class="ket">${R.caraTeks}${R.tempo.hari ? ' · ' + R.tempo.teks : ''}${R.kontak ? ' · ' + R.kontak : ' · nomor belum ada di kartu'}</div></div>
      ${R.uangTeks ? h`<div class="pita-info ${R.uangAwas ? 'awas' : ''}" data-k="uang">${R.uangTeks}</div>` : ''}
      <div class="kartu" style="gap: 0;">${R.gMilik.map((g) => barisHargaBelanja(g, pa))}${R.dipesanMerk.length ? h`<div class="ket" data-k="blh-dipesan" style="padding-top: 6px;">Sudah dipesan, menunggu datang: ${R.dipesanMerk.map((b) => b.merk).join(', ')}</div>` : ''}</div>
      ${R.karung ? h`<div class="utama" data-aksi="blWaBuka" data-p="${pa}">KIRIM PESANAN ${pa} · ${R.karung} karung</div>` : ''}</div>`;
  }
  function gambarHari(H) {
    return h`<div class="hg-kolom" data-k="hari"><div class="hg-ringkas tiga" data-k="ringkas-bl">${H.ringkas.map((r, i) => h`<div class="${r.nyala && r.a ? 'nyala' : ''}" data-k="rl-${i}"><span class="a">${r.a}</span><span class="l">${r.l}</span></div>`)}</div>
      ${H.perluSemua.length ? h`<div class="kaca-btn putus" data-aksi="blSaranSemua">${H.saranSemuaTeks}</div>` : ''}
      <div class="kartu" style="gap: 0;">${H.kelompok.map((g) => h`<div data-k="hk-${g.judul}"><div class="hg-kepala"><span class="nm">${g.judul}</span><span class="md ${g.awas ? 'naik' : ''}">${g.ket}</span></div>
        ${g.isi.map((b) => h`<div class="bl-hari" data-k="bh-${b.merk}"><div class="atas"><span class="${b.kritis ? 'awas-teks' : ''}" style="font-weight: 600;">${b.merk}</span><span class="ket">${b.hari === null ? '—' : (b.hari > 30 ? '30+' : b.hari) + ' hr'}</span></div>
          <div class="bl-rel"><i class="${b.hari !== null && b.hari <= H.atur.ambangHari ? 'kritis' : ''}" style="width: ${b.hari === null ? 0 : Math.min(100, Math.round(b.hari / 30 * 100))}%;"></i><u style="left: ${b.hari === null ? 0 : Math.min(100, Math.round(b.hari / 30 * 100))}%; width: ${b.k && b.hariSesudah !== null ? Math.max(0, Math.min(100, Math.round(b.hariSesudah / 30 * 100)) - Math.min(100, Math.round((b.hari || 0) / 30 * 100))) : 0}%;"></u><b style="left: ${Math.round(H.atur.ambangHari / 30 * 100)}%;"></b></div>
          ${barisBelanja(b, 'rapat')}</div>`)}</div>`)}<div class="ket" style="padding-top: 6px;">${H.legenda}</div></div></div>`;
  }
  function gambarKertas(s, H) {
    return h`<div class="hg-kolom" data-k="kertas">${H.perluSemua.length ? h`<div class="kaca-btn putus" data-aksi="blSaranSemua">${H.saranSemuaTeks}</div>` : ''}
      ${H.kertas.length ? '' : h`<div class="pita-info">Tidak ada yang perlu dibeli — semua stok cukup lebih dari ${H.atur.ambangHari} hari atau sudah dipesan.</div>`}
      <div class="bl-kertas"><div class="ket" style="line-height: 28px; text-transform: uppercase; letter-spacing: 0.08em;">Daftar belanja · ${tanggalPendek(waktu().tanggal)}</div>
        ${H.kertas.map((r) => h`<div data-k="kr-${r.kunci}"><div class="jd">${r.pemasok} <span class="ket" style="font-size: 10.5px;">${r.karung ? r.karung + ' karung · ' + BL.blKG(r.kg) : 'belum ada yang dipilih'}</span></div>
          ${r.g.map((g) => h`<div class="bl-tulis" data-k="kt-${g.kunci}"><div class="bl-centang ${g.k > 0 ? 'ya' : ''}" data-aksi="blKetukG" data-p="${r.pemasok}" data-g="${g.kunci}">${g.k > 0 ? '✓' : ''}</div><div data-aksi="blKetukG" data-p="${r.pemasok}" data-g="${g.kunci}"><div style="font-weight: 600;">${g.label}${g.basi ? h` <span class="ket" style="font-size: 10px;">· harga ${tanggalPendek(g.tanggal)}</span>` : ''}</div>${g.kodeTeks || g.hariTeks ? h`<div class="ket" style="font-size: 10px;">${[g.kodeTeks, g.hariTeks].filter(Boolean).join(' · ')}</div>` : ''}${g.merk.map((b) => h`<div class="ket" style="font-size: 10px;" data-k="ktm-${b.merk}">${b.merk}${b.k ? ' · ' + b.k + ' krg' : ''} · ${b.sisaTeks}${b.k > 0 && b.sesudahTeks ? ' · ' + b.sesudahTeks : ''}</div>`)}${g.k > 0 ? h`<div class="ket" style="font-size: 10px;">±${RP(g.rp)} · ${g.hargaTeks}</div>` : ''}</div>
            <div>${g.k > 0 ? h`<span class="step"><span data-aksi="blUbahG" data-p="${r.pemasok}" data-g="${g.kunci}" data-arah="-1">−</span><span class="n" style="min-width: 66px; font-size: 12.5px;">${g.k} krg</span><span data-aksi="blUbahG" data-p="${r.pemasok}" data-g="${g.kunci}" data-arah="1">+</span></span>` : h`<span class="ket" style="font-size: 10.5px;">${g.saranTeks}</span>`}</div></div>`)}
          <div class="bl-kaki"><div><div class="serif" style="font-size: 15px;">${r.karung ? '±' + RP(r.rp) : ''}</div><div class="ket" style="font-size: 10px;">${r.karung && r.muatanKg ? (r.lebih ? 'kelebihan ' + BL.blKG(r.lebih) + ' dari satu truk' : 'truk masih muat ' + BL.blKG(r.sisaMuat)) : ''}</div></div>${r.karung ? h`<div class="kaca-btn kecil gelap" data-aksi="blWaBuka" data-p="${r.pemasok}">kirim ke WA</div>` : ''}</div></div>`)}</div>
      ${H.lainnya.length ? h`<div class="kartu" style="gap: 0;"><div class="label" style="padding-top: 2px;">Belum perlu — tapi boleh ditambah</div>${H.lainnya.map((b) => h`<div class="bl-baris" data-k="ln-${b.merk}"><div><div class="nm">${b.merk}</div><div class="ket">${b.sisaTeks}</div></div><div class="kaca-btn kecil" data-aksi="blPakai" data-merk="${b.merk}">tambah</div></div>`)}</div>` : ''}</div>`;
  }
  function gambarWaPesanan(s, H) {
    const R = H.perP.find((r) => r.pemasok === s.wa2); if (!R || !R.karung) return h`<div class="pita-info awas" data-k="wa-kosong">Belum ada karung untuk ${s.wa2} di daftar. <span data-aksi="blWaBuka" data-p="${s.wa2}" style="text-decoration: underline; cursor: pointer;">tutup</span></div>`;
    const P = BL.susunPesanan(s.pesan, s.wa2, waktu(), s.waHarga, s.waJanji, namaPencatat());
    return h`<div class="kartu hg-lembar" data-k="wa-pesanan" style="gap: 8px;"><div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Pesanan untuk ${R.pemasok}</div><div class="ket">${R.kontak ? 'WhatsApp ke ' + R.kontak : 'nomor belum ada di kartu — WhatsApp menanyakan tujuannya'}</div></div><div class="kaca-btn" data-aksi="blWaBuka" data-p="${s.wa2}">tutup</div></div>
      <div class="jalur bungkus" data-k="wa-pem">${H.perP.filter((r) => r.karung).map((r) => h`<div class="seg ${r.pemasok === s.wa2 ? 'aktif' : ''}" data-aksi="blWaBuka" data-p="${r.pemasok}" data-k="wp-${r.kunci}">${r.pemasok}</div>`)}</div>
      <div class="hg-wa">${(P.baris || []).map((t, i) => h`<div data-k="wb-${i}">${i === 0 ? h`<b>${t.replace(/\*/g, '')}</b>` : t}</div>`)}</div>
      <div class="jalur rapat"><div class="seg ${s.waHarga ? 'aktif' : ''}" data-aksi="blWaHarga">${s.waHarga ? '✓ perkiraan jumlah uang ikut dikirim' : 'perkiraan jumlah uang TIDAK ikut dikirim'}</div></div>
      <div class="ket">Satu baris = satu harga beli terakhir dari ${R.pemasok} — pemasok mengenal barangnya dari harga; merek yang seharga digabung.</div>
      ${P.lebihTeks ? h`<div class="pita-info awas">${P.lebihTeks}</div>` : ''}${P.uangTeks ? h`<div class="pita-info">${P.uangTeks}</div>` : ''}
      ${pilihJanji(s.waJanji, 'blWaJanji', 'blWaJanjiKetik', 'wj', 'Dijanjikan datang')}
      <div class="utama" data-aksi="blKirim">KIRIM KE WHATSAPP · catat sebagai pesanan</div></div>`;
  }
  /** paket tanggal janji: pil janji datang (belum tahu · hari ini · besok · lusa) + isian tanggal lain. aksi = pil, ketik = isian. */
  function pilihJanji(nilai, aksi, ketik, k, judul) {
    const iso = waktu().tanggal; const v = String(nilai || ''); const pil = JN.jnPilihan(iso); const lain = v && !pil.some(([t]) => t === v);
    return h`<div data-k="${k}-janji"><div class="label">${judul}</div><div class="jalur rapat bungkus" data-k="${k}-pil">${pil.map(([t, nm]) => h`<div class="seg ${v === t ? 'aktif' : ''}" data-aksi="${aksi}" data-t="${t}" data-k="${k}-p-${nm}">${nm}${t ? ' · ' + tanggalPendek(t).replace(/ \d{4}$/, '') : ''}</div>`)}</div>
      <input class="ketik-nama" type="date" min="${iso}" value="${lain ? v : ''}" data-ketik="${ketik}" data-k="${k}-tgl" aria-label="tanggal janji lain">
      <div class="ket">${v ? 'Janji datang ' + tanggalPendek(v) + ' — dipakai menghitung pemasok tepat waktu (Laporan › Pondasi › Tepat janji).' : 'Belum tahu? Biarkan kosong, isi sesudah pemasok membalas — pesanan tanpa janji tidak dihitung tepat / telat.'}</div></div>`;
  }
  function gambarPesanan(H) {
    const semua = BL.pesananSemua().slice(0, 8); if (!semua.length) return '';
    const s = st(); const jp = s.janjiP;
    return h`<div class="kartu platina" data-k="pesanan" style="gap: 2px;"><div class="label">Pesanan ke pemasok</div>${semua.map((p) => h`<div class="hg-tugas" data-k="ps-${p.id}"><div><div>${p.pemasok} · dipesan ${tanggalPendek(p.tanggal)} ${p.jam || ''} · <b>${p.status === 'menunggu' ? 'menunggu datang' : p.status === 'datang' ? 'sudah datang' + (p.datangTanggal ? ' ' + tanggalPendek(p.datangTanggal) : '') : 'dibatalkan'}</b></div><div class="ket">${(Array.isArray(p.barisHarga) && p.barisHarga.length ? p.barisHarga.map((b) => (b.hargaPerKg > 0 ? (b.jenis || 'beras') + ' ' + RP(b.hargaPerKg) : (b.merk || []).join('/')) + ' ×' + b.karung) : (p.baris || []).map((b) => b.merk + ' ' + b.karung)).join(' · ')} · ${p.karung} karung · ${BL.blKG(p.kg)} · ±${RP(p.rp)}</div>${(() => { const X = JN.jnPesananPemasok(p.id, kini()); return X ? h`<div class="ket ${X.keadaan === 'lewat' || X.keadaan === 'telat' || X.isi === 'sebagian' ? 'awas-teks' : ''}" data-k="psj-${p.id}">${JN.jnKataBaris(X)}</div>` : ''; })()}</div>
      ${p.status === 'menunggu' ? h`<div class="hg-aksi-kecil"><div class="kaca-btn kecil" data-aksi="blBukaLagi" data-id="${p.id}">WA lagi</div><div class="kaca-btn kecil ${jp && jp.id === String(p.id) ? 'aktif' : ''}" data-aksi="blJanjiBuka" data-id="${p.id}">${p.janjiTanggal ? 'geser janji' : 'isi janji'}</div><div class="kaca-btn kecil" data-aksi="blPesanan" data-id="${p.id}" data-status="datang">sudah datang</div><div class="kaca-btn kecil putus" data-aksi="blPesanan" data-id="${p.id}" data-status="batal">batalkan</div></div>` : ''}
</div>
      ${p.status === 'menunggu' && jp && jp.id === String(p.id) ? h`<div class="kartu" data-k="psj-ubah-${p.id}" style="gap: 6px;">${pilihJanji(jp.tanggal, 'blJanjiPilih', 'blJanjiKetik', 'pj', p.janjiTanggal ? 'Geser janji datang (janji pertama tetap dihitung)' : 'Janji datang dari ' + p.pemasok)}<div class="tombol-baris rapat"><div class="kaca-btn" data-aksi="blJanjiBuka" data-id="${p.id}">batal</div><div class="kaca-btn aktif emas" data-aksi="blJanjiSimpan">SIMPAN JANJI</div></div></div>` : ''}`)}
      <div class="ket" style="padding-top: 4px;">"Sudah datang" dibaca sendiri dari kedatangan pemasok itu sesudah pesanan (Stok → Barang masuk); tombolnya untuk pesanan yang barangnya datang tanpa dicatat lewat Barang masuk (mis. dicatat sebelum sistem lama pensiun 3 Okt).</div></div>`;
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

  // ---------- H4 BANDING PEMASOK (owner 26 Nov 2026, sensus ulang 1c: A6 · A18 · A19 · A95 · A129 · A137) ----------
  // Angka dari banding-pemasok-logika (baca saja); catatan & setelan lewat banding-catat-logika. Satu markup tiga lebar: tabel per kelas jadi baris bertumpuk di HP.
  function bdDrafBaru(jenis) { const A = BC.bcAtur(); return { jenis, tanggal: waktu().tanggal, pemasok: '', kelas: '', merek: '', hargaPerKg: '', ongkirPerKg: '', sampaiToko: false, catatan: '', sumber: A.sumber[0] || '', tingkat: 'grosir', mutu: 'medium', wilayah: A.wilayah }; }
  const bdTgl = (t) => tanggalPendek(t).replace(/ \d{4}$/, '');
  const bdPersen = (v) => (v === null || v === undefined ? 'belum terukur' : DESIMAL(Math.round(v * 10) / 10) + ' %');
  const bdKg = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
  function gambarBanding(s, L) {
    const iso = waktu().tanggal; const tab = BD.BD_TAB.some(([id]) => id === s.tabD) ? s.tabD : 'minggu'; const SM = BC.bcStatusMinggu(iso);
    const lalu = BC.bcBulanGeser(iso.slice(0, 7), -1); const dib = BC.bcDibanding(lalu); const nUsul = BC.bcUsulMenunggu(); const A = BC.bcAtur();
    const ac = BC.bcEntri(BC.bcTambahHari(iso, -62), iso).filter((e) => e.jenis === 'acuan'); const acAkhir = ac[ac.length - 1] || null;
    const panel = tab === 'bulan' ? gambarBdBulan(s) : tab === 'rapor' ? gambarBdRapor(s) : tab === 'acuan' ? gambarBdAcuan(s) : tab === 'tren' ? gambarBdTren() : gambarBdMinggu(s);
    return h`<section class="hg-banding" data-k="banding">
      <div class="hg-ringkas" data-k="bd-ringkas">
        <div class="${SM.cukup ? '' : 'nyala'}" data-k="bd-r-minggu" data-aksi="tabD" data-t="minggu"><span class="a">${SM.n}/${SM.min}</span><span class="l">pemasok berharga minggu ini</span></div>
        <div class="${dib ? '' : 'nyala'}" data-k="bd-r-bulan" data-aksi="tabD" data-t="bulan"><span class="a">${dib ? '✓' : '—'}</span><span class="l">banding ${lalu.slice(5, 7)}/${lalu.slice(2, 4)} ${dib ? 'sudah dibaca' : 'belum dibaca'}</span></div>
        <div data-k="bd-r-acuan" data-aksi="tabD" data-t="acuan"><span class="a">${acAkhir ? bdTgl(acAkhir.tanggal) : '—'}</span><span class="l">harga acuan terakhir</span></div>
        <div class="${nUsul ? 'nyala' : ''}" data-k="bd-r-usul"><span class="a">${nUsul}</span><span class="l">usul tablet menunggu</span></div></div>
      ${nUsul ? h`<div class="pita-info emas" data-k="bd-usul">${nUsul} usul harga dari tablet menunggu — putuskan di Menu › Toko ini › Peran & persetujuan › Persetujuan (Setujui = dicatat di sini atas nama pengusulnya).</div>` : ''}
      <div class="tombol-baris" data-k="bd-tombol" style="grid-template-columns: 1fr 1fr auto;">
        <div class="kaca-btn ${s.bdCatat && s.bdCatat.jenis === 'tawaran' ? 'aktif' : ''} emas" data-aksi="bdBuka" data-jenis="tawaran" data-k="bd-buka-tawaran">+ Harga tawaran</div>
        <div class="kaca-btn ${s.bdCatat && s.bdCatat.jenis === 'acuan' ? 'aktif' : ''}" data-aksi="bdBuka" data-jenis="acuan" data-k="bd-buka-acuan">+ Harga acuan</div>
        <div class="kaca-btn ${s.aturBd ? 'aktif' : ''}" data-aksi="bukaAturBd" data-k="bd-buka-atur">Atur</div></div>
      ${s.bdCatat ? gambarBdCatat(s) : ''}${s.aturBd ? gambarBdAtur(s) : ''}
      ${tabBaris(BD.BD_TAB, tab, 'tabD', L === 'hp' ? 'enam' : '')}
      <div class="bd-panel" data-k="bd-panel-${tab}">${panel}</div>
      <div class="ket" style="font-size: 11px;" data-k="bd-rumus">${BD.BD_RUMUS.modal}. ${BD.BD_RUMUS.layak}${A.adaPotong ? '' : ' (potongan mutu belum diatur — Rp0)'}. ${BD.BD_RUMUS.tawaran}. Pengingat tiap ${(BC.BC_HARI.find((x) => x[0] === A.hariMinggu) || ['', ''])[1]} (harga ${A.minPemasok} pemasok) & tanggal ${A.tanggalBulan} (banding bulan lalu) — Menu › Toko ini › Pengingat.</div>
    </section>`;
  }
  function gambarBdCatat(s) {
    const d = s.bdCatat; const A = BC.bcAtur(); const C = BD.bdCalon(kini()); const taw = d.jenis === 'tawaran';
    const isian = (kolom, judul, ph, tipe) => h`<div><div class="ket">${judul}</div><input class="ketik-nama" type="${tipe === 'date' ? 'date' : 'text'}" ${tipe === 'angka' ? 'inputmode="numeric"' : ''} value="${d[kolom] || ''}" placeholder="${ph || ''}" data-ketik="bdKetik" data-kolom="${kolom}" data-k="bd-i-${kolom}"></div>`;
    const pil = (kolom, daftar) => h`<div class="jalur bungkus rapat" data-k="bd-pil-${kolom}">${daftar.map(([v, nm]) => h`<div class="seg ${String(d[kolom]) === String(v) ? 'aktif' : ''}" data-aksi="bdPilihKolom" data-kolom="${kolom}" data-v="${v}">${nm}</div>`)}</div>`;
    const chip = (kolom, daftar) => (daftar.length ? h`<div class="jalur bungkus rapat bd-chip" data-k="bd-chip-${kolom}">${daftar.slice(0, 12).map((v) => h`<div class="seg ${d[kolom] === v ? 'aktif' : ''}" data-aksi="bdPilihKolom" data-kolom="${kolom}" data-v="${v}">${v}</div>`)}</div>` : '');
    return h`<div class="kartu pegas bd-catat" data-k="bd-catat" style="gap: 8px;"><div class="label">${taw ? 'Harga tawaran pemasok (tidak / belum dibeli)' : 'Harga acuan resmi (untuk tawar-menawar harga beli)'}</div>
      <div class="jalur rapat" data-k="bd-jenis">${BC.BC_JENIS.map(([id, nm]) => h`<div class="seg ${d.jenis === id ? 'aktif' : ''}" data-aksi="bdJenis" data-jenis="${id}">${nm}</div>`)}</div>
      ${taw ? h`<div class="ps-form tiga">${isian('pemasok', 'Pemasok yang menawarkan', 'nama pemasok')}${isian('kelas', 'Kelas / jenis beras', 'mis. IR64 Elevate')}${isian('merek', 'Merek dia (boleh kosong)', '')}</div>
          ${chip('pemasok', C.pemasok)}${chip('kelas', C.kelas)}
          <div class="ps-form tiga">${isian('hargaPerKg', 'Harga per kg', '12.900', 'angka')}${d.sampaiToko ? h`<div><div class="ket">Ongkos kirim per kg</div><div class="k2" style="padding-top: 8px;">sudah termasuk (harga sampai toko)</div></div>` : isian('ongkirPerKg', 'Ongkos kirim per kg (kosong = belum tahu)', '', 'angka')}${isian('tanggal', 'Tanggal ditanya', '', 'date')}</div>
          <div class="seg ${d.sampaiToko ? 'aktif' : ''}" data-aksi="bdSampai" data-k="bd-sampai" style="align-self: flex-start;">${d.sampaiToko ? '✓ ' : ''}harga sudah sampai toko (tanpa ongkos kirim)</div>`
        : h`<div class="ket">Sumber</div>${pil('sumber', A.sumber.map((x) => [x, x]))}<div class="ket">Tingkat harga</div>${pil('tingkat', BC.BC_TINGKAT)}<div class="ket">Mutu</div>${pil('mutu', BC.BC_MUTU)}
          <div class="ps-form tiga">${isian('hargaPerKg', 'Harga per kg', '13.100', 'angka')}${isian('wilayah', 'Wilayah', 'mis. nasional / provinsi')}${isian('tanggal', 'Tanggal datanya', '', 'date')}</div>`}
      ${isian('catatan', 'Catatan (boleh kosong)', taw ? 'mis. minimal 5 ton, tempo 14 hari' : '')}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bdBuka" data-jenis="${d.jenis}">batal</div><div class="kaca-btn aktif emas" data-aksi="bdSimpan" data-k="bd-simpan">SIMPAN ${taw ? 'HARGA TAWARAN' : 'HARGA ACUAN'}</div></div></div>`;
  }
  function gambarBdAtur(s) {
    const a = s.aturBd; const isian = (kolom, judul, ph) => h`<div><div class="ket">${judul}</div><input class="ketik-nama" type="text" inputmode="${kolom === 'sumber' || kolom === 'wilayah' ? 'text' : 'numeric'}" value="${kolom.indexOf('pm.') === 0 ? (a.potongMutu || {})[kolom.slice(3)] || '' : a[kolom] || ''}" placeholder="${ph || ''}" data-ketik="bdAturKetik" data-kolom="${kolom}" data-k="bd-a-${kolom}"></div>`;
    return h`<div class="kartu pegas" data-k="bd-atur" style="gap: 8px;"><div class="label">Atur banding pemasok · angka owner</div>
      <div class="ps-form tiga">${isian('minPemasok', 'Pemasok minimal per minggu & bulan', '3')}${isian('tanggalBulan', 'Tanggal banding bulanan (1–28)', '1')}${isian('wilayah', 'Wilayah harga acuan', 'mis. Jawa Barat')}</div>
      <div class="ket">Hari pengingat mingguan (catat harga sebelum belanja)</div>
      <div class="jalur bungkus rapat" data-k="bd-a-hari">${BC.BC_HARI.map(([n, nm]) => h`<div class="seg ${Number(a.hariMinggu) === n ? 'aktif' : ''}" data-aksi="bdAturHari" data-h="${n}">${nm}</div>`)}</div>
      ${isian('sumber', 'Sumber harga acuan (pisahkan dengan koma)', 'Panel Harga Bapanas, PIHPS BI, BPS')}
      <div class="ket">Potongan mutu — rupiah per kg yang ditambahkan ke modal layak jual untuk tiap tanda AWAS saat barang datang (kosong / 0 = tidak dipotong). Ambang tandanya diatur di Stok › Barang masuk › Atur.</div>
      <div class="ps-form tiga">${BC.BC_TANDA.map(([id, nm]) => isian('pm.' + id, nm, 'Rp/kg'))}</div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturBd">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturBd" data-k="bd-a-simpan">SIMPAN ATURAN</div></div></div>`;
  }
  // daftar catatan (tawaran / acuan) satu rentang + hapus dua ketukan
  function gambarBdEntri(s, E, judul) {
    if (!E.length) return '';
    return h`<div class="kartu" data-k="bd-entri" style="gap: 2px;"><div class="label">${judul} · ${E.length}</div>${E.slice().reverse().map((e) => h`<div class="bd-entri" data-k="bd-e-${e.id}"><div><div>${BC.bcTeks(e)}</div><div class="k2">${e.oleh ? 'dicatat ' + e.oleh : ''}${e.dariUsul ? ' · dari usul tablet' : ''}${e.catatan ? ' · ' + e.catatan : ''}</div></div>
      <div class="kaca-btn kecil ${s.bdYakinHapus === e.id ? 'awas' : 'putus'}" data-aksi="bdHapus" data-id="${e.id}">${s.bdYakinHapus === e.id ? 'YAKIN — hapus' : 'hapus'}</div></div>`)}</div>`;
  }
  function gambarBdMinggu(s) {
    const iso = waktu().tanggal; const senin = s.bdSenin || BC.bcSenin(iso); const M = BD.bdMinggu(senin, kini()); const E = BC.bcEntri(M.senin, M.akhir);
    const het = (x) => (x ? h`<span class="hg-cap">HET ${x}</span>` : '');
    return h`<div class="bd-nav" data-k="bd-nav-minggu"><div class="kaca-btn kecil" data-aksi="bdMinggu" data-arah="-1">‹ minggu lalu</div><div class="nm">${bdTgl(M.senin)} – ${bdTgl(M.minggu)}${M.berjalan ? ' · minggu ini' : ''}</div><div class="kaca-btn kecil ${s.bdSenin ? '' : 'mati'}" data-aksi="bdMinggu" data-arah="1">berikutnya ›</div></div>
      <div class="pita-info ${M.cukup ? 'emas' : 'awas'}" data-k="bd-minggu-kal">${M.kalimat}</div>
      ${M.kelas.length ? M.kelas.map((g, gi) => h`<div class="kartu bd-kelas" data-k="bd-mk-${g.kelas}" style="--i: ${gi};"><div class="hg-kepala"><span class="nm">${g.kelas} ${het(g.het)}</span><span class="md">${g.nPemasok} pemasok · harga beli per kg</span></div>
        <div class="bd-jajar">${g.kolom.map((c, i) => h`<div class="bd-sel ${i === 0 ? 'murah' : ''} ${c.jenis === 'tawaran' ? 'tawar' : ''}" data-k="bd-ms-${c.kunci}-${c.jenis}"><div class="pm">${c.pemasok}</div><div class="n">${RP(c.harga)}</div>
          <div class="k2">${c.jenis === 'tawaran' ? 'tawaran · ditanya ' + c.tanggal.map(bdTgl).join(', ') : 'datang ' + c.tanggal.map(bdTgl).join(', ') + ' · ' + bdKg(c.kg)}${i > 0 ? ' · +' + RP(c.lebih) : ''}</div></div>`)}</div></div>`)
        : h`<div class="kartu" data-k="bd-minggu-kosong"><div class="k2">Belum ada kedatangan maupun harga tawaran minggu ini. Tanya harga ke pemasok lalu ketuk "+ Harga tawaran".</div></div>`}
      ${M.acuan.length ? h`<div class="kartu" data-k="bd-minggu-acuan" style="gap: 2px;"><div class="label">Harga acuan minggu ini</div>${M.acuan.map((e) => h`<div class="k2">${BC.bcTeks(e)}</div>`)}</div>` : ''}
      ${gambarBdEntri(s, E, 'Catatan harga minggu ini')}`;
  }
  function gambarBdBulan(s) {
    const iso = waktu().tanggal; const key = s.bdBulan || iso.slice(0, 7); const B = BD.bdBulan(key, kini()); const A = BC.bcAtur();
    const baris = (x, i) => h`<div class="bd-urut ${x.jenis === 'tawaran' ? 'tawar' : ''} ${i === 0 ? 'murah' : ''}" data-k="bd-u-${x.kunci}-${x.jenis}">
      <div class="no">${x.urut}</div><div class="pm"><b>${x.pemasok}</b><div class="k2">${x.jenis === 'tawaran' ? 'TAWARAN · perkiraan' + (x.ongkirDitebak ? ' · ongkir rata-rata toko' : '') : x.n + ' baris · ' + bdKg(x.kgNyata) + (x.nBelumTimbang ? ' · ' + x.nBelumTimbang + ' belum ditimbang' : '') + (x.nAwas ? ' · ' + x.nAwas + ' mutu AWAS' : '')}</div></div>
      <div class="pecah"><span>nota ${RP(x.hargaKg)}</span><span>+ bongkar & ongkir ${RP(x.bongkarKg)}</span><span>${x.timbangKg >= 0 ? '+' : '−'} timbang ${RP(Math.abs(x.timbangKg))}</span><span class="tb">= modal ${RP(x.modalKg)}</span>
        <span>+ mutu ${RP(x.mutuKg)}</span><span>+ susut ${RP(x.susutKg)} (${bdPersen(x.susutPct)})</span></div>
      <div class="n">${RP(x.layakKg)}<div class="k2">${i === 0 ? 'termurah' : '+' + RP(x.lebihMahal) + '/kg'}</div></div></div>`;
    return h`<div class="bd-nav" data-k="bd-nav-bulan"><div class="kaca-btn kecil" data-aksi="bdGeserBulan" data-arah="-1">‹ bulan lalu</div><div class="nm">${B.nama}${B.berjalan ? ' · berjalan' : ''}</div><div class="kaca-btn kecil ${s.bdBulan ? '' : 'mati'}" data-aksi="bdGeserBulan" data-arah="1">berikutnya ›</div></div>
      <div class="pita-info ${!B.menutup ? 'awas' : B.cukup ? 'emas' : 'awas'}" data-k="bd-bulan-kal">${B.kalimat}</div>
      ${B.kelas.map((g, gi) => h`<div class="kartu bd-kelas" data-k="bd-bk-${g.kelas}" style="--i: ${gi};"><div class="hg-kepala"><span class="nm">${g.kelas}${g.het ? h` <span class="hg-cap">HET ${g.het}</span>` : ''}</span><span class="md">${bdKg(g.kg)} · layak jual per kg, termurah dulu</span></div>
        ${g.baris.map(baris)}<div class="k2" style="margin-top: 4px;">${g.kalimat}</div></div>`)}
      <div class="kartu" data-k="bd-tandai" style="gap: 6px;"><div class="label">Ritual bulanan · ${B.nama}</div>
        ${B.dibanding ? h`<div class="k2">Sudah dibanding ${tanggalPendek(B.dibanding.tanggal)} ${B.dibanding.jam || ''}${B.dibanding.catatan ? ' — ' + B.dibanding.catatan : ''}</div>`
          : h`<div class="k2">Baca urutan di atas (minimal ${A.minPemasok} pemasok), tulis keputusannya kalau ada (mis. "kelas X pindah ke pemasok Y"), lalu tandai. Pengingat tanggal ${A.tanggalBulan} berhenti sesudah ditandai.</div>
            <input class="ketik-nama" type="text" placeholder="Keputusan / temuan (boleh kosong)" value="${s.bdTandai || ''}" data-ketik="bdTandaiKetik" data-k="bd-tandai-ketik">
            <div class="kaca-btn aktif emas" data-aksi="bdTandaiSimpan" data-bulan="${B.key}" data-k="bd-tandai-simpan" style="align-self: flex-start;">Tandai ${B.nama} sudah dibanding</div>`}</div>
      <div class="ket" style="font-size: 11px;" data-k="bd-bulan-ket">Penjaga: Σ modal semua baris (+ ${B.dilewati} baris kemasan jadi / tanpa kg) ${B.menutup ? '=' : '≠'} nilai kedatangan bulan ini di Bon pemasok (${RP(B.sapuan)}). Susut gudang = Laporan › Susut per pemasok, ${BD.BD_BULAN_SUSUT} bulan s.d. ${tanggalPendek(B.susut.akhir)}; rata-rata toko ${bdPersen(B.susut.rataPct)} (dipakai harga tawaran).</div>`;
  }
  function gambarBdRapor(s) {
    const iso = waktu().tanggal; const key = s.bdBulan || iso.slice(0, 7); const R = BD.bdRapor(key, kini());
    const baris = (a, b) => h`<div class="bd-rp-baris"><span>${a}</span><span>${b}</span></div>`;
    return h`<div class="bd-nav" data-k="bd-nav-rapor"><div class="kaca-btn kecil" data-aksi="bdGeserBulan" data-arah="-1">‹ bulan lalu</div><div class="nm">Rapor ${R.nama}${R.berjalan ? ' · berjalan' : ''}</div><div class="kaca-btn kecil ${s.bdBulan ? '' : 'mati'}" data-aksi="bdGeserBulan" data-arah="1">berikutnya ›</div></div>
      <div class="pita-info emas" data-k="bd-rapor-kal">${R.kalimat}</div>
      ${R.pemasok.map((p, i) => { const G = p.kelompok; const T = p.timbang; return h`<div class="kartu bd-rapor" data-k="bd-rp-${p.kunci}" style="--i: ${i};"><div class="hg-kepala"><span class="nm">${p.pemasok}</span><span class="md">${G ? p.kedatangan + ' kedatangan · ' + p.kelas.length + ' kelas' : p.kedatangan ? p.kedatangan + ' kedatangan kemasan jadi' : 'hanya tawaran'}</span></div>
        ${G ? h`<div class="bd-rp">${baris('Belanja (sesudah klaim/retur)', RP(G.uang))}${baris('Bongkar & ongkos kirim', RP(G.bongkar) + ' · ' + RP(G.bongkarKg) + '/kg')}${baris('Kg nota → diterima', bdKg(G.kgNota) + ' → ' + bdKg(G.kgNyata))}
          ${baris('Modal sampai toko', RP(G.modalKg) + '/kg')}${baris('Layak jual', RP(G.layakKg) + '/kg')}</div>` : ''}
        ${G ? h`<div class="bd-rp">${baris('Timbang', T ? (T.ditimbang + T.sebagian ? (T.selisihKg === 0 ? 'pas' : (T.selisihKg < 0 ? 'kurang ' : 'lebih ') + bdKg(Math.abs(T.selisihKg))) + ' (' + bdPersen(T.persen) + ')' + (T.nilaiKurang ? ' · nilai kurang ' + RP(T.nilaiKurang) : '') : 'belum ditimbang') + (T.belumTimbang ? ' · ' + T.belumTimbang + ' kedatangan belum' : '') : '—')}
          ${baris('Mutu', p.tanda.length ? p.tanda.map((x) => x.nama + ' ×' + x.n).join(', ') + (p.potMutuRp ? ' · potongan ' + RP(p.potMutuRp) : '') : T && T.dicek ? 'dicek, tanpa AWAS' : 'belum dicek')}
          ${baris('Retur / ditolak', p.retur.n || p.tolak.n ? bdKg(p.retur.kg) + ' (' + RP(p.retur.rp) + ') · ditolak ' + bdKg(p.tolak.kg) + ' (' + RP(p.tolak.rp) + ')' : 'tidak ada')}
          ${baris('Klaim', p.klaim.n || p.klaim.diminta || p.klaim.disetujui || p.klaim.ditolak ? (p.klaim.rp ? RP(p.klaim.rp) + ' dipotong' : 'belum dipotong') + (p.klaim.diminta ? ' · ' + p.klaim.diminta + ' diminta' : '') + (p.klaim.ditolak ? ' · ' + p.klaim.ditolak + ' ditolak' : '') : 'tidak ada')}
          ${baris('Susut gudang (3 bulan)', bdPersen(p.susut ? p.susut.pct : null))}${baris('Dipesan → datang', p.kirim ? BP.bpHariTeks(p.kirim.rataHari) + ' (' + p.kirim.n + ' pesanan)' : 'belum ada pesanan lewat Belanja')}</div>` : ''}
        ${p.tawaran.length ? h`<div class="k2">Harga tawaran: ${p.tawaran.map((e) => e.kelas + ' ' + RP(e.hargaPerKg) + ' (' + bdTgl(e.tanggal) + ')').join(' · ')}</div>` : ''}${G ? '' : h`<div class="k2">${p.kalimat}</div>`}</div>`; })}
      ${R.pemasok.length ? '' : h`<div class="kartu"><div class="k2">Belum ada kedatangan ${R.nama}.</div></div>`}`;
  }
  function gambarBdAcuan(s) {
    const A = BD.bdAcuan(kini()); const T = A.tarik; const E = BC.bcEntri(A.dari, A.iso).filter((e) => e.jenis === 'acuan');
    return h`<div class="pita-info emas" data-k="bd-acuan-kal">${A.kalimat}</div>
      ${A.acuan.map((e, i) => h`<div class="kartu bd-kelas" data-k="bd-ac-${e.id}" style="--i: ${i};"><div class="hg-kepala"><span class="nm">${e.sumber} · ${e.tingkatNama.split(' /')[0]} ${e.mutu}</span><span class="md">${bdTgl(e.tanggal)}${e.wilayah ? ' · ' + e.wilayah : ''}</span></div>
        <div class="bd-acuan"><div class="n">${RP(e.hargaPerKg)}<span class="k2">/kg${e.gerak ? (e.gerak > 0 ? ' ▲ ' : ' ▼ ') + RP(Math.abs(e.gerak)) : ''}</span></div><div class="k2">${e.kalimat}</div></div></div>`)}
      <div class="kartu" data-k="bd-tarik" style="gap: 4px;"><div class="label">Tarik otomatis · ${T.sumber || 'Panel Harga Bapanas'}</div><div class="${T.ada && T.status === 'gagal' ? 'pita-info awas' : 'k2'}">${T.kalimat}</div>
        ${(T.harga || []).map((x, i) => h`<div class="bd-entri" data-k="bd-t-${i}"><div><div>${x.nama || x.mutu} · ${x.tingkat} ${x.mutu} · ${RP(x.hargaPerKg)}/kg</div><div class="k2">${bdTgl(x.tanggal)}${x.wilayah ? ' · ' + x.wilayah : ''}${x.tebakTingkat ? ' · tingkat harga DITEBAK — periksa di panelharga.badanpangan.go.id sebelum Pakai' : ''}</div></div>
          <div class="kaca-btn kecil ${x.dipakai ? 'mati' : 'aktif'}" data-aksi="bdPakaiTarik" data-i="${i}">${x.dipakai ? 'sudah dicatat' : 'Pakai'}</div></div>`)}</div>
      ${gambarBdEntri(s, E, 'Catatan harga acuan 62 hari')}`;
  }
  function gambarBdTren() {
    const T = BD.bdTren(kini(), BD.BD_TREN); const maks = Math.max(1, ...T.kelas.map((k) => Math.max(0, ...k.titik.filter((t) => t.ada).map((t) => t.modalKg))));
    const min = Math.min(...T.kelas.map((k) => Math.min(Infinity, ...k.titik.filter((t) => t.ada).map((t) => t.modalKg))).filter(isFinite), maks); const lebar = (v) => Math.round(8 + 92 * (v - min * 0.97) / Math.max(1, maks - min * 0.97));
    return h`<div class="pita-info emas" data-k="bd-tren-kal">${T.kalimat} Modal sampai toko per kg, semua pemasok digabung (tertimbang kg).</div>
      ${T.kelas.map((k, i) => h`<div class="kartu bd-kelas" data-k="bd-tr-${k.kelas}" style="--i: ${i};"><div class="hg-kepala"><span class="nm">${k.kelas}${k.het ? h` <span class="hg-cap">HET ${k.het}</span>` : ''}</span><span class="md">${k.kalimat}</span></div>
        ${k.titik.map((t) => h`<div class="bd-tren" data-k="bd-tt-${k.kelas}-${t.key}"><span class="bl">${t.nama}</span>${t.ada ? h`<span class="bt"><i style="width: ${lebar(t.modalKg)}%;"></i></span><span class="n">${RP(t.modalKg)}${t.gerak ? h`<small class="${t.gerak > 0 ? 'naik' : 'turun'}">${t.gerak > 0 ? '▲' : '▼'}${RP(Math.abs(t.gerak))}</small>` : ''}</span>` : h`<span class="bt kosong"></span><span class="n k2">tidak ada kedatangan</span>`}</div>`)}</div>`)}`;
  }

  K.dengar(gambar); dengarkan(() => nanti(gambar));
  let tundaUkur = null; window.addEventListener('resize', () => { clearTimeout(tundaUkur); tundaUkur = setTimeout(gambar, 160); });
  // dipanggil layar Menu / Stok: buka keluarga (katalog | bon | belanja) — lewat penangan yang sama dengan ketukan; pemasok = buka bukunya
  const buka = (keluarga, t) => { AKSI.keluarga({ nama: KELUARGA_ID.indexOf(keluarga) >= 0 ? keluarga : 'katalog' }); if (t && t.pemasok) set({ bukuNama: t.pemasok, tabB: 'buku' }); if (t && t.tab) set(keluarga === 'katalog' ? { tabH: t.tab } : keluarga === 'bon' ? { tabB: t.tab } : keluarga === 'banding' ? { tabD: t.tab } : { tabL: t.tab }); };
  return { keadaan: K, belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan, gambar, buka, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil && (_kotor || !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar); } };
}
