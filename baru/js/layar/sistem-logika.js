// LOGIKA layar SISTEM (di bawah Menu → "Toko ini"), tanpa DOM. Desain terkunci owner 19 Sep 2026 (kanvas Sistem, SS1–SS5):
//   SS1 Perangkat & antrean kirim (sensus 61 + 64) · SS2 Peran & persetujuan (62) · SS3 Cadangan & kuota (63, pilihan C)
//   SS4 Lokasi (65, fondasi) · SS5 Pengingat (67, pilihan B + C: aturan + kalender).
// Sumber angka = data toko yang sama dengan sistem lama (perangkatStatus & logAktivitas = koleksi sistem lama); yang BARU:
// aturanToko/{perangkat,peran,cadangan,lokasi,pengingat} (angka & daftar kebijakan owner), cadanganCatatan, pengingat, persetujuan, pindahStok.
// Kejujuran: antrean = catatan yang sungguh belum diakui server (hasPendingWrites), bukan hitungan sendiri; yang tidak bisa dihitung DISEBUT.
// Tidak ada kolom PIN/sandi di mana pun — kunci perangkat diatur di perangkatnya (aturan tetap).
// Nama pembantu diprefiks `ss` karena bundel uji jsc satu lingkup.
import { hitungUtangPemasok, hitungStokBahanKemasan, hitungStokKarungPerMerk } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, kunciPelanggan } from '../mesin/pembantu.js';
import { KOLEKSI } from '../data/koleksi.js';
import { ambilPenjualan, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, ambilPetaJenisBeras, cacheMentah } from '../data/toko.js';
import { tempoPemasok } from './bon-pemasok-logika.js';
import { RP, ANGKA, hariIniIso, jamKini, tanggalPendek } from '../inti/format.js';
import { semuaBon, pesanTagih } from './bon-logika.js';
import { SERVER_BUKA } from '../data/akses.js';

