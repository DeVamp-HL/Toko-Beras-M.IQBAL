// RINCI KARCIS (putaran 20) — logika tanpa DOM. Karcis = nota kasir darurat yang cuma menyebut NOMINAL (jenis 'kasir_darurat_nominal', ditulis tablet /
// kasir-darurat-nominal.html) + nota kasir yang jumlahnya belum pasti (perluKoreksi). Owner merincinya jadi barang bertitel supaya stok terpotong & laba punya modal.
// Cara kerja di sistem baru: karcis DIIKAT ke keranjang Jual (seperti tukar), barangnya dipilih dari rak seperti menjual biasa (tebakan dari katalog sekali ketuk),
// lalu SIMPAN RINCIAN menulis bentuk dokumen yang SAMA dengan simpanRinciTrx() index.html: baris barang {grupNota, asalDarurat, rinciDari, koreksiDari, alasanKoreksi,
// dirinciPada}, sisa yang belum terurai = karcis baru bertanda sama (uang masuk tidak pernah hilang), karcis asli DITANDAI dikoreksiOleh (tidak dihapus). Yang ditolak
// hanya KELEBIHAN (barang > uang yang masuk) — aturan owner 9 Agu 2026 ([[rinci-darurat-fleksibel-scope]]). Tanggal & jam baris = tanggal & jam karcisnya (uangnya masuk hari itu).
// Rapikan (perluKoreksi): bentuk koreksi (koreksiDari + alasanKoreksi, tanpa asalDarurat) dan jumlahnya harus menutup nominal PERSIS (uang tetap).
// Tarik balik (urungkanRinciTrx): seluruh grup dibatalkan, catatan kantong id+1 dihapus, karcis asli dipulihkan — hanya bila grupnya masih utuh.
import { penjualanMasihBerlaku, bakuCaraBayar, hargaKarungUtuh, namaSingkatTrx, kunciKemasan } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilHargaLiteran, ambilHargaKemasan, tolakKunci, butuhGet, ingatStokKarung } from '../data/toko.js';
import { KP_BATAS_GET } from '../data/kunci-periode.js';
import { RP, hariIniIso, tanggalPendek, jamSetempat } from '../inti/format.js';
import { susunRak, masukkan, terapkanNego, periksaStokKeranjang, pecahItemsWadah, aturWadah, angkaRupiah } from './jual-logika.js';
import { wbLiteranLangsung } from './wadah-bernama-logika.js';
import { koleksiWadah } from './wadah-jual-logika.js';
import { skPecah, skHapusPemecah } from './setengah-logika.js';
import { tolakBatalReturBon } from './retur-logika.js';
import { ngAtur } from './nego-logika.js';

const KC_TERKUNCI = 'karcis ini tidak bisa dirinci lagi; stok yang terlanjur keluar dibetulkan lewat Stok › Cocokkan hari ini';
const KC_TOLERANSI_BULAT = 500;   // literan: pecahan di bawah Rp500 tidak terpakai di lapangan (kandidatDarurat 32170)
const kcEkor = (id) => '#' + String(id).slice(-4);

/** Karcis & nota kasir yang menunggu dirinci/dirapikan — hanya yang masih berlaku (sisa hasil rinci ikut, ia karcis juga). Terbaru dulu. */
export function daftarKarcis(kini) {
  const iso = hariIniIso(kini); const daftar = [];
  ambilPenjualan().forEach((p) => {
    const karcis = p.jenis === 'kasir_darurat_nominal'; if (!karcis && !p.perluKoreksi) return;
    daftar.push({ id: String(p.id), asliId: p.id, jenisAsal: karcis ? 'karcis' : 'rapikan', tanggal: p.tanggal || '', jam: p.jam || '', nominal: Math.round(p.hargaTotal || 0), cara: bakuCaraBayar(p.caraBayar), nama: String(p.namaPelanggan || '').trim(),
      oleh: String(p.operator || p.oleh || '').trim(), sisaDari: p.asalDarurat && p.rinciDari ? String(p.rinciDari) : null, hariIni: p.tanggal === iso,
      teks: karcis ? (p.asalDarurat ? 'Sisa karcis ' + kcEkor(p.rinciDari || p.id) + ' yang belum diurai' : 'Karcis ' + kcEkor(p.id)) : namaSingkatTrx(p) + ' · jumlah belum pasti' });
  });
  daftar.sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam));
  return { daftar, nKarcis: daftar.filter((d) => d.jenisAsal === 'karcis').length, nRapikan: daftar.filter((d) => d.jenisAsal === 'rapikan').length, total: daftar.reduce((a, d) => a + (d.jenisAsal === 'karcis' ? d.nominal : 0), 0) };
}

