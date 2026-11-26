// Panel KALENDER KEPATUHAN (owner 26 Nov 2026, sensus ulang 1c A16 A38 A45): kartu kalender + Atur kalender & bentuk usaha (Laporan › Pajak, owner) dan kartu
// "sudah dikerjakan" satu butir (Menu › Pengingat, owner & Penjaga laci — rules v22). Isi & angka = patuh-logika.js; panel ini hanya menggambar & meneruskan ketukan.
// Tulisan: satu dokumen kepatuhanCek per tanda (susunCentangPatuh) dan setelan aturanToko/kepatuhan (susunAturPatuh, owner).
import { h } from '../inti/dom.js';
import { tanggalPendek } from '../inti/format.js';
import { PT_BATAS, PT_BELUM, PT_BENTUK, PT_CATAT, PT_ULANG, ptAtur, ptCocokPajak, ptKalender, susunAturPatuh, susunCentangPatuh } from './patuh-logika.js';

const KATA = { lewat: 'lewat', hariIni: 'hari ini', segera: 'segera', nanti: 'nanti', tanpaTanggal: 'tanpa tanggal', selesai: 'selesai', mati: 'mati' };
const drafDari = (A) => ({ butir: A.butir.map((b) => Object.assign({}, b, { hariSebelum: String(b.hariSebelum) })), usaha: JSON.parse(JSON.stringify(A.usaha)) });

/** Kartu tanda "sudah dikerjakan" satu butir (s.ptBuka = id butir yang dibuka, s.ptCatatan = catatan). */
export function kartuCentang(b, s) {
  if (!b) return '';
  return h`<div class="kartu pt-centang" data-k="pt-centang-${b.id}" style="gap: 6px;"><div style="font-weight: 700;">${b.nama} · ${b.teks}</div>${b.ket ? h`<div class="k2">${b.ket}</div>` : ''}
    ${b.akhir ? h`<div class="k2">terakhir dikerjakan ${tanggalPendek(b.akhir.tanggal)}${b.akhir.oleh ? ' oleh ' + b.akhir.oleh : ''}${b.akhir.catatan ? ' · ' + b.akhir.catatan : ''}</div>` : ''}
    ${b.tanpaTanggal ? h`<div class="k2 awas-teks">Belum punya tanggal — owner mengisinya di Laporan › Pajak › Kalender › Atur.</div>`
      : h`<input class="ketik-nama" type="text" maxlength="${PT_BATAS.catatan}" placeholder="${b.keadaan === 'lewat' ? 'Catatan WAJIB: kapan dikerjakan / nomor bukti' : 'Catatan (boleh kosong): nomor bukti, siapa yang mengurus'}" value="${s.ptCatatan || ''}" data-ketik="ptCatatan">
        <div class="kaca-btn aktif emas" data-aksi="ptCentang" data-id="${b.id}" data-periode="${b.periode || ''}">SUDAH DIKERJAKAN · ${b.periode || ''}</div>`}</div>`;
}

