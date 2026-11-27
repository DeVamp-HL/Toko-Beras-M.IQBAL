// Panel ARSIP, AUDIT & BAGIKAN di Menu › Toko ini (paket P8, owner 27 Nov 2026 — sensus A94 B13 B81 B103). Hanya menggambar & meneruskan ketukan; angka & dokumen dari
// arsip-foto-logika (af), omzet-perangkat-logika (orp), jejak-cari-logika (jc), dasbor-publik-logika (dpb). Yang DIBACA dari server (log hari lain, foto satu bulan) dibaca
// sekali saat diketuk lewat opsi.bacaLog / opsi.bacaFotoBulan (firebase.js; owner saja); mode cadangan = memakai yang ada di memori (disebut SIMULASI).
//   · Perangkat & antrean › Perangkat: kartu Omzet per perangkat (B13).
//   · Perangkat & antrean › Jejak pencatat: Cari log hari lain + riwayat satu catatan (B81).
//   · Cadangan & simpanan › Arsip foto: belum berfoto 30 hari, per bulan, Unduh arsip foto bulan itu (A94).
//   · Cadangan & simpanan › Tautan Dasbor: buat tautan beku (centang bagian, 1/7/30/90 hari), daftar, salin / WhatsApp, cabut (B103). Owner saja.
import { h } from '../inti/dom.js';
import { RP, ANGKA, tanggalPendek, hariIniIso } from '../inti/format.js';
import { sumberData, cacheMentah } from '../data/toko.js';
import * as AF from './arsip-foto-logika.js';
import * as ORP from './omzet-perangkat-logika.js';
import * as JC from './jejak-cari-logika.js';
import * as DPB from './dasbor-publik-logika.js';

export const AA_DRAF_KOSONG = () => ({ orp: 'bulan', jcTanggal: '', jcSaring: { oleh: '', koleksi: '', kata: '' }, jcHasil: null, jcMuat: '', jcPesan: '', jcCatatan: null,
  afMuat: '', dpbBagian: DPB.dpbBagianBawaan(), dpbHari: DPB.DPB_HARI_BAWAAN, dpbUntuk: '', dpbBaru: null, dpbYakin: null });
const aaOwner = (akun) => !!akun && akun.jenis === 'owner';
const aaServer = () => sumberData().jenis === 'firestore';

