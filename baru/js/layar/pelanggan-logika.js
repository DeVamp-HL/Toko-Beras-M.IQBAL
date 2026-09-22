// LAYAR PELANGGAN — LOGIKA (tanpa DOM): PL1 KENALI PELANGGAN (dikunci owner 18 Sep = gabungan Sketsa · Tampah · Belanja · Jam · Minggu · Benang · Hafalan)
// + PL3 THR PELANGGAN SETIA (Daftar Setia · Meja Bingkisan · Amplop). Dijaga alat-uji/uji_pelanggan_baru.py. Bon (PL2) di bon-logika.js.
//
// Orang = NAMA yang diketik di nota (kunciPelanggan, sama dengan sistem berjalan: nama = kunci, ejaan terbaru menang). Owner & karyawan tidak hafal nama
// (memori orang-dan-peran-toko) → dikenali lewat yang TERLIHAT: cip ciri di kartu, jam biasa datang, hari langganan, yang biasa dibelinya.
// Kartu pelanggan = dokumen `pelangganCatatan` {id = kunci, nama, catatan, ciri, rute} PERSIS simpanCatatanPelanggan index.html 25126 — `ciri` ditulis sebagai
// gabungan cip supaya gerbang KR1 sistem lama (catatanPelangganBerisi: catatan | ciri | rute) membaca orang yang sama sebagai "dikenali"; kolom tambahan
// sistem baru: cip[], asli, kontak, biasa, arah (= rute). Selang = median hari antar-kedatangan, baru dihitung bila ≥ 3 hari kedatangan (memori
// bangku-yang-kosong); "bangku kosong" = sudah ≥ N× selangnya sendiri tidak datang (N setelan owner). Nama kembar TIDAK pernah digabung sendiri — cuma
// ditawarkan (memori nama-pelanggan-teks-bebas); SATUKAN = owner memutuskan, semua dokumen bernama itu ditulis ulang atas satu nama (rupiah tidak berubah).
// Benang (yang datang bukan orangnya) = koleksi baru `pelangganTitip`; angka & daftar kebijakan owner = `aturanToko/pelanggan`.
import { hitungPiutang } from '../mesin/beku.js';
import { kunciPelanggan, catatanPelangganBerisi } from '../mesin/pembantu.js';
import { ambilPenjualanSemua, ambilPenjualan, ambilPiutangMutasi, ambilPelangganCatatan, ambilThrPelanggan, ambilPesanan, cacheMentah } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';

export const TANYA_CIRI = [['siapa', 'Siapa dia'], ['tampak', 'Yang tampak'], ['naik', 'Datang naik apa'], ['beli', 'Belinya apa']];
export const ATUR_PELANGGAN_BAWAAN = {
  kosongKali: 20, notaBesar: 500000, tagihHari: 14, macetHari: 180, anggaranThr: 500000,
  ciriDaftar: [['ibu-ibu', 'siapa'], ['bapak-bapak', 'siapa'], ['anak muda', 'siapa'], ['nenek / kakek', 'siapa'], ['kerudung', 'tampak'], ['peci', 'tampak'], ['kacamata', 'tampak'],
    ['naik motor', 'naik'], ['jalan kaki', 'naik'], ['mobil bak', 'naik'], ['becak', 'naik'], ['bawa gerobak', 'naik'], ['karung', 'beli'], ['kemasan', 'beli'], ['literan', 'beli'], ['warung / usaha', 'beli']].map((x) => ({ nama: x[0], grup: x[1] })),
  arahDaftar: [], titipDaftar: ['membayarkan bon', 'mengambilkan belanjaan', 'disuruh belanja'],
  alasanHapus: ['pindah, tidak bisa dihubungi', 'sudah meninggal', 'disepakati tidak ditagih', 'nominal kecil, tidak sepadan ditagih'],
  salamTagih: 'Mohon dicek. Pembayaran bisa tunai di toko atau QRIS. Terima kasih 🙏',
  bentukThr: [{ nama: 'Sarung', n: 75000 }, { nama: 'Mukena', n: 90000 }, { nama: 'Sirup + biskuit', n: 60000 }, { nama: 'Beras 5 kg', n: 80000 }],
};
const plAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const plKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const plPolos = (t) => String(t || '').toLowerCase().replace(/\b(bu|ibu|pak|bapak|mas|mbak|bang|uda|koh|teh|nek|haji|h)\b/g, ' ').replace(/[^a-z0-9]+/g, ' ').trim();
export const hariKe = (iso) => Math.round(Date.UTC(+String(iso).slice(0, 4), +String(iso).slice(5, 7) - 1, +String(iso).slice(8, 10)) / 86400000);
export const hariMingguKe = (iso) => (new Date(String(iso) + 'T00:00:00Z').getUTCDay() + 6) % 7;   // Senin = 0
export const NAMA_HARI = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
export const HARI_PANJANG = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
export const waktuKata = (j) => (j < 11 ? 'pagi' : j < 15 ? 'siang' : 'sore');
const plJam = (t) => { const m = /^(\d{1,2})[:.]/.exec(String(t || '')); return m ? Math.min(23, Number(m[1])) : null; };
const plMedian = (a) => { if (!a.length) return null; const b = a.slice().sort((x, y) => x - y); const t = Math.floor(b.length / 2); return b.length % 2 ? b[t] : (b[t - 1] + b[t]) / 2; };
export const inisial = (n) => { const k = String(n || '').trim().split(/\s+/).filter((x) => !/^(bu|ibu|pak|bapak|mas|mbak|bang|uda|koh|teh|nek|h)$/i.test(x)); const p = (k.length ? k : [String(n || '')]).slice(0, 2).map((x) => x[0] || '').join('').toUpperCase(); return p || '?'; };
export const acak = (t) => { let h = 7; for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) % 9973; return h; };   // urutan "acak" yang sama tiap kali — pembeda ditaruh DI DEPAN (memori PL1 V4)

