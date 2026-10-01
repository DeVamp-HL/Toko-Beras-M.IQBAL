#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tutup_buku_bertahap.py — rancangan TUTUP BUKU BERTAHAP (Okt 2026; owner 1 Okt: batas 18 pemeriksaan kunci per kiriman tetap) di jsc.
KOTAK PASIR (ANGKA & NAMA CONTOH, bukan angka toko). Tanpa peramban.

Yang dijaga:
  T0  saldo pembuka ≤ 18 pemeriksaan = SATU kiriman seperti dulu (tanpa berita acara 'berjalan')
  T1  40 nama berutang (+ 1 bon pemasok + titik kas 31 Des) → 3 kiriman, tiap kiriman ≤ 18 pemeriksaan (penjaga pusat meloloskan), berita acara
      'berjalan' di kiriman PERTAMA, penanda (titik kas · pengaturan/tutupBuku · berita acara 'terkunci') di kiriman TERAKHIR, tanpa id ganda
  T2  sesudah kiriman 1 saja: tahun 2026 masih utuh — era tidak pindah, Agustus tidak FINAL, 12 baris 31 Des sama (piutang tidak dobel), kemajuan 1 dari 3
  T3  putus di kiriman 2 → lanjutkan: hanya kiriman 2 & 3 (id & isi sama), lalu hanya 3; sesudahnya terkunci, era 2026, pembuka tidak dobel
  T4  arsip terputus → dilanjutkan dari sisa; kemajuan arsip; pemeriksaan ulang dari mesin (hari tutup buku) sama; langkah 7 memakai tahun yang terkunci
      (dulu layar memakai tahun berjalan 2027 → "Kunci tahunnya dulu", berita acara tak pernah selesai) + STATIS uang.js
  T5  batalkan dari 'berjalan' (dan pembatalan yang terputus) → semua pembuka ditarik, era tetap, mulai lagi bisa
  T6  batalkan dari 'terkunci' dengan 19 nama + bon → tiap kiriman tarik ≤ 18 (dulu satu kiriman 21+ → ditolak penjaga, tutup buku tak bisa dibatalkan)
  T7  titik kas sudah maju ke 2 Jan → patokan 31 Des dari tutup hari 31 Des (kolom titik); titik 2 Jan tidak ditimpa; tutup hari menulis kolom titik
  T8  penjualan 1 Jan sebelum tutup buku → pemeriksaan ulang TIDAK berbunyi palsu
  T9  catatan 2026 berubah di tengah jalan → lanjut ditolak (batalkan dulu)
  T10 (asap, bila ada cadangan lokal di _privat/) data toko pada 5 Jan 2027: dipecah, tiap kiriman ≤ 18; batal juga ≤ 18
  §8 (syarat wajib hasil tinjauan 1 Okt, docs/rancangan-tutup-buku-bertahap.md):
  N1  HP STAF (tanpa tutupBukuAcara) melihat angka yang SAMA dengan HP owner di tiap titik putus — penanda = batch pembuka ber-penandaBuku (koleksi yang staf baca)
  N2  Lanjutkan sesudah tutup hari Januari: titik 31 Des yang disusun saat mulai TIDAK dikirim (aturan titik dinilai saat kirim), titikDitulis false
  N3  mulai di masa tenggang (2 Jan), lanjut 5 Jan: sisa dipecah ulang dengan jam sekarang — tiap kiriman ≤ 18, penanda tetap terakhir, pembuka tepat sekali

    python3 alat-uji/uji_tutup_buku_bertahap.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tutup_buku_bertahap.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
import uji_uang_baru  # noqa: E402
JSC = uji_kunci_periode.JSC
MODUL = uji_kunci_periode.MODUL + ['baru/js/layar/sistem-logika.js']
JAM = "var __KINI = new Date('2027-01-05T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
function coba(nama, f) { try { f(); } catch (e) { gagal.push(nama + ' → JATUH: ' + (e && e.message ? e.message : e)); } }
var TITIK31 = { tanggal: '2026-12-31', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 };
function kotak(nNama, tambah) {
  KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
  pasok('aturanToko', []); pasok('tutupBukuAcara', []); pasok('pengaturan', []); while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []);
  var jual = KOTAK.penjualan.slice(); for (var q = 0; q < nNama; q++) jual.push({ id: 'k' + q, tanggal: '2026-08-' + String(2 + (q % 20)).padStart(2, '0'), jam: '10:00', caraBayar: 'Kredit', jenis: 'karung', merkSumber: 'Angsa', totalKg: 10, beratKarungAcuan: 50, jumlahKarung: 0.2, hargaTotal: 200000, hppTotalSaatJual: 130000, namaPelanggan: 'Pengutang Contoh ' + q });
  (tambah || []).forEach(function (x) { jual.push(x); }); pasok('penjualan', jual);
  localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(TITIK31));
}
var n0 = 50000; function jam(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: '10:00', kini: new Date(iso).toISOString(), idUnik: function () { n0 += 1; return n0; } }; }
var D = { paraf: { owner: true, saksi: true }, saksi: 'Saksi Contoh', langkah: {} };
// satu kiriman "masuk server": penjaga pusat yang sama dengan layar (bulan terkunci / > 18 pemeriksaan = tidak dikirim), lalu cache
var tolakPenjaga = [];
function kirim(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) { tolakPenjaga.push(j.pesan); return false; }
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); return true; }
function idKiriman(k) { return k.dokumen.map(function (x) { return x.koleksi + '|' + x.data.id + '|' + (x.data.status || ''); }).join(','); }
function baris(B) { var o = {}; B.harta.concat(B.utang).forEach(function (b) { o[b.id] = b.n; }); return o; }
function samaBaris(a, b) { return Object.keys(a).every(function (k) { return (a[k] === null && b[k] === null) || (a[k] !== null && b[k] !== null && Math.abs(a[k] - b[k]) < 0.5); }); }
var PEMBUKA = ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'];
function nPembukaMentah(tahun) { var n = 0; PEMBUKA.forEach(function (c) { cacheMentah(c).forEach(function (x) { if (x.tutupBuku && Number(x.tahunDari) === tahun) n += 1; }); }); return n; }
function acara(tahun) { return ambilTutupBukuAcara().find(function (a) { return Number(a.tahun) === tahun; }) || null; }
var R, W, L, B;

