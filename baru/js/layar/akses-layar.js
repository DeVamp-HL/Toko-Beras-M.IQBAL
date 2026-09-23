// Layar mengikuti peran (putaran 23, Tahap 3 — setipis mungkin, keputusan owner 24 Sep: yang login 1–2 bulan ke depan hanya owner).
// Satu pintu untuk layar: kisi SS2 (sistem-logika) × yang dibuka server (akses.js). Penegaknya tetap penulis pusat & rules;
// di sini hanya supaya tombol tampil MATI dengan kalimat sebabnya, bukan hilang diam-diam.
import { tombolTindakan, angkaBoleh, batasBarisNota, batasHasilAdukan } from '../data/akses.js';
import { ssPeran, SS_TINDAKAN } from './sistem-logika.js';

export const bukanOwner = (akun) => !!akun && akun.jenis !== 'owner';
/** { boleh, kalimat } untuk satu tindakan SS2 bagi akun yang masuk (owner / mode cadangan = selalu boleh). */
export function tombolAkun(akun, tindakan) {
  if (!bukanOwner(akun)) return { boleh: true, kalimat: '' };
  const T = SS_TINDAKAN.find((t) => t.id === tindakan);
  return tombolTindakan(akun, tindakan, ssPeran().hak(akun.peran, tindakan), T ? T.nama : tindakan);
}
/** Tindakan di LUAR kisi SS2 (retur, pesanan, opname, kantong, tempat, HPP …): owner saja putaran ini (peta §2). */
export function tombolLuarKisi(akun) { return bukanOwner(akun) ? { boleh: false, kalimat: 'Perlu persetujuan owner — alurnya menyusul' } : { boleh: true, kalimat: '' }; }
export { angkaBoleh, batasBarisNota, batasHasilAdukan };
