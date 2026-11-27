// Panel FOTO NOTA KEDATANGAN di layar Stok (paket P8, owner 27 Nov 2026 — A94: "owner + tablet Penjaga laci"). Kartu satu kedatangan (bon pemasok ATAU tunai): ambil foto / pilih
// dari galeri → dikecilkan di perangkat (foto-bon-logika, sama dengan foto bon pemasok) → satu foto + tanda ringannya (arsip-foto-logika afTandaDari) ditulis bersama
// (firebase.js simpanFotoBon, koleksi fotoBon idBon = id kedatangan). OWNER melihat, memperbesar & menghapus foto (dibaca saat diketuk). PENJAGA LACI (tablet, rules v26)
// hanya MENAMBAH foto — foto tidak bisa ia lihat lagi sesudah keluar lembar (baca foto = owner saja); panel menyebut foto yang baru ia kirim di sesi ini.
// Mode cadangan (pratinjau) = SIMULASI di memori layar ini, tidak tertulis ke mana pun. Panel ini hanya menggambar & meneruskan ketukan.
import { h } from '../inti/dom.js';
import { tanggalPendek } from '../inti/format.js';
import * as FB from './foto-bon-logika.js';
import * as AF from './arsip-foto-logika.js';
import { bukanOwner } from './akses-layar.js';
import { bolehFotoNota } from '../data/akses.js';