// ---- T0 · sedikit nama = satu kiriman seperti dulu
coba('T0', function () { kotak(5); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W);
  ok('T0 5 nama berutang: SATU kiriman (≤ 18), tanpa berita acara berjalan; kiriman itu sudah membawa penanda terkunci', !R.tolak && R.kiriman && R.kiriman.length === 1 && R.kiriman[0].get <= 18
    && !R.kiriman[0].dokumen.some(function (x) { return x.koleksi === 'tutupBukuAcara' && x.data.status === 'berjalan'; }) && R.kiriman[0].dokumen.some(function (x) { return x.koleksi === 'tutupBukuAcara' && x.data.status === 'terkunci'; }), J(R.tolak || R.kiriman.map(function (k) { return k.get; }))); });

// ---- T1 · 40 nama → 3 kiriman
coba('T1', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W);
  ok('T1 40 nama berutang tidak ditolak (dipecah)', !R.tolak, R.tolak);
  var K = R.kiriman || []; var gets = K.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); });
  ok('T1 3 kiriman; tiap kiriman ≤ 18 pemeriksaan kunci menurut penjaga pusat (18 + 18 + 7)', K.length === 3 && gets.every(function (g) { return g <= 18; }) && K.every(function (k) { return !jagaKunci(k.dokumen, k.hapus || []); }), J(gets));
  ok('T1 berita acara BERJALAN (rencana + dokumen pembuka) di kiriman PERTAMA; penanda (titik 31 Des · pengaturan/tutupBuku · berita acara TERKUNCI) hanya di kiriman TERAKHIR',
    K.length === 3 && K[0].dokumen[0].koleksi === 'tutupBukuAcara' && K[0].dokumen[0].data.status === 'berjalan' && K[0].dokumen[0].data.rencana.n === 3 && K[0].dokumen[0].data.pembuka.length === R.acara.nPembuka
    && K.slice(0, 2).every(function (k) { return !k.dokumen.some(function (x) { return (x.koleksi === 'pengaturan') || (x.koleksi === 'tutupBukuAcara' && x.data.status === 'terkunci'); }); })
    && ['titikKas', 'tutupBuku'].every(function (id) { return K[2].dokumen.some(function (x) { return x.koleksi === 'pengaturan' && x.data.id === id; }); }) && K[2].dokumen.some(function (x) { return x.koleksi === 'tutupBukuAcara' && x.data.status === 'terkunci'; }));
  var ids = {}; var dobel = 0, n = 0; K.forEach(function (k) { k.dokumen.forEach(function (x) { if (!x.data.tutupBuku) return; n += 1; var key = x.koleksi + '|' + x.data.id; if (ids[key]) dobel += 1; ids[key] = 1; }); });
  ok('T1 semua dokumen saldo pembuka ada tepat sekali di kiriman (' + R.acara.nPembuka + ')', n === R.acara.nPembuka && dobel === 0, J([n, dobel])); });

