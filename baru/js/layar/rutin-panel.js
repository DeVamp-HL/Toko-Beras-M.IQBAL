// Panel HALAMAN TUGAS STAF + DAFTAR RUTIN (owner 27 Nov 2026, paket P6: B116 + A143). Isi & angka = tugas-staf-logika.js & rutin-logika.js; panel ini hanya
// menggambar & meneruskan ketukan. Dipasang layar Menu: akun staf (Penjaga laci & karyawan) melihat kartu Tugas hari ini PALING ATAS (halaman pembuka sesudah masuk)
// + kartu Rutin; owner melihat Menu › Toko ini › Rutin (hari ini · siapa mencentang · atur daftar).
// Tulisan: satu dokumen rutinCek per centang (susunCentangRutin — owner, Penjaga laci, karyawan: rules v25) · hapus centang (owner) · aturanToko/rutin (owner).
import { h } from '../inti/dom.js';
import { tanggalPendek } from '../inti/format.js';
import { RN_BATAS, RN_HARI, RN_MULAI, RN_OTOMATIS, RN_ULANG, RN_UNTUK, rnAtur, rnHari, rnRiwayat, susunAturRutin, susunBatalRutin, susunCentangRutin } from './rutin-logika.js';
import { tsTugas } from './tugas-staf-logika.js';

const KATA = { sudah: 'beres', belum: 'belum', nanti: 'nanti', lewat: 'lewat', tidakTerbaca: 'owner' };
const drafDari = (A) => ({ butir: A.butir.map((b) => Object.assign({}, b, { hari: String(b.hari) })) });

/** Kartu TUGAS HARI INI (akun staf, paling atas Menu). opsi = { akun, kini }. */
export function kartuTugasStaf(s, opsi) {
  const o = opsi || {}; let T; try { T = tsTugas(o.kini || new Date(), o.akun); } catch (e) { return h`<div class="kartu" data-k="ts-galat"><div class="ket awas-teks">Tugas hari ini gagal dihitung: ${String((e && e.message) || e)}</div></div>`; }
  let urut = 0;
  return h`<div class="kartu emas ts-kartu" data-k="ts-kartu" style="gap: 8px;"><div class="label">Tugas hari ini · ${tanggalPendek(T.iso)}</div>
    <div class="pita-info ${T.awas ? 'awas' : 'emas'}" data-k="ts-ringkas">${T.kalimat}</div>
    ${T.daftar.map((x) => h`<div class="ts-baris ${x.n > 0 ? (x.awas ? 'awas' : 'buka') : 'beres'}" data-k="ts-${x.id}" data-aksi="tsKe" data-id="${x.id}" style="--urut: ${Math.min(urut++, 10)};"><div style="min-width: 0;"><div style="font-weight: 600;">${x.nama}</div><div class="k2">${x.ket}</div></div><div class="ts-n">${x.galat ? '!' : x.n > 0 ? x.n : '✓'}</div></div>`)}
    <div class="kaca-btn aktif emas" data-aksi="stafKe" data-t="jual" data-k="ts-jual">MULAI JUALAN ›</div></div>`;
}

/** Satu baris rutin (staf & owner). owner = tampilkan tombol batal centang. */
function barisRutin(b, s, owner) {
  const buka = s.rnCatat && s.rnCatat.id === b.id;
  return h`<div class="rn-baris ${b.keadaan}" data-k="rn-${b.id}"><div style="min-width: 0;"><div style="font-weight: 600;">${b.nama}</div>
      <div class="k2">${b.jadwal}${b.untuk !== 'semua' ? ' · ' + (RN_UNTUK.find((u) => u.id === b.untuk) || {}).nama : ''} · ${b.teks}${b.catatan ? ' · ' + b.catatan : ''}</div>${b.ket ? h`<div class="k2 redup">${b.ket}</div>` : ''}
      ${buka ? h`<div style="display: flex; gap: 6px; margin-top: 4px;"><input class="ketik-nama" type="text" placeholder="catatan (boleh kosong)" value="${s.rnCatat.teks}" data-ketik="rnCatatKetik"><div class="kaca-btn kecil aktif emas" data-aksi="rnCentang" data-id="${b.id}">✓ simpan</div></div>` : ''}</div>
    <div class="n">${b.sudah ? h`<span class="rn-cap sudah">✓</span>${owner && b.cekId ? h`<div class="tautan" data-aksi="rnBatal" data-id="${b.cekId}">batal</div>` : ''}` : b.bisaCentang ? h`<div class="kaca-btn kecil ${b.keadaan === 'lewat' ? 'awas' : 'aktif'}" data-aksi="rnCentang" data-id="${b.id}">centang</div><div class="tautan" data-aksi="rnCatatBuka" data-id="${b.id}">+ catatan</div>` : h`<span class="rn-cap ${b.keadaan}">${KATA[b.keadaan] || b.keadaan}</span>`}</div></div>`;
}

