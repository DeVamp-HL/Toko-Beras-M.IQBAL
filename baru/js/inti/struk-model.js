// MODEL STRUK GAYA SERTIFIKAT (owner 17 Nov 2026, butir 3) — murni: tanpa DOM, tanpa impor, tanpa data toko (dipakai printer tablet, pratinjau Jual, dan
// halaman uji cetak yang tidak boleh memuat Firestore). Masukan = garis susunStruk() (struk-logika.js) yang tiap barisnya bertanda `jenis`.
// Owner memilih gaya "Sertifikat" + logo F mahkota padi (huruf M). Isi & angka TIDAK berubah: model ini cuma mengelompokkan baris susunStruk()
// (bertanda `jenis`) supaya printer tablet / pratinjau bisa menggambarnya sebagai kop · Nota Nº · isian bertitik · tabel uraian · ringkasan · TOTAL bergaris
// ganda · pembayaran · tanda tangan yang melayani. Struk teks, WhatsApp & Pusat Dokumen tetap memakai baris yang sama apa adanya.
/** Model gambar Sertifikat dari garis susunStruk(). Baris tanpa `jenis` (garis pemisah) diabaikan. */
export function stModelSertifikat(garis) {
  const M = { kop: '', kopBesar: '', kopKecil: '', alamat: '', telp: '', no: '', faktur: '', tanggal: '', pembeli: '', alamatPembeli: '', jatuhTempo: '', pelayan: '', barang: [], ringkas: [], total: '', bayar: [], bon: [], catatan: [], kaki: '' };
  let kini = null;
  (garis || []).forEach((g) => {
    if (!g || g.garis) return; const kiri = String(g.kiri || ''); const kanan = String(g.kanan || '');
    if (g.jenis === 'kop') M.kop = kiri; else if (g.jenis === 'alamat') M.alamat = kiri; else if (g.jenis === 'telp') M.telp = String(g.nilai || kiri);
    else if (g.jenis === 'nota') M.no = String(g.nilai || ''); else if (g.jenis === 'tanggal') M.tanggal = String(g.nilai || kiri);
    // B2 (owner 17 Nov 2026): faktur — nomor faktur, alamat pembeli, jatuh tempo (baris tanpa angka kanan)
    else if (g.jenis === 'faktur') M.faktur = String(g.nilai || ''); else if (g.jenis === 'alamatPembeli') M.alamatPembeli = String(g.nilai || ''); else if (g.jenis === 'jatuhTempo') M.jatuhTempo = String(g.nilai || kiri);
    else if (g.jenis === 'pembeli') M.pembeli = String(g.nilai || ''); else if (g.jenis === 'pelayan') M.pelayan = String(g.nilai || '');
    else if (g.jenis === 'barang') { kini = { nama: kiri, n: kanan, rinci: [] }; M.barang.push(kini); }
    else if (g.jenis === 'rinci') { if (!kini) return; if (g.jumlah && !kini.n) { kini.n = kanan; kini.rinci.push({ teks: kiri.trim(), n: '' }); } else kini.rinci.push({ teks: kiri.trim(), n: kanan }); }
    else if (g.jenis === 'ringkas') M.ringkas.push({ label: kiri, n: kanan });
    else if (g.jenis === 'total') M.total = kanan;
    else if (g.jenis === 'bon') M.bon.push({ teks: kiri, tebal: !!g.tebal });
    else if (g.jenis === 'bayar') M.bayar.push({ label: kiri, n: kanan, tebal: !!g.tebal });
    else if (g.jenis === 'catatan') M.catatan.push({ teks: kiri.trim(), tebal: !!g.tebal });
    else if (g.jenis === 'kaki') M.kaki = kiri;
  });
  const m = /^(TOKO BERAS)\s+(.+)$/i.exec(M.kop.trim());   // "TOKO BERAS M.IQBAL" → besar "M.IQBAL", kecil "TOKO BERAS"
  M.kopBesar = m ? m[2].trim() : M.kop.trim(); M.kopKecil = m ? 'TOKO BERAS' : '';
  return M;
}

/**
 * Tebal goresan tambahan (titik printer) untuk huruf berkontras tinggi. Uji cetak owner 17 Nov di CPad: garis rambut Bodoni hilang di printer panas —
 * Rp44.000 tercetak seperti "Rp 11.000", Rp40.000 seperti "Rp 10.000", "Rp" seperti "Ilp", huruf M logo seperti "VI". Di Mac garis yang sama masih
 * terbaca (perender Mac lebih tebal), jadi pratinjau Mac tidak menangkapnya. Obatnya: tepi huruf ikut digores selebar ini supaya garis tertipis
 * selalu ≥ ±3 titik di perangkat mana pun. Jost (garis rata) tidak perlu. k = lebar kertas / 576 (58 mm lebih kecil, tapi batas bawahnya tetap).
 */
