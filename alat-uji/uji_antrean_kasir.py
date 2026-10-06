#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_antrean_kasir.py — putaran 25b: ANTREAN KASIR TIDAK BOLEH MACET, di PERAMBAN SUNGGUHAN (Chrome headless) atas SALINAN kasir-darurat-nominal.html
yang dilayani lokal, dengan Firestore REST PALSU (fetch diganti sebelum skrip halaman jalan) yang menolak karcis bertanggal bulan
"terkunci" persis seperti rules v4 untuk kasir@ (403 PERMISSION_DENIED), dan bisa diatur menjawab 401 / 429 / 503 / sinyal putus.

Sampai 2 Okt 2026 skenario yang sama juga dijalankan atas kasir.html (+ buku kecil bayar bon 39b no. 4). Sejak kasir.html pensiun (owner 3 Okt
2026: halaman pengalih tanpa script, versi terakhirnya di tag git sistem-lama-terakhir) bagian itu DIHAPUS bersama objeknya, begitu juga pemeriksaan
"golonganJawaban() kembar di kedua berkas" — pasangannya hilang; perilakunya tetap diuji di peramban (403/401/429/503) atas kasir darurat.

SKENARIO:
  · karcis ke-2 dari 5 ditolak → karcis 1, 3, 4, 5 masuk; karcis 2 di daftar "ditolak" (isi utuh); layar masuk TIDAK muncul; pita tampil;
    karcis yang ditolak tidak dikirim ulang walau antrean dijalankan lagi
  · 401 (tidak dikenali) → layar masuk muncul; antrean utuh; tidak ada yang pindah ke "ditolak"
  · sinyal putus / 429 / 503 → antrean utuh, tidak ada yang "ditolak", tidak ada layar masuk; dicoba lagi → semua masuk
  · belum masuk → TIDAK ada kiriman sama sekali (403 tanpa kunci bukan penolakan aturan)
  · denyut melaporkan antrean, jumlah ditolak, dan versi (= VERSI sw-kasir.js)
  · sesudah MUAT ULANG (profil & alamat sama): karcis yang ditolak masih ada, pita masih tampil, daftarnya menyebut tanggal & nominal;
    "sudah dicatat ulang" butuh DUA ketukan dan MEMINDAH ke arsip (tidak menghapus) — pita, Tutup & tombol arsip DIKETUK (klik DOM)
  · TOMBOL SUNGGUHAN (owner 3 Okt, perkuat): papan angka, "000", + BARANG BERIKUTNYA, hapus barang (tombol innerHTML), HAPUS, KREDIT, ketik nama,
    SIMPAN — diketuk lewat klik DOM (data-aksi → jalankanAksi → AKSI), bukan fungsinya dipanggil langsung
  · CSP (owner 3 Okt, perkuat): salinan memakai CSP halaman yang SAMA — hash halaman + hash skenario uji, TANPA 'unsafe-inline' (dulu salinan
    dilonggarkan ke 'unsafe-inline', jadi handler sebaris yang tersisa tetap JALAN di uji padahal mati di HP). Tiap pemuatan: tombol KANARI
    ber-onclick sebaris wajib DIBLOKIR & tercatat (bukti CSP berlaku & pendengar hidup), dan NOL pelanggaran lain sampai skenario selesai.
STATIS: VERSI_APLIKASI kasir darurat = VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/, 25c),
        dan lantai kunci bulan KP_VERSI_KASIR_25B (kasir-v26) tidak di atas versi yang disajikan;
  service worker mengunduh versi baru melewati cache HTTP (cache:'reload'); kasir darurat memuat ulang diri saat versi baru mengambil alih;
  salinan uji peramban (dibangun TANPA peramban, teks yang sama dengan yang dimuat Chrome): script-src = hash halaman + hash skenario uji,
  tanpa 'unsafe-inline', direktif lain tetap; tiap script sesudah meta ber-hash; penjaga pelanggaran & palsu Firestore SEBELUM meta.
  (FILES service worker = berkas yang ada & tanpa kasir.html: uji_pensiun_sistem_lama.py, job uji.)
/baru/ (jsc, KOTAK PASIR — nama & angka contoh): ⛔ "semua perangkat kasir yang berdenyut 7 hari terakhir sudah versi 25b" menyebut nama perangkat
  yang tertinggal; Beranda › Perlu perhatian menyebut antrean, ditolak, dan versi lama per HP kasir.

    python3 alat-uji/uji_antrean_kasir.py                → N lulus · 0 gagal (keluar 1 bila ada yang gagal)
    python3 alat-uji/uji_antrean_kasir.py --kontrol      → tiap kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_antrean_kasir.py --gambar DIR   → juga simpan tangkapan layar kasir darurat (pita & daftar ditolak) ke DIR
Tanpa jaringan luar, tanpa Node. Butuh Google Chrome (sama dengan uji_layar_kunci.py).