// ---- T2 · sesudah kiriman 1 saja: tahun lama utuh
coba('T2', function () { var sebelumMesin = baris(barisTahun(2026)); var piutang0 = hitungPiutang('2026-12-31').reduce(function (a, x) { return a + x.sisa; }, 0);
  ok('T2 kiriman 1 masuk (penjaga pusat meloloskan)', kirim(R.kiriman[0]), tolakPenjaga.slice(-1)[0]);
  ok('T2 era TIDAK pindah (bkEra null, ssEraTutupBuku null), layar K6 tetap tahun 2026, Agustus 2026 tidak FINAL', bkEra() === null && ssEraTutupBuku() === null && tahunBuku(new Date(__KINI)).tahun === 2026 && lpFinal('2026-08') === false, J([bkEra(), ssEraTutupBuku(), tahunBuku(new Date(__KINI)).tahun, lpFinal('2026-08')]));
  ok('T2 mesin tidak melihat pembuka yang baru sebagian: 12 baris 31 Des sama, piutang tidak dobel', samaBaris(sebelumMesin, baris(barisTahun(2026))) && hitungPiutang('2026-12-31').reduce(function (a, x) { return a + x.sisa; }, 0) === piutang0, J([piutang0, hitungPiutang('2026-12-31').reduce(function (a, x) { return a + x.sisa; }, 0)]));
  var KM = kemajuanBuku(); ok('T2 kemajuan: pembuka 1 dari 3, kalimat menyebut tahun masih terbuka', KM && KM.fase === 'pembuka' && KM.sudah === 1 && KM.total === 3 && /MASIH TERBUKA/.test(KM.teks), J(KM));
  ok('T2 mulai baru ditolak selama berjalan', /sedang berjalan/.test(susunKunci(2026, D, W).tolak || ''), susunKunci(2026, D, W).tolak); });

// ---- T3 · putus di kiriman 2 → lanjut
coba('T3', function () { L = lanjutBuku(2026);
  ok('T3 lanjut sesudah putus di kiriman 2: tinggal kiriman 2 & 3, isi & id SAMA dengan rencana', !L.tolak && L.sudah === 1 && L.kiriman.length === 2 && L.kiriman[0].ke === 2 && idKiriman(L.kiriman[0]) === idKiriman(R.kiriman[1]) && idKiriman(L.kiriman[1]) === idKiriman(R.kiriman[2]), J(L.tolak || [L.sudah, L.kiriman.map(function (k) { return k.ke; })]));
  ok('T3 kiriman 2 masuk', kirim(L.kiriman[0]), tolakPenjaga.slice(-1)[0]);
  L = lanjutBuku(2026); ok('T3 lanjut lagi: hanya kiriman 3 (kiriman 2 tidak dikirim ulang)', !L.tolak && L.kiriman.length === 1 && L.kiriman[0].ke === 3, J(L.tolak || L.kiriman.map(function (k) { return k.ke; })));
  ok('T3 kiriman 3 (penanda) masuk', kirim(L.kiriman[0]), tolakPenjaga.slice(-1)[0]);
  ok('T3 sesudah penanda: berita acara terkunci, era 2026, K6 pindah ke 2027; pembuka tepat ' + R.acara.nPembuka + ' (tidak dobel); lanjut tidak ada lagi',
    acara(2026).status === 'terkunci' && bkEra() === 2026 && tahunBuku(new Date(__KINI)).tahun === 2027 && nPembukaMentah(2026) === R.acara.nPembuka && !!lanjutBuku(2026).tolak, J([acara(2026).status, bkEra(), nPembukaMentah(2026)])); });

// ---- T4 · arsip terputus → lanjut; pemeriksaan ulang
coba('T4', function () { var KM = kemajuanBuku(); var total = R.arsip.length;
  ok('T4 kemajuan arsip: 0 dari ' + total + ' (angka toko dobel sampai habis)', KM && KM.fase === 'arsip' && KM.sisa === total && /DOBEL/.test(KM.teks), J(KM));
  arsipkanDokumen(2026, arsipBuku(2026).daftar.slice(0, 18)); KM = kemajuanBuku();
  ok('T4 arsip putus sesudah potongan 1 → kemajuan 18 dari ' + total + '; sisa dihitung ulang dari catatan yang masih ada', KM.fase === 'arsip' && KM.sudah === 18 && arsipBuku(2026).n === total - 18, J(KM));
  arsipkanDokumen(2026, arsipBuku(2026).daftar); KM = kemajuanBuku();
  ok('T4 lanjut arsip sampai habis → fase selesaikan', KM && KM.fase === 'selesaikan' && arsipBuku(2026).n === 0, J(KM));
  var PU = periksaUlangBuku(2026); ok('T4 pemeriksaan ulang dari mesin (hari tutup buku) = sebelum apa pun dikirim: 12 baris sama', PU && PU.semuaSama, J(PU && PU.beda));
  var KMs = kemajuanBuku(); var SL = susunSelesai(KMs.tahun, 'cadangan-sesudah.json', W); if (!SL.tolak) kirim(SL);
  ok('T4 langkah 7 memakai tahun yang TERKUNCI (2026, bukan tahun layar 2027): selesai; sesudahnya tidak ada yang tertunda', KMs.tahun === 2026 && tahunBuku(new Date(__KINI)).tahun === 2027 && !SL.tolak && acara(2026).status === 'selesai' && kemajuanBuku() === null, J([KMs, SL.tolak, acara(2026).status])); });