/** Tebakan dari katalog untuk satu nominal — kandidatDarurat + kombinasiDarurat sistem lama: literan kelipatan 0,5 L (toleransi bulat Rp500, harga PAS dibawa), kemasan 1–6, karung 50/25 1–4, kombinasi 2–3 barang yang jumlahnya persis. */
export function tebakanKarcis(nominal) {
  const n = Math.round(Number(nominal) || 0); if (!(n > 0)) return [];
  // putaran 27: harga liter yang dipakai rak = wadah + merek literan langsung
  const hasil = []; const stokK = ingatStokKarung(); const lk = aturWadah().daftar.concat(wbLiteranLangsung().daftar); const literan = ambilHargaLiteran().filter((h) => h.hargaPerLiter > 0 && lk.indexOf(h.merk) >= 0); const kemasan = ambilHargaKemasan().filter((h) => h.hargaPerUnit > 0);
  literan.forEach((h) => { const L = Math.round(n / h.hargaPerLiter * 2) / 2; if (!(L >= 0.5 && L <= 40)) return; const katalog = Math.round(L * h.hargaPerLiter); const selisih = n - katalog;
    if (selisih === 0) hasil.push({ tepat: true, label: h.merk + ' ' + String(L).replace('.', ',') + ' L', isi: [{ jalur: 'literan', kunci: h.merk, jumlah: L }] });
    else if (Math.abs(selisih) < KC_TOLERANSI_BULAT) hasil.push({ tepat: false, label: h.merk + ' ' + String(L).replace('.', ',') + ' L · bulat ' + (selisih > 0 ? '+' : '−') + RP(Math.abs(selisih)), isi: [{ jalur: 'literan', kunci: h.merk, jumlah: L, hargaPas: n }] }); });
  kemasan.forEach((h) => { const u = Math.round(n / h.hargaPerUnit); if (u >= 1 && u <= 6 && u * h.hargaPerUnit === n) hasil.push({ tepat: true, label: h.merk + ' ' + h.ukuran + ' kg × ' + u, isi: [{ jalur: 'kemasan', kunci: kunciKemasan(h.merk, h.ukuran), jumlah: u }] }); });
  Object.keys(stokK).forEach((merk) => { [50, 25].forEach((b) => { const hu = (hargaKarungUtuh(merk, b) || {}).perUnit || 0; if (!(hu > 0)) return; const k = Math.round(n / hu); if (k >= 1 && k <= 4 && k * hu === n) hasil.push({ tepat: true, label: 'Karung ' + b + ' kg ' + merk + ' × ' + k, isi: [{ jalur: 'karung', kunci: merk, berat: b, jumlah: k }] }); }); });
  hasil.sort((a, b) => (b.tepat ? 1 : 0) - (a.tepat ? 1 : 0));
  // kolam untuk kombinasi (penjaga kasir darurat mencatat total per pembeli, bukan per barang — aturan lapangan 8 Agu 2026)
  const kolam = [];
  literan.forEach((h) => { for (let L = 1; L <= 25; L++) kolam.push({ jalur: 'literan', kunci: h.merk, jumlah: L, harga: h.hargaPerLiter * L, label: h.merk + ' ' + L + ' L', jangkar: false }); });
  kemasan.forEach((h) => { for (let u = 1; u <= 3; u++) kolam.push({ jalur: 'kemasan', kunci: kunciKemasan(h.merk, h.ukuran), jumlah: u, harga: h.hargaPerUnit * u, label: h.merk + ' ' + h.ukuran + ' kg × ' + u, jangkar: true }); });
  Object.keys(stokK).forEach((merk) => { [50, 25].forEach((b) => { const hu = (hargaKarungUtuh(merk, b) || {}).perUnit || 0; if (!(hu > 0)) return; for (let k = 1; k <= 2; k++) kolam.push({ jalur: 'karung', kunci: merk, berat: b, jumlah: k, harga: hu * k, label: 'Karung ' + b + ' ' + merk + ' × ' + k, jangkar: true }); }); });
  const isiDari = (x) => ({ jalur: x.jalur, kunci: x.kunci, berat: x.berat, jumlah: x.jumlah });
  const kecil = kolam.filter((x) => x.harga < n); const kombo = [];
  for (let i = 0; i < kecil.length && kombo.length < 6; i++) for (let j = i + 1; j < kecil.length && kombo.length < 6; j++) { if (kecil[i].harga + kecil[j].harga === n && (kecil[i].jalur + kecil[i].kunci + (kecil[i].berat || '')) !== (kecil[j].jalur + kecil[j].kunci + (kecil[j].berat || ''))) kombo.push({ tepat: true, label: kecil[i].label + ' + ' + kecil[j].label, isi: [isiDari(kecil[i]), isiDari(kecil[j])] }); }
  const jangkar = kecil.filter((x) => x.jangkar); const lit = kecil.filter((x) => x.jalur === 'literan' && x.jumlah <= 10);
  for (let a = 0; a < jangkar.length && kombo.length < 6; a++) for (let i = 0; i < lit.length && kombo.length < 6; i++) for (let j = i + 1; j < lit.length && kombo.length < 6; j++) { if (jangkar[a].harga + lit[i].harga + lit[j].harga === n && lit[i].kunci !== lit[j].kunci) kombo.push({ tepat: true, label: jangkar[a].label + ' + ' + lit[i].label + ' + ' + lit[j].label, isi: [isiDari(jangkar[a]), isiDari(lit[i]), isiDari(lit[j])] }); }
  return kelompokkanTebakan(hasil).slice(0, 6).concat(kelompokkanTebakan(kombo));
}
// putaran 31.1 (serah terima 28 Sep): tebakan memilih NAMA dari harga, jadi IR64 Ascent/Elevate/Apex yang seharga tertukar dan hanya jumlah IR64 yang berarti
// (susut September). Dua nama atau lebih dengan bentuk yang sama (jalur, berat, jumlah, harga pas) untuk nominal itu = SATU tebakan yang BERTANYA namanya.
const kcBentuk = (t) => t.isi.map((x) => x.jalur + '|' + (x.berat || '') + '|' + x.jumlah + '|' + (x.hargaPas || '')).join('+') + '|' + (t.tepat ? 1 : 0);
/** Tebakan yang bentuknya sama tapi namanya beda (harga sama) digabung: { seharga: true, pilihan: [tebakan…] } — tidak memilih diam-diam. */
export function kelompokkanTebakan(daftar) {
  const out = []; (daftar || []).forEach((t) => { const b = kcBentuk(t); let g = out.find((x) => x.bentuk === b); if (!g) { g = { bentuk: b, tepat: t.tepat, pilihan: [] }; out.push(g); } g.pilihan.push(t); });
  return out.map((g) => (g.pilihan.length === 1 ? g.pilihan[0] : { tepat: g.tepat, seharga: true, pilihan: g.pilihan, label: g.pilihan.map((p) => p.label).join(' / ') + ' — harga sama, pilih namanya' }));
}