export const ssHariKe = (iso) => Math.round(Date.UTC(+String(iso).slice(0, 4), +String(iso).slice(5, 7) - 1, +String(iso).slice(8, 10)) / 86400000);
export const ssTambahHari = (iso, n) => new Date((ssHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
const ssKosong = (v) => !String(v == null ? '' : v).trim();
const ssAngka = (v, min, maks) => { const n = Number(String(v == null ? '' : v).replace(',', '.')); return isFinite(n) && n >= min && n <= maks ? n : null; };
const ssUrutTerbaru = (a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || ''));
const ssHariNama = (iso) => ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'][new Date(iso + 'T00:00:00Z').getUTCDay()];

// ---------- tindakan berpintu izin & peran (SS2) — dari kanvas-kanvas yang sudah dikunci ----------
export const SS_TINDAKAN = [['jualTunai', 'Jual tunai & kembalian', 'Jual'], ['jualBon', 'Jual dengan bon (pelanggan lama)', 'Jual'], ['nego', 'Nego di bawah jatah margin', 'Jual'], ['terimaBon', 'Terima pembayaran bon', 'Uang'],
  ['hitungLaci', 'Hitung & rapikan laci', 'Uang'], ['uangKeluar', 'Catat uang keluar dari laci', 'Uang'], ['adukan', 'Catat adukan (bongkar kemasan)', 'Stok'], ['kedatangan', 'Hitung truk & draf kedatangan', 'Stok'],
  ['hargaBeli', 'Isi harga beli / modal', 'Stok'], ['koreksi', 'Koreksi nota yang sudah tersimpan', 'Jual'], ['hapus', 'Hapus catatan', 'Semua'], ['pelangganBaru', 'Daftarkan pelanggan baru', 'Pelanggan'], ['atur', 'Ubah setelan (Atur)', 'Sistem']].map((t) => ({ id: t[0], nama: t[1], modul: t[2] }));
export const SS_PERAN = [['owner', 'Owner'], ['ben', 'Ben (penjaga laci)'], ['karyawan', 'Karyawan (Hasan, Gono)']].map((p) => ({ id: p[0], nama: p[1] }));
export const SS_NILAI_HAK = ['sendiri', 'owner', 'tidak'];
export const SS_LABEL_HAK = { sendiri: 'boleh sendiri', owner: 'minta owner', tidak: 'tidak boleh' };
const SS_HAK_BAWAAN = { ben: { jualTunai: 'sendiri', jualBon: 'sendiri', nego: 'owner', terimaBon: 'sendiri', hitungLaci: 'sendiri', uangKeluar: 'owner', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'owner', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak' },
  karyawan: { jualTunai: 'sendiri', jualBon: 'owner', nego: 'tidak', terimaBon: 'sendiri', hitungLaci: 'tidak', uangKeluar: 'tidak', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'tidak', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak' } };
export const SS_JENIS_PENGINGAT = [['bon', 'Bon pemasok jatuh tempo', 'hariBon'], ['janji', 'Janji bayar pelanggan', 'hariJanji'], ['kantong', 'Kantong menipis', 'hariKantong'], ['opname', 'Opname rutin', 'hariOpname'], ['cadangan', 'Cadangan berkas', 'hariCadangan'], ['pajak', 'Setoran PPh final bulan lalu', 'hariPajak']].map((j) => ({ id: j[0], nama: j[1], kunci: j[2] }));
export const SS_PENERIMA = ['Owner', 'Ben'];

// ---------- ATUR SENDIRI — angka & daftar kebijakan owner, satu dokumen aturanToko per layar; bawaan = angka desain terkunci ----------
export const SS_ATUR_BAWAAN = {
  perangkat: { batasAntre: 30, batasDenyut: 15, pemegang: ['Owner', 'Ben'] },
  peran: { hak: SS_HAK_BAWAAN, batasSekaligus: 300000, jatahBen: 50, jejak: [] },
  cadangan: { simpanHari: 30, ambangKuota: 80, cadanganTiap: 7 },
  lokasi: { daftar: [{ id: 'toko', nama: 'Toko M.IQBAL', alamat: '', utama: true }], pengantar: ['Ben', 'Gono'] },
  pengingat: { nyala: { bon: true, janji: true, kantong: true, opname: true, cadangan: true, pajak: true }, ke: { bon: ['Owner'], janji: ['Owner', 'Ben'], kantong: ['Ben'], opname: ['Owner'], cadangan: ['Owner'], pajak: ['Owner'] },
    hariBon: 3, hariJanji: 1, hariKantong: 7, hariOpname: 2, hariCadangan: 0, hariPajak: 3, tundaHari: 2, maksTunda: 2, opnameTiap: 14 },
};
const ssSalin = (x) => JSON.parse(JSON.stringify(x));
/** Setelan layar `id` (perangkat | peran | cadangan | lokasi | pengingat): dokumen owner ditimpakan ke bawaan, kolom demi kolom (bawaan mengisi yang belum diatur). */
export function ssAtur(id) {
  const B = ssSalin(SS_ATUR_BAWAAN[id]); const d = cacheMentah('aturan').find((x) => String(x.id) === id) || null; if (!d) return B;
  Object.keys(B).forEach((k) => {
    if (d[k] === undefined || d[k] === null) return;
    if (k === 'hak' || k === 'nyala' || k === 'ke') { Object.keys(d[k] || {}).forEach((sub) => { B[k][sub] = (k === 'hak' ? Object.assign({}, B[k][sub] || {}, d[k][sub] || {}) : d[k][sub]); }); }
    else B[k] = d[k];
  });
  return B;
}
/** Simpan setelan satu layar; ditolak menyebut sebabnya (nama kosong, angka di luar batas, lokasi utama hilang, dst.). */
export function susunAturSistem(id, isi, w) {
  const A = ssAtur(id); const o = {}; const nama = (arr, maks) => (Array.isArray(arr) ? arr : []).map((x) => String(x == null ? '' : x).trim()).filter(Boolean).slice(0, maks || 20);
  const angka = (k, min, maks, satuan) => { const n = ssAngka(isi[k] !== undefined ? isi[k] : A[k], min, maks); if (n === null) return k + ' harus ' + min + '–' + maks + (satuan ? ' ' + satuan : ''); o[k] = Math.round(n); return ''; };
  let tolak = '';
  if (id === 'perangkat') { tolak = angka('batasAntre', 1, 600, 'menit') || angka('batasDenyut', 1, 600, 'menit'); o.pemegang = nama(isi.pemegang !== undefined ? isi.pemegang : A.pemegang); if (!tolak && !o.pemegang.some((x) => x.toLowerCase() === 'owner')) tolak = 'Owner tidak bisa dihapus dari daftar pencatat'; }
  else if (id === 'peran') { tolak = angka('batasSekaligus', 0, 50000000, 'rupiah') || angka('jatahBen', 0, 100, '%'); o.hak = ssSalin(A.hak); o.jejak = (A.jejak || []).slice(0, 40);
    const h = isi.hak || {}; Object.keys(h).forEach((p) => { if (p === 'owner' || !SS_HAK_BAWAAN[p]) { tolak = tolak || 'Hak owner tidak diubah — owner selalu boleh semuanya'; return; } Object.keys(h[p]).forEach((t) => { if (SS_NILAI_HAK.indexOf(h[p][t]) < 0 || !SS_TINDAKAN.some((x) => x.id === t)) { tolak = tolak || 'Nilai hak tidak dikenal'; return; } o.hak[p][t] = h[p][t]; }); }); }
  else if (id === 'cadangan') tolak = angka('simpanHari', 1, 365, 'hari') || angka('ambangKuota', 10, 100, '%') || angka('cadanganTiap', 1, 30, 'hari');
  else if (id === 'lokasi') { const daftar = (Array.isArray(isi.daftar) ? isi.daftar : A.daftar).map((l, i) => ({ id: String(l.id || ('lk' + (i + 1))).trim(), nama: String(l.nama || '').trim(), alamat: String(l.alamat || '').trim().slice(0, 80), utama: !!l.utama }));
    if (!daftar.length) tolak = 'Minimal satu lokasi'; else if (daftar.some((l) => !l.nama)) tolak = 'Ada lokasi yang belum bernama — beri nama atau hapus dulu'; else if (new Set(daftar.map((l) => l.id)).size !== daftar.length) tolak = 'Dua lokasi memakai kode yang sama';
    else if (daftar.filter((l) => l.utama).length !== 1) tolak = 'Harus ada tepat satu lokasi utama';
    else { const hilang = A.daftar.filter((l) => !daftar.some((x) => x.id === l.id)); const isi3 = ssStokLokasi(); const perangkat = cacheMentah('perangkat');
      hilang.forEach((l) => { if (tolak) return; const kg = Object.keys(isi3).reduce((a, m) => a + (isi3[m][l.id] || 0), 0); if (kg > 0.05) tolak = 'Masih ada ' + ANGKA(kg) + ' kg stok di ' + l.nama + ' — pindahkan dulu'; else if (perangkat.some((p) => p.lokasi === l.id)) tolak = perangkat.filter((p) => p.lokasi === l.id).map((p) => p.nama || p.id).join(', ') + ' masih mencatat di ' + l.nama; }); }
    o.daftar = daftar; o.pengantar = nama(isi.pengantar !== undefined ? isi.pengantar : A.pengantar); }
  else if (id === 'pengingat') { tolak = angka('hariBon', 0, 60, 'hari') || angka('hariJanji', 0, 60, 'hari') || angka('hariKantong', 0, 90, 'hari') || angka('hariOpname', 0, 60, 'hari') || angka('hariCadangan', 0, 60, 'hari') || angka('hariPajak', 0, 14, 'hari') || angka('tundaHari', 1, 30, 'hari') || angka('maksTunda', 0, 10, 'kali') || angka('opnameTiap', 1, 90, 'hari');
    o.nyala = Object.assign({}, A.nyala, isi.nyala || {}); o.ke = Object.assign({}, A.ke); Object.keys(isi.ke || {}).forEach((j) => { o.ke[j] = nama(isi.ke[j], 4); }); SS_JENIS_PENGINGAT.forEach((j) => { if (!tolak && o.nyala[j.id] && !(o.ke[j.id] || []).length) tolak = 'Minimal satu orang yang diingatkan untuk ' + j.nama.toLowerCase(); }); }
  else return { tolak: 'Setelan tidak dikenal' };
  if (tolak) return { tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({ id, tanggal: w.tanggal, jam: w.jam }, o) }], patch: { kabar: 'Setelan tersimpan — langsung berlaku', kabarAwas: false } };
}

// ---------- SS1 · Perangkat & antrean kirim ----------
export const SS_NAMA_KOLEKSI = { penjualan: 'Nota', piutangMutasi: 'Buku bon', batchMasuk: 'Barang masuk', produksiKemasan: 'Adukan', penyesuaianStok: 'Cocokkan beras', penyesuaianKemasan: 'Cocokkan kemasan', stokBahanKemasan: 'Kantong', stokBahanLiteran: 'Kantong literan', retur: 'Retur', karantina: 'Karantina',
  pengeluaranHarian: 'Belanja harian', tutupHari: 'Tutup hari', pesanan: 'Pesanan', pelangganCatatan: 'Kartu pelanggan', thrPelanggan: 'THR', tagihPelanggan: 'Tagihan', pelangganTitip: 'Titipan', wadahLiteran: 'Wadah literan', aturanToko: 'Setelan', bukuHapus: 'Buku hapus', cadanganCatatan: 'Cadangan', pengingat: 'Pengingat', persetujuan: 'Persetujuan', pindahStok: 'Pindah stok',
  utangPemasokMutasi: 'Bon pemasok', kasbonMutasi: 'Kasbon', katalogHargaKarung: 'Harga karung', katalogHargaKemasan: 'Harga kemasan', katalogHargaLiteran: 'Harga literan', setoranKas: 'Setoran kas', amplopLaba: 'Amplop laba', modalOwner: 'Modal owner', utangOwnerMutasi: 'Utang ke owner', tembusanStok: 'Tembusan stok', pemasokCatatan: 'Kartu pemasok', biayaBulanan: 'Biaya bulanan' };
export const ssNamaKoleksi = (n) => SS_NAMA_KOLEKSI[n] || n || 'catatan';
/** Kartu perangkat dari denyut (perangkatStatus) + antrean perangkat INI dari Firestore (hasPendingWrites). idIni = id perangkat ini. */
export function ssPerangkat(kini, antre, idIni) {
  const A = ssAtur('perangkat'); const t = kini.getTime(); const iso = hariIniIso(kini);
  const daftar = cacheMentah('perangkat').map((d) => { const pada = d.pada ? new Date(d.pada) : null; const menit = pada && isFinite(pada.getTime()) ? Math.max(0, Math.round((t - pada.getTime()) / 60000)) : null;
    return { id: String(d.id), nama: d.nama || '(belum dinamai)', dinamai: !!d.nama, aplikasi: d.aplikasi === 'baru' ? 'sistem baru' : d.aplikasi === 'kasir' ? 'kasir' : 'sistem lama', akun: d.akun || '', pada: d.pada || '', menitLalu: menit,
      hidup: menit !== null && menit <= A.batasDenyut, hariIni: !!pada && hariIniIso(pada) === iso, antrean: Number(d.antrean) || 0, pemegang: d.pemegang || '', lokasi: d.lokasi || '', ini: String(d.id) === String(idIni),
      denyutTeks: menit === null ? 'belum pernah berdenyut' : menit === 0 ? 'berdenyut barusan' : menit < 60 ? 'denyut ' + menit + ' menit lalu' : menit < 1440 ? 'denyut ' + Math.round(menit / 60) + ' jam lalu' : 'denyut ' + Math.round(menit / 1440) + ' hari lalu' }; })
    .sort((a, b) => (b.ini ? 1 : 0) - (a.ini ? 1 : 0) || String(b.pada).localeCompare(String(a.pada)));
  const antreIni = (antre || []).map((q) => { const lama = q.pada ? Math.max(0, Math.round((t - new Date(q.pada).getTime()) / 60000)) : null; return Object.assign({}, q, { nama: ssNamaKoleksi(q.koleksi), lama, terlalu: lama !== null && lama > A.batasAntre, jam: q.pada ? jamKini(new Date(q.pada)) : '' }); });
  const lainAntre = daftar.filter((d) => !d.ini).reduce((a, d) => a + d.antrean, 0);
  return { daftar, antre: antreIni, nAntre: antreIni.length, lainAntre, hidup: daftar.filter((d) => d.hidup).length, hariIni: daftar.filter((d) => d.hariIni).length, atur: A,
    ringkas: !daftar.length ? 'Belum ada perangkat yang berdenyut — denyut ditulis begitu perangkat masuk dan tersambung' : daftar.length + ' perangkat pernah menulis · ' + daftar.filter((d) => d.hariIni).length + ' berdenyut hari ini' + (antreIni.length ? ' · ' + antreIni.length + ' catatan perangkat ini belum sampai server' : '') + (lainAntre ? ' · ' + lainAntre + ' menunggu di perangkat lain (menurut denyutnya)' : '') };
}
/** Jejak pencatat: `batas` tulisan terakhir (logAktivitas kedua sistem). sampai = tidak sedang menunggu server di perangkat ini. */
export function ssJejak(kini, antre, saring) {
  const iso = hariIniIso(kini); const tunda = new Set((antre || []).map((q) => q.koleksi + '|' + q.id)); const batas = (KOLEKSI.find((k) => k.nama === 'logAktivitas') || {}).batas || 150;
  const semua = cacheMentah('log').map((l) => { const d = l.pada ? new Date(l.pada) : null; const ada = d && isFinite(d.getTime());
    return { id: String(l.id), pada: l.pada || '', tanggal: ada ? hariIniIso(d) : '', jam: ada ? jamKini(d) : '', oleh: l.oleh || '—', perangkat: l.perangkat || '—', aksi: l.aksi || 'tulis', koleksi: l.koleksi || '',
      teks: (l.aksi === 'batalkan' ? 'BATAL · ' : l.aksi === 'tandai-koreksi' ? 'KOREKSI · ' : l.aksi === 'hapus' ? 'HAPUS · ' : '') + ssNamaKoleksi(l.koleksi) + (l.ringkas ? ' · ' + l.ringkas : ''), sampai: !tunda.has((l.koleksi || '') + '|' + String(l.idDok || '')) }; }).sort(ssUrutTerbaru);
  const hariIni = semua.filter((l) => l.tanggal === iso); const orang = {}; semua.forEach((l) => { orang[l.oleh] = (orang[l.oleh] || 0) + 1; });
  const tampil = (saring ? semua.filter((l) => l.oleh === saring) : semua).slice(0, 100);
  return { tampil, semua: semua.length, hariIni: hariIni.length, belumSampai: hariIni.filter((l) => !l.sampai).length, terbatas: semua.length >= batas, batas,
    perOrang: Object.keys(orang).sort((a, b) => orang[b] - orang[a]).map((n) => ({ nama: n, n: orang[n], hariIni: hariIni.filter((l) => l.oleh === n).length, belum: hariIni.filter((l) => l.oleh === n && !l.sampai).length })) };
}

// ---------- SS2 · Peran & persetujuan ----------
// Putaran 23c (owner 24 Sep): kisi menampilkan KEBENARAN SERVER. Kisi `sendiri` yang tidak dibuka firestore.rules v3 (akses.js SERVER_BUKA)
// tampil "tertutup server" beserta sebabnya (peta §6) — bukan "boleh sendiri". Nilai kisi tersimpan tetap; yang berubah cuma yang digambar.
export const SS_TERTUTUP_SERVER = { hitungLaci: 'menutup hari menimpa titik kas (angka uang yang sudah tercatat) — owner saja sampai ada alur persetujuan',
  kedatangan: 'kedatangan wajib harga beli, padahal harga beli tidak boleh untuk peran ini — owner saja sampai ada draf kedatangan tanpa harga' };
export const SS_LABEL_TAMPIL = { sendiri: 'boleh sendiri', server: 'tertutup server', owner: 'minta owner', tidak: 'tidak boleh' };
export function ssHakServer(peran, tindakan, nilai) {
  if (peran === 'owner') return { nilai, label: SS_LABEL_TAMPIL[nilai], ket: '' };
  if (nilai === 'sendiri' && (SERVER_BUKA[tindakan] || []).indexOf(peran) < 0) return { nilai: 'server', label: SS_LABEL_TAMPIL.server, ket: SS_TERTUTUP_SERVER[tindakan] || 'server belum membuka tindakan ini untuk peran ini' };
  if (nilai === 'owner') return { nilai, label: SS_LABEL_TAMPIL.owner, ket: 'alur persetujuannya belum ada — sampai itu dibangun, server menutupnya' };
  return { nilai, label: SS_LABEL_TAMPIL[nilai] || nilai, ket: '' };
}
export function ssPeran() {
  const A = ssAtur('peran'); const hak = (peran, t) => (peran === 'owner' ? 'sendiri' : (A.hak[peran] || {})[t] || 'tidak');
  const tampil = (peran, t) => ssHakServer(peran, t, hak(peran, t));
  return { tindakan: SS_TINDAKAN, hak, tampil, batasSekaligus: A.batasSekaligus, jatahBen: A.jatahBen, jejak: (A.jejak || []).slice(0, 12),
    peran: SS_PERAN.map((p) => ({ id: p.id, nama: p.nama, ket: p.id === 'owner' ? 'semua boleh · tidak diubah' : ['sendiri', 'server', 'owner', 'tidak'].map((v) => [SS_TINDAKAN.filter((t) => tampil(p.id, t.id).nilai === v).length, SS_LABEL_TAMPIL[v]]).filter((x) => x[0] > 0).map((x) => x[0] + ' ' + x[1]).join(' · ') })) };
}
/** Ketuk satu hak = memutar sendiri → minta owner → tidak boleh; hak owner tidak diubah. */
export function susunPutarHak(peran, tindakan, w) {
  if (peran === 'owner') return { tolak: 'Hak owner tidak diubah — owner selalu boleh semuanya (dan tidak mengubah haknya sendiri)' };
  const P = ssPeran(); const T = SS_TINDAKAN.find((t) => t.id === tindakan); const R = SS_PERAN.find((p) => p.id === peran); if (!T || !R) return { tolak: 'Tindakan / peran tidak dikenal' };
  const lama = P.hak(peran, tindakan); const baru = SS_NILAI_HAK[(SS_NILAI_HAK.indexOf(lama) + 1) % 3]; const hak = {}; hak[peran] = {}; hak[peran][tindakan] = baru;
  const r = susunAturSistem('peran', { hak, batasSekaligus: P.batasSekaligus, jatahBen: P.jatahBen }, w); if (r.tolak) return r;
  r.dokumen[0].data.jejak = [{ tanggal: w.tanggal, jam: w.jam, teks: R.nama + ' · ' + T.nama + ': ' + SS_LABEL_HAK[lama] + ' → ' + SS_LABEL_HAK[baru] }].concat(P.jejak).slice(0, 40);
  const srv = ssHakServer(peran, tindakan, baru);
  r.patch = { kabar: R.nama + ' kini ' + SS_LABEL_HAK[baru] + ' untuk "' + T.nama + '"' + (srv.nilai === 'server' ? ' — tapi server menutupnya untuk peran ini (' + srv.ket + '), jadi tampil "tertutup server"' : ' — berlaku di tablet begitu tersambung'), kabarAwas: srv.nilai === 'server' }; return r;
}
// ---------- SS2 · AKUN PER ORANG (putaran 23): permintaan akses & akun terdaftar — HANYA owner menulis (rules: aksesAkun tulis = owner, peran ∈ ben/karyawan) ----------
export const SS_KALIMAT_SERVER = 'Server menegakkan: baca & catat baru. Koreksi, hapus, dan \'minta owner\' tertutup sampai alur persetujuan ada.';
export const SS_PERAN_AKUN = SS_PERAN.filter((p) => p.id !== 'owner');   // aksesAkun TIDAK pernah memberi peran owner (owner = email)
export function ssAkun() {
  const akunDok = cacheMentah('aksesAkun'); const terdaftar = (uid) => akunDok.some((a) => String(a.uid || a.id) === uid);
  const minta = cacheMentah('permintaanAkses').map((m) => ({ uid: String(m.uid || m.id), email: String(m.email || ''), nama: String(m.nama || ''), pada: String(m.pada || '') }))
    .filter((m) => !terdaftar(m.uid)).sort((a, b) => b.pada.localeCompare(a.pada));
  const akun = akunDok.map((a) => ({ uid: String(a.uid || a.id), nama: String(a.nama || ''), email: String(a.email || ''), peran: String(a.peran || ''), aktif: a.aktif === true,
    namaPeran: (SS_PERAN.find((p) => p.id === a.peran) || { nama: String(a.peran || '?') }).nama })).sort((x, y) => (Number(y.aktif) - Number(x.aktif)) || x.nama.localeCompare(y.nama));
  return { minta, akun };
}
/** Daftarkan = tulis aksesAkun/{uid} DAN hapus permintaannya — satu batch (tulisDokumen dengan hapus). */
export function susunDaftarkan(uid, peran, w) {
  const m = ssAkun().minta.find((x) => x.uid === String(uid)); if (!m) return { tolak: 'Permintaannya sudah tidak ada' };
  if (!SS_PERAN_AKUN.some((p) => p.id === peran)) return { tolak: 'Pilih perannya dulu (' + SS_PERAN_AKUN.map((p) => p.nama).join(' atau ') + ') — akun tidak pernah bisa jadi owner' };
  const data = { id: m.uid, uid: m.uid, nama: m.nama, email: m.email, peran, aktif: true, dibuatPada: w.kini };
  return { dokumen: [{ koleksi: 'aksesAkun', data }], hapus: [{ koleksi: 'permintaanAkses', id: m.uid }], jejakHapus: 'minta akses disetujui: ' + m.email + ' → ' + peran,
    patch: { akunPilih: {}, kabar: m.nama + ' (' + m.email + ') didaftarkan sebagai ' + (SS_PERAN.find((p) => p.id === peran) || {}).nama + ' — layarnya terbuka sendiri di perangkatnya.', kabarAwas: false } };
}
export function susunTolakAkses(uid, alasan, w) {
  const m = ssAkun().minta.find((x) => x.uid === String(uid)); if (!m) return { tolak: 'Permintaannya sudah tidak ada' };
  if (ssKosong(alasan)) return { tolak: 'Menolak butuh alasan — dicatat di jejak' };
  void w;
  return { dokumen: [], hapus: [{ koleksi: 'permintaanAkses', id: m.uid }], jejakHapus: 'minta akses DITOLAK: ' + m.email + ' — ' + String(alasan).trim().slice(0, 120),
    patch: { alasanAkses: '', kabar: 'Permintaan ' + m.email + ' ditolak dan dicatat di jejak. Orangnya bisa minta lagi.', kabarAwas: false } };
}
/** Ubah peran / aktif. Menonaktifkan & mengaktifkan = dua ketukan; nonaktif langsung mencabut semua pendengar di perangkat orang itu. */
export function susunUbahAkun(uid, ubah, w, yakin) {
  const a = cacheMentah('aksesAkun').find((x) => String(x.uid || x.id) === String(uid)); if (!a) return { tolak: 'Akun itu tidak ditemukan' };
  const U = ubah || {}; void w;
  if (U.peran !== undefined && !SS_PERAN_AKUN.some((p) => p.id === U.peran)) return { tolak: 'Peran tidak dikenal — akun tidak pernah bisa jadi owner' };
  if (U.aktif !== undefined && !yakin) return { tolak: 'Ketuk sekali lagi untuk ' + (U.aktif ? 'mengaktifkan' : 'menonaktifkan') + ' ' + (a.nama || a.email) + (U.aktif ? '' : ' — perangkatnya langsung berhenti membaca data toko'), perluYakin: true };
  const data = Object.assign({}, a, U.peran !== undefined ? { peran: U.peran } : {}, U.aktif !== undefined ? { aktif: U.aktif === true } : {});
  const teks = U.peran !== undefined ? 'kini ' + (SS_PERAN.find((p) => p.id === U.peran) || {}).nama : U.aktif ? 'diaktifkan lagi' : 'DINONAKTIFKAN';
  return { dokumen: [{ koleksi: 'aksesAkun', data }], patch: { yakinAkun: null, kabar: (a.nama || a.email) + ' ' + teks + '.', kabarAwas: U.aktif === false } };
}
/** Permintaan "minta owner" (ditulis tablet/Mac ke koleksi persetujuan): yang menunggu + riwayat keputusan. */
export function ssPersetujuan(kini) {
  const semua = cacheMentah('persetujuan').slice().sort(ssUrutTerbaru); const P = ssPeran();
  const baris = (m) => ({ id: String(m.id), dari: m.dari || '—', peran: m.peran || (String(m.dari || '').toLowerCase() === 'ben' ? 'ben' : 'karyawan'), tindakan: m.tindakan || '', namaTindakan: (SS_TINDAKAN.find((t) => t.id === m.tindakan) || { nama: m.tindakan || 'tindakan' }).nama, modul: (SS_TINDAKAN.find((t) => t.id === m.tindakan) || { modul: '' }).modul,
    teks: m.teks || '', n: Number(m.nominal) || 0, tanggal: m.tanggal || '', jam: m.jam || '', status: m.status || 'menunggu', alasanTolak: m.alasanTolak || '', diputusTanggal: m.diputusTanggal || '',
    saran: m.tindakan && P.hak(m.peran || 'karyawan', m.tindakan) === 'tidak' ? 'Peran ' + (m.dari || 'ini') + ' sebenarnya TIDAK BOLEH untuk ini — kalau sering, ubah haknya' : 'Menurut kisi hak, ini memang minta owner' });
  const menunggu = semua.filter((m) => (m.status || 'menunggu') === 'menunggu').map(baris); const riwayat = semua.filter((m) => m.status && m.status !== 'menunggu').map(baris).slice(0, 20);
  return { menunggu, riwayat, kecil: menunggu.filter((m) => m.n <= P.batasSekaligus).length, batas: P.batasSekaligus, judul: menunggu.length ? menunggu.length + ' permintaan menunggu owner' : 'Tidak ada yang menunggu' + (cacheMentah('persetujuan').length ? '' : ' — permintaan datang dari tablet karyawan (belum ada tabletnya)') };
}
export function susunPutusPersetujuan(id, setuju, alasan, w) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id)); if (!m) return { tolak: 'Permintaannya tidak ditemukan' }; if (m.status && m.status !== 'menunggu') return { tolak: 'Sudah diputus ' + (m.diputusTanggal ? tanggalPendek(m.diputusTanggal) : '') };
  if (!setuju && ssKosong(alasan)) return { tolak: 'Menolak butuh alasan — supaya ' + (m.dari || 'peminta') + ' tahu sebabnya' };
  return { dokumen: [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: setuju ? 'disetujui' : 'ditolak', alasanTolak: setuju ? '' : String(alasan).trim().slice(0, 80), diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini }) }],
    patch: { kabar: setuju ? 'Disetujui — ' + (m.dari || 'peminta') + ' bisa melanjutkan di perangkatnya' : 'Ditolak (' + String(alasan).trim() + ') — ' + (m.dari || 'peminta') + ' dapat kabarnya', kabarAwas: false } };
}
export function susunSetujuiKecil(w) {
  const P = ssPersetujuan(new Date(w.kini)); const kecil = P.menunggu.filter((m) => m.n <= P.batas); if (!kecil.length) return { tolak: P.menunggu.length ? 'Semua permintaan di atas batas "sekaligus" (' + RP(P.batas) + ') — setujui satu per satu' : 'Tidak ada yang menunggu' };
  const dokumen = []; kecil.forEach((m) => { const r = susunPutusPersetujuan(m.id, true, '', w); if (r.dokumen) dokumen.push(r.dokumen[0]); });
  return { dokumen, patch: { kabar: kecil.length + ' permintaan kecil (≤ ' + RP(P.batas) + ') disetujui sekaligus' + (P.menunggu.length - kecil.length ? '; ' + (P.menunggu.length - kecil.length) + ' yang besar masih menunggu' : ''), kabarAwas: false } };
}

