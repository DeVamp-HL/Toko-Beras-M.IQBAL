// Panel TUTUP HARI di tablet (owner 22 Nov 2026, paket ④: kartu di Menu akun tablet, Penjaga laci). Logika & bentuk dokumen di tutup-tablet-logika.js;
// panel ini hanya menggambar, meneruskan ketukan, dan mencetak slip. Yang ditulis: HITUNGAN LACI berstatus "menunggu" (rules v16) dan cek wadah (rules v5,
// sudah ada). HITUNG BUTA — tidak ada angka seharusnya / selisih di layar ini; harinya ditutup owner dari HP (Uang › Tutup hari).
import { h } from '../inti/dom.js';
import { RP, KG, tanggalPendek, tanggalTutupAktif } from '../inti/format.js';
import * as HL from './tutup-tablet-logika.js';
import * as WB from './wadah-bernama-logika.js';
import * as ST from './struk-logika.js';
import * as PR from '../inti/printer.js';
import { asliAda, printerSibuk, masihMencetak, hasilTakDiketahui, KALIMAT_MASIH_MENCETAK, KALIMAT_TAK_DIKABARI } from '../inti/perangkat.js';
import { hakAkun, tombolAkun } from './akses-layar.js';

export const HL_DRAF_KOSONG = HL.HL_DRAF_KOSONG;
const kelasStatus = (st) => (st === 'disetujui' ? 'lunas' : st === 'ditolak' ? 'awas' : 'tunggu');
/** Kartu ini tampil untuk akun tablet Penjaga laci yang kisi hitungLaci-nya bukan "tidak boleh" (server: rules v16 stafHitungLaci(['ben'])). */
export const hlTampil = (akun) => !!akun && akun.jenis === 'aktif' && akun.peran === 'ben' && hakAkun(akun, 'hitungLaci') !== 'tidak';

