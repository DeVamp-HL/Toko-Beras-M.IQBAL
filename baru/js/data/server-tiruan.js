// SERVER TIRUAN (gladi tutup buku, 7 Okt 2026): /baru/ bicara ke Firebase Emulator Suite (Firestore + Auth) — HANYA untuk uji di runner GitHub.
// Alamat: /baru/?emulator=127.0.0.1:8080 (Firestore) [&emulatorAuth=127.0.0.1:9099 (Auth; bawaan: host yang sama, port 9099)].
// Penjaga:
//   · halaman BUKAN localhost / 127.0.0.1 (situs sungguhan, github.io): parameter ini DIABAIKAN — aplikasi ke data toko seperti biasa;
//   · halaman lokal yang MEMINTA server tiruan (?emulator= ada, walau kosong) dengan alamat yang salah: GAGAL-TERTUTUP — { tolak }, firebase.js tidak
//     menyambung ke server MANA PUN (bukan jatuh ke data toko) dan app.js memasang bilah merah "SERVER TIRUAN DITOLAK" (tinjauan 7 Okt);
//   · alamat emulator juga localhost / 127.0.0.1 dengan port angka — tidak bisa diarahkan ke server lain;
//   · proyeknya proyek "demo-" (PROYEK_TIRUAN): kalau sambungan ke emulator gagal, permintaan jatuh ke proyek yang tidak ada, BUKAN ke data toko.
// CSP baru/index.html TIDAK dilonggarkan untuk ini: connect-src situs tetap Firebase saja, jadi peramban memblokir sambungan ke emulator di situs.
// Salinan uji (alat-uji/gladi_tutup_buku.py) yang menambah alamat emulator ke connect-src salinannya. Modul ini tanpa impor (diuji di jsc: uji_server_tiruan.py).
export const PROYEK_TIRUAN = 'demo-gladi-toko';
export const HOST_LOKAL = ['localhost', '127.0.0.1'];
const PORT_AUTH_BAWAAN = 9099;

/** 'host:port' → { host, port } kalau host lokal & port 1–65535; selain itu null. */
export function alamatLokal(teks) {
  const m = /^([a-z0-9.]+):([0-9]{1,5})$/i.exec(String(teks || '').trim());
  if (!m) return null;
  const host = m[1].toLowerCase(); const port = Number(m[2]);
  if (HOST_LOKAL.indexOf(host) < 0 || !(port >= 1 && port <= 65535)) return null;
  return { host, port };
}

/**
 * Setelan server tiruan dari alamat halaman. q = URLSearchParams halaman, namaHost = location.hostname.
 * → null (tidak diminta, atau halaman bukan lokal — diam) · { tolak: kalimat } (diminta di halaman lokal tapi alamatnya salah — GAGAL-TERTUTUP) ·
 *   { firestore: { host, port }, auth: 'http://host:port', proyek }.
 */
export function serverTiruan(q, namaHost) {
  const minta = q && typeof q.get === 'function' ? q.get('emulator') : null;
  if (minta === null || minta === undefined) return null;   // tidak diminta. ?emulator= kosong TETAP permintaan → ditolak di bawah (bukan jatuh ke data toko)
  if (HOST_LOKAL.indexOf(String(namaHost || '').toLowerCase()) < 0) return null;
  const fs = alamatLokal(minta);
  if (!fs) return { tolak: 'Alamat emulator Firestore harus localhost / 127.0.0.1 dengan port (mis. 127.0.0.1:8080). Aplikasi tidak disambungkan ke data mana pun.' };
  const mintaAuth = q.get('emulatorAuth');
  const au = mintaAuth !== null && mintaAuth !== undefined ? alamatLokal(mintaAuth) : { host: fs.host, port: PORT_AUTH_BAWAAN };
  if (!au) return { tolak: 'Alamat emulator Auth harus localhost / 127.0.0.1 dengan port (mis. 127.0.0.1:9099). Aplikasi tidak disambungkan ke data mana pun.' };
  return { firestore: fs, auth: 'http://' + au.host + ':' + au.port, proyek: PROYEK_TIRUAN };
}

/** Setelan aplikasi Firebase untuk server tiruan: proyek demo (tanpa kunci toko). Emulator menerima kunci apa pun. */
export function configTiruan(t) {
  return { apiKey: 'demo-kunci-gladi', authDomain: t.proyek + '.firebaseapp.com', projectId: t.proyek, appId: '1:0:web:gladi', messagingSenderId: '0', storageBucket: '' };
}
