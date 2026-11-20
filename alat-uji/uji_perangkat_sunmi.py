#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_perangkat_sunmi.py — paket S1 (19 Nov 2026): cangkang SUNMI. Pintu perangkat baru/js/inti/perangkat.js dijalankan ASLI di jsc dengan
aplikasi tablet TIRUAN (window.Capacitor palsu — tidak ada printer, scanner, atau lampu sungguhan), plus pemasang APK apk/pasang.py.

Yang dijaga:
  JSC (perangkat.js)
  · bukan aplikasi (HP/Mac): tidak ada yang melempar — asliAda false, lampu { ok: false }, pindai tidak mendengar, kemampuan kosong
  · scanner vs PIN: ketikan jari (≥ 35 ms antar ketukan) BUKAN mesin; ≥ 3 ketukan beruntun < 35 ms = mesin; dua ketukan cepat saja belum
  · jalur 'sunmi' berhasil → CetakUsb TIDAK disentuh; peringatan (kertas hampir habis) ikut pulang
  · jalur 'sunmi' gagal SEBELUM ada byte terkirim (plugin tak ada di APK lama, printer tak ketemu) → jatuh ke CetakUsb TEPAT satu kali,
    printer dilepas dulu, sebabnya ikut pulang
  · printer MENJAWAB ada halangan (PRINTER_xxx: kertas habis, tutup terbuka, diam sesudah data dikirim) → galat dilempar, CetakUsb TIDAK
    dipanggil (tidak ada struk dobel)
  · jalur 'aplikasi' → hanya CetakUsb
  · pindai: kejadian diteruskan ke semua pendengar, isi bukan teks dibuang, pelepas bekerja
  · lampu: warna benar, tidak pernah melempar, berhenti memanggil sesudah aplikasi terbukti tak punya lampu
  PYTHON (apk/pasang.py — teks contoh manifest & build.gradle bentuk Capacitor 7)
  · manifest: usb.host, penyaring USB, <queries> scanner & layanan SUNMI, penjaga "Hapus data", allowBackup mati, configChanges lengkap;
    dijalankan dua kali = sama; pola tak dikenal = DITOLAK (bukan APK diam-diam tanpa bagiannya)
  · build.gradle: versi dari nomor jalan, dua pustaka resmi SUNMI tepat satu kali
  STATIS
  · tiap *Plugin.java di apk/tambahan terdaftar di MainActivity; nama plugin di Java = nama yang dipanggil perangkat.js
  · app.js: pendengar keydown panel PIN menampung dulu (tidak memanggil tekanPin langsung); teks catatan struk jalur lama tidak berubah
  · jual.js: lampu hanya lewat pembungkus yang menelan galat, hijau hanya sesudah nota sungguh tercatat
  · apk.yml membuktikan tanda tangan V1 dan V2 (syarat SUNMI App Store)

    python3 alat-uji/uji_perangkat_sunmi.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_perangkat_sunmi.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, glob, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MODUL = os.path.join(AKAR, 'baru', 'js', 'inti', 'perangkat.js')
PASANG = os.path.join(AKAR, 'apk', 'pasang.py')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });
const ketik = (jeda, n, mulai) => { let t = []; for (let i = 0; i < n; i++) t = ketikTambah(t, String(i % 10), (mulai || 1000) + i * jeda); return t; };

// aplikasi tiruan: daftar plugin + jawaban per "Plugin.metode" (fungsi → nilai / melempar)
function pasangAplikasi(plugin, jawab) {
  const catat = []; const dengar = {};
  globalThis.window = { Capacitor: {
    isNativePlatform: () => true,
    PluginHeaders: plugin.map((name) => ({ name })),
    nativePromise: (p, m, isi) => { catat.push(p + '.' + m); const f = jawab[p + '.' + m];
      if (plugin.indexOf(p) < 0) return Promise.reject(Object.assign(new Error('unable to find plugin : ' + p), {}));
      if (!f) return Promise.resolve({});
      try { return Promise.resolve(f(isi)); } catch (e) { return Promise.reject(e); } },
    addListener: (p, kejadian, fn) => { dengar[p + '.' + kejadian] = fn; return { remove: () => { delete dengar[p + '.' + kejadian]; } }; },
  } };
  return { catat, dengar, hitung: (x) => catat.filter((y) => y === x).length };
}
const tolak = (pesan, kode) => () => { const e = new Error(pesan); if (kode) e.code = kode; throw e; };

