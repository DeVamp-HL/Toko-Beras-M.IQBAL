// KUNCI PERIODE (putaran 25, owner 25 Sep 2026) — inti TANPA impor dan tanpa DOM: bulan mana yang terkunci, tulisan mana yang menyentuh bulan apa,
// dan berapa access call yang dibutuhkan server untuk memeriksanya. Aturannya SAMA dengan firestore.rules v4; periksa_rules.py membandingkan daftar
// koleksi bertanggal, nama field tanggalnya, dan tenggang minimal di kedua tempat.
//
// Dokumen kunci: aturanToko/kunciPeriode = { sampaiBulan: 'YYYY-MM' | null, riwayat: [{ aksi: 'kunci'|'buka', bulan, pada, olehUid, alasan, … }] }.
// Semua bulan ≤ sampaiBulan terkunci (bentuk AWALAN) — jadi yang perlu dinilai dari satu tulisan cukup bulan TERTUA yang disentuhnya.
// Peta lengkap & keputusan owner: docs/peta-kunci-periode.md.
export const KP_ID = 'kunciPeriode';
export const KP_ID_ATUR = 'kunciAtur';
// Keputusan owner 1 Okt 2026 (pilihan A): bulan 2026 TIDAK dikunci sampai tutup buku 2026 selesai — kunci berbentuk awalan (mengunci September ikut
// mengunci 2022–Agustus), lalu saldo pembuka bertanggal lama & arsip tutup buku pasti ditolak server. Kunci bulanan mulai Januari 2027.
export const KP_KUNCI_MULAI = '2027-01';
export const KP_TENGGANG_MIN = 3;       // hari — DITEGAKKAN rules (tenggangMin()): bulan M paling cepat dikunci tanggal KP_TENGGANG_MIN + 1 bulan M+1 (owner 25 Sep: 3 → tanggal 4)
export const KP_TENGGANG_BAWAAN = 3;    // bawaan layar = minimal: kunci paling cepat tanggal 4 (bisa dinaikkan owner, tidak di bawah minimal)
export const KP_BATAS_GET = 18;         // access call per kiriman: batas Firebase 20 per batch, sisa 2 (keputusan owner 24 Sep)
// Owner 25 Sep: kunci PERTAMA baru boleh sesudah putaran 25b — index.html & kasir*.html memperlakukan penolakan server sebagai "belum masuk" dan
// antreannya macet di catatan yang ditolak (peta §5). 25b (26 Sep): kasir*.html memisahkan catatan yang ditolak (uji_antrean_kasir.py) dan index.html
// hanya-baca lewat satu penjaga, antrean lamanya dikirim sekali (uji_sistem_lama_bacasaja.py) → true. Sejak 3 Okt 2026 index.html & kasir.html pensiun
// (halaman pengalih; uji_sistem_lama_bacasaja.py ikut dihapus) — nilai ini tetap true.
export const KP_SIAP_25B = true;
// Putaran 25b: kasir*.html versi ini (= VERSI sw-kasir.js) memisahkan catatan yang ditolak server — satu karcis bulan terkunci tidak lagi menahan karcis lain.
// Perangkat kasir yang berdenyut dalam KP_VERSI_HARI hari terakhir dengan versi di bawahnya = ⛔ di daftar periksa (namanya disebut).
// Sampai 25b nilai ini = VERSI sw-kasir.js. Sejak 25c (kasir-v27) ia LANTAI kunci bulan saja — HP v26 sudah memisahkan karcis ditolak, jadi tidak menahan
// kunci; versi terbaru yang disajikan = KK_VERSI_KASIR_TERBARU (katalog-kasir.js). uji_antrean_kasir.py: lantai ≤ versi sw = versi terbaru /baru/.
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
// ---- PINTU TUTUP BUKU (rules v7, keputusan owner 7 Okt K8 "pengecualian sempit"; sanggahan rules 7 Okt) — inti klien yang SAMA dengan firestore.rules
// pintuTahun / pintuTulis / pintuHapus / pintuTitik / pintuSah / arsipSah / acaraTutupPintu. Dokumen pengaturan/pintuBuku = { id, tahun: Y, status: 'berjalan' |
// 'tutup', sampai: Date (Timestamp di server) }. Selama terbuka & belum lewat `sampai`, OWNER boleh (hanya catatan bertanggal ≤ Desember Y yang bulannya
// terkunci): membuat / menghapus saldo pembuka tahun Y (tutupBuku + tahunDari Y) di KP_KOLEKSI_PEMBUKA saja, menghapus catatan yang salinannya ikut ditulis
// ke arsipTahun di batch yang sama (op.arsip — rules membandingkan isinya), mengembalikan catatan dari arsip Y (op.pulih — isinya sama dengan salinannya), dan
// menulis titik kas 31 Des Y atau PERSIS titikSebelum berita acara Y. Tidak ada pintu untuk ubah.
// Access call di server (cache tidak diandalkan): 1 (kunci) + 1 (pintu) + 1 (salinan arsip, hanya arsip & pulih; berita acara, hanya titik kembali). Salinan
// arsip yang ikut ditulis: 1 (kunci, di luar masa bebas) + 1 (catatan asli, bila bulannya terkunci). Membuka pintu: 1 (berita acara). Berita acara
// selesai / dibatalkan: 1 (pintu).
export const KP_ID_PINTU = 'pintuBuku';
export const KP_PINTU_JAM_MAKS = 72;   // = rules pintuSah(): sampai ≤ jam server + 72 jam
export const KP_PINTU_JAM = 48;        // umur yang ditulis aplikasi (jam perangkat): sisa 24 jam untuk jam HP yang kecepatan
export const KP_PINTU_SISA_JAM = 12;   // pintu yang tinggal < 12 jam diperbarui (dibuka lagi) sebelum arsip / pembatalan dilanjutkan
export const KP_KOLEKSI_PINTU = ['penjualan', 'batchMasuk', 'produksiKemasan', 'retur', 'pengeluaranHarian', 'setoranKas', 'penyesuaianKemasan', 'amplopLaba', 'modalOwner',
  'utangPemasokMutasi', 'utangOwnerMutasi', 'stokBahanKemasan', 'stokBahanLiteran', 'piutangMutasi', 'kasbonMutasi', 'penyesuaianStok', 'tutupHari', 'biayaBulanan'];   // = koleksi yang diarsip tutup buku (tbDaftarKoleksi ∩ KP_KOLEKSI; rules kolArsip; periksa_rules.py & uji_tutup_buku_2027.py)