HASIL LEWAT SERVER, BUKAN LEWAT DOM (27 Sep 2026, docs/catatan-uji-peramban.md): skenario mengirim hasilnya ke server uji (POST /_hasil) SEBELUM
mengabarkan selesai, jadi sebelum halaman selesai dimuat. Alat uji tidak lagi menunggu Chrome headless menyerahkan isi halaman — di runner
macOS Chrome kadang berhenti menjalankan halaman kasir darurat tepat saat mengambil DOM (6 dari 38 pemuatan di diagnosis), dan itu dulu
memicu percobaan ulang. MUAT ULANG terjadi di Chrome yang SAMA: sesudah mengirim hasil skenario utama, halaman memuat ulang dirinya
(location.replace, seperti HP penjaga memuat ulang halaman) — penyimpanan halaman tidak perlu ditulis ke disk lalu dibaca Chrome baru (di runner
Chrome yang ditutup SIGTERM tidak menulisnya: PR #43, 100 dari 100 pasangan kehilangan seluruh penyimpanan). Sesudah semua hasil masuk Chrome
ditutup baik-baik (SIGTERM); yang menolak dalam 10 dtk dimatikan paksa dan dihitung di STAT['chrome_ditutup_paksa'].
"""
import os, re, sys, json, time, shutil, signal, socket, tempfile, threading, subprocess, http.server, socketserver, functools, urllib.parse
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import coba_ulang   # noqa: E402  (tiap percobaan ulang menulis baris DICOBA ULANG — keputusan owner 26 Sep)
import uji_csp      # noqa: E402  (owner 3 Okt, perkuat: hash salinan uji dihitung dengan cara yang SAMA dengan --pasang)
import contextlib   # noqa: E402
CHROME = next((p for p in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'] if os.path.exists(p)), None)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
DARURAT = 'kasir-darurat-nominal.html'

# ---------- PENJAGA CSP (owner 3 Okt, perkuat): disisip PALING AWAL di <head>, SEBELUM meta CSP → tidak terkena CSP ----------
# Salinan uji memakai CSP halaman yang SAMA (csp_salinan: hash halaman + hash skenario uji, TANPA 'unsafe-inline'). Tiap yang diblokir peramban —
# handler sebaris di tombol, script tanpa hash, koneksi/gambar di luar daftar — dicatat lewat 'securitypolicyviolation'; skenario wajib berakhir
# dengan NOL. KANARI: satu tombol ber-onclick sebaris dibuat & diketuk di awal tiap pemuatan; handlernya WAJIB diblokir dan tercatat — bukti CSP
# berlaku di salinan (tidak dilonggarkan) dan pendengarnya hidup. Tanpa kanari, "nol pelanggaran" ikut lulus kalau pendengarnya mati.
# Dipakai juga uji_katalog_kasir.py.
PENJAGA_CSP = r"""<script>
(function () {
  var C = window.__csp = { pelanggaran: [], sedangKanari: false };
  document.addEventListener('securitypolicyviolation', function (e) {
    C.pelanggaran.push({ arahan: String(e.effectiveDirective || e.violatedDirective || ''), diblokir: String(e.blockedURI || ''), baris: e.lineNumber || 0, kanari: C.sedangKanari });
  });
  C.kanari = async function () {
    var n = C.pelanggaran.length, t0 = Date.now(), b = document.createElement('button');
    C.sedangKanari = true;
    b.type = 'button'; b.style.display = 'none'; b.setAttribute('onclick', 'window.__kanariJalan = true');
    document.body.appendChild(b); b.click();
    while (C.pelanggaran.length === n && Date.now() - t0 < 3000) await new Promise(function (r) { setTimeout(r, 30); });
    await new Promise(function (r) { setTimeout(r, 100); });
    C.sedangKanari = false; b.parentNode.removeChild(b);
    var k = C.pelanggaran.slice(n);
    return { tercatat: k.length, jalan: !!window.__kanariJalan, arahan: k.map(function (x) { return x.arahan; }) };
  };
  C.lain = function () { return C.pelanggaran.filter(function (x) { return !x.kanari; }); };
})();
</script>"""

# ---------- Firestore REST PALSU: dipasang PALING AWAL di <head> (sesudah PENJAGA_CSP), sebelum skrip halaman ----------
KEPALA = r"""<script>
(function () {
  try { delete Navigator.prototype.serviceWorker; } catch (e) {}   // tanpa service worker: yang diuji berkasnya, bukan cache
  var P = window.__palsu = { jaringan: true, mode: 'ok', sampaiBulan: '2026-08', masuk: [], permintaan: [], denyut: [], tanpaKunci: 0 };
  var TOLAK = { error: { code: 403, message: 'Missing or insufficient permissions.', status: 'PERMISSION_DENIED' } };
  function jawab(status, isi) { return Promise.resolve(new Response(JSON.stringify(isi || {}), { status: status, headers: { 'Content-Type': 'application/json' } })); }
  function nilai(v) { if (!v) return null; if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return v.doubleValue;
    if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null; if ('mapValue' in v) { var o = {}, f = v.mapValue.fields || {}; for (var k in f) o[k] = nilai(f[k]); return o; } return null; }
  var asli = window.fetch.bind(window);
  window.fetch = function (url, opsi) {
    url = String(url); opsi = opsi || {};
    if (url.charAt(0) === '/' || url.indexOf(location.origin) === 0) return asli(url, opsi);   // server uji (/_siap), bukan Firestore
    if (!P.jaringan) return Promise.reject(new TypeError('Failed to fetch'));
    if (url.indexOf('securetoken.googleapis.com') >= 0) return jawab(200, { id_token: 't-uji-segar', refresh_token: 'r-uji', expires_in: '3600' });
    if (url.indexOf('identitytoolkit.googleapis.com') >= 0) return jawab(200, { idToken: 't-uji', refreshToken: 'r-uji', expiresIn: '3600' });
    var m = /\/documents\/([^/?]+)\/([^?]+)/.exec(url); if (!m) return jawab(404, {});
    var koleksi = m[1], id = decodeURIComponent(m[2]), metode = String(opsi.method || 'GET').toUpperCase();
    var kunci = !!(opsi.headers && opsi.headers.Authorization);
    if (metode === 'GET') {
      // 39b no. 4: katalog ringkasanKasir/aktif dilayani dari localStorage '__uji_katalog' { waktu (updateTime server), isi } — lewat keFs halaman itu sendiri
      var kat = null; try { kat = koleksi === 'ringkasanKasir' ? JSON.parse(localStorage.getItem('__uji_katalog') || 'null') : null; } catch (e) {}
      if (kat && typeof keFs === 'function') { var fk = {}; for (var kk in kat.isi) fk[kk] = keFs(kat.isi[kk]); return jawab(200, { name: 'katalog', fields: fk, updateTime: kat.waktu }); }
      return jawab(404, { error: { code: 404, status: 'NOT_FOUND' } });
    }
    var data = {}; try { var f = JSON.parse(opsi.body).fields || {}; for (var k in f) data[k] = nilai(f[k]); } catch (e) {}
    if (koleksi === 'perangkatStatus') { P.denyut.push(data); return jawab(200, {}); }
    P.permintaan.push({ koleksi: koleksi, id: id, kunci: kunci, hargaTotal: data.hargaTotal, tanggal: data.tanggal });
    if (!kunci) { P.tanpaKunci++; return jawab(403, TOLAK); }                        // server sungguhan: request.auth == null → ditolak rules
    if (P.mode === '401') return jawab(401, { error: { code: 401, message: 'Request had invalid authentication credentials.', status: 'UNAUTHENTICATED' } });
    if (P.mode === '429') return jawab(429, { error: { code: 429, message: 'Quota exceeded.', status: 'RESOURCE_EXHAUSTED' } });
    if (P.mode === '503') return jawab(503, { error: { code: 503, message: 'The service is currently unavailable.', status: 'UNAVAILABLE' } });
    if (P.sampaiBulan && String(data.tanggal || '').slice(0, 7) <= P.sampaiBulan) return jawab(403, TOLAK);   // rules v4 kasir@: tglBaru di bulan terkunci
    P.masuk.push({ koleksi: koleksi, id: id, hargaTotal: data.hargaTotal, tanggal: data.tanggal, nominal: data.nominal, nama: data.namaPelanggan, cara: data.caraBayar });
    return jawab(200, koleksi === 'piutangMutasi' ? { name: 'dok', fields: {}, updateTime: '2026-09-30T03:00:00.000000Z' } : { name: 'dok', fields: {} });
  };
})();
</script>"""

# ---------- penyesuai per berkas: cara mencatat, kunci penyimpanan, denyut (kasir.html pensiun 3 Okt 2026 — tinggal kasir darurat) ----------
PENYESUAI = {
    DARURAT: r"""var A = { antrean: 'darurat_antrean_v1', gagal: 'darurat_gagal_v1', arsip: 'darurat_ditolak_arsip_v1', auth: 'kasir_auth_v1',
  catat: function (n) { String(n).split('').forEach(function (c) { tekanAngka(c); }); simpanNominal(); },   // fungsi papan angka + SIMPAN (ketukan: ketukTombol)
  catatLama: function (n, tgl) { var a = JSON.parse(localStorage.getItem(this.antrean) || '[]'); var id = Date.now() + Math.random();   // karcis yang tertahan offline sejak bulan lalu
    a.push({ koleksi: 'penjualan', docId: String(id), data: { id: id, tanggal: tgl, jam: '20:15', jenis: 'kasir_darurat_nominal', namaProduk: '(tidak tercatat — kasir darurat)', hargaTotal: n,
      caraBayar: 'Tunai', namaPelanggan: '', grupNota: id, oleh: '(darurat tanpa nama)', perangkat: 'd-uji' } }); localStorage.setItem(this.antrean, JSON.stringify(a)); },
  denyut: function () { denyutTerakhirD = 0; kirimDenyutD(); } };""",
}

SKENARIO = r"""<script>
(async function () {
  __PENYESUAI__
  var tunggu = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var sampai = async function (f, ms) { var t0 = Date.now(); while (Date.now() - t0 < (ms || 6000)) { try { if (f()) return true; } catch (e) {} await tunggu(30); } return false; };
  var P = window.__palsu; var hasil = { skenario: {} };
  var L = function (k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return null; } };
  var tampil = function (id) { var e = document.getElementById(id); return !!e && e.classList.contains('tampil'); };
  // owner 3 Okt (perkuat): KETUK = klik DOM pada elemen yang tampil di HP (data-aksi → jalankanAksi → AKSI), bukan fungsinya dipanggil langsung
  var ketuk = function (sel) { var el = document.querySelector(sel); if (!el) throw new Error('tidak ada di layar: ' + sel); el.click(); };
  var reset = function (masuk) { [A.antrean, A.gagal, A.arsip].forEach(function (k) { localStorage.removeItem(k); });
    if (masuk) localStorage.setItem(A.auth, JSON.stringify({ refreshToken: 'r-uji', idToken: 't-uji', kedaluwarsa: Date.now() + 3600000 })); else localStorage.removeItem(A.auth);
    P.masuk = []; P.permintaan = []; P.denyut = []; P.tanpaKunci = 0; P.jaringan = true; P.mode = 'ok';
    document.querySelectorAll('.lapisan.tampil').forEach(function (e) { e.classList.remove('tampil'); }); };
  var diam = async function () { await sampai(function () { return !window.sedangKirim; }, 6000); await tunggu(150); };
  var kosong = function () { return sampai(function () { return L(A.antrean).length === 0; }, 6000); };
  var potret = function () { var pita = document.getElementById('pitaDitolak');
    return { antrean: L(A.antrean).map(function (x) { return x.data.hargaTotal; }),
      ditolak: L(A.gagal).map(function (x) { return { h: x.data && x.data.hargaTotal, t: x.data && x.data.tanggal, alasan: x.ditolak && x.ditolak.alasan, status: x.ditolak && x.ditolak.status }; }),
      arsip: L(A.arsip).map(function (x) { return x.data && x.data.hargaTotal; }), masuk: P.masuk.map(function (x) { return x.hargaTotal; }), login: tampil('layarLogin'),
      pita: pita && getComputedStyle(pita).display !== 'none' ? pita.textContent : '', chip: document.getElementById('chipStatus').textContent,
      permintaan: P.permintaan.map(function (x) { return x.hargaTotal; }), tanpaKunci: P.tanpaKunci }; };
  try {
    var s = new URLSearchParams(location.search).get('s') || 'utama';
    hasil.kanari = window.__csp ? await window.__csp.kanari() : null;   // CSP halaman berlaku di salinan & pendengar pelanggaran hidup
    if (s === 'utama') {
      reset(true); P.jaringan = false; A.catat(1100); A.catat(1200); A.catat(1300); kirimAntrean(true); await diam(); hasil.skenario.jaringanPutus = potret();
      P.jaringan = true; kirimAntrean(true); await kosong(); await diam(); hasil.skenario.jaringanPulih = potret();
      reset(true); P.jaringan = false; A.catat(2100); A.catat(2200); P.jaringan = true; P.mode = '429'; kirimAntrean(true); await diam(); hasil.skenario.sibuk429 = potret();
      P.mode = '503'; kirimAntrean(true); await diam(); hasil.skenario.sibuk503 = potret();
      P.mode = 'ok'; kirimAntrean(true); await kosong(); await diam(); hasil.skenario.sibukPulih = potret();
      reset(true); P.jaringan = false; A.catat(3100); A.catat(3200); P.jaringan = true; P.mode = '401'; kirimAntrean(true); await sampai(function () { return tampil('layarLogin'); }, 3000); await diam();
      hasil.skenario.tidakDikenal401 = potret();
      reset(false); P.jaringan = false; A.catat(4100); A.catat(4200); P.jaringan = true; kirimAntrean(true); await diam();
      await tunggu(1700);   // kasir darurat membuka layar masuk 1,3 detik sesudah SIMPAN kalau belum masuk — tunggu di sini, jangan sampai jatuh ke skenario berikutnya
      hasil.skenario.belumMasuk = potret();
      // owner 3 Okt (perkuat): TOMBOL SUNGGUHAN diketuk lewat klik DOM di bawah CSP halaman yang sama (tanpa 'unsafe-inline') — handler sebaris
      // yang tersisa di tombol akan mati diam-diam di sini (dan tercatat sebagai pelanggaran). Hasilnya = yang dulu dicapai fungsi langsung.
      reset(true); P.jaringan = false;
      var K = {}, nama = document.getElementById('namaPembeliD');
      var lcd = function () { return document.getElementById('lcdAngka').textContent.replace(/\D/g, ''); };
      var nBaris = function () { return document.querySelectorAll('#daftarBaris [data-aksi="hapusBaris"]').length; };
      var papan = function (v) { ketuk('#papan [data-aksi="angka"][data-nilai="' + v + '"]'); };
      papan('7'); papan('000'); K.lcdTujuhRibu = lcd();
      ketuk('#btnTambahBaris'); papan('9'); papan('9'); ketuk('#btnTambahBaris'); K.barisDua = nBaris();
      ketuk('#daftarBaris [data-aksi="hapusBaris"][data-nilai="1"]'); K.barisSesudahHapus = nBaris();
      papan('1'); papan('2'); papan('5'); ketuk('#papan [data-aksi="hapusAngka"]'); papan('0'); papan('0'); K.lcdSeribuDuaRatus = lcd();
      ketuk('#bayarD-Kredit'); K.kreditTerpilih = document.getElementById('bayarD-Kredit').classList.contains('pilih');
      ketuk('#btnSimpan'); K.tanpaNama = { antrean: L(A.antrean).length, kurang: nama.classList.contains('kurang') };
      nama.value = 'Pembeli Uji'; nama.dispatchEvent(new Event('input', { bubbles: true })); K.sesudahKetikKurang = nama.classList.contains('kurang');
      ketuk('#btnSimpan');
      K.antrean = L(A.antrean).map(function (x) { return [x.data.hargaTotal, x.data.caraBayar, x.data.namaPelanggan]; });
      K.satuNota = L(A.antrean).length === 2 && L(A.antrean)[0].data.grupNota === L(A.antrean)[1].data.grupNota;
      K.sesudahSimpan = { nama: nama.value, tunai: document.getElementById('bayarD-Tunai').classList.contains('pilih') };
      await diam(); P.jaringan = true; kirimAntrean(true); await kosong(); await diam();
      K.masuk = P.masuk.map(function (x) { return [x.hargaTotal, x.cara, x.nama]; });
      hasil.skenario.ketukTombol = K;
      // PALING AKHIR: karcis ke-2 dari 5 bertanggal bulan terkunci — sisanya dibaca lagi sesudah muat ulang
      reset(true); P.jaringan = false; A.catat(5100); A.catatLama(5200, '2026-08-31'); A.catat(5300); A.catat(5400); A.catat(5500);
      hasil.antreanAwal = L(A.antrean).map(function (x) { return x.data.hargaTotal; });
      P.jaringan = true; kirimAntrean(true); await kosong(); await diam();
      kirimAntrean(false); await diam(); kirimAntrean(true); await diam();
      hasil.skenario.keduaDitolak = potret();
      A.denyut(); await sampai(function () { return P.denyut.length > 0; }, 3000); hasil.denyut = P.denyut[P.denyut.length - 1] || null;
    } else if (s === 'gambarDaftar') {
      await tunggu(300); bukaDaftarDitolak();
    } else if (s === 'muatUlang') {
      await tunggu(400); hasil.skenario.sesudahMuatUlang = potret();
      // owner 3 Okt (perkuat): pita, Tutup & tombol arsip DIKETUK lewat klik DOM — dulu bukaDaftarDitolak() / arsipkanDitolak() dipanggil langsung
      ketuk('#pitaDitolak'); hasil.daftarTeks = document.getElementById('isiDitolak').innerText; hasil.daftarTampil = tampil('layarDitolak');
      ketuk('#layarDitolak [data-aksi="tutupDitolak"]'); hasil.sesudahTutup = tampil('layarDitolak');
      ketuk('#pitaDitolak'); ketuk('#btnArsipDitolak'); hasil.sesudahSatuKetuk = potret(); ketuk('#btnArsipDitolak'); hasil.sesudahDuaKetuk = potret();
      hasil.versiLayar = document.getElementById('versiApp').textContent;
    } else { await tunggu(300); }
  } catch (e) { hasil.galat = String(e && (e.stack || e.message) || e); }
  await tunggu(100);   // pelanggaran CSP dikabarkan peramban sebagai tugas tersendiri — beri waktu sebelum dihitung
  hasil.cspLain = window.__csp ? window.__csp.lain() : null;
  // hasil dikirim LANGSUNG ke server uji (per skenario), sebelum /_siap — jadi sebelum halaman selesai dimuat, tidak lewat DOM yang harus
  // diserahkan Chrome. ?lanjut= → muat ulang di Chrome yang SAMA (seperti HP penjaga memuat ulang halaman), penyimpanan halaman ikut.
  try { await fetch('/_hasil' + location.search, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(hasil) }); } catch (e) {}
  fetch('/_siap');
  var lanjut = new URLSearchParams(location.search).get('lanjut');
  if (lanjut) location.replace(lanjut);
})();
</script>"""


# ---------- server lokal: /_tahan menahan event load sampai skenario selesai (/_siap) ----------
class Pelayan(http.server.SimpleHTTPRequestHandler):
    keadaan = None
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/_siap'):
            self.keadaan['siap'].set(); self.send_response(204); self.end_headers(); return
        if self.path.startswith('/_tahan'):
            self.keadaan['siap'].wait(45); time.sleep(0.4)   # halaman sehat mengabarkan selesai dalam hitungan detik, juga di runner CI
            try: self.send_response(200); self.send_header('Content-Type', 'image/gif'); self.end_headers()
            except (BrokenPipeError, ConnectionResetError): return   # Chrome sudah ditutup begitu hasil masuk — gambar penahan tidak ditunggu lagi
            try: self.wfile.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
            except (BrokenPipeError, ConnectionResetError): pass
            return
        return super().do_GET()
    def do_POST(self):
        if self.path.startswith('/_hasil'):   # hasil skenario, dikirim halaman sebelum /_siap; kuncinya ?s= (kosong kalau tidak ada)
            n = int(self.headers.get('Content-Length') or 0); isi = self.rfile.read(n).decode('utf-8', 'replace')
            self.keadaan['hasil_per'][_kunci_skenario(self.path)] = isi
            self.send_response(204); self.end_headers(); return
        self.send_response(404); self.end_headers()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()


def _kunci_skenario(jalur):
    """'/berkas.html?s=utama&lanjut=…' → 'utama'; tanpa ?s= → ''."""
    return urllib.parse.parse_qs(urllib.parse.urlsplit(jalur).query).get('s', [''])[0]


def csp_salinan(t, suntikan, asli=None):
    """CSP SALINAN UJI kasir darurat (owner 3 Okt, perkuat — menggantikan longgarkan_csp, yang mengganti script-src salinan dengan 'unsafe-inline':
    handler sebaris yang tersisa tetap JALAN di uji padahal mati di HP penjaga, dan hash halaman tidak pernah diuji peramban).
    script-src salinan = hash halaman + hash tiap script di `suntikan` (skenario uji yang disisip SESUDAH meta), TANPA 'unsafe-inline' — peramban
    menegakkan CSP yang sama dengan HP penjaga. Hash halaman dipakai APA ADANYA; hanya dihitung ulang (uji_csp.tulis_hash, cara yang sama dengan
    --pasang) kalau salinan diubah kontrol (t != asli), supaya yang berbunyi cacat yang dituju, bukan hash basi. Yang disisip SEBELUM meta
    (PENJAGA_CSP, palsu Firestore) tidak terkena CSP dan tidak perlu hash. Direktif lain TETAP."""
    pola = r'<meta http-equiv="Content-Security-Policy" content="[^"]*?script-src [^;"]*'
    assert re.search(pola, t), 'meta CSP kasir darurat tanpa script-src — perbarui uji'
    if asli is not None and t != asli: t = uji_csp.tulis_hash(t)
    m = re.search(pola, t); ada = m.group(0).split()
    return t[:m.end()] + ''.join(' ' + h for h in uji_csp.hash_sebaris(suntikan) if h not in ada) + t[m.end():]


def salinan(t, berkas=DARURAT, asli=None):
    """Teks salinan uji peramban — TANPA menulis atau menyalakan apa pun (dipakai siapkan DAN pemeriksaan statis): PENJAGA_CSP + palsu Firestore
    tepat sesudah <head> (SEBELUM meta CSP), skenario + penahan sebelum </body>, CSP salinan = hash halaman + hash skenario (csp_salinan)."""
    assert t.count('<head>') == 1 and t.count('</body>') == 1
    skenario = SKENARIO.replace('__PENYESUAI__', PENYESUAI[berkas])
    t = csp_salinan(t, skenario, asli)
    return t.replace('<head>', '<head>' + PENJAGA_CSP + KEPALA, 1).replace('</body>', skenario + "<img src='/_tahan' alt='' style='display:none'></body>", 1)


def siapkan(berkas, ganti=None):
    """Folder kerja berisi salinan berkas kasir yang disuntik (salinan()). ganti = [(lama, baru)] untuk kontrol."""
    d = tempfile.mkdtemp(prefix='antre-'); asli = open(os.path.join(AKAR, berkas), encoding='utf-8').read(); t = asli
    for lama, baru in (ganti or []):
        assert lama in t, 'kontrol basi: ' + berkas + ' · ' + lama[:70]; t = t.replace(lama, baru)
    open(os.path.join(d, berkas), 'w', encoding='utf-8').write(salinan(t, berkas, asli))
    return d


@contextlib.contextmanager
def ganti_alat(alat, modul=None):
    """Kontrol atas ALAT UJI ini sendiri (owner 3 Okt, perkuat): {nama global: [(lama, baru)] untuk teks | fungsi pengganti}, dipulihkan sesudahnya.
    modul = modul tempat global itu (bawaan: modul ini; uji_katalog_kasir memberi modul uji_antrean_kasir yang diimpornya)."""
    g = vars(modul) if modul else globals(); simpan = {}
    try:
        for n, v in (alat or {}).items():
            simpan[n] = g[n]
            if callable(v): g[n] = v; continue
            t = g[n]
            for lama, baru in v:
                assert lama in t, 'kontrol basi (alat): ' + n + ' · ' + lama[:70]; t = t.replace(lama, baru)
            g[n] = t
        yield
    finally:
        g.update(simpan)


def _salinan_longgar(t, suntikan, asli=None):
    """PERUSAK untuk kontrol: cara lama (script-src salinan = 'unsafe-inline', hash dibuang)."""
    return re.sub(r"script-src [^;]*;", "script-src 'unsafe-inline';", t, count=1)


def _ikat_tanpa_dns(self):
    """Pengganti HTTPServer.server_bind: bawaannya menanyakan nama host 127.0.0.1 ke DNS (socket.getfqdn) tiap server dinyalakan, dan di
    runner macOS pertanyaan itu menggantung ±35 dtk (PR #42: tiap kasus uji_coba_ulang 35,7 dtk di CI, 0,7 dtk di Mac pengembang)."""
    socketserver.TCPServer.server_bind(self)
    self.server_name, self.server_port = self.server_address[:2]


def layani(d):
    t0 = time.time()
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    keadaan = {'siap': threading.Event(), 'hasil_per': {}}
    kelas = type('PelayanRun', (Pelayan,), {'keadaan': keadaan})
    Srv = type('SrvAntre', (http.server.ThreadingHTTPServer,), {'request_queue_size': 64, 'daemon_threads': True, 'server_bind': _ikat_tanpa_dns})
    srv = Srv(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    if os.environ.get('CI'): print('  [peramban] server uji menyala %.1f dtk' % (time.time() - t0), file=sys.stderr, flush=True)
    return srv, port, keadaan


# Penyimpanan yang bisa DIUBAH skenario halaman (kasir: localStorage). Difoto sebelum percobaan pertama, dipulihkan sebelum tiap percobaan ulang.
PENYIMPANAN_HALAMAN = [os.path.join('Default', 'Local Storage'), os.path.join('Default', 'IndexedDB')]


def _salin_penyimpanan(dari, ke):
    """Ganti penyimpanan halaman di profil `ke` dengan milik `dari` (yang tidak ada di `dari` = dihapus dari `ke`). Chrome sudah mati."""
    for rel in PENYIMPANAN_HALAMAN:
        a, b = os.path.join(dari, rel), os.path.join(ke, rel)
        shutil.rmtree(b, ignore_errors=True)
        if os.path.isdir(a): shutil.copytree(a, b)


def buka(port, keadaan, profil, jalur, gambar=None, tunggu=60, lalu=None):
    """Satu pemuatan halaman di Chrome headless. → teks JSON hasil skenario (dikirim halaman ke POST /_hasil); gambar = berkas PNG (tangkapan
    layar). lalu = jalur pemuatan BERIKUTNYA di Chrome yang SAMA (halaman memuat ulang dirinya sesudah mengirim hasil) → (hasil, hasil_lalu). Isi halaman (DOM) TIDAK dibutuhkan: Chrome headless di runner macOS kadang berhenti menjalankan halaman tepat saat mengambil DOM
    (docs/catatan-uji-peramban.md), dan hasil yang sudah masuk tidak terpengaruh. Yang dicoba SEKALI lagi hanya halaman yang TIDAK mengirim
    hasil (Chrome macet total sebelum skenario selesai, PR #41: 2 dari ±60 pemuatan).
    Percobaan yang gagal bisa sudah menjalankan sebagian skenarionya dan MENGUBAH penyimpanan (PR #42: skenario muat ulang sudah mengarsipkan
    karcis → percobaan ulang gagal palsu; di skenario lain bisa lulus palsu). Maka penyimpanan halaman difoto SEBELUM percobaan pertama dan
    dipulihkan sebelum tiap percobaan ulang: percobaan ulang mulai dari keadaan yang sama persis dengan percobaan pertama.
    Tiap percobaan ulang menulis baris DICOBA ULANG (coba_ulang.py): kalau mulai sering muncul, itu masalah sungguhan, bukan Chrome yang lambat."""
    BATAS = 2
    foto = tempfile.mkdtemp(prefix='antre-foto-'); _salin_penyimpanan(profil, foto)
    try:
        return _buka_dengan_ulang(port, keadaan, profil, jalur, gambar, tunggu, foto, BATAS, lalu)
    finally:
        shutil.rmtree(foto, ignore_errors=True)


def _buka_dengan_ulang(port, keadaan, profil, jalur, gambar, tunggu, foto, BATAS, lalu=None):
    h = ''; sebab = ''
    for coba in range(1, BATAS + 1):
        if coba > 1:
            coba_ulang.catat(jalur, sebab, coba, BATAS, log=coba_ulang.ekor_berkas(keadaan.get('log_chrome', '')))
            _salin_penyimpanan(foto, profil)   # mulai lagi dari keadaan SEBELUM percobaan pertama
        for kunci in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):   # kunci profil sisa Chrome yang sudah dimatikan
            try:
                if os.path.lexists(os.path.join(profil, kunci)): os.unlink(os.path.join(profil, kunci))
            except OSError: pass
        h = _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu, lalu)
        if gambar or not keadaan['hasil_kurang']: return h
        sebab = 'halaman tidak mengirim hasil' + (' (%s)' % ', '.join(keadaan['hasil_kurang']) if lalu else
                                                  ' (tapi mengabarkan selesai)' if keadaan['siap'].is_set() else '')
    print('  [peramban] %s %s — percobaan terakhir (%d dari %d), tidak diulang lagi' % (jalur, sebab, BATAS, BATAS), file=sys.stderr, flush=True)
    return h


