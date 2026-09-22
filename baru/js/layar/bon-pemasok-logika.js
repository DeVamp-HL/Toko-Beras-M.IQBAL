// LAYAR HARGA & PEMASOK — H2 BON PEMASOK (dikunci owner 18 Sep 2026: gabungan Tusukan Bon · Garis Jatuh Tempo · Buku Bon). Logika tanpa DOM, awalan bp.
// Angka bon dari MESIN BEKU hitungUtangPemasok: sisa = nilai − Σ bayar, bon yang dibayar sebagian TETAP di daftar (memori sisa-bon-dianggap-lunas).
// Satu pembayaran = satu bon (bonId), tidak boleh melebihi sisa bon itu; bon tertua cuma SARAN (RODA MAS tertua dulu, SEJATI terbaru dulu — owner yang memilih).
// Dokumen = simpanBayarBon / simpanSaldoAwalUtang index.html: utangPemasokMutasi {id, tanggal, jam, tipe 'bayar', pemasok, nominal, catatan, bonId, bonTanggal}
// (+ kolom baru sistem baru: dari = laci/brankas/rekening, biayaAdmin, adminNama) dan {tipe 'saldoAwal', pemasok, nominal, catatan, bonTanggal} untuk bon lama.
// Biaya admin transfer = BIAYA TOKO → dokumen pengeluaranHarian {kategori 'toko'} dalam batch yang sama (laba berkurang segitu; bayar bonnya sendiri tidak menyentuh laba).
// Tempo tidak tertulis di dokumen mana pun (memori tempo-bon-pemasok): tempo = isian owner di KARTU pemasok (pemasokCatatan.tempo); tanpa tempo kartu dipakai tempo umum
// aturanToko/catatStok.tempoHari (yang dipakai Menu & Pengingat sejak putaran 14) — dan disebut sumbernya; tanpa keduanya jatuh tempo TIDAK diramal.
// Uang toko: sistem lama tidak punya saldo per kantong, yang bisa dijaga TOTAL kas (kasPada; null bila titik kas belum disetel) — "dari mana uangnya" dicatat sebagai kolom.
import { hitungUtangPemasok, kasPada } from '../mesin/beku.js';
import { batchDiutang, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilUtangPemasokMutasi, ambilPemasokCatatan, ambilPengeluaranHarian, cacheMentah } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const ATUR_BON_BAWAAN = { dekatHari: 7, admin: [{ nama: 'BI-FAST', n: 2500 }, { nama: 'Transfer antarbank', n: 6500 }] };
export const TEMPAT_UANG = [['laci', 'Laci'], ['brankas', 'Brankas'], ['rekening', 'Rekening']];
export const TAB_BON = [['tusuk', 'Tusukan bon'], ['garis', 'Jatuh tempo'], ['buku', 'Buku bon']];
export const TEMPO_PILIHAN = [0, 7, 14, 21, 30];
const bpAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const bpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const bpHariKe = (iso) => Math.round(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10)) / 86400000);
export const bpTambahHari = (iso, n) => new Date((bpHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
export const pemasokSungguhan = (nama) => { const n = String(nama || '').trim(); return n !== '' && n !== 'STOK AWAL' && !n.startsWith('TUTUP BUKU'); };
const namaTempat = (id) => (TEMPAT_UANG.find((t) => t[0] === id) || [id, id])[1];

export function aturBon() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'bonPemasok') || null;
  const dekat = a && isFinite(Number(a.dekatHari)) && Number(a.dekatHari) >= 0 && Number(a.dekatHari) <= 60 ? Number(a.dekatHari) : ATUR_BON_BAWAAN.dekatHari;
  const admin = a && Array.isArray(a.admin) ? a.admin.filter((x) => x && String(x.nama || '').trim()).map((x) => ({ nama: String(x.nama).trim(), n: Math.max(0, Math.round(Number(x.n) || 0)) })) : ATUR_BON_BAWAAN.admin.map((x) => Object.assign({}, x));
  return { dekatHari: dekat, admin, dariOwner: !!a };
}
export function susunAturBon(isi, w) {
  const kini = aturBon(); let dekat = kini.dekatHari; if (!bpKosong(isi.dekatHari)) { dekat = Math.round(bpAngka(isi.dekatHari)); if (!(dekat >= 0 && dekat <= 60)) return { tolak: 'Bon dianggap dekat: 0–60 hari' }; }
  const admin = []; for (const x of (isi.admin || [])) { const nm = String(x.nama || '').trim(); const n = Math.round(bpAngka(x.n)); if (!nm && !(n > 0)) continue; if (!nm) return { tolak: 'Biaya admin ' + RP(n) + ' belum diberi nama' }; if (!(n >= 0)) return { tolak: 'Biaya admin ' + nm + ' tidak boleh minus' }; admin.push({ nama: nm.slice(0, 40), n }); }
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'bonPemasok', tanggal: w.tanggal, jam: w.jam, dekatHari: dekat, admin } }], patch: { aturB: null, kabar: 'Aturan bon pemasok disimpan — dekat = ' + dekat + ' hari · ' + (admin.length ? admin.map((x) => x.nama + ' ' + RP(x.n)).join(', ') : 'tanpa pilihan biaya admin'), kabarAwas: false } };
}
/** Tempo umum = aturanToko/catatStok.tempoHari (angka owner di Stok → Barang masuk → Atur); bawaannya 21 hari = angka yang sama dengan lembar Atur itu
 *  (ATUR_CATAT bawaan; median bon RODA MAS yang terukur — memori tempo-bon-pemasok). Dipakai Menu & Pengingat sejak putaran 14, jadi tidak boleh berbeda di sini. */
