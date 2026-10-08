#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_belanja_tutup_buku.py — SIAP 2027 · P4 (audit 8 Okt 2026): Harga & Pemasok › Belanja tetap utuh sesudah tutup buku. KOTAK PASIR (nama & angka contoh) di jsc.

Sesudah ritual, arsip memindah semua kedatangan ≤ 31 Des. Dulu daftarPemasok hanya membaca kedatangan hidup: Belanja kehilangan SEMUA pemasok & harga beli
terakhir (truk kosong, muatan 0, "Pakai saran" 0 karung) dan pesanan Desember yang sudah datang kembali "menunggu". Kini ringkasan tahun di batch penanda membawa
`pemasok` & `pesananDatang` (bon-pemasok-logika: bpKumpul = fungsi yang sama dengan daftarPemasok; bpPesananDatang = aturan yang sama dengan pesananSemua).

  B1  ritual 5 Jan 2027: hitungBelanja SEBELUM = SESUDAH (arsip habis) — pemasok di truk (cara bayar, terakhir, tempo, saran), harga & tanggal per merek
      (sumber, harga yang dipakai, kalimat harga), muatan truk, saranSemuaTeks, "Pakai saran" & pesan WA per harga, status & tanggal datang tiap pesanan, kartu
      pemasok (kedatangan, belanja, kg, terakhir, kebiasaan bayar); kotak tidak kosong (3 pemasok, merek perlu, saran > 0, pesanan datang lewat ringkasan)
  B2  sesudah kunci (arsip belum mulai) & arsip setengah jalan: bagian PEMASOK = sebelum (kedatangan yang dihitung ringkasan tidak dihitung dua kali). Saran &
      stok tidak dibandingkan di tengah ritual: selama arsip berjalan stok toko memang dobel (saldo pembuka + catatan 2026 yang belum pindah)
  B3  kedatangan 2027 menang per merek (harga & tanggal baru), kedatangan susulan bertanggal 2026 dihitung sekali — sama dengan bila ritual belum terjadi
  B4  ringkasan versi 1 (tanpa `pemasok`/`pesananDatang`) tetap terbaca: tidak jatuh, catatan hidup saja (dan memang kosong — celah yang ditutup P4)
  B5  ringkasan: bentuk yang diterima Firestore; isi = bpKumpul pada 31 Des (kedatangan 2027 tidak ikut); pesananDatang = pesanan 2026 yang datang ≤ 31 Des
  B6  Batalkan tutup buku → catatan hidup lagi, sama dengan sebelum
  B7  tutup buku 2027 (5 Jan 2028): pemasok yang hanya mengirim di 2026 tetap ada (ringkasan 2026 dibawa ringkasan 2027), Belanja sebelum = sesudah lagi

Sanggahan P4 (audit 8 Okt):
  · id kedatangan & pesanan = angka pecahan dari jam tulis (seperti cadangan toko) — dulu 'b01'… (Number = NaN) sehingga urutan tulis tidak teruji. SEJATI
    berganti ejaan di 2026: arsip setengah jalan dengan ejaan lama yang masih hidup tetap menampilkan ejaan terbaru (B2, ringkasan `urut`); susulan RODA
    11 Des membuat tanggal datang ps1 = yang pertama, bukan yang di ringkasan (B3). Kunci peta pesananDatang berTITIK (B5).
  B8  kedatangan Januari dicatat SEBELUM kunci (ritual tertunda, kunci 5 Jan): HANYA "Stok beras" beda (rupiah — rata-rata harga beli mesin; kg & merek sama),
      kelompok 3 sama, "selesai" diterima pada ketukan kedua; dicatat SESUDAH pita "arsipnya habis" (3 Jan, atau hari ritual sesudah jam kunci) → semua sama.
      Prosedur pulih darurat menyebutnya — STATIS (PROSEDUR_B8): bukan alasan membatalkan, catat sesudah arsip habis
  B9  langkah Kunci LATIHAN menyusun & memeriksa ringkasan tahun (ringkasLatihan): kalimatnya; penyusun jatuh / isian ditolak server / terlalu besar ketahuan;
      kunci sungguhan memeriksa isian yang sama (DITOLAK berkalimat, tanpa kiriman); susunKunci yang jatuh berkalimat di layar Uang — STATIS (UANG_B9)

    python3 alat-uji/uji_belanja_tutup_buku.py               → N lulus · 0 gagal
    python3 alat-uji/uji_belanja_tutup_buku.py --kontrol     → logika / kalimat prosedur / layar yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_belanja_tutup_buku.py --cadangan=/jalur/backup-batch-….json   (atau env UJI_CADANGAN=…) → asap atas cadangan LOKAL + nota & pesanan
        TIRUAN (laju 14 hari di akhir Desember): ritual 5 Jan 2027, Belanja sebelum = sesudah kunci / setengah arsip / arsip habis. Dilewati di CI (cadangan toko
        tidak pernah ada di repo); keluarannya hanya hitungan (pemasok, merek, pesanan, ukuran ringkasan), tanpa rupiah. Pembanding tanpa ringkasan pemasok
        (bentuk sebelum P4) WAJIB berbeda — kalau sama, asapnya tidak menguji penggabungan. Juga langkah Kunci LATIHAN (potret & ringkasan) atas data toko.
