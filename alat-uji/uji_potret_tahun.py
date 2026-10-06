#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_potret_tahun.py — PAKET B siap 2027 (owner 7 Okt 2026): Laporan & Pajak membaca TAHUN YANG SUDAH DITUTUP BUKU. KOTAK PASIR (nama & angka contoh) di jsc.

Sesudah tutup buku 2026, arsip memindah catatan 2026 keluar dari memori. Tanpa potret, Pajak & Laporan 2026 jadi Rp0 bertanda FINAL (audit kesiapan 2027 H1/H2,
R1–R5). Yang dijaga di sini:
  P1  RITUAL menulis POTRET tahun di berita acara (tutupBukuAcara/{tahun}.potret): 12 bulan + hari berjualan, bentuk yang diterima Firestore (tanpa undefined /
      fungsi / larik di dalam larik), juga di kiriman 'berjalan' & 'terkunci'; gagal disusun = kunci DITOLAK; latihan menyusunnya tanpa menulis
  P2  SEBELUM ritual = SESUDAH ritual (arsip habis), rupiah demi rupiah, per layar — jam 5 Jan 2027 DAN 31 Mar 2027:
      Pajak 2026 (12 masa: omzet sistem, nota, sebelum potongan, kumulatif, PPh, kelengkapan) · Rekap pajak untuk konsultan · DK3 rekap 12 bulan · Laba (tiga angka,
      tangga, jumlah nota rugi/tanpa modal/susut) · ke mana laba kotor · inti bulan · kendali biaya per jenis + pemicu + titik impas · Tahunan 2026 · laporan berkop
      laba-rugi 1/3/12 bulan · arus kas (baris masuk/keluar) · neraca akhir tiap bulan (kas akhir bulan dari tutup hari) · neraca hari ini (laba ditahan dari
      potret, bukan "belum terjelaskan") · Harian 14 hari · Mingguan per hari · tren Dasbor hari/minggu/bulan · Biaya Januari (bulan lalu = Desember)
  P3  setoran masa DESEMBER 2026 dicatat 10 Jan 2027 (sesudah ritual): potret omzet saat setor = omzet sebelum ritual, status "disetor", bukan "berubah"
  P4  PILIH TAHUN di Pajak: daftar 2027 + 2026; bawaan Jan–Mar = tahun lalu selama ada masa terutang; 1 Apr = tahun berjalan; pil masa & omzet di luar sistem
      tahun lalu = 12 bulan; layar memakai tahun pilihan (statis laporan.js); Beranda & pengingat menyebut masa Desember (R2)
  P5  JANUARI 2027 tidak dicap "belum lengkap" karena awal sistem pindah (R4) — dengan potret DAN tanpa potret (tahun ditutup sistem ini, tahun sesudahnya sejak 1 Jan)
  P6  BATALKAN tutup buku: potret tidak dibaca lagi, angka kembali dari catatan hidup (= sebelum ritual)
  P7  tahun ditutup TANPA potret (dikunci sebelum Paket B): Bukti omzet, DK3, laporan berkop, neraca menolak / '—' — tidak ada Rp0 bertanda final
  P8  omzet tahun lalu PER TAHUN + tawaran dari sistem; aturan pajak berlabel tahun pajak (rapi-rapi audit)

    python3 alat-uji/uji_potret_tahun.py                 → N lulus · 0 gagal
    python3 alat-uji/uji_potret_tahun.py --kontrol       → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_potret_tahun.py --asap=/jalur/backup-batch-….json   (atau env POTRET_ASAP=…) → juga cadangan LOKAL (tidak di-commit; dilewati di CI)
