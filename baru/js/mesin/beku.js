// DIBUAT OLEH alat-uji/pindah_mesin.py — JANGAN DISUNTING TANGAN.
// Tubuh tiap fungsi disalin byte demi byte dari index.html; gerbang: `python3 alat-uji/pindah_mesin.py --periksa`.
// MESIN UANG BEKU (26 dari 28). Belum dipindah: tulisSaldoPembuka (ritual Tutup Buku, memakai alert/confirm dan 700+ fungsi layar); thPagar (pagar Tutup Hari, membaca document).
import { ambilAmplopLaba, ambilBahanKemasan, ambilBahanLiteran, ambilBiayaBulanan, ambilHargaKarung, ambilHargaKemasan, ambilKarantina, ambilKasbonMutasi, ambilModalOwner, ambilPelangganCatatan, ambilPengeluaranHarian, ambilPenjualan, ambilPenjualanSemua, ambilPenyesuaianKemasan, ambilPenyesuaianStok, ambilPesanan, ambilPiutangMutasi, ambilProduksi, ambilProduksiBerlaku, ambilRetur, ambilSemuaBatch, ambilSetoranKas, ambilTembusanStok, ambilTitikKas, ambilTutupHari, ambilUtangOwnerMutasi, ambilUtangPemasokMutasi, wzDiKeranjangAktif, wzDiKeranjangParkir } from '../data/toko.js';
import { HARGA_AWAL_BAHAN_LITERAN, JENDELA_LAJU_HARI, JENIS_BAHAN_KEMASAN, JENIS_LITERAN_KHUSUS, KAPASITAS_KARUNG_BEKAS_LITER, KOLEKSI_AMPLOP, KOLEKSI_BAHAN_KEMASAN, KOLEKSI_BAHAN_LITERAN, KOLEKSI_BATCH, KOLEKSI_BULANAN, KOLEKSI_HARIAN, KOLEKSI_KARANTINA, KOLEKSI_KASBON, KOLEKSI_MODAL, KOLEKSI_PENJUALAN, KOLEKSI_PENYESUAIAN, KOLEKSI_PENY_KEMASAN, KOLEKSI_PESANAN, KOLEKSI_PIUTANG, KOLEKSI_PRODUKSI, KOLEKSI_RETUR, KOLEKSI_SETORAN, KOLEKSI_TEMBUSAN, KOLEKSI_TUTUP, KOLEKSI_UTANG_OWNER, KOLEKSI_UTANG_PEMASOK, LABEL_BAHAN_KEMASAN, LABEL_BAHAN_LITERAN, MULAI_SUSUT_LABA, NEGO_LANTAI, POS_BIAYA_BULANAN, RASIO_DEFAULT, RASIO_KONVERSI, TANGGAL_STOK_AWAL, batchDiutang, caraBayarKunci, cocok, daftarModalOwner, kasbonPotongGaji, kunciKemasan, hppTaksiranRetur, hppTercatat, jumlahTrx, uangKembaliRetur, labelBahan, formatRupiah, potonganGajiPerPegawai, tanggalLokalIso, geserHari, akhirBulanIso, bulanDari, isoKeTanggal, kunciPelanggan, namaSingkatTrx, formatTanggal, namaBulanPanjang, penjualanMasihBerlaku, tkPenjualanHidup, tkTargetPengganti, tkApakahYatim, tkSetTertaut, daftarGerakanKas, totalUtangPemasokSemua, bakuCaraBayar, bulatKeAtas500, pesananBelumTuntas, tbCutoff, tbPunyaBerat, produksiMasihBerlaku, wzJumlahDiDaftar, merkPunyaKarungBerat, cariHargaKarungPerKg, hargaKarungUtuh, tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan, rtKunciNota, rtRantaiNota, twBanyak, twSatuanDibayar, rtDasarNota, rtKalimatLebih } from './pembantu.js';
// ---- mesin beku (verbatim; lihat catatan di pembantu.js soal baris kosong) ----
  function hitungArusKasInti(cocok, bayaranBln) {
    const jmlHarga = arr => arr.reduce((a, x) => a + (x.hargaTotal || 0), 0);
    const jmlNominal = arr => arr.reduce((a, x) => a + (x.nominal || 0), 0);

    // ambilPenjualan() sudah membuang yang dibatalkan/dikoreksi — transaksi batal
    // memang tidak pernah jadi uang.
    const jual = ambilPenjualan().filter(p => cocok(p.tanggal));
    const kredit = jual.filter(p => caraBayarKunci(p) === 'kredit');
    const qris = jual.filter(p => caraBayarKunci(p) === 'qris');
    const tunai = jual.filter(p => caraBayarKunci(p) !== 'kredit' && caraBayarKunci(p) !== 'qris');

    const piutangBayar = ambilPiutangMutasi().filter(m => m.tipe === 'bayar' && cocok(m.tanggal));
    // KASBON DILUNASI POTONG GAJI BUKAN UANG MASUK (21 Agu 2026). Dikonfirmasi My DeV:
    // di toko ini SEMUA kasbon dilunasi dengan memotong gaji — pegawai tidak pernah
    // menyerahkan uang tunai. Formulirnya memang sudah punya pilihan "Potong gaji",
    // tapi mesin kas dulu menghitung SEMUA pelunasan sebagai kas masuk. Akibatnya laci
    // seolah bertambah padahal tidak ada rupiah yang masuk — muncul sebagai "selisih
    // KURANG" saat Tutup Hari (kejadian nyata: Rp1.562.500 pada 21 Agu 2026).
    // Sisi gaji ditangani di bayaranBiayaBulanan(): gaji tunai keluar = gaji − potongan.
    const kasbonBayar = ambilKasbonMutasi().filter(m => m.tipe === 'bayar' && cocok(m.tanggal)
      && !kasbonPotongGaji(m));
    // MODAL OWNER — satu-satunya sumber (daftarModalOwner sudah menyatukan setoranKas
    // lama sebagai 'tarik' dan membuang kembarannya). Menyeberang batas pemilik, jadi
    // ikut bergerak di arus kas — beda dengan amplop & brankas yang cuma pindah tempat.
    const modalGerak = daftarModalOwner().filter(x => cocok(x.tanggal));
    const modalSetor = modalGerak.filter(x => x.tipe === 'setor');
    const setoran = modalGerak.filter(x => x.tipe !== 'setor');   // 'tarik' = setoran ke owner
    const kasbonAmbil = ambilKasbonMutasi().filter(m => m.tipe === 'ambil' && cocok(m.tanggal));

    // STOK AWAL BUKAN ARUS KAS (keputusan My DeV 12 Agustus 2026).
    // Barang yang sudah ada di gudang saat sistem mulai dipakai dicatat 8 Agustus 2026
    // sebagai foto keadaan awal — uangnya sudah keluar jauh sebelum itu, di luar sistem.
    // Penandanya lahir bersama formulir Stok Awal (formulirnya sendiri dicabut 13 Agu
    // 2026 sesudah pemindahan selesai; datanya tetap dan tetap dibaca di sini).
    const batch = ambilSemuaBatch().filter(k => cocok(k.tanggal) && !k.stokAwal);
    // BELANJA DIPECAH (25 Agu 2026): batch BON tidak mengeluarkan uang beras pada hari
    // kedatangan — hanya BONGKARNYA yang tunai (dibayar kuli & supir, tidak pernah
    // diutang). Nilai berasnya keluar nanti lewat "Bayar bon pemasok" pada TANGGAL
    // BAYARNYA. Dokumen lama tanpa caraBayar = tunai, angka historis tidak bergeser.
    const belanja = batch.reduce((a, k) =>
      a + (batchDiutang(k) ? 0 : (k.merkList || []).reduce((x, m) => x + (m.subtotalHarga || 0), 0)) + (k.biayaBongkar || 0), 0);
    const bayarBon = ambilUtangPemasokMutasi().filter(m => m.tipe === 'bayar' && cocok(m.tanggal));

    // Tiap pos biaya bulanan lewat predikat yang sama persis dengan penjualan, belanja,
    // dan lainnya — tidak ada lagi perlakuan khusus. Pos tanpa tanggal tidak akan pernah
    // cocok, jadi otomatis tidak terhitung sebagai uang keluar.
    // Baris bernominal nol (gaji yang habis dipotong kasbon) ada demi LABA, tapi di sisi
    // kas ia bukan pembayaran — tidak ada rupiah yang berpindah, jadi tidak ikut di sini.
    const bayarTerhitung = (bayaranBln || []).filter(x => x.tanggal && cocok(x.tanggal) && x.nominal > 0);
    const biayaBulanan = bayarTerhitung.reduce((a, x) => a + x.nominal, 0);

    const harianToko = ambilPengeluaranHarian().filter(h => h.kategori === 'toko' && cocok(h.tanggal));
    // PRIVE OWNER (21 Agu 2026, keputusan My DeV): biaya hidup pemilik untuk sementara
    // memang diambil dari laci toko — belum ada kas pribadi terpisah. Aturannya:
    // pengeluaran kategori Owner = uang KELUAR dari laci (supaya hitungan malam cocok),
    // tapi BUKAN biaya toko (tidak menyentuh laba). Bukunya yang memisahkan uang
    // pribadi dan uang toko, bukan lacinya.
    // Konsekuensi disiplin: entri Owner HANYA untuk uang yang benar-benar keluar dari
    // laci — belanja PRIBADI dari dompet sendiri tetap jangan dicatat sama sekali.
    // (6 Sep 2026) Yang berubah cuma sisi laba: sejak layar Belanja lahir, laba
    // membaca 'toko' DAN 'tokoDompet'. Sisi kas di sini TIDAK ikut berubah — kalau
    // 'tokoDompet' diberi baris keluar di sini, kas toko akan turun saat owner
    // membayar pakai uangnya sendiri, dan itu persis kekeliruan yang dilarang.
    const harianOwner = ambilPengeluaranHarian().filter(h => h.kategori === 'owner' && cocok(h.tanggal));
    // PELUNASAN UTANG KE OWNER: uang benar-benar keluar laci, tapi BUKAN biaya —
    // bebannya sudah diakui saat belanjanya dicatat. Pola yang sama dengan bayar bon
    // pemasok. Belanja 'tokoDompet' sendiri TIDAK punya baris di sini, dan justru
    // ketiadaannya yang membuat kas toko tidak bergerak saat utang itu lahir.
    const bayarUtangOwner = ambilUtangOwnerMutasi().filter(m => m.tipe === 'bayar' && cocok(m.tanggal));
    const returDipakai = ambilRetur().filter(r => cocok(r.tanggal));
    // BRUTO, bukan neto (12 Agu 2026): selisih tukar yang pelanggan TAMBAHKAN adalah
    // uang yang sungguh masuk laci — dulu dijaringkan diam-diam ke angka refund,
    // sehingga rincian kategori tidak pernah bisa dicocokkan dengan Buku Kas yang
    // mencatat kejadian per kejadian. Bersihnya sama persis; rinciannya kini jujur.
    const refund = returDipakai.reduce((a, r) => a + (r.nominalRefund || 0) + Math.max(0, r.selisihHargaTukar || 0), 0);
    const tukarMasuk = returDipakai.reduce((a, r) => a + Math.max(0, -(r.selisihHargaTukar || 0)), 0);
    // Kantong kemasan & paper bag literan TIDAK punya penanda stokAwal: keduanya masuk
    // lewat formulir beli bahan biasa, jadi tidak ada bedanya di data selain tanggal.
    // Pemilik memastikan (12 Agu 2026) seluruh pembelian bahan bertanggal 8 Agustus 2026
    // adalah stok awal — barangnya dibeli bulan sebelumnya, cuma dicatat hari itu.
    const bahanDipakai = b => b.tipe === 'beli' && cocok(b.tanggal) && b.tanggal !== TANGGAL_STOK_AWAL;
    const beliKemasan = ambilBahanKemasan().filter(bahanDipakai);
    const beliLiteran = ambilBahanLiteran().filter(bahanDipakai);

    const masuk = [
      { label: 'Penjualan tunai', nominal: jmlHarga(tunai), n: tunai.length, satuan: 'transaksi' },
      { label: 'Penjualan QRIS', nominal: jmlHarga(qris), n: qris.length, satuan: 'transaksi' },
      { label: 'Pelunasan piutang', nominal: jmlNominal(piutangBayar), n: piutangBayar.length, satuan: 'pembayaran' },
      { label: 'Kasbon dikembalikan', nominal: jmlNominal(kasbonBayar), n: kasbonBayar.length, satuan: 'kali' },
      { label: 'Tukar — pelanggan menambah', nominal: tukarMasuk, n: returDipakai.filter(r => (r.selisihHargaTukar || 0) < 0).length, satuan: 'retur' },
      // Uang pribadi menyeberang jadi kas toko. Uang masuk sungguhan — tapi BUKAN
      // pendapatan, jadi tidak pernah menyentuh laba.
      { label: 'Modal owner disetor', nominal: jmlNominal(modalSetor), n: modalSetor.length, satuan: 'kali' }
    ];
    const keluar = [
      { label: 'Belanja beras (tunai + bongkar)', nominal: belanja, n: batch.length, satuan: 'kedatangan' },
      { label: 'Bayar bon pemasok', nominal: jmlNominal(bayarBon), n: bayarBon.length, satuan: 'pembayaran' },
      { label: 'Biaya bulanan', nominal: biayaBulanan, n: bayarTerhitung.length, satuan: 'pembayaran',
        ket: bayarTerhitung.length
          ? bayarTerhitung.map(x => x.label).join(', ')
          : 'belum ada pos yang tercatat dibayar' },
      { label: 'Pengeluaran harian (Toko)', nominal: jmlNominal(harianToko), n: harianToko.length, satuan: 'catatan' },
      { label: 'Prive owner — hidup dari laci', nominal: jmlNominal(harianOwner), n: harianOwner.length, satuan: 'catatan' },
      { label: 'Bayar utang ke owner', nominal: jmlNominal(bayarUtangOwner), n: bayarUtangOwner.length, satuan: 'pembayaran' },
      { label: 'Refund retur', nominal: refund, n: returDipakai.length, satuan: 'retur' },
      { label: 'Beli kantong kemasan', nominal: jmlHarga(beliKemasan), n: beliKemasan.length, satuan: 'pembelian' },
      { label: 'Beli paper bag literan', nominal: jmlHarga(beliLiteran), n: beliLiteran.length, satuan: 'pembelian' },
      { label: 'Kasbon diambil pegawai', nominal: jmlNominal(kasbonAmbil), n: kasbonAmbil.length, satuan: 'kali' },
      // Setoran malam + penarikan modal ke kantong owner — uang benar-benar keluar dari
      // kas toko, tapi BUKAN biaya (lihat Ke-Mana-Uang: baris & vonisnya sendiri).
      { label: 'Setoran ke owner & tarik modal', nominal: jmlNominal(setoran), n: setoran.length, satuan: 'kali' }
    ];
    const totalMasuk = masuk.reduce((a, x) => a + x.nominal, 0);
    const totalKeluar = keluar.reduce((a, x) => a + x.nominal, 0);
    return {
      masuk, keluar, totalMasuk, totalKeluar,
      bersih: totalMasuk - totalKeluar,
      omzetPenuh: jmlHarga(jual), kreditBulanIni: jmlHarga(kredit), jumlahKredit: kredit.length,
      // Angka mentah per pos (13 Agu 2026) — dipakai kartu "Ke mana uang bulan ini"
      // supaya pecahannya berasal dari SUMBER YANG SAMA, bukan hitungan tandingan.
      pos: {
        tunai: jmlHarga(tunai), qris: jmlHarga(qris),
        pelunasan: jmlNominal(piutangBayar),
        kasbonBayar: jmlNominal(kasbonBayar), kasbonAmbil: jmlNominal(kasbonAmbil),
        tukarMasuk, refund, belanja, bayarBon: jmlNominal(bayarBon),
        berasDiutang: batch.reduce((a, k) => a + (batchDiutang(k) ? (k.merkList || []).reduce((x, m) => x + (m.subtotalHarga || 0), 0) : 0), 0),
        biayaBulanan, harian: jmlNominal(harianToko), prive: jmlNominal(harianOwner),
        beliKemasan: jmlHarga(beliKemasan), beliLiteran: jmlHarga(beliLiteran),
        setoran: jmlNominal(setoran),
        bayarUtangOwner: jmlNominal(bayarUtangOwner),
        modalSetor: jmlNominal(modalSetor), modalTarik: jmlNominal(setoran)
      }
    };
  }
  function hitungLabaRentang(cocok) {
    const semua = ambilPenjualan().filter(p => cocok(p.tanggal));
    const terhitung = semua.filter(hppTercatat);
    const tanpaHpp = semua.filter(p => !hppTercatat(p));
    const omzetHitungKotor = terhitung.reduce((a, p) => a + (p.hargaTotal || 0), 0);
    const hppKotor = terhitung.reduce((a, p) => a + (p.hppTotalSaatJual || 0), 0);
    // ===== RETUR IKUT LABA (perintah pemilik 9 Sep 2026) =====
    // Sampai commit ini fungsi ini hanya membaca ambilPenjualan(); ia TIDAK PERNAH
    // menyentuh ambilRetur(), dan simpanRetur tidak pernah menyentuh dokumen penjualannya.
    // Akibatnya refund keluar dari KAS tapi laba tidak bergerak satu rupiah pun — diukur
    // di kotak pasir: refund Rp1.000.000 menurunkan kas Rp1.000.000 sementara margin kotor
    // tetap Rp300.000. Laba lebih besar dari kenyataan sebesar SELURUH refund yang pernah
    // dibayar, sejak kapan pun jalur retur mulai dipakai, dan tidak ada satu layar pun yang
    // menyebutnya. Arahnya menenangkan — itu sebabnya ia bertahan paling lama.
    //
    // Bentuknya: uang kembali SELALU mengurangi omzet. HPP ikut dibalik HANYA kalau
    // kondisinya 'utuh', karena hanya barang utuh yang benar-benar kembali ke stok
    // (hitungStokKarungPerMerk 12704 & hitungStokKemasan 12802 sama-sama hanya menghitung
    // kondisi 'utuh'). Barang TIDAK UTUH tidak kembali, jadi biayanya tetap terbebankan —
    // dan itulah yang membuat rugi retur tidak-utuh tergambar sebesar barang yang hilang.
    //
    // TIDAK BERTABRAKAN dengan nilaiRp 0 pada rework karantina (744e3ef): karantina cuma
    // punya SATU pintu masuk (13343) yang berpagar kondisi === 'tidak_utuh' (13330), dan
    // cabang tidak-utuh di sini tidak membalik HPP. Jadi biaya barang karantina tetap
    // sudah lewat laba, persis alasan nilaiRp 0 itu ditulis. Diperiksa sebelum baris ini
    // ditulis, bukan sesudahnya.
    const returPeriode = ambilRetur().filter(r => cocok(r.tanggal));
    let returUang = 0, returHpp = 0;
    if (returPeriode.length > 0) {
      returUang = returPeriode.reduce((a, r) => a + uangKembaliRetur(r), 0);
      const adaUtuh = returPeriode.some(r => r.kondisi === 'utuh');
      // Stok baru dihitung kalau memang ada retur utuh di periode ini — fungsi ini
      // dipanggil per bulan dalam pengulangan laporan, dan sebagian besar periode nihil.
      if (adaUtuh) {
        const stokKrg = hitungStokKarungPerMerk(), stokKem = hitungStokKemasan();
        returPeriode.forEach(r => {
          if (r.kondisi === 'utuh') returHpp += hppTaksiranRetur(r, stokKrg, stokKem);
        });
      }
    }
    const omzetHitung = omzetHitungKotor - returUang;
    const hpp = hppKotor - returHpp;
    return {
      jumlahTrx: semua.length, jumlahHitung: terhitung.length, jumlahTanpaHpp: tanpaHpp.length,
      omzetPenuh: semua.reduce((a, p) => a + (p.hargaTotal || 0), 0) - returUang,
      omzetHitung, hpp, margin: omzetHitung - hpp,
      // Dipajang terpisah supaya layar bisa MENYEBUT pengurangnya, bukan cuma memajang
      // hasil yang lebih kecil tanpa sebab. Omzet - HPP tetap = margin.
      returUang, returHpp, returJumlah: returPeriode.length,
      omzetTanpaHpp: tanpaHpp.reduce((a, p) => a + (p.hargaTotal || 0), 0)
    };
  }
  function hitungLabaBersihRentang(dariIso, sampaiIso, bayaranBln) {
    const cocok = t => !!t && t >= dariIso && t <= sampaiIso;
    const laba = hitungLabaRentang(cocok);
    const bayaran = bayaranBln || bayaranBiayaBulanan();
    // BEBAN TOKO = belanja toko dari laci ('toko') DAN dari dompet pribadi owner
    // ('tokoDompet'). Keduanya beban toko yang sama besarnya; yang membedakan cuma
    // dari kantong mana uangnya keluar — dan itu urusan KAS, bukan urusan laba.
    // PENTING: pasangan baris ini di hitungArusKasInti (kas) SENGAJA tetap 'toko' saja.
    // Dua baris yang terlihat kembar itu memang harus menyimpang; lihat komentar di sana.
    const harianRows = ambilPengeluaranHarian().filter(h => (h.kategori === 'toko' || h.kategori === 'tokoDompet') && cocok(h.tanggal));
    const harianToko = harianRows.reduce((a, h) => a + (h.nominal || 0), 0);
    const dompetRows = harianRows.filter(h => h.kategori === 'tokoDompet');
    const harianDompet = dompetRows.reduce((a, h) => a + (h.nominal || 0), 0);
    const hapusRows = ambilPiutangMutasi().filter(m => m.tipe === 'hapusBuku' && cocok(m.tanggal));
    const hapusBuku = hapusRows.reduce((a, m) => a + (m.nominal || 0), 0);
    // SUSUT & SELISIH STOK — sukunya sendiri, sengaja tidak diselipkan ke biaya toko
    // maupun ke HPP: besarnya harus kelihatan supaya bisa ditagih perbaikannya.
    // DITULIS SEBAGAI PENJUMLAHAN dengan tanda apa adanya (nilaiRp negatif = stok
    // berkurang = laba turun), supaya tandanya tidak pernah tertukar di kemudian hari.
    const susutRows = barisSusutStok(cocok);
    const susutStok = susutRows.reduce((a, x) => a + x.nilaiRp, 0);
    let jatahBulanan = 0, nHari = 0;
    for (let t = dariIso; t <= sampaiIso; t = geserHari(t, 1)) { jatahBulanan += jatahBiayaBulananHari(t, bayaran); nHari++; }
    const biayaToko = harianToko + jatahBulanan;
    return Object.assign(laba, {
      dariIso, sampaiIso, nHari, harianToko, nHarian: harianRows.length, jatahBulanan, biayaToko,
      harianDompet, nDompet: dompetRows.length,
      hapusBuku, nHapus: hapusRows.length, susutStok, nSusut: susutRows.length,
      labaBersih: laba.margin - biayaToko - hapusBuku + susutStok
    });
  }
  function barisSusutStok(cocok) {
    const baris = [];
    const tambah = (x, nama, satuan, jumlah, alasan) => {
      if (typeof x.nilaiRp !== 'number' || !isFinite(x.nilaiRp) || x.nilaiRp === 0) return;
      if (!x.tanggal || x.tanggal < MULAI_SUSUT_LABA || !cocok(x.tanggal)) return;
      baris.push({ tanggal: x.tanggal, jam: x.jam || '', nama, satuan,
        jumlah: jumlah || 0, nilaiRp: x.nilaiRp, alasan: alasan || '' });
    };
    ambilPenyesuaianStok().forEach(x => tambah(x, x.merk || '(karung)', 'kg', x.selisihKg, x.alasan));
    ambilPenyesuaianKemasan().forEach(x =>
      tambah(x, (x.namaProduk || '') + ' ' + x.ukuranKemasan + ' kg', 'unit', x.selisihUnit, x.alasan));
    ambilBahanKemasan().concat(ambilBahanLiteran()).forEach(x => {
      if (x.tipe === 'opname') tambah(x, labelBahan(x.jenis), 'pcs', x.jumlah, x.catatan);
    });
    return baris.sort((a, b) => (a.tanggal < b.tanggal ? 1 : a.tanggal > b.tanggal ? -1 : 0));
  }
  function bayaranBiayaBulanan() {
    const out = [];
    const barisGaji = [];   // dikumpulkan dulu lintas bulan, potongan kasbon dipakaikan di bawah
    ambilBiayaBulanan().forEach(b => {
      // Peta per pos MENANG MUTLAK begitu dokumennya punya. tanggalBayar tunggal (bentuk
      // yang cuma dipakai beberapa jam pada 12 Agu 2026) hanya jadi cadangan untuk dokumen
      // yang belum pernah punya peta itu. Kalau dipakai sebagai cadangan PER KOLOM, pos
      // yang sengaja dikosongkan karena belum dibayar akan ikut bertanggal dan terhitung
      // sebagai uang keluar — persis kebalikan dari maksudnya.
      const punyaPerPos = !!b.tanggalBayarPos;
      const peta = b.tanggalBayarPos || {};
      POS_BIAYA_BULANAN.forEach(pos => {
        const nominal = b[pos.kunci] || 0;
        if (!(nominal > 0)) return;
        // Pos non-gaji: kotor = bersih, tidak ada potongan apa pun.
        out.push({ bulan: b.bulan, pos: pos.kunci, label: pos.label, labelLaba: pos.label,
          nominal, nominalKotor: nominal, dipotong: 0,
          tanggal: punyaPerPos ? (peta[pos.kunci] || '') : (b.tanggalBayar || '') });
      });
      // Gaji dipecah per pegawai. Yang harinya nol tidak menghasilkan pembayaran apa pun.
      // Dokumen lama: tanggalBayarGaji belum ada, jadi jatuh balik ke tanggal gaji gabungan
      // (tanggalBayarPos.gaji), lalu ke tanggalBayar tunggal — supaya catatan lama tidak
      // tiba-tiba jadi "belum dibayar" cuma karena bentuk datanya berubah.
      const petaGaji = b.tanggalBayarGaji || null;
      const cadanganGaji = (punyaPerPos ? (peta.gaji || '') : '') || b.tanggalBayar || '';
      (b.rincianGaji || []).forEach(r => {
        const nominal = r.gaji || 0;
        if (!(nominal > 0)) return;
        barisGaji.push({ bulan: b.bulan, pos: 'gaji:' + r.nama, nama: r.nama, kotor: nominal,
          tanggal: petaGaji ? (petaGaji[r.nama] || '') : cadanganGaji });
      });
    });

    // Potongan kasbon dipakaikan SESUDAH semua baris gaji terkumpul — urut tanggal bayar
    // paling lama dulu — supaya potongan yang melampaui satu bulan mengalir ke bulan
    // berikutnya, bukan terpaksa dipaksa muat lalu hilang.
    const sisaPotong = potonganGajiPerPegawai();
    barisGaji.sort((x, y) => String(x.tanggal || '9999').localeCompare(String(y.tanggal || '9999')));
    barisGaji.forEach(g => {
      const tersedia = sisaPotong[g.nama] || 0;
      const dipotong = Math.min(tersedia, g.kotor);
      if (dipotong > 0) sisaPotong[g.nama] = tersedia - dipotong;
      const tunai = g.kotor - dipotong;
      // DUA ANGKA, dua pertanyaan berbeda (koreksi pemilik 23 Agu 2026):
      //   nominal      = uang tunai yang benar-benar keluar laci  -> ARUS KAS & BUKU KAS
      //   nominalKotor = gaji penuh sebelum potongan kasbon       -> LABA
      // Kasbon yang dilunasi potong gaji adalah PENYELESAIAN PIUTANG kepada pegawai,
      // bukan pengurang biaya gaji: uang toko tetap terpakai penuh sebagai upah, yang
      // berubah cuma wujudnya (sebagian menutup piutang kasbon, bukan berpindah tangan).
      // Sebelum koreksi ini laba bersih tercatat TERLALU TINGGI sebesar total potongan.
      // Baris tetap dibuat walau tunainya nol — kalau di-skip seperti dulu, gaji yang
      // habis dipotong kasbon lenyap sama sekali dari biaya laba.
      out.push({ bulan: g.bulan, pos: g.pos, nama: g.nama, nominal: tunai, nominalKotor: g.kotor,
        dipotong, tanggal: g.tanggal, labelLaba: 'Gaji ' + g.nama,
        label: 'Gaji ' + g.nama + (dipotong > 0 ? ' (kotor ' + formatRupiah(g.kotor)
          + ' − kasbon ' + formatRupiah(dipotong) + ')' : '') });
    });
    return out;
  }
  function jatahBiayaBulananHari(iso, bayaranBln) {
    const bl = bulanDari(iso);
    // GAJI PENUH (nominalKotor), bukan gaji sesudah potongan kasbon — lihat alasannya
    // di bayaranBiayaBulanan(). Jalur kas tetap memakai x.nominal.
    const total = (bayaranBln || bayaranBiayaBulanan()).filter(x => x.bulan === bl)
      .reduce((a, x) => a + (x.nominalKotor === undefined ? x.nominal : x.nominalKotor), 0);
    const nHari = parseInt(akhirBulanIso(bl).slice(8, 10), 10);
    const hari = parseInt(iso.slice(8, 10), 10);
    const dasar = Math.floor(total / nHari);
    return hari === nHari ? total - dasar * (nHari - 1) : dasar;
  }

  function hitungStokKarungPerMerk(sampai) {
    // `sampai` (Tutup Buku, 13 Agu 2026): batas tanggal INKLUSIF. Kosong = semua.
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    const batch = batasi(ambilSemuaBatch()); // sudah terurut terbaru dulu (by id) dari pasangSinkronisasi/urutkanTerbaru
    const stok = {}; // { merk: { totalMasuk, terpakai, totalNilaiMasuk, hargaTerakhirPerKg, hppTerakhirPerKg } }

    batch.forEach(k => {
      const merkDenganHpp = hitungHppMerkDalamBatch(k.merkList, k.biayaBongkar);
      merkDenganHpp.forEach(m => {
        // Baris BAL bukan karung sumber — bags jadi yang stoknya hidup di hitungStokKemasan
        // lewat dokumen beli-jadi pasangannya. Ikut di sini = barang yang sama dihitung
        // dua kali. (Alokasi bongkarnya tetap dihitung atas SEMUA baris di atas — porsi
        // milik bal terbawa ke HPP per pcs-nya, bukan ke kolam.)
        if (m.bentuk === 'bal') return;
        if (!stok[m.merk]) stok[m.merk] = { totalMasuk: 0, terpakai: 0, totalNilaiMasuk: 0, hargaTerakhirPerKg: m.hargaPerKg, idTerakhir: k.id };
        stok[m.merk].totalMasuk += m.totalKg;
        // HPP dihitung RATA-RATA TERTIMBANG dari seluruh histori beli merk ini (pola sama dengan
        // bahan kemasan/literan) — bukan cuma HPP batch terakhir, supaya tidak bias kalau batch
        // lama yang jauh lebih murah/mahal masih jadi sebagian besar sisa stok.
        // Bug lama (ditemukan saat audit 1 Agustus 2026): pakai HPP batch dgn tanggal terbaru saja,
        // dan tie-break-nya salah arah (>= tanggal) sehingga batch tanggal sama tapi id lebih lama
        // yang menang, bukan yang benar-benar terakhir diinput.
        stok[m.merk].totalNilaiMasuk += m.hppPerKg * m.totalKg;
        // "Harga beli terakhir" (bukan HPP) tetap disimpan terpisah sebagai info referensi di tab Stok —
        // batch diproses terurut id menurun (terbaru dulu), jadi hasil pertama per merk sudah yang terbaru.
        if (k.id >= stok[m.merk].idTerakhir) {
          stok[m.merk].hargaTerakhirPerKg = m.hargaPerKg;
          stok[m.merk].idTerakhir = k.id;
        }
      });
    });

    // Kurangi pemakaian dari penjualan (jalur karung utuh & repacking dadakan & literan langsung dari merk)
    batasi(ambilPenjualan()).forEach(p => {
      if ((p.jenis === 'karung' || p.jenis === 'repacking' || p.jenis === 'literan') && p.merkSumber && stok[p.merkSumber]) {
        stok[p.merkSumber].terpakai += p.totalKg;
      }
    });

    // Kurangi pemakaian dari produksi kemasan (yang narik dari karung sumber).
    // Produksi campuran (4 Agu 2026) bawa sumberList per merk; produksi lama satu merk.
    // ambilProduksiBerlaku() (9 Agu 2026) — kalau raw ambilProduksi() dipakai, catatan
    // yang sudah dikoreksi ikut menarik kg pemakaian LAGI dari catatan penggantinya juga
    // (dobel hitung), karena keduanya sama-sama tersimpan sebagai dokumen terpisah.
    batasi(ambilProduksiBerlaku()).forEach(pr => {
      if (Array.isArray(pr.sumberList) && pr.sumberList.length > 0) {
        pr.sumberList.forEach(s => { if (s.merk && stok[s.merk]) stok[s.merk].terpakai += (s.kg || 0); });
      } else if (pr.merkSumber && stok[pr.merkSumber]) {
        stok[pr.merkSumber].terpakai += pr.kgDipakai;
      }
    });

    // Retur karung UTUH balik ke stok (kurangi "terpakai" = tambah sisa). Retur TIDAK UTUH masuk karantina, tidak di sini.
    batasi(ambilRetur()).forEach(r => {
      if (r.jenisAsal === 'karung' && r.kondisi === 'utuh' && r.merkSumber && stok[r.merkSumber]) {
        stok[r.merkSumber].terpakai -= r.totalKg;
      }
    });

    // Penyesuaian opname (12 Agu 2026): selisihKg = fisik − sistem saat dihitung.
    // Lewat 'terpakai' dan BUKAN 'totalMasuk', supaya HPP rata-rata tertimbang tidak
    // tersentuh — barang susut tidak mengubah harga modal barang yang tersisa.
    batasi(ambilPenyesuaianStok()).forEach(o => {
      if (o.merk && stok[o.merk]) stok[o.merk].terpakai -= (o.selisihKg || 0);
    });

    // Produksi 50 kg yang digabung balik ke karung utuh (keputusan My DeV 9 Agu 2026):
    // kg yang berhasil dipak ulang jadi karung ditambahkan sebagai stok BARU ke merk
    // tujuan yang dipilih pemakai — dinilai dari HPP bahan bakunya saja, TANPA upah
    // repacking, supaya rata-rata tertimbangnya tidak tercampur biaya buruh (sama
    // seperti batch beli menilai stok cuma dari harga barang, bukan ongkos apa pun
    // sesudahnya). Kg yang dikreditkan = kg yang benar-benar jadi karung (ukuran×unit),
    // bukan kg yang dipakai dari sumber — selisihnya (susut) sengaja tidak dikreditkan.
    batasi(ambilProduksiBerlaku()).forEach(pr => {
      if (!pr.jadiKarungUtuh || !pr.merkTujuan) return;
      const totalKgJadi = (pr.ukuranKemasan || 0) * (pr.jumlahUnit || 0);
      if (totalKgJadi <= 0) return;
      if (!stok[pr.merkTujuan]) stok[pr.merkTujuan] = { totalMasuk: 0, terpakai: 0, totalNilaiMasuk: 0, hargaTerakhirPerKg: 0, idTerakhir: pr.id };
      stok[pr.merkTujuan].totalMasuk += totalKgJadi;
      stok[pr.merkTujuan].totalNilaiMasuk += (pr.hppSumberPerKgDipakai || 0) * (pr.kgDipakai || 0);
    });

    const hasil = {};
    Object.keys(stok).forEach(merk => {
      hasil[merk] = {
        sisaKg: Math.round((stok[merk].totalMasuk - stok[merk].terpakai) * 100) / 100,
        hargaTerakhirPerKg: stok[merk].hargaTerakhirPerKg,
        // Nama field dipertahankan (dipakai luas di simpanPenjualan/simpanProduksi/tampilkanStok)
        // tapi isinya sekarang rata-rata tertimbang, bukan HPP batch terakhir saja.
        hppTerakhirPerKg: stok[merk].totalMasuk > 0 ? stok[merk].totalNilaiMasuk / stok[merk].totalMasuk : 0
      };
    });
    return hasil;
  }
  function hitungStokKemasan(sampai) {
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    // ambilProduksiBerlaku() (9 Agu 2026) — catatan yang HPP-nya sudah dikoreksi
    // dikeluarkan, supaya HPP-Rp0 yang lama tidak lagi ikut menyeret rata-rata
    // tertimbang produk itu (temuan audit margin: Angsa 25 kg & Kembang 10 kg).
    const produksi = batasi(ambilProduksiBerlaku());
    const stok = {}; // { "namaProduk|ukuranKg": { unitDibuat, unitTerjual, nilaiProduksiTotal } }

    // Semua kunci lewat kunciKemasan() (26 Agu 2026): ukuran tersimpan ada yang angka
    // ada yang teks, dan sampai sekarang loop-loop di bawah merangkai kuncinya sendiri
    // dengan '+' — satu dokumen berukuran teks sudah cukup membuat penjualan atau
    // penyesuaian meleset diam-diam ke kunci yang tidak ada.
    const kosongKemasan = (nama, ukuran) => ({ namaProduk: nama,
      ukuranKemasan: isFinite(Number(ukuran)) ? Number(ukuran) : ukuran,
      unitDibuat: 0, unitTerjual: 0, unitDipakaiProduksi: 0, nilaiProduksiTotal: 0, penyesuaian: 0 });

    produksi.forEach(pr => {
      // Produksi 50 kg yang digabung balik ke karung utuh BUKAN kemasan jadi — sudah
      // dihitung sebagai stok karung di hitungStokKarungPerMerk(). Ikut dihitung di sini
      // juga berarti barang yang sama muncul dobel di dua bagian tab Stok sekaligus.
      if (pr.jadiKarungUtuh) return;
      const kunci = kunciKemasan(pr.namaProduk, pr.ukuranKemasan);
      if (!stok[kunci]) stok[kunci] = kosongKemasan(pr.namaProduk, pr.ukuranKemasan);
      stok[kunci].unitDibuat += pr.jumlahUnit;
      stok[kunci].nilaiProduksiTotal += (pr.hppPerUnit || 0) * pr.jumlahUnit;
    });

    // ===== KEMASAN JADI YANG DIBONGKAR JADI BAHAN ADUKAN (26 Agustus 2026) =====
    // Sekarung Perahu Layar 50 kg yang sudah jadi boleh dibongkar lagi, dicampur beras
    // karung sumber, lalu dibungkus ulang jadi ukuran lain. Unit yang dipakai WAJIB
    // hilang dari stok — kalau tidak, karung yang sudah dibongkar tetap mengaku siap
    // jual (persis kebalikan bug BMW 20 kg yang baru dibereskan 26 Agu).
    //
    // Diturunkan dari ambilProduksiBerlaku() — BUKAN catatan pengembalian terpisah.
    // Akibatnya: produksi yang dikoreksi/dibatalkan MENGEMBALIKAN unitnya sendiri,
    // tanpa satu baris kode pengembalian pun. Pola yang sama dengan ambilPenjualan()
    // yang menyaring transaksi batal.
    produksi.forEach(pr => {
      (pr.sumberKemasanList || []).forEach(sk => {
        const kunci = kunciKemasan(sk.namaProduk, sk.ukuranKemasan);
        if (!stok[kunci]) stok[kunci] = kosongKemasan(sk.namaProduk, sk.ukuranKemasan);
        stok[kunci].unitDipakaiProduksi += (sk.unit || 0);
      });
    });

    batasi(ambilPenjualan()).forEach(p => {
      if (p.jenis === 'kemasan') {
        const kunci = kunciKemasan(p.namaProduk, p.ukuranKemasan);
        if (stok[kunci]) stok[kunci].unitTerjual += p.jumlahUnit;
      }
    });

    // Retur kemasan UTUH balik ke stok (kurangi unitTerjual = tambah sisa). Retur TIDAK UTUH masuk karantina, tidak di sini.
    batasi(ambilRetur()).forEach(r => {
      if (r.jenisAsal === 'kemasan' && r.kondisi === 'utuh') {
        const kunci = kunciKemasan(r.namaProduk, r.ukuranKemasan);
        if (stok[kunci]) stok[kunci].unitTerjual -= r.jumlahUnit;
      }
    });

    // COCOKKAN KEMASAN (26 Agu 2026): selisih hitungan gudang lawan sistem.
    // Ditambahkan sebagai suku TERSENDIRI (bukan lewat unitDibuat) — persis alasan yang
    // sama dengan opname bahan yang sengaja tidak lewat cabang 'beli': unit yang tidak
    // pernah diproduksi kalau ikut membagi rata-rata akan menyeret HPP jadi salah.
    // hppRataRataPerUnit tetap nilaiProduksiTotal / unitDibuat.
    batasi(ambilPenyesuaianKemasan()).forEach(o => {
      const kunci = kunciKemasan(o.namaProduk, o.ukuranKemasan);
      if (!stok[kunci]) stok[kunci] = kosongKemasan(o.namaProduk, o.ukuranKemasan);
      stok[kunci].penyesuaian += (o.selisihUnit || 0);
    });

    const hasil = {};
    Object.keys(stok).forEach(kunci => {
      const hppRataRata = stok[kunci].unitDibuat > 0 ? Math.round(stok[kunci].nilaiProduksiTotal / stok[kunci].unitDibuat) : 0;
      hasil[kunci] = { ...stok[kunci],
        // unitDipakaiProduksi = dibongkar jadi bahan adukan lain; nilainya sudah
        // mengalir ke HPP hasil adukan itu, jadi ia hilang dari sini dan tidak
        // pernah menyentuh pembagi rata-rata (unitDibuat).
        sisaUnit: stok[kunci].unitDibuat - stok[kunci].unitTerjual
          - (stok[kunci].unitDipakaiProduksi || 0) + (stok[kunci].penyesuaian || 0),
        hppRataRataPerUnit: hppRataRata };
    });
    return hasil;
  }

  function hitungStokBahanKemasan(sampai) {
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    const semua = batasi(ambilBahanKemasan());
    const stok = {}; // { jenis: { totalBeli, totalTerpakai, totalHargaBeli, sisaPcs, hppPerPcs (rata-rata tertimbang) } }
    JENIS_BAHAN_KEMASAN.forEach(j => { stok[j] = { totalBeli: 0, totalTerpakai: 0, totalHargaBeli: 0 }; });
    semua.forEach(b => {
      if (!stok[b.jenis]) stok[b.jenis] = { totalBeli: 0, totalTerpakai: 0, totalHargaBeli: 0 };
      if (b.tipe === 'pakai') {
        stok[b.jenis].totalTerpakai += b.jumlah;
      } else if (b.tipe === 'opname') {
        // Penyesuaian opname (13 Agu 2026): menggeser SISA saja. SENGAJA bukan lewat
        // cabang beli — kalau lewat sana, pcs gratisan ikut membagi rata-rata harga
        // dan menyeret ongkos kantong per pcs jadi salah.
        stok[b.jenis].penyesuaian = (stok[b.jenis].penyesuaian || 0) + b.jumlah;
      } else if (b.tipe === 'saldoAwal') {
        // Saldo pembuka tutup buku (13 Agu 2026): membawa sisa DAN harga rata-rata
        // tahun lalu, tapi bukan uang keluar — pembaca uang menyaring tipe 'beli'.
        stok[b.jenis].totalBeli += b.jumlah;
        stok[b.jenis].totalHargaBeli += (b.hargaTotal || 0);
      } else {
        stok[b.jenis].totalBeli += b.jumlah;
        stok[b.jenis].totalHargaBeli += (b.hargaTotal || 0);
      }
    });
    Object.keys(stok).forEach(j => {
      const s = stok[j];
      s.sisaPcs = s.totalBeli - s.totalTerpakai + (s.penyesuaian || 0);
      s.hppPerPcs = s.totalBeli > 0 ? Math.round(s.totalHargaBeli / s.totalBeli) : 0;
    });
    return stok;
  }

  function hitungStokBahanLiteran(sampai) {
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    const semua = batasi(ambilBahanLiteran());
    const stok = {};
    Object.keys(HARGA_AWAL_BAHAN_LITERAN).forEach(j => { stok[j] = { totalBeli: 0, totalTerpakai: 0, totalHargaBeli: 0 }; });
    semua.forEach(b => {
      if (!stok[b.jenis]) stok[b.jenis] = { totalBeli: 0, totalTerpakai: 0, totalHargaBeli: 0 };
      if (b.tipe === 'pakai') {
        stok[b.jenis].totalTerpakai += b.jumlah;
      } else if (b.tipe === 'opname') {
        // Penyesuaian opname (13 Agu 2026): menggeser SISA saja. SENGAJA bukan lewat
        // cabang beli — kalau lewat sana, pcs gratisan ikut membagi rata-rata harga
        // dan menyeret ongkos kantong per pcs jadi salah.
        stok[b.jenis].penyesuaian = (stok[b.jenis].penyesuaian || 0) + b.jumlah;
      } else if (b.tipe === 'saldoAwal') {
        // Saldo pembuka tutup buku (13 Agu 2026): membawa sisa DAN harga rata-rata
        // tahun lalu, tapi bukan uang keluar — pembaca uang menyaring tipe 'beli'.
        stok[b.jenis].totalBeli += b.jumlah;
        stok[b.jenis].totalHargaBeli += (b.hargaTotal || 0);
      } else {
        stok[b.jenis].totalBeli += b.jumlah;
        stok[b.jenis].totalHargaBeli += (b.hargaTotal || 0);
      }
    });
    Object.keys(stok).forEach(j => {
      const s = stok[j];
      s.sisaPcs = s.totalBeli - s.totalTerpakai + (s.penyesuaian || 0);
      s.hargaPerPcs = s.totalBeli > 0 ? Math.round(s.totalHargaBeli / s.totalBeli) : 0;
    });
    return stok;
  }
  function hitungPiutang(sampai) {
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    const peta = {};
    function slot(nama, urut) {
      const k = kunciPelanggan(nama);
      if (!k) return null;
      if (!peta[k]) peta[k] = { kunci: k, nama: String(nama).trim(), urutNama: urut || 0, kredit: 0, saldoAwal: 0, bayar: 0, dihapus: 0, mutasi: [] };
      // Ejaan yang dipakai = dari mutasi paling baru, supaya pembetulan ejaan ikut terpakai.
      if ((urut || 0) >= peta[k].urutNama) { peta[k].nama = String(nama).trim(); peta[k].urutNama = urut || 0; }
      return peta[k];
    }
    batasi(ambilPenjualan()).forEach(p => {
      if (p.caraBayar !== 'Kredit') return;
      const s = slot(p.namaPelanggan, p.id);
      if (!s) return;
      const n = p.hargaTotal || 0;
      s.kredit += n;
      s.mutasi.push({ jenis: 'jual', tanggal: p.tanggal, jam: p.jam || '', nominal: n, idTrx: p.id,
        ket: namaSingkatTrx(p) });
    });
    batasi(ambilPiutangMutasi()).forEach(m => {
      const s = slot(m.namaPelanggan, m.id);
      if (!s) return;
      const n = m.nominal || 0;
      if (m.tipe === 'bayar') {
        s.bayar += n;
        s.mutasi.push({ jenis: 'bayar', tanggal: m.tanggal, jam: m.jam || '', nominal: n, idMutasi: m.id,
          ket: 'Bayar' + (m.caraBayar ? ' · ' + m.caraBayar : '') + (m.catatan ? ' · ' + m.catatan : '') });
      } else if (m.tipe === 'saldoAwal') {
        s.saldoAwal += n;
        s.mutasi.push({ jenis: 'saldoAwal', tanggal: m.tanggal, jam: m.jam || '', nominal: n, idMutasi: m.id,
          ket: 'Saldo awal' + (m.catatan ? ' · ' + m.catatan : '') });
      } else if (m.tipe === 'hapusBuku') {
        // HAPUS BUKU (13 Agu 2026): utang yang diputuskan tidak akan kembali. Mengurangi
        // sisa SEPERTI pembayaran, tapi BUKAN uang masuk — arus kas & buku kas menyaring
        // tipe 'bayar' saja, jadi mutasi ini tidak pernah menyentuh kas. Jejaknya
        // permanen di riwayat pelanggan dan dilaporkan sebagai kerugian di Laporan
        // Bulanan. Dokumen tidak pernah dihapus — pola mutasi-saja seperti semua uang.
        s.dihapus += n;
        s.mutasi.push({ jenis: 'hapusBuku', tanggal: m.tanggal, jam: m.jam || '', nominal: n, idMutasi: m.id,
          ket: 'Hapus buku' + (m.alasan ? ' · ' + m.alasan : '') });
      }
    });
    const hasil = Object.keys(peta).map(k => {
      const s = peta[k];
      s.sisa = Math.round((s.kredit + s.saldoAwal - s.bayar - s.dihapus) * 100) / 100;
      s.total = s.kredit + s.saldoAwal;
      // UMUR PIUTANG (12 Agu 2026) — pembayaran dianggap melunasi utang TERTUA dulu
      // (FIFO), kebiasaan penagihan di mana pun. Sisa yang tinggal karena itu melekat
      // pada utang termuda, dan umurnya dihitung dari utang tertua yang BELUM tertutup.
      // Catatan 09 memperlihatkan kenapa ini penting: tujuh piutang di sana sudah lewat
      // setahun (dua di atas 3,5 tahun) tanpa pernah ada yang menandai mereka menua.
      const utang = s.mutasi.filter(m => m.jenis === 'jual' || m.jenis === 'saldoAwal')
        .slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
      // Hapus buku ikut memadamkan utang TERTUA lebih dulu, sama seperti pembayaran —
      // sisa yang tinggal memang melekat di utang yang lebih muda.
      let sisaBayar = s.bayar + s.dihapus;
      s.tanggalTertua = null;
      for (const u of utang) {
        if (sisaBayar >= u.nominal) { sisaBayar -= u.nominal; continue; }
        s.tanggalTertua = u.tanggal || null;   // utang pertama yang belum tertutup penuh
        break;
      }
      // Math.max(0, ...) dulu mengubah tanggal MASA DEPAN (salah ketik tahun) jadi "umur 0 hari"
      // — tak terbedakan dari utang yang lahir hari ini. Sekarang dibedakan: umurHari tetap
      // seperti dulu untuk tanggal yang wajar, dan tanggalJanggal menyala kalau tanggalnya
      // mendahului hari ini, supaya layar bisa menyebutnya alih-alih memajang nol yang wajar.
      const _umur = s.tanggalTertua
        ? Math.round((isoKeTanggal(tanggalLokalIso()) - isoKeTanggal(s.tanggalTertua)) / 86400000)
        : null;
      s.tanggalJanggal = !!(s.sisa > 0 && _umur !== null && _umur < 0);
      s.umurHari = (s.sisa > 0 && s.tanggalTertua) ? Math.max(0, _umur) : null;
      return s;
    });
    // Yang masih berutang di atas, TERTUA dulu — bukan terbesar. Yang menua diam-diam
    // itulah yang berubah jadi piutang mati; nominal besar yang baru kemarin justru
    // paling gampang ditagih. Yang sudah lunas turun ke bawah.
    hasil.sort((a, b) => (b.sisa > 0) - (a.sisa > 0)
      || (b.umurHari || 0) - (a.umurHari || 0)
      || (b.sisa - a.sisa) || a.nama.localeCompare(b.nama));
    return hasil;
  }
  function hitungUtangPemasok(sampaiIso) {
    const sd = t => !sampaiIso || String(t || '') <= sampaiIso;
    const per = {}; // pemasok -> { pemasok, bon: [{id, tanggal, nilai, dibayar}], saldoAwalTotal, dibayarTotal }
    const pastikan = nm => {
      const kunci = String(nm || '').trim();
      if (!kunci) return null;
      if (!per[kunci]) per[kunci] = { pemasok: kunci, bon: [], totalUtang: 0 };
      return per[kunci];
    };
    ambilSemuaBatch().forEach(k => {
      if (k.stokAwal || !batchDiutang(k)) return;
      if (!sd(k.tanggal)) return;
      const px = pastikan(k.pemasok);
      if (!px) return;
      const nilai = (k.merkList || []).reduce((a, m) => a + (m.subtotalHarga || 0), 0);
      px.bon.push({ id: String(k.id), tanggal: k.tanggal || '', nilai, dibayar: 0, jenis: 'batch' });
    });
    ambilUtangPemasokMutasi().forEach(m => {
      if (m.tipe !== 'saldoAwal') return;
      // Bon pra-sistem: umurnya dipegang bonTanggal, bukan tanggal dicatatnya.
      // Bon tanpa tanggal ('') selalu lolos — dia memang yang tertua, dan '' <= tanggal
      // apa pun. JANGAN jatuh ke m.tanggal di sini: itu tanggal DICATATNYA, dan bon lama
      // yang baru didigitalkan hari ini akan hilang dari jawaban "per tanggal" justru
      // karena dia tua. Kunci saring wajib sama persis dengan kunci urut di bawah
      // (m.bonTanggal || '') — kalau tidak, satu bon punya dua tanggal lahir.
      if (!sd(m.bonTanggal || '')) return;
      const px = pastikan(m.pemasok);
      if (!px) return;
      // Tanggal bon HARUS tanggal bonnya sendiri — bukan tanggal dicatatnya. Bon lama
      // tanpa tanggal tampil '(tanpa tanggal)' dan diurutkan PALING TUA ('' terurut
      // paling awal): bon pra-sistem memang yang tertua, dan umurnya jujur tak diketahui.
      px.bon.push({ id: String(m.id), tanggal: m.bonTanggal || '', nilai: m.nominal || 0, dibayar: 0, jenis: 'saldoAwal', catatan: m.catatan || '' });
    });
    Object.values(per).forEach(px => px.bon.sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal))));
    ambilUtangPemasokMutasi().forEach(m => {
      if (m.tipe !== 'bayar') return;
      if (!sd(m.tanggal)) return;
      const px = per[String(m.pemasok || '').trim()];
      if (!px) return;
      let sisa = m.nominal || 0;
      const tunjuk = m.bonId ? px.bon.find(b => b.id === String(m.bonId)) : null;
      // Hanya saat menjawab "per tanggal": kalau bon yang DITUNJUK pembayaran ini belum
      // lahir per tanggal itu, pembayarannya belum boleh mengalir ke bon tertua sebagai
      // cadangan — dia akan melunasi bon lain yang saat itu sungguh-sungguh masih
      // terbuka, dan utangnya menguap. Pembayaran tanpa bonId (dokumen lama) tetap
      // memakai cadangan seperti dulu, jadi jalur tanpa argumen tidak bergeser.
      if (sampaiIso && m.bonId && !tunjuk) return;
      if (tunjuk) {
        const ambil = Math.min(sisa, tunjuk.nilai - tunjuk.dibayar);
        tunjuk.dibayar += ambil; sisa -= ambil;
      }
      // sisa pembayaran (atau pembayaran tanpa penunjuk) mengalir ke bon tertua yang belum lunas
      px.bon.forEach(b => {
        if (sisa <= 0) return;
        const ambil = Math.min(sisa, b.nilai - b.dibayar);
        b.dibayar += ambil; sisa -= ambil;
      });
      // KELEBIHAN BAYAR TIDAK BOLEH MENGUAP. Kalau sesudah dua gelung di atas masih ada
      // `sisa`, artinya pembayaran ke pemasok ini melebihi SELURUH bon yang tercatat —
      // dan itu berarti ada kedatangan yang bonnya belum masuk buku. Dulu angka itu dibuang
      // tanpa jejak; hitungUtangOwner (tepat di atas) sudah membawa `tekor` keluar dengan
      // alasan yang sama, utang pemasok cuma belum kebagian.
      if (sisa > 0.5) px.tekor = Math.round((px.tekor || 0) + sisa);
    });
    const hasil = [];
    Object.values(per).forEach(px => {
      px.bon = px.bon.filter(b => b.nilai - b.dibayar > 0.5)
        .map(b => Object.assign(b, { sisa: Math.round(b.nilai - b.dibayar),
          umurHari: b.tanggal ? Math.max(0, Math.round((isoKeTanggal(tanggalLokalIso()) - isoKeTanggal(b.tanggal)) / 86400000)) : null }));
      px.totalUtang = px.bon.reduce((a, b) => a + b.sisa, 0);
      px.tekor = px.tekor || 0;   // selalu ada kolomnya, supaya pembaca tidak perlu menebak
      // Pemasok yang utangnya nol TAPI kelebihan dibayar tetap ikut keluar — kalau tidak, satu-
      // satunya jejak kelebihan bayar hilang lagi. totalUtang-nya 0, jadi totalUtangPemasokSemua
      // dan nBon tidak bergeser sedikit pun.
      if (px.totalUtang > 0 || px.tekor > 0) hasil.push(px);
    });
    return hasil.sort((a, b) => b.totalUtang - a.totalUtang);
  }
  function hitungUtangOwner(sampaiIso) {
    const sd = t => !sampaiIso || (t || '') <= sampaiIso;
    const mut = ambilUtangOwnerMutasi();
    const timbul = ambilPengeluaranHarian()
      .filter(h => h.kategori === 'tokoDompet' && sd(h.tanggal))
      .reduce((a, h) => a + (h.nominal || 0), 0)
      + mut.filter(m => m.tipe === 'saldoAwal' && sd(m.tanggal))
        .reduce((a, m) => a + (m.nominal || 0), 0);
    const bayar = mut.filter(m => m.tipe === 'bayar' && sd(m.tanggal))
      .reduce((a, m) => a + (m.nominal || 0), 0);
    // TEKOR dibawa keluar, tidak dibungkam. Dibayar melebihi yang pernah timbul berarti
    // ada dokumen sisi-timbul yang hilang (dihapus tangan, atau tersapu tutup buku yang
    // tidak membawa pasangannya). Kalau dijepit diam-diam ke nol, kerusakan itu tidak
    // cuma tersembunyi — dia MEMAKAN utang berikutnya sampai sebesar tekornya.
    return { timbul, bayar, sisa: Math.max(0, timbul - bayar), tekor: Math.max(0, bayar - timbul) };
  }
  function hitungKasbon(sampai) {
    const batasi = arr => sampai ? arr.filter(x => (x.tanggal || '') <= sampai) : arr;
    const peta = {};
    batasi(ambilKasbonMutasi()).forEach(m => {
      const k = kunciPelanggan(m.namaPegawai);
      if (!k) return;
      if (!peta[k]) peta[k] = { kunci: k, nama: String(m.namaPegawai).trim(), urutNama: 0, ambil: 0, bayar: 0, mutasi: [] };
      const s = peta[k];
      if ((m.id || 0) >= s.urutNama) { s.nama = String(m.namaPegawai).trim(); s.urutNama = m.id || 0; }
      const n = m.nominal || 0;
      if (m.tipe === 'bayar') {
        s.bayar += n;
        s.mutasi.push({ jenis: 'bayar', tanggal: m.tanggal, nominal: n, id: m.id,
          ket: 'Dikembalikan' + (m.caraBayar ? ' · ' + m.caraBayar : '') + (m.catatan ? ' · ' + m.catatan : '') });
      } else if (m.tipe === 'saldoAwal') {
        // Saldo pembuka tutup buku — menambah tanggungan seperti ambil, tapi BUKAN uang
        // keluar tahun ini: arus kas menyaring tipe 'ambil' saja.
        s.ambil += n;
        s.mutasi.push({ jenis: 'saldoAwal', tanggal: m.tanggal, nominal: n, id: m.id,
          ket: 'Saldo awal (tutup buku)' + (m.catatan ? ' · ' + m.catatan : '') });
      } else {
        s.ambil += n;
        s.mutasi.push({ jenis: 'ambil', tanggal: m.tanggal, nominal: n, id: m.id,
          ket: 'Ambil kasbon' + (m.catatan ? ' · ' + m.catatan : '') });
      }
    });
    const hasil = Object.keys(peta).map(k => {
      const s = peta[k];
      s.sisa = Math.round((s.ambil - s.bayar) * 100) / 100;
      s.mutasi.sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (b.id || 0) - (a.id || 0));
      return s;
    });
    hasil.sort((a, b) => (b.sisa - a.sisa) || a.nama.localeCompare(b.nama));
    return hasil;
  }
  function kasPada(sampaiTgl) {
    const t = ambilTitikKas();
    if (!t) return null;
    if (sampaiTgl && sampaiTgl < t.tanggal) return null;   // mundur dari titik = tidak tahu, bukan menebak
    let saldo = (t.laci || 0) + (t.rekening || 0) + (t.amplop || 0) + (t.brankas || 0);
    daftarGerakanKas().forEach(r => {
      if (r.t > t.tanggal && (!sampaiTgl || r.t <= sampaiTgl)) saldo += r.masuk - r.keluar;
    });
    return saldo;
  }
  function bagiBiayaAdukan(baris, totalBiaya) {
    const totalKgJadi = baris.reduce((a, x) => a + (x.ukuranKemasan || 0) * (x.jumlahUnit || 0), 0);
    if (!(totalKgJadi > 0)) return null;
    let terpakai = 0;
    return baris.map((x, i) => {
      if (i < baris.length - 1) {
        const v = Math.round(totalBiaya * (x.ukuranKemasan || 0) / totalKgJadi);
        terpakai += v * (x.jumlahUnit || 0);
        return v;
      }
      return (totalBiaya - terpakai) / (x.jumlahUnit || 1);
    });
  }
  function hitungNeraca(sampai) {
    const stokK = hitungStokKarungPerMerk(sampai);
    // STOK MINUS MENGURANGI KEKAYAAN, tidak dinilai Rp0. Menjepitnya membuat merek yang
    // catatannya minus terbaca sama dengan merek yang pas habis — dan kekayaan toko memajang
    // barang yang menurut bukunya sendiri tidak ada. Diukur 16 Sep 2026 dengan mesin ini atas
    // cadangan 11 Sep: nol merek minus, jadi angka hari ini TIDAK bergeser sedikit pun; yang
    // berubah cuma apa yang terjadi kalau minusnya kembali.
    const nilaiSack = Object.keys(stokK).reduce((a, m) =>
      a + (stokK[m].sisaKg || 0) * (stokK[m].hppTerakhirPerKg || 0), 0);
    const sackMinus = Object.keys(stokK).filter(m => (stokK[m].sisaKg || 0) < -0.05);
    const stokB = hitungStokKemasan(sampai);
    const nilaiBags = Object.keys(stokB).reduce((a, k) =>
      a + (stokB[k].sisaUnit || 0) * (stokB[k].hppRataRataPerUnit || 0), 0);
    const bagsMinus = Object.keys(stokB).filter(k => (stokB[k].sisaUnit || 0) < 0);
    const bhk = hitungStokBahanKemasan(sampai), bhl = hitungStokBahanLiteran(sampai);
    const nilaiBahan = Object.keys(bhk).reduce((a, j) => a + Math.max(0, bhk[j].sisaPcs || 0) * (bhk[j].hppPerPcs || 0), 0)
      + Object.keys(bhl).reduce((a, j) => a + Math.max(0, bhl[j].sisaPcs || 0) * (bhl[j].hargaPerPcs || 0), 0);
    const daftarPiutang = hitungPiutang(sampai).filter(x => x.sisa > 0);
    const piutang = daftarPiutang.reduce((a, x) => a + x.sisa, 0);
    const daftarKasbon = hitungKasbon(sampai).filter(x => x.sisa > 0);
    const kasbon = daftarKasbon.reduce((a, x) => a + x.sisa, 0);
    const kas = kasPada(sampai || null);
    const stok = Math.round(nilaiSack + nilaiBags + nilaiBahan);
    const uo = hitungUtangOwner(sampai || null);
    const utangOwner = uo.sisa;
    const up = totalUtangPemasokSemua(sampai || null);
    const utangPemasok = up.nominal || 0;
    return { kas, nilaiSack: Math.round(nilaiSack), nilaiBags: Math.round(nilaiBags),
      nilaiBahan: Math.round(nilaiBahan), stok, piutang, nPiutang: daftarPiutang.length,
      kasbon, nKasbon: daftarKasbon.length,
      utangOwner, utangPemasok, nBonPemasok: up.nBon || 0,
      // Daftar merek yang catatannya MINUS dibawa keluar supaya layar bisa menyebutnya.
      // Tanpa ini nilai minus cuma mengurangi diam-diam, dan pembaca melihat kekayaan yang
      // lebih kecil tanpa tahu sebabnya — menukar satu kebohongan dengan kebohongan lain.
      sackMinus, bagsMinus, adaStokMinus: (sackMinus.length + bagsMinus.length) > 0,
      kewajiban: utangOwner + utangPemasok,
      total: kas === null ? null : Math.round(kas + stok + piutang + kasbon - utangOwner - utangPemasok) };
  }
  function hitungHppMerkDalamBatch(daftarMerk, biayaBongkar) {
    const totalKgSemua = daftarMerk.reduce((a, m) => a + m.totalKg, 0);
    return daftarMerk.map(m => {
      const alokasiBongkar = totalKgSemua > 0 ? (m.totalKg / totalKgSemua) * biayaBongkar : 0;
      const hppPerKg = m.totalKg > 0 ? (m.subtotalHarga + alokasiBongkar) / m.totalKg : 0;
      return { ...m, alokasiBongkar, hppPerKg };
    });
  }
  function pembulatanTunai(total, caraBayar) {
    return bakuCaraBayar(caraBayar) === 'Tunai' && total > 0 ? bulatKeAtas500(total) - Math.round(total) : 0;
  }
  function hitungLajuPakai() {
    const mulai = tanggalLokalIso(new Date(Date.now() - JENDELA_LAJU_HARI * 86400000));
    const kgMerk = {}, unitKemasan = {}, pcsBahan = {};
    ambilPenjualan().forEach(p => {
      if ((p.tanggal || '') < mulai) return;
      if ((p.jenis === 'karung' || p.jenis === 'repacking' || p.jenis === 'literan') && p.merkSumber) {
        kgMerk[p.merkSumber] = (kgMerk[p.merkSumber] || 0) + (p.totalKg || 0);
      }
      if (p.jenis === 'kemasan') {
        const k = kunciKemasan(p.namaProduk, p.ukuranKemasan);
        unitKemasan[k] = (unitKemasan[k] || 0) + (p.jumlahUnit || 0);
      }
    });
    // Produksi ikut menguras kolam sack — bagian dari laju pemakaian merk.
    ambilProduksiBerlaku().forEach(pr => {
      if ((pr.tanggal || '') < mulai) return;
      if (Array.isArray(pr.sumberList) && pr.sumberList.length > 0) {
        pr.sumberList.forEach(x => { if (x.merk) kgMerk[x.merk] = (kgMerk[x.merk] || 0) + (x.kg || 0); });
      } else if (pr.merkSumber && !pr.beliJadi) {
        kgMerk[pr.merkSumber] = (kgMerk[pr.merkSumber] || 0) + (pr.kgDipakai || 0);
      }
    });
    ambilBahanKemasan().concat(ambilBahanLiteran()).forEach(b => {
      if (b.tipe !== 'pakai' || (b.tanggal || '') < mulai) return;
      pcsBahan[b.jenis] = (pcsBahan[b.jenis] || 0) + (b.jumlah || 0);
    });
    const bagi = o => { const h = {}; Object.keys(o).forEach(k => { h[k] = o[k] / JENDELA_LAJU_HARI; }); return h; };
    return { kgMerk: bagi(kgMerk), unitKemasan: bagi(unitKemasan), pcsBahan: bagi(pcsBahan) };
  }
  function tbDaftarKoleksi(tahun) {
    const cutoff = tbCutoff(tahun);
    // Pembuka piutang sengaja bertanggal utang tertuanya (supaya umurnya jujur), jadi
    // tanggalnya jatuh SEBELUM cutoff dan langkah 3 akan menghapus dokumen yang baru
    // ditulis langkah 2 — itu sebabnya ada pengecualian di sini.
    // Tapi pengecualiannya WAJIB dibatasi pada tutup buku yang SEDANG berjalan. Kalau
    // semua dokumen ber-tutupBuku kebal selamanya, pembuka tahun-tahun lalu ikut lolos,
    // lalu tutup buku berikutnya menghitung sisanya LAGI dan menulis pembuka baru di
    // sebelahnya — piutang, kasbon, stok, dan (sejak G4) kewajiban BERLIPAT DUA tiap
    // pergantian tahun. Terukur: Rp1jt -> Rp1jt -> Rp2jt -> Rp4jt pada tiga siklus.
    // Pembuka tahun lalu memang HARUS ikut diarsipkan dan dihapus — dia bagian riwayat
    // tahun ini, persis seperti dokumen biasa.
    const tgl = arr => arr.filter(x => (x.tanggal || '') <= cutoff && !(x.tutupBuku && x.tahunDari === tahun));
    return [
      { koleksi: KOLEKSI_PENJUALAN,      label: 'penjualan',          dok: tgl(ambilPenjualanSemua()) },
      { koleksi: KOLEKSI_BATCH,          label: 'kedatangan',         dok: tgl(ambilSemuaBatch()) },
      { koleksi: KOLEKSI_PRODUKSI,       label: 'produksi',           dok: tgl(ambilProduksi()) },
      { koleksi: KOLEKSI_RETUR,          label: 'retur',              dok: tgl(ambilRetur()) },
      { koleksi: KOLEKSI_KARANTINA,      label: 'karantina',          dok: tgl(ambilKarantina()) },
      { koleksi: KOLEKSI_HARIAN,         label: 'pengeluaran harian', dok: tgl(ambilPengeluaranHarian()) },
      // Yang belum tuntas disaring keluar SEBELUM tgl() — jadi ia tidak diarsipkan sebagai
      // riwayat (memang bukan riwayat, ia masih berjalan) dan tidak ikut dihapus.
      { koleksi: KOLEKSI_PESANAN,        label: 'pesanan',            dok: tgl(ambilPesanan().filter(p => !pesananBelumTuntas(p))) },
      { koleksi: KOLEKSI_SETORAN,        label: 'setoran kas',        dok: tgl(ambilSetoranKas()) },
      { koleksi: KOLEKSI_PENY_KEMASAN,   label: 'penyesuaian kemasan', dok: tgl(ambilPenyesuaianKemasan()) },
      { koleksi: KOLEKSI_AMPLOP,         label: 'amplop laba',        dok: tgl(ambilAmplopLaba()) },
      { koleksi: KOLEKSI_MODAL,          label: 'modal owner',        dok: tgl(ambilModalOwner()) },
      { koleksi: KOLEKSI_UTANG_PEMASOK,  label: 'utang pemasok',      dok: tgl(ambilUtangPemasokMutasi()) },
      // WAJIB berdampingan dengan utang pemasok. Kalau koleksi ini absen, sisi TIMBUL
      // utang owner ikut terhapus (dia dokumen pengeluaranHarian 'tokoDompet', koleksi
      // di atas) sementara sisi LUNAS-nya hidup selamanya — utangnya menguap DAN
      // pelunasan yatimnya memakan utang tahun berikutnya.
      { koleksi: KOLEKSI_UTANG_OWNER,    label: 'utang ke owner',     dok: tgl(ambilUtangOwnerMutasi()) },
      { koleksi: KOLEKSI_TEMBUSAN,       label: 'tembusan stok',      dok: tgl(ambilTembusanStok()) },
      { koleksi: KOLEKSI_BAHAN_KEMASAN,  label: 'bahan kemasan',      dok: tgl(ambilBahanKemasan()) },
      { koleksi: KOLEKSI_BAHAN_LITERAN,  label: 'bahan literan',      dok: tgl(ambilBahanLiteran()) },
      { koleksi: KOLEKSI_PIUTANG,        label: 'mutasi piutang',     dok: tgl(ambilPiutangMutasi()) },
      { koleksi: KOLEKSI_KASBON,         label: 'mutasi kasbon',      dok: tgl(ambilKasbonMutasi()) },
      { koleksi: KOLEKSI_PENYESUAIAN,    label: 'penyesuaian stok',   dok: tgl(ambilPenyesuaianStok()) },
      { koleksi: KOLEKSI_TUTUP,          label: 'tutup hari',         dok: tgl(ambilTutupHari()) },
      { koleksi: KOLEKSI_BULANAN,        label: 'biaya bulanan',      dok: ambilBiayaBulanan().filter(b => (b.bulan || '') <= tahun + '-12') }
    ];
  }

  function hitungSaldoTutup(tahun) {
    const cutoff = tbCutoff(tahun);
    const karung = [];
    const petaKarung = hitungStokKarungPerMerk(cutoff);
    Object.keys(petaKarung).forEach(m => {
      const st = petaKarung[m];
      if (Math.abs(st.sisaKg) < 0.01) return;
      karung.push({ merk: m, sisaKg: st.sisaKg, hppPerKg: st.hppTerakhirPerKg || 0,
        punya50: tbPunyaBerat(m, 50, cutoff), punya25: tbPunyaBerat(m, 25, cutoff) });
    });
    const kemasan = [];
    const petaKem = hitungStokKemasan(cutoff);
    Object.keys(petaKem).forEach(k => {
      const st = petaKem[k];
      if (!(st.sisaUnit > 0)) return;
      kemasan.push({ namaProduk: st.namaProduk, ukuran: st.ukuranKemasan, sisaUnit: st.sisaUnit, hppPerUnit: st.hppRataRataPerUnit || 0 });
    });
    const bahanK = [], bahanL = [];
    const petaBK = hitungStokBahanKemasan(cutoff);
    Object.keys(petaBK).forEach(j => { const st = petaBK[j];
      if (st.sisaPcs > 0) bahanK.push({ jenis: j, sisaPcs: st.sisaPcs, hargaRata: st.hppPerPcs || 0 }); });
    const petaBL = hitungStokBahanLiteran(cutoff);
    Object.keys(petaBL).forEach(j => { const st = petaBL[j];
      if (st.sisaPcs > 0) bahanL.push({ jenis: j, sisaPcs: st.sisaPcs, hargaRata: st.hargaPerPcs || 0 }); });
    const piutang = hitungPiutang(cutoff).filter(x => x.sisa > 0)
      .map(x => ({ nama: x.nama, sisa: x.sisa, tanggalTertua: x.tanggalTertua || cutoff }));
    const kasbon = hitungKasbon(cutoff).filter(x => x.sisa > 0)
      .map(x => ({ nama: x.nama, sisa: x.sisa }));
    // KEWAJIBAN (6 Sep 2026). Sebelum ini saldo penutupan hanya berisi HARTA — akibatnya
    // tiap pergantian tahun kewajiban yang menggantung lenyap: dokumennya dihapus di
    // langkah 3, saldo pembukanya tidak pernah ditulis. Untuk utang pemasok itu cacat
    // lama yang tak terlihat karena neraca belum punya sisi kewajiban; sesudah neraca
    // menampilkannya, hilangnya jadi lompatan kekayaan yang tidak bisa dijelaskan.
    // Utang pemasok dibawa PER BON supaya umur dan nama pemasoknya tetap jujur —
    // pola yang sama dengan piutang di atas.
    // AMPLOP LABA ikut menyeberang. amplopLaba ADA di tbDaftarKoleksi — dokumennya
    // diarsipkan lalu DIHAPUS langkah 3 — tapi sampai 6 Sep 2026 tidak ada saldo pembuka
    // yang menggantikannya. Kelas cacat yang sama dengan kewajiban di 78053f8; bedanya
    // di sini yang lenyap bukan utang, melainkan TEMPAT UANG. Akibatnya dua: laporan
    // bulanan memajang "Saldo amplop sekarang Rp0" padahal amplop fisiknya berisi, dan
    // penjaga kejujuran amplop tiap malam berteriak "LEBIH" sebesar isi amplop —
    // selamanya. Alarm yang selalu bohong akhirnya diabaikan, lalu alarm yang benar
    // ikut diabaikan.
    const amplop = saldoAmplop(cutoff);
    const utangOwner = hitungUtangOwner(cutoff).sisa;
    const utangPemasok = hitungUtangPemasok(cutoff).map(px => ({
      pemasok: px.pemasok,
      bon: px.bon.map(b => ({ sisa: b.sisa, bonTanggal: b.tanggal || '', catatan: b.catatan || '' }))
    }));
    return { tahun, cutoff, karung, kemasan, bahanK, bahanL, piutang, kasbon, amplop, utangOwner, utangPemasok };
  }

  function saldoAmplop(sampaiIso) {
    return ambilAmplopLaba().reduce((a, x) => {
      if (sampaiIso && String(x.tanggal || '') > sampaiIso) return a;
      return a + (x.tipe === 'ambil' ? -(x.nominal || 0) : (x.nominal || 0));
    }, 0);
  }
  function stokMaksJalur(jalur, kunci) {
    if (!kunci) return null;
    if (jalur === 'kemasan') { const s = hitungStokKemasan()[kunci]; return s ? Math.max(0, s.sisaUnit - wzDiKeranjang('kemasan', kunci)) : null; }
    if (jalur === 'karung') {
      const s = hitungStokKarungPerMerk()[kunci];
      const berat = parseFloat((document.getElementById('jualKarungBerat') || {}).value) || 50;
      // SETENGAH SACK boleh (permintaan pemilik 21 Agu 2026: 0,5 / 1,5 / 2,5).
      // Dibulatkan ke bawah ke kelipatan 0,5 supaya stok tetap TIDAK PERNAH minus:
      // sisa 629,84 kg / 50 = 12,596 -> 12,5 sack (625 kg), bukan 12,59.
      // Isi struk dikurangi dalam KG dulu, baru dibagi berat — kalau dibalik, pembulatan
      // ke bawah terjadi dua kali dan sisanya jadi lebih kecil dari yang sebenarnya ada.
      return s ? Math.max(0, Math.floor((s.sisaKg - wzDiKeranjang('karung', kunci)) / berat * 2) / 2) : null;
    }
    return null;
  }
  function wzDiKeranjang(jalur, kunci) {
    return wzDiKeranjangAktif(jalur, kunci) + wzDiKeranjangParkir(jalur, kunci);
  }
  function thDorongRiwayat(dokBaru, lama) {
    if (!lama) return;
    const salin = {};
    Object.keys(lama).forEach(k => { if (k !== 'riwayat') salin[k] = lama[k]; });
    salin.digantiPada = dokBaru.diubahPada;
    dokBaru.riwayat = (lama.riwayat || []).concat([salin]);
  }

export { hitungArusKasInti, hitungLabaRentang, hitungLabaBersihRentang, barisSusutStok, bayaranBiayaBulanan, jatahBiayaBulananHari, hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanKemasan, hitungStokBahanLiteran, hitungPiutang, hitungUtangPemasok, hitungUtangOwner, hitungKasbon, kasPada, bagiBiayaAdukan, hitungNeraca, hitungHppMerkDalamBatch, pembulatanTunai, hitungLajuPakai, tbDaftarKoleksi, hitungSaldoTutup, saldoAmplop, stokMaksJalur, wzDiKeranjang, thDorongRiwayat };
