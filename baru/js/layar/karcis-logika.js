// RINCI KARCIS (putaran 20) — logika tanpa DOM. Karcis = nota kasir darurat yang cuma menyebut NOMINAL (jenis 'kasir_darurat_nominal', ditulis tablet /
// kasir-darurat-nominal.html) + nota kasir yang jumlahnya belum pasti (perluKoreksi). Owner merincinya jadi barang bertitel supaya stok terpotong & laba punya modal.
// Cara kerja di sistem baru: karcis DIIKAT ke keranjang Jual (seperti tukar), barangnya dipilih dari rak seperti menjual biasa (tebakan dari katalog sekali ketuk),
// lalu SIMPAN RINCIAN menulis bentuk dokumen yang SAMA dengan simpanRinciTrx() index.html: baris barang {grupNota, asalDarurat, rinciDari, koreksiDari, alasanKoreksi,
// dirinciPada}, sisa yang belum terurai = karcis baru bertanda sama (uang masuk tidak pernah hilang), karcis asli DITANDAI dikoreksiOleh (tidak dihapus). Yang ditolak
// hanya KELEBIHAN (barang > uang yang masuk) — aturan owner 9 Agu 2026 ([[rinci-darurat-fleksibel-scope]]). Tanggal & jam baris = tanggal & jam karcisnya (uangnya masuk hari itu).
// Rapikan (perluKoreksi): bentuk koreksi (koreksiDari + alasanKoreksi, tanpa asalDarurat) dan jumlahnya harus menutup nominal PERSIS (uang tetap).
// Tarik balik (urungkanRinciTrx): seluruh grup dibatalkan, catatan kantong id+1 dihapus, karcis asli dipulihkan — hanya bila grupnya masih utuh.
import { hitungStokKarungPerMerk } from '../mesin/beku.js';
import { penjualanMasihBerlaku, bakuCaraBayar, hargaKarungUtuh, namaSingkatTrx, kunciKemasan } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilHargaLiteran, ambilHargaKemasan } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';
import { susunRak, masukkan, terapkanNego, periksaStokKeranjang } from './jual-logika.js';
import { koleksiWadah } from './wadah-jual-logika.js';

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
  const hasil = []; const stokK = hitungStokKarungPerMerk(); const literan = ambilHargaLiteran().filter((h) => h.hargaPerLiter > 0); const kemasan = ambilHargaKemasan().filter((h) => h.hargaPerUnit > 0);
  literan.forEach((h) => { const L = Math.round(n / h.hargaPerLiter * 2) / 2; if (!(L >= 0.5 && L <= 40)) return; const katalog = Math.round(L * h.hargaPerLiter); const selisih = n - katalog;
    if (selisih === 0) hasil.push({ tepat: true, label: h.merk + ' ' + String(L).replace('.', ',') + ' L', isi: [{ jalur: 'literan', kunci: h.merk, jumlah: L }] });
    else if (Math.abs(selisih) < KC_TOLERANSI_BULAT) hasil.push({ tepat: false, label: h.merk + ' ' + String(L).replace('.', ',') + ' L · bulat ' + (selisih > 0 ? '+' : '−') + RP(Math.abs(selisih)), isi: [{ jalur: 'literan', kunci: h.merk, jumlah: L, hargaPas: n }] }); });
  kemasan.forEach((h) => { const u = Math.round(n / h.hargaPerUnit); if (u >= 1 && u <= 6 && u * h.hargaPerUnit === n) hasil.push({ tepat: true, label: h.merk + ' ' + h.ukuran + ' kg × ' + u, isi: [{ jalur: 'kemasan', kunci: kunciKemasan(h.merk, h.ukuran), jumlah: u }] }); });
  Object.keys(stokK).forEach((merk) => { [50, 25].forEach((b) => { const hu = (hargaKarungUtuh(merk, b) || {}).perUnit || 0; if (!(hu > 0)) return; const k = Math.round(n / hu); if (k >= 1 && k <= 4 && k * hu === n) hasil.push({ tepat: true, label: 'Karung ' + b + ' kg ' + merk + ' × ' + k, isi: [{ jalur: 'karung', kunci: merk, berat: b, jumlah: k }] }); }); });
  hasil.sort((a, b) => (b.tepat ? 1 : 0) - (a.tepat ? 1 : 0));
  // kolam untuk kombinasi (Gono mencatat total per pembeli, bukan per barang — aturan lapangan 8 Agu 2026)
  const kolam = [];
  literan.forEach((h) => { for (let L = 1; L <= 25; L++) kolam.push({ jalur: 'literan', kunci: h.merk, jumlah: L, harga: h.hargaPerLiter * L, label: h.merk + ' ' + L + ' L', jangkar: false }); });
  kemasan.forEach((h) => { for (let u = 1; u <= 3; u++) kolam.push({ jalur: 'kemasan', kunci: kunciKemasan(h.merk, h.ukuran), jumlah: u, harga: h.hargaPerUnit * u, label: h.merk + ' ' + h.ukuran + ' kg × ' + u, jangkar: true }); });
  Object.keys(stokK).forEach((merk) => { [50, 25].forEach((b) => { const hu = (hargaKarungUtuh(merk, b) || {}).perUnit || 0; if (!(hu > 0)) return; for (let k = 1; k <= 2; k++) kolam.push({ jalur: 'karung', kunci: merk, berat: b, jumlah: k, harga: hu * k, label: 'Karung ' + b + ' ' + merk + ' × ' + k, jangkar: true }); }); });
  const isiDari = (x) => ({ jalur: x.jalur, kunci: x.kunci, berat: x.berat, jumlah: x.jumlah });
  const kecil = kolam.filter((x) => x.harga < n); const kombo = [];
  for (let i = 0; i < kecil.length && kombo.length < 6; i++) for (let j = i + 1; j < kecil.length && kombo.length < 6; j++) { if (kecil[i].harga + kecil[j].harga === n && (kecil[i].jalur + kecil[i].kunci + (kecil[i].berat || '')) !== (kecil[j].jalur + kecil[j].kunci + (kecil[j].berat || ''))) kombo.push({ tepat: true, label: kecil[i].label + ' + ' + kecil[j].label, isi: [isiDari(kecil[i]), isiDari(kecil[j])] }); }
  const jangkar = kecil.filter((x) => x.jangkar); const lit = kecil.filter((x) => x.jalur === 'literan' && x.jumlah <= 10);
  for (let a = 0; a < jangkar.length && kombo.length < 6; a++) for (let i = 0; i < lit.length && kombo.length < 6; i++) for (let j = i + 1; j < lit.length && kombo.length < 6; j++) { if (jangkar[a].harga + lit[i].harga + lit[j].harga === n && lit[i].kunci !== lit[j].kunci) kombo.push({ tepat: true, label: jangkar[a].label + ' + ' + lit[i].label + ' + ' + lit[j].label, isi: [isiDari(jangkar[a]), isiDari(lit[i]), isiDari(lit[j])] }); }
  return hasil.slice(0, 6).concat(kombo);
}

