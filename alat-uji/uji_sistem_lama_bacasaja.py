#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_sistem_lama_bacasaja.py — putaran 25b Bagian B: SISTEM LAMA (index.html) HANYA-BACA lewat SATU penjaga, keputusan owner 26 Sep 2026.

STATIS (sumber index.html):
  · setiap panggilan setDoc / deleteDoc / runTransaction berada di fungsi yang bertanya ke penjagaTulis() SEBELUM menulis (catatLogAktivitas =
    jejak pembantu: semua pemanggilnya berpenjaga); tidak ada writeBatch / updateDoc / addDoc
  · yang TETAP TERBUKA persis keputusan owner: pengaturan/jenisBeras, pengaturan/aksesKasir, pengaturan/keamanan (+ pulihkan lewat konfirmasi
    ketik); yang bukan catatan persis: katalog kasir, denyut, antrean lama sekali
  · perulangan kirim ulang antrean (setInterval / tiap sinyal kembali) tidak ada lagi; antrean-sekali tidak memanggil modal sandi
  · pita permanen berbunyi "Sistem lama sekarang hanya-baca. Catat dan batalkan di /baru/" dengan tautan ke baru/
PERAMBAN (Chrome headless, index.html SUNGGUHAN, Firebase PALSU lokal yang menolak catatan bertanggal sebelum September seperti bulan terkunci):
  · antrean lama (3 catatan, 1 bertanggal Agustus) dikirim SEKALI sesudah masuk: 2 masuk, 1 ke daftar "ditolak" (isi utuh), antrean kosong,
    modal sandi TIDAK muncul, pita menyebutnya; "kirim sekali lagi" tidak mengirim ulang yang ditolak
  · setiap jalan tulis catatan ditolak penjaga: simpan & hapus untuk semua koleksi bertanggal dan koleksi lain yang sudah pindah ke /baru/
    (termasuk titik kas & tempat simpan), tombol sungguhan hapus nota & hapus uang keluar — nol tulisan ke server, tidak masuk antrean, modal
    hanya-baca tampil, alert "cek internet" yang bohong diredam
  · yang terbuka tetap jalan: setelan jenis beras, operator kasir, PIN owner; katalog kasir & denyut terbit sendiri; pulihkan dari berkas
    cadangan hanya sesudah mengetik PULIHKAN (batal = nol tulisan), dan sesudahnya penjaga kembali menutup
  · fitur baca tetap jalan: riwayat penjualan tergambar dari data server
  · tanpa ketukan apa pun: tidak ada satu pun penolakan (halaman tidak mencoba menulis catatan sendiri)

    python3 alat-uji/uji_sistem_lama_bacasaja.py            → N lulus · 0 gagal
    python3 alat-uji/uji_sistem_lama_bacasaja.py --kontrol  → penjaga yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, shutil, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from uji_antrean_kasir import CHROME, layani, buka, hasil_dari, teks_stat  # noqa: E402  (Chrome headless + server /_siap /_tahan /_hasil yang sama)

PESAN = 'Sistem lama sekarang hanya-baca. Catat dan batalkan di /baru/'
TERBUKA = {'pengaturan/jenisBeras', 'pengaturan/aksesKasir', 'pengaturan/keamanan'}
BUKAN_CATATAN = {'katalog', 'denyut', 'antrean-sekali'}
SDK = 'https://www.gstatic.com/firebasejs/10.13.0/'