/** Ikat satu karcis ke keranjang (seperti tukar): satu karcis per keranjang, tidak bersama tukar/pesanan; cara bayar & nama pembeli diprakarsai dari karcisnya. */
export function ikatKarcis(s, id, kini) {
  const k = daftarKarcis(kini).daftar.find((x) => x.id === String(id)); if (!k) return { kabar: 'Karcis itu tidak ada lagi di antrean — sudah dirinci atau dibatalkan di perangkat lain', kabarAwas: true };
  if (s.karcis) return { kabar: 'Keranjang ini sedang merinci karcis ' + kcEkor(s.karcis.id) + ' — simpan atau lepas dulu', kabarAwas: true };
  if (s.tukar) return { kabar: 'Keranjang ini terikat tukar — catat notanya atau batal tukar dulu', kabarAwas: true };
  // tinjauan no. 9: karcis membawa nama & cara bayarnya sendiri — buka kredit SEKALI untuk nota sebelumnya tidak ikut
  return { karcis: k, cara: k.cara === 'QRIS' || k.cara === 'Kredit' ? k.cara : 'Tunai', pelanggan: k.nama, uang: 0, potongan: 0, pesananId: null, lembar: null, kreditDibuka: false, jalur: s.jalur === 'retur' ? 'sering' : s.jalur, negoId: null,
    kabar: (k.jenisAsal === 'karcis' ? 'Merinci karcis ' : 'Merapikan nota ') + kcEkor(k.id) + ' ' + RP(k.nominal) + ' (' + k.tanggal.slice(8) + '/' + k.tanggal.slice(5, 7) + ' ' + k.jam + ') — pilih barangnya dari rak seperti menjual biasa' + (s.keranjang.length ? '; ' + s.keranjang.length + ' barang yang sudah di keranjang ikut dihitung' : ''), kabarAwas: false };
}
export function lepasKarcis(s) { return s.karcis ? { karcis: null, kcPilih: null, kabar: 'Karcis dilepas — tidak ada yang ditulis; barang di keranjang tetap', kabarAwas: false } : {}; }

/** Isi keranjang dari satu tebakan: tiap barang lewat masukkan() (langit-langit stok tetap dijaga); harga PAS literan dipasang sebagai nego. */
export function pakaiTebakan(s, t) {
  // putaran 31.1: dua nama seharga → tawarkan pilihan, jangan ambil yang pertama
  if (t && t.seharga) return { kcPilih: t, kabar: t.pilihan.length + ' nama seharga untuk nominal ini (' + t.pilihan.map((p) => p.label).join(', ') + ') — ketuk namanya; tebakan tidak memilih sendiri', kabarAwas: false };
  let st = Object.assign({}, s); const rak = susunRak(st);
  // tinjauan 7 Okt: harga PAS = penjualan yang SUDAH terjadi — owner yang merinci tidak tunduk pada daftar "boleh di bawah modal" (alasannya tetap tercatat);
  // bukan-owner tetap lewat owner. Harga pas yang tidak bisa dipasang DISEBUT (dulu diam-diam tinggal harga katalog).
  const A = ngAtur(); const aturPas = Object.assign({}, A, { bawahModal: A.bawahModal.indexOf('owner') >= 0 ? A.bawahModal : A.bawahModal.concat(['owner']) }); const gagalPas = [];
  for (const x of t.isi) {
    const chip = (rak[x.jalur] || []).find((c) => c.kunci === x.kunci && (!x.berat || c.berat === x.berat)); if (!chip) return { kabar: x.kunci + ' tidak ada di rak (harga/stoknya tidak terbaca) — pilih barangnya sendiri', kabarAwas: true };
    const p = masukkan(Object.assign({}, st, { pilih: chip, ketik: '' }), x.jumlah); if (p.kabarAwas) return p;
    st = Object.assign(st, p);
    // owner 7 Okt (JS2-C): harga PAS karcis = penjualan yang SUDAH terjadi di kasir darurat — di bawah modal pun dicatat apa adanya, alasannya tertulis
    if (x.hargaPas) { const b = st.keranjang[st.keranjang.length - 1]; const q = terapkanNego(Object.assign({}, st, { negoAlasan: 'harga pas karcis kasir darurat', negoAtur: aturPas }), b.id, Math.round(x.hargaPas / x.jumlah)); if (q.keranjang) { st = Object.assign(st, q); const bb = st.keranjang[st.keranjang.length - 1]; if (bb.trx.hargaTotal !== x.hargaPas) bb.trx.hargaTotal = x.hargaPas; }
      else gagalPas.push(b.trx.label + ' ' + RP(x.hargaPas) + ': ' + String(q.kabar || 'tidak bisa dipasang')); }
  }
  return { keranjang: st.keranjang, urutBaris: st.urutBaris, pilih: null, lembar: null, ketik: '', kcPilih: null,
    kabar: 'Tebakan dipakai: ' + t.label + (gagalPas.length ? ' — harga pas BELUM terpasang (' + gagalPas.join('; ') + ')' : '') + ' — periksa lalu SIMPAN RINCIAN', kabarAwas: gagalPas.length > 0 };
}

