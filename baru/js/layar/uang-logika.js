// LAYAR UANG — bagian BERSAMA + K1 CATAT UANG KELUAR (dikunci owner 17 Sep 2026: C · Pita Laci) + K4 PINDAH UANG (A · Tiga Tempat Uang).
// Logika tanpa DOM; nama pembantu berawalan ug (bersama) · uk (uang keluar) · pu (pindah uang) karena bundel uji jsc satu lingkup.
//
// SATU KEBENARAN UANG: kasPada() (mesin beku) = seluruh uang toko. Sistem lama tidak punya saldo per tempat uang (laci · brankas · rekening · amplop) —
// ia hanya tahu TOTAL + titik kas per tempat. saldoKantong() di sini MEMBAGI total itu ke tempatnya: berangkat dari titik kas, tiap gerakan kas
// (daftarGerakanKas, mesin beku) diletakkan di tempatnya — dokumen yang menyebut `dari`/`tempat` (kolom baru sistem baru) dipakai, sisanya mengikuti
// aturan lama (QRIS → rekening, selain itu laci) — lalu pindah tempat (amplopLaba, pindahUang) digeser antar tempat. Jumlah keempat tempat SELALU =
// kasPada() (dijaga alat uji). Yang tidak bisa dihitung (titik kas belum ada) DISEBUT, tidak ditebak.
//
// Empat arti uang keluar (K1) ditulis sebelum disimpan: biaya toko (kas −, laba −) · toko berutang ke owner (kas tetap, laba −, utang +) · ambil
// pribadi/prive (kas −, laba tetap) · bukan urusan toko (tidak ditulis). Semua dokumen = bentuk sistem lama (pengeluaranHarian kategori toko/owner/
// tokoDompet) + kolom `dari`. Kasbon owner = kasbonMutasi a.n. "Owner" (mesin kasbon, neraca & tutup buku sudah menghitungnya) bertanda owner: true.
import { kasPada, hitungKasbon, hitungLabaBersihRentang, hitungUtangOwner } from '../mesin/beku.js';
import { daftarGerakanKas, daftarModalOwner, kunciPelanggan, POS_BIAYA_BULANAN, namaBulanPanjang, akhirBulanIso } from '../mesin/pembantu.js';
import { ambilTitikKas, ambilAmplopLaba, ambilPindahUang, ambilPengeluaranHarian, ambilKasbonMutasi, ambilModalOwner, ambilUtangOwnerMutasi, ambilUtangPemasokMutasi, ambilBiayaBulanan, ambilPiutangMutasi, ambilBahanKemasan, ambilBahanLiteran, cacheMentah } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { TEMPAT_UANG, aturBon } from './bon-pemasok-logika.js';

