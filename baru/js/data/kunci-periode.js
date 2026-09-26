// KUNCI PERIODE (putaran 25, owner 25 Sep 2026) — inti TANPA impor dan tanpa DOM: bulan mana yang terkunci, tulisan mana yang menyentuh bulan apa,
// dan berapa access call yang dibutuhkan server untuk memeriksanya. Aturannya SAMA dengan firestore.rules v4; periksa_rules.py membandingkan daftar
// koleksi bertanggal, nama field tanggalnya, dan tenggang minimal di kedua tempat.
//
// Dokumen kunci: aturanToko/kunciPeriode = { sampaiBulan: 'YYYY-MM' | null, riwayat: [{ aksi: 'kunci'|'buka', bulan, pada, olehUid, alasan, … }] }.
// Semua bulan ≤ sampaiBulan terkunci (bentuk AWALAN) — jadi yang perlu dinilai dari satu tulisan cukup bulan TERTUA yang disentuhnya.
// Peta lengkap & keputusan owner: docs/peta-kunci-periode.md.
export const KP_ID = 'kunciPeriode';
export const KP_ID_ATUR = 'kunciAtur';
export const KP_TENGGANG_MIN = 3;       // hari — DITEGAKKAN rules (tenggangMin()): bulan M paling cepat dikunci tanggal KP_TENGGANG_MIN + 1 bulan M+1 (owner 25 Sep: 3 → tanggal 4)
export const KP_TENGGANG_BAWAAN = 3;    // bawaan layar = minimal: kunci paling cepat tanggal 4 (bisa dinaikkan owner, tidak di bawah minimal)
export const KP_BATAS_GET = 18;         // access call per kiriman: batas Firebase 20 per batch, sisa 2 (keputusan owner 24 Sep)
// Owner 25 Sep: kunci PERTAMA baru boleh sesudah putaran 25b — index.html & kasir*.html memperlakukan penolakan server sebagai "belum masuk" dan
// antreannya macet di catatan yang ditolak (peta §5). 25b (26 Sep): kasir*.html memisahkan catatan yang ditolak (uji_antrean_kasir.py) dan index.html
// hanya-baca lewat satu penjaga, antrean lamanya dikirim sekali (uji_sistem_lama_bacasaja.py) → true.
export const KP_SIAP_25B = true;
// Putaran 25b: kasir*.html versi ini (= VERSI sw-kasir.js) memisahkan catatan yang ditolak server — satu karcis bulan terkunci tidak lagi menahan karcis lain.
// Perangkat kasir yang berdenyut dalam KP_VERSI_HARI hari terakhir dengan versi di bawahnya = ⛔ di daftar periksa (namanya disebut).
// uji_antrean_kasir.py memastikan nilai ini sama dengan VERSI_APLIKASI kedua berkas kasir dan VERSI sw-kasir.js.
export const KP_VERSI_KASIR_25B = 'kasir-v26';
export const KP_VERSI_HARI = 7;
/** 'kasir-v26' → 26; versi tidak dilaporkan / bentuk lain → 0 (dianggap lama). */
export function kpNomorVersiKasir(v) { const m = /^kasir-v(\d+)$/.exec(String(v || '').trim()); return m ? Number(m[1]) : 0; }
export const kpVersiKasirCukup = (v) => kpNomorVersiKasir(v) >= kpNomorVersiKasir(KP_VERSI_KASIR_25B);
/** Perangkat kasir (kasir-darurat-nominal.html / kasir.html) menurut denyutnya: aplikasi, atau awalan kode perangkat d- / k- (pembagian-tiga-berkas-kasir). */
export const kpPerangkatKasir = (p) => !!p && (p.aplikasi === 'darurat' || p.aplikasi === 'kasir' || /^[dk]-/.test(String(p.id || '')));
export const kpNamaAplikasiKasir = (p) => (p && (p.aplikasi === 'darurat' || /^d-/.test(String(p.id || ''))) ? 'kasir darurat' : 'kasir');
export const KP_WIB_MS = 25200000;      // UTC+7; WIB tanpa musim panas

// Koleksi bertanggal (peta §2): nama field yang dinilai. utangPemasokMutasi tipe saldoAwal dinilai dari bonTanggal (K4: tanggal yang dibaca mesin);
// pengaturan hanya dokumen titikKas (nilai BARU saat simpan — titik boleh maju dari bulan terkunci; nilai LAMA saat dihapus).
// pajakSetoran & pajakOmzetLuar SENGAJA tidak ada (K6). Jejak (logAktivitas dkk.) & setelan tidak ada.
export const KP_KOLEKSI = {
  penjualan: 'tanggal', retur: 'tanggal', pengeluaranHarian: 'tanggal', piutangMutasi: 'tanggal', kasbonMutasi: 'tanggal', utangPemasokMutasi: 'tanggal',
  utangOwnerMutasi: 'tanggal', batchMasuk: 'tanggal', produksiKemasan: 'tanggal', stokBahanKemasan: 'tanggal', stokBahanLiteran: 'tanggal',
  penyesuaianStok: 'tanggal', penyesuaianKemasan: 'tanggal', amplopLaba: 'tanggal', modalOwner: 'tanggal', setoranKas: 'tanggal',
  biayaBulanan: 'bulan', tutupHari: 'tanggal', pindahUang: 'tanggal', slipUpah: 'tanggal', pengaturan: 'tanggal',
};
const KP_BLN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];