// owner 11 Okt 2026: nominal karcis kasir darurat BOLEH dibetulkan saat merinci (naik atau turun, alasan wajib) — uang yang sungguh masuk bisa beda
// dari yang terketik di tablet (130.000 → 135.000). Draf menempel di karcis yang diikat (k.nominalBaru teks rupiah, k.alasanNominal): lepas / simpan = hilang.
// Hanya karcis nominal; nota yang dirapikan tetap menutup jumlahnya persis (uang nota tidak berubah).
/** Nominal yang berlaku untuk karcis yang sedang dirinci: { nominal, asli, diubah, selisih, alasan, sedangDiubah, salah }. */
export function nominalKarcis(k) {
  const asli = Math.round((k && k.nominal) || 0); const sedang = !!k && k.jenisAsal === 'karcis' && k.nominalBaru !== undefined && k.nominalBaru !== null;
  if (!sedang) return { nominal: asli, asli, diubah: false, selisih: 0, alasan: '', sedangDiubah: false, salah: false };
  const n = angkaRupiah(k.nominalBaru); const diubah = n > 0 && n !== asli;
  return { nominal: n > 0 ? n : asli, asli, diubah, selisih: diubah ? n - asli : 0, alasan: String(k.alasanNominal || '').trim(), sedangDiubah: true, salah: !(n > 0) };
}
/** Kalimat dampak uang dari nominal yang dibetulkan — dipakai di lembar Simpan rincian dan kabar sesudah simpan. */
export function teksDampakNominal(k, cara, nama) {
  const N = nominalKarcis(k); if (!N.diubah) return '';
  const naik = N.selisih > 0; const tgl = tanggalPendek(k.tanggal);
  return 'Nominal karcis ' + RP(N.asli) + ' → ' + RP(N.nominal) + ' (' + (naik ? '+' : '−') + RP(Math.abs(N.selisih)) + '): omzet ' + tgl + ' ' + (naik ? 'naik' : 'turun') + ' ' + RP(Math.abs(N.selisih))
    + (cara === 'Kredit' ? ', bon ' + (nama || 'pembeli') + ' ' + (naik ? 'bertambah' : 'berkurang') : cara === 'QRIS' ? ', uang QRIS hari itu ikut ' + (naik ? 'naik' : 'turun') : ', uang laci hari itu ' + (naik ? 'naik' : 'turun')) + ' ' + RP(Math.abs(N.selisih));
}
/** Buka / ketik / tutup draf nominal. nilai = teks rupiah atau angka (pil "ubah jadi Rp…"). */
export function bukaNominalKarcis(s, nilai) {
  const k = s.karcis; if (!k) return {}; if (k.jenisAsal !== 'karcis') return { kabar: 'Nota yang dirapikan tidak bisa diubah nominalnya — uang nota itu sudah pasti, barangnya yang menutup persis', kabarAwas: true };
  return { karcis: Object.assign({}, k, { nominalBaru: nilai !== undefined && nilai !== null && String(nilai) !== '' ? String(nilai) : String(k.nominal), alasanNominal: k.alasanNominal || '' }) };
}
export function ketikNominalKarcis(s, kolom, v) {
  const k = s.karcis; if (!k || k.nominalBaru === undefined) return {};
  return { karcis: Object.assign({}, k, kolom === 'alasan' ? { alasanNominal: String(v || '').slice(0, 120) } : { nominalBaru: String(v || '').slice(0, 15) }) };
}
export function tutupNominalKarcis(s) { const k = s.karcis; if (!k) return {}; const b = Object.assign({}, k); delete b.nominalBaru; delete b.alasanNominal; return { karcis: b }; }
/** Penjaga draf nominal yang dipakai SIMPAN RINCIAN & perbaikan karcis: '' = sah (atau tidak diubah). */
function tolakNominal(k) {
  const N = nominalKarcis(k); if (!N.sedangDiubah) return '';
  if (N.salah) return 'Nominal baru belum terbaca — ketik uang yang sebenarnya masuk (mis. 135000), atau tutup "ubah nominal"';
  if (N.diubah && N.alasan.length < 3) return 'Tulis alasan nominal diubah (mis. "salah ketik, harusnya 135.000") — jejaknya ikut tersimpan di karcis';
  return '';
}

/** Uang vs barang di keranjang saat merinci. Potongan nota TIDAK dipakai (harga barangnya yang dinego). Nominal = yang berlaku (bisa dibetulkan owner). */
export function hitungKarcis(s) {
  const k = s.karcis; if (!k) return null; const N = nominalKarcis(k); const total = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0); const sisa = N.nominal - total;
  return { k, N, nominal: N.nominal, total, sisa, lebih: sisa < 0, pas: sisa === 0 && total > 0, teks: !s.keranjang.length ? 'belum ada barang' : sisa === 0 ? 'PAS ' + RP(total) + ' — siap disimpan' : sisa > 0 ? 'Sisa ' + RP(sisa) + ' belum terurai — ' + (k.jenisAsal === 'karcis' ? 'boleh disimpan, sisanya tetap tercatat sebagai karcis' : 'rapikan harus menutup persis') : 'KELEBIHAN ' + RP(-sisa) + ' — hapus atau betulkan harga barang' + (k.jenisAsal === 'karcis' ? ', atau ubah nominal karcis kalau uang yang masuk memang ' + RP(total) : '') };
}

const kcBersih = (t) => { const d = Object.assign({}, t); ['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego', 'pecahan', '_takaran', 'setengahDari', 'setengahHargaBaru'].forEach((k) => { delete d[k]; }); return d; };
const kcPasangan = (d, w, dokumen) => {
  if (d.kemasanLiteran && d.jumlahKemasanLiteranDipakai > 0) dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: d.id + 1, tipe: 'pakai', jenis: d.kemasanLiteran, jumlah: d.jumlahKemasanLiteranDipakai, hargaTotal: 0, tanggal: d.tanggal, catatan: 'Otomatis dari rincian darurat id ' + d.id } });
  if (d.jenis === 'wadah' && d.jenisWadah && d.jumlahUnit > 0) dokumen.push({ koleksi: koleksiWadah(d.jenisWadah), data: { id: d.id + 1, tipe: 'pakai', jenis: d.jenisWadah, jumlah: d.jumlahUnit, hargaTotal: 0, tanggal: d.tanggal, catatan: 'Dijual sebagai barang di rincian id ' + d.id } });
  if (d.kemasanRepack && d.jumlahKemasanRepackDipakai > 0) dokumen.push({ koleksi: koleksiWadah(d.kemasanRepack), data: { id: d.id + 1, tipe: 'pakai', jenis: d.kemasanRepack, jumlah: d.jumlahKemasanRepackDipakai, hargaTotal: 0, tanggal: d.tanggal, catatan: 'Otomatis dari rincian repack id ' + d.id + ' (wadah ditanggung toko)' } });
};