# ---------- Firebase PALSU (permukaan yang diimpor index.html) ----------
PALSU = {
    'firebase-app.js': "export function initializeApp(c) { return { options: c }; }\n",
    'firebase-auth.js': r"""
export const browserLocalPersistence = {};
const A = { currentUser: null };
export function getAuth() { return A; }
export function setPersistence() { return Promise.resolve(); }
export function signInWithEmailAndPassword() { return Promise.reject({ code: 'auth/uji-palsu' }); }
export function onAuthStateChanged(a, f) { setTimeout(() => { A.currentUser = window.__ujiUser || null; f(A.currentUser); }, 30); return () => {}; }
""",
    'firebase-firestore.js': r"""
const T = () => (window.__ujiTulis = window.__ujiTulis || []);
const D = () => window.__ujiData || {};
export function getFirestore() { return { palsu: true }; }
export const collection = (db, nama) => ({ nama }), doc = (db, nama, id) => ({ nama, id: String(id) });
export const query = (c) => c, orderBy = () => ({}), limit = () => ({});
const tolak = (ref, data) => (window.__ujiTolak ? window.__ujiTolak(ref.nama, ref.id, data) : false);
export function setDoc(ref, data) { T().push(['set', ref.nama, ref.id, data && data.tanggal || '']); return tolak(ref, data) ? Promise.reject({ code: 'permission-denied', message: 'Missing or insufficient permissions.' }) : Promise.resolve(); }
export function deleteDoc(ref) { T().push(['hapus', ref.nama, ref.id]); return Promise.resolve(); }
export function runTransaction() { T().push(['transaksi']); return Promise.resolve({}); }
export function onSnapshot(ref, ok) {
  setTimeout(() => {
    if (ref.id !== undefined) { const d = (D()[ref.nama] || []).find((x) => String(x.id) === ref.id) || null; ok({ id: ref.id, exists: () => !!d, data: () => d }); return; }
    const docs = (D()[ref.nama] || []).map((x) => ({ id: String(x.id), data: () => x, exists: () => true }));
    ok({ docs, size: docs.length, empty: !docs.length, forEach: (f) => docs.forEach(f), metadata: { fromCache: false, hasPendingWrites: false }, docChanges: () => [] });
  }, 10);
  return () => {};
}
""",
}

# Tanggal contoh = HARI INI di mesin yang menjalankan uji (Chrome memakai zona waktu yang sama). Dulu dipaku '2026-09-26': riwayat penjualan
# sistem lama menampilkan transaksi hari ini, jadi sejak 27 Sep pemeriksaan "fitur baca" gagal (di Mac pengembang lewat tengah malam WIB,
# di runner mulai 00.00 UTC = 07.00 WIB).
HARI = __import__('datetime').date.today().isoformat()
ANTREAN_LAMA = [
    {'koleksi': 'penjualan', 'data': {'id': 7001, 'tanggal': '2026-09-20', 'jam': '10:00', 'jenis': 'karung', 'namaProduk': 'Beras Contoh (karung utuh)', 'hargaTotal': 600000, 'caraBayar': 'Tunai'}},
    {'koleksi': 'penjualan', 'data': {'id': 7002, 'tanggal': '2026-08-20', 'jam': '11:00', 'jenis': 'karung', 'namaProduk': 'Beras Contoh (karung utuh)', 'hargaTotal': 610000, 'caraBayar': 'Tunai'}},
    {'koleksi': 'pengeluaranHarian', 'data': {'id': 7003, 'tanggal': '2026-09-21', 'kategori': 'toko', 'nominal': 15000, 'keterangan': 'Plastik contoh'}},
]
DATA = {'penjualan': [{'id': 8001, 'tanggal': HARI, 'jam': '09:30', 'jenis': 'karung', 'merkSumber': 'Beras Contoh', 'namaProduk': 'Beras Contoh (karung utuh)',
                       'jumlahKarung': 1, 'beratKarungAcuan': 50, 'totalKg': 50, 'hargaTotal': 600000, 'hppTotalSaatJual': 550000, 'caraBayar': 'Tunai', 'namaPelanggan': 'Pembeli Contoh Riwayat'}],
        'pengeluaranHarian': [{'id': 8101, 'tanggal': HARI, 'kategori': 'toko', 'nominal': 10000, 'keterangan': 'Contoh'}]}
