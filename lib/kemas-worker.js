// Pekerja kompresi cadangan koleksi (rapi-rapi 0, 13 Sep 2026).
// Mengompres JSON cadangan di luar utas utama: kompresi penjualan (±1,8 juta karakter)
// memakan ±150 ms di Mac dan lebih lama di HP — terlalu berat untuk dijalankan tiap kali
// satu penjualan masuk. Tidak menyentuh localStorage: hasilnya dikirim balik, utas utama
// yang menulis (supaya kegagalan kuota tetap tertangkap simpanLokal).
importScripts('lz-string.js');
self.onmessage = function (e) {
  var d = e.data || {};
  var hasil = null;
  try { hasil = LZString.compressToUTF16(String(d.teks || '')); } catch (err) { hasil = null; }
  self.postMessage({ id: d.id, kunci: d.kunci, hasil: hasil });
};
