#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_titipan.py — titipan uang keluar & pesan dari tablet, notifikasi dalam aplikasi, dan notifikasi HP owner (owner 21 Nov 2026), dijalankan ASLI di jsc
dengan data tiruan, ditambah pemeriksaan pemasangannya.

Kenapa ada: titipan menyentuh uang toko (laci, laba, kasbon) lewat tangan orang lain. Satu cacat lama sudah ketemu saat paket ini dibangun: papan
Persetujuan menandai titipan "disetujui" TANPA menulis uangnya, dan "setujui sekaligus" hanya mengirim dokumen pertama tiap putusan.

Yang dipegang:
  · tablet menulis HANYA persetujuan "menunggu" berbentuk rules v13 (jenis sah, nominal bulat > 0, atas nama sendiri, tanpa kolom keputusan / betulan)
  · menyetujui = satu kiriman: persetujuan disetujui + uangnya (belanja toko / untuk karyawan → pengeluaranHarian kategori toko; kasbon → kasbonMutasi
    ambil) bertanggal & berjam TITIPANNYA, dari laci, menunjuk titipannya (dariPersetujuan); betulan owner menimpa tetapi angka asli tetap tercatat
  · penjaga: putus dua kali, uang dobel, bulan terkunci, tolak tanpa alasan, jenis / nominal tidak sah; titipan lama tanpa kolom jenis = belanja toko
  · pesan: dibaca + balasan; tidak pernah ikut "setujui sekaligus"; papan Persetujuan & Uang memutus lewat pintu yang SAMA
  · notifikasi dalam aplikasi: owner diberi kabar permintaan BARU (bukan saat aplikasi dibuka); tablet diberi kabar putusan permintaannya sendiri
  · isi push server (functions/pesan.js): hanya permintaan menunggu, teks pendek, data semua teks; token mati dikenali; lokasi fungsi = lokasi database
  · service worker notifikasi membaca pesan DATA FCM & selalu menampilkan notifikasi; dukungan perangkat (iPhone hanya dari Layar Utama)
  · pemasangan: rules v13 notifOwner owner saja, CSP, firebase.json, kartu tablet & owner, tutup hari, setujui sekaligus mengirim SEMUA dokumen

    python3 alat-uji/uji_titipan.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_titipan.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
FMT = 'baru/js/inti/format.js'; TPL = 'baru/js/layar/titipan-logika.js'; KBL = 'baru/js/layar/kabar-baru-logika.js'
PSN = 'functions/pesan.js'; SWN = 'baru/notif/sw-notif.js'; NHP = 'baru/js/data/notif-hp.js'
SL = 'baru/js/layar/sistem-logika.js'; UG = 'baru/js/layar/uang-logika.js'; UJ = 'baru/js/layar/uang.js'; MN = 'baru/js/layar/menu.js'; TPP = 'baru/js/layar/titipan-panel.js'
AK = 'baru/js/data/akses.js'; TH = 'baru/js/layar/tutup-hari-logika.js'; APP = 'baru/js/app.js'; IDX = 'baru/index.html'; RULES = 'firestore.rules'
FJ = 'firebase.json'; FIX = 'functions/index.js'; PAS = 'functions/pasang.sh'; FB = 'baru/js/data/firebase.js'; KER = 'baru/css/kerangka.css'
BERKAS = [FMT, TPL, KBL, PSN, SWN, NHP, SL, UG, UJ, MN, TPP, AK, TH, APP, IDX, RULES, FJ, FIX, PAS, FB, KER]

# data/toko.js tiruan: koleksi di __DB, bulan terkunci di __KUNCI
TIRUAN = r"""
var __DB = { persetujuan: [], harian: [], kasbon: [] }; var __KUNCI = '';
function cacheMentah(n) { return __DB[n === 'persetujuan' ? 'persetujuan' : n] || []; }
function ambilPengeluaranHarian() { return __DB.harian; } function ambilKasbonMutasi() { return __DB.kasbon; }
function tolakKunciTanggal(t) { return __KUNCI && String(t || '').slice(0, 7) <= __KUNCI ? 'bulan ' + String(t).slice(0, 7) + ' sudah dikunci' : ''; }
"""