# Hitungan per proses (dibaca beban_kasir_darurat.py & dicetak di CI): peluncuran Chrome, pemuatan halaman, dan Chrome yang tidak mau ditutup
# baik-baik sesudah semua hasil masuk.
STAT = {'muat': 0, 'halaman': 0, 'chrome_ditutup_paksa': 0}


def _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu, lalu=None):
    kunci = [_kunci_skenario(j) for j in ([jalur] + ([lalu] if lalu else []))]
    keadaan['siap'] = threading.Event(); keadaan['hasil_per'] = {}; keadaan['hasil_kurang'] = kunci; keadaan['ditutup_paksa'] = False
    alamat = jalur + (('&' if '?' in jalur else '?') + 'lanjut=' + urllib.parse.quote(lalu, safe='') if lalu else '')
    arg = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
           '--user-data-dir=' + profil, '--window-size=500,900', '--hide-scrollbars',
           '--use-mock-keychain', '--password-store=basic']   # macOS tanpa layar: jangan menunggu keychain sungguhan
    # TANPA --dump-dom: DOM tidak dibutuhkan (hasil datang lewat POST /_hasil), dan dalam mode --dump-dom Chrome di macOS mengabaikan SIGTERM
    # (uji lokal 27 Sep: 22 dari 22 tidak mau ditutup baik-baik 10 dtk). Tanpa mode itu Chrome headless jalan seperti peramban biasa.
    arg += (['--screenshot=' + gambar] if gambar else [])
    # catatan Chrome (stderr) ke berkas di profil — dibaca HANYA kalau percobaan ini gagal dan halaman dicoba ulang (bukti di bawah baris DICOBA ULANG)
    keadaan['log_chrome'] = os.path.join(profil, 'log-chrome-%d.txt' % int(time.time() * 1000))
    log = open(keadaan['log_chrome'], 'wb')
    p = subprocess.Popen(arg + ['--enable-logging=stderr', 'http://127.0.0.1:%d%s' % (port, alamat)], stdout=subprocess.DEVNULL, stderr=log,
                         start_new_session=True)   # grup proses sendiri: dimatikan SEKALIGUS (renderer, GPU, penyimpanan), bukan cuma induknya
    log.close()
    STAT['muat'] += 1; STAT['halaman'] += len(kunci)
    t0 = time.time()
    try:
        if gambar:
            while time.time() - t0 < tunggu and p.poll() is None and not (os.path.exists(gambar) and os.path.getsize(gambar) > 0): time.sleep(0.2)
            time.sleep(0.3); return ''
        # Tunggu HASIL (semua skenario rangkaian), bukan DOM. Chrome yang keluar sebelum hasil lengkap = gagal (tidak menunggu sisa `tunggu`).
        kurang = lambda: [k for k in kunci if k not in keadaan['hasil_per']]
        while kurang() and time.time() - t0 < tunggu and p.poll() is None: time.sleep(0.1)
        keadaan['hasil_kurang'] = kurang()
        if keadaan['hasil_kurang']: return ('', '') if lalu else ''
        # Hasil sudah di tangan. Chrome TIDAK ditunggu menyerahkan DOM atau keluar sendiri: di macOS ia sering tidak keluar sendiri, dan kadang
        # berhenti menjalankan halaman saat mengambil DOM (docs/catatan-uji-peramban.md). Tutup baik-baik (SIGTERM); tidak mau ditutup dalam
        # 10 dtk → dihitung, lalu grupnya dimatikan paksa. Penyimpanan halaman TIDAK diandalkan tertulis ke disk (lihat kepala berkas).
        try:
            os.kill(p.pid, signal.SIGTERM); p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            keadaan['ditutup_paksa'] = True; STAT['chrome_ditutup_paksa'] += 1
        except ProcessLookupError: pass
        h = [keadaan['hasil_per'][k] for k in kunci]
        return tuple(h) if lalu else h[0]
    finally:
        try: os.killpg(p.pid, signal.SIGKILL)   # sisa proses Chrome tidak boleh ikut menulis ke profil yang dipakai pemuatan berikutnya
        except (ProcessLookupError, PermissionError): p.kill()
        p.wait()
        if os.environ.get('CI'):
            ket = ' · Chrome tidak mau ditutup baik-baik 10 dtk sesudah hasil masuk → dimatikan paksa (bukan percobaan ulang)' if keadaan['ditutup_paksa'] else ''
            if not gambar and keadaan['hasil_kurang']: ket = ' · halaman TIDAK mengirim hasil (%s)' % ', '.join(k or '-' for k in keadaan['hasil_kurang'])
            print('  [peramban] %s%s %.1f dtk%s' % (jalur, ' → ' + lalu if lalu else '', time.time() - t0, ket), file=sys.stderr, flush=True)


