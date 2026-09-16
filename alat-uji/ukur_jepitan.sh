#!/bin/zsh
# ukur_jepitan.sh — MENGUKUR akibat jepitan di dalam mesin beku, memakai MESIN ASLINYA.
# Modul index.html dievaluasi utuh di jsc (prelude harness), cache diisi dari cadangan toko,
# lalu mesinnya dipanggil apa adanya. Tidak ada rumus tandingan: yang dilaporkan bacaan mesin.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; AKAR="$(cd "$DIR/.." && pwd)"
for c in /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc \
         /System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc; do
  [[ -x "$c" ]] && JSC="$c" && break; done
KERJA="$(mktemp -d)"
cp "$DIR"/harness/prelude.js "$DIR"/harness/stub-firebase-*.js "$KERJA"/
cp "$AKAR"/lib/lz-string.js "$KERJA"/ 2>/dev/null
CADANGAN="${1:-$AKAR/backup-batch-miqbal-2026-09-11.json}"
cp "$CADANGAN" "$KERJA"/cadangan.json

python3 - "$AKAR/index.html" "$KERJA" <<'PY'
import re, sys, pathlib, json
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); kerja = pathlib.Path(sys.argv[2])
m = re.search(r'<script type="module">(.*?)</script>', html, re.S)
js = m.group(1)
js, n = re.subn(r'https://www\.gstatic\.com/firebasejs/[^"\']+/firebase-(app|firestore|auth)\.js', r'./stub-firebase-\1.js', js)
assert n == 3, n
# UKUR disisipkan di UJUNG modul: di sini seluruh mesin & cache sudah dideklarasikan.
UKUR = r'''
// ================= PENGUKUR (disisipkan harness, bukan bagian aplikasi) =================
try {
  const B = globalThis.__CADANGAN;
  _cachePenjualan = B.penjualan || []; _cacheBatch = B.batchMasuk || [];
  _cacheProduksi = B.produksiKemasan || []; _cacheRetur = B.retur || [];
  _cacheKarantina = B.karantina || []; _cachePenyesuaian = B.penyesuaianStok || [];
  _cachePenyKemasan = B.penyesuaianKemasan || []; _cacheBahanKemasan = B.stokBahanKemasan || [];
  _cacheBahanLiteran = B.stokBahanLiteran || []; _cachePiutang = B.piutangMutasi || [];
  _cacheKasbon = B.kasbonMutasi || []; _cacheUtangPemasok = B.utangPemasokMutasi || [];
  _cacheHarian = B.pengeluaranHarian || []; _cacheTutup = B.tutupHari || [];
  _cacheSetoran = B.setoranKas || []; _cacheAmplop = B.amplopLaba || []; _cacheModal = B.modalOwner || [];
  _cacheBulanan = B.biayaBulanan || []; _cacheHargaKarung = B.katalogHargaKarung || [];
  _cacheHargaKemasan = B.katalogHargaKemasan || []; _cacheHargaLiteran = B.katalogHargaLiteran || [];

  const RP = n => (n < 0 ? '-' : '') + 'Rp' + Math.round(Math.abs(n)).toLocaleString('id-ID');
  const H = [];

  // ---- 1. STOK MINUS: bacaan MESIN, bukan hitungan ulang ----
  const sk = hitungStokKarungPerMerk();
  const minusK = Object.keys(sk).filter(m => (sk[m].sisaKg || 0) < -0.05)
    .map(m => ({ merk: m, kg: sk[m].sisaKg, hpp: sk[m].hppTerakhirPerKg || 0 }))
    .sort((a, b) => a.kg - b.kg);
  H.push('=== 1. STOK KARUNG MINUS (bacaan hitungStokKarungPerMerk) ===');
  H.push('  merek bersisa minus: ' + minusK.length + ' dari ' + Object.keys(sk).length);
  let rpMinusK = 0;
  minusK.forEach(x => { rpMinusK += x.kg * x.hpp;
    H.push('    ' + (x.merk + '                    ').slice(0, 22) + x.kg.toFixed(1).padStart(10) + ' kg  x ' + RP(x.hpp) + '/kg = ' + RP(x.kg * x.hpp)); });
  H.push('  nilai stok karung minus : ' + RP(rpMinusK) + '   (sekarang dijepit jadi Rp0 di neraca)');
  H.push('  -- SEMUA merek karung, terkecil dulu (kontrol: kalau semua positif, jepitannya memang mandul hari ini) --');
  Object.keys(sk).map(m => ({ m, kg: sk[m].sisaKg })).sort((a,b)=>a.kg-b.kg).forEach(x =>
    H.push('    ' + (x.m + '                    ').slice(0,22) + String(x.kg).padStart(12) + ' kg'));

  const sm = hitungStokKemasan();
  const minusM = Object.keys(sm).filter(k => (sm[k].sisaUnit || 0) < 0)
    .map(k => ({ k, u: sm[k].sisaUnit, hpp: sm[k].hppRataRataPerUnit || 0 }));
  let rpMinusM = 0; minusM.forEach(x => rpMinusM += x.u * x.hpp);
  H.push('  kemasan jadi minus      : ' + minusM.length + ' jenis, nilai ' + RP(rpMinusM));
  minusM.slice(0, 6).forEach(x => H.push('    ' + (x.k + '                    ').slice(0, 22) + String(x.u).padStart(8) + ' unit x ' + RP(x.hpp)));

  // ---- 2. NERACA: sekarang vs kalau minus ikut dihitung ----
  const N = hitungNeraca();
  H.push('');
  H.push('=== 2. NERACA (bacaan hitungNeraca) ===');
  Object.keys(N).forEach(k => { if (typeof N[k] === 'number') H.push('    ' + (k + '                        ').slice(0, 26) + RP(N[k])); });
  H.push('  JIKA stok minus ikut mengurangi: kekayaan bergeser ' + RP(rpMinusK + rpMinusM));

  // ---- 3. UTANG PEMASOK: adakah kelebihan bayar yang dibuang ----
  H.push('');
  H.push('=== 3. UTANG PEMASOK (bacaan hitungUtangPemasok) ===');
  const U = hitungUtangPemasok();
  H.push('    keluarannya ARRAY sepanjang ' + U.length + ' (satu per pemasok)');
  U.forEach(x => {
    const bon = x.bon || [];
    const nilai = bon.reduce((a,b)=>a+(b.nilai||0),0), dibayar = bon.reduce((a,b)=>a+(b.dibayar||0),0);
    H.push('      ' + ((x.pemasok||'?') + '                  ').slice(0,20)
      + ' bon ' + RP(nilai) + ' · dibayar ' + RP(dibayar) + ' · sisa ' + RP(x.sisa != null ? x.sisa : nilai-dibayar)
      + ' · kolom: ' + Object.keys(x).join(','));
  });
  // Apakah ADA pembayaran yang melebihi seluruh bon pemasok itu?
  const mut = (globalThis.__CADANGAN.utangPemasokMutasi||[]);
  const perBayar = {}; mut.forEach(m => { if (m.tipe==='bayar') perBayar[m.pemasok]=(perBayar[m.pemasok]||0)+(m.nominal||0); });
  H.push('    -- pembayaran dari mutasi vs bon yang terserap (mesin) --');
  U.forEach(x => { const bon=(x.bon||[]).reduce((a,b)=>a+(b.nilai||0),0);
    const bayar=perBayar[x.pemasok]||0;
    H.push('      ' + ((x.pemasok||'?')+'                  ').slice(0,20) + ' bayar ' + RP(bayar) + ' vs bon ' + RP(bon)
      + (bayar > bon + 1 ? '  -> KELEBIHAN ' + RP(bayar-bon) + ' (dibuang, tidak ada kolom tekor)' : '  -> muat')); });

  // ---- 4. KONTROL POSITIF: paksa satu merek jadi MINUS, neraca WAJIB ikut turun ----
  H.push('');
  H.push('=== 4. KONTROL POSITIF (stok dipaksa minus di kotak pasir) ===');
  const sebelum = hitungNeraca();
  const merkUji = Object.keys(sk)[0];
  const hppUji = sk[merkUji].hppTerakhirPerKg || 0;
  // jual 5.000 kg lagi dari merek itu -> sisanya pasti minus
  _cachePenjualan = _cachePenjualan.concat([{
    id: 'uji-minus', trxId: 'uji-minus', tanggal: '2026-09-11', jam: '23:59', jenis: 'karung',
    merkSumber: merkUji, namaProduk: merkUji, totalKg: 5000, jumlahKarung: 100,
    hargaTotal: 0, hppTotalSaatJual: 0, caraBayar: 'Tunai'
  }]);
  const sk2 = hitungStokKarungPerMerk();
  const sesudah = hitungNeraca();
  const kgBaru = sk2[merkUji].sisaKg;
  H.push('    merek uji           : ' + merkUji + '  ' + kgBaru.toFixed(1) + ' kg (hpp ' + RP(hppUji) + '/kg)');
  H.push('    nilaiSack sebelum   : ' + RP(sebelum.nilaiSack));
  H.push('    nilaiSack sesudah   : ' + RP(sesudah.nilaiSack));
  H.push('    selisih             : ' + RP(sesudah.nilaiSack - sebelum.nilaiSack));
  const turun = sesudah.nilaiSack < sebelum.nilaiSack;
  H.push('    stok minus MENGURANGI kekayaan? ' + (turun ? 'YA  <-- tambalan bekerja' : 'TIDAK — masih dijepit jadi Rp0'));
  H.push('    layar bisa menyebutnya?          ' + (sesudah.adaStokMinus ? 'YA, daftar: ' + sesudah.sackMinus.join(', ') : 'TIDAK'));
  if (!turun || !sesudah.adaStokMinus) H.push('    *** KONTROL POSITIF GAGAL ***');
  _cachePenjualan = _cachePenjualan.filter(x => x.id !== 'uji-minus');

  // ---- 5. KANTONG: harga per lembar menurut mesin ----
  H.push('');
  H.push('=== 5. KANTONG (bacaan hitungStokBahanKemasan) ===');
  const bk = hitungStokBahanKemasan();
  Object.keys(bk).sort().forEach(j => {
    const x = bk[j];
    H.push('    ' + (j + '                              ').slice(0, 30)
      + 'sisa ' + String(x.sisaPcs).padStart(6) + ' lembar  x ' + RP(x.hppPerPcs || 0) + '/lembar');
  });
  H.push('    (repack dadakan hari ini TIDAK memotong satu pun dari daftar ini)');

  print(H.join('\n'));
} catch (e) { print('PENGUKUR GAGAL: ' + (e && e.stack || e)); }
'''
js = js + UKUR
(kerja / 'modul.js').write_text(js, encoding='utf-8')
(kerja / 'jalan.js').write_text(
    "globalThis.__CADANGAN = JSON.parse(readFile('cadangan.json'));\n"
    "import('./modul.js').catch(e => print('MODUL GAGAL: ' + (e && e.stack || e)));\n", encoding='utf-8')
PY

cd "$KERJA" && "$JSC" --module-file=prelude.js jalan.js 2>&1
