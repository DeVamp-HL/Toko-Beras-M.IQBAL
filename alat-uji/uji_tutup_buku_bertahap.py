#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tutup_buku_bertahap.py — rancangan TUTUP BUKU BERTAHAP (Okt 2026; owner 1 Okt: batas 18 pemeriksaan kunci per kiriman tetap) di jsc.
KOTAK PASIR (ANGKA & NAMA CONTOH, bukan angka toko). Tanpa peramban.

Yang dijaga:
  T0  saldo pembuka ≤ 18 pemeriksaan = SATU kiriman seperti dulu (tanpa berita acara 'berjalan')
  T1  40 nama berutang (+ 1 bon pemasok + titik kas 31 Des) → 3 kiriman, tiap kiriman ≤ 18 pemeriksaan (penjaga pusat meloloskan), berita acara
      'berjalan' di kiriman PERTAMA, penanda (titik kas · pengaturan/tutupBuku · berita acara 'terkunci') di kiriman TERAKHIR, tanpa id ganda
  T2  sesudah kiriman 1 saja: tahun 2026 masih utuh — era tidak pindah, Agustus tidak FINAL, 12 baris 31 Des sama (piutang tidak dobel), kemajuan = saldo pembuka kiriman 1
  T3  putus di kiriman 2 → lanjutkan: hanya kiriman 2 & 3 (id & isi sama; lanjutan 1 & 2), lalu hanya 3; sesudahnya terkunci, era 2026, pembuka tidak dobel
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
  N4  kiriman yang belum diakui server (masih di antrean perangkat) bukan "masuk": pita fase tunggu, Lanjutkan & Batalkan menolak sampai antrean kosong
  N5  penjualan di antara kiriman 1 dan Lanjutkan (hari yang sama) → periksa ulang tidak berbunyi palsu (patokan diambil tepat sebelum kiriman pertama sesi itu)
  N6  "selesaikan" ditolak selama arsip belum habis; periksa ulang beda = ditolak menyebut barisnya, baru diterima pada ketukan kedua (dicatat di berita acara)
  N7  kalimat berhenti: kiriman 1 tutup buku → "Kunci tahun" lagi; kiriman 1 pembatalan → "Batalkan" lagi (Lanjutkan = meneruskan tutup buku); sesudahnya "Lanjutkan"
  N8  dibatalkan, dikunci lagi, dibatalkan lagi → berita acara mencatat tanggal pembatalan KEDUA
  N9  tutup buku setengah jalan → daftar periksa Kunci bulan punya butir ⛔ (kunci bulan ditolak); sesudah selesai butirnya beres
  Putaran 3 (tinjauan + sanggah sesudah §8):
  P3-AAL1  HP A sedang lanjut arsip, HP B membatalkan sampai tuntas → arsip HP A berhenti di antara potongan (catatan 2026 tidak tersapu sesudah "dibatalkan");
           tombol pita yang mati sungguh mati (CSS + penjaga sibuk)
  P3-AAL1b potongan arsip yang mendarat SESUDAH pembatalan tuntas dikembalikan perangkat yang mengarsip (hanya bila dibatalkan, bukan selesai)
  P3-UTBU1 hasil periksa ulang dibekukan saat arsip habis (berita acara periksaArsip); nota Januari sesudahnya tidak membuat "selesai" berbunyi / tercatat TIDAK SAMA
  P3-UTBU2 baris yang tidak bisa dihitung mesin (titik kas sudah maju) = "belum bisa dihitung" di pita, "selesai", kabar & berita acara — bukan "TIDAK SAMA"
  P3-AAL2  arsip tahun berikutnya putus lalu dilanjutkan: batch penanda tahun lalu diarsipkan paling akhir → tidak ada pembuka tahun lalu tertinggal di koleksi hidup
  P3-AAL3  penanda yang tertahan di HP lain mendarat sesudah pembatalan tuntas → fase RUSAK (batalkan), bukan "lanjutkan arsip"; pembatalan membereskannya
  P3-AAL4  Lanjutkan & Batalkan ditolak tanpa internet atau selama berita acara / pengaturan masih salinan perangkat (Firestore fromCache)
  P3-AAL5  hapus pembatalan yang menunggu server = fase tunggu (Lanjutkan pembatalan ditolak), bukan "sudah ditarik"
  P3-AAL6  tutup buku satu kiriman yang antre: kalimat menyebut pita "Tahun … terkunci" → "Lanjutkan" (arsip), bukan "… sudah masuk"
  P3-AAL7  satu satuan sesudah pecah ulang: pita = saldo pembuka yang sudah masuk; kalimat & progres Lanjutkan = "kiriman lanjutan i dari n" + jumlah itu
  Putaran 4 (owner 1 Okt: SATU PERANGKAT SAJA):
  P4-1  berita acara mencatat PEMEGANG (perangkat yang memulai); selama berjalan / terkunci / membatalkan, Lanjutkan, Batalkan, lanjut arsip, periksa ulang
        & selesai dari perangkat lain DITOLAK dengan kalimat yang menyebut nama pemegang; mulai lagi sesudah dibatalkan = pemegang baru; tanpa pemegang = bebas
  P4-2  AMBIL ALIH dari pemegang yang rusak / hilang: hanya bila tersambung & data dari server, antrean kosong, berita acara diam ≥ 60 menit, pemegang tidak
        berdenyut 15 menit; dua ketukan dengan kalimat peringatan; sesudahnya pemegang lama ditolak; percobaan berikut tidak membawa jejak ambil alih lama
  P4-3  arsip: status dibaca ulang sesudah SETIAP potongan, termasuk yang TERAKHIR — potongan terakhir yang mendarat sesudah pembatalan tuntas dikembalikan
        (simulasi memakai bentuk uang.js yang sebenarnya: UANG_CEK_TIAP_POTONGAN dibaca dari berkasnya)
  P4-4  hasil beku periksa ulang = dokumen TERSENDIRI tanpa kolom status (pengaturan/periksaArsip<tahun>) bertanda percobaan: yang mendarat telat sesudah
        dibatalkan / selesai tidak mengubah status berita acara; hasil beku percobaan lama tidak dipakai percobaan berikut

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
  var KM = kemajuanBuku(); ok('T2 kemajuan: saldo pembuka kiriman 1 dari semua (satuan saldo pembuka, putaran 3 AAL7), kalimat menyebut tahun masih terbuka', KM && KM.fase === 'pembuka' && KM.sudah === R.kiriman[0].pembuka.length && KM.total === R.acara.nPembuka && /MASIH TERBUKA/.test(KM.teks), J(KM));
  ok('T2 mulai baru ditolak selama berjalan', /sedang berjalan/.test(susunKunci(2026, D, W).tolak || ''), susunKunci(2026, D, W).tolak); });

// ---- T3 · putus di kiriman 2 → lanjut
coba('T3', function () { L = lanjutBuku(2026);
  ok('T3 lanjut sesudah putus di kiriman 2: tinggal kiriman 2 & 3 (lanjutan 1 & 2), isi & id SAMA dengan rencana', !L.tolak && L.sudah === R.kiriman[0].pembuka.length && L.kiriman.length === 2 && L.kiriman[0].ke === 1 && L.kiriman[0].lanjutan && idKiriman(L.kiriman[0]) === idKiriman(R.kiriman[1]) && idKiriman(L.kiriman[1]) === idKiriman(R.kiriman[2]), J(L.tolak || [L.sudah, L.kiriman.map(function (k) { return k.ke; })]));
  ok('T3 kiriman 2 masuk', kirim(L.kiriman[0]), tolakPenjaga.slice(-1)[0]);
  L = lanjutBuku(2026); ok('T3 lanjut lagi: hanya kiriman 3 = lanjutan 1 dari 1 (kiriman 2 tidak dikirim ulang)', !L.tolak && L.kiriman.length === 1 && L.kiriman[0].ke === 1 && L.kiriman[0].total === 1 && idKiriman(L.kiriman[0]) === idKiriman(R.kiriman[2]), J(L.tolak || L.kiriman.map(function (k) { return k.ke; })));
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
  ok('N3 lanjut 5 Jan: sisa dipecah ulang — tiap kiriman ≤ 18 & lolos penjaga pusat, nomor kiriman lanjutan mulai 1 (putaran 3 AAL7), penanda hanya di kiriman terakhir; sesudahnya terkunci, tiap pembuka tepat sekali',
    !L.tolak && L.kiriman.length >= 2 && g.every(function (x) { return x <= 18; }) && masuk.every(Boolean) && L.kiriman[0].ke === 1 && L.kiriman[0].lanjutan && L.kiriman.every(function (k, i) { return k.penanda === (i === L.kiriman.length - 1); })
    && acara(2026).status === 'terkunci' && nPembukaMentah(2026) === R.acara.nPembuka && !lanjutBuku(2026).kiriman, J([rencana, g, L.tolak, masuk, tolakPenjaga.slice(-1)])); });

// ---- §8 no. 4 · kiriman yang BELUM diakui server (opsi tunggu 30 detik habis): Firestore sudah menaruhnya di cache (hasPendingWrites) — bukan "masuk"
function tundakan(k) { var per = {}; k.dokumen.forEach(function (x) { (per[x.koleksi] = per[x.koleksi] || []).push(String(x.data.id)); }); if (typeof setelTertunda === 'function') Object.keys(per).forEach(function (c) { setelTertunda(c, per[c]); }); }
function lepasTunda() { if (typeof setelTertunda === 'function') KOLEKSI.forEach(function (k) { setelTertunda(k.nama, []); }); }
coba('N4', function () { kotak(40); W = jam('2027-01-05T08:00:00+07:00'); R = susunKunci(2026, D, W);
  terapkanKeCache(R.kiriman[0].dokumen); tundakan(R.kiriman[0]);
  var KM = kemajuanBuku(); L = lanjutBuku(2026); var Bt = susunBatal(2026, [], W);
  ok('N4 kiriman 1 masih antre di perangkat: pita TIDAK menghitungnya masuk (fase tunggu); Lanjutkan & Batalkan menolak dengan kalimat menunggu server',
    !!KM && KM.fase === 'tunggu' && !KM.sudah && /menunggu server/.test(KM.teks) && !!L.tolak && /menunggu server/.test(L.tolak) && !!Bt.tolak && /menunggu server/.test(Bt.tolak), J([KM, L.tolak || L.kiriman.length, Bt.tolak || Bt.kiriman.length]));
  lepasTunda(); L = lanjutBuku(2026); ok('N4 server mengaku kiriman 1 → Lanjutkan mengirim sisanya (2 kiriman lanjutan)', !L.tolak && L.kiriman.length === 2 && L.kiriman[0].ke === 1 && L.kiriman[0].lanjutan, J(L.tolak || L.kiriman.length));
  kirim(L.kiriman[0]); terapkanKeCache(L.kiriman[1].dokumen); tundakan(L.kiriman[1]); KM = kemajuanBuku();
  ok('N4 kiriman PENANDA masih antre: pita fase tunggu (bukan "terkunci" / arsip), Lanjutkan menolak', !!KM && KM.fase === 'tunggu' && !!lanjutBuku(2026).tolak, J(KM));
  lepasTunda(); KM = kemajuanBuku(); ok('N4 penanda diakui server → fase arsip', !!KM && KM.fase === 'arsip', J(KM)); });
