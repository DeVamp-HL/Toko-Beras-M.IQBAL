// Panel JURNAL BERPASANGAN (owner 26 Nov 2026, modul ERP no. 69) — Laporan › Jurnal. Angka = jurnal-logika.js (turunan dari catatan yang ada + koreksi owner);
// panel ini hanya menggambar & meneruskan ketukan. Satu-satunya tulisan: entri koreksi owner (aturanToko/jurnalKoreksi, susunKoreksi / susunHapusKoreksi).
// Gerak: Σ debit & Σ kredit bergulir (data-gulir), pita debit/kredit per akun tumbuh (lebar ber-transisi), baris & entri masuk bergiliran (--urut), lampu penjaga
// berganti warna saat datanya berubah.
import { h } from '../inti/dom.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { JR_AKUN, JR_KEL, JR_AKUN_KOREKSI, JR_JENIS, jrAkun, jrBulan, jrBukuBesar, jrBarisTampil, jrKoreksi, susunKoreksi, susunHapusKoreksi } from './jurnal-logika.js';

export const JR_TAB = [['saldo', 'Neraca saldo'], ['entri', 'Entri'], ['besar', 'Buku besar'], ['cocok', 'Cocokkan'], ['koreksi', 'Koreksi owner']];
const JR_HAL = 40;
const jrpNilai = (r, f) => (r.normal === 'D' ? r[f] : -r[f]);   // saldo di sisi normal akun (harta & beban: debit; kewajiban, modal, pendapatan: kredit)
const jrpDrafKosong = (t) => ({ id: '', tanggal: t, ket: '', baris: [{ akun: 'labaKoreksi', d: '', k: '' }, { akun: 'utangLain', d: '', k: '' }] });

