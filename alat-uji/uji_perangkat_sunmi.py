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

  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'CetakUsb.cetak': () => ({ nama: 'usb' }) });
  r = await cetakAsli('QUJD', 'aplikasi');
  cek('jalur aplikasi: hanya CetakUsb', r.jalur === 'aplikasi' && A.catat.join(',') === 'CetakUsb.cetak', A.catat.join(','));
  A = pasangAplikasi(['CetakUsb', 'PrinterSunmi'], { 'PrinterSunmi.cetak': tolak('x', 'BELUM_KIRIM'), 'CetakUsb.cetak': tolak('antarmuka dipegang aplikasi lain') });
  g = null; try { await cetakAsli('QUJD', 'sunmi'); } catch (e) { g = e; }
  cek('dua jalur gagal: KEDUA sebab sampai ke pemanggil — sebab jalur yang dipilih di depan, sebab kabel menyusul', g && g.message === 'x · kirim langsung lewat kabel USB juga gagal: antarmuka dipegang aplikasi lain' && g.sebabUtama === 'x', g && g.message);

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
  cek('tanya mode: jalur diteruskan, jawaban printer pulang apa adanya', (await printerMode('bt')).mode === 'label printer' && isiTanyaMode.lewat === 'bt' && (await printerMode(), isiTanyaMode.lewat === 'usb'));
  await kirimTspl('CLS\nPRINT 1\n', 'usb');
  cek('perintah label: data & jalur diteruskan apa adanya', isiTspl && isiTspl.data === 'CLS\nPRINT 1\n' && isiTspl.lewat === 'usb', JSON.stringify(isiTspl));
  await printerStatus('bt'); const lewatBt = isiStatus.lewat; await printerStatus();
  cek('periksa printer: jalur bt diteruskan; tanpa isi = usb', lewatBt === 'bt' && isiStatus.lewat === 'usb');
  cek('daftar printer Bluetooth pulang apa adanya', (await printerBt()).daftar[0].nama === 'CloudPrint_0001');

  A = pasangAplikasi(['Biometrik'], { 'Biometrik.info': () => ({ ada: false, terdaftar: false, kode: 12, kalimat: 'tablet ini tidak punya sensor sidik jari' }), 'Biometrik.minta': (isi) => ({ ok: true, isi }) });
  const KB = await kemampuan();
  cek('kemampuan: sidik jari ditanya bila pluginnya ada', KB.plugin.Biometrik === true && KB.biometrik && KB.biometrik.ada === false && KB.biometrik.kode === 12, JSON.stringify(KB));
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
    cc = re.search(r'android:configChanges="([^"]*)"', m).group(1).split('|')
    ok('manifest: configChanges memuat navigation, keyboard, keyboardHidden tanpa kembar', all(x in cc for x in ('navigation', 'keyboard', 'keyboardHidden')) and len(cc) == len(set(cc)), '|'.join(cc))
    ok('manifest: aktivitas utama tetap satu & masih bisa dibuka', m.count('android:name=".MainActivity"') == 1 and 'android.intent.category.LAUNCHER' in m and m.count('</activity>') == 1)
    ok('manifest: dijalankan dua kali = sama', P['ubah_manifest'](m) == m)

    def ditolak(f, *a):
        try: f(*a)
        except P['Tolak']: return True
        except Exception: return False
        return False
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
    hilang = [p + '.' + m for p, m in sorted(dipanggil) if not re.search(r'@PluginMethod\s+public void ' + m + r'\(', baca('apk', 'tambahan', p + 'Plugin.java'))]
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
       and re.search(r'if \(!izinBt\(\)\) \{\s+call\.reject\("Izin Bluetooth belum diberikan', sunmi))
    ok('PrinterSunmi: pindah jalur kabel ↔ Bluetooth melepas sambungan lama dulu; sambungan dipakai ulang hanya bila jalurnya sama',
       'if (ada != null && printerBt != bt) lepasDiam();' in sunmi and 'if (ada != null && printerBt == bt && ada.isConnected()) {' in sunmi and 'printerBt = bt;' in sunmi)
    tspl = sunmi[sunmi.index('    public void tspl(final PluginCall call) {'):]; tspl = tspl[:tspl.index('\n    }\n') + 7]
    ok('PrinterSunmi label: perintah TSPL dikirim apa adanya, TANPA menanyakan keadaan printer dengan bahasa struk', 'p.sendTSPLData(data);' in tspl and 'tanya(' not in tspl and 'commitTransBuffer' not in tspl)
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
       "await printerSetelMode(m, lewatKini());" in ujs and "setTimeout(() => { bacaMode(true).then(() => { $('ucModeSetel').disabled = false; }); }, 3500);" in ujs)
    ok('uji-cetak.js S4: label contoh berkode contoh (tidak pernah jadi barcode barang)', "kode: 'UJI-LABEL-0001'" in ujs and "export const TK_KODE_CONTOH = 'UJI-LABEL';" in baca('baru', 'js', 'layar', 'tanda-kenal-logika.js'))
    pr = baca('baru', 'js', 'inti', 'printer.js')
    ok('printer.js: teks jalur lama tidak berubah di catatan struk', "j === 'aplikasi' ? 'aplikasi tablet' : 'peramban'" in pr and "PR.namaJalur(r.jalur)" in baca('baru', 'js', 'layar', 'jual.js'))
    ok('printer.js: jalur bawaan tetap USB langsung; SDK SUNMI hanya bila dipilih di perangkat', "jalur: 'usb' };" in pr and "return a.jalur === 'sunmi' ? 'sunmi' : 'aplikasi';" in pr)
    ok('printer.js S4: Bluetooth hanya bila dipilih di perangkat & hanya di aplikasi; ketiga jalur aplikasi lewat cetakAsli',
       "if (asliAda() && a.jalur === 'sunmi-bt') return 'sunmi-bt';" in pr and "if (j === 'aplikasi' || j === 'sunmi' || j === 'sunmi-bt') {" in pr and "['sunmi-bt', 'SDK SUNMI lewat Bluetooth" in pr)
    ok('printer.js S4: label stiker bercelah lewat SDK memakai pintu label (kirimTspl); selain itu byte yang sama lewat jalur cetak biasa; tanpa printer = melempar',
       "if (l.cara === 'tspl' && (j === 'sunmi' || j === 'sunmi-bt')) {" in pr and "const r = await kirimTspl(l.teks.join('\\n') + '\\n', lewatJalur(j));" in pr
       and "const j = pilih || await jalurCetak(); if (j === 'dialog') throw new Error('Tidak ada printer di perangkat ini — label dicetak dari tablet kasir');" in pr and "labelCara: 'struk'" in pr)
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
    ('jalur aplikasi ikut memakai SDK SUNMI', 'js', "if (jalur === 'sunmi' || jalur === 'sunmi-bt') {", "if (jalur) {"),
    ('S4: jalur Bluetooth diam-diam mencetak lewat kabel', 'js', "{ data, lewat: lewatJalur(jalur) }", "{ data }"),
    ('S4: jalur kabel dianggap Bluetooth', 'js', "(jalur === 'sunmi-bt' ? 'bt' : 'usb');", "(jalur ? 'bt' : 'usb');"),
    ('S4: hasil cetak Bluetooth dilaporkan sebagai jalur kabel', 'js', "return { jalur, nama: (r && r.nama) || '', peringatan:", "return { jalur: 'sunmi', nama: (r && r.nama) || '', peringatan:"),
    ('S4: mode kertas di luar 1–3 diteruskan ke printer', 'js', "if (!MODE_KERTAS.some((x) => x[0] === m)) return Promise.reject(galat('Mode kertas tidak dikenal', 'SALAH_ISI'));", ""),
    ('S4: jawaban mode label terbaca sebagai struk', 'js', "return t.indexOf('label') >= 0 ? 'label' : t.indexOf('receipt') >= 0 ? 'struk' : '';", "return t.indexOf('label') >= 0 ? 'struk' : t.indexOf('receipt') >= 0 ? 'label' : '';"),
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
    ('peringatan kertas hampir habis hilang', 'js', "peringatan: (r && r.peringatan) || '', cadanganDari: '' };\n    } catch (e) {", "peringatan: '', cadanganDari: '' };\n    } catch (e) {"),
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
