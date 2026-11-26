// SCAN STRUK = KEADAAN NOTA MENURUT DATA TOKO (owner 26 Nov 2026, paket "QR satu pintu" bagian B). Logika TANPA DOM, nama berawalan sp.
// Dijaga alat-uji/uji_pindai_struk.py.
//
// Begitu QR struk di-scan di tablet, lembar struk menampilkan keadaan nota itu menurut DATA, bukan menurut kertasnya: berlaku / dibatalkan / dikoreksi,
// tanggal & umur nota, total yang tercatat, retur yang sudah terjadi, sisa bon (nota ini & semua bon orangnya), faktur, surat jalan. Kertas yang angkanya
// dicoret, struk dari nota yang sudah dibatalkan, atau struk lama yang dibawa lagi untuk retur langsung ketahuan.
// TIDAK ADA ANGKA BARU: semuanya dibaca dari penyusun yang sudah ada — notaDari (struk-logika), semuaBon & pnNota (bon-logika, sisa per nota yang menutup ke
// mesin), fkNota (faktur), ajKeadaan (surat jalan), koleksi retur (notaAsalId). Bayar bon tetap lewat lembar Pelanggan › Bon yang sudah ada (susunBayarBon):
// modul ini hanya MENYIAPKAN isiannya (orang, faktur yang dipilih, nominal bila jelas), tidak menulis apa pun.
import { ambilRetur, kunciNota, ingatPerVersi } from '../data/toko.js';
import { semuaBon, pnNota } from './bon-logika.js';
import { fkNota } from './faktur-logika.js';
import { ajUntukNota, ajKeadaan } from './antar-logika.js';
// paket QR kedua (owner 26 Nov 2026): retur sekali scan — baris karung & kemasan yang bisa diretur, dihitung penyusun Riwayat yang sama (rwNotaLengkap)
import { rwNotaLengkap, rwKunci } from './riwayat-logika.js';
// karcis ambil nanti (owner 26 Nov 2026): barang titipan nota yang di-scan
import { abKeadaan, abJumlahTeks } from './ambil-logika.js';
import { kunciPelanggan, formatTanggal } from '../mesin/pembantu.js';
import { RP, hariIniIso } from '../inti/format.js';

const spHariKe = (iso) => { const m = /^(\d{4})-(\d\d)-(\d\d)$/.exec(String(iso || '')); return m ? Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000) : null; };
/** Umur nota dalam kata: 'hari ini' · 'kemarin' · 'N hari lalu' · '' (tanggal tidak terbaca). */
export function spUmurKata(tanggal, iso) {
  const a = spHariKe(tanggal), b = spHariKe(iso); if (a === null || b === null) return '';
  const d = b - a; return d <= 0 ? 'hari ini' : d === 1 ? 'kemarin' : d + ' hari lalu';
}
/** Nomor nota pendek (sama dengan stNoNota di struk-logika — modul ini tidak mengimpor struk-logika supaya tidak melingkar). */
const spNoPendek = (nota) => String((nota && (nota.trxId || nota.grupNota || nota.id)) || '').replace(/\D/g, '').slice(-6);

/**
 * Keadaan satu nota untuk pita scan. nota = bentuk notaDari / notaDariBaris (struk-logika); kini = Date (bawaan sekarang).
 * Hasil null (tanpa nota) atau { status: 'berlaku' | 'batal' | 'koreksi', judul, awas (perlu perhatian), baris: [teks], retur: banyak retur,
 *   bon: null | { sisaNota, sisaOrang, nama, tertua, faktur }, bayar: null | { orang, nama, faktur: [no], nominal: '' | teks angka, catatan },
 *   barisRetur: [{ id (baris nota), teks, bisa, sebab }] — karung & kemasan nota yang masih berlaku (paket QR kedua: retur sekali scan) }.
 * bayar.nominal hanya diisi bila jelas: faktur (sisa faktur itu — pembayaran menunjuk faktur), atau bon eceran yang memang TERTUA (pembayaran bon
 * menutup yang tertua dulu, jadi angka nota lain akan menutup nota yang salah). Selain itu kosong — kasir mengetik sendiri.
 */