function jrpLampu(B) {
  const J = B.J, Lb = B.Lb, C = B.C;
  const l = [['seimbang', J.seimbang && J.menutup, 'Σ debit = Σ kredit', J.seimbang ? (J.menutup ? RP(J.debit) : 'saldo tidak menutup') : J.nTidakSeimbang + ' entri tidak seimbang'],
    ['laba', Lb.cocok, 'Laba jurnal = Laporan', Lb.cocok ? RP(Lb.laba) + (Lb.koreksi ? ' (koreksi ' + RP(Lb.koreksi) + ')' : '') : 'beda ' + RP(Lb.beda)],
    ['uang', C.uangCocok, 'Uang = tempat uang', C.uangAda ? (C.uangCocok ? 'empat tempat cocok' : C.uang.filter((u) => !u.cocok).map((u) => u.nama).join(', ')) : 'belum ada patokan'],
    ['neraca', C.bersamaCocok && C.pecahCocok !== false, 'Neraca = Laporan', C.bersamaCocok ? (C.selisihBuku === null ? 'baris sama' : 'beda buku terurai') : C.bersama.filter((r) => r.laporan !== null && !r.cocok).map((r) => r.nama).join(', ')]];
  return h`<div class="jr-lampu" data-k="jr-lampu">${l.map((x) => h`<div class="${x[1] ? 'hijau' : 'merah'}" data-aksi="jrTab" data-t="cocok" data-k="jl-${x[0]}"><i></i><span>${x[2]}</span><b>${x[3]}</b></div>`)}</div>`;
}
function jrpSaldo(B) {
  const rows = B.J.baris.filter((r) => r.awal || r.debit || r.kredit || r.akhir); const maks = Math.max(1, ...rows.map((r) => Math.max(r.debit, r.kredit))); let urut = 0;
  return h`<div class="kartu" data-k="jr-saldo" style="gap: 4px;"><div class="label">Neraca saldo · ${tanggalPendek(B.dari)} s.d. ${tanggalPendek(B.sampai)} · saldo di sisi normal akun</div>
    <div class="jr-kepala"><span>Akun</span><span>Awal</span><span>Debit</span><span>Kredit</span><span>Akhir</span></div>
    ${JR_KEL.map(([kel, nama]) => { const r = rows.filter((x) => x.kel === kel); return r.length ? h`<div class="jr-kel" data-k="jk-${kel}">${nama}</div>${r.map((x) => h`<div class="jr-akun ${x.sifat}" style="--urut: ${Math.min(urut++, 18)};" data-aksi="jrAkun" data-a="${x.akun}" data-k="ja-${x.akun}">
      <span>${x.nama}${x.sifat === 'khusus' ? h` <em>hanya di jurnal</em>` : x.sifat === 'penyesuaian' ? h` <em>penjelas beda</em>` : ''}</span><span>${RP(jrpNilai(x, 'awal'))}</span><span>${x.debit ? RP(x.debit) : '—'}</span><span>${x.kredit ? RP(x.kredit) : '—'}</span><b>${RP(jrpNilai(x, 'akhir'))}</b>
      <div class="jr-pita"><i class="d" style="width: ${Math.round(x.debit / maks * 100)}%;"></i><i class="k" style="width: ${Math.round(x.kredit / maks * 100)}%;"></i></div></div>`)}` : ''; })}
    <div class="jr-akun jumlah" data-k="ja-jumlah"><span>Jumlah mutasi</span><span></span><span data-gulir="${B.J.debit}">${RP(B.J.debit)}</span><span data-gulir="${B.J.kredit}">${RP(B.J.kredit)}</span><b>${B.J.seimbang ? 'seimbang' : 'TIDAK seimbang'}</b></div>
    <div class="k2">${B.nEntri} entri · laba bulan ini menurut jurnal ${RP(B.Lb.laba)} (Laporan ${RP(B.Lb.laporan)}${B.Lb.koreksi ? ', koreksi owner ' + RP(B.Lb.koreksi) : ''}). Ketuk akun untuk buku besarnya.</div></div>`;
}
function jrpEntri(B, s) {
  const semua = B.J.entri.filter((e) => !s.jenisJr || e.k === s.jenisJr).slice().reverse(); const hal = Math.max(0, Math.min(s.halJr || 0, Math.floor(Math.max(0, semua.length - 1) / JR_HAL))); const tampil = semua.slice(hal * JR_HAL, hal * JR_HAL + JR_HAL);
  return h`<div class="kartu" data-k="jr-entri" style="gap: 4px;"><div class="label">Entri · terbaru di atas · ${semua.length} entri${s.jenisJr ? ' ' + (JR_JENIS[s.jenisJr] || s.jenisJr) : ''}</div>
    <div class="jalur rapat" data-k="jr-jenis" style="flex-wrap: wrap;"><div class="seg ${s.jenisJr ? '' : 'aktif'}" data-aksi="jrJenis" data-j="" data-k="jj-semua">semua</div>${B.perJenis.map((x) => h`<div class="seg ${s.jenisJr === x.k ? 'aktif' : ''}" data-aksi="jrJenis" data-j="${x.k}" data-k="jj-${x.k}">${x.nama} · ${x.n}</div>`)}</div>
    ${tampil.map((e, i) => h`<div class="jr-entri" style="--urut: ${Math.min(i, 14)};" data-k="je-${e.k}-${e.id}"><div class="jr-entri-kepala"><span>${e.t ? tanggalPendek(e.t) : 'tanpa tanggal'}${e.j && /^\d\d:\d\d/.test(e.j) ? ' ' + e.j.slice(0, 5) : ''}</span><span class="pg-cap">${JR_JENIS[e.k] || e.k}</span><span class="ket">${e.ket}</span></div>
      ${jrBarisTampil(e).map((r) => h`<div class="jr-baris ${r.kredit ? 'kredit' : ''}"><span>${r.nama}</span><span>${r.debit ? RP(r.debit) : ''}</span><span>${r.kredit ? RP(r.kredit) : ''}</span></div>`)}</div>`)}
    ${semua.length > JR_HAL ? h`<div style="display: flex; gap: 6px; align-items: center;"><div class="kaca-btn kecil ${hal ? '' : 'redup'}" data-aksi="jrHal" data-n="${hal - 1}">‹ lebih baru</div><span class="k2">${hal * JR_HAL + 1}–${Math.min(semua.length, hal * JR_HAL + JR_HAL)} dari ${semua.length}</span><div class="kaca-btn kecil ${(hal + 1) * JR_HAL < semua.length ? '' : 'redup'}" data-aksi="jrHal" data-n="${hal + 1}">lebih lama ›</div></div>` : ''}</div>`;
}
function jrpBesar(B, s) {
  const pakai = B.J.baris.filter((r) => r.awal || r.debit || r.kredit || r.akhir); const akun = pakai.some((r) => r.akun === s.akunJr) ? s.akunJr : (pakai[0] || { akun: 'laci' }).akun; const BB = jrBukuBesar(akun, B.dari, B.sampai); const a = BB.akun; const tanda = a.normal === 'D' ? 1 : -1;
  return h`<div class="kartu" data-k="jr-besar" style="gap: 4px;"><div class="label">Buku besar · ${a.nama} · saldo di sisi ${a.normal === 'D' ? 'debit' : 'kredit'}</div>
    <select class="ketik-nama" data-ketik="jrAkunPilih" data-k="jr-besar-pilih">${pakai.map((r) => h`<option value="${r.akun}" ${r.akun === akun ? 'selected' : ''}>${r.nama}</option>`)}</select>
    <div class="jr-baris awal"><span>Saldo awal ${tanggalPendek(B.dari)}</span><span></span><b data-gulir="${tanda * BB.awal}">${RP(tanda * BB.awal)}</b></div>
    ${BB.baris.slice(-120).map((r, i) => h`<div class="jr-buku" style="--urut: ${Math.min(i, 14)};"><span>${r.t ? tanggalPendek(r.t) : '—'}</span><span class="ket">${r.ket}</span><span>${r.debit ? RP(r.debit) : ''}</span><span>${r.kredit ? RP(r.kredit) : ''}</span><b>${RP(tanda * r.saldo)}</b></div>`)}
    ${BB.baris.length > 120 ? h`<div class="k2">${BB.baris.length - 120} baris lebih lama tidak ditampilkan (saldo awal tetap benar).</div>` : ''}
    <div class="jr-baris awal"><span>Saldo akhir ${tanggalPendek(B.sampai)}</span><span></span><b data-gulir="${tanda * BB.akhir}">${RP(tanda * BB.akhir)}</b></div>${BB.cocok ? '' : h`<div class="pita-info awas">Saldo berjalan tidak sama dengan saldo akhir — laporkan.</div>`}</div>`;
}
function jrpCocok(B) {
  const C = B.C; const ok = (b) => (b ? 'hijau' : 'merah'); const maks = Math.max(1, ...C.pecahan.map((r) => Math.abs(r.n)));
  return h`<div class="kartu" data-k="jr-cocok-uang" style="gap: 2px;"><div class="label">Uang per tempat · jurnal vs tempat uang (${C.uangAda ? 'patokan ' + tanggalPendek(B.J.akhir.patokan.tanggal) : 'belum ada patokan'})</div>
      ${C.uang.map((u) => h`<div class="jr-cek ${ok(u.cocok)}" data-k="jcu-${u.id}"><span>${u.nama}</span><span>${RP(u.jurnal)}</span><span>${u.mesin === null ? '—' : RP(u.mesin)}</span></div>`)}</div>
    <div class="kartu" data-k="jr-cocok-neraca" style="gap: 2px;"><div class="label">Neraca ${tanggalPendek(B.sampai)} · jurnal vs Laporan › Neraca</div>
      ${C.bersama.map((r, i) => h`<div class="jr-cek ${r.laporan === null ? '' : ok(r.cocok)}" data-k="jcn-${i}"><span>${r.nama}</span><span>${RP(r.jurnal)}</span><span>${r.laporan === null ? 'belum bisa dihitung' : RP(r.laporan)}</span></div>`)}
      ${C.khusus.length ? h`<div class="label" style="margin-top: 4px;">Hanya di jurnal</div>${C.khusus.map((r) => h`<div class="jr-cek" data-k="jck-${r.akun}"><span>${r.nama}${r.n < 0 && r.kel === 'kewajiban' ? ' (minus = sudah dibayar lebih dulu dari jatahnya)' : ''}</span><span>${RP(r.n)}</span><span>${r.kel}</span></div>`)}` : ''}</div>
    <div class="kartu" data-k="jr-cocok-laba" style="gap: 2px;"><div class="label">Laba ${B.nama} · jurnal vs Laporan › Laba</div>
      <div class="jr-cek ${ok(B.Lb.cocok)}"><span>Laba bersih</span><span data-gulir="${B.Lb.laba}">${RP(B.Lb.laba)}</span><span>${RP(B.Lb.laporan)}${B.Lb.koreksi ? ' + koreksi ' + RP(B.Lb.koreksi) : ''}</span></div>
      ${B.Lb.rinci.filter((r) => r.n).map((r) => h`<div class="jr-baris"><span>${r.nama}</span><span></span><span>${RP(r.n)}</span></div>`)}</div>
    <div class="kartu" data-k="jr-cocok-beda" style="gap: 4px;"><div class="label">Beda "belum terjelaskan buku" di Neraca ${C.selisihBuku === null ? '· belum bisa dihitung' : RP(C.selisihBuku) + ' = …'}</div>
      ${C.pecahan.map((r, i) => h`<div class="jr-pecah" style="--urut: ${Math.min(i, 12)};" data-k="jp-${i}"><span>${r.nama}</span><b class="${r.n < 0 ? 'rugi' : ''}" data-gulir="${r.n}">${RP(r.n)}</b><div class="lp-pita"><span style="width: ${Math.round(Math.abs(r.n) / maks * 100)}%;"></span></div></div>`)}
      ${C.selisihBuku === null ? '' : h`<div class="jr-cek ${ok(C.pecahCocok)}"><span>Jumlah</span><span>${RP(C.pecahanJumlah)}</span><span>${C.pecahCocok ? 'menutup' : 'tidak menutup'}</span></div>`}
      <div class="k2">Neraca Laporan menulis laba ditahan sebagai sisa (harta − utang − modal) lalu menyebut bedanya dengan laba kumulatif. Jurnal memecah beda itu jadi baris bernama: posisi awal saat mulai mencatat, uang yang dihitung ulang, stok yang dinilai harga modal terakhir, penjualan tanpa modal, upah & biaya yang belum dibayar, dan seterusnya.${C.bedaBuku ? ' Sisa yang belum bisa dijelaskan: ' + RP(C.bedaBuku) + ' (beda buku pembantu).' : ''}</div></div>`;
}
function jrpKoreksi(s, kini) {
  const K = jrKoreksi(); const d = s.drafJk; const sd = d ? d.baris.reduce((a, r) => a + (Number(String(r.d).replace(/\D/g, '')) || 0), 0) : 0, sk = d ? d.baris.reduce((a, r) => a + (Number(String(r.k).replace(/\D/g, '')) || 0), 0) : 0;
  const form = d ? h`<div class="kartu lp-lembar jr-lembar" data-k="jr-lembar" style="gap: 6px;"><div class="kepala-lembar"><div class="serif" style="font-size: 18px;">${d.id ? 'Ubah koreksi' : 'Entri koreksi owner'}</div><div class="kaca-btn" data-aksi="jkTutup">tutup</div></div>
      <div class="k2">Untuk penyesuaian yang tidak lewat layar mana pun (mis. saran konsultan: biaya yang lupa dicatat, pendapatan lain). Hanya akun laba, utang lain, harta lain, dan koreksi modal; uang, stok, bon, utang pemasok & modal owner dicatat lewat layarnya sendiri. Koreksi ikut neraca & laba JURNAL — laba di Laporan tidak berubah.</div>
      <div class="lp-kb-form" data-k="jk-form"><label for="jkTanggal"><div>Tanggal</div><div class="k2">bulan yang masih terbuka</div></label><input id="jkTanggal" class="ketik-nama" type="date" max="${s.hariJr}" value="${d.tanggal}" data-ketik="jkKetik" data-kolom="tanggal">
        <label for="jkKet"><div>Alasan</div><div class="k2">wajib</div></label><input id="jkKet" class="ketik-nama" type="text" maxlength="120" value="${d.ket}" data-ketik="jkKetik" data-kolom="ket"></div>
      ${d.baris.map((r, i) => h`<div class="jr-form-baris" data-k="jkb-${i}"><select class="ketik-nama" data-ketik="jkAkun" data-i="${i}">${JR_AKUN_KOREKSI.map((id) => h`<option value="${id}" ${r.akun === id ? 'selected' : ''}>${jrAkun(id).nama}</option>`)}</select>
        <input id="jkD${i}" class="ketik-nama" type="text" inputmode="numeric" placeholder="debit" value="${r.d}" data-ketik="jkBaris" data-i="${i}" data-kolom="d"><input id="jkK${i}" class="ketik-nama" type="text" inputmode="numeric" placeholder="kredit" value="${r.k}" data-ketik="jkBaris" data-i="${i}" data-kolom="k">
        ${d.baris.length > 2 ? h`<div class="kaca-btn kecil" data-aksi="jkBuang" data-i="${i}">×</div>` : ''}</div>`)}
      <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;"><div class="kaca-btn kecil" data-aksi="jkTambah">+ baris</div><span class="${sd === sk && sd > 0 ? 'k2' : 'k2 awas-teks'}" data-k="jk-imbang">debit ${RP(sd)} · kredit ${RP(sk)}${sd === sk && sd > 0 ? ' · seimbang' : ' · belum seimbang'}</span></div>
      <div style="display: flex; gap: 8px;"><div class="utama ${sd === sk && sd > 0 ? '' : 'redup'}" data-aksi="jkSimpan">SIMPAN</div>${d.id ? h`<div class="kaca-btn ${s.yakinJk === d.id ? 'awas' : ''}" data-aksi="jkHapus" data-id="${d.id}">${s.yakinJk === d.id ? 'yakin hapus?' : 'hapus'}</div>` : ''}</div></div>` : '';
  return h`<div class="kartu" data-k="jr-koreksi" style="gap: 4px;"><div class="label">Entri koreksi owner · ${K.entri.length} entri</div>
    ${K.entri.slice().reverse().map((e, i) => h`<div class="jr-entri" style="--urut: ${Math.min(i, 14)};" data-aksi="jkUbah" data-id="${e.id}" data-k="jke-${e.id}"><div class="jr-entri-kepala"><span>${tanggalPendek(e.tanggal)}</span><span class="pg-cap">koreksi</span><span class="ket">${e.ket}</span></div>
      ${e.baris.map((r) => h`<div class="jr-baris ${r.k ? 'kredit' : ''}"><span>${(jrAkun(r.akun) || { nama: r.akun }).nama}</span><span>${r.d ? RP(r.d) : ''}</span><span>${r.k ? RP(r.k) : ''}</span></div>`)}</div>`)}
    ${K.entri.length ? '' : h`<div class="k2">Belum ada koreksi. Jurnal di atas seluruhnya turunan dari catatan toko.</div>`}
    ${K.nBuang ? h`<div class="pita-info awas">${K.nBuang} entri koreksi cacat (akun tak dikenal / tidak seimbang) tidak dipakai.</div>` : ''}
    ${d ? '' : h`<div class="kaca-btn aktif emas" data-aksi="jkBaru" style="align-self: flex-start;">+ entri koreksi</div>`}</div>${form}`;
}

