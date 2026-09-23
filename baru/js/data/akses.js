// AKSES PER ORANG (putaran 23, "jalan A"): siapa yang masuk, perannya apa, boleh membaca & mencatat apa.
// Logika TANPA DOM & tanpa Firebase — dijaga alat-uji/uji_akses_baru.py. Dasar tiap daftar: docs/peta-hak-akses.md (§ disebut di tiap baris).
// SERVER (firestore.rules v3) yang menegakkan. Berkas ini membuat layar & penulis pusat berkata SAMA dengan rules, supaya kiriman yang
// pasti ditolak server tidak pernah dikirim (dan yang tetap ditolak server tertangkap di antre-lokal.js, tidak hilang diam).
// Keputusan owner 24 Sep: akun tanpa aksesAkun aktif = nol akses (kecuali minta didaftarkan); owner dikenali lewat EMAIL, aksesAkun tak pernah
// memberi peran owner; jalur kasir@ tetap milik kasir@ saja; satu baris jejak per kiriman bukan-owner memuat daftar dokumennya.
import { KOLEKSI } from './koleksi.js';

export const EMAIL_OWNER = 'owner@tokoberasmiqbal.web.app';
export const EMAIL_KASIR = 'kasir@tokoberasmiqbal.web.app';
// Id peran = SS_PERAN tanpa owner. UTANG (dicatat owner 24 Sep): 'ben' memakai nama orang; peran harus bernama jabatan. Data SS2 bergantung padanya.
export const PERAN_BUKAN_OWNER = ['ben', 'karyawan'];
export const NAMA_PERAN = { owner: 'Owner', ben: 'Ben (penjaga laci)', karyawan: 'Karyawan' };
export const BATAS_ACCESS_CALL = 20;   // per batch/transaksi (dokumentasi Firebase); cache dianggap TIDAK ada (keputusan owner poin 4)

// §3 — yang DIBACA bukan-owner. Koleksi utuh + setelan PER DOKUMEN (aturanToko & pengaturan bercampur tarif upah, NPWP, titik kas, PIN).
export const BACA_STAF = ['penjualan', 'piutangMutasi', 'pelangganCatatan', 'pelangganTitip', 'pesanan', 'tagihPelanggan', 'strukKeluar',
  'batchMasuk', 'produksiKemasan', 'penyesuaianStok', 'penyesuaianKemasan', 'retur', 'karantina', 'stokBahanKemasan', 'stokBahanLiteran', 'wadahLiteran', 'pindahTempat',
  'katalogHargaKarung', 'katalogHargaKemasan', 'katalogHargaLiteran', 'hargaWadah'];
export const DOK_STAF = { aturanToko: ['struk', 'pelanggan', 'pelangganKembar', 'catatStok', 'kantong', 'tempat', 'peran', 'perangkat'], pengaturan: ['tempatSimpan'] };
// §4 — CREATE bukan-owner: koleksi → peran yang boleh. Menambah peran nanti = menambah satu nama di sini DAN di daftar yang sama di firestore.rules.
export const BUAT_STAF = { penjualan: ['ben', 'karyawan'], piutangMutasi: ['ben', 'karyawan'], stokBahanLiteran: ['ben', 'karyawan'], stokBahanKemasan: ['ben', 'karyawan'],
  produksiKemasan: ['ben', 'karyawan'], pelangganCatatan: ['ben', 'karyawan'], strukKeluar: ['ben', 'karyawan'], logAktivitas: ['ben', 'karyawan'], perangkatStatus: ['ben', 'karyawan'] };
export const KREDIT_STAF = ['ben'];   // penjualan caraBayar Kredit (jualBon): ben `sendiri`, karyawan `owner`
// §5 — dua pengecualian UPDATE. Kolom atribusi ubah ikut (penulis pusat menulisnya); kolom pencipta (oleh, perangkat, lokasi) TIDAK pernah ditambah bukan-owner.
export const KOLOM_ATRIBUSI_UBAH = ['diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada'];
export const UBAH_STAF = {
  pesanan: { peran: ['ben', 'karyawan'], kolom: ['status', 'riwayatStatus', 'trxIdJual'].concat(KOLOM_ATRIBUSI_UBAH) },
  perangkatStatus: { peran: ['ben', 'karyawan'], kolom: ['id', 'nama', 'akun', 'akunUid', 'aplikasi', 'pada', 'antrean', 'gagal', 'versi', 'pemegang', 'lokasi'] },
};
export const LAYAR_STAF = ['jual', 'pelanggan', 'stok', 'menu'];
// §1 — tindakan SS2 yang DIBUKA server putaran ini, per peran. Selebihnya tertutup (hitung laci & kedatangan: §6).
export const SERVER_BUKA = { jualTunai: ['ben', 'karyawan'], jualBon: ['ben'], terimaBon: ['ben', 'karyawan'], adukan: ['ben', 'karyawan'], pelangganBaru: ['ben', 'karyawan'] };
export const KALIMAT_MINTA_OWNER = 'Perlu persetujuan owner — alurnya menyusul';

const aKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const namaPeran = (p) => NAMA_PERAN[p] || p;

/** Keadaan akun sesudah Firebase Auth menjawab. dok = isi aksesAkun/{uid} (null = belum ada). Owner HANYA lewat email. */
export function keadaanAkun(email, uid, dok) {
  const e = String(email || '').trim().toLowerCase();
  if (!uid) return { jenis: 'keluar', peran: null, nama: '', uid: '' };
  if (e === EMAIL_OWNER) return { jenis: 'owner', peran: 'owner', nama: 'Owner', uid, email: e };
  if (e === EMAIL_KASIR) return { jenis: 'kasir', peran: null, nama: 'kasir@', uid, email: e, kalimat: 'Akun kasir@ hanya untuk kasir darurat. Di sini masuk dengan akun pribadi yang didaftarkan owner.' };
  if (!dok) return { jenis: 'belum', peran: null, nama: '', uid, email: e, kalimat: 'Akun ini belum didaftarkan owner' };
  const peran = String(dok.peran || '');
  if (dok.aktif !== true) return { jenis: 'nonaktif', peran: null, nama: String(dok.nama || ''), uid, email: e, kalimat: 'Akun ini dinonaktifkan owner' };
  if (PERAN_BUKAN_OWNER.indexOf(peran) < 0) return { jenis: 'nonaktif', peran: null, nama: String(dok.nama || ''), uid, email: e, kalimat: 'Peran akun ini tidak dikenal ("' + peran + '") — minta owner memperbaikinya' };
  return { jenis: 'aktif', peran, nama: String(dok.nama || '').trim() || e, uid, email: e };
}
export const bisaBekerja = (akun) => !!akun && (akun.jenis === 'owner' || akun.jenis === 'aktif');
export const teksMasukSebagai = (akun) => (!akun || !bisaBekerja(akun) ? '' : akun.jenis === 'owner' ? 'Owner' : akun.nama + ' (' + namaPeran(akun.peran) + ')');

/** Isi permintaanAkses/{uid} yang ditulis akun yang belum terdaftar (rules: create oleh pemilik uid, kolom persis ini). */
export function susunPermintaan(akun, namaKetik, kiniIso) {
  if (!akun || akun.jenis !== 'belum') return { tolak: akun && akun.jenis === 'kasir' ? akun.kalimat : 'Akun ini tidak perlu minta didaftarkan' };
  const nama = String(namaKetik || '').trim().slice(0, 40); if (nama.length < 2) return { tolak: 'Ketik nama lu (minimal dua huruf) supaya owner tahu ini siapa' };
  return { data: { uid: akun.uid, email: akun.email, nama, pada: kiniIso } };
}

/** Pendengar per peran (Tahap 3): owner = semua koleksi.js; bukan-owner = §3 (koleksi utuh + dokumen setelan satu per satu) + aksesAkun dirinya. */
export function pendengarPeran(akun) {
  if (!bisaBekerja(akun)) return [];
  if (akun.jenis === 'owner') return KOLEKSI.map((k) => ({ nama: k.nama }));
  const out = BACA_STAF.map((n) => ({ nama: n }));
  Object.keys(DOK_STAF).forEach((n) => out.push({ nama: n, dok: DOK_STAF[n].slice() }));
  return out;
}
export const bolehLayar = (akun, layar) => bisaBekerja(akun) && (akun.jenis === 'owner' || LAYAR_STAF.indexOf(layar) >= 0);
/** Angka yang dihitung dari koleksi yang tidak didengarkan TIDAK digambar (bukan Rp0). Kembali: '' = boleh; selain itu kalimatnya. */
export function angkaBoleh(akun, koleksiDibutuhkan) {
  if (!akun || akun.jenis === 'owner') return '';
  const didengar = pendengarPeran(akun).map((p) => p.nama); const kurang = (koleksiDibutuhkan || []).filter((k) => didengar.indexOf(k) < 0);
  return kurang.length ? 'tidak termasuk hak ' + namaPeran(akun.peran) : '';
}

