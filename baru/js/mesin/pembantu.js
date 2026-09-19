// DIBUAT OLEH alat-uji/pindah_mesin.py — JANGAN DISUNTING TANGAN.
// Tubuh tiap fungsi disalin byte demi byte dari index.html; gerbang: `python3 alat-uji/pindah_mesin.py --periksa`.
// Pembantu: konstanta & fungsi yang dipanggil mesin beku (bukan mesin, tapi ikut verbatim).
import { ambilAmplopLaba, ambilBahanKemasan, ambilBahanLiteran, ambilBiayaBulanan, ambilHargaKarung, ambilHargaKemasan, ambilKarantina, ambilKasbonMutasi, ambilModalOwner, ambilPelangganCatatan, ambilPengeluaranHarian, ambilPenjualan, ambilPenjualanSemua, ambilPenyesuaianKemasan, ambilPenyesuaianStok, ambilPesanan, ambilPiutangMutasi, ambilProduksi, ambilProduksiBerlaku, ambilRetur, ambilSemuaBatch, ambilSetoranKas, ambilTembusanStok, ambilTitikKas, ambilTutupHari, ambilUtangOwnerMutasi, ambilUtangPemasokMutasi, wzDiKeranjangAktif, wzDiKeranjangParkir } from '../data/toko.js';
import { bayaranBiayaBulanan, hitungPiutang, hitungUtangPemasok } from './beku.js';

  const AMBANG_HARI_KRITIS = 4;
  const HARGA_AWAL_BAHAN_LITERAN = { 'paperbag5l': 305, 'paperbag10l': 395, 'karungbekas': 1500 };
  const JENDELA_LAJU_HARI = 14;
  const JENIS_BAHAN_KEMASAN = ['5kg_kembangbmw', '5kg_putriagri', '10kg_kembangbmw', '10kg_putriagri_lele', '20kg_kembangbmw', '20kg_putriagri_lele_persik', '25kg_kembang'];
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
    '5kg_kembangbmw': '5 kg — Kembang/BMW', '5kg_putriagri': '5 kg — Putri Agri',
    '10kg_kembangbmw': '10 kg — Kembang/BMW', '10kg_putriagri_lele': '10 kg — Putri Agri/Lele',
    '20kg_kembangbmw': '20 kg — Kembang/BMW', '20kg_putriagri_lele_persik': '20 kg — Putri Agri/Lele/Persik',
    '25kg_kembang': '25 kg — Kembang'
  };
  const LABEL_BAHAN_LITERAN = { 'paperbag5l': 'Paper bag 5 liter', 'paperbag10l': 'Paper bag 10 liter', 'karungbekas': 'Karung bekas' };
  const MULAI_SUSUT_LABA = '2026-09-01';
  const NEGO_LANTAI = 500;
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
      const st = stokKrg[r.merkSumber];
      return Math.round((r.totalKg || 0) * ((st && st.hppTerakhirPerKg) || 0));
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
    return (r.nominalRefund || 0) + Math.max(0, r.selisihHargaTukar || 0);
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

export { AMBANG_HARI_KRITIS, HARGA_AWAL_BAHAN_LITERAN, JENDELA_LAJU_HARI, JENIS_BAHAN_KEMASAN, JENIS_LITERAN_KHUSUS, KAPASITAS_KARUNG_BEKAS_LITER, KOLEKSI_AMPLOP, KOLEKSI_BAHAN_KEMASAN, KOLEKSI_BAHAN_LITERAN, KOLEKSI_BATCH, KOLEKSI_BULANAN, KOLEKSI_HARIAN, KOLEKSI_KARANTINA, KOLEKSI_KASBON, KOLEKSI_MODAL, KOLEKSI_PENJUALAN, KOLEKSI_PENYESUAIAN, KOLEKSI_PENY_KEMASAN, KOLEKSI_PESANAN, KOLEKSI_PIUTANG, KOLEKSI_PRODUKSI, KOLEKSI_RETUR, KOLEKSI_SETORAN, KOLEKSI_TEMBUSAN, KOLEKSI_TUTUP, KOLEKSI_UTANG_OWNER, KOLEKSI_UTANG_PEMASOK, LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, NEGO_LANTAI, POS_BIAYA_BULANAN, RASIO_DEFAULT, RASIO_KONVERSI, TANGGAL_STOK_AWAL, batchDiutang, caraBayarKunci, cocok, daftarModalOwner, kasbonPotongGaji, kunciKemasan, hppTaksiranRetur, hppTercatat, jumlahTrx, uangKembaliRetur, labelBahan, formatRupiah, potonganGajiPerPegawai, tanggalLokalIso, geserHari, akhirBulanIso, bulanDari, isoKeTanggal, kunciPelanggan, namaSingkatTrx, formatTanggal, namaBulanPanjang, penjualanMasihBerlaku, tkPenjualanHidup, tkTargetPengganti, tkApakahYatim, tkSetTertaut, daftarGerakanKas, totalUtangPemasokSemua, bakuCaraBayar, bulatKeAtas500, pesananBelumTuntas, tbCutoff, tbPunyaBerat, produksiMasihBerlaku, wzJumlahDiDaftar, merkPunyaKarungBerat, cariHargaKarungPerKg, hargaKarungUtuh, tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan, rtKunciNota, rtRantaiNota, twBanyak, twSatuanDibayar, rtDasarNota, rtKalimatLebih };