/** Ikat satu karcis ke keranjang (seperti tukar): satu karcis per keranjang, tidak bersama tukar/pesanan; cara bayar & nama pembeli diprakarsai dari karcisnya. */
export function ikatKarcis(s, id, kini) {
  const k = daftarKarcis(kini).daftar.find((x) => x.id === String(id)); if (!k) return { kabar: 'Karcis itu tidak ada lagi di antrean — sudah dirinci atau dibatalkan di perangkat lain', kabarAwas: true };
  if (s.karcis) return { kabar: 'Keranjang ini sedang merinci karcis ' + kcEkor(s.karcis.id) + ' — simpan atau lepas dulu', kabarAwas: true };
  if (s.tukar) return { kabar: 'Keranjang ini terikat tukar — catat notanya atau batal tukar dulu', kabarAwas: true };
  return { karcis: k, cara: k.cara === 'QRIS' || k.cara === 'Kredit' ? k.cara : 'Tunai', pelanggan: k.nama, uang: 0, potongan: 0, pesananId: null, lembar: null, jalur: s.jalur === 'retur' ? 'sering' : s.jalur, negoId: null,
    kabar: (k.jenisAsal === 'karcis' ? 'Merinci karcis ' : 'Merapikan nota ') + kcEkor(k.id) + ' ' + RP(k.nominal) + ' (' + k.tanggal.slice(8) + '/' + k.tanggal.slice(5, 7) + ' ' + k.jam + ') — pilih barangnya dari rak seperti menjual biasa' + (s.keranjang.length ? '; ' + s.keranjang.length + ' barang yang sudah di keranjang ikut dihitung' : ''), kabarAwas: false };
}
export function lepasKarcis(s) { return s.karcis ? { karcis: null, kabar: 'Karcis dilepas — tidak ada yang ditulis; barang di keranjang tetap', kabarAwas: false } : {}; }

