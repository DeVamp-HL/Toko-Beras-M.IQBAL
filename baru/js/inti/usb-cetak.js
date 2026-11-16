// CETAK LEWAT USB (putaran T1 — Sunmi CPad + printer 80 mm di Multi-Function Stand/Base) — WebUSB di Chrome Android, tanpa aplikasi tambahan.
// Hanya mengirim byte yang sudah disusun escpos.js; tidak membaca atau menulis data toko. Izin perangkat diberikan sekali lewat dialog
// peramban (requestDevice); sesudah itu getDevices() menemukannya lagi tanpa bertanya. Kalau peramban/perangkat menolak (WebUSB tidak ada, atau
// antarmuka printer sudah dipegang layanan sistem Sunmi), jalannya = bungkus APK (catatan rencana T1) — penyebabnya disebut apa adanya.

const KELAS_PRINTER = 0x07;
const POTONGAN = 4096;   // byte per transferOut (aman untuk printer USB full-speed)

export const usbAda = () => typeof navigator !== 'undefined' && !!navigator.usb;

/** Ringkasan satu perangkat untuk layar diagnosis (VID/PID, nama, antarmuka & endpoint). */
export function usbRingkas(d) {
  if (!d) return null;
  const hex = (n) => '0x' + ('0000' + (n || 0).toString(16)).slice(-4);
  const antarmuka = [];
  ((d.configuration && d.configuration.interfaces) || []).forEach((i) => {
    (i.alternates || []).forEach((a) => {
      antarmuka.push({ nomor: i.interfaceNumber, kelas: a.interfaceClass, subkelas: a.interfaceSubclass, protokol: a.interfaceProtocol,
        diklaim: !!i.claimed, endpoint: (a.endpoints || []).map((e) => e.direction + ' ' + e.type + ' #' + e.endpointNumber) });
    });
  });
  return { vid: hex(d.vendorId), pid: hex(d.productId), pabrik: d.manufacturerName || '', nama: d.productName || '', seri: d.serialNumber || '',
    kelas: d.deviceClass, antarmuka };
}

/** Pilih antarmuka + endpoint bulk OUT: kelas printer didahulukan, lalu kelas vendor (0xFF) yang punya bulk OUT. */
export function usbPilihJalur(d) {
  const calon = [];
  ((d.configuration && d.configuration.interfaces) || []).forEach((i) => {
    (i.alternates || []).forEach((a) => {
      const keluar = (a.endpoints || []).find((e) => e.direction === 'out' && e.type === 'bulk');
      if (keluar) calon.push({ antarmuka: i.interfaceNumber, alternatif: a.alternateSetting, endpoint: keluar.endpointNumber, kelas: a.interfaceClass });
    });
  });
  calon.sort((x, y) => (x.kelas === KELAS_PRINTER ? 0 : x.kelas === 0xff ? 1 : 2) - (y.kelas === KELAS_PRINTER ? 0 : y.kelas === 0xff ? 1 : 2));
  return calon[0] || null;
}

/** Minta izin perangkat. semua = true → daftar SEMUA perangkat USB (untuk printer yang tidak mengaku kelas printer). */
export async function usbMinta(semua) {
  if (!usbAda()) throw new Error('Peramban ini tidak punya WebUSB (perlu Chrome di Android/desktop, alamat https)');
  return navigator.usb.requestDevice({ filters: semua ? [] : [{ classCode: KELAS_PRINTER }] });
}

/** Perangkat yang sudah pernah diizinkan (tanpa dialog). */
export async function usbDiingat() {
  if (!usbAda()) return [];
  return navigator.usb.getDevices();
}

/** Kirim byte ke printer. Menutup perangkat sesudahnya supaya layanan lain (atau cetak berikut) tidak terkunci. Hasil: { byte, jalur }. */
export async function usbKirim(d, byte) {
  if (!d) throw new Error('Belum ada printer yang dipilih');
  let langkah = 'membuka perangkat';
  try {
    if (!d.opened) await d.open();
    langkah = 'memilih konfigurasi';
    if (!d.configuration) await d.selectConfiguration(1);
    const j = usbPilihJalur(d);
    if (!j) throw new Error('perangkat tidak punya endpoint bulk OUT — bukan printer, atau printer memakai jalur lain');
    langkah = 'mengklaim antarmuka ' + j.antarmuka;
    await d.claimInterface(j.antarmuka);
    if (j.alternatif) { langkah = 'memilih alternatif ' + j.alternatif; await d.selectAlternateInterface(j.antarmuka, j.alternatif); }
    langkah = 'mengirim data';
    for (let i = 0; i < byte.length; i += POTONGAN) {
      const r = await d.transferOut(j.endpoint, byte.subarray(i, i + POTONGAN));
      if (r.status !== 'ok') throw new Error('transfer berstatus ' + r.status);
    }
    langkah = 'melepas antarmuka';
    await d.releaseInterface(j.antarmuka);
    return { byte: byte.length, jalur: j };
  } catch (e) {
    const pesan = e && e.message ? e.message : String(e);
    throw new Error('Gagal saat ' + langkah + ': ' + pesan + (langkah.indexOf('mengklaim') === 0 ? ' (antarmuka mungkin dipegang layanan printer bawaan Sunmi → jalan APK)' : ''));
  } finally {
    try { if (d.opened) await d.close(); } catch (e) { /* sudah tertutup */ }
  }
}
