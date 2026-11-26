// Panel ASET TETAP (owner 26 Nov 2026, modul ERP no. 70) — Laporan › Aset tetap. Angka & aturan = aset-tetap-logika.js; panel ini hanya menggambar & meneruskan
// ketukan. Tulisan: satu dokumen aturanToko/asetTetap (owner saja) lewat susunAset / susunHapusAset / susunAturAset. Gerak: nilai hari ini & bulan ini bergulir
// (data-gulir), pita nilai buku tiap barang menyusut (lebar ber-transisi), batang 12 bulan ke depan tumbuh, baris masuk bergiliran (--urut), asLembar meluncur masuk.
import { h } from '../inti/dom.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { AST_JENIS, AST_MULAI_BAWAAN, astAtur, astBacaDraf, astCalon, astHabis, astJenis, astPerBulan, astRingkas, astNamaBulan, susunAset, susunAturAset, susunHapusAset } from './aset-tetap-logika.js';

const asDrafKosong = () => ({ id: '', nama: '', jenis: 'kecil', harga: '', tanggalBeli: '', umurBulan: '', sisa: '', dariKeluar: '', catatan: '', bayar: 'owner' });
const asDrafDari = (a) => ({ id: a.id, nama: a.nama, jenis: a.jenis, harga: String(a.harga), tanggalBeli: a.tanggalBeli, umurBulan: String(a.umurBulan), sisa: a.sisa ? String(a.sisa) : '', dariKeluar: a.dariKeluar || '', catatan: a.catatan || '', bayar: a.dariKeluar ? 'toko' : 'owner' });
const asPersen = (a, b) => (b > 0 ? Math.max(0, Math.min(100, Math.round(a / b * 100))) : 0);

