// LAYAR UANG — K3 OWNER & TOKO (dikunci owner 17 Sep 2026: B · Timbangan). Logika tanpa DOM; pembantu berawalan ot.
// Empat hubungan uang owner-toko yang WAJIB tetap terpisah: masuk & tidak kembali = setoran modal · masuk & wajib kembali = pinjaman owner ke toko ·
// keluar & tidak kembali = ambil pribadi (dicatat di Uang keluar; di sini cuma dibaca) · keluar & wajib kembali = kasbon owner.
// Dua utang berlawanan arah DIGAMBAR DUA-DUANYA; "saling lunaskan" = perbuatan sadar yang tercatat, nol uang bergerak.
//
// Semua lewat mesin uang lama (tak ada mesin baru), dengan pengkodean yang dijaga alat uji:
//  - setor / tarik modal   → modalOwner {tipe setor|tarik} + tempat (kolom baru). Tarik > modal tertanam DITOLAK → arahkan ke ambil pribadi.
//  - owner meminjamkan     → modalOwner {tipe setor, pinjaman: true} (uang MASUK — satu-satunya pintu kas masuk milik owner di mesin lama)
//                            + utangOwnerMutasi {tipe saldoAwal, pinjaman: true} (utang toko ke owner TIMBUL tanpa menyentuh laba — 'tokoDompet' akan
//                            menekan laba). Modal tertanam sistem baru TIDAK menghitung dokumen berbendera pinjaman; laporan sistem lama menghitungnya
//                            sebagai setoran modal (sistem lama tidak diperbaiki — keputusan owner 19 Sep).
//  - toko mengembalikan    → utangOwnerMutasi {tipe bayar} (bentuk bjLunasi) + dari.
//  - kasbon owner          → kasbonMutasi a.n. Owner {tipe ambil, owner: true} (mesin kasbon: kas keluar, neraca & tutup buku membawanya).
//  - owner mengembalikan   → kasbonMutasi Owner {tipe bayar, caraBayar Tunai} (kas masuk).
//  - kasbon → ambil pribadi→ kasbonMutasi Owner {tipe bayar, caraBayar 'Potong gaji', alih: 'prive'}: mesin lama menganggap 'Potong gaji' = bukan uang masuk
//                            (kasbon berkurang, kas tetap); ambil pribadi bulan ini bertambah di penjumlah sistem baru (priveBulan).
//  - saling lunaskan       → kasbon Owner bayar 'Potong gaji' alih 'salingLunas' (kasbon −, kas tetap) + utangOwnerMutasi {tipe saldoAwal, nominal NEGATIF,
//                            alih 'salingLunas'} (utang toko −, kas tetap; mesin menjumlah timbul secara aritmetika).
import { hitungUtangOwner } from '../mesin/beku.js';
import { daftarModalOwner } from '../mesin/pembantu.js';
import { ambilUtangOwnerMutasi, ambilKasbonMutasi, ambilPengeluaranHarian } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { TEMPAT_UANG } from './bon-pemasok-logika.js';
import { NAMA_KASBON_OWNER, ugAngka, ugNamaTempat, ugKiniDari, saldoKantong, ugCukup, modalTertanam, kasbonOwner, priveBulan } from './uang-logika.js';