export function stTebalHuruf(font, k) {
  const f = String(font || ''); const kk = k > 0 ? k : 1;
  if (/Bodoni/.test(f)) return Math.max(2, 2.6 * kk);
  if (/Cormorant/.test(f)) return Math.max(1.6, 2 * kk);
  if (/Cinzel/.test(f)) return Math.max(1, 1.2 * kk);
  return 0;
}

// ---------- TANDA TERIMA BARANG MASUK (owner 28 Nov 2026: "struk cetak 2 lembar buat jauh lebih rapi dan lebih profesional termasuk adakan logo") ----------
/** Garis tanda terima bergaya gambar? (baris bertanda `jenis` berawalan 'tt' — terima-barang-logika.js tbmGaris). */
export const stAdaTandaTerima = (garis) => (garis || []).some((g) => g && typeof g.jenis === 'string' && /^tt[A-Z]/.test(g.jenis));
/**
 * Model gambar tanda terima dari garis tbmGaris(). Isi & angka TIDAK berubah: hanya dikelompokkan (kop · judul & nomor · lembar · isian · barang ·
 * jumlah & nilai nota · pembayaran · catatan untuk pemasok · tanda tangan · kaki). Baris ttRuang (ruang tanda tangan gaya teks) diabaikan — gambarnya
 * membuat ruang sendiri.
 */
export function stModelTandaTerima(garis) {
  const M = { kop: '', kopBesar: '', kopKecil: '', alamat: '', telp: '', judul: '', no: '', lembar: '', datang: '', dari: '', barang: [], jumlah: '', nilai: '', bayar: [], bayarKet: [],
    keadaan: '', catatan: [], ttd: null, namaSupir: false, kaki: '' };
  let kini = null; let kel = null;
  (garis || []).forEach((g) => {
    if (!g || g.garis || typeof g.jenis !== 'string') return; const kiri = String(g.kiri || ''); const kanan = String(g.kanan || ''); const j = g.jenis;
    if (j === 'ttKop') M.kop = kiri; else if (j === 'ttAlamat') M.alamat = kiri; else if (j === 'ttTelp') M.telp = String(g.nilai || kiri);
    else if (j === 'ttJudul') M.judul = kiri; else if (j === 'ttNo') M.no = String(g.nilai || ''); else if (j === 'ttLembar') M.lembar = String(g.nilai || '');
    else if (j === 'ttDatang') M.datang = String(g.nilai || ''); else if (j === 'ttDari') M.dari = String(g.nilai || '');
    else if (j === 'ttBarang') { const v = g.nilai && typeof g.nilai === 'object' ? g.nilai : {}; kini = { nama: String(v.nama || kiri), rinci: String(v.rinci || ''), kg: String(v.kg || ''), timbang: '' }; M.barang.push(kini); }
    else if (j === 'ttTimbang') { if (kini) kini.timbang = kanan; }
    else if (j === 'ttJumlah') M.jumlah = kanan; else if (j === 'ttNilai') M.nilai = kanan;
    else if (j === 'ttBayar') M.bayar.push({ label: kiri, n: kanan, tebal: !!g.tebal });
    else if (j === 'ttBayarKet') M.bayarKet.push(kiri); else if (j === 'ttKeadaan') M.keadaan = kiri;
    else if (j === 'ttCatJudul') { kel = { judul: kiri, baris: [] }; M.catatan.push(kel); }
    else if (j === 'ttCat') { if (!kel) { kel = { judul: '', baris: [] }; M.catatan.push(kel); } kel.baris.push({ teks: kiri, n: kanan, tebal: !!g.tebal }); }
    else if (j === 'ttTtd') M.ttd = { kiri, kanan }; else if (j === 'ttNamaSupir') M.namaSupir = true; else if (j === 'ttKaki') M.kaki = kiri;
  });
  const m = /^(TOKO BERAS)\s+(.+)$/i.exec(M.kop.trim());   // "TOKO BERAS M.IQBAL" → besar "M.IQBAL", kecil "TOKO BERAS" (sama dengan nota)
  M.kopBesar = m ? m[2].trim() : M.kop.trim(); M.kopKecil = m ? 'TOKO BERAS' : '';
  return M;
}