"""
import os, sys, json, subprocess, tempfile, re
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
JSC = uji_kunci_periode.JSC
_M = uji_kunci_periode.MODUL + ['baru/js/layar/sistem-logika.js', 'baru/js/layar/kendali-biaya-logika.js', 'baru/js/layar/potret-logika.js', 'baru/js/layar/dasbor-logika.js']
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]
JAM = "var __KINI = new Date('2027-01-05T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
JT = 1000000


def jual(id, tgl, harga, kg=10, cara='Tunai', **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50,
         'hargaTotal': harga, 'hppTotalSaatJual': kg * 12000, 'trxId': 't-' + id, 'hargaAsliSatuan': harga}
    d.update(k); return d


def susun_kotak():
    """ANGKA CONTOH: toko contoh mulai mencatat 5 Jun 2026 (Jan–Mei = catatan lama 100 jt/bulan diketik owner). Jun–Des: nota tunai/QRIS/bon tiap 3 hari,
    potongan nota, tawar turun, nota tanpa modal, nota rugi, nota batal, retur, susut, biaya harian & bulanan, potongan QRIS, ambil pribadi, tutup hari (sebagian
    dengan isi tempat uang), kedatangan berutang + bayar sebagian. 2027: nota pertama 2 Jan (1 Jan libur)."""
    import datetime
    pj = []; n = 0; d = datetime.date(2026, 6, 5)
    while d <= datetime.date(2026, 12, 31):
        n += 1; t = d.isoformat(); i = n % 6; kg = 10 + (n % 4) * 5; harga = kg * (13600 + (n % 3) * 200)
        cara = ['Tunai', 'QRIS', 'Tunai', 'Kredit', 'QRIS', 'Tunai'][i]
        x = jual('n%03d' % n, t, harga, kg, cara, **({'namaPelanggan': 'Pelanggan Contoh ' + 'AB'[(n // 6) % 2]} if cara == 'Kredit' else {}))
        if n % 7 == 0: x['potonganTransaksi'] = 2000; x['hargaTotal'] = harga - 2000
        if n % 11 == 0: x['hargaAsliSatuan'] = harga + 5000; x['negoSelisih'] = -5000
        if n % 13 == 0: x['hppTotalSaatJual'] = 0
        if n % 17 == 0: x['hppTotalSaatJual'] = harga + 30000
        pj.append(x)
        if n % 9 == 0: pj.append(jual('m%03d' % n, t, 260000, 20, 'QRIS', jam='15:00', trxId='t-m%03d' % n))
        d += datetime.timedelta(days=3)
    for t, h in [('2026-12-28', 410000), ('2026-12-29', 275000), ('2026-12-30', 540000), ('2026-12-31', 820000)]:
        pj.append(jual('d' + t[-2:], t, h, 30, 'Tunai'))
    pj.append(jual('x1', '2026-11-11', 500000, 30, dibatalkan=True))
    pj += [jual('j1', '2027-01-02', 680000, 50), jual('j2', '2027-01-04', 410000, 30, 'QRIS'), jual('j3', '2027-01-05', 275000, 20, 'Kredit', namaPelanggan='Pelanggan Contoh A')]
    batch = [{'id': 'b1', 'tanggal': '2026-06-04', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
              'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 400, 'totalKg': 20000, 'hargaPerKg': 12000, 'subtotalHarga': 240000000}]},
             {'id': 'b2', 'tanggal': '2026-11-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 50000,
              'merkList': [{'id': 'b20', 'merk': 'Beo', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 100, 'totalKg': 5000, 'hargaPerKg': 13000, 'subtotalHarga': 65000000}]}]
    harian = []
    for b in range(6, 13):
        m = '2026-%02d' % b
        harian += [{'id': 'h-bensin-' + m, 'kategori': 'toko', 'tanggal': m + '-10', 'jam': '09:00', 'keterangan': 'Bensin antar', 'nominal': 40000 + b * 1000},
                   {'id': 'mdr-' + m + '-20', 'kategori': 'toko', 'tanggal': m + '-20', 'jam': '21:00', 'keterangan': 'Potongan QRIS', 'nominal': 1500 + b * 100, 'mdr': True, 'dari': 'rekening'},
                   {'id': 'h-kopi-' + m, 'kategori': 'toko', 'tanggal': m + '-12', 'jam': '10:00', 'keterangan': 'Kopi pekerja', 'nominal': 25000, 'untuk': 'karyawan'},
                   {'id': 'h-owner-' + m, 'kategori': 'owner', 'tanggal': m + '-25', 'jam': '19:00', 'keterangan': 'Belanja dapur rumah', 'nominal': 300000}]
    harian += [{'id': 'h-2027-1', 'kategori': 'toko', 'tanggal': '2027-01-03', 'jam': '09:00', 'keterangan': 'Bensin antar', 'nominal': 45000},
               {'id': 'h-2027-2', 'kategori': 'owner', 'tanggal': '2027-01-04', 'jam': '19:00', 'keterangan': 'Belanja dapur rumah', 'nominal': 200000}]
    bulanan = [{'id': m, 'bulan': m, 'listrik': 400000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': m + '-05'}, 'rincianGaji': [{'nama': 'Pekerja Contoh', 'hari': 26, 'gaji': 1560000}],
                'tanggalBayarGaji': {'Pekerja Contoh': m + '-28'}, 'gaji': 1560000, 'gajiHariOrang': 26} for m in ['2026-10', '2026-11', '2026-12']]
    tutup = [{'id': t, 'tanggal': t, 'jam': '21:00', 'omzet': 0, 'kasFisikLaci': 0} for t in ['2026-06-05', '2026-07-05', '2026-08-04', '2026-09-03', '2026-10-03']]
    tutup += [{'id': '2026-11-30', 'tanggal': '2026-11-30', 'jam': '21:00', 'selisihLaci': 0, 'titik': {'laci': 2500000, 'rekening': 9000000, 'amplop': 0, 'brankas': 12000000}},
              {'id': '2026-12-30', 'tanggal': '2026-12-30', 'jam': '21:00', 'selisihLaci': 20000, 'titik': {'laci': 2700000, 'rekening': 9500000, 'amplop': 0, 'brankas': 12500000}},
              {'id': '2026-12-31', 'tanggal': '2026-12-31', 'jam': '21:00', 'selisihLaci': -5000, 'titik': {'laci': 2800000, 'rekening': 9600000, 'amplop': 0, 'brankas': 12500000}}]
    return {
        'penjualan': pj, 'batchMasuk': batch, 'pengeluaranHarian': harian, 'biayaBulanan': bulanan, 'tutupHari': tutup,
        'retur': [{'id': 'rt1', 'tanggal': '2026-11-20', 'jam': '11:00', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 5, 'jumlahKarung': 0.1, 'beratKarungAcuan': 50, 'kondisi': 'tidak_utuh',
                   'penyelesaian': 'refund', 'nominalRefund': 70000, 'nilaiDikembalikan': 70000, 'notaAsalId': 'n001', 'notaAsalTanggal': '2026-06-05', 'catatan': 'basah'},
                  {'id': 'rt2', 'tanggal': '2026-12-30', 'jam': '11:00', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 5, 'jumlahKarung': 0.1, 'beratKarungAcuan': 50, 'kondisi': 'tidak_utuh',
                   'penyelesaian': 'refund', 'nominalRefund': 68000, 'nilaiDikembalikan': 68000, 'notaAsalId': 'd29', 'notaAsalTanggal': '2026-12-29', 'catatan': 'kutu'}],
        'karantina': [{'id': 'rt1', 'tanggal': '2026-11-20', 'asalRetur': True, 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 5, 'statusTindakan': 'dibuang', 'catatan': 'basah'},
                      {'id': 'rt2', 'tanggal': '2026-12-30', 'asalRetur': True, 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 5, 'statusTindakan': 'dibuang', 'catatan': 'kutu'}],
        'penyesuaianStok': [{'id': 'ps1', 'tanggal': '2026-10-15', 'jam': '20:00', 'merk': 'Angsa', 'selisihKg': -12, 'nilaiRp': -144000, 'alasan': 'tercecer'}],
        'piutangMutasi': [{'id': 'pb1', 'tipe': 'bayar', 'namaPelanggan': 'Pelanggan Contoh A', 'nominal': 150000, 'tanggal': '2026-12-15', 'jam': '10:00', 'caraBayar': 'Tunai'}],
        'utangPemasokMutasi': [{'id': 'ub1', 'tipe': 'bayar', 'pemasok': 'PEMASOK CONTOH', 'nominal': 20000000, 'tanggal': '2026-12-01', 'jam': '10:00', 'bonTanggal': '2026-11-10', 'dari': 'rekening'}],
        'modalOwner': [{'id': 'mo1', 'tanggal': '2026-06-01', 'jam': '08:00', 'tipe': 'setor', 'nominal': 250000000, 'catatan': 'modal awal contoh'}],
        'aturanToko': [], 'pajakOmzetLuar': [], 'pajakSetoran': [], 'tutupBukuAcara': [], 'pengaturan': [], 'dokumenCetak': [], 'produksiKemasan': [], 'stokBahanKemasan': [], 'stokBahanLiteran': [],
        'kasbonMutasi': [], 'slipUpah': [], 'absenKaryawan': [], 'pindahUang': [], 'amplopLaba': [], 'utangOwnerMutasi': [], 'setoranKas': [], 'penyesuaianKemasan': [], 'pesanan': [],
        'pelangganCatatan': [], 'pemasokCatatan': [], 'thrPelanggan': [], 'tembusanStok': [], 'tagihPelanggan': [], 'strukKeluar': [], 'wadahLiteran': [], 'perangkatStatus': [],
    }


KOTAK = susun_kotak()

BERSAMA = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(typeof ket === 'string' ? ket : J(ket)).slice(0, 500) : '')); }
function coba(nama, f) { try { f(); } catch (e) { gagal.push(nama + ' → JATUH: ' + (e && e.message ? e.message : e) + ' ' + String(e && e.stack || '').split('\n').slice(0, 2).join(' / ')); } }
var nId = 70000; function jam(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: iso.slice(11, 16), kini: new Date(iso).toISOString(), idUnik: function () { nId += 1; return 'u' + nId; } }; }
var LA = { idPerangkat: 'mac-contoh', namaPerangkat: 'Mac contoh', antre: [], menunggu: 0, offline: false };
var D = { paraf: { owner: true, saksi: true }, saksi: 'Saksi Contoh', langkah: {} };
function kirim(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) throw new Error('penjaga pusat menolak: ' + j.pesan);
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); }
function tulis(r) { if (!r || r.tolak) throw new Error('DITOLAK: ' + (r && r.tolak)); kirim({ dokumen: r.dokumen || [], hapus: r.hapus || [] }); return r; }
function acara(tahun) { return ambilTutupBukuAcara().filter(function (a) { return Number(a.tahun) === tahun; })[0] || null; }
var BLN26 = []; for (var m = 1; m <= 12; m++) BLN26.push('2026-' + String(m).padStart(2, '0'));
var akhirB = function (k) { return akhirBulanIso(k); };
/** Hari berjualan tanpa tutup hari diputus "diterima apa adanya" (A1) — tanpa putusan susunKunci menolak di pintu masuk (g1). */
function putusSemua(w) { var G = gerbangBuku(2026, new Date(__KINI), LA, { g3: true }); if (!G.belumPutus.length) return 0; var isi = {}; G.belumPutus.forEach(function (t) { isi[t] = 'contoh: hari tanpa tutup hari, diterima apa adanya'; }); tulis(susunPutusanHari(isi, w)); return G.belumPutus.length; }
/** Ritual tutup buku 2026 penuh (kunci → semua kiriman → arsip habis). */
function ritual(w) { putusSemua(w); var R = susunKunci(2026, D, w, LA); if (R.tolak) return R; R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar); return R; }
/** Firestore menerima: tanpa undefined / fungsi / NaN / Infinity, tanpa larik langsung di dalam larik, kunci peta tidak kosong & bukan __x__. → daftar pelanggaran. */
function bentukFirestore(o, jalur, out) { out = out || []; jalur = jalur || '';
  if (o === undefined) out.push(jalur + ' undefined'); else if (typeof o === 'function') out.push(jalur + ' fungsi'); else if (typeof o === 'number' && !isFinite(o)) out.push(jalur + ' ' + o);
  else if (Array.isArray(o)) o.forEach(function (x, i) { if (Array.isArray(x)) out.push(jalur + '[' + i + '] larik di dalam larik'); bentukFirestore(x, jalur + '[' + i + ']', out); });
  else if (o && typeof o === 'object') Object.keys(o).forEach(function (k) { if (!k || /^__.*__$/.test(k)) out.push(jalur + ' kunci "' + k + '"'); bentukFirestore(o[k], jalur + '.' + k, out); });
  return out; }

/** Angka semua layar untuk tahun 2026 pada jam `kini` — dipanggil SEBELUM dan SESUDAH ritual dengan fungsi yang sama. */
function layar(kini) {
  var o = {}; var T = pjTahun(2026, kini);
  o.pajak = T.daftar.map(function (b) { return [b.key, b.sistem, b.nNota, b.sebelumPotongan, b.potongan ? b.potongan.nota + '/' + b.potongan.tawar : null, b.lama, b.omzet, b.kum, b.kumGabung, b.kena, b.pph, b.lengkap, b.sebagian, b.tempo].join('|'); });
  o.pajakJumlah = [T.totalSistem, T.totalSebelumPotongan, T.totalPph, T.kosong, T.awalSistem, T.kum].join('|');
  var DR = dokRekapPajak(T, { nama: 'Toko Contoh', alamat: 'Jl. Contoh', versi: 1 }); o.rekapPajak = DR.baris.filter(function (b) { return !/^Per bulan|^  setoran|Sumber aturan|^\[BELUM/.test(b.nama); }).map(function (b) { return b.nama + '=' + b.teks; });
  o.dk3 = rekapOmzet(kini).daftar.filter(function (b) { return b.key < '2027'; }).map(function (b) { return [b.key, b.omzet, b.n, b.absen, b.perkiraan, b.perkiraanLengkap].join('|'); });
  o.laba = BLN26.map(function (k) { var B = labaBulan(k, kini); return J([B.L.omzetPenuh, B.L.omzetHitung, B.L.hpp, B.margin, B.labaBersih, B.tunai, B.marginKredit, B.omzetKredit, B.nKredit, B.marginDibayar, B.marginDihapus, B.marginDiretur || 0, B.mdr, B.biayaLain, B.cakupan, B.omzetKotor, B.penyebut, B.omzetTanpaHpp, B.susutTotal, B.tanpaCatatan, B.terjun]); });
  o.labaDaftar = BLN26.map(function (k) { var B = labaBulan(k, kini); var A = B.dalamArsip; return A ? [A.nRugi, A.nRugiNota, A.rugiRp, A.nTanpaHpp, A.nTanpaHppNota, A.nSusut].join('|') : [B.rugi.length, new Set(B.rugi.map(function (p) { return p.nota; })).size, B.rugi.reduce(function (a, p) { return a + p.margin; }, 0), B.tanpaHpp.length, new Set(B.tanpaHpp.map(function (p) { return p.nota; })).size, B.susut.length].join('|'); });
  o.keMana = BLN26.map(function (k) { var M = keManaLabaKotor(k, kini); return J([M.baris.map(function (r) { return [r.id, r.n, r.ket]; }), M.menutup, M.tanpaCatatan, M.pct(M.biayaToko)]); });
  o.inti = BLN26.map(function (k) { var I = intiBulan(k, kini); return J([I.omzet, I.rataHari, I.hpp, I.margin, I.biayaToko, I.labaBersih, I.keluar, I.masuk, I.bersih, I.kredit, I.belumBayarTotal]); });
  o.biaya = BLN26.map(function (k) { var K = kendaliBulan(k, kini); var P = pemicuBiaya(K); var TI = titikImpas(K, kini);
    return J([K.baris.map(function (r) { return [r.id, r.n, r.jumlah, r.nLalu, r.acuan, r.delta]; }), K.semuaBiaya, K.kgTerjual, K.kgHitung, K.menutup, K.tanpaCatatan, P.baris.map(function (r) { return [r.id, r.n, r.nLalu]; }), [TI.omzetImpas, TI.menutupKini, TI.labaSampai, TI.teks]]); });
  var RT = rekapTahun(2026, kini); o.tahun = J([RT.bulan.map(function (b) { return [b.key, b.omzet, b.n, b.margin, b.biaya, b.labaBersih, b.susut, b.kas, b.hpp, b.sebelumBuku]; }), RT.omzet, RT.n, RT.hpp, RT.margin, RT.biaya, RT.labaBersih, RT.susut, RT.lebihKurangKas, RT.cocokJumlah, RT.bulanJalan, RT.rataBulan]);
  o.berkop = [];
  BLN26.slice(5).forEach(function (k) { [1, 3].forEach(function (n) { var LB = laporanBerkop('labarugi', k, n, kini); o.berkop.push(k + '/' + n + ': ' + LB.baris.map(function (r) { return r.nama + '=' + r.teks; }).join('; ') + ' | ' + LB.catatan); }); });
  var L12 = laporanBerkop('labarugi', '2026-12', 12, kini); o.berkop.push('12: ' + L12.baris.map(function (r) { return r.nama + '=' + r.teks; }).join('; ') + ' | ' + L12.catatan);
  o.arus = ['2026-10', '2026-12'].map(function (k) { return laporanBerkop('aruskas', k, 3, kini).baris.filter(function (r) { return !/^Kas awal|^Kas akhir|^Penyesuaian|^Lebih\/kurang/.test(r.nama); }).map(function (r) { return r.nama + '=' + r.teks; }).join('; '); });
  o.neraca = BLN26.slice(5).map(function (k) { var NP = neracaPada(akhirB(k), kini, lpKasAkhirBulan(k)); return J([NP.total, NP.aset, NP.kewajiban, NP.modal, NP.labaDitahan, NP.labaKum, NP.prive, NP.menurutMesin, NP.selisihBuku, NP.harta.map(function (r) { return r.n; }), NP.pasiva.map(function (r) { return r.n; }), NP.tolak, NP.catatan]); });
  o.kasAkhir = BLN26.slice(5).map(function (k) { var X = lpKasAkhirBulan(k); return [X.kas, X.sumber, X.tolak].join('|'); });
  var NK = neracaPada(null, kini); o.neracaKini = J([NK.labaKum, NK.prive, NK.menurutMesin]);
  o.hari = hariTerakhir(kini, 14).map(function (x) { return [x.iso, x.n, x.omzet].join('|'); });
  o.minggu = [lpSenin('2026-12-21'), lpSenin('2026-12-28')].map(function (a) { var R = rekapMinggu(a, kini); return J([R.hari.map(function (d) { return [d.iso, d.omzet, d.n, d.margin]; }), R.omzet, R.n, R.margin, R.jumlahTanpaHpp, R.lalu, R.cocokJumlah]); });
  o.tren = ['hari', 'minggu', 'bulan'].map(function (r) { return dbTren(r, kini).batang.map(function (b) { return [b.id, b.omzet, b.margin, b.nota, b.tanpaHpp, b.retur, b.absen].join('|'); }).join(' ; '); });
  var BI = dbBulanIni(kini); o.bulanIni = J([BI.biaya.map(function (r) { return [r.id, r.nLalu]; }), BI.pemicu.map(function (p) { return [p.id, p.teksLalu]; }), BI.pendekLalu]);
  o.rekapHari = ['2026-12-30', '2026-12-31', '2026-11-20'].map(function (t) { var R = rekapHari(t); return [R.omzet, R.n, R.margin, R.jumlahTanpaHpp, R.retur].join('|'); });
  o.lalu = [rekapTahun(2027, kini).lalu, lpOmzetTahun(2026)].join('|');
  o.enam = enamBulan(kini).daftar.map(function (b) { return [b.key, b.omzet, b.n].join('|'); });
  o.banding = J(bandingLabaRugi('2026-12', '2026-11', kini).baris.map(function (r) { return [r.nama, r.a, r.b, r.d]; }));
  return o;
}
function beda(a, b) { var out = []; Object.keys(a).forEach(function (k) { var x = J(a[k]), y = J(b[k]); if (x !== y) { var xa = Array.isArray(a[k]) ? a[k] : [x], ya = Array.isArray(b[k]) ? b[k] : [y]; var i = 0; while (i < xa.length && J(xa[i]) === J(ya[i])) i++; out.push(k + '[' + i + ']: ' + String(J(xa[i])).slice(0, 260) + '  ≠  ' + String(J(ya[i])).slice(0, 260)); } }); return out; }
function persiapkan(w) {
  KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []);
  __ls = {}; __dom['jualKarungBerat'] = { value: '50' }; localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-06-01', laci: 1000000, brankas: 5000000, rekening: 3000000, amplop: 0 }));
  // pajak contoh: aturan dari tombol (tahun pajak 2026), catatan lama Jan–Mei 100 jt + Jun tgl 1–4, setoran Jul ber-NTPN
  var w26 = jam('2026-12-20T10:00:00+07:00'); tulis(susunPakaiAturan(w26));
  ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05'].forEach(function (b) { tulis(susunOmzetLuar({ bulan: b, sumber: 'catatanLama', jumlah: '100.000.000', keterangan: 'buku contoh' }, w26)); });
  tulis(susunOmzetLuar({ bulan: '2026-06', sumber: 'catatanLama', jumlah: '2.000.000', keterangan: 'tanggal 1–4 Juni dari buku contoh' }, w26));
  jam(w.kini); return w;
}
"""

