#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_periksa_sesudah.py — PAKET C siap 2027 (8 Okt 2026): kartu "Pemeriksaan sesudah tutup buku" (Uang › Tutup buku). KOTAK PASIR (nama & angka contoh) di jsc.

Sesudah 13 Okt 2026 tidak ada lagi yang memeriksa cadangan SESUDAH tutup buku di luar aplikasi — aplikasi memeriksa sendiri, owner membaca kartunya.
Simulator ritual = uji_potret_tahun.py (persiapkan, ritual: putusan per tanggal → susunKunci → semua kiriman → arsip) + hasil periksa dibekukan saat arsip
habis (susunPeriksaArsip, seperti uang.js jalankanBuku) + selesai (susunSelesai). Kotak pasir potret ditambah buku khusus: buku 25 kg (indukUkuran), buku
wadah (stokWadah), karung wadah, karung belakang (merkAsal), buku adukan, merek pemasok, kemasan jadi, katalog harga (rak Jual), kasbon dua orang.

  S1  ritual 5 Jan 2027 → kartu tampil (fase selesaikan) → SEMUA pemeriksaan sama (6 kelompok, 27 baris); cache kembali utuh sesudah diperiksa; sumber =
      hasil yang DIBEKUKAN (tanggalnya); sesudah "selesai" tetap sama — juga 20 Jan sesudah kegiatan Januari sungguhan (jual karung & 25 kg, retur nota 2026,
      hitung ulang stok, barang masuk merek baru, adukan, bayar bon, modal, kasbon); "selesai" yang belum diakui server = belum bisa diperiksa; berkas
  S2  kapan tampil: sebelum ritual tidak; arsip belum habis tidak; selesai → sampai akhir Februari 2027 (10 Feb ya, 1 Mar tidak); ritual telat (selesai 20 Mar)
      → 30 hari sesudahnya; tutup buku tahun berikutnya: tahun = yang terakhir ditutup
  S3  KONTROL KOTAK (tiap kerusakan berbunyi di baris yang BENAR): modal pembuka diubah · merek pembuka dihapus · tanda 25 kg lepas · karung hilang dari rak ·
      potret bulan hilang / omzetnya berubah · stok minus disuntik · piutang pembuka diubah (sesudah & sebelum dibekukan) · penanda hilang · setoran dipotret
      hilang · SANGGAHAN: nama merek tertukar saat ritual (kg & rupiah sama) · bon pelanggan / kasbon / utang pindah orang (total sama) · bon pemasok pembuka
      diubah tanpa jejak · setoran ber-NTPN diganti setoran lain berjumlah sama.
      BUKAN kerusakan: setoran masa Desember sesudah tutup buku · CATATAN SUSULAN bertanggal 2026 (nota & setor modal) yang masuk sesudah kunci sebelum arsip
      habis (tetap beres, disebut, tanpa "batalkan" — juga sesudah selesai & "sudah dicatat") · karcis hari ritual yang ditulis sebelum kunci tapi telat masuk ·
      bon lama pemasok DIBETULKAN owner 15 Jan (jejak riwayat). Batasnya: nota yang ditulis SESUDAH jam kunci di hari ritual (berjualan selama arsip) = beda.
  S4  BELUM BISA DIPERIKSA ('?', bukan ✓): data belum dimuat · data ditolak server (modal owner; bon pelanggan & bon pemasok → baris saldo pembuka '?', bukan
      "hilang") · perangkat tanpa internet · data masih salinan perangkat (berita acara / pengaturan) · kiriman tutup buku & hasil beku masih menunggu server ·
      hasil tidak dibekukan & titik kas sudah maju (uang per tempat; dengan hasil beku tetap ✓) · tanpa patokan / potret / ringkasan / pembanding 31 Des
  S5  stok minus HARI INI karena catatan sesudah tutup buku: disebut di keterangan, bukan alasan "beda" (yang diperiksa = saldo pembuka)
  S6  layar: uang.js ASLI digambar di jsc (Mac, tablet, HP: ringkasan, ✓ / ✗ dua angka / ✗ satu keadaan untuk baris teks / ? dengan sebab, lihat semua, unduh,
      tanpa internet, galat tanpa pesan mentah, kalimat tanpa bahasa mesin) + statis: lokal app.js membawa keadaan muat; modul ada di modulepreload
  S7  HEMAT BACA NYALA (#111 × Paket C, owner 8 Okt): koleksi yang BELUM LENGKAP di perangkat ini (SATU sumber hemat-baca.js hbBelumLengkap → firebase.js
      hematKeadaan → app.js lokalPerangkat → uang.js muatData → pstKurang) = "?" dengan sebab toko ("data modal owner belum dibaca penuh sejak kuota baca direset
      pukul 15.00 WIB — ketuk "baca penuh sekarang" …"), bukan ✓; nyala & lengkap = SAMA PERSIS dengan mati; tanpa internet & ditolak server tetap menang; keputusan
      final lain memakai sumber yang sama: daftar periksa kunci bulan (⛔ butir hemat), Lanjutkan/Batalkan tutup buku (bkSambungan), gerbang g7 (layar langkah 1
      DAN pintu susunKunci), perkiraan kuota ("?"), Laporan › Pajak (pita "?", rekap konsultan / catat setoran / omzet tahun lalu dari sistem DITAHAN), dokumen
      Laporan untuk bank (Rekap Omzet Bulanan, Bukti Omzet, Neraca, laporan berkop, paket bank — DITAHAN). Sebab satu jenis catatan tidak dipinjamkan ke yang lain.
      Layar uang.js & laporan.js ASLI di jsc; saklar mati = HTML sama persis.

    python3 alat-uji/uji_periksa_sesudah.py                    → N lulus · 0 gagal
    python3 alat-uji/uji_periksa_sesudah.py --kontrol          → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_periksa_sesudah.py --cadangan=/jalur/backup-batch-….json   (atau env PERIKSA_ASAP=…) → simulasi ritual 2026 atas cadangan LOKAL:
        semua sama (dilewati di CI: cadangan toko tidak ada di repo; keluaran hanya jumlah baris & hitungan buku, tanpa rupiah)
    python3 alat-uji/uji_periksa_sesudah.py --banding=<ref git>   → UJI PEMBANDING saklar MATI: kartu, daftar gerbang, kunci bulan, Lanjutkan/Batalkan, layar
        Uang & Pajak dihitung dengan berkas di <ref> (mis. commit sebelum #111 × Paket C) dan berkas kerja — wajib SAMA PERSIS (keluar 2 kalau beda)
"""
import os, sys, json, subprocess
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
import uji_potret_tahun as UP  # noqa: E402

LOGIKA = 'baru/js/layar/periksa-sesudah-logika.js'
MODUL = [m for i, m in enumerate(UP.MODUL + ['baru/js/data/hemat-baca.js', LOGIKA]) if m not in (UP.MODUL + ['baru/js/data/hemat-baca.js', LOGIKA])[:i]]
M_OK = {'siap': True, 'siapN': 56, 'total': 56, 'ditolak': [], 'offline': False}
N_BARIS = 27

TAMBAH = r"""
// ---- kotak pasir potret + buku khusus & kasbon (angka contoh) — ditulis 1 Des 2026, sebelum ritual
function tambahBukuKhusus() { terapkanKeCache([
  { koleksi: 'batchMasuk', data: { id: 'kb1', tanggal: '2026-12-01', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [
    { merk: 'Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 12000, subtotalHarga: 6000000 },
    { merk: 'Bebek 25 kg', satuan: 'karung', beratKarung: 25, jumlahKarung: 8, totalKg: 200, hargaPerKg: 12100, subtotalHarga: 2420000, indukUkuran: 'Bebek' },
    { merk: 'Kelas Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, hargaPerKg: 10000, subtotalHarga: 2000000, merkPemasok: 'Merek Pemasok Contoh' },
    { merk: 'Tanpa Harga Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 10500, subtotalHarga: 1050000 },
    { merk: 'Wadah W1', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, stokWadah: 'W1' },
    { merk: 'Karung wadah W1', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, karungWadah: 'W1' },
    { merk: 'Karung belakang W1 · Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, hargaPerKg: 12000, subtotalHarga: 600000, karungBelakang: 'W1', merkAsal: 'Bebek' },
    { merk: 'Adukan Kembang 5 kg', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, bukuAdukan: 'Kembang|5' }] } },
  { koleksi: 'produksiKemasan', data: { id: 'kp1', tanggal: '2026-12-02', jam: '09:00', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 12, hppPerUnit: 61000, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true } },
  { koleksi: 'katalogHargaKarung', data: { id: 'Bebek', merk: 'Bebek', hargaPerKg: 13000 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Kelas Contoh', merk: 'Kelas Contoh', hargaPerKg: 11000 } },
  { koleksi: 'katalogHargaKarung', data: { id: 'Angsa', merk: 'Angsa', hargaPerKg: 13800 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Beo', merk: 'Beo', hargaPerKg: 14000 } },
  { koleksi: 'kasbonMutasi', data: { id: 'ksA', tipe: 'ambil', namaPegawai: 'Pekerja Contoh A', nominal: 300000, tanggal: '2026-12-03', jam: '09:00', catatan: 'contoh', dari: 'laci' } },
  { koleksi: 'kasbonMutasi', data: { id: 'ksB', tipe: 'ambil', namaPegawai: 'Pekerja Contoh B', nominal: 200000, tanggal: '2026-12-03', jam: '09:05', catatan: 'contoh', dari: 'laci' } }]); }
var M_OK = """ + json.dumps(M_OK) + r""";
function baris(H, id) { var x = null; H.kelompok.forEach(function (g) { g.baris.forEach(function (b) { if (b.id === id) x = b; }); }); return x; }
function ringkasH(H) { return H ? H.ringkas + ' | beda: ' + H.kelompok.reduce(function (o, g) { return o.concat(g.baris.filter(function (b) { return b.status !== 'sama'; }).map(function (b) { return b.id + '=' + b.status + ' ' + (b.sebab || '') + ' ' + (b.rincian || []).slice(0, 3).join('; '); })); }, []).join(' || ') : 'null'; }
/** Ritual penuh seperti uang.js: kunci → kiriman → arsip → hasil periksa dibekukan (pemegang = LA). */
function ritualPenuh(w) { var R = ritual(w); if (R.tolak) return R; var PA = susunPeriksaArsip(2026, w, LA, true); if (PA.dokumen) kirim({ dokumen: PA.dokumen }); return R; }
/** Ritual dengan jeda: kunci & semua kiriman, daftar arsip disusun (seperti jalankanBuku), lalu `sela()` (catatan yang masuk di tengah), arsip, beku. */
function ritualSela(w, sela) { putusSemua(w); var R = susunKunci(2026, D, w, LA); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); R.kiriman.forEach(kirim); var daftar = arsipBuku(2026).daftar;
  sela(); arsipkanDokumen(2026, daftar); var PA = susunPeriksaArsip(2026, w, LA, true); if (PA.dokumen) kirim({ dokumen: PA.dokumen }); return PA; }
function siapKotak(isoJam) { var w = persiapkan(jam(isoJam || '2027-01-05T10:00:00+07:00')); tambahBukuKhusus();
  // setoran PPh masa Juli (dicatat Agustus, sebelum ritual) — ikut potret pajak
  var wJul = jam('2026-08-14T10:00:00+07:00'); tulis(susunSetoran({ masaPajak: '2026-07', tanggalSetor: '2026-08-14', jumlah: String(Math.max(1, pjTahun(2026, new Date(__KINI)).daftar[6].pph || 1)), ntpn: 'AB12CD34EF56GH78', catatan: 'bukti kertas contoh' }, wJul, new Date(__KINI)));
  jam(w.kini); return w; }
/** Ubah satu dokumen di cache (salinan, tanpa penjaga — kerusakan SESUDAH ritual, mis. lewat Console). */
function ubahDok(koleksi, cari, ubah) { var k = KOLEKSI.filter(function (x) { return x.nama === koleksi; })[0]; var d = cacheMentah(k.cache).filter(cari)[0]; if (!d) throw new Error('kontrol: dokumen ' + koleksi + ' tidak ketemu'); var b = JSON.parse(JSON.stringify(d)); ubah(b); terapkanKeCache([{ koleksi: koleksi, data: b }]); return b; }
function hapusDok(koleksi, id) { terapkanKeCache([{ koleksi: koleksi, hapus: id }]); }
function pembuka(cache, f) { return cacheMentah(cache).filter(function (x) { return x.tutupBuku && x.tahunDari === 2026 && (!f || f(x)); }); }
/** Isi seluruh cache (untuk "kembali utuh sesudah diperiksa"). */
function fotoCache() { return KOLEKSI.map(function (k) { return k.nama + ':' + J(cacheMentah(k.cache)); }).join('\n'); }
/** Kegiatan Januari biasa sesudah ritual (12 Jan) — bukan kerusakan. */
function kegiatanJanuari() { jam('2027-01-12T10:00:00+07:00'); terapkanKeCache([
    { koleksi: 'penjualan', data: { id: 'jan1', tanggal: '2027-01-12', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek', totalKg: 100, beratKarungAcuan: 50, jumlahKarung: 2, hargaTotal: 1300000, hppTotalSaatJual: 1200000, trxId: 't-jan1' } },
    { koleksi: 'penjualan', data: { id: 'jan2', tanggal: '2027-01-12', jam: '10:05', caraBayar: 'Kredit', namaPelanggan: 'Pelanggan Contoh A', jenis: 'karung', merkSumber: 'Bebek 25 kg', totalKg: 50, beratKarungAcuan: 25, jumlahKarung: 2, hargaTotal: 650000, hppTotalSaatJual: 605000, trxId: 't-jan2' } },
    { koleksi: 'retur', data: { id: 'rtj', tanggal: '2027-01-12', jam: '11:00', jenisAsal: 'karung', merkSumber: 'Bebek', totalKg: 50, jumlahKarung: 1, beratKarungAcuan: 50, kondisi: 'utuh', penyelesaian: 'refund', nominalRefund: 650000, nilaiDikembalikan: 650000, notaAsalId: 'd30', notaAsalTanggal: '2026-12-30' } },
    { koleksi: 'penyesuaianStok', data: { id: 'opj', tanggal: '2027-01-12', jam: '20:00', merk: 'Kelas Contoh', selisihKg: -3, nilaiRp: -30000, alasan: 'tercecer' } },
    { koleksi: 'batchMasuk', data: { id: 'kbj', tanggal: '2027-01-08', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ merk: 'Merpati', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 11500, subtotalHarga: 5750000 }] } },
    { koleksi: 'katalogHargaKarung', data: { id: 'Merpati', merk: 'Merpati', hargaPerKg: 12500 } },
    { koleksi: 'produksiKemasan', data: { id: 'adj', tanggal: '2027-01-12', jam: '13:00', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 5, hppPerUnit: 61000, merkSumber: 'Bebek', kgDipakai: 25 } },
    { koleksi: 'piutangMutasi', data: { id: 'lbj', tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh B', nominal: 500000, tanggal: '2027-01-12', jam: '12:00', caraBayar: 'Tunai' } },
    { koleksi: 'modalOwner', data: { id: 'moj', tanggal: '2027-01-12', jam: '08:00', tipe: 'setor', nominal: 5000000, catatan: 'contoh' } },
    { koleksi: 'kasbonMutasi', data: { id: 'ksj', tipe: 'ambil', namaPegawai: 'Pekerja Contoh A', nominal: 100000, tanggal: '2027-01-12', jam: '09:00', catatan: 'contoh', dari: 'laci' } }]); }
"""

SKENARIO = r"""
// ==================== S1 · ritual 5 Jan 2027 → semua sama ====================
var W, H0;
coba('S1', function () {
  W = siapKotak();
  ok('S1 sebelum ritual: kartu tidak tampil (belum ada tahun yang ditutup sistem ini)', pstTahun(new Date(__KINI)) === null && pstPeriksa(new Date(__KINI), M_OK) === null);
  var R = ritualPenuh(W); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak);
  var A = acara(2026); var SB = A.pembukaRingkas && A.pembukaRingkas.sebelum;
  ok('S1 berita acara menyimpan ringkasan saldo pembuka (baris yang ditulis: beras bertanda & kemasan) DAN pembanding dari catatan hidup 31 Des (per merek, produk, pelanggan, orang, pemasok); bentuk diterima Firestore',
    A.pembukaRingkas && A.pembukaRingkas.versi === 2 && A.pembukaRingkas.beras.some(function (r) { return r.merk === 'Bebek 25 kg' && r.indukUkuran === 'Bebek' && r.kg === 200; }) && A.pembukaRingkas.kemasan.some(function (k) { return k.nama === 'Kembang' && k.unit === 12; })
    && !!SB && SB.merek.some(function (r) { return r.merk === 'Kelas Contoh' && r.kg === 200; }) && SB.kemasan.length >= 1 && SB.piutang.length === 2 && SB.kasbon.length === 2 && SB.utangP.length === 1 && !bentukFirestore(A.pembukaRingkas).length,
    J(SB && [SB.merek.slice(0, 2), SB.piutang, SB.kasbon, SB.utangP]));
  ok('S1 patokan hari tutup buku menyimpan jam & catatan Januari yang SUDAH ada saat kunci (bayar & hapus buku 4 Jan)', A.hariIni.jam === '10:00' && Array.isArray(A.hariIni.ada) && A.hariIni.ada.indexOf('piutangMutasi|pb2') >= 0 && A.hariIni.ada.indexOf('piutangMutasi|ph1') >= 0 && !bentukFirestore(A.hariIni).length, J([A.hariIni.jam, A.hariIni.ada]));
  var T = pstTahun(new Date(__KINI));
  ok('S1 sesudah kunci & arsip habis: kartu tampil untuk 2026, fase selesaikan (berita acara terkunci)', T && T.tahun === 2026 && T.fase === 'selesaikan' && T.acara.status === 'terkunci', J(T && { tahun: T.tahun, fase: T.fase }));
  var foto0 = fotoCache(); H0 = pstPeriksa(new Date(__KINI), M_OK); var foto1 = fotoCache();
  ok('S1 cache KEMBALI UTUH sesudah diperiksa (saringan "saat dibuka" & "seperti saat kunci" sementara) — isi tiap koleksi sama persis', foto0 === foto1, String(foto0.length) + ' → ' + String(foto1.length));
  ok('S1 sumber baris perbandingan = hasil yang DIBEKUKAN saat arsip habis, bertanggal (bukan dihitung ulang)', H0 && H0.sumber === 'hasil periksa ulang yang dibekukan saat arsip habis (5 Jan 2027)', H0 && H0.sumber);
  ok('S1 SEMUA pemeriksaan sama: 6 kelompok, 27 baris, 0 beda, 0 belum; ringkasan "Semua 27 pemeriksaan sama — tutup buku 2026 beres"; tanpa catatan sesudah kunci',
    H0 && H0.beres && H0.n === 27 && H0.nBeda === 0 && H0.nBelum === 0 && H0.kelompok.length === 6 && H0.ringkas === 'Semua 27 pemeriksaan sama — tutup buku 2026 beres' && H0.susulan === 0 && H0.sesudahKunci === 0, ringkasH(H0));
  ok('S1 kelompok 1 = 11 baris beku; kelompok 6 = 3 baris beku (piutang, utang pemasok, utang ke owner — tidak dobel) + per pelanggan / orang / pemasok',
    H0.kelompok[0].baris.length === 11 && H0.kelompok[5].baris.map(function (b) { return b.id; }).join(',') === 'piutang,utangP,utangO,piutangNama,kasbonNama,utangNama'
    && H0.kelompok[0].baris.every(function (b) { return ['piutang', 'utangP', 'utangO'].indexOf(b.id) < 0; }), J(H0.kelompok[5].baris.map(function (b) { return b.id; })));
  var c3 = baris(H0, 'rakJual'), c1 = baris(H0, 'bukuMerek'), c2 = baris(H0, 'bukuKemasan'), mb = baris(H0, 'modalPembuka');
  ok('S1 rak Jual: karung Bebek 50 & "Bebek" 25 kg (buku Bebek 25 kg), Kelas Contoh, Angsa, Beo; 5 tanda buku terbaca; merek tanpa harga disebut, bukan beda; keadaannya satu teks',
    c3.status === 'sama' && /^5 karung tampil di rak Jual, 5 tanda buku/.test(c3.ket) && /1 baris tanpa harga di katalog/.test(c3.ket) && c3.a === '5 karung di rak · 5 tanda buku', J(c3));
  ok('S1 buku beras per merek & kemasan saat 2027 dibuka = catatan 31 Des (pembanding yang berdiri sendiri); modal pembuka = neraca 31 Des di potret',
    c1.status === 'sama' && /pembanding: sisa per merek di catatan 31 Des/.test(c1.ket) && c1.a > 0 && Math.abs(c1.a - c1.b) < 0.01 && c2.status === 'sama' && c2.a === 12 && mb.status === 'sama' && mb.a === mb.b && /neraca 31 Des di potret/.test(mb.ket), J([c1, c2, mb]));
  ok('S1 per pelanggan / orang / pemasok saat dibuka = catatan 31 Des (2 pelanggan, 2 orang kasbon, 1 pemasok)', ['piutangNama', 'kasbonNama', 'utangNama'].every(function (id) { return baris(H0, id).status === 'sama'; })
    && baris(H0, 'piutangNama').a === acara(2026).sebelum.filter(function (b) { return b.id === 'piutang'; })[0].n && baris(H0, 'kasbonNama').a === 500000 && /^2 nama/.test(baris(H0, 'kasbonNama').ket), J([baris(H0, 'piutangNama'), baris(H0, 'kasbonNama'), baris(H0, 'utangNama')]));
  ok('S1 pajak 2026 dari potret: 12 bulan, omzet = potret, setoran Juli = potret (NTPN masih ada), layar Pajak 12 masa bertanda tutup buku',
    ['pajakPotret', 'pajakOmzet', 'pajakSetor', 'pajakLayar'].every(function (id) { return baris(H0, id).status === 'sama'; }) && baris(H0, 'pajakOmzet').a > 0 && baris(H0, 'pajakSetor').a > 0, J(H0.kelompok[3]));
  ok('S1 petunjuk fase selesaikan menyebut langkah berikutnya (cadangan sesudah · selesai, lalu unduh hasil pemeriksaan) — tanpa orang luar', H0.petunjuk.length === 1 && /unduh cadangan sesudah · selesai/.test(H0.petunjuk[0]) && !/claude/i.test(J(H0)), J(H0.petunjuk));
  var B = pstBerkas(H0, new Date(__KINI));
  ok('S1 berkas hasil pemeriksaan: nama per tahun, 6 kelompok, 27 baris bertanda "sama", ringkasan & status berita acara, catatan sesudah kunci 0', B.nama === 'pemeriksaan-tutup-buku-2026-miqbal.json' && B.isi.kelompok.length === 6 && B.isi.n === 27
    && B.isi.kelompok.reduce(function (a, g) { return a + g.baris.filter(function (b) { return b.hasil === 'sama'; }).length; }, 0) === 27 && B.isi.beritaAcara.status === 'terkunci' && JSON.parse(J(B.isi)).ringkasan === H0.ringkas
    && B.isi.catatanSesudahKunci.susulan === 0 && B.isi.dibetulkanSesudahKunci.length === 0, J(B.nama));
  // selesai (cadangan sesudah) → status selesai, tetap sama
  var wS = jam('2027-01-05T11:00:00+07:00'); tulis(susunSelesai(2026, 'cadangan-sesudah-contoh.json', wS, false, LA));
  var H1 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S1 sesudah "selesai": kartu tetap tampil, semua sama, petunjuk = simpan berkas bersama cadangan SESUDAH & kunci Januari mulai 4 Feb', acara(2026).status === 'selesai' && H1 && H1.beres && H1.fase === 'selesai' && /cadangan SESUDAH/.test(H1.petunjuk[0]) && /4 Feb/.test(H1.petunjuk[0]), ringkasH(H1));
  setelTertunda('tutupBukuAcara', ['2026']); var H1t = pstPeriksa(new Date(__KINI), M_OK); setelTertunda('tutupBukuAcara', []);
  ok('S1 berita acara "selesai" yang belum diakui server (menunggu di perangkat ini) → semua "belum bisa diperiksa", bukan beres', H1t.nBelum === H1t.n && !H1t.beres && /menunggu server/.test(baris(H1t, 'modalPembuka').sebab), ringkasH(H1t));
  kegiatanJanuari(); jam('2027-01-20T10:00:00+07:00'); var H2 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S1 20 Jan 2027 sesudah kegiatan Januari sungguhan (jual karung & 25 kg, retur nota 2026, hitung ulang, barang masuk merek baru, adukan, bayar bon, modal, kasbon): tetap semua sama — yang diperiksa saldo pembuka & hasil beku, bukan stok hari ini',
    H2 && H2.beres && H2.n === 27 && ambilPenjualanSemua().some(function (p) { return p.id === 'jan2'; }), ringkasH(H2));
});

// ==================== S2 · kapan kartu tampil ====================
coba('S2', function () {
  var w = siapKotak(); putusSemua(w); var R = susunKunci(2026, D, w, LA); R.kiriman.forEach(kirim);
  ok('S2 terkunci tetapi arsip BELUM habis: kartu tidak tampil (pita tutup buku menyuruh meneruskan arsip)', pstTahun(new Date(__KINI)) === null);
  arsipkanDokumen(2026, arsipBuku(2026).daftar); var PA = susunPeriksaArsip(2026, w, LA, true); kirim({ dokumen: PA.dokumen });
  ok('S2 arsip habis → tampil', !!pstTahun(new Date(__KINI)));
  tulis(susunSelesai(2026, 'cadangan-sesudah-contoh.json', jam('2027-01-05T12:00:00+07:00'), false, LA));
  jam('2027-02-10T10:00:00+07:00'); var a = !!pstTahun(new Date(__KINI)); jam('2027-02-28T23:00:00+07:00'); var b = !!pstTahun(new Date(__KINI)); jam('2027-03-01T08:00:00+07:00'); var c = !!pstTahun(new Date(__KINI));
  ok('S2 selesai 5 Jan: tampil 10 Feb & 28 Feb, tidak tampil 1 Mar 2027', a && b && !c, J([a, b, c]));
  ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { x.selesaiTanggal = '2027-03-20'; });
  jam('2027-04-18T10:00:00+07:00'); var d = !!pstTahun(new Date(__KINI)); jam('2027-04-20T10:00:00+07:00'); var e = !!pstTahun(new Date(__KINI));
  ok('S2 ritual telat (selesai 20 Mar): tampil sampai 30 hari sesudahnya (18 Apr ya, 20 Apr tidak)', d && !e, J([d, e]));
  // tahun berikutnya: berita acara 2027 selesai (tiruan) → tahun = 2027 (yang terakhir ditutup)
  terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'tb2027', tanggal: '2028-01-01', pemasok: 'TUTUP BUKU 2027', stokAwal: true, merkList: [], tutupBuku: true, tahunDari: 2027, bertahap: true, penandaBuku: true } },
    { koleksi: 'tutupBukuAcara', data: { id: '2027', tahun: 2027, status: 'selesai', tanggal: '2028-01-02', selesaiTanggal: '2028-01-02', paraf: { pada: '2028-01-02T03:00:00.000Z' } } }]);
  jam('2028-01-10T10:00:00+07:00'); var T = pstTahun(new Date(__KINI));
  ok('S2 tutup buku tahun berikutnya: kartu memeriksa 2027 (tahun yang terakhir ditutup), bukan 2026', T && T.tahun === 2027, J(T && T.tahun));
});

// ==================== S3 · kontrol kotak: tiap kerusakan berbunyi di barisnya ====================
function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); var H = pstPeriksa(new Date(__KINI), M_OK); if (!H || !H.beres) throw new Error('kotak tidak beres sebelum dirusak: ' + ringkasH(H)); return w; }
function hasilRusak() { var H = pstPeriksa(new Date(__KINI), M_OK); return H; }
coba('S3-modal', function () { siapRitual(); ubahDok('modalOwner', function (x) { return x.tutupBuku && x.tahunDari === 2026; }, function (x) { x.nominal += 1000000; });
  var H = hasilRusak(); var m = baris(H, 'modalPembuka');
  ok('S3 modal pembuka diubah → baris "Modal owner" BEDA dengan dua angkanya (neraca 31 Des vs saldo pembuka), ringkasan "jangan jualan/menagih dulu"', m.status === 'beda' && m.b - m.a === 1000000 && /^\d+ pemeriksaan beda — jangan jualan\/menagih dulu, lihat barisnya/.test(H.ringkas) && H.petunjuk.some(function (p) { return /Modal owner di buku 2027/.test(p) && /batalkan/.test(p); }), ringkasH(H)); });
coba('S3-merek', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Bebek 25 kg'; }); }, function (x) { x.merkList = x.merkList.filter(function (r) { return r.merk !== 'Bebek 25 kg'; }); });
  var H = hasilRusak(); var c1 = baris(H, 'bukuMerek'), c3 = baris(H, 'rakJual');
  ok('S3 satu merek pembuka dihapus → "Buku beras per merek" BEDA menyebut Bebek 25 kg (TIDAK ADA di buku) & rak Jual BEDA (25 kg tidak terbaca / tidak tampil)',
    c1.status === 'beda' && c1.rincian.some(function (t) { return /^Bebek 25 kg: 31 Des 200 kg → TIDAK ADA di buku$/.test(t); }) && c3.status === 'beda' && c3.rincian.some(function (t) { return /Bebek 25 kg/.test(t); }), J([c1.rincian, c3.rincian])); });
coba('S3-tanda', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Bebek 25 kg'; }); }, function (x) { x.merkList.forEach(function (r) { if (r.merk === 'Bebek 25 kg') delete r.indukUkuran; }); });
  var H = hasilRusak(); var c3 = baris(H, 'rakJual'), c1 = baris(H, 'bukuMerek');
  ok('S3 tanda buku 25 kg lepas dari dokumen pembuka (kg tetap) → rak Jual BEDA: tanda tidak terbaca; buku per merek tetap sama; keadaan rak = satu teks yang menyebut jumlah yang tidak cocok',
    c3.status === 'beda' && c3.rincian.some(function (t) { return /Bebek 25 kg: tanda buku 25 kg \(induk Bebek\) tidak terbaca/.test(t); }) && c1.status === 'sama' && /tidak cocok$/.test(c3.a) && c3.b === null, J([c3.a, c3.rincian])); });