/** Angka & daftar kebijakan owner (aturanToko/pelanggan); belum diatur → bawaan. */
export function aturPelanggan() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'pelanggan') || null; const B = ATUR_PELANGGAN_BAWAAN;
  const angka = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : B[k]);
  const daftar = (k, bersih) => (a && Array.isArray(a[k]) ? a[k].map(bersih).filter(Boolean) : B[k].slice());
  return { kosongKali: angka('kosongKali', (n) => n >= 10 && n <= 100), notaBesar: angka('notaBesar', (n) => n >= 0), tagihHari: angka('tagihHari', (n) => n >= 0 && n <= 365), macetHari: angka('macetHari', (n) => n >= 0 && n <= 3650), anggaranThr: angka('anggaranThr', (n) => n >= 0),
    ciriDaftar: daftar('ciriDaftar', (x) => (x && x.nama ? { nama: String(x.nama).trim(), grup: String(x.grup || 'lain') } : null)), arahDaftar: daftar('arahDaftar', (x) => (plKosong(x) ? null : String(x).trim())), titipDaftar: daftar('titipDaftar', (x) => (plKosong(x) ? null : String(x).trim())),
    alasanHapus: daftar('alasanHapus', (x) => (plKosong(x) ? null : String(x).trim())), salamTagih: a && !plKosong(a.salamTagih) ? String(a.salamTagih) : B.salamTagih, bentukThr: daftar('bentukThr', (x) => (x && x.nama ? { nama: String(x.nama).trim(), n: Math.max(0, Number(x.n) || 0) } : null)), dariOwner: !!a };
}
/** Simpan aturan: isi = {kosongKali, notaBesar, tagihHari, macetHari, anggaranThr (teks), ciriDaftar[{nama,grup}], arahDaftar[], titipDaftar[], alasanHapus[], salamTagih, bentukThr[{nama,n}]}. Baris yang masih dipakai tidak boleh hilang. */
export function susunAturPelanggan(isi, w) {
  const kini = aturPelanggan(); const baca = (k, syarat, teks) => { if (plKosong(isi[k])) return { nilai: kini[k] }; const n = plAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const kk = baca('kosongKali', (n) => n >= 10 && n <= 100, 'Bangku kosong minimal 10 (= 1,0× selangnya), maksimal 100'); if (kk.tolak) return { tolak: kk.tolak };
  const nb = baca('notaBesar', (n) => n >= 0, 'Batas nota yang perlu nama tidak boleh minus'); if (nb.tolak) return { tolak: nb.tolak };
  const th = baca('tagihHari', (n) => n >= 0 && n <= 365, 'Waktunya ditagih: 0–365 hari'); if (th.tolak) return { tolak: th.tolak };
  const mh = baca('macetHari', (n) => n >= 0 && n <= 3650, 'Disebut macet: 0–3650 hari'); if (mh.tolak) return { tolak: mh.tolak };
  const ag = baca('anggaranThr', (n) => n >= 0, 'Anggaran THR tidak boleh minus'); if (ag.tolak) return { tolak: ag.tolak };
  const rapi = (d, ambil) => (Array.isArray(d) ? d.map(ambil).filter(Boolean) : null);
  const ciri = rapi(isi.ciriDaftar, (x) => (x && !plKosong(x.nama) ? { nama: String(x.nama).trim(), grup: String(x.grup || 'lain') } : null)) || kini.ciriDaftar;
  const arah = rapi(isi.arahDaftar, (x) => (plKosong(x) ? null : String(x).trim())) || kini.arahDaftar; const titip = rapi(isi.titipDaftar, (x) => (plKosong(x) ? null : String(x).trim())) || kini.titipDaftar;
  const alasan = rapi(isi.alasanHapus, (x) => (plKosong(x) ? null : String(x).trim())) || kini.alasanHapus; const bentuk = rapi(isi.bentukThr, (x) => (x && !plKosong(x.nama) ? { nama: String(x.nama).trim(), n: Math.max(0, plAngka(x.n)) } : null)) || kini.bentukThr;
  // baris yang masih dipakai kartu orang tidak boleh hilang / berganti nama — cirinya jadi yatim
  const orang = semuaOrang(new Date()); const hilangCiri = kini.ciriDaftar.filter((c) => !ciri.some((x) => x.nama === c.nama)).filter((c) => orang.some((o) => o.cip.indexOf(c.nama) >= 0));
  if (hilangCiri.length) return { tolak: 'Ciri "' + hilangCiri[0].nama + '" masih dipakai ' + orang.filter((o) => o.cip.indexOf(hilangCiri[0].nama) >= 0).length + ' orang — lepas dulu dari kartu mereka' };
  const hilangArah = kini.arahDaftar.filter((a) => arah.indexOf(a) < 0).filter((a) => orang.some((o) => o.arah === a)); if (hilangArah.length) return { tolak: 'Arah "' + hilangArah[0] + '" masih dipakai kartu orang — lepas dulu' };
  const hilangTitip = kini.titipDaftar.filter((a) => titip.indexOf(a) < 0).filter((a) => cacheMentah('titip').some((t) => t.apa === a)); if (hilangTitip.length) return { tolak: 'Urusan "' + hilangTitip[0] + '" masih dipakai benang — buang dulu benangnya' };
  const salam = plKosong(isi.salamTagih) ? kini.salamTagih : String(isi.salamTagih).trim().slice(0, 200);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'pelanggan', tanggal: w.tanggal, jam: w.jam, kosongKali: kk.nilai, notaBesar: nb.nilai, tagihHari: th.nilai, macetHari: mh.nilai, anggaranThr: ag.nilai, ciriDaftar: ciri, arahDaftar: arah, titipDaftar: titip, alasanHapus: alasan, salamTagih: salam, bentukThr: bentuk } }],
    patch: { kabar: 'Aturan pelanggan disimpan — ' + ciri.length + ' cip ciri · bangku kosong ' + (kk.nilai / 10).toFixed(1).replace('.', ',') + '× selang · nota ≥ ' + RP(nb.nilai) + ' perlu nama · tagih sesudah ' + th.nilai + ' hari · macet sesudah ' + mh.nilai + ' hari · anggaran THR ' + RP(ag.nilai), kabarAwas: false } };
}
const plBukanKembar = () => { const d = cacheMentah('aturan').find((x) => String(x.id) === 'pelangganKembar'); return d && Array.isArray(d.bukan) ? d.bukan.map(String) : []; };

// ====================== SATU TEMPAT MEMBACA TIAP ORANG ======================
const plBarangKunci = (p) => (p.jenis === 'kemasan' ? 'kemasan|' + (p.namaProduk || '') + '|' + (p.ukuranKemasan || '') : p.jenis === 'karung' ? 'karung|' + (p.merkSumber || '') : p.jenis === 'literan' ? 'literan|' + (p.merkSumber || '') : p.jenis === 'repacking' ? 'repack|' + (p.namaProduk || p.merkSumber || '') : '');
export const plBarangNama = (k) => { const b = String(k).split('|'); return b[0] === 'kemasan' ? b[1] + ' ' + String(b[2]).replace('.', ',') + ' kg' : b[0] === 'karung' ? b[1] + ' karung' : b[0] === 'literan' ? b[1] + ' literan' : b[0] === 'repack' ? 'repack ' + b[1] : k; };
/** Kartu tersimpan (pelangganCatatan) dibaca ke bentuk baru: cip[] (atau pecahan `ciri` lama), arah (= rute), asli, kontak, biasa. */
export function kartuTersimpan(kunci) {
  const c = ambilPelangganCatatan().find((x) => kunciPelanggan(x.nama || x.id) === kunci) || null; if (!c) return null;
  const cip = Array.isArray(c.cip) ? c.cip.map(String) : String(c.ciri || '').split(/\s*[·,;]\s*/).map((x) => x.trim()).filter(Boolean);
  return { dok: c, nama: String(c.nama || c.id), cip, catatan: String(c.catatan || ''), arah: String(c.arah || c.rute || ''), asli: String(c.asli || ''), kontak: String(c.kontak || ''), biasa: String(c.biasa || ''), dikenali: catatanPelangganBerisi(c) };
}
/**
 * Semua orang yang pernah tercatat (nota bernama, buku bon, kartu): kunjungan (hari datang), jam biasa, selang, hari langganan, belanja per tahun,
 * barang yang biasa dibeli, bon, kartu. `kini` = Date "sekarang" (mode cadangan: saat unduh).
 */
