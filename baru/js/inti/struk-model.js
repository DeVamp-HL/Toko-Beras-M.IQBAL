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
