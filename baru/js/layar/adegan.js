// ADEGAN — animasi cerita di layar Jual (permintaan owner 19 Sep 2026: "biar gua gak gampang bosen waktu di toko").
//   · literan masuk keranjang  → SEROK dari wadah kotak → dituang ke kantong kertas → diikat → dikemas
//   · isi ulang wadah          → serok dari KARUNG TERBUKA di belakang → dituang ke kotak wadah, permukaannya naik
//   · buka karung (owner 21 Sep) → satu karung DIANGKAT dari TUMPUKAN GUDANG (tumpukannya berkurang satu) → ditaruh & dibuka di belakang wadah
//   · kemasan masuk keranjang  → kemasan jatuh ke keranjang belanja, keranjangnya memantul
//   · nota dicatat → (owner 23 Sep) SELALU dimulai dengan TERIMA UANG: tangan pembeli menyerahkan uang ke tangan toko (QRIS = ponsel
//     bercentang, BON = kertas bon — bukan uang), BARU disusul adegan barangnya:
//   · nota dicatat (literan/kemasan) → SERAH TERIMA: dua tangan toko (atas & bawah kemasan) → dua tangan pembeli
//   · nota dicatat (karung)    → karung DIANGKUT, tangan pembeli memberi uang ke tangan toko (jalur lama, kini tak dipakai adeganNota)
//   · (owner 22 Sep) karung 50 kg / kemasan ≥ 10 kg masuk keranjang → ORANG MEMANGGUL karung ke pundaknya;
//     nota dicatat → orang yang tadi memanggul menaruhnya ke MOTOR (banyak → MOBIL bak terbuka), kendaraan pergi → jadi alat bayar;
//     setengah karung (25 kg dari karung 50 kg) → karung 50 kg DITUANG ke karung bekas, lalu mulutnya DIJAHIT
// Kejujuran: yang "jadi uang" hanya Tunai. QRIS digambar ponsel ber-centang; BON digambar kertas bon — bukan uang,
// karena belum ada uang yang berpindah (memori: status yang berbohong soal uang).
// Teknis: hanya transform & opacity (dikomposit GPU → mulus), tidak menghalangi ketukan (pointer-events: none),
// dilewati bila tab tersembunyi atau pemakai meminta "kurangi gerakan".
import { esc } from '../inti/dom.js';

const adeganDiam = () => document.hidden || (typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches);
let jamTutup = 0;

function panggung() {
  let p = document.getElementById('panggung');
  if (!p) { p = document.createElement('div'); p.id = 'panggung'; p.className = 'panggung'; p.setAttribute('aria-hidden', 'true'); document.body.appendChild(p); }
  return p;
}
function mainkan(svg, keterangan, lamaMs) {
  if (adeganDiam()) return false;
  const p = panggung(); clearTimeout(jamTutup);
  p.classList.remove('main', 'tutup'); p.innerHTML = '<div class="panggung-kartu">' + svg + '<div class="panggung-ket">' + keterangan + '</div></div>';
  void p.offsetWidth; p.style.setProperty('--lama', lamaMs + 'ms'); p.classList.add('main');
  jamTutup = setTimeout(() => { p.classList.add('tutup'); jamTutup = setTimeout(() => { p.classList.remove('main', 'tutup'); p.innerHTML = ''; }, 420); }, lamaMs + 500);
  return true;
}