// ---------- SS3 · Cadangan & kuota ----------
const SS_TAK_DICADANGKAN = { logAktivitas: 1, perangkatStatus: 1 };   // jejak terbatas & denyut bukan data toko
/** Era tutup buku = tahun saldo pembuka terakhir (eraTutupBuku index.html); null = belum pernah tutup buku. */
export function ssEraTutupBuku() {
  let t = null; ['batch', 'piutang', 'kasbon', 'produksi', 'bahanKemasan', 'bahanLiteran', 'utangPemasok', 'utangOwner', 'amplop'].forEach((c) => cacheMentah(c).forEach((x) => { if (x && x.tutupBuku) { const n = Number(x.tahunDari); if (isFinite(n) && (t === null || n > t)) t = n; } }));
  return t;
}
/** Isi berkas cadangan = bentuk unduhBackup() sistem lama (versi 5): semua koleksi + peta jenis beras + cap era; koleksi baru ikut. */
export function ssBerkasCadangan(kini) {
  const isi = { versi: 5, diunduhPada: kini.toISOString(), sumber: 'sistem baru', eraTutupBuku: ssEraTutupBuku() }; let dokumen = 0, koleksi = 0;
  KOLEKSI.forEach((k) => { if (SS_TAK_DICADANGKAN[k.nama]) return; isi[k.nama] = cacheMentah(k.cache).slice(); dokumen += isi[k.nama].length; koleksi += 1; });
  isi.petaJenisBeras = ambilPetaJenisBeras();
  return { isi, dokumen, koleksi, nama: 'backup-batch-miqbal-' + hariIniIso(kini) + '.json' };
}
export function susunCatatCadangan(b, ukuranBytes, w, perangkat) {
  return { dokumen: [{ koleksi: 'cadanganCatatan', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, perangkat: perangkat || '', nama: b.nama, ukuranKb: Math.round((ukuranBytes || 0) / 1024), dokumen: b.dokumen, koleksi: b.koleksi, jenis: 'manual', ok: true, versi: 5, era: b.isi.eraTutupBuku } }],
    patch: { kabar: 'Berkas ' + b.nama + ' diunduh (' + ANGKA(Math.round((ukuranBytes || 0) / 1024)) + ' KB · ' + ANGKA(b.dokumen) + ' catatan) — simpan juga di tempat lain (Drive / komputer)', kabarAwas: false } };
}
export const SS_LS_BATAS_KB = 5120;   // localStorage peramban ±5 MB (perkiraan umum, bukan angka pasti)
export const SS_LAJU_LS_KB = 62;      // ±62 KB/hari pertumbuhan cadangan lokal SISTEM LAMA (pengukuran 15 Sep 2026) — PERKIRAAN
/** Kalender 14 hari & kesehatan. lokal = { autoTanggal (cap cadangan otomatis sistem lama di perangkat ini), lsKb, usageKb, quotaKb, koleksiSiap, koleksiTotal } — dari peramban. */
export function ssCadangan(kini, lokal, hariPilih) {
  const A = ssAtur('cadangan'); const iso = hariIniIso(kini); const L = lokal || {};
  const catatan = cacheMentah('cadangan').map((c) => ({ id: String(c.id), tanggal: c.tanggal || '', jam: c.jam || '', perangkat: c.perangkat || '', nama: c.nama || '', kb: Number(c.ukuranKb) || 0, dokumen: Number(c.dokumen) || 0, ok: c.ok !== false, jenis: c.jenis || 'manual', sumber: 'sistem baru' }));
  if (L.autoTanggal) catatan.push({ id: 'lama-auto-' + L.autoTanggal, tanggal: L.autoTanggal, jam: '', perangkat: 'HP ini', nama: 'backup otomatis sistem lama', kb: 0, dokumen: 0, ok: true, jenis: 'otomatis', sumber: 'sistem lama' });
  catatan.sort((a, b) => (b.tanggal + b.jam).localeCompare(a.tanggal + a.jam));
  const terakhir = catatan.find((c) => c.ok) || null; const umurHari = terakhir ? ssHariKe(iso) - ssHariKe(terakhir.tanggal) : null;
  const kalender = []; for (let h = 13; h >= 0; h--) { const t = ssTambahHari(iso, -h); const hari = catatan.filter((c) => c.tanggal === t); kalender.push({ iso: t, tgl: String(parseInt(t.slice(8, 10), 10)), nm: ssHariNama(t), n: hari.length, keadaan: hari.some((c) => c.ok) ? 'ok' : hari.length ? 'gagal' : '', ini: t === iso, aktif: t === (hariPilih || iso) }); }
  const pilih = hariPilih || iso; const hariDaftar = catatan.filter((c) => c.tanggal === pilih);
  const lsKb = L.lsKb === undefined || L.lsKb === null ? null : Number(L.lsKb); const pct = lsKb === null ? null : Math.round(lsKb / SS_LS_BATAS_KB * 100);
  const kuota = { adaAngka: lsKb !== null, kb: lsKb, batasKb: SS_LS_BATAS_KB, pct, awas: pct !== null && pct >= A.ambangKuota, sisaHari: lsKb === null ? null : Math.max(0, Math.floor((SS_LS_BATAS_KB - lsKb) / SS_LAJU_LS_KB)),
    teks: lsKb === null ? 'Ukuran simpanan lokal tidak bisa dibaca di peramban ini' : ANGKA(lsKb) + ' KB dari ±' + ANGKA(SS_LS_BATAS_KB) + ' KB simpanan lokal (sistem lama + baru, alamat yang sama) terpakai',
    ket: lsKb === null ? '' : 'bertambah ±' + SS_LAJU_LS_KB + ' KB/hari menurut pengukuran 15 Sep (perkiraan) → ±' + Math.max(0, Math.floor((SS_LS_BATAS_KB - lsKb) / SS_LAJU_LS_KB)) + ' hari lagi penuh',
    awasTeks: pct === null ? '' : pct >= A.ambangKuota ? 'Di atas ambang ' + A.ambangKuota + '% (Atur): kalau penuh, layar SISTEM LAMA berhenti menyegarkan diam-diam — bersihkan cadangan lokalnya dari Setelan sistem lama' : 'Masih di bawah ambang ' + A.ambangKuota + '%' };
  const simpanan = { adaAngka: L.usageKb !== undefined && L.usageKb !== null, kb: Number(L.usageKb) || 0, quotaKb: Number(L.quotaKb) || 0, pct: L.quotaKb ? Math.round((Number(L.usageKb) || 0) / Number(L.quotaKb) * 100) : null };
  const sehat = [['cadangan terakhir', terakhir ? (umurHari === 0 ? 'hari ini' : umurHari + ' hari lalu') : 'belum pernah'], ['dari sistem baru', String(catatan.filter((c) => c.sumber === 'sistem baru' && c.ok).length) + ' berkas'],
    ['otomatis sistem lama (HP ini)', L.autoTanggal ? tanggalPendek(L.autoTanggal) : 'tidak ada capnya'], ['koleksi di simpanan perangkat', L.koleksiTotal ? (L.koleksiSiap || 0) + ' dari ' + L.koleksiTotal : '—']].map((x) => ({ t: x[0], n: x[1] }));
  return { catatan, terakhir, umurHari, telat: umurHari === null || umurHari > A.cadanganTiap, kalender, hariPilih: pilih, hariDaftar, hariJudul: (pilih === iso ? 'Hari ini' : tanggalPendek(pilih)) + ': ' + (hariDaftar.length ? hariDaftar.length + ' cadangan' : 'tidak ada cadangan'), kuota, simpanan, sehat, atur: A,
    ringkas: terakhir ? 'Terakhir ' + tanggalPendek(terakhir.tanggal) + (terakhir.jam ? ' ' + terakhir.jam : '') + ' · ' + terakhir.sumber + (terakhir.kb ? ' · ' + ANGKA(terakhir.kb) + ' KB' : '') + (umurHari > A.cadanganTiap ? ' — sudah ' + umurHari + ' hari, lebih dari jadwal ' + A.cadanganTiap + ' hari' : '') : 'Belum pernah ada cadangan yang tercatat — unduh sekarang',
    era: ssEraTutupBuku() };
}