lepasTunda();

// ---- §8 no. 5 · mulai 2 Jan 07.00, putus sesudah kiriman 1, toko berjualan 09.00, Lanjutkan 21.00 hari yang sama → periksa ulang TIDAK berbunyi palsu
coba('N5', function () { kotak(40); W = jam('2027-01-02T07:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]);
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'jan2', tanggal: '2027-01-02', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]);
  jam('2027-01-02T21:00:00+07:00'); L = lanjutBuku(2026); (L.kiriman || []).forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var PU = periksaUlangBuku(2026);
  ok('N5 ada penjualan di antara kiriman 1 dan Lanjutkan (hari yang sama): periksa ulang sesudah kunci & arsip SAMA (patokan diambil tepat sebelum kiriman pertama sesi itu)',
    !L.tolak && acara(2026).status === 'terkunci' && !!PU && PU.semuaSama, J([L.tolak, PU && PU.beda.map(function (b) { return b.nama.split(' · ')[0] + ' ' + b.a + ' vs ' + b.b; })])); });

// ---- §8 no. 6 · "Selesaikan" (tidak bisa dibatalkan lagi) hanya sesudah arsip habis DAN periksa ulang sama; beda = ketukan kedua yang menyebut barisnya
coba('N6', function () { kotak(5); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim);
  var S0 = susunSelesai(2026, 'cadangan-sesudah.json', W);
  ok('N6 arsip belum habis → selesai DITOLAK (lanjutkan arsip dulu)', !!S0.tolak && /arsip/.test(S0.tolak), J(S0.tolak || 'diterima'));
  arsipkanDokumen(2026, arsipBuku(2026).daftar);
  // nominal satu pembuka piutang berubah (putaran 3 AAL3: pembuka yang HILANG selagi terkunci = fase rusak, bukan selesaikan)
  var pi = cacheMentah('piutang').filter(function (x) { return x.tutupBuku; })[0]; terapkanKeCache([{ koleksi: 'piutangMutasi', data: Object.assign({}, pi, { nominal: pi.nominal + 50000 }) }]);
  var KM = kemajuanBuku(); var S1 = susunSelesai(2026, 'cadangan-sesudah.json', W);
  ok('N6 periksa ulang BEDA (nominal satu pembuka piutang berubah): pita selesaikan menyebut barisnya; selesai DITOLAK dan minta ketukan kedua yang menyebut barisnya',
    !!KM && KM.fase === 'selesaikan' && /Piutang/.test(KM.teks) && !!S1.tolak && !!S1.perluYakin && /Piutang/.test(S1.tolak), J([KM, S1.tolak || 'diterima']));
  var S2 = susunSelesai(2026, 'cadangan-sesudah.json', W, true); if (!S2.tolak) kirim(S2);
  ok('N6 ketukan kedua: selesai; berita acara mencatat periksa ulang yang beda', !S2.tolak && acara(2026).status === 'selesai' && !!acara(2026).periksaUlang && acara(2026).periksaUlang.sama === false && /Piutang/.test(acara(2026).periksaUlang.beda.join()), J(S2.tolak || acara(2026).periksaUlang)); });

// ---- §8 no. 7 · kalimat bila berhenti menyebut tombol yang BENAR-BENAR meneruskan hal itu
function kabarBerhenti() { return typeof kabarBerhentiBuku === 'function' ? kabarBerhentiBuku.apply(null, arguments) : '(kalimat ada di uang.js, tidak bisa diuji)'; }
coba('N7', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W);
  var ka = kabarBerhenti('kunci', 2026, 1, R.kiriman.length, { gagal: true, pesan: 'ditolak server' });
  ok('N7 tutup buku berhenti di kiriman 1 (tidak ada yang masuk, pita lanjut tidak ada): kalimat menyuruh "Kunci tahun" lagi, bukan "Lanjutkan"', kemajuanBuku() === null && /"Kunci tahun/.test(ka) && !/Lanjutkan/.test(ka), ka);
  kirim(R.kiriman[0]); kirim(R.kiriman[1]); B = susunBatal(2026, [], W); var KM = kemajuanBuku(); var kb = kabarBerhenti('batal', 2026, 1, B.kiriman.length, { gagal: true, pesan: 'ditolak server' });
  ok('N7 pembatalan berhenti di kiriman 1 (pita masih fase pembuka — "Lanjutkan" = meneruskan TUTUP BUKU): kalimat menyuruh "Batalkan" lagi', !!KM && KM.fase === 'pembuka' && /"Batalkan" lagi/.test(kb) && !/ketuk "Lanjutkan"/.test(kb), J([KM && KM.fase, kb]));
  var kd = kabarBerhenti('batal', 2026, 1, B.kiriman.length, { antre: true });
  ok('N7 kiriman 1 pembatalan belum diakui server: tunggu antrean dulu, lalu "Lanjutkan" HANYA bila pita menyebut pembatalan, selain itu "Batalkan" lagi', /menunggu server/.test(kd) && /"Batalkan" lagi/.test(kd), kd);
  kirim(B.kiriman[0]); var kc = kabarBerhenti('batal', 2026, 2, B.kiriman.length, { gagal: true, pesan: 'ditolak server' });
  ok('N7 pembatalan berhenti sesudah kiriman 1 masuk (pita fase batal): kalimat menyuruh "Lanjutkan" untuk meneruskan pembatalan', B.kiriman.length >= 2 && (kemajuanBuku() || {}).fase === 'batal' && /ketuk "Lanjutkan" untuk meneruskan pembatalan/i.test(kc), J([B.kiriman.length, kc])); });

// ---- §8 no. 8 · tutup buku dibatalkan 5 Jan, dikunci lagi 8 Jan, dibatalkan lagi 9 Jan → berita acara mencatat tanggal pembatalan KEDUA
coba('N8', function () { kotak(5); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  B = susunBatal(2026, arsipSimulasi(), W); B.kiriman.forEach(kirim); pulihkanArsip(2026, B.pulih); kirim({ dokumen: [B.akhir] }); var t1 = acara(2026).dibatalkanTanggal;
  W = jam('2027-01-08T10:00:00+07:00'); R = susunKunci(2026, D, W); var bersih = !R.tolak && R.acara.dibatalkanTanggal === undefined && R.acara.dibatalkanPada === undefined;
  R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  W = jam('2027-01-09T10:00:00+07:00'); B = susunBatal(2026, arsipSimulasi(), W); B.kiriman.forEach(kirim); pulihkanArsip(2026, B.pulih); kirim({ dokumen: [B.akhir] });
  ok('N8 kunci kedua tidak membawa tanggal pembatalan pertama; pembatalan kedua tercatat 9 Jan (bukan 5 Jan)', t1 === '2027-01-05' && bersih && acara(2026).status === 'dibatalkan' && acara(2026).dibatalkanTanggal === '2027-01-09' && /^2027-01-09/.test(new Date(new Date(acara(2026).dibatalkanPada).getTime() + 7 * 3600000).toISOString()),
    J([t1, R.acara && R.acara.dibatalkanTanggal, acara(2026).dibatalkanTanggal, acara(2026).dibatalkanPada])); });

// ---- §8 no. 9 · tutup buku setengah jalan → daftar periksa Kunci bulan punya butir ⛔ (mengunci Januari 2027 di tengahnya = pembuka, arsip & batal ditolak server)
coba('N9', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]);
  var KK = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} };
  var butirTB = function (DP) { return DP.butir.filter(function (b) { return b.id !== 'tundaTutupBuku' && /tutup buku/i.test(b.teks + ' ' + b.ket); }); };
  jam('2027-02-05T10:00:00+07:00'); var DP = kpDaftarPeriksa('2027-01', new Date(__KINI), KK); var tb = butirTB(DP);
  ok('N9 tutup buku 2026 setengah jalan: daftar periksa Kunci bulan Januari 2027 punya butir ⛔ yang belum beres → kunci bulan ditolak', tb.length === 1 && tb[0].blokir && !tb[0].ok && !DP.boleh, J(tb));
  jam('2027-01-05T10:00:00+07:00'); L = lanjutBuku(2026); (L.kiriman || []).forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar); var SL = susunSelesai(2026, 'cadangan-sesudah.json', W); if (!SL.tolak) kirim(SL);
  jam('2027-02-05T10:00:00+07:00'); DP = kpDaftarPeriksa('2027-01', new Date(__KINI), KK); tb = butirTB(DP);
  ok('N9 sesudah tutup buku selesai: butir itu beres', kemajuanBuku() === null && tb.length === 1 && tb[0].ok, J([SL.tolak, tb])); });

