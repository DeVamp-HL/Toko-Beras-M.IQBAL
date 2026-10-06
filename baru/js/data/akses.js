// AKSES PER ORANG (putaran 23, "jalan A"): siapa yang masuk, perannya apa, boleh membaca & mencatat apa.
// Logika TANPA DOM & tanpa Firebase — dijaga alat-uji/uji_akses_baru.py. Dasar tiap daftar: docs/peta-hak-akses.md (§ disebut di tiap baris).
// SERVER (firestore.rules v3) yang menegakkan. Berkas ini membuat layar & penulis pusat berkata SAMA dengan rules, supaya kiriman yang
// pasti ditolak server tidak pernah dikirim (dan yang tetap ditolak server tertangkap di antre-lokal.js, tidak hilang diam).
// Keputusan owner 24 Sep: akun tanpa aksesAkun aktif = nol akses (kecuali minta didaftarkan); owner dikenali lewat EMAIL, aksesAkun tak pernah
// memberi peran owner; jalur kasir@ tetap milik kasir@ saja; satu baris jejak per kiriman bukan-owner memuat daftar dokumennya.
import { KOLEKSI } from './koleksi.js';
import { kpNilaiKiriman, kpNamaBulan } from './kunci-periode.js';

export const EMAIL_OWNER = 'owner@tokoberasmiqbal.web.app';
export const EMAIL_KASIR = 'kasir@tokoberasmiqbal.web.app';
// Id peran = SS_PERAN tanpa owner. UTANG (dicatat owner 24 Sep): 'ben' memakai nama orang; peran harus bernama jabatan. Data SS2 bergantung padanya.
export const PERAN_BUKAN_OWNER = ['ben', 'karyawan'];
export const NAMA_PERAN = { owner: 'Owner', ben: 'Ben (penjaga laci)', karyawan: 'Karyawan' };
export const BATAS_ACCESS_CALL = 20;   // per batch/transaksi (dokumentasi Firebase); cache dianggap TIDAK ada (keputusan owner poin 4)
// Putaran 23c (owner 24 Sep): kiriman bukan-owner dijaga SISA 2 di bawah batas Firebase. Terburuk per jenis kiriman dihitung dari fungsi
// aslinya oleh alat-uji/peta_akses.py --kiriman (CI, gagal bila > 18). Batas baris/hasil di bawah membuat terburuknya 17.
export const CADANGAN_ACCESS_CALL = 2;
export const BATAS_KIRIM_STAF = BATAS_ACCESS_CALL - CADANGAN_ACCESS_CALL;   // 18 = paling banyak 17 dokumen + 1 baris jejak
export const BATAS_BARIS_NOTA_STAF = 7;     // nota: 7 baris (nota nyata terpanjang di cadangan toko: 7 baris) — DOKUMENNYA dijaga batasDokumenKirim (39b no. 21: literan wadah campuran = satu baris per merek asal)
export const BATAS_HASIL_ADUKAN_STAF = 8;   // adukan: 8 hasil × (produksi + kantong) + jejak = 17

// §3 — yang DIBACA bukan-owner. Koleksi utuh + setelan PER DOKUMEN (aturanToko & pengaturan bercampur tarif upah, NPWP, titik kas, PIN).
export const BACA_STAF = ['penjualan', 'piutangMutasi', 'pelangganCatatan', 'pelangganTitip', 'pesanan', 'tagihPelanggan', 'strukKeluar',
  'batchMasuk', 'produksiKemasan', 'penyesuaianStok', 'penyesuaianKemasan', 'retur', 'karantina', 'stokBahanKemasan', 'stokBahanLiteran', 'wadahLiteran', 'pindahTempat',
  'katalogHargaKarung', 'katalogHargaKemasan', 'katalogHargaLiteran', 'hargaWadah'];