def teks_stat():
    return 'peluncuran Chrome %d · pemuatan halaman %d · Chrome yang tidak mau ditutup baik-baik sesudah hasil masuk (dimatikan paksa): %d' % (
        STAT['muat'], STAT['halaman'], STAT['chrome_ditutup_paksa'])


def hasil_dari(h):
    """Teks JSON dari POST /_hasil → dict; kosong / rusak → None (pemeriksa melaporkan 'tidak ada hasil')."""
    try: return json.loads(h) if h else None
    except ValueError: return None


def jalankan_berkas(berkas, ganti=None, gambar_dir=None):
    """→ (hasil utama, hasil muat ulang) untuk satu berkas. Muat ulang di Chrome yang SAMA (halaman memuat ulang dirinya, localStorage ikut,
    seperti HP penjaga memuat ulang halaman). --gambar (pemeriksaan mata di Mac, bukan CI) memakai jalur lama: tiap pemuatan Chrome sendiri,
    bergantung pada Chrome menulis penyimpanan ke disk (di runner itu tidak terjadi)."""
    d = siapkan(berkas, ganti); srv, port, keadaan = layani(d); profil = tempfile.mkdtemp(prefix='antre-profil-')
    try:
        if not gambar_dir:
            u, m = buka(port, keadaan, profil, '/' + berkas + '?s=utama', lalu='/' + berkas + '?s=muatUlang')
            return hasil_dari(u), hasil_dari(m)
        u = hasil_dari(buka(port, keadaan, profil, '/' + berkas + '?s=utama'))
        if u:
            os.makedirs(gambar_dir, exist_ok=True); dasar = os.path.splitext(berkas)[0]
            buka(port, keadaan, profil, '/' + berkas + '?s=gambar', gambar=os.path.join(gambar_dir, dasar + '-pita-ditolak.png'))
            buka(port, keadaan, profil, '/' + berkas + '?s=gambarDaftar', gambar=os.path.join(gambar_dir, dasar + '-daftar-ditolak.png'))
        m = hasil_dari(buka(port, keadaan, profil, '/' + berkas + '?s=muatUlang'))
        return u, m
    finally:
        srv.shutdown(); shutil.rmtree(profil, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)