"""
import os, sys, json, subprocess, tempfile, datetime
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
JSC = uji_kunci_periode.JSC
_M = uji_kunci_periode.MODUL + ['baru/js/layar/sistem-logika.js', 'baru/js/layar/belanja-logika.js', 'baru/js/layar/periksa-sesudah-logika.js']
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]
JAM = "var __KINI = new Date('2027-01-05T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


# Sanggahan P4 (temuan 3): id dokumen seperti di toko — angka pecahan dari JAM TULIS (cadangan toko: id batch & pesanan = float). Dulu id contoh 'b01'… →
# Number(id) = NaN = 0: urutan tulis (ejaan nama pemasok terbaru, urutan sesama tanggal) tidak pernah teruji. Kunci peta pesananDatang jadi berTITIK, seperti di toko.
ID = {}


def idw(nama, tgl, jam, pecah=0.25):
    ID[nama] = int(datetime.datetime.fromisoformat(tgl + 'T' + jam + ':00+07:00').timestamp() * 1000) + pecah
    return ID[nama]


def batch(nama, tgl, pemasok, cara, baris, jam='08:00', tulis=None):
    """tulis = (tanggal, jam) saat dicatat bila beda dengan tanggal kedatangan (catatan susulan)."""
    ml = []
    for i, x in enumerate(baris):
        m, kg, h = x[0], x[1], x[2]
        r = {'id': nama + '-' + str(i), 'merk': m, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg // 50, 'totalKg': kg, 'hargaPerKg': h, 'subtotalHarga': kg * h}
        if len(x) > 3: r['merkPemasok'] = x[3]
        ml.append(r)
    return {'id': idw(nama, *(tulis or (tgl, jam))), 'tanggal': tgl, 'jam': jam, 'pemasok': pemasok, 'caraBayar': cara, 'biayaBongkar': 0, 'merkList': ml}


def jual(id, tgl, merk, kg):
    return {'id': id, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50,
            'jumlahKarung': kg / 50, 'hargaTotal': kg * 13500, 'hppTotalSaatJual': kg * 12000, 'trxId': 't-' + id}


def susun_kotak():
    """ANGKA & NAMA CONTOH. Tiga pemasok: RODA CONTOH (biasanya bon), SEJATI CONTOH (tunai), LAMA CONTOH (hanya mengirim Agustus 2026). 14 kedatangan 2026 +
    1 kedatangan 3 Jan 2027 (Angsa harga baru). Penjualan: satu nota besar 21 Des per merek + laju 14 hari (22 Des – 4 Jan) → Angsa, Kelas Contoh, Rusa habis
    ≤ 7 hari; Bebek & Pandan aman. Pesanan: ps1 RODA 10 Des (datang 12 Des — hanya ringkasan yang tahu sesudah arsip), ps2 LAMA 28 Des (menunggu → Pandan
    sudah dipesan), ps3 RODA 30 Des (datang 3 Jan, catatan hidup), ps4 batal, ps5 'datang' tersimpan.
    Sanggahan P4: SEJATI berganti ejaan di 2026 (Agustus–September "Sejati Contoh", sesudahnya "SEJATI CONTOH") — nama yang tampil = ejaan kedatangan yang
    TERAKHIR DITULIS (urut = id), juga saat kedatangan berejaan baru sudah diarsip dan yang berejaan lama masih hidup (arsip setengah jalan)."""
    R, S, L, S0 = 'RODA CONTOH', 'SEJATI CONTOH', 'LAMA CONTOH', 'Sejati Contoh'
    b = [batch('b00', '2026-08-01', 'STOK AWAL', 'tunai', [('Angsa', 200, 11500)]),
         batch('b01', '2026-08-10', R, 'utang', [('Angsa', 1000, 12000), ('Bebek', 500, 12500)]),
         batch('b02', '2026-08-15', S0, 'tunai', [('Rusa', 600, 11000)]),
         batch('b03', '2026-08-25', L, 'tunai', [('Pandan', 300, 15000)]),
         batch('b04', '2026-09-05', R, 'utang', [('Angsa', 1500, 12100), ('Kelas Contoh', 500, 10000, 'Merek Pemasok Contoh')]),
         batch('b05', '2026-09-20', S0, 'tunai', [('Rusa', 800, 11100)]),
         batch('b06', '2026-10-02', R, 'tunai', [('Bebek', 1000, 12600)]),
         batch('b07', '2026-10-15', R, 'utang', [('Angsa', 2000, 12200)]),
         batch('b08', '2026-10-28', S, 'tunai', [('Rusa', 1000, 11200)]),
         batch('b09', '2026-11-05', R, 'utang', [('Kelas Contoh', 700, 10100, 'Merek Pemasok Lain'), ('Bebek', 300, 12700)]),
         batch('b10', '2026-11-18', S, 'tunai', [('Rusa', 500, 11150)]),
         batch('b11', '2026-11-30', R, 'utang', [('Angsa', 1500, 12300)]),
         batch('b12', '2026-12-05', S, 'tunai', [('Rusa', 400, 11300)]),
         batch('b13', '2026-12-12', R, 'utang', [('Angsa', 1000, 12400), ('Bebek', 500, 12750)]),
         batch('b14', '2026-12-20', S, 'tunai', [('Rusa', 300, 11400)]),
         batch('b15', '2027-01-03', R, 'utang', [('Angsa', 300, 12800)], jam='09:00')]
    b[0]['stokAwal'] = True
    pj = []
    # nota besar 21 Des (sesudah semua kedatangan 2026) = pemakaian Agustus–Desember; laju 14 hari: 22 Des – 4 Jan
    besar = {'Angsa': 6060, 'Bebek': 1280, 'Kelas Contoh': 490, 'Rusa': 2650, 'Pandan': 60}
    laju = {'Angsa': 80, 'Bebek': 30, 'Kelas Contoh': 40, 'Rusa': 50, 'Pandan': 10}
    for m, kg in besar.items(): pj.append(jual('besar-' + m, '2026-12-21', m, kg))
    d = datetime.date(2026, 12, 22)
    while d <= datetime.date(2027, 1, 4):
        for m, kg in laju.items(): pj.append(jual('l-%s-%s' % (m, d.isoformat()), d.isoformat(), m, kg))
        d += datetime.timedelta(days=1)
    ps = [{'id': idw('ps1', '2026-12-10', '10:00', 0.5), 'tanggal': '2026-12-10', 'jam': '10:00', 'pemasok': R, 'baris': [{'merk': 'Angsa', 'karung': 20, 'berat': 50, 'kg': 1000, 'hargaPerKg': 12300}], 'karung': 20, 'kg': 1000, 'status': 'menunggu'},
          {'id': idw('ps2', '2026-12-28', '09:00', 0.5), 'tanggal': '2026-12-28', 'jam': '09:00', 'pemasok': L, 'baris': [{'merk': 'Pandan', 'karung': 4, 'berat': 50, 'kg': 200, 'hargaPerKg': 15000}], 'karung': 4, 'kg': 200, 'status': 'menunggu'},
          {'id': idw('ps3', '2026-12-30', '11:00', 0.5), 'tanggal': '2026-12-30', 'jam': '11:00', 'pemasok': R, 'baris': [{'merk': 'Bebek', 'karung': 6, 'berat': 50, 'kg': 300, 'hargaPerKg': 12750}], 'karung': 6, 'kg': 300, 'status': 'menunggu'},
          {'id': idw('ps4', '2026-12-15', '10:00', 0.5), 'tanggal': '2026-12-15', 'jam': '10:00', 'pemasok': S, 'baris': [{'merk': 'Rusa', 'karung': 10, 'berat': 50, 'kg': 500, 'hargaPerKg': 11300}], 'karung': 10, 'kg': 500, 'status': 'batal'},
          {'id': idw('ps5', '2026-11-01', '10:00', 0.5), 'tanggal': '2026-11-01', 'jam': '10:00', 'pemasok': S, 'baris': [{'merk': 'Rusa', 'karung': 10, 'berat': 50, 'kg': 500, 'hargaPerKg': 11150}], 'karung': 10, 'kg': 500, 'status': 'datang', 'datangTanggal': '2026-11-18'}]
    return {'batchMasuk': b, 'penjualan': pj, 'pesananPemasok': ps,
            'pemasokCatatan': [{'id': 'roda contoh', 'nama': R, 'kontak': '0812 0000 0000', 'catatan': 'contoh', 'tempo': 21}],
            'modalOwner': [{'id': 'mo1', 'tanggal': '2026-08-01', 'jam': '08:00', 'tipe': 'setor', 'nominal': 200000000, 'catatan': 'modal contoh'}],
            'aturanToko': [], 'tutupBukuAcara': [], 'pengaturan': []}


KOTAK = susun_kotak()
# kedatangan yang ditulis skenario (B3, B7, B8) — id = jam tulisnya (sesudah ritual 5 Jan 10.00)
idw('b16', '2027-01-05', '10:30'); idw('b17', '2027-01-05', '10:35'); idw('b18', '2027-01-05', '10:40'); idw('b19', '2027-01-05', '10:50'); idw('c01', '2027-06-01', '08:00')

BERSAMA = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function PSN(n) { return 'pesanan|' + ID[n]; }
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(typeof ket === 'string' ? ket : J(ket)).slice(0, 600) : '')); }
function coba(nama, f) { try { f(); } catch (e) { gagal.push(nama + ' → JATUH: ' + (e && e.message ? e.message : e) + ' ' + String(e && e.stack || '').split('\n').slice(0, 2).join(' / ')); } }
var nId = 80000; function jam(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: iso.slice(11, 16), kini: new Date(iso).toISOString(), idUnik: function () { nId += 1; return 'u' + nId; } }; }
var LA = { idPerangkat: 'mac-contoh', namaPerangkat: 'Mac contoh', antre: [], menunggu: 0, offline: false };
var D = { paraf: { owner: true, saksi: true }, saksi: 'Saksi Contoh', langkah: {} };
function kirim(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) throw new Error('penjaga pusat menolak: ' + j.pesan);
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); }
function tulis(r) { if (!r || r.tolak) throw new Error('DITOLAK: ' + (r && r.tolak)); kirim({ dokumen: r.dokumen || [], hapus: r.hapus || [] }); return r; }
function acara(tahun) { return ambilTutupBukuAcara().filter(function (a) { return Number(a.tahun) === tahun; })[0] || null; }
/** Hari berjualan tanpa tutup hari diputus "diterima apa adanya" (A1) — tanpa putusan susunKunci menolak di pintu masuk (g1). */
function putus(tahun, w) { var G = gerbangBuku(tahun, new Date(__KINI), LA, { g3: true }); if (!G.belumPutus.length) return 0; var isi = {}; G.belumPutus.forEach(function (t) { isi[t] = 'contoh: hari tanpa tutup hari, diterima apa adanya'; }); tulis(susunPutusanHari(isi, w)); return G.belumPutus.length; }
/** Kunci tahun: putusan, susunKunci, semua kiriman (arsip BELUM). */
function kunci(tahun, w) { putus(tahun, w); var R = susunKunci(tahun, D, w, LA); if (R.tolak) throw new Error('kunci ' + tahun + ' ditolak: ' + R.tolak); R.kiriman.forEach(kirim); return R; }
function arsipSemua(tahun, w) { arsipkanDokumen(tahun, arsipBuku(tahun).daftar); var PA = susunPeriksaArsip(tahun, w, LA, true); if (PA.dokumen) kirim({ dokumen: PA.dokumen }); }
function penanda() { return ambilSemuaBatch().filter(function (x) { return x.tutupBuku && x.penandaBuku && x.ringkasTahun; }).sort(function (a, b) { return Number(b.tahunDari) - Number(a.tahunDari); })[0] || null; }
/** Firestore menerima: tanpa undefined / fungsi / NaN / Infinity, tanpa larik langsung di dalam larik, kunci peta tidak kosong & bukan __x__. → daftar pelanggaran. */
function bentukFirestore(o, jalur, out) { out = out || []; jalur = jalur || '';
  if (o === undefined) out.push(jalur + ' undefined'); else if (typeof o === 'function') out.push(jalur + ' fungsi'); else if (typeof o === 'number' && !isFinite(o)) out.push(jalur + ' ' + o);
  else if (Array.isArray(o)) o.forEach(function (x, i) { if (Array.isArray(x)) out.push(jalur + '[' + i + '] larik di dalam larik'); bentukFirestore(x, jalur + '[' + i + ']', out); });
  else if (o && typeof o === 'object') Object.keys(o).forEach(function (k) { if (!k || /^__.*__$/.test(k)) out.push(jalur + ' kunci "' + k + '"'); bentukFirestore(o[k], jalur + '.' + k, out); });
  return out; }
/**
 * Yang owner lihat di Harga & Pemasok › Belanja (+ kartu pemasok) — dipanggil SEBELUM dan SESUDAH dengan fungsi yang sama. Satu kunci = satu hal yang dibandingkan.
 * Kunci berawalan "stok|" bergantung pada stok: selama arsip berjalan stok toko memang DOBEL (saldo pembuka + catatan 2026 yang belum pindah — kemajuan arsip
 * menyebutnya), jadi di tengah ritual yang dibandingkan hanya bagian pemasok (bedaPemasok).
 */
function potretBelanja(kini) {
  var H = hitungBelanja({}, kini); var o = {};
  o.truk = H.perP.map(function (r) { return [r.pemasok, r.cara, r.caraTeks, r.terakhir, r.tempo.teks].join('|'); }).join(' ; ');
  o['stok|truk'] = H.perP.map(function (r) { return [r.pemasok, r.saran.map(function (b) { return b.merk + ':' + b.saranK; }).join('+'), r.saranKarung, r.saranG].join('|'); }).join(' ; ');
  o.pemasokTruk = H.D.pemasok.map(function (p) { return p.nama; }).join(',');
  o.muatan = [H.atur.muatanKg, H.atur.muatanTerukur, muatanTerukur()].join('|');
  o['stok|saranSemua'] = H.saranSemuaTeks; o.tanpaPemasok = H.D.tanpaPemasok.join(','); o['stok|ringkas'] = J(H.ringkas);
  var sumber = {}; H.D.merk.forEach(function (x) { sumber[x.merk] = x.sumber.map(function (s) { return s.pemasok + ' ' + s.harga + ' ' + s.tanggal + ' ' + s.kode; }).join(' / '); });
  H.baris.forEach(function (b) { o['merek|' + b.merk] = [sumber[b.merk], b.pakai ? [b.pakai.pemasok, b.pakai.harga, b.pakai.tanggal, b.pakai.lalu ? b.pakai.lalu.harga + '@' + b.pakai.lalu.tanggal : ''].join(' ') : '-', b.hargaTeks, b.dipesanTeks].join(' | ');
    o['stok|' + b.merk] = [b.sisa, Math.round(b.laju * 1000) / 1000, b.hari, b.saranK, b.perlu].join(' | '); });
  pesananSemua().forEach(function (p) { o['pesanan|' + p.id] = p.status + '|' + p.datangTanggal; });
  var P = pakaiSaran(H, {}, ''); var H2 = hitungBelanja(P.pesan, kini); o['stok|pakaiSaran'] = [P.baris, P.merk, P.karung].join('|');
  H2.perP.forEach(function (r) { o['stok|wa|' + r.pemasok] = r.g.map(function (g) { return g.teks; }).join(' ; ') + ' || ' + r.uangTeks; });
  daftarPemasok().forEach(function (p) { o['kartu|' + p.kunci] = [p.nama, p.kedatangan, p.belanja, p.totalKg, p.terakhir, p.caraTeks, p.kontak, p.tempo].join('|'); });
  return o; }
function bedaPemasok(a, b) { return beda(a, b).filter(function (x) { return x.indexOf('stok|') !== 0; }); }
function beda(a, b) { var out = []; Object.keys(a).concat(Object.keys(b).filter(function (k) { return !(k in a); })).forEach(function (k) { if (a[k] !== b[k]) out.push(k + ': ' + a[k] + '  →  ' + b[k]); }); return out; }
"""

