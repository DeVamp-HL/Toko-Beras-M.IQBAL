// LAYAR JUAL — GAMBAR & KETUKAN. Satu markup untuk tiga lebar; lebar diatur css/kerangka.css.
// Logika (rak, tagihan, antrean, bayar) ada di jual-logika.js dan diuji tanpa peramban.
import { h, mentah, gabung, pasang, delegasi } from '../inti/dom.js';
import { buatKeadaan } from '../inti/keadaan.js';
import { RP, ANGKA, DESIMAL, tanggalPendek } from '../inti/format.js';
import * as L from './jual-logika.js';
import { sumberData, dengarkan } from '../data/toko.js';

const IKON = {
  gelap: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
  terang: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/></svg>',
  hapus: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg>',
};
const TUTS = ['1', '2', '3', '⌫', '4', '5', '6', ',', '7', '8', '9', '0'];

export function pasangLayarJual(akar, opsi) {
  const K = buatKeadaan(L.keadaanAwal());
  const set = (patch) => K.setel(patch);
  const S = () => K.baca();

  const aksi = {
    jalur: ({ jalur }) => set({ jalur, lembar: null, pilih: null }),
    mode: () => opsi.gantiMode(),
    chip: ({ jalur, kunci, berat }) => { const rak = rakKini(); const c = (rak[jalur] || []).find((x) => x.kunci === kunci && (!berat || String(x.berat) === berat)); if (c) set(L.ketukChip(S(), c)); },
    sering: ({ id }) => { const c = rakKini().sering.find((x) => x.id === id); if (c) set(L.ketukChip(S(), c)); },
    tuts: ({ t }) => set(L.tekanTuts(S(), t)),
    preset: ({ n }) => set(L.masukkan(S(), Number(n))),
    masukkan: () => set(L.masukkan(S())),
    tutup: () => set({ lembar: null, pilih: null, negoId: null, ketik: '' }),
    bukaKeranjang: () => set({ lembar: S().lembar === 'keranjang' ? null : 'keranjang' }),
    hapusBaris: ({ id }) => set(L.hapusBaris(S(), id)),
    kurangBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(S(), id, -Number(langkah || 1))),
    tambahBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(S(), id, Number(langkah || 1))),
    nego: ({ id }) => set({ negoId: id, lembar: 'nego', ketik: '' }),
    terapkanNego: () => set(L.terapkanNego(S(), S().negoId, L.angkaKetik(S().ketik))),
    bukaPotongan: () => set({ lembar: 'potongan', ketik: '' }),
    terapkanPotongan: () => set(L.setelPotongan(S(), L.angkaKetik(S().ketik))),
    hapusPotongan: () => set(L.setelPotongan(S(), 0)),
    parkir: () => set(L.parkir(S())),
    pembeliLain: () => set(L.pembeliLain(S())),
    antrean: ({ id }) => set(L.pakaiAntrean(S(), Number(id))),
    buangAntrean: ({ id }) => set(L.buangAntrean(S(), Number(id))),
    bukaBayar: () => set({ lembar: 'bayar', ketik: '' }),
    cara: ({ cara }) => set(L.pilihCara(S(), cara)),
    pecahan: ({ n }) => set(L.tambahUang(S(), Number(n))),
    uangPas: () => set(L.uangPas(S())),
    uangKetik: () => set(L.uangKetik(S())),
    hapusUang: () => set({ uang: 0 }),
    simpan: () => set(L.simpan(S())),
    bukaPelanggan: () => set({ lembar: 'pelanggan', cariPelanggan: '' }),
    pilihPelanggan: ({ nama }) => set({ pelanggan: nama, lembar: null, cariPelanggan: '', kabar: '' }),
    lepasPelanggan: () => set({ pelanggan: '', kabar: '' }),
    cariPelanggan: (v) => set({ cariPelanggan: String(v || '').slice(0, 40) },),
    enterPelanggan: (v) => { const n = String(v || '').trim(); if (n) set({ pelanggan: n, lembar: null, cariPelanggan: '' }); },
    tutupKabar: () => set({ kabar: '' }),
  };
  delegasi(akar, aksi);

  let _rak = null, _rakUntuk = '', _lembarSebelum = null;
  function rakKini() {
    const s = S(); L.sinkronKeranjang(s);
    const tanda = s.pelanggan + '|' + s.keranjang.length + '|' + s.antrean.length + '|' + opsi.versiData();
    if (!_rak || _rakUntuk !== tanda) { _rak = L.susunRak(s); _rakUntuk = tanda; }
    return _rak;
  }

  function gambar() {
    const s = S();
    const rak = rakKini();
    const t = L.hitungTagihan(s);
    const hari = L.hariIni(s);
    const sumber = sumberData();
    const info = L.infoPelanggan(s.pelanggan);
    // lembar hanya "naik" saat pertama dibuka — tiap ketukan menggambar ulang, jangan mengulang animasinya
    const muncul = s.lembar !== _lembarSebelum ? 'muncul' : ''; _lembarSebelum = s.lembar;
    document.body.classList.toggle('ada-lembar', !!s.lembar && s.lembar !== 'keranjang');
    document.body.classList.toggle('keranjang-terbuka', s.lembar === 'keranjang');
    pasang(akar, h`
      <input type="hidden" id="jualKarungBerat" value="${s.satuanKarung}">
      <div class="bola emas"></div><div class="bola platina"></div><div class="bola sampanye"></div>
      <header class="kepala-jual">
        <div><div class="serif" style="font-size: 26px;">Jual</div><div class="ket">${tanggalPendek(hari.iso)} · ${opsi.statusTeks()}</div></div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <div class="pil ${sumber.jenis === 'firestore' ? '' : 'kedip'}">${sumber.jenis === 'firestore' ? 'data toko' : sumber.jenis === 'cadangan' ? 'CADANGAN' : 'belum ada data'}</div>
          <div class="tombol-mode" data-aksi="mode" title="${opsi.mode() === 'gelap' ? 'Mode terang' : 'Mode gelap'}">${mentah(IKON[opsi.mode() === 'gelap' ? 'terang' : 'gelap'])}</div>
        </div>
      </header>
      <div class="pita-info emas baca-saja">BACA SAJA — angka dari ${sumber.keterangan || 'data toko'}; nota belum bisa dicatat dari sini (putaran berikutnya).</div>
      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? 'awas' : ''}" data-aksi="tutupKabar">${s.kabar}</div>` : ''}

      <section class="jual-rak">
        <div class="jalur">
          ${L.JALUR.map(([id, nama]) => h`<div class="seg ${s.jalur === id ? 'aktif' : ''}" data-aksi="jalur" data-jalur="${id}">${nama}</div>`)}
          ${L.JALUR_NANTI.map(([id, nama]) => h`<div class="seg nanti" title="putaran berikutnya">${nama}</div>`)}
        </div>
        ${s.antrean.length ? h`<div class="bilah-antre">
          ${s.antrean.map((a) => h`<div class="tab-antre ${a.beku.pelanggan ? 'bernama' : ''}"><span data-aksi="antrean" data-id="${a.id}">${a.beku.pelanggan || 'tanpa nama'} · ${a.beku.items.length} brg · ${RP(a.beku.items.reduce((x, b) => x + b.trx.hargaTotal, 0))}</span><span class="buang" data-aksi="buangAntrean" data-id="${a.id}" title="buang struk">${mentah(IKON.hapus)}</span></div>`)}
        </div>` : ''}
        ${gambarChip(s, rak)}
      </section>

      <section class="jual-keranjang ${s.lembar === 'keranjang' ? 'terbuka' : ''}">
        <div class="ringkas-keranjang" data-aksi="bukaKeranjang">
          <span>${s.keranjang.length ? s.keranjang.length + ' barang' : 'Keranjang kosong'}${s.pelanggan ? ' · ' + s.pelanggan : ''}</span>
          <span class="serif" style="font-size: 20px;">${RP(t.total)}</span>
        </div>
        <div class="isi-keranjang">
          <div class="keranjang">
            ${s.keranjang.length ? s.keranjang.map((b) => h`<div class="b">
              <div class="t"><div style="font-weight: 600;">${b.trx.label}</div><div class="ket">${DESIMAL(b.trx.jumlah)} ${b.trx.satuan} × ${RP(b.trx.hargaSatuan)}${b.trx.nego ? ' · nego' : ''}${b.trx.kemasanLiteran ? ' · ' + (b.trx.jumlahKemasanLiteranDipakai || 1) + ' kantong' : ''}</div></div>
              <span class="step"><span data-aksi="kurangBaris" data-id="${b.id}" data-langkah="${b.trx.satuan === 'karung' ? 0.5 : 1}">−</span><span class="n">${DESIMAL(b.trx.jumlah)}</span><span data-aksi="tambahBaris" data-id="${b.id}" data-langkah="${b.trx.satuan === 'karung' ? 0.5 : 1}">+</span></span>
              <div class="h" data-aksi="nego" data-id="${b.id}" title="ketuk untuk nego">${RP(b.trx.hargaTotal)}</div>
              <span class="hapus" data-aksi="hapusBaris" data-id="${b.id}">${mentah(IKON.hapus)}</span>
            </div>`) : h`<div class="kosong">Ketuk barang di rak untuk mulai.</div>`}
          </div>
          <div class="tombol-baris">
            <div class="kaca-btn ${s.pelanggan ? 'aktif' : ''}" data-aksi="bukaPelanggan">${s.pelanggan ? s.pelanggan : 'Nama pembeli'}</div>
            <div class="kaca-btn ${t.potongan ? 'aktif' : ''}" data-aksi="bukaPotongan">${t.potongan ? 'Potongan ' + RP(t.potongan) : 'Potongan'}</div>
            <div class="kaca-btn" data-aksi="pembeliLain">Pembeli lain</div>
          </div>
          ${info && info.sisa > 0 ? h`<div class="ket">Bon ${s.pelanggan} sekarang ${RP(info.sisa)} · biasa belanja ${RP(info.rataBulanan)}/bulan</div>` : ''}
          ${info && info.pesanan && info.pesanan.length ? h`<div class="pita-info">${info.pesanan.length} pesanan ${s.pelanggan} belum tuntas — buka di layar Pesanan (putaran berikutnya)</div>` : ''}
          <div class="bulat"></div>
          <div class="total"><span class="label">Subtotal</span><span class="n" style="font-size: 16px;">${RP(t.subtotal)}</span></div>
          ${t.potongan ? h`<div class="total"><span class="label">Potongan</span><span class="n" style="font-size: 16px;">− ${RP(t.potongan)}</span></div>` : ''}
          ${t.bulat ? h`<div class="total"><span class="label">Pembulatan Rp500 (${s.cara === 'Kredit' ? 'bon' : 'tunai'})</span><span class="n" style="font-size: 16px;">+ ${RP(t.bulat)}</span></div>` : ''}
          <div class="total"><span class="label">Ditagih</span><span class="n">${RP(t.total)}</span></div>
          <div class="utama" data-aksi="bukaBayar">BAYAR · ${RP(t.total)}</div>
          <div class="ket" style="text-align: center; cursor: pointer;" data-aksi="parkir">parkir struk ini — stoknya tetap dipegang</div>
        </div>
      </section>

      <aside class="jual-samping">
        <div class="kartu hari">
          <div class="label">Hari ini · ${hari.baris} baris · ${hari.nota} nota</div>
          <div class="serif" style="font-size: 24px;">${RP(hari.omzet)}</div>
          <div class="ket">${Object.keys(hari.perCara).map((c) => c + ' ' + RP(hari.perCara[c])).join(' · ') || 'belum ada penjualan'} · ${DESIMAL(hari.kg)} kg</div>
          ${hari.terakhir.map((r) => h`<div class="r"><span class="w">${r.jam}</span><span class="t">${r.teks}${r.nama ? ' · ' + r.nama : ''}</span><span class="n">${RP(r.n)}</span></div>`)}
        </div>
      </aside>

      ${gambarLembar(s, rak, t, info, muncul)}
    `);
  }

  function gambarChip(s, rak) {
    const daftar = s.jalur === 'sering' ? rak.sering : (rak[s.jalur] || []);
    if (!daftar.length) return h`<div class="pita-info">${s.jalur === 'sering' ? (s.pelanggan ? s.pelanggan + ' belum punya kebiasaan belanja 90 hari terakhir' : 'Belum ada yang laku 28 hari terakhir') : 'Belum ada barang berharga di jalur ini — isi harganya di Katalog'}</div>`;
    const penuh = Math.max(1, ...daftar.map((c) => c.sisa || 0));   // isian chip = sisa relatif terhadap yang paling banyak di jalur ini
    return h`<div class="rak-chip">${daftar.map((c) => h`<div class="chip ${s.pilih && s.pilih.kunci === c.kunci && s.pilih.jalur === c.jalur && (s.pilih.berat || 0) === (c.berat || 0) ? 'dipilih' : ''} ${c.sisa <= 0 ? 'habis' : c.sisa <= 2 ? 'kurang' : ''}"
        data-aksi="${s.jalur === 'sering' ? 'sering' : 'chip'}" data-id="${c.id || ''}" data-jalur="${c.jalur}" data-kunci="${c.kunci}" data-berat="${c.berat || ''}">
      <div class="isian" style="height: ${Math.round(Math.min(100, (c.sisa || 0) / penuh * 100))}%;"></div>
      <div class="nama">${c.nama}</div>
      <div class="rinci">${c.ukuran}${c.keterangan ? ' · ' + c.keterangan : ''}</div>
      <div class="harga">${RP(c.harga)}<span class="satuan">/${c.satuan}</span></div>
      <div class="stok">${c.sisa <= 0 ? 'habis' : c.sisaTeks}${c.dipegang > 0 ? ' · ' + (c.jalur === 'kemasan' ? c.dipegang + ' unit' : DESIMAL(c.dipegang) + ' kg') + ' dipegang struk lain' : ''}</div>
    </div>`)}</div>`;
  }

  function gambarLembar(s, rak, t, info, muncul) {
    if (!s.lembar || s.lembar === 'keranjang') return '';
    const L1 = h`<div class="lembar tirai" data-aksi="tutup"></div>`;
    const kepala = (judul, ket) => h`<div style="display: flex; justify-content: space-between; align-items: baseline;"><span class="judul">${judul}</span><span class="ket" style="cursor: pointer; text-decoration: underline;" data-aksi="tutup">tutup</span></div>${ket ? h`<div class="ket">${ket}</div>` : ''}`;
    const tuts = (aksiMasuk, label) => h`<div class="tuts">${TUTS.map((k) => h`<div class="k ${/^\d$/.test(k) ? '' : 'f'}" data-aksi="tuts" data-t="${k}">${k}</div>`)}<div class="k f aksi" style="grid-column: span 4;" data-aksi="${aksiMasuk}">${label}</div></div>`;
    if (s.lembar === 'jumlah' && s.pilih) {
      const c = s.pilih; const maks = L.maksUntuk(c);
      const preset = c.jalur === 'karung' ? [1, 2, 5, 10] : c.jalur === 'kemasan' ? [1, 2, 3, 5] : [1, 2, 5, 10];
      return h`${L1}<div class="lembar ${muncul}">
        ${kepala(c.nama + ' ' + c.ukuran, RP(c.harga) + '/' + c.satuan + ' · bebas dijual ' + (maks === null ? '—' : DESIMAL(maks) + ' ' + c.satuan))}
        <div class="tombol-baris">${preset.map((n) => h`<div class="kaca-btn" data-aksi="preset" data-n="${n}">${n} ${c.satuan}</div>`)}</div>
        <div class="label">Jumlah</div><div class="angka">${s.ketik || '0'} <span class="ket">${c.satuan}</span>${s.ketik ? h` <span class="ket">= ${RP(c.harga * L.angkaKetik(s.ketik))}</span>` : ''}</div>
        ${tuts('masukkan', 'MASUKKAN KE KERANJANG')}
      </div>`;
    }
    if (s.lembar === 'nego') {
      const b = s.keranjang.find((x) => x.id === s.negoId); if (!b) return '';
      return h`${L1}<div class="lembar ${muncul}">
        ${kepala('Nego ' + b.trx.label, 'harga sekarang ' + RP(b.trx.hargaSatuan) + '/' + b.trx.satuan + ' · ketik harga barunya')}
        <div class="angka">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>
        ${tuts('terapkanNego', 'PAKAI HARGA INI')}
      </div>`;
    }
    if (s.lembar === 'potongan') {
      return h`${L1}<div class="lembar ${muncul}">
        ${kepala('Potongan nota', 'nominal, dipotong dari subtotal ' + RP(t.subtotal))}
        <div class="angka">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>
        ${tuts('terapkanPotongan', 'PAKAI POTONGAN')}
        ${t.potongan ? h`<div class="kaca-btn putus" data-aksi="hapusPotongan">hapus potongan ${RP(t.potongan)}</div>` : ''}
      </div>`;
    }
    if (s.lembar === 'pelanggan') {
      const daftar = L.daftarPelanggan(s.cariPelanggan);
      return h`${L1}<div class="lembar ${muncul}">
        ${kepala('Siapa pembelinya?', 'nama dari catatan penjualan & kartu pelanggan toko')}
        <input class="ketik-nama" id="cariPelanggan" type="text" value="${s.cariPelanggan}" data-ketik="cariPelanggan" data-enter="enterPelanggan" placeholder="Ketik namanya — Enter untuk memakai nama baru">
        ${s.pelanggan ? h`<div class="kaca-btn putus" data-aksi="lepasPelanggan">Tanpa nama</div>` : ''}
        <div class="daftar-nama">${daftar.map((o) => h`<div class="baris-nama ${o.sisaBon > 0 ? 'berutang' : ''}" data-aksi="pilihPelanggan" data-nama="${o.nama}">
          <span>${o.nama}${o.terdaftar ? ' ✓' : ''}</span><span class="ket">${o.sisaBon > 0 ? 'bon ' + RP(o.sisaBon) + (o.umurHari ? ' · ' + o.umurHari + ' hari' : '') : o.kali + '× belanja'}</span></div>`)}
        ${daftar.length ? '' : h`<div class="ket">Belum ada nama itu — tekan Enter untuk memakai nama baru.</div>`}
      </div>`;
    }
    if (s.lembar === 'bayar') {
      const tolak = L.alasanTolak(s);
      return h`${L1}<div class="lembar ${muncul}">
        ${kepala('Bayar', s.keranjang.length + ' barang' + (s.pelanggan ? ' · ' + s.pelanggan : ''))}
        <div class="total"><span class="label">Ditagih</span><span class="n">${RP(t.total)}</span></div>
        ${t.bulat ? h`<div class="ket">termasuk pembulatan ke Rp500 ${RP(t.bulat)} (${s.cara === 'Kredit' ? 'bon ikut dibulatkan' : 'tunai'})</div>` : ''}
        <div class="tombol-baris">${[['Tunai', 'Tunai'], ['QRIS', 'QRIS'], ['Kredit', 'Bon']].map(([c, nm]) => h`<div class="kaca-btn ${s.cara === c ? 'aktif' : ''}" data-aksi="cara" data-cara="${c}">${nm}</div>`)}</div>
        ${s.cara === 'Tunai' ? h`
          <div class="label">Uang yang diterima — ketuk lembarannya</div>
          <div class="pecahan">${L.PECAHAN.map((p) => h`<div class="kaca-btn" data-aksi="pecahan" data-n="${p}">${p >= 1000 ? p / 1000 + ' rb' : p}</div>`)}<div class="kaca-btn aktif" data-aksi="uangPas">PAS</div></div>
          <div class="total"><span class="label">diterima ${t.uang ? h`<span class="ket" style="text-decoration: underline; cursor: pointer;" data-aksi="hapusUang">hapus</span>` : ''}</span><span class="n" style="font-size: 20px;">${RP(t.uang)}</span></div>
          ${t.kembalian ? h`<div class="total"><span class="label">Kembalian</span><span class="n" style="font-size: 20px;">${RP(t.kembalian)}</span></div>` : ''}
          ${t.sisaJadiBon ? h`<div class="pita-info awas">kurang ${RP(t.kurang)} — sisanya jadi bon atas nama ${s.pelanggan || '… (pilih nama pembelinya)'}. Yang kurang dicatat di buku bon, bukan ditolak, bukan dianggap lunas.</div>` : ''}
` : ''}
        ${s.cara === 'QRIS' ? h`<div class="pita-info">QRIS = angka persis, tidak dibulatkan. Yang masuk rekening sudah dipotong MDR — catatan toko, tidak dicetak di struk.</div>` : ''}
        ${s.cara === 'Kredit' ? h`<div class="pita-info ${s.pelanggan ? '' : 'awas'}">Bon ${s.pelanggan ? 'atas nama ' + s.pelanggan + (info && info.sisa > 0 ? ' — bon lama ' + RP(info.sisa) : '') : 'harus ada nama pembelinya'}${info && info.batas ? ' · biasa belanja ' + RP(info.rataBulanan) + '/bulan' : ''}</div>` : ''}
        <div class="kaca-btn" data-aksi="bukaPelanggan">${s.pelanggan ? s.pelanggan : 'Nama pembeli'}</div>
        <div class="utama ${tolak ? 'redup' : ''}" data-aksi="simpan">${tolak || 'CATAT NOTA · ' + RP(t.total)}</div>
        <div class="ket" style="text-align: center;">putaran ini BACA SAJA — tombol ini memeriksa notanya, belum menyimpan</div>
        ${s.cara === 'Tunai' ? h`<div class="bulat"></div><div class="ket">atau ketik nominal uang yang diterima:</div><div class="angka" style="font-size: 20px;">${s.ketik ? RP(L.angkaKetik(s.ketik)) : 'Rp0'}</div>${tuts('uangKetik', 'PAKAI NOMINAL INI')}` : ''}
      </div>`;
    }
    return '';
  }

  K.dengar(gambar);
  dengarkan(() => { _rak = null; gambar(); });
  gambar();
  return { keadaan: K, gambar };
}