/** Kartu panel. s.hl = draf (HL_DRAF_KOSONG); s.hlCekYakin = { W, kg } (dikosongkan = dua ketukan); opsi = { akun, kini }. */
export function kartuTutupTablet(s, opsi) {
  const o = opsi || {}; const a = o.akun; const d = Object.assign(HL_DRAF_KOSONG(), s.hl || {}); const kini = o.kini || new Date();
  const iso = tanggalTutupAktif(kini); const saya = HL.hlMilikSaya(a, iso); const hariIni = saya.filter((b) => b.tanggal === iso); const tunggu = hariIni.filter((b) => b.status === 'menunggu');
  const kepala = h`<div class="label">Tutup hari · ${tanggalPendek(iso)}${tunggu.length ? ' · hitungan menunggu owner' : hariIni.some((b) => b.status === 'disetujui') ? ' · ditutup owner' : ''}</div>`;
  const daftar = saya.length ? h`<div class="label" data-k="hl-daftar">Hitungan dari tablet ini · 7 hari</div>${saya.map((b) => h`<div class="tp-baris ${kelasStatus(b.status)}" data-k="hl-${b.id}"><div style="min-width: 0;">
      <div>Hitungan laci ${tanggalPendek(b.tanggal)} · <b>${RP(b.hitung)}</b>${b.amankan ? ' · ' + RP(b.amankan) + ' ke brankas' : ''}</div>
      <div class="k2">${b.jam} · ${b.dari} · <b>${b.namaStatus}</b>${b.diputus ? ' ' + b.diputus : ''}</div>
      ${b.alasan ? h`<div class="k2 awas-teks">Owner: ${b.alasan}</div>` : ''}${b.balasan ? h`<div class="k2">Owner: ${b.balasan}</div>` : ''}</div>
      <div class="kaca-btn kecil tp-cetak" data-aksi="hlCetak" data-id="${b.id}">Cetak</div></div>`)}` : '';
  if (!d.buka) return h`<div class="kartu" data-k="hl-kartu" style="gap: 8px;">${kepala}
      <div class="ket" style="font-size: 11px;">Hitung uang di laci, timbang cepat, cek wadah, lalu pindahkan uang lebih ke brankas. Hitungannya dikirim ke owner; owner yang menutup hari di HP.</div>
      <div class="kaca-btn aktif emas" data-aksi="hlBuka" data-k="hl-buka">${tunggu.length ? 'HITUNG ULANG LACI' : 'MULAI TUTUP HARI'}</div>${daftar}</div>`;
  const H = HL.hlHitung(d, kini);
  const pecah = h`<div data-k="hl-pecahan">${H.pecahan.map((x) => h`<div class="th-pecah" data-k="hl-pc-${x.p}"><span>${RP(x.p)}</span><span class="step"><span data-aksi="hlPecahan" data-p="${x.p}" data-arah="-1">−</span><input class="ketik-nama" type="text" inputmode="numeric" value="${x.n || ''}" placeholder="0" data-ketik="hlPecahanKetik" data-p="${x.p}"><span data-aksi="hlPecahan" data-p="${x.p}" data-arah="1">＋</span></span><span class="jm">${x.n ? RP(x.jumlah) : ''}</span></div>`)}
      <div class="th-pecah"><span>Koin & receh</span><input class="ketik-nama" type="text" inputmode="numeric" value="${d.receh}" placeholder="0" data-ketik="hlKetik" data-kolom="receh" style="width: 100px;"><span class="jm"></span></div>
      <div class="th-baris jumlah"><span>Dihitung</span><span class="n" style="font-size: 18px;" data-k="hl-jumlah">${RP(H.hitung)}</span></div></div>`;
  const timbang = H.timbang.length ? h`<div data-k="hl-timbang"><div class="label" style="font-size: 9.5px;">2 · Timbang cepat</div>${H.timbang.map((m) => h`<div class="th-timb" data-k="hl-tb-${m.merk}"><div><div style="font-weight: 600;">${m.merk}</div><div class="ket" style="font-size: 10.5px;">catatan ${KG(m.sistem)} · keluar hari ini ${KG(m.keluar)}</div></div>
      <input class="ketik-nama" type="text" inputmode="decimal" placeholder="kg ditimbang" value="${(d.timbang || {})[m.merk] || ''}" data-ketik="hlTimbang" data-merk="${m.merk}" style="width: 110px;"></div>`)}
      <div class="ket" style="font-size: 10.5px;">Boleh dilewati. Bedanya dicatat owner sebagai penyesuaian stok saat menutup hari.</div></div>`
    : h`<div class="ket" data-k="hl-timbang-kosong">2 · Timbang cepat: tidak ada beras karung yang keluar hari ini.</div>`;
  const CW = WB.wbCekHari(H.iso); const cwAktif = CW.daftar.filter((x) => x.aktif); const tbCek = tombolAkun(a, 'isiUlang');
  const cwTombol = (x, [id, nm]) => (!tbCek.boleh ? h`<div class="kaca-btn kecil mati" data-aksi="hlMati" data-kal="${tbCek.kalimat}">${nm}</div>`
    : id === 'kosong' && s.hlCekYakin && s.hlCekYakin.W === x.W ? h`<div class="kaca-btn kecil aktif awas" data-aksi="hlCek" data-w="${x.W}" data-hasil="kosong">KETUK LAGI · ±${KG(s.hlCekYakin.kg)}</div>`
    : h`<div class="kaca-btn kecil ${x.dicek && x.hasil === id ? 'aktif' : ''}" data-aksi="hlCek" data-w="${x.W}" data-hasil="${id}">${x.dicek && x.hasil === id ? '✓ ' + nm : nm}</div>`);
  const cek = h`<div data-k="hl-cek"><div class="label" style="font-size: 9.5px;">3 · Cek wadah literan · ${H.cek.dicek} dari ${H.cek.aktif}</div>
      ${cwAktif.map((x) => h`<div class="cw-baris ${x.dicek ? 'dicek' : ''}" data-k="hl-cw-${CW.daftar.indexOf(x)}"><div class="cw-atas"><span>${x.no} · ${x.W}</span><span class="ket" style="font-size: 10.5px;">${x.dicek ? 'dicek ' + x.jam + (x.oleh ? ' oleh ' + x.oleh : '') : 'BELUM dicek'}</span></div>
        <div class="cw-aksi">${WB.WB_CEK.map((c) => cwTombol(x, c))}</div></div>`)}
      ${!cwAktif.length ? h`<div class="ket">Belum ada wadah yang punya buku sendiri.</div>` : ''}
      ${s.hlCekYakin ? h`<div class="pita-info awas" data-k="hl-cw-yakin">Wadah ${s.hlCekYakin.W} dikosongkan? Ketuk "KETUK LAGI" untuk mencatat, atau <span data-aksi="hlCekBatal" style="text-decoration: underline; cursor: pointer;">batal</span>.</div>` : ''}
      <div class="ket" style="font-size: 10.5px;">Sesuai = isi kotak sama dengan catatan · Lupa isi ulang = tuangannya belum dicatat · Dikosongkan = isinya dikembalikan ke karung. Langsung tercatat.</div></div>`;
  const aman = !H.amankanBisa ? h`<div class="ket" data-k="hl-aman-mati">4 · Amankan laci: setelan uang kembalian owner belum terbaca di tablet — uangnya tetap di laci, owner yang memutus.</div>`
    : !(H.pindah > 0) ? h`<div class="ket" data-k="hl-aman-kosong">4 · Amankan laci: isi laci tidak lebih dari uang kembalian ${RP(H.kembalian)} — tidak ada yang dipindah.</div>`
    : h`<div data-k="hl-aman"><div class="label" style="font-size: 9.5px;">4 · Amankan laci</div><div class="th-baris"><span>Pindahkan ke brankas</span><span class="n" style="font-size: 18px;">${RP(H.pindah)}</span></div>
      <div class="ket" style="font-size: 11px;">Sisakan ${RP(H.kembalian)} di laci untuk kembalian besok.</div>
      <div class="tombol-baris rapat"><div class="kaca-btn ${d.amankan === 'sudah' ? 'aktif' : ''}" data-aksi="hlAman" data-p="sudah">Sudah dipindah</div><div class="kaca-btn ${d.amankan === 'tidak' ? 'aktif' : ''}" data-aksi="hlAman" data-p="tidak">Tidak dipindah</div></div></div>`;
  return h`<div class="kartu" data-k="hl-kartu" style="gap: 8px;">${kepala}
    ${H.kalimatTanggal ? h`<div class="pita-info emas" data-k="hl-lewat-malam">${H.kalimatTanggal}</div>` : ''}
    <div class="label" style="font-size: 9.5px;">1 · Hitung uang di laci</div>${pecah}${timbang}${cek}${aman}
    <div class="kaca-btn aktif emas" data-aksi="hlKirim" data-k="hl-kirim">${H.tolakHitung ? H.tolakHitung : 'KIRIM HITUNGAN KE OWNER · ' + RP(H.hitung)}</div>
    <div class="tombol-baris rapat"><div class="kaca-btn kecil" data-aksi="hlTutupLembar">tutup lembar</div></div>
    <div class="ket" style="font-size: 11px;">Owner melihat hitunganmu di HP dan menutup hari dari sana. Kalau owner minta hitung ulang, alasannya muncul di bawah.</div>${daftar}</div>`;
}