def periksa_csp(ok, label, h):
    """owner 3 Okt (perkuat): CSP halaman BERLAKU di salinan uji (kanari ber-onclick sebaris diblokir & tercatat, tidak jalan) dan NOL pelanggaran
    lain sepanjang pemuatan. Dipakai juga uji_katalog_kasir.py. h = hasil satu pemuatan (dict)."""
    k = h.get('kanari') or {}
    ok(label + ': CSP halaman berlaku di salinan uji — tombol KANARI ber-onclick sebaris DIBLOKIR & tercatat (pendengar pelanggaran hidup)',
       k.get('tercatat', 0) >= 1 and k.get('jalan') is False and all(str(a).startswith('script-src') for a in (k.get('arahan') or ['?'])), k)
    ok(label + ': NOL pelanggaran CSP selain kanari (hash halaman & skenario, tombol yang diketuk, koneksi, gambar)', h.get('cspLain') == [], h.get('cspLain'))


def periksa_peramban(berkas, u, m, versi_sw):
    """→ [(nama, lulus, keterangan)] untuk satu berkas."""
    kata = 'karcis' if berkas == DARURAT else 'catatan'
    out = []; ok = lambda n, c, k='': out.append((berkas + ' · ' + n, bool(c), k))
    if not u or u.get('galat'):
        return [(berkas + ' · skenario utama jalan', False, {'galat': (u or {}).get('galat', 'tidak ada hasil (halaman tidak jalan)'), 'cspLain': (u or {}).get('cspLain')})]
    periksa_csp(ok, 'utama', u)
    S = u['skenario']
    j = S['jaringanPutus']; ok('sinyal putus: antrean utuh (3), tidak ada yang "ditolak", layar masuk tidak muncul', j['antrean'] == [1100, 1200, 1300] and not j['ditolak'] and not j['login'], j)
    j = S['jaringanPulih']; ok('sinyal kembali → dicoba lagi → ketiganya masuk berurutan, antrean kosong', j['masuk'] == [1100, 1200, 1300] and not j['antrean'] and not j['ditolak'], j)
    for k, n in (('sibuk429', '429 (kuota / sibuk)'), ('sibuk503', '503 (server galat)')):
        j = S[k]; ok(n + ': antrean utuh (2), tidak ada yang "ditolak", layar masuk tidak muncul', j['antrean'] == [2100, 2200] and not j['ditolak'] and not j['login'] and not j['masuk'], j)
    j = S['sibukPulih']; ok('server pulih → keduanya masuk', j['masuk'] == [2100, 2200] and not j['antrean'] and not j['ditolak'], j)
    j = S['tidakDikenal401']; ok('401 → layar masuk muncul, antrean utuh (2), tidak ada yang pindah ke "ditolak"', j['login'] and j['antrean'] == [3100, 3200] and not j['ditolak'] and not j['masuk'], j)
    j = S['belumMasuk']; ok('belum masuk → nol kiriman ke server (403 tanpa kunci bukan penolakan aturan), antrean utuh, tidak ada "ditolak"' + (', layar masuk muncul' if berkas == DARURAT else ''),
                            j['tanpaKunci'] == 0 and not j['permintaan'] and j['antrean'] == [4100, 4200] and not j['ditolak'] and (j['login'] or berkas != DARURAT), j)
    j = S.get('ketukTombol') or {}
    ok('TOMBOL SUNGGUHAN (klik DOM → data-aksi → AKSI): papan 7 + "000" → LCD 7.000 ("000" tetap teks), + BARANG BERIKUTNYA dua kali → 2 baris',
       j.get('lcdTujuhRibu') == '7000' and j.get('barisDua') == 2, j)
    ok('ketuk: tombol hapus barang (dibangun innerHTML) menghapus baris ke-2; HAPUS menghapus satu angka (125 → 12 → 1200)',
       j.get('barisSesudahHapus') == 1 and j.get('lcdSeribuDuaRatus') == '1200', j)
    ok('ketuk: KREDIT terpilih; SIMPAN tanpa nama DITOLAK (kolom nama ditandai, antrean kosong); ketikan nama (input) membersihkan tandanya',
       j.get('kreditTerpilih') is True and j.get('tanpaNama') == {'antrean': 0, 'kurang': True} and j.get('sesudahKetikKurang') is False, j)
    ok('ketuk: SIMPAN → 2 karcis satu nota (7.000 & 1.200, Kredit, bernama) di antrean, kolom kembali kosong & Tunai; terkirim berurutan',
       j.get('antrean') == [[7000, 'Kredit', 'Pembeli Uji'], [1200, 'Kredit', 'Pembeli Uji']] and j.get('satuNota') is True
       and j.get('sesudahSimpan') == {'nama': '', 'tunai': True} and j.get('masuk') == j.get('antrean'), j)
    j = S['keduaDitolak']
    ok('antrean awal 5 ' + kata + ', yang ke-2 bertanggal bulan terkunci', u.get('antreanAwal') == [5100, 5200, 5300, 5400, 5500], u.get('antreanAwal'))
    ok(kata + ' ke-2 dari 5 ditolak → 1, 3, 4, 5 MASUK berurutan, antrean kosong', j['masuk'] == [5100, 5300, 5400, 5500] and not j['antrean'], j)
    ok(kata + ' ke-2 ada di daftar "ditolak" dengan isi utuh (nominal, tanggal) & alasan aturan (403)',
       len(j['ditolak']) == 1 and j['ditolak'][0]['h'] == 5200 and j['ditolak'][0]['t'] == '2026-08-31' and j['ditolak'][0]['alasan'] == 'aturan' and j['ditolak'][0]['status'] == 403, j['ditolak'])
    ok('layar masuk TIDAK muncul karena penolakan aturan', not j['login'], j)
    ok('yang ditolak TIDAK dikirim ulang walau antrean dijalankan dua kali lagi (satu permintaan saja)', j['permintaan'].count(5200) == 1, j['permintaan'])
    ok('pita tampil: "1 ' + kata + ' ditolak server (bulan sudah dikunci)"', ('1 ' + kata + ' ditolak server (bulan sudah dikunci)') in j['pita'], j['pita'])
    ok('bilah status menyebut "1 ditolak"', '1 ditolak' in j['chip'], j['chip'])
    dy = u.get('denyut') or {}
    ok('denyut melaporkan antrean 0, ditolak 1, versi = VERSI sw-kasir.js (' + versi_sw + ')', dy.get('antrean') == 0 and dy.get('gagal') == 1 and dy.get('versi') == versi_sw, dy)
    if not m or m.get('galat'):
        out.append((berkas + ' · muat ulang jalan', False, {'galat': (m or {}).get('galat', 'tidak ada hasil'), 'cspLain': (m or {}).get('cspLain')})); return out
    periksa_csp(ok, 'muat ulang', m)
    j = m['skenario']['sesudahMuatUlang']
    ok('sesudah MUAT ULANG: ' + kata + ' yang ditolak masih ada (tidak hilang), pita masih tampil', len(j['ditolak']) == 1 and j['ditolak'][0]['h'] == 5200 and 'ditolak server' in j['pita'], j)
    ok('pita DIKETUK → daftar ditolak menyebut tanggal, jam & nominal supaya bisa dicatat ulang', m.get('daftarTampil') and '31/08/2026' in (m.get('daftarTeks') or '') and '20:15' in (m.get('daftarTeks') or '') and '5.200' in (m.get('daftarTeks') or ''), m.get('daftarTeks'))
    ok('Tutup DIKETUK → daftar ditolak tertutup', m.get('sesudahTutup') is False, m.get('sesudahTutup'))
    ok('"sudah dicatat ulang": satu ketukan TIDAK memindah apa pun', len(m['sesudahSatuKetuk']['ditolak']) == 1 and not m['sesudahSatuKetuk']['arsip'], m['sesudahSatuKetuk'])
    ok('ketukan kedua MEMINDAH ke arsip (tidak dihapus), pita hilang', not m['sesudahDuaKetuk']['ditolak'] and m['sesudahDuaKetuk']['arsip'] == [5200] and not m['sesudahDuaKetuk']['pita'], m['sesudahDuaKetuk'])
    ok('versi yang berjalan tampil di layar ("versi 3 Okt b" — naik bersama kasir-v32)', m.get('versiLayar') == 'versi 3 Okt b', m.get('versiLayar'))
    return out


