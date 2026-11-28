// Panel TUGAS DARI OWNER di tablet (owner 28 Nov 2026, rules v27: "Foto bukti hanya saat gua minta" + "Tugas dari owner"). Owner mengirim tugas dari lonceng
// (Obrolan › Tugas / Tugas + foto) atau dari titipan yang menunggu ("Minta foto bukti"). Tablet menjawab dengan SELESAI — catatan singkat, dan FOTO bila owner
// mewajibkannya. Foto dikecilkan (±300 KB, sama dengan foto nota) lalu dikirim ke koleksi fotoBukti; jawabannya = persetujuan 'tugasSelesai' yang menyebut id
// fotonya → kabar ke HP owner (kabarOwner) dan papan Persetujuan ("lihat foto"). Tanpa tugas wajib foto, tablet TIDAK memotret apa pun.
import { h } from '../inti/dom.js';
import { tanggalPendek } from '../inti/format.js';
import { cacheMentah } from '../data/toko.js';
import * as KB from './kabar-baru-logika.js';
import { fbnKecilkan, fbnKB } from './foto-bon-logika.js';

export const TO_DRAF_KOSONG = () => ({ buka: '', catatan: '', fotoUntuk: '', fotoUrl: '', fotoKb: '' });
const toStatus = { menunggu: 'terkirim ke owner', dibaca: 'dibaca owner', disetujui: 'dibaca owner', ditolak: 'ditolak owner' };

/** Jawaban tugas dari akun ini (terbaru dulu, paling banyak 3) — supaya penjaga tahu jawabannya sudah sampai & dibaca. */
function jawabanSaya(akun) {
  const uid = String((akun && akun.uid) || ''); if (!uid) return [];
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'tugasSelesai' && String(m.mintaUid || '') === uid)
    .sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || String(b.jam || '').localeCompare(String(a.jam || ''))).slice(0, 3);
}

/** Kartu tugas (tablet). Tidak ada tugas & tidak ada jawaban = kartu tidak tampil. opsi = { akun }. */
export function kartuTugasOwner(s, opsi) {
  const akun = opsi && opsi.akun; if (!akun || akun.jenis === 'owner') return '';
  const T = KB.kbTugasTerbuka(); const J = jawabanSaya(akun); if (!T.length && !J.length) return '';
  const d = Object.assign(TO_DRAF_KOSONG(), s.to || {}); const sibuk = !!s.toSibuk;
  const form = (t) => h`<div class="kartu" data-k="to-form-${t.id}" style="gap: 6px; margin-top: 6px;">
      <input class="ketik-nama" type="text" maxlength="300" placeholder="Catatan untuk owner (boleh kosong)" value="${d.catatan}" data-ketik="toKetik" data-k="to-cat">
      ${t.wajibFoto ? h`<div class="tombol-baris" data-k="to-foto-baris"><label class="kaca-btn ${d.fotoUntuk === String(t.id) ? '' : 'aktif'}" for="toFotoKamera" data-k="to-ambil">${d.fotoUntuk === String(t.id) ? 'Ganti foto' : 'Ambil foto'}</label>
          ${d.fotoUntuk === String(t.id) ? h`<span class="k2" data-k="to-foto-kb">foto siap · ${d.fotoKb}</span>` : h`<span class="k2" data-k="to-foto-wajib">owner meminta foto untuk tugas ini</span>`}</div>
        <input id="toFotoKamera" type="file" accept="image/*" capture="environment" data-to-foto="${t.id}" hidden>
        ${d.fotoUntuk === String(t.id) && d.fotoUrl ? h`<img src="${d.fotoUrl}" alt="Foto bukti" data-k="to-pratinjau" style="max-width: 220px; max-height: 220px; border-radius: 10px; object-fit: cover;">` : ''}` : ''}
      <div class="pn-dua"><div class="kaca-btn aktif emas" data-aksi="toKirim" data-k="to-kirim">${sibuk ? 'mengirim…' : 'SELESAI · KIRIM KE OWNER'}</div><div class="kaca-btn" data-aksi="toBatal">batal</div></div></div>`;
  const baris = (t) => h`<div class="tp-baris tunggu" data-k="to-${t.id}"><div style="min-width: 0; flex: 1;"><div>${t.teks}</div>
      <div class="k2">${tanggalPendek(t.tanggal)} ${t.jam} · dari owner${t.wajibFoto ? h` · <b>WAJIB FOTO</b>` : ''}</div>
      ${d.buka === String(t.id) ? form(t) : ''}</div>
      ${d.buka === String(t.id) ? '' : h`<div class="kaca-btn kecil aktif emas" data-aksi="toBuka" data-id="${t.id}" data-k="to-buka-${t.id}">Kerjakan</div>`}</div>`;
  const jawab = (m) => h`<div class="tp-baris ${m.status === 'menunggu' ? 'tunggu' : 'lunas'}" data-k="to-j-${m.id}"><div style="min-width: 0;"><div>${m.teks}</div>
      <div class="k2">${tanggalPendek(m.tanggal)} ${m.jam} · <b>${toStatus[m.status] || m.status}</b></div>${m.balasan ? h`<div class="ket">Balasan owner: ${m.balasan}</div>` : ''}</div></div>`;
  return h`<div class="kartu" data-k="to-kartu" style="gap: 8px;"><div class="label">Tugas dari owner${T.length ? ' · ' + T.length + ' belum dikerjakan' : ''}</div>
    ${T.length ? T.map(baris) : h`<div class="ket" data-k="to-kosong">Semua tugas sudah dijawab.</div>`}
    ${J.length ? h`<div class="label" data-k="to-jawab">Jawaban terakhir</div>${J.map(jawab)}` : ''}</div>`;
}