/** Kartu RUTIN (staf: rutin perannya; owner: semuanya). opsi = { akun, kini, owner }. */
export function kartuRutin(s, opsi) {
  const o = opsi || {}; let R; try { R = rnHari(o.kini || new Date(), o.akun); } catch (e) { return h`<div class="kartu" data-k="rn-galat"><div class="ket awas-teks">Daftar rutin gagal dihitung: ${String((e && e.message) || e)}</div></div>`; }
  if (!R.baris.length) return '';
  return h`<div class="kartu rn-kartu" data-k="rn-kartu" style="gap: 6px;"><div class="label">Rutin${R.dariOwner ? '' : ' · daftar bawaan'}</div>
    <div class="${R.nLewat ? 'pita-info awas' : 'k2'}" data-k="rn-ringkas">${R.kalimat}</div>
    ${R.kelompok.map((k) => h`<div class="label" style="font-size: 9.5px; margin-top: 4px;" data-k="rn-k-${k.ulang}">${k.nama} · ${k.nSudah} dari ${k.n}</div>${k.baris.map((b) => barisRutin(b, s, o.owner))}`)}
    <div class="ket" style="font-size: 10.5px;">Yang bertanda "terbaca dari …" tercentang sendiri begitu dikerjakan di layarnya. Centang tercatat atas nama orang yang jaga.</div></div>`;
}

/** Menu › Toko ini › Rutin (owner): tab hari ini · siapa mencentang · atur daftar. */
export function gambarRutinOwner(s, opsi) {
  const o = opsi || {}; const tab = o.tab || 'hari';
  if (tab === 'riwayat') { const R = rnRiwayat(o.kini || new Date(), 14);
    return h`<div class="kartu" data-k="rn-riwayat" style="gap: 4px;"><div class="label">Rutin harian · siapa mencentang · 14 hari</div>
      ${R.hari.length ? R.hari.map((x) => h`<div class="ug-baris dua" data-k="rn-r-${x.iso}"><div style="min-width: 0;"><div>${tanggalPendek(x.iso)} · <b>${x.nSudah} dari ${x.n}</b></div><div class="k2">${Object.keys(x.oleh).length ? Object.keys(x.oleh).map((n) => n + ' ' + x.oleh[n]).join(' · ') : 'belum ada yang mencentang'}${x.terlewat.length ? ' · terlewat: ' + x.terlewat.slice(0, 4).join(', ') + (x.terlewat.length > 4 ? ', …' : '') : ''}</div></div></div>`) : h`<div class="k2">Riwayat terisi mulai ${tanggalPendek(RN_MULAI)} (hari daftar rutin lahir).</div>`}
      <div class="ket" style="font-size: 10.5px;">Hanya butir harian yang dicentang tangan (${R.nManual} butir). Butir otomatis riwayatnya ada di layarnya masing-masing.</div></div>`; }
  if (tab === 'atur') return kartuAtur(s.rnAtur || drafDari(rnAtur()), !!s.rnAtur);
  return kartuRutin(s, { akun: o.akun, kini: o.kini, owner: true });
}

function kartuAtur(a, sunting) {
  const seg = (v, id, aksi, i, nama) => h`<span class="seg ${String(v) === String(id) ? 'aktif' : ''}" data-aksi="${aksi}" data-i="${i}" data-nilai="${id}">${nama}</span>`;
  return h`<div class="kartu rn-atur" data-k="rn-atur" style="gap: 8px;"><div class="label">Atur daftar rutin · ${a.butir.length} butir (paling banyak ${RN_BATAS.butir})</div>
    ${a.butir.map((b, i) => h`<div class="pt-atur-baris" data-k="rn-a-${i}"><div class="ps-form dua"><div><div class="ket">Nama</div><input class="ketik-nama" type="text" maxlength="${RN_BATAS.nama}" value="${b.nama}" data-ketik="rnAturKetik" data-i="${i}" data-kolom="nama"></div>
        <div><div class="ket">Keterangan</div><input class="ketik-nama" type="text" maxlength="${RN_BATAS.ket}" value="${b.ket || ''}" data-ketik="rnAturKetik" data-i="${i}" data-kolom="ket"></div></div>
      <div class="hg-pil">${RN_ULANG.map((u) => seg(b.ulang, u.id, 'rnAturUlang', i, u.nama))}</div>
      ${b.ulang === 'mingguan' ? h`<div class="hg-pil">${[1, 2, 3, 4, 5, 6, 7].map((d) => seg(b.hari, d, 'rnAturHari', i, RN_HARI[d]))}</div>`
        : b.ulang === 'bulanan' ? h`<div><div class="ket">Tanggal (1–28, kosong / 0 = akhir bulan)</div><input class="ketik-nama sempit" type="text" inputmode="numeric" value="${String(b.hari) === '0' ? '' : b.hari}" data-ketik="rnAturKetik" data-i="${i}" data-kolom="hari"></div>` : ''}
      <div class="hg-pil">${RN_UNTUK.map((u) => seg(b.untuk, u.id, 'rnAturUntuk', i, u.nama))}</div>
      <div class="hg-pil">${b.otomatis ? h`<span class="seg">terbaca dari ${RN_OTOMATIS[b.otomatis]}</span>` : ''}<span class="seg ${b.nyala !== false ? 'aktif' : ''}" data-aksi="rnAturNyala" data-i="${i}">${b.nyala !== false ? 'menyala' : 'mati'}</span><span class="seg" data-aksi="rnAturHapus" data-i="${i}">hapus butir</span></div></div>`)}
    <div class="kaca-btn kecil" data-aksi="rnAturTambah" style="align-self: flex-start;">+ tambah butir</div>
    <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="rnAturBatal">${sunting ? 'batal' : 'tutup'}</div><div class="kaca-btn aktif emas" data-aksi="rnAturSimpan">SIMPAN DAFTAR</div></div>
    <div class="k2">"Semua yang jaga" = Penjaga laci & karyawan boleh mencentang · "Penjaga laci" = karyawan tidak melihatnya · "Owner" = hanya di HP / Mac owner. Butir otomatis tidak dicentang tangan.</div></div>`;
}

