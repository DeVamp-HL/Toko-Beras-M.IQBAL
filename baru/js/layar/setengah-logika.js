// SETENGAH KARUNG dari kemasan 50 kg hasil produksi/campuran (putaran 27 Bagian 4, owner 27 Sep: "kemasan 50 kg hasil campuran boleh dijual 25 kg").
// Cara buku = JALUR PEMECAHAN YANG SUDAH ADA (docs/peta-stok-merek.md §4): satu kemasan <nama> 50 kg dibongkar jadi 2 × <nama> 25 kg lewat penyusun Adukan
// (susunSimpanAdukan: bahan = kemasan jadi, hasil = 2 unit 25 kg, tanpa upah & tanpa kantong → modal dibagi dua oleh mesin beku bagiBiayaAdukan, Σ persis),
// lalu SATU kemasan 25 kg terjual di nota yang sama. Sisa 25 kg tampil sebagai kemasan 25 kg biasa. Semuanya satu kiriman (writeBatch) dan ikut kunci bulan
// (produksi & nota bertanggal hari ini). Tidak ada jenis dokumen baru; penanda `dariSetengah` di baris nota (= id produksi pemecah) & di produksinya.
// Harga 25 kg = katalog <nama> 25 kg; belum ada → usul = ½ harga 50 kg dibulatkan KE ATAS ke Rp100 (owner boleh mengubah) dan harga itu ikut disimpan ke
// katalog di kiriman yang sama supaya sisa 25 kg-nya tampil di rak dengan harga yang sama.
// Tanpa DOM; nama berawalan sk (bundel uji satu lingkup). Dijaga alat-uji/uji_setengah_karung.py.
import { hitungStokKemasan } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { ambilHargaKemasan, ambilProduksi } from '../data/toko.js';
import { susunSimpanAdukan } from './stok-adukan-logika.js';

export const SK_BESAR = 50;
export const SK_KECIL = 25;
const skBulat100 = (n) => Math.ceil(n / 100 - 1e-9) * 100;
const skAngka = (v) => Math.round(Number(String(v === undefined || v === null ? '' : v).replace(/\./g, '').replace(',', '.')) || 0);
/** Harga ½ untuk chip kemasan 50 kg: katalog 25 kg bila ada, selain itu usul ½ harga 50 kg ke atas ke Rp100. null = bukan kemasan 50 kg. */
export function skInfo(chip) {
  if (!chip || chip.jalur !== 'kemasan' || Number(chip.ukuranKg) !== SK_BESAR || chip.setengahDari) return null;
  const k = ambilHargaKemasan().find((x) => x.merk === chip.nama && Number(x.ukuran) === SK_KECIL); const dariKatalog = !!(k && Number(k.hargaPerUnit) > 0);
  const usul = skBulat100((Number(chip.harga) || 0) / 2);
  return { dariKatalog, harga25: dariKatalog ? Number(k.hargaPerUnit) : usul, usul, sisa: chip.sisa, nama: chip.nama, kunci50: chip.kunci };
}
/** Chip ½ yang dimasukkan ke keranjang: kemasan <nama> 25 kg, 1 unit, stoknya dipegang dari kemasan 50 kg (kunci = kunci 50 kg, dibaca langit-langit stok). */
export function skChip(chip, hargaKetik) {
  const i = skInfo(chip); if (!i) return null;
  const ketik = skAngka(hargaKetik); const harga = i.dariKatalog ? i.harga25 : (ketik > 0 ? ketik : i.usul);
  return { jalur: 'kemasan', kunci: chip.kunci, nama: chip.nama, ukuran: SK_KECIL + ' kg', ukuranKg: SK_KECIL, harga, satuan: 'kemasan', sisa: chip.sisa, sisaTeks: chip.sisaTeks, hppPerUnit: (Number(chip.hppPerUnit) || 0) / 2,
    setengahDari: chip.kunci, setengahHargaBaru: i.dariKatalog ? 0 : harga };
}
/** Bentuk "dipegang" baris ½ untuk langit-langit stok (mesin beku wzDiKeranjang): 1 unit kemasan 50 kg, bukan 25 kg. */
export function skTrxPegang(t) { return t && t.setengahDari ? { jenis: 'kemasan', namaProduk: t.namaProduk, ukuranKemasan: SK_BESAR, jumlahUnit: 1, totalKg: SK_BESAR } : t; }
/**
 * Dokumen pemecah untuk SATU baris ½ di nota: produksiKemasan dari penyusun Adukan (bahan 1 × 50 kg, hasil 2 × 25 kg) + katalog 25 kg bila belum ada.
 * → { dokumen, idProduksi, hppPerUnit } | { tolak }.
 */
export function skPecah(t, w) {
  const draf = { tanggal: w.tanggal, bahan: [], bahanKemasan: [{ kunci: t.setengahDari, unit: 1 }], hasil: [{ nama: t.namaProduk, ukuran: String(SK_KECIL), unit: '2', kantongJenis: '', kantongJumlah: '' }], upah: '' };
  const r = susunSimpanAdukan(draf, w, {}); if (r.tolak) return { tolak: t.namaProduk + ' ½: ' + r.tolak };
  const dokumen = r.dokumen.map((d) => (d.koleksi === 'produksiKemasan' ? { koleksi: d.koleksi, data: Object.assign({}, d.data, { dariSetengah: true, keterangan: '½ karung: 1 × ' + t.namaProduk + ' 50 kg dipecah jadi 2 × 25 kg, satu terjual di nota yang sama' }) } : d));
  const idProduksi = r.batchId; const hppPerUnit = r.hitung.sahH[0].hppPerUnit;
  if (t.setengahHargaBaru > 0 && !ambilHargaKemasan().some((x) => x.merk === t.namaProduk && Number(x.ukuran) === SK_KECIL)) {
    dokumen.push({ koleksi: 'katalogHargaKemasan', data: { id: t.namaProduk.toLowerCase().replace(/\s+/g, '_') + '_' + SK_KECIL + 'kg', merk: t.namaProduk, ukuran: SK_KECIL, hargaPerUnit: t.setengahHargaBaru, diubahPada: w.kini, modalSaatSetel: 0 } });
  }
  return { dokumen, idProduksi, hppPerUnit };
}
/** Batalkan nota barusan: pemecah ikut dicabut kalau sisa 25 kg-nya belum terpakai (stok 25 kg tidak boleh jadi minus); kalau sudah, pecahannya tetap. */
export function skHapusPemecah(baris) {
  const hapus = []; const stok = hitungStokKemasan();
  baris.filter((p) => p.dariSetengah && p.jenis === 'kemasan').forEach((p) => {
    const pr = ambilProduksi().find((x) => String(x.id) === String(p.dariSetengah)); if (!pr) return;
    const s = stok[kunciKemasan(p.namaProduk, p.ukuranKemasan)]; if (s && (s.sisaUnit || 0) + 1 - 2 < 0) return;   // nota batal = +1, pemecah dicabut = −2
    hapus.push({ koleksi: 'produksiKemasan', id: pr.id });
  });
  return hapus;
}