DIKUNCI_SIMPAN = ['penjualan', 'retur', 'pengeluaranHarian', 'piutangMutasi', 'kasbonMutasi', 'utangPemasokMutasi', 'utangOwnerMutasi', 'batchMasuk', 'produksiKemasan',
                  'stokBahanKemasan', 'stokBahanLiteran', 'penyesuaianStok', 'penyesuaianKemasan', 'amplopLaba', 'modalOwner', 'setoranKas', 'biayaBulanan', 'tutupHari',
                  'pindahUang', 'slipUpah', 'karantina', 'katalogHargaKarung', 'katalogHargaKemasan', 'katalogHargaLiteran', 'pelangganCatatan', 'pesanan', 'thrPelanggan',
                  'pemasokCatatan', 'titipanHarian', 'tembusanStok', 'aturanToko', 'wadahLiteran', 'hargaWadah']

KEPALA = r"""<script>
(function () {
  window.__ujiUser = { email: 'owner@tokoberasmiqbal.web.app', uid: 'uid-owner-uji', getIdToken: function () { return Promise.resolve('t-uji'); } };
  // REST mentah ke Firestore (segarkanRoster membaca pengaturan/aksesKasir) dijawab lokal: tidak ada jaringan luar di uji ini
  var asli = window.fetch.bind(window); window.__ujiRest = [];
  window.fetch = function (u, o) { u = String(u); if (u.indexOf('googleapis.com') >= 0) { window.__ujiRest.push([(o && o.method) || 'GET', u.split('?')[0].split('/documents/')[1] || u]); return Promise.resolve(new Response('{}', { status: 404 })); } return asli(u, o); };
  window.__ujiData = __DATA__;
  window.__ujiTolak = function (koleksi, id, data) { return !!(data && data.tanggal && String(data.tanggal) < '2026-09-01'); };   // "Agustus terkunci"
  window.__ujiAlert = []; window.alert = function (m) { window.__ujiAlert.push(String(m)); };
  window.__ujiPrompt = 'alasan uji'; window.prompt = function () { return window.__ujiPrompt; };
  window.confirm = function () { return true };
  window.__ujiGalat = []; window.addEventListener('error', function (e) { window.__ujiGalat.push(String(e.message || e)); });
  try { if (location.search.indexOf('s=utama') >= 0) localStorage.setItem('miqbal_antrean_tunda_v1', JSON.stringify(__ANTREAN__)); } catch (e) {}
})();
</script>"""