// ---- putaran 3 AAL1 · HP A sedang "lanjutkan arsip" (daftar dihitung SEKALI, dikirim per 18); sesudah potongan 1 HP B membatalkan sampai tuntas → arsip HP A
//      BERHENTI sebelum potongan berikutnya (status berita acara di cache dibaca ulang), sisa catatan 2026 tidak tersapu ke arsip sesudah "dibatalkan"
var penjagaArsip = function (tahun) { return typeof arsipBerhentiBuku === 'function' ? arsipBerhentiBuku(tahun) : ''; };
// = firebase.js arsipkanBerkas (potongan 18, progres sesudah tiap potongan) + panggilan progres jalankanBuku di uang.js (berhenti bila penjaga berbunyi)
function arsipLayar(tahun, daftar, sela) {
  var h = penjagaArsip(tahun); if (h) return h;
  for (var i = 0; i < daftar.length; i += 18) { arsipkanDokumen(tahun, daftar.slice(i, i + 18)); var sudah = Math.min(i + 18, daftar.length); if (sela) sela(sudah);
    h = (UANG_CEK_TIAP_POTONGAN || sudah < daftar.length) ? penjagaArsip(tahun) : ''; if (h) return h; }
  return '';
}
coba('P3-AAL1', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var nJual = ambilPenjualanSemua().length; R.kiriman.forEach(kirim);
  var daftarA = arsipBuku(2026).daftar; var awal = typeof arsipBerhentiBuku === 'function' ? arsipBerhentiBuku(2026) : '(penjaga arsip tidak ada)';
  var henti = arsipLayar(2026, daftarA, function (sudah) { if (sudah !== 18) return;
    var B2 = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }), W); B2.kiriman.forEach(kirim); pulihkanArsip(2026, B2.pulih); kirim({ dokumen: [B2.akhir] }); });
  var diArsip = arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).length;
  ok('P3-AAL1 arsip HP A (' + daftarA.length + ' catatan, per 18) berhenti sesudah HP B membatalkan tuntas: kalimat menyebut dibatalkan; penjualan 2026 utuh, arsip 2026 kosong, tidak ada yang setengah',
    awal === '' && /dibatalkan/.test(henti) && acara(2026).status === 'dibatalkan' && ambilPenjualanSemua().length === nJual && diArsip === 0 && kemajuanBuku() === null,
    J([awal, henti, acara(2026).status, ambilPenjualanSemua().length + '/' + nJual, diArsip, kemajuanBuku()])); });
// susulan: potongan 2 HP A sudah TERKIRIM (diperiksa sesudah potongan 1: masih terkunci) dan baru mendarat SESUDAH pembatalan HP B tuntas → HP A, begitu melihat
// pembatalan, mengembalikan potongan yang baru saja ia pindah (dulu: 18 catatan 2026 tertinggal di arsip tanpa pita)
coba('P3-AAL1b', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var nJual = ambilPenjualanSemua().length; R.kiriman.forEach(kirim);
  var daftarA = arsipBuku(2026).daftar; arsipkanDokumen(2026, daftarA.slice(0, 18)); var h1 = penjagaArsip(2026);
  var B2 = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }), W); B2.kiriman.forEach(kirim); pulihkanArsip(2026, B2.pulih); kirim({ dokumen: [B2.akhir] });
  var potong2 = daftarA.slice(18, 36); arsipkanDokumen(2026, potong2); var h2 = penjagaArsip(2026);
  var balik = typeof arsipBalikBuku === 'function' ? arsipBalikBuku(2026, potong2) : []; if (balik.length) pulihkanArsip(2026, balik);
  var diArsip = arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).length;
  ok('P3-AAL1b potongan yang mendarat sesudah pembatalan tuntas dikembalikan HP A sendiri: penjualan 2026 utuh, arsip 2026 kosong',
    h1 === '' && /dibatalkan/.test(h2) && balik.length === 18 && ambilPenjualanSemua().length === nJual && diArsip === 0 && kemajuanBuku() === null,
    J([h1, h2, balik.length, ambilPenjualanSemua().length + '/' + nJual, diArsip]));
  ok('P3-AAL1b yang SELESAI ditutup perangkat lain tidak pernah dikembalikan (hanya pembatalan)', typeof arsipBalikBuku === 'function' && (function () {
    terapkanKeCache([{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara(2026), { status: 'selesai' }) }]); var x = arsipBalikBuku(2026, potong2).length;
    terapkanKeCache([{ koleksi: 'tutupBukuAcara', data: Object.assign({}, acara(2026), { status: 'dibatalkan' }) }]); return x === 0; })()); });

// ---- putaran 3 UTBU-1 · tutup buku tuntas 2 Jan 07.00 (periksa ulang sama), nota tunai Januari 10.00, "selesai" 12.00 → hasil periksa ulang yang DIBEKUKAN
//      saat arsip habis dipakai (dulu dihitung ulang terhadap patokan pagi: stok & laci "TIDAK SAMA", tercatat permanen di berita acara)
coba('P3-UTBU1', function () { kotak(40); W = jam('2027-01-02T07:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  // = jalankanBuku (uang.js) sesudah arsip habis
  var PA = typeof susunPeriksaArsip === 'function' ? susunPeriksaArsip(2026, W) : null; if (PA && PA.dokumen) kirim({ dokumen: PA.dokumen });
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'jan2', tanggal: '2027-01-02', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]);
  var W2 = jam('2027-01-02T12:00:00+07:00'); var hidup = periksaUlangBuku(2026); var KM = kemajuanBuku(); var S1 = susunSelesai(2026, 'cadangan-sesudah.json', W2); if (!S1.tolak) kirim(S1);
  ok('P3-UTBU1 nota Januari sesudah arsip habis (hitung ulang sekarang berbeda): pita tanpa AWAS, "selesai" diterima pada ketukan PERTAMA, berita acara mencatat periksa ulang SAMA (hasil saat arsip habis)',
    !!PA && !!PA.PU && PA.PU.semuaSama && !!hidup && !hidup.semuaSama && !!KM && KM.fase === 'selesaikan' && !/AWAS/.test(KM.teks) && !S1.tolak && acara(2026).status === 'selesai' && !!acara(2026).periksaUlang && acara(2026).periksaUlang.sama === true,
    J([PA && PA.PU && PA.PU.ringkas, hidup && hidup.ringkas, KM && KM.teks, S1.tolak || 'diterima', acara(2026).periksaUlang])); });

// ---- putaran 3 UTBU-2 · tutup buku tuntas 2 Jan 07.00 TANPA hasil yang dibekukan (dihitung ulang), tanpa satu transaksi Januari pun; tutup hari 2 & 3 Jan
//      memajukan titik kas → 4 baris uang pada 2 Jan tidak bisa dihitung mesin. Kalimat & catatan berita acara: "belum bisa dihitung", BUKAN "TIDAK SAMA"
coba('P3-UTBU2', function () { kotak(40); W = jam('2027-01-02T07:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  ['2027-01-02', '2027-01-03'].forEach(function (t) { var tk = { id: 'titikKas', tanggal: t, laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000, diubahPada: t + 'T14:00:00.000Z' };
    terapkanKeCache([{ koleksi: 'pengaturan', data: tk }]); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(tk)); });
  var W4 = jam('2027-01-04T08:00:00+07:00'); var KM = kemajuanBuku(); var S1 = susunSelesai(2026, 'cadangan-sesudah.json', W4); var S2 = susunSelesai(2026, 'cadangan-sesudah.json', W4, true); if (!S2.tolak) kirim(S2);
  var kal = typeof bkKalimatPeriksa === 'function' ? bkKalimatPeriksa(periksaUlangBuku(2026)) : '(kalimat tidak bisa diuji)'; var pu = acara(2026).periksaUlang || {};
  ok('P3-UTBU2 4 baris uang tidak bisa dihitung (titik kas sudah maju): pita, "selesai" & kalimat layar menyebut "belum bisa dihitung" (Uang di laci …), tidak ada "TIDAK SAMA"; berita acara: beda kosong, belum bisa dihitung 4',
    !!KM && KM.fase === 'selesaikan' && /4 baris belum bisa dihitung \(Uang di laci/.test(KM.teks) && !/TIDAK SAMA/.test(KM.teks) && !!S1.tolak && /belum bisa dihitung/.test(S1.tolak) && !/TIDAK SAMA/.test(S1.tolak)
    && /4 baris belum bisa dihitung/.test(kal) && !/TIDAK SAMA/.test(kal) && !S2.tolak && pu.sama === false && Array.isArray(pu.beda) && !pu.beda.length && Array.isArray(pu.belumBisa) && pu.belumBisa.length === 4,
    J([KM && KM.teks, S1.tolak, kal, pu])); });

// ---- putaran 3 AAL2 · tutup buku 2026 tuntas; setahun kemudian tutup buku 2027: ARSIP 2027 putus sesudah potongan pertama, lalu "Lanjutkan" (daftar dihitung
//      ulang dari catatan yang masih ada). Batch PENANDA 2026 diarsipkan paling akhir → sisa pembuka 2026 tetap terlihat & ikut diarsipkan, tidak tertinggal
coba('P3-AAL2', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var SL = susunSelesai(2026, 'cadangan-sesudah.json', W); if (!SL.tolak) kirim(SL);
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'j2027', tanggal: '2027-06-01', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]);
  var W2 = jam('2028-01-05T10:00:00+07:00'); var R2 = susunKunci(2027, D, W2); (R2.kiriman || []).forEach(kirim);
  var A0 = arsipBuku(2027).daftar; var n2026 = A0.filter(function (x) { return x.data.tutupBuku && Number(x.data.tahunDari) === 2026; }).length;
  arsipkanDokumen(2027, A0.slice(0, 18)); var KM = kemajuanBuku(); var A1 = arsipBuku(2027).daftar;
  arsipkanDokumen(2027, A1); var tinggal = nPembukaMentah(2026);
  ok('P3-AAL2 arsip 2027 putus sesudah 18 dari ' + A0.length + ' (' + n2026 + ' pembuka 2026): pita masih arsip (sisa ' + (A0.length - 18) + '), Lanjutkan memindah sisanya; tidak ada pembuka 2026 tertinggal di koleksi hidup',
    !R2.tolak && A0.length > 18 && !!KM && KM.fase === 'arsip' && KM.sisa === A0.length - 18 && A1.length === A0.length - 18 && tinggal === 0 && arsipBuku(2027).n === 0,
    J([R2.tolak, A0.length, KM && (KM.fase + ' · sisa ' + KM.sisa), A1.length, tinggal])); });