/** Kartu Omzet per perangkat (B13) — tab Perangkat. */
export function kartuOmzetPerangkat(s, d) {
  let R; try { R = ORP.orpRingkas(d, (s.aa || {}).orp); } catch (e) { return h`<div class="kartu" data-k="orp"><div class="label">Omzet per perangkat</div><div class="ket awas-teks">Gagal dihitung: ${String((e && e.message) || e)}</div></div>`; }
  const maks = Math.max(1, ...R.baris.map((b) => b.omzet));
  return h`<div class="kartu" data-k="orp" style="gap: 6px;"><div class="label">Omzet per perangkat · ${R.nama}</div>
    <div class="hg-pil" data-k="orp-pil">${R.pilihan.map(([id, nm]) => h`<div class="seg ${R.pilih === id ? 'aktif' : ''}" data-aksi="aaOrp" data-p="${id}">${nm}</div>`)}</div>
    <div class="k2" data-k="orp-kalimat">${R.kalimat} · total ${RP(R.total)}</div>
    ${R.baris.map((b, i) => h`<div class="aa-orp" data-k="orp-${i}"><div class="aa-orp-atas"><span><b>${b.label}</b> <span class="k2">${b.jenisNama}${b.aplikasi ? ' · ' + b.aplikasi : ''}</span></span><span>${RP(b.omzet)} · ${ANGKA(b.nota)} nota</span></div>
      <div class="aa-batang"><i style="width: ${Math.round(b.omzet / maks * 100)}%;"></i></div></div>`)}
    ${R.perJenis.length > 1 ? h`<div class="k2" data-k="orp-jenis">Per jenis (tebakan): ${R.perJenis.map((j) => j.nama + ' ' + RP(j.omzet)).join(' · ')}</div>` : ''}
    <div class="ket" style="font-size: 10.5px;">${R.catatan} Sumber: ${R.sumber}.</div></div>`;
}
/** Kartu Cari log hari lain & riwayat satu catatan (B81) — tab Jejak pencatat. nama = penamaan jenis catatan (ssNamaKoleksi). */
export function kartuCariLog(s, d, akun, nama) {
  if (!aaOwner(akun)) return '';
  const A = s.aa || AA_DRAF_KOSONG(); const H = A.jcHasil; const J = H ? JC.jcSaring(H.daftar, A.jcSaring, nama) : null; const S = A.jcSaring || {};
  return h`<div class="kartu" data-k="jc" style="gap: 6px;"><div class="label">Cari log hari lain</div>
    <div class="k2">Yang tampil di atas cuma ${150} tulisan terbaru. Pilih tanggal → log hari itu dibaca SEKALI dari server (± 190 tulisan sehari = ± 190 baca, masih di jatah gratis harian).</div>
    <div style="display: flex; gap: 6px; flex-wrap: wrap;"><input class="ketik-nama sempit" type="date" value="${A.jcTanggal || hariIniIso(d)}" max="${hariIniIso(d)}" data-ketik="aaJcTanggal"><div class="kaca-btn aktif" data-aksi="aaJcBaca" data-k="jc-baca">${A.jcMuat === 'muat' ? 'Membaca…' : 'Baca log tanggal ini'}</div></div>
    ${A.jcPesan ? h`<div class="pita-info ${A.jcMuat === 'galat' ? 'awas' : ''}" data-k="jc-pesan">${A.jcPesan}</div>` : ''}
    ${J ? h`<div data-k="jc-hasil" style="display: flex; flex-direction: column; gap: 4px;"><div class="label">${H.judul} · ${J.kalimat}</div>
      <div class="hg-pil" data-k="jc-orang"><div class="seg ${!S.oleh ? 'aktif' : ''}" data-aksi="aaJcSaring" data-kolom="oleh" data-nilai="">semua orang</div>${J.perOrang.map((o) => h`<div class="seg ${S.oleh === o.nama ? 'aktif' : ''}" data-aksi="aaJcSaring" data-kolom="oleh" data-nilai="${o.nama}">${o.nama} · ${o.n}</div>`)}</div>
      <div class="hg-pil" data-k="jc-jenis"><div class="seg ${!S.koleksi ? 'aktif' : ''}" data-aksi="aaJcSaring" data-kolom="koleksi" data-nilai="">semua catatan</div>${J.perJenis.map((x) => h`<div class="seg ${S.koleksi === x.id ? 'aktif' : ''}" data-aksi="aaJcSaring" data-kolom="koleksi" data-nilai="${x.id}">${x.nama} · ${x.n}</div>`)}</div>
      <input class="ketik-nama" type="text" placeholder="cari kata / id catatan (mis. nama pelanggan, 1764…)" value="${S.kata || ''}" data-ketik="aaJcKata">
      ${J.tampil.map((l) => h`<div class="pr-jejak" data-k="jc-${l.id}"><span class="j">${l.tanggal === hariIniIso(d) ? l.jam : tanggalPendek(l.tanggal) + ' ' + l.jam}</span><span>${l.teks}<div class="k2">${l.oleh} · ${l.perangkat}${l.idDok ? ' · id ' + l.idDok : ''}</div></span>${l.idDok ? h`<span class="pr-cap ok" data-aksi="aaJcCatatan" data-id="${l.idDok}" title="semua log catatan ini">riwayat ›</span>` : h`<span></span>`}</div>`)}
      ${J.lebih ? h`<div class="ket">… ${J.lebih} tulisan lagi — persempit saringannya.</div>` : ''}</div>` : ''}</div>`;
}
/** Arsip foto (A94) — Cadangan & simpanan › Arsip foto. */
export function gambarArsipFoto(s, d, akun) {
  const A = s.aa || AA_DRAF_KOSONG(); let B, BL; try { B = AF.afBelum(d); BL = AF.afBulan(d); } catch (e) { return h`<div class="kartu awas" data-k="af"><div class="ket">Arsip foto gagal dihitung: ${String((e && e.message) || e)}</div></div>`; }
  return h`<div class="kartu ${B.n ? 'awas' : ''}" data-k="af-belum" style="gap: 4px;"><div class="label">Belum berfoto · ${B.hari} hari terakhir</div><div style="font-weight: 600;">${B.kalimat}</div>
      ${B.belum.slice(0, 12).map((x) => h`<div class="cd-baris" data-k="af-k-${x.id}"><div><div>${tanggalPendek(x.tanggal)} · ${x.pemasok} · ${x.jenis === 'tunai' ? 'TUNAI' : 'bon'}</div><div class="k2">${RP(x.nilai)}</div></div><div class="kaca-btn kecil" data-aksi="aaFotoKedatangan" data-id="${x.id}">foto ›</div></div>`)}
      ${B.belum.length > 12 ? h`<div class="k2">… ${B.belum.length - 12} kedatangan lagi</div>` : ''}
      ${B.kas.length ? h`<div class="k2" data-k="af-kas">${B.kas.length} nota kas kecil bertanda "nota ada" belum difoto — foto dari Uang › Uang keluar.</div>` : ''}
      ${B.catatanLama ? h`<div class="pita-info" data-k="af-lama">${B.catatanLama}</div>` : ''}</div>
    <div class="kartu" data-k="af-bulan" style="gap: 4px;"><div class="label">Arsip foto per bulan</div>
      <div class="k2">Foto nota & bon TIDAK ikut cadangan berkas (± 300 KB per foto). Arsipnya diunduh terpisah: satu berkas per bulan yang bisa dibuka tanpa internet & dicetak. Foto dibaca dari server saat tombolnya diketuk.</div>
      ${BL.map((b) => h`<div class="cd-baris" data-k="af-b-${b.key}"><div><div style="font-weight: 600;">${b.nama}</div><div class="k2">${b.foto} foto bertanda${b.kb ? ' · ± ' + ANGKA(b.kb) + ' KB' : ''} · ${b.berfoto} dari ${b.kedatangan} kedatangan berfoto${b.perJenis.length ? ' · ' + b.perJenis.map((j) => AF.afNamaJenis(j.jenis) + ' ' + j.n).join(', ') : ''}</div></div>
        ${aaOwner(akun) ? h`<div class="kaca-btn kecil ${A.afMuat === b.key ? 'mati' : ''}" data-aksi="aaUnduhFoto" data-key="${b.key}">${A.afMuat === b.key ? 'membaca…' : 'unduh'}</div>` : ''}</div>`)}
      <div class="ket" style="font-size: 10.5px;">${AF.afPerkiraanUnduh(BL[0])}. Foto lama (sebelum 27 Nov 2026) ikut didaftarkan saat bulannya diunduh, supaya hitungan "belum berfoto" jujur.</div></div>`;
}
/** Tautan beku Dasbor (B103) — Cadangan & simpanan › Tautan Dasbor. Owner saja. */
export function gambarTautanDasbor(s, d, akun, dasar, proyek) {
  if (!aaOwner(akun)) return h`<div class="ket">Tautan Dasbor hanya untuk akun owner.</div>`;
  const A = s.aa || AA_DRAF_KOSONG(); const semua = DPB.dpbSemua(d); const aktif = semua.filter((x) => x.aktif); const lewat = semua.filter((x) => !x.aktif);
  let P = null; try { P = DPB.dpbPratinjau(A.dpbBagian, d); } catch (e) { P = { baris: [['Pratinjau', 'gagal dihitung: ' + String((e && e.message) || e)]] }; }
  const baru = A.dpbBaru ? semua.find((x) => x.kode === A.dpbBaru) : null;
  return h`<div class="kartu" data-k="dpb-buat" style="gap: 6px;"><div class="label">Buat tautan beku Dasbor</div>
      <div class="k2">Untuk pihak luar (bank, akuntan, partner): halaman TANPA login berisi angka yang DIBEKUKAN sekarang — tidak ikut berubah. Nama pelanggan, pemasok & staf tidak pernah ikut. Sesudah masa berlakunya lewat, server sendiri menolak tautan itu.</div>
      <div class="label">Bagian yang boleh terlihat</div>
      <div class="hg-pil" data-k="dpb-bagian">${DPB.DPB_BAGIAN.map(([id, nm]) => h`<div class="seg ${A.dpbBagian.indexOf(id) >= 0 ? 'aktif' : ''}" data-aksi="aaDpbBagian" data-id="${id}">${A.dpbBagian.indexOf(id) >= 0 ? '✓ ' : ''}${nm}</div>`)}</div>
      <div class="label">Berlaku</div>
      <div class="hg-pil" data-k="dpb-hari">${DPB.DPB_HARI.map((n) => h`<div class="seg ${Number(A.dpbHari) === n ? 'aktif' : ''}" data-aksi="aaDpbHari" data-n="${n}">${n} hari</div>`)}</div>
      <input class="ketik-nama" type="text" maxlength="${DPB.DPB_UNTUK_MAKS}" placeholder="untuk siapa (boleh kosong, mis. Bank) — ikut terlihat di halamannya" value="${A.dpbUntuk || ''}" data-ketik="aaDpbUntuk">
      <div class="kartu" data-k="dpb-pratinjau" style="gap: 2px; padding: 8px 10px;"><div class="label">Yang akan dibekukan (bulan ini + 3 bulan sebelumnya per bulan)</div>${(P.baris || []).map((r) => h`<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 2px 10px; font-size: 12px; padding: 2px 0;"><span>${r[0]}</span><span style="text-align: right;">${r[1]}</span></div>`)}</div>
      <div class="utama ${A.dpbYakin === 'buat' ? 'awas' : ''}" data-aksi="aaDpbBuat" data-k="dpb-tombol">${A.dpbYakin === 'buat' ? 'YAKIN — BUAT TAUTAN ' + A.dpbHari + ' HARI' : 'BUAT TAUTAN'}</div>
      ${A.dpbYakin === 'buat' ? h`<div class="pita-info awas" data-k="dpb-yakin">Siapa pun yang memegang tautan ini bisa melihat ${A.dpbBagian.map(DPB.dpbNamaBagian).join(', ').toLowerCase()} sampai ${DPB.dpbJamTeks(d.getTime() + Number(A.dpbHari) * 86400000)}. Ketuk sekali lagi untuk membuat.</div>` : ''}
      ${!aaServer() ? h`<div class="ket">SIMULASI (cadangan): tautan hanya dibuat di memori layar ini — halaman tamunya tidak bisa membukanya.</div>` : ''}</div>
    ${baru ? h`<div class="kartu emas" data-k="dpb-baru" style="gap: 6px;"><div class="label">Tautan baru${baru.untuk ? ' · untuk ' + baru.untuk : ''}</div><div class="k2" style="word-break: break-all;">${DPB.dpbTautan(baru.kode, dasar, proyek)}</div>
      <div class="pn-dua"><div class="kaca-btn aktif" data-aksi="aaDpbSalin" data-kode="${baru.kode}">salin tautan</div><div class="kaca-btn" data-aksi="aaDpbWa" data-kode="${baru.kode}">kirim WhatsApp</div></div></div>` : ''}
    <div class="kartu" data-k="dpb-daftar" style="gap: 4px;"><div class="label">Tautan aktif · ${aktif.length}</div>
      ${aktif.length ? aktif.map((x) => h`<div class="cd-baris" data-k="dpb-${x.kode}"><div><div style="font-weight: 600;">${x.untuk || 'tanpa catatan'} · sisa ${x.sisaHari} hari</div><div class="k2">sampai ${x.sampaiTeks} · ${x.bagian.join(', ')}</div></div>
        <div style="display: flex; gap: 4px;"><div class="kaca-btn kecil" data-aksi="aaDpbSalin" data-kode="${x.kode}">salin</div><div class="kaca-btn kecil ${A.dpbYakin === x.kode ? 'awas' : 'putus'}" data-aksi="aaDpbCabut" data-kode="${x.kode}">${A.dpbYakin === x.kode ? 'YAKIN cabut' : 'cabut'}</div></div></div>`) : h`<div class="k2">Belum ada tautan aktif.</div>`}
      ${lewat.length ? h`<div class="k2" data-k="dpb-lewat">${lewat.length} tautan sudah lewat (server sudah menolaknya).</div><div class="kaca-btn kecil putus" data-aksi="aaDpbBersih" style="align-self: flex-start;">hapus yang sudah lewat dari daftar</div>` : ''}</div>`;
}
const aaUnduh = (nama, teks, jenis) => { const blob = new Blob([teks], { type: jenis }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = nama; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(url), 4000); return blob.size; };
/** Cadangan berkas + log 30 hari (B81): dibaca dari server (owner) atau dari memori (cadangan / bukan owner — disebut). b = ssBerkasCadangan. */
export async function aaSertakanLog(b, kini, opsi, akun) {
  const R = JC.jcRentangCadangan(kini, JC.JC_HARI_CADANGAN);
  if (aaServer() && aaOwner(akun) && opsi && opsi.bacaLog) { try { const L = await opsi.bacaLog({ dari: R.dari, sampai: R.sampai }, JC.JC_MAKS_CADANGAN); return JC.jcSertakanLog(b, L, R); } catch (e) { return JC.jcSertakanLog(b, null, R, String((e && e.message) || e)); } }
  const L = (cacheMentah('log') || []).filter((l) => l && String(l.pada || '') >= R.dari && String(l.pada || '') < R.sampai); return JC.jcSertakanLog(b, L, R);
}
/** Aksi panel (digabung ke AKSI Menu). o = { set, st, tulis, waktu, kini, opsi, akun, dasar, proyek, keTujuan }. */
export function aksiPanelArsipAudit(o) {
  const { set, st } = o; const A = () => Object.assign(AA_DRAF_KOSONG(), st().aa || {}); const ubah = (p) => set({ aa: Object.assign(A(), p) }); const ak = () => (o.akun ? o.akun() : null);
  const tautanDari = (kode) => DPB.dpbTautan(kode, o.dasar ? o.dasar() : '', o.proyek ? o.proyek() : '');
  async function bacaLog(saring, judul, maks) {
    if (!aaOwner(ak())) return; ubah({ jcMuat: 'muat', jcPesan: '', jcSaring: { oleh: '', koleksi: '', kata: '' } });
    if (!aaServer() || !o.opsi.bacaLog) { const L = (cacheMentah('log') || []).filter((l) => (saring.idDok ? String(l.idDok || '') === String(saring.idDok) : String(l.pada || '') >= saring.dari && String(l.pada || '') < saring.sampai));
      return ubah({ jcMuat: 'ada', jcHasil: { judul, daftar: L }, jcPesan: 'SIMULASI (cadangan): yang dibaca hanya log di memori perangkat ini (' + L.length + ' tulisan)' }); }
    try { const L = await o.opsi.bacaLog(saring, maks); ubah({ jcMuat: 'ada', jcHasil: { judul, daftar: L }, jcPesan: JC.jcKalimatBaca(L, maks, judul) }); }
    catch (e) { ubah({ jcMuat: 'galat', jcPesan: 'Log belum bisa dibaca: ' + String((e && (e.code || e.message)) || e) }); }
  }
  return {
    aaOrp: ({ p }) => ubah({ orp: p }),
    aaJcTanggal: (v) => ubah({ jcTanggal: String(v || '').slice(0, 10) }),
    aaJcKata: (v) => ubah({ jcSaring: Object.assign({}, A().jcSaring, { kata: String(v || '').slice(0, 60) }) }),
    aaJcSaring: ({ kolom, nilai }) => ubah({ jcSaring: Object.assign({}, A().jcSaring, { [kolom]: A().jcSaring[kolom] === nilai ? '' : nilai }) }),
    aaJcBaca: () => { const t = A().jcTanggal || hariIniIso(o.kini()); const R = JC.jcRentangHari(t); if (!R) return ubah({ jcMuat: 'galat', jcPesan: 'Tanggal tidak sah' }); return bacaLog({ dari: R.dari, sampai: R.sampai }, 'Log ' + tanggalPendek(t), JC.JC_MAKS_HARI); },
    aaJcCatatan: ({ id }) => bacaLog({ idDok: String(id) }, 'Riwayat catatan ' + id, JC.JC_MAKS_CATATAN),
    aaFotoKedatangan: ({ id }) => { if (o.keTujuan) o.keTujuan({ ke: 'stok', lembar: 'masuk', isi: { koreksi: String(id) } }); },
    aaUnduhFoto: async ({ key }) => {
      if (!aaOwner(ak()) || A().afMuat) return; ubah({ afMuat: key }); set({ kabar: 'Membaca foto ' + AF.afNamaBulan(key) + ' dari server…', kabarAwas: false });
      let F = []; try { F = aaServer() && o.opsi.bacaFotoBulan ? await o.opsi.bacaFotoBulan(key) : []; } catch (e) { ubah({ afMuat: '' }); return set({ kabar: 'Foto belum bisa dibaca: ' + String((e && (e.code || e.message)) || e), kabarAwas: true }); }
      ubah({ afMuat: '' }); const B = AF.afBerkasArsip(F, key, o.kini()); if (B.tolak) return set({ kabar: (aaServer() ? '' : 'SIMULASI (cadangan): foto tidak ada di berkas cadangan — ') + B.tolak, kabarAwas: !aaServer() });
      try { aaUnduh(B.nama, B.isi, 'text/html'); } catch (e) { return set({ kabar: 'Peramban ini tidak bisa mengunduh berkas: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
      const T = AF.afSusunTandaKurang(F); if (!T.kosong) await o.tulis(T); set({ kabar: B.kabar + (T.kosong ? '' : ' · ' + T.patch.kabar), kabarAwas: false });
    },
    aaDpbBagian: ({ id }) => { const b = A().dpbBagian.slice(); const i = b.indexOf(id); if (i >= 0) b.splice(i, 1); else b.push(id); ubah({ dpbBagian: b, dpbYakin: null }); },
    aaDpbHari: ({ n }) => ubah({ dpbHari: Number(n), dpbYakin: null }),
    aaDpbUntuk: (v) => ubah({ dpbUntuk: String(v || '').slice(0, DPB.DPB_UNTUK_MAKS), dpbYakin: null }),
    aaDpbBuat: async () => {
      if (!aaOwner(ak())) return set({ kabar: 'Tautan Dasbor hanya untuk akun owner', kabarAwas: true }); const a = A();
      const P = DPB.dpbPilihSah({ bagian: a.dpbBagian, hari: a.dpbHari, untuk: a.dpbUntuk }); if (P.tolak) return set({ kabar: P.tolak, kabarAwas: true });
      if (a.dpbYakin !== 'buat') return ubah({ dpbYakin: 'buat' });
      if (aaServer() && typeof navigator !== 'undefined' && navigator.onLine === false) return set({ kabar: 'Membuat tautan butuh internet — sambungkan dulu (jam berlakunya diperiksa server)', kabarAwas: true });
      const r = DPB.dpbSusunBuat({ bagian: a.dpbBagian, hari: a.dpbHari, untuk: a.dpbUntuk }, o.kini(), o.waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      if (await o.tulis(r)) ubah({ dpbBaru: r.kode, dpbYakin: null, dpbUntuk: '' });
    },
    aaDpbSalin: async ({ kode }) => { const t = tautanDari(kode); try { await navigator.clipboard.writeText(t); set({ kabar: 'Tautan disalin — tempel di pesan untuk pihak luar', kabarAwas: false }); } catch (e) { set({ kabar: 'Tidak bisa menyalin otomatis — salin manual: ' + t, kabarAwas: true }); } },
    aaDpbWa: ({ kode }) => { const x = DPB.dpbSemua(o.kini()).find((y) => y.kode === kode); if (!x) return; const teks = DPB.dpbPesanWa(x.untuk, tautanDari(kode), x.sampaiMs);
      try { const w = window.open('https://wa.me/?text=' + encodeURIComponent(teks), '_blank'); if (w) { try { w.opener = null; } catch (e) { /* jendela sudah pindah asal */ } } } catch (e) { set({ kabar: 'WhatsApp tidak bisa dibuka: ' + (e && e.message ? e.message : e), kabarAwas: true }); } },
    aaDpbCabut: async ({ kode }) => { if (!aaOwner(ak())) return; if (A().dpbYakin !== kode) return ubah({ dpbYakin: kode }); const r = DPB.dpbSusunCabut(kode); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); if (await o.tulis(r)) ubah({ dpbYakin: null, dpbBaru: A().dpbBaru === kode ? null : A().dpbBaru }); },
    aaDpbBersih: async () => { if (!aaOwner(ak())) return; const r = DPB.dpbSusunBersihkan(o.kini()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await o.tulis(r); },
  };
}
