// LAYAR JUAL — GAMBAR & KETUKAN. Satu markup untuk tiga lebar; lebar diatur css/kerangka.css.
// Logika (rak, tagihan, antrean, bayar) ada di jual-logika.js dan diuji tanpa peramban.
import { h, mentah, gabung, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, ANGKA, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as L from './jual-logika.js';
import * as RT from './retur-logika.js';
import * as WJ from './wadah-jual-logika.js';
import * as ST from './struk-logika.js';
import { kunciPelanggan } from '../mesin/pembantu.js';
import { hariIniIso } from '../inti/format.js';
import { sumberData, dengarkan, tulisDokumen, hapusDokumen } from '../data/toko.js';
import { gulirkan, terbangkan, tengah, sekali } from '../inti/gerak.js';
import { adeganSerok, adeganKemasanMasuk, adeganSerahTerima, adeganTerimaUang, adeganIsiUlang, adeganPanggul, adeganMuat, adeganTuangJahit } from './adegan.js';

import { gambarChipBarang } from './gambar.js';
import { panelIsiUlang, aksiPanelWadah } from './wadah-panel.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
  hapus: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg>',
};
const TUTS = ['1', '2', '3', '⌫', '4', '5', '6', ',', '7', '8', '9', '0'];

export function pasangLayarJual(akar, opsi) {
  const K = buatKeadaan(L.keadaanAwal());
  const set = (patch) => K.setel(patch);
  const S = () => K.baca();

  const aksi = {
    jalur: ({ jalur }) => set({ jalur, lembar: null, pilih: null }),
    mode: () => opsi.gantiMode(),
    chip: ({ jalur, kunci, berat }) => { const rak = rakKini(); const c = (rak[jalur] || []).find((x) => x.kunci === kunci && (!berat || String(x.berat) === berat)); if (c) set(Object.assign({ isiW: null }, L.ketukChip(S(), c))); },
    sering: ({ id }) => { const c = rakKini().sering.find((x) => x.id === id); if (c) set(L.ketukChip(S(), c)); },
    tuts: ({ t }) => set(L.tekanTuts(S(), t)),
    preset: ({ n }, el) => masukDenganGerak(L.masukkan(S(), Number(n)), el),
    masukkan: (arg, el) => masukDenganGerak(L.masukkan(S()), el),
    tutup: () => set({ lembar: null, pilih: null, negoId: null, ketik: '', isiW: null }),
    bukaKeranjang: () => set({ lembar: S().lembar === 'keranjang' ? null : 'keranjang' }),
    hapusBaris: ({ id }) => set(L.hapusBaris(S(), id)),
    kurangBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(S(), id, -Number(langkah || 1))),
    tambahBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(S(), id, Number(langkah || 1))),
    nego: ({ id }) => set({ negoId: id, lembar: 'nego', ketik: '' }),
    terapkanNego: () => set(L.terapkanNego(S(), S().negoId, L.angkaKetik(S().ketik))),
    bukaPotongan: () => set({ lembar: 'potongan', ketik: '' }),
    terapkanPotongan: () => set(L.setelPotongan(S(), L.angkaKetik(S().ketik))),
    hapusPotongan: () => set(L.setelPotongan(S(), 0)),
    parkir: () => set(L.parkir(S())),
    pembeliLain: () => set(L.pembeliLain(S())),
    antrean: ({ id }) => set(L.pakaiAntrean(S(), Number(id))),
    buangAntrean: ({ id }) => set(L.buangAntrean(S(), Number(id))),
    bukaBayar: () => set({ lembar: 'bayar', ketik: '' }),
    cara: ({ cara }) => set(L.pilihCara(S(), cara)),
    pecahan: ({ n }) => set(L.tambahUang(S(), Number(n))),
    uangPas: () => set(L.uangPas(S())),
    uangKetik: () => set(L.uangKetik(S())),
    hapusUang: () => set({ uang: 0 }),
    simpan: async () => {
      const r = L.simpanNota(S());
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      const keranjangTadi = S().keranjang.slice(); const uangTadi = S().cara === 'Tunai' ? S().uang : 0;
      set({ kabar: 'Mencatat…', kabarAwas: false });
      try {
        const h = await tulisDokumen(r.dokumen);
        if (h && h.gagal) return set({ kabar: 'DITOLAK, nota tidak tersimpan: ' + h.pesan, kabarAwas: true });
        adeganNota(r.nota, keranjangTadi, uangTadi);   // hanya sesudah nota SUNGGUH tercatat — adegan tidak boleh merayakan nota yang ditolak
        set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI (cadangan, tidak ke Firestore) — ' : h && h.antre ? 'Tersimpan di perangkat, menunggu server — ' : 'Tersimpan — ') + r.ringkas + strukOtomatis(r) }));
      } catch (e) { set({ kabar: 'GAGAL mencatat: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
    },
    bukaKredit: () => set({ kreditDibuka: true, kabar: 'Kredit dibuka sekali untuk nota ini — keputusan owner, tercatat di nota', kabarAwas: false }),
    batalkanNota: async () => {
      const p = L.susunPembatalan(S().notaTerakhir, 'Diurungkan dari sistem baru');
      if (!p) return set({ notaTerakhir: null, kabar: 'Tidak ada nota yang bisa dibatalkan', kabarAwas: true });
      try {
        await tulisDokumen(p.dokumen);
        if (p.hapus.length) await hapusDokumen(p.hapus);
        set({ notaTerakhir: null, kabar: 'Nota dibatalkan — ' + p.jumlah + ' baris ditandai dibatalkan (tidak dihapus)' + (p.hapus.some((x) => x.koleksi === 'retur') ? '; retur tukarnya ikut dicabut (lahir bersama, pergi bersama)' : ''), kabarAwas: false });
      } catch (e) { set({ kabar: 'GAGAL membatalkan: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
    },
    bukaPelanggan: () => set({ lembar: 'pelanggan', cariPelanggan: '' }),
    pilihPelanggan: ({ nama }) => set({ pelanggan: nama, lembar: null, cariPelanggan: '', kabar: '' }),
    lepasPelanggan: () => set({ pelanggan: '', kabar: '' }),
    cariPelanggan: (v) => set({ cariPelanggan: String(v || '').slice(0, 40) },),
    enterPelanggan: (v) => { const n = String(v || '').trim(); if (n) set({ pelanggan: n, lembar: null, cariPelanggan: '' }); },
    tutupKabar: () => set({ kabar: '' }),
    // ---- putaran 3 ----
    namaRepack: (v) => set({ namaRepack: String(v || '').slice(0, 60) }),
    bonus: ({ id }) => set(L.toggleBonus(S(), id)),
    penggantiRetur: ({ id }) => set(L.togglePenggantiRetur(S(), id)),
    bukaPesanan: ({ saring }) => set({ lembar: 'pesanan', psSaring: saring || '' }),
    psSaring: (v) => set({ psSaring: String(v || '').slice(0, 40) }),
    psNama: (v) => set({ psNama: String(v || '').slice(0, 40) }),
    psIsi: (v) => set({ psIsi: String(v || '').slice(0, 200) }),
    psAlamat: (v) => set({ psAlamat: String(v || '').slice(0, 120) }),
    psNilai: (v) => set({ psNilai: String(v || '').slice(0, 15) }),
    simpanPesanan: () => tulisPesanan(L.susunPesananBaru(S(), L.waktuSekarang(S().sekarang || undefined))),
    antarPesanan: ({ id }) => tulisPesanan(L.susunPesananAntar(id, L.waktuSekarang(S().sekarang || undefined))),
    batalPesanan: ({ id }) => tulisPesanan(L.susunPesananBatal(id, L.waktuSekarang(S().sekarang || undefined))),
    ikatPesanan: ({ id }) => set(L.ikatPesanan(S(), id)),
    lepasPesanan: () => set(L.lepasPesanan(S())),
    // ---- putaran 4: retur menunjuk nota ----
    rtCari: (v) => set({ rtCari: String(v || '').slice(0, 40) }),
    tunjukNota: ({ id }) => set(Object.assign(RT.returAwal(), { rtCari: S().rtCari, rtNotaId: id, lembar: 'retur', ketik: '' })),
    rtKondisi: ({ v }) => set({ rtKondisi: v }),
    rtPenyelesaian: ({ v }) => set({ rtPenyelesaian: v, rtTimpa: false }),
    rtAlasanChip: ({ v }) => set({ rtAlasan: v }),
    rtAlasan: (v) => set({ rtAlasan: String(v || '').slice(0, 120) }),
    rtTimpa: () => set({ rtTimpa: !S().rtTimpa }),
    rtNominal: (v) => set({ rtNominal: String(v || '').slice(0, 15) }),
    rtAlasanTimpa: (v) => set({ rtAlasanTimpa: String(v || '').slice(0, 120) }),
    catatRetur: async () => {
      const r = RT.susunRetur(S(), L.waktuSekarang(S().sekarang || undefined));
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      if (r.ikat) { const p = L.ikatTukar(S(), r.ikat); if (p.kabar) return set(p); return set(Object.assign({}, r.patch, p)); }
      try {
        const h = await tulisDokumen(r.dokumen);
        if (h && h.gagal) return set({ kabar: 'DITOLAK, retur tidak tersimpan: ' + h.pesan, kabarAwas: true });
        set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : h && h.antre ? 'Tersimpan di perangkat, menunggu server — ' : '') + r.patch.kabar }));
      } catch (e) { set({ kabar: 'GAGAL mencatat retur: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
    },
    batalTukar: () => set(L.batalTukar(S())),
    // ---- putaran 15: wadah dijual (repack: wadah dipilih, lembar, dijual/ditanggung, upah) + harga jual wadah ----
    rpWadah: ({ jenis }) => { const sama = S().rpWadah === jenis; set({ rpWadah: sama ? '' : jenis, rpLembar: sama ? '' : String(WJ.saranLembar(L.angkaKetik(S().ketik), jenis) || '') }); },
    rpLembar: ({ d }) => set({ rpLembar: String(Math.max(0, Math.round(L.angkaKetik(S().rpLembar)) + Number(d || 0))) }),
    rpSaran: () => set({ rpLembar: String(WJ.saranLembar(L.angkaKetik(S().ketik), S().rpWadah)) }),
    rpDijual: ({ v }) => set({ rpDijual: v === '1' }),
    rpUpah: (v) => set({ rpUpah: String(v || '').replace(/[^\d]/g, '').slice(0, 9) }),
    bukaAturWadah: () => { const isi = {}; WJ.daftarAturWadah().forEach((d) => { isi[d.jenis] = d.harga ? String(d.harga) : ''; }); set({ lembar: 'aturWadah', aturWadah: isi }); },
    aturWadahKetik: (v, el) => { const isi = Object.assign({}, S().aturWadah || {}); isi[el.dataset.jenis] = String(v || '').replace(/[^\d]/g, '').slice(0, 7); set({ aturWadah: isi }); },
    simpanAturWadah: () => tulisUmum(WJ.susunAturHargaWadah(S().aturWadah || {}, L.waktuSekarang(S().sekarang || undefined))),
    // ---- putaran 15: struk (JS3-A kertas & WA, JS3-C aturan otomatis) ----
    bukaStruk: ({ trx, grup, id }) => set({ lembar: 'struk', strukKunci: { trxId: trx || null, grupNota: grup || null, id: id || null }, strukKertas: null, strukSertakan: null }),
    strukKertas: ({ mm }) => set({ strukKertas: Number(mm) }),
    strukSertakan: ({ nama }) => { const kini = Object.assign({}, ST.stAtur().sertakan, S().strukSertakan || {}); const t = Object.assign({}, S().strukSertakan || {}); t[nama] = !kini[nama]; set({ strukSertakan: t }); },
    kirimWa: () => { const n = notaStruk(); if (!n) return; const st = ST.susunStruk(n.nota, n.atur, n.pilih); const w = bukaWa(st.wa);
      catatStruk(n.nota, 'wa', w ? 'dibuka di WhatsApp (tanpa nomor tujuan)' : 'jendela WhatsApp ditahan peramban');
      set({ kabar: w ? 'WhatsApp dibuka dengan struk ' + (n.nota.nama || 'tanpa nama') + ' ' + RP(n.nota.total) + ' — tanpa nomor tujuan, WhatsApp yang bertanya ke siapa' : 'Peramban menahan jendela WhatsApp — izinkan pop-up untuk alamat ini, lalu ketuk lagi', kabarAwas: !w }); },
    cetakStruk: () => { const n = notaStruk(); if (n) cetak(n.nota, n.atur, n.pilih, ''); },
    bukaAturStruk: () => set({ lembar: 'aturStruk', aturStruk: ST.stAtur() }),
    aturStrukKop: (v, el) => { const a = drafStruk(); a.kop[el.dataset.kolom] = String(v || '').slice(0, 80); set({ aturStruk: a }); },
    aturStrukKaki: (v) => { const a = drafStruk(); a.kaki = String(v || '').slice(0, 80); set({ aturStruk: a }); },
    aturStrukKertas: ({ mm }) => { const a = drafStruk(); a.kertas = Number(mm); set({ aturStruk: a }); },
    aturStrukSertakan: ({ nama }) => { const a = drafStruk(); a.sertakan[nama] = !a.sertakan[nama]; set({ aturStruk: a }); },
    aturStrukOto: ({ jalur, v }) => { const a = drafStruk(); a.oto[jalur] = v; set({ aturStruk: a }); },
    aturStrukOrang: ({ kunci, v }) => { const a = drafStruk(); if (v === 'ikut') delete a.perOrang[kunci]; else a.perOrang[kunci] = v; set({ aturStruk: a }); },
    simpanAturStruk: () => tulisUmum(ST.susunAturStruk(S().aturStruk || ST.stAtur(), L.waktuSekarang(S().sekarang || undefined))),
  };
  const drafStruk = () => JSON.parse(JSON.stringify(S().aturStruk || ST.stAtur()));
  /** Nota yang sedang dibuka di lembar struk + setelan + timpaan untuk struk ini saja. */
  function notaStruk() {
    const s = S(); if (!s.strukKunci) return null; const nota = ST.notaDari(s.strukKunci); if (!nota) return null;
    const atur = ST.stAtur(); return { nota, atur, pilih: { kertas: s.strukKertas || atur.kertas, sertakan: Object.assign({}, atur.sertakan, s.strukSertakan || {}) } };
  }
  function bukaWa(teks) { try { return window.open(ST.tautanWa(teks), '_blank', 'noopener'); } catch (e) { return null; } }
  /** Cetak = teks struk yang sama lewat dialog cetak perangkat ini (#cetakStruk, satu-satunya yang tampil saat print). */
  function cetak(nota, atur, pilih, ket) {
    const st = ST.susunStruk(nota, atur, pilih); const el = document.getElementById('cetakStruk'); if (!st || !el) return;
    el.textContent = st.teks; el.className = 'cetak-struk k' + st.kertasMm;
    try { window.print(); } catch (e) { set({ kabar: 'Dialog cetak tidak bisa dibuka: ' + (e && e.message ? e.message : e), kabarAwas: true }); return; }
    catatStruk(nota, 'cetak', (ket ? ket + ' · ' : '') + 'dialog cetak perangkat ini · ' + st.kertasMm + ' mm');
  }
  function catatStruk(nota, cara, ket) { tulisDokumen([ST.susunStrukKeluar(nota, cara, L.waktuSekarang(S().sekarang || undefined), ket)]).catch((e) => console.error('catat struk', e)); }
  /** Aturan otomatis JS3-C sesudah nota tersimpan: cetak → dialog cetak; WA → dicoba dibuka, kalau ditahan peramban dikatakan (tombolnya tetap ada di Struk). */
  function strukOtomatis(r) {
    try {
      const baris = r.dokumen.filter((x) => x.koleksi === 'penjualan').map((x) => Object.assign({ oleh: opsi.pemegang ? opsi.pemegang() : '' }, x.data));
      const nota = ST.notaDariBaris(baris); const atur = ST.stAtur(); const o = ST.putusOto(atur, nota); let teks = '';
      if (o.cetak) { setTimeout(() => cetak(nota, atur, null, 'otomatis: ' + o.teks), 900); teks += ' · struk dicetak otomatis'; }
      if (o.wa) { const st = ST.susunStruk(nota, atur, null); const w = bukaWa(st.wa); if (w) { catatStruk(nota, 'wa', 'otomatis: ' + o.teks); teks += ' · WhatsApp dibuka otomatis'; } else teks += ' · WhatsApp otomatis DITAHAN peramban — ketuk Struk › Kirim WhatsApp'; }
      return teks;
    } catch (e) { console.error('struk otomatis', e); return ''; }
  }
  async function tulisUmum(r) {
    if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    try {
      const h = await tulisDokumen(r.dokumen);
      if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true });
      set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar }));
    } catch (e) { set({ kabar: 'GAGAL menulis: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  // barang masuk keranjang → tetes emas terbang dari tombol yang diketuk ke bilah keranjang, bilahnya memegas
  function masukDenganGerak(patch, el) {
    const dari = el ? tengah(el) : null; const masuk = patch.keranjang && patch.keranjang.length > S().keranjang.length;
    const baris = masuk ? patch.keranjang[patch.keranjang.length - 1].trx : null;
    set(patch);
    if (!masuk) return;
    // ADEGAN (owner 19 Sep): literan/repack = serok → kantong → ikat; kemasan = masuk keranjang belanja; karung cukup saat nota dicatat
    let lamaAdegan = 0;
    if (baris.jenis === 'literan' || baris.jenis === 'repacking') {
      const kg = baris.totalKg || 0; const serokan = kg <= 2 ? 1 : kg <= 6 ? 2 : 3;   // serok ±1,8 kg — digambar paling banyak tiga kali
      if (adeganSerok({ nama: baris.label, jumlahTeks: DESIMAL(baris.jumlah) + ' ' + baris.satuan, dariKarung: baris.jenis === 'repacking' || L.aturWadah().daftar.indexOf(baris.merkSumber) < 0, kemasanLiteran: baris.kemasanLiteran || (baris.jenis === 'repacking' ? 'kantong' : null), serokan })) lamaAdegan = serokan * 820 + 700;
    } else if (baris.jenis === 'karung') {
      // owner 22 Sep: karung utuh → dipanggul ke pundak; setengah karung (0,5 = 25 kg dari karung 50 kg) → dituang ke karung bekas lalu dijahit
      const j = baris.jumlah || 0; const berat = baris.beratKarungAcuan || 50;
      if (j % 1) { if (adeganTuangJahit({ nama: baris.merkSumber, berat: String(berat), kg: DESIMAL(Math.round((j % 1) * berat * 10) / 10) })) lamaAdegan = 3400; }
      else if (adeganPanggul({ nama: baris.merkSumber, jenis: 'karung', berat: String(berat), jumlahTeks: DESIMAL(j) + ' karung ' + berat + ' kg' })) lamaAdegan = 1700;
    } else if (baris.jenis === 'wadah') {
      if (adeganKemasanMasuk({ nama: baris.label, ukuran: '', jumlahTeks: DESIMAL(baris.jumlah) + ' lembar' })) lamaAdegan = 900;
    } else if (baris.jenis === 'kemasan') {
      const uk = Number(baris.ukuranKemasan) || 0; const ukT = String(baris.ukuranKemasan).replace('.', ',');
      if (uk >= 10) { if (adeganPanggul({ nama: baris.namaProduk, jenis: 'kemasan', ukuran: ukT, jumlahTeks: DESIMAL(baris.jumlah) + ' kemasan ' + ukT + ' kg' + (baris.bonusUnit ? ' + bonus' : '') })) lamaAdegan = 1700; }
      else if (adeganKemasanMasuk({ nama: baris.label, ukuran: ukT, jumlahTeks: DESIMAL(baris.jumlah) + ' kemasan' + (baris.bonusUnit ? ' + bonus' : '') })) lamaAdegan = 900;
    }
    const mendarat = () => { const bilah = akar.querySelector('.ringkas-keranjang'); if (dari) terbangkan(lamaAdegan ? { x: innerWidth / 2, y: 150 } : dari, bilah); setTimeout(() => sekali(akar.querySelector('.jual-keranjang'), 'pegas', 520), 420); };
    setTimeout(() => requestAnimationFrame(mendarat), lamaAdegan);
  }
  // Kendaraan pembeli menurut isi keranjang (aturan owner 22 Sep): karung > 3 → mobil, selain itu motor; kemasan ≥ 10 kg sama seperti karung;
  // kemasan 5 kg: > 20 mobil, > 1 motor; literan > 10 L motor; repack > 10 kg motor. Satu saja yang minta mobil → mobil. Tidak ada → serah terima biasa.
  function kendaraanUntuk(keranjang) {
    // dijumlah per nota (bukan per baris): 2 karung + 2 karung = 4 karung → mobil
    const j = { karung: 0, besar: 0, kecil: 0, liter: 0, kg: 0 };
    keranjang.forEach((b) => { const t = b.trx;
      if (t.jenis === 'karung') j.karung += t.jumlahKarung || 0;
      else if (t.jenis === 'kemasan') { if ((Number(t.ukuranKemasan) || 0) >= 10) j.besar += t.jumlahUnit || 0; else j.kecil += t.jumlahUnit || 0; }
      else if (t.jenis === 'literan') j.liter += t.jumlahLiter || 0;
      else if (t.jenis === 'repacking') j.kg += t.totalKg || 0; });
    if (j.karung > 3 || j.besar > 3 || j.kecil > 20) return 'mobil';
    if (j.karung > 0 || j.besar > 0 || j.kecil > 1 || j.liter > 10 || j.kg > 10) return 'motor';
    return null;
  }
  // nota dicatat (owner 23 Sep) → SELALU dimulai adegan TERIMA UANG (BON = kertas bon), lalu disusul adegan barang menurut barang TERBESAR nilainya:
  // diangkut motor/mobil bila muatannya besar, selain itu serah terima (kantong kertas / kemasan)
  function adeganNota(nota, keranjang, uangDiterima) {
    const utama = keranjang.slice().sort((a, b) => (b.trx.nilaiBarangPengganti || b.trx.hargaTotal || 0) - (a.trx.nilaiBarangPengganti || a.trx.hargaTotal || 0))[0]; if (!utama) return;
    const t = utama.trx; const cara = nota.cara; const kembali = cara === 'Tunai' && uangDiterima > nota.tagihan ? 'kembali ' + RP(uangDiterima - nota.tagihan) : nota.bayarSebagian ? 'sisa jadi bon' : '';
    const uang = { cara: nota.bayarSebagian ? 'Tunai' : cara, jumlahRp: RP(nota.bayarSebagian || nota.tagihan), ket: kembali };
    const kend = kendaraanUntuk(keranjang);
    const banyakTeks = (t.jenis === 'karung' ? DESIMAL(t.jumlah) + ' karung ' + (t.merkSumber || '') : t.jenis === 'kemasan' ? DESIMAL(t.jumlahUnit) + ' kemasan ' + String(t.ukuranKemasan).replace('.', ',') + ' kg' : DESIMAL(t.jumlah) + ' ' + (t.satuan || '') + ' ' + (t.merkSumber || t.namaProduk || '')) + (keranjang.length > 1 ? ' + ' + (keranjang.length - 1) + ' baris lain' : '');
    const barang = () => {
      if (kend) {
        const jenis = t.jenis === 'karung' ? 'karung' : t.jenis === 'kemasan' ? 'kemasan' : 'kantong';
        const banyak = t.jenis === 'karung' ? Math.ceil(t.jumlahKarung || 1) : t.jenis === 'kemasan' ? (t.jumlahUnit || 1) : Math.ceil((t.jenis === 'literan' ? (t.jumlahLiter || 0) / 10 : (t.totalKg || 0) / 10) || 1);
        adeganMuat({ kendaraan: kend, jenis, ukuran: t.jenis === 'kemasan' ? String(t.ukuranKemasan).replace('.', ',') : String(t.beratKarungAcuan || 50), banyak, banyakTeks });
      } else adeganSerahTerima({ jenis: t.jenis === 'kemasan' ? 'kemasan' : 'kantong', ukuran: t.jenis === 'kemasan' ? String(t.ukuranKemasan).replace('.', ',') : '', namaTeks: banyakTeks });
    };
    const lamaUang = adeganTerimaUang(uang);
    if (lamaUang) setTimeout(barang, lamaUang + 200); else barang();
  }
  async function tulisPesanan(r) {
    if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    try {
      const h = await tulisDokumen(r.dokumen);
      if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true });
      set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar }));
    } catch (e) { set({ kabar: 'GAGAL menulis pesanan: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  // panel isi ulang wadah (takar demi takar) — penangan bersama dengan layar Stok
  async function tulisWadah(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }
    try { const x = await tulisDokumen(r.dokumen); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); return true; }
    catch (e) { set({ kabar: 'GAGAL mencatat: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  Object.assign(aksi, aksiPanelWadah({ set, st: S, tulis: tulisWadah, keranjang: S, waktu: () => L.waktuSekarang(S().sekarang || undefined),
    sesudahCatat: (wadah, r) => { const hsl = r.hitung; const dulu = hsl.wadah; const kini = L.tinggiWadah(wadah, S());
      adeganIsiUlang({ nama: wadah, keterangan: hsl.takar + ' takar · ' + DESIMAL(hsl.kg) + ' kg' + (hsl.banding ? ' · campur ' + hsl.banding : ''), serokan: Math.ceil(hsl.takar / 8), dari: dulu, ke: kini || dulu }); } }));
  delegasi(akar, aksi);

  let _rak = null, _rakUntuk = '', _lembarSebelum = null;
  function rakKini() {
    const s = S(); L.sinkronKeranjang(s);
    // rak bergantung pada ISI keranjang (jumlah + bonus), bukan cuma banyaknya baris — +1 unit atau bonus mengubah sisa chip
    const tanda = (s.tukar ? 'tk' : '') + s.pelanggan + '|' + s.keranjang.map((b) => b.trx.jenis + ':' + b.trx.jumlah + ':' + (b.trx.bonusUnit || 0) + ':' + (b.trx.kemasanRepack || '') + (b.trx.jumlahKemasanRepackDipakai || '')).join(',') + '|' + s.antrean.length + '|' + opsi.versiData();
    if (!_rak || _rakUntuk !== tanda) { _rak = L.susunRak(s); _rakUntuk = tanda; }
    return _rak;
  }

  function gambar() {
    const s = S();
    const rak = rakKini();
    const t = L.hitungTagihan(s);
    const hari = L.hariIni(s);
    const sumber = sumberData();
    const info = L.infoPelanggan(s.pelanggan);
    const nPesanan = L.daftarPesanan('').length;
    const psIkat = s.pesananId ? L.ambilPesananDoc(s.pesananId) : null;
    // lembar hanya "naik" saat pertama dibuka — tiap ketukan menggambar ulang, jangan mengulang animasinya
    const muncul = s.lembar !== _lembarSebelum ? 'muncul' : ''; _lembarSebelum = s.lembar;
    const adaUrung = !!(s.notaTerakhir && Date.now() - s.notaTerakhir.pada < L.BATAS_URUNGKAN_DETIK * 1000);
    document.body.classList.toggle('ada-lembar', !!s.lembar && s.lembar !== 'keranjang');
    document.body.classList.toggle('keranjang-terbuka', s.lembar === 'keranjang');
    pasang(akar, h`
      <input type="hidden" id="jualKarungBerat" value="${s.satuanKarung}">
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Jual</div><div class="ket">${tanggalPendek(hari.iso)} · ${opsi.statusTeks()}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'data toko' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode" title="${opsi.mode() === 'gelap' ? 'Mode terang' : 'Mode gelap'}">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div>
        </div>
      </header>
      ${sumber.jenis === 'cadangan' ? h`<div class="pita-info emas baca-saja">SIMULASI — angka dari ${sumber.keterangan}; nota yang dicatat di sini TIDAK masuk Firestore.</div>` : sumber.jenis !== 'firestore' ? h`<div class="pita-info awas baca-saja">Belum tersambung ke data toko — masuk dulu sebagai owner.</div>` : h`<div class="pita-info emas baca-saja">Nota dicatat ke data toko yang sama dengan sistem lama · ${opsi.statusTeks()}</div>`}
      ${s.kabar || adaUrung ? h`<div class="kabar-kotak">
        ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : ''}" data-aksi="tutupKabar">${s.kabar}</div>` : ''}
        ${adaUrung ? h`<div class="pita-info urung"><span>Nota barusan: ${s.notaTerakhir.ringkas}</span><span style="display: flex; gap: 6px;"><span class="kaca-btn" data-aksi="bukaStruk" data-trx="${s.notaTerakhir.trxId}">Struk ›</span><span class="kaca-btn putus" data-aksi="batalkanNota">Batalkan nota barusan</span></span></div>` : ''}
      </div>` : ''}

      <section class="jual-rak">
        <div class="jalur">
          ${L.JALUR.map(([id, nama]) => h`<div class="seg ${s.jalur === id ? 'aktif' : ''}" data-aksi="jalur" data-jalur="${id}">${nama}</div>`)}
          ${L.JALUR_NANTI.map(([id, nama]) => h`<div class="seg nanti" title="putaran berikutnya">${nama}</div>`)}
        </div>
        ${s.antrean.length ? h`<div class="bilah-antre">
          ${s.antrean.map((a) => h`<div class="tab-antre ${a.beku.pelanggan ? 'bernama' : ''}"><span data-aksi="antrean" data-id="${a.id}">${a.beku.pelanggan || 'tanpa nama'} · ${a.beku.items.length} brg · ${RP(a.beku.items.reduce((x, b) => x + b.trx.hargaTotal, 0))}</span><span class="buang" data-aksi="buangAntrean" data-id="${a.id}" title="buang struk">${mentah(IKON.hapus)}</span></div>`)}
        </div>` : ''}
        ${gambarChip(s, rak)}
      </section>

      <section class="jual-keranjang ${s.lembar === 'keranjang' ? 'terbuka' : ''}">
        <div class="ringkas-keranjang" data-aksi="bukaKeranjang">
          <span>${s.keranjang.length ? s.keranjang.length + ' barang' : 'Keranjang kosong'}${s.pelanggan ? ' · ' + s.pelanggan : ''}</span>
          <span class="serif" style="font-size: 20px;" data-gulir="${Math.max(0, t.total)}">${RP(Math.max(0, t.total))}</span>
        </div>
        <div class="isi-keranjang">
          <div class="keranjang">
            ${s.keranjang.length ? s.keranjang.map((b) => h`<div class="b ${b.trx.penggantiRetur ? 'pengganti' : ''}" data-k="baris-${b.id}">
              <div class="t"><div style="font-weight: 600;">${b.trx.label}</div><div class="ket">${DESIMAL(b.trx.jumlah)} ${b.trx.satuan} × ${RP(b.trx.hargaSatuan)}${b.trx.nego ? ' · nego' : ''}${b.trx.kemasanLiteran ? ' · ' + (b.trx.jumlahKemasanLiteranDipakai || 1) + ' kantong' : ''}${b.trx.bonusUnit ? ' · +1 bonus (stok ' + b.trx.jumlahUnit + ')' : ''}${b.trx.penggantiRetur ? ' · PENGGANTI RETUR, nilai ' + RP(b.trx.nilaiBarangPengganti) : ''}${b.trx.kemasanRepack ? ' · ' + b.trx.jumlahKemasanRepackDipakai + ' lembar ' + ((WJ.jenisWadah(b.trx.kemasanRepack) || {}).label || b.trx.kemasanRepack) + ' ditanggung toko' + (b.trx.biayaKemasanRepack ? ' (HPP +' + RP(b.trx.biayaKemasanRepack) + ')' : ' (modal belum ada)') : ''}${b.trx.upahRepack ? ' · upah repack ' + RP(b.trx.upahRepack) : ''}${b.trx.jenis === 'wadah' && b.trx.hppTotalSaatJual === undefined ? ' · tanpa modal: belum masuk hitungan laba' : ''}</div></div>
              <span class="step"><span data-aksi="kurangBaris" data-id="${b.id}" data-langkah="${b.trx.satuan === 'karung' ? 0.5 : 1}">−</span><span class="n">${DESIMAL(b.trx.jumlah)}</span><span data-aksi="tambahBaris" data-id="${b.id}" data-langkah="${b.trx.satuan === 'karung' ? 0.5 : 1}">+</span></span>
              <div class="h" data-aksi="nego" data-id="${b.id}" title="ketuk untuk nego">${RP(b.trx.hargaTotal)}</div>
              <span class="hapus" data-aksi="hapusBaris" data-id="${b.id}">${mentah(IKON.hapus)}</span>
              <div class="bendera">
                ${b.trx.jenis === 'kemasan' ? h`<span class="pil ${b.trx.bonusUnit ? 'nyala' : ''}" data-aksi="bonus" data-id="${b.id}" title="1 unit gratis: stok & modal ikut, uang tidak">${b.trx.bonusUnit ? '✓ bonus +1' : '+1 bonus'}</span>` : ''}
                <span class="pil awas ${b.trx.penggantiRetur ? 'nyala' : ''} ${s.penggantiTanya === b.id ? 'nyala' : ''}" data-aksi="penggantiRetur" data-id="${b.id}" title="tukar tanpa nota: omzet & kas Rp0, modal tetap keluar">${b.trx.penggantiRetur ? '✓ pengganti retur' : s.penggantiTanya === b.id ? 'ketuk lagi: pengganti retur' : 'pengganti retur'}</span>
              </div>
            </div>`) : h`<div class="kosong">Ketuk barang di rak untuk mulai.</div>`}
          </div>
          ${s.tukar ? h`<div class="pita-info emas">TUKAR · ${s.tukar.ringkas} kembali senilai <b>${RP(s.tukar.kredit)}</b> — dipotong dari keranjang ini. Retur baru TERCATAT saat nota dicatat. <span style="text-decoration: underline; cursor: pointer;" data-aksi="batalTukar">batal tukar</span></div>` : ''}
          ${s.pesananId && psIkat ? h`<div class="pita-info emas">Keranjang ini untuk PESANAN ${psIkat.namaPelanggan || ''} — ${psIkat.isi || ''}. Begitu nota dicatat, pesanannya jadi DIBAYAR. <span style="text-decoration: underline; cursor: pointer;" data-aksi="lepasPesanan">lepas</span></div>` : ''}
          <div class="tombol-baris">
            <div class="kaca-btn ${s.pelanggan ? 'aktif' : ''}" data-aksi="bukaPelanggan">${s.pelanggan ? s.pelanggan : 'Nama pembeli'}</div>
            <div class="kaca-btn ${t.potongan ? 'aktif' : ''}" data-aksi="bukaPotongan">${t.potongan ? 'Potongan ' + RP(t.potongan) : 'Potongan'}</div>
            <div class="kaca-btn ${nPesanan ? 'aktif' : ''}" data-aksi="bukaPesanan" data-saring="">Pesanan${nPesanan ? ' · ' + nPesanan : ''}</div>
            <div class="kaca-btn" data-aksi="pembeliLain">Pembeli lain</div>
          </div>
          ${info && info.sisa > 0 ? h`<div class="ket">Bon ${s.pelanggan} sekarang ${RP(info.sisa)} · biasa belanja ${RP(info.rataBulanan)}/bulan</div>` : ''}
          ${info && info.pesanan && info.pesanan.length && !s.pesananId ? h`<div class="pita-info" data-aksi="bukaPesanan" data-saring="${s.pelanggan}" style="cursor: pointer;">${info.pesanan.length} pesanan ${s.pelanggan} belum tuntas — ketuk untuk melihat / mencatat jualnya</div>` : ''}
          <div class="bulat"></div>
          <div class="total"><span class="label">Subtotal</span><span class="n" style="font-size: 16px;">${RP(t.subtotal)}</span></div>
          ${t.potongan ? h`<div class="total"><span class="label">Potongan</span><span class="n" style="font-size: 16px;">− ${RP(t.potongan)}</span></div>` : ''}
          ${t.kredit ? h`<div class="total"><span class="label">Barang kembali (tukar)</span><span class="n" style="font-size: 16px;">− ${RP(t.kredit)}</span></div>` : ''}
          ${t.bulat ? h`<div class="total"><span class="label">Pembulatan Rp500 (${s.cara === 'Kredit' ? 'bon' : 'tunai'})</span><span class="n" style="font-size: 16px;">+ ${RP(t.bulat)}</span></div>` : ''}
          <div class="total"><span class="label">Ditagih</span><span class="n" data-gulir="${Math.max(0, t.total)}">${RP(Math.max(0, t.total))}</span></div>
          <div class="utama" data-aksi="bukaBayar">BAYAR · ${RP(Math.max(0, t.total))}</div>
          <div class="ket" style="text-align: center; cursor: pointer;" data-aksi="parkir">parkir struk ini — stoknya tetap dipegang</div>
        </div>
      </section>

      <aside class="jual-samping">
        <div class="kartu hari">
          <div class="label">Hari ini · ${hari.baris} baris · ${hari.nota} nota</div>
          <div class="serif" style="font-size: 24px;" data-gulir="${hari.omzet}">${RP(hari.omzet)}</div>
          <div class="ket">${Object.keys(hari.perCara).map((c) => c + ' ' + RP(hari.perCara[c])).join(' · ') || 'belum ada penjualan'} · ${DESIMAL(hari.kg)} kg</div>
          ${hari.terakhir.map((r) => h`<div class="r ketuk" data-aksi="bukaStruk" data-trx="${r.trxId}" data-grup="${r.grupNota}" data-id="${r.id}" title="buka struk"><span class="w">${r.jam}</span><span class="t">${r.teks}${r.nama ? ' · ' + r.nama : ''}</span><span class="n">${RP(r.n)}</span></div>`)}
          ${hari.terakhir.length ? h`<div class="ket" style="padding-top: 4px;">ketuk baris → struk (WhatsApp / cetak)</div>` : ''}
        </div>
      </aside>

      ${gambarLembar(s, rak, t, info, muncul)}
    `);
  }

  function gambarRetur(s) {
    const daftar = RT.daftarNotaRetur(s);
    return h`<div class="pita-info">Retur MENUNJUK NOTA: ketuk nota barangnya, isi berapa yang kembali — nilainya dihitung dari nota itu. Uang kembali atau tukar barang.</div>
      <input class="ketik-nama" id="rtCari" type="text" value="${s.rtCari}" data-ketik="rtCari" placeholder="cari nama pembeli / barang (60 hari terakhir)">
      <div class="kartu daftar-nota">${daftar.map((o) => h`<div class="baris-nota ${o.bisa ? '' : 'tak-bisa'}" ${o.bisa ? mentah('data-aksi="tunjukNota"') : ''} data-id="${o.id}">
        <div class="atas"><span><b>${o.teks}</b>${o.nama ? ' · ' + o.nama : ''}</span><span class="n">${RP(o.hargaTotal)}</span></div>
        <div class="ket">${tanggalPendek(o.tanggal)} ${o.jam} · ${o.cara}${o.bisa ? ' · boleh kembali ' + DESIMAL(o.sisa) + ' ' + o.satuan : ''}</div>
        ${o.bisa ? '' : h`<div class="ket awas-teks">${o.sebab}${o.cadangan ? ' Yang seperti ini masih lewat layar Retur sistem lama (nominalnya diketik tangan).' : ''}</div>`}
      </div>`)}${daftar.length ? '' : h`<div class="ket" style="padding: 10px 4px;">Tidak ada nota karung/kemasan yang cocok.</div>`}</div>`;
  }

  function gambarChip(s, rak) {
    if (s.jalur === 'retur') return gambarRetur(s);
    const daftar = s.jalur === 'sering' ? rak.sering : (rak[s.jalur] || []);
    const pitaWadah = s.jalur === 'wadah' ? h`<div class="pita-info" data-k="pita-wadah">Wadah = <b>barang dagangan</b> (keputusan owner 17 Sep): tiap lembar jadi baris nota & menambah omzet, buku kantong/karung bekas turun. Yang belum punya harga jual tidak tampil. <span class="tautan" data-aksi="bukaAturWadah">Atur harga jual wadah ›</span></div>` : '';
    if (!daftar.length) return h`${pitaWadah}<div class="pita-info">${s.jalur === 'sering' ? (s.pelanggan ? s.pelanggan + ' belum punya kebiasaan belanja 90 hari terakhir' : 'Belum ada yang laku 28 hari terakhir') : s.jalur === 'wadah' ? 'Belum ada wadah yang diberi harga jual — ketuk "Atur harga jual wadah" di atas.' : 'Belum ada barang berharga di jalur ini — isi harganya di Katalog'}</div>`;
    // isi gambar = sisa relatif terhadap yang paling banyak DI KELOMPOKNYA (wadah literan memakai isinya sendiri, bukan perbandingan)
    const satuChip = (c, penuh, i) => h`<div class="chip ${s.pilih && s.pilih.kunci === c.kunci && s.pilih.jalur === c.jalur && (s.pilih.berat || 0) === (c.berat || 0) ? 'dipilih' : ''} ${c.sisa <= 0 && !c.tanpaBatas ? 'habis' : c.sisa <= 2 && !c.tanpaBatas ? 'kurang' : ''} ${c.wadah && c.wadah.diketahui && c.wadah.perluIsi ? 'isi-ulang' : ''}"
        data-k="chip-${s.jalur}-${c.jalur}-${c.kunci}-${c.berat || ''}" style="--urut: ${Math.min(i, 14)};"
        data-aksi="${s.jalur === 'sering' ? 'sering' : 'chip'}" data-id="${c.id || ''}" data-jalur="${c.jalur}" data-kunci="${c.kunci}" data-berat="${c.berat || ''}">
      <div class="teks-chip">
        <div class="nama">${c.nama}</div>
        <div class="rinci">${c.ukuran}${c.keterangan ? ' · ' + c.keterangan : ''}</div>
        <div class="harga">${RP(c.harga)}<span class="satuan">/${c.satuan}</span></div>
        <div class="stok">${c.sisa <= 0 && !c.tanpaBatas ? 'habis' : c.sisaTeks}${c.dipegang > 0 ? ' · ' + (c.jalur === 'kemasan' ? c.dipegang + ' unit' : c.jalur === 'wadah' ? c.dipegang + ' lembar' : DESIMAL(c.dipegang) + ' kg') + ' dipegang struk lain' : ''}</div>
        ${c.wadah ? h`<div class="stok wadah-ket">${!c.wadah.diketahui ? 'wadah belum ditandai isi ulang' : c.wadah.perluIsi ? 'WADAH ±' + DESIMAL(c.wadah.sisaKg) + ' kg — ISI ULANG' : 'wadah ±' + DESIMAL(c.wadah.sisaKg) + ' kg'}</div>` : ''}
        ${c.jalur === 'wadah' ? h`<div class="stok ${c.modalAneh ? 'awas-teks' : ''}">${c.adaModal ? 'modal ' + RP(c.modal) + ' · margin ' + RP(c.harga - c.modal) + (c.modalAneh ? ' · PERIKSA' : '') : 'modal belum ada'}</div>` : ''}
      </div>
      <div class="gambar-chip">${mentah(gambarChipBarang(c, penuh))}</div>
    </div>`;
    const maks = (d) => Math.max(1, ...d.map((c) => c.sisa || 0));
    const kelompok = s.jalur !== 'sering' && rak.kelompok && rak.kelompok[s.jalur] ? rak.kelompok[s.jalur] : null;
    if (kelompok) return h`${kelompok.map((g) => h`<div class="kelompok-rak" data-k="kel-${s.jalur}-${g.k}"><div class="judul-kelompok"><span>${g.judul}</span><span class="ket">${g.daftar.length} barang · termurah dulu</span></div>
      <div class="rak-chip">${g.daftar.map((c, i) => satuChip(c, maks(g.daftar), i))}</div></div>`)}`;
    return h`${pitaWadah}<div class="rak-chip" data-k="rak-${s.jalur}">${daftar.map((c, i) => satuChip(c, maks(daftar), i))}</div>`;
  }

  function gambarLembar(s, rak, t, info, muncul) {
    const sumber = sumberData();
    if (!s.lembar || s.lembar === 'keranjang') return '';
    const L1 = h`<div class="lembar tirai" data-k="tirai" data-aksi="tutup"></div>`;
    const kepala = (judul, ket) => h`<div style="display: flex; justify-content: space-between; align-items: baseline;"><span class="judul">${judul}</span><span class="ket" style="cursor: pointer; text-decoration: underline;" data-aksi="tutup">tutup</span></div>${ket ? h`<div class="ket">${ket}</div>` : ''}`;
    const tuts = (aksiMasuk, label) => h`<div class="tuts">${TUTS.map((k) => h`<div class="k ${/^\d$/.test(k) ? '' : 'f'}" data-aksi="tuts" data-t="${k}">${k}</div>`)}${aksiMasuk ? h`<div class="k f aksi" style="grid-column: span 4;" data-aksi="${aksiMasuk}">${label}</div>` : ''}</div>`;
    if (s.lembar === 'jumlah' && s.pilih) {
      const c = s.pilih; const maks = L.maksUntuk(c);
      const preset = c.jalur === 'karung' ? [1, 2, 5, 10] : c.jalur === 'kemasan' ? [1, 2, 3, 5] : c.jalur === 'repack' ? [5, 10, 20, 25] : c.jalur === 'wadah' ? [1, 2, 5, 10] : [1, 2, 5, 10];
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala(c.nama + ' ' + c.ukuran, RP(c.harga) + '/' + c.satuan + ' · bebas dijual ' + (maks === null ? (c.tanpaBatas ? 'tidak dibatasi buku (hasil samping)' : '—') : DESIMAL(maks) + ' ' + c.satuan))}
        ${c.jalur === 'literan' && c.wadah ? panelIsiUlang(c.kunci, s, s, { lipat: true }) : ''}
        ${c.jalur === 'wadah' ? h`<div class="ket ${c.modalAneh ? 'awas-teks' : ''}">${c.teksModal}</div>` : ''}
        ${c.jalur === 'repack' ? h`<div class="ket">Jadi produk apa (nama jual di nota) — kosong = nama mereknya</div><input class="ketik-nama" id="namaRepack" type="text" value="${s.namaRepack}" data-ketik="namaRepack" placeholder="${c.nama}">` : ''}
        <div class="tombol-baris">${preset.map((n) => h`<div class="kaca-btn" data-aksi="preset" data-n="${n}">${n} ${c.satuan}</div>`)}</div>
        <div class="label">Jumlah</div><div class="angka">${s.ketik || '0'} <span class="ket">${c.satuan}</span>${s.ketik ? h` <span class="ket">= ${RP(c.harga * L.angkaKetik(s.ketik))}</span>` : ''}</div>
        ${c.jalur === 'repack' ? gambarRepackWadah(s) : ''}
        ${tuts('masukkan', 'MASUKKAN KE KERANJANG')}
      </div>`;
    }
    if (s.lembar === 'nego') {
      const b = s.keranjang.find((x) => x.id === s.negoId); if (!b) return '';
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Nego ' + b.trx.label, 'harga sekarang ' + RP(b.trx.hargaSatuan) + '/' + b.trx.satuan + ' · ketik harga barunya')}
        <div class="angka">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>
        ${tuts('terapkanNego', 'PAKAI HARGA INI')}
      </div>`;
    }
    if (s.lembar === 'potongan') {
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Potongan nota', 'nominal, dipotong dari subtotal ' + RP(t.subtotal))}
        <div class="angka">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>
        ${tuts('terapkanPotongan', 'PAKAI POTONGAN')}
        ${t.potongan ? h`<div class="kaca-btn putus" data-aksi="hapusPotongan">hapus potongan ${RP(t.potongan)}</div>` : ''}
      </div>`;
    }
    if (s.lembar === 'pelanggan') {
      const daftar = L.daftarPelanggan(s.cariPelanggan);
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Siapa pembelinya?', 'nama dari catatan penjualan & kartu pelanggan toko')}
        <input class="ketik-nama" id="cariPelanggan" type="text" value="${s.cariPelanggan}" data-ketik="cariPelanggan" data-enter="enterPelanggan" placeholder="Ketik namanya — Enter untuk memakai nama baru">
        ${s.pelanggan ? h`<div class="kaca-btn putus" data-aksi="lepasPelanggan">Tanpa nama</div>` : ''}
        <div class="daftar-nama">${daftar.map((o) => h`<div class="baris-nama ${o.sisaBon > 0 ? 'berutang' : ''}" data-aksi="pilihPelanggan" data-nama="${o.nama}">
          <span>${o.nama}${o.terdaftar ? ' ✓' : ''}</span><span class="ket">${o.sisaBon > 0 ? 'bon ' + RP(o.sisaBon) + (o.umurHari ? ' · ' + o.umurHari + ' hari' : '') : o.kali + '× belanja'}</span></div>`)}
        ${daftar.length ? '' : h`<div class="ket">Belum ada nama itu — tekan Enter untuk memakai nama baru.</div>`}
      </div>`;
    }
    if (s.lembar === 'retur') {
      const n = RT.notaDitunjuk(s);
      if (!n || n.hilang || !n.d.ok) return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">${kepala('Retur', 'nota ini tidak bisa ditunjuk lagi')}<div class="pita-info awas">${!n || n.hilang ? 'Nota tidak ditemukan lagi — dibatalkan, dikoreksi, atau dihapus.' : n.d.sebab}</div></div>`;
      const d = n.d; const tukar = s.rtPenyelesaian === 'tukar';
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Retur · ' + n.teks, 'nota ' + tanggalPendek(n.t.tanggal) + (n.t.namaPelanggan ? ' · ' + n.t.namaPelanggan : '') + ' · boleh kembali ' + DESIMAL(d.sisa) + ' ' + d.satuan + (d.sudahDiretur ? ' (' + DESIMAL(d.sudahDiretur) + ' sudah diretur)' : ''))}
        <div class="ket">Harga dibayar per ${d.satuan}: ${RP(d.perSatuan)} — dari ${d.dasar}</div>
        <div class="label">Berapa ${d.satuan} yang kembali${d.satuan === 'kg' ? ' (boleh sebagian)' : ''}</div>
        <div class="angka">${s.ketik || '0'} <span class="ket">${d.satuan}</span>${n.nilai ? h` <span class="ket">= ${RP(n.nilai)}</span>` : ''}</div>
        ${tuts(null, '')}
        <div class="label">Barangnya boleh dijual lagi?</div>
        <div class="tombol-baris"><div class="kaca-btn ${s.rtKondisi === 'utuh' ? 'aktif' : ''}" data-aksi="rtKondisi" data-v="utuh">Layak → kembali ke stok</div><div class="kaca-btn ${s.rtKondisi === 'tidak_utuh' ? 'aktif' : ''}" data-aksi="rtKondisi" data-v="tidak_utuh">Rusak / ragu → Karantina</div></div>
        <div class="label">Alasan (wajib)</div>
        <div class="bendera">${RT.ALASAN_RETUR.map((a) => h`<span class="pil ${s.rtAlasan === a ? 'nyala' : ''}" data-aksi="rtAlasanChip" data-v="${a}">${a}</span>`)}</div>
        <input class="ketik-nama" id="rtAlasan" type="text" value="${s.rtAlasan}" data-ketik="rtAlasan" placeholder="atau tulis alasannya">
        <div class="label">Diselesaikan dengan</div>
        <div class="tombol-baris"><div class="kaca-btn ${tukar ? '' : 'aktif'}" data-aksi="rtPenyelesaian" data-v="refund">Uang kembali</div><div class="kaca-btn ${tukar ? 'aktif' : ''}" data-aksi="rtPenyelesaian" data-v="tukar">Tukar barang</div></div>
        ${tukar ? h`<div class="pita-info">Tukar: nilai ${RP(n.nilai)} dipotong dari keranjang pengganti. Retur + penjualan penggantinya dicatat BERSAMA saat nota dicatat — tidak bisa bon, tidak bisa bayar sebagian.</div>`
          : h`<div class="ket" style="cursor: pointer; text-decoration: underline;" data-aksi="rtTimpa">${s.rtTimpa ? 'pakai hitungan sistem ' + RP(n.nilai) : 'kembalikan LEBIH KECIL dari hitungan sistem?'}</div>
            ${s.rtTimpa ? h`<input class="ketik-nama" id="rtNominal" type="text" inputmode="numeric" value="${s.rtNominal}" data-ketik="rtNominal" placeholder="uang yang dikembalikan (Rp), paling banyak ${RP(n.nilai)}"><input class="ketik-nama" id="rtAlasanTimpa" type="text" value="${s.rtAlasanTimpa}" data-ketik="rtAlasanTimpa" placeholder="kenapa lebih kecil (wajib, jejak permanen)">` : ''}`}
        ${s.kabar && s.kabarAwas ? h`<div class="pita-info awas">${s.kabar}</div>` : ''}
        <div class="utama" data-aksi="catatRetur">${tukar ? 'IKAT KE KERANJANG · pilih penggantinya' : 'CATAT RETUR · uang keluar ' + RP(s.rtTimpa ? L.angkaRupiah(s.rtNominal) : n.nilai)}</div>
      </div>`;
    }
    if (s.lembar === 'pesanan') {
      const daftar = L.daftarPesanan(s.psSaring);
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Pesanan', 'BUKAN uang & BUKAN stok sampai notanya dicatat · dipesan → diantar → dibayar lewat nota')}
        <input class="ketik-nama" id="psSaring" type="text" value="${s.psSaring}" data-ketik="psSaring" placeholder="saring nama pemesan">
        <div class="daftar-nama">${daftar.map((o) => h`<div class="ps-kartu">
          <div class="atas"><b>${o.nama}</b><span class="pil status-${o.status}">${L.STATUS_PESANAN[o.status] || o.status}</span></div>
          <div class="isi">${o.isi}${o.alamat ? h` · <span class="ket">${o.alamat}</span>` : ''}</div>
          <div class="ket">${tanggalPendek(o.tanggal)}${o.jam ? ' · ' + o.jam : ''}${o.nilai ? ' · perkiraan ' + RP(o.nilai) : ''}</div>
          <div class="aksi">
            ${o.status === 'dipesan' ? h`<span class="pil" data-aksi="antarPesanan" data-id="${o.id}">→ antar</span>` : ''}
            ${s.pesananId === o.id ? h`<span class="pil utamaKecil" data-aksi="lepasPesanan">✓ terikat ke keranjang · lepas</span>` : h`<span class="pil utamaKecil" data-aksi="ikatPesanan" data-id="${o.id}">catat jualnya →</span>`}
            <span class="pil" data-aksi="batalPesanan" data-id="${o.id}">batalkan</span>
          </div>
        </div>`)}${daftar.length ? '' : h`<div class="ket" style="padding: 10px 4px;">${s.psSaring ? 'Tidak ada pesanan aktif atas nama itu.' : 'Belum ada pesanan aktif.'}</div>`}</div>
        <div class="bulat"></div>
        <div class="judul">Pesanan baru</div>
        <div class="ps-form">
          <input class="ketik-nama" id="psNama" type="text" value="${s.psNama}" data-ketik="psNama" placeholder="Nama pemesan">
          <input class="ketik-nama" id="psIsi" type="text" value="${s.psIsi}" data-ketik="psIsi" placeholder="Pesan apa (mis. 2 karung Angsa)">
          <input class="ketik-nama" id="psAlamat" type="text" value="${s.psAlamat}" data-ketik="psAlamat" placeholder="Alamat antar (boleh kosong)">
          <input class="ketik-nama" id="psNilai" type="text" inputmode="numeric" value="${s.psNilai}" data-ketik="psNilai" placeholder="Perkiraan nilai Rp (boleh kosong)">
          <div class="kaca-btn aktif" data-aksi="simpanPesanan">CATAT PESANAN</div>
        </div>
      </div>`;
    }
    if (s.lembar === 'struk') return gambarStruk(s, L1, muncul, kepala);
    if (s.lembar === 'aturStruk') return gambarAturStruk(s, L1, muncul, kepala);
    if (s.lembar === 'aturWadah') return gambarAturWadah(s, L1, muncul, kepala);
    if (s.lembar === 'bayar') {
      const tolak = L.alasanTolak(s);
      const kunciKredit = s.cara === 'Kredit' && !t.sisaJadiBon && s.keranjang.length ? L.alasanKunciKredit(s, t.total) : null;
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala('Bayar', s.keranjang.length + ' barang' + (s.pelanggan ? ' · ' + s.pelanggan : ''))}
        ${t.kredit ? h`<div class="ket">keranjang ${RP(t.subtotal - t.potongan)} − barang kembali (tukar) ${RP(t.kredit)}</div>` : ''}
        <div class="total"><span class="label">${t.kredit ? 'Pembeli bayar' : 'Ditagih'}</span><span class="n">${RP(Math.max(0, t.total))}</span></div>
        ${t.bulat ? h`<div class="ket">termasuk pembulatan ke Rp500 ${RP(t.bulat)} (${s.cara === 'Kredit' ? 'bon ikut dibulatkan' : 'tunai'})</div>` : ''}
        <div class="tombol-baris">${[['Tunai', 'Tunai'], ['QRIS', 'QRIS'], ['Kredit', 'Bon']].map(([c, nm]) => h`<div class="kaca-btn ${s.cara === c ? 'aktif' : ''}" data-aksi="cara" data-cara="${c}">${nm}</div>`)}</div>
        ${s.cara === 'Tunai' ? h`
          <div class="label">Uang yang diterima — ketuk lembarannya</div>
          <div class="pecahan">${L.PECAHAN.map((p) => h`<div class="kaca-btn" data-aksi="pecahan" data-n="${p}">${p >= 1000 ? p / 1000 + ' rb' : p}</div>`)}<div class="kaca-btn aktif" data-aksi="uangPas">PAS</div></div>
          <div class="total"><span class="label">diterima ${t.uang ? h`<span class="ket" style="text-decoration: underline; cursor: pointer;" data-aksi="hapusUang">hapus</span>` : ''}</span><span class="n" style="font-size: 20px;" data-gulir="${t.uang}">${RP(t.uang)}</span></div>
          ${t.kembalian ? h`<div class="total" data-k="kembalian"><span class="label">Kembalian</span><span class="n" style="font-size: 20px;" data-gulir="${t.kembalian}">${RP(t.kembalian)}</span></div>` : ''}
          ${t.sisaJadiBon ? h`<div class="pita-info awas">kurang ${RP(t.kurang)} — sisanya jadi bon atas nama ${s.pelanggan || '… (pilih nama pembelinya)'}. Yang kurang dicatat di buku bon, bukan ditolak, bukan dianggap lunas.</div>` : ''}
` : ''}
        ${s.cara === 'QRIS' ? h`<div class="pita-info">QRIS = angka persis, tidak dibulatkan. Yang masuk rekening sudah dipotong MDR — catatan toko, tidak dicetak di struk.</div>` : ''}
        ${s.cara === 'Kredit' ? h`<div class="pita-info ${s.pelanggan ? '' : 'awas'}">Bon ${s.pelanggan ? 'atas nama ' + s.pelanggan + (info && info.sisa > 0 ? ' — bon lama ' + RP(info.sisa) : '') : 'harus ada nama pembelinya'}${info && info.batas ? ' · batas ' + RP(info.batas) + ' (2× belanja bulanan)' : ''}</div>` : ''}
        ${kunciKredit && s.pelanggan ? h`<div class="pita-info awas">${kunciKredit}</div><div class="kaca-btn putus" data-aksi="bukaKredit">Buka kredit SEKALI untuk nota ini (keputusan owner, tercatat)</div>` : ''}
        ${s.kreditDibuka && s.cara === 'Kredit' ? h`<div class="ket">kredit dibuka sekali oleh owner — nota membawa tanda kreditDibukaOwner</div>` : ''}
        <div class="kaca-btn" data-aksi="bukaPelanggan">${s.pelanggan ? s.pelanggan : 'Nama pembeli'}</div>
        <div class="utama ${tolak ? 'redup' : ''}" data-aksi="simpan">${tolak || 'CATAT NOTA · ' + RP(t.total)}</div>
        <div class="ket" style="text-align: center;">${sumber.jenis === 'cadangan' ? 'SIMULASI — tidak ke Firestore' : 'masuk ke koleksi penjualan yang sama dengan sistem lama; bisa dibatalkan ' + L.BATAS_URUNGKAN_DETIK + ' detik sesudahnya'}</div>
        ${s.cara === 'Tunai' ? h`<div class="bulat"></div><div class="ket">atau ketik nominal uang yang diterima:</div><div class="angka" style="font-size: 20px;">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>${tuts('uangKetik', 'PAKAI NOMINAL INI')}` : ''}
      </div>`;
    }
    return '';
  }

  // ---------- putaran 15: repack + wadah (merek kemasan → ukuran → lembar → dijual / ditanggung; upah per nota) ----------
  function gambarRepackWadah(s) {
    const kg = L.angkaKetik(s.ketik); const daftar = WJ.daftarAturWadah(); const dw = s.rpWadah ? daftar.find((d) => d.jenis === s.rpWadah) : null;
    const lembar = Math.max(0, Math.round(L.angkaKetik(s.rpLembar)));
    let ketSisi = '';
    if (dw) {
      if (s.rpDijual) ketSisi = dw.harga ? 'Masuk nota sebagai barang: ' + RP(dw.harga) + ' × ' + lembar + ' lembar = ' + RP(dw.harga * lembar) + '. Menambah omzet.' : dw.label + ' belum punya harga jual — layar menolak menagihnya. Setel harganya (jalur Wadah › Atur) atau pilih ditanggung toko.';
      else ketSisi = 'Tidak masuk nota. ' + (dw.adaModal ? 'Nilainya ' + RP(dw.modal) + ' × ' + lembar + ' lembar = ' + RP(dw.modal * lembar) + ', masuk HPP baris repack (memotong margin).' : 'Nilainya belum ada karena wadah ini belum pernah tercatat dibeli — HPP tidak bertambah.');
    }
    return h`<div class="bulat"></div><div class="label">Wadahnya (boleh dilewati)</div>
      <div class="rak-wadah-kecil">${daftar.map((d) => h`<div class="kaca-btn ${s.rpWadah === d.jenis ? 'aktif' : ''}" data-k="rpw-${d.jenis}" data-aksi="rpWadah" data-jenis="${d.jenis}"><span>${d.label}</span><span class="ket">${d.harga ? RP(d.harga) + '/lembar' : 'tanpa harga jual'} · ${d.hasilSamping ? 'hasil samping' : 'buku ' + d.sisaBuku}</span></div>`)}</div>
      ${dw ? h`<div class="baris-wadah-repack" data-k="rp-lembar"><span>Lembar</span><span class="step"><span data-aksi="rpLembar" data-d="-1">−</span><span class="n">${lembar}</span><span data-aksi="rpLembar" data-d="1">+</span></span><span class="ket tautan" data-aksi="rpSaran">saran ${WJ.saranLembar(kg, dw.jenis)} lembar dari ${DESIMAL(kg)} kg — boleh ditimpa</span></div>
        <div class="tombol-baris"><div class="kaca-btn ${s.rpDijual ? 'aktif' : ''}" data-aksi="rpDijual" data-v="1">Dijual ke pembeli</div><div class="kaca-btn ${!s.rpDijual ? 'aktif' : ''}" data-aksi="rpDijual" data-v="0">Ditanggung toko</div></div>
        <div class="ket ${s.rpDijual && !dw.harga ? 'awas-teks' : ''}">${ketSisi}</div>` : ''}
      <input class="ketik-nama sempit" id="rpUpah" type="text" inputmode="numeric" value="${s.rpUpah}" data-ketik="rpUpah" placeholder="Upah repack Rp (boleh kosong) — melekat ke baris repack">`;
  }
  // ---------- putaran 15: struk (JS3-A: kertas 58/80 & WhatsApp dari satu penyusun; JS3-C: aturan otomatis) ----------
  function gambarStruk(s, L1, muncul, kepala) {
    const n = notaStruk();
    if (!n) return h`${L1}<div class="lembar ${muncul}" data-k="lembar-struk">${kepala('Struk', 'nota tidak ditemukan')}<div class="pita-info awas">Nota ini tidak ada di data yang dimuat perangkat ini.</div></div>`;
    const st = ST.susunStruk(n.nota, n.atur, n.pilih); const o = ST.putusOto(n.atur, n.nota); const riw = ST.riwayatStruk(hariIniIso(s.sekarang));
    return h`${L1}<div class="lembar ${muncul}" data-k="lembar-struk">
      ${kepala('Struk · ' + (n.nota.nama || 'tanpa nama'), tanggalPendek(n.nota.tanggal) + (n.nota.jam ? ' ' + n.nota.jam : '') + ' · ' + RP(n.nota.total) + ' · ' + (n.nota.cara === 'Kredit' ? 'Bon' : n.nota.cara) + (n.nota.berlaku ? '' : ' · SUDAH ' + (n.nota.dibatalkan ? 'DIBATALKAN' : 'DIKOREKSI')))}
      <div class="bendera"><span class="ket" style="align-self: center;">kertas</span>${[58, 80].map((k) => h`<span class="pil ${n.pilih.kertas === k ? 'nyala' : ''}" data-aksi="strukKertas" data-mm="${k}">${k} mm</span>`)}<span class="ket tautan" style="margin-left: auto; align-self: center;" data-aksi="bukaAturStruk">atur kop & aturan ›</span></div>
      <div class="bendera">${ST.ST_SERTAKAN.map(([k, nm]) => h`<span class="pil ${n.pilih.sertakan[k] ? 'nyala' : ''}" data-aksi="strukSertakan" data-nama="${k}">${nm}</span>`)}</div>
      <pre class="st-kertas k${n.pilih.kertas}" data-k="kertas-struk">${st.teks}</pre>
      <div class="tombol-baris"><div class="kaca-btn aktif" data-aksi="kirimWa">Kirim WhatsApp</div><div class="kaca-btn" data-aksi="cetakStruk">Cetak</div></div>
      <div class="ket">Struk yang sama untuk kertas dan WhatsApp — cuma menyusun nota yang sudah tersimpan, tidak ada angka baru. WhatsApp dibuka tanpa nomor tujuan (WhatsApp yang bertanya ke siapa; nomor pembeli tidak disimpan). Cetak = dialog cetak perangkat ini; printer struk tertanam baru ada di tablet karyawan.</div>
      ${n.nota.cara === 'QRIS' ? h`<div class="pita-info">QRIS: yang masuk rekening sudah dipotong MDR — catatan toko, tidak dicetak di struk pembeli.</div>` : ''}
      <div class="ket">Aturan otomatis untuk nota seperti ini: <b>${o.teks}</b> (diatur di "atur kop & aturan").</div>
      <div class="bulat"></div>
      <div class="label">${riw.length} struk keluar hari ini</div>
      <div class="hari" data-k="riwayat-struk">${riw.slice(0, 6).map((r) => h`<div class="r" data-k="rs-${r.id}"><span class="w">${r.jam}</span><span class="t">${r.cara} · ${r.nama}${r.ket ? ' · ' + r.ket : ''}</span><span class="n">${RP(r.total)}</span></div>`)}${riw.length ? '' : h`<div class="ket">belum ada</div>`}</div>
    </div>`;
  }
  function gambarAturStruk(s, L1, muncul, kepala) {
    const a = s.aturStruk || ST.stAtur(); const n = s.strukKunci ? ST.notaDari(s.strukKunci) : null; const kunci = n && n.nama ? kunciPelanggan(n.nama) : '';
    const pil = (nyala, aksi, data, teks) => h`<span class="pil ${nyala ? 'nyala' : ''}" data-aksi="${aksi}" ${mentah(Object.keys(data).map((k) => 'data-' + k + '="' + String(data[k]).replace(/"/g, '&quot;') + '"').join(' '))}>${teks}</span>`;
    return h`${L1}<div class="lembar ${muncul}" data-k="lembar-aturStruk">
      ${kepala('Atur struk', 'kop & kalimat kaki berlaku untuk kertas dan WhatsApp sekaligus — setelan owner')}
      <input class="ketik-nama sempit" id="stKopNama" type="text" value="${a.kop.nama}" data-ketik="aturStrukKop" data-kolom="nama" placeholder="Nama toko (kop)">
      <input class="ketik-nama sempit" id="stKopAlamat" type="text" value="${a.kop.alamat}" data-ketik="aturStrukKop" data-kolom="alamat" placeholder="Alamat (boleh kosong)">
      <input class="ketik-nama sempit" id="stKopTelp" type="text" value="${a.kop.telp}" data-ketik="aturStrukKop" data-kolom="telp" placeholder="Telepon / WhatsApp toko (boleh kosong)">
      <input class="ketik-nama sempit" id="stKaki" type="text" value="${a.kaki}" data-ketik="aturStrukKaki" placeholder="Kalimat kaki, mis. Terima kasih 🙏">
      <div class="label">Lebar kertas</div><div class="bendera">${[58, 80].map((k) => pil(a.kertas === k, 'aturStrukKertas', { mm: k }, k + ' mm'))}</div>
      <div class="label">Disertakan (bawaan; bisa diubah per struk)</div><div class="bendera">${ST.ST_SERTAKAN.map(([k, nm]) => pil(!!a.sertakan[k], 'aturStrukSertakan', { nama: k }, nm))}</div>
      <div class="label">Cetak otomatis sesudah nota tersimpan</div><div class="bendera">${ST.ST_OTO_CETAK.map(([v, nm]) => pil(a.oto.cetak === v, 'aturStrukOto', { jalur: 'cetak', v }, nm))}</div>
      <div class="label">WhatsApp otomatis sesudah nota tersimpan</div><div class="bendera">${ST.ST_OTO_WA.map(([v, nm]) => pil(a.oto.wa === v, 'aturStrukOto', { jalur: 'wa', v }, nm))}</div>
      ${kunci ? h`<div class="label">Pilihan ${n.nama} — mengalahkan aturan</div><div class="bendera">${ST.ST_PILIHAN_ORANG.map(([v, nm]) => pil((a.perOrang[kunci] || 'ikut') === v, 'aturStrukOrang', { kunci, v }, nm))}</div>` : h`<div class="ket">Pilihan per pelanggan diatur dari struk nota yang ada namanya.</div>`}
      ${Object.keys(a.perOrang).length ? h`<div class="ket">Pelanggan dengan pilihan sendiri: ${Object.keys(a.perOrang).map((k) => k + ' → ' + (ST.ST_PILIHAN_ORANG.find((x) => x[0] === a.perOrang[k]) || [])[1]).join(' · ')}</div>` : ''}
      <div class="ket">Cetak otomatis membuka dialog cetak perangkat ini. WhatsApp otomatis bisa DITAHAN peramban HP (jendela baru tanpa ketukan) — kalau begitu dikatakan, dan tombol Kirim WhatsApp tetap ada di struk. Bawaan keduanya mati.</div>
      <div class="utama" data-aksi="simpanAturStruk">SIMPAN SETELAN STRUK</div>
    </div>`;
  }
  function gambarAturWadah(s, L1, muncul, kepala) {
    const daftar = WJ.daftarAturWadah(); const isi = s.aturWadah || {};
    return h`${L1}<div class="lembar ${muncul}" data-k="lembar-aturWadah">
      ${kepala('Harga jual wadah', 'per LEMBAR · kosong = tidak dijual · lantai ' + RP(WJ.WJ_LANTAI_LEMBAR))}
      <div class="pita-info">Wadah = barang dagangan (owner 17 Sep). Yang diberi harga tampil di jalur Wadah dan bisa dijual dari Repack sebagai baris nota; yang kosong hanya bisa "ditanggung toko". Modal dibaca dari buku kantong sistem lama.</div>
      <div class="daftar-nama" style="max-height: 46vh;">${daftar.map((d) => h`<div class="baris-atur-wadah" data-k="aw-${d.jenis}"><div><div style="font-weight: 600;">${d.label}</div><div class="ket ${d.modalAneh ? 'awas-teks' : ''}">${d.hasilSamping ? 'hasil samping · buku ' + d.sisaBuku : 'buku ' + d.sisaBuku + ' lembar'} · ${d.adaModal ? 'modal ' + RP(d.modal) : 'modal belum ada'}${d.modalAneh ? ' · PERIKSA catatan belinya' : ''}${d.sejak ? ' · harga sejak ' + tanggalPendek(d.sejak) : ''}</div></div><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${isi[d.jenis] || ''}" data-ketik="aturWadahKetik" data-jenis="${d.jenis}" placeholder="Rp/lembar"></div>`)}</div>
      <div class="utama" data-aksi="simpanAturWadah">SIMPAN HARGA JUAL WADAH</div>
    </div>`;
  }

  K.dengar(() => { gambar(); gulirkan(akar, RP); });
  let _jamUrung = null;
  K.dengar((s) => { clearTimeout(_jamUrung); if (s.notaTerakhir) _jamUrung = setTimeout(gambar, Math.max(0, L.BATAS_URUNGKAN_DETIK * 1000 - (Date.now() - s.notaTerakhir.pada) + 50)); });
  dengarkan(() => { _rak = null; gambar(); gulirkan(akar, RP); });
  gambar(); gulirkan(akar, RP);
  return { keadaan: K, gambar };
}