coba('S3-potret', function () { siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { delete x.potret.bulan['2026-08']; });
  var H = hasilRusak(); var d1 = baris(H, 'pajakPotret');
  ok('S3 potret satu bulan hilang → "Potret 2026: 12 bulan lengkap" BEDA (11 dari 12, menyebut 2026-08), omzet & layar Pajak ikut BEDA', d1.status === 'beda' && d1.b === 11 && d1.rincian.join() === '2026-08 tidak ada di potret' && baris(H, 'pajakLayar').status === 'beda', J([d1, baris(H, 'pajakLayar').rincian])); });
coba('S3-chip', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Kelas Contoh'; }); }, function (x) { x.merkList.forEach(function (r) { if (r.merk === 'Kelas Contoh') r.beratKarung = '50'; }); });
  var H = hasilRusak(); var c3 = baris(H, 'rakJual'), c1 = baris(H, 'bukuMerek');
  ok('S3 baris pembuka Kelas Contoh rusak bentuknya (berat karung jadi teks, kg tetap) → rak Jual BEDA: "Kelas Contoh 50 kg … tidak tampil di rak Jual"; buku per merek tetap sama',
    c3.status === 'beda' && c3.rincian.join() === 'Kelas Contoh 50 kg (buku Kelas Contoh): tidak tampil di rak Jual' && c1.status === 'sama', J([c3.rincian, c1.status])); });
coba('S3-potret-omzet', function () { siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { x.potret.bulan['2026-08'].omzet += 1000; });
  var H = hasilRusak(); var d2 = baris(H, 'pajakOmzet');
  ok('S3 omzet satu bulan di potret berubah (12 bulan tetap lengkap) → "Omzet 2026 di Laporan › Pajak = potret" BEDA, dua angkanya berselisih Rp1.000', d2.status === 'beda' && d2.b - d2.a === 1000 && baris(H, 'pajakPotret').status === 'sama', J(d2)); });
coba('S3-minus', function () { siapRitual(); terapkanKeCache([{ koleksi: 'stokBahanKemasan', data: { id: 'suntik-minus', tipe: 'saldoAwal', jenis: 'paperbag5l', jumlah: -20, hargaTotal: 0, tanggal: '2027-01-01', catatan: 'kontrol', tutupBuku: true, tahunDari: 2026, bertahap: true } }]);
  var H = hasilRusak(); var e1 = baris(H, 'minus');
  ok('S3 stok minus disuntik ke saldo pembuka (kantong −20) → "Tidak ada stok minus" BEDA dengan buku & jalannya; keadaannya satu teks', e1.status === 'beda' && e1.a === '1 buku minus' && e1.b === null && /minus 20 lembar/.test(e1.rincian[0]) && /Stok › Kantong/.test(e1.rincian[0]), J(e1)); });
coba('S3-piutang', function () { siapRitual(); ubahDok('piutangMutasi', function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.tipe === 'saldoAwal'; }, function (x) { x.nominal += 250000; });
  var H = hasilRusak(); var c0 = baris(H, 'pembuka');
  ok('S3 piutang pembuka diubah SESUDAH hasil dibekukan → "Saldo pembuka di buku = berita acara 31 Des" BEDA menyebut piutang pelanggan (Rp250.000 lebih); bon per pelanggan ikut BEDA',
    c0.status === 'beda' && c0.rincian.some(function (t) { var m = /^Piutang pelanggan: berita acara (Rp[\d.]+) → saldo pembuka di buku (Rp[\d.]+)$/.exec(t); return !!m && Number(m[2].replace(/\D/g, '')) - Number(m[1].replace(/\D/g, '')) === 250000; }) && baris(H, 'piutangNama').status === 'beda', J(c0.rincian)); });
coba('S3-piutang-awal', function () {
  // piutang pembuka berubah SEBELUM arsip habis (hasil periksa belum dibekukan) → kelompok 6 menghitung ulang dari mesin
  var w = siapKotak(); putusSemua(w); var R = susunKunci(2026, D, w, LA); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  ubahDok('piutangMutasi', function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.tipe === 'saldoAwal'; }, function (x) { x.nominal += 250000; });
  var PA = susunPeriksaArsip(2026, w, LA, true); kirim({ dokumen: PA.dokumen });
  var H = hasilRusak(); var p = baris(H, 'piutang');
  ok('S3 piutang pembuka berubah sebelum hasil dibekukan → baris "Piutang pelanggan" di kelompok 6 BEDA (dua angka, selisih Rp250.000)', p.status === 'beda' && p.b - p.a === 250000 && H.kelompok[5].baris.indexOf(p) >= 0, J(p)); });