SKENARIO = r"""<script>
(async function () {
  var tunggu = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var sampai = async function (f, ms) { var t0 = Date.now(); while (Date.now() - t0 < (ms || 8000)) { try { if (f()) return true; } catch (e) {} await tunggu(40); } return false; };
  var hasil = {}; var U; var T = function () { return window.__ujiTulis || []; };
  var tampil = function (id) { var e = document.getElementById(id); return !!e && e.classList.contains('tampil'); };
  var L = function (k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return null; } };
  try {
    await sampai(function () { return window.__uji; }); U = window.__uji;
    await sampai(function () { return T().filter(function (t) { return t[1] === 'penjualan' || t[1] === 'pengeluaranHarian'; }).length >= 3; }, 6000);
    await tunggu(4800);   // katalog kasir terbit 4 detik sesudah data berubah
    hasil.awal = { tulis: T().slice(), antrean: L('miqbal_antrean_tunda_v1'), ditolak: L('miqbal_antrean_ditolak_v1'), modalSandi: tampil('modalLoginBg'), modalHanyaBaca: tampil('modalHanyaBacaBg'),
      pitaUtama: (document.getElementById('pitaHanyaBaca') || {}).innerText || '', pitaAntrean: (document.getElementById('pitaAntreanLama') || {}).innerText || '', alert: window.__ujiAlert.slice() };
    var n0 = T().length; window.kirimAntreanTunda(); await tunggu(400);
    hasil.kirimLagi = { tulisBaru: T().slice(n0) };
    // ---- setiap jalan tulis catatan ditolak
    hasil.tolak = [];
    for (var i = 0; i < DIKUNCI.length; i++) {
      var k = DIKUNCI[i]; var nA = T().length; var aA = L('miqbal_antrean_tunda_v1').length; var alA = window.__ujiAlert.length; U.tutupModalHanyaBaca(); var kode = '';
      try { await U.simpanKeFirestore(k, { id: 'uji-' + k, tanggal: '2026-09-26', bulan: '2026-09', nominal: 1 }); } catch (e) { kode = String(e && e.code || e); }
      var kodeH = ''; try { await U.hapusDariFirestore(k, 'uji-hapus-' + k); } catch (e) { kodeH = String(e && e.code || e); }
      hasil.tolak.push({ k: k, kode: kode, kodeH: kodeH, tulis: T().length - nA, antrean: L('miqbal_antrean_tunda_v1').length - aA, modal: tampil('modalHanyaBacaBg') });
    }
    var extra = [['pengaturan', 'titikKas'], ['pengaturan', 'tempatSimpan']];
    for (var j = 0; j < extra.length; j++) { var nB = T().length; var kd = ''; try { await U.simpanKeFirestore(extra[j][0], { id: extra[j][1], tanggal: '2026-09-26' }); } catch (e) { kd = String(e && e.code || e); } hasil.tolak.push({ k: extra[j].join('/'), kode: kd, kodeH: 'hanya-baca', tulis: T().length - nB, antrean: 0, modal: tampil('modalHanyaBacaBg') }); }
    // tombol sungguhan (confirm → ya): hapus nota & hapus uang keluar
    U.tutupModalHanyaBaca(); var nC = T().length; var alC = window.__ujiAlert.length;
    await window.hapusPenjualan(8001); await window.hapusHarian(8101); await tunggu(200);
    hasil.tombol = { tulis: T().length - nC, alertBaru: window.__ujiAlert.slice(alC), modal: tampil('modalHanyaBacaBg') };
    // ---- yang terbuka
    var nD = T().length; var galatTerbuka = [];
    for (var m = 0; m < TERBUKA.length; m++) { try { await U.simpanKeFirestore('pengaturan', { id: TERBUKA[m], peta: {}, diubahPada: '2026-09-26T03:00:00.000Z' }); } catch (e) { galatTerbuka.push(TERBUKA[m] + ':' + (e && e.code)); } }
    hasil.terbuka = { tulis: T().slice(nD), galat: galatTerbuka };
    // ---- pulihkan dari berkas cadangan: batal (ketikan salah) lalu PULIHKAN
    var berkas = function () { return new File([JSON.stringify({ versi: 5, penjualan: [{ id: 'pulih-1', tanggal: '2026-09-25', jam: '08:00', jenis: 'karung', hargaTotal: 1, caraBayar: 'Tunai' }] })], 'backup.json', { type: 'application/json' }); };
    window.__ujiPrompt = 'pulih'; var nE = T().length; window.muatDariFile({ target: { files: [berkas()], value: 'x' } }); await tunggu(700);
    hasil.pulihBatal = { tulis: T().slice(nE) };
    window.__ujiPrompt = 'PULIHKAN'; var nF = T().length; window.muatDariFile({ target: { files: [berkas()], value: 'x' } }); await sampai(function () { return T().slice(nF).some(function (t) { return t[2] === 'pulih-1'; }); }, 3000); await tunggu(300);
    hasil.pulih = { tulis: T().slice(nF) };
    var nG = T().length; var kdG = ''; try { await U.simpanKeFirestore('penjualan', { id: 'sesudah-pulih', tanggal: '2026-09-26' }); } catch (e) { kdG = String(e && e.code); }
    hasil.sesudahPulih = { kode: kdG, tulis: T().length - nG };
    // ---- fitur baca
    window.pindahHalaman('jual'); if (U.tampilkanRiwayatJual) U.tampilkanRiwayatJual(); await tunggu(300);
    hasil.baca = { riwayat: ((document.getElementById('daftarRiwayatJual') || {}).innerText || '').slice(0, 2000) };
    hasil.galat = window.__ujiGalat.slice(); hasil.rest = window.__ujiRest.slice();
  } catch (e) { hasil.galatSkenario = String(e && (e.stack || e.message) || e); }
  // hasil dikirim LANGSUNG ke server uji sebelum /_siap — tidak lewat DOM yang harus diserahkan Chrome (docs/catatan-uji-peramban.md)
  try { await fetch('/_hasil' + location.search, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(hasil) }); } catch (e) {}
  fetch('/_siap');
})();
</script>"""