// ---- T5 · batal dari berjalan (+ pembatalan terputus)
coba('T5', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var s0 = baris(barisTahun(2026)); kirim(R.kiriman[0]); kirim(R.kiriman[1]);
  B = susunBatal(2026, [], W); ok('T5 batal dari berjalan: tiap kiriman tarik ≤ 18, tanpa ubah era/titik', !B.tolak && B.kiriman.every(function (k) { return butuhGet(k.dokumen, k.hapus) <= 18; }) && !B.kiriman[0].dokumen.some(function (x) { return x.koleksi === 'pengaturan'; }), J(B.tolak || B.kiriman.map(function (k) { return k.get; })));
  kirim(B.kiriman[0]);
  ok('T5 pembatalan putus sesudah kiriman 1: mulai baru ditolak, kemajuan fase batal', /Pembatalan tutup buku 2026 belum selesai/.test(susunKunci(2026, D, W).tolak || '') && (kemajuanBuku() || {}).fase === 'batal', J([susunKunci(2026, D, W).tolak, kemajuanBuku()]));
  B = susunBatal(2026, [], W); B.kiriman.forEach(kirim); kirim({ dokumen: [B.akhir] });
  ok('T5 pembatalan dilanjutkan: semua pembuka ditarik, berita acara dibatalkan, era null, 12 baris sama seperti sebelum; mulai lagi BISA', nPembukaMentah(2026) === 0 && acara(2026).status === 'dibatalkan' && bkEra() === null && samaBaris(s0, baris(barisTahun(2026))) && !susunKunci(2026, D, W).tolak, J([nPembukaMentah(2026), acara(2026).status, susunKunci(2026, D, W).tolak])); });

// ---- T6 · batal dari terkunci, 19 nama + bon
coba('T6', function () { kotak(19); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var s0 = baris(barisTahun(2026)); var nJual = ambilPenjualanSemua().length;
  R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  B = susunBatal(2026, arsipSimulasi(), W); var g = B.tolak ? [] : B.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus); });
  ok('T6 batal dari terkunci (19 nama + bon): dipecah, tiap kiriman ≤ 18 dan lolos penjaga pusat', !B.tolak && B.kiriman.length >= 2 && g.every(function (x) { return x <= 18; }) && B.kiriman.every(function (k) { return !jagaKunci(k.dokumen, k.hapus); }), J(B.tolak || g));
  B.kiriman.forEach(kirim); pulihkanArsip(2026, B.pulih); kirim({ dokumen: [B.akhir] });
  ok('T6 sesudah batal: era null, penjualan kembali utuh, 12 baris 31 Des sama seperti sebelum', bkEra() === null && ambilPenjualanSemua().length === nJual && samaBaris(s0, baris(barisTahun(2026))) && nPembukaMentah(2026) === 0, J([bkEra(), ambilPenjualanSemua().length, nJual])); });

// ---- T7 · titik kas sudah maju ke Januari
coba('T7', function () { kotak(5); var S31 = saldoKantong('2026-12-31');
  pasok('tutupHari', [{ id: '2026-12-31', tanggal: '2026-12-31', jam: '20:00', omzet: 0, titik: { laci: S31.laci, rekening: S31.rekening, amplop: S31.amplop, brankas: S31.brankas } }]);
  localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2027-01-02', laci: S31.laci + 500000, brankas: S31.brankas, rekening: S31.rekening, amplop: S31.amplop }));
  W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var kas = R.tolak ? {} : baris({ harta: R.sebelum.harta, utang: [] });
  ok('T7 titik kas 2 Jan: kunci TIDAK ditolak; uang per tempat 31 Des = hitungan tutup hari 31 Des; titik 2 Jan tidak ditimpa (titik tidak ditulis)', !R.tolak && R.titikTahun && R.titikTahun.dari === 'tutupHari' && kas.laci === S31.laci && kas.brankas === S31.brankas && kas.rekening === S31.rekening && kas.amplop === S31.amplop && R.titik === null && !R.dokumen.some(function (x) { return x.data.id === 'titikKas'; }), J(R.tolak || [R.titikTahun, kas]));
  R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  ok('T7 sesudah kunci & arsip: titik kas tetap 2 Jan; pemeriksaan ulang sama', ambilTitikKas().tanggal === '2027-01-02' && (periksaUlangBuku(2026) || {}).semuaSama, J([ambilTitikKas(), periksaUlangBuku(2026) && periksaUlangBuku(2026).beda]));
  // tutup hari menulis kolom titik di dokumennya = isi titik kas malam itu
  kotak(0); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-12-30', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
  var W31 = jam('2026-12-31T20:00:00+07:00'); var DT = { lembar: { 100000: 20 }, receh: 0, alasan: 'uji', rekPilih: '', rekNyata: '', sisih: null, timbang: {}, status: { laci: 'beres', timbang: 'lewat', amankan: 'lewat' } };
  var TT = susunTutup(DT, W31, true); var dt = TT.tolak ? null : TT.dokumen.find(function (x) { return x.koleksi === 'tutupHari'; }).data;
  ok('T7 tutup hari 31 Des: dokumen tutupHari membawa titik = titik kas malam itu (laci, rekening, amplop, brankas)', !!dt && !!dt.titik && ['laci', 'rekening', 'amplop', 'brankas'].every(function (k) { return dt.titik[k] === TT.titik[k]; }), J(TT.tolak || (dt && dt.titik))); });