coba('S3-sembunyi', function () { siapRitual(); var tanda = cacheMentah('batch').filter(function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.penandaBuku; })[0];
  ubahDok('batchMasuk', function (x) { return x.id === tanda.id; }, function (x) { delete x.penandaBuku; });
  var H = hasilRusak(); ok('S3 penanda tutup buku hilang → kartu TETAP tampil (tahun dibaca dari berita acara, bukan dari era yang ikut mundur)', !!H && H.tahun === 2026 && eraBuku() !== 2026, J([eraBuku(), H && H.tahun])); if (!H) return;
  var c0 = baris(H, 'pembuka'), c1 = baris(H, 'bukuMerek');
  ok('S3 penanda tutup buku hilang (saldo pembuka bertahap tidak terbaca) → saldo pembuka BEDA ("tidak terbaca"), buku per merek BEDA, Pajak 2026 tidak lagi dari potret (BEDA)', c0.status === 'beda' && c0.rincian.some(function (t) { return /catatan saldo pembuka ada tapi tidak terbaca/.test(t); }) && c1.status === 'beda' && baris(H, 'pajakLayar').status === 'beda' && baris(H, 'pajakOmzet').status === 'beda', J([c0.rincian.slice(0, 2), c1.rincian.slice(0, 2)])); });
coba('S3-setoran', function () { siapRitual(); var s = cacheMentah('pajakSetoran').filter(function (x) { return x.masaPajak === '2026-07'; })[0]; hapusDok('pajakSetoran', s.id);
  var H = hasilRusak(); var d3 = baris(H, 'pajakSetor');
  ok('S3 setoran PPh yang dipotret hilang → "Setoran PPh 2026 = potret" BEDA menyebut masa 2026-07 (jumlah & NTPN-nya)', d3.status === 'beda' && /^2026-07: potret Rp[\d.]+ → sekarang Rp0$/.test(d3.rincian[0]) && d3.rincian.some(function (t) { return /NTPN AB12CD34EF56GH78 yang tercatat saat tahun dikunci tidak ada lagi/.test(t); }), J(d3)); });
coba('S3-setoran-ntpn', function () { siapRitual(); var s = cacheMentah('pajakSetoran').filter(function (x) { return x.masaPajak === '2026-07'; })[0];
  var w = jam('2027-01-10T10:00:00+07:00'); tulis(susunSetoran({ masaPajak: '2026-07', tanggalSetor: '2027-01-10', jumlah: String(s.jumlah), ntpn: 'ZZ99ZZ99ZZ99ZZ99', catatan: 'contoh pengganti' }, w, new Date(__KINI))); hapusDok('pajakSetoran', s.id);
  var d3 = baris(hasilRusak(), 'pajakSetor');
  ok('S3 (sanggahan) setoran Juli yang dipotret DIHAPUS lalu diganti setoran lain berjumlah sama (NTPN lain) di Januari → BEDA menyebut NTPN yang hilang, walau jumlah per masa tertutup',
    d3.status === 'beda' && d3.a === d3.b && d3.rincian.join() === '2026-07: setoran NTPN AB12CD34EF56GH78 yang tercatat saat tahun dikunci tidak ada lagi', J(d3)); });
coba('S3-setoran-baru', function () { siapRitual(); var w = jam('2027-01-10T10:00:00+07:00'); tulis(susunSetoran({ masaPajak: '2026-12', tanggalSetor: '2027-01-10', jumlah: '50000', ntpn: '1234ABCD5678EFGH' }, w, new Date(__KINI)));
  var H = hasilRusak(); var d3 = baris(H, 'pajakSetor');
  ok('S3 (bukan kerusakan) setoran masa Desember dicatat 10 Jan sesudah tutup buku → setoran tetap SAMA, keterangan menyebut tambahannya', d3.status === 'sama' && /termasuk Rp50\.000 yang dicatat pada\/sesudah hari tutup buku \(5 Jan 2027\)/.test(d3.ket) && d3.b - d3.a === 50000, J(d3)); });
// ---- sanggahan: kesalahan ritual yang total rupiahnya SAMA (penjaga yang mewarisi kekuatannya) — pembanding dari catatan hidup 31 Des
coba('S3-tukar-merek', function () {
  var w = siapKotak(); var asli = pembukaBuku; var R;
  pembukaBuku = function (t, ww) { var P0 = asli(t, ww); P0.dokumen.forEach(function (x) { if (x.koleksi === 'batchMasuk') (x.data.merkList || []).forEach(function (m) { if (m.merk === 'Kelas Contoh') m.merk = 'Tanpa Harga Contoh'; else if (m.merk === 'Tanpa Harga Contoh') m.merk = 'Kelas Contoh'; }); }); return P0; };
  try { R = ritualPenuh(w); } finally { pembukaBuku = asli; }
  var H = pstPeriksa(new Date(__KINI), M_OK); var c1 = baris(H, 'bukuMerek');
  ok('S3 (sanggahan) ritual menukar nama dua merek pembuka (kg & harga per baris tetap — kunci diterima, baris perbandingan sama) → "Buku beras per merek" BEDA: Kelas Contoh 200 → 100 kg, Tanpa Harga Contoh 100 → 200 kg',
    !R.tolak && baris(H, 'beras').status === 'sama' && c1.status === 'beda' && c1.rincian.indexOf('Kelas Contoh: 31 Des 200 kg → buku 100 kg') >= 0 && c1.rincian.indexOf('Tanpa Harga Contoh: 31 Des 100 kg → buku 200 kg') >= 0 && !H.beres, J([R.tolak, c1.rincian])); });
coba('S3-tukar-orang', function () { siapRitual();
  var P = pembuka('piutang', function (x) { return x.tipe === 'saldoAwal'; }); var nA = P[0].namaPelanggan, nB = P[1].namaPelanggan;
  ubahDok('piutangMutasi', function (x) { return x.id === P[0].id; }, function (x) { x.namaPelanggan = nB; }); ubahDok('piutangMutasi', function (x) { return x.id === P[1].id; }, function (x) { x.namaPelanggan = nA; });
  var H = hasilRusak(); var o = baris(H, 'piutangNama');
  ok('S3 (sanggahan) nama pelanggan dua saldo piutang pembuka TERTUKAR (total sama) → "Bon per pelanggan" BEDA menyebut keduanya; saldo pembuka (total) tetap sama',
    P.length === 2 && P[0].nominal !== P[1].nominal && o.status === 'beda' && o.rincian.length === 2 && o.rincian.every(function (t) { return /^Pelanggan Contoh [AB]: bon 31 Des Rp[\d.]+ → saat dibuka Rp[\d.]+$/.test(t); }) && baris(H, 'pembuka').status === 'sama' && o.a === o.b, J([o.rincian, baris(H, 'pembuka').status]));
  var K = pembuka('kasbon'); ubahDok('kasbonMutasi', function (x) { return x.id === K[0].id; }, function (x) { x.namaPegawai = K[1].namaPegawai; }); ubahDok('kasbonMutasi', function (x) { return x.id === K[1].id; }, function (x) { x.namaPegawai = K[0].namaPegawai; });
  var k2 = baris(hasilRusak(), 'kasbonNama');
  ok('S3 (sanggahan) nama pegawai dua kasbon pembuka TERTUKAR → "Kasbon per orang" BEDA', K.length === 2 && k2.status === 'beda' && k2.rincian.length === 2 && /^Pekerja Contoh [AB]: kasbon 31 Des/.test(k2.rincian[0]), J(k2.rincian));
  ubahDok('utangPemasokMutasi', function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.tipe === 'saldoAwal'; }, function (x) { x.pemasok = 'PEMASOK LAIN CONTOH'; });
  var u = baris(hasilRusak(), 'utangNama');
  ok('S3 (sanggahan) bon pemasok pembuka pindah ke pemasok lain (total utang sama) → "Utang per pemasok" BEDA menyebut keduanya', u.status === 'beda' && u.rincian.some(function (t) { return /^PEMASOK CONTOH: utang 31 Des Rp[\d.]+ → saat dibuka tidak ada$/.test(t); }) && u.rincian.some(function (t) { return /^PEMASOK LAIN CONTOH: utang 31 Des tidak ada → saat dibuka Rp/.test(t); }), J(u.rincian)); });
// ---- sanggahan: BUKAN kerusakan — catatan susulan, karcis hari ritual yang telat, pembetulan sah bon lama
coba('S3-susulan', function () { var w = siapKotak(); var mo0 = 0;
  var PA = ritualSela(w, function () { terapkanKeCache([
    { koleksi: 'penjualan', data: { id: 'susul1', tanggal: '2026-12-31', jam: '20:30', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 650000, hppTotalSaatJual: 600000, trxId: 't-susul1' } },
    { koleksi: 'modalOwner', data: { id: 'susul2', tanggal: '2026-12-30', jam: '09:00', tipe: 'setor', nominal: 2000000, catatan: 'contoh: setoran modal yang telat masuk' } }]); });
  var H = pstPeriksa(new Date(__KINI), M_OK); var p = H.petunjuk.join(' | ');
  ok('S3 (sanggahan, A9) nota & setoran modal bertanggal 2026 masuk SESUDAH kunci sebelum arsip habis → hasil beku TIDAK menghitungnya (stok beras & modal sama), jumlahnya tercatat (susulan 2)',
    !!PA.dokumen && PA.dokumen[0].data.susulan === 2 && PA.PU.semuaSama && PA.PU.susulan === 2 && baris(H, 'beras').status === 'sama' && baris(H, 'modalPembuka').status === 'sama' && H.susulan === 2, J([PA.PU && PA.PU.ringkas, ringkasH(H)]));
  ok('S3 (sanggahan, A9) kartu tetap BERES; petunjuk menyebut 2 catatan susulan "bukan alasan membatalkan" & pita susulan — TIDAK menyuruh batalkan',
    H.beres && /^2 catatan masuk SESUDAH tutup buku 2026 dikunci \(2 bertanggal 2026 — catatan susulan\) — tidak ikut dibandingkan karena bukan bagian ritual\. Itu bukan alasan membatalkan\. Pita catatan susulan/.test(H.petunjuk[0]) && !/Ketuk "batalkan"/.test(p) && !!susulanBuku(2026), p);
  var S = susunSelesai(2026, 'cadangan-sesudah-contoh.json', jam('2027-01-05T11:00:00+07:00'), false, LA); var S2 = susunSelesai(2026, 'cadangan-sesudah-contoh.json', jam('2027-01-05T11:00:00+07:00'), true, LA); tulis(S2);
  var H2 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S3 (sanggahan, A9) "selesai" (pita: ketukan kedua karena susulan, BUKAN karena baris tidak sama) → kartu tetap beres, tanpa "jalan pulang darurat"', !!S.perluYakin && !/TIDAK SAMA/.test(S.tolak) && H2.beres && H2.fase === 'selesai' && !/jalan pulang darurat/.test(H2.petunjuk.join(' ')), J([S.tolak, H2.petunjuk]));
  tulis(susunCatatSusulan(2026, jam('2027-01-06T10:00:00+07:00'))); var H3 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S3 (sanggahan, A9) sesudah "sudah dicatat": beres, kalimat pita hilang, jumlah catatan sesudah kunci tetap disebut', H3.beres && !/Pita catatan susulan/.test(H3.petunjuk.join(' ')) && /^2 catatan masuk SESUDAH tutup buku 2026/.test(H3.petunjuk[0]), J(H3.petunjuk)); });
coba('S3-susulan-hari', function () { var w = siapKotak();
  var PA = ritualSela(w, function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'telat1', tanggal: '2027-01-05', jam: '08:30', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 650000, hppTotalSaatJual: 600000, trxId: 't-telat1' } }]); });
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S3 (sanggahan) karcis bertanggal HARI RITUAL 08.30 (sebelum kunci 10.00) yang baru masuk sesudah kunci → tidak ikut dibandingkan: stok beras & uang sama, beres, disebut', PA.PU.semuaSama && PA.dokumen[0].data.sesudahKunci === 1 && H.beres && H.sesudahKunci === 1
    && /^1 catatan masuk SESUDAH tutup buku 2026 dikunci \(1 bertanggal hari tutup buku, ditulis sebelum kunci tapi baru masuk sesudahnya\)/.test(H.petunjuk[0]), J([PA.PU.ringkas, H.petunjuk])); });
