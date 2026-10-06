#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kisi_ss2.py — audit 39b no. 22 (KOTAK PASIR, angka & nama CONTOH, jsc saja, TANPA peramban).
Kisi SS2 (aturanToko/peran) harus DITEGAKKAN untuk akun bukan-owner — bukan cuma 4 tombol:
  · nego / potongan nota (kisi bawaan: Ben "minta owner", karyawan "tidak"; server tidak pernah membukanya) ditolak penjaga & tombolnya mati;
  · hak yang DIPUTAR owner jadi "minta owner"/"tidak" (jual tunai, jual bon, terima bon, pelanggan baru, adukan, isi ulang) ditolak penjaga;
  · kisi bawaan tidak menolak pekerjaan harian (nota tunai, bon Ben + bayar sebagian, terima bon, orang baru, adukan, isi ulang, struk).
Sumber hak = ssAtur('peran').hak[peran] — jalur yang SAMA dengan app.js setelSumberHak.

    python3 alat-uji/uji_kisi_ss2.py            → N lulus · M gagal (keluar 2 bila gagal)
    python3 alat-uji/uji_kisi_ss2.py --kontrol  → perbaikan yang dirusak wajib berbunyi (keluar 3 bila ada yang diam)
    python3 alat-uji/uji_kisi_ss2.py <akar>     → jalankan atas salinan repo lain (mis. main, untuk melihatnya GAGAL)