/** SIMPAN RINCIAN — bentuk simpanRinciTrx() index.html 32587 (karcis) / koreksi (rapikan). {tolak} atau {dokumen, patch, ringkas, rinci}. */
export function susunRinciDokumen(s, w) {
  const k = s.karcis; if (!k) return { tolak: 'Tidak ada karcis yang sedang dirinci' };
  const p = ambilPenjualanSemua().find((x) => String(x.id) === k.id);
  if (!p || !penjualanMasihBerlaku(p)) return { tolak: 'Karcis ' + kcEkor(k.id) + ' sudah dirinci / dibatalkan di perangkat lain — lepas, lalu buka antrean lagi' };
  const kunci = tolakKunci('penjualan', p, KC_TERKUNCI); if (kunci) return { tolak: kunci, pembalik: 'cocok' };   // putaran 25
  if (!s.keranjang.length) return { tolak: 'Tambahkan barangnya dulu — atau ketuk salah satu tebakan' };
  if (s.tukar) return { tolak: 'Keranjang terikat tukar — batal tukar dulu' };
  if (Math.round(s.potongan || 0) > 0) return { tolak: 'Potongan nota tidak dipakai saat merinci — nego harga barangnya saja' };
  const cara = bakuCaraBayar(s.cara); const nama = String(s.pelanggan || '').trim();
  if (cara === 'Kredit' && !nama) return { tolak: 'Bon harus punya nama pembeli — tanpa nama, utangnya tidak bisa ditagih' };
  const tn = tolakNominal(k); if (tn) return { tolak: tn };   // owner 11 Okt: nominal dibetulkan → alasan wajib
  const H = hitungKarcis(s); if (H.lebih) return { tolak: 'Jumlah barang ' + RP(H.total) + ' KELEBIHAN ' + RP(-H.sisa) + ' dari nominal ' + RP(H.nominal) + ' — tidak boleh melebihi uang yang masuk' + (k.jenisAsal === 'karcis' ? '; kalau uangnya memang ' + RP(H.total) + ', ubah nominal karcisnya dulu (alasan wajib)' : '') };
  const N = H.N; const teksNominal = N.diubah ? 'nominal dibetulkan ' + RP(N.asli) + ' → ' + RP(N.nominal) + ': ' + N.alasan : '';
  if (k.jenisAsal === 'rapikan' && H.sisa !== 0) return { tolak: 'Merapikan harus menutup ' + RP(k.nominal) + ' persis (uang nota tetap) — sekarang ' + RP(H.total) };
  const stok = periksaStokKeranjang(s); if (stok) return { tolak: stok };
  const karcis = k.jenisAsal === 'karcis'; const idGrup = w.idUnik(); const kini = w.kini || new Date().toISOString(); const dokumen = []; const ids = []; const label = [];
  // putaran 27 (Bagian 5): literan wadah dipecah per merek asal persis seperti nota Jual (satu label per takaran; baris internalnya diikat takaranId)
  const takaranPertama = {}; let tolakPecah = '';
  // putaran 28b (owner 28 Sep): ½ karung juga saat merinci karcis — pemecah 1 × 50 kg → 2 × 25 kg ditulis di kiriman yang sama, BERTANGGAL & BERJAM KARCIS
  // (barangnya dipecah saat dijual), persis nota Jual (setengah-logika.js skPecah); modal baris = modal 25 kg hasil pecahan
  const wKarcis = Object.assign({}, w, { tanggal: p.tanggal, jam: p.jam || w.jam });
  pecahItemsWadah(s.keranjang.map((b) => Object.assign({}, b.trx)), s).forEach((t) => {
    const d = kcBersih(t); if (!t._takaran || !takaranPertama[t._takaran]) label.push(t.label || namaSingkatTrx(t));
    if (t.setengahDari) { const pc = skPecah(t, wKarcis); if (pc.tolak) tolakPecah = tolakPecah || pc.tolak; else { d.hppTotalSaatJual = Math.round(pc.hppPerUnit); d.dariSetengah = pc.idProduksi; pc.dokumen.forEach((x) => dokumen.push(x)); } }
    d.id = w.idUnik(); d.tanggal = p.tanggal; d.jam = p.jam || ''; d.caraBayar = cara; d.namaPelanggan = nama; d.hargaAsliSatuan = t.hargaAsli; if (t.nego) d.negoSelisih = t.hargaSatuan - t.hargaAsli;
    d.grupNota = idGrup; d.koreksiDari = p.id; d.dirinciPada = kini;
    if (t._takaran) d.takaranId = takaranPertama[t._takaran] || (takaranPertama[t._takaran] = String(d.id));   // putaran 27: pengikat baris internal satu takaran
    if (karcis) { d.asalDarurat = true; d.rinciDari = p.id; d.alasanKoreksi = 'Rincian dari kasir darurat ' + kcEkor(p.id) + (teksNominal ? ' (' + teksNominal + ')' : ''); } else d.alasanKoreksi = 'Dirapikan dari kasir ' + kcEkor(p.id);
    if (p.operator) d.operator = p.operator;
    dokumen.push({ koleksi: 'penjualan', data: d }); ids.push(d.id); kcPasangan(d, w, dokumen);
  });
  if (tolakPecah) return { tolak: tolakPecah };
  if (karcis && H.sisa > 0) { const sisaDoc = { id: w.idUnik(), tanggal: p.tanggal, jam: p.jam || '', caraBayar: cara, namaPelanggan: nama, jenis: 'kasir_darurat_nominal', hargaTotal: H.sisa, grupNota: idGrup, asalDarurat: true, rinciDari: p.id, koreksiDari: p.id, alasanKoreksi: 'Sisa belum diurai dari kasir darurat ' + kcEkor(p.id) + (teksNominal ? ' (' + teksNominal + ')' : ''), dirinciPada: kini }; if (p.operator) sisaDoc.operator = p.operator; dokumen.push({ koleksi: 'penjualan', data: sisaDoc }); ids.push(sisaDoc.id); }
  const asli = Object.assign({}, p, { dikoreksiOleh: ids[0], alasanKoreksi: (karcis ? 'Dirinci jadi ' : 'Dirapikan jadi ') + s.keranjang.length + ' barang: ' + label.join(' + ') + (karcis && H.sisa > 0 ? ' + sisa ' + RP(H.sisa) + ' belum diurai' : '') + (teksNominal ? '; ' + teksNominal : '') });
  if (N.diubah) { asli.nominalDibetulkan = N.nominal; asli.alasanNominal = N.alasan.slice(0, 120); }   // dicabut lagi bila rinciannya ditarik balik (susunUrungRinci)
  dokumen.push({ koleksi: 'penjualan', data: asli });
  // putaran 25: karcis bulan lalu (di luar masa tenggang) — tiap catatan diperiksa kunci di server; satu rincian tidak boleh butuh lebih dari 18 pemeriksaan
  const g = butuhGet(dokumen); if (g > KP_BATAS_GET) return { tolak: 'Karcis bulan lalu: rincian ini menyentuh ' + g + ' catatan (batas ' + KP_BATAS_GET + ' sekali kirim) — rinci sebagian barangnya dulu (sisanya tetap jadi karcis), lalu rinci lagi' };
  const ringkas = (karcis ? 'Karcis ' : 'Nota ') + kcEkor(p.id) + ' ' + (N.diubah ? RP(N.asli) + ' dibetulkan jadi ' + RP(N.nominal) : RP(k.nominal)) + ' → ' + s.keranjang.length + ' barang ' + RP(H.total) + (H.sisa > 0 ? ' + sisa ' + RP(H.sisa) + ' tetap jadi karcis' : '') + ' · ' + cara + (nama ? ' · ' + nama : '') + ' · tanggal & jam mengikuti karcisnya' + (N.diubah ? ' · ' + teksDampakNominal(k, cara, nama) : '');
  return { dokumen, ringkas, rinci: { grupNota: idGrup, asliId: p.id, ids }, patch: { keranjang: [], karcis: null, pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, ketik: '', penggantiTanya: null, kreditDibuka: false,
    notaTerakhir: { trxId: idGrup, idPenjualan: ids, piutangId: null, pesanan: null, retur: null, rinci: { grupNota: idGrup, asliId: p.id }, pada: Date.now(), ringkas, nama }, kabar: 'Tersimpan — ' + ringkas, kabarAwas: false } };
}