coba('S3-hari-sesudah', function () { var w = siapKotak();
  var PA = ritualSela(w, function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'jual11', tanggal: '2027-01-05', jam: '11:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 650000, hppTotalSaatJual: 600000, trxId: 't-jual11' } }]); });
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S3 (batas) nota ditulis SESUDAH jam kunci di hari ritual (berjualan selama arsip — dilarang daftar periksa) tetap terhitung → stok beras BEDA, tidak disebut "sesudah kunci"', !PA.PU.semuaSama && baris(H, 'beras').status === 'beda' && H.sesudahKunci === 0 && PA.dokumen[0].data.sesudahKunci === 0, J([PA.PU.ringkas, H.sesudahKunci])); });
coba('S3-betul-bon', function () { siapRitual(); tulis(susunSelesai(2026, 'cadangan-sesudah-contoh.json', jam('2027-01-05T11:00:00+07:00'), false, LA));
  var bon = pembuka('utangPemasok', function (x) { return x.tipe === 'saldoAwal'; })[0]; var n0 = Math.round(bon.nominal); var w = jam('2027-01-15T10:00:00+07:00');
  var r = susunBetulBonLama(bon.id, { tgl: bon.bonTanggal || '', ketik: String(n0 - 500000) }, 'contoh: bon kertas ternyata lebih kecil', w); tulis(r);
  var H = pstPeriksa(new Date(__KINI), M_OK); var c0 = baris(H, 'pembuka');
  ok('S3 (sanggahan) bon lama pemasok pembuka DIBETULKAN owner 15 Jan (alasan, riwayat) → saldo pembuka & utang per pemasok tetap SAMA (dibandingkan dengan nilai saat kunci), pembetulannya disebut; kartu beres',
    !r.tolak && c0.status === 'sama' && new RegExp('bon lama PEMASOK CONTOH dibetulkan owner 15 Jan 2027: ' + RP(n0).replace(/\./g, '\\.') + ' → ' + RP(n0 - 500000).replace(/\./g, '\\.')).test(c0.ket) && baris(H, 'utangNama').status === 'sama' && H.beres && H.dibetulkan.length === 1
    && dokDiCache('utangPemasokMutasi', bon.id).nominal === n0 - 500000, J([r.tolak, c0.ket, ringkasH(H)]));
  ubahDok('utangPemasokMutasi', function (x) { return x.id === bon.id; }, function (x) { delete x.riwayat; delete x.alasanKoreksi; });
  var H2 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S3 bon pemasok pembuka berubah TANPA jejak pembetulan → saldo pembuka BEDA (utang ke pemasok) & utang per pemasok BEDA', baris(H2, 'pembuka').status === 'beda' && baris(H2, 'pembuka').rincian.some(function (t) { return /^Utang ke pemasok: berita acara/.test(t); }) && baris(H2, 'utangNama').status === 'beda', ringkasH(H2)); });

// ==================== S4 · belum bisa diperiksa ('?', bukan ✓) ====================
coba('S4', function () {
  siapRitual(); var k = new Date(__KINI);
  var H1 = pstPeriksa(k, { siap: false, siapN: 30, total: 56, ditolak: [] });
  ok('S4 data belum selesai dimuat → SEMUA baris "belum bisa diperiksa" dengan sebabnya, ringkasan bukan "beres"', H1.nBelum === H1.n && !H1.beres && /^27 dari 27 pemeriksaan belum bisa diperiksa — tutup buku 2026 belum bisa dinyatakan beres/.test(H1.ringkas) && H1.kelompok.every(function (g) { return g.baris.every(function (b) { return /belum selesai dimuat di perangkat ini \(30 dari 56 bagian\)/.test(b.sebab); }); }), ringkasH(H1));
  var H2 = pstPeriksa(k, { siap: true, siapN: 56, total: 56, ditolak: ['modalOwner'] });
  ok('S4 data modal owner ditolak server → baris modal & saldo pembuka "belum" (kalimat toko, bukan nama koleksi), baris yang tidak membutuhkannya tetap diperiksa', baris(H2, 'modalPembuka').status === 'belum' && /^data modal owner ditolak server di perangkat ini/.test(baris(H2, 'modalPembuka').sebab) && baris(H2, 'pembuka').status === 'belum'
    && baris(H2, 'pajakOmzet').status === 'sama' && baris(H2, 'beras').status === 'sama' && H2.nBeda === 0, ringkasH(H2));
  var H3 = pstPeriksa(k, Object.assign({}, M_OK, { offline: true }));
  ok('S4 perangkat tanpa internet → semua "belum bisa diperiksa" (angka dari simpanan perangkat), bukan beres', H3.nBelum === H3.n && /tanpa internet — angkanya dari simpanan perangkat/.test(baris(H3, 'beras').sebab), ringkasH(H3));
  setelTertunda('tutupBukuAcara', ['2026']); var H4 = pstPeriksa(k, M_OK); setelTertunda('tutupBukuAcara', []);
  ok('S4 berita acara masih menunggu server di perangkat ini → semua "belum" (tunggu antrean kosong)', H4.nBelum === H4.n && /menunggu server/.test(baris(H4, 'beras').sebab), ringkasH(H4));
  setelTertunda('pengaturan', ['periksaArsip2026']); var H5 = pstPeriksa(k, M_OK); setelTertunda('pengaturan', []);
  ok('S4 (sanggahan) hasil beku periksa ulang masih menunggu server (bisa ditolak) → semua "belum", bukan beres', H5.nBelum === H5.n && !H5.beres && /menunggu server/.test(baris(H5, 'beras').sebab), ringkasH(H5));
  try { setelDariCache('pengaturan', true); var H6 = pstPeriksa(k, M_OK); } finally { setelDariCache('pengaturan', false); }
  ok('S4 (sanggahan) pengaturan (hasil beku) masih salinan perangkat → baris perbandingan "belum" (belum dijawab server), bukan beres', baris(H6, 'beras').status === 'belum' && /^data pengaturan toko masih dari simpanan perangkat, belum dijawab server/.test(baris(H6, 'beras').sebab) && !H6.beres, ringkasH(H6));
  try { setelDariCache('tutupBukuAcara', true); var H7 = pstPeriksa(k, M_OK); } finally { setelDariCache('tutupBukuAcara', false); }
  ok('S4 (sanggahan) berita acara masih salinan perangkat → semua "belum"', H7.nBelum === H7.n && /berita acara tutup buku masih dari simpanan perangkat/.test(baris(H7, 'pembuka').sebab), ringkasH(H7));
});
coba('S4-ditolak-pembuka', function () {
  siapRitual(); pasok('piutangMutasi', []); var H = pstPeriksa(new Date(__KINI), { siap: true, siapN: 56, total: 56, ditolak: ['piutangMutasi'] });
  ok('S4 (sanggahan) catatan bon pelanggan DITOLAK server (cache kosong, tetap "siap") → saldo pembuka & bon per pelanggan "belum bisa diperiksa", BUKAN "dokumen hilang ✗"', baris(H, 'pembuka').status === 'belum' && /^data catatan bon pelanggan ditolak server/.test(baris(H, 'pembuka').sebab)
    && baris(H, 'piutangNama').status === 'belum' && baris(H, 'kasbonNama').status === 'sama' && baris(H, 'utangNama').status === 'sama' && H.nBeda === 0 && !H.beres, ringkasH(H));
  siapRitual(); pasok('utangPemasokMutasi', []); var H2 = pstPeriksa(new Date(__KINI), { siap: true, siapN: 56, total: 56, ditolak: ['utangPemasokMutasi'] });
  ok('S4 (sanggahan) bon pemasok DITOLAK server → saldo pembuka & utang per pemasok "belum", bukan ✗', baris(H2, 'pembuka').status === 'belum' && /bon pemasok ditolak server/.test(baris(H2, 'pembuka').sebab) && baris(H2, 'utangNama').status === 'belum' && H2.nBeda === 0, ringkasH(H2)); });
coba('S4-beku-kas', function () {
  // hasil periksa DIBEKUKAN saat arsip habis + titik kas maju (tutup hari 10 Jan) → uang per tempat tetap diperiksa dari hasil beku (✓), bukan "?"
  siapRitual(); var w = jam('2027-01-10T21:00:00+07:00'); terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2027-01-10', laci: 1000000, rekening: 2000000, amplop: 0, brankas: 3000000, diubahPada: w.kini } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S4 hasil beku + titik kas sudah maju (tutup hari Januari) → uang per tempat tetap SAMA dari hasil yang dibekukan, semua beres', ['laci', 'brankas', 'rekening', 'amplop'].every(function (id) { return baris(H, id).status === 'sama'; }) && H.beres && /dibekukan saat arsip habis/.test(H.sumber), ringkasH(H)); });
coba('S4-kas', function () {
  // hasil periksa TIDAK dibekukan (dokumen periksaArsip hilang) dan titik kas sudah maju (tutup hari 10 Jan) → uang per tempat '?' (mesin tidak menghitung mundur)
  siapRitual(); hapusDok('pengaturan', 'periksaArsip2026');
  var w = jam('2027-01-10T21:00:00+07:00'); terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2027-01-10', laci: 1000000, rekening: 2000000, amplop: 0, brankas: 3000000, diubahPada: w.kini } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK); var kas = ['laci', 'brankas', 'rekening', 'amplop'].map(function (id) { return baris(H, id); });
  ok('S4 tanpa hasil yang dibekukan & titik kas sudah maju → baris uang per tempat "belum bisa diperiksa" (bukan ✓), stok tetap diperiksa, sumber "dihitung ulang sekarang"',
    kas.every(function (b) { return b.status === 'belum' && /titik kas sudah maju/.test(b.sebab); }) && baris(H, 'beras').status === 'sama' && /^dihitung ulang sekarang/.test(H.sumber) && !H.beres, ringkasH(H)); });
coba('S4-tanpa', function () {
  siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { delete x.hariIni; delete x.potret; delete x.pembukaRingkas; });
  hapusDok('pengaturan', 'periksaArsip2026');
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S4 berita acara tanpa patokan hari tutup buku → kelompok 1 & 3 baris beku kelompok 6 "belum" (tidak bisa diulang), bukan ✓', H.kelompok[0].baris.concat(H.kelompok[5].baris.slice(0, 3)).every(function (b) { return b.status === 'belum' && /tidak menyimpan patokan hari tutup buku/.test(b.sebab); }) && H.kelompok[0].baris.length === 11, ringkasH(H));
  ok('S4 tanpa potret → "12 bulan lengkap" BEDA (Laporan & Pajak hanya di arsip), omzet/setoran/layar "belum"; modal memakai angka berita acara', baris(H, 'pajakPotret').status === 'beda' && ['pajakOmzet', 'pajakSetor', 'pajakLayar'].every(function (id) { return baris(H, id).status === 'belum'; }) && baris(H, 'modalPembuka').status === 'sama' && /berita acara \(tanpa potret\)/.test(baris(H, 'modalPembuka').ket), ringkasH(H));
  ok('S4 (sanggahan) tanpa ringkasan & pembanding 31 Des → buku per merek, kemasan, rak Jual & per nama "belum bisa diperiksa" (tidak dibandingkan dengan dirinya sendiri), bukan ✓',
    ['bukuMerek', 'bukuKemasan', 'piutangNama', 'kasbonNama', 'utangNama'].every(function (id) { return baris(H, id).status === 'belum' && /tidak menyimpan pembanding dari catatan 31 Des/.test(baris(H, id).sebab); })
    && baris(H, 'rakJual').status === 'belum' && /tanda buku yang terlepas tidak bisa ketahuan/.test(baris(H, 'rakJual').sebab), J([baris(H, 'bukuMerek'), baris(H, 'rakJual').sebab])); });
coba('S4-v1', function () {
  siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { delete x.pembukaRingkas.sebelum; x.pembukaRingkas.versi = 1; });
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S4 (sanggahan) ringkasan tanpa pembanding 31 Des (versi 1) → buku per merek, kemasan & per nama "belum"; rak Jual & tanda buku tetap diperiksa (baris yang ditulis ada)',
    ['bukuMerek', 'bukuKemasan', 'piutangNama', 'kasbonNama', 'utangNama'].every(function (id) { return baris(H, id).status === 'belum'; }) && baris(H, 'rakJual').status === 'sama' && H.nBelum === 5 && H.nBeda === 0, ringkasH(H)); });

// ==================== S5 · stok minus HARI INI (catatan sesudah tutup buku) ====================
coba('S5', function () {
  siapRitual(); var w = jam('2027-01-06T10:00:00+07:00'); terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'lebih1', tanggal: '2027-01-06', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek 25 kg', totalKg: 300, beratKarungAcuan: 25, jumlahKarung: 12, hargaTotal: 3900000, hppTotalSaatJual: 3630000, trxId: 't-lebih1' } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK); var e1 = baris(H, 'minus');
  ok('S5 penjualan Januari melebihi buku (Bebek 25 kg −100 kg) → baris saldo pembuka tetap SAMA, keterangan menyebut minus hari ini & jalannya (Stok › Cocokkan)', e1.status === 'sama' && e1.a === 'tidak ada yang minus' && /CATATAN: hari ini 1 buku minus karena catatan sesudah tutup buku \(Buku Bebek 25 kg minus 100 kg\)/.test(e1.ket) && /Stok › Cocokkan/.test(e1.ket) && H.beres, J(e1));
});

// ==================== S7 · HEMAT BACA NYALA (#111 × Paket C): koleksi yang belum lengkap → "?" dengan sebab, bukan ✓ ====================
/** Peta kelengkapan seperti hbSesi.belumLengkap(): koleksi → "belum dibaca penuh sejak kuota baca direset" (hari kuota 5 Jan 2027 — reset 15.00 WIB). */
var SH7 = hbSebabHarian('2027-01-05');
function hbHarian(daftar) { var o = {}; daftar.forEach(function (k) { o[k] = { jenis: 'harian', sebab: SH7 }; }); return o; }
var BAHASA_MESIN_S7 = /koleksi|dokumen|chip|JSON|cache|mesin|piutangMutasi|utangPemasokMutasi|modalOwner|batchMasuk|tutupBukuAcara|pengaturan\/|capServer|delta|nisan/;
coba('S7', function () {
  siapRitual(); var k = new Date(__KINI); var mati = pstPeriksa(k, M_OK);
  var lengkap = pstPeriksa(k, Object.assign({}, M_OK, { hemat: {} }));
  ok('S7 nyala & SEMUA lengkap (peta kelengkapan kosong) → hasil SAMA PERSIS dengan saklar mati (27 sama, beres)', mati && mati.beres && J(lengkap) === J(mati), ringkasH(lengkap));
  var H1 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: hbHarian(['penjualan', 'modalOwner']) }));
  ok('S7 nyala: modal owner belum dibaca penuh sejak reset → baris modal "?" dengan sebab toko persis ("data modal owner belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk \"baca penuh sekarang\" (Menu › Sistem › Perangkat › Hemat baca)"), bukan ✓; baris yang tidak membutuhkannya (perbandingan beku, pajak dari potret) tetap ✓',
    baris(H1, 'modalPembuka').status === 'belum' && baris(H1, 'modalPembuka').sebab === 'data modal owner belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang" (Menu › Sistem › Perangkat › Hemat baca)'
    && baris(H1, 'pajakSetor').status === 'sama' && H1.kelompok[0].baris.every(function (b) { return b.status === 'sama'; }) && !H1.beres && H1.nBeda === 0, ringkasH(H1));
  var H2 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: hbHarian(hbKoleksiHemat()) }));
  var q2 = H2.kelompok.reduce(function (o, g) { return o.concat(g.baris.filter(function (b) { return b.status === 'belum'; })); }, []);
  ok('S7 nyala: SEMUA catatan toko belum dibaca penuh sejak reset → 13 dari 27 "?" (yang membaca buku hidup), 14 baris beku tetap ✓ (berita acara & hasil beku = setelan yang selalu didengar penuh); ringkasan "belum bisa diperiksa", bukan beres',
    H2.nBelum === 13 && H2.nBeda === 0 && !H2.beres && /^13 dari 27 pemeriksaan belum bisa diperiksa — tutup buku 2026 belum bisa dinyatakan beres/.test(H2.ringkas)
    && q2.every(function (b) { return /^data .+ belum dibaca penuh sejak kuota baca direset pukul 15\.00 WIB — ketuk "baca penuh sekarang" \(Menu › Sistem › Perangkat › Hemat baca\)$/.test(b.sebab) && !BAHASA_MESIN_S7.test(b.sebab) && !/jenis catatan lainnya/.test(b.sebab); }), ringkasH(H2));
  var H3 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: { batchMasuk: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' }, penjualan: { jenis: 'harian', sebab: SH7 } } }));
  ok('S7 nyala: sebab dari sumbernya diteruskan apa adanya — barang masuk "sedang dibaca penuh" → baris stok "data barang masuk sedang dibaca penuh — tunggu sampai selesai"',
    baris(H3, 'bukuMerek').status === 'belum' && baris(H3, 'bukuMerek').sebab === 'data barang masuk sedang dibaca penuh — tunggu sampai selesai' && baris(H3, 'modalPembuka').status === 'sama', ringkasH(H3));
  var H4 = pstPeriksa(k, Object.assign({}, M_OK, { offline: true, hemat: hbHarian(['modalOwner']) }));
  try { setelDariCache('modalOwner', true); var H5 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: hbHarian(['modalOwner']) })); var H5b = pstPeriksa(k, M_OK); } finally { setelDariCache('modalOwner', false); }
  ok('S7 urutan sebab: tanpa internet menang atas hemat; sebab hemat menang atas "masih dari simpanan perangkat" (koleksi hemat yang belum terperiksa ditandai salinan perangkat oleh firebase.js); mati tetap kalimat lama',
    /tanpa internet/.test(baris(H4, 'modalPembuka').sebab) && baris(H5, 'modalPembuka').sebab === 'data modal owner ' + SH7 && /masih dari simpanan perangkat, belum dijawab server/.test(baris(H5b, 'modalPembuka').sebab),
    J([baris(H4, 'modalPembuka').sebab, baris(H5, 'modalPembuka').sebab, baris(H5b, 'modalPembuka').sebab]));
  hapusDok('pengaturan', 'periksaArsip2026');
  var H6 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: hbHarian(['penjualan']) })); var H6m = pstPeriksa(k, M_OK);
  ok('S7 hasil beku tidak ada di perangkat ini (baris perbandingan dihitung ulang dari SELURUH buku) + penjualan belum dibaca penuh sejak reset → 11 baris perbandingan "?" — mati: dihitung ulang',
    H6.kelompok[0].baris.every(function (b) { return b.status === 'belum' && /^data penjualan belum dibaca penuh sejak kuota baca direset/.test(b.sebab); }) && H6m.kelompok[0].baris.some(function (b) { return b.status === 'sama'; }), ringkasH(H6));
  // sanggahan 8 Okt (d): sebab SATU jenis catatan dulu dipinjamkan ke semua ("data penjualan, retur, modal owner sedang dibaca penuh — tunggu") — owner menunggu,
  // padahal retur & modal owner butuh ketukan "baca penuh sekarang"
  var H7 = pstPeriksa(k, Object.assign({}, M_OK, { hemat: { penjualan: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' }, retur: { jenis: 'harian', sebab: SH7 }, modalOwner: { jenis: 'harian', sebab: SH7 } } }));
  var s7 = (H7.kelompok[0].baris[0] || {}).sebab || '';
  ok('S7 (sanggahan 8 Okt) sebab tidak dipinjamkan: penjualan "sedang dibaca penuh" disebut namanya; retur & modal owner dihitung dengan sebabnya sendiri ("2 jenis catatan lainnya belum dibaca penuh sejak … — ketuk")',
    s7 === 'data penjualan sedang dibaca penuh — tunggu sampai selesai; 2 jenis catatan lainnya ' + SH7 && !BAHASA_MESIN_S7.test(s7) && H7.kelompok[0].baris.every(function (b) { return b.status === 'belum' && b.sebab === s7; }), s7);
});
// ---- S7b · keputusan final LAIN dari sumber yang sama (logika): kunci bulan, Lanjutkan/Batalkan tutup buku, gerbang g7
coba('S7b', function () {
  siapRitual(); var k = new Date(__KINI); var K0 = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} };
  var D0 = kpDaftarPeriksa('2026-12', k, K0), Dl = kpDaftarPeriksa('2026-12', k, Object.assign({}, K0, { hemat: {} })), Db = kpDaftarPeriksa('2026-12', k, Object.assign({}, K0, { hemat: hbHarian(['penjualan', 'kasbonMutasi']) }));
  var bh = Db.butir.find(function (b) { return b.id === 'hemat'; }), bl = Dl.butir.find(function (b) { return b.id === 'hemat'; });
  ok('S7b kunci bulan: saklar mati = tanpa butir hemat (daftar sama); nyala & lengkap = ⛔ butir hemat ✓; nyala & belum dibaca penuh sejak reset = ⛔ butir hemat MEMBLOKIR dengan sebab toko, jumlah jenis catatan SEBELUM petunjuk (tanpa kurung ganda)',
    !D0.butir.some(function (b) { return b.id === 'hemat'; }) && bl && bl.ok && bl.blokir && bh && !bh.ok && bh.blokir && bh.ket === 'data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB (2 jenis catatan) — ketuk "baca penuh sekarang" (Menu › Sistem › Perangkat › Hemat baca)' && Db.blokir === D0.blokir + 1 && !Db.boleh
    && J(D0.butir) === J(Dl.butir.filter(function (b) { return b.id !== 'hemat'; })), J([bh, bl, D0.blokir, Db.blokir]));
  ok('S7b Lanjutkan / Batalkan tutup buku: mati = boleh (seperti dulu); nyala & lengkap = boleh; nyala & belum lengkap = DITOLAK dengan sebab ("data perangkat ini sedang dibaca penuh …"); tanpa internet tetap kalimat lama',
    bkSambungan({}) === '' && bkSambungan({ hemat: { nyala: false } }) === '' && bkSambungan({ hemat: { nyala: true, belumLengkap: {} } }) === ''
    && bkSambungan({ hemat: { nyala: true, belumLengkap: { penjualan: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' } } } }) === 'Tutup buku: data perangkat ini sedang dibaca penuh — tunggu sampai selesai — Lanjutkan atau Batalkan sesudah datanya lengkap.'
    && /tanpa internet/.test(bkSambungan({ offline: true, hemat: { nyala: true, belumLengkap: hbHarian(['penjualan']) } })), bkSambungan({ hemat: { nyala: true, belumLengkap: { penjualan: { jenis: 'periksa', sebab: 'x' } } } }));
  var G0 = gerbangBuku(2027, k, { antre: [] }), G1 = gerbangBuku(2027, k, { antre: [], hemat: { nyala: true, totalSesiIni: true, belumLengkap: {} } });
  var G2 = gerbangBuku(2027, k, { antre: [], hemat: { nyala: true, totalSesiIni: true, belumLengkap: { pengeluaranHarian: { jenis: 'periksa', sebab: 'belum dicocokkan dengan catatan yang dihapus di server — tunggu sebentar' } } } });
  var G3 = gerbangBuku(2027, k, { antre: [], hemat: { nyala: true, totalSesiIni: false, belumLengkap: {} } }); var g7 = function (G) { return G.daftar.find(function (x) { return x.id === 'g7'; }); };
  ok('S7b gerbang tutup buku g7: mati = tidak ada; nyala, dibaca penuh sesi ini & lengkap = ✓; dibaca penuh sesi ini tapi batu nisan belum dicocokkan (SATU sumber) = belum, sebabnya disebut; belum dibaca penuh sesi ini = belum',
    !g7(G0) && g7(G1) && g7(G1).ok && g7(G2) && !g7(G2).ok && g7(G2).ket === 'data perangkat ini belum dicocokkan dengan catatan yang dihapus di server — tunggu sebentar' && !G2.semuaOk && g7(G3) && !g7(G3).ok && /belum dibaca penuh sesi ini/.test(g7(G3).ket),
    J([g7(G1), g7(G2), g7(G3)]));
  var SH0 = ssHemat({ nyala: false, saklar: false, owner: true }, []), SH1 = ssHemat({ nyala: true, saklar: true, owner: true, belumLengkap: hbHarian(['penjualan', 'retur']) }, []), SH2 = ssHemat({ nyala: true, saklar: true, owner: true, belumLengkap: { penjualan: { jenis: 'periksa', sebab: 'x' } } }, []);
  var JS = 'belum bisa dipastikan sudah dibaca penuh sejak kuota baca terakhir direset (jam server belum diterima) — tunggu sebentar';
  var SH3 = ssHemat({ nyala: true, saklar: true, owner: true, belumLengkap: { penjualan: { jenis: 'harian', sebab: JS }, retur: { jenis: 'harian', sebab: JS }, kasbonMutasi: { jenis: 'harian', sebab: SH7 } } }, []);
  var SH4 = ssHemat({ nyala: true, saklar: true, owner: true, klaim: { hari: '2027-01-05', nama: 'iPad contoh', selesai: 1, temuanTunda: { penjualan: 2 } } }, []);
  ok('S7b panel Menu › Sistem › Perangkat › Hemat baca (tempat tombol "baca penuh sekarang"): nyala & 2 jenis catatan belum dibaca penuh sejak reset → kalimat per sebab ("jenis catatan", bukan "koleksi"; petunjuk menu dibuang — panelnya ini) + keputusan yang menunggu; mati / hanya belum terperiksa → kosong',
    SH0.harianBelum === '' && SH1.harianBelum === '2 jenis catatan belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang". Kartu pemeriksaan sesudah tutup buku, kunci bulan, Laporan › Pajak & dokumen Laporan menunggu sampai lengkap.' && SH2.harianBelum === '', J([SH0.harianBelum, SH1.harianBelum]));
  ok('S7b panel (sanggahan 8 Okt): "jam server belum diterima" TIDAK dihitung sebagai "belum dibaca penuh" (dihitung per sebab); baca penuh harian toko dengan ubahan yang tidak bisa sampai ke perangkat lain disebut',
    SH3.harianBelum === '2 jenis catatan ' + JS + '; 1 jenis catatan belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang". Kartu pemeriksaan sesudah tutup buku, kunci bulan, Laporan › Pajak & dokumen Laporan menunggu sampai lengkap.'
    && /selesai oleh iPad contoh · 2 ubahan tanpa cap belum bisa sampai ke perangkat lain/.test(SH4.harian), J([SH3.harianBelum, SH4.harian]));
});
// ---- S7c · (sanggahan 8 Okt) PINTU tutup buku: susunKunci memeriksa kelengkapan hemat (g7) lagi — sesudah unduh cadangan, arsip, saldo & paraf berdua,
//      potret & saldo pembuka disusun dari seluruh buku perangkat ini. Dulu g7 hanya di layar langkah 1 (uang.js bkPeriksa)
coba('S7c', function () {
  var w = siapKotak(); putusSemua(w);
  var Lb = Object.assign({}, LA, { hemat: { nyala: true, totalSesiIni: true, belumLengkap: hbHarian(['penjualan']) } }), Ll = Object.assign({}, LA, { hemat: { nyala: true, totalSesiIni: true, belumLengkap: {} } });
  var Rb = susunKunci(2026, D, w, Lb), R0 = susunKunci(2026, D, w, LA), Rl = susunKunci(2026, D, w, Ll), Rs = susunKunci(2026, D, w, Object.assign({}, LA, { hemat: { nyala: true, totalSesiIni: false, belumLengkap: {} } }));
  ok('S7c susunKunci (pintu masuk) dengan hemat nyala & penjualan belum dibaca penuh sejak reset → DITOLAK dengan butir g7 & sebab toko; belum dibaca penuh sesi ini → ditolak; saklar mati / nyala & lengkap → kiriman disusun (sama dengan dulu)',
    !!Rb.tolak && /^Periksa dulu belum beres — Perangkat ini sudah membaca penuh semua catatan sesi ini \(hemat baca\): data perangkat ini belum dibaca penuh sejak kuota baca direset/.test(Rb.tolak) && !Rb.kiriman
    && !!Rs.tolak && /belum dibaca penuh sesi ini/.test(Rs.tolak) && !R0.tolak && !!R0.kiriman && R0.kiriman.length > 0 && !Rl.tolak && !!Rl.kiriman && J(Rl.kiriman.length) === J(R0.kiriman.length),
    J([Rb.tolak, Rs.tolak, R0.tolak, Rl.tolak]));
});
"""


# ---- S6 · layar Uang › Tutup buku ASLI digambar di jsc (uang.js + modul impornya; peramban tidak dinyalakan) ----
MODUL_LAYAR = MODUL + ['baru/js/inti/dom.js', 'baru/js/inti/kunci.js', 'baru/js/inti/keadaan.js', 'baru/js/inti/isian.js', 'baru/js/inti/jadwal.js', 'baru/js/inti/gerak.js',
                       'baru/js/layar/akses-layar.js', 'baru/js/layar/uang.js']
LAYAR = r"""
var __html = ''; pasang = function (akar, isi) { __html = isi && isi.__mentah ? isi.html : String(isi); }; delegasi = function () {}; gulirkan = function () {}; nanti = function () {}; segera = function () {};
setelKunci(false); var __lebar = 1100; window.matchMedia = function (q) { var m = /min-width: (\d+)px/.exec(q); return { matches: !!m && __lebar >= Number(m[1]) }; }; window.addEventListener = function () {};
if (typeof setTimeout === 'undefined') { var setTimeout = function () { return 0; }; var clearTimeout = function () {}; }
var NS = new Proxy({}, { get: function (o, k) { return (0, eval)(String(k)); } }); var UG = NS, UP = NS, OT = NS, TD = NS, BK = NS, KP = NS, PST = NS, WB = NS;
// ekspor berganti nama (`export { a as b }` dibuang bundel) — nama yang dipakai uang.js lewat ruang nama
var kpNama = kpNamaBulan, kpWaktu = kpWib, PILIHAN_POTONG = UP_POTONG, bkRP = RP, tdAngka = ANGKA;
var akarU = { classList: { add: function () {}, remove: function () {} }, firstElementChild: null, offsetWidth: 0 };
var __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: false };
var U = null; var gambarU = function (patch) { U.keadaan.setel(patch || {}); U.gambar(); return __html; };
// hemat baca (#111): null = lokal() TANPA kolom hemat (persis uji S6 lama); objek = app.js lokalPerangkat `hemat` (fb.hematKeadaan())
var __hemat = null;
function lokalU() { var o = { antre: [], menunggu: 0, idPerangkat: 'mac-contoh', namaPerangkat: 'Mac contoh', offline: !!__muat.offline, koleksiSiap: __muat.koleksiSiap, koleksiTotal: __muat.koleksiTotal, ditolak: __muat.ditolak, antreLokal: { belum: [], ditolak: [] }, parkir: [] };
  if (__hemat !== null) o.hemat = __hemat; return o; }
function buatU() { return pasangLayarUang(akarU, { akun: function () { return { jenis: 'owner' }; }, gantiMode: function () {}, mode: function () { return 'terang'; }, sekarang: function () { return new Date(__KINI); }, statusRingkas: function () { return 'owner'; }, pindah: function () {},
    lokal: lokalU, bukaStok: function () {} }); }
/** Potongan HTML kartu pemeriksaan / kartu perkiraan kuota (untuk "sama persis"). */
function potong(t, awal, akhir) { var i = t.indexOf(awal); if (i < 0) return ''; var j = t.indexOf(akhir, i); return t.slice(i, j < 0 ? t.length : j); }
function rusakHtml(t) { return /NaN|undefined|\[object Object\]/.test(t.replace(/data-[a-z-]+="[^"]*"/g, '')); }
/** Teks kartu pemeriksaan yang TERBACA owner (tanpa tag & atribut). */
function teksKartu(t) { var m = /data-k="tb-periksa"[\s\S]*?data-aksi="pstUnduh">[^<]*</.exec(t); return m ? m[0].replace(/<[^>]*>/g, ' ').replace(/data-[a-z-]+="[^"]*"/g, '') : ''; }
var BAHASA_MESIN = /koleksi|dokumen|chip|JSON|cache|mesin|piutangMutasi|utangPemasokMutasi|modalOwner|batchMasuk|tutupBukuAcara|pengaturan\//;
coba('S6', function () {
  siapRitual(); setelSumber('firestore', 'kotak pasir');
  U = buatU();
  U.tampilkan(true);
  var mac = gambarU({ keluarga: 'buku' }); __lebar = 400; var hp = gambarU({ keluarga: 'buku' }); __lebar = 800; var tab = gambarU({ keluarga: 'buku' }); __lebar = 1100;
  ok('S6 uang.js ASLI (Mac, tablet, HP): kartu "Pemeriksaan sesudah tutup buku 2026" digambar di Tutup buku dengan ringkasan "Semua 27 pemeriksaan sama", tombol unduh berkas & lihat semua; tanpa NaN/undefined',
    [mac, hp, tab].every(function (t) { return /data-k="tb-periksa"/.test(t) && /Pemeriksaan sesudah tutup buku 2026/.test(t) && /data-k="pst-ringkas">Semua 27 pemeriksaan sama — tutup buku 2026 beres</.test(t) && /data-aksi="pstUnduh">unduh hasil pemeriksaan \(berkas\)</.test(t) && /lihat semua 27 baris/.test(t) && !rusakHtml(t); }),
    J([mac.length, (mac.match(/data-k="pst-ringkas">[^<]*/) || [''])[0], rusakHtml(mac) ? (mac.replace(/data-[a-z-]+="[^"]*"/g, '').match(/.{60}(NaN|undefined|\[object Object\]).{40}/) || [''])[0] : '']));
  ok('S6 bawaan: baris yang SAMA disembunyikan (6 judul kelompok "semua … sama"); "lihat semua" menggambar 27 baris bertanda ✓', (mac.match(/class="tb-cek [a-z]+" data-k="pst-/g) || []).length === 0 && (mac.match(/data-k="pstk-/g) || []).length === 6
    && (gambarU({ pstRinci: true }).match(/class="tb-cek ok" data-k="pst-/g) || []).length === 27, J((gambarU({ pstRinci: true }).match(/data-k="pst-[a-zA-Z]+"/g) || []).length));
  ubahDok('modalOwner', function (x) { return x.tutupBuku && x.tahunDari === 2026; }, function (x) { x.nominal += 1000000; });
  ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Bebek 25 kg'; }); }, function (x) { x.merkList.forEach(function (r) { if (r.merk === 'Bebek 25 kg') delete r.indukUkuran; }); });
  var rusak = gambarU({ pstRinci: false }); var nRak = (rusak.match(/data-k="pst-rakJual">[\s\S]*?<div class="pst-n">([^<]*)<\/div>/) || ['', ''])[1];
  ok('S6 ada yang beda: kartu bertanda awas, baris modal digambar ✗ dengan DUA angka (sebelum → sesudah) & petunjuk jalannya; baris yang sama tetap tersembunyi',
    /class="kartu awas" data-k="tb-periksa"/.test(rusak) && /class="tb-cek tidak" data-k="pst-modalPembuka"><span class="t">✗<\/span>/.test(rusak) && /data-k="pst-modalPembuka">[\s\S]*?Rp[\d.]+ → Rp[\d.]+/.test(rusak) && /data-k="pst-petunjuk-0">Modal owner di buku 2027/.test(rusak) && /\d pemeriksaan beda — jangan jualan\/menagih dulu/.test(rusak), (rusak.match(/data-k="pst-modalPembuka">.{0,400}/) || [''])[0]);
  ok('S6 (sanggahan, tiga keadaan) baris bersatuan teks (rak Jual) yang beda digambar ✗ dengan SATU keadaan sekarang — tanpa panah, sisi kanan tidak kosong', /class="tb-cek tidak" data-k="pst-rakJual"/.test(rusak) && /^\d+ karung di rak · \d+ tanda buku · 1 tidak cocok$/.test(nRak) && nRak.indexOf('→') < 0, nRak);
  ok('S6 (sanggahan) kalimat kartu tanpa bahasa mesin (nama koleksi, "dokumen", "chip", "JSON", "mesin") — keadaan beda', !BAHASA_MESIN.test(teksKartu(gambarU({ pstRinci: true }))), (teksKartu(gambarU({ pstRinci: true })).match(/.{50}(koleksi|dokumen|chip|JSON|cache|mesin).{30}/) || [''])[0]);
  __muat = { koleksiSiap: 20, koleksiTotal: 56, ditolak: [] }; var belum = gambarU({ pstRinci: false }); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [] };
  ok('S6 data belum selesai dimuat: baris digambar "?" (kelas belum) dengan sebabnya — bukan ✓, bukan ✗; baris teks "—"', (belum.match(/class="tb-cek belum" data-k="pst-[a-zA-Z]+"><span class="t">\?<\/span>/g) || []).length === 27 && /belum bisa diperiksa — data toko belum selesai dimuat di perangkat ini \(20 dari 56 bagian\)/.test(belum) && !/class="tb-cek ok" data-k="pst-/.test(belum)
    && /data-k="pst-rakJual">[\s\S]*?<div class="pst-n">—<\/div>/.test(belum), J((belum.match(/class="tb-cek [a-z]+" data-k="pst-[a-zA-Z]+"/g) || []).length));
  __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: ['modalOwner', 'piutangMutasi'] }; var tolak = gambarU({ pstRinci: false }); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [] };
  ok('S6 (sanggahan) data ditolak server: sebabnya kalimat toko ("data modal owner, catatan bon pelanggan ditolak server"), tanpa nama koleksi', /data modal owner, catatan bon pelanggan ditolak server di perangkat ini/.test(tolak) && !BAHASA_MESIN.test(teksKartu(tolak)), (teksKartu(tolak).match(/.{40}(koleksi|dokumen|chip|JSON|mesin).{30}/) || [''])[0]);
  __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: true }; var luring = gambarU({ pstRinci: false }); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: false };
  ok('S6 (sanggahan) lokal() menyebut perangkat tanpa internet → semua baris "?" (angka dari simpanan perangkat), bukan beres', /data-k="pst-ringkas">27 dari 27 pemeriksaan belum bisa diperiksa/.test(luring) && /tanpa internet — angkanya dari simpanan perangkat/.test(luring), (luring.match(/data-k="pst-ringkas">[^<]*/) || [''])[0]);
  setelSumber('belum', ''); var tanpa = gambarU({}); setelSumber('cadangan', 'kotak pasir'); var cad = gambarU({});
  ok('S6 belum tersambung ke data toko: semua "belum bisa diperiksa"; membaca berkas cadangan = data lengkap (diperiksa)', /data-k="pst-ringkas">27 dari 27 pemeriksaan belum bisa diperiksa/.test(tanpa) && /data-k="pst-ringkas">\d pemeriksaan beda/.test(cad), (cad.match(/data-k="pst-ringkas">[^<]*/) || [''])[0]);
  // console.error dibungkam sebentar (keluaran jsc = satu baris JSON); yang diuji: pesan mentah TIDAK sampai ke layar
  var asliP = pstPeriksa, asliE = console.error, keConsole = ''; pstPeriksa = function () { throw new Error('contoh galat XQZ di dalam'); }; console.error = function (a, e) { keConsole += String(a) + ' ' + String(e && e.message); };
  var galat; try { galat = gambarU({}); } finally { pstPeriksa = asliP; console.error = asliE; }
  ok('S6 (sanggahan) pemeriksaan jatuh: layar Tutup buku tetap tergambar, kartu berkalimat toko — pesan galat mentah TIDAK di layar (hanya console)', /data-k="tb-periksa"/.test(galat) && /Pemeriksaan tidak bisa dijalankan di perangkat ini — tutup buku belum bisa dinyatakan beres/.test(galat) && !/XQZ/.test(galat) && /XQZ/.test(keConsole), (galat.match(/data-k="tb-periksa".{0,300}/) || [''])[0]);
});
// ---- S7 · layar Uang ASLI dengan hemat baca (app.js lokalPerangkat `hemat` → muatData → pstKurang; kuota; g7; kunci bulan)
function hbHarianL(daftar) { var o = {}; daftar.forEach(function (k) { o[k] = { jenis: 'harian', sebab: hbSebabHarian('2027-01-05') }; }); return o; }
coba('S7-layar', function () {
  siapRitual(); setelSumber('firestore', 'kotak pasir'); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: false }; __lebar = 1100;
  U = buatU(); U.tampilkan(true);
  __hemat = null; var h0 = gambarU({ keluarga: 'buku', pstRinci: true });
  __hemat = { nyala: false, saklar: false, owner: true }; var h1 = gambarU({ keluarga: 'buku', pstRinci: true });
  ok('S7 layar: saklar MATI (lokal membawa hemat { nyala: false }) → HTML Uang › Tutup buku SAMA PERSIS dengan tanpa kolom hemat (kartu 27 ✓, kuota berangka, tanpa g7)',
    h0 === h1 && /data-k="pst-ringkas">Semua 27 pemeriksaan sama/.test(h0) && /Perkiraan kuota Firestore \(batas Spark/.test(h0) && !/data-k="g-g7"/.test(h0), J([h0.length, h1.length]));
  __hemat = { nyala: true, totalSesiIni: true, belumLengkap: {} }; var h2 = gambarU({ keluarga: 'buku', pstRinci: true });
  ok('S7 layar: nyala & SEMUA lengkap → kartu pemeriksaan & perkiraan kuota SAMA PERSIS dengan mati; g7 ✓',
    potong(h2, 'data-k="tb-periksa"', 'data-aksi="pstUnduh"') === potong(h0, 'data-k="tb-periksa"', 'data-aksi="pstUnduh"') && potong(h2, 'data-k="tb-kuota"', 'data-aksi="bkPeriksa"') === potong(h0, 'data-k="tb-kuota"', 'data-aksi="bkPeriksa"')
    && /class="tb-cek ok" data-k="g-g7"/.test(h2), J([potong(h2, 'data-k="tb-periksa"', 'data-aksi="pstUnduh"').length, potong(h0, 'data-k="tb-periksa"', 'data-aksi="pstUnduh"').length]));
  __hemat = { nyala: true, totalSesiIni: true, belumLengkap: hbHarianL(hbKoleksiHemat()) }; var h3 = gambarU({ keluarga: 'buku', pstRinci: true });
  var nQ = (h3.match(/class="tb-cek belum" data-k="pst-[a-zA-Z]+"><span class="t">\?<\/span>/g) || []).length; var kartu3 = teksKartu(h3);
  ok('S7 layar: nyala & belum dibaca penuh sejak reset → 13 baris digambar "?" dengan sebab toko ("… belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang" (Menu › Sistem › Perangkat › Hemat baca)"), ringkasan "belum bisa diperiksa", tanpa bahasa mesin',
    nQ === 13 && /data-k="pst-ringkas">13 dari 27 pemeriksaan belum bisa diperiksa/.test(h3) && /belum bisa diperiksa — data [^<]+ belum dibaca penuh sejak kuota baca direset pukul 15\.00 WIB — ketuk (&quot;|")baca penuh sekarang(&quot;|") \(Menu › Sistem › Perangkat › Hemat baca\)/.test(h3) && !BAHASA_MESIN.test(kartu3) && !rusakHtml(h3),
    J([nQ, (h3.match(/data-k="pst-ringkas">[^<]*/) || [''])[0], (kartu3.match(/.{40}(koleksi|dokumen|chip|JSON|cache|mesin).{30}/) || [''])[0]]));
  ok('S7 layar: perkiraan kuota tutup buku "?" — belum bisa dihitung dari data setengah (tanpa angka baca/tulis), sebabnya disebut; g7 belum (sebab dari sumber yang sama)',
    /data-k="tb-kuota-hemat"><span class="t">\?<\/span>/.test(h3) && /Perkiraan kuota tutup buku 2027 belum bisa dihitung/.test(h3) && !/Perkiraan kuota Firestore \(batas Spark/.test(h3) && /class="tb-cek tidak" data-k="g-g7"/.test(h3)
    && /data-k="g-g7">[\s\S]*?data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15\.00 WIB \(\d+ jenis catatan\) — ketuk/.test(h3), (h3.match(/data-k="tb-kuota[\s\S]{0,400}/) || [''])[0]);
  var kp3 = /data-k="kp-butir"/.test(h3), kp0 = /data-k="kp-butir"/.test(h0);
  ok('S7 layar: kartu kunci bulan (Desember 2026 bisa dicalonkan) — ⛔ butir hemat muncul HANYA saat nyala & memblokir; mati: tidak ada', kp0 && kp3 && !/data-k="kp-hemat"/.test(h0) && /class="tb-cek tidak" data-k="kp-hemat"/.test(h3), J([kp0, kp3]));
  __hemat = null;
});
"""


# ---- S7 · Laporan › Pajak ASLI (laporan.js) dengan hemat baca: pita "?", rekap konsultan / catat setoran / omzet tahun lalu dari sistem DITAHAN; mati = HTML sama ----
MODUL_PAJAK = MODUL + ['baru/js/inti/dom.js', 'baru/js/inti/kunci.js', 'baru/js/inti/keadaan.js', 'baru/js/inti/isian.js', 'baru/js/inti/jadwal.js', 'baru/js/inti/gerak.js', 'baru/js/layar/laporan.js']
LAYAR_PAJAK = r"""
var __html = ''; pasang = function (akar, isi) { __html = isi && isi.__mentah ? isi.html : String(isi); }; var __aksi = null; delegasi = function (akar, a) { __aksi = a; }; gulirkan = function () {}; nanti = function () {}; segera = function () {};
setelKunci(false); window.matchMedia = function (q) { return { matches: /1100px/.test(q) }; }; window.addEventListener = function () {}; if (typeof setTimeout === 'undefined') { var setTimeout = function () { return 0; }; var clearTimeout = function () {}; }
var LP = new Proxy({}, { get: function (o, k) { return (0, eval)(String(k)); } }); var PJ = LP; var KB = LP;
var akarL = { classList: { add: function () {}, remove: function () {} }, firstElementChild: null, offsetWidth: 0 };
var __hematL = null; var L9 = null; var gambarL = function (patch) { L9.keadaan.setel(patch || {}); L9.gambar(); return __html; };
function hbHarianP(daftar) { var o = {}; daftar.forEach(function (k) { o[k] = { jenis: 'harian', sebab: hbSebabHarian('2027-01-05') }; }); return o; }
function bukaL(denganHemat) { var o = { sekarang: function () { return new Date(__KINI); }, statusRingkas: function () { return 'owner'; }, mode: function () { return 'terang'; }, gantiMode: function () {}, pindah: function () {}, keTujuan: function () {} };
  if (denganHemat) o.hemat = function () { return __hematL; }; return pasangLayarLaporan(akarL, o); }
coba('S7-pajak', function () {
  siapRitual(); setelSumber('firestore', 'kotak pasir');
  L9 = bukaL(false); L9.tampilkan(true); var P = { keluarga: 'pajak', tahunPj: 2027, drafSetor: null, drafLuar: null, drafPj: null, kabar: '' };
  var p0 = gambarL(P); L9 = bukaL(true); L9.tampilkan(true); __hematL = { nyala: false }; var p1 = gambarL(P); __hematL = { nyala: true, belumLengkap: {} }; var p2 = gambarL(P);
  __hematL = { nyala: true, belumLengkap: hbHarianP(['kasbonMutasi', 'batchMasuk']) }; var p2b = gambarL(P);
  ok('S7 Pajak: saklar mati / app.js tanpa hemat / nyala & lengkap / yang belum lengkap bukan data pajak (kasbon, barang masuk) → HTML Laporan › Pajak SAMA PERSIS, tanpa pita "?"',
    p0.length > 1000 && p0 === p1 && p1 === p2 && p2 === p2b && !/data-k="pj-hemat"/.test(p0), J([p0.length, p1.length, p2.length, p2b.length]));
  __hematL = { nyala: true, belumLengkap: hbHarianP(['penjualan']) }; var p3 = gambarL(P);
  ok('S7 Pajak: penjualan belum dibaca penuh sejak reset → pita "?" di atas layar: angka pajak belum bisa dipastikan + sebab toko (ketuk baca penuh sekarang), tanpa "di perangkat ini … perangkat ini"; rekap konsultan ditahan',
    /data-k="pj-hemat"><b>\?<\/b> Angka pajak belum bisa dipastikan — data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15\.00 WIB — ketuk (&quot;|")baca penuh sekarang/.test(p3) && !/di perangkat ini belum bisa dipastikan/.test(p3) && /Rekap untuk konsultan &amp; catat setoran ditahan sampai lengkap|Rekap untuk konsultan & catat setoran ditahan sampai lengkap/.test(p3)
    && !/NaN|undefined|\[object Object\]/.test(p3.replace(/data-[a-z-]+="[^"]*"/g, '')), (p3.match(/data-k="pj-hemat"[^]{0,300}/) || [''])[0]);
  var nS = cacheMentah('pajakSetoran').length; var nA = cacheMentah('aturan').length;
  L9.keadaan.setel({ drafSetor: { masaPajak: '2027-01', tanggalSetor: '2027-01-05', jumlah: '1000', ntpn: '', atasNama: 'Contoh', catatan: 'setoran contoh uji' }, kabar: '' });
  __aksi.pjSetorSimpan(); drainMicrotasks(); var k1 = L9.keadaan.baca().kabar; var n1 = cacheMentah('pajakSetoran').length;
  __aksi.pjKeluar({ cara: 'cetak' }); drainMicrotasks(); var k2 = L9.keadaan.baca().kabar;
  __aksi.pjTawarPakai(); drainMicrotasks(); var k3 = L9.keadaan.baca().kabar;
  ok('S7 Pajak: catat setoran (memotret omzet & PPh) DITAHAN tanpa menulis apa pun, rekap konsultan DITAHAN, omzet tahun lalu dari sistem DITAHAN — kalimat toko + sebab, draf tetap di layar',
    /^Setoran ditahan — angka pajak belum bisa dipastikan: data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15\.00 WIB — ketuk "baca penuh sekarang"/.test(k1) && n1 === nS && !!L9.keadaan.baca().drafSetor
    && /^Rekap pajak ditahan — angka pajak belum bisa dipastikan: data perangkat ini belum dibaca penuh sejak kuota baca direset/.test(k2) && /^Omzet tahun lalu dari sistem ditahan — /.test(k3) && cacheMentah('aturan').length === nA, J([k1, k2, k3, nS, n1]));
  __hematL = { nyala: false }; L9.keadaan.setel({ kabar: '' }); __aksi.pjSetorSimpan(); drainMicrotasks(); var n2 = cacheMentah('pajakSetoran').length;
  ok('S7 Pajak (kontrol arah): saklar mati → setoran yang sama TERSIMPAN (penjaga hanya saat hemat baca nyala & belum lengkap)', n2 === nS + 1 && !/ditahan/.test(L9.keadaan.baca().kabar || ''), J([nS, n2, L9.keadaan.baca().kabar]));  // ---- S7d · (sanggahan 8 Okt) dokumen Laporan untuk bank / kartu kredit dari mesin yang SAMA dengan Pajak: Rekap Omzet Bulanan & Bukti Omzet (pjOmzetSistem),
  //      Neraca & laporan berkop (seluruh buku), paket bank — DITAHAN saat hemat nyala & belum lengkap (dulu tetap keluar tanpa "?"); mati = keluar seperti dulu
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'identitas', nama: 'Toko Contoh', alamat: 'Jalan Contoh 1' } }]);
  var b26 = {}; ['2026-11', '2026-12'].forEach(function (k) { b26[k] = true; });
  var keluarSemua = function () { var o = {}; [['blRekapKeluar', { keluarga: 'bulanan', tabB: 'ringkas' }], ['blBuktiKeluar', { keluarga: 'bulanan', tabB: 'bukti', pilihBukti: b26 }], ['nrKeluar', { keluarga: 'neraca', sampaiN: '' }],
      ['dkKeluar', { keluarga: 'dokumen', tabD: 'laporan', jenisD: 'labarugi', keD: '2026-12', rentangD: 1 }]].forEach(function (x) { L9.keadaan.setel(Object.assign({ kabar: '' }, x[1])); __aksi[x[0]]({ cara: 'pdf' }); drainMicrotasks(); o[x[0]] = L9.keadaan.baca().kabar; });
    L9.keadaan.setel({ kabar: '', keluarga: 'dokumen', tabD: 'paket' }); __aksi.dkPaketSusun(); drainMicrotasks(); o.paket = L9.keadaan.baca().kabar; return o; };
  var nC0 = cacheMentah('dokumenCetak').length; __hematL = { nyala: true, belumLengkap: hbHarianP(['penjualan']) }; var kT = keluarSemua(); var nC1 = cacheMentah('dokumenCetak').length;
  var hB = gambarL({ keluarga: 'bulanan', tabB: 'ringkas', kabar: '' }), hBk = gambarL({ keluarga: 'bulanan', tabB: 'bukti', pilihBukti: b26, kabar: '' }), hN = gambarL({ keluarga: 'neraca', kabar: '' }), hD = gambarL({ keluarga: 'dokumen', tabD: 'laporan', kabar: '' }), hP = gambarL({ keluarga: 'dokumen', tabD: 'paket', kabar: '' });
  var BELUM = 'belum bisa dipastikan: data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB';
  ok('S7d Laporan (sanggahan 8 Okt): penjualan belum dibaca penuh sejak reset → Rekap Omzet Bulanan, Bukti Omzet, Neraca, laporan berkop & paket bank DITAHAN ("<judul> ditahan — angkanya belum bisa dipastikan: data perangkat ini …"), TANPA nomor cetakan terpakai',
    kT.blRekapKeluar.indexOf('Rekap Omzet Bulanan ditahan — angkanya ' + BELUM) === 0 && kT.blBuktiKeluar.indexOf('Bukti Omzet ditahan — angkanya ' + BELUM) === 0 && /^Laporan Neraca ditahan — angkanya belum bisa dipastikan: data perangkat ini/.test(kT.nrKeluar)
    && /^Laporan Laba-Rugi ditahan — angkanya belum bisa dipastikan: data perangkat ini/.test(kT.dkKeluar) && /^Paket bank ditahan — angkanya belum bisa dipastikan: data perangkat ini/.test(kT.paket) && nC1 === nC0, J([kT, nC0, nC1]));
  ok('S7d layar: tombol keluar bertanda tolak dengan kalimat yang sama (Bulanan rekap & bukti, Neraca, Dokumen laporan & paket bank)',
    /data-k="tolak-blRekapKeluar">Rekap Omzet Bulanan ditahan — angkanya belum bisa dipastikan/.test(hB) && /data-k="tolak-blBuktiKeluar">Bukti Omzet ditahan — angkanya belum bisa dipastikan/.test(hBk) && /data-k="tolak-nrKeluar">Laporan Neraca ditahan/.test(hN)
    && /data-k="tolak-dkKeluar">Laporan [^<]+ ditahan — angkanya belum bisa dipastikan/.test(hD) && /data-k="tolak-paket-hemat">data perangkat ini/.test(hP) && !/NaN|undefined|\[object Object\]/.test((hB + hBk + hN + hD + hP).replace(/data-[a-z-]+="[^"]*"/g, '')),
    J([(hB.match(/data-k="tolak-blRekapKeluar">[^<]*/) || [''])[0], (hP.match(/data-k="tolak-paket-hemat">[^<]*/) || [''])[0]]));
  __hematL = { nyala: true, belumLengkap: hbHarianP(['kasbonMutasi']) }; var kK = keluarSemua(); var nC2 = cacheMentah('dokumenCetak').length;
  ok('S7d: yang belum lengkap BUKAN data omzet (kasbon) → rekap & bukti omzet keluar; neraca, laporan berkop & paket bank (seluruh buku) tetap ditahan',
    !/ditahan/.test(kK.blRekapKeluar) && !/ditahan/.test(kK.blBuktiKeluar) && /ditahan/.test(kK.nrKeluar) && /ditahan/.test(kK.dkKeluar) && /ditahan/.test(kK.paket) && nC2 === nC1 + 2, J([kK, nC1, nC2]));
  __hematL = { nyala: false }; var kM = keluarSemua(); var nC3 = cacheMentah('dokumenCetak').length;
  ok('S7d (kontrol arah): saklar mati → kelimanya keluar seperti dulu (nomor cetakan terpakai), tidak ada "ditahan"', !['blRekapKeluar', 'blBuktiKeluar', 'nrKeluar', 'dkKeluar', 'paket'].some(function (x) { return /ditahan/.test(kM[x] || ''); }) && nC3 > nC2 + 3, J([kM, nC2, nC3]));
});
"""


def bundelan_pajak():
    import re
    bagian = [bundel_baru.PRELUDE]
    for m in MODUL_PAJAK:
        teks = open(os.path.join(AKAR, m), encoding='utf-8').read()
        teks = re.sub(r"^(\s*import\s[^;\n]*;)\s*//.*$", r"\1", teks, flags=re.M)
        bagian.append('\n// ===== ' + m + ' =====\n' + bundel_baru.polos(teks))
    return uji_kunci_periode.satu_lingkup('\n'.join(bagian))


def bundelan_layar():
    import re
    bagian = [bundel_baru.PRELUDE]
    for m in MODUL_LAYAR:
        teks = open(os.path.join(AKAR, m), encoding='utf-8').read()
        teks = re.sub(r"^(\s*import\s[^;\n]*;)\s*//.*$", r"\1", teks, flags=re.M)
        bagian.append('\n// ===== ' + m + ' =====\n' + bundel_baru.polos(teks))
    return uji_kunci_periode.satu_lingkup('\n'.join(bagian))


def utama(js, cek_statis=True, js_layar=None, js_pajak=None):
    h, e = UP.jalan(UP.JAM + js + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
    if h is None: return 0, ['JSC JATUH: ' + e]
    l, g = h['lulus'], h['gagal'] + (statis() if cek_statis else [])
    if js_layar:
        h2, e2 = UP.jalan(UP.JAM + js_layar + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO.split('// ==================== S1 ·')[0]
                          + "function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); return w; }\n" + LAYAR
                          + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
        if h2 is None: g = g + ['S6 LAYAR JSC JATUH: ' + e2]
        else: l += h2['lulus']; g = g + h2['gagal']
    if js_pajak:
        h3, e3 = UP.jalan(UP.JAM + js_pajak + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO.split('// ==================== S1 ·')[0]
                          + "function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); return w; }\n" + LAYAR_PAJAK
                          + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
        if h3 is None: g = g + ['S7 PAJAK JSC JATUH: ' + e3]
        else: l += h3['lulus']; g = g + h3['gagal']
    return l, g


# ---- S6 · layar (statis): kartu dipasang di uang.js, keadaan muat dari app.js, modulepreload ----
STATIS = [
    ('baru/js/layar/uang.js', 'uang.js memanggil pemeriksaan dengan keadaan muat perangkat', 'PST.pstPeriksa(kini(), muatData())'),
    ('baru/js/layar/uang.js', 'uang.js menggambar kartu di Tutup buku', 'data-k="tb-periksa"'),
    ('baru/js/layar/uang.js', 'tombol unduh hasil pemeriksaan (berkas)', 'data-aksi="pstUnduh"'),
    ('baru/js/layar/uang.js', 'unduh memakai berkas pemeriksaan', 'const B = PST.pstBerkas(H, kini()); const bytes = unduh(B.isi, B.nama);'),
    ('baru/js/layar/uang.js', 'kartu tidak menjatuhkan layar Tutup buku', "console.error('pemeriksaan sesudah tutup buku', e)"),
    ('baru/js/layar/uang.js', 'keadaan muat membawa "tanpa internet" dari lokal()', 'offline: !!L.offline }, hb); };'),
    ('baru/js/layar/uang.js', 'hemat baca: keadaan muat membawa kelengkapan dari lokal() (hanya saat nyala)', "const hb = hematNyala(L) ? { hemat: Object.assign({}, L.hemat.belumLengkap || {}) } : {};"),
    ('baru/js/app.js', 'hemat baca: lokal() layar Uang membawa keadaan hemat (kelengkapan)', "hemat: (() => { try { return fb.hematKeadaan(); } catch (e) { return { nyala: false }; } })() });"),
    ('baru/js/app.js', 'hemat baca: Laporan › Pajak membaca keadaan hemat', "keTujuan,\n  hemat: () => { try { return fb.hematKeadaan(); } catch (e) { return { nyala: false }; } } });"),
    ('baru/js/data/firebase.js', 'hemat baca: hematKeadaan meneruskan keadaan sesi hemat (belumLengkap)', 'return Object.assign(_hemat.keadaan(), dasar);'),
    ('baru/js/data/hemat-baca.js', 'hemat baca: keadaan() sesi membawa SATU sumber kelengkapan', ', belumLengkap: sesi.belumLengkap() };'),
    ('baru/js/app.js', 'lokal() layar Uang membawa keadaan muat (koleksi siap / total / ditolak)', 'koleksiSiap: statusFb.koleksiSiap, koleksiTotal: statusFb.koleksiTotal, ditolak: statusFb.ditolak || []'),
    ('baru/js/app.js', 'lokal() layar Uang membawa keadaan tanpa internet', 'offline: statusFb.offline,'),
    ('baru/index.html', 'modul pemeriksaan ada di modulepreload', '<link rel="modulepreload" href="js/layar/periksa-sesudah-logika.js">'),
]


def statis(ganti=None):
    out = []
    for berkas, nama, jangkar in STATIS:
        t = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
        if ganti and ganti[0] == berkas: t = t.replace(ganti[1], ganti[2])
        if jangkar not in t: out.append('statis ' + berkas + ': ' + nama)
    return out


ASAP = r"""
// ==================== ASAP — CADANGAN TOKO LOKAL (tidak di-commit; dilewati di CI). Putusan per tanggal & aturan pajak = TIRUAN di memori, bukan data owner ====================
var salahA = []; var hasilA = {};
function muatCad() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' };
  terapkanKeCache([{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: 5, batasBebas: 500000000, batasOmzet: 4800000000 }, { tanggal: '2026-10-06', jam: '10:00' }) }]); }
['2027-01-05T10:00:00+07:00', '2027-02-20T10:00:00+07:00'].forEach(function (x, i) {
  muatCad(); var w = jam('2027-01-05T10:00:00+07:00'); var R0 = ritualPenuh(w); if (R0.tolak) { salahA.push('ritual ditolak: ' + R0.tolak.slice(0, 300)); return; }
  if (i === 1) tulis(susunSelesai(2026, 'cadangan-sesudah-asap.json', jam('2027-01-05T12:00:00+07:00'), false, LA));
  jam(x); var t0 = new Date().getTime(); var H = pstPeriksa(new Date(__KINI), M_OK);
  if (!H) { salahA.push(x + ': kartu tidak tampil'); return; }
  hasilA[x.slice(0, 10)] = { fase: H.fase, n: H.n, sama: H.nSama, beda: H.nBeda, belum: H.nBelum, perKelompok: H.kelompok.map(function (g) { return g.baris.length; }),
    rak: baris(H, 'rakJual').ket, bukuMerek: baris(H, 'bukuMerek').ket.split(' · ')[0], kemasan: baris(H, 'bukuKemasan').ket, pembuka: baris(H, 'pembuka').a + ' catatan',
    perNama: ['piutangNama', 'kasbonNama', 'utangNama'].map(function (id) { return baris(H, id).ket.split(' · ')[0]; }), susulan: H.susulan, sesudahKunci: H.sesudahKunci, sumber: H.sumber.replace(/\(.*\)/, ''), ms: new Date().getTime() - t0 };
  if (!H.beres) salahA.push(x + ': ' + ringkasH(H).replace(/Rp[\d.]+/g, 'Rp…').slice(0, 900));
  // hemat baca (#111): nyala & lengkap = sama persis; nyala & SEMUA belum dibaca penuh sejak reset = baris yang membaca buku hidup "?" (tidak ada ✗ palsu)
  var Hl = pstPeriksa(new Date(__KINI), Object.assign({}, M_OK, { hemat: {} })); var semuaH = {}; hbKoleksiHemat().forEach(function (n) { semuaH[n] = { jenis: 'harian', sebab: hbSebabHarian('2027-01-05') }; });
  var Hh = pstPeriksa(new Date(__KINI), Object.assign({}, M_OK, { hemat: semuaH }));
  hasilA[x.slice(0, 10)].hemat = { lengkapSama: J(Hl) === J(H), belumDibacaPenuh: { belum: Hh.nBelum, beda: Hh.nBeda, sama: Hh.nSama } };
  if (J(Hl) !== J(H)) salahA.push(x + ': hemat baca nyala & lengkap TIDAK sama dengan mati');
  if (Hh.nBeda || !Hh.nBelum || Hh.beres) salahA.push(x + ': hemat baca nyala & belum dibaca penuh — ' + Hh.nBelum + ' belum, ' + Hh.nBeda + ' beda');
});
print(JSON.stringify({ salah: salahA, hasil: hasilA }));
"""


def asap(js, berkas):
    h, e = UP.jalan(UP.JAM + js + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\nvar CAD = ' + open(berkas, encoding='utf-8').read() + ';\n' + UP.BERSAMA + TAMBAH + ASAP)
    if h is None: return None, ['ASAP JATUH: ' + e]
    return h['hasil'], h['salah']


RUSAK = [
    ('kartu memakai hasil periksa HIDUP saja (bkPeriksaDipakai dilewati) — titik kas yang maju membuat ✓ jadi ?', "const PU = bkPeriksaDipakai(tahun); const H = a.hariIni || null;", "const PU = periksaUlangBuku(tahun); const H = a.hariIni || null;"),
    ('baris "?" dianggap sama (lulus palsu)', "    return pstBaris({ id: b.id, judul, ket, status: 'belum', a: b.a, b: b.b, sebab });\n", "    return pstBaris({ id: b.id, judul, ket, status: 'sama', a: b.a, b: b.b, sebab });\n"),
    ('data belum dimuat tidak ditahan (tanpa penjaga muat)', "const m = M || {}; if (m.siap === false) return", "const m = M || {}; if (false) return"),
    ('data ditolak server diabaikan', "if (tolak.length) return 'data '", "if (false) return 'data '"),
    ('sanggahan: perangkat tanpa internet dianggap tersambung', "  if (m.offline) return", "  if (false) return"),
    ('sanggahan: salinan perangkat (belum dijawab server) dianggap jawaban server', "if (basi.length) return 'data '", "if (false) return 'data '"),
    ('kiriman tutup buku yang menunggu server diabaikan', "  if (tunggu) return 'catatan tutup buku", "  if (false) return 'catatan tutup buku"),
    ('berita acara selesai yang menunggu server tidak dilihat (kemajuanBuku saja)', " || dokTertunda('tutupBukuAcara', String(T.acara.id || T.tahun))", ""),
    ('sanggahan: hasil beku yang menunggu server tidak dilihat', " || dokTertunda('pengaturan', 'periksaArsip' + T.tahun);", ";"),
    ('modal: saldo pembuka dibandingkan dengan dirinya sendiri', "const sama = !hilang && Math.abs(sesudah - beku.n) < 0.5;", "const sama = !hilang;"),
    ('sanggahan: modal dibaca dari buku hidup (setoran modal susulan = beda palsu)', "{ id: 'modal', judul: '2 · Modal owner', baris: [pstModal(T, M, tunggu, S.modal)] },", "{ id: 'modal', judul: '2 · Modal owner', baris: [pstModal(T, M, tunggu, Math.round(modalTertanam(tbCutoff(T.tahun))))] },"),
    ('saldo pembuka tidak dijumlah lagi dari dokumennya (piutang pembuka diubah lolos)', "    if (x === undefined || x === null || Math.abs(Number(b.n) - Number(x)) >= 0.5) bedaJ.push(", "    if (false) bedaJ.push("),
    ('saldo pembuka tersembunyi dihitung ada', "else if (!pembukaBerlaku(x)) sembunyi += 1; else ada += 1; });", "else ada += 1; });"),
    ('sanggahan: baris saldo pembuka hanya menuntut koleksi stok (bon pelanggan ditolak = "dokumen hilang" ✗)', "const kurangP = pstKurang(M, PST_PERLU_PEMBUKA, tunggu)", "const kurangP = pstKurang(M, PST_PERLU_STOK, tunggu)"),
    ('sanggahan: bon lama yang DIBETULKAN owner dibaca dengan nilai barunya (pembetulan sah = ✗)', "  return r ? Object.assign({}, d, { nominal: Number(r.dari.nominal), bonTanggal: r.dari.bonTanggal || null }) : d;", "  return d;"),
    ('tanda buku & rak dari dokumen pembuka sekarang, bukan baris yang ditulis di berita acara (tanda 25 kg yang lepas lolos)', "  return R ? R.beras.map((r) => Object.assign({}, r)) : null;",
     "  return R ? pstPembukaMentah('batch', Number(a.tahun)).reduce((o, b) => o.concat((b.merkList || []).map((m) => ({ merk: m.merk, satuan: m.satuan, berat: Number(m.beratKarung) || 0, kg: Number(m.totalKg) || 0, indukUkuran: m.indukUkuran }))), []) : null;"),
    ('sanggahan: buku per merek dibandingkan dengan baris yang DITULIS (penjaga mewarisi kekuatannya — merek tertukar lolos)', "const exp = {}; if (SB) (SB.merek || []).forEach((r) => { exp[r.merk] = (exp[r.merk] || 0) + (Number(r.kg) || 0); });", "const exp = {}; (BP || []).forEach((r) => { exp[r.merk] = (exp[r.merk] || 0) + (Number(r.kg) || 0); });"),
    ('sanggahan: tanpa pembanding yang berdiri sendiri = ✓ (lulus palsu)', "    : !SB ? pstBaris({ id: 'bukuMerek', judul: j1, status: 'belum'", "    : !SB ? pstBaris({ id: 'bukuMerek', judul: j1, status: 'sama'"),
    ('sanggahan: per nama — pindah orang tidak disebut', "    if (Math.abs(nA - nB) >= 0.5) beda.push(", "    if (false) beda.push("),
    ('buku dibaca dari cache hidup, bukan saat tahun baru dibuka (penjualan Januari = beda palsu)', "  return denganCacheSaring(nama, (d) => !!(d && d.tutupBuku && Number(d.tahunDari) === t), fn, pstSaatKunci);", "  return fn();"),
    ('rak Jual: tanda buku 25 kg tidak dibaca lagi', "    if (r.indukUkuran) { nTanda += 1; const u = C.uk[m]; if (!u || u.induk !== String(r.indukUkuran) || (b && u.berat !== b)) salah.push(", "    if (r.indukUkuran) { nTanda += 1; const u = C.uk[m]; if (false) salah.push("),
    ('rak Jual: karung yang hilang tidak disebut', "    if (!ch) salah.push(nama + ' ' + b + ' kg (buku ' + m + '): tidak tampil di rak Jual');", "    if (!ch) nTanpaHarga += 0;"),
    ('stok minus saldo pembuka tidak dihitung', "    const minus = minusBuku(tglBuka).daftar.filter((x) => PST_JENIS_STOK[x.jenis]);", "    const minus = [];"),
    ('minus hari ini dijadikan beda (bukan yang diperiksa)', "status: V.minus.length ? 'beda' : 'sama', satuan: 'teks', a: V.minus.length", "status: V.minus.length || minusKini.length ? 'beda' : 'sama', satuan: 'teks', a: V.minus.length"),
    ('potret: bulan yang hilang tidak dihitung', "const kosongB = kunciBulan.filter((k) => !bulan[k] ||", "const kosongB = [].filter((k) => !bulan[k] ||"),
    ('pajak: omzet dibandingkan dengan dirinya sendiri', "status: Math.abs(Math.round(TJ.totalSistem) - ptOmzet) < 0.5 ? 'sama' : 'beda', a: ptOmzet", "status: 'sama', a: ptOmzet"),
    ('setoran: yang hilang lolos', "if (!(x.jumlahSetor - baru - 0.5 <= ps && ps <= x.jumlahSetor + 0.5)) bedaS.push(", "if (!(x.jumlahSetor - baru - 0.5 <= ps)) bedaS.push("),
    ('sanggahan: setoran — NTPN yang hilang ditutupi setoran lain berjumlah sama', "if (ntpnKini.indexOf(nt) < 0) bedaS.push(", "if (false) bedaS.push("),
    ('setoran sesudah tutup buku dianggap beda', "const baru = x.setor.filter((s) => sejak && String(s.dicatatPada || '') >= sejak)", "const baru = x.setor.filter((s) => false)"),
    ('kelompok 6 dihitung dua kali (utang & piutang juga di kelompok 1)', "const lain = PB.baris.filter((x) => PST_UTANG.indexOf(x.id) < 0);", "const lain = PB.baris.slice();"),
    ('sanggahan: catatan susulan tidak disebut (petunjuk "bukan alasan membatalkan" hilang)', "if (L.susulan || L.sesudahKunci || SU) petunjuk.push(", "if (false) petunjuk.push("),
    ('kartu tampil sebelum arsip habis', "if (a.status === 'terkunci') return bkArsipHabis(tahun) || !arsipBuku(tahun).n ?", "if (a.status === 'terkunci') return true ?"),
    ('kartu tampil selamanya sesudah selesai', "return iso <= pstAkhirFeb(tahun + 1) || (s30 && iso <= s30) ?", "return true ?"),
    ('tahun kartu dari era (saldo pembuka yang terlihat), bukan berita acara — penanda hilang = kartu lenyap diam-diam', "const a = ambilTutupBukuAcara().filter((x) => x && isFinite(Number(x.tahun)) && (x.status === 'terkunci' || x.status === 'selesai'))", "const a = ambilTutupBukuAcara().filter((x) => x && Number(x.tahun) === eraBuku() && (x.status === 'terkunci' || x.status === 'selesai'))"),
    ('ringkasan "beres" walau ada yang belum bisa diperiksa', "const beres = !nBeda && !nBelum && n > 0;", "const beres = !nBeda && n > 0;"),
    ('hemat (#111): kelengkapan perangkat diabaikan — koleksi yang belum dibaca penuh sejak reset dianggap lengkap (✓ palsu)', "const hb = m.hemat ? hbBelumUntuk(m.hemat, semua ? null : perlu) : null; if (hb) return", "const hb = null; if (hb) return"),
    ('hemat (#111): kelengkapan hanya diperiksa untuk "semua" (koleksi per baris diabaikan)', "const hb = m.hemat ? hbBelumUntuk(m.hemat, semua ? null : perlu) : null;", "const hb = m.hemat && semua ? hbBelumUntuk(m.hemat, null) : null;"),
    ('hemat (#111): sebab hemat kalah dari "masih dari simpanan perangkat" (owner menunggu sinyal, padahal harus baca penuh)', "  const hb = m.hemat ? hbBelumUntuk(m.hemat, semua ? null : perlu) : null; if (hb) return 'data ' + pstKataRingkas(hb.utama) + ' ' + hb.sebab + hbEkorLain(hb);\n  const basi = (semua ? KOLEKSI.map((k) => k.nama) : perlu).filter((n) => koleksiDariCache(n)); if (basi.length) return 'data ' + pstDaftarKata(basi) + ' masih dari simpanan perangkat, belum dijawab server — tunggu sampai tersambung';\n",
     "  const basi = (semua ? KOLEKSI.map((k) => k.nama) : perlu).filter((n) => koleksiDariCache(n)); if (basi.length) return 'data ' + pstDaftarKata(basi) + ' masih dari simpanan perangkat, belum dijawab server — tunggu sampai tersambung';\n  const hb = m.hemat ? hbBelumUntuk(m.hemat, semua ? null : perlu) : null; if (hb) return 'data ' + pstKataRingkas(hb.utama) + ' ' + hb.sebab + hbEkorLain(hb);\n"),
    ('hemat (sanggahan 8 Okt): sebab satu jenis catatan dipinjamkan ke semua yang disebut (owner menunggu padahal yang lain butuh ketukan)', "if (hb) return 'data ' + pstKataRingkas(hb.utama) + ' ' + hb.sebab + hbEkorLain(hb);", "if (hb) return 'data ' + pstKataRingkas(hb.koleksi) + ' ' + hb.sebab;"),
]
RUSAK_LAIN = [
    ('ritual tidak menyimpan ringkasan saldo pembuka di berita acara', 'baru/js/layar/tutup-buku-logika.js', "  acara.pembukaRingkas = ringkasPembuka(P.dokumen, tahun);\n", ""),
    ('sanggahan: ritual tidak menyimpan pembanding dari catatan hidup 31 Des', 'baru/js/layar/tutup-buku-logika.js', "  if (R.versi === 2) R.sebelum = bkPembandingSebelum(tbCutoff(Number(tahun)));\n", ""),
    ('hasil yang dibekukan tidak bertanda (kartu tidak tahu sumbernya)', 'baru/js/layar/tutup-buku-logika.js', "{ beku: { tanggal: String(P.tanggal || ''), pada: String(P.pada || ''), susulan: Number(P.susulan) || 0, sesudahKunci: Number(P.sesudahKunci) || 0 } }", "{}"),
    ('sanggahan (A9): catatan susulan ikut dihitung di sisi sesudah periksa ulang', 'baru/js/layar/tutup-buku-logika.js', "if (susul[id]) return 'susulan';", "if (false) return 'susulan';"),
    ('sanggahan: karcis hari ritual yang ditulis sebelum kunci tapi telat masuk ikut dihitung', 'baru/js/layar/tutup-buku-logika.js', "    return t < H.tanggal || (jamP && String(d.jam || '') < jamP) ? 'sesudahKunci' : ''; };", "    return ''; };"),
    ('sanggahan: nota yang ditulis SESUDAH jam kunci ikut disaring (berjualan selama arsip lolos)', 'baru/js/layar/tutup-buku-logika.js', "(jamP && String(d.jam || '') < jamP)", "true"),
    ('sanggahan: patokan hari tutup buku tanpa daftar catatan yang sudah ada', 'baru/js/layar/tutup-buku-logika.js', "ada: ada.sort() };", "ada: null };"),
    ('hemat (#111): kunci bulan tanpa ⛔ butir kelengkapan (potret bulan dibekukan dari data setengah)', 'baru/js/layar/kunci-periode-logika.js', "  if (K.hemat) { const hb = hbKalimatBelum(K.hemat, null);", "  if (false) { const hb = hbKalimatBelum(K.hemat, null);"),
    ('hemat (#111): Lanjutkan / Batalkan tutup buku dari buku yang belum lengkap', 'baru/js/layar/tutup-buku-logika.js', "  if (hb) return 'Tutup buku: ' + hb + ' — Lanjutkan atau Batalkan sesudah datanya lengkap.';", "  if (false) return 'Tutup buku: ' + hb + ' — Lanjutkan atau Batalkan sesudah datanya lengkap.';"),
    ('hemat (#111): g7 hanya "dibaca penuh sesi ini" (batu nisan & ubahan sesudahnya diabaikan)', 'baru/js/layar/tutup-buku-logika.js', "const ok7 = !!L.hemat.totalSesiIni && !hb;", "const ok7 = !!L.hemat.totalSesiIni;"),
    ('hemat (sanggahan 8 Okt): pintu susunKunci tidak memeriksa g7 (kelengkapan hanya di layar langkah 1)', 'baru/js/layar/tutup-buku-logika.js', "(g.id === 'g1' || g.id === 'g6' || g.id === 'g7') && !g.ok", "(g.id === 'g1' || g.id === 'g6') && !g.ok"),
    ('hemat (sanggahan 8 Okt): pintu susunKunci memanggil gerbang tanpa lokal() layar (g7 tidak pernah ada di pintu)', 'baru/js/layar/tutup-buku-logika.js', "const G = gerbangBuku(tahun, ugKiniDari(w), L || {}, {});", "const G = gerbangBuku(tahun, ugKiniDari(w), {}, {});"),
    ('cache sementara tidak dikembalikan sesudah diperiksa (layar lain membaca saldo pembuka saja)', 'baru/js/data/toko.js', "  try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); _versiCache += 1; }\n}\n\n// ---- keranjang aktif", "  return fn();\n}\n\n// ---- keranjang aktif"),
]
# uang.js — layar dijalankan di jsc; kontrolnya memakai bundel layar
RUSAK_LAYAR = [
    ('sanggahan (tiga keadaan): baris teks digambar "sebelum → sesudah" dengan sisi kanan kosong', "x.satuan === 'teks' ? (x.status === 'belum' || !ada(x.a) ? '—' : PST.pstTeks(x.a, 'teks'))\n      : ", ""),
    ('sanggahan: pesan galat mentah tampil di layar', "Pemeriksaan tidak bisa dijalankan di perangkat ini — tutup buku", "Pemeriksaan tidak bisa dijalankan di perangkat ini (${String((e && e.message) || e).slice(0, 120)}) — tutup buku"),
    ('sanggahan: keadaan tanpa internet tidak diteruskan ke kartu', "offline: !!L.offline }, hb); };", "offline: false }, hb); };"),
    ('hemat: muatData tidak meneruskan kelengkapan (kartu ✓ palsu dari data setengah)', "const hb = hematNyala(L) ? { hemat: Object.assign({}, L.hemat.belumLengkap || {}) } : {};", "const hb = {};"),
    ('hemat: perkiraan kuota dihitung dari data setengah', "    const hb = hematBelum(null);\n", "    const hb = '';\n"),
    ('hemat: konteks kunci bulan tanpa kelengkapan', "hematNyala(L) ? { hemat: Object.assign({}, L.hemat.belumLengkap || {}) } : {}); };", "{}); };"),
]
RUSAK_PAJAK = [
    ('hemat: catat setoran & omzet tahun lalu dari data setengah tidak ditahan', "  const tahanPajak = (apa) => { const hb = hematPajak(); if (!hb) return false;", "  const tahanPajak = (apa) => { const hb = ''; if (!hb) return false;"),
    ('hemat: pita "?" pajak hilang (angka setengah tampil pasti)', "const HB = hematPajak(); if (HB) Dk.tolak", "const HB = ''; if (HB) Dk.tolak"),
    ('hemat: rekap konsultan dari data setengah tidak ditahan', "const hbK = hematPajak(); if (hbK) D.tolak", "const hbK = ''; if (hbK) D.tolak"),
    ('hemat: pajak membaca kelengkapan koleksi yang salah (penjualan tidak ikut)', "const PJ_PERLU_HEMAT = ['penjualan', 'retur', 'pajakSetoran', 'pajakOmzetLuar'];", "const PJ_PERLU_HEMAT = ['retur', 'pajakSetoran', 'pajakOmzetLuar'];"),
    # ---- sanggahan 8 Okt (b): dokumen Laporan untuk bank / kartu kredit dari mesin yang sama — tiap penjaga berbunyi di S7d
    ('hemat (sanggahan 8 Okt): Rekap Omzet Bulanan dari data setengah tidak ditahan', "const dokRekapJaga = () => tahanDok(dokRekap(), LP_PERLU_OMZET);", "const dokRekapJaga = () => dokRekap();"),
    ('hemat (sanggahan 8 Okt): Bukti Omzet dari data setengah tidak ditahan', "const D = tahanDok({ kop: LP.kopUntuk(LP.pakaiKop().pakai.omzet, I), judul: 'Bukti Omzet',", "const D = ((x) => x)({ kop: LP.kopUntuk(LP.pakaiKop().pakai.omzet, I), judul: 'Bukti Omzet',"),
    ('hemat (sanggahan 8 Okt): Neraca berkop dari data setengah tidak ditahan', "tahanDok(D, ['*']); await keluarkan(D, { jenis: 'neraca'", "await keluarkan(D, { jenis: 'neraca'"),
    ('hemat (sanggahan 8 Okt): laporan berkop (laba-rugi / arus kas) dari data setengah tidak ditahan', "const D = tahanDok(LP.laporanBerkop(s.jenisD, s.keD || bulanKini(), s.rentangD, kini()), ['*']); await keluarkan", "const D = LP.laporanBerkop(s.jenisD, s.keD || bulanKini(), s.rentangD, kini()); await keluarkan"),
    ('hemat (sanggahan 8 Okt): paket bank dari data setengah tidak ditahan', "const hbP = hematBelum(['*']); if (hbP) {", "const hbP = ''; if (hbP) {"),
    ('hemat (sanggahan 8 Okt): rekap & bukti omzet membaca kelengkapan koleksi yang salah (penjualan tidak ikut)', "const LP_PERLU_OMZET = ['penjualan', 'retur'];", "const LP_PERLU_OMZET = ['retur'];"),
    ('hemat (sanggahan 8 Okt): rekap & bukti omzet menunggu SELURUH buku (kasbon yang belum lengkap menahan omzet)', "const LP_PERLU_OMZET = ['penjualan', 'retur'];", "const LP_PERLU_OMZET = ['*'];"),
]


def bundelan():
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))


# ---- UJI PEMBANDING saklar MATI (#111 × Paket C): hasil kartu / gerbang / kunci bulan / Lanjutkan-Batalkan / HTML Uang & Pajak dengan berkas di <ref> vs berkas kerja ----
BANDING_UANG = r"""
siapRitual(); setelSumber('firestore', 'kotak pasir'); var kB = new Date(__KINI); __hemat = { nyala: false, saklar: false, owner: true }; var hasilB = {};
hasilB.kartu = [M_OK, { siap: false, siapN: 30, total: 56, ditolak: [] }, Object.assign({}, M_OK, { offline: true }), { siap: true, siapN: 56, total: 56, ditolak: ['modalOwner', 'piutangMutasi'] }].map(function (M) { return pstPeriksa(kB, M); });
hasilB.gerbang = gerbangBuku(2027, kB, { antre: [], idPerangkat: 'mac-contoh', hemat: __hemat });
hasilB.kunci = kpDaftarPeriksa('2026-12', kB, { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} });
hasilB.sambung = [bkSambungan({ hemat: __hemat }), bkSambungan({ offline: true, hemat: __hemat })];
U = buatU(); U.tampilkan(true); hasilB.uang = [gambarU({ keluarga: 'buku' }), gambarU({ pstRinci: true })];
// sanggahan 8 Okt (e): kartu kunci bulan dari LAYAR (uang.js konteksKunci — jalan hemat yang sesungguhnya saat mati), bukan hanya kpDaftarPeriksa tanpa hemat
hasilB.kpKartu = potong(gambarU({ keluarga: 'buku', pstRinci: false }), 'data-k="kp-butir"', 'data-aksi="kpKunci"');
__muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: true }; hasilB.uang.push(gambarU({})); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], offline: false };
// pintu tutup buku (susunKunci) dengan lokal() layar saat mati — g7 tidak ada, kiriman sama
var wB = siapKotak(); putusSemua(wB); var RB = susunKunci(2026, D, wB, Object.assign({}, LA, { hemat: __hemat })); hasilB.pintu = { tolak: RB.tolak || '', n: RB.kiriman ? RB.kiriman.length : -1 };
print(JSON.stringify(hasilB));
"""
BANDING_PAJAK = r"""
siapRitual(); setelSumber('firestore', 'kotak pasir'); __hematL = { nyala: false }; L9 = bukaL(true); L9.tampilkan(true); var hasilB = {};
hasilB.pajak = [gambarL({ keluarga: 'pajak', tahunPj: 2027 }), gambarL({ keluarga: 'pajak', tahunPj: 2026 })];
L9.keadaan.setel({ drafSetor: { masaPajak: '2027-01', tanggalSetor: '2027-01-05', jumlah: '1000', ntpn: '', atasNama: 'Contoh', catatan: 'setoran contoh uji' }, kabar: '' });
__aksi.pjSetorSimpan(); drainMicrotasks(); __aksi.pjKeluar({ cara: 'cetak' }); drainMicrotasks(); hasilB.setor = [cacheMentah('pajakSetoran').length, L9.keadaan.baca().kabar];
// sanggahan 8 Okt (b): dokumen Laporan (Bulanan rekap & bukti, Neraca, Dokumen laporan & paket) — HTML & hasil ketukan keluar saat mati sama persis
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'identitas', nama: 'Toko Contoh', alamat: 'Jalan Contoh 1' } }]); var bB = { '2026-11': true, '2026-12': true };
hasilB.laporan = [gambarL({ keluarga: 'bulanan', tabB: 'ringkas', kabar: '' }), gambarL({ keluarga: 'bulanan', tabB: 'bukti', pilihBukti: bB, kabar: '' }), gambarL({ keluarga: 'neraca', kabar: '' }),
  gambarL({ keluarga: 'dokumen', tabD: 'laporan', jenisD: 'labarugi', keD: '2026-12', kabar: '' }), gambarL({ keluarga: 'dokumen', tabD: 'paket', kabar: '' })];
hasilB.keluar = [['blRekapKeluar', { keluarga: 'bulanan', tabB: 'ringkas' }], ['blBuktiKeluar', { keluarga: 'bulanan', tabB: 'bukti', pilihBukti: bB }], ['nrKeluar', { keluarga: 'neraca' }],
  ['dkKeluar', { keluarga: 'dokumen', tabD: 'laporan', jenisD: 'labarugi', keD: '2026-12', rentangD: 1 }], ['dkPaketSusun', { keluarga: 'dokumen', tabD: 'paket' }]].map(function (x) {
  L9.keadaan.setel(Object.assign({ kabar: '' }, x[1])); __aksi[x[0]]({ cara: 'pdf' }); drainMicrotasks(); return [x[0], L9.keadaan.baca().kabar, cacheMentah('dokumenCetak').length]; });
print(JSON.stringify(hasilB));
"""


def banding_mati(ref):
    import re
    def baca_ref(m):
        r = subprocess.run(['git', 'show', ref + ':' + m], cwd=AKAR, capture_output=True, text=True)
        if r.returncode != 0: raise SystemExit('BANDING: ' + m + ' tidak ada di ' + ref)
        return r.stdout
    def baca_kerja(m): return open(os.path.join(AKAR, m), encoding='utf-8').read()
    def bdl(daftar, baca):
        bagian = [bundel_baru.PRELUDE]
        for m in daftar:
            teks = re.sub(r"^(\s*import\s[^;\n]*;)\s*//.*$", r"\1", baca(m), flags=re.M)
            bagian.append('\n// ===== ' + m + ' =====\n' + bundel_baru.polos(teks))
        return uji_kunci_periode.satu_lingkup('\n'.join(bagian))
    awal = (UP.JAM, '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO.split('// ==================== S1 ·')[0]
            + "function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); return w; }\n")
    hasil = {}
    for nama, daftar, depan, isi in [('uang', MODUL_LAYAR, LAYAR.split("coba('S6',")[0], BANDING_UANG), ('pajak', MODUL_PAJAK, LAYAR_PAJAK.split("coba('S7-pajak',")[0], BANDING_PAJAK)]:
        for sisi, baca in [('ref', baca_ref), ('kerja', baca_kerja)]:
            h, e = UP.jalan(awal[0] + bdl(daftar, baca) + awal[1] + depan + isi)
            if h is None: raise SystemExit('BANDING ' + nama + ' (' + sisi + ') JSC JATUH: ' + e)
            hasil[(nama, sisi)] = h
    # sanggahan 8 Okt (e): pembanding yang tidak menggambar kartu kunci bulan / dokumen Laporan = lulus kosong
    for sisi in ['ref', 'kerja']:
        if 'data-k="kp-butir"' not in (hasil[('uang', sisi)].get('kpKartu') or ''): raise SystemExit('BANDING: kartu kunci bulan tidak tergambar (' + sisi + ') — pembanding kosong')
        if len(hasil[('pajak', sisi)].get('laporan') or []) != 5: raise SystemExit('BANDING: dokumen Laporan tidak tergambar (' + sisi + ')')
    beda = []
    for nama in ['uang', 'pajak']:
        A, B = hasil[(nama, 'ref')], hasil[(nama, 'kerja')]
        for k in sorted(set(A) | set(B)):
            if json.dumps(A.get(k), sort_keys=True) != json.dumps(B.get(k), sort_keys=True): beda.append(nama + '.' + k)
    n = sum(len(hasil[(nama, 'ref')]) for nama in ['uang', 'pajak'])
    return n, beda


if __name__ == '__main__':
    ref_b = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--banding=')), '')
    if ref_b:
        n, beda = banding_mati(ref_b)
        print('UJI PEMBANDING saklar MATI (%s vs berkas kerja): %d bagian · %s' % (ref_b, n, 'SAMA PERSIS' if not beda else 'BEDA: ' + ', '.join(beda)))
        sys.exit(2 if beda else 0)
    js = bundelan()
    if '--kontrol' in sys.argv:
        kode = 0; logika = open(os.path.join(AKAR, LOGIKA), encoding='utf-8').read()
        for nama, a, b in RUSAK:
            if logika.count(a) != 1 or js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_LAIN:
            sumber = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
            if sumber.count(a) != 1 or js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        jl = bundelan_layar(); uang = open(os.path.join(AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
        for nama, a, b in RUSAK_LAYAR:
            if uang.count(a) != 1 or jl.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(jl.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js, False, jl.replace(a, b))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        jp = bundelan_pajak(); lap = open(os.path.join(AKAR, 'baru/js/layar/laporan.js'), encoding='utf-8').read()
        for nama, a, b in RUSAK_PAJAK:
            if lap.count(a) != 1 or jp.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(jp.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js, False, None, jp.replace(a, b))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for berkas, nama, jangkar in STATIS:
            g = statis((berkas, jangkar, jangkar[:len(jangkar) // 2] + '§' + jangkar[len(jangkar) // 2 + 1:]))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + 'statis dicabut: ' + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js, True, bundelan_layar(), bundelan_pajak())
    print('PEMERIKSAAN SESUDAH TUTUP BUKU (kotak pasir + layar Uang jsc): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    berkas = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--cadangan=')), '') or os.environ.get('PERIKSA_ASAP', '')
    if berkas:
        if not os.path.exists(berkas): print('ASAP: berkas cadangan tidak ada (' + berkas + ')'); sys.exit(2)
        h, s = asap(js, berkas)
        print('ASAP CADANGAN LOKAL (%s): %s' % (os.path.basename(berkas), json.dumps(h, ensure_ascii=False)))
        for x in s: print('   ✗ ' + x)
        if s: sys.exit(2)
    sys.exit(0 if not g else 2)