"""
import os, sys, json, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__))
AKAR = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else os.path.join(SINI, '..'))
sys.path.insert(0, os.path.join(AKAR, 'alat-uji'))
import bundel_baru  # noqa: E402
import peta_akses   # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = peta_akses.MODUL_KIRIM + ['baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/sistem-logika.js']

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
var J = function (x) { return JSON.stringify(x); };
var W = { tanggal: '2026-09-24', jam: '10:00', kini: '2026-09-24T03:00:00.000Z', idUnik: (function () { var n = 5000; return function () { n += 1; return n; }; })() };
var KINI = new Date(Date.now());
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
// KOTAK PASIR
pasok('penjualan', [{ id: 11, trxId: 11, tanggal: '2026-09-20', jam: '09:00', caraBayar: 'Kredit', namaPelanggan: 'Pembeli Contoh', hargaTotal: 500000, jenis: 'karung', merkSumber: 'Angsa', totalKg: 50 }]);
pasok('batchMasuk', [{ id: 'b1', tanggal: '2026-09-01', merkList: [{ merk: 'Angsa', satuan: 'karung', beratKarung: 50, totalKg: 5000, subtotalHarga: 65000000, hargaPerKg: 13000 }] },
  { id: 'b2', tanggal: '2026-09-20', jam: '08:00', pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: [{ id: '1', merk: 'Wadah Angsa', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, stokWadah: 'Angsa' }] }]);
pasok('wadahLiteran', [{ id: 9001, tanggal: '2026-09-01', jam: '07:00', tipe: 'atur', penuhKg: 50, puncakKg: 60, isiUlangKg: 10, takarKg: 1.8, daftar: ['Angsa'] },
  { id: 9002, tanggal: '2026-09-20', jam: '08:00', tipe: 'isi', wadah: 'Angsa', isiKg: 0, stokWadah: 'Wadah Angsa', pindahAwal: true }]);
// kisi tersimpan = bentuk dokumen aturanToko/peran di cadangan toko (tanpa isiUlang → bawaan mengisinya); hak() = jalur app.js setelSumberHak
var KISI0 = { ben: { hapus: 'tidak', jualBon: 'sendiri', terimaBon: 'sendiri', jualTunai: 'sendiri', uangKeluar: 'owner', koreksi: 'owner', atur: 'tidak', kedatangan: 'sendiri', hargaBeli: 'tidak', nego: 'owner', hitungLaci: 'sendiri', adukan: 'sendiri', pelangganBaru: 'sendiri' },
  karyawan: { atur: 'tidak', jualTunai: 'sendiri', nego: 'tidak', jualBon: 'owner', terimaBon: 'sendiri', hitungLaci: 'tidak', koreksi: 'tidak', adukan: 'sendiri', pelangganBaru: 'sendiri', kedatangan: 'sendiri', hapus: 'tidak', hargaBeli: 'tidak', uangKeluar: 'tidak' } };
function setelKisi(ubah) { var k = JSON.parse(J(KISI0)); Object.keys(ubah || {}).forEach(function (p) { Object.keys(ubah[p]).forEach(function (t) { k[p][t] = ubah[p][t]; }); });
  pasok('aturanToko', [{ id: 'peran', hak: k, batasSekaligus: 300000, jatahBen: 50, jejak: [] }]); }
// = app.js setelSumberHak: kisi peran + jatah nego akun (owner 7 Okt, JS2-C)
function hak(akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); }
function kirim(akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false, lama: null }; }), [], hak(akun), KINI); }
var KARUNG = function () { return { jenis: 'karung', merkSumber: 'Angsa', jumlahKarung: 1, totalKg: 50, hargaTotal: 690000, hargaSatuan: 690000, hargaAsli: 690000, jumlah: 1, hppTotalSaatJual: 650000 }; };
function nota(cara, uang, ubah) { var s = Object.assign({ keranjang: [{ id: 'b0', trx: KARUNG() }], pelanggan: 'Pembeli Contoh', cara: cara, uang: uang, potongan: 0 }, ubah || {}); return susunNotaDokumen(s, W).dokumen; }
// owner 7 Okt (JS2-C): nego OWNER di bawah modal butuh alasan — bahan uji "nego dalam" memakai alasan supaya baris negonya memang terbentuk
function notaNego(harga, akun) { var s = { keranjang: [{ id: 'b0', trx: KARUNG() }], pelanggan: 'Pembeli Contoh', cara: 'Tunai', uang: 1e9, potongan: 0, negoAlasan: 'bahan uji', negoAkun: akun || null, negoHak: akun ? hak(akun).nego : 'sendiri' }; var r = terapkanNego(s, 'b0', harga); return nota('Tunai', 1e9, { keranjang: r.keranjang || s.keranjang }); }
var YAKIN = { bahan: true, kemasan: true, kantongKosong: true, kantong: true, susut: true };
function aduk() { return susunSimpanAdukan({ tanggal: '2026-09-24', bahan: [{ merk: 'Angsa', kg: '10' }], bahanKemasan: [], hasil: [{ nama: 'Hasil Contoh', ukuran: '5', unit: '2', kantongJenis: '5kg_kembangbmw', kantongJumlah: '2' }], upah: '0', batasHasil: 8 }, W, YAKIN).dokumen; }
function bayarBon() { return susunBayarBon(KINI, 'pembeli contoh', '100.000', 'Tunai', '', '', W).dokumen; }
function orangBaru() { return susunOrangBaru(KINI, 'Orang Baru Contoh', W).dokumen; }
function isiUlang() { return wbSusunIsiUlangTiga('Angsa', 'Angsa', { jenis: 'setengah' }, W, null, {}).dokumen; }
var MINTA = KALIMAT_MINTA_OWNER;

// ---- 1 · NEGO & POTONGAN (kisi bawaan; server tidak pernah membuka nego untuk bukan-owner)
setelKisi();
var dNego = notaNego(500), dPot = nota('Tunai', 1e9, { potongan: 689500 }), dSama = notaNego(690000);
ok('bahan uji: nota nego Rp500 (owner, di bawah modal, beralasan) membawa negoSelisih −689.500; potongan Rp689.500 membawa potonganTransaksi; nego ke harga yang sama = kembali ke katalog (tanpa negoSelisih)',
  dNego[0].data.negoSelisih === -689500 && dNego[0].data.negoStatus === 'bawahModal' && dPot[0].data.potonganTransaksi === 689500 && !dSama[0].data.negoSelisih, J([dNego[0].data.negoSelisih, dNego[0].data.negoStatus, dPot[0].data.potonganTransaksi, dSama[0].data.negoSelisih]));
var n1 = kirim(KRY, dNego), n2 = kirim(BEN, dNego), n3 = kirim(KRY, dPot), n4 = kirim(BEN, dPot), n5 = kirim(OWN, dNego);
ok('nego: karyawan (kisi "tidak") menjual karung Rp690.000 seharga Rp500 → DITOLAK penjaga "Peran Karyawan tidak boleh nego …"', /^Peran Karyawan tidak boleh nego/.test(n1.tolak || ''), J(n1));
ok('nego: Ben (kisi "minta owner", alurnya belum ada) → DITOLAK "Perlu persetujuan owner"', n2.tolak === MINTA, J(n2));
ok('potongan nota = nego: karyawan potong Rp689.500 → DITOLAK; Ben → DITOLAK minta owner', /^Peran Karyawan tidak boleh nego/.test(n3.tolak || '') && n4.tolak === MINTA, J([n3, n4]));
ok('owner tetap bebas nego (0 access call)', !n5.tolak && n5.accessCall === 0, J(n5));
var n6 = kirim(KRY, dSama);
ok('kontrol: lembar nego dipakai tapi harganya tetap harga katalog (negoSelisih 0) → BOLEH (bukan nego)', !n6.tolak, J(n6));
setelKisi({ ben: { nego: 'sendiri' } }); var n7 = kirim(BEN, dNego);
ok('nego: owner memutar Ben jadi "boleh sendiri" → tetap DITOLAK minta owner karena server belum membukanya (SERVER_BUKA tanpa nego) — sama dengan kisi "tertutup server"',
  n7.tolak === MINTA && ssPeran().tampil('ben', 'nego').label === 'tertutup server', J([n7, ssPeran().tampil('ben', 'nego')]));
// owner 7 Okt (JS2-C): nego DALAM JATAH orangnya bukan "nego di bawah jatah margin" — Ben (jatah bawaan 50 %) boleh sendiri, karyawan (0 %) tidak
setelKisi(); var dJatah = notaNego(670000, BEN), n8 = kirim(BEN, dJatah);
ok('jatah: Ben menawar karung Rp690.000 (modal Rp650.000) jadi Rp670.000 = batas jatah 50 % → baris bertanda jatah, penjaga MENGIZINKAN', dJatah[0].data.negoStatus === 'jatah' && dJatah[0].data.negoBatas === 670000 && dJatah[0].data.negoJatah === 50 && !n8.tolak, J([dJatah[0].data, n8]));
var dJatahK = JSON.parse(J(dJatah)); var n9 = kirim(KRY, dJatahK);
ok('jatah: baris yang sama dikirim KARYAWAN (jatah 0 %, kisi "tidak") → DITOLAK — jatah di baris lebih besar dari jatah akunnya', /^Peran Karyawan tidak boleh nego/.test(n9.tolak || ''), J(n9));
var dPalsu = JSON.parse(J(dJatah)); dPalsu[0].data.negoSelisih = -25000; dPalsu[0].data.hargaTotal = 665000; var n10 = kirim(BEN, dPalsu);
ok('jatah: baris bertanda "jatah" tapi harganya Rp665.000 < batas Rp670.000 → DITOLAK minta owner', n10.tolak === MINTA, J(n10));
var dSetuju = JSON.parse(J(dPalsu)); dSetuju[0].data.negoStatus = 'disetujui'; dSetuju[0].data.negoSetujuId = 'ps1'; var n11 = kirim(BEN, dSetuju), n12 = (function () { var d = JSON.parse(J(dSetuju)); delete d[0].data.negoSetujuId; return kirim(BEN, d); })();
ok('jatah: nego di bawah jatah yang DISETUJUI owner (negoSetujuId) → boleh; tanda disetujui tanpa id persetujuan → DITOLAK', !n11.tolak && n12.tolak === MINTA, J([n11, n12]));
var dLama = JSON.parse(J(dJatah)); delete dLama[0].data.negoStatus; var n13 = kirim(BEN, dLama);
ok('jatah: nego bentuk lama (tanpa negoStatus) dari Ben → tetap DITOLAK minta owner', n13.tolak === MINTA, J(n13));
pasok('aturanToko', [{ id: 'peran', hak: KISI0, batasSekaligus: 300000, jatahBen: 30, jejak: [] }]); var n14 = kirim(BEN, dJatah);
ok('jatah: owner menurunkan jatah Ben jadi 30 % → baris bertanda jatah 50 % DITOLAK (jatah baris > jatah akun)', n14.tolak === MINTA, J(n14));
setelKisi();

// ---- 2 · kisi bawaan: pekerjaan harian TIDAK ditolak (tanpa tolak palsu)
setelKisi();
var b = { tunaiK: kirim(KRY, nota('Tunai', 1e9)), qrisK: kirim(KRY, nota('QRIS', 0)), bonB: kirim(BEN, nota('Kredit', 0)), sebagianB: kirim(BEN, nota('Tunai', 1000)),
  bayarK: kirim(KRY, bayarBon()), orangK: kirim(KRY, orangBaru()), adukK: kirim(KRY, aduk()), isiK: kirim(KRY, isiUlang()), isiB: kirim(BEN, isiUlang()),
  strukK: kirim(KRY, [susunStrukKeluar({ trxId: 11, nama: 'Pembeli Contoh', total: 70000 }, 'cetak', W, '')]) };
ok('kisi bawaan: karyawan nota tunai & QRIS, Ben nota bon & bayar sebagian (dengan pelunasan notaTrxId), karyawan terima bon, orang baru, adukan, isi ulang (Ben juga), struk → SEMUA boleh',
  Object.keys(b).every(function (k) { return !b[k].tolak; }), J(b));
var kb = kirim(KRY, nota('Kredit', 0));
ok('kisi bawaan: karyawan jual BON tetap ditolak minta owner (seperti sebelumnya)', kb.tolak === MINTA, J(kb));

// ---- 3 · hak yang DIPUTAR owner berlaku di penjaga
var putar = function (p, t, v) { var u = {}; u[p] = {}; u[p][t] = v; setelKisi(u); };
putar('karyawan', 'jualTunai', 'tidak'); var r1 = kirim(KRY, nota('Tunai', 1e9));
ok('diputar: karyawan jual tunai → "tidak" → nota tunai DITOLAK "Peran Karyawan tidak boleh jual tunai …"', /^Peran Karyawan tidak boleh jual tunai/.test(r1.tolak || ''), J(r1));
putar('ben', 'jualBon', 'owner'); var r2 = kirim(BEN, nota('Kredit', 0)), r2b = kirim(BEN, nota('Tunai', 1000));
ok('diputar: Ben jual bon → "minta owner" → nota bon & bayar sebagian DITOLAK minta owner', r2.tolak === MINTA && r2b.tolak === MINTA, J([r2, r2b]));
putar('karyawan', 'terimaBon', 'tidak'); var r3 = kirim(KRY, bayarBon());
ok('diputar: karyawan terima bon → "tidak" → pembayaran bon DITOLAK "Peran Karyawan tidak boleh terima pembayaran bon"', /^Peran Karyawan tidak boleh terima pembayaran bon/.test(r3.tolak || ''), J(r3));
putar('ben', 'terimaBon', 'tidak'); var r3b = kirim(BEN, nota('Tunai', 1000)), r3c = kirim(BEN, bayarBon());
ok('diputar: Ben terima bon → "tidak": bayar sebagian DI NOTA tetap boleh (bagian jual bon), terima bon sendiri DITOLAK', !r3b.tolak && /^Peran Ben \(penjaga laci\) tidak boleh terima pembayaran bon/.test(r3c.tolak || ''), J([r3b, r3c]));
putar('karyawan', 'pelangganBaru', 'owner'); var r4 = kirim(KRY, orangBaru());
ok('diputar: karyawan pelanggan baru → "minta owner" → kartu baru DITOLAK minta owner', r4.tolak === MINTA, J(r4));
putar('karyawan', 'adukan', 'tidak'); var r5 = kirim(KRY, aduk());
ok('diputar: karyawan adukan → "tidak" → adukan DITOLAK "Peran Karyawan tidak boleh catat adukan …"', /^Peran Karyawan tidak boleh catat adukan/.test(r5.tolak || ''), J(r5));
putar('karyawan', 'isiUlang', 'tidak'); var r6 = kirim(KRY, isiUlang());
ok('diputar: karyawan isi ulang → "tidak" → isi ulang wadah DITOLAK "Peran Karyawan tidak boleh isi ulang & cek wadah literan"', /^Peran Karyawan tidak boleh isi ulang/.test(r6.tolak || ''), J(r6));
setelKisi();

// ---- 4 · tombol nego & potongan di layar Jual memakai kisi (sumber diperiksa: layar butuh DOM)
var JS = SUMBER.jual;
ok('jual.js: ketuk harga (nego) memeriksa jatah & kisi orangnya (owner 7 Okt: NG.ngBolehNego) dan nego diputus dengan akun (SBN()); tombol Potongan tetap memeriksa tombolAkun(…, \'nego\')',
  JS.indexOf("nego: ({ id }) => { const a = opsi.akun ? opsi.akun() : null; const tb = NG.ngBolehNego(a, hakAkun(a, 'nego'), undefined, !!(bolehMintaOwner(a) || {}).boleh); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true });") >= 0
  && JS.indexOf("terapkanNego: () => set(L.terapkanNego(SBN(), S().negoId, L.angkaKetik(S().ketik))),") >= 0
  && JS.indexOf("bukaPotongan: () => { const tb = tombolAkun(opsi.akun ? opsi.akun() : null, 'nego'); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true }); set({ lembar: 'potongan', ketik: '' }); },") >= 0);
var bK = ngBolehNego(KRY, hak(KRY).nego), bB = ngBolehNego(BEN, hak(BEN).nego), bO = ngBolehNego(OWN, 'sendiri');
ok('tombol nego (owner 7 Okt): karyawan (jatah 0 %, kisi "tidak") mati dengan kalimat jatah; Ben (jatah 50 %) & owner terbuka', !bK.boleh && /jatah nego/.test(bK.kalimat) && bB.boleh && bO.boleh, J([bK, bB, bO]));
var tbK = tombolTindakan(KRY, 'nego', hak(KRY).nego, 'Nego di bawah jatah margin'), tbB = tombolTindakan(BEN, 'nego', hak(BEN).nego, 'Nego di bawah jatah margin');
ok('tombol nego: karyawan mati "Peran Karyawan tidak boleh nego di bawah jatah margin", Ben mati minta owner', !tbK.boleh && /tidak boleh nego/.test(tbK.kalimat) && !tbB.boleh && tbB.kalimat === MINTA, J([tbK, tbB]));
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan(js, src_jual):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-09-24T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + js
                + '\nvar SUMBER = ' + json.dumps({'jual': src_jual}) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[:900]]
    h = json.loads(out); return h['lulus'], h['gagal']


if __name__ == '__main__':
    teks = dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL)
    bun = lambda T: '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + p + ' =====\n' + bundel_baru.polos(T[p]) for p in MODUL])
    sj = open(os.path.join(AKAR, 'baru/js/layar/jual.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        A = 'baru/js/data/akses.js'
        rusak = {
            'penjaga tidak menegakkan kisi (kembali ke main)': (A, "  for (const t of tindakanKiriman(D, hak.jatahNego)) { if (hak[t] !== 'sendiri' || (SERVER_BUKA[t] || []).indexOf(P) < 0) return { tolak: tolakTindakan(t) }; }\n", ''),
            'kisi ditegakkan tapi SERVER_BUKA diabaikan': (A, " || (SERVER_BUKA[t] || []).indexOf(P) < 0) return { tolak: tolakTindakan(t) }; }", ") return { tolak: tolakTindakan(t) }; }"),
            'potongan tidak dihitung nego': (A, " || (Number(d.potonganTransaksi) || 0) > 0", ''),
            'nego tidak dihitung': (A, "if (!negoDalamJatah(d, jatahNego) ||", "if (false ||"),
            'nego dalam jatah tidak membandingkan jatah akun (owner 7 Okt)': (A, " && jatah <= (Number(jatahNego) || 0);", ";"),
            'nego dalam jatah tidak membandingkan batas (owner 7 Okt)': (A, "return batas > 0 && harga >= batas && jatah > 0", "return jatah > 0"),
            'disetujui tanpa id persetujuan diterima (owner 7 Okt)': (A, "if (d.negoStatus === 'disetujui') return !!d.negoSetujuId;", "if (d.negoStatus === 'disetujui') return true;"),
            'pelunasan di nota dihitung terima bon': (A, "if (!jual.length && baru.some((x) => x.koleksi === 'piutangMutasi')) t.terimaBon = 1;", "if (baru.some((x) => x.koleksi === 'piutangMutasi')) t.terimaBon = 1;"),
            'isi ulang dihitung adukan': (A, "if (adaWadah) t.isiUlang = 1; else if", "if (false) t.isiUlang = 1; else if"),
            'tombol nego tanpa jatah & kisi': ('jual.js', "const tb = NG.ngBolehNego(a, hakAkun(a, 'nego'), undefined, !!(bolehMintaOwner(a) || {}).boleh); if (!tb.boleh) return set({ kabar: tb.kalimat, kabarAwas: true });", ""),
            'nego diputus tanpa akun (owner 7 Okt)': ('jual.js', "terapkanNego: () => set(L.terapkanNego(SBN(), S().negoId", "terapkanNego: () => set(L.terapkanNego(S(), S().negoId"),
        }
        kode = 0
        for nama, (berkas, a, b2) in rusak.items():
            T = dict(teks); J2 = sj
            if berkas == 'jual.js':
                if a not in J2: print('KONTROL BASI  ' + nama); kode = 3; continue
                J2 = J2.replace(a, b2)
            else:
                if a not in T[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
                T[berkas] = T[berkas].replace(a, b2)
            l, g = jalan(bun(T), J2)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(bun(teks), sj)
    print('KISI SS2 (no. 22): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x[:400])
    sys.exit(2 if g else 0)