KAIT = "\n  // uji_sistem_lama_bacasaja: pegangan uji (SALINAN uji saja)\n  window.__uji = { simpanKeFirestore, hapusDariFirestore, penjagaTulis, tutupModalHanyaBaca, tampilkanRiwayatJual };\n"


def sumber(teks=None):
    return teks if teks is not None else open(os.path.join(AKAR, 'index.html'), encoding='utf-8').read()


# ---------- STATIS ----------
def fungsi_pembungkus(baris, i):
    for j in range(i, -1, -1):
        m = re.match(r'^  (?:async )?function (\w+)\s*\(', baris[j])
        if m: return m.group(1), j
    return None, None


def periksa_statis(s):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    m = re.search(r'<script type="module">(.*)</script>\s*</body>', s, re.S); modul = m.group(1) if m else ''
    ok('modul index.html ditemukan', bool(modul))
    imp = re.search(r'import \{([^}]*)\} from "' + re.escape(SDK) + 'firebase-firestore.js"', modul)
    ok('tidak ada writeBatch / updateDoc / addDoc di impor Firestore', imp and not re.search(r'\b(writeBatch|updateDoc|addDoc)\b', imp.group(1)), imp.group(1) if imp else '')
    baris = modul.split('\n'); tanpa = []; titik = 0; pembantu = {}
    for i, b in enumerate(baris):
        if re.match(r'^\s*(//|\*)', b) or 'import {' in b or re.match(r'^\s*getFirestore, collection', b): continue
        for x in re.finditer(r'\b(setDoc|deleteDoc|runTransaction)\(', b):
            f, j = fungsi_pembungkus(baris, i); titik += 1
            if f == 'catatLogAktivitas': pembantu[f] = True; continue
            sebelum = '\n'.join(baris[j:i]) + '\n' + b[:x.start()]   # badan fungsi SEBELUM panggilan tulis ini
            if 'penjagaTulis(' not in sebelum: tanpa.append('%s (%s, baris modul %d)' % (x.group(1), f, i + 1))
    ok('%d panggilan setDoc/deleteDoc/runTransaction — semuanya di fungsi yang bertanya ke penjagaTulis() lebih dulu' % titik, titik >= 8 and not tanpa, tanpa)
    # catatLogAktivitas: tiap pemanggilnya berpenjaga sebelum memanggil
    tanpaLog = []
    for i, b in enumerate(baris):
        if 'catatLogAktivitas(' in b and not re.match(r'^  function catatLogAktivitas', b) and not re.match(r'^\s*//', b):
            f, j = fungsi_pembungkus(baris, i)
            if 'penjagaTulis(' not in '\n'.join(baris[j:i + 1]): tanpaLog.append('%s baris %d' % (f, i + 1))
    ok('jejak (catatLogAktivitas) hanya dipanggil sesudah penjaga', not tanpaLog, tanpaLog)
    tb = re.search(r"const TULIS_TERBUKA = \{([^}]*)\};", modul); jb = re.search(r"const JALUR_BUKAN_CATATAN = \{([^}]*)\};", modul)
    ok('yang TETAP TERBUKA persis keputusan owner: jenis beras, operator kasir, PIN owner', tb and set(re.findall(r"'(pengaturan/\w+)'", tb.group(1))) == TERBUKA and len(re.findall(r"'[^']+':", tb.group(1))) == 3, tb.group(1) if tb else '')
    ok('jalur bukan-catatan persis: katalog kasir, denyut, antrean lama sekali', jb and set(re.findall(r"'?([\w-]+)'?:", jb.group(1))) == BUKAN_CATATAN, jb.group(1) if jb else '')
    ok('penjaga menolak jalur di luar daftar (tidak ada "return true" tanpa syarat)', re.search(r"function penjagaTulis\(jalur, koleksi, id\) \{\n    if \(JALUR_BUKAN_CATATAN\[jalur\]\) return true;\n    if \(jalur === 'simpan' && \(_modePulih \|\| TULIS_TERBUKA\[koleksi \+ '/' \+ id\]\)\) return true;\n    _tolakHanyaBacaPada = Date.now\(\);", modul))
    ok('simpanKeFirestore & hapusDariFirestore bertanya ke penjaga di baris PERTAMA', re.search(r"async function simpanKeFirestore\(nomorKoleksi, data\) \{\n    if \(!penjagaTulis\('simpan', nomorKoleksi, data && data\.id\)\) throw galatHanyaBaca\(\);", modul)
       and re.search(r"async function hapusDariFirestore\(nomorKoleksi, id\) \{\n    if \(!penjagaTulis\('hapus', nomorKoleksi, id\)\) throw galatHanyaBaca\(\);", modul))
    ok('perulangan kirim ulang antrean DICABUT (tidak ada setInterval / listener sinyal ke kirimAntreanTunda)', not re.search(r'setInterval\(\s*kirimAntreanTunda|addEventListener\(\s*.online.\s*,\s*kirimAntreanTunda', modul))
    ks = re.search(r'async function kirimAntreanSekali\(manual\) \{(.*?)\n  \}\n', modul, re.S)
    ok('antrean lama sekali: tanpa modal sandi, tanpa while/perulangan ulang', ks and 'mintaLoginKalauDitolak' not in ks.group(1) and 'while' not in ks.group(1) and '_kirimSekaliSudah = true' in ks.group(1))
    pita = re.search(r'<div id="pitaHanyaBaca"[^>]*>(.*?)<div id="pitaAntreanLama">', s, re.S)
    ok('pita permanen: "' + PESAN + '" + tautan ke baru/', pita and PESAN.replace(' /baru/', '') in re.sub(r'<[^>]+>', '', pita.group(1)).replace(' /baru/ ›', '') and 'href="baru/"' in pita.group(1), pita.group(1) if pita else '')
    ok('pulihkan dari berkas cadangan minta ketik PULIHKAN sebelum mode pulih', re.search(r"if \(String\(ketikPulih \|\| ''\)\.trim\(\)\.toUpperCase\(\) !== 'PULIHKAN'\) \{ event\.target\.value = ''; return; \}\n        _modePulih = true;", modul) and '_modePulih = false;' in modul)
    return out


