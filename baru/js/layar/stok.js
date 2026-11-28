// LAYAR STOK — GAMBAR & KETUKAN. Beranda Stok S9 (dikunci owner) + tab Wadah literan + lembar Barang masuk / Adukan / Cocokkan + tab Karantina yang memutuskan.
// Logika & angka di stok-logika.js, stok-catat-logika.js (ST1/ST3), stok-adukan-logika.js (ST2), stok-karantina-logika.js.
// Layar dimorf (elemen hidup terus) → batang isi, gunung wadah, dan angka bertransisi; baris masuk bergiliran saat lahir.
import { nanti, segera } from '../inti/jadwal.js';   // owner 29 Sep: bunyi data/status digabung sekali per bingkai (lag & freeze)
import { h, mentah, pasang, delegasi, esc } from '../inti/dom.js';
import { terkunci } from '../inti/kunci.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { pasangIsian } from '../inti/isian.js';
import { RP, DESIMAL, ANGKA, tanggalPendek, tanggalTutupAktif } from '../inti/format.js';
import * as S from './stok-logika.js';
import * as L from './jual-logika.js';
import * as C from './stok-catat-logika.js';
import { tpSusunPutus } from './titipan-logika.js';   // Tahap 5: usul dari tablet yang sudah dikerjakan owner ditandai "sudah diperiksa" (kabar barang masuk)
// paket P4 (owner 27 Nov 2026, A25): tarif bongkar kuli per karung — dicek di Barang masuk (cuma tanda)
import * as PB from './pembelian-logika.js';
import * as MT from './masuk-tablet-logika.js';   // owner 22 Nov 2026 (paket ③): barang masuk dari tablet — bon + titipan bongkar & bayar supir + kabar owner
import * as A from './stok-adukan-logika.js';
import * as Q from './stok-karantina-logika.js';
import * as KT from './stok-kantong-logika.js';
import * as TP from './stok-tempat-logika.js';
import * as HP from './stok-hpp-logika.js';
import { gambarWadah, gambarKarungStok } from './gambar.js';
import { tombolAkun, tombolLuarKisi, bukanOwner, batasHasilAdukan, batasDokumenKirim } from './akses-layar.js';
import { panelIsiUlang, aksiPanelWadah } from './wadah-panel.js';
import { kartuTerima, lembarTerima, aksiPanelTerima } from './terima-barang-panel.js';   // owner 21 Nov 2026: tanda terima barang masuk untuk supir pemasok
import { kartuFotoNota, aksiPanelFotoNota } from './foto-nota-panel.js';   // paket P8 (owner 27 Nov 2026, A94 · rules v26): foto nota kedatangan tunai & bon — owner + tablet Penjaga laci
import { adeganIsiUlang, adeganBukaKarung, adeganAdukan } from './adegan.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen, tulisBertahap, tolakKunciTanggal, kabarKiriman, kunciLuarCache } from '../data/toko.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { jbKelompokStok } from './jenis-beras-logika.js';
import * as VR from './varian-logika.js';
import * as WB from './wadah-bernama-logika.js';
import { aturHarga } from './harga-logika.js';
import { kkSertakanKiriman } from '../data/katalog-kasir.js';   // 25c: total per jenis beras (owner 27 Sep: Harga + Stok + Jual)
// putaran 30: kelas mutu merek
import * as KM from './kelas-merek-logika.js';
// owner 26 Nov 2026 (stok minus, label & kepatuhan): tab Tugas gudang (stok minus · hilang & rusak per jenis · tugas terbuka · kemasan bertanggal) + label sesudah
// adukan / Barang masuk (label-panel: satu pintu cetak label, tulisannya cuma kode label toko baru — tandaKenal)
import * as GD from './gudang-logika.js';
import * as JN from './janji-logika.js';   // paket tanggal janji (owner 27 Nov 2026, rules v24): janji datang pesanan ke pemasok dari tablet
import * as AB from './ambil-logika.js';   // owner 26 Nov 2026: barang titipan pembeli disebut di Cocokkan
import * as LB from './label-logika.js';
import * as SG from './stok-pantau-logika.js';   // paket P5 (owner 27 Nov 2026): kartu stok · produksi per bulan · rencana produksi · opname kejutan
import { kartuLabelAdukan, kartuLabelMasuk, aksiPanelLabel } from './label-panel.js';
// owner 26 Nov 2026 (Dasbor sensus B127, "Hari + kg per barang"): lembar stok minimum per barang (Stok › Gudang; Dasbor & Belanja membaca angka yang sama)
import { kartuStokMinimum, aksiPanelStokMinimum } from './stok-minimum-panel.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_TAB = 'miqbal_baru_stok_tab';
const KUNCI_DRAF_MASUK = 'miqbal_baru_draf_masuk';   // draf barang masuk per perangkat — pulih sesudah layar disegarkan (pola KUNCI_DRAF_MASUK index.html)
const KUNCI_DRAF_COCOK = 'miqbal_baru_draf_cocok';   // hitungan keliling gudang yang belum disimpan
const KUNCI_DRAF_ADUKAN = 'miqbal_baru_draf_adukan'; // adukan yang sedang diketik (bahan → hasil) — pulih sesudah layar disegarkan
const simpanLokal = (k, v) => { try { if (v) localStorage.setItem(k, JSON.stringify(v)); else localStorage.removeItem(k); } catch (e) { /* abaikan */ } };
const bacaLokal = (k) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } };

export function pasangLayarStok(akar, opsi) {
  const tabAwal = (() => { try { return localStorage.getItem(KUNCI_TAB) || 'gudang'; } catch (e) { return 'gudang'; } })();
  // putaran 23d: keadaan awal sebagai FUNGSI — dipanggil ulang saat ganti orang (inti/isian.js)
  // 30 Sep (owner: "terlalu banyak tampilan"): pengaturan karung & wadah di rincian wadah dilipat; terbuka/tertutupnya diingat per perangkat
  const KUNCI_RINCIAN_LAIN = 'miqbal_rincian_wadah_lain_v1';
  const rincianLainAwal = () => { try { return localStorage.getItem(KUNCI_RINCIAN_LAIN) === '1'; } catch (e) { return false; } };
  const awal = () => ({ tab: S.TAB_STOK.some((t) => t[0] === tabAwal) ? tabAwal : 'gudang', tanya: 'beli', kabar: '', kabarAwas: false, janjiP: null, wadahAktif: null, isiW: null, rincianLain: rincianLainAwal(), krKetik: '', krNama: '', krAsal: null, krPilih: false, lainPilih: false, gnKetik: '', akYakin: '', tandai: null, shKetik: '', bgKetik: '', bgAlasan: '', bgYakin: false, atur: null, drPilih: null, drYakin: false, tpTab: 'tiga',
    lembar: null, masuk: null, cocok: null, aturC: null, aturHpp: null, cpDraf: null, aturMutu: null, ptYakin: null, btYakin: null, rtDraf: null, yakinM: false, yakinHapus: false, yakinC: {}, puKetik: {}, puYakin: '', guYakin: '', ttgYakin: false, kbsYakin: false, kbNilai: '', kbNilaiYakin: false, kpTeks: '', kpYakin: false,
    adukan: null, yakinA: {}, yakinHapusA: false, bukaA: null, koreksiA: { total: '', alasan: '' }, qBuka: null, qAlasan: '', qYakin: '',
    // putaran 16: Kantong (ST4), Tempat simpan (ST5), HPP (ST6)
    kt: { jenis: '', jumlah: '', harga: '', toko: '' }, ktTab: 'rak', ktYakin: {}, ktHapus: null, ktAlasan: '', ktYakinHapus: false, aturKt: null,
    pkIsi: {}, pkYakin: null,   // owner 11 Okt: pecah kantong gabungan lama per merek — pkIsi[gabungan][merek] = teks lembar hasil hitung fisik; pkYakin = gabungan yang sudah diketuk sekali
    tp: { pilih: null, tempat: null }, aturTp: null,
    hp: { merk: null, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'kartu' }, aturHp: null, fifo: { pilih: '', yakin: '' },
    // putaran 27: tawaran harga jual varian sesudah barang masuk (Bagian 2)
    varianTawar: null, vrKetik: {}, vrYakin: false,
    // owner 21 Nov 2026: tanda terima barang masuk — tbm = { id } kedatangan yang kartunya sedang dibuka (null = tidak ada)
    tbm: null });
  const K = buatKeadaan(awal());
  const ISIAN = pasangIsian(K, awal, [['janjiP', (v) => !!(v && v.tanggal)], 'isiW', 'aturHpp', 'krKetik', 'kbNilai', 'krNama', 'gnKetik', 'shKetik', 'bgKetik', 'bgAlasan', ['puKetik', (v) => !!(v && Object.keys(v).length)], 'atur', 'koreksiA', 'qAlasan', 'kt', 'ktAlasan', 'aturKt', 'aturC', 'cpDraf', 'aturMutu', 'rtDraf', 'usDraf', 'ukKetik', ['tbKetik', (v) => !!(v && Object.keys(v).length)], 'tbMulai', ['tp', (v) => !!(v && v.pilih)], 'aturTp', ['hp', (v) => !!(v && (v.ketik || v.alasan || Object.keys(v.massal || {}).length))], 'aturHp', 'aturUm', 'aturKj', ['pkIsi', (v) => !!(v && Object.keys(v).length)], ['vrKetik', (v) => !!(v && Object.keys(v).some((k) => v[k]))]], [KUNCI_DRAF_MASUK, KUNCI_DRAF_COCOK, KUNCI_DRAF_ADUKAN]);
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; let _kotor = true;   /* owner 29 Sep (lag): permintaan gambar saat tersembunyi cukup MENANDAI; saat dibuka digambar hanya kalau kotor */ const kini = () => opsi.sekarang() || new Date();
  // sanggahan layar mulus 7 Okt: dibuka lagi tanpa data baru tetap digambar ulang bila hari, hari tutup aktif (jam 12 siang) atau titik kas perangkat
  // berubah sejak gambar terakhir (kunciLuarCache) — semuanya tidak menaikkan versi data
  let _kunciLuar = ''; const kunciLuar = () => kunciLuarCache(kini());
  const waktu = () => L.waktuSekarang(opsi.sekarang() || undefined);
  const KGs = (n) => DESIMAL(Math.round((Number(n) || 0) * 100) / 100) + ' kg';
  // atribut data-… untuk tombol yang dibangun dari daftar (nilai di-escape; tidak ada id yang menjadi kode)
  const atr = (o) => mentah(Object.keys(o || {}).map((k) => ' data-' + k + '="' + esc(o[k]) + '"').join(''));
  // sesudah karung dibuka (langsung, atau lewat ketukan kedua "tandai"): draf pilihan karung dikosongkan, adegan karung turun dari tumpukan
  const sesudahBukaKarung = (merk, wadah, r) => { set({ krNama: '', krAsal: null, krPilih: false, lainPilih: false, isiW: null, tandai: null }); const g = r.gudang; if (!g) return;
    adeganBukaKarung({ nama: merk, wadah: wadah || '', berat: g.kgKarung, dariKarung: g.dariKarung, keKarung: g.keKarung, dariKg: DESIMAL(Math.round(g.dariKg * 10) / 10), keKg: DESIMAL(Math.round(g.keKg * 10) / 10) }); };

  // putaran 25: hapus + dokumen dalam SATU kiriman yang hasilnya diperiksa (dulu dua kiriman: hapus lalu jejak/penggantinya); jalur besar dari bulan lalu
  // (r.kelompok: koreksi/hapus adukan) dikirim BERTAHAP; tolakan kunci membawa tombol pembalik (r.pembalik = 'cocok' → Cocokkan hari ini)
  async function tulis(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true, kpPembalik: r.pembalik || null }); return false; }
    try { const x = r.kelompok ? await tulisBertahap(r.judulBertahap || 'Koreksi stok bertahap', r.kelompok) : await tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus });
      if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch, { kpPembalik: null, kabar: kabarKiriman(x, r.patch.kabar) + (x && x.potongan > 1 ? ' (dikirim ' + x.potongan + ' tahap)' : '') })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  // owner 7 Okt: karung bekas yang lahir dari karung habis — akun bukan-owner menitipnya (owner mencatat), owner menulisnya langsung
  const stafKb = () => ({ staf: bukanOwner(opsi.akun ? opsi.akun() : null) });
  const keranjangJual = () => ({ keranjang: opsi.keranjangJual().keranjang, antrean: opsi.keranjangJual().antrean, batasDok: batasDokumenKirim(opsi.akun ? opsi.akun() : null) });   // 39b no. 21: isian takar akun bukan-owner
  // audit 39b no. 29: hitungan berat tab Wadah literan (buku semua wadah, daftar aktivasi, karung tertinggal, komposisi/selisih/cek wadah yang dibuka) dulu
  // diulang tiap ketukan & tiap huruf yang diketik (±50 ms di data toko 1 Okt). Kini sekali per (versi data · tanggal · isi keranjang Jual) — pola rak Jual.
  let _ingatW = { k: null, isi: {} };
  const ingatanWadah = () => { if (!opsi.versiData) return (nama, f) => f();   // tanpa versi data = tanpa ingatan (tidak pernah basi)
    const k = opsi.versiData() + '|' + tanggalTutupAktif(kini()) + '|' + JSON.stringify(keranjangJual()); if (_ingatW.k !== k) _ingatW = { k, isi: {} };
    const isi = _ingatW.isi; return (nama, f) => (nama in isi ? isi[nama] : (isi[nama] = f())); };
  // mode "atur susunan": draf di keadaan layar; baru ditulis saat SIMPAN (satu dokumen berisi seluruh aturan)
  const drafAtur = () => { const a = L.aturWadah(); const t = (n) => String(n).replace('.', ','); const kgl = { bawaan: a.kgPerLiter.bawaan ? t(a.kgPerLiter.bawaan) : '', merek: {} }; Object.keys(a.kgPerLiter.merek).forEach((m) => { kgl.merek[m] = t(a.kgPerLiter.merek[m]); }); return { kgl, penuh: t(a.penuhKg), puncak: t(a.puncakKg), ulang: t(a.isiUlangKg), takar: t(a.takarKg), susut: t(a.susutWajarKg), sisih: t(a.sisihKg), merekKarung: a.merekKarung.slice(), daftar: a.daftar.slice(), resep: JSON.parse(JSON.stringify(a.resep)), pilih: null, resepUntuk: null }; };
  // owner 22 Nov 2026: draf kosong Barang masuk per akun — tablet (bukan owner) selalu bon, dengan isian upah bongkar & bayar ke supir (titipan)
  const drafKosongMasuk = () => (bukanOwner(opsi.akun ? opsi.akun() : null) ? MT.mtDrafKosong(waktu()) : C.drafMasukKosong(waktu()));
  const ubahAtur = (f) => { const d = JSON.parse(JSON.stringify(st().atur || drafAtur())); f(d); set({ atur: d }); };
  const AKSI = Object.assign({
    // tombolMati (tombol peran mati dengan kalimat sebabnya) datang dari aksiPanelWadah (wadah-panel.js) — dulu ditulis dua kali, yang panel menang diam-diam
    // menutup lipatan membatalkan konfirmasi dua ketukan & pilihan yang menunggu di dalamnya (tidak ada yang hidup tersembunyi — tinjauan #76 S2)
    rincianLain: () => { const v = !st().rincianLain; try { localStorage.setItem(KUNCI_RINCIAN_LAIN, v ? '1' : '0'); } catch (e) { /* abaikan */ }
      set(Object.assign({ rincianLain: v }, v ? {} : { bgYakin: false, krPilih: false, krNama: '', krAsal: null, tandai: st().tandai && st().tandai.jenis === 'bukaKarung' ? null : st().tandai })); },
    tab: ({ t }) => { try { localStorage.setItem(KUNCI_TAB, t); } catch (e) { /* abaikan */ } set({ tab: t, kabar: '', tandai: null, akYakin: '', ttgYakin: false }); },
    tanya: ({ id }) => set({ tanya: id }),
    keBelanja: () => opsi.bukaHarga && opsi.bukaHarga('belanja'),   // putaran 17: Harga & Pemasok → Belanja (saran yang sama, per pemasok, muatan truk, pesanan WA)
    mode: () => opsi.gantiMode(),
    tutupKabar: () => set({ kabar: '' }),
    pilihWadah: ({ merk }) => set({ wadahAktif: st().wadahAktif === merk ? null : merk, isiW: null, krKetik: '', krNama: '', krAsal: null, krPilih: false, gnKetik: '', shKetik: '', bgKetik: '', bgAlasan: '', bgYakin: false, tandai: null, akYakin: '' }),
    // putaran 28 (owner 28 Sep): isi yang dikeluarkan dari kotak = karung wadah sendiri — sisihkan saat tutup, tuang balik saat buka, bongkar setahun sekali
    shKetik: (v) => set({ shKetik: String(v).slice(0, 6) }),
    bgKetik: (v) => set({ bgKetik: String(v).slice(0, 6), bgYakin: false }),
    bgAlasan: (v) => set({ bgAlasan: String(v).slice(0, 80) }),
    sisihkan: async ({ merk }) => { if (await tulis(WB.wbSusunSisih(merk, st().shKetik, waktu()))) set({ shKetik: '' }); },
    tuangBalik: async ({ merk }) => { if (await tulis(WB.wbSusunTuangBalik(merk, st().shKetik, waktu()))) set({ shKetik: '' }); },
    bongkar: async ({ merk }) => { const r = WB.wbSusunBongkar(merk, st().bgKetik, st().bgAlasan, waktu(), st().bgYakin); if (r.perluYakin) return set({ bgYakin: true, kabar: r.tolak, kabarAwas: false });
      if (await tulis(r)) set({ bgKetik: '', bgAlasan: '', bgYakin: false }); },
    // putaran 39 (owner 29 Sep a · d): AKTIVASI buku wadah PER WADAH — owner memutuskan, tidak ada "semua sekaligus". Dua ketukan; buku merek asal kurang →
    // ketukan pertama cuma menggambar pita dua tombol ("Catat barang masuk dulu" / "TANDAI UNTUK DICOCOKKAN"), ketukan kedua di pita yang menulis.
    aktifkan: async ({ merk }) => { const W = merk; const r = WB.wbSusunAktifkan(W, waktu(), {});
      if (r.perluTandai) return set({ tandai: { jenis: 'aktifkan', W, kalimat: r.tolak, daftar: r.perluTandai }, akYakin: '', kabar: '' });
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, akYakin: '' });
      if (st().akYakin !== W) { const j = r.jadi; return set({ akYakin: W, tandai: null, kabarAwas: false, kabar: 'Ketuk sekali lagi: buku wadah ' + W + ' lahir, isi ±' + KGs(j.isiKg) + (j.kolam.length ? ' + karung terbuka di belakangnya ' + j.kolam.map((k) => k.merk + ' ±' + KGs(k.kg)).join(', ') : '') + ' pindah dari buku ' + (j.sumber.map((x) => x.merk + ' −' + KGs(x.kg)).join(', ') || 'tidak ada') + ' — modal ikut, laba & neraca tidak berubah' }); }
      set({ akYakin: '' }); await tulis(r); },
    // ketukan kedua pola "tandai": kiriman yang sama dengan opsi { tandai: true } — buku merek dibiarkan minus, bertanda perluCocokkan sampai merek itu dihitung
    tandaiTulis: async () => { const t = st().tandai; if (!t) return;
      const r = t.jenis === 'aktifkan' ? WB.wbSusunAktifkan(t.W, waktu(), { tandai: true }) : L.susunBukaKarung(t.merk, waktu(), t.wadah, t.asal, Object.assign({ tandai: true }, stafKb()));
      if (r.perluTandai) return set({ tandai: Object.assign({}, t, { kalimat: r.tolak, daftar: r.perluTandai }) });   // keadaan bergeser di antara dua ketukan — kalimatnya disegarkan, tidak menulis
      const jadi = await tulis(r); if (!jadi) return set({ tandai: null, akYakin: '' });
      if (t.jenis === 'aktifkan') set({ tandai: null, akYakin: '' }); else sesudahBukaKarung(t.merk, t.wadah, r); },
    tandaiBatal: () => set({ tandai: null, akYakin: '' }),
    // "Catat barang masuk dulu" → lembar Barang masuk, nama merek yang kurang sudah terisi di baris pertama (pintu yang sama dengan Menu)
    tandaiMasuk: () => { const t = st().tandai; const m = t && t.daftar && t.daftar[0] ? t.daftar[0].merk : ''; set({ tandai: null, akYakin: '' }); buka('masuk', null, m ? { merk: m } : null); },
    // "Hitung fisik dulu" → Cocokkan › Tumpukan gudang, barang merek itu langsung terbuka (lembar & draf yang sudah ada; tidak memakai ketukan pembalik yang membolak-balik)
    hitungFisik: ({ merk }) => { set({ tandai: null, akYakin: '' }); AKSI.bukaCocok({}); ubahCocok((c) => { c.tab = 'tumpukan'; c.buka = 'tumpukan|' + merk; kosongkanKetik(c); });
      set({ kabar: 'Hitung fisik tumpukan ' + merk + ' di gudang — karung 50 / 25 kg utuh; selisihnya tercatat hari ini, sesudah itu wadahnya bisa diaktifkan', kabarAwas: false }); },
    // putaran 27 (Bagian 5): wadah = TEMPAT bernama; ganti nama → isi, karung di belakangnya & harga liter ikut pindah (buku stok tidak disentuh)
    gnKetik: (v) => set({ gnKetik: String(v).slice(0, 40) }),
    gantiNamaWadah: async ({ merk }) => { const baru = String(st().gnKetik || '').replace(/\s+/g, ' ').trim(); const r = KM.kmSusunGantiNamaWadah(merk, baru, waktu());   // putaran 30: peta kelas ikut di kiriman yang sama
      if (await tulis(r)) set({ gnKetik: '', wadahAktif: baru }); },
    // karung di belakang wadah BERNAMA (owner 21 Sep): namanya dipilih dari karung sumber di gudang; membukanya menurunkan tumpukan gudang nama itu
    krPilihBuka: () => set({ krPilih: !st().krPilih }),
    // putaran 28 (tiga pintu): karung dari tumpukan gudang · baru datang dari pemasok (data-batch) · kemasan jadi hasil adukan (data-uk)
    krNama: ({ merk, asal, batch, uk }) => set({ krNama: merk, krAsal: asal === 'masuk' ? { jenis: 'masuk', batchId: batch } : asal === 'adukan' ? { jenis: 'adukan', namaProduk: merk, ukuran: Number(uk) || 0 } : null, krPilih: false }),
    lainPilihBuka: () => set({ lainPilih: !st().lainPilih }),
    // putaran 39: di belakang wadah AKTIF buka karung = pindah buku merek → karung belakang; buku merek kurang → r.perluTandai → pita dua tombol (ketukan kedua = tandaiTulis)
    bukaKarung: async ({ merk, wadah }, el) => { if (el) sekali(el.closest('.kartu'), 'pegas', 520); const asal = st().krNama === merk ? st().krAsal : null; const r = L.susunBukaKarung(merk, waktu(), wadah || '', asal, stafKb());
      if (r.perluTandai) return set({ tandai: { jenis: 'bukaKarung', merk, wadah: wadah || '', asal, kalimat: r.tolak, daftar: r.perluTandai }, kabar: '' });
      if (await tulis(r)) sesudahBukaKarung(merk, wadah, r); },
    krKetik: (v) => set({ krKetik: String(v).slice(0, 6) }),
    // ---- PUTARAN 22: deretan karung terbuka bisa dipilih, disamakan, dikembalikan ke tumpukan
    drPilih: ({ merk, lokasi }) => { const d = st().drPilih; const sama = d && d.merk === merk && d.lokasi === (lokasi || ''); set({ drPilih: sama ? null : { merk, lokasi: lokasi || '' }, drYakin: false, krKetik: '', kabar: '' }); },
    // putaran 39c: slot kosong dipilih (cuma keterangan + pintu ke wadahnya); karung habis dihapus dari deretan (dua ketukan bila bukunya masih bersisa → susut)
    drKosong: ({ wadah }) => { const d = st().drPilih; const sama = d && !d.merk && d.lokasi === wadah; set({ drPilih: sama ? null : { merk: '', lokasi: wadah }, drYakin: false, krKetik: '', kabar: '' }); },
    drHapus: async ({ merk, lokasi }) => { const d = st().drPilih; const yakin = st().drYakin && !!d && d.merk === merk && d.lokasi === (lokasi || ''); const r = L.susunHapusKarungHabis(merk, lokasi || '', waktu(), yakin, stafKb()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, drYakin: !!r.perluYakin, drPilih: r.perluYakin ? { merk, lokasi: lokasi || '' } : d });
      if (await tulis(r)) set({ drYakin: false, isiW: null }); },
    drKembalikan: async ({ merk, lokasi }) => { const d = st().drPilih; const yakin = st().drYakin && !!d && d.merk === merk && d.lokasi === (lokasi || ''); const r = L.susunKembalikanKarung(merk, lokasi || '', waktu(), yakin, stafKb()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: !!r.perluYakin, drYakin: !!r.perluYakin, drPilih: r.perluYakin ? { merk, lokasi: lokasi || '' } : d });
      if (await tulis(r)) set({ drYakin: false, isiW: null }); },
    tpTab: ({ t }) => set({ tpTab: t }),
    tpGeser: async ({ kunci, arah }) => { await tulis(TP.susunGeserTumpukan(kunci, Number(arah), waktu())); },
    tpTempatBaru: async ({ posisi }) => { const r = TP.susunTempatBaru(posisi, waktu()); if (!(await tulis(r))) return; const p = st().tp.pilih; if (p) await tulis(TP.susunPindah(p, r.nama, waktu())); },
    samakanKarung: async ({ merk, wadah }) => { if (await tulis(L.susunSamakanKarung(merk, st().krKetik, waktu(), wadah || '', stafKb()))) set({ krKetik: '', krNama: '', krAsal: null, krPilih: false, isiW: null }); },
    bukaAtur: () => set({ atur: st().atur ? null : drafAtur(), wadahAktif: null }),
    aturPenuh: (v) => ubahAtur((d) => { d.penuh = String(v).slice(0, 6); }), aturPuncak: (v) => ubahAtur((d) => { d.puncak = String(v).slice(0, 6); }),
    aturUlang: (v) => ubahAtur((d) => { d.ulang = String(v).slice(0, 6); }), aturTakar: (v) => ubahAtur((d) => { d.takar = String(v).slice(0, 6); }),
    aturKgl: (v, el) => ubahAtur((d) => { d.kgl = d.kgl || { bawaan: '', merek: {} }; const m = el && el.dataset ? el.dataset.merk : ''; if (m) d.kgl.merek[m] = String(v).slice(0, 6); else d.kgl.bawaan = String(v).slice(0, 6); }),   // owner 17 Nov (butir 5): berat 1 liter
    aturSusut: (v) => ubahAtur((d) => { d.susut = String(v).slice(0, 6); }),
    aturSisih: (v) => ubahAtur((d) => { d.sisih = String(v).slice(0, 6); }),
    aturMerekKarung: ({ merk }) => ubahAtur((d) => { const m = d.merekKarung || L.aturWadah().merekKarung.slice(); const i = m.indexOf(merk); if (i >= 0) m.splice(i, 1); else m.push(merk); d.merekKarung = m; }),
    aturGeser: ({ i, arah }) => ubahAtur((d) => { d.daftar = L.geserWadah(d.daftar, Number(i), Number(arah)); d.pilih = null; }),
    aturPilih: ({ i }) => ubahAtur((d) => { d.pilih = d.pilih === Number(i) ? null : Number(i); d.resepUntuk = null; }),
    aturGanti: ({ i, merk }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.gantiBerasWadah(d.daftar, Number(i), merk); if (lama && lama !== merk) delete d.resep[lama]; d.pilih = null; }),
    aturLepas: ({ i }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.lepasWadah(d.daftar, Number(i)); delete d.resep[lama]; d.pilih = null; }),
    aturTambah: () => ubahAtur((d) => { d.pilih = d.daftar.length; d.resepUntuk = null; }),
    aturResep: ({ merk }) => ubahAtur((d) => { d.resepUntuk = d.resepUntuk === merk ? null : merk; d.pilih = null; if (!d.resep[merk]) d.resep[merk] = L.resepWadah(merk); }),
    aturResepTakar: ({ merk, j, arah }) => ubahAtur((d) => { const r = d.resep[merk]; if (!r || !r[Number(j)]) return; r[Number(j)].takar = Math.max(0, r[Number(j)].takar + Number(arah)); }),
    aturResepTambah: ({ merk, bahan }) => ubahAtur((d) => { const r = d.resep[merk] || (d.resep[merk] = L.resepWadah(merk)); if (r.length < L.WADAH_MAKS_RESEP && !r.some((x) => x.merk === bahan)) r.push({ merk: bahan, takar: 1 }); }),
    simpanAtur: async () => { const d = st().atur; if (!d) return; const r = L.susunAturWadah({ penuhKg: d.penuh, puncakKg: d.puncak, isiUlangKg: d.ulang, takarKg: d.takar, susutWajarKg: d.susut, sisihKg: d.sisih, kgPerLiter: d.kgl, merekKarung: d.merekKarung || L.aturWadah().merekKarung, daftar: d.daftar, resep: d.resep }, waktu()); if (await tulis(r)) set({ atur: null }); },
    // ---- BARANG MASUK (ST1): draf di keadaan layar + localStorage; ditulis saat SIMPAN
    bukaMasuk: () => set({ lembar: 'masuk', masuk: bacaLokal(KUNCI_DRAF_MASUK) || drafKosongMasuk(), yakinM: false, yakinHapus: false, kabar: '', aturC: null, tbm: null }),
    tutupLembar: () => set({ lembar: null, kabar: '', aturC: null, yakinM: false, yakinHapus: false, yakinHapusA: false, bukaA: null, tbm: null }),
    mKetik: (v, el) => ubahMasuk((d) => { const k = el.dataset.kolom; const i = el.dataset.i; if (i !== undefined) d.baris[Number(i)][k] = String(v).slice(0, k === 'merk' || k === 'namaMutu' ? 40 : k === 'alasanTolak' ? 160 : 12); else { d[k] = String(v).slice(0, k === 'alasan' || k === 'pemasok' ? 60 : k === 'alasanPotong' ? 160 : k === 'catatanBebas' ? C.CP_MAKS.bebas : 12); if (k === 'pemasok') d.pakaiPotong = ''; } }),
    mPilih: ({ kolom, i, nilai }) => ubahMasuk((d) => { if (i !== undefined) { const r = d.baris[Number(i)]; r[kolom] = kolom === 'beratKarung' ? Number(nilai) : nilai;
      // kemasan jadi (dijual per kemasan): tidak dipotong per kg & tidak ditolak dari baris ini — isian itu dikosongkan saat barisnya dijadikan kemasan
      if (kolom === 'masuk' && nilai === 'kemasan') { r.kgPotong = ''; r.ditolak = ''; r.alasanTolak = ''; } } else { d[kolom] = nilai; if (kolom === 'pemasok') d.pakaiPotong = ''; } }),   // ganti pemasok = centang "pakai potongan" dilepas (potongan milik pemasok lain tidak ikut terpakai)
    mTambahBaris: () => ubahMasuk((d) => { d.baris.push(C.barisMasukKosong()); }),
    // Tahap 3 (owner 26 Nov 2026): klaim LANGSUNG saat datang — selisih timbang baris itu dipakai sebagai kg yang dipotong; isi karung bebas (daftar owner)
    mPotongTimbang: ({ i, kg }) => ubahMasuk((d) => { d.baris[Number(i)].kgPotong = String(kg).replace('.', ','); }),
    ukBuka: () => set({ ukBuka: !st().ukBuka, ukKetik: '', kabar: '' }),
    // paket P4 (owner 27 Nov 2026, A25): tarif bongkar kuli per karung (sama untuk semua kuli; 50 & 25 kg boleh beda) — owner saja menulis, berlaku sejak tanggalnya
    tbBuka: () => set({ tbBuka: !st().tbBuka, tbKetik: {}, tbMulai: '', kabar: '' }),
    tbKetik: (v, el) => { const k = Object.assign({}, st().tbKetik || {}); k[el.dataset.berat] = String(v).replace(/[^\d]/g, '').slice(0, 6); set({ tbKetik: k }); },
    tbMulai: (v) => set({ tbMulai: String(v).slice(0, 10) }),
    tbSimpan: async () => { const x = st(); const baris = Object.keys(x.tbKetik || {}).map((b) => ({ berat: Number(b), rp: x.tbKetik[b] })); await tulis(PB.pbSusunTarif({ mulai: x.tbMulai, baris }, waktu())); },
    ukKetik: (v) => set({ ukKetik: String(v).slice(0, 6) }),
    ukTambah: async () => { await tulis(C.susunTambahUkuran(st().ukKetik, waktu())); },
    ukHapus: async ({ n }) => { await tulis(C.susunHapusUkuran(n, waktu())); },
    // paket Barang masuk & mutu, Tahap 1 (owner 26 Nov 2026): catatan untuk pemasok + klaim pada kedatangan yang sedang dibuka; ambang mutu per kelas
    cpBuka: ({ id }) => set({ cpDraf: st().cpDraf && String(st().cpDraf.id) === String(id) ? null : C.cpDraf(id), kabar: '' }),
    cpKetik: (v, el) => { const d = JSON.parse(JSON.stringify(st().cpDraf || {})); if (!d.baris) return; const k = el.dataset.kolom, i = el.dataset.i; if (i !== undefined) d.baris[Number(i)][k] = String(v).slice(0, k === 'ket' ? C.CP_MAKS.ket + 20 : k === 'merk' ? 60 : 12); else d[k] = String(v).slice(0, k === 'catatan' ? C.CP_MAKS.ket + 20 : k === 'bebas' ? C.CP_MAKS.bebas + 20 : 14); d.dariUsul = false; set({ cpDraf: d }); },
    cpPilih: ({ kolom, i, nilai }) => { const d = JSON.parse(JSON.stringify(st().cpDraf || {})); if (!d.baris) return; if (i !== undefined) d.baris[Number(i)][kolom] = nilai; else d[kolom] = d[kolom] === nilai && kolom === 'cara' ? '' : nilai; set({ cpDraf: d }); },
    cpTambah: () => { const d = JSON.parse(JSON.stringify(st().cpDraf || {})); if (!d.baris) return; d.baris.push(C.cpBarisKosong()); set({ cpDraf: d }); },
    cpBuang: ({ i }) => { const d = JSON.parse(JSON.stringify(st().cpDraf || {})); if (!d.baris) return; d.baris.splice(Number(i), 1); set({ cpDraf: d }); },
    cpSimpan: async () => { const d = st().cpDraf; if (!d) return; await tulis(denganUsulSelesai(C.susunCatatanPemasok(d.id, d, waktu()), d.usulId, 'Catatan untuk pemasok sudah disimpan owner')); },
    cpSurat: ({ id }) => { if (opsi.keTujuan) opsi.keTujuan({ ke: 'laporan', keluarga: 'dokumen', jenis: 'pemasok', pilih: String(id) }); else set({ kabar: 'Suratnya dibuat di Laporan › Dokumen › Dokumen kecil › Catatan untuk pemasok', kabarAwas: false }); },
    // Tahap 2 (owner 26 Nov 2026): bukukan klaim "bon dipotong" (dua ketukan) & retur ke pemasok — keduanya lewat jalur koreksi kedatangan di logika
    ptKlaim: async ({ id }) => { if (st().ptYakin !== String(id)) return set({ ptYakin: String(id), kabar: '' }); if (await tulis(C.susunPotongKlaim(id, waktu(), st().ptTempat))) set({ masuk: C.drafDariKedatangan(id), ptYakin: null, ptTempat: null }); },
    // owner 26 Nov 2026: uang kembali pembelian tunai bisa ke laci ATAU rekening
    ptTempat: ({ t }) => set({ ptTempat: t, ptYakin: null, kabar: '' }),
    // Tahap 6: pembetulan kedatangan lama jadi kg timbang — dua ketukan (pratinjau angkanya sudah di kartu)
    btTimbang: async ({ id }) => { if (st().btYakin !== String(id)) return set({ btYakin: String(id), kabar: '' }); if (await tulis(C.susunBetulTimbang(id, '', waktu(), true))) set({ btYakin: null, masuk: st().masuk && st().masuk.id && String(st().masuk.id) === String(id) ? C.drafDariKedatangan(id) : st().masuk }); },
    // potongan yang menunggu pembelian berikutnya ternyata dibayar pemasok dengan uang → dua ketukan, masuk laci / rekening
    ptTerima: async ({ id, i, t }) => { const k = id + '|' + i + '|' + t; if (st().ptTerima !== k) return set({ ptTerima: k, kabar: '' }); if (await tulis(C.susunTerimaPotongan(id, Number(i), t, waktu()))) set({ masuk: C.drafDariKedatangan(id), ptTerima: null }); },
    rtTempat: ({ t }) => set({ rtDraf: Object.assign({}, st().rtDraf || {}, { tempat: t, yakin: false }) }),
    rtBuka: ({ id }) => set({ rtDraf: st().rtDraf && String(st().rtDraf.id) === String(id) ? null : { id: String(id), merk: '', kg: '', alasan: '', yakin: false }, kabar: '' }),
    rtKetik: (v, el) => { const d = Object.assign({}, st().rtDraf || {}); d[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'alasan' ? 160 : 12); d.yakin = false; set({ rtDraf: d }); },
    rtPilih: ({ merk }) => set({ rtDraf: Object.assign({}, st().rtDraf || {}, { merk, yakin: false }) }),
    rtSimpan: async () => { const d = st().rtDraf; if (!d) return; const H = C.hitungReturPemasok(d.id, d); if (H.tolak) return set({ kabar: H.tolak, kabarAwas: true }); if (!d.yakin) return set({ rtDraf: Object.assign({}, d, { yakin: true }), kabar: '' });
      if (await tulis(denganUsulSelesai(C.susunReturPemasok(d.id, d, waktu()), d.usulId, 'Sudah dikembalikan ke pemasok di buku'))) set({ masuk: C.drafDariKedatangan(d.id), rtDraf: null }); },
    // ---- Tahap 5 (owner 26 Nov 2026: "semua tentang barang masuk adakan di tablet") ----
    // tablet · catatan untuk pemasok & klaim SAAT mencatat (baris di draf Barang masuk)
    mcKetik: (v, el) => ubahMasuk((d) => { const r = (d.catatan || [])[Number(el.dataset.i)]; const k = el.dataset.kolom; if (r) r[k] = String(v).slice(0, k === 'ket' ? C.CP_MAKS.ket : k === 'merk' ? 60 : 12); }),
    mcPilih: ({ kolom, i, nilai }) => ubahMasuk((d) => { if (i !== undefined) { const r = (d.catatan || [])[Number(i)]; if (r) r[kolom] = nilai; } else d[kolom] = d[kolom] === nilai ? '' : nilai; }),
    mcTambah: () => ubahMasuk((d) => { d.catatan = (d.catatan || []).concat([C.cpBarisKosong()]); }),
    mcBuang: ({ i }) => ubahMasuk((d) => { (d.catatan || []).splice(Number(i), 1); if (!(d.catatan || []).length) d.klaimCara = ''; }),
    mcTimbang: () => ubahMasuk((d) => { const hm = MT.mtHitung(d, waktu()); const ada = (d.catatan || []).map((r) => r.jenis + '|' + r.merk);
      hm.sah.forEach((b) => { const sel = b.cek ? b.cek.selisihKg : null; const nm = b.merkPemasok || b.merkKetik || b.merk;
        if (sel !== null && sel !== undefined && Math.abs(sel) > 0.004 && ada.indexOf((sel < 0 ? 'kurang' : 'lebih') + '|' + nm) < 0) d.catatan = (d.catatan || []).concat([{ jenis: sel < 0 ? 'kurang' : 'lebih', merk: nm, jumlah: String(Math.abs(sel)).replace('.', ','), satuan: 'kg', ket: b.cek.perkiraan ? 'perkiraan dari timbang sampel' : 'hasil timbang' }]);
        if (b.cek && b.cek.awas.length && ada.indexOf('mutu|' + nm) < 0) d.catatan = (d.catatan || []).concat([{ jenis: 'mutu', merk: nm, jumlah: '', satuan: 'kg', ket: b.cek.awas.join('; ').slice(0, C.CP_MAKS.ket) }]); }); }),
    // tablet · USUL untuk kedatangan yang sudah tersimpan (owner yang memutuskan)
    usBuka: ({ id, jenis }) => set({ usDraf: st().usDraf && String(st().usDraf.id) === String(id) && st().usDraf.jenis === jenis ? null : MT.mtUsulKosong(id, jenis), kabar: '' }),
    usKetik: (v, el) => { const d = JSON.parse(JSON.stringify(st().usDraf || {})); if (!d.id) return; const k = el.dataset.kolom, i = el.dataset.i;
      if (i !== undefined) { if (d.baris[Number(i)]) d.baris[Number(i)][k] = String(v).slice(0, k === 'ket' ? C.CP_MAKS.ket : k === 'merk' ? 60 : 12); } else d[k] = String(v).slice(0, k === 'teks' ? MT.MT_USUL_BATAS.teks : k === 'bebas' ? C.CP_MAKS.bebas : k === 'alasan' ? 160 : 12); set({ usDraf: d }); },
    usPilih: ({ kolom, i, nilai }) => { const d = JSON.parse(JSON.stringify(st().usDraf || {})); if (!d.id) return; if (i !== undefined) { if (d.baris[Number(i)]) d.baris[Number(i)][kolom] = nilai; } else d[kolom] = d[kolom] === nilai && kolom === 'cara' ? '' : nilai; set({ usDraf: d }); },
    usTambah: () => { const d = JSON.parse(JSON.stringify(st().usDraf || {})); if (!d.id) return; d.baris.push(C.cpBarisKosong()); set({ usDraf: d }); },
    usBuang: ({ i }) => { const d = JSON.parse(JSON.stringify(st().usDraf || {})); if (!d.id) return; d.baris.splice(Number(i), 1); set({ usDraf: d }); },
    usKirim: async () => { const d = st().usDraf; if (!d) return; if (await tulis(MT.mtSusunUsul(d, opsi.akun ? opsi.akun() : null, waktu()))) set({ usDraf: null }); },
    // owner · usul dari tablet: catatan / retur mengisi lembarnya (owner memeriksa lalu menyimpan sendiri); yang lain ditandai sudah diperiksa
    usulPakai: ({ id, pid }) => { const x = MT.mtDrafDariUsul(id, pid); if (!x) return set({ kabar: 'Usul itu sudah diperiksa, atau bukan usul yang mengisi lembar', kabarAwas: true }); set(Object.assign({ kabar: 'Lembarnya diisi dari usul tablet — periksa, ubah bila perlu, lalu simpan', kabarAwas: false }, x)); },
    usulSelesai: async ({ pid }) => { await tulis(tpSusunPutus(pid, 'dibaca', {}, waktu())); },
    // owner · usul "potong di kedatangan ini" dari tablet (dua ketukan): bon berkurang sebesar potongan yang menunggu, tanpa uang bergerak
    ppSetuju: async ({ id }) => { if (st().ppYakin !== String(id)) return set({ ppYakin: String(id), kabar: '' }); if (await tulis(C.susunSetujuPakaiPotong(id, waktu()))) set({ masuk: C.drafDariKedatangan(id), ppYakin: null }); },
    ppLepas: async ({ id }) => { if (await tulis(C.susunLepasUsulPakai(id, waktu()))) set({ masuk: C.drafDariKedatangan(id), ppYakin: null }); },
    bukaAturMutu: () => set({ aturMutu: st().aturMutu ? null : C.ckDrafMutuKelas(), kabar: '' }),
    mutuKetik: (v, el) => { const a = JSON.parse(JSON.stringify(st().aturMutu || C.ckDrafMutuKelas())); a[el.dataset.kelas][el.dataset.kolom] = String(v).slice(0, 8); set({ aturMutu: a }); },
    simpanAturMutu: async () => { const a = st().aturMutu; if (!a) return; await tulis(C.susunAturMutuKelas(a, waktu())); },
    // putaran 30: merek baru → kelas mutu (pil); '' = tanpa kelas. Pilihan ikut draf localStorage & ditulis dalam kiriman Simpan barang masuk
    mKelas: ({ i, kelas }) => ubahMasuk((d) => { const b = d.baris[Number(i)]; b.kelas = String(kelas || ''); b.kelasPilih = true; }),
    // audit 39b no. 43: petunjuk satu ketukan — baris yang diketik "TH" diganti ke nama varian yang sudah berbuku ("TH · House"); jawaban kelas/varian lama dibuang
    mPakaiVarian: ({ i, merk }) => ubahMasuk((d) => { const b = d.baris[Number(i)]; if (!b || !merk) return; b.merk = String(merk); b.kelas = ''; b.kelasPilih = false; b.varian = ''; b.namaMutu = ''; }),
    // putaran 27 (Bagian 2): harga beli beda > batas dari modal → owner memilih SAMA barangnya (gabung) atau BEDA MUTU (varian "<nama> · <mutu>")
    mVarian: ({ i, v }) => ubahMasuk((d) => { const b = d.baris[Number(i)]; b.varian = v; if (v !== 'beda') b.namaMutu = ''; }),   // memilih, bukan bolak-balik: ketukan ganda tidak membatalkan jawaban
    vrKetik: (v, el) => { const k = Object.assign({}, st().vrKetik || {}); k[el.dataset.merk] = String(v).slice(0, 12); set({ vrKetik: k, vrYakin: false }); },
    vrTerbit: async ({ merk, usul }) => { const ketik = (st().vrKetik || {})[merk]; const r = VR.vrSusunTerbitHarga(merk, ketik !== undefined && ketik !== '' ? ketik : usul, waktu(), st().vrYakin);
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, vrYakin: !!r.perluYakin });
      const sisa = (st().varianTawar || []).filter((x) => x.merk !== merk); const k = kkSertakanKiriman(r, waktu().kini); if (await tulis(Object.assign({}, k, { patch: Object.assign({}, k.patch, { varianTawar: sisa.length ? sisa : null }) }))) sekali(akar.querySelector('.stok-masuk'), 'pegas', 520); },
    vrNanti: ({ merk }) => { const sisa = (st().varianTawar || []).filter((x) => x.merk !== merk); set({ varianTawar: sisa.length ? sisa : null, kabar: 'Harga ' + merk + ' belum disetel — rak Jual belum menampilkannya sampai harganya terbit (Harga & Pemasok › Katalog).', kabarAwas: false }); },
    mLepasBaris: ({ i }) => ubahMasuk((d) => { if (d.baris.length > 1) d.baris.splice(Number(i), 1); else d.baris[0] = C.barisMasukKosong(); }),
    // paket tanggal janji (owner 27 Nov 2026: "Owner + Penjaga laci dari tablet", rules v24 stafJanjiPemasok): Penjaga laci mengisi / menggeser janji datang
    mtJanjiBuka: ({ id }) => { const x = JN.jnPesananPemasok(id, kini()); set({ janjiP: st().janjiP && st().janjiP.id === String(id) ? null : { id: String(id), tanggal: x && x.janji.akhir ? x.janji.akhir : '' }, kabar: '' }); },
    mtJanjiPilih: ({ t }) => { const j = st().janjiP; if (j) set({ janjiP: Object.assign({}, j, { tanggal: String(t || '') }) }); },
    mtJanjiKetik: (v) => { const j = st().janjiP; if (j) set({ janjiP: Object.assign({}, j, { tanggal: String(v || '') }) }); },
    mtJanjiSimpan: async () => { const j = st().janjiP; if (!j) return; const ak = opsi.akun ? opsi.akun() : null; const tb = tombolAkun(ak, 'kedatangan'); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true });
      await tulis(JN.jnSusunJanjiPemasok(j.id, j.tanggal, waktu(), (ak && ak.nama) || 'Owner')); },
    mBaru: () => { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: drafKosongMasuk(), yakinM: false, yakinHapus: false, kabar: '', tbm: null }); },
    mSimpan: async () => { const d = st().masuk; if (!d) return; const akM = opsi.akun ? opsi.akun() : null;
      // owner 22 Nov 2026 (paket ③): akun tablet = Penjaga laci → kedatangan bon + titipan bongkar & bayar supir + kabar owner (masuk-tablet-logika, rules v15)
      const r = bukanOwner(akM) ? MT.mtSusunSimpan(d, akM, waktu(), st().yakinM) : C.susunSimpanMasuk(d, waktu(), st().yakinM);
      // tinjauan E1: tolakan koreksi membawa jalan lainnya (r.pembalik: 'cocok' → Cocokkan hari ini · 'pindahNama' → pindah buku sisa nama lama ke nama baru)
      if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true, yakinM: !!r.perluYakin, kpPembalik: r.pembalik || null, kpTeks: r.pindahTeks || '', kpYakin: false }); return; }
      // owner 21 Nov 2026: kedatangan yang baru tersimpan langsung menawarkan tanda terimanya (untuk supir pemasok)
      const dm = (r.dokumen || []).find((x) => x.koleksi === 'batchMasuk'); const idT = dm && dm.data ? dm.data.id : null;
      if (await tulis(r)) { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: drafKosongMasuk(), yakinM: false, yakinHapus: false, tbm: idT !== null && idT !== undefined ? { id: String(idT) } : null }); sekali(akar.querySelector('.stok-masuk'), 'pegas', 520); } },
    mKoreksi: ({ id }) => { const d = C.drafDariKedatangan(id); if (!d) return; if (d.fondasi) return set({ kabar: 'Batch fondasi (stok awal / saldo pembuka) menopang seluruh stok & modal — tidak diubah dari sini', kabarAwas: true });
      set({ masuk: d, yakinM: false, yakinHapus: false, tbm: null, kabar: d.adaBal ? 'Kedatangan ini punya baris bal (beli jadi) — baris itu tidak ikut diubah dari sini' : '', kabarAwas: false }); },
    mHapus: async () => { const d = st().masuk; if (!d || !d.id) return; if (!st().yakinHapus) { const r0 = C.susunHapusKedatangan(d.id, d.alasan, waktu()); if (r0.tolak) return set({ kabar: r0.tolak, kabarAwas: true, kpPembalik: r0.pembalik || null }); return set({ yakinHapus: true, kabar: 'Ketuk sekali lagi untuk menghapus kedatangan ini — stok & modal dihitung ulang tanpa kedatangan ini', kabarAwas: true }); }
      const r = C.susunHapusKedatangan(d.id, d.alasan, waktu());
      if (await tulis(r)) { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false }); } },
    // aturan pencatatan (angka kebijakan owner)
    bukaAturC: () => { const a = C.aturCatat(); const t = (n) => String(n).replace('.', ','); set({ aturC: st().aturC ? null : { minKarung: t(a.minKarung), tempoHari: t(a.tempoHari), batasSelisih: t(a.batasSelisih), ambangSusutPositif: String(a.ambangSusutPositif), batasVarian: t(a.batasVarian), kadarAirMaks: t(a.kadarAirMaks), patahMaks: t(a.patahMaks) } }); },   // paket brief 9 Okt: + ambang mutu saat terima
    // putaran 28 (owner 28 Sep): pisahkan buku karung 25 kg merek dua ukuran — hasil hitung karung 25 kg utuh, dua ketukan
    // owner 7 Okt: karung bekas yang DITITIP akun bukan-owner (karung habis saat mereka isi ulang) dicatat owner sekali kirim — dua ketukan
    kbsCatat: async () => { if (!st().kbsYakin) return set({ kbsYakin: true, kabar: 'Ketuk sekali lagi untuk mencatat karung bekas titipan ke bukunya (stok karung bekas & laba bergerak sebesar modal per lembarnya)', kabarAwas: true });
      await tulis(WB.wbSusunKarungBekasTunda(waktu())); set({ kbsYakin: false }); },
    // owner 7 Okt: NILAI KARUNG BEKAS per lembar = angka kebijakan owner (bawaan keputusan 15 Sep) — disimpan DAN diterapkan ke buku mesin (dua ketukan bila rupiah
    // bergerak; neraca naik = laba hari ini naik sebesar selisih nilai rak). Kelahiran karung bekas dinilai harga buku itu.
    kbNilaiKetik: (v) => set({ kbNilai: String(v).slice(0, 9), kbNilaiYakin: false }),
    kbNilaiSimpan: async () => { if (bukanOwner(opsi.akun ? opsi.akun() : null)) return set({ kabar: 'Nilai karung bekas diatur owner', kabarAwas: true });
      const r = WB.wbSusunNilaiKarungBekas(st().kbNilai, waktu(), st().kbNilaiYakin); if (r.perluYakin) return set({ kbNilaiYakin: true, kabar: r.tolak, kabarAwas: true });
      if (await tulis(r)) set({ kbNilaiYakin: false }); },
    // 39b no. 5 · keputusan owner 1 Okt: buku karung belakang yang tertinggal sesudah dikembalikan dengan kode lama — pindah balik (dua ketukan) / timbang dulu
    ttgPindah: async () => { if (!st().ttgYakin) return set({ ttgYakin: true, kabar: 'Ketuk sekali lagi untuk memindah balik sisa pengembalian lama ke mereknya (modal ikut; laba tetap)', kabarAwas: true }); await tulis(WB.wbSusunPindahTertinggal(waktu())); },
    puKetik: (v, el) => { const m = el && el.dataset.merk; if (!m) return; const d = Object.assign({}, st().puKetik || {}); d[m] = String(v).slice(0, 4); set({ puKetik: d, puYakin: '' }); },
    // audit 39b no. 35 (owner 30 Sep): buku per ukuran merek per liter / kelas sendiri digabung balik ke induk — dua ketukan, satu pindah buku
    gabungUkuran: async ({ merk }) => { const r = C.ckSusunGabungUkuran(merk, waktu(), st().guYakin === merk);
      if (r.perluYakin) return set({ guYakin: merk, kabar: r.tolak, kabarAwas: false });
      if (await tulis(r)) set({ guYakin: '' }); },
    pisahUkuran: async ({ merk }) => { const r = C.ckSusunPisahUkuran(merk, (st().puKetik || {})[merk], waktu(), st().puYakin === merk);
      if (r.perluYakin) return set({ puYakin: merk, kabar: r.tolak, kabarAwas: false });
      if (await tulis(r)) { const d = Object.assign({}, st().puKetik || {}); delete d[merk]; set({ puKetik: d, puYakin: '' }); } },
    cKetikAtur: (v, el) => { const a = Object.assign({}, st().aturC || {}); a[el.dataset.kolom] = String(v).slice(0, 12); set({ aturC: a }); },
    // paket KPI laba (butir 12): batas HPP per kg per merek
    hppBuka: () => set({ aturHpp: st().aturHpp ? null : {} }), hppKetik: (v, el) => { const a = Object.assign({}, st().aturHpp || {}); a[el.dataset.merek] = String(v).slice(0, 10); set({ aturHpp: a }); },
    hppSimpan: async () => { const a = st().aturHpp; if (!a) return; const isi = {}; C.ckDaftarHppMaks().forEach((x) => { isi[x.merek] = a[x.merek] !== undefined ? a[x.merek] : x.batas ? String(x.batas) : ''; }); if (await tulis(C.susunAturHppMaks(isi, waktu()))) set({ aturHpp: null }); },
    simpanAturC: async () => { const a = st().aturC; if (!a) return; if (await tulis(C.susunAturCatat(a, waktu()))) set({ aturC: null }); },
    // ---- ADUKAN (ST2-C "Timbangan Adukan"): draf di keadaan layar + localStorage; ditulis saat SIMPAN; buku adukan → rincian, koreksi satu kesatuan, hapus
    bukaAdukan: () => set({ lembar: 'adukan', adukan: bacaLokal(KUNCI_DRAF_ADUKAN) || A.drafAdukanKosong(waktu()), yakinA: {}, yakinHapusA: false, bukaA: null, koreksiA: { total: '', alasan: '' }, kabar: '', aturC: null }),
    aKetik: (v, el) => ubahAdukan((d) => { const kel = el.dataset.kel; const k = el.dataset.kolom; if (kel) d[kel][Number(el.dataset.i)][k] = String(v).slice(0, k === 'merk' || k === 'nama' ? 40 : 12); else d[k] = String(v).slice(0, k === 'alasanOplos' ? 160 : 12); }),
    aPilih: ({ kel, kolom, i, nilai }) => ubahAdukan((d) => { if (!kel) { d[kolom] = nilai; return; } const b = d[kel][Number(i)]; b[kolom] = nilai;
      if (kel === 'hasil' && kolom === 'ukuran') { b.kantongJenis = ''; b.kantongJumlah = ''; }
      if (kel === 'hasil' && kolom === 'kantongJenis') b.kantongJumlah = nilai ? (b.kantongJumlah || b.unit || '') : ''; }),   // pilih kantong → lembarnya = unit (boleh diubah); "tanpa" → kosong
    aTambahKg: ({ i, kg }) => ubahAdukan((d) => { const b = d.bahan[Number(i)]; b.kg = String(Math.round((angka(b.kg) + Number(kg)) * 1000) / 1000).replace('.', ','); }),
    aTambah: ({ kel }) => ubahAdukan((d) => { d[kel].push(kel === 'bahan' ? A.barisBahanKosong() : kel === 'bahanKemasan' ? A.barisBahanKemasanKosong() : A.barisHasilKosong()); }),
    aLepas: ({ kel, i }) => ubahAdukan((d) => { d[kel].splice(Number(i), 1); if (kel !== 'bahanKemasan' && !d[kel].length) d[kel].push(kel === 'bahan' ? A.barisBahanKosong() : A.barisHasilKosong()); }),
    aBaru: () => { simpanLokal(KUNCI_DRAF_ADUKAN, null); set({ adukan: A.drafAdukanKosong(waktu()), yakinA: {}, kabar: '' }); },
    aSimpan: async () => { const d = st().adukan; if (!d) return; const r = A.susunSimpanAdukan(Object.assign({}, d, { batasHasil: batasHasilAdukan(opsi.akun ? opsi.akun() : null) }), waktu(), st().yakinA);
      if (r.tolak) { const y = Object.assign({}, st().yakinA); if (r.perluYakin) y[r.perluYakin] = true; set({ kabar: r.tolak, kabarAwas: true, yakinA: y }); return; }
      if (await tulis(r)) { simpanLokal(KUNCI_DRAF_ADUKAN, null); set({ adukan: A.drafAdukanKosong(waktu()), yakinA: {}, bukaA: String(r.batchId), koreksiA: { total: '', alasan: '' } }); sekali(akar.querySelector('.stok-adukan'), 'pegas', 520);
        const hs = r.hitung; adeganAdukan({ bahanTeks: hs.teksBahan, hasilTeks: hs.teksHasil, ukuran: hs.sahH[0].ukuran, banyak: hs.sahH.reduce((a, x) => a + x.unit, 0) }); } },
    aBuka: ({ batch }) => set({ bukaA: st().bukaA === batch ? null : batch, koreksiA: { total: '', alasan: '' }, yakinHapusA: false, kabar: '' }),
    aKetikKoreksi: (v, el) => { const k = Object.assign({}, st().koreksiA); k[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'alasan' ? 60 : 14); set({ koreksiA: k, yakinHapusA: false }); },
    aKoreksi: async () => { const b = st().bukaA; if (!b) return; if (await tulis(A.susunKoreksiAdukan(b, st().koreksiA.total, st().koreksiA.alasan, waktu()))) set({ koreksiA: { total: '', alasan: '' } }); },
    aHapus: async () => { const b = st().bukaA; if (!b) return; const r = A.susunHapusAdukan(b, st().koreksiA.alasan, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, yakinHapusA: false });
      if (!st().yakinHapusA) return set({ yakinHapusA: true, kabar: 'Ketuk sekali lagi untuk menghapus SELURUH adukan ini — bahan kembali ke stok asal, hasil dicabut dari stok kemasan', kabarAwas: true });
      if (await tulis(Object.assign({ judulBertahap: 'Hapus adukan' }, r))) set({ bukaA: null, yakinHapusA: false, koreksiA: { total: '', alasan: '' } }); },
    // ---- KARANTINA: satu keputusan per barang (layak jual / rework / balik ke pemasok / buang)
    qBuka: ({ id }) => set({ qBuka: st().qBuka === id ? null : id, qAlasan: '', qYakin: '', kabar: '' }),
    qAlasan: (v) => set({ qAlasan: String(v).slice(0, 80), qYakin: '' }),
    qPutus: async ({ id, tindakan }) => { const r = Q.susunPutusKarantina(id, tindakan, st().qAlasan, waktu(), st().qYakin);
      if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true, qYakin: r.perluYakin || '' }); return; }
      if (await tulis(r)) set({ qBuka: null, qAlasan: '', qYakin: '' }); },
    // ---- COCOKKAN (ST3): hitungan keliling gudang di keadaan layar + localStorage; ditulis saat SIMPAN
    bukaCocok: () => set({ lembar: 'cocok', cocok: drafCocok(), yakinC: {}, kabar: '', aturC: null }),
    // putaran 25: tombol pembalik "Bulan X terkunci — cocokkan stok HARI INI": buka Cocokkan langsung di barang catatan asalnya
    // tinjauan E1 (no. 3): koreksi nama yang ditolak karena buku nama lama sudah bergerak → pindah buku sisanya (dua ketukan); kedatangan tidak diubah
    kpPindahNama: async () => { const d = st().masuk; if (!d) return; const r = C.ckSusunPindahKoreksi(d, waktu(), st().kpYakin);
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, kpYakin: !!r.perluYakin, kpPembalik: r.perluYakin ? 'pindahNama' : null });
      if (await tulis(r)) { simpanLokal(KUNCI_DRAF_MASUK, null); set({ masuk: C.drafMasukKosong(waktu()), yakinM: false, yakinHapus: false, kpYakin: false, kpTeks: '' }); } },
    kpCocok: ({ kunci }) => { AKSI.bukaCocok({}); if (kunci) { const kk = String(kunci).replace(/^beras\|/, 'tumpukan|'); const tb = kk.split('|')[0]; if (C.TAB_COCOK.some((x) => x[0] === tb)) AKSI.cTab({ t: tb }); AKSI.cBuka({ kunci: kk }); } set({ kpPembalik: null, kabar: 'Cocokkan HARI INI — hitung fisiknya, selisihnya tercatat hari ini (catatan bulan terkunci tidak disentuh)', kabarAwas: false }); },
    cTab: ({ t }) => ubahCocok((c) => { c.tab = C.tabCocokSah(t); c.buka = null; kosongkanKetik(c); }),
    cBuka: ({ kunci }) => ubahCocok((c) => { c.buka = c.buka === kunci ? null : kunci; kosongkanKetik(c); }),
    cSatuan: ({ s: sat }) => ubahCocok((c) => { c.satuanIsi = sat; }),
    cKetik: (v, el) => ubahCocok((c) => { c[el.dataset.kolom] = String(v).slice(0, 10); }),
    // paket P5 (owner 27 Nov 2026, A70 · A43): siapa menghitung / mendampingi (berlaku untuk hitungan yang disimpan) + hama per tumpukan
    cOrang: (v, el) => ubahCocok((c) => { c[el.dataset.kolom] = String(v).slice(0, C.CC_ORANG_MAKS); }),
    cOrangPilih: ({ kolom, nama }) => ubahCocok((c) => { c[kolom] = c[kolom] === nama ? '' : nama; }),
    cHama: ({ kunci, v }) => ubahCocok((c) => { c.hama = Object.assign({}, c.hama || {}); if (c.hama[kunci] === v) delete c.hama[kunci]; else c.hama[kunci] = v; }),
    cAlasan: (v, el) => ubahCocok((c) => { c.alasan[el.dataset.kunci] = String(v).slice(0, 60); }),
    cPas: ({ kunci, sistem, karung }) => ubahCocok((c) => { if (c.sampel) delete c.sampel[kunci]; if (sistem !== undefined && sistem !== '') c.hitung[kunci] = String(sistem); if (karung !== undefined && karung !== '') c.hitung[kunci.replace(/^wadah\|/, 'wadahKarung|')] = String(karung); if (c.buka === kunci) c.buka = null; }),
    cPakai: ({ kunci, satuan }) => { if (kunci.indexOf('tumpukan|') === 0) { const S0 = C.ccSampel(Object.assign(cocokKosong(), st().cocok || {}), kunci.slice('tumpukan|'.length)); if (S0.masalah) return set({ kabar: S0.masalah, kabarAwas: true }); }
     ubahCocok((c) => {
      const tab = kunci.indexOf('karungKhusus|') === 0 ? 'wadah' : kunci.split('|')[0]; const B = C.barangCocok(tab).find((b) => b.kunci === kunci);
      // timbang sampel (boleh kosong): karung utuh × rata-rata sampel — tanpa sampel = karung × 50 / 25 kg seperti dulu; Tahap 6: buku ikut timbang = berat asli karung terbaru
      if (tab === 'tumpukan') { const S = C.ccSampel(c, kunci.slice('tumpukan|'.length)); c.hitung[kunci] = String(S.kg); c.sampel = Object.assign({}, c.sampel || {}); if (S.ada) c.sampel[kunci] = { karung: S.karung, kgSampel: S.kgSampel, isiKarung: S.isiKarung, rata: S.rata, alamiKg: S.alamiKg }; else delete c.sampel[kunci]; }   // paket Susut A71: bagian alami ikut tersimpan
      else if (tab === 'wadah' && B) { if (B.jenis !== 'karung' && String(c.isi || '').trim()) c.hitung[kunci] = String(isiKeKg(c.isi, c.satuanIsi, B)); if (String(c.kr || '').trim()) c.hitung[B.kunciKarung] = String(angka(c.kr)); }
      else if (satuan !== 'kg') c.hitung[kunci] = String(angka(c.angka));
      c.buka = null; kosongkanKetik(c); }); },
    cHapusHitung: ({ kunci }) => ubahCocok((c) => { delete c.hitung[kunci]; if (c.sampel) delete c.sampel[kunci]; delete c.hitung[kunci.replace(/^wadah\|/, 'wadahKarung|')]; }),
    // putaran 27: cocokkan wadah menemukan isi ulang yang lupa dicatat → catat dulu sebagai takar dari karung di belakangnya, baru dicocokkan
    cLupa: async ({ wadah, merk, n }) => { if (await tulis(L.susunTakarWadah(wadah, [{ merk, takar: Number(n), dari: wadah }], waktu(), keranjangJual()))) set({ kabar: st().kabar + ' — sekarang cocokkan lagi isi wadah ' + wadah + '.' }); },
    cBersih: () => { simpanLokal(KUNCI_DRAF_COCOK, null); set({ cocok: cocokKosong(), yakinC: {}, kabar: 'Hitungan dikosongkan', kabarAwas: false }); },
    cSimpan: async () => { const c = st().cocok; if (!c) return; const r = C.susunSimpanCocok(c.tab, c.hitung, c.alasan, waktu(), st().yakinC, c.sampel, { dihitungOleh: c.dihitungOleh, didampingi: c.didampingi, hama: c.hama });
      if (r.tolak) { const y = Object.assign({}, st().yakinC); if (r.perluYakin) y[r.perluYakin] = true; set({ kabar: r.tolak, kabarAwas: true, yakinC: y }); return; }
      // 39b no. 5: hitungan karung wadah (kunciKarung) ikut dibersihkan dari draf sesudah simpan (dulu tertinggal dan tampil "cocok ✓")
      if (await tulis(r)) { const sisa = Object.assign({}, c.hitung); r.hitung.baris.forEach((b) => { delete sisa[b.kunci]; if (b.kunciKarung) delete sisa[b.kunciKarung]; }); const al = Object.assign({}, c.alasan); const sp = Object.assign({}, c.sampel || {}); const hm = Object.assign({}, c.hama || {}); r.hitung.baris.forEach((b) => { delete al[b.kunci]; delete sp[b.kunci]; delete hm[b.kunci]; });
        const c2 = Object.assign({}, c, { hitung: sisa, alasan: al, sampel: sp, hama: hm, buka: null }); simpanLokal(KUNCI_DRAF_COCOK, Object.keys(sisa).length ? c2 : null); set({ cocok: c2, yakinC: {} }); } },
    // ---- KANTONG (ST4-B+C): rak, nota beli per batch (harga per LEMBAR), buku beli (hapus beralasan), riwayat harga
    bukaKantong: () => set({ lembar: 'kantong', kabar: '', ktYakin: {}, ktHapus: null, ktAlasan: '', ktYakinHapus: false, aturKt: null, kt: Object.assign({ jenis: '', jumlah: '', harga: '', toko: '' }, st().kt, { jenis: st().kt.jenis || ((KT.rakKantong().daftar[0] || {}).jenis || '') }) }),
    ktTab: ({ t }) => set({ ktTab: t }),
    ktJenis: ({ jenis }) => set({ kt: Object.assign({}, st().kt, { jenis }), ktYakin: {}, kabar: '' }),
    ktKetik: (v, el) => { const k = Object.assign({}, st().kt); k[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'toko' ? 60 : 12); set({ kt: k, ktYakin: {} }); },
    ktSimpan: async () => { const r = KT.susunSimpanBeli(st().kt, waktu(), st().ktYakin); if (r.tolak) { const y = Object.assign({}, st().ktYakin); if (r.perluYakin) y[r.perluYakin] = true; return set({ kabar: r.tolak, kabarAwas: true, ktYakin: y }); } if (await tulis(r)) sekali(akar.querySelector('.stok-kantong'), 'pegas', 520); },
    ktHapusPilih: ({ id }) => set({ ktHapus: st().ktHapus === id ? null : id, ktAlasan: '', ktYakinHapus: false, kabar: '' }),
    ktAlasan: (v) => set({ ktAlasan: String(v).slice(0, 60), ktYakinHapus: false }),
    ktHapus: async () => { const id = st().ktHapus; if (!id) return; const r = KT.susunHapusBeli(id, st().ktAlasan, waktu(), st().ktYakinHapus); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, ktYakinHapus: !!r.perluYakin });
      await tulis(r); },
    bukaAturKt: () => { const a = KT.aturKantong(); set({ aturKt: st().aturKt ? null : { lonjakan: String(a.lonjakan), hariAman: String(a.hariAman), lantaiHarga: String(a.lantaiHarga) } }); },
    ktKetikAtur: (v, el) => { const a = Object.assign({}, st().aturKt || {}); a[el.dataset.kolom] = String(v).slice(0, 8); set({ aturKt: a }); },
    simpanAturKt: async () => { const a = st().aturKt; if (a) await tulis(KT.susunAturKantong(a, waktu())); },
    // owner 11 Okt: pecah kantong gabungan lama jadi buku per merek lewat hitung fisik (stok-kantong-logika susunPecahKantong)
    pkKetik: (v, el) => { const L = el.dataset.l; const isi = Object.assign({}, st().pkIsi); isi[L] = Object.assign({}, isi[L] || {}); isi[L][el.dataset.j] = String(v).slice(0, 7); set({ pkIsi: isi, pkYakin: st().pkYakin === L ? null : st().pkYakin }); },
    pkSimpan: async ({ l }) => { const r = KT.susunPecahKantong(l, (st().pkIsi || {})[l] || {}, waktu(), st().pkYakin === l); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, pkYakin: r.perluYakin ? l : null });
      if (await tulis(r)) { const isi = Object.assign({}, st().pkIsi); delete isi[l]; set({ pkIsi: isi }); } },
    // ---- TEMPAT SIMPAN (ST5-A "Denah Toko"): ketuk barang, lalu ketuk tempat tujuannya; peta = dokumen yang sama dengan sistem lama
    bukaTempat: () => set({ lembar: 'tempat', kabar: '', tp: { pilih: null, tempat: null }, aturTp: null }),
    tpPilih: ({ kunci }) => { const sama = st().tp.pilih === kunci; const brg = TP.barangTempat().find((b) => b.kunci === kunci); set({ tp: Object.assign({}, st().tp, { pilih: sama ? null : kunci }), kabar: sama || !brg ? '' : 'Sekarang ketuk tempat tujuan ' + brg.nama + ' — atau "tanpa tempat"', kabarAwas: false }); },
    tpKetukTempat: async ({ nama }) => { const p = st().tp.pilih; if (!p) return set({ tp: Object.assign({}, st().tp, { tempat: st().tp.tempat === nama ? null : nama }), kabar: '' }); await tulis(TP.susunPindah(p, nama || '', waktu())); },
    bukaAturTp: () => { const a = TP.aturTempat(); set({ aturTp: st().aturTp ? null : { daftar: a.daftar.map((t) => Object.assign({}, t)), batasTumpuk: String(a.batasTumpuk) } }); },
    tpAturNama: (v, el) => ubahAturTp((d) => { d.daftar[Number(el.dataset.i)].nama = String(v).slice(0, 40); }),
    tpAturPosisi: (v, el) => ubahAturTp((d) => { d.daftar[Number(el.dataset.i)].posisi = String(v || ''); }),
    tpAturTambah: () => ubahAturTp((d) => { d.daftar.push({ nama: '', posisi: '' }); }),
    tpAturBawaan: () => ubahAturTp((d) => { const berisi = TP.barangTempat().map((b) => b.tempat).filter(Boolean); const lama = d.daftar.filter((t) => berisi.indexOf(t.nama) >= 0); d.daftar = TP.TEMPAT_BAWAAN.map((t) => Object.assign({}, t)).concat(lama.filter((t) => !TP.TEMPAT_BAWAAN.some((b) => b.nama.toLowerCase() === t.nama.toLowerCase())).map((t) => ({ nama: t.nama, posisi: '' }))); }),
    tpAturLepas: ({ i }) => ubahAturTp((d) => { d.daftar.splice(Number(i), 1); }),
    tpAturBatas: (v) => ubahAturTp((d) => { d.batasTumpuk = String(v).slice(0, 5); }),
    simpanAturTp: async () => { const a = st().aturTp; if (!a) return; const r = TP.susunAturTempat(a, waktu()); if (r.perluYakin) return set({ aturTp: Object.assign({}, a, { yakin: true }), kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    // ---- HPP (ST6-A+B): kartu modal, koreksi harga kedatangan terakhir (satu nama / massal), garis waktu
    // paket P5 (A56): kartu stok per merek — owner (memuat harga beli)
    bukaKartu: ({ kunci }) => set({ lembar: 'kartu', kabar: '', ksKunci: kunci || st().ksKunci || ((SG.sgDaftarKartu()[0] || {}).kunci || ''), ksSemua: false }),
    ksPilih: ({ kunci }) => set({ ksKunci: kunci, ksSemua: false, ksCari: '' }),
    ksHari: ({ n }) => set({ ksHari: n, ksSemua: false }),
    ksRinci: () => set({ ksRinci: !st().ksRinci }),
    ksSemua: () => set({ ksSemua: !st().ksSemua }),
    ksCari: (v) => set({ ksCari: String(v).slice(0, 30) }),
    // paket P5 (B72): Stok › Produksi
    prBulan: ({ bulan }) => set({ prBulan: bulan }),
    // paket P5 (A92): opname kejutan — owner; benih pengundi dibuat di perangkat ini (crypto), staf tidak bisa membaca setelannya
    bukaAturKj: () => { const a = SG.sgKejutanAtur(); set({ aturKj: st().aturKj ? null : { kaliSebulan: String(a.kaliSebulan), nMerek: String(a.nMerek) } }); },
    kjKetik: (v, el) => { const a = Object.assign({}, st().aturKj || {}); a[el.dataset.kolom] = String(v).slice(0, 3); set({ aturKj: a }); },
    simpanAturKj: async ({ mati, ulang }) => { const a = st().aturKj || {}; const acak = (() => { try { const b = new Uint8Array(12); crypto.getRandomValues(b); return Array.from(b, (x) => x.toString(16).padStart(2, '0')).join(''); } catch (e) { return ''; } })();
      await tulis(SG.susunAturKejutan(Object.assign({}, a, { aktif: mati !== '1', benih: acak, undiUlang: ulang === '1' }), waktu())); },
    bukaHpp: () => set({ lembar: 'hpp', kabar: '', hp: Object.assign({ merk: null, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'kartu' }, st().hp, { yakin: false }), aturHp: null }),
    hpTab: ({ t }) => set({ hp: Object.assign({}, st().hp, { tab: t }), kabar: '' }),
    hpPilih: ({ merk }) => set({ hp: Object.assign({}, st().hp, { merk: st().hp.merk === merk ? null : merk, ketik: '', yakin: false }), kabar: '' }),
    hpKetik: (v, el) => { const h = Object.assign({}, st().hp); h[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'alasan' ? 60 : 12); h.yakin = false; set({ hp: h }); },
    hpSimpan: async () => { const h = st().hp; if (!h.merk) return set({ kabar: 'Ketuk nama berasnya dulu', kabarAwas: true }); const r = HP.susunKoreksiHpp(h.merk, h.ketik, h.alasan, waktu(), h.yakin);
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, hp: Object.assign({}, h, { yakin: !!r.perluYakin }) }); if (await tulis(r)) sekali(akar.querySelector('.stok-hpp'), 'pegas', 520); },
    hpSiapkan: () => { const h = st().hp; if (!h.merk) return set({ kabar: 'Ketuk nama berasnya dulu', kabarAwas: true }); if (!String(h.ketik).trim()) return set({ kabar: 'Ketik harga beli per kg yang baru', kabarAwas: true }); const m = Object.assign({}, h.massal); m[h.merk] = h.ketik; set({ hp: Object.assign({}, h, { massal: m, ketik: '' }), kabar: h.merk + ' disiapkan — belum tersimpan sampai "terapkan sekaligus"', kabarAwas: false }); },
    hpBuang: ({ merk }) => { const m = Object.assign({}, st().hp.massal); delete m[merk]; set({ hp: Object.assign({}, st().hp, { massal: m }), kabar: '' }); },
    hpMassal: async () => { const h = st().hp; const r = HP.susunKoreksiMassal(h.massal, h.alasan, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); if (await tulis(r)) sekali(akar.querySelector('.stok-hpp'), 'pegas', 520); },
    bukaAturHp: () => { const a = HP.aturHpp(); set({ aturHp: st().aturHp ? null : { batasLonjak: String(a.batasLonjak), lantaiHpp: String(a.lantaiHpp) } }); },
    hpKetikAtur: (v, el) => { const a = Object.assign({}, st().aturHp || {}); a[el.dataset.kolom] = String(v).slice(0, 10); set({ aturHp: a }); },
    simpanAturHp: async () => { const a = st().aturHp; if (a) await tulis(HP.susunAturHpp(a, waktu())); },
    // modal FIFO (owner 9 Okt 2026, "saklar di lu"): pilih hari mulai (besok / 1 Jan), dua ketukan; sudah berjalan → hanya bisa dimatikan
    fifoPilih: ({ tanggal }) => set({ fifo: { pilih: (st().fifo || {}).pilih === tanggal ? '' : tanggal, yakin: '' }, kabar: '' }),
    fifoSimpan: async ({ mode }) => { const f = st().fifo || {}; const r = HP.susunSaklarFifo(mode, f.pilih || '', waktu(), f.yakin === mode);
      if (r.tolak) return set({ kabar: r.tolak, kabarAwas: !r.perluYakin, fifo: Object.assign({}, f, { yakin: r.perluYakin || '' }) });
      if (await tulis(r)) set({ fifo: { pilih: '', yakin: '' } }); },
    // ---- UMUR & PUTARAN (paket brief 9 Okt, butir 2): kartu pertanyaan, rincian buku yang diketuk, Atur ambang (aturanToko/stokUmur)
    umTanya: ({ id }) => set({ umTanya: id, umPilih: null }),
    umPilih: ({ kunci }) => set({ umPilih: st().umPilih === kunci ? null : kunci }),
    bukaAturUm: () => { const a = S.umAtur(); set({ aturUm: st().aturUm ? null : { ambangUmurHari: String(a.ambangUmurHari), ambangHariStok: String(a.ambangHariStok), periodeHari: String(a.periodeHari), targetHariMin: String(a.targetHariMin), targetHariMaks: String(a.targetHariMaks), umurTuaHari: String(a.umurTuaHari), batasSimpanHari: String(a.batasSimpanHari) } }); },
    umKetikAtur: (v, el) => { const a = Object.assign({}, st().aturUm || {}); a[el.dataset.kolom] = String(v).slice(0, 4); set({ aturUm: a }); },
    simpanAturUm: async () => { const a = st().aturUm; if (a) await tulis(S.susunAturUmur(a, waktu())); },
  }, aksiPanelWadah({ set, st, tulis, keranjang: keranjangJual, waktu,
    sesudahCatat: (wadah, r) => { const hsl = r.hitung; adeganIsiUlang({ nama: wadah, keterangan: hsl.takar + ' takar · ' + DESIMAL(hsl.kg) + ' kg' + (hsl.banding ? ' · campur ' + hsl.banding : ''), serokan: Math.ceil(hsl.takar / 8), dari: hsl.wadah, ke: L.tinggiWadah(wadah, keranjangJual()) || hsl.wadah }); } }),
  aksiPanelTerima({ set, akun: opsi.akun, waktu }));
  // owner 26 Nov 2026 (stok minus, label & kepatuhan): cetak label sesudah adukan / Barang masuk + Tugas gudang
  Object.assign(AKSI, aksiPanelStokMinimum({ set, st, tulis, waktu }));
  Object.assign(AKSI, aksiPanelLabel({ set, st, waktu, tulisDokumen }), {
    // Tugas gudang: baris membuka layar yang menyelesaikannya (bentuk tujuan baris Menu); bulan hilang & rusak ini / lalu
    gdKe: ({ i, dari }) => { const T = dari === 'minus' ? GD.gdMinus(kini()).daftar[Number(i)] : GD.gdTugas(kini(), waktu()).daftar[Number(i)]; if (!T || !T.tujuan) return;
      if (T.tujuan.ke === 'stok') { if (T.tujuan.lembar) set({ lembar: T.tujuan.lembar, kabar: '' }); else if (T.tujuan.tab) set({ tab: T.tujuan.tab, lembar: null, kabar: '' }); return; }
      if (opsi.keTujuan) opsi.keTujuan(T.tujuan); },
    gdBulan: ({ b }) => set({ gdBulan: b === 'lalu' ? 'lalu' : 'ini' }),
    gdSemua: () => set({ gdSemua: !st().gdSemua }),
  });
  Object.assign(AKSI, aksiPanelFotoNota({ set, st, akun: opsi.akun, waktu, foto: opsi.foto || null, akar }));   // paket P8: foto nota kedatangan (owner + tablet Penjaga laci)
  delegasi(akar, AKSI);

  const angka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0; const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
  const cocokKosong = () => ({ tab: 'tumpukan', hitung: {}, alasan: {}, sampel: {}, buka: null, karung: '', karung25: '', kg: '', sampelKarung: '', sampelKg: '', angka: '', isi: '', satuanIsi: 'takar', kr: '' });
  // draf hitungan lama (tab 'beras' = satu angka untuk tumpukan + karung terbuka + wadah) dibuka di tab tumpukan; angkanya tidak dipakai (putaran 27)
  const drafCocok = () => { const c = bacaLokal(KUNCI_DRAF_COCOK); return c ? Object.assign(cocokKosong(), c, { tab: C.tabCocokSah(c.tab) }) : cocokKosong(); };
  // Tahap 5: kiriman owner yang mengerjakan USUL dari tablet ikut menandai kabarnya "sudah diperiksa" (satu kiriman; kabar yang sudah diputus dilewati)
  const denganUsulSelesai = (r, pid, balasan) => { if (!r || r.tolak || !pid) return r; const p = tpSusunPutus(pid, 'dibaca', { balasan }, waktu()); return p.tolak ? r : Object.assign({}, r, { dokumen: (r.dokumen || []).concat(p.dokumen) }); };
  const ubahMasuk = (f) => { const d = JSON.parse(JSON.stringify(st().masuk || drafKosongMasuk())); f(d); simpanLokal(KUNCI_DRAF_MASUK, d); set({ masuk: d, yakinM: false, yakinHapus: false }); };
  // putaran 27: isi wadah boleh diketik dalam takar (× isi satu takar aturan wadah), liter (× rasio), atau kg
  const isiKeKg = (v, sat, B) => Math.round(angka(v) * (sat === 'takar' ? B.takarKg : sat === 'liter' ? B.rasio : 1) * 100) / 100;
  const kosongkanKetik = (c) => { c.karung = ''; c.karung25 = ''; c.kg = ''; c.sampelKarung = ''; c.sampelKg = ''; c.angka = ''; c.isi = ''; c.kr = ''; };
  const ubahCocok = (f) => { const c = JSON.parse(JSON.stringify(st().cocok || cocokKosong())); f(c); simpanLokal(KUNCI_DRAF_COCOK, c); set({ cocok: c, yakinC: {} }); };
  const ubahAdukan = (f) => { const d = JSON.parse(JSON.stringify(st().adukan || A.drafAdukanKosong(waktu()))); f(d); simpanLokal(KUNCI_DRAF_ADUKAN, d); set({ adukan: d, yakinA: {} }); };
  const ubahAturTp = (f) => { const a = TP.aturTempat(); const d = JSON.parse(JSON.stringify(st().aturTp || { daftar: a.daftar, batasTumpuk: String(a.batasTumpuk) })); f(d); d.yakin = false; set({ aturTp: d }); };
  function gambar() {
    if (!tampil || terkunci()) { _kotor = true; return; } _kotor = false; _kunciLuar = kunciLuar();
    const s = st(); const sumber = sumberData(); const k = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Stok</div><div class="ket">${tanggalPendek(L.waktuSekarang(k).tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">${opsi.lonceng ? mentah(opsi.lonceng()) : ''}<div class="pil pil-akun ${sumber.jenis === 'firestore' ? '' : 'kedip'}" data-pil-akun title="Akun yang masuk · ketuk untuk Keluar">${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      ${s.kabar && s.kpPembalik === 'cocok' ? h`<div class="kaca-btn putus" data-k="kabar-pembalik" data-aksi="kpCocok" data-kunci="" style="align-self: flex-start;">Buat Cocokkan hari ini</div>` : ''}
      ${s.kabar && s.kpPembalik === 'pindahNama' ? h`<div class="kaca-btn ${s.kpYakin ? 'awas' : 'aktif emas'}" data-k="kabar-pindah" data-aksi="kpPindahNama" style="align-self: flex-start;">${s.kpYakin ? 'YAKIN — ' : ''}${s.kpTeks || 'Pindah buku sisanya'}</div>` : ''}
      ${s.lembar === 'masuk' ? gambarMasuk(s) : s.lembar === 'cocok' ? gambarCocok(s) : s.lembar === 'adukan' ? gambarAdukan(s) : s.lembar === 'kantong' ? gambarKantong(s) : s.lembar === 'tempat' ? gambarTempat(s) : s.lembar === 'hpp' ? gambarHpp(s) : s.lembar === 'kartu' ? gambarKartuStok(s) : s.lembar === 'stokMin' ? kartuStokMinimum(s) : s.lembar === 'terima' ? lembarTerima(s, { akun: opsi.akun ? opsi.akun() : null, bawah: gambarUsulTablet(s) }) : h`<div class="jalur" data-k="tab">${S.TAB_STOK.map(([id, nm]) => h`<div class="seg ${s.tab === id ? 'aktif' : ''}" data-aksi="tab" data-t="${id}">${nm}</div>`)}</div>
      ${s.tab === 'gudang' ? gambarGudang(s, k) : s.tab === 'wadah' ? gambarTabWadah(s) : s.tab === 'kapur' ? gambarKapur(k) : s.tab === 'umur' ? gambarUmur(s, k) : s.tab === 'tugas' ? gambarTugas(s) : s.tab === 'produksi' ? gambarProduksi(s, k) : gambarKarantina(s)}`}
    `);
    gulirkan(akar, RP);
  }

  function gambarGudang(s, k) {
    const g = S.susunGudang(s.tanya, k); const j = g.jawab;
    // rapi-rapi 29 Sep (kelompok 2): tombol kerja (Barang masuk, Adukan, Cocokkan, …) dulu terkubur di dasar halaman ±2.600 px di Mac. Kini di <aside>
    // tepat sesudah kartu pertanyaan: HP/tablet = urutan tanya → tombol → jawaban → per jenis (stok.css `order`); Mac = kolom kanan yang menempel.
    return h`<section class="stok-gudang" data-k="gudang">
      <div class="tanya">${g.kartu.map((c) => h`<div class="kartu-t ${c.id === g.aktif ? 'aktif' : ''}" data-aksi="tanya" data-id="${c.id}"><div class="q">${c.q}</div>
        <div class="a ${c.awas ? 'awas' : ''}" ${c.angka !== undefined ? mentah('data-gulir="' + Math.round(c.angka) + '"') : ''}>${c.a}</div></div>`)}</div>
      <aside class="stok-samping" data-k="stok-samping">
      ${(() => { const ak = opsi.akun ? opsi.akun() : null; const t = (aksi, nama, tb, kelas) => (tb.boleh ? h`<div class="kaca-btn ${kelas || ''}" data-aksi="${aksi}">${nama}</div>` : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${tb.kalimat}">${nama}</div>`);
        return h`<div class="stok-aksi" data-k="stok-aksi"><div class="tombol-baris">${t('bukaMasuk', 'Barang masuk', tombolAkun(ak, 'kedatangan'), 'aktif')}${t('bukaAdukan', 'Adukan', tombolAkun(ak, 'adukan'), 'aktif')}${t('bukaCocok', 'Cocokkan', tombolLuarKisi(ak), 'aktif')}</div>
      <div class="tombol-baris" data-k="tombol-16">${t('bukaKantong', 'Kantong', tombolLuarKisi(ak))}${t('bukaTempat', 'Tempat simpan', tombolLuarKisi(ak))}${bukanOwner(ak) ? h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="HPP / modal tidak termasuk hak ${ak.nama}">HPP / modal</div>` : h`<div class="kaca-btn" data-aksi="bukaHpp">HPP / modal</div>`}</div>
      ${bukanOwner(ak) ? '' : h`<div class="tombol-baris" data-k="tombol-kartu"><div class="kaca-btn" data-aksi="bukaKartu">Kartu stok</div></div>`}
      ${bukanOwner(ak) ? h`<div class="kaca-btn" data-k="tombol-terima" data-aksi="bukaTerima">Tanda terima barang masuk</div>` : ''}</div>`; })()}
      ${(() => { const JB = jbKelompokStok(); return JB.length ? h`<div class="kartu" data-k="per-jenis" style="gap: 2px;"><div class="label">Beras di buku per jenis</div>
        ${JB.map((x) => h`<div class="jawab" data-k="jn-${x.jenis}"><span class="kiri"><span class="nm">${x.jenis}</span><span class="w">${x.merk.join(' · ')}</span></span><span class="kanan"><span class="n">${DESIMAL(Math.round(x.kg * 10) / 10)} kg</span><span class="w">${x.merk.length} nama</span></span></div>`)}
        <div class="ket" style="font-size: 11px;">Jenis diatur di Harga & Pemasok › Katalog harga › Jenis beras. Salah jenis hanya menggeser kelompok — stok & harga tidak berubah.</div></div>` : ''; })()}
      </aside>
      <div class="kartu jawaban" data-k="jawab-${g.aktif}">
        <div class="label">${g.judul}</div>
        ${j.baris.length ? h`<div class="daftar-jawab">${j.baris.map((b, i) => h`<div class="jawab" data-k="${g.aktif}-${b.kunci}" style="--urut: ${Math.min(i, 16)};">
          <span class="kiri"><span class="nm">${b.nama}</span>${b.karung !== undefined ? h`<span class="tumpuk-mini" data-k="tm-${b.kunci}">${Array.from({ length: Math.min(b.karung, 14) }).map((_, n) => h`<i data-k="tm-${b.kunci}-${n}"></i>`)}${b.karung > 14 ? h`<b>+${b.karung - 14}</b>` : ''}</span>` : ''}<span class="w">${b.ket}</span><span class="batang"><span class="isi-batang ${b.awas ? 'awas' : ''}" style="transform: scaleX(${Math.round(Math.max(0.02, Math.min(1, b.isi)) * 1000) / 1000});"></span></span></span>
          <span class="kanan"><span class="n ${b.awas ? 'awas' : ''}">${b.n}</span><span class="w">${b.nKet}</span></span></div>`)}</div>`
          : h`<div class="menolak" style="padding: 12px 0;">${j.kosong}</div>`}
        <div class="rumus">${j.rumus}</div>
        ${j.takTeks ? h`<div class="ket" style="font-size: 11.5px;">${j.takTeks}</div>` : ''}
        ${g.aktif === 'beli' ? h`<div class="kaca-btn kecil" data-aksi="keBelanja" data-k="ke-belanja" style="align-self: flex-start;">Susun belanja per pemasok & kirim pesanan WhatsApp ›</div>` : ''}
        ${g.aktif === 'beli' && !bukanOwner(opsi.akun ? opsi.akun() : null) ? h`<div class="kaca-btn kecil" data-aksi="smBuka" data-k="ke-stok-minimum" style="align-self: flex-start;">Stok minimum per barang (hari atau kg) ›</div>` : ''}
      </div>
    </section>`;
  }
  const kepalaLembar = (judul, ket) => h`<div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${judul}</div><div class="ket">${ket}</div></div><div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>`;
  // ---------- KANTONG (ST4-B+C) ----------
  function gambarKantong(s) {
    const R = KT.rakKantong(); const PK = KT.daftarPecahKantong(); const kt = s.kt; const J = R.daftar.find((x) => x.jenis === kt.jenis) || null; const hb = KT.hitungBeli(kt); const buku = KT.bukuBeli(20); const H = s.ktHapus ? buku.find((b) => String(b.id) === String(s.ktHapus)) : null;
    const tolak = !J ? 'Pilih jenis kantongnya' : !(hb.jumlah > 0) ? 'Ketik jumlah lembarnya' : !(hb.harga > 0) ? 'Ketik harga SATU lembar' : '';
    return h`<section class="stok-kantong" data-k="kantong">
      ${kepalaLembar('Kantong', 'kantong kosong & paper bag: beli per batch (harga per LEMBAR), rak, buku beli, riwayat harga')}
      <div class="jalur rapat" data-k="kt-tab">${KT.TAB_KANTONG.map(([id, nm]) => h`<div class="seg ${s.ktTab === id ? 'aktif' : ''}" data-aksi="ktTab" data-t="${id}">${nm}</div>`)}</div>
      ${PK.length ? h`<div class="kartu" data-k="kt-pecah" style="gap: 8px; border-color: var(--awas);"><div class="label">Pecah per merek · kantong gabungan lama</div>
        <div class="ket">Buku kantong sekarang per merek. Hitung fisik tiap merek di toko (0 kalau tidak ada), lalu simpan: modal per lembar gabungan disalin ke tiap merek, selisih hitungan dicatat seperti Cocokkan. Sampai dipecah, tumpukan gabungan masih bisa dipakai.</div>
        ${PK.map((g) => { const isi = (s.pkIsi || {})[g.jenis] || {}; const HP = KT.hitungPecah(g.jenis, isi); return h`<div data-k="pk-${g.jenis}" style="display: flex; flex-direction: column; gap: 6px; padding-top: 6px;">
          <div style="font-weight: 600;">${g.label}</div><div class="ket">buku ${DESIMAL(g.sisa)} lembar · modal ${RP(g.modal)}/lembar${g.hargaJual ? ' · dijual ' + RP(g.hargaJual) + '/lembar' : ''}</div>
          <div class="ps-form tiga">${g.merek.map((m) => h`<div><div class="ket">${m.nama} (lembar)</div><input class="ketik-nama" id="pk-${g.jenis}-${m.jenis}" type="text" inputmode="numeric" value="${isi[m.jenis] || ''}" data-ketik="pkKetik" data-l="${g.jenis}" data-j="${m.jenis}" placeholder="hitung"></div>`)}</div>
          <div class="ket ${HP.selisih ? 'awas-teks' : ''}">${HP.teks}</div>
          <div class="utama ${HP.semuaTerisi && !HP.salah.length ? '' : 'redup'}" data-aksi="pkSimpan" data-l="${g.jenis}">${s.pkYakin === g.jenis ? 'YAKIN — simpan hitungan & pecah' : 'SIMPAN HITUNG · pecah jadi per merek'}</div></div>`; })}</div>` : ''}
      ${s.ktTab === 'riwayat' ? h`<div class="kartu" data-k="kt-riwayat" style="gap: 4px;"><div class="label">Riwayat harga per lembar · lonjakan > ${R.atur.lonjakan} % ditandai</div>
        ${KT.riwayatHarga().map((j) => h`<div data-k="rh-${j.jenis}" style="padding-top: 6px;"><div style="font-weight: 600; font-size: 12.5px;">${j.label}</div><div class="ket">${j.ket}</div>
          ${j.baris.map((b) => h`<div class="kt-riw" data-k="rh-${j.jenis}-${b.id}"><span class="ket">${tanggalPendek(b.tanggal)}</span><span class="lonjak">${b.lonjak}${b.murah ? ' · di bawah lantai' : ''}</span><span class="ket">${DESIMAL(b.jumlah)} lbr</span><span class="n ${b.murah ? 'awas' : ''}">${RP(b.harga)}</span></div>`)}</div>`)}
        <div class="ket" style="padding-top: 6px;">Harga terakhir tiap jenis = pembanding beli berikutnya; modal per lembar yang dipakai adukan & wadah dijual = rata-rata buku (mesin yang sama dengan sistem lama).</div></div>`
      : h`<div class="kartu" data-k="kt-rak" style="gap: 6px;"><div class="label">Rak kantong · tinggi = sisa · merah = cukup < ${R.atur.hariAman} hari</div>
        <div class="kt-rak">${R.daftar.map((k) => h`<div class="kt-tumpuk ${k.awas ? 'awas' : ''} ${J && J.jenis === k.jenis ? 'aktif' : ''}" data-k="kt-${k.jenis}" data-aksi="ktJenis" data-jenis="${k.jenis}" title="${k.teksHari}"><div class="n">${DESIMAL(k.sisa)}</div><div class="isi" style="transform: scaleY(${k.tinggi});"></div><div class="nm">${k.nama.replace('Kantong ', '')}<br>${k.ukuran}</div></div>`)}</div>
        <div class="ket ${R.awas.length ? 'awas-teks' : ''}">${R.rakKet}</div></div>`}
      <div class="kartu" data-k="kt-nota" style="gap: 8px;">
        <div style="font-weight: 700;">${J ? J.label : 'pilih jenisnya di rak'}</div>${J ? h`<div class="ket">sisa ${DESIMAL(J.sisa)} lembar · ${J.teksHarga} · ${J.teksHari}</div>` : ''}
        <div class="ps-form tiga"><div><div class="ket">Jumlah (lembar)</div><input class="ketik-nama" id="ktJumlah" type="text" inputmode="numeric" value="${kt.jumlah}" data-ketik="ktKetik" data-kolom="jumlah" placeholder="0"></div>
          <div><div class="ket">Harga SATU lembar (Rp)</div><input class="ketik-nama" id="ktHarga" type="text" inputmode="numeric" value="${kt.harga}" data-ketik="ktKetik" data-kolom="harga" placeholder="0"></div>
          <div><div class="ket">Toko kantong (boleh kosong)</div><input class="ketik-nama" id="ktToko" type="text" value="${kt.toko}" data-ketik="ktKetik" data-kolom="toko" placeholder="nama toko"></div></div>
        ${hb.murah ? h`<div class="pita-info awas">${hb.murahTeks}</div>` : ''}${hb.lonjak ? h`<div class="pita-info awas">${hb.lonjakTeks}</div>` : ''}
        <div class="ket">${hb.teks || 'jumlah × harga per lembar'} · tunai, keluar dari laci hari ini (mesin arus kas menghitung tiap catatan beli)</div>
        <div class="utama ${tolak ? 'redup' : ''}" data-aksi="ktSimpan">${tolak || 'SIMPAN BELI · ' + RP(hb.total) + ' · tunai'}</div></div>
      <div class="kartu" data-k="kt-buku" style="gap: 2px;"><div class="label">Buku beli kantong · ketuk untuk menghapus (beralasan)</div>
        ${buku.length ? buku.map((b) => h`<div class="jawab ${s.ktHapus === String(b.id) || s.ktHapus === b.id ? 'dipilih' : ''}" data-k="kb-${b.id}" data-aksi="ktHapusPilih" data-id="${b.id}"><span class="kiri"><span class="nm">${tanggalPendek(b.tanggal)}${b.jam ? ' ' + b.jam : ''} · ${b.label}</span><span class="w">${DESIMAL(b.jumlah)} × ${RP(b.harga)}${b.toko ? ' · ' + b.toko : ''}${b.lama ? ' · catatan sistem lama (harga = total ÷ jumlah)' : ''}${b.murah ? ' · DI BAWAH LANTAI' : ''}</span></span><span class="kanan"><span class="n ${b.murah ? 'awas' : ''}">${RP(b.total)}</span></span></div>`) : h`<div class="menolak" style="padding: 8px 0;">Belum ada catatan beli kantong.</div>`}
        ${H && tolakKunciTanggal(H.tanggal, '') ? h`<div data-k="kt-hapus" style="display: flex; flex-direction: column; gap: 6px; padding-top: 8px;"><div class="kaca-btn putus" data-aksi="kpCocok" data-kunci="${'kantong|' + H.jenis}">${tolakKunciTanggal(H.tanggal, '').split(' — ')[0]} — cocokkan kantong hari ini</div><div class="ket awas-teks">Catatan beli bulan terkunci tidak bisa dihapus; lembar yang tidak pernah ada dibetulkan lewat Cocokkan HARI INI. Uangnya tidak punya pembetul (K2).</div></div>`
          : H ? h`<div data-k="kt-hapus" style="display: flex; flex-direction: column; gap: 6px; padding-top: 8px;"><input class="ketik-nama sempit" id="ktAlasan" type="text" value="${s.ktAlasan}" data-ketik="ktAlasan" placeholder="Alasan hapus (wajib)"><div class="kaca-btn awas" data-aksi="ktHapus">${s.ktYakinHapus ? 'YAKIN HAPUS batch ini' : 'hapus batch ' + tanggalPendek(H.tanggal) + ' · ' + H.label}</div></div>` : ''}</div>
      ${s.aturKt ? h`<div class="kartu" data-k="atur-kt" style="gap: 8px;"><div class="label">Aturan kantong · angka owner</div><div class="ps-form tiga">
        <div><div class="ket">Batas lonjakan harga (%)</div><input class="ketik-nama" id="akLonjak" type="text" inputmode="numeric" value="${s.aturKt.lonjakan}" data-ketik="ktKetikAtur" data-kolom="lonjakan"></div>
        <div><div class="ket">Stok kantong aman (hari)</div><input class="ketik-nama" id="akHari" type="text" inputmode="numeric" value="${s.aturKt.hariAman}" data-ketik="ktKetikAtur" data-kolom="hariAman"></div>
        <div><div class="ket">Lantai harga per lembar (Rp)</div><input class="ketik-nama" id="akLantai" type="text" inputmode="numeric" value="${s.aturKt.lantaiHarga}" data-ketik="ktKetikAtur" data-kolom="lantaiHarga"></div></div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturKt">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturKt">SIMPAN ATURAN</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturKt" style="align-self: flex-start;">Atur lonjakan, stok aman & lantai harga ${R.atur.dariOwner ? '· diatur owner' : '· bawaan'} ›</div>`}
      <div class="ket" style="font-size: 11px;">Satu batch = jenis · jumlah · harga per lembar (sama dengan sistem lama). Harga di bawah lantai dan lonjakan ditanya dulu — sistem lama pernah menyimpan Rp1/lembar. Batch yang lembarnya sudah terpakai tidak bisa dihapus. Karung bekas tidak dibeli (hasil samping).</div>
    </section>`;
  }
  // ---------- TEMPAT SIMPAN (ST5-A) ----------
  function gambarTempat(s) {
    const T = TP.susunTempat(); const pilih = s.tp.pilih ? T.barang.find((b) => b.kunci === s.tp.pilih) : null; const iso = L.waktuSekarang(kini()).tanggal; const riw = TP.riwayatPindah(iso, 8);
    const zonaKls = (t) => (s.tp.tempat === t.nama ? ' aktif' : '') + (t.tumpuk ? ' tumpuk' : '');
    return h`<section class="stok-tempat" data-k="tempat">
      ${kepalaLembar('Tempat simpan', 'di mana tiap beras & kemasan disimpan · cuma catatan tempat, stok & modal tidak berubah')}
      <div class="ket">${pilih ? pilih.nama + ' dipilih — ketuk tempat tujuannya di denah / daftar, atau "tanpa tempat"' : 'Ketuk barang dulu, lalu ketuk tempatnya'}</div>
      <div class="bendera" data-k="tp-barang">${T.barang.map((b) => h`<span class="pil ${s.tp.pilih === b.kunci ? 'nyala' : ''}" data-k="tb-${b.kunci}" data-aksi="tpPilih" data-kunci="${b.kunci}">${b.nama} · ${b.tempat || 'tanpa tempat'}</span>`)}${T.barang.length ? '' : h`<span class="ket">belum ada barang bersisa</span>`}</div>
      <div class="jalur rapat" data-k="tp-tab"><div class="seg ${s.tpTab !== 'denah' ? 'aktif' : ''}" data-aksi="tpTab" data-t="tiga">Tumpukan 3D</div><div class="seg ${s.tpTab === 'denah' ? 'aktif' : ''}" data-aksi="tpTab" data-t="denah">Denah</div></div>
      ${s.tpTab !== 'denah' ? gambarTumpukan3D(s, pilih) : h`<div class="kartu" data-k="tp-denah-kartu" style="gap: 6px;"><div class="label">Denah toko · ketuk kotaknya${T.kosong ? ' · belum ada tempat, tambahkan lewat Atur' : ''}</div>
        <div class="tp-denah">${T.perabot.map((f) => h`<div class="tp-perabot ${f.id}" data-k="tf-${f.id}" style="left: ${f.x}%; top: ${f.y}%; width: ${f.w}%; height: ${f.h}%;"><span>${f.nama}</span></div>`)}${T.kotakKosong.map((z) => h`<div class="tp-kosong" data-k="tq-${z.posisi}" style="${z.gaya}" title="belum ada tempat di kotak ini — Atur daftar tempat"><span>${z.nama}</span></div>`)}${T.zona.map((t) => h`<div class="tp-zona${zonaKls(t)}" data-k="tz-${t.nama}" style="${t.gaya}" data-aksi="tpKetukTempat" data-nama="${t.nama}"><b>${t.nama}</b><span class="n">${t.teksJumlah}</span><span class="ket">${t.teksIsi}</span><span class="ket">${t.teksNilai}</span></div>`)}</div>
        <div class="ket" style="font-size: 10.5px;">Denah dari foto toko 23 Sep: jalan di bawah, pintu rumah di atas, lorong ubin di tengah, tumpukan karung kiri–kanan (kanan belakang paling tinggi), kotak wadah literan di mulut toko dengan deretan karung terbuka di belakangnya, pajangan kemasan & meja di kanan.</div>
        <div class="bendera">${T.tanpaKotak.map((t) => h`<span class="pil ${s.tp.tempat === t.nama ? 'nyala' : ''} ${t.tumpuk ? 'awas' : ''}" data-k="tk-${t.nama}" data-aksi="tpKetukTempat" data-nama="${t.nama}">${t.nama} · ${t.teksIsi}</span>`)}<span class="pil ${s.tp.tempat === '' ? 'nyala' : ''}" data-k="tk-tanpa" data-aksi="tpKetukTempat" data-nama="">tanpa tempat · ${T.tanpaTempat.n} barang</span></div>
        <div class="ket ${T.tempat.some((t) => t.tumpuk) ? 'awas-teks' : ''}">${T.tumpukKet}</div></div>`}
      <div class="kartu" data-k="tp-daftar" style="gap: 2px;"><div class="label">Isi tiap tempat</div>
        ${T.tempat.map((t) => h`<div data-k="td-${t.nama}"><div class="tp-kepala ${t.tumpuk ? 'tumpuk' : ''}" data-aksi="tpKetukTempat" data-nama="${t.nama}"><b>${t.nama}</b><span class="ket">${t.n ? t.n + ' barang · ' + t.teksJumlah + ' · ' + t.teksNilai : 'kosong'}${t.tumpuk ? ' · MENUMPUK' : ''}</span></div>
          ${t.isi.map((b) => h`<div class="jawab ${s.tp.pilih === b.kunci ? 'dipilih' : ''}" data-k="ti-${b.kunci}" data-aksi="tpPilih" data-kunci="${b.kunci}"><span class="kiri"><span class="nm">${b.nama}</span><span class="w">${b.teksSisa}</span></span><span class="kanan"><span class="n">${RP(Math.round(b.nilai))}</span></span></div>`)}</div>`)}
        <div class="tp-kepala" data-aksi="tpKetukTempat" data-nama=""><b>tanpa tempat</b><span class="ket">${T.tanpaTempat.n} barang · ${T.tanpaTempat.teks}</span></div>
        ${T.tanpaTempat.isi.map((b) => h`<div class="jawab ${s.tp.pilih === b.kunci ? 'dipilih' : ''}" data-k="tt-${b.kunci}" data-aksi="tpPilih" data-kunci="${b.kunci}"><span class="kiri"><span class="nm">${b.nama}</span><span class="w">${b.teksSisa}</span></span><span class="kanan"><span class="n">${RP(Math.round(b.nilai))}</span></span></div>`)}</div>
      ${riw.length ? h`<div class="kartu" data-k="tp-riwayat" style="gap: 2px;"><div class="label">Pindahan hari ini</div>${riw.map((r) => h`<div class="ket" data-k="tr-${r.id}">${r.jam} · ${r.barang}: ${r.dari || 'tanpa tempat'} → ${r.ke || 'tanpa tempat'}</div>`)}</div>` : ''}
      ${s.aturTp ? h`<div class="kartu" data-k="atur-tp" style="gap: 8px;"><div class="label">Daftar tempat · kotak di denah · batas menumpuk</div>
        ${s.aturTp.daftar.map((t, i) => h`<div class="tp-atur-baris" data-k="ta-${i}"><input class="ketik-nama sempit" type="text" value="${t.nama}" data-ketik="tpAturNama" data-i="${i}" placeholder="nama tempat"><select class="ketik-nama sempit" data-ketik="tpAturPosisi" data-i="${i}">${TP.POSISI_DENAH.map(([v, nm]) => h`<option value="${v}" ${t.posisi === v ? mentah('selected') : ''}>${nm}</option>`)}</select><span class="kaca-btn kecil awas" data-aksi="tpAturLepas" data-i="${i}">lepas</span></div>`)}
        <div class="tombol-baris rapat"><div class="kaca-btn kecil" data-aksi="tpAturTambah">+ tempat</div><div class="kaca-btn kecil putus" data-aksi="tpAturBawaan">pakai denah bawaan dari foto toko</div></div>
        <div><div class="ket">Menumpuk di atas (% nilai rak)</div><input class="ketik-nama sempit" id="tpBatas" type="text" inputmode="numeric" value="${s.aturTp.batasTumpuk}" data-ketik="tpAturBatas"></div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturTp">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturTp">SIMPAN DAFTAR TEMPAT</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturTp" style="align-self: flex-start;">Atur daftar tempat, kotak denah & batas menumpuk ${T.atur.dariOwner ? '· diatur owner' : '· bawaan'} ›</div>`}
      <div class="ket" style="font-size: 11px;">Peta tempat = dokumen yang sama dengan sistem lama (tempat boleh kosong, barang boleh tanpa tempat). Tempat yang masih berisi tidak bisa dihapus. Menumpuk = satu tempat memegang nilai rak di atas batas.</div>
    </section>`;
  }
  // ---------- TEMPAT SIMPAN · TUMPUKAN 3D (owner 23 Sep): denah yang sama digambar isometrik, tiap barang = tumpukan karung setinggi stoknya ----------
  function gambarTumpukan3D(s, pilih) {
    const T3 = TP.susunTumpukan(); const P = TP.tpIso; const pk = (x, y, z) => { const q = P(x, y, z); return q.sx + ',' + q.sy; };
    const lantai = (x, y, w, d, z) => pk(x, y, z) + ' ' + pk(x + w, y, z) + ' ' + pk(x + w, y + d, z) + ' ' + pk(x, y + d, z);
    // karung isometrik: lebar 6 (x) · dalam 8 (y) · tinggi 2,3 per lapis; kemasan lebih pipih; digambar dari yang paling jauh (x+y kecil) supaya yang depan menutupi yang belakang
    const semuaStack = []; T3.zona.forEach((z) => z.stacks.forEach((st) => semuaStack.push(Object.assign({ zona: z.nama }, st))));
    semuaStack.sort((a, b) => (a.x + a.y) - (b.x + b.y));
    const kotakKarung = (cx, cy, z0, tinggi, lebar, dalam, kls) => { const x0 = cx - lebar / 2, y0 = cy - dalam / 2; return `<polygon class="sisi-kiri ${kls}" points="${pk(x0, y0 + dalam, z0)} ${pk(x0 + lebar, y0 + dalam, z0)} ${pk(x0 + lebar, y0 + dalam, z0 + tinggi)} ${pk(x0, y0 + dalam, z0 + tinggi)}"/><polygon class="sisi-kanan ${kls}" points="${pk(x0 + lebar, y0, z0)} ${pk(x0 + lebar, y0 + dalam, z0)} ${pk(x0 + lebar, y0 + dalam, z0 + tinggi)} ${pk(x0 + lebar, y0, z0 + tinggi)}"/><polygon class="sisi-atas ${kls}" points="${lantai(x0, y0, lebar, dalam, z0 + tinggi)}"/>`; };
    const tumpukanSvg = (st) => { const kem = st.jenis !== 'karung'; const tinggi = kem ? 1.4 : 2.3; const lebar = kem ? 5 : 6, dalam = kem ? 6 : 8; let g = '';
      if (st.kosong) g += `<polygon class="jejak" points="${lantai(st.x - lebar / 2, st.y - dalam / 2, lebar, dalam, 0.05)}"/>`;
      for (let i = 0; i < st.lapis; i++) g += kotakKarung(st.x, st.y, i * tinggi, tinggi, lebar, dalam, kem ? 'kemasan' : 'karung');
      const puncak = P(st.x, st.y - dalam / 2, st.lapis * tinggi + 1.5); const dipilih = pilih && pilih.kunci === st.kunci;
      return `<g class="tumpukan ${dipilih ? 'dipilih' : ''} ${st.kosong ? 'kosong' : ''}" data-aksi="tpPilih" data-kunci="${esc(st.kunci)}" data-k="t3-${esc(st.kunci)}"><title>${esc(st.nama + ' · ' + st.teks + ' · ' + st.zona)}</title>${g}<text class="nama-tumpukan" x="${puncak.sx}" y="${puncak.sy - 1}" text-anchor="middle">${esc(st.nama.length > 14 ? st.nama.slice(0, 13) + '…' : st.nama)}</text><text class="angka-tumpukan" x="${puncak.sx}" y="${puncak.sy + 3.2}" text-anchor="middle">${esc(st.jenis === 'karung' ? (st.karung + (st.lebih ? '' : '') + ' krg') : Math.round(st.sisa) + ' unit')}</text></g>`; };
    const kosongSvg = TP.kotakBelumDipakai().map((z) => { const c = P(z.x + z.w / 2, z.y + z.d / 2, 0); return `<g class="zona-iso kosong" data-aksi="tpTempatBaru" data-posisi="${esc(z.posisi)}" data-k="zk-${esc(z.posisi)}"><title>${esc('belum jadi tempat — ketuk untuk menjadikannya tempat "' + z.nama + '"' + (pilih ? ' dan menaruh ' + pilih.nama + ' di sana' : ''))}</title><polygon class="lantai-zona" points="${lantai(z.x, z.y, z.w, z.d, 0)}"/><text class="nama-zona" x="${c.sx}" y="${c.sy + 1}" text-anchor="middle">${esc(z.nama.toUpperCase())}</text></g>`; }).join('');
    const zonaSvg = T3.zona.map((z) => { const c = P(z.x + z.w / 2, z.y + z.d / 2, 0); return `<g class="zona-iso ${z.tumpuk ? 'tumpuk' : ''} ${s.tp.tempat === z.nama ? 'aktif' : ''}" data-aksi="tpKetukTempat" data-nama="${esc(z.nama)}" data-k="z3-${esc(z.nama)}"><polygon class="lantai-zona" points="${lantai(z.x, z.y, z.w, z.d, 0)}"/><text class="nama-zona" x="${c.sx}" y="${c.sy + (z.n ? z.d * 0.22 : 1)}" text-anchor="middle">${esc(z.nama.toUpperCase())}${z.n ? '' : ' · kosong'}</text></g>`; }).join('');
    const perabotSvg = T3.perabot.map((f) => `<g class="perabot-iso ${f.id}"><polygon points="${lantai(f.x, f.y, f.w, f.d, 0)}"/>${f.id === 'lorong' || f.id === 'pintu-depan' ? `<text x="${P(f.x + f.w / 2, f.y + f.d / 2, 0).sx}" y="${P(f.x + f.w / 2, f.y + f.d / 2, 0).sy + 1}" text-anchor="middle">${esc(f.nama)}</text>` : ''}</g>`).join('');
    const svg = `<svg class="iso-toko" viewBox="-122 -22 214 152" aria-label="Susunan tumpukan beras di toko (isometrik)"><polygon class="tanah" points="${lantai(0, 0, 100, T3.dalam, 0)}"/>${perabotSvg}${kosongSvg}${zonaSvg}${semuaStack.map(tumpukanSvg).join('')}</svg>`;
    const dip = pilih ? semuaStack.find((st) => st.kunci === pilih.kunci) : null; const zDip = dip ? T3.zona.find((z) => z.nama === dip.zona) : null;
    return h`<div class="kartu" data-k="tp-3d" style="gap: 6px;"><div class="label">Tumpukan beras di toko · tinggi = banyak karung (rantai stok) · ketuk tumpukan, lalu ketuk lantai tempat tujuannya · lantai putus-putus = kotak denah yang belum jadi tempat (ketuk untuk menjadikannya)</div>
      <div class="iso-bungkus" data-k="iso-bungkus">${mentah(svg)}</div>
      ${dip ? h`<div class="dr-aksi" data-k="t3-aksi"><div><b>${dip.nama}</b> · ${dip.teks} · di ${dip.zona}${dip.lebih ? ' · digambar ' + TP.TP_LAPIS_MAKS + ' dari ' + dip.karung + ' karung' : ''}</div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${dip.urut === 0 ? 'mati' : ''}" data-aksi="tpGeser" data-kunci="${dip.kunci}" data-arah="-1">‹ geser ke depan</div><div class="kaca-btn ${zDip && dip.urut >= zDip.stacks.length - 1 ? 'mati' : ''}" data-aksi="tpGeser" data-kunci="${dip.kunci}" data-arah="1">geser ke belakang ›</div><div class="kaca-btn" data-aksi="tpKetukTempat" data-nama="">tanpa tempat</div><div class="kaca-btn" data-aksi="tpPilih" data-kunci="${dip.kunci}">lepas pilihan</div></div>
        <div class="ket" style="font-size: 10.5px;">Ketuk lantai tempat lain untuk memindahkan tumpukan ini ke sana (sesudah kedatangan disusun ulang). Geser = urutan di dalam tempat yang sama. Semuanya cuma catatan letak — stok & modal tidak berubah.</div></div>`
      : h`<div class="ket">${T3.totalKarung} karung di tumpukan menurut buku · ${T3.tanpaTempat.length ? T3.tanpaTempat.length + ' barang belum diberi tempat (pilih dari daftar di atas lalu ketuk lantainya)' : 'semua barang sudah bertempat'} · ${T3.tumpukKet}</div>`}</div>`;
  }
  // ---------- HPP / MODAL (ST6-A+B) ----------
  // putaran 30: harga beli per KELAS mutu — tiap kedatangan anggota satu garis, rata-rata tertimbang per bulan, batas periode data disebut
  function gambarHppKelas() {
    const K = KM.kmKartuKelas();
    return h`<div class="kartu" data-k="hp-kelas" style="gap: 6px;"><div class="label">Harga beli per kelas mutu</div><div class="ket" data-k="hp-kelas-periode">${K.periodeTeks}. Kelas = nama wadah atau nama yang ditandai kelas; merek pemasok yang berganti nama dipetakan ke kelasnya (Harga › Katalog › Kelas mutu).</div>
      ${K.kartu.map((k) => h`<div data-k="hk-${k.kelas}" style="padding-top: 6px;"><div style="font-weight: 700; font-size: 12.5px;">${k.kelas}${k.jenis === 'sendiri' ? ' · kelas tanpa wadah (buku atas nama ini)' : k.jenis === 'merek' ? ' · merek yang dipakai sebagai kelas' : ''}</div><div class="ket">${k.ketAnggota}</div>
        ${k.kosong ? h`<div class="ket">${k.ketKosong}</div>` : h`<div class="jalur bungkus rapat" data-k="hk-bulan-${k.kelas}">${k.perBulan.map((m) => h`<div class="seg" data-k="hb-${k.kelas}-${m.bulan}">${m.bulanTeks} · ${RP(m.rata)}/kg · ${DESIMAL(m.kg)} kg · ${m.n} kedatangan · ${m.teks}</div>`)}</div>
        ${k.baris.map((r, i) => h`<div class="hp-garis" data-k="hk-${k.kelas}-${i}"><span class="ket">${tanggalPendek(r.tanggal)}</span><div><div class="bar ${r.koreksi ? 'koreksi' : ''}" style="transform: scaleX(${r.lebar / 100});"></div><div class="ket" style="font-size: 10px;">${r.merk}${r.merkPemasok ? ' (' + r.merkPemasok + ')' : ''} · ${r.pemasok} · ${DESIMAL(r.kg)} kg</div></div><span class="n">${RP(r.harga)}${r.lonjak ? ' ' + r.lonjak : ''}</span></div>`)}`}</div>`)}
      ${K.tanpaKelas.length ? h`<div class="ket" data-k="hp-kelas-tanpa">${K.tanpaKelas.length} merek tanpa kelas: ${K.tanpaKelas.join(', ')} — petakan di Harga › Katalog › Kelas mutu.</div>` : ''}
      ${K.belumKonfirmasi.length ? h`<div class="ket" data-k="hp-kelas-tebakan">${K.belumKonfirmasi.length} merek kelasnya belum dikonfirmasi owner (tebakan / kosong).</div>` : ''}</div>`;
  }
  /** Kartu saklar modal FIFO (Stok › HPP, owner saja — lembar ini memang owner saja). */
  function gambarFifo(s) {
    const SF = HP.saklarFifo(kini()); const f = s.fifo || {};
    const riw = SF.riwayat.slice(0, 3).map((r) => (r.aksi === 'mati' ? 'dimatikan' : (r.aksi === 'ganti' ? 'diganti ke ' : 'dijadwalkan ') + tanggalPendek(r.mulai)) + ' (' + tanggalPendek(r.tanggal) + ' ' + (r.jam || '') + ')').join(' · ');
    return h`<div class="kartu" data-k="hp-fifo" style="gap: 8px;">
      <div class="label">Cara hitung modal</div>
      <div style="font-weight: 700;">${SF.keadaan === 'mati' ? 'RATA-RATA semua kedatangan' : SF.keadaan === 'rencana' ? 'FIFO mulai ' + tanggalPendek(SF.mulai) : 'FIFO sejak ' + tanggalPendek(SF.mulai)}</div>
      <div class="ket">${SF.teks}</div>
      <div class="ket">FIFO: karung yang paling lama keluar duluan — modal tiap nota = harga kedatangan TERLAMA yang masih ada; nilai rak = kedatangan terbaru. Wadah literan campuran tetap rata-rata. Nota yang sudah tercatat tidak berubah; pajak omzet tidak berubah.</div>
      ${SF.keadaan !== 'nyala' ? h`<div class="jalur rapat" data-k="hp-fifo-pilih">${SF.pilihan.map((p) => h`<div class="seg ${f.pilih === p.tanggal ? 'aktif' : ''}" data-aksi="fifoPilih" data-tanggal="${p.tanggal}">${p.label}</div>`)}</div>` : ''}
      <div class="tombol-baris">${SF.keadaan !== 'nyala' ? h`<div class="utama ${f.pilih ? '' : 'redup'}" data-aksi="fifoSimpan" data-mode="nyala">${f.yakin === 'nyala' ? 'YAKIN, PAKAI FIFO MULAI ' + tanggalPendek(f.pilih) : SF.keadaan === 'rencana' ? 'GANTI HARI MULAI' : 'PAKAI FIFO'}</div>` : ''}${SF.keadaan !== 'mati' ? h`<div class="kaca-btn" data-aksi="fifoSimpan" data-mode="mati">${f.yakin === 'mati' ? 'YAKIN, KEMBALI KE RATA-RATA' : SF.keadaan === 'rencana' ? 'batalkan rencana FIFO' : 'kembali ke rata-rata'}</div>` : ''}</div>
      ${riw ? h`<div class="ket" style="font-size: 11px;">riwayat saklar: ${riw}</div>` : ''}</div>`;
  }
  function gambarHpp(s) {
    const K = HP.kartuHpp(); const hp = s.hp; const M = hp.merk ? K.kartu.find((k) => k.merk === hp.merk) : null; const N = M && String(hp.ketik).trim() ? HP.nilaiKoreksi(M.merk, hp.ketik) : null; const log = HP.logKoreksi(8);
    const PM = HP.pratinjauMassal(hp.massal);
    const koreksi = M ? h`<div class="kartu" data-k="hp-koreksi" style="gap: 8px;"><div style="font-weight: 700;">Koreksi ${M.merk}</div>
      <div class="ket">${M.fifo ? 'modal nota berikutnya ' + RP(Math.round(M.modalKeluar)) + '/kg (FIFO) · nilai rak ' + RP(Math.round(M.modal)) + '/kg (= neraca)' : 'modal rata-rata ' + RP(Math.round(M.modal)) + '/kg (buku, = laba & neraca)'} · harga beli terbaru ${M.hargaTerbaru === null ? 'belum ada' : RP(M.hargaTerbaru) + '/kg'} · ${M.jual ? 'jual ' + RP(M.jual) + '/kg · ' : ''}${M.teksMargin} · sisa ${DESIMAL(Math.round(M.sisa * 10) / 10)} kg</div>
      ${M.fifo ? h`<div class="ket" data-k="hp-lapisan">${M.teksFifo}</div>` : ''}
      ${(() => { const u = S.umKalimat(M.merk, kini()); return u ? h`<div class="ket" data-k="hp-umur">${u} (Stok › Umur & putaran)</div>` : ''; })()}
      ${M.bisaKoreksi ? h`<div class="ket">HPP adalah TURUNAN kedatangan — yang dikoreksi = harga beli per kg pada kedatangan TERAKHIR nama ini (${N && !N.tolak ? N.teksTarget : 'kedatangan terakhir yang bukan fondasi'}).</div>
        <div class="ps-form dua"><div><div class="ket">Harga beli per kg yang benar (Rp)</div><input class="ketik-nama" id="hpKetik" type="text" inputmode="numeric" value="${hp.ketik}" data-ketik="hpKetik" data-kolom="ketik" placeholder="0"></div><div><div class="ket">Alasan (wajib)</div><input class="ketik-nama" id="hpAlasan" type="text" value="${hp.alasan}" data-ketik="hpKetik" data-kolom="alasan" placeholder="mis. bongkar belum masuk"></div></div>
        ${N && N.tolak ? h`<div class="pita-info awas">${N.tolak}</div>` : ''}${N && !N.tolak && N.lonjak ? h`<div class="pita-info awas">HPP: ${N.lonjak}</div>` : ''}${N && !N.tolak && N.rugi ? h`<div class="pita-info awas">${N.rugi}</div>` : ''}
        ${N && !N.tolak ? h`<div class="hp-delta">${N.teksDelta}</div>` : ''}
        <div class="tombol-baris"><div class="utama ${!N || N.tolak || !String(hp.alasan).trim() ? 'redup' : ''}" data-aksi="hpSimpan">${hp.yakin ? 'YAKIN, SIMPAN' : 'SIMPAN KOREKSI'}</div><div class="kaca-btn" data-aksi="hpSiapkan">siapkan untuk massal</div></div>`
      : h`<div class="pita-info">Modal ${M.merk} datang dari stok awal / saldo pembuka (fondasi) — tidak dikoreksi dari sini; catat kedatangan barunya di Barang masuk.</div>`}</div>` : '';
    return h`<section class="stok-hpp" data-k="hpp">
      ${kepalaLembar('HPP / modal', 'cara hitung modal (rata-rata / FIFO) · harga beli terbaru (pembanding) · margin ke katalog · koreksi beralasan')}
      ${gambarFifo(s)}
      <div class="jalur rapat" data-k="hp-tab">${HP.TAB_HPP.map(([id, nm]) => h`<div class="seg ${hp.tab === id ? 'aktif' : ''}" data-aksi="hpTab" data-t="${id}">${nm}</div>`)}</div>
      <div class="ket">${K.ringkasTeks}</div>
      ${hp.tab === 'garis' ? h`<div class="kartu" data-k="hp-garis" style="gap: 4px;">${HP.garisWaktu().map((g) => h`<div data-k="hg-${g.merk}" style="padding-top: 6px;"><div style="font-weight: 700; font-size: 12.5px;">${g.merk}</div><div class="ket">${g.ket}</div>
          ${g.baris.map((r, i) => h`<div class="hp-garis" data-k="hg-${g.merk}-${i}"><span class="ket">${tanggalPendek(r.tanggal)}</span><div><div class="bar ${r.koreksi ? 'koreksi' : ''}" style="transform: scaleX(${r.lebar / 100});"></div><div class="ket" style="font-size: 10px;">${r.sumber} · ${DESIMAL(r.kg)} kg</div></div><span class="n">${RP(r.hpp)}${r.lonjak ? ' ' + r.lonjak : ''}</span></div>`)}</div>`)}</div>`
      : hp.tab === 'kelas' ? gambarHppKelas()
      : hp.tab === 'massal' ? h`<div class="ket">${PM.teks}</div><div class="kartu" data-k="hp-massal" style="gap: 2px;">${K.kartu.map((k) => { const m = PM.baris.find((b) => b.merk === k.merk); return h`<div class="jawab hp-massal ${hp.merk === k.merk ? 'dipilih' : ''}" data-k="hm-${k.merk}" data-aksi="hpPilih" data-merk="${k.merk}"><span class="kiri"><span class="nm">${k.merk}</span><span class="w">${m ? m.ket : DESIMAL(Math.round(k.sisa * 10) / 10) + ' kg · ' + k.teksMargin}</span></span><span class="kanan"><span class="ket">${RP(Math.round(k.modal))}</span><span class="n ${m && m.tolak ? 'awas' : ''}">${m ? RP(m.harga) : '—'}</span>${m ? h`<span class="ket tautan" data-aksi="hpBuang" data-merk="${k.merk}">buang</span>` : ''}</span></div>`; })}</div>
        ${koreksi}
        <div class="kartu" data-k="hp-massal-simpan" style="gap: 6px;"><input class="ketik-nama sempit" id="hpAlasanMassal" type="text" value="${hp.alasan}" data-ketik="hpKetik" data-kolom="alasan" placeholder="Satu alasan untuk semua (wajib)"><div class="utama ${PM.siap && String(hp.alasan).trim() ? '' : 'redup'}" data-aksi="hpMassal">${PM.siap ? 'TERAPKAN ' + PM.n + ' HPP SEKALIGUS · nilai rak ' + (PM.delta >= 0 ? '+' : '−') + RP(Math.round(Math.abs(PM.delta))) : PM.teks}</div><div class="ket">Semua-atau-tidak-sama-sekali: satu angka ditolak = tidak ada yang tersimpan.</div></div>`
      : h`<div class="hp-kartu-daftar" data-k="hp-kartu">${K.kartu.map((k) => h`<div class="kartu hp-kartu ${hp.merk === k.merk ? 'aktif' : ''}" data-k="hk-${k.merk}" data-aksi="hpPilih" data-merk="${k.merk}"><div><div style="font-weight: 700;">${k.merk}</div><div class="ket">${DESIMAL(Math.round(k.sisa * 10) / 10)} kg · nilai rak ${RP(Math.round(k.nilaiRak))} · ${k.sumber}</div>${k.fifo ? h`<div class="ket">${k.teksFifo}</div>` : ''}<div class="ket">harga beli terbaru ${k.hargaTerbaru === null ? 'belum ada' : RP(k.hargaTerbaru) + '/kg'}${Math.abs(k.bedaTerbaru) >= 1 ? ' (' + (k.bedaTerbaru > 0 ? '+' : '−') + RP(Math.round(Math.abs(k.bedaTerbaru))) + ' dari rata-rata)' : ''}${k.lonjakTerakhir ? ' · kedatangan terakhir ' + (k.lonjakTerakhir > 0 ? '▲' : '▼') + Math.abs(k.lonjakTerakhir) + ' %' : ''}</div></div><div style="text-align: right;"><div class="n">${RP(Math.round(k.modal))}<span class="ket">/kg</span></div><div class="m ${k.kelasMargin}">${k.teksMargin}</div></div></div>`)}</div>
        ${koreksi}`}
      ${log.length ? h`<div class="kartu" data-k="hp-log" style="gap: 2px;"><div class="label">Koreksi terakhir · perubahan nilai rak</div>${log.map((l) => h`<div class="hp-garis" data-k="hl-${l.id}" style="grid-template-columns: minmax(0, 1fr) auto;"><span class="ket">${tanggalPendek(l.tanggal)} ${l.jam} · ${l.merk} ${RP(l.hargaDari)} → ${RP(l.hargaKe)}/kg${l.massal ? ' (massal ' + l.massal + ')' : ''} · ${l.alasan}</span><span class="n ${l.deltaNilai < 0 ? 'awas' : ''}">${l.deltaNilai >= 0 ? '+' : '−'}${RP(Math.abs(l.deltaNilai))}</span></div>`)}</div>` : ''}
      ${s.aturHp ? h`<div class="kartu" data-k="atur-hp" style="gap: 8px;"><div class="label">Aturan HPP · angka owner</div><div class="ps-form dua">
        <div><div class="ket">Batas lonjakan modal (%)</div><input class="ketik-nama" id="ahLonjak" type="text" inputmode="numeric" value="${s.aturHp.batasLonjak}" data-ketik="hpKetikAtur" data-kolom="batasLonjak"></div>
        <div><div class="ket">Lantai HPP per kg (Rp)</div><input class="ketik-nama" id="ahLantai" type="text" inputmode="numeric" value="${s.aturHp.lantaiHpp}" data-ketik="hpKetikAtur" data-kolom="lantaiHpp"></div></div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturHp">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturHp">SIMPAN ATURAN</div></div></div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturHp" style="align-self: flex-start;">Atur batas lonjakan & lantai HPP ${K.atur.dariOwner ? '· diatur owner' : '· bawaan'} ›</div>`}
      <div class="ket" style="font-size: 11px;">${HP.saklarFifo(kini()).keadaan === 'nyala' ? 'Buku menilai modal FIFO (karung terlama keluar duluan; wadah campuran rata-rata); harga beli terbaru dipajang sebagai pembanding.' : 'Buku menilai modal RATA-RATA tertimbang semua kedatangan sampai saklar FIFO berlaku; harga beli terbaru dipajang sebagai pembanding.'} Angka aneh ditolak dengan kalimat, bukan dipotong diam-diam; margin Rp0 boleh (disengaja?).</div>
    </section>`;
  }

  function gambarTabWadah(s) {
    const M = ingatanWadah(); const w = M('susun', () => S.susunWadah(keranjangJual())); const a = w.atur; const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const tumpukanTeks = (t) => (!t.adaBuku ? t.merk + ' tidak ada di buku gudang' : t.minus ? 'tumpukan ' + t.merk + ' di gudang: buku KURANG ' + KG(-t.kg) + ' dari yang sudah di wadah & karung terbuka — cocokkan stok' : 'tumpukan ' + t.merk + ' di gudang ±' + t.karung + ' karung (' + KG(t.kg) + ') · buku ' + KG(t.bukuKg) + (t.lengkap ? '' : ' · perkiraan, ada yang belum ditandai'));
    if (s.atur) return gambarAturWadah(s.atur, w);
    const aktif = w.daftar.find((x) => x.nama === s.wadahAktif) || null;
    return h`<section class="stok-wadah" data-k="wadah">
      <div class="pita-info">Tumpukan karung di gudang → karung 50 kg yang sudah dibuka BERJAJAR di belakang deretan wadah → kotak wadah → dijual per liter. Satu wadah boleh diisi dari karung mana pun di deretan itu (mis. Angsa: 1 takar dari karung E + 1 takar dari karung D — foto toko 23 Sep). Buka karung: tumpukan gudang turun satu. Takar: karung yang dipilih turun, wadah naik. Literan terjual: wadah turun.
        ${w.perluIsi ? w.perluIsi + ' wadah minta diisi ulang. ' : ''}${w.karungTipis ? w.karungTipis + ' karung di belakang hampir habis. ' : ''}${w.belumDitandai ? w.belumDitandai + ' wadah belum pernah ditandai isinya.' : ''}</div>
      ${(() => { const DA = M('aktivasi', () => WB.wbDaftarAktivasi()); const belum = DA.filter((x) => !x.aktif); if (!belum.length) return '';
        // putaran 39 (owner 29 Sep a · d): aktivasi PER WADAH, owner memutuskan tiap barisnya — tidak ada tombol "semua sekaligus" (data lama tidak diubah diam-diam)
        const ak = opsi.akun ? opsi.akun() : null; const TL = tombolLuarKisi(ak); const TM = tombolAkun(ak, 'kedatangan');
        const tb = (aksi, nama, kelas, data, T) => (T.boleh ? h`<div class="kaca-btn ${kelas}" data-aksi="${aksi}"${atr(data)}>${nama}</div>` : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${T.kalimat}">${nama}</div>`);
        return h`<div class="kartu" data-k="aktivasi" style="gap: 4px;"><div class="label">Aktivasi buku wadah — per wadah, owner memutuskan · ${DA.length - belum.length} dari ${DA.length} wadah aktif</div>
          <div class="ket">Wadah yang aktif memegang BUKU SENDIRI: isi ulang masuk, literan keluar, cocokkan = penyesuaian buku itu. Mengaktifkan = isi tercatat (+ karung terbuka di belakangnya) pindah dari buku merek asalnya ke buku wadah, modal ikut — laba & neraca tidak berubah. Buku merek asal yang kurang tidak ditambal diam-diam: hitung fisik / catat barang masuk dulu, atau tandai untuk dicocokkan.</div>
          ${DA.map((x, i) => { const mFisik = ((x.kurang[0] || x.sumber[0]) || {}).merk || ''; const yakin = s.akYakin === x.W;
            const status = x.aktif ? 'aktif ✓' : x.bisa && x.cukup ? 'bisa diaktifkan' : x.bisa ? 'bisa — buku merek kurang' : 'belum bisa';
            return h`<div class="ak-baris" data-k="ak-${x.W}" style="--urut: ${i};"><div class="ak-kepala"><b>${x.no} · ${x.W}</b><span class="pil kecil ${x.aktif ? 'nyala' : x.bisa && !x.cukup ? 'awas' : ''}">${status}</span><span class="ket">${x.diketahui ? 'isi tercatat ±' + KG(x.isiKg) : 'isi belum ditandai'}${x.kolam.length ? ' · karung terbuka di belakang: ' + x.kolam.map((k) => k.merk + ' ±' + KG(k.kg)).join(', ') : ''}</span></div>
              ${x.aktif ? '' : h`${!x.bisa && x.alasan ? h`<div class="ket awas-teks">${x.alasan}</div>` : ''}
              ${x.sumber.length ? h`<div class="ak-sumber" data-k="ak-sumber-${x.W}"><span class="k">merek asal</span><span class="k">di wadah</span><span class="k">di karung</span><span class="k">buku merek</span><span class="k">kurang</span>
                ${x.sumber.map((m) => h`<span class="nm">${m.merk}</span><span class="n">${KG(m.diWadah)}</span><span class="n">${KG(m.diKarung)}</span><span class="n ${m.tanpaBuku ? 'awas' : ''}">${m.tanpaBuku ? 'tidak ada' : KG(m.buku)}</span><span class="n ${m.kurang > 0.004 ? 'awas' : ''}">${m.kurang > 0.004 ? KG(m.kurang) : '—'}</span>`)}</div>`
              : h`<div class="ket">Menurut catatan wadah ini kosong dan tidak ada karung terbuka di belakangnya${x.diketahui ? ' — aktivasi cuma melahirkan bukunya (0 kg)' : ''}.</div>`}
              <div class="tombol-baris rapat" data-k="ak-tombol-${x.W}">${x.bisa && x.cukup ? tb('aktifkan', yakin ? 'YAKIN — AKTIFKAN ' + x.no : 'AKTIFKAN ' + x.no, yakin ? 'awas' : 'aktif emas', { merk: x.W }, TL) : ''}${x.bisa && !x.cukup ? tb('aktifkan', 'TANDAI UNTUK DICOCOKKAN', 'awas', { merk: x.W }, TL) : ''}${mFisik ? tb('hitungFisik', 'Hitung fisik ' + mFisik + ' dulu', '', { merk: mFisik }, TL) : ''}${tb('bukaMasuk', 'Catat barang masuk', '', {}, TM)}${!x.diketahui ? h`<div class="kaca-btn putus" data-aksi="pilihWadah" data-merk="${x.W}">samakan isi ${x.no} ›</div>` : ''}</div>
              ${s.tandai && s.tandai.jenis === 'aktifkan' && s.tandai.W === x.W ? pitaTandai(s.tandai) : ''}`}</div>`; })}</div>`; })()}
      ${(() => { const TT = M('tertinggal', () => WB.wbKarungTertinggal()); if (!TT.semua.length) return ''; const ak = opsi.akun ? opsi.akun() : null; const TK = tombolLuarKisi(ak); const KG2 = (n) => DESIMAL(Math.round(n * 100) / 100) + ' kg';
        // 39b no. 5 · keputusan owner 1 Okt: sisa pengembalian karung 30 Sep dengan kode lama — beras sudah di tumpukan, buku karung belakang masih memuatnya → SATU tombol
        const di = (x) => (x.lokasi === undefined ? 'sudah dikembalikan, belakang ' + x.wadah : x.lokasi === '' ? 'karung lepas, masih berdiri' : 'masih berdiri di belakang ' + x.lokasi);
        return h`<div class="kartu" data-k="karung-tertinggal" style="gap: 6px;"><div class="label">Buku karung yang tertinggal · sisa pengembalian sebelum 1 Okt</div>
          <div class="ket">Beras ini sudah balik ke tumpukan gudang, tapi masih tercatat di buku karung belakang: ${TT.semua.map((x) => x.merk + ' ' + KG2(x.pindahKg) + ' (' + di(x) + ')').join(' · ')}. Pindah balik = buku karung → buku mereknya (modal ikut); laba tidak berubah.${TT.berdiri.length ? ' Karung yang masih berdiri: sisa lamanya keluar dari bukunya; kalau mau ditimbang, pakai Cocokkan biasa sesudahnya.' : ''}</div>
          ${TK.boleh ? h`<div class="kaca-btn ${s.ttgYakin ? 'awas' : 'aktif emas'}" data-aksi="ttgPindah">${s.ttgYakin ? 'YAKIN — pindah balik ' + TT.semua.length + ' karung · ' + KG2(TT.kgSemua) : 'Pindah balik ' + TT.semua.length + ' karung · ' + KG2(TT.kgSemua) + ' ke mereknya'}</div>` : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${TK.kalimat}">Pindah balik (owner)</div>`}</div>`; })()}
      ${(() => { const KT = M('karungBekasTunda', () => WB.wbKarungBekasTunda()); if (!KT.n) return ''; const ak = opsi.akun ? opsi.akun() : null; const TK = tombolLuarKisi(ak);
        // owner 7 Okt: karung di belakang wadah yang habis = karung bekas; yang dicatat akun bukan-owner dititip (rules v5 belum membuka buku karung bekas untuknya)
        const teks = (x) => (x.merkAsal || x.merk) + ' (' + x.wadah + (x.tanggalAsal ? ', ' + tanggalPendek(x.tanggalAsal) + (x.jamAsal ? ' ' + x.jamAsal : '') : '') + (x.olehAsal ? ', ' + x.olehAsal : '') + ')';
        return h`<div class="kartu" data-k="karung-bekas-tunda" style="gap: 6px;"><div class="label">Karung bekas menunggu dicatat · ${KT.n}</div>
          <div class="ket">${KT.lahir.length ? 'Karung habis → jadi karung bekas: ' + KT.lahir.map(teks).join(' · ') + '. ' : ''}${KT.batal.length ? 'Ternyata belum habis / dikembalikan → catatan karung bekasnya dicabut: ' + KT.batal.map(teks).join(' · ') + '. ' : ''}Dicatat akun bukan-owner; buku karung bekas baru bergerak sesudah owner mencatatnya di sini (bertanggal hari ini, tanggal asalnya ikut tertulis).</div>
          ${TK.boleh ? h`<div class="kaca-btn ${s.kbsYakin ? 'awas' : 'aktif emas'}" data-aksi="kbsCatat">${s.kbsYakin ? 'YAKIN — catat ' + KT.n + ' karung bekas' : 'Catat ' + KT.n + ' karung bekas ke bukunya'}</div>` : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${TK.kalimat}">Catat karung bekas (owner)</div>`}</div>`; })()}
      ${(() => { const ak = opsi.akun ? opsi.akun() : null; if (bukanOwner(ak)) return ''; const N = M('kbNilai', () => WB.wbKbNilai()); const ketik = String(s.kbNilai || '').trim();
        // owner 7 Okt: nilai karung bekas = setelan owner (bawaan keputusan 15 Sep); kelahiran dinilai harga BUKU mesin supaya neraca = laba — setelan berlaku sesudah diterapkan ke buku
        const sel = (n) => RP(n) + '/lembar'; const rak = Math.max(0, N.sisa); const d = rak * (N.setelan - N.buku);
        const tombol = s.kbNilaiYakin ? 'YAKIN — terapkan ' + (ketik ? 'nilai baru' : sel(N.setelan)) : ketik ? 'Simpan & terapkan ke buku' : N.selaras && N.diatur ? 'Ubah nilai (ketik dulu)' : 'Terapkan ' + sel(N.setelan) + ' ke buku';
        return h`<div class="kartu" data-k="nilai-karung-bekas" style="gap: 6px;"><div class="label">Nilai karung bekas · ${sel(N.setelan)} · ${N.diatur ? 'setelan owner' : 'bawaan: keputusan owner 15 Sep'}</div>
          <div class="ket ${N.selaras ? '' : 'awas-teks'}">${N.selaras ? 'Buku karung bekas ' + rak + ' lembar dinilai ' + sel(N.buku) + ' — karung bekas yang lahir dinilai ' + RP(N.buku) + ', yang dipakai / dijual dibebankan ' + RP(N.buku) + '.'
            : 'Buku karung bekas ' + rak + ' lembar masih dinilai ' + sel(N.buku) + ' (rata-rata baris belanja lamanya — baris itu tidak diubah). Karung bekas yang lahir dinilai harga BUKU itu supaya neraca = laba, sampai setelan diterapkan: rak ' + (d >= 0 ? 'naik ' : 'turun ') + RP(Math.abs(d)) + ' = laba hari itu ' + (d >= 0 ? 'naik ' : 'turun ') + RP(Math.abs(d)) + ' (selisih nilai, bukan uang masuk; bulan lalu tidak berubah).'}</div>
          <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="kbNilaiKetik" type="text" inputmode="numeric" placeholder="${RP(N.setelan)} per lembar" value="${s.kbNilai}" data-ketik="kbNilaiKetik">
            <div class="kaca-btn ${s.kbNilaiYakin ? 'awas' : !ketik && N.selaras && N.diatur ? 'mati' : 'aktif emas'}" data-aksi="kbNilaiSimpan">${tombol}</div></div></div>`; })()}
      ${(() => { const SL = L.slotKarungWadah(); const LP = L.karungLepasDeretan(); const dp = s.drPilih; const kPilih = dp && dp.merk ? SL.find((x) => !x.kosong && x.merk === dp.merk && x.W === dp.lokasi) : null; const lPilih = dp && dp.merk && !kPilih ? LP.find((x) => x.merk === dp.merk && x.lokasi === dp.lokasi) : null; const k = kPilih ? kPilih.karung : lPilih;
        // putaran 39c (owner 30 Sep): deretan = SATU SLOT PER WADAH (W1..Wn) seperti tata letak HP; karung habis bisa dihapus; dikembalikan / dihapus → slot "?" garis putus; karung lepas di baris kecil sendiri
        return h`<div class="kartu" data-k="deretan" style="gap: 6px;"><div class="label">Deretan karung terbuka di belakang wadah · ${SL.length} slot, urut W1 → W${SL.length}${LP.length ? ' · lalu ' + LP.length + ' karung lepas' : ''}</div>
        <div class="petak-wadah deretan-slot" data-k="deretan-slot">${SL.map((x, i) => x.kosong
          ? h`<div class="kartu petak slot kosong ${dp && !dp.merk && dp.lokasi === x.W ? 'dipilih' : ''}" data-k="slot-${x.W}" data-aksi="drKosong" data-wadah="${x.W}" title="belum ada karung di belakang wadah ${x.W}" style="--urut: ${i};"><div class="no">${x.no}</div><div class="gambar-chip">${mentah(gambarKarungStok(x.karung))}</div><div class="nm">belum ada karung</div><div class="ket">${x.alasan}${x.terakhirMerk ? ' · terakhir ' + x.terakhirMerk : ''}</div></div>`
          : h`<div class="kartu petak slot ${x.habis ? 'habis' : ''} ${kPilih && kPilih.W === x.W ? 'dipilih' : ''}" data-k="slot-${x.W}" data-aksi="drPilih" data-merk="${x.merk}" data-lokasi="${x.W}" title="di belakang wadah ${x.W}" style="--urut: ${i};"><div class="no">${x.no}</div><div class="gambar-chip">${mentah(gambarKarungStok(x.karung))}</div><div class="nm">${x.merkAsal}</div><div class="ket">${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : 'belum ditandai'}${x.habis ? ' · HABIS' : ''}${x.bukuSendiri ? ' · buku sendiri' : ''}</div></div>`)}</div>
        ${LP.length ? h`<div class="label" style="font-size: 9px;">Karung lepas · yatim · sisihan wadah (masih berisi)</div><div class="deretan-isi">${LP.map((y) => h`<div class="karung-deret ${dp && dp.merk === y.merk && dp.lokasi === y.lokasi ? 'dipakai' : ''}" data-k="dr-${y.merk}|${y.lokasi}" data-aksi="drPilih" data-merk="${y.merk}" data-lokasi="${y.lokasi}" title="${y.letak}"><div class="gambar-chip">${mentah(gambarKarungStok(y))}</div><div class="nm">${y.merkAsal || y.merk}</div><div class="ket">±${KG(y.sisaKg)}</div></div>`)}</div>` : ''}
        ${(() => { if (dp && !dp.merk && dp.lokasi) { const x = SL.find((z) => z.W === dp.lokasi); return h`<div class="dr-aksi" data-k="dr-aksi"><div><b>${x ? x.no + ' · ' + x.W : dp.lokasi}</b> · belum ada karung di belakangnya${x && x.alasan ? ' (' + x.alasan + ')' : ''}${x && x.terakhirMerk ? ' · terakhir ' + x.terakhirMerk : ''}</div>
            <div class="ket">Karung berikutnya diambil dari tumpukan gudang lewat isi ulang wadah ini (tiga ketukan: pilih mereknya dari tumpukan) — merek apa pun yang datang dari pemasok.</div>
            <div class="tombol-baris rapat"><div class="kaca-btn" data-aksi="pilihWadah" data-merk="${dp.lokasi}">buka wadah ${x ? x.no : dp.lokasi} ›</div></div></div>`; }
          if (!k) return h`<div class="ket">Ketuk satu karung untuk menyamakan sisanya, mengembalikannya ke tumpukan, atau menghapusnya kalau sudah habis. Slot "?" = belum ada karung di belakang wadah itu.</div>`;
          const habis = k.diketahui && k.sisaMentahKg <= 0.5; const lokasi = kPilih ? kPilih.W : lPilih.lokasi; const nama = kPilih ? kPilih.merkAsal : (lPilih.merkAsal || lPilih.merk); const letak = kPilih ? 'di belakang wadah ' + kPilih.W : lPilih.letak;
          return h`<div class="dr-aksi" data-k="dr-aksi"><div><b>${nama}</b>${kPilih && kPilih.bukuSendiri ? ' (buku sendiri ' + kPilih.merk + ')' : ''} · ${letak} · ${k.diketahui ? 'sisa ±' + KG(k.sisaKg) : 'belum ditandai'}${habis ? ' — HABIS' : ''}${lPilih && lPilih.yatim ? ' · yatim (wadahnya kini memegang karung lain)' : ''}</div>
            <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="drKetik" type="text" inputmode="decimal" placeholder="sisa kg" value="${s.krKetik}" data-ketik="krKetik"><div class="kaca-btn ${String(s.krKetik || '').trim() ? '' : 'mati'}" data-aksi="samakanKarung" data-merk="${k.merk}" data-wadah="${lokasi}">samakan sisa</div>
              ${habis ? h`<div class="kaca-btn ${s.drYakin ? 'awas' : 'aktif emas'}" data-aksi="drHapus" data-merk="${k.merk}" data-lokasi="${lokasi}">${s.drYakin ? 'YAKIN — hapus & catat susut bukunya' : 'habis · hapus dari deretan'}</div>` : h`<div class="kaca-btn ${s.drYakin ? 'awas' : 'putus'}" data-aksi="drKembalikan" data-merk="${k.merk}" data-lokasi="${lokasi}">${s.drYakin ? 'YAKIN — kembalikan ke tumpukan' : 'kembalikan ke tumpukan gudang'}</div>`}
              ${lokasi && w.daftar.some((z) => z.nama === lokasi) ? h`<div class="kaca-btn" data-aksi="pilihWadah" data-merk="${lokasi}">buka wadah ${kPilih ? kPilih.no : lokasi} ›</div>` : ''}</div>
            <div class="ket" style="font-size: 10.5px;">${habis ? 'Hapus = karung yang sudah habis dilipat; slotnya jadi kosong ("?") dan karung berikutnya dibuka dari tumpukan saat isi ulang, merek apa pun. Kalau bukunya masih bersisa, ketukan kedua mencatat susutnya (tidak diam).' : 'Kembalikan = karung ini dianggap tidak jadi dibuka / sudah ditaruh lagi di tumpukan: sisanya kembali dihitung ke tumpukan gudang (catatan bukanya dihapus bila belum pernah ditakar). Stok buku tidak berubah.'}</div></div>`; })()}</div>`; })()}
      <div class="petak-wadah" data-k="petak">${w.daftar.map((x, i) => h`<div class="kartu petak ${x.nama === s.wadahAktif ? 'dipilih' : ''} ${x.diketahui && x.perluIsi ? 'isi-ulang' : ''}" data-k="petak-${x.nama}" data-aksi="pilihWadah" data-merk="${x.nama}" style="--urut: ${i};">
        <div class="no">${x.no}</div>
        <div class="tumpuk-gambar"><div class="gambar-karung">${mentah(gambarKarungStok(x.karung))}</div><div class="gambar-kotak">${mentah(gambarWadah(x))}</div></div>
        <div class="nm">${x.nama}</div>
        <div class="ket">karung ${(x.stokSendiri ? x.karungAsal : x.karungNama) !== x.nama ? (x.stokSendiri ? x.karungAsal : x.karungNama) + ' ' : ''}${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}${x.stokSendiri && WB.wbBukuKhusus(x.karungNama) ? ' · buku sendiri' : ''}</div>
        <div class="ket">wadah ${x.diketahui ? '±' + KG(x.sisaKg) : '?'}</div>
      </div>`)}</div>
      <div class="kaca-btn" data-aksi="bukaAtur">Atur susunan, isi &amp; aturan wadah</div>
      ${aktif ? h`<div class="kartu rincian-wadah" data-k="rincian-${aktif.nama}">
        <div class="label">${aktif.no} · ${aktif.nama}${aktif.resep.length > 1 ? ' · campuran ' + aktif.resep.map((r) => r.takar).join(' : ') + ' — ' + aktif.resep.map((r) => r.merk).join(' : ') : ''}</div>
        ${(() => { const K = WB.wbKomposisi(aktif.nama, keranjangJual()); if (K.stokSendiri) return h`<div class="ket" data-k="komposisi-${aktif.nama}">Stok wadah sendiri (buku ${K.kunci}): ±${KG(K.totalKg)} · modal ${RP(Math.round(WB.wbModalPerKg(aktif.nama)))}/kg. Literan yang terjual cuma memotong stok wadah ini; takar dari karung di belakang memindah buku karungnya ke sini (modal ikut).${K.totalKg < -0.004 ? ' Stoknya MINUS — takar yang lupa dicatat? catat takarnya atau cocokkan wadah ini.' : ''}</div>`;
          return h`<div class="ket" data-k="komposisi-${aktif.nama}">${!K.diketahui ? 'Isi per merek belum diketahui — cocokkan wadah ini dulu (Stok › Cocokkan › Wadah literan).'
          : K.positif.length ? 'Isi menurut buku: ' + K.positif.map((x) => x.merk + ' ' + KG(x.kg)).join(' + ') + '. Literan yang terjual memotong buku merek-merek itu sebanding isinya' + (K.positif.length > 1 ? ' (' + K.positif.map((x) => Math.round(x.kg * 100 / K.positif.reduce((q, y) => q + y.kg, 0)) + '%').join(' : ') + ')' : '') + '.' : 'Menurut buku wadah ini kosong.'}
          ${Object.keys(K.bagian).some((m) => K.bagian[m] < 0) ? ' Ada bagian MINUS (' + Object.keys(K.bagian).filter((m) => K.bagian[m] < 0).map((m) => m + ' ' + KG(K.bagian[m])).join(', ') + ') — isi ulang lupa dicatat? cocokkan wadah ini.' : ''}</div>`; })()}
        ${panelIsiUlang(aktif.nama, s, keranjangJual(), { akun: opsi.akun ? opsi.akun() : null })}
        ${(() => { const KB0 = aktif.stokSendiri ? WB.wbKarungBelakangWadah(aktif.nama).filter((k) => k.diketahui && Math.abs(k.selisihKg) > 0.05) : [];
          // peringatan yang dulu hanya ada di dalam lipatan tetap disebut di luarnya (tinjauan #76 S1): catatan ≠ buku, takar melebihi isi karung, tumpukan minus
          const awas = [].concat(KB0.length ? ['catatan karung di belakang beda dengan bukunya: ' + KB0.map((k) => k.merk + ' ' + (k.selisihKg > 0 ? '+' : '−') + KG(Math.abs(k.selisihKg))).join(', ')] : [],
            aktif.karung && aktif.karung.diketahui && aktif.karung.lewat ? ['takar yang tercatat ' + KG(aktif.karung.lewat) + ' LEBIH dari isi karung di belakang'] : [],
            aktif.tumpukan && aktif.tumpukan.adaBuku && aktif.tumpukan.minus ? ['tumpukan ' + aktif.tumpukan.merk + ' di gudang: buku KURANG ' + KG(-aktif.tumpukan.kg)] : []);
          return h`<div class="kaca-btn putus" data-k="rincian-lain-${aktif.nama}" data-aksi="rincianLain">${s.rincianLain ? 'tutup pengaturan karung & wadah' : 'Karung di belakang, ganti nama & karung sisihan ▾'}</div>
          ${!s.rincianLain && awas.length ? h`<div class="ket awas-teks" data-k="rincian-awas-${aktif.nama}">${awas.join(' · ')} — buka "Karung di belakang" di atas untuk menyamakan.</div>` : ''}`; })()}
        ${s.rincianLain ? h`
        <div class="tombol-baris rapat" data-k="ganti-nama"><input class="ketik-nama sempit" id="gnKetik" type="text" placeholder="nama baru wadah ini" value="${s.gnKetik}" data-ketik="gnKetik"><div class="kaca-btn putus ${String(s.gnKetik || '').trim() ? '' : 'mati'}" data-aksi="gantiNamaWadah" data-merk="${aktif.nama}">ganti nama wadah</div></div>
        ${(() => { const nk = s.krNama || aktif.karungNama; const draf = nk !== aktif.karungNama; const kr = draf ? L.karungBelakang(nk, aktif.nama) : aktif.karung; const tg = draf ? L.tumpukanGudang(nk) : aktif.tumpukan; const C = s.krPilih ? L.calonBukaKarung(14) : null; const asal = s.krNama && s.krNama === nk ? s.krAsal : null;
          const asalTeks = !asal ? 'dari tumpukan gudang' : asal.jenis === 'masuk' ? 'yang baru datang dari pemasok' : '— kemasan ' + asal.ukuran + ' kg hasil adukan';
          // putaran 39: di belakang wadah aktif karungnya bernama kunci bukunya ('Karung belakang W · merek') — tampil & dibuka atas nama MEREK ASALNYA (buka = pindah buku merek → karung belakang)
          const nkAsal = WB.wbMerkAsal(nk); const bukuKB = nkAsal !== nk; const bukaMerk = bukuKB ? nkAsal : nk;
          return h`<div class="baris-wadah" data-k="kr-${nk}"><div class="gambar-chip besar">${mentah(gambarKarungStok(kr))}</div>
          <div><div class="label">Karung di belakang · dari tumpukan gudang, kiriman pemasok, atau hasil adukan</div>
            <div class="serif" style="font-size: 19px;">${nkAsal}${bukuKB ? ' · buku sendiri' : ''} ${kr.diketahui ? '±' + KG(kr.sisaKg) : '— belum ditandai'}</div>
            <div class="ket">${draf ? 'BELUM dicatat: buka satu karung ' + nk + ' ' + asalTeks + ' atau ketik sisanya — baru karung ini jadi karung di belakang ' + aktif.nama + '.'
              : kr.diketahui ? 'dari ' + kr.penuhKg + ' kg · terakhir ' + tanggalPendek(kr.sejakTanggal) + ' ' + kr.sejakJam + (kr.lewat ? ' · takar yang tercatat ' + KG(kr.lewat) + ' LEBIH dari isi karungnya — samakan' : '') : 'Buka satu karung baru dari tumpukan gudang, atau ketik sisa karung yang sedang terbuka.'}</div>
            <div class="ket">${asal && asal.jenis === 'adukan' ? 'stok kemasan ' + nk + ' ' + asal.ukuran + ' kg turun 1 unit; berasnya masuk buku sendiri Adukan ' + nk + ' ' + asal.ukuran + ' kg (terpisah dari beli pemasok)' : tumpukanTeks(tg)}</div></div></div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${kr.diketahui && kr.sisaKg > a.takarKg * 3 ? '' : 'aktif'}" data-aksi="bukaKarung" data-merk="${bukaMerk}" data-wadah="${aktif.nama}">Buka 1 ${asal && asal.jenis === 'adukan' ? nk + ' ' + asal.ukuran + ' kg' : 'karung ' + nkAsal} ${asal && asal.jenis === 'adukan' ? 'hasil adukan' : asalTeks}</div>
          <div class="kaca-btn putus" data-aksi="krPilihBuka">${s.krPilih ? 'batal' : 'karung lain…'}</div></div>
        ${s.tandai && s.tandai.jenis === 'bukaKarung' && s.tandai.wadah === aktif.nama ? pitaTandai(s.tandai) : ''}
        ${C ? h`<div class="pintu-karung" data-k="calon-karung">
          <div class="label">1 · Tumpukan gudang</div>
          <div class="tombol-baris rapat" data-k="pintu-tumpukan">${C.tumpukan.length ? C.tumpukan.map((t) => h`<div class="kaca-btn ${t.merk === nkAsal && !asal ? 'aktif' : ''}" data-aksi="krNama" data-merk="${t.merk}" data-asal="">${t.merk} · ${t.karung} karung${t.dipegang.length ? ' · sudah terbuka di belakang ' + t.dipegang.join(', ') : ''}</div>`) : h`<div class="ket">Menurut buku, tidak ada karung di tumpukan gudang.</div>`}</div>
          <div class="label">2 · Baru datang dari pemasok · 14 hari terakhir</div>
          <div class="tombol-baris rapat" data-k="pintu-masuk">${C.masuk.length ? C.masuk.map((x) => h`<div class="kaca-btn ${asal && asal.jenis === 'masuk' && String(asal.batchId) === String(x.batchId) && x.merk === nk ? 'aktif' : ''}" data-aksi="krNama" data-merk="${x.merk}" data-asal="masuk" data-batch="${x.batchId}">${x.merk} · ${x.karung}×${x.berat} kg · ${tanggalPendek(x.tanggal)}${x.pemasok ? ' · ' + x.pemasok : ''}</div>`) : h`<div class="ket">Tidak ada kedatangan karung 14 hari terakhir — catat dulu di Stok › Barang masuk.</div>`}</div>
          <div class="label">3 · Hasil adukan · kemasan jadi 25 / 50 kg</div>
          <div class="tombol-baris rapat" data-k="pintu-adukan">${C.adukan.length ? C.adukan.map((x) => h`<div class="kaca-btn ${asal && asal.jenis === 'adukan' && x.namaProduk === nk && asal.ukuran === x.ukuran ? 'aktif' : ''}" data-aksi="krNama" data-merk="${x.namaProduk}" data-asal="adukan" data-uk="${x.ukuran}">${x.namaProduk} ${x.ukuran} kg · ${x.unit} unit</div>`) : h`<div class="ket">Tidak ada kemasan jadi 25 / 50 kg di stok.</div>`}</div>
          <div class="ket" style="font-size: 10.5px;">Di buku ketiganya sama: karung pemasok & tumpukan = buku merek itu; kemasan hasil adukan dibuka = stok kemasannya turun 1 unit, berasnya masuk buku sendiri "Adukan <nama> <ukuran> kg" (modal ikut, tidak dicampur ke buku merek pemasok).</div></div>` : ''}
        <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="krKetik" type="text" inputmode="decimal" placeholder="sisa kg" value="${s.krKetik}" data-ketik="krKetik"><div class="kaca-btn ${String(s.krKetik || '').trim() ? '' : 'mati'}" data-aksi="samakanKarung" data-merk="${nk}" data-wadah="${aktif.nama}">samakan sisa karung ${nkAsal}</div>${!draf && kr.diketahui ? h`<div class="kaca-btn ${s.drYakin && s.drPilih && s.drPilih.merk === nk && s.drPilih.lokasi === aktif.nama ? 'awas' : 'putus'}" data-aksi="drKembalikan" data-merk="${nk}" data-lokasi="${aktif.nama}">${s.drYakin && s.drPilih && s.drPilih.merk === nk ? 'YAKIN — kembalikan' : 'kembalikan ke tumpukan'}</div>` : ''}</div>`; })()}
        ${aktif.stokSendiri ? (() => { const { KB, KT, SW, CK } = M('aktif|' + aktif.nama, () => ({ KB: WB.wbKarungBelakangWadah(aktif.nama), KT: WB.wbKomposisiTurunan(aktif.nama, keranjangJual()), SW: WB.wbSelisihWadah(aktif.nama, keranjangJual()), CK: WB.wbCekHari(tanggalTutupAktif(kini())).daftar.find((x) => x.W === aktif.nama) || null }));
          const beda = (k) => k.diketahui && Math.abs(k.selisihKg) > 0.05; const adaBeda = KB.some(beda);
          // putaran 39 (owner 29 Sep 1 · c · e · f): karung belakang = BUKU MESIN per merek; catatan (kolam) vs buku disebut selisihnya; komposisi = turunan isi ulang; cek tutup toko hari ini
          return h`<div class="kartu" data-k="belakang-${aktif.nama}" style="gap: 6px;"><div class="label">Karung di belakang wadah ${aktif.no} ${aktif.nama} · buku sendiri per merek</div>
            ${KB.length ? h`<div class="kb-baris kepala" data-k="kb-kepala-${aktif.nama}"><span class="k">merek</span><span class="k">buku</span><span class="k">catatan</span><span class="k">selisih</span></div>
              ${KB.map((k) => h`<div class="kb-baris ${beda(k) ? 'awas' : ''}" data-k="kb-${k.kunci}"><span class="nm">${k.merk}</span><span class="n">±${KG(k.bukuKg)}</span><span class="n">${k.diketahui ? '±' + KG(k.kolamKg) : 'belum ditandai'}</span><span class="n ${beda(k) ? 'awas' : ''}">${!k.diketahui ? '—' : beda(k) ? (k.selisihKg > 0 ? '+' : '−') + KG(Math.abs(k.selisihKg)) : 'cocok'}</span>
                ${beda(k) ? h`<div class="kb-aksi"><span class="ket awas-teks">catatan ${k.selisihKg > 0 ? 'LEBIH' : 'KURANG'} ${KG(Math.abs(k.selisihKg))} dari buku ${k.kunci} — ketik sisa kg-nya, lalu</span><div class="kaca-btn kecil ${String(s.krKetik || '').trim() ? 'awas' : 'mati'}" data-aksi="samakanKarung" data-merk="${k.kunci}" data-wadah="${aktif.nama}">samakan karungnya</div></div>` : ''}</div>`)}
              ${adaBeda ? h`<div class="tombol-baris rapat" data-k="kb-ketik-${aktif.nama}"><input class="ketik-nama sempit" id="kbKetik" type="text" inputmode="decimal" placeholder="sisa kg karung yang disamakan" value="${s.krKetik}" data-ketik="krKetik"><div class="ket" style="align-self: center;">Samakan = catatan karung diset ke sisa yang ditimbang; bukunya tidak berubah (buku turun hanya lewat takar / cocokkan). Bukunya yang salah? Timbang di Cocokkan › Wadah literan — tercatatnya = buku, jadi buku dan catatan sama-sama jadi hitungan.</div></div>` : ''}`
            : h`<div class="ket">Belum ada karung berbuku sendiri di belakang wadah ini — buka karung dari tumpukan gudang: buku merek turun, buku "Karung belakang ${aktif.nama} · merek" naik (modal ikut).</div>`}
            <div class="ket" data-k="komposisi-turunan-${aktif.nama}">Isi kotak (turunan isi ulang sejak titik samakan terakhir): ${KT.teks}</div>
            ${SW.ada ? h`<div class="ket awas-teks" data-k="selisih-${aktif.nama}">${SW.teks}</div>` : ''}
            <div class="ket" data-k="cek-${aktif.nama}">Cek tutup toko hari ini: ${CK && CK.dicek ? CK.hasilTeks + ' · ' + CK.jam + (CK.oleh ? ' oleh ' + CK.oleh : '') + (CK.bukuSaatCek !== null ? ' · buku saat dicek ±' + KG(CK.bukuSaatCek) : '') : 'belum dicek'}</div></div>`; })() : ''}
        ${aktif.stokSendiri ? (() => { const KW = WB.wbKarungWadah(aktif.nama); const ada = KW.sisaKg > 0.004; return h`<div class="kartu" data-k="sisih-${aktif.nama}" style="gap: 6px;">
          <div class="label">Karung wadah ${aktif.no} ${aktif.nama} · isi yang dikeluarkan dari kotak</div>
          <div class="ket">${ada ? 'Karung sisihan ±' + KG(KW.sisaKg) + ' — stok terpisah (buku ' + KW.kunci + ').' : 'Karung sisihannya kosong.'} Tutup toko: sisihkan yang menggunung ke karung ini; buka toko: tuang balik. Setahun sekali: bongkar = kotak dikosongkan penuh ke karung, hasilnya ditimbang.</div>
          <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="shKetik" type="text" inputmode="decimal" placeholder="${DESIMAL(a.sisihKg)} kg" value="${s.shKetik}" data-ketik="shKetik">
            <div class="kaca-btn" data-aksi="sisihkan" data-merk="${aktif.nama}">sisihkan ${String(s.shKetik || '').trim() ? '' : DESIMAL(a.sisihKg) + ' kg '}ke karung</div>
            ${ada ? h`<div class="kaca-btn aktif" data-aksi="tuangBalik" data-merk="${aktif.nama}">tuang balik ${String(s.shKetik || '').trim() ? '' : 'semua ±' + KG(KW.sisaKg)}</div>` : ''}</div>
          <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="bgKetik" type="text" inputmode="decimal" placeholder="hasil timbang kg" value="${s.bgKetik}" data-ketik="bgKetik">
            <input class="ketik-nama sempit" id="bgAlasan" type="text" placeholder="alasan kalau selisih besar" value="${s.bgAlasan}" data-ketik="bgAlasan">
            <div class="kaca-btn ${s.bgYakin ? 'awas' : 'putus'} ${String(s.bgKetik || '').trim() ? '' : 'mati'}" data-aksi="bongkar" data-merk="${aktif.nama}">${s.bgYakin ? 'YAKIN — bongkar ' + aktif.nama : 'bongkar (kosongkan penuh)'}</div></div></div>`; })() : ''}
        ` : ''}
      </div>` : h`<div class="ket" style="text-align: center;">Ketuk satu wadah untuk mengisi ulang atau menandai karungnya.</div>`}
      <div class="kartu" data-k="karung-lain" style="gap: 6px;"><div class="label">Karung terbuka lain · bahan campuran, tidak di belakang wadah</div>
        ${w.lain.length ? w.lain.map((x) => h`<div class="jawab" data-k="kl-${x.nama}|${x.lokasi}"><span class="kiri"><span class="nm">${x.nama}${x.lokasi ? ' · dulu di belakang wadah ' + x.lokasi : ''}</span><span class="w">${x.karungWadah ? 'karung sisihan / bongkaran wadah ' + x.karungWadah + ' — dituang balik lewat rincian wadahnya, atau ditakar ke wadah lain dari deretan' : tumpukanTeks(x.tumpukan)}</span></span>
          <span class="kanan"><span class="n">${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}</span>${x.karungWadah ? '' : h`<span class="w tautan" data-aksi="bukaKarung" data-merk="${x.nama}">buka karung baru</span>`}${x.karung.diketahui ? h`<span class="w tautan" data-aksi="drPilih" data-merk="${x.nama}" data-lokasi="${x.lokasi}">atur / kembalikan ›</span>` : ''}</span></div>`) : h`<div class="ket">Belum ada.</div>`}
        <div class="ket tautan" data-aksi="lainPilihBuka">${s.lainPilih ? 'batal' : '+ buka karung bahan campuran dari gudang'}</div>
        ${s.lainPilih ? h`<div class="tombol-baris rapat" data-k="calon-lain">${L.calonKarung().map((t) => h`<div class="kaca-btn" data-aksi="bukaKarung" data-merk="${t.merk}">${t.merk} · ${t.karung} karung${t.dipegang.length ? ' · sudah terbuka di belakang ' + t.dipegang.join(', ') : ''}</div>`)}</div>` : ''}</div>
      <div class="kartu" data-k="atur-wadah" style="gap: 4px;"><div class="label">Aturan wadah ${a.dariOwner ? '· diatur owner ' + tanggalPendek(a.sejak) : '· bawaan'}</div>
        <div class="ket">rata sejajar bibir kotak ${DESIMAL(a.penuhKg)} kg · menggunung sampai ${DESIMAL(a.puncakKg)} kg · minta isi ulang saat tersisa ${DESIMAL(a.isiUlangKg)} kg · 1 takar ${DESIMAL(a.takarKg)} kg · susut wajar ≤ ${DESIMAL(a.susutWajarKg)} kg/wadah/hari · sisihkan ${DESIMAL(a.sisihKg)} kg saat tutup · ${a.daftar.length} wadah</div>
        <div class="ket">Tiap tingkat turun lewat jalurnya sendiri: buka karung → tumpukan gudang · takar → karung di belakang turun, STOK WADAH naik (buku merek karungnya pindah ke buku wadah, modal ikut) · literan terjual → stok wadah saja. Untuk tiap merek: tumpukan + karung terbuka = bukunya; untuk tiap wadah: isi wadah = buku wadahnya.</div></div>
    </section>`;
  }

  // Pita dua tombol pola "tandai" (owner 29 Sep d): ketukan pertama sudah menolak dengan kalimat r.tolak + r.perluTandai; di sini owner memilih —
  // catat barang masuk dulu (lembar Barang masuk, merek terisi) atau TANDAI UNTUK DICOCOKKAN (ketukan kedua = kiriman yang sama dengan opsi { tandai: true }).
  function pitaTandai(t) {
    const ak = opsi.akun ? opsi.akun() : null; const TM = tombolAkun(ak, 'kedatangan'); const daftar = t.daftar || [];
    return h`<div class="pita-info awas pita-tandai" data-k="pita-tandai-${t.jenis}-${t.W || t.wadah || ''}-${t.merk || ''}"><div><b>${t.kalimat}</b></div>
      <div class="ket">${daftar.map((x) => x.merk + ': buku ' + (x.buku === null || x.buku === undefined ? 'tidak ada' : KGs(x.buku)) + ' · butuh ' + KGs(x.butuh) + ' · kurang ' + KGs(x.kurang)).join(' · ')}. Tandai = buku merek dibiarkan MINUS sebesar itu dan pindahannya bertanda "perlu dicocokkan" sampai merek itu dihitung di Stok › Cocokkan — tidak ada angka yang ditulis diam-diam.</div>
      <div class="tombol-baris rapat">${TM.boleh ? h`<div class="kaca-btn" data-aksi="tandaiMasuk">Catat barang masuk dulu</div>` : h`<div class="kaca-btn mati" data-aksi="tombolMati" data-kal="${TM.kalimat}">Catat barang masuk dulu</div>`}<div class="kaca-btn awas" data-aksi="tandaiTulis">TANDAI UNTUK DICOCOKKAN</div><div class="kaca-btn putus" data-aksi="tandaiBatal">batal</div></div></div>`;
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
        <div><div class="ket">Isi satu takar / serok (kg)</div><input class="ketik-nama" id="aturTakar" type="text" inputmode="decimal" value="${d.takar}" data-ketik="aturTakar"></div>
        <div><div class="ket">Susut takar wajar per wadah per hari (kg) — dipakai saat cocokkan wadah</div><input class="ketik-nama" id="aturSusut" type="text" inputmode="decimal" value="${d.susut}" data-ketik="aturSusut"></div>
        <div><div class="ket">Disisihkan ke karung wadah saat tutup toko (kg)</div><input class="ketik-nama" id="aturSisih" type="text" inputmode="decimal" value="${d.sisih}" data-ketik="aturSisih"></div></div></div>
      ${(() => { const kgl = d.kgl || { bawaan: '', merek: {} }; const bawaanKini = L.kgPerLiterBawaan(); const langsung = WB.wbLiteranLangsung().daftar.filter((m) => d.daftar.indexOf(m) < 0); const merek = d.daftar.concat(langsung);
        const contoh = (n) => '10 L = ' + DESIMAL(Math.round(n * 10 * 100) / 100) + ' kg';
        return h`<div class="kartu" data-k="atur-kg-liter" style="gap: 8px;"><div class="label">Berat 1 liter (kg) · dipakai menghitung stok & modal literan</div>
        <div class="ket">1 liter beras ±0,8 kg (1,8 kg itu satu takar/serok, diatur di atas). Kosong = ikut angka bawaan. Berlaku untuk jualan SESUDAH disimpan — nota lama tidak berubah.</div>
        <div class="ps-form dua"><div><div class="ket">Bawaan semua merek · sekarang ${DESIMAL(bawaanKini)} kg (${contoh(bawaanKini)})</div><input class="ketik-nama" id="aturKglBawaan" type="text" inputmode="decimal" placeholder="${DESIMAL(bawaanKini)}" value="${kgl.bawaan}" data-ketik="aturKgl"></div>
        ${merek.map((m) => h`<div data-k="kgl-${m}"><div class="ket">${m} · sekarang ${DESIMAL(L.kgPerLiter(m))} kg</div><input class="ketik-nama" id="aturKgl-${m}" type="text" inputmode="decimal" placeholder="ikut bawaan" value="${kgl.merek[m] || ''}" data-ketik="aturKgl" data-merk="${m}"></div>`)}</div></div>`; })()}
      ${(() => { const mk = d.merekKarung || L.aturWadah().merekKarung; return h`<div class="kartu" data-k="atur-merek-karung" style="gap: 8px;"><div class="label">Nama wadah yang juga MEREK KARUNG pemasok</div>
        <div class="ket">Nama wadah lain (mis. IR64 Apex) = kelas mutu: tidak bisa dipakai di barang masuk — beras datang dibukukan per merek di karungnya. Yang ditandai di sini (mis. Angsa) boleh datang atas nama itu.</div>
        <div class="tombol-baris rapat">${d.daftar.map((m) => h`<div class="kaca-btn ${mk.indexOf(m) >= 0 ? 'aktif' : 'putus'}" data-aksi="aturMerekKarung" data-merk="${m}">${mk.indexOf(m) >= 0 ? '✓ ' : ''}${m}</div>`)}</div></div>`; })()}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN SUSUNAN &amp; ATURAN</div></div>
    </section>`;
  }

  // ---------- BARANG MASUK (ST1): satu kedatangan = pemasok · tanggal · baris nama × karung × harga/kg · cara bayar · upah bongkar ----------
  // paket KPI laba (owner 24 Nov 2026, butir 12): batas HPP per kg per merek — owner saja (aturanToko/catatStok.hppMaksPerKg, dibaca tablet untuk menandai)
  function gambarAturHpp(s) {
    if (bukanOwner(opsi.akun ? opsi.akun() : null)) return '';
    const a = s.aturHpp; const D = C.ckDaftarHppMaks(); const n = D.filter((x) => x.batas > 0).length;
    if (!a) return h`<div class="ket tautan" data-aksi="hppBuka" data-k="hpp-buka">Batas HPP per kg per merek · ${n ? n + ' merek berbatas' : 'belum diatur'} — kedatangan yang lewat ditandai ›</div>`;
    return h`<div class="kartu" data-k="atur-hpp" style="gap: 6px;"><div class="label">Batas HPP per kg per merek · angka owner</div>
      <div class="ket">HPP = harga beli + bongkar dibagi menurut kg (rumus mesin). Lewat = LEBIH dari batas (sama persis = tidak ditandai). Kosong = tanpa batas. Hanya tanda — kedatangan tetap boleh dicatat.</div>
      ${D.map((x) => h`<div class="ps-form dua" data-k="hpp-${x.merek}"><div><div style="font-weight: 600;">${x.merek}</div><div class="ket">modal sekarang ${x.modal ? RP(Math.round(x.modal)) : '—'}/kg · beli terakhir ${x.beli ? RP(Math.round(x.beli)) : '—'}/kg</div></div><input class="ketik-nama" type="text" inputmode="numeric" placeholder="tanpa batas" value="${a[x.merek] !== undefined ? a[x.merek] : x.batas ? String(x.batas) : ''}" data-ketik="hppKetik" data-merek="${x.merek}"></div>`)}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="hppBuka">batal</div><div class="kaca-btn aktif emas" data-aksi="hppSimpan">SIMPAN BATAS</div></div></div>`;
  }
  function gambarAturC(s) {
    const a = s.aturC; if (!a) return '';
    return h`<div class="kartu" data-k="atur-catat" style="gap: 8px;"><div class="label">Aturan pencatatan · angka owner</div><div class="ps-form dua">
      <div><div class="ket">Satu mobil minimal (karung)</div><input class="ketik-nama" id="acMin" type="text" inputmode="numeric" value="${a.minKarung}" data-ketik="cKetikAtur" data-kolom="minKarung"></div>
      <div><div class="ket">Tempo bon pemasok (hari)</div><input class="ketik-nama" id="acTempo" type="text" inputmode="numeric" value="${a.tempoHari}" data-ketik="cKetikAtur" data-kolom="tempoHari"></div>
      <div><div class="ket">Selisih wajar cocokkan (%)</div><input class="ketik-nama" id="acBatas" type="text" inputmode="decimal" value="${a.batasSelisih}" data-ketik="cKetikAtur" data-kolom="batasSelisih"></div>
      <div><div class="ket">Stok bertambah tanpa pembelian, ditanya di atas (Rp)</div><input class="ketik-nama" id="acAmbang" type="text" inputmode="numeric" value="${a.ambangSusutPositif}" data-ketik="cKetikAtur" data-kolom="ambangSusutPositif"></div>
      <div><div class="ket">Harga beli beda dari modal lebih dari (%) → ditanya "sama barangnya / beda mutu"</div><input class="ketik-nama" id="acVarian" type="text" inputmode="decimal" value="${a.batasVarian}" data-ketik="cKetikAtur" data-kolom="batasVarian"></div>
      <div><div class="ket">Mutu saat terima: kadar air maksimal (%) — di atasnya ditandai AWAS</div><input class="ketik-nama" id="acAir" type="text" inputmode="decimal" value="${a.kadarAirMaks}" data-ketik="cKetikAtur" data-kolom="kadarAirMaks"></div>
      <div><div class="ket">Mutu saat terima: butir patah maksimal (%) — di atasnya ditandai AWAS</div><input class="ketik-nama" id="acPatah" type="text" inputmode="decimal" value="${a.patahMaks}" data-ketik="cKetikAtur" data-kolom="patahMaks"></div></div>
      ${(() => { const mb = C.aturCatat().mutuBawaan; return mb.kadarAirMaks || mb.patahMaks ? h`<div class="ket" data-k="ac-mutu-bawaan">${[mb.kadarAirMaks ? 'kadar air ' + C.ATUR_CATAT_BAWAAN.kadarAirMaks + ' %' : '', mb.patahMaks ? 'butir patah ' + C.ATUR_CATAT_BAWAAN.patahMaks + ' %' : ''].filter(Boolean).join(' & ')} = angka bawaan (perkiraan) — bisa diubah di sini.</div>` : ''; })()}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturC">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturC">SIMPAN ATURAN</div></div></div>`;
  }
  // ---------- TIMBANG & MUTU SAAT TERIMA (paket brief 9 Okt, butir 6 & 7): per baris, OPSIONAL (keputusan owner) — dilipat sampai dibuka / terisi ----------
  // catatan pemeriksaan saja: kg buku, stok, modal, HPP, dan bon tetap menurut nota; kosong = belum ditimbang / tidak dicek (bukan selisih 0)
  const tmD = (n) => DESIMAL(Math.round(n * 10) / 10);
  const tmBawaanTeks = (a) => { const x = [a.mutuBawaan.kadarAirMaks ? 'kadar air ' + tmD(a.kadarAirMaks) + ' %' : '', a.mutuBawaan.patahMaks ? 'butir patah ' + tmD(a.patahMaks) + ' %' : ''].filter(Boolean);
    return x.length ? ' Ambang ' + x.join(' & ') + ' = angka bawaan (perkiraan) — bisa diubah di Atur di bawah.' : ' Ambang = setelan owner (Atur di bawah).'; };
  function gambarCekMasuk(b, isi, i, a) {
    const c = b.cek;
    // Tahap 6 (owner 25 Nov 2026): baris kedatangan yang ikut timbang WAJIB ditimbang — isiannya selalu terbuka (tidak bisa dilipat)
    if (!c.ada && !isi.cekBuka && !b.ikutTimbang) return h`<div class="ket tautan" data-k="mc-buka-${i}" data-aksi="mPilih" data-kolom="cekBuka" data-i="${i}" data-nilai="1">+ timbang &amp; cek mutu saat terima (boleh kosong)</div>`;
    const pil = (kolom, daftar) => h`<div class="jalur rapat" data-k="mc-${kolom}-${i}"><div class="seg ${!isi[kolom] ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="${kolom}" data-i="${i}" data-nilai="">tidak dicek</div>${daftar.map(([id, nm]) => h`<div class="seg ${isi[kolom] === id ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="${kolom}" data-i="${i}" data-nilai="${id}">${nm}</div>`)}</div>`;
    return h`<div class="pita-info ${c.masalah || c.awas.length ? 'awas' : ''}" data-k="mc-${i}" style="display: flex; flex-direction: column; gap: 6px;">
      <div class="ps-form dua"><div><div class="ket">Berat timbang seluruh baris (kg)${b.ikutTimbang ? h` <b class="awas-teks">WAJIB</b> (atau sampel di bawah)` : ''}${b.kgNota > 0 ? ' · nota ' + b.jumlahKarung + ' × ' + b.beratKarung + ' = ' + tmD(b.kgNota) + ' kg' : ''}</div><input class="ketik-nama" id="mTimbang${i}" type="text" inputmode="decimal" placeholder="belum ditimbang" value="${isi.timbangKg || ''}" data-ketik="mKetik" data-kolom="timbangKg" data-i="${i}"></div>
        <div class="ket ${c.selisihKg !== null && c.selisihKg < 0 ? 'awas-teks' : ''}" style="align-self: end;" data-k="mc-tb-${i}">${c.masalah ? '' : c.timbangTeks}${c.nilaiKurang ? ' ≈ ' + RP(c.nilaiKurang) + (b.ikutTimbang ? ' dibayar tanpa barangnya (modal per kg naik)' : ' (perkiraan nilai, tidak dibukukan)') : ''}${b.ikutTimbang && b.kgTerima !== null && !b.masalah ? h`<br><b data-k="mc-buku-${i}">dibukukan ${tmD(b.totalKg)} kg</b> (nota ${tmD(b.kgNota)} kg · uang tetap ${RP(b.subtotalHarga)})` : ''}</div></div>
      <div class="ps-form dua" data-k="mc-sampel-${i}"><div><div class="ket">Atau timbang SAMPEL: berapa karung ditimbang</div><input class="ketik-nama" id="mSampelN${i}" type="text" inputmode="numeric" placeholder="mis. 5" value="${isi.sampelKarung || ''}" data-ketik="mKetik" data-kolom="sampelKarung" data-i="${i}"></div>
        <div><div class="ket">Berat semua karung sampel itu (kg)${c.sampel ? ' · rata-rata ' + tmD(c.sampel.rata) + ' kg per karung' + (c.sampel.kurangPerKarung ? (c.sampel.kurangPerKarung > 0 ? ', kurang ' : ', lebih ') + tmD(Math.abs(c.sampel.kurangPerKarung)) + ' kg dari label' : '') : ''}</div><input class="ketik-nama" id="mSampelKg${i}" type="text" inputmode="decimal" placeholder="mis. 247,5" value="${isi.sampelKg || ''}" data-ketik="mKetik" data-kolom="sampelKg" data-i="${i}"></div></div>
      ${c.sampel && c.sampel.lebihDariBaris ? h`<div class="ket awas-teks">Karung sampel lebih banyak dari karung baris ini — periksa angkanya.</div>` : ''}
      <div class="ps-form dua"><div><div class="ket">Kadar air (%) · AWAS di atas ${tmD(a.kadarAirMaks)}</div><input class="ketik-nama" id="mAir${i}" type="text" inputmode="decimal" placeholder="tidak dicek" value="${isi.kadarAir || ''}" data-ketik="mKetik" data-kolom="kadarAir" data-i="${i}"></div>
        <div><div class="ket">Butir patah (%) · AWAS di atas ${tmD(a.patahMaks)}</div><input class="ketik-nama" id="mPatah${i}" type="text" inputmode="decimal" placeholder="tidak dicek" value="${isi.butirPatah || ''}" data-ketik="mKetik" data-kolom="butirPatah" data-i="${i}"></div></div>
      <div data-k="mc-kelas-${i}"><div class="ket">Kelas mutu baris ini (untuk menilai rincian di bawah)</div><div class="jalur rapat"><div class="seg ${!isi.kelasMutu ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="kelasMutu" data-i="${i}" data-nilai="">belum dipilih</div>${C.TM_KELAS.map(([id, nm]) => h`<div class="seg ${isi.kelasMutu === id ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="kelasMutu" data-i="${i}" data-nilai="${id}">${nm}</div>`)}</div></div>
      <div class="ps-form dua" data-k="mc-rinci-${i}">${C.TM_RINCI.slice(1).map(([id, nm, sat]) => { const maks = isi.kelasMutu ? a.mutuKelas[isi.kelasMutu][id] : 0; return h`<div><div class="ket">${nm} (${sat})${maks ? ' · AWAS di atas ' + tmD(maks) : ''}</div><input class="ketik-nama" id="mR-${id}-${i}" type="text" inputmode="decimal" placeholder="tidak dicek" value="${isi[id] || ''}" data-ketik="mKetik" data-kolom="${id}" data-i="${i}"></div>`; })}</div>
      <div><div class="ket">Kutu</div>${pil('kutu', C.TM_KUTU)}</div>
      <div><div class="ket">Bau</div>${pil('bau', C.TM_BAU)}</div>
      <div class="ket ${c.awas.length ? 'awas-teks' : ''}" data-k="mc-mutu-${i}">${c.masalah ? '' : c.awas.length ? 'AWAS: ' + c.awas.join(' · ') : 'mutu: ' + c.mutuTeks}</div>
      <div class="ket" style="font-size: 10.5px;">${b.ikutTimbang ? 'Stok dibukukan dari HASIL TIMBANG ini (kurang maupun lebih dari nota); uang ke pemasok tetap sesuai nota, jadi modal per kg ikut naik / turun sedikit. Mutu = catatan pemeriksaan saja.' : 'Catatan pemeriksaan saja — kg di buku, stok, modal, HPP, dan bon tetap menurut nota. Kosong = belum ditimbang / tidak dicek.'}${tmBawaanTeks(a)}${!c.ada && !b.ikutTimbang ? h` <span class="tautan" data-aksi="mPilih" data-kolom="cekBuka" data-i="${i}" data-nilai="">lipat</span>` : ''}</div></div>`;
  }
  // Tahap 6 (owner 25 Nov 2026, butir 5): kedatangan LAMA yang sudah ditimbang tapi bukunya masih ikut nota → owner mengetuk sendiri pembetulannya
  // sesudah melihat angkanya (C.hitungBetulTimbang); uang tetap, nota jual yang sudah tercatat tidak diubah. Koreksi kedatangan = kartu kedatangan itu saja.
  function gambarBetulTimbang(s, idKoreksi) {
    const daftar = idKoreksi ? [C.hitungBetulTimbang(idKoreksi)].filter((x) => !x.tolak) : C.calonBetulTimbang(3); if (!daftar.length) return '';
    const KG = (n) => DESIMAL(Math.round(n * 100) / 100) + ' kg';
    return h`<div class="kartu" data-k="betul-timbang" style="gap: 8px;"><div class="label">Stok ikut timbang · kedatangan lama yang bukunya masih ikut nota</div>
      ${daftar.map((H) => h`<div data-k="bt-${H.id}" style="display: flex; flex-direction: column; gap: 6px;">
        <div><b>${H.pemasok}</b> · ${tanggalPendek(H.tanggal)} · ${H.cara === 'utang' ? 'bon' : 'tunai'} · buku ${KG(H.kgLama)} → <b>${KG(H.kgBaru)}</b> (${H.selisih < 0 ? 'turun ' : 'naik '}${KG(Math.abs(H.selisih))}) · uang <b>${RP(H.nilai)}</b> tetap</div>
        ${H.baris.filter((x) => Math.abs(x.selisih) > 0.004).map((x) => h`<div class="ket" data-k="bt-${H.id}-${x.merk}">${x.merk}: nota ${KG(x.kgNota)} · buku ${KG(x.kgLama)} → <b>${KG(x.kgBaru)}</b>${x.perkiraan ? ' (perkiraan timbang sampel)' : ' (timbang)'} · modal ${RP(Math.round(x.modalLama))} → ${RP(Math.round(x.modalBaru))}/kg · sisa buku sekarang ${KG(x.buku)} → ${KG(x.bukuSesudah)}</div>`)}
        ${H.minus.length ? h`<div class="ket awas-teks">Buku jadi minus: ${H.minus.map((x) => x.merk + ' ' + KG(x.kg)).join(', ')} — karungnya sudah terjual sebagai 50 kg; cocokkan sesudahnya.</div>` : ''}
        <div class="ket" style="font-size: 10.5px;">Nota jual yang sudah tercatat tidak diubah. Karung kedatangan ini yang dijual sesudahnya memotong berat aslinya; layar, harga, dan struk tetap "50 kg".</div>
        <div class="kaca-btn ${s.btYakin === String(H.id) ? 'awas' : 'aktif emas'}" data-aksi="btTimbang" data-id="${H.id}" data-k="bt-tombol-${H.id}">${s.btYakin === String(H.id) ? 'YAKIN — BETULKAN JADI ' + KG(H.kgBaru) + ', UANG TETAP' : 'BETULKAN JADI KG TIMBANG'}</div></div>`)}</div>`;
  }
  // rekap per pemasok (C.rekapTimbangMutu — fungsi yang sama kelak dipasang di kartu pemasok Harga & Pemasok)
  function gambarRekapTimbang() {
    const R = C.rekapTimbangMutu(); const T = R.total; const KG = (n) => tmD(n) + ' kg';
    const sel = (kg, pct) => (kg === 0 ? 'pas 0 kg' : (kg > 0 ? '+' : '−') + KG(Math.abs(kg))) + (pct !== null && kg !== 0 ? ' (' + (pct > 0 ? '+' : '−') + tmD(Math.abs(pct)) + ' %)' : '');
    return h`<div class="kartu" data-k="timbang-mutu" style="gap: 6px;"><div class="label">Timbang &amp; mutu kedatangan · per pemasok</div>
      ${R.pemasok.length ? R.pemasok.map((p) => h`<div class="jawab" data-k="tmp-${p.pemasok}"><span class="kiri"><span class="nm">${p.pemasok}</span>
          <span class="w">ditimbang ${p.ditimbang} dari ${p.kedatangan} kedatangan${p.sebagian ? ' · ' + p.sebagian + ' sebagian' : ''}${p.belumTimbang ? ' · ' + p.belumTimbang + ' belum ditimbang' : ''}</span>
          <span class="w">${p.barisTimbang ? 'selisih timbang − nota ' + sel(p.selisihKg, p.persenRata) + ' dari ' + KG(p.kgNota) + ' nota yang ditimbang' + (p.kgKurang && p.kgLebih ? ' (kurang ' + KG(p.kgKurang) + ', lebih ' + KG(p.kgLebih) + ')' : '') : 'belum ada yang ditimbang'}</span>
          <span class="w ${p.kedatanganAwas ? 'awas-teks' : ''}">mutu dicek ${p.dicek} dari ${p.kedatangan} kedatangan${p.kedatanganAwas ? ' · ' + p.kedatanganAwas + ' kedatangan AWAS' : ''}</span>
          <span class="batang"><span class="isi-batang" style="transform: scaleX(${p.kedatangan ? Math.round(p.ditimbang / p.kedatangan * 1000) / 1000 : 0});"></span></span></span>
        <span class="kanan"><span class="n">${p.barisTimbang ? (p.kgKurang ? '−' + KG(p.kgKurang) : 'tidak kurang') : '—'}</span><span class="w">${p.barisTimbang ? h`${p.nilaiKurang ? h`≈ <span ${mentah('data-gulir="' + p.nilaiKurang + '"')}>${RP(p.nilaiKurang)}</span>` : 'Rp0'} kurang` : 'belum ditimbang'}</span></span></div>
        ${p.awas.slice(0, 5).map((x) => h`<div class="ket awas-teks" data-k="tma-${x.batchId}-${x.merk}">AWAS ${tanggalPendek(x.tanggal)} · ${x.merk}: ${x.alasan.join(', ')}</div>`)}${p.awas.length > 5 ? h`<div class="ket">+${p.awas.length - 5} baris AWAS lain dari ${p.pemasok}</div>` : ''}`) : h`<div class="ket">Belum ada kedatangan dari pemasok di buku.</div>`}
      ${R.pemasok.length > 1 ? h`<div class="ket" data-k="tmp-total">Semua pemasok: ditimbang ${T.ditimbang} dari ${T.kedatangan} kedatangan${T.sebagian ? ' (' + T.sebagian + ' sebagian)' : ''} · ${T.barisTimbang ? 'selisih ' + sel(T.selisihKg, T.persenRata) + (T.nilaiKurang ? ' · kurang ≈ ' + RP(T.nilaiKurang) : '') : 'belum ada yang ditimbang'} · mutu AWAS ${T.kedatanganAwas} kedatangan</div>` : ''}
      ${R.lewatBal ? h`<div class="ket">${R.lewatBal} kedatangan isinya baris bal (beli jadi) saja — tidak ditimbang dari sini, tidak ikut hitungan.</div>` : ''}
      <div class="ket" style="font-size: 10.5px;">Kosong = belum ditimbang / tidak dicek (bukan selisih 0). Selisih = berat timbang − kg nota, rata-rata % ditimbang menurut kg. Nilai kg kurang = kg kurang × harga beli per kg barisnya — perkiraan nilai, tidak dibukukan: stok, modal, HPP, dan bon tetap menurut nota. AWAS = kadar air di atas ${tmD(R.atur.kadarAirMaks)} %, butir patah di atas ${tmD(R.atur.patahMaks)} %, ada kutu, atau bau tidak normal.${tmBawaanTeks(R.atur)}</div></div>`;
  }
  function gambarMasuk(s) {
    if (bukanOwner(opsi.akun ? opsi.akun() : null)) return gambarMasukTablet(s);
    const d = s.masuk || C.drafMasukKosong(waktu()); const hm = C.hitungMasuk(d); const a = C.aturCatat(); const koreksi = !!d.id; const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const pemasok = C.calonPemasok().slice(0, 6); const merk = C.calonMerkMasuk();
    return h`<section class="stok-masuk" data-k="masuk">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">${koreksi ? 'Koreksi kedatangan' : 'Barang masuk'}</div><div class="ket">${koreksi ? d.pemasok + ' · ' + tanggalPendek(d.tanggal) : 'satu mobil = satu catatan · harga per kg + upah bongkar jadi modal tiap nama'}</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      ${koreksi ? kartuTerima(d.id, { akun: opsi.akun ? opsi.akun() : null }) : s.tbm ? kartuTerima(s.tbm.id, { akun: opsi.akun ? opsi.akun() : null, tutup: true }) : ''}
      ${!koreksi && s.tbm ? kartuLabelMasuk(s.tbm.id, s) : ''}
      ${kartuFotoNota(koreksi ? d.id : s.tbm ? s.tbm.id : null, { s, akun: opsi.akun ? opsi.akun() : null })}
      ${gambarBetulTimbang(s, koreksi ? d.id : null)}
      ${(s.varianTawar || []).length ? h`<div class="kartu" data-k="varian-tawar" style="gap: 8px;"><div class="label">Harga jual varian · belum ada harganya</div>
        ${s.varianTawar.map((x) => { const usul = VR.vrUsulHarga(x.modalKg, aturHarga()); return h`<div data-k="vt-${x.merk}" style="display: flex; flex-direction: column; gap: 6px;"><div><b>${x.merk}</b> · modal ${RP(Math.round(x.modalKg))}/kg (dari kedatangan ini) · usul ${RP(usul)}/kg = modal + target untung katalog</div>
          <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="vr-${x.merk}" type="text" inputmode="numeric" placeholder="${usul}" value="${(s.vrKetik || {})[x.merk] || ''}" data-ketik="vrKetik" data-merk="${x.merk}">
            <div class="kaca-btn aktif emas" data-aksi="vrTerbit" data-merk="${x.merk}" data-usul="${usul}">${s.vrYakin ? 'YAKIN — terbitkan di bawah modal' : 'TERBITKAN HARGA ' + x.merk}</div><div class="kaca-btn putus" data-aksi="vrNanti" data-merk="${x.merk}">nanti</div></div></div>`; })}
        <div class="ket" style="font-size: 11px;">Terbit = katalog per kg nama ini saja (rak Jual & katalog HP kasir ikut); draf harga lain tidak ikut terbit.</div></div>` : ''}
      ${koreksi ? (() => { const bb = C.ckBayarBonId(d.id); return bb.dibayar <= 0 && bb.dibayarMesin > 0 ? h`<div class="pita-info" data-k="mk-terbayar">Bon ini sudah terbayar ${RP(bb.dibayarMesin)} lewat aliran pembayaran pemasok ini — tanggal datangnya tidak bisa diubah.</div>` : bb.dibayar > 0 ? h`<div class="pita-info emas" data-k="mk-dibayar"><b>Bon ini sudah dibayar ${RP(bb.dibayar)}</b>${bb.bayar.length ? ' (' + bb.bayar.map((x) => x.tanggal ? tanggalPendek(x.tanggal) : 'tanpa tanggal').join(', ') + ')' : ''}. Cara bayar, nama pemasok, dan tanggal datangnya tidak bisa diubah; nilai beras${hm.nilaiBal ? ' + baris bal' : ''} tidak boleh di bawah ${RP(bb.dibayar)}; kedatangan ini tidak bisa dihapus — supaya pembayarannya tidak melunasi bon lain tanpa uang.</div>` : ''; })() : ''}
      <div class="kartu" data-k="masuk-kepala" style="gap: 8px;">
        <div class="ps-form dua"><div><div class="ket">Tanggal datang</div><input class="ketik-nama" id="mTanggal" type="date" value="${d.tanggal}" data-ketik="mKetik" data-kolom="tanggal"></div>
          <div><div class="ket">Upah bongkar (Rp, tunai)</div><input class="ketik-nama" id="mBongkar" type="text" inputmode="numeric" placeholder="0" value="${d.bongkar}" data-ketik="mKetik" data-kolom="bongkar"></div></div>
        ${gambarTarifTanda(d)}
        <div class="ps-form dua" data-k="masuk-ongkir"><div><div class="ket">Ongkos kirim supir pemasok (Rp, tunai)</div><input class="ketik-nama" id="mOngkir" type="text" inputmode="numeric" placeholder="0" value="${d.ongkir || ''}" data-ketik="mKetik" data-kolom="ongkir"></div>
          <div class="ket" style="align-self: end;">Masuk modal beras bersama upah bongkar (dibagi per kg) dan keluar dari laci hari itu.</div></div>
        <div data-k="masuk-bebas"><div class="ket">Catatan untuk pemasok (bebas, boleh kosong) — ikut tercetak di surat untuk pemasok</div><textarea class="ketik-nama" id="mBebas" rows="2" maxlength="${C.CP_MAKS.bebas}" placeholder="mis. 2 karung sobek, minta diganti di kiriman berikut" data-ketik="mKetik" data-kolom="catatanBebas">${d.catatanBebas || ''}</textarea></div>
        <div><div class="ket">Pemasok</div><input class="ketik-nama" id="mPemasok" type="text" placeholder="nama pemasok" value="${d.pemasok}" data-ketik="mKetik" data-kolom="pemasok">
          ${pemasok.length ? h`<div class="tombol-baris rapat" data-k="calon-pemasok">${pemasok.map((p) => h`<div class="kaca-btn kecil ${d.pemasok === p ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="pemasok" data-nilai="${p}">${p}</div>`)}</div>` : ''}</div>
        <div class="jalur" data-k="cara-bayar"><div class="seg ${d.caraBayar !== 'utang' ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="caraBayar" data-nilai="tunai">Tunai — keluar laci hari ini</div><div class="seg ${d.caraBayar === 'utang' ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="caraBayar" data-nilai="utang">Bon pemasok</div></div>
        ${d.caraBayar === 'utang' && a.tempoHari ? h`<div class="ket">bon jatuh tempo ${a.tempoHari} hari dari tanggal datang (setelan owner) — masuk buku bon pemasok</div>` : ''}
      </div>
      ${hm.baris.map((b, i) => h`<div class="kartu baris-masuk ${b.terisi && b.masalah ? 'awas' : ''}" data-k="mb-${i}" style="gap: 6px;">
        <div class="label">Baris ${i + 1}${b.kemasan ? ' · KEMASAN JADI' + (b.kemasanSah ? ' · ' + b.jumlahKarung + ' × ' + UK(b.beratKarung) + ' kg · ' + RP(b.subtotalHarga) : '') : b.sah ? ' · ' + KG(b.totalKg) + ' · ' + RP(b.subtotalHarga) : ''}</div>
        <input class="ketik-nama" id="mMerk${i}" type="text" placeholder="${b.kemasan ? 'nama kemasan (yang tertulis di bungkusnya)' : 'nama beras / karung'}" value="${d.baris[i].merk}" data-ketik="mKetik" data-kolom="merk" data-i="${i}">
        ${!b.merk ? h`<div class="tombol-baris rapat" data-k="calon-merk-${i}">${(b.kemasan ? C.kjCalonNama() : merk).slice(0, 8).map((m) => h`<div class="kaca-btn kecil" data-aksi="mPilih" data-kolom="merk" data-i="${i}" data-nilai="${m}">${m}</div>`)}</div>` : ''}
        <div class="ps-form tiga"><div><div class="ket">${b.kemasan ? 'Jumlah kemasan' : 'Karung'}</div><input class="ketik-nama" id="mJml${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].jumlahKarung}" data-ketik="mKetik" data-kolom="jumlahKarung" data-i="${i}"></div>
          <div><div class="ket">Harga / kg${b.lalu ? ' · lalu ' + RP(b.lalu.harga) + (b.lalu.tanggalTeks ? ' · ' + b.lalu.tanggalTeks : '') + (b.lalu.pemasok && !b.lalu.fondasi ? ' · ' + b.lalu.pemasok : b.lalu.fondasi ? ' · stok awal' : '') : b.hargaLalu ? ' · lalu ' + RP(b.hargaLalu) : ''}</div><input class="ketik-nama" id="mHarga${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].hargaPerKg}" data-ketik="mKetik" data-kolom="hargaPerKg" data-i="${i}"></div>
          <div><div class="ket">${b.kemasan ? 'Isi per kemasan' : 'Isi karung'}</div>${pilUkuran(d.baris[i], i)}</div></div>
        ${b.arahVarian ? h`<div class="ket ${b.arahVarian.arah === 'naik' ? 'awas-teks' : ''}" data-k="mav-${i}">Varian ${b.arahVarian.teks}</div>` : ''}
        ${koreksi ? '' : h`<div class="ket tautan" data-k="mkj-${i}" data-aksi="mPilih" data-kolom="masuk" data-i="${i}" data-nilai="${b.kemasan ? '' : 'kemasan'}">${b.kemasan ? 'KEMASAN JADI — masuk buku Kemasan, dijual per kemasan (ketuk untuk kembali ke beras per kg)' : 'karung kecil yang dijual utuh per kemasan? jadikan baris ini KEMASAN JADI'}</div>`}
        ${koreksi || b.kemasan || d.baris[i].ditolak ? '' : pilPotong(b, d.baris[i], i)}
        ${koreksi || b.kemasan ? '' : pilTolak(d.baris[i], i)}
        ${b.kemasan ? '' : gambarCekMasuk(b, d.baris[i], i, a)}
        ${b.sah && (b.vr.perlu || b.vr.arsip || b.varian) ? h`<div class="pita-info ${b.varian ? '' : 'emas'}" data-k="mv-${i}">${b.vr.arsip ? b.merk + ' sudah DIARSIPKAN (habis, tidak tampil di Jual & katalog). Barang ini sama dengan ' + b.merk + ' yang dulu?' + (b.vr.perlu ? ' Harga belinya beda ' + DESIMAL(b.vr.beda) + ' % dari modal lama.' : '') : b.vr.perlu ? 'Harga beli ' + RP(b.hargaPerKg) + '/kg beda ' + DESIMAL(b.vr.beda) + ' % dari modal ' + b.merk + ' ' + RP(Math.round(b.vr.modal)) + '/kg (batas ' + DESIMAL(b.vr.batas) + ' %) — barangnya sama?' : 'Baris ini ditandai beda mutu.'}
          <div class="tombol-baris rapat"><div class="kaca-btn ${b.varian === 'sama' ? 'aktif' : ''}" data-aksi="mVarian" data-i="${i}" data-v="sama">${b.vr.arsip ? 'Pulihkan ' + b.merk + ' — sama barangnya' : 'Sama barangnya — gabung'}</div><div class="kaca-btn ${b.varian === 'beda' ? 'aktif' : ''}" data-aksi="mVarian" data-i="${i}" data-v="beda">Beda mutu — jadi varian</div></div>
          ${b.varian === 'beda' ? h`<input class="ketik-nama" id="mMutu${i}" type="text" placeholder="nama mutu, mis. Premium (kosong = tanggal datang)" value="${d.baris[i].namaMutu || ''}" data-ketik="mKetik" data-kolom="namaMutu" data-i="${i}">
            <div class="ket">dicatat sebagai <b>${b.merkSimpan}</b> — kolam ${b.merk} yang lama tidak disentuh (dijual sampai habis); jenis beras ikut ${b.merk}; harga jualnya ditawarkan sesudah disimpan</div>` : b.varian === 'sama' ? h`<div class="ket">digabung ke ${b.merk}: modal per kg dirata-rata dengan stok lama, seperti biasa</div>` : ''}</div>` : ''}
        ${koreksi && b.merkPemasok ? h`<div class="pita-info" data-k="mp-${i}">dicatat sebagai <b>${b.merk}</b> · merek pemasok <b>${b.merkPemasok}</b> — keterangan di kedatangan ini, bukan buku sendiri${b.merkPemasok !== String(d.baris[i].merkPemasok || '') ? ' (diambil dari nama lama baris ini)' : ''}</div>` : ''}
        ${b.saranVarian && b.saranVarian.length ? h`<div class="pita-info emas" data-k="msv-${i}"><div><b>${b.merkKetik}</b> sudah dicatat sebagai <b>${b.saranVarian.map((v) => v.nama).join(' / ')}</b> — pakai itu?</div>
          <div class="tombol-baris rapat" data-k="msv-pil-${i}">${b.saranVarian.map((v) => h`<div class="kaca-btn aktif emas" data-aksi="mPakaiVarian" data-i="${i}" data-merk="${v.nama}">pakai ${v.nama}${v.bukuKg > 0.004 ? ' · buku ' + KG(v.bukuKg) : ''}</div>`)}</div>
          <div class="ket">Satu ketukan: stoknya masuk buku yang sama. Kalau memang barang lain, biarkan — baris ini jadi nama baru ${b.merkKetik}.</div></div>` : ''}
        ${b.varianInduk && b.varianInduk.length ? h`<div class="pita-info emas" data-k="mvi-${i}"><div><b>${b.merk}</b> punya varian <b>${b.varianInduk.map((v) => v.nama).join(' / ')}</b> — karung yang datang ini yang mana?</div>
          <div class="tombol-baris rapat" data-k="mvi-pil-${i}">${b.varianInduk.map((v) => h`<div class="kaca-btn aktif emas" data-aksi="mPakaiVarian" data-i="${i}" data-merk="${v.nama}">masuk ${v.nama}${v.bukuKg > 0.004 ? ' · isi buku ' + KG(v.bukuKg) : ''}</div>`)}</div>
          <div class="ket">Satu ketukan: karungnya masuk buku varian itu. Kalau memang ${b.merk} biasa, biarkan — masuk buku ${b.merk}.</div></div>` : ''}
        ${b.baru ? h`<div class="pita-info ${b.kelas || b.kelasPilih ? '' : 'emas'}" data-k="mk-${i}">${b.keSendiri ? h`Merek baru <b>${b.merkKetik}</b> dicatat sebagai <b>${b.merk}</b> · merek pemasok ${b.merkKetik}${b.lalu ? ' · lalu ' + RP(b.lalu.harga) + ' (' + b.lalu.tanggalTeks + (b.lalu.pemasok && !b.lalu.fondasi ? ' · ' + b.lalu.pemasok : '') + ')' : ' · belum ada harga lalu'}` : b.kelas ? h`Merek baru <b>${b.merkKetik}</b> · kelas <b>${b.kelas}</b>${b.kelasAsal === 'tebakan' ? ' (tebakan — ketuk kelas lain kalau keliru)' : ''}${b.laluKelas ? ' · lalu ' + RP(b.laluKelas.harga) + ' (' + b.laluKelas.merk + (b.laluKelas.merkPemasok ? ' (' + b.laluKelas.merkPemasok + ')' : '') + ' · ' + b.laluKelas.tanggalTeks + ' · ' + b.laluKelas.pemasok + ')' + (b.laluKelas.lain.length ? ' · pemasok lain: ' + b.laluKelas.lain.map((x) => x.pemasok + ' ' + RP(x.harga) + ' (' + x.tanggalTeks + ')').join(', ') : '') : ' · kelas ini belum punya kedatangan nyata'}` : b.kelasPilih ? h`Merek baru <b>${b.merkKetik}</b> · tanpa kelas — harga lalunya nanti dari merek ini sendiri` : h`Merek baru <b>${b.merkKetik}</b> — kelas mana? (boleh tanpa kelas; simpan tidak menunggu jawaban ini)`}
          <div class="tombol-baris rapat" data-k="mk-pil-${i}">${b.calonKelas.map((c) => h`<div class="kaca-btn kecil ${b.kelas === c.nama ? 'aktif' : ''}" data-aksi="mKelas" data-i="${i}" data-kelas="${c.nama}">${c.nama}${c.jenis === 'sendiri' ? ' · buku' : ''}</div>`)}<div class="kaca-btn kecil ${b.kelasPilih && !b.kelas ? 'aktif' : ''}" data-aksi="mKelas" data-i="${i}" data-kelas="">tanpa kelas</div></div>
          ${b.kelasTanya ? h`<div class="ket awas-teks">${b.kelasTanya}</div>` : ''}</div>` : ''}
        ${b.sah && b.lewatHppMaks ? h`<div class="pita-info awas" data-k="m-hpp-${i}">HPP ${RP(Math.round(b.hppPerKg))}/kg LEWAT batas ${RP(b.hppMaks)}/kg — boleh dicatat, ditandai di Laporan & Dasbor</div>` : ''}
        <div class="ket ${b.terisi && b.masalah ? 'awas-teks' : ''}">${b.terisi && b.masalah ? b.masalah : b.kemasanSah ? 'modal ' + RP(Math.round(b.hppPerUnit)) + ' per kemasan (' + RP(Math.round(b.hppPerKg)) + '/kg' + (b.alokasiBongkar ? ', termasuk bongkar' + (hm.ongkir ? ' & ongkos kirim ' : ' ') + RP(b.alokasiBongkar) : '') + ') → buku Kemasan "' + b.merk + ' ' + UK(b.beratKarung) + ' kg" +' + b.jumlahKarung + ' · harga jualnya diatur di Harga' : b.kemasan ? 'isi nama kemasan, jumlah kemasan, dan harga beli per kg' : b.sah ? 'modal ' + RP(Math.round(b.hppPerKg)) + '/kg' + (b.alokasiBongkar ? ' (termasuk bongkar' + (hm.ongkir ? ' & ongkos kirim ' : ' ') + RP(b.alokasiBongkar) + ')' : '') + (b.hargaLalu && Math.abs(b.hargaPerKg - b.hargaLalu) / b.hargaLalu > 0.1 ? ' · beda ' + Math.round(Math.abs(b.hargaPerKg - b.hargaLalu) / b.hargaLalu * 100) + ' % dari harga lalu' : '') + (b.arah && b.arah.teks ? ' · ' + b.arah.teks : '') : 'isi nama, jumlah karung, dan harga per kg'}${hm.baris.length > 1 || b.terisi ? h`<span class="tautan" style="float: right;" data-aksi="mLepasBaris" data-i="${i}">lepas baris</span>` : ''}</div>
      </div>`)}
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="mTambahBaris">+ baris nama lain</div>${!koreksi && (d.pemasok || hm.sah.length || hm.kemasan.length) ? h`<div class="kaca-btn" data-aksi="mBaru">kosongkan</div>` : ''}</div>
      <div class="kartu" data-k="masuk-ringkas" style="gap: 4px;"><div class="label">Jumlah</div>
        <div class="serif" style="font-size: 19px;">${hm.karung} karung · ${KG(hm.kg)}${hm.kemasan.length ? ' + ' + hm.unitKemasan + ' kemasan jadi' : ''}</div>
        ${(() => { const T = hm.ikutTimbang; if (!T.baris) return ''; return T.belum.length ? h`<div class="pita-info awas" data-k="masuk-ikut">Baris ${T.belum.map((b) => b.ke).join(', ')} belum ditimbang — <b>WAJIB</b> timbang seluruh baris atau timbang sampel sebelum disimpan. Stok dibukukan dari hasil timbang; uang ke pemasok tetap sesuai nota.</div>`
          : h`<div class="pita-info emas" data-k="masuk-ikut">Stok ikut timbang: nota <b>${KG(T.kgNota)}</b> → dibukukan <b>${KG(T.kgBuku)}</b> (${T.selisihKg === 0 ? 'pas' : (T.selisihKg < 0 ? 'kurang ' : 'lebih ') + KG(Math.abs(T.selisihKg))}). Uang tetap sesuai nota${T.selisihKg ? ' — modal per kg ' + (T.selisihKg < 0 ? 'naik' : 'turun') + ' sedikit' : ''}; karung tetap dijual &amp; dicetak "${'50 kg'}", stok dipotong berat aslinya.</div>`; })()}
        <div class="ket">beras ${RP(hm.nilaiBeras)}${hm.kemasan.length ? ' + kemasan jadi ' + RP(hm.nilaiKemasan) : ''}${hm.nilaiBal ? ' + baris bal ' + RP(hm.nilaiBal) + ' (tidak diubah)' : ''}${hm.bongkar ? ' + bongkar ' + RP(hm.bongkar) : ''}${hm.ongkir ? ' + ongkos kirim ' + RP(hm.ongkir) : ''} = <b>${RP(hm.total)}</b> · ${d.caraBayar === 'utang' ? 'jadi bon pemasok' : 'tunai dari laci'}${hm.bongkar || hm.ongkir ? ' (bongkar & ongkos kirim selalu tunai)' : ''}</div>
        ${hm.ditolak.length ? h`<div class="ket awas-teks" data-k="masuk-ditolak">${hm.ditolak.length} baris DITOLAK (${hm.ditolak.map((b) => (b.merkKetik || b.merk) + ' ' + b.jumlahKarung + ' karung').join(', ')}) — tidak masuk stok dan tidak masuk bon; hanya dicatat untuk surat pemasok.</div>` : ''}
        ${hm.potongKg > 0 ? (koreksi ? h`<div class="ket" data-k="masuk-potong">Sudah dipotong ${UK(hm.potongKg)} kg (klaim / retur) — kg dan nilai di atas sudah sesudah potongan.</div>`
          : h`<div data-k="masuk-potong" style="display: flex; flex-direction: column; gap: 6px;"><div class="pita-info emas">Dipotong langsung <b>${UK(hm.potongKg)} kg</b> (${RP(hm.potongRp)}) karena kurang — kg dan nilai di atas sudah dari kg yang benar-benar datang; ${d.caraBayar === 'utang' ? 'bon pemasok dicatat ' + RP(hm.nilaiBeras) : 'laci keluar ' + RP(hm.nilaiBeras) + ' untuk berasnya'}. Tercatat di surat untuk pemasok.</div>
            <input class="ketik-nama" id="mAlasanPotong" type="text" maxlength="160" placeholder="alasan dipotong (boleh kosong) — mis. ditimbang kurang, karung bocor" value="${d.alasanPotong || ''}" data-ketik="mKetik" data-kolom="alasanPotong"></div>`) : ''}
        ${(() => { const T = hm.timbang; if (!T.ditimbang && !T.dicek) return ''; return h`<div class="ket ${T.awas || T.selisihKg < 0 ? 'awas-teks' : ''}" data-k="masuk-timbang">Timbang: ${T.ditimbang} dari ${T.baris} baris${T.ditimbang ? ' · selisih ' + (T.selisihKg === 0 ? 'pas 0 kg' : (T.selisihKg > 0 ? '+' : '−') + tmD(Math.abs(T.selisihKg)) + ' kg (' + (T.selisihKg > 0 ? '+' : '−') + tmD(Math.abs(T.persen)) + ' %)') + (T.nilaiKurang ? ' · kurang ≈ ' + RP(T.nilaiKurang) + (hm.ikutTimbang.ikut ? ' (dibayar tanpa barangnya — modal per kg naik)' : ' (perkiraan nilai, tidak dibukukan)') : '') : ''} · mutu dicek ${T.dicek} baris${T.awas ? ' · ' + T.awas + ' baris AWAS' : ''} — ${hm.ikutTimbang.ikut ? 'stok dibukukan dari hasil timbang; uang (bon / laci) tetap menurut nota.' : h`catatan pemeriksaan saja: ${KG(hm.kg)} di atas, stok, modal, HPP &amp; bon tetap menurut nota.`}</div>`; })()}
        ${!koreksi && hm.tunggu.length ? h`<div class="pita-info emas" data-k="masuk-tunggu">${hm.tunggu[0].pemasok} masih punya potongan <b>${RP(hm.potongTunggu)}</b> yang disepakati dipotong di pembelian berikutnya (${hm.tunggu.map((x) => (x.jenis === 'retur' ? 'retur' : 'klaim') + ' kedatangan ' + tanggalPendek(x.tanggalDatang) + ' ' + RP(x.rp)).join(' · ')}).
          <div class="kaca-btn ${hm.pakaiPotong ? 'aktif emas' : 'aktif'}" data-aksi="mPilih" data-kolom="pakaiPotong" data-nilai="${hm.pakaiPotong ? '' : '1'}" data-k="masuk-pakai">${hm.pakaiPotong ? '✓ DIPOTONG DI KEDATANGAN INI — ketuk untuk batal' : 'POTONG DI KEDATANGAN INI'}</div>
          ${hm.pakaiPotong ? h`<div class="ket" data-k="masuk-pakai-hitung">Nilai barang ${RP(hm.nilaiBeras + hm.nilaiKemasan)} − potongan ${RP(hm.potongTunggu)} = <b>${RP(hm.nilaiBeras + hm.nilaiKemasan - hm.potongTunggu)}</b> ${d.caraBayar === 'utang' ? 'jadi sisa bon pemasok' : 'yang dibayar dari laci'}. Stok & modal tetap dihitung dari nilai penuh barangnya.</div>` : h`<div class="ket">Belum diketuk = kedatangan ini dibayar penuh; potongannya tetap menunggu.</div>`}</div>` : ''}
        ${koreksi ? h`<input class="ketik-nama" id="mAlasan" type="text" placeholder="alasan koreksi / hapus (wajib)" value="${d.alasan || ''}" data-ketik="mKetik" data-kolom="alasan">` : ''}
        <div class="kaca-btn aktif emas" data-aksi="mSimpan">${koreksi ? 'SIMPAN KOREKSI' : 'SIMPAN BARANG MASUK · ' + RP(hm.total)}</div>
        ${koreksi ? h`<div class="tombol-baris rapat"><div class="kaca-btn ${s.yakinHapus ? 'awas' : 'putus'}" data-aksi="mHapus">${s.yakinHapus ? 'YAKIN HAPUS kedatangan ini' : 'hapus kedatangan'}</div><div class="kaca-btn" data-aksi="mBaru">batal koreksi</div></div>` : ''}
        ${koreksi && d.riwayat ? '' : ''}</div>
      <div class="kartu" data-k="buku-kedatangan" style="gap: 6px;"><div class="label">Buku kedatangan · ketuk untuk koreksi</div>
        ${C.daftarKedatangan(12).map((k) => { const kc = tolakKunciTanggal(k.tanggal, ''); const dr = kc ? C.drafDariKedatangan(k.id) : null; return kc ? h`<div class="jawab terkunci" data-k="bk-${k.id}" data-aksi="kpCocok" data-kunci="${dr && dr.baris[0] ? 'tumpukan|' + dr.baris[0].merk : ''}" title="${kc}"><span class="kiri"><span class="nm">${k.pemasok} <span class="w">· ${tanggalPendek(k.tanggal)}</span></span><span class="w">${kc.split(' — ')[0]} — cocokkan stok hari ini</span></span><span class="kanan"><span class="n">${RP(k.nilai)}</span><span class="w">terkunci</span></span></div>` : h`<div class="jawab ${d.id && String(d.id) === String(k.id) ? 'dipilih' : ''}" data-k="bk-${k.id}" data-aksi="mKoreksi" data-id="${k.id}"><span class="kiri"><span class="nm">${k.pemasok} <span class="w">· ${tanggalPendek(k.tanggal)}${k.jam ? ' ' + k.jam : ''}</span></span><span class="w">${k.ringkas}${k.dikoreksi ? ' · dikoreksi' : ''}${k.cek && k.cek.teks ? ' · ' + k.cek.teks : ''}</span></span>
          <span class="kanan"><span class="n">${k.fondasi ? 'fondasi' : RP(k.nilai)}</span><span class="w">${k.fondasi ? 'tidak diubah' : k.karung + ' karung · ' + (k.cara === 'utang' ? 'bon' : 'tunai')}</span></span></div>`; })}</div>
      ${C.bukuHapus(6).length ? h`<div class="kartu" data-k="buku-hapus" style="gap: 4px;"><div class="label">Buku hapus</div>${C.bukuHapus(6).map((x) => h`<div class="ket" data-k="bh-${x.id}">${tanggalPendek(x.tanggal)} ${x.jam} · ${x.pemasok} ${tanggalPendek(x.tanggalDok)} · ${x.ringkas} — ${x.alasan}</div>`)}</div>` : ''}
      ${koreksi ? gambarCatatanPemasok(s, d.id) : ''}
      ${gambarRekapTimbang()}
      <div class="ket tautan" data-aksi="bukaAturMutu" data-k="atur-mutu-buka">${s.aturMutu ? 'tutup ambang mutu per kelas' : 'Atur: ambang mutu per kelas (premium · medium) — butir patah, menir, kuning, butir lain, gabah'}</div>${gambarAturMutu(s)}
      ${gambarAturUkuran(s)}
      ${gambarAturTarif(s)}
      <div class="ket tautan" data-aksi="bukaAturC">${s.aturC ? 'tutup aturan' : 'Atur: minimal karung per mobil, tempo bon, selisih wajar, ambang mutu saat terima'}</div>${gambarAturC(s)}
      ${gambarAturHpp(s)}
    </section>`;
  }
  // ---------- CATATAN UNTUK PEMASOK & KLAIM (paket Barang masuk & mutu, Tahap 1 — owner 26 Nov 2026) ----------
  // tampil saat sebuah kedatangan dibuka (koreksi): yang kurang / lebih / tertinggal / mutu, cara klaim & statusnya. CATATAN SAJA — stok, modal, bon tidak berubah.
  function gambarCatatanPemasok(s, id) {
    const K = C.cpKedatangan(id); if (!K) return ''; const d = s.cpDraf && String(s.cpDraf.id) === String(id) ? s.cpDraf : null;
    const ringkas = K.ada ? K.catatan.length + ' baris' + (K.klaim ? ' · ' + K.klaim.caraNama.toLowerCase() + (K.klaim.nilai ? ' ' + RP(K.klaim.nilai) : '') + ' · ' + K.klaim.statusNama.toLowerCase() : ' · belum diklaim') : K.usul.length ? 'belum dicatat — ' + K.usul.length + ' usul dari timbang & mutu' : 'belum ada catatan';
    if (!d) return h`${gambarUsulOwner(s, id, K)}<div class="kartu" data-k="cp-kartu" style="gap: 6px;"><div class="label">Catatan untuk pemasok · ${ringkas}</div>
      ${K.catatan.map((c, i) => h`<div class="ket" data-k="cpl-${i}">${c.jenisNama} · ${c.merk}${c.jumlah ? ' · ' + DESIMAL(c.jumlah) + ' ' + c.satuan : ''}${c.ket ? ' — ' + c.ket : ''}</div>`)}
      ${K.bebas.trim() ? h`<div class="ket" data-k="cp-bebas">Catatan: ${K.bebas}</div>` : ''}
      ${K.ditolak.map((x, i) => h`<div class="ket awas-teks" data-k="cpt-${i}">Ditolak saat datang · ${x.merk} · ${x.jumlahKarung} karung — ${x.alasan}</div>`)}
      ${K.potongan.map((x, i) => h`<div class="ket" data-k="cpp-${i}">${tanggalPendek(x.tanggal)} · ${x.jenisNama} · ${DESIMAL(x.kg)} kg · ${x.tunggu ? RP(x.tunggu) + (x.dipakai ? (x.dipakai.cara === 'beli' ? ' · sudah dipotong di kedatangan ' : ' · uangnya diterima di ' + x.dipakai.cara + ' ') + tanggalPendek(x.dipakai.tanggal) : ' · MENUNGGU pembelian berikutnya') : x.uangKembali ? 'uang kembali ke ' + x.tempat + ' ' + RP(x.uangKembali) : x.saatDatang ? 'nilai turun ' + RP(x.rp) : 'bon turun ' + RP(x.rp)}${x.alasan ? ' — ' + x.alasan : ''}${x.tunggu && !x.dipakai && !K.kunci ? h` · ${['laci', 'rekening'].map((t) => h`<span class="tautan" data-aksi="ptTerima" data-id="${id}" data-i="${x.i}" data-t="${t}" data-k="ptt-${i}-${t}">${s.ptTerima === id + '|' + x.i + '|' + t ? 'YAKIN — uangnya masuk ' + t : 'uangnya ternyata diterima di ' + t}</span> `)}` : ''}</div>`)}
      ${K.kunci ? h`<div class="ket">${K.kunci.split(' — ')[0]} — catatannya tidak bisa diubah.</div>` : h`<div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="cpBuka" data-id="${id}" data-k="cp-buka">${K.ada ? 'ubah catatan & klaim' : 'tulis catatan untuk pemasok'}</div>${K.ada ? h`<div class="kaca-btn" data-aksi="cpSurat" data-id="${id}" data-k="cp-surat">buat surat siap cetak</div>` : ''}</div>`}
      ${!K.kunci && K.klaim && K.klaim.cara === 'potong' && !K.klaim.dibukukan ? (() => { const H = C.hitungPotongKlaim(id, s.ptTempat); return H.tolak ? h`<div class="pita-info" data-k="pt-belum">Belum dibukukan: ${H.tolak}</div>`
        : h`<div class="pita-info emas" data-k="pt-siap">Pemasok sudah setuju. Kalau dibukukan: ${H.baris.map((x) => x.merk + ' ' + DESIMAL(x.kgNota - x.kgSudah) + ' → ' + DESIMAL(x.kgBaru) + ' kg').join(' · ')}; ${H.tunai ? 'belanja tunai' : 'bon'} ${RP(H.bonLama)} → <b>${RP(H.bonBaru)}</b> (turun ${RP(H.rp)}); stok ikut turun ${DESIMAL(H.kg)} kg. Harga per kg tidak berubah.${H.tunai ? ' ' + kalimatUangKembali(H) : ''}</div>
          ${H.tunai ? pilTempat('ptTempat', H.tempat) : ''}
          <div class="kaca-btn ${s.ptYakin === String(id) ? 'awas' : 'aktif emas'}" data-aksi="ptKlaim" data-id="${id}" data-k="pt-bukukan">${s.ptYakin === String(id) ? 'YAKIN — ' + (H.tempat === 'berikut' ? 'dipotong nanti ' : H.tunai ? 'uang kembali ' : 'potong bon ') + RP(H.rp) : 'BUKUKAN · ' + (H.tempat === 'berikut' ? 'dipotong di pembelian berikutnya ' : H.tunai ? 'uang kembali ' : 'potong bon ') + RP(H.rp)}</div>`; })() : ''}
      ${!K.kunci ? gambarRetur(s, id, K) : ''}
      <div class="ket" style="font-size: 10.5px;">Bahan berunding dengan pemasok. Catatan dan klaim tidak mengubah stok, modal, bon, atau uang — yang mengubah hanya "BUKUKAN" dan "kembalikan ke pemasok" di atas.</div></div>`;
    return h`<div class="kartu" data-k="cp-tulis" style="gap: 8px;"><div class="label">Catatan untuk pemasok · ${K.pemasok || 'tanpa nama'} · ${tanggalPendek(K.tanggal)}</div>
      ${d.usulId ? h`<div class="pita-info emas" data-k="cp-dari-tablet">Diisi dari usul ${d.usulDari || 'tablet'} — periksa dulu. Menyimpan = catatannya masuk ke kedatangan ini dan usulnya ditandai sudah diperiksa.</div>` : ''}
      ${d.dariUsul ? h`<div class="pita-info" data-k="cp-usul">Baris di bawah diusulkan dari hasil timbang & cek mutu kedatangan ini — periksa, ubah, lalu simpan.</div>` : ''}
      ${d.baris.map((r, i) => h`<div data-k="cpr-${i}" style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--kaca-tepi); padding-top: 6px;">
        <div class="jalur rapat">${C.CP_JENIS.map(([jid, nm]) => h`<div class="seg ${r.jenis === jid ? 'aktif' : ''}" data-aksi="cpPilih" data-kolom="jenis" data-i="${i}" data-nilai="${jid}">${nm}</div>`)}</div>
        <div class="ps-form dua"><div><div class="ket">Barangnya</div><input class="ketik-nama" id="cpMerk${i}" type="text" placeholder="nama beras" value="${r.merk}" data-ketik="cpKetik" data-kolom="merk" data-i="${i}"></div>
          <div><div class="ket">Jumlah${r.jenis === 'mutu' ? ' (boleh kosong)' : ''}</div><div style="display: flex; gap: 6px;"><input class="ketik-nama" id="cpJml${i}" type="text" inputmode="decimal" placeholder="0" value="${r.jumlah}" data-ketik="cpKetik" data-kolom="jumlah" data-i="${i}">
            <div class="jalur rapat">${C.CP_SATUAN.map(([sid, nm]) => h`<div class="seg ${r.satuan === sid ? 'aktif' : ''}" data-aksi="cpPilih" data-kolom="satuan" data-i="${i}" data-nilai="${sid}">${nm}</div>`)}</div></div></div></div>
        <input class="ketik-nama" id="cpKet${i}" type="text" maxlength="${C.CP_MAKS.ket}" placeholder="keterangan — mis. karung sobek, tertinggal di gudang pemasok" value="${r.ket}" data-ketik="cpKetik" data-kolom="ket" data-i="${i}">
        <div class="ket tautan" data-aksi="cpBuang" data-i="${i}">buang baris ini</div></div>`)}
      <div class="kaca-btn putus" data-aksi="cpTambah" data-k="cp-tambah">+ baris catatan</div>
      <div data-k="cp-bebas-tulis"><div class="label">Catatan bebas untuk pemasok</div><textarea class="ketik-nama" id="cpBebas" rows="3" maxlength="${C.CP_MAKS.bebas}" placeholder="tulis apa saja yang mau disampaikan — ikut tercetak di surat" data-ketik="cpKetik" data-kolom="bebas">${d.bebas || ''}</textarea></div>
      <div class="label">Mau diselesaikan bagaimana</div>
      <div class="jalur rapat" data-k="cp-cara">${C.KLAIM_CARA.map(([cid, nm]) => h`<div class="seg ${d.cara === cid ? 'aktif' : ''}" data-aksi="cpPilih" data-kolom="cara" data-nilai="${cid}">${nm}</div>`)}</div>
      ${d.cara ? h`<div class="jalur rapat" data-k="cp-status">${C.KLAIM_STATUS.map(([sid, nm]) => h`<div class="seg ${d.status === sid ? 'aktif' : ''}" data-aksi="cpPilih" data-kolom="status" data-nilai="${sid}">${nm}</div>`)}</div>
        ${d.cara === 'catat' ? '' : h`<div class="ps-form dua"><div><div class="ket">Nilai yang diminta (Rp)${K.nilaiKurang ? ' · kosong = perkiraan dari timbang ' + RP(K.nilaiKurang) : ''}</div><input class="ketik-nama" id="cpNilai" type="text" inputmode="numeric" placeholder="${K.nilaiKurang || 0}" value="${d.nilai}" data-ketik="cpKetik" data-kolom="nilai"></div>
          <div><div class="ket">Catatan kesepakatan</div><input class="ketik-nama" id="cpCat" type="text" placeholder="mis. dipotong di bon berikutnya" value="${d.catatan}" data-ketik="cpKetik" data-kolom="catatan"></div></div>`}
        ${d.cara === 'potong' ? h`<div class="pita-info" data-k="cp-potong">Menyimpan klaim ini BELUM mengubah bon, stok, atau uang. Sesudah pemasok setuju: ubah statusnya jadi "Disetujui pemasok", simpan, lalu ketuk BUKUKAN di kartu catatan — stok dihitung dari kg yang benar-benar datang; kedatangan bon = bonnya turun, kedatangan tunai = uang kembali dari pemasok masuk laci atau rekening (dipilih saat membukukan).</div>` : ''}` : h`<div class="ket">Belum dipilih = catatan disimpan tanpa klaim.</div>`}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="cpBuka" data-id="${id}">batal</div><div class="kaca-btn aktif emas" data-aksi="cpSimpan" data-k="cp-simpan">SIMPAN CATATAN</div></div></div>`;
  }
  // Tahap 2: beras yang SUDAH masuk stok lalu dikembalikan ke pemasok — stok & bon kedatangan itu turun (dua ketukan, pratinjau dulu)
  // kedatangan TUNAI (Tahap 3): yang turun = nilai belanja tunainya; uangnya kembali dari pemasok ke laci (lihat stok-catat-logika, bagian Tahap 2)
  const kalimatUangKembali = (H) => H.tempat === 'berikut' ? 'Uangnya TIDAK kembali sekarang: ' + RP(H.rp) + ' dipotong pemasok di pembelian berikutnya — ditawarkan saat barang pemasok ini berikutnya dicatat. '
      + (H.dalamTitik ? 'Laci di buku tidak berubah.' : 'Hari kedatangannya belum ditutup, jadi patokan laci ' + tanggalPendek(H.titik) + ' diturunkan ' + RP(H.rp) + ' supaya laci di buku tidak naik.')
    : 'Uang kembali ' + RP(H.rp) + ' masuk ' + (H.tempat === 'rekening' ? 'REKENING' : 'LACI') + ' — ketuk SESUDAH uangnya diterima. '
    + (H.tempat === 'rekening' ? (H.dalamTitik ? 'Hari kedatangannya sudah ditutup, jadi patokan rekening ' + tanggalPendek(H.titik) + ' dinaikkan ' + RP(H.rp) + '.' : 'Hari kedatangannya belum ditutup: rekening di patokan kas naik ' + RP(H.rp) + ', laci tidak berubah.')
      : H.dalamTitik ? 'Hari kedatangannya sudah ditutup, jadi patokan laci ' + tanggalPendek(H.titik) + ' dinaikkan ' + RP(H.rp) + ' supaya hitungan laci malam ini tidak terbaca lebih.' : 'Hari kedatangannya belum ditutup: laci di buku naik sendiri.');
  const pilTempat = (aksi, kini) => h`<div data-k="pt-tempat"><div class="ket">Uang kembalinya diterima di — atau dipotong nanti</div><div class="jalur rapat" style="flex-wrap: wrap;">${C.PT_TEMPAT.map(([t, nm]) => h`<div class="seg ${kini === t ? 'aktif' : ''}" data-aksi="${aksi}" data-t="${t}">${nm}</div>`)}</div></div>`;
  function gambarRetur(s, id, K) {
    const d = s.rtDraf && String(s.rtDraf.id) === String(id) ? s.rtDraf : null; const tunai = K.cara !== 'utang';
    if (!d) return h`<div class="ket tautan" data-aksi="rtBuka" data-id="${id}" data-k="rt-buka">kembalikan sebagian beras kedatangan ini ke pemasok (${tunai ? 'stok turun, uangnya kembali ke laci / rekening atau dipotong di pembelian berikutnya' : 'stok & bon turun'})</div>`;
    const H = d.merk && String(d.kg).trim() ? C.hitungReturPemasok(id, d) : null;
    return h`<div data-k="rt-tulis" style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--kaca-tepi); padding-top: 6px;"><div class="label">Kembalikan ke pemasok</div>
      ${d.usulId ? h`<div class="pita-info emas" data-k="rt-dari-tablet">Diisi dari usul ${d.usulDari || 'tablet'} — periksa kg & alasannya. Stok & bon baru berubah sesudah diketuk dua kali di bawah.</div>` : ''}
      <div class="jalur rapat" data-k="rt-merk">${K.timbang.baris.map((x) => h`<div class="seg ${d.merk === (x.merkPemasok || x.merk) ? 'aktif' : ''}" data-aksi="rtPilih" data-merk="${x.merkPemasok || x.merk}">${x.merkPemasok || x.merk}</div>`)}</div>
      <div class="ps-form dua"><div><div class="ket">Berapa kg dikembalikan</div><input class="ketik-nama" id="rtKg" type="text" inputmode="decimal" placeholder="0" value="${d.kg}" data-ketik="rtKetik" data-kolom="kg"></div>
        <div><div class="ket">Alasannya (wajib)</div><input class="ketik-nama" id="rtAlasan" type="text" placeholder="mis. berkutu, apek" value="${d.alasan}" data-ketik="rtKetik" data-kolom="alasan"></div></div>
      ${H ? (H.tolak ? h`<div class="ket awas-teks" data-k="rt-tolak">${H.tolak}</div>` : h`<div class="pita-info" data-k="rt-pratinjau">${H.baris[0].merk}: ${DESIMAL(H.baris[0].kgNota - H.baris[0].kgSudah)} → ${DESIMAL(H.baris[0].kgBaru)} kg; ${H.tunai ? 'belanja tunai' : 'bon'} ${RP(H.bonLama)} → <b>${RP(H.bonBaru)}</b> (turun ${RP(H.rp)}); stok turun ${DESIMAL(H.kg)} kg. Dibukukan pada kedatangan ini, bukan sebagai catatan hari ini.${H.tunai ? ' ' + kalimatUangKembali(H) : ''}</div>`) : ''}
      ${tunai ? pilTempat('rtTempat', C.PT_TEMPAT.some((x) => x[0] === d.tempat) ? d.tempat : 'laci') : ''}
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="rtBuka" data-id="${id}">batal</div><div class="kaca-btn ${d.yakin ? 'awas' : 'aktif emas'}" data-aksi="rtSimpan" data-k="rt-simpan">${d.yakin ? 'YAKIN — kembalikan' : 'KEMBALIKAN KE PEMASOK'}</div></div></div>`;
  }
  function gambarAturMutu(s) {
    const a = s.aturMutu; if (!a) return '';
    return h`<div class="kartu" data-k="atur-mutu" style="gap: 8px;"><div class="label">Ambang mutu per kelas · di atasnya baris ditandai AWAS</div>
      ${C.TM_KELAS.map(([k, nmK]) => h`<div data-k="am-${k}" style="display: flex; flex-direction: column; gap: 6px;"><div><b>${nmK}</b></div><div class="ps-form dua">${C.TM_RINCI.map(([id, nm, sat]) => h`<div><div class="ket">${nm} maksimal (${sat})</div><input class="ketik-nama" id="am-${k}-${id}" type="text" inputmode="decimal" placeholder="kosong = tidak dinilai" value="${a[k][id] || ''}" data-ketik="mutuKetik" data-kelas="${k}" data-kolom="${id}"></div>`)}</div></div>`)}
      <div class="ket">Butir patah & menir terisi angka bawaan (premium 15 % & 0,5 % · medium 25 % & 2 %) — periksa dengan aturan yang berlaku. Yang kosong tidak dinilai. Hanya menandai; kedatangan tetap boleh dicatat.</div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturMutu">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturMutu" data-k="am-simpan">SIMPAN AMBANG</div></div></div>`;
  }
  // ---------- BARANG MASUK DARI TABLET (owner 22 Nov 2026, paket ③; rules v15) ----------
  // Penjaga laci: kedatangan langsung jadi stok + BON pemasok; harga dari nota supir (beda dari harga lalu = owner dikabari); upah bongkar & uang ke supir dari
  // laci = TITIPAN ke owner. Tanpa pilihan cara bayar, tanggal, kelas, varian, koreksi, hapus, atau aturan — itu urusan owner di HP.
  // ---------- Tahap 3 (owner 26 Nov 2026): isi karung bebas, klaim langsung saat datang, tolak baris — dipakai lembar owner DAN tablet ----------
  const UK = (n) => String(Math.round(Number(n) * 100) / 100).replace('.', ',');
  function pilUkuran(r, i) {
    const L = C.ukuranKarungPilihan(); const kini = Number(r.beratKarung); const semua = kini > 0 && L.indexOf(kini) < 0 ? L.concat([kini]) : L;
    return h`<div class="jalur rapat" data-k="uk-${i}" style="flex-wrap: wrap;">${semua.map((n) => h`<div class="seg ${kini === n ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="beratKarung" data-i="${i}" data-nilai="${n}">${UK(n)} kg</div>`)}</div>`;
  }
  function pilPotong(b, r, i) {
    const sel = b.cek && b.cek.selisihKg !== null && b.cek.selisihKg !== undefined && b.cek.selisihKg < 0 ? Math.round(-b.cek.selisihKg * 100) / 100 : 0;
    return h`<div class="ps-form dua" data-k="mpt-${i}"><div><div class="ket">Kurang saat datang — kg yang dipotong (klaim langsung)</div><input class="ketik-nama" id="mPotong${i}" type="text" inputmode="decimal" placeholder="0 = sesuai nota" value="${r.kgPotong || ''}" data-ketik="mKetik" data-kolom="kgPotong" data-i="${i}"></div>
      <div class="ket" style="align-self: end;">${b.kgPotong > 0 && b.sah && b.ikutTimbang ? h`nota ${UK(b.kgNota)} kg − ${UK(b.kgPotong)} = <b>${UK(b.kgTagih)} kg</b> yang dibayar · nilai turun ${RP(Math.round(b.kgNota * b.hargaPerKg) - b.subtotalHarga)} · stok tetap dari hasil timbang ${UK(b.totalKg)} kg`
        : b.kgPotong > 0 && b.sah ? h`nota ${UK(b.kgNota)} kg − ${UK(b.kgPotong)} = <b>${UK(b.totalKg)} kg</b> yang dibukukan · nilai turun ${RP(Math.round(b.kgNota * b.hargaPerKg) - b.subtotalHarga)}`
        : sel > 0 && !(b.kgPotong > 0) ? h`<span class="tautan" data-aksi="mPotongTimbang" data-i="${i}" data-kg="${sel}">pakai selisih timbang: potong ${UK(sel)} kg</span>`
          // Tahap 6: kedatangan ikut timbang — stok sudah dari hasil timbang; kg yang dipotong hanya menurunkan uang ke pemasok (bon / belanja tunai)
          : b.ikutTimbang ? 'Kosong = dibayar sesuai nota. Diisi = uang ke pemasok dipotong kg itu (harga per kg tetap); stok tetap dari hasil timbang.' : 'Kosong = diterima sesuai nota. Diisi = stok & nilai dihitung dari kg yang benar-benar datang; harga per kg tetap.'}</div></div>`;
  }
  function pilTolak(r, i) {
    return h`<div data-k="mt-${i}" style="display: flex; flex-direction: column; gap: 6px;"><div class="ket tautan ${r.ditolak ? 'awas-teks' : ''}" data-aksi="mPilih" data-kolom="ditolak" data-i="${i}" data-nilai="${r.ditolak ? '' : '1'}">${r.ditolak ? 'baris ini DITOLAK — tidak masuk stok & bon (ketuk untuk membatalkan)' : 'tolak baris ini (mutu tidak sesuai — tidak diterima)'}</div>
      ${r.ditolak ? h`<input class="ketik-nama" id="mTolak${i}" type="text" maxlength="160" placeholder="alasan ditolak (wajib) — mis. berkutu, kadar air tinggi" value="${r.alasanTolak || ''}" data-ketik="mKetik" data-kolom="alasanTolak" data-i="${i}">` : ''}</div>`;
  }
  // paket P4 (owner 27 Nov 2026, A25): upah bongkar MENURUT TARIF = karung × tarif per karung yang berlaku di tanggal datang (PB.pbCekBongkar) — cuma tanda, tetap
  // boleh disimpan; "pakai Rp…" mengisi kolom upah bongkar. Tablet ikut membaca (aturanToko/catatStok); tautan menulis tarif hanya untuk owner.
  function gambarTarifTanda(d) {
    const T = PB.pbCekBongkar(d.baris, d.bongkar, d.tanggal); if (T.keadaan === 'tanpaKarung') return '';
    if (T.keadaan === 'tanpaTarif') return bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : h`<div class="ket" data-k="masuk-tarif">${T.teks} — <span class="tautan" data-aksi="tbBuka">tulis tarifnya ›</span></div>`;
    return h`<div class="ket ${T.awas ? 'awas-teks' : ''}" data-k="masuk-tarif">${T.teks}${T.awas && T.harap > 0 ? h` <span class="tautan" data-aksi="mPilih" data-kolom="bongkar" data-nilai="${String(T.harap)}" data-k="masuk-tarif-pakai">pakai ${RP(T.harap)} ›</span>` : ''}</div>`;
  }
  /** Atur tarif bongkar kuli (owner): satu tarif toko per karung, per ukuran karung, berlaku sejak tanggal yang dipilih. */
  function gambarAturTarif(s) {
    const iso = waktu().tanggal; const T = PB.pbTarifKini(iso, C.ukuranKarungPilihan()); const ringkas = T.baris.filter((x) => x.rp !== null).map((x) => UK(x.berat) + ' kg ' + RP(x.rp)).join(' · ');
    return h`<div class="ket tautan" data-aksi="tbBuka" data-k="tb-buka">${s.tbBuka ? 'tutup tarif bongkar' : 'Atur tarif bongkar kuli per karung: ' + (ringkas || 'belum ditulis')}</div>
      ${s.tbBuka ? h`<div class="kartu" data-k="tb-atur" style="gap: 8px;"><div class="label">Tarif bongkar kuli · per karung · sama untuk semua kuli</div>
        <div class="ps-form dua">${T.baris.map((x) => h`<div data-k="tb-${x.berat}"><div class="ket">Karung ${UK(x.berat)} kg${x.rp !== null ? ' · sekarang ' + RP(x.rp) + ' sejak ' + tanggalPendek(x.mulai) : ' · belum ada'}${x.nanti ? ' · ' + RP(x.nanti.rp) + ' mulai ' + tanggalPendek(x.nanti.mulai) : ''}</div><input class="ketik-nama" type="text" inputmode="numeric" placeholder="${x.rp !== null ? String(x.rp) : 'Rp per karung'}" value="${(s.tbKetik || {})[String(x.berat)] || ''}" data-ketik="tbKetik" data-berat="${String(x.berat)}"></div>`)}
          <div><div class="ket">Berlaku mulai</div><input class="ketik-nama" type="date" value="${s.tbMulai || iso}" data-ketik="tbMulai"></div></div>
        <div class="kaca-btn aktif emas" data-aksi="tbSimpan" data-k="tb-simpan">SIMPAN TARIF</div>
        ${T.riwayat.length ? h`<div class="ket" data-k="tb-riwayat">Tertulis: ${T.riwayat.map((x) => 'sejak ' + tanggalPendek(x.mulai) + ' karung ' + UK(x.berat) + ' kg ' + RP(x.rp)).join(' · ')}</div>` : ''}
        <div class="ket" style="font-size: 11px;">Kuli bongkar = orang pasar (bukan dari pemasok, bukan karyawan). Barang masuk menghitung karung × tarif dan menandai kalau upah bongkar yang diketik beda — cuma tanda, tetap boleh disimpan. Kosong = tidak diubah; 0 = tanpa upah. Kedatangan lama dicek dengan tarif yang berlaku di harinya (Dasbor › Buku pembelian). Tampil juga di tablet.</div></div>` : ''}`;
  }
  /** Atur isi karung (owner): daftar ukuran yang bisa dipilih di Barang masuk — tambah / lepas, tanpa ngoding. */
  function gambarAturUkuran(s) {
    const L = C.ukuranKarungPilihan();
    return h`<div class="ket tautan" data-aksi="ukBuka" data-k="uk-buka">${s.ukBuka ? 'tutup isi karung' : 'Atur isi karung: ' + L.map((n) => UK(n) + ' kg').join(' · ')}</div>
      ${s.ukBuka ? h`<div class="kartu" data-k="uk-atur" style="gap: 8px;"><div class="label">Isi karung yang bisa dipilih${C.ukuranMilikOwner() ? '' : ' · bawaan'}</div>
        <div class="tombol-baris rapat" data-k="uk-daftar">${L.map((n) => h`<div class="kaca-btn kecil" data-aksi="ukHapus" data-n="${n}" data-k="ukd-${n}">${UK(n)} kg ✕</div>`)}</div>
        <div class="tombol-baris rapat"><input class="ketik-nama sempit" id="ukKetik" type="text" inputmode="decimal" placeholder="mis. 10 · 2,5 · 0,5" value="${s.ukKetik || ''}" data-ketik="ukKetik"><div class="kaca-btn aktif emas" data-aksi="ukTambah" data-k="uk-tambah">TAMBAH UKURAN</div></div>
        <div class="ket" style="font-size: 11px;">Bebas ${UK(C.UK_BATAS.min)}–${C.UK_BATAS.maks} kg, paling banyak ${C.UK_BATAS.banyak} ukuran; ketuk ukuran untuk melepasnya (kedatangan lama tidak berubah). Tampil juga di tablet. Karung berukuran selain 25 kg masuk buku beras per kg merek itu: stok = jumlah karung × isi karung.</div></div>` : ''}`;
  }
  // ---------- Tahap 5 (owner 26 Nov 2026): baris catatan untuk pemasok — penyunting yang dipakai lembar tablet (awalan mc) & usul tablet (awalan us) ----------
  function editorCatatan(rows, pre) {
    return (rows || []).map((r, i) => h`<div data-k="${pre}r-${i}" style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--kaca-tepi); padding-top: 6px;">
      <div class="jalur rapat" style="flex-wrap: wrap;">${C.CP_JENIS.map(([jid, nm]) => h`<div class="seg ${r.jenis === jid ? 'aktif' : ''}" data-aksi="${pre}Pilih" data-kolom="jenis" data-i="${i}" data-nilai="${jid}">${nm}</div>`)}</div>
      <div class="ps-form dua"><div><div class="ket">Barangnya</div><input class="ketik-nama" id="${pre}Merk${i}" type="text" placeholder="nama beras" value="${r.merk || ''}" data-ketik="${pre}Ketik" data-kolom="merk" data-i="${i}"></div>
        <div><div class="ket">Jumlah${r.jenis === 'mutu' ? ' (boleh kosong)' : ''}</div><div style="display: flex; gap: 6px;"><input class="ketik-nama" id="${pre}Jml${i}" type="text" inputmode="decimal" placeholder="0" value="${r.jumlah || ''}" data-ketik="${pre}Ketik" data-kolom="jumlah" data-i="${i}">
          <div class="jalur rapat">${C.CP_SATUAN.map(([sid, nm]) => h`<div class="seg ${r.satuan === sid ? 'aktif' : ''}" data-aksi="${pre}Pilih" data-kolom="satuan" data-i="${i}" data-nilai="${sid}">${nm}</div>`)}</div></div></div></div>
      <input class="ketik-nama" id="${pre}Ket${i}" type="text" maxlength="${C.CP_MAKS.ket}" placeholder="keterangan — mis. karung sobek, tertinggal di gudang pemasok" value="${r.ket || ''}" data-ketik="${pre}Ketik" data-kolom="ket" data-i="${i}">
      <div class="ket tautan" data-aksi="${pre}Buang" data-i="${i}">buang baris ini</div></div>`);
  }
  /** TABLET · kedatangan tersimpan yang dipilih: catatan yang sudah ada + usul untuk owner (catatan & klaim, kembalikan, pembetulan, hapus). Tidak menulis buku. */
  function gambarUsulTablet(s) {
    const ak = opsi.akun ? opsi.akun() : null; const id = s.tbm && s.tbm.id !== undefined ? String(s.tbm.id) : ''; if (!id || !bukanOwner(ak)) return '';
    const K = C.cpKedatangan(id); if (!K) return ''; const d = s.usDraf && String(s.usDraf.id) === id ? s.usDraf : null; const tunggu = MT.mtUsulMenunggu(id);
    const b = C.batchKedatangan(id); const up = b && b.usulPakaiPotong ? Math.round(Number(b.usulPakaiPotong.rp) || 0) : 0;
    const H = d && d.jenis === 'retur' && d.merk && String(d.kg).trim() ? C.hitungReturPemasok(id, d) : null;
    return h`<div class="kartu" data-k="us-kartu" style="gap: 6px;"><div class="label">Catatan &amp; usul untuk owner · ${K.pemasok || 'tanpa nama'} · ${tanggalPendek(K.tanggal)}</div>
      ${K.catatan.map((c, i) => h`<div class="ket" data-k="usl-${i}">${c.jenisNama} · ${c.merk}${c.jumlah ? ' · ' + DESIMAL(c.jumlah) + ' ' + c.satuan : ''}${c.ket ? ' — ' + c.ket : ''}</div>`)}
      ${K.klaim ? h`<div class="ket" data-k="us-klaim">${K.klaim.caraNama} · ${K.klaim.statusNama.toLowerCase()}</div>` : ''}
      ${K.bebas.trim() ? h`<div class="ket" data-k="us-bebas">Catatan: ${K.bebas}</div>` : ''}
      ${K.ditolak.map((x, i) => h`<div class="ket awas-teks" data-k="ust-${i}">Ditolak saat datang · ${x.merk} · ${x.jumlahKarung} karung — ${x.alasan}</div>`)}
      ${K.potongan.map((x, i) => h`<div class="ket" data-k="usp-${i}">${tanggalPendek(x.tanggal)} · ${x.jenisNama} · ${DESIMAL(x.kg)} kg</div>`)}
      ${!K.ada ? h`<div class="ket" data-k="us-kosong">Belum ada catatan untuk pemasok di kedatangan ini${K.usul.length ? ' — hasil timbang & cek mutu menemukan ' + K.usul.length + ' hal yang bisa dicatat' : ''}.</div>` : ''}
      ${up ? h`<div class="pita-info emas" data-k="us-potong">Potong ${RP(up)} di kedatangan ini sudah DIUSULKAN — menunggu owner; bonnya masih penuh.</div>` : ''}
      ${tunggu.map((u) => h`<div class="pita-info" data-k="us-tunggu-${u.pid}">Menunggu owner · ${tanggalPendek(u.tanggal)} ${u.jam} · ${u.teks}</div>`)}
      ${K.kunci ? h`<div class="ket">${K.kunci.split(' — ')[0]} — kedatangan ini tidak bisa diubah lagi.</div>` : h`<div class="label">Usulkan ke owner</div>
        <div class="jalur rapat" data-k="us-jenis" style="flex-wrap: wrap;">${MT.MT_USUL.map(([jid, nm]) => h`<div class="seg ${d && d.jenis === jid ? 'aktif' : ''}" data-aksi="usBuka" data-id="${id}" data-jenis="${jid}">${nm}</div>`)}</div>
        ${!d ? h`<div class="ket">Yang jaga mengusulkan; owner yang memutuskan dari HP. Mengirim usul tidak mengubah stok, bon, atau uang.</div>` : ''}
        ${d && d.jenis === 'catatan' ? h`${editorCatatan(d.baris, 'us')}
          <div class="kaca-btn putus" data-aksi="usTambah" data-k="us-tambah">+ baris catatan</div>
          <div><div class="ket">Catatan bebas untuk pemasok</div><textarea class="ketik-nama" id="usBebas" rows="2" maxlength="${C.CP_MAKS.bebas}" placeholder="tulis apa saja yang mau disampaikan" data-ketik="usKetik" data-kolom="bebas">${d.bebas || ''}</textarea></div>
          <div class="label">Mau diselesaikan bagaimana</div><div class="jalur rapat" data-k="us-cara" style="flex-wrap: wrap;">${C.KLAIM_CARA.map(([cid, nm]) => h`<div class="seg ${d.cara === cid ? 'aktif' : ''}" data-aksi="usPilih" data-kolom="cara" data-nilai="${cid}">${nm}</div>`)}</div>
          ${d.cara ? h`<div class="jalur rapat" data-k="us-status" style="flex-wrap: wrap;">${C.KLAIM_STATUS.map(([sid, nm]) => h`<div class="seg ${d.status === sid ? 'aktif' : ''}" data-aksi="usPilih" data-kolom="status" data-nilai="${sid}">${nm}</div>`)}</div>` : ''}` : ''}
        ${d && d.jenis === 'retur' ? h`<div class="jalur rapat" data-k="us-merk" style="flex-wrap: wrap;">${K.timbang.baris.map((x) => h`<div class="seg ${d.merk === (x.merkPemasok || x.merk) ? 'aktif' : ''}" data-aksi="usPilih" data-kolom="merk" data-nilai="${x.merkPemasok || x.merk}">${x.merkPemasok || x.merk}</div>`)}</div>
          <div class="ps-form dua"><div><div class="ket">Berapa kg dikembalikan</div><input class="ketik-nama" id="usKg" type="text" inputmode="decimal" placeholder="0" value="${d.kg}" data-ketik="usKetik" data-kolom="kg"></div>
            <div><div class="ket">Alasannya (wajib)</div><input class="ketik-nama" id="usAlasan" type="text" placeholder="mis. berkutu, apek" value="${d.alasan}" data-ketik="usKetik" data-kolom="alasan"></div></div>
          ${H ? (H.tolak ? h`<div class="ket awas-teks" data-k="us-retur-tolak">${H.tolak}</div>` : h`<div class="pita-info" data-k="us-retur-pratinjau">${H.baris[0].merk}: ${DESIMAL(H.baris[0].kgNota - H.baris[0].kgSudah)} → ${DESIMAL(H.baris[0].kgBaru)} kg kalau owner membukukan. Stok &amp; bon BELUM berubah sampai owner menyetujui.</div>`) : ''}` : ''}
        ${d && (d.jenis === 'koreksi' || d.jenis === 'hapus') ? h`<div><div class="ket">${d.jenis === 'hapus' ? 'Kenapa kedatangan ini minta dihapus' : 'Apa yang salah, dan yang benarnya bagaimana'}</div><textarea class="ketik-nama" id="usTeks" rows="3" maxlength="${MT.MT_USUL_BATAS.teks}" placeholder="${d.jenis === 'hapus' ? 'mis. tercatat dua kali' : 'mis. harga Angsa seharusnya 13.100, karung 38 bukan 40'}" data-ketik="usKetik" data-kolom="teks">${d.teks || ''}</textarea></div>` : ''}
        ${d ? h`<div class="tombol-baris"><div class="kaca-btn" data-aksi="usBuka" data-id="${id}" data-jenis="${d.jenis}">batal</div><div class="kaca-btn aktif emas" data-aksi="usKirim" data-k="us-kirim">KIRIM USUL KE OWNER</div></div>` : ''}`}</div>`;
  }
  /** OWNER · usul dari tablet untuk kedatangan yang sedang dibuka: pakai potongan (setujui) + usul catatan / kembalikan / pembetulan / hapus. */
  function gambarUsulOwner(s, id, K) {
    const b = C.batchKedatangan(id); const adaPakai = !!(b && b.usulPakaiPotong); const U = MT.mtUsulMenunggu(id); if (!adaPakai && !U.length) return '';
    const P = adaPakai ? C.ptUsulPakai(id, waktu().tanggal) : null;
    return h`<div class="kartu" data-k="uo-kartu" style="gap: 6px;"><div class="label">Usul dari tablet · menunggu keputusan</div>
      ${P ? (P.tolak ? h`<div class="pita-info" data-k="uo-pakai-tolak">Yang jaga mengusulkan potongan ${RP(P.usulRp)} dipakai di kedatangan ini, tetapi belum bisa: ${P.tolak}.</div><div class="kaca-btn putus" data-aksi="ppLepas" data-id="${id}" data-k="uo-pakai-lepas" style="align-self: flex-start;">lepas usul ini</div>`
        : h`<div class="pita-info emas" data-k="uo-pakai">Yang jaga mengusulkan: potongan ${P.pemasok} <b>${RP(P.rp)}</b> (klaim / retur sebelumnya) dipakai di kedatangan ini. Kalau disetujui: bon ${RP(P.sisaBon)} → <b>${RP(P.sisaBon - P.rp)}</b>; tidak ada uang yang bergerak, laci di buku tetap${P.dalamTitik ? '' : ' (patokan laci ' + tanggalPendek(P.titik) + ' + ' + RP(P.rp) + ' mengimbangi bayar bon dari laci)'}. Stok & modal tidak berubah.</div>
          <div class="tombol-baris rapat"><div class="kaca-btn ${s.ppYakin === String(id) ? 'awas' : 'aktif emas'}" data-aksi="ppSetuju" data-id="${id}" data-k="uo-pakai-setuju">${s.ppYakin === String(id) ? 'YAKIN — potong bon ' + RP(P.rp) : 'SETUJUI · potong bon ' + RP(P.rp)}</div><div class="kaca-btn putus" data-aksi="ppLepas" data-id="${id}" data-k="uo-pakai-lepas">tidak dipakai</div></div>`) : ''}
      ${U.map((u) => h`<div data-k="uo-${u.pid}" style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--kaca-tepi); padding-top: 6px;"><div class="ket">${u.dari} · ${tanggalPendek(u.tanggal)} ${u.jam}</div><div>${u.teks}</div>
        <div class="tombol-baris rapat">${!K.kunci && (u.usul.jenis === 'catatan' || u.usul.jenis === 'retur') ? h`<div class="kaca-btn aktif" data-aksi="usulPakai" data-id="${id}" data-pid="${u.pid}" data-k="uo-pakai-${u.pid}">${u.usul.jenis === 'catatan' ? 'isi lembar catatan dari usul ini' : 'isi lembar kembalikan dari usul ini'}</div>` : ''}<div class="kaca-btn putus" data-aksi="usulSelesai" data-pid="${u.pid}" data-k="uo-selesai-${u.pid}">tandai sudah diperiksa</div></div>
        ${u.usul.jenis === 'koreksi' ? h`<div class="ket">Pembetulannya dikerjakan di lembar koreksi di atas (harga, jumlah, pemasok), lalu tandai sudah diperiksa.</div>` : u.usul.jenis === 'hapus' ? h`<div class="ket">Menghapus tetap lewat "hapus kedatangan" di atas (dua ketukan, beralasan).</div>` : ''}</div>`)}</div>`;
  }
  /** paket tanggal janji: pesanan ke pemasok yang menunggu datang + janjinya (rules v24: Penjaga laci membaca & mengisi / menggeser janji). Kosong = tidak tampil. */
  function kartuJanjiTablet(s, ak) {
    let D = []; try { D = JN.jnMenungguPemasok(kini()).slice(0, 5); } catch (e) { return ''; }
    if (!D.length) return ''; const boleh = tombolAkun(ak, 'kedatangan').boleh; const jp = s.janjiP; const iso = waktu().tanggal;
    return h`<div class="kartu" data-k="mt-janji" style="gap: 6px;"><div class="label">Pesanan ke pemasok yang menunggu · janji datang</div>
      ${D.map((x) => h`<div data-k="mtj-${x.id}" style="display: grid; grid-template-columns: minmax(0, 1fr); gap: 6px; padding: 6px 0; border-bottom: 1px dashed var(--garis);"><div><div><b>${x.nama}</b> · dipesan ${tanggalPendek(x.dibuat).replace(/ \d{4}$/, '')} · ${x.pesan} karung</div><div class="ket ${x.keadaan === 'lewat' ? 'awas-teks' : ''}">${JN.jnKataBaris(x)}</div></div>
        ${boleh ? h`<div class="tombol-baris rapat"><div class="kaca-btn kecil ${jp && jp.id === x.id ? 'aktif' : ''}" data-aksi="mtJanjiBuka" data-id="${x.id}">${x.janji.awal ? 'geser janji' : 'isi janji'}</div></div>` : ''}</div>
        ${boleh && jp && jp.id === x.id ? h`<div class="kartu" data-k="mtj-ubah-${x.id}" style="gap: 6px;"><div class="jalur rapat bungkus">${JN.jnPilihan(iso).filter(([t]) => t).map(([t, nm]) => h`<div class="seg ${jp.tanggal === t ? 'aktif' : ''}" data-aksi="mtJanjiPilih" data-t="${t}" data-k="mtj-p-${nm}">${nm} · ${tanggalPendek(t).replace(/ \d{4}$/, '')}</div>`)}</div>
          <input class="ketik-nama" type="date" min="${x.dibuat}" value="${jp.tanggal}" data-ketik="mtJanjiKetik" aria-label="tanggal janji datang">
          <div class="ket">${x.janji.awal ? 'Pemasok menggeser janjinya? Tanggal baru dicatat; tepat waktu tetap dihitung dari janji pertama (' + tanggalPendek(x.janji.awal) + ').' : 'Isi tanggal yang dijanjikan pemasok / supir.'}</div>
          <div class="tombol-baris rapat"><div class="kaca-btn" data-aksi="mtJanjiBuka" data-id="${x.id}">batal</div><div class="kaca-btn aktif emas" data-aksi="mtJanjiSimpan">SIMPAN JANJI</div></div></div>` : ''}`)}
      <div class="ket" style="font-size: 11px;">Barang yang datang dicatat seperti biasa di bawah — pesanannya otomatis dianggap datang. Isi &amp; jumlah pesanan diatur owner.</div></div>`;
  }
  function gambarMasukTablet(s) {
    const w = waktu(); const d = Object.assign(MT.mtDrafKosong(w), s.masuk || {}); const hm = MT.mtHitung(d, w); const a = C.aturCatat(); const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const pemasok = C.calonPemasok().slice(0, 6); const merk = C.calonMerkMasuk(); const ak = opsi.akun ? opsi.akun() : null;
    const titip = (hm.bongkarTitip > 0 ? hm.bongkarTitip : 0) + (hm.supirTitip > 0 ? hm.supirTitip : 0) + (hm.ongkirTitip > 0 ? hm.ongkirTitip : 0);
    return h`<section class="stok-masuk" data-k="masuk">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Barang masuk</div><div class="ket">${tanggalPendek(w.tanggal)} · langsung jadi stok &amp; BON pemasok · harga dari nota supir · uang dari laci dititip ke owner</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      ${s.tbm ? kartuTerima(s.tbm.id, { akun: ak, tutup: true }) : ''}
      ${s.tbm ? kartuFotoNota(s.tbm.id, { s, akun: ak }) : ''}
      ${s.tbm ? kartuLabelMasuk(s.tbm.id, s) : ''}
      ${kartuJanjiTablet(s, ak)}
      <div class="kartu" data-k="masuk-kepala" style="gap: 8px;">
        <div><div class="ket">Pemasok</div><input class="ketik-nama" id="mPemasok" type="text" placeholder="nama pemasok" value="${d.pemasok}" data-ketik="mKetik" data-kolom="pemasok">
          ${pemasok.length ? h`<div class="tombol-baris rapat" data-k="calon-pemasok">${pemasok.map((p) => h`<div class="kaca-btn kecil ${d.pemasok === p ? 'aktif' : ''}" data-aksi="mPilih" data-kolom="pemasok" data-nilai="${p}">${p}</div>`)}</div>` : ''}</div>
        <div class="pita-info" data-k="mt-bon">Dicatat sebagai <b>bon pemasok</b> (jatuh tempo ${a.tempoHari} hari). Uang yang dibayar ke supir sekarang diisi di bawah — owner yang mencatatnya ke bon.</div>
      </div>
      ${hm.baris.map((b, i) => h`<div class="kartu baris-masuk ${b.terisi && (b.masalah || b.masalahTablet) ? 'awas' : ''}" data-k="mb-${i}" style="gap: 6px;">
        <div class="label">Baris ${i + 1}${b.kemasan ? ' · KEMASAN JADI' + (b.kemasanSah ? ' · ' + b.jumlahKarung + ' × ' + UK(b.beratKarung) + ' kg · ' + RP(b.subtotalHarga) : '') : b.sah ? ' · ' + KG(b.totalKg) + ' · ' + RP(b.subtotalHarga) : ''}</div>
        <input class="ketik-nama" id="mMerk${i}" type="text" placeholder="${b.kemasan ? 'nama kemasan (yang tertulis di bungkusnya)' : 'nama beras / karung'}" value="${d.baris[i].merk}" data-ketik="mKetik" data-kolom="merk" data-i="${i}">
        ${!b.merk ? h`<div class="tombol-baris rapat" data-k="calon-merk-${i}">${(b.kemasan ? C.kjCalonNama() : merk).slice(0, 8).map((m) => h`<div class="kaca-btn kecil" data-aksi="mPilih" data-kolom="merk" data-i="${i}" data-nilai="${m}">${m}</div>`)}</div>` : ''}
        <div class="ps-form tiga"><div><div class="ket">${b.kemasan ? 'Jumlah kemasan' : 'Karung'}</div><input class="ketik-nama" id="mJml${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].jumlahKarung}" data-ketik="mKetik" data-kolom="jumlahKarung" data-i="${i}"></div>
          <div><div class="ket">Harga / kg (nota supir)${b.lalu ? ' · lalu ' + RP(b.lalu.harga) : b.hargaLalu ? ' · lalu ' + RP(b.hargaLalu) : ''}</div><input class="ketik-nama" id="mHarga${i}" type="text" inputmode="numeric" placeholder="0" value="${d.baris[i].hargaPerKg}" data-ketik="mKetik" data-kolom="hargaPerKg" data-i="${i}"></div>
          <div><div class="ket">${b.kemasan ? 'Isi per kemasan' : 'Isi karung'}</div>${pilUkuran(d.baris[i], i)}</div></div>
        ${b.arahVarian ? h`<div class="ket ${b.arahVarian.arah === 'naik' ? 'awas-teks' : ''}" data-k="mt-av-${i}">Varian ${b.arahVarian.teks}</div>` : ''}
        <div class="ket tautan" data-k="mt-kj-${i}" data-aksi="mPilih" data-kolom="masuk" data-i="${i}" data-nilai="${b.kemasan ? '' : 'kemasan'}">${b.kemasan ? 'KEMASAN JADI — masuk buku Kemasan, dijual per kemasan (ketuk untuk kembali ke beras per kg)' : 'karung kecil yang dijual utuh per kemasan? jadikan baris ini KEMASAN JADI'}</div>
        ${b.kemasan || d.baris[i].ditolak ? '' : pilPotong(b, d.baris[i], i)}
        ${b.kemasan ? '' : pilTolak(d.baris[i], i)}
        ${b.kemasan ? '' : gambarCekMasuk(b, d.baris[i], i, a)}
        ${b.saranVarian && b.saranVarian.length ? h`<div class="pita-info emas" data-k="mt-sv-${i}"><div><b>${b.merkKetik}</b> sudah dicatat sebagai <b>${b.saranVarian.map((v) => v.nama).join(' / ')}</b> — pakai itu?</div>
          <div class="tombol-baris rapat" data-k="mt-sv-pil-${i}">${b.saranVarian.map((v) => h`<div class="kaca-btn aktif emas" data-aksi="mPakaiVarian" data-i="${i}" data-merk="${v.nama}">pakai ${v.nama}</div>`)}</div></div>` : ''}
        ${b.varianInduk && b.varianInduk.length ? h`<div class="pita-info emas" data-k="mt-vi-${i}"><div><b>${b.merk}</b> punya varian <b>${b.varianInduk.map((v) => v.nama).join(' / ')}</b> — karung yang datang ini yang mana?</div>
          <div class="tombol-baris rapat" data-k="mt-vi-pil-${i}">${b.varianInduk.map((v) => h`<div class="kaca-btn aktif emas" data-aksi="mPakaiVarian" data-i="${i}" data-merk="${v.nama}">masuk ${v.nama}</div>`)}</div></div>` : ''}
        ${b.merekBaru ? h`<div class="pita-info emas" data-k="mt-baru-${i}">Merek baru <b>${b.merkKetik}</b> — belum punya buku stok. Tetap dicatat atas nama ini (buku baru, tanpa kelas &amp; harga jual); owner dikabari, yang mengatur kelas &amp; harga jualnya atau membetulkan dari HP. Salah ketik? Pilih nama yang sudah ada.</div>` : ''}
        ${b.gabung ? h`<div class="pita-info emas" data-k="mt-jauh-${i}">Harga ${RP(b.hargaPerKg)}/kg beda ${DESIMAL(b.vr.beda)} % dari modal ${b.merk} — dicatat sebagai ${b.merk} yang sama; owner dikabari dan yang memutus kalau ternyata beda mutu.</div>` : ''}
        <div class="ket ${b.terisi && (b.masalah || b.masalahTablet) ? 'awas-teks' : ''}">${b.terisi && b.masalah ? b.masalah : b.terisi && b.masalahTablet ? b.masalahTablet : b.kemasanSah ? 'masuk buku Kemasan "' + b.merk + ' ' + UK(b.beratKarung) + ' kg" +' + b.jumlahKarung + ' — dijual per kemasan; harga jualnya diatur owner' : b.kemasan ? 'isi nama kemasan, jumlah kemasan, dan harga beli per kg dari nota supir' : b.sah ? (b.merekBaru ? 'merek baru — belum ada harga lalu; owner dikabari' : hm.hargaBeda.some((x) => x.merk === b.merkSimpan) ? 'harga beda dari harga lalu — owner dikabari' : 'harga sama dengan harga lalu') : 'isi nama, jumlah karung, dan harga per kg dari nota supir'}${hm.baris.length > 1 || b.terisi ? h`<span class="tautan" style="float: right;" data-aksi="mLepasBaris" data-i="${i}">lepas baris</span>` : ''}</div>
      </div>`)}
      <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="mTambahBaris">+ baris nama lain</div>${d.pemasok || hm.sah.length || hm.kemasan.length ? h`<div class="kaca-btn" data-aksi="mBaru">kosongkan</div>` : ''}</div>
      <div class="kartu" data-k="mt-titip" style="gap: 6px;"><div class="label">Uang dari laci saat barang datang · dititip ke owner</div>
        <div class="ps-form dua"><div><div class="ket">Upah bongkar (Rp)</div><input class="ketik-nama" id="mBongkar" type="text" inputmode="numeric" placeholder="0" value="${d.bongkar}" data-ketik="mKetik" data-kolom="bongkar"></div>
          <div><div class="ket">Dibayar ke supir sekarang (Rp)</div><input class="ketik-nama" id="mSupir" type="text" inputmode="numeric" placeholder="0" value="${d.bayarSupir}" data-ketik="mKetik" data-kolom="bayarSupir"></div></div>
        ${gambarTarifTanda(d)}
        <div class="ps-form dua" data-k="mt-ongkir"><div><div class="ket">Ongkos kirim supir pemasok (Rp)</div><input class="ketik-nama" id="mOngkir" type="text" inputmode="numeric" placeholder="0" value="${d.ongkir || ''}" data-ketik="mKetik" data-kolom="ongkir"></div>
          <div class="ket" style="align-self: end;">Ongkos antar barang ini (bukan pembayaran berasnya).</div></div>
        <div class="ket" style="font-size: 11px;">Boleh diambil dari laci sekarang; laci di buku berkurang sesudah owner menyetujui. Upah bongkar &amp; ongkos kirim masuk modal barang ini; bayar ke supir dicatat owner ke bon pemasoknya.</div></div>
      <div class="kartu" data-k="mt-bebas" style="gap: 6px;"><div class="label">Catatan untuk pemasok (boleh kosong)</div>
        <textarea class="ketik-nama" id="mBebas" rows="2" maxlength="${C.CP_MAKS.bebas}" placeholder="mis. 2 karung sobek, 1 karung tertinggal — owner yang meneruskan ke pemasok" data-ketik="mKetik" data-kolom="catatanBebas">${d.catatanBebas || ''}</textarea></div>
      <div class="kartu" data-k="mt-catatan" style="gap: 8px;"><div class="label">Yang kurang, lebih, tertinggal, atau mutunya tidak sesuai · ${(d.catatan || []).length ? (d.catatan || []).length + ' baris' : 'boleh kosong'}</div>
        ${editorCatatan(d.catatan || [], 'mc')}
        <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="mcTambah" data-k="mc-tambah">+ baris catatan</div>${hm.timbang.ditimbang || hm.timbang.awas ? h`<div class="kaca-btn" data-aksi="mcTimbang" data-k="mc-timbang">isi dari hasil timbang &amp; cek mutu</div>` : ''}</div>
        ${(d.catatan || []).length ? h`<div class="label">Mau diselesaikan bagaimana</div><div class="jalur rapat" data-k="mc-cara" style="flex-wrap: wrap;">${C.KLAIM_CARA.map(([cid, nm]) => h`<div class="seg ${d.klaimCara === cid ? 'aktif' : ''}" data-aksi="mcPilih" data-kolom="klaimCara" data-nilai="${cid}">${nm}</div>`)}</div>
          <div class="ket">${d.klaimCara ? 'Dicatat "sudah disampaikan" ke pemasok. Menyimpan catatan ini TIDAK mengubah bon atau stok — yang memotong bon / mengembalikan uang tetap owner.' : 'Belum dipilih = dicatat saja, tanpa permintaan.'}</div>` : ''}
        <div class="ket" style="font-size: 11px;">Ikut tersimpan di kedatangan ini dan bisa langsung dicetak untuk supir dari kartu tanda terima (tombol "CETAK CATATAN PEMASOK").</div></div>
      <div class="kartu" data-k="masuk-ringkas" style="gap: 4px;"><div class="label">Jumlah</div>
        <div class="serif" style="font-size: 19px;">${hm.karung} karung · ${KG(hm.kg)}${hm.kemasan.length ? ' + ' + hm.unitKemasan + ' kemasan jadi' : ''}</div>
        ${(() => { const T = hm.ikutTimbang; if (!T.baris) return ''; return T.belum.length ? h`<div class="pita-info awas" data-k="mt-ikut">Baris ${T.belum.map((b) => b.ke).join(', ')} belum ditimbang — <b>WAJIB</b> timbang seluruh baris atau timbang sampel sebelum disimpan. Stok dibukukan dari hasil timbang; uang ke pemasok tetap sesuai nota.</div>`
          : h`<div class="pita-info emas" data-k="mt-ikut">Stok ikut timbang: nota <b>${KG(T.kgNota)}</b> → dibukukan <b>${KG(T.kgBuku)}</b> (${T.selisihKg === 0 ? 'pas' : (T.selisihKg < 0 ? 'kurang ' : 'lebih ') + KG(Math.abs(T.selisihKg))}). Uang tetap sesuai nota${T.selisihKg ? ' — modal per kg ' + (T.selisihKg < 0 ? 'naik' : 'turun') + ' sedikit' : ''}; karung tetap dijual &amp; dicetak "${'50 kg'}", stok dipotong berat aslinya.</div>`; })()}
        <div class="ket">nilai ${RP(hm.nilai)}${hm.kemasan.length ? ' (beras ' + RP(hm.nilaiBeras) + ' + kemasan jadi ' + RP(hm.nilaiKemasan) + ')' : ''} · <b>jadi bon pemasok</b>${titip ? ' · dititip ke owner ' + RP(titip) : ''}${hm.hargaBeda.length ? ' · ' + hm.hargaBeda.length + ' harga beda dari lalu' : ''}</div>
        ${hm.potongKg > 0 ? h`<div class="pita-info emas" data-k="mt-potong">Dipotong langsung <b>${UK(hm.potongKg)} kg</b> (${RP(hm.potongRp)}) karena kurang — bon dicatat dari kg yang benar-benar datang; owner dikabari.</div>
          <input class="ketik-nama" id="mAlasanPotong" type="text" maxlength="160" placeholder="alasan dipotong (boleh kosong) — mis. ditimbang kurang, karung bocor" value="${d.alasanPotong || ''}" data-ketik="mKetik" data-kolom="alasanPotong">` : ''}
        ${hm.ditolak.length ? h`<div class="ket awas-teks" data-k="mt-ditolak">${hm.ditolak.length} baris DITOLAK (${hm.ditolak.map((b) => (b.merkKetik || b.merk) + ' ' + b.jumlahKarung + ' karung').join(', ')}) — tidak masuk stok dan tidak masuk bon; owner dikabari.</div>` : ''}
        ${hm.tunggu.length ? h`<div class="pita-info emas" data-k="mt-tunggu">${hm.tunggu[0].pemasok} masih punya potongan <b>${RP(hm.potongTunggu)}</b> yang disepakati dipotong di pembelian berikutnya (${hm.tunggu.map((x) => (x.jenis === 'retur' ? 'retur' : 'klaim') + ' kedatangan ' + tanggalPendek(x.tanggalDatang) + ' ' + RP(x.rp)).join(' · ')}).
          <div class="kaca-btn ${hm.usulPotong ? 'aktif emas' : 'aktif'}" data-aksi="mPilih" data-kolom="pakaiPotong" data-nilai="${hm.usulPotong ? '' : '1'}" data-k="mt-pakai">${hm.usulPotong ? '✓ DIUSULKAN DIPOTONG DI KEDATANGAN INI — ketuk untuk batal' : 'USULKAN POTONG DI KEDATANGAN INI'}</div>
          <div class="ket" data-k="mt-pakai-ket">${hm.usulPotong ? h`Bon dicatat <b>penuh ${RP(hm.nilai)}</b> dulu; sesudah owner menyetujui dari HP bonnya jadi ${RP(hm.nilai - hm.potongTunggu)}. Yang dibayar ke supir sekarang tetap diisi di "Dibayar ke supir".` : 'Belum diketuk = bon dicatat penuh; potongannya tetap menunggu.'}</div></div>` : ''}
        <div class="kaca-btn aktif emas" data-aksi="mSimpan">${s.yakinM ? 'YAKIN — SIMPAN BARANG MASUK' : 'SIMPAN BARANG MASUK · ' + RP(hm.nilai)}</div></div>
      <div class="ket tautan" data-aksi="bukaTerima" data-k="mt-ke-tersimpan">Kedatangan yang sudah tersimpan: tanda terima, catatan pemasok, usul kembalikan / pembetulan untuk owner</div>
    </section>`;
  }
  // ---------- COCOKKAN / HITUNG GUDANG (ST3): beras (karung × isi + kg lepas), kemasan jadi (unit), kantong (lembar) ----------
  function gambarCocok(s) {
    const c = Object.assign(cocokKosong(), s.cocok || {}); c.tab = C.tabCocokSah(c.tab); const r = C.susunCocok(c.tab, c.hitung, c.alasan, s.yakinC);
    const aktif = r.baris.find((b) => b.kunci === c.buka) || null; const KG = (n) => DESIMAL(Math.round(n * 100) / 100);
    const nilai = (b) => (b.satuan === 'kg' ? KG(b.sistem) + ' kg' : b.sistem + ' ' + b.satuan);
    const sel = (n) => (n > 0 ? '+' : '') + KG(n) + ' kg';
    const judulTab = { tumpukan: 'tumpukan gudang: karung utuh 50 / 25 kg per nama · selisih = karung hilang / lebih × modal · tidak ada liter di sini', wadah: 'wadah literan: isi kotak (takar / liter / kg) + karung terbuka di belakangnya · selisih dibagi ke merek asal isinya · susut kecil = wajar', kemasan: 'kemasan jadi per unit', kantong: 'kantong kosong & paper bag per lembar' };
    // ---- panel isian satu barang
    const panelTumpukan = (b) => h`<div class="ps-form tiga"><div><div class="ket">Karung 50 kg utuh</div><input class="ketik-nama" id="ckKarung" type="text" inputmode="numeric" placeholder="0" value="${c.karung}" data-ketik="cKetik" data-kolom="karung"></div>
        <div><div class="ket">Karung 25 kg utuh</div><input class="ketik-nama" id="ckKarung25" type="text" inputmode="numeric" placeholder="0" value="${c.karung25}" data-ketik="cKetik" data-kolom="karung25"></div>
        <div><div class="ket">kg karung terbuka yang TIDAK di belakang wadah (repack / literan langsung)</div><input class="ketik-nama" id="ckKg" type="text" inputmode="decimal" placeholder="0" value="${c.kg}" data-ketik="cKetik" data-kolom="kg"></div></div>
      ${(() => { const S0 = C.ccSampel(Object.assign({}, c, { sampelKarung: '', sampelKg: '' }), b.nama); return h`<div class="ket" data-k="ck-hitung">${angka(c.karung)} × 50 + ${angka(c.karung25)} × 25 + ${DESIMAL(angka(c.kg))} = <b>${KG(angka(c.karung) * 50 + angka(c.karung25) * 25 + angka(c.kg))} kg</b> di tumpukan${S0.asli ? h` → berat asli <b>${KG(S0.kg)} kg</b> (karung "50 kg" ${b.nama} berisi hasil timbang kedatangannya)` : ''} · tercatat ±${b.karungSistem} karung ${b.beratKarung} kg</div>`; })()}
      <div class="ps-form dua" data-k="ck-sampel"><div><div class="ket">Timbang sampel — berapa karung ditimbang (boleh kosong)</div><input class="ketik-nama" id="ckSampelKarung" type="text" inputmode="numeric" placeholder="0" value="${c.sampelKarung || ''}" data-ketik="cKetik" data-kolom="sampelKarung"></div>
        <div><div class="ket">Berat SELURUH sampel itu (kg)</div><input class="ketik-nama" id="ckSampelKg" type="text" inputmode="decimal" placeholder="0" value="${c.sampelKg || ''}" data-ketik="cKetik" data-kolom="sampelKg"></div></div>
      ${(() => { const S = C.ccSampel(c, b.nama); return !S.ada ? h`<div class="ket" style="font-size: 10.5px;">Sampel kosong = tiap karung dianggap penuh 50 / 25 kg. Diisi = karung utuh dikalikan rata-rata berat sampel.</div>` : S.masalah ? h`<div class="ket awas-teks" data-k="ck-sampel-hasil">${S.masalah}</div>`
        : h`<div class="pita-info" data-k="ck-sampel-hasil">Sampel ${S.karung} karung = ${KG(S.kgSampel)} kg → rata-rata <b>${KG(S.rata)} kg</b> per karung ${S.isiKarung} kg (${S.persen > 0 ? '+' : ''}${DESIMAL(S.persen)} %). Seluruh karung utuh dikalikan rata-rata itu: <b>${KG(S.kg)} kg</b> di tumpukan (tanpa sampel ${KG(S.kgNota)} kg, beda ${KG(S.selisihKg)} kg). Perkiraan dari sampel — dipakai sebagai hitungan kalau "PAKAI HITUNGAN INI" diketuk; selisihnya dibukukan seperti hitungan biasa.</div>`; })()}`;
    const panelWadah = (b) => h`<div class="ket">komposisi tercatat: ${b.komposisi.length ? b.komposisi.map((x) => x.merk + ' ' + KG(x.kg) + ' kg').join(' + ') : b.isiSistem === null ? 'belum pernah disamakan' : 'kosong'} · modal isi ${RP(Math.round(b.modal))}/kg${b.sejak ? ' · disamakan terakhir ' + tanggalPendek(b.sejak) : ''}</div>
      <div class="ps-form dua"><div><div class="ket">Isi kotak wadah</div><input class="ketik-nama" id="ckIsi" type="text" inputmode="decimal" placeholder="0" value="${c.isi}" data-ketik="cKetik" data-kolom="isi">
          <div class="jalur rapat">${[['takar', 'takar'], ['liter', 'liter'], ['kg', 'kg']].map(([id, nm]) => h`<div class="seg ${c.satuanIsi === id ? 'aktif' : ''}" data-aksi="cSatuan" data-s="${id}">${nm}</div>`)}</div></div>
        <div><div class="ket">Sisa karung ${b.karungLabel || b.karungNama} di belakangnya (kg)${b.karungBuku ? ' · tercatat = bukunya' : ''}</div><input class="ketik-nama" id="ckKr" type="text" inputmode="decimal" placeholder="${b.karungSistem === null ? 'belum ditandai' : KG(b.karungSistem)}" value="${c.kr}" data-ketik="cKetik" data-kolom="kr"></div></div>
      ${String(c.isi || '').trim() ? h`<div class="ket">${DESIMAL(angka(c.isi))} ${c.satuanIsi}${c.satuanIsi === 'kg' ? '' : ' × ' + DESIMAL(c.satuanIsi === 'takar' ? b.takarKg : b.rasio) + ' kg'} = <b>${KG(isiKeKg(c.isi, c.satuanIsi, b))} kg</b> di kotak</div>` : ''}`;
    // audit 39b no. 5: karung berbuku sendiri di luar slot wadah — cuma sisa karungnya yang ditimbang; tercatat = bukunya
    const panelKarung = (b) => h`<div class="ket">${b.lokasi ? 'di belakang wadah ' + b.lokasi : 'karung lepas (tidak di belakang wadah)'} · buku ${b.karungNama}${b.karungCatatan !== null && Math.abs(b.karungCatatan - b.karungSistem) > 0.05 ? ' · catatan karungnya ±' + KG(b.karungCatatan) + ' kg (ikut diset ke hitungan)' : ''}</div>
      <div><div class="ket">Sisa karung ditimbang (kg)</div><input class="ketik-nama" id="ckKr" type="text" inputmode="decimal" placeholder="${KG(b.karungSistem)}" value="${c.kr}" data-ketik="cKetik" data-kolom="kr"></div>`;
    const catatanKr = (b) => (b.karungBuku && b.karungCatatan !== null && Math.abs(b.karungCatatan - b.karungSistem) > 0.05 ? ' · catatan karung ±' + KG(b.karungCatatan) + ' kg' : '');
    const hasilWadah = (b) => h`<div class="ket ${b.besar ? 'awas-teks' : ''}">${b.pertama ? 'hitungan PERTAMA (belum pernah ditandai) — jadi titik awal, tidak ada selisih · ' : ''}${b.jenis === 'karung' ? '' : 'isi ' + (b.isiH === null ? '—' : KG(b.isiH) + ' kg' + (b.isiSistem === null ? '' : ' (tercatat ' + KG(b.isiSistem) + ', ' + sel(b.dIsi) + ')')) + ' · '}karung ${b.krH === null ? '—' : KG(b.krH) + ' kg' + (b.karungSistem === null ? '' : ' (tercatat ' + KG(b.karungSistem) + ', ' + sel(b.dKr) + ')')}
        → ${b.selisih === 0 ? 'cocok' : 'selisih ' + sel(b.selisih) + ' = ' + RP(b.rp) + (b.wajar ? ' · SUSUT TAKAR WAJAR (≤ ' + KG(b.wajarKg) + ' kg dalam ' + b.lamaHari + ' hari)' : b.besar ? ' · DI ATAS batas wajar ' + KG(b.wajarKg) + ' kg — alasannya wajib' : '')}
        ${Object.keys(b.alokasi).length ? ' · buku: ' + Object.keys(b.alokasi).map((m) => m + ' ' + sel(b.alokasi[m])).join(', ') : ''}${b.aneh ? ' · ANEH: melebihi isi kotak / karung, cek lagi' : ''}</div>
      ${b.lupaTakar ? h`<div class="pita-info emas" data-k="lupa-${b.nama}">${b.isiSistem !== null && b.isiSistem < 0 ? 'Wadah ' + b.nama + ' tercatat MINUS ' + KG(-b.isiSistem) + ' kg' : 'Wadah lebih ' + KG(b.dIsi) + ' kg, karung di belakangnya kurang ' + KG(-b.dKr) + ' kg'} — sepertinya ada isi ulang yang lupa dicatat.
        <div class="kaca-btn aktif" data-aksi="cLupa" data-wadah="${b.nama}" data-merk="${b.karungNama}" data-n="${b.lupaTakar}">catat isi ulang ${b.lupaTakar} takar dari karung ${b.karungLabel || b.karungNama} dulu</div></div>` : ''}`;
    const panel = (b) => h`<div class="kartu rincian-wadah" data-k="panel-${b.kunci}" style="gap: 8px;"><div class="label">${b.no ? b.no + ' · ' : ''}${b.nama}</div>
        <div class="ket">tercatat ${b.tab === 'wadah' ? (b.jenis === 'karung' ? 'karung ' + KG(b.karungSistem) + ' kg (buku)' : 'isi ' + (b.isiSistem === null ? '? (belum ditandai)' : KG(b.isiSistem) + ' kg') + ' + karung ' + (b.karungSistem === null ? '?' : KG(b.karungSistem) + ' kg' + (b.karungBuku ? ' (buku)' : '')) + catatanKr(b)) : nilai(b)} · modal ${RP(Math.round(b.modal))}/${b.satuan}${b.cocokAkhir ? ' · terakhir dicocokkan ' + b.cocokAkhir : ' · belum pernah dicocokkan'}</div>
        ${b.rincian ? h`<div class="ket">${b.rincian}</div>` : ''}
        ${b.tab === 'tumpukan' ? h`${panelTumpukan(b)}<div data-k="ck-hama-${b.kunci}"><div class="ket">Hama di tumpukan ini? (dicatat bersama hitungannya · boleh dilewati)</div>
          <div class="jalur rapat">${S.UM_HAMA.map(([id, nm]) => h`<div class="seg ${(c.hama || {})[b.kunci] === id ? 'aktif' : ''}" data-aksi="cHama" data-kunci="${b.kunci}" data-v="${id}">${nm}</div>`)}</div></div>` : b.tab === 'wadah' ? (b.jenis === 'karung' ? panelKarung(b) : panelWadah(b)) : h`<div><div class="ket">Dihitung (${b.satuan})</div><input class="ketik-nama" id="ckAngka" type="text" inputmode="numeric" placeholder="0" value="${c.angka}" data-ketik="cKetik" data-kolom="angka"></div>`}
        <div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="cPakai" data-kunci="${b.kunci}" data-satuan="${b.satuan}">PAKAI HITUNGAN INI</div>${b.tab === 'wadah' && b.jenis === 'karung' ? (b.karungSistem >= 0 ? h`<div class="kaca-btn" data-aksi="cPas" data-kunci="${b.kunci}" data-sistem="${b.karungSistem}">✓ cocok persis</div>` : '') : b.tab === 'wadah' ? (b.isiSistem !== null || b.karungSistem !== null ? h`<div class="kaca-btn" data-aksi="cPas" data-kunci="${b.kunci}" data-sistem="${b.isiSistem === null ? '' : b.isiSistem}" data-karung="${b.karungSistem === null ? '' : b.karungSistem}">✓ cocok persis</div>` : '') : h`<div class="kaca-btn" data-aksi="cPas" data-kunci="${b.kunci}" data-sistem="${b.sistem}">✓ cocok persis</div>`}</div>
        ${b.ada ? (b.tab === 'wadah' ? hasilWadah(b) : h`<div class="ket ${b.selisih < 0 ? 'awas-teks' : ''}">dihitung ${b.satuan === 'kg' ? KG(b.dihitung) + ' kg' : b.dihitung + ' ' + b.satuan} → ${b.selisih === 0 ? 'cocok persis' : 'selisih ' + (b.selisih > 0 ? '+' : '') + (b.satuan === 'kg' ? KG(b.selisih) + ' kg' : b.selisih + ' ' + b.satuan) + (b.tab === 'tumpukan' && b.beratKarung ? ' (' + DESIMAL(Math.round(b.selisih / b.beratKarung * 100) / 100) + ' karung)' : '') + ' = ' + RP(b.rp) + (b.selisih < 0 ? ' (susut)' : ' (stok naik)')}${b.tab === 'tumpukan' && (c.sampel || {})[b.kunci] ? ' · perkiraan dari timbang sampel ' + c.sampel[b.kunci].karung + ' karung (rata-rata ' + KG(c.sampel[b.kunci].rata) + ' kg)' : ''}${b.aneh ? ' · ANEH: lebih dari dua kali tercatat, cek lagi' : ''}</div>`) : ''}
        ${b.besar ? h`<div><div class="ket">${b.tab === 'wadah' ? 'Di atas susut wajar' : 'Selisih lebih dari ' + r.batasSelisih + ' %'} — alasannya (wajib)</div><input class="ketik-nama" id="ckAlasan-${b.kunci}" type="text" placeholder="mis. tumpah waktu bongkar" value="${b.alasan}" data-ketik="cAlasan" data-kunci="${b.kunci}"></div>` : ''}
        ${b.ada ? h`<div class="ket tautan" data-aksi="cHapusHitung" data-kunci="${b.kunci}">hapus hitungan ini</div>` : ''}</div>`;
    const kanan = (b) => (!b.ada ? '—' : b.tab === 'wadah' && b.pertama && b.selisih === 0 ? 'titik awal' : b.selisih === 0 ? 'cocok' : (b.selisih > 0 ? '+' : '') + (b.satuan === 'kg' ? KG(b.selisih) + ' kg' : b.selisih));
    const ketBaris = (b) => (b.tab === 'wadah' ? (b.jenis === 'karung' ? 'buku ' + KG(b.karungSistem) + ' kg' + catatanKr(b) : 'isi ' + (b.isiSistem === null ? '?' : KG(b.isiSistem) + ' kg') + ' · karung ' + (b.karungLabel || b.karungNama) + ' ' + (b.karungSistem === null ? '?' : KG(b.karungSistem) + ' kg') + catatanKr(b)) + (b.ada && b.wajar ? ' · susut wajar' : '')
      : 'tercatat ' + nilai(b) + (b.ada ? ' · dihitung ' + (b.satuan === 'kg' ? KG(b.dihitung) : b.dihitung) : '')) + (b.cocokAkhir ? '' : ' · belum pernah dicocokkan');
    return h`<section class="stok-cocok" data-k="cocok">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Cocokkan · hitung gudang</div><div class="ket">${judulTab[c.tab] || ''} · kurang = susut memotong laba, lebih = stok naik tanpa mengubah modal</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      <div class="jalur kisi4" data-k="tab-cocok">${C.TAB_COCOK.map(([id, nm]) => h`<div class="seg ${c.tab === id ? 'aktif' : ''}" data-aksi="cTab" data-t="${id}">${nm}</div>`)}</div>
      ${(() => { const T = AB.abRingkasBarang(); return T.length ? h`<div class="pita-info emas" data-k="cocok-titipan"><b>Barang titipan pembeli — sudah terjual, masih di toko. JANGAN ikut dihitung:</b> ${T.map((x) => x.nama + ' ' + AB.abJumlahTeks(x.jumlah, x.satuan) + ' (' + x.nota + ' nota)').join(' · ')}</div>` : ''; })()}
      ${(() => { const calon = C.ccCalonOrang(); const isi = (kolom, judul, ph) => h`<div><div class="ket">${judul}</div><input class="ketik-nama" id="ck-${kolom}" type="text" placeholder="${ph}" value="${c[kolom] || ''}" data-ketik="cOrang" data-kolom="${kolom}">
          ${calon.length ? h`<div class="jalur rapat">${calon.map((n) => h`<div class="seg ${c[kolom] === n ? 'aktif' : ''}" data-aksi="cOrangPilih" data-kolom="${kolom}" data-nama="${n}">${n}</div>`)}</div>` : ''}</div>`;
        return h`<div class="kartu" data-k="cocok-orang" style="gap: 6px;"><div class="label">Siapa yang menghitung</div><div class="ps-form dua">${isi('dihitungOleh', 'Dihitung oleh', 'nama yang menghitung')}${isi('didampingi', 'Didampingi', 'kosong = tidak didampingi')}</div>
          <div class="ket" style="font-size: 10.5px;">Ikut tersimpan di tiap barang yang dihitung · Laporan › Mingguan menyebut hitungan yang tidak didampingi. Stok, laba, dan kas tidak dipengaruhi.</div></div>`; })()}
      <div class="op-ringkas" data-k="ringkas-cocok"><div>dihitung<b>${r.dihitung} / ${r.semua}</b></div><div>susut (potong laba)<b>${RP(r.susutRp)}</b></div><div>lebih (stok naik)<b>${RP(r.lebihRp)}</b></div></div>
      <div class="kaca-btn ${r.dihitung ? 'aktif emas' : 'mati'}" data-aksi="cSimpan">${r.tolak && !r.perluYakin ? r.tolak : c.tab === 'wadah' ? 'SIMPAN COCOKKAN WADAH · ' + ((n) => (n[0] ? n[0] + ' wadah' : '') + (n[1] ? (n[0] ? ' + ' : '') + n[1] + ' karung' : '') || '0 wadah')([r.baris.filter((b) => b.ada && b.jenis !== 'karung').length, r.baris.filter((b) => b.ada && b.jenis === 'karung').length]) : 'SIMPAN COCOKKAN · ' + r.berubah + ' berubah'}</div>
      ${c.tab === 'tumpukan' ? (() => { const G = C.ckCalonGabungUkuran(); if (!G.length) return ''; return h`<div class="kartu" data-k="gabung-ukuran" style="gap: 6px;">
        <div class="label">Gabungkan buku karung 25 kg ke induknya · ${G.length} buku</div>
        <div class="ket">Merek yang dijual per liter / kelas sendiri tidak memakai buku per ukuran (keputusan owner 30 Sep): karung 25 kg-nya dijual & ditakar dari buku induk. Isi buku di bawah pindah seluruhnya ke induknya, modal ikut, laba tidak berubah — bukan cocokkan.</div>
        ${G.map((x) => h`<div class="tombol-baris rapat" data-k="gu-${x.kunci}"><div class="ket" style="min-width: 150px;"><b>${x.kunci}</b> · ${KG(x.kg)} kg → ${x.induk} (${KG(x.indukKg)} → ${KG(Math.round((x.indukKg + x.kg) * 100) / 100)} kg)</div>
          <div class="kaca-btn ${s.guYakin === x.kunci ? 'awas' : 'aktif emas'}" data-aksi="gabungUkuran" data-merk="${x.kunci}">${s.guYakin === x.kunci ? 'YAKIN — gabungkan' : 'gabungkan ke ' + x.induk}</div></div>`)}</div>`; })() : ''}
      ${c.tab === 'tumpukan' ? (() => { const P = C.ckCalonPisahUkuran(); if (!P.length) return ''; return h`<div class="kartu" data-k="pisah-ukuran" style="gap: 6px;">
        <div class="label">Pisahkan buku karung 25 kg · ${P.length} merek datang dua ukuran</div>
        <div class="ket">Karung 50 kg dan 25 kg merek yang sama sekarang masih satu buku. Hitung karung 25 kg yang masih UTUH di gudang, tulis jumlahnya (0 kalau tidak ada): sejumlah itu pindah ke buku "Merek 25 kg", modal ikut, laba tidak berubah. Sesudahnya karung 25 kg merek itu dijual, diretur, dan dicatat masuk dari bukunya sendiri.</div>
        ${P.map((x) => h`<div class="tombol-baris rapat" data-k="pu-${x.merk}"><div class="ket" style="min-width: 150px;"><b>${x.merk}</b> · buku ${KG(x.bukuKg)} kg</div>
          <input class="ketik-nama sempit" id="pu-${x.merk}" type="text" inputmode="numeric" placeholder="karung 25 kg utuh" value="${(s.cocok && s.puKetik && s.puKetik[x.merk]) || ''}" data-ketik="puKetik" data-merk="${x.merk}">
          <div class="kaca-btn ${s.puYakin === x.merk ? 'awas' : 'putus'}" data-aksi="pisahUkuran" data-merk="${x.merk}">${s.puYakin === x.merk ? 'YAKIN — pisahkan' : 'pisahkan ke ' + x.baru}</div></div>`)}</div>`; })() : ''}
      ${aktif ? panel(aktif) : h`<div class="ket" style="text-align: center;">Ketuk barangnya lalu isi hasil hitungannya, atau ✓ kalau cocok persis. Hitungan tersimpan di HP ini sampai disimpan.</div>`}
      <div class="kartu" data-k="daftar-cocok" style="gap: 2px;">${r.baris.length ? r.baris.map((b) => h`<div class="jawab ${b.kunci === c.buka ? 'dipilih' : ''}" data-k="cb-${b.kunci}" data-aksi="cBuka" data-kunci="${b.kunci}">
          <span class="kiri"><span class="nm">${b.no ? b.no + ' · ' : ''}${b.nama}</span><span class="w">${ketBaris(b)}</span></span>
          <span class="kanan"><span class="n ${b.ada && b.selisih < 0 ? 'awas' : ''}">${kanan(b)}</span><span class="w ${b.perluAlasan ? 'awas-teks' : ''}">${b.perluAlasan ? 'butuh alasan · ' : ''}${b.ada && b.selisih ? RP(b.rp) : b.ada ? '✓' : ''}</span></span></div>`) : h`<div class="ket">Tidak ada barang di kelompok ini.</div>`}</div>
      ${r.dihitung ? h`<div class="ket tautan" data-aksi="cBersih">kosongkan semua hitungan</div>` : ''}
      ${C.riwayatCocok(6).length ? h`<div class="kartu" data-k="riwayat-cocok" style="gap: 4px;"><div class="label">Hitungan sebelumnya</div>${C.riwayatCocok(6).map((g) => h`<div data-k="rc-${g.kunci}"><div class="ket"><b>${tanggalPendek(g.tanggal)} ${g.jam}</b> · ${g.baris.length} barang · ${RP(g.rp)}${g.oleh ? ' · dihitung ' + g.oleh : ''}${g.damping ? ' · didampingi ' + g.damping : ''}</div>${g.baris.map((x, i) => h`<div class="ket" style="padding-left: 10px;" data-k="rc-${g.kunci}-${i}">${x.nama} ${x.teks} · ${RP(x.rp)}${x.alasan ? ' · ' + x.alasan : ''}${x.hama ? ' · HAMA: ' + x.hama : ''}</div>`)}</div>`)}</div>` : ''}
      <div class="ket tautan" data-aksi="bukaAturC">${s.aturC ? 'tutup aturan' : 'Atur: selisih wajar & ambang stok bertambah'}</div>${gambarAturC(s)}
      ${c.tab === 'wadah' ? h`<div class="ket" style="font-size: 11px;">Batas susut wajar per wadah per hari diatur di Stok › Wadah literan › Atur (sekarang ${DESIMAL(L.aturWadah().susutWajarKg)} kg).</div>` : ''}
    </section>`;
  }

  function gambarKapur(k) {
    const p = S.susunKapur(k);
    return h`<section data-k="kapur"><div class="kartu" style="gap: 4px; padding: 10px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Papan Kapur · perubahan stok hari ini</div><div class="ket" style="font-size: 11px;">${p.banyak} catatan</div></div>
      ${p.baris.length ? p.baris.map((x, i) => h`<div class="kapur ${x.jenis}" data-k="kp-${x.k}" style="--urut: ${Math.min(i, 16)};"><span class="w">${x.jam}</span><span class="isi-kapur">${x.isi}</span><span class="n">${x.n}</span></div>`) : h`<div class="menolak" style="padding: 12px 0;">Belum ada perubahan stok hari ini.</div>`}
    </div></section>`;
  }
  // ---------- UMUR & PUTARAN (paket brief 9 Okt, butir 2): tab sendiri — papan S9 Gudang tidak disentuh. Kartu pertanyaan → daftar per kelompok buku (karung FIFO ·
  // karung di belakang wadah FIFO sejak dibuka · wadah campuran rata-rata) → ketuk buku = rincian lapisan & perputarannya. Ambang di Atur (owner). Berat, bukan rupiah.
  // ---------- TUGAS GUDANG (owner 26 Nov 2026, sensus ulang 1c B49 B50 B53 B54 + A62): satu tab, empat kartu; angka = gudang-logika / label-logika apa adanya ----------
  function gambarTugas(s) {
    const KG = (n) => DESIMAL(Math.round(n * 100) / 100) + ' kg';
    const T = GD.gdTugas(kini(), waktu()); const M = GD.gdMinus(kini()); const iso = T.iso; const keyIni = iso.slice(0, 7);
    const keyLalu = (() => { const y = Number(keyIni.slice(0, 4)), m = Number(keyIni.slice(5, 7)); return m === 1 ? (y - 1) + '-12' : y + '-' + String(m - 1).padStart(2, '0'); })();
    const B = GD.gdBuang(s.gdBulan === 'lalu' ? keyLalu : keyIni, kini()); const KM = LB.lbRingkasKemasan(kini()); let urut = 0;
    const rpM = (n) => (n < 0 ? '−' + RP(-n) : RP(n)); const maksM = Math.max(1, ...M.top.map((x) => Math.abs(x.rp)));
    const minus = (s.gdSemua ? M.daftar : M.top);
    return h`<section class="stok-tugas" data-k="tugas">
      <div class="tanya">${[['tgs-buka', 'Tugas terbuka', T.n ? T.n + ' di ' + T.nJenis + ' jenis' : 'beres', T.awas], ['tgs-minus', 'Buku minus', M.n ? M.n + ' · ' + rpM(M.rp) : 'tidak ada', M.n > 0], ['tgs-buang', 'Hilang ' + (s.gdBulan === 'lalu' ? 'bulan lalu' : 'bulan ini'), B.diarsip ? 'arsip' : KG(B.total.hilangKg), false], ['tgs-kemas', 'Kemasan bertanggal', KM.lewat.length ? KM.lewat.length + ' lewat' : KM.dekat.length ? KM.dekat.length + ' dekat' : KM.nBertanggal ? 'aman' : '—', KM.lewat.length > 0]]
        .map((c) => h`<div class="kartu-t" data-k="${c[0]}"><div class="q">${c[1]}</div><div class="a ${c[3] ? 'awas' : ''}">${c[2]}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="tgk-tugas"><div class="label">Tugas gudang yang masih terbuka</div>
        <div class="daftar-jawab">${T.daftar.map((x, i) => h`<div class="jawab ${x.n ? '' : 'beres'}" data-k="tg-${x.id}" data-aksi="gdKe" data-i="${i}" style="--urut: ${Math.min(urut++, 16)}; cursor: pointer;">
          <span class="kiri"><span class="nm">${x.nama}</span><span class="w">${x.ket}</span></span><span class="kanan"><span class="n ${x.awas ? 'awas' : ''}">${x.n === null ? '?' : x.n}</span><span class="w">${x.n ? 'buka ›' : 'beres'}</span></span></div>`)}</div>
        ${T.pindahLokasi ? h`<div class="ket" style="font-size: 11px;">${T.pindahLokasi}</div>` : ''}</div>
      ${bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : gambarKejutan(s)}
      <div class="kartu jawaban" data-k="tgk-minus"><div class="label">Stok minus · ${M.n ? M.n + ' buku' : 'tidak ada'}${M.n > M.top.length ? ' · ' + GD.GD_TOP + ' terdalam' : ''}</div>
        ${M.n ? h`<div class="daftar-jawab">${minus.map((x, i) => h`<div class="jawab" data-k="tm-${x.jenis}-${x.kunci}" data-aksi="gdKe" data-dari="minus" data-i="${i}" style="--urut: ${Math.min(urut++, 16)}; cursor: pointer;">
          <span class="kiri"><span class="nm">${i + 1}. ${x.nama}${x.wadah ? ' (buku wadah)' : ''}</span><span class="w">${GD.GD_JENIS_STOK[x.jenis]} · ${x.jalan}</span><span class="batang"><span class="isi-batang awas" style="transform: scaleX(${x.dinilai ? Math.round(Math.abs(x.rp) / maksM * 1000) / 1000 : 0});"></span></span></span>
          <span class="kanan"><span class="n awas">${x.teksJumlah}</span><span class="w">${x.dinilai ? rpM(x.rp) : 'belum bisa dinilai'}</span></span></div>`)}</div>
          ${M.lebih ? h`<div class="kaca-btn kecil" data-aksi="gdSemua" style="align-self: flex-start;">${s.gdSemua ? 'tampilkan ' + GD.GD_TOP + ' terdalam saja' : 'tampilkan semua ' + M.n + ' buku'}</div>` : ''}` : h`<div class="menolak" style="padding: 8px 0;">Tidak ada buku yang minus — beras, kemasan, dan kantong semuanya ≥ 0.</div>`}
        ${M.n ? h`<div class="ket" style="font-size: 11px;">${M.kalimat} Nilai = sisa × modal per satuan yang sama dengan neraca. Ketuk satu baris untuk mencocokkan.</div>` : ''}</div>
      <div class="kartu jawaban" data-k="tgk-buang"><div class="label">Beras hilang, lebih & rusak per jenis · ${B.nama}</div>
        <div class="hg-pil" data-k="tg-bulan"><span class="seg ${s.gdBulan === 'lalu' ? '' : 'aktif'}" data-aksi="gdBulan" data-b="ini">bulan ini</span><span class="seg ${s.gdBulan === 'lalu' ? 'aktif' : ''}" data-aksi="gdBulan" data-b="lalu">bulan lalu</span></div>
        ${B.diarsip ? h`<div class="ket">${B.kalimat}</div>` : B.jenis.length ? h`<div class="daftar-jawab">${B.jenis.map((x) => h`<div class="jawab" data-k="tb-${x.jenis}" style="--urut: ${Math.min(urut++, 16)};">
          <span class="kiri"><span class="nm">${x.jenis}</span><span class="w">${[x.hilangKg ? 'hilang ' + KG(x.hilangKg) : '', x.naikKg ? 'lebih ' + KG(x.naikKg) : '', x.rusakKg ? 'rusak dikembalikan ' + KG(x.rusakKg) + ' (taksiran modal ' + RP(x.rusakRp) + ')' : ''].filter(Boolean).join(' · ') || '—'}${x.merek.length ? ' · ' + x.merek.slice(0, 4).join(', ') + (x.merek.length > 4 ? ' …' : '') : ''}</span></span>
          <span class="kanan"><span class="n ${x.hilangRp < 0 ? 'awas' : ''}">${rpM(x.hilangRp + x.naikRp)}</span><span class="w">hilang − lebih</span></span></div>`)}</div>` : h`<div class="menolak" style="padding: 8px 0;">Tidak ada beras hilang, lebih, atau rusak tercatat.</div>`}
        ${!B.diarsip && (B.bahan.hilangRp || B.bahan.naikRp) ? h`<div class="ket">${B.bahan.nama}: ${rpM(B.bahan.hilangRp + B.bahan.naikRp)}</div>` : ''}
        ${!B.diarsip && B.total.rusakKg ? h`<div class="ket">Nasib barang rusak di karantina: dibuang ${KG(B.nasib.dibuang)} · balik ke pemasok ${KG(B.nasib.dikembalikan_pemasok)} · rework ${KG(B.nasib.dirework)} · ternyata layak ${KG(B.nasib.layak_jual)} · menunggu ${KG(B.nasib.belum_diputuskan)}</div>` : ''}
        <div class="ket ${B.menutup === false ? 'awas-teks' : ''}" style="font-size: 11px;">${B.kalimat} Jenis = setelan Jenis beras (Harga › Jenis beras). Rugi barang rusak sudah tercatat di nota aslinya — angka taksiran modal di sini tidak memotong laba lagi.</div></div>
      <div class="kartu jawaban" data-k="tgk-kemasan"><div class="label">Kemasan bertanggal · keluarkan yang paling cepat lewat</div>
        ${KM.daftar.length ? h`<div class="daftar-jawab">${KM.daftar.map((x) => h`<div class="jawab" data-k="tk-${x.kunci}" style="--urut: ${Math.min(urut++, 16)};">
          <span class="kiri"><span class="nm">${x.nama} · ${ANGKA(x.sisa)} kantong</span><span class="w">${x.teks}</span>${x.lapisan.length > 1 ? h`<span class="w">${x.lapisan.map((l) => tanggalPendek(l.tanggal).replace(/ \d{4}$/, '') + ' ×' + ANGKA(l.unit)).join(' · ')}</span>` : ''}</span>
          <span class="kanan"><span class="n ${x.status === 'lewat' ? 'awas' : ''}">${x.tertua.sisaHari < 0 ? 'lewat' : x.tertua.sisaHari + ' hr'}</span><span class="w">${x.status === 'dekat' ? 'dekat' : x.status === 'lewat' ? 'tarik dari rak' : 'aman'}</span></span></div>`)}</div>`
          : h`<div class="menolak" style="padding: 8px 0;">Belum ada kemasan bertanggal yang bersisa.</div>`}
        ${KM.tanpa.length ? h`<div class="ket">Tanpa tanggal kemas (stok awal / beli jadi): ${KM.tanpa.slice(0, 6).map((x) => x.nama + ' ' + ANGKA(x.sisa)).join(' · ')}${KM.tanpa.length > 6 ? ' …' : ''}</div>` : ''}
        <div class="ket" style="font-size: 11px;">Baik dipakai sebelum = tanggal adukan + ${KM.umurBulan} bulan · tanda dekat ≤ ${KM.ambang} hari (Jual › Label & kartu › Atur label). Yang laku dianggap adukan TERLAMA dulu (sama dengan umur karung) — kemasan di rak yang lebih tua dikeluarkan duluan.</div></div>
    </section>`;
  }
  // ---------- paket P5 (owner 27 Nov 2026, A56): KARTU STOK per merek — tanggal · masuk · keluar · sisa berjalan · harga beli/kg ----------
  function gambarKartuStok(s) {
    const KGt = (n) => { const x = Math.round(Math.abs(n) * 100) / 100; const b = Math.floor(x); const d = Math.round((x - b) * 100); return (n < 0 ? '−' : '') + ANGKA(b) + (d ? ',' + String(d).padStart(2, '0').replace(/0$/, '') : ''); };
    const daftar = SG.sgDaftarKartu(); const kunci = s.ksKunci || (daftar[0] || {}).kunci || '';
    const hariN = s.ksHari || '30'; const iso = waktu().tanggal; const dari = hariN === 'semua' ? '2000-01-01' : (() => { const d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() - (Number(hariN) - 1)); return d.toISOString().slice(0, 10); })();
    const K = kunci ? SG.sgKartuStok(kunci, dari, iso, !!s.ksRinci) : null; const cari = String(s.ksCari || '').toLowerCase();
    const calon = daftar.filter((x) => !cari || x.kunci.toLowerCase().indexOf(cari) >= 0).slice(0, cari ? 24 : 12);
    const baris = K ? (s.ksSemua ? K.baris : K.baris.slice(-60)) : [];
    return h`<section class="stok-kartu" data-k="kartu-stok">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Kartu stok${kunci ? ' · ' + kunci : ''}</div><div class="ket">tiap gerak buku dalam kg, berurutan · sisa berjalan · harga beli per kg di baris barang masuk</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      <div class="kartu" data-k="ks-pilih" style="gap: 6px;"><input class="ketik-nama" id="ksCari" type="text" placeholder="cari nama beras…" value="${s.ksCari || ''}" data-ketik="ksCari">
        <div class="tombol-baris rapat">${calon.map((x) => h`<div class="kaca-btn kecil ${x.kunci === kunci ? 'aktif' : ''}" data-aksi="ksPilih" data-kunci="${x.kunci}" data-k="ks-c-${x.kunci}">${x.kunci} · ${KGt(x.sisa)} kg${x.wadah ? ' (wadah)' : ''}</div>`)}</div>
        <div class="jalur rapat">${[['7', '7 hari'], ['30', '30 hari'], ['90', '90 hari'], ['semua', 'semua']].map(([n, nm]) => h`<div class="seg ${hariN === n ? 'aktif' : ''}" data-aksi="ksHari" data-n="${n}">${nm}</div>`)}<div class="seg ${s.ksRinci ? 'aktif' : ''}" data-aksi="ksRinci">per nota</div></div></div>
      ${!K ? h`<div class="menolak">Belum ada buku beras.</div>` : h`<div class="kartu" data-k="ks-tabel-${kunci}" style="gap: 4px;">
        <div class="op-ringkas"><div>sisa awal ${tanggalPendek(K.dari).replace(/ \d{4}$/, '')}<b>${KGt(K.saldoAwal)} kg</b></div><div>masuk · keluar<b>+${KGt(K.masukKg)} · −${KGt(K.keluarKg)}</b></div><div>sisa sekarang<b>${KGt(K.sisaAkhir)} kg</b></div></div>
        <div class="ks-tabel" data-k="ks-baris">
          <div class="ks-b kepala"><span>tanggal · gerak</span><span>masuk</span><span>keluar</span><span>sisa</span></div>
          ${K.baris.length > baris.length ? h`<div class="ks-b redup"><span>… ${K.baris.length - baris.length} baris lebih awal</span><span></span><span></span><span></span></div>` : ''}
          ${baris.map((r, i) => h`<div class="ks-b ${r.jenis === 'cocok' || r.jenis === 'sesuai' ? (r.keluar ? 'awas' : 'emas') : ''}" data-k="ks-${i}"><span><b>${tanggalPendek(r.tanggal).replace(/ \d{4}$/, '')}${r.jam ? ' ' + r.jam : ''}</b> · ${r.nama}<span class="w">${r.ket}${r.harga !== null && r.harga > 0 ? ' · beli ' + RP(r.harga) + '/kg' + (r.modal && Math.round(r.modal) !== Math.round(r.harga) ? ' (modal ' + RP(Math.round(r.modal)) + '/kg)' : '') : ''}${r.didampingi ? ' · didampingi ' + r.didampingi : ''}</span></span>
            <span>${r.masuk ? '+' + KGt(r.masuk) : ''}</span><span>${r.keluar ? '−' + KGt(r.keluar) : ''}</span><span><b>${KGt(r.sisa)}</b></span></div>`)}
        </div>
        ${K.baris.length > 60 ? h`<div class="kaca-btn kecil" data-aksi="ksSemua" style="align-self: flex-start;">${s.ksSemua ? 'tampilkan 60 terakhir' : 'tampilkan semua ' + K.baris.length + ' baris'}</div>` : ''}
        <div class="ket ${K.menutup ? '' : 'awas-teks'}" style="font-size: 11px;">${K.kalimat} Harga beli terakhir ${RP(K.hargaTerakhir)}/kg · modal di buku ${RP(Math.round(K.modalBuku))}/kg. Hitungan gudang & penyesuaian ikut mengubah sisa (kurang = merah, lebih = emas). ${s.ksRinci ? 'Tiap nota satu baris.' : 'Nota satu jalur di hari yang sama digabung — ketuk "per nota" untuk rinciannya.'}</div></div>`}
    </section>`;
  }

  // ---------- paket P5 (owner 27 Nov 2026, B72 · A50): PRODUKSI per bulan · susut adukan · sampel isi & oplos · rencana produksi ----------
  function gambarProduksi(s, k) {
    const KGt = (n) => { const x = Math.round(Math.abs(n) * 10) / 10; const b = Math.floor(x); const d = Math.round((x - b) * 10); return (n < 0 ? '−' : '') + ANGKA(b) + (d ? ',' + d : ''); }; const D = SG.sgProduksiDeret(k, 6); const ada = D.filter((b) => !b.sebelum); const key = s.prBulan && ada.some((b) => b.key === s.prBulan) ? s.prBulan : (ada[ada.length - 1] || {}).key;
    const B = ada.find((b) => b.key === key) || null; const R = SG.sgRencanaProduksi(k); const maks = Math.max(1, ...ada.map((b) => b.kgJadi)); let urut = 0;
    const pct = (x) => (x === null ? '—' : DESIMAL(x) + ' %');
    return h`<section class="stok-produksi" data-k="produksi">
      <div class="tanya">${[['pr-n', 'Adukan ' + (B ? B.nama : ''), B ? B.adukan + ' adukan' : '—', false], ['pr-kg', 'Kg jadi', B ? KGt(B.kgJadi) + ' kg' : '—', false], ['pr-susut', 'Susut adukan', B ? pct(B.susutPersen) : '—', !!B && B.susutPersen !== null && B.susutPersen < 0],
        ['pr-biaya', 'Kantong + upah per kg', B && B.biayaPerKg !== null ? RP(Math.round(B.biayaPerKg)) : '—', false], ['pr-tanda', 'Tanda (oplos · kurang isi · lebih berat)', B ? (B.tanda.oplos + B.tanda.kurangIsi + B.tanda.lebihBerat ? B.tanda.oplos + ' · ' + B.tanda.kurangIsi + ' · ' + B.tanda.lebihBerat : 'tidak ada') : '—', !!B && B.tanda.oplos + B.tanda.kurangIsi + B.tanda.lebihBerat > 0]]
        .map((c) => h`<div class="kartu-t ${c[3] ? 'merah' : ''}" data-k="${c[0]}"><div class="q">${c[1]}</div><div class="a ${c[3] ? 'awas' : ''}">${c[2]}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="pr-deret"><div class="label">Produksi per bulan · ketuk bulan untuk rinciannya</div>
        <div class="daftar-jawab">${D.map((b) => b.sebelum ? h`<div class="jawab beres" data-k="prd-${b.key}"><span class="kiri"><span class="nm">${b.nama}</span><span class="w">sebelum catatan toko</span></span><span class="kanan"><span class="n">—</span></span></div>`
          : h`<div class="jawab ${b.key === key ? 'dipilih' : ''}" data-k="prd-${b.key}" data-aksi="prBulan" data-bulan="${b.key}" style="--urut: ${Math.min(urut++, 16)}; cursor: pointer;">
            <span class="kiri"><span class="nm">${b.nama}${b.berjalan ? ' · berjalan' : ''}</span><span class="w">${b.adukan} adukan · bahan ${KGt(b.kgBahan)} → jadi ${KGt(b.kgJadi)} kg · susut ${pct(b.susutPersen)} · kantong ${RP(b.kantongRp)} + upah ${RP(b.upahRp)}${b.tanda.oplos ? ' · ' + b.tanda.oplos + ' OPLOS' : ''}${b.tanda.kurangIsi ? ' · ' + b.tanda.kurangIsi + ' kurang isi' : ''}${b.tanda.lebihBerat ? ' · ' + b.tanda.lebihBerat + ' lebih berat' : ''}</span>
              <span class="batang"><span class="isi-batang" style="transform: scaleX(${Math.round(b.kgJadi / maks * 1000) / 1000});"></span></span></span>
            <span class="kanan"><span class="n">${KGt(b.kgJadi)}</span><span class="w">kg jadi</span></span></div>`)}</div>
        <div class="ket" style="font-size: 11px;">Angka bahan, jadi, kantong & upah = catatan adukannya (sama dengan Laporan › Pondasi › dikemas sendiri). Susut adukan = (kg bahan − kg jadi) ÷ kg bahan. Pindah buku, takar ke wadah & kemasan beli jadi tidak ikut.</div></div>
      ${B ? h`<div class="kartu jawaban" data-k="pr-bulan-${B.key}"><div class="label">${B.nama} · ${B.daftar.length} adukan${B.tanda.sampel ? ' · ' + B.tanda.sampel + ' sampel isi ditimbang' : ''}</div>
        ${B.daftar.length ? h`<div class="daftar-jawab">${B.daftar.slice().reverse().map((g) => h`<div class="jawab ${g.awas ? 'awas' : ''}" data-k="pra-${g.batch}"><span class="kiri"><span class="nm">${g.bahanTeks} → ${g.hasilTeks}</span>
            <span class="w">${tanggalPendek(g.tanggal).replace(/ \d{4}$/, '')}${g.jam ? ' ' + g.jam : ''} · ${KGt(g.kgBahan)} → ${KGt(g.kgJadi)} kg${g.jenis === 'rework' ? ' · rework karantina' : ''}</span>
            ${g.oplos ? h`<span class="w awas-teks">OPLOS disimpan owner: ${g.oplos.alasan}</span>` : ''}${g.lebihBerat ? h`<span class="w awas-teks">hasil LEBIH BERAT ${KGt(g.kgJadi - g.kgBahan)} kg dari bahannya</span>` : ''}
            ${g.sampel.map((x, i) => h`<span class="w ${x.kurang ? 'awas-teks' : ''}" data-k="pra-${g.batch}-s${i}">sampel ${x.nama}: ${x.unit} kantong ${KGt(x.kg)} kg → rata-rata ${DESIMAL(Math.round(x.rata * 1000) / 1000)} kg (${x.persen > 0 ? '+' : ''}${DESIMAL(x.persen)} %)${x.kurang ? ' · KURANG ISI' : ''}</span>`)}</span>
            <span class="kanan"><span class="n ${g.susutPersen !== null && g.susutPersen < 0 ? 'awas' : ''}">${pct(g.susutPersen)}</span><span class="w">susut</span></span></div>`)}</div>` : h`<div class="menolak">Belum ada adukan di bulan ini.</div>`}
        ${B.menutup ? '' : h`<div class="ket awas-teks">Jumlah per adukan tidak sama dengan Laporan › Pondasi — laporkan.</div>`}</div>` : ''}
      <div class="kartu jawaban" data-k="pr-rencana"><div class="label">Rencana produksi · yang perlu diaduk untuk ${R.targetHari} hari</div>
        ${R.daftar.length ? h`<div class="daftar-jawab">${R.daftar.map((x) => h`<div class="jawab ${x.hariHabis <= 2 ? 'awas' : ''}" data-k="prr-${x.kunci}"><span class="kiri"><span class="nm">aduk ${x.unit} × ${x.nama}</span>
            <span class="w">sisa ${ANGKA(x.sisa)} · laku ±${DESIMAL(Math.round(x.laju * 10) / 10)}/hari → habis ${DESIMAL(Math.round(x.hariHabis * 10) / 10)} hari · jadi ${KGt(x.kgJadi)} kg, bahan ±${KGt(x.kgBahan)} kg${x.susutPersen ? ' (susut terakhir ' + DESIMAL(x.susutPersen) + ' %)' : ''}</span>
            ${x.bahan.length ? h`<span class="w ${x.bahanKurang.length ? 'awas-teks' : ''}">bahan biasa: ${x.bahan.map((b) => b.merk + ' ' + KGt(b.kg) + ' kg (buku ' + (b.sisa === null ? '?' : KGt(b.sisa)) + ')').join(' + ')}${x.bahanKurang.length ? ' · bahan KURANG' : ''}</span>` : ''}
            ${x.kantong ? h`<span class="w ${x.kantong.kurang ? 'awas-teks' : ''}">kantong ${x.kantong.label} · sisa ${ANGKA(x.kantong.sisa)} lembar${x.kantong.kurang ? ' · KURANG' : ''}</span>` : ''}</span>
            <span class="kanan"><span class="n">${x.unit}</span><span class="w">unit</span></span></div>`)}</div>` : h`<div class="menolak">${R.kalimat}.</div>`}
        <div class="ket" style="font-size: 11px;">${R.rumus}. Rencana ini dihitung, tidak disimpan — catat adukannya di Stok › Adukan sesudah jadi.</div></div>
    </section>`;
  }
  // ---------- paket P5 (owner 27 Nov 2026, A92): OPNAME KEJUTAN — owner saja (staf tidak membaca setelannya; kartu ini tidak digambar untuk akun staf) ----------
  function gambarKejutan(s) {
    const S0 = SG.sgKejutanStatus(kini()); const A = S0.atur; const a = s.aturKj; const kataK = { nanti: 'nanti', 'hari ini': 'HARI INI', menunggu: 'menunggu', selesai: 'selesai', terlewat: 'terlewat' };
    const isian = (kolom, nama) => h`<div><div class="ket">${nama}</div><input class="ketik-nama" id="kj-${kolom}" type="text" inputmode="numeric" value="${a[kolom]}" data-ketik="kjKetik" data-kolom="${kolom}"></div>`;
    return h`<div class="kartu jawaban" data-k="tgk-kejutan"><div class="label">Opname kejutan · tanggal & merek diundi · hanya owner yang melihat</div>
      <div class="ket ${S0.harus.length ? 'awas-teks' : ''}">${S0.kalimat}${A.aktif ? ' · ' + A.kaliSebulan + '× sebulan, ' + A.nMerek + ' merek tiap kali' : ''}</div>
      ${A.aktif && S0.daftar.length ? h`<div class="daftar-jawab">${S0.daftar.map((x) => h`<div class="jawab ${x.keadaan === 'selesai' ? 'beres' : ''}" data-k="kj-${x.tanggal}"><span class="kiri"><span class="nm">${tanggalPendek(x.tanggal)}</span>
          <span class="w">${x.merek.length ? x.merek.map((m) => m + (x.sudah.indexOf(m) >= 0 ? ' ✓' : '')).join(' · ') : 'merek diundi pada harinya'}${x.keadaan === 'terlewat' ? ' · belum dihitung: ' + x.belum.join(', ') : ''}</span></span>
          <span class="kanan"><span class="n ${x.keadaan === 'hari ini' || x.keadaan === 'menunggu' || x.keadaan === 'terlewat' ? 'awas' : ''}">${kataK[x.keadaan]}</span></span></div>`)}</div>` : ''}
      ${a ? h`<div class="ps-form dua">${isian('kaliSebulan', 'Berapa kali sebulan (1–31)')}${isian('nMerek', 'Berapa merek tiap kali (1–50)')}</div>
          <div class="tombol-baris rapat"><div class="kaca-btn" data-aksi="bukaAturKj">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturKj">${A.aktif ? 'SIMPAN' : 'NYALAKAN OPNAME KEJUTAN'}</div>${A.aktif ? h`<div class="kaca-btn putus" data-aksi="simpanAturKj" data-ulang="1">undi ulang tanggal</div><div class="kaca-btn putus" data-aksi="simpanAturKj" data-mati="1">matikan</div>` : ''}</div>`
        : h`<div class="kaca-btn kecil" data-aksi="bukaAturKj" style="align-self: flex-start;">${A.aktif ? 'Atur opname kejutan ›' : 'Nyalakan opname kejutan ›'}</div>`}
      <div class="ket" style="font-size: 11px;">Pengingatnya muncul di lonceng owner pada tanggal itu: hitung tumpukan merek yang diundi di Stok › Cocokkan (sampai ${SG.SG_KEJUTAN_TENGGANG} hari sesudahnya = selesai). Merek diundi dari yang berisi di gudang pagi itu. Bawaan 2× sebulan, 3 merek (pilihan owner 27 Nov 2026). Pengingat opname rutin tiap N hari tetap jalan.</div></div>`;
  }
  function gambarUmur(s, k) {
    const U = S.umPapan(k, s.umTanya, s.umPilih); const A = U.atur; const ak = opsi.akun ? opsi.akun() : null; const au = s.aturUm; let urut = 0;
    const isian = (id, kolom, nama) => h`<div><div class="ket">${nama}</div><input class="ketik-nama" id="${id}" type="text" inputmode="numeric" value="${au[kolom]}" data-ketik="umKetikAtur" data-kolom="${kolom}"></div>`;
    return h`<section class="stok-umur" data-k="umur">
      <div class="tanya">${U.kartu.map((c) => h`<div class="kartu-t ${c.id === U.aktif ? 'aktif' : ''} ${c.merah ? 'merah' : ''}" data-aksi="umTanya" data-id="${c.id}" data-k="um-k-${c.id}"><div class="q">${c.q}</div><div class="a ${c.awas ? 'awas' : ''}">${c.a}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="um-jawab-${U.aktif}">
        <div class="label">${U.judul}</div>
        ${U.kelompok.length ? U.kelompok.map((g) => h`<div data-k="um-g-${g.id}" style="display: flex; flex-direction: column; gap: 2px;">${g.label ? h`<div class="ket" style="font-weight: 600; padding-top: 6px;">${g.label}</div>` : ''}
          <div class="daftar-jawab">${g.baris.map((b) => h`<div class="jawab ${b.rinci ? 'dipilih' : ''}" data-k="um-${g.id}-${b.kunci}" data-aksi="umPilih" data-kunci="${b.kunci}" style="--urut: ${Math.min(urut++, 16)}; cursor: pointer;">
            <span class="kiri"><span class="nm">${b.nama}</span><span class="w">${b.ket}</span><span class="batang"><span class="isi-batang ${b.awas ? 'awas' : ''}" style="transform: scaleX(${Math.round(b.isi * 1000) / 1000});"></span></span>
              ${b.rinci ? b.rinci.map((x, i) => h`<span class="w ${x.awas ? 'awas-teks' : ''}" data-k="um-r-${b.kunci}-${i}" style="display: block; padding-top: 3px;">${x.teks}</span>`) : ''}</span>
            <span class="kanan"><span class="n ${b.awas ? 'awas' : ''}">${b.n}</span><span class="w">${b.nKet}</span></span></div>`)}</div></div>`)
          : h`<div class="menolak" style="padding: 12px 0;">${U.kosong}</div>`}
        <div class="rumus">${U.rumus}</div>
        <div class="ket" style="font-size: 11.5px;" data-k="um-tutup">${U.tutup}</div>
        <div class="ket" style="font-size: 11px;">Ketuk satu baris untuk rincian lapisan & perputarannya. Umur & putaran = BERAT (kg); nilai rupiah stok ada di Gudang & HPP (cara hitung modalnya — rata-rata atau FIFO — di kartu HPP).</div>
      </div>
      ${au ? h`<div class="kartu" data-k="atur-um" style="gap: 8px;"><div class="label">Ambang umur & putaran · angka owner</div><div class="ps-form dua">
        ${isian('umAmbangUmur', 'ambangUmurHari', 'Lambat laku bila umur stok lebih dari (hari)')}${isian('umAmbangHari', 'ambangHariStok', 'Lambat laku bila hari stok lebih dari (hari)')}${isian('umPeriode', 'periodeHari', 'Periode perputaran (hari, 7–120)')}</div>
        <div class="label" data-k="atur-um-target">Target hari stok toko · dalam rupiah (Laporan › Mingguan & Dasbor)</div><div class="ps-form dua">
        ${isian('umTargetMin', 'targetHariMin', 'Stok tipis bila cukup untuk kurang dari (hari)')}${isian('umTargetMaks', 'targetHariMaks', 'Modal kebanyakan diam bila lebih dari (hari)')}</div>
        <div class="ket" style="font-size: 11px;">Hari stok toko = nilai modal stok (beras karung + kemasan) ÷ modal barang yang terjual per hari. Bawaan 7–14 hari (keputusan owner 27 Nov 2026).</div>
        <div class="label" data-k="atur-um-lapisan">Umur stok dalam rupiah · lapisan (Dasbor › Mutu usaha)</div><div class="ps-form dua">${isian('umTua', 'umurTuaHari', 'Stok lama bila umurnya lebih dari (hari)')}</div>
        <div class="ket" style="font-size: 11px;">Lapisan: sampai ambang umur di atas · sampai batas stok lama · lebih tua. Bawaan 60 hari (paket P3).</div>
        <div class="label" data-k="atur-um-simpan">Batas simpan · tanda kedua, merah</div><div class="ps-form dua">
        ${isian('umBatasSimpan', 'batasSimpanHari', 'Lewat batas simpan bila umur stok lebih dari (hari)')}</div>
        <div class="ket" style="font-size: 11px;">Sesudah lambat laku, stok yang umurnya lewat batas ini ditandai merah di Umur & putaran, Tugas gudang & Dasbor. Bawaan 120 hari (±4 bulan, keputusan owner 27 Nov 2026).</div>
        <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAturUm">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAturUm">SIMPAN AMBANG</div></div></div>`
      : bukanOwner(ak) ? h`<div class="kaca-btn kecil mati" data-aksi="tombolMati" data-kal="Ambang umur & putaran diatur owner" style="align-self: flex-start;">Atur ambang · owner saja</div>`
      : h`<div class="kaca-btn kecil" data-aksi="bukaAturUm" style="align-self: flex-start;">Atur ambang umur, hari stok & periode putaran ›</div>`}
      <div class="ket" style="font-size: 11px;" data-k="um-ambang">Ambang sekarang: umur stok > ${A.ambangUmurHari} hari · hari stok > ${A.ambangHariStok} hari · perputaran ${A.periodeHari} hari · target hari stok toko ${A.targetHariMin}–${A.targetHariMaks} hari · stok lama > ${A.umurTuaHari} hari · batas simpan ${A.batasSimpanHari} hari — ${A.dariOwner ? 'diatur owner' + (A.sejak ? ' ' + tanggalPendek(A.sejak) : '') : 'angka bawaan (perkiraan) — bisa diubah di Atur'}${bukanOwner(ak) && !A.dariOwner ? ' · akun ini tidak membaca setelan owner, jadi memakai angka bawaan' : ''}.</div>
    </section>`;
  }

  // ---------- ADUKAN (ST2-C "Timbangan Adukan"): bahan masuk ⇄ hasil jadi di atas; bahan (karung dari gudang / kemasan jadi dibongkar) → hasil (nama · ukuran · unit · kantong) → biaya → buku ----------
  function gambarAdukan(s) {
    const d = s.adukan || A.drafAdukanKosong(waktu()); const ha = A.hitungAdukan(d); const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg'; const RPb = (n) => RP(Math.round(n));
    const calonB = A.calonBahan(); const calonN = A.calonNamaHasil(); const calonK = A.calonKemasanBahan(); const buka = s.bukaA ? A.rincianAdukan(s.bukaA) : null; const buku = A.daftarAdukan(12);
    const susutTeks = (masuk, jadi, susut) => (!(masuk > 0) ? 'isi bahannya dulu, lalu hasilnya' : susut > 0.0001 ? 'susut ' + KG(susut) + ' (' + Math.round(susut / masuk * 1000) / 10 + ' %) — terserap ke modal hasil, bukan hilang dari buku' : susut < -0.0001 ? 'hasil LEBIH ' + KG(-susut) + ' dari bahannya — cek ketikan' : 'pas — kg masuk = kg jadi');
    const timbang = (masuk, rpMasuk, jadi, rpJadi, kunci) => h`<div class="ad-timbang" data-k="tb-${kunci}"><div class="sisi"><b>${KG(masuk)}</b>bahan · <span ${mentah('data-gulir="' + Math.round(rpMasuk) + '"')}>${RPb(rpMasuk)}</span></div><span class="panah">⇄</span><div class="sisi"><b>${KG(jadi)}</b>jadi · <span ${mentah('data-gulir="' + Math.round(rpJadi) + '"')}>${RPb(rpJadi)}</span></div></div>`;
    const kosong = !(d.bahan.some((b) => b.merk || b.kg) || d.bahanKemasan.length || d.hasil.some((x) => x.nama || x.unit) || d.upah);
    const pratinjau = buka && buka.bisaKoreksi ? A.pratinjauKoreksiAdukan(buka.batch, s.koreksiA.total) : [];
    return h`<section class="stok-adukan" data-k="adukan">
      <div class="kepala-lembar"><div><div class="serif" style="font-size: 20px;">Adukan</div><div class="ket">karung dibongkar jadi kemasan · satu adukan = satu kesatuan biaya, dibagi ke tiap hasil menurut kg</div></div>
        <div class="kaca-btn" data-aksi="tutupLembar">tutup</div></div>
      <div class="kartu" data-k="timbang-draf" style="gap: 6px;"><div class="label">Bahan masuk ⇄ hasil jadi</div>${timbang(ha.kgMasuk, ha.nilaiBahan, ha.kgJadi, ha.total, 'draf')}
        <div class="ket ${ha.kgMasuk > 0 && Math.abs(ha.susutPersen) > A.BATAS_SUSUT_ADUKAN * 100 ? 'awas-teks' : ''}">${susutTeks(ha.kgMasuk, ha.kgJadi, ha.susutKg)}</div></div>
      <div class="kartu" data-k="bahan" style="gap: 6px;"><div class="label">Bahan · karung dari tumpukan gudang</div>
        ${ha.bahan.map((b, i) => h`<div class="baris-adukan ${b.terisi && b.masalah ? 'awas' : ''}" data-k="ab-${i}">
          <input class="ketik-nama" id="abMerk${i}" type="text" placeholder="nama karung" value="${d.bahan[i].merk}" data-ketik="aKetik" data-kel="bahan" data-kolom="merk" data-i="${i}">
          ${!b.merk ? h`<div class="tombol-baris rapat" data-k="calon-bahan-${i}">${calonB.slice(0, 8).map((c) => h`<div class="kaca-btn kecil" data-aksi="aPilih" data-kel="bahan" data-kolom="merk" data-i="${i}" data-nilai="${c.merk}">${c.merk} · ${KG(c.sisaKg)}</div>`)}</div>` : ''}
          <div class="ps-form dua"><div><div class="ket">Kg dipakai${b.sisaKg !== null ? ' · buku ' + KG(b.sisaKg) : ''}</div><input class="ketik-nama" id="abKg${i}" type="text" inputmode="decimal" placeholder="0" value="${d.bahan[i].kg}" data-ketik="aKetik" data-kel="bahan" data-kolom="kg" data-i="${i}"></div>
            <div><div class="ket">tambah cepat · 1 karung = 50 kg</div><div class="jalur rapat bungkus"><div class="seg" data-aksi="aTambahKg" data-i="${i}" data-kg="50">+50 kg</div><div class="seg" data-aksi="aTambahKg" data-i="${i}" data-kg="25">+25 kg</div></div></div></div>
          <div class="ket ${b.terisi && b.masalah ? 'awas-teks' : ''}">${b.terisi && b.masalah ? b.masalah : b.sah ? 'modal ' + RPb(b.hpp) + '/kg → ' + RPb(b.nilai) : 'pilih namanya, lalu kg yang dipakai'}${ha.bahan.length > 1 || b.terisi ? h`<span class="tautan" style="float: right;" data-aksi="aLepas" data-kel="bahan" data-i="${i}">lepas</span>` : ''}</div></div>`)}
        ${ha.bahanKemasan.map((b, i) => h`<div class="baris-adukan ${b.terisi && b.masalah ? 'awas' : ''}" data-k="ak-${i}"><div class="ket">Kemasan jadi yang dibongkar</div>
          <div class="tombol-baris rapat" data-k="calon-kemasan-${i}">${calonK.length ? calonK.map((c) => h`<div class="kaca-btn kecil ${d.bahanKemasan[i].kunci === c.kunci ? 'aktif' : ''}" data-aksi="aPilih" data-kel="bahanKemasan" data-kolom="kunci" data-i="${i}" data-nilai="${c.kunci}">${c.namaProduk} ${DESIMAL(c.ukuranKemasan)} kg · sisa ${c.sisaUnit}</div>`) : h`<div class="ket">Tidak ada kemasan 50 / 25 kg yang bersisa.</div>`}</div>
          <div class="ps-form dua"><div><div class="ket">Unit dibongkar${b.sisaUnit !== null ? ' · sisa ' + b.sisaUnit : ''}</div><input class="ketik-nama" id="akUnit${i}" type="text" inputmode="numeric" placeholder="0" value="${d.bahanKemasan[i].unit}" data-ketik="aKetik" data-kel="bahanKemasan" data-kolom="unit" data-i="${i}"></div>
            <div class="ket" style="align-self: end;">${b.sah ? KG(b.kg) + ' · modal ' + RPb(b.hpp) + '/unit → ' + RPb(b.nilai) : b.masalah || 'kantong lamanya hangus, nilainya masuk adukan ini'}</div></div>
          <div class="ket"><span class="tautan" data-aksi="aLepas" data-kel="bahanKemasan" data-i="${i}">lepas</span></div></div>`)}
        <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="aTambah" data-kel="bahan">+ karung lain</div><div class="kaca-btn putus" data-aksi="aTambah" data-kel="bahanKemasan">+ bongkar kemasan jadi 50 / 25 kg</div></div></div>
      <div class="kartu" data-k="hasil" style="gap: 6px;"><div class="label">Hasil · kemasan yang jadi</div>
        ${ha.hasil.map((x, i) => h`<div class="baris-adukan ${x.terisi && x.masalah ? 'awas' : ''}" data-k="ah-${i}">
          <input class="ketik-nama" id="ahNama${i}" type="text" placeholder="nama di kemasan (Kembang, Putri Agri, Ascent…)" value="${d.hasil[i].nama}" data-ketik="aKetik" data-kel="hasil" data-kolom="nama" data-i="${i}">
          ${!x.nama ? h`<div class="tombol-baris rapat" data-k="calon-nama-${i}">${calonN.slice(0, 8).map((n) => h`<div class="kaca-btn kecil" data-aksi="aPilih" data-kel="hasil" data-kolom="nama" data-i="${i}" data-nilai="${n}">${n}</div>`)}</div>` : ''}
          <div class="ps-form tiga"><div><div class="ket">Ukuran</div><div class="jalur rapat bungkus">${A.UKURAN_HASIL_PILIHAN.map((u) => h`<div class="seg ${Number(d.hasil[i].ukuran) === u ? 'aktif' : ''}" data-aksi="aPilih" data-kel="hasil" data-kolom="ukuran" data-i="${i}" data-nilai="${u}">${u} kg</div>`)}</div></div>
            <div><div class="ket">Unit jadi</div><input class="ketik-nama" id="ahUnit${i}" type="text" inputmode="numeric" placeholder="0" value="${d.hasil[i].unit}" data-ketik="aKetik" data-kel="hasil" data-kolom="unit" data-i="${i}"></div>
            <div><div class="ket">Kantong${x.kantongSisa !== null ? ' · sisa ' + x.kantongSisa + ' lembar' : ''}</div><div class="jalur rapat bungkus"><div class="seg ${!d.hasil[i].kantongJenis ? 'aktif' : ''}" data-aksi="aPilih" data-kel="hasil" data-kolom="kantongJenis" data-i="${i}" data-nilai="">tanpa</div>
              ${A.kantongUntuk(x.ukuran).map((k) => h`<div class="seg ${d.hasil[i].kantongJenis === k.jenis ? 'aktif' : ''}" data-aksi="aPilih" data-kel="hasil" data-kolom="kantongJenis" data-i="${i}" data-nilai="${k.jenis}">${k.label.replace(/^\d+ kg — /, '')} · ${RP(k.hppPerPcs)}</div>`)}</div></div></div>
          ${d.hasil[i].kantongJenis ? h`<div class="ps-form dua"><div><div class="ket">Lembar kantong dipakai</div><input class="ketik-nama" id="ahKantong${i}" type="text" inputmode="numeric" placeholder="${x.unit || 0}" value="${d.hasil[i].kantongJumlah}" data-ketik="aKetik" data-kel="hasil" data-kolom="kantongJumlah" data-i="${i}"></div><div class="ket" style="align-self: end;">${x.kantongTanpaCacah ? 'lembarnya kosong = kantong terhitung gratis' : RP(x.biayaKantong) + ' masuk biaya adukan'}</div></div>` : ''}
          ${x.sah || d.hasil[i].sampelUnit || d.hasil[i].sampelKg ? h`<div class="ps-form dua" data-k="ah-sampel-${i}"><div><div class="ket">Timbang sampel · berapa kantong ditimbang (boleh kosong)</div><input class="ketik-nama" id="ahSampelU${i}" type="text" inputmode="numeric" placeholder="0" value="${d.hasil[i].sampelUnit || ''}" data-ketik="aKetik" data-kel="hasil" data-kolom="sampelUnit" data-i="${i}"></div>
            <div><div class="ket">Berat SELURUH sampel itu (kg)</div><input class="ketik-nama" id="ahSampelKg${i}" type="text" inputmode="decimal" placeholder="0" value="${d.hasil[i].sampelKg || ''}" data-ketik="aKetik" data-kel="hasil" data-kolom="sampelKg" data-i="${i}"></div></div>
          ${x.sampel ? h`<div class="${x.sampel.masalah ? 'ket awas-teks' : x.sampel.kurang ? 'pita-info awas' : 'ket'}" data-k="ah-sampel-hasil-${i}">${x.sampel.masalah ? x.sampel.masalah : (x.sampel.kurang ? 'KURANG ISI — ' : 'Isi sesuai label — ') + x.sampel.unit + ' kantong = ' + DESIMAL(x.sampel.kg) + ' kg → rata-rata ' + DESIMAL(Math.round(x.sampel.rata * 1000) / 1000) + ' kg per kantong ' + DESIMAL(x.ukuran) + ' kg (' + (x.sampel.persen > 0 ? '+' : '') + DESIMAL(x.sampel.persen) + ' %)' + (x.sampel.kurang ? '. Tetap bisa disimpan; tandanya ikut di Stok › Produksi.' : '')}</div>` : ''}` : ''}
          <div class="ket ${x.terisi && x.masalah ? 'awas-teks' : ''}">${x.terisi && x.masalah ? x.masalah : x.sah ? KG(x.kg) + ' · modal ' + RPb(x.hppPerUnit || 0) + '/unit (' + RPb(x.hppPerKg || 0) + '/kg)' : 'nama, ukuran, jumlah unit — kantongnya kalau pakai'}${ha.hasil.length > 1 || x.terisi ? h`<span class="tautan" style="float: right;" data-aksi="aLepas" data-kel="hasil" data-i="${i}">lepas</span>` : ''}</div></div>`)}
        <div class="tombol-baris rapat"><div class="kaca-btn putus" data-aksi="aTambah" data-kel="hasil">+ ukuran / nama lain dari adukan yang sama</div></div></div>
      <div class="kartu" data-k="biaya" style="gap: 6px;"><div class="label">Biaya adukan</div>
        <div class="ps-form dua"><div><div class="ket">Tanggal</div><input class="ketik-nama" id="aTanggal" type="date" value="${d.tanggal}" data-ketik="aKetik" data-kolom="tanggal"></div>
          <div><div class="ket">Upah kemas (Rp)</div><input class="ketik-nama" id="aUpah" type="text" inputmode="numeric" placeholder="0" value="${d.upah}" data-ketik="aKetik" data-kolom="upah"></div></div>
        <div class="ket">bahan ${RPb(ha.nilaiBahan)} + kantong ${RP(ha.biayaKantong)} + upah ${RP(ha.upah)} = <b>${RPb(ha.total)}</b> → dibagi ke tiap hasil menurut kg; sisa pembulatan ke baris terakhir supaya jumlahnya persis. Kas tidak bergerak (upah masuk gaji).</div>
        ${ha.lebihBerat ? h`<div class="pita-info awas" data-k="ad-lebih-berat">Hasil ${KG(ha.kgJadi)} LEBIH BERAT ${KG(ha.kgJadi - ha.kgMasuk)} dari bahannya ${KG(ha.kgMasuk)} — beras tidak bertambah saat dikemas. Cek ketikan kg bahan / unit hasil. Kalau disimpan, adukan ini ditandai di Stok › Produksi.</div>` : ''}
        ${ha.kelas.status === 'oplos' ? h`<div class="pita-info awas" data-k="ad-oplos">${ha.kelas.teks}. Keputusan owner: bahan berkelas lebih rendah dari label hasilnya DITAHAN — akun staf tidak bisa menyimpan.${bukanOwner(opsi.akun ? opsi.akun() : null) ? ' Ganti bahannya atau nama / label hasilnya, atau minta owner.' : ' Owner tetap bisa menyimpan dengan alasan + ketuk dua kali; adukannya ditandai merah.'}</div>
          ${!bukanOwner(opsi.akun ? opsi.akun() : null) ? h`<div><div class="ket">Alasan menyimpan adukan oplos ini (wajib)</div><input class="ketik-nama" id="aAlasanOplos" type="text" placeholder="mis. label akan diganti medium besok" value="${d.alasanOplos || ''}" data-ketik="aKetik" data-kolom="alasanOplos"></div>` : ''}`
          : ha.kelas.status === 'belum' ? h`<div class="ket" data-k="ad-kelas">${ha.kelas.teks}.</div>` : ha.kelas.status === 'aman' ? h`<div class="ket" data-k="ad-kelas" style="font-size: 11px;">Kelas: ${ha.kelas.teks.toLowerCase()}.</div>` : ''}
        <div class="kaca-btn aktif emas" data-aksi="aSimpan">SIMPAN ADUKAN · ${RPb(ha.total)}</div>
        ${!kosong ? h`<div class="ket tautan" data-aksi="aBaru">kosongkan</div>` : ''}</div>
      <div class="kartu" data-k="buku-adukan" style="gap: 6px;"><div class="label">Buku adukan · ketuk untuk rincian, koreksi biaya, atau hapus</div>
        ${buku.length ? buku.map((a) => h`<div class="jawab ${s.bukaA === a.batch ? 'dipilih' : ''}" data-k="ba-${a.batch}" data-aksi="aBuka" data-batch="${a.batch}"><span class="kiri"><span class="nm">${a.bahanTeks} → ${a.hasilTeks}</span><span class="w">${tanggalPendek(a.tanggal)}${a.jam ? ' ' + a.jam : ''}${a.dikoreksi ? ' · dikoreksi' : ''}${a.jenis === 'rework' ? ' · rework karantina' : a.jenis === 'gabungKarung' ? ' · gabung karung (lama)' : ''}</span></span>
          <span class="kanan"><span class="n">${RP(a.total)}</span><span class="w">${KG(a.kgMasuk)} → ${KG(a.kgJadi)}</span></span></div>`) : h`<div class="ket">Belum ada adukan.</div>`}</div>
      ${buka ? h`<div class="kartu rincian-wadah" data-k="rincian-${buka.batch}" style="gap: 8px;"><div class="label">${tanggalPendek(buka.tanggal)}${buka.jam ? ' ' + buka.jam : ''} · ${buka.bahanTeks} → ${buka.hasilTeks}</div>
        ${timbang(buka.kgMasuk, buka.biaya.bahan, buka.kgJadi, buka.biaya.total, 'r' + buka.batch)}<div class="ket">${susutTeks(buka.kgMasuk, buka.kgJadi, buka.susutKg)}</div>
        <div class="ket">bahan ${RPb(buka.biaya.bahan)} · kantong ${RPb(buka.biaya.kantong)} · upah ${RPb(buka.biaya.upah)} · total tercatat <b>${RPb(buka.biaya.total)}</b>${buka.dikoreksi ? ' (sudah dikoreksi)' : ''}</div>
        ${buka.hasil.map((x) => h`<div class="jawab" data-k="rh-${x.id}"><span class="kiri"><span class="nm">${x.unit} × ${x.nama} ${DESIMAL(x.ukuran)} kg</span><span class="w">${x.kantong} · sisa sekarang ${x.sisaKini} unit</span></span><span class="kanan"><span class="n">${RPb(x.hppPerUnit)}</span><span class="w">/unit · ${RPb(x.bagian)}</span></span></div>`)}
        ${buka.riwayat.length ? h`<div class="ket">Jejak koreksi: ${buka.riwayat.map((r) => r.pada + ' · ' + r.nama + ' → ' + RPb(r.hppPerUnit) + '/unit (' + r.alasan + ')').join(' · ')}</div>` : ''}
        ${buka.bisaKoreksi ? h`<div class="label">Koreksi satu kesatuan · total biaya adukan yang benar</div>
          <div class="ps-form dua"><div><div class="ket">Total biaya (Rp)</div><input class="ketik-nama" id="akTotal" type="text" inputmode="numeric" placeholder="${Math.round(buka.biaya.total)}" value="${s.koreksiA.total}" data-ketik="aKetikKoreksi" data-kolom="total"></div>
            <div><div class="ket">Alasan koreksi / hapus (wajib)</div><input class="ketik-nama" id="akAlasan" type="text" placeholder="mis. lupa upah kemas" value="${s.koreksiA.alasan}" data-ketik="aKetikKoreksi" data-kolom="alasan"></div></div>
          ${pratinjau.length ? h`<div class="ket" data-k="pratinjau-koreksi">bagi ulang: ${pratinjau.map((p) => p.nama + ' ' + RPb(p.lama) + ' → ' + RPb(p.baru) + '/unit').join(' · ')}</div>` : ''}
          ${tolakKunciTanggal(buka.tanggal, '') ? h`<div class="kaca-btn putus" data-aksi="kpCocok" data-kunci="${buka.hasil[0] ? 'kemasan|' + kunciKemasan(buka.hasil[0].nama, buka.hasil[0].ukuran) : ''}">${tolakKunciTanggal(buka.tanggal, '').split(' — ')[0]} — cocokkan stok hari ini</div><div class="ket awas-teks">Biaya adukan bulan terkunci tidak bisa dikoreksi (K2); hasil yang tidak pernah jadi dibetulkan lewat Cocokkan HARI INI.</div>`
            : h`<div class="tombol-baris rapat"><div class="kaca-btn aktif" data-aksi="aKoreksi">KOREKSI TOTAL → bagi ulang</div><div class="kaca-btn ${!buka.bisaHapus ? 'mati' : s.yakinHapusA ? 'awas' : 'putus'}" data-aksi="aHapus">${s.yakinHapusA ? 'YAKIN HAPUS seluruh adukan' : 'hapus adukan'}</div></div>`}
          <div class="ket ${buka.bisaHapus ? '' : 'awas-teks'}">${buka.bisaHapus ? 'Hapus = ' + buka.bahanTeks + ' kembali ke stok asal, ' + buka.hasilTeks + ' dicabut dari stok kemasan, kantongnya kembali; jejaknya ke buku hapus.' : buka.takBisaHapus}</div>`
          : h`<div class="ket awas-teks">${buka.takBisaKoreksi}</div>`}</div>` : ''}
      ${buka ? kartuLabelAdukan(buka.batch, s) : ''}
      ${C.bukuHapus(6).length ? h`<div class="kartu" data-k="buku-hapus-adukan" style="gap: 4px;"><div class="label">Buku hapus</div>${C.bukuHapus(6).map((x) => h`<div class="ket" data-k="bha-${x.id}">${tanggalPendek(x.tanggal)} ${x.jam} · ${x.koleksi === 'produksiKemasan' ? 'adukan' : /stokBahan/.test(x.koleksi) ? 'beli kantong ' + x.pemasok : 'kedatangan ' + x.pemasok} ${tanggalPendek(x.tanggalDok)} · ${x.ringkas} — ${x.alasan}</div>`)}</div>` : ''}
    </section>`;
  }
  // ---------- KARANTINA: barang kembali yang menunggu satu keputusan ----------
  function gambarKarantina(s) {
    const q = Q.daftarKarantina(waktu()); const buka = q.antre.find((x) => x.id === s.qBuka) || null;
    return h`<section class="stok-karantina" data-k="karantina"><div class="kartu" style="gap: 8px; padding: 12px 14px;">
      <div class="label">Karantina · barang kembali yang menunggu keputusan</div>
      ${q.antre.length ? h`<div class="pita-info awas">${q.antre.length} barang · ${DESIMAL(q.totalKg)} kg menunggu satu keputusan: ternyata layak jual / rework / balik ke pemasok / buang. Ketuk barangnya.</div>
        ${q.antre.map((x) => h`<div class="jawab ${x.id === s.qBuka ? 'dipilih' : ''}" data-k="q-${x.id}" data-aksi="qBuka" data-id="${x.id}"><span class="kiri"><span class="nm">${x.nama}</span><span class="w">kembali ${tanggalPendek(x.tanggal)}${x.catatan ? ' · ' + x.catatan : ''}${x.returUtuh ? ' · returnya sudah dikoreksi layak jual' : ''}</span></span>
          <span class="kanan"><span class="n">${DESIMAL(x.kg)} kg</span><span class="w">${x.satuan === 'unit' ? x.jumlah + ' unit' : 'karung terbuka'}</span></span></div>`)}`
        : h`<div class="menolak">Karantina kosong — tidak ada barang kembali yang menunggu diputuskan.</div>`}
    </div>
    ${buka ? h`<div class="kartu rincian-wadah" data-k="q-panel-${buka.id}" style="gap: 8px;"><div class="label">${buka.nama} · ${DESIMAL(buka.kg)} kg · kembali ${tanggalPendek(buka.tanggal)}</div>
      ${buka.opnameSesudah.length ? h`<div class="ket awas-teks">Sesudah retur ini ada cocokkan ${buka.nama} (${buka.opnameSesudah.join(', ')}) — kalau barang ini ikut ditimbang waktu itu, stoknya sudah naik lewat cocokkan.</div>` : ''}
      <input class="ketik-nama" id="qAlasan" type="text" placeholder="alasan / catatan keputusan (wajib untuk layak jual)" value="${s.qAlasan}" data-ketik="qAlasan">
      ${buka.pilihan.map((p) => h`<div data-k="qp-${p.tindakan}" style="display: flex; flex-direction: column; gap: 3px;"><div class="kaca-btn ${!p.bisa ? 'mati' : s.qYakin === p.tindakan ? 'awas' : p.tindakan === 'layak_jual' ? 'aktif emas' : p.tindakan === 'dirework' ? 'aktif' : p.tindakan === 'dibuang' ? 'putus' : ''}" data-aksi="qPutus" data-id="${buka.id}" data-tindakan="${p.tindakan}">${s.qYakin === p.tindakan ? 'YAKIN — ' + p.label : p.label}</div>
        <div class="ket ${p.bisa ? '' : 'awas-teks'}">${p.bisa ? p.akibat : p.sebab}</div></div>`)}
    </div>` : ''}
    ${q.riwayat.length ? h`<div class="kartu" data-k="q-riwayat" style="gap: 4px;"><div class="label">Keputusan sebelumnya</div>${q.riwayat.map((r) => h`<div class="ket" data-k="qr-${r.id}">${tanggalPendek(r.tanggalKeputusan)} · ${r.nama} ${DESIMAL(r.kg)} kg → ${r.label}${r.catatan ? ' — ' + r.catatan : ''}</div>`)}</div>` : ''}
    </section>`;
  }

  K.dengar(gambar);
  dengarkan(() => nanti(gambar));
  // dipanggil layar Menu: buka lembar (masuk | cocok | adukan) atau tab (gudang | wadah | kapur | karantina) — lewat penangan yang sama dengan ketukan
  const buka = (lembar, tab, isi) => { set({ lembar: null }); if (lembar === 'masuk') { AKSI.bukaMasuk({}); if (isi && isi.koreksi) AKSI.mKoreksi({ id: String(isi.koreksi) }); if (isi && isi.merk) { ubahMasuk((d) => { const i = d.baris.findIndex((b) => !String(b.merk || '').trim()); if (i >= 0) d.baris[i].merk = isi.merk; else d.baris.push(Object.assign(C.barisMasukKosong(), { merk: isi.merk })); }); set({ kabar: 'Barang masuk untuk ' + isi.merk + ' — isi jumlah karung & harga per kg', kabarAwas: false }); } } else if (lembar === 'cocok') AKSI.bukaCocok({}); else if (lembar === 'adukan') AKSI.bukaAdukan({}); else if (lembar === 'kantong') AKSI.bukaKantong({}); else if (lembar === 'tempat') AKSI.bukaTempat({}); else if (lembar === 'hpp') AKSI.bukaHpp({}); else if (lembar === 'stokMin') AKSI.smBuka({}); else if (tab) AKSI.tab({ t: tab }); };
  return { keadaan: K, belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan, gambar, buka, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil && (_kotor || !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar); } };
}
