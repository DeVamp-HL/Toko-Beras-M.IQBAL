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
  T10 (asap, bila ada cadangan lokal di _privat/) data toko pada 5 Jan 2027: dipecah, tiap kiriman ≤ 18; batal juga ≤ 18 — hari berjualan tanpa tutup hari
      diberi putusan TIRUAN dulu (tanpa itu pintu masuk wajib menolak karena g1; uji_kunci_periode.PUTUSAN_TIRUAN)
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
  P4-5  lembar K6 sesudah kunci: baris yang sisi mesinnya tidak bisa dihitung bertanda "?" (bukan "≠"); kalimat lembar = kalimat pita (bkKalimatPeriksa)
  TRV6-EKOR-1 (tinjauan rules v6) — ekor pembatalan (kembalikan arsip → baca ulang → kembalikan sisa → 'dibatalkan'); yang dijalankan = jalankanBatal
        APA ADANYA dari uang.js (batal_uang membaca berkasnya), HP A beku di satu titik, perangkat lain bekerja, HP A hidup lagi:
        a          Mac B ambil alih → batal tuntas → mulai lagi → arsip → selesai; potongan 2 mendarat sesudahnya → HP A berhenti, potongan itu diarsipkan lagi,
                   arsip percobaan baru tidak dikembalikan, tidak ada berita acara; angka = sebelum HP A hidup lagi; tetap 'selesai'
        titik 1–4  sama, beku sebelum pengembalian pertama / sebelum baca ulang / saat baca ulang / sebelum 'dibatalkan' → berhenti di titik itu
        b          pembatalan biasa satu perangkat (dari terkunci & berjalan): tuntas seperti sebelum, penjaga tidak pernah berbunyi
        c          Mac B batal tuntas, belum mulai lagi → HP A berhenti, TIDAK mengarsipkan (catatan itu tempatnya di buku hidup)
        pemegang · dua tab (percobaan lain, pemegang sama) · berjalan (percobaan baru baru kiriman 1) · balik (pulihBalikBuku: percobaan sama = tidak)

  SIAP 2027 (owner 7 Okt 2026, paket A — "gua mau semua siap ketika sudah tahun 2027"):
  S-A1     hari berjualan tanpa tutup hari: tanpa putusan g1 & susunKunci MENOLAK; putusan per tanggal (alasan ≥ 5) = dokumen aturanToko/putusanHari; putusan
           riwayat kunci bulan dipakai ulang; ikut berita acara; dicabut → menolak lagi; tutup hari tidak dibuat mundur
  S-RITUAL ritual penuh: periksa ulang 14 baris sama (12 + modal owner + upah); A3 tanda buku (25 kg, digabung, adukan, merek pemasok, berstok 0) & rak Jual
           sebelum = sesudah; A4 modal owner menyeberang (pembuka 31 Des, bukan uang masuk); A6 upah belum dibayar sama (patokan sistem lama dibawa berita acara),
           upah Desember yang dibayar Januari dibukukan ke Januari; A7 KR1 / laju / daftar pelanggan sebelum = sesudah (identitas dengan mesin sebelum ritual)
  S-A5     stok/kemasan minus, kelebihan bayar pelanggan, bayar lebih ke pemasok: g6 menolak dengan kalimat & jalan beres, baris pembanding tidak buta minus
  S-A8     perkiraan kuota tulis/hapus/baca vs batas Spark + jam reset (14.00/15.00 WIB) + peringatan MEPET / TIDAK MUAT + perkiraan Batalkan
  S-A9     catatan 2026 yang mendarat sesudah penanda (di tengah arsip / sesudah selesai): terdeteksi, pita selesaikan (bukan lanjutkan arsip), ketukan kedua,
           tercatat di berita acara & Beranda, "sudah dicatat" tanpa menghapus
  S-A2     Beranda 3 Jan: tutup buku tahun lalu belum dikerjakan — kunci bulan menunggu (daftar periksa kunci bulan: uji_kunci_periode.py)
  ASAP SIAP 2027 (cadangan LOKAL, tidak di-commit; dilewati di CI): ritual penuh pada 1 Jan 2027 15.10 & 5 Jan 2027 (+ Batalkan) dengan putusan TIRUAN:
           semua baris sama persis, rak Jual, buku 25 kg, tanda buku, modal, upah, KR1 tiap pelanggan terdaftar, laju, daftar pelanggan, stok tiap buku sama.
           python3 alat-uji/uji_tutup_buku_bertahap.py --asap=/jalur/backup-batch-….json   (atau env TUTUP_BUKU_ASAP=/jalur/…)

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
  // siap 2027 (A1): hari berjualan kotak pasir tanpa tutup hari diputus "diterima apa adanya" — tanpa putusan, susunKunci menolak (gerbang g1 di pintu masuk)
  putusSemua();
  localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(TITIK31));
}
// semua tahun yang ada di kotak (P3-AAL2 menutup 2027 juga — panggil lagi sesudah menambah nota)
function putusSemua() { var tH = {}; ambilTutupHari().forEach(function (t) { tH[t.tanggal] = 1; }); var ph = {}; ambilPenjualan().forEach(function (p) { if (p.tanggal && !tH[p.tanggal]) ph[p.tanggal] = { jenis: 'diterima', alasan: 'kotak pasir — hari contoh tanpa tutup hari' }; });
  pasok('aturanToko', cacheMentah('aturan').filter(function (d) { return String(d.id) !== 'putusanHari'; }).concat([{ id: 'putusanHari', hari: ph }])); }
var n0 = 50000; function jam(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: '10:00', kini: new Date(iso).toISOString(), idUnik: function () { n0 += 1; return n0; } }; }
var D = { paraf: { owner: true, saksi: true }, saksi: 'Saksi Contoh', langkah: {} };
// satu kiriman "masuk server": penjaga pusat yang sama dengan layar (bulan terkunci / > 18 pemeriksaan = tidak dikirim), lalu cache
var tolakPenjaga = [];
function kirim(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) { tolakPenjaga.push(j.pesan); return false; }
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); return true; }
function idKiriman(k) { return k.dokumen.map(function (x) { return x.koleksi + '|' + x.data.id + '|' + (x.data.status || ''); }).join(','); }
function baris(B) { var o = {}; B.harta.concat(B.utang).forEach(function (b) { o[b.id] = b.n; }); return o; }
function samaBaris(a, b) { return Object.keys(a).every(function (k) { return (a[k] === null && b[k] === null) || (a[k] !== null && b[k] !== null && Math.abs(a[k] - b[k]) < 0.5); }); }
var PEMBUKA = ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop', 'modal'];   // siap 2027: modal owner punya saldo pembuka
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
  ok('N9 tutup buku 2026 setengah jalan: daftar periksa Kunci bulan Januari 2027 punya butir ⛔ yang belum beres (setengah jalan + siap 2027 A2 tutup buku tahun lalu belum selesai) → kunci bulan ditolak', tb.length === 2 && tb.every(function (b) { return b.blokir && !b.ok; }) && !DP.boleh, J(tb));
  jam('2027-01-05T10:00:00+07:00'); L = lanjutBuku(2026); (L.kiriman || []).forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar); var SL = susunSelesai(2026, 'cadangan-sesudah.json', W); if (!SL.tolak) kirim(SL);
  jam('2027-02-05T10:00:00+07:00'); DP = kpDaftarPeriksa('2027-01', new Date(__KINI), KK); tb = butirTB(DP);
  ok('N9 sesudah tutup buku selesai: kedua butir beres', kemajuanBuku() === null && tb.length === 2 && tb.every(function (b) { return b.ok; }), J([SL.tolak, tb])); });

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
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'j2027', tanggal: '2027-06-01', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]); putusSemua();
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

// ---- putaran 4 BP4R-2 · HP A memulai lalu membatalkan tuntas; sesudah itu kiriman saldo pembuka HP A yang tertahan mendarat ('dibatalkan' + sisa pembuka).
//      "Lanjutkan pembatalan" dari 'dibatalkan' tidak dijaga pemegang (boleh dari perangkat mana pun) → perangkat yang memulainya harus jadi pemegang 'membatalkan'.
//      Dulu pemegang HP A ikut tersalin → Mac B diterima di kiriman 1 lalu ditolak dirinya sendiri di kiriman 2 ("sedang dikerjakan di HP A").
coba('P4-7', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); kirim(R.kiriman[0]);
  B = susunBatal(2026, [], W, HPA); (B.kiriman || []).forEach(kirim); if (B.akhir) kirim({ dokumen: [B.akhir] });
  kirim(R.kiriman[1]); var a0 = acara(2026) || {};
  var BB = susunBatal(2026, [], jam('2027-01-05T12:00:00+07:00'), MACB); var b1 = BB.kiriman ? BB.kiriman[0].dokumen[0].data : {}; if (BB.kiriman) kirim(BB.kiriman[0]);
  ok('P4-7 sisa saldo pembuka mendarat sesudah dibatalkan → pembatalan lanjutan dari Mac B: pemegang "membatalkan" = Mac B, Mac B tidak ditolak dirinya sendiri di kiriman berikutnya',
    a0.status === 'dibatalkan' && !BB.tolak && b1.status === 'membatalkan' && !!b1.pemegang && b1.pemegang.id === 'p-macb' && bukanPemegang(2026, MACB) === '' && KAL_A.test(bukanPemegang(2026, HPA).replace('Mac toko contoh', 'HP owner contoh')),
    J([a0.status, BB.tolak, b1.status, b1.pemegang, bukanPemegang(2026, MACB)])); });

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

// ---- putaran 4 P4-5 (TP3-T4/LP3-C2): arsip putus 5 Jan, tutup hari 5 & 6 Jan memajukan titik kas, Lanjutkan 7 Jan. Lembar K6 sesudah kunci memakai hasil periksa
//      ulang (sesudahLive): baris uang yang sisi MESIN-nya tidak bisa dihitung = '?' (belum bisa dihitung), bukan '≠'; kalimatnya = kalimat pita. Dulu lembar berkata
//      "ADA 4 BARIS YANG TIDAK SAMA" + '≠' sementara kabar & pita berkata "4 baris belum bisa dihitung".
coba('P4-5', function () { kotak(40); W = jam('2027-01-05T10:00:00+07:00'); R = susunKunci(2026, D, W, HPA); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar.slice(0, 18));
  ['2027-01-05', '2027-01-06'].forEach(function (t) { var tk = { id: 'titikKas', tanggal: t, laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000, diubahPada: t + 'T14:00:00.000Z' };
    terapkanKeCache([{ koleksi: 'pengaturan', data: tk }]); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(tk)); });
  var W7 = jam('2027-01-07T09:00:00+07:00'); arsipkanDokumen(2026, arsipBuku(2026).daftar); var PU = susunPeriksaArsip(2026, W7, HPA).PU || { baris: [] };
  var kas = PU.baris.filter(function (b) { return ['laci', 'brankas', 'rekening', 'amplop'].indexOf(b.id) >= 0; }), lain = PU.baris.filter(function (b) { return kas.indexOf(b) < 0; }); var kal = bkKalimatPeriksa(PU);
  ok('P4-5 4 baris uang yang sisi mesinnya tidak bisa dihitung bertanda "?" (bukan "≠"), baris lain "✓"; kalimat yang sama dengan pita: "4 baris belum bisa dihitung", tanpa TIDAK SAMA',
    kas.length === 4 && kas.every(function (b) { return b.b === null && b.tanda === '?'; }) && lain.length === 10 && lain.every(function (b) { return b.tanda === '✓'; }) && /4 baris belum bisa dihitung/.test(kal) && !/TIDAK SAMA/.test(kal),
    J([PU.baris.map(function (b) { return b.id + ' ' + b.tanda; }), kal])); });

// ---- TRV6-EKOR-1 (tinjauan rules v6) · EKOR PEMBATALAN. HP A (pemegang) membatalkan dari 'terkunci'; semua kiriman tarik masuk; HP A BEKU di tengah ekor
//      (pengembalian arsip → baca arsip ulang → kembalikan sisanya → 'dibatalkan'); perangkat lain bekerja; HP A hidup lagi. Dulu penjaga pemegang hanya per
//      kiriman tarik → HP A mengembalikan sisa arsip + SELURUH arsip tahun itu (termasuk arsip percobaan baru) ke buku hidup: 'selesai' + angka DOBEL tanpa pita.
//      Yang dijalankan = fungsi jalankanBatal APA ADANYA dari uang.js (buatBatalUang, dibaca dari berkasnya oleh Python) dengan pengganti: tulisDokumen = server
//      yang mencap jam ubah + model kecil v6 untuk berita acara; pulihkanArsip = firebase.js pulihkanBerkas (potongan 18, progres sesudah tiap potongan mendarat);
//      titik "beku" = kait di antara langkah. Perangkat lain memakai lapisan logika di "server" yang sama (cache kotak pasir).
var EK = null;
// model kecil rules v6 (bukan model lengkap — itu periksa_rules.py): percobaan LAIN hanya di atas 'dibatalkan' dengan jam mulai lebih baru; 'selesai' tidak mundur
function v6Tolak(baru) { var lama = acara(Number(baru.tahun)); if (!lama) return false; var pl = String((lama.paraf || {}).pada || ''), pb = String((baru.paraf || {}).pada || '');
  if (pl === pb) return lama.status === 'selesai' && baru.status !== 'selesai'; return !(lama.status === 'dibatalkan' && pb > pl); }
function kaitEk(nama) { var f = EK.kait[nama]; if (!f) return; delete EK.kait[nama]; f(); if (nama === EK.beku) { EK.jepret = jepretEk(); EK.bangun = true; } }
function jepretEk() { var B = barisBuku('2027-01-05', '2027-01-05');
  return J({ jual: ambilPenjualanSemua().length, arsip: arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).length, pembuka: nPembukaMentah(2026), baris: baris(B) }); }
function pulihPotongEk(tahun, potong) { terapkanKeCache(potong.map(function (x) { return { koleksi: x.koleksi, data: x.dok }; }));
  _arsip = _arsip.filter(function (a) { return !(a.tahun === tahun && potong.some(function (x) { return x.koleksi === a.koleksi && String(x.idAsli) === String(a.idAsli); })); }); }
// BK = namespace tutup-buku-logika.js: BK.<nama> dicari di lingkup bundel jsc (eval NAMA fungsi yang dipakai uang.js — kode uji, tidak ada masukan luar)
var ALAT_EK = { set: function (p) { Object.assign(EK.S, p); }, lokal: function () { return EK.L; }, waktu: function () { return EK.W; }, setelTitik: function () {}, LANGKAH_KOSONG: function () { return {}; },
  BK: new Proxy({}, { get: function (t, k) { return typeof k === 'string' && /^[A-Za-z_]\w*$/.test(k) ? eval(k) : undefined; } }),
  tulisDokumen: async function (daftar, hapus) { var ba = (daftar || []).filter(function (x) { return x.koleksi === 'tutupBukuAcara'; }); if (EK.bangun) EK.acaraSesudah += ba.length;
    if (ba.some(function (x) { return v6Tolak(x.data); })) return { gagal: true, pesan: 'permission-denied (model v6)' };
    kirimJam({ dokumen: daftar || [], hapus: hapus || [] }); if (!ba.some(function (x) { return x.data.status === 'dibatalkan'; }) && nPembukaMentah(2026) === 0) kaitEk('kirimanAkhir'); return { ok: true }; },
  pulihkanArsip: async function (tahun, daftar, progres) { EK.fase += 1; var fase = EK.fase;
    for (var i = 0; i < daftar.length; i += 18) { kaitEk('pulih:' + fase + ':' + (i / 18 + 1)); var potong = daftar.slice(i, i + 18); pulihPotongEk(tahun, potong);
      EK.potong.push((EK.bangun ? 'sesudah ' : '') + fase + ':' + (i / 18 + 1) + ':' + potong.length); if (progres) progres(Math.min(i + 18, daftar.length), daftar.length); }
    kaitEk('sesudahPulih:' + fase); return { ok: true, n: daftar.length }; },
  bacaArsipTahun: async function (tahun) { EK.baca += 1; kaitEk('baca:' + EK.baca); if (EK.bangun) EK.bacaSesudah += 1; return bacaArsipTahun(tahun); },
  arsipkanDokumen: async function (tahun, daftar, progres) { EK.arsipUlang.push(daftar.length); return arsipkanDokumen(tahun, daftar, progres); } };