// koleksi yang memang punya SALDO PEMBUKA tutup buku = nilai toko.js CACHE_PEMBUKA = rules kolPembuka() (periksa_rules.py membandingkan ketiganya)
export const KP_KOLEKSI_PEMBUKA = ['batchMasuk', 'piutangMutasi', 'kasbonMutasi', 'produksiKemasan', 'stokBahanKemasan', 'stokBahanLiteran', 'utangPemasokMutasi', 'utangOwnerMutasi',
  'amplopLaba', 'modalOwner'];
export const KP_TITIK_KOLOM = ['tanggal', 'laci', 'brankas', 'rekening', 'amplop'];   // = rules titikSebelum(): titik kas yang dikembalikan = titikSebelum persis
export const KP_ACARA_AKHIR = ['selesai', 'dibatalkan'];   // = rules acaraTutupPintu(): berita acara berstatus ini membaca dokumen pintu (1 access call)
/** Milidetik dari nilai waktu apa pun yang mungkin dipegang cache: Date, Timestamp Firestore (toMillis), {seconds} (berkas cadangan), angka, teks ISO. */
export function kpMs(v) {
  if (v === null || v === undefined) return NaN;
  if (v instanceof Date) return v.getTime();
  if (typeof v.toMillis === 'function') return v.toMillis();
  if (typeof v === 'object' && v.seconds !== undefined) return Number(v.seconds) * 1000 + Math.floor(Number(v.nanoseconds || 0) / 1e6);
  if (typeof v === 'number') return v;
  return Date.parse(String(v));
}
/** Pintu yang TERBUKA menurut dokumen d pada jam kini → { tahun, sampai (ms), titikSebelum } atau null (tidak ada / tutup / lewat / bentuk salah).
 *  titikSebelum = titik kas sebelum tutup buku di berita acara tahun itu (toko.js pintuDari) — satu-satunya titik selain 31 Des yang boleh lewat pintu. */
