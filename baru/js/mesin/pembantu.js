// SUMBER KEBENARAN MESIN UANG BEKU sejak 3 Okt 2026 (dulu disalin byte demi byte dari index.html oleh pindah_mesin.py, kini pensiun) — JANGAN DISUNTING tanpa izin owner.
// Gerbang: `python3 alat-uji/beku2.py --sidik` (sidik tiap fungsi di alat-uji/beku.sha256 & pembantu.sha256); membuka mesin = izin owner → `beku2.py --catat`.
// Pembantu: konstanta & fungsi yang dipanggil mesin beku (bukan mesin, tapi ikut verbatim).
import { ambilAmplopLaba, ambilBahanKemasan, ambilBahanLiteran, ambilBiayaBulanan, ambilHargaKarung, ambilHargaKemasan, ambilHargaLiteran, ambilKarantina, ambilKasbonMutasi, ambilModalOwner, ambilPelangganCatatan, ambilPengeluaranHarian, ambilPenjualan, ambilPenjualanSemua, ambilPenyesuaianKemasan, ambilPenyesuaianStok, ambilPesanan, ambilPetaJenisBeras, ambilPiutangMutasi, ambilProduksi, ambilProduksiBerlaku, ambilRetur, ambilSemuaBatch, ambilSetoranKas, ambilTembusanStok, ambilTitikKas, ambilTutupHari, ambilUtangOwnerMutasi, ambilUtangPemasokMutasi, wzDiKeranjangAktif, wzDiKeranjangParkir } from '../data/toko.js';
import { bayaranBiayaBulanan, hitungPiutang, hitungStokBahanLiteran, hitungStokKarungPerMerk, hitungStokKemasan, hitungUtangPemasok } from './beku.js';

  const AMBANG_HARI_KRITIS = 4;
  const HARGA_AWAL_BAHAN_LITERAN = { 'paperbag5l': 305, 'paperbag10l': 395, 'karungbekas': 1500 };
  const JENDELA_LAJU_HARI = 14;
  const JENIS_BAHAN_KEMASAN = ['5kg_kembang', '5kg_bmw', '5kg_putriagri', '10kg_kembang', '10kg_bmw', '10kg_putriagri', '10kg_lele', '20kg_kembang', '20kg_bmw', '20kg_putriagri', '20kg_lele', '20kg_persik', '25kg_kembang'];
  const JENIS_LITERAN_KHUSUS = ['Ketan Putih','Ketan Putih Paris','Ketan Hitam PK','Ketan Hitam Sosoh','Beras Merah'];
  const KAPASITAS_KARUNG_BEKAS_LITER = 65;
  const KOLEKSI_AMPLOP = 'amplopLaba';
  const KOLEKSI_BAHAN_KEMASAN = 'stokBahanKemasan';
  const KOLEKSI_BAHAN_LITERAN = 'stokBahanLiteran';
  const KOLEKSI_BATCH = 'batchMasuk';
  const KOLEKSI_BULANAN = 'biayaBulanan';
  const KOLEKSI_HARIAN = 'pengeluaranHarian';
  const KOLEKSI_KARANTINA = 'karantina';
  const KOLEKSI_KASBON = 'kasbonMutasi';
  const KOLEKSI_MODAL = 'modalOwner';
  const KOLEKSI_PENJUALAN = 'penjualan';
  const KOLEKSI_PENYESUAIAN = 'penyesuaianStok';
  const KOLEKSI_PENY_KEMASAN = 'penyesuaianKemasan';
  const KOLEKSI_PESANAN = 'pesanan';
  const KOLEKSI_PIUTANG = 'piutangMutasi';
  const KOLEKSI_PRODUKSI = 'produksiKemasan';
  const KOLEKSI_RETUR = 'retur';
  const KOLEKSI_SETORAN = 'setoranKas';
  const KOLEKSI_TEMBUSAN = 'tembusanStok';
  const KOLEKSI_TUTUP = 'tutupHari';
  const KOLEKSI_UTANG_OWNER = 'utangOwnerMutasi';
  const KOLEKSI_UTANG_PEMASOK = 'utangPemasokMutasi';
  const LABEL_BAHAN_KEMASAN = {
    '5kg_kembang': '5 kg — Kembang', '5kg_bmw': '5 kg — BMW', '5kg_putriagri': '5 kg — Putri Agri',
    '10kg_kembang': '10 kg — Kembang', '10kg_bmw': '10 kg — BMW', '10kg_putriagri': '10 kg — Putri Agri', '10kg_lele': '10 kg — Lele',
    '20kg_kembang': '20 kg — Kembang', '20kg_bmw': '20 kg — BMW', '20kg_putriagri': '20 kg — Putri Agri', '20kg_lele': '20 kg — Lele', '20kg_persik': '20 kg — Persik',
    '25kg_kembang': '25 kg — Kembang',
    '5kg_kembangbmw': '5 kg — Kembang/BMW (gabungan lama)', '10kg_kembangbmw': '10 kg — Kembang/BMW (gabungan lama)', '10kg_putriagri_lele': '10 kg — Putri Agri/Lele (gabungan lama)',
    '20kg_kembangbmw': '20 kg — Kembang/BMW (gabungan lama)', '20kg_putriagri_lele_persik': '20 kg — Putri Agri/Lele/Persik (gabungan lama)'
  };
  const LABEL_BAHAN_LITERAN = { 'paperbag5l': 'Paper bag 5 liter', 'paperbag10l': 'Paper bag 10 liter', 'karungbekas': 'Karung bekas' };
  const MULAI_SUSUT_LABA = '2026-09-01';
  const NEGO_LANTAI = 500;
  const PILIHAN_JENIS_BERAS = ['IR64', 'Pandan Wangi', 'IR42', 'Rojolele', 'Ketan Putih', 'Ketan Hitam', 'Beras Merah'];
  const POS_BIAYA_BULANAN = [
    { kunci: 'listrik', label: 'Listrik', idTgl: 'tglBiayaListrik' },
    { kunci: 'akses', label: 'Akses / gapura', idTgl: 'tglBiayaAkses' },
    { kunci: 'keamanan', label: 'Keamanan lingkungan', idTgl: 'tglBiayaKeamanan' },
    { kunci: 'internet', label: 'Internet / Wifi', idTgl: 'tglBiayaInternet' }
    // 'bensin' & 'benang' dikeluarkan 21 Agu 2026 — pindah ke Pengeluaran Harian karena
    // belinya tidak rutin. Dokumen bulan lama masih memuat angkanya, tapi karena daftar
    // ini yang menentukan apa yang dibaca, angka itu berhenti ikut arus kas & laporan.
  ];
  const RASIO_DEFAULT = 0.82;
  const RASIO_KONVERSI = {
    'Ketan Putih': 0.815, 'Ketan Hitam PK': 0.810,
    'Ketan Hitam Sosoh': 0.800, 'Ketan Putih Paris': 0.800, 'Beras Merah': 0.800
  };
  const TANGGAL_STOK_AWAL = '2026-08-08';