// ---- T8 · penjualan 1 Jan
coba('T8', function () { kotak(5, [{ id: 'jan1', tanggal: '2027-01-01', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 }]);
  W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var PU = periksaUlangBuku(2026); ok('T8 ada penjualan 1 Jan: pemeriksaan ulang dari mesin TIDAK berbunyi palsu (stok & laci sama)', !R.tolak && PU && PU.semuaSama, J(R.tolak || (PU && PU.beda))); });

// ---- T9 · catatan tahun lama berubah di tengah jalan
coba('T9', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]);
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'susulan', tanggal: '2026-12-20', jam: '10:00', caraBayar: 'Kredit', jenis: 'karung', merkSumber: 'Angsa', totalKg: 10, beratKarungAcuan: 50, jumlahKarung: 0.2, hargaTotal: 200000, hppTotalSaatJual: 130000, namaPelanggan: 'Pengutang Susulan' } }]);
  L = lanjutBuku(2026); ok('T9 nota 20 Des masuk di tengah jalan → lanjut DITOLAK dengan kalimat (batalkan, lalu mulai lagi)', !!L.tolak && /berubah sejak tutup buku dimulai/.test(L.tolak), J(L)); });

// ---- §8 no. 1 · HP STAF: hanya koleksi yang staf dengar (akses.js pendengarPeran — tanpa tutupBukuAcara, kasbon, utang, …); angka HARUS sama dengan HP owner
function sebagaiStaf(f) {
  var dengar = {}; pendengarPeran({ jenis: 'aktif', peran: 'karyawan', nama: 'staf', uid: 'u1' }).forEach(function (p) { dengar[p.nama] = p.dok || true; });
  var simpan = {}; KOLEKSI.forEach(function (k) { simpan[k.nama] = cacheMentah(k.cache); var d = dengar[k.nama];
    if (!d) pasok(k.nama, []); else if (d !== true) pasok(k.nama, cacheMentah(k.cache).filter(function (x) { return d.indexOf(String(x.id)) >= 0; })); });
  try { return f(); } finally { KOLEKSI.forEach(function (k) { pasok(k.nama, simpan[k.nama]); }); }
}
function lihatToko() { var st = hitungStokKarungPerMerk(); var kg = 0, rp = 0; Object.keys(st).forEach(function (m) { kg += st[m].sisaKg; rp += st[m].sisaKg * (st[m].hppTerakhirPerKg || 0); });
  var km = hitungStokKemasan(); var u = 0; Object.keys(km).forEach(function (k) { u += km[k].sisaUnit; });
  var bk = hitungStokBahanKemasan(), bl = hitungStokBahanLiteran(); var pcs = 0; Object.keys(bk).forEach(function (j) { pcs += bk[j].sisaPcs; }); Object.keys(bl).forEach(function (j) { pcs += bl[j].sisaPcs; });
  return J({ kg: Math.round(kg * 10) / 10, rp: Math.round(rp), kemasan: u, kantong: pcs, piutang: hitungPiutang().reduce(function (a, x) { return a + x.sisa; }, 0), era: ssEraTutupBuku() }); }
var titikPutus = [];
function bandingStaf(label) { var o = lihatToko(); var s = sebagaiStaf(lihatToko); titikPutus.push({ label: label, owner: o, staf: s }); }
function stafBeda() { return titikPutus.filter(function (t) { return t.owner !== t.staf; }).map(function (t) { return t.label + ' owner ' + t.owner + ' staf ' + t.staf; }); }
coba('N1', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); titikPutus = [];
  var awal = lihatToko(); bandingStaf('awal');
  R.kiriman.forEach(function (k, i) { kirim(k); bandingStaf('sesudah kiriman ' + (i + 1) + ' dari ' + R.kiriman.length); });
  var A = arsipBuku(2026).daftar; arsipkanDokumen(2026, A.slice(0, 18)); bandingStaf('arsip 18 dari ' + A.length); arsipkanDokumen(2026, arsipBuku(2026).daftar); bandingStaf('arsip habis');
  B = susunBatal(2026, arsipSimulasi(), W); B.kiriman.forEach(function (k, i) { kirim(k); bandingStaf('batal dari terkunci · kiriman tarik ' + (i + 1) + ' dari ' + B.kiriman.length); });
  pulihkanArsip(2026, B.pulih); kirim({ dokumen: [B.akhir] }); bandingStaf('sesudah batal');
  kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]); kirim(R.kiriman[1]);
  B = susunBatal(2026, [], W); B.kiriman.forEach(function (k, i) { kirim(k); bandingStaf('batal dari berjalan · kiriman tarik ' + (i + 1) + ' dari ' + B.kiriman.length); });
  var staf2 = titikPutus.filter(function (t) { return /kiriman (1|2) dari 3$/.test(t.label); });
  ok('N1 HP staf = HP owner di SETIAP titik putus (kiriman pembuka, arsip, batal dari terkunci & dari berjalan) — ' + titikPutus.length + ' titik', titikPutus.length >= 9 && !stafBeda().length, J(stafBeda()));
  ok('N1 selama berjalan HP staf melihat tahun 2026 utuh (stok & piutang tidak dobel)', staf2.length === 2 && staf2.every(function (t) { return t.staf === awal; }), J(staf2)); });