// ---- putaran 3 AAL3 · kiriman TERAKHIR (penanda) tertahan di antrean HP A; HP B membatalkan sampai tuntas; antrean HP A lalu masuk server → berita acara
//      'terkunci' lagi dengan saldo pembuka tidak lengkap. Pita: fase RUSAK (batalkan), BUKAN "lanjutkan arsip"; pembatalan membereskannya
coba('P3-AAL3', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); var s0 = baris(barisTahun(2026)); var piutang0 = hitungPiutang('2027-01-05').reduce(function (a, x) { return a + x.sisa; }, 0);
  kirim(R.kiriman[0]); kirim(R.kiriman[1]); var tertahan = R.kiriman[2];
  B = susunBatal(2026, [], W); B.kiriman.forEach(kirim); kirim({ dokumen: [B.akhir] }); kirim(tertahan);
  var KM = kemajuanBuku(); var ada = nPembukaMentah(2026);
  ok('P3-AAL3 penanda mendarat sesudah pembatalan tuntas (' + ada + ' dari ' + R.acara.nPembuka + ' saldo pembuka): pita fase rusak menyuruh "batalkan", bukan arsip',
    acara(2026).status === 'terkunci' && ada < R.acara.nPembuka && !!KM && KM.fase === 'rusak' && /batalkan/.test(KM.teks) && !/lanjutkan arsip/.test(KM.teks), J([acara(2026).status, ada, KM]));
  B = susunBatal(2026, arsipSimulasi(), W); if (!B.tolak) { B.kiriman.forEach(kirim); pulihkanArsip(2026, B.pulih); kirim({ dokumen: [B.akhir] }); }
  ok('P3-AAL3 "batalkan" membereskannya: pembuka 0, berita acara dibatalkan, era null, piutang & 12 baris 31 Des seperti sebelum, pita kosong',
    !B.tolak && nPembukaMentah(2026) === 0 && acara(2026).status === 'dibatalkan' && bkEra() === null && hitungPiutang('2027-01-05').reduce(function (a, x) { return a + x.sisa; }, 0) === piutang0 && samaBaris(s0, baris(barisTahun(2026))) && kemajuanBuku() === null,
    J([B.tolak, nPembukaMentah(2026), acara(2026).status, bkEra(), kemajuanBuku()])); });

// ---- putaran 3 AAL4 · Mac B terakhir tersambung sesudah kiriman 1 (cache: 'berjalan'); HP A menuntaskan semuanya. Mac B dibuka TANPA internet / data masih
//      salinan perangkat (Firestore fromCache) → Lanjutkan & Batalkan DITOLAK sampai data server tiba (dulu kirimannya mendarat belakangan: 'selesai' mundur
//      jadi 'terkunci', titik kas Januari ditimpa). firebase.js menyetor tanda fromCache per koleksi ke toko.js (setelDariCache)
var sambungan = function (L) { return typeof bkSambungan === 'function' ? bkSambungan(L) : ''; };
var dariCache = function (k, ya) { if (typeof setelDariCache === 'function') setelDariCache(k, ya); };
coba('P3-AAL4', function () { kotak(40); W = jam('2027-01-05T08:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]);
  var KM = kemajuanBuku(); var tanpaInternet = sambungan({ offline: true });
  dariCache('tutupBukuAcara', true); var basiAcara = sambungan({ offline: false }); dariCache('tutupBukuAcara', false);
  dariCache('pengaturan', true); var basiAtur = sambungan({ offline: false }); dariCache('pengaturan', false);
  var segar = typeof bkSambungan === 'function' ? bkSambungan({ offline: false }) : '(penjaga sambungan tidak ada)';
  ok('P3-AAL4 Lanjutkan / Batalkan (pita ' + (KM && KM.fase) + '): tanpa internet DITOLAK; berita acara atau pengaturan masih salinan perangkat DITOLAK; data server segar = boleh',
    !!KM && /internet/.test(tanpaInternet) && /data terbaru/.test(tanpaInternet) && /data terbaru/.test(basiAcara) && /data terbaru/.test(basiAtur) && segar === '', J([tanpaInternet, basiAcara, basiAtur, segar])); });

// ---- putaran 3 AAL5 · kiriman ke-2 pembatalan berisi HAPUS saja dan belum diakui server ({ antre }). Firestore sudah membuang dokumennya dari cache, jadi tanda
//      per dokumen (hasPendingWrites) tidak melihatnya — hapus yang menunggu server dicatat per kiriman (firebase.js tulisBerkas → toko.js setelHapusTertunda)
var hapusTunda = function (id, h) { if (typeof setelHapusTertunda === 'function') setelHapusTertunda(id, h); };
coba('P3-AAL5', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  B = susunBatal(2026, arsipSimulasi(), W); kirim(B.kiriman[0]); var K2 = B.kiriman[1];
  terapkanKeCache(K2.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); hapusTunda('k-uji-hapus', K2.hapus);
  var KM = kemajuanBuku(); var B2 = susunBatal(2026, arsipSimulasi(), W);
  ok('P3-AAL5 hapus kiriman ke-2 pembatalan (' + K2.hapus.length + ' saldo pembuka) masih menunggu server: pita fase tunggu, Lanjutkan pembatalan DITOLAK (bukan dianggap sudah ditarik)',
    K2.hapus.length > 0 && !(K2.dokumen || []).length && !!KM && KM.fase === 'tunggu' && /menunggu server/.test(KM.teks) && !!B2.tolak && /menunggu server/.test(B2.tolak), J([KM, B2.tolak || B2.kiriman.length]));
  hapusTunda('k-uji-hapus', null); KM = kemajuanBuku();
  ok('P3-AAL5 server mengaku hapus itu → pita kembali fase batal (lanjutkan pembatalan)', !!KM && KM.fase === 'batal', J(KM)); });
hapusTunda('k-uji-hapus', null);

// ---- putaran 3 AAL6 · tutup buku yang muat SATU kiriman, kiriman itu belum diakui server ({ antre }). Sesudah server mengaku, pita = "Tahun 2026 terkunci; …"
//      (bukan "… sudah masuk") dan tombol K6 sudah "KUNCI TAHUN 2027" → kalimat menyebut pita yang BENAR dan "Lanjutkan" (arsip)
coba('P3-AAL6', function () { kotak(5); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W);
  var kab = kabarBerhenti('kunci', 2026, 1, R.kiriman.length, { antre: true, pesan: 'server belum mengaku dalam 30 detik' });
  kirim(R.kiriman[0]); var KM = kemajuanBuku();
  ok('P3-AAL6 satu kiriman antre: kalimat menyebut pita "Tahun 2026 terkunci" → "Lanjutkan"; pita sesudah server mengaku memang berbunyi begitu',
    R.kiriman.length === 1 && /pita "Tahun 2026 terkunci/.test(kab) && /ketuk "Lanjutkan"/.test(kab) && !/sudah masuk" muncul/.test(kab) && !!KM && /^Tahun 2026 terkunci/.test(KM.teks) && tahunBuku(new Date(__KINI)).tahun === 2027, J([kab, KM && KM.teks])); });

// ---- putaran 3 AAL7 · mulai 2 Jan (masa tenggang), putus sesudah kiriman 1; Lanjutkan 5 Jan (sisa dipecah ulang); putus lagi sesudah kiriman lanjutan pertama.
//      Satu satuan: pita menghitung SALDO PEMBUKA yang sudah masuk; kalimat & progres Lanjutkan menyebut "kiriman lanjutan i dari n" + jumlah pembuka yang masuk
coba('P3-AAL7', function () { var tambah = []; for (var q = 0; q < 20; q++) tambah.push({ id: 'd' + q, tanggal: '2026-12-' + String(10 + (q % 15)).padStart(2, '0'), jam: '10:00', caraBayar: 'Kredit', jenis: 'karung', merkSumber: 'Angsa', totalKg: 10, beratKarungAcuan: 50, jumlahKarung: 0.2, hargaTotal: 200000, hppTotalSaatJual: 130000, namaPelanggan: 'Pengutang Desember ' + q });
  kotak(25, tambah); W = jam('2027-01-02T10:00:00+07:00'); R = susunKunci(2026, D, W); kirim(R.kiriman[0]); jam('2027-01-05T10:00:00+07:00');
  L = lanjutBuku(2026); var L1 = (L.kiriman || []).map(function (k) { return k.ke + '/' + k.total + (k.lanjutan ? ' lanjutan' : ''); }); kirim(L.kiriman[0]);
  var kab = kabarBerhenti(L.kiriman[1].lanjutan ? 'lanjut' : 'kunci', 2026, L.kiriman[1].ke, L.kiriman[1].total, { gagal: true, pesan: 'ditolak server' }, L.kiriman[1]);
  var KM = kemajuanBuku(); var ada = nPembukaMentah(2026); var L2 = lanjutBuku(2026); var k2 = (L2.kiriman || [])[0] || {};
  ok('P3-AAL7 sesudah pecah ulang: pita = ' + ada + ' dari ' + R.acara.nPembuka + ' saldo pembuka; kalimat "kiriman lanjutan 2 dari 2" + jumlah yang sama; Lanjutkan berikutnya = lanjutan 1 dari 1',
    L1.join() === '1/2 lanjutan,2/2 lanjutan' && !!KM && KM.fase === 'pembuka' && KM.sudah === ada && KM.total === R.acara.nPembuka && KM.teks.indexOf(ada + ' dari ' + R.acara.nPembuka + ' saldo pembuka sudah masuk') >= 0
    && /kiriman lanjutan 2 dari 2/.test(kab) && kab.indexOf(ada + ' dari ' + R.acara.nPembuka + ' saldo pembuka') >= 0 && /[Kk]etuk "Lanjutkan"/.test(kab) && k2.ke === 1 && k2.total === 1 && !!k2.lanjutan,
    J([L1, KM, kab, [k2.ke, k2.total, k2.lanjutan]])); });