export function spKeadaanNota(nota, kini) {
  if (!nota) return null;
  const iso = hariIniIso(kini || new Date());
  const kunci = (nota.baris || []).length ? kunciNota(nota.baris[0]) : String(nota.trxId || nota.grupNota || nota.id || '');
  return ingatPerVersi('spKeadaan|' + kunci + '|' + iso, () => spHitung(nota, iso, kini || new Date()));
}
function spHitung(nota, iso, kini) {
  const status = nota.berlaku ? 'berlaku' : nota.dibatalkan ? 'batal' : 'koreksi';
  const judul = status === 'berlaku' ? 'NOTA ASLI — tercatat di data toko & masih berlaku' : status === 'batal' ? 'NOTA INI SUDAH DIBATALKAN — tidak berlaku lagi' : 'NOTA INI SUDAH DIKOREKSI — tidak berlaku lagi';
  const baris = []; let awas = status !== 'berlaku';
  const umur = spUmurKata(nota.tanggal, iso);
  baris.push('Dibeli ' + formatTanggal(nota.tanggal) + (nota.jam ? ' ' + nota.jam : '') + (umur ? ' (' + umur + ')' : '') + ' · ' + (nota.nama || 'tanpa nama'));
  baris.push(status === 'berlaku' ? 'Total menurut data toko ' + RP(nota.total) + ' — kalau angka di kertas beda, yang benar angka ini'
    : 'Waktu dicatat totalnya ' + RP(nota.total) + ' — kertas ini tidak bisa dipakai untuk retur atau tagihan');
  // retur yang sudah terjadi dari baris-baris nota ini (dokumen retur menunjuk baris asalnya lewat notaAsalId)
  const ids = new Set((nota.baris || []).map((p) => String(p.id)));
  const rt = (ambilRetur() || []).filter((r) => r && r.notaAsalId !== undefined && r.notaAsalId !== null && ids.has(String(r.notaAsalId)))
    .sort((a, b) => String(a.tanggal + ' ' + (a.jam || '')).localeCompare(String(b.tanggal + ' ' + (b.jam || ''))));
  if (rt.length) baris.push('Sudah ' + rt.length + ' kali retur dari nota ini · terakhir ' + formatTanggal(rt[rt.length - 1].tanggal) + ' — periksa barangnya sebelum retur lagi');
  // uang: lunas saat beli, atau bon (sisa nota ini dari pnNota yang menutup ke mesin; faktur dari fkNota)
  let bon = null, bayar = null;
  if (nota.cara !== 'Kredit') baris.push('Dibayar ' + (nota.cara || 'Tunai') + ' saat beli');
  else if (status === 'berlaku' && kunciPelanggan(nota.nama)) {
    const orang = kunciPelanggan(nota.nama); const B = semuaBon(kini); const b = B.find((x) => x.kunci === orang) || null;
    const P = pnNota(kini, B); const k = 'n:' + ((nota.baris || []).length ? kunciNota(nota.baris[0]) : '');
    const x = P.nota.find((y) => y.kunci === k) || null; const sisaNota = x ? Math.round(x.sisa) : 0;
    const F = fkNota(nota.trxId || nota.grupNota || nota.id, kini); const fBuka = F && F.sisa > 0.5 ? F : null;
    const tertua = !!(b && b.buka && b.buka.length && ids.has(String(b.buka[0].idTrx)));
    const sisaOrang = b ? Math.max(0, Math.round(b.sisa)) : 0;
    bon = { sisaNota, sisaOrang, nama: b ? b.nama : nota.nama, tertua, faktur: fBuka ? fBuka.no : '' };
    if (sisaNota > 0) {
      const lewat = x && x.status === 'lewat' ? ' · LEWAT jatuh tempo ' + x.hariLewat + ' hari' : x && x.status === 'hariIni' ? ' · jatuh tempo HARI INI' : '';
      baris.push((fBuka ? 'Faktur ' + fBuka.no : 'Bon nota ini') + ': sisa ' + RP(fBuka ? fBuka.sisa : sisaNota) + lewat + (sisaOrang > sisaNota ? ' · semua bon ' + bon.nama + ' ' + RP(sisaOrang) : ''));
      if (lewat) awas = true;
    } else baris.push('Bon nota ini sudah tertutup' + (sisaOrang > 0 ? ' · ' + bon.nama + ' masih punya bon lain ' + RP(sisaOrang) : ''));
    if (b && sisaOrang > 0) {
      const nominal = fBuka ? String(Math.round(fBuka.sisa)) : sisaNota > 0 && tertua ? String(Math.min(sisaNota, sisaOrang)) : '';
      bayar = { orang, nama: b.nama, faktur: fBuka ? [fBuka.no] : [], nominal, catatan: 'Scan struk nota No. ' + spNoPendek(nota) };
      if (!fBuka && sisaNota > 0 && !tertua) baris.push('Bayar bon eceran menutup nota TERTUA dulu — nota ini bukan yang tertua, jadi jumlahnya diketik sendiri');
    }
  } else if (status === 'berlaku') baris.push('Nota bon tanpa nama pembeli — tidak ada bon yang bisa dibayar dari sini');
  // surat jalan
  if (nota.noSJ) {
    const sj = ajUntukNota(nota.trxId)[0] || null; const K = sj ? ajKeadaan(sj, iso) : null;
    baris.push('Diantar · surat jalan ' + nota.noSJ + (K ? ' · ' + K.statusTeks + (K.sisaTagih > 0 ? ' · uang bayar di tempat belum pulang ' + RP(K.sisaTagih) : '') : ''));
    if (K && K.sisaTagih > 0 && K.status !== 'berangkat') awas = true;
  }
  // retur sekali scan (paket QR kedua): baris karung & kemasan nota yang masih berlaku — bisa diretur (tombol di pita) atau sebabnya tidak bisa
  const L = status === 'berlaku' && (nota.baris || []).length ? rwNotaLengkap(rwKunci(nota.baris[0])) : null;
  const barisRetur = L ? L.baris.filter((b) => b.bisaRetur || b.sebabRetur).map((b) => ({ id: String(b.id), teks: b.teks, bisa: !!b.bisaRetur, sebab: b.bisaRetur ? '' : String(b.sebabRetur || '') })) : [];
  // karcis ambil nanti: struk = karcisnya — barang yang masih dititip & tombol serahkan (Jual) bila ada sisa
  const T = status === 'berlaku' && nota.trxId ? abKeadaan(nota.trxId) : null;
  if (T && !T.batal) baris.push(T.habis ? 'Barang titipan sudah diambil semua' : 'DITITIP — belum diambil: ' + T.isi.filter((x) => x.sisa > 0).map((x) => x.nama + ' ' + abJumlahTeks(x.sisa, x.satuan)).join(', '));
  return { status, judul, awas, baris, retur: rt.length, bon, bayar, barisRetur, titip: T && !T.batal && !T.habis ? { trxId: T.trxId } : null };
}