function batalHPA(kait, beku) {
  EK = { S: {}, L: HPA, W: jam('2027-01-05T10:00:00+07:00'), kait: kait || {}, beku: beku || '', bangun: false, jepret: '', fase: 0, baca: 0, bacaSesudah: 0, acaraSesudah: 0, potong: [], arsipUlang: [], hasil: undefined };
  buatBatalUang(ALAT_EK)(2026).then(function (x) { EK.hasil = x; }, function (e) { EK.hasil = 'JATUH: ' + (e && e.message ? e.message : e); }); drainMicrotasks(); return EK;
}
// HP A mengunci 2026 (pemegang), arsip habis, lalu mengetuk "batalkan" → jalankanBatal (dijalankan batalHPA)
function siapEk() { kotak(40); var W0 = jam('2027-01-05T10:00:00+07:00'); var s0 = baris(barisTahun(2026)), n0 = ambilPenjualanSemua().length; var R0 = susunKunci(2026, D, W0, HPA); (R0.kiriman || []).forEach(kirimJam);
  arsipkanDokumen(2026, arsipBuku(2026).daftar); return { s0: s0, nJual: n0, P0: R0.acara ? String(R0.acara.paraf.pada) : '', tolak: R0.tolak || '', status: (acara(2026) || {}).status, arsip: arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).length }; }
// Mac B (≥ 60 menit kemudian): ambil alih → tuntaskan pembatalan → mulai lagi (percobaan baru) → arsip → selesai
function macAlih() { var y = susunAmbilAlih(2026, MACB, jam('2027-01-05T12:00:00+07:00'), true); if (y.dokumen) kirimJam(y); EK.alih = y.tolak || 'ok'; }
function macBatal() { macAlih(); var B2 = susunBatal(2026, bacaArsip26(), jam('2027-01-05T12:05:00+07:00'), MACB); (B2.kiriman || []).forEach(kirimJam); if (B2.akhir) { pulihkanArsip(2026, B2.pulih); kirimJam({ dokumen: [B2.akhir] }); } EK.batalB = B2.tolak || 'ok'; }
function macMulai() { macBatal(); var W3 = jam('2027-01-05T12:10:00+07:00'); var R2 = susunKunci(2026, D, W3, MACB); EK.R2 = R2; EK.P1 = R2.acara ? String(R2.acara.paraf.pada) : ''; return W3; }
function macSelesai() { var W3 = macMulai(); (EK.R2.kiriman || []).forEach(kirimJam); arsipkanDokumen(2026, arsipBuku(2026).daftar); var PA = susunPeriksaArsip(2026, W3, MACB); if (PA.dokumen) kirimJam({ dokumen: PA.dokumen });
  var SL = susunSelesai(2026, 'cad2.json', W3, true, MACB); if (!SL.tolak) kirimJam(SL); EK.selesaiB = (EK.R2.tolak || '') + (SL.tolak || ''); }
var KAL_EKOR = /^Pembatalan tutup buku 2026 dihentikan: tutup bukunya sudah diubah dari (perangkat lain|jendela lain di perangkat ini) \(/;
// (a) + tiap titik pemeriksaan: HP A beku di titik itu; Mac B ambil alih, batal tuntas, mulai lagi, arsip, selesai; HP A hidup lagi → berhenti, tidak mengembalikan
//     arsip percobaan baru, tidak menulis berita acara; angka = sebelum HP A hidup lagi; berita acara tetap 'selesai' percobaan baru
function cekSelesaiEk(nama, ket, x, syarat) { var a = acara(2026) || {};
  ok('TRV6-EKOR ' + nama + ' · ' + ket, x.alih === 'ok' && x.batalB === 'ok' && x.selesaiB === '' && x.bangun && x.hasil === false && KAL_EKOR.test(x.S.kabar || '') && /sudah ditutup lagi sampai selesai/.test(x.S.kabar || '') && !!x.S.kabarAwas
    && x.acaraSesudah === 0 && jepretEk() === x.jepret && a.status === 'selesai' && String(a.paraf.pada) === x.P1 && x.P1 !== String((x.siap || {}).P0) && kemajuanBuku() === null && syarat,
    J([x.alih, x.batalB, x.selesaiB, x.hasil, x.S.kabar, x.acaraSesudah, x.potong.filter(function (p) { return /^sesudah/.test(p); }), x.bacaSesudah, x.arsipUlang, jepretEk() === x.jepret ? 'angka sama' : 'ANGKA BEDA: ' + jepretEk() + ' vs ' + x.jepret, a.status])); }
var sesudahEk = function (x) { return x.potong.filter(function (p) { return /^sesudah/.test(p); }); };
coba('TRV6-EKOR a', function () { var S0 = siapEk(); var x = batalHPA({ 'pulih:1:2': macSelesai }, 'pulih:1:2'); x.siap = S0;
  cekSelesaiEk('a', 'HP A beku sesudah potongan pengembalian 1 (' + S0.arsip + ' catatan arsip); potongan 2 mendarat sesudah Mac B menyelesaikan percobaan baru → HP A berhenti di potongan itu, mengarsipkannya lagi (18), tidak membaca / mengembalikan arsip percobaan baru',
    x, S0.tolak === '' && S0.arsip > 36 && J(sesudahEk(x)) === J(['sesudah 1:2:18']) && J(x.arsipUlang) === J([18]) && x.bacaSesudah === 0); });
coba('TRV6-EKOR titik 1', function () { var S0 = siapEk(); var x = batalHPA({ kirimanAkhir: macSelesai }, 'kirimanAkhir'); x.siap = S0;
  cekSelesaiEk('titik 1', 'beku sesudah kiriman tarik terakhir, SEBELUM pengembalian pertama → tidak satu potongan pun dikembalikan', x, sesudahEk(x).length === 0 && x.arsipUlang.length === 0); });
coba('TRV6-EKOR titik 2', function () { var S0 = siapEk(); var x = batalHPA({ 'sesudahPulih:1': macSelesai }, 'sesudahPulih:1'); x.siap = S0;
  cekSelesaiEk('titik 2', 'beku sesudah pengembalian pertama tuntas, SEBELUM arsip dibaca ulang → arsip percobaan baru tidak dibaca; potongan yang sah kembali tidak diarsipkan lagi', x, x.bacaSesudah === 0 && sesudahEk(x).length === 0 && x.arsipUlang.length === 0); });
coba('TRV6-EKOR titik 3', function () { var S0 = siapEk(); var x = batalHPA({ 'baca:2': macSelesai }, 'baca:2'); x.siap = S0;
  cekSelesaiEk('titik 3', 'beku saat arsip dibaca ulang (yang terbaca = SELURUH arsip percobaan baru), SEBELUM pengembalian kedua → tidak ada yang dikembalikan', x, sesudahEk(x).length === 0 && x.fase === 1 && x.arsipUlang.length === 0); });
coba('TRV6-EKOR titik 4', function () { var S0 = siapEk(); var telat = null;
  // satu potongan arsip yang mendarat telat (P3-AAL1 susulan) → arsip yang dibaca ulang berisi satu catatan → pengembalian kedua jalan; beku sesudahnya, SEBELUM 'dibatalkan'
  var x = batalHPA({ 'baca:2': function () { var d = arsipBuku(2026).daftar; telat = d.length; if (d.length) arsipkanDokumen(2026, d.slice(0, 1)); }, 'sesudahPulih:2': macSelesai }, 'sesudahPulih:2'); x.siap = S0;
  cekSelesaiEk('titik 4', 'beku sesudah pengembalian kedua, SEBELUM berita acara dibatalkan → tidak menulis berita acara', x, telat > 0 && x.fase === 2 && x.arsipUlang.length === 0); });
// (c) Mac B membatalkan tuntas lalu BELUM mulai lagi → HP A berhenti; potongan yang mendarat TIDAK diarsipkan lagi (tempatnya di buku hidup)
coba('TRV6-EKOR c', function () { var S0 = siapEk(); var x = batalHPA({ 'pulih:1:2': macBatal }, 'pulih:1:2'); var a = acara(2026) || {};
  ok('TRV6-EKOR c · Mac B ambil alih & batal tuntas (belum mulai lagi); HP A hidup lagi → berhenti ("sudah dibatalkan tuntas"), tidak menulis berita acara, tidak mengarsipkan apa pun; penjualan 2026 utuh, arsip 2026 kosong, saldo pembuka 0',
    x.alih === 'ok' && x.batalB === 'ok' && x.hasil === false && KAL_EKOR.test(x.S.kabar || '') && /dari perangkat lain/.test(x.S.kabar || '') && /sudah dibatalkan tuntas/.test(x.S.kabar || '') && x.acaraSesudah === 0 && x.arsipUlang.length === 0 && J(sesudahEk(x)) === J(['sesudah 1:2:18'])
    && a.status === 'dibatalkan' && ambilPenjualanSemua().length === S0.nJual && arsipSimulasi().filter(function (q) { return q.tahun === 2026; }).length === 0 && nPembukaMentah(2026) === 0 && jepretEk() === x.jepret && samaBaris(S0.s0, baris(barisTahun(2026))) && kemajuanBuku() === null,
    J([x.alih, x.batalB, x.hasil, x.S.kabar, x.acaraSesudah, x.arsipUlang, sesudahEk(x), a.status, ambilPenjualanSemua().length + '/' + S0.nJual, nPembukaMentah(2026)])); });
// pemegang: Mac B baru mengambil alih (masih 'membatalkan' percobaan yang sama) → HP A berhenti, tidak mengarsipkan apa pun; Mac B menuntaskan → angka seperti semula
coba('TRV6-EKOR pemegang', function () { var S0 = siapEk(); var x = batalHPA({ 'pulih:1:2': macAlih }, 'pulih:1:2'); var a1 = acara(2026) || {};
  var B2 = susunBatal(2026, bacaArsip26(), jam('2027-01-05T12:30:00+07:00'), MACB); (B2.kiriman || []).forEach(kirimJam); if (B2.akhir) { pulihkanArsip(2026, B2.pulih); kirimJam({ dokumen: [B2.akhir] }); }
  ok('TRV6-EKOR pemegang · sesudah diambil alih Mac B HP A berhenti ("sedang dibatalkan di Mac toko contoh"), tidak menulis berita acara / mengarsipkan; Mac B menuntaskan → dibatalkan, penjualan 2026 utuh, arsip kosong',
    x.alih === 'ok' && x.hasil === false && KAL_EKOR.test(x.S.kabar || '') && /sedang dibatalkan di Mac toko contoh/.test(x.S.kabar || '') && x.acaraSesudah === 0 && x.arsipUlang.length === 0 && a1.status === 'membatalkan' && a1.pemegang.id === 'p-macb'
    && !B2.tolak && acara(2026).status === 'dibatalkan' && ambilPenjualanSemua().length === S0.nJual && arsipSimulasi().filter(function (q) { return q.tahun === 2026; }).length === 0 && nPembukaMentah(2026) === 0 && kemajuanBuku() === null,
    J([x.alih, x.hasil, x.S.kabar, x.acaraSesudah, x.arsipUlang, a1.status, B2.tolak, acara(2026).status, ambilPenjualanSemua().length + '/' + S0.nJual])); });
// percobaan: DUA TAB di HP A (pemegang sama). Tab 1 beku di ekor; tab 2 menuntaskan pembatalan itu, mulai lagi (percobaan baru, HP A), mengunci, mengarsip, lalu
//      mulai MEMBATALKAN percobaan baru (kiriman masuk, ekornya belum) → tab 1 hidup lagi: 'membatalkan' + pemegang sama, tapi percobaan lain → berhenti
coba('TRV6-EKOR dua tab', function () { var S0 = siapEk(); var B3 = null;
  var x = batalHPA({ 'pulih:1:2': function () { var B1 = susunBatal(2026, bacaArsip26(), jam('2027-01-05T10:20:00+07:00'), HPA); (B1.kiriman || []).forEach(kirimJam); if (B1.akhir) { pulihkanArsip(2026, B1.pulih); kirimJam({ dokumen: [B1.akhir] }); }
    var R2 = susunKunci(2026, D, jam('2027-01-05T10:30:00+07:00'), HPA); (R2.kiriman || []).forEach(kirimJam); arsipkanDokumen(2026, arsipBuku(2026).daftar); EK.P1 = R2.acara ? String(R2.acara.paraf.pada) : '';
    B3 = susunBatal(2026, bacaArsip26(), jam('2027-01-05T10:40:00+07:00'), HPA); (B3.kiriman || []).forEach(kirimJam); } }, 'pulih:1:2');
  var a1 = acara(2026) || {}; if (B3 && B3.akhir) { pulihkanArsip(2026, B3.pulih); kirimJam({ dokumen: [B3.akhir] }); }
  ok('TRV6-EKOR dua tab · tab 1 berhenti (percobaan lain sedang dibatalkan di perangkat yang sama), tidak menulis berita acara, tidak mengarsipkan; tab 2 menuntaskan → dibatalkan, penjualan 2026 utuh, arsip kosong',
    !!B3 && !B3.tolak && x.hasil === false && KAL_EKOR.test(x.S.kabar || '') && /sedang dibatalkan di HP owner contoh/.test(x.S.kabar || '') && /dari jendela lain di perangkat ini/.test(x.S.kabar || '') && x.acaraSesudah === 0 && x.arsipUlang.length === 0 && a1.status === 'membatalkan' && String(a1.paraf.pada) === EK.P1 && EK.P1 !== S0.P0
    && acara(2026).status === 'dibatalkan' && ambilPenjualanSemua().length === S0.nJual && arsipSimulasi().filter(function (q) { return q.tahun === 2026; }).length === 0 && nPembukaMentah(2026) === 0 && kemajuanBuku() === null,
    J([B3 && B3.tolak, x.hasil, x.S.kabar, x.acaraSesudah, x.arsipUlang, a1.status, acara(2026).status, ambilPenjualanSemua().length + '/' + S0.nJual])); });
// berjalan: Mac B batal tuntas lalu mulai lagi, baru kiriman 1 masuk (percobaan baru 'berjalan' — tahun 2026 masih terbuka) → HP A berhenti, TIDAK mengarsipkan
coba('TRV6-EKOR berjalan', function () { var S0 = siapEk(); var x = batalHPA({ 'pulih:1:2': function () { macMulai(); if (EK.R2.kiriman) kirimJam(EK.R2.kiriman[0]); } }, 'pulih:1:2'); var a = acara(2026) || {};
  ok('TRV6-EKOR berjalan · percobaan baru baru berjalan (' + ((EK.R2 || {}).kiriman || []).length + ' kiriman, 1 masuk) → HP A berhenti ("sedang ditutup lagi"), tidak mengarsipkan; penjualan 2026 tetap di buku hidup, angka = sebelum HP A hidup lagi',
    x.hasil === false && KAL_EKOR.test(x.S.kabar || '') && /sedang ditutup lagi/.test(x.S.kabar || '') && x.acaraSesudah === 0 && x.arsipUlang.length === 0 && a.status === 'berjalan' && ((EK.R2 || {}).kiriman || []).length > 1
    && ambilPenjualanSemua().length === S0.nJual && jepretEk() === x.jepret, J([x.hasil, x.S.kabar, x.acaraSesudah, x.arsipUlang, a.status, ambilPenjualanSemua().length + '/' + S0.nJual])); });
// (b) pembatalan biasa satu perangkat tanpa gangguan: tuntas persis seperti sebelum (penjaga tidak pernah berbunyi) — dari 'terkunci' (arsip > 2 potongan) & 'berjalan'
coba('TRV6-EKOR b', function () { var S0 = siapEk(); var x = batalHPA(); var a = acara(2026) || {}; var nP = Math.ceil(S0.arsip / 18);
  ok('TRV6-EKOR b · dari terkunci (' + S0.arsip + ' catatan arsip, ' + nP + ' potongan): tuntas — dibatalkan, kabar biasa, tanpa arsip ulang; penjualan 2026 utuh, arsip kosong, saldo pembuka 0, 12 baris 2026 = sebelum tutup buku',
    x.hasil === true && /^Tutup buku 2026 dibatalkan — /.test(x.S.kabar || '') && !x.S.kabarAwas && x.arsipUlang.length === 0 && x.potong.length === nP && nP > 2 && a.status === 'dibatalkan' && String(a.paraf.pada) === S0.P0
    && ambilPenjualanSemua().length === S0.nJual && arsipSimulasi().filter(function (q) { return q.tahun === 2026; }).length === 0 && nPembukaMentah(2026) === 0 && samaBaris(S0.s0, baris(barisTahun(2026))) && kemajuanBuku() === null,
    J([x.hasil, x.S.kabar, x.arsipUlang, x.potong.length + '/' + nP, a.status, ambilPenjualanSemua().length + '/' + S0.nJual, nPembukaMentah(2026)]));
  kotak(40); var R0 = susunKunci(2026, D, jam('2027-01-05T10:00:00+07:00'), HPA); kirimJam(R0.kiriman[0]); var y = batalHPA();
  ok('TRV6-EKOR b · dari berjalan (tanpa arsip): tuntas — dibatalkan, saldo pembuka 0', y.hasil === true && !y.S.kabarAwas && acara(2026).status === 'dibatalkan' && nPembukaMentah(2026) === 0 && kemajuanBuku() === null, J([y.hasil, y.S.kabar, acara(2026).status])); });
// pulihBalikBuku: percobaan yang SAMA (mis. terkunci telat dari zaman v5) tidak diarsipkan lagi; percobaan lain terkunci → bentuk arsipkanDokumen ({ koleksi, id, data })
coba('TRV6-EKOR balik', function () { kotak(5); var d = arsipBuku(2026).daftar.slice(0, 2).map(function (x) { return { koleksi: x.koleksi, idAsli: x.id, dok: x.data }; });
  pasok('tutupBukuAcara', [{ id: '2026', tahun: 2026, status: 'terkunci', paraf: { owner: true, saksi: true, pada: 'P0' } }]);
  var sama = typeof pulihBalikBuku === 'function' ? pulihBalikBuku(2026, d, 'P0') : null, lain = typeof pulihBalikBuku === 'function' ? pulihBalikBuku(2026, d, 'P-lama') : null;
  ok('TRV6-EKOR balik · percobaan sama = tidak diarsipkan lagi; percobaan lain terkunci = { koleksi, id: idAsli, data: dok } (bentuk arsipBuku/arsipkanDokumen)',
    !!sama && sama.length === 0 && !!lain && lain.length === 2 && lain.every(function (x, i) { return x.koleksi === d[i].koleksi && x.id === d[i].idAsli && x.data === d[i].dok; }), J([sama, lain && lain.map(function (x) { return [x.koleksi, x.id]; })])); });

__SIAP2027__
print(JSON.stringify({ lulus: lulus, gagal: gagal, penjaga: tolakPenjaga }));
"""

SIAP2027 = r"""
// ==================== SIAP 2027 (owner 7 Okt 2026, paket A) — KOTAK PASIR (nama & angka contoh) ====================
function semuaBaris(B) { var o = {}; B.harta.concat(B.utang, B.lain || []).forEach(function (b) { o[b.id] = b.n; }); return o; }
function ritualPenuh(tahun, w, L0) { var R = susunKunci(tahun, D, w, L0); if (R.tolak) return { tolak: R.tolak }; R.kiriman.forEach(kirim); arsipkanDokumen(tahun, arsipBuku(tahun).daftar);
  var PA = susunPeriksaArsip(tahun, w, L0, true); if (PA.dokumen) terapkanKeCache(PA.dokumen); return R; }
function potretSiap(kini) { var hari = hariIniIso(kini); __dom['jualKarungBerat'] = { value: '50' }; var s0 = keadaanAwal(); sinkronKeranjang(s0); var rak = susunRak(s0); var chip = {};
  ['karung', 'kemasan', 'literan', 'repack'].forEach(function (j) { rak[j].forEach(function (c) { chip[j + '|' + c.kunci + '|' + (c.berat || '')] = c.nama + '|' + c.ukuran + '|' + c.harga + '|' + Math.round((c.sisa || 0) * 1000) / 1000; }); });
  return { baris: semuaBaris(barisBuku(hari, hari)), chip: chip, ukuran: J(petaUkuran()), terpisah: J(indukTerpisah()), digabung: J(ukuranDigabung()), wadah: J(petaBukuWadah()), modal: modalTertanam(), upah: upahPada(hari),
    kas: J(['laci', 'brankas', 'rekening', 'amplop'].map(function (k) { var S = saldoKantong(); return S.ada ? Math.round(S[k]) : null; })) }; }
function bedaObj(a, b) { var out = []; Object.keys(a).concat(Object.keys(b).filter(function (k) { return !(k in a); })).forEach(function (k) { if (a[k] !== b[k]) out.push(k + ': ' + a[k] + ' → ' + b[k]); }); return out; }
function samaLaju(a, b) { return ['kgMerk', 'unitKemasan', 'pcsBahan'].every(function (g) { var x = a[g] || {}, y = b[g] || {}; return Object.keys(x).concat(Object.keys(y)).every(function (k) { return Math.abs((x[k] || 0) - (y[k] || 0)) < 1e-6; }); }); }
function orangRingkas(kini) { return semuaOrang(kini).map(function (o) { return o.kunci + '|' + o.nama + '|' + o.kunjungan + '|' + o.terakhir + '|' + Math.round(o.total) + '|' + o.nota + '|' + o.selang + '|' + o.jam + '|' + o.pola.join('+'); }).sort().join(','); }

// ---- A1 · putusan per tanggal: tanpa putusan memblokir; alasan ≥ 5; putusan kunci bulan dipakai ulang; ikut berita acara; tutup hari tidak dibuat mundur
coba('S-A1', function () { kotak(5); W = jam('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI); pasok('aturanToko', []);
  var G = gerbangBuku(2026, kini, {}, {}); var R0 = susunKunci(2026, D, W); var nTutup = ambilTutupHari().length;
  ok('A1 tanpa putusan: g1 MEMBLOKIR (lewati g1 tidak berlaku) & susunKunci menolak di pintu masuk dengan hari yang belum diputus', !G.daftar[0].ok && G.belumPutus.length > 1 && !gerbangBuku(2026, kini, {}, { g1: true }).daftar[0].ok && /belum ditutup & belum diputus/.test(R0.tolak || ''), J([G.daftar[0].ket, R0.tolak]));
  var H = G.belumPutus.slice(); var pendek = {}; H.forEach(function (t) { pendek[t] = 'abc'; });
  ok('A1 alasan kurang dari 5 huruf ditolak', /minimal 5 huruf/.test(susunPutusanHari(pendek, W).tolak || ''));
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: null, riwayat: [{ aksi: 'kunci', bulan: H[0].slice(0, 7), hari: [{ iso: H[0], jenis: 'diterima', alasan: 'diputus saat kunci bulan contoh', nNota: 1 }] }] } }]);
  var isi = {}; H.slice(1).forEach(function (t) { isi[t] = 'lupa ditutup, uang sudah dihitung contoh'; }); var P = susunPutusanHari(isi, W); if (!P.tolak) terapkanKeCache(P.dokumen);
  var G2 = gerbangBuku(2026, kini, {}, {});
  ok('A1 sesudah putusan: g1 lolos — tanggal pertama memakai putusan riwayat kunci bulan, sisanya dokumen aturanToko/putusanHari; tidak ada tutup hari baru', !P.tolak && G2.daftar[0].ok && G2.hari[0].putusan && G2.hari[0].putusan.dari === 'kunci bulan' && G2.hari.slice(1).every(function (h) { return h.putusan && h.putusan.dari === 'tutup buku'; }) && ambilTutupHari().length === nTutup, J([P.tolak, G2.daftar[0]]));
  var R = susunKunci(2026, D, W);
  ok('A1 berita acara membawa putusan tiap tanggal (alasan & jumlah nota); teks berita acara menyebutnya', !R.tolak && R.acara.putusanHari.length === H.length && R.acara.putusanHari.every(function (h) { return h.alasan.length >= 5 && h.nNota >= 1; })
    && /tidak ditutup, diterima apa adanya/.test(teksAcara(2026, { paraf: { owner: true, saksi: true } }, R.banding, R.sebelum, 'Saksi Contoh', W)), J(R.tolak || R.acara.putusanHari));
  var C = {}; C[H[1]] = ''; var P2 = susunPutusanHari(C, W); if (!P2.tolak) terapkanKeCache(P2.dokumen);
  ok('A1 putusan dicabut → g1 memblokir lagi (tanggal itu saja)', !P2.tolak && !gerbangBuku(2026, kini, {}, {}).daftar[0].ok && gerbangBuku(2026, kini, {}, {}).belumPutus.join() === H[1], J(P2.tolak)); });

