// Layar mengikuti peran (putaran 23, Tahap 3 — setipis mungkin, keputusan owner 24 Sep: yang login 1–2 bulan ke depan hanya owner).
// Satu pintu untuk layar: kisi SS2 (sistem-logika) × yang dibuka server (akses.js). Penegaknya tetap penulis pusat & rules;
// di sini hanya supaya tombol tampil MATI dengan kalimat sebabnya, bukan hilang diam-diam.
import { tombolTindakan, angkaBoleh, batasBarisNota, batasHasilAdukan, batasDokumenKirim, bolehLayar, bisaBekerja, BUAT_STAF, BACA_STAF } from '../data/akses.js';
import { ssPeran, SS_TINDAKAN } from './sistem-logika.js';

export const bukanOwner = (akun) => !!akun && akun.jenis !== 'owner';
/** Tombol yang membuka LAYAR LAIN tampil hanya kalau akun ini boleh membuka layar itu — sama persis dengan gerbang pindah() di app.js (akun yang belum
 *  bisa bekerja & mode cadangan tidak disaring di sini). Owner 7 Okt (tinjauan): staf tanpa Laporan tidak diberi tombol yang hanya berujung kabar
 *  "tidak termasuk hak". */
export const bolehBukaLayar = (akun, layar) => !akun || !bisaBekerja(akun) || bolehLayar(akun, layar);
/** { boleh, kalimat } untuk satu tindakan SS2 bagi akun yang masuk (owner / mode cadangan = selalu boleh). */
export function tombolAkun(akun, tindakan) {
  if (!bukanOwner(akun)) return { boleh: true, kalimat: '' };
  const T = SS_TINDAKAN.find((t) => t.id === tindakan);
  return tombolTindakan(akun, tindakan, ssPeran().hak(akun.peran, tindakan), T ? T.nama : tindakan);
}
/** Tindakan di LUAR kisi SS2 (retur, pesanan, opname, kantong, tempat, HPP …): owner saja putaran ini (peta §2). */
export function tombolLuarKisi(akun) { return bukanOwner(akun) ? { boleh: false, kalimat: 'Perlu persetujuan owner — alurnya menyusul' } : { boleh: true, kalimat: '' }; }
/** owner 7 Okt (JS2-C): nilai kisi SS2 untuk satu tindakan akun ini ('sendiri' | 'owner' | 'tidak'; owner / mode cadangan = 'sendiri'). */
export function hakAkun(akun, tindakan) { return bukanOwner(akun) ? ssPeran().hak(akun.peran, tindakan) : 'sendiri'; }
/**
 * owner 7 Okt (JS2-C): akun ini bisa MINTA OWNER lewat koleksi persetujuan (menulis permintaannya & membaca keputusannya)? Mengikuti daftar yang dibuka server
 * (BUAT_STAF / BACA_STAF = firestore.rules, dijaga periksa_rules.py). Belum dibuka → kalimat sebabnya + jalan keluarnya.
 */
export function bolehMintaOwner(akun) {
  if (!bukanOwner(akun)) return { boleh: false, kalimat: 'Owner tidak perlu minta persetujuan' };
  const buka = (BUAT_STAF.persetujuan || []).indexOf(akun.peran) >= 0 && BACA_STAF.indexOf('persetujuan') >= 0;
  return buka ? { boleh: true, kalimat: '' } : { boleh: false, kalimat: 'Minta owner dari perangkat ini belum bisa — server belum membuka permintaan nego untuk akun karyawan. Pakai batas jatah, parkir struk ini sampai owner datang, atau owner yang mencatat nota ini.' };
}
export { angkaBoleh, batasBarisNota, batasHasilAdukan, batasDokumenKirim };