PEMERIKSA = r"""
const hasil = []; const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : JSON.stringify(ket)) });
let _id = 0; const W = { tanggal: '2026-11-22', jam: '09:15', kini: '2026-11-22T02:15:00.000Z', idUnik: () => 'id' + (++_id) };
const BEN = { jenis: 'aktif', peran: 'ben', nama: 'Penjaga A', uid: 'uid-tablet' }; const LAIN = { jenis: 'aktif', peran: 'karyawan', nama: 'Orang B', uid: 'uid-lain' };
const OWNER = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-owner' };
const tulis = (r) => { (r.dokumen || []).forEach((x) => { const k = x.koleksi === 'pengeluaranHarian' ? 'harian' : x.koleksi === 'kasbonMutasi' ? 'kasbon' : x.koleksi; const a = __DB[k] = __DB[k] || []; const i = a.findIndex((d) => String(d.id) === String(x.data.id)); if (i >= 0) a[i] = x.data; else a.push(x.data); }); return r; };
const KUNCI_PUTUS = ['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'koreksiOwner', 'balasan'];

// ---------- tablet menulis titipan ----------
cek('nominal: 50000, 50.000, Rp 50.000 → 50000; pecahan / huruf → NaN', tpAngka('50000') === 50000 && tpAngka('50.000') === 50000 && tpAngka('Rp 50.000') === 50000 && isNaN(tpAngka('50,5')) && isNaN(tpAngka('lima')) && isNaN(tpAngka('')));
let r = tpSusunMinta({ jenis: 'toko', nominal: '25.000', teks: 'Kantong 5 kg' }, BEN, W); const t1 = r.dokumen && r.dokumen[0].data;
cek('titipan belanja toko: satu dokumen persetujuan, tanpa dokumen uang', r.dokumen && r.dokumen.length === 1 && r.dokumen[0].koleksi === 'persetujuan', r);
cek('bentuk rules v13: uangKeluar, menunggu, jenis toko, nominal bulat 25000, mintaUid = penulis, dari laci', t1 && t1.tindakan === 'uangKeluar' && t1.status === 'menunggu' && t1.jenis === 'toko' && t1.nominal === 25000 && Number.isInteger(t1.nominal) && t1.mintaUid === 'uid-tablet' && t1.dariTempat === 'laci', t1);
cek('titipan tanpa kolom keputusan / betulan', t1 && !KUNCI_PUTUS.some((k) => k in t1), t1);
cek('belanja toko tidak membawa nama pegawai', t1 && !('namaPegawai' in t1), t1);
cek('kabar tablet: laci di buku belum berkurang', /belum berkurang/.test(r.patch.kabar), r.patch.kabar);
tulis(r);
cek('titipan yang sama tidak dikirim dua kali selagi menunggu', /tidak dikirim dua kali/.test(tpSusunMinta({ jenis: 'toko', nominal: '25000', teks: 'Kantong 5 kg' }, BEN, W).tolak || ''));
cek('jenis tidak sah ditolak', /Pilih jenisnya/.test(tpSusunMinta({ jenis: 'pribadi', nominal: '1000', teks: 'x' }, BEN, W).tolak || ''));
cek('nominal kosong / nol / pecahan ditolak', /Isi nominalnya/.test(tpSusunMinta({ jenis: 'toko', nominal: '', teks: 'x' }, BEN, W).tolak || '') && !!tpSusunMinta({ jenis: 'toko', nominal: '0', teks: 'x' }, BEN, W).tolak && /rupiah bulat/.test(tpSusunMinta({ jenis: 'toko', nominal: '10,5', teks: 'x' }, BEN, W).tolak || ''));
cek('kasbon tanpa nama ditolak; belanja tanpa keterangan ditolak', /untuk siapa/.test(tpSusunMinta({ jenis: 'kasbon', nominal: '100000' }, BEN, W).tolak || '') && /untuk apa/.test(tpSusunMinta({ jenis: 'toko', nominal: '1000', teks: '  ' }, BEN, W).tolak || ''));
cek('tanpa akun ditolak', !!tpSusunMinta({ jenis: 'toko', nominal: '1000', teks: 'x' }, null, W).tolak);
r = tulis(tpSusunMinta({ jenis: 'kasbon', nominal: '100000', teks: '', nama: 'Orang B' }, BEN, W)); const t2 = r.dokumen[0].data;
cek('kasbon: jenis kasbon, namaPegawai, keterangan boleh kosong', t2.jenis === 'kasbon' && t2.namaPegawai === 'Orang B' && t2.teks === '', t2);
r = tulis(tpSusunMinta({ jenis: 'karyawan', nominal: '15000', teks: 'Makan siang', nama: 'Orang B' }, BEN, W)); const t3 = r.dokumen[0].data;
r = tulis(tpSusunPesan('Kantong 5 kg tinggal 20 lembar', BEN, W)); const p1 = r.dokumen[0].data;
cek('pesan: tindakan pesan, menunggu, mintaUid penulis, tanpa balasan', p1.tindakan === 'pesan' && p1.status === 'menunggu' && p1.mintaUid === 'uid-tablet' && !('balasan' in p1), p1);
cek('pesan kosong / 501 huruf ditolak; 500 huruf boleh', !!tpSusunPesan('   ', BEN, W).tolak && /500 huruf/.test(tpSusunPesan('x'.repeat(501), BEN, W).tolak || '') && !tpSusunPesan('x'.repeat(500), BEN, W).tolak);
const saya = tpMilikSaya(BEN, '2026-11-22', 7);
cek('daftar tablet: empat milik akun ini, terbaru di atas, status menunggu owner', saya.length === 4 && saya.every((b) => b.status === 'menunggu' && b.namaStatus === 'menunggu owner'), saya.map((b) => b.ringkas));
cek('daftar tablet tidak memuat milik akun lain', tpMilikSaya(LAIN, '2026-11-22', 7).length === 0);
cek('kalimat titipan: jenis · nama · keterangan · rupiah', tpTeks(t2) === 'Kasbon karyawan · Orang B · Rp100.000' && tpTeks(t3) === 'Untuk karyawan · Makan siang · untuk Orang B · Rp15.000' && tpTeks(t1) === 'Belanja toko · Kantong 5 kg · Rp25.000', [tpTeks(t1), tpTeks(t2), tpTeks(t3)]);
cek('tutup hari: 3 titipan menunggu Rp140.000 sampai hari ini; sebelum hari itu nol', tpMenungguSampai('2026-11-22').n === 3 && tpMenungguSampai('2026-11-22').rp === 140000 && tpMenungguSampai('2026-11-21').n === 0 && /sudah keluar dari laci/.test(tpMenungguSampai('2026-11-22').kalimat), tpMenungguSampai('2026-11-22'));

// ---------- notifikasi dalam aplikasi (sidik sebelum putusan) ----------
const sidikOwner0 = kbSidik(OWNER); const sidikTablet0 = kbSidik(BEN); const sidikLain0 = kbSidik(LAIN);
cek('owner: 4 menunggu; tablet: 4 milik sendiri', sidikOwner0.n === 4 && Object.keys(sidikTablet0.milik).length === 4, [sidikOwner0.n, Object.keys(sidikTablet0.milik)]);
cek('pembanding pertama tidak berbunyi (aplikasi baru dibuka)', kbBanding(null, sidikOwner0).length === 0 && kbBanding(null, sidikTablet0).length === 0);

// ---------- owner memutus ----------
const W2 = { tanggal: '2026-11-23', jam: '07:30', kini: '2026-11-23T00:30:00.000Z', idUnik: () => 'id' + (++_id) };
r = tpSusunPutus(t1.id, 'setuju', {}, W2);
cek('setujui belanja toko: persetujuan disetujui + pengeluaranHarian dalam SATU kiriman', r.dokumen && r.dokumen.length === 2 && r.dokumen[0].koleksi === 'persetujuan' && r.dokumen[0].data.status === 'disetujui' && r.dokumen[1].koleksi === 'pengeluaranHarian', r);
const u1 = r.dokumen && r.dokumen[1].data;
cek('uangnya: kategori toko, untuk toko, Rp25.000, dari laci, menunjuk titipan', u1 && u1.kategori === 'toko' && u1.untuk === 'toko' && u1.nominal === 25000 && u1.dari === 'laci' && u1.dariPersetujuan === t1.id && u1.keterangan === 'Kantong 5 kg', u1);
cek('uangnya bertanggal & berjam TITIPAN (22 Nov 09:15), bukan hari disetujui (23 Nov)', u1 && u1.tanggal === '2026-11-22' && u1.jam === '09:15', u1);
cek('putusan mencatat kapan diputus', r.dokumen[0].data.diputusTanggal === '2026-11-23' && r.dokumen[0].data.diputusJam === '07:30');
tulis(r);
cek('tidak bisa diputus dua kali', /Sudah diputus/.test(tpSusunPutus(t1.id, 'setuju', {}, W2).tolak || ''));
r = tpSusunPutus(t2.id, 'setuju', { nominal: '80.000' }, W2);
const u2 = r.dokumen && r.dokumen[1].data; const p2 = r.dokumen && r.dokumen[0].data;
cek('kasbon disetujui dengan betulan: kasbonMutasi ambil Rp80.000 atas nama Orang B, dari laci', u2 && r.dokumen[1].koleksi === 'kasbonMutasi' && u2.tipe === 'ambil' && u2.namaPegawai === 'Orang B' && u2.nominal === 80000 && u2.dari === 'laci' && u2.dariPersetujuan === t2.id, u2);
cek('betulan owner tercatat: nominal baru 80.000, asli 100.000, koreksiOwner', p2 && p2.koreksiOwner === true && p2.nominal === 80000 && p2.nominalAsli === 100000 && p2.jenisAsli === 'kasbon', p2);
cek('kabar betulan menyebut tanggal titipan', /dengan betulan/.test(r.patch.kabar) && /22 Nov 2026 09:15/.test(r.patch.kabar), r.patch.kabar);
tulis(r);
cek('menolak tanpa alasan ditolak', /butuh alasan/.test(tpSusunPutus(t3.id, 'tolak', { alasan: ' ' }, W2).tolak || ''));
r = tpSusunPutus(t3.id, 'setuju', { jenis: 'toko', teks: 'Bensin motor', nominal: '20000', nama: '' }, W2);
cek('betulan jenis: untuk karyawan → belanja toko, tanpa nama di keterangan', r.dokumen && r.dokumen[1].data.untuk === 'toko' && r.dokumen[1].data.keterangan === 'Bensin motor' && r.dokumen[0].data.jenisAsli === 'karyawan', r.dokumen && r.dokumen.map((x) => x.data));
cek('betulan nominal pecahan ditolak', /rupiah bulat/.test(tpSusunPutus(t3.id, 'setuju', { nominal: '20.000,5' }, W2).tolak || ''));
r = tpSusunPutus(t3.id, 'setuju', {}, W2);
cek('untuk karyawan: kategori toko, untuk karyawan, nama ikut keterangan', r.dokumen && r.dokumen[1].data.untuk === 'karyawan' && r.dokumen[1].data.kategori === 'toko' && r.dokumen[1].data.keterangan === 'Makan siang · Orang B', r.dokumen && r.dokumen[1].data);
// penjaga dobel: uang untuk titipan ini sudah ada (mis. dua perangkat owner memutus bersamaan)
__DB.harian.push({ id: 'dobel', dariPersetujuan: t3.id, nominal: 15000 });
cek('uang untuk titipan yang sama tidak ditulis dua kali', /tidak ditulis dua kali/.test(tpSusunPutus(t3.id, 'setuju', {}, W2).tolak || ''));
__DB.harian = __DB.harian.filter((h) => h.id !== 'dobel');
__KUNCI = '2026-11';
cek('bulan titipan sudah dikunci → ditolak dengan kalimat kuncinya', /dikunci/.test(tpSusunPutus(t3.id, 'setuju', {}, W2).tolak || ''));
__KUNCI = '';
r = tpSusunPutus(t3.id, 'tolak', { alasan: 'Sudah dibayar owner' }, W2);
cek('tolak: hanya persetujuan, tanpa uang; alasan tercatat', r.dokumen.length === 1 && r.dokumen[0].data.status === 'ditolak' && r.dokumen[0].data.alasanTolak === 'Sudah dibayar owner', r);
tulis(r);
cek('pesan tidak bisa "disetujui"', /dibaca/.test(tpSusunPutus(p1.id, 'setuju', {}, W2).tolak || ''));
r = tulis(tpSusunPutus(p1.id, 'dibaca', { balasan: 'Oke, besok dibelikan' }, W2));
cek('pesan dibaca + balasan', r.dokumen.length === 1 && r.dokumen[0].data.status === 'dibaca' && r.dokumen[0].data.balasan === 'Oke, besok dibelikan', r);
cek('titipan lama tanpa kolom jenis = belanja toko', tpJenis({ tindakan: 'uangKeluar' }) === 'toko');
__DB.persetujuan.push({ id: 'lama1', tindakan: 'uangKeluar', status: 'menunggu', teks: 'Tali rafia', nominal: 15000, tanggal: '2026-09-19', jam: '10:42', dari: 'Penjaga A' });
r = tpSusunPutus('lama1', 'setuju', {}, W2);
cek('titipan lama tanpa jenis disetujui sebagai belanja toko', r.dokumen && r.dokumen[1].data.untuk === 'toko' && r.dokumen[1].data.nominal === 15000, r);
__DB.persetujuan = __DB.persetujuan.filter((m) => m.id !== 'lama1');
cek('sesudah diputus: tidak ada yang menunggu', tpMenunggu().length === 0 && tpMenungguSampai('2026-11-30').n === 0, tpMenunggu());

// ---------- notifikasi: putusan → tablet; permintaan baru → owner ----------
const ev = kbBanding(sidikTablet0, kbSidik(BEN));
cek('tablet diberi kabar 4 putusan (3 titipan, 1 pesan)', ev.length === 4 && ev.every((e) => e.jenis === 'putus'), ev.map((e) => e.judul));
const tolakEv = ev.find((e) => e.status === 'ditolak');
cek('kabar penolakan menyebut alasannya', tolakEv && /Sudah dibayar owner/.test(tolakEv.isi) && /DITOLAK/.test(tolakEv.judul), tolakEv);
cek('kabar pesan dibaca menyebut balasannya', ev.some((e) => e.status === 'dibaca' && /besok dibelikan/.test(e.isi)));
cek('ringkasan beberapa kabar: satu pita, merah bila ada yang ditolak', kbRingkas(ev).judul === '4 kabar baru' && kbRingkas(ev).awas === true, kbRingkas(ev));
cek('akun lain tidak diberi kabar putusan permintaan orang lain', kbBanding(sidikLain0, kbSidik(LAIN)).length === 0, kbBanding(sidikLain0, kbSidik(LAIN)));
const sidikOwner1 = kbSidik(OWNER); tulis(tpSusunPesan('Timbangan rusak', BEN, W2));
const evO = kbBanding(sidikOwner1, kbSidik(OWNER));
cek('owner diberi kabar permintaan BARU saja; ketuk → Uang', evO.length === 1 && evO[0].judul === 'Pesan dari tablet' && /Timbangan rusak/.test(evO[0].isi) && evO[0].layar === 'uang', evO);
cek('owner: kabar tidak berulang tanpa permintaan baru', kbBanding(kbSidik(OWNER), kbSidik(OWNER)).length === 0);
cek('beda akun = belum ada pembanding (tidak berbunyi)', kbBanding(kbSidik(BEN), kbSidik(OWNER)).length === 0);

// ---------- cetak ----------
const bCetak = tpMilikSaya(BEN, '2026-11-23', 7).find((b) => b.jenis === 'kasbon');
const slip = tpTeksCetak(bCetak, { nama: 'Toko Uji' }, { tanggal: '2026-11-23', jam: '08:00', oleh: 'Penjaga A' });
cek('slip titipan: judul, NOMINAL, angka diketik asli bila dibetulkan, status, paraf', /^TITIPAN UANG KELUAR/.test(slip) && /NOMINAL  Rp80\.000/.test(slip) && /Diketik  Rp100\.000/.test(slip) && /Status  disetujui/.test(slip) && /Paraf yang jaga/.test(slip), slip);
const rekap = tpTeksRekap(tpMilikSaya(BEN, '2026-11-23', 7), '2026-11-22', { nama: 'Toko Uji' }, {});
cek('rekap hari: disetujui Rp105.000 (25.000 + 80.000), ditolak Rp15.000, pesan 1', /Disetujui  Rp105\.000/.test(rekap) && /Ditolak  Rp15\.000/.test(rekap) && /Pesan: 1/.test(rekap), rekap);

// ---------- isi push server (functions/pesan.js) ----------
const P = __modul.exports;
const n1 = P.pesanNotif({ tindakan: 'uangKeluar', status: 'menunggu', jenis: 'kasbon', namaPegawai: 'Orang B', nominal: 100000, dari: 'Penjaga A' }, 'x1');
cek('push titipan: judul & isi pendek, layar uang, tag per permintaan', n1 && n1.judul === 'Titipan uang keluar · Penjaga A' && n1.isi === 'Kasbon karyawan · Orang B · Rp100.000' && n1.layar === 'uang' && n1.tag === 'persetujuan-x1', n1);
cek('push: semua kolom data berupa teks (syarat pesan data FCM)', n1 && Object.keys(n1).every((k) => typeof n1[k] === 'string'));
cek('push tidak dikirim untuk permintaan yang sudah diputus', P.pesanNotif({ tindakan: 'pesan', status: 'dibaca', teks: 'x' }, 'x') === null && P.pesanNotif(null, 'x') === null);
const n2 = P.pesanNotif({ tindakan: 'pesan', teks: 'y'.repeat(400), dari: 'A' }, 'x2');
cek('push pesan panjang dipotong ' + P.BATAS_ISI + ' huruf', n2.isi.length === P.BATAS_ISI && /…$/.test(n2.isi), n2.isi.length);
cek('push nego → layar menu, rupiah ikut', P.pesanNotif({ tindakan: 'nego', teks: 'Beras A 5 kg', nominal: 70000, dari: 'B' }, 'x3').layar === 'menu' && /Rp70\.000/.test(P.pesanNotif({ tindakan: 'nego', teks: 'Beras A 5 kg', nominal: 70000, dari: 'B' }, 'x3').isi));
cek('token mati dikenali; galat lain tidak', P.tokenMati('messaging/registration-token-not-registered') && !P.tokenMati('messaging/internal-error'));
cek('lokasi fungsi: nam5 → us-central1, eur3 → europe-west1, asia-southeast2 tetap', P.lokasiFungsi('nam5') === 'us-central1' && P.lokasiFungsi('eur3') === 'europe-west1' && P.lokasiFungsi('asia-southeast2') === 'asia-southeast2' && P.lokasiFungsi('') === '');

// ---------- service worker notifikasi ----------
const m1 = __sw.bacaPesan(JSON.stringify({ data: { judul: 'J', isi: 'I', tag: 'T', layar: 'uang' }, from: '1', fcmMessageId: 'f' }));
cek('SW membaca pesan DATA FCM', m1.judul === 'J' && m1.isi === 'I' && m1.tag === 'T' && m1.layar === 'uang', m1);
const m2 = __sw.bacaPesan(JSON.stringify({ notification: { title: 'A', body: 'B' } })); const m3 = __sw.bacaPesan('bukan json');
cek('SW: pesan notifikasi biasa & teks polos tetap tampil berjudul', m2.judul === 'A' && m2.isi === 'B' && m3.judul === 'Toko Beras M.IQBAL' && m3.isi === 'bukan json', [m2, m3]);
let tampil = 0; __sw.daftar.push.forEach((f) => f({ data: { text: () => '{"data":{"judul":"x"}}' }, waitUntil: (p) => { tampil += 1; } }));
cek('SW: tiap push menampilkan notifikasi (Safari mencabut izin situs yang diam)', tampil === 1 && __sw.tampil.length === 1 && __sw.tampil[0][0] === 'x', __sw.tampil);

// ---------- dukungan perangkat (notif-hp.js) ----------
const W0 = (o) => Object.assign({ isSecureContext: true, PushManager: function () {}, Notification: function () {}, matchMedia: () => ({ matches: false }) }, o || {});
const iphone = { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)', serviceWorker: {}, standalone: false };
cek('iPhone di tab Safari: belum bisa, disuruh Tambah ke Layar Utama', !nhDukung({ nav: iphone, win: W0() }).ok && /Layar Utama/.test(nhDukung({ nav: iphone, win: W0() }).sebab));
cek('iPhone dari Layar Utama: bisa', nhDukung({ nav: Object.assign({}, iphone, { standalone: true }), win: W0() }).ok);
cek('Mac Chrome: bisa; tanpa PushManager: tidak', nhDukung({ nav: { userAgent: 'Mozilla/5.0 (Macintosh)', serviceWorker: {} }, win: W0() }).ok && !nhDukung({ nav: { userAgent: 'Mac', serviceWorker: {} }, win: (() => { const w = W0(); delete w.PushManager; return w; })() }).ok);
cek('bukan https: tidak', !nhDukung({ nav: { userAgent: 'Mac', serviceWorker: {} }, win: W0({ isSecureContext: false }) }).ok);
cek('kunci VAPID: base64url diawali B ±87 huruf sah; teks lain tidak', nhVapidSah('B' + 'a'.repeat(86)) && !nhVapidSah('kunci-rahasia') && !nhVapidSah('B' + 'a'.repeat(20)) && !nhVapidSah('Aaaa' + 'a'.repeat(84)));

print(JSON.stringify(hasil));
"""