/** Kartu kalender (owner): semua butir + cek aturan bulanan + bentuk usaha + Atur. jenisWp & statusPkp = profil pajak (Laporan › Pajak) untuk dicocokkan. */
export function kartuKalender(s, kini, jenisWp, statusPkp) {
  const K = ptKalender(kini); const a = s.ptAtur; const cocok = ptCocokPajak(K.usaha, jenisWp, statusPkp); let urut = 0;
  const baris = (b) => h`<div class="pt-baris ${b.keadaan}" data-k="ptb-${b.id}" style="--urut: ${Math.min(urut++, 14)};"><div><div style="font-weight: 600;">${b.nama}${b.basi ? h` <span class="pg-cap awas">lewat 30 hari</span>` : ''}</div>
      <div class="k2">${b.teks}${b.akhir ? ' · terakhir ' + tanggalPendek(b.akhir.tanggal) + (b.akhir.oleh ? ' (' + b.akhir.oleh + ')' : '') : ''}</div>${b.ket ? h`<div class="k2">${b.ket}</div>` : ''}</div>
    <div class="n"><span class="pg-cap ${b.keadaan === 'lewat' ? 'awas' : ''}">${KATA[b.keadaan] || b.keadaan}</span>${!b.tanpaTanggal && !b.selesai && b.nyala ? h`<div class="tautan" data-aksi="ptBuka" data-id="${b.id}">tandai ›</div>` : ''}</div></div>
    ${s.ptBuka === b.id ? kartuCentang(b, s) : ''}`;
  const aturan = K.baris.filter((b) => b.kelompok === 'aturan'); const lain = K.baris.filter((b) => b.kelompok !== 'aturan');
  const bentuk = PT_BENTUK.find((x) => x.id === K.usaha.bentuk) || PT_BENTUK[0]; const catat = PT_CATAT.find((x) => x.id === K.usaha.catat) || PT_CATAT[0];
  return h`<div class="kartu pt-kalender" data-k="pt-kalender" style="gap: 6px;"><div class="label">Kalender kepatuhan${K.dariOwner ? '' : ' · isi bawaan'}</div>
    <div class="${K.perlu.some((x) => x.keadaan === 'lewat') ? 'pita-info awas' : 'k2'}" data-k="pt-ringkas">${K.kalimat}</div>
    ${lain.map(baris)}
    <div class="label" style="margin-top: 4px;">Cek aturan tiap bulan</div>${aturan.map(baris)}
    <div class="label" style="margin-top: 4px;">Bentuk usaha & kewajiban catat</div>
    <div class="k2" data-k="pt-usaha">${bentuk.nama} · ${catat.nama}${K.usaha.konfirmasi.tanggal ? ' · dikonfirmasi ke ' + (K.usaha.konfirmasi.ke || 'KPP / konsultan') + ' ' + tanggalPendek(K.usaha.konfirmasi.tanggal) + (K.usaha.konfirmasi.catatan ? ' (' + K.usaha.konfirmasi.catatan + ')' : '') : ''}</div>
    ${cocok.map((t, i) => h`<div class="k2 awas-teks" data-k="pt-cocok-${i}">${t}</div>`)}
    <div class="k2">Setor PPh final tiap tanggal 15 ada di atas (Pajak) dan di Pengingat. Ben bisa menandai "sudah dikerjakan" dari tablet (Menu › Toko ini › Pengingat). Push pagi 07.00 WIB ke HP / Mac owner & tablet Ben — bila fungsi server sudah dipasang (functions/pasang.sh).</div>
    ${a ? kartuAtur(a) : h`<div class="kaca-btn kecil" data-aksi="ptAturBuka" style="align-self: flex-start;" data-k="pt-atur-buka">Atur kalender & bentuk usaha ›</div>`}</div>`;
}

function kartuAtur(a) {
  const seg = (v, id, aksi, i, nama) => h`<span class="seg ${v === id ? 'aktif' : ''}" data-aksi="${aksi}" data-i="${i}" data-nilai="${id}">${nama}</span>`;
  const contoh = (u) => (u === 'tahunan' ? 'BB-HH, mis. 03-31' : u === 'sekali' ? 'TTTT-BB-HH' : 'tanggal 01–31');
  return h`<div class="kartu pt-atur" data-k="pt-atur" style="gap: 8px;"><div class="label">Atur kalender · angka & daftar owner</div>
    ${a.butir.map((b, i) => h`<div class="pt-atur-baris" data-k="pt-a-${i}"><div class="ps-form dua"><div><div class="ket">Nama</div><input class="ketik-nama" type="text" maxlength="${PT_BATAS.nama}" value="${b.nama}" data-ketik="ptAturKetik" data-i="${i}" data-kolom="nama"></div>
        <div><div class="ket">Tanggal (${contoh(b.ulang)}${b.id === 'spt' ? '; kosong = ikut bentuk usaha' : ''})</div><input class="ketik-nama" type="text" value="${b.tanggal}" data-ketik="ptAturKetik" data-i="${i}" data-kolom="tanggal"></div></div>
      <div class="hg-pil">${PT_ULANG.map((u) => seg(b.ulang, u.id, 'ptAturUlang', i, u.nama))}</div>
      <div class="ps-form dua"><div><div class="ket">Ingatkan … hari sebelum (0–${PT_BATAS.hariSebelum[1]})</div><input class="ketik-nama" type="text" inputmode="numeric" value="${b.hariSebelum}" data-ketik="ptAturKetik" data-i="${i}" data-kolom="hariSebelum"></div>
        <div><div class="ket">Keterangan (di mana mengeceknya)</div><input class="ketik-nama" type="text" maxlength="${PT_BATAS.ket}" value="${b.ket}" data-ketik="ptAturKetik" data-i="${i}" data-kolom="ket"></div></div>
      <div class="hg-pil"><span class="seg ${b.nyala !== false ? 'aktif' : ''}" data-aksi="ptAturNyala" data-i="${i}">${b.nyala !== false ? 'menyala' : 'mati'}</span><span class="seg" data-aksi="ptAturHapus" data-i="${i}">hapus butir</span></div></div>`)}
    <div class="kaca-btn kecil" data-aksi="ptAturTambah" style="align-self: flex-start;">+ tambah butir (izin lain, PBB, perpanjang sewa, …)</div>
    <div class="label">Bentuk usaha</div><div class="hg-pil" data-k="pt-a-bentuk">${PT_BENTUK.map((x) => h`<span class="seg ${a.usaha.bentuk === x.id ? 'aktif' : ''}" data-aksi="ptUsaha" data-kolom="bentuk" data-nilai="${x.id}">${x.nama}</span>`)}</div>
    <div class="label">Kewajiban catat</div><div class="hg-pil" data-k="pt-a-catat">${PT_CATAT.map((x) => h`<span class="seg ${a.usaha.catat === x.id ? 'aktif' : ''}" data-aksi="ptUsaha" data-kolom="catat" data-nilai="${x.id}">${x.nama}</span>`)}</div>
    <div class="ps-form dua"><div><div class="ket">Dikonfirmasi ke (KPP / konsultan)</div><input class="ketik-nama" type="text" maxlength="60" value="${a.usaha.konfirmasi.ke}" data-ketik="ptUsahaKetik" data-kolom="ke"></div>
      <div><div class="ket">Tanggal konfirmasi (TTTT-BB-HH)</div><input class="ketik-nama" type="text" value="${a.usaha.konfirmasi.tanggal}" data-ketik="ptUsahaKetik" data-kolom="tanggal"></div></div>
    <div><div class="ket">Catatan konfirmasi (tanpa NIK / NPWP)</div><input class="ketik-nama" type="text" maxlength="200" value="${a.usaha.konfirmasi.catatan}" data-ketik="ptUsahaKetik" data-kolom="catatan"></div>
    <div class="tombol-baris" style="grid-template-columns: 1fr 1fr;"><div class="kaca-btn" data-aksi="ptAturBuka">batal</div><div class="kaca-btn aktif emas" data-aksi="ptAturSimpan">SIMPAN KALENDER</div></div>
    <div class="k2">Keterangan bawaan menyebut tempat mengecek, bukan nasihat hukum atau pajak — yang belum dibaca langsung dari sumber resmi bertanda ${PT_BELUM}.</div></div>`;
}