SKENARIO = r"""
function muat() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' };
  localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-12-31', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 0 })); }
var W, A, B, R;

// ---- B1 · ritual 5 Jan 2027: Belanja sebelum = sesudah (arsip habis)
coba('B1', function () { muat(); W = jam('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI); A = potretBelanja(kini);
  ok('B1 kotak tidak kosong SEBELUM ritual: 3 pemasok di truk, muatan terukur > 0, saran > 0 karung, Angsa harga 3 Jan 2027, Pandan sudah dipesan, ps1 datang 12 Des',
    A.pemasokTruk === 'RODA CONTOH,SEJATI CONTOH,LAMA CONTOH' && Number(A.muatan.split('|')[0]) > 0 && /karung$/.test(A['stok|saranSemua']) && !/ 0 karung$/.test(A['stok|saranSemua'])
    && /RODA CONTOH 12800 2027-01-03/.test(A['merek|Angsa']) && /sudah dipesan/.test(A['merek|Pandan']) && A[PSN('ps1')] === 'datang|2026-12-12' && A[PSN('ps2')] === 'menunggu|' && A[PSN('ps3')] === 'datang|2027-01-03', J(A));
  R = kunci(2026, W); var Bk = potretBelanja(kini);
  ok('B2 sesudah KUNCI (ringkasan terlihat, arsip belum mulai): bagian pemasok = sebelum — kedatangan 2026 yang masih hidup tidak dihitung dua kali', bedaPemasok(A, Bk).length === 0, bedaPemasok(A, Bk));
  // setengah: kedatangan berselang-seling (yang terbaru ikut pindah) + separuh catatan lain
  var daftar = arsipBuku(2026).daftar; var bm = daftar.filter(function (x) { return x.koleksi === 'batchMasuk'; }), lain = daftar.filter(function (x) { return x.koleksi !== 'batchMasuk'; });
  arsipkanDokumen(2026, bm.filter(function (x, i) { return i % 2 === 0; }).concat(lain.slice(0, Math.ceil(lain.length / 2))));
  var nHidup = ambilSemuaBatch().filter(function (b) { return !b.stokAwal && (b.tanggal || '') <= '2026-12-31'; }).length; var Bs = potretBelanja(kini);
  // sanggahan P4 (temuan 3): SEJATI yang masih hidup hanya berejaan LAMA ("Sejati Contoh", Agustus–September), yang berejaan baru sudah pindah ke arsip —
  // nama yang tampil tetap ejaan yang terakhir ditulis (ringkasan: urut = id kedatangan terakhir) = sebelum ritual
  var sej = ambilSemuaBatch().filter(function (b) { return !b.stokAwal && kunciPelanggan(b.pemasok) === 'sejati contoh' && (b.tanggal || '') <= '2026-12-31'; }).map(function (b) { return b.pemasok; });
  ok('B2 arsip SETENGAH jalan (' + nHidup + ' dari 14 kedatangan 2026 masih hidup; SEJATI hidup hanya berejaan lama): bagian pemasok = sebelum, nama "SEJATI CONTOH"',
    nHidup > 0 && nHidup < 14 && sej.length > 0 && sej.every(function (n) { return n === 'Sejati Contoh'; }) && bedaPemasok(A, Bs).length === 0 && Bs['kartu|sejati contoh'].split('|')[0] === 'SEJATI CONTOH',
    J([nHidup, sej, bedaPemasok(A, Bs), Bs['kartu|sejati contoh']]));
  arsipSemua(2026, W); B = potretBelanja(kini); var hidup = ambilSemuaBatch().filter(function (b) { return !b.stokAwal; }).map(function (b) { return b.id; });
  ok('B1 arsip HABIS (kedatangan hidup tinggal 3 Jan 2027): Belanja sesudah = sebelum — truk, harga & tanggal per merek, muatan, saran, Pakai saran & WA, pesanan, kartu pemasok', hidup.join() === String(ID.b15) && beda(A, B).length === 0, J([hidup, beda(A, B)])); });

// ---- B4 · ringkasan versi 1 (tanpa pemasok / pesananDatang): tetap terbaca = catatan hidup saja (celah lama: truk & harga 2026 hilang)
coba('B4', function () { var T = penanda(); var RT = T.ringkasTahun; var kini = new Date(__KINI);
  terapkanKeCache([{ koleksi: 'batchMasuk', data: Object.assign({}, T, { ringkasTahun: Object.assign({}, RT, { versi: 1, pemasok: undefined, pesananDatang: undefined }) }) }]);
  var V1 = null, err = ''; try { V1 = potretBelanja(kini); } catch (e) { err = String(e && e.message || e); }
  ok('B4 ringkasan versi 1: Belanja tidak jatuh; hanya catatan hidup — truk tinggal RODA (kedatangan 3 Jan), muatan 300 kg, SEJATI & LAMA hilang, ps1 datang 3 Jan (bukan 12 Des)',
    !err && !!V1 && V1.pemasokTruk === 'RODA CONTOH' && V1.muatan.split('|')[0] === '300' && V1[PSN('ps1')] === 'datang|2027-01-03' && beda(A, V1).length > 5, err || J(V1 && beda(A, V1).slice(0, 6)));
  terapkanKeCache([{ koleksi: 'batchMasuk', data: T }]);
  ok('B4 penanda dikembalikan → sama lagi', beda(A, potretBelanja(kini)).length === 0, beda(A, potretBelanja(kini))); });

// ---- B5 · isi & bentuk ringkasan
coba('B5', function () { var RT = penanda().ringkasTahun; var P = RT.pemasok || {}; var r = P['roda contoh'] || {};
  ok('B5 ringkasan tahun versi 2 berbentuk Firestore (tanpa undefined / larik di dalam larik / kunci kosong)', RT.versi === 2 && bentukFirestore(RT, 'ringkasTahun').length === 0, bentukFirestore(RT, 'ringkasTahun').slice(0, 5));
  ok('B5 pemasok = 3 pemasok sungguhan (STOK AWAL / TUTUP BUKU bukan pemasok); RODA: 7 kedatangan ≤ 31 Des (kedatangan 3 Jan TIDAK ikut), ids 7, 7 kedatangan terakhir, Angsa terakhir 12 Des 12.400, Kelas Contoh membawa merek pemasoknya',
    Object.keys(P).sort().join() === 'lama contoh,roda contoh,sejati contoh' && r.nama === 'RODA CONTOH' && r.kedatangan === 7 && r.ids.length === 7 && r.akhir.length === 7 && r.terakhir === '2026-12-12'
    && r.hargaPerMerk.Angsa.tanggal === '2026-12-12' && r.hargaPerMerk.Angsa.hargaPerKg === 12400 && r.hargaPerMerk['Kelas Contoh'].merkPemasok === 'Merek Pemasok Lain' && r.akhir[0].id === ID.b13 && r.akhir[0].utang === true
    && r.urut === ID.b13 && (P['sejati contoh'] || {}).nama === 'SEJATI CONTOH' && (P['sejati contoh'] || {}).urut === ID.b14, J([r, P['sejati contoh']]));
  var harap = {}; harap[String(ID.ps1)] = '2026-12-12';
  ok('B5 pesananDatang = { id ps1 (angka berTITIK, seperti di toko): 12 Des } (ps3 datang sesudah 31 Des → catatan hidup; ps4 batal & ps5 tersimpan tidak dibawa)', J(RT.pesananDatang) === J(harap) && String(ID.ps1).indexOf('.') > 0, J(RT.pesananDatang)); });

// ---- B3 · kedatangan 2027 menang per merek; susulan bertanggal 2026 dihitung sekali (= seandainya ritual belum terjadi). Susulan RODA 11 Des (ditulis
//      sesudah ritual, antara pesanan ps1 10 Des dan kedatangan 12 Des di ringkasan): tanggal datang ps1 = yang PERTAMA (11 Des), bukan yang di ringkasan
coba('B3', function () { var kini = new Date(__KINI);
  var baru = [{ koleksi: 'batchMasuk', data: { id: ID.b16, tanggal: '2027-01-05', jam: '10:30', pemasok: 'SEJATI CONTOH', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ merk: 'Rusa', satuan: 'karung', beratKarung: 50, jumlahKarung: 20, totalKg: 1000, hargaPerKg: 11600, subtotalHarga: 11600000 }, { merk: 'Pandan', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 15500, subtotalHarga: 1550000 }] } },
    { koleksi: 'batchMasuk', data: { id: ID.b17, tanggal: '2026-12-29', jam: '15:00', pemasok: 'SEJATI CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: 'Rusa', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 11500, subtotalHarga: 1150000 }] } },
    { koleksi: 'batchMasuk', data: { id: ID.b18, tanggal: '2026-12-11', jam: '14:00', pemasok: 'RODA CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: 'Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 12650, subtotalHarga: 1265000 }] } }];
  terapkanKeCache(baru); var B3 = potretBelanja(kini);
  muat(); terapkanKeCache(baru); var A3 = potretBelanja(kini);
  ok('B3 kedatangan 5 Jan 2027 (Rusa 11.600, Pandan dari pemasok lain) + susulan 29 Des & 11 Des: sesudah ritual = seandainya ritual belum terjadi; Rusa memakai harga 5 Jan, kartu SEJATI & RODA menghitung susulan sekali, ps1 datang 11 Des',
    beda(A3, B3).length === 0 && /SEJATI CONTOH 11600 2027-01-05/.test(B3['merek|Rusa']) && B3['kartu|sejati contoh'].split('|')[1] === '8' && B3['kartu|roda contoh'].split('|')[1] === '9'
    && B3[PSN('ps1')] === 'datang|2026-12-11', J([beda(A3, B3), B3['merek|Rusa'], B3['kartu|sejati contoh'], B3['kartu|roda contoh'], B3[PSN('ps1')]])); });

// ---- B6 · Batalkan tutup buku → catatan hidup lagi
coba('B6', function () { muat(); W = jam('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI); var A6 = potretBelanja(kini); kunci(2026, W); arsipSemua(2026, W);
  var BT = susunBatal(2026, arsipSimulasi().filter(function (a) { return a.tahun === 2026; }).map(function (a) { return { koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }; }), W, LA);
  if (BT.tolak) throw new Error('batal ditolak: ' + BT.tolak); BT.kiriman.forEach(kirim); pulihkanArsip(2026, BT.pulih); kirim({ dokumen: [BT.akhir] });
  ok('B6 sesudah BATAL: penanda hilang, era kosong, Belanja = sebelum', !penanda() && eraBuku() === null && beda(A6, potretBelanja(kini)).length === 0, J([eraBuku(), beda(A6, potretBelanja(kini))])); });

// ---- B7 · tahun berikutnya: ringkasan 2026 dibawa ringkasan 2027
// (selesai = ketukan kedua: periksa ulang "Stok beras" berbeda karena kedatangan 3 Jan SEBELUM ritual — rata-rata HPP mesin dihitung dari seluruh riwayat beli,
// sesudah ritual dari saldo pembuka; sudah begitu di main sebelum P4, bukan bagian Belanja. Dijaga B8 + prosedur pulih darurat)
coba('B7', function () { muat(); W = jam('2027-01-05T10:00:00+07:00'); kunci(2026, W); arsipSemua(2026, W); var SL = susunSelesai(2026, 'contoh-sesudah.json', W, true, LA); tulis(SL);
  var t27 = [{ koleksi: 'batchMasuk', data: { id: ID.c01, tanggal: '2027-06-01', jam: '08:00', pemasok: 'RODA CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: 'Angsa', satuan: 'karung', beratKarung: 50, jumlahKarung: 40, totalKg: 2000, hargaPerKg: 12900, subtotalHarga: 25800000 }] } }];
  for (var d = new Date('2027-12-22T00:00:00Z'); d.toISOString().slice(0, 10) <= '2028-01-04'; d.setUTCDate(d.getUTCDate() + 1)) { var t = d.toISOString().slice(0, 10);
    t27.push({ koleksi: 'penjualan', data: { id: 'm-' + t, tanggal: t, jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 100, beratKarungAcuan: 50, jumlahKarung: 2, hargaTotal: 1350000, hppTotalSaatJual: 1290000, trxId: 't-m-' + t } }); }
  terapkanKeCache(t27); var W2 = jam('2028-01-05T10:00:00+07:00'); var kini = new Date(__KINI); var A7 = potretBelanja(kini);
  kunci(2027, W2); arsipSemua(2027, W2); var B7 = potretBelanja(kini); var P27 = (penanda().ringkasTahun || {}).pemasok || {};
  ok('B7 tutup buku 2027: Belanja sebelum = sesudah; LAMA CONTOH (hanya mengirim Agustus 2026) tetap di truk dengan harga Pandan 25 Agu 2026 — ringkasan 2027 membawa ringkasan 2026',
    beda(A7, B7).length === 0 && /LAMA CONTOH/.test(B7.pemasokTruk) && /LAMA CONTOH 15000 2026-08-25/.test(B7['merek|Pandan']) && !!P27['lama contoh'] && P27['lama contoh'].kedatangan === 1 && P27['roda contoh'].kedatangan === 9,
    J([beda(A7, B7), B7.pemasokTruk, B7['merek|Pandan'], P27['lama contoh'], P27['roda contoh'] && P27['roda contoh'].kedatangan])); });

// ---- B8 · sanggahan P4 (temuan sedang, di luar Belanja): kedatangan Januari dicatat SEBELUM kunci (ritual tertunda, kunci 5 Jan) → kartu & pita: HANYA
//      "Stok beras" beda (rupiahnya: rata-rata harga beli mesin dihitung dari dasar lain; kg & jumlah merek sama), semua baris lain sama — termasuk kelompok 3;
//      "selesai" diterima pada ketukan kedua. Dicatat SESUDAH pita "arsipnya habis" (bertanggal 3 Jan, atau hari ritual sesudah jam kunci) → semua sama.
//      Prosedur pulih darurat menyebutnya (bukan alasan membatalkan; catat sesudah arsip habis) — dijaga statis di Python (PROSEDUR_B8).
coba('B8', function () {
  var B15 = KOTAK.batchMasuk.filter(function (b) { return b.id === ID.b15; })[0];
  function ritual(cara) { muat(); if (cara !== 'sebelum') pasok('batchMasuk', KOTAK.batchMasuk.filter(function (b) { return b.id !== ID.b15; }));
    var w = jam('2027-01-05T10:00:00+07:00'); kunci(2026, w); arsipSemua(2026, w);
    if (cara === 'sesudah') terapkanKeCache([{ koleksi: 'batchMasuk', data: B15 }]);
    if (cara === 'hariRitual') terapkanKeCache([{ koleksi: 'batchMasuk', data: Object.assign({}, B15, { id: ID.b19, tanggal: '2027-01-05', jam: '10:50' }) }]);
    var w2 = jam('2027-01-05T11:00:00+07:00'); var PS = pstPeriksa(new Date(__KINI)); var semua = [].concat.apply([], PS.kelompok.map(function (g) { return g.baris; }));
    var K = kemajuanBuku(); var SL = susunSelesai(2026, 'contoh-sesudah.json', w2, false, LA);
    return { PS: PS, beda: semua.filter(function (x) { return x.status === 'beda'; }).map(function (x) { return x.id; }), rak: PS.kelompok.filter(function (g) { return g.id === 'rak'; })[0].baris.map(function (x) { return x.status; }),
      pita: K ? K.teks : '', SL: SL, w2: w2 }; }
  var X = ritual('sebelum'); var H = acara(2026).hariIni; var nmA = H.baris.filter(function (b) { return b.id === 'beras'; })[0];
  var nmB = barisBuku(H.tanggal, H.tanggal).harta.filter(function (b) { return b.id === 'beras'; })[0];
  ok('B8 kedatangan 3 Jan dicatat SEBELUM kunci: kartu "1 pemeriksaan beda — jangan jualan/menagih dulu" dan yang beda HANYA Stok beras (kelompok 3 sama); pita & ketukan "selesai" pertama menyebut "1 baris TIDAK SAMA (Stok beras)"',
    X.PS.nBeda === 1 && X.PS.nBelum === 0 && X.beda.join() === 'beras' && /^1 pemeriksaan beda — jangan jualan\/menagih dulu/.test(X.PS.ringkas) && X.rak.every(function (st) { return st === 'sama'; })
    && X.SL.perluYakin === true && /Pemeriksaan ulang dari mesin: 1 baris TIDAK SAMA \(Stok beras\)\./.test(X.SL.tolak) && /1 baris TIDAK SAMA \(Stok beras\)/.test(X.pita),
    J([X.PS.ringkas, X.beda, X.rak, X.SL.tolak, X.pita]));
  ok('B8 … sebabnya NILAI (rata-rata harga beli), bukan barang: nama baris (kg & jumlah merek) sesudah ritual = patokan, hanya rupiahnya beda',
    !!nmA && !!nmB && nmA.nama === nmB.nama && Math.abs(nmA.n - nmB.n) >= 1, J([nmA, nmB && { nama: nmB.nama, n: nmB.n }]));
  var Y = susunSelesai(2026, 'contoh-sesudah.json', X.w2, true, LA);
  ok('B8 … ketukan "selesai" kedua menerimanya — beda dicatat di berita acara (tidak perlu membatalkan & mengulang)', !Y.tolak && !!Y.dokumen && Y.dokumen[0].data.status === 'selesai'
    && J(Y.dokumen[0].data.periksaUlang.beda) === J([nmA.nama]), J([Y.tolak, Y.dokumen && Y.dokumen[0].data.periksaUlang]));
  [['tanpa', 'tanpa kedatangan Januari'], ['sesudah', 'kedatangan 3 Jan dicatat SESUDAH pita "arsipnya habis"'], ['hariRitual', 'kedatangan hari ritual (5 Jan 10.50, sesudah jam kunci) dicatat SESUDAH pita "arsipnya habis"']].forEach(function (c) {
    var Z = ritual(c[0]); ok('B8 ' + c[1] + ': kartu "Semua … pemeriksaan sama", "selesai" tanpa ketukan kedua', Z.PS.beres && /^Semua \d+ pemeriksaan sama — tutup buku 2026 beres$/.test(Z.PS.ringkas) && !Z.SL.tolak,
      J([Z.PS.ringkas, Z.beda, Z.SL.tolak])); }); });

// ---- B9 · sanggahan P4 (temuan 4): langkah Kunci LATIHAN menyusun & memeriksa ringkasan tahun (tanpa menulis) — penyusun jatuh / isian ditolak server / terlalu
//      besar ketahuan di Desember; kunci sungguhan memeriksa isian yang sama (ditolak berkalimat, tidak ada yang ditulis); susunKunci yang jatuh berkalimat (uang.js)
coba('B9', function () { muat(); var w = jam('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI); putus(2026, w);
  var n0 = ambilTutupBukuAcara().length; var PL = potretLatihan(2026, kini); var RL = ringkasLatihan(2026, PL.ukuran);
  ok('B9 latihan: "Ringkasan 2026: N pelanggan · 3 pemasok · 1 pesanan sudah datang · … KB." — fungsi yang sama dengan kunci sungguhan, tidak menulis apa pun',
    PL.ok && RL.ok && /^Ringkasan 2026: \d+ pelanggan · 3 pemasok · 1 pesanan sudah datang · \d+ KB\.$/.test(RL.teks) && RL.ukuran === J(ringkasTahun(2026)).length && ambilTutupBukuAcara().length === n0, J([PL.ok, RL]));
  var asliP = ringkasPemasokTahun, asliS = ringkasPesananTahun, jatuh = '', RJ = null, RB = null, RK = null;
  try { ringkasPemasokTahun = function () { throw new Error('contoh rusak'); }; RJ = ringkasLatihan(2026, PL.ukuran);
    try { susunKunci(2026, D, w, LA); } catch (e) { jatuh = bkKalimatKunciJatuh(2026, e); } } finally { ringkasPemasokTahun = asliP; }
  ok('B9 penyusun ringkasan JATUH: latihan "GAGAL disusun … kunci sungguhan akan DITOLAK" + jalan owner; kunci sungguhan jatuh → kalimat layar "TIDAK dikunci, tidak ada yang ditulis"',
    !!RJ && !RJ.ok && /^Ringkasan tahun 2026 GAGAL disusun: contoh rusak — kunci sungguhan akan DITOLAK\. Tutup lalu buka lagi aplikasinya/.test(RJ.teks)
    && /^Kunci tahun 2026 gagal disusun \(contoh rusak\) — tahun 2026 TIDAK dikunci, tidak ada yang ditulis\. Tutup lalu buka lagi/.test(jatuh) && ambilTutupBukuAcara().length === n0, J([RJ, jatuh]));
  try { ringkasPesananTahun = function () { return { 'ps-contoh': undefined, x: NaN }; }; RB = ringkasLatihan(2026, PL.ukuran); RK = susunKunci(2026, D, w, LA); } finally { ringkasPesananTahun = asliS; }
  ok('B9 isian yang ditolak server (tanpa isi, bukan angka): latihan "tidak bisa disimpan server … kunci sungguhan akan DITOLAK"; kunci sungguhan DITOLAK berkalimat sama, tidak ada kiriman',
    !!RB && !RB.ok && /tidak bisa disimpan server: ringkasan › pesanan yang sudah datang › ps-contoh tanpa isi; ringkasan › pesanan yang sudah datang › x bukan angka — kunci sungguhan akan DITOLAK\./.test(RB.teks)
    && !!RK && /tidak bisa disimpan server: ringkasan › pesanan yang sudah datang › ps-contoh tanpa isi; ringkasan › pesanan yang sudah datang › x bukan angka\. Tahun 2026 TIDAK dikunci, tidak ada yang ditulis\./.test(RK.tolak || '') && !RK.kiriman && ambilTutupBukuAcara().length === n0, J([RB, RK && RK.tolak]));
  var RU = ringkasLatihan(2026, BK_BATAS_ISI);
  ok('B9 ringkasan + potret di atas batas: latihan memperingatkan "bisa melewati batas satu dokumen server"', !RU.ok && /^Ringkasan tahun 2026 \d+ KB \+ potret \d+ KB: berita acara tutup buku bisa melewati batas satu dokumen server/.test(RU.teks), RU.teks);
  var RN = susunKunci(2026, D, w, LA);
  ok('B9 penyusun dipulihkan → kunci sungguhan tidak ditolak (pemeriksa isian tidak menolak ringkasan yang benar)', !RN.tolak && RN.kiriman.length > 0 && bkRingkasSiap(2026, ringkasTahun(2026)).ok, RN.tolak || ''); });

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

# ---- ASAP atas cadangan LOKAL (tidak di-commit; dilewati di CI): nota & pesanan TIRUAN supaya laju 14 hari & pesanan Desember ada pada 5 Jan 2027
ASAP = r"""
var salah = []; var J = JSON.stringify; var nId = 900000;
function Wk(iso) { __KINI = new Date(iso).getTime(); return { tanggal: kpWib(new Date(iso)).iso, jam: iso.slice(11, 16), kini: new Date(iso).toISOString(), idUnik: function () { nId += 1; return 'asap' + nId; } }; }
function muatCad() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' }; }
function tiruan() {
  // nota TIRUAN 22 Des – 4 Jan: tiap merek berstok (bukan buku khusus) laku ±(25–70 % stok 21 Des) dalam 14 hari — sebagian merek jadi "perlu dipesan"; stok tidak minus
  var st = stokMerekSaja(hitungStokKarungPerMerk('2026-12-21')); var nota = []; var ke = 0;
  Object.keys(st).sort().forEach(function (m) { var sisa = Number(st[m].sisaKg) || 0; if (sisa < 100) return; ke += 1; var bagian = ke % 3 === 0 ? 0.7 : 0.25; var perHari = Math.floor(sisa * bagian / 14);
    if (perHari <= 0) return; for (var d = new Date('2026-12-22T00:00:00Z'); d.toISOString().slice(0, 10) <= '2027-01-04'; d.setUTCDate(d.getUTCDate() + 1)) { var t = d.toISOString().slice(0, 10);
      nota.push({ koleksi: 'penjualan', data: { id: 'asap-j-' + ke + '-' + t, tanggal: t, jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: m, totalKg: perHari, beratKarungAcuan: 50, jumlahKarung: perHari / 50, hargaTotal: perHari * 14000, hppTotalSaatJual: perHari * 13000, trxId: 'asap-t-' + ke + '-' + t } }); } });
  // pesanan TIRUAN: pemasok pertama 15 Des (+ kedatangan tiruan 16 Des = datang, hanya ringkasan yang tahu sesudah arsip), pemasok kedua 30 Des (menunggu)
  var pem = daftarPemasok().filter(function (p) { return p.kedatangan > 0; }); var tambah = []; var p1 = pem[0], p2 = pem[1] || pem[0];
  if (p1) { var m1 = Object.keys(p1.hargaPerMerk)[0]; var h1 = p1.hargaPerMerk[m1].terakhir.hargaPerKg;
    tambah.push({ koleksi: 'pesananPemasok', data: { id: 'asap-ps1', tanggal: '2026-12-15', jam: '08:00', pemasok: p1.nama, baris: [{ merk: m1, karung: 2, berat: 50, kg: 100, hargaPerKg: h1 }], karung: 2, kg: 100, status: 'menunggu' } });
    tambah.push({ koleksi: 'batchMasuk', data: { id: 'asap-b1', tanggal: '2026-12-16', jam: '09:00', pemasok: p1.nama, caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: m1, satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: h1, subtotalHarga: 100 * h1 }] } }); }
  if (p2) { var m2 = Object.keys(p2.hargaPerMerk).slice(-1)[0]; tambah.push({ koleksi: 'pesananPemasok', data: { id: 'asap-ps2', tanggal: '2026-12-30', jam: '08:00', pemasok: p2.nama, baris: [{ merk: m2, karung: 2, berat: 50, kg: 100, hargaPerKg: p2.hargaPerMerk[m2].terakhir.hargaPerKg }], karung: 2, kg: 100, status: 'menunggu' } }); }
  terapkanKeCache(nota.concat(tambah)); return { nota: nota.length, merek: ke };
}
var LA = { idPerangkat: 'asap-mac', namaPerangkat: 'Mac asap', antre: [], menunggu: 0, offline: false };
function kirimA(k) { var j = jagaKunci(k.dokumen || [], k.hapus || []); if (j) { salah.push('penjaga pusat menolak kiriman: ' + j.pesan); return false; }
  if (k.hapus && k.hapus.length) terapkanKeCache(k.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (k.dokumen && k.dokumen.length) terapkanKeCache(k.dokumen); return true; }
muatCad(); var w = Wk('2027-01-05T10:00:00+07:00'); var kini = new Date(__KINI); var T = tiruan(); var out = { nota: T.nota, merekLaku: T.merek };
var G0 = gerbangBuku(2026, kini, LA, { g3: true }); var isi = {}; G0.belumPutus.forEach(function (t) { isi[t] = 'asap: putusan TIRUAN, bukan putusan owner'; }); var P = G0.belumPutus.length ? susunPutusanHari(isi, w) : { dokumen: [] };
if (P.tolak) salah.push('putusan tiruan ditolak: ' + P.tolak); else terapkanKeCache(P.dokumen);
var A = potretBelanja(kini); var H0 = hitungBelanja({}, kini);
out.sebelum = { pemasokTruk: H0.D.pemasok.length, merek: H0.baris.length, merekBerharga: H0.baris.filter(function (b) { return !!b.pakai; }).length, perlu: H0.baris.filter(function (b) { return b.perlu; }).length, saran: H0.saranSemuaTeks.replace(/^Pakai saran: /, ''), muatanAda: H0.atur.muatanKg > 0,
  pesanan: pesananSemua().map(function (p) { return p.status; }).join(',') };
// sanggahan P4 (temuan 4): langkah Kunci LATIHAN atas data toko — ringkasan tersusun, isiannya diterima server, ringkasan + potret di bawah batas
var PLa = potretLatihan(2026, kini), RLa = ringkasLatihan(2026, PLa.ukuran); out.latihan = { potret: PLa.ok, ringkasan: RLa.ok, ukuranPotret: PLa.ukuran, ukuranRingkasan: RLa.ukuran };
if (!PLa.ok || !RLa.ok) salah.push('latihan Kunci: ' + PLa.teks.slice(0, 200) + ' · ' + RLa.teks.slice(0, 300));
var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'asap', langkah: {} }, w, LA);
if (R.tolak) salah.push('kunci ditolak: ' + R.tolak.slice(0, 300)); else {
  R.kiriman.forEach(kirimA); var Bk = potretBelanja(kini); var d1 = bedaPemasok(A, Bk); if (d1.length) salah.push('sesudah KUNCI ≠ sebelum: ' + d1.slice(0, 4).join(' || ').slice(0, 600));
  var daftar = arsipBuku(2026).daftar; arsipkanDokumen(2026, daftar.slice(0, Math.floor(daftar.length / 2))); var Bs = potretBelanja(kini); var d2 = bedaPemasok(A, Bs); if (d2.length) salah.push('arsip SETENGAH ≠ sebelum: ' + d2.slice(0, 4).join(' || ').slice(0, 600));
  arsipkanDokumen(2026, arsipBuku(2026).daftar); var B = potretBelanja(kini); var d3 = beda(A, B); if (d3.length) salah.push('arsip HABIS ≠ sebelum: ' + d3.slice(0, 4).join(' || ').slice(0, 600));
  var TP = ambilSemuaBatch().filter(function (x) { return x.tutupBuku && x.penandaBuku; })[0] || {}; var RT = TP.ringkasTahun || {};
  // pembanding: ringkasan TANPA pemasok (bentuk sebelum P4) — celah yang ditutup harus terlihat di data toko juga (truk & harga 2026 kosong)
  terapkanKeCache([{ koleksi: 'batchMasuk', data: Object.assign({}, TP, { ringkasTahun: Object.assign({}, RT, { pemasok: undefined, pesananDatang: undefined }) }) }]);
  var H1 = hitungBelanja({}, kini); out.tanpaRingkasanPemasok = { pemasokTruk: H1.D.pemasok.length, merekBerharga: H1.baris.filter(function (b) { return !!b.pakai; }).length, muatanAda: H1.atur.muatanKg > 0 };
  terapkanKeCache([{ koleksi: 'batchMasuk', data: TP }]); if (beda(A, potretBelanja(kini)).length) salah.push('penanda dikembalikan tetapi Belanja tidak kembali sama');
  if (out.tanpaRingkasanPemasok.pemasokTruk >= out.sebelum.pemasokTruk && out.tanpaRingkasanPemasok.merekBerharga >= out.sebelum.merekBerharga) salah.push('pembanding tanpa ringkasan pemasok TIDAK berbeda — asap ini tidak menguji penggabungan');
  out.ringkasan = { pemasok: Object.keys(RT.pemasok || {}).length, pesananDatang: Object.keys(RT.pesananDatang || {}).length, ukuranPemasok: J(RT.pemasok || {}).length, ukuranRingkasan: J(RT).length, bentuk: bentukFirestore(RT, 'ringkasTahun').length };
  out.kedatanganHidup = ambilSemuaBatch().filter(function (b) { return !b.stokAwal && !b.tutupBuku; }).length; out.dibandingkan = Object.keys(A).length;
  if (out.ringkasan.bentuk) salah.push('ringkasan tidak berbentuk Firestore');
  if (!out.sebelum.pemasokTruk || !out.sebelum.merekBerharga) salah.push('asap kosong: tidak ada pemasok / harga sebelum ritual'); }