/** Isi keranjang dari satu tebakan: tiap barang lewat masukkan() (langit-langit stok tetap dijaga); harga PAS literan dipasang sebagai nego. */
export function pakaiTebakan(s, t) {
  let st = Object.assign({}, s); const rak = susunRak(st);
  for (const x of t.isi) {
    const chip = (rak[x.jalur] || []).find((c) => c.kunci === x.kunci && (!x.berat || c.berat === x.berat)); if (!chip) return { kabar: x.kunci + ' tidak ada di rak (harga/stoknya tidak terbaca) — pilih barangnya sendiri', kabarAwas: true };
    const p = masukkan(Object.assign({}, st, { pilih: chip, ketik: '' }), x.jumlah); if (p.kabarAwas) return p;
    st = Object.assign(st, p);
    if (x.hargaPas) { const b = st.keranjang[st.keranjang.length - 1]; const q = terapkanNego(st, b.id, Math.round(x.hargaPas / x.jumlah)); if (q.keranjang) { st = Object.assign(st, q); const bb = st.keranjang[st.keranjang.length - 1]; if (bb.trx.hargaTotal !== x.hargaPas) bb.trx.hargaTotal = x.hargaPas; } }
  }
  return { keranjang: st.keranjang, urutBaris: st.urutBaris, pilih: null, lembar: null, ketik: '', kabar: 'Tebakan dipakai: ' + t.label + ' — periksa lalu SIMPAN RINCIAN', kabarAwas: false };
}

/** Uang vs barang di keranjang saat merinci. Potongan nota TIDAK dipakai (harga barangnya yang dinego). */
export function hitungKarcis(s) {
  const k = s.karcis; if (!k) return null; const total = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0); const sisa = k.nominal - total;
  return { k, total, sisa, lebih: sisa < 0, pas: sisa === 0 && total > 0, teks: !s.keranjang.length ? 'belum ada barang' : sisa === 0 ? 'PAS ' + RP(total) + ' — siap disimpan' : sisa > 0 ? 'Sisa ' + RP(sisa) + ' belum terurai — ' + (k.jenisAsal === 'karcis' ? 'boleh disimpan, sisanya tetap tercatat sebagai karcis' : 'rapikan harus menutup persis') : 'KELEBIHAN ' + RP(-sisa) + ' — hapus atau betulkan harga barang' };
}