/** 'YYYY-MM…' → nomor bulan (tahun × 12 + bulan), sama dengan bulanDari() di rules. Tidak ada / rusak → 0 (paling tua: ikut terkunci bila ada yang terkunci). */
export function kpIdx(s) { return typeof s === 'string' && /^\d{4}-\d{2}(-\d{2})?$/.test(s) ? Number(s.slice(0, 4)) * 12 + Number(s.slice(5, 7)) : 0; }
export function kpBulanStr(idx) { if (!(idx > 0)) return '0000-00'; const y = Math.floor((idx - 1) / 12), m = idx - y * 12; return y + '-' + String(m).padStart(2, '0'); }
export const kpGeser = (bulan, n) => kpBulanStr(kpIdx(bulan) + n);
export function kpNamaBulan(bulan) { const i = kpIdx(bulan); return i > 0 ? KP_BLN[Number(bulan.slice(5, 7)) - 1] + ' ' + bulan.slice(0, 4) : 'bulan tanpa tanggal'; }
export function kpAkhirBulan(bulan) { const y = Number(bulan.slice(0, 4)), m = Number(bulan.slice(5, 7)); return bulan + '-' + String(new Date(Date.UTC(y, m, 0)).getUTCDate()).padStart(2, '0'); }

/** Waktu WIB dari jam perangkat (server memakai request.time + 7 jam; keduanya dihitung dengan cara yang sama). */
export function kpWib(kini) {
  const d = new Date((kini instanceof Date ? kini.getTime() : Date.now()) + KP_WIB_MS);
  const iso = d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0');
  return { iso, bulan: iso.slice(0, 7), hari: d.getUTCDate(), idx: kpIdx(iso) };
}
/** Tanpa get() di server: bulan berjalan (atau sesudahnya), atau bulan lalu selama masa tenggang minimal (bulan itu pasti belum bisa dikunci). */
export function kpBebas(idx, kini) { const W = kpWib(kini); return idx >= W.idx || (idx === W.idx - 1 && W.hari <= KP_TENGGANG_MIN); }
/** Boleh-tidaknya bulan M dikunci MENURUT RULES (tenggang minimal). Tenggang layar (≥ minimal) dinilai di daftar periksa. */
export function kpBolehDikunci(bulan, kini, tenggang) { const W = kpWib(kini); const i = kpIdx(bulan); const t = Math.max(KP_TENGGANG_MIN, Number(tenggang) || KP_TENGGANG_MIN); return i > 0 && (i < W.idx - 1 || (i === W.idx - 1 && W.hari > t)); }

/** Dokumen kunci & setelannya dari isi cache aturanToko. */
export function kpDok(aturan) { return (aturan || []).find((d) => d && String(d.id) === KP_ID) || null; }
export function kpSampai(aturan) { const d = kpDok(aturan); const s = d ? d.sampaiBulan : null; return typeof s === 'string' && /^\d{4}-\d{2}$/.test(s) ? s : null; }
export function kpTenggang(aturan) { const d = (aturan || []).find((x) => x && String(x.id) === KP_ID_ATUR); const n = d ? Math.round(Number(d.tenggang)) : KP_TENGGANG_BAWAAN; return isFinite(n) && n >= KP_TENGGANG_MIN ? Math.min(n, 20) : KP_TENGGANG_BAWAAN; }
export const kpBulanTerkunci = (bulan, sampai) => !!sampai && kpIdx(bulan) <= kpIdx(sampai);
export const kpTanggalTerkunci = (tgl, sampai) => !!sampai && kpIdx(typeof tgl === 'string' && tgl ? tgl : null) <= kpIdx(sampai);