# ---------- STATIS ----------
def fungsi(teks, nama):
    m = re.search(r'function ' + nama + r'\([^)]*\) \{.*?\n\}\n', teks, re.S); return m.group(0) if m else None


def periksa_statis(teks):
    """teks = {berkas: isi} (boleh salinan rusak untuk kontrol). → [(nama, lulus, ket)]"""
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    sw = teks['sw-kasir.js']; vs = re.search(r"const VERSI = '([^']+)';", sw)
    kp = re.search(r"export const KP_VERSI_KASIR_25B = '([^']+)';", teks['baru/js/data/kunci-periode.js'])
    for b in (DARURAT,):
        va = re.search(r"var VERSI_APLIKASI = '([^']+)';", teks[b])
        ok(b + ': VERSI_APLIKASI = VERSI sw-kasir.js (' + (vs.group(1) if vs else '?') + ')', va and vs and va.group(1) == vs.group(1), va.group(1) if va else None)
        ok(b + ': denyut mengirim VERSI_APLIKASI (bukan teks versi yang ditulis tangan)', re.search(r'versi: VERSI_APLIKASI\b', teks[b]) and not re.search(r"versi: 'kasir-v\d+'", teks[b]))
        ok(b + ': memuat ulang diri saat versi baru mengambil alih (controllerchange) & menanyakan versi baru (reg.update)', "addEventListener('controllerchange'" in teks[b] and 'reg.update()' in teks[b])
        ok(b + ': tidak mengirim antrean tanpa masuk (403 tanpa kunci ≠ ditolak aturan)', "if (!sudahLogin()) { setStatus(navigator.onLine); return; }" in teks[b])
    # 25c: /baru/ memegang DUA angka versi — versi terbaru yang disajikan (KK_VERSI_KASIR_TERBARU, harus = sw) dan LANTAI kunci bulan (KP_VERSI_KASIR_25B:
    # versi pertama yang memisahkan karcis ditolak; tetap kasir-v26 — HP v26 tidak menahan kunci bulan). Keduanya dijaga dalam satu pemeriksaan ini.
    kk = re.search(r"export const KK_VERSI_KASIR_TERBARU = '([^']+)';", teks['baru/js/data/katalog-kasir.js']); no = lambda x: int(re.match(r'kasir-v(\d+)$', x.group(1)).group(1)) if x and re.match(r'kasir-v(\d+)$', x.group(1)) else -1
    ok('/baru/: versi kasir terbaru (KK_VERSI_KASIR_TERBARU) = VERSI sw-kasir.js; lantai kunci bulan KP_VERSI_KASIR_25B (kasir-v26) ≤ versi itu', kk and vs and kk.group(1) == vs.group(1) and kp and kp.group(1) == 'kasir-v26' and 0 < no(kp) <= no(vs), [x.group(1) if x else None for x in (kk, kp, vs)])
    ok('sw-kasir.js mengunduh versi baru melewati cache HTTP peramban (cache: \'reload\')', "new Request(f, { cache: 'reload' })" in sw)
    out += periksa_salinan(teks[DARURAT], lambda: salinan(teks[DARURAT], DARURAT, _asli()), SKENARIO.replace('__PENYESUAI__', PENYESUAI[DARURAT]), PENJAGA_CSP)
    return out


def _asli():
    return open(os.path.join(AKAR, DARURAT), encoding='utf-8').read()