// ---- putaran 4 P4-1 · PEMEGANG PERANGKAT (owner 1 Okt: SATU PERANGKAT SAJA). Tutup buku dimulai di HP A → berita acara mencatat pemegang = HP A. Selama
//      'berjalan' / 'terkunci' / 'membatalkan', semua langkah yang MENULIS tutup buku dari Mac B ditolak dengan kalimat yang menyebut HP A; dari HP A jalan.
//      (Dulu kiriman yang tertahan di HP A mendarat sesudah Mac B membatalkan / menyelesaikan / melanjutkan, dan menimpanya — tiga putaran tambal.)
var HPA = { idPerangkat: 'p-hpa', namaPerangkat: 'HP owner contoh', antre: [], menunggu: 0, offline: false };
var MACB = { idPerangkat: 'p-macb', namaPerangkat: 'Mac toko contoh', antre: [], menunggu: 0, offline: false };
var bukanPemegang = function (t, L) { return typeof bkBukanPemegang === 'function' ? bkBukanPemegang(t, L) : ''; };
var KAL_A = /Tutup buku 2026 sedang dikerjakan di HP owner contoh\. Lanjutkan atau batalkan dari perangkat itu\./;
coba('P4-1', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA);
  var bj = R.kiriman ? R.kiriman[0].dokumen[0].data : null; var tk = R.acara || {};
  ok('P4-1 mulai di HP A: berita acara berjalan & terkunci mencatat pemegang = { id, nama } HP A',
    !R.tolak && !!bj && bj.status === 'berjalan' && !!bj.pemegang && bj.pemegang.id === 'p-hpa' && bj.pemegang.nama === 'HP owner contoh' && !!tk.pemegang && tk.pemegang.id === 'p-hpa', J(R.tolak || [bj && bj.pemegang, tk.pemegang]));
  kirim(R.kiriman[0]);
  var lB = lanjutBuku(2026, MACB), bB = susunBatal(2026, [], W, MACB), l0 = lanjutBuku(2026), lA = lanjutBuku(2026, HPA);
  ok('P4-1 berjalan: Lanjutkan & Batalkan dari Mac B DITOLAK dengan kalimat yang menyebut HP A; tanpa identitas perangkat juga ditolak; dari HP A jalan',
    KAL_A.test(lB.tolak || '') && KAL_A.test(bB.tolak || '') && KAL_A.test(l0.tolak || '') && !lA.tolak && !!lA.kiriman && lA.kiriman.length === 2, J([lB.tolak, bB.tolak, l0.tolak, lA.tolak]));
  (lA.kiriman || []).forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar.slice(0, 18));
  var hB = arsipBerhentiBuku(2026, MACB), hA = arsipBerhentiBuku(2026, HPA), bB2 = susunBatal(2026, [], W, MACB);
  ok('P4-1 terkunci, arsip setengah: lanjut arsip (penjaga arsip) & Batalkan dari Mac B ditolak; dari HP A boleh',
    acara(2026).status === 'terkunci' && KAL_A.test(bukanPemegang(2026, MACB)) && KAL_A.test(hB) && hA === '' && KAL_A.test(bB2.tolak || ''), J([acara(2026).status, hB, hA, bB2.tolak]));
  arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var pB = susunPeriksaArsip(2026, W, MACB), sB = susunSelesai(2026, 'cad.json', W, true, MACB), pA = susunPeriksaArsip(2026, W, HPA);
  ok('P4-1 arsip habis: periksa ulang (hasil beku) & selesai dari Mac B ditolak (tidak ada tulisan); dari HP A jalan', !pB.dokumen && KAL_A.test(sB.tolak || '') && !!pA.dokumen, J([!!pB.dokumen, sB.tolak, !!pA.dokumen]));
  if (pA.dokumen) kirim({ dokumen: pA.dokumen }); var sA = susunSelesai(2026, 'cad.json', W, false, HPA); if (!sA.tolak) kirim(sA);
  ok('P4-1 HP A menyelesaikan; sesudah selesai tidak ada yang dijaga lagi', !sA.tolak && acara(2026).status === 'selesai' && bukanPemegang(2026, MACB) === '', J(sA.tolak)); });
coba('P4-1b', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); kirim(R.kiriman[0]);
  B = susunBatal(2026, [], W, HPA); (B.kiriman || []).forEach(kirim); if (B.akhir) kirim({ dokumen: [B.akhir] });
  var R2 = susunKunci(2026, D, jam('2027-01-06T10:00:00+07:00'), MACB); if (R2.kiriman) kirim(R2.kiriman[0]); var a2 = acara(2026) || {};
  ok('P4-1b dibatalkan dari HP A, dimulai lagi di Mac B: pemegang = Mac B (pemegang lama tidak terbawa); HP A sekarang ditolak',
    !R2.tolak && a2.status === 'berjalan' && !!a2.pemegang && a2.pemegang.id === 'p-macb' && /sedang dikerjakan di Mac toko contoh/.test(lanjutBuku(2026, HPA).tolak || '') && !lanjutBuku(2026, MACB).tolak, J([R2.tolak, a2.status, a2.pemegang, lanjutBuku(2026, HPA).tolak]));
  // Mac B membatalkan percobaannya; percobaan berikut disusun TANPA identitas perangkat (uji / latihan lama) → pemegang Mac B tidak boleh terbawa
  B = susunBatal(2026, [], W, MACB); (B.kiriman || []).forEach(kirim); if (B.akhir) kirim({ dokumen: [B.akhir] });
  R = susunKunci(2026, D, jam('2027-01-07T10:00:00+07:00')); if (R.kiriman) kirim(R.kiriman[0]); var a3 = acara(2026) || {};
  ok('P4-1b berita acara TANPA pemegang (uji / latihan lama, pemegang percobaan lama tidak terbawa): boleh dari perangkat mana pun',
    !R.tolak && a3.status === 'berjalan' && !a3.pemegang && !lanjutBuku(2026, MACB).tolak && bukanPemegang(2026, HPA) === '', J([R.tolak, a3.status, a3.pemegang])); });

// ---- putaran 4 P4-2 · AMBIL ALIH: HP A (pemegang) rusak / hilang / datanya terhapus di tengah tutup buku. Mac B boleh mengambil alih HANYA bila: tersambung & data
//      tutup buku dari server, antrean Mac B kosong, berita acara tidak berubah ≥ 60 menit, HP A tidak berdenyut 15 menit terakhir — dua ketukan, kalimat jujur
var ambilAlih = function (t, L, w, y) { return typeof susunAmbilAlih === 'function' ? susunAmbilAlih(t, L, w, y) : { tolak: '(ambil alih tidak ada)' }; };
// "server" yang mencap jam ubah tiap dokumen (= beriAtribusiAkun di firebase.js: diubahPada)
function kirimJam(k) { return kirim({ dokumen: (k.dokumen || []).map(function (x) { return { koleksi: x.koleksi, data: Object.assign({}, x.data, { diubahPada: new Date(__KINI).toISOString() }) }; }), hapus: k.hapus }); }
function denyut(id, iso) { terapkanKeCache([{ koleksi: 'perangkatStatus', data: { id: id, nama: '', aplikasi: 'baru', pada: new Date(iso).toISOString() } }]); }
coba('P4-2', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); kirimJam(R.kiriman[0]); denyut('p-hpa', '2027-01-05T10:05:00+07:00');
  var t30 = ambilAlih(2026, MACB, jam('2027-01-05T10:30:00+07:00'), true);
  denyut('p-hpa', '2027-01-05T11:00:00+07:00'); var t70 = ambilAlih(2026, MACB, jam('2027-01-05T11:10:00+07:00'), true);
  var W2 = jam('2027-01-05T11:30:00+07:00');
  var antre = ambilAlih(2026, Object.assign({}, MACB, { antre: [{ id: 'k-1' }] }), W2, true), mati = ambilAlih(2026, Object.assign({}, MACB, { offline: true }), W2, true);
  dariCache('tutupBukuAcara', true); var basi = ambilAlih(2026, MACB, W2, true); dariCache('tutupBukuAcara', false);
  dariCache('perangkatStatus', true); var basiD = ambilAlih(2026, MACB, W2, true); dariCache('perangkatStatus', false);
  var diri = ambilAlih(2026, HPA, W2, true);
  ok('P4-2 ditolak: berita acara baru berubah 30 menit · HP A berdenyut 10 menit lalu · antrean Mac B belum kosong · tanpa internet · data tutup buku / denyut masih salinan perangkat · pemegangnya sendiri',
    /60 menit/.test(t30.tolak || '') && /berdenyut 10 menit/.test(t70.tolak || '') && /belum diakui server/.test(antre.tolak || '') && /internet/.test(mati.tolak || '') && /data terbaru/.test(basi.tolak || '') && /denyut/.test(basiD.tolak || '') && !!diri.tolak && !diri.dokumen
    && ![t30, t70, antre, mati, basi, basiD, diri].some(function (x) { return x.dokumen; }), J([t30.tolak, t70.tolak, antre.tolak, mati.tolak, basi.tolak, basiD.tolak, diri.tolak]));
  var y1 = ambilAlih(2026, MACB, W2, false);
  ok('P4-2 semua syarat terpenuhi (berita acara diam 90 menit, HP A terakhir berdenyut 30 menit lalu): ketukan PERTAMA = kalimat peringatan jujur, belum menulis apa pun',
    !!y1.perluYakin && !y1.dokumen && /HP owner contoh/.test(y1.tolak || '') && /kiriman yang belum terkirim/.test(y1.tolak || '') && /masuk belakangan/.test(y1.tolak || '') && /HP lama mati/.test(y1.tolak || ''), J(y1));
  var y2 = ambilAlih(2026, MACB, W2, true); if (y2.dokumen) kirimJam(y2); var a = acara(2026) || {};
  ok('P4-2 ketukan kedua: berita acara yang sama (status & rencana tetap) dengan pemegang Mac B + pemegangLama HP A + jam ambil alih',
    !y2.tolak && !!y2.dokumen && a.status === 'berjalan' && !!a.rencana && !!a.pemegang && a.pemegang.id === 'p-macb' && !!a.pemegangLama && a.pemegangLama.id === 'p-hpa' && !!a.diambilAlihPada, J([y2.tolak, a.status, a.pemegang, a.pemegangLama, a.diambilAlihPada]));
  var lA = lanjutBuku(2026, HPA), kembali = ambilAlih(2026, HPA, jam('2027-01-05T11:35:00+07:00'), true), lB = lanjutBuku(2026, MACB);
  ok('P4-2 sesudahnya HP A (hidup lagi) ditolak seperti perangkat lain dan tidak bisa langsung mengambil alih kembali; Mac B melanjutkan sampai terkunci',
    /sedang dikerjakan di Mac toko contoh/.test(lA.tolak || '') && !!kembali.tolak && !kembali.dokumen && !lB.tolak && (function () { (lB.kiriman || []).forEach(kirimJam); return acara(2026).status === 'terkunci' && acara(2026).pemegang.id === 'p-macb'; })(), J([lA.tolak, kembali.tolak, lB.tolak]));
  B = susunBatal(2026, arsipSimulasi(), W2, MACB); (B.kiriman || []).forEach(kirimJam); if (B.akhir) { pulihkanArsip(2026, B.pulih); kirimJam({ dokumen: [B.akhir] }); }
  var R3 = susunKunci(2026, D, jam('2027-01-06T10:00:00+07:00'), HPA); var a3 = R3.acara || {};
  ok('P4-2 dibatalkan Mac B, dimulai lagi di HP A: pemegang HP A, tanpa pemegangLama / jam ambil alih percobaan lama', !B.tolak && !R3.tolak && !!a3.pemegang && a3.pemegang.id === 'p-hpa' && !a3.pemegangLama && !a3.diambilAlihPada,
    J([B.tolak, R3.tolak, a3.pemegang, a3.pemegangLama, a3.diambilAlihPada])); });

