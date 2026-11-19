// TANDA KENAL (paket S2a, 19 Nov 2026) — apa ARTI satu kode yang dibaca scanner tablet. TANPA impor (dijalankan apa adanya di jsc:
// alat-uji/uji_tanda_kenal.py); tidak membaca & tidak menulis data toko.
// S2a: QR nomor nota di struk — scan struk → notanya terbuka (retur, cetak ulang).
// S2b: pasangan kode → sasaran (koleksi tandaKenal, rules v12): barcode kemasan → barang di rak Jual; nomor seri kartu NFC → pembeli. Modul ini
// hanya MENYUSUN & MENCARI — daftar tandaKenal diberikan pemanggil, dokumen baru dikembalikan untuk ditulis pemanggil.

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

// ---------- paket S2b: pasangan kode → sasaran (catatan TAMBAH-SAJA; yang terbaru menang) ----------
/** Jalur rak yang boleh dipasangi barcode: barang berbungkus (karung pabrik, kemasan toko). Literan / repack / wadah ditakar, tidak ber-barcode. */
export const TK_JALUR_BARCODE = ['karung', 'kemasan'];
/** Mode daftar (kode menunggu dipasangkan) gugur sendiri sesudah sekian ms — supaya ketukan rak berikutnya yang jauh sesudahnya tidak ikut terpasang. */
export const TK_DAFTAR_GUGUR_MS = 60000;

/** Kode yang DISIMPAN. barcode: teks cetak 4–64 huruf (dirapikan tepinya), bukan QR struk toko; nfc: nomor seri heksa 4–10 byte, huruf besar.
 *  '' = tidak bisa dipakai. */
export function tkKode(jenis, mentah) {
  const t = String(mentah === undefined || mentah === null ? '' : mentah).trim();
  if (jenis === 'nfc') { const u = t.toUpperCase(); return /^(?:[0-9A-F]{2}){4,10}$/.test(u) ? u : ''; }
  if (jenis === 'barcode') return /^[\x20-\x7e]{4,64}$/.test(t) && t.indexOf(TK_AWALAN_NOTA) !== 0 ? t : '';
  return '';
}

/** Pasangan TERBARU satu kode (id terbesar menang). null = belum dikenal, atau pasangan terakhirnya dilepas (sasaran kosong). */
export function tkCari(daftar, jenis, kode) {
  let d = null;
  (daftar || []).forEach((x) => { if (x && x.jenis === jenis && String(x.kode) === String(kode) && (!d || Number(x.id) > Number(d.id))) d = x; });
  return d && d.sasaran && typeof d.sasaran === 'object' ? d : null;
}

/** Sasaran barcode dari chip rak Jual. null = chip ini tidak bisa dipasangi barcode (literan, repack, wadah). */
export function tkSasaranChip(chip) {
  if (!chip || TK_JALUR_BARCODE.indexOf(chip.jalur) < 0 || chip.kunci === undefined || chip.kunci === null || String(chip.kunci) === '') return null;
  return { jalur: chip.jalur, kunci: String(chip.kunci), berat: chip.berat === undefined || chip.berat === null ? '' : String(chip.berat),
    nama: (String(chip.nama || chip.kunci) + (chip.ukuran ? ' ' + chip.ukuran : '')).slice(0, 80) };
}

/** Chip rak yang ditunjuk sasaran barcode — cara cari yang sama dengan aksi chip di jual.js. null = barangnya sedang tidak di rak (habis / tanpa
 *  harga / diarsipkan): kasir diberi tahu, tidak dipilihkan barang lain. */
export function tkChipDari(rak, sasaran) {
  if (!rak || !sasaran || TK_JALUR_BARCODE.indexOf(sasaran.jalur) < 0) return null;
  return (rak[sasaran.jalur] || []).find((x) => String(x.kunci) === String(sasaran.kunci) && (!sasaran.berat || String(x.berat) === String(sasaran.berat))) || null;
}

/** Mode daftar masih berlaku? tk = { jenis, kode, mode: 'daftar', pada } · kini = Date.now(). */
export const tkMasihDaftar = (tk, jenis, kini) => !!(tk && tk.mode === 'daftar' && tk.jenis === jenis && Number(kini) - Number(tk.pada || 0) <= TK_DAFTAR_GUGUR_MS);

/** Dokumen pasangan baru. sasaran: barcode → hasil tkSasaranChip · nfc → { nama }. w = { tanggal, jam, idUnik }.
 *  Hasil { dokumen: [{ koleksi: 'tandaKenal', data }], patch } atau { tolak }. Penulis (toko.js) yang membubuhkan siapa & perangkat mana. */
export function tkSusunDaftar(jenis, kodeMentah, sasaran, w) {
  const kode = tkKode(jenis, kodeMentah);
  if (!kode) return { tolak: jenis === 'nfc' ? 'Nomor seri kartu tidak terbaca utuh — tempel ulang kartunya' : 'Kode ini tidak bisa dipakai sebagai barcode barang' };
  let s = null;
  if (jenis === 'barcode') {
    if (!sasaran || TK_JALUR_BARCODE.indexOf(sasaran.jalur) < 0 || !String(sasaran.kunci || '')) return { tolak: 'Barcode hanya bisa dipasangkan ke karung atau kemasan di rak — literan dan repack ditakar, tidak ber-barcode' };
    s = { jalur: sasaran.jalur, kunci: String(sasaran.kunci), berat: String(sasaran.berat || ''), nama: String(sasaran.nama || sasaran.kunci).slice(0, 80) };
  } else {
    const nama = String((sasaran && sasaran.nama) || '').trim();
    if (!nama) return { tolak: 'Pilih nama pembelinya dulu' };
    s = { nama: nama.slice(0, 60) };
  }
  return { dokumen: [{ koleksi: 'tandaKenal', data: { id: w.idUnik(), jenis, kode, sasaran: s, tanggal: w.tanggal, jam: w.jam } }],
    patch: { tk: null, kabar: (jenis === 'nfc' ? 'Kartu ' + tkRingkasKode(kode) + ' kini milik ' : 'Barcode ' + tkRingkasKode(kode) + ' kini = ') + s.nama, kabarAwas: false } };
}

/** Kode panjang dipendekkan untuk kalimat di layar. */
export function tkRingkasKode(kode) { const t = String(kode || ''); return t.length > 18 ? t.slice(0, 8) + '…' + t.slice(-6) : t; }

