// KELAS BERAS BAHAN vs LABEL HASIL ADUKAN — "isi kemasan sesuai label, tanpa oplos" (paket P5, owner 27 Nov 2026, sensus A50). Tanpa DOM, BACA SAJA, awalan kh.
//
// Modul DAUN (data/toko.js + pembantu + jual-logika aturWadah — semuanya sudah ada di tiap bundel yang memuat Adukan) supaya Adukan bisa memeriksa kelas tanpa
// membawa het-logika / harga-logika / kelas-merek-logika ke bundel Stok. Satu sumber dengan Harga › HET: kelas bahan = peta HET owner (aturanToko/het.peta) atas
// SATUAN pemetaan merek itu — aturan yang SAMA dengan hetUnit (kelas yang DIKONFIRMASI: nama wadah, kelas tanpa wadah, peta owner, dipakai jadi kelas; tebakan =
// merek itu sendiri), dibaca langsung dari aturanToko/kelasMerek seperti kmKelasMerk + kmTerisi; uji_stok_p5 membandingkan khKategori dengan
// hetAtur().peta[hetUnit(m).unit] untuk setiap merek di cadangan toko. Kelas label hasil = kelas mutu Atur label (aturanToko/catatStok.label.kelas, label-logika)
// bila owner mengisinya untuk kemasan itu; selain itu peta HET atas nama hasilnya.
// Keputusan owner 27 Nov 2026: bahan berkelas LEBIH RENDAH dari label hasil (mis. medium → label premium) = OPLOS → DITAHAN (akun staf tidak bisa menyimpan;
// owner dua ketukan + alasan, adukannya bertanda merah). Bahan lebih tinggi dari label (premium dikemas medium) tidak ditandai. Belum dipetakan = disebut saja.
import { cacheMentah } from '../data/toko.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { aturWadah } from './jual-logika.js';

// tingkat kelas: angka lebih besar = kelas lebih tinggi. 'bukan' (bukan beras HET, mis. ketan) tidak dibandingkan.
export const KH_TINGKAT = { premium: 3, medium: 2, submedium: 1, pecah: 0 };
export const KH_NAMA = { premium: 'premium', medium: 'medium', submedium: 'submedium', pecah: 'pecah', bukan: 'bukan beras HET' };
const KH_HET = ['premium', 'medium', 'bukan'];
const KH_LABEL = ['Premium', 'Medium', 'Submedium', 'Pecah'];   // = LB_KELAS label-logika (uji_stok_p5 memeriksa sama)
const khBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const khDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;

/** Peta HET owner { satuan: 'premium' | 'medium' | 'bukan' } (isi yang tidak dikenal dibuang — sama dengan hetAtur). */
export function khPetaHet() {
  const d = khDok('het'); const p = d && d.peta && typeof d.peta === 'object' && !Array.isArray(d.peta) ? d.peta : {}; const out = {};
  Object.keys(p).forEach((u) => { if (KH_HET.indexOf(p[u]) >= 0) out[u] = p[u]; }); return out;
}
/** Satuan pemetaan HET satu merek (aturan hetUnit): kelas yang sudah dikonfirmasi owner, selain itu merek itu sendiri. */
export function khSatuan(merk) {
  const m = khBersih(merk); if (!m) return ''; if (aturWadah().daftar.indexOf(m) >= 0) return m;   // nama = nama wadah (asal 'wadah')
  const d = khDok('kelasMerek'); const obj = (o) => (o && typeof o === 'object' && !Array.isArray(o) ? o : {}); const peta = obj(d && d.peta), asal = obj(d && d.asal);
  if (d && Array.isArray(d.kelasSendiri) && d.kelasSendiri.map(String).indexOf(m) >= 0) return m;   // kelas tanpa wadah
  if (Object.prototype.hasOwnProperty.call(peta, m)) { const k = khBersih(peta[m]); return asal[m] === 'tebakan' || !k ? m : k; }   // peta owner ('' = sengaja tanpa kelas)
  return m;   // dipakai jadi kelas merek lain = kelasnya dirinya sendiri; tebakan / tanpa petunjuk = merek itu sendiri
}
/** Kategori HET merek/nama: 'premium' | 'medium' | 'bukan' | '' (belum dipetakan). */
export function khKategori(merk, peta) { const P = peta || khPetaHet(); return P[khSatuan(merk)] || ''; }
/** Kelas mutu yang diisi owner di Atur label untuk kemasan itu ('Premium' … ) atau ''. */
export function khKelasLabel(nama, ukuran) {
  const d = khDok('catatStok'); const a = d && d.label && typeof d.label === 'object' && d.label.kelas && typeof d.label.kelas === 'object' ? d.label.kelas : {};
  const v = a[kunciKemasan(khBersih(nama), Number(ukuran))]; return KH_LABEL.indexOf(v) >= 0 ? v : '';
}
const khTingkat = (k) => { const x = String(k || '').toLowerCase(); return KH_TINGKAT[x] !== undefined ? KH_TINGKAT[x] : null; };

