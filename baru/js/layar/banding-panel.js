// Panel USUL HARGA TAWARAN / ACUAN di tablet (paket Banding pemasok, owner 26 Nov 2026: "Owner + Ben lewat usul"). Penjaga laci mengetik harga yang
// ditawarkan pemasok (atau harga acuan resmi); yang terkirim HANYA usul berstatus "menunggu" (persetujuan 'hargaBanding', rules v21). Owner menyetujui di
// Menu › Toko ini › Peran & persetujuan › Persetujuan — baru catatannya ditulis (banding-catat-logika bcPasangUsul). Tablet tidak membaca catatan banding toko.
import { h } from '../inti/dom.js';
import { tanggalPendek } from '../inti/format.js';
import * as BC from './banding-catat-logika.js';
import { calonPemasok } from './stok-catat-logika.js';

export const UB_DRAF_KOSONG = () => ({ jenis: 'tawaran', pemasok: '', kelas: '', merek: '', hargaPerKg: '', ongkirPerKg: '', sampaiToko: false, catatan: '', sumber: BC.BC_SUMBER_BAWAAN[0], tingkat: 'grosir', mutu: 'medium', wilayah: '' });
const ubKelas = (st) => (st === 'disetujui' ? 'lunas' : st === 'ditolak' ? 'awas' : 'tunggu');
const ubStatus = { menunggu: 'menunggu owner', disetujui: 'dicatat owner', ditolak: 'ditolak' };

/** Kartu usul (Penjaga laci saja). s.ub = draf; opsi = { akun }. */
export function kartuUsulBanding(s, opsi) {
  const d = Object.assign(UB_DRAF_KOSONG(), s.ub || {}); const taw = d.jenis === 'tawaran'; const U = BC.bcUsulSaya(opsi.akun); let calon = []; try { calon = calonPemasok() || []; } catch (e) { calon = []; }
  const isian = (kolom, judul, ph, angka) => h`<div><div class="ket">${judul}</div><input class="ketik-nama" type="text" ${angka ? 'inputmode="numeric"' : ''} value="${d[kolom] || ''}" placeholder="${ph || ''}" data-ketik="ubKetik" data-kolom="${kolom}" data-k="ub-i-${kolom}"></div>`;
  const pil = (kolom, daftar) => h`<div class="jalur bungkus rapat" data-k="ub-pil-${kolom}">${daftar.map(([v, nm]) => h`<div class="seg ${String(d[kolom]) === String(v) ? 'aktif' : ''}" data-aksi="ubPilih" data-kolom="${kolom}" data-v="${v}">${nm}</div>`)}</div>`;
  const baris = (b) => h`<div class="tp-baris ${ubKelas(b.status)}" data-k="ub-${b.id}"><div style="min-width: 0;"><div>${b.teks}</div><div class="k2">${tanggalPendek(b.tanggal)} ${b.jam} · <b>${ubStatus[b.status] || b.status}</b></div>${b.alasan ? h`<div class="k2 awas-teks">Alasan owner: ${b.alasan}</div>` : ''}</div></div>`;
  return h`<div class="kartu" data-k="ub-kartu" style="gap: 8px;"><div class="label">Harga dari pemasok lain · usul ke owner${U.menunggu.length ? ' · ' + U.menunggu.length + ' menunggu' : ''}</div>
    <div class="ket">Pemasok menawarkan harga tapi tidak jadi dibeli? Catat di sini — owner membandingkan minimal 3 pemasok tiap minggu.</div>
    <div class="tombol-baris" data-k="ub-jenis">${BC.BC_JENIS.map(([id, nm]) => h`<div class="kaca-btn ${d.jenis === id ? 'aktif' : ''}" data-aksi="ubPilih" data-kolom="jenis" data-v="${id}">${nm}</div>`)}</div>
    ${taw ? h`<div class="ps-form tiga">${isian('pemasok', 'Pemasok', 'nama pemasok')}${isian('kelas', 'Kelas / jenis beras', 'mis. IR64 medium')}${isian('merek', 'Merek (boleh kosong)', '')}</div>
        ${calon.length ? h`<div class="jalur bungkus rapat" data-k="ub-calon">${calon.slice(0, 8).map((p) => h`<div class="seg ${d.pemasok === p ? 'aktif' : ''}" data-aksi="ubPilih" data-kolom="pemasok" data-v="${p}">${p}</div>`)}</div>` : ''}
        <div class="ps-form tiga">${isian('hargaPerKg', 'Harga per kg', '12.900', true)}${d.sampaiToko ? h`<div><div class="ket">Ongkos kirim</div><div class="k2" style="padding-top: 8px;">sudah termasuk</div></div>` : isian('ongkirPerKg', 'Ongkos kirim per kg (kosong = belum tahu)', '', true)}${isian('catatan', 'Catatan', 'mis. minimal 5 ton')}</div>
        <div class="seg ${d.sampaiToko ? 'aktif' : ''}" data-aksi="ubSampai" style="align-self: flex-start;">${d.sampaiToko ? '✓ ' : ''}harga sudah sampai toko</div>`
      : h`${pil('sumber', BC.BC_SUMBER_BAWAAN.map((x) => [x, x]))}${pil('tingkat', BC.BC_TINGKAT)}${pil('mutu', BC.BC_MUTU)}<div class="ps-form tiga">${isian('hargaPerKg', 'Harga per kg', '13.100', true)}${isian('wilayah', 'Wilayah', 'nasional / provinsi')}${isian('catatan', 'Catatan', '')}</div>`}
    <div class="kaca-btn aktif emas" data-aksi="ubKirim" data-k="ub-kirim">KIRIM USUL KE OWNER</div>
    ${U.menunggu.length || U.riwayat.length ? h`<div class="label" data-k="ub-daftar">Usul dari akun ini</div>${U.menunggu.concat(U.riwayat).slice(0, 8).map(baris)}` : ''}</div>`;
}

/** Aksi panel — digabung ke AKSI layar Menu. tulis(r) = penulis layar; waktu() = { tanggal, jam, kini, idUnik }. */
export function aksiUsulBanding({ set, st, tulis, akun, waktu }) {
  const draf = () => Object.assign(UB_DRAF_KOSONG(), st().ub || {}); const ubah = (p) => set({ ub: Object.assign(draf(), p) }); const ak = () => (akun ? akun() : null);
  return {
    ubPilih: ({ kolom, v }) => ubah({ [kolom]: kolom === 'pemasok' && draf().pemasok === v ? '' : v }),
    ubSampai: () => ubah({ sampaiToko: !draf().sampaiToko, ongkirPerKg: '' }),
    ubKetik: (v, el) => { const k = el.dataset.kolom; ubah({ [k]: String(v).slice(0, k === 'catatan' ? 160 : 60) }); },
    ubKirim: async () => { const d = draf(); if (await tulis(BC.bcSusunUsul(d.jenis, d, ak(), waktu()))) set({ ub: Object.assign(UB_DRAF_KOSONG(), { jenis: d.jenis }) }); },
  };
}