/** Aksi panel. opsi = { set, st, tulis (r → Promise<bool>), waktu, kini, akun, pergi(tujuan) }. */
export function aksiPanelRutin({ set, st, tulis, waktu, kini, akun, pergi }) {
  const draf = () => JSON.parse(JSON.stringify(st().rnAtur || drafDari(rnAtur())));
  const centang = async (id) => { const c = st().rnCatat && st().rnCatat.id === id ? st().rnCatat.teks : ''; const r = susunCentangRutin(id, c, waktu(), akun ? akun() : null, kini()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); };
  return {
    tsKe: ({ id }) => { const T = tsTugas(kini(), akun ? akun() : null); const x = T.daftar.find((d) => d.id === id); if (!x || !x.tujuan) return;
      if (x.tujuan.ke === 'menu') { set({ kabar: x.ket, kabarAwas: false }); try { const el = document.querySelector('[data-k="rn-kartu"]'); if (el && el.scrollIntoView) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) { /* tanpa gulir */ } return; }
      if (pergi) pergi(x.tujuan); },
    rnCentang: ({ id }) => centang(id),
    rnCatatBuka: ({ id }) => set({ rnCatat: st().rnCatat && st().rnCatat.id === id ? null : { id, teks: '' }, kabar: '' }),
    rnCatatKetik: (v) => set({ rnCatat: Object.assign({}, st().rnCatat, { teks: String(v).slice(0, RN_BATAS.catatan) }) }),
    rnBatal: async ({ id }) => { await tulis(susunBatalRutin(id, akun ? akun() : null)); },
    rnAturKetik: (v, el) => { const a = draf(); const b = a.butir[Number(el.dataset.i)]; if (!b) return; const k = el.dataset.kolom;
      b[k] = k === 'hari' ? String(v).replace(/[^0-9]/g, '').slice(0, 2) : String(v).slice(0, k === 'ket' ? RN_BATAS.ket : RN_BATAS.nama); set({ rnAtur: a }); },
    rnAturUlang: ({ i, nilai }) => { const a = draf(); const b = a.butir[Number(i)]; if (b && b.ulang !== nilai) { b.ulang = nilai; b.hari = nilai === 'mingguan' ? '1' : '0'; } set({ rnAtur: a }); },
    rnAturHari: ({ i, nilai }) => { const a = draf(); const b = a.butir[Number(i)]; if (b) b.hari = String(nilai); set({ rnAtur: a }); },
    rnAturUntuk: ({ i, nilai }) => { const a = draf(); const b = a.butir[Number(i)]; if (b) b.untuk = nilai; set({ rnAtur: a }); },
    rnAturNyala: ({ i }) => { const a = draf(); const b = a.butir[Number(i)]; if (b) b.nyala = b.nyala === false; set({ rnAtur: a }); },
    rnAturHapus: ({ i }) => { const a = draf(); a.butir.splice(Number(i), 1); set({ rnAtur: a }); },
    rnAturTambah: () => { const a = draf(); a.butir.push({ id: '', nama: '', ulang: 'harian', hari: '0', untuk: 'semua', ket: '', nyala: true }); set({ rnAtur: a }); },
    rnAturBatal: () => set({ rnAtur: null, kabar: '' }),
    rnAturSimpan: async () => { const r = susunAturRutin(draf(), waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
  };
}
