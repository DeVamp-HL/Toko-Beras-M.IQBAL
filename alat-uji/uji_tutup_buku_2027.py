#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tutup_buku_2027.py — TUTUP BUKU TAHUN YANG BULANNYA SUDAH DIKUNCI (owner 7 Okt 2026, K8 "pengecualian sempit"; rules v7 pintu tutup buku).
KOTAK PASIR (nama & angka CONTOH, bukan angka toko), jsc + penafsir rules mini (alat-uji/rules_mini.py). Tanpa peramban.

Sebelum v7: begitu satu bulan 2027 dikunci, tutup buku 2027 mustahil (rules menolak tulis/hapus bulan terkunci) dan butir A2 menahan kunci 2028 → buntu Januari
2028. Uji ini menjalankan ritualnya SUNGGUHAN lewat jalankanBuku / jalankanBatal / bukaPintu APA ADANYA dari baru/js/layar/uang.js, dengan "server tiruan"
(penulis bentuk firebase.js: tulis, arsip per potongan kpPecahBiaya, pengembalian) yang MENCATAT tiap batch — lalu TIAP batch dinilai TEKS firestore.rules
(penafsir mini, keadaan sebelum & sesudah batch, access call dihitung tanpa cache):

  P0  tutup buku 2026 (tanpa bulan terkunci) jalan seperti dulu — TANPA pintu, semua batch diterima rules v7 (regresi jalur 2026)
  P1  2027 berjalan (nota tunai & bon, bon pemasok, bayar sebagian, kasbon, modal, amplop, biaya bulanan, pindah uang); Januari–November 2027 DIKUNCI
  P2  5 Jan 2028: tahun 2027 boleh ditutup sungguhan (dulu ditolak); kiriman 1 = berita acara 'berjalan' SENDIRIAN, kiriman 2 MEMBUKA pintu (server membaca
      berita acara SEBELUM batch — sanggahan rules 7 Okt); saldo pembuka bertanggal lama (piutang tertua 2026,
      bon pemasok 2026 & 2027) lewat pintu; arsip memindah catatan bulan terkunci (juga saldo pembuka 2026) — tiap batch DITERIMA rules, ≤ 18 access call,
      dan perkiraan layar = hitungan server (penjaga klien = rules); periksa ulang "sama persis"; selesai MENUTUP pintu; kunci Februari 2028 tidak lagi buntu
  P3  selama pintu terbuka, catatan bulan terkunci LAINNYA tetap terkunci: ubah catatan terkunci (bukan arsip), buat catatan biasa, saldo pembuka tahun lain,
      hapus tanpa salinan arsip, pindahUang (tidak diarsip), ubah saldo pembuka 2027, kasir@ / staf lewat pintu — DITOLAK rules DAN penjaga klien.
      Sanggahan rules 7 Okt (rules saja): hapus dengan salinan arsip SAMPAH / BEDA isi, salinan arsip karangan, "saldo pembuka" di penjualan &
      pengeluaranHarian, titik kas mundur jauh, berita acara + pintu tahun lain dalam SATU kiriman, berita acara selesai tanpa menutup pintu — DITOLAK;
      sesudah selesai: berita acara tidak bisa dihapus, pintu tidak bisa dibuka lagi
  P4  BATALKAN sesudah arsip penuh (jalankanBatal uang.js): tarik saldo pembuka (juga yang bertanggal lama) & kembalikan arsip lewat pintu — batch diterima rules;
      SEMUA catatan kembali PERSIS (isi, jumlah, titik kas), era kembali 2026, pintu tertutup, berita acara dibatalkan. P4b: saldo pembuka yang mendarat
      SESUDAH dibatalkan → pembatalan lanjutan menulis 'membatalkan' sendirian dulu, baru pintu & tarikannya (diterima rules)
  P5  Desember 2027 ikut dikunci (10 Jan 2028): titik kas 31 Des & modal owner 31 Des lewat pintu; arsip TERPUTUS di tengah, pintu kedaluwarsa (2 hari kemudian)
      → Lanjutkan membuka pintu lagi (bukaPintu uang.js) lalu arsip habis, sama persis
  P6  tanpa pintu (rules menolak) = penjaga klien juga menolak — kiriman tidak dikirim (kalimat bulan terkunci), tidak ada setengah jalan
  P7  30 nama berutang bertanggal bulan terkunci: saldo pembuka dipecah (berita acara 'berjalan' sendirian di kiriman 1, pintu di kiriman 2), putus sesudah
      kiriman 2, tiga hari kemudian (pintu kedaluwarsa) Lanjutkan (lanjutBuku) membuka pintu lagi di kiriman lanjutan pertama — semua batch diterima rules

    python3 alat-uji/uji_tutup_buku_2027.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tutup_buku_2027.py --kontrol  → kerusakan (klien, uang.js, rules) wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, re
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode, uji_tutup_buku_bertahap, uji_uang_baru, rules_mini  # noqa: E402

MODUL = uji_tutup_buku_bertahap.MODUL
OWNER = {'uid': 'uid-owner-uji', 'email': 'owner@tokoberasmiqbal.web.app'}
AKUN = {'owner': OWNER, 'kasir': {'uid': 'uid-kasir-uji', 'email': 'kasir@tokoberasmiqbal.web.app'}, 'staf': {'uid': 'uid-staf-uji', 'email': 'staf.uji@contoh.com'}}
DB_STAF = {'aksesAkun/uid-staf-uji': {'uid': 'uid-staf-uji', 'nama': 'Staf Uji', 'peran': 'ben', 'aktif': True}}
UANG_AWAL = '  async function jalankanBuku(tahun, kiriman, titik, kabarAkhir) {'
UANG_AKHIR = '\n  const bandingB = '


