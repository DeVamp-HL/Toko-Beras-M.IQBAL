// LOGIKA layar SISTEM (di bawah Menu → "Toko ini"), tanpa DOM. Desain terkunci owner 19 Sep 2026 (kanvas Sistem, SS1–SS5):
//   SS1 Perangkat & antrean kirim (sensus 61 + 64) · SS2 Peran & persetujuan (62) · SS3 Cadangan & kuota (63, pilihan C)
//   SS4 Lokasi (65, fondasi) · SS5 Pengingat (67, pilihan B + C: aturan + kalender).
// Sumber angka = data toko yang sama dengan sistem lama (perangkatStatus & logAktivitas = koleksi sistem lama); yang BARU:
// aturanToko/{perangkat,peran,cadangan,lokasi,pengingat} (angka & daftar kebijakan owner), cadanganCatatan, pengingat, persetujuan, pindahStok.
// Kejujuran: antrean = catatan yang sungguh belum diakui server (hasPendingWrites), bukan hitungan sendiri; yang tidak bisa dihitung DISEBUT.
// Tidak ada kolom PIN/sandi di mana pun — kunci perangkat diatur di perangkatnya (aturan tetap). KECUALI (putaran T1 langkah 3, owner 16 Nov 2026):
// aturanToko/peran.operator = orang di tablet, PIN-nya tersimpan sebagai PBKDF2 bergaram (tablet-logika.js) — bukan PIN-nya sendiri.
// Nama pembantu diprefiks `ss` karena bundel uji jsc satu lingkup.
import { hitungUtangPemasok, hitungStokBahanKemasan } from '../mesin/beku.js';
import { LABEL_BAHAN_KEMASAN, kunciPelanggan, uangKembaliRetur } from '../mesin/pembantu.js';
import { KOLEKSI } from '../data/koleksi.js';
import { ambilPenjualan, ambilRetur, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, ambilPetaJenisBeras, cacheMentah, eraBuku, ingatStokKarung } from '../data/toko.js';
import { tempoPemasok, petaGulir, gulirBon } from './bon-pemasok-logika.js';
import { kantongLama } from './wadah-jual-logika.js';
import { RP, ANGKA, hariIniIso, jamKini, tanggalPendek } from '../inti/format.js';
import { semuaBon, pesanTagih, pnHariTagih } from './bon-logika.js';
import { SERVER_BUKA, PERAN_BUKAN_OWNER } from '../data/akses.js';
import { HB_TEMPAT } from '../data/hemat-baca.js';
// owner 7 Okt (JS2-C): bawaan batas nego satu sumber
import { NG_BAWAAN, ngPeriksaMinta } from './nego-logika.js';
// B1 (owner 16 Nov 2026): usul harga pelanggan usaha
import { htTeksUbah, htPasangUsul, HT_TINDAKAN } from './harga-tingkat-logika.js';
// B2 (owner 17 Nov 2026): permintaan persetujuan bon (batas kredit terlewati) di papan Persetujuan
import { fkTeksMinta, FK_TINDAKAN, fkSemua } from './faktur-logika.js';
// owner 21 Nov 2026: titipan uang keluar & pesan dari tablet — papan ini memutusnya lewat pintu yang SAMA dengan Uang (tpSusunPutus menulis uangnya)
import { tpSusunPutus, tpTeks, TP_TINDAKAN, TP_PESAN, TP_KABAR } from './titipan-logika.js';
// paket Banding pemasok (owner 26 Nov 2026): pengingat mingguan (harga ≥ N pemasok) & bulanan (banding bulan lalu) + usul harga tawaran / acuan dari tablet
// (rules v21) — modul DAUN banding-catat-logika (tanpa mesin laporan)
import { bcSumberPengingat, bcPasangUsul, bcTeksUsul, BC_TINDAKAN } from './banding-catat-logika.js';
// owner 26 Nov 2026: lokasi langit & cuaca gerbang (atur Perangkat)
import { lgLokasiSah } from '../inti/langit-logika.js';