/** Lembar catat / ubah satu barang. */
function asLembar(s, kini) {
  const d = s.drafAs; const J = astJenis(d.jenis); const R = astBacaDraf(Object.assign({}, d, { dariKeluar: d.bayar === 'toko' ? d.dariKeluar : '' }), kini);
  const calon = d.bayar === 'toko' ? astCalon(s.cariAs, d.id, 24) : []; const pilih = d.bayar === 'toko' && d.dariKeluar ? calon.concat(astCalon('', d.id, 400)).find((c) => c.id === String(d.dariKeluar)) || null : null;
  const a = R.aset || null; const pratinjau = a ? 'Susut ±' + RP(astPerBulan(a)) + ' sebulan · habis disusutkan ' + tanggalPendek(astHabis(a)) + (a.sisa ? ' (sisa ' + RP(a.sisa) + ')' : '') + (R.tunjuk ? ' · laba ' + astNamaBulan(R.tunjuk.tanggal) + ' naik ' + RP(Math.min(a.harga, Math.round(Number(R.tunjuk.nominal) || 0))) + ' karena uang keluar itu bukan biaya lagi' : '') : R.tolak;
  return h`<div class="kartu lp-lembar as-lembar" data-k="as-lembar" style="gap: 8px;"><div class="kepala-lembar"><div class="serif" style="font-size: 18px;">${d.id ? 'Ubah aset' : 'Catat aset tetap'}</div><div class="kaca-btn" data-aksi="asTutup">tutup</div></div>
    <div class="lp-kb-form" data-k="as-form">
      <label for="asNama"><div>Nama barang</div><div class="k2">mis. timbangan duduk 150 kg, motor antar</div></label><input id="asNama" class="ketik-nama" type="text" maxlength="60" value="${d.nama}" data-ketik="asKetik" data-kolom="nama">
    </div>
    <div class="label">Jenis · umur bawaan</div>
    <div class="jalur rapat" data-k="as-jenis" style="flex-wrap: wrap;">${AST_JENIS.map((j) => h`<div class="seg ${d.jenis === j.id ? 'aktif' : ''}" data-aksi="asPilih" data-kolom="jenis" data-nilai="${j.id}" data-k="asj-${j.id}">${j.nama} · ${j.umurBulan / 12} th</div>`)}</div>
    <div class="k2">${J.contoh}</div>
    <div class="label">Dibeli pakai uang siapa?</div>
    <div class="jalur rapat" data-k="as-bayar" style="flex-wrap: wrap;"><div class="seg ${d.bayar === 'owner' ? 'aktif' : ''}" data-aksi="asPilih" data-kolom="bayar" data-nilai="owner" data-k="asb-owner">dibawa owner / sebelum sistem</div><div class="seg ${d.bayar === 'toko' ? 'aktif' : ''}" data-aksi="asPilih" data-kolom="bayar" data-nilai="toko" data-k="asb-toko">uang toko · sudah tercatat di Uang keluar</div></div>
    ${d.bayar === 'toko' ? h`<div class="k2">Pilih catatan Uang keluarnya (terbesar dulu) — catatan itu tidak jadi biaya lagi (laba bulannya naik), diganti penyusutan. Bulan yang sudah dikunci tidak bisa dipilih.</div>
      <input id="asCari" class="ketik-nama" type="text" placeholder="cari keterangan uang keluar (mis. timbangan)" value="${s.cariAs || ''}" data-ketik="asCari">
      ${pilih ? h`<div class="pita-info emas" data-k="as-pilihan">Dipilih: ${tanggalPendek(pilih.tanggal)} · ${pilih.keterangan} · ${RP(pilih.nominal)}${pilih.dompet ? ' · dompet owner' : ''}</div>` : ''}
      <div class="as-calon" data-k="as-calon">${calon.length ? calon.map((c, i) => h`<div class="as-calon-baris ${String(d.dariKeluar) === c.id ? 'aktif' : ''} ${c.terkunci || c.dipakai ? 'redup' : ''}" style="--urut: ${Math.min(i, 12)};" data-k="asc-${c.id}" ${c.terkunci || c.dipakai ? '' : h`data-aksi="asTunjuk" data-id="${c.id}" data-n="${c.nominal}"`}><span>${tanggalPendek(c.tanggal)} · ${c.keterangan}${c.terkunci ? ' · bulan terkunci' : c.dipakai ? ' · sudah aset "' + c.dipakai + '"' : ''}</span><b>${RP(c.nominal)}</b></div>`) : h`<div class="k2">Tidak ada uang keluar untuk toko yang cocok.</div>`}</div>` : ''}
    <div class="lp-kb-form" data-k="as-form2">
      <label for="asHarga"><div>Harga beli (rupiah)</div><div class="k2">${pilih ? 'paling besar ' + RP(pilih.nominal) + ' (nominal catatannya)' : 'harga saat dibeli, bukan harga sekarang'}</div></label><input id="asHarga" class="ketik-nama" type="text" inputmode="numeric" value="${d.harga}" data-ketik="asKetik" data-kolom="harga">
      <label for="asTanggal"><div>Tanggal beli</div><div class="k2">${pilih ? 'ikut tanggal catatan uang keluarnya' : 'boleh sebelum sistem mencatat'}</div></label><input id="asTanggal" class="ketik-nama" type="date" max="${s.hariAs}" value="${pilih ? pilih.tanggal : d.tanggalBeli}" ${pilih ? 'disabled' : ''} data-ketik="asKetik" data-kolom="tanggalBeli">
      <label for="asUmur"><div>Umur (bulan)</div><div class="k2">kosong = bawaan ${J.umurBulan} bulan (${J.umurBulan / 12} tahun)</div></label><input id="asUmur" class="ketik-nama" type="text" inputmode="numeric" placeholder="${J.umurBulan}" value="${d.umurBulan}" data-ketik="asKetik" data-kolom="umurBulan">
      <label for="asSisa"><div>Nilai sisa di akhir umur</div><div class="k2">kosong = bawaan 0 · garis lurus (rata tiap hari)</div></label><input id="asSisa" class="ketik-nama" type="text" inputmode="numeric" placeholder="0" value="${d.sisa}" data-ketik="asKetik" data-kolom="sisa">
      <label for="asCatatan"><div>Catatan</div><div class="k2">boleh kosong — nomor nota, toko tempat beli</div></label><input id="asCatatan" class="ketik-nama" type="text" maxlength="120" value="${d.catatan}" data-ketik="asKetik" data-kolom="catatan">
    </div>
    <div class="${a ? 'k2' : 'k2 awas-teks'}" data-k="as-pratinjau">${pratinjau}</div>
    <div style="display: flex; gap: 8px; flex-wrap: wrap;"><div class="utama ${a ? '' : 'redup'}" data-aksi="asSimpan" data-k="as-simpan">SIMPAN</div>${d.id ? h`<div class="kaca-btn ${s.yakinAs === d.id ? 'awas' : ''}" data-aksi="asHapus" data-id="${d.id}" data-k="as-hapus">${s.yakinAs === d.id ? 'yakin hapus?' : 'hapus dari daftar'}</div>` : ''}</div></div>`;
}