/** Aksi panel. opsi = { set, st, tulis (r → Promise<bool>), waktu, kini }. */
export function aksiPanelPatuh({ set, st, tulis, waktu, kini }) {
  const ubah = (f) => { const a = JSON.parse(JSON.stringify(st().ptAtur || drafDari(ptAtur()))); f(a); set({ ptAtur: a }); };
  return {
    ptBuka: ({ id }) => set({ ptBuka: st().ptBuka === id ? null : id, ptCatatan: '', kabar: '' }),
    ptCatatan: (v) => set({ ptCatatan: String(v).slice(0, PT_BATAS.catatan) }),
    ptCentang: async ({ id, periode }) => { const r = susunCentangPatuh(id, periode, st().ptCatatan, waktu(), kini()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    ptAturBuka: () => set({ ptAtur: st().ptAtur ? null : drafDari(ptAtur()), kabar: '' }),
    ptAturKetik: (v, el) => ubah((a) => { const b = a.butir[Number(el.dataset.i)]; if (b) b[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'ket' ? PT_BATAS.ket : 60); }),
    ptAturUlang: ({ i, nilai }) => ubah((a) => { const b = a.butir[Number(i)]; if (b && b.ulang !== nilai) { b.ulang = nilai; b.tanggal = ''; } }),
    ptAturNyala: ({ i }) => ubah((a) => { const b = a.butir[Number(i)]; if (b) b.nyala = b.nyala === false; }),
    ptAturHapus: ({ i }) => ubah((a) => { a.butir.splice(Number(i), 1); }),
    ptAturTambah: () => ubah((a) => { a.butir.push({ id: '', nama: '', ulang: 'sekali', tanggal: '', hariSebelum: '30', ket: '', nyala: true }); }),
    ptUsaha: ({ kolom, nilai }) => ubah((a) => { a.usaha[kolom] = nilai || ''; }),
    ptUsahaKetik: (v, el) => ubah((a) => { a.usaha.konfirmasi = Object.assign({}, a.usaha.konfirmasi || {}); a.usaha.konfirmasi[el.dataset.kolom] = String(v).slice(0, 200); }),
    ptAturSimpan: async () => { const a = st().ptAtur; if (!a) return; const r = susunAturPatuh(a, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
  };
}