def periksa_salinan(halaman, bangun, suntikan, penjaga):
    """owner 3 Okt (perkuat): salinan uji peramban DIBANGUN TANPA PERAMBAN (teks yang sama dengan yang dimuat Chrome) dan diperiksa: script-src =
    hash halaman (apa adanya; dihitung ulang hanya kalau kontrol mengubah halaman) + hash skenario uji, TANPA 'unsafe-inline'; direktif lain tetap;
    tiap script sebaris sesudah meta ber-hash di script-src, tidak lebih; penjaga pelanggaran CSP (dengan kanari) & palsu Firestore SEBELUM meta.
    halaman = teks kasir darurat yang diuji (boleh salinan rusak kontrol); bangun() → teks salinan. Dipakai juga uji_katalog_kasir.py."""
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + DARURAT + ': salinan uji peramban — ' + n, bool(c), k))
    try: sl = bangun()
    except AssertionError as e: sl = None; sebab = str(e)
    if sl is None: return [('statis · ' + DARURAT + ': salinan uji peramban dibangun', False, sebab)]
    a = _csp(halaman if halaman == _asli() else uji_csp.tulis_hash(halaman)); b = _csp(sl) or {}
    tambah = uji_csp.hash_sebaris(suntikan); lain = lambda d: dict((k, v) for k, v in (d or {}).items() if k != 'script-src')
    ok("script-src = hash halaman + hash skenario uji, TANPA 'unsafe-inline'; direktif lain tetap",
       a and sorted(b.get('script-src', [])) == sorted(a.get('script-src', []) + tambah) and "'unsafe-inline'" not in b.get('script-src', []) and lain(a) == lain(b),
       {'salinan': b.get('script-src'), 'halaman': (a or {}).get('script-src'), 'suntikan': tambah})
    meta = sl.find('<meta http-equiv="Content-Security-Policy"')
    ok('tiap script sebaris sesudah meta CSP (halaman + skenario) ber-hash di script-src, tidak lebih',
       meta > 0 and sorted(uji_csp.hash_sebaris(sl[meta:])) == sorted(b.get('script-src', [])), (uji_csp.hash_sebaris(sl[meta:]), b.get('script-src')))
    pos = [sl.find(x) for x in ("addEventListener('securitypolicyviolation'", 'C.kanari = async function', 'window.fetch = function')]
    ok('penjaga pelanggaran CSP (securitypolicyviolation + kanari) & palsu Firestore disisip SEBELUM meta CSP (tidak terkena CSP)',
       penjaga in sl and all(0 <= x < meta for x in pos), (pos, meta))
    return out


def _csp(t):
    """Meta CSP → {direktif: [sumber]}; tanpa meta → None."""
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', t)
    return dict((x.split()[0], x.split()[1:]) for x in m.group(1).split(';') if x.split()) if m else None


def baca_semua():
    return {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in (DARURAT, 'sw-kasir.js', 'baru/js/data/kunci-periode.js', 'baru/js/data/katalog-kasir.js')}


# ---------- /baru/ di jsc (KOTAK PASIR) ----------
JSC_SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
var __KINI = new Date('2026-09-26T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };
var kini = new Date(__KINI);
function hp(id, aplikasi, versi, pada, antrean, gagal_, nama) { return { id: id, nama: nama || '', aplikasi: aplikasi, versi: versi, pada: pada, antrean: antrean || 0, gagal: gagal_ || 0 }; }
pasok('perangkatStatus', [
  hp('d-baru', 'darurat', 'kasir-v26', '2026-09-26T02:50:00.000Z', 0, 0, 'Penjaga Contoh A'),
  hp('d-lama', 'darurat', 'kasir-v24', '2026-09-25T09:00:00.000Z', 0, 0, 'Penjaga Contoh B'),
  hp('d-tanpa', 'darurat', '', '2026-09-24T09:00:00.000Z', 0, 0, ''),
  hp('k-jauh', 'kasir', 'kasir-v25', '2026-09-15T09:00:00.000Z', 0, 0, 'Penjaga Contoh C'),
  hp('p-owner', 'baru', 'baru', '2026-09-26T02:55:00.000Z', 0, 0, 'Mac Contoh'),
  hp('d-tolak', 'darurat', 'kasir-v26', '2026-09-26T01:00:00.000Z', 0, 2, 'Penjaga Contoh D'),
  hp('d-antre', 'darurat', 'kasir-v26', '2026-09-26T01:30:00.000Z', 3, 0, 'Penjaga Contoh E')]);
var BERSIH = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {}, siap25b: true };
var D = kpDaftarPeriksa('2026-08', kini, BERSIH); var b = D.butir.find(function (x) { return x.id === 'versiKasir'; });
ok('⛔ versi 25b ada, memblokir, dan kunci ditolak selama ada HP kasir versi lama', b && b.blokir && !b.ok && !D.boleh, J(b));
var r = b ? b.rincian.join(' | ') : '';
ok('⛔ versi 25b menyebut NAMA perangkat yang tertinggal & versinya (Penjaga Contoh B kasir-v24; d-tanpa "versi tidak dilaporkan")', /Penjaga Contoh B · kasir darurat · kasir-v24/.test(r) && /d-tanpa · kasir darurat · versi tidak dilaporkan/.test(r), r);
ok('⛔ versi 25b TIDAK menyebut yang sudah v26, sistem baru, atau yang tidak berdenyut 7 hari (kasir-v25 11 hari lalu)', !/Penjaga Contoh A|Mac Contoh|Penjaga Contoh C|Penjaga Contoh D|Penjaga Contoh E/.test(r) && b.rincian.length === 2, r);
pasok('perangkatStatus', cacheMentah('perangkat').map(function (p) { return Object.assign({}, p, p.aplikasi === 'baru' ? {} : { versi: 'kasir-v26' }); }));
var D2 = kpDaftarPeriksa('2026-08', kini, BERSIH); var b2 = D2.butir.find(function (x) { return x.id === 'versiKasir'; });
ok('semua HP kasir sudah kasir-v26 → butir versi beres', b2 && b2.ok, J(b2));
pasok('perangkatStatus', [hp('d-baru', 'darurat', 'kasir-v26', '2026-09-26T02:50:00.000Z', 0, 0, 'Penjaga Contoh A'), hp('d-lama', 'darurat', 'kasir-v24', '2026-09-25T09:00:00.000Z', 0, 0, 'Penjaga Contoh B'),
  hp('d-tolak', 'darurat', 'kasir-v26', '2026-09-26T01:00:00.000Z', 0, 2, 'Penjaga Contoh D'), hp('d-antre', 'darurat', 'kasir-v26', '2026-09-26T01:30:00.000Z', 3, 0, 'Penjaga Contoh E'),
  hp('k-jauh', 'kasir', 'kasir-v25', '2026-09-15T09:00:00.000Z', 0, 0, 'Penjaga Contoh C'), hp('p-owner', 'baru', 'baru', '2026-09-26T02:55:00.000Z', 0, 0, 'Mac Contoh')]);
var PH = kpPerhatianPerangkat(kini); var t = PH.map(function (x) { return x.teks; }).join(' | ');
ok('Perlu perhatian: HP dengan karcis DITOLAK disebut dengan jumlahnya (awas)', PH.some(function (x) { return /Penjaga Contoh D/.test(x.teks) && /2 DITOLAK server/.test(x.teks) && x.awas && x.nilai === '2 ditolak'; }), t);
ok('Perlu perhatian: HP dengan antrean disebut jumlah antreannya', PH.some(function (x) { return /Penjaga Contoh E/.test(x.teks) && /3 antre/.test(x.teks); }), t);
ok('Perlu perhatian: HP kasir versi lama (berdenyut 7 hari) disebut versinya', PH.some(function (x) { return /Penjaga Contoh B/.test(x.teks) && /masih kasir-v24, belum 25b/.test(x.teks) && x.awas; }), t);
ok('Perlu perhatian DIAM untuk HP yang beres, sistem baru, dan HP lama yang tidak berdenyut 7 hari tanpa antrean/ditolak', !/Penjaga Contoh A|Mac Contoh|Penjaga Contoh C/.test(t) && PH.length === 3, t);
ok('versi dibaca sebagai NOMOR: kasir-v100 ≥ kasir-v26, kasir-v9 < kasir-v26, teks lain = lama', kpVersiKasirCukup('kasir-v100') && !kpVersiKasirCukup('kasir-v9') && !kpVersiKasirCukup('baru') && !kpVersiKasirCukup(undefined));
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan_jsc(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(baris[-1]), ''


def bundel_jsc():
    import bundel_baru, uji_kunci_periode
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(uji_kunci_periode.MODUL))


def periksa_baru(js):
    h, e = jalan_jsc(js + '\n' + JSC_SKENARIO)
    if h is None: return [('/baru/ · jsc jalan', False, e)]
    return [('/baru/ · ' + x, False, '') for x in h['gagal']] + [('/baru/ · kasus %d' % (i + 1), True, '') for i in range(h['lulus'])]


def cetak(hasil):
    lulus = [x for x in hasil if x[1]]; gagal = [x for x in hasil if not x[1]]
    for n, _, k in gagal: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:300] if k not in ('', None) else ''))
    return len(lulus), len(gagal)


def semua(ganti_berkas=None, ganti_jsc=None, gambar_dir=None, hanya=None):
    """ganti_berkas = {berkas: [(lama, baru)]} (kontrol); kunci '@nama' = global alat uji ini (ganti_alat). hanya = daftar bagian yang dijalankan
    ('statis', 'peramban', 'baru')."""
    ganti_berkas = ganti_berkas or {}
    alat = dict((k[1:], v) for k, v in ganti_berkas.items() if k.startswith('@'))
    with ganti_alat(alat):
        return _semua(dict((k, v) for k, v in ganti_berkas.items() if not k.startswith('@')), ganti_jsc, gambar_dir, hanya)