const kcBersih = (t) => { const d = Object.assign({}, t); ['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego'].forEach((k) => { delete d[k]; }); return d; };
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
  if (!s.keranjang.length) return { tolak: 'Tambahkan barangnya dulu — atau ketuk salah satu tebakan' };
  if (s.tukar) return { tolak: 'Keranjang terikat tukar — batal tukar dulu' };
  if (Math.round(s.potongan || 0) > 0) return { tolak: 'Potongan nota tidak dipakai saat merinci — nego harga barangnya saja' };
  const cara = bakuCaraBayar(s.cara); const nama = String(s.pelanggan || '').trim();
  if (cara === 'Kredit' && !nama) return { tolak: 'Bon harus punya nama pembeli — tanpa nama, utangnya tidak bisa ditagih' };
  const H = hitungKarcis(s); if (H.lebih) return { tolak: 'Jumlah barang ' + RP(H.total) + ' KELEBIHAN ' + RP(-H.sisa) + ' dari nominal ' + RP(k.nominal) + ' — tidak boleh melebihi uang yang masuk' };
  if (k.jenisAsal === 'rapikan' && H.sisa !== 0) return { tolak: 'Merapikan harus menutup ' + RP(k.nominal) + ' persis (uang nota tetap) — sekarang ' + RP(H.total) };
  const stok = periksaStokKeranjang(s); if (stok) return { tolak: stok };
  const karcis = k.jenisAsal === 'karcis'; const idGrup = w.idUnik(); const kini = w.kini || new Date().toISOString(); const dokumen = []; const ids = []; const label = [];
  s.keranjang.forEach((b) => {
    const t = b.trx; const d = kcBersih(t); label.push(t.label || namaSingkatTrx(t));
    d.id = w.idUnik(); d.tanggal = p.tanggal; d.jam = p.jam || ''; d.caraBayar = cara; d.namaPelanggan = nama; d.hargaAsliSatuan = t.hargaAsli; if (t.nego) d.negoSelisih = t.hargaSatuan - t.hargaAsli;
    d.grupNota = idGrup; d.koreksiDari = p.id; d.dirinciPada = kini;
    if (karcis) { d.asalDarurat = true; d.rinciDari = p.id; d.alasanKoreksi = 'Rincian dari kasir darurat ' + kcEkor(p.id); } else d.alasanKoreksi = 'Dirapikan dari kasir ' + kcEkor(p.id);
    if (p.operator) d.operator = p.operator;
    dokumen.push({ koleksi: 'penjualan', data: d }); ids.push(d.id); kcPasangan(d, w, dokumen);
  });
  if (karcis && H.sisa > 0) { const sisaDoc = { id: w.idUnik(), tanggal: p.tanggal, jam: p.jam || '', caraBayar: cara, namaPelanggan: nama, jenis: 'kasir_darurat_nominal', hargaTotal: H.sisa, grupNota: idGrup, asalDarurat: true, rinciDari: p.id, koreksiDari: p.id, alasanKoreksi: 'Sisa belum diurai dari kasir darurat ' + kcEkor(p.id), dirinciPada: kini }; if (p.operator) sisaDoc.operator = p.operator; dokumen.push({ koleksi: 'penjualan', data: sisaDoc }); ids.push(sisaDoc.id); }
  const asli = Object.assign({}, p, { dikoreksiOleh: ids[0], alasanKoreksi: (karcis ? 'Dirinci jadi ' : 'Dirapikan jadi ') + s.keranjang.length + ' barang: ' + label.join(' + ') + (karcis && H.sisa > 0 ? ' + sisa ' + RP(H.sisa) + ' belum diurai' : '') });
  dokumen.push({ koleksi: 'penjualan', data: asli });
  const ringkas = (karcis ? 'Karcis ' : 'Nota ') + kcEkor(p.id) + ' ' + RP(k.nominal) + ' → ' + s.keranjang.length + ' barang ' + RP(H.total) + (H.sisa > 0 ? ' + sisa ' + RP(H.sisa) + ' tetap jadi karcis' : '') + ' · ' + cara + (nama ? ' · ' + nama : '') + ' · tanggal & jam mengikuti karcisnya';
  return { dokumen, ringkas, rinci: { grupNota: idGrup, asliId: p.id, ids }, patch: { keranjang: [], karcis: null, pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, ketik: '', penggantiTanya: null,
    notaTerakhir: { trxId: idGrup, idPenjualan: ids, piutangId: null, pesanan: null, retur: null, rinci: { grupNota: idGrup, asliId: p.id }, pada: Date.now(), ringkas, nama }, kabar: 'Tersimpan — ' + ringkas, kabarAwas: false } };
}

/** Hanya perbaiki cara bayar / nama pembeli karcis (barangnya belum diingat) — simpanPerbaikanDarurat() 32371: pengganti + asli ditandai. */
export function susunPerbaikanKarcis(s, w) {
  const k = s.karcis; if (!k) return { tolak: 'Tidak ada karcis yang sedang dibuka' };
  const p = ambilPenjualanSemua().find((x) => String(x.id) === k.id); if (!p || !penjualanMasihBerlaku(p) || p.jenis !== 'kasir_darurat_nominal') return { tolak: 'Karcis ' + kcEkor(k.id) + ' sudah tidak berlaku' };
  const cara = bakuCaraBayar(s.cara); const nama = String(s.pelanggan || '').trim(); const lama = bakuCaraBayar(p.caraBayar || 'Tunai');
  if (cara === 'Kredit' && !nama) return { tolak: 'Bon harus punya nama pembeli' };
  if (cara === lama && nama === String(p.namaPelanggan || '').trim()) return { tolak: 'Tidak ada yang berubah — cara bayar dan nama pembelinya masih sama' };
  const idBaru = w.idUnik(); const kini = w.kini || new Date().toISOString();
  const pengganti = Object.assign({}, p, { id: idBaru, caraBayar: cara, namaPelanggan: nama, koreksiDari: p.id, alasanKoreksi: 'Perbaikan cara bayar / nama pembeli', dikoreksiPada: kini }); delete pengganti.dikoreksiOleh; delete pengganti.dibatalkan;
  const asli = Object.assign({}, p, { dikoreksiOleh: idBaru, alasanKoreksi: 'Diperbaiki: ' + lama + ' → ' + cara + (nama ? ', pembeli ' + nama : '') });
  return { dokumen: [{ koleksi: 'penjualan', data: pengganti }, { koleksi: 'penjualan', data: asli }], patch: { karcis: null, keranjang: s.keranjang, pelanggan: '', cara: 'Tunai', lembar: null, kabar: 'Karcis ' + kcEkor(p.id) + ' diperbaiki: ' + lama + ' → ' + cara + (nama ? ', pembeli ' + nama : '') + ' — barangnya masih menunggu dirinci (karcis pengganti ' + kcEkor(idBaru) + ')', kabarAwas: false } };
}