// ---- §8 no. 2 · Lanjutkan sesudah tutup hari Januari: titik kas Januari (hitungan fisik) TIDAK ditimpa titik 31 Des yang disusun saat mulai
function dokDi(K, koleksi, id) { var out = []; (K || []).forEach(function (k) { k.dokumen.forEach(function (x) { if (x.koleksi === koleksi && (id === undefined || String(x.data.id) === id)) out.push(x.data); }); }); return out; }
coba('N2', function () { kotak(40); W = jam('2027-01-02T07:00:00+07:00'); R = susunKunci(2026, D, W); var titikRencana = dokDi(R.kiriman, 'pengaturan', 'titikKas').map(function (t) { return t.tanggal; });
  kirim(R.kiriman[0]);
  var T2 = { id: 'titikKas', tanggal: '2027-01-02', laci: 2450000, brankas: 10000000, rekening: 3000000, amplop: 1000000, diubahPada: '2027-01-02T13:00:00.000Z' };
  terapkanKeCache([{ koleksi: 'pengaturan', data: T2 }]); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(T2));
  jam('2027-01-03T08:00:00+07:00'); L = lanjutBuku(2026); var bawa = dokDi(L.kiriman, 'pengaturan', 'titikKas'); var ak = dokDi(L.kiriman, 'tutupBukuAcara').filter(function (a) { return a.status === 'terkunci'; })[0];
  (L.kiriman || []).forEach(kirim); var dok = dokDiCache('pengaturan', 'titikKas');
  ok('N2 mulai 2 Jan pagi (rencana membawa titik 31 Des), tutup hari 2 Jan memajukan titik, Lanjutkan 3 Jan: titik 31 Des TIDAK dikirim, berita acara titikDitulis false, titik kas tetap 2 Jan (laci 2.450.000)',
    titikRencana.join() === '2026-12-31' && !L.tolak && !bawa.length && !!ak && ak.titikDitulis === false && !L.titik && dok.tanggal === '2027-01-02' && dok.laci === 2450000 && acara(2026).status === 'terkunci',
    J([titikRencana, L.tolak, bawa, ak && ak.titikDitulis, dok]));
  B = susunBatal(2026, [], W); ok('N2 batal sesudahnya tidak mengembalikan titik kas (titik 2 Jan dipertahankan)', !B.tolak && !B.titik && !dokDi(B.kiriman, 'pengaturan', 'titikKas').length, J(B.tolak || B.titik)); });

// ---- §8 no. 3 · mulai di masa tenggang (2 Jan: tulisan bertanggal Desember tanpa pemeriksaan), lanjut 5 Jan: kiriman sisa dipecah ulang dengan jam SEKARANG
coba('N3', function () { var tambah = []; for (var q = 0; q < 20; q++) tambah.push({ id: 'd' + q, tanggal: '2026-12-' + String(10 + (q % 15)).padStart(2, '0'), jam: '10:00', caraBayar: 'Kredit', jenis: 'karung', merkSumber: 'Angsa', totalKg: 10, beratKarungAcuan: 50, jumlahKarung: 0.2, hargaTotal: 200000, hppTotalSaatJual: 130000, namaPelanggan: 'Pengutang Desember ' + q });
  kotak(25, tambah); W = jam('2027-01-02T10:00:00+07:00'); R = susunKunci(2026, D, W); var rencana = R.tolak ? R.tolak : R.kiriman.map(function (k) { return k.get; });
  kirim(R.kiriman[0]); jam('2027-01-05T10:00:00+07:00'); var lama = R.kiriman.slice(1).map(function (k) { return butuhGet(k.dokumen, k.hapus || []); });
  L = lanjutBuku(2026); var g = L.tolak ? [] : L.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); }); var masuk = L.tolak ? [] : L.kiriman.map(kirim);
  ok('N3 kiriman rencana 2 Jan dihitung pada 5 Jan > 18 (keadaan yang dulu ditolak selamanya)', lama.some(function (x) { return x > 18; }), J([rencana, lama]));
  ok('N3 lanjut 5 Jan: sisa dipecah ulang — tiap kiriman ≤ 18 & lolos penjaga pusat, nomor kiriman melanjutkan (mulai 2), penanda hanya di kiriman terakhir; sesudahnya terkunci, tiap pembuka tepat sekali',
    !L.tolak && L.kiriman.length >= 2 && g.every(function (x) { return x <= 18; }) && masuk.every(Boolean) && L.kiriman[0].ke === 2 && L.kiriman.every(function (k, i) { return k.penanda === (i === L.kiriman.length - 1); })
    && acara(2026).status === 'terkunci' && nPembukaMentah(2026) === R.acara.nPembuka && !lanjutBuku(2026).kiriman, J([rencana, g, L.tolak, masuk, tolakPenjaga.slice(-1)])); });

