// PUTUSAN OWNER DI TABLET — sidik jari Tahap B (owner 23 Nov 2026). Logika tanpa DOM & tanpa Firebase; awalan ow. Dijaga alat-uji/uji_owner_tablet.py.
// Keputusan owner 23 Nov 2026:
//  · satu tempel jari = SATU putusan (setujui / tolak / tandai dibaca);
//  · sandi akun owner diketik owner sekali di tablet, lalu disimpan TERKUNCI penanda jari (plugin Biometrik rahasiaSimpan; hangus bila ada jari baru = ketik lagi);
//  · "lu yang pilih yang paling masuk akal": boleh diputus di tablet = titipan uang keluar, pesan & kabar barang masuk, nego harga, bon lewat batas, usul harga
//    pelanggan — semuanya lewat susunPutusPersetujuan yang SAMA dengan HP/Mac (dokumen uang / setelan ikut di kiriman yang sama). Hitungan laci = hanya TOLAK
//    (minta hitung ulang). TUTUP HARI di tablet TIDAK: menutup hari menulis dokumen uang dari seluruh buku, dan akun tablet tidak membaca semua koleksi uang.
//  · tiap putusan bercap diputusDi 'tablet · sidik jari owner' (+ jejak pencatat `lewat`), supaya di HP kelihatan mana yang diputus di tablet.
// Penulisnya firebase.js tulisSebagaiOwner (sesi owner sementara, auth di memori, keluar sesudah satu kiriman).
import { ssPersetujuan, susunPutusPersetujuan, SS_HITUNG_LACI } from './sistem-logika.js';
import { TP_TINDAKAN, TP_PESAN, TP_KABAR } from './titipan-logika.js';
import { FK_TINDAKAN } from './faktur-logika.js';
import { HT_TINDAKAN } from './harga-tingkat-logika.js';

export const OW_KUNCI = 'miqbal_owner_tablet_v1';   // localStorage PERANGKAT: { data, iv, uid, dipasang } — data/iv = sandi terkunci penanda (tidak terbaca tanpa jari)
export const OW_DI = 'tablet · sidik jari owner';
// boleh disetujui & ditolak di tablet (dibaca saat dipakai, bukan saat modul dimuat)
const owBisaSetuju = (t) => [TP_TINDAKAN, 'nego', FK_TINDAKAN, HT_TINDAKAN].indexOf(t) >= 0;

/** Simpanan perangkat → objek (rusak / kosong = null). */
export function owBaca(teks) {
  try { const o = JSON.parse(String(teks || '')); return o && typeof o === 'object' && o.data && o.iv && o.uid ? o : null; } catch (e) { return null; }
}
/** Putusan owner di tablet MENYALA untuk akun tablet `akun`: simpanan ada & milik akun tablet ini. */
export const owNyala = (lokal, akun) => !!lokal && !!akun && String(lokal.uid) === String(akun.uid || '');
/** Yang boleh diputus di tablet untuk satu permintaan { tindakan }: { setuju, tolak, dibaca } — tidak satu pun = hanya di HP/Mac. */
export function owBoleh(m) {
  const t = String((m && m.tindakan) || '');
  if (t === TP_PESAN || t === TP_KABAR) return { setuju: false, tolak: false, dibaca: true };
  if (t === SS_HITUNG_LACI) return { setuju: false, tolak: true, dibaca: false };
  if (owBisaSetuju(t)) return { setuju: true, tolak: true, dibaca: false };
  return { setuju: false, tolak: false, dibaca: false };
}
/** Permintaan yang menunggu owner, dengan apa yang boleh di tablet (yang tidak boleh tetap tampil, disebut "di HP/Mac"). */
export function owDaftar(kini) {
  return ssPersetujuan(kini).menunggu.map((m) => Object.assign({}, m, { boleh: owBoleh(m),
    hanyaHp: !owBoleh(m).setuju && !owBoleh(m).tolak && !owBoleh(m).dibaca ? 'diputus di HP/Mac owner' : m.tindakan === SS_HITUNG_LACI ? 'menutup hari tetap di lembar Tutup hari (HP/Mac) — di tablet hanya minta hitung ulang' : '' }));
}
/**
 * Susun putusan di tablet (aksi 'setuju' | 'tolak' | 'dibaca'): jalur yang sama dengan HP (susunPutusPersetujuan), lalu dokumen permintaannya diberi cap
 * diputusDi. Yang tidak boleh di tablet = ditolak dengan sebabnya. → { dokumen, hapus?, patch } | { tolak }
 */