export function semuaOrang(kini) {
  const iso = hariIniIso(kini); const jamKini = kini.getHours(); const atur = aturPelanggan(); const peta = {};
  const slot = (nama, urut) => { const k = kunciPelanggan(nama); if (!k) return null; if (!peta[k]) peta[k] = { kunci: k, nama: String(nama).trim(), urutNama: 0, hari: {}, jamList: [], total: 0, tahun: {}, barang: {}, nota: 0, notaAkhir: null };
    if ((urut || 0) >= peta[k].urutNama) { peta[k].nama = String(nama).trim(); peta[k].urutNama = urut || 0; } return peta[k]; };
  ambilPenjualan().forEach((p) => { if (!p.namaPelanggan) return; const o = slot(p.namaPelanggan, Number(p.id) || 0); if (!o) return; const t = p.tanggal || ''; if (t) o.hari[t] = (o.hari[t] || 0) + 1; const j = plJam(p.jam); if (j !== null) o.jamList.push(j);
    o.total += p.hargaTotal || 0; const th = t.slice(0, 4); if (th) o.tahun[th] = (o.tahun[th] || 0) + (p.hargaTotal || 0); const bk = plBarangKunci(p); if (bk) o.barang[bk] = (o.barang[bk] || 0) + 1; o.nota += 1; if (!o.notaAkhir || (t + (p.jam || '')) > (o.notaAkhir.tanggal + (o.notaAkhir.jam || ''))) o.notaAkhir = p; });
  ambilPiutangMutasi().forEach((m) => { if (!m.namaPelanggan) return; const o = slot(m.namaPelanggan, Number(m.id) || 0); if (o && m.tipe === 'bayar' && m.tanggal) o.hari[m.tanggal] = (o.hari[m.tanggal] || 0) + 1; });   // nama di buku bon ikut jadi orang; pembayar bon juga DATANG (hitungPelanggan index.html) — saldo awal & hapus buku bukan kunjungan
  ambilPelangganCatatan().forEach((c) => slot(c.nama || c.id, 0));
  const piutang = {}; hitungPiutang().forEach((r) => { piutang[r.kunci] = r; });
  const bukan = plBukanKembar();
  const daftar = Object.keys(peta).map((k) => { const o = peta[k]; const tgl = Object.keys(o.hari).sort(); const kunjungan = tgl.length; const terakhir = tgl.length ? tgl[tgl.length - 1] : '';
    const selang = kunjungan >= 3 ? Math.round(plMedian(tgl.slice(1).map((t, i) => hariKe(t) - hariKe(tgl[i]))) * 10) / 10 : null; const jamMed = plMedian(o.jamList); const jam = jamMed === null ? null : Math.round(jamMed);
    const hari = [0, 0, 0, 0, 0, 0, 0]; tgl.forEach((t) => { hari[hariMingguKe(t)] += 1; }); const kartu = kartuTersimpan(k); const r = piutang[k] || null; const utang = r ? Math.max(0, r.sisa || 0) : 0;
    const sejak = terakhir ? hariKe(iso) - hariKe(terakhir) : null; const adaSelang = selang !== null && selang > 0; const hariIni = sejak === 0; const jatuh = adaSelang ? Math.round((selang - sejak) * 10) / 10 : null;
    const kosong = adaSelang && sejak * 10 >= selang * atur.kosongKali; const belumJadi = plPolos(o.nama).length < 2 && o.nama.trim().length < 3;
    const pola = Object.keys(o.barang).sort((a, b) => o.barang[b] - o.barang[a]).slice(0, 4);
    return { kunci: k, nama: o.nama, kunjungan, terakhir, selang, jam, hari, total: o.total, tahun: o.tahun, nota: o.nota, pola, utang, umurBon: r ? r.umurHari : null, kartu, cip: kartu ? kartu.cip : [], catatan: kartu ? kartu.catatan : '', arah: kartu ? kartu.arah : '', asli: kartu ? kartu.asli : '', kontak: kartu ? kartu.kontak : '', biasa: kartu ? kartu.biasa : '',
      dikenali: !!(kartu && kartu.dikenali), sejak, adaSelang, hariIni, jatuh, kosong, belumJadi, waktu: jam === null ? '' : waktuKata(jam), diharap: adaSelang && !kosong && jatuh !== null && jatuh <= 0 && !hariIni, sekarang: jam !== null && waktuKata(jam) === waktuKata(jamKini) }; });
  daftar.sort((a, b) => b.kunjungan - a.kunjungan || a.nama.localeCompare(b.nama)); daftar.forEach((o, i) => { o.no = i; o.warna = i % 6; });
  daftar.__bukan = bukan; return daftar;
}
const plTgl = (iso) => { const B = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']; return iso ? parseInt(iso.slice(8, 10), 10) + ' ' + B[parseInt(iso.slice(5, 7), 10) - 1] : ''; };
export function datangTeks(b) {
  return b.hariIni ? 'sudah datang hari ini' : b.sejak === null ? 'belum pernah tercatat datang' : b.kosong ? 'biasanya tiap ' + String(b.selang).replace('.', ',') + ' hari — sudah ' + b.sejak + ' hari tidak datang' : !b.adaSelang ? 'terakhir ' + plTgl(b.terakhir) + ' · baru ' + b.kunjungan + ' kali, belum terbaca polanya'
    : b.jatuh <= 0 ? 'biasanya tiap ' + String(b.selang).replace('.', ',') + ' hari — waktunya datang' + (b.jatuh < 0 ? ' (telat ' + String(-b.jatuh).replace('.', ',') + ' hari)' : ' hari ini') : 'biasanya tiap ' + String(b.selang).replace('.', ',') + ' hari · kira-kira ' + String(b.jatuh).replace('.', ',') + ' hari lagi';
}
export const julukan = (b) => b.cip.slice(0, 3).join(' · ') || (b.belumJadi ? 'namanya belum jadi' : 'belum ada cirinya');
export const jamTeks = (b) => (b.jam === null ? '' : 'biasanya ' + b.waktu + ' (±' + String(b.jam).padStart(2, '0') + '.00)');
const nilaiKini = (b) => (b.sekarang ? 4 : 0) + (b.diharap ? 3 : 0) + (b.jatuh !== null && b.jatuh > 0 && b.jatuh <= 1 ? 1 : 0) + (b.hariIni ? -5 : 0) + (b.kosong ? -1 : 0) + Math.min(2, b.kunjungan / 10);
const punya = (b, c) => b.cip.indexOf(c) >= 0;
const NAIK = [['naik motor', 'motor'], ['jalan kaki', 'kaki'], ['mobil bak', 'bak'], ['becak', 'becak'], ['bawa gerobak', 'gerobak']]; const BELI = [['karung', 'karung'], ['kemasan', 'kemasan'], ['literan', 'liter']];
/** Bahan gambar sketsa dari cip (Sketsa dari Ciri): kerudung/peci/kacamata/uban/muda; lencana kiri = naik apa, kanan = beli apa. */
export function sketsa(b) {
  const naik = NAIK.find((x) => punya(b, x[0])); const beli = BELI.find((x) => punya(b, x[0]));
  return { kosong: !b.cip.length, kerudung: punya(b, 'kerudung'), peci: punya(b, 'peci'), kacamata: punya(b, 'kacamata'), uban: punya(b, 'nenek / kakek'), muda: punya(b, 'anak muda'), rambut: !punya(b, 'kerudung') && !punya(b, 'peci') && !punya(b, 'nenek / kakek'), naik: naik ? naik[1] : '', beli: beli ? beli[1] : '', warna: b.warna || 0 };
}
const cari = (semua, teks) => { const c = plPolos(teks) || String(teks || '').trim().toLowerCase(); return !c ? semua : semua.filter((b) => plPolos(b.nama).indexOf(c) >= 0 || b.nama.toLowerCase().indexOf(c) >= 0 || plPolos(b.asli).indexOf(c) >= 0); };
/** Nama kembar (sesudah sapaan dibuang, satu memuat yang lain) yang belum dinyatakan "bukan" — ditawarkan, tidak digabung sendiri. */
export function pasanganKembar(semua) {
  const out = []; const bukan = semua.__bukan || plBukanKembar();
  semua.forEach((a, i) => semua.forEach((b, j) => { if (j <= i) return; const pa = plPolos(a.nama), pb = plPolos(b.nama); if (pa.length < 3 || pb.length < 3) return;
    if (pa === pb || (' ' + pa + ' ').indexOf(' ' + pb + ' ') >= 0 || (' ' + pb + ' ').indexOf(' ' + pa + ' ') >= 0) { const k = [a.kunci, b.kunci].sort().join('+'); if (bukan.indexOf(k) < 0) out.push({ k, a, b }); } }));
  return out;
}
/** Tab WAJAH (Sketsa dari Ciri): yang paling mungkin berdiri di depan meja sekarang di atas. */
export function susunWajah(kini, teksCari) {
  const semua = semuaOrang(kini); const jam = kini.getHours();
  const daftar = cari(semua, teksCari).slice().sort((a, b) => nilaiKini(b) - nilaiKini(a) || b.kunjungan - a.kunjungan).map((b) => Object.assign({}, b, { sk: sketsa(b), sub: julukan(b), datang: datangTeks(b), titik: b.utang > 0 ? 'bon' : b.kosong ? 'lama tak datang' : b.hariIni ? 'tadi' : '' }));
  return { daftar, kiniTeks: 'Jam ' + String(jam).padStart(2, '0') + '.' + String(kini.getMinutes()).padStart(2, '0') + ' — yang biasa datang ' + waktuKata(jam) + ' dan sudah waktunya ada di atas', tanpaCiri: semua.filter((b) => !b.dikenali).length, semua: semua.length,
    kembar: pasanganKembar(semua).map((p) => ({ k: p.k, teks: p.a.nama + ' ↔ ' + p.b.nama, a: p.a.kunci, b: p.b.kunci })), belumJadi: semua.filter((b) => b.belumJadi).map((b) => ({ kunci: b.kunci, nama: b.nama })) };
}
/** Tab TAMPAH: layar bertanya satu per satu (ciri yang membelah sisa paling rata); jawaban = [{c, j: ya|bukan|entah}]. */
export function susunTampah(kini, jawaban) {
  const semua = semuaOrang(kini); const atur = aturPelanggan(); const bisa = semua.filter((b) => b.cip.length > 0); let sisa = bisa.slice(); const lempar = []; const sah = (jawaban || []).filter((q) => atur.ciriDaftar.some((c) => c.nama === q.c));
  sah.forEach((q) => { if (q.j === 'entah') return; const tetap = sisa.filter((b) => punya(b, q.c) === (q.j === 'ya')); sisa.forEach((b) => { if (tetap.indexOf(b) < 0) lempar.push({ kunci: b.kunci, nama: b.nama, sebab: (q.j === 'ya' ? 'bukan ' : '') + q.c }); }); sisa = tetap; });
  const sudah = sah.map((q) => q.c); let tanya = null;
  if (sisa.length > 1) atur.ciriDaftar.forEach((c) => { if (!c.nama || sudah.indexOf(c.nama) >= 0) return; const n = sisa.filter((b) => punya(b, c.nama)).length; if (n === 0 || n === sisa.length) return; const timpang = Math.abs(2 * n - sisa.length); if (!tanya || timpang < tanya.timpang) tanya = { c: c.nama, grup: c.grup, n, timpang }; });
  const urut = sisa.slice().sort((a, b) => (b.sekarang ? 1 : 0) - (a.sekarang ? 1 : 0) || b.kunjungan - a.kunjungan); const MAKS = 25; const nT = Math.min(MAKS, urut.length);
  const kutub = (sudut, r) => { const a = (sudut * Math.PI) / 180; return { kiri: Math.round((50 + r * Math.cos(a)) * 10) / 10, atas: Math.round((50 + r * Math.sin(a)) * 10) / 10 }; };
  const letak = (i) => (nT === 1 ? { kiri: 50, atas: 50 } : nT <= 9 ? kutub(-90 + (i * 360) / nT, 25) : i < 9 ? kutub(-90 + i * 40, 18) : kutub(-90 + ((i - 9) * 360) / (nT - 9), 37));
  return { tanya, label: tanya ? (TANYA_CIRI.find((t) => t[0] === tanya.grup) || [0, 'Ciri lain'])[1] : '', kalau: tanya ? 'kalau ya tersisa ' + tanya.n + ' · kalau bukan tersisa ' + (sisa.length - tanya.n) : '',
    orang: urut.slice(0, MAKS).map((b, i) => Object.assign({}, b, letak(i), { sk: sketsa(b) })), lebih: Math.max(0, urut.length - MAKS), ketemu: sisa.length === 1 ? Object.assign({}, sisa[0], { sk: sketsa(sisa[0]), datang: datangTeks(sisa[0]) }) : null, buntu: sisa.length === 0, sama: sisa.length > 1 && !tanya,
    sisa: urut.map((b) => ({ kunci: b.kunci, nama: b.nama, sub: julukan(b), jamTeks: jamTeks(b) })), info: (tanya ? 'Tanya ke-' + (sah.length + 1) + ' · ' : sah.length + ' tanya · ') + 'tersisa ' + sisa.length + ' dari ' + bisa.length, riwayat: sah.map((q) => q.c + ': ' + (q.j === 'ya' ? 'ya' : q.j === 'bukan' ? 'bukan' : 'tidak kelihatan')), lempar, tanpaCiri: semua.length - bisa.length };
}
/** Tab BELANJA: nota besar hari ini yang belum bernama (satu nota = satu grupNota) + tebakan dari barangnya & jamnya. */
export function susunBelanja(kini, notaKunci, keranjang) {
  const semua = semuaOrang(kini); const atur = aturPelanggan(); const iso = hariIniIso(kini);
  const grup = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== iso || String(p.namaPelanggan || '').trim()) return; const g = String(p.grupNota || p.id); if (!grup[g]) grup[g] = { kunci: g, jam: p.jam || '', barang: [], n: 0, baris: [] }; grup[g].n += p.hargaTotal || 0; grup[g].baris.push(p); const bk = plBarangKunci(p); if (bk && grup[g].barang.indexOf(bk) < 0) grup[g].barang.push(bk); });
  const semuaNota = Object.values(grup).sort((a, b) => a.jam.localeCompare(b.jam)); const besar = semuaNota.filter((g) => g.n >= atur.notaBesar); const kecil = semuaNota.length - besar.length;
  const N = besar.find((g) => g.kunci === notaKunci) || null; const isi = N ? N.barang : (keranjang || []); const waktuD = N ? waktuKata(plJam(N.jam) === null ? kini.getHours() : plJam(N.jam)) : waktuKata(kini.getHours());
  const semuaBarang = {}; semua.forEach((b) => b.pola.forEach((k) => { semuaBarang[k] = (semuaBarang[k] || 0) + 1; })); const barang = Object.keys(semuaBarang).sort((a, b) => semuaBarang[b] - semuaBarang[a]).slice(0, 10).map((k) => ({ kunci: k, nama: plBarangNama(k), aktif: isi.indexOf(k) >= 0 }));
  const tebak = semua.map((b) => { const kena = isi.filter((k) => b.pola.indexOf(k) >= 0); return { b, kena, nilai: kena.length * 2 + (kena.length && b.waktu === waktuD ? 1 : 0) }; }).filter((x) => x.kena.length > 0).sort((x, y) => y.nilai - x.nilai || y.b.kunjungan - x.b.kunjungan)
    .map((x) => Object.assign({}, x.b, { sk: sketsa(x.b), alasan: 'biasa beli ' + x.kena.map(plBarangNama).join(' + ') + (x.b.waktu === waktuD ? ' · jamnya cocok (' + waktuD + ')' : x.b.waktu ? ' · biasanya ' + x.b.waktu : ''), yakin: x.kena.length === isi.length && x.b.waktu === waktuD ? 'cocok semua' : x.kena.length + '/' + isi.length + ' barang' }));
  return { nota: besar.map((g) => ({ kunci: g.kunci, jam: g.jam, teks: g.barang.map(plBarangNama).join(' + ') || (g.baris[0] && g.baris[0].namaProduk) || 'nota', n: g.n, baris: g.baris.length })), kecil, notaBesar: atur.notaBesar, dipilih: N ? N.kunci : null, isi, barang, tebak, waktu: waktuD, adaIsi: isi.length > 0 };
}
/** "Ini dia": nota tanpa nama ditempelkan ke orangnya — semua baris nota itu ditulis ulang dengan namaPelanggan (rupiahnya tidak berubah). */
export function susunIniDia(kini, notaKunci, kunciOrang) {
  const iso = hariIniIso(kini); const baris = ambilPenjualan().filter((p) => p.tanggal === iso && String(p.grupNota || p.id) === String(notaKunci)); if (!baris.length) return { tolak: 'Nota itu sudah tidak ada' };
  if (baris.some((p) => String(p.namaPelanggan || '').trim())) return { tolak: 'Nota itu sudah bernama' };
  const o = semuaOrang(kini).find((b) => b.kunci === kunciOrang); if (!o) return { tolak: 'Orangnya tidak ditemukan' };
  return { dokumen: baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { namaPelanggan: o.nama }) })), patch: { kabar: 'Nota ' + (baris[0].jam || '') + ' ' + RP(baris.reduce((a, p) => a + (p.hargaTotal || 0), 0)) + ' ditempelkan ke ' + o.nama + ' — kedatangannya ikut tercatat, uangnya tidak berubah.', kabarAwas: false } };
}
/** Tab JAM DINDING: tiap orang duduk di jam biasanya ia datang (06–17). */
export function susunJam(kini) {
  const semua = semuaOrang(kini); const J = kini.getHours(); const titik = (jam, r) => { const a = ((jam % 12) / 12) * 2 * Math.PI - Math.PI / 2; return { kiri: Math.round((50 + r * Math.cos(a)) * 10) / 10, atas: Math.round((50 + r * Math.sin(a)) * 10) / 10 }; };
  const perJam = {}; const orang = semua.filter((b) => b.jam !== null && b.dikenali).sort((a, b) => b.kunjungan - a.kunjungan).map((b) => { const ke = perJam[b.jam] = (perJam[b.jam] || 0) + 1; const t = titik(b.jam, 36.5 - (ke - 1) * 13); return Object.assign({}, b, t, { lapis: ke, dekat: Math.abs(b.jam - J) <= 1 && !b.hariIni }); });
  const angka = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17].map((j) => Object.assign({ t: j, kini: j === J }, titik(j, 47.5)));
  const sekitar = semua.filter((b) => b.jam !== null && Math.abs(b.jam - J) <= 1).sort((a, b) => (b.diharap ? 1 : 0) - (a.diharap ? 1 : 0) || b.kunjungan - a.kunjungan).map((b) => Object.assign({}, b, { sub: julukan(b), datang: datangTeks(b), jamTeks: jamTeks(b) }));
  return { orang, angka, sudut: Math.round((((J % 12) + kini.getMinutes() / 60) / 12) * 3600) / 10, sekitar, sekitarTeks: 'Biasa datang sekitar jam ' + (J - 1) + '–' + (J + 1), tanpaJam: semua.filter((b) => b.jam === null || !b.dikenali).length };
}
/** Tab MINGGU: hari langganan (orang warung belanja di hari yang sama tiap minggu). */
export function susunMinggu(kini) {
  const semua = semuaOrang(kini); const H = hariMingguKe(hariIniIso(kini)); const bagian = (b, i) => (b.kunjungan > 0 ? b.hari[i] / b.kunjungan : 0);
  const daftar = semua.filter((b) => b.kunjungan >= 3).sort((a, b) => bagian(b, H) - bagian(a, H) || b.kunjungan - a.kunjungan).map((b) => Object.assign({}, b, { kali: b.hari[H] + ' dari ' + b.kunjungan + ' kali datangnya hari ' + HARI_PANJANG[H], kuat: bagian(b, H) >= 0.5, sel: b.hari.map((h, i) => ({ n: h, kelas: h === 0 ? 'nol' : bagian(b, i) >= 0.5 ? 'besar' : bagian(b, i) >= 0.25 ? 'sedang' : 'kecil', kini: i === H })) }));
  return { hariKe: H, hariNama: HARI_PANJANG[H], daftar, kuat: daftar.filter((d) => d.kuat).map((d) => d.nama), kurang: semua.filter((b) => b.kunjungan < 3).length };
}
// ====================== BENANG: yang datang bukan orangnya (pelangganTitip) ======================
export function susunBenang(kini, siapa) {
  const semua = semuaOrang(kini); const orang = (k) => semua.find((b) => b.kunci === k) || null; const titip = cacheMentah('titip').filter((t) => orang(t.dari) && orang(t.untuk));
  const SISI = 5; const jadiUntuk = {}; titip.forEach((t) => { jadiUntuk[t.untuk] = true; }); const kiri = [], kanan = [];
  titip.slice().sort((a, b) => (b.kali || 0) - (a.kali || 0)).forEach((t) => { const d = jadiUntuk[t.dari] ? kanan : kiri; if (d.indexOf(t.dari) < 0) d.push(t.dari); if (kanan.indexOf(t.untuk) < 0) kanan.push(t.untuk); });
  const kutub = (sudut, r) => { const a = (sudut * Math.PI) / 180; return { kiri: Math.round((50 + r * Math.cos(a)) * 10) / 10, atas: Math.round((50 + r * Math.sin(a)) * 10) / 10 }; }; const pos = {};
  const taruh = (d, kn) => d.forEach((id, i) => { const langkah = Math.min(40, 160 / d.length); const geser = (i - (d.length - 1) / 2) * langkah; pos[id] = kutub(kn ? geser : 180 - geser, 34); }); taruh(kiri.slice(0, SISI), false); taruh(kanan.slice(0, SISI), true);
  const tampil = titip.filter((t) => pos[t.dari] && pos[t.untuk]); const terlibat = kiri.slice(0, SISI).concat(kanan.slice(0, SISI)).filter((id) => tampil.some((t) => t.dari === id || t.untuk === id)); const S = terlibat.indexOf(siapa) >= 0 ? siapa : null;
  const nm = (k) => (orang(k) ? orang(k).nama : k);
  return { pin: terlibat.map((id) => Object.assign({}, orang(id), pos[id], { pendek: nm(id).split(/\s+/).slice(0, 2).join(' '), aktif: S === id })),
    tali: tampil.map((t) => { const a = pos[t.dari], b = pos[t.untuk]; const dx = b.kiri - a.kiri, dy = b.atas - a.atas; return { kiri: a.kiri, atas: a.atas, panjang: Math.round(Math.sqrt(dx * dx + dy * dy) * 10) / 10, sudut: Math.round((Math.atan2(dy, dx) * 180) / Math.PI * 10) / 10, tkiri: Math.round((a.kiri + dx * 0.4) * 10) / 10, tatas: Math.round((a.atas + dy * 0.4) * 10) / 10, kali: (t.kali || 1) + '×', redup: !!S && t.dari !== S && t.untuk !== S }; }),
    baris: titip.filter((t) => !S || t.dari === S || t.untuk === S).map((t) => ({ id: t.id, teks: nm(t.dari) + ' datang untuk ' + nm(t.untuk), ket: (t.apa || '') + ' · sudah ' + (t.kali || 1) + ' kali' + (orang(t.untuk).utang > 0 ? ' · bon ' + nm(t.untuk) + ' ' + RP(orang(t.untuk).utang) : ''), dari: t.dari, untuk: t.untuk })),
    sembunyi: titip.length - tampil.length, siapa: S, judul: S ? 'Benang milik ' + nm(S) : 'Semua benang · ' + titip.length, semua: semua.map((b) => ({ kunci: b.kunci, nama: b.nama })), jenis: aturPelanggan().titipDaftar };
}
export function susunTitip(dari, untuk, apa, w) {
  if (!dari) return { tolak: 'Pilih siapa yang datang' }; if (!untuk) return { tolak: 'Pilih ia datang untuk siapa' }; if (dari === untuk) return { tolak: 'Orang yang sama — itu bukan titipan' };
  if (!apa || aturPelanggan().titipDaftar.indexOf(apa) < 0) return { tolak: 'Pilih urusannya apa' };
  const ada = cacheMentah('titip').find((t) => t.dari === dari && t.untuk === untuk && t.apa === apa) || null; const semua = semuaOrang(new Date()); const nm = (k) => { const o = semua.find((b) => b.kunci === k); return o ? o.nama : k; };
  const data = ada ? Object.assign({}, ada, { kali: (ada.kali || 1) + 1, tanggal: w.tanggal, jam: w.jam }) : { id: w.idUnik(), dari, untuk, apa, kali: 1, tanggal: w.tanggal, jam: w.jam };
  return { dokumen: [{ koleksi: 'pelangganTitip', data }], patch: { kabar: (ada ? 'Dicatat lagi: ' : 'Benang baru: ') + nm(dari) + ' datang untuk ' + nm(untuk) + ' (' + apa + ', ' + data.kali + ' kali). Nota, bon, dan pembayarannya TETAP atas nama ' + nm(untuk) + '.', kabarAwas: false } };
}
export function susunTitipLagi(id, w) { const t = cacheMentah('titip').find((x) => String(x.id) === String(id)); if (!t) return { tolak: 'Benang itu sudah tidak ada' }; return susunTitip(t.dari, t.untuk, t.apa, w); }
export function susunBuangTitip(id) { const t = cacheMentah('titip').find((x) => String(x.id) === String(id)); if (!t) return { tolak: 'Benang itu sudah tidak ada' }; return { hapus: [{ koleksi: 'pelangganTitip', id: t.id }], patch: { kabar: 'Benang dibuang', kabarAwas: false } }; }
// ====================== HAFALAN: karyawan belajar mengenali ======================
/** kuis = {putaran, no, jawab, benar, salah[], hanya|null}; pengecoh = yang cirinya paling mirip. */
export function susunHafalan(kini, kuis) {
  const semua = semuaOrang(kini); const bisa = semua.filter((b) => b.cip.length > 0); const urutId = (a, b) => (a.kunci < b.kunci ? -1 : 1); const q = kuis || { putaran: 1, no: 0, jawab: null, benar: 0, salah: [], hanya: null };
  const dek = bisa.filter((b) => !q.hanya || q.hanya.indexOf(b.kunci) >= 0).sort((a, b) => acak(q.putaran + ':' + a.kunci) - acak(q.putaran + ':' + b.kunci) || urutId(a, b));
  const K = q.no < dek.length ? dek[q.no] : null; const sama = (a, b) => a.cip.filter((c) => b.cip.indexOf(c) >= 0).length;
  const pengecoh = K ? bisa.filter((b) => b.kunci !== K.kunci).sort((a, b) => sama(b, K) - sama(a, K) || acak(q.no + ':' + a.kunci) - acak(q.no + ':' + b.kunci) || urutId(a, b)).slice(0, 2) : [];
  const pilihan = K ? pengecoh.concat([K]).sort((a, b) => acak(q.putaran + 'p' + q.no + ':' + a.kunci) - acak(q.putaran + 'p' + q.no + ':' + b.kunci) || urutId(a, b)) : []; const sudah = q.jawab !== null && q.jawab !== undefined;
  return { kartu: K ? Object.assign({}, K, { sk: sketsa(K), tulisan: sudah ? K.nama : 'siapa ini?', ciriTeks: K.cip.join(' · '), jamBiasa: K.jam === null ? 'jam datangnya belum tercatat' : 'biasanya datang ' + K.waktu + ' (±' + String(K.jam).padStart(2, '0') + '.00)', beliBiasa: K.biasa ? 'biasa beli: ' + K.biasa : K.pola.length ? 'biasa beli: ' + K.pola.slice(0, 2).map(plBarangNama).join(', ') : 'belum terbaca apa yang biasa dibelinya' }) : null,
    pilihan: pilihan.map((b) => ({ kunci: b.kunci, nama: b.nama, benar: !!K && b.kunci === K.kunci, dipilih: q.jawab === b.kunci })), sudah, dek: dek.length, kosong: dek.length === 0, selesai: !K && dek.length > 0, no: q.no, benar: q.benar, salah: q.salah.filter((id, i, a) => a.indexOf(id) === i).map((id) => semua.find((b) => b.kunci === id)).filter(Boolean),
    hasil: !sudah || !K ? '' : q.jawab === K.kunci ? 'Betul — ' + K.nama + '.' : 'Bukan. Ini ' + K.nama + ' — ' + K.cip.slice(0, 3).join(', ') + '.', tanpaCiri: semua.length - bisa.length };
}
// ====================== KARTU, ORANG BARU, GABUNG ======================
export function kartuOrang(kini, kunci) {
  const semua = semuaOrang(kini); const b = semua.find((x) => x.kunci === kunci); if (!b) return null;
  return Object.assign({}, b, { sk: sketsa(b), ringkas: b.kunjungan + ' kali datang · belanja ' + RP(b.total) + (b.utang > 0 ? ' · bon ' + RP(b.utang) : ''), datang: datangTeks(b) + (b.jam !== null ? ' · ' + b.waktu : ''), polaTeks: b.pola.slice(0, 3).map(plBarangNama).join(', '),
    bonTeks: b.dikenali ? 'Dikenali → kasir BOLEH mencatat bon baru atas namanya.' : 'Belum dikenali → kasir MENOLAK bon baru (aturan KR1). Isi salah satu: ciri, catatan, atau arah datangnya.', ciriDaftar: aturPelanggan().ciriDaftar, arahDaftar: aturPelanggan().arahDaftar });
}
/** Simpan kartu: isi = {nama, cip[], catatan, arah, asli, kontak, biasa}. Dokumen persis simpanCatatanPelanggan (+ kolom baru); ejaan nama boleh dirapikan selama kuncinya sama. */
export function susunSimpanKartu(kini, kunci, isi, w) {
  const nama = String(isi.nama || '').trim(); if (nama.length < 2) return { tolak: 'Namanya terlalu pendek — minimal dua huruf' };
  if (kunciPelanggan(nama) !== kunci) return { tolak: 'Mengganti nama = memindahkan semua nota & bon ke nama lain — pakai SATUKAN dari daftar nama kembar, atau tambah sebagai orang baru' };
  const cip = (Array.isArray(isi.cip) ? isi.cip : []).map((x) => String(x).trim()).filter((x, i, a) => x && a.indexOf(x) === i); const lama = kartuTersimpan(kunci); const kontak = String(isi.kontak || '').trim();
  if (kontak && kontak.replace(/\D/g, '').length < 9) return { tolak: 'Nomor WhatsApp-nya kurang panjang' };
  const data = Object.assign({}, lama ? lama.dok : {}, { id: kunci, nama, catatan: String(isi.catatan || '').trim(), ciri: cip.join(' · '), rute: String(isi.arah || '').trim(), cip, arah: String(isi.arah || '').trim(), asli: String(isi.asli || '').trim(), kontak, biasa: String(isi.biasa || '').trim(), diubahPada: w.kini });
  return { dokumen: [{ koleksi: 'pelangganCatatan', data }], dikenali: catatanPelangganBerisi(data), patch: { kabar: 'Kartu ' + nama + ' tersimpan' + (catatanPelangganBerisi(data) ? ' — dikenali, kasir boleh mencatat bon atas namanya.' : ' TANPA ciri, catatan, maupun arah — selama kosong, kasir menolak bon baru untuk ' + nama + '.'), kabarAwas: !catatanPelangganBerisi(data) } };
}
export function orangMirip(kini, nama) { const nb = String(nama || '').trim(); if (nb.length < 3) return []; const c = plPolos(nb); return semuaOrang(kini).filter((b) => { const a = plPolos(b.nama); return a && c && (a === c || (' ' + a + ' ').indexOf(' ' + c + ' ') >= 0 || (' ' + c + ' ').indexOf(' ' + a + ' ') >= 0); }).map((b) => ({ kunci: b.kunci, nama: b.nama, sub: julukan(b) })); }
export function susunOrangBaru(kini, nama, w) {
  const nb = String(nama || '').trim(); if (nb.length < 2) return { tolak: 'Ketik namanya (minimal dua huruf)' }; const k = kunciPelanggan(nb);
  if (semuaOrang(kini).some((b) => b.kunci === k)) return { tolak: 'Nama itu sudah ada — buka kartunya' };
  return { dokumen: [{ koleksi: 'pelangganCatatan', data: { id: k, nama: nb, catatan: '', ciri: '', rute: '', cip: [], arah: '', asli: '', kontak: '', biasa: '', diubahPada: w.kini } }], kunci: k, patch: { kabar: 'Ditambahkan: ' + nb + '. Isi cirinya supaya bisa dikenali lagi.', kabarAwas: false } };
}
export const BATAS_DOKUMEN_GABUNG = 180;   // satu writeBatch Firestore = 500 tulisan, tiap dokumen + baris log = 2 → aman di bawah 200
/** Rincian sebelum SATUKAN: berapa dokumen yang akan ditulis ulang atas nama yang dipakai. */
export function rincianGabung(kini, kunciPakai, kunciLain) {
  const semua = semuaOrang(kini); const P = semua.find((b) => b.kunci === kunciPakai), L = semua.find((b) => b.kunci === kunciLain); if (!P || !L) return { tolak: 'Salah satu nama sudah tidak ada' }; if (P.kunci === L.kunci) return { tolak: 'Itu nama yang sama' };
  const milikL = (nm) => kunciPelanggan(nm) === L.kunci; const penjualan = ambilPenjualanSemua().filter((p) => milikL(p.namaPelanggan)); const piutang = ambilPiutangMutasi().filter((m) => milikL(m.namaPelanggan)); const pesanan = ambilPesanan().filter((p) => milikL(p.namaPelanggan || p.nama));
  const thr = ambilThrPelanggan().filter((t) => t.kunci === L.kunci || milikL(t.nama)); const titip = cacheMentah('titip').filter((t) => t.dari === L.kunci || t.untuk === L.kunci); const tagih = cacheMentah('tagih').filter((t) => t.kunci === L.kunci); const kartuL = kartuTersimpan(L.kunci);
  const n = penjualan.length + piutang.length + pesanan.length + thr.length + titip.length + tagih.length + (kartuL ? 1 : 0) + 1;
  return { pakai: P, lain: L, penjualan, piutang, pesanan, thr, titip, tagih, kartuL, n, bisa: n <= BATAS_DOKUMEN_GABUNG, arti: 'Semua nota, bon, dan catatan "' + L.nama + '" pindah ke "' + P.nama + '": jadi ' + (P.kunjungan + L.kunjungan) + ' kali datang, belanja ' + RP(P.total + L.total) + (P.utang + L.utang > 0 ? ', bon ' + RP(P.utang + L.utang) : '') + '. ' + n + ' dokumen ditulis ulang namanya; tidak ada rupiah yang berubah.' + (n > BATAS_DOKUMEN_GABUNG ? ' TERLALU BANYAK untuk satu kali tulis (batas ' + BATAS_DOKUMEN_GABUNG + ') — biarkan terpisah.' : '') };
}
export function susunGabung(kini, kunciPakai, kunciLain, w) {
  const r = rincianGabung(kini, kunciPakai, kunciLain); if (r.tolak) return r; if (!r.bisa) return { tolak: r.n + ' dokumen atas nama "' + r.lain.nama + '" — terlalu banyak untuk disatukan sekali tulis (batas ' + BATAS_DOKUMEN_GABUNG + '). Biarkan terpisah.' };
  const P = r.pakai, L = r.lain; const dokumen = []; const hapus = [];
  r.penjualan.forEach((p) => dokumen.push({ koleksi: 'penjualan', data: Object.assign({}, p, { namaPelanggan: P.nama }) })); r.piutang.forEach((m) => dokumen.push({ koleksi: 'piutangMutasi', data: Object.assign({}, m, { namaPelanggan: P.nama }) }));
  r.pesanan.forEach((p) => dokumen.push({ koleksi: 'pesanan', data: Object.assign({}, p, { namaPelanggan: P.nama }) })); r.thr.forEach((t) => dokumen.push({ koleksi: 'thrPelanggan', data: Object.assign({}, t, { kunci: P.kunci, nama: P.nama }) }));
  r.tagih.forEach((t) => dokumen.push({ koleksi: 'tagihPelanggan', data: Object.assign({}, t, { kunci: P.kunci, nama: P.nama }) }));
  r.titip.forEach((t) => { const d = t.dari === L.kunci ? P.kunci : t.dari, u = t.untuk === L.kunci ? P.kunci : t.untuk; if (d === u) hapus.push({ koleksi: 'pelangganTitip', id: t.id }); else dokumen.push({ koleksi: 'pelangganTitip', data: Object.assign({}, t, { dari: d, untuk: u }) }); });
  const kP = kartuTersimpan(P.kunci), kL = r.kartuL; const gab = (a, b) => (a || b || '');
  const kartu = Object.assign({}, kP ? kP.dok : {}, { id: P.kunci, nama: P.nama, cip: (kP ? kP.cip : []).concat((kL ? kL.cip : []).filter((c) => !(kP && kP.cip.indexOf(c) >= 0))), catatan: [kP ? kP.catatan : '', kL ? kL.catatan : '', 'dulu juga tercatat sebagai "' + L.nama + '"'].filter(Boolean).join(' · '), arah: gab(kP && kP.arah, kL && kL.arah), asli: gab(kP && kP.asli, kL && kL.asli), kontak: gab(kP && kP.kontak, kL && kL.kontak), biasa: gab(kP && kP.biasa, kL && kL.biasa), diubahPada: w.kini });
  kartu.ciri = kartu.cip.join(' · '); kartu.rute = kartu.arah; dokumen.push({ koleksi: 'pelangganCatatan', data: kartu }); if (kL) hapus.push({ koleksi: 'pelangganCatatan', id: kL.dok.id });
  return { dokumen, hapus, patch: { kabar: '"' + L.nama + '" disatukan ke "' + P.nama + '" — ' + dokumen.length + ' dokumen ditulis ulang namanya, rupiah tidak berubah.', kabarAwas: false } };
}
export function susunBukanKembar(k, w) { const bukan = plBukanKembar(); if (bukan.indexOf(k) >= 0) return { tolak: 'Sudah dicatat' }; return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'pelangganKembar', tanggal: w.tanggal, jam: w.jam, bukan: bukan.concat([k]) } }], patch: { kabar: 'Dicatat: dua orang yang berbeda — tidak ditawarkan lagi', kabarAwas: false } }; }

