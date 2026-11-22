// SIDIK JARI OWNER DI TABLET — Tahap A (owner 22 Nov 2026). Logika tanpa DOM & tanpa Firebase; awalan sj. Dijaga alat-uji/uji_sidik_tablet.py.
// Keputusan owner 22 Nov 2026:
//  · Yang didaftarkan di Setelan Android tablet HANYA jari owner. Android tidak tahu jari siapa, dan PIN layar kunci tablet BUKAN pengaman (staf pasti
//    dikasih PIN waktu layar terkunci, lalu bisa mendaftarkan jarinya) → sidik jari owner HANYA menyala bila PENANDA JARI BARU terpasang di tablet ini:
//    kunci AndroidKeyStore wajib sidik jari KUAT tiap pemakaian, hangus sendiri begitu ada jari baru didaftarkan (plugin Biometrik, PR #174). Masuk & intip
//    selalu lewat kunci itu (sidikJariKunci / CryptoObject) — bukan sekadar "cocok/tidak" (sidikJariUji).
//  · Uji OrderPAD 3 (Android 14, APK 1.31): kelas KUAT, uji kunci LULUS, penanda HANGUS sesudah jari baru → Tahap A dibangun.
//  · Orang yang dibuka jari = orang pilihan owner yang membuka Ringkas hari ini (aturanToko/peran.ringkasOrang, "Dibuka oleh") — satu setelan, satu orang.
//  · Tahap A: (1) masuk sebagai orang itu dengan jari di "Siapa yang jaga?" (PIN tetap cadangan), (2) INTIP UANG — saat orang lain jaga, jari owner membuka
//    Ringkas hari ini sementara, tertutup sendiri sesudah intipDetik tidak disentuh (setelan owner, bawaan 60), (3) JEJAK: kiriman selama masuk lewat jari
//    bertanda "sidik jari" di jejak pencatat. Penanda HANGUS = sidik jari mati di tablet ini + kabar ke owner (pesan otomatis).
//  · Tahap B (owner menyetujui di tablet) TIDAK di sini.
import { ssAtur } from './sistem-logika.js';

export const SJ_KUNCI = 'miqbal_sidik_owner_v1';   // localStorage PERANGKAT: { orang, uid, dipasang, hangus, hangusPada, dikabarkan }
export const SJ_INTIP_BAWAAN = 60;                 // detik — owner 22 Nov 2026 "±1 menit tidak disentuh"; diatur owner (aturanToko/peran.intipDetik)
export const SJ_INTIP_MIN = 15, SJ_INTIP_MAKS = 600;
export const SJ_LEWAT = 'sidik jari';

/** Orang yang dibuka sidik jari = orang pembuka Ringkas hari ini ('' = mati). */
export const sjOrang = () => String((ssAtur('peran') || {}).ringkasOrang || '');
/** Lama intip uang (detik) — setelan owner, bawaan 60. */
export function sjIntipDetik() {
  const n = Number((ssAtur('peran') || {}).intipDetik);
  return isFinite(n) && n >= SJ_INTIP_MIN && n <= SJ_INTIP_MAKS ? Math.round(n) : SJ_INTIP_BAWAAN;
}
/** Simpanan perangkat → objek (rusak / kosong = null). */
export function sjBaca(teks) {
  try { const o = JSON.parse(String(teks || '')); return o && typeof o === 'object' && o.orang && o.uid ? o : null; } catch (e) { return null; }
}
/** Sidik jari owner menyala di perangkat ini untuk akun tablet `akun`: dinyalakan untuk orang pilihan owner yang SEKARANG, akun yang sama, belum hangus. */
export function sjNyala(lokal, akun, orang) {
  const o = orang === undefined ? sjOrang() : String(orang || '');
  return !!lokal && !lokal.hangus && !!akun && String(lokal.uid) === String(akun.uid || '') && !!o && String(lokal.orang) === o;
}
/** Tombol sidik jari di panel PIN orang `op`? */
export const sjBolehMasuk = (op, lokal, akun, orang) => !!op && op.aktif !== false && sjNyala(lokal, akun, orang) && String(op.id) === String(lokal.orang);
/** Intip uang boleh? Sidik jari menyala, yang jaga BUKAN orang itu sendiri (dia sudah melihat Ringkas), akun tablet ditandai membaca data uang. */
export function sjBolehIntip(efektif, lokal, akunAsli, orang) {
  return sjNyala(lokal, akunAsli, orang) && !!efektif && !!efektif.operatorId && String(efektif.operatorId) !== String(lokal.orang) && !!akunAsli && akunAsli.bacaUang === true;
}
/** Intip harus tertutup? (tidak disentuh `detik` detik) */
export const sjHarusTutupIntip = (sentuh, kini, detik) => (Number(kini) || 0) - (Number(sentuh) || 0) >= (Number(detik) || SJ_INTIP_BAWAAN) * 1000;