def uang_js(teks=None):
    """jalankanBuku + jalankanBatal + bukaPintu APA ADANYA dari uang.js, dibungkus buatUang(A) (set / st / lokal / waktu / BK / tulisDokumen / … = kotak pasir)."""
    u = teks if teks is not None else open(os.path.join(AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
    a = u.index(UANG_AWAL); b = u.index(UANG_AKHIR, a)
    return ('function buatUang(A) { var set = A.set, st = A.st, lokal = A.lokal, waktu = A.waktu, BK = A.BK, bacaArsipTahun = A.bacaArsipTahun, pulihkanArsip = A.pulihkanArsip,'
            ' tulisDokumen = A.tulisDokumen, arsipkanDokumen = A.arsipkanDokumen, setelTitik = A.setelTitik, LANGKAH_KOSONG = A.LANGKAH_KOSONG;\n' + u[a:b] +
            '\n  return { jalankanBuku: jalankanBuku, jalankanBatal: jalankanBatal }; }\n')


SKENARIO = r"""
(function () {   // satu lingkup fungsi: nama pembantu uji tidak bertabrakan dengan nama di bundel
var gagal = [], lulus = 0; var J = JSON.stringify; var CATATAN = {};
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(ket).slice(0, 700) : '')); }
function salin(x) { return x === undefined || x === null ? null : JSON.parse(J(x)); }

// ==================== SERVER TIRUAN — bentuk baru/js/data/firebase.js; TIAP batch dicatat (untuk penilai rules di Python) lalu diterapkan ====================
var JAM_SERVER = '__JAM_SERVER__';   // = serverTimestamp() capServer (hemat baca) — Python mengganti dengan jam batch
var SRV = { batch: [], coba: [], arsip: {}, nKirim: 0, putusSesudah: null, fase: '' };
var TAHUN_DB = [2025, 2026, 2027, 2028];
function hemat(kol) { var k = KOLEKSI.find(function (x) { return x.nama === kol; }); return !!k && !k.kelas; }
function dokNyata(kol, id) { return kol === 'arsipTahun' ? salin(SRV.arsip[id] || null) : salin(dokDiCache(kol, id)); }
function potretDb(ops) {
  var db = {}; var t = function (kol, id) { var d = dokNyata(kol, String(id)); if (d) db[kol + '/' + id] = d; };
  t('aturanToko', 'kunciPeriode'); t('pengaturan', 'pintuBuku'); t('pengaturan', 'titikKas');
  ambilTutupBukuAcara().forEach(function (a) { db['tutupBukuAcara/' + a.id] = salin(a); });
  ops.forEach(function (o) { t(o.koleksi, o.id); if (o.koleksi !== 'arsipTahun') TAHUN_DB.forEach(function (y) { t('arsipTahun', y + '|' + o.koleksi + '|' + o.id); });
    else { var bg = String(o.id).split('|'); if (bg.length === 3) t(bg[1], bg[2]); } });   // salinan arsip: rules arsipSah membaca catatan aslinya
  return db;
}
function terapkan(ops) {
  var c = [];
  ops.forEach(function (o) {
    if (o.koleksi === 'arsipTahun') { if (o.op === 'delete') delete SRV.arsip[o.id]; else SRV.arsip[o.id] = salin(o.data); return; }
    if (o.koleksi === 'logAktivitas') return;
    if (o.op === 'delete') c.push({ koleksi: o.koleksi, hapus: o.id }); else { var d = salin(o.data); delete d.capServer; c.push({ koleksi: o.koleksi, data: d }); }   // hemat baca: cap dikupas sebelum memori
  });
  terapkanKeCache(c);
}
function catat(nama, ops, perkiraan) {
  SRV.nKirim += 1; if (SRV.putusSesudah !== null && SRV.nKirim > SRV.putusSesudah) return false;   // sinyal putus (tiruan): batch ini TIDAK sampai server
  SRV.batch.push({ nama: SRV.fase + ' · ' + nama, jam: new Date(__KINI).toISOString(), ops: ops.map(salin), db: potretDb(ops), perkiraan: perkiraan === undefined ? null : perkiraan });
  terapkan(ops); return true;
}
var NLOG = 0; function logOp(r) { NLOG += 1; return { op: 'set', koleksi: 'logAktivitas', id: 'log-' + NLOG, data: { id: 'log-' + NLOG, ringkas: r } }; }
function setCap(kol, d) { var x = salin(d); if (hemat(kol)) x.capServer = JAM_SERVER; return x; }
var jumlah = function (a) { return a.reduce(function (s, x) { return s + x; }, 0); };
setelPenulis({
  tulis: async function (daftar, hapus) { var ops = [];
    (daftar || []).forEach(function (x) { ops.push({ op: 'set', koleksi: x.koleksi, id: String(x.data.id), data: setCap(x.koleksi, x.data) }); ops.push(logOp('tulis')); });
    (hapus || []).forEach(function (x) { ops.push({ op: 'delete', koleksi: x.koleksi, id: String(x.id) }); ops.push(logOp('hapus')); });
    return catat('tulis', ops, nilaiKunci(daftar || [], hapus || []).perluGet) ? { ok: true } : { antre: true, pesan: 'sinyal putus (tiruan)' }; },
  hapus: async function (daftar) { var ops = daftar.map(function (x) { return { op: 'delete', koleksi: x.koleksi, id: String(x.id) }; }); return catat('hapus', ops, nilaiKunci([], daftar).perluGet) ? { ok: true } : { antre: true }; },
  arsipkan: async function (tahun, daftar, progres, biaya) { var b = biaya || daftar.map(function () { return 1; }); var P = kpPecahBiaya(b, 18, 18); var sudah = 0;
    for (var q = 0; q < P.length; q++) { var potong = daftar.slice(P[q][0], P[q][1]); var ops = [];
      potong.forEach(function (x) { var aid = tahun + '|' + x.koleksi + '|' + x.id; ops.push({ op: 'set', koleksi: 'arsipTahun', id: aid, data: { id: aid, tahun: tahun, koleksi: x.koleksi, idAsli: String(x.id), dok: x.data } }); ops.push({ op: 'delete', koleksi: x.koleksi, id: String(x.id) }); });
      ops.push(logOp('arsip'));
      if (!catat('arsip ' + tahun + ' potongan ' + (q + 1) + '/' + P.length, ops, jumlah(b.slice(P[q][0], P[q][1])))) throw new Error('arsip terputus (sinyal putus tiruan)');
      sudah += potong.length; if (progres) progres(sudah, daftar.length); }
    return { ok: true, n: sudah }; },
  bacaArsip: async function (tahun) { return Object.keys(SRV.arsip).map(function (k) { return SRV.arsip[k]; }).filter(function (a) { return a.tahun === tahun; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: salin(a.dok) }; }); },
  pulihkan: async function (tahun, daftar, progres, biaya) { var b = biaya || daftar.map(function () { return 1; }); var P = kpPecahBiaya(b, 18, 18); var sudah = 0;
    for (var q = 0; q < P.length; q++) { var potong = daftar.slice(P[q][0], P[q][1]); var ops = [];
      potong.forEach(function (x) { ops.push({ op: 'set', koleksi: x.koleksi, id: String(x.idAsli), data: setCap(x.koleksi, x.dok) }); ops.push({ op: 'delete', koleksi: 'arsipTahun', id: tahun + '|' + x.koleksi + '|' + x.idAsli }); });
      ops.push(logOp('pulihkan'));
      if (!catat('pulihkan ' + tahun + ' potongan ' + (q + 1) + '/' + P.length, ops, jumlah(b.slice(P[q][0], P[q][1])))) throw new Error('pengembalian terputus (tiruan)');
      sudah += potong.length; if (progres) progres(sudah, daftar.length); }
    return { ok: true, n: sudah }; } });
// percobaan yang WAJIB ditolak (tidak diterapkan): dinilai rules di Python; penjaga klien (jagaKunci) dinilai di sini
function cobaTolak(nama, akun, daftar, hapus) {
  var ops = (daftar || []).map(function (x) { return { op: 'set', koleksi: x.koleksi, id: String(x.data.id), data: setCap(x.koleksi, x.data) }; }).concat((hapus || []).map(function (x) { return { op: 'delete', koleksi: x.koleksi, id: String(x.id) }; }));
  SRV.coba.push({ nama: nama, akun: akun, jam: new Date(__KINI).toISOString(), ops: ops, db: potretDb(ops) });
  return akun === 'owner' ? jagaKunci(daftar || [], hapus || []) : 'bukan-owner';
}

// percobaan yang WAJIB ditolak rules, berbentuk ops mentah (bukan tulisan layar): salinan arsip karangan, berita acara, pintu — tidak dinilai penjaga klien
function cobaRules(nama, akun, ops) { SRV.coba.push({ nama: nama, akun: akun, jam: new Date(__KINI).toISOString(), ops: ops.map(salin), db: potretDb(ops) }); }

// ==================== KOTAK & ALAT ====================
var D = { paraf: { owner: true, saksi: true }, saksi: 'Saksi Contoh', langkah: {} };
var L = { idPerangkat: 'mac-uji', namaPerangkat: 'Mac Uji', antre: [], menunggu: 0, offline: false };
var nId = 80000; var W = null;
function jam(iso) { __KINI = new Date(iso).getTime(); W = { tanggal: kpWib(new Date(iso)).iso, jam: iso.slice(11, 16), kini: new Date(iso).toISOString(), idUnik: function () { nId += 1; return 'u' + nId; } }; return W; }
var S = { langkahB: {} };
var BKP = new Proxy({}, { get: function (t, k) { return typeof k === 'string' && /^[A-Za-z_]\w*$/.test(k) ? eval(k) : undefined; } });   // namespace tutup-buku-logika (kode uji)
var UANG = buatUang({ set: function (p) { Object.assign(S, p); }, st: function () { return S; }, lokal: function () { return L; }, waktu: function () { return W; }, BK: BKP,
  setelTitik: function (t) { if (t) localStorage.setItem('miqbal_titik_kas_v1', J(Object.assign({ id: 'titikKas' }, t))); }, LANGKAH_KOSONG: function () { return {}; },
  tulisDokumen: tulisDokumen, arsipkanDokumen: arsipkanDokumen, pulihkanArsip: pulihkanArsip, bacaArsipTahun: bacaArsipTahun });
function acara(t) { return ambilTutupBukuAcara().find(function (a) { return Number(a.tahun) === t; }) || null; }
function putusSemua() { var tH = {}; ambilTutupHari().forEach(function (t) { tH[t.tanggal] = 1; }); var ph = {}; ambilPenjualan().forEach(function (p) { if (p.tanggal && !tH[p.tanggal]) ph[p.tanggal] = { jenis: 'diterima', alasan: 'kotak pasir — hari contoh tanpa tutup hari' }; });
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'putusanHari', hari: ph } }]); }
function kunci(sampai) { terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: sampai, riwayat: [{ aksi: 'kunci', bulan: sampai, pada: '2027-12-04T03:00:00.000Z', olehUid: 'uid-owner-uji' }] } }]); }
var PEMBUKA = ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop', 'modal'];
function nPembuka(t) { var n = 0; PEMBUKA.forEach(function (c) { cacheMentah(c).forEach(function (x) { if (x.tutupBuku && Number(x.tahunDari) === t) n += 1; }); }); return n; }
function pembukaTahun(t) { var o = []; PEMBUKA.forEach(function (c) { cacheMentah(c).forEach(function (x) { if (x.tutupBuku && Number(x.tahunDari) === t) o.push(x); }); }); return o; }
// potret SELURUH isi toko (semua koleksi di memori, tanpa capServer) + titik kas — pembanding "kembali persis" sesudah Batalkan
var TANPA = { tutupBukuAcara: 1, pengaturan: 1, logAktivitas: 1, cadanganCatatan: 1, perangkatStatus: 1, aturanToko: 1 };
function potretToko() { var o = {}; KOLEKSI.forEach(function (k) { if (TANPA[k.nama]) return; cacheMentah(k.cache).forEach(function (d) { var x = salin(d); delete x.capServer; o[k.nama + '/' + d.id] = J(urutKunci(x)); }); });
  var t = ambilTitikKas(); o['titik'] = t ? J([t.tanggal, t.laci, t.brankas, t.rekening, t.amplop]) : ''; return o; }
function urutKunci(x) { if (Array.isArray(x)) return x.map(urutKunci); if (x && typeof x === 'object') { var o = {}; Object.keys(x).sort().forEach(function (k) { o[k] = urutKunci(x[k]); }); return o; } return x; }
function bedaPotret(a, b) { var out = []; Object.keys(a).forEach(function (k) { if (!(k in b)) out.push('hilang ' + k); else if (a[k] !== b[k]) out.push('berubah ' + k); }); Object.keys(b).forEach(function (k) { if (!(k in a)) out.push('baru ' + k); }); return out; }
function samaBaris(PU) { return !!PU && PU.semuaSama; }
function jual(id, tgl, cara, merk, kg, harga, hpp, lain) { return Object.assign({ id: id, tanggal: tgl, jam: '10:00', caraBayar: cara, jenis: 'karung', merkSumber: merk, totalKg: kg, beratKarungAcuan: 50, jumlahKarung: kg / 50, hargaTotal: harga, hppTotalSaatJual: hpp }, lain || {}); }
async function ritual(tahun, w) {
  var R = susunKunci(tahun, D, w, L); if (R.tolak) return { tolak: R.tolak };
  var okB = await UANG.jalankanBuku(tahun, R.kiriman, R.titik, R.patch.kabar); return { R: R, ok: okB };
}
async function selesai(tahun, w) { var SL = susunSelesai(tahun, 'cadangan-sesudah-uji.json', w, false, L); if (SL.tolak) return SL.tolak; var h = await tulisDokumen(SL.dokumen, [], { tunggu: true }); return h && h.ok ? '' : J(h); }

// ==================== P0 · tutup buku 2026 (tanpa bulan terkunci) ====================
async function siapkan2026() {
  KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(KOTAK).forEach(function (n) { pasok(n, salin(KOTAK[n])); });
  localStorage.setItem('miqbal_titik_kas_v1', J({ tanggal: '2026-12-31', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
  SRV.arsip = {}; putusSemua();
  SRV.fase = 'P0 tutup buku 2026'; var w = jam('2027-01-05T10:00:00+07:00');
  var T = tahunBuku(new Date(__KINI)); var r = await ritual(2026, w); var s = r.tolak ? r.tolak : await selesai(2026, w);
  return { T: T, r: r, s: s };
}
// ==================== P1 · 2027 berjalan, Januari–November dikunci ====================
function isi2027() {
  terapkanKeCache([
    { koleksi: 'penjualan', data: jual('t1', '2027-02-14', 'Tunai', 'Angsa', 50, 700000, 650000) },
    { koleksi: 'penjualan', data: jual('t2', '2027-03-05', 'Kredit', 'Angsa', 25, 350000, 325000, { namaPelanggan: 'Pak Contoh' }) },
    { koleksi: 'penjualan', data: jual('t3', '2027-06-10', 'QRIS', 'IR64 Apex', 20, 300000, 280000) },
    { koleksi: 'penjualan', data: jual('t4', '2027-11-30', 'Tunai', 'Angsa', 10, 140000, 130000) },
    { koleksi: 'penjualan', data: jual('t5', '2027-12-20', 'Tunai', 'Angsa', 10, 140000, 130000) },
    { koleksi: 'piutangMutasi', data: { id: 'pb1', tipe: 'bayar', namaPelanggan: 'Bu Contoh', nominal: 100000, tanggal: '2027-04-02', jam: '10:00' } },
    { koleksi: 'batchMasuk', data: { id: 'b27', tanggal: '2027-05-02', jam: '08:00', pemasok: 'RODA CONTOH', caraBayar: 'utang', biayaBongkar: 0,
      merkList: [{ id: 'b27a', merk: 'Angsa', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 13500, subtotalHarga: 6750000 }] } },
    { koleksi: 'utangPemasokMutasi', data: { id: 'up1', tipe: 'bayar', pemasok: 'RODA CONTOH', nominal: 5000000, tanggal: '2027-07-01', jam: '09:00' } },
    { koleksi: 'pengeluaranHarian', data: { id: 'h27', kategori: 'toko', tanggal: '2027-08-15', jam: '09:00', keterangan: 'Bensin antar', nominal: 30000 } },
    { koleksi: 'kasbonMutasi', data: { id: 'kb27', tipe: 'ambil', namaPegawai: 'Gama', nominal: 150000, tanggal: '2027-09-01', jam: '15:00', catatan: 'contoh' } },
    { koleksi: 'modalOwner', data: { id: 'm27', tanggal: '2027-02-01', jam: '08:00', tipe: 'setor', nominal: 5000000, catatan: 'tambah modal contoh' } },
    { koleksi: 'amplopLaba', data: { id: 'am27', tanggal: '2027-10-05', jam: '21:00', tipe: 'setor', nominal: 75000, catatan: 'sisihan contoh' } },
    { koleksi: 'biayaBulanan', data: { id: '2027-05', bulan: '2027-05', listrik: 350000, internet: 250000, akses: 0, keamanan: 0, tanggalBayarPos: { listrik: '2027-05-10', internet: '2027-05-05' }, rincianGaji: [], tanggalBayarGaji: {}, gaji: 0, gajiHariOrang: 0 } },
    { koleksi: 'pindahUang', data: { id: 'pd27', tanggal: '2027-04-10', jam: '21:00', dari: 'laci', ke: 'brankas', nominal: 100000, alasan: 'contoh (tidak diarsip)', biayaAdmin: 0, adminNama: '' } },
  ]);
  putusSemua();
}

async function utama() {
  // ---- P0
  var P0 = await siapkan2026(); var b0 = SRV.batch.length;
  ok('P0 tutup buku 2026 (tanpa bulan terkunci): boleh sungguhan TANPA pintu, ritual & selesai jalan', P0.T.bolehSungguhan && !P0.T.perluPintu && !P0.r.tolak && P0.r.ok && !P0.s && (acara(2026) || {}).status === 'selesai', J([P0.T.teks, P0.r.tolak, P0.s, S.kabar]));
  ok('P0 tanpa dokumen pintu sama sekali (jalur 2026 tidak berubah)', !dokDiCache('pengaturan', 'pintuBuku') && SRV.batch.every(function (b) { return b.ops.every(function (o) { return !(o.koleksi === 'pengaturan' && o.id === 'pintuBuku'); }); }), b0);
  CATATAN.p0 = SRV.batch.length;
  // ---- P1
  isi2027(); kunci('2027-11');
  var pembuka2026 = pembukaTahun(2026).map(function (x) { return x.tanggal || x.bonTanggal; });
  ok('P1 kotak: saldo pembuka 2026 bertanggal bulan yang kini TERKUNCI (piutang tertua 2026, 1 Jan 2027) — ikut diarsip tutup buku 2027', pembuka2026.some(function (t) { return t < '2027-01-01'; }) && pembuka2026.some(function (t) { return t === '2027-01-01'; }), J(pembuka2026));
  // ---- P6 · sebelum v7 (tanpa pintu di klien) penjaga menolak: dicek di kontrol; di sini: catatan bulan terkunci biasa tetap ditolak penjaga
  jam('2028-01-05T10:00:00+07:00');
  var j0 = jagaKunci([{ koleksi: 'penjualan', data: jual('x0', '2027-06-01', 'Tunai', 'Angsa', 1, 14000, 13000) }], []);
  ok('P6 tanpa pintu: nota bertanggal Juni 2027 (terkunci) ditolak penjaga klien dengan kalimat bulan terkunci', j0 && j0.terkunci && /Juni 2027 terkunci/.test(j0.pesan), J(j0));
  var T = tahunBuku(new Date(__KINI)); var G = gerbangBuku(2027, new Date(__KINI), L, { g3: true });
  ok('P2 tahun 2027 (Jan–Nov terkunci) BOLEH ditutup sungguhan lewat pintu (dulu ditolak = buntu Januari 2028); kalimatnya menyebut pintu', T.tahun === 2027 && T.bolehSungguhan && T.perluPintu && T.adaKunci && /pintu tutup buku/.test(T.teks), J(T));
  ok('P2 gerbang g1 (putusan) & g6 (tanpa minus) lolos di kotak', G.daftar.filter(function (g) { return g.id === 'g1' || g.id === 'g6'; }).every(function (g) { return g.ok; }), J(G.daftar.filter(function (g) { return !g.ok; })));
  var sebelum = potretToko(); var arsip0 = arsipBuku(2027); var nKunci = arsip0.daftar.filter(function (x) { var b = kpBulanDok(x.koleksi, x.data); return b !== null && b <= kpIdx('2027-11'); }).length;
  CATATAN.nArsip = arsip0.n; CATATAN.nArsipTerkunci = nKunci;
  // ---- P2 ritual (jalankanBuku uang.js)
  // sanggahan rules 7 Okt (rules saja), SEBELUM ritual: ikatan pintu ke ritual tidak bisa dikarang dalam SATU kiriman; berita acara baru wajib berbentuk &
  // berjam mulai jujur; pintu hanya untuk TAHUN LALU walau berita acara tahun lain sudah ada
  var paraf0 = { owner: true, saksi: true, pada: new Date(__KINI).toISOString() };
  cobaRules('P2a SATU kiriman: berita acara 2027 baru + pintu 2027 + hapus nota Juni 2027 dengan salinannya', 'owner', [
    { op: 'set', koleksi: 'tutupBukuAcara', id: '2027', data: { id: '2027', tahun: 2027, mode: 'sungguhan', status: 'berjalan', paraf: paraf0 } },
    { op: 'set', koleksi: 'pengaturan', id: 'pintuBuku', data: { id: 'pintuBuku', tahun: 2027, status: 'berjalan', sampai: new Date(__KINI + 24 * 3600000) } },
    { op: 'set', koleksi: 'arsipTahun', id: '2027|penjualan|t3', data: { id: '2027|penjualan|t3', tahun: 2027, koleksi: 'penjualan', idAsli: 't3', dok: salin(dokDiCache('penjualan', 't3')) } },
    { op: 'delete', koleksi: 'penjualan', id: 't3' }]);
  cobaRules('P2c berita acara 2027 baru dengan jam mulai MUNDUR 3 hari', 'owner', [{ op: 'set', koleksi: 'tutupBukuAcara', id: '2027', data: { id: '2027', tahun: 2027, mode: 'sungguhan', status: 'berjalan', paraf: { owner: true, saksi: true, pada: new Date(__KINI - 3 * 86400000).toISOString() } } }]);
  terapkanKeCache([{ koleksi: 'tutupBukuAcara', data: { id: '2025', tahun: 2025, mode: 'sungguhan', status: 'berjalan', paraf: paraf0 } }]);   // berita acara tahun LAIN yang sedang berjalan
  cobaRules('P2b pintu 2025 di atas berita acara 2025 yang berjalan (bukan tahun lalu)', 'owner', [{ op: 'set', koleksi: 'pengaturan', id: 'pintuBuku', data: { id: 'pintuBuku', tahun: 2025, status: 'berjalan', sampai: new Date(__KINI + 24 * 3600000) } }]);
  terapkanKeCache([{ koleksi: 'tutupBukuAcara', hapus: '2025' }]);
  SRV.fase = 'P2 tutup buku 2027'; var b1 = SRV.batch.length;
  var r = await ritual(2027, W);
  ok('P2 ritual 2027 jalan sampai arsip habis (jalankanBuku uang.js)', !r.tolak && r.ok === true, J([r.tolak, S.kabar]));
  var K1 = r.R && r.R.kiriman ? r.R.kiriman[0] : null; var K2 = r.R && r.R.kiriman ? r.R.kiriman[1] : null;
  var pintuK2 = K2 ? K2.dokumen.filter(function (x) { return x.koleksi === 'pengaturan' && x.data.id === 'pintuBuku'; })[0] : null;
  ok('P2 kiriman 1 = berita acara \'berjalan\' SENDIRIAN (server membaca berita acara SEBELUM kiriman yang membuka pintu); kiriman 2 membuka pintu (tahun 2027, berjalan, sampai ≤ 72 jam)',
    !!K1 && K1.dokumen.length === 1 && K1.dokumen[0].koleksi === 'tutupBukuAcara' && K1.dokumen[0].data.status === 'berjalan' && !!pintuK2 && pintuK2.data.tahun === 2027 && pintuK2.data.status === 'berjalan'
    && pintuK2.data.sampai instanceof Date && pintuK2.data.sampai.getTime() - __KINI <= 72 * 3600000 && pintuK2.data.sampai.getTime() > __KINI, J([K1 && K1.dokumen.map(function (x) { return x.koleksi + '/' + x.data.id; }), K2 && K2.dokumen.map(function (x) { return x.koleksi + '/' + x.data.id; })]));
  var lamaTerkunci = pembukaTahun(2027).filter(function (x) { var t = x.bonTanggal && x.tipe === 'saldoAwal' && x.pemasok ? x.bonTanggal : x.tanggal; return t && t <= '2027-11-30'; });
  ok('P2 saldo pembuka 2027 bertanggal BULAN TERKUNCI ikut masuk (piutang tertua 2026-09, bon pemasok 2026-08 & 2027-05) — lewat pintu', lamaTerkunci.length >= 3
    && lamaTerkunci.some(function (x) { return x.namaPelanggan === 'Bu Contoh' && x.tanggal === '2026-09-19'; }) && lamaTerkunci.some(function (x) { return x.pemasok && x.bonTanggal === '2027-05-02'; }), J(lamaTerkunci.map(function (x) { return [x.namaPelanggan || x.pemasok, x.tanggal, x.bonTanggal]; })));
  var PA = dokDiCache('pengaturan', 'periksaArsip2027');
  ok('P2 periksa ulang dari mesin sesudah arsip: SAMA PERSIS (semua baris)', samaBaris(S.sesudahLive) && !!PA, J([S.sesudahLive && S.sesudahLive.ringkas, S.kabar]));
  var sisaTerkunci = []; KOLEKSI.forEach(function (k) { if (KP_KOLEKSI_PINTU.indexOf(k.nama) < 0) return; cacheMentah(k.cache).forEach(function (d) { var b = kpBulanDok(k.nama, d); if (b !== null && b <= kpIdx('2027-12') && !(d.tutupBuku && Number(d.tahunDari) === 2027)) sisaTerkunci.push(k.nama + '/' + d.id); }); });
  ok('P2 arsip habis: tidak ada catatan ≤ Des 2027 tersisa di koleksi yang diarsip (selain saldo pembuka 2027); salinannya di arsip = ' + arsip0.n, sisaTerkunci.length === 0 && Object.keys(SRV.arsip).filter(function (k) { return SRV.arsip[k].tahun === 2027; }).length === arsip0.n, J(sisaTerkunci.slice(0, 8)));
  ok('P2 pindahUang Apr 2027 (tidak diarsip, tidak berpintu) tetap di buku hidup', !!dokDiCache('pindahUang', 'pd27'));
  var pintu = pintuBuku(); ok('P2 pintu masih terbuka selama belum selesai', !!pintu && pintu.tahun === 2027, J(dokDiCache('pengaturan', 'pintuBuku')));
  // ---- P3 · selama pintu terbuka: catatan bulan terkunci LAINNYA tetap terkunci (klien & rules)
  var pb27 = lamaTerkunci.filter(function (x) { return x.namaPelanggan; })[0] || lamaTerkunci[0]; var kolPb = pb27 && pb27.namaPelanggan ? 'piutangMutasi' : 'utangPemasokMutasi';
  SRV.arsip['2027|pindahUang|pd27'] = { id: '2027|pindahUang|pd27', tahun: 2027, koleksi: 'pindahUang', idAsli: 'pd27', dok: salin(dokDiCache('pindahUang', 'pd27')) };   // salinan yang SUDAH ada (mis. ditulis dari Console)
  var c = [
    cobaTolak('P3a ubah pindahUang Apr 2027 (terkunci, tidak diarsip)', 'owner', [{ koleksi: 'pindahUang', data: Object.assign({}, dokDiCache('pindahUang', 'pd27'), { nominal: 1 }) }], []),
    cobaTolak('P3b hapus pindahUang Apr 2027 walau salinan arsipnya ADA (pindahUang tidak berpintu)', 'owner', [], [{ koleksi: 'pindahUang', id: 'pd27' }]),
    cobaTolak('P3c nota BIASA bertanggal Juni 2027', 'owner', [{ koleksi: 'penjualan', data: jual('x1', '2027-06-01', 'Tunai', 'Angsa', 1, 14000, 13000) }], []),
    cobaTolak('P3d "saldo pembuka" tahun LAIN (tahunDari 2026) bertanggal Maret 2027', 'owner', [{ koleksi: 'piutangMutasi', data: { id: 'x2', tipe: 'saldoAwal', namaPelanggan: 'Contoh Lain', nominal: 1, tanggal: '2027-03-01', tutupBuku: true, tahunDari: 2026 } }], []),
    cobaTolak('P3e UBAH saldo pembuka 2027 bertanggal lama (pintu tidak membuka ubah)', 'owner', [{ koleksi: kolPb, data: Object.assign({}, pb27, { nominal: (pb27 && pb27.nominal || 0) + 1 }) }], []),
    cobaTolak('P3f kembalikan catatan yang TIDAK ada di arsip (bulan terkunci)', 'owner', [{ koleksi: 'penjualan', data: jual('x3', '2027-02-02', 'Tunai', 'Angsa', 1, 14000, 13000) }], []),
    // sanggahan rules 7 Okt: "saldo pembuka" hanya di koleksi yang memang punya saldo pembuka — nota & uang keluar bertanda tutupBuku tetap catatan biasa
    cobaTolak('P3i nota PENJUALAN bertanda tutupBuku + tahunDari 2027 bertanggal April 2027 (bukan koleksi saldo pembuka)', 'owner', [{ koleksi: 'penjualan', data: jual('x5', '2027-04-12', 'Tunai', 'Angsa', 1, 5000000, 13000, { tutupBuku: true, tahunDari: 2027 }) }], []),
    cobaTolak('P3j uang keluar (pengeluaranHarian) bertanda tutupBuku + tahunDari 2027 bertanggal Maret 2027', 'owner', [{ koleksi: 'pengeluaranHarian', data: { id: 'x6', kategori: 'toko', tanggal: '2027-03-02', jam: '09:00', keterangan: 'contoh', nominal: 750000, tutupBuku: true, tahunDari: 2027 } }], []),
    cobaTolak('P3k titik kas MUNDUR ke 1 Jan 2020 lewat pintu (bukan 31 Des 2027, bukan titikSebelum)', 'owner', [{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2020-01-01', laci: 1, brankas: 0, rekening: 0, amplop: 0 } }], []),
  ];
  delete SRV.arsip['2027|pindahUang|pd27'];
  ok('P3 penjaga klien MENOLAK kesembilan percobaan bulan terkunci selama pintu terbuka (yang kena hukum rules sama dicek di Python)', c.every(function (x) { return x && x.terkunci; }), J(c));
  // sanggahan rules 7 Okt (rules saja): ikatan pintu ke ritual tidak bisa dikarang dalam satu kiriman; berita acara tidak selesai selagi pintunya terbuka
  var acNow = salin(acara(2027));
  cobaRules('P3l SATU kiriman: berita acara 2025 baru + pintu 2025 (berita acara belum ada sebelum kiriman, bukan tahun lalu)', 'owner', [
    { op: 'set', koleksi: 'tutupBukuAcara', id: '2025', data: { id: '2025', tahun: 2025, mode: 'sungguhan', status: 'berjalan', paraf: { owner: true, saksi: true, pada: new Date(__KINI).toISOString() } } },
    { op: 'set', koleksi: 'pengaturan', id: 'pintuBuku', data: { id: 'pintuBuku', tahun: 2025, status: 'berjalan', sampai: new Date(__KINI + 24 * 3600000) } }]);
  cobaRules('P3m berita acara 2027 SELESAI tanpa menutup pintu', 'owner', [{ op: 'set', koleksi: 'tutupBukuAcara', id: '2027', data: Object.assign({}, acNow, { status: 'selesai' }) }]);
  cobaRules('P3n pintu tahun 2026 (bukan tahun lalu; berita acaranya selesai)', 'owner', [{ op: 'set', koleksi: 'pengaturan', id: 'pintuBuku', data: { id: 'pintuBuku', tahun: 2026, status: 'berjalan', sampai: new Date(__KINI + 24 * 3600000) } }]);
  cobaRules('P3o salinan arsip KARANGAN: nota Juni 2027 yang tidak pernah ada', 'owner', [{ op: 'set', koleksi: 'arsipTahun', id: '2027|penjualan|karang1', data: { id: '2027|penjualan|karang1', tahun: 2027, koleksi: 'penjualan', idAsli: 'karang1', dok: jual('karang1', '2027-06-03', 'Tunai', 'Angsa', 50, 9999999, 650000) } }]);
  cobaTolak('P3g kasir@ membuat saldo pembuka 2027 bertanggal lama', 'kasir', [{ koleksi: 'piutangMutasi', data: { id: 'x4', tipe: 'saldoAwal', namaPelanggan: 'Contoh', nominal: 1, tanggal: '2026-09-19', tutupBuku: true, tahunDari: 2027 } }], []);
  cobaTolak('P3h staf menghapus saldo pembuka 2027 bertanggal lama', 'staf', [], [{ koleksi: kolPb, id: pb27 ? pb27.id : 'x' }]);
  // ---- selesai menutup pintu; kunci Februari 2028 tidak buntu
  SRV.fase = 'P2 selesai 2027'; var es = await selesai(2027, W); var pt = dokDiCache('pengaturan', 'pintuBuku');
  ok('P2 SELESAI: berita acara selesai & pintu DITUTUP (status tutup) di kiriman yang sama', !es && (acara(2027) || {}).status === 'selesai' && pt && pt.status === 'tutup' && !pintuBuku(), J([es, pt]));
  // sesudah selesai: pintu tahun itu tidak bisa dibuka lagi, berita acaranya tidak bisa dihapus (lalu dibuat lagi)
  cobaRules('P2x buka pintu 2027 lagi sesudah SELESAI', 'owner', [{ op: 'set', koleksi: 'pengaturan', id: 'pintuBuku', data: { id: 'pintuBuku', tahun: 2027, status: 'berjalan', sampai: new Date(__KINI + 24 * 3600000) } }]);
  cobaRules('P2y hapus berita acara 2027 yang SELESAI', 'owner', [{ op: 'delete', koleksi: 'tutupBukuAcara', id: '2027' }]);
  jam('2028-02-05T10:00:00+07:00'); var DP = kpDaftarPeriksa('2028-01', new Date(__KINI), { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} });
  var tb = DP.butir.filter(function (b) { return b.id === 'tutupBukuLalu'; })[0];
  ok('P2 kunci Januari 2028: butir "Tutup buku 2027 sudah selesai" BERES (tidak buntu lagi)', !!tb && tb.ok, J(tb));
  CATATAN.p2 = SRV.batch.length - b1;
  return sebelum;
}

// ---- P4 · BATALKAN sesudah arsip penuh (jalankanBatal uang.js): semua kembali persis
async function batalkan() {
  SRV.batch = []; SRV.coba = []; NLOG = 0; S = { langkahB: {} };
  await siapkan2026(); isi2027(); kunci('2027-11'); jam('2028-01-05T10:00:00+07:00');
  var sebelum = potretToko(); var era0 = eraBuku();
  SRV.fase = 'P4 tutup buku 2027'; var r = await ritual(2027, W);
  ok('P4 ritual 2027 sampai arsip habis (untuk dibatalkan)', !r.tolak && r.ok === true, J([r.tolak, S.kabar]));
  jam('2028-01-05T13:00:00+07:00'); SRV.fase = 'P4 BATALKAN';
  var okB = await UANG.jalankanBatal(2027);
  var sesudah = potretToko(); var beda = bedaPotret(sebelum, sesudah); var pt = dokDiCache('pengaturan', 'pintuBuku');
  ok('P4 Batalkan tuntas (jalankanBatal uang.js): berita acara dibatalkan, saldo pembuka 2027 = 0, arsip 2027 kosong', okB === true && (acara(2027) || {}).status === 'dibatalkan' && nPembuka(2027) === 0 && Object.keys(SRV.arsip).filter(function (k) { return SRV.arsip[k].tahun === 2027; }).length === 0, J([okB, S.kabar, nPembuka(2027)]));
  ok('P4 SEMUA catatan toko kembali PERSIS seperti sebelum ritual (isi tiap dokumen, jumlah, titik kas) — ' + Object.keys(sebelum).length + ' dibandingkan', beda.length === 0, J(beda.slice(0, 12)));
  ok('P4 era kembali 2026; pintu DITUTUP bersama berita acara dibatalkan', eraBuku() === era0 && era0 === 2026 && pt && pt.status === 'tutup' && !pintuBuku(), J([eraBuku(), pt]));
  // ---- P4b · saldo pembuka 2027 bertanggal bulan terkunci yang MENDARAT SESUDAH dibatalkan (kiriman HP lain yang tertahan) → pembatalan lanjutan
  terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 'telat1', tipe: 'saldoAwal', namaPelanggan: 'Bu Contoh', nominal: 1000, tanggal: '2026-09-19', jam: '00:00', tutupBuku: true, tahunDari: 2027, bertahap: true } }]);
  jam('2028-01-05T15:00:00+07:00'); SRV.fase = 'P4b pembatalan lanjutan'; var b0 = SRV.batch.length;
  var R2 = susunBatal(2027, [], W, L); var k1 = (R2.kiriman || [])[0] || { dokumen: [] }; var k2 = (R2.kiriman || [])[1] || { dokumen: [], hapus: [] };
  ok('P4b dari dibatalkan: kiriman 1 = berita acara membatalkan SENDIRIAN (server membaca berita acara sebelum kiriman pintu), kiriman 2 = pintu + tarik saldo pembuka telat',
    !R2.tolak && k1.dokumen.length === 1 && k1.dokumen[0].koleksi === 'tutupBukuAcara' && k1.dokumen[0].data.status === 'membatalkan' && !(k1.hapus || []).length
    && k2.dokumen.some(function (x) { return x.koleksi === 'pengaturan' && x.data.id === 'pintuBuku'; }) && (k2.hapus || []).some(function (x) { return x.id === 'telat1'; }), J(R2.tolak || (R2.kiriman || []).map(function (k) { return [k.dokumen.map(function (x) { return x.koleksi + '/' + x.data.id; }), (k.hapus || []).map(function (x) { return x.id; })]; })));
  var okB2 = await UANG.jalankanBatal(2027);
  ok('P4b pembatalan lanjutan tuntas: saldo pembuka telat ditarik, berita acara dibatalkan lagi, pintu tertutup', okB2 === true && !dokDiCache('piutangMutasi', 'telat1') && (acara(2027) || {}).status === 'dibatalkan' && !pintuBuku() && SRV.batch.length - b0 >= 3, J([okB2, S.kabar, SRV.batch.length - b0]));
  CATATAN.p4 = SRV.batch.length;
}

// ---- P5 · Desember ikut terkunci; arsip putus; pintu kedaluwarsa; Lanjutkan membuka pintu lagi
async function desemberTerkunci() {
  SRV.batch = []; SRV.coba = []; NLOG = 0; S = { langkahB: {} };
  await siapkan2026(); isi2027(); kunci('2027-12'); jam('2028-01-10T10:00:00+07:00');
  SRV.fase = 'P5 tutup buku 2027 (Des terkunci)';
  var R = susunKunci(2027, D, W, L);
  ok('P5 Desember terkunci: susunan saldo pembuka memuat modal owner 31 Des 2027 & titik kas 31 Des (lewat pintu)', !R.tolak && R.kiriman.some(function (k) { return k.dokumen.some(function (x) { return x.koleksi === 'modalOwner' && x.data.tanggal === '2027-12-31'; }); })
    && R.kiriman.some(function (k) { return k.dokumen.some(function (x) { return x.koleksi === 'pengaturan' && x.data.id === 'titikKas' && x.data.tanggal === '2027-12-31'; }); }), J(R.tolak || R.kiriman.map(function (k) { return k.dokumen.map(function (x) { return x.koleksi + '/' + (x.data.tanggal || x.data.id); }); })));
  var nKirim = R.kiriman.length; SRV.nKirim = 0; SRV.putusSesudah = nKirim + 2;   // kiriman saldo pembuka masuk, arsip putus sesudah 2 potongan
  var okB = await UANG.jalankanBuku(2027, R.kiriman, R.titik, R.patch.kabar);
  var KM = kemajuanBuku();
  ok('P5 arsip TERPUTUS di tengah: jalankanBuku berhenti, pita = fase arsip (sisa catatan), kalimat menyuruh Lanjutkan', okB === false && KM && KM.fase === 'arsip' && KM.sisa > 0 && /Lanjutkan/.test(S.kabar), J([okB, KM, S.kabar]));
  SRV.putusSesudah = null;
  // selagi pintu MASIH terbuka & arsip setengah jalan: hapus catatan bulan terkunci TANPA salinan arsipnya (atau dengan salinan bertahun lain) tetap ditolak
  var sisaA = arsipBuku(2027).daftar.filter(function (x) { return !x.data.tutupBuku; })[0];
  // sanggahan rules 7 Okt (rules saja): salinan arsip wajib = isi catatan yang dihapus — sampah / isi beda ditolak walau pintu terbuka
  if (sisaA) {
    var aid = '2027|' + sisaA.koleksi + '|' + sisaA.id; var beda = Object.assign({}, salin(sisaA.data), { catatanUji: 'diubah lewat arsip' });
    cobaRules('P5c hapus catatan bulan terkunci dengan "salinan arsip" SAMPAH', 'owner', [{ op: 'set', koleksi: 'arsipTahun', id: aid, data: { x: 1 } }, { op: 'delete', koleksi: sisaA.koleksi, id: String(sisaA.id) }]);
    cobaRules('P5d hapus catatan bulan terkunci dengan salinan arsip BERISI LAIN (hapus lalu tulis ulang = ubah)', 'owner', [{ op: 'set', koleksi: 'arsipTahun', id: aid, data: { id: aid, tahun: 2027, koleksi: sisaA.koleksi, idAsli: String(sisaA.id), dok: beda } }, { op: 'delete', koleksi: sisaA.koleksi, id: String(sisaA.id) }]);
    cobaRules('P5e salinan arsip berisi lain TANPA menghapus (untuk "dikembalikan" nanti)', 'owner', [{ op: 'set', koleksi: 'arsipTahun', id: aid, data: { id: aid, tahun: 2027, koleksi: sisaA.koleksi, idAsli: String(sisaA.id), dok: beda } }]);
    SRV.arsip[aid] = { id: aid, tahun: 2027, koleksi: sisaA.koleksi, idAsli: String(sisaA.id), dok: beda };   // salinan berisi lain yang SUDAH ada (mis. dari Console)
    cobaRules('P5f hapus catatan bulan terkunci di atas salinan arsip berisi lain yang sudah ada (tanpa menulis salinan)', 'owner', [{ op: 'delete', koleksi: sisaA.koleksi, id: String(sisaA.id) }]);
    delete SRV.arsip[aid];
  }
  var cA = sisaA ? [cobaTolak('P5a hapus catatan bulan terkunci TANPA salinan arsip (pintu terbuka, arsip setengah jalan)', 'owner', [], [{ koleksi: sisaA.koleksi, id: sisaA.id }]),
    cobaTolak('P5b hapus catatan bulan terkunci dengan salinan arsip bertahun LAIN (2026|…)', 'owner', [{ koleksi: 'arsipTahun', data: { id: '2026|' + sisaA.koleksi + '|' + sisaA.id, tahun: 2026, koleksi: sisaA.koleksi, idAsli: String(sisaA.id), dok: sisaA.data } }], [{ koleksi: sisaA.koleksi, id: sisaA.id }])] : [];
  ok('P5 pintu terbuka: hapus catatan bulan terkunci TANPA salinan arsip tahun pintu → penjaga klien menolak (rules dicek di Python)', !!sisaA && !!pintuBuku() && cA.every(function (x) { return x && x.terkunci; }), J([sisaA && sisaA.koleksi, cA]));
  jam('2028-01-12T15:00:00+07:00');   // 53 jam kemudian: pintu (48 jam) sudah lewat
  ok('P5 dua hari kemudian pintu KEDALUWARSA (klien tidak menganggapnya terbuka)', !pintuBuku(), J(dokDiCache('pengaturan', 'pintuBuku')));
  var b0 = SRV.batch.length; var okL = await UANG.jalankanBuku(2027, [], null, 'Arsip 2027 dilanjutkan.');
  var bukaLagi = SRV.batch.slice(b0).filter(function (b) { return b.ops.some(function (o) { return o.koleksi === 'pengaturan' && o.id === 'pintuBuku' && o.data && o.data.status === 'berjalan'; }); });
  ok('P5 Lanjutkan: bukaPintu (uang.js) MEMBUKA pintu lagi SEBELUM potongan arsip berikutnya, lalu arsip habis & periksa ulang sama persis', okL === true && bukaLagi.length === 1 && SRV.batch.indexOf(bukaLagi[0]) === b0 && samaBaris(S.sesudahLive), J([okL, bukaLagi.length, S.kabar]));
  var es = await selesai(2027, W); ok('P5 selesai → pintu tertutup', !es && (dokDiCache('pengaturan', 'pintuBuku') || {}).status === 'tutup', es);
  CATATAN.p5 = SRV.batch.length;
}

// ---- P7 · banyak nama berutang bertanggal bulan terkunci → saldo pembuka DIPECAH beberapa kiriman (berita acara 'berjalan' + pintu di kiriman 1);
// putus sesudah kiriman 1, tiga hari kemudian (pintu kedaluwarsa) Lanjutkan → lanjutBuku membuka pintu lagi di kiriman lanjutan pertama
async function banyakKiriman() {
  SRV.batch = []; SRV.coba = []; NLOG = 0; S = { langkahB: {} };
  await siapkan2026(); isi2027();
  var bon = []; for (var q = 0; q < 30; q++) bon.push({ koleksi: 'penjualan', data: jual('kr' + q, '2027-0' + (2 + (q % 3)) + '-' + String(3 + (q % 20)).padStart(2, '0'), 'Kredit', 'Angsa', 1, 14000, 13000, { namaPelanggan: 'Pengutang Contoh ' + q }) });
  terapkanKeCache(bon); putusSemua(); kunci('2027-11'); jam('2028-01-05T10:00:00+07:00');
  SRV.fase = 'P7 tutup buku 2027 (banyak kiriman)'; var R = susunKunci(2027, D, W, L);
  var K = R.kiriman || []; var k1 = K[0] || { dokumen: [] };
  var k2 = K[1] || { dokumen: [] };
  ok('P7 30 nama berutang Feb–Apr 2027 (terkunci): saldo pembuka dipecah ≥ 3 kiriman; kiriman 1 = berita acara berjalan SENDIRIAN, kiriman 2 membuka PINTU; tiap kiriman ≤ 18 (perkiraan layar)', !R.tolak && K.length >= 4
    && k1.dokumen.length === 1 && k1.dokumen[0].koleksi === 'tutupBukuAcara' && k1.dokumen[0].data.status === 'berjalan' && k2.dokumen.some(function (x) { return x.koleksi === 'pengaturan' && x.data.id === 'pintuBuku'; }) && K.every(function (k) { return k.get <= 18; }), J(R.tolak || K.map(function (k) { return k.get; })));
  SRV.nKirim = 0; SRV.putusSesudah = 2; var okB = await UANG.jalankanBuku(2027, K, R.titik, R.patch.kabar); SRV.putusSesudah = null;
  var KM = kemajuanBuku();
  ok('P7 putus sesudah kiriman 2: tahun MASIH TERBUKA (fase saldo pembuka), pita menyuruh lanjutkan', okB === false && KM && KM.fase === 'pembuka' && KM.sudah > 0 && KM.sudah < KM.total, J([okB, KM]));
  jam('2028-01-08T11:00:00+07:00');
  ok('P7 tiga hari kemudian pintu kedaluwarsa', !pintuBuku());
  var Lj = lanjutBuku(2027, L); var p1 = Lj.kiriman && Lj.kiriman[0] ? Lj.kiriman[0].dokumen.filter(function (x) { return x.koleksi === 'pengaturan' && x.data.id === 'pintuBuku'; })[0] : null;
  ok('P7 Lanjutkan: kiriman lanjutan PERTAMA membuka pintu lagi (sampai ≥ 48 jam dari sekarang); tiap kiriman ≤ 18', !Lj.tolak && !!p1 && p1.data.sampai.getTime() - __KINI >= 47 * 3600000 && Lj.kiriman.every(function (k) { return k.get <= 18; }), J(Lj.tolak || Lj.kiriman.map(function (k) { return k.get; })));
  var okL = await UANG.jalankanBuku(2027, Lj.kiriman, Lj.titik, 'Tutup buku 2027 dilanjutkan.');
  ok('P7 sesudah Lanjutkan: semua saldo pembuka masuk tepat sekali, arsip habis, periksa ulang sama persis', okL === true && (acara(2027) || {}).status === 'terkunci' && nPembuka(2027) === (acara(2027) || {}).nPembuka && samaBaris(S.sesudahLive), J([okL, S.kabar, nPembuka(2027)]));
  var es = await selesai(2027, W); ok('P7 selesai → pintu tertutup', !es && (dokDiCache('pengaturan', 'pintuBuku') || {}).status === 'tutup', es);
  CATATAN.p7 = SRV.batch.length;
}

var HASIL = null;
(async function () {
  var semua = { batch: [], coba: [] };
  try { await utama(); } catch (e) { gagal.push('P0–P3 JATUH: ' + (e && e.stack ? e.stack.slice(0, 600) : e)); }
  semua.batch = semua.batch.concat(SRV.batch); semua.coba = semua.coba.concat(SRV.coba);
  try { await batalkan(); } catch (e) { gagal.push('P4 JATUH: ' + (e && e.stack ? e.stack.slice(0, 600) : e)); }
  semua.batch = semua.batch.concat(SRV.batch); semua.coba = semua.coba.concat(SRV.coba);
  try { await desemberTerkunci(); } catch (e) { gagal.push('P5 JATUH: ' + (e && e.stack ? e.stack.slice(0, 600) : e)); }
  semua.batch = semua.batch.concat(SRV.batch); semua.coba = semua.coba.concat(SRV.coba);
  try { await banyakKiriman(); } catch (e) { gagal.push('P7 JATUH: ' + (e && e.stack ? e.stack.slice(0, 600) : e)); }
  semua.batch = semua.batch.concat(SRV.batch); semua.coba = semua.coba.concat(SRV.coba);
  HASIL = { lulus: lulus, gagal: gagal, batch: semua.batch, coba: semua.coba, catatan: CATATAN };
})();
drainMicrotasks();
print(J(HASIL || { lulus: lulus, gagal: gagal.concat(['skenario tidak selesai (janji menggantung)']), batch: [], coba: [], catatan: CATATAN }));
})();
"""


def _ubah(nilai, jam, jalur=''):
    """JSON jsc → nilai rules: '__JAM_SERVER__' = jam batch (serverTimestamp); pengaturan/pintuBuku.sampai (Date → teks ISO) = timestamp."""
    if isinstance(nilai, dict):
        out = {}
        for k, v in nilai.items():
            if k == 'sampai' and jalur == 'pengaturan/pintuBuku' and isinstance(v, str): out[k] = rules_mini.Ts.dari_iso(v)
            else: out[k] = _ubah(v, jam)
        return out
    if isinstance(nilai, list): return [_ubah(v, jam) for v in nilai]
    if nilai == '__JAM_SERVER__': return jam
    return nilai


def nilai_rules(teks_rules, hasil):
    """Tiap batch ritual WAJIB diterima rules (≤ 18 access call; perkiraan layar = server); tiap percobaan WAJIB ditolak."""
    R = rules_mini.Rules(teks_rules); salah = []; n = 0; maks = 0; pintu = 0
    for b in hasil['batch']:
        jam = rules_mini.Ts.dari_iso(b['jam'])
        db = dict((k, _ubah(v, jam, k)) for k, v in b['db'].items())
        ops = [{'op': o['op'], 'koleksi': o['koleksi'], 'id': o['id'], 'data': _ubah(o.get('data'), jam, o['koleksi'] + '/' + o['id'])} for o in b['ops']]
        h = rules_mini.nilai_batch(R, ops, OWNER, db, jam); n += 1; maks = max(maks, h['akses'])
        if any(o['koleksi'] == 'pengaturan' and o['id'] == 'pintuBuku' for o in ops): pintu += 1
        if not h['boleh']:
            i = next(i for i, x in enumerate(h['tiap']) if not x.boleh); o = ops[i]
            salah.append('server MENOLAK batch "%s": %s %s/%s%s' % (b['nama'], h['jenis'][i], o['koleksi'], o['id'], (' (' + h['tiap'][i].galat + ')') if h['tiap'][i].galat else ''))
        if h['akses'] > 18: salah.append('batch "%s": %d access call (> 18)' % (b['nama'], h['akses']))
        if b.get('perkiraan') is not None and b['perkiraan'] != h['akses']: salah.append('batch "%s": perkiraan layar %s access call ≠ server %d (penjaga klien ≠ rules)' % (b['nama'], b['perkiraan'], h['akses']))
    nc = 0
    for c in hasil['coba']:
        jam = rules_mini.Ts.dari_iso(c['jam']); db = dict((k, _ubah(v, jam, k)) for k, v in c['db'].items()); db.update(DB_STAF)
        ops = [{'op': o['op'], 'koleksi': o['koleksi'], 'id': o['id'], 'data': _ubah(o.get('data'), jam, o['koleksi'] + '/' + o['id'])} for o in c['ops']]
        h = rules_mini.nilai_batch(R, ops, AKUN[c['akun']], db, jam); nc += 1
        if h['boleh']: salah.append('server MENERIMA percobaan yang wajib ditolak: ' + c['nama'])
    return salah, {'batch': n, 'aksesMaks': maks, 'batchPintu': pintu, 'percobaan': nc}


def jalan(teks=None, teks_rules=None):
    """teks = {berkas: isi} pengganti (kontrol). → (lulus, gagal, info)."""
    T = teks or {}
    js = uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(T.get(m) or open(os.path.join(AKAR, m), encoding='utf-8').read()) for m in MODUL]))
    prog = uji_tutup_buku_bertahap.JAM + js + '\n' + uang_js(T.get('baru/js/layar/uang.js')) + '\nvar KOTAK = ' + json.dumps(uji_uang_baru.KOTAK) + ';\n' + SKENARIO
    h, e = uji_tutup_buku_bertahap.jalan(prog)
    if h is None: return 0, ['JSC JATUH: ' + e], {}
    rs = teks_rules if teks_rules is not None else open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()
    try: salah, info = nilai_rules(rs, h)
    except Exception as ex: salah, info = ['penilai rules jatuh: %r' % ex], {}
    info.update(h.get('catatan') or {})
    if not h['batch']: salah.append('tidak ada batch yang tercatat')
    return h['lulus'], h['gagal'] + salah, info


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        KP, TB, UG, TK, RL = 'baru/js/data/kunci-periode.js', 'baru/js/layar/tutup-buku-logika.js', 'baru/js/layar/uang.js', 'baru/js/data/toko.js', 'firestore.rules'
        RUSAK = [
            ('klien: tahun berbulan terkunci tanpa pintu (perluPintu dimatikan)', TB, "const perluPintu = !!sampai;", "const perluPintu = false;"),
            ('klien: arsip lewat pintu dihitung 1 access call (potongan kebesaran → server menolak > 18)', KP, "if (op.hapus) return pembuka(op.lama) ? 1 : op.arsip ? 2 : 0;", "if (op.hapus) return pembuka(op.lama) ? 1 : op.arsip ? 0.0001 : 0;"),
            ('klien: saldo pembuka lewat pintu dihitung tanpa biaya pintu (kiriman kebesaran → perkiraan ≠ server / > 18)', KP, "  return pembuka(op.data) ? 1 : op.pulih ? 2 : 0;", "  return pembuka(op.data) ? 0.0001 : op.pulih ? 2 : 0;"),
            ('klien: pengembalian arsip tidak ditandai (Batalkan tertahan penjaga klien)', TK, "[], { pintu: 'pulih' }); if (j && j.terkunci) throw new Error(j.pesan);", "[]); if (j && j.terkunci) throw new Error(j.pesan);"),
            ('klien: penjaga klien membuka UBAH lewat pintu', KP, "  if (op.lama) return 0;   // dokumen sudah ada = UBAH → tidak ada pintu untuk ubah", "  if (op.lama) return 1;"),
            ('klien: saldo pembuka tahun mana pun lewat pintu', KP, "const pembuka = (d) => !!d && KP_KOLEKSI_PEMBUKA.indexOf(op.koleksi) >= 0 && d.tutupBuku === true && Number(d.tahunDari) === y;", "const pembuka = (d) => !!d && KP_KOLEKSI_PEMBUKA.indexOf(op.koleksi) >= 0 && d.tutupBuku === true;"),
            ('klien: saldo pembuka di koleksi mana pun (nota / uang keluar bertanda tutupBuku lolos penjaga)', KP, "const pembuka = (d) => !!d && KP_KOLEKSI_PEMBUKA.indexOf(op.koleksi) >= 0 && d.tutupBuku === true", "const pembuka = (d) => !!d && d.tutupBuku === true", 'P3 penjaga klien MENOLAK'),
            ('klien: titik kas lewat pintu tanggal berapa pun', KP, "return op.data.tanggal === y + '-12-31' ? 1 : kpTitikSebelum(op.data, pintu.titikSebelum) ? 2 : 0; }", "return 1; }", 'P3 penjaga klien MENOLAK'),
            ('klien: titik kas kembali (titikSebelum) dihitung tanpa baca berita acara (perkiraan ≠ server)', KP, "kpTitikSebelum(op.data, pintu.titikSebelum) ? 2 : 0; }", "kpTitikSebelum(op.data, pintu.titikSebelum) ? 1 : 0; }", 'P4 BATALKAN · tulis": perkiraan layar'),
            ('klien: salinan arsip dihitung tanpa access call (perkiraan ≠ server / potongan kebesaran)', KP, "    if (op.hapus && op.arsip) out.perluGet += (kpBebas(b, kini) ? 0 : 1) + (kunci ? 1 : 0);\n", "\n", 'arsip 2026 potongan'),
            ('klien: berita acara selesai / dibatalkan dihitung tanpa baca pintu (perkiraan ≠ server)', KP, "KP_ACARA_AKHIR.indexOf(op.data.status) >= 0 && !(op.lama && kpSama(op.data, op.lama))) out.perluGet += 1;", "KP_ACARA_AKHIR.indexOf(op.data.status) >= 0 && !(op.lama && kpSama(op.data, op.lama))) out.perluGet += 0;", 'access call ≠ server 1'),
            ('klien: berita acara TIDAK dikirim sendirian dulu (pintu satu kiriman dengan berita acara baru)', TB, "  if (pintu) acara.rencana.acaraDulu = true;\n", "\n", 'P2 kiriman 1 = berita acara'),
            ('klien: pembatalan lanjutan dari dibatalkan tidak menulis membatalkan sendirian dulu', TB, "const dulu = !!pintu && ['berjalan', 'terkunci', 'membatalkan'].indexOf(acara.status) < 0;", "const dulu = false;", 'P4b dari dibatalkan'),
            ('klien: titikSebelum berita acara tidak dibawa pintu (titik kembali ditolak penjaga)', TK, "  return kpPintu(d, kini, a && a.titikSebelum);", "  return kpPintu(d, kini);", 'P4 Batalkan tuntas'),
            ('klien: pintu tidak ditutup saat selesai', TB, ".concat(bkTutupPintu(tahun, w)), patch:", ", patch:"),
            ('klien: pintu tidak ditutup saat dibatalkan', TB, "akhirDokumen: [akhir].concat(bkTutupPintu(tahun, w, !!pintu)),", "akhirDokumen: [akhir],"),
            ('klien: kiriman lanjutan tidak membuka pintu lagi', TB, "const pintu = (susunPintu(tahun, wP).dokumen || [])[0] || null;", "const pintu = null;"),
            ('klien: kiriman pertama tidak memuat dokumen pintu (bkKirimanDari tanpa ekstra)', TB, "const kiriman = bkKirimanDari(berjalan, pintu ? [pintu] : []);", "const kiriman = bkKirimanDari(berjalan, []);"),
            ('klien: pintu tidak diperbarui (dianggap segar walau kedaluwarsa)', TB, "  if (!kunciSampai() || bkPintuSegar(tahun, bkJam(w))) return {};", "  if (!kunciSampai() || dokDiCache('pengaturan', KP_ID_PINTU)) return {};"),
            ('uang.js: arsip tanpa membuka pintu dulu', UG, "    if (!(await bukaPintu(tahun, 'Arsip'))) return false;\n", "\n"),
            ('uang.js: berita acara dibatalkan ditulis tanpa menutup pintu', UG, "tulisDokumen(r.akhirDokumen || [r.akhir], [], { tunggu: true })", "tulisDokumen([r.akhir], [], { tunggu: true })"),
        ]
        RUSAK_RULES = [
            ('rules: pintu tanpa getAfter (dibaca sebelum batch — kiriman pertama yang membuka pintu ditolak)', "let p = getAfter(/databases/$(database)/documents/pengaturan/pintuBuku);", "let p = get(/databases/$(database)/documents/pengaturan/pintuBuku);"),
            ('rules: hapus bulan terkunci tanpa salinan arsip diterima', "|| salinanArsip(getAfter(/databases/$(database)/documents/arsipTahun/$(string(y) + '|' + kol + '|' + id)), y, kol, id, resource.data));", "|| true);"),
            ('rules: salinan arsip tidak dibandingkan isinya (salinan berisi lain lolos)', "\n        && isi.diff(a.data.get('dok', {})).affectedKeys().hasOnly(['capServer']);", ";", 'P5f'),
            ('rules: salinan arsip karangan diterima (arsipTahun owner bebas)', "allow create, update: if owner() && arsipSah(id);", "allow create, update: if owner();", 'P3o'),
            ('rules: salinan arsip bulan terkunci tidak diikat ke aslinya', " || salinanAsli(d))));", " || true)));", 'P5e'),
            ('rules: saldo pembuka di koleksi mana pun (kolPembuka dicabut)', "      return kol in ['batchMasuk', 'piutangMutasi',", "      return true || kol in ['batchMasuk', 'piutangMutasi',", 'P3i'),
            ('rules: berita acara dibaca SESUDAH batch (ritual karangan satu kiriman lolos)', "let a = get(/databases/$(database)/documents/tutupBukuAcara/$(string(y)));", "let a = getAfter(/databases/$(database)/documents/tutupBukuAcara/$(string(y)));", 'P2a'),
            ('rules: pintu untuk tahun lampau mana pun (bukan hanya tahun lalu)', "y is int && y == wib().year() - 1", "y is int && y < wib().year()", 'P2b'),
            ('rules: berita acara selesai walau pintu terbuka', "      return !(b.get('status', '') in ['selesai', 'dibatalkan']) || pintuMati(", "      return true || pintuMati(", 'P3m'),
            ('rules: berita acara baru bentuk / jam apa saja', "allow create: if owner() && acaraBaru(id);", "allow create: if owner();", 'P2c'),
            ('rules: berita acara selesai bisa dihapus (lalu dibuat lagi)', "allow delete: if owner() && resource.data.get('status', '') == 'dibatalkan';", "allow delete: if owner();", 'P2y'),
            ('rules: titik kas lewat pintu tanggal berapa pun ≤ 31 Des', " && (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));", ";", 'P3k'),
            ('rules: pintu membuka UBAH juga (saldo pembuka bertanggal lama bisa diubah)', "      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('piutangMutasi',",
             "      allow update: if (owner() && tglUbah('tanggal')) || (owner() && pintuTulis('piutangMutasi', id, bulanDok(request.resource.data, 'tanggal')));\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('piutangMutasi',"),
            ('rules: pindahUang ikut berpintu', "    match /pindahUang/{id} {\n      allow read: if owner();\n      allow create: if owner() && tglBaru('tanggal');\n      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && tglLama('tanggal');",
             "    match /pindahUang/{id} {\n      allow read: if owner();\n      allow create: if owner() && tglBaru('tanggal');\n      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('pindahUang', id, bulanDok(resource.data, 'tanggal')));"),
            ('rules: saldo pembuka tahun mana pun', "((kolPembuka(kol) && d.get('tutupBuku', false) == true && d.get('tahunDari', 0) == y) || pulihArsip(kol, id, y))", "((kolPembuka(kol) && d.get('tutupBuku', false) == true) || pulihArsip(kol, id, y))"),
            ('rules: kasir@ lewat pintu', "(owner() && pintuTulis('piutangMutasi',", "((owner() || kasir()) && pintuTulis('piutangMutasi',"),
            ('rules: titik kas tanpa pintu (Desember terkunci → titik 31 Des ditolak)', "(id != 'titikKas' || tglBaru('tanggal') || pintuTitik())", "(id != 'titikKas' || tglBaru('tanggal'))"),
            ('rules: pengembalian arsip ditolak (Batalkan buntu)', "      return salinanArsip(get(/databases/$(database)/documents/arsipTahun/$(string(y) + '|' + kol + '|' + id)), y, kol, id, request.resource.data);", "      return false;"),
        ]
        kode = 0
        # kontrol bertanda `harap` (sanggahan rules 7 Okt) wajib berbunyi karena SEBABNYA (teks itu ada di salah satu kegagalan), bukan karena kegagalan lain
        def lapor(nama, g, harap):
            kena = [x for x in g if harap in x] if harap else g
            print(('BERBUNYI ' if kena else 'DIAM!!   ' if not g else 'SALAH SEBAB ') + nama + ' → ' + ((kena or g)[0][:150] if g else '-'))
            return 0 if kena else 3
        for x in RUSAK:
            nama, berkas, a, b = x[:4]; harap = x[4] if len(x) > 4 else None
            t = baca(berkas)
            if t.count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = jalan({berkas: t.replace(a, b)})
            kode = max(kode, lapor(nama, g, harap))
        RS = baca('firestore.rules')
        for x in RUSAK_RULES:
            nama, a, b = x[:3]; harap = x[3] if len(x) > 3 else None
            if RS.count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = jalan(teks_rules=RS.replace(a, b))
            kode = max(kode, lapor(nama, g, harap))
        sys.exit(kode)
    l, g, info = jalan()
    print('TUTUP BUKU 2027 lewat pintu (kotak pasir + rules v7 dinilai penafsir mini): %d lulus · %d gagal · %s' % (l, len(g), json.dumps(info, ensure_ascii=False)))
    [print('   ✗ ' + x) for x in g]
    sys.exit(1 if g else 0)