/** Tarik balik satu rincian (urungkanRinciTrx 32665): grup harus UTUH; semua baris dibatalkan, kantong id+1 dihapus, karcis asli dipulihkan ke antrean. */
export function susunUrungRinci(rinci, w) {
  if (!rinci || !rinci.grupNota) return { tolak: 'Tidak ada rincian yang bisa ditarik balik' };
  const grup = ambilPenjualanSemua().filter((x) => String(x.grupNota) === String(rinci.grupNota) && (x.asalDarurat || String(x.koreksiDari) === String(rinci.asliId)));
  if (!grup.length) return { tolak: 'Rincian itu tidak ditemukan lagi' };
  const tersentuh = grup.find((x) => !penjualanMasihBerlaku(x));
  if (tersentuh) return { tolak: 'Tidak bisa ditarik balik: catatan ' + kcEkor(tersentuh.id) + ' dari rincian ini sudah ' + (tersentuh.dikoreksiOleh ? 'dikoreksi/dirinci lagi (lihat ' + kcEkor(tersentuh.dikoreksiOleh) + ')' : 'dibatalkan') + ' — bereskan yang itu dulu supaya totalnya tidak dobel' };
  const kini = (w && w.kini) || new Date().toISOString(); const dokumen = []; const hapus = [];
  grup.forEach((g) => { dokumen.push({ koleksi: 'penjualan', data: Object.assign({}, g, { dibatalkan: true, alasanKoreksi: 'Rincian diurungkan', dikoreksiPada: kini, dibatalkanPada: kini }) });
    if (g.jenis === 'literan' && g.kemasanLiteran) hapus.push({ koleksi: 'stokBahanLiteran', id: g.id + 1 }); if (g.jenis === 'wadah' && g.jenisWadah) hapus.push({ koleksi: koleksiWadah(g.jenisWadah), id: g.id + 1 }); if (g.kemasanRepack && g.jumlahKemasanRepackDipakai > 0) hapus.push({ koleksi: koleksiWadah(g.kemasanRepack), id: g.id + 1 }); });
  const asli = ambilPenjualanSemua().find((x) => String(x.id) === String(rinci.asliId));
  if (asli) { const pulih = Object.assign({}, asli); delete pulih.dikoreksiOleh; delete pulih.alasanKoreksi; dokumen.push({ koleksi: 'penjualan', data: pulih }); }
  return { dokumen, hapus, jumlah: grup.length, patch: { notaTerakhir: null, kabar: 'Rincian ditarik balik — ' + grup.length + ' catatan dibatalkan, karcis ' + kcEkor(rinci.asliId) + ' kembali ke antrean', kabarAwas: false } };
}

/** Rincian yang dibuat hari `iso` dan masih utuh (bisa ditarik balik dari daftar karcis). */
export function riwayatRinci(iso) {
  const grup = {}; ambilPenjualanSemua().forEach((x) => { if (!x.grupNota || !x.dirinciPada || !(x.asalDarurat || x.koreksiDari)) return; const kapan = new Date(x.dirinciPada); if (isNaN(kapan.getTime()) || hariIniIso(kapan) !== iso) return; const g = grup[x.grupNota] = grup[x.grupNota] || { grupNota: x.grupNota, asliId: x.rinciDari || x.koreksiDari, n: 0, total: 0, jam: String(kapan.getHours()).padStart(2, '0') + ':' + String(kapan.getMinutes()).padStart(2, '0'), utuh: true, tanggal: x.tanggal }; g.n += 1; g.total += x.hargaTotal || 0; if (!penjualanMasihBerlaku(x)) g.utuh = false; });
  return Object.keys(grup).map((k) => grup[k]).sort((a, b) => b.jam.localeCompare(a.jam));
}
export { kcEkor };