/**
 * Periksa satu adukan. bahan = [{ nama }] (karung: merek · kemasan yang dibongkar: { nama, ukuran }), hasil = [{ nama, ukuran }].
 * → { status: 'kosong' | 'oplos' | 'belum' | 'aman', oplos: [{ hasil, kelasHasil, sumberKelas, bahan, kelasBahan }], belum: [nama], bahan: [...], hasil: [...], teks }.
 * Oplos = ada bahan yang tingkatnya LEBIH RENDAH dari label salah satu hasil. Nama 'bukan beras HET' tidak dibandingkan. Belum dipetakan = tidak bisa diperiksa (disebut).
 */
export function khCekAdukan(bahan, hasil) {
  const P = khPetaHet();
  const B = (bahan || []).filter((x) => x && khBersih(x.nama)).map((x) => { const lb = x.ukuran ? khKelasLabel(x.nama, x.ukuran) : ''; const k = lb ? lb.toLowerCase() : khKategori(x.nama, P);
    return { nama: khBersih(x.nama) + (x.ukuran ? ' ' + String(x.ukuran).replace('.', ',') + ' kg' : ''), kelas: k, tingkat: khTingkat(k) }; });
  const H = (hasil || []).filter((x) => x && khBersih(x.nama)).map((x) => { const lb = khKelasLabel(x.nama, x.ukuran); const k = lb ? lb.toLowerCase() : khKategori(x.nama, P);
    return { nama: khBersih(x.nama) + ' ' + String(x.ukuran || '').replace('.', ',') + ' kg', kelas: k, sumber: lb ? 'label' : k ? 'het' : '', tingkat: khTingkat(k) }; });
  if (!B.length || !H.length) return { status: 'kosong', oplos: [], belum: [], bahan: B, hasil: H, teks: '' };
  const oplos = []; H.forEach((h) => { if (h.tingkat === null) return; B.forEach((b) => { if (b.tingkat !== null && b.tingkat < h.tingkat) oplos.push({ hasil: h.nama, kelasHasil: KH_NAMA[h.kelas] || h.kelas, sumberKelas: h.sumber, bahan: b.nama, kelasBahan: KH_NAMA[b.kelas] || b.kelas }); }); });
  const belum = B.concat(H).filter((x) => !x.kelas).map((x) => x.nama).filter((n, i, a) => a.indexOf(n) === i);
  const status = oplos.length ? 'oplos' : belum.length ? 'belum' : 'aman';
  const teks = oplos.length ? 'OPLOS: ' + oplos.map((o) => o.bahan + ' (' + o.kelasBahan + ') masuk ke ' + o.hasil + ' berlabel ' + o.kelasHasil + (o.sumberKelas === 'label' ? ' (Atur label)' : ' (peta HET)')).join(' · ')
    : belum.length ? 'Kelas belum dipetakan: ' + belum.join(', ') + ' — tidak bisa diperiksa oplosnya (petakan di Harga › HET atau Atur label)'
      : 'Kelas bahan sama atau lebih tinggi dari label hasil — bukan oplos';
  return { status, oplos, belum, bahan: B, hasil: H, teks };
}