// ---------- potongan gambar ----------
// tangan (menghadap kanan, telapak ke bawah) dalam kotak ±64×26; lengan baju = pihaknya (toko emas, pembeli platina)
const tangan = (kelas) => `<g class="tangan ${kelas}"><path class="lengan" d="M-46 -9 h26 v20 h-26 z"/><path class="kulit" d="M-20 -8 h16 q7 -5 17 -3 l13 3 q7 2 7 9 q0 7 -7 7 h-30 q-6 0 -10 -4 h-6 z"/><path class="ruas" d="M14 -2 v9 M21 -1 v9 M28 1 v8"/></g>`;
const kantongKertas = () => `<g class="paket kantong"><path class="badan" d="M-22 -8 L22 -8 L26 36 L-26 36 Z"/><path class="leher" d="M-13 -8 L-7 -22 L7 -22 L13 -8 Z"/><path class="lipat" d="M-10 -8 L-13 36 M10 -8 L13 36"/><path class="tali" d="M-9 -12 h18 M-9 -12 q-8 -6 -2 -11 M9 -12 q8 -6 2 -11"/></g>`;
const kemasan = (ukuran) => `<g class="paket kemasan"><rect class="badan" x="-22" y="-26" width="44" height="60" rx="6"/><path class="lipat" d="M-22 -18 h44 M-22 26 h44"/><rect class="label" x="-14" y="-8" width="28" height="20" rx="3"/><text class="angka-paket" x="0" y="7" text-anchor="middle">${esc(ukuran)}</text></g>`;
const karung = (berat) => `<g class="paket karung"><path class="badan" d="M-24 -22 Q0 -14 24 -22 L30 -12 Q36 16 30 40 Q0 46 -30 40 Q-36 16 -30 -12 Z"/><path class="tali" d="M-12 -32 Q-6 -22 -14 -21 M12 -32 Q6 -22 14 -21 M-14 -21 Q0 -15 14 -21"/><text class="angka-paket" x="0" y="18" text-anchor="middle">${esc(berat)}</text></g>`;
const uang = () => `<g class="alat-bayar uang"><g transform="rotate(-14)"><rect class="lembar-uang" x="-34" y="-17" width="68" height="34" rx="4"/></g><g transform="rotate(6)"><rect class="lembar-uang" x="-34" y="-17" width="68" height="34" rx="4"/><circle class="cap" cx="0" cy="0" r="9"/><text class="rp" x="0" y="4" text-anchor="middle">Rp</text></g><circle class="koin" cx="40" cy="16" r="8"/><circle class="koin" cx="-42" cy="18" r="6"/></g>`;
const qris = () => `<g class="alat-bayar qris"><rect class="ponsel" x="-20" y="-32" width="40" height="64" rx="7"/><path class="kotak-qr" d="M-12 -20 h9 v9 h-9 z M3 -20 h9 v9 h-9 z M-12 -5 h9 v9 h-9 z M4 -4 h3 v3 h-3 z M9 1 h3 v3 h-3 z"/><circle class="cap" cx="0" cy="20" r="8"/><path class="centang" d="M-4 20 l3 3 l6 -7"/></g>`;
const bon = () => `<g class="alat-bayar bon"><path class="kertas" d="M-24 -30 h48 v56 l-8 -5 l-8 5 l-8 -5 l-8 5 l-8 -5 l-8 5 z"/><path class="baris-bon" d="M-16 -18 h32 M-16 -8 h32 M-16 2 h20"/><text class="rp" x="0" y="18" text-anchor="middle">BON</text></g>`;
const alatBayar = (cara, sisaBon) => (cara === 'QRIS' ? qris() : cara === 'Kredit' ? bon() : (sisaBon ? `<g transform="translate(34 -22) scale(0.62)">${bon()}</g>` : '') + uang());
const wadahKotak = () => `<g class="wadah-adegan"><path class="gunung-adegan" d="M-44 0 Q-24 -2 -12 -24 Q0 -40 12 -24 Q24 -2 44 0 Z"/><path class="kotak-adegan" d="M-48 0 h96 l-6 46 h-84 z"/><path class="lipat" d="M-46 16 h92 M-44 32 h88"/></g>`;
const karungBuka = () => `<g class="wadah-adegan"><path class="gunung-adegan" d="M-30 -4 Q0 -22 30 -4 Z"/><path class="kotak-adegan" d="M-32 -6 Q0 2 32 -6 Q40 26 34 46 Q0 52 -34 46 Q-40 26 -32 -6 Z"/></g>`;
// orang menghadap kanan, titik asal di kakinya; .beban = barang yang dipanggul di pundak (diisi pemanggil)
const orang = (beban) => `<g class="orang"><g class="tubuh"><path class="kaki kaki-kiri" d="M-4 -34 L-9 0"/><path class="kaki kaki-kanan" d="M4 -34 L9 0"/><path class="badan-orang" d="M-12 -36 Q-15 -70 0 -74 Q15 -70 12 -36 Z"/><circle class="kepala" cx="0" cy="-85" r="9.5"/><path class="lengan-orang" d="M9 -66 Q26 -64 24 -84"/><g class="beban">${beban || ''}</g></g></g>`;
const motor = () => `<g class="kendaraan motor"><g class="roda-grup"><circle class="roda" cx="-32" cy="0" r="13"/><circle class="jari" cx="-32" cy="0" r="5.5"/></g><g class="roda-grup"><circle class="roda" cx="34" cy="0" r="13"/><circle class="jari" cx="34" cy="0" r="5.5"/></g><path class="rangka" d="M-32 0 L-14 -26 L16 -26 L34 0 M16 -26 L26 -44"/><path class="jok" d="M-44 -34 h34 l6 8 h-44 z"/><path class="tangki" d="M-10 -40 h24 l8 12 h-32 z"/><path class="setang" d="M18 -48 h18"/><circle class="lampu" cx="38" cy="-40" r="3.5"/><path class="knalpot" d="M-8 -14 h-30 v4 h30 z"/></g>`;
const mobil = () => `<g class="kendaraan mobil"><path class="bodi" d="M-80 -24 h68 v-26 h30 l18 24 h14 v26 h-130 z"/><path class="bak-garis" d="M-80 -24 h68 v-16 h-68 z M-12 -24 v-26"/><rect class="kaca" x="-6" y="-46" width="24" height="18" rx="3"/><circle class="lampu" cx="48" cy="-14" r="3"/><g class="roda-grup"><circle class="roda" cx="-52" cy="0" r="12"/><circle class="jari" cx="-52" cy="0" r="5"/></g><g class="roda-grup"><circle class="roda" cx="26" cy="0" r="12"/><circle class="jari" cx="26" cy="0" r="5"/></g></g>`;
const karungBekas = () => `<g class="karung-bekas"><clipPath id="klipBekas"><path d="M-27 -38 h54 Q54 -8 30 40 Q0 46 -30 40 Q-54 -8 -27 -38 Z"/></clipPath><g clip-path="url(#klipBekas)"><rect class="isi-kantong isi-bekas" x="-56" y="-40" width="112" height="86"/></g><path class="badan bekas" d="M-27 -38 h54 Q54 -8 30 40 Q0 46 -30 40 Q-54 -8 -27 -38 Z"/><path class="lipat" d="M-18 -26 v56 M18 -26 v56"/><path class="jahitan" pathLength="100" d="M-27 -38 l4 -6 l4 6 l4 -6 l4 6 l4 -6 l4 6 l4 -6 l4 6 l4 -6 l4 6 l4 -6 l4 6 l4 -6 l2 6"/></g>`;
const jarum = () => `<g class="jarum"><path class="benang" d="M-4 6 q-10 10 -4 24"/><path class="batang-jarum" d="M-16 14 L14 -6"/><circle class="lubang" cx="10" cy="-3" r="2"/></g>`;
// muatan di kendaraan: sampai tiga buah ditumpuk
const muatan = (jenis, ukuran, banyak) => { const n = Math.max(1, Math.min(3, Math.ceil(Number(banyak) || 1))); const satu = jenis === 'karung' ? karung(ukuran || '50') : jenis === 'kemasan' ? kemasan(ukuran || '') : kantongKertas();
  return Array.from({ length: n }).map((_, i) => `<g transform="translate(${i * 7} ${-i * 6}) scale(0.58)">${satu}</g>`).join(''); };