export function kpPintu(d, kini, titikSebelum) {
  if (!d || d.status !== 'berjalan') return null; const y = Number(d.tahun); const s = kpMs(d.sampai); const t = kini instanceof Date ? kini.getTime() : Date.now();
  return Number.isFinite(y) && y > 0 && Number.isFinite(s) && s > t ? { tahun: Math.trunc(y), sampai: s, titikSebelum: titikSebelum && typeof titikSebelum === 'object' ? titikSebelum : null } : null;
}
/** Titik kas d = titikSebelum s PERSIS (tanggal & keempat kantong; kolom yang tidak ada = null) — rules titikSebelum(). */
export function kpTitikSebelum(d, s) {
  const v = (x, k) => (x && x[k] !== undefined ? x[k] : null);
  return !!(d && s && typeof s === 'object') && KP_TITIK_KOLOM.every((k) => kpSama(v(d, k), v(s, k)));
}
/** Satu operasi bulan terkunci lewat pintu? → access call TAMBAHAN di luar pemeriksaan kunci (1 pembuka / titik 31 Des, 2 arsip / pulih / titik kembali) atau 0 (ditolak). */
export function kpLewatPintu(op, b, pintu) {
  if (!pintu || !(b <= pintu.tahun * 12 + 12)) return 0;
  const y = pintu.tahun; const pembuka = (d) => !!d && KP_KOLEKSI_PEMBUKA.indexOf(op.koleksi) >= 0 && d.tutupBuku === true && Number(d.tahunDari) === y;
  if (op.koleksi === 'pengaturan') { if (!(op.data && String(op.data.id) === 'titikKas' && !op.hapus)) return 0; return op.data.tanggal === y + '-12-31' ? 1 : kpTitikSebelum(op.data, pintu.titikSebelum) ? 2 : 0; }
  if (KP_KOLEKSI_PINTU.indexOf(op.koleksi) < 0) return 0;
  if (op.hapus) return pembuka(op.lama) ? 1 : op.arsip ? 2 : 0;
  if (op.lama) return 0;   // dokumen sudah ada = UBAH → tidak ada pintu untuk ubah
  return pembuka(op.data) ? 1 : op.pulih ? 2 : 0;
}
/**
 * Nilai satu kiriman. ops = [{ koleksi, data?, lama?, hapus?, arsip?, pulih? }]. Kembali: { terkunci: [{ koleksi, id, bulan }], perluGet (owner & kasir@), lewatTenggang
 * (bukan-owner), lewatPintu }. perluGet = jumlah access call server untuk kunci — 1 per tulisan bertanggal bulan lampau di luar masa tenggang (cache TIDAK
 * diandalkan) — DITAMBAH jalur pintu tutup buku (pintu = kpPintu(…) atau null; hanya dinilai bila `sampai` diberikan) dan pembukaan pintu (1).
 */