/** Aksi panel — digabung ke AKSI layar Menu. tulis(r) = penulis layar (kabar ikut); waktu() = { tanggal, jam, kini, idUnik }. */
export function aksiTutupTablet({ set, st, tulis, akun, waktu }) {
  const draf = () => Object.assign(HL_DRAF_KOSONG(), st().hl || {});
  const ubah = (p) => set({ hl: Object.assign(draf(), p) });
  const ak = () => (akun ? akun() : null);
  function cetak(teks, nama) {
    if (!asliAda()) { const pre = document.getElementById('cetakStruk'); if (pre) { pre.textContent = teks; pre.className = 'cetak-struk k' + (Number(ST.stAtur().kertas) === 58 ? 58 : 80); } try { window.print(); } catch (e) { /* abaikan */ } return; }
    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
    set({ kabar: 'Mencetak ' + nama.toLowerCase() + '…', kabarAwas: false });
    PR.cetakTeks(teks).then((r) => set({ kabar: nama + ' tercetak lewat ' + PR.namaJalur(r.jalur) + (r.cadanganDari ? ' — jalur yang dipilih tidak jalan (' + r.cadanganDari + ')' : ''), kabarAwas: !!r.cadanganDari }))
      .catch((e) => {
        if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });
        if (hasilTakDiketahui(e)) return set({ kabar: KALIMAT_TAK_DIKABARI, kabarAwas: true });
        set({ kabar: nama + ' TIDAK tercetak: ' + (e && e.message ? e.message : e), kabarAwas: true });
      });
  }
  const dicetak = () => { const w = waktu(); const a = ak(); return { tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }; };
  return {
    hlBuka: () => ubah({ buka: true }),
    hlTutupLembar: () => set({ hl: Object.assign(draf(), { buka: false }), hlCekYakin: null }),
    hlPecahan: ({ p, arah }) => { const l = Object.assign({}, draf().lembar); l[p] = Math.max(0, (Number(l[p]) || 0) + Number(arah)); ubah({ lembar: l }); },
    hlPecahanKetik: (v, el) => { const l = Object.assign({}, draf().lembar); l[el.dataset.p] = Math.max(0, Math.floor(Number(String(v).replace(/[^\d]/g, '')) || 0)); ubah({ lembar: l }); },
    hlKetik: (v, el) => ubah({ [el.dataset.kolom]: String(v).slice(0, 14) }),
    hlTimbang: (v, el) => { const t = Object.assign({}, draf().timbang); t[el.dataset.merk] = String(v).slice(0, 10); ubah({ timbang: t }); },
    hlAman: ({ p }) => ubah({ amankan: draf().amankan === p ? '' : p }),
    hlMati: ({ kal }) => set({ kabar: kal, kabarAwas: true }),
    hlCek: async ({ w: W, hasil }) => {
      const tb = tombolAkun(ak(), 'isiUlang'); if (!tb.boleh) return set({ hlCekYakin: null, kabar: tb.kalimat, kabarAwas: true });
      const r = WB.wbSusunCek(W, hasil, waktu()); if (r.tolak) return set({ hlCekYakin: null, kabar: r.tolak, kabarAwas: true });
      if (hasil === 'kosong') { const y = st().hlCekYakin; if (!y || y.W !== W) return set({ hlCekYakin: { W, kg: r.sisihKg }, kabar: '', kabarAwas: false }); }
      set({ hlCekYakin: null }); await tulis(r);
    },
    hlCekBatal: () => set({ hlCekYakin: null, kabar: '' }),
    hlKirim: async () => { const d = draf(); if (await tulis(HL.hlSusunKirim(d, ak(), waktu()))) set({ hl: HL_DRAF_KOSONG(), hlCekYakin: null }); },
    hlCetak: ({ id }) => { const w = waktu(); const b = HL.hlMilikSaya(ak(), w.tanggal).find((x) => x.id === String(id)); if (!b) return set({ kabar: 'Hitungannya tidak ditemukan', kabarAwas: true });
      cetak(HL.hlTeksCetak(b, ST.stAtur().kop, dicetak()), 'Hitungan laci'); },
  };
}
