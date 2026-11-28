// SERAH TERIMA LACI SAAT GANTI JAGA (owner 28 Nov 2026). Logika tanpa DOM; awalan sl. Dijaga alat-uji/uji_serah_laci.py.
// Keputusan owner 28 Nov 2026 (ditanya di depan):
//  1. Yang menghitung = ORANG YANG DATANG, sebelum mulai jaga (orang yang pulang ikut menyaksikan). Pemicunya: di tablet ini sudah ada orang LAIN yang jaga
//     hari itu, lalu orang berikutnya masuk PIN / sidik jari. Orang pertama hari itu tidak menghitung (laci semalam = Tutup hari).
//  2. WAJIB: sebelum hitungan terkirim, tablet tidak bisa dipakai jual (layar lain tertahan di Menu).
//  3. Per pecahan, sama dengan hitung laci Tutup hari (pecahan & receh dari setelan owner aturanToko/tutupHari — hlHitung).
//  4. HITUNG BUTA: tablet tidak pernah menampilkan "seharusnya" / selisih. Owner melihatnya di papan Persetujuan: seharusnya pada jam serah terima =
//     rumus laci Tutup hari hari itu − uang laci yang tercatat SESUDAH jam itu (tdSesudahHitung, rumus yang sama dengan hitungan tutup tablet).
// Kiriman = persetujuan tindakan 'kabarToko' jenis 'serahLaci' (rules v27 stafUsulTablet — tanpa rules baru): status menunggu, mintaUid penulis, teks, tanpa kolom
// keputusan; owner menandainya dibaca (boleh dibalas) seperti kabar toko lain. Push ke HP owner lewat kabarOwner (judul "Serah terima laci").
import { cacheMentah } from '../data/toko.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { hlHitung, HL_DRAF_KOSONG } from './tutup-tablet-logika.js';
import { rumusLaci, tdSesudahHitung } from './tutup-hari-logika.js';

export const SL_JENIS = 'serahLaci';
export const SL_KUNCI_TERAKHIR = 'miqbal_baru_jaga_terakhir';   // { tanggal, orangId, nama } — orang terakhir yang jaga di tablet INI
export const SL_KUNCI_WAJIB = 'miqbal_baru_serah_laci';         // { tanggal, dari, ke, keId, sejak } — serah terima yang belum dikirim (bertahan saat aplikasi dibuka ulang)
export const SL_DRAF_KOSONG = () => ({ lembar: {}, receh: '' });

/**
 * Sesudah PIN / sidik jari berhasil. lalu = isi SL_KUNCI_TERAKHIR (boleh null), op = { id, nama } orang yang baru masuk, w = { tanggal, jam }.
 * → { terakhir: isi baru SL_KUNCI_TERAKHIR, wajib: serah terima yang harus dihitung (null bila tidak perlu) }.
 */
export function slSesudahPin(lalu, op, w, wajibLama) {
  const terakhir = { tanggal: String(w.tanggal), orangId: String((op && op.id) || ''), nama: String((op && op.nama) || '') };
  // serah terima yang belum dikirim hari ini tetap wajib selama orang yang sama yang masuk; orang lain lagi = dia yang menghitung, "dari" tetap orang sebelumnya
  if (wajibLama && wajibLama.tanggal === w.tanggal) return { terakhir, wajib: Object.assign({}, wajibLama, { ke: terakhir.nama, keId: terakhir.orangId }) };
  const ganti = !!lalu && lalu.tanggal === w.tanggal && !!lalu.orangId && lalu.orangId !== terakhir.orangId;
  return { terakhir, wajib: ganti ? { tanggal: String(w.tanggal), dari: String(lalu.nama || ''), ke: terakhir.nama, keId: terakhir.orangId, sejak: String(w.jam || '') } : null };
}
/** Serah terima yang masih berlaku hari ini (yang tanggalnya lewat = gugur: hari itu sudah ditutup lewat Tutup hari). */
export const slMasihWajib = (wajib, tanggal) => (!!wajib && wajib.tanggal === tanggal ? wajib : null);

