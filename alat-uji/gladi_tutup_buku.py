#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gladi_tutup_buku.py — GLADI TUTUP BUKU di SERVER TIRUAN: Firebase Emulator Suite (Firestore + Auth, aturan = firestore.rules repo) diisi DATA CONTOH
sintetis skala toko (gladi_data_contoh.py), lalu /baru/ ASLI dibuka di Chrome headless lewat ?emulator= (baru/js/data/server-tiruan.js) dan Uang ›
Tutup buku dijalankan lewat layarnya — ketukan sungguhan, bukan fungsi logika.

HANYA DI RUNNER GITHUB ACTIONS (CLAUDE.md, keputusan owner 27 Sep 2026: uji peramban berulang & emulator hanya di runner). Di luar Actions alat ini
MENOLAK jalan, kecuali --periksa-salinan (statis: menyusun salinan uji tanpa Chrome & tanpa emulator). Satu Chrome sekali jalan, grup prosesnya
dimatikan sesudah tiap skenario. Dijalankan di dalam `firebase emulators:exec` (.github/workflows/gladi-tutup-buku.yml).

SKENARIO (urutannya = urutan ritual owner; langkah tiap skenario = daftar nama di SKENARIO, langkahnya fungsi bernama di SKENARIO_JS → mudah disesuaikan
sesudah Paket A mengubah gerbang tutup buku):
  latihan  data MACET · jam halaman 31 Des 2026 21.45 WIB: masuk sebagai owner contoh → muat penuh → Uang › Tutup buku → LATIHAN tujuh langkah sampai
           "Latihan selesai" — TANPA satu pun tulisan/hapus ke server selain denyut perangkat & katalog kasir (latar, bukan tutup buku).
  gerbang  data MACET · jam halaman 1 Jan 2027 15.30 WIB (sesudah reset kuota): mode SUNGGUHAN boleh; gerbang g1 (23 hari tanpa tutup hari) tampil
           memblokir, tombol "1 hal belum beres — bereskan dulu"; mengetuknya tidak memajukan langkah dan tidak menulis apa pun.
  ritual   data BERSIH · 1 Jan 2027 15.30 WIB: SUNGGUHAN sampai paraf → kunci, server MENOLAK kiriman saldo pembuka ke-2 (aturan emulator diganti sementara,
           salinan firestore.rules repo + satu blok ditolak) → kartu "lanjutkan / batalkan" tampil → BATALKAN SEBELUM PENANDA (pembuka ditarik);
           mulai lagi → arsip DITOLAK server di potongan pertama → kartu "lanjutkan / batalkan" → aturan repo dipulihkan → LANJUTKAN → arsip habis
           → BATALKAN SESUDAH PENANDA (arsip dikembalikan, pembuka ditarik) → isi server = sebelum ritual; mulai lagi → selesai (cadangan sesudah).
Tiap langkah: baca (dokumen yang diterima pendengar halaman — penghitung di salinan SDK uji), tulis & hapus (beda isi emulator lewat REST sebelum ↔
sesudah langkah), dibandingkan dengan batas Spark (50 rb baca, 20 rb tulis, 20 rb hapus per hari).

KELUARAN: laporan JSON (--keluar) + ringkasan Markdown (--ringkasan; workflow menempelnya ke halaman ringkasan run). Keluar 0 = semua cek lulus, 2 = gagal.

    python3 alat-uji/gladi_tutup_buku.py --keluar laporan.json --ringkasan ringkasan.md [--skenario latihan,gerbang,ritual]
    python3 alat-uji/gladi_tutup_buku.py --kontrol            → kerusakan di SALINAN uji (latihan menulis, gerbang g1 dibuang, data kurang dimuat) wajib
                                                               membuat cek gagal (keluar 3 kalau ada yang diam)
    python3 alat-uji/gladi_tutup_buku.py --periksa-salinan    → (boleh di Mac) salinan uji disusun & diperiksa statis: CSP salinan = CSP situs + alamat
                                                               emulator saja, jam palsu sebelum meta CSP, SDK penghitung, skenario dari 'self'