export const TEMPO_UMUM_BAWAAN = 21;
export function tempoUmum() { const d = cacheMentah('aturan').find((x) => String(x.id) === 'catatStok'); const n = d ? Number(d.tempoHari) : NaN; return { hari: isFinite(n) && n > 0 ? n : TEMPO_UMUM_BAWAAN, dariOwner: isFinite(n) && n > 0 }; }

/** Semua pemasok yang pernah ada: kedatangan nyata + bon lama + kartu. Kartu = pemasokCatatan {id = kunci, nama, kontak, catatan} + kolom baru orang, tempo. */
export function daftarPemasok() {
  const peta = {}; const kartu = {}; ambilPemasokCatatan().forEach((c) => { kartu[String(c.id)] = c; });
  const pastikan = (nama) => { const nm = String(nama || '').trim(); if (!pemasokSungguhan(nm)) return null; const k = kunciPelanggan(nm); if (!peta[k]) peta[k] = { kunci: k, nama: nm, urutNama: 0, kedatangan: 0, belanja: 0, totalKg: 0, terakhir: '', hargaPerMerk: {}, batch: [], cara: [] }; return peta[k]; };
  ambilSemuaBatch().forEach((b) => { const s = pastikan(b.pemasok); if (!s || b.stokAwal) return; if ((Number(b.id) || 0) >= s.urutNama) { s.nama = String(b.pemasok).trim(); s.urutNama = Number(b.id) || 0; }
    const nilai = (b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0); s.kedatangan += 1; s.belanja += nilai; if ((b.tanggal || '') > s.terakhir) s.terakhir = b.tanggal || '';
    s.batch.push({ id: b.id, tanggal: b.tanggal || '', jam: b.jam || '', nMerk: (b.merkList || []).length, nilai, utang: batchDiutang(b), kg: (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0) }); s.cara.push({ tanggal: b.tanggal || '', id: Number(b.id) || 0, utang: batchDiutang(b) });
    (b.merkList || []).forEach((m) => { if (!m.merk || !(Number(m.hargaPerKg) > 0)) return; s.totalKg += Number(m.totalKg) || 0; const h = s.hargaPerMerk[m.merk] = s.hargaPerMerk[m.merk] || { riwayat: [] }; h.riwayat.push({ tanggal: b.tanggal || '', id: Number(b.id) || 0, hargaPerKg: Number(m.hargaPerKg), kg: Number(m.totalKg) || 0 }); }); });
  ambilUtangPemasokMutasi().forEach((m) => { const s = pastikan(m.pemasok); if (s && !s.urutNama) s.nama = String(m.pemasok).trim(); });
  Object.values(kartu).forEach((c) => { const s = pastikan(c.nama || c.id); if (s && !s.urutNama && c.nama) s.nama = String(c.nama).trim(); });
  return Object.keys(peta).map((k) => { const s = peta[k]; Object.keys(s.hargaPerMerk).forEach((m) => { const h = s.hargaPerMerk[m]; h.riwayat.sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || b.id - a.id); h.terakhir = h.riwayat[0]; });
    s.batch.sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || (Number(b.id) || 0) - (Number(a.id) || 0)); s.cara.sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || b.id - a.id);
    const tiga = s.cara.slice(0, 3); const nBon = tiga.filter((x) => x.utang).length; s.caraBiasa = !tiga.length ? '' : nBon * 2 > tiga.length ? 'bon' : 'tunai'; s.caraTeks = !tiga.length ? 'belum pernah ada kedatangan' : (s.caraBiasa === 'bon' ? 'biasanya BON' : 'biasanya TUNAI') + ' (' + nBon + ' dari ' + tiga.length + ' kedatangan terakhir bon)';
    const c = kartu[k] || {}; s.kontak = String(c.kontak || '').trim(); s.catatan = String(c.catatan || '').trim(); s.orang = String(c.orang || '').trim(); s.tempo = isFinite(Number(c.tempo)) && Number(c.tempo) > 0 ? Math.round(Number(c.tempo)) : 0; s.adaKartu = !!kartu[k];
    delete s.cara; return s; }).sort((a, b) => String(b.terakhir).localeCompare(String(a.terakhir)) || a.nama.localeCompare(b.nama));
}
export const cariPemasok = (nama) => daftarPemasok().find((p) => p.kunci === kunciPelanggan(nama)) || null;
/** Tempo yang dipakai untuk meramal jatuh tempo bon pemasok ini, berikut SUMBERNYA. hari 0 = tidak diramal. */
export function tempoPemasok(nama) {
  const p = cariPemasok(nama); if (p && p.tempo > 0) return { hari: p.tempo, sumber: 'kartu', teks: 'tempo ' + p.tempo + ' hari (kartu pemasok)' };
  const u = tempoUmum(); if (u.hari > 0) return { hari: u.hari, sumber: 'umum', teks: 'tempo umum ' + u.hari + ' hari' + (u.dariOwner ? ' (Atur Barang masuk)' : ' (bawaan — ubah di Atur Barang masuk atau di kartu pemasok)') };
  return { hari: 0, sumber: '', teks: 'tempo belum disepakati — jatuh tempo tidak diramal' };
}
export const nomorWa = (kontak) => { const d = String(kontak || '').replace(/\D/g, ''); if (!d) return ''; return d.startsWith('0') ? '62' + d.slice(1) : d.startsWith('62') ? d : d; };

