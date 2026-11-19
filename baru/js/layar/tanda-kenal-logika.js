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
/** Kode di label CONTOH layar Perangkat (uji-cetak.js): tidak pernah jadi barcode barang — label uji yang ter-scan tidak ikut terpasang. */
export const TK_KODE_CONTOH = 'UJI-LABEL';
/** Jalur rak yang boleh dipasangi barcode: barang berbungkus (karung pabrik, kemasan toko). Literan / repack / wadah ditakar, tidak ber-barcode. */
export const TK_JALUR_BARCODE = ['karung', 'kemasan'];
/** Mode daftar (kode menunggu dipasangkan) gugur sendiri sesudah sekian ms — supaya ketukan rak berikutnya yang jauh sesudahnya tidak ikut terpasang. */
export const TK_DAFTAR_GUGUR_MS = 60000;

/** Kode yang DISIMPAN. barcode: teks cetak 4–64 huruf (dirapikan tepinya), bukan QR struk toko; nfc: nomor seri heksa 4–10 byte, huruf besar.
 *  '' = tidak bisa dipakai. */
export function tkKode(jenis, mentah) {
  const t = String(mentah === undefined || mentah === null ? '' : mentah).trim();
  if (jenis === 'nfc') { const u = t.toUpperCase(); return /^(?:[0-9A-F]{2}){4,10}$/.test(u) ? u : ''; }
  if (jenis === 'barcode') return /^[\x20-\x7e]{4,64}$/.test(t) && t.indexOf(TK_AWALAN_NOTA) !== 0 && t.indexOf(TK_KODE_CONTOH) !== 0 ? t : '';
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

// ---------- paket S4 (19 Nov 2026): daftar pasangan yang berlaku, LEPAS, dan label buatan toko ----------
/** Awalan kode label yang DIBUAT toko untuk kemasan tanpa barcode pabrik. Saat di-scan ia barcode biasa (tkKode menerimanya, tkUraiPindai = 'lain'). */
export const TK_AWALAN_LABEL = 'MIQ:B:';
/** Huruf kode label: tanpa 0 O 1 I supaya tidak tertukar saat dibaca orang. */
export const TK_HURUF_LABEL = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
export const TK_PANJANG_LABEL = 8;
export const TK_LABEL_MAKS = 50;   // lembar label sekali cetak

/** Pasangan yang BERLAKU sekarang: satu baris per (jenis, kode) = catatan terbarunya; yang terakhirnya dilepas tidak ikut. Terbaru di atas. */
export function tkDaftarKini(daftar) {
  const akhir = {};
  (daftar || []).forEach((x) => {
    if (!x || (x.jenis !== 'barcode' && x.jenis !== 'nfc')) return;
    const k = x.jenis + '|' + String(x.kode); if (!akhir[k] || Number(x.id) > Number(akhir[k].id)) akhir[k] = x;
  });
  return Object.keys(akhir).map((k) => akhir[k]).filter((x) => x.sasaran && typeof x.sasaran === 'object').sort((a, b) => Number(b.id) - Number(a.id));
}

/** Catatan LEPAS: kode ini tidak lagi menunjuk apa pun (sasaran null). Catatan lamanya TIDAK dihapus — yang terbaru menang, jadi scan / tempel
 *  berikutnya kembali "belum dikenal" dan bisa dipasangkan lagi. Kode yang tidak sedang terpasang ditolak (tidak ada yang dilepas). */
export function tkSusunLepas(daftar, jenis, kodeMentah, w) {
  const kode = tkKode(jenis, kodeMentah); const d = kode ? tkCari(daftar, jenis, kode) : null;
  if (!d) return { tolak: (jenis === 'nfc' ? 'Kartu' : 'Barcode') + ' ini tidak sedang terpasang' };
  return { dokumen: [{ koleksi: 'tandaKenal', data: { id: w.idUnik(), jenis, kode, sasaran: null, tanggal: w.tanggal, jam: w.jam } }],
    patch: { kabar: (jenis === 'nfc' ? 'Kartu ' : 'Barcode ') + tkRingkasKode(kode) + ' dilepas dari ' + String(d.sasaran.nama || 'pasangannya'), kabarAwas: false } };
}

/** Kode label baru. acak() → bilangan 0 ≤ x < 1; sudahAda(kode) → true bila kode itu pernah dipakai. '' = tidak berhasil (dicoba 20 kali). */
export function tkKodeLabel(acak, sudahAda) {
  for (let coba = 0; coba < 20; coba++) {
    let s = '';
    for (let i = 0; i < TK_PANJANG_LABEL; i++) s += TK_HURUF_LABEL.charAt(Math.max(0, Math.min(TK_HURUF_LABEL.length - 1, Math.floor(Number(acak()) * TK_HURUF_LABEL.length))));
    const kode = TK_AWALAN_LABEL + s; if (!sudahAda || !sudahAda(kode)) return kode;
  }
  return '';
}

/** Label buatan toko yang SEDANG terpasang ke barang ini (jalur, kunci, dan berat sama). null = barang ini belum punya label toko. */
export function tkLabelBarang(daftar, sasaran) {
  if (!sasaran) return null;
  return tkDaftarKini(daftar).find((x) => x.jenis === 'barcode' && String(x.kode).indexOf(TK_AWALAN_LABEL) === 0 && x.sasaran.jalur === sasaran.jalur
    && String(x.sasaran.kunci) === String(sasaran.kunci) && String(x.sasaran.berat || '') === String(sasaran.berat || '')) || null;
}

/** Siapkan label untuk satu chip rak: label toko yang sudah ada DIPAKAI LAGI (kemasan yang sama = kode yang sama); belum ada → kode baru + catatan
 *  pasangannya. Hasil { kode, sasaran, dokumen ([] bila kodenya sudah ada) } atau { tolak }. */
export function tkSiapkanLabel(daftar, chip, w, acak) {
  const sasaran = tkSasaranChip(chip);
  if (!sasaran) return { tolak: 'Label hanya untuk karung atau kemasan di rak — literan dan repack ditakar, tidak berlabel' };
  const ada = tkLabelBarang(daftar, sasaran);
  if (ada) return { kode: String(ada.kode), sasaran: ada.sasaran, dokumen: [] };
  const terpakai = {}; (daftar || []).forEach((x) => { if (x && x.jenis === 'barcode') terpakai[String(x.kode)] = 1; });
  const kode = tkKodeLabel(acak, (k) => !!terpakai[k]);
  if (!kode) return { tolak: 'Kode label baru tidak berhasil dibuat — coba sekali lagi' };
  const r = tkSusunDaftar('barcode', kode, sasaran, w);
  return r.tolak ? { tolak: r.tolak } : { kode, sasaran: r.dokumen[0].data.sasaran, dokumen: r.dokumen };
}

/** Isi satu label: yang dibaca orang (nama barang, kode pendek) + yang dibaca scanner (kode utuh sebagai QR). */
export function tkIsiLabel(sasaran, kode) {
  const k = String(kode || '');
  return { judul: String((sasaran && sasaran.nama) || '').slice(0, 80), ket: 'TOKO BERAS M.IQBAL', kode: k,
    teksKode: k.indexOf(TK_AWALAN_LABEL) === 0 ? k.slice(TK_AWALAN_LABEL.length) : tkRingkasKode(k) };
}

/** Jumlah lembar label yang sah: bilangan bulat 1–TK_LABEL_MAKS; selain itu 0 (ditolak, bukan dibulatkan diam-diam). */
export function tkJumlahLabel(v) { const n = Number(String(v === undefined || v === null ? '' : v).trim()); return Number.isInteger(n) && n >= 1 && n <= TK_LABEL_MAKS ? n : 0; }