export const NAMA_KASBON_OWNER = 'Owner';
export const KELUARGA_UANG = [['keluar', 'Uang keluar'], ['upah', 'Orang & upah'], ['owner', 'Owner & toko'], ['pindah', 'Pindah uang'], ['tutup', 'Tutup hari'], ['buku', 'Tutup buku']];
export const ugAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
export const ugKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const ugAturDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;
export const ugNamaTempat = (id) => (id === 'amplop' ? 'Amplop laba' : id === 'dompet' ? 'Dompet owner' : (TEMPAT_UANG.find((t) => t[0] === id) || [id, id])[1]);
export const ugHariKe = (iso) => Math.round(new Date(iso + 'T00:00:00Z').getTime() / 86400000);
export const ugTambahHari = (iso, n) => new Date((ugHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
export const ugAwalBulan = (iso) => String(iso).slice(0, 7) + '-01';
/** "Sekarang" menurut w (waktu layar): tanggal w, tengah hari setempat — bukan jam mesin (di cadangan, hari ini = hari cadangan diunduh). */
export const ugKiniDari = (w) => new Date(String(w.tanggal) + 'T12:00:00');
const ugKasbonOwner = (m) => kunciPelanggan(m.namaPegawai) === kunciPelanggan(NAMA_KASBON_OWNER);

// ---------- SALDO PER TEMPAT UANG ----------
/** Tempat sebuah baris gerakan kas: dokumen yang menyebut tempatnya menang; sisanya aturan lama (masuk QRIS → rekening; lainnya laci). */
function ugPetaKantong() {
  const p = {}; const isi = (id, t) => { if (id !== undefined && id !== null && t && TEMPAT_UANG.some((x) => x[0] === t)) p[String(id)] = t; };
  ambilPengeluaranHarian().forEach((h) => isi(h.id, h.dari)); ambilKasbonMutasi().forEach((m) => isi(m.id, m.dari)); ambilUtangPemasokMutasi().forEach((m) => isi(m.id, m.dari));
  ambilUtangOwnerMutasi().forEach((m) => isi(m.id, m.dari)); ambilModalOwner().forEach((m) => isi(m.id, m.tempat)); ambilPiutangMutasi().forEach((m) => isi(m.id, m.dari));
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((b) => isi(b.id, b.dari));
  // biaya bulanan: barisnya ber-id 0 — dikenali lewat tanggal + awal labelnya; dariPos ditulis K1 dengan kunci yang sama dengan mesin (pos.kunci / 'gaji:' + nama)
  const bl = {}; ambilBiayaBulanan().forEach((b) => { const d = b.dariPos || {}; Object.keys(d).forEach((k) => { if (!d[k]) return; const label = k.indexOf('gaji:') === 0 ? 'Gaji ' + k.slice(5) : ((POS_BIAYA_BULANAN.find((x) => x.kunci === k) || {}).label || k); bl[b.bulan + '|' + label] = d[k]; }); });
  return { id: p, bulanan: bl };
}
/** Penentu tempat uang satu baris gerakan kas — aturan yang SAMA dengan saldoKantong (dokumen yang menyebut tempatnya menang). 39b no. 13: dipakai kertas laci tutup hari. */
export function kantongGerakan() { const peta = ugPetaKantong(); return (r) => ugKantongBaris(r, peta); }
function ugKantongBaris(r, peta) {
  if (r.id && peta.id[String(r.id)]) return peta.id[String(r.id)];
  if (!r.id) { const m = String(r.label || '').match(/^(.*?)(?: \(kotor.*)? — biaya (.+)$/); if (m) { const bulan = ugBulanDariNama(m[2]); const t = peta.bulanan[bulan + '|' + m[1]]; if (t) return t; } }
  return r.keluar > 0 ? 'laci' : (r.kantong || 'laci');
}
const NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
function ugBulanDariNama(teks) { const m = String(teks).trim().match(/^(\S+)\s+(\d{4})$/); if (!m) return ''; const i = NAMA_BULAN.indexOf(m[1]); return i < 0 ? '' : m[2] + '-' + String(i + 1).padStart(2, '0'); }
/**
 * Saldo tiap tempat uang sampai `sampai` (bawaan: sekarang). ada=false bila titik kas belum disetel atau tanggalnya mundur dari titik (tidak ditebak).
 * total selalu = kasPada(sampai): tiap gerakan kas diletakkan tepat sekali; pindah tempat (amplop, pindahUang) jumlahnya nol.
 */
export function saldoKantong(sampai) {
  const t = ambilTitikKas(); const kosong = { ada: false, titik: t, laci: null, brankas: null, rekening: null, amplop: null, total: null, mesin: kasPada(sampai || null) };
  if (!t || (sampai && sampai < t.tanggal)) return kosong;
  const s = { laci: Number(t.laci) || 0, brankas: Number(t.brankas) || 0, rekening: Number(t.rekening) || 0, amplop: Number(t.amplop) || 0 };
  const dalam = (x) => x > t.tanggal && (!sampai || x <= sampai); const peta = ugPetaKantong();
  daftarGerakanKas().forEach((r) => { if (!dalam(r.t)) return; const k = ugKantongBaris(r, peta); if (r.masuk > 0) s[k] += r.masuk; if (r.keluar > 0) s[k] -= r.keluar; });
  ambilAmplopLaba().forEach((a) => { if (a.tutupBuku || !dalam(a.tanggal || '')) return; const n = Number(a.nominal) || 0; if (a.tipe === 'ambil') { s.amplop -= n; s.laci += n; } else { s.laci -= n; s.amplop += n; } });
  ambilPindahUang().forEach((p) => { if (!dalam(p.tanggal || '')) return; const n = Number(p.nominal) || 0; if (s[p.dari] !== undefined) s[p.dari] -= n; if (s[p.ke] !== undefined) s[p.ke] += n; });
  const total = s.laci + s.brankas + s.rekening + s.amplop; const mesin = kasPada(sampai || null);
  return { ada: true, titik: t, laci: s.laci, brankas: s.brankas, rekening: s.rekening, amplop: s.amplop, total, mesin, cocok: mesin !== null && Math.abs(total - mesin) < 0.5,
    minus: ['laci', 'brankas', 'rekening', 'amplop'].filter((k) => s[k] < -0.5), teksTitik: 'titik kas ' + tanggalPendek(t.tanggal) };
}
/** Kalimat kalau tempat uang tidak cukup — atau pengakuan bahwa isinya belum bisa dihitung (bukan berarti cukup). */
export function ugCukup(S, tempat, n) {
  if (!S.ada) return { boleh: true, takTerperiksa: true, teks: 'isi ' + ugNamaTempat(tempat).toLowerCase() + ' belum bisa dihitung (titik kas belum disetel) — tidak diperiksa' };
  const isi = S[tempat]; if (isi === undefined || isi === null) return { boleh: true, takTerperiksa: true, teks: '' };
  if (n > isi + 0.5) return { boleh: false, teks: ugNamaTempat(tempat) + ' cuma ' + RP(isi) + ' — tidak cukup untuk ' + RP(n) };
  return { boleh: true, teks: '' };
}

// ---------- angka owner-toko yang dibaca banyak layar ----------
/** Modal owner yang tertanam = Σ setor − Σ tarik (modalOwner + setoranKas lama lewat daftarModalOwner); pinjaman owner ke toko TIDAK dihitung modal. */
export function modalTertanam(sampai) { return daftarModalOwner().reduce((a, m) => { if (m.pinjaman || (sampai && (m.tanggal || '') > sampai)) return a; const n = Number(m.nominal) || 0; return a + (m.tipe === 'setor' ? n : -n); }, 0); }
/** Kasbon owner (owner berutang ke toko) — dibaca dari mesin kasbon a.n. Owner. */
export function kasbonOwner(sampai) { const k = hitungKasbon(sampai || null).find((x) => x.kunci === kunciPelanggan(NAMA_KASBON_OWNER)); return { sisa: k ? Math.max(0, k.sisa) : 0, ambil: k ? k.ambil : 0, bayar: k ? k.bayar : 0, mutasi: k ? k.mutasi : [] }; }
/** Ambil pribadi dalam rentang = prive dari laci (pengeluaranHarian owner) + kasbon owner yang dijadikan ambil pribadi + tarik modal (penjaga modal sistem lama). */
export function priveRentang(awal, akhir) {
  const dlm = (t) => (t || '') >= awal && (t || '') <= akhir;
  const prive = ambilPengeluaranHarian().filter((h) => h.kategori === 'owner' && dlm(h.tanggal)).reduce((a, h) => a + (Number(h.nominal) || 0), 0);
  const alih = ambilKasbonMutasi().filter((m) => m.tipe === 'bayar' && m.alih === 'prive' && ugKasbonOwner(m) && dlm(m.tanggal)).reduce((a, m) => a + (Number(m.nominal) || 0), 0);
  const tarik = daftarModalOwner().filter((m) => m.tipe !== 'setor' && !m.pinjaman && dlm(m.tanggal)).reduce((a, m) => a + (Number(m.nominal) || 0), 0);
  return { prive, alih, tarik, total: prive + alih + tarik, awal, akhir };
}
/** Ambil pribadi bulan ini (awal bulan sampai iso). */
export function priveBulan(iso) { return priveRentang(ugAwalBulan(iso), iso); }
// ---------- putaran 29: tiga TUJUAN uang keluar (owner 27 Sep 2026) ----------
// `untuk` = kolom baru di pengeluaranHarian: 'toko' (operasional: kantong, listrik, bahan masak untuk makan karyawan, perbaikan) atau 'karyawan'
// (dinikmati karyawan di luar upah: kopi, rokok, makanan jadi dari warung). Keduanya TETAP kategori 'toko'/'tokoDompet' di mata mesin laba —
// yang bertambah hanya pemilahannya. Catatan lama tanpa `untuk` = BELUM DIPILAH (bukan toko, bukan karyawan); di kartu ia dihitung di biaya toko
// (arti yang selama ini ia punya) dan jumlahnya disebut. Pribadi = kategori 'owner' seperti sekarang, tidak diberi `untuk`.
export const TUJUAN_KELUAR = [['toko', 'Untuk toko'], ['karyawan', 'Untuk karyawan'], ['pribadi', 'Untuk pribadi']];
export const ugUntukDok = (h) => (h.kategori === 'owner' ? 'pribadi' : h.untuk === 'karyawan' ? 'karyawan' : h.untuk === 'toko' ? 'toko' : '');
const ugBiayaBank = (h) => !!(h.dariBayarBon || h.dariPindah) || /^biaya admin/i.test(String(h.keterangan || ''));
/** Pemilahan biaya toko harian (kategori toko + tokoDompet, = harianToko mesin laba) dalam rentang: untuk toko · untuk karyawan · belum dipilah; di dalam toko: potongan QRIS & biaya bank. */
export function pilahHarian(awal, akhir) {
  const P = { total: 0, n: 0, toko: 0, nToko: 0, karyawan: 0, nKaryawan: 0, belum: 0, nBelum: 0, mdr: 0, nMdr: 0, bank: 0, nBank: 0, awal, akhir };
  ambilPengeluaranHarian().forEach((h) => { if (!(h.kategori === 'toko' || h.kategori === 'tokoDompet') || !h.tanggal || h.tanggal < awal || h.tanggal > akhir) return; const n = Number(h.nominal) || 0; P.total += n; P.n += 1;
    const u = ugUntukDok(h); if (u === 'karyawan') { P.karyawan += n; P.nKaryawan += 1; return; }
    if (u === 'toko') { P.toko += n; P.nToko += 1; } else { P.belum += n; P.nBelum += 1; }
    if (h.mdr && h.kategori === 'toko') { P.mdr += n; P.nMdr += 1; } else if (ugBiayaBank(h)) { P.bank += n; P.nBank += 1; } });
  P.tokoSemua = P.toko + P.belum;   // yang dihitung sebagai keperluan toko di kartu = dipilah toko + belum dipilah
  return P;
}

// ==================== K1 · CATAT UANG KELUAR ====================
export const TAB_KELUAR = [['hari', 'Hari ini'], ['catat', 'Catat'], ['tagihan', 'Tagihan']];
export const ATUR_KELUAR_BAWAAN = { perluToko: [], perluKaryawan: [], perluPribadi: [], bulanan: [], aman: 0, alasan: ['Mendesak keluarga', 'Sudah diperhitungkan', 'Ditutup dari laba bulan depan'] };
// bawaan bila catatan kosong: 'karyawan' = yang dinikmati karyawan di luar upah (owner 27 Sep: kopi, rokok, makan dari warung); bahan mentah untuk memasak = toko
const UK_PERLU_UMUM = { toko: ['Bensin antar', 'Upah bongkar', 'Kebutuhan masak', 'Tali & plastik', 'Lain-lain'], karyawan: ['Kopi', 'Rokok', 'Makan dari warung', 'Lain-lain'], pribadi: ['Belanja dapur', 'Keperluan keluarga', 'Lain-lain'] };
/** Keperluan yang TERUKUR dari catatan: keterangan yang paling sering dipakai (dan nominal biasanya = median), bukan daftar karangan. kategori = toko | karyawan | owner. */
export function perluTerukur(kategori) {
  const cocokK = (h) => (kategori === 'owner' ? h.kategori === 'owner' : (h.kategori === 'toko' || h.kategori === 'tokoDompet') && (kategori === 'karyawan' ? h.untuk === 'karyawan' : h.untuk !== 'karyawan'));
  const k = {}; ambilPengeluaranHarian().forEach((h) => { if (cocokK(h) && h.keterangan) { const nm = String(h.keterangan).trim().replace(/\s*\((bulanan|dari .*)\)$/i, ''); const kk = nm.toLowerCase(); if (!kk || /^potongan qris|^biaya admin/.test(kk)) return; if (!k[kk]) k[kk] = { nama: nm, n: 0, nominal: [] }; k[kk].n += 1; k[kk].nominal.push(Number(h.nominal) || 0); } });
  const urut = Object.keys(k).map((x) => k[x]).sort((a, b) => b.n - a.n).slice(0, 6);
  if (!urut.length) return UK_PERLU_UMUM[kategori === 'toko' ? 'toko' : kategori === 'karyawan' ? 'karyawan' : 'pribadi'].map((nama) => ({ nama, biasa: 0 }));
  return urut.map((x) => { const s = x.nominal.slice().sort((a, b) => a - b); const med = s.length ? s[Math.floor((s.length - 1) / 2)] : 0; return { nama: x.nama, biasa: x.n >= 3 ? Math.round(med / 1000) * 1000 : 0 }; });
}
export function aturKeluar(iso) {
  const a = ugAturDok('uangKeluar') || {}; const daftar = (arr, ganti) => (Array.isArray(arr) && arr.length ? arr.filter((x) => x && String(x.nama || '').trim()).map((x) => ({ nama: String(x.nama).trim(), biasa: Math.max(0, Math.round(Number(x.biasa) || 0)) })) : ganti);
  const amanOwner = isFinite(Number(a.aman)) && Number(a.aman) > 0 ? Math.round(Number(a.aman)) : 0;
  const laba = iso ? hitungLabaBersihRentang(ugAwalBulan(iso), iso).labaBersih : 0;
  return { perluToko: daftar(a.perluToko, perluTerukur('toko')), perluKaryawan: daftar(a.perluKaryawan, perluTerukur('karyawan')), perluPribadi: daftar(a.perluPribadi, perluTerukur('owner')), bulanan: daftar(a.bulanan, []), alasan: Array.isArray(a.alasan) && a.alasan.length ? a.alasan.map(String) : ATUR_KELUAR_BAWAAN.alasan,
    aman: amanOwner || Math.max(0, laba), amanDariLaba: !amanOwner, labaBulan: laba, dariOwner: !!ugAturDok('uangKeluar'), terukurToko: !(Array.isArray(a.perluToko) && a.perluToko.length), terukurKaryawan: !(Array.isArray(a.perluKaryawan) && a.perluKaryawan.length), terukurPribadi: !(Array.isArray(a.perluPribadi) && a.perluPribadi.length) };
}
/** Daftar keperluan menurut tujuan (toko · karyawan · pribadi). */
export const perluUntuk = (A, untuk) => (untuk === 'karyawan' ? A.perluKaryawan : untuk === 'pribadi' ? A.perluPribadi : A.perluToko);
export function susunAturKeluar(isi, w) {
  const daftar = (arr, nama) => { const out = []; let salah = ''; (Array.isArray(arr) ? arr : []).forEach((x) => { const nm = String((x && x.nama) || '').trim(); const n = ugAngka(x && x.biasa); if (!nm && !(n > 0)) return; if (!nm) { salah = nama + ': ada baris bernominal ' + RP(n) + ' tanpa nama'; return; } out.push({ nama: nm.slice(0, 40), biasa: Math.max(0, Math.round(n)) }); }); return { out, salah }; };
  const t = daftar(isi.perluToko, 'Keperluan toko'), ky = daftar(isi.perluKaryawan, 'Keperluan karyawan'), p = daftar(isi.perluPribadi, 'Keperluan pribadi'), b = daftar(isi.bulanan, 'Tagihan bulanan');
  const salah = t.salah || ky.salah || p.salah || b.salah; if (salah) return { tolak: salah };
  // satu nama tidak boleh hidup di dua tujuan — tombol rutinnya jadi bermakna ganda
  const kembar = t.out.map((x) => x.nama.toLowerCase()).filter((nm) => ky.out.some((y) => y.nama.toLowerCase() === nm)); if (kembar.length) return { tolak: '"' + kembar[0] + '" ada di keperluan toko DAN karyawan — pilih salah satu tujuannya' };
  const aman = ugKosong(isi.aman) ? 0 : ugAngka(isi.aman); if (aman < 0) return { tolak: 'Batas aman tidak boleh minus' };
  const alasan = (Array.isArray(isi.alasan) ? isi.alasan : []).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'uangKeluar', tanggal: w.tanggal, jam: w.jam, perluToko: t.out, perluKaryawan: ky.out, perluPribadi: p.out, bulanan: b.out, aman: Math.round(aman), alasan: alasan.length ? alasan : ATUR_KELUAR_BAWAAN.alasan } }],
    patch: { aturK: null, kabar: 'Aturan uang keluar disimpan — ' + t.out.length + ' keperluan toko · ' + ky.out.length + ' karyawan · ' + p.out.length + ' pribadi · ' + b.out.length + ' tagihan tambahan · batas aman ' + (aman > 0 ? RP(aman) : 'ikut laba bulan berjalan'), kabarAwas: false } };
}
/** Empat arti — satu tempat, dibaca layar dan buktinya. untuk = toko | karyawan | pribadi (karyawan = biaya toko yang dipilah untuk karyawan; laba turun sama besar). */
export function artiKeluar(untuk, dari, n, sbgKasbon) {
  const k = ugNamaTempat(dari); const ky = untuk === 'karyawan';
  if (sbgKasbon) return { sel: 'kasbon', cap: 'kasbon owner', judul: 'Kasbon owner', a: k + ' berkurang ' + RP(n), b: 'laba tidak berubah, ambil pribadi tidak bertambah', c: 'owner berutang ' + RP(n) + ' ke toko — wajib dikembalikan' };
  if ((untuk === 'toko' || ky) && dari !== 'dompet') return { sel: 'beban', cap: ky ? 'untuk karyawan' : 'biaya toko', judul: ky ? 'Untuk karyawan (biaya toko)' : 'Biaya toko', a: k + ' berkurang ' + RP(n), b: 'laba berkurang ' + RP(n), c: ky ? 'dipilah sebagai biaya karyawan di luar upah' : '' };
  if (untuk === 'toko' || ky) return { sel: 'utang', cap: ky ? 'untuk karyawan · berutang' : 'toko berutang', judul: ky ? 'Untuk karyawan — toko berutang ke owner' : 'Toko berutang ke owner', a: 'uang toko tidak berkurang', b: 'laba berkurang ' + RP(n), c: 'toko berutang ' + RP(n) + ' ke owner' + (ky ? ' · dipilah sebagai biaya karyawan' : '') };
  if (dari !== 'dompet') return { sel: 'prive', cap: 'ambil pribadi', judul: 'Ambil pribadi (prive)', a: k + ' berkurang ' + RP(n), b: 'laba TIDAK berubah', c: 'ini uang pribadi owner, bukan biaya toko' };
  return { sel: 'luar', cap: 'bukan urusan toko', judul: 'Tidak masuk catatan toko', a: 'uang toko tidak tersentuh', b: 'laba tidak berubah', c: 'tidak ada yang ditulis' };
}
/** Periksa isian K1: D = { untuk: toko|karyawan|pribadi, dari: laci|brankas|rekening|dompet, perlu, ketik, catatan }. */
export function hitungKeluar(D, kini) {
  const iso = hariIniIso(kini); const A = aturKeluar(iso); const S = saldoKantong(); const n = Math.round(ugAngka(D.ketik)); const A4 = artiKeluar(D.untuk, D.dari, n, false);
  const P = priveBulan(iso); const sisaAman = A.aman - P.total;
  const daftarPerlu = perluUntuk(A, D.untuk); const perlu = daftarPerlu.find((p) => p.nama === D.perlu) || (D.perlu && String(D.perlu).trim() ? { nama: String(D.perlu).trim(), biasa: 0 } : null);
  let tolak = ''; let cukup = { boleh: true, teks: '' };
  if (!(n > 0)) tolak = 'Isi nominalnya dulu'; else if (!perlu) tolak = 'Pilih untuk apa';
  else if (D.dari !== 'dompet') { cukup = ugCukup(S, D.dari, n); if (!cukup.boleh) tolak = cukup.teks; }
  const lewatAman = !tolak && A4.sel === 'prive' && n > Math.max(0, sisaAman);
  return { n, arti: A4, perlu, tolak, lewatAman, sisaAman, aman: A.aman, amanDariLaba: A.amanDariLaba, priveTerpakai: P.total, takTerperiksa: !!cukup.takTerperiksa, catatanCukup: cukup.takTerperiksa ? cukup.teks : '', S, atur: A,
    priveTeks: A.amanDariLaba && A.labaBulan <= 0 ? 'Ambil pribadi bulan ini ' + RP(P.total) + ' — bulan ini belum ada laba bersih (' + RP(A.labaBulan) + '), jadi setiap ambil pribadi berjalan dari modal; batas aman bisa disetel di Atur'
      : sisaAman >= 0 ? 'Ambil pribadi bulan ini ' + RP(P.total) + ' · batas aman ' + RP(A.aman) + (A.amanDariLaba ? ' (= laba bersih bulan berjalan)' : '') + ' · sisa ' + RP(sisaAman) : 'Ambil pribadi bulan ini ' + RP(P.total) + ' — sudah LEWAT ' + RP(-sisaAman) + ' dari batas aman ' + RP(A.aman) + (A.amanDariLaba ? ' (= laba bersih bulan berjalan)' : ''),
    lewatTeks: lewatAman ? 'Ambil pribadi ' + RP(n) + ' ini membuat bulan ini lewat ' + RP(n - Math.max(0, sisaAman)) + ' dari batas aman ' + RP(A.aman) + '.' : '', kasbonTeks: (function () { const K = artiKeluar(D.untuk, D.dari, n, true); return K.a + ' · ' + K.b + ' · ' + K.c; })() };
}
/** Susun dokumennya. pilihan = { jadiKasbon: true } | { alasan: '…' } | null. */
export function susunKeluar(D, w, pilihan) {
  const H = hitungKeluar(D, ugKiniDari(w)); if (H.tolak) return { tolak: H.tolak };
  const P = pilihan || {}; const ket = H.perlu.nama + (D.catatan && String(D.catatan).trim() ? ' — ' + String(D.catatan).trim().slice(0, 60) : '');
  if (H.lewatAman && !P.jadiKasbon && !P.alasan) return { tolak: H.lewatTeks + ' Catat sebagai kasbon owner, atau pilih alasannya.', perluYakin: 'aman' };
  if (H.arti.sel === 'luar') return { dokumen: [], patch: { kabar: 'Tidak masuk catatan toko — uang pribadi dari dompet sendiri. Tidak ada yang ditulis.', kabarAwas: false, ketik: '', perlu: '' } };
  if (P.jadiKasbon) {
    const data = { id: w.idUnik(), tipe: 'ambil', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: H.n, tanggal: w.tanggal, jam: w.jam, catatan: ket, dari: D.dari };
    return { dokumen: [{ koleksi: 'kasbonMutasi', data }], urung: [{ koleksi: 'kasbonMutasi', id: data.id }], patch: { kabar: 'Tercatat · Kasbon owner ' + RP(H.n) + ' dari ' + ugNamaTempat(D.dari) + ' — owner berutang ke toko, ambil pribadi tidak bertambah', kabarAwas: false, ketik: '', perlu: '', paksa: null } };
  }
  const kategori = H.arti.sel === 'beban' ? 'toko' : H.arti.sel === 'utang' ? 'tokoDompet' : 'owner';
  const data = { id: w.idUnik(), kategori, tanggal: w.tanggal, keterangan: ket, nominal: H.n, jam: w.jam };
  if (kategori !== 'owner') data.untuk = D.untuk === 'karyawan' ? 'karyawan' : 'toko';   // putaran 29: tujuan dipilah; pribadi tetap bentuk lama
  if (D.dari !== 'dompet') data.dari = D.dari;
  if (P.alasan) { data.alasanAman = String(P.alasan).trim().slice(0, 80); }
  const A4 = H.arti;
  return { dokumen: [{ koleksi: 'pengeluaranHarian', data }], urung: [{ koleksi: 'pengeluaranHarian', id: data.id }],
    patch: { kabar: 'Tercatat · ' + A4.judul + ' ' + RP(H.n) + ' — ' + A4.a + ' · ' + A4.b + (A4.c ? ' · ' + A4.c : '') + (H.takTerperiksa ? ' · ' + H.catatanCukup : ''), kabarAwas: false, ketik: '', perlu: '', catatan: '', paksa: null } };
}
export function susunUrungKeluar(urung) {
  if (!urung || !urung.length) return { tolak: 'Tidak ada yang bisa dibatalkan' };
  return { hapus: urung.slice(), patch: { kabar: 'Dibatalkan — catatan tadi dicabut, tidak ada yang berubah', kabarAwas: false, urung: null } };
}
/** Titipan dari tablet: permintaan "catat uang keluar" yang menunggu owner (koleksi persetujuan, SS2). Menyetujui = menulis pengeluarannya + memutus permintaannya. */
export function titipanKeluar() {
  return cacheMentah('persetujuan').filter((m) => m.tindakan === 'uangKeluar' && (!m.status || m.status === 'menunggu')).sort((a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || '')))
    .map((m) => ({ id: String(m.id), oleh: m.dari || '?', teks: m.teks || '(tanpa keterangan)', n: Math.round(Number(m.nominal) || 0), tanggal: m.tanggal || '', jam: m.jam || '', dari: m.dariTempat || 'laci' }));
}
export function susunPutusTitipan(id, setuju, alasan, w) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id)); if (!m) return { tolak: 'Permintaannya tidak ditemukan' };
  if (m.status && m.status !== 'menunggu') return { tolak: 'Sudah diputus ' + (m.diputusTanggal ? tanggalPendek(m.diputusTanggal) : '') };
  if (!setuju && ugKosong(alasan)) return { tolak: 'Menolak butuh alasan — supaya ' + (m.dari || 'peminta') + ' tahu sebabnya' };
  const dokumen = [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: setuju ? 'disetujui' : 'ditolak', alasanTolak: setuju ? '' : String(alasan).trim().slice(0, 80), diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini }) }];
  const n = Math.round(Number(m.nominal) || 0); const dari = m.dariTempat || 'laci';
  if (setuju) { if (!(n > 0)) return { tolak: 'Permintaan ini tidak menyebut nominal — tolak, minta dicatat ulang' }; dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: String(m.teks || 'Titipan tablet').slice(0, 80), nominal: n, dari, oleh: (m.dari || 'tablet') + ' (disetujui owner)', dariPersetujuan: String(m.id) } }); }
  return { dokumen, patch: { kabar: setuju ? 'Catatan ' + (m.dari || 'tablet') + ' disetujui · ' + ugNamaTempat(dari) + ' berkurang ' + RP(n) : 'Catatan ' + (m.dari || 'tablet') + ' ditolak — uang toko tidak berubah, ' + (m.dari || 'tablet') + ' diberi tahu di perangkatnya', kabarAwas: false } };
}
/** Buku hari ini: semua uang keluar (harian toko/owner/tokoDompet + kasbon owner) bertanggal iso, terbaru di atas. */
export function bukuKeluar(iso) {
  const rows = [];
  ambilPengeluaranHarian().forEach((h) => { if (h.tanggal !== iso) return; const sel = h.kategori === 'tokoDompet' ? 'utang' : h.kategori === 'owner' ? 'prive' : 'beban'; const untuk = ugUntukDok(h); const A = artiKeluar(untuk || 'toko', h.kategori === 'tokoDompet' ? 'dompet' : (h.dari || 'laci'), Number(h.nominal) || 0, false);
    rows.push({ id: String(h.id), koleksi: 'pengeluaranHarian', jam: h.jam || '', ket: h.keterangan || '', n: Number(h.nominal) || 0, sel, untuk, cap: untuk || sel === 'prive' ? A.cap : A.cap + ' · belum dipilah', dari: h.kategori === 'tokoDompet' ? 'dompet owner' : ugNamaTempat(h.dari || 'laci').toLowerCase() + (h.dari ? '' : ' (dianggap)'), oleh: h.oleh || '', alasan: h.alasanAman || '', otomatis: !!(h.dariBayarBon || h.dariPindah || h.mdr || h.dariTutup) }); });
  ambilKasbonMutasi().forEach((m) => { if (m.tanggal !== iso || m.tipe !== 'ambil' || !ugKasbonOwner(m)) return; rows.push({ id: String(m.id), koleksi: 'kasbonMutasi', jam: m.jam || '', ket: m.catatan || 'Kasbon owner', n: Number(m.nominal) || 0, sel: 'kasbon', untuk: '', cap: 'kasbon owner', dari: ugNamaTempat(m.dari || 'laci').toLowerCase(), oleh: m.oleh || '', alasan: '', otomatis: false }); });
  rows.sort((a, b) => String(b.jam).localeCompare(String(a.jam)) || String(b.id).localeCompare(String(a.id)));
  const j = { beban: 0, utang: 0, prive: 0, kasbon: 0, karyawan: 0 }; rows.forEach((r) => { j[r.sel] += r.n; if (r.untuk === 'karyawan') j.karyawan += r.n; });
  const laci = rows.filter((r) => r.dari.indexOf('laci') === 0).reduce((a, r) => a + r.n, 0);
  return { rows, jumlah: j, n: rows.length, keluarLaci: laci, total: rows.reduce((a, r) => a + r.n, 0) };
}
/** Tagihan bulanan bulan `iso`: empat pos mesin lama (dibagi rata per hari di laba) + tagihan tambahan owner (dicatat sebagai belanja harian hari itu). */
export function tagihanBulan(iso) {
  const bulan = String(iso).slice(0, 7); const A = aturKeluar(); const dok = ambilBiayaBulanan().find((b) => b.bulan === bulan) || null; const out = [];
  const bulanLalu = ambilBiayaBulanan().filter((b) => b.bulan < bulan).sort((a, b) => b.bulan.localeCompare(a.bulan)).slice(0, 3);
  POS_BIAYA_BULANAN.forEach((pos) => { const n = dok ? Number(dok[pos.kunci]) || 0 : 0; const tgl = dok ? ((dok.tanggalBayarPos || {})[pos.kunci] || (dok.tanggalBayarPos ? '' : (dok.tanggalBayar || ''))) : '';
    const lalu = bulanLalu.map((b) => Number(b[pos.kunci]) || 0).filter((x) => x > 0).sort((a, b) => a - b); const biasa = lalu.length ? lalu[Math.floor((lalu.length - 1) / 2)] : 0;
    out.push({ kunci: pos.kunci, nama: pos.label, jenis: 'pos', lunas: n > 0 && !!tgl, n, tanggal: tgl, biasa, tercatatTanpaTanggal: n > 0 && !tgl, dari: dok && dok.dariPos ? dok.dariPos[pos.kunci] || '' : '' }); });
  A.bulanan.forEach((t) => { const h = ambilPengeluaranHarian().find((x) => x.kategori === 'toko' && String(x.tanggal || '').slice(0, 7) === bulan && x.keterangan === t.nama + ' (bulanan)') || null;
    out.push({ kunci: 'tambahan:' + t.nama, nama: t.nama, jenis: 'tambahan', lunas: !!h, n: h ? Number(h.nominal) || 0 : 0, tanggal: h ? h.tanggal : '', biasa: t.biasa, tercatatTanpaTanggal: false, dari: h ? h.dari || '' : '' }); });
  const belum = out.filter((t) => !t.lunas); return { bulan, daftar: out, belum, nBelum: belum.length, perkiraan: belum.reduce((a, t) => a + (t.biasa || 0), 0), namaBulan: namaBulanPanjang(bulan + '-01'), dok };
}
/** Bayar satu tagihan: pos mesin lama → dokumen biayaBulanan bulan itu (digabung, tanggal per pos); tambahan → belanja harian "<nama> (bulanan)". */
export function susunBayarTagihan(kunci, ketik, dari, w) {
  const T = tagihanBulan(w.tanggal); const t = T.daftar.find((x) => x.kunci === kunci); if (!t) return { tolak: 'Tagihan tidak dikenal' };
  if (t.lunas) return { tolak: t.nama + ' sudah dibayar ' + tanggalPendek(t.tanggal) + ' bulan ini' };
  const n = Math.round(ugKosong(ketik) ? t.biasa : ugAngka(ketik)); if (!(n > 0)) return { tolak: 'Ketik jumlahnya — belum ada nominal biasanya untuk ' + t.nama };
  if (!TEMPAT_UANG.some((x) => x[0] === dari)) return { tolak: 'Uangnya dari mana — laci, brankas, atau rekening?' };
  const S = saldoKantong(); const c = ugCukup(S, dari, n); if (!c.boleh) return { tolak: c.teks };
  if (t.jenis === 'tambahan') { const data = { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: t.nama + ' (bulanan)', nominal: n, dari };
    return { dokumen: [{ koleksi: 'pengeluaranHarian', data }], urung: [{ koleksi: 'pengeluaranHarian', id: data.id }], patch: { kabar: t.nama + ' dibayar ' + RP(n) + ' dari ' + ugNamaTempat(dari) + ' — dicatat sebagai belanja harian hari ini (laba hari ini)' + (c.takTerperiksa ? ' · ' + c.teks : ''), kabarAwas: false, bayarT: null } }; }
  const lama = T.dok || { id: T.bulan, bulan: T.bulan }; const data = Object.assign({}, lama, { id: T.bulan, bulan: T.bulan });
  // dokumen lama bertanggal tunggal (tanggalBayar): saat berpindah ke peta per pos, SEMUA pos yang sudah bernilai dibawa tanggalnya — kalau tidak, pos lain mendadak "belum dibayar" dan kas bergeser
  const peta = Object.assign({}, lama.tanggalBayarPos || {}); if (!lama.tanggalBayarPos && lama.tanggalBayar) { POS_BIAYA_BULANAN.forEach((p) => { if (Number(lama[p.kunci]) > 0) peta[p.kunci] = lama.tanggalBayar; }); if (Number(lama.gaji) > 0) peta.gaji = lama.tanggalBayar; }
  peta[t.kunci] = w.tanggal; data.tanggalBayarPos = peta; data[t.kunci] = n; data.dariPos = Object.assign({}, lama.dariPos || {}, { [t.kunci]: dari });
  ['akses', 'keamanan', 'listrik', 'internet'].forEach((k) => { if (data[k] === undefined) data[k] = 0; }); if (data.gaji === undefined) data.gaji = 0; if (data.gajiHariOrang === undefined) data.gajiHariOrang = 0; if (!Array.isArray(data.rincianGaji)) data.rincianGaji = [];
  return { dokumen: [{ koleksi: 'biayaBulanan', data }], patch: { kabar: t.nama + ' ' + T.namaBulan + ' dibayar ' + RP(n) + ' dari ' + ugNamaTempat(dari) + ' — uang keluar hari ini; di laba dibagi rata per hari sebulan (mesin lama)' + (c.takTerperiksa ? ' · ' + c.teks : ''), kabarAwas: false, bayarT: null } };
}