// ---- putaran 4 P4-3 · arsip HP A: potongan TERAKHIR sudah terkirim; sebelum ia mendarat, tutup buku dibatalkan tuntas dari tab lain di HP A (pemegang yang sama).
//      Potongan itu lalu mendarat. Callback progres uang.js harus membaca status sesudah potongan terakhir juga → potongan itu dikembalikan HP A sendiri.
//      Dulu `sudah < total ? … : ''` → tidak diperiksa → catatan 2026 potongan terakhir tertinggal di arsip sesudah "dibatalkan", tanpa pita.
// = firebase.js arsipkanBerkas (potongan 18, progres sesudah commit) + callback progres jalankanBuku di uang.js (bentuknya dibaca dari berkas: UANG_CEK_TIAP_POTONGAN)
function arsipLayarP4(tahun, daftar, L, sebelumPotong) {
  var henti = arsipBerhentiBuku(tahun, L), tadi = 0, potongTadi = [], balik = [];
  try { if (!henti) for (var i = 0; i < daftar.length; i += 18) { if (sebelumPotong) sebelumPotong(i / 18 + 1); arsipkanDokumen(tahun, daftar.slice(i, i + 18)); var sudah = Math.min(i + 18, daftar.length);
      potongTadi = daftar.slice(tadi, sudah); tadi = sudah; henti = (UANG_CEK_TIAP_POTONGAN || sudah < daftar.length) ? arsipBerhentiBuku(tahun, L) : ''; if (henti) throw new Error(henti); } }
  catch (e) { balik = henti ? arsipBalikBuku(tahun, potongTadi) : []; if (balik.length) pulihkanArsip(tahun, balik); }
  return { henti: henti || '', dikembalikan: balik.length };
}
coba('P4-3', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); var nJual = ambilPenjualanSemua().length; R.kiriman.forEach(kirim);
  var daftarA = arsipBuku(2026).daftar; var nPotong = Math.ceil(daftarA.length / 18); var nAkhir = daftarA.length - (nPotong - 1) * 18;
  var H = arsipLayarP4(2026, daftarA, HPA, function (ke) { if (ke !== nPotong) return;
    var B2 = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }; }), W, HPA);
    (B2.kiriman || []).forEach(kirim); if (B2.akhir) { pulihkanArsip(2026, B2.pulih); kirim({ dokumen: [B2.akhir] }); } });
  var diArsip = arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).length;
  ok('P4-3 potongan terakhir (' + nAkhir + ' dari ' + daftarA.length + ' catatan) mendarat sesudah pembatalan tuntas: HP A membaca status sesudahnya, berhenti, mengembalikannya — penjualan 2026 utuh, arsip 2026 kosong',
    nPotong >= 2 && /dibatalkan/.test(H.henti) && H.dikembalikan === nAkhir && acara(2026).status === 'dibatalkan' && ambilPenjualanSemua().length === nJual && diArsip === 0 && kemajuanBuku() === null,
    J([nPotong, H, acara(2026).status, ambilPenjualanSemua().length + '/' + nJual, diArsip, kemajuanBuku()])); });

// ---- putaran 4 P4-4 (TP3-T1/LP3-Y1): hasil beku periksa ulang disusun HP A sesudah arsip habis, lalu TERTAHAN (sinyal putus). Sementara itu tab lain di HP A
//      (pemegang yang sama) membatalkan sampai tuntas / menyelesaikan. Tulisan itu lalu mendarat: dulu berita acara UTUH berstatus 'terkunci' → 'dibatalkan' /
//      'selesai' mundur jadi 'terkunci', pita menyuruh "lanjutkan arsip" atas catatan yang sudah kembali (penjualan 2026 tersapu ke arsip).
function bacaArsip26() { return arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }; }); }
coba('P4-4', function () { kotak(40); var nJual = ambilPenjualanSemua().length; W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var PA = susunPeriksaArsip(2026, W, HPA); var bentuk = (PA.dokumen || []).map(function (x) { return x.koleksi + (x.data.status !== undefined ? ':status' : ''); });
  var B2 = susunBatal(2026, bacaArsip26(), W, HPA); (B2.kiriman || []).forEach(kirim); if (B2.akhir) { pulihkanArsip(2026, B2.pulih); kirim({ dokumen: [B2.akhir] }); }
  if (PA.dokumen) kirim({ dokumen: PA.dokumen });
  ok('P4-4 hasil beku = satu dokumen pengaturan tanpa kolom status; mendarat SESUDAH pembatalan tuntas → berita acara tetap dibatalkan, pita kosong, penjualan 2026 utuh',
    bentuk.join() === 'pengaturan' && acara(2026).status === 'dibatalkan' && kemajuanBuku() === null && ambilPenjualanSemua().length === nJual, J([bentuk, acara(2026).status, kemajuanBuku(), ambilPenjualanSemua().length + '/' + nJual]));
  kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  PA = susunPeriksaArsip(2026, W, HPA); var SL = susunSelesai(2026, 'cad2.json', W, false, HPA); if (!SL.tolak) kirim(SL); if (PA.dokumen) kirim({ dokumen: PA.dokumen });
  ok('P4-4 mendarat SESUDAH selesai → berita acara tetap selesai (tidak mundur jadi terkunci yang bisa dibatalkan lagi)', !SL.tolak && acara(2026).status === 'selesai' && !!acara(2026).selesaiPada && kemajuanBuku() === null,
    J([SL.tolak, acara(2026).status, kemajuanBuku()])); });
// LP3-Z1: percobaan 1 dibekukan TIDAK SAMA (nota 5 Jan masuk sebelum arsip habis), lalu dibatalkan; percobaan 2 (8 Jan) belum membekukan hasilnya sendiri
//      (tertahan / tab tertutup) → "selesai" & pita TIDAK memakai hasil percobaan 1 (dulu kolomnya ikut terbawa di berita acara percobaan 2)
coba('P4-4 Z1', function () { kotak(40); var W1 = jam('2027-01-05T07:00:00+07:00'); var R1 = susunKunci(2026, D, W1, HPA); R1.kiriman.forEach(kirim);
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'jan5', tanggal: '2027-01-05', jam: '11:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]);
  arsipkanDokumen(2026, arsipBuku(2026).daftar); var PA1 = susunPeriksaArsip(2026, W1, HPA); if (PA1.dokumen) kirim({ dokumen: PA1.dokumen }); var beku1 = PA1.PU ? bkKalimatPeriksa(PA1.PU) : '';
  var B1 = susunBatal(2026, bacaArsip26(), W1, HPA); (B1.kiriman || []).forEach(kirim); if (B1.akhir) { pulihkanArsip(2026, B1.pulih); kirim({ dokumen: [B1.akhir] }); }
  var W2 = jam('2027-01-08T07:00:00+07:00'); var R2 = susunKunci(2026, D, W2, HPA); (R2.kiriman || []).forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  var KM = kemajuanBuku(); var S1 = susunSelesai(2026, 'cad2.json', W2, false, HPA);
  ok('P4-4 Z1 hasil beku percobaan 1 (TIDAK SAMA) tidak dipakai percobaan 2: pita selesaikan tanpa AWAS, "selesai" diterima pada ketukan pertama',
    /TIDAK SAMA/.test(beku1) && !R2.tolak && !!KM && KM.fase === 'selesaikan' && !/AWAS/.test(KM.teks) && !S1.tolak, J([beku1, R2.tolak, KM && KM.teks, S1.tolak || 'diterima']));
  var PA2 = susunPeriksaArsip(2026, W2, HPA); if (PA2.dokumen) kirim({ dokumen: PA2.dokumen }); var dok = dokDiCache('pengaturan', 'periksaArsip2026') || {};
  ok('P4-4 Z1 hasil beku percobaan 2 menggantikannya dan bertanda percobaan 2 (dipakai "selesai")', !!PA2.dokumen && !!dok.percobaan && dok.percobaan === String(acara(2026).paraf.pada) && dok.percobaan !== String(R1.acara.paraf.pada),
    J([!!PA2.dokumen, dok.percobaan])); });

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


UANG_TIAP_POTONGAN = "henti = BK.arsipBerhentiBuku(tahun, lokal()); if (henti) throw new Error(henti);"