export const DOK_STAF = { aturanToko: ['struk', 'pelanggan', 'pelangganKembar', 'catatStok', 'kantong', 'tempat', 'peran', 'perangkat'], pengaturan: ['tempatSimpan'] };
// §4 — CREATE bukan-owner: koleksi → peran yang boleh. Menambah peran nanti = menambah satu nama di sini DAN di daftar yang sama di firestore.rules.
export const BUAT_STAF = { penjualan: ['ben', 'karyawan'], piutangMutasi: ['ben', 'karyawan'], stokBahanLiteran: ['ben', 'karyawan'], stokBahanKemasan: ['ben', 'karyawan'],
  produksiKemasan: ['ben', 'karyawan'], pelangganCatatan: ['ben', 'karyawan'], strukKeluar: ['ben', 'karyawan'], logAktivitas: ['ben', 'karyawan'], perangkatStatus: ['ben', 'karyawan'],
  wadahLiteran: ['ben', 'karyawan'], batchMasuk: ['ben', 'karyawan'] };   // rules v5 (putaran 39): wadahLiteran hanya tipe takar/karung/karungIsi/cek; batchMasuk hanya batch LAHIR BUKU 0 kg (periksaKiriman)
export const TIPE_WADAH_STAF = ['takar', 'karung', 'karungIsi', 'cek'];   // = stafBuatWadah di rules v5
export const KREDIT_STAF = ['ben'];   // penjualan caraBayar Kredit (jualBon): ben `sendiri`, karyawan `owner`
// §5 — dua pengecualian UPDATE. Kolom atribusi ubah ikut (penulis pusat menulisnya); kolom pencipta (oleh, perangkat, lokasi) TIDAK pernah ditambah bukan-owner.
export const KOLOM_ATRIBUSI_UBAH = ['diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada'];
export const UBAH_STAF = {
  pesanan: { peran: ['ben', 'karyawan'], kolom: ['status', 'riwayatStatus', 'trxIdJual'].concat(KOLOM_ATRIBUSI_UBAH) },
  perangkatStatus: { peran: ['ben', 'karyawan'], kolom: ['id', 'nama', 'akun', 'akunUid', 'aplikasi', 'pada', 'antrean', 'gagal', 'versi', 'pemegang', 'lokasi'] },
};
export const LAYAR_STAF = ['jual', 'pelanggan', 'stok', 'menu'];
// §1 — tindakan SS2 yang DIBUKA server putaran ini, per peran. Selebihnya tertutup (hitung laci & kedatangan: §6).
export const SERVER_BUKA = { jualTunai: ['ben', 'karyawan'], jualBon: ['ben'], terimaBon: ['ben', 'karyawan'], adukan: ['ben', 'karyawan'], pelangganBaru: ['ben', 'karyawan'], isiUlang: ['ben', 'karyawan'] };   // isiUlang: rules v5 (putaran 39)
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
/** Batas baris per nota / hasil per adukan untuk akun ini (0 = tanpa batas: owner). Layar menyerahkannya ke logika (s.batasBaris, draf.batasHasil). */
export const batasBarisNota = (akun) => (akun && akun.jenis !== 'owner' ? BATAS_BARIS_NOTA_STAF : 0);
export const batasHasilAdukan = (akun) => (akun && akun.jenis !== 'owner' ? BATAS_HASIL_ADUKAN_STAF : 0);
/** 39b no. 21: dokumen paling banyak per kiriman akun ini (0 = owner) = pagar periksaKiriman tanpa baris jejak. Layar menyerahkannya ke logika (s.batasDok): nota & isian takar. */
export const batasDokumenKirim = (akun) => (akun && akun.jenis !== 'owner' ? BATAS_KIRIM_STAF - 1 : 0);
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
  katalogHargaKarung: 'hargaBeli', katalogHargaKemasan: 'hargaBeli', katalogHargaLiteran: 'hargaBeli', wadahLiteran: 'isiUlang' };
const NAMA_TINDAKAN = { kedatangan: 'hitung truk & draf kedatangan', uangKeluar: 'catat uang keluar dari laci', hitungLaci: 'hitung & rapikan laci', atur: 'ubah setelan (Atur)',
  hargaBeli: 'isi harga beli / modal', hapus: 'hapus catatan', koreksi: 'koreksi nota yang sudah tersimpan', jualBon: 'jual dengan bon', isiUlang: 'isi ulang & cek wadah literan',
  jualTunai: 'jual tunai & kembalian', nego: 'nego di bawah jatah margin', terimaBon: 'terima pembayaran bon', adukan: 'catat adukan (bongkar kemasan)', pelangganBaru: 'daftarkan pelanggan baru' };