out.salah = salah; print(J(out));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def bundelan(ganti=None):
    """ganti = (berkas, lama, baru): bundel dengan SATU berkas dirusak (kontrol)."""
    if not ganti: return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))
    b, lama, baru = ganti
    return uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(
        (open(os.path.join(AKAR, m), encoding='utf-8').read().replace(lama, baru) if m == b else open(os.path.join(AKAR, m), encoding='utf-8').read())) for m in MODUL]))


def baca(berkas, ganti=None):
    """isi berkas repo; ganti = (berkas, lama, baru) dari kontrol — berkas yang dirusak dibaca dalam bentuk rusaknya."""
    t = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
    return t.replace(ganti[1], ganti[2]) if ganti and ganti[0] == berkas else t


PROSEDUR = 'docs/prosedur-pulih-darurat.md'
UANG = 'baru/js/layar/uang.js'
# B8 (temuan sedang): kalimat prosedur yang menjaga owner dari putaran batal-ulang — kalau perilakunya berubah (B8 merah), kalimat ini ikut ditinjau
PROSEDUR_B8 = [
    ('daftar periksa 1 Jan: truk sebelum arsip habis → catat SESUDAH pita, menunjuk butir Stok beras',
     'Truk datang sebelum pita "Tahun 2026 terkunci dan arsipnya habis" (ritual tertunda)? Kedatangannya dicatat SESUDAH pita itu'),
    ('daftar periksa 1 Jan: tidak sebelum langkah 6, tidak selama arsip', 'jangan dicatat sebelum langkah 6, jangan juga selama arsip berjalan'),
    ('bab Pemeriksaan: judul butir', '**"Stok beras" beda karena kedatangan Januari yang dicatat SEBELUM kunci**'),
    ('bab Pemeriksaan: sebabnya rata-rata harga beli, kg & uang tidak berubah', 'jadi rupiah baris Stok beras beda walau kg beras dan uangnya tidak berubah'),
    ('bab Pemeriksaan: mengulang ritual beda lagi', 'membatalkan lalu mengulang ritual akan beda LAGI'),
    ('bab Pemeriksaan: kalimat kartu & pita yang dikutip = kalimat aplikasi (B8)', '(kartu: "1 pemeriksaan beda — jangan jualan/menagih\ndulu"; pita: "1 baris TIDAK SAMA (Stok beras)")'),
    ('bab Pemeriksaan: hanya Stok beras ✗ + kelompok 3 ✓ → BUKAN alasan membatalkan, selesai dua kali', 'itu BUKAN alasan\nmembatalkan: ketuk "selesai" dua kali'),
    ('bab Pemeriksaan: bukan penghalang berjualan / kunci bulan Januari', 'untuk kasus ini itu bukan penghalang berjualan, menagih, atau kunci bulan Januari'),
    ('bab Pemeriksaan: pencegahnya', 'kedatangan Januari dicatat SESUDAH pita "Tahun … terkunci dan arsipnya\nhabis"'),
]
# B9 (temuan 4): layar Uang memakai pemeriksa yang diuji B9
UANG_B9 = [
    ('latihan menyusun ringkasan tahun (setelah potret, ukuran potret ikut)', "const PL = BK.potretLatihan(T.tahun, kini()); const RL = BK.ringkasLatihan(T.tahun, PL.ukuran);"),
    ('latihan: kalimat & tanda awas ringkasan', "kabar: 'Latihan: tidak ada yang dikunci. ' + PL.teks + ' ' + RL.teks, kabarAwas: !PL.ok || !RL.ok }"),
    ('susunKunci yang jatuh berkalimat (belum ada yang dikirim)', "let r; try { r = BK.susunKunci(T.tahun, { paraf: s.parafB, saksi: s.saksiB, langkah: s.langkahB, cadangan1: s.cad1, arsipNama: s.arsipNama }, waktu(), lokal()); if (r.tolak) return set({ siapKunci: false, kabar: r.tolak, kabarAwas: true }); } catch (e) { return set({ siapKunci: false, kabar: BK.bkKalimatKunciJatuh(T.tahun, e), kabarAwas: true }); }"),
]


