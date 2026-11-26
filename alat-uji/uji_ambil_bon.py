#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_ambil_bon.py — paket QR kedua, rules v23 (owner 26 Nov 2026): KARCIS AMBIL NANTI & CEK BON DARI HP. KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  AB titipan: baris karung & kemasan nota ikut dititip (literan / pengganti retur tidak), catatan titip ikut kiriman nota yang SAMA (nota diantar tidak dititip),
     bentuk dokumen = stafAmbilBarang (penjaga kiriman akses.js menerimanya), serahkan sebagian-sebagian (melebihi sisa / ½ karung / pecahan kemasan / kosong
     ditolak), sisa per baris, titipan HABIS, nota DIBATALKAN = titipan gugur, nota yang sudah diarsip tutup buku = titipan tetap, daftar tertua dulu, ringkasan
     barang untuk Cocokkan, baris struk.
  BP cek bon: kode 22 huruf dari pembangkit acak (byte ≥ 248 dibuang), ringkasan = semuaBon & pnNota (sisa per nota menutup), buat (ditolak bila sudah ada / tanpa
     bon), cabut = hapus, tulis ulang HANYA yang berubah (jam tidak dihitung), orang yang bonnya lunas → sisa 0, tautan & pesan WhatsApp.
  ST statis: halaman bon.html (CSP: skrip dari asal sendiri, sambungan hanya ke Firestore, tanpa penyimpanan / tautan keluar), penulis pusat menulis bonPublik
     TANPA atribusi penulis, sinkron cek bon hanya dari owner sesudah semua data terbaca, layar Jual / Pelanggan / Stok tersambung.

    python3 alat-uji/uji_ambil_bon.py            → N lulus · 0 gagal
    python3 alat-uji/uji_ambil_bon.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_faktur  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
AB = 'baru/js/layar/ambil-logika.js'; BP = 'baru/js/layar/bon-publik-logika.js'; JL = 'baru/js/layar/jual-logika.js'; AK = 'baru/js/data/akses.js'
MODUL = bundel_baru.lengkapi([m for m in uji_faktur.MODUL if m not in (AB, BP)] + [AB, BP] + ([AK] if AK not in uji_faktur.MODUL else []))
SUMBER = {'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'jual': 'baru/js/layar/jual.js', 'pelanggan': 'baru/js/layar/pelanggan.js', 'stok': 'baru/js/layar/stok.js',
          'app': 'baru/js/app.js', 'fb': 'baru/js/data/firebase.js', 'html': 'baru/bon.html', 'hal': 'baru/js/bon-halaman.js', 'struk': 'baru/js/layar/struk-logika.js', 'index': 'baru/index.html'}
JAM = "var __KINI = new Date('2026-11-28T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(i, tgl, cara, nama, trx, n, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'hargaTotal': n,
         'hppTotalSaatJual': round(n * 0.9), 'trxId': trx, 'jumlahKarung': 1, 'beratKarungAcuan': 50}
    d.update(x); return d