def _semua(ganti_berkas, ganti_jsc, gambar_dir, hanya):
    hanya = hanya or ['statis', 'peramban', 'baru']; hasil = []
    teks = baca_semua()
    for b, gs in ganti_berkas.items():
        for lama, baru in gs:
            assert lama in teks[b], 'kontrol basi: ' + b + ' · ' + lama[:70]; teks[b] = teks[b].replace(lama, baru)
    versi_sw = re.search(r"const VERSI = '([^']+)';", teks['sw-kasir.js']).group(1)
    if 'statis' in hanya: hasil += periksa_statis(teks)
    if 'peramban' in hanya:
        if not CHROME: hasil.append(('peramban · Google Chrome tersedia', False, 'tidak ditemukan'))
        else:
            dirusak = [b for b in (DARURAT,) if b in ganti_berkas]
            for b in (dirusak or [DARURAT]):   # kontrol: hanya berkas yang dirusak yang dijalankan di peramban
                u, m = jalankan_berkas(b, ganti_berkas.get(b), gambar_dir if b == DARURAT else None)
                hasil += periksa_peramban(b, u, m, versi_sw)
    if 'baru' in hanya:
        js = bundel_jsc()
        for lama, baru in (ganti_jsc or []):
            assert lama in js, 'kontrol basi (jsc): ' + lama[:70]; js = js.replace(lama, baru)
        hasil += periksa_baru(js)
    return hasil


KONTROL = [
    # (nama, ganti per berkas, ganti jsc, bagian)
    ('penolakan aturan diperlakukan sebagai "belum masuk" (kasir darurat)', {DARURAT: [("if (status === 403) return adaToken ? 'ditolak-aturan' : 'masuk-ulang';", "if (status === 403) return 'masuk-ulang';")]}, None, ['peramban']),
    ('karcis ditolak DIHAPUS (tidak ditulis ke daftar ditolak)', {DARURAT: [("    try { localStorage.setItem(K_GAGAL, JSON.stringify(d)); } catch (e) { return false; }\n  }\n  cabutDariAntrean(item);", "  }\n  cabutDariAntrean(item);")]}, None, ['peramban']),
    ('karcis ditolak dicoba ulang terus (403 = coba lagi) — antrean macet', {DARURAT: [("if (status === 403) return adaToken ? 'ditolak-aturan' : 'masuk-ulang';", "if (status === 403) return adaToken ? 'coba-lagi' : 'masuk-ulang';")]}, None, ['peramban']),
    ('429 (kuota habis) dianggap ditolak — karcis dibuang ke daftar ditolak', {DARURAT: [("if (status === 408 || status === 409 || status === 429 || !(status >= 400 && status < 500)) return 'coba-lagi';", "if (status === 408 || status === 409 || !(status >= 400 && status < 500)) return 'coba-lagi';")]}, None, ['peramban']),
    # kasir.html pensiun (3 Okt 2026): kontrol ini dulu merusak kasir.html — kini kasir darurat (teks penjaganya sama persis), statis + peramban
    ('antrean dikirim tanpa masuk (403 tanpa kunci jadi "ditolak")', {DARURAT: [("  if (!sudahLogin()) { setStatus(navigator.onLine); return; }\n  sedangKirim = true;", "  sedangKirim = true;"),
                                                                        ("      if (!(opsi.headers && opsi.headers.Authorization)) {\n        selesai(false); if (!sudahLogin()) tampilkanLayarLogin(true); return;\n      }\n", "")]}, None, ['statis', 'peramban']),
    ('pita ditolak tidak digambar', {DARURAT: [("  el.style.display = 'block';\n}\nfunction barisDitolakHtml", "}\nfunction barisDitolakHtml")]}, None, ['peramban']),
    ('arsip "sudah dicatat ulang" satu ketukan', {DARURAT: [("  if (!yakinArsip) {\n    yakinArsip = true;", "  if (false) {\n    yakinArsip = true;")]}, None, ['peramban']),
    # 25c: sesudah versi, denyut kasir darurat membawa `katalog` (baris versinya berakhir koma) — kontrol mengganti nilainya saja
    ('denyut masih versi tulis-tangan lama', {DARURAT: [("    versi: VERSI_APLIKASI,\n", "    versi: 'kasir-v24',\n")]}, None, ['statis', 'peramban']),
    ('sw-kasir.js naik tanpa kasir ikut (VERSI beda)', {'sw-kasir.js': [("const VERSI = 'kasir-v32';", "const VERSI = 'kasir-v33';")]}, None, ['statis']),
    ('service worker memakai cache HTTP lama', {'sw-kasir.js': [("c.addAll(FILES.map((f) => new Request(f, { cache: 'reload' })))", "c.addAll(FILES)")]}, None, ['statis']),
    ('meta CSP kasir darurat tanpa script-src (salinan uji tidak bisa menambah hash skenario)', {DARURAT: [("script-src 'sha256-", "script-sumber 'sha256-")]}, None, ['statis']),
    # owner 3 Okt (perkuat): salinan uji memakai CSP halaman (bukan 'unsafe-inline'), tombol diketuk lewat klik DOM, pelanggaran CSP dihitung (+ kanari)
    ("salinan uji kembali melonggarkan script-src ke 'unsafe-inline' (statis)", {'@csp_salinan': _salinan_longgar}, None, ['statis']),
    ("salinan uji kembali melonggarkan script-src ke 'unsafe-inline' (peramban: kanari ikut jalan)", {'@csp_salinan': _salinan_longgar}, None, ['peramban']),
    ('salinan uji tidak menghitung ulang hash halaman yang diubah kontrol (yang berbunyi hash basi, bukan cacat yang dituju)',
     {DARURAT: [("    versi: VERSI_APLIKASI,\n", "    versi: VERSI_APLIKASI + '',\n")], '@csp_salinan': lambda t, s, asli=None, f=csp_salinan: f(t, s, None)}, None, ['statis']),
    ('pendengar pelanggaran CSP dicabut (statis)', {'@PENJAGA_CSP': [("  document.addEventListener('securitypolicyviolation', function (e) {", "  (function (e) {")]}, None, ['statis']),
    ('pendengar pelanggaran CSP dicabut (peramban: kanari tidak tercatat)', {'@PENJAGA_CSP': [("  document.addEventListener('securitypolicyviolation', function (e) {", "  (function (e) {")]},
     None, ['peramban']),
    ('onclick sebaris kembali di tombol SIMPAN (peramban: diblokir CSP, ketukan tidak menyimpan)', {DARURAT: [('id="btnSimpan" data-aksi="simpan"', 'id="btnSimpan" onclick="simpanNominal()"')]}, None, ['peramban']),
    ('pendengar delegasi click dicabut (peramban: semua tombol sungguhan mati)', {DARURAT: [("document.addEventListener('click', jalankanAksi);\n", "")]}, None, ['peramban']),
    ('angka papan dibaca sebagai ANGKA ("000" jadi 0)', {DARURAT: [("  angka: function (el) { tekanAngka(el.getAttribute('data-nilai')); },", "  angka: function (el) { tekanAngka(Number(el.getAttribute('data-nilai'))); },")]}, None, ['peramban']),
    ('pendengar ketikan dicabut (kolom nama tetap ditandai sesudah diketik)', {DARURAT: [("document.addEventListener('input', jalankanAksi);\n", "")]}, None, ['peramban']),
    ('tombol Tutup daftar ditolak tanpa data-aksi (mati)', {DARURAT: [('<button type="button" data-aksi="tutupDitolak">Tutup</button>', '<button type="button">Tutup</button>')]}, None, ['peramban']),
    ('/baru/: HP kasir versi lama tidak memblokir kunci', {}, [("tambah({ id: 'versiKasir', blokir: true, ok: !lamaV.length,", "tambah({ id: 'versiKasir', blokir: true, ok: true,")], ['baru']),
    ('/baru/: versi dibandingkan sebagai ada/tidak, bukan nomor', {}, [("const kpVersiKasirCukup = (v) => kpNomorVersiKasir(v) >= kpNomorVersiKasir(KP_VERSI_KASIR_25B);", "const kpVersiKasirCukup = (v) => !!v;")], ['baru']),
    ('/baru/: Perlu perhatian diam soal karcis ditolak', {}, [("if (tolak) bagian.push(tolak + ' DITOLAK server", "if (false) bagian.push(tolak + ' DITOLAK server")], ['baru']),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, gb, gj, bagian in KONTROL:
            try:
                h = semua(gb, gj, hanya=bagian); g = [x for x in h if not x[1]]
            except AssertionError as e:
                print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        print(teks_stat())
        sys.exit(kode)
    gd = sys.argv[sys.argv.index('--gambar') + 1] if '--gambar' in sys.argv else None
    h = semua(gambar_dir=gd)
    l, g = cetak(h)
    print('ANTREAN KASIR (25b): %d lulus · %d gagal' % (l, g))
    print(teks_stat())
    if gd: print('tangkapan layar: ' + gd)
    sys.exit(1 if g else 0)