SKENARIO = r"""
// ==================== P1 + P2 · ritual 5 Jan 2027, banding 5 Jan & 31 Mar ====================
var W5, S5, S31, R;
coba('P1-P2', function () {
  W5 = persiapkan(jam('2027-01-05T10:00:00+07:00'));
  var setorJul = susunSetoran({ masaPajak: '2026-07', tanggalSetor: '2026-08-14', jumlah: String(pjTahun(2026, new Date(__KINI)).daftar[6].pph), ntpn: 'AB12CD34EF56GH78', catatan: 'bukti kertas contoh' }, W5, new Date(__KINI)); tulis(setorJul);
  var k5 = new Date(__KINI); S5 = layar(k5); jam('2027-03-31T10:00:00+07:00'); S31 = layar(new Date(__KINI)); W5 = jam('2027-01-05T10:00:00+07:00');
  ok('kotak pasir masuk akal: 2026 punya omzet sistem tiap bulan Jun–Des, PPh dihitung (aturan dari tombol), Jan–Mei catatan lama; layar sebelum ritual tidak Rp0',
    pjTahun(2026, k5).daftar.slice(5).every(function (b) { return b.sistem > 0; }) && pjTahun(2026, k5).totalPph > 0 && pjTahun(2026, k5).lengkap && S5.hari.length === 14, J(S5.pajak));
  ok('LATIHAN menyusun potret tanpa menulis apa pun (kalimat ringkas, ukuran) — kunci sungguhan memakai fungsi yang sama', (function () { var n0 = ambilTutupBukuAcara().length; var PL = potretLatihan(2026, k5); return PL.ok && /^Potret 2026: 12 bulan & \d+ hari berjualan · omzet sistem Rp/.test(PL.teks) && /neraca 31 Des Rp/.test(PL.teks) && ambilTutupBukuAcara().length === n0 && PL.ukuran > 1000; })(), potretLatihan(2026, k5).teks);
  R = ritual(W5);
  ok('ritual 5 Jan 2027 tidak ditolak; berita acara membawa potret 2026 (versi 1, 12 bulan, hari berjualan, nota pertama sistem 5 Jun, catatan pertama 4 Jun)', !R.tolak && !!R.acara.potret && R.acara.potret.versi === 1 && Object.keys(R.acara.potret.bulan).length === 12 && Object.keys(R.acara.potret.hari).length > 50 && R.acara.potret.awalSistem === '2026-06-05' && R.acara.potret.pertama === '2026-06-04', R.tolak || J(Object.keys(R.acara.potret || {})));
  var adaDiKiriman = R.kiriman.map(function (k) { return k.dokumen.filter(function (x) { return x.koleksi === 'tutupBukuAcara'; }).map(function (x) { return x.data.status + ':' + !!x.data.potret; }).join(','); }).filter(Boolean);
  ok('potret ikut SEMUA tulisan berita acara (berjalan / terkunci) di kiriman', adaDiKiriman.length >= 1 && adaDiKiriman.every(function (s) { return s.split(',').every(function (x) { return /:true$/.test(x); }); }), J(adaDiKiriman));
  var BF = bentukFirestore(acara(2026)); var ukuran = J(acara(2026)).length;
  ok('bentuk potret diterima Firestore (tanpa undefined/fungsi/NaN, tanpa larik di dalam larik); ukuran berita acara jauh di bawah 1 MiB', !BF.length && ukuran < 400000, J([BF.slice(0, 5), ukuran]));
  ok('arsip habis: tidak ada penjualan 2026 di catatan hidup; tahun 2026 DIARSIP & ber-potret; status berita acara terkunci', ambilPenjualanSemua().every(function (p) { return p.tanggal > '2026-12-31'; }) && tahunDiarsip(2026) && !!potretTahun(2026) && acara(2026).status === 'terkunci' && !tahunDiarsip(2027), J(ambilPenjualanSemua().map(function (p) { return p.tanggal; })));
  var A5 = layar(new Date(__KINI)); var b5 = beda(S5, A5);
  ok('5 Jan 2027: SEMUA layar 2026 sesudah ritual = sebelum ritual (Pajak, rekap konsultan, DK3, Laba, ke mana, inti, Biaya, Tahunan, laporan berkop, arus kas, neraca akhir bulan, kas akhir bulan, neraca hari ini, Harian, Mingguan, Dasbor, Bulan ini, Bulanan, Banding)', !b5.length, b5.slice(0, 6));
  jam('2027-03-31T10:00:00+07:00'); var A31 = layar(new Date(__KINI)); var b31 = beda(S31, A31); W5 = jam('2027-01-05T10:00:00+07:00');
  ok('31 Mar 2027: semua layar 2026 sesudah ritual = sebelum ritual', !b31.length, b31.slice(0, 6));
  ok('tidak ada Rp0 bertanda FINAL: omzet Pajak & DK3 2026 sesudah arsip > 0 tiap bulan Jun–Des, bulan 2026 FINAL', pjTahun(2026, new Date(__KINI)).daftar.slice(5).every(function (b) { return b.sistem > 0 && b.dariPotret; }) && rekapOmzet(new Date(__KINI)).daftar.filter(function (b) { return b.key >= '2026-06' && b.key <= '2026-12'; }).every(function (b) { return b.omzet > 0 && b.final; }));
  var BO = buktiOmzet({ '2026-11': true, '2026-12': true }, new Date(__KINI)); var sb = S5.dk3.filter(function (x) { return /^2026-1[12]\|/.test(x); }).map(function (x) { return Number(x.split('|')[1]); });
  ok('Bukti omzet Nov–Des 2026 (final sesudah tutup buku) = omzet sebelum ritual, tidak ditolak', !BO.tolak && BO.total === sb[0] + sb[1] && BO.baris.every(function (b) { return b.tanda === 'final'; }), J([BO.tolak, BO.total, sb]));
  var NP = neracaTanggal('2026-12-15', new Date(__KINI), true); var N31 = neracaTanggal('2026-12-31', new Date(__KINI), true);
  ok('Neraca: 31 Des 2026 dari potret (sama dengan sebelum ritual), 15 Des 2026 ditolak dengan sebab yang benar (diarsip, pilih akhir bulan) — bukan "titik kas"', N31.total !== null && J(N31.total) === J(JSON.parse(S5.neraca[6])[0]) && /sudah diarsip \(tutup buku 2026\); yang tersimpan neraca akhir tiap bulan\. Pilih 31 Des 2026/.test(NP.tolak) && !/titik kas/.test(NP.tolak), J([N31.total, NP.tolak]));
  var RH = rekapHari('2026-12-30');
  ok('Harian 30 Des 2026: omzet, nota & margin dari potret, rincian uang/arus kas/buku kas ikut arsip (null, bukan Rp0)', RH.diarsip && RH.omzet > 0 && RH.tunai === null && RH.bersih === null && !RH.buku.length, J(RH));
  var RM = rekapMinggu(lpSenin('2026-12-28'), new Date(__KINI));
  ok('Mingguan 28 Des – 3 Jan: 4 hari dari potret, laba bersih & arus kas minggu itu tidak disusun (null) dan disebut', RM.diarsip === 4 && RM.labaBersih === null && RM.bersih === null && RM.hari.filter(function (d) { return d.diarsip; }).length === 4, J([RM.diarsip, RM.labaBersih]));
  var KJ = kendaliBulan('2026-12', new Date(__KINI)); var PA = paretoBiaya(KJ);
  ok('Biaya Desember 2026: per jenis dari potret, pareto menyebut rincian sudah diarsip (bukan "Belum ada biaya tercatat")', KJ.diarsip && PA.diarsip && /sudah diarsip \(tutup buku\)/.test(PA.teks) && !/Belum ada biaya/.test(PA.teks), PA.teks);
});

// ==================== P1b · potret gagal disusun → kunci DITOLAK; latihan menyebutnya ====================
coba('P1b', function () {
  var w = persiapkan(jam('2027-01-05T10:00:00+07:00')); putusSemua(w); var asli = susunPotret; susunPotret = function () { throw new Error('kotak pasir: mesin potret rusak'); };
  try { var Rx = susunKunci(2026, D, w, LA); var PL = potretLatihan(2026, new Date(__KINI));
    ok('potret gagal disusun → kunci DITOLAK menyebut sebabnya (tanpa potret laporan & pajak 2026 jadi Rp0 sesudah arsip); tidak ada yang ditulis', !!Rx.tolak && /Potret 2026 gagal disusun \(kotak pasir: mesin potret rusak\) — tahun TIDAK dikunci/.test(Rx.tolak) && !Rx.kiriman && !acara(2026), Rx.tolak);
    ok('latihan menyebut potret gagal (ketahuan sebelum ritual), bukan diam', !PL.ok && /Potret 2026 GAGAL disusun: kotak pasir: mesin potret rusak/.test(PL.teks), PL.teks);
  } finally { susunPotret = asli; }
});

// ==================== P3 · setoran masa Desember 2026 dicatat Januari ====================
coba('P3', function () {
  var w = jam('2027-01-10T10:00:00+07:00'); var k = new Date(__KINI); var Des0 = S5.pajak[11].split('|'); var pph = Number(Des0[10]);
  var r = susunSetoran({ masaPajak: '2026-12', tanggalSetor: '2027-01-10', jumlah: String(pph), ntpn: '1234ABCD5678EFGH' }, w, k); tulis(r);
  var s = cacheMentah('pajakSetoran').filter(function (x) { return x.masaPajak === '2026-12'; })[0]; var B = pjTahun(2026, k).daftar[11];
  ok('setoran masa 2026-12 tersimpan 10 Jan 2027 (sesudah ritual): potret omzet & perkiraan saat setor = angka sebelum ritual; status "disetor" (bukan "berubah"), ber-NTPN', !!s && s.omzetSaatSetor === Number(Des0[6]) && s.pphPerkiraanSaatSetor === pph && B.status.kode === 'disetor' && /NTPN 1234ABCD5678EFGH/.test(B.status.teks), J([s, B.status]));
  ok('peringatan kunci setoran Desember menyebut tutup buku, bukan "kunci bulan dulu"', /bergeser sampai tutup buku 2026|tutup buku/.test(r.peringatan || pjPeringatanKunci('2026-12')) || r.peringatan === '', r.peringatan);
});

// ==================== P4 · pilih tahun, bawaan Jan–Mar, Beranda & pengingat ====================
coba('P4', function () {
  persiapkan(jam('2027-01-05T10:00:00+07:00')); var w = jam('2027-01-05T10:00:00+07:00'); R = ritual(w);
  var k = new Date(__KINI); var DT = pjDaftarTahun(k);
  ok('daftar tahun Pajak 5 Jan 2027: 2027 (berjalan) & 2026 (tutup buku, ber-potret)', DT.length === 2 && DT[0].tahun === 2027 && DT[0].berjalan && DT[1].tahun === 2026 && DT[1].potret && DT[1].ditutup, J(DT));
  ok('bawaan 5 Jan 2027 = 2026 (masa Desember terutang); pil masa & omzet di luar sistem tahun 2026 = 12 bulan', pjTahunBawaan(k) === 2026 && pjTahun(2026, k).daftar.length === 12 && pjTahun(2027, k).daftar.length === 1, J([pjTahunBawaan(k)]));
  var PH = pjPerhatian(jam('2027-01-20T10:00:00+07:00') && new Date(__KINI));
  ok('Beranda 20 Jan 2027: menyebut masa tahun lalu yang lewat tempo (Des 26, tempo 15 Jan)', PH.length === 1 && /lewat tempo [^·]*Des 26/.test(PH[0].teks), J(PH));
  jam('2027-02-05T10:00:00+07:00'); var SG = pjSumberPengingat(new Date(__KINI));
  ok('pengingat 5 Feb 2027 masih menyebut "Setor PPh final Desember 2026" (dulu hilang begitu Februari)', SG.some(function (x) { return x.kunci === '2026-12' && /Desember 2026/.test(x.teks) && x.jatuh === '2027-01-15'; }), J(SG.map(function (x) { return x.kunci; })));
  // semua masa 2026 disetor → bawaan Januari kembali ke tahun berjalan
  var w2 = jam('2027-01-12T10:00:00+07:00'); pjTahun(2026, new Date(__KINI)).daftar.forEach(function (b) { if (b.pph > 0 && b.jumlahSetor < b.pph) tulis(susunSetoran({ masaPajak: b.key, tanggalSetor: '2027-01-12', jumlah: String(b.pph - b.jumlahSetor), ntpn: 'ZZZZ0000ZZZZ' + b.key.slice(5, 7) + '00', catatan: 'contoh: dicatat mundur' }, w2, new Date(__KINI))); });
  ok('semua masa 2026 disetor → bawaan 12 Jan = 2027; 31 Mar tetap 2027; daftar tetap memuat 2026', pjTahunBawaan(new Date(__KINI)) === 2027 && pjTahunBawaan(jam('2027-03-31T10:00:00+07:00') && new Date(__KINI)) === 2027 && pjDaftarTahun(new Date(__KINI)).some(function (x) { return x.tahun === 2026; }));
  // masih terutang di 31 Mar → bawaan 2026; 1 Apr → 2027
  persiapkan(jam('2027-03-31T10:00:00+07:00')); R = ritual(jam('2027-03-31T10:00:00+07:00'));
  ok('ritual terlambat 31 Mar 2027 tetap jalan; bawaan 31 Mar = 2026 (masih terutang), 1 Apr = 2027', !R.tolak && pjTahunBawaan(new Date(__KINI)) === 2026 && pjTahunBawaan(jam('2027-04-01T10:00:00+07:00') && new Date(__KINI)) === 2027, R.tolak);
  var DR = dokRekapPajak(pjTahun(2026, jam('2027-03-31T10:00:00+07:00') && new Date(__KINI)), { nama: 'Toko Contoh', alamat: 'Jl. Contoh', versi: 1 });
  ok('Rekap pajak 2026 untuk konsultan bisa dicetak 31 Mar 2027: 12 bulan, "potret tutup buku 2026", "Omzet tahun 2025", sumber aturan diperiksa untuk 2026', DR.periode === '2026' && DR.baris.some(function (b) { return /^Per bulan 2026 · angka sistem dari potret tutup buku 2026$/.test(b.nama); }) && DR.baris.some(function (b) { return b.nama === 'Omzet tahun 2025'; }) && DR.baris.some(function (b) { return /diperiksa untuk tahun pajak 2026/.test(b.nama); }) && DR.baris.filter(function (b) { return /^(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember) 2026/.test(b.nama); }).length === 12, J(DR.baris.slice(0, 4)));
});

// ==================== P5 · Januari 2027 tidak "belum lengkap" (R4) ====================
coba('P5', function () {
  persiapkan(jam('2027-01-05T10:00:00+07:00')); R = ritual(jam('2027-01-05T10:00:00+07:00')); var k = new Date(__KINI); var J1 = pjTahun(2027, k).daftar[0];
  ok('dengan potret: nota pertama 2027 tanggal 2 Jan (1 Jan libur) — Januari 2027 LENGKAP, bukan "sebagian"; awal sistem = nota pertama sepanjang masa', J1.lengkap && !J1.sebagian && pjAwalSistem() === '2026-06-05', J([J1.lengkap, J1.sebagian, pjAwalSistem()]));
  var DP = kpDaftarPeriksa('2027-01', jam('2027-02-05T10:00:00+07:00') && new Date(__KINI), { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} }); var bl = DP.butir.filter(function (b) { return b.id === 'omzetLuar'; })[0];
  ok('daftar periksa kunci Januari 2027: butir omzet di luar sistem "sudah diisi / tidak perlu" (tidak minta centang)', !!bl && bl.ok && !bl.perluCentang, J(bl));
  // tanpa potret (tahun ditutup sistem ini sebelum Paket B): tahun sesudahnya tetap tercatat sejak 1 Januari
  terapkanKeCache([{ koleksi: 'tutupBukuAcara', data: (function () { var a = Object.assign({}, acara(2026)); delete a.potret; return a; })() }]);
  var J2 = pjTahun(2027, jam('2027-01-05T10:00:00+07:00') && new Date(__KINI)).daftar[0];
  ok('tanpa potret: awal sistem = 1 Jan 2027 (tahun sesudah tutup buku), Januari 2027 tetap LENGKAP', pjAwalSistem() === '2027-01-01' && J2.lengkap && !J2.sebagian, J([pjAwalSistem(), J2.lengkap]));
});

// ==================== P6 · batalkan tutup buku ====================
coba('P6', function () {
  var w = persiapkan(jam('2027-01-05T10:00:00+07:00')); S5 = layar(new Date(__KINI)); R = ritual(w);
  var BT = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }; }), w, LA);
  if (BT.tolak) throw new Error('batal ditolak: ' + BT.tolak); BT.kiriman.forEach(kirim); pulihkanArsip(2026, BT.pulih); kirim({ dokumen: [BT.akhir] });
  var A = layar(new Date(__KINI)); var b = beda(S5, A);
  ok('Batalkan: berita acara dibatalkan → potret TIDAK dibaca lagi (tahun 2026 tidak diarsip), angka dari catatan hidup = sebelum ritual', acara(2026).status === 'dibatalkan' && !tahunDiarsip(2026) && !potretTahun(2026) && !b.length, b.slice(0, 4));
  var des0 = pjOmzetSistem('2026-12').omzet; terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'koreksi-des', tanggal: '2026-12-20', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 10, beratKarungAcuan: 50, jumlahKarung: 0.2, hargaTotal: 140000, hppTotalSaatJual: 120000, trxId: 't-koreksi-des' } }]);
  ok('sesudah Batalkan, nota Desember yang dicatat untuk membetulkan TAMPIL di Pajak & Laporan (catatan hidup, bukan potret beku)', pjOmzetSistem('2026-12').omzet === des0 + 140000 && labaBulan('2026-12', new Date(__KINI)).L.omzetPenuh === des0 + 140000 && pjTahun(2026, new Date(__KINI)).daftar[11].sistem === des0 + 140000, J([des0, pjOmzetSistem('2026-12').omzet]));
});

// ==================== P7 · tahun ditutup TANPA potret ====================
coba('P7', function () {
  var w = persiapkan(jam('2027-01-05T10:00:00+07:00')); R = ritual(w);
  terapkanKeCache([{ koleksi: 'tutupBukuAcara', data: (function () { var a = Object.assign({}, acara(2026)); delete a.potret; return a; })() }]); var k = new Date(__KINI);
  var BO = buktiOmzet({ '2026-11': true }, k); var RO = rekapOmzet(k); var LB = laporanBerkop('labarugi', '2026-12', 3, k); var NP = neracaTanggal('2026-12-31', k, true); var T = pjTahun(2026, k); var RT = rekapTahun(2026, k);
  ok('tanpa potret: Bukti omzet 2026 DITOLAK (bukan Rp0 final)', /tidak punya angka omzet di sistem \(tahunnya ditutup tanpa potret/.test(BO.tolak || ''), BO.tolak);
  ok('tanpa potret: DK3 menandai bulan 2026 "tanpaPotret"; laporan berkop & neraca 31 Des menolak dengan sebabnya', RO.daftar.filter(function (b) { return b.key >= '2026-02' && b.key <= '2026-12'; }).every(function (b) { return b.tanpaPotret; }) && /sudah tutup buku tanpa potret/.test(LB.tolak) && /tanpa potret/.test(NP.tolak) && NP.total === null, J([LB.tolak, NP.tolak]));
  ok('tanpa potret: Pajak 2026 tidak memakai Rp0 sistem — bulan berlabel diarsip tanpa potret, tahun bertanda tanpaPotret; Tahunan 2026 "—" per bulan, bukan Rp0', T.tanpaPotret && T.daftar.every(function (b) { return b.tanpaPotret && b.sistem === null; }) && RT.bulan.every(function (b) { return b.tanpaPotret && b.omzet === null; }) && /TANPA potret/.test(RT.status), J([T.tanpaPotret, RT.status]));
});

// ==================== P8 · omzet tahun lalu per tahun, aturan berlabel tahun ====================
coba('P8', function () {
  var w = persiapkan(jam('2027-01-05T10:00:00+07:00')); R = ritual(w); var k = new Date(__KINI);
  var TW = pjTawarOmzetTahunLalu(2027, k); var T26 = pjTahun(2026, k);
  ok('tawaran omzet 2026 untuk profil 2027 = kumulatif gabung Pajak 2026 (potret + isian luar), lengkap', !!TW && TW.tahun === 2026 && TW.n === T26.kumGabung && TW.lengkap && TW.potret, J(TW));
  tulis(susunOmzetTahunLaluDariSistem(2027, w, k)); var P = pjProfil();
  ok('dipakai: tersimpan per tahun (omzetTahunan 2026), tawaran hilang, Pajak 2027 membaca omzet 2026 itu; 2026 tetap membaca 2025 (kosong)', P.omzetTahunan['2026'] === T26.kumGabung && !pjTawarOmzetTahunLalu(2027, k) && pjTahun(2027, k).omzetTahunLalu === T26.kumGabung && pjTahun(2026, k).omzetTahunLalu === null, J(P.omzetTahunan));
  var A27 = pjTahun(2027, k).aturanTahun; var A26 = pjTahun(2026, k).aturanTahun;
  ok('aturan dari tombol diisi untuk tahun pajak 2026 → layar 2027 diberi peringatan "belum diperiksa", 2026 tidak; tombol dari layar 2027 → peringatan hilang', A27.belum && /diisi untuk tahun 2026 — tahun 2027 belum diperiksa/.test(A27.teks) && !A26.belum && (function () { tulis(susunPakaiAturan(w, 2027)); return !pjTahun(2027, k).aturanTahun.belum && !pjTahun(2026, k).aturanTahun.belum; })(), J([A27, A26]));
  var DR = dokRekapPajak(pjTahun(2027, k), { nama: 'Toko Contoh', alamat: 'Jl. Contoh', versi: 1 });
  ok('rekap 2027 mencetak "Omzet tahun 2026" (angka per tahun), bukan "Omzet tahun lalu"', DR.baris.some(function (b) { return b.nama === 'Omzet tahun 2026' && b.teks === RP(T26.kumGabung); }) && !DR.baris.some(function (b) { return b.nama === 'Omzet tahun lalu'; }));
});
"""