export const ssHariKe = (iso) => Math.round(Date.UTC(+String(iso).slice(0, 4), +String(iso).slice(5, 7) - 1, +String(iso).slice(8, 10)) / 86400000);
export const ssTambahHari = (iso, n) => new Date((ssHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
const ssKosong = (v) => !String(v == null ? '' : v).trim();
const ssAngka = (v, min, maks) => { const n = Number(String(v == null ? '' : v).replace(',', '.')); return isFinite(n) && n >= min && n <= maks ? n : null; };
const ssUrutTerbaru = (a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || ''));
const ssHariNama = (iso) => ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'][new Date(iso + 'T00:00:00Z').getUTCDay()];

// ---------- tindakan berpintu izin & peran (SS2) — dari kanvas-kanvas yang sudah dikunci ----------
export const SS_TINDAKAN = [['jualTunai', 'Jual tunai & kembalian', 'Jual'], ['jualBon', 'Jual dengan bon (pelanggan lama)', 'Jual'], ['nego', 'Nego di bawah jatah margin', 'Jual'], ['terimaBon', 'Terima pembayaran bon', 'Uang'],
  ['hitungLaci', 'Hitung & rapikan laci', 'Uang'], ['uangKeluar', 'Catat uang keluar dari laci', 'Uang'], ['adukan', 'Catat adukan (bongkar kemasan)', 'Stok'], ['kedatangan', 'Catat barang masuk (harga nota supir, jadi bon pemasok)', 'Stok'],
  ['hargaBeli', 'Isi harga beli / modal', 'Stok'], ['koreksi', 'Koreksi nota yang sudah tersimpan', 'Jual'], ['hapus', 'Hapus catatan', 'Semua'], ['pelangganBaru', 'Daftarkan pelanggan baru', 'Pelanggan'], ['hargaPelanggan', 'Atur harga pelanggan usaha (tingkat & harga khusus)', 'Pelanggan'], ['atur', 'Ubah setelan (Atur)', 'Sistem'],
  ['isiUlang', 'Isi ulang & cek wadah literan', 'Stok'],
  ['antar', 'Bikin surat jalan & antar (bersama notanya)', 'Jual'], ['terimaAntar', 'Tandai barang antaran diterima / gagal', 'Jual'],
  ['pesanan', 'Bikin & ubah pesanan, PO, jadwal rutin & uang muka', 'Jual']].map((t) => ({ id: t[0], nama: t[1], modul: t[2] }));   // B3 (owner 18 Nov 2026) — rules v10   // putaran 39 (owner 29 Sep): karyawan menuang & mengecek wadah — rules v5
export const SS_PERAN = [['owner', 'Owner'], ['ben', 'Penjaga laci'], ['karyawan', 'Karyawan (giliran)']].map((p) => ({ id: p[0], nama: p[1] }));
export const SS_NILAI_HAK = ['sendiri', 'owner', 'tidak'];
export const SS_LABEL_HAK = { sendiri: 'boleh sendiri', owner: 'minta owner', tidak: 'tidak boleh' };
const SS_HAK_BAWAAN = { ben: { jualTunai: 'sendiri', jualBon: 'sendiri', nego: 'owner', terimaBon: 'sendiri', hitungLaci: 'sendiri', uangKeluar: 'owner', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'owner', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak', isiUlang: 'sendiri', hargaPelanggan: 'owner', antar: 'sendiri', terimaAntar: 'sendiri', pesanan: 'sendiri' },
  karyawan: { jualTunai: 'sendiri', jualBon: 'owner', nego: 'tidak', terimaBon: 'sendiri', hitungLaci: 'tidak', uangKeluar: 'tidak', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'tidak', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak', isiUlang: 'sendiri', hargaPelanggan: 'tidak', antar: 'tidak', terimaAntar: 'sendiri', pesanan: 'tidak' } };   // B4 (owner 18 Nov 2026): pesanan, PO, jadwal rutin = owner + Ben — rules v11
// jenis yang hari-sebelumnya dibawa sumbernya sendiri (bukan angka Atur pengingat)
export const SS_HARI_DI_SUMBER = { patuh: 'hari sebelum diatur per butir (Laporan › Pajak › Kalender)', kemasan: 'tanda dekat diatur di Jual › Label & kartu › Atur label' };
export const SS_JENIS_PENGINGAT = [['bon', 'Bon pemasok jatuh tempo', 'hariBon'], ['janji', 'Janji bayar pelanggan', 'hariJanji'], ['kantong', 'Kantong menipis', 'hariKantong'], ['opname', 'Opname rutin', 'hariOpname'], ['cadangan', 'Cadangan berkas', 'hariCadangan'], ['pajak', 'Setoran PPh final bulan lalu', 'hariPajak'], ['faktur', 'Faktur pelanggan jatuh tempo', 'hariFaktur'], ['gudang', 'Cek mingguan timbangan & gudang', 'hariGudang'], ['kuartal', 'Target kuartal belum diisi', 'hariKuartal'], ['tinjauan', 'Tinjauan bulanan belum ditulis', 'hariTinjauan'],
  // owner 26 Nov 2026 (kas & rekening, bon eceran): setor ke bank · cocok saldo rekening akhir bulan · hari tagih bon pelanggan
  ['setor', 'Setor ke bank (brankas lewat batas)', 'hariSetor'], ['rekening', 'Cocok saldo rekening usaha akhir bulan', 'hariRekening'], ['tagih', 'Hari tagih bon pelanggan', 'hariTagih'],
  // owner 26 Nov 2026 (stok minus, label & kepatuhan — "pasang notifikasi"): kalender kepatuhan (hari sebelum PER BUTIR, Laporan › Pajak › Kalender) · kemasan dekat
  // "baik dipakai sebelum" (tanda dekat = setelan label) · buku stok minus. Sumbernya diteruskan app.js lewat lokal.patuh / lokal.gudang (pola lokal.pajak).
  ['patuh', 'Kalender kepatuhan', 'hariPatuh'], ['kemasan', 'Kemasan dekat "baik dipakai sebelum"', 'hariKemasan'], ['minus', 'Buku stok minus', 'hariMinus'],
  // paket Banding pemasok (owner 26 Nov 2026): harga dari N pemasok tiap minggu · banding bulan lalu — hari, tanggal & N diatur di Harga & Pemasok › Banding › Atur
  ['banding', 'Harga dari N pemasok minggu ini', 'hariBanding'], ['bandingBulan', 'Banding pemasok bulan lalu', 'hariBandingBulan'],
  // paket P3 (owner 27 Nov 2026, sensus A4): PERINGATAN UANG — biaya lewat anggaran · susut merah · modal per kg lewat batas · harga di bawah minimum, + usulan Claude
  // (owner: "boleh tambahkan asal masuk akal") untung per kg di bawah target · kas di bawah ambang. Sumbernya peringatan-logika (pwSumberPengingat) lewat lokal.peringatan, owner saja.
  ['anggaran', 'Biaya lewat anggaran', 'hariAnggaran'], ['susut', 'Susut beras merah', 'hariSusut'], ['hpp', 'Modal per kg lewat batas', 'hariHpp'], ['harga', 'Harga di bawah minimum', 'hariHarga'],
  ['untungKg', 'Untung per kg di bawah target', 'hariUntungKg'], ['kas', 'Kas di bawah ambang minimum', 'hariKas'],
  // paket P5 (owner 27 Nov 2026, A92): opname kejutan — tanggal & merek diundi (stok-pantau-logika), sumbernya diteruskan app.js lewat lokal.gudang HANYA di perangkat owner
  ['kejutan', 'Opname kejutan (diundi)', 'hariKejutan']].map((j) => ({ id: j[0], nama: j[1], kunci: j[2] }));   // gudang: paket KPI laba (owner 24 Nov 2026, butir 14)
// paket P6 (owner 27 Nov 2026, A119 + A82): selisih laci BERULANG (alarm, angka di Uang › Tutup hari › Atur) · selisih yang "dicari besok" belum dijelaskan — dihitung
// laci-logika (lhSumberPengingat, OWNER saja: angka uang) dan diteruskan app.js lewat lokal.peringatan. Baris sendiri supaya daftar di atas tidak bergeser.
SS_JENIS_PENGINGAT.push({ id: 'laci', nama: 'Selisih laci berulang', kunci: 'hariLaci' }, { id: 'jelaskan', nama: 'Selisih laci belum dijelaskan', kunci: 'hariJelaskan' });
export const SS_JENIS_LACI = ['laci', 'jelaskan'];   // = jenis lhSumberPengingat laci-logika
export const SS_PENERIMA = ['Owner', 'Ben'];

// ---------- ATUR SENDIRI — angka & daftar kebijakan owner, satu dokumen aturanToko per layar; bawaan = angka desain terkunci ----------
export const SS_ATUR_BAWAAN = {
  perangkat: { batasAntre: 30, batasDenyut: 15, pemegang: ['Owner', 'Ben'], cuaca: null },   // cuaca: lokasi langit gerbang { nama, lat, lon } (owner 26 Nov 2026)
  // owner 7 Okt (JS2-C): jatah nego per peran (% margin) + per akun (uid → %, kosong = ikut peran), siapa boleh di bawah modal ('owner' | peran | 'uid:…'), langkah batas
  peran: { hak: SS_HAK_BAWAAN, batasSekaligus: 300000, jatahBen: NG_BAWAAN.ben, jatahKaryawan: NG_BAWAAN.karyawan, jatahAkun: {}, bawahModal: NG_BAWAAN.bawahModal.slice(), langkahNego: NG_BAWAAN.langkah, jejak: [],
    operator: {}, ringkasOrang: '', intipDetik: 60 },   // owner 22 Nov 2026 (sidik jari Tahap A): intip uang tertutup sendiri sesudah intipDetik tidak disentuh · putaran T1 langkah 3 (owner 16 Nov): orang di tablet — tablet-logika.js · owner 21 Nov: orang yang membuka Ringkas hari ini (kode orang, '' = mati)
  cadangan: { simpanHari: 30, ambangKuota: 80, cadanganTiap: 7 },
  lokasi: { daftar: [{ id: 'toko', nama: 'Toko M.IQBAL', alamat: '', utama: true }], pengantar: ['Ben'] },
  pengingat: { nyala: { anggaran: true, susut: true, hpp: true, harga: true, untungKg: true, kas: true, bon: true, janji: true, kantong: true, opname: true, cadangan: true, pajak: true, faktur: true, gudang: true, setor: true, rekening: true, tagih: true, kuartal: true, tinjauan: true, banding: true, bandingBulan: true, patuh: true, kemasan: true, minus: true, kejutan: true }, ke: { anggaran: ['Owner'], susut: ['Owner'], hpp: ['Owner'], harga: ['Owner'], untungKg: ['Owner'], kas: ['Owner'], bon: ['Owner'], janji: ['Owner', 'Ben'], kantong: ['Ben'], opname: ['Owner'], cadangan: ['Owner'], pajak: ['Owner'], faktur: ['Owner', 'Ben'], gudang: ['Owner', 'Ben'], setor: ['Owner'], rekening: ['Owner'], tagih: ['Owner', 'Ben'], kuartal: ['Owner'], tinjauan: ['Owner'], banding: ['Owner', 'Ben'], bandingBulan: ['Owner'], patuh: ['Owner', 'Ben'], kemasan: ['Owner', 'Ben'], minus: ['Owner'], kejutan: ['Owner'] },
    hariAnggaran: 0, hariSusut: 0, hariHpp: 0, hariHarga: 0, hariUntungKg: 0, hariKas: 0, hariBon: 3, hariJanji: 1, hariKantong: 7, hariOpname: 2, hariCadangan: 0, hariPajak: 3, hariFaktur: 3, hariGudang: 0, hariSetor: 0, hariRekening: 1, hariTagih: 0, hariKuartal: 7, hariTinjauan: 0, hariBanding: 0, hariBandingBulan: 0, hariPatuh: 0, hariKemasan: 0, hariMinus: 0, hariKejutan: 0, tundaHari: 2, maksTunda: 2, opnameTiap: 14, gudangTiap: 7 },
};
// paket P6: bawaan dua jenis pengingat selisih laci — menyala, ke Owner, tanpa hari sebelum (pola peringatan uang P3)
Object.assign(SS_ATUR_BAWAAN.pengingat.nyala, { laci: true, jelaskan: true }); Object.assign(SS_ATUR_BAWAAN.pengingat.ke, { laci: ['Owner'], jelaskan: ['Owner'] }); Object.assign(SS_ATUR_BAWAAN.pengingat, { hariLaci: 0, hariJelaskan: 0 });
const ssSalin = (x) => JSON.parse(JSON.stringify(x));
// ---------- orang di tablet (putaran T1 langkah 3, owner 16 Nov 2026) — bentuk yang boleh ditulis; diatur lewat tablet-logika.js ----------
export const SS_MAKS_ORANG_TABLET = 12;
/** Peta orang di tablet → bentuk bersih, atau { tolak } bila ada yang tidak sah (tidak dibuang diam-diam). Dokumen peran ditimpa UTUH tiap disimpan:
 *  susunAturSistem('peran') selalu membawa peta ini, jadi memutar hak / mengubah jatah nego tidak menghapus orang di tablet. */
export function ssBersihkanOrangTablet(peta) {
  const out = {}; const ids = Object.keys(peta || {}); const nama = {}; const t = (v) => String(v === undefined || v === null ? '' : v).trim();
  if (ids.length > SS_MAKS_ORANG_TABLET) return { tolak: 'Paling banyak ' + SS_MAKS_ORANG_TABLET + ' orang di tablet' };
  for (let i = 0; i < ids.length; i++) {
    const id = ids[i]; const o = peta[id] || {}; const n = t(o.nama);
    if (!/^o[a-z0-9]{3,24}$/.test(id)) return { tolak: 'Kode orang di tablet tidak sah (' + id + ')' };
    if (n.length < 2 || n.length > 30) return { tolak: 'Nama orang di tablet harus 2–30 huruf' };
    if (nama[n.toLowerCase()]) return { tolak: 'Nama "' + n + '" dua kali di daftar tablet' }; nama[n.toLowerCase()] = 1;
    if (PERAN_BUKAN_OWNER.indexOf(o.peran) < 0) return { tolak: 'Peran ' + n + ' tidak dikenal' };
    if (!/^g[0-9a-f]{32}$/.test(t(o.garam)) || !/^[0-9a-f]{64}$/.test(t(o.acak))) return { tolak: 'PIN ' + n + ' tidak berbentuk sah — atur ulang PIN-nya' };
    const it = Number(o.iterasi); if (!(it >= 10000 && it <= 1000000 && Math.floor(it) === it)) return { tolak: 'Hitungan PIN ' + n + ' tidak sah' };
    out[id] = { nama: n, peran: o.peran, aktif: o.aktif !== false, garam: t(o.garam), acak: t(o.acak), iterasi: it, dibuat: t(o.dibuat), diubah: t(o.diubah) };
  }
  return { peta: out };
}
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
  if (id === 'perangkat') { tolak = angka('batasAntre', 1, 600, 'menit') || angka('batasDenyut', 1, 600, 'menit'); o.pemegang = nama(isi.pemegang !== undefined ? isi.pemegang : A.pemegang); if (!tolak && !o.pemegang.some((x) => x.toLowerCase() === 'owner')) tolak = 'Owner tidak bisa dihapus dari daftar pencatat';
    o.cuaca = lgLokasiSah(isi.cuaca !== undefined ? isi.cuaca : A.cuaca); }   // owner 26 Nov 2026: lokasi langit & cuaca gerbang (null = langit ikut jam saja)
  else if (id === 'peran') { tolak = angka('batasSekaligus', 0, 50000000, 'rupiah') || angka('jatahBen', 0, 100, '%') || angka('jatahKaryawan', 0, 100, '%') || angka('langkahNego', 1, 1000000, 'rupiah') || angka('intipDetik', 15, 600, 'detik'); o.hak = ssSalin(A.hak); o.jejak = (A.jejak || []).slice(0, 40);
    // owner 7 Okt (JS2-C): jatah per akun — kosong = ikut perannya; di bawah modal — kunci yang dikenal saja (owner, peran, uid akun terdaftar)
    const ja = isi.jatahAkun !== undefined ? isi.jatahAkun : A.jatahAkun; o.jatahAkun = {};
    Object.keys(ja || {}).forEach((u) => { if (ssKosong(ja[u])) return; const n = ssAngka(ja[u], 0, 100); if (n === null) tolak = tolak || 'jatah nego per akun harus 0–100 %'; else o.jatahAkun[u] = Math.round(n); });
    const kenal = ['owner'].concat(SS_PERAN_AKUN.map((p) => p.id), cacheMentah('aksesAkun').map((a) => 'uid:' + String(a.uid || a.id)));
    o.bawahModal = (Array.isArray(isi.bawahModal) ? isi.bawahModal : A.bawahModal).map(String).filter((k, i, L) => kenal.indexOf(k) >= 0 && L.indexOf(k) === i);
    const ot = ssBersihkanOrangTablet(isi.operator !== undefined ? isi.operator : A.operator); if (ot.tolak) tolak = tolak || ot.tolak; else o.operator = ot.peta;   // T1-3: dibawa utuh
    // owner 21 Nov 2026: Ringkas hari ini di tablet hanya untuk SATU orang pilihan owner — kode orang yang ada di daftar tablet, atau '' (mati). Dibawa utuh.
    const ro = String(isi.ringkasOrang !== undefined ? isi.ringkasOrang : (A.ringkasOrang || '')).trim(); if (ro && !(o.operator || {})[ro]) tolak = tolak || 'Orang pembuka Ringkas hari ini tidak ada di daftar tablet'; else o.ringkasOrang = ro;
    const h = isi.hak || {}; Object.keys(h).forEach((p) => { if (p === 'owner' || !SS_HAK_BAWAAN[p]) { tolak = tolak || 'Hak owner tidak diubah — owner selalu boleh semuanya'; return; } Object.keys(h[p]).forEach((t) => { if (SS_NILAI_HAK.indexOf(h[p][t]) < 0 || !SS_TINDAKAN.some((x) => x.id === t)) { tolak = tolak || 'Nilai hak tidak dikenal'; return; } o.hak[p][t] = h[p][t]; }); }); }
  else if (id === 'cadangan') tolak = angka('simpanHari', 1, 365, 'hari') || angka('ambangKuota', 10, 100, '%') || angka('cadanganTiap', 1, 30, 'hari');
  else if (id === 'lokasi') { const daftar = (Array.isArray(isi.daftar) ? isi.daftar : A.daftar).map((l, i) => ({ id: String(l.id || ('lk' + (i + 1))).trim(), nama: String(l.nama || '').trim(), alamat: String(l.alamat || '').trim().slice(0, 80), utama: !!l.utama }));
    if (!daftar.length) tolak = 'Minimal satu lokasi'; else if (daftar.some((l) => !l.nama)) tolak = 'Ada lokasi yang belum bernama — beri nama atau hapus dulu'; else if (new Set(daftar.map((l) => l.id)).size !== daftar.length) tolak = 'Dua lokasi memakai kode yang sama';
    else if (daftar.filter((l) => l.utama).length !== 1) tolak = 'Harus ada tepat satu lokasi utama';
    else { const hilang = A.daftar.filter((l) => !daftar.some((x) => x.id === l.id)); const isi3 = ssStokLokasi(); const perangkat = cacheMentah('perangkat');
      hilang.forEach((l) => { if (tolak) return; const kg = Object.keys(isi3).reduce((a, m) => a + (isi3[m][l.id] || 0), 0); if (kg > 0.05) tolak = 'Masih ada ' + ANGKA(kg) + ' kg stok di ' + l.nama + ' — pindahkan dulu'; else if (perangkat.some((p) => p.lokasi === l.id)) tolak = perangkat.filter((p) => p.lokasi === l.id).map((p) => p.nama || p.id).join(', ') + ' masih mencatat di ' + l.nama; }); }
    o.daftar = daftar; o.pengantar = nama(isi.pengantar !== undefined ? isi.pengantar : A.pengantar); }
  else if (id === 'pengingat') { tolak = angka('hariBon', 0, 60, 'hari') || angka('hariJanji', 0, 60, 'hari') || angka('hariKantong', 0, 90, 'hari') || angka('hariOpname', 0, 60, 'hari') || angka('hariCadangan', 0, 60, 'hari') || angka('hariPajak', 0, 14, 'hari') || angka('hariFaktur', 0, 30, 'hari') || angka('hariGudang', 0, 7, 'hari') || angka('hariKuartal', 0, 30, 'hari') || angka('hariTinjauan', 0, 14, 'hari') || angka('hariSetor', 0, 14, 'hari') || angka('hariRekening', 0, 14, 'hari') || angka('hariTagih', 0, 6, 'hari') || angka('hariPatuh', 0, 60, 'hari') || angka('hariKemasan', 0, 60, 'hari') || angka('hariMinus', 0, 7, 'hari') || angka('hariKejutan', 0, 7, 'hari') || angka('tundaHari', 1, 30, 'hari') || angka('maksTunda', 0, 10, 'kali') || angka('opnameTiap', 1, 90, 'hari') || angka('gudangTiap', 1, 30, 'hari');
    tolak = tolak || ['hariAnggaran', 'hariSusut', 'hariHpp', 'hariHarga', 'hariUntungKg', 'hariKas'].map((k) => angka(k, 0, 7, 'hari')).find((x) => x) || '';   // paket P3: jenis peringatan uang
    tolak = tolak || ['hariLaci', 'hariJelaskan'].map((k) => angka(k, 0, 7, 'hari')).find((x) => x) || '';   // paket P6: selisih laci
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
    return { id: String(d.id), nama: d.nama || '(belum dinamai)', dinamai: !!d.nama, aplikasi: d.aplikasi === 'baru' ? 'sistem baru' : d.aplikasi === 'kasir' ? 'kasir' : d.aplikasi === 'darurat' ? 'kasir darurat' : 'sistem lama', akun: d.akun || '', pada: d.pada || '', menitLalu: menit,
      hidup: menit !== null && menit <= A.batasDenyut, hariIni: !!pada && hariIniIso(pada) === iso, antrean: Number(d.antrean) || 0, ditolak: Number(d.gagal) || 0, versi: d.versi || '', pemegang: d.pemegang || '', lokasi: d.lokasi || '', ini: String(d.id) === String(idIni),
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
      teks: (l.lewat ? '[' + String(l.lewat) + '] ' : '') + (l.aksi === 'batalkan' ? 'BATAL · ' : l.aksi === 'tandai-koreksi' ? 'KOREKSI · ' : l.aksi === 'hapus' ? 'HAPUS · ' : '') + ssNamaKoleksi(l.koleksi) + (l.ringkas ? ' · ' + l.ringkas : ''), sampai: !tunda.has((l.koleksi || '') + '|' + String(l.idDok || '')) }; }).sort(ssUrutTerbaru);
  const hariIni = semua.filter((l) => l.tanggal === iso); const orang = {}; semua.forEach((l) => { orang[l.oleh] = (orang[l.oleh] || 0) + 1; });
  const tampil = (saring ? semua.filter((l) => l.oleh === saring) : semua).slice(0, 100);
  return { tampil, semua: semua.length, hariIni: hariIni.length, belumSampai: hariIni.filter((l) => !l.sampai).length, terbatas: semua.length >= batas, batas,
    perOrang: Object.keys(orang).sort((a, b) => orang[b] - orang[a]).map((n) => ({ nama: n, n: orang[n], hariIni: hariIni.filter((l) => l.oleh === n).length, belum: hariIni.filter((l) => l.oleh === n && !l.sampai).length })) };
}

// ---------- SS1 · Hemat baca (owner 7 Okt 2026, siap 2027 — docs/rancangan-hemat-baca.md) ----------
const SS_MODE_HEMAT = { delta: 'dengar ubahan', total: 'baca penuh', penuh: 'dengar penuh' };
/**
 * Panel Menu › Toko ini › Perangkat & antrean › Hemat baca (HB_TEMPAT). K = keadaan hemat perangkat ini (firebase.js hematKeadaan), siap = daftar siap-nyala (hbSiapNyala).
 * Angka baca = PERKIRAAN (catatan yang datang dari server ke perangkat), bukan tagihan — tagihan dibaca di tab Usage Console. Kalimat toko.
 */
export function ssHemat(K, siap) {
  const H = K || {};
  const daftar = (H.koleksi || []).map((x) => ({ k: x.k, nama: ssNamaKoleksi(x.k), mode: x.bacaJalan ? 'sedang dibaca penuh' : SS_MODE_HEMAT[x.mode] || 'menunggu', ok: !!x.terperiksa,
    ket: x.vMati ? 'tab ini berhenti menerima data — muat ulang' : x.galat ? 'galat server: ' + x.galat : x.wajibTotal || (x.terperiksa ? 'cocok dengan server' : x.sebab || 'belum terperiksa'), totalPada: x.totalPada || null }))
    .sort((a, b) => (a.ok ? 1 : 0) - (b.ok ? 1 : 0) || a.nama.localeCompare(b.nama));
  const kapan = daftar.map((x) => x.totalPada).filter((x) => x); const S = siap || [];
  const status = !H.saklar ? 'MATI' : H.nyala ? 'NYALA' : 'NYALA, belum berjalan';
  const kl = H.klaim || null;
  // #111 × Paket C: koleksi yang terperiksa tapi belum dibaca penuh sejak kuota baca terakhir direset (SATU sumber hbBelumLengkap) — keputusan final menunggu;
  // tombolnya ada di panel ini. Sanggahan 7 Okt: dihitung PER SEBAB (jam server belum diterima / kuota habis / ubahan toko belum sampai ≠ "belum dibaca penuh"),
  // "jenis catatan" (bukan "koleksi"); petunjuk menu dibuang — panelnya ini
  const BL = H.belumLengkap || {}; const grupH = {};
  Object.keys(BL).forEach((k) => { if (!BL[k] || BL[k].jenis !== 'harian') return; const s = String(BL[k].sebab || '').replace(' (' + HB_TEMPAT + ')', ''); grupH[s] = (grupH[s] || 0) + 1; });
  const tundaToko = kl && kl.selesai && kl.temuanTunda && typeof kl.temuanTunda === 'object' ? Object.keys(kl.temuanTunda).reduce((a, k) => a + (Number(kl.temuanTunda[k]) || 0), 0) : 0;
  return { status, nyala: !!H.nyala, saklar: !!H.saklar, owner: !!H.owner,
    harianBelum: H.nyala && Object.keys(grupH).length ? Object.keys(grupH).map((s) => grupH[s] + ' jenis catatan ' + s).join('; ') + '. Kartu pemeriksaan sesudah tutup buku, kunci bulan, Laporan › Pajak & dokumen Laporan menunggu sampai lengkap.' : '',
    judul: 'Hemat baca: ' + status + ' di perangkat ini',
    ket: H.nyala ? 'Perangkat ini memakai simpanannya sendiri dan hanya menarik catatan yang berubah (bercap jam server). Sekali sehari satu perangkat owner membaca penuh untuk toko, sesudah kuota baca Firebase direset (' + (H.jamReset || '14.00/15.00') + ' WIB); tiap perangkat membaca penuh paling lambat 14 hari sekali.'
      : 'Mati = tiap kali aplikasi dibuka, semua catatan toko dibaca dari server (±7 rb baca; kuota gratis 50 rb sehari). Nyalakan HANYA sesudah daftar siap-nyala hijau 3 hari berturut-turut.',
    koleksi: daftar, nBelum: daftar.filter((x) => !x.ok).length, tertua: kapan.length ? Math.min.apply(null, kapan) : null, terbaru: kapan.length ? Math.max.apply(null, kapan) : null,
    harian: !kl ? 'belum ada baca penuh harian toko' : kl.selesai ? 'baca penuh harian ' + kl.hari + ' selesai oleh ' + (kl.nama || kl.perangkat || 'perangkat owner') + (tundaToko ? ' · ' + tundaToko + ' ubahan tanpa cap belum bisa sampai ke perangkat lain (perangkat lain diminta baca penuh sendiri)' : '') : 'baca penuh harian ' + kl.hari + ' sedang dikerjakan ' + (kl.nama || kl.perangkat || 'perangkat owner'),
    klaimKabar: H.klaimKabar || '', baca: H.baca || null, siap: S, siapOk: S.length > 0 && S.every((x) => x.ok),
    bolehNyala: !H.saklar && !!H.owner && !!H.nisanSah, alasanTidak: !H.owner ? 'hanya owner yang bisa menyalakan' : !H.nisanSah ? 'aturan server v7 belum terbukti di perangkat ini (owner menerbitkan rules v7 lewat Console dulu)' : '',
    kabar: [H.kabarMati, H.kabar, H.nisanKabar, H.ayunan, H.jalurPenuh, H.berhenti].filter((x) => !!x) };
}

// ---------- SS2 · Peran & persetujuan ----------
// Putaran 23c (owner 24 Sep): kisi menampilkan KEBENARAN SERVER. Kisi `sendiri` yang tidak dibuka firestore.rules v3 (akses.js SERVER_BUKA)
// tampil "tertutup server" beserta sebabnya (peta §6) — bukan "boleh sendiri". Nilai kisi tersimpan tetap; yang berubah cuma yang digambar.
export const SS_HITUNG_LACI = 'hitungLaci';   // rules v16 — sama dengan tutup-hari-logika HL_TINDAKAN (dijaga uji_tutup_tablet)
export const SS_TERTUTUP_SERVER = { hargaPelanggan: 'setelan harga hanya ditulis owner — "boleh sendiri" tetap jadi usul ke owner', hitungLaci: 'menutup hari menimpa titik kas (angka uang yang sudah tercatat) — Penjaga laci MENGIRIM hitungan laci dari kartu Tutup hari di tablet (rules v16), harinya ditutup owner dari Uang › Tutup hari',
  kedatangan: 'barang masuk dari tablet hanya untuk Penjaga laci (rules v15, keputusan owner 22 Nov 2026) — karyawan tidak mencatat kedatangan',
  uangKeluar: 'uang keluar dari tablet selalu jadi TITIPAN ke owner (rules v13) — laci di buku berkurang sesudah owner menyetujui' };
export const SS_LABEL_TAMPIL = { sendiri: 'boleh sendiri', server: 'tertutup server', owner: 'minta owner', tidak: 'tidak boleh' };
export function ssHakServer(peran, tindakan, nilai) {
  if (peran === 'owner') return { nilai, label: SS_LABEL_TAMPIL[nilai], ket: '' };
  if (nilai === 'sendiri' && (SERVER_BUKA[tindakan] || []).indexOf(peran) < 0) return { nilai: 'server', label: SS_LABEL_TAMPIL.server, ket: SS_TERTUTUP_SERVER[tindakan] || 'server belum membuka tindakan ini untuk peran ini' };
  if (nilai === 'owner' && tindakan === HT_TINDAKAN) return { nilai, label: SS_LABEL_TAMPIL.owner, ket: 'usul ke owner lewat papan Persetujuan — berlaku sesudah owner setujui' };   // B1 (owner 16 Nov 2026), rules v8
  if (nilai === 'owner' && tindakan === 'uangKeluar') return { nilai, label: SS_LABEL_TAMPIL.owner, ket: 'titipan dari tablet (kartu "Uang keluar & pesan" di Menu akun tablet) — owner menyetujui, membetulkan, atau menolak di Uang / papan Persetujuan' };   // owner 21 Nov 2026, rules v13
  if (nilai === 'owner') return { nilai, label: SS_LABEL_TAMPIL.owner, ket: 'alur persetujuannya belum ada — sampai itu dibangun, server menutupnya' };
  return { nilai, label: SS_LABEL_TAMPIL[nilai] || nilai, ket: '' };
}
export function ssPeran() {
  const A = ssAtur('peran'); const hak = (peran, t) => (peran === 'owner' ? 'sendiri' : (A.hak[peran] || {})[t] || 'tidak');
  const tampil = (peran, t) => ssHakServer(peran, t, hak(peran, t));
  return { tindakan: SS_TINDAKAN, hak, tampil, batasSekaligus: A.batasSekaligus, jatahBen: A.jatahBen, jatahKaryawan: A.jatahKaryawan, jatahAkun: A.jatahAkun || {}, bawahModal: A.bawahModal || [], langkahNego: A.langkahNego, jejak: (A.jejak || []).slice(0, 12),
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
  const akun = akunDok.map((a) => ({ uid: String(a.uid || a.id), nama: String(a.nama || ''), email: String(a.email || ''), peran: String(a.peran || ''), aktif: a.aktif === true, bacaUang: a.peran === 'ben' && a.bacaUang === true,
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
  // rules v14 (owner 21 Nov 2026): tanda bacaUang = akun ini membaca data uang untuk Ringkas hari ini di tablet. Hanya Penjaga laci; menyalakan = dua ketukan.
  if (U.bacaUang !== undefined) {
    if (U.bacaUang && (U.peran !== undefined ? U.peran : a.peran) !== 'ben') return { tolak: 'Data uang untuk Ringkas hari ini hanya untuk akun Penjaga laci (akun tablet)' };
    if (U.bacaUang && !yakin) return { tolak: 'Ketuk sekali lagi: akun ' + (a.nama || a.email) + ' akan MEMBACA data uang toko (titik kas, uang keluar, kasbon, upah, ambil pribadi). Di tablet angkanya tampil hanya saat orang pilihan lu yang jaga.', perluYakin: true };
  }
  const turunDariBen = U.peran !== undefined && U.peran !== 'ben';   // peran pindah dari Penjaga laci = tanda baca uang ikut mati
  const data = Object.assign({}, a, U.peran !== undefined ? { peran: U.peran } : {}, U.aktif !== undefined ? { aktif: U.aktif === true } : {}, U.bacaUang !== undefined ? { bacaUang: U.bacaUang === true } : {}, turunDariBen && a.bacaUang ? { bacaUang: false } : {});
  const teks = U.bacaUang !== undefined ? (U.bacaUang ? 'kini MEMBACA data uang untuk Ringkas hari ini di tablet' : 'tidak lagi membaca data uang') : U.peran !== undefined ? 'kini ' + (SS_PERAN.find((p) => p.id === U.peran) || {}).nama : U.aktif ? 'diaktifkan lagi' : 'DINONAKTIFKAN';
  return { dokumen: [{ koleksi: 'aksesAkun', data }], patch: { yakinAkun: null, kabar: (a.nama || a.email) + ' ' + teks + '.', kabarAwas: U.aktif === false } };
}
/** Permintaan "minta owner" (ditulis tablet/Mac ke koleksi persetujuan): yang menunggu + riwayat keputusan. */
export function ssPersetujuan(kini) {
  // owner 23 Nov 2026: pesan owner KE tablet bukan permintaan yang diputus — tidak tampil di papan ini (menunggu / riwayat)
  const semua = cacheMentah('persetujuan').filter((m) => m && m.tindakan !== 'pesanOwner').slice().sort(ssUrutTerbaru); const P = ssPeran();
  // B2 (owner 17 Nov 2026): permintaan BON lewat batas kredit — kalimatnya dihitung ulang dari buku bon sekarang (fkTeksMinta), tindakan kisinya = jualBon
  const tKisi = (m) => (m.tindakan === FK_TINDAKAN ? 'jualBon' : m.tindakan);
  const baris = (m) => { const Q = m.tindakan === 'nego' ? ngPeriksaMinta(m) : null; const HU = m.tindakan === HT_TINDAKAN ? htTeksUbah(m.ubah) : null; const KR = m.tindakan === FK_TINDAKAN ? fkTeksMinta(m) : null; return { id: String(m.id), dari: m.dari || '—', peran: m.peran || (String(m.dari || '').toLowerCase() === 'ben' ? 'ben' : 'karyawan'), tindakan: m.tindakan || '', namaTindakan: KR !== null ? 'Bon melewati batas kredit' : m.tindakan === TP_PESAN ? 'Pesan untuk owner' : (SS_TINDAKAN.find((t) => t.id === m.tindakan) || { nama: m.tindakan || 'tindakan' }).nama, modul: KR !== null ? 'Jual' : m.tindakan === TP_PESAN ? 'Pesan' : (SS_TINDAKAN.find((t) => t.id === m.tindakan) || { modul: '' }).modul,
    // sanggahan rules 7 Okt: permintaan NEGO tidak pernah ikut "setujui semua yang kecil" — rules tidak mengikat nominal / batas / alasan kiriman staf ke harga
    // barang, jadi owner melihatnya satu per satu; teks & angkanya dihitung ulang di sini (ngPeriksaMinta: barang, hargaMinta, jumlah + harga katalog sekarang)
    sekaligus: m.tindakan !== 'nego' && m.tindakan !== HT_TINDAKAN && m.tindakan !== FK_TINDAKAN,   // B1: usul harga pelanggan · B2: permintaan bon — dilihat satu per satu (kalimatnya dihitung ulang)
    teks: Q ? Q.teks : HU !== null ? HU : KR !== null ? KR : m.teks || '', n: Q ? Q.nominal || 0 : HU !== null ? 0 : Number(m.nominal) || 0, tanggal: m.tanggal || '', jam: m.jam || '', status: m.status || 'menunggu', alasanTolak: m.alasanTolak || '', diputusTanggal: m.diputusTanggal || '',
    saran: m.tindakan === TP_PESAN ? 'Pesan dari tablet — tandai dibaca, boleh dengan balasan singkat' : m.tindakan && P.hak(m.peran || 'karyawan', tKisi(m)) === 'tidak' ? 'Peran ' + (m.dari || 'ini') + ' sebenarnya TIDAK BOLEH untuk ini — kalau sering, ubah haknya' : 'Menurut kisi hak, ini memang minta owner' }; };
  // owner 21 Nov 2026: titipan uang keluar → kalimat titipan (jenis · keterangan · nama · rupiah); pesan → bukan uang (n 0), tidak pernah ikut "setujui sekaligus"
  // owner 22 Nov 2026: kabar barang masuk (tablet) = seperti pesan — bukan uang, ditandai diperiksa, tidak pernah ikut "setujui sekaligus"
  const barisTP = (m) => { const b = baris(m); if (m.tindakan === TP_TINDAKAN) b.teks = tpTeks(m); if (m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) Object.assign(b, { n: 0, sekaligus: false });
    // owner 22 Nov 2026 (paket ④): hitungan laci dari tablet — bukan uang keluar; diselesaikan di Uang › Tutup hari (Setujui di sini ditolak), tidak ikut sekaligus
    if (m.tindakan === SS_HITUNG_LACI) Object.assign(b, { n: 0, sekaligus: false, teks: 'Hitungan laci ' + tanggalPendek(m.tanggal || '') + ' · ' + RP(Number(m.hitung) || 0) + (Number(m.amankan) ? ' · ' + RP(Number(m.amankan)) + ' ke brankas' : ''), saran: 'Diselesaikan di Uang › Tutup hari (Pakai hitungan ini) — Tolak = minta hitung ulang' });
    if (m.tindakan === TP_KABAR) Object.assign(b, { teks: 'Barang masuk · ' + (m.teks || ''), saran: 'Kabar barang masuk dari tablet — tandai sudah diperiksa; harga & jumlah dibetulkan di Stok › Barang masuk' });
    // paket Banding pemasok (rules v21): usul harga tawaran / acuan dari tablet — bukan uang, dilihat satu per satu; Setujui = catatannya ditulis (dicek ulang)
    if (m.tindakan === BC_TINDAKAN) Object.assign(b, { n: 0, sekaligus: false, namaTindakan: m.jenis === 'acuan' ? 'Usul harga acuan resmi' : 'Usul harga tawaran pemasok', teks: bcTeksUsul(m), saran: 'Setujui = dicatat di Harga & Pemasok › Banding atas nama ' + (m.dari || 'tablet') + ' · Tolak = tulis alasannya' });
    return Object.assign(b, { pesan: m.tindakan === TP_PESAN || m.tindakan === TP_KABAR, balasan: m.balasan || '' }); };
  const menunggu = semua.filter((m) => (m.status || 'menunggu') === 'menunggu').map(barisTP); const riwayat = semua.filter((m) => m.status && m.status !== 'menunggu').map(barisTP).slice(0, 20);
  return { menunggu, riwayat, kecil: menunggu.filter((m) => m.sekaligus && m.n <= P.batasSekaligus).length, batas: P.batasSekaligus, judul: menunggu.length ? menunggu.length + ' permintaan menunggu owner' : 'Tidak ada yang menunggu' + (cacheMentah('persetujuan').length ? '' : ' — permintaan datang dari tablet karyawan (belum ada tabletnya)') };
}
export function susunPutusPersetujuan(id, setuju, alasan, w) {
  const m = cacheMentah('persetujuan').find((x) => String(x.id) === String(id)); if (!m) return { tolak: 'Permintaannya tidak ditemukan' }; if (m.status && m.status !== 'menunggu') return { tolak: 'Sudah diputus ' + (m.diputusTanggal ? tanggalPendek(m.diputusTanggal) : '') };
  // owner 21 Nov 2026: titipan uang keluar → uangnya ditulis di kiriman yang sama; pesan → ditandai dibaca (alasan = balasan). Dulu titipan hanya ditandai disetujui.
  if (m.tindakan === TP_TINDAKAN) return tpSusunPutus(id, setuju ? 'setuju' : 'tolak', setuju ? {} : { alasan }, w);
  if (m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) return tpSusunPutus(id, 'dibaca', { balasan: alasan }, w);
  // owner 22 Nov 2026 (paket ④): menyetujui hitungan laci = menutup hari — hanya lewat lembar Tutup hari (dokumen uang ikut); menolak = minta hitung ulang (di bawah)
  if (m.tindakan === SS_HITUNG_LACI && setuju) return { tolak: 'Hitungan laci diselesaikan di Uang › Tutup hari — ketuk "Pakai hitungan ini", cek QRIS (atau lewati), lalu Tutup' };
  if (!setuju && ssKosong(alasan)) return { tolak: 'Menolak butuh alasan — supaya ' + (m.dari || 'peminta') + ' tahu sebabnya' };
  // B1 (owner 16 Nov 2026): menyetujui usul harga pelanggan = memasang ubahannya ke setelan SEKARANG di kiriman yang sama (dihitung ulang, bukan teks kiriman)
  const HP = setuju && m.tindakan === HT_TINDAKAN ? htPasangUsul(m, w) : setuju && m.tindakan === BC_TINDAKAN ? bcPasangUsul(m, w) : null; if (HP && HP.tolak) return { tolak: HP.tolak };   // + banding pemasok (rules v21)
  return { dokumen: [{ koleksi: 'persetujuan', data: Object.assign({}, m, { status: setuju ? 'disetujui' : 'ditolak', alasanTolak: setuju ? '' : String(alasan).trim().slice(0, 80), diputusTanggal: w.tanggal, diputusJam: w.jam, diputusPada: w.kini }) }].concat(HP ? HP.dokumen : []),
    patch: { kabar: HP ? 'Disetujui & dipasang — ' + HP.kabar : setuju ? 'Disetujui — ' + (m.dari || 'peminta') + ' bisa melanjutkan di perangkatnya' : 'Ditolak (' + String(alasan).trim() + ') — ' + (m.dari || 'peminta') + ' dapat kabarnya', kabarAwas: false } };
}
export function susunSetujuiKecil(w) {
  const P = ssPersetujuan(new Date(w.kini)); const kecil = P.menunggu.filter((m) => m.sekaligus && m.n <= P.batas); const nSatu = P.menunggu.filter((m) => !m.sekaligus).length;
  if (!kecil.length) return { tolak: P.menunggu.length ? 'Semua permintaan di atas batas "sekaligus" (' + RP(P.batas) + ')' + (nSatu ? ' atau permintaan nego' : '') + ' — setujui satu per satu' : 'Tidak ada yang menunggu' };
  // owner 21 Nov 2026: SEMUA dokumen tiap putusan ikut (titipan uang = persetujuan + uangnya — dulu hanya dokumen pertama, uangnya hilang);
  // yang tidak bisa diputus (mis. bulan terkunci) dilewati dan disebut
  const dokumen = []; const lewat = []; kecil.forEach((m) => { const r = susunPutusPersetujuan(m.id, true, '', w); if (r.dokumen) r.dokumen.forEach((x) => dokumen.push(x)); else lewat.push((m.dari || '?') + ': ' + (r.tolak || 'tidak bisa')); });
  if (!dokumen.length) return { tolak: 'Tidak ada yang bisa disetujui sekaligus — ' + lewat.join(' · ') };
  return { dokumen, patch: { kabar: (kecil.length - lewat.length) + ' permintaan kecil (≤ ' + RP(P.batas) + ') disetujui sekaligus' + (P.menunggu.length - kecil.length - nSatu ? '; ' + (P.menunggu.length - kecil.length - nSatu) + ' yang besar masih menunggu' : '') + (nSatu ? '; ' + nSatu + ' permintaan nego dilihat satu per satu (angkanya dihitung ulang dari harga katalog)' : '') + (lewat.length ? '; dilewati: ' + lewat.join(' · ') : ''), kabarAwas: !!lewat.length } };
}

// ---------- SS3 · Cadangan & kuota ----------
const SS_TAK_DICADANGKAN = { logAktivitas: 1, perangkatStatus: 1 };   // jejak terbatas & denyut bukan data toko
/** Era tutup buku = tahun saldo pembuka terakhir (eraTutupBuku index.html); null = belum pernah tutup buku. Satu tempat: toko.js eraBuku (daftar koleksi
 *  pembuka CACHE_PEMBUKA — termasuk modal owner sejak siap 2027; dulu daftar sendiri di sini tanpa modal). */
export function ssEraTutupBuku() { return eraBuku(); }
/** Isi berkas cadangan = bentuk unduhBackup() sistem lama (versi 5): semua koleksi + peta jenis beras + cap era; koleksi baru ikut. */
export function ssBerkasCadangan(kini, hemat) {
  const isi = { versi: 5, diunduhPada: kini.toISOString(), sumber: 'sistem baru', eraTutupBuku: ssEraTutupBuku() }; let dokumen = 0, koleksi = 0;
  KOLEKSI.forEach((k) => { if (SS_TAK_DICADANGKAN[k.nama]) return; isi[k.nama] = cacheMentah(k.cache).slice(); dokumen += isi[k.nama].length; koleksi += 1; });
  isi.petaJenisBeras = ambilPetaJenisBeras();
  // owner 7 Okt (hemat baca nyala): koleksi yang belum terperiksa dengan server DISEBUT di nama berkas & isinya (kalau ragu, berkas mengaku). Mati = sama persis.
  const belum = hemat && hemat.nyala ? (hemat.belum || []) : [];
  if (belum.length) isi.keadaanData = { belum: belum.slice(), kalimat: belum.length + ' koleksi belum terperiksa dengan server saat diunduh (hemat baca)' };
  return { isi, dokumen, koleksi, nama: 'backup-batch-miqbal-' + hariIniIso(kini) + (belum.length ? '-BELUM-TERPERIKSA' : '') + '.json' };
}
export function susunCatatCadangan(b, ukuranBytes, w, perangkat) {
  return { dokumen: [{ koleksi: 'cadanganCatatan', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, perangkat: perangkat || '', nama: b.nama, ukuranKb: Math.round((ukuranBytes || 0) / 1024), dokumen: b.dokumen, koleksi: b.koleksi, jenis: 'manual', ok: true, versi: 5, era: b.isi.eraTutupBuku } }],
    patch: { kabar: 'Berkas ' + b.nama + ' diunduh (' + ANGKA(Math.round((ukuranBytes || 0) / 1024)) + ' KB · ' + ANGKA(b.dokumen) + ' catatan) — simpan juga di tempat lain (Drive / komputer)', kabarAwas: false } };
}
export const SS_LS_BATAS_KB = 5120;   // localStorage peramban ±5 MB (perkiraan umum, bukan angka pasti)
export const SS_LAJU_LS_KB = 62;      // ±62 KB/hari pertumbuhan cadangan lokal SISTEM LAMA (pengukuran 15 Sep 2026) — PERKIRAAN
/** Kalender 14 hari & kesehatan. lokal = { autoTanggal (cap cadangan otomatis sistem lama di perangkat ini), lsKb, usageKb, quotaKb, koleksiSiap, koleksiTotal,
 *  lamaKb & lamaN (ukuran & JUMLAH sisa simpanan sistem lama, dihitung layar saat lembar dibuka; null = belum/tidak terbaca) } — dari peramban. */
export function ssCadangan(kini, lokal, hariPilih) {
  const A = ssAtur('cadangan'); const iso = hariIniIso(kini); const L = lokal || {};
  const catatan = cacheMentah('cadangan').map((c) => ({ id: String(c.id), tanggal: c.tanggal || '', jam: c.jam || '', perangkat: c.perangkat || '', nama: c.nama || '', kb: Number(c.ukuranKb) || 0, dokumen: Number(c.dokumen) || 0, ok: c.ok !== false, jenis: c.jenis || 'manual', sumber: 'sistem baru' }));
  if (L.autoTanggal) catatan.push({ id: 'lama-auto-' + L.autoTanggal, tanggal: L.autoTanggal, jam: '', perangkat: 'HP ini', nama: 'backup otomatis sistem lama', kb: 0, dokumen: 0, ok: true, jenis: 'otomatis', sumber: 'sistem lama' });
  catatan.sort((a, b) => (b.tanggal + b.jam).localeCompare(a.tanggal + a.jam));
  const terakhir = catatan.find((c) => c.ok) || null; const umurHari = terakhir ? ssHariKe(iso) - ssHariKe(terakhir.tanggal) : null;
  const kalender = []; for (let h = 13; h >= 0; h--) { const t = ssTambahHari(iso, -h); const hari = catatan.filter((c) => c.tanggal === t); kalender.push({ iso: t, tgl: String(parseInt(t.slice(8, 10), 10)), nm: ssHariNama(t), n: hari.length, keadaan: hari.some((c) => c.ok) ? 'ok' : hari.length ? 'gagal' : '', ini: t === iso, aktif: t === (hariPilih || iso) }); }
  const pilih = hariPilih || iso; const hariDaftar = catatan.filter((c) => c.tanggal === pilih);
  const lsKb = L.lsKb === undefined || L.lsKb === null ? null : Number(L.lsKb); const pct = lsKb === null ? null : Math.round(lsKb / SS_LS_BATAS_KB * 100);
  // owner 7 Okt (tinjauan): ada/tidak ada sisa lama diputuskan dari JUMLAH simpanannya (lamaN), bukan dari KB yang dibulatkan (sisa < 0,5 KB dulu ditulis
  // "tidak ada lagi" padahal kartunya menyebut 1 simpanan). Tanpa lamaN (pemanggil lama) jatuh ke lamaKb > 0. null = belum/tidak terbaca → tidak disebut.
  const adaLama = L.lamaN !== undefined && L.lamaN !== null ? Number(L.lamaN) > 0 : L.lamaKb === undefined || L.lamaKb === null ? null : Number(L.lamaKb) > 0;
  const kbLama = Number(L.lamaKb) || 0;
  const kuota = { adaAngka: lsKb !== null, kb: lsKb, batasKb: SS_LS_BATAS_KB, pct, awas: pct !== null && pct >= A.ambangKuota, sisaHari: lsKb === null ? null : Math.max(0, Math.floor((SS_LS_BATAS_KB - lsKb) / SS_LAJU_LS_KB)),
    teks: lsKb === null ? 'Ukuran simpanan lokal tidak bisa dibaca di peramban ini' : ANGKA(lsKb) + ' KB dari ±' + ANGKA(SS_LS_BATAS_KB) + ' KB simpanan lokal (sistem baru, kasir darurat & sisa sistem lama — alamat yang sama) terpakai',
    // owner 7 Okt (sisa pensiun #103): laju ±62 KB/hari dulu = cadangan SISTEM LAMA; sejak pensiun 3 Okt sisanya tidak bertambah lagi → kalimatnya menyebut
    // sisa itu (lamaKb dari layar), bukan ramalan "hari lagi penuh" yang sudah tidak berlaku. sisaHari tetap dihitung (angka lama, tidak digambar).
    ket: lsKb === null || adaLama === null ? '' : adaLama ? '±' + (kbLama < 0.5 ? 'kurang dari 1' : ANGKA(Math.round(kbLama))) + ' KB di antaranya sisa sistem lama yang sudah pensiun (tidak bertambah lagi) — bisa dibersihkan di bawah' : 'tidak ada lagi sisa sistem lama di perangkat ini',
    // peringatan hanya menunjuk tombol bersihkan kalau tombolnya ADA (ada sisa lama). Tanpa sisa lama yang memenuhi simpanan = sistem baru & kasir darurat sendiri.
    awasTeks: pct === null ? '' : pct >= A.ambangKuota ? 'Di atas ambang ' + A.ambangKuota + '% (Atur): kalau penuh, simpanan sistem baru di perangkat ini (draf, kiriman yang menunggu sinyal) bisa gagal tersimpan — '
      + (adaLama ? 'bersihkan sisa sistem lama dengan tombol di bawah' : adaLama === false ? 'sisa sistem lama sudah tidak ada, jadi yang memenuhi simpanan adalah sistem baru & kasir darurat sendiri. Jangan hapus data situs di setelan peramban (kiriman yang belum sampai server ikut hilang); unduh cadangan dulu' : 'sisa sistem lama di perangkat ini belum terbaca')
      : 'Masih di bawah ambang ' + A.ambangKuota + '%' };
  const simpanan = { adaAngka: L.usageKb !== undefined && L.usageKb !== null, kb: Number(L.usageKb) || 0, quotaKb: Number(L.quotaKb) || 0, pct: L.quotaKb ? Math.round((Number(L.usageKb) || 0) / Number(L.quotaKb) * 100) : null };
  const sehat = [['cadangan terakhir', terakhir ? (umurHari === 0 ? 'hari ini' : umurHari + ' hari lalu') : 'belum pernah'], ['dari sistem baru', String(catatan.filter((c) => c.sumber === 'sistem baru' && c.ok).length) + ' berkas'],
    ['otomatis sistem lama (HP ini)', L.autoTanggal ? tanggalPendek(L.autoTanggal) : 'tidak ada capnya'], ['koleksi di simpanan perangkat', L.koleksiTotal ? (L.koleksiSiap || 0) + ' dari ' + L.koleksiTotal : '—']].map((x) => ({ t: x[0], n: x[1] }));
  return { catatan, terakhir, umurHari, telat: umurHari === null || umurHari > A.cadanganTiap, kalender, hariPilih: pilih, hariDaftar, hariJudul: (pilih === iso ? 'Hari ini' : tanggalPendek(pilih)) + ': ' + (hariDaftar.length ? hariDaftar.length + ' cadangan' : 'tidak ada cadangan'), kuota, simpanan, sehat, atur: A,
    ringkas: terakhir ? 'Terakhir ' + tanggalPendek(terakhir.tanggal) + (terakhir.jam ? ' ' + terakhir.jam : '') + ' · ' + terakhir.sumber + (terakhir.kb ? ' · ' + ANGKA(terakhir.kb) + ' KB' : '') + (umurHari > A.cadanganTiap ? ' — sudah ' + umurHari + ' hari, lebih dari jadwal ' + A.cadanganTiap + ' hari' : '') : 'Belum pernah ada cadangan yang tercatat — unduh sekarang',
    era: ssEraTutupBuku() };
}
// owner 7 Okt (sisa pensiun #103): kunci simpanan lokal milik SISTEM LAMA (index.html) dan kasir.html lama — DIBEKUKAN dari tag git sistem-lama-terakhir
// (48a694d). Dikurangi yang masih dibaca /baru/ (nomor & nama perangkat, titik kas, peta jenis beras, cap cadangan otomatis lama) dan yang dipakai kasir
// darurat (akun, operator, katalog HP kasir): yang itu TIDAK ada di daftar ini, jadi tombol bersihkan tidak pernah menyentuhnya. Dijaga uji_dokumen_sisa.py.
export const SS_KUNCI_LAMA = ['miqbal_amplop_laba_v1', 'miqbal_antrean_ditolak_v1', 'miqbal_antrean_tunda_v1', 'miqbal_batch_masuk_v2', 'miqbal_biaya_bulanan',
  'miqbal_buka_toko_v2', 'miqbal_draf_masuk_v1', 'miqbal_gerbang_v1', 'miqbal_karantina_v1', 'miqbal_kasbon_mutasi_v1', 'miqbal_katalog_harga_karung_v1', 'miqbal_katalog_harga_kemasan_v1',
  'miqbal_katalog_harga_literan_v1', 'miqbal_modal_owner_v1', 'miqbal_owner_unlock', 'miqbal_pelanggan_catatan_v1', 'miqbal_pemasok_catatan_v1', 'miqbal_pengeluaran_harian_v1',
  'miqbal_penjualan_v1', 'miqbal_penyesuaian_kemasan_v1', 'miqbal_penyesuaian_stok_v1', 'miqbal_pesanan_v1', 'miqbal_pin_owner_v1', 'miqbal_pin_percobaan_v1', 'miqbal_piutang_mutasi_v1',
  'miqbal_produksi_kemasan_v1', 'miqbal_qris_v1', 'miqbal_retur_v1', 'miqbal_ringkasan_terakhir', 'miqbal_ringkasan_terbit_v1', 'miqbal_roster_v1', 'miqbal_setoran_kas_v1',
  'miqbal_stok_bahan_kemasan_v1', 'miqbal_stok_bahan_literan_v1', 'miqbal_tema_v1', 'miqbal_tembusan_stok_v1', 'miqbal_tempat_simpan_v1', 'miqbal_thr_pelanggan_v1', 'miqbal_titipan_harian_v1',
  'miqbal_tukar_setengah_v1', 'miqbal_tutup_hari_v1', 'miqbal_uji_penjaga_v1', 'miqbal_utang_owner_v1', 'miqbal_utang_pemasok_v1',
  'kasir_antrean_v1', 'kasir_bayar_bon_v1', 'kasir_ditolak_arsip_v1', 'kasir_gagal_v1', 'kasir_perangkat_v1', 'kasir_roster_v1'];
// antrean lama = catatan yang belum pernah sampai server (larik JSON). Yang masih berisi TIDAK dibersihkan sampai salinannya diunduh (kalau ragu, menutup).
export const SS_KUNCI_LAMA_ANTREAN = ['miqbal_antrean_tunda_v1', 'miqbal_antrean_ditolak_v1', 'kasir_antrean_v1', 'kasir_gagal_v1', 'kasir_bayar_bon_v1', 'kasir_ditolak_arsip_v1'];
// kunci sistem lama yang TIDAK ikut berkas "unduh salinannya" (owner 7 Okt, tinjauan): salinan PIN owner (garam + acak PIN 4–8 angka — mudah ditebak ulang
// kalau berkasnya dibagikan), hitungan PIN salah, dan penanda gembok terbuka. Tetap ikut DIBERSIHKAN.
export const SS_KUNCI_LAMA_TAK_DIUNDUH = ['miqbal_pin_owner_v1', 'miqbal_pin_percobaan_v1', 'miqbal_owner_unlock'];
/** Isi berkas "unduh salinannya": kunci daftar beku yang ada apa adanya, TANPA SS_KUNCI_LAMA_TAK_DIUNDUH. isi = { kunci: teks | null } → { isi, n, dibuang:[kunci] }. */
export function ssSalinanLama(isi) {
  const I = isi || {}; const out = {}; const dibuang = [];
  SS_KUNCI_LAMA.forEach((k) => { const v = I[k]; if (v === null || v === undefined) return; if (SS_KUNCI_LAMA_TAK_DIUNDUH.indexOf(k) >= 0) { dibuang.push(k); return; } out[k] = String(v); });
  return { isi: out, n: Object.keys(out).length, dibuang };
}
/**
 * Sisa simpanan sistem lama di perangkat ini. isi = { kunci: teks | null } — layar membaca localStorage HANYA untuk SS_KUNCI_LAMA; sudahUnduh = salinannya
 * sudah diunduh di layar ini. → { ada:[{ kunci, kb, antrean, n }], kb, dibersihkan:[kunci], kbBersih, dijaga:[…], nCatatan, teks }.
 */
export function ssSimpananLama(isi, sudahUnduh) {
  const I = isi || {}; const ada = [];
  SS_KUNCI_LAMA.forEach((k) => { const v = I[k]; if (v === null || v === undefined) return; const s = String(v); const antrean = SS_KUNCI_LAMA_ANTREAN.indexOf(k) >= 0; let n = null;
    if (antrean) { try { const j = JSON.parse(s.trim() || '[]'); n = Array.isArray(j) ? j.length : j && typeof j === 'object' ? Object.keys(j).length : j ? 1 : 0; } catch (e) { n = s.trim() ? 1 : 0; } }
    ada.push({ kunci: k, kb: (k.length + s.length) * 2 / 1024, antrean, n }); });
  const dijaga = ada.filter((x) => x.antrean && x.n > 0 && !sudahUnduh); const bersih = ada.filter((x) => dijaga.indexOf(x) < 0);
  const kb = ada.reduce((a, x) => a + x.kb, 0); const kbBersih = bersih.reduce((a, x) => a + x.kb, 0); const nCatatan = dijaga.reduce((a, x) => a + x.n, 0);
  return { ada, kb, dibersihkan: bersih.map((x) => x.kunci), kbBersih, dijaga, nCatatan,
    teks: !ada.length ? 'Tidak ada sisa simpanan sistem lama di perangkat ini.' : 'Salinan data toko yang dulu disimpan sistem lama & kasir lama di perangkat ini supaya bisa jalan tanpa internet. Sejak pensiun 3 Okt tidak ada aplikasi di perangkat ini yang membacanya lagi, tapi masih memakan simpanan perangkat. Membersihkannya TIDAK menghapus data toko di server; nomor & nama perangkat, titik kas, jenis beras, dan simpanan kasir darurat tidak disentuh.' };
}

// ---------- SS4 · Lokasi (fondasi) ----------
export function ssLokasi() { const A = ssAtur('lokasi'); const utama = A.daftar.find((l) => l.utama) || A.daftar[0]; return { daftar: A.daftar, utama, pengantar: A.pengantar }; }
/** Stok per merek per lokasi (kg): buku mesin lama = seluruhnya di lokasi utama; pindah stok menggesernya (keluar −, masuk +). Jumlah semua lokasi = buku. */
export function ssStokLokasi() {
  const { utama } = ssLokasi(); const stokK = ingatStokKarung(); const out = {};
  Object.keys(stokK).forEach((m) => { out[m] = {}; out[m][utama.id] = Math.round((stokK[m].sisaKg || 0) * 100) / 100; });
  cacheMentah('pindahStok').forEach((p) => { if (!p.merk || !p.lokasi) return; if (!out[p.merk]) out[p.merk] = {}; const kg = Number(p.kg) || 0; out[p.merk][p.lokasi] = Math.round(((out[p.merk][p.lokasi] || 0) + (p.tipe === 'masuk' ? kg : -kg)) * 100) / 100; });
  return out;
}
export function ssLaporLokasi(kini) {
  const { daftar, utama } = ssLokasi(); const iso = hariIniIso(kini); const bulan = iso.slice(0, 7); const stok = ssStokLokasi(); const stokK = ingatStokKarung(); const perangkat = cacheMentah('perangkat');
  const lapor = daftar.map((l) => { const merek = Object.keys(stok).filter((m) => Math.abs(stok[m][l.id] || 0) > 0.05).map((m) => ({ nama: m, kg: stok[m][l.id] })).sort((a, b) => b.kg - a.kg);
    const kg = merek.reduce((a, m) => a + m.kg, 0); const nilai = merek.reduce((a, m) => a + m.kg * ((stokK[m.nama] || {}).hppTerakhirPerKg || 0), 0);
    const nota = ambilPenjualan().filter((p) => (p.lokasi || utama.id) === l.id); const hariIni = nota.filter((p) => p.tanggal === iso); const bulanIni = nota.filter((p) => (p.tanggal || '').slice(0, 7) === bulan);
    // no. 19: omzet per lokasi = penjualan − uang retur lokasi itu (retur membawa lokasi perangkat; tanpa lokasi → lokasi utama)
    const rt = ambilRetur().filter((r) => (r.lokasi || utama.id) === l.id); const uangR = (f) => rt.filter((r) => f(String(r.tanggal || ''))).reduce((a, r) => a + uangKembaliRetur(r), 0);
    return { id: l.id, nama: l.nama, utama: l.utama, alamat: l.alamat, kg, nilai, merek, omzetHari: hariIni.reduce((a, p) => a + (p.hargaTotal || 0), 0) - uangR((t) => t === iso), notaHari: new Set(hariIni.map((p) => p.grupNota || p.trxId || p.id)).size, omzetBulan: bulanIni.reduce((a, p) => a + (p.hargaTotal || 0), 0) - uangR((t) => t.slice(0, 7) === bulan), notaBulan: new Set(bulanIni.map((p) => p.grupNota || p.trxId || p.id)).size,
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
  // Paket F1: bon lama yang bergulir diramal dari kedatangan terakhir pemasoknya (gulirBon — aturan yang sama dengan layar Bon pemasok)
  const G = petaGulir();
  hitungUtangPemasok().forEach((px) => { const T = tempoPemasok(px.pemasok); (px.bon || []).forEach((b) => { const g = gulirBon(G, px.pemasok, b); const d = g || b.tanggal; if (!d || !(T.hari > 0)) { bonTanpaTanggal += 1; return; } out.push({ id: 'bon|' + b.id, jenis: 'bon', kunci: b.id, teks: 'Bon ' + px.pemasok + ' jatuh tempo', siapa: px.pemasok, jatuh: ssTambahHari(d, T.hari), n: b.sisa, ket: (g ? 'bon lama bergulir · ikut kedatangan ' + tanggalPendek(g) : 'bon ' + tanggalPendek(b.tanggal)) + ' · ' + T.teks }); }); });
  semuaBon(kini).forEach((b) => { if (b.sisa <= 0 || !b.tagih || !b.tagih.janji || (b.status !== 'menunggu' && b.status !== 'janjiLewat')) return; out.push({ id: 'janji|' + b.kunci + '|' + b.tagih.janji, jenis: 'janji', kunci: b.kunci, teks: b.nama + ' janji bayar', siapa: b.nama, jatuh: b.tagih.janji, n: b.sisa, ket: 'ditagih ' + tanggalPendek(b.tagih.tanggal) + ' · sisa bon ' + RP(b.sisa) }); });
  const bahan = hitungStokBahanKemasan(); const mulai = ssTambahHari(iso, -14); const pakai = {}; ambilBahanKemasan().forEach((x) => { if (x.tipe === 'pakai' && !x.pindahMerek && (x.tanggal || '') >= mulai) pakai[x.jenis] = (pakai[x.jenis] || 0) + (Number(x.jumlah) || 0); });
  // owner 11 Okt: pindahan ke buku per merek bukan pemakaian; gabungan lama yang sudah dipecah (sisa 0) tidak diingatkan lagi
  Object.keys(bahan).forEach((j) => { const laju = (pakai[j] || 0) / 14; if (!(laju > 0)) return; if (kantongLama(j) && !((bahan[j].sisaPcs || 0) > 0)) return; const sisa = Math.max(0, bahan[j].sisaPcs || 0); const hari = Math.floor(sisa / laju); const jatuh = ssTambahHari(iso, hari);
    out.push({ id: 'kantong|' + j + '|' + jatuh.slice(0, 7), jenis: 'kantong', kunci: j, teks: (LABEL_BAHAN_KEMASAN[j] || j) + ' cukup ' + hari + ' hari', siapa: 'kantong', jatuh, n: 0, ket: ANGKA(sisa) + ' pcs · terpakai ±' + ANGKA(Math.round(laju * 7)) + ' pcs/minggu' }); });
  let opnameAkhir = ''; ambilPenyesuaianStok().concat(ambilPenyesuaianKemasan()).forEach((x) => { if (x.dariRework) return; if ((x.tanggal || '') > opnameAkhir) opnameAkhir = x.tanggal; }); ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((x) => { if (x.tipe === 'opname' && !x.lahirKarungBekas && !x.nilaiKarungBekas && (x.tanggal || '') > opnameAkhir) opnameAkhir = x.tanggal; });
  out.push({ id: 'opname|' + (opnameAkhir ? ssTambahHari(opnameAkhir, A.opnameTiap) : iso), jenis: 'opname', kunci: 'stok', teks: opnameAkhir ? 'Opname rutin (terakhir ' + tanggalPendek(opnameAkhir) + ')' : 'Opname pertama — belum pernah dicocokkan', siapa: 'stok', jatuh: opnameAkhir ? ssTambahHari(opnameAkhir, A.opnameTiap) : iso, n: 0, ket: 'tiap ' + A.opnameTiap + ' hari (Atur)' });
  const C = ssAtur('cadangan'); let cadAkhir = (lokal && lokal.autoTanggal) || ''; cacheMentah('cadangan').forEach((c) => { if (c.ok !== false && (c.tanggal || '') > cadAkhir) cadAkhir = c.tanggal; });
  out.push({ id: 'cadangan|' + (cadAkhir ? ssTambahHari(cadAkhir, C.cadanganTiap) : iso), jenis: 'cadangan', kunci: 'cadangan', teks: cadAkhir ? 'Cadangan berkas (terakhir ' + tanggalPendek(cadAkhir) + ')' : 'Belum pernah ada cadangan berkas', siapa: 'cadangan', jatuh: cadAkhir ? ssTambahHari(cadAkhir, C.cadanganTiap) : iso, n: 0, ket: 'tiap ' + C.cadanganTiap + ' hari (Atur cadangan)' });
  // putaran 24: pajak — sumbernya dihitung modul pajak (owner saja) dan diteruskan lewat lokal.pajak: tanggal setor bulan lalu, hanya kalau bulan itu terutang & belum disetor
  (lokal && Array.isArray(lokal.pajak) ? lokal.pajak : []).forEach((p) => { if (p && p.jenis === 'pajak' && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  // B2 (owner 17 Nov 2026): faktur pelanggan usaha yang masih terbuka — jatuh = tanggal jatuh tempo faktur (tempo pelanggan), nominal = sisa faktur itu
  fkSemua(kini).forEach((f) => { if (!(f.sisa > 0.5) || !/^\d{4}-\d{2}-\d{2}$/.test(String(f.jatuhTempo || ''))) return; out.push({ id: 'faktur|' + f.no, jenis: 'faktur', kunci: f.kunci, teks: 'Faktur ' + f.no + ' · ' + f.nama + ' jatuh tempo', siapa: f.nama, jatuh: f.jatuhTempo, n: f.sisa, ket: 'sisa ' + RP(f.sisa) + ' dari ' + RP(f.total) + ' · nota ' + tanggalPendek(f.tanggal) + ' · tempo ' + f.tempoHari + ' hari' }); });
  // paket KPI laba (owner 24 Nov 2026, butir 14): cek mingguan timbangan & gudang — jatuh = cek terakhir (koleksi cekGudang) + gudangTiap hari; belum pernah = hari ini
  const CG = ssCekGudang(kini); out.push({ id: 'gudang|' + CG.jatuh, jenis: 'gudang', kunci: 'gudang', teks: CG.terakhir ? 'Cek timbangan & gudang (terakhir ' + tanggalPendek(CG.terakhir.tanggal) + ')' : 'Cek timbangan & gudang — belum pernah', siapa: 'gudang', jatuh: CG.jatuh, n: 0, ket: 'tiap ' + CG.tiap + ' hari · ' + SS_CEK_GUDANG.length + ' hal: ' + SS_CEK_GUDANG.map((c) => c.pendek).join(', ') });
  // Pondasi paket kedua (owner 24 Nov 2026): target kuartal BERIKUTNYA yang belum diisi — jatuh = hari pertama kuartal itu (diingatkan hariKuartal hari
  // sebelumnya); kuartal BERJALAN yang targetnya masih kosong diingatkan hanya selama SS_KUARTAL_SUSUL hari pertamanya (sesudah itu tidak ditagih terus).
  const kwKini = ssKuartalKey(iso), kwDepan = ssKuartalGeser(kwKini, 1); const ket = 'omzet, laba bersih & batas utang — Laporan › Kuartal › Atur target';
  if (!ssTargetKuartal(kwDepan).ada) out.push({ id: 'kuartal|' + kwDepan, jenis: 'kuartal', kunci: kwDepan, teks: 'Isi target ' + ssKuartalNama(kwDepan), siapa: 'kuartal', jatuh: ssKuartalAwal(kwDepan), n: 0, ket });
  if (!ssTargetKuartal(kwKini).ada && ssHariKe(iso) - ssHariKe(ssKuartalAwal(kwKini)) < SS_KUARTAL_SUSUL) out.push({ id: 'kuartal|' + kwKini, jenis: 'kuartal', kunci: kwKini, teks: 'Isi target ' + ssKuartalNama(kwKini) + ' (sudah berjalan)', siapa: 'kuartal', jatuh: ssKuartalAwal(kwKini), n: 0, ket });
  // Pondasi paket ketujuh (owner 25 Nov 2026): tinjauan bulanan — bulan LALU yang belum ditinjau, jatuh = tanggal 1 bulan ini; ditagih hanya SS_TINJAUAN_SUSUL
  // hari pertama (bukan pengingat "lewat" abadi) dan hanya kalau bulan lalu memang ada jualannya
  const blnLalu = ssBulanGeser(iso.slice(0, 7), -1);
  if (!ssTinjauanBulan(blnLalu) && Number(iso.slice(8, 10)) <= SS_TINJAUAN_SUSUL && ambilPenjualan().some((p) => String(p.tanggal || '').slice(0, 7) === blnLalu))
    out.push({ id: 'tinjauan|' + blnLalu, jenis: 'tinjauan', kunci: blnLalu, teks: 'Tulis tinjauan bulan ' + blnLalu.slice(5, 7) + '/' + blnLalu.slice(0, 4), siapa: 'tinjauan', jatuh: iso.slice(0, 7) + '-01', n: 0, ket: 'yang berjalan, yang tidak, keputusan — Laporan › Pondasi › Tinjauan bulanan' });
  // owner 26 Nov 2026 (A105): HARI TAGIH — satu pengingat pada hari tagih tetap (jatuh = hari tagih berikutnya), nominal = bon yang jatuh tempo sampai hari itu
  const HT = pnHariTagih(kini); if (HT.nyala && HT.daftar.length) out.push({ id: 'tagih|' + HT.berikut, jenis: 'tagih', kunci: 'tagih', teks: 'Hari tagih ' + HT.nama + ': ' + HT.daftar.length + ' orang', siapa: 'bon pelanggan', jatuh: HT.berikut, n: HT.rp,
    ket: HT.daftar.slice(0, 4).map((o) => o.nama + ' ' + RP(o.rp)).join(' · ') + (HT.daftar.length > 4 ? ' · +' + (HT.daftar.length - 4) + ' orang' : '') + ' — Pelanggan › Bon › Papan tagih' });
  // owner 26 Nov 2026: setor ke bank & cocok rekening — dihitung kas-rekening-logika (owner saja, butuh uang) dan diteruskan lewat lokal.uang (pola lokal.pajak)
  (lokal && Array.isArray(lokal.uang) ? lokal.uang : []).forEach((p) => { if (p && (p.jenis === 'setor' || p.jenis === 'rekening') && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  // paket Banding pemasok (owner 26 Nov 2026): minggu ini belum punya harga dari N pemasok (jatuh = hari setelan, bawaan Jumat) · bulan lalu belum ditandai
  // "sudah dibanding" (jatuh = tanggal setelan, bawaan tanggal 1; ditagih paling lama 7 hari) — aturan & jadwalnya di banding-catat-logika
  bcSumberPengingat(iso).forEach((p) => out.push(p));
  // owner 26 Nov 2026 (stok minus, label & kepatuhan): kalender kepatuhan (patuh-logika ptSumberPengingat) · kemasan dekat "baik dipakai sebelum" (label-logika) · buku
  // stok minus (gudang-logika) — dihitung modulnya masing-masing dan diteruskan app.js lewat lokal.patuh / lokal.gudang (modul itu memakai sistem-logika: tanpa impor balik)
  (lokal && Array.isArray(lokal.patuh) ? lokal.patuh : []).forEach((p) => { if (p && p.jenis === 'patuh' && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  (lokal && Array.isArray(lokal.gudang) ? lokal.gudang : []).forEach((p) => { if (p && (p.jenis === 'kemasan' || p.jenis === 'minus' || p.jenis === 'kejutan') && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  // paket P3 (owner 27 Nov 2026, A4): peringatan uang — dihitung peringatan-logika (owner saja, butuh angka uang) dan diteruskan app.js lewat lokal.peringatan
  (lokal && Array.isArray(lokal.peringatan) ? lokal.peringatan : []).forEach((p) => { if (p && SS_JENIS_PERINGATAN.indexOf(p.jenis) >= 0 && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  // paket P6 (owner 27 Nov 2026, A119 + A82): selisih laci berulang & belum dijelaskan — laci-logika lewat lokal.peringatan (owner saja)
  (lokal && Array.isArray(lokal.peringatan) ? lokal.peringatan : []).forEach((p) => { if (p && SS_JENIS_LACI.indexOf(p.jenis) >= 0 && /^\d{4}-\d{2}-\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });
  out.bonTanpaTanggal = bonTanpaTanggal; return out;
}
/** Jenis pengingat yang sumbernya peringatan-logika (paket P3) — sama dengan PW_JENIS. */
export const SS_JENIS_PERINGATAN = ['anggaran', 'susut', 'hpp', 'harga', 'untungKg', 'kas'];
// ---------- KUARTAL: kunci & target (Pondasi paket kedua) — SATU sumber untuk pengingat di atas, kuartal-logika (Laporan › Kuartal) & pondasi-logika (penyimpan) ----------
export const SS_KUARTAL_SUSUL = 14;
export const SS_TARGET_KUARTAL = [{ id: 'omzet', nama: 'Target omzet', satuan: 'rupiah' }, { id: 'labaBersih', nama: 'Target laba bersih', satuan: 'rupiah' }, { id: 'utangMaks', nama: 'Utang paling banyak di akhir kuartal', satuan: 'rupiah' }];
/** 'YYYY-MM-DD' / 'YYYY-MM' → 'YYYY-K1'…'YYYY-K4' (K1 = Jan–Mar). */
export const ssKuartalKey = (iso) => String(iso).slice(0, 4) + '-K' + (Math.floor((Number(String(iso).slice(5, 7)) - 1) / 3) + 1);
/** Geser n kuartal (negatif = mundur), melewati pergantian tahun. */
export const ssKuartalGeser = (key, n) => { const i = Number(String(key).slice(0, 4)) * 4 + (Number(String(key).slice(6, 7)) - 1) + n; return Math.floor(i / 4) + '-K' + ((i % 4 + 4) % 4 + 1); };
/** Hari pertama kuartal: 'YYYY-K4' → 'YYYY-10-01'. */
export const ssKuartalAwal = (key) => String(key).slice(0, 4) + '-' + String((Number(String(key).slice(6, 7)) - 1) * 3 + 1).padStart(2, '0') + '-01';
export const ssKuartalNama = (key) => 'K' + String(key).slice(6, 7) + ' ' + String(key).slice(0, 4);
/** Target owner satu kuartal dari aturanToko/pondasi.targetKuartal[key]: { omzet, labaBersih, utangMaks (0 = belum diisi), ada }. Baca saja. */
export function ssTargetKuartal(key) {
  const d = cacheMentah('aturan').find((x) => String(x.id) === 'pondasi') || {}; const t = (d.targetKuartal && typeof d.targetKuartal === 'object' && d.targetKuartal[key]) || {}; const out = { key, ada: false };
  SS_TARGET_KUARTAL.forEach((x) => { const n = Number(t[x.id]); out[x.id] = isFinite(n) && n > 0 ? Math.round(n) : 0; if (out[x.id] > 0) out.ada = true; });
  return out;
}
/** Semua pengingat + keadaannya (selesai / ditunda / WA hari ini) menurut aturan owner; kalender −3 … +10 hari. */
export function ssPengingat(kini, lokal, hariKe) {
  const iso = hariIniIso(kini); const A = ssAtur('pengingat'); const keadaan = {}; cacheMentah('pengingat').forEach((k) => { keadaan[String(k.id)] = k; }); const H = hariKe === undefined || hariKe === null ? 0 : Number(hariKe);
  const sumber = ssSumberPengingat(kini, lokal).map((p) => { const k = keadaan[p.id] || {}; const tunda = Number(k.tundaHari) || 0; const sisa = ssHariKe(p.jatuh) - ssHariKe(iso) + tunda; const jk = SS_JENIS_PENGINGAT.find((j) => j.id === p.jenis);
    return Object.assign({}, p, { selesai: k.status === 'selesai', catatan: k.catatan || '', tunda, tundaKali: Number(k.tundaKali) || 0, waHari: k.waTanggal === iso, sisa, nyala: A.nyala[p.jenis] !== false, hariSebelum: p.hariSebelum !== undefined && p.hariSebelum !== null && isFinite(Number(p.hariSebelum)) ? Number(p.hariSebelum) : Number(A[jk.kunci]) || 0,   // patuh & kemasan: hari sebelum dibawa sumbernya (per butir / setelan label)
      ke: A.ke[p.jenis] || ['Owner'],
      sisaTeks: (sisa < 0 ? 'lewat ' + (-sisa) + ' hari' : sisa === 0 ? 'hari ini' : sisa + ' hari lagi') + (tunda ? ' · ditunda ' + tunda + ' hari' : ''), jatuhEfektif: ssTambahHari(p.jatuh, tunda) }); });
  const aktif = sumber.filter((p) => p.nyala && !p.selesai && p.sisa <= p.hariSebelum).sort((a, b) => a.sisa - b.sisa || b.n - a.n);
  const lewat = aktif.filter((p) => p.sisa < 0), hariIni = aktif.filter((p) => p.sisa === 0), segera = aktif.filter((p) => p.sisa > 0);
  const kalender = []; for (let h = -3; h <= 10; h++) { const t = ssTambahHari(iso, h); const di = sumber.filter((p) => p.nyala && !p.selesai && p.sisa === h); kalender.push({ iso: t, h, tgl: String(parseInt(t.slice(8, 10), 10)), nm: ssHariNama(t), n: di.length, lewat: h < 0 && di.length > 0, ini: h === 0, aktif: h === H }); }
  const hariDaftar = sumber.filter((p) => p.nyala && !p.selesai && p.sisa === H);
  return { sumber, aktif, lewat, hariIni, segera, kalender, hariKe: H, hariDaftar, hariJudul: (H === 0 ? 'Hari ini' : H < 0 ? tanggalPendek(ssTambahHari(iso, H)) + ' (lewat)' : tanggalPendek(ssTambahHari(iso, H))) + ': ' + (hariDaftar.length ? hariDaftar.length + ' pengingat' : 'tidak ada'),
    ringkas: aktif.length ? lewat.length + ' lewat · ' + hariIni.length + ' hari ini · ' + segera.length + ' segera' + (lewat.some((p) => p.jenis === 'bon') ? ' · bon pemasok lewat ' + RP(lewat.filter((p) => p.jenis === 'bon').reduce((a, p) => a + p.n, 0)) : '') : 'Tidak ada pengingat — semua beres',
    aturan: SS_JENIS_PENGINGAT.map((j) => ({ id: j.id, nama: j.nama, nyala: A.nyala[j.id] !== false, hari: Number(A[j.kunci]) || 0, ke: A.ke[j.id] || [], sumber: sumber.filter((p) => p.jenis === j.id && !p.selesai).length, ket: (A.nyala[j.id] !== false ? (SS_HARI_DI_SUMBER[j.id] || 'ingatkan ' + (Number(A[j.kunci]) || 0) + ' hari sebelum') : 'mati') + ' · ke ' + (A.ke[j.id] || []).join(' & ') })), atur: A, bonTanpaTanggal: sumber.bonTanpaTanggal || 0 };
}
// ---------- CEK MINGGUAN TIMBANGAN & GUDANG (paket KPI laba, owner 24 Nov 2026, butir 14) ----------
// Owner 24 Nov: "Ben juga dari tablet" → koleksi BARU cekGudang (rules v19: owner || stafCekGudang(ben), atas nama penulisnya, kolom dibatasi; ubah & hapus owner).
// Satu dokumen per cek (tambah-saja). Tiap hal dijawab beres / ada masalah; ada masalah = catatan wajib. Bukan uang, bukan stok.
export const SS_CEK_GUDANG = [['timbangan', 'Timbangan akurat', 'timbangan', 'dicek dengan anak timbang / beras 1 kg yang sudah pasti'], ['palet', 'Palet utuh, karung tidak menyentuh lantai & dinding', 'palet', ''],
  ['bocor', 'Tidak ada bocor (atap, karung)', 'bocor', ''], ['lembap', 'Gudang kering, tidak lembap', 'kelembapan', ''], ['kutu', 'Tidak ada kutu / hama', 'kutu', '']].map((c) => ({ id: c[0], nama: c[1], pendek: c[2], ket: c[3] }));
export const SS_CEK_KOLOM = ['id', 'tanggal', 'jam', 'minggu', 'cek', 'catatan'];   // = kolom isi stafCekGudang rules v19 (+ kolom atribusi penulis pusat)
export const SS_CEK_CATATAN_MAKS = 160;
/** Keadaan cek: terakhir (dokumen terbaru), jatuh (terakhir + tiap hari; belum pernah = hari ini), riwayat 8 terakhir dengan hal yang bermasalah. Dibaca owner & tablet. */
export function ssCekGudang(kini) {
  const iso = hariIniIso(kini); const A = ssAtur('pengingat'); const tiap = Number(A.gudangTiap) || 7;
  const semua = cacheMentah('cekGudang').filter((d) => d && /^\d{4}-\d{2}-\d{2}$/.test(String(d.tanggal || ''))).slice().sort((a, b) => String(b.tanggal + ' ' + (b.jam || '')).localeCompare(String(a.tanggal + ' ' + (a.jam || ''))) || String(b.id).localeCompare(String(a.id)));
  const terakhir = semua[0] || null; const jatuh = terakhir ? ssTambahHari(terakhir.tanggal, tiap) : iso; const sisa = ssHariKe(jatuh) - ssHariKe(iso);
  const riwayat = semua.slice(0, 8).map((d) => { const c = d.cek || {}; const masalah = SS_CEK_GUDANG.filter((x) => c[x.id] === false).map((x) => x.pendek); return { id: String(d.id), tanggal: d.tanggal, jam: d.jam || '', oleh: d.oleh || '', masalah, catatan: d.catatan || '' }; });
  return { iso, tiap, terakhir: terakhir ? riwayat[0] : null, jatuh, sisa, perlu: sisa <= 0, riwayat, teks: !terakhir ? 'Belum pernah dicek — cek hari ini' : sisa < 0 ? 'Lewat ' + (-sisa) + ' hari (terakhir ' + tanggalPendek(terakhir.tanggal) + ')' : sisa === 0 ? 'Waktunya hari ini (terakhir ' + tanggalPendek(terakhir.tanggal) + ')' : 'Berikutnya ' + tanggalPendek(jatuh) + ' · ' + sisa + ' hari lagi' };
}
/** Simpan satu cek: cek = { hal: true (beres) | false (ada masalah) } — kelima hal WAJIB dijawab; ada masalah → catatan wajib (apa & di mana). */
export function susunCekGudang(cek, catatan, w, kini) {
  const C = {}; let kurang = 0; SS_CEK_GUDANG.forEach((x) => { const v = cek ? cek[x.id] : undefined; if (v === true || v === false) C[x.id] = v; else kurang += 1; });
  if (kurang) return { tolak: 'Jawab dulu kelima hal (beres / ada masalah) — ' + kurang + ' belum dijawab' };
  const cat = String(catatan || '').trim(); const masalah = SS_CEK_GUDANG.filter((x) => C[x.id] === false);
  if (masalah.length && cat.length < 5) return { tolak: 'Ada masalah (' + masalah.map((x) => x.pendek).join(', ') + ') — tulis catatannya dulu: apa & di mana' };
  if (cat.length > SS_CEK_CATATAN_MAKS) return { tolak: 'Catatan paling panjang ' + SS_CEK_CATATAN_MAKS + ' huruf' };
  const G = ssCekGudang(kini || new Date(w.kini));
  const data = { id: 'cg-' + w.tanggal + '-' + String(w.idUnik()).replace(/[^0-9a-z]/gi, '').slice(-10), tanggal: w.tanggal, jam: w.jam, minggu: G.jatuh, cek: C, catatan: cat };
  return { dokumen: [{ koleksi: 'cekGudang', data }], patch: { cekG: null, kabar: 'Cek timbangan & gudang tersimpan' + (masalah.length ? ' — ' + masalah.length + ' masalah dicatat: ' + masalah.map((x) => x.pendek).join(', ') : ' — semua beres') + ' · berikutnya ' + tanggalPendek(ssTambahHari(w.tanggal, G.tiap)), kabarAwas: masalah.length > 0 } };
}
const ssDokPengingat = (p, w, tambahan) => ({ koleksi: 'pengingat', data: Object.assign({ id: p.id, jenis: p.jenis, kunci: p.kunci, jatuh: p.jatuh, teks: p.teks, tanggal: w.tanggal, jam: w.jam, status: 'tunda', catatan: p.catatan || '', tundaHari: p.tunda || 0, tundaKali: p.tundaKali || 0 }, tambahan) });
export function susunSelesaiPengingat(p, catatan, w) {
  if (!p) return { tolak: 'Pilih pengingatnya' }; if (p.jenis === 'gudang') return { tolak: 'Cek gudang diselesaikan dengan mengisi kelima halnya — tombol SIMPAN CEK di bawah' }; if (p.selesai) return { tolak: 'Sudah ditandai selesai' }; if (p.sisa < 0 && ssKosong(catatan)) return { tolak: 'Pengingat yang sudah lewat butuh catatan: apa yang terjadi?' };
  return { dokumen: [ssDokPengingat(p, w, { status: 'selesai', catatan: String(catatan || '').trim().slice(0, 80) })], patch: { kabar: p.jenis === 'bon' ? 'Ditandai selesai — pembayarannya sendiri dicatat di bon pemasok (Harga & Pemasok → Bon pemasok)' : p.jenis === 'janji' ? 'Ditandai selesai — pembayarannya dicatat lewat Pelanggan → Bon' : 'Ditandai selesai', kabarAwas: false } };
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

// ==================== BUKU PEGANGAN (Pondasi paket kedua C, owner 24 Nov 2026; rules v20: aturanToko/bukuPegangan terbaca ben & karyawan, tulis owner) ====================
// Aturan kerja tertulis toko: owner menulis bab (judul · isi · untuk siapa) di Menu › Toko ini › Buku pegangan; staf MEMBACANYA di tablet. Satu dokumen,
// bab berurutan. Bukan uang, bukan stok. Tidak ada tanda "sudah dibaca" (itu butuh tulisan staf — tidak dibuka rules v20).
export const SS_PEGANGAN_ID = 'bukuPegangan';
export const SS_PEGANGAN_UNTUK = [['semua', 'Semua'], ['ben', 'Penjaga laci'], ['karyawan', 'Karyawan']];
export const SS_PEGANGAN_MAKS = { bab: 40, judul: 80, isi: 2000 };
const ssPeganganDok = () => cacheMentah('aturan').find((d) => d && String(d.id) === SS_PEGANGAN_ID) || null;
/** Buku pegangan yang tersimpan: { ada, n, bab: [{ id, judul, isi, untuk, untukNama }], tanggal, jam, teks }. Bab tanpa judul dibuang; `untuk` tak dikenal = semua. */
export function ssPegangan() {
  const d = ssPeganganDok();
  const bab = (d && Array.isArray(d.bab) ? d.bab : []).filter((b) => b && String(b.judul || '').trim()).map((b) => { const untuk = SS_PEGANGAN_UNTUK.some((u) => u[0] === b.untuk) ? b.untuk : 'semua';
    return { id: String(b.id || ''), judul: String(b.judul).trim(), isi: String(b.isi || ''), untuk, untukNama: SS_PEGANGAN_UNTUK.find((u) => u[0] === untuk)[1] }; });
  return { ada: bab.length > 0, n: bab.length, bab, tanggal: d ? String(d.tanggal || '') : '', jam: d ? String(d.jam || '') : '',
    teks: bab.length ? bab.length + ' bab' + (d && d.tanggal ? ' · terakhir diubah ' + tanggalPendek(d.tanggal) : '') : 'belum ada isinya' };
}
/** Bab yang tampil untuk satu peran: owner semua; ben / karyawan = bab "semua" + bab untuk perannya. */
export function ssPeganganUntuk(peran) { const B = ssPegangan().bab; return peran === 'owner' ? B : B.filter((b) => b.untuk === 'semua' || b.untuk === peran); }
/** Draf lembar tulis: bab yang ada (id) atau bab baru kosong. */
export function ssDrafBab(id) { const b = id ? ssPegangan().bab.find((x) => x.id === id) : null; return b ? { id: b.id, judul: b.judul, isi: b.isi, untuk: b.untuk } : { id: '', judul: '', isi: '', untuk: 'semua' }; }
// SATU dokumen memuat bab DAN pembagian tugas (paket keempat, 25 Nov 2026): tiap simpan membawa keduanya utuh — menyimpan bab tidak boleh menghapus tugas, dan sebaliknya.
const ssDokPegangan = (bab, tugas, w) => ({ koleksi: 'aturanToko', data: { id: SS_PEGANGAN_ID, bab: bab.map((b) => ({ id: b.id, judul: b.judul, isi: b.isi, untuk: b.untuk })),
  tugas: tugas.map((t) => ({ id: t.id, urusan: t.urusan, pegang: t.pegang, ganti: t.ganti })), tanggal: w.tanggal, jam: w.jam } });
const ssSimpanPegangan = (bab, w, kabar) => ({ dokumen: [ssDokPegangan(bab, ssTugas().baris, w)],
  patch: { bpgDraf: null, yakinBpg: null, kabar, kabarAwas: false } });
/** Tambah bab baru (id kosong) atau ubah bab yang ada. Judul 3–80 huruf & tidak kembar, isi 5–2.000 huruf, untuk siapa wajib dipilih, paling banyak 40 bab. */
export function susunBabPegangan(d, w) {
  const judul = String((d && d.judul) || '').trim(), isi = String((d && d.isi) || '').replace(/\r\n/g, '\n').trim(), untuk = d ? d.untuk : ''; const M = SS_PEGANGAN_MAKS; const bab = ssPegangan().bab.slice();
  if (judul.length < 3) return { tolak: 'Judul bab paling sedikit 3 huruf' };
  if (judul.length > M.judul) return { tolak: 'Judul bab paling panjang ' + M.judul + ' huruf' };
  if (isi.length < 5) return { tolak: 'Isi bab belum ditulis' };
  if (isi.length > M.isi) return { tolak: 'Isi bab paling panjang ' + M.isi + ' huruf — pecah jadi dua bab' };
  if (!SS_PEGANGAN_UNTUK.some((u) => u[0] === untuk)) return { tolak: 'Pilih bab ini untuk siapa' };
  const id = String((d && d.id) || ''); const i = id ? bab.findIndex((b) => b.id === id) : -1;
  if (id && i < 0) return { tolak: 'Bab yang diubah sudah tidak ada — tutup lalu buka lagi' };
  if (i < 0 && bab.length >= M.bab) return { tolak: 'Paling banyak ' + M.bab + ' bab — gabungkan atau hapus yang tidak dipakai' };
  if (bab.some((b, k) => k !== i && b.judul.toLowerCase() === judul.toLowerCase())) return { tolak: 'Sudah ada bab berjudul "' + judul + '"' };
  if (i >= 0 && bab[i].judul === judul && bab[i].isi === isi && bab[i].untuk === untuk) return { tolak: 'Tidak ada yang diubah' };
  const b = { id: i >= 0 ? id : 'bab-' + w.idUnik(), judul, isi, untuk }; if (i >= 0) bab[i] = b; else bab.push(b);
  return ssSimpanPegangan(bab, w, 'Bab "' + judul + '" ' + (i >= 0 ? 'diubah' : 'ditambahkan') + ' — terbaca di tablet ' + SS_PEGANGAN_UNTUK.find((u) => u[0] === untuk)[1].toLowerCase());
}
/** Hapus satu bab. */
export function susunHapusBab(id, w) {
  const bab = ssPegangan().bab; const b = bab.find((x) => x.id === String(id)); if (!b) return { tolak: 'Bab itu sudah tidak ada' };
  return ssSimpanPegangan(bab.filter((x) => x.id !== b.id), w, 'Bab "' + b.judul + '" dihapus');
}
/** Geser urutan satu bab: arah −1 = naik, +1 = turun. Di ujung = ditolak dengan kalimat. */
export function susunGeserBab(id, arah, w) {
  const bab = ssPegangan().bab.slice(); const i = bab.findIndex((x) => x.id === String(id)); const j = i + (Number(arah) < 0 ? -1 : 1);
  if (i < 0) return { tolak: 'Bab itu sudah tidak ada' }; if (j < 0 || j >= bab.length) return { tolak: 'Bab itu sudah di ' + (j < 0 ? 'paling atas' : 'paling bawah') };
  const t = bab[i]; bab[i] = bab[j]; bab[j] = t;
  return ssSimpanPegangan(bab, w, 'Urutan bab diubah — "' + t.judul + '" sekarang nomor ' + (j + 1));
}

// ==================== PEMBAGIAN TUGAS (Pondasi paket keempat, owner 25 Nov 2026 — pilar "organisasi": tim & hirarki) ====================
// Siapa memegang urusan apa dan siapa penggantinya. Owner menulis; Penjaga laci & karyawan membaca di tablet. Disimpan di dokumen buku pegangan yang SAMA
// (kolom `tugas`) — dokumen itu sudah terbaca staf (rules v20), jadi tanpa rules baru. Bukan uang, bukan stok, bukan hak akses (akses tetap di Peran).
export const SS_TUGAS_MAKS = { baris: 30, urusan: 60, nama: 40 };
/** Pembagian tugas tersimpan: { ada, n, baris: [{ id, urusan, pegang, ganti }], nTanpaGanti, tanpaGanti: [urusan], bebanTerbanyak { nama, n } | null, teks }. */
export function ssTugas() {
  const d = ssPeganganDok();
  const baris = (d && Array.isArray(d.tugas) ? d.tugas : []).filter((t) => t && String(t.urusan || '').trim() && String(t.pegang || '').trim())
    .map((t) => ({ id: String(t.id || ''), urusan: String(t.urusan).trim(), pegang: String(t.pegang).trim(), ganti: String(t.ganti || '').trim() }));
  const tanpa = baris.filter((t) => !t.ganti); const per = {}; baris.forEach((t) => { const k = t.pegang.toLowerCase(); per[k] = per[k] || { nama: t.pegang, n: 0 }; per[k].n += 1; });
  const beban = Object.keys(per).map((k) => per[k]).sort((a, b) => b.n - a.n || a.nama.localeCompare(b.nama))[0] || null;
  return { ada: baris.length > 0, n: baris.length, baris, nTanpaGanti: tanpa.length, tanpaGanti: tanpa.map((t) => t.urusan), bebanTerbanyak: beban,
    teks: baris.length ? baris.length + ' urusan' + (tanpa.length ? ' · ' + tanpa.length + ' belum punya pengganti' : ' · semua punya pengganti') : 'belum ditulis' };
}
export function ssDrafTugas(id) { const t = id ? ssTugas().baris.find((x) => x.id === id) : null; return t ? { id: t.id, urusan: t.urusan, pegang: t.pegang, ganti: t.ganti } : { id: '', urusan: '', pegang: '', ganti: '' }; }
const ssSimpanTugas = (baris, w, kabar) => ({ dokumen: [ssDokPegangan(ssPegangan().bab, baris, w)], patch: { tgsDraf: null, yakinTgs: null, kabar, kabarAwas: false } });
/** Tambah / ubah satu urusan. Urusan 3–60 huruf & tidak kembar, pemegang wajib (2–40 huruf), pengganti boleh kosong (DISEBUT belum ada) tapi tidak boleh orang yang sama. */
export function susunTugas(d, w) {
  const urusan = String((d && d.urusan) || '').trim(), pegang = String((d && d.pegang) || '').trim(), gantiT = String((d && d.ganti) || '').trim(); const M = SS_TUGAS_MAKS; const baris = ssTugas().baris.slice();
  if (urusan.length < 3) return { tolak: 'Urusan paling sedikit 3 huruf — mis. Terima barang dari supir' };
  if (urusan.length > M.urusan) return { tolak: 'Urusan paling panjang ' + M.urusan + ' huruf' };
  if (pegang.length < 2) return { tolak: 'Tulis siapa yang memegang urusan ini' };
  if (pegang.length > M.nama || gantiT.length > M.nama) return { tolak: 'Nama paling panjang ' + M.nama + ' huruf' };
  if (gantiT && gantiT.toLowerCase() === pegang.toLowerCase()) return { tolak: 'Pengganti harus orang lain — kosongkan kalau memang belum ada' };
  const id = String((d && d.id) || ''); const i = id ? baris.findIndex((t) => t.id === id) : -1;
  if (id && i < 0) return { tolak: 'Urusan yang diubah sudah tidak ada — tutup lalu buka lagi' };
  if (i < 0 && baris.length >= M.baris) return { tolak: 'Paling banyak ' + M.baris + ' urusan — gabungkan yang mirip' };
  if (baris.some((t, k) => k !== i && t.urusan.toLowerCase() === urusan.toLowerCase())) return { tolak: 'Urusan "' + urusan + '" sudah ada' };
  if (i >= 0 && baris[i].urusan === urusan && baris[i].pegang === pegang && baris[i].ganti === gantiT) return { tolak: 'Tidak ada yang diubah' };
  const t = { id: i >= 0 ? id : 'tgs-' + w.idUnik(), urusan, pegang, ganti: gantiT }; if (i >= 0) baris[i] = t; else baris.push(t);
  return ssSimpanTugas(baris, w, 'Urusan "' + urusan + '" ' + (i >= 0 ? 'diubah' : 'ditambahkan') + ' — dipegang ' + pegang + (gantiT ? ', pengganti ' + gantiT : ', BELUM ada pengganti'));
}
export function susunHapusTugas(id, w) {
  const baris = ssTugas().baris; const t = baris.find((x) => x.id === String(id)); if (!t) return { tolak: 'Urusan itu sudah tidak ada' };
  return ssSimpanTugas(baris.filter((x) => x.id !== t.id), w, 'Urusan "' + t.urusan + '" dihapus');
}

// ==================== CATATAN PERCOBAAN (Pondasi paket keempat, owner 25 Nov 2026 — "R&D" di catatan Pondasi bisnis) ====================
// Owner menulis APA yang dicoba, untuk merek mana (kosong = seluruh toko), mulai & selesai. Angkanya TIDAK disimpan di sini: Laporan › Pondasi mengukurnya
// tiap dibuka dari nota (pdPercobaan → merekRentang). Satu dokumen aturanToko/percobaan, owner saja (staf tidak membacanya — tidak masuk daftar baca rules).
export const SS_PERCOBAAN_ID = 'percobaan';
export const SS_PERCOBAAN_MAKS = { n: 30, judul: 80, teks: 600, merek: 60 };
// tanggal yang tidak ada (31 Feb) → Date tidak sah: toISOString MELEMPAR, jadi diperiksa dulu
const ssIsoSah = (t) => { if (!/^\d{4}-\d{2}-\d{2}$/.test(String(t || ''))) return false; const d = new Date(t + 'T00:00:00Z'); return !isNaN(d.getTime()) && d.toISOString().slice(0, 10) === t; };
/** Percobaan tersimpan, yang mulai paling baru dulu: { ada, n, daftar: [{ id, judul, merek, mulai, selesai, catatan, kesimpulan }] }. */
export function ssPercobaan() {
  const d = cacheMentah('aturan').find((x) => x && String(x.id) === SS_PERCOBAAN_ID) || null;
  const daftar = (d && Array.isArray(d.daftar) ? d.daftar : []).filter((x) => x && String(x.judul || '').trim() && ssIsoSah(x.mulai))
    .map((x) => ({ id: String(x.id || ''), judul: String(x.judul).trim(), merek: String(x.merek || '').trim(), mulai: String(x.mulai), selesai: ssIsoSah(x.selesai) ? String(x.selesai) : '', catatan: String(x.catatan || ''), kesimpulan: String(x.kesimpulan || '') }))
    .sort((a, b) => b.mulai.localeCompare(a.mulai) || a.judul.localeCompare(b.judul));
  return { ada: daftar.length > 0, n: daftar.length, daftar };
}
export function ssDrafPercobaan(id, hariIni) { const x = id ? ssPercobaan().daftar.find((y) => y.id === id) : null;
  return x ? { id: x.id, judul: x.judul, merek: x.merek, mulai: x.mulai, selesai: x.selesai, catatan: x.catatan, kesimpulan: x.kesimpulan } : { id: '', judul: '', merek: '', mulai: String(hariIni || ''), selesai: '', catatan: '', kesimpulan: '' }; }
const ssSimpanPercobaan = (daftar, w, kabar) => ({ dokumen: [{ koleksi: 'aturanToko', data: { id: SS_PERCOBAAN_ID, daftar: daftar.map((x) => ({ id: x.id, judul: x.judul, merek: x.merek, mulai: x.mulai, selesai: x.selesai, catatan: x.catatan, kesimpulan: x.kesimpulan })), tanggal: w.tanggal, jam: w.jam } }],
  patch: { pcDraf: null, yakinPc: null, kabar, kabarAwas: false } });
/** Tambah / ubah satu percobaan. Judul 3–80 huruf & tidak kembar; mulai wajib (tanggal sah); selesai kosong = masih berjalan, kalau diisi tidak boleh sebelum mulai. */
export function susunPercobaan(d, w) {
  const M = SS_PERCOBAAN_MAKS; const judul = String((d && d.judul) || '').trim(), merek = String((d && d.merek) || '').trim(), mulai = String((d && d.mulai) || '').trim(), selesai = String((d && d.selesai) || '').trim();
  const catatan = String((d && d.catatan) || '').replace(/\r\n/g, '\n').trim(), kesimpulan = String((d && d.kesimpulan) || '').replace(/\r\n/g, '\n').trim(); const daftar = ssPercobaan().daftar.slice();
  if (judul.length < 3) return { tolak: 'Tulis apa yang dicoba — paling sedikit 3 huruf' };
  if (judul.length > M.judul) return { tolak: 'Judul paling panjang ' + M.judul + ' huruf' };
  if (merek.length > M.merek) return { tolak: 'Nama merek terlalu panjang' };
  if (!ssIsoSah(mulai)) return { tolak: 'Tanggal mulai belum diisi' };
  if (selesai && !ssIsoSah(selesai)) return { tolak: 'Tanggal selesai tidak terbaca — kosongkan kalau masih berjalan' };
  if (selesai && selesai < mulai) return { tolak: 'Tanggal selesai tidak boleh sebelum tanggal mulai' };
  if (catatan.length > M.teks || kesimpulan.length > M.teks) return { tolak: 'Catatan & kesimpulan paling panjang ' + M.teks + ' huruf' };
  const id = String((d && d.id) || ''); const i = id ? daftar.findIndex((x) => x.id === id) : -1;
  if (id && i < 0) return { tolak: 'Percobaan yang diubah sudah tidak ada — tutup lalu buka lagi' };
  if (i < 0 && daftar.length >= M.n) return { tolak: 'Paling banyak ' + M.n + ' percobaan — hapus yang sudah tidak dipakai' };
  if (daftar.some((x, k) => k !== i && x.judul.toLowerCase() === judul.toLowerCase())) return { tolak: 'Sudah ada percobaan berjudul "' + judul + '"' };
  const baru = { id: i >= 0 ? id : 'pc-' + w.idUnik(), judul, merek, mulai, selesai, catatan, kesimpulan };
  if (i >= 0 && ['judul', 'merek', 'mulai', 'selesai', 'catatan', 'kesimpulan'].every((k) => daftar[i][k] === baru[k])) return { tolak: 'Tidak ada yang diubah' };
  if (i >= 0) daftar[i] = baru; else daftar.push(baru);
  return ssSimpanPercobaan(daftar, w, 'Percobaan "' + judul + '" ' + (i >= 0 ? 'diubah' : 'dicatat') + ' — ' + (merek || 'seluruh toko') + ', mulai ' + tanggalPendek(mulai) + (selesai ? ' sampai ' + tanggalPendek(selesai) : ', masih berjalan'));
}
export function susunHapusPercobaan(id, w) {
  const daftar = ssPercobaan().daftar; const x = daftar.find((y) => y.id === String(id)); if (!x) return { tolak: 'Percobaan itu sudah tidak ada' };
  return ssSimpanPercobaan(daftar.filter((y) => y.id !== x.id), w, 'Percobaan "' + x.judul + '" dihapus (nota & angkanya tidak tersentuh)');
}

// ==================== PIHAK YANG BERKEPENTINGAN & TINJAUAN BULANAN (Pondasi paket ketujuh, owner 25 Nov 2026 — "stakeholders" & "CGC" di catatan Pondasi bisnis) ====================
// Keduanya catatan OWNER SAJA di aturanToko (tidak masuk daftar baca staf): `pihak` = catatan per pihak (apa yang mereka harapkan dari toko, apa yang toko
// butuhkan dari mereka) — daftar pihaknya sendiri disusun Laporan › Pondasi dari data (pdPihak); `tinjauan` = satu catatan per bulan + potret lampu saat ditulis.
export const SS_PIHAK_ID = 'pihak';
export const SS_PIHAK_JENIS = [['pemasok', 'Pemasok'], ['pembeli', 'Pembeli'], ['staf', 'Staf'], ['uang', 'Bank & pemberi pinjaman'], ['tempat', 'Pemilik tempat & lingkungan'], ['lain', 'Lain-lain']];
export const SS_PIHAK_MAKS = { n: 80, nama: 60, teks: 300 };
/** Catatan pihak tersimpan: { n, daftar: [{ kunci, jenis, nama, harap, butuh, manual }] } — manual = pihak yang ditambahkan owner sendiri (bukan dari data). */
export function ssPihak() {
  const d = cacheMentah('aturan').find((x) => x && String(x.id) === SS_PIHAK_ID) || null;
  const daftar = (d && Array.isArray(d.daftar) ? d.daftar : []).filter((x) => x && String(x.kunci || '') && String(x.nama || '').trim())
    .map((x) => ({ kunci: String(x.kunci), jenis: SS_PIHAK_JENIS.some((j) => j[0] === x.jenis) ? x.jenis : 'lain', nama: String(x.nama).trim(), harap: String(x.harap || ''), butuh: String(x.butuh || ''), manual: !!x.manual }));
  return { n: daftar.length, daftar };
}
const ssSimpanPihak = (daftar, w, kabar) => ({ dokumen: [{ koleksi: 'aturanToko', data: { id: SS_PIHAK_ID, daftar: daftar.map((x) => ({ kunci: x.kunci, jenis: x.jenis, nama: x.nama, harap: x.harap, butuh: x.butuh, manual: !!x.manual })), tanggal: w.tanggal, jam: w.jam } }],
  patch: { phDraf: null, yakinPh: null, kabar, kabarAwas: false } });
/** Simpan catatan satu pihak. kunci kosong = pihak BARU yang ditambahkan owner (manual). Pihak dari data yang kedua catatannya dikosongkan = catatannya dihapus. */
export function susunPihak(d, w) {
  const M = SS_PIHAK_MAKS; const nama = String((d && d.nama) || '').trim(), jenis = d ? d.jenis : '', harap = String((d && d.harap) || '').replace(/\r\n/g, '\n').trim(), butuh = String((d && d.butuh) || '').replace(/\r\n/g, '\n').trim();
  const daftar = ssPihak().daftar.slice(); const kunci = String((d && d.kunci) || ''); const i = kunci ? daftar.findIndex((x) => x.kunci === kunci) : -1; const baru = !kunci;
  if (nama.length < 2) return { tolak: 'Tulis nama pihaknya' };
  if (nama.length > M.nama) return { tolak: 'Nama paling panjang ' + M.nama + ' huruf' };
  if (!SS_PIHAK_JENIS.some((j) => j[0] === jenis)) return { tolak: 'Pilih jenis pihaknya' };
  if (harap.length > M.teks || butuh.length > M.teks) return { tolak: 'Tiap catatan paling panjang ' + M.teks + ' huruf' };
  if (baru && daftar.some((x) => x.manual && x.nama.toLowerCase() === nama.toLowerCase())) return { tolak: '"' + nama + '" sudah ada di daftar' };
  const manual = baru || (i >= 0 && daftar[i].manual);
  if (!manual && !harap && !butuh) { if (i < 0) return { tolak: 'Belum ada yang ditulis' }; daftar.splice(i, 1); return ssSimpanPihak(daftar, w, 'Catatan untuk ' + nama + ' dikosongkan'); }
  if (i < 0 && daftar.length >= M.n) return { tolak: 'Paling banyak ' + M.n + ' pihak bercatatan' };
  const x = { kunci: baru ? 'manual|' + w.idUnik() : kunci, jenis, nama, harap, butuh, manual };
  if (i >= 0 && ['jenis', 'nama', 'harap', 'butuh'].every((k) => daftar[i][k] === x[k])) return { tolak: 'Tidak ada yang diubah' };
  if (i >= 0) daftar[i] = x; else daftar.push(x);
  return ssSimpanPihak(daftar, w, (baru ? 'Pihak "' + nama + '" ditambahkan' : 'Catatan untuk ' + nama + ' tersimpan'));
}
/** Hapus pihak yang ditambahkan owner sendiri. Pihak dari data tidak bisa dihapus dari sini (ia muncul selama ada di data) — catatannya dikosongkan lewat susunPihak. */
export function susunHapusPihak(kunci, w) {
  const daftar = ssPihak().daftar; const x = daftar.find((y) => y.kunci === String(kunci)); if (!x) return { tolak: 'Pihak itu sudah tidak ada' };
  if (!x.manual) return { tolak: x.nama + ' muncul dari data toko — kosongkan catatannya saja' };
  return ssSimpanPihak(daftar.filter((y) => y.kunci !== x.kunci), w, 'Pihak "' + x.nama + '" dihapus');
}

export const SS_TINJAUAN_ID = 'tinjauan';
export const SS_TINJAUAN_MAKS = { n: 36, teks: 800 };
export const SS_TINJAUAN_SUSUL = 14;
export const SS_WARNA_LAMPU = ['merah', 'amber', 'hijau', 'tanpa'];
/** Geser bulan 'YYYY-MM' n bulan (negatif = mundur). */
export const ssBulanGeser = (key, n) => { const i = Number(String(key).slice(0, 4)) * 12 + (Number(String(key).slice(5, 7)) - 1) + n; return Math.floor(i / 12) + '-' + String((i % 12 + 12) % 12 + 1).padStart(2, '0'); };
const ssBulanSah = (k) => /^\d{4}-(0[1-9]|1[0-2])$/.test(String(k || ''));
const ssAngkaAtauNull = (n) => (typeof n === 'number' && isFinite(n) ? Math.round(n) : null);
/** Potret yang boleh disimpan: warna tiap lampu + jumlah per warna + tiga angka hari itu (kekayaan bersih, uang toko, laba bersih 30 hari; null = belum bisa dihitung). */
export function ssPotretBersih(p) {
  if (!p || typeof p !== 'object') return null; const lampu = {}; Object.keys(p.lampu || {}).slice(0, 20).forEach((k) => { if (SS_WARNA_LAMPU.indexOf(p.lampu[k]) >= 0) lampu[String(k)] = p.lampu[k]; });
  const hitung = (w) => Object.keys(lampu).filter((k) => lampu[k] === w).length;
  return { tanggal: /^\d{4}-\d{2}-\d{2}$/.test(String(p.tanggal || '')) ? String(p.tanggal) : '', lampu, merah: hitung('merah'), amber: hitung('amber'), hijau: hitung('hijau'), tanpa: hitung('tanpa'), bersih: ssAngkaAtauNull(p.bersih), kas: ssAngkaAtauNull(p.kas), laba30: ssAngkaAtauNull(p.laba30) };
}
/** Tinjauan tersimpan, bulan terbaru dulu: { n, daftar: [{ bulan, tanggal, jam, jalan, macet, putusan, potret }] }. */
export function ssTinjauan() {
  const d = cacheMentah('aturan').find((x) => x && String(x.id) === SS_TINJAUAN_ID) || null;
  const daftar = (d && Array.isArray(d.daftar) ? d.daftar : []).filter((x) => x && ssBulanSah(x.bulan) && String(x.putusan || '').trim())
    .map((x) => ({ bulan: String(x.bulan), tanggal: String(x.tanggal || ''), jam: String(x.jam || ''), jalan: String(x.jalan || ''), macet: String(x.macet || ''), putusan: String(x.putusan).trim(), potret: ssPotretBersih(x.potret) }))
    .sort((a, b) => b.bulan.localeCompare(a.bulan));
  return { n: daftar.length, daftar };
}
export function ssTinjauanBulan(key) { return ssTinjauan().daftar.find((x) => x.bulan === String(key)) || null; }
const ssSimpanTinjauan = (daftar, w, kabar) => ({ dokumen: [{ koleksi: 'aturanToko', data: { id: SS_TINJAUAN_ID, daftar: daftar.map((x) => ({ bulan: x.bulan, tanggal: x.tanggal, jam: x.jam, jalan: x.jalan, macet: x.macet, putusan: x.putusan, potret: x.potret })), tanggal: w.tanggal, jam: w.jam } }],
  patch: { tjDraf: null, yakinTj: null, kabar, kabarAwas: false } });
/**
 * Tulis / ubah tinjauan satu bulan. Keputusan WAJIB (≥ 3 huruf) — tinjauan tanpa keputusan hanya cerita; bulan tidak boleh di depan bulan berjalan.
 * `potret` = keadaan lampu saat ini (disusun pondasi-logika). Potret DIBEKUKAN saat tinjauan pertama kali ditulis: mengubah teksnya kemudian TIDAK mengganti
 * potret (kalau diganti, "waktu itu berapa lampu merah" ikut bergeser). Disimpan paling banyak 36 bulan terbaru.
 */
export function susunTinjauan(d, potret, w) {
  const M = SS_TINJAUAN_MAKS; const bulan = String((d && d.bulan) || ''); const rapi = (t) => String(t || '').replace(/\r\n/g, '\n').trim(); const jalan = rapi(d && d.jalan), macet = rapi(d && d.macet), putusan = rapi(d && d.putusan);
  if (!ssBulanSah(bulan)) return { tolak: 'Bulan yang ditinjau tidak dikenal' };
  if (bulan > String(w.tanggal).slice(0, 7)) return { tolak: 'Bulan itu belum berjalan' };
  if (putusan.length < 3) return { tolak: 'Tulis keputusannya — apa yang dikerjakan bulan depan' };
  if (jalan.length > M.teks || macet.length > M.teks || putusan.length > M.teks) return { tolak: 'Tiap bagian paling panjang ' + M.teks + ' huruf' };
  const daftar = ssTinjauan().daftar.slice(); const i = daftar.findIndex((x) => x.bulan === bulan);
  if (i >= 0 && daftar[i].jalan === jalan && daftar[i].macet === macet && daftar[i].putusan === putusan) return { tolak: 'Tidak ada yang diubah' };
  const x = { bulan, tanggal: i >= 0 ? daftar[i].tanggal : w.tanggal, jam: i >= 0 ? daftar[i].jam : w.jam, jalan, macet, putusan, potret: i >= 0 && daftar[i].potret ? daftar[i].potret : ssPotretBersih(potret) };
  if (i >= 0) daftar[i] = x; else daftar.push(x);
  daftar.sort((a, b) => b.bulan.localeCompare(a.bulan));
  return ssSimpanTinjauan(daftar.slice(0, M.n), w, 'Tinjauan ' + bulan.slice(5, 7) + '/' + bulan.slice(0, 4) + (i >= 0 ? ' diubah (potret lampunya tetap yang pertama)' : ' tersimpan bersama potret lampu hari ini'));
}
export function susunHapusTinjauan(bulan, w) {
  const daftar = ssTinjauan().daftar; const x = daftar.find((y) => y.bulan === String(bulan)); if (!x) return { tolak: 'Tinjauan itu sudah tidak ada' };
  return ssSimpanTinjauan(daftar.filter((y) => y.bulan !== x.bulan), w, 'Tinjauan ' + x.bulan.slice(5, 7) + '/' + x.bulan.slice(0, 4) + ' dihapus');
}