const alatFoto = () => ({
  buka: async (berkas) => {
    if (typeof createImageBitmap === 'function') { try { const g = await createImageBitmap(berkas, { imageOrientation: 'from-image' }); return { lebar: g.width, tinggi: g.height, gambar: g }; } catch (e) { /* jatuh ke <img> */ } }
    const url = URL.createObjectURL(berkas);
    try { const img = await new Promise((jadi, gagal) => { const i = new Image(); i.addEventListener('load', () => jadi(i)); i.addEventListener('error', () => gagal(new Error('gambar tidak terbaca'))); i.src = url; }); return { lebar: img.naturalWidth, tinggi: img.naturalHeight, gambar: img }; }
    finally { setTimeout(() => URL.revokeObjectURL(url), 30000); }
  },
  jpeg: (g, w, t, mutu) => { const c = document.createElement('canvas'); c.width = w; c.height = t; const x = c.getContext('2d'); x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, t); x.drawImage(g, 0, 0, w, t); return c.toDataURL('image/jpeg', mutu); },
});

/**
 * Aksi panel — digabung ke AKSI layar Menu. foto = { ada() (Firestore tersambung), simpan(data) → { ok | antre | gagal } }. toFotoDipilih(el) dipanggil dari
 * peristiwa 'change' input berkas (menu.js), bukan dari ketukan.
 */
export function aksiTugasOwner({ set, st, tulis, akun, waktu, foto }) {
  let hasil = null; let proses = false; let kecilkan = false;
  const draf = () => Object.assign(TO_DRAF_KOSONG(), st().to || {}); const ubah = (p) => set({ to: Object.assign(draf(), p) });
  const buangFoto = () => { const d = draf(); if (d.fotoUrl) { try { URL.revokeObjectURL(d.fotoUrl); } catch (e) { /* abaikan */ } } hasil = null; };
  return {
    toBuka: ({ id }) => { if (draf().buka === String(id)) return; buangFoto(); set({ to: Object.assign(TO_DRAF_KOSONG(), { buka: String(id) }) }); },
    toBatal: () => { buangFoto(); set({ to: TO_DRAF_KOSONG() }); },
    toKetik: (v) => ubah({ catatan: String(v).slice(0, 300) }),
    toFotoDipilih: async (el) => {
      const berkas = (el && el.files && el.files[0]) || null; const untuk = String((el && el.dataset.toFoto) || ''); if (el) el.value = ''; if (!berkas || kecilkan) return;
      kecilkan = true; set({ kabar: 'Mengecilkan foto…', kabarAwas: false });
      try {
        const x = await fbnKecilkan(berkas, alatFoto()); if (x.tolak) return set({ kabar: x.tolak, kabarAwas: true });
        buangFoto(); hasil = { jenis: x.jenis, base64: x.base64, byte: x.byte, lebar: x.lebar, tinggi: x.tinggi };
        let url = ''; try { url = URL.createObjectURL(berkas); } catch (e) { url = ''; }
        ubah({ fotoUntuk: untuk, fotoUrl: url, fotoKb: fbnKB(x.byte) }); set({ kabar: 'Foto siap (' + fbnKB(x.byte) + ') — terkirim bersama jawaban tugas', kabarAwas: false });
      } finally { kecilkan = false; }
    },
    toKirim: async () => {
      const a = akun ? akun() : null; const d = draf(); const t = KB.kbTugasTerbuka().find((x) => String(x.id) === d.buka);
      if (!t) return set({ kabar: 'Tugas itu sudah dijawab atau dibatalkan owner', kabarAwas: true });
      const adaFoto = !!hasil && d.fotoUntuk === String(t.id);
      if (t.wajibFoto && !adaFoto) return set({ kabar: 'Owner meminta FOTO untuk tugas ini — ketuk "Ambil foto" dulu', kabarAwas: true });
      if (proses) return; proses = true; set({ toSibuk: true });
      try {
        let fotoId = ''; let ekor = '';
        if (adaFoto) {
          const w0 = waktu(); const data = Object.assign({ id: 'fbk-' + Date.now() + '-' + Math.floor(Math.random() * 1e4), tugasId: String(t.id), tanggal: w0.tanggal, jam: w0.jam }, hasil);
          if (!foto || !foto.ada()) ekor = ' · SIMULASI (cadangan): foto tidak dikirim ke mana pun';
          else { const F = await foto.simpan(data); if (F && F.gagal) return set({ kabar: 'Foto TIDAK terkirim — tugas belum dijawab: ' + F.pesan, kabarAwas: true }); if (F && F.antre) ekor = ' · foto belum sampai server (sinyal lambat) — terkirim sendiri saat internet lancar'; }
          fotoId = data.id;
        }
        const r = KB.kbSusunTugasSelesai(t, d.catatan, fotoId, waktu(), a, a && a.nama); if (r.patch && ekor) r.patch.kabar += ekor;
        if (await tulis(r)) { buangFoto(); set({ to: TO_DRAF_KOSONG() }); }
      } finally { proses = false; set({ toSibuk: false }); }
    },
  };
}