/** Laporan › Aset tetap. grid = penyusun kolom layar Laporan; asetLama = aturLaporan() (isian lama satu angka). */
export function gambarAset(s, L, kini, grid, asetLama) {
  const R = astRingkas(kini, asetLama); const P = R.P; let urut = 0;
  const hero = h`<div class="kartu hero" data-k="as-hero" style="gap: 4px;"><div class="label">Aset tetap · nilai hari ini (harga beli − penyusutan)</div>
    <div class="lp-besar ${P.n ? '' : 'kosong'}" ${P.n ? h`data-gulir="${P.buku}"` : ''}>${P.n ? RP(P.buku) : 'belum ada barang'}</div>
    ${P.n ? h`<div class="lp-pita" data-k="as-pita-total"><span style="width: ${asPersen(P.buku, P.harga)}%;"></span></div><div class="k2">${P.n} barang · harga beli ${RP(P.harga)} − penyusutan terkumpul ${RP(P.susut)}${P.sebelum ? ' (' + RP(P.sebelum) + ' di antaranya sebelum ' + tanggalPendek(R.mulai) + ', tidak memotong laba)' : ''}</div>` : h`<div class="k2">Catat timbangan, rak, etalase, mesin jahit karung, motor antar, renovasi — barang yang dipakai bertahun-tahun, bukan barang dagangan.</div>`}
    <div class="lp-status" data-k="as-status"><div>${R.belumMulai ? 'Mulai memotong laba' : 'Penyusutan ' + R.bulan.nama}<b ${R.belumMulai ? '' : h`data-gulir="${R.bulan.penuh}"`}>${R.belumMulai ? tanggalPendek(R.mulai) : RP(R.bulan.penuh)}</b></div><div>s.d. hari ini<b data-gulir="${R.bulan.sdHariIni}">${RP(R.bulan.sdHariIni)}</b></div><div>dari uang keluar<b data-gulir="${P.dariBiaya}">${RP(P.dariBiaya)}</b></div></div>
    <div style="display: flex; gap: 6px; flex-wrap: wrap;"><div class="kaca-btn aktif emas" data-aksi="asBaru" data-k="as-baru">+ catat aset</div><div class="kaca-btn kecil" data-aksi="asAturBuka" data-k="as-atur-buka">mulai memotong laba: ${tanggalPendek(R.mulai)}${R.mulaiBawaan ? ' (bawaan)' : ''} ›</div></div></div>`;
  const atur = s.aturAs ? h`<div class="kartu lp-lembar" data-k="as-atur" style="gap: 8px;"><div class="kepala-lembar"><div class="serif" style="font-size: 18px;">Mulai memotong laba</div><div class="kaca-btn" data-aksi="asAturTutup">tutup</div></div>
    <div class="k2">Penyusutan hari ini dan sesudahnya memotong laba bersih. Penyusutan sebelum tanggal ini tetap mengurangi nilai aset, tapi tidak memotong laba bulan mana pun. Bawaan ${tanggalPendek(AST_MULAI_BAWAAN)} (keputusan owner 26 Nov 2026). Bulan yang sudah dikunci tidak boleh ikut bergeser.</div>
    <input id="asMulai" class="ketik-nama" type="date" value="${s.aturAs.mulai}" data-ketik="asAturKetik"><div class="utama" data-aksi="asAturSimpan">SIMPAN</div></div>` : '';
  const lama = R.lama && !P.n ? h`<div class="pita-info" data-k="as-lama">Isian lama: aset tetap ${RP(R.lama.asetTetap)}${R.lama.asetKet ? ' (' + R.lama.asetKet + ')' : ''} masih dipakai Neraca sampai daftar ini punya satu barang — sesudah itu Neraca membaca daftar ini saja.</div>` : '';
  const hilang = R.tunjukHilang.length ? h`<div class="pita-info awas" data-k="as-hilang">${R.tunjukHilang.map((x) => '"' + x.nama + '"').join(', ')} menunjuk uang keluar yang sudah tidak ada / bukan biaya toko lagi — dihitung sebagai barang bawaan owner. Ubah barangnya untuk memilih catatan lain.</div>` : '';
  const depan = h`<div class="kartu" data-k="as-depan" style="gap: 6px;"><div class="label">Penyusutan 12 bulan ke depan · memotong laba bersih${R.belumMulai ? ' mulai ' + tanggalPendek(R.mulai) : ''}</div>
    <div class="lp-grafik" data-k="as-grafik">${R.depan.map((b) => h`<div class="${b.mulai ? '' : 'draf'} ${b.key === R.bulan.key ? 'aktif' : ''}" data-k="asg-${b.key}" title="${b.nama} · ${RP(b.n)}"><i style="height: ${Math.max(4, Math.round(b.n / R.maks * 100))}px;"></i><span>${b.nama.slice(0, 3)}</span></div>`)}</div>
    <div class="k2">Batang putus = bulan sebelum mulai memotong laba. Angka harian: Σ hari = bulan persis.</div></div>`;
  const daftar = h`<div class="kartu" data-k="as-daftar" style="gap: 2px;"><div class="label">Daftar aset · ketuk untuk mengubah</div>
    ${P.daftar.length ? P.daftar.map((a) => h`<div class="as-baris" style="--urut: ${Math.min(urut++, 14)};" data-aksi="asUbah" data-id="${a.id}" data-k="as-${a.id}">
      <div><div style="font-weight: 600;">${a.nama}</div><div class="k2">${astJenis(a.jenis).nama} · dibeli ${tanggalPendek(a.tanggalBeli)} · umur ${a.umurBulan} bulan${a.habis ? ' · sudah habis disusutkan' : ' · habis ' + tanggalPendek(astHabis(a))}</div>
        <div class="k2">${a.tunjuk ? 'dari uang keluar ' + tanggalPendek(a.tunjuk.tanggal) + ' (' + RP(a.tunjuk.n) + ') — bukan biaya lagi' : 'dibawa owner / dibeli sebelum sistem'} · ±${RP(a.perBulan)}/bulan</div>
        <div class="lp-pita" data-k="asp-${a.id}"><span style="width: ${asPersen(a.buku, a.harga)}%;"></span></div></div>
      <div class="n"><b data-gulir="${a.buku}">${RP(a.buku)}</b><div class="k2">dari ${RP(a.harga)}</div></div></div>`)
      : h`<div class="k2">Belum ada barang. Ketuk "+ catat aset".</div>`}
    ${astAtur().aset.length > P.daftar.length ? h`<div class="k2">${astAtur().aset.length - P.daftar.length} barang bertanggal beli sesudah hari ini tidak ditampilkan.</div>` : ''}</div>`;
  const kaki = h`<div class="lp-kaki">Aset tetap = barang toko yang dipakai bertahun-tahun. Harganya tidak jadi biaya sekaligus: dibagi rata sepanjang umurnya (garis lurus, per hari) — itu penyusutan, dan penyusutan memotong laba bersih seperti biaya lain, tanpa uang keluar. Barang yang dulu dibeli pakai uang toko dan sudah tercatat di Uang keluar bisa ditunjuk catatannya supaya tidak terhitung dua kali (biaya sekaligus + penyusutan). Neraca membaca nilai hari ini. Mesin uang beku tidak diubah; angka bulan yang sudah dikunci tidak boleh bergeser.</div>`;
  const kiri = h`${hero}${atur}${lama}${hilang}${s.drafAs ? asLembar(s, kini) : ''}`;
  if (L === 'hp') return h`<section data-k="aset">${kiri}${daftar}${depan}${kaki}</section>`;
  return h`<section data-k="aset">${grid(L, [kiri, h`${daftar}`, h`${depan}${kaki}`])}</section>`;
}