// ---- A3 · A4 · A6 · A7 · ritual penuh di kotak yang memuat buku khusus, modal, upah sistem lama, dan pelanggan langganan
coba('S-RITUAL', function () { kotak(3);
  var hari = function (dari, sampai) { var o = {}; for (var d = new Date(dari + 'T00:00:00Z'); d.toISOString().slice(0, 10) <= sampai; d.setUTCDate(d.getUTCDate() + 1)) o[d.toISOString().slice(0, 10)] = 1; return o; };
  terapkanKeCache([
    { koleksi: 'batchMasuk', data: { id: 'sb1', tanggal: '2026-12-01', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [
      { merk: 'Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 12000, subtotalHarga: 6000000 },
      { merk: 'Bebek 25 kg', satuan: 'karung', beratKarung: 25, jumlahKarung: 8, totalKg: 200, hargaPerKg: 12100, subtotalHarga: 2420000, indukUkuran: 'Bebek' },
      { merk: 'Rusa', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, hargaPerKg: 11000, subtotalHarga: 2200000 },
      { merk: 'Rusa 25 kg', satuan: 'karung', beratKarung: 25, jumlahKarung: 2, totalKg: 50, hargaPerKg: 11000, subtotalHarga: 550000, indukUkuran: 'Rusa' },
      { merk: 'Kelas Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, hargaPerKg: 10000, subtotalHarga: 2000000, merkPemasok: 'Merek Pemasok Contoh' },
      { merk: 'Habis Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 10500, subtotalHarga: 1050000 },
      { merk: 'Adukan Kembang 5 kg', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, bukuAdukan: 'Kembang|5' }] } },
    { koleksi: 'produksiKemasan', data: { id: 'sg1', tanggal: '2026-12-05', jam: '09:00', namaProduk: 'Rusa', ukuranKemasan: 50, jumlahUnit: 1, kgDipakai: 50, hppSumberPerKgDipakai: 11000, jadiKarungUtuh: true, merkTujuan: 'Rusa', sumberList: [{ merk: 'Rusa 25 kg', kg: 50 }], gabungUkuran: { dari: 'Rusa 25 kg', induk: 'Rusa', berat: 25 } } },
    { koleksi: 'penjualan', data: { id: 'sj1', tanggal: '2026-12-10', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Habis Contoh', totalKg: 100, beratKarungAcuan: 50, jumlahKarung: 2, hargaTotal: 1100000, hppTotalSaatJual: 1050000 } },
    { koleksi: 'katalogHargaKarung', data: { id: 'Bebek', merk: 'Bebek', hargaPerKg: 13000 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Rusa', merk: 'Rusa', hargaPerKg: 12000 } },
    { koleksi: 'katalogHargaKarung', data: { id: 'Kelas Contoh', merk: 'Kelas Contoh', hargaPerKg: 11000 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Habis Contoh', merk: 'Habis Contoh', hargaPerKg: 11500 } },
    // A4: setoran & tarikan modal Desember (selain modal 25 jt kotak)
    { koleksi: 'modalOwner', data: { id: 'sm1', tanggal: '2026-12-15', jam: '09:00', tipe: 'setor', nominal: 10000000, catatan: 'tambah modal contoh' } },
    { koleksi: 'modalOwner', data: { id: 'sm2', tanggal: '2026-12-16', jam: '09:00', tipe: 'tarik', nominal: 2000000, catatan: 'tarik modal contoh' } },
    // A6: Gama dibayar SISTEM LAMA sampai 30 Nov (biayaBulanan, ikut diarsip); hari kerja Agu & 20 Nov sudah dibayar; 1 Des – 4 Jan belum
    { koleksi: 'biayaBulanan', data: { id: '2026-11', bulan: '2026-11', listrik: 0, internet: 0, akses: 0, keamanan: 0, rincianGaji: [{ nama: 'Gama', hari: 20, gaji: 1200000 }], tanggalBayarGaji: { Gama: '2026-11-30' }, gaji: 1200000, gajiHariOrang: 20 } },
    { koleksi: 'absenKaryawan', data: { id: 'gama|2026-08', nama: 'Gama', bulan: '2026-08', hari: { '2026-08-20': 1, '2026-08-21': 1, '2026-08-31': 1 } } },
    { koleksi: 'absenKaryawan', data: { id: 'gama|2026-11', nama: 'Gama', bulan: '2026-11', hari: { '2026-11-20': 1 } } },
    { koleksi: 'absenKaryawan', data: { id: 'gama|2026-12', nama: 'Gama', bulan: '2026-12', hari: hari('2026-12-01', '2026-12-31') } },
    { koleksi: 'absenKaryawan', data: { id: 'gama|2027-01', nama: 'Gama', bulan: '2027-01', hari: hari('2027-01-01', '2027-01-04') } },
    // A7: pelanggan langganan terdaftar — belanja Okt–Des & Januari; pelanggan lain yang cuma belanja 2026; bahan pakai & kemasan di 14 hari terakhir tahun
    { koleksi: 'pelangganCatatan', data: { id: 'pembeli contoh', nama: 'Pembeli Contoh', catatan: 'langganan contoh' } },
    { koleksi: 'penjualan', data: { id: 'sk1', tanggal: '2026-10-20', jam: '09:00', caraBayar: 'Tunai', namaPelanggan: 'Pembeli Contoh', jenis: 'karung', merkSumber: 'Bebek', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 650000, hppTotalSaatJual: 600000 } },
    { koleksi: 'penjualan', data: { id: 'sk2', tanggal: '2026-12-28', jam: '15:00', caraBayar: 'Kredit', namaPelanggan: 'Pembeli Contoh', jenis: 'karung', merkSumber: 'Bebek', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 650000, hppTotalSaatJual: 600000 } },
    { koleksi: 'penjualan', data: { id: 'sk3', tanggal: '2027-01-03', jam: '10:00', caraBayar: 'Tunai', namaPelanggan: 'Pembeli Contoh', jenis: 'karung', merkSumber: 'Bebek 25 kg', totalKg: 25, beratKarungAcuan: 25, jumlahKarung: 1, hargaTotal: 330000, hppTotalSaatJual: 302500 } },
    { koleksi: 'penjualan', data: { id: 'sk4', tanggal: '2026-12-29', jam: '11:00', caraBayar: 'Tunai', namaPelanggan: 'Pembeli Lama Contoh', jenis: 'karung', merkSumber: 'Kelas Contoh', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 550000, hppTotalSaatJual: 500000 } },
    { koleksi: 'penjualan', data: { id: 'sk5', tanggal: '2026-12-30', jam: '16:00', caraBayar: 'Tunai', namaPelanggan: 'Pembeli Lama Contoh', jenis: 'karung', merkSumber: 'Rusa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 600000, hppTotalSaatJual: 550000 } },
    { koleksi: 'stokBahanKemasan', data: { id: 'sbk1', tipe: 'beli', jenis: 'paperbag5l', jumlah: 100, hargaTotal: 100000, tanggal: '2026-12-01' } },
    { koleksi: 'stokBahanKemasan', data: { id: 'sbk2', tipe: 'pakai', jenis: 'paperbag5l', jumlah: 6, tanggal: '2026-12-27' } },
    // repack 14 hari terakhir (laju) · kemasan jadi yang habis pada 31 Des (chip "habis" di rak)
    { koleksi: 'penjualan', data: { id: 'sk6', tanggal: '2026-12-26', jam: '12:00', caraBayar: 'Tunai', jenis: 'repacking', merkSumber: 'Bebek', namaProduk: 'Bebek', totalKg: 5, hargaTotal: 70000, hppTotalSaatJual: 60000 } },
    { koleksi: 'produksiKemasan', data: { id: 'sk-p1', tanggal: '2026-12-02', jam: '09:00', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 2, hppPerUnit: 62000, kgDipakai: 10, merkSumber: 'Bebek' } },
    { koleksi: 'penjualan', data: { id: 'sk-k1', tanggal: '2026-12-03', jam: '10:00', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 2, totalKg: 10, hargaTotal: 144000, hppTotalSaatJual: 124000 } },
    { koleksi: 'katalogHargaKemasan', data: { id: 'hm-kembang5', merk: 'Kembang', ukuran: 5, hargaPerUnit: 72000 } }]);
  putusSemua(); W = jam('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI);
  var G = gerbangBuku(2026, kini, {}, {}); ok('S gerbang: g1 (diputus) & g6 lolos di kotak ini', G.daftar[0].ok && G.daftar.filter(function (g) { return g.id === 'g6'; })[0].ok, J(G.daftar.filter(function (g) { return !g.ok; })));
  // A7 identitas SEBELUM ritual: tanpa ringkasan, pembaca lintas tahun = angka mesin apa adanya; salinan rumus per hari = mesin
  var kr0 = kreditLintas(infoKreditPelanggan('Pembeli Contoh'), 'Pembeli Contoh'); var lj0 = lajuLintas(hitungLajuPakai()); var org0 = orangRingkas(kini);
  var LH = lajuHarian(tanggalLokalIso(new Date(Date.now() - 14 * 86400000)), '9999-12-31'); var lajuSalin = { kgMerk: {}, unitKemasan: {}, pcsBahan: {} };
  Object.keys(LH).forEach(function (t) { [['kg', 'kgMerk'], ['unit', 'unitKemasan'], ['pcs', 'pcsBahan']].forEach(function (p) { Object.keys(LH[t][p[0]]).forEach(function (k) { lajuSalin[p[1]][k] = (lajuSalin[p[1]][k] || 0) + LH[t][p[0]][k] / 14; }); }); });
  var KH = kreditHarian(tanggalLokalIso(new Date(Date.now() - 89 * 86400000)), '9999-12-31')['pembeli contoh'] || {}; var tKH = Object.keys(KH).reduce(function (a, t) { return a + KH[t]; }, 0);
  ok('A7 identitas sebelum ritual: KR1 & laju lintas tahun = mesin apa adanya; salinan rumus per hari (lajuHarian, kreditHarian) = hitungLajuPakai & infoKreditPelanggan', J(kr0) === J(infoKreditPelanggan('Pembeli Contoh')) && J(lj0) === J(hitungLajuPakai()) && samaLaju(lajuSalin, hitungLajuPakai()) && Math.round(tKH / 3) === kr0.rataBulanan && kr0.batas > 0, J([kr0, tKH]));
  var A = potretSiap(kini); var mo0 = modalTertanam('2026-12-31');
  terapkanKeCache([{ koleksi: 'modalOwner', data: { id: 'uji-bertahap', tipe: 'setor', nominal: 1, tanggal: '2026-12-31', tutupBuku: true, tahunDari: 2099, bertahap: true } }]);
  ok('A4 pembuka modal bertahap tanpa penanda tahunnya TIDAK terlihat mesin (modal tetap) — saringan yang sama dengan koleksi pembuka lain', modalTertanam('2026-12-31') === mo0, J([mo0, modalTertanam('2026-12-31')]));
  terapkanKeCache([{ koleksi: 'modalOwner', hapus: 'uji-bertahap' }]);
  var R = ritualPenuh(2026, W, HPA); ok('S ritual penuh diterima (kunci, semua kiriman, arsip habis)', !R.tolak && arsipBuku(2026).n === 0, R.tolak);
  var B = potretSiap(kini); var PU = periksaUlangBuku(2026);
  ok('S periksa ulang dari mesin: SEMUA baris sama persis (12 + modal owner + upah)', !!PU && PU.semuaSama && PU.baris.length === 14, PU && J(PU.beda));
  var tanda = ambilSemuaBatch().filter(function (x) { return x.tutupBuku && x.penandaBuku; })[0] || { merkList: [] }; var rb = function (m) { return tanda.merkList.filter(function (x) { return x.merk === m; }); };
  ok('A3 baris pembuka membawa tanda buku: indukUkuran (berat 25), digabungKe, bukuAdukan (bukan karungWadah), merkPemasok; buku berstok 0 lahir lagi (0 kg)',
    rb('Bebek 25 kg').some(function (x) { return x.indukUkuran === 'Bebek' && x.beratKarung === 25; }) && rb('Rusa 25 kg').some(function (x) { return x.digabungKe === 'Rusa' && x.indukUkuran === 'Rusa'; })
    && rb('Adukan Kembang 5 kg').length > 0 && rb('Adukan Kembang 5 kg').every(function (x) { return x.bukuAdukan === 'Kembang|5' && !x.karungWadah; }) && rb('Kelas Contoh').every(function (x) { return x.merkPemasok === 'Merek Pemasok Contoh'; })
    && rb('Habis Contoh').length > 0 && rb('Habis Contoh').every(function (x) { return x.totalKg === 0; }), J(tanda.merkList));
  ok('A3 petaUkuran, indukTerpisah, ukuranDigabung, petaBukuWadah sebelum = sesudah ritual', A.ukuran === B.ukuran && A.terpisah === B.terpisah && A.digabung === B.digabung && A.wadah === B.wadah && /Bebek 25 kg/.test(B.terpisah) && !/Rusa 25 kg/.test(B.terpisah), J([A.ukuran, B.ukuran, A.terpisah, B.terpisah, A.digabung, B.digabung]));
  ok('A3 rak Jual sebelum = sesudah (chip 25 kg dari bukunya sendiri, buku & kemasan berstok 0 tetap punya chip habis)', bedaObj(A.chip, B.chip).length === 0 && !!B.chip['karung|Bebek 25 kg|25'] && !B.chip['karung|Bebek|25'] && !!B.chip['karung|Habis Contoh|50'] && !!B.chip['kemasan|Kembang|5|'], J(bedaObj(A.chip, B.chip)));
  var mp = cacheMentah('modal').filter(function (x) { return x.tutupBuku && x.tahunDari === 2026; });
  ok('A4 modal owner menyeberang: satu pembuka setor 33 jt (25 + 10 − 2, kotak) bertanggal 31 Des 00.00; modal 31 Des & hari ini sama; uang per tempat TIDAK berubah (bukan uang masuk)', mp.length === 1 && mp[0].tipe === 'setor' && mp[0].nominal === 33000000 && mp[0].tanggal === '2026-12-31' && mp[0].jam === '00:00' && mp[0].bertahap
    && modalTertanam('2026-12-31') === mo0 && A.modal === B.modal && A.modal === 33000000 && A.kas === B.kas && A.baris.modal === B.baris.modal, J([mp, mo0, A.modal, B.modal, A.kas, B.kas]));
  var ug0 = A.upah.orang.filter(function (o) { return o.nama === 'Gama'; })[0] || {}, ug1 = B.upah.orang.filter(function (o) { return o.nama === 'Gama'; })[0] || {};
  ok('A6 upah yang belum dibayar sama sebelum/sesudah; Gama mulai 1 Des — patokan sistem lama (30 Nov) dibawa berita acara, hari Agu & 20 Nov tidak dibuka lagi', A.upah.jumlah === B.upah.jumlah && A.upah.jumlah > 0 && ug0.mulai === '2026-12-01' && ug1.mulai === '2026-12-01'
    && (acara(2026).upah || []).some(function (o) { return o.nama === 'Gama' && o.lama === '2026-11-30'; }) && mulaiUpah('Gama', '2027-01-05').sumber === 'lama', J([A.upah, B.upah, acara(2026).upah]));
  var kr1 = kreditLintas(infoKreditPelanggan('Pembeli Contoh'), 'Pembeli Contoh');
  ok('A7 KR1 Pembeli Contoh sebelum = sesudah (90 hari menyeberang lewat ringkasan; mesin sendiri tinggal Januari)', kr1.batas === kr0.batas && kr1.rataBulanan === kr0.rataBulanan && !!kr1.lintasTahun && infoKreditPelanggan('Pembeli Contoh').batas < kr0.batas
    && !alasanKunciKredit({ pelanggan: 'Pembeli Contoh', kreditDibuka: false }, 1000), J([kr0, kr1, infoKreditPelanggan('Pembeli Contoh')]));
  ok('A7 laju pakai 14 hari sebelum = sesudah', samaLaju(lj0, lajuLintas(hitungLajuPakai())) && !samaLaju(lj0, hitungLajuPakai()), J([lj0, lajuLintas(hitungLajuPakai())]));
  ok('A7 daftar pelanggan sebelum = sesudah (kunjungan, terakhir, belanja, jam, barang) — yang cuma belanja 2026 tidak hilang', org0 === orangRingkas(kini) && /pembeli lama contoh/.test(orangRingkas(kini)), J([org0, orangRingkas(kini)]));
  // A6b: upah Desember dibayar 5 Jan SESUDAH tutup buku → biayanya ke Januari 2027, bukan biaya 2026 baru
  var UB = susunBayarUpah('Gama', 'tidak', W); var bb = (UB.dokumen || []).filter(function (x) { return x.koleksi === 'biayaBulanan'; });
  ok('A6 bayar upah 5 Jan: biayaBulanan hanya 2027-01 (hari kerja Desember dibukukan ke bulan bayar, rincian tetap 1 Des – 4 Jan); tidak ada biaya 2026 baru', !UB.tolak && bb.length === 1 && bb[0].data.bulan === '2027-01' && /tahun yang sudah ditutup buku/.test(UB.patch.kabar) && bb[0].data.rincianGaji.some(function (r) { return r.dari === '2026-12-01'; }), J(UB.tolak || bb)); });

// ---- A5 · stok minus, kemasan minus, kelebihan bayar pelanggan, kelebihan bayar ke pemasok per 31 Des
coba('S-A5', function () { kotak(3);
  terapkanKeCache([
    { koleksi: 'produksiKemasan', data: { id: 'sm-p1', tanggal: '2026-12-01', jam: '09:00', namaProduk: 'Kemasan Contoh', ukuranKemasan: 5, jumlahUnit: 1, hppPerUnit: 65000, kgDipakai: 5, merkSumber: 'Angsa' } },
    { koleksi: 'penjualan', data: { id: 'sm-k1', tanggal: '2026-12-20', jam: '10:00', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kemasan Contoh', ukuranKemasan: 5, jumlahUnit: 3, totalKg: 15, hargaTotal: 210000, hppTotalSaatJual: 195000 } },
    { koleksi: 'penjualan', data: { id: 'sm-k2', tanggal: '2026-12-20', jam: '11:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'IR64 Apex', totalKg: 500, beratKarungAcuan: 50, jumlahKarung: 10, hargaTotal: 7000000, hppTotalSaatJual: 7000000 } },
    { koleksi: 'piutangMutasi', data: { id: 'sm-pm1', tipe: 'bayar', namaPelanggan: 'Pembeli Lebih Contoh', nominal: 50000, tanggal: '2026-12-21', jam: '10:00', caraBayar: 'Tunai' } },
    { koleksi: 'utangPemasokMutasi', data: { id: 'sm-up1', tipe: 'bayar', pemasok: 'RODA CONTOH', nominal: 25000000, tanggal: '2026-12-22', jam: '10:00' } }]);
  putusSemua(); W = jam('2027-01-05T10:00:00+07:00'); var G = gerbangBuku(2026, new Date(__KINI), {}, {}); var g6 = G.daftar.filter(function (g) { return g.id === 'g6'; })[0]; var teks = (g6.rincian || []).map(function (x) { return x.teks + ' — ' + x.jalan; }).join(' | ');
  ok('A5 g6 MEMBLOKIR dengan kalimat toko per buku/nama & jalan beresnya: beras minus (opname), kemasan minus, kelebihan bayar pelanggan, bayar ke pemasok lebih', !g6.ok && !g6.bisaLewati && /Buku IR64 Apex minus 40 kg/.test(teks) && /Cocokkan/.test(teks) && /Kemasan Contoh 5 kg minus 2 kantong/.test(teks) && /Pembeli Lebih Contoh/.test(teks) && /Bayar ke RODA CONTOH lebih Rp5\.000\.000/.test(teks) && /catat bon/.test(teks), teks);
  ok('A5 susunKunci menolak (pintu masuk)', /Tidak ada stok minus/.test(susunKunci(2026, D, W).tolak || ''), susunKunci(2026, D, W).tolak);
  var SB = barisTahun(2026); var BD = bandingBuku(SB, sesudahDariPembuka(pembukaBuku(2026, W), SB)); var beda = BD.beda.map(function (b) { return b.id; });
  ok('A5 baris pembanding tidak lagi buta minus: beras, kemasan, piutang (dibayar LEBIH), utang pemasok (dibayar LEBIH) berbeda sebelum/sesudah', ['beras', 'kemasan', 'piutang', 'utangP'].every(function (k) { return beda.indexOf(k) >= 0; }) && SB.utang[0].n === -5000000 && /dibayar LEBIH/.test(SB.utang[0].nama) && /MINUS/.test(SB.harta[1].nama), J([beda, SB.utang[0], SB.harta[1]])); });

// ---- A8 · perkiraan kuota Firestore & jam reset
coba('S-A8', function () { kotak(40); W = jam('2026-12-20T10:00:00+07:00'); var Q = perkiraanKuota(2026, new Date(__KINI));
  ok('A8 perkiraan untuk 1 Jan 2027 sesudah reset 15.00 WIB: tulis ≥ 2×saldo pembuka + arsip, hapus = arsip, baca ≥ satu muat penuh; batal ≥ 2×arsip baca; kalimat saran jam, Console', Q.rencana === '2027-01-01' && Q.jamReset === 15 && Q.ritual.tulis >= 2 * Q.nPembuka + Q.nArsip && Q.ritual.hapus === Q.nArsip && Q.ritual.baca >= Q.muat && Q.batal.baca >= 2 * Q.nArsip
    && /15\.00 WIB/.test(Q.kalimat[0]) && /Muat dalam kuota/.test(Q.kalimat[1]) && /Console/.test(Q.kalimat[3]) && !Q.lewat && !Q.mepet, J(Q));
  // sanggahan paket A: hari pergantian — tengah malam Minggu ke-2 Maret masih PST (15.00 WIB), tengah malam Minggu ke-1 November masih PDT (14.00 WIB)
  var JR = [['2027-07-01', 14], ['2027-01-01', 15], ['2026-10-31', 14], ['2026-11-01', 14], ['2026-11-02', 15], ['2027-03-13', 15], ['2027-03-14', 15], ['2027-03-15', 14], ['2027-11-07', 14], ['2027-11-08', 15]];
  var jr = JR.map(function (x) { return jamResetKuota(x[0]); }); var I0 = Intl.DateTimeFormat; var jr0;
  try { Intl.DateTimeFormat = function () { throw new RangeError('tanpa data zona (uji)'); }; jr0 = JR.map(function (x) { return jamResetKuota(x[0]); }); } finally { Intl.DateTimeFormat = I0; }
  ok('A8 jam reset kuota dari zona America/Los_Angeles: 14.00 WIB selama musim panas AS, 15.00 WIB selainnya — juga di hari pergantian (8 Mar/14 Mar Minggu ke-2 → 15.00, 1 Nov/7 Nov Minggu ke-1 → 14.00)',
    JR.every(function (x, i) { return jr[i] === x[1]; }), J(JR.map(function (x, i) { return x[0] + ' ' + jr[i] + '/' + x[1]; })));
  ok('A8 jam reset kuota di peramban tanpa data zona (aturan tanggal): sama persis, juga di hari pergantian', JR.every(function (x, i) { return jr0[i] === x[1]; }), J(JR.map(function (x, i) { return x[0] + ' ' + jr0[i] + '/' + x[1]; })));
  var tadi = BATAS_SPARK.tulis; BATAS_SPARK.tulis = Math.max(1, Math.floor(Q.ritual.tulis / 2)); var Q2 = perkiraanKuota(2026, new Date(Date.parse('2027-01-02T16:00:00+07:00')));
  BATAS_SPARK.tulis = Math.ceil(Q.ritual.tulis / 0.9); var Q3 = perkiraanKuota(2026, new Date(Date.parse('2027-01-03T16:00:00+07:00'))); BATAS_SPARK.tulis = tadi;
  ok('A8 peringatan: lewat batas → "TIDAK MUAT … DOBEL"; > 80 % → "MEPET"', Q2.lewat && /TIDAK MUAT/.test(Q2.kalimat[1]) && /DOBEL/.test(Q2.kalimat[1]) && Q3.mepet && !Q3.lewat && /MEPET/.test(Q3.kalimat[1]), J([Q2.kalimat, Q3.kalimat])); });

// ---- A9 · catatan bertanggal 2026 yang mendarat sesudah penanda (karcis HP penjaga yang tertahan offline)
coba('S-A9', function () { kotak(5); W = jam('2027-01-02T16:00:00+07:00'); var R = susunKunci(2026, D, W, HPA); R.kiriman.forEach(kirim); var daftar = arsipBuku(2026).daftar;
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'susul1', tanggal: '2026-12-31', jam: '20:30', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]);
  arsipkanDokumen(2026, daftar); var PA = susunPeriksaArsip(2026, W, HPA, true); if (PA.dokumen) terapkanKeCache(PA.dokumen);
  var S = susulanBuku(); var KM = kemajuanBuku();
  ok('A9 karcis yang masuk di tengah arsip: hasil periksa tetap dibekukan (susulan 1); pita fase selesaikan (BUKAN "lanjutkan arsip" yang akan menyapunya); kalimat & jalan beresnya', !!PA.dokumen && PA.dokumen[0].data.susulan === 1 && !!S && S.n === 1 && S.rupiah === 700000 && !!KM && KM.fase === 'selesaikan' && /SESUDAH tutup buku 2026/.test(KM.teks) && /Jangan dihapus/.test(S.jalan) && /LEBIH/.test(S.jalan), J([PA.dokumen, S && S.teks, KM]));
  var SL = susunSelesai(2026, 'cadangan-sesudah.json', W, false, HPA); ok('A9 selesai butuh ketukan kedua yang menyebut susulan', !!SL.perluYakin && /SESUDAH tutup buku 2026/.test(SL.tolak || ''), J(SL));
  SL = susunSelesai(2026, 'cadangan-sesudah.json', W, true, HPA); if (!SL.tolak) kirim(SL);
  ok('A9 berita acara selesai mencatat susulan; Beranda menyebutnya; catatannya tetap di buku hidup', acara(2026).status === 'selesai' && acara(2026).susulan && acara(2026).susulan.n === 1 && bkPerhatian(new Date(__KINI)).some(function (x) { return /SESUDAH tutup buku 2026/.test(x.teks); }) && ambilPenjualanSemua().some(function (p) { return p.id === 'susul1'; }), J([SL.tolak, acara(2026).susulan]));
  var C = susunCatatSusulan(2026, W); if (!C.tolak) terapkanKeCache(C.dokumen);
  ok('A9 "sudah dicatat": pita hilang, catatannya TIDAK dihapus; karcis susulan berikutnya muncul lagi', !C.tolak && susulanBuku() === null && ambilPenjualanSemua().some(function (p) { return p.id === 'susul1'; })
    && (terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'susul2', tanggal: '2026-12-30', jam: '19:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }]), !!susulanBuku() && susulanBuku().n === 1), J(C.tolak)); });

// ---- A9 (sanggahan paket A) · pesanan Desember yang BELUM tuntas saat ritual sengaja tidak diarsip (tbDaftarKoleksi) — dibayar Januari BUKAN susulan;
// pengeluaran yang telat masuk = susulan dengan kalimat pengeluaran (uang KURANG, biaya kurang → laba terlihat lebih besar), bukan kalimat nota
coba('S-A9b', function () { kotak(5);
  var ps = { id: 'ps-des', tanggal: '2026-12-20', jam: '10:00', namaPelanggan: 'Pemesan Contoh', isi: '2 karung contoh', alamat: '', nilaiPerkiraan: 1300000, status: 'dipesan', trxIdJual: null, riwayatStatus: [{ status: 'dipesan', pada: '2026-12-20T03:00:00.000Z' }] };
  terapkanKeCache([{ koleksi: 'pesanan', data: ps }]); W = jam('2027-01-02T16:00:00+07:00'); var R = ritualPenuh(2026, W, HPA); var PA = dokDiCache('pengaturan', 'periksaArsip2026');
  ok('A9 pesanan 20 Des belum tuntas saat ritual: tidak diarsip, dicatat TERTINGGAL di hasil periksa; bukan susulan', !R.tolak && ambilPesanan().some(function (p) { return p.id === 'ps-des'; }) && !!PA && (PA.tertinggal || []).indexOf('pesanan|ps-des') >= 0 && susulanBuku() === null, J([R.tolak, PA && PA.tertinggal]));
  W = jam('2027-01-06T10:00:00+07:00');
  terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'ps-jual', tanggal: '2027-01-06', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 100, beratKarungAcuan: 50, jumlahKarung: 2, hargaTotal: 1300000, hppTotalSaatJual: 1200000, namaPelanggan: 'Pemesan Contoh', trxId: 't-ps' } },
    { koleksi: 'pesanan', data: Object.assign({}, ps, { status: 'dibayar', trxIdJual: 't-ps', riwayatStatus: ps.riwayatStatus.concat([{ status: 'dibayar', pada: '2027-01-06T03:00:00.000Z' }]) }) }]);
  var KM = kemajuanBuku();
  ok('A9 pesanan itu DIBAYAR 6 Jan (masuk daftar arsip 2026): BUKAN susulan — pita selesaikan tanpa AWAS susulan, Beranda diam', arsipBuku(2026).n === 1 && susulanBuku() === null && !!KM && KM.fase === 'selesaikan' && !/SESUDAH tutup buku/.test(KM.teks) && !bkPerhatian(new Date(__KINI)).some(function (x) { return /SESUDAH tutup buku/.test(x.teks); }), J([arsipBuku(2026).n, susulanBuku() && susulanBuku().teks, KM]));
  var SL = susunSelesai(2026, 'cadangan-sesudah.json', W, false, HPA);
  ok('A9 selesai tanpa ketukan kedua (tidak ada susulan); berita acara mencatat pesanan yang tertinggal', !SL.tolak && !SL.perluYakin && !SL.dokumen[0].data.susulan && (SL.dokumen[0].data.tertinggal || []).indexOf('pesanan|ps-des') >= 0, J(SL.tolak || SL.dokumen[0].data.tertinggal));
  if (!SL.tolak) kirim(SL); terapkanKeCache([{ koleksi: 'pengaturan', hapus: 'periksaArsip2026' }]);
  ok('A9 sesudah selesai, tanpa hasil periksa (mis. tidak tersimpan): pesanan itu tetap bukan susulan — berita acara yang menahannya', acara(2026).status === 'selesai' && susulanBuku() === null, J(susulanBuku() && susulanBuku().teks));
  terapkanKeCache([{ koleksi: 'pengeluaranHarian', data: { id: 'kel-susul', tanggal: '2026-12-30', jam: '18:00', kategori: 'toko', untuk: 'toko', keterangan: 'listrik contoh', nominal: 250000, dari: 'laci' } }]);
  var S = susulanBuku();
  ok('A9 pengeluaran 30 Des yang telat masuk: susulan dengan kalimat PENGELUARAN — uang KURANG, biaya 2026 kurang, laba terlihat lebih besar; tidak menyebut LEBIH / omzet',
    !!S && S.n === 1 && S.rupiahKeluar === 250000 && S.biaya === 250000 && S.rupiah === 0 && /pengeluaran Rp250\.000/.test(S.teks) && /catatan HP/.test(S.teks) && /KURANG/.test(S.jalan) && /Biaya 2026 di berita acara kurang Rp250\.000/.test(S.jalan) && /laba 2026 terlihat lebih besar/.test(S.jalan) && !/LEBIH/.test(S.jalan) && !/Omzet/.test(S.jalan) && /pajak 2026/.test(S.jalan), J(S && [S.teks, S.jalan])); });

// ---- A4 (sanggahan paket A) · saldo pembuka modal owner bertanggal 31 Des BUKAN gerakan uang 2026: bukan ambil pribadi Desember, bukan setoran/penarikan di buku
// owner (juga bukan bukti setoran), tidak tampil di buku kas 31 Des. Modal MINUS (tarik lebih dari setor) → pembuka 'tarik'
coba('S-A4b', function () { kotak(3);
  terapkanKeCache([{ koleksi: 'modalOwner', data: { id: 'ma-t1', tanggal: '2026-12-16', jam: '09:00', tipe: 'tarik', nominal: 40000000, catatan: 'tarik modal contoh' } }]);
  putusSemua(); W = jam('2027-01-05T10:00:00+07:00'); var pr0 = priveRentang('2026-12-01', '2026-12-31').tarik; var mo0 = modalTertanam('2026-12-31');
  var R = ritualPenuh(2026, W, HPA); var mp = cacheMentah('modal').filter(function (x) { return x.tutupBuku && x.tahunDari === 2026; })[0] || null;
  ok('A4 modal minus menyeberang: satu pembuka TARIK sebesar minusnya, bertanggal 31 Des; modal sebelum = sesudah', !R.tolak && !!mp && mp.tipe === 'tarik' && mp.nominal === -mo0 && mo0 < 0 && mp.tanggal === '2026-12-31' && modalTertanam('2026-12-31') === mo0, J([R.tolak, mp, mo0]));
  var pr1 = priveRentang('2026-12-01', '2026-12-31');
  ok('A4 pembuka TARIK bukan ambil pribadi Desember (dulu terhitung tarik modal 31 Des)', pr0 === 40000000 && pr1.tarik === 0 && pr1.total === 0, J([pr0, pr1]));
  var BO = bukuOwner(300); var bo = BO.filter(function (r) { return mp && r.id === String(mp.id); })[0] || null;
  ok('A4 buku owner: pembuka = "Modal owner dibawa dari tahun lalu (minus)" tanpa uang bergerak (arah 0), bukan setoran/penarikan; saldo mundurnya tetap benar; tidak ada di pilihan bukti setoran modal',
    !!bo && /^Modal owner dibawa dari tahun lalu \(minus\)$/.test(bo.judul) && bo.arah === 0 && /tidak ada uang bergerak/.test(bo.ket) && BO.filter(function (r) { return r.ubah === 'modal' && r.arah === 1; }).every(function (r) { return r.id !== bo.id; })
    && /modal owner jadi −?Rp/.test(bo.s), J([bo, BO.slice(0, 3)]));
  var RH = rekapHari('2026-12-31');
  ok('A4 buku kas 31 Des: baris pembuka modal tidak tampil (bukan gerakan uang)', !!mp && !RH.buku.some(function (r) { return String(r.id) === String(mp.id); }) && daftarGerakanKas().some(function (r) { return String(r.id) === String(mp.id); }), J(RH.buku)); });

// ---- era tutup buku dihitung di SATU tempat (sanggahan paket A): cap era berkas cadangan (ssEraTutupBuku) = toko.js eraBuku — juga pembuka modal owner
coba('S-ERA', function () { kotak(3);
  terapkanKeCache([{ koleksi: 'modalOwner', data: { id: 'era-modal', tanggal: '2030-12-31', jam: '00:00', tipe: 'setor', nominal: 1000, tutupBuku: true, tahunDari: 2030 } }]);
  ok('era satu tempat: cap era cadangan = eraBuku, juga bila tahun itu hanya punya pembuka modal owner', eraBuku() === 2030 && ssEraTutupBuku() === 2030 && ssBerkasCadangan(new Date(__KINI)).isi.eraTutupBuku === 2030, J([eraBuku(), ssEraTutupBuku()]));
  terapkanKeCache([{ koleksi: 'modalOwner', hapus: 'era-modal' }]); });

// ---- A2 · Beranda: tutup buku tahun lalu yang belum selesai (owner) — kunci bulan menunggu
coba('S-A2', function () { kotak(3); jam('2027-01-03T10:00:00+07:00');
  ok('A2 Beranda 3 Jan 2027 tanpa tutup buku: satu baris "Tutup buku 2026 belum dikerjakan — kunci bulan 2027 menunggu"', bkPerhatian(new Date(__KINI)).some(function (x) { return /Tutup buku 2026 belum dikerjakan/.test(x.teks) && /kunci bulan 2027 menunggu/.test(x.teks); }), J(bkPerhatian(new Date(__KINI)))); });
"""

ASAP = r"""
KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var salah = []; var n27 = 90000; var W = { tanggal: '2027-01-05', jam: '10:00', kini: new Date(__KINI).toISOString(), idUnik: function () { n27 += 1; return n27; } };
// siap 2027 (A1, sanggahan paket A): hari berjualan tanpa tutup hari diberi putusan TIRUAN (uji_kunci_periode.PUTUSAN_TIRUAN) — ritualnya tetap diuji
var PT = putusanTiruan(2026, W); cekTiruan(PT, salah);
var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'uji asap', langkah: {} }, W); var out = { tolak: R.tolak || '', putusanTiruan: PT.n };
if (!R.tolak) { out.kiriman = R.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); }); out.pembuka = R.acara.nPembuka; out.arsip = R.arsip.length;
  if (out.kiriman.some(function (g) { return g > 18; })) salah.push('ada kiriman pembuka > 18');
  R.kiriman.forEach(function (k) { terapkanKeCache(k.dokumen); });
  var B = susunBatal(2026, [], W); out.batal = B.tolak ? B.tolak : B.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus); });
  if (B.tolak || out.batal.some(function (g) { return g > 18; })) salah.push('batal data toko > 18 atau ditolak');
} else salah.push('ditolak: ' + R.tolak);
out.salah = salah; print(JSON.stringify(out));
"""


ASAP_2027 = r"""
// ==================== ASAP SIAP 2027 — ritual tutup buku 2026 PENUH atas CADANGAN LOKAL (tidak di-commit; dilewati di CI) ====================
// Putusan per tanggal = TIRUAN (bukan putusan owner). Tidak ada yang ditulis ke mana pun: semua di memori jsc.
var J = JSON.stringify; var salah = []; var nId = 700000;
function muatCad() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' }; }
function Wk(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: iso.slice(11, 16), kini: new Date(iso).toISOString(), idUnik: function () { nId += 1; return 'asap' + nId; } }; }
var LA = { idPerangkat: 'asap-mac', namaPerangkat: 'Mac asap', antre: [], menunggu: 0, offline: false };
function kirimA(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) { salah.push('penjaga pusat menolak kiriman: ' + j.pesan); return false; }
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); return true; }
function potretA(kini) { var hari = hariIniIso(kini); var B = barisBuku(hari, hari); var baris = {}; B.harta.concat(B.utang, B.lain).forEach(function (b) { baris[b.id] = b.n; });
  var s0 = keadaanAwal(); sinkronKeranjang(s0); var rak = susunRak(s0); var chip = {}; ['karung', 'kemasan', 'literan', 'repack'].forEach(function (j) { rak[j].forEach(function (c) { chip[j + '|' + c.kunci + '|' + (c.berat || '')] = c.nama + '|' + c.ukuran + '|' + c.harga + '|' + Math.round((c.sisa || 0) * 1000) / 1000; }); });
  var kredit = {}; ambilPelangganCatatan().forEach(function (c) { var nm = c.nama || c.id; var i = kreditLintas(infoKreditPelanggan(nm), nm); if (i && i.ada) kredit[kunciPelanggan(nm)] = i.terdaftar + '|' + i.batas; });
  var orang = {}; semuaOrang(kini).forEach(function (o) { orang[o.kunci] = o.kunjungan + '|' + o.terakhir + '|' + Math.round(o.total) + '|' + o.nota + '|' + o.selang + '|' + o.jam + '|' + o.pola.join('+'); });
  var stok = {}; var SK = hitungStokKarungPerMerk(); Object.keys(SK).forEach(function (m) { stok[m] = Math.round(SK[m].sisaKg * 100) / 100; });
  var kem = {}; var SM = hitungStokKemasan(); Object.keys(SM).forEach(function (k) { if (SM[k].sisaUnit > 0) kem[k] = SM[k].sisaUnit; });
  return { baris: baris, chip: chip, ukuran: J(petaUkuran()), terpisah: J(indukTerpisah()), digabung: J(ukuranDigabung()), wadah: J(petaBukuWadah()), stokWadah: J(petaStokWadah()), modal: Math.round(modalTertanam()),
    kredit: kredit, laju: lajuLintas(hitungLajuPakai()), orang: orang, stok: stok, kem: kem, upah: upahPada(hari).jumlah, nMerek: Object.keys(SK).length }; }
function bedaA(a, b) { var out = []; Object.keys(a).concat(Object.keys(b).filter(function (k) { return !(k in a); })).forEach(function (k) { if (a[k] !== b[k]) out.push(k); }); return out; }
function bedaLaju(a, b) { var out = []; ['kgMerk', 'unitKemasan', 'pcsBahan'].forEach(function (g) { var x = a[g] || {}, y = b[g] || {}; Object.keys(x).concat(Object.keys(y)).forEach(function (k) { if (Math.abs((x[k] || 0) - (y[k] || 0)) > 1e-6) out.push(g + '|' + k); }); }); return out; }
function bedaStok(a, b) { var out = []; Object.keys(a).concat(Object.keys(b)).forEach(function (k) { if (Math.abs((a[k] || 0) - (b[k] || 0)) > 0.011) out.push(k); }); return out.filter(function (x, i) { return out.indexOf(x) === i; }); }
function ritualA(isoJam, ujiBatal) {
  muatCad(); var w = Wk(isoJam); var kini = new Date(__KINI); var r = { jam: isoJam }; var tanda = isoJam.slice(0, 10) + ': ';
  var G0 = gerbangBuku(2026, kini, LA, { g3: true }); r.hariTanpaTutup = G0.hari.length; r.belumDiputus = G0.belumPutus.length;
  var isi = {}; G0.belumPutus.forEach(function (t) { isi[t] = 'asap: putusan TIRUAN, bukan putusan owner'; }); var P = G0.belumPutus.length ? susunPutusanHari(isi, w) : { dokumen: [] };
  if (P.tolak) salah.push(tanda + 'putusan tiruan ditolak: ' + P.tolak); else terapkanKeCache(P.dokumen);
  var G = gerbangBuku(2026, kini, LA, { g3: true }); r.gerbang = G.daftar.map(function (g) { return g.id + (g.ok ? ' ok' : ' BELUM: ' + g.ket.slice(0, 160)); });
  ['g1', 'g6'].forEach(function (id) { var g = G.daftar.filter(function (x) { return x.id === id; })[0]; if (!g.ok) salah.push(tanda + id + ' belum lolos: ' + g.ket.slice(0, 200)); });
  var Q = perkiraanKuota(2026, kini); r.kuota = { rencana: Q.rencana, jam: Q.jamReset, ritual: Q.ritual, batal: Q.batal, muat: Q.muat, lewat: Q.lewat, mepet: Q.mepet };
  var A = potretA(kini); var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'asap', langkah: {} }, w, LA);
  if (R.tolak) { salah.push(tanda + 'kunci ditolak: ' + R.tolak.slice(0, 300)); return r; }
  r.kiriman = R.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); }); r.pembuka = R.acara.nPembuka; r.arsip = R.arsip.length; r.banding = R.banding.ringkas;
  if (!R.banding.semuaSama) salah.push(tanda + 'banding sebelum/sesudah: ' + R.banding.ringkas);
  if (r.kiriman.some(function (g) { return g > 18; })) salah.push(tanda + 'ada kiriman > 18 pemeriksaan');
  R.kiriman.forEach(kirimA); arsipkanDokumen(2026, arsipBuku(2026).daftar); var PA = susunPeriksaArsip(2026, w, LA, true); if (PA.dokumen) terapkanKeCache(PA.dokumen);
  var PU = periksaUlangBuku(2026); r.periksaUlang = PU ? PU.ringkas : 'tidak bisa'; if (!PU || !PU.semuaSama) salah.push(tanda + 'periksa ulang: ' + (PU ? PU.ringkas : 'tidak bisa'));
  var B = potretA(kini); var c = {};
  c.baris = bedaA(A.baris, B.baris); c.chip = bedaA(A.chip, B.chip); c.kredit = bedaA(A.kredit, B.kredit); c.orang = bedaA(A.orang, B.orang); c.laju = bedaLaju(A.laju, B.laju); c.stok = bedaStok(A.stok, B.stok); c.kem = bedaStok(A.kem, B.kem);
  ['ukuran', 'terpisah', 'digabung', 'stokWadah', 'modal', 'upah'].forEach(function (k) { if (A[k] !== B[k]) c[k] = [A[k], B[k]]; }); var wa = JSON.parse(A.wadah), wb = JSON.parse(B.wadah); var dw = Object.keys(wa).concat(Object.keys(wb)).filter(function (k) { return J(wa[k]) !== J(wb[k]); }).map(function (k) { return k + ' : ' + J(wa[k]) + ' → ' + J(wb[k]); }); if (dw.length) c.wadah = dw;
  Object.keys(c).forEach(function (k) { if (Array.isArray(c[k]) ? c[k].length : c[k] !== undefined) salah.push(tanda + 'BEDA sebelum/sesudah · ' + k + ': ' + J(c[k]).slice(0, 400)); });
  r.dibandingkan = { baris: Object.keys(A.baris).length, chip: Object.keys(A.chip).length, kreditTerdaftar: Object.keys(A.kredit).length, kreditBerbatas: Object.keys(A.kredit).filter(function (k) { return Number(A.kredit[k].split('|')[1]) > 0; }).length,
    orang: Object.keys(A.orang).length, buku: Object.keys(A.stok).length, kemasanBerstok: Object.keys(A.kem).length, buku25: JSON.parse(A.ukuran) ? Object.keys(JSON.parse(A.ukuran)).length : 0 };
  r.kemajuan = kemajuanBuku() ? kemajuanBuku().fase : null; r.susulan = susulanBuku(2026) ? susulanBuku(2026).n : 0;
  if (ujiBatal) {
    var BT = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }; }), w, LA);
    if (BT.tolak) salah.push(tanda + 'batal ditolak: ' + BT.tolak); else { r.batalKiriman = BT.kiriman.map(function (k) { return butuhGet(k.dokumen, k.hapus || []); }); BT.kiriman.forEach(kirimA); pulihkanArsip(2026, BT.pulih); kirimA({ dokumen: [BT.akhir] });
      if (r.batalKiriman.some(function (g) { return g > 18; })) salah.push(tanda + 'batal: kiriman > 18');
      var C = potretA(kini); var bb = bedaA(A.baris, C.baris).concat(bedaStok(A.stok, C.stok)); if (bb.length || eraBuku() !== null) salah.push(tanda + 'sesudah BATAL tidak kembali persis: ' + J(bb).slice(0, 300)); r.batal = bb.length ? 'BEDA' : 'kembali persis'; }
  } else {
    var SL = susunSelesai(2026, 'asap-sesudah.json', w, false, LA); if (SL.tolak) salah.push(tanda + 'selesai ditolak: ' + SL.tolak.slice(0, 300)); else kirimA(SL);
    r.selesai = acara(2026) ? acara(2026).status : null;
    Wk('2027-02-05T10:00:00+07:00'); var DP = kpDaftarPeriksa('2027-01', new Date(__KINI), { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {} });
    var tb = DP.butir.filter(function (b) { return b.id === 'tutupBukuLalu'; })[0]; r.kunciJanuari = tb ? (tb.ok ? 'tutup buku 2026 selesai — butir beres' : tb.ket) : 'butir tidak ada'; if (!tb || !tb.ok) salah.push(tanda + 'butir kunci Januari belum beres sesudah selesai');
  }
  return r;
}
function acara(tahun) { return ambilTutupBukuAcara().filter(function (a) { return Number(a.tahun) === tahun; })[0] || null; }
var hasil = [ritualA('2027-01-01T15:10:00+07:00', false), ritualA('2027-01-05T10:00:00+07:00', false), ritualA('2027-01-05T10:00:00+07:00', true)];
print(JSON.stringify({ hasil: hasil, salah: salah }));
"""


def asap_2027(js, berkas):
    """Siap 2027: ritual penuh atas cadangan LOKAL (owner: tidak di-commit). Hasilnya hanya ke layar terminal; kosong `salah` = lulus."""
    a, e = jalan(JAM + js + '\nvar CAD = ' + open(berkas, encoding='utf-8').read() + ';\n' + ASAP_2027)
    if a is None: return None, ['ASAP SIAP 2027 JATUH: ' + e]
    return a, a['salah']


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


def batal_uang(teks=None):
    """TRV6-EKOR-1: fungsi jalankanBatal APA ADANYA dari uang.js (teks = isi uang.js; bawaan dibaca dari berkasnya), dibungkus buatBatalUang(A) supaya
    set / lokal / waktu / BK / tulisDokumen / pulihkanArsip / bacaArsipTahun / arsipkanDokumen-nya diganti kotak pasir (ALAT_EK di SKENARIO)."""
    u = teks if teks is not None else open(os.path.join(bundel_baru.AKAR, 'baru/js/layar/uang.js'), encoding='utf-8').read()
    a = u.index('  async function jalankanBatal(tahun, arsipAda) {'); b = u.index('\n  const bandingB = ', a)
    return ('function buatBatalUang(A) { var set = A.set, lokal = A.lokal, waktu = A.waktu, BK = A.BK, bacaArsipTahun = A.bacaArsipTahun, pulihkanArsip = A.pulihkanArsip,'
            ' tulisDokumen = A.tulisDokumen, arsipkanDokumen = A.arsipkanDokumen, setelTitik = A.setelTitik, LANGKAH_KOSONG = A.LANGKAH_KOSONG;\n' + u[a:b] + '\n  return jalankanBatal; }\n')


def utama(js, cek=None, uang=None):
    cek = cek_tiap_potongan() if cek is None else cek
    h, e = jalan(JAM + js + '\n' + batal_uang(uang) + '\nvar UANG_CEK_TIAP_POTONGAN = ' + ('true' if cek else 'false') + ';\nvar KOTAK = ' + json.dumps(uji_uang_baru.KOTAK) + ';\n' + SKENARIO.replace('__SIAP2027__', SIAP2027))
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


# TRV6-EKOR-1: ekor pembatalan uang.js sesudah tambalan (BARU) dan sebelumnya (LAMA) — kontrol "bentuk lama" memasang LAMA di tempat BARU
EKOR_BARU = '\n'.join([
    "    let henti = '', potongTadi = []; const cekEkor = () => { henti = BK.pulihBerhentiBuku(tahun, lokal(), r.percobaan); if (henti) throw new Error(henti); };",
    "    const kembalikan = (daftar) => { let tadi = 0; return pulihkanArsip(tahun, daftar, (sudah, total) => { set({ progres: { sudah, total, satuan: 'dokumen dikembalikan dari arsip' } }); potongTadi = daftar.slice(tadi, sudah); tadi = sudah; cekEkor(); potongTadi = []; }); };",
    "    try { cekEkor(); await kembalikan(r.pulih); cekEkor(); const sisaA = await bacaArsipTahun(tahun); cekEkor(); if (sisaA.length) await kembalikan(sisaA); cekEkor(); } catch (e) {",
    "      const ulang = henti ? BK.pulihBalikBuku(tahun, potongTadi, r.percobaan) : []; if (ulang.length) { try { await arsipkanDokumen(tahun, ulang); } catch (e2) { console.error(e2); } }",
    "      set({ sibuk: false, progres: null, kabar: henti || 'Pengembalian terhenti: ' + (e && e.message ? e.message : e) + ' — ketuk \"Lanjutkan\" untuk meneruskan pembatalan', kabarAwas: true }); return false; }"])
EKOR_LAMA = '\n'.join([
    "    const balik = (sudah, total) => set({ progres: { sudah, total, satuan: 'dokumen dikembalikan dari arsip' } });",
    "    try { await pulihkanArsip(tahun, r.pulih, balik); const sisaA = await bacaArsipTahun(tahun); if (sisaA.length) await pulihkanArsip(tahun, sisaA, balik); } catch (e) { set({ sibuk: false, progres: null, kabar: 'Pengembalian terhenti: ' + (e && e.message ? e.message : e) + ' — ketuk \"Lanjutkan\" untuk meneruskan pembatalan', kabarAwas: true }); return false; }"])

STATIS = [
    # ---- siap 2027 (owner 7 Okt, paket A)
    ('siap 2027 A1 · putusan per tanggal disimpan dari layar & kunci bulan memakai putusan tersimpan', ["bkPutusSimpan: async () => { await tulis(BK.susunPutusanHari(st().bkPutus, waktu())); },", "const putusanKunci = (s) => Object.assign({}, BK.putusanHari(), s.kpPutus);", "putusanHari: putusanKunci(s), centang: s.kpCentang", "${g.id === 'g1' && g.hari && g.hari.length ? putusanG1(s, g) : ''}"]),
    ('siap 2027 · pita LATIHAN jujur: ritualnya tidak menulis apa pun, hanya "Simpan putusan" yang tersimpan sungguhan', ['hanya "Simpan putusan" per tanggal di langkah 1 yang tersimpan sungguhan']),
    ('siap 2027 · kartu Kunci bulan: putusan tersimpan jadi titik awal (ketukan pada pilihan aktif tidak menghapus alasannya)', ["const aktif = putusanKunci(st())[t];", "if (aktif && aktif.jenis === jenis) { if (!p[t]) return; delete p[t]; } else p[t] = { jenis, alasan: (aktif || {}).alasan || '' };"]),
    ('siap 2027 A5 · rincian g6 (buku/nama & jalan beres) tampil di langkah 1', ["${g.id === 'g6' && g.rincian && g.rincian.length ?", "<b>${x.teks}</b> — ${x.jalan}"]),
    ('siap 2027 A8 · perkiraan kuota tampil di langkah 1 (tulis/hapus/baca vs batas Spark, saran jam, Batalkan)', ["${kuotaBuku(T)}", "Q = BK.perkiraanKuota(T.tahun, kini());", "baris('Kalau dibatalkan sesudah arsip', Q.B)"]),
    ('siap 2027 A9 · arsip yang selesai menandai sisanya SUSULAN; pita susulan & "sudah dicatat"', ["const PA = BK.susunPeriksaArsip(tahun, waktu(), lokal(), true);", "const KM = BK.kemajuanBuku(); const SU = BK.susulanBuku();", 'data-aksi="bkSusulanCatat"', "await tulis(BK.susunCatatSusulan(S.tahun, waktu()));"]),
    ('siap 2027 A4/A6 · baris modal & upah (ikut dibandingkan, tidak masuk jumlah) tampil di lembar K6', ["${B.baris.slice(SB.harta.length + SB.utang.length).map((b) =>", "B.baris.slice(SB.harta.length, SB.harta.length + SB.utang.length)"]),
    ('siap 2027 A2/A9 · Beranda membaca tutup buku (owner)', ["perhatianPajak(k), perhatianBuku(k), perhatianKunci(k)", "return bkPerhatian(k);"], 'baru/js/layar/ringkasan.js'),
    ('siap 2027 A7 · KR1 di Jual (kunci kredit & kartu pelanggan) memakai lintas tahun', ["const info = kreditLintas(infoKreditPelanggan(nama), nama);", "const i = kreditLintas(infoKreditPelanggan(nama), nama);"], 'baru/js/layar/jual-logika.js'),
    ('siap 2027 A7 · laju pakai lintas tahun di Stok, Beranda, Belanja, Kantong', ["const laju = lajuLintas(hitungLajuPakai());"], 'baru/js/layar/stok-logika.js'),
    ('siap 2027 A7 · laju pakai lintas tahun di Beranda', ["const laju = lajuLintas(hitungLajuPakai());"], 'baru/js/layar/ringkasan-logika.js'),
    ('siap 2027 A7 · laju pakai lintas tahun di Belanja', ["const laju = lajuLintas(hitungLajuPakai()).kgMerk || {};"], 'baru/js/layar/belanja-logika.js'),
    ('siap 2027 A7 · laju pakai lintas tahun di Kantong', ["const laju = lajuLintas(hitungLajuPakai()).pcsBahan || {};"], 'baru/js/layar/stok-kantong-logika.js'),
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
    ('putaran 3 AAL1 (susulan) · pembatalan membaca arsip ulang sekali sebelum berita acara dibatalkan', ["const sisaA = await bacaArsipTahun(tahun); cekEkor(); if (sisaA.length) await kembalikan(sisaA);", "const kembalikan = (daftar) => { let tadi = 0; return pulihkanArsip(tahun, daftar, (sudah, total) =>"]),
    ('TRV6-EKOR-1 · ekor pembatalan: BK.pulihBerhentiBuku sebelum tiap langkah & sesudah SETIAP potongan; potongan yang membuatnya berhenti → BK.pulihBalikBuku → arsipkanDokumen',
     ["const cekEkor = () => { henti = BK.pulihBerhentiBuku(tahun, lokal(), r.percobaan); if (henti) throw new Error(henti); };", "potongTadi = daftar.slice(tadi, sudah); tadi = sudah; cekEkor(); potongTadi = []; });",
      "try { cekEkor(); await kembalikan(r.pulih); cekEkor(); const sisaA = await bacaArsipTahun(tahun); cekEkor(); if (sisaA.length) await kembalikan(sisaA); cekEkor(); } catch (e) {",
      "const ulang = henti ? BK.pulihBalikBuku(tahun, potongTadi, r.percobaan) : []; if (ulang.length) { try { await arsipkanDokumen(tahun, ulang); }", "kabar: henti || 'Pengembalian terhenti: '"]),
    ('putaran 3 UTBU-1 · hasil periksa ulang dibekukan saat arsip habis (ditulis ke berita acara)', ["const PA = BK.susunPeriksaArsip(tahun, waktu(), lokal(), true); if (PA.dokumen) { try { await tulisDokumen(PA.dokumen, [], { tunggu: true }); }", "const PU = PA.PU || {"]),
    ('putaran 3 UTBU-2 · kabar sesudah arsip memakai kalimat periksa ulang yang sama (belum bisa dihitung ≠ TIDAK SAMA)', ["' AWAS: ' + BK.bkKalimatPeriksa(PA.PU) + ' — periksa dulu, jangan diselesaikan.'"]),
    ('putaran 3 AAL3 · Lanjutkan menolak tutup buku yang tidak utuh (fase rusak) — tidak meneruskan arsip', ["if (KM.fase === 'rusak') return set({ kabar: KM.teks, kabarAwas: true });"]),
    ('putaran 3 AAL4 · Lanjutkan & Batalkan hanya dari data server (tanpa internet / salinan perangkat = ditolak)', ["bkLanjut: async () => { if (st().sibuk) return; const sb = BK.bkSambungan(lokal()); if (sb) return set({ kabar: sb, kabarAwas: true });", "bkBatal: async () => { if (st().sibuk) return; const sb = BK.bkSambungan(lokal()); if (sb) return set({ yakinBatalB: null, kabar: sb, kabarAwas: true });"]),
    ('putaran 3 AAL4 · firebase.js menyetor tanda salinan perangkat (fromCache) per koleksi ke toko.js', ["setelDariCache(k.nama, _dariCache[k.nama]);"], 'baru/js/data/firebase.js'),
    ('putaran 3 AAL5 · firebase.js mencatat HAPUS yang menunggu server per kiriman sampai commit selesai', ["setelHapusTertunda(idKiriman, H);", ".finally(() => { setelHapusTertunda(idKiriman, null);"], 'baru/js/data/firebase.js'),
    ('putaran 4 P4-3 · callback progres arsip membaca status sesudah SETIAP potongan, termasuk yang terakhir (bentuk yang disuntik ke kotak pasir)', [UANG_TIAP_POTONGAN]),
    ('putaran 4 P4-5 · lembar K6 sesudah kunci memakai kalimat pita (bkKalimatPeriksa), bukan ringkasan banding "TIDAK SAMA"', ["${s.sesudahLive ? (BK.bkKalimatPeriksa(s.sesudahLive.baris ? s.sesudahLive : null) || B.ringkas) + ' (diperiksa ulang dari mesin sesudah kunci)' : B.ringkas}"]),
    ('putaran 4 P4-1 · Kunci mencatat perangkat ini sebagai pemegang (lokal() ke susunKunci)', ["arsipNama: s.arsipNama }, waktu(), lokal()); if (r.tolak) return set({ siapKunci: false,"]),
    ('putaran 4 P4-1 · Lanjutkan & Batalkan hanya dari pemegang — dicek sebelum arsip dibaca; susun* menerima lokal()', ["const bp = BK.bkBukanPemegang(KM.tahun, lokal()); if (bp) return set({ kabar: bp, kabarAwas: true });", "const bp = BK.bkBukanPemegang(tahun, lokal()); if (bp) return set({ yakinBatalB: null, kabar: bp, kabarAwas: true });", "const Lj = BK.lanjutBuku(KM.tahun, lokal());", "const r = BK.susunBatal(tahun, arsip, waktu(), lokal());"]),
    ('putaran 4 P4-1 · kiriman berikutnya (tutup buku & pembatalan) berhenti bila perangkat ini bukan lagi pemegangnya', ["const bpK = BK.bkBukanPemegang(tahun, lokal()); if (bpK) { set({ sibuk: false, progres: null, kabar: bpK, kabarAwas: true }); return false; }\n      let h = null; try { h = await tulisDokumen(k.dokumen, k.hapus || [], { tunggu: true });"]),
    ('putaran 4 P4-2 · tombol ambil alih di pita perangkat lain; dua ketukan & syaratnya dijaga BK.susunAmbilAlih', ["data-aksi=\"bkAmbilAlih\">${KM && s.yakinAmbilB === KM.tahun ? 'ketuk sekali lagi · ambil alih' : 'ambil alih'}", "const r = BK.susunAmbilAlih(KM.tahun, lokal(), waktu(), st().yakinAmbilB === KM.tahun); if (r.perluYakin) return set({ yakinAmbilB: KM.tahun, kabar: r.tolak, kabarAwas: true });"]),
    ('putaran 4 P4-1 · pita K6 di perangkat lain: keadaan + kalimat pemegang, TANPA tombol lanjutkan / batalkan / selesai', ["const bukanP = KM ? BK.bkBukanPemegang(KM.tahun, lokal()) : '';", "${bukanP ? pitaBukan : h`<div class=\"hg-pil\"><div class=\"seg aktif ${s.sibuk ? 'mati' : ''}\" data-aksi=\"bkLanjut\">", "${bukanP ? pitaBukan : h`<div class=\"hg-pil\"><div class=\"seg aktif ${s.sibuk ? 'mati' : ''}\" data-aksi=\"bkCadangan\""]),
]
# sanggahan paket A: jangkar kontrol yang dipakai lebih dari satu kontrol
SUSULAN_SARING = "const daftar = A.daftar.filter((x) => !sudah[x.koleksi + '|' + x.id] && !tinggal[x.koleksi + '|' + x.id]);"
JAM_RESET_BARU = '\n'.join([
    "if (j === 0) return 14; if (j === 23) return 15; } catch (e) { /* tanpa data zona */ }",
    "  const y = Number(d.slice(0, 4)); const minggu = (bln, ke) => { const a = new Date(Date.UTC(y, bln, 1)); return new Date(Date.UTC(y, bln, 1 + ((7 - a.getUTCDay()) % 7) + (ke - 1) * 7)).toISOString().slice(0, 10); };",
    "  return d > minggu(2, 2) && d <= minggu(10, 1) ? 14 : 15;"])
JAM_RESET_LAMA = JAM_RESET_BARU.replace("if (j === 0) return 14; if (j === 23) return 15; }", "void j; }").replace("return d > minggu(2, 2) && d <= minggu(10, 1) ? 14 : 15;", "return d >= minggu(2, 2) && d < minggu(10, 1) ? 14 : 15;")

RUSAK = [
    # ---- siap 2027 (owner 7 Okt, paket A)
    ('A1 · alasan putusan tidak dinilai (kurang dari 5 huruf diterima)', 'baru/js/layar/tutup-buku-logika.js', "const bkAlasanCukup = (a) => String(a || '').trim().length >= 5;", "const bkAlasanCukup = (a) => true;"),
    ('A1 · kunci tanpa gerbang di pintu masuk (hari belum diputus / minus lolos)', 'baru/js/layar/tutup-buku-logika.js', "if (gTolak.length) return { tolak: 'Periksa dulu belum beres — '", "if (false) return { tolak: 'Periksa dulu belum beres — '"),
    ('A1 · putusan riwayat kunci bulan tidak dipakai ulang', 'baru/js/layar/tutup-buku-logika.js', "if (r && r.aksi === 'kunci') (r.hari || []).forEach(", "if (false) (r.hari || []).forEach("),
    ('A1 · berita acara tanpa putusan hari', 'baru/js/layar/tutup-buku-logika.js', "    putusanHari: G.hari.map((h) => ({ iso: h.iso,", "    putusanHariLama: G.hari.map((h) => ({ iso: h.iso,"),
    ('A3 · tanda indukUkuran tidak dibawa (buku 25 kg terdampar)', 'baru/js/layar/tutup-buku-logika.js', "(pas.length ? pas : baris.slice(0, 1)).forEach((r) => { r.indukUkuran = pu[k].induk; });", "void pas;"),
    ('A3 · buku berstok 0 tidak lahir lagi', 'baru/js/layar/tutup-buku-logika.js', "Object.keys(stokK).concat(Object.keys(pw)).sort().forEach((k) => {", "Object.keys(pw).sort().forEach((k) => {"),
    ('A3 · kemasan adukan yang dibuka jadi karung wadah lagi', 'baru/js/layar/tutup-buku-logika.js', "else if (bw[r.merk] && bw[r.merk].jenis === 'adukan') r.bukuAdukan = asliAdukan[r.merk] || bw[r.merk].wadah; else if (bw[r.merk]) r.karungWadah", "else if (bw[r.merk]) r.karungWadah"),
    ('A3 · tanda gabung balik ke induk tidak dibawa', 'baru/js/layar/tutup-buku-logika.js', "if (ug[r.merk]) r.digabungKe = ug[r.merk];", ""),
    ('A3 · toko.js tidak membaca tanda gabung dari baris pembuka', 'baru/js/data/toko.js', "if (m && m.merk && m.digabungKe && !out[String(m.merk)]) out[String(m.merk)] = String(m.digabungKe);", ""),
    ('A3 · merek pemasok kelas tidak dibawa', 'baru/js/layar/tutup-buku-logika.js', "if (pemasokKelas[r.merk]) r.merkPemasok = pemasokKelas[r.merk];", ""),
    ('A3 · kemasan berstok 0 tidak lahir lagi (chip habis hilang dari rak)', 'baru/js/layar/tutup-buku-logika.js', "if (Math.abs(s.sisaUnit) > 1e-9) return;\n    d.push(", "return;\n    d.push("),
    ('A4 · modal owner tanpa saldo pembuka', 'baru/js/layar/tutup-buku-logika.js', "if (Math.abs(modal) >= 0.5) d.push({ koleksi: 'modalOwner',", "if (false) d.push({ koleksi: 'modalOwner',"),
    ('A4 · pembuka modal bertanggal 1 Jan (terbaca uang masuk)', 'baru/js/layar/tutup-buku-logika.js', "nominal: Math.round(Math.abs(modal)), tanggal: c, jam: '00:00',", "nominal: Math.round(Math.abs(modal)), tanggal: tglBuka, jam: '00:00',"),
    ('A4 · modal owner tanpa saringan pembuka bertahap', 'baru/js/data/toko.js', "export function ambilModalOwner() { return bkSaring(_cache.modal); }", "export function ambilModalOwner() { return _cache.modal; }"),
    ('A4 · baris modal owner tidak dibandingkan', 'baru/js/layar/tutup-buku-logika.js', "  const lain = [{ id: 'modal',", "  const lain = [{ id: 'modalX',"),
    ('A5 · gerbang g6 dimatikan', 'baru/js/layar/tutup-buku-logika.js', "tanggalPendek(sampai), ok: !M.n,", "tanggalPendek(sampai), ok: true,"),
    ('A5 · baris kemasan buta minus lagi', 'baru/js/layar/tutup-buku-logika.js', "if (!(Math.abs(s.sisaUnit) > 1e-9)) return; unit += s.sisaUnit;", "if (!(s.sisaUnit > 0)) return; unit += s.sisaUnit;"),
    ('A5 · bayar lebih ke pemasok tidak mengurangi baris utang', 'baru/js/layar/tutup-buku-logika.js', "const utangP = up.reduce((a, x) => a + x.totalUtang, 0) - tekorP,", "const utangP = up.reduce((a, x) => a + x.totalUtang, 0),"),
    ('A5 · baris pembuka beras minus dinilai minus (buta)', 'baru/js/layar/tutup-buku-logika.js', "j.beras += Number(m.totalKg) > 0 ? Number(m.subtotalHarga) || 0 : 0;", "j.beras += Number(m.subtotalHarga) || 0;"),
    ('A6 · patokan gaji sistem lama tidak dibawa berita acara', 'baru/js/layar/upah-logika.js', "  const k = upKunci(nama); let sampai = '';\n  ambilTutupBukuAcara()", "  const k = upKunci(nama); let sampai = ''; return sampai;\n  ambilTutupBukuAcara()"),
    ('A6 · upah Desember menulis biaya 2026 sesudah tutup buku', 'baru/js/layar/upah-logika.js', "!(tolakKunciTanggal(b + '-01', '') || upTahunDitutup(b))", "!tolakKunciTanggal(b + '-01', '')"),
    ('A6 · baris upah belum dibayar tidak dibandingkan', 'baru/js/layar/tutup-buku-logika.js', "{ id: 'upah', nama: 'Upah karyawan yang belum dibayar · '", "{ id: 'upahX', nama: 'Upah karyawan yang belum dibayar · '"),
    ('A7 · ringkasan tahun tidak ditulis di batch penanda', 'baru/js/layar/tutup-buku-logika.js', "  tanda.data.ringkasTahun = ringkasTahun(tahun);", ""),
    ('A7 · KR1 tidak memakai ringkasan', 'baru/js/data/toko.js', "if (Math.abs(ring - hidupLama) < 0.5) return info;", "return info;"),
    ('A7 · laju pakai tidak memakai ringkasan', 'baru/js/data/toko.js', "geser(R.laju.hari, 1); geser(hidup, -1);", "geser(hidup, -1);"),
    ('A7 · salinan rumus laju per hari bergeser dari mesin', 'baru/js/data/toko.js', "if ((p.jenis === 'karung' || p.jenis === 'repacking' || p.jenis === 'literan') && p.merkSumber) tb(h(t).kg, p.merkSumber, p.totalKg || 0);", "if ((p.jenis === 'karung' || p.jenis === 'literan') && p.merkSumber) tb(h(t).kg, p.merkSumber, p.totalKg || 0);"),
    ('A7 · daftar pelanggan tidak memakai ringkasan', 'baru/js/layar/pelanggan-logika.js', "  const RA = ringkasArsip();\n  if (RA && RA.pelanggan) {", "  const RA = null;\n  if (RA && RA.pelanggan) {"),
    ('A8 · jam reset kuota selalu 14.00 (zona Pasifik diabaikan)', 'baru/js/layar/tutup-buku-logika.js', "if (j === 0) return 14; if (j === 23) return 15; } catch", "return 14; } catch"),
    ('A8 · jam reset kembali ke aturan tanggal LAMA (meleset satu jam di Minggu pergantian Maret & November)', 'baru/js/layar/tutup-buku-logika.js', JAM_RESET_BARU, JAM_RESET_LAMA),
    ('A8 · tanpa data zona: aturan tanggal lama (meleset di hari pergantian)', 'baru/js/layar/tutup-buku-logika.js', "return d > minggu(2, 2) && d <= minggu(10, 1) ? 14 : 15;", "return d >= minggu(2, 2) && d < minggu(10, 1) ? 14 : 15;"),
    ('A8 · peringatan MEPET tidak pernah muncul', 'baru/js/layar/tutup-buku-logika.js', "mepet = R.filter((x) => x.n <= x.batas && x.n > 0.8 * x.batas);", "mepet = R.filter((x) => false);"),
    ('A9 · susulan disapu sebagai sisa arsip (lanjutkan arsip)', 'baru/js/layar/tutup-buku-logika.js', "if (a.status === 'terkunci') { const sisa = bkArsipHabis(tahun) ? 0 : arsipBuku(tahun).n;", "if (a.status === 'terkunci') { const sisa = arsipBuku(tahun).n;"),
    ('A9 · hasil periksa tidak dibekukan bila ada catatan susulan', 'baru/js/layar/tutup-buku-logika.js', "(sisa && !habis)", "sisa"),
    ('A9 · susulan tidak terdeteksi', 'baru/js/layar/tutup-buku-logika.js', "  if (!a || !(a.status === 'selesai' || (a.status === 'terkunci' && bkArsipHabis(t)))) return null;", "  return null;"),
    ('A9 · "sudah dicatat" tidak menyembunyikan apa pun', 'baru/js/layar/tutup-buku-logika.js', SUSULAN_SARING, "const daftar = A.daftar.filter((x) => !tinggal[x.koleksi + '|' + x.id]);"),
    ('A9 · pesanan yang sengaja tertinggal (belum tuntas) disebut susulan begitu dibayar Januari', 'baru/js/layar/tutup-buku-logika.js', SUSULAN_SARING, "const daftar = A.daftar.filter((x) => !sudah[x.koleksi + '|' + x.id]);"),
    ('A9 · hasil periksa saat arsip habis tidak mencatat pesanan yang tertinggal', 'baru/js/layar/tutup-buku-logika.js', "    tertinggal: bkTertinggalKini(tahun) };", "    tertinggal: [] };"),
    ('A9 · berita acara selesai tidak mencatat pesanan yang tertinggal', 'baru/js/layar/tutup-buku-logika.js', "periksaUlang, susulan, tertinggal, langkah:", "periksaUlang, susulan, langkah:"),
    ('A9 · pengeluaran telat memakai kalimat nota (tanpa kalimat pengeluaran)', 'baru/js/layar/tutup-buku-logika.js', "const keluar = daftar.filter((x) => x.koleksi === 'pengeluaranHarian');", "const keluar = [];"),
    ('A4 · pembuka modal (31 Des) terbaca tarik modal = ambil pribadi Desember', 'baru/js/layar/uang-logika.js', "&& !m.pinjaman && !m.tutupBuku && dlm(m.tanggal)", "&& !m.pinjaman && dlm(m.tanggal)"),
    ('A4 · buku owner: pembuka modal tampil sebagai setoran / penarikan (dan bukti setoran)', 'baru/js/layar/owner-toko-logika.js', "    if (m.tutupBuku) { rows.push(", "    if (false) { rows.push("),
    ('A4 · buku kas 31 Des menampilkan pembuka modal sebagai gerakan uang', 'baru/js/layar/laporan-logika.js', "r.t === iso && !pembukaModal[String(r.id)]", "r.t === iso"),
    ('era · cap era cadangan dihitung sendiri lagi (dua tempat, tanpa modal owner)', 'baru/js/layar/sistem-logika.js', "export function ssEraTutupBuku() { return eraBuku(); }",
     "export function ssEraTutupBuku() { let t = null; ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'].forEach((c) => cacheMentah(c).forEach((x) => { if (x && x.tutupBuku && pembukaBerlaku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } })); return t; }"),
    ('A2 · Beranda tidak menyebut tutup buku tahun lalu', 'baru/js/layar/tutup-buku-logika.js', "if (T.bolehSungguhan && !bkTahunSelesai(T.tahun).ok) {", "if (false) {"),
    ('saldo pembuka tidak dipecah (sekali kirim)', 'baru/js/layar/tutup-buku-logika.js', "const Pt = kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] }))",
     "const Pt = { potongan: [{ dokumen: P.dokumen.concat(penanda, [{ koleksi: 'tutupBukuAcara', data: acara }]), get: 0 }] } || kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] }))"),
    ('mesin melihat pembuka yang belum selesai (saringan data mati)', 'baru/js/data/toko.js', "const bkSaring = (arr) => { const s = arr.filter(pembukaBerlaku);", "const bkSaring = (arr) => { return arr; const s = arr.filter(pembukaBerlaku);"),
    ('§8 no. 1 · HP staf: pembuka tanpa penanda tetap terlihat (saringan hanya dari berita acara)', 'baru/js/data/toko.js', "return !k.sembunyi[t] && (!x.bertahap || !!k.penanda[t]); }", "return !k.sembunyi[t]; }"),
    ('§8 no. 1 · batch penanda ikut kiriman PERTAMA (bukan terakhir)', 'baru/js/layar/tutup-buku-logika.js', "const Pt = kpPotong(P.dokumen.filter((x) => x !== tanda).map((x) => ({ dokumen: [x] })).concat([{ dokumen: [tanda].concat(penanda,",
     "const Pt = kpPotong(P.dokumen.map((x) => ({ dokumen: [x] })).concat([{ dokumen: [].concat(penanda,"),
    ('§8 no. 1 · batal menghapus batch penanda TERAKHIR (bukan di kiriman pertama)', 'baru/js/layar/tutup-buku-logika.js', "const P = kpPotong([{ dokumen: awal, hapus: tanda }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] }))),",
     "const P = kpPotong([{ dokumen: awal, hapus: [] }].concat(sisa.map((x) => ({ dokumen: [], hapus: [x] })), [{ dokumen: [], hapus: tanda }]),"),
    # siap 2027: era = toko.js eraBuku (satu tempat, juga dibaca upah)
    ('era menghitung pembuka yang belum selesai', 'baru/js/data/toko.js', "if (x && x.tutupBuku && pembukaBerlaku(x)) { const n = Number(x.tahunDari);", "if (x && x.tutupBuku) { const n = Number(x.tahunDari);"),
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
    ('§8 no. 6 · selesai tanpa memeriksa arsip & periksa ulang', 'baru/js/layar/tutup-buku-logika.js', "  const sisa = bkArsipHabis(tahun) ? 0 : arsipBuku(tahun).n; if (sisa) return { tolak: ANGKA(sisa) + ' catatan '", "  const sisa = 0; if (sisa) return { tolak: ANGKA(sisa) + ' catatan '"),
    ('§8 no. 6 · selesai menerima periksa ulang yang beda tanpa ketukan kedua', 'baru/js/layar/tutup-buku-logika.js', "  if (kal && !yakin) return {", "  if (kal && !yakin && false) return {"),
    ('§8 no. 7 · pembatalan yang berhenti di kiriman 1 menyuruh "Lanjutkan"', 'baru/js/layar/tutup-buku-logika.js', "return awal + (ke === 1 ? ' Kiriman ini tidak masuk", "return awal + (false ? ' Kiriman ini tidak masuk"),
    ('§8 no. 7 · tutup buku yang berhenti di kiriman 1 menyuruh "Lanjutkan"', 'baru/js/layar/tutup-buku-logika.js', "return awal + (ke === 1 ? ' Tidak ada yang masuk", "return awal + (false ? ' Tidak ada yang masuk"),
    ('§8 no. 8 · mulai baru membawa tanggal pembatalan lama', 'baru/js/layar/tutup-buku-logika.js', "delete acara.dariStatus; delete acara.dibatalkanPada; delete acara.dibatalkanTanggal;", "delete acara.dariStatus;"),
    ('§8 no. 9 · daftar periksa Kunci bulan tidak melihat tutup buku setengah jalan', 'baru/js/layar/kunci-periode-logika.js', "tambah({ id: 'tutupBukuTuntas', blokir: true, ok: !KMb,", "tambah({ id: 'tutupBukuTuntas', blokir: true, ok: true || !KMb,"),
    ('putaran 3 AAL1 · arsip tidak berhenti walau tutup buku dibatalkan dari perangkat lain', 'baru/js/layar/tutup-buku-logika.js', "const a = bkAcara(tahun); if (a && a.status === 'terkunci') return bkBukanPemegang(tahun, L);", "const a = bkAcara(tahun); if (true) return '';"),
    ('putaran 3 UTBU-1 · "selesai" & pita menghitung ulang periksa ulang (hasil yang dibekukan diabaikan)', 'baru/js/layar/tutup-buku-logika.js', "  if (!P || !Array.isArray(P.baris) || !bkPercobaan(a) ||", "  if (true ||"),
    ('putaran 3 UTBU-1 · hasil periksa ulang tidak disusun untuk dibekukan', 'baru/js/layar/tutup-buku-logika.js', "  if (!PU || !a || a.status !== 'terkunci' || (sisa && !habis) || bkBukanPemegang(tahun, L) || !bkPercobaan(a)) return { PU };", "  if (true) return { PU };"),
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
    ('putaran 4 BP4R-2 · pembatalan lanjutan dari "dibatalkan" membawa pemegang lama', 'baru/js/layar/tutup-buku-logika.js', "  if (acara.status === 'dibatalkan') { const pg = bkPerangkatIni(L); if (pg) batal.pemegang = pg; }\n", ""),
    ('TRV6-EKOR · kalimat menyebut "perangkat lain" untuk jendela lain di perangkat yang sama', 'baru/js/layar/tutup-buku-logika.js', "String(L.idPerangkat || '') === String(p.id) ? 'jendela lain di perangkat ini' : 'perangkat lain';", "false ? 'jendela lain di perangkat ini' : 'perangkat lain';"),
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
    ('putaran 4 P4-5 · sisi mesin yang tidak bisa dihitung ditandai "≠"', 'baru/js/layar/tutup-buku-logika.js', "tanda: !ada ? '' : !tahu || s === null ? '?' :", "tanda: !ada ? '' : !tahu ? '?' :"),
    ('pemeriksaan ulang kembali ke 1 Jan vs 31 Des', 'baru/js/layar/tutup-buku-logika.js', "return bandingBuku({ harta: H.baris, utang: [] }, o);",
     "const B1 = barisBuku((tahun + 1) + '-01-01', (tahun + 1) + '-01-01'); const o1 = {}; B1.harta.concat(B1.utang).forEach((b) => { o1[b.id] = b.n; }); return bandingBuku({ harta: a.sebelum, utang: [] }, o1);"),
    # ---- TRV6-EKOR-1: ekor pembatalan (jalankanBatal uang.js dijalankan apa adanya — berkas yang dirusak ikut dibaca)
    ('TRV6-EKOR-1 · uang.js bentuk lama (ekor tanpa penjaga, sebelum tambalan)', 'baru/js/layar/uang.js', EKOR_BARU, EKOR_LAMA),
    ('TRV6-EKOR-1 · uang.js tidak memeriksa SEBELUM pengembalian pertama', 'baru/js/layar/uang.js', "try { cekEkor(); await kembalikan(r.pulih);", "try { await kembalikan(r.pulih);"),
    ('TRV6-EKOR-1 · uang.js tidak memeriksa SEBELUM arsip dibaca ulang', 'baru/js/layar/uang.js', "await kembalikan(r.pulih); cekEkor(); const sisaA", "await kembalikan(r.pulih); const sisaA"),
    ('TRV6-EKOR-1 · uang.js tidak memeriksa SEBELUM pengembalian kedua', 'baru/js/layar/uang.js', "const sisaA = await bacaArsipTahun(tahun); cekEkor(); if (sisaA.length)", "const sisaA = await bacaArsipTahun(tahun); if (sisaA.length)"),
    ('TRV6-EKOR-1 · uang.js tidak memeriksa SEBELUM berita acara dibatalkan', 'baru/js/layar/uang.js', "if (sisaA.length) await kembalikan(sisaA); cekEkor(); } catch (e) {", "if (sisaA.length) await kembalikan(sisaA); } catch (e) {"),
    ('TRV6-EKOR-1 · uang.js tidak memeriksa sesudah tiap potongan pengembalian', 'baru/js/layar/uang.js', "tadi = sudah; cekEkor(); potongTadi = []; });", "tadi = sudah; potongTadi = []; });"),
    ('TRV6-EKOR-1 · uang.js tidak mengarsipkan lagi potongan yang membuatnya berhenti', 'baru/js/layar/uang.js', "if (ulang.length) { try { await arsipkanDokumen(tahun, ulang); }", "if (false) { try { await arsipkanDokumen(tahun, ulang); }"),
    ('TRV6-EKOR-1 · uang.js mengarsipkan lagi potongan yang SAH kembali (lolos pemeriksaannya)', 'baru/js/layar/uang.js', "tadi = sudah; cekEkor(); potongTadi = []; });", "tadi = sudah; cekEkor(); });"),
    ('TRV6-EKOR-1 · penjaga ekor tidak membaca status (selain membatalkan boleh lanjut)', 'baru/js/layar/tutup-buku-logika.js', "if (a && a.status === 'membatalkan' && bkPercobaan(a) === String(percobaan || '') && !bkBukanPemegang(tahun, L)) return '';",
     "if (a && bkPercobaan(a) === String(percobaan || '') && !bkBukanPemegang(tahun, L)) return '';"),
    ('TRV6-EKOR-1 · penjaga ekor tidak membaca percobaan', 'baru/js/layar/tutup-buku-logika.js', "if (a && a.status === 'membatalkan' && bkPercobaan(a) === String(percobaan || '') && !bkBukanPemegang(tahun, L)) return '';",
     "if (a && a.status === 'membatalkan' && !bkBukanPemegang(tahun, L)) return '';"),
    ('TRV6-EKOR-1 · penjaga ekor tidak membaca pemegang', 'baru/js/layar/tutup-buku-logika.js', "if (a && a.status === 'membatalkan' && bkPercobaan(a) === String(percobaan || '') && !bkBukanPemegang(tahun, L)) return '';",
     "if (a && a.status === 'membatalkan' && bkPercobaan(a) === String(percobaan || '')) return '';"),
    ('TRV6-EKOR-1 · susunBatal tidak mencatat percobaan (penjaga ekor berbunyi palsu)', 'baru/js/layar/tutup-buku-logika.js', "percobaan: bkPercobaan(batal), ", ""),
    ('TRV6-EKOR-1 · arsip ulang di status mana pun (berjalan / membatalkan / dibatalkan ikut)', 'baru/js/layar/tutup-buku-logika.js', "if (!a || (a.status !== 'terkunci' && a.status !== 'selesai') || bkPercobaan(a) === String(percobaan || '')) return [];",
     "if (!a || bkPercobaan(a) === String(percobaan || '')) return [];"),
    ('TRV6-EKOR-1 · arsip ulang juga pada percobaan yang SAMA', 'baru/js/layar/tutup-buku-logika.js', "if (!a || (a.status !== 'terkunci' && a.status !== 'selesai') || bkPercobaan(a) === String(percobaan || '')) return [];",
     "if (!a || (a.status !== 'terkunci' && a.status !== 'selesai')) return [];"),
    ('TRV6-EKOR-1 · arsip ulang tidak pernah', 'baru/js/layar/tutup-buku-logika.js', "  return (daftar || []).map((x) => ({ koleksi: x.koleksi, id: x.idAsli, data: x.dok })); }", "  return []; }"),
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
            if berkas == 'baru/js/layar/uang.js': l, g = utama(bundelan(), uang=asli.replace(lama, baru))   # TRV6-EKOR-1: jalankanBatal dari berkas yang dirusak
            else:
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
        a, e = jalan(JAM + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + uji_kunci_periode.PUTUSAN_TIRUAN + ASAP)
        if a is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s) pada 5 Jan 2027: %s' % (os.path.basename(cad[-1]), json.dumps(a, ensure_ascii=False)))
        if a['salah']: sys.exit(2)
    # siap 2027: asap ritual penuh atas cadangan LOKAL (argumen --asap=… atau env TUTUP_BUKU_ASAP) — dilewati di CI (cadangan toko tidak pernah ada di repo)
    berkas = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--asap=')), '') or os.environ.get('TUTUP_BUKU_ASAP', '')
    if berkas and os.environ.get('GITHUB_ACTIONS'): print('ASAP SIAP 2027 dilewati (CI)')
    elif berkas and not g:
        a, salah = asap_2027(js, berkas)
        if a is not None:
            for h in a['hasil']:
                print('ASAP SIAP 2027 %s · putusan tiruan %d hari · kiriman %s · %d pembuka · %d arsip · %s · periksa ulang: %s · %s' % (h['jam'], h.get('belumDiputus', 0), h.get('kiriman'), h.get('pembuka', 0), h.get('arsip', 0), h.get('banding', '-'), h.get('periksaUlang', '-'), h.get('batal') or h.get('kunciJanuari', '-')))
                print('    dibandingkan: %s · kuota ritual %s · batal %s (rencana %s, reset %s.00 WIB)' % (json.dumps(h.get('dibandingkan')), json.dumps(h.get('kuota', {}).get('ritual')), json.dumps(h.get('kuota', {}).get('batal')), h.get('kuota', {}).get('rencana'), h.get('kuota', {}).get('jam')))
        for x in salah: print('   ✗ ASAP ' + x[:500])
        print('ASAP SIAP 2027 (%s): %s' % (os.path.basename(berkas), 'LULUS' if not salah else '%d GAGAL' % len(salah)))
        if salah: sys.exit(2)
    sys.exit(1 if g else 0)