# ---------- PERAMBAN ----------
def siapkan(teks):
    d = tempfile.mkdtemp(prefix='bacasaja-')
    shutil.copytree(os.path.join(AKAR, 'lib'), os.path.join(d, 'lib'))
    os.makedirs(os.path.join(d, '_palsu'))
    for nama, isi in PALSU.items():
        open(os.path.join(d, '_palsu', nama), 'w', encoding='utf-8').write(isi)
        assert SDK + nama in teks, 'impor ' + nama + ' berubah — perbarui uji'; teks = teks.replace(SDK + nama, '/_palsu/' + nama)
    i = teks.rindex('</script>'); teks = teks[:i] + KAIT + teks[i:]
    kepala = KEPALA.replace('__DATA__', json.dumps(DATA)).replace('__ANTREAN__', json.dumps(ANTREAN_LAMA))
    sk = SKENARIO.replace('var hasil = {};', 'var hasil = {}; var DIKUNCI = ' + json.dumps(DIKUNCI_SIMPAN) + '; var TERBUKA = ' + json.dumps(sorted(x.split('/')[1] for x in TERBUKA)) + ';')
    teks = teks.replace('<head>', '<head>' + kepala, 1).replace('</body>', sk + "<img src='/_tahan' alt='' style='display:none'></body>", 1)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(teks)
    return d