// arah: +1 uang MASUK ke toko, −1 uang KELUAR dari toko, 0 tidak ada uang yang bergerak
export const JENIS_OWNER = {
  setor: { arah: 1, judul: 'Setor modal', kata: 'Setoran modal', ket: ['Tabungan pribadi', 'Hasil usaha lain', 'Lain-lain'] },
  tarik: { arah: -1, judul: 'Tarik modal', kata: 'Penarikan modal', ket: ['Dipakai usaha lain', 'Keperluan pribadi besar', 'Lain-lain'] },
  pinjam: { arah: 1, judul: 'Owner meminjamkan ke toko', kata: 'Pinjaman owner ke toko', ket: ['Menalangi bon pemasok', 'Tambahan uang belanja', 'Lain-lain'] },
  bayarPinjam: { arah: -1, judul: 'Toko mengembalikan ke owner', kata: 'Pengembalian pinjaman owner', ket: [] },
  kasbon: { arah: -1, judul: 'Kasbon owner', kata: 'Kasbon owner', ket: ['Keperluan keluarga', 'Keperluan mendadak', 'Lain-lain'] },
  kembaliKasbon: { arah: 1, judul: 'Owner mengembalikan kasbon', kata: 'Pengembalian kasbon owner', ket: [] },
  alihPrive: { arah: 0, judul: 'Kasbon dijadikan ambil pribadi', kata: 'Kasbon dialihkan jadi ambil pribadi', ket: [] },
  salingLunas: { arah: 0, judul: 'Saling lunaskan', kata: 'Saling lunaskan', ket: [] },
};
/** Posisi hari ini: modal tertanam · toko berutang ke owner · owner berutang ke toko (kasbon) · ambil pribadi bulan ini · isi tempat uang. */
export function posisiOwner(kini) {
  const iso = hariIniIso(kini); const U = hitungUtangOwner(); const K = kasbonOwner(); const P = priveBulan(iso); const S = saldoKantong();
  const bersih = U.sisa - K.sisa;
  return { modal: modalTertanam(), utangToko: U.sisa, tekorUtang: U.tekor, kasbonOwner: K.sisa, prive: P.total, priveRinci: P, S,
    bersihTeks: U.sisa === 0 && K.sisa === 0 ? 'Impas — tidak ada yang berutang' : bersih === 0 ? 'Sama besar — kalau saling dilunaskan, impas' : bersih > 0 ? 'Kalau saling dilunaskan: toko masih berutang ' + RP(bersih) + ' ke owner' : 'Kalau saling dilunaskan: owner masih berutang ' + RP(-bersih) + ' ke toko',
    bisaSalingLunas: Math.min(U.sisa, K.sisa) > 0, tinggiKiri: Math.round(8 + 92 * U.sisa / Math.max(U.sisa, K.sisa, 1)), tinggiKanan: Math.round(8 + 92 * K.sisa / Math.max(U.sisa, K.sisa, 1)) };
}
function otBatas(jenis, P) {
  if (jenis === 'tarik') return [P.modal, 'Modal owner di toko cuma ' + RP(P.modal) + '. Lebih dari itu namanya ambil pribadi — catat di Uang keluar'];
  if (jenis === 'bayarPinjam') return [P.utangToko, 'Utang toko ke owner cuma ' + RP(P.utangToko)];
  if (jenis === 'kembaliKasbon' || jenis === 'alihPrive') return [P.kasbonOwner, 'Kasbon owner cuma ' + RP(P.kasbonOwner)];
  if (jenis === 'salingLunas') return [Math.min(P.kasbonOwner, P.utangToko), 'Yang bisa saling dilunaskan cuma ' + RP(Math.min(P.kasbonOwner, P.utangToko))];
  return [Infinity, ''];
}
/** Arti sebelum disimpan — satu tempat, dibaca lembar dan buktinya. */
export function artiOwner(jenis, n, tempat, P) {
  const t = ugNamaTempat(tempat);
  if (jenis === 'setor') return [t + ' bertambah ' + RP(n), 'modal owner di toko jadi ' + RP(P.modal + n), 'laba tidak berubah — ini modal, bukan untung'];
  if (jenis === 'tarik') return [t + ' berkurang ' + RP(n), 'modal owner di toko jadi ' + RP(P.modal - n), 'laba tidak berubah'];
  if (jenis === 'pinjam') return [t + ' bertambah ' + RP(n), 'toko jadi berutang ' + RP(P.utangToko + n) + ' ke owner — wajib dikembalikan', 'laba tidak berubah'];
  if (jenis === 'bayarPinjam') return [t + ' berkurang ' + RP(n), 'utang toko ke owner tinggal ' + RP(P.utangToko - n), 'laba tidak berubah'];
  if (jenis === 'kasbon') return [t + ' berkurang ' + RP(n), 'owner jadi berutang ' + RP(P.kasbonOwner + n) + ' ke toko — wajib dikembalikan', 'laba dan ambil pribadi tidak berubah'];
  if (jenis === 'kembaliKasbon') return [t + ' bertambah ' + RP(n), 'kasbon owner tinggal ' + RP(P.kasbonOwner - n), 'laba tidak berubah'];
  if (jenis === 'alihPrive') return ['uang toko tidak berubah', 'kasbon owner berkurang ' + RP(n), 'ambil pribadi bulan ini bertambah ' + RP(n)];
  return ['uang toko tidak berubah', 'utang toko ke owner tinggal ' + RP(P.utangToko - n), 'kasbon owner tinggal ' + RP(P.kasbonOwner - n)];
}
/** D = { jenis, ketik, tempat, ket }. */
export function hitungOwner(D, kini) {
  const P = posisiOwner(kini); const J = JENIS_OWNER[D.jenis] || null; const n = Math.round(ugAngka(D.ketik)); let tolak = ''; let c = { boleh: true };
  if (!J) tolak = 'Pilih perbuatannya'; else { const B = otBatas(D.jenis, P);
    if (!(n > 0)) tolak = 'Isi nominalnya dulu'; else if (J.ket.length && !D.ket) tolak = 'Pilih keterangannya';
    else if (n > B[0] + 0.5) tolak = B[1]; else if (J.arah !== 0 && !TEMPAT_UANG.some((x) => x[0] === D.tempat)) tolak = 'Pilih tempat uangnya';
    else if (J.arah === -1) { c = ugCukup(P.S, D.tempat, n); if (!c.boleh) tolak = c.teks; } }
  const A = J && n > 0 ? artiOwner(D.jenis, n, D.tempat, P) : ['', '', ''];
  return { n, J, P, tolak, arti: A, takTerperiksa: !!c.takTerperiksa, label: tolak || ('SIMPAN · ' + (J ? J.judul : '')), batas: J ? otBatas(D.jenis, P)[0] : 0 };
}
export function susunOwner(D, w) {
  const H = hitungOwner(D, ugKiniDari(w)); if (H.tolak) return { tolak: H.tolak };
  const J = H.J; const n = H.n; const ket = String(D.ket || J.kata).slice(0, 60); const dokumen = []; const urung = []; const dorong = (koleksi, data) => { dokumen.push({ koleksi, data }); urung.push({ koleksi, id: data.id }); };
  const dasar = () => ({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam });
  if (D.jenis === 'setor' || D.jenis === 'tarik') dorong('modalOwner', Object.assign(dasar(), { tipe: D.jenis, nominal: n, catatan: ket, tempat: D.tempat }));
  else if (D.jenis === 'pinjam') { const u = Object.assign(dasar(), { tipe: 'saldoAwal', pinjaman: true, nominal: n, catatan: 'Pinjaman owner ke toko — ' + ket }); dorong('utangOwnerMutasi', u); dorong('modalOwner', Object.assign(dasar(), { tipe: 'setor', pinjaman: true, pasangan: u.id, nominal: n, catatan: 'Pinjaman owner ke toko — ' + ket + ' (bukan modal)', tempat: D.tempat })); }
  else if (D.jenis === 'bayarPinjam') dorong('utangOwnerMutasi', Object.assign(dasar(), { tipe: 'bayar', nominal: n, catatan: 'Toko mengembalikan pinjaman owner', dari: D.tempat }));
  else if (D.jenis === 'kasbon') dorong('kasbonMutasi', Object.assign(dasar(), { tipe: 'ambil', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: n, catatan: ket, dari: D.tempat }));
  else if (D.jenis === 'kembaliKasbon') dorong('kasbonMutasi', Object.assign(dasar(), { tipe: 'bayar', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: n, caraBayar: 'Tunai', catatan: 'Owner mengembalikan kasbon', dari: D.tempat }));
  else if (D.jenis === 'alihPrive') dorong('kasbonMutasi', Object.assign(dasar(), { tipe: 'bayar', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: n, caraBayar: 'Potong gaji', alih: 'prive', catatan: 'Kasbon dijadikan ambil pribadi (tidak ada uang bergerak)' }));
  else if (D.jenis === 'salingLunas') { dorong('kasbonMutasi', Object.assign(dasar(), { tipe: 'bayar', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: n, caraBayar: 'Potong gaji', alih: 'salingLunas', catatan: 'Saling lunaskan dengan utang toko ke owner' })); dorong('utangOwnerMutasi', Object.assign(dasar(), { tipe: 'saldoAwal', alih: 'salingLunas', nominal: -n, catatan: 'Saling lunaskan dengan kasbon owner (utang toko berkurang, tidak ada uang bergerak)' })); }
  const P2 = { modal: H.P.modal + (D.jenis === 'setor' ? n : D.jenis === 'tarik' ? -n : 0), utangToko: H.P.utangToko + (D.jenis === 'pinjam' ? n : D.jenis === 'bayarPinjam' || D.jenis === 'salingLunas' ? -n : 0), kasbonOwner: H.P.kasbonOwner + (D.jenis === 'kasbon' ? n : D.jenis === 'kembaliKasbon' || D.jenis === 'alihPrive' || D.jenis === 'salingLunas' ? -n : 0) };
  const bukti = ['TOKO BERAS M.IQBAL', 'Bukti · ' + J.kata, tanggalPendek(w.tanggal) + ' · ' + w.jam, '', 'Jumlah            ' + RP(n)].concat(J.arah !== 0 ? [(J.arah === 1 ? 'Masuk ke          ' : 'Keluar dari       ') + ugNamaTempat(D.tempat)] : []).concat(D.ket ? ['Keterangan        ' + D.ket] : [])
    .concat(['', 'Sesudah ini:', 'Modal owner       ' + RP(P2.modal), 'Toko utang owner  ' + RP(P2.utangToko), 'Kasbon owner      ' + RP(P2.kasbonOwner), '', 'Dicatat oleh: owner']).join('\n');
  return { dokumen, urung, bukti, patch: { kabar: J.kata + ' ' + RP(n) + ' tercatat — ' + H.arti.join(' · ') + (H.takTerperiksa ? ' · isi tempat uang belum bisa dihitung, tidak diperiksa' : ''), kabarAwas: false, aksi: null, bukti } };
}
/** Buku owner: tiap baris hanya menyebut saldo yang IA ubah, terbaru di atas. */
export function bukuOwner(n) {
  const rows = [];
  daftarModalOwner().forEach((m) => { const nn = Number(m.nominal) || 0; if (m.pinjaman) rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Pinjaman owner ke toko', ket: (m.catatan || '').replace(/^Pinjaman owner ke toko — /, '') + ' · masuk ke ' + ugNamaTempat(m.tempat || 'laci'), n: nn, arah: 1, ubah: 'utang' });
    else if (m.tipe === 'setor') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Setoran modal', ket: (m.catatan || '') + (m.tempat ? ' · masuk ke ' + ugNamaTempat(m.tempat) : ''), n: nn, arah: 1, ubah: 'modal' });
    else rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: m.dariSetoran || m.dariSetoranLama ? 'Setoran tutup hari ke owner' : 'Penarikan modal', ket: (m.catatan || '') + (m.tempat ? ' · keluar dari ' + ugNamaTempat(m.tempat) : ''), n: nn, arah: -1, ubah: 'modal' }); });
  ambilUtangOwnerMutasi().forEach((m) => { const nn = Number(m.nominal) || 0; if (m.pinjaman) return;   // pasangannya sudah dibaca dari modalOwner
    if (m.tipe === 'bayar') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Toko mengembalikan ke owner', ket: (m.catatan || '') + (m.dari ? ' · keluar dari ' + ugNamaTempat(m.dari) : ''), n: nn, arah: -1, ubah: 'utang' });
    else if (m.alih === 'salingLunas') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Saling lunaskan', ket: 'utang toko ke owner & kasbon owner sama-sama berkurang · tidak ada uang bergerak', n: Math.abs(nn), arah: 0, ubah: 'saling' });
    else rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: m.tutupBuku ? 'Utang toko ke owner dibawa dari tahun lalu' : 'Utang toko ke owner (saldo awal)', ket: m.catatan || '', n: nn, arah: 0, ubah: 'utang' }); });
  ambilPengeluaranHarian().forEach((h) => { if (h.kategori !== 'tokoDompet') return; rows.push({ id: String(h.id), t: (h.tanggal || '') + ' ' + (h.jam || ''), tanggal: h.tanggal || '', jam: h.jam || '', judul: 'Belanja toko pakai dompet owner', ket: (h.keterangan || '') + ' · toko berutang ke owner', n: Number(h.nominal) || 0, arah: 0, ubah: 'utang' }); });
  ambilKasbonMutasi().forEach((m) => { if (String(m.namaPegawai || '').trim().toLowerCase() !== NAMA_KASBON_OWNER.toLowerCase()) return; const nn = Number(m.nominal) || 0;
    if (m.tipe === 'ambil') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Kasbon owner', ket: (m.catatan || '') + ' · keluar dari ' + ugNamaTempat(m.dari || 'laci'), n: nn, arah: -1, ubah: 'kasbon' });
    else if (m.alih === 'prive') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Kasbon dijadikan ambil pribadi', ket: 'kasbon berkurang, ambil pribadi bertambah · tidak ada uang bergerak', n: nn, arah: 0, ubah: 'kasbon' });
    else if (m.alih === 'salingLunas') return;   // pasangannya sudah dibaca dari utangOwnerMutasi
    else if (m.tipe === 'bayar') rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Owner mengembalikan kasbon', ket: (m.catatan || '') + (m.dari ? ' · masuk ke ' + ugNamaTempat(m.dari) : ''), n: nn, arah: 1, ubah: 'kasbon' })
    else rows.push({ id: String(m.id), t: (m.tanggal || '') + ' ' + (m.jam || ''), tanggal: m.tanggal || '', jam: m.jam || '', judul: 'Kasbon owner dibawa dari tahun lalu', ket: m.catatan || '', n: nn, arah: 0, ubah: 'kasbon' }); });
  // setoran tutup hari sistem lama bernominal nol (20-an dokumen 'mo-st-' yang tak pernah dipakai) tidak mengubah apa pun — tidak digambar
  const berisi = rows.filter((r) => r.n > 0.5);
  berisi.sort((a, b) => b.t.localeCompare(a.t) || b.id.localeCompare(a.id));
  // saldo sesudah tiap baris = dihitung mundur dari posisi sekarang
  const P = posisiOwner(new Date(Date.now())); let modal = P.modal, utang = P.utangToko, kasbon = P.kasbonOwner;
  berisi.forEach((r) => { r.s = r.ubah === 'modal' ? 'modal owner jadi ' + RP(modal) : r.ubah === 'utang' ? 'toko berutang ke owner jadi ' + RP(utang) : r.ubah === 'kasbon' ? 'kasbon owner jadi ' + RP(kasbon) : 'toko berutang jadi ' + RP(utang) + ' · kasbon owner jadi ' + RP(kasbon);
    if (r.ubah === 'modal') modal -= r.arah * r.n; else if (r.ubah === 'utang') utang -= (r.judul.indexOf('mengembalikan') >= 0 ? -r.n : r.n); else if (r.ubah === 'kasbon') kasbon -= (r.judul === 'Kasbon owner' || r.judul.indexOf('dibawa') >= 0 ? r.n : -r.n); else { utang += r.n; kasbon += r.n; } });
  return berisi.slice(0, n || 40);
}