/** rules v5 stafBuatLahir: batch LAHIR BUKU 0 kg (buku baru wadah / karung belakang) — bukan kedatangan. */
const batchLahir = (d) => !!d && d.lahirBuku === true && d.stokAwal === true && !(Number(d.biayaBongkar) || 0) && String(d.pemasok || '') === 'LAHIR BUKU' && (d.merkList || []).every((r) => !(Number(r.totalKg) || 0) && !(Number(r.subtotalHarga) || 0));

/**
 * owner 7 Okt (JS2-C batas nego): satu baris penjualan yang harganya DITAWAR boleh dikirim bukan-owner tanpa tindakan "nego di bawah jatah margin" bila
 * (a) harganya tidak turun (negoSelisih ≥ 0), (b) DALAM JATAH orangnya — negoStatus 'jatah', harga ≥ negoBatas, 0 < negoJatah ≤ jatah akun ini (jatahNego,
 * setelan owner per orang), atau (c) DISETUJUI owner (negoStatus 'disetujui' + negoSetujuId — permintaan lewat koleksi persetujuan).
 * Nego tanpa tanda (bentuk lama), di bawah batas, jatah lebih besar dari jatah akun, atau di bawah modal = tindakan nego.
 */
export function negoDalamJatah(d, jatahNego) {
  const sel = Number(d && d.negoSelisih) || 0; if (sel >= 0) return true;
  if (d.negoStatus === 'disetujui') return !!d.negoSetujuId;
  if (d.negoStatus !== 'jatah') return false;
  const harga = (Number(d.hargaAsliSatuan) || 0) + sel; const batas = Number(d.negoBatas); const jatah = Number(d.negoJatah);
  return batas > 0 && harga >= batas && jatah > 0 && jatah <= (Number(jatahNego) || 0);
}
/**
 * audit 39b no. 22: tindakan kisi SS2 yang dijalankan SATU kiriman bukan-owner (dokumen baru saja; update pesanan menumpang notanya).
 * Ada penjualan = nota: jual bon (Kredit, termasuk bayar sebagian) atau jual tunai, + nego bila ada harga ditawar (negoSelisih) atau potongan nota.
 * owner 7 Okt: harga ditawar DALAM jatah orangnya / disetujui owner bukan tindakan nego (negoDalamJatah; jatahNego = jatah akun yang mengirim).
 * Tanpa nota: pelunasan = terima bon · kartu baru = pelanggan baru · wadah literan / buku lahir = isi ulang · produksi & kantong pakai = adukan.
 * Struk & jejak tidak menjalankan tindakan apa pun. Bentuk dokumennya tetap dijaga BUAT_STAF / UBAH_STAF di periksaKiriman.
 */
export function tindakanKiriman(D, jatahNego) {
  const baru = (D || []).filter((x) => !x.ada); const t = {}; const ada = (k) => baru.some((x) => x.koleksi === k);
  const jual = baru.filter((x) => x.koleksi === 'penjualan');
  jual.forEach((x) => { const d = x.data || {}; t[String(d.caraBayar || '').toLowerCase() === 'kredit' ? 'jualBon' : 'jualTunai'] = 1;
    if (!negoDalamJatah(d, jatahNego) || (Number(d.potonganTransaksi) || 0) > 0) t.nego = 1; });
  if (!jual.length && baru.some((x) => x.koleksi === 'piutangMutasi')) t.terimaBon = 1;
  if (ada('pelangganCatatan')) t.pelangganBaru = 1;
  const adaWadah = ada('wadahLiteran') || ada('batchMasuk');
  if (!jual.length) { if (adaWadah) t.isiUlang = 1; else if (ada('produksiKemasan') || ada('stokBahanKemasan') || ada('stokBahanLiteran')) t.adukan = 1; }
  return Object.keys(t);
}