/** Hanya perbaiki cara bayar / nama pembeli karcis (barangnya belum diingat) — simpanPerbaikanDarurat() 32371: pengganti + asli ditandai. */
export function susunPerbaikanKarcis(s, w) {
  const k = s.karcis; if (!k) return { tolak: 'Tidak ada karcis yang sedang dibuka' };
  const p = ambilPenjualanSemua().find((x) => String(x.id) === k.id); if (!p || !penjualanMasihBerlaku(p) || p.jenis !== 'kasir_darurat_nominal') return { tolak: 'Karcis ' + kcEkor(k.id) + ' sudah tidak berlaku' };
  const kunci = tolakKunci('penjualan', p, 'cara bayar karcis ini tidak bisa diubah lagi; bon yang dibayar belakangan dicatat lewat Pelanggan › Terima bon hari ini'); if (kunci) return { tolak: kunci };   // putaran 25
  const cara = bakuCaraBayar(s.cara); const nama = String(s.pelanggan || '').trim(); const lama = bakuCaraBayar(p.caraBayar || 'Tunai');
  if (cara === 'Kredit' && !nama) return { tolak: 'Bon harus punya nama pembeli' };
  // owner 11 Okt: nominal ikut bisa dibetulkan tanpa merinci barangnya (alasan wajib); karcis pengganti membawa nominal baru, yang lama ditandai
  const tn = tolakNominal(k); if (tn) return { tolak: tn }; const N = nominalKarcis(k);
  if (cara === lama && nama === String(p.namaPelanggan || '').trim() && !N.diubah) return { tolak: 'Tidak ada yang berubah — cara bayar, nama pembeli, dan nominalnya masih sama' };
  const idBaru = w.idUnik(); const kini = w.kini || new Date().toISOString();
  const teksNominal = N.diubah ? 'nominal dibetulkan ' + RP(N.asli) + ' → ' + RP(N.nominal) + ': ' + N.alasan : '';
  const berubah = (cara !== lama ? lama + ' → ' + cara : '') + (nama !== String(p.namaPelanggan || '').trim() ? (cara !== lama ? ', ' : '') + 'pembeli ' + (nama || '(tanpa nama)') : '');
  const pengganti = Object.assign({}, p, { id: idBaru, caraBayar: cara, namaPelanggan: nama, koreksiDari: p.id, alasanKoreksi: 'Perbaikan ' + [berubah ? 'cara bayar / nama pembeli' : '', teksNominal].filter(Boolean).join('; '), dikoreksiPada: kini }); delete pengganti.dikoreksiOleh; delete pengganti.dibatalkan;
  if (N.diubah) { pengganti.hargaTotal = N.nominal; pengganti.nominalSebelum = N.asli; pengganti.alasanNominal = N.alasan.slice(0, 120); }
  const asli = Object.assign({}, p, { dikoreksiOleh: idBaru, alasanKoreksi: 'Diperbaiki: ' + [berubah, teksNominal].filter(Boolean).join('; ') });
  return { dokumen: [{ koleksi: 'penjualan', data: pengganti }, { koleksi: 'penjualan', data: asli }], patch: { karcis: null, keranjang: s.keranjang, pelanggan: '', cara: 'Tunai', lembar: null, kreditDibuka: false, kabar: 'Karcis ' + kcEkor(p.id) + ' diperbaiki: ' + [berubah, N.diubah ? teksDampakNominal(k, cara, nama) : ''].filter(Boolean).join(' · ') + ' — barangnya masih menunggu dirinci (karcis pengganti ' + kcEkor(idBaru) + ')', kabarAwas: false } };
}