export function owSusunPutus(id, aksi, alasan, w) {
  const m = ssPersetujuan(new Date(w.kini)).menunggu.find((x) => String(x.id) === String(id)); if (!m) return { tolak: 'Permintaan itu sudah diputus atau tidak ada lagi' };
  const B = owBoleh(m);
  if (aksi === 'setuju' && !B.setuju) return { tolak: B.tolak ? 'Yang ini tidak disetujui di tablet — ' + (m.tindakan === SS_HITUNG_LACI ? 'tutup hari di lembar Tutup hari (HP/Mac)' : 'putuskan di HP/Mac') : 'Yang ini diputus di HP/Mac owner' };
  if (aksi === 'tolak' && !B.tolak) return { tolak: 'Yang ini tidak bisa ditolak di tablet — putuskan di HP/Mac owner' };
  if (aksi === 'dibaca' && !B.dibaca) return { tolak: 'Yang ini bukan pesan' };
  if (aksi === 'tolak' && !String(alasan || '').trim()) return { tolak: 'Menolak butuh alasan — supaya ' + (m.dari || 'peminta') + ' tahu sebabnya' };
  const r = susunPutusPersetujuan(id, aksi !== 'tolak', aksi === 'dibaca' ? String(alasan || '') : alasan, w); if (r.tolak) return r;
  const dokumen = (r.dokumen || []).map((d) => (d.koleksi === 'persetujuan' && String(d.data.id) === String(id) ? { koleksi: d.koleksi, data: Object.assign({}, d.data, { diputusDi: OW_DI }) } : d));
  if (!dokumen.some((d) => d.koleksi === 'persetujuan' && String(d.data.id) === String(id))) return { tolak: 'Putusan tidak menulis permintaannya — tidak dikirim' };
  return Object.assign({}, r, { dokumen });
}
/** Kalimat untuk tombol / kabar tiap aksi. */
export const owNamaAksi = (aksi) => (aksi === 'setuju' ? 'Setujui' : aksi === 'tolak' ? 'Tolak' : 'Tandai dibaca');
/** Keadaan kartu: 'tidak' (APK lama) · 'mati' · 'nyala'. */
export function owKeadaan(lokal, akun, ada) {
  if (!ada) return { st: 'tidak', teks: 'Aplikasi di tablet ini belum bisa menyimpan sandi terkunci jari — pasang APK terbaru' };
  if (owNyala(lokal, akun)) return { st: 'nyala', teks: 'Menyala sejak ' + String(lokal.dipasang || '').slice(0, 10) + ' — tiap putusan = tempel jari owner; mati sendiri bila ada jari baru di tablet' };
  return { st: 'mati', teks: 'Mati — owner menyalakan dengan sandi akun owner (diketik sekali, lalu terkunci sidik jari)' };
}
/** Tolakan plugin / penulis saat memutus → { kalimat, matikan } — matikan = simpanan tidak bisa dipakai lagi (hangus, kunci berganti, sandi diganti). */
export function owArtiGagal(e) {
  const kode = String((e && e.code) || '');
  if (kode === 'BIOMETRIK_HANGUS') return { matikan: true, hangus: true, kalimat: 'ada jari baru didaftarkan di tablet — sandi owner yang tersimpan DIHAPUS. Hapus jari asing di Setelan tablet, lalu nyalakan lagi' };
  if (kode === 'PENANDA_TIDAK_ADA' || kode === 'PENANDA_GAGAL' || kode === 'RAHASIA_RUSAK') return { matikan: true, kalimat: 'kunci sidik jari tablet berganti / hilang — nyalakan lagi dengan sandi owner' };
  if (kode === 'UNIMPLEMENTED' || kode === 'TIDAK_ADA') return { matikan: false, kalimat: 'aplikasi tablet belum bisa — pasang APK terbaru' };
  return { matikan: false, kalimat: '' };
}