// ==================== K4 · PINDAH UANG ====================
export const ATUR_PINDAH_BAWAAN = { jaga: 500000, alasan: ['Amankan ke brankas', 'Isi laci untuk kembalian', 'Setor ke bank', 'Tarik tunai dari bank', 'Lain-lain'] };
export function aturPindah() {
  const a = ugAturDok('pindahUang') || {}; const jaga = isFinite(Number(a.jaga)) && Number(a.jaga) >= 0 ? Math.round(Number(a.jaga)) : ATUR_PINDAH_BAWAAN.jaga;
  return { jaga, alasan: Array.isArray(a.alasan) && a.alasan.length ? a.alasan.map(String) : ATUR_PINDAH_BAWAAN.alasan.slice(), admin: aturBon().admin, dariOwner: !!ugAturDok('pindahUang') };
}
export function susunAturPindah(isi, w) {
  const jaga = ugKosong(isi.jaga) ? aturPindah().jaga : ugAngka(isi.jaga); if (!(jaga >= 0) || jaga > 100000000) return { tolak: 'Uang kembalian di laci harus 0–100.000.000' };
  const alasan = (Array.isArray(isi.alasan) ? isi.alasan : []).map((x) => String(x || '').trim()).filter(Boolean).slice(0, 8); if (!alasan.length) return { tolak: 'Pilihan "untuk apa" tidak boleh kosong' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'pindahUang', tanggal: w.tanggal, jam: w.jam, jaga: Math.round(jaga), alasan } }], patch: { aturP: null, kabar: 'Aturan pindah uang disimpan — uang kembalian di laci ' + RP(jaga) + ' · ' + alasan.length + ' pilihan alasan. Biaya admin bank diatur di Bon pemasok (satu daftar untuk keduanya).', kabarAwas: false } };
}
/** D = { dari, ke, ketik, alasan, adminI }. */
export function hitungPindah(D) {
  const S = saldoKantong(); const A = aturPindah(); const n = Math.round(ugAngka(D.ketik)); const pakaiAdmin = D.dari === 'rekening' || D.ke === 'rekening'; const biaya = pakaiAdmin && D.adminI >= 0 ? A.admin[Number(D.adminI)] || null : null; const admin = biaya ? biaya.n : 0;
  let tolak = ''; let cukup = { boleh: true, teks: '' };
  if (!D.dari || !D.ke) tolak = 'Pilih dari mana dan ke mana'; else if (D.dari === D.ke) tolak = 'Dari dan ke tidak boleh sama'; else if (!(n > 0)) tolak = 'Isi nominalnya dulu'; else if (!D.alasan) tolak = 'Pilih untuk apa';
  else { cukup = ugCukup(S, D.dari, n + admin); if (!cukup.boleh) tolak = cukup.teks + (admin ? ' (termasuk biaya admin ' + RP(admin) + ')' : ''); }
  return { n, admin, biaya, pakaiAdmin, tolak, S, atur: A, takTerperiksa: !!cukup.takTerperiksa, catatanCukup: cukup.takTerperiksa ? cukup.teks : '',
    artiA: ugNamaTempat(D.dari) + ' berkurang ' + RP(n + admin) + ' · ' + ugNamaTempat(D.ke) + ' bertambah ' + RP(n),
    artiB: admin ? 'jumlah uang toko berkurang ' + RP(admin) + ' — itu biaya admin bank, masuk biaya toko · laba berkurang ' + RP(admin) : 'jumlah uang toko TIDAK berubah · laba tidak berubah — ini cuma pindah tempat',
    label: tolak || ('PINDAHKAN ' + RP(n) + ' · ' + ugNamaTempat(D.dari) + ' → ' + ugNamaTempat(D.ke)), semua: S.ada && D.dari ? Math.max(0, Math.round((S[D.dari] || 0) - admin)) : 0, sisakan: S.ada && D.dari ? Math.max(0, Math.round((S[D.dari] || 0) - A.jaga - admin)) : 0 };
}
export function susunPindah(D, w) {
  const H = hitungPindah(D); if (H.tolak) return { tolak: H.tolak };
  const data = { id: D.id || w.idUnik(), tanggal: w.tanggal, jam: w.jam, dari: D.dari, ke: D.ke, nominal: H.n, alasan: String(D.alasan).slice(0, 60), biayaAdmin: H.admin, adminNama: H.biaya ? H.biaya.nama : '' };
  const dokumen = [{ koleksi: 'pindahUang', data }]; const urung = [{ koleksi: 'pindahUang', id: data.id }];
  if (H.admin > 0) { const adm = { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama + ' — pindah uang ' + ugNamaTempat(D.dari) + ' → ' + ugNamaTempat(D.ke), nominal: H.admin, dari: D.dari, dariPindah: data.id }; dokumen.push({ koleksi: 'pengeluaranHarian', data: adm }); urung.push({ koleksi: 'pengeluaranHarian', id: adm.id }); }
  return { dokumen, urung, patch: { kabar: RP(H.n) + ' dipindah · ' + ugNamaTempat(D.dari) + ' → ' + ugNamaTempat(D.ke) + (H.admin ? ' · biaya admin ' + RP(H.admin) + ' jadi biaya toko' : ' · jumlah uang toko tetap') + (H.takTerperiksa ? ' · ' + H.catatanCukup : ''), kabarAwas: false, pindah: null } };
}
export function susunUrungPindah(id) {
  const p = ambilPindahUang().find((x) => String(x.id) === String(id)); if (!p) return { tolak: 'Catatan pindahnya tidak ditemukan' };
  const hapus = [{ koleksi: 'pindahUang', id: p.id }]; ambilPengeluaranHarian().forEach((h) => { if (String(h.dariPindah || '') === String(p.id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });
  return { hapus, patch: { kabar: 'Dibatalkan — ' + RP(Number(p.nominal) || 0) + ' kembali ke ' + ugNamaTempat(p.dari) + (hapus.length > 1 ? ', biaya adminnya ikut dicabut' : ''), kabarAwas: false, urung: null } };
}
/** putaran 29 (Bagian 4): CATAT ISI REKENING menurut m-banking. Tutup hari tidak pernah menghitung rekening (ia hanya memotong MDR), jadi titik kas
 *  rekening bisa 0 = belum pernah diisi — dan transfer ke pemasok akan ditolak "rekening tidak cukup". Ditulis sebagai pengaturan/titikKas (jenis yang
 *  sudah ada) bertanggal KEMARIN: laci/brankas/amplop = hasil hitung sampai kemarin, rekening = isi yang diketik DIKURANGI gerakan rekening hari ini,
 *  supaya gerakan hari ini tetap terhitung. Bila titik sudah bertanggal hari ini (sesudah Tutup hari), titik hari ini ditulis ulang dengan rekening yang
 *  diketik. Kas total bergeser sebesar selisihnya; di laporan arus kas ia muncul sebagai titik yang disetel ulang (baris bernama), tidak disembunyikan. */
export function hitungTitikRekening(ketik, w) {
  const S = saldoKantong(); const n = Math.round(ugAngka(ketik)); const kemarin = ugTambahHari(w.tanggal, -1);
  if (!S.ada) return { n, tolak: 'Titik kas belum disetel — Tutup hari dulu malam ini, sesudahnya isi rekening bisa dicatat', S, belumPernah: true };
  if (ugKosong(ketik) || n < 0) return { n, tolak: 'Ketik isi rekening menurut m-banking', S, belumPernah: !(Number(S.titik.rekening) > 0) };
  const T = S.titik; let dasar, tanggal, rekening;
  if (kemarin >= T.tanggal) { dasar = saldoKantong(kemarin); tanggal = kemarin; rekening = n - (S.rekening - dasar.rekening); } else { dasar = S; tanggal = T.tanggal; rekening = n; }
  const selisih = n - S.rekening; const titik = { id: 'titikKas', tanggal, laci: Math.round(dasar.laci), brankas: Math.round(dasar.brankas), rekening: Math.round(rekening), amplop: Math.round(dasar.amplop), diubahPada: w.kini };
  return { n, tolak: '', S, titik, selisih, belumPernah: !(Number(T.rekening) > 0), arti: 'Rekening jadi ' + RP(n) + ' (' + (selisih === 0 ? 'sama dengan hitungan' : (selisih > 0 ? 'naik ' : 'turun ') + RP(Math.abs(selisih)) + ' dari hitungan ' + RP(S.rekening)) + ') · laci, brankas, amplop tidak berubah · laba tidak berubah · patokan kas pindah ke ' + tanggalPendek(tanggal) };
}
export function susunTitikRekening(ketik, w) {
  const H = hitungTitikRekening(ketik, w); if (H.tolak) return { tolak: H.tolak };
  return { dokumen: [{ koleksi: 'pengaturan', data: H.titik }], titik: H.titik, patch: { rekIsi: null, kabar: 'Isi rekening dicatat ' + RP(H.n) + ' — ' + H.arti, kabarAwas: false } };
}
/** Rutin sekali ketuk: angkanya dihitung dari isi tempat uang SAAT INI (bukan angka mati). */
export function rutinPindah() {
  const S = saldoKantong(); const A = aturPindah(); if (!S.ada) return { ada: false, S, jaga: A.jaga, daftar: [] };
  const amankan = Math.max(0, Math.round(S.laci - A.jaga)), isi = Math.max(0, Math.round(A.jaga - S.laci));
  return { ada: true, S, jaga: A.jaga, daftar: [
    { id: 'amankan', t: 'Tutup toko — amankan laci', k: 'laci → brankas · sisakan ' + RP(A.jaga) + ' untuk kembalian besok', n: amankan, bisa: amankan > 0, dari: 'laci', ke: 'brankas', alasan: 'Amankan ke brankas' },
    { id: 'isi', t: 'Buka toko — isi laci', k: 'brankas → laci · sampai laci berisi ' + RP(A.jaga), n: isi, bisa: isi > 0 && isi <= S.brankas, dari: 'brankas', ke: 'laci', alasan: 'Isi laci untuk kembalian' }] };
}
/** Buku pindah: pindahUang + sisihan amplop tutup hari (amplopLaba), terbaru di atas. */
export function bukuPindah(n) {
  const rows = ambilPindahUang().map((p) => ({ id: String(p.id), t: (p.tanggal || '') + ' ' + (p.jam || ''), tanggal: p.tanggal || '', jam: p.jam || '', judul: ugNamaTempat(p.dari) + ' → ' + ugNamaTempat(p.ke), ket: (p.alasan || '') + (Number(p.biayaAdmin) > 0 ? ' · biaya admin ' + RP(p.biayaAdmin) + (p.adminNama ? ' (' + p.adminNama + ')' : '') : ''), n: Number(p.nominal) || 0, jenis: 'pindah', oleh: p.oleh || '' }))
    .concat(ambilAmplopLaba().filter((a) => !a.tutupBuku && Number(a.nominal) > 0).map((a) => ({ id: String(a.id), t: (a.tanggal || '') + ' ' + (a.jam || ''), tanggal: a.tanggal || '', jam: a.jam || '', judul: a.tipe === 'ambil' ? 'Amplop laba → Laci' : 'Laci → Amplop laba', ket: a.catatan || (a.tipe === 'ambil' ? 'diambil dari amplop' : 'disisihkan'), n: Number(a.nominal) || 0, jenis: 'amplop', oleh: a.oleh || '' })));
  rows.sort((a, b) => b.t.localeCompare(a.t) || b.id.localeCompare(a.id)); return rows.slice(0, n || 30);
}