"""
import os, re, sys, json, time, shutil, signal, socket, secrets, hashlib, datetime, functools, threading, subprocess, tempfile, socketserver, http.server
import urllib.request, urllib.error, urllib.parse
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import gladi_data_contoh as DC  # noqa: E402

SDK = 'https://www.gstatic.com/firebasejs/10.13.0/'
PROYEK = re.search(r"export const PROYEK_TIRUAN = '([^']+)';", open(os.path.join(AKAR, 'baru/js/data/server-tiruan.js'), encoding='utf-8').read()).group(1)
EMAIL_OWNER = re.search(r"export const EMAIL_OWNER = '([^']+)';", open(os.path.join(AKAR, 'baru/js/data/akses.js'), encoding='utf-8').read()).group(1)
EMAIL_KARYAWAN = 'karyawan.contoh@gladi.contoh'
SPARK = {'baca': 50000, 'tulis': 20000, 'hapus': 20000}
# tulisan LATAR (bukan tutup buku): denyut perangkat & katalog HP kasir yang diterbitkan owner otomatis
LATAR = {'perangkatStatus', 'ringkasanKasir'}
CHROME = next((p for p in ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
                           '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] if os.path.exists(p)), None)
TUNGGU_SKENARIO = {'latihan': 900, 'gerbang': 600, 'ritual': 6000}


def alamat_emulator():
    fs = os.environ.get('FIRESTORE_EMULATOR_HOST') or '127.0.0.1:8080'; au = os.environ.get('FIREBASE_AUTH_EMULATOR_HOST') or '127.0.0.1:9099'
    return fs.replace('localhost', '127.0.0.1'), au.replace('localhost', '127.0.0.1')


FS_HOST, AUTH_HOST = alamat_emulator()
FS, AUTH = 'http://' + FS_HOST, 'http://' + AUTH_HOST
DB = 'projects/%s/databases/(default)' % PROYEK
OWNER = {'Authorization': 'Bearer owner'}   # emulator: lewati aturan (pengisi data & pembaca isi server saja; halaman tetap tunduk aturan repo)


# ============================== REST emulator ==============================
def rest(metode, url, data=None, kepala=None, waktu=180):
    body = None if data is None else json.dumps(data).encode('utf-8')
    h = {'Content-Type': 'application/json'}; h.update(kepala or {})
    req = urllib.request.Request(url, data=body, method=metode, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=waktu) as r: t = r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise RuntimeError('%s %s → HTTP %s: %s' % (metode, url.split('?')[0], e.code, e.read().decode('utf-8', 'replace')[:400]))
    return json.loads(t) if t.strip()[:1] in ('{', '[') else t


def tunggu_emulator(batas=180):
    t0 = time.time(); galat = ''
    while time.time() - t0 < batas:
        try:
            rest('GET', FS + '/', waktu=5); rest('GET', AUTH + '/', waktu=5); return
        except Exception as e: galat = str(e); time.sleep(1)
    raise RuntimeError('emulator tidak menjawab dalam %d dtk: %s' % (batas, galat))


def ke_nilai(v):
    if v is None: return {'nullValue': None}
    if isinstance(v, bool): return {'booleanValue': v}
    if isinstance(v, int): return {'integerValue': str(v)}
    if isinstance(v, float): return {'doubleValue': v}
    if isinstance(v, str): return {'stringValue': v}
    if isinstance(v, list): return {'arrayValue': {'values': [ke_nilai(x) for x in v]}}
    if isinstance(v, dict): return {'mapValue': {'fields': {k: ke_nilai(x) for k, x in v.items()}}}
    raise TypeError('nilai tidak dikenal: %r' % (v,))


def dari_nilai(n):
    if 'nullValue' in n: return None
    if 'booleanValue' in n: return n['booleanValue']
    if 'integerValue' in n: return int(n['integerValue'])
    if 'doubleValue' in n: return float(n['doubleValue'])
    if 'stringValue' in n: return n['stringValue']
    if 'timestampValue' in n: return n['timestampValue']
    if 'arrayValue' in n: return [dari_nilai(x) for x in n['arrayValue'].get('values', [])]
    if 'mapValue' in n: return {k: dari_nilai(x) for k, x in n['mapValue'].get('fields', {}).items()}
    return n


def id_dok(koleksi, d):
    """Id dokumen = String(data.id) persis aplikasi (arsip menghapus doc(koleksi, String(id))); biaya bulanan = bulannya (tbDaftarKoleksi)."""
    return str(d.get('bulan') or d['id']) if koleksi == 'biayaBulanan' else str(d['id'])


def kosongkan():
    rest('DELETE', FS + '/emulator/v1/projects/%s/databases/(default)/documents' % PROYEK)
    rest('DELETE', AUTH + '/emulator/v1/projects/%s/accounts' % PROYEK)


def tulis_rest(daftar):
    """[(koleksi, id, data)] → commit per 400 (Bearer owner, tanpa aturan)."""
    for i in range(0, len(daftar), 400):
        rest('POST', FS + '/v1/' + DB + '/documents:commit', {'writes': [{'update': {'name': DB + '/documents/' + k + '/' + i_, 'fields': {a: ke_nilai(b) for a, b in d.items()}}}
                                                                       for k, i_, d in daftar[i:i + 400]]}, OWNER)


def isi_data(data):
    daftar = [(k, id_dok(k, d), d) for k, v in data.items() if isinstance(v, list) for d in v]
    tulis_rest(daftar); return len(daftar)


def buat_akun(email, sandi):
    r = rest('POST', AUTH + '/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo-kunci-gladi', {'email': email, 'password': sandi, 'returnSecureToken': True})
    return r['localId']


def koleksi_ada():
    out, tok = [], None
    while True:
        r = rest('POST', FS + '/v1/' + DB + '/documents:listCollectionIds', dict({'pageSize': 500}, **({'pageToken': tok} if tok else {})), OWNER)
        out += r.get('collectionIds', []); tok = r.get('nextPageToken')
        if not tok: return sorted(out)


def jalankan_query(koleksi, pilih=True):
    q = {'from': [{'collectionId': koleksi}]}
    if pilih: q['select'] = {'fields': [{'fieldPath': '__name__'}]}
    return [x['document'] for x in rest('POST', FS + '/v1/' + DB + '/documents:runQuery', {'structuredQuery': q}, OWNER) if isinstance(x, dict) and 'document' in x]


def potret():
    """Isi server SEKARANG: {koleksi: {id: updateTime}} — dasar hitungan tulis/hapus per langkah."""
    return {k: {d['name'].rsplit('/', 1)[1]: d.get('updateTime', '') for d in jalankan_query(k)} for k in koleksi_ada()}


def potret_isi(koleksi):
    """Isi lengkap (dekode) koleksi-koleksi itu: {koleksi: {id: data}} — pembanding 'isi server kembali seperti sebelum ritual'."""
    return {k: {d['name'].rsplit('/', 1)[1]: {a: dari_nilai(b) for a, b in d.get('fields', {}).items()} for d in jalankan_query(k, pilih=False)} for k in koleksi}


def beda(a, b):
    """Dua potret → ({koleksi: n tulis}, {koleksi: n hapus}). Tulis = dokumen baru + dokumen yang jam ubahnya berganti."""
    tulis, hapus = {}, {}
    for k in sorted(set(a) | set(b)):
        A, B = a.get(k, {}), b.get(k, {})
        t = len(set(B) - set(A)) + sum(1 for i in set(A) & set(B) if A[i] != B[i]); h = len(set(A) - set(B))
        if t: tulis[k] = t
        if h: hapus[k] = h
    return tulis, hapus


ATURAN_REPO = open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()


def pasang_aturan(teks):
    r = rest('PUT', FS + '/emulator/v1/projects/%s:securityRules' % PROYEK, {'rules': {'files': [{'name': 'firestore.rules', 'content': teks}]}})
    galat = [x for x in (r.get('issues') or []) if isinstance(r, dict) and str(x.get('severity', '')).upper() == 'ERROR'] if isinstance(r, dict) else []
    if galat: raise RuntimeError('aturan emulator ditolak: %s' % json.dumps(galat)[:400])


def aturan_tolak(koleksi):
    """SALINAN firestore.rules repo dengan tulisan (create/update) ke satu koleksi ditolak server — memotong ritual di tengah seperti kuota habis /
    sinyal putus. Hanya di emulator, sementara; firestore.rules repo TIDAK diubah."""
    m = re.search(r'(\n    match /' + re.escape(koleksi) + r'/\{[a-zA-Z]+\} \{\n)', ATURAN_REPO)
    assert m, 'blok aturan ' + koleksi + ' tidak ketemu — perbarui gladi'
    return ATURAN_REPO[:m.end()] + '      allow create, update: if false;   // GLADI: penolakan sementara\n' + ATURAN_REPO[m.end():]


# koleksi yang diarsip tutup buku (beku.js tbDaftarKoleksi) — dibandingkan isinya sebelum ritual ↔ sesudah pembatalan
KOLEKSI_2026 = ['penjualan', 'batchMasuk', 'produksiKemasan', 'retur', 'karantina', 'pengeluaranHarian', 'pesanan', 'setoranKas', 'penyesuaianKemasan', 'amplopLaba', 'modalOwner',
                'utangPemasokMutasi', 'utangOwnerMutasi', 'tembusanStok', 'stokBahanKemasan', 'stokBahanLiteran', 'piutangMutasi', 'kasbonMutasi', 'penyesuaianStok', 'tutupHari', 'biayaBulanan']


def banding_isi(awal):
    kini = potret_isi(KOLEKSI_2026); arsip = len(jalankan_query('arsipTahun'))
    lebih = {k: len(set(kini.get(k, {})) - set(awal.get(k, {}))) for k in KOLEKSI_2026}; kurang = {k: len(set(awal.get(k, {})) - set(kini.get(k, {}))) for k in KOLEKSI_2026}
    ubah = {k: sum(1 for i in awal.get(k, {}) if i in kini.get(k, {}) and awal[k][i] != kini[k][i]) for k in KOLEKSI_2026}
    contoh = next(([k, i] for k in KOLEKSI_2026 for i in awal.get(k, {}) if i in kini.get(k, {}) and awal[k][i] != kini[k][i]), None)
    saring = lambda d: {k: v for k, v in d.items() if v}
    return {'sama': not saring(lebih) and not saring(kurang) and not saring(ubah), 'lebih': saring(lebih), 'kurang': saring(kurang), 'ubah': saring(ubah), 'contohUbah': contoh,
            'arsip': arsip, 'dokumen': sum(len(v) for v in kini.values())}


def cakupan_aturan():
    try: return rest('GET', FS + '/emulator/v1/projects/%s:ruleCoverage' % PROYEK, waktu=60)
    except Exception as e: return {'galat': str(e)[:300]}


# ============================== salinan /baru/ untuk uji ==============================
def jam_palsu(iso):
    """Jam halaman = iso lalu BERJALAN (bukan beku: SDK Firebase & penunggu skenario butuh waktu yang maju). Pola Date pengganti alat uji lain.
    Disisip SEBELUM meta CSP → tidak terkena CSP salinan."""
    return ("<script>(function(){var R=Date,g=new R(" + json.dumps(iso) + ").getTime()-R.now();"
            "function D(a,b,c,d,e,f,h){if(!(this instanceof D))return new R(R.now()+g).toString();if(arguments.length===0)return new R(R.now()+g);"
            "if(arguments.length===1)return new R(a);return new R(a,b,c===undefined?1:c,d||0,e||0,f||0,h||0);}"
            "D.prototype=R.prototype;D.now=function(){return R.now()+g;};D.UTC=R.UTC;D.parse=R.parse;window.Date=D;window.__jamGladi=" + json.dumps(iso) + ";})();</script>")


def csp_salinan(t):
    """connect-src salinan = connect-src situs + alamat emulator (Firestore & Auth) — direktif lain, hash script sebaris, sumber lain TETAP."""
    m = re.search(r'(<meta http-equiv="Content-Security-Policy" content="[^"]*?connect-src )([^;"]*)', t)
    assert m, 'meta CSP /baru/ tanpa connect-src — perbarui gladi'
    return t[:m.end(1)] + m.group(2) + ' http://%s http://%s' % (FS_HOST, AUTH_HOST) + t[m.end():]


def salinan_index(t, jam):
    assert t.count('<head>') == 1 and t.count('</body>') == 1 and '<script type="module" src="js/app.js"></script>' in t
    t = csp_salinan(t)
    return t.replace('<head>', '<head>' + jam_palsu(jam), 1).replace('</body>', '<script type="module" src="/_gladi/skenario.js"></script>\n</body>', 1)


def siapkan(jam, rusak=None):
    """Folder kerja: baru/ (salinan) — index.html (CSP salinan, jam palsu, skenario), firebase.js (Firestore lewat SDK penghitung), app.js (pegangan layar)."""
    d = tempfile.mkdtemp(prefix='gladi-'); shutil.copytree(os.path.join(AKAR, 'baru'), os.path.join(d, 'baru'))
    def ubah(rel, f):
        p = os.path.join(d, 'baru', rel); s = open(p, encoding='utf-8').read(); open(p, 'w', encoding='utf-8').write(f(s))
    ubah('index.html', lambda s: salinan_index(s, jam))
    def fb(s):
        assert s.count(SDK + 'firebase-firestore.js') == 1, 'impor Firestore di firebase.js berubah — perbarui gladi'
        return s.replace(SDK + 'firebase-firestore.js', '/_gladi/firebase-firestore.js')
    ubah('js/data/firebase.js', fb)
    ubah('js/app.js', lambda s: s + '\nwindow.__gladiLayar = { uang, jual: layar };   // gladi_tutup_buku: pegangan layar (salinan uji saja)\n')
    for rel, lama, baru in (rusak or []):
        def r(s, lama=lama, baru=baru):
            assert s.count(lama) == 1, 'kontrol basi: ' + rel + ' · ' + lama[:70]
            return s.replace(lama, baru, 1)
        ubah(rel, r)
    return d


# SDK Firestore ASLI + penghitung dokumen yang DITERIMA halaman dari server (pendengar & getDocs). Bukan pengganti: semua ekspor SDK diteruskan,
# hanya onSnapshot & getDocs dibungkus. Perkiraan baca Firestore: tiap dokumen yang masuk/berubah di hasil pendengar & tiap dokumen getDocs.
SDK_PENGHITUNG = r"""
export * from '__SDK__firebase-firestore.js';
import { onSnapshot as _onSnapshot, getDocs as _getDocs } from '__SDK__firebase-firestore.js';
const B = (window.__gladiBaca = window.__gladiBaca || { dokumen: 0, perKoleksi: {} });
const nama = (r) => { try { if (r && typeof r.path === 'string') return r.path.split('/')[0]; const q = r && r._query; return q && q.path && q.path.segments ? q.path.segments[0] : '?'; } catch (e) { return '?'; } };
const tambah = (k, n) => { if (!n) return; B.dokumen += n; B.perKoleksi[k] = (B.perKoleksi[k] || 0) + n; };
function hitung(k, snap) {
  if (!snap || !snap.metadata || snap.metadata.fromCache) return;
  if (typeof snap.docChanges === 'function') { let n = 0; snap.docChanges().forEach((c) => { if ((c.type === 'added' || c.type === 'modified') && !c.doc.metadata.hasPendingWrites) n += 1; }); tambah(k, n); }
  else if (typeof snap.exists === 'function' && snap.exists() && !snap.metadata.hasPendingWrites) tambah(k, 1);
}
export function onSnapshot(ref, ...args) {
  const k = nama(ref); const i = args.findIndex((a) => typeof a === 'function');
  if (i >= 0) { const asli = args[i]; args[i] = (snap) => { try { hitung(k, snap); } catch (e) { /* penghitung tidak boleh mengganggu */ } return asli(snap); }; }
  return _onSnapshot(ref, ...args);
}
export async function getDocs(q) { const s = await _getDocs(q); try { if (!s.metadata.fromCache) tambah(nama(q), s.size); } catch (e) { /* abaikan */ } return s; }
""".replace('__SDK__', SDK)

# Skenario di halaman. Langkah = fungsi bernama di LANGKAH; urutannya dari konfig (SKENARIO di Python). Tiap langkah melapor ke server uji (/_langkah)
# yang MENGUKUR isi emulator sebelum menjawab — halaman menunggu jawaban, jadi hitungan tulis/hapus jatuh ke langkah yang benar.
SKENARIO_JS = r"""
import * as fb from '/baru/js/data/firebase.js';
import * as toko from '/baru/js/data/toko.js';
import { KOLEKSI } from '/baru/js/data/koleksi.js';
import * as BK from '/baru/js/layar/tutup-buku-logika.js';
const K = await (await fetch('/_gladi/konfig.json', { cache: 'no-store' })).json();
const konsol = []; const errAsli = console.error;
console.error = function () { try { konsol.push(Array.from(arguments).map((x) => String(x && x.stack ? x.stack : x)).join(' ').slice(0, 400)); } catch (e) { /* abaikan */ } return errAsli.apply(console, arguments); };
window.addEventListener('error', (e) => konsol.push('error: ' + String(e.message || e).slice(0, 300)));
window.addEventListener('unhandledrejection', (e) => konsol.push('rejection: ' + String((e.reason && (e.reason.stack || e.reason.message)) || e.reason).slice(0, 400)));
const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));
async function sampai(f, ms, apa) { const t0 = performance.now(); while (performance.now() - t0 < ms) { try { const v = f(); if (v) return v; } catch (e) { /* belum */ } await tunggu(120); } throw new Error('tidak tercapai dalam ' + Math.round(ms / 1000) + ' dtk: ' + apa); }
let ST = {}; fb.dengarkanStatus((s) => { ST = s; });
const $ = (id) => document.getElementById(id);
const U = () => window.__gladiLayar.uang; const su = () => U().keadaan.baca();
const akarU = () => $('layarUang');
const ringkasKM = () => { const k = BK.kemajuanBuku(); return k ? { fase: k.fase, tahun: k.tahun, teks: k.teks, sudah: k.sudah || 0, total: k.total || 0 } : null; };
const acara = () => { const a = toko.ambilTutupBukuAcara().find((x) => Number(x.tahun) === 2026); return a ? { status: a.status, nPembuka: a.nPembuka, nArsip: a.nArsip, kiriman: a.rencana ? a.rencana.n : null } : null; };
function potret() {
  const s = su(); const A = akarU();
  const g = [...A.querySelectorAll('.tb-cek')].map((e) => ({ id: (e.dataset.k || '').replace(/^g-/, ''), ok: e.classList.contains('ok'), teks: (e.children[1] && e.children[1].children[0] ? e.children[1].children[0].textContent : ''), ket: (e.querySelector('.k') || {}).textContent || '' }));
  const tp = A.querySelector('[data-aksi="bkPeriksa"]'); const kartu = A.querySelector('[data-k="tb-lanjut"], [data-k="tb-selesaikan"]');
  return { modeB: s.modeB, langkahB: Object.assign({}, s.langkahB), kabar: s.kabar, kabarAwas: !!s.kabarAwas, selesaiLatihan: !!s.selesaiLatihan, sibuk: !!s.sibuk, bukaB: s.bukaB,
    gerbang: g, tombolPeriksa: tp ? { teks: tp.textContent.trim(), kelas: tp.className } : null, km: ringkasKM(), acara: acara(), era: BK.bkEra(),
    kartuLanjut: kartu ? { k: kartu.dataset.k, teks: kartu.textContent.trim().slice(0, 300), tombol: [...kartu.querySelectorAll('[data-aksi]')].map((e) => ({ aksi: e.dataset.aksi, teks: e.textContent.trim(), mati: e.classList.contains('mati') })) } : null,
    tombolBatal: !!A.querySelector('.kaca-btn[data-aksi="bkBatal"]'), antre: (ST.antre || []).length, menunggu: ST.menunggu || 0, lokal: ST.lokal || null, galatFb: ST.galat || '' };
}
const salinBaca = () => JSON.parse(JSON.stringify(window.__gladiBaca || { dokumen: 0, perKoleksi: {} }));
async function lapor(nama, info, minta) {
  const r = await fetch('/_langkah', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nama, info: info || {}, baca: salinBaca(), minta: minta || null }) });
  const j = await r.json(); if (!j.ok) throw new Error('server uji menolak langkah ' + nama + ': ' + j.pesan); return j;
}
async function ketuk(sel, apa, harap, ms) {
  const el = akarU().querySelector(sel);
  if (!el) throw new Error('tombol tidak ada: ' + apa + ' (' + sel + ') · yang ada: ' + [...new Set([...akarU().querySelectorAll('[data-aksi]')].map((e) => e.dataset.aksi))].join(','));
  el.click(); await tunggu(400);
  await sampai(() => !su().sibuk && (!harap || harap()), ms || 120000, apa);
  await tunggu(300);
}
const ketukLapor = async (nama, sel, harap, ms, minta) => { await ketuk(sel, nama, harap, ms); return lapor(nama, potret(), minta); };
const PERIKSA = '[data-aksi="bkPeriksa"]';
const L = {
  async masuk() {
    await sampai(() => ST.masuk || ($('formMasuk') && !$('formMasuk').hidden), 90000, 'formulir Masuk tampil');
    if (!ST.masuk) { $('isianEmail').value = K.email; $('isianSandi').value = K.sandi; $('tombolMasuk').click(); }
    await sampai(() => ST.masuk && ST.akun && ST.akun.jenis === 'owner', 90000, 'masuk sebagai owner contoh');
    await lapor('masuk', { akun: ST.akun.jenis, sumber: toko.sumberData(), bilah: (document.querySelector('.bilah-uji') || {}).textContent || '' });
  },
  async muatPenuh() {
    const t0 = performance.now();
    await sampai(() => ST.koleksiTotal > 0 && ST.koleksiSiap >= ST.koleksiTotal, 600000, 'semua koleksi termuat');
    try { await sampai(() => (window.__gladiBaca || {}).dokumen >= K.harapBaca, 180000, 'dokumen data contoh sampai di halaman'); } catch (e) { konsol.push('muat penuh: ' + e.message); }
    await tunggu(2500);
    const n = {}; KOLEKSI.forEach((k) => { n[k.nama] = toko.cacheMentah(k.cache).length; });
    await lapor('muat penuh', { detik: Math.round((performance.now() - t0) / 100) / 10, koleksiSiap: ST.koleksiSiap, koleksiTotal: ST.koleksiTotal, ditolak: ST.ditolak || [], galat: ST.galat || '', offline: !!ST.offline, cache: n });
  },
  async bukaTutupBuku() {
    document.querySelector('[data-tujuan="uang"]').click();
    await sampai(() => akarU().querySelector('[data-aksi="keluarga"][data-nama="buku"]'), 60000, 'layar Uang tampil');
    await ketuk('[data-aksi="keluarga"][data-nama="buku"]', 'keluarga Tutup buku', () => akarU().querySelector(PERIKSA));
    await lapor('buka Uang › Tutup buku', potret());
  },
  async latihan() {
    await ketukLapor('LATIHAN dipilih', '[data-aksi="bkMode"][data-m="latihan"]', () => su().modeB === 'latihan');
    await ketukLapor('1 periksa', PERIKSA, () => !!su().langkahB.periksa);
    await ketukLapor('2 cadangan sebelum', '[data-aksi="bkCadangan"][data-k-cad="cadangan1"]', () => !!su().langkahB.cadangan1);
    await ketukLapor('3 arsip', '[data-aksi="bkArsip"]', () => !!su().langkahB.arsip);
    await ketukLapor('4 saldo pembuka', '[data-aksi="bkSaldo"]', () => !!su().langkahB.saldo);
    await ketukLapor('5a pilih saksi', '[data-aksi="bkSaksi"][data-nama="' + K.saksi + '"]', () => su().saksiB === K.saksi);
    await ketukLapor('5b paraf owner', '[data-aksi="bkParaf"][data-siapa="owner"]', () => su().parafB.owner);
    await ketukLapor('5c paraf saksi', '[data-aksi="bkParaf"][data-siapa="saksi"]', () => !!su().langkahB.paraf);
    await ketukLapor('6a kunci (ketukan 1)', '[data-aksi="bkKunci"]', () => su().siapKunci || !!su().langkahB.kunci);
    await ketukLapor('6b kunci (ketukan 2)', '[data-aksi="bkKunci"]', () => !!su().langkahB.kunci);
    await ketukLapor('7 selesai latihan', '[data-aksi="bkSelesaiLatihan"]', () => su().selesaiLatihan);
  },
  async sungguhan() { await ketukLapor('SUNGGUHAN dipilih', '[data-aksi="bkMode"][data-m="sungguhan"]', () => su().modeB === 'sungguhan' || su().kabarAwas); },
  async gerbangDiblokir() { await ketukLapor('1 periksa (diblokir gerbang)', PERIKSA, () => su().kabarAwas || !!su().langkahB.periksa); },
  // ---- ritual SUNGGUHAN (data bersih). Paket A (gerbang tutup buku diubah) → sesuaikan sampaiParaf / gerbang di sini, bukan di Python.
  async sampaiParaf() {
    await ketukLapor('1 periksa (semua beres)', PERIKSA, () => !!su().langkahB.periksa || su().kabarAwas);
    await ketukLapor('2 cadangan sebelum (unduh)', '[data-aksi="bkCadangan"][data-k-cad="cadangan1"]', () => !!su().langkahB.cadangan1 || su().kabarAwas, 300000);
    await ketukLapor('3 arsip (unduh berkas)', '[data-aksi="bkArsip"]', () => !!su().langkahB.arsip || su().kabarAwas, 300000);
    await ketukLapor('4 saldo pembuka', '[data-aksi="bkSaldo"]', () => !!su().langkahB.saldo);
    await ketuk('[data-aksi="bkSaksi"][data-nama="' + K.saksi + '"]', 'pilih saksi', () => su().saksiB === K.saksi);
    await ketuk('[data-aksi="bkParaf"][data-siapa="owner"]', 'paraf owner', () => su().parafB.owner);
    await ketukLapor('5 paraf owner + saksi', '[data-aksi="bkParaf"][data-siapa="saksi"]', () => !!su().langkahB.paraf);
  },
  async kunciTerputusPembuka() {
    await lapor('server mulai menolak saldo pembuka bon pemasok', potret(), 'tolak:utangPemasokMutasi');
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → kiriman saldo pembuka ditolak server', '[data-aksi="bkKunci"]', () => !!ringkasKM() || su().kabarAwas, 1800000, 'pulihkan');
  },
  async batalkanSebelumPenanda() {
    await ketuk('[data-k="tb-lanjut"] [data-aksi="bkBatal"]', 'batalkan (ketukan 1)', () => su().yakinBatalB === 2026);
    await ketukLapor('BATALKAN sebelum penanda', '[data-k="tb-lanjut"] [data-aksi="bkBatal"]', () => { const a = acara(); return a && a.status === 'dibatalkan' && !ringkasKM(); }, 1800000);
  },
  async mulaiLagi() {
    await ketukLapor('mulai lagi: SUNGGUHAN', '[data-aksi="bkMode"][data-m="sungguhan"]', () => su().modeB === 'sungguhan' && !su().langkahB.periksa);
    await L.sampaiParaf();
  },
  async kunciTerputusArsip() {
    await lapor('server mulai menolak arsip', potret(), 'tolak:arsipTahun');
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → saldo pembuka masuk, arsip ditolak server', '[data-aksi="bkKunci"]', () => { const k = ringkasKM(); return (k && k.fase === 'arsip') || su().kabarAwas; }, 1800000, 'pulihkan');
  },
  async lanjutkan() { await ketukLapor('LANJUTKAN arsip', '[data-k="tb-lanjut"] [data-aksi="bkLanjut"]', () => !ringkasKM() || ringkasKM().fase === 'selesaikan', 3600000); },
  async batalkanSesudahPenanda() {
    const sel = '.kaca-btn[data-aksi="bkBatal"], [data-k="tb-selesaikan"] [data-aksi="bkBatal"]';
    await ketuk(sel, 'batalkan (ketukan 1)', () => su().yakinBatalB === 2026);
    await ketukLapor('BATALKAN sesudah penanda', sel, () => { const a = acara(); return a && a.status === 'dibatalkan' && !ringkasKM(); }, 3600000);
  },
  async kunciPenuh() {
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → saldo pembuka + arsip penuh', '[data-aksi="bkKunci"]', () => { const k = ringkasKM(); return (k && k.fase === 'selesaikan') || (acara() && acara().status === 'terkunci' && !k) || su().kabarAwas; }, 3600000);
  },
  async selesai() {
    const sel = '[data-k="tb-selesaikan"] [data-aksi="bkCadangan"], .utama[data-aksi="bkCadangan"][data-k-cad="cadangan2"]';
    await ketukLapor('7 cadangan sesudah · SELESAI', sel, () => { const a = acara(); return (a && a.status === 'selesai') || su().kabarAwas; }, 600000);
  },
};
let galat = '';
try { for (const nama of K.langkah) { if (!L[nama]) throw new Error('langkah tidak dikenal: ' + nama); await L[nama](); } }
catch (e) { galat = String((e && (e.stack || e.message)) || e).slice(0, 1500); }
let akhir = null; try { akhir = potret(); } catch (e) { akhir = { galat: String(e) }; }
await fetch('/_hasil', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ galat, konsol: konsol.slice(-40), akhir, baca: salinBaca() }) });
"""

# Skenario → (varian data, jam halaman, langkah)
SKENARIO = {
    'latihan': ('macet', DC.JAM_LATIHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'latihan']),
    'gerbang': ('macet', DC.JAM_SUNGGUHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'sungguhan', 'gerbangDiblokir']),
    'ritual': ('bersih', DC.JAM_SUNGGUHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'sungguhan', 'sampaiParaf', 'kunciTerputusPembuka', 'batalkanSebelumPenanda',
                                            'mulaiLagi', 'kunciTerputusArsip', 'lanjutkan', 'batalkanSesudahPenanda', 'mulaiLagi', 'kunciPenuh', 'selesai']),
}


# ============================== server uji ==============================
def _ikat_tanpa_dns(self):
    socketserver.TCPServer.server_bind(self); self.server_name, self.server_port = self.server_address[:2]


class Pelayan(http.server.SimpleHTTPRequestHandler):
    keadaan = None
    def log_message(self, *a): pass
    def kirim(self, kode, isi, jenis):
        b = isi.encode('utf-8') if isinstance(isi, str) else isi
        self.send_response(kode); self.send_header('Content-Type', jenis); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        K = self.keadaan; j = self.path.split('?')[0]
        if j == '/_gladi/skenario.js': return self.kirim(200, SKENARIO_JS, 'text/javascript')
        if j == '/_gladi/firebase-firestore.js': return self.kirim(200, SDK_PENGHITUNG, 'text/javascript')
        if j == '/_gladi/konfig.json': return self.kirim(200, json.dumps(K['konfig']), 'application/json')
        return super().do_GET()
    def do_POST(self):
        K = self.keadaan; n = int(self.headers.get('Content-Length') or 0); isi = json.loads(self.rfile.read(n).decode('utf-8') or '{}')
        if self.path.startswith('/_langkah'):
            try: jawab = K['ukur'](isi)
            except Exception as e: jawab = {'ok': False, 'pesan': str(e)[:400]}
            return self.kirim(200, json.dumps(jawab), 'application/json')
        if self.path.startswith('/_hasil'):
            K['hasil'] = isi; K['selesai'].set(); return self.kirim(200, '{"ok":true}', 'application/json')
        self.send_response(404); self.end_headers()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()
    def guess_type(self, path):
        return 'text/javascript' if str(path).endswith('.js') else super().guess_type(path)


def layani(d, keadaan):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    kelas = type('PelayanGladi', (Pelayan,), {'keadaan': keadaan})
    Srv = type('SrvGladi', (http.server.ThreadingHTTPServer,), {'request_queue_size': 256, 'daemon_threads': True, 'server_bind': _ikat_tanpa_dns})
    srv = Srv(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def jalankan_chrome(port, profil, batas, keadaan):
    """SATU Chrome headless; selesai = halaman mengirim /_hasil, atau batas waktu. Grup prosesnya dimatikan sesudahnya (CLAUDE.md)."""
    arg = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
           '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--user-data-dir=' + profil, '--window-size=1440,1000', '--hide-scrollbars',
           '--use-mock-keychain', '--password-store=basic']
    if sys.platform.startswith('linux'): arg.append('--no-sandbox')   # runner Ubuntu: sandbox userns dibatasi AppArmor; halaman = salinan lokal
    log = open(os.path.join(profil, '..', os.path.basename(profil) + '-chrome.log'), 'wb')
    url = 'http://127.0.0.1:%d/baru/index.html?emulator=%s' % (port, FS_HOST) + ('&emulatorAuth=' + AUTH_HOST if AUTH_HOST.split(':')[1] != '9099' else '')
    p = subprocess.Popen(arg + ['--enable-logging=stderr', url], stdout=subprocess.DEVNULL, stderr=log, start_new_session=True); log.close()
    t0 = time.time()
    try:
        while not keadaan['selesai'].is_set() and time.time() - t0 < batas and p.poll() is None: time.sleep(0.5)
        return keadaan['selesai'].is_set(), round(time.time() - t0, 1), p.poll()
    finally:
        try: os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError): p.kill()
        p.wait()


# ============================== satu skenario ==============================
def jalankan_skenario(nama, data, sandi, rusak=None, cetak=print, kait=None):
    varian, jam, langkah = SKENARIO[nama]
    meta = data['gladi']; d = siapkan(jam, rusak); profil = os.path.join(d, 'profil'); os.makedirs(profil)
    harap = sum(len(v) for k, v in data.items() if isinstance(v, list) and k != 'logAktivitas') + min(150, len(data.get('logAktivitas', [])))
    K = {'konfig': {'email': EMAIL_OWNER, 'sandi': sandi, 'langkah': langkah, 'saksi': meta['saksi'][0], 'harapBaca': harap},
         'selesai': threading.Event(), 'hasil': None, 'langkah': [], 'kunci': threading.Lock()}
    K['potret'] = potret(); K['baca'] = 0; K['t'] = time.time()
    def ukur(isi):
        with K['kunci']:
            p = potret(); tulis, hapus = beda(K['potret'], p); K['potret'] = p
            baca = int((isi.get('baca') or {}).get('dokumen') or 0); db = baca - K['baca']; K['baca'] = baca
            r = {'nama': isi.get('nama'), 'detik': round(time.time() - K['t'], 1), 'baca': db, 'bacaPer': (isi.get('baca') or {}).get('perKoleksi'), 'tulis': sum(tulis.values()),
                 'hapus': sum(hapus.values()), 'tulisPer': tulis, 'hapusPer': hapus, 'info': isi.get('info') or {}}
            if (kait or {}).get(r['nama']): r['kait'] = kait[r['nama']]()
            K['t'] = time.time(); K['langkah'].append(r)
            cetak('  · %-52s %6.1f dtk · baca %6d · tulis %6d · hapus %6d%s' % (r['nama'][:52], r['detik'], r['baca'], r['tulis'], r['hapus'],
                                                                             ('  [' + ', '.join('%s +%d' % x for x in sorted(tulis.items())) + ']') if tulis and r['tulis'] < 60 else ''))
            m = isi.get('minta') or ''
            if m.startswith('tolak:'): pasang_aturan(aturan_tolak(m.split(':', 1)[1])); r['aturan'] = 'firestore.rules repo + ' + m.split(':', 1)[1] + ' ditolak'; cetak('    (aturan emulator: %s DITOLAK sementara)' % m.split(':', 1)[1])
            elif m == 'pulihkan': pasang_aturan(ATURAN_REPO); r['aturan'] = 'firestore.rules repo (dipulihkan)'; cetak('    (aturan emulator: firestore.rules repo dipulihkan)')
            return {'ok': True}
    K['ukur'] = ukur
    srv, port = layani(d, K)
    try:
        ok, detik, kode = jalankan_chrome(port, profil, TUNGGU_SKENARIO[nama], K)
    finally:
        srv.shutdown(); pasang_aturan(ATURAN_REPO)
        log = os.path.join(d, 'profil-chrome.log'); ekor = open(log, 'rb').read().decode('utf-8', 'replace').splitlines()[-30:] if os.path.exists(log) else []
        shutil.rmtree(d, ignore_errors=True)
    H = K['hasil'] or {}
    return {'nama': nama, 'varian': varian, 'jamHalaman': jam, 'langkahDiminta': langkah, 'selesai': ok, 'detik': detik, 'kodeChrome': kode, 'langkah': K['langkah'],
            'galat': H.get('galat') if ok else 'halaman tidak mengirim hasil dalam %d dtk (Chrome %s)' % (TUNGGU_SKENARIO[nama], kode),
            'konsol': H.get('konsol') or [], 'akhir': H.get('akhir'), 'ekorChrome': [] if ok and not H.get('galat') else ekor}


# ============================== cek ==============================
def L_(S, nama):
    return next((x for x in S['langkah'] if x['nama'] == nama), None)


def cek_umum(S, data, c, tolak_sengaja=()):
    c.append(('skenario berjalan sampai akhir tanpa galat', S['selesai'] and not S['galat'], (S['galat'] or '')[:600]))
    m = L_(S, 'masuk')
    c.append(('masuk sebagai owner contoh di SERVER TIRUAN (bilah "SERVER TIRUAN" tampil, sumber Firestore)', bool(m) and m['info'].get('akun') == 'owner' and 'SERVER TIRUAN' in (m['info'].get('bilah') or ''),
              m and {k: m['info'].get(k) for k in ('akun', 'bilah')}))
    mp = L_(S, 'muat penuh')
    if not mp: c.append(('muat penuh', False, 'langkah tidak tercapai')); return
    I = mp['info']; kurang = {}
    for k, v in data.items():
        if not isinstance(v, list) or k not in I.get('cache', {}): continue
        harap = min(150, len(v)) if k == 'logAktivitas' else len(v)
        ada = I['cache'][k]
        if (ada < harap) or (k not in ('perangkatStatus', 'logAktivitas') and ada != harap): kurang[k] = (ada, harap)
    c.append(('muat penuh: semua koleksi siap, tak ada yang ditolak aturan, isi cache = data contoh per koleksi (%d dokumen)' % sum(len(v) for v in data.values() if isinstance(v, list)),
              I.get('koleksiSiap') == I.get('koleksiTotal') and not I.get('ditolak') and not I.get('galat') and not kurang, {'siap': [I.get('koleksiSiap'), I.get('koleksiTotal')], 'ditolak': I.get('ditolak'), 'galat': I.get('galat'), 'beda': kurang}))
    bocor = [x for x in S['konsol'] if ('permission' in x.lower() or 'FirebaseError' in x) and not any(k in x for k in tolak_sengaja)]
    c.append(('tidak ada galat izin / FirebaseError di konsol halaman' + (' (selain penolakan sengaja: ' + ', '.join(tolak_sengaja) + ')' if tolak_sengaja else ''), not bocor, bocor[:3]))


def tulisan_bukan_latar(langkah):
    t = {}
    for x in langkah:
        for k, n in x['tulisPer'].items():
            if k not in LATAR: t[k] = t.get(k, 0) + n
        for k, n in x['hapusPer'].items(): t['hapus:' + k] = t.get('hapus:' + k, 0) + n
    return t


def cek_latihan(S, data, c):
    cek_umum(S, data, c)
    i = next((n for n, x in enumerate(S['langkah']) if x['nama'] == 'LATIHAN dipilih'), None)
    sesudah = S['langkah'][i:] if i is not None else []
    akhir = L_(S, '7 selesai latihan')
    urut = ['periksa', 'cadangan1', 'arsip', 'saldo', 'paraf', 'kunci', 'cadangan2']
    c.append(('LATIHAN jalan sampai akhir: tujuh langkah beres, "Latihan selesai"', bool(akhir) and akhir['info'].get('selesaiLatihan') and all(akhir['info']['langkahB'].get(k) for k in urut)
              and (akhir['info'].get('kabar') or '').startswith('Latihan selesai'), akhir and {'langkahB': akhir['info'].get('langkahB'), 'kabar': akhir['info'].get('kabar')}))
    s6 = L_(S, '6b kunci (ketukan 2)')
    c.append(('LATIHAN: 12 baris sebelum = sesudah (kunci latihan tidak ditolak "ada baris yang tidak sama")', bool(s6) and s6['info'].get('kabar') == 'Latihan: tidak ada yang dikunci', s6 and s6['info'].get('kabar')))
    t = tulisan_bukan_latar(sesudah)
    c.append(('LATIHAN TANPA MENULIS: 0 tulis & 0 hapus ke server selama tujuh langkah (selain denyut perangkat & katalog kasir)', bool(sesudah) and not t, t))


def cek_gerbang(S, data, c):
    cek_umum(S, data, c)
    n = len(data['gladi']['hariTanpaTutup']); m = L_(S, 'SUNGGUHAN dipilih'); p = L_(S, '1 periksa (diblokir gerbang)')
    c.append(('1 Jan: mode SUNGGUHAN boleh dipilih (tahun 2026 sudah lewat)', bool(m) and m['info'].get('modeB') == 'sungguhan' and not m['info'].get('kabarAwas'), m and {'modeB': m['info'].get('modeB'), 'kabar': m['info'].get('kabar')}))
    G = (m or {}).get('info', {}).get('gerbang') or []
    g1 = next((g for g in G if g['id'] == 'g1'), None); lain = [g for g in G if g['id'] != 'g1' and not g['ok']]
    c.append(('gerbang g1 tampil MEMBLOKIR: "%d hari belum ditutup: …"; gerbang lain beres' % n, bool(g1) and not g1['ok'] and g1['ket'].startswith('%d hari belum ditutup' % n) and not lain and len(G) >= 5,
              {'g1': g1, 'lain belum': lain, 'n': len(G)}))
    tp = (m or {}).get('info', {}).get('tombolPeriksa') or {}
    c.append(('tombol periksa redup: "1 hal belum beres — bereskan dulu"', tp.get('teks') == '1 hal belum beres — bereskan dulu' and 'redup' in (tp.get('kelas') or ''), tp))
    c.append(('mengetuk periksa DITOLAK: langkah 1 tidak beres, kabar menyebut yang belum beres', bool(p) and not p['info']['langkahB'].get('periksa') and p['info'].get('kabarAwas')
              and p['info'].get('kabar') == '1 hal belum beres — bereskan dulu', p and {'langkahB': p['info'].get('langkahB'), 'kabar': p['info'].get('kabar')}))
    i = next((k for k, x in enumerate(S['langkah']) if x['nama'] == 'SUNGGUHAN dipilih'), None)
    t = tulisan_bukan_latar(S['langkah'][i:] if i is not None else [])
    c.append(('SUNGGUHAN yang diblokir tidak menulis apa pun ke server', i is not None and not t, t))


def cek_ritual(S, data, c):
    cek_umum(S, data, c, tolak_sengaja=('utangPemasokMutasi', 'arsipTahun', 'insufficient permissions'))
    p = L_(S, '6 kunci → kiriman saldo pembuka ditolak server')
    km = (p or {}).get('info', {}).get('km') or {}; kt = (p or {}).get('info', {}).get('kartuLanjut') or {}
    tombol = [t['aksi'] for t in kt.get('tombol', [])]
    c.append(('kiriman saldo pembuka ke-2 ditolak server → berhenti di tengah; kartu "lanjutkan / batalkan" TERSEDIA', bool(p) and km.get('fase') == 'pembuka' and 'bkLanjut' in tombol and 'bkBatal' in tombol
              and ((p or {}).get('info', {}).get('acara') or {}).get('status') == 'berjalan', {'km': km, 'tombol': tombol, 'acara': (p or {}).get('info', {}).get('acara')}))
    b1 = L_(S, 'BATALKAN sebelum penanda')
    c.append(('BATALKAN SEBELUM PENANDA: saldo pembuka yang sempat masuk ditarik, berita acara "dibatalkan", era tetap', bool(b1) and (b1['info'].get('acara') or {}).get('status') == 'dibatalkan'
              and b1['info'].get('era') is None and not b1['info'].get('km'), b1 and {k: b1['info'].get(k) for k in ('acara', 'era', 'km', 'kabar')}))
    a = L_(S, '6 kunci → saldo pembuka masuk, arsip ditolak server')
    kmA = (a or {}).get('info', {}).get('km') or {}; ktA = [t['aksi'] for t in ((a or {}).get('info', {}).get('kartuLanjut') or {}).get('tombol', [])]
    c.append(('arsip ditolak server di potongan pertama → kartu "lanjutkan / batalkan" TERSEDIA (fase arsip, berita acara terkunci)', bool(a) and kmA.get('fase') == 'arsip' and 'bkLanjut' in ktA and 'bkBatal' in ktA,
              {'km': kmA, 'tombol': ktA, 'acara': (a or {}).get('info', {}).get('acara')}))
    l = L_(S, 'LANJUTKAN arsip')
    n_arsip = (l or {}).get('tulisPer', {}).get('arsipTahun', 0)
    c.append(('LANJUTKAN: arsip habis dipindah ke arsipTahun, pita tinggal "selesaikan"', bool(l) and (l['info'].get('km') or {}).get('fase') in (None, 'selesaikan') and n_arsip > 0,
              l and {'km': l['info'].get('km'), 'arsipTahun ditulis': n_arsip, 'kabar': l['info'].get('kabar')}))
    b2 = L_(S, 'BATALKAN sesudah penanda')
    c.append(('BATALKAN SESUDAH PENANDA: arsip dikembalikan, saldo pembuka ditarik, berita acara "dibatalkan"', bool(b2) and (b2['info'].get('acara') or {}).get('status') == 'dibatalkan' and b2['hapus'] > 0,
              b2 and {'acara': b2['info'].get('acara'), 'hapus': b2['hapusPer'], 'tulis': b2['tulisPer']}))
    kb = (b2 or {}).get('kait') or {}
    c.append(('sesudah dua pembatalan isi server = sebelum ritual (dokumen & isinya, %d koleksi tahun 2026), arsipTahun kosong' % len(KOLEKSI_2026), bool(kb) and kb.get('sama') and kb.get('arsip') == 0, kb))
    s = L_(S, '7 cadangan sesudah · SELESAI')
    c.append(('ritual penuh SELESAI: berita acara "selesai", era 2026, tidak ada yang tertunda', bool(s) and (s['info'].get('acara') or {}).get('status') == 'selesai' and s['info'].get('era') == 2026 and not s['info'].get('km'),
              s and {k: s['info'].get(k) for k in ('acara', 'era', 'km', 'kabar')}))


CEK = {'latihan': cek_latihan, 'gerbang': cek_gerbang, 'ritual': cek_ritual}


# ============================== laporan ==============================
def ringkas_md(lap):
    out = ['## Gladi tutup buku — server tiruan (Firebase Emulator, aturan = `firestore.rules` repo, data contoh sintetis)', '',
           'Proyek emulator `%s` · firebase-tools %s · batas Spark per hari: baca %s · tulis %s · hapus %s' % (lap['proyek'], lap.get('firebaseTools', '?'), *[format(SPARK[k], ',').replace(',', '.') for k in ('baca', 'tulis', 'hapus')]), '']
    for v, m in lap['data'].items():
        out.append('- data **%s**: %s dokumen, %d hari tanpa tutup hari%s' % (v, format(m['dokumen'], ',').replace(',', '.'), len(m['hariTanpaTutup']), (' — ' + m['periksa']) if m.get('periksa') else ''))
    out.append('')
    for S in lap['skenario']:
        ok = all(x['ok'] for x in S['cek'])
        out += ['### %s %s — data %s, jam halaman %s (%s dtk)' % ('✅' if ok else '❌', S['nama'], S['varian'], S['jamHalaman'], S['detik']), '',
                '| langkah | dtk | baca | tulis | hapus | Σ baca / 50 rb | Σ tulis / 20 rb | Σ hapus / 20 rb |', '|---|---:|---:|---:|---:|---:|---:|---:|']
        sb = st = sh = 0
        for x in S['langkah']:
            sb += x['baca']; st += x['tulis']; sh += x['hapus']
            out.append('| %s%s | %s | %d | %d | %d | %.1f%% | %.1f%% | %.1f%% |' % (x['nama'], (' · _' + x['aturan'] + '_') if x.get('aturan') else '', x['detik'], x['baca'], x['tulis'], x['hapus'],
                                                                         100.0 * sb / SPARK['baca'], 100.0 * st / SPARK['tulis'], 100.0 * sh / SPARK['hapus']))
        out += ['', 'Cek:']
        for x in S['cek']: out.append('- %s %s%s' % ('✓' if x['ok'] else '✗', x['nama'], '' if x['ok'] else ' — `' + json.dumps(x['ket'], ensure_ascii=False)[:500].replace('`', "'") + '`'))
        if S.get('galat'): out += ['', '```', S['galat'][:1500], '```']
        if S.get('konsol') and not ok: out += ['', 'Konsol halaman (ekor):', '```', '\n'.join(S['konsol'][-15:])[:3000], '```']
        out.append('')
    out.append('Baca = dokumen yang DITERIMA pendengar halaman dari server (penghitung di salinan SDK uji; get() di aturan tidak termasuk). Tulis/hapus = beda isi '
               'emulator sebelum ↔ sesudah langkah (REST). Jam server emulator = jam runner, bukan jam halaman.')
    return '\n'.join(out)


def jalankan(daftar, sandi, rusak=None, cetak=print):
    lap = {'mulai': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'proyek': PROYEK, 'firebaseTools': os.environ.get('FIREBASE_TOOLS_VERSI', '?'),
           'spark': SPARK, 'data': {}, 'skenario': []}
    data_per = {}; varian_kini = None; awal_isi = None
    pasang_aturan(ATURAN_REPO)   # aturan emulator = teks firestore.rules repo, apa pun yang dimuat firebase.json
    for nama in daftar:
        varian = SKENARIO[nama][0]
        if varian not in data_per:
            data_per[varian] = DC.bangun(varian)
            h, cacat = DC.periksa(data_per[varian], varian) if DC.jalan_js('print("{}")')[0] is not None else (None, [])
            lap['data'][varian] = dict(data_per[varian]['gladi'], periksa=(DC.ringkas(h, data_per[varian]) if h and not cacat else ('; '.join(cacat) if cacat else 'tidak dinilai (tanpa jsc/node)')))
        data = data_per[varian]
        if varian != varian_kini or nama == 'ritual':
            cetak('— data %s: kosongkan emulator, isi %d dokumen, akun owner & karyawan contoh' % (varian, data['gladi']['dokumen']))
            kosongkan(); t0 = time.time(); n = isi_data(data)
            buat_akun(EMAIL_OWNER, sandi); uid_k = buat_akun(EMAIL_KARYAWAN, secrets.token_urlsafe(18))
            tulis_rest([('aksesAkun', uid_k, {'uid': uid_k, 'nama': 'Karyawan Contoh Gladi', 'email': EMAIL_KARYAWAN, 'peran': 'karyawan', 'aktif': True})])
            cetak('  %d dokumen masuk emulator dalam %.1f dtk' % (n, time.time() - t0)); varian_kini = varian
            if nama == 'ritual': awal_isi = potret_isi(KOLEKSI_2026)
        cetak('— skenario %s (jam halaman %s)' % (nama, SKENARIO[nama][1]))
        # ritual: tepat sesudah pembatalan kedua (sebelum mulai lagi), isi server dibandingkan dengan isi sebelum ritual — di dalam langkah itu, halaman menunggu
        kait = {'BATALKAN sesudah penanda': lambda: banding_isi(awal_isi)} if nama == 'ritual' else None
        S = jalankan_skenario(nama, data, sandi, rusak, cetak, kait)
        c = []
        CEK[nama](S, data, c)
        S['cek'] = [{'nama': a, 'ok': bool(b), 'ket': k} for a, b, k in c]
        for x in S['cek']: cetak('  %s %s%s' % ('✓' if x['ok'] else '✗', x['nama'], '' if x['ok'] else ' → ' + json.dumps(x['ket'], ensure_ascii=False)[:400]))
        if S['galat']: cetak('  GALAT: ' + S['galat'][:800])
        if S['konsol'] and any(not x['ok'] for x in S['cek']): cetak('  konsol: ' + ' | '.join(S['konsol'][-8:])[:1500])
        lap['skenario'].append(S)
    lap['cakupanAturan'] = cakupan_aturan()
    lap['lulus'] = all(x['ok'] for S in lap['skenario'] for x in S['cek'])
    return lap


# kontrol: SALINAN uji dirusak → cek yang dituju wajib gagal. (nama, skenario, rusak, cek yang wajib gagal)
KONTROL = [
    ('LATIHAN yang diam-diam menulis', 'latihan', [('js/layar/uang.js', "    bkSaldo: () => { const s = st(); if (!bkUrut(s, 'saldo')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); set(",
                                                     "    bkSaldo: () => { const s = st(); if (!bkUrut(s, 'saldo')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); tulisDokumen([{ koleksi: 'cadanganCatatan', data: { id: 'gladi-bocor', tanggal: '2026-12-31', jam: '21:50' } }]).catch(() => {}); set(")],
     'LATIHAN TANPA MENULIS'),
    ('gerbang g1 tidak memblokir', 'gerbang', [('js/layar/tutup-buku-logika.js', "ok: belumTutup.length === 0, ket:", "ok: true, ket:")], 'gerbang g1 tampil MEMBLOKIR'),
    ('salinan tidak memuat satu koleksi (muat penuh tidak lengkap)', 'latihan', [('js/data/koleksi.js', "  { nama: 'pengeluaranHarian',   urut: 'id',    cache: 'harian' },\n", '')],
     'muat penuh: semua koleksi siap'),
]


def periksa_salinan():
    """Statis (boleh di Mac): salinan uji disusun lalu diperiksa — tanpa Chrome, tanpa emulator."""
    import uji_csp
    c = []; d = siapkan(DC.JAM_SUNGGUHAN)
    try:
        asli = open(os.path.join(AKAR, 'baru/index.html'), encoding='utf-8').read(); s = open(os.path.join(d, 'baru/index.html'), encoding='utf-8').read()
        A, _ = uji_csp.csp_dari(asli); B, pos = uji_csp.csp_dari(s)
        tambah = [x for x in B.get('connect-src', []) if x not in A.get('connect-src', [])]
        c.append(('CSP salinan = CSP situs + http://<emulator Firestore> & http://<emulator Auth> di connect-src SAJA', {k: v for k, v in A.items() if k != 'connect-src'} == {k: v for k, v in B.items() if k != 'connect-src'}
                  and sorted(tambah) == sorted(['http://' + FS_HOST, 'http://' + AUTH_HOST]), tambah))
        c.append(('hash script sebaris situs tetap berlaku di salinan (script sebarisnya tidak diubah)', uji_csp.hash_sebaris(asli) == [h for h in uji_csp.hash_sebaris(s) if h in uji_csp.hash_sebaris(asli)]
                  and all(h in B.get('script-src', []) for h in uji_csp.hash_sebaris(asli)), ''))
        i_jam = s.find('window.__jamGladi'); c.append(('jam palsu disisip SEBELUM meta CSP (tidak terkena CSP salinan)', 0 <= i_jam < pos, (i_jam, pos)))
        c.append(('skenario dimuat dari situs sendiri (script-src \'self\'), sesudah app.js', s.find('<script type="module" src="js/app.js">') < s.find('<script type="module" src="/_gladi/skenario.js">'), ''))
        fbs = open(os.path.join(d, 'baru/js/data/firebase.js'), encoding='utf-8').read()
        c.append(('firebase.js salinan: Firestore lewat SDK penghitung (/_gladi/), app & auth tetap dari gstatic', "from '/_gladi/firebase-firestore.js'" in fbs and SDK + 'firebase-auth.js' in fbs and SDK + 'firebase-app.js' in fbs, ''))
        c.append(('SDK penghitung meneruskan SEMUA ekspor SDK asli (export *) dan hanya membungkus onSnapshot & getDocs', SDK_PENGHITUNG.count("export * from '" + SDK + "firebase-firestore.js'") == 1
                  and sorted(re.findall(r'export (?:async )?function (\w+)', SDK_PENGHITUNG)) == ['getDocs', 'onSnapshot'], ''))
        c.append(('berkas terbit TIDAK disentuh (salinan di folder sementara)', open(os.path.join(AKAR, 'baru/index.html'), encoding='utf-8').read() == asli, ''))
        for nama, (_, _, langkah) in SKENARIO.items():
            ada = set(re.findall(r'^  async (\w+)\(\)', SKENARIO_JS, re.M))
            c.append(('skenario %s: semua langkahnya ada di SKENARIO_JS' % nama, all(x in ada for x in langkah), [x for x in langkah if x not in ada]))
        c.append(('aturan penolak (gladi) = salinan firestore.rules + satu baris tolak, isi lain sama', aturan_tolak('arsipTahun').replace('      allow create, update: if false;   // GLADI: penolakan sementara\n', '') == ATURAN_REPO, ''))
    finally: shutil.rmtree(d, ignore_errors=True)
    return c


if __name__ == '__main__':
    arg = sys.argv[1:]
    def opsi(n, b):
        return arg[arg.index(n) + 1] if n in arg else b
    if '--periksa-salinan' in arg:
        c = periksa_salinan(); g = [x for x in c if not x[1]]
        for n, ok, k in c: print(('✓ ' if ok else '✗ ') + n + ('' if ok else ' → ' + str(k)[:300]))
        print('SALINAN UJI GLADI: %d lulus · %d gagal' % (len(c) - len(g), len(g))); sys.exit(2 if g else 0)
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        print('DITOLAK: gladi tutup buku menyalakan Chrome & emulator — HANYA di runner GitHub Actions (CLAUDE.md, keputusan owner 27 Sep 2026).\n'
              'Jalankan workflow "Gladi tutup buku" (Actions › Gladi tutup buku › Run workflow). Di Mac boleh: --periksa-salinan.')
        sys.exit(2)
    if not CHROME: print('Chrome tidak ditemukan di runner — GAGAL'); sys.exit(2)
    tunggu_emulator()
    sandi = secrets.token_urlsafe(24)   # sandi akun owner contoh: dibuat tiap run, hanya di emulator, tidak dicetak
    if '--kontrol' in arg:
        kode = 0
        for nama, sk, rusak, wajib in KONTROL:
            print('KONTROL · ' + nama, flush=True)
            lap = jalankan([sk], sandi, rusak, cetak=lambda *a: None)
            gagal = [x for S in lap['skenario'] for x in S['cek'] if not x['ok']]
            kena = [x for x in gagal if x['nama'].startswith(wajib)]
            print(('BERBUNYI ' if kena else 'DIAM!!   ') + nama + ' → ' + ((kena[0]['nama'] + ' · ' + json.dumps(kena[0]['ket'], ensure_ascii=False)[:160]) if kena else 'cek "' + wajib + '" tetap lulus'), flush=True)
            if not kena: kode = 3
        sys.exit(kode)
    daftar = [x.strip() for x in opsi('--skenario', os.environ.get('GLADI_SKENARIO') or 'latihan,gerbang,ritual').split(',') if x.strip()]
    salah = [x for x in daftar if x not in SKENARIO]
    if salah: print('skenario tidak dikenal: %s (ada: %s)' % (', '.join(salah), ', '.join(SKENARIO))); sys.exit(2)
    lap = jalankan(daftar, sandi)
    keluar = opsi('--keluar', ''); ring = opsi('--ringkasan', '')
    if keluar:
        os.makedirs(os.path.dirname(os.path.abspath(keluar)), exist_ok=True); json.dump(lap, open(keluar, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ringkas_md(lap)
    if ring: open(ring, 'w', encoding='utf-8').write(md)
    print('\n' + md)
    sys.exit(0 if lap['lulus'] else 2)