const bebanPundak = (jenis, ukuran) => `<g transform="translate(16 -106) rotate(-10) scale(0.7)">${jenis === 'kemasan' ? kemasan(ukuran || '') : karung(ukuran || '50')}</g>`;
const serok = () => `<g class="serok-adegan"><path class="gagang" d="M10 -34 L0 -8"/><path class="mangkuk" d="M-16 -8 h32 l-4 16 h-24 z"/><path class="beras-serok" d="M-14 -8 q14 -12 28 0 z"/></g>`;

// ---------- adegan ----------
/** Literan / repack masuk keranjang: serok → kantong → ikat. n = banyak serokan (1–3) menurut banyaknya beras. */
export function adeganSerok({ nama, jumlahTeks, dariKarung, kemasanLiteran, serokan }) {
  const n = Math.max(1, Math.min(3, Number(serokan) || 1)); const satu = 820; const lama = n * satu + 900;
  const wadahKantong = kemasanLiteran === 'karungbekas' ? '<g class="kantong-isi karung-kecil">' + karung('').replace('class="paket karung"', 'class="paket karung terbuka"') + '</g>'
    : `<g class="kantong-isi"><path class="badan" d="M-24 -30 L24 -30 L28 36 L-28 36 Z"/><rect class="isi-kantong" x="-26" y="-26" width="52" height="60"/><path class="lipat" d="M-12 -30 L-15 36 M12 -30 L15 36"/><g class="ikatan"><path class="leher" d="M-24 -30 L-7 -46 L7 -46 L24 -30 Z"/><path class="tali" d="M-10 -34 h20 M-10 -34 q-9 -6 -3 -12 M10 -34 q9 -6 3 -12"/></g></g>`;
  const svg = `<svg class="adegan serok" viewBox="0 0 320 170" style="--n: ${n}; --satu: ${satu}ms; --total: ${n * satu}ms;">
    <g transform="translate(86 112)">${dariKarung ? karungBuka() : wadahKotak()}</g>
    <g transform="translate(232 118)">${wadahKantong}</g>
    <g class="butir"><circle cx="232" cy="66" r="2"/><circle cx="226" cy="60" r="1.6"/><circle cx="238" cy="58" r="1.6"/><circle cx="231" cy="52" r="1.4"/></g>
    <g class="jalur-serok">${serok()}</g>
  </svg>`;
  return mainkan(svg, '<b>' + esc(nama) + '</b> · ' + esc(jumlahTeks) + (kemasanLiteran ? ' · dikemas &amp; diikat' : ' · diserok'), lama);
}
/** Isi ulang wadah: serok dari KARUNG TERBUKA di belakang → dituang ke KOTAK WADAH, permukaannya naik (menggunung bila lewat rata). */
export function adeganIsiUlang({ nama, keterangan, serokan, dari, ke }) {
  const n = Math.max(1, Math.min(3, Number(serokan) || 1)); const satu = 820; const lama = n * satu + 700;
  const b3 = (x) => Math.round(Math.max(0, Math.min(1, x)) * 1000) / 1000;
  const svg = `<svg class="adegan serok isi-ulang" viewBox="0 0 320 170" style="--n: ${n}; --satu: ${satu}ms; --total: ${n * satu}ms; --dalam-dari: ${b3(dari.dalam)}; --dalam-ke: ${b3(ke.dalam)}; --gunung-dari: ${b3(dari.gunung)}; --gunung-ke: ${b3(ke.gunung)};">
    <g transform="translate(86 112)">${karungBuka()}</g>
    <g transform="translate(232 112)"><g class="wadah-adegan"><path class="gunung-adegan gunung-naik" d="M-44 0 Q-24 -2 -12 -24 Q0 -40 12 -24 Q24 -2 44 0 Z"/><clipPath id="klipIsiWadah"><path d="M-47 0 h94 l-5.6 45 h-82.8 z"/></clipPath><g clip-path="url(#klipIsiWadah)"><rect class="isi-kantong isi-wadah-naik" x="-48" y="0" width="96" height="46"/></g><path class="kotak-adegan kosong" d="M-48 0 h96 l-6 46 h-84 z"/><path class="lipat" d="M-46 16 h92 M-44 32 h88"/></g></g>
    <g class="butir"><circle cx="232" cy="66" r="2"/><circle cx="226" cy="60" r="1.6"/><circle cx="238" cy="58" r="1.6"/><circle cx="231" cy="52" r="1.4"/></g>
    <g class="jalur-serok">${serok()}</g>
  </svg>`;
  return mainkan(svg, '<b>Isi ulang ' + esc(nama) + '</b> · ' + esc(keterangan), lama);
}
/** Buka karung: satu karung diangkat dari tumpukan gudang (kiri) → mendarat di belakang kotak wadah (kanan) → mulutnya dibuka. Angka tumpukan ikut turun. */
export function adeganBukaKarung({ nama, wadah, berat, dariKarung, keKarung, dariKg, keKg }) {
  const tumpuk = [[-30, 40], [30, 40], [0, 40], [-15, 8], [15, 8]].map(([x, y]) => `<g transform="translate(${x} ${y}) scale(0.62)">${karung('')}</g>`).join('');
  const svg = `<svg class="adegan buka-karung" viewBox="0 0 320 170">
    <g transform="translate(78 84)">${tumpuk}<g class="karung-diangkat"><g transform="translate(0 -24) scale(0.62)">${karung(berat || 50)}</g></g></g>
    <text class="angka-tumpuk dari" x="78" y="160" text-anchor="middle">${esc(dariKarung)} karung</text><text class="angka-tumpuk ke" x="78" y="160" text-anchor="middle">${esc(keKarung)} karung</text>
    <g transform="translate(244 78) scale(0.62)"><g class="karung-mendarat">${karungBuka()}</g></g>
    <g transform="translate(244 122) scale(0.7)">${wadahKotak().replace('class="gunung-adegan"', 'class="gunung-adegan" style="opacity: 0;"')}</g>
  </svg>`;
  return mainkan(svg, '<b>Karung ' + esc(nama) + '</b> diambil dari tumpukan gudang' + (wadah ? ' → di belakang wadah ' + esc(wadah) : '') + ' · tumpukan ' + esc(dariKg) + ' → ' + esc(keKg) + ' kg', 2300);
}
/** Karung / kemasan besar masuk keranjang: orang mengangkat karung dari lantai ke PUNDAKNYA (memanggul). */
export function adeganPanggul({ nama, jenis, ukuran, berat, jumlahTeks }) {
  const isi = jenis === 'kemasan' ? kemasan(ukuran || '') : karung(berat || '50');
  const svg = `<svg class="adegan panggul" viewBox="0 0 320 170">
    <path class="lantai" d="M40 150 h240"/>
    <g transform="translate(128 150)">${orang('')}<g class="beban-lantai"><g transform="translate(58 -34) scale(0.7)">${isi}</g></g></g>
  </svg>`;
  return mainkan(svg, '<b>' + esc(nama) + '</b> · ' + esc(jumlahTeks) + ' · dipanggul', 1700);
}
/**
 * TERIMA UANG (adegan pertama tiap nota, owner 23 Sep): tangan pembeli datang dari kanan membawa alat bayar, tangan toko datang dari kiri,
 * alat bayarnya berpindah ke tangan toko, tangan pembeli mundur. Tunai = uang (bayar sebagian: + kertas bon kecil), QRIS = ponsel bercentang,
 * BON = KERTAS BON (bukan uang — belum ada uang yang berpindah). Mengembalikan lamanya (ms) supaya adegan barang bisa disusulkan.
 */