/**
 * Penjaga penulis pusat untuk akun bukan-owner — dijalankan SEBELUM dikirim. dokumen = [{ koleksi, data, ada, lama }] (ada/lama dari cache),
 * hapus = [{ koleksi, id }]. hakPeran = kisi SS2 peran itu ({ tindakan: 'sendiri'|'owner'|'tidak' }) + jatahNego (owner 7 Okt: jatah nego akun ini, % margin —
 * app.js setelSumberHak). Kembali { tolak } atau { accessCall }.
 * Putaran 25: bukan-owner hanya boleh menulis catatan bertanggal bulan berjalan atau bulan lalu SELAMA masa tenggang minimal — di rules tanpa get()
 * (kunciPeriode tidak pernah dibaca untuk bukan-owner), jadi access call tetap 1 per dokumen. Di luar itu: owner yang menulis (ditolak server → daftar ditolak).
 */
export function periksaKiriman(akun, dokumen, hapus, hakPeran, kini) {
  if (!akun) return { tolak: 'Belum masuk' };
  if (akun.jenis === 'owner') return { accessCall: 0 };
  if (!bisaBekerja(akun)) return { tolak: akun.kalimat || 'Akun ini belum bisa mencatat' };
  const P = akun.peran; const hak = hakPeran || {};
  const tolakTindakan = (t) => { const h = hak[t] || 'tidak'; return h === 'tidak' ? 'Peran ' + namaPeran(P) + ' tidak boleh ' + (NAMA_TINDAKAN[t] || t) : KALIMAT_MINTA_OWNER; };
  if (hapus && hapus.length) return { tolak: tolakTindakan('hapus') };
  const D = dokumen || []; if (!D.length) return { tolak: 'Tidak ada yang dikirim' };
  const accessCall = D.length + 1;   // tiap dokumen memeriksa aksesAkun sekali + satu baris jejak kiriman (peta §7)
  if (accessCall > BATAS_KIRIM_STAF) return { tolak: 'Kiriman ini terlalu besar untuk satu kali kirim (' + D.length + ' catatan, batas ' + (BATAS_KIRIM_STAF - 1) + ') — ' + (D.some((x) => x.koleksi === 'penjualan') ? 'pecah jadi dua nota' : 'catat dalam dua kali') };
  for (const x of D) {
    const d = x.data || {};
    if (!x.ada) {
      const boleh = BUAT_STAF[x.koleksi] || [];
      if (boleh.indexOf(P) < 0) return { tolak: tolakTindakan(TINDAKAN_DARI[x.koleksi] || 'koreksi') };
      if (x.koleksi === 'penjualan') {
        if (d.dibatalkan || d.dikoreksiOleh) return { tolak: tolakTindakan('koreksi') };
        if (String(d.caraBayar || '').toLowerCase() === 'kredit' && KREDIT_STAF.indexOf(P) < 0) return { tolak: tolakTindakan('jualBon') };
        // 39b no. 9: tanda "kredit dibuka sekali oleh owner" (KR1 dilewati) hanya ditulis owner
        if (d.kreditDibukaOwner) return { tolak: KALIMAT_MINTA_OWNER };
        // tinjauan no. 22: tanda PENGGANTI RETUR (nota Rp0, barang keluar tanpa uang) = retur & tukar → owner saja (peta hak §2)
        if (d.penggantiRetur) return { tolak: KALIMAT_MINTA_OWNER };
      }
      if (x.koleksi === 'piutangMutasi' && d.tipe !== 'bayar') return { tolak: tolakTindakan('koreksi') };
      if ((x.koleksi === 'stokBahanLiteran' || x.koleksi === 'stokBahanKemasan') && d.tipe !== 'pakai') return { tolak: tolakTindakan('hargaBeli') };
      // rules v5 (putaran 39): karyawan menulis wadahLiteran hanya takar / karung / karungIsi / cek (aturan wadah & titik samakan isi = owner), batchMasuk hanya batch LAHIR BUKU 0 kg
      if (x.koleksi === 'wadahLiteran' && TIPE_WADAH_STAF.indexOf(String(d.tipe || '')) < 0) return { tolak: tolakTindakan('atur') };
      if (x.koleksi === 'batchMasuk' && !batchLahir(d)) return { tolak: tolakTindakan('kedatangan') };
      // owner 7 Okt (JS2-C): permintaan nego ke owner — hanya bentuk "menunggu" bertindakan nego, tanpa keputusan, dari peran yang kisinya bukan "tidak boleh".
      // Sampai rules membuka persetujuan untuk bukan-owner (BUAT_STAF di atas belum memuatnya) baris ini tidak tercapai — penjaganya disiapkan bersama layarnya.
      if (x.koleksi === 'persetujuan' && (d.tindakan !== 'nego' || d.status !== 'menunggu' || d.diputusPada || (hak.nego || 'tidak') === 'tidak')) return { tolak: tolakTindakan('nego') };
    } else {
      const u = UBAH_STAF[x.koleksi]; if (!u || u.peran.indexOf(P) < 0) return { tolak: tolakTindakan(TINDAKAN_DARI[x.koleksi] || 'koreksi') };
      const lama = x.lama || {}; const kunci = {}; Object.keys(lama).concat(Object.keys(d)).forEach((kk) => { kunci[kk] = true; });
      const berubah = Object.keys(kunci).filter((kk) => JSON.stringify(lama[kk]) !== JSON.stringify(d[kk]));
      const liar = berubah.filter((kk) => u.kolom.indexOf(kk) < 0); if (liar.length) return { tolak: tolakTindakan('koreksi') };
      if (x.koleksi === 'pesanan' && (['dibayar', 'batal'].indexOf(String(lama.status || '')) >= 0 || d.status !== 'dibayar')) return { tolak: tolakTindakan('koreksi') };
    }
  }
  // audit 39b no. 22: kisi SS2 DITEGAKKAN di sini (dulu hak hanya memilih kalimat; yang menahan cuma 4 tombol). Tiap tindakan kiriman ini wajib "boleh sendiri"
  // di kisi peran DAN dibuka server (SERVER_BUKA); nego tidak pernah dibuka untuk bukan-owner. Kisi yang diputar owner belum ditegakkan rules (tanpa get()).
  for (const t of tindakanKiriman(D, hak.jatahNego)) { if (hak[t] !== 'sendiri' || (SERVER_BUKA[t] || []).indexOf(P) < 0) return { tolak: tolakTindakan(t) }; }
  // putaran 25: hanya bulan berjalan / bulan lalu dalam masa tenggang minimal (rules tglStaf(), tanpa get()); dinilai SESUDAH hak, supaya kalimat hak tetap yang tampil
  const lewat = kpNilaiKiriman(D.map((x) => ({ koleksi: x.koleksi, data: x.data, lama: x.lama })), null, kini || new Date(Date.now())).lewatTenggang;
  if (lewat.length) return { tolak: 'Catatan bertanggal ' + kpNamaBulan(lewat[0].bulan) + ' sudah lewat masa tenggang — hanya owner yang bisa mencatatnya sekarang' };
  return { accessCall };
}

/** SATU baris jejak per kiriman bukan-owner (owner poin 1-B): memuat daftar SEMUA dokumen di kiriman itu. */
export function jejakKiriman(akun, dokumen, konteks) {
  const k = konteks || {}; const daftar = (dokumen || []).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id), ringkas: ringkasDok(x.data) }));
  return { id: k.idJejak, pada: k.kini, aksi: 'kirim', koleksi: daftar.length === 1 ? daftar[0].koleksi : '(kiriman)', idDok: daftar.length ? daftar[0].id : '', oleh: akun.nama, olehUid: akun.uid,
    perangkat: k.perangkat, ringkas: daftar.length + ' catatan: ' + daftar.map((d) => d.koleksi + (d.ringkas ? ' ' + d.ringkas : '')).join(' | ').slice(0, 300), dokumen: daftar };
}
