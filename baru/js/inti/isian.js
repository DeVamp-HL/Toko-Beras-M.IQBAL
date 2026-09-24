// PUTARAN 23d (owner 24 Sep): isian LOKAL yang belum disimpan — di memori (keadaan layar) atau localStorage — ikut pola keranjang saat ganti orang.
// Tiap layar memasang SATU penjaga:
//   belum()   = ada isian: kunci keadaan yang nilainya beda dari keadaan awal, atau draf lokal di localStorage;
//   lupakan() = draf lokal dihapus, lalu SELURUH keadaan layar kembali ke awal (kunci di luar keadaan awal dibuang) — bukan cuma kunci yang dicek.
// Draf yang tersimpan di SERVER (aturanToko/hargaDraf = draf katalog harga) milik toko, bukan milik orang yang masuk — tidak disentuh di sini.
const sama = (a, b) => JSON.stringify(a === undefined ? null : a) === JSON.stringify(b === undefined ? null : b);
const bacaMentah = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const hapusLokal = (k) => { try { localStorage.removeItem(k); } catch (e) { /* penyimpanan terkunci */ } };

/**
 * K = keadaan layar (inti/keadaan.js) · awal() = keadaan awal SEGAR (dipanggil ulang saat melupakan, sesudah draf lokal dihapus)
 * isian = [kunci | [kunci, (nilai, nilaiAwal, s) => bool]] — bawaan: beda dari keadaan awal
 * lokal = [kunciLocalStorage | [kunci, (teksMentah) => bool]] — bawaan: ada isinya
 */
export function pasangIsian(K, awal, isian, lokal) {
  const dasar = awal();
  const cek = (isian || []).map((x) => (Array.isArray(x) ? x : [x, (v, a) => !sama(v, a)]));
  const drafLokal = (lokal || []).map((x) => (Array.isArray(x) ? x : [x, (t) => t !== null && t !== '']));
  return {
    belum: () => { const s = K.baca(); return cek.some(([k, f]) => f(s[k], dasar[k], s)) || drafLokal.some(([k, f]) => { const t = bacaMentah(k); return t !== null && f(t); }); },
    lupakan: () => { drafLokal.forEach(([k]) => hapusLokal(k)); K.setel((s) => { const b = awal(); Object.keys(s).forEach((k) => { if (!(k in b)) b[k] = undefined; }); return b; }); },
  };
}

export const kalimatIsianKeluar = (nama) => 'Ada isian belum disimpan di: ' + nama.join(', ') + ' — kembali untuk menyimpan, atau kosongkan semua?';