STATIS_LAYAR = [
    ('Pajak memakai tahun pilihan (bukan tahun berjalan saja)', "  function gambarPajak(s, L) {\n    const T = PJ.pjTahun(tahunPajak(), kini());"),
    ('setoran dibuka untuk tahun pilihan', "pjSetorBuka: ({ b }) => { const T = PJ.pjTahun(tahunPajak(), kini());"),
    ('rekap konsultan dicetak untuk tahun pilihan', "pjKeluar: async ({ cara }) => { const T = PJ.pjTahun(tahunPajak(), kini());"),
    ('pemilih tahun digambar dari pjDaftarTahun', 'data-aksi="pjTahun" data-t="${x.tahun}"'),
    ('bawaan tahun dari pjTahunBawaan', "s.tahunPj && PJ.pjDaftarTahun(kini()).some((x) => x.tahun === s.tahunPj) ? s.tahunPj : PJ.pjTahunBawaan(kini())"),
    ('pil masa setoran & bulan omzet luar dari tahun yang dibuka', "${T.daftar.slice().reverse().map((b) => h`${pil(dl.bulan, b.key, 'pjLuarPilih', 'bulan')}${b.pendek}</div>`)}"),
    ('omzet tahun lalu disimpan untuk tahun pilihan', "PJ.susunProfilPajak(Object.assign({}, st().drafPj || {}, { tahunPajak: tahunPajak() }), waktu())"),
]