/** Semua bon terbuka (mesin beku) + tempo, status, urutan tusukan & garis jatuh tempo. */
export function susunBon(kini) {
  const iso = hariIniIso(kini || new Date()); const atur = aturBon(); const kas = kasPada(); const up = hitungUtangPemasok();
  const bon = []; up.forEach((px) => { const T = tempoPemasok(px.pemasok); (px.bon || []).forEach((b) => { const jatuh = T.hari > 0 && b.tanggal ? bpTambahHari(b.tanggal, T.hari) : ''; const sisaHari = jatuh ? bpHariKe(jatuh) - bpHariKe(iso) : null;
    bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0), umur: b.umurHari, jenis: b.jenis, catatan: b.catatan || '', jatuh, sisaHari, tempo: T,
      status: !jatuh ? 'tanpaTempo' : sisaHari < 0 ? 'lewat' : sisaHari <= atur.dekatHari ? 'dekat' : 'jauh' }); }); });
  bon.forEach((b) => { b.tempoTeks = b.status === 'tanpaTempo' ? 'tempo belum disepakati' : b.status === 'lewat' ? 'LEWAT ' + (-b.sisaHari) + ' hari (jatuh tempo ' + tanggalPendek(b.jatuh) + ')' : b.sisaHari === 0 ? 'jatuh tempo HARI INI' : 'jatuh tempo ' + tanggalPendek(b.jatuh) + ' · ' + b.sisaHari + ' hari lagi';
    b.ket = (b.umur === null || b.umur === undefined ? 'umur tidak diketahui' : 'umur ' + b.umur + ' hari') + (b.dibayar > 0 ? ' · sudah dibayar ' + RP(b.dibayar) + ' dari ' + RP(b.nilai) : '') + (b.jenis === 'saldoAwal' ? ' · bon lama (sebelum sistem)' : '');
    b.cap = b.jenis === 'saldoAwal' ? 'bon lama' : b.dibayar > 0 ? 'sebagian' : ''; b.isi = b.jenis === 'saldoAwal' ? (b.catatan || 'bon lama sebelum sistem') : bpIsiBatch(b.id); });
  const urutTua = (a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || (Number(a.id) || 0) - (Number(b.id) || 0);
  const total = bon.reduce((a, b) => a + b.sisa, 0); const tekor = up.reduce((a, x) => a + (x.tekor || 0), 0);
  const tusukan = up.map((px) => { const d = bon.filter((b) => b.pemasok === px.pemasok).sort(urutTua); const T = tempoPemasok(px.pemasok); return { pemasok: px.pemasok, tempo: T, tekor: px.tekor || 0, total: d.reduce((a, b) => a + b.sisa, 0), bon: d.map((b, i) => Object.assign({}, b, { saran: i === 0 && d.length > 1 })) }; }).filter((t) => t.bon.length || t.tekor > 0);
  const berTempo = bon.filter((b) => b.jatuh).sort((a, b) => a.jatuh.localeCompare(b.jatuh) || urutTua(a, b)), tanpaTempo = bon.filter((b) => !b.jatuh).sort(urutTua);
  const garis = []; let jalan = 0, kiniSudah = false, habisSudah = false; const tanda = (teks, kelas) => garis.push({ tanda: true, teks, kelas });
  berTempo.forEach((b) => { if (!kiniSudah && b.sisaHari >= 0) { tanda('hari ini · ' + tanggalPendek(iso), 'kini'); kiniSudah = true; }
    if (kas !== null && !habisSudah && jalan + b.sisa > kas) { tanda('uang toko ' + RP(kas) + ' habis di sini — bon berikut kurang ' + RP(jalan + b.sisa - kas), 'habis'); habisSudah = true; } jalan += b.sisa; garis.push(Object.assign({ tanda: false }, b)); });
  if (!kiniSudah && berTempo.length) tanda('hari ini · ' + tanggalPendek(iso), 'kini');
  if (tanpaTempo.length) { tanda('tempo belum disepakati — tidak diramal. Isi di kartu pemasoknya.', ''); tanpaTempo.forEach((b) => garis.push(Object.assign({ tanda: false }, b))); }
  const lewat = berTempo.filter((b) => b.status === 'lewat'), dekat = berTempo.filter((b) => b.status === 'dekat'); const jml = (d) => d.reduce((a, b) => a + b.sisa, 0);
  return { bon, total, nBon: bon.length, nPemasok: tusukan.filter((t) => t.bon.length).length, kas, adaKas: kas !== null, tekor, tusukan, garis, lewat, dekat, tanpaTempo, atur, iso,
    kasTeks: kas === null ? 'uang toko belum bisa dihitung — titik kas belum disetel di perangkat ini (Tutup Hari sistem lama)' : 'uang toko sekarang ' + RP(kas) + ' (semua kantong, dari titik kas + gerakan sesudahnya)',
    ringkas: [{ a: String(lewat.length), l: 'lewat tempo', nyala: lewat.length > 0 }, { a: RP(jml(lewat) + jml(dekat)), l: 'jatuh ≤ ' + atur.dekatHari + ' hari', nyala: false }, { a: String(tanpaTempo.length), l: 'tanpa tempo', nyala: false }],
    cukupTeks: !berTempo.length ? 'Belum ada bon yang bisa diramal jatuh temponya.' : kas === null ? 'Uang toko belum bisa dihitung, jadi belum bisa dibandingkan dengan bon yang jatuh tempo.' : habisSudah ? 'Uang toko TIDAK cukup untuk semua bon yang sudah punya tempo.' : 'Uang toko cukup untuk semua bon yang sudah punya tempo.', kurang: habisSudah };
}
function bpIsiBatch(id) { const b = ambilSemuaBatch().find((x) => String(x.id) === String(id)); if (!b) return ''; const ml = b.merkList || []; const kg = ml.reduce((a, m) => a + (Number(m.totalKg) || 0), 0); return ml.map((m) => m.merk).filter(Boolean).slice(0, 4).join(', ') + (ml.length > 4 ? ' …' : '') + (kg ? ' · ' + Math.round(kg).toLocaleString('id-ID') + ' kg' : ''); }