/** Tarik balik satu rincian (urungkanRinciTrx 32665): grup harus UTUH; semua baris dibatalkan, kantong id+1 dihapus, karcis asli dipulihkan ke antrean. */
export function susunUrungRinci(rinci, w) {
  if (!rinci || !rinci.grupNota) return { tolak: 'Tidak ada rincian yang bisa ditarik balik' };
  const grup = ambilPenjualanSemua().filter((x) => String(x.grupNota) === String(rinci.grupNota) && (x.asalDarurat || String(x.koreksiDari) === String(rinci.asliId)));
  if (!grup.length) return { tolak: 'Rincian itu tidak ditemukan lagi' };
  const terkunci = grup.map((x) => tolakKunci('penjualan', x, 'rincian ini tidak bisa ditarik balik; barang yang dikembalikan dicatat sebagai RETUR hari ini (menunjuk nota ini)')).find(Boolean);
  if (terkunci) return { tolak: terkunci, pembalik: 'retur' };   // putaran 25
  const tersentuh = grup.find((x) => !penjualanMasihBerlaku(x));
  if (tersentuh) return { tolak: 'Tidak bisa ditarik balik: catatan ' + kcEkor(tersentuh.id) + ' dari rincian ini sudah ' + (tersentuh.dikoreksiOleh ? 'dikoreksi/dirinci lagi (lihat ' + kcEkor(tersentuh.dikoreksiOleh) + ')' : 'dibatalkan') + ' — bereskan yang itu dulu supaya totalnya tidak dobel' };
  const kini = (w && w.kini) || new Date().toISOString(); const dokumen = []; const hapus = [];
  // putaran 28b: ½ karung di rincian — pemecahnya ikut dicabut kalau sisa 25 kg-nya belum terpakai (sama dengan membatalkan nota Jual)
  const hapusPecah = skHapusPemecah(grup); hapusPecah.forEach((x) => hapus.push(x));
  grup.forEach((g) => { dokumen.push({ koleksi: 'penjualan', data: Object.assign({}, g, { dibatalkan: true, alasanKoreksi: 'Rincian diurungkan', dikoreksiPada: kini, dibatalkanPada: kini }) });
    if (g.jenis === 'literan' && g.kemasanLiteran) hapus.push({ koleksi: 'stokBahanLiteran', id: g.id + 1 }); if (g.jenis === 'wadah' && g.jenisWadah) hapus.push({ koleksi: koleksiWadah(g.jenisWadah), id: g.id + 1 }); if (g.kemasanRepack && g.jumlahKemasanRepackDipakai > 0) hapus.push({ koleksi: koleksiWadah(g.kemasanRepack), id: g.id + 1 }); });
  const asli = ambilPenjualanSemua().find((x) => String(x.id) === String(rinci.asliId));
  if (asli) { const pulih = Object.assign({}, asli); delete pulih.dikoreksiOleh; delete pulih.alasanKoreksi; delete pulih.nominalDibetulkan; delete pulih.alasanNominal; dokumen.push({ koleksi: 'penjualan', data: pulih }); }   // owner 11 Okt: karcis kembali ke nominal aslinya
  // putaran 25: rincian besar dari bulan lalu (> 18 pemeriksaan kunci) dikirim BERTAHAP — satu kelompok per baris (baris + kantongnya), karcis asli dipulihkan PALING AKHIR
  const kelompok = butuhGet(dokumen, hapus) > KP_BATAS_GET ? dokumen.filter((d) => String(d.data.id) !== String(rinci.asliId)).map((d) => ({ dokumen: [d], hapus: hapus.filter((h) => String(h.id) === String(Number(d.data.id) + 1)) }))
    .concat([{ dokumen: dokumen.filter((d) => String(d.data.id) === String(rinci.asliId)), hapus: hapusPecah }]) : null;
  return { dokumen, hapus, kelompok, jumlah: grup.length, patch: { notaTerakhir: null, kabar: 'Rincian ditarik balik — ' + grup.length + ' catatan dibatalkan, karcis ' + kcEkor(rinci.asliId) + ' kembali ke antrean' + (asli && asli.nominalDibetulkan ? ' dengan nominal aslinya ' + RP(asli.hargaTotal || 0) + ' (nominal yang dibetulkan ikut ditarik)' : ''), kabarAwas: false } };
}