const FN_KABAR_PERMISI = 'server belum membuka foto nota dari tablet (rules v26 — owner menerbitkannya di Firebase Console)';
/** Kartu foto nota untuk kedatangan `id` (kosong bila bukan kedatangan nyata / akun tidak boleh). ctx = { s, akun }. */
export function kartuFotoNota(id, ctx) {
  if (id === undefined || id === null || id === '') return ''; const c = ctx || {}; const a = c.akun || null; if (!bolehFotoNota(a)) return '';
  const K = AF.afKedatangan(id); if (!K) return '';
  const owner = !bukanOwner(a); const s = c.s || {}; const F = s.fn && String(s.fn.id) === String(id) ? s.fn : { muat: 'belum', daftar: [], pesan: '' };
  const daftar = FB.fbnUrut(F.daftar || [], String(id)); const besar = F.besar ? daftar.find((x) => String(x.id) === String(F.besar)) : null;
  const nAntre = daftar.filter((x) => x.antre).length; const tahan = !!F.proses;
  const status = F.muat === 'muat' ? 'Memuat foto…' : F.muat === 'galat' ? F.pesan
    : owner ? (F.muat === 'ada' ? (daftar.length ? daftar.length + ' foto' + (nAntre ? ' (' + nAntre + ' BELUM sampai server)' : '') : 'Belum ada foto nota kedatangan ini') : (K.nFoto ? K.nFoto + ' foto tercatat — ketuk "lihat foto"' : 'Belum ada foto nota kedatangan ini'))
      : (daftar.length ? daftar.length + ' foto dikirim dari tablet ini' + (nAntre ? ' (' + nAntre + ' BELUM sampai server)' : '') + ' — fotonya dilihat owner' : 'Foto nota / bon supir, lalu kirim — owner yang melihatnya');
  return h`<div class="kartu fn-kartu" data-k="fn-kartu" style="gap: 6px;"><div class="label">Foto nota ${K.jenis === 'tunai' ? 'kedatangan (TUNAI)' : 'bon pemasok'} · ${K.pemasok} · ${tanggalPendek(K.tanggal)}</div>
    <div class="ket ${F.muat === 'galat' ? 'awas-teks' : ''}" data-k="fn-status">${status}${F.pesan && F.muat !== 'galat' ? ' · ' + F.pesan : ''}</div>
    <div class="tombol-baris rapat"><div class="kaca-btn ${tahan ? 'mati' : 'aktif'}" data-aksi="fnAmbil" data-id="${K.id}" data-cara="kamera">${F.proses ? 'Memproses foto…' : 'Ambil foto'}</div><div class="kaca-btn ${tahan ? 'mati' : ''}" data-aksi="fnAmbil" data-id="${K.id}" data-cara="galeri">Pilih dari galeri</div>
      ${owner && F.muat !== 'ada' && F.muat !== 'muat' && K.nFoto ? h`<div class="kaca-btn" data-aksi="fnLihat" data-id="${K.id}" data-k="fn-lihat">lihat foto (${K.nFoto})</div>` : ''}</div>
    <input id="fnKamera" type="file" accept="image/*" capture="environment" data-fn-pilih="kamera" hidden><input id="fnGaleri" type="file" accept="image/*" multiple data-fn-pilih="galeri" hidden>
    <div class="ket" style="font-size: 10.5px;">Dikecilkan di perangkat ini dulu (±${FB.fbnKB(FB.FBN_TARGET)} per foto), paling banyak ${FB.FBN_PALING_BANYAK} foto per kedatangan. Foto disimpan di server (dibaca hanya saat dibuka), TIDAK ikut cadangan berkas — arsipnya diunduh per bulan di Menu › Toko ini › Cadangan & simpanan.</div>
    ${besar ? h`<div class="fn-besar" data-k="fn-besar" data-aksi="fnBesar" data-id="${besar.id}"><img src="${FB.fbnSrc(besar)}" alt="Foto nota besar"><div class="ket">ketuk untuk menutup</div></div>` : ''}
    ${daftar.length ? h`<div class="fn-kisi" data-k="fn-kisi">${daftar.map((f) => h`<div class="fn-foto" data-k="fn-${f.id}">${f.base64 && owner ? h`<img src="${FB.fbnSrc(f)}" alt="Foto nota" data-aksi="fnBesar" data-id="${f.id}">` : f.base64 ? h`<img src="${FB.fbnSrc(f)}" alt="Foto nota">` : ''}<div class="ket ${f.antre ? 'awas-teks' : ''}">${f.antre ? 'BELUM sampai server' : (f.tanggal ? tanggalPendek(f.tanggal) + ' ' : '') + (f.jam || '') + ' · ' + FB.fbnKB(f.byte)}</div>
      ${owner && !f.antre ? h`<div class="kaca-btn kecil ${F.yakinHapus === String(f.id) ? 'awas' : 'putus'}" data-aksi="fnHapus" data-id="${f.id}">${F.yakinHapus === String(f.id) ? 'YAKIN hapus' : 'hapus'}</div>` : ''}</div>`)}</div>` : ''}
  </div>`;
}
/** Aksi panel (digabung ke AKSI layar Stok). o = { set, st, akun, waktu, foto, akar }. foto = { ada, baca, simpan, hapus } dari app.js (null = simulasi). */
export function aksiPanelFotoNota(o) {
  const { set, st, waktu } = o; const ak = () => (o.akun ? o.akun() : null); const sim = {}; let antre = 0;
  const fotoServer = () => !!(o.foto && o.foto.ada && o.foto.ada());
  const ubah = (id, p) => { const F0 = st().fn && String(st().fn.id) === String(id) ? st().fn : { id: String(id), muat: 'belum', daftar: [], pesan: '' }; set({ fn: Object.assign({}, F0, p, { id: String(id) }) }); };
  const alat = () => ({
    buka: async (berkas) => {
      if (typeof createImageBitmap === 'function') { try { const g = await createImageBitmap(berkas, { imageOrientation: 'from-image' }); return { lebar: g.width, tinggi: g.height, gambar: g }; } catch (e) { /* jatuh ke <img> */ } }
      const url = URL.createObjectURL(berkas);
      try { const img = await new Promise((jadi, gagal) => { const i = new Image(); i.addEventListener('load', () => jadi(i)); i.addEventListener('error', () => gagal(new Error('gambar tidak terbaca'))); i.src = url; }); return { lebar: img.naturalWidth, tinggi: img.naturalHeight, gambar: img }; }
      finally { setTimeout(() => URL.revokeObjectURL(url), 30000); }
    },
    jpeg: (g, w, t, mutu) => { const c = document.createElement('canvas'); c.width = w; c.height = t; const x = c.getContext('2d'); x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, t); x.drawImage(g, 0, 0, w, t); return c.toDataURL('image/jpeg', mutu); },
  });
  async function dipilih(el) {
    const berkas = Array.from((el && el.files) || []); if (el) el.value = ''; const F = st().fn; if (!berkas.length || !F || F.proses) return;
    const K = AF.afKedatangan(F.id); if (!K) return set({ kabar: 'Kedatangan itu sudah tidak ada', kabarAwas: true });
    ubah(F.id, { proses: true }); set({ kabar: 'Mengecilkan foto…', kabarAwas: false });
    for (const f of berkas) {
      const hasil = await FB.fbnKecilkan(f, alat()); const bon = { id: K.id, pemasok: K.pemasok, tanggal: K.tanggal, noBon: K.noBon };
      const r = FB.fbnSusunSimpan(bon, hasil, waktu(), (st().fn || {}).daftar || [], antre); if (r.tolak) { ubah(F.id, { proses: false }); return set({ kabar: r.tolak, kabarAwas: true }); }
      const tanda = AF.afTandaDari(r.data);
      const x = fotoServer() ? await o.foto.simpan(r.data, tanda) : { ok: true, simulasi: true, data: r.data };
      if (x && x.gagal) { ubah(F.id, { proses: false }); return set({ kabar: 'Foto TIDAK tersimpan: ' + (/permission/i.test(x.pesan || '') ? FN_KABAR_PERMISI : x.pesan), kabarAwas: true }); }
      if (x && x.simulasi) sim[K.id] = (sim[K.id] || []).concat([r.data]);
      if (x && x.antre) { antre += 1; ikuti(x.selesai, String(r.data.id), K.id); }
      ubah(F.id, { daftar: ((st().fn || {}).daftar || []).concat([Object.assign({}, x.data || r.data, x && x.antre ? { antre: true } : {})]), muat: bukanOwner(ak()) ? 'kirim' : ((st().fn || {}).muat === 'ada' ? 'ada' : 'kirim') });
      set({ kabar: x && x.antre ? FB.fbnKabarAntre(r.data) : (x && x.simulasi ? 'SIMULASI (cadangan) — ' : '') + r.patch.kabar.replace('Foto bon', 'Foto nota'), kabarAwas: !!(x && x.antre) });
    }
    ubah(F.id, { proses: false });
  }
  function ikuti(selesai, id, idK) {
    if (!selesai || typeof selesai.then !== 'function') return;
    selesai.then((y) => { antre = Math.max(0, antre - 1); const F2 = st().fn; const di = !!(F2 && String(F2.id) === String(idK));
      if (y && y.ok) { if (di) ubah(idK, { daftar: (F2.daftar || []).map((z) => (String(z.id) === id ? Object.assign({}, z, { antre: false }) : z)) }); set({ kabar: 'Foto nota yang tadi menunggu sudah SAMPAI di server', kabarAwas: false }); return; }
      if (di) ubah(idK, { daftar: (F2.daftar || []).filter((z) => String(z.id) !== id) });
      set({ kabar: 'Foto nota yang tadi menunggu DITOLAK server — TIDAK tersimpan: ' + (y && /permission/i.test(y.pesan || '') ? FN_KABAR_PERMISI : (y && y.pesan) || 'tanpa keterangan'), kabarAwas: true }); });
  }
  if (o.akar) o.akar.addEventListener('change', (ev) => { const el = ev.target && ev.target.closest ? ev.target.closest('[data-fn-pilih]') : null; if (el) dipilih(el).catch((e) => { const F = st().fn; if (F) ubah(F.id, { proses: false }); set({ kabar: 'Foto gagal diproses: ' + (e && e.message ? e.message : e), kabarAwas: true }); }); });
  return {
    fnAmbil: ({ id, cara }) => { const F = st().fn; if (F && F.proses) return; ubah(id, {}); const el = o.akar ? o.akar.querySelector(cara === 'kamera' ? '#fnKamera' : '#fnGaleri') : null; if (el) el.click(); },
    fnLihat: async ({ id }) => {
      if (bukanOwner(ak())) return; ubah(id, { muat: 'muat', daftar: [], pesan: '', besar: null, yakinHapus: null });
      if (!fotoServer()) return ubah(id, { muat: 'ada', daftar: (sim[String(id)] || []).slice(), pesan: 'SIMULASI (cadangan): foto hanya disimpan di memori layar ini' });
      try { const d = await o.foto.baca(String(id)); ubah(id, { muat: 'ada', daftar: d || [], pesan: d && d.dariCache ? 'dibaca dari cache perangkat (server belum terjangkau)' : '' }); }
      catch (e) { ubah(id, { muat: 'galat', pesan: 'Foto belum bisa dibaca: ' + String((e && (e.code || e.message)) || e) }); }
    },
    fnBesar: ({ id }) => { const F = st().fn; if (!F) return; ubah(F.id, { besar: F.besar && String(F.besar) === String(id) ? null : String(id) }); },
    fnHapus: async ({ id }) => {
      const F = st().fn; if (!F || bukanOwner(ak())) return; if (F.yakinHapus !== String(id)) return ubah(F.id, { yakinHapus: String(id) });
      const x = fotoServer() ? await o.foto.hapus(String(id), F.id) : { ok: true, simulasi: true };
      if (x && x.gagal) return set({ kabar: 'Foto TIDAK terhapus: ' + x.pesan, kabarAwas: true });
      if (x && x.simulasi) sim[F.id] = (sim[F.id] || []).filter((z) => String(z.id) !== String(id));
      ubah(F.id, { daftar: (F.daftar || []).filter((z) => String(z.id) !== String(id)), yakinHapus: null, besar: null }); set({ kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + 'Foto nota dihapus', kabarAwas: false });
    },
  };
}
