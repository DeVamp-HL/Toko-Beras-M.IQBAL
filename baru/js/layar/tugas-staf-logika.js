// HALAMAN TUGAS STAF (owner 27 Nov 2026, sensus ulang B116 — paket P6). Tanpa DOM, BACA SAJA, awalan ts.
// Keputusan owner: staf (Penjaga laci & karyawan) yang masuk di tablet / HP staf MENDARAT di halaman tugasnya dulu (Menu akun staf, kartu paling atas), satu ketuk
// ke Jual; isinya SAMA untuk semua staf ("Sama untuk semua" — termasuk janji bayar & sisa bon, yang memang sudah terbaca staf di layar Pelanggan).
// TIDAK ADA RUMUS BARU: tiap baris = fungsi layar sumbernya apa adanya, dan semua datanya sudah ada di daftar baca staf (akses.js BACA_STAF: wadahLiteran, pesanan,
// suratJalan, piutangMutasi, tagihPelanggan, penjualan, ambilBarang) + rutinCek / aturanToko/rutin (rules v25). Satu baris galat tidak mematikan yang lain.
import { hariIniIso, tanggalPendek, RP } from '../inti/format.js';
import { susunWadah } from './stok-logika.js';
import { wbCekHari } from './wadah-bernama-logika.js';
import { poDaftarAktif, poHariKe } from './pesanan-logika.js';
import { ajDaftar } from './antar-logika.js';
import { semuaBon } from './bon-logika.js';
import { daftarKarcis } from './karcis-logika.js';
import { abDaftar } from './ambil-logika.js';
import { rnHari } from './rutin-logika.js';

/** Akun yang mendarat di halaman tugas sesudah masuk: akun staf yang bekerja (bukan owner, bukan kasir@). */
export const tsMendarat = (akun) => !!akun && akun.jenis === 'aktif' && (akun.peran === 'ben' || akun.peran === 'karyawan');

/**
 * Tugas hari ini untuk satu akun staf. → { iso, daftar: [{ id, nama, n, ket, awas, tujuan, baris? }], terbuka, n, kalimat }.
 * tujuan = layar yang boleh dibuka staf (jual · pelanggan · stok · menu), bentuk keTujuan app.js.
 */
export function tsTugas(kini, akun) {
  const iso = hariIniIso(kini); const out = [];
  const baris = (id, nama, f) => { try { out.push(Object.assign({ id, nama }, f())); } catch (e) { out.push({ id, nama, n: null, ket: 'tidak terbaca: ' + String((e && e.message) || e), awas: false, galat: true }); } };
  baris('rutin', 'Centang rutin', () => { const R = rnHari(kini, akun); const belum = R.baris.filter((x) => x.keadaan === 'belum' || x.keadaan === 'lewat');
    return { n: belum.length, ket: !R.n ? 'belum ada rutin untuk peran ini' : R.kalimat + (belum.length ? ' · belum: ' + belum.slice(0, 3).map((x) => x.nama).join(' · ') + (belum.length > 3 ? ' · +' + (belum.length - 3) : '') : ''), awas: R.nLewat > 0, tujuan: { ke: 'menu', rutin: true } }; });
  baris('wadah', 'Wadah literan', () => { const S = susunWadah(null); const isi = S.daftar.filter((x) => x.diketahui && x.perluIsi); const C = wbCekHari(iso);
    return { n: isi.length, ket: (isi.length ? 'perlu diisi: ' + isi.slice(0, 4).map((x) => x.nama).join(', ') : 'semua cukup') + (C.nAktif ? ' · cek saat tutup ' + C.nDicek + ' dari ' + C.nAktif : ''), awas: false, tujuan: { ke: 'stok', tab: 'wadah' } }; });
  baris('antar', 'Pesanan & antar', () => { const hP = poHariKe(iso); const P = poDaftarAktif('').filter((o) => o.status === 'dipesan' && o.tanggalKirim && poHariKe(o.tanggalKirim) - hP <= 1); const A = ajDaftar(iso, '');
    const n = P.length + A.jalan.length + A.gagal.length;
    return { n, ket: n ? [P.length ? P.length + ' dikirim hari ini / besok (' + P.slice(0, 3).map((o) => o.nama + (o.tanggalKirim < iso ? ' telat' : o.tanggalKirim === iso ? ' hari ini' : ' besok')).join(', ') + ')' : '', A.jalan.length ? A.jalan.length + ' masih di jalan' : '', A.gagal.length ? A.gagal.length + ' gagal antar belum dibereskan' : ''].filter(Boolean).join(' · ') : 'tidak ada yang harus diantar',
      awas: A.gagal.length > 0 || P.some((o) => o.tanggalKirim <= iso), tujuan: { ke: 'jual', lembar: A.gagal.length || A.jalan.length ? 'antar' : 'pesanan' } }; });
  baris('janji', 'Janji bayar ditagih', () => { const B = semuaBon(kini).filter((b) => b.sisa > 0 && b.tagih && b.tagih.janji && (b.status === 'janjiLewat' || (b.status === 'menunggu' && b.tagih.janji <= iso)));
    return { n: B.length, ket: B.length ? B.slice(0, 3).map((b) => b.nama + ' ' + RP(b.sisa) + (b.status === 'janjiLewat' ? ' (lewat)' : ' (hari ini)')).join(' · ') + (B.length > 3 ? ' · +' + (B.length - 3) + ' orang' : '') : 'tidak ada janji bayar hari ini',
      awas: B.some((b) => b.status === 'janjiLewat'), tujuan: { ke: 'pelanggan', keluarga: 'bon' }, baris: B.slice(0, 6).map((b) => ({ nama: b.nama, sisa: b.sisa, janji: b.tagih.janji, lewat: b.status === 'janjiLewat' })) }; });
  baris('karcis', 'Karcis belum dirinci', () => { const K = daftarKarcis(kini); const hari = K.daftar.filter((x) => x.jenisAsal === 'karcis' && x.hariIni).length;
    return { n: K.nKarcis, ket: K.nKarcis ? K.nKarcis + ' karcis' + (hari ? ' (' + hari + ' hari ini)' : '') + ' · ' + RP(K.total) + (K.nRapikan ? ' · ' + K.nRapikan + ' nota perlu dirapikan' : '') : 'tidak ada karcis yang menunggu', awas: K.nKarcis > 0, tujuan: { ke: 'jual', lembar: 'karcis' } }; });
  baris('titip', 'Barang titipan belum diambil', () => { const D = abDaftar();
    return { n: D.length, ket: D.length ? D.slice(0, 3).map((k) => k.nama + ' (' + tanggalPendek(k.tanggal) + ')').join(' · ') + (D.length > 3 ? ' · +' + (D.length - 3) : '') : 'tidak ada', awas: false, tujuan: { ke: 'jual', lembar: 'titipan' } }; });
  const terbuka = out.filter((x) => x.n > 0); const n = terbuka.reduce((a, x) => a + x.n, 0);
  return { iso, daftar: out, terbuka, n, awas: out.some((x) => x.awas), kalimat: terbuka.length ? n + ' tugas di ' + terbuka.length + ' bagian' : 'Semua tugas beres — selamat jualan' };
}