def periksa_peramban(teks):
    out = []; ok = lambda n, c, k='': out.append(('peramban · ' + n, bool(c), k))
    if not CHROME: return [('peramban · Google Chrome tersedia', False, 'tidak ditemukan')]
    d = siapkan(teks); srv, port, keadaan = layani(d); profil = tempfile.mkdtemp(prefix='bacasaja-profil-')
    try:
        h = hasil_dari(buka(port, keadaan, profil, '/index.html?s=utama', tunggu=90))
    finally:
        srv.shutdown(); shutil.rmtree(profil, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)
    if not h or h.get('galatSkenario'): return [('peramban · skenario jalan', False, (h or {}).get('galatSkenario', 'tidak ada hasil (halaman tidak jalan)'))]
    A = h['awal']; tulis = A['tulis']
    kirim = lambda k, i: [t for t in tulis if t[1] == k and str(t[2]) == str(i)]
    ok('antrean lama: tiap catatan dikirim SEKALI (7001, 7002, 7003)', all(len(kirim(k, i)) == 1 for k, i in (('penjualan', 7001), ('penjualan', 7002), ('pengeluaranHarian', 7003))), tulis)
    ok('antrean lama: yang masuk selesai, antrean kosong', A['antrean'] == [], A['antrean'])
    ok('antrean lama: yang ditolak (Agustus) pindah ke daftar "ditolak" dengan isi utuh', len(A['ditolak']) == 1 and A['ditolak'][0]['data']['id'] == 7002 and A['ditolak'][0]['data']['hargaTotal'] == 610000, A['ditolak'])
    ok('antrean lama: modal sandi ("Database terkunci") TIDAK muncul', not A['modalSandi'])
    ok('pita permanen tampil: "' + PESAN + '"', 'Sistem lama sekarang hanya-baca' in A['pitaUtama'] and '/baru/' in A['pitaUtama'], A['pitaUtama'])
    ok('pita menyebut catatan lama yang ditolak untuk dicatat ulang di /baru/', '1 catatan lama DITOLAK server' in A['pitaAntrean'], A['pitaAntrean'])
    ok('"kirim sekali lagi" tidak mengirim ulang yang ditolak (nol tulisan catatan)', not [t for t in h['kirimLagi']['tulisBaru'] if t[1] not in ('perangkatStatus', 'ringkasanKasir')], h['kirimLagi'])
    ok('tanpa ketukan apa pun: penjaga tidak pernah menolak (modal hanya-baca tidak muncul) & tidak ada alert', not A['modalHanyaBaca'] and not A['alert'], A)
    ok('katalog kasir (ringkasanKasir) tetap terbit sendiri — jalur bukan-catatan', any(t[1] == 'ringkasanKasir' for t in tulis), [t[1] for t in tulis])
    ok('denyut perangkat tetap terkirim', any(t[1] == 'perangkatStatus' for t in tulis))
    ok('tidak ada tulisan lain saat halaman dibuka (selain antrean sekali, katalog, denyut)', not [t for t in tulis if t[1] not in ('perangkatStatus', 'ringkasanKasir') and str(t[2]) not in ('7001', '7002', '7003')], tulis)
    bocor = [x for x in h['tolak'] if not (x['kode'] == 'hanya-baca' and x['kodeH'] == 'hanya-baca' and x['tulis'] == 0 and x['antrean'] == 0 and x['modal'])]
    ok('%d koleksi (semua bertanggal + yang sudah pindah ke /baru/ + titik kas & tempat simpan): simpan & hapus DITOLAK penjaga, nol tulisan, tidak masuk antrean, modal hanya-baca tampil' % len(h['tolak']),
       len(h['tolak']) == len(DIKUNCI_SIMPAN) + 2 and not bocor, bocor[:3])
    T = h['tombol']
    ok('tombol sungguhan hapus nota & hapus uang keluar: nol tulisan, modal hanya-baca, alert "cek internet" diredam', T['tulis'] == 0 and T['modal'] and not T['alertBaru'], T)
    ok('terbuka: setelan jenis beras, operator kasir, PIN owner tetap tersimpan', sorted(t[2] for t in h['terbuka']['tulis'] if t[1] == 'pengaturan') == sorted(x.split('/')[1] for x in TERBUKA) and not h['terbuka']['galat'], h['terbuka'])
    ok('pulihkan: ketikan salah = batal, nol tulisan', not h['pulihBatal']['tulis'], h['pulihBatal'])
    ok('pulihkan: sesudah mengetik PULIHKAN, catatan dari berkas terunggah', any(t[1] == 'penjualan' and t[2] == 'pulih-1' for t in h['pulih']['tulis']), h['pulih'])
    ok('sesudah pulihkan, penjaga menutup lagi', h['sesudahPulih']['kode'] == 'hanya-baca' and h['sesudahPulih']['tulis'] == 0, h['sesudahPulih'])
    ok('fitur baca: riwayat penjualan tergambar dari data server', 'Pembeli Contoh Riwayat' in h['baca']['riwayat'] or 'Beras Contoh' in h['baca']['riwayat'], h['baca']['riwayat'][:300])
    ok('tidak ada galat JavaScript di halaman', not h.get('galat'), h.get('galat'))
    ok('jalan REST mentah hanya MEMBACA (nol PATCH/POST/DELETE ke Firestore dari sistem lama)', all(r[0] == 'GET' for r in h.get('rest') or []), h.get('rest'))
    return out