/** Nyalakan (sesudah penanda terpasang & uji kunci lulus): hanya oleh orang pilihan owner yang sedang jaga. */
export function sjSusunNyala(efektif, akunAsli, w) {
  const o = sjOrang();
  if (!o) return { tolak: 'Owner belum memilih orang pembuka Ringkas hari ini (Menu › Toko ini › Peran & persetujuan › Orang di tablet) — sidik jari membuka orang itu' };
  if (!efektif || String(efektif.operatorId || '') !== o) return { tolak: 'Sidik jari hanya bisa dinyalakan oleh orang pilihan owner yang sedang jaga (masuk dengan PIN-nya)' };
  return { lokal: { orang: o, uid: String((akunAsli || {}).uid || ''), dipasang: w.kini, hangus: false } };
}
/** Penanda hangus: tandai (kabar ke owner menyusul begitu ada orang jaga). */
export const sjTandaiHangus = (lokal, w) => Object.assign({}, lokal || {}, { hangus: true, hangusPada: (lokal && lokal.hangusPada) || w.kini, dikabarkan: false });
export const sjPerluKabar = (lokal) => !!lokal && lokal.hangus === true && lokal.dikabarkan !== true;
/** Pesan otomatis ke owner (rules v13 stafKirimPesan: atas nama akun tablet yang sedang dijaga). */
export function sjDokKabarHangus(lokal, efektif, w) {
  const teks = 'OTOMATIS dari tablet: ada jari baru didaftarkan di Setelan tablet sejak sidik jari owner dinyalakan (' + String((lokal && lokal.dipasang) || '').slice(0, 10)
    + ') — sidik jari owner DIMATIKAN di tablet ini. Kalau itu bukan jari lu, ada orang yang tahu PIN layar kunci tablet. Hapus jari asing itu di Setelan, lalu nyalakan lagi dari Menu tablet sesudah masuk dengan PIN.';
  return { koleksi: 'persetujuan', data: { id: w.idUnik(), tindakan: 'pesan', status: 'menunggu', teks, mintaUid: String(efektif.uid), dari: 'Tablet · otomatis', peran: String(efektif.peran || ''),
    tanggal: w.tanggal, jam: w.jam, pada: w.kini } };
}
/** Keadaan untuk kartu di Menu tablet (orang pilihan owner yang jaga). */
export function sjKeadaan(lokal, akunAsli, orang, ada) {
  if (!ada) return { st: 'tidak', teks: 'Aplikasi di tablet ini belum punya penanda jari baru — pasang APK terbaru (1.31 ke atas)' };
  if (!(orang === undefined ? sjOrang() : orang)) return { st: 'tidak', teks: 'Owner belum memilih orang pembuka Ringkas hari ini' };
  if (lokal && lokal.hangus && String(lokal.uid) === String((akunAsli || {}).uid || '')) return { st: 'hangus', teks: 'MATI — ada jari baru didaftarkan di tablet sejak dinyalakan. Hapus jari asing di Setelan tablet, lalu nyalakan lagi.' };
  if (sjNyala(lokal, akunAsli, orang)) return { st: 'nyala', teks: 'Menyala sejak ' + String(lokal.dipasang || '').slice(0, 10) + ' — masuk & intip uang dengan jari owner; mati sendiri bila ada jari baru didaftarkan' };
  return { st: 'mati', teks: 'Mati — nyalakan sesudah memastikan di Setelan tablet HANYA jari owner yang terdaftar' };
}