/** Tombol tindakan SS2 untuk akun ini. hak = nilai kisi SS2 untuk peran itu ('sendiri' | 'owner' | 'tidak'). Boleh = kisi `sendiri` DAN server membuka. */
export function tombolTindakan(akun, tindakan, hak, namaTindakan) {
  if (!akun) return { boleh: false, kalimat: 'Belum masuk' };
  if (akun.jenis === 'owner') return { boleh: true, kalimat: '' };
  if (!bisaBekerja(akun)) return { boleh: false, kalimat: akun.kalimat || 'Akun ini belum bisa mencatat' };
  if (hak === 'tidak') return { boleh: false, kalimat: 'Peran ' + namaPeran(akun.peran) + ' tidak boleh ' + String(namaTindakan || tindakan).toLowerCase() };
  if (hak !== 'sendiri') return { boleh: false, kalimat: KALIMAT_MINTA_OWNER };
  const buka = SERVER_BUKA[tindakan] || []; if (buka.indexOf(akun.peran) < 0) return { boleh: false, kalimat: KALIMAT_MINTA_OWNER };
  return { boleh: true, kalimat: '' };
}

/** Ringkasan satu dokumen (baris jejak) — sama dengan ringkasDok yang dipakai penulis pusat sejak putaran 2. */
export function ringkasDok(d) {
  if (!d) return '';
  const n = (d.hargaTotal !== undefined && d.hargaTotal !== null) ? d.hargaTotal : ((d.nominal !== undefined && d.nominal !== null) ? d.nominal : '');
  const nm = d.namaProduk || d.namaPelanggan || d.namaPegawai || d.pemasok || d.merkSumber || d.keterangan || d.catatan || '';
  return (String(nm).slice(0, 40) + (n !== '' ? ' · Rp' + Math.round(n).toLocaleString('id-ID') : '')).trim();
}

/**
 * Atribusi satu pintu (persis simpanKeFirestore index.html untuk owner) + identitas SAH: olehUid / diubahOlehUid = uid akun yang masuk.
 * ada = dokumen itu sudah ada (penulis pusat membaca cache). Owner: pencipta diisi bila kosong (seperti dulu). Bukan-owner: pencipta hanya di dokumen BARU —
 * update tidak pernah menambah oleh/perangkat/lokasi (rules membatasi kolomnya, peta §5). Dokumen lama tanpa olehUid tetap sah; tidak ditambal.
 */
export function beriAtribusiAkun(data, akun, konteks, ada) {
  const d = Object.assign({}, data); const k = konteks || {};
  const isiPencipta = akun.jenis === 'owner' || !ada;
  if (isiPencipta) {
    if (!d.oleh) { d.oleh = akun.nama; d.olehUid = akun.uid; }
    if (!d.perangkat) d.perangkat = k.perangkat;
    if (k.lokasi && !d.lokasi) d.lokasi = k.lokasi;
  }
  d.diubahOleh = akun.nama; d.diubahOlehUid = akun.uid; d.diubahPerangkat = k.perangkat; d.diubahPada = k.kini;
  Object.keys(d).forEach((x) => { if (d[x] === undefined) delete d[x]; });
  return d;
}

// koleksi/operasi → tindakan SS2 yang biasanya menulisnya (hanya untuk kalimat penolakan yang bisa dipahami)
const TINDAKAN_DARI = { batchMasuk: 'kedatangan', pengeluaranHarian: 'uangKeluar', kasbonMutasi: 'uangKeluar', tutupHari: 'hitungLaci', aturanToko: 'atur', koreksiHpp: 'hargaBeli',
  katalogHargaKarung: 'hargaBeli', katalogHargaKemasan: 'hargaBeli', katalogHargaLiteran: 'hargaBeli' };
const NAMA_TINDAKAN = { kedatangan: 'hitung truk & draf kedatangan', uangKeluar: 'catat uang keluar dari laci', hitungLaci: 'hitung & rapikan laci', atur: 'ubah setelan (Atur)',
  hargaBeli: 'isi harga beli / modal', hapus: 'hapus catatan', koreksi: 'koreksi nota yang sudah tersimpan', jualBon: 'jual dengan bon' };