// ---------- SS4 · Lokasi (fondasi) ----------
export function ssLokasi() { const A = ssAtur('lokasi'); const utama = A.daftar.find((l) => l.utama) || A.daftar[0]; return { daftar: A.daftar, utama, pengantar: A.pengantar }; }
/** Stok per merek per lokasi (kg): buku mesin lama = seluruhnya di lokasi utama; pindah stok menggesernya (keluar −, masuk +). Jumlah semua lokasi = buku. */
export function ssStokLokasi() {
  const { utama } = ssLokasi(); const stokK = hitungStokKarungPerMerk(); const out = {};
  Object.keys(stokK).forEach((m) => { out[m] = {}; out[m][utama.id] = Math.round((stokK[m].sisaKg || 0) * 100) / 100; });
  cacheMentah('pindahStok').forEach((p) => { if (!p.merk || !p.lokasi) return; if (!out[p.merk]) out[p.merk] = {}; const kg = Number(p.kg) || 0; out[p.merk][p.lokasi] = Math.round(((out[p.merk][p.lokasi] || 0) + (p.tipe === 'masuk' ? kg : -kg)) * 100) / 100; });
  return out;
}
export function ssLaporLokasi(kini) {
  const { daftar, utama } = ssLokasi(); const iso = hariIniIso(kini); const bulan = iso.slice(0, 7); const stok = ssStokLokasi(); const stokK = hitungStokKarungPerMerk(); const perangkat = cacheMentah('perangkat');
  const lapor = daftar.map((l) => { const merek = Object.keys(stok).filter((m) => Math.abs(stok[m][l.id] || 0) > 0.05).map((m) => ({ nama: m, kg: stok[m][l.id] })).sort((a, b) => b.kg - a.kg);
    const kg = merek.reduce((a, m) => a + m.kg, 0); const nilai = merek.reduce((a, m) => a + m.kg * ((stokK[m.nama] || {}).hppTerakhirPerKg || 0), 0);
    const nota = ambilPenjualan().filter((p) => (p.lokasi || utama.id) === l.id); const hariIni = nota.filter((p) => p.tanggal === iso); const bulanIni = nota.filter((p) => (p.tanggal || '').slice(0, 7) === bulan);
    return { id: l.id, nama: l.nama, utama: l.utama, alamat: l.alamat, kg, nilai, merek, omzetHari: hariIni.reduce((a, p) => a + (p.hargaTotal || 0), 0), notaHari: new Set(hariIni.map((p) => p.grupNota || p.trxId || p.id)).size, omzetBulan: bulanIni.reduce((a, p) => a + (p.hargaTotal || 0), 0),
      perangkat: perangkat.filter((p) => (p.lokasi || (l.utama ? '' : null)) === l.id || (l.utama && !p.lokasi)).map((p) => p.nama || p.id), kosong: !merek.length && !nota.length }; });
  return { lapor, utama, ket: daftar.length > 1 ? 'Nota & catatan membawa lokasi perangkat yang mencatatnya; catatan lama tanpa lokasi dihitung di lokasi utama (' + utama.nama + ').' : 'Baru satu lokasi — pindah stok & saringan lokasi hidup begitu ada lokasi kedua (tambahkan di Atur).' };
}
export function susunPindahStok(merk, dari, ke, kg, pengantar, w) {
  const { daftar, pengantar: P } = ssLokasi(); const D = daftar.find((l) => l.id === dari), K = daftar.find((l) => l.id === ke);
  if (daftar.length < 2) return { tolak: 'Belum ada lokasi lain — tambahkan di Atur dulu' }; if (!merk) return { tolak: 'Pilih mereknya' }; if (!D || !K) return { tolak: 'Lokasi asal / tujuan tidak dikenal' }; if (dari === ke) return { tolak: 'Asal dan tujuan sama' };
  const n = ssAngka(kg, 0.01, 1000000); if (n === null) return { tolak: 'Ketik berapa kg yang dipindah' };
  const ada = (ssStokLokasi()[merk] || {})[dari] || 0; if (n > ada + 0.005) return { tolak: 'Cuma ada ' + ANGKA(ada) + ' kg ' + merk + ' di ' + D.nama };
  if (ssKosong(pengantar) || P.indexOf(String(pengantar).trim()) < 0) return { tolak: 'Siapa yang mengantar? (pilih dari daftar pengantar)' };
  const id = w.idUnik(); const dasar = { pasangan: id, dari, ke, merk, kg: Math.round(n * 100) / 100, pengantar: String(pengantar).trim(), tanggal: w.tanggal, jam: w.jam };
  return { dokumen: [{ koleksi: 'pindahStok', data: Object.assign({ id, tipe: 'keluar', lokasi: dari }, dasar) }, { koleksi: 'pindahStok', data: Object.assign({ id: id + 1, tipe: 'masuk', lokasi: ke }, dasar) }],
    patch: { kabar: ANGKA(n) + ' kg ' + merk + ' pindah ' + D.nama + ' → ' + K.nama + ' (diantar ' + String(pengantar).trim() + '). Bukan penjualan: buku toko & modal tetap.', kabarAwas: false } };
}
export function susunJadikanUtama(id, w) {
  const { daftar, pengantar } = ssLokasi(); const L = daftar.find((l) => l.id === id); if (!L) return { tolak: 'Lokasi tidak dikenal' }; if (L.utama) return { tolak: L.nama + ' sudah lokasi utama' };
  const r = susunAturSistem('lokasi', { daftar: daftar.map((l) => Object.assign({}, l, { utama: l.id === id })), pengantar }, w); if (r.dokumen) r.patch = { kabar: L.nama + ' jadi lokasi utama — catatan tanpa lokasi dihitung di sini', kabarAwas: false }; return r;
}