def baca_semua():
    return {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}


def rakit(t):
    js = bundel_baru.PRELUDE + TIRUAN
    js += bundel_baru.polos(t[FMT]) + '\n' + bundel_baru.polos(t[TPL]) + '\n' + bundel_baru.polos(t[KBL]) + '\n'
    # notif-hp.js: hanya bagian murni (impor firebase.js dibuang; fungsi yang memakainya tidak dipanggil)
    js += bundel_baru.polos(t[NHP]).replace('await import(NH_SDK)', 'null') + '\n'
    # functions/pesan.js (CommonJS) dalam lingkupnya sendiri
    js += 'var __modul = { exports: {} }; (function (module) {\n' + t[PSN] + '\n})(__modul);\n'
    # service worker dalam lingkupnya sendiri dengan self tiruan
    js += ("var __sw = { daftar: { install: [], activate: [], push: [], notificationclick: [] }, tampil: [] };\n(function () {\n"
           "var self = { addEventListener: function (n, f) { (__sw.daftar[n] = __sw.daftar[n] || []).push(f); }, skipWaiting: function () {}, clients: { claim: function () {} },\n"
           "  registration: { scope: 'https://contoh/baru/notif/', showNotification: function (j, o) { __sw.tampil.push([j, o]); return 1; } } };\n"
           + t[SWN] + "\n__sw.bacaPesan = bacaPesan;\n})();\n")
    return js


