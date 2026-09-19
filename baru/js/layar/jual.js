// LAYAR JUAL — GAMBAR & KETUKAN. Satu markup untuk tiga lebar; lebar diatur css/kerangka.css.
// Logika (rak, tagihan, antrean, bayar) ada di jual-logika.js dan diuji tanpa peramban.
import { h, mentah, gabung, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, ANGKA, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as L from './jual-logika.js';
import * as RT from './retur-logika.js';
import { sumberData, dengarkan, tulisDokumen, hapusDokumen } from '../data/toko.js';
import { gulirkan, terbangkan, tengah, sekali } from '../inti/gerak.js';
import { adeganSerok, adeganKemasanMasuk, adeganSerahTerima, adeganKarung } from './adegan.js';

import { gambarWadah, gambarChipBarang } from './gambar.js';

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
    chip: ({ jalur, kunci, berat }) => { const rak = rakKini(); const c = (rak[jalur] || []).find((x) => x.kunci === kunci && (!berat || String(x.berat) === berat)); if (c) set(L.ketukChip(S(), c)); },
    sering: ({ id }) => { const c = rakKini().sering.find((x) => x.id === id); if (c) set(L.ketukChip(S(), c)); },
    tuts: ({ t }) => set(L.tekanTuts(S(), t)),
    preset: ({ n }, el) => masukDenganGerak(L.masukkan(S(), Number(n)), el),
    masukkan: (arg, el) => masukDenganGerak(L.masukkan(S()), el),
    isiUlangWadah: async ({ merk }) => {
      const r = L.susunIsiUlangWadah(merk, L.waktuSekarang(S().sekarang || undefined));
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      try { const h = await tulisDokumen(r.dokumen); if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true }); set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); }
      catch (e) { set({ kabar: 'GAGAL menandai isi ulang: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
    },
    tutup: () => set({ lembar: null, pilih: null, negoId: null, ketik: '' }),
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
        set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI (cadangan, tidak ke Firestore) — ' : h && h.antre ? 'Tersimpan di perangkat, menunggu server — ' : 'Tersimpan — ') + r.ringkas }));
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
  };
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
    } else if (baris.jenis === 'kemasan') {
      if (adeganKemasanMasuk({ nama: baris.label, ukuran: String(baris.ukuranKemasan).replace('.', ','), jumlahTeks: DESIMAL(baris.jumlah) + ' kemasan' + (baris.bonusUnit ? ' + bonus' : '') })) lamaAdegan = 900;
    }
    const mendarat = () => { const bilah = akar.querySelector('.ringkas-keranjang'); if (dari) terbangkan(lamaAdegan ? { x: innerWidth / 2, y: 150 } : dari, bilah); setTimeout(() => sekali(akar.querySelector('.jual-keranjang'), 'pegas', 520), 420); };
    setTimeout(() => requestAnimationFrame(mendarat), lamaAdegan);
  }
  // nota dicatat → adegan menurut barang TERBESAR nilainya: karung diangkut, selain itu serah terima (kantong kertas / kemasan)
  function adeganNota(nota, keranjang, uangDiterima) {
    const utama = keranjang.slice().sort((a, b) => (b.trx.nilaiBarangPengganti || b.trx.hargaTotal || 0) - (a.trx.nilaiBarangPengganti || a.trx.hargaTotal || 0))[0]; if (!utama) return;
    const t = utama.trx; const cara = nota.cara; const kembali = cara === 'Tunai' && uangDiterima > nota.tagihan ? 'kembali ' + RP(uangDiterima - nota.tagihan) : nota.bayarSebagian ? 'sisa jadi bon' : '';
    const data = { cara: nota.bayarSebagian ? 'Tunai' : cara, jumlahRp: RP(nota.bayarSebagian || nota.tagihan), ket: kembali };
    if (t.jenis === 'karung') adeganKarung(Object.assign(data, { berat: String(t.beratKarungAcuan || 50), banyak: DESIMAL(t.jumlah) + ' karung ' + (t.merkSumber || '') }));
    else adeganSerahTerima(Object.assign(data, { jenis: t.jenis === 'kemasan' ? 'kemasan' : 'kantong', ukuran: t.jenis === 'kemasan' ? String(t.ukuranKemasan).replace('.', ',') : '' }));
  }
  async function tulisPesanan(r) {
    if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
    try {
      const h = await tulisDokumen(r.dokumen);
      if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true });
      set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar }));
    } catch (e) { set({ kabar: 'GAGAL menulis pesanan: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  delegasi(akar, aksi);

  let _rak = null, _rakUntuk = '', _lembarSebelum = null;
  function rakKini() {
    const s = S(); L.sinkronKeranjang(s);
    // rak bergantung pada ISI keranjang (jumlah + bonus), bukan cuma banyaknya baris — +1 unit atau bonus mengubah sisa chip
    const tanda = (s.tukar ? 'tk' : '') + s.pelanggan + '|' + s.keranjang.map((b) => b.trx.jenis + ':' + b.trx.jumlah + ':' + (b.trx.bonusUnit || 0)).join(',') + '|' + s.antrean.length + '|' + opsi.versiData();
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
        ${adaUrung ? h`<div class="pita-info urung"><span>Nota barusan: ${s.notaTerakhir.ringkas}</span><span class="kaca-btn putus" data-aksi="batalkanNota">Batalkan nota barusan</span></div>` : ''}
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
              <div class="t"><div style="font-weight: 600;">${b.trx.label}</div><div class="ket">${DESIMAL(b.trx.jumlah)} ${b.trx.satuan} × ${RP(b.trx.hargaSatuan)}${b.trx.nego ? ' · nego' : ''}${b.trx.kemasanLiteran ? ' · ' + (b.trx.jumlahKemasanLiteranDipakai || 1) + ' kantong' : ''}${b.trx.bonusUnit ? ' · +1 bonus (stok ' + b.trx.jumlahUnit + ')' : ''}${b.trx.penggantiRetur ? ' · PENGGANTI RETUR, nilai ' + RP(b.trx.nilaiBarangPengganti) : ''}</div></div>
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
          ${hari.terakhir.map((r) => h`<div class="r"><span class="w">${r.jam}</span><span class="t">${r.teks}${r.nama ? ' · ' + r.nama : ''}</span><span class="n">${RP(r.n)}</span></div>`)}
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
    if (!daftar.length) return h`<div class="pita-info">${s.jalur === 'sering' ? (s.pelanggan ? s.pelanggan + ' belum punya kebiasaan belanja 90 hari terakhir' : 'Belum ada yang laku 28 hari terakhir') : 'Belum ada barang berharga di jalur ini — isi harganya di Katalog'}</div>`;
    // isi gambar = sisa relatif terhadap yang paling banyak DI KELOMPOKNYA (wadah literan memakai isinya sendiri, bukan perbandingan)
    const satuChip = (c, penuh, i) => h`<div class="chip ${s.pilih && s.pilih.kunci === c.kunci && s.pilih.jalur === c.jalur && (s.pilih.berat || 0) === (c.berat || 0) ? 'dipilih' : ''} ${c.sisa <= 0 ? 'habis' : c.sisa <= 2 ? 'kurang' : ''} ${c.wadah && c.wadah.diketahui && c.wadah.perluIsi ? 'isi-ulang' : ''}"
        data-k="chip-${s.jalur}-${c.jalur}-${c.kunci}-${c.berat || ''}" style="--urut: ${Math.min(i, 14)};"
        data-aksi="${s.jalur === 'sering' ? 'sering' : 'chip'}" data-id="${c.id || ''}" data-jalur="${c.jalur}" data-kunci="${c.kunci}" data-berat="${c.berat || ''}">
      <div class="teks-chip">
        <div class="nama">${c.nama}</div>
        <div class="rinci">${c.ukuran}${c.keterangan ? ' · ' + c.keterangan : ''}</div>
        <div class="harga">${RP(c.harga)}<span class="satuan">/${c.satuan}</span></div>
        <div class="stok">${c.sisa <= 0 ? 'habis' : c.sisaTeks}${c.dipegang > 0 ? ' · ' + (c.jalur === 'kemasan' ? c.dipegang + ' unit' : DESIMAL(c.dipegang) + ' kg') + ' dipegang struk lain' : ''}</div>
        ${c.wadah ? h`<div class="stok wadah-ket">${!c.wadah.diketahui ? 'wadah belum ditandai isi ulang' : c.wadah.perluIsi ? 'WADAH ±' + DESIMAL(c.wadah.sisaKg) + ' kg — ISI ULANG' : 'wadah ±' + DESIMAL(c.wadah.sisaKg) + ' kg'}</div>` : ''}
      </div>
      <div class="gambar-chip">${mentah(gambarChipBarang(c, penuh))}</div>
    </div>`;
    const maks = (d) => Math.max(1, ...d.map((c) => c.sisa || 0));
    const kelompok = s.jalur !== 'sering' && rak.kelompok && rak.kelompok[s.jalur] ? rak.kelompok[s.jalur] : null;
    if (kelompok) return h`${kelompok.map((g) => h`<div class="kelompok-rak" data-k="kel-${s.jalur}-${g.k}"><div class="judul-kelompok"><span>${g.judul}</span><span class="ket">${g.daftar.length} barang · termurah dulu</span></div>
      <div class="rak-chip">${g.daftar.map((c, i) => satuChip(c, maks(g.daftar), i))}</div></div>`)}`;
    return h`<div class="rak-chip" data-k="rak-${s.jalur}">${daftar.map((c, i) => satuChip(c, maks(daftar), i))}</div>`;
  }

  function gambarLembar(s, rak, t, info, muncul) {
    const sumber = sumberData();
    if (!s.lembar || s.lembar === 'keranjang') return '';
    const L1 = h`<div class="lembar tirai" data-k="tirai" data-aksi="tutup"></div>`;
    const kepala = (judul, ket) => h`<div style="display: flex; justify-content: space-between; align-items: baseline;"><span class="judul">${judul}</span><span class="ket" style="cursor: pointer; text-decoration: underline;" data-aksi="tutup">tutup</span></div>${ket ? h`<div class="ket">${ket}</div>` : ''}`;
    const tuts = (aksiMasuk, label) => h`<div class="tuts">${TUTS.map((k) => h`<div class="k ${/^\d$/.test(k) ? '' : 'f'}" data-aksi="tuts" data-t="${k}">${k}</div>`)}${aksiMasuk ? h`<div class="k f aksi" style="grid-column: span 4;" data-aksi="${aksiMasuk}">${label}</div>` : ''}</div>`;
    if (s.lembar === 'jumlah' && s.pilih) {
      const c = s.pilih; const maks = L.maksUntuk(c);
      const preset = c.jalur === 'karung' ? [1, 2, 5, 10] : c.jalur === 'kemasan' ? [1, 2, 3, 5] : c.jalur === 'repack' ? [5, 10, 20, 25] : [1, 2, 5, 10];
      return h`${L1}<div class="lembar ${muncul}" data-k="lembar-${s.lembar}">
        ${kepala(c.nama + ' ' + c.ukuran, RP(c.harga) + '/' + c.satuan + ' · bebas dijual ' + (maks === null ? '—' : DESIMAL(maks) + ' ' + c.satuan))}
        ${c.jalur === 'literan' && c.wadah ? (() => { const w = L.tinggiWadah(c.kunci, s); return h`<div class="baris-wadah"><div class="gambar-chip besar">${mentah(gambarWadah(w))}</div>
          <div><div class="ket">${!w.diketahui ? 'Wadah ini belum pernah ditandai diisi ulang, jadi isinya belum bisa digambar.' : 'Isi wadah ±' + DESIMAL(w.sisaKg) + ' kg dari ' + w.penuhKg + ' kg · ditandai penuh ' + tanggalPendek(w.sejakTanggal) + ' ' + w.sejakJam + (w.lewat ? ' · sudah terjual ' + DESIMAL(w.lewat) + ' kg LEBIH dari isinya — lupa menandai?' : '')}</div>
            <div class="kaca-btn ${w.diketahui && !w.perluIsi ? '' : 'aktif'}" data-aksi="isiUlangWadah" data-merk="${c.kunci}">Wadah baru diisi ulang (penuh, menggunung)</div></div></div>`; })() : ''}
        ${c.jalur === 'repack' ? h`<div class="ket">Jadi produk apa (nama jual di nota) — kosong = nama mereknya</div><input class="ketik-nama" id="namaRepack" type="text" value="${s.namaRepack}" data-ketik="namaRepack" placeholder="${c.nama}">` : ''}
        <div class="tombol-baris">${preset.map((n) => h`<div class="kaca-btn" data-aksi="preset" data-n="${n}">${n} ${c.satuan}</div>`)}</div>
        <div class="label">Jumlah</div><div class="angka">${s.ketik || '0'} <span class="ket">${c.satuan}</span>${s.ketik ? h` <span class="ket">= ${RP(c.harga * L.angkaKetik(s.ketik))}</span>` : ''}</div>
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

  K.dengar(() => { gambar(); gulirkan(akar, RP); });
  let _jamUrung = null;
  K.dengar((s) => { clearTimeout(_jamUrung); if (s.notaTerakhir) _jamUrung = setTimeout(gambar, Math.max(0, L.BATAS_URUNGKAN_DETIK * 1000 - (Date.now() - s.notaTerakhir.pada) + 50)); });
  dengarkan(() => { _rak = null; gambar(); gulirkan(akar, RP); });
  gambar(); gulirkan(akar, RP);
  return { keadaan: K, gambar };
}