def cek_tiap_potongan():
    """putaran 4 P4-3: callback progres arsip di uang.js membaca status sesudah SETIAP potongan (termasuk yang terakhir)?"""
    return UANG_TIAP_POTONGAN in open(os.path.join(bundel_baru.AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()


def utama(js, cek=None):
    cek = cek_tiap_potongan() if cek is None else cek
    h, e = jalan(JAM + js + '\nvar UANG_CEK_TIAP_POTONGAN = ' + ('true' if cek else 'false') + ';\nvar KOTAK = ' + json.dumps(uji_uang_baru.KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


STATIS = [
    ('kiriman bertahap menunggu pengakuan server & berhenti dengan kalimat kiriman ke-n', ["await tulisDokumen(k.dokumen, k.hapus || [], { tunggu: true })", "kabar: BK.kabarBerhentiBuku(k.lanjutan ? 'lanjut' : 'kunci', tahun, k.ke, k.total, h, k)"]),
    ('§8 no. 7 · pembatalan yang berhenti memakai kalimat yang menyebut tombol yang benar', ["kabar: BK.kabarBerhentiBuku('batal', tahun, i + 1, r.kiriman.length, h)"]),
    ('pita kemajuan K6: lanjutkan / batalkan / selesaikan', ["BK.kemajuanBuku()", 'data-aksi="bkLanjut"', 'data-k="tb-selesaikan"']),
    ('langkah 7 memakai tahun yang terkunci', ["const tahun = KM7 && KM7.fase === 'selesaikan' ? KM7.tahun :"]),
    ('patokan kas tahun di layar (bukan titik kas sekarang)', ["const SB = BK.barisTahun(T.tahun); const B = s.sesudahLive || bandingB(s, T);", "const bandingB = (s, T) => { const SB = BK.barisTahun(T.tahun);"]),
    ('§8 no. 2 · Lanjutkan menyetel titik kas perangkat HANYA dari titik yang ikut kiriman lanjut (lanjutBuku.titik)', ["jalankanBuku(KM.tahun, Lj.kiriman || [], Lj.titik || null,"]),
    ('§8 no. 4 · Lanjutkan & Batalkan menunggu antrean perangkat (fase tunggu) — tidak mengirim apa pun', ["if (KM.fase === 'tunggu') return set({ kabar: KM.teks, kabarAwas: true });", "if (KM && KM.fase === 'tunggu') return set({ yakinBatalB: null, kabar: KM.teks, kabarAwas: true });"]),
    ('§8 no. 6 · selesai di layar: periksa ulang & arsip SEBELUM berkas diunduh, ketukan kedua bila beda', ["if (k === 'cadangan2') { const r0 = BK.susunSelesai(tahun, '', waktu(), s.yakinSelesai === tahun, lokal());", "const r = BK.susunSelesai(tahun, nama, waktu(), s.yakinSelesai === tahun, lokal());"]),
    ('§8 no. 4 · firebase.js menyetor dokumen yang menunggu server (hasPendingWrites) ke toko.js', ["setelTertunda(k.nama, tunda.map((t) => t.id));", "KOLEKSI.forEach((k) => { pasok(k.nama, []); setelTertunda(k.nama, []); });"], 'baru/js/data/firebase.js'),
    ('putaran 3 AAL1 · Lanjutkan & Batalkan tidak jalan selagi tutup buku / arsip sibuk di perangkat ini', ["bkLanjut: async () => { if (st().sibuk) return;", "bkBatal: async () => { if (st().sibuk) return;"]),
    ('putaran 3 AAL1 · arsip berhenti di antara potongan bila berita acara tahun itu bukan lagi terkunci', ["potongTadi = A.daftar.slice(tadi, sudah); tadi = sudah; henti = BK.arsipBerhentiBuku(tahun, lokal()); if (henti) throw new Error(henti);", "let henti = BK.arsipBerhentiBuku(tahun, lokal());", "if (henti) { set({ sibuk: false, progres: null, kabar: henti, kabarAwas: true }); return false; }"]),
    ('putaran 3 AAL1 · tombol pita .seg.mati di layar Uang sungguh tidak bisa diketuk', [".layar-uang .seg.mati { opacity: 0.45; pointer-events: none; }"], 'baru/css/uang.css'),
    ('putaran 3 AAL1 (susulan) · arsip yang berhenti karena pembatalan mengembalikan potongan terakhirnya sendiri', ["const balik = henti ? BK.arsipBalikBuku(tahun, potongTadi) : []; if (balik.length) { try { await pulihkanArsip(tahun, balik); }", "potongTadi = A.daftar.slice(tadi, sudah); tadi = sudah;"]),
    ('putaran 3 AAL1 (susulan) · pembatalan membaca arsip ulang sekali sebelum berita acara dibatalkan', ["const sisaA = await bacaArsipTahun(tahun); if (sisaA.length) await pulihkanArsip(tahun, sisaA, balik);"]),
    ('putaran 3 UTBU-1 · hasil periksa ulang dibekukan saat arsip habis (ditulis ke berita acara)', ["const PA = BK.susunPeriksaArsip(tahun, waktu(), lokal()); if (PA.dokumen) { try { await tulisDokumen(PA.dokumen, [], { tunggu: true }); }", "const PU = PA.PU || {"]),
    ('putaran 3 UTBU-2 · kabar sesudah arsip memakai kalimat periksa ulang yang sama (belum bisa dihitung ≠ TIDAK SAMA)', ["' AWAS: ' + BK.bkKalimatPeriksa(PA.PU) + ' — periksa dulu, jangan diselesaikan.'"]),
    ('putaran 3 AAL3 · Lanjutkan menolak tutup buku yang tidak utuh (fase rusak) — tidak meneruskan arsip', ["if (KM.fase === 'rusak') return set({ kabar: KM.teks, kabarAwas: true });"]),
    ('putaran 3 AAL4 · Lanjutkan & Batalkan hanya dari data server (tanpa internet / salinan perangkat = ditolak)', ["bkLanjut: async () => { if (st().sibuk) return; const sb = BK.bkSambungan(lokal()); if (sb) return set({ kabar: sb, kabarAwas: true });", "bkBatal: async () => { if (st().sibuk) return; const sb = BK.bkSambungan(lokal()); if (sb) return set({ yakinBatalB: null, kabar: sb, kabarAwas: true });"]),
    ('putaran 3 AAL4 · firebase.js menyetor tanda salinan perangkat (fromCache) per koleksi ke toko.js', ["setelDariCache(k.nama, _dariCache[k.nama]);"], 'baru/js/data/firebase.js'),
    ('putaran 3 AAL5 · firebase.js mencatat HAPUS yang menunggu server per kiriman sampai commit selesai', ["setelHapusTertunda(idKiriman, H);", ".finally(() => { setelHapusTertunda(idKiriman, null);"], 'baru/js/data/firebase.js'),
    ('putaran 4 P4-3 · callback progres arsip membaca status sesudah SETIAP potongan, termasuk yang terakhir (bentuk yang disuntik ke kotak pasir)', [UANG_TIAP_POTONGAN]),
    ('putaran 4 P4-1 · Kunci mencatat perangkat ini sebagai pemegang (lokal() ke susunKunci)', ["arsipNama: s.arsipNama }, waktu(), lokal()); if (r.tolak) return set({ siapKunci: false,"]),
    ('putaran 4 P4-1 · Lanjutkan & Batalkan hanya dari pemegang — dicek sebelum arsip dibaca; susun* menerima lokal()', ["const bp = BK.bkBukanPemegang(KM.tahun, lokal()); if (bp) return set({ kabar: bp, kabarAwas: true });", "const bp = BK.bkBukanPemegang(tahun, lokal()); if (bp) return set({ yakinBatalB: null, kabar: bp, kabarAwas: true });", "const Lj = BK.lanjutBuku(KM.tahun, lokal());", "const r = BK.susunBatal(tahun, arsip, waktu(), lokal());"]),
    ('putaran 4 P4-1 · kiriman berikutnya (tutup buku & pembatalan) berhenti bila perangkat ini bukan lagi pemegangnya', ["const bpK = BK.bkBukanPemegang(tahun, lokal()); if (bpK) { set({ sibuk: false, progres: null, kabar: bpK, kabarAwas: true }); return false; }\n      let h = null; try { h = await tulisDokumen(k.dokumen, k.hapus || [], { tunggu: true });"]),
    ('putaran 4 P4-2 · tombol ambil alih di pita perangkat lain; dua ketukan & syaratnya dijaga BK.susunAmbilAlih', ["data-aksi=\"bkAmbilAlih\">${KM && s.yakinAmbilB === KM.tahun ? 'ketuk sekali lagi · ambil alih' : 'ambil alih'}", "const r = BK.susunAmbilAlih(KM.tahun, lokal(), waktu(), st().yakinAmbilB === KM.tahun); if (r.perluYakin) return set({ yakinAmbilB: KM.tahun, kabar: r.tolak, kabarAwas: true });"]),
    ('putaran 4 P4-1 · pita K6 di perangkat lain: keadaan + kalimat pemegang, TANPA tombol lanjutkan / batalkan / selesai', ["const bukanP = KM ? BK.bkBukanPemegang(KM.tahun, lokal()) : '';", "${bukanP ? pitaBukan : h`<div class=\"hg-pil\"><div class=\"seg aktif ${s.sibuk ? 'mati' : ''}\" data-aksi=\"bkLanjut\">", "${bukanP ? pitaBukan : h`<div class=\"hg-pil\"><div class=\"seg aktif ${s.sibuk ? 'mati' : ''}\" data-aksi=\"bkCadangan\""]),
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
    ('§8 no. 4 · Lanjutkan & Batalkan tidak memeriksa antrean perangkat', 'baru/js/layar/tutup-buku-logika.js', "  const nT = bkTunda(tahun); if (nT) return { tolak: bkKalimatTunda(tahun, nT) };\n  const ub = bkBerubah(a);", "  const ub = bkBerubah(a);"),
    ('§8 no. 4 · pita tidak memeriksa antrean perangkat', 'baru/js/layar/tutup-buku-logika.js', "  const nT = bkTunda(tahun); if (nT) return { tahun, fase: 'tunggu', tunda: nT, teks: bkKalimatTunda(tahun, nT) };", "  const nT = 0;"),
    ('§8 no. 5 · Lanjutkan memakai patokan periksa ulang dari saat MULAI', 'baru/js/layar/tutup-buku-logika.js', "const kunci = Object.assign({}, a, { status: 'terkunci', hariIni: { tanggal: hari, baris:", "const kunci = Object.assign({}, a, { status: 'terkunci', hariIniBaru: { tanggal: hari, baris:"),
    ('§8 no. 6 · selesai tanpa memeriksa arsip & periksa ulang', 'baru/js/layar/tutup-buku-logika.js', "  const sisa = arsipBuku(tahun).n; if (sisa) return { tolak: ANGKA(sisa) + ' catatan '", "  const sisa = 0; if (sisa) return { tolak: ANGKA(sisa) + ' catatan '"),
    ('§8 no. 6 · selesai menerima periksa ulang yang beda tanpa ketukan kedua', 'baru/js/layar/tutup-buku-logika.js', "  if (kal && !yakin) return {", "  if (kal && !yakin && false) return {"),
    ('§8 no. 7 · pembatalan yang berhenti di kiriman 1 menyuruh "Lanjutkan"', 'baru/js/layar/tutup-buku-logika.js', "return awal + (ke === 1 ? ' Kiriman ini tidak masuk", "return awal + (false ? ' Kiriman ini tidak masuk"),
    ('§8 no. 7 · tutup buku yang berhenti di kiriman 1 menyuruh "Lanjutkan"', 'baru/js/layar/tutup-buku-logika.js', "return awal + (ke === 1 ? ' Tidak ada yang masuk", "return awal + (false ? ' Tidak ada yang masuk"),
    ('§8 no. 8 · mulai baru membawa tanggal pembatalan lama', 'baru/js/layar/tutup-buku-logika.js', "delete acara.dariStatus; delete acara.dibatalkanPada; delete acara.dibatalkanTanggal;", "delete acara.dariStatus;"),
    ('§8 no. 9 · daftar periksa Kunci bulan tidak melihat tutup buku setengah jalan', 'baru/js/layar/kunci-periode-logika.js', "tambah({ id: 'tutupBukuTuntas', blokir: true, ok: !KMb,", "tambah({ id: 'tutupBukuTuntas', blokir: true, ok: true || !KMb,"),
    ('putaran 3 AAL1 · arsip tidak berhenti walau tutup buku dibatalkan dari perangkat lain', 'baru/js/layar/tutup-buku-logika.js', "const a = bkAcara(tahun); if (a && a.status === 'terkunci') return bkBukanPemegang(tahun, L);", "const a = bkAcara(tahun); if (true) return '';"),
    ('putaran 3 UTBU-1 · "selesai" & pita menghitung ulang periksa ulang (hasil yang dibekukan diabaikan)', 'baru/js/layar/tutup-buku-logika.js', "  if (!P || !Array.isArray(P.baris) || !bkPercobaan(a) ||", "  if (true ||"),
    ('putaran 3 UTBU-1 · hasil periksa ulang tidak disusun untuk dibekukan', 'baru/js/layar/tutup-buku-logika.js', "  if (!PU || !a || a.status !== 'terkunci' || arsipBuku(tahun).n || bkBukanPemegang(tahun, L) || !bkPercobaan(a)) return { PU };", "  if (true) return { PU };"),
    ('putaran 4 P4-4 · hasil beku kembali ditulis di berita acara UTUH (berstatus terkunci)', 'baru/js/layar/tutup-buku-logika.js', "  return { PU, dokumen: [{ koleksi: 'pengaturan', data: periksaArsip }] };", "  return { PU, dokumen: [{ koleksi: 'tutupBukuAcara', data: Object.assign({}, a, { periksaArsip }) }, { koleksi: 'pengaturan', data: periksaArsip }] };"),
    ('putaran 4 P4-4 · hasil beku percobaan lama dipakai percobaan berikut (tanda percobaan diabaikan)', 'baru/js/layar/tutup-buku-logika.js', " || String(P.percobaan || '') !== bkPercobaan(a)) return periksaUlangBuku(tahun);", ") return periksaUlangBuku(tahun);"),
    ('putaran 3 UTBU-2 · baris yang tidak bisa dihitung mesin disebut TIDAK SAMA', 'baru/js/layar/tutup-buku-logika.js', "beda: PU.baris.filter((b) => b.tahu && b.b !== null && !b.sama)", "beda: PU.baris.filter((b) => b.tahu && !b.sama)"),
    ('putaran 3 AAL2 · batch penanda tahun lalu diarsipkan dalam urutan biasa (bisa lebih dulu dari pembukanya)', 'baru/js/layar/tutup-buku-logika.js', "const daftar = semua.filter((x) => !tanda(x)).concat(semua.filter(tanda));", "const daftar = semua;"),
    ('putaran 3 AAL3 · terkunci dengan saldo pembuka tidak lengkap tetap disebut fase arsip', 'baru/js/layar/tutup-buku-logika.js', "if (adaP < Number(a.nPembuka) && bkEra() === tahun) return {", "if (false) return {"),
    ('putaran 3 AAL4 · Lanjutkan & Batalkan jalan dari salinan perangkat / tanpa internet', 'baru/js/layar/tutup-buku-logika.js', "if (!(L && L.offline) && !basi) return '';", "if (true) return '';"),
    ('putaran 3 AAL5 · hapus yang menunggu server tidak dihitung tunggu', 'baru/js/layar/tutup-buku-logika.js', "  Object.keys(KOLEKSI_CACHE).forEach((c) => { n += hapusTertunda(KOLEKSI_CACHE[c]); });\n", ""),
    ('putaran 3 AAL6 · satu kiriman antre menyebut pita "… sudah masuk" (yang tidak akan muncul)', 'baru/js/layar/tutup-buku-logika.js', "'Sesudah itu: kalau pita ' + (total === 1 ?", "'Sesudah itu: kalau pita ' + (false ?"),
    ('putaran 3 AAL7 · pita menghitung kiriman rencana (bukan saldo pembuka yang sudah masuk)', 'baru/js/layar/tutup-buku-logika.js', "const P = a.pembuka || []; const sudah = P.filter((x) => !!dokDiCache(x.koleksi, x.data.id)).length;", "const P = (a.rencana || {}).kiriman || []; const sudah = 1;"),
    ('putaran 3 AAL7 · kiriman lanjutan dinomori menurut rencana saat mulai', 'baru/js/layar/tutup-buku-logika.js', "const k = { ke: i + 1, total: Pt.potongan.length, lanjutan: true,", "const k = { ke: i + 2, total: Pt.potongan.length + 1, lanjutan: true,"),
    ('putaran 3 AAL1 (susulan) · potongan yang mendarat sesudah pembatalan tidak dikembalikan', 'baru/js/layar/tutup-buku-logika.js', "if (!a || (a.status !== 'membatalkan' && a.status !== 'dibatalkan')) return [];", "if (true) return [];"),
    ('putaran 3 AAL1 (susulan) · tahun yang SELESAI ditutup perangkat lain ikut dikembalikan', 'baru/js/layar/tutup-buku-logika.js', "if (!a || (a.status !== 'membatalkan' && a.status !== 'dibatalkan')) return [];", "if (!a) return [];"),
    ('putaran 4 P4-1 · berita acara tidak mencatat pemegang', 'baru/js/layar/tutup-buku-logika.js', "const pg = bkPerangkatIni(L); if (pg) acara.pemegang = pg;", "const pg = null;"),
    ('putaran 4 P4-1 · percobaan ulang membawa pemegang percobaan lama', 'baru/js/layar/tutup-buku-logika.js', "  delete acara.pemegang;\n", "\n"),
    ('putaran 4 P4-1 · penjaga pemegang mati (perangkat mana pun boleh)', 'baru/js/layar/tutup-buku-logika.js', "  if (L && L.idPerangkat && String(L.idPerangkat) === String(p.id)) return '';", "  return '';"),
    ('putaran 4 P4-1 · Lanjutkan tidak memeriksa pemegang', 'baru/js/layar/tutup-buku-logika.js', "  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };\n  const nT = bkTunda(tahun);", "  const nT = bkTunda(tahun);"),
    ('putaran 4 P4-1 · Batalkan tidak memeriksa pemegang', 'baru/js/layar/tutup-buku-logika.js', "if (nT) return { tolak: bkKalimatTunda(tahun, nT) };\n  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };", "if (nT) return { tolak: bkKalimatTunda(tahun, nT) };"),
    ('putaran 4 P4-1 · selesai tidak memeriksa pemegang', 'baru/js/layar/tutup-buku-logika.js', "return { tolak: 'Kunci tahunnya dulu' };\n  const bp = bkBukanPemegang(tahun, L); if (bp) return { tolak: bp };", "return { tolak: 'Kunci tahunnya dulu' };"),
    ('putaran 4 P4-1 · penjaga arsip tidak memeriksa pemegang', 'baru/js/layar/tutup-buku-logika.js', "if (a && a.status === 'terkunci') return bkBukanPemegang(tahun, L);", "if (a && a.status === 'terkunci') return '';"),
    ('putaran 4 P4-2 · ambil alih tanpa syarat 60 menit berita acara diam', 'baru/js/layar/tutup-buku-logika.js', "if (menit === null || menit < 60) return {", "if (false) return {"),
    ('putaran 4 P4-2 · ambil alih walau pemegang masih berdenyut', 'baru/js/layar/tutup-buku-logika.js', "if (terakhir !== null && t - terakhir < 15 * 60000) return {", "if (false) return {"),
    ('putaran 4 P4-2 · ambil alih walau antrean perangkat ini belum kosong', 'baru/js/layar/tutup-buku-logika.js', "  if (nA) return { tolak: 'Ambil alih ditolak: '", "  if (false) return { tolak: 'Ambil alih ditolak: '"),
    ('putaran 4 P4-2 · ambil alih tanpa internet / dari salinan perangkat', 'baru/js/layar/tutup-buku-logika.js', "  const sb = bkSambungan(L); if (sb) return { tolak: sb };\n  if (koleksiDariCache('perangkatStatus'))", "  if (false)"),
    ('putaran 4 P4-2 · ambil alih sekali ketuk (tanpa kalimat peringatan)', 'baru/js/layar/tutup-buku-logika.js', "  if (!yakin) return { perluYakin: true,", "  if (false) return { perluYakin: true,"),
    ('putaran 4 P4-2 · percobaan berikut membawa jejak ambil alih lama', 'baru/js/layar/tutup-buku-logika.js', "  delete acara.pemegangLama; delete acara.diambilAlihPada;", "  delete acara.diambilAlihPada;"),
    ('pemeriksaan ulang kembali ke 1 Jan vs 31 Des', 'baru/js/layar/tutup-buku-logika.js', "return bandingBuku({ harta: H.baris, utang: [] }, o);",
     "const B1 = barisBuku((tahun + 1) + '-01-01', (tahun + 1) + '-01-01'); const o1 = {}; B1.harta.concat(B1.utang).forEach((b) => { o1[b.id] = b.n; }); return bandingBuku({ harta: a.sebelum, utang: [] }, o1);"),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for st in STATIS:   # statis: jangkar pertama dibuang dari berkasnya → pemeriksa statis wajib melihatnya
            nama, wajib = st[0], st[1]; u0 = open(os.path.join(bundel_baru.AKAR, st[2] if len(st) > 2 else 'baru/js/layar/uang.js'), encoding='utf-8').read()
            if not all(x in u0 for x in wajib): print('KONTROL BASI  statis uang.js · ' + nama); kode = 3; continue
            u1 = u0.replace(wajib[0], ''); kurang = [x for x in wajib if x not in u1]
            print(('BERBUNYI ' if kurang else 'DIAM!!   ') + 'statis uang.js · ' + nama + ' dibuang → tidak ada: ' + ' | '.join(kurang)[:100])
            if not kurang: kode = 3
        l, g = utama(bundelan(), cek=False)
        print(('BERBUNYI ' if g else 'DIAM!!   ') + 'putaran 4 P4-3 · uang.js memeriksa status hanya bila masih ada potongan berikutnya (bentuk lama) → ' + (g[0][:140] if g else '-'))
        if not g: kode = 3
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
    for st in STATIS:
        nama, wajib = st[0], st[1]; u = open(os.path.join(bundel_baru.AKAR, st[2] if len(st) > 2 else 'baru/js/layar/uang.js'), encoding='utf-8').read()
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