/** Bulan (nomor) yang dinilai dari satu dokumen koleksi bertanggal; null = koleksi / dokumen tidak kena kunci. */
export function kpBulanDok(koleksi, d) {
  const f = KP_KOLEKSI[koleksi]; if (!f || !d) return null;
  if (koleksi === 'pengaturan' && String(d.id) !== 'titikKas') return null;
  if (koleksi === 'utangPemasokMutasi' && d.tipe === 'saldoAwal') return kpIdx(d.bonTanggal || null);
  return kpIdx(d[f]);
}
function kpSama(a, b) {
  if (a === b) return true; if (!a || !b || typeof a !== 'object' || typeof b !== 'object') return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false; const ka = Object.keys(a).sort(), kb = Object.keys(b).sort();
  return ka.length === kb.length && ka.every((k, i) => k === kb[i] && kpSama(a[k], b[k]));
}
/** Bulan tertua yang disentuh satu operasi (= yang dinilai server). op = { koleksi, data?, lama?, hapus? }. null = tidak kena; 'sama' = tulis-ulang identik. */
export function kpBulanOp(op) {
  if (!KP_KOLEKSI[op.koleksi]) return null;
  if (op.hapus) return op.lama ? kpBulanDok(op.koleksi, op.lama) : null;   // dokumen yang tidak ada di cache: server menilai dokumen sungguhan (lihat risiko di peta)
  if (op.lama && kpSama(op.data, op.lama)) return 'sama';
  const b = kpBulanDok(op.koleksi, op.data);
  if (!op.lama || (op.koleksi === 'pengaturan' && String(op.data.id) === 'titikKas')) return b;
  const l = kpBulanDok(op.koleksi, op.lama); if (b === null) return l; if (l === null) return b; return Math.min(b, l);
}
/**
 * Nilai satu kiriman. ops = [{ koleksi, data?, lama?, hapus? }]. Kembali: { terkunci: [{ koleksi, id, bulan }], perluGet (owner & kasir@), lewatTenggang (bukan-owner) }.
 * perluGet = jumlah operasi yang di server memanggil get() dokumen kunci — tulisan bertanggal bulan lampau di luar masa tenggang (cache TIDAK diandalkan).
 */
export function kpNilaiKiriman(ops, sampai, kini) {
  const out = { terkunci: [], perluGet: 0, lewatTenggang: [] };
  (ops || []).forEach((op) => {
    const b = kpBulanOp(op); if (b === null || b === 'sama') return;
    const id = String((op.data && op.data.id) || (op.lama && op.lama.id) || op.id || '');
    if (sampai && b <= kpIdx(sampai)) out.terkunci.push({ koleksi: op.koleksi, id, bulan: kpBulanStr(b) });
    if (!kpBebas(b, kini)) { out.perluGet += 1; out.lewatTenggang.push({ koleksi: op.koleksi, id, bulan: kpBulanStr(b) }); }
  });
  return out;
}
/** Kalimat penolakan yang sama di semua layar. */
export function kpKalimat(bulan, pembalik) { return 'Bulan ' + kpNamaBulan(bulan) + ' terkunci — ' + (pembalik || 'catatannya tidak bisa diubah lagi; betulkan dengan catatan hari ini'); }

/**
 * KIRIM BERTAHAP (owner 25 Sep): kiriman owner yang menyentuh banyak dokumen bulan lampau dipecah; tiap potongan ≤ KP_BATAS_GET operasi ber-get().
 * kelompok = [{ dokumen: [{ koleksi, data }], hapus: [{ koleksi, id }] }] — satu kelompok = satu kesatuan yang tidak boleh terbelah (mis. baris pengganti + asal yang ditandai).
 * cariLama(koleksi, id) → dokumen lama di cache (untuk menilai update/hapus). Kembali { potongan: [{ dokumen, hapus, get }] } atau { tolak }.
 */
export function kpPotong(kelompok, cariLama, kini) {
  const potongan = []; let kini_ = { dokumen: [], hapus: [], get: 0 };
  for (let i = 0; i < (kelompok || []).length; i++) {
    const k = kelompok[i]; const ops = (k.dokumen || []).map((x) => ({ koleksi: x.koleksi, data: x.data, lama: cariLama(x.koleksi, x.data.id) })).concat((k.hapus || []).map((x) => ({ koleksi: x.koleksi, id: x.id, lama: cariLama(x.koleksi, x.id), hapus: true })));
    const g = kpNilaiKiriman(ops, null, kini).perluGet;
    if (g > KP_BATAS_GET) return { tolak: 'Satu bagian kiriman ini sendiri menyentuh ' + g + ' catatan bulan lampau (batas ' + KP_BATAS_GET + ' sekali kirim) — tidak bisa dipecah lebih kecil' };
    if (kini_.get + g > KP_BATAS_GET && (kini_.dokumen.length || kini_.hapus.length)) { potongan.push(kini_); kini_ = { dokumen: [], hapus: [], get: 0 }; }
    kini_.dokumen = kini_.dokumen.concat(k.dokumen || []); kini_.hapus = kini_.hapus.concat(k.hapus || []); kini_.get += g;
  }
  if (kini_.dokumen.length || kini_.hapus.length) potongan.push(kini_);
  return { potongan };
}