(async () => {
  // ---- bukan aplikasi ----
  cek('bukan aplikasi: asliAda false', asliAda() === false);
  cek('bukan aplikasi: adaPlugin false', adaPlugin('Lampu') === false);
  let g = null; try { await panggilAsli('CetakUsb', 'cetak', {}); } catch (e) { g = e; }
  cek('bukan aplikasi: panggilAsli menolak berkode TIDAK_ADA', g && g.code === 'TIDAK_ADA', g && g.code);
  cek('bukan aplikasi: lampu tidak melempar, { ok: false }', (await lampuBerhasil()).ok === false && (await lampuGagal()).ok === false && (await lampuPadam()).ok === false);
  const k0 = await kemampuan(); cek('bukan aplikasi: kemampuan kosong', k0.aplikasi === false && k0.info === null);
  const lepas0 = padaPindai(() => {}); cek('bukan aplikasi: padaPindai memberi pelepas', typeof lepas0 === 'function'); lepas0();

  // ---- scanner vs jari ----
  cek('jari (120 ms antar ketukan) bukan mesin', ketikMesin(ketik(120, 6)) === false);
  cek('jari cepat (60 ms) bukan mesin', ketikMesin(ketik(60, 6)) === false);
  cek('tepat di batas ' + KETIK_JEDA_MESIN + ' ms bukan mesin', ketikMesin(ketik(KETIK_JEDA_MESIN, 8)) === false);
  cek('scanner 13 angka berjarak 8 ms = mesin', ketikMesin(ketik(8, 13)) === true);
  cek('dua ketukan cepat saja belum mesin', ketikMesin(ketik(5, 2)) === false);
  cek('tiga ketukan cepat = mesin', ketikMesin(ketik(5, 3)) === true);
  cek('dua pasang ketukan cepat yang dipisah jeda jari bukan mesin (hitungan beruntun mulai lagi)', ketikMesin(ketik(5, 2).concat(ketik(5, 2, 1300)).concat(ketik(5, 2, 1600))) === false);
  cek('jari lalu scan menyusul = mesin', ketikMesin(ketik(150, 3).concat(ketik(6, 8, 5000))) === true);
  cek('tampungan kosong / satu ketukan bukan mesin', ketikMesin([]) === false && ketikMesin(ketik(1, 1)) === false && ketikMesin(null) === false);
  const awal = ketik(100, 2); const sesudah = ketikTambah(awal, '7', 9000);
  cek('ketikTambah tidak mengubah tampungan lama', awal.length === 2 && sesudah.length === 3 && sesudah[2].k === '7' && sesudah[2].t === 9000);
  cek('menunggu diam ' + KETIK_TUNGGU + ' ms: lebih lama dari jeda mesin, tidak terasa di jari', KETIK_TUNGGU > KETIK_JEDA_MESIN && KETIK_TUNGGU <= 120);

  // ---- cetak lewat aplikasi ----
  let A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': () => ({ nama: 'NT320', peringatan: 'Kertas printer hampir habis' }), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  cek('aplikasi: asliAda true, plugin terdaftar terbaca', asliAda() === true && adaPlugin('PrinterSunmi') === true && adaPlugin('Lampu') === false);
  let r = await cetakAsli('QUJD', 'sunmi');
  cek('jalur sunmi berhasil: jalur = sunmi, peringatan ikut', r.jalur === 'sunmi' && r.nama === 'NT320' && r.peringatan === 'Kertas printer hampir habis' && r.cadanganDari === '', JSON.stringify(r));
  cek('jalur sunmi berhasil: CetakUsb tidak disentuh', A.hitung('CetakUsb.cetak') === 0 && A.hitung('PrinterSunmi.cetak') === 1, A.catat.join(','));

  A = pasangAplikasi(['CetakUsb'], { 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'sunmi');
  cek('APK lama (tanpa PrinterSunmi): jatuh ke CetakUsb tepat sekali', r.jalur === 'aplikasi' && A.hitung('CetakUsb.cetak') === 1 && /unable to find plugin/.test(r.cadanganDari), JSON.stringify(r) + ' ' + A.catat.join(','));

  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Printer SUNMI tidak ditemukan di USB', 'BELUM_KIRIM'), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'sunmi');
  cek('SDK gagal sebelum kirim: printer dilepas lalu CetakUsb tepat sekali', r.jalur === 'aplikasi' && A.catat.join(',') === 'PrinterSunmi.cetak,PrinterSunmi.lepas,CetakUsb.cetak', A.catat.join(','));
  cek('SDK gagal sebelum kirim: sebabnya ikut pulang', r.cadanganDari === 'Printer SUNMI tidak ditemukan di USB', r.cadanganDari);

  for (const kode of ['PRINTER_OUT_PAPER', 'PRINTER_COVER', 'PRINTER_DIAM']) {
    A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('halangan', kode), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
    g = null; try { await cetakAsli('QUJD', 'sunmi'); } catch (e) { g = e; }
    cek(kode + ': galat dilempar, CetakUsb TIDAK dipanggil (tidak dobel)', g && g.code === kode && A.hitung('CetakUsb.cetak') === 0, A.catat.join(','));
  }
  cek('galatPrinter mengenali hanya kode PRINTER_', galatPrinter({ code: 'PRINTER_COVER' }) && !galatPrinter({ code: 'BELUM_KIRIM' }) && !galatPrinter(new Error('x')) && !galatPrinter(null));
  // uji owner 20 Nov 2026 (Bluetooth, cetak pertama sesudah printer menganggur): pustaka SUNMI mengabari UNKNOWN sesudah data dikirim dan layar
  // menulis "Cetak gagal: keadaan printer tidak diketahui". Hasilnya tidak diketahui — kalimatnya harus menyebut langkah berikutnya, tanpa kirim ulang.
  for (const kode of ['PRINTER_UNKNOWN', 'PRINTER_DIAM']) {
    A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Cetak gagal: keadaan printer tidak diketahui', kode), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
    g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
    cek(kode + ': printer diam sesudah data dikirim → kalimat "tidak mengabari hasil, lihat kertasnya"', g && g.message === KALIMAT_TAK_DIKABARI, g && g.message);
    cek(kode + ': kodenya tetap (tetap galat printer) dan tidak ada kiriman ulang lewat jalur lain', g && g.code === kode && galatPrinter(g) && A.catat.join(',') === 'PrinterSunmi.cetak', (g && g.code) + ' · ' + A.catat.join(','));
    cek(kode + ': kabar asli aplikasi ikut dibawa untuk catatan layar Perangkat', g && g.asli === 'Cetak gagal: keadaan printer tidak diketahui', g && g.asli);
  }
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Printer belum bisa mencetak: kertas habis', 'PRINTER_OUT_PAPER'), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
  cek('halangan pasti (kertas habis): kalimat printer sampai apa adanya, bukan "tidak mengabari"', g && g.message === 'Printer belum bisa mencetak: kertas habis' && g.asli === undefined, g && g.message);
  cek('hasilTakDiketahui hanya untuk printer yang diam (UNKNOWN / DIAM)', hasilTakDiketahui({ code: 'PRINTER_UNKNOWN' }) && hasilTakDiketahui({ code: 'PRINTER_DIAM' }) && !hasilTakDiketahui({ code: 'PRINTER_OUT_PAPER' })
    && !hasilTakDiketahui({ code: 'PRINTER_OFFLINE' }) && !hasilTakDiketahui({ code: 'BELUM_KIRIM' }) && !hasilTakDiketahui(new Error('x')) && !hasilTakDiketahui(null));
  cek('kalimat "tidak mengabari" tidak menyebut gagal dan menyebut langkah berikutnya', !/gagal/i.test(KALIMAT_TAK_DIKABARI) && /lihat kertasnya/.test(KALIMAT_TAK_DIKABARI) && /cetak lagi/.test(KALIMAT_TAK_DIKABARI), KALIMAT_TAK_DIKABARI);

  // uji owner 20 Nov 2026 malam (Jual, Bluetooth): ketukan Cetak kedua saat cetakan pertama belum dikabari memutus sambungan cetakan pertama
  // ("printer tidak tersambung", dua baris struk keluar). Satu cetakan pada satu waktu: yang kedua ditolak SEBELUM menyentuh aplikasi.
  {
    let lepasTahan = null; const tahan = new Promise((ok) => { lepasTahan = ok; });
    A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': () => tahan.then(() => ({ nama: 'NT320' })), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
    cek('satu cetakan: sebelum ada cetakan, printer tidak sibuk', printerSibuk() === false);
    const pertama = cetakAsli('QUJD', 'sunmi-bt');
    cek('satu cetakan: selama cetakan pertama belum dikabari, printer sibuk', printerSibuk() === true);
    g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
    cek('satu cetakan: cetakan kedua ditolak berkode SEDANG_CETAK dengan kalimat "tunggu kabarnya"', g && g.code === 'SEDANG_CETAK' && g.message === KALIMAT_MASIH_MENCETAK, g && (g.code + ' · ' + g.message));
    cek('satu cetakan: cetakan kedua TIDAK menyentuh aplikasi (tidak menanya printer, tidak melepas sambungan, tidak lewat kabel)', A.catat.join(',') === 'PrinterSunmi.cetak', A.catat.join(','));
    g = null; try { await cetakAsli('QUJD', 'aplikasi'); } catch (e) { g = e; }
    cek('satu cetakan: jalur kabel juga menunggu (tidak ada dua cetakan bersamaan lewat jalur mana pun)', g && g.code === 'SEDANG_CETAK' && A.hitung('CetakUsb.cetak') === 0, A.catat.join(','));
    g = null; try { await kirimTspl('SIZE 40 mm,30 mm', 'bt'); } catch (e) { g = e; }
    cek('satu cetakan: perintah label ditolak selama cetakan belum dikabari', g && g.code === 'SEDANG_CETAK' && A.hitung('PrinterSunmi.tspl') === 0, A.catat.join(','));
    g = null; try { await pastikanModeLabel('struk', 'bt'); } catch (e) { g = e; }
    cek('satu cetakan: mode printer tidak ditanya di belakang cetakan yang belum dikabari', g && g.code === 'SEDANG_CETAK' && A.hitung('PrinterSunmi.mode') === 0, A.catat.join(','));
    g = null; try { await printerSetelMode(2, 'bt'); } catch (e) { g = e; }
    cek('satu cetakan: mode kertas tidak dipindah di tengah cetakan', g && g.code === 'SEDANG_CETAK' && A.hitung('PrinterSunmi.setelMode') === 0, A.catat.join(','));
    lepasTahan(); r = await pertama;
    cek('satu cetakan: cetakan pertama selesai tanpa terganggu', r.jalur === 'sunmi-bt' && r.nama === 'NT320', JSON.stringify(r));
    cek('satu cetakan: sesudah dikabari, printer tidak sibuk lagi', printerSibuk() === false);
    r = await cetakAsli('QUJD', 'sunmi-bt');
    cek('satu cetakan: cetakan berikutnya jalan seperti biasa', r.jalur === 'sunmi-bt' && A.hitung('PrinterSunmi.cetak') === 2, A.catat.join(','));
    A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Cetak gagal: keadaan printer tidak diketahui', 'PRINTER_UNKNOWN'), 'PrinterSunmi.tspl': tolak('Perintah label tidak terkirim', 'BELUM_KIRIM') });
    g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
    cek('satu cetakan: cetakan yang berakhir "tidak mengabari" juga membuka kunci', g && g.code === 'PRINTER_UNKNOWN' && printerSibuk() === false, g && g.code);
    g = null; try { await kirimTspl('SIZE 40 mm,30 mm', 'bt'); } catch (e) { g = e; }
    cek('satu cetakan: perintah label yang gagal juga membuka kunci', g && g.code === 'BELUM_KIRIM' && printerSibuk() === false && A.hitung('PrinterSunmi.tspl') === 1, (g && g.code) + ' · ' + A.catat.join(','));
    // kunci tidak boleh macet: aplikasi yang tidak pernah menjawab tidak mengunci toko dari printernya
    {
      let lepasA = null, lepasB = null; let ke = 0; const jamAsli = Date.now; let maju = 0; Date.now = () => jamAsli() + maju;
      A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': () => { ke += 1; return new Promise((ok) => { if (ke === 1) lepasA = ok; else lepasB = ok; }).then(() => ({ nama: 'NT320' })); } });
      const a1 = cetakAsli('QUJD', 'sunmi-bt');
      maju = BATAS_SIBUK_MS - 1000;
      cek('kunci macet: sebelum ' + (BATAS_SIBUK_MS / 1000) + ' detik masih dianggap mencetak', printerSibuk() === true);
      cek('kunci macet: batasnya lebih lama dari batas terpanjang aplikasi (sambung 12 + tanya 4 + cetak Bluetooth 60 detik)', BATAS_SIBUK_MS > (12 + 4 + 60) * 1000, BATAS_SIBUK_MS);
      maju = BATAS_SIBUK_MS + 1000;
      cek('kunci macet: aplikasi tidak pernah menjawab → sesudah batas, kunci dianggap lepas', printerSibuk() === false);
      const a2 = cetakAsli('QUJD', 'sunmi-bt');
      cek('kunci macet: cetakan baru boleh jalan dan memegang kuncinya sendiri', A.hitung('PrinterSunmi.cetak') === 2 && printerSibuk() === true, A.catat.join(','));
      lepasA(); await a1;
      cek('kunci macet: jawaban terlambat cetakan lama TIDAK membuka kunci cetakan baru', printerSibuk() === true);
      lepasB(); await a2;
      cek('kunci macet: cetakan baru selesai → kunci terbuka', printerSibuk() === false);
      Date.now = jamAsli;
    }
    // percobaan "kirim per potong" lewat Bluetooth DICABUT (owner 20 Nov 2026 malam: di kertas hanya potong pertama yang keluar) → satu struk = satu kiriman
    {
      const terima = [];
      A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': (isi) => { terima.push(isi.data + ':' + isi.lewat); return { nama: 'bt', peringatan: 'Kertas printer hampir habis' }; } });
      r = await cetakAsli('UTUH', 'sunmi-bt', ['P1', 'P2', 'P3']);
      cek('satu kiriman: larik di argumen ketiga TIDAK lagi memecah struk — satu panggilan cetak dengan kiriman utuh', terima.join(',') === 'UTUH:bt' && r.jalur === 'sunmi-bt' && r.peringatan === 'Kertas printer hampir habis' && r.cadanganDari === '' && !('potong' in r), terima.join(',') + ' ' + JSON.stringify(r));
      cek('satu kiriman: pengenal & kode "struk terpotong" sudah tidak ada', typeof strukTerpotong === 'undefined' && typeof galatTerpotong === 'undefined');
    }
    // ---- jalur JARINGAN (20 Nov 2026): cetak lewat Wi-Fi/LAN ke pintu HTTP printer, dititipkan ke CapacitorHttp ----
    {
      JARINGAN.jedaMs = 0; JARINGAN.tanyaMaks = 6;
      const ALAMAT = '192.168.7.21';
      // printer tiruan: jawabannya disalin dari printer toko (uji 20 Nov 2026), termasuk akhiran baris \r\n
      const NAMA = ['printing', 'no_paper', 'paper_jam', 'paper_not_taken', 'platen_opened', 'thermal_head_overheated', 'step_motor_overheated'];
      const teksKeadaan = (k, tugas) => NAMA.map((n) => n + ': ' + ((k || {})[n] ? 'yes' : 'no')).join('\r\n') + '\r\n' + (tugas ? 'task_status: ' + tugas + '\r\n' : '');
      function printer(o) {
        const st = { tugas: 60, tanyaTugas: 0, kiriman: [], url: [], isi: [] }; o = o || {};
        const jawab = (isi) => { st.url.push(isi.url); st.isi.push(isi);
          if (isi.url.indexOf('/cgi-bin/print.cgi') >= 0) { if (o.cetak) return o.cetak(isi, st); st.kiriman.push(isi.data); st.tugas += 1; return { status: 200, data: 'task_id: ' + st.tugas + '\r\n' }; }
          if (isi.url.indexOf('task_id=') >= 0) { st.tanyaTugas += 1; if (o.tanya) return o.tanya(isi, st); return { status: 200, data: teksKeadaan(o.keadaan, st.tanyaTugas >= (o.selesaiPada || 2) ? 'printed' : 'not printed') }; }
          if (o.awal) return o.awal(isi, st);
          return { status: 200, data: teksKeadaan(o.keadaan) }; };
        return { st, jawab };
      }
      const lempar = (pesan, kode) => { const e = new Error(pesan); e.code = kode; throw e; };
      const pasang = (P, usb) => pasangAplikasi(['CapacitorHttp', 'CetakUsb', 'PrinterSunmi'], { 'CapacitorHttp.request': P.jawab, 'CetakUsb.cetak': usb || (() => ({ nama: 'usb' })) });

      // alamat: hanya IPv4 pribadi
      cek('jaringan: alamat pribadi diterima dan dirapikan (spasi, tempelan http://…/#/… dari QR struk uji jaringan)', alamatPrinterSah(' 192.168.7.21 ') === '192.168.7.21' && alamatPrinterSah('http://192.168.7.21/#/deviceInfo') === '192.168.7.21'
        && alamatPrinterSah('10.0.0.5') === '10.0.0.5' && alamatPrinterSah('172.16.0.1') === '172.16.0.1' && alamatPrinterSah('172.31.255.254') === '172.31.255.254' && alamatPrinterSah('192.168.007.021') === '192.168.7.21');
      cek('jaringan: alamat di luar jaringan toko, nama, port, dan yang rusak DITOLAK', ['8.8.8.8', '172.32.0.1', '172.15.0.1', '192.169.1.1', '11.0.0.1', '192.168.1.256', '192.168.1', '192.168.7.21:8080', 'printer.local', 'https://contoh.com', '', null, undefined, '192.168.7.21.5', '1.2.3.4']
        .every((x) => alamatPrinterSah(x) === ''));
      // base64 → heksa
      cek('jaringan: base64 → heksa huruf kecil, byte demi byte (termasuk ganjalan = dan baris baru)', b64KeHeksa('QUJD') === '414243' && b64KeHeksa('G0AbYQE=') === '1b401b6101' && b64KeHeksa('AA==') === '00' && b64KeHeksa('//8=') === 'ffff'
        && b64KeHeksa('G0Ab\nYQE=') === '1b401b6101' && b64KeHeksa('') === '' && b64KeHeksa('AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=') === '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f',
        [b64KeHeksa('QUJD'), b64KeHeksa('G0AbYQE='), b64KeHeksa('//8=')].join(' '));
      // membaca jawaban printer
      let k = bacaJawabJaringan(teksKeadaan({ paper_not_taken: 1 }, 'printed'));
      cek('jaringan: jawaban keadaan printer terbaca (kertas belum diambil, pekerjaan tercetak)', k.dikenali && k.belumDiambil === true && k.kertasHabis === false && k.tutupTerbuka === false && k.mencetak === false && k.tugasStatus === 'printed', JSON.stringify(k));
      cek('jaringan: nomor pekerjaan terbaca dari jawaban kirim', bacaJawabJaringan('task_id: 54\r\n').tugas === '54' && bacaJawabJaringan('task_id: 54\r\n').dikenali === false);
      cek('jaringan: jawaban yang bukan dari printer TIDAK dikenali', !bacaJawabJaringan('<html><body>router</body></html>').dikenali && !bacaJawabJaringan('').dikenali && !bacaJawabJaringan(null).dikenali && !bacaJawabJaringan({ a: 1 }).dikenali);
      cek('jaringan: halangan pasti → kode & kalimat yang sama dengan jalur SDK; tutup terbuka didahulukan', halanganJaringan(bacaJawabJaringan(teksKeadaan({ no_paper: 1 }))).kode === 'PRINTER_OUT_PAPER'
        && halanganJaringan(bacaJawabJaringan(teksKeadaan({ no_paper: 1, platen_opened: 1 }))).kode === 'PRINTER_COVER' && halanganJaringan(bacaJawabJaringan(teksKeadaan({ paper_jam: 1 }))).kalimat === 'kertas macet'
        && halanganJaringan(bacaJawabJaringan(teksKeadaan({ thermal_head_overheated: 1 }))).kode === 'PRINTER_OVER_HOT' && halanganJaringan(bacaJawabJaringan(teksKeadaan({ step_motor_overheated: 1 }))).kode === 'PRINTER_MOTOR_HOT'
        && halanganJaringan(bacaJawabJaringan(teksKeadaan({ paper_not_taken: 1, printing: 1 }))) === null && halanganJaringan(null) === null);

      // periksa printer
      let P = printer(); A = pasang(P); let sj = await printerJaringanStatus(' 192.168.7.21 ');
      cek('jaringan: periksa printer → siap; satu permintaan POST ke status.cgi di alamat itu, tanpa nomor seri', sj.siap && sj.kalimat === 'siap' && sj.alamat === ALAMAT && P.st.url.join(',') === 'http://192.168.7.21/cgi-bin/status.cgi'
        && P.st.isi[0].method === 'POST' && P.st.isi[0].responseType === 'text' && P.st.url.join(',').indexOf('sn=') < 0, JSON.stringify(sj) + ' ' + P.st.url.join(','));
      P = printer({ keadaan: { paper_not_taken: 1 } }); A = pasang(P); sj = await printerJaringanStatus(ALAMAT);
      cek('jaringan: kertas belum diambil bukan halangan, tapi disebut', sj.siap && sj.kalimat === 'siap (struk sebelumnya belum diambil)', sj.kalimat);
      P = printer({ keadaan: { no_paper: 1 } }); A = pasang(P); sj = await printerJaringanStatus(ALAMAT);
      cek('jaringan: kertas habis → tidak siap, berkalimat', !sj.siap && sj.menghalangi && sj.kalimat === 'kertas habis', sj.kalimat);
      P = printer(); A = pasang(P); g = null; try { await printerJaringanStatus('8.8.8.8'); } catch (e) { g = e; }
      cek('jaringan: alamat tidak sah → SALAH_ISI, TIDAK ADA permintaan yang berangkat', g && g.code === 'SALAH_ISI' && A.catat.length === 0, (g && g.code) + ' ' + A.catat.join(','));
      P = printer({ awal: () => ({ status: 200, data: '<html>router</html>' }) }); A = pasang(P); g = null; try { await printerJaringanStatus(ALAMAT); } catch (e) { g = e; }
      cek('jaringan: alamat yang menjawab tapi bukan printer → BELUM_KIRIM "bukan seperti printer SUNMI"', g && g.code === 'BELUM_KIRIM' && /bukan seperti printer SUNMI/.test(g.message), g && g.message);
      P = printer({ awal: () => lempar('Failed to connect to /192.168.7.21:80', 'ConnectException') }); A = pasang(P); g = null; try { await printerJaringanStatus(ALAMAT); } catch (e) { g = e; }
      cek('jaringan: printer tidak terjangkau → BELUM_KIRIM berkalimat toko, sebab aslinya ikut', g && g.code === 'BELUM_KIRIM' && /tidak terjangkau lewat jaringan/.test(g.message) && /Failed to connect/.test(g.message), g && g.message);
      P = printer({ awal: () => lempar('CLEARTEXT communication to 192.168.7.21 not permitted by network security policy', 'UnknownServiceException') }); A = pasang(P); g = null; try { await printerJaringanStatus(ALAMAT); } catch (e) { g = e; }
      cek('jaringan: aplikasi lama (HTTP polos belum diizinkan) → "pasang APK terbaru"', g && g.code === 'BELUM_KIRIM' && /pasang APK terbaru/.test(g.message), g && g.message);

      // cetak: jalan mulus
      P = printer({ selesaiPada: 3 }); A = pasang(P); r = await cetakAsli('G0AbYQE=', 'jaringan', { alamat: ALAMAT });
      cek('jaringan: cetak = tanya keadaan → kirim heksa → tanya pekerjaan sampai "printed"', r.jalur === 'jaringan' && r.tugas === '61' && r.nama === ALAMAT && r.cadanganDari === ''
        && P.st.url.join(' ') === ['http://192.168.7.21/cgi-bin/status.cgi', 'http://192.168.7.21/cgi-bin/print.cgi?copies=1', 'http://192.168.7.21/cgi-bin/status.cgi?task_id=61', 'http://192.168.7.21/cgi-bin/status.cgi?task_id=61', 'http://192.168.7.21/cgi-bin/status.cgi?task_id=61'].join(' '),
        JSON.stringify(r) + ' · ' + P.st.url.join(' '));
      cek('jaringan: isi kiriman = heksa dari data cetak, sebagai teks polos; kabel tidak disentuh', P.st.kiriman.join(',') === '1b401b6101' && P.st.isi[1].headers['Content-Type'] === 'text/plain; charset=utf-8' && P.st.isi[1].method === 'POST'
        && A.hitung('CetakUsb.cetak') === 0 && A.hitung('PrinterSunmi.cetak') === 0, P.st.kiriman.join(',') + ' ' + A.catat.join(','));
      cek('jaringan: sesudah cetak, kunci "sedang mencetak" terbuka', printerSibuk() === false);
      // halangan pasti SEBELUM kirim
      P = printer({ keadaan: { no_paper: 1 } }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: kertas habis → ditolak SEBELUM ada yang dikirim, kode printer, tanpa kabel', g && g.code === 'PRINTER_OUT_PAPER' && g.message === 'Printer belum bisa mencetak: kertas habis' && P.st.kiriman.length === 0 && A.hitung('CetakUsb.cetak') === 0, (g && g.message) + ' ' + A.catat.join(','));
      // alamat kosong / di luar jaringan toko
      P = printer(); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: '' }); } catch (e) { g = e; }
      let g2 = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: '8.8.8.8' }); } catch (e) { g2 = e; }
      let g3 = null; try { await cetakAsli('G0A=', 'jaringan', null); } catch (e) { g3 = e; }
      cek('jaringan: alamat kosong / di luar jaringan toko → SALAH_ISI, tidak ada yang berangkat ke mana pun (juga tidak ke kabel)', g && g.code === 'SALAH_ISI' && g2 && g2.code === 'SALAH_ISI' && g3 && g3.code === 'SALAH_ISI' && A.catat.length === 0, [g && g.code, g2 && g2.code, g3 && g3.code, A.catat.join(',')].join(' '));
      // tidak terjangkau → kabel dicoba, dengan sebab jaringan terbaca
      let usbData = null;
      P = printer({ awal: () => lempar('failed to connect to /192.168.7.21 (port 80) after 4000ms', 'SocketTimeoutException') }); A = pasang(P, (isi) => { usbData = isi.data; return { nama: 'usb' }; });
      r = await cetakAsli('G0AbYQE=', 'jaringan', { alamat: ALAMAT });
      cek('jaringan: printer tidak terjangkau (belum ada yang dikirim) → kabel USB menerima data yang sama, sebab jaringan ikut pulang', r.jalur === 'aplikasi' && usbData === 'G0AbYQE=' && /tidak terjangkau lewat jaringan/.test(r.cadanganDari) && P.st.kiriman.length === 0, JSON.stringify(r));
      P = printer({ awal: () => lempar('Failed to connect', 'ConnectException') }); A = pasang(P, () => lempar('Printer USB tidak ditemukan', 'BELUM_KIRIM')); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: jaringan DAN kabel gagal → kedua sebab terbaca, sebab jaringan di depan', g && /tidak terjangkau lewat jaringan/.test(g.sebabUtama) && /kirim langsung lewat kabel USB juga gagal: Printer USB tidak ditemukan/.test(g.message) && g.message.indexOf(g.sebabUtama) === 0, g && g.message);
      // kiriman berangkat lalu tidak jelas → hasil tidak diketahui, TANPA kirim ulang
      P = printer({ cetak: () => lempar('timeout', 'SocketTimeoutException') }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: sambungan putus SAAT mengirim → "lihat kertasnya" (PRINTER_DIAM), kabel TIDAK dicoba (bisa dobel)', g && g.code === 'PRINTER_DIAM' && g.message === KALIMAT_TAK_DIKABARI && /terputus di tengah jalan/.test(g.asli) && A.hitung('CetakUsb.cetak') === 0, (g && g.code) + ' ' + (g && g.asli) + ' ' + A.catat.join(','));
      P = printer({ cetak: () => ({ status: 200, data: 'ok\r\n' }) }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: kiriman diterima tanpa nomor pekerjaan → hasil tidak diketahui, tanpa kabel', g && g.code === 'PRINTER_DIAM' && hasilTakDiketahui(g) && /tidak memberi nomor pekerjaan/.test(g.asli) && A.hitung('CetakUsb.cetak') === 0, g && g.asli);
      P = printer({ selesaiPada: 999 }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: printer tidak pernah melapor "printed" → berhenti bertanya sesudah batasnya, hasil tidak diketahui, tanpa kabel, kunci terbuka', g && g.code === 'PRINTER_DIAM' && P.st.tanyaTugas === JARINGAN.tanyaMaks && /pekerjaan 61/.test(g.asli)
        && A.hitung('CetakUsb.cetak') === 0 && printerSibuk() === false, (g && g.asli) + ' tanya ' + P.st.tanyaTugas);
      // printer lenyap dari jaringan sesudah menerima kiriman: tiap tanya makan lama → berhenti menurut JAM, jauh sebelum kunci cetak kedaluwarsa
      {
        const jamAsli = Date.now; let maju = 0; Date.now = () => jamAsli() + maju; JARINGAN.tanyaMaks = 50;
        P = printer({ tanya: () => { maju += 12000; lempar('timeout', 'SocketTimeoutException'); } }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
        Date.now = jamAsli; JARINGAN.tanyaMaks = 6;
        cek('jaringan: lama menunggu dibatasi ' + (JARINGAN.tungguMs / 1000) + ' detik (lebih pendek dari kunci cetak ' + (BATAS_SIBUK_MS / 1000) + ' detik) → berhenti sesudah beberapa tanya, hasil tidak diketahui', g && g.code === 'PRINTER_DIAM' && P.st.tanyaTugas === 3
          && JARINGAN.tungguMs + 2 * (JARINGAN.sambungMs + JARINGAN.bacaMs) + 20000 < BATAS_SIBUK_MS, (g && g.code) + ' tanya ' + P.st.tanyaTugas);
      }
      // halangan muncul di tengah cetak
      P = printer({ tanya: () => ({ status: 200, data: teksKeadaan({ no_paper: 1 }, 'not printed') }) }); A = pasang(P); g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: kertas habis di tengah cetak → "Cetak terhenti: kertas habis", kode printer, tanpa kabel', g && g.code === 'PRINTER_OUT_PAPER' && g.message === 'Cetak terhenti: kertas habis' && A.hitung('CetakUsb.cetak') === 0 && P.st.tanyaTugas === 1, g && g.message);
      // satu tanya yang gagal bukan kabar
      P = printer({ tanya: (isi, st) => { if (st.tanyaTugas === 1) lempar('timeout', 'SocketTimeoutException'); if (st.tanyaTugas === 2) return { status: 500, data: 'galat' }; return { status: 200, data: teksKeadaan({}, 'printed') }; } }); A = pasang(P);
      r = await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT });
      cek('jaringan: tanya pekerjaan yang gagal / dijawab aneh diulang, bukan dianggap gagal cetak', r.jalur === 'jaringan' && P.st.tanyaTugas === 3 && A.hitung('CetakUsb.cetak') === 0, JSON.stringify(r) + ' tanya ' + P.st.tanyaTugas);
      // satu cetakan pada satu waktu juga untuk jaringan
      let lepasCetak = null; P = printer({ cetak: (isi, st) => new Promise((ok) => { lepasCetak = () => { st.tugas += 1; ok({ status: 200, data: 'task_id: ' + st.tugas + '\r\n' }); }; }) }); A = pasang(P);
      const jl = cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT });
      for (let i = 0; i < 30 && !lepasCetak; i++) await Promise.resolve();
      g = null; try { await cetakAsli('G0A=', 'jaringan', { alamat: ALAMAT }); } catch (e) { g = e; }
      cek('jaringan: cetakan kedua selagi yang pertama belum dikabari → SEDANG_CETAK, tidak ada kiriman kedua', !!lepasCetak && g && g.code === 'SEDANG_CETAK' && P.st.url.filter((u) => u.indexOf('print.cgi') >= 0).length === 1, (g && g.code) + ' ' + P.st.url.join(' '));
      lepasCetak(); r = await jl;
      cek('jaringan: cetakan pertama selesai tanpa terganggu', r.jalur === 'jaringan' && r.tugas === '61', JSON.stringify(r));
      JARINGAN.jedaMs = 400; JARINGAN.tanyaMaks = 50;
    }
    cek('masihMencetak hanya untuk SEDANG_CETAK — bukan galat printer, bukan "hasil tidak diketahui"', masihMencetak({ code: 'SEDANG_CETAK' }) && !masihMencetak({ code: 'PRINTER_UNKNOWN' }) && !masihMencetak({ code: 'BELUM_KIRIM' }) && !masihMencetak(null)
      && !galatPrinter({ code: 'SEDANG_CETAK' }) && !hasilTakDiketahui({ code: 'SEDANG_CETAK' }));
    cek('kalimat "masih mencetak" tidak menyebut gagal dan menyuruh menunggu', !/gagal/i.test(KALIMAT_MASIH_MENCETAK) && /tunggu/.test(KALIMAT_MASIH_MENCETAK) && /jangan ketuk/.test(KALIMAT_MASIH_MENCETAK), KALIMAT_MASIH_MENCETAK);
  }

  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'aplikasi');
  cek('jalur aplikasi: hanya CetakUsb', r.jalur === 'aplikasi' && A.catat.join(',') === 'CetakUsb.cetak', A.catat.join(','));
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('x', 'BELUM_KIRIM'), 'CetakUsb.cetak': tolak('antarmuka dipegang aplikasi lain') });
  g = null; try { await cetakAsli('QUJD', 'sunmi'); } catch (e) { g = e; }
  cek('dua jalur gagal: KEDUA sebab sampai ke pemanggil — sebab jalur yang dipilih di depan, sebab kabel menyusul', g && g.message === 'x · kirim langsung lewat kabel USB juga gagal: antarmuka dipegang aplikasi lain' && g.sebabUtama === 'x', g && g.message);
  // penjaga di sisi aplikasi (PrinterSunmiPlugin › ambilPintu, butuh APK baru): perintah printer lain belum selesai → aplikasi menolak SEDANG_CETAK
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Printer masih mengerjakan perintah sebelumnya — tunggu kabarnya dulu', 'SEDANG_CETAK'), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
  cek('aplikasi menolak SEDANG_CETAK: sampai ke layar sebagai "tunggu kabarnya dulu" — TIDAK jatuh ke kabel (bisa dobel) dan TIDAK melepas sambungan cetakan yang sedang jalan',
    g && g.code === 'SEDANG_CETAK' && masihMencetak(g) && g.message === KALIMAT_MASIH_MENCETAK && /mengerjakan perintah sebelumnya/.test(g.asli) && A.catat.join(',') === 'PrinterSunmi.cetak' && printerSibuk() === false,
    (g && g.code) + ' · ' + (g && g.message) + ' · ' + A.catat.join(','));

  // ---- pindai ----
  A = pasangAplikasi(['Pindai', 'Lampu'], { 'Lampu.nyala': (isi) => ({ ok: true, kode: 0, isi }), 'Lampu.mati': () => ({ ok: true, kode: 0 }) });
  const dapat = []; const dapat2 = [];
  const lepas1 = padaPindai((x) => dapat.push(x.data)); padaPindai((x) => dapat2.push(x.data));
  const siar = A.dengar['Pindai.pindai'];
  cek('pindai: pendengar terpasang di plugin Pindai', typeof siar === 'function');
  if (siar) { siar({ data: 'MBR-0001' }); siar({ data: 12345 }); siar(null); siar({ data: '' }); lepas1(); siar({ data: '8991234567890' }); }
  cek('pindai: teks diteruskan, bukan-teks & kosong dibuang', dapat.join('|') === 'MBR-0001', dapat.join('|'));
  cek('pindai: pelepas hanya melepas pendengarnya sendiri', dapat2.join('|') === 'MBR-0001|8991234567890', dapat2.join('|'));
  cek('pindai: hasil terakhir tersimpan', pindaiTerakhir() && pindaiTerakhir().data === '8991234567890');

  // ---- lampu ----
  let L = await lampuBerhasil();
  cek('lampu berhasil: hijau (2), tidak berkedip, padam sendiri', L.ok && L.isi.warna === 2 && L.isi.kedip === false && L.isi.batasMs > 0, JSON.stringify(L));
  L = await lampuGagal();
  cek('lampu gagal: merah (1), berkedip, padam sendiri', L.ok && L.isi.warna === 1 && L.isi.kedip === true && L.isi.batasMs > 0, JSON.stringify(L));
  cek('lampu padam memanggil Lampu.mati', (await lampuPadam()).ok === true && A.hitung('Lampu.mati') === 1);
  // ---- paket S4: lampu berwarna per kejadian ----
  const AL = lampuAtur(null);
  cek('lampu bawaan: lima kejadian; nota tersimpan hijau, cetak gagal merah berkedip', Object.keys(AL).join(',') === 'berhasil,gagal,kenal,asing,kertas' && AL.berhasil.warna === 'hijau' && AL.berhasil.kedip === false && AL.gagal.warna === 'merah' && AL.gagal.kedip === true, JSON.stringify(AL));
  cek('lampu bawaan: tidak ada dua kejadian yang terlihat sama', new Set(Object.keys(AL).map((k) => AL[k].warna + '|' + AL[k].kedip)).size === 5);
  const AS = lampuAtur({ berhasil: { warna: 'sian', kedip: true, detik: 3 }, gagal: { warna: 'ungu', kedip: 'ya', detik: 99 }, kenal: { warna: 'mati' }, asing: 'x', lain: { warna: 'putih' } });
  cek('setelan lampu tersimpan dipakai; isi tidak sah dibuang satu per satu (bawaannya tetap)', AS.berhasil.warna === 'sian' && AS.berhasil.kedip === true && AS.berhasil.detik === 3 && AS.gagal.warna === 'merah' && AS.gagal.kedip === true && AS.gagal.detik === 6 && AS.kenal.warna === 'mati' && AS.asing.warna === 'kuning' && AS.lain === undefined, JSON.stringify(AS));
  L = await lampuKejadian('kenal');
  cek('lampu kejadian "dikenali": biru (3), lama nyala = detik × 1000, tidak berkedip', L.ok && L.isi.warna === 3 && L.isi.batasMs === 1000 && L.isi.kedip === false, JSON.stringify(L));
  L = await lampuAsing(); cek('lampu "belum dikenal": kuning (4) berkedip', L.ok && L.isi.warna === 4 && L.isi.kedip === true, JSON.stringify(L));
  L = await lampuKertas(); cek('lampu "kertas hampir habis": magenta (6) berkedip', L.ok && L.isi.warna === 6 && L.isi.kedip === true, JSON.stringify(L));
  L = await lampuKejadian('berhasil', { warna: 'putih', kedip: true, detik: 2.5 });
  cek('lampu kejadian: timpaan tombol Coba dipakai', L.ok && L.isi.warna === 7 && L.isi.kedip === true && L.isi.batasMs === 2500, JSON.stringify(L));
  const nNyala = A.hitung('Lampu.nyala'); L = await lampuKejadian('asing', { warna: 'mati' });
  cek('kejadian yang diatur "tidak menyala" tidak memanggil lampu', L.ok === false && L.mati === true && A.hitung('Lampu.nyala') === nNyala);
  cek('kejadian tak dikenal tidak menyalakan apa-apa', (await lampuKejadian('entah')).ok === false && A.hitung('Lampu.nyala') === nNyala);
  const gudang = {}; globalThis.localStorage = { getItem: (k) => (k in gudang ? gudang[k] : null), setItem: (k, v) => { gudang[k] = String(v); } };
  cek('simpan lampu: tersimpan di perangkat & langsung dipakai; kejadian lain tetap bawaan', lampuSimpan({ berhasil: { warna: 'magenta', kedip: false, detik: 2 } }) === true && JSON.parse(gudang[LAMPU_KUNCI]).berhasil.warna === 'magenta' && lampuAtur().berhasil.warna === 'magenta' && lampuAtur().gagal.warna === 'merah');
  L = await lampuBerhasil(); cek('lampuBerhasil mengikuti setelan perangkat', L.ok && L.isi.warna === 6 && L.isi.batasMs === 2000, JSON.stringify(L));
  gudang[LAMPU_KUNCI] = '{rusak'; cek('simpanan lampu rusak → bawaan, tidak melempar', lampuAtur().berhasil.warna === 'hijau' && lampuAtur().kertas.warna === 'magenta');
  delete globalThis.localStorage;

  A = pasangAplikasi(['CetakUsb'], {});
  cek('aplikasi tanpa plugin Lampu: { ok: false } tanpa memanggil', (await lampuBerhasil()).ok === false && A.catat.length === 0, A.catat.join(','));
  A = pasangAplikasi(['Lampu'], { 'Lampu.nyala': tolak('layanan mati') });
  const L1 = await lampuBerhasil(); const L2 = await lampuBerhasil();
  cek('lampu yang menolak: tidak melempar, lalu berhenti memanggil', L1.ok === false && L2.ok === false && A.hitung('Lampu.nyala') === 1, A.catat.join(','));

  // ---- kartu kemampuan ----
  A = pasangAplikasi(['CetakUsb', 'Perangkat', 'Pindai'], { 'Perangkat.info': () => ({ merek: 'SUNMI', model: 'CPad', versiApk: '1.6' }), 'Pindai.info': () => ({ terpasang: true }) });
  const K = await kemampuan();
  cek('kemampuan: plugin yang ada ditanya, yang tidak ada dilewati', K.aplikasi && K.info.model === 'CPad' && K.pindai.terpasang === true && K.lampu === null && K.plugin.Lampu === false && A.hitung('Lampu.dukung') === 0, JSON.stringify(K));

  // ---- NFC (paket S2a) ----
  const lepasN0 = padaTempel(() => {}); lepasN0();
  cek('aplikasi tanpa plugin Nfc: padaTempel tidak memasang pendengar', A.dengar['Nfc.tempel'] === undefined);
  A = pasangAplikasi(['Nfc'], { 'Nfc.info': () => ({ ada: true, nyala: true }) });
  const kartu = []; const kartu2 = [];
  const lepasN = padaTempel((x) => kartu.push(x.uid)); padaTempel((x) => kartu2.push(x.uid + ':' + x.jenis.join('+')));
  const tempel = A.dengar['Nfc.tempel'];
  cek('nfc: pendengar terpasang di plugin Nfc', typeof tempel === 'function');
  if (tempel) { tempel({ uid: '04a1b2c3', jenis: ['NfcA', 'MifareUltralight'] }); tempel({ uid: 'XYZ12345' }); tempel({ uid: '04A1B' }); tempel({ uid: '04A1B2' }); tempel({ uid: 12345678 }); tempel(null); tempel({ uid: '0102030405060708090A0B' }); lepasN(); tempel({ uid: '04A1B2C3D4E5F6' }); }
  cek('nfc: nomor seri heksa 4–10 byte diteruskan berhuruf besar; bentuk lain dibuang', kartu.join('|') === '04A1B2C3', kartu.join('|'));
  cek('nfc: pelepas hanya melepas pendengarnya sendiri; jenis kartu ikut', kartu2.join('|') === '04A1B2C3:NfcA+MifareUltralight|04A1B2C3D4E5F6:', kartu2.join('|'));
  cek('nfc: kartu terakhir tersimpan', tempelTerakhir() && tempelTerakhir().uid === '04A1B2C3D4E5F6');
  const KN = await kemampuan();
  cek('kemampuan: NFC ditanya bila pluginnya ada', KN.plugin.Nfc === true && KN.nfc && KN.nfc.ada === true && KN.nfc.nyala === true && KN.lampu === null, JSON.stringify(KN));

  // ================= paket S4: Bluetooth, mode kertas, label, sidik jari =================
  let isiCetak = null;
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': (isi) => { isiCetak = isi; return { nama: 'CloudPrint_0001' }; }, 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'sunmi-bt');
  cek('jalur sunmi-bt: SDK dipanggil dengan lewat = bt, jalurnya pulang apa adanya, CetakUsb tidak disentuh', r.jalur === 'sunmi-bt' && isiCetak.lewat === 'bt' && isiCetak.data === 'QUJD' && A.hitung('CetakUsb.cetak') === 0, JSON.stringify(r) + JSON.stringify(isiCetak));
  r = await cetakAsli('QUJD', 'sunmi');
  cek('jalur sunmi (kabel): lewat = usb', r.jalur === 'sunmi' && isiCetak.lewat === 'usb', JSON.stringify(isiCetak));
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Bluetooth tablet mati', 'BELUM_KIRIM'), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'sunmi-bt');
  cek('Bluetooth gagal sebelum kirim: jatuh ke USB langsung tepat sekali, sebabnya ikut pulang', r.jalur === 'aplikasi' && r.cadanganDari === 'Bluetooth tablet mati' && A.catat.join(',') === 'PrinterSunmi.cetak,PrinterSunmi.lepas,CetakUsb.cetak', A.catat.join(','));
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('halangan', 'PRINTER_COVER'), 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
  cek('Bluetooth: printer menjawab ada halangan → galat dilempar, TIDAK dicetak ulang lewat kabel', g && g.code === 'PRINTER_COVER' && A.hitung('CetakUsb.cetak') === 0, A.catat.join(','));
  // uji owner 20 Nov (APK 1.19): Bluetooth gagal DAN kabel tidak tercolok — layar dulu hanya menyebut "Printer USB tidak ditemukan"
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('Printer SUNMI tidak bisa disambung lewat Bluetooth: printer tidak menjawab', 'BELUM_KIRIM'), 'CetakUsb.cetak': tolak('Printer USB tidak ditemukan', 'KABEL') });
  g = null; try { await cetakAsli('QUJD', 'sunmi-bt'); } catch (e) { g = e; }
  cek('Bluetooth gagal & kabel tidak tercolok: sebab Bluetooth terbaca di depan, sebab kabel menyusul, kode galat = milik jalur kabel',
    g && g.message.indexOf('Printer SUNMI tidak bisa disambung lewat Bluetooth: printer tidak menjawab · ') === 0 && /kabel USB juga gagal: Printer USB tidak ditemukan$/.test(g.message)
    && g.code === 'KABEL' && !galatPrinter(g) && A.catat.join(',') === 'PrinterSunmi.cetak,PrinterSunmi.lepas,CetakUsb.cetak', g && (g.message + ' · ' + g.code + ' · ' + A.catat.join(',')));
  cek('lewatJalur: hanya sunmi-bt yang berarti Bluetooth', lewatJalur('sunmi-bt') === 'bt' && lewatJalur('sunmi') === 'usb' && lewatJalur('aplikasi') === 'usb' && lewatJalur(undefined) === 'usb');

  let isiMode = null, isiTspl = null, isiStatus = null, isiTanyaMode = null;
  A = pasangAplikasi(['PrinterSunmi'], { 'PrinterSunmi.setelMode': (isi) => { isiMode = isi; return { dikirim: true }; }, 'PrinterSunmi.tspl': (isi) => { isiTspl = isi; return { byte: 4 }; },
    'PrinterSunmi.status': (isi) => { isiStatus = isi; return { siap: true }; }, 'PrinterSunmi.mode': (isi) => { isiTanyaMode = isi; return { mode: 'label printer' }; }, 'PrinterSunmi.bt': () => ({ ada: true, izin: true, nyala: true, daftar: [{ nama: 'CloudPrint_0001', mac: 'AA:BB' }] }) });
  await printerSetelMode('2', 'bt');
  cek('pindah mode: angka mode & jalur diteruskan', isiMode && isiMode.mode === 2 && isiMode.lewat === 'bt', JSON.stringify(isiMode));
  let nTolak = 0; for (const m of [0, 4, 5, 'label', null, 1.5]) { try { await printerSetelMode(m); } catch (e) { if (e.code === 'SALAH_ISI') nTolak++; } }
  cek('pindah mode: mode di luar 1, 2, 3 ditolak TANPA memanggil printer', nTolak === 6 && A.hitung('PrinterSunmi.setelMode') === 1, nTolak + ' / ' + A.hitung('PrinterSunmi.setelMode'));
  cek('mode kertas: tiga mode bernomor 1 2 3 (struk, label, tanpa alas)', MODE_KERTAS.map((x) => x[0]).join(',') === '1,2,3' && /struk/.test(MODE_KERTAS[0][1]) && /label/.test(MODE_KERTAS[1][1]) && /tanpa alas/.test(MODE_KERTAS[2][1]));
  cek('jawaban printer dibaca: struk / label / tidak dikenali', bacaModeKertas('Receipt printer') === 'struk' && bacaModeKertas('label printer') === 'label' && bacaModeKertas('') === '' && bacaModeKertas(null) === '' && bacaModeKertas('NORMAL') === '');
  // uji owner 20 Nov 2026 (APK 1.22): printer toko menjawab "Linerless printer" untuk mode 3, dan "" sesaat sesudah pindah mode
  cek('jawaban "Linerless printer" = mode tanpa alas (bukan "tidak dikenali")', bacaModeKertas('Linerless printer') === 'tanpa-alas' && bacaModeKertas('LINERLESS PRINTER') === 'tanpa-alas' && MODE_NAMA['tanpa-alas'] === 'STIKER TANPA ALAS');
  const km = (t) => kalimatModeKertas(t);
  cek('kalimat mode: tiga mode terbaca = baik, teks asli printer ikut', km('Receipt printer').baik && /mode STRUK \(kertas bersambung\) — "Receipt printer"$/.test(km('Receipt printer').teks)
    && km('label printer').baik && /mode LABEL \(stiker bercelah\)/.test(km('label printer').teks) && km('Linerless printer').baik && /mode STIKER TANPA ALAS — "Linerless printer"$/.test(km('Linerless printer').teks), km('Linerless printer').teks);
  cek('kalimat mode: jawaban kosong = "belum menjawab", bukan "tidak dikenali"', !km('').baik && /belum menjawab/.test(km('').teks) && !/tidak dikenali/.test(km('').teks) && !km(null).baik && /belum menjawab/.test(km('  ').teks)
    && !km('NORMAL').baik && /tidak dikenali — "NORMAL"$/.test(km('NORMAL').teks), km('').teks);
  cek('label lawan mode: hanya dua pasangan yang pasti salah yang ditolak', /mode STRUK/.test(labelTolakMode('tspl', 'struk')) && /mode LABEL/.test(labelTolakMode('struk', 'label'))
    && labelTolakMode('tspl', 'label') === '' && labelTolakMode('struk', 'struk') === '' && labelTolakMode('struk', 'tanpa-alas') === '' && labelTolakMode('tspl', 'tanpa-alas') === ''
    && labelTolakMode('struk', '') === '' && labelTolakMode('tspl', '') === '');
  cek('tanya mode: jalur diteruskan, jawaban printer pulang apa adanya', (await printerMode('bt')).mode === 'label printer' && isiTanyaMode.lewat === 'bt' && (await printerMode(), isiTanyaMode.lewat === 'usb'));
  await kirimTspl('CLS\nPRINT 1\n', 'usb');
  cek('perintah label: data & jalur diteruskan apa adanya', isiTspl && isiTspl.data === 'CLS\nPRINT 1\n' && isiTspl.lewat === 'usb', JSON.stringify(isiTspl));
  await printerStatus('bt'); const lewatBt = isiStatus.lewat; await printerStatus();
  cek('periksa printer: jalur bt diteruskan; tanpa isi = usb', lewatBt === 'bt' && isiStatus.lewat === 'usb');
  cek('daftar printer Bluetooth pulang apa adanya', (await printerBt()).daftar[0].nama === 'CloudPrint_0001');
  let isiJaga = null;
  // uji owner 20 Nov 2026 malam (APK 1.25, jalur jaringan): tombol mode hanya mencari di USB → "tidak ditemukan di USB — pastikan tercolok ke stand"
  {
    const urut = []; let jw = {};
    const sdk = (jawab) => { urut.length = 0; jw = jawab; return pasangAplikasi(['PrinterSunmi'], { 'PrinterSunmi.mode': (isi) => { urut.push('mode:' + isi.lewat); return jw[isi.lewat](); }, 'PrinterSunmi.setelMode': (isi) => { urut.push('setel:' + isi.lewat); return jw[isi.lewat](); } }); };
    const btMati = tolak('Bluetooth tablet mati — nyalakan di Setelan tablet', 'BELUM_KIRIM'); const usbKosong = tolak('Printer SUNMI tidak ditemukan di USB — pastikan printer menyala dan tercolok ke stand', 'BELUM_KIRIM');
    sdk({ bt: () => ({ mode: 'Receipt printer' }), usb: usbKosong }); let rm = await lewatSdk('jaringan', (l) => printerMode(l));
    cek('mode di jalur jaringan: Bluetooth ditanya DULU dan jawabannya dipakai; kabel tidak disentuh; hasil menyebut lewat mana', rm.mode === 'Receipt printer' && rm.lewat === 'bt' && urut.join(',') === 'mode:bt' && URUT_SDK_JARINGAN.join(',') === 'bt,usb', JSON.stringify(rm) + ' ' + urut.join(','));
    sdk({ bt: btMati, usb: () => ({ mode: 'label printer' }) }); rm = await lewatSdk('jaringan', (l) => printerMode(l));
    cek('mode di jalur jaringan: Bluetooth belum bisa (belum ada yang dikirim) → kabel dicoba, jawabannya dipakai', rm.mode === 'label printer' && rm.lewat === 'usb' && urut.join(',') === 'mode:bt,mode:usb', JSON.stringify(rm) + ' ' + urut.join(','));
    sdk({ bt: btMati, usb: usbKosong }); g = null; try { await lewatSdk('jaringan', (l) => printerMode(l)); } catch (e) { g = e; }
    cek('mode di jalur jaringan: dua-duanya belum bisa → SATU kalimat yang menyebut kenapa lewat jaringan tidak bisa + sebab Bluetooth + sebab kabel', g && g.code === 'BELUM_KIRIM' && /^lewat jaringan mode kertas tidak bisa diurus/.test(g.message)
      && g.message.indexOf('Bluetooth: Bluetooth tablet mati') > 0 && g.message.indexOf('kabel USB: Printer SUNMI tidak ditemukan di USB') > g.message.indexOf('Bluetooth: Bluetooth tablet mati') && urut.join(',') === 'mode:bt,mode:usb', g && g.message);
    sdk({ bt: tolak('Printer tidak menjawab saat ditanya mode kertasnya', 'PRINTER_DIAM'), usb: () => ({ mode: 'label printer' }) }); g = null; try { await lewatSdk('jaringan', (l) => printerMode(l)); } catch (e) { g = e; }
    cek('mode di jalur jaringan: printer DIAM lewat Bluetooth (bukan "belum kirim") → dilempar apa adanya, kabel TIDAK dicoba', g && g.code === 'PRINTER_DIAM' && urut.join(',') === 'mode:bt', (g && g.code) + ' ' + urut.join(','));
    sdk({ bt: () => ({ dikirim: true }), usb: usbKosong }); rm = await lewatSdk('jaringan', (l) => printerSetelMode(2, l));
    cek('pindah mode di jalur jaringan: perintah dikirim SEKALI, lewat Bluetooth', rm.dikirim === true && rm.lewat === 'bt' && urut.join(',') === 'setel:bt', JSON.stringify(rm) + ' ' + urut.join(','));
    sdk({ bt: () => ({ dikirim: true }), usb: () => ({ dikirim: true }) }); g = null; try { await lewatSdk('jaringan', (l) => printerSetelMode(7, l)); } catch (e) { g = e; }
    cek('pindah mode di jalur jaringan: mode tak dikenal ditolak TANPA menyentuh printer lewat cara mana pun', g && g.code === 'SALAH_ISI' && urut.length === 0, (g && g.code) + ' ' + urut.join(','));
    sdk({ bt: () => ({ mode: 'Receipt printer' }), usb: () => ({ mode: 'label printer' }) });
    const rb = await lewatSdk('sunmi-bt', (l) => printerMode(l)); const ru = await lewatSdk('sunmi', (l) => printerMode(l)); const ra = await lewatSdk('usb', (l) => printerMode(l));
    cek('jalur selain jaringan: mode tetap ditanya lewat jalurnya sendiri, satu kali, tanpa cara cadangan', rb.lewat === 'bt' && rb.mode === 'Receipt printer' && ru.lewat === 'usb' && ru.mode === 'label printer' && ra.lewat === 'usb' && urut.join(',') === 'mode:bt,mode:usb,mode:usb', urut.join(','));
    sdk({ bt: () => ({ mode: 'x' }), usb: usbKosong }); g = null; try { await lewatSdk('sunmi', (l) => printerMode(l)); } catch (e) { g = e; }
    cek('jalur kabel: kabel tidak tercolok TIDAK diam-diam pindah ke Bluetooth', g && /tidak ditemukan di USB/.test(g.message) && urut.join(',') === 'mode:usb', (g && g.message) + ' ' + urut.join(','));
    cek('nama cara menyambung untuk layar', namaLewat('bt') === 'Bluetooth' && namaLewat('usb') === 'kabel USB' && namaLewat() === 'kabel USB');
  }
  const jaga = (jawab) => pasangAplikasi(['PrinterSunmi'], { 'PrinterSunmi.mode': (isi) => { isiJaga = isi; return typeof jawab === 'function' ? jawab() : { mode: jawab }; } });
  const coba = async (cara, lewat) => { try { return { hasil: await pastikanModeLabel(cara, lewat) }; } catch (e) { return { galat: e }; } };
  A = jaga('label printer'); let pj = await coba('struk', 'bt');
  cek('penjaga label: bahasa struk ke printer di mode LABEL ditolak (SALAH_MODE) — printer ditanya lewat jalur yang sama', pj.galat && pj.galat.code === 'SALAH_MODE' && /mode LABEL/.test(pj.galat.message) && isiJaga.lewat === 'bt' && A.catat.join(',') === 'PrinterSunmi.mode', pj.galat && pj.galat.message);
  A = jaga('Receipt printer'); pj = await coba('tspl', 'usb');
  cek('penjaga label: perintah label ke printer di mode STRUK ditolak (SALAH_MODE)', pj.galat && pj.galat.code === 'SALAH_MODE' && /mode STRUK/.test(pj.galat.message) && isiJaga.lewat === 'usb', pj.galat && pj.galat.message);
  A = jaga('label printer'); pj = await coba('tspl', 'bt');
  const pj2 = (A = jaga('Receipt printer'), await coba('struk', 'usb')); const pj3 = (A = jaga('Linerless printer'), await coba('struk', 'usb')); const pj4 = (A = jaga(''), await coba('tspl', 'usb'));
  cek('penjaga label: pasangan yang cocok, mode tanpa alas, dan jawaban kosong dibiarkan lewat', pj.hasil && pj.hasil.mode === 'label' && pj.hasil.ditanya && pj2.hasil && pj2.hasil.mode === 'struk'
    && pj3.hasil && pj3.hasil.mode === 'tanpa-alas' && pj4.hasil && pj4.hasil.mode === '' && pj4.hasil.ditanya, JSON.stringify([pj, pj2, pj3, pj4]));
  A = jaga(tolak('Printer SUNMI tidak ditemukan di USB', 'BELUM_KIRIM')); pj = await coba('struk', 'usb'); const pj5 = await coba('tspl', 'usb');
  cek('penjaga label: printer tak bisa ditanya — bahasa struk dibiarkan (jalur cetak masih bisa jatuh ke kabel), perintah label melempar sebab aslinya', pj.hasil && pj.hasil.ditanya === false && pj.hasil.mode === ''
    && pj5.galat && pj5.galat.code === 'BELUM_KIRIM' && /tidak ditemukan di USB/.test(pj5.galat.message), JSON.stringify(pj) + ' ' + (pj5.galat && pj5.galat.message));

  A = pasangAplikasi(['Biometrik'], { 'Biometrik.info': () => ({ ada: false, terdaftar: false, kode: 12, kalimat: 'tablet ini tidak punya sensor sidik jari' }), 'Biometrik.minta': (isi) => ({ ok: true, isi }) });
  const KB = await kemampuan();
  cek('kemampuan: sidik jari ditanya bila pluginnya ada', KB.plugin.Biometrik === true && KB.biometrik && KB.biometrik.ada === false && KB.biometrik.kode === 12, JSON.stringify(KB));
  const st = (kode, pesan) => { const e = new Error(pesan || 'x'); if (kode) e.code = kode; return sidikJariTolak(e); };
  cek('sidik jari dibatalkan orangnya (kode 5, 10, 13) = batal berkalimat toko, bukan kegagalan', [5, 10, 13].every((k) => st('BIOMETRIK_' + k, 'Fingerprint operation canceled by user.').batal && st('BIOMETRIK_' + k).kalimat === 'uji dibatalkan'));
  cek('sidik jari gagal sungguhan tetap gagal: terkunci, belum ada jari, tanpa sensor; kode tak dikenal = pesan aslinya', !st('BIOMETRIK_7').batal && /terlalu banyak/.test(st('BIOMETRIK_7').kalimat)
    && /belum ada jari/.test(st('BIOMETRIK_11').kalimat) && /sensor/.test(st('BIOMETRIK_12').kalimat) && !st('BIOMETRIK_99', 'aneh').batal && st('BIOMETRIK_99', 'aneh').kalimat === 'aneh'
    && st('BIOMETRIK_GAGAL', 'Layar aplikasi belum siap').kalimat === 'Layar aplikasi belum siap' && !st('', 'tanpa kode').batal && st('BIOMETRIK_100').batal === false);
  cek('uji sidik jari memanggil Biometrik.minta; info pulang apa adanya', (await sidikJariUji()).isi.judul === 'Uji sidik jari' && (await sidikJariInfo()).kalimat === 'tablet ini tidak punya sensor sidik jari');
  A = pasangAplikasi(['CetakUsb'], {}); const KB0 = await kemampuan();
  cek('aplikasi lama tanpa plugin Biometrik: tidak dipanggil, biometrik = null', KB0.biometrik === null && KB0.plugin.Biometrik === false && A.hitung('Biometrik.info') === 0, A.catat.join(','));

  print(JSON.stringify(hasil));
})().catch((e) => { print(JSON.stringify([{ nama: 'pemeriksa jatuh', ok: false, ket: String(e && e.stack || e) }])); });
"""

MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale|smallestScreenSize|screenLayout|uiMode"
            android:name=".MainActivity"
            android:launchMode="singleTask"
            android:exported="true">

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false">
        </provider>
    </application>

    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
'''

GRADLE = '''apply plugin: 'com.android.application'

android {
    namespace "id.miqbal.tokoberas"
    defaultConfig {
        applicationId "id.miqbal.tokoberas"
        versionCode 1
        versionName "1.0"
    }
}

repositories {
    flatDir{
        dirs '../capacitor-cordova-android-plugins/src/main/libs', 'libs'
    }
}

dependencies {
    implementation fileTree(include: ['*.jar'], dir: 'libs')
    implementation "androidx.appcompat:appcompat:$androidxAppCompatVersion"
}

apply from: 'capacitor.build.gradle'
'''


def siapkan(sumber):
    # modul tanpa impor → buang kata `export` supaya jalan sebagai skrip biasa di jsc
    return sumber.replace('export const ', 'const ').replace('export async function ', 'async function ').replace('export function ', 'function ')


def jalankan_jsc(sumber):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(siapkan(sumber) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return [{'nama': 'jsc tidak jalan', 'ok': False, 'ket': (r.stderr or r.stdout).strip()[:400]}]
    return json.loads(r.stdout.strip().splitlines()[-1])


def muat_pasang(sumber):
    ruang = {'__name__': 'pasang_uji', '__file__': PASANG}
    exec(compile(sumber, PASANG, 'exec'), ruang)
    return ruang


def periksa_pasang(sumber):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    try: P = muat_pasang(sumber)
    except Exception as e: return [{'nama': 'pasang.py tidak bisa dimuat', 'ok': False, 'ket': repr(e)}]
    try: m = P['ubah_manifest'](MANIFEST)
    except Exception as e: return [{'nama': 'ubah_manifest jatuh pada manifest Capacitor', 'ok': False, 'ket': repr(e)}]
    ok('manifest: USB host + penyaring printer', 'android.hardware.usb.host' in m and 'USB_DEVICE_ATTACHED' in m and '@xml/device_filter' in m)
    ok('manifest: <queries> scanner SUNMI & layanan perangkat SUNMI, di luar <application>',
       all(('<package android:name="%s" />' % p) in m for p in ('com.sunmi.scanner', 'com.sunmi.tmservice')) and m.index('<queries>') < m.index('<application') and m.count('<queries>') == 1)
    ok('manifest: penjaga "Hapus data" terpasang & aktivitasnya dideklarasikan tertutup',
       'android:manageSpaceActivity="id.miqbal.tokoberas.KelolaRuangActivity"' in m and '<activity android:name="id.miqbal.tokoberas.KelolaRuangActivity" android:exported="false" />' in m)
    ok('manifest: izin NFC ada, pembaca NFC TIDAK diwajibkan, di luar <application>, tepat sekali',
       m.count('<uses-permission android:name="android.permission.NFC" />') == 1 and m.count('<uses-feature android:name="android.hardware.nfc" android:required="false" />') == 1
       and m.index('android.permission.NFC') < m.index('<application') and 'android.hardware.nfc" android:required="true"' not in m)
    ok('manifest: izin sidik jari ada, sensor TIDAK diwajibkan, di luar <application>, tepat sekali',
       m.count('<uses-permission android:name="android.permission.USE_BIOMETRIC" />') == 1 and m.count('<uses-feature android:name="android.hardware.fingerprint" android:required="false" />') == 1
       and m.index('android.permission.USE_BIOMETRIC') < m.index('<application') and 'android.hardware.fingerprint" android:required="true"' not in m)
    ok('manifest: tidak meminta izin lokasi (Bluetooth memakai perangkat yang sudah dipasangkan, tanpa pencarian)', 'ACCESS_FINE_LOCATION' not in m and 'ACCESS_COARSE_LOCATION' not in m)
    ok('manifest: allowBackup mati', 'android:allowBackup="false"' in m and 'android:allowBackup="true"' not in m)
    # paket jaringan (20 Nov 2026): printer di jaringan lokal hanya bicara HTTP polos
    tag = m[m.index('<application'):]; tag = tag[:tag.index('>')]
    ok('manifest: HTTP polos diizinkan (printer jaringan) — tepat sekali, di tag <application>', m.count('android:usesCleartextTraffic="true"') == 1 and 'android:usesCleartextTraffic="true"' in tag and 'usesCleartextTraffic="false"' not in m, tag)
    ok('manifest: yang sudah menulis usesCleartextTraffic="false" dibalik, tetap tepat sekali',
       P['ubah_manifest'](MANIFEST.replace('<application', '<application\n        android:usesCleartextTraffic="false"', 1)).count('android:usesCleartextTraffic="true"') == 1)
    cc_json = json.load(open(os.path.join(AKAR, 'apk', 'capacitor.config.json'), encoding='utf-8'))
    ok('capacitor.config.json: halaman toko tetap https dan isi campuran di WebView tetap DITOLAK (izin HTTP polos hanya untuk permintaan ke printer)',
       cc_json.get('android', {}).get('allowMixedContent') is False and cc_json.get('server', {}).get('url', '').startswith('https://') and cc_json.get('server', {}).get('androidScheme') == 'https', cc_json)
    cc = re.search(r'android:configChanges="([^"]*)"', m).group(1).split('|')
    ok('manifest: configChanges memuat navigation, keyboard, keyboardHidden tanpa kembar', all(x in cc for x in ('navigation', 'keyboard', 'keyboardHidden')) and len(cc) == len(set(cc)), '|'.join(cc))
    ok('manifest: aktivitas utama tetap satu & masih bisa dibuka', m.count('android:name=".MainActivity"') == 1 and 'android.intent.category.LAUNCHER' in m and m.count('</activity>') == 1)
    ok('manifest: dijalankan dua kali = sama', P['ubah_manifest'](m) == m)

    def ditolak(f, *a):
        try: f(*a)
        except P['Tolak']: return True
        except Exception: return False
        return False
    ok('manifest ber-networkSecurityConfig DITOLAK (atribut HTTP polos akan diam-diam tidak berlaku)', ditolak(P['ubah_manifest'], MANIFEST.replace('<application', '<application\n        android:networkSecurityConfig="@xml/jaringan"', 1)))
    ok('manifest tanpa configChanges DITOLAK', ditolak(P['ubah_manifest'], MANIFEST.replace('android:configChanges', 'android:lain')))
    ok('manifest dua aktivitas DITOLAK', ditolak(P['ubah_manifest'], MANIFEST.replace('</activity>', '</activity>\n<activity android:name=".Lain"></activity>')))

    try: g = P['ubah_gradle'](GRADLE, 6)
    except Exception as e: h.append({'nama': 'ubah_gradle jatuh pada build.gradle Capacitor', 'ok': False, 'ket': repr(e)}); return h
    ok('gradle: versi dari nomor jalan', 'versionCode 6' in g and 'versionName "1.6"' in g)
    pustaka = re.findall(r"implementation '(com\.sunmi:[^']+)'", g)
    ok('gradle: dua pustaka resmi SUNMI, versi dikunci, tepat sekali', sorted(pustaka) == sorted(P['PUSTAKA']) and len(pustaka) == 2 and all(re.search(r':\d+(\.\d+)+$', x) for x in pustaka), pustaka)
    ok('gradle: pustaka printer luar & SunmiCustomer API', any(x.startswith('com.sunmi:external-printerlibrary2:') for x in pustaka) and any(x.startswith('com.sunmi:customerservice:') for x in pustaka))
    ok('gradle: pustaka sidik jari AndroidX, versi dikunci, tepat sekali', g.count("implementation 'androidx.biometric:biometric:1.1.0'") == 1 and P['PUSTAKA_LAIN'] == ('androidx.biometric:biometric:1.1.0',))
    ok('gradle: pustaka di dalam blok dependencies aplikasi', g.index('dependencies {') < g.index("implementation 'com.sunmi:") < g.index("apply from: 'capacitor.build.gradle'"))
    ok('gradle: dijalankan dua kali = sama', P['ubah_gradle'](g, 6) == g)
    ok('gradle tanpa versionCode DITOLAK', ditolak(P['ubah_gradle'], GRADLE.replace('versionCode 1', ''), 6))
    ok('gradle tanpa blok dependencies DITOLAK', ditolak(P['ubah_gradle'], GRADLE.replace('dependencies {', 'ketergantungan {'), 6))
    return h


def baca(*bagian):
    with open(os.path.join(AKAR, *bagian), encoding='utf-8') as f: return f.read()


def periksa_statis(perangkat_js):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    utama = baca('apk', 'tambahan', 'MainActivity.java')
    plugin = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(AKAR, 'apk', 'tambahan', '*Plugin.java')))
    ok('tujuh plugin perangkat ada', plugin == ['BiometrikPlugin', 'CetakUsbPlugin', 'LampuPlugin', 'NfcPlugin', 'PerangkatPlugin', 'PindaiPlugin', 'PrinterSunmiPlugin'], plugin)
    belum = [p for p in plugin if ('registerPlugin(%s.class);' % p) not in utama]
    ok('tiap plugin terdaftar di MainActivity sebelum super.onCreate', not belum and utama.index('registerPlugin(') < utama.index('super.onCreate('), belum)
    nama = {}
    for p in plugin:
        m = re.search(r'@CapacitorPlugin\(name = "(\w+)"[,)]', baca('apk', 'tambahan', p + '.java')); nama[p] = m.group(1) if m else ''
    ok('nama plugin di Java = nama yang dipanggil halaman', nama == {'BiometrikPlugin': 'Biometrik', 'CetakUsbPlugin': 'CetakUsb', 'LampuPlugin': 'Lampu', 'NfcPlugin': 'Nfc', 'PerangkatPlugin': 'Perangkat', 'PindaiPlugin': 'Pindai', 'PrinterSunmiPlugin': 'PrinterSunmi'}, nama)
    dipanggil = set(re.findall(r"panggilAsli\('(\w+)', '(\w+)'", perangkat_js + baca('baru', 'js', 'inti', 'printer.js')))
    # CapacitorHttp = plugin INTI Capacitor (selalu terdaftar: Bridge.registerAllPlugins), bukan berkas di apk/tambahan — dipakai jalur jaringan
    inti = {(p, m) for p, m in dipanggil if p == 'CapacitorHttp'}
    ok('plugin inti Capacitor yang dipanggil halaman: hanya CapacitorHttp.request, dan Capacitor-nya memang versi yang punya plugin itu (≥ 4)',
       inti == {('CapacitorHttp', 'request')} and re.search(r'"@capacitor/android":\s*"\^?([4-9]|\d\d)\.', baca('apk', 'package.json')), sorted(inti))
    hilang = [p + '.' + m for p, m in sorted(dipanggil - inti) if not re.search(r'@PluginMethod\s+public void ' + m + r'\(', baca('apk', 'tambahan', p + 'Plugin.java'))]
    ok('tiap metode yang dipanggil halaman ada di plugin Java-nya', len(dipanggil) >= 13 and not hilang, hilang or sorted(dipanggil))
    sunmi = baca('apk', 'tambahan', 'PrinterSunmiPlugin.java')
    ok('PrinterSunmi: kode BELUM_KIRIM & PRINTER_ sama dengan yang dibaca perangkat.js', 'BELUM_KIRIM = "BELUM_KIRIM"' in sunmi and '"PRINTER_" + namaStatus(s)' in sunmi and '"PRINTER_DIAM"' in sunmi and "indexOf('PRINTER_') === 0" in perangkat_js)
    ok('PrinterSunmi: keadaan printer ditanya SEBELUM data dikirim', sunmi.index('siapkan(call, p -> tanya(p, s -> {\n            if (takPasti(s))') < sunmi.index('kirim(call, p, isi,'))
    # ---- paket S4: Bluetooth, mode kertas, label ----
    ok('PrinterSunmi Bluetooth: hanya perangkat yang SUDAH dipasangkan & bernama CloudPrint_ — tanpa pencarian (pencarian butuh izin lokasi)',
       'CloudPrinterBuilder.buildPrinter(d.getName(), d.getAddress())' in sunmi and sunmi.count('nama.startsWith(AWALAN_BT)') == 2 and 'AWALAN_BT = "CloudPrint_"' in sunmi
       and 'getBondedDevices()' in sunmi and 'SearchMethod.BT' not in sunmi and 'startDiscovery' not in sunmi)
    # uji owner 20 Nov (APK 1.19): pustaka menolak menyambung — "Bluetooth permission is not granted" = BtHelper.getDevice memeriksa izin LOKASI
    pasang = baca('apk', 'pasang.py')
    ok('PrinterSunmi Bluetooth: pemeriksaan izin lokasi milik pustaka dijawab KonteksBt — hanya dua izin lokasi, hanya di sambungan Bluetooth',
       'private static final class KonteksBt extends ContextWrapper {' in sunmi
       and 'return Manifest.permission.ACCESS_FINE_LOCATION.equals(izin) || Manifest.permission.ACCESS_COARSE_LOCATION.equals(izin);' in sunmi
       and 'return izinLokasi(izin) ? PackageManager.PERMISSION_GRANTED : super.checkPermission(izin, pid, uid);' in sunmi
       and 'return izinLokasi(izin) ? PackageManager.PERMISSION_GRANTED : super.checkSelfPermission(izin);' in sunmi
       and 'p.connect(bt ? new KonteksBt(getContext()) : getContext(), new ConnectCallback() {' in sunmi and sunmi.count('new KonteksBt(') == 1
       and 'import android.content.ContextWrapper;' in sunmi and 'import android.content.pm.PackageManager;' in sunmi)
    ok('aplikasi TIDAK meminta izin lokasi: tidak ada di daftar izin plugin, tidak dipasang ke manifest',
       sunmi.count('ACCESS_FINE_LOCATION') == 1 and sunmi.count('ACCESS_COARSE_LOCATION') == 1 and not re.search(r'@Permission\([^)]*ACCESS_', sunmi)
       and sunmi.count('@Permission(') == 1 and 'LOCATION' not in pasang and 'requestPermissionForAlias("bluetooth"' in sunmi and sunmi.count('requestPermissionForAlias(') == 1)
    ok('PrinterSunmi Bluetooth: sebab gagal sambung diberi kalimat toko, teks asli pustaka tetap ikut',
       sunmi.count('sebabSambung(sebab, bt)') == 1 and sunmi.count('sebabSambung(e.getMessage(), bt)') == 1 and 'return arti + " (" + s + ")";' in sunmi
       and sunmi.count('"Printer SUNMI tidak bisa disambung lewat Bluetooth: "') == 2)
    ok('PrinterSunmi Bluetooth: izin saat jalan diminta dari tombol Periksa Bluetooth; tanpa izin = BELUM_KIRIM berkalimat',
       '@Permission(alias = "bluetooth", strings = { Manifest.permission.BLUETOOTH_CONNECT })' in sunmi and 'requestPermissionForAlias("bluetooth", call, "sesudahIzinBt");' in sunmi
       and re.search(r'if \(!izinBt\(\)\) \{\s+tolak\(call, "Izin Bluetooth belum diberikan', sunmi))
    ok('PrinterSunmi: pindah jalur kabel ↔ Bluetooth melepas sambungan lama dulu; sambungan dipakai ulang hanya bila jalurnya sama',
       'if (ada != null && printerBt != bt) lepasDiam();' in sunmi and 'if (ada != null && printerBt == bt && ada.isConnected()) {' in sunmi and 'printerBt = bt;' in sunmi)
    tspl = sunmi[sunmi.index('    public void tspl(final PluginCall call) {'):]; tspl = tspl[:tspl.index('\n    }\n') + 7]
    ok('PrinterSunmi label: perintah TSPL dikirim apa adanya, TANPA menanyakan keadaan printer dengan bahasa struk', 'p.sendTSPLData(data);' in tspl and 'tanya(' not in tspl and 'commitTransBuffer' not in tspl)
    # satu perintah printer pada satu waktu, di sisi aplikasi (owner 21 Nov 2026: "boleh kita kerjakan yang ini")
    pintu = [n for n in ('status', 'cetak', 'bukaLaci', 'mode', 'setelMode', 'tspl') if ('    public void %s(final PluginCall call) {\n        if (!ambilPintu(call)) return;\n' % n) not in sunmi]
    ok('PrinterSunmi pintu: tiap perintah yang memegang printer (status, cetak, laci, mode, pindah mode, label) mengambil pintu SEBELUM menyentuh sambungan', not pintu, pintu)
    ok('PrinterSunmi pintu: perintah kedua ditolak berkode SEDANG_CETAK tanpa menyentuh sambungan; pemegang lama yang tak pernah selesai dianggap lepas',
       'if (pemegang.compareAndSet(null, new Pegang(String.valueOf(call.getCallbackId()), kini()))) return true;\n        call.reject(KALIMAT_SIBUK, SEDANG_CETAK);\n        return false;' in sunmi
       and 'if (lama != null && kini() - lama.sejak >= BATAS_PINTU_MS) pemegang.compareAndSet(lama, null);' in sunmi and 'private static final String SEDANG_CETAK = "SEDANG_CETAK";' in sunmi)
    ok('PrinterSunmi pintu: SEMUA jawaban lewat jawab() / tolak() yang melepas pintu dulu — tidak ada jalan keluar yang meninggalkan pintu terkunci',
       sunmi.count('call.reject(') == 3 and sunmi.count('call.resolve(') == 2 and sunmi.count('tolak(call, ') == 28 and sunmi.count('jawab(call, ') == 7
       and 'private void jawab(PluginCall call, JSObject o) {\n        lepasPintu(call);\n        call.resolve(o);' in sunmi
       and 'private void tolak(PluginCall call, String pesan, String kode) {\n        lepasPintu(call);\n        call.reject(pesan, kode);' in sunmi,
       [sunmi.count('call.reject('), sunmi.count('call.resolve('), sunmi.count('tolak(call, '), sunmi.count('jawab(call, ')])
    ok('PrinterSunmi pintu: hanya pemegangnya sendiri yang melepas (jawaban terlambat perintah lama tidak membuka pintu perintah baru)',
       'if (p != null && p.id.equals(String.valueOf(call.getCallbackId()))) pemegang.compareAndSet(p, null);' in sunmi)
    batas = {k: int(v) for k, v in re.findall(r'private static final (?:int|long) (BATAS_\w+) = (\d+);', sunmi)}
    ok('PrinterSunmi pintu: batasnya lebih lama dari perintah terpanjang (sambung Bluetooth + tanya + cetak Bluetooth) dan sama dengan kunci di halaman',
       batas.get('BATAS_PINTU_MS', 0) > batas.get('BATAS_SAMBUNG_BT_MS', 10**9) + batas.get('BATAS_STATUS_MS', 10**9) + batas.get('BATAS_CETAK_BT_MS', 10**9)
       and ('export const BATAS_SIBUK_MS = %d;' % batas.get('BATAS_PINTU_MS', 0)) in perangkat_js, batas)
    ok('PrinterSunmi lepas: sambungan TIDAK dilepas selagi perintah lain memegang printer',
       'public void lepas(PluginCall call) {' in sunmi and sunmi.index('if (pintuDipegang()) {', sunmi.index('public void lepas(PluginCall call) {')) < sunmi.index('lepasDiam();', sunmi.index('public void lepas(PluginCall call) {')))
    ok('PrinterSunmi mode kertas: hanya 1, 2, 3; hasilnya dibaca dari jawaban printer (getPrintMode)', 'if (m == null || m < 1 || m > 3) {' in sunmi and 'p.setPrintMode(m);' in sunmi and 'p.getPrintMode(new PropCallback() {' in sunmi)
    bio = baca('apk', 'tambahan', 'BiometrikPlugin.java')
    ok('Biometrik: jalur AndroidX (BiometricManager + BiometricPrompt), bukan FingerprintManager lama',
       'BiometricManager.from(getContext()).canAuthenticate(JENIS)' in bio and 'new BiometricPrompt(a, ContextCompat.getMainExecutor(a)' in bio and 'import android.hardware.fingerprint' not in bio)
    ok('Biometrik: hanya menjawab ada-tidaknya sensor & satu kali uji — tidak menyimpan, tidak membuka akun, tidak membaca data',
       not re.search(r'SharedPreferences|Firebase|Cipher|KeyStore|CryptoObject|getFilesDir|WebView', bio) and bio.count('@PluginMethod') == 2)
    ok('Pindai: aksi siaran scanner SUNMI & penerima terbuka', 'com.sunmi.scanner.ACTION_DATA_CODE_RECEIVED' in baca('apk', 'tambahan', 'PindaiPlugin.java') and 'RECEIVER_EXPORTED' in baca('apk', 'tambahan', 'PindaiPlugin.java'))
    nfc = baca('apk', 'tambahan', 'NfcPlugin.java')
    ok('Nfc: membaca hanya selama aplikasi di depan (nyala saat kembali, mati saat ditinggal), kejadian "tempel" dari utas utama',
       re.search(r'handleOnResume\(\) \{\s+super\.handleOnResume\(\);\s+mulai\(\);', nfc) and re.search(r'handleOnPause\(\) \{\s+berhenti\(\);', nfc)
       and 'enableReaderMode(' in nfc and 'disableReaderMode(' in nfc and 'runOnUiThread(() -> notifyListeners("tempel", o))' in nfc)
    ok('Nfc: hanya nomor seri yang dibaca — tidak ada tulis kartu, tidak ada baca isi', not re.search(r'Ndef|MifareClassic|transceive|writeNdefMessage|connect\(', nfc) and 'FLAG_READER_SKIP_NDEF_CHECK' in nfc)
    ok('KelolaRuangActivity langsung menutup diri', re.search(r'super\.onCreate\(savedInstanceState\);\s+finish\(\);', baca('apk', 'tambahan', 'KelolaRuangActivity.java')))

    app = baca('baru', 'js', 'app.js')
    blok = app[app.index("document.addEventListener('keydown', (ev) => {\n  if (panelOrang.hidden"):]; blok = blok[:blok.index('});') + 3]
    ok('app.js: keydown panel PIN menampung dulu, tidak memanggil tekanPin langsung', 'ketikTambah(' in blok and 'tekanPin(' not in blok and 'setTimeout(lepasKetik, KETIK_TUNGGU)' in blok and 'ev.timeStamp' in blok, blok[:200])
    ok('app.js: ketikan mesin / berbarengan siaran scanner dibuang tanpa memeriksa PIN', "if (ketikMesin(t) || Date.now() - _pindaiPada < 600) { _pinKetik = ''; gambarPanelOrang(); pesanOrang(KALIMAT_SCAN); return; }" in app)
    ok('index.html: perangkat.js dipramuat', '<link rel="modulepreload" href="js/inti/perangkat.js">' in baca('baru', 'index.html'))
    # 19 Nov 2026 (owner, di CPad): scanner & lampu sekartu dengan "Periksa printer" terbaca seolah printer punya scanner → dua alat, dua kartu
    hal = baca('baru', 'uji-cetak.html')
    kartu = lambda i: hal[hal.index('<section id="%s"' % i):].split('</section>', 1)[0] if ('<section id="%s"' % i) in hal else ''
    ok('uji-cetak.html: scanner & lampu di kartu TABLET, "Periksa printer" di kartu PRINTER',
       'id="ucPindai"' in kartu('ucSunmi') and 'id="ucLampu"' in kartu('ucSunmi') and 'id="ucNfc"' in kartu('ucSunmi') and 'ucStatus' not in kartu('ucSunmi')
       and 'id="ucStatus"' in kartu('ucPrinterSunmi') and 'ucPindai' not in kartu('ucPrinterSunmi') and 'ucLampu' not in kartu('ucPrinterSunmi')
       and "$('ucPrinterSunmi').hidden = !app; $('ucSunmi').hidden = !app;" in baca('baru', 'js', 'layar', 'uji-cetak.js'))
    ujs = baca('baru', 'js', 'layar', 'uji-cetak.js')
    ok('uji-cetak.html S4: Bluetooth & mode kertas di kartu PRINTER; sidik jari & setelan lampu di kartu TABLET; kartu Label sendiri (hanya di aplikasi)',
       all(('id="%s"' % i) in kartu('ucPrinterSunmi') for i in ('ucBt', 'ucBtHasil', 'ucModeKertas', 'ucModeBaca', 'ucModeSetel', 'ucModeHasil'))
       and all(('id="%s"' % i) in kartu('ucSunmi') for i in ('ucSidik', 'ucSidikUji', 'ucLampuAtur', 'ucLampuSimpan', 'ucLampuBawaan', 'ucLampuPadam'))
       and all(('id="%s"' % i) in kartu('ucLabel') for i in ('ucLabelCara', 'ucLabelLebar', 'ucLabelTinggi', 'ucLabelCelah', 'ucLabelPotong', 'ucLabelCetak', 'ucLabelPratinjau'))
       and "$('ucLabel').hidden = !app;" in ujs and 'ucSidik' not in kartu('ucPrinterSunmi') and 'ucBt' not in kartu('ucSunmi'))
    ok('uji-cetak.js S4: tiap id yang dipakai skrip ada di halaman', not [i for i in set(re.findall(r"\$\('(uc\w+)'\)", ujs)) if ('id="%s"' % i) not in hal], [i for i in set(re.findall(r"\$\('(uc\w+)'\)", ujs)) if ('id="%s"' % i) not in hal])
    ok('uji-cetak.js S4: sesudah pindah mode, yang ditampilkan JAWABAN printer (ditanya lagi), bukan mode yang diminta',
       "const r = await lewatSdk($('ucJalur').value, (l) => printerSetelMode(m, l));" in ujs and "setTimeout(() => { bacaMode(true).then(() => { $('ucModeSetel').disabled = false; }); }, 3500);" in ujs)
    # susulan paket jaringan (20 Nov 2026 malam): di jalur jaringan tombol mode dulu hanya mencari printer di USB
    ok('layar Perangkat: Baca mode & Pindah mode lewat lewatSdk (jalur yang DIPILIH menentukan caranya); tidak ada lagi panggilan mode yang menebak USB',
       "const r = await lewatSdk($('ucJalur').value, (l) => printerMode(l)); const k = kalimatModeKertas(r && r.mode);" in ujs
       and 'printerMode(lewatKini())' not in ujs and 'printerSetelMode(m, lewatKini())' not in ujs
       and "const sebutLewat = (r) => ($('ucJalur').value === 'jaringan' && r && r.lewat ? ' (lewat ' + namaLewat(r.lewat) + ')' : '');" in ujs
       and "$('ucModeHasil').textContent = k.teks + sebutLewat(r);" in ujs)
    ok('halaman Perangkat: kartu printer tidak lagi berkata keadaan "ditanyakan lewat SDK SUNMI" saja; kartu mode menerangkan caranya di jalur jaringan',
       'ditanyakan lewat SDK SUNMI.</p>' not in hal and 'ditanyakan lewat jalur cetak yang sedang dipilih (SDK SUNMI, atau jaringan).' in hal
       and 'di jalur jaringan dua-duanya dicoba sendiri (Bluetooth dulu, lalu kabel).' in kartu('ucPrinterSunmi'))
    ok('Jual: keterangan tombol Cetak tidak lagi menyebut "printer USB" saja', 'Cetak = printer USB tablet ini' not in baca('baru', 'js', 'layar', 'jual.js') and 'Cetak = printer tablet ini bila sudah diatur' in baca('baru', 'js', 'layar', 'jual.js'))
    ok('uji-cetak.js S4: label contoh berkode contoh (tidak pernah jadi barcode barang)', "kode: 'UJI-LABEL-0001'" in ujs and "export const TK_KODE_CONTOH = 'UJI-LABEL';" in baca('baru', 'js', 'layar', 'tanda-kenal-logika.js'))
    pr = baca('baru', 'js', 'inti', 'printer.js')
    ok('printer.js: teks jalur lama tidak berubah di catatan struk', "j === 'aplikasi' ? 'aplikasi tablet' : 'peramban'" in pr and "PR.namaJalur(r.jalur)" in baca('baru', 'js', 'layar', 'jual.js'))
    ok('printer.js: jalur bawaan tetap USB langsung; SDK SUNMI hanya bila dipilih di perangkat', "jalur: 'usb', alamatPrinter: '' };" in pr and "return a.jalur === 'sunmi' ? 'sunmi' : 'aplikasi';" in pr)
    # percobaan "kirim per potong" lewat Bluetooth DICABUT (owner 20 Nov 2026 malam): di kertas hanya potong pertama yang keluar; jalur jaringan yang dipakai
    es = baca('baru', 'js', 'inti', 'escpos.js'); uhtml = baca('baru', 'uji-cetak.html'); pk = baca('baru', 'js', 'inti', 'perangkat.js')
    sisa = [(n, k) for n, t in (('printer.js', pr), ('escpos.js', es), ('perangkat.js', pk), ('uji-cetak.js', ujs), ('uji-cetak.html', uhtml), ('jual.js', baca('baru', 'js', 'layar', 'jual.js')), ('antar-panel.js', baca('baru', 'js', 'layar', 'antar-panel.js')))
            for k in ('btPotong', 'ucBtPotong', 'epPotong', 'strukTerpotong', 'galatTerpotong', 'PRINTER_TERPOTONG', 'potongan, opsi', 's.batas', 'sg.batas', 'r.potong') if k in t]
    ok('kirim per potong dicabut seluruhnya: saklar, setelan, pemotong kiriman, dan kode "struk terpotong" tidak tersisa di halaman mana pun', not sisa, sisa)
    ok('satu struk = satu kiriman: kirimCetak(byte, jalur, timpa) → cetakAsli(data, jalur, opsi); layar Perangkat & Jual memanggilnya tanpa batas potong',
       "export async function kirimCetak(byte, jalur, timpa) {" in pr and "const r = await cetakAsli(epBase64(byte), j, opsi);" in pr and "  const r = await kirimCetak(s.byte, j);" in pr
       and "return { byte: sg.byte, gaya: 'gambar', kertas: a.kertas, gambar: g };" in pr and "return { byte: w.hasil(), lebar: gambar.lebar, tinggi: gambar.tinggi };" in es
       and "const jalurCoba = a.jalur === 'sunmi' || a.jalur === 'sunmi-bt' || a.jalur === 'jaringan' ? a.jalur : 'aplikasi';" in ujs
       and "const r = await kirimCetak(s.byte, jalurCoba, { alamat: a.alamatPrinter });" in ujs)
    ok('printer.js S4: Bluetooth hanya bila dipilih di perangkat & hanya di aplikasi; ketiga jalur aplikasi lewat cetakAsli',
       "if (asliAda() && a.jalur === 'sunmi-bt') return 'sunmi-bt';" in pr and "if (j === 'aplikasi' || j === 'sunmi' || j === 'sunmi-bt' || j === 'jaringan') {" in pr and "['sunmi-bt', 'SDK SUNMI lewat Bluetooth" in pr)
    ok('printer.js S4: label stiker bercelah lewat SDK memakai pintu label (kirimTspl); selain itu byte yang sama lewat jalur cetak biasa; tanpa printer = melempar',
       "if (l.cara === 'tspl' && (j === 'sunmi' || j === 'sunmi-bt')) {" in pr and "const r = await kirimTspl(l.teks.join('\\n') + '\\n', lewatJalur(j));" in pr
       and "const j = pilih || await jalurCetak(); if (j === 'dialog') throw new Error('Tidak ada printer di perangkat ini — label dicetak dari tablet kasir');" in pr and "labelCara: 'struk'" in pr)
    # uji owner 20 Nov 2026: label yang bahasanya salah untuk mode printer — ditanya & ditolak SEBELUM dikirim, hanya di jalur SDK
    cl = pr[pr.index('export async function cetakLabel('):]
    jg = "if (j === 'sunmi' || j === 'sunmi-bt') await pastikanModeLabel(l.cara, lewatJalur(j));"
    ok('printer.js: mode printer dicocokkan dengan cara label SEBELUM ada yang dikirim (pintu label maupun jalur cetak biasa)',
       cl.count(jg) == 1 and cl.index('const l = susunLabel(isi, jumlah, timpa);') < cl.index(jg) < cl.index('await kirimTspl(') < cl.index('await kirimCetak(l.byte, j, timpa')
       and "pastikanModeLabel, alamatPrinterSah } from './perangkat.js';" in pr)
    ok('layar Perangkat: hasil tanya mode & batal sidik jari memakai kalimat dari perangkat.js',
       "const k = kalimatModeKertas(r && r.mode);" in ujs and "tulisLog('Mode kertas' + sebutLewat(r) + ': ' + k.teks, !k.baik);" in ujs
       and "catch (e) { const t = sidikJariTolak(e); tulisLog('Sidik jari: ' + t.kalimat, !t.batal); }" in ujs and 'bacaModeKertas' not in ujs)
    # 19 Nov 2026 (ketahuan saat layar Perangkat dicoba): label contoh dulu selalu lewat jalur TERSIMPAN walau formulir memilih jalur lain
    ok('printer.js S4: label contoh memakai jalur yang dipilih di formulir (timpa.jalur), bukan hanya yang tersimpan — hanya di aplikasi',
       "const pilih = timpa && asliAda() && PR_JALUR.some((x) => x[0] === timpa.jalur) ? (timpa.jalur === 'usb' ? 'aplikasi' : timpa.jalur) : '';" in pr
       and "const r = await cetakLabel(LABEL_CONTOH, 1, a);" in ujs and "await PR.cetakLabel(TK.tkIsiLabel(sasaran, kode), n);" in baca('baru', 'js', 'layar', 'jual.js'))
    ok('printer.js S4: setelan label di luar batas dibuang (bawaan tetap)', "if (Number.isInteger(d[k]) && d[k] >= b[0] && d[k] <= b[1]) a[k] = d[k];" in pr and "PR_LABEL_BATAS = { labelLebar: [20, 80], labelTinggi: [15, 200], labelCelah: [0, 10] }" in pr)
    jual = baca('baru', 'js', 'layar', 'jual.js')
    # 19 Nov 2026: panggilan lampu yang melempar di alur simpan membuat nota yang SUDAH tercatat dilaporkan "GAGAL mencatat" (ditangkap uji_keranjang_tahan)
    ok('jual.js: lampu hanya lewat pembungkus yang menelan galat — tidak ada panggilan lampu telanjang di alur simpan / cetak',
       "function lampu(nama) { try { const f = PK[nama]; if (typeof f === 'function') {" in jual and "} catch (e) { /* tanpa lampu */ } }" in jual
       and jual.count("lampu('lampuBerhasil')") == 1 and jual.count("lampu('lampuGagal')") == 2   # cetak struk gagal + cetak label gagal (paket S4)
       and not re.search(r'(?<![\'\w.])lampu(Berhasil|Gagal)\(', jual) and not re.search(r'PK\.lampu\w*\(', jual))
    ok('jual.js: lampu hijau hanya sesudah nota SUNGGUH tercatat (sesudah cabang DITOLAK), bukan saat simulasi',
       jual.index("return set({ kabar: 'DITOLAK, nota tidak tersimpan: '") < jual.index("if (!(h && h.simulasi)) lampu('lampuBerhasil');") < jual.index('const lamaAdegan = adeganNota('))
    # uji owner 20 Nov 2026 (ketiga): printer diam sesudah data dikirim — layar tidak boleh menyebut "gagal" / "tidak tercetak", dialog cetak tidak dibuka sendiri
    tangkap = jual[jual.index("lampu('lampuGagal');"):]; tangkap = tangkap[:tangkap.index('cetakDialog(st, nota, ket);')]
    ok('jual.js: struk yang hasilnya tidak dikabari printer → kalimat "lihat kertasnya", SEBELUM cabang "Printer … gagal" dan tanpa membuka dialog cetak',
       "if (PK.hasilTakDiketahui(e)) { kabariGagal(PK.KALIMAT_TAK_DIKABARI); return; }" in tangkap
       and tangkap.index('PK.hasilTakDiketahui(e)') < tangkap.index("PR.sebutPrinter(j) + ' gagal ('"), tangkap[:300])
    ok('jual.js: label yang hasilnya tidak dikabari printer tidak disebut "tidak tercetak"',
       "if (PK.hasilTakDiketahui(e)) return set({ kabar: PK.KALIMAT_TAK_DIKABARI + (dokumen.length ?" in jual
       and jual.index("if (PK.hasilTakDiketahui(e)) return set({ kabar: PK.KALIMAT_TAK_DIKABARI + (dokumen.length ?") < jual.index("set({ kabar: 'Label tidak tercetak: '"))
    antar = baca('baru', 'js', 'layar', 'antar-panel.js'); tangkap = antar[antar.index('.catch((e) => {\n          // uji owner 20 Nov 2026'):]; tangkap = tangkap[:tangkap.index('dialog();')]
    ok('antar-panel.js: lembar surat jalan yang hasilnya tidak dikabari printer → "lihat kertasnya", SEBELUM cabang "gagal" dan tanpa membuka dialog cetak',
       "import { hasilTakDiketahui, masihMencetak, printerSibuk, KALIMAT_MASIH_MENCETAK, asliAda } from '../inti/perangkat.js';" in antar and "if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-' + (n + 1) + ' dari ' + lembar.length" in tangkap
       and tangkap.index('hasilTakDiketahui(e)') < tangkap.index("PR.sebutPrinter(j) + ' gagal'"), tangkap[:300])
    ok('uji-cetak.js: baris cetak & label yang gagal memuat lama waktunya dan kabar asli aplikasi (pembeda ±1 detik dari ±40 detik)',
       "const pesanGagal = (e, mulaiPada) => pesan(e) + (e && e.asli ? ' · kabar aslinya: \"' + e.asli + '\"' : '') + (mulaiPada ? ' · ' + (Date.now() - mulaiPada) + ' ms' : '');" in ujs
       and "    tulisLog(pesanGagal(e, mulaiPada) + ukuran, true);\n" in ujs and "ukuran = ' · gaya ' + s.gaya + ' · ' + s.byte.length + ' byte';" in ujs
       and "tulisLog((masihMencetak(e) ? 'Label contoh belum dikirim: ' : hasilTakDiketahui(e) ? 'Label contoh: ' : 'Label contoh gagal: ') + pesanGagal(e, mulai), true);" in ujs)
    # uji owner 20 Nov 2026 malam (keempat): satu cetakan pada satu waktu + catatan keadaan printer sebelum/sesudah
    ok('jual.js: selama satu struk belum dikabari printer, ketukan Cetak berikutnya hanya dijawab kabar — diperiksa SEBELUM jalur cetak disentuh',
       "if (sedangCetak() || PK.printerSibuk()) { set({ kabar: PK.KALIMAT_MASIH_MENCETAK, kabarAwas: true }); return; }" in jual
       and jual.index("if (sedangCetak() || PK.printerSibuk())") < jual.index("PR.jalurCetak().then((j) => {\n      if (j === 'dialog') { cetakDialog(st, nota, ket); return; }"))
    ok('jual.js: tombol Cetak bertulisan "Mencetak…" selama menunggu printer, dan kembali di KETIGA ujung (berhasil, gagal, jalur tak terbaca)',
       "k = mencetak = Date.now(); set({});\n      return PR.cetakGaris(" in jual and "${sedangCetak() ? 'Mencetak…' : 'Cetak'}" in jual
       and "{   // owner 17 Nov (butir 3): logo toko bersama bila setelan struk menyertakannya\n        usaiCetak(k);" in jual
       and "}).catch((e) => {\n        usaiCetak(k);" in jual and "}).catch(() => { usaiCetak(k); cetakDialog(st, nota, ket); });" in jual
       and "const usaiCetak = (k) => { if (mencetak !== k) return; mencetak = 0; set(S().kabar === PK.KALIMAT_MASIH_MENCETAK ? { kabar: '', kabarAwas: false } : {}); };" in jual
       and "const sedangCetak = () => mencetak > 0 && Date.now() - mencetak < PK.BATAS_SIBUK_MS;" in jual)
    ok('jual.js: "masih mencetak" bukan kegagalan printer — tanpa lampu gagal, tanpa dialog cetak (struk dan label)',
       jual.index("if (PK.masihMencetak(e)) { set({ kabar: PK.KALIMAT_MASIH_MENCETAK, kabarAwas: true }); return; }") < jual.index("lampu('lampuGagal');")
       and jual.index("if (PK.masihMencetak(e)) return set({ kabar: PK.KALIMAT_MASIH_MENCETAK + (dokumen.length ?") < jual.index("if (PK.hasilTakDiketahui(e)) return set({ kabar: PK.KALIMAT_TAK_DIKABARI + (dokumen.length ?"))
    ok('antar-panel.js: surat jalan tidak dikirim selama cetakan lain belum dikabari, dan "masih mencetak" tidak membuka dialog',
       antar.index("if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });") < antar.index("PR.jalurCetak().then((j) => {\n      if (j === 'dialog') return dialog();")
       and antar.index("if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK") < antar.index("if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-'"))
    ok('uji-cetak.js: cetak contoh lewat SDK mencatat jawaban printer SEBELUM cetak, dan menanyainya lagi SESUDAH printer diam',
       ujs.index("if (sdk) sebelum = await keadaanSingkat(lewatJalur(a.jalur));\n") < ujs.index("mulaiPada = Date.now(); const r = await kirimCetak(")
       and "if (sdk && hasilTakDiketahui(e)) tulisLog('Keadaan printer sebelum cetak itu: ' + sebelum + ' · sesudahnya: ' + await keadaanSingkat(lewatJalur(a.jalur)), true);" in ujs
       and "const keadaanSingkat = (lewat) => printerStatus(lewat).then((r) => '\"' + r.kalimat + '\"', (e) => 'tidak bisa ditanya (' + pesan(e) + ')');" in ujs)
    tj = jual[jual.index("lampu('lampuGagal');"):]; tj = tj[:tj.index('cetakDialog(st, nota, ket);')]
    # paket jaringan (20 Nov 2026): jalur cetak lewat Wi-Fi/LAN
    ok('printer.js: jalur "jaringan" ada di pilihan, hanya di aplikasi & hanya bila dipilih; bawaan tetap USB',
       "['jaringan', 'Jaringan Wi-Fi / LAN" in pr and "if (asliAda() && a.jalur === 'jaringan') return 'jaringan';" in pr and "jalur: 'usb', alamatPrinter: '' };" in pr)
    ok('printer.js: alamat printer tersimpan disaring (hanya IPv4 pribadi) saat dibaca; isian layar Perangkat menang atas yang tersimpan',
       "if (typeof d.alamatPrinter === 'string') a.alamatPrinter = alamatPrinterSah(d.alamatPrinter);" in pr
       and "const opsi = j === 'jaringan' ? { alamat: timpa && typeof timpa.alamat === 'string' ? timpa.alamat : prAtur().alamatPrinter } : null;" in pr)
    ok('printer.js: catatan struk & kabar menyebut jaringan dengan benar (bukan "printer USB")',
       "j === 'jaringan' ? 'aplikasi tablet (jaringan Wi-Fi/LAN)'" in pr and "return j === 'sunmi-bt' || j === 'jaringan' ? 'printer ' : 'printer USB ';" in pr
       and "export function sebutPrinter(j) { return j === 'sunmi-bt' ? 'Printer Bluetooth' : j === 'jaringan' ? 'Printer jaringan' : 'Printer USB'; }" in pr)
    ok('printer.js: label stiker bercelah lewat jaringan ditolak berkalimat SEBELUM ada yang dikirim; label kertas bersambung lewat jalur cetak biasa',
       cl.index("if (l.cara === 'tspl' && j === 'jaringan') {") < cl.index('await kirimCetak(l.byte, j, timpa') and "e.code = 'SALAH_MODE'; throw e; }" in cl)
    ok('perangkat.js: permintaan jaringan hanya lewat CapacitorHttp, hanya ke http://<alamat sah> + jalan tetap; tanpa nomor seri di alamat',
       perangkat_js.count("panggilAsli('CapacitorHttp', 'request'") == 1 and "{ url: 'http://' + alamat + jalan, method: 'POST'," in perangkat_js
       and "const a = alamatPrinterSah(alamat); if (!a) throw galat(KALIMAT_ALAMAT, 'SALAH_ISI');" in perangkat_js and 'sn=' not in perangkat_js and "'/cgi-bin/print.cgi?copies=1'" in perangkat_js)
    ok('layar Perangkat: kotak alamat printer hanya tampil untuk jalur jaringan, ikut disimpan, dan dipakai Cetak contoh & Periksa printer',
       'id="ucAlamatBaris" hidden' in uhtml and 'id="ucAlamat"' in uhtml and "alamatPrinter: $('ucAlamat').value.trim()," in ujs and "$('ucAlamat').value = a.alamatPrinter || ''; tampilJalur();" in ujs
       and "function tampilJalur() { $('ucAlamatBaris').hidden = $('ucJalur').value !== 'jaringan'; }" in ujs and "$('ucJalur').addEventListener('change', tampilJalur);" in ujs
       and "const r = await printerJaringanStatus($('ucAlamat').value);" in ujs
       and ujs.index("if ($('ucJalur').value === 'jaringan') {") < ujs.index("const r = await printerStatus(lewatKini());"))
    cd = jual[jual.index('  function cetakDialog(st, nota, ket) {'):]; cd = cd[:cd.index('  function catatStruk(')]
    ok('jual.js: di aplikasi tablet cetakDialog tidak membuka dialog dan TIDAK mencatat baris struk keluar (dulu: baris untuk struk yang tidak pernah keluar)',
       cd.index("if (PK.asliAda()) { kabariGagal('Struk TIDAK tercetak:") < cd.index('window.print()') < cd.index("catatStruk(nota, 'cetak',")
       and cd.count("catatStruk(") == 1 and "lalu tekan Cetak lagi'); return; }\n    const el = document.getElementById('cetakStruk');" in cd)
    ok('jual.js: printer gagal di aplikasi tablet → kabar "struk TIDAK tercetak", sebab printernya tetap terbaca, tanpa dialog',
       tj.index("if (PK.asliAda()) { kabariGagal(PR.sebutPrinter(j) + ' gagal (' + (e && e.message ? e.message : e) + ') — ' + TANPA_DIALOG); return; }")
       < tj.index("') — dialog cetak dibuka sebagai gantinya'") and "const TANPA_DIALOG = 'struk TIDAK tercetak. Bereskan printernya, lalu tekan Cetak lagi';" in jual)
    ok('jual.js: kabar gagal cetak dibuang begitu struk berikutnya sungguh keluar (tidak hidup lebih lama dari gagalnya)',
       "const kabariGagal = (teks) => { kabarGagal = teks; set({ kabar: teks, kabarAwas: true }); };" in jual
       and "        usaiCetak(k);\n        if (kabarGagal && S().kabar === kabarGagal) set({ kabar: '', kabarAwas: false });\n        kabarGagal = '';\n        catatStruk(nota, 'cetak'," in jual)
    ok('antar-panel.js: di aplikasi tablet surat jalan yang gagal tidak membuka dialog; kabarnya menyebut jalur yang benar dan sebabnya',
       antar.index("const dialog = () => { if (asliAda()) return set({ kabar: 'Surat jalan TIDAK tercetak:") < antar.index('try { window.print(); }')
       and antar.index("if (asliAda()) return set({ kabar: gagal + 'surat jalan TIDAK tercetak'") < antar.index("set({ kabar: gagal + 'dialog cetak dibuka sebagai gantinya', kabarAwas: true }); dialog();")
       and "const gagal = PR.sebutPrinter(j) + ' gagal' + (n ? ' sesudah ' + n + ' lembar' : '') + ' (' + (e && e.message ? e.message : e) + ') — ';" in antar)
    ok('perintah label: kabar "tanpa kabar" tidak menyebut mode printer (uji owner: dikirim juga saat printer di mode tanpa alas)',
       'di mode label tidak mengabari' not in ujs and 'di mode label tidak mengabari' not in jual and 'printer tidak mengabari hasil perintah label' in ujs and 'printer tidak mengabari hasil perintah label' in jual)
    alur = baca('.github', 'workflows', 'apk.yml')
    ok('apk.yml: tanda tangan V1 dan V2 dinyalakan & dibuktikan', '--v1-signing-enabled true --v2-signing-enabled true' in alur and "grep -q 'Verified using v1 scheme (JAR signing): true'" in alur and "grep -q 'Verified using v2 scheme (APK Signature Scheme v2): true'" in alur)
    return h


def periksa(perangkat_js, pasang_py, diam=False):
    def aman(nama, f, *a):
        # pemeriksa yang jatuh = GAGAL yang terbaca, bukan alat uji yang berhenti di tengah
        try: return f(*a)
        except Exception as e: return [{'nama': nama + ' jatuh', 'ok': False, 'ket': repr(e)[:300]}]
    h = jalankan_jsc(perangkat_js) + aman('pemeriksa pasang.py', periksa_pasang, pasang_py) + aman('pemeriksa statis', periksa_statis, perangkat_js)
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + x['ket']))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


# (nama, berkas 'js' | 'py', lama, baru)
MUTASI = [
    ('halangan printer tidak dikenali → struk dobel lewat USB', 'js', "e.code.indexOf('PRINTER_') === 0", "e.code.indexOf('PRINTER_') === 99"),
    ('jalur SUNMI tidak pernah jatuh ke CetakUsb', 'js', "if (galatPrinter(e)) throw e;", "throw e;"),
    ('printer tidak dilepas sebelum jatuh ke CetakUsb', 'js', "try { await panggilAsli('PrinterSunmi', 'lepas', {}); } catch (e2) { /* APK lama: plugin tidak ada */ }", ""),
    ('dua jalur gagal: sebab jalur yang dipilih hilang dari kabar', 'js', "const g = galat(sebab + ' · kirim langsung lewat kabel USB juga gagal: ' + pesanGalat(e3), e3 && e3.code);", "const g = galat(pesanGalat(e3), e3 && e3.code);"),
    ('dua jalur gagal: kode galat jalur kabel hilang', 'js', "pesanGalat(e3), e3 && e3.code);", "pesanGalat(e3), 'BELUM_KIRIM');"),
    ('dua jalur gagal: sebab utama tidak dibawa terpisah', 'js', "g.sebabUtama = sebab; throw g;", "throw g;"),
    ('printer diam: kalimat pustaka "Cetak gagal" sampai ke layar', 'js', "      if (hasilTakDiketahui(e)) { const g = galat(KALIMAT_TAK_DIKABARI, e.code); g.asli = pesanGalat(e); throw g; }\n", ""),
    ('printer diam: kode galat hilang (bisa dikirim ulang lewat kabel)', 'js', "const g = galat(KALIMAT_TAK_DIKABARI, e.code); g.asli", "const g = galat(KALIMAT_TAK_DIKABARI, 'BELUM_KIRIM'); g.asli"),
    ('printer diam: kabar asli aplikasi tidak dibawa', 'js', "const g = galat(KALIMAT_TAK_DIKABARI, e.code); g.asli = pesanGalat(e); throw g; }", "const g = galat(KALIMAT_TAK_DIKABARI, e.code); throw g; }"),
    ('printer diam: UNKNOWN dari pustaka tidak dikenali', 'js', "(e.code === 'PRINTER_UNKNOWN' || e.code === 'PRINTER_DIAM')", "(e.code === 'PRINTER_DIAM')"),
    ('printer diam: batas waktu aplikasi tidak dikenali', 'js', "(e.code === 'PRINTER_UNKNOWN' || e.code === 'PRINTER_DIAM')", "(e.code === 'PRINTER_UNKNOWN')"),
    ('halangan pasti ikut disebut "tidak mengabari"', 'js', "(e.code === 'PRINTER_UNKNOWN' || e.code === 'PRINTER_DIAM')", "(galatPrinter(e))"),
    ('satu cetakan: ketukan kedua tetap dikirim ke aplikasi', 'js', "  tolakBilaSibuk(); const k = { sejak: Date.now() }; kunci = k;\n", "  const k = { sejak: Date.now() }; kunci = k;\n"),
    ('satu cetakan: kunci tidak pernah dipasang', 'js', "  tolakBilaSibuk(); const k = { sejak: Date.now() }; kunci = k;\n", "  tolakBilaSibuk(); const k = { sejak: Date.now() };\n"),
    ('satu cetakan: kunci tidak dibuka sesudah cetakan selesai atau gagal', 'js', "  try { return await kerja(); } finally { if (kunci === k) kunci = null; }", "  return await kerja();"),
    ('satu cetakan: jawaban cetakan lama membuka kunci cetakan yang lebih baru', 'js', "finally { if (kunci === k) kunci = null; }", "finally { kunci = null; }"),
    ('satu cetakan: kunci macet selamanya bila aplikasi tidak pernah menjawab', 'js', "export const printerSibuk = () => !!kunci && Date.now() - kunci.sejak < BATAS_SIBUK_MS;", "export const printerSibuk = () => !!kunci;"),
    ('satu cetakan: kunci lepas sebelum batas terpanjang aplikasi', 'js', "export const BATAS_SIBUK_MS = 90000;", "export const BATAS_SIBUK_MS = 30000;"),
    ('satu cetakan: tolakan tanpa kode SEDANG_CETAK (layar membuka dialog / lewat kabel)', 'js', "const tolakBilaSibuk = () => { if (printerSibuk()) throw galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'); };", "const tolakBilaSibuk = () => { if (printerSibuk()) throw galat(KALIMAT_MASIH_MENCETAK, 'BELUM_KIRIM'); };"),
    ('satu cetakan: cetak struk tidak lewat kunci', 'js', "export const cetakAsli = (data, jalur, opsi) => satuCetakan(() => cetakAsliDalam(data, jalur, opsi));", "export const cetakAsli = (data, jalur, opsi) => cetakAsliDalam(data, jalur, opsi);"),
    ('satu cetakan: perintah label tidak lewat kunci', 'js', "satuCetakan(() => panggilAsli('PrinterSunmi', 'tspl',", "(() => panggilAsli('PrinterSunmi', 'tspl',"),
    ('satu cetakan: mode ditanya di belakang cetakan yang belum dikabari', 'js', "  tolakBilaSibuk();\n  let mode = '';", "  let mode = '';"),
    ('satu cetakan: mode kertas dipindah di tengah cetakan', 'js', "  if (printerSibuk()) return Promise.reject(galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'));\n", ""),
    ('satu cetakan: "masih mencetak" dikenali sebagai galat printer', 'js', "export function masihMencetak(e) { return !!(e && e.code === 'SEDANG_CETAK'); }", "export function masihMencetak(e) { return galatPrinter(e); }"),
    ('kalimat "masih mencetak" menyebut gagal', 'js', "'Cetakan sebelumnya belum dikabari printer — tunggu kabarnya dulu, jangan ketuk Cetak lagi (paling lama ±1,5 menit)'", "'Cetak gagal — tunggu kabarnya dulu, jangan ketuk Cetak lagi'"),
    ('jaringan: alamat di luar jaringan toko diterima', 'js', "  return pribadi ? b.join('.') : '';", "  return b.join('.');"),
    ('jaringan: tempelan alamat web tidak dirapikan', 'js', ".replace(/^https?:\\/\\//i, '').replace(/[\\/#?].*$/, '');", ";"),
    ('jaringan: heksa terbalik per byte', 'js', "keluar.push(h[v >> 4] + h[v & 15]);", "keluar.push(h[v & 15] + h[v >> 4]);"),
    ('jaringan: jawaban bukan-printer dianggap printer', 'js', "return { dikenali: ya('no_paper') !== null && ya('platen_opened') !== null,", "return { dikenali: true,"),
    ('jaringan: kertas habis dibaca sebagai tutup terbuka', 'js', "if (k.kertasHabis) return { kode: 'PRINTER_OUT_PAPER', kalimat: 'kertas habis' };", "if (k.kertasHabis) return { kode: 'PRINTER_COVER', kalimat: 'tutup printer terbuka' };"),
    ('jaringan: kertas belum diambil dianggap halangan', 'js', "  if (k.macet) return { kode: 'PRINTER_JAM_PAPER', kalimat: 'kertas macet' };", "  if (k.macet || k.belumDiambil) return { kode: 'PRINTER_JAM_PAPER', kalimat: 'kertas macet' };"),
    ('jaringan: alamat tidak sah tetap dihubungi', 'js', "const a = alamatPrinterSah(alamat); if (!a) throw galat(KALIMAT_ALAMAT, 'SALAH_ISI');", "const a = String(alamat || '').trim();"),
    ('jaringan: aplikasi lama tidak diberi tahu "pasang APK terbaru"', 'js', "if (kode === 'UnknownServiceException' || p.indexOf('cleartext') >= 0) return 'apk';", ""),
    ('jaringan: halangan pasti tetap dikirimi data', 'js', "  if (s.menghalangi) throw galat('Printer belum bisa mencetak: ' + s.kalimat, halanganJaringan(s.keadaan).kode);\n", ""),
    ('jaringan: kiriman tanpa copies', 'js', "'/cgi-bin/print.cgi?copies=1'", "'/cgi-bin/print.cgi'"),
    ('jaringan: data dikirim masih base64', 'js', "'/cgi-bin/print.cgi?copies=1', b64KeHeksa(data64),", "'/cgi-bin/print.cgi?copies=1', data64,"),
    ('jaringan: sambungan putus saat kirim jatuh ke kabel (struk dobel)', 'js', "throw galat('Kiriman ke printer terputus di tengah jalan (' + pesanGalat(e) + ')', 'PRINTER_DIAM');", "throw galat('Kiriman ke printer terputus di tengah jalan (' + pesanGalat(e) + ')', 'BELUM_KIRIM');"),
    ('jaringan: tanpa nomor pekerjaan dianggap berhasil dikirim ulang lewat kabel', 'js', "tapi tidak memberi nomor pekerjaan (jawaban ' + (r ? r.status : '?') + ')', 'PRINTER_DIAM');", "tapi tidak memberi nomor pekerjaan (jawaban ' + (r ? r.status : '?') + ')', 'BELUM_KIRIM');"),
    ('jaringan: "printed" tidak pernah dikenali', 'js', "if (k.tugasStatus === 'printed') return { nama: s.alamat, tugas, peringatan: '' };", "if (k.tugasStatus === 'selesai') return { nama: s.alamat, tugas, peringatan: '' };"),
    ('jaringan: "not printed" sudah dianggap tercetak', 'js', "if (k.tugasStatus === 'printed') return { nama: s.alamat, tugas, peringatan: '' };", "if (k.tugasStatus) return { nama: s.alamat, tugas, peringatan: '' };"),
    ('jaringan: halangan di tengah cetak diabaikan', 'js', "    if (h && !k.mencetak) throw galat('Cetak terhenti: ' + h.kalimat, h.kode);\n", ""),
    ('jaringan: satu tanya yang gagal menghentikan cetakan', 'js', "catch (e) { /* satu tanya yang gagal bukan kabar apa-apa — tanya lagi */ }", "catch (e) { throw e; }"),
    ('jaringan: batas bertanya tidak dipatuhi (tidak pernah menyerah)', 'js', "for (let i = 0; i < JARINGAN.tanyaMaks && Date.now() < habisPada; i++) {", "for (let i = 0; i < JARINGAN.tanyaMaks * 3 && Date.now() < habisPada; i++) {"),
    ('jaringan: lama menunggu tidak dibatasi (kunci cetak bisa kedaluwarsa duluan)', 'js', "for (let i = 0; i < JARINGAN.tanyaMaks && Date.now() < habisPada; i++) {", "for (let i = 0; i < JARINGAN.tanyaMaks; i++) {"),
    ('jaringan: printer diam berakhir sebagai "belum kirim"', 'js', "tapi belum melaporkannya tercetak', 'PRINTER_DIAM');", "tapi belum melaporkannya tercetak', 'BELUM_KIRIM');"),
    ('jaringan: tidak terjangkau tidak pernah mencoba kabel', 'js', "      if (galatPrinter(e) || (e && e.code === 'SALAH_ISI')) throw e;\n      sebab = pesanGalat(e);", "      throw e;"),
    ('jaringan: alamat kosong jatuh ke kabel', 'js', "      if (galatPrinter(e) || (e && e.code === 'SALAH_ISI')) throw e;\n      sebab = pesanGalat(e);", "      if (galatPrinter(e)) throw e;\n      sebab = pesanGalat(e);"),
    ('jaringan: hasil tak diketahui sampai ke layar dengan kalimat mentah', 'js', "      if (hasilTakDiketahui(e)) { const gj = galat(KALIMAT_TAK_DIKABARI, e.code); gj.asli = pesanGalat(e); throw gj; }\n", ""),
    ('jaringan: jalur jaringan diam-diam lewat kabel', 'js', "  if (jalur === 'jaringan') {", "  if (jalur === 'jaringan-x') {"),
    ('jaringan: nomor pekerjaan tidak dibawa pulang', 'js', "cadanganDari: '', tugas: r.tugas };", "cadanganDari: '' };"),
    ('pasang.py: izin HTTP polos tidak dipasang', 'py', "        m = m.replace('<application', '<application\\n        android:usesCleartextTraffic=\"true\"', 1)", "        pass"),
    ('pasang.py: networkSecurityConfig tidak dijaga', 'py', "    if 'android:networkSecurityConfig' in m: raise Tolak(", "    if False: raise Tolak("),
    ('pasang.py: usesCleartextTraffic="false" dibiarkan', 'py', "    m = m.replace('android:usesCleartextTraffic=\"false\"', 'android:usesCleartextTraffic=\"true\"')", "    pass"),
    ('kalimat "tidak mengabari" menyebut gagal', 'js', "'Printer tidak mengabari hasil cetaknya — lihat kertasnya dulu; kalau tidak keluar, cetak lagi'", "'Cetak gagal — lihat kertasnya dulu; kalau tidak keluar, cetak lagi'"),
    ('mode jaringan: hanya mencari di kabel (cacat 20 Nov malam)', 'js', "export const URUT_SDK_JARINGAN = ['bt', 'usb'];", "export const URUT_SDK_JARINGAN = ['usb'];"),
    ('mode jaringan: kabel dulu (6 detik menunggu sebelum Bluetooth)', 'js', "export const URUT_SDK_JARINGAN = ['bt', 'usb'];", "export const URUT_SDK_JARINGAN = ['usb', 'bt'];"),
    ('mode jaringan: printer diam tetap dicoba lewat cara lain', 'js', "    catch (e) { if (!(e && e.code === 'BELUM_KIRIM')) throw e; sebab.push(namaLewat(l) + ': ' + pesanGalat(e)); }", "    catch (e) { sebab.push(namaLewat(l) + ': ' + pesanGalat(e)); }"),
    ('mode jaringan: sebab tiap cara tidak dibawa', 'js', "sebab.push(namaLewat(l) + ': ' + pesanGalat(e)); }", "sebab.push(namaLewat(l)); }"),
    ('mode jaringan: hasil tidak menyebut lewat mana', 'js', "    try { return Object.assign({}, await kerja(l), { lewat: l }); }", "    try { return await kerja(l); }"),
    ('mode jalur kabel: diam-diam pindah ke Bluetooth', 'js', "  if (jalur !== 'jaringan') { const l = lewatJalur(jalur); return Object.assign({}, await kerja(l), { lewat: l }); }\n", ""),
    ('mode tanpa alas tidak dikenali', 'js', "return t.indexOf('linerless') >= 0 ? 'tanpa-alas' : t.indexOf('label') >= 0", "return t.indexOf('label') >= 0"),
    ('jawaban mode kosong disebut "tidak dikenali"', 'js', "  if (!asli) return { teks: 'Printer belum menjawab modenya", "  if (false) return { teks: 'Printer belum menjawab modenya"),
    ('penjaga label: perintah label ke mode struk lolos', 'js', "if (cara === 'tspl' && mode === 'struk') return", "if (false) return"),
    ('penjaga label: bahasa struk ke mode label lolos', 'js', "if (cara !== 'tspl' && mode === 'label') return", "if (false) return"),
    ('penjaga label: tolakan tidak pernah dilempar', 'js', "const tolak = labelTolakMode(cara, mode); if (tolak) throw galat(tolak, 'SALAH_MODE');", ""),
    ('penjaga label: tolakan tanpa kode SALAH_MODE', 'js', "if (tolak) throw galat(tolak, 'SALAH_MODE');", "if (tolak) throw galat(tolak, 'BELUM_KIRIM');"),
    ('penjaga label: printer tak bisa ditanya menghentikan label bahasa struk', 'js', "catch (e) { if (cara === 'tspl') throw e; return { mode: '', ditanya: false }; }", "catch (e) { throw e; }"),
    ('penjaga label: perintah label dikirim buta saat printer tak bisa ditanya', 'js', "catch (e) { if (cara === 'tspl') throw e; return { mode: '', ditanya: false }; }", "catch (e) { return { mode: '', ditanya: false }; }"),
    ('penjaga label: mode ditanya lewat jalur lain', 'js', "try { const r = await printerMode(lewat); mode = bacaModeKertas(r && r.mode); }", "try { const r = await printerMode(); mode = bacaModeKertas(r && r.mode); }"),
    ('sidik jari dibatalkan dilaporkan sebagai kegagalan', 'js', "if (n === 5 || n === 10 || n === 13) return { batal: true, kalimat: 'uji dibatalkan' };", ""),
    ('sidik jari terkunci dilaporkan sebagai batal', 'js', "if (n === 7) return { batal: false,", "if (n === 7) return { batal: true,"),
    ('jalur aplikasi ikut memakai SDK SUNMI', 'js', "if (jalur === 'sunmi' || jalur === 'sunmi-bt') {", "if (jalur) {"),
    ('aplikasi menolak SEDANG_CETAK tapi struk tetap dikirim lewat kabel (dobel)', 'js', "      if (masihMencetak(e)) { const gs = galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'); gs.asli = pesanGalat(e); throw gs; }\n", ""),
    ('S4: jalur Bluetooth diam-diam mencetak lewat kabel', 'js', "{ data, lewat: lewatJalur(jalur) }", "{ data }"),
    ('S4: jalur kabel dianggap Bluetooth', 'js', "(jalur === 'sunmi-bt' ? 'bt' : 'usb');", "(jalur ? 'bt' : 'usb');"),
    ('S4: hasil cetak Bluetooth dilaporkan sebagai jalur kabel', 'js', "return { jalur, nama: (r && r.nama) || '', peringatan: (r && r.peringatan) || '', cadanganDari: '' };", "return { jalur: 'sunmi', nama: (r && r.nama) || '', peringatan: (r && r.peringatan) || '', cadanganDari: '' };"),
    ('S4: mode kertas di luar 1–3 diteruskan ke printer', 'js', "if (!MODE_KERTAS.some((x) => x[0] === m)) return Promise.reject(galat('Mode kertas tidak dikenal', 'SALAH_ISI'));", ""),
    ('S4: jawaban mode label terbaca sebagai struk', 'js', ": t.indexOf('label') >= 0 ? 'label' : t.indexOf('receipt') >= 0 ? 'struk' : '';", ": t.indexOf('label') >= 0 ? 'struk' : t.indexOf('receipt') >= 0 ? 'label' : '';"),
    ('S4: jawaban mode tak dikenal dianggap struk', 'js', "t.indexOf('receipt') >= 0 ? 'struk' : '';", "'struk';"),
    ('S4: jalur perintah label tidak diteruskan', 'js', "{ data: String(data || ''), lewat: lewat === 'bt' ? 'bt' : 'usb' }", "{ data: String(data || '') }"),
    ('S4: lampu yang diatur "tidak menyala" tetap menyala', 'js', "  if (!a.warna || a.warna === LAMPU_MATI || !LAMPU_WARNA[a.warna]) return Promise.resolve({ ok: false, mati: true });\n", ""),
    ('S4: setelan lampu tidak sah diterima', 'js', "if (x.warna === LAMPU_MATI || LAMPU_WARNA[x.warna]) b.warna = x.warna;", "if (x.warna) b.warna = x.warna;"),
    ('S4: lama nyala lampu di luar batas diterima', 'js', "if (typeof x.detik === 'number' && x.detik >= LAMPU_DETIK[0] && x.detik <= LAMPU_DETIK[1]) b.detik = x.detik;", "if (typeof x.detik === 'number') b.detik = x.detik;"),
    ('S4: lama nyala lampu diabaikan', 'js', "batasMs: Math.round((Number(a.detik) || 1.5) * 1000) });", "batasMs: 1500 });"),
    ('S4: tombol Coba tidak memakai isian di layar', 'js', "const a = Object.assign({}, lampuAtur()[nama], timpa || {});", "const a = Object.assign({}, lampuAtur()[nama]);"),
    ('S4: setelan lampu tersimpan tidak dibaca', 'js', "const d = (simpanan === undefined ? simpananLampu() : simpanan) || {};", "const d = simpanan || {};"),
    ('S4: dua kejadian lampu terlihat sama', 'js', "['kertas', 'Kertas printer hampir habis', { warna: 'magenta', kedip: true,", "['kertas', 'Kertas printer hampir habis', { warna: 'kuning', kedip: true,"),
    ('S4: kemampuan tidak menanyakan sidik jari', 'js', ", coba('Biometrik', 'info')]);", ", Promise.resolve(null)]);"),
    ('peringatan kertas hampir habis hilang', 'js', "peringatan: (r && r.peringatan) || '', cadanganDari: '' };", "peringatan: '', cadanganDari: '' };"),
    ('scanner tidak dikenali (jeda mesin 0)', 'js', "export const KETIK_JEDA_MESIN = 35;", "export const KETIK_JEDA_MESIN = 0;"),
    ('jari dianggap mesin (jeda mesin 200)', 'js', "export const KETIK_JEDA_MESIN = 35;", "export const KETIK_JEDA_MESIN = 200;"),
    ('dua ketukan cepat sudah dianggap mesin', 'js', "export const KETIK_MESIN_MIN = 3;", "export const KETIK_MESIN_MIN = 2;"),
    ('beruntun tidak dihitung ulang sesudah jeda', 'js', "} else beruntun = 1;", "}"),
    ('lampu melempar saat aplikasi menolak', 'js', ".catch(() => { _lampuMati = true; return { ok: false }; })", ""),
    ('lampu terus memanggil aplikasi yang tak punya lampu', 'js', "_lampuMati = true; ", ""),
    ('lampu gagal tidak berkedip', 'js', "['gagal', 'Cetak gagal atau perlu dilihat', { warna: 'merah', kedip: true,", "['gagal', 'Cetak gagal atau perlu dilihat', { warna: 'merah', kedip: false,"),
    ('pindai meneruskan isi bukan teks', 'js', "if (!d || typeof d.data !== 'string' || !d.data) return;", "if (!d) return;"),
    ('pelepas pindai melepas semua pendengar', 'js', "if (i >= 0) _pendengarPindai.splice(i, 1);", "_pendengarPindai.length = 0;"),
    ('kemampuan memanggil plugin yang tidak ada', 'js', "(k.plugin[plugin] === false ? Promise.resolve(null) : ", "(false ? Promise.resolve(null) : "),
    ('nfc meneruskan nomor seri yang bukan heksa', 'js', "if (!/^(?:[0-9A-F]{2}){4,10}$/.test(uid)) return;", "if (!uid) return;"),
    ('pelepas nfc melepas semua pendengar', 'js', "if (i >= 0) _pendengarTempel.splice(i, 1);", "_pendengarTempel.length = 0;"),
    ('nfc dipasang walau aplikasinya tidak punya plugin Nfc', 'js', "if (_tempelTerpasang || !asliAda() || adaPlugin('Nfc') === false) return;", "if (_tempelTerpasang || !asliAda()) return;"),
    ('kemampuan tidak menanyakan NFC', 'js', ", coba('Nfc', 'info'), coba('Biometrik', 'info')]);", ", Promise.resolve(null), coba('Biometrik', 'info')]);"),
    ('manifest: izin NFC tidak dipasang', 'py', "    if IZIN_NFC not in m:", "    if False:"),
    ('manifest: pembaca NFC diwajibkan', 'py', 'android:name="android.hardware.nfc" android:required="false" />\\n\\n    <application', 'android:name="android.hardware.nfc" android:required="true" />\\n\\n    <application'),
    ('manifest: <queries> scanner hilang', 'py', "TANYA_PAKET = ('com.sunmi.scanner', 'com.sunmi.tmservice')", "TANYA_PAKET = ('com.sunmi.tmservice',)"),
    ('manifest: allowBackup dibiarkan menyala', 'py', "m = m.replace('android:allowBackup=\"true\"', 'android:allowBackup=\"false\"')", "pass"),
    ('manifest: penjaga data tidak dideklarasikan', 'py', "'    <activity android:name=\"%s\" android:exported=\"false\" />\\n    </application>' % PENJAGA_DATA", "'    </application>'"),
    ('manifest: configChanges tidak dilengkapi', 'py', "lengkap = bagian + [x for x in ANTI_KEDIP if x not in bagian]", "lengkap = bagian"),
    ('S4 manifest: izin sidik jari tidak dipasang', 'py', "    if IZIN_BIOMETRIK not in m:", "    if False:"),
    ('S4 manifest: sensor sidik jari diwajibkan', 'py', 'android:name="android.hardware.fingerprint" android:required="false" />\\n\\n    <application', 'android:name="android.hardware.fingerprint" android:required="true" />\\n\\n    <application'),
    ('S4 gradle: pustaka sidik jari hilang', 'py', "PUSTAKA_LAIN = ('androidx.biometric:biometric:1.1.0',)", "PUSTAKA_LAIN = ()"),
    ('gradle: pustaka printer SUNMI hilang', 'py', "PUSTAKA = ('com.sunmi:external-printerlibrary2:1.0.16', ", "PUSTAKA = ("),
    ('gradle: pustaka disisipkan dua kali', 'py', "kurang = [p for p in PUSTAKA + PUSTAKA_LAIN if p not in g2]", "kurang = list(PUSTAKA + PUSTAKA_LAIN)"),
]


def main():
    if not os.path.exists(JSC): print('GAGAL: jsc tidak ditemukan'); return 1
    js = open(MODUL, encoding='utf-8').read(); py = open(PASANG, encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, berkas, lama, baru in MUTASI:
            sumber = js if berkas == 'js' else py
            if lama not in sumber: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            rusak = sumber.replace(lama, baru, 1)
            if periksa(rusak if berkas == 'js' else js, rusak if berkas == 'py' else py, diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(js, py, diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(js, py) else 1


if __name__ == '__main__':
    sys.exit(main())