/**
 * Penjaga penulis pusat untuk akun bukan-owner — dijalankan SEBELUM dikirim. dokumen = [{ koleksi, data, ada, lama }] (ada/lama dari cache),
 * hapus = [{ koleksi, id }]. hakPeran = kisi SS2 peran itu ({ tindakan: 'sendiri'|'owner'|'tidak' }). Kembali { tolak } atau { accessCall }.
 */
export function periksaKiriman(akun, dokumen, hapus, hakPeran) {
  if (!akun) return { tolak: 'Belum masuk' };
  if (akun.jenis === 'owner') return { accessCall: 0 };
  if (!bisaBekerja(akun)) return { tolak: akun.kalimat || 'Akun ini belum bisa mencatat' };
  const P = akun.peran; const hak = hakPeran || {};
  const tolakTindakan = (t) => { const h = hak[t] || 'tidak'; return h === 'tidak' ? 'Peran ' + namaPeran(P) + ' tidak boleh ' + (NAMA_TINDAKAN[t] || t) : KALIMAT_MINTA_OWNER; };
  if (hapus && hapus.length) return { tolak: tolakTindakan('hapus') };
  const D = dokumen || []; if (!D.length) return { tolak: 'Tidak ada yang dikirim' };
  const accessCall = D.length + 1;   // tiap dokumen memeriksa aksesAkun sekali + satu baris jejak kiriman (peta §7)
  if (accessCall > BATAS_ACCESS_CALL) return { tolak: 'Kiriman ini terlalu besar untuk satu kali kirim (' + D.length + ' catatan, batas ' + (BATAS_ACCESS_CALL - 1) + ') — pecah jadi dua nota' };
  for (const x of D) {
    const d = x.data || {};
    if (!x.ada) {
      const boleh = BUAT_STAF[x.koleksi] || [];
      if (boleh.indexOf(P) < 0) return { tolak: tolakTindakan(TINDAKAN_DARI[x.koleksi] || 'koreksi') };
      if (x.koleksi === 'penjualan') {
        if (d.dibatalkan || d.dikoreksiOleh) return { tolak: tolakTindakan('koreksi') };
        if (String(d.caraBayar || '').toLowerCase() === 'kredit' && KREDIT_STAF.indexOf(P) < 0) return { tolak: tolakTindakan('jualBon') };
      }
      if (x.koleksi === 'piutangMutasi' && d.tipe !== 'bayar') return { tolak: tolakTindakan('koreksi') };
      if ((x.koleksi === 'stokBahanLiteran' || x.koleksi === 'stokBahanKemasan') && d.tipe !== 'pakai') return { tolak: tolakTindakan('hargaBeli') };
    } else {
      const u = UBAH_STAF[x.koleksi]; if (!u || u.peran.indexOf(P) < 0) return { tolak: tolakTindakan(TINDAKAN_DARI[x.koleksi] || 'koreksi') };
      const lama = x.lama || {}; const kunci = {}; Object.keys(lama).concat(Object.keys(d)).forEach((kk) => { kunci[kk] = true; });
      const berubah = Object.keys(kunci).filter((kk) => JSON.stringify(lama[kk]) !== JSON.stringify(d[kk]));
      const liar = berubah.filter((kk) => u.kolom.indexOf(kk) < 0); if (liar.length) return { tolak: tolakTindakan('koreksi') };
      if (x.koleksi === 'pesanan' && (['dibayar', 'batal'].indexOf(String(lama.status || '')) >= 0 || d.status !== 'dibayar')) return { tolak: tolakTindakan('koreksi') };
    }
  }
  return { accessCall };
}

/** SATU baris jejak per kiriman bukan-owner (owner poin 1-B): memuat daftar SEMUA dokumen di kiriman itu. */
export function jejakKiriman(akun, dokumen, konteks) {
  const k = konteks || {}; const daftar = (dokumen || []).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id), ringkas: ringkasDok(x.data) }));
  return { id: k.idJejak, pada: k.kini, aksi: 'kirim', koleksi: daftar.length === 1 ? daftar[0].koleksi : '(kiriman)', idDok: daftar.length ? daftar[0].id : '', oleh: akun.nama, olehUid: akun.uid,
    perangkat: k.perangkat, ringkas: daftar.length + ' catatan: ' + daftar.map((d) => d.koleksi + (d.ringkas ? ' ' + d.ringkas : '')).join(' | ').slice(0, 300), dokumen: daftar };
}
