// Sumber data pengganti: berkas cadangan toko (backup-batch-*.json yang diunduh dari index.html).
// Dipakai untuk mencoba sistem baru di komputer tanpa menyentuh Firestore — mis. ?cadangan=../backup-batch-….json
// Berkas cadangan TIDAK ikut repo (.gitignore); di toko nyata jalur ini tidak dipakai.
import { pasok, setelSumber } from './toko.js';

export async function muatCadangan(url) {
  const r = await fetch(url, { cache: 'no-store' });
  if (!r.ok) throw new Error('cadangan tidak terbaca: ' + r.status);
  const cad = await r.json();
  return isiDariCadangan(cad, url);
}

export function isiDariCadangan(cad, keterangan) {
  let n = 0;
  Object.keys(cad).forEach((nama) => { if (Array.isArray(cad[nama]) && pasok(nama, cad[nama])) n += 1; });
  // peta tempat simpan di cadangan (petaTempatSimpan, dari localStorage sistem lama) → dokumen pengaturan/tempatSimpan yang dibaca layar Stok
  if (cad.petaTempatSimpan && typeof cad.petaTempatSimpan === 'object' && !Array.isArray(cad.pengaturan)) { pasok('pengaturan', [{ id: 'tempatSimpan', peta: cad.petaTempatSimpan }]); n += 1; }
  // peta jenis beras di cadangan v5 ikut dibawa ke localStorage (kunci yang sama dengan index.html)
  if (cad.petaJenisBeras && typeof cad.petaJenisBeras === 'object') {
    try { localStorage.setItem('miqbal_jenis_beras_v1', JSON.stringify(cad.petaJenisBeras)); } catch (e) { /* penyimpanan terkunci */ }
  }
  setelSumber('cadangan', 'cadangan ' + String(cad.diunduhPada || '').slice(0, 10) + (keterangan ? ' · ' + keterangan.split('/').pop() : ''));
  return { koleksi: n, diunduhPada: cad.diunduhPada || null };
}
