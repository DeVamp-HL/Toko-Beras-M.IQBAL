// LAYAR STOK — GAMBAR & KETUKAN. Beranda Stok S9 (dikunci owner) + tab Wadah literan. Logika & angka di stok-logika.js.
// Layar dimorf (elemen hidup terus) → batang isi, gunung wadah, dan angka bertransisi; baris masuk bergiliran saat lahir.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as S from './stok-logika.js';
import * as L from './jual-logika.js';
import * as C from './stok-catat-logika.js';
import { gambarWadah, gambarKarungStok } from './gambar.js';
import { panelIsiUlang, aksiPanelWadah } from './wadah-panel.js';
import { adeganIsiUlang, adeganBukaKarung } from './adegan.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, hapusDokumen } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_TAB = 'miqbal_baru_stok_tab';
const KUNCI_DRAF_MASUK = 'miqbal_baru_draf_masuk';   // draf barang masuk per perangkat — pulih sesudah layar disegarkan (pola KUNCI_DRAF_MASUK index.html)
const KUNCI_DRAF_COCOK = 'miqbal_baru_draf_cocok';   // hitungan keliling gudang yang belum disimpan
const simpanLokal = (k, v) => { try { if (v) localStorage.setItem(k, JSON.stringify(v)); else localStorage.removeItem(k); } catch (e) { /* abaikan */ } };
const bacaLokal = (k) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } };

export function pasangLayarStok(akar, opsi) {
  const tabAwal = (() => { try { return localStorage.getItem(KUNCI_TAB) || 'gudang'; } catch (e) { return 'gudang'; } })();
  const K = buatKeadaan({ tab: S.TAB_STOK.some((t) => t[0] === tabAwal) ? tabAwal : 'gudang', tanya: 'beli', kabar: '', kabarAwas: false, wadahAktif: null, isiW: null, krKetik: '', krNama: '', krPilih: false, lainPilih: false, atur: null,
    lembar: null, masuk: null, cocok: null, aturC: null, yakinM: false, yakinHapus: false, yakinC: {} });
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; const kini = () => opsi.sekarang() || new Date();
  const waktu = () => L.waktuSekarang(opsi.sekarang() || undefined);

  async function tulis(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }
    try { const x = await tulisDokumen(r.dokumen); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  const keranjangJual = () => ({ keranjang: opsi.keranjangJual().keranjang, antrean: opsi.keranjangJual().antrean });
  // mode "atur susunan": draf di keadaan layar; baru ditulis saat SIMPAN (satu dokumen berisi seluruh aturan)
  const drafAtur = () => { const a = L.aturWadah(); const t = (n) => String(n).replace('.', ','); return { penuh: t(a.penuhKg), puncak: t(a.puncakKg), ulang: t(a.isiUlangKg), takar: t(a.takarKg), daftar: a.daftar.slice(), resep: JSON.parse(JSON.stringify(a.resep)), pilih: null, resepUntuk: null }; };
  const ubahAtur = (f) => { const d = JSON.parse(JSON.stringify(st().atur || drafAtur())); f(d); set({ atur: d }); };
  delegasi(akar, Object.assign({
    tab: ({ t }) => { try { localStorage.setItem(KUNCI_TAB, t); } catch (e) { /* abaikan */ } set({ tab: t, kabar: '' }); },
    tanya: ({ id }) => set({ tanya: id }),
    mode: () => opsi.gantiMode(),
    tutupKabar: () => set({ kabar: '' }),
    pilihWadah: ({ merk }) => set({ wadahAktif: st().wadahAktif === merk ? null : merk, isiW: null, krKetik: '', krNama: '', krPilih: false }),
    // karung di belakang wadah BERNAMA (owner 21 Sep): namanya dipilih dari karung sumber di gudang; membukanya menurunkan tumpukan gudang nama itu
    krPilihBuka: () => set({ krPilih: !st().krPilih }),
    krNama: ({ merk }) => set({ krNama: merk, krPilih: false }),
    lainPilihBuka: () => set({ lainPilih: !st().lainPilih }),
    bukaKarung: async ({ merk, wadah }, el) => { sekali(el.closest('.kartu'), 'pegas', 520); const r = L.susunBukaKarung(merk, waktu(), wadah || '');
      if (await tulis(r)) { set({ krNama: '', krPilih: false, lainPilih: false, isiW: null }); const g = r.gudang; adeganBukaKarung({ nama: merk, wadah: wadah || '', berat: g.kgKarung, dariKarung: g.dariKarung, keKarung: g.keKarung, dariKg: DESIMAL(Math.round(g.dariKg * 10) / 10), keKg: DESIMAL(Math.round(g.keKg * 10) / 10) }); } },
    krKetik: (v) => set({ krKetik: String(v).slice(0, 6) }),
    samakanKarung: async ({ merk, wadah }) => { if (await tulis(L.susunSamakanKarung(merk, st().krKetik, waktu(), wadah || ''))) set({ krKetik: '', krNama: '', krPilih: false, isiW: null }); },
    bukaAtur: () => set({ atur: st().atur ? null : drafAtur(), wadahAktif: null }),
    aturPenuh: (v) => ubahAtur((d) => { d.penuh = String(v).slice(0, 6); }), aturPuncak: (v) => ubahAtur((d) => { d.puncak = String(v).slice(0, 6); }),
    aturUlang: (v) => ubahAtur((d) => { d.ulang = String(v).slice(0, 6); }), aturTakar: (v) => ubahAtur((d) => { d.takar = String(v).slice(0, 6); }),
    aturGeser: ({ i, arah }) => ubahAtur((d) => { d.daftar = L.geserWadah(d.daftar, Number(i), Number(arah)); d.pilih = null; }),
    aturPilih: ({ i }) => ubahAtur((d) => { d.pilih = d.pilih === Number(i) ? null : Number(i); d.resepUntuk = null; }),
    aturGanti: ({ i, merk }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.gantiBerasWadah(d.daftar, Number(i), merk); if (lama && lama !== merk) delete d.resep[lama]; d.pilih = null; }),
    aturLepas: ({ i }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.lepasWadah(d.daftar, Number(i)); delete d.resep[lama]; d.pilih = null; }),
    aturTambah: () => ubahAtur((d) => { d.pilih = d.daftar.length; d.resepUntuk = null; }),
    aturResep: ({ merk }) => ubahAtur((d) => { d.resepUntuk = d.resepUntuk === merk ? null : merk; d.pilih = null; if (!d.resep[merk]) d.resep[merk] = L.resepWadah(merk); }),
    aturResepTakar: ({ merk, j, arah }) => ubahAtur((d) => { const r = d.resep[merk]; if (!r || !r[Number(j)]) return; r[Number(j)].takar = Math.max(0, r[Number(j)].takar + Number(arah)); }),
    aturResepTambah: ({ merk, bahan }) => ubahAtur((d) => { const r = d.resep[merk] || (d.resep[merk] = L.resepWadah(merk)); if (r.length < L.WADAH_MAKS_RESEP && !r.some((x) => x.merk === bahan)) r.push({ merk: bahan, takar: 1 }); }),
    simpanAtur: async () => { const d = st().atur; if (!d) return; const r = L.susunAturWadah({ penuhKg: d.penuh, puncakKg: d.puncak, isiUlangKg: d.ulang, takarKg: d.takar, daftar: d.daftar, resep: d.resep }, waktu()); if (await tulis(r)) set({ atur: null }); },
    lama: () => set({ kabar: 'Mencatat adukan masih lewat sistem lama — menyusul di putaran Stok berikutnya.', kabarAwas: false }),
    // ---- BARANG MASUK (ST1): draf di keadaan layar + localStorage; ditulis saat SIMPAN
    bukaMasuk: () => set({ lembar: 'masuk', masuk: bacaLokal(KUNCI_DRAF_MASUK) || C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false, kabar: '', aturC: null }),
    tutupLembar: () => set({ lembar: null, kabar: '', aturC: null, yakinM: false, yakinHapus: false }),
    mKetik: (v, el) => ubahMasuk((d) => { const k = el.dataset.kolom; const i = el.dataset.i; if (i !== undefined) d.baris[Number(i)][k] = String(v).slice(0, k === 'merk' ? 40 : 12); else d[k] = String(v).slice(0, k === 'alasan' || k === 'pemasok' ? 60 : 12); }),
    mPilih: ({ kolom, i, nilai }) => ubahMasuk((d) => { if (i !== undefined) d.baris[Number(i)][kolom] = kolom === 'beratKarung' ? Number(nilai) : nilai; else d[kolom] = nilai; }),
    mTambahBaris: () => ubahMasuk((d) => { d.baris.push(C.barisMasukKosong()); }),
    mLepasBaris: ({ i }) => ubahMasuk((d) => { if (d.baris.length > 1) d.baris.splice(Number(i), 1); else d.baris[0] = C.barisMasukKosong(); }),
    mBaru: () => { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false, kabar: '' }); },
    mSimpan: async () => { const d = st().masuk; if (!d) return; const r = C.susunSimpanMasuk(d, waktu(), st().yakinM);
      if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true, yakinM: !!r.perluYakin }); return; }
      if (await tulis(r)) { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false }); sekali(akar.querySelector('.stok-masuk'), 'pegas', 520); } },
    mKoreksi: ({ id }) => { const d = C.drafDariKedatangan(id); if (!d) return; if (d.fondasi) return set({ kabar: 'Batch fondasi (stok awal / saldo pembuka) menopang seluruh stok & modal — tidak diubah dari sini', kabarAwas: true });
      set({ masuk: d, yakinM: false, yakinHapus: false, kabar: d.adaBal ? 'Kedatangan ini punya baris bal (beli jadi) — baris itu tidak ikut diubah dari sini' : '', kabarAwas: false }); },
    mHapus: async () => { const d = st().masuk; if (!d || !d.id) return; if (!st().yakinHapus) { const r0 = C.susunHapusKedatangan(d.id, d.alasan, waktu()); if (r0.tolak) return set({ kabar: r0.tolak, kabarAwas: true }); return set({ yakinHapus: true, kabar: 'Ketuk sekali lagi untuk menghapus kedatangan ini — stok & modal dihitung ulang tanpa kedatangan ini', kabarAwas: true }); }
      const r = C.susunHapusKedatangan(d.id, d.alasan, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      try { const x = await hapusDokumen(r.hapus); if (x && x.gagal) return set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); } catch (e) { return set({ kabar: 'GAGAL menghapus: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
      if (await tulis({ dokumen: r.dokumen, patch: r.patch })) { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false }); } },
    // aturan pencatatan (angka kebijakan owner)
    bukaAturC: () => { const a = C.aturCatat(); const t = (n) => String(n).replace('.', ','); set({ aturC: st().aturC ? null : { minKarung: t(a.minKarung), tempoHari: t(a.tempoHari), batasSelisih: t(a.batasSelisih), ambangSusutPositif: String(a.ambangSusutPositif) } }); },
    cKetikAtur: (v, el) => { const a = Object.assign({}, st().aturC || {}); a[el.dataset.kolom] = String(v).slice(0, 12); set({ aturC: a }); },
    simpanAturC: async () => { const a = st().aturC; if (!a) return; if (await tulis(C.susunAturCatat(a, waktu()))) set({ aturC: null }); },
    // ---- COCOKKAN (ST3): hitungan keliling gudang di keadaan layar + localStorage; ditulis saat SIMPAN
    bukaCocok: () => set({ lembar: 'cocok', cocok: bacaLokal(KUNCI_DRAF_COCOK) || cocokKosong(), yakinC: {}, kabar: '', aturC: null }),
    cTab: ({ t }) => ubahCocok((c) => { c.tab = t; c.buka = null; c.karung = ''; c.kg = ''; c.angka = ''; }),
    cBuka: ({ kunci }) => ubahCocok((c) => { c.buka = c.buka === kunci ? null : kunci; c.karung = ''; c.kg = ''; c.angka = ''; }),
    cKetik: (v, el) => ubahCocok((c) => { c[el.dataset.kolom] = String(v).slice(0, 10); }),
    cAlasan: (v, el) => ubahCocok((c) => { c.alasan[el.dataset.kunci] = String(v).slice(0, 60); }),
    cPas: ({ kunci, sistem }) => ubahCocok((c) => { c.hitung[kunci] = String(sistem); if (c.buka === kunci) c.buka = null; }),
    cPakai: ({ kunci, satuan }) => ubahCocok((c) => { if (satuan === 'kg') { const kr = angka(c.karung); const kg = angka(c.kg); c.hitung[kunci] = String(Math.round((kr * (st().beratHitung || 50) + kg) * 100) / 100); } else c.hitung[kunci] = String(angka(c.angka)); c.buka = null; c.karung = ''; c.kg = ''; c.angka = ''; }),
    cBerat: ({ n }) => set({ beratHitung: Number(n) }),
    cHapusHitung: ({ kunci }) => ubahCocok((c) => { delete c.hitung[kunci]; }),
    cBersih: () => { simpanLokal(KUNCI_DRAF_COCOK, null); set({ cocok: cocokKosong(), yakinC: {}, kabar: 'Hitungan dikosongkan', kabarAwas: false }); },
    cSimpan: async () => { const c = st().cocok; if (!c) return; const r = C.susunSimpanCocok(c.tab, c.hitung, c.alasan, waktu(), st().yakinC);
      if (r.tolak) { const y = Object.assign({}, st().yakinC); if (r.perluYakin) y[r.perluYakin] = true; set({ kabar: r.tolak, kabarAwas: true, yakinC: y }); return; }
      if (await tulis(r)) { const sisa = Object.assign({}, c.hitung); r.hitung.baris.forEach((b) => { delete sisa[b.kunci]; }); const al = Object.assign({}, c.alasan); r.hitung.baris.forEach((b) => { delete al[b.kunci]; });
        const c2 = Object.assign({}, c, { hitung: sisa, alasan: al, buka: null }); simpanLokal(KUNCI_DRAF_COCOK, Object.keys(sisa).length ? c2 : null); set({ cocok: c2, yakinC: {} }); } },
  }, aksiPanelWadah({ set, st, tulis, keranjang: keranjangJual, waktu,
    sesudahCatat: (wadah, r) => { const hsl = r.hitung; adeganIsiUlang({ nama: wadah, keterangan: hsl.takar + ' takar · ' + DESIMAL(hsl.kg) + ' kg' + (hsl.banding ? ' · campur ' + hsl.banding : ''), serokan: Math.ceil(hsl.takar / 8), dari: hsl.wadah, ke: L.tinggiWadah(wadah, keranjangJual()) || hsl.wadah }); } })));

  const angka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0; const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
  const cocokKosong = () => ({ tab: 'beras', hitung: {}, alasan: {}, buka: null, karung: '', kg: '', angka: '' });
  const ubahMasuk = (f) => { const d = JSON.parse(JSON.stringify(st().masuk || C.drafMasukKosong(waktu()))); f(d); simpanLokal(KUNCI_DRAF_MASUK, d); set({ masuk: d, yakinM: false, yakinHapus: false }); };
  const ubahCocok = (f) => { const c = JSON.parse(JSON.stringify(st().cocok || cocokKosong())); f(c); simpanLokal(KUNCI_DRAF_COCOK, c); set({ cocok: c, yakinC: {} }); };
  function gambar() {
    if (!tampil) return;
    const s = st(); const sumber = sumberData(); const k = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Stok</div><div class="ket">${tanggalPendek(L.waktuSekarang(k).tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'data toko' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      ${s.lembar === 'masuk' ? gambarMasuk(s) : s.lembar === 'cocok' ? gambarCocok(s) : h`<div class="jalur" data-k="tab">${S.TAB_STOK.map(([id, nm]) => h`<div class="seg ${s.tab === id ? 'aktif' : ''}" data-aksi="tab" data-t="${id}">${nm}</div>`)}</div>
      ${s.tab === 'gudang' ? gambarGudang(s, k) : s.tab === 'wadah' ? gambarTabWadah(s) : s.tab === 'kapur' ? gambarKapur(k) : gambarKarantina()}`}
    `);
    gulirkan(akar, RP);
  }

  function gambarGudang(s, k) {
    const g = S.susunGudang(s.tanya, k); const j = g.jawab;
    return h`<section class="stok-gudang" data-k="gudang">
      <div class="tanya">${g.kartu.map((c) => h`<div class="kartu-t ${c.id === g.aktif ? 'aktif' : ''}" data-aksi="tanya" data-id="${c.id}"><div class="q">${c.q}</div>
        <div class="a ${c.awas ? 'awas' : ''}" ${c.angka !== undefined ? mentah('data-gulir="' + Math.round(c.angka) + '"') : ''}>${c.a}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="jawab-${g.aktif}">
        <div class="label">${g.judul}</div>
        ${j.baris.length ? h`<div class="daftar-jawab">${j.baris.map((b, i) => h`<div class="jawab" data-k="${g.aktif}-${b.kunci}" style="--urut: ${Math.min(i, 16)};">
          <span class="kiri"><span class="nm">${b.nama}</span>${b.karung !== undefined ? h`<span class="tumpuk-mini" data-k="tm-${b.kunci}">${Array.from({ length: Math.min(b.karung, 14) }).map((_, n) => h`<i data-k="tm-${b.kunci}-${n}"></i>`)}${b.karung > 14 ? h`<b>+${b.karung - 14}</b>` : ''}</span>` : ''}<span class="w">${b.ket}</span><span class="batang"><span class="isi-batang ${b.awas ? 'awas' : ''}" style="transform: scaleX(${Math.round(Math.max(0.02, Math.min(1, b.isi)) * 1000) / 1000});"></span></span></span>
          <span class="kanan"><span class="n ${b.awas ? 'awas' : ''}">${b.n}</span><span class="w">${b.nKet}</span></span></div>`)}</div>`
          : h`<div class="menolak" style="padding: 12px 0;">${j.kosong}</div>`}
        <div class="rumus">${j.rumus}</div>
        ${j.takTeks ? h`<div class="ket" style="font-size: 11.5px;">${j.takTeks}</div>` : ''}
      </div>
      <div class="tombol-baris"><div class="kaca-btn aktif" data-aksi="bukaMasuk">Barang masuk</div><div class="kaca-btn" data-aksi="lama">Adukan</div><div class="kaca-btn aktif" data-aksi="bukaCocok">Cocokkan</div></div>
    </section>`;
  }

  function gambarTabWadah(s) {
    const w = S.susunWadah(keranjangJual()); const a = w.atur; const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const tumpukanTeks = (t) => (!t.adaBuku ? t.merk + ' tidak ada di buku gudang' : t.minus ? 'tumpukan ' + t.merk + ' di gudang: buku KURANG ' + KG(-t.kg) + ' dari yang sudah di wadah & karung terbuka — cocokkan stok' : 'tumpukan ' + t.merk + ' di gudang ±' + t.karung + ' karung (' + KG(t.kg) + ') · buku ' + KG(t.bukuKg) + (t.lengkap ? '' : ' · perkiraan, ada yang belum ditandai'));
    if (s.atur) return gambarAturWadah(s.atur, w);
    const aktif = w.daftar.find((x) => x.nama === s.wadahAktif) || null;
    return h`<section class="stok-wadah" data-k="wadah">
      <div class="pita-info">Tumpukan karung di gudang → satu karung bernama, terbuka di belakang tiap wadah → kotak wadah → dijual per liter. Buka karung: tumpukan gudang nama itu turun satu karung. Takar: karung di belakang turun, wadah naik. Literan terjual: wadah turun.
        ${w.perluIsi ? w.perluIsi + ' wadah minta diisi ulang. ' : ''}${w.karungTipis ? w.karungTipis + ' karung di belakang hampir habis. ' : ''}${w.belumDitandai ? w.belumDitandai + ' wadah belum pernah ditandai isinya.' : ''}</div>
      <div class="petak-wadah" data-k="petak">${w.daftar.map((x, i) => h`<div class="kartu petak ${x.nama === s.wadahAktif ? 'dipilih' : ''} ${x.diketahui && x.perluIsi ? 'isi-ulang' : ''}" data-k="petak-${x.nama}" data-aksi="pilihWadah" data-merk="${x.nama}" style="--urut: ${i};">
        <div class="no">${x.no}</div>
        <div class="tumpuk-gambar"><div class="gambar-karung">${mentah(gambarKarungStok(x.karung))}</div><div class="gambar-kotak">${mentah(gambarWadah(x))}</div></div>
        <div class="nm">${x.nama}</div>
        <div class="ket">karung ${x.karungNama !== x.nama ? x.karungNama + ' ' : ''}${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}</div>
        <div class="ket">wadah ${x.diketahui ? '±' + KG(x.sisaKg) : '?'}</div>
      </div>`)}</div>
      <div class="kaca-btn" data-aksi="bukaAtur">Atur susunan, isi &amp; aturan wadah</div>
      ${aktif ? h`<div class="kartu rincian-wadah" data-k="rincian-${aktif.nama}">
        <div class="label">${aktif.no} · ${aktif.nama}${aktif.resep.length > 1 ? ' · campuran ' + aktif.resep.map((r) => r.takar).join(' : ') + ' — ' + aktif.resep.map((r) => r.merk).join(' : ') : ''}</div>
        ${(() => { const nk = s.krNama || aktif.karungNama; const draf = nk !== aktif.karungNama; const kr = draf ? L.karungBelakang(nk, aktif.nama) : aktif.karung; const tg = draf ? L.tumpukanGudang(nk) : aktif.tumpukan; const calon = s.krPilih ? L.calonKarung() : [];
          return h`<div class="baris-wadah" data-k="kr-${nk}"><div class="gambar-chip besar">${mentah(gambarKarungStok(kr))}</div>
          <div><div class="label">Karung di belakang · dari tumpukan gudang</div>
            <div class="serif" style="font-size: 19px;">${nk} ${kr.diketahui ? '±' + KG(kr.sisaKg) : '— belum ditandai'}</div>
            <div class="ket">${draf ? 'BELUM dicatat: buka satu karung ' + nk + ' atau ketik sisanya — baru karung ini jadi karung di belakang ' + aktif.nama + '.'
              : kr.diketahui ? 'dari ' + kr.penuhKg + ' kg · terakhir ' + tanggalPendek(kr.sejakTanggal) + ' ' + kr.sejakJam + (kr.lewat ? ' · takar yang tercatat ' + KG(kr.lewat) + ' LEBIH dari isi karungnya — samakan' : '') : 'Buka satu karung baru dari tumpukan gudang, atau ketik sisa karung yang sedang terbuka.'}</div>
            <div class="ket">${tumpukanTeks(tg)}</div></div></div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${kr.diketahui && kr.sisaKg > a.takarKg * 3 ? '' : 'aktif'}" data-aksi="bukaKarung" data-merk="${nk}" data-wadah="${aktif.nama}">Buka 1 karung ${nk} dari tumpukan gudang</div>
          <div class="kaca-btn putus" data-aksi="krPilihBuka">${s.krPilih ? 'batal' : 'karung lain…'}</div></div>
        ${s.krPilih ? h`<div class="tombol-baris rapat" data-k="calon-karung">${calon.length ? calon.map((t) => h`<div class="kaca-btn ${t.merk === nk ? 'aktif' : ''}" data-aksi="krNama" data-merk="${t.merk}">${t.merk} · ${t.karung} karung${t.dipegang.length ? ' · sudah terbuka di belakang ' + t.dipegang.join(', ') : ''}</div>`) : h`<div class="ket">Menurut buku, tidak ada karung di tumpukan gudang.</div>`}</div>` : ''}
        <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="krKetik" type="text" inputmode="decimal" placeholder="sisa kg" value="${s.krKetik}" data-ketik="krKetik"><div class="kaca-btn ${String(s.krKetik || '').trim() ? '' : 'mati'}" data-aksi="samakanKarung" data-merk="${nk}" data-wadah="${aktif.nama}">samakan sisa karung ${nk}</div></div>`; })()}
        ${panelIsiUlang(aktif.nama, s, keranjangJual())}
      </div>` : h`<div class="ket" style="text-align: center;">Ketuk satu wadah untuk mengisi ulang atau menandai karungnya.</div>`}
      <div class="kartu" data-k="karung-lain" style="gap: 6px;"><div class="label">Karung terbuka lain · bahan campuran, tidak di belakang wadah</div>
        ${w.lain.length ? w.lain.map((x) => h`<div class="jawab" data-k="kl-${x.nama}|${x.lokasi}"><span class="kiri"><span class="nm">${x.nama}${x.lokasi ? ' · dulu di belakang wadah ' + x.lokasi : ''}</span><span class="w">${tumpukanTeks(x.tumpukan)}</span></span>
          <span class="kanan"><span class="n">${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}</span><span class="w tautan" data-aksi="bukaKarung" data-merk="${x.nama}">buka karung baru</span></span></div>`) : h`<div class="ket">Belum ada.</div>`}
        <div class="ket tautan" data-aksi="lainPilihBuka">${s.lainPilih ? 'batal' : '+ buka karung bahan campuran dari gudang'}</div>
        ${s.lainPilih ? h`<div class="tombol-baris rapat" data-k="calon-lain">${L.calonKarung().map((t) => h`<div class="kaca-btn" data-aksi="bukaKarung" data-merk="${t.merk}">${t.merk} · ${t.karung} karung${t.dipegang.length ? ' · sudah terbuka di belakang ' + t.dipegang.join(', ') : ''}</div>`)}</div>` : ''}</div>
      <div class="kartu" data-k="atur-wadah" style="gap: 4px;"><div class="label">Aturan wadah ${a.dariOwner ? '· diatur owner ' + tanggalPendek(a.sejak) : '· bawaan'}</div>
        <div class="ket">rata sejajar bibir kotak ${DESIMAL(a.penuhKg)} kg · menggunung sampai ${DESIMAL(a.puncakKg)} kg · minta isi ulang saat tersisa ${DESIMAL(a.isiUlangKg)} kg · 1 takar ${DESIMAL(a.takarKg)} kg · ${a.daftar.length} wadah</div>
        <div class="ket">Tiap tingkat turun lewat jalurnya sendiri: buka karung → tumpukan gudang · takar → karung di belakang (wadah naik) · literan terjual → wadah. Buku mesin lama tetap dipotong sekali saja, saat terjual — jumlah tumpukan + karung terbuka + isi wadah selalu sama dengan buku.</div></div>
    </section>`;
  }

  function gambarAturWadah(d, w) {
    const calonWadah = L.calonBerasWadah(d.daftar); const pos = d.pilih;
    return h`<section class="stok-wadah" data-k="wadah-atur">
      <div class="pita-info emas">Atur susunan: ‹ › memindah posisi kotak · ketuk nama untuk mengganti berasnya · "campuran" menyetel perbandingan takar bawaan. Belum tersimpan sampai SIMPAN.</div>
      <div class="petak-wadah atur" data-k="petak-atur">${d.daftar.map((m, i) => h`<div class="kartu petak ${pos === i ? 'dipilih' : ''}" data-k="pa-${m}">
        <div class="no">W${i + 1}</div><div class="nm tautan" data-aksi="aturPilih" data-i="${i}">${m}</div>
        <div class="geser"><div class="kaca-btn ${i === 0 ? 'mati' : ''}" data-aksi="aturGeser" data-i="${i}" data-arah="-1">‹</div><div class="kaca-btn ${i === d.daftar.length - 1 ? 'mati' : ''}" data-aksi="aturGeser" data-i="${i}" data-arah="1">›</div></div>
        <div class="ket tautan" data-aksi="aturResep" data-merk="${m}">${(d.resep[m] || []).filter((x) => x.takar > 0).length > 1 ? 'campuran ' + d.resep[m].filter((x) => x.takar > 0).map((x) => x.takar).join(' : ') : 'campuran'}</div>
      </div>`)}<div class="kartu petak putus ${pos === d.daftar.length ? 'dipilih' : ''}" data-k="pa-tambah" data-aksi="aturTambah"><div class="no">+</div><div class="nm">tambah wadah</div></div></div>
      ${pos !== null && pos !== undefined ? h`<div class="kartu" data-k="atur-pilih" style="gap: 8px;"><div class="label">${pos < d.daftar.length ? 'W' + (pos + 1) + ' sekarang ' + d.daftar[pos] + ' — ganti dengan beras mana?' : 'Wadah baru W' + (pos + 1) + ' — beras mana?'}</div>
        <div class="tombol-baris rapat">${calonWadah.length ? calonWadah.map((m) => h`<div class="kaca-btn" data-aksi="aturGanti" data-i="${pos}" data-merk="${m}">${m}</div>`) : h`<div class="ket">Semua beras literan sudah punya wadah.</div>`}</div>
        ${pos < d.daftar.length ? h`<div class="kaca-btn putus" data-aksi="aturLepas" data-i="${pos}">lepas W${pos + 1} — ${d.daftar[pos]} jadi diserok langsung dari karung</div>` : ''}</div>` : ''}
      ${d.resepUntuk && d.daftar.indexOf(d.resepUntuk) >= 0 ? (() => { const m = d.resepUntuk; const r = d.resep[m] || L.resepWadah(m); const calon = L.calonCampur(r.map((x) => x.merk));
        return h`<div class="kartu" data-k="atur-resep" style="gap: 8px;"><div class="label">Campuran bawaan ${m} · perbandingan takar</div>
          ${r.map((x, j) => h`<div class="baris-takar" data-k="rs-${x.merk}"><span class="kiri"><span class="nm">${x.merk}</span></span>
            <span class="langkah"><div class="kaca-btn" data-aksi="aturResepTakar" data-merk="${m}" data-j="${j}" data-arah="-1">−</div><span class="n">${x.takar} <span class="ket">takar</span></span><div class="kaca-btn aktif" data-aksi="aturResepTakar" data-merk="${m}" data-j="${j}" data-arah="1">+</div></span></div>`)}
          ${r.length < L.WADAH_MAKS_RESEP ? h`<div class="ket">tambah karung ke campuran:</div><div class="tombol-baris rapat">${calon.map((b) => h`<div class="kaca-btn" data-aksi="aturResepTambah" data-merk="${m}" data-bahan="${b}">${b}</div>`)}</div>` : ''}</div>`; })() : ''}
      <div class="kartu" data-k="atur-angka" style="gap: 8px;"><div class="label">Angka wadah</div><div class="ps-form dua">
        <div><div class="ket">Rata sejajar bibir kotak (kg)</div><input class="ketik-nama" id="aturPenuh" type="text" inputmode="decimal" value="${d.penuh}" data-ketik="aturPenuh"></div>
        <div><div class="ket">Batas menggunung (kg)</div><input class="ketik-nama" id="aturPuncak" type="text" inputmode="decimal" value="${d.puncak}" data-ketik="aturPuncak"></div>
        <div><div class="ket">Minta isi ulang saat tersisa (kg)</div><input class="ketik-nama" id="aturUlang" type="text" inputmode="decimal" value="${d.ulang}" data-ketik="aturUlang"></div>
        <div><div class="ket">Isi satu takar / serok (kg)</div><input class="ketik-nama" id="aturTakar" type="text" inputmode="decimal" value="${d.takar}" data-ketik="aturTakar"></div></div></div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN SUSUNAN &amp; ATURAN</div></div>
    </section>`;
  }

  // ---------- BARANG MASUK (ST1): satu kedatangan = pemasok · tanggal · baris nama × karung × harga/kg · cara bayar · upah bongkar ----------
  function gambarAturC(s) {
    const a = s.aturC; if (!a) return '';
    return h`<div class="kartu" data-k="atur-catat" style="gap: 8px;"><div class="label">Aturan pencatatan · angka owner</div><div class="ps-form dua">
      <div><div class="ket">Satu mobil minimal (karung)</div><input class="ketik-nama" id="acMin" type="text" inputmode="numeric" value="${a.minKarung}" data-ketik="cKetikAtur" data-kolom="minKarung"></div>
      <div><div class="ket">Tempo bon pemasok (hari)</div><input class="ketik-nama" id="acTempo" type="text" inputmode="numeric" value="${a.tempoHari}" data-ketik="cKetikAtur" data-kolom="tempoHari"></div>
      <div><div class="ket">Selisih wajar cocokkan (%)</div><input class="ketik-nama" id="acBatas" type="text" inputmode="decimal" value="${a.batasSelisih}" data-ketik="cKetikAtur" data-kolom="batasSelisih"></div>
      <div><div class="ket">Stok bertambah tanpa pembelian, ditanya di atas (Rp)</div><input class="ketik-nama" id="acAmbang" type="text" inputmode="numeric" value="${a.ambangSusutPositif}" data-ketik="cKetikAtur" data-kolom="ambangSusutPositif"></div></div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturC">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturC">SIMPAN ATURAN</div></div></div>`;
  }
  function gambarMasuk(s) {
    const d = s.masuk || C.drafMasukKosong(waktu()); const hm = C.hitungMasuk(d); const a = C.aturCatat(); const koreksi = !!d.id; const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const pemasok = C.calonPemasok().slice(0, 6); const merk = C.calonMerkMasuk();
    return h`<section class="stok-masuk" data-k="masuk">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${koreksi ? 'Koreksi kedatangan' : 'Barang masuk'}</div><div class="ket">${koreksi ? d.pemasok + ' · ' + tanggalPendek(d.tanggal) : 'satu mobil = satu catatan · harga per kg + upah bongkar jadi modal tiap nama'}</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      <div class="kartu" data-k="masuk-kepala" style="gap: 8px;">
        <div class="ps-form dua"><div><div class="ket">Tanggal datang</div><input class="ketik-nama" id="mTanggal" type="date" value="${d.tanggal}" data-ketik="mKetik" data-kolom="tanggal"></div>
          <div><div class="ket">Upah bongkar (Rp, tunai)</div><input class="ketik-nama" id="mBongkar" type="text" inputmode="numeric" placeholder="0" value="${d.bongkar}" data-ketik="mKetik" data-kolom="bongkar"></div></div>
        <div><div class="ket">Pemasok</div><input class="ketik-nama" id="mPemasok" type="text" placeholder="nama pemasok" value="${d.pemasok}" data-ketik="mKetik" data-kolom="pemasok">
          ${pemasok.length ? h`<div class="tombol-baris rapat" data-k="calon-pemasok">${pemasok.map((p) => h`<div class="kaca-btn kecil ${d.pemasok === p ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="pemasok" data-nilai="${p}">${p}</div>`)}</div>` : ''}</div>
        <div class="jalur" data-k="cara-bayar"><div class="seg ${d.caraBayar !== 'utang' ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="caraBayar" data-nilai="tunai">Tunai — keluar laci hari ini</div><div class="seg ${d.caraBayar === 'utang' ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="caraBayar" data-nilai="utang">Bon pemasok</div></div>
        ${d.caraBayar === 'utang' && a.tempoHari ? h`<div class="ket">bon jatuh tempo ${a.tempoHari} hari dari tanggal datang (setelan owner) — masuk buku bon pemasok</div>` : ''}
      </div>
      ${hm.baris.map((b, i) => h`<div class="kartu baris-masuk ${b.terisi && b.masalah ? 'awas' : ''}" data-k="mb-${i}" style="gap: 6px;">
        <div class="label">Baris ${i + 1}${b.sah ? ' · ' + KG(b.totalKg) + ' · ' + RP(b.subtotalHarga) : ''}</div>
        <input class="ketik-nama" id="mMerk${i}" type="text" placeholder="nama beras / karung" value="${d.baris[i].merk}" data-ketik="mKetik" data-kolom="merk" data-i="${i}">
        ${!b.merk ? h`<div class="tombol-baris rapat" data-k="calon-merk-${i}">${merk.slice(0, 8).map((m) => h`<div class="kaca-btn kecil" data-aksi="mPilih" data-kolom="merk" data-i="${i}" data-nilai="${m}">${m}</div>`)}</div>` : ''}
        <div class="ps-form tiga"><div><div class="ket">Karung</div><input class="ketik-nama" id="mJml${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].jumlahKarung}" data-ketik="mKetik" data-kolom="jumlahKarung" data-i="${i}"></div>
          <div><div class="ket">Harga / kg${b.hargaLalu ? ' · lalu ' + RP(b.hargaLalu) : ''}</div><input class="ketik-nama" id="mHarga${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].hargaPerKg}" data-ketik="mKetik" data-kolom="hargaPerKg" data-i="${i}"></div>
          <div><div class="ket">Isi karung</div><div class="jalur rapat">${C.BERAT_KARUNG_PILIHAN.map((n) => h`<div class="seg ${Number(d.baris[i].beratKarung) === n ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="beratKarung" data-i="${i}" data-nilai="${n}">${n} kg</div>`)}</div></div></div>
        <div class="ket ${b.terisi && b.masalah ? 'awas-teks' : ''}">${b.terisi && b.masalah ? b.masalah : b.sah ? 'modal ' + RP(Math.round(b.hppPerKg)) + '/kg' + (b.alokasiBongkar ? ' (termasuk bongkar ' + RP(b.alokasiBongkar) + ')' : '') + (b.hargaLalu && Math.abs(b.hargaPerKg - b.hargaLalu) / b.hargaLalu > 0.1 ? ' · beda ' + Math.round(Math.abs(b.hargaPerKg - b.hargaLalu) / b.hargaLalu * 100) + ' % dari harga lalu' : '') : 'isi nama, jumlah karung, dan harga per kg'}${hm.baris.length > 1 || b.terisi ? h`<span class="tautan" style="float: right;" data-aksi="mLepasBaris" data-i="${i}">lepas baris</span>` : ''}</div>
      </div>`)}
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="mTambahBaris">+ baris nama lain</div>${!koreksi && (d.pemasok || hm.sah.length) ? h`<div class="kaca-btn" data-aksi="mBaru">kosongkan</div>` : ''}</div>
      <div class="kartu" data-k="masuk-ringkas" style="gap: 4px;"><div class="label">Jumlah</div>
        <div class="serif" style="font-size: 19px;">${hm.karung} karung · ${KG(hm.kg)}</div>
        <div class="ket">beras ${RP(hm.nilaiBeras)}${hm.bongkar ? ' + bongkar ' + RP(hm.bongkar) : ''} = <b>${RP(hm.total)}</b> · ${d.caraBayar === 'utang' ? 'jadi bon pemasok' : 'tunai dari laci'}${hm.bongkar ? ' (bongkar selalu tunai)' : ''}</div>
        ${koreksi ? h`<input class="ketik-nama" id="mAlasan" type="text" placeholder="alasan koreksi / hapus (wajib)" value="${d.alasan || ''}" data-ketik="mKetik" data-kolom="alasan">` : ''}
        <div class="kaca-btn aktif emas" data-aksi="mSimpan">${koreksi ? 'SIMPAN KOREKSI' : 'SIMPAN BARANG MASUK · ' + RP(hm.total)}</div>
        ${koreksi ? h`<div class="tombol-baris rapat"><div class="kaca-btn ${s.yakinHapus ? 'awas' : 'putus'}" data-aksi="mHapus">${s.yakinHapus ? 'YAKIN HAPUS kedatangan ini' : 'hapus kedatangan'}</div><div class="kaca-btn" data-aksi="mBaru">batal koreksi</div></div>` : ''}
        ${koreksi && d.riwayat ? '' : ''}</div>
      <div class="kartu" data-k="buku-kedatangan" style="gap: 6px;"><div class="label">Buku kedatangan · ketuk untuk koreksi</div>
        ${C.daftarKedatangan(12).map((k) => h`<div class="jawab ${d.id && String(d.id) === String(k.id) ? 'dipilih' : ''}" data-k="bk-${k.id}" data-aksi="mKoreksi" data-id="${k.id}"><span class="kiri"><span class="nm">${k.pemasok} <span class="w">· ${tanggalPendek(k.tanggal)}${k.jam ? ' ' + k.jam : ''}</span></span><span class="w">${k.ringkas}${k.dikoreksi ? ' · dikoreksi' : ''}</span></span>
          <span class="kanan"><span class="n">${k.fondasi ? 'fondasi' : RP(k.nilai)}</span><span class="w">${k.fondasi ? 'tidak diubah' : k.karung + ' karung · ' + (k.cara === 'utang' ? 'bon' : 'tunai')}</span></span></div>`)}</div>
      ${C.bukuHapus(6).length ? h`<div class="kartu" data-k="buku-hapus" style="gap: 4px;"><div class="label">Buku hapus</div>${C.bukuHapus(6).map((x) => h`<div class="ket" data-k="bh-${x.id}">${tanggalPendek(x.tanggal)} ${x.jam} · ${x.pemasok} ${tanggalPendek(x.tanggalDok)} · ${x.ringkas} — ${x.alasan}</div>`)}</div>` : ''}
      <div class="ket tautan" data-aksi="bukaAturC">${s.aturC ? 'tutup aturan' : 'Atur: minimal karung per mobil, tempo bon, selisih wajar'}</div>${gambarAturC(s)}
    </section>`;
  }
  // ---------- COCOKKAN / HITUNG GUDANG (ST3): beras (karung × isi + kg lepas), kemasan jadi (unit), kantong (lembar) ----------
  function gambarCocok(s) {
    const c = s.cocok || cocokKosong(); const r = C.susunCocok(c.tab, c.hitung, c.alasan, s.yakinC); const berat = s.beratHitung || 50;
    const aktif = r.baris.find((b) => b.kunci === c.buka) || null; const KG = (n) => DESIMAL(Math.round(n * 100) / 100);
    const nilai = (b) => (b.satuan === 'kg' ? KG(b.sistem) + ' kg' : b.sistem + ' ' + b.satuan);
    return h`<section class="stok-cocok" data-k="cocok">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Cocokkan · hitung gudang</div><div class="ket">tercatat vs dihitung · selisih kg DAN rupiah · kurang = susut memotong laba, lebih = stok naik tanpa mengubah modal</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      <div class="jalur" data-k="tab-cocok">${C.TAB_COCOK.map(([id, nm]) => h`<div class="seg ${c.tab === id ? 'aktif' : ''}" data-aksi="cTab" data-t="${id}">${nm}</div>`)}</div>
      <div class="op-ringkas" data-k="ringkas-cocok"><div>dihitung<b>${r.dihitung} / ${r.semua}</b></div><div>susut (potong laba)<b>${RP(r.susutRp)}</b></div><div>lebih (stok naik)<b>${RP(r.lebihRp)}</b></div></div>
      <div class="kaca-btn ${r.dihitung ? 'aktif emas' : 'mati'}" data-aksi="cSimpan">${r.tolak && !r.perluYakin ? r.tolak : 'SIMPAN COCOKKAN · ' + r.berubah + ' berubah'}</div>
      ${aktif ? h`<div class="kartu rincian-wadah" data-k="panel-${aktif.kunci}" style="gap: 8px;"><div class="label">${aktif.nama}</div>
        <div class="ket">tercatat ${nilai(aktif)} · modal ${RP(aktif.modal)}/${aktif.satuan}${aktif.cocokAkhir ? ' · terakhir dicocokkan ' + aktif.cocokAkhir : ' · belum pernah dicocokkan'}</div>
        ${aktif.rincian ? h`<div class="ket">${aktif.rincian}</div>` : ''}
        ${aktif.satuan === 'kg' ? h`<div class="ps-form tiga"><div><div class="ket">Karung utuh</div><input class="ketik-nama" id="ckKarung" type="text" inputmode="numeric" placeholder="0" value="${c.karung}" data-ketik="cKetik" data-kolom="karung"></div>
            <div><div class="ket">Kg lepas (wadah, karung terbuka)</div><input class="ketik-nama" id="ckKg" type="text" inputmode="decimal" placeholder="0" value="${c.kg}" data-ketik="cKetik" data-kolom="kg"></div>
            <div><div class="ket">Isi karung</div><div class="jalur rapat">${C.BERAT_KARUNG_PILIHAN.map((n) => h`<div class="seg ${berat === n ? 'aktif' : ''}" data-aksi="cBerat" data-n="${n}">${n} kg</div>`)}</div></div></div>
          <div class="ket">${angka(c.karung)} × ${berat} + ${DESIMAL(angka(c.kg))} = <b>${KG(angka(c.karung) * berat + angka(c.kg))} kg</b> dihitung</div>`
          : h`<div><div class="ket">Dihitung (${aktif.satuan})</div><input class="ketik-nama" id="ckAngka" type="text" inputmode="numeric" placeholder="0" value="${c.angka}" data-ketik="cKetik" data-kolom="angka"></div>`}
        <div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="cPakai" data-kunci="${aktif.kunci}" data-satuan="${aktif.satuan}">PAKAI HITUNGAN INI</div><div class="kaca-btn" data-aksi="cPas" data-kunci="${aktif.kunci}" data-sistem="${aktif.sistem}">✓ cocok persis</div></div>
        ${aktif.ada ? h`<div class="ket ${aktif.selisih < 0 ? 'awas-teks' : ''}">dihitung ${aktif.satuan === 'kg' ? KG(aktif.dihitung) + ' kg' : aktif.dihitung + ' ' + aktif.satuan} → ${aktif.selisih === 0 ? 'cocok persis' : 'selisih ' + (aktif.selisih > 0 ? '+' : '') + (aktif.satuan === 'kg' ? KG(aktif.selisih) + ' kg' : aktif.selisih + ' ' + aktif.satuan) + ' = ' + RP(aktif.rp) + (aktif.selisih < 0 ? ' (susut)' : ' (stok naik)')}${aktif.aneh ? ' · ANEH: lebih dari dua kali tercatat, cek lagi' : ''}</div>` : ''}
        ${aktif.besar ? h`<div><div class="ket">Selisih lebih dari ${r.batasSelisih} % — alasannya (wajib)</div><input class="ketik-nama" id="ckAlasan-${aktif.kunci}" type="text" placeholder="mis. tumpah waktu bongkar" value="${aktif.alasan}" data-ketik="cAlasan" data-kunci="${aktif.kunci}"></div>` : ''}
        ${aktif.ada ? h`<div class="ket tautan" data-aksi="cHapusHitung" data-kunci="${aktif.kunci}">hapus hitungan ini</div>` : ''}</div>` : h`<div class="ket" style="text-align: center;">Ketuk barangnya lalu isi hasil hitungannya, atau ✓ kalau cocok persis. Hitungan tersimpan di HP ini sampai disimpan.</div>`}
      <div class="kartu" data-k="daftar-cocok" style="gap: 2px;">${r.baris.length ? r.baris.map((b) => h`<div class="jawab ${b.kunci === c.buka ? 'dipilih' : ''}" data-k="cb-${b.kunci}" data-aksi="cBuka" data-kunci="${b.kunci}">
          <span class="kiri"><span class="nm">${b.nama}</span><span class="w">tercatat ${nilai(b)}${b.ada ? ' · dihitung ' + (b.satuan === 'kg' ? KG(b.dihitung) : b.dihitung) : ''}${b.cocokAkhir ? '' : ' · belum pernah dicocokkan'}</span></span>
          <span class="kanan"><span class="n ${b.ada && b.selisih < 0 ? 'awas' : ''}">${!b.ada ? '—' : b.selisih === 0 ? 'cocok' : (b.selisih > 0 ? '+' : '') + (b.satuan === 'kg' ? KG(b.selisih) + ' kg' : b.selisih)}</span><span class="w ${b.perluAlasan ? 'awas-teks' : ''}">${b.perluAlasan ? 'butuh alasan · ' : ''}${b.ada && b.selisih ? RP(b.rp) : b.ada ? '✓' : ''}</span></span></div>`) : h`<div class="ket">Tidak ada barang di kelompok ini.</div>`}</div>
      ${r.dihitung ? h`<div class="ket tautan" data-aksi="cBersih">kosongkan semua hitungan</div>` : ''}
      ${C.riwayatCocok(6).length ? h`<div class="kartu" data-k="riwayat-cocok" style="gap: 4px;"><div class="label">Hitungan sebelumnya</div>${C.riwayatCocok(6).map((g) => h`<div data-k="rc-${g.kunci}"><div class="ket"><b>${tanggalPendek(g.tanggal)} ${g.jam}</b> · ${g.baris.length} barang · ${RP(g.rp)}</div>${g.baris.map((x, i) => h`<div class="ket" style="padding-left: 10px;" data-k="rc-${g.kunci}-${i}">${x.nama} ${x.teks} · ${RP(x.rp)}${x.alasan ? ' · ' + x.alasan : ''}</div>`)}</div>`)}</div>` : ''}
      <div class="ket tautan" data-aksi="bukaAturC">${s.aturC ? 'tutup aturan' : 'Atur: selisih wajar & ambang stok bertambah'}</div>${gambarAturC(s)}
    </section>`;
  }

  function gambarKapur(k) {
    const p = S.susunKapur(k);
    return h`<section data-k="kapur"><div class="kartu" style="gap: 4px; padding: 10px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Papan Kapur · perubahan stok hari ini</div><div class="ket" style="font-size: 11px;">${p.banyak} catatan</div></div>
      ${p.baris.length ? p.baris.map((x, i) => h`<div class="kapur ${x.jenis}" data-k="kp-${x.k}" style="--urut: ${Math.min(i, 16)};"><span class="w">${x.jam}</span><span class="isi-kapur">${x.isi}</span><span class="n">${x.n}</span></div>`) : h`<div class="menolak" style="padding: 12px 0;">Belum ada perubahan stok hari ini.</div>`}
    </div></section>`;
  }

  function gambarKarantina() {
    const q = S.susunKarantina();
    return h`<section data-k="karantina"><div class="kartu" style="gap: 8px; padding: 12px 14px;">
      <div class="label">Karantina · barang kembali yang belum diputuskan</div>
      ${q.baris.length ? h`<div class="pita-info awas">${q.baris.length} barang · ${DESIMAL(q.totalKg)} kg menunggu keputusan (layak jual / rework / kembali ke pemasok / buang) — memutuskannya masih lewat sistem lama.</div>
        ${q.baris.map((x) => h`<div class="jawab" data-k="q-${x.k}"><span class="kiri"><span class="nm">${x.nama}</span><span class="w">${tanggalPendek(x.tanggal)} · ${x.catatan}</span></span><span class="kanan"><span class="n">${DESIMAL(x.kg)} kg</span></span></div>`)}`
        : h`<div class="menolak">Karantina kosong — tidak ada barang kembali yang menunggu diputuskan.</div>`}
    </div></section>`;
  }

  K.dengar(gambar);
  dengarkan(() => gambar());
  return { gambar, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil) gambar(); } };
}