// ====================== PL3 · THR PELANGGAN SETIA ======================
export function susunThr(kini, tahun) {
  const semua = semuaOrang(kini); const atur = aturPelanggan(); const Th = Number(tahun) || kini.getFullYear(); const thr = ambilThrPelanggan();
  const ini = (k) => thr.find((t) => t.kunci === k && Number(t.tahun) === Th) || null; const lalu = (k) => thr.find((t) => t.kunci === k && Number(t.tahun) === Th - 1) || null;
  const daftar = semua.map((o) => ({ o, belanja: o.tahun[String(Th)] || 0, ini: ini(o.kunci), lalu: lalu(o.kunci) })).sort((a, b) => b.belanja - a.belanja || b.o.kunjungan - a.o.kunjungan); daftar.forEach((b, i) => { b.no = i + 1; });
  const dapat = daftar.filter((b) => b.ini); const terpakai = dapat.reduce((a, b) => a + (Number(b.ini.nilai) || 0), 0); const diserahkan = dapat.filter((b) => b.ini.serah); const sisa = atur.anggaranThr - terpakai;
  const gambar = (b) => ({ kunci: b.o.kunci, no: b.no, nama: b.o.nama, belanja: b.belanja, belanjaTeks: b.belanja ? 'belanja ' + Th + ' ' + RP(b.belanja) + ' · ' + b.o.kunjungan + ' kali datang' : 'belum belanja di ' + Th, laluTeks: b.lalu ? 'tahun lalu: ' + b.lalu.bentuk : 'tahun lalu belum dapat', ada: !!b.ini, id: b.ini ? b.ini.id : null, bentuk: b.ini ? b.ini.bentuk : '', nilai: b.ini ? Number(b.ini.nilai) || 0 : 0, serah: !!(b.ini && b.ini.serah), status: !b.ini ? '' : b.ini.serah ? '✓ ' + b.ini.bentuk : 'rencana: ' + b.ini.bentuk });
  return { tahun: Th, daftar: daftar.map(gambar), dapat: dapat.map(gambar), belumDapat: daftar.filter((b) => !b.ini).map(gambar), terpakai, anggaran: atur.anggaranThr, sisa, diserahkan: diserahkan.length, meterIsi: Math.min(100, Math.round(diserahkan.reduce((a, b) => a + (Number(b.ini.nilai) || 0), 0) / Math.max(1, atur.anggaranThr) * 100)),
    meterRencana: Math.max(0, Math.min(100, Math.round(dapat.filter((b) => !b.ini.serah).reduce((a, b) => a + (Number(b.ini.nilai) || 0), 0) / Math.max(1, atur.anggaranThr) * 100))), bentuk: atur.bentukThr, ringkas: dapat.length + ' orang · ' + diserahkan.length + ' sudah diserahkan' };
}
export function usulThr(kini, tahun, bentukNama) { const t = susunThr(kini, tahun); const B = t.bentuk.find((x) => x.nama === bentukNama) || t.bentuk[0] || null; const muat = B && B.n > 0 ? Math.max(0, Math.floor(t.sisa / B.n)) : 0; const calon = t.belumDapat.filter((b) => b.belanja > 0).slice(0, muat);
  return { bentuk: B, muat, calon, teks: !B ? 'Belum ada bentuk THR — tambah di Atur.' : t.sisa <= 0 ? 'Amplopnya sudah habis.' : !calon.length ? 'Tidak ada lagi yang bisa diusulkan — sisanya tidak cukup untuk satu ' + B.nama + ', atau semua sudah kebagian.' : 'Sisa ' + RP(t.sisa) + ' cukup untuk ' + muat + ' ' + B.nama + ' → ' + calon.length + ' orang teratas yang belum kebagian: ' + calon.map((b) => b.nama).join(', ') + '.' }; }