def semua(teks=None, bagian=('statis', 'peramban')):
    t = sumber(teks); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'peramban' in bagian: out += periksa_peramban(t)
    return out


KONTROL = [
    ('penjaga dilepas (selalu mengizinkan)', "  function penjagaTulis(jalur, koleksi, id) {\n    if (JALUR_BUKAN_CATATAN[jalur]) return true;", "  function penjagaTulis(jalur, koleksi, id) {\n    return true;\n    if (JALUR_BUKAN_CATATAN[jalur]) return true;", ('statis', 'peramban')),
    ('simpanKeFirestore tidak bertanya ke penjaga', "    if (!penjagaTulis('simpan', nomorKoleksi, data && data.id)) throw galatHanyaBaca();\n", "", ('statis', 'peramban')),
    ('satu transaksi (tutup hari) lepas dari penjaga', "    if (!penjagaTulis('transaksi', KOLEKSI_TUTUP, hariIni)) return;\n", "", ('statis',)),
    ('perulangan kirim ulang antrean kembali', "  async function kirimAntreanTunda() { return kirimAntreanSekali(true); }\n", "  async function kirimAntreanTunda() { return kirimAntreanSekali(true); }\n  setInterval(kirimAntreanTunda, 30000);\n", ('statis',)),
    ('catatan lama yang ditolak DIBUANG (tidak ditulis ke daftar ditolak)', "if (String((e && e.code) || '').includes('permission-denied') && catatDitolakLama(item)) buangDariAntreanTunda(item);", "if (String((e && e.code) || '').includes('permission-denied')) buangDariAntreanTunda(item);", ('peramban',)),
    ('modal sandi muncul lagi di antrean lama', "        // sinyal / timeout: tetap di antrean — TIDAK diulang otomatis\n", "        mintaLoginKalauDitolak(e);\n", ('statis', 'peramban')),
    ('titik kas ikut dibuka (di luar keputusan owner)', "'pengaturan/keamanan': 'PIN owner' };", "'pengaturan/keamanan': 'PIN owner', 'pengaturan/titikKas': 'titik kas' };", ('statis', 'peramban')),
    ('pulihkan tanpa konfirmasi ketik', "        if (String(ketikPulih || '').trim().toUpperCase() !== 'PULIHKAN') { event.target.value = ''; return; }\n", "", ('statis', 'peramban')),
    ('alert "cek internet" tidak diredam', "if (Date.now() - _tolakHanyaBacaPada < 3000) return undefined;", "if (false) return undefined;", ('peramban',)),
    ('pita permanen hilang', 'Sistem lama sekarang hanya-baca. Catat dan batalkan di <a href="baru/">/baru/ ›</a>', '', ('statis', 'peramban')),
]

if __name__ == '__main__':
    S0 = sumber()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, lama, baru, bagian in KONTROL:
            if lama not in S0: print('KONTROL BASI  ' + nama); kode = 3; continue
            h = semua(S0.replace(lama, baru, 1), bagian); g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(S0); g = [x for x in h if not x[1]]
    for n, _, k in g: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:400] if k not in ('', None) else ''))
    print('SISTEM LAMA HANYA-BACA (25b): %d lulus · %d gagal' % (len(h) - len(g), len(g)))
    print(teks_stat())
    sys.exit(1 if g else 0)
