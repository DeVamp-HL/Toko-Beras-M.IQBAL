// PANEL PESANAN — B4 pesanan, PO & order rutin (owner 18 Nov 2026). Dipakai layar Jual: lembar Pesanan = pengingat jadwal rutin yang belum dibuat, cek stok
// pesanan & jadwal 14 hari, pesanan aktif (antar, catat jual, ubah, uang muka, batal — DP pilih jadi saldo / dikembalikan), sudah jadi nota, form pesanan
// dari KATALOG (+ jadwal rutin), daftar jadwal. Logika & angka di pesanan-logika.js / jual-logika.js — panel ini hanya menggambar & meneruskan ketukan.
// Bikin & ubah = kisi SS2 'pesanan' (owner + Ben; rules v11); karyawan melihat & tetap bisa "catat jualnya".
import { h } from '../inti/dom.js';
import { RP, tanggalPendek, hariIniIso } from '../inti/format.js';
import * as PO from './pesanan-logika.js';
import { tombolAkun, bukanOwner } from './akses-layar.js';
import { tulisDokumen, kabarKiriman } from '../data/toko.js';
import { daftarBarang } from './stok-logika.js';

const KABAR_PERMISI = 'Server belum membuka pesanan & jadwal rutin untuk tablet (rules v11 — diterbitkan owner di Firebase Console). Sesudah terbit, coba lagi.';
const PS_STATUS = { dipesan: 'DIPESAN', diantar: 'DIANTAR', dibayar: 'JADI NOTA', batal: 'BATAL' };
const jumlahTeks = (n) => String(Math.round((Number(n) || 0) * 100) / 100).replace('.', ',');

/**
 * ctx = { set, S (keadaan Jual), akun(), waktu() ({ tanggal, jam, kini, idUnik }), rak() (rak Jual yang sedang tampil), hargaBaris(chip, jumlah, nama) → rupiah
 *         (harga pembeli itu: eceran / tingkat), jadiNota(saring, hari) (jual-logika daftarPesananJadiNota) }.
 */