// ---- PUTARAN 25b: BATALKAN karcis kasir darurat yang salah ketik (satu-satunya pekerjaan yang masih dilakukan owner di sistem lama, 25 Sep) ----
// Padanan mulaiBatalkanTrx() index.html 32117, BENTUK DOKUMEN SAMA: { ...p, dibatalkan: true, alasanKoreksi, dikoreksiPada, dibatalkanPada } — baris TIDAK dihapus;
// kantong literan pasangan (id+1) ikut dicabut seperti di sana. Atribusi (diubahOleh / diubahPerangkat / diubahPada, + uid akun) ditempel penulis pusat.
// Hanya catatan yang LAHIR dari kasir darurat: karcis nominal (termasuk sisa yang belum diurai), barang tuts bernama (viaDarurat), atau perangkat berawalan d-.
// Karcis yang sudah dirinci → tarik balik rinciannya dulu (karcis kembali ke antrean, lalu bisa dibatalkan).
const KC_BATAL_TERKUNCI = 'karcis ini tidak bisa dibatalkan lagi — salah ketiknya tetap tercatat di bulan itu';
export const kcDariDarurat = (p) => !!p && (p.jenis === 'kasir_darurat_nominal' || p.viaDarurat === true || /^d-/.test(String(p.perangkat || '')));
/** Catatan kasir darurat bertanggal `iso` (bawaan: hari ini) yang masih berlaku — daftar "Karcis kasir darurat hari ini" di lembar Karcis. Terbaru dulu. */
export function karcisDaruratHari(kini, iso) {
  const hari = iso || hariIniIso(kini);
  return ambilPenjualan().filter((p) => kcDariDarurat(p) && p.tanggal === hari)
    .map((p) => ({ id: String(p.id), tanggal: p.tanggal, jam: p.jam || '', nominal: Math.round(p.hargaTotal || 0), cara: bakuCaraBayar(p.caraBayar), nama: String(p.namaPelanggan || '').trim(),
      oleh: String(p.operator || p.oleh || '').trim(), teks: p.jenis === 'kasir_darurat_nominal' ? (p.asalDarurat ? 'Sisa karcis ' + kcEkor(p.rinciDari || p.id) : 'Karcis ' + kcEkor(p.id)) : namaSingkatTrx(p) + ' · tuts kasir darurat',
      ket: String(p.keteranganDarurat || '').trim() }))
    .sort((a, b) => (b.jam + b.id).localeCompare(a.jam + a.id));
}
/** {tolak} atau {dokumen, hapus, patch}. alasan wajib (≥ 3 huruf) — jejaknya dibaca lagi nanti, seperti prompt di sistem lama. */
export function susunBatalKarcis(id, alasan, w) {
  const p = ambilPenjualanSemua().find((x) => String(x.id) === String(id));
  if (!p) return { tolak: 'Karcis itu tidak ditemukan lagi' };
  if (!kcDariDarurat(p)) return { tolak: 'Ini bukan catatan kasir darurat — batalkan lewat jalurnya sendiri' };
  if (!penjualanMasihBerlaku(p)) return { tolak: 'Karcis ' + kcEkor(p.id) + ' sudah ' + (p.dibatalkan ? 'dibatalkan' : 'dirinci/dikoreksi (tarik balik rinciannya dulu)') + ' — tidak dibatalkan dua kali' };
  const kunci = tolakKunci('penjualan', p, KC_BATAL_TERKUNCI); if (kunci) return { tolak: kunci };
  // audit 39b no. 37 tinjauan U37-U1: karcis yang barangnya sudah kembali lewat retur nota bon tidak dibatalkan (retur & mutasi retur tetap tinggal, bon jadi minus)
  const tolakRb = tolakBatalReturBon([p.id]); if (tolakRb) return { tolak: tolakRb };
  const a = String(alasan || '').trim(); if (a.length < 3) return { tolak: 'Tulis alasannya dulu (mis. "salah ketik, harusnya 39.000") — barisnya tetap tersimpan dan ditandai dibatalkan' };
  const kini = (w && w.kini) || new Date().toISOString();
  const data = Object.assign({}, p, { dibatalkan: true, alasanKoreksi: a.slice(0, 120), dikoreksiPada: kini, dibatalkanPada: kini });
  const hapus = p.jenis === 'literan' && p.kemasanLiteran ? [{ koleksi: 'stokBahanLiteran', id: p.id + 1 }] : [];
  return { dokumen: [{ koleksi: 'penjualan', data }], hapus, patch: { kcBatal: null, kabar: 'Karcis ' + kcEkor(p.id) + ' ' + RP(p.hargaTotal || 0) + ' (' + tanggalPendek(p.tanggal) + ' ' + (p.jam || '') + ') DIBATALKAN — ' + a + '. Barisnya tetap ada, ditandai dibatalkan; omzet & uang laci hari itu turun ' + RP(p.hargaTotal || 0) + '.', kabarAwas: false } };
}

/** Rincian yang dibuat hari `iso` (menurut jam dinding setempat) dan masih utuh (bisa ditarik balik dari daftar karcis). Terbaru dirinci dulu.
 *  jam & tanggal = JAM KARCIS ASLI (saat penjualan terjadi di kasir) — sama dengan jam yang ditulis di baris rinciannya. jamRinci = kapan owner
 *  merinci (dirinciPada, disimpan UTC) digambar setempat. Dulu `jam` berisi jam merinci, padahal di layar tertulis di sebelah nomor karcis. */
export function riwayatRinci(iso) {
  const grup = {}; ambilPenjualanSemua().forEach((x) => { if (!x.grupNota || !x.dirinciPada || !(x.asalDarurat || x.koreksiDari)) return; const kapan = new Date(x.dirinciPada); if (isNaN(kapan.getTime()) || hariIniIso(kapan) !== iso) return; const g = grup[x.grupNota] = grup[x.grupNota] || { grupNota: x.grupNota, asliId: x.rinciDari || x.koreksiDari, idPertama: x.id, n: 0, total: 0, jam: x.jam || '', tanggal: x.tanggal, jamRinci: jamSetempat(x.dirinciPada), dirinciPada: String(x.dirinciPada), utuh: true }; g.n += 1; g.total += x.hargaTotal || 0; if (!penjualanMasihBerlaku(x)) g.utuh = false; });
  return Object.keys(grup).map((k) => grup[k]).sort((a, b) => b.dirinciPada.localeCompare(a.dirinciPada));   // ISO UTC: urut lintas tengah malam
}
export { kcEkor };