/** Ketukan panel aset tetap. */
export function aksiPanelAset({ set, st, tulis, waktu, kini, iso }) {
  const ubah = (f) => { const d = Object.assign({}, st().drafAs || asDrafKosong()); f(d); set({ drafAs: d, yakinAs: null }); };
  return {
    asBaru: () => set({ drafAs: asDrafKosong(), cariAs: '', yakinAs: null, hariAs: iso(), kabar: '' }),
    asUbah: ({ id }) => { const a = astAtur().aset.find((x) => x.id === id); if (a) set({ drafAs: asDrafDari(a), cariAs: '', yakinAs: null, hariAs: iso(), kabar: '' }); },
    asTutup: () => set({ drafAs: null, yakinAs: null, cariAs: '' }),
    asKetik: (v, el) => ubah((d) => { d[el.dataset.kolom] = String(v).slice(0, el.dataset.kolom === 'catatan' ? 120 : 60); }),
    asPilih: ({ kolom, nilai }) => ubah((d) => { d[kolom] = nilai; if (kolom === 'bayar' && nilai === 'owner') d.dariKeluar = ''; if (kolom === 'jenis') d.umurBulan = ''; }),
    asCari: (v) => set({ cariAs: String(v).slice(0, 40) }),
    asTunjuk: ({ id, n }) => ubah((d) => { if (String(d.dariKeluar) === String(id)) { d.dariKeluar = ''; return; } d.dariKeluar = String(id); const c = astCalon('', d.id, 400).find((x) => x.id === String(id)); if (c) { d.tanggalBeli = c.tanggal; if (!d.harga || Number(String(d.harga).replace(/\D/g, '')) > c.nominal) d.harga = String(n); if (!d.nama) d.nama = c.keterangan.slice(0, 60); } }),
    asSimpan: async () => { const d = st().drafAs; if (!d) return; const r = susunAset(Object.assign({}, d, { dariKeluar: d.bayar === 'toko' ? d.dariKeluar : '' }), waktu(), kini()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    asHapus: async ({ id }) => { const r = susunHapusAset(id, waktu(), st().yakinAs === id); if (r.perluYakin) return set({ yakinAs: id, kabar: r.tolak, kabarAwas: false }); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
    asAturBuka: () => set({ aturAs: st().aturAs ? null : { mulai: astAtur().mulai }, kabar: '' }),
    asAturTutup: () => set({ aturAs: null }),
    asAturKetik: (v) => set({ aturAs: { mulai: String(v) } }),
    asAturSimpan: async () => { const a = st().aturAs; if (!a) return; const r = susunAturAset(a, waktu()); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true }); await tulis(r); },
  };
}