export function buatPanelPesanan(ctx) {
  const set = ctx.set; const S = ctx.S; const akun = () => (ctx.akun ? ctx.akun() : null);
  const hari = () => hariIniIso(S().sekarang || new Date());
  const boleh = () => tombolAkun(akun(), 'pesanan');
  const owner = () => !bukanOwner(akun());
  const tahan = () => { const tb = boleh(); if (!tb.boleh) { set({ kabar: tb.kalimat, kabarAwas: true }); return true; } return false; };
  async function tulis(r, sesudah) {
    if (!r || r.tolak) return set({ kabar: (r && r.tolak) || 'Tidak ada yang ditulis', kabarAwas: true });
    try {
      const x = await tulisDokumen(r.dokumen || []);
      if (x && x.gagal) return set({ kabar: 'DITOLAK: ' + (/permission/i.test(x.pesan || '') ? KABAR_PERMISI : x.pesan), kabarAwas: true });
      set(Object.assign({}, r.patch, sesudah || {}, { kabar: kabarKiriman(x, r.patch.kabar), kabarAwas: !!r.patch.kabarAwas }));
    } catch (e) { set({ kabar: 'GAGAL menulis: ' + (e && e.message ? e.message : e), kabarAwas: true }); }
  }
  const draf = () => S().psDraf;
  const ubahDraf = (o) => { const d = draf(); if (d) set({ psDraf: Object.assign({}, d, o) }); };
  const hargaDraf = (d) => (b) => { const c = PO.poChipCocok(ctx.rak(), b); return c ? ctx.hargaBaris(c, b.jumlah, d.nama) : 0; };
  const chipDari = (p) => { if (!p) return null; const daftar = ctx.rak()[p.jalur] || []; return daftar.find((c) => String(c.kunci) === String(p.kunci) && (p.jalur !== 'karung' || String(c.berat) === String(p.berat))) || null; };
  const formKosong = { psPilih: null, psCari: '', psJumlah: '' };
  const PANJANG = { nama: 40, noPO: PO.PO_NO_MAKS + 1, tanggalKirim: 10, alamat: 120, catatan: PO.PO_CATATAN_MAKS };

  const aksi = {
    // ---- form pesanan
    psBaru: () => { if (tahan()) return; set(Object.assign({ psDraf: PO.poDrafBaru(S().psSaring), psBuka: null }, formKosong)); },
    psUbah: ({ id }) => { if (tahan()) return; const ps = PO.poAmbil(id); if (!ps) return set({ kabar: 'Pesanan tidak ditemukan', kabarAwas: true }); set(Object.assign({ psDraf: PO.poDrafDariPesanan(ps), psBuka: null }, formKosong)); },
    psDariJadwal: ({ id, tgl }) => { if (tahan()) return; const j = PO.poJadwalSemua().find((x) => x.id === String(id)); if (!j) return; set(Object.assign({ psDraf: PO.poDrafDariJadwal(j, tgl), psBuka: null }, formKosong)); },
    psTutupForm: () => set(Object.assign({ psDraf: null }, formKosong)),
    psKetik: (v, el) => { const k = el && el.dataset ? el.dataset.kolom : ''; const d = draf(); if (!PANJANG[k] || !d || (k === 'nama' && d.id)) return; const o = {}; o[k] = String(v || '').slice(0, PANJANG[k]); set({ psDraf: Object.assign({}, d, o) }); },
    psCari: (v) => set({ psCari: String(v || '').slice(0, 30), psPilih: null }),
    psPilihChip: ({ jalur, kunci, berat }) => { const p = { jalur, kunci, berat: berat || '' }; if (chipDari(p)) set({ psPilih: p, psJumlah: '' }); },
    psJumlah: (v) => set({ psJumlah: String(v || '').replace(/[^\d,.]/g, '').slice(0, 8) }),
    psTambah: () => {
      const s = S(); const d = s.psDraf; if (!d || !s.psPilih) return; const c = chipDari(s.psPilih); if (!c) return set({ kabar: 'Barang itu tidak ada di rak lagi', kabarAwas: true });
      const r = PO.poBarisDariChip(c, s.psJumlah); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true });
      const t = PO.poTaruhBaris(d.baris, r.baris); if (t.tolak) return set({ kabar: t.tolak, kabarAwas: true });
      set(Object.assign({ psDraf: Object.assign({}, d, { baris: t.baris }), kabar: '' }, formKosong));
    },
    psBuangBaris: ({ k2 }) => { const d = draf(); if (d) ubahDraf({ baris: d.baris.filter((b) => PO.poKunciBaris(b) !== k2) }); },
    psRutin: () => { const d = draf(); if (!d || d.id || d.dariJadwal) return;
      ubahDraf({ jadwal: d.jadwal && d.jadwal.nyala ? null : { nyala: true, ulang: 'mingguan', hari: PO.poHariMinggu(d.tanggalKirim && PO.poTanggalSah(d.tanggalKirim) ? d.tanggalKirim : hari()), tanggalBulan: '' } }); },
    psUlang: ({ u }) => { const d = draf(); if (d && d.jadwal && PO.PO_ULANG[u]) ubahDraf({ jadwal: Object.assign({}, d.jadwal, { ulang: u }) }); },
    psHari: ({ n }) => { const d = draf(); if (d && d.jadwal) ubahDraf({ jadwal: Object.assign({}, d.jadwal, { hari: Number(n) }) }); },
    psTglBulan: (v) => { const d = draf(); if (d && d.jadwal) set({ psDraf: Object.assign({}, d, { jadwal: Object.assign({}, d.jadwal, { tanggalBulan: String(v || '').replace(/\D/g, '').slice(0, 2) }) }) }); },
    psSimpan: () => { const d = draf(); if (!d || tahan()) return; tulis(PO.poSusunPesanan(d, ctx.waktu(), { harga: hargaDraf(d) }), Object.assign({ psDraf: null }, formKosong)); },
    // ---- uang muka
    psDpBuka: ({ id }) => { if (tahan()) return; set({ psBuka: { id: String(id), mode: 'dp' }, psDp: '', psDpCara: 'Tunai', psDraf: null }); },
    psDpKetik: (v) => set({ psDp: String(v || '').slice(0, 15) }),
    psDpCara: ({ c }) => set({ psDpCara: c === 'QRIS' ? 'QRIS' : 'Tunai' }),
    psDpSimpan: () => { const s = S(); if (!s.psBuka || tahan()) return; tulis(PO.poSusunUangMuka(PO.poAmbil(s.psBuka.id), s.psDp, s.psDpCara, ctx.waktu()), { psBuka: null, psDp: '' }); },
    // ---- batal (uang muka: jadi saldo / dikembalikan tunai — owner)
    psBatalBuka: ({ id }) => { if (tahan()) return; set({ psBuka: { id: String(id), mode: 'batal' }, psNasib: '', psAlasan: '', psDraf: null }); },
    psNasib: ({ n }) => { if (n === 'kembali' && !owner()) return set({ kabar: 'Mengembalikan uang muka = uang keluar dari laci — owner yang mencatatnya. Pilih "jadi saldo pelanggan", atau minta owner.', kabarAwas: true });
      set({ psNasib: n === 'kembali' ? 'kembali' : 'saldo' }); },
    psAlasan: (v) => set({ psAlasan: String(v || '').slice(0, 120) }),
    psBatalSimpan: () => { const s = S(); if (!s.psBuka || tahan()) return; tulis(PO.poSusunBatal(PO.poAmbil(s.psBuka.id), s.psNasib, s.psAlasan, ctx.waktu(), { owner: owner() }), { psBuka: null, psNasib: '', psAlasan: '' }); },
    psTutupBuka: () => set({ psBuka: null }),
    // ---- jadwal rutin
    psLewati: ({ id, tgl }) => { if (tahan()) return; tulis(PO.poSusunLewati(id, tgl, ctx.waktu())); },
    psRutinDaftar: () => set({ psRutinBuka: !S().psRutinBuka }),
    psJadwalAktif: ({ id, a }) => { if (tahan()) return; tulis(PO.poSusunJadwalAktif(id, a === '1', ctx.waktu())); },
  };

  // ---------- gambar ----------
  function gambarForm(s) {
    const d = s.psDraf; const rak = ctx.rak(); const cari = String(s.psCari || '').trim().toLowerCase(); const H = hargaDraf(d);
    const calon = cari ? PO.PO_JALUR.reduce((a, j) => a.concat(rak[j] || []), []).filter((c) => (c.nama + ' ' + (c.ukuran || '')).toLowerCase().indexOf(cari) >= 0).slice(0, 14) : [];
    const pilih = chipDari(s.psPilih); const P0 = s.psPilih; const dipilih = (c) => !!P0 && c.jalur === P0.jalur && String(c.kunci) === String(P0.kunci) && (c.jalur !== 'karung' || String(c.berat) === String(P0.berat)); const total = d.baris.reduce((a, b) => a + (H(b) || 0), 0); const J = d.jadwal && d.jadwal.nyala ? d.jadwal : null;
    return h`<div class="ps-form" data-k="ps-form">
      <div class="judul">${d.id ? 'Ubah pesanan' : d.dariJadwal ? 'Pesanan dari jadwal rutin · kirim ' + tanggalPendek(d.tanggalKirim) : 'Pesanan baru'}</div>
      <input class="ketik-nama" id="psFNama" type="text" value="${d.nama}" data-ketik="psKetik" data-kolom="nama" placeholder="Nama pemesan" ${d.id ? 'disabled' : ''}>
      <input class="ketik-nama" id="psFPO" type="text" value="${d.noPO}" data-ketik="psKetik" data-kolom="noPO" placeholder="No. PO dari pelanggan (boleh kosong)">
      <div class="label">Tanggal kirim</div>
      <input class="ketik-nama" id="psFTgl" type="date" value="${d.tanggalKirim}" data-ketik="psKetik" data-kolom="tanggalKirim">
      <input class="ketik-nama" id="psFAlamat" type="text" value="${d.alamat}" data-ketik="psKetik" data-kolom="alamat" placeholder="Alamat antar (boleh kosong)">
      <div class="label">Barang dari katalog${d.baris.length ? ' · ' + d.baris.length : ''}</div>
      ${d.isiLama ? h`<div class="ket">Isi lama (ditulis bebas): ${d.isiLama} — pilih barangnya dari katalog di bawah.</div>` : ''}
      <div class="daftar-nama" data-k="ps-f-baris">${d.baris.map((b) => h`<div class="baris-ps" data-k="psb-${PO.poKunciBaris(b)}"><span>${jumlahTeks(b.jumlah)} ${b.jalur === 'literan' ? 'L' : b.satuan} · ${b.nama}</span>
        <span class="ket">${H(b) ? RP(H(b)) : 'harga tidak terbaca'}</span> <span class="pil" data-aksi="psBuangBaris" data-k2="${PO.poKunciBaris(b)}" data-k="psbx-${PO.poKunciBaris(b)}">×</span></div>`)}${d.baris.length ? '' : h`<div class="ket">Belum ada barang — cari mereknya di bawah.</div>`}</div>
      <input class="ketik-nama" id="psFCari" type="text" value="${s.psCari || ''}" data-ketik="psCari" placeholder="cari barang: merek / ukuran (mis. IR64, 5 kg)">
      ${calon.length ? h`<div class="ps-pil" data-k="ps-f-calon">${calon.map((c) => h`<span class="pil ${dipilih(c) ? 'utamaKecil' : ''}" data-aksi="psPilihChip" data-jalur="${c.jalur}" data-kunci="${c.kunci}" data-berat="${c.jalur === 'karung' ? c.berat : ''}">${c.nama} · ${c.jalur === 'literan' ? '' : c.jalur + ' '}${c.ukuran || ''} · ${RP(c.harga)}</span>`)}</div>`
        : cari ? h`<div class="ket">Tidak ada barang rak yang cocok dengan "${s.psCari}".</div>` : ''}
      ${pilih ? h`<div class="ps-jumlah" data-k="ps-f-jumlah"><b>${pilih.nama} ${pilih.ukuran || ''}</b>
        <input class="ketik-nama" id="psFJumlah" type="text" inputmode="decimal" value="${s.psJumlah || ''}" data-ketik="psJumlah" data-enter="psTambah" placeholder="${pilih.jalur === 'karung' ? 'berapa karung' : pilih.jalur === 'kemasan' ? 'berapa kemasan' : 'berapa liter'}">
        <div class="kaca-btn aktif" data-aksi="psTambah">+ tambah</div></div>` : ''}
      ${d.baris.length ? h`<div class="ket" data-k="ps-f-total">perkiraan ${RP(total)} (harga ${d.nama ? d.nama : 'eceran'} hari ini — nota memakai harga saat dicatat)</div>` : ''}
      <input class="ketik-nama" id="psFCatatan" type="text" value="${d.catatan}" data-ketik="psKetik" data-kolom="catatan" placeholder="Catatan (boleh kosong)">
      ${!d.id && !d.dariJadwal ? h`<div class="kaca-btn ${J ? 'aktif' : ''}" data-aksi="psRutin" data-k="ps-f-rutin">${J ? '✓ ' : ''}ulangi sebagai order rutin</div>
        ${J ? h`<div class="ps-pil" data-k="ps-f-ulang">${Object.keys(PO.PO_ULANG).map((u) => h`<span class="pil ${J.ulang === u ? 'utamaKecil' : ''}" data-aksi="psUlang" data-u="${u}">${PO.PO_ULANG[u]}</span>`)}</div>
          ${J.ulang === 'bulanan' ? h`<input class="ketik-nama" id="psFBulanKe" type="text" inputmode="numeric" value="${J.tanggalBulan}" data-ketik="psTglBulan" placeholder="tanggal kirim tiap bulan (1–28; kosong = tanggal kirim di atas)">`
          : h`<div class="ps-pil" data-k="ps-f-hari">${PO.PO_HARI.map((n, i) => h`<span class="pil ${Number(J.hari) === i ? 'utamaKecil' : ''}" data-aksi="psHari" data-n="${i}">${n.slice(0, 3)}</span>`)}</div>`}
          <div class="ket">Jadwal cuma memunculkan PENGINGAT ${PO.poHariIngat()} hari sebelum tanggal kirim (Pesanan & Dasbor); pesanannya tetap dibuat dengan ketukan.</div>` : ''}` : ''}
      <div class="tombol-baris"><div class="utama ${d.baris.length && d.nama ? '' : 'redup'}" data-aksi="psSimpan">${d.id ? 'SIMPAN UBAHAN' : 'CATAT PESANAN'}</div><div class="kaca-btn" data-aksi="psTutupForm">batal</div></div>
    </div>`;
  }
  function formBuka(s, o) {
    const B = s.psBuka; if (!B || B.id !== o.id) return '';
    if (B.mode === 'dp') return h`<div class="ps-form" data-k="ps-dp-form">
      <input class="ketik-nama" id="psFDp" type="text" inputmode="numeric" value="${s.psDp || ''}" data-ketik="psDpKetik" data-enter="psDpSimpan" placeholder="Uang muka Rp">
      <div class="tombol-baris">${['Tunai', 'QRIS'].map((c) => h`<div class="kaca-btn ${s.psDpCara === c ? 'aktif' : ''}" data-aksi="psDpCara" data-c="${c}">${c}</div>`)}</div>
      <div class="ket">Uang pelanggan DIPEGANG toko, bukan omzet: masuk kas sekarang, notanya kelak dipotong sebesar ini.</div>
      <div class="tombol-baris"><div class="kaca-btn aktif" data-aksi="psDpSimpan">SIMPAN UANG MUKA</div><div class="kaca-btn" data-aksi="psTutupBuka">batal</div></div>
    </div>`;
    return h`<div class="ps-form" data-k="ps-batal-form">
      ${o.dp > 0 ? h`<div class="ket awas-teks">Pesanan ini punya uang muka ${RP(o.dp)} — pilih dulu uangnya diapakan:</div>
        <div class="tombol-baris"><div class="kaca-btn ${s.psNasib === 'saldo' ? 'aktif' : ''}" data-aksi="psNasib" data-n="saldo" data-k="ps-nasib-saldo">jadi saldo ${o.nama} (memotong belanja berikutnya)</div>
        <div class="kaca-btn ${s.psNasib === 'kembali' ? 'aktif' : ''} ${owner() ? '' : 'redup'}" data-aksi="psNasib" data-n="kembali" data-k="ps-nasib-kembali">kembalikan tunai dari laci${owner() ? '' : ' (owner)'}</div></div>` : ''}
      <input class="ketik-nama" id="psFAlasan" type="text" value="${s.psAlasan || ''}" data-ketik="psAlasan" placeholder="Alasan batal (boleh kosong)">
      <div class="tombol-baris"><div class="kaca-btn putus" data-aksi="psBatalSimpan">BATALKAN PESANAN</div><div class="kaca-btn" data-aksi="psTutupBuka">jangan</div></div>
    </div>`;
  }
  function kartu(s, o, tb) {
    const ket = [o.tanggalKirim ? 'kirim ' + tanggalPendek(o.tanggalKirim) : 'tanggal kirim belum ada', o.noPO ? 'PO ' + o.noPO : '', o.alamat, o.nilai ? 'perkiraan ' + RP(o.nilai) : '', o.rutin ? 'dari jadwal rutin' : ''].filter(Boolean).join(' · ');
    const r = tb.boleh ? '' : 'redup';
    return h`<div class="ps-kartu" data-k="ps-${o.id}">
      <div class="atas"><b>${o.nama}</b><span class="pil status-${o.status}">${PS_STATUS[o.status] || o.status}</span></div>
      <div class="isi">${o.isi}</div>
      <div class="ket">${ket}</div>
      ${o.dp > 0 ? h`<div class="ket" data-k="ps-dp-${o.id}"><b>uang muka ${RP(o.dp)}</b> — dipegang toko, memotong notanya</div>` : ''}
      ${o.catatan ? h`<div class="ket">${o.catatan}</div>` : ''}
      <div class="aksi">
        ${o.status === 'dipesan' ? h`<span class="pil ${r}" data-aksi="antarPesanan" data-id="${o.id}">→ antar</span>` : ''}
        ${s.pesananId === o.id ? h`<span class="pil utamaKecil" data-aksi="lepasPesanan">✓ terikat ke keranjang · lepas</span>` : h`<span class="pil utamaKecil" data-aksi="ikatPesanan" data-id="${o.id}">catat jualnya →</span>`}
        <span class="pil ${r}" data-aksi="psUbah" data-id="${o.id}">ubah</span>
        <span class="pil ${r}" data-aksi="psDpBuka" data-id="${o.id}" data-k="ps-dpbuka-${o.id}">+ uang muka</span>
        <span class="pil ${r}" data-aksi="psBatalBuka" data-id="${o.id}">batalkan</span>
      </div>
      ${formBuka(s, o)}
    </div>`;
  }
  function gambarLembar(s, muncul, kepala, L1) {
    const tb = boleh(); const Hr = hari();
    const ingat = PO.poPengingat(Hr); let stok = []; try { stok = PO.poCekStok(Hr, daftarBarang()); } catch (e) { stok = []; }
    const awas = stok.filter((x) => x.awas || !x.dikenal); const daftar = PO.poDaftarAktif(s.psSaring); const jadiNota = ctx.jadiNota(s.psSaring, Hr); const jadwal = PO.poJadwalSemua();
    return h`${L1}<div class="lembar ${muncul}" data-k="lembar-pesanan">
      ${kepala('Pesanan', 'BUKAN uang & BUKAN stok sampai notanya dicatat · dipesan → diantar → jadi nota → lunas · uang muka memotong notanya')}
      ${s.psDraf ? gambarForm(s) : h`<div class="kaca-btn aktif ${tb.boleh ? '' : 'redup'}" data-aksi="psBaru" data-k="ps-baru">+ pesanan baru (dari katalog)</div>`}
      ${ingat.length ? h`<div class="label" data-k="ps-ingat-label">Order rutin — perlu dibuat · ${ingat.length}</div>
        <div class="daftar-nama" data-k="ps-ingat">${ingat.map((x) => h`<div class="ps-kartu" data-k="psi-${x.jadwal.id}-${x.tanggal}">
          <div class="atas"><b>${x.jadwal.nama}</b><span class="pil ${x.hariLagi <= 0 ? 'status-diantar' : ''}">${x.kata}</span></div>
          <div class="isi">${x.jadwal.isi}</div>
          <div class="ket">${tanggalPendek(x.tanggal)} · ${PO.poKataJadwal(x.jadwal)}${x.jadwal.noPO ? ' · PO ' + x.jadwal.noPO : ''}</div>
          <div class="aksi"><span class="pil utamaKecil ${tb.boleh ? '' : 'redup'}" data-aksi="psDariJadwal" data-id="${x.jadwal.id}" data-tgl="${x.tanggal}">buat pesanannya →</span>
            <span class="pil ${tb.boleh ? '' : 'redup'}" data-aksi="psLewati" data-id="${x.jadwal.id}" data-tgl="${x.tanggal}">lewati sekali</span></div>
        </div>`)}</div>` : ''}
      ${awas.length ? h`<div class="label">Stok untuk pesanan & jadwal ${PO.PO_JENDELA_STOK_HARI} hari</div>
        <div class="daftar-nama" data-k="ps-stok">${awas.map((x) => h`<div class="ket ${x.awas ? 'awas-teks' : ''}" data-k="pss-${x.kunci}">${PO.poKataStok(x)}</div>`)}</div>`
        : stok.length ? h`<div class="ket" data-k="ps-stok-cukup">Stok cukup untuk ${stok.length} barang pesanan & jadwal ${PO.PO_JENDELA_STOK_HARI} hari ke depan (laju jual ikut dihitung).</div>` : ''}
      <input class="ketik-nama" id="psSaring" type="text" value="${s.psSaring}" data-ketik="psSaring" placeholder="saring nama pemesan">
      <div class="daftar-nama" data-k="ps-aktif">${daftar.map((o) => kartu(s, o, tb))}${daftar.length ? '' : h`<div class="ket" style="padding: 10px 4px;">${s.psSaring ? 'Tidak ada pesanan aktif atas nama itu.' : 'Belum ada pesanan aktif.'}</div>`}</div>
      ${jadiNota.length ? h`<div class="label" style="margin-top: 8px;">Sudah jadi nota · yang belum lunas + lunas 30 hari terakhir</div>
      <div class="daftar-nama" data-k="ps-jadi-nota">${jadiNota.map((o) => h`<div class="ps-kartu">
        <div class="atas"><b>${o.nama}</b><span class="pil ${o.uang.lunas ? '' : 'status-diantar'}">JADI NOTA · ${o.uang.lunas ? 'LUNAS' : 'BELUM LUNAS'}</span></div>
        <div class="isi">${o.isi}${o.alamat ? h` · <span class="ket">${o.alamat}</span>` : ''}</div>
        <div class="ket ${o.uang.lunas ? '' : 'awas-teks'}">nota ${tanggalPendek(o.uang.tanggal)} · ${o.uang.kata}</div>
      </div>`)}</div>` : ''}
      <div class="kaca-btn" data-aksi="psRutinDaftar" data-k="ps-rutin-daftar">jadwal order rutin · ${jadwal.filter((j) => j.aktif).length} jalan${jadwal.some((j) => !j.aktif) ? ' · ' + jadwal.filter((j) => !j.aktif).length + ' berhenti' : ''} ${s.psRutinBuka ? '▲' : '▼'}</div>
      ${s.psRutinBuka ? h`<div class="daftar-nama" data-k="ps-rutin">${jadwal.map((j) => h`<div class="ps-kartu ${j.aktif ? '' : 'redup'}" data-k="psj-${j.id}">
        <div class="atas"><b>${j.nama}</b><span class="pil">${j.aktif ? PO.poKataJadwal(j) : 'BERHENTI'}</span></div>
        <div class="isi">${j.isi}</div>
        <div class="ket">mulai ${tanggalPendek(j.mulai)}${j.noPO ? ' · PO ' + j.noPO : ''}${j.alamat ? ' · ' + j.alamat : ''}</div>
        <div class="aksi"><span class="pil ${tb.boleh ? '' : 'redup'}" data-aksi="psJadwalAktif" data-id="${j.id}" data-a="${j.aktif ? '0' : '1'}">${j.aktif ? 'hentikan' : 'jalankan lagi'}</span></div>
      </div>`)}${jadwal.length ? '' : h`<div class="ket" style="padding: 6px 4px;">Belum ada jadwal — centang "ulangi sebagai order rutin" waktu mencatat pesanan.</div>`}</div>` : ''}
    </div>`;
  }
  return { aksi, gambarLembar };
}