/** Laporan › Jurnal. daftar = daftarBulan (pilihan bulan); grid = penyusun kolom layar Laporan. */
export function gambarJurnal(s, L, kini, daftar, grid) {
  const key = s.bulanJr && daftar.some((b) => b.key === s.bulanJr) ? s.bulanJr : daftar[0].key; const B = jrBulan(key, kini); const tab = JR_TAB.some((t) => t[0] === s.tabJr) ? s.tabJr : 'saldo';
  const pilih = h`<div class="kartu" data-k="jr-bulan" style="gap: 6px;"><div class="label">Jurnal berpasangan · turunan dari catatan toko · tiap kejadian dua sisi</div>
    <div class="jalur rapat" data-k="jr-bulan-pilih" style="flex-wrap: wrap;">${daftar.slice(0, 12).map((b) => h`<div class="seg ${b.key === key ? 'aktif' : ''}" data-aksi="jrBulan" data-b="${b.key}" data-k="jb-${b.key}">${b.pendek}</div>`)}</div>
    ${B.tolak ? h`<div class="pita-info">${B.tolak}.</div>` : jrpLampu(B)}</div>`;
  if (B.tolak) return h`<section data-k="jurnal">${pilih}</section>`;
  const tabs = h`<div class="jalur rapat" data-k="jr-tab">${JR_TAB.map(([id, nm]) => h`<div class="seg ${tab === id ? 'aktif' : ''}" data-aksi="jrTab" data-t="${id}" data-k="jt-${id}">${nm}</div>`)}</div>`;
  const isi = tab === 'entri' ? jrpEntri(B, s) : tab === 'besar' ? jrpBesar(B, s) : tab === 'cocok' ? jrpCocok(B) : tab === 'koreksi' ? jrpKoreksi(s, kini) : jrpSaldo(B);
  const kaki = h`<div class="lp-kaki">Jurnal ini DISUSUN dari catatan yang sudah ada (nota, bon, retur, kasbon, modal, barang masuk, bon pemasok, upah & biaya bulanan, uang keluar, pindah uang, amplop, tutup hari, susut, aset tetap) — tidak ada catatan baru, mesin uang tidak diubah. Laba jurnal = Laporan › Laba; uang = isi tempat uang; neraca = Laporan › Neraca, dan beda "belum terjelaskan" di sana dipecah jadi baris bernama. Koreksi owner hanya mengubah jurnal.</div>`;
  if (L === 'hp') return h`<section data-k="jurnal">${pilih}${tabs}${isi}${kaki}</section>`;
  return h`<section data-k="jurnal">${pilih}${tabs}${grid(L, [isi, tab === 'cocok' ? kaki : h`${jrpCocok(B)}${kaki}`])}</section>`;   // layar lebar: cocokkan selalu terlihat di kanan
}