/** Hitungan per pecahan (pecahan & receh setelan owner, sama dengan Tutup hari). */
export function slHitung(draf, kini) {
  const H = hlHitung(Object.assign(HL_DRAF_KOSONG(), { lembar: (draf && draf.lembar) || {}, receh: (draf && draf.receh) || '' }), kini);
  return { pecahan: H.pecahan, receh: H.receh, hitung: H.hitung, tolak: H.tolakHitung };
}

/** Kirim hitungan serah terima. akun = orang yang jaga (uid akun tablet). → { dokumen, patch } atau { tolak }. */
export function slSusunKirim(draf, wajib, akun, w, kini) {
  if (!wajib) return { tolak: 'Tidak ada serah terima laci yang menunggu' };
  if (!akun || !akun.uid || akun.jenis === 'owner') return { tolak: 'Serah terima laci dikirim dari tablet' };
  const H = slHitung(draf, kini); if (H.tolak) return { tolak: H.tolak };
  const lembar = {}; H.pecahan.forEach((x) => { if (x.n > 0) lembar[String(x.p)] = x.n; });
  const teks = ('Serah terima laci ' + (wajib.dari || '?') + ' → ' + (wajib.ke || akun.nama || '?') + ' jam ' + w.jam + ' · dihitung ' + RP(H.hitung)).slice(0, 500);
  const data = { id: w.idUnik(), tindakan: 'kabarToko', jenis: SL_JENIS, status: 'menunggu', mintaUid: String(akun.uid), dari: String(wajib.ke || akun.nama || ''), teks,
    hitung: H.hitung, lembar, receh: H.receh, dariOrang: String(wajib.dari || ''), keOrang: String(wajib.ke || akun.nama || ''), tanggal: w.tanggal, jam: w.jam };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { sl: SL_DRAF_KOSONG(), kabar: 'Serah terima laci terkirim ke owner (' + RP(H.hitung) + ') — silakan mulai jaga', kabarAwas: false } };
}

/**
 * OWNER: seharusnya di laci pada jam serah terima & selisihnya. m = dokumen persetujuan serahLaci. Rumus laci Tutup hari hari itu dikurangi uang laci yang
 * tercatat SESUDAH jam serah terima (catatan yang ditulis hari itu). Titik kas belum disetel = tidak ditebak. → { ada, seharusnya, selisih, teks }.
 */
export function slSelisih(m) {
  if (!m || m.jenis !== SL_JENIS || !/^\d{4}-\d{2}-\d{2}$/.test(String(m.tanggal || '')) || !/^\d{2}:\d{2}/.test(String(m.jam || ''))) return { ada: false, teks: '' };
  let R; try { R = rumusLaci(m.tanggal); } catch (e) { R = null; }
  if (!R || !R.ada) return { ada: false, teks: 'Seharusnya belum bisa dihitung — ' + ((R && R.teks) || 'data uang belum terbaca') };
  let S; try { S = tdSesudahHitung(m.tanggal, m.tanggal, String(m.jam).slice(0, 5)); } catch (e) { S = { net: 0, n: 0 }; }
  const seharusnya = Math.round(R.seharusnya - (Number(S.net) || 0)); const hitung = Math.round(Number(m.hitung) || 0); const selisih = hitung - seharusnya;
  const kata = selisih === 0 ? 'PAS' : selisih > 0 ? 'LEBIH ' + RP(selisih) : 'KURANG ' + RP(-selisih);
  return { ada: true, seharusnya, hitung, selisih, sesudah: S.n || 0,
    teks: 'Seharusnya ' + RP(seharusnya) + ' pada ' + tanggalPendek(m.tanggal) + ' ' + String(m.jam).slice(0, 5) + ' · dihitung ' + RP(hitung) + ' · ' + kata + (selisih ? ' (jaga ' + (m.dariOrang || 'sebelumnya') + ')' : '')
      + ((S.n || 0) ? ' · ' + S.n + ' catatan laci sesudah jam itu tidak dihitung' : '') };
}
/** Serah terima laci yang tercatat (terbaru dulu) — dipakai papan owner & kartu tablet (status kiriman sendiri). */
export function slDaftar(uid) {
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'kabarToko' && m.jenis === SL_JENIS && (!uid || String(m.mintaUid || '') === String(uid)))
    .sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || String(b.jam || '').localeCompare(String(a.jam || '')));
}
