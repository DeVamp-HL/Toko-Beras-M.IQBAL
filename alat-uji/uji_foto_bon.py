#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_foto_bon.py — owner 7 Okt 2026: "buatkan fitur foto BON kalo bisa". Tanpa peramban (aturan CLAUDE.md): logika di jsc dengan KANVAS TIRUAN + pemeriksaan statis.
  · Pengecil (foto-bon-logika.js fbnKecilkan): sisi panjang ≤ 1600 px (tidak pernah dibesarkan), JPEG mutu 0,6 dulu lalu turun, lalu ukuran diperkecil;
    berhenti di yang pertama ≤ 300 KB; tidak ada yang ≤ sasaran tapi ≤ 700 KB → dipakai (lebihTarget); di atas batas → ditolak (dokumen Firestore ≤ 1 MiB).
    Berkas yang bukan gambar → ditolak dengan kalimat. Byte dihitung dari base64 (padding).
  · Penyimpan (fbnSusunSimpan): satu dokumen per foto {idBon, pemasok, tanggalBon, noBon, tanggal, jam, jenis, base64, byte, lebar, tinggi} — bon wajib,
    paling banyak 6 foto per bon, di atas batas ditolak; oleh/olehUid diisi penulis (bukan logika).
  · STATIS: koleksi fotoBon TIDAK ada di KOLEKSI (tidak didengar → tidak ikut baca penuh harian, cache, cadangan); firebase.js membacanya sekali per bon
    (getDocs + where idBon) dan menulis/menghapus tanpa salinan antre lokal, owner saja; layar memakai input berkas accept image/* + capture kamera,
    pilihan berkas lewat peristiwa change (tanpa handler sebaris); CSP img-src memuat data: & blob:; modulepreload memuat foto-bon-logika.js.

    python3 alat-uji/uji_foto_bon.py            → N lulus · 0 gagal
    python3 alat-uji/uji_foto_bon.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
MODUL = ['baru/js/inti/format.js', 'baru/js/layar/foto-bon-logika.js']

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify; var selesai = false;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
// KANVAS TIRUAN: ukuran JPEG (byte) = lebar × tinggi × mutu × k; data URL base64 dengan padding yang benar untuk byte itu
var tiruan = function (k, opsi) { var catat = []; return { catat: catat,
  buka: function (b) { if (opsi && opsi.rusak) return Promise.reject(new Error('bukan gambar')); return Promise.resolve({ lebar: b.lebar, tinggi: b.tinggi, gambar: { id: 'img' } }); },
  jpeg: function (g, w, h, q) { var byte = Math.max(1, Math.round(w * h * q * k)); catat.push([w, h, q, byte]); var n = Math.ceil(byte / 3) * 4; var pad = (3 - byte % 3) % 3; var s = new Array(n - pad + 1).join('A') + (pad === 2 ? '==' : pad === 1 ? '=' : ''); return 'data:image/jpeg;base64,' + s; } }; };
var W = { tanggal: '2026-10-07', jam: '09:15', idUnik: (function () { var n = 100; return function () { n += 1; return n; }; })() };
var BON = { id: 'b9', pemasok: 'PEMASOK CONTOH', tanggal: '2026-10-05', noBon: '12345' };
(async function () {
  try {
    ok('ukuran: 4000×3000 → 1600×1200; 3000×4000 → 1200×1600; 1000×800 tetap (tidak dibesarkan); sisi 800 → 800×600', J(fbnUkuran(4000, 3000, 1600)) === J({ lebar: 1600, tinggi: 1200, skala: 0.4 }) && fbnUkuran(3000, 4000, 1600).lebar === 1200 && fbnUkuran(3000, 4000, 1600).tinggi === 1600 && J(fbnUkuran(1000, 800, 1600)) === J({ lebar: 1000, tinggi: 800, skala: 1 }) && fbnUkuran(4000, 3000, 800).lebar === 800, J([fbnUkuran(4000, 3000, 1600), fbnUkuran(1000, 800, 1600)]));
    ok('byte dari base64 menghitung padding: "QUJD" 3 · "QUI=" 2 · "QQ==" 1 · kosong 0', fbnByte('QUJD') === 3 && fbnByte('QUI=') === 2 && fbnByte('QQ==') === 1 && fbnByte('') === 0);
    ok('data URL dipisah jadi jenis + base64; bukan data URL gambar → null; src dibangun balik', J(fbnPisahDataUrl('data:image/jpeg;base64,QUJD')) === J({ jenis: 'image/jpeg', base64: 'QUJD' }) && fbnPisahDataUrl('http://x/y.jpg') === null && fbnPisahDataUrl('data:text/html;base64,QUJD') === null && fbnSrc({ jenis: 'image/jpeg', base64: 'QUJD' }) === 'data:image/jpeg;base64,QUJD');
    // 1 · foto HP 4000×3000, k kecil → langsung muat di mutu 0,6 pada 1600×1200
    var T1 = tiruan(0.2); var H1 = await fbnKecilkan({ lebar: 4000, tinggi: 3000 }, T1);
    ok('foto 4000×3000: dikecilkan ke 1600×1200 mutu 0,6 di percobaan PERTAMA (≤ 300 KB), byte = isi base64, asal disebut', !H1.tolak && H1.lebar === 1600 && H1.tinggi === 1200 && H1.mutu === 0.6 && H1.coba === 1 && !H1.lebihTarget && H1.byte === fbnByte(H1.base64) && H1.byte <= FBN_TARGET && H1.jenis === 'image/jpeg' && H1.asalLebar === 4000 && J(T1.catat) === J([[1600, 1200, 0.6, 230400]]), J([H1.lebar, H1.mutu, H1.coba, H1.byte, T1.catat]));
    // 2 · lebih berat → mutu turun dulu (ukuran tetap), baru ukuran
    var T2 = tiruan(0.4); var H2 = await fbnKecilkan({ lebar: 4000, tinggi: 3000 }, T2);
    ok('foto lebih berat: mutu turun 0,6 → 0,5 → … di ukuran 1600 dulu, baru sisi diperkecil; hasil pertama ≤ 300 KB dipakai', !H2.tolak && H2.byte <= FBN_TARGET && T2.catat[0][2] === 0.6 && T2.catat[1][2] === 0.5 && T2.catat[0][0] === 1600 && T2.catat.slice(0, 4).every(function (c) { return c[0] === 1600; }) && H2.coba === T2.catat.length, J([H2.lebar, H2.mutu, H2.coba, T2.catat]));
    // 3 · tak satu pun ≤ sasaran, tapi terkecil ≤ batas → dipakai, lebihTarget
    var T3 = tiruan(3.2); var H3 = await fbnKecilkan({ lebar: 4000, tinggi: 3000 }, T3);
    ok('tak ada yang ≤ 300 KB tapi yang terkecil ≤ 700 KB → dipakai yang TERKECIL, bertanda lebihTarget; semua 16 percobaan dijalani', !H3.tolak && H3.lebihTarget === true && H3.byte > FBN_TARGET && H3.byte <= FBN_BATAS && T3.catat.length === FBN_SKALA.length * FBN_MUTU.length && H3.byte === Math.min.apply(null, T3.catat.map(function (c) { return c[3]; })), J([H3.byte, T3.catat.length]));
    // 4 · masih di atas batas → ditolak dengan kalimat
    var H4 = await fbnKecilkan({ lebar: 4000, tinggi: 3000 }, tiruan(20));
    ok('masih di atas 700 KB sesudah semua percobaan → DITOLAK dengan kalimat (foto ulang lebih dekat)', !!H4.tolak && /sesudah dikecilkan — lebih dari/.test(H4.tolak) && /Foto ulang/.test(H4.tolak), J(H4));
    // 5 · berkas bukan gambar / alat tidak ada
    var H5 = await fbnKecilkan({ lebar: 1, tinggi: 1 }, tiruan(1, { rusak: true })); var H6 = await fbnKecilkan({}, null);
    ok('berkas bukan gambar → ditolak "tidak bisa dibuka sebagai gambar"; alat kanvas tidak ada → ditolak', /tidak bisa dibuka sebagai gambar/.test(H5.tolak || '') && /tidak tersedia/.test(H6.tolak || ''), J([H5, H6]));
    // 6 · penyimpan
    var S1 = fbnSusunSimpan(BON, H1, W, []); var d = S1.data;
    ok('dokumen foto: idBon, pemasok, tanggalBon, noBon, tanggal & jam simpan, jenis, base64, byte (dihitung ulang), lebar, tinggi — TANPA oleh (diisi penulis); id dari idUnik; kabar menyebut ukuran',
      !S1.tolak && d.id === '101' && d.idBon === 'b9' && d.pemasok === 'PEMASOK CONTOH' && d.tanggalBon === '2026-10-05' && d.noBon === '12345' && d.tanggal === '2026-10-07' && d.jam === '09:15' && d.jenis === 'image/jpeg' && d.base64 === H1.base64 && d.byte === H1.byte && d.lebar === 1600 && d.tinggi === 1200 && d.oleh === undefined && /Foto bon 5 Okt 2026 PEMASOK CONTOH tersimpan \(225 KB, 1600×1200 px\)/.test(S1.patch.kabar), J([d.id, d.byte, S1.patch.kabar]));
    var enam = [1, 2, 3, 4, 5, 6].map(function (i) { return { id: i, idBon: 'b9', base64: 'QUJD' }; });
    ok('tanpa bon ditolak; hasil yang ditolak diteruskan kalimatnya; 6 foto sudah ada → ditolak; base64 di atas batas → ditolak; jenis bukan gambar → ditolak',
      /Pilih bonnya/.test(fbnSusunSimpan(null, H1, W, []).tolak || '') && fbnSusunSimpan(BON, H4, W, []).tolak === H4.tolak && /sudah punya 6 foto/.test(fbnSusunSimpan(BON, H1, W, enam).tolak || '')
      && /lebih dari/.test(fbnSusunSimpan(BON, { jenis: 'image/jpeg', base64: new Array(Math.ceil(FBN_BATAS / 3) * 4 + 9).join('A'), lebar: 1, tinggi: 1 }, W, []).tolak || '') && /tidak terbaca/.test(fbnSusunSimpan(BON, { jenis: 'text/html', base64: 'QUJD' }, W, []).tolak || ''));
    var u = fbnUrut([{ id: 1, idBon: 'b9', tanggal: '2026-10-06', jam: '10:00', base64: 'A' }, { id: 2, idBon: 'b8', tanggal: '2026-10-07', jam: '10:00', base64: 'A' }, { id: 3, idBon: 'b9', tanggal: '2026-10-07', jam: '08:00', base64: 'A' }, { id: 4, idBon: 'b9', tanggal: '2026-10-07', jam: '09:00' }], 'b9');
    ok('urut foto satu bon: terbaru dulu, bon lain & dokumen tanpa isi dibuang', J(u.map(function (x) { return x.id; })) === J([3, 1]), J(u));
    ok('konstanta: sisi 1600, mutu awal 0,6, sasaran 300 KB, batas 700 KB (< 1 MiB dokumen sesudah base64), 6 foto per bon, koleksi fotoBon', FBN_SISI === 1600 && FBN_MUTU[0] === 0.6 && FBN_TARGET === 300 * 1024 && FBN_BATAS === 700 * 1024 && Math.ceil(FBN_BATAS / 3) * 4 < 1048576 - 4096 && FBN_PALING_BANYAK === 6 && FBN_KOLEKSI === 'fotoBon');
  } catch (e) { gagal.push('JATUH: ' + e + ' ' + (e && e.stack)); }
  selesai = true;
})();
drainMicrotasks();
if (!selesai) gagal.push('janji tidak selesai');
print(J({ lulus: lulus, gagal: gagal }));
"""


def statis(teks=None):
    t = teks or {}
    def baca(p): return t[p] if p in t else open(os.path.join(AKAR, p), encoding='utf-8').read()
    g = []; n = 0
    kol = baca('baru/js/data/koleksi.js')
    n += 1
    if 'fotoBon' in kol: g.append('fotoBon ada di KOLEKSI → didengar terus, ikut baca penuh harian & cadangan')
    fb = baca('baru/js/data/firebase.js')
    m = re.search(r'export async function bacaFotoBon\(idBon\) \{(.*?)\n\}', fb, re.S); n += 1
    if not m or "getDocs(query(collection(db, KOLEKSI_FOTO_BON), where('idBon', '==', String(idBon))))" not in m.group(1) or 'onSnapshot' in m.group(1): g.append('bacaFotoBon bukan baca sekali per bon (getDocs + where idBon)')
    m2 = re.search(r'export async function simpanFotoBon\(data\) \{(.*?)\n\}', fb, re.S); n += 1
    if not m2 or 'antre.tambah' in m2.group(1) or 'pemilikSaja()' not in m2.group(1): g.append('simpanFotoBon menyalin foto ke antre lokal / tidak owner saja')
    m3 = re.search(r'export async function hapusFotoBon\(id, idBon\) \{(.*?)\n\}', fb, re.S); n += 1
    if not m3 or 'pemilikSaja()' not in m3.group(1): g.append('hapusFotoBon tidak owner saja')
    hj = baca('baru/js/layar/harga.js'); n += 1
    if 'type="file" accept="image/*" capture="environment" data-foto-pilih="kamera"' not in hj or 'type="file" accept="image/*" multiple data-foto-pilih="galeri"' not in hj: g.append('input foto: kamera (capture) & galeri tidak lengkap')
    n += 1
    if "akar.addEventListener('change'" not in hj or 'data-foto-pilih' not in hj: g.append('pilihan berkas tidak didengar lewat change')
    n += 1
    if 'opsi.foto.baca(b.id)' not in hj or 'muatFoto(b)' not in hj: g.append('foto tidak dimuat saat lembar bon dibuka')
    idx = baca('baru/index.html'); n += 1
    csp = re.search(r'img-src ([^;]+);', idx)
    if not csp or 'data:' not in csp.group(1) or 'blob:' not in csp.group(1): g.append('CSP img-src tanpa data:/blob:')
    n += 1
    if '<link rel="modulepreload" href="js/layar/foto-bon-logika.js">' not in idx: g.append('modulepreload foto-bon-logika.js belum ada')
    app = baca('baru/js/app.js'); n += 1
    if 'baca: (idBon) => fb.bacaFotoBon(idBon)' not in app: g.append('app.js tidak menyerahkan pembaca foto ke layar Harga')
    cad = baca('baru/js/data/cadangan.js'); n += 1
    if 'fotoBon' in cad: g.append('cadangan memuat fotoBon')
    return n - len(g), g


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    def jalan(isi):
        h, e = uji_wadah_bernama.jalan(isi + '\n' + SKENARIO)
        return (h['lulus'], h['gagal']) if h else (0, ['JSC JATUH: ' + e])
    if '--kontrol' in sys.argv:
        rusak = {
            'ukuran dibesarkan (tanpa batas sisi)': js.replace("const skala = panjang > S ? S / panjang : 1;", "const skala = S / panjang;"),
            'byte base64 tanpa padding': js.replace("const pad = s.endsWith('==') ? 2 : s.endsWith('=') ? 1 : 0;", "const pad = 0;"),
            'berhenti di percobaan pertama walau di atas sasaran': js.replace("      if (hasil.byte <= FBN_TARGET) return Object.assign(hasil, { lebihTarget: false });", "      return Object.assign(hasil, { lebihTarget: false });"),
            'di atas batas tetap dipakai': js.replace("  if (terkecil && terkecil.byte <= FBN_BATAS) return Object.assign(terkecil, { coba, lebihTarget: true });", "  if (terkecil) return Object.assign(terkecil, { coba, lebihTarget: true });"),
            'tanpa batas jumlah foto per bon': js.replace("  if ((ada || []).length >= FBN_PALING_BANYAK)", "  if (false)"),
            'urutan mutu dibalik (ukuran dulu)': js.replace("const FBN_SKALA = [1, 0.8, 0.64, 0.5];", "const FBN_SKALA = [0.5, 0.64, 0.8, 1];"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = jalan(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        statis_rusak = {
            'fotoBon didengar (masuk KOLEKSI)': {'baru/js/data/koleksi.js': open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read().replace("  { nama: 'stokBahanLiteran',", "  { nama: 'fotoBon', urut: 'id', cache: 'fotoBon' },\n  { nama: 'stokBahanLiteran',", 1)},
            'foto disalin ke antre lokal': {'baru/js/data/firebase.js': open(os.path.join(AKAR, 'baru/js/data/firebase.js'), encoding='utf-8').read().replace("  const b = writeBatch(db); b.set(doc(db, KOLEKSI_FOTO_BON, String(d.id)), d);", "  antre.tambah({ id: 'f', dokumen: [d] }); const b = writeBatch(db); b.set(doc(db, KOLEKSI_FOTO_BON, String(d.id)), d);", 1)},
            'kamera tanpa capture': {'baru/js/layar/harga.js': open(os.path.join(AKAR, 'baru/js/layar/harga.js'), encoding='utf-8').read().replace('capture="environment" ', '', 1)},
            'CSP img-src tanpa data:': {'baru/index.html': open(os.path.join(AKAR, 'baru/index.html'), encoding='utf-8').read().replace("img-src 'self' data: blob:;", "img-src 'self' blob:;", 1)},
        }
        for nama, t in statis_rusak.items():
            if any(v == open(os.path.join(AKAR, k), encoding='utf-8').read() for k, v in t.items()): print('KONTROL BASI  ' + nama); kode = 3; continue
            _, g = statis(t)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(js)
    ls, gs = statis()
    print('FOTO BON (jsc kanvas tiruan + statis): %d lulus · %d gagal' % (l + ls, len(g) + len(gs)))
    for x in g + gs: print('   ✗ ' + x)
    sys.exit(0 if not g and not gs else 2)
