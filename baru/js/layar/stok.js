// LAYAR STOK — GAMBAR & KETUKAN. Beranda Stok S9 (dikunci owner) + tab Wadah literan. Logika & angka di stok-logika.js.
// Layar dimorf (elemen hidup terus) → batang isi, gunung wadah, dan angka bertransisi; baris masuk bergiliran saat lahir.
import { h, mentah, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as S from './stok-logika.js';
import * as L from './jual-logika.js';
import { gambarWadah, gambarKarungStok } from './gambar.js';
import { panelIsiUlang, aksiPanelWadah } from './wadah-panel.js';
import { adeganIsiUlang } from './adegan.js';
import { gulirkan, sekali } from '../inti/gerak.js';
import { sumberData, dengarkan, tulisDokumen } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
};
const KUNCI_TAB = 'miqbal_baru_stok_tab';

export function pasangLayarStok(akar, opsi) {
  const tabAwal = (() => { try { return localStorage.getItem(KUNCI_TAB) || 'gudang'; } catch (e) { return 'gudang'; } })();
  const K = buatKeadaan({ tab: S.TAB_STOK.some((t) => t[0] === tabAwal) ? tabAwal : 'gudang', tanya: 'beli', kabar: '', kabarAwas: false, wadahAktif: null, isiW: null, krKetik: '', atur: null });
  const set = (p) => K.setel(p); const st = () => K.baca();
  let tampil = false; const kini = () => opsi.sekarang() || new Date();
  const waktu = () => L.waktuSekarang(opsi.sekarang() || undefined);

  async function tulis(r) {
    if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }
    try { const x = await tulisDokumen(r.dokumen); if (x && x.gagal) { set({ kabar: 'DITOLAK: ' + x.pesan, kabarAwas: true }); return false; }
      set(Object.assign({}, r.patch, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); return true; }
    catch (e) { set({ kabar: 'GAGAL menyimpan: ' + (e && e.message ? e.message : e), kabarAwas: true }); return false; }
  }
  const keranjangJual = () => ({ keranjang: opsi.keranjangJual().keranjang, antrean: opsi.keranjangJual().antrean });
  // mode "atur susunan": draf di keadaan layar; baru ditulis saat SIMPAN (satu dokumen berisi seluruh aturan)
  const drafAtur = () => { const a = L.aturWadah(); const t = (n) => String(n).replace('.', ','); return { penuh: t(a.penuhKg), puncak: t(a.puncakKg), ulang: t(a.isiUlangKg), takar: t(a.takarKg), daftar: a.daftar.slice(), resep: JSON.parse(JSON.stringify(a.resep)), pilih: null, resepUntuk: null }; };
  const ubahAtur = (f) => { const d = JSON.parse(JSON.stringify(st().atur || drafAtur())); f(d); set({ atur: d }); };
  delegasi(akar, Object.assign({
    tab: ({ t }) => { try { localStorage.setItem(KUNCI_TAB, t); } catch (e) { /* abaikan */ } set({ tab: t, kabar: '' }); },
    tanya: ({ id }) => set({ tanya: id }),
    mode: () => opsi.gantiMode(),
    tutupKabar: () => set({ kabar: '' }),
    pilihWadah: ({ merk }) => set({ wadahAktif: st().wadahAktif === merk ? null : merk, isiW: null, krKetik: '' }),
    bukaKarung: ({ merk }, el) => { sekali(el.closest('.kartu'), 'pegas', 520); tulis(L.susunBukaKarung(merk, waktu())); },
    krKetik: (v) => set({ krKetik: String(v).slice(0, 6) }),
    samakanKarung: async ({ merk }) => { if (await tulis(L.susunSamakanKarung(merk, st().krKetik, waktu()))) set({ krKetik: '' }); },
    bukaAtur: () => set({ atur: st().atur ? null : drafAtur(), wadahAktif: null }),
    aturPenuh: (v) => ubahAtur((d) => { d.penuh = String(v).slice(0, 6); }), aturPuncak: (v) => ubahAtur((d) => { d.puncak = String(v).slice(0, 6); }),
    aturUlang: (v) => ubahAtur((d) => { d.ulang = String(v).slice(0, 6); }), aturTakar: (v) => ubahAtur((d) => { d.takar = String(v).slice(0, 6); }),
    aturGeser: ({ i, arah }) => ubahAtur((d) => { d.daftar = L.geserWadah(d.daftar, Number(i), Number(arah)); d.pilih = null; }),
    aturPilih: ({ i }) => ubahAtur((d) => { d.pilih = d.pilih === Number(i) ? null : Number(i); d.resepUntuk = null; }),
    aturGanti: ({ i, merk }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.gantiBerasWadah(d.daftar, Number(i), merk); if (lama && lama !== merk) delete d.resep[lama]; d.pilih = null; }),
    aturLepas: ({ i }) => ubahAtur((d) => { const lama = d.daftar[Number(i)]; d.daftar = L.lepasWadah(d.daftar, Number(i)); delete d.resep[lama]; d.pilih = null; }),
    aturTambah: () => ubahAtur((d) => { d.pilih = d.daftar.length; d.resepUntuk = null; }),
    aturResep: ({ merk }) => ubahAtur((d) => { d.resepUntuk = d.resepUntuk === merk ? null : merk; d.pilih = null; if (!d.resep[merk]) d.resep[merk] = [{ merk, takar: 1 }]; }),
    aturResepTakar: ({ merk, j, arah }) => ubahAtur((d) => { const r = d.resep[merk]; if (!r || !r[Number(j)]) return; r[Number(j)].takar = Math.max(0, r[Number(j)].takar + Number(arah)); }),
    aturResepTambah: ({ merk, bahan }) => ubahAtur((d) => { const r = d.resep[merk] || (d.resep[merk] = [{ merk, takar: 1 }]); if (r.length < L.WADAH_MAKS_RESEP && !r.some((x) => x.merk === bahan)) r.push({ merk: bahan, takar: 1 }); }),
    simpanAtur: async () => { const d = st().atur; if (!d) return; const r = L.susunAturWadah({ penuhKg: d.penuh, puncakKg: d.puncak, isiUlangKg: d.ulang, takarKg: d.takar, daftar: d.daftar, resep: d.resep }, waktu()); if (await tulis(r)) set({ atur: null }); },
    lama: () => set({ kabar: 'Mencatat barang masuk, adukan, dan cocokkan stok masih lewat sistem lama — menyusul di putaran Stok berikutnya.', kabarAwas: false }),
  }, aksiPanelWadah({ set, st, tulis, keranjang: keranjangJual, waktu,
    sesudahCatat: (wadah, r) => { const hsl = r.hitung; adeganIsiUlang({ nama: wadah, keterangan: hsl.takar + ' takar · ' + DESIMAL(hsl.kg) + ' kg' + (hsl.banding ? ' · campur ' + hsl.banding : ''), serokan: Math.ceil(hsl.takar / 8), dari: hsl.wadah, ke: L.tinggiWadah(wadah, keranjangJual()) || hsl.wadah }); } })));

  function gambar() {
    if (!tampil) return;
    const s = st(); const sumber = sumberData(); const k = kini();
    pasang(akar, h`
      <div class="latar-bola"><div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Stok</div><div class="ket">${tanggalPendek(L.waktuSekarang(k).tanggal)} · ${sumber.jenis === 'firestore' ? opsi.statusRingkas() : sumber.jenis === 'cadangan' ? 'membaca cadangan' : 'belum tersambung'}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;"><div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'data toko' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div></div>
      </header>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : 'emas'}" data-k="kabar" data-aksi="tutupKabar" style="cursor: pointer;">${s.kabar}</div>` : ''}
      <div class="jalur" data-k="tab">${S.TAB_STOK.map(([id, nm]) => h`<div class="seg ${s.tab === id ? 'aktif' : ''}" data-aksi="tab" data-t="${id}">${nm}</div>`)}</div>
      ${s.tab === 'gudang' ? gambarGudang(s, k) : s.tab === 'wadah' ? gambarTabWadah(s) : s.tab === 'kapur' ? gambarKapur(k) : gambarKarantina()}
    `);
    gulirkan(akar, RP);
  }

  function gambarGudang(s, k) {
    const g = S.susunGudang(s.tanya, k); const j = g.jawab;
    return h`<section class="stok-gudang" data-k="gudang">
      <div class="tanya">${g.kartu.map((c) => h`<div class="kartu-t ${c.id === g.aktif ? 'aktif' : ''}" data-aksi="tanya" data-id="${c.id}"><div class="q">${c.q}</div>
        <div class="a ${c.awas ? 'awas' : ''}" ${c.angka !== undefined ? mentah('data-gulir="' + Math.round(c.angka) + '"') : ''}>${c.a}</div></div>`)}</div>
      <div class="kartu jawaban" data-k="jawab-${g.aktif}">
        <div class="label">${g.judul}</div>
        ${j.baris.length ? h`<div class="daftar-jawab">${j.baris.map((b, i) => h`<div class="jawab" data-k="${g.aktif}-${b.kunci}" style="--urut: ${Math.min(i, 16)};">
          <span class="kiri"><span class="nm">${b.nama}</span><span class="w">${b.ket}</span><span class="batang"><span class="isi-batang ${b.awas ? 'awas' : ''}" style="transform: scaleX(${Math.round(Math.max(0.02, Math.min(1, b.isi)) * 1000) / 1000});"></span></span></span>
          <span class="kanan"><span class="n ${b.awas ? 'awas' : ''}">${b.n}</span><span class="w">${b.nKet}</span></span></div>`)}</div>`
          : h`<div class="menolak" style="padding: 12px 0;">${j.kosong}</div>`}
        <div class="rumus">${j.rumus}</div>
        ${j.takTeks ? h`<div class="ket" style="font-size: 11.5px;">${j.takTeks}</div>` : ''}
      </div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="lama">Barang masuk</div><div class="kaca-btn" data-aksi="lama">Adukan</div><div class="kaca-btn" data-aksi="lama">Cocokkan</div></div>
    </section>`;
  }

  function gambarTabWadah(s) {
    const w = S.susunWadah(keranjangJual()); const a = w.atur; const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';
    const tumpukanTeks = (t) => (!t.adaBuku ? 'merek ini tidak ada di buku stok' : t.minus ? 'tumpukan gudang: buku KURANG ' + KG(-t.kg) + ' dari yang sudah di wadah & karung terbuka — cocokkan stok' : 'tumpukan gudang ±' + t.karung + ' karung (' + KG(t.kg) + ') · buku ' + KG(t.bukuKg) + (t.lengkap ? '' : ' · perkiraan, ada yang belum ditandai'));
    if (s.atur) return gambarAturWadah(s.atur, w);
    const aktif = w.daftar.find((x) => x.nama === s.wadahAktif) || null;
    return h`<section class="stok-wadah" data-k="wadah">
      <div class="pita-info">Tumpukan karung di gudang → satu karung terbuka di belakang wadah → kotak wadah → dijual per liter. Tiap takar isi ulang mengurangi karung di belakangnya; karungnya habis, satu karung baru diambil dari tumpukan.
        ${w.perluIsi ? w.perluIsi + ' wadah minta diisi ulang. ' : ''}${w.karungTipis ? w.karungTipis + ' karung di belakang hampir habis. ' : ''}${w.belumDitandai ? w.belumDitandai + ' wadah belum pernah ditandai isinya.' : ''}</div>
      <div class="petak-wadah" data-k="petak">${w.daftar.map((x, i) => h`<div class="kartu petak ${x.nama === s.wadahAktif ? 'dipilih' : ''} ${x.diketahui && x.perluIsi ? 'isi-ulang' : ''}" data-k="petak-${x.nama}" data-aksi="pilihWadah" data-merk="${x.nama}" style="--urut: ${i};">
        <div class="no">${x.no}</div>
        <div class="tumpuk-gambar"><div class="gambar-karung">${mentah(gambarKarungStok(x.karung))}</div><div class="gambar-kotak">${mentah(gambarWadah(x))}</div></div>
        <div class="nm">${x.nama}</div>
        <div class="ket">karung ${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}</div>
        <div class="ket">wadah ${x.diketahui ? '±' + KG(x.sisaKg) : '?'}</div>
      </div>`)}</div>
      <div class="kaca-btn" data-aksi="bukaAtur">Atur susunan, isi &amp; aturan wadah</div>
      ${aktif ? h`<div class="kartu rincian-wadah" data-k="rincian-${aktif.nama}">
        <div class="label">${aktif.no} · ${aktif.nama}${aktif.resep.length > 1 ? ' · campuran ' + aktif.resep.map((r) => r.takar).join(' : ') + ' — ' + aktif.resep.map((r) => r.merk).join(' : ') : ''}</div>
        <div class="baris-wadah"><div class="gambar-chip besar">${mentah(gambarKarungStok(aktif.karung))}</div>
          <div><div class="serif" style="font-size: 19px;">${aktif.karung.diketahui ? 'Karung di belakang ±' + KG(aktif.karung.sisaKg) : 'Karung di belakang belum ditandai'}</div>
            <div class="ket">${aktif.karung.diketahui ? 'dari 50 kg · terakhir ' + tanggalPendek(aktif.karung.sejakTanggal) + ' ' + aktif.karung.sejakJam + (aktif.karung.lewat ? ' · takar yang tercatat ' + KG(aktif.karung.lewat) + ' LEBIH dari isi karungnya — samakan' : '') : 'Buka satu karung baru dari tumpukan, atau ketik sisa karung yang sedang terbuka.'}</div>
            <div class="ket">${tumpukanTeks(aktif.tumpukan)}</div></div></div>
        <div class="tombol-baris rapat"><div class="kaca-btn ${aktif.karung.diketahui && aktif.karung.sisaKg > a.takarKg * 3 ? '' : 'aktif'}" data-aksi="bukaKarung" data-merk="${aktif.nama}">Buka 1 karung baru dari tumpukan</div>
          <input class="ketik-nama sempit" id="krKetik" type="text" inputmode="decimal" placeholder="sisa kg" value="${s.krKetik}" data-ketik="krKetik"><div class="kaca-btn" data-aksi="samakanKarung" data-merk="${aktif.nama}">samakan sisa karung</div></div>
        ${panelIsiUlang(aktif.nama, s, keranjangJual())}
      </div>` : h`<div class="ket" style="text-align: center;">Ketuk satu wadah untuk mengisi ulang atau menandai karungnya.</div>`}
      ${w.lain.length ? h`<div class="kartu" data-k="karung-lain" style="gap: 6px;"><div class="label">Karung terbuka lain · bahan campuran</div>
        ${w.lain.map((x) => h`<div class="jawab" data-k="kl-${x.nama}"><span class="kiri"><span class="nm">${x.nama}</span><span class="w">${tumpukanTeks(x.tumpukan)}</span></span>
          <span class="kanan"><span class="n">${x.karung.diketahui ? '±' + KG(x.karung.sisaKg) : '?'}</span><span class="w tautan" data-aksi="bukaKarung" data-merk="${x.nama}">buka karung baru</span></span></div>`)}</div>` : ''}
      <div class="kartu" data-k="atur-wadah" style="gap: 4px;"><div class="label">Aturan wadah ${a.dariOwner ? '· diatur owner ' + tanggalPendek(a.sejak) : '· bawaan'}</div>
        <div class="ket">rata sejajar bibir kotak ${DESIMAL(a.penuhKg)} kg · menggunung sampai ${DESIMAL(a.puncakKg)} kg · minta isi ulang saat tersisa ${DESIMAL(a.isiUlangKg)} kg · 1 takar ${DESIMAL(a.takarKg)} kg · ${a.daftar.length} wadah</div>
        <div class="ket">Ini alat ukur: buku stok tiap merek baru berkurang saat literannya TERJUAL, jadi isi ulang tidak memotong buku dua kali.</div></div>
    </section>`;
  }

  function gambarAturWadah(d, w) {
    const calonWadah = L.calonBerasWadah(d.daftar); const pos = d.pilih;
    return h`<section class="stok-wadah" data-k="wadah-atur">
      <div class="pita-info emas">Atur susunan: ‹ › memindah posisi kotak · ketuk nama untuk mengganti berasnya · "campuran" menyetel perbandingan takar bawaan. Belum tersimpan sampai SIMPAN.</div>
      <div class="petak-wadah atur" data-k="petak-atur">${d.daftar.map((m, i) => h`<div class="kartu petak ${pos === i ? 'dipilih' : ''}" data-k="pa-${m}">
        <div class="no">W${i + 1}</div><div class="nm tautan" data-aksi="aturPilih" data-i="${i}">${m}</div>
        <div class="geser"><div class="kaca-btn ${i === 0 ? 'mati' : ''}" data-aksi="aturGeser" data-i="${i}" data-arah="-1">‹</div><div class="kaca-btn ${i === d.daftar.length - 1 ? 'mati' : ''}" data-aksi="aturGeser" data-i="${i}" data-arah="1">›</div></div>
        <div class="ket tautan" data-aksi="aturResep" data-merk="${m}">${(d.resep[m] || []).filter((x) => x.takar > 0).length > 1 ? 'campuran ' + d.resep[m].filter((x) => x.takar > 0).map((x) => x.takar).join(' : ') : 'campuran'}</div>
      </div>`)}<div class="kartu petak putus ${pos === d.daftar.length ? 'dipilih' : ''}" data-k="pa-tambah" data-aksi="aturTambah"><div class="no">+</div><div class="nm">tambah wadah</div></div></div>
      ${pos !== null && pos !== undefined ? h`<div class="kartu" data-k="atur-pilih" style="gap: 8px;"><div class="label">${pos < d.daftar.length ? 'W' + (pos + 1) + ' sekarang ' + d.daftar[pos] + ' — ganti dengan beras mana?' : 'Wadah baru W' + (pos + 1) + ' — beras mana?'}</div>
        <div class="tombol-baris rapat">${calonWadah.length ? calonWadah.map((m) => h`<div class="kaca-btn" data-aksi="aturGanti" data-i="${pos}" data-merk="${m}">${m}</div>`) : h`<div class="ket">Semua beras literan sudah punya wadah.</div>`}</div>
        ${pos < d.daftar.length ? h`<div class="kaca-btn putus" data-aksi="aturLepas" data-i="${pos}">lepas W${pos + 1} — ${d.daftar[pos]} jadi diserok langsung dari karung</div>` : ''}</div>` : ''}
      ${d.resepUntuk && d.daftar.indexOf(d.resepUntuk) >= 0 ? (() => { const m = d.resepUntuk; const r = d.resep[m] || [{ merk: m, takar: 1 }]; const calon = L.calonCampur(r.map((x) => x.merk));
        return h`<div class="kartu" data-k="atur-resep" style="gap: 8px;"><div class="label">Campuran bawaan ${m} · perbandingan takar</div>
          ${r.map((x, j) => h`<div class="baris-takar" data-k="rs-${x.merk}"><span class="kiri"><span class="nm">${x.merk}</span></span>
            <span class="langkah"><div class="kaca-btn" data-aksi="aturResepTakar" data-merk="${m}" data-j="${j}" data-arah="-1">−</div><span class="n">${x.takar} <span class="ket">takar</span></span><div class="kaca-btn aktif" data-aksi="aturResepTakar" data-merk="${m}" data-j="${j}" data-arah="1">+</div></span></div>`)}
          ${r.length < L.WADAH_MAKS_RESEP ? h`<div class="ket">tambah merek ke campuran:</div><div class="tombol-baris rapat">${calon.map((b) => h`<div class="kaca-btn" data-aksi="aturResepTambah" data-merk="${m}" data-bahan="${b}">${b}</div>`)}</div>` : ''}</div>`; })() : ''}
      <div class="kartu" data-k="atur-angka" style="gap: 8px;"><div class="label">Angka wadah</div><div class="ps-form dua">
        <div><div class="ket">Rata sejajar bibir kotak (kg)</div><input class="ketik-nama" id="aturPenuh" type="text" inputmode="decimal" value="${d.penuh}" data-ketik="aturPenuh"></div>
        <div><div class="ket">Batas menggunung (kg)</div><input class="ketik-nama" id="aturPuncak" type="text" inputmode="decimal" value="${d.puncak}" data-ketik="aturPuncak"></div>
        <div><div class="ket">Minta isi ulang saat tersisa (kg)</div><input class="ketik-nama" id="aturUlang" type="text" inputmode="decimal" value="${d.ulang}" data-ketik="aturUlang"></div>
        <div><div class="ket">Isi satu takar / serok (kg)</div><input class="ketik-nama" id="aturTakar" type="text" inputmode="decimal" value="${d.takar}" data-ketik="aturTakar"></div></div></div>
      <div class="tombol-baris"><div class="kaca-btn" data-aksi="bukaAtur">batal</div><div class="kaca-btn aktif emas" data-aksi="simpanAtur">SIMPAN SUSUNAN &amp; ATURAN</div></div>
    </section>`;
  }

  function gambarKapur(k) {
    const p = S.susunKapur(k);
    return h`<section data-k="kapur"><div class="kartu" style="gap: 4px; padding: 10px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center;"><div class="label">Papan Kapur · perubahan stok hari ini</div><div class="ket" style="font-size: 11px;">${p.banyak} catatan</div></div>
      ${p.baris.length ? p.baris.map((x, i) => h`<div class="kapur ${x.jenis}" data-k="kp-${x.k}" style="--urut: ${Math.min(i, 16)};"><span class="w">${x.jam}</span><span class="isi-kapur">${x.isi}</span><span class="n">${x.n}</span></div>`) : h`<div class="menolak" style="padding: 12px 0;">Belum ada perubahan stok hari ini.</div>`}
    </div></section>`;
  }

  function gambarKarantina() {
    const q = S.susunKarantina();
    return h`<section data-k="karantina"><div class="kartu" style="gap: 8px; padding: 12px 14px;">
      <div class="label">Karantina · barang kembali yang belum diputuskan</div>
      ${q.baris.length ? h`<div class="pita-info awas">${q.baris.length} barang · ${DESIMAL(q.totalKg)} kg menunggu keputusan (layak jual / rework / kembali ke pemasok / buang) — memutuskannya masih lewat sistem lama.</div>
        ${q.baris.map((x) => h`<div class="jawab" data-k="q-${x.k}"><span class="kiri"><span class="nm">${x.nama}</span><span class="w">${tanggalPendek(x.tanggal)} · ${x.catatan}</span></span><span class="kanan"><span class="n">${DESIMAL(x.kg)} kg</span></span></div>`)}`
        : h`<div class="menolak">Karantina kosong — tidak ada barang kembali yang menunggu diputuskan.</div>`}
    </div></section>`;
  }

  K.dengar(gambar);
  dengarkan(() => gambar());
  return { gambar, tampilkan: (ya) => { const tadi = tampil; tampil = !!ya; if (tampil && !tadi) { akar.classList.remove('masuk'); void akar.offsetWidth; akar.classList.add('masuk'); setTimeout(() => akar.classList.remove('masuk'), 1200); } if (tampil) gambar(); } };
}
