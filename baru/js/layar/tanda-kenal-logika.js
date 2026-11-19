// TANDA KENAL (paket S2a, 19 Nov 2026) — apa ARTI satu kode yang dibaca scanner tablet. TANPA impor (dijalankan apa adanya di jsc:
// alat-uji/uji_tanda_kenal.py); tidak membaca & tidak menulis data toko.
// Sekarang: QR nomor nota di struk — scan struk → notanya terbuka (retur, cetak ulang). Barcode kemasan & kartu pelanggan NFC menyusul di
// paket S2b (keduanya butuh tempat menyimpan pasangan kode → barang / pembeli).

/** Awalan QR struk toko. Kode berawalan lain BUKAN struk toko ini. */
export const TK_AWALAN_NOTA = 'MIQ:N:';
/** QR dicetak sebagai ASCII (escpos.js); lebih panjang dari ini QR di kertas 58 mm jadi terlalu rapat untuk dibaca. */
export const TK_PANJANG_MAKS = 96;
const KUNCI_DARI = { t: 'trxId', g: 'grupNota', i: 'id' };
const CETAK = /^[\x21-\x7e]+$/;   // huruf yang bisa dicetak tanpa spasi

/** Teks QR untuk satu nota (bentuk notaDari di struk-logika.js): 'MIQ:N:t:<trxId>' | 'MIQ:N:g:<grupNota>' | 'MIQ:N:i:<id>'.
 *  Urutan pilihnya sama dengan notaDari (trxId dulu). '' = tidak ada kunci yang bisa dicetak → struk dicetak TANPA QR, bukan dengan QR yang salah. */
export function tkQrNota(nota) {
  if (!nota) return '';
  const ada = (v) => v !== undefined && v !== null && String(v) !== '';
  const pilih = ada(nota.trxId) ? ['t', nota.trxId] : ada(nota.grupNota) ? ['g', nota.grupNota] : ada(nota.id) ? ['i', nota.id] : null;
  if (!pilih) return '';
  const teks = TK_AWALAN_NOTA + pilih[0] + ':' + String(pilih[1]);
  return CETAK.test(String(pilih[1])) && teks.length <= TK_PANJANG_MAKS ? teks : '';
}

/** Hasil scan → { jenis: 'nota', kunci: { trxId } | { grupNota } | { id } } · { jenis: 'rusak', kode } (berawalan struk toko tapi tidak utuh)
 *  · { jenis: 'lain', kode } (bukan struk toko: barcode kemasan dsb.) · null (kosong). Kunci selalu TEKS — notaDari membandingkan sebagai teks. */
export function tkUraiPindai(teks) {
  const t = String(teks === undefined || teks === null ? '' : teks).trim();
  if (!t) return null;
  if (t.indexOf(TK_AWALAN_NOTA) !== 0) return { jenis: 'lain', kode: t };
  const sisa = t.slice(TK_AWALAN_NOTA.length); const kolom = KUNCI_DARI[sisa.charAt(0)]; const nilai = sisa.slice(2);
  if (!kolom || sisa.charAt(1) !== ':' || !CETAK.test(nilai) || t.length > TK_PANJANG_MAKS) return { jenis: 'rusak', kode: t };
  const kunci = {}; kunci[kolom] = nilai;
  return { jenis: 'nota', kunci };
}

/** Lembar Jual yang boleh diganti lembar struk saat sebuah struk di-scan: layar dasar, keranjang, atau struk lain. Lembar berisi isian yang sedang
 *  dikerjakan (bayar, jumlah, retur, …) TIDAK ditimpa — kasir diberi tahu, bukan dipindahkan diam-diam. */
export const tkLembarBolehDiganti = (lembar) => !lembar || lembar === 'struk' || lembar === 'keranjang';