export function kpNilaiKiriman(ops, sampai, kini, pintu) {
  const out = { terkunci: [], perluGet: 0, lewatTenggang: [], lewatPintu: 0 };
  (ops || []).forEach((op) => {
    if (op.koleksi === 'pengaturan' && !op.hapus && op.data && String(op.data.id) === KP_ID_PINTU && op.data.status === 'berjalan') out.perluGet += 1;   // pintuSah: get berita acara
    // rules acaraTutupPintu: berita acara selesai / dibatalkan membaca dokumen pintu (kirim ulang identik tidak)
    if (op.koleksi === 'tutupBukuAcara' && !op.hapus && op.data && KP_ACARA_AKHIR.indexOf(op.data.status) >= 0 && !(op.lama && kpSama(op.data, op.lama))) out.perluGet += 1;
    const b = kpBulanOp(op); if (b === null || b === 'sama') return;
    const id = String((op.data && op.data.id) || (op.lama && op.lama.id) || op.id || '');
    let tambah = 0; const kunci = !!sampai && b <= kpIdx(sampai);
    if (kunci) { tambah = kpLewatPintu(op, b, pintu); if (tambah) out.lewatPintu += 1; else out.terkunci.push({ koleksi: op.koleksi, id, bulan: kpBulanStr(b) }); }
    if (!kpBebas(b, kini)) { out.perluGet += 1 + tambah; out.lewatTenggang.push({ koleksi: op.koleksi, id, bulan: kpBulanStr(b) }); }
    // arsip: salinan arsipTahun yang ikut ditulis (rules arsipSah) — 1 (kunci) di luar masa bebas, + 1 (catatan asli) bila bulannya terkunci
    if (op.hapus && op.arsip) out.perluGet += (kpBebas(b, kini) ? 0 : 1) + (kunci ? 1 : 0);
  });
  return out;
}
/** Pecah daftar biaya (access call per butir) jadi potongan: ≤ batasN butir dan ≤ batasGet access call per potongan → [[awal, akhir)…]. Butir > batasGet = sendiri. */
export function kpPecahBiaya(biaya, batasN, batasGet) {
  const out = []; let a = 0, g = 0;
  for (let i = 0; i < biaya.length; i += 1) {
    const x = Number(biaya[i]) || 0;
    if (i > a && (i - a >= batasN || g + x > batasGet)) { out.push([a, i]); a = i; g = 0; }
    g += x;
  }
  if (a < biaya.length) out.push([a, biaya.length]);
  return out;
}
/** Kalimat penolakan yang sama di semua layar. */
export function kpKalimat(bulan, pembalik) { return 'Bulan ' + kpNamaBulan(bulan) + ' terkunci — ' + (pembalik || 'catatannya tidak bisa diubah lagi; betulkan dengan catatan hari ini'); }

/**
 * KIRIM BERTAHAP (owner 25 Sep): kiriman owner yang menyentuh banyak dokumen bulan lampau dipecah; tiap potongan ≤ KP_BATAS_GET operasi ber-get().
 * kelompok = [{ dokumen: [{ koleksi, data }], hapus: [{ koleksi, id }] }] — satu kelompok = satu kesatuan yang tidak boleh terbelah (mis. baris pengganti + asal yang ditandai).
 * cariLama(koleksi, id) → dokumen lama di cache (untuk menilai update/hapus). Kembali { potongan: [{ dokumen, hapus, get }] } atau { tolak }.
 */
export function kpPotong(kelompok, cariLama, kini, opsi) {
  // opsi = { sampai, pintu } (tutup buku v7): biaya jalur pintu tutup buku ikut dihitung — tanpa opsi = seperti dulu (1 per tulisan bulan lampau)
  const o = opsi || {}; const potongan = []; let kini_ = { dokumen: [], hapus: [], get: 0 };
  for (let i = 0; i < (kelompok || []).length; i++) {
    const k = kelompok[i]; const ops = (k.dokumen || []).map((x) => ({ koleksi: x.koleksi, data: x.data, lama: cariLama(x.koleksi, x.data.id) })).concat((k.hapus || []).map((x) => ({ koleksi: x.koleksi, id: x.id, lama: cariLama(x.koleksi, x.id), hapus: true })));
    const g = kpNilaiKiriman(ops, o.sampai || null, kini, o.pintu || null).perluGet;
    if (g > KP_BATAS_GET) return { tolak: 'Satu bagian kiriman ini sendiri menyentuh ' + g + ' catatan bulan lampau (batas ' + KP_BATAS_GET + ' sekali kirim) — tidak bisa dipecah lebih kecil' };
    if (kini_.get + g > KP_BATAS_GET && (kini_.dokumen.length || kini_.hapus.length)) { potongan.push(kini_); kini_ = { dokumen: [], hapus: [], get: 0 }; }
    kini_.dokumen = kini_.dokumen.concat(k.dokumen || []); kini_.hapus = kini_.hapus.concat(k.hapus || []); kini_.get += g;
  }
  if (kini_.dokumen.length || kini_.hapus.length) potongan.push(kini_);
  return { potongan };
}