def jalankan(t):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(rakit(t) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return None, (r.stderr or r.stdout).strip()
    return json.loads(r.stdout.strip().splitlines()[-1]), ''


def periksa_statis(t):
    h = []
    def ok(nama, benar, ket=''): h.append({'nama': 'statis: ' + nama, 'ok': bool(benar), 'ket': ket})
    ok('titipan-logika hanya membaca data (impor data/toko + format), tanpa penulis', re.findall(r"^import\s[^;]*;", t[TPL], flags=re.M) == [
        "import { cacheMentah, ambilPengeluaranHarian, ambilKasbonMutasi, tolakKunciTanggal } from '../data/toko.js';", "import { RP, tanggalPendek } from '../inti/format.js';"])
    ok('panel tablet tidak menulis dokumen uang (hanya lewat tpSusunMinta / tpSusunPesan)', not re.search(r"koleksi: '(pengeluaranHarian|kasbonMutasi)'", t[TPP]) and 'TP.tpSusunMinta(d, ak(), waktu())' in t[TPP] and 'TP.tpSusunPesan(d.pesan, ak(), waktu())' in t[TPP])
    ok('kisi uangKeluar "tidak boleh" → tombol mati di tablet', "const hak = hakAkun(a, 'uangKeluar');" in t[TPP] and "hak === 'tidak'" in t[TPP])
    ok('Uang memutus lewat titipan-logika (satu pintu)', "return tpSusunPutus(id, setuju ? 'setuju' : 'tolak', setuju ? (isi || {}) : { alasan }, w);" in t[UG])
    ok('papan Persetujuan memutus titipan & pesan lewat pintu yang SAMA', "if (m.tindakan === TP_TINDAKAN) return tpSusunPutus(id, setuju ? 'setuju' : 'tolak', setuju ? {} : { alasan }, w);" in t[SL] and "if (m.tindakan === TP_PESAN) return tpSusunPutus(id, 'dibaca', { balasan: alasan }, w);" in t[SL])
    ok('setujui sekaligus mengirim SEMUA dokumen tiap putusan (bukan hanya yang pertama)', 'if (r.dokumen) r.dokumen.forEach((x) => dokumen.push(x));' in t[SL] and 'dokumen.push(r.dokumen[0])' not in t[SL])
    ok('pesan tidak ikut setujui sekaligus', "if (m.tindakan === TP_PESAN) Object.assign(b, { n: 0, sekaligus: false });" in t[SL])
    ok('penjaga kiriman akses.js: bentuk titipan & pesan = rules v13', "['toko', 'karyawan', 'kasbon'].indexOf(d.jenis) < 0" in t[AK] and 'd.teks.length > 500' in t[AK])
    ok('tutup hari menyebut titipan menunggu (rekap & layar)', 'titipan: tpMenungguSampai(iso),' in t[TH] and "'Titipan uang keluar tablet BELUM diputus · '" in t[TH] and t[UJ].count('data-k="k5-titipan"') == 3)
    ok('kartu tablet paling atas di Menu akun tablet', "${kartuTitipan(s, { akun: akunM, orang, kiniIso: hariIniIso(kini()) })}\n      <div class=\"kartu\" data-k=\"staf-akun\"" in t[MN])
    ok('Uang owner: Setujui / Betulkan / Tolak + pesan dibaca', all(x in t[UJ] for x in ('data-aksi="ukTtBetul"', 'data-aksi="ukTtSetujuBetul"', 'data-aksi="ukPesanBaca"', '${gambarTitipan(s, TT)}')))
    ok('notifikasi dalam aplikasi dipasang di app.js (pembanding, pita, lampu)', 'const baru = kbSidik(a); const ev = kbBanding(_kb, baru); _kb = baru;' in t[APP] and "if (asliAda()) lampuKejadian('owner');" in t[APP] and 'id="kabarBaru"' in t[IDX])
    ok('pita notifikasi benar-benar hilang saat hidden (display flex tidak mengalahkan [hidden])', '.kabar-baru[hidden] { display: none; }' in t[KER])
    ok('pembanding pertama hanya sesudah data lengkap', "if (!a || !a.uid || !dataLengkap()) { _kb = null; return; }" in t[APP])
    # push
    m = re.search(r'\n    match /notifOwner/\{id\} \{\n(.*?)\n    \}', t[RULES], re.S)
    ok('rules: token notifikasi owner saja', bool(m) and re.sub(r'\s+', ' ', m.group(1)).strip() == 'allow read, write: if owner();', m.group(1) if m else '')
    ok('token ditulis owner saja (firebase.js) di notifOwner/{id perangkat}', "export const KOLEKSI_NOTIF = 'notifOwner';" in t[FB] and "const ownerSaja = () => (!status.akun || status.akun.jenis !== 'owner'" in t[FB])
    ny = t[NHP][t[NHP].find('export async function nhNyalakan'):t[NHP].find('export async function nhMatikan')]
    a1 = ny.find('await Notification.requestPermission()')
    ok('izin notifikasi diminta LANGSUNG dari ketukan (await pertama)', a1 >= 0 and a1 == ny.find('await'), ny[:200])
    ok('menu: nhNyalakan dipanggil sebelum menyetel keadaan (masih di dalam ketukan)', 'nhNyala: async () => { if (st().nhSibuk) return; const p = nhNyalakan(vapidToko()); set(' in t[MN])
    cs = re.search(r"connect-src ([^;]*);", t[IDX]).group(1).split()
    ok('CSP /baru/: host pendaftaran token FCM dibuka', 'https://fcmregistrations.googleapis.com' in cs and 'https://firebaseinstallations.googleapis.com' in cs)
    fj = json.loads(t[FJ]); fn = fj.get('functions')
    ok('firebase.json: fungsi dari functions/, rules tetap firestore.rules', fj.get('firestore', {}).get('rules') == 'firestore.rules' and isinstance(fn, list) and fn and fn[0].get('source') == 'functions')
    ok('fungsi server: pemicu persetujuan baru, region dari LOKASI, pesan DATA, token mati dibuang', "onDocumentCreated('persetujuan/{id}'" in t[FIX] and "region: process.env.LOKASI || 'asia-southeast2'" in t[FIX] and 'data: { judul: p.judul, isi: p.isi, tag: p.tag, layar: p.layar },' in t[FIX] and 'mati.map((ref) => ref.delete())' in t[FIX])
    ok('fungsi server tidak menulis data toko (hanya membuang token mati)', not re.search(r"\.(set|update|add)\(", t[FIX]) and t[FIX].count('.delete()') == 1)
    ok('skrip pasang: lokasi dari database Firestore → .env, deploy fungsi saja', 'gcloud firestore databases describe' in t[PAS] and "printf 'LOKASI=%s\\n'" in t[PAS] and 'deploy --only functions' in t[PAS])
    ok('service worker notifikasi tidak menyimpan salinan halaman & tidak membaca data toko', not re.search(r"caches\.|fetch\(|firestore", t[SWN]))
    return h


def periksa(t, diam=False):
    h, galat = jalankan(t)
    if h is None:
        if not diam: print('GAGAL: jsc tidak jalan —', galat[:800])
        return False
    h = h + periksa_statis(t)
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + str(x['ket'])[:700]))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