def statis(lap=None):
    lap = lap if lap is not None else open(os.path.join(AKAR, 'baru/js/layar/laporan.js'), encoding='utf-8').read(); out = []
    for nama, jangkar in STATIS_LAYAR:
        if jangkar not in lap: out.append('statis laporan.js: ' + nama)
    if 'PJ.pjTahun(null' in lap: out.append('statis laporan.js: masih ada PJ.pjTahun(null …) — tahun berjalan saja')
    uang = open(os.path.join(AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
    if 'BK.potretLatihan(T.tahun, kini())' not in uang: out.append('statis uang.js: langkah Kunci latihan tidak menyusun potret')
    return out


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[-1500:]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def bundelan():
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))


def utama(js, cek_statis=True):
    h, e = jalan(JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + BERSAMA + SKENARIO + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
    if h is None: return 0, ['JSC JATUH: ' + e]
    g = h['gagal'] + (statis() if cek_statis else [])
    return h['lulus'], g


ASAP = r"""
// ==================== ASAP — CADANGAN TOKO LOKAL (tidak di-commit; dilewati di CI). Putusan per tanggal & aturan pajak = TIRUAN di memori, bukan data owner ====================
var salahA = [];
function muatCad() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' };
  terapkanKeCache([{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: 5, batasBebas: 500000000, batasOmzet: 4800000000 }, { tanggal: '2026-10-06', jam: '10:00' }) }]); }
var hasilA = {};
[['2027-01-05T10:00:00+07:00'], ['2027-03-31T10:00:00+07:00']].forEach(function (x) {
  muatCad(); var w = jam(x[0]); var k = new Date(__KINI); var S = layar(k);
  var R0 = ritual(w); if (R0.tolak) { salahA.push(x[0] + ' ritual ditolak: ' + R0.tolak.slice(0, 300)); return; }
  var A = layar(new Date(__KINI)); var b = beda(S, A); if (b.length) salahA.push(x[0] + ' SESUDAH ≠ SEBELUM: ' + J(b.slice(0, 4)));
  var BF = bentukFirestore(acara(2026)); if (BF.length) salahA.push(x[0] + ' bentuk Firestore: ' + J(BF.slice(0, 4)));
  var berjalan = R0.kiriman[0].dokumen.filter(function (d) { return d.koleksi === 'tutupBukuAcara'; }).map(function (d) { return J(d.data).length; });
  hasilA[x[0].slice(0, 10)] = { omzetSistem2026: pjTahun(2026, k).totalSistem, pph2026: pjTahun(2026, k).totalPph, bulanFinal: rekapOmzet(k).daftar.filter(function (b) { return b.final; }).length, hariPotret: Object.keys(acara(2026).potret.hari).length,
    ukuranBeritaAcara: J(acara(2026)).length, ukuranKirimanPertama: berjalan, layarDibandingkan: Object.keys(S).length };
  if (J(acara(2026)).length > 900000 || berjalan.some(function (n) { return n > 900000; })) salahA.push(x[0] + ' berita acara terlalu besar untuk Firestore (> 900 KB)');
  if (x[0].slice(0, 10) === '2027-01-05') { var wS = jam('2027-01-10T10:00:00+07:00'); var D12 = pjTahun(2026, new Date(__KINI)).daftar[11];
    var rS = susunSetoran({ masaPajak: '2026-12', tanggalSetor: '2027-01-10', jumlah: String(Math.max(1, D12.pph || 1)), ntpn: '1234ABCD5678EFGH' }, wS, new Date(__KINI));
    if (rS.tolak) salahA.push('setoran Desember ditolak: ' + rS.tolak); else { tulis(rS); var s = cacheMentah('pajakSetoran').filter(function (y) { return y.masaPajak === '2026-12'; })[0]; if (!s || s.omzetSaatSetor !== D12.omzet) salahA.push('setoran Desember: potret omzet salah'); hasilA.setoranDes = s ? s.omzetSaatSetor : null; } }
});
print(JSON.stringify({ salah: salahA, hasil: hasilA }));
"""


def asap(js, berkas):
    h, e = jalan(JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CAD = ' + open(berkas, encoding='utf-8').read() + ';\n' + BERSAMA + ASAP)
    if h is None: return None, ['ASAP JATUH: ' + e]
    return h['hasil'], h['salah']


RUSAK = [
    ('ritual tidak menulis potret di berita acara', 'baru/js/layar/tutup-buku-logika.js', "  try { acara.potret = susunPotret(tahun, ugKiniDari(w)); } catch (e) {", "  try { susunPotret(tahun, ugKiniDari(w)); } catch (e) {"),
    ('potret gagal disusun tetap dikunci (diam)', 'baru/js/layar/tutup-buku-logika.js', "return { tolak: 'Potret ' + tahun + ' gagal disusun (' + String((e && e.message) || e).slice(0, 160) + ') — tahun TIDAK dikunci", "if (0) return { tolak: 'Potret ' + tahun + ' gagal disusun (' + String((e && e.message) || e).slice(0, 160) + ') — tahun TIDAK dikunci"),
    ('pembaca mengabaikan potret (Rp0 FINAL lagi)', 'baru/js/data/toko.js', "function potretBulan(key) { const P = potretTahun(key);", "function potretBulan(key) { const P = null && potretTahun(key);"),
    ('potret tetap dibaca sesudah Batalkan (tanpa penjaga era & status berita acara)', 'baru/js/data/toko.js', "  if (era !== null) (_cache.tutupBukuAcara || []).forEach((a) => { const t = Number(a && a.tahun); if (!isFinite(t) || t > era || (a.status !== 'terkunci' && a.status !== 'selesai')) return;", "  (_cache.tutupBukuAcara || []).forEach((a) => { const t = Number(a && a.tahun); if (!isFinite(t)) return;"),
    ('Pajak: omzet sistem tidak membaca potret', 'baru/js/layar/pajak-logika.js', "  const Pt = potretBulan(key); if (Pt) return { omzet: Number(Pt.omzet) || 0, n: Number(Pt.n) || 0 };", ""),
    ('Pajak: potongan nota tidak membaca potret', 'baru/js/layar/pajak-logika.js', "  const Pt = potretBulan(key); if (Pt && Pt.potongan) return Object.assign({}, Pt.potongan);", ""),
    ('R4: awal sistem pindah ke nota pertama 2027', 'baru/js/layar/pajak-logika.js', "  const q = awalPotret('awalSistem'); if (q && (!p || q < p)) p = q;\n  const era = eraBerAcara(); if (era !== null && (!p || p > era + '-12-31')) p = (era + 1) + '-01-01';\n", ""),
    ('R4 tanpa potret: tahun sesudah tutup buku tidak sejak 1 Januari', 'baru/js/layar/pajak-logika.js', "if (era !== null && (!p || p > era + '-12-31')) p = (era + 1) + '-01-01';", "if (false) p = (era + 1) + '-01-01';"),
    ('Laporan: catatan pertama tidak membaca potret (bulan 2026 hilang dari daftar)', 'baru/js/layar/laporan-logika.js', "const q = awalPotret('pertama'); return q && (!p || q < p) ? q : p; }", "return p; }"),
    ('Laba: bulan ditutup tidak membaca potret', 'baru/js/layar/laporan-logika.js', "  const Pt = potretBulan(key); if (Pt && Pt.lb) return lpLabaPotret(key, Pt);   // Paket B: tahun yang sudah ditutup buku", ""),
    ('Ke mana laba kotor: bulan ditutup tidak membaca potret', 'baru/js/layar/laporan-logika.js', "  const Pt = potretBulan(key); if (Pt && Pt.km) {", "  const Pt = null; if (Pt && Pt.km) {"),
    ('Inti bulan: bulan ditutup tidak membaca potret', 'baru/js/layar/laporan-logika.js', "  const Pt = potretBulan(key); if (Pt && Pt.inti) return", "  const Pt = null; if (Pt && Pt.inti) return"),
    ('Biaya: bulan ditutup tidak membaca potret', 'baru/js/layar/kendali-biaya-logika.js', "  const Pt = potretBulan(key); if (Pt && Pt.kb) return kbDariPotret(key, kini, Pt);", ""),
    ('Biaya: pemicu bulan ditutup dihitung dari catatan (kedatangan & QRIS hilang)', 'baru/js/layar/kendali-biaya-logika.js', "  if (X.pemicu) return X.pemicu;\n", ""),
    ('rentang laba-rugi tidak dijumlah per bulan dari potret', 'baru/js/layar/laporan-logika.js', "  if (!lpBulanDitutup(dari, sampai).length) return ugLabaBersih(dari, sampai, B);\n", "  return ugLabaBersih(dari, sampai, B);\n"),
    ('arus kas tidak membaca potret', 'baru/js/layar/laporan-logika.js', "  if (!lpBulanDitutup(dari, sampai).length) return hitungArusKasInti((t) => !!t && t >= dari && t <= sampai, B);", "  return hitungArusKasInti((t) => !!t && t >= dari && t <= sampai, B);"),
    ('neraca akhir bulan ditutup dihitung dari catatan hidup', 'baru/js/layar/laporan-logika.js', "if (s && lpTutup(s)) return lpNeracaArsip(s);   // Paket B", "if (false) return lpNeracaArsip(s);   // Paket B"),
    ('neraca: laba ditahan tahun lalu tidak dari potret (belum terjelaskan)', 'baru/js/layar/laporan-logika.js', "  if (PtN && PtN.labaKum !== null && PtN.labaKum !== undefined) { const c1", "  if (false) { const c1"),
    ('kas akhir bulan ditutup tidak dari potret', 'baru/js/layar/laporan-logika.js', "if (Pt && Pt.kas) return Object.assign({}, Pt.kas);", "if (false) return Object.assign({}, Pt.kas);"),
    ('hari ditutup tidak dari potret (Harian, Mingguan, Dasbor)', 'baru/js/layar/laporan-logika.js', "  tutup.forEach((t) => { const P = potretHari(t); if (!P) { out.tanpaPotret += 1; return; }", "  tutup.forEach((t) => { const P = null; if (!P) { out.tanpaPotret += 1; return; }"),
    ('Harian: 14 hari tidak membaca potret', 'baru/js/layar/laporan-logika.js', "    if (lpTutup(t)) { const P = potretHari(t); out.push({ iso: t, n: P ? P.nota : 0, omzet: P ? P.omzet : 0,", "    if (lpTutup(t)) { const P = null; out.push({ iso: t, n: P ? P.nota : 0, omzet: P ? P.omzet : 0,"),
    ('Tahunan: bulan ditutup tidak membaca potret', 'baru/js/layar/laporan-logika.js', "    const Pt = potretBulan(key); if (!Pt && lpTutup(key)) {", "    const Pt = null; if (!Pt && lpTutup(key)) {"),
    ('Tahunan: omzet tahun lalu tidak dari potret', 'baru/js/layar/laporan-logika.js', "function lpOmzetTahun(y) { const P = potretTahun(y);", "function lpOmzetTahun(y) { const P = null;"),
    ('Bukti omzet: bulan tanpa angka dicetak Rp0 final', 'baru/js/layar/laporan-logika.js', "  const tanpaAngka = terpilih.filter((b) => b.absen || b.tanpaPotret);", "  const tanpaAngka = [];"),
    ('DK3: bulan ditutup tanpa potret tidak ditandai', 'baru/js/layar/laporan-logika.js', "lpTutup(k) && !potretBulan(k) ? { tanpaPotret: true } : {})); }", "{})); }"),
    ('laporan berkop menyentuh bulan tanpa potret tidak ditolak', 'baru/js/layar/laporan-logika.js', "  if (tanpaPotret.length) tolak = lpKalimatTanpaPotret(tanpaPotret);\n", ""),
    ('bawaan Pajak selalu tahun berjalan', 'baru/js/layar/pajak-logika.js', "  const iso = hariIniIso(kini || new Date(Date.now())); const th = Number(iso.slice(0, 4)); if (Number(iso.slice(5, 7)) > 3) return th;", "  const iso = hariIniIso(kini || new Date(Date.now())); const th = Number(iso.slice(0, 4)); return th;"),
    ('daftar tahun Pajak tanpa tahun lalu', 'baru/js/layar/pajak-logika.js', "  return Object.keys(ada).map(Number).sort((a, b) => b - a).map((y) => ({ tahun: y,", "  return [th].map((y) => ({ tahun: y,"),
    ('Beranda Jan–Mar tidak memeriksa tahun lalu', 'baru/js/layar/pajak-logika.js', "const semua = (Number(iso.slice(5, 7)) <= 3 ? pjTahun(thIni - 1, kini).daftar : []).concat(T.daftar);", "const semua = [].concat(T.daftar);"),
    ('pengingat hanya tahun berjalan (Desember lenyap)', 'baru/js/layar/pajak-logika.js', "  [th - 1, th].forEach((y) => { const T = pjTahun(y, kini); if (!T.hitung) return;", "  [th].forEach((y) => { const T = pjTahun(y, kini); if (!T.hitung) return;"),
    ('omzet tahun lalu tidak per tahun (satu kolom)', 'baru/js/layar/pajak-logika.js', "function pjOmzetTahunLalu(P, th) { const v = P.omzetTahunan ? P.omzetTahunan[String(Number(th) - 1)] : undefined; return v === undefined ? null : v; }", "function pjOmzetTahunLalu(P, th) { return P.omzetTahunLalu; }"),
    ('aturan tanpa label tahun pajak', 'baru/js/layar/pajak-logika.js', "const belum = !!hitung && Number(th) > diisi;", "const belum = false;"),
    ('latihan tidak menyusun potret (gagal baru ketahuan saat ritual)', 'baru/js/layar/tutup-buku-logika.js', "function potretLatihan(tahun, kini) { try { const Pt = susunPotret(tahun, kini);", "function potretLatihan(tahun, kini) { try { const Pt = { tahun, bulan: {}, hari: {} };"),
]
RUSAK_LAYAR = [
    ('laporan.js: Pajak kembali ke tahun berjalan saja', "  function gambarPajak(s, L) {\n    const T = PJ.pjTahun(tahunPajak(), kini());", "  function gambarPajak(s, L) {\n    const T = PJ.pjTahun(null, kini());"),
    ('laporan.js: setoran hanya tahun berjalan', "pjSetorBuka: ({ b }) => { const T = PJ.pjTahun(tahunPajak(), kini());", "pjSetorBuka: ({ b }) => { const T = PJ.pjTahun(null, kini());"),
    ('laporan.js: tanpa pemilih tahun', 'data-aksi="pjTahun" data-t="${x.tahun}"', 'data-aksi="pjTahunX" data-t="${x.tahun}"'),
]


if __name__ == '__main__':
    js = bundelan()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            sumber = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
            if sumber.count(a) != 1 or js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        lap = open(os.path.join(AKAR, 'baru/js/layar/laporan.js'), encoding='utf-8').read()
        for nama, a, b in RUSAK_LAYAR:
            if lap.count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            g = statis(lap.replace(a, b))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('POTRET TAHUN DITUTUP (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    berkas = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--asap=')), '') or os.environ.get('POTRET_ASAP', '')
    if berkas:
        h, s = asap(js, berkas)
        print('ASAP CADANGAN LOKAL (%s): %s' % (os.path.basename(berkas), json.dumps(h, ensure_ascii=False)))
        for x in s: print('   ✗ ' + x)
        if s: sys.exit(2)
    sys.exit(0 if not g else 2)