KOTAK = {
    'penjualan': [
        jual(102, '2026-10-20', 'Kredit', 'Bu Sari', 'a1', 300000), jual(104, '2026-11-10', 'Kredit', 'Bu Sari', 'a2', 200000),
        jual(105, '2026-11-20', 'Kredit', 'Bu Sari', 'a3', 150000),
        jual(301, '2026-11-26', 'Tunai', 'Pak Budi', 'T1', 1400000, jumlahKarung=2),
        jual(302, '2026-11-26', 'Tunai', 'Pak Budi', 'T1', 140000, jenis='kemasan', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=2),
        jual(303, '2026-11-26', 'Tunai', 'Pak Budi', 'T1', 24000, jenis='literan', jumlahLiter=2),
        jual(304, '2026-11-26', 'Tunai', 'Pak Budi', 'T1', 3000, jenis='wadah', namaProduk='Karung bekas', jumlahUnit=1, jumlahKarung=0),
        jual(311, '2026-11-27', 'Tunai', 'Bu Ani', 'T2', 700000, dibatalkan=True),
    ],
    'piutangMutasi': [{'id': 201, 'tanggal': '2026-11-12', 'jam': '10:00', 'tipe': 'bayar', 'namaPelanggan': 'Bu Sari', 'nominal': 350000, 'caraBayar': 'Tunai'}],
    'pelangganCatatan': [{'id': 'bu sari', 'nama': 'Bu Sari', 'catatan': 'warung', 'kontak': '0812 0000 2222'}],
    'ambilBarang': [
        {'id': 'ab-2', 'tanggal': '2026-11-27', 'jam': '08:00', 'jenis': 'titip', 'trxId': 'T2', 'namaPelanggan': 'Bu Ani', 'isi': [{'idBaris': '311', 'jenis': 'karung', 'nama': 'Angsa karung 50 kg', 'jumlah': 1, 'satuan': 'karung'}], 'catatan': ''},
        {'id': 'ab-9', 'tanggal': '2025-12-30', 'jam': '08:00', 'jenis': 'titip', 'trxId': 'ARSIP', 'namaPelanggan': 'Pak Lama', 'isi': [{'idBaris': '9', 'jenis': 'kemasan', 'nama': 'Kembang 5 kg', 'jumlah': 3, 'satuan': 'kemasan'}], 'catatan': ''},
    ],
    'bonPublik': [], 'aturanToko': [],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-11-28T10:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-11-28', jam: '10:00', kini: '2026-11-28T03:00:00.000Z', idUnik: function () { nId += 1; return nId + 0.5; } };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var pj = function (trx) { return ambilPenjualanSemua().filter(function (p) { return String(p.trxId) === trx; }); };

// ==================== AB · TITIPAN ====================
var isi = abIsiTitip(pj('T1'));
ok('AB: karung & kemasan ikut dititip (nama, jumlah, satuan, id baris); literan & wadah tidak', J(isi) === J([{ idBaris: '301', jenis: 'karung', nama: 'Angsa karung 50 kg', jumlah: 2, satuan: 'karung' }, { idBaris: '302', jenis: 'kemasan', nama: 'Kembang 5 kg', jumlah: 2, satuan: 'kemasan' }]), J(isi));
ok('AB: pengganti retur & jumlah 0 tidak dititip', abIsiTitip([{ id: 1, jenis: 'karung', jumlahKarung: 1, penggantiRetur: true }, { id: 2, jenis: 'kemasan', jumlahUnit: 0 }]).length === 0);
var T = abSusunTitip('T1', ' Pak Budi ', isi, W).data;
ok('AB: dokumen titip — id = kolom id (ab-…), jenis titip, trxId teks, nama dirapikan, kolom = AB_KOLOM', /^ab-[0-9a-zA-Z-]+$/.test(T.id) && T.jenis === 'titip' && T.trxId === 'T1' && T.namaPelanggan === 'Pak Budi' && Object.keys(T).every(function (k) { return AB_KOLOM.indexOf(k) >= 0; }), J(T));
ok('AB: penjaga kiriman staf (akses.js = stafAmbilBarang) menerima dokumen titip & ambil penyusun; menolak kolom asing / jenis lain / isi kosong',
  ambilBarangSah(T) && ambilBarangSah({ id: 'ab-x', tanggal: '2026-11-28', jam: '10:00', jenis: 'ambil', trxId: 'T1', namaPelanggan: 'x', isi: [{ idBaris: '301', jumlah: 1 }], catatan: '' })
  && !ambilBarangSah(Object.assign({}, T, { hargaTotal: 1 })) && !ambilBarangSah(Object.assign({}, T, { jenis: 'batal' })) && !ambilBarangSah(Object.assign({}, T, { isi: [] })));
terapkanKeCache([{ koleksi: 'ambilBarang', data: T }]);
var K1 = abKeadaan('T1');
ok('AB: keadaan titipan — dua baris, belum ada yang diambil', K1 && K1.isi.length === 2 && K1.isi.every(function (x) { return x.diambil === 0 && x.sisa === x.jumlah; }) && !K1.habis && !K1.batal, J(K1));
ok('AB: serahkan melebihi sisa DITOLAK', /sisa titipan 2 karung/.test(String(abSusunAmbil('T1', { '301': '3' }, W).tolak)));
ok('AB: setengah karung boleh, pecahan kemasan & ⅓ karung DITOLAK, kosong DITOLAK', !abSusunAmbil('T1', { '301': '0,5' }, W).tolak && !!abSusunAmbil('T1', { '302': '1,5' }, W).tolak && !!abSusunAmbil('T1', { '301': '0,3' }, W).tolak && !!abSusunAmbil('T1', {}, W).tolak);
var A1 = abSusunAmbil('T1', { '301': '1' }, W, ' diambil anaknya ');
ok('AB: serahkan sebagian = catatan ambil (isi id baris + jumlah, catatan dirapikan), kabar menyebut sisanya', A1.dokumen && A1.dokumen[0].data.jenis === 'ambil' && J(A1.dokumen[0].data.isi) === J([{ idBaris: '301', jumlah: 1 }]) && A1.dokumen[0].data.catatan === 'diambil anaknya' && !A1.habis && /sisa: Angsa karung 50 kg 1 karung, Kembang 5 kg 2 kemasan/.test(A1.patch.kabar) && ambilBarangSah(A1.dokumen[0].data), J(A1));
terapkanKeCache(A1.dokumen);
var K2 = abKeadaan('T1');
ok('AB: sesudah diambil sebagian — sisa per baris & riwayat', K2.isi[0].diambil === 1 && K2.isi[0].sisa === 1 && K2.isi[1].sisa === 2 && K2.riwayat.length === 1 && /Angsa karung 50 kg 1/.test(K2.riwayat[0].teks), J(K2));
var A2 = abSusunAmbil('T1', { '301': '1', '302': '2' }, W); terapkanKeCache(A2.dokumen);
ok('AB: sisa diambil semua → HABIS (kabar), tidak bisa diserahkan lagi', A2.habis && /HABIS/.test(A2.patch.kabar) && abKeadaan('T1').habis && /sudah diambil/.test(String(abSusunAmbil('T1', { '301': '1' }, W).tolak)), J(A2.patch));
ok('AB: nota DIBATALKAN → titipan gugur (tidak di daftar, tidak bisa diserahkan, tidak di struk)', abKeadaan('T2').batal && !abDaftar().some(function (k) { return k.trxId === 'T2'; }) && /dibatalkan/.test(String(abSusunAmbil('T2', { '311': '1' }, W).tolak)) && abBarisStruk('T2').length === 0);
ok('AB: nota yang sudah diarsip tutup buku (barisnya tidak ada lagi) — titipannya TETAP', !abKeadaan('ARSIP').batal && abDaftar().some(function (k) { return k.trxId === 'ARSIP'; }));
ok('AB: ringkasan barang untuk Cocokkan (barang titipan per nama)', J(abRingkasBarang()) === J([{ nama: 'Kembang 5 kg', satuan: 'kemasan', jumlah: 3, nota: 1 }]), J(abRingkasBarang()));
ok('AB: baris struk — DITITIP + sisa; habis = sudah diambil semua; bukan titipan = kosong', abBarisStruk('ARSIP')[0] === 'DITITIP DI TOKO — ambil dengan struk ini:' && /Kembang 5 kg 3 kemasan/.test(abBarisStruk('ARSIP')[1]) && /sudah diambil semua/.test(abBarisStruk('T1')[0]) && abBarisStruk('a1').length === 0, J([abBarisStruk('ARSIP'), abBarisStruk('T1')]));
// nota dari keranjang: catatan titip ikut kiriman yang sama
var itemK = { jenis: 'karung', merkSumber: 'Angsa', namaProduk: 'Angsa (karung utuh)', beratKarungAcuan: 50, jumlahKarung: 2, totalKg: 100, hargaTotal: 1400000, hppTotalSaatJual: 1300000, label: 'Angsa 50 kg', satuan: 'karung', jumlah: 2, hargaSatuan: 700000, hargaAsli: 700000 };
var sN = Object.assign(keadaanAwal(), { keranjang: [{ id: 'b1', trx: itemK }], pelanggan: 'Pak Budi', cara: 'QRIS', ambilNanti: true, sekarang: KINI });
var N1 = susunNotaDokumen(sN, W); var tt = (N1.dokumen || []).filter(function (x) { return x.koleksi === 'ambilBarang'; });
ok('AB: nota "diambil nanti" → SATU catatan titip di kiriman yang sama, menunjuk baris nota & trxId-nya; kabar menyebut DITITIP', tt.length === 1 && tt[0].data.trxId === String(N1.trxId) && tt[0].data.isi[0].idBaris === String(N1.idPenjualan[0]) && N1.titip === true && /DITITIP/.test(N1.ringkas), J(N1.ringkas));
ok('AB: tanpa saklar → tanpa titipan', susunNotaDokumen(Object.assign({}, sN, { ambilNanti: false }), W).dokumen.every(function (x) { return x.koleksi !== 'ambilBarang'; }));
ok('AB: keadaan awal tanpa saklar titip', keadaanAwal().ambilNanti === false);

// ==================== BP · CEK BON ====================
var urutan = function (arr) { var i = 0; return function (n) { var b = new Uint8Array(n); for (var j = 0; j < n; j++) { b[j] = arr[i % arr.length]; i++; } return b; }; };
var kode = bpKodeBaru(urutan([255, 249, 0, 1, 61, 62, 247]));
ok('BP: kode 22 huruf [A-Za-z0-9], byte ≥ 248 DIBUANG (tidak dibagi rata)', kode.length === BP_PANJANG && /^[A-Za-z0-9]{22}$/.test(kode) && kode.slice(0, 5) === 'AB9A9', kode);
ok('BP: kode sah = 20–64 huruf alfanumerik', bpKodeSah(kode) && !bpKodeSah('abc') && !bpKodeSah('x'.repeat(22) + '/') && !bpKodeSah(''));
var R = bpRingkas('Bu Sari', KINI);
ok('BP: ringkasan = buku bon (sisa 300.000) + nota belum lunas per pembagian buku bon (10 Nov 150.000, 20 Nov 150.000) + jatuh tempo', R && R.sisa === 300000 && J(R.nota.map(function (x) { return [x.tanggal, x.sisa]; })) === J([['2026-11-10', 150000], ['2026-11-20', 150000]]) && R.nota.every(function (x) { return /^\d{4}-\d\d-\d\d$/.test(x.jatuhTempo); }) && R.nama === 'Bu Sari', J(R));
ok('BP: ringkasan TIDAK memuat data lain (kunci, nama, sisa, nota, toko saja)', J(Object.keys(R).sort()) === J(['kunci', 'nama', 'nota', 'sisa', 'toko']));
var B1 = bpSusunBuat('Bu Sari', KINI, W, urutan([1, 2, 3, 4, 5]));
ok('BP: buat tautan = satu dokumen bonPublik/<kode> berisi ringkasan + jam diperbarui', B1.dokumen && B1.dokumen[0].koleksi === 'bonPublik' && B1.dokumen[0].data.id === B1.kode && B1.dokumen[0].data.sisa === 300000 && B1.dokumen[0].data.diperbarui === W.kini, J(B1));
ok('BP: tanpa bon → ditolak', !!bpSusunBuat('Orang Baru', KINI, W).tolak);
terapkanKeCache(B1.dokumen);
ok('BP: sudah ada → ditolak (cabut dulu); bpUntuk menemukannya per nama', !!bpSusunBuat('bu sari', KINI, W).tolak && bpUntuk('BU SARI').id === B1.kode);
ok('BP: ringkasan sama (jam berbeda tidak dihitung) → tidak ada yang ditulis ulang', bpPerluTulis(KINI, { kini: '2026-11-29T00:00:00.000Z' }).length === 0);
terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 202, tanggal: '2026-11-28', jam: '09:30', tipe: 'bayar', namaPelanggan: 'Bu Sari', nominal: 150000, caraBayar: 'Tunai' } }]);
var U = bpPerluTulis(KINI, { kini: '2026-11-28T03:30:00.000Z' });
ok('BP: bon berubah (bayar 150.000) → ringkasan ditulis ulang: sisa 150.000, satu nota, jam baru', U.length === 1 && U[0].data.id === B1.kode && U[0].data.sisa === 150000 && U[0].data.nota.length === 1 && U[0].data.diperbarui === '2026-11-28T03:30:00.000Z', J(U));
terapkanKeCache(U); terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 203, tanggal: '2026-11-28', jam: '09:40', tipe: 'bayar', namaPelanggan: 'Bu Sari', nominal: 150000, caraBayar: 'Tunai' } }]);
var U2 = bpPerluTulis(KINI, W);
ok('BP: bon lunas → ringkasan sisa 0 tanpa nota (tautan tetap hidup)', U2.length === 1 && U2[0].data.sisa === 0 && U2[0].data.nota.length === 0, J(U2));
terapkanKeCache([{ koleksi: 'bonPublik', data: { id: 'Z'.repeat(22), kunci: 'orang hilang', nama: 'Orang Hilang', sisa: 50000, nota: [{ tanggal: '2026-10-01', sisa: 50000, jatuhTempo: '2026-10-15', faktur: '' }], toko: 'Toko Beras M.IQBAL', diperbarui: '2026-10-01T00:00:00.000Z' } }]);
var U3 = bpPerluTulis(KINI, W).filter(function (x) { return x.data.id === 'Z'.repeat(22); });
ok('BP: orang yang sudah tidak ada di buku bon (mis. sesudah tutup buku) → ringkasan sisa 0, bukan sisa lama', U3.length === 1 && U3[0].data.sisa === 0 && U3[0].data.nota.length === 0 && U3[0].data.nama === 'Orang Hilang', J(U3));
var C1 = bpSusunCabut('Bu Sari');
ok('BP: cabut = hapus dokumennya (tautan lama mati), tanpa tulis', J(C1.hapus) === J([{ koleksi: 'bonPublik', id: B1.kode }]) && C1.dokumen.length === 0 && !!bpSusunCabut('Pak Budi').tolak);
ok('BP: tautan = folder /baru/ + bon.html#k=<kode>; proyek lain disebut (p=), proyek toko tidak', bpTautan('KODE', 'https://x.y/baru/') === 'https://x.y/baru/bon.html#k=KODE' && bpTautan('KODE', 'https://x.y/baru/', 'contoh-toko-beras') === 'https://x.y/baru/bon.html#k=KODE&p=contoh-toko-beras' && bpTautan('KODE', '', 'toko-beras-m-iqbal') === 'bon.html#k=KODE');
ok('BP: pesan WhatsApp memuat tautan & larangan membagikan', /https:\/\/x\.y\/baru\/bon\.html#k=KODE/.test(bpPesanWa('Bu Sari', 'https://x.y/baru/bon.html#k=KODE')) && /jangan dibagikan/.test(bpPesanWa('Bu Sari', 'u')));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

RUSAK = [
    ('titip: literan ikut dititip', AB, "filter((p) => p && (p.jenis === 'karung' || p.jenis === 'kemasan') && !p.penggantiRetur)", "filter((p) => p && !p.penggantiRetur)"),
    ('ambil: melebihi sisa diterima', AB, "if (n > x.sisa + 1e-9) {", "if (false) {"),
    ('ambil: pecahan kemasan diterima', AB, "(x.satuan === 'karung' ? (n * 2) % 1 !== 0 : n % 1 !== 0)", "(x.satuan === 'karung' ? (n * 2) % 1 !== 0 : false)"),
    ('ambil: riwayat ambil tidak mengurangi sisa', AB, "diambil[k] = abAngka((diambil[k] || 0) + abAngka(x.jumlah));", "diambil[k] = 0;"),
    ('titip: nota dibatalkan tetap di daftar', AB, ".filter((k) => k && !k.habis && !k.batal)", ".filter((k) => k && !k.habis)"),
    ('titip: nota yang diarsip dianggap batal', AB, "return r.length > 0 && r.every((p) => p.dibatalkan);", "return r.every((p) => p.dibatalkan);"),
    ('nota: titipan tidak ikut kiriman', JL, "  if (isiTitip.length) dokumen.push(abSusunTitip(trxId, nama, isiTitip, w));\n", ""),
    ('nota: titipan ikut walau saklar mati', JL, "const isiTitip = s.ambilNanti && !antar ?", "const isiTitip = !antar ?"),
    ('cek bon: byte ≥ 248 tidak dibuang (tidak merata)', BP, "if (b[i] < 248) k += BP_HURUF[b[i] % 62];", "k += BP_HURUF[b[i] % 62];"),
    ('cek bon: jam ikut dibandingkan (tulis tiap kali)', BP, "return bpSama(d, R) ? null :", "return false ? null :"),
    ('cek bon: lunas = ringkasan tidak ditulis', BP, "|| { kunci: d.kunci, nama: d.nama, sisa: 0, nota: [], toko: 'Toko Beras M.IQBAL' }", "|| null; if (!R) return null"),
    ('cek bon: buat dua tautan untuk satu orang', BP, "  if (bpUntuk(nama)) return { tolak:", "  if (false) return { tolak:"),
    ('akses: penjaga kiriman titipan menerima kolom asing', AK, "if (Object.keys(d).some((k) => AMBIL_KOLOM.indexOf(k) < 0)) return false;\n  return /^\\d{4}", "\n  return /^\\d{4}"),
]
STATIS = [
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_ambil_bon.py && python3 alat-uji/uji_ambil_bon.py --kontrol']),
    ('BACA-DULU menyebut titipan & cek bon', 'baca', ['Karcis ambil nanti', 'ambilBarang', 'bonPublik', 'bon.html', 'rules v23']),
    ('bon.html: CSP ketat (skrip asal sendiri, sambungan hanya Firestore, tanpa base/form), tanpa skrip sebaris, noindex & no-referrer', 'html',
     ["content=\"default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src https://firestore.googleapis.com; base-uri 'none'; form-action 'none'\"",
      '<script src="js/bon-halaman.js"></script>', '<meta name="robots" content="noindex, nofollow">', '<meta name="referrer" content="no-referrer">']),
    ('halaman cek bon: kode dari # (tidak ke server), satu GET tanpa kredensial, 404 = tautan dicabut', 'hal',
     ["String(location.hash || '')", "credentials: 'omit'", "if (r.status === 404) { pesan('Tautan tidak berlaku'", "/documents/bonPublik/' + encodeURIComponent(H.kode)"]),
    ('penulis pusat: bonPublik ditulis APA ADANYA (tanpa nama / uid / perangkat / lokasi penulis)', 'fb', ["if (kkMentah(x.koleksi) || x.koleksi === 'bonPublik') { b.set(doc(db, x.koleksi, String(x.data.id)), x.data);"]),
    ('app.js: ringkasan cek bon ditulis dari OWNER saja, sesudah semua data terbaca, bukan simulasi', 'app',
     ["a.jenis !== 'owner' || sumberData().jenis !== 'firestore' || statusFb.offline || !(statusFb.koleksiTotal > 0 && statusFb.koleksiSiap >= statusFb.koleksiTotal)) return;", 'dengarkan(sinkronCekBon);']),
    ('Pelanggan: cek bon hanya untuk owner, cabut bertanya dulu', 'pelanggan', ["${!bukanOwner(opsi.akun ? opsi.akun() : null) && (O.sisa > 0 || BP.bpUntuk(O.nama)) ? gambarCekBon(s, O) : ''}", 'data-aksi="cekBonCabutTanya"', 'YA, CABUT']),
    ('Jual: saklar diambil nanti, daftar titipan, lembar serahkan, tombol serahkan di pita scan', 'jual',
     ['data-aksi="ambilNantiSaklar"', 'data-aksi="bukaTitipan"', "if (s.lembar === 'ambil') return gambarAmbil(s, L1, muncul, kepala);", 'data-aksi="ambilBuka" data-trx="${K.titip.trxId}"', "const r = AB.abSusunAmbil(s.abTrx, isi, tkWaktu(), s.abCatatan || '');"]),
    ('Stok › Cocokkan menyebut barang titipan', 'stok', ['data-k="cocok-titipan"', 'AB.abRingkasBarang()']),
    ('struk menulis baris titipan', 'struk', ["if (nota.berlaku && nota.trxId) abBarisStruk(nota.trxId).forEach("]),
    ('index.html memuat modul baru lebih dulu', 'index', ['<link rel="modulepreload" href="js/layar/ambil-logika.js">', '<link rel="modulepreload" href="js/layar/bon-publik-logika.js">']),
]
RUSAK_STATIS = [
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_ambil_bon.py', 'true'),
    ('bon.html boleh menyambung ke mana saja', 'html', 'connect-src https://firestore.googleapis.com;', 'connect-src *;'),
    ('penulis pusat menempelkan atribusi ke bonPublik', 'fb', "if (kkMentah(x.koleksi) || x.koleksi === 'bonPublik') {", "if (kkMentah(x.koleksi)) {"),
    ('cek bon ditulis tanpa menunggu semua data', 'app', " || !(statusFb.koleksiTotal > 0 && statusFb.koleksiSiap >= statusFb.koleksiTotal)) return;", ") return;"),
]


def bundel(teks):
    return bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)


def jalan(teks):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return None, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    return json.loads(out), None


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:140])
    hal = src['hal']
    for terlarang in ('localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'innerHTML', 'eval(', 'http://'):
        if terlarang in hal: g.append('halaman cek bon memakai ' + terlarang)
    if '<script>' in src['html'] or 'onclick' in src['html'].lower() or 'href="http' in src['html']: g.append('bon.html: skrip sebaris / penangan sebaris / tautan keluar')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); h, e = jalan(T); g = e if h is None else h['gagal']
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        print('KONTROL ' + ('LULUS' if kode == 0 else 'GAGAL'))
        sys.exit(kode)
    h, e = jalan(teks); ls, gs = statis(src)
    g = e if h is None else h['gagal']
    print('KOTAK PASIR: %d lulus · %d gagal' % (0 if h is None else h['lulus'], len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    sys.exit(1 if g or gs else 0)