export function adeganTerimaUang({ cara, jumlahRp, ket }) {
  const lama = 2300; const sisaBon = /bon/i.test(ket || '');
  const svg = `<svg class="adegan terima ${cara === 'Kredit' ? 'bon' : cara === 'QRIS' ? 'qris' : 'tunai'}" viewBox="0 0 320 170" style="--lama: ${lama}ms;">
    <g transform="translate(160 92)">
      <g class="grup-toko"><g transform="translate(-58 6) scale(1 -1)">${tangan('toko')}</g></g>
      <g class="grup-pembeli"><g transform="translate(58 -10) scale(-1 1)">${tangan('pembeli')}</g></g>
      <g transform="translate(0 -14)"><g class="alat-pindah">${alatBayar(cara, sisaBon)}</g></g>
    </g>
  </svg>`;
  return mainkan(svg, keteranganBayar(cara, jumlahRp, ket), lama) ? lama : false;
}
/** Nota dicatat (sesudah terima uang): orang yang memanggul berjalan ke kendaraan, menaruh muatannya, kendaraan pergi. kendaraan: 'motor' | 'mobil'. */
export function adeganMuat({ kendaraan, jenis, ukuran, banyak, banyakTeks }) {
  const mobilKah = kendaraan === 'mobil'; const lama = 3800;
  const svg = `<svg class="adegan muat ${mobilKah ? 'mobil' : 'motor'}" viewBox="0 0 320 170" style="--lama: ${lama}ms;">
    <path class="lantai" d="M0 150 h320"/>
    <!-- grup yang dianimasikan CSS TIDAK boleh membawa atribut transform (CSS transform menimpanya) → posisinya di grup pembungkus -->
    <g transform="translate(${mobilKah ? 226 : 214} 150)"><g class="kendaraan-grup">${mobilKah ? mobil() : motor()}<g transform="translate(${mobilKah ? -62 : -30} ${mobilKah ? -30 : -40})"><g class="muatan">${muatan(jenis, ukuran, banyak)}</g></g></g></g>
    <g transform="translate(-40 150)"><g class="pembawa">${orang(bebanPundak(jenis, ukuran))}</g></g>
  </svg>`;
  return mainkan(svg, '<b>Naik ' + (mobilKah ? 'mobil' : 'motor') + '</b> · ' + esc(banyakTeks) + ' · diantar ke kendaraan pembeli', lama);
}
/** Setengah karung: karung 50 kg diangkat, DITUANG ke karung bekas sampai separuh, lalu mulut karung bekasnya DIJAHIT. */
export function adeganTuangJahit({ nama, berat, kg }) {
  const lama = 3400;
  const svg = `<svg class="adegan tuang-jahit" viewBox="0 0 320 170" style="--lama: ${lama}ms;">
    <path class="lantai" d="M40 152 h240"/>
    <g transform="translate(104 118)"><g class="karung-tuang">${karung(berat || '50')}</g></g>
    <g class="butir"><circle cx="196" cy="74" r="2"/><circle cx="204" cy="66" r="1.7"/><circle cx="212" cy="78" r="1.6"/><circle cx="200" cy="86" r="1.5"/><circle cx="208" cy="58" r="1.4"/></g>
    <g transform="translate(218 118)">${karungBekas()}<g transform="translate(-34 -46)"><g class="jalur-jarum">${jarum()}</g></g></g>
  </svg>`;
  return mainkan(svg, '<b>' + esc(kg) + ' kg ' + esc(nama) + '</b> · dituang dari karung ' + esc(berat || '50') + ' kg ke karung bekas, lalu dijahit', lama);
}
/** Kemasan masuk keranjang belanja. */
export function adeganKemasanMasuk({ nama, ukuran, jumlahTeks }) {
  const svg = `<svg class="adegan masuk-keranjang" viewBox="0 0 320 170">
    <g transform="translate(160 40)"><g class="jatuh">${kemasan(ukuran)}</g></g>
    <g transform="translate(160 128)"><g class="keranjang-belanja"><path class="gagang-keranjang" d="M-40 -14 Q0 -64 40 -14"/><path class="badan-keranjang" d="M-54 -14 h108 l-10 46 h-88 z"/><path class="anyam" d="M-48 0 h96 M-44 14 h88 M-28 -14 l6 46 M0 -14 v46 M28 -14 l-6 46"/></g></g>
  </svg>`;
  return mainkan(svg, '<b>' + esc(nama) + '</b> · ' + esc(jumlahTeks) + ' masuk keranjang', 1250);
}
/** Nota dicatat (sesudah terima uang) — serah terima barang: dua tangan toko → dua tangan pembeli. jenis: 'kantong' | 'kemasan'. */
export function adeganSerahTerima({ jenis, ukuran, namaTeks }) {
  const paket = jenis === 'kemasan' ? kemasan(ukuran || '') : kantongKertas();
  const svg = `<svg class="adegan serah" viewBox="0 0 320 170" style="--lama: 2300ms;">
    <g transform="translate(160 86)">
      <g class="grup-toko"><g transform="translate(-20 -44)">${tangan('toko')}</g><g transform="translate(-20 50) scale(1 -1)">${tangan('toko')}</g></g>
      <g class="grup-pembeli"><g transform="translate(20 -44) scale(-1 1)">${tangan('pembeli')}</g><g transform="translate(20 50) scale(-1 -1)">${tangan('pembeli')}</g></g>
      <g class="grup-paket">${paket}</g>
    </g>
  </svg>`;
  return mainkan(svg, '<b>Serah terima</b> · ' + esc(namaTeks || '') + ' · diserahkan ke pembeli', 2300);
}
/** Nota dicatat (karung) — karung diangkut, tangan pembeli memberi alat bayar ke tangan toko. */
export function adeganKarung({ berat, cara, jumlahRp, ket, banyak }) {
  const svg = `<svg class="adegan angkut" viewBox="0 0 320 170">
    <g transform="translate(160 92)">
      <g class="grup-angkut"><g class="ayun">${karung(berat)}<g transform="translate(-6 50) scale(1 -1)">${tangan('toko')}</g><g transform="translate(6 50) scale(-1 -1)">${tangan('toko')}</g></g></g>
      <g class="grup-terima"><g transform="translate(-4 22) scale(1 -1)">${tangan('toko')}</g></g>
      <g class="grup-beri"><g transform="translate(4 -6) scale(-1 1)">${tangan('pembeli')}</g><g class="bawaan" transform="translate(-34 8) scale(0.55)">${alatBayar(cara)}</g></g>
      <g transform="translate(44 -4)"><g class="grup-bayar">${alatBayar(cara)}</g></g>
    </g>
  </svg>`;
  return mainkan(svg, (banyak ? '<b>' + esc(banyak) + '</b> diangkut · ' : '') + keteranganBayar(cara, jumlahRp, ket), 3100);
}
function keteranganBayar(cara, jumlahRp, ket) {
  const kepala = cara === 'QRIS' ? 'QRIS masuk' : cara === 'Kredit' ? 'Dicatat BON — belum ada uang' : 'Uang diterima';
  return '<b>' + kepala + '</b> · ' + esc(jumlahRp) + (ket ? ' · ' + esc(ket) : '');
}