// ---- fungsi pembantu (verbatim) ----
  function batchDiutang(k) { return k.caraBayar === 'utang'; }
  function caraBayarKunci(p) { return String((p && p.caraBayar) || '').trim().toLowerCase(); }
  function cocok(teks, kata) {
    return (teks || '').toString().toLowerCase().includes(kata);
  }
  function daftarModalOwner() {
    const modal = ambilModalOwner();
    const sudahDipetakan = {};
    modal.forEach(m => { if (m.dariSetoran) sudahDipetakan[m.dariSetoran] = true; });
    const lama = ambilSetoranKas().filter(x => !sudahDipetakan[x.id]).map(x => ({
      id: x.id, tanggal: x.tanggal, jam: x.jam || '', tipe: 'tarik', nominal: x.nominal || 0,
      catatan: x.catatan || 'Setoran ke owner', dariSetoranLama: true
    }));
    return modal.concat(lama);
  }
  function kasbonPotongGaji(m) {
    return String((m && m.caraBayar) || '').trim().toLowerCase() === 'potong gaji';
  }
  function kunciKemasan(nama, ukuran) {
    const u = Number(ukuran);
    return String(nama || '') + '|' + (isFinite(u) ? u : String(ukuran || ''));
  }
  function hppTaksiranRetur(r, stokKrg, stokKem) {
    if (r.jenisAsal === 'karung') {
      // Modal FIFO (owner 9 Okt 2026, tinjauan): retur yang dicatat saat merek FIFO menyimpan modal kembalinya sendiri (hppKembali = irisan depan
      // antrean saat retur) — laba bulan retur tidak bergeser oleh penjualan sesudahnya. Tanpa kolom itu: modal rata-rata (hppRataPerKg bila buku
      // sedang FIFO, karena hppTerakhirPerKg di sana = nilai sisa per kg). Saklar mati = rumus lama persis.
      if (typeof r.hppKembali === 'number' && isFinite(r.hppKembali)) return Math.round(r.hppKembali);
      const st = stokKrg[r.merkSumber];
      return Math.round((r.totalKg || 0) * ((st && (st.hppRataPerKg !== undefined ? st.hppRataPerKg : st.hppTerakhirPerKg)) || 0));
    }
    const st = stokKem[kunciKemasan(r.namaProduk, r.ukuranKemasan)];
    return Math.round((r.jumlahUnit || 0) * ((st && st.hppRataRataPerUnit) || 0));
  }
  function hppTercatat(p) {
    if (p.hppTotalSaatJual === undefined || p.hppTotalSaatJual === null) return false;
    return p.hppTotalSaatJual > 0 || (p.hargaTotal || 0) === 0;
  }
  function jumlahTrx(p) {
    if (p.jenis === 'kemasan') return { nilai: p.jumlahUnit || 0, satuan: 'unit', field: 'jumlahUnit' };
    if (p.jenis === 'karung') return { nilai: p.jumlahKarung || 0, satuan: 'karung', field: 'jumlahKarung' };
    if (p.jenis === 'literan') return { nilai: p.jumlahLiter || 0, satuan: 'liter', field: 'jumlahLiter' };
    if (p.jenis === 'repacking') return { nilai: p.totalKg || 0, satuan: 'kg', field: 'totalKg' };
    return null;
  }
  function uangKembaliRetur(r) {
    // Retur nota BON (audit 39b no. 37, keputusan owner 2 Okt 2026): nilai barang yang kembali
    // memotong bon (kolom potongBon + mutasi piutang tipe 'retur'), bukan uang laci. Laba & omzet
    // membacanya di sini sebagai pengurang penjualan; jalur kas (hitungArusKasInti,
    // daftarGerakanKas) membaca nominalRefund langsung, jadi kas tidak bergerak.
    return (r.nominalRefund || 0) + Math.max(0, r.selisihHargaTukar || 0) + (r.potongBon || 0);
  }
  function labelBahan(jenis) { return LABEL_BAHAN_KEMASAN[jenis] || LABEL_BAHAN_LITERAN[jenis] || jenis; }

  function formatRupiah(angka) { return 'Rp' + Math.round(angka).toLocaleString('id-ID'); }
  function potonganGajiPerPegawai() {
    const sisa = {};
    ambilKasbonMutasi().forEach(m => {
      if (m.tipe !== 'bayar' || !kasbonPotongGaji(m)) return;
      const n = String(m.namaPegawai || '').trim();
      if (!n) return;
      sisa[n] = (sisa[n] || 0) + (m.nominal || 0);
    });
    return sisa;
  }
  function tanggalLokalIso(d) {
    d = d || new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function geserHari(iso, n) { const d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return tanggalLokalIso(d); }
  function akhirBulanIso(bl) {
    const y = parseInt(bl.slice(0, 4), 10), m = parseInt(bl.slice(5, 7), 10);
    return bl + '-' + String(new Date(y, m, 0).getDate()).padStart(2, '0');
  }
  function bulanDari(iso) { return String(iso || '').slice(0, 7); }
  function isoKeTanggal(iso) { return new Date(iso + 'T00:00:00'); }
  function kunciPelanggan(nama) {
    return String(nama || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function namaSingkatTrx(p) {
    const nama = p.namaProduk || p.merkSumber || 'Penjualan';
    // Tiga cabang di bawah punya jaring pengaman, cabang ini dulu tidak — catatan
    // yang kehilangan ukuran/jumlah menulis "undefined kg × undefined" di Buku Kas.
    // Kalau datanya tidak ada, sebut namanya saja; jangan mengarang angka.
    if (p.jenis === 'kemasan') return (p.ukuranKemasan && p.jumlahUnit)
      ? `${nama} ${p.ukuranKemasan} kg × ${p.jumlahUnit}` : nama;
    if (p.jenis === 'karung') return `Sack ${p.beratKarungAcuan || 50} ${nama} × ${p.jumlahKarung || ''}`.trim();
    if (p.jenis === 'literan') return `Literan ${nama} · ${p.jumlahLiter || 0} L`;
    if (p.jenis === 'repacking') return `Repacking ${nama} · ${p.totalKg || 0} kg`;
    return nama;
  }

  function formatTanggal(iso) {
    if (!iso) return '-';
    const d = new Date(iso + 'T00:00:00');
    return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function namaBulanPanjang(iso) {
    if (!iso) return '';
    const BULAN = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
    const [th, bl] = iso.split('-');
    return BULAN[parseInt(bl, 10) - 1] + ' ' + th;
  }
  function penjualanMasihBerlaku(p) {
    return !p.dibatalkan && !p.dikoreksiOleh;
  }
  function tkPenjualanHidup(id) {
    const semua = ambilPenjualanSemua();
    let p = semua.find(x => String(x.id) === String(id));
    for (let i = 0; p && p.dikoreksiOleh && i < 20; i++) { const nx = String(p.dikoreksiOleh); p = semua.find(x => String(x.id) === nx); }
    return p && penjualanMasihBerlaku(p) ? p : null;
  }
  function tkTargetPengganti(r) {
    const h = r.hitunganTukarSistem || {};
    return r.tukarModel === 'kreditBarangGabung' && h.pengganti > 0 ? h.pengganti + (h.pembulatan || 0) : null;
  }
  function tkApakahYatim(r, tertaut) {
    if (!(r.tukarModel === 'kreditBarang' || r.tukarModel === 'kreditBarangGabung')) return false;
    if (r.penggantiDikonfirmasi && tkPenjualanHidup(r.penggantiDikonfirmasi.penjualanId)) return false;
    const a = tertaut.get(String(r.id));
    const target = tkTargetPengganti(r);
    if (target === null) return !(a && a.n > 0);
    return !(a && a.rp >= target - 1);
  }
  function tkSetTertaut() {
    const m = new Map();
    ambilPenjualan().forEach(pj => {
      if (!pj.tukarReturId) return;
      const k = String(pj.tukarReturId);
      const a = m.get(k) || { n: 0, rp: 0, bulat: 0 };
      a.n++; a.rp += pj.hargaTotal || 0; a.bulat += pj.pembulatan || 0;
      m.set(k, a);
    });
    return m;
  }
  function daftarGerakanKas() {
    const rows = [];
    // kantong: ke mana / dari mana uangnya. Default 'laci' — itu memang kebenaran
    // lapangan toko ini: yang tidak lewat rekening berpindah tangan di laci. Uang
    // KELUAR selalu dianggap dari laci; tidak ada catatan yang membedakannya, dan
    // menebak lebih jauh cuma memindahkan kesalahan ke tempat yang lebih sulit dilihat.
    const dorong = (t, jam, id, label, masuk, keluar, kantong) => {
      if (!(masuk > 0) && !(keluar > 0)) return;   // baris Rp0 (mis. pengganti retur) tidak berarti di buku kas
      rows.push({ t: t || '', jam: jam || '', id: id || 0, label, masuk: masuk || 0, keluar: keluar || 0,
        kantong: keluar > 0 ? 'laci' : (kantong || 'laci') });
    };
    const kantongBayar = x => caraBayarKunci(x) === 'qris' ? 'rekening' : 'laci';
    ambilPenjualan().forEach(p => {
      if (caraBayarKunci(p) === 'kredit') return;  // belum jadi uang — masuk lewat pelunasan piutang
      dorong(p.tanggal, p.jam, p.id, namaSingkatTrx(p) + (caraBayarKunci(p) === 'qris' ? ' · QRIS' : ''), p.hargaTotal, 0, kantongBayar(p));
    });
    ambilPiutangMutasi().forEach(m => {
      if (m.tipe !== 'bayar') return;
      dorong(m.tanggal, m.jam, m.id, 'Pelunasan piutang — ' + (m.namaPelanggan || ''), m.nominal, 0, kantongBayar(m));
    });
    ambilKasbonMutasi().forEach(m => {
      // HANYA ambil/bayar. Cabang else yang lama ikut menangkap tipe saldoAwal
      // (tutup buku) sebagai uang keluar — dan hero "Uang Kas Sekarang" dihitung
      // dari daftar ini, jadi kasbon terbawa akan menggerus kas sekarang secara
      // diam-diam. Tertangkap audit 14 Agu 2026, SEBELUM tutup buku pertama.
      // Potong gaji tidak memindahkan uang: jangan pernah muncul sebagai kas masuk di
      // Buku Kas. Jejaknya tetap hidup di riwayat kasbon pegawainya sendiri.
      if (m.tipe === 'bayar' && kasbonPotongGaji(m)) return;
      if (m.tipe === 'bayar') dorong(m.tanggal, m.jam, m.id, 'Kasbon kembali — ' + (m.namaPegawai || ''), m.nominal, 0, kantongBayar(m));
      else if (m.tipe === 'ambil') dorong(m.tanggal, m.jam, m.id, 'Kasbon — ' + (m.namaPegawai || ''), 0, m.nominal);
    });
    daftarModalOwner().forEach(x => x.tipe === 'setor'
      ? dorong(x.tanggal, x.jam, x.id, 'Modal owner disetor' + (x.catatan ? ' — ' + x.catatan : ''), x.nominal, 0)
      : dorong(x.tanggal, x.jam, x.id, x.dariSetoranLama || x.dariSetoran ? 'Setoran ke owner' : 'Modal owner ditarik' + (x.catatan ? ' — ' + x.catatan : ''), 0, x.nominal));
    ambilSemuaBatch().forEach(k => {
      if (k.stokAwal) return;
      const nilaiBeras = (k.merkList || []).reduce((x, m) => x + (m.subtotalHarga || 0), 0);
      if (batchDiutang(k)) {
        // Bon: uang beras TIDAK bergerak hari itu — cuma bongkarnya. Nilai bonnya
        // ditulis di keterangan supaya jejaknya tetap terbaca di Buku Kas.
        dorong(k.tanggal, '', k.id, 'Bongkar — ' + (k.pemasok || '') + ' (bon ' + formatRupiah(nilaiBeras) + ' — utang)', 0, k.biayaBongkar || 0);
      } else {
        dorong(k.tanggal, '', k.id, 'Belanja beras — ' + (k.pemasok || '') + ' (' + (k.merkList || []).length + ' merk)', 0, nilaiBeras + (k.biayaBongkar || 0));
      }
    });
    ambilUtangPemasokMutasi().forEach(m => {
      if (m.tipe !== 'bayar') return;
      dorong(m.tanggal, m.jam || '', m.id, 'Bayar bon ' + (m.pemasok || '') + (m.bonTanggal ? ' — bon ' + formatTanggal(m.bonTanggal) : ''), 0, m.nominal || 0);
    });
    bayaranBiayaBulanan().forEach(x => {
      if (!x.tanggal) return;                      // belum dibayar = belum bergerak
      if (!(x.nominal > 0)) return;                // habis dipotong kasbon = tidak ada uang bergerak
      dorong(x.tanggal, '', 0, x.label + ' — biaya ' + namaBulanPanjang(x.bulan + '-01'), 0, x.nominal);
    });
    ambilPengeluaranHarian().forEach(h => {
      // Owner ikut Buku Kas sebagai prive (21 Agu 2026) — uangnya keluar dari laci
      // yang sama, jadi wajib kelihatan di buku; labelnya membedakan, bukan disembunyikan.
      if (h.kategori === 'owner') { dorong(h.tanggal, '', h.id, 'Prive owner — ' + (h.keterangan || ''), 0, h.nominal); return; }
      // 'tokoDompet' (belanja toko dibayar dompet pribadi) sengaja TIDAK didorong:
      // bebannya masuk laba, tapi tidak ada rupiah yang keluar dari laci toko.
      if (h.kategori !== 'toko') return;
      dorong(h.tanggal, '', h.id, 'Harian — ' + (h.keterangan || ''), 0, h.nominal);
    });
    ambilUtangOwnerMutasi().forEach(m => {
      if (m.tipe !== 'bayar' || !(m.nominal > 0)) return;
      dorong(m.tanggal, m.jam || '', m.id, 'Bayar utang ke owner' + (m.catatan ? ' — ' + m.catatan : ''), 0, m.nominal);
    });
    // A (11 Sep): kaki retur TUKAR bukan uang keluar dari laci — ia nilai barang yang kembali,
    // pasangan penjualan penggantinya. Labelnya jujur DUA arah: kalau penggantinya belum tercatat,
    // ia mengaku kas tercatat terpotong. HANYA teks: angka, tanggal, dan kantong tidak berubah
    // (kasPada cuma membaca t/masuk/keluar).
    const tukarTertaut = tkSetTertaut();
    ambilRetur().forEach(r => {
      const nama = r.merkSumber || r.namaProduk || '';
      const tukar = r.tukarModel === 'kreditBarang' || r.tukarModel === 'kreditBarangGabung';
      const labelRetur = !tukar ? 'Refund retur — ' + nama
        : (tkApakahYatim(r, tukarTertaut) ? 'Tukar — ' + nama + ' kembali · PENGGANTI BELUM TERCATAT'
          : 'Tukar — ' + nama + ' kembali (dipotong dari penjualan pengganti)');
      if (r.nominalRefund > 0) dorong(r.tanggal, r.jam, r.id, labelRetur, 0, r.nominalRefund);
      const sel = r.selisihHargaTukar || 0;
      if (sel > 0) dorong(r.tanggal, r.jam, r.id, 'Selisih tukar — ' + nama, 0, sel);
      else if (sel < 0) dorong(r.tanggal, r.jam, r.id, 'Selisih tukar (pelanggan nambah) — ' + nama, -sel, 0);
    });
    const bahan = b2 => b2.tipe === 'beli' && b2.tanggal !== TANGGAL_STOK_AWAL;
    ambilBahanKemasan().filter(bahan).forEach(b2 =>
      dorong(b2.tanggal, '', b2.id, 'Beli kantong kemasan — ' + (LABEL_BAHAN_KEMASAN[b2.jenis] || b2.jenis), 0, b2.hargaTotal));
    ambilBahanLiteran().filter(bahan).forEach(b2 =>
      dorong(b2.tanggal, '', b2.id, 'Beli bahan literan — ' + (LABEL_BAHAN_LITERAN[b2.jenis] || b2.jenis), 0, b2.hargaTotal));
    rows.sort((x, y) => x.t.localeCompare(y.t) || x.jam.localeCompare(y.jam) || (x.id - y.id));
    return rows;
  }
  function totalUtangPemasokSemua(sampaiIso) {
    return hitungUtangPemasok(sampaiIso).reduce((a, x) => ({ nominal: a.nominal + x.totalUtang, nBon: a.nBon + x.bon.length }), { nominal: 0, nBon: 0 });
  }
  function bakuCaraBayar(c) {
    const k = String(c || '').trim().toLowerCase();
    if (k === 'qris') return 'QRIS';
    if (k === 'kredit') return 'Kredit';
    if (k === 'tunai') return 'Tunai';
    return String(c || '').trim() || 'Tunai';
  }
  function bulatKeAtas500(n) { return Math.ceil(Math.round(n) / 500) * 500; }
  function pesananBelumTuntas(p) {
    const st = String(p.status || '');
    return st !== 'dibayar' && st !== 'batal';
  }

  function tbCutoff(tahun) { return tahun + '-12-31'; }

  function tbPunyaBerat(merk, berat, cutoff) {
    return ambilSemuaBatch().some(k => (k.tanggal || '') <= cutoff &&
      (k.merkList || []).some(m => m.merk === merk && m.satuan === 'karung' && m.beratKarung === berat));
  }
  function produksiMasihBerlaku(pr) { return !pr.dikoreksiOleh; }
  function wzJumlahDiDaftar(daftar, jalur, kunci) {
    let n = 0;
    (daftar || []).forEach(function (it) {
      const t = (it && it.trx) || {};
      if (jalur === 'kemasan') {
        // Kunci dibangun oleh kunciKemasan, sama dengan yang dipakai mesinnya — bukan
        // dirakit ulang di sini, supaya tidak bisa berselisih diam-diam.
        if (t.jenis === 'kemasan' && kunciKemasan(t.namaProduk, t.ukuranKemasan) === kunci) n += (t.jumlahUnit || 0);
        return;
      }
      // Karung, literan, dan repacking menimba kolam KG YANG SAMA (hitungStokKarungPerMerk),
      // jadi dikurangi dalam KG lalu dikonversi SEKALI di ujung — bukan dijumlahkan silang.
      //
      // JENISNYA DISEBUT, tidak disiratkan. Mesin menyatakan aturan ini lantang di LIMA
      // tempat (12806, 17353, 18064, 20449, 20509), kata demi kata: kolam kg cuma dikurangi
      // oleh karung, repacking, dan literan. Penjaga ini tempat KEENAM — dan tanpa klausa
      // di bawah ia satu-satunya yang menyatakannya lewat KELALAIAN.
      // Hari ini itu tidak tertangkap: baris jenis 'kemasan' (15504, dan 27148 di jalur
      // kasir) tidak menyetel merkSumber. Tapi baris itu MEMBAWA totalKg — ukuranKemasan ×
      // jumlahUnit — jadi field yang dijumlah sudah ada; yang belum ada cuma field yang
      // dicocokkan. Satu field jaraknya dari memotong dua kali: kg yang sudah meninggalkan
      // kolam karung saat produksi, dipotong lagi saat bag-nya dijual.
      // Dan merkSumber di seluruh berkas ini berarti ASAL-USUL. Suatu hari seseorang akan
      // menambahkannya ke baris kemasan karena itu memang artinya — lalu langit-langit
      // karung mengetat diam-diam dan mulai menolak penjualan yang SAH, di meja kasir.
      // Cocok dengan mesin karena MENYETUJUI, bukan karena diam.
      if ((t.jenis === 'karung' || t.jenis === 'repacking' || t.jenis === 'literan')
        && t.merkSumber === kunci) n += (t.totalKg || 0);
    });
    return n;
  }
  function merkPunyaKarungBerat(merk, berat) {
    const dariBeli = ambilSemuaBatch().some(k => (k.merkList || []).some(m => m.merk === merk && m.satuan === 'karung' && m.beratKarung === berat));
    if (dariBeli) return true;
    // Produksi 50 kg yang digabung balik ke karung utuh (bukan jadi kemasan sendiri —
    // keputusan My DeV 9 Agu 2026) juga membuat merk itu "punya karung 50 kg", walau
    // merk itu tidak pernah dibeli langsung dari pemasok. Cuma berlaku di 50 kg, karena
    // cuma di situ jadiKarungUtuh dipakai.
    if (berat !== 50) return false;
    return ambilProduksiBerlaku().some(pr => pr.jadiKarungUtuh && pr.merkTujuan === merk);
  }
  function cariHargaKarungPerKg(merk) {
    const cocok = ambilHargaKarung().find(h => h.merk === merk);
    return cocok ? cocok.hargaPerKg : null;
  }

  function hargaKarungUtuh(merk, beratKarung) {
    const hKemasan = ambilHargaKemasan().find(x => x.merk === merk && x.ukuran === beratKarung);
    if (hKemasan && hKemasan.hargaPerUnit > 0) {
      return { perUnit: hKemasan.hargaPerUnit, sumber: 'kemasan' };
    }
    const perKg = cariHargaKarungPerKg(merk);
    if (perKg === null || perKg <= 0) return null;
    return { perUnit: Math.round(perKg * beratKarung), perKg, sumber: 'karung' };
  }
  function tentukanKemasanLiteran(jumlahLiter) {
    if (jumlahLiter < 5) return null;
    if (jumlahLiter === 5) return 'paperbag5l';
    if (jumlahLiter < 13) return 'paperbag10l';
    return 'karungbekas';
  }
  function jumlahKemasanLiteran(jumlahLiter) {
    const jenis = tentukanKemasanLiteran(jumlahLiter);
    if (!jenis) return 0;
    // Paper bag selalu 1: 5 L pas satu kantong, 5-12 L pas satu kantong 10 L.
    if (jenis !== 'karungbekas') return 1;
    return Math.max(1, Math.ceil(jumlahLiter / KAPASITAS_KARUNG_BEKAS_LITER));
  }
  function hargaBahanLiteranEfektif(jenis, stokBahanLiteran) {
    return (stokBahanLiteran[jenis]?.hargaPerPcs || 0) || HARGA_AWAL_BAHAN_LITERAN[jenis] || 0;
  }
  function catatanPelangganBerisi(c) {
    return !!(c && (String(c.catatan || '').trim() || String(c.ciri || '').trim() || String(c.rute || '').trim()));
  }
  function infoKreditPelanggan(nama) {
    const k = kunciPelanggan(nama);
    if (!k) return { ada: false };
    const terdaftar = ambilPelangganCatatan().some(c => kunciPelanggan(c.nama || c.id) === k && catatanPelangganBerisi(c));
    const rekor = hitungPiutang().find(x => x.kunci === k);
    const sisa = rekor ? Math.max(0, rekor.sisa || 0) : 0;
    const batasIso = tanggalLokalIso(new Date(Date.now() - 89 * 86400000));
    let total90 = 0;
    ambilPenjualan().forEach(t => {
      if ((t.tanggal || '') >= batasIso && kunciPelanggan(t.namaPelanggan) === k) total90 += t.hargaTotal || 0;
    });
    const rataBulanan = Math.round(total90 / 3);
    return { ada: true, terdaftar, sisa, rataBulanan, batas: rataBulanan * 2 };
  }
  function rtKunciNota(p) { return String(p.trxId || p.grupNota || p.id); }
  function rtRantaiNota(t) {
    const semua = ambilPenjualanSemua();
    const ids = [String(t.id)];
    let kini = t, jaga = 0;
    while (kini && kini.koreksiDari != null && jaga++ < 50) {
      const idLama = String(kini.koreksiDari);
      if (ids.indexOf(idLama) >= 0) break;
      ids.push(idLama);
      kini = semua.find(x => String(x.id) === idLama);
    }
    return ids;
  }
  function twBanyak(p) {
    if (p.jenis === 'literan') return p.jumlahLiter || 0;      // lawan hargaPerLiter
    if (p.jenis === 'kemasan') return p.jumlahUnit || 0;       // lawan hargaPerUnit
    return p.totalKg || 0;                                     // karung & repacking, lawan hargaPerKg
  }
  function twSatuanDibayar(p, potNota, subNota) {
    const t = { nilai: twBanyak(p) };
    if (!(t.nilai > 0)) return null;
    const bersih = (p.hargaTotal || 0) - (p.pembulatan || 0);
    if (!(bersih > 0)) return null;
    const pas = (potNota > 0 && subNota > 0) ? bersih * (1 - potNota / subNota) : bersih;
    return pas / t.nilai;
  }
  function rtDasarNota(t) {
    if (t.jenis !== 'karung' && t.jenis !== 'kemasan') {
      return { ok: false, sebab: 'Jalur retur untuk literan / repacking belum ada — pakai koreksi transaksi di Riwayat.' };
    }
    // Penolakan di bawah ini BUKAN soal nota yang tidak ada: barangnya jelas, cuma nilainya
    // tidak boleh / tidak bisa dihitung sistem. Karena itu mereka membawa `cadangan` —
    // rtIsiDariTrx tetap mengisi barang & jumlah seperti di main, tanpa menunjuk nota,
    // dan nominalnya diketik tangan. Tanpa cadangan, di HP (pemilih manual tersembunyi)
    // nota semacam ini jadi jalan buntu.
    if (caraBayarKunci(t) === 'kredit') {
      return { ok: false, cadangan: true, sebab: 'Nota ini KREDIT — pembeli belum membayarnya. Sistem tidak menghitung nilainya: '
        + 'kalau refund, uangnya JANGAN keluar dari laci (retur yang mengurangi piutang belum ada di sistem).' };
    }
    if (t.perluKoreksi) {
      return { ok: false, cadangan: true, sebab: 'Nota ini masih bertanda perlu dikoreksi (jumlahnya hasil hitung balik dari harga), jadi harga per satuannya tidak dipercaya.' };
    }
    if (t.jenis === 'kemasan' && (t.bonusUnit || 0) > 0) {
      return { ok: false, cadangan: true, sebab: 'Nota ini memuat unit BONUS (gratis), jadi harga per unit tidak bisa diturunkan tanpa tahu unit mana yang kembali.' };
    }
    const kunci = rtKunciNota(t);
    const senota = ambilPenjualan().filter(x => rtKunciNota(x) === kunci);
    const potNota = senota.filter(x => x.jenis === 'potongan').reduce((a, x) => a + Math.max(0, -(x.hargaTotal || 0)), 0);
    const subNota = senota.filter(x => (x.hargaTotal || 0) > 0).reduce((a, x) => a + (x.hargaTotal || 0) - (x.pembulatan || 0), 0);
    const perSatuan = twSatuanDibayar(t, potNota, subNota);
    if (!(perSatuan > 0)) return { ok: false, cadangan: true, sebab: 'Harga per satuan nota ini tidak bisa diturunkan (total atau jumlahnya nol).' };
    const satuan = t.jenis === 'kemasan' ? 'unit' : 'kg';
    const banyakNota = t.jenis === 'kemasan' ? (t.jumlahUnit || 0) : (t.totalKg || 0);
    const rantai = rtRantaiNota(t);
    const sudahDiretur = ambilRetur().filter(r => r.notaAsalId != null && rantai.indexOf(String(r.notaAsalId)) >= 0)
      .reduce((a, r) => a + (r.jumlahDikembalikan || 0), 0);
    const sisa = Math.round((banyakNota - sudahDiretur) * 1000) / 1000;
    if (!(sisa > 0)) return { ok: false, sebab: 'Nota ini sudah diretur seluruhnya: ' + sudahDiretur.toLocaleString('id-ID') + ' dari ' + banyakNota.toLocaleString('id-ID') + ' ' + satuan + '.' };
    const dasar = 'hargaTotal ' + formatRupiah(t.hargaTotal || 0)
      + ((t.pembulatan || 0) > 0 ? ' − pembulatan tunai ' + formatRupiah(t.pembulatan) : '')
      + (potNota > 0 ? ' − potongan nota diprorata' : '')
      + ' ÷ ' + banyakNota.toLocaleString('id-ID') + ' ' + satuan;
    return { ok: true, perSatuan, satuan, banyakNota, sudahDiretur, sisa, potNota, dasar };
  }
  function rtKalimatLebih(d, jml) {
    return 'Yang dikembalikan ' + jml.toLocaleString('id-ID') + ' ' + d.satuan + ' melebihi sisa nota: '
      + d.banyakNota.toLocaleString('id-ID') + ' ' + d.satuan + ' di nota'
      + (d.sudahDiretur > 0 ? ', ' + d.sudahDiretur.toLocaleString('id-ID') + ' sudah diretur sebelumnya' : '')
      + ' — sisa ' + d.sisa.toLocaleString('id-ID') + ' ' + d.satuan + '. Retur tidak disimpan.';
  }
  function susunIsiKatalogKasir() {
    try {
      const stokKemasan = hitungStokKemasan();
      const stokKarung = hitungStokKarungPerMerk();
      const stokBahanLiteran = hitungStokBahanLiteran();
      const hargaKemasan = ambilHargaKemasan();
      const hargaLiteran = ambilHargaLiteran();
      const batch = ambilSemuaBatch();

      const kemasan = Object.keys(stokKemasan).map(kunci => {
        const s = stokKemasan[kunci];
        const [namaProduk, ukuranStr] = kunci.split('|');
        const ukuran = parseFloat(ukuranStr);
        const h = hargaKemasan.find(x => x.merk === namaProduk && x.ukuran === ukuran);
        return { kunci, namaProduk, ukuran, sisaUnit: s.sisaUnit || 0,
          hppPerUnit: s.hppRataRataPerUnit || 0, hargaPerUnit: h ? h.hargaPerUnit : 0 };
      });

      const merkKarung = Object.keys(stokKarung).map(merk => {
        const s = stokKarung[merk];
        const hL = hargaLiteran.find(x => x.merk === merk);
        return { merk, sisaKg: s.sisaKg || 0, hppPerKg: s.hppTerakhirPerKg || 0,
          beratKarung: 50, karung50: merkPunyaKarungBerat(merk, 50),
          // Sack 25 (13 Agu 2026) — kasir & darurat butuh tahu merk mana yang punya
          // sack 25 dan harganya, dengan aturan harga yang sama dengan 50.
          karung25: merkPunyaKarungBerat(merk, 25),
          hargaKarung25: (hargaKarungUtuh(merk, 25) || {}).perUnit || 0,
          // Harga siap pakai per karung 50kg — Katalog Kemasan menang atas harga/kg (aturan 4 Agu 2026).
          hargaKarung50: (hargaKarungUtuh(merk, 50) || {}).perUnit || 0,
          hargaPerKg: cariHargaKarungPerKg(merk) || 0,
          hargaPerLiter: hL ? hL.hargaPerLiter : 0,
          rasio: RASIO_KONVERSI[merk] || RASIO_DEFAULT };
      });

      const bahanLiteran = {};
      Object.keys(stokBahanLiteran).forEach(j => {
        bahanLiteran[j] = { sisaPcs: stokBahanLiteran[j].sisaPcs || 0, hargaPerPcs: stokBahanLiteran[j].hargaPerPcs || 0 };
      });

      // Piutang ikut diterbitkan supaya kasir bisa menampilkan daftar pelanggan berutang
      // dan menerima pembayaran tanpa perlu membaca seluruh riwayat penjualan (kasir
      // sengaja cuma membaca SATU dokumen ini). Yang lunas tidak dikirim — kasir hanya
      // perlu tahu siapa yang masih punya sisa.
      const piutang = hitungPiutang().filter(p => p.sisa > 0)
        .map(p => ({ nama: p.nama, sisa: p.sisa }));

      return { kemasan, merkKarung, bahanLiteran, piutang };
    } catch (e) { console.error('Gagal menyusun katalog kasir', e); return null; }
  }
  function tebakJenisBeras(merk) {
    const m = String(merk || '');
    if (/^IR64/i.test(m) || m === 'Angsa' || m === 'Perahu Layar') return 'IR64';
    if (/^IR42/i.test(m)) return 'IR42';
    if (/^Ketan Hitam/i.test(m)) return 'Ketan Hitam';
    if (/^Ketan/i.test(m)) return 'Ketan Putih';
    if (/Pandan Wangi/i.test(m)) return 'Pandan Wangi';
    if (/Beras Merah/i.test(m)) return 'Beras Merah';
    if (/Rojolele|Rojo Lele/i.test(m)) return 'Rojolele';
    return '';
  }
  function jenisUntukMerk(merk) {
    const peta = ambilPetaJenisBeras();
    return peta[merk] !== undefined ? peta[merk] : tebakJenisBeras(merk);
  }
  function semuaMerkDikenal() {
    const kumpul = {};
    Object.keys(hitungStokKarungPerMerk()).forEach(m => { kumpul[m] = true; });
    Object.keys(hitungStokKemasan()).forEach(k => { kumpul[k.split('|')[0]] = true; });
    ambilHargaKarung().forEach(h => { kumpul[h.merk] = true; });
    return Object.keys(kumpul).sort();
  }
  async function acakPin(pin, garam) {
    const data = new TextEncoder().encode(String(garam) + '|' + String(pin));
    const buf = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

export { AMBANG_HARI_KRITIS, HARGA_AWAL_BAHAN_LITERAN, JENDELA_LAJU_HARI, JENIS_BAHAN_KEMASAN, JENIS_LITERAN_KHUSUS, KAPASITAS_KARUNG_BEKAS_LITER, KOLEKSI_AMPLOP, KOLEKSI_BAHAN_KEMASAN, KOLEKSI_BAHAN_LITERAN, KOLEKSI_BATCH, KOLEKSI_BULANAN, KOLEKSI_HARIAN, KOLEKSI_KARANTINA, KOLEKSI_KASBON, KOLEKSI_MODAL, KOLEKSI_PENJUALAN, KOLEKSI_PENYESUAIAN, KOLEKSI_PENY_KEMASAN, KOLEKSI_PESANAN, KOLEKSI_PIUTANG, KOLEKSI_PRODUKSI, KOLEKSI_RETUR, KOLEKSI_SETORAN, KOLEKSI_TEMBUSAN, KOLEKSI_TUTUP, KOLEKSI_UTANG_OWNER, KOLEKSI_UTANG_PEMASOK, LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, NEGO_LANTAI, PILIHAN_JENIS_BERAS, POS_BIAYA_BULANAN, RASIO_DEFAULT, RASIO_KONVERSI, TANGGAL_STOK_AWAL, batchDiutang, caraBayarKunci, cocok, daftarModalOwner, kasbonPotongGaji, kunciKemasan, hppTaksiranRetur, hppTercatat, jumlahTrx, uangKembaliRetur, labelBahan, formatRupiah, potonganGajiPerPegawai, tanggalLokalIso, geserHari, akhirBulanIso, bulanDari, isoKeTanggal, kunciPelanggan, namaSingkatTrx, formatTanggal, namaBulanPanjang, penjualanMasihBerlaku, tkPenjualanHidup, tkTargetPengganti, tkApakahYatim, tkSetTertaut, daftarGerakanKas, totalUtangPemasokSemua, bakuCaraBayar, bulatKeAtas500, pesananBelumTuntas, tbCutoff, tbPunyaBerat, produksiMasihBerlaku, wzJumlahDiDaftar, merkPunyaKarungBerat, cariHargaKarungPerKg, hargaKarungUtuh, tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan, rtKunciNota, rtRantaiNota, twBanyak, twSatuanDibayar, rtDasarNota, rtKalimatLebih, susunIsiKatalogKasir, tebakJenisBeras, jenisUntukMerk, semuaMerkDikenal, acakPin };