// ---------- SS5 · Pengingat ----------
// putaran 17: tempo bon per pemasok = kartu pemasok > tempo umum (aturanToko/catatStok) > tidak diramal — satu kebenaran dengan layar Harga & Pemasok → Bon (tempoPemasok).
/** Sumber pengingat dari data: bon pemasok, janji bayar, kantong menipis (laju pakai 14 hari), opname rutin, cadangan berkas. */
export function ssSumberPengingat(kini, lokal) {
  const iso = hariIniIso(kini); const A = ssAtur('pengingat'); const out = []; let bonTanpaTanggal = 0;
  hitungUtangPemasok().forEach((px) => { const T = tempoPemasok(px.pemasok); (px.bon || []).forEach((b) => { if (!b.tanggal || !(T.hari > 0)) { bonTanpaTanggal += 1; return; } out.push({ id: 'bon|' + b.id, jenis: 'bon', kunci: b.id, teks: 'Bon ' + px.pemasok + ' jatuh tempo', siapa: px.pemasok, jatuh: ssTambahHari(b.tanggal, T.hari), n: b.sisa, ket: 'bon ' + tanggalPendek(b.tanggal) + ' · ' + T.teks }); }); });
  semuaBon(kini).forEach((b) => { if (b.sisa <= 0 || !b.tagih || !b.tagih.janji || (b.status !== 'menunggu' && b.status !== 'janjiLewat')) return; out.push({ id: 'janji|' + b.kunci + '|' + b.tagih.janji, jenis: 'janji', kunci: b.kunci, teks: b.nama + ' janji bayar', siapa: b.nama, jatuh: b.tagih.janji, n: b.sisa, ket: 'ditagih ' + tanggalPendek(b.tagih.tanggal) + ' · sisa bon ' + RP(b.sisa) }); });
  const bahan = hitungStokBahanKemasan(); const mulai = ssTambahHari(iso, -14); const pakai = {}; ambilBahanKemasan().forEach((x) => { if (x.tipe === 'pakai' && (x.tanggal || '') >= mulai) pakai[x.jenis] = (pakai[x.jenis] || 0) + (Number(x.jumlah) || 0); });
  Object.keys(bahan).forEach((j) => { const laju = (pakai[j] || 0) / 14; if (!(laju > 0)) return; const sisa = Math.max(0, bahan[j].sisaPcs || 0); const hari = Math.floor(sisa / laju); const jatuh = ssTambahHari(iso, hari);
    out.push({ id: 'kantong|' + j + '|' + jatuh.slice(0, 7), jenis: 'kantong', kunci: j, teks: (LABEL_BAHAN_KEMASAN[j] || j) + ' cukup ' + hari + ' hari', siapa: 'kantong', jatuh, n: 0, ket: ANGKA(sisa) + ' pcs · terpakai ±' + ANGKA(Math.round(laju * 7)) + ' pcs/minggu' }); });
  let opnameAkhir = ''; ambilPenyesuaianStok().concat(ambilPenyesuaianKemasan()).forEach((x) => { if (x.dariRework) return; if ((x.tanggal || '') > opnameAkhir) opnameAkhir = x.tanggal; }); ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((x) => { if (x.tipe === 'opname' && (x.tanggal || '') > opnameAkhir) opnameAkhir = x.tanggal; });
  out.push({ id: 'opname|' + (opnameAkhir ? ssTambahHari(opnameAkhir, A.opnameTiap) : iso), jenis: 'opname', kunci: 'stok', teks: opnameAkhir ? 'Opname rutin (terakhir ' + tanggalPendek(opnameAkhir) + ')' : 'Opname pertama — belum pernah dicocokkan', siapa: 'stok', jatuh: opnameAkhir ? ssTambahHari(opnameAkhir, A.opnameTiap) : iso, n: 0, ket: 'tiap ' + A.opnameTiap + ' hari (Atur)' });
  const C = ssAtur('cadangan'); let cadAkhir = (lokal && lokal.autoTanggal) || ''; cacheMentah('cadangan').forEach((c) => { if (c.ok !== false && (c.tanggal || '') > cadAkhir) cadAkhir = c.tanggal; });
  out.push({ id: 'cadangan|' + (cadAkhir ? ssTambahHari(cadAkhir, C.cadanganTiap) : iso), jenis: 'cadangan', kunci: 'cadangan', teks: cadAkhir ? 'Cadangan berkas (terakhir ' + tanggalPendek(cadAkhir) + ')' : 'Belum pernah ada cadangan berkas', siapa: 'cadangan', jatuh: cadAkhir ? ssTambahHari(cadAkhir, C.cadanganTiap) : iso, n: 0, ket: 'tiap ' + C.cadanganTiap + ' hari (Atur cadangan)' });
  // putaran 24: pajak — sumbernya dihitung modul pajak (owner saja) dan diteruskan lewat lokal.pajak: tanggal setor bulan lalu, hanya kalau bulan itu terutang & belum disetor
  (lokal && Array.isArray(lokal.pajak) ? lokal.pajak : []).forEach((p) => { if (p && p.jenis === 'pajak' && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  out.bonTanpaTanggal = bonTanpaTanggal; return out;
}
/** Semua pengingat + keadaannya (selesai / ditunda / WA hari ini) menurut aturan owner; kalender −3 … +10 hari. */
export function ssPengingat(kini, lokal, hariKe) {
  const iso = hariIniIso(kini); const A = ssAtur('pengingat'); const keadaan = {}; cacheMentah('pengingat').forEach((k) => { keadaan[String(k.id)] = k; }); const H = hariKe === undefined || hariKe === null ? 0 : Number(hariKe);
  const sumber = ssSumberPengingat(kini, lokal).map((p) => { const k = keadaan[p.id] || {}; const tunda = Number(k.tundaHari) || 0; const sisa = ssHariKe(p.jatuh) - ssHariKe(iso) + tunda; const jk = SS_JENIS_PENGINGAT.find((j) => j.id === p.jenis);
    return Object.assign({}, p, { selesai: k.status === 'selesai', catatan: k.catatan || '', tunda, tundaKali: Number(k.tundaKali) || 0, waHari: k.waTanggal === iso, sisa, nyala: A.nyala[p.jenis] !== false, hariSebelum: Number(A[jk.kunci]) || 0, ke: A.ke[p.jenis] || ['Owner'],
      sisaTeks: (sisa < 0 ? 'lewat ' + (-sisa) + ' hari' : sisa === 0 ? 'hari ini' : sisa + ' hari lagi') + (tunda ? ' · ditunda ' + tunda + ' hari' : ''), jatuhEfektif: ssTambahHari(p.jatuh, tunda) }); });
  const aktif = sumber.filter((p) => p.nyala && !p.selesai && p.sisa <= p.hariSebelum).sort((a, b) => a.sisa - b.sisa || b.n - a.n);
  const lewat = aktif.filter((p) => p.sisa < 0), hariIni = aktif.filter((p) => p.sisa === 0), segera = aktif.filter((p) => p.sisa > 0);
  const kalender = []; for (let h = -3; h <= 10; h++) { const t = ssTambahHari(iso, h); const di = sumber.filter((p) => p.nyala && !p.selesai && p.sisa === h); kalender.push({ iso: t, h, tgl: String(parseInt(t.slice(8, 10), 10)), nm: ssHariNama(t), n: di.length, lewat: h < 0 && di.length > 0, ini: h === 0, aktif: h === H }); }
  const hariDaftar = sumber.filter((p) => p.nyala && !p.selesai && p.sisa === H);
  return { sumber, aktif, lewat, hariIni, segera, kalender, hariKe: H, hariDaftar, hariJudul: (H === 0 ? 'Hari ini' : H < 0 ? tanggalPendek(ssTambahHari(iso, H)) + ' (lewat)' : tanggalPendek(ssTambahHari(iso, H))) + ': ' + (hariDaftar.length ? hariDaftar.length + ' pengingat' : 'tidak ada'),
    ringkas: aktif.length ? lewat.length + ' lewat · ' + hariIni.length + ' hari ini · ' + segera.length + ' segera' + (lewat.some((p) => p.jenis === 'bon') ? ' · bon pemasok lewat ' + RP(lewat.filter((p) => p.jenis === 'bon').reduce((a, p) => a + p.n, 0)) : '') : 'Tidak ada pengingat — semua beres',
    aturan: SS_JENIS_PENGINGAT.map((j) => ({ id: j.id, nama: j.nama, nyala: A.nyala[j.id] !== false, hari: Number(A[j.kunci]) || 0, ke: A.ke[j.id] || [], sumber: sumber.filter((p) => p.jenis === j.id && !p.selesai).length, ket: (A.nyala[j.id] !== false ? 'ingatkan ' + (Number(A[j.kunci]) || 0) + ' hari sebelum' : 'mati') + ' · ke ' + (A.ke[j.id] || []).join(' & ') })), atur: A, bonTanpaTanggal: sumber.bonTanpaTanggal || 0 };
}
const ssDokPengingat = (p, w, tambahan) => ({ koleksi: 'pengingat', data: Object.assign({ id: p.id, jenis: p.jenis, kunci: p.kunci, jatuh: p.jatuh, teks: p.teks, tanggal: w.tanggal, jam: w.jam, status: 'tunda', catatan: p.catatan || '', tundaHari: p.tunda || 0, tundaKali: p.tundaKali || 0 }, tambahan) });
export function susunSelesaiPengingat(p, catatan, w) {
  if (!p) return { tolak: 'Pilih pengingatnya' }; if (p.selesai) return { tolak: 'Sudah ditandai selesai' }; if (p.sisa < 0 && ssKosong(catatan)) return { tolak: 'Pengingat yang sudah lewat butuh catatan: apa yang terjadi?' };
  return { dokumen: [ssDokPengingat(p, w, { status: 'selesai', catatan: String(catatan || '').trim().slice(0, 80) })], patch: { kabar: p.jenis === 'bon' ? 'Ditandai selesai — pembayarannya sendiri dicatat di bon pemasok (sistem lama)' : p.jenis === 'janji' ? 'Ditandai selesai — pembayarannya dicatat lewat Pelanggan → Bon' : 'Ditandai selesai', kabarAwas: false } };
}
export function susunTundaPengingat(p, w) {
  const A = ssAtur('pengingat'); if (!p) return { tolak: 'Pilih pengingatnya' }; if (p.selesai) return { tolak: 'Sudah selesai' }; if (p.tundaKali >= A.maksTunda) return { tolak: 'Sudah ditunda ' + p.tundaKali + ' kali — batasnya ' + A.maksTunda + ' (Atur). Selesaikan dengan catatan' };
  const tunda = p.tunda + A.tundaHari; return { dokumen: [ssDokPengingat(p, w, { status: 'tunda', tundaHari: tunda, tundaKali: p.tundaKali + 1 })], patch: { kabar: p.teks + ' ditunda ' + A.tundaHari + ' hari → ' + tanggalPendek(ssTambahHari(p.jatuh, tunda)) + (p.tundaKali + 1 >= A.maksTunda ? ' — ini tundaan terakhir' : ''), kabarAwas: false } };
}
/** WA untuk janji bayar: kalimat tagihan yang sama dengan layar Pelanggan (pesanTagih); kedua kali sehari ditanya dulu. */
export function susunWaPengingat(kini, p, w, yakin) {
  if (!p || p.jenis !== 'janji') return { tolak: 'WA hanya untuk janji bayar pelanggan' }; const pesan = pesanTagih(kini, p.kunci); if (!pesan) return { tolak: 'Bonnya sudah tidak ada' };
  if (p.waHari && !yakin) return { perluYakin: true, tolak: 'Sudah dikirim WA hari ini ke ' + p.siapa + ' — ketuk sekali lagi kalau mau kirim lagi' };
  return { url: pesan.url, dokumen: [ssDokPengingat(p, w, { status: p.selesai ? 'selesai' : 'tunda', waTanggal: w.tanggal })], patch: { kabar: 'WhatsApp dibuka untuk ' + p.siapa + ' · ' + pesan.tujuan, kabarAwas: false } };
}
export function susunSaklarPengingat(jenis, w) {
  const A = ssAtur('pengingat'); const j = SS_JENIS_PENGINGAT.find((x) => x.id === jenis); if (!j) return { tolak: 'Jenis tidak dikenal' }; const nyala = {}; nyala[jenis] = A.nyala[jenis] === false;
  const r = susunAturSistem('pengingat', { nyala }, w); if (r.dokumen) r.patch = { kabar: j.nama + (nyala[jenis] ? ' dinyalakan' : ' dimatikan — yang lewat tetap tercatat, cuma tidak diingatkan'), kabarAwas: false }; return r;
}
export function susunKePengingat(jenis, nama, w) {
  const A = ssAtur('pengingat'); const j = SS_JENIS_PENGINGAT.find((x) => x.id === jenis); if (!j) return { tolak: 'Jenis tidak dikenal' }; const ada = (A.ke[jenis] || []).slice(); const i = ada.indexOf(nama); if (i >= 0) ada.splice(i, 1); else ada.push(nama);
  if (!ada.length) return { tolak: 'Minimal satu orang yang diingatkan' }; const ke = {}; ke[jenis] = ada; const r = susunAturSistem('pengingat', { ke }, w); if (r.dokumen) r.patch = { kabar: j.nama + ' → ' + ada.join(' & '), kabarAwas: false }; return r;
}
export const ssKunciOrang = kunciPelanggan;