MUTASI = [
    ('uang ditanggali hari disetujui', TPL, "const tgl = String(m.tanggal || w.tanggal); const jam = String(m.jam || w.jam);", "const tgl = String(w.tanggal); const jam = String(w.jam);"),
    ('kasbon ditulis sebagai biaya toko', TPL, "  if (jenis === 'kasbon') uang = {", "  if (false) uang = {"),
    ('menyetujui tanpa menulis uangnya', TPL, "  return { dokumen: [{ koleksi: 'persetujuan', data: baru }, uang],", "  return { dokumen: [{ koleksi: 'persetujuan', data: baru }],"),
    ('penjaga dobel dicabut', TPL, "  if (sudahDitulis(m.id)) return", "  if (false) return"),
    ('bulan terkunci tidak diperiksa', TPL, "const kunci = tolakKunciTanggal(tgl, ''); if (kunci)", "const kunci = ''; if (kunci)"),
    ('betulan owner tidak mencatat angka asli', TPL, "  if (ubah) Object.assign(baru, { koreksiOwner: true, nominalAsli:", "  if (ubah) Object.assign(baru, { koreksiOwnerX: true, nominalAsliX:"),
    ('tolak tanpa alasan diterima', TPL, "const alasan = tpPotong(o.alasan, TP_BATAS.alasan); if (!alasan) return", "const alasan = tpPotong(o.alasan, TP_BATAS.alasan) || '-'; if (!alasan) return"),
    ('titipan dikirim dua kali', TPL, "  if (ada) return { tolak: 'Titipan yang sama", "  if (false) return { tolak: 'Titipan yang sama"),
    ('nominal pecahan diterima', TPL, "  if (!/^\\d+$/.test(t)) return NaN;", "  if (!/^[\\d,]+$/.test(t)) return NaN; return Number(t.replace(',', '.'));"),
    ('titipan lama tanpa jenis ditolak', TPL, "export const tpJenis = (m) => (m && m.jenis ? String(m.jenis) : 'toko');", "export const tpJenis = (m) => (m && m.jenis ? String(m.jenis) : '');"),
    ('pesan bisa disetujui seperti uang', TPL, "    if (keputusan !== 'dibaca') return { tolak: 'Pesan hanya ditandai dibaca", "    if (false) return { tolak: 'Pesan hanya ditandai dibaca"),
    ('pesan tanpa batas panjang', TPL, "  if (t.length > TP_BATAS.pesan) return", "  if (false) return"),
    ('daftar tablet memuat milik akun lain', TPL, "const milik = (m, akun) => !!akun && String(m.mintaUid || '') === String(akun.uid || '');", "const milik = (m, akun) => !!akun;"),
    ('tutup hari menghitung titipan yang sudah diputus', TPL, "  const x = cacheMentah('persetujuan').filter((m) => m.tindakan === TP_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && (!iso", "  const x = cacheMentah('persetujuan').filter((m) => m.tindakan === TP_TINDAKAN && (!iso"),
    ('notifikasi berbunyi saat aplikasi baru dibuka', KBL, "  if (!lama || !baru || lama.owner !== baru.owner || lama.uid !== baru.uid) return [];", "  if (!baru) return []; lama = lama || { owner: baru.owner, uid: baru.uid, menunggu: {}, milik: {} };"),
    ('tablet diberi kabar milik akun lain', KBL, "    if (uid && uidPeminta(m) === uid) out.milik[id]", "    if (uid) out.milik[id]"),
    ('owner diberi kabar permintaan lama berulang', KBL, "filter((id) => !lama.menunggu[id])", "filter((id) => true)"),
    ('push untuk permintaan yang sudah diputus', PSN, "  if ((d.status || 'menunggu') !== 'menunggu') return null;", ""),
    ('push isi tanpa batas', PSN, "const pendek = (s) => (s.length > BATAS_ISI ? s.slice(0, BATAS_ISI - 1) + '…' : s);", "const pendek = (s) => s;"),
    ('lokasi multi-region tidak dipetakan', PSN, "  if (l === 'nam5' || l === 'us') return 'us-central1';", ""),
    ('SW diam saat push (tanpa notifikasi)', SWN, "  e.waitUntil(self.registration.showNotification(m.judul,", "  e.waitUntil(String(m.judul,"),
    ('SW tidak membaca pesan data FCM', SWN, "p.data && typeof p.data === 'object') ? p.data :", "false) ? p.data :"),
    ('iPhone di tab Safari dianggap bisa', NHP, "  if (ios && !mandiri) return", "  if (false) return"),
    ('izin diminta sesudah menunggu hal lain', NHP, "  let izin; try { izin = await Notification.requestPermission(); }", "  await Promise.resolve(); let izin; try { izin = await Notification.requestPermission(); }"),
    ('setujui sekaligus kembali hanya dokumen pertama', SL, 'if (r.dokumen) r.dokumen.forEach((x) => dokumen.push(x));', 'if (r.dokumen) dokumen.push(r.dokumen[0]);'),
    ('papan Persetujuan menandai titipan tanpa menulis uang', SL, "  if (m.tindakan === TP_TINDAKAN) return tpSusunPutus(id, setuju ? 'setuju' : 'tolak', setuju ? {} : { alasan }, w);\n", ''),
    ('tutup hari diam soal titipan', TH, "titipan: tpMenungguSampai(iso),", ''),
    ('rules: token notifikasi terbaca staf', RULES, "    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read, write: if owner() || staf(['ben', 'karyawan']);"),
    ('CSP kehilangan pendaftaran token', IDX, " https://fcmregistrations.googleapis.com;", ";"),
    ('fungsi server di region tetap (tidak ikut lokasi database)', FIX, "region: process.env.LOKASI || 'asia-southeast2'", "region: 'us-central1'"),
    ('fungsi server tidak membuang token mati', FIX, "  await Promise.all(mati.map((ref) => ref.delete()));\n", ''),
    ('pembanding notifikasi sebelum data lengkap', APP, "if (!a || !a.uid || !dataLengkap()) { _kb = null; return; }", "if (!a || !a.uid) { _kb = null; return; }"),
    ('pita notifikasi tidak pernah hilang', KER, '.kabar-baru[hidden] { display: none; }', ''),
    ('kartu tablet tidak dipasang di Menu', MN, "      ${kartuTitipan(s, { akun: akunM, orang, kiniIso: hariIniIso(kini()) })}\n", ''),
]


def main():
    asli = baca_semua()
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, berkas, lama, baru in MUTASI:
            if lama not in asli[berkas]: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            t = dict(asli); t[berkas] = asli[berkas].replace(lama, baru, 1)
            if periksa(t, diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(asli, diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(asli) else 1


if __name__ == '__main__':
    sys.exit(main())