/** Ketukan panel jurnal. */
export function aksiPanelJurnal({ set, st, tulis, waktu, kini, iso }) {
  const ubah = (f) => { const d = JSON.parse(JSON.stringify(st().drafJk || jrpDrafKosong(iso()))); f(d); set({ drafJk: d, yakinJk: null }); };
  return {
    jrKeCocok: () => set({ keluarga: 'jurnal', tabJr: 'cocok', bulanJr: null, kabar: '' }),   // dari Laporan › Neraca: pecahan beda "belum terjelaskan"
    jrBulan: ({ b }) => set({ bulanJr: b, halJr: 0, kabar: '' }), jrTab: ({ t }) => set({ tabJr: t, kabar: '' }), jrJenis: ({ j }) => set({ jenisJr: j || '', halJr: 0 }), jrHal: ({ n }) => set({ halJr: Math.max(0, Number(n) || 0) }),
    jrAkun: ({ a }) => set({ akunJr: a, tabJr: 'besar' }), jrAkunPilih: (v) => set({ akunJr: String(v) }),
    jkBaru: () => set({ drafJk: jrpDrafKosong(iso()), yakinJk: null, hariJr: iso(), kabar: '' }), jkTutup: () => set({ drafJk: null, yakinJk: null }),
    jkUbah: ({ id }) => { const e = jrKoreksi().entri.find((x) => x.id === id); if (e) set({ drafJk: { id: e.id, tanggal: e.tanggal, ket: e.ket, baris: e.baris.map((r) => ({ akun: r.akun, d: r.d ? String(r.d) : '', k: r.k ? String(r.k) : '' })) }, yakinJk: null, hariJr: iso(), kabar: '' }); },
    jkKetik: (v, el) => ubah((d) => { d[el.dataset.kolom] = String(v).slice(0, 120); }), jkAkun: (v, el) => ubah((d) => { const r = d.baris[Number(el.dataset.i)]; if (r) r.akun = String(v); }),
    jkBaris: (v, el) => ubah((d) => { const r = d.baris[Number(el.dataset.i)]; if (r) r[el.dataset.kolom] = String(v).slice(0, 16); }),
    jkTambah: () => ubah((d) => { if (d.baris.length < 12) d.baris.push({ akun: 'labaKoreksi', d: '', k: '' }); }), jkBuang: ({ i }) => ubah((d) => { if (d.baris.length > 2) d.baris.splice(Number(i), 1); }),
    jkSimpan: async () => { const d = st().drafJk; if (!d) return; const r = susunKoreksi(d, waktu(), kini()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    jkHapus: async ({ id }) => { const r = susunHapusKoreksi(id, waktu(), st().yakinJk === id); if (r.perluYakin) return set({ yakinJk: id, kabar: r.tolak, kabarAwas: false }); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
  };
}