/** Buku bon per pemasok: barang datang lewat bon (+), bon lama (+), bayar (−), utang jadi berapa (saldo berjalan). */
export function bukuBon(nama) {
  const k = kunciPelanggan(nama); const kej = [];
  ambilSemuaBatch().forEach((b) => { if (b.stokAwal || !batchDiutang(b) || kunciPelanggan(b.pemasok) !== k) return; kej.push({ t: b.tanggal || '', j: b.jam || '', u: 0, teks: 'Barang datang — bon', ket: bpIsiBatch(b.id), n: Math.round((b.merkList || []).reduce((a, m) => a + (Number(m.subtotalHarga) || 0), 0)) }); });
  ambilUtangPemasokMutasi().forEach((m) => { if (kunciPelanggan(m.pemasok) !== k) return;
    if (m.tipe === 'saldoAwal') kej.push({ t: m.bonTanggal || '', j: '', u: 0, teks: 'Bon lama (sebelum sistem)', ket: m.catatan || (m.bonTanggal ? '' : 'tanggal bon tidak diketahui'), n: Math.round(Number(m.nominal) || 0) });
    else if (m.tipe === 'bayar') kej.push({ t: m.tanggal || '', j: m.jam || '', u: 1, teks: 'Bayar bon' + (m.bonTanggal ? ' ' + tanggalPendek(m.bonTanggal) : ''), ket: (m.dari ? 'dari ' + namaTempat(m.dari) : '') + (Number(m.biayaAdmin) > 0 ? ' · admin ' + RP(m.biayaAdmin) : '') + (m.catatan ? ' · ' + m.catatan : ''), n: -Math.round(Number(m.nominal) || 0), id: m.id }); });
  kej.sort((a, b) => a.t.localeCompare(b.t) || a.u - b.u || a.j.localeCompare(b.j)); let sd = 0;
  const baris = kej.map((e) => { sd += e.n; return Object.assign({}, e, { saldo: sd }); });
  return { baris, saldo: sd };
}