print(JSON.stringify({ lulus: lulus, gagal: gagal, penjaga: tolakPenjaga }));
"""

ASAP = r"""
KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var salah = []; var n27 = 90000; var W = { tanggal: '2027-01-05', jam: '10:00', kini: new Date(__KINI).toISOString(), idUnik: function () { n27 += 1; return n27; } };
var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'uji asap', langkah: {} }, W); var out = { tolak: R.tolak || '' };
if (!R.tolak) { out.kiriman = R.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); }); out.pembuka = R.acara.nPembuka; out.arsip = R.arsip.length;
  if (out.kiriman.some(function (g) { return g > 18; })) salah.push('ada kiriman pembuka > 18');
  R.kiriman.forEach(function (k) { terapkanKeCache(k.dokumen); });
  var B = susunBatal(2026, [], W); out.batal = B.tolak ? B.tolak : B.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus); });
  if (B.tolak || out.batal.some(function (g) { return g > 18; })) salah.push('batal data toko > 18 atau ditolak');
} else salah.push('ditolak: ' + R.tolak);
out.salah = salah; print(JSON.stringify(out));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def bundelan():
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))


def utama(js):
    h, e = jalan(JAM + js + '\nvar KOTAK = ' + json.dumps(uji_uang_baru.KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


STATIS = [
    ('kiriman bertahap menunggu pengakuan server & berhenti dengan kalimat kiriman ke-n', ["await tulisDokumen(k.dokumen, k.hapus || [], { tunggu: true })", "'Berhenti di kiriman ' + k.ke + ' dari ' + k.total"]),
    ('pita kemajuan K6: lanjutkan / batalkan / selesaikan', ["BK.kemajuanBuku()", 'data-aksi="bkLanjut"', 'data-k="tb-selesaikan"']),
    ('langkah 7 memakai tahun yang terkunci', ["const tahun = KM7 && KM7.fase === 'selesaikan' ? KM7.tahun :"]),
    ('patokan kas tahun di layar (bukan titik kas sekarang)', ["const SB = BK.barisTahun(T.tahun); const B = s.sesudahLive || bandingB(s, T);", "const bandingB = (s, T) => { const SB = BK.barisTahun(T.tahun);"]),
    ('§8 no. 2 · Lanjutkan menyetel titik kas perangkat HANYA dari titik yang ikut kiriman lanjut (lanjutBuku.titik)', ["jalankanBuku(KM.tahun, Lj.kiriman || [], Lj.titik || null,"]),
]
RUSAK = [
    ('saldo pembuka tidak dipecah (sekali kirim)', 'baru/js/layar/tutup-buku-logika.js', "const Pt = kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] }))",
     "const Pt = { potongan: [{ dokumen: P.dokumen.concat(penanda, [{ koleksi: 'tutupBukuAcara', data: acara }]), get: 0 }] } || kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] }))"),
    ('mesin melihat pembuka yang belum selesai (saringan data mati)', 'baru/js/data/toko.js', "const bkSaring = (arr) => { const s = arr.filter(pembukaBerlaku);", "const bkSaring = (arr) => { return arr; const s = arr.filter(pembukaBerlaku);"),
    ('§8 no. 1 · HP staf: pembuka tanpa penanda tetap terlihat (saringan hanya dari berita acara)', 'baru/js/data/toko.js', "return !k.sembunyi[t] && (!x.bertahap || !!k.penanda[t]); }", "return !k.sembunyi[t]; }"),
    ('§8 no. 1 · batch penanda ikut kiriman PERTAMA (bukan terakhir)', 'baru/js/layar/tutup-buku-logika.js', "const Pt = kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] })).concat([{ dokumen: [tanda].concat(penanda,",
     "const Pt = kpPotong(P.dokumen.map((x) => ({ dokumen: [x] })).concat([{ dokumen: [].concat(penanda,"),
    ('§8 no. 1 · batal menghapus batch penanda TERAKHIR (bukan di kiriman pertama)', 'baru/js/layar/tutup-buku-logika.js', "const P = kpPotong([{ dokumen: awal, hapus: tanda }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] }))),",
     "const P = kpPotong([{ dokumen: awal, hapus: [] }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] })), [{ dokumen: [], hapus: tanda }]),"),
    ('era menghitung pembuka yang belum selesai', 'baru/js/layar/tutup-buku-logika.js', "if (bkTutupBuku(x) && pembukaBerlaku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }\nexport function aturBuku",
     "if (bkTutupBuku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }\nexport function aturBuku"),
    ('rencana tidak disimpan di server (berita acara berjalan tidak ikut kiriman 1)', 'baru/js/layar/tutup-buku-logika.js', "if (i === 0 && n > 1) dokumen.unshift(", "if (false) dokumen.unshift("),
    ('lanjut mengirim ulang kiriman yang sudah masuk', 'baru/js/layar/tutup-buku-logika.js', "const belumAda = a.pembuka.filter((x) => tanda.indexOf(x) < 0 && !dokDiCache(x.koleksi, x.data.id));", "const belumAda = a.pembuka.filter((x) => tanda.indexOf(x) < 0);"),
    ('lanjut tanpa memeriksa perubahan tahun lama', 'baru/js/layar/tutup-buku-logika.js', "const ub = bkBerubah(a); if (ub) return { tolak: ub };", "const ub = '';"),
    ('mulai baru saat pembatalan belum tuntas', 'baru/js/layar/tutup-buku-logika.js', "const tg = bkTertunda(tahun); if (tg) return { tolak: tg };", "const tg = '';"),
    ('§8 no. 2 · Lanjutkan menulis titik 31 Des walau titik kas sudah di Januari', 'baru/js/layar/tutup-buku-logika.js', "const akhir = bkTitikKini({ dokumen: tanda.concat(a.penanda || [], [{ koleksi: 'tutupBukuAcara', data: kunci }]) }, tahun);",
     "const akhir = { dokumen: tanda.concat(a.penanda || [], [{ koleksi: 'tutupBukuAcara', data: kunci }]) };"),
    ('§8 no. 3 · Lanjutkan memecah sisa dengan jam MULAI (bukan jam sekarang)', 'baru/js/layar/tutup-buku-logika.js', "const Pt = kpPotong(belumAda.map((x) => ({ dokumen: [x] })).concat([akhir]), dokDiCache, new Date(Date.now()));",
     "const Pt = kpPotong(belumAda.map((x) => ({ dokumen: [x] })).concat([akhir]), dokDiCache, new Date(a.rencana.dibuat));"),
    ('batal tidak dipecah', 'baru/js/layar/tutup-buku-logika.js', "const P = kpPotong([{ dokumen: awal, hapus: tanda }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] }))), dokDiCache, ugKiniDari(w));",
     "const P = { potongan: [{ dokumen: awal, hapus, get: 0 }] };"),
    ('titik kas tahun hanya dari titik kas sekarang', 'baru/js/layar/tutup-buku-logika.js', "const th = ambilTutupHari().filter((d) => d && d.tanggal && d.tanggal <= c && d.titik)", "const th = ambilTutupHari().filter((d) => false)"),
    ('titik 2 Jan ditimpa titik 31 Des', 'baru/js/layar/tutup-buku-logika.js', "const titik = K.ada && T0 && T0.dari === 'titikKas' ? {", "const titik = K.ada && T0 ? {"),
    ('tutup hari tidak menyimpan titik di dokumennya', 'baru/js/layar/tutup-hari-logika.js', "dokTutup.titik = { laci: titik.laci,", "dokTutup.titikLain = { laci: titik.laci,"),
    ('kemajuan menyebut tahun berjalan, bukan tahun yang terkunci', 'baru/js/layar/tutup-buku-logika.js', "  if (!a) return null; const tahun = Number(a.tahun);", "  if (!a) return null; const tahun = Number(a.tahun) + (a.status === 'terkunci' ? 1 : 0);"),
    ('pemeriksaan ulang kembali ke 1 Jan vs 31 Des', 'baru/js/layar/tutup-buku-logika.js', "return bandingBuku({ harta: H.baris, utang: [] }, o);",
     "const B1 = barisBuku((tahun + 1) + '-01-01', (tahun + 1) + '-01-01'); const o1 = {}; B1.harta.concat(B1.utang).forEach((b) => { o1[b.id] = b.n; }); return bandingBuku({ harta: a.sebelum, utang: [] }, o1);"),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        u0 = open(os.path.join(bundel_baru.AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
        for nama, wajib in STATIS:   # statis: jangkar pertama dibuang dari uang.js → pemeriksa statis wajib melihatnya
            if not all(x in u0 for x in wajib): print('KONTROL BASI  statis uang.js · ' + nama); kode = 3; continue
            u1 = u0.replace(wajib[0], ''); kurang = [x for x in wajib if x not in u1]
            print(('BERBUNYI ' if kurang else 'DIAM!!   ') + 'statis uang.js · ' + nama + ' dibuang → tidak ada: ' + ' | '.join(kurang)[:100])
            if not kurang: kode = 3
        for nama, berkas, lama, baru in RUSAK:
            asli = open(os.path.join(bundel_baru.AKAR, berkas), encoding='utf-8').read()
            if asli.count(lama) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            js = uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(
                (asli.replace(lama, baru) if m == berkas else open(os.path.join(bundel_baru.AKAR, m), encoding='utf-8').read())) for m in MODUL]))
            l, g = utama(js)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    js = bundelan(); l, g = utama(js)
    u = open(os.path.join(bundel_baru.AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
    for nama, wajib in STATIS:
        kurang = [x for x in wajib if x not in u]
        if kurang: g.append('statis uang.js · ' + nama + ' → tidak ada: ' + ' | '.join(kurang))
        else: l += 1
    for x in g: print('   ✗ ' + x[:400])
    print('TUTUP BUKU BERTAHAP (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    cad = sorted(glob.glob(os.path.join(bundel_baru.AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and not g:
        a, e = jalan(JAM + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if a is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s) pada 5 Jan 2027: %s' % (os.path.basename(cad[-1]), json.dumps(a, ensure_ascii=False)))
        if a['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