def statis(ganti=None):
    pr, ua = baca(PROSEDUR, ganti), baca(UANG, ganti)
    return ['STATIS prosedur: ' + n for n, t in PROSEDUR_B8 if t not in pr] + ['STATIS uang.js: ' + n for n, t in UANG_B9 if t not in ua]


def utama(js, ganti=None):
    st = statis(ganti)
    h, e = jalan(JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar ID = ' + json.dumps(ID) + ';\n' + BERSAMA + SKENARIO)
    if h is None: return 0, st + ['JSC JATUH: ' + e]
    return h['lulus'] + len(PROSEDUR_B8) + len(UANG_B9) - len(st), st + h['gagal']


BP = 'baru/js/layar/bon-pemasok-logika.js'
BL = 'baru/js/layar/belanja-logika.js'
TB = 'baru/js/layar/tutup-buku-logika.js'
RUSAK = [
    # owner (audit P4 no. 5): kontrol yang mematikan PENGGABUNGAN — wajib merah
    ('penggabungan dimatikan: daftarPemasok tanpa ringkasan tahun (celah lama: truk & harga 2026 hilang)', BP, "const { peta, pastikan } = bpKumpul('', ringkasArsip());", "const { peta, pastikan } = bpKumpul('', null);"),
    ('ringkasan tahun tidak membawa pemasok', TB, "pemasok: ringkasPemasokTahun(c), ", ""),
    ('ringkasan tahun tidak membawa pesanan yang sudah datang', TB, ", pesananDatang: ringkasPesananTahun(c)", ""),
    ('kedatangan yang sudah dihitung ringkasan dihitung dua kali (ids diabaikan)', BP, "const hitung = !dihitung[String(b.id)];", "const hitung = true;"),
    ('harga dari ringkasan menimpa kedatangan 2027 (yang lebih baru kalah)', BP, "const h = s.hargaPerMerk[m] = s.hargaPerMerk[m] || { riwayat: [] };\n      h.riwayat.push(",
     "const h = s.hargaPerMerk[m] = { riwayat: [] };\n      h.riwayat.push("),
    ('12 kedatangan terakhir dari ringkasan tidak dibaca (muatan & kebiasaan bayar)', BP, "(Array.isArray(r.akhir) ? r.akhir : []).forEach(", "[].forEach("),
    ('muatan truk hanya dari catatan hidup (bentuk sebelum P4)', BL, "const kg = [].concat.apply([], daftarPemasok().map((p) => p.batch))",
     "const kg = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok)).map((b) => ({ id: b.id, tanggal: b.tanggal, kg: (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0) }))"),
    ('pesanan: ringkasan tahun tidak dibaca (pesanan Desember kembali menunggu)', BL, "bpPesananDatang(p, batch, p.status === 'batal' || p.status === 'datang' ? null : RA)", "bpPesananDatang(p, batch, null)"),
    ('pesanan: tanggal datang dari kedatangan 2027, bukan yang pertama', BP, "tanggal: r !== null && (!sesudah.length || r < String(hidup || '')) ? r : hidup", "tanggal: r !== null && !sesudah.length ? r : hidup"),
    ('ringkasan 2027 tidak membawa ringkasan 2026 (pemasok lama hilang di tahun kedua)', BP, "const { peta } = bpKumpul(cutoff, R && String(R.cutoff || '') < String(cutoff) ? R : null);", "const { peta } = bpKumpul(cutoff, null);"),
    ('jumlah dari ringkasan tidak ditambahkan (kartu pemasok menyusut)', BP, "s.kedatangan += Number(r.kedatangan) || 0; s.belanja += Number(r.belanja) || 0;", "s.belanja += Number(r.belanja) || 0;"),
    # ---- sanggahan P4 temuan 3: dua mutasi yang dulu DIAM (id contoh bukan angka; tanpa susulan di antara pesanan & kedatangan ringkasan)
    ('nama pemasok dari ringkasan tidak dibaca (urut) — ejaan lama yang masih hidup menang', BP, "if ((Number(r.urut) || 0) >= s.urutNama) { s.nama = String(r.nama).trim(); s.urutNama = Number(r.urut) || 0; }", ""),
    ('tanggal datang pesanan: ringkasan selalu menang (susulan yang lebih awal kalah)', BP, "tanggal: r !== null && (!sesudah.length || r < String(hidup || '')) ? r : hidup", "tanggal: r !== null ? r : hidup"),
    # ---- sanggahan P4 temuan 1 (sedang): kedatangan Januari sebelum kunci — kalimat prosedur & hasil periksa yang dibekukan
    ('prosedur: butir "Stok beras" beda karena kedatangan Januari dihapus', PROSEDUR, '**"Stok beras" beda karena kedatangan Januari yang dicatat SEBELUM kunci** (ritual tertunda: langkah 6 baru jalan sesudah toko menerima truk Januari).\nNilai stok dihitung dari rata-rata harga beli. Sebelum ritual rata-rata itu memakai seluruh pembelian tahun lalu, sesudahnya mulai dari saldo pembuka\n31 Des — kedatangan Januari dirata-rata dengan dasar lain, jadi rupiah baris Stok beras beda walau kg beras dan uangnya tidak berubah. Kedatangan itu tetap\nada, jadi membatalkan lalu mengulang ritual akan beda LAGI. Kalau yang ✗ HANYA baris **Stok beras** (kartu: "1 pemeriksaan beda — jangan jualan/menagih\ndulu"; pita: "1 baris TIDAK SAMA (Stok beras)") dan semua baris lain ✓ — termasuk kelompok 3 (buku beras per merek = catatan 31 Des) — itu BUKAN alasan\nmembatalkan: ketuk "selesai" dua kali (ketukan kedua menerima beda itu dan mencatatnya di berita acara) dan tulis tanggal kedatangannya di catatan kertas\ntutup buku. Kartu tetap menyebut "1 pemeriksaan beda" sampai akhir Februari; untuk kasus ini itu bukan penghalang berjualan, menagih, atau kunci bulan Januari.\nAda baris lain yang ikut ✗ → jalan keluar biasa di bawah. Supaya tidak terjadi: kedatangan Januari dicatat SESUDAH pita "Tahun … terkunci dan arsipnya\nhabis" (barang boleh diturunkan, bon kertasnya disimpan dulu) — jangan sebelum kunci, jangan selama arsip berjalan.\n', ''),
    ('prosedur: petunjuk daftar periksa 1 Jan (catat sesudah arsip habis) dihapus', PROSEDUR, '      - Truk datang sebelum pita "Tahun 2026 terkunci dan arsipnya habis" (ritual tertunda)? Kedatangannya dicatat SESUDAH pita itu — barangnya boleh\n        diturunkan, bon kertasnya disimpan dulu; jangan dicatat sebelum langkah 6, jangan juga selama arsip berjalan. Sudah terlanjur dicatat sebelum\n        langkah 6: bab "Pemeriksaan sesudah tutup buku", butir **"Stok beras" beda karena kedatangan Januari yang dicatat SEBELUM kunci**.\n', ''),
    ('hasil periksa ulang tidak dibekukan saat arsip habis (dihitung ulang tiap kali — kedatangan sesudah arsip ikut terbaca)', TB,
     "if (!P || !Array.isArray(P.baris) || !bkPercobaan(a) || String(P.percobaan || '') !== bkPercobaan(a)) return periksaUlangBuku(tahun);",
     "if (true || !P || !Array.isArray(P.baris) || !bkPercobaan(a) || String(P.percobaan || '') !== bkPercobaan(a)) return periksaUlangBuku(tahun);"),
    # ---- sanggahan P4 temuan 4: ringkasan tahun diperiksa di LATIHAN & di pintu kunci sungguhan
    ('latihan tidak menyusun ringkasan tahun (uang.js)', UANG, "const RL = BK.ringkasLatihan(T.tahun, PL.ukuran);", "const RL = { ok: true, teks: '' };"),
    ('susunKunci yang jatuh tanpa kalimat (uang.js)', UANG, "catch (e) { return set({ siapKunci: false, kabar: BK.bkKalimatKunciJatuh(T.tahun, e), kabarAwas: true }); }", "catch (e) { throw e; }"),
    ('kunci sungguhan tidak memeriksa isian ringkasan', TB, "const RS = bkRingkasSiap(tahun, tanda.data.ringkasTahun); if (!RS.ok)", "const RS = { ok: true }; if (!RS.ok)"),
    ('pemeriksa isian buta "tanpa isi" (undefined)', TB, "if (o === undefined) hasil.push(J + ' tanpa isi');", "if (o === undefined) void 0;"),
    ('latihan buta ukuran (ringkasan + potret)', TB, "if (S.ukuran + pot > BK_BATAS_ISI) return", "if (false) return"),
    ('latihan: penyusun ringkasan yang jatuh ikut menjatuhkan latihan', TB, "catch (e) { return { ok: false, teks: 'Ringkasan tahun ' + tahun + ' GAGAL disusun: '",
     "catch (e) { throw e; return { ok: false, teks: 'Ringkasan tahun ' + tahun + ' GAGAL disusun: '"),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, lama, baru in RUSAK:
            asli = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
            if asli.count(lama) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(bundelan((berkas, lama, baru)), (berkas, lama, baru))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:160] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    js = bundelan(); l, g = utama(js)
    for x in g: print('   ✗ ' + x[:700])
    print('BELANJA SESUDAH TUTUP BUKU (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    berkas = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--cadangan=')), '') or os.environ.get('UJI_CADANGAN', '')
    if berkas and os.environ.get('GITHUB_ACTIONS'): print('ASAP CADANGAN dilewati (CI)')
    elif berkas and not g:
        if not os.path.isfile(berkas): print('ASAP CADANGAN: berkas tidak ada — ' + berkas); sys.exit(2)
        a, e = jalan(JAM + js + '\nvar CAD = ' + open(berkas, encoding='utf-8').read() + ';\n' + BERSAMA + ASAP)
        if a is None: print('ASAP CADANGAN JATUH: ' + e); sys.exit(2)
        print('ASAP CADANGAN (%s) 5 Jan 2027 · nota tiruan %d (%d merek) · sebelum: %s · ringkasan: %s · latihan Kunci: %s · kedatangan hidup sesudah arsip %s · %s hal dibandingkan · pembanding tanpa ringkasan pemasok: %s'
              % (os.path.basename(berkas), a.get('nota', 0), a.get('merekLaku', 0), json.dumps(a.get('sebelum'), ensure_ascii=False), json.dumps(a.get('ringkasan')), json.dumps(a.get('latihan')), a.get('kedatanganHidup'), a.get('dibandingkan'), json.dumps(a.get('tanpaRingkasanPemasok'))))
        for x in a['salah']: print('   ✗ ASAP ' + x[:700])
        print('ASAP CADANGAN: ' + ('LULUS — Belanja sebelum = sesudah kunci / setengah arsip / arsip habis' if not a['salah'] else '%d GAGAL' % len(a['salah'])))
        if a['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