// ---- LEMBAR BAYAR: satu pembayaran = satu bon; uang dari mana; biaya admin (rekening) = biaya toko
export function hitungBayar(d, kini) {
  const D = Object.assign({ pemasok: '', bonId: '', ketik: '', dari: '', adminI: -1, catatan: '' }, d || {}); const B = susunBon(kini); const atur = B.atur;
  const bonP = B.bon.filter((b) => b.pemasok === D.pemasok).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal))); const bon = bonP.find((b) => b.id === String(D.bonId)) || null;
  const n = Math.round(bpAngka(D.ketik)); const biaya = D.dari === 'rekening' && D.adminI >= 0 ? atur.admin[D.adminI] || null : null; const admin = biaya ? biaya.n : 0;
  let tolak = ''; if (!bon) tolak = 'Pilih bon yang dibayar'; else if (!(n > 0)) tolak = 'Ketik jumlah yang dibayar'; else if (n > bon.sisa) tolak = 'Melebihi sisa bon ini (' + RP(bon.sisa) + ') — satu pembayaran satu bon, bon lain dicatat terpisah supaya jejaknya jelas';
  else if (!D.dari) tolak = 'Uangnya dari mana?'; else if (B.adaKas && n + admin > B.kas) tolak = 'Uang toko cuma ' + RP(B.kas) + ' — tidak cukup' + (admin ? ' (termasuk biaya admin ' + RP(admin) + ')' : '');
  const lunas = !!bon && n === bon.sisa;
  return { D, B, bonP, bon, n, admin, biaya, tolak, lunas, arti: bon && n > 0 && n <= bon.sisa ? { a: lunas ? 'Bon ' + tanggalPendek(bon.tanggal) + ' LUNAS — keluar dari daftar' : 'Dibayar SEBAGIAN — sisa bon jadi ' + RP(bon.sisa - n) + ', bonnya TETAP di daftar', b: (D.dari ? namaTempat(D.dari) : 'uang toko') + ' berkurang ' + RP(n + admin) + (admin ? ' (termasuk admin ' + RP(admin) + ')' : ''), c: 'laba TIDAK berubah — berasnya sudah dihitung waktu datang' + (admin ? ' · biaya admin ' + RP(admin) + ' masuk biaya toko, laba berkurang segitu' : '') } : null,
    label: tolak || (lunas ? 'BAYAR LUNAS ' + RP(n) : 'BAYAR SEBAGIAN ' + RP(n)) };
}
export function susunBayar(d, w) {
  const H = hitungBayar(d, new Date(w.kini)); if (H.tolak) return { tolak: H.tolak };
  const id = w.idUnik(); const catatan = String(H.D.catatan || '').trim().slice(0, 80);
  const bayar = { id, tanggal: w.tanggal, jam: w.jam, tipe: 'bayar', pemasok: H.bon.pemasok, nominal: H.n, catatan, bonId: H.bon.id, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };
  if (H.admin > 0) { bayar.biayaAdmin = H.admin; bayar.adminNama = H.biaya.nama; }
  const dokumen = [{ koleksi: 'utangPemasokMutasi', data: bayar }];
  if (H.admin > 0) dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama + ' — bayar bon ' + H.bon.pemasok + (H.bon.tanggal ? ' ' + tanggalPendek(H.bon.tanggal) : ''), nominal: H.admin, dariBayarBon: id } });
  return { dokumen, bayarId: id, patch: { bayar: null, urung: { id, sampai: Date.now() + 90000, teks: 'Batalkan pembayaran ' + RP(H.n) + ' tadi' }, kabar: 'Bon ' + tanggalPendek(H.bon.tanggal) + ' ' + H.bon.pemasok + (H.lunas ? ' LUNAS' : ' dibayar sebagian, sisa ' + RP(H.bon.sisa - H.n)) + ' · ' + namaTempat(H.D.dari) + ' berkurang ' + RP(H.n + H.admin) + (H.admin ? ' (admin ' + RP(H.admin) + ' jadi biaya toko)' : ''), kabarAwas: false } };
}
/** Batalkan pembayaran barusan (≤ 90 detik): hapus dokumen bayar + dokumen biaya adminnya. */
export function susunUrungBayar(id) {
  const m = ambilUtangPemasokMutasi().find((x) => String(x.id) === String(id) && x.tipe === 'bayar'); if (!m) return { tolak: 'Pembayaran itu sudah tidak ada' };
  const hapus = [{ koleksi: 'utangPemasokMutasi', id: m.id }]; ambilPengeluaranHarian().forEach((h) => { if (String(h.dariBayarBon || '') === String(id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });
  return { hapus, patch: { urung: null, kabar: 'Pembayaran ' + RP(m.nominal || 0) + ' dibatalkan — bon ' + m.pemasok + ' dan ' + namaTempat(m.dari || 'laci') + ' kembali seperti semula' + (hapus.length > 1 ? ' (biaya adminnya ikut dicabut)' : ''), kabarAwas: false } };
}
// ---- LEMBAR BON LAMA (sebelum sistem): utang bertambah; uang, stok, laba TIDAK berubah
export function hitungBonLama(d) {
  const D = Object.assign({ pemasok: '', nama: '', tgl: '', ketik: '', catatan: '' }, d || {}); const n = Math.round(bpAngka(D.ketik)); const namaBaru = String(D.nama || '').trim();
  const kembar = namaBaru ? daftarPemasok().find((p) => p.kunci === kunciPelanggan(namaBaru)) : null; const pemasok = D.pemasok || (kembar ? kembar.nama : namaBaru);
  let tolak = ''; if (!pemasok) tolak = 'Pilih atau ketik nama pemasoknya'; else if (!(n > 0)) tolak = 'Ketik nilai bonnya'; else if (D.tgl && !/^\d{4}-\d{2}-\d{2}$/.test(D.tgl)) tolak = 'Tanggal bon tidak terbaca';
  return { D, n, pemasok, kembar: kembar && !D.pemasok ? kembar.nama : '', tolak, arti: n > 0 ? 'Utang ke ' + (pemasok || 'pemasok') + ' bertambah ' + RP(n) + ' · uang toko, stok, dan laba TIDAK berubah — ini utang dari masa sebelum sistem.' : '', label: tolak || 'CATAT BON LAMA ' + RP(n) };
}
export function susunBonLama(d, w) {
  const H = hitungBonLama(d); if (H.tolak) return { tolak: H.tolak };
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'saldoAwal', pemasok: H.pemasok.slice(0, 60), nominal: H.n, catatan: String(H.D.catatan || '').trim().slice(0, 120), bonTanggal: H.D.tgl || null };
  return { dokumen: [{ koleksi: 'utangPemasokMutasi', data }], patch: { lama: null, bukuNama: H.pemasok, kabar: 'Bon lama ' + RP(H.n) + ' ' + H.pemasok + ' dicatat' + (H.D.tgl ? ' (tanggal bon ' + tanggalPendek(H.D.tgl) + ')' : ' (tanggal bon tidak diketahui — dihitung paling tua)') + ' — uang toko, stok, dan laba tidak berubah', kabarAwas: false } };
}
// ---- KARTU PEMASOK: orang, kontak, tempo, catatan = isian owner (dokumen pemasokCatatan sistem lama + kolom baru orang & tempo)
export function susunKartu(nama, isi, w) {
  const nm = String(nama || '').trim(); if (!pemasokSungguhan(nm)) return { tolak: 'Nama pemasok kosong' }; const p = cariPemasok(nm);
  const tempo = bpKosong(isi.tempo) ? 0 : Math.round(bpAngka(isi.tempo)); if (!(tempo >= 0 && tempo <= 120)) return { tolak: 'Tempo bon: 0–120 hari (0 = belum disepakati)' };
  const data = { id: kunciPelanggan(nm), nama: p ? p.nama : nm, kontak: String(isi.kontak || '').trim().slice(0, 30), catatan: String(isi.catatan || '').trim().slice(0, 160), orang: String(isi.orang || '').trim().slice(0, 40), tempo, diubahPada: w.kini };
  return { dokumen: [{ koleksi: 'pemasokCatatan', data }], patch: { kartu: null, kabar: 'Kartu ' + data.nama + ' tersimpan — ' + (tempo > 0 ? 'tiap bonnya diramal jatuh tempo ' + tempo + ' hari sesudah barang datang' : 'tempo kartu kosong, dipakai tempo umum ' + tempoUmum().hari + ' hari'), kabarAwas: false } };
}