const thDok = (o, Th, bentuk, nilai, w) => ({ id: w.idUnik(), tahun: Th, kunci: o.kunci, nama: o.nama, bentuk, nilai, tanggal: w.tanggal, jam: w.jam, serah: false });
export function susunBeriThr(kini, kunci, tahun, bentuk, nilai, w) {
  const Th = Number(tahun); if (!(Th >= 2020 && Th <= 2100)) return { tolak: 'Tahunnya tidak wajar' }; const o = semuaOrang(kini).find((b) => b.kunci === kunci); if (!o) return { tolak: 'Orangnya tidak ditemukan' };
  if (ambilThrPelanggan().some((t) => t.kunci === kunci && Number(t.tahun) === Th)) return { tolak: 'THR ' + Th + ' untuk ' + o.nama + ' sudah tercatat — hapus dulu kalau salah' }; const bt = String(bentuk || '').trim(); if (!bt) return { tolak: 'Bentuknya wajib — supaya tahun depan terbaca siapa dapat apa' };
  const n = Math.max(0, plAngka(nilai)); const t = susunThr(kini, Th); return { dokumen: [{ koleksi: 'thrPelanggan', data: thDok(o, Th, bt, n, w) }], lewat: n > t.sisa ? n - t.sisa : 0, patch: { kabar: o.nama + ' direncanakan dapat ' + bt + (n ? ' (±' + RP(n) + ')' : '') + ' untuk THR ' + Th + (n > t.sisa ? ' — amplop ' + Th + ' lewat ' + RP(n - t.sisa) : '') + '. Ini catatan siapa dapat apa, bukan catatan uang.', kabarAwas: false } };
}
export function susunUsulThr(kini, tahun, bentukNama, w) { const u = usulThr(kini, tahun, bentukNama); if (!u.calon.length) return { tolak: u.teks }; const semua = semuaOrang(kini);
  return { dokumen: u.calon.map((c) => ({ koleksi: 'thrPelanggan', data: thDok(semua.find((b) => b.kunci === c.kunci), Number(tahun), u.bentuk.nama, u.bentuk.n, w) })), patch: { kabar: u.calon.length + ' orang direncanakan dapat ' + u.bentuk.nama + '. Centang satu-satu waktu bingkisannya diserahkan.', kabarAwas: false } }; }
export function susunSerahThr(id, w) { const t = ambilThrPelanggan().find((x) => String(x.id) === String(id)); if (!t) return { tolak: 'Catatan THR itu sudah tidak ada' }; const serah = !t.serah;
  return { dokumen: [{ koleksi: 'thrPelanggan', data: Object.assign({}, t, { serah, serahTanggal: serah ? w.tanggal : null }) }], patch: { kabar: serah ? t.bentuk + ' untuk ' + t.nama + ' dicatat sudah diserahkan' : 'Centang ' + t.nama + ' dibatalkan', kabarAwas: false } }; }
export function susunHapusThr(id) { const t = ambilThrPelanggan().find((x) => String(x.id) === String(id)); if (!t) return { tolak: 'Catatan THR itu sudah tidak ada' }; return { hapus: [{ koleksi: 'thrPelanggan', id: t.id }], patch: { kabar: 'Catatan THR ' + t.tahun + ' ' + t.nama + ' dihapus', kabarAwas: false } }; }
