#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_rules_emulator.py — BUKTI SERVER untuk rules v7 (PR #111, sebelum owner menerbitkannya): Firebase Emulator Firestore menilai rules dengan MESIN
RULES YANG SAMA dengan server produksi. Sampai 7 Okt, v7 hanya dinilai penafsir mini (alat-uji/rules_mini.py — "model bukan server"); di sini teks
firestore.rules cabang ini dipasang ke emulator dan tiap kasus dikirim lewat REST dengan TOKEN AKUN PALSU (JWT tak bertanda tangan — diterima emulator,
tidak pernah server sungguhan), jadi salah tulis yang tidak dimodelkan penafsir mini ikut ketahuan.

HANYA DI RUNNER GITHUB ACTIONS untuk bagian yang menyalakan emulator & node (CLAUDE.md, keputusan owner 27 Sep 2026: emulator & peramban tidak di Mac
owner) — workflow .github/workflows/uji-rules-emulator.yml. Di Mac boleh: --periksa / --kontrol (statis + model + jsc, tanpa emulator).

A · KASUS RULES — semua kasus docs/uji-rules-v7.md (18 "Wajib owner" + semua opsional ★A/B/N/F/K/R/P/T) + kasus model M-* (periksa_rules.KASUS_V7 —
    dokumen uji U1–U11 yang SAMA, tabel "Dokumen uji") + kasus S-* yang hanya bisa di server (cap = jam server lewat transform REQUEST_TIME, yang tidak
    bisa diketik di Playground). Tiap kasus: emulator dikosongkan, dokumen uji diisi lewat jalur admin (Bearer owner — emulator melewati rules), lalu
    SATU operasi dengan token akun "Isian Playground" (owner@ uid-uji, kasir@ uid-kasir-uji, staf uid-uji-b, akun tanpa aksesAkun baru1). LOLOS/DITOLAK
    wajib = kolom "Wajib" (★: dibaca dari tabel docs; M/S: kolom model). Tanggal "hari ini" & jam relatif (besok, 5 hari lagi, cap 1 jam lalu) digeser ke
    jam runner; cap = jam server (JAM_UJI_V7) dikirim sebagai transform REQUEST_TIME. Tahun di dokumen uji (2025 = tahun lalu) disusun untuk Okt–Des
    2026: di tahun lain semua kasus dilaporkan TIDAK TERUKUR (bukan dilewati diam) dan alat ini gagal.
    v6: kasus yang sama dijalankan atas firestore.rules.v6 — yang berbeda WAJIB persis BEDA_V6 (lima ubahan v6 → v7 di docs; bukti ubahan itulah yang
    membuat beda), selebihnya sama dengan v7.
    KONTROL: rules v7 dirusak satu suku (pintuSah selalu benar, ulangKasirBercap tanpa syarat capServer, salinan arsip tanpa pembanding isi, …) → kasus
    sasarannya WAJIB berbalik dari kolom Wajib (LOLOS ↔ DITOLAK, bukan galat). Kasus yang sama lulus dengan rules utuh → sebabnya suku itu.
C · KASIR DARURAT — KODE ASLI kasir-darurat-nominal.html (kasir_emulator.js: skrip sebaris halaman di node, DOM tiruan, fetch ke emulator): kasir-v33
    (berkas cabang ini) nota baru :commit + capServer REQUEST_TIME → masuk; kirim ulang identik (jawaban hilang) → :commit DITERIMA (ulangKasirBercap), cap
    jam server baru; kirim ulang yang mengubah isi → :commit & cara lama ditolak, server tidak berubah. kasir-v32 (KASIR_V32_COMMIT) kirim ulang identik
    atas nota bercap → PATCH utuh diterima (capServer terbuang), yang mengubah isi → ditolak. Di v6: kirim ulang v33 jatuh ke cara lama (PATCH updateMask)
    dan tetap masuk tanpa dobel; v32 atas nota bercap DITOLAK (sebab v7 perlu). Kontrol: suku (kasir() && ulangKasirBercap()) dicabut → berbunyi.

    python3 alat-uji/uji_rules_emulator.py --periksa    → statis + model (+ jsc / node: kode kasir dengan server palsu) — boleh di Mac
    python3 alat-uji/uji_rules_emulator.py --kontrol    → kerusakan pada pemeriksa statis wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_rules_emulator.py --emulator --keluar hasil.json --ringkasan ringkasan.md   → di runner, di dalam `firebase emulators:exec`
"""
import os, re, sys, json, time, base64, shutil, datetime, tempfile, subprocess, urllib.request, urllib.error, urllib.parse
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import periksa_rules as P   # noqa: E402  — kasus & dokumen uji v7 yang SAMA dengan model CI (KASUS_V7, DB_UJI_V7, AKUN_UJI, WAJIB_V7)
import rules_mini as RM     # noqa: E402

PROYEK = 'demo-uji-rules'                       # proyek emulator "demo-": tanpa kredensial, Firebase tidak pernah menyambungkannya ke server sungguhan
PROYEK_HALAMAN = 'toko-beras-m-iqbal'           # proyek yang ditulis kasir darurat — kasir_emulator.js menulis ulang alamatnya ke emulator
KASIR_V32_COMMIT = 'b973f7f71585048c6b4d698d769fa0db42bfba62'   # main 6 Okt 2026: kasir-darurat-nominal.html terakhir ber-VERSI kasir-v32 (HP penjaga sebelum cabang ini)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
WIB = datetime.timezone(datetime.timedelta(hours=7))
DOK = 'docs/uji-rules-v7.md'
FS_HOST = (os.environ.get('FIRESTORE_EMULATOR_HOST') or '127.0.0.1:8080').replace('localhost', '127.0.0.1')
FS = 'http://' + FS_HOST
DB = 'projects/%s/databases/(default)' % PROYEK
ADMIN = {'Authorization': 'Bearer owner'}       # emulator: melewati rules — hanya pengisi dokumen uji & pembaca isi server, tidak pernah operasi kasus
TS, JAM = RM.Ts, P.JAM_UJI_V7
SERVER = 'REQUEST_TIME'                          # penanda nilai: capServer = jam server permintaan itu (transform)

# ---- kasus S-*: hanya bisa di server — cap = jam server (request.time) tidak bisa diketik di Playground. Model menilainya juga (cap = JAM_UJI_V7).
NOTA, BERCAP = P.NOTA, P.BERCAP
KASUS_SERVER = [
    ('S-A1', 'kasir@ nota baru kasir-v33: capServer = jam server (REQUEST_TIME)', 'kasir', 'create', 'penjualan', 'uji-v7-s1', dict(NOTA, id='uji-v7-s1', capServer=JAM), None, True, 0),
    ('S-A2', 'kasir@ kirim ulang identik + capServer jam server (ulangKasirBercap)', 'kasir', 'update', 'penjualan', 'uji-v7-nota', dict(NOTA, capServer=JAM), None, True, 0),
    ('S-A3', 'kasir@ kirim ulang atas nota bercap: cap lama diganti jam server', 'kasir', 'update', 'penjualan', 'uji-v7-bercap', dict(NOTA, id='uji-v7-bercap', capServer=JAM), BERCAP, True, 0),
    ('S-B1', 'owner batu nisan bercap jam server', 'owner', 'create', 'batuNisan', 'uji-v7', {'id': 'penjualan|x', 'koleksi': 'penjualan', 'idDok': 'x', 'capServer': JAM}, None, True, 0),
    ('S-B2', 'owner batu nisan TANPA capServer', 'owner', 'create', 'batuNisan', 'uji-v7', {'id': 'penjualan|x', 'koleksi': 'penjualan', 'idDok': 'x'}, None, False, None),
]
KASUS = P.KASUS_V7 + KASUS_SERVER

# ---- v6 → v7: kasus yang WAJIB berbeda (nomor ubahan di docs/uji-rules-v7.md "Yang berubah v6 → v7"); semua kasus lain WAJIB sama di v6
BEDA_V6 = dict([(k, 1) for k in ('★A3', '★A4', 'M-A5', 'S-A2', 'S-A3', 'S-B1')] + [(k, 2) for k in ('★N1', '★N2')] + [(k, 3) for k in ('★F1', '★F2', '★F3')]
               + [(k, 4) for k in ('★K3', '★K4', '★K5', '★K6')]
               + [(k, 5) for k in ('★P1', '★P22', 'M-P26b', 'M-P26c', 'M-P26d', '★P2', 'M-P3', '★P4', '★P5', '★P26', '★P16', '★P17', '★P18', '★P24', 'M-P24b', 'M-P24c',
                                   'M-P27', '★T2', '★T3', '★T4', '★T5', 'M-T8', 'M-T9')])
UBAHAN = {1: 'hemat baca (kirim ulang kasir@ bercap, batu nisan)', 2: 'permintaan nego staf', 3: 'foto bon', 4: 'kasir@ dipangkas', 5: 'pintu tutup buku'}

# ---- KONTROL: rules v7 dirusak SATU suku → kasus sasarannya wajib berbalik (dinilai juga oleh model di --periksa)
KONTROL = [
    ('pintuSah selalu benar (pintu dibuka tanpa syarat)', [("      return d.get('status', '') == 'berjalan' && y is int && y == wib().year() - 1\n",
                                                             "      return true || d.get('status', '') == 'berjalan' && y is int && y == wib().year() - 1\n")],
     ['★P16', '★P17', '★P18', '★P24', 'M-P24b', 'M-P24c', 'M-P27']),
    ('ulangKasirBercap tanpa syarat capServer (cap jam HP diterima)', [("\n        && (!request.resource.data.keys().hasAny(['capServer']) || request.resource.data.capServer == request.time);", ";")], ['★B2']),
    ('salinan arsip tanpa pembanding isi', [("\n        && isi.diff(a.data.get('dok', {})).affectedKeys().hasOnly(['capServer']);", ";")], ['★P20', '★P13']),
    ('pintu tanpa batas waktu (sampai tidak dinilai)', [("\n        && request.time < p.data.sampai ? int(p.data.tahun) : 0;", " ? int(p.data.tahun) : 0;")], ['★P19']),
    ('berita acara baru tanpa pemeriksa jam mulai', [("\n        && p[0:10] in [hariUtc(request.time - duration.value(1, 'd')), hariUtc(request.time), hariUtc(request.time + duration.value(1, 'd'))];", ";")], ['★T2']),
    ('berita acara selesai walau pintu terbuka', [("      return !(b.get('status', '') in ['selesai', 'dibatalkan']) || pintuMati(", "      return true || pintuMati(")], ['★T3']),
    ('kasir@ boleh lagi membuat piutangMutasi (jalur kasir.html)', [("      allow create: if (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi',",
                                                                      "      allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi',")], ['★K3']),
    ('foto bon jenis apa saja', [("        && request.resource.data.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp']\n", "\n")], ['★F5']),
    ('permintaan nego atas nama orang lain', [(" && d.get('negoUid', '') == request.auth.uid", "")], ['★N4']),
    ('batu nisan tanpa cap jam server', [("      allow create, update: if owner() && request.resource.data.capServer == request.time;", "      allow create, update: if owner();")], ['★B6', 'S-B2']),
    ('saldo pembuka di koleksi mana pun', [("      return kol in ['batchMasuk', 'piutangMutasi',", "      return true || kol in ['batchMasuk', 'piutangMutasi',")], ['★P23']),
    ('salinan arsip tidak diikat ke catatan aslinya', [(" || salinanAsli(d))));", " || true)));")], ['★P22']),
    ('staf membaca batu nisan', [("    match /batuNisan/{id} {\n      allow read: if owner();", "    match /batuNisan/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);")], ['★B4']),
]
# kontrol bagian C: suku kirim ulang bercap dicabut dari update penjualan → kirim ulang kasir-v33 & kasir-v32 atas nota bercap wajib berbunyi
KONTROL_KASIR = ('suku (kasir() && ulangKasirBercap()) dicabut dari update penjualan', [(" || (kasir() && ulangKasirBercap());", ";")], ['c2', 'c4'])


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


def rusak(teks, ganti):
    for lama, baru in ganti:
        if teks.count(lama) != 1: raise ValueError('KONTROL BASI — jangkar tidak tepat 1× di rules: ' + lama.strip()[:90])
        teks = teks.replace(lama, baru, 1)
    return teks


# ============================== kolom "Wajib" docs/uji-rules-v7.md ==============================
def wajib_dok(teks=None):
    """{'★X': True (LOLOS) / False (DITOLAK)} dari tiap baris tabel ★ (Wajib owner & opsional). Sel bergaris tegak ber-escape (\\|) tidak dipotong."""
    out = {}
    for baris in (teks if teks is not None else baca(DOK)).split('\n'):
        m = re.match(r'^\|(?: \d+ \|)? (★[A-Z]\d+) \|', baris)
        if not m: continue
        sel = [x.strip() for x in re.split(r'(?<!\\)\|', baris)[1:-1]]
        w = [x for x in sel if x in ('LOLOS', 'DITOLAK')]
        out[m.group(1)] = (w[0] == 'LOLOS') if len(w) == 1 else None
    return out


# ============================== geser waktu ke jam runner ==============================
class Jam:
    """Jam runner (= jam emulator, mesin yang sama): hari ini & kemarin WIB, tahun WIB."""
    def __init__(self, ms=None):
        self.ms = int(ms if ms is not None else time.time() * 1000)
        d = datetime.datetime.fromtimestamp(self.ms / 1000.0, WIB)
        self.hari_ini = d.date().isoformat(); self.kemarin = (d.date() - datetime.timedelta(days=1)).isoformat(); self.tahun = d.year
        self.iso = datetime.datetime.fromtimestamp(self.ms / 1000.0, datetime.timezone.utc).isoformat()


def geser(v, J):
    """Nilai kasus model (jam uji 9 Okt 2026 03.00Z) → nilai di jam runner. Cap = jam uji persis → SERVER (transform REQUEST_TIME); jam relatif (besok,
    5 hari lagi, 1 jam lalu, 1 menit lalu) → relatif ke jam runner; jam mutlak (2020, 2100) tetap; "hari ini" & titik kas kemarin → tanggal WIB runner."""
    if isinstance(v, TS):
        if v.ms == JAM.ms: return SERVER
        d = v.ms - JAM.ms
        return TS(J.ms + d) if abs(d) <= 10 * 86400000 else v
    if isinstance(v, dict): return {k: geser(x, J) for k, x in v.items()}
    if isinstance(v, list): return [geser(x, J) for x in v]
    if isinstance(v, str):
        if v == P.HARI_INI: return J.hari_ini
        if v.startswith(P.HARI_INI + 'T'): return J.hari_ini + v[len(P.HARI_INI):]
        if v == P.DB_UJI_V7['pengaturan/titikKas']['tanggal']: return J.kemarin
    return v


# ============================== REST emulator ==============================
def ke_nilai(v):
    if v is None: return {'nullValue': None}
    if isinstance(v, bool): return {'booleanValue': v}
    if isinstance(v, int): return {'integerValue': str(v)}
    if isinstance(v, float): return {'doubleValue': v}
    if isinstance(v, str): return {'stringValue': v}
    if isinstance(v, TS): return {'timestampValue': datetime.datetime.fromtimestamp(v.ms / 1000.0, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + '%03dZ' % (v.ms % 1000)}
    if isinstance(v, list): return {'arrayValue': {'values': [ke_nilai(x) for x in v]}}
    if isinstance(v, dict): return {'mapValue': {'fields': {k: ke_nilai(x) for k, x in v.items()}}}
    raise TypeError('nilai tidak dikenal: %r' % (v,))


def ke_kolom(d):
    """isi → (fields, [kolom transform REQUEST_TIME]). SERVER hanya boleh di tingkat atas (capServer)."""
    f, t = {}, []
    for k, v in d.items():
        if v == SERVER: t.append(k)
        else: f[k] = ke_nilai(v)
    return f, t


def dari_nilai(n):
    if 'nullValue' in n: return None
    if 'booleanValue' in n: return n['booleanValue']
    if 'integerValue' in n: return int(n['integerValue'])
    if 'doubleValue' in n: return float(n['doubleValue'])
    if 'stringValue' in n: return n['stringValue']
    if 'timestampValue' in n: return {'__ts': n['timestampValue']}
    if 'arrayValue' in n: return [dari_nilai(x) for x in n['arrayValue'].get('values', [])]
    if 'mapValue' in n: return {k: dari_nilai(x) for k, x in n['mapValue'].get('fields', {}).items()}
    return n


def rest(metode, url, data=None, kepala=None, waktu=60):
    """→ (kode HTTP, isi JSON atau teks). HTTPError TIDAK dilempar — kode 403 adalah hasil kasus."""
    body = None if data is None else json.dumps(data).encode('utf-8')
    h = {'Content-Type': 'application/json'}; h.update(kepala or {})
    req = urllib.request.Request(url, data=body, method=metode, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=waktu) as r: kode, t = r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: kode, t = e.code, e.read().decode('utf-8', 'replace')
    try: isi = json.loads(t) if t.strip()[:1] in ('{', '[') else t
    except ValueError: isi = t
    return kode, isi


def wajib_ok(kode, isi, apa):
    if not 200 <= kode < 300: raise RuntimeError('%s → HTTP %s: %s' % (apa, kode, json.dumps(isi)[:400] if not isinstance(isi, str) else isi[:400]))
    return isi


def tunggu_emulator(batas=180):
    t0 = time.time(); g = ''
    while time.time() - t0 < batas:
        try:
            kode, _ = rest('GET', FS + '/', waktu=5)
            if kode < 500: return
        except Exception as e: g = str(e)
        time.sleep(1)
    raise RuntimeError('emulator tidak menjawab dalam %d dtk: %s' % (batas, g))


def pasang_aturan(teks):
    kode, isi = rest('PUT', FS + '/emulator/v1/projects/%s:securityRules' % PROYEK, {'rules': {'files': [{'name': 'firestore.rules', 'content': teks}]}})
    wajib_ok(kode, isi, 'pasang rules')
    galat = [x for x in ((isi or {}).get('issues') or []) if str(x.get('severity', '')).upper() == 'ERROR'] if isinstance(isi, dict) else []
    if galat: raise RuntimeError('rules ditolak emulator: %s' % json.dumps(galat)[:600])


def kosongkan():
    wajib_ok(*rest('DELETE', FS + '/emulator/v1/projects/%s/databases/(default)/documents' % PROYEK), apa='kosongkan emulator')


def nama_dok(jalur): return DB + '/documents/' + jalur


def isi_admin(db):
    """dokumen uji lewat jalur admin (Bearer owner — rules tidak menilai), satu commit."""
    if not db: return
    w = []
    for jalur, d in db.items():
        f, t = ke_kolom(d)
        if t: raise ValueError('dokumen uji %s memakai cap jam server — tidak bisa lewat admin' % jalur)
        w.append({'update': {'name': nama_dok(jalur), 'fields': f}})
    wajib_ok(*rest('POST', FS + '/v1/' + DB + '/documents:commit', {'writes': w}, ADMIN), apa='isi dokumen uji')


def ambil_admin(jalur):
    kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + '/'.join(urllib.parse.quote(x, safe='') for x in jalur.split('/')), kepala=ADMIN)
    if kode == 404: return None
    wajib_ok(kode, isi, 'baca ' + jalur)
    return {k: dari_nilai(v) for k, v in (isi.get('fields') or {}).items()}


def token(akun):
    """id token emulator: JWT alg none (tanpa tanda tangan) — uid & email persis tabel "Isian Playground". Hanya emulator yang menerimanya."""
    kini = int(time.time())
    b = lambda o: base64.urlsafe_b64encode(json.dumps(o, separators=(',', ':')).encode('utf-8')).rstrip(b'=').decode('ascii')
    muatan = {'iss': 'https://securetoken.google.com/' + PROYEK, 'aud': PROYEK, 'iat': kini - 60, 'auth_time': kini - 60, 'exp': kini + 3600,
              'sub': akun['uid'], 'user_id': akun['uid'], 'email': akun['email'], 'email_verified': True,
              'firebase': {'sign_in_provider': 'password', 'identities': {'email': [akun['email']]}}}
    return b({'alg': 'none', 'typ': 'JWT'}) + '.' + b(muatan) + '.'


def operasi(op, kol, id_, data, akun):
    """SATU operasi kasus dengan token akun → ('LOLOS' | 'DITOLAK' | 'GALAT', keterangan)."""
    k = {'Authorization': 'Bearer ' + token(akun)}
    komit = FS + '/v1/' + DB + '/documents:commit'
    if op in ('create', 'update'):
        f, t = ke_kolom(data)
        w = {'update': {'name': nama_dok(kol + '/' + id_), 'fields': f}, 'currentDocument': {'exists': op == 'update'}}
        if t: w['updateTransforms'] = [{'fieldPath': x, 'setToServerValue': 'REQUEST_TIME'} for x in t]
        kode, isi = rest('POST', komit, {'writes': [w]}, k)
    elif op == 'delete': kode, isi = rest('POST', komit, {'writes': [{'delete': nama_dok(kol + '/' + id_)}]}, k)
    elif op == 'get': kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + kol + '/' + urllib.parse.quote(id_, safe=''), kepala=k)
    elif op == 'list': kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + kol + '?pageSize=5', kepala=k)
    else: raise ValueError(op)
    ket = '' if 200 <= kode < 300 else ('HTTP %d %s' % (kode, (isi.get('error') or {}).get('status', '') if isinstance(isi, dict) else str(isi)[:80]))
    if 200 <= kode < 300 or (kode == 404 and op == 'get'): return 'LOLOS', ket or ('dokumen tidak ada (izin baca lolos)' if kode == 404 else '')
    if kode == 403 and 'PERMISSION_DENIED' in json.dumps(isi): return 'DITOLAK', ket
    return 'GALAT', ket + ' ' + json.dumps(isi)[:300]


# ============================== bagian A: kasus ==============================
def db_kasus(K, J):
    no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
    db = dict(P.DB_UJI_V7); db.update(ubah_db or {})
    db = {k: geser(v, J) for k, v in db.items() if v is not None}
    if op == 'create': db.pop(kol + '/' + id_, None)   # create = dokumen belum ada (Playground: isian apa adanya)
    return db


def jalankan_kasus(K, J, wajib):
    no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
    harap = wajib.get(no, boleh)
    r = {'no': no, 'nama': nama, 'akun': aud, 'op': op, 'jalur': kol + '/' + id_, 'wajib': 'LOLOS' if harap else 'DITOLAK'}
    if J.tahun != 2026:
        r.update(hasil='TIDAK TERUKUR', ket='dokumen uji docs/uji-rules-v7.md disusun untuk Okt–Des 2026 (2025 = tahun lalu); jam runner tahun %d' % J.tahun, ok=False)
        return r
    try:
        kosongkan(); isi_admin(db_kasus(K, J))
        h, ket = operasi(op, kol, id_, geser(data, J) if data is not None else None, P.AKUN_UJI[aud])
    except Exception as e: h, ket = 'GALAT', 'alat uji: ' + str(e)[:300]
    r.update(hasil=h, ket=ket, ok=(h == r['wajib']))
    return r


def jalankan_semua(J, teks_rules, kasus=None):
    pasang_aturan(teks_rules); w = wajib_dok()
    return [jalankan_kasus(K, J, w) for K in (kasus or KASUS)]


# ============================== bagian C: kasir darurat (kode asli, node) ==============================
def skrip_halaman(html):
    """skrip sebaris kasir darurat (yang memuat kirimAntrean) — satu-satunya <script> tanpa atribut yang berisi mesin kirim."""
    xs = [s for s in re.findall(r'<script>(.*?)</script>', html, re.S) if 'function kirimAntrean' in s]
    if len(xs) != 1: raise ValueError('skrip kirimAntrean di kasir darurat: %d (harus 1)' % len(xs))
    return xs[0]


def html_v32():
    """kasir-darurat-nominal.html di KASIR_V32_COMMIT (riwayat git penuh) → teks, atau None bila commit tidak terbaca (riwayat dangkal)."""
    try: t = subprocess.run(['git', 'show', KASIR_V32_COMMIT + ':kasir-darurat-nominal.html'], cwd=AKAR, capture_output=True, text=True, timeout=60)
    except Exception: return None
    return t.stdout if t.returncode == 0 and t.stdout else None


def node_kasir(skrip, simpanan, aksi=None):
    """kasir_emulator.js di node (runner) → hasil {permintaan, antrean, ditolak, simpanan, antreanSesudahCatat, …}."""
    d = tempfile.mkdtemp(prefix='kasir-emulator-')
    try:
        ps = os.path.join(d, 'skrip.js'); open(ps, 'w', encoding='utf-8').write(skrip)
        pm = os.path.join(d, 'minta.json')
        json.dump({'skrip': ps, 'simpanan': simpanan, 'aksi': aksi, 'emulator': FS_HOST, 'proyekHalaman': PROYEK_HALAMAN, 'proyekEmulator': PROYEK}, open(pm, 'w', encoding='utf-8'))
        r = subprocess.run(['node', os.path.join(SINI, 'kasir_emulator.js'), pm], capture_output=True, text=True, timeout=180, env=dict(os.environ, TZ='Asia/Jakarta'))
        baris = [x for x in r.stdout.strip().split('\n') if x.startswith('{')]
        if not baris: return {'galat': 'node tanpa hasil: ' + (r.stderr or r.stdout)[-800:]}
        return json.loads(baris[-1])
    finally: shutil.rmtree(d, ignore_errors=True)


def tulisan_nota(h):
    """permintaan tulis ke penjualan dari satu jalan halaman → [{'cara': 'commit'|'patch'|'patch-mask', 'status', 'cap': transform REQUEST_TIME, 'mask'}]."""
    out = []
    for x in h.get('permintaan') or []:
        u = x.get('url', '')
        if ':commit' in u:
            try: w = json.loads(x.get('badan') or '{}')['writes'][0]
            except Exception: w = {}
            if '/documents/penjualan/' not in (w.get('update') or {}).get('name', ''): continue
            out.append({'cara': 'commit', 'status': x.get('status'), 'cap': [t.get('fieldPath') + '=' + str(t.get('setToServerValue')) for t in w.get('updateTransforms') or []],
                        'mask': bool(w.get('updateMask')), 'kunci': x.get('kunci')})
        elif x.get('metode') == 'PATCH' and '/documents/penjualan/' in u:
            out.append({'cara': 'patch-mask' if 'updateMask.fieldPaths=' in u else 'patch', 'status': x.get('status'), 'cap': [], 'mask': 'updateMask.fieldPaths=' in u, 'kunci': x.get('kunci')})
    return out


def simpanan_awal():
    kasir = P.AKUN_UJI['kasir']
    return {'kasir_auth_v1': json.dumps({'refreshToken': 'uji-emulator', 'idToken': token(kasir), 'kedaluwarsa': int(time.time() * 1000) + 3000 * 1000})}


def dengan_antrean(simpanan, item):
    s = dict(simpanan); s['darurat_antrean_v1'] = json.dumps([item]); return s


def tanpa_cap(d): return {k: v for k, v in (d or {}).items() if k != 'capServer'}


def cap(d): return ((d or {}).get('capServer') or {}).get('__ts') if isinstance((d or {}).get('capServer'), dict) else None


def isi_sama(dok, item):
    """isi dokumen server (tanpa capServer) = isi karcis (kolom & nilai; angka pecahan id dibandingkan sebagai angka)."""
    return json.dumps(tanpa_cap(dok), sort_keys=True) == json.dumps(item['data'], sort_keys=True)


def jalur_kasir(v33, v32, aturan):
    """aturan 'v7' | 'v6' | 'kontrol' — langkah c1…c6 di emulator kosong; → (langkah, cek [(id, nama, ok, ket)])."""
    kosongkan(); c = []; L = {}
    s0 = simpanan_awal(); kini0 = time.time()
    # c1 · nota baru (kasir-v33): simpanNominal → kirimAntrean → :commit + capServer REQUEST_TIME
    h1 = node_kasir(v33, s0, {'nota': 15000}); L['c1'] = h1
    item = (h1.get('antreanSesudahCatat') or [None])[0]
    if not item or h1.get('galat'):
        c.append(('c1', 'kasir-v33 mencatat nota baru (simpanNominal) & mengirimnya', False, h1.get('galat') or 'antrean kosong sesudah simpanNominal'))
        return L, c
    jalur = 'penjualan/' + item['docId']; d1 = ambil_admin(jalur); t1 = tulisan_nota(h1)
    c.append(('c1', 'kasir-v33 nota baru: SATU :commit bercap (transform capServer = REQUEST_TIME, tanpa updateMask) DITERIMA; isi server = karcis + capServer jam server',
              h1.get('versi') == 'kasir-v33' and t1 == [{'cara': 'commit', 'status': 200, 'cap': ['capServer=REQUEST_TIME'], 'mask': False, 'kunci': True}] and not h1['antrean'] and not h1['ditolak']
              and bool(d1) and isi_sama(d1, item) and bool(cap(d1)) and abs(datetime.datetime.fromisoformat(cap(d1).replace('Z', '+00:00')).timestamp() - kini0) < 600,
              {'versi': h1.get('versi'), 'tulisan': t1, 'antrean': len(h1['antrean']), 'ditolak': len(h1['ditolak']), 'cap': cap(d1)}))
    # c2 · kirim ulang IDENTIK (jawaban kiriman pertama hilang di jalan): karcis yang sama kembali ke antrean, halaman dibuka lagi
    h2 = node_kasir(v33, dengan_antrean(h1['simpanan'], item)); L['c2'] = h2; d2 = ambil_admin(jalur); t2 = tulisan_nota(h2)
    if aturan == 'v6':
        c.append(('c2', 'v6: kirim ulang :commit DITOLAK (cap beda, tanpa ulangKasirBercap) → cara lama PATCH updateMask MASUK; tidak pindah ke "ditolak"; cap pertama tetap (tanpa dobel)',
                  [x['cara'] + ':' + str(x['status']) for x in t2] == ['commit:403', 'patch-mask:200'] and not h2['antrean'] and not h2['ditolak'] and bool(d2) and isi_sama(d2, item) and cap(d2) == cap(d1),
                  {'tulisan': t2, 'ditolak': len(h2['ditolak']), 'cap1': cap(d1), 'cap2': cap(d2)}))
    else:
        c.append(('c2', 'kirim ulang IDENTIK kasir-v33: :commit DITERIMA (ulangKasirBercap), tanpa jatuh ke cara lama; capServer = jam server yang BARU; isi sama',
                  [x['cara'] + ':' + str(x['status']) for x in t2] == ['commit:200'] and not h2['antrean'] and not h2['ditolak'] and bool(d2) and isi_sama(d2, item)
                  and bool(cap(d2)) and bool(cap(d1)) and cap(d2) > cap(d1), {'tulisan': t2, 'ditolak': len(h2['ditolak']), 'cap1': cap(d1), 'cap2': cap(d2)}))
    # c3 · kirim ulang yang MENGUBAH isi (hargaTotal + 5.000): :commit ditolak, cara lama ditolak → daftar "ditolak"; server tidak berubah
    ubah = json.loads(json.dumps(item)); ubah['data']['hargaTotal'] = item['data']['hargaTotal'] + 5000
    h3 = node_kasir(v33, dengan_antrean(h2['simpanan'], ubah)); L['c3'] = h3; d3 = ambil_admin(jalur); t3 = tulisan_nota(h3)
    c.append(('c3', 'kirim ulang kasir-v33 yang MENGUBAH isi: :commit DITOLAK, cara lama (PATCH updateMask) DITOLAK → karcis di daftar "ditolak"; dokumen server tidak berubah',
              [x['cara'] + ':' + str(x['status']) for x in t3] == ['commit:403', 'patch-mask:403'] and not h3['antrean'] and len(h3['ditolak']) == len(h2['ditolak']) + 1
              and d3 == d2, {'tulisan': t3, 'ditolak': len(h3['ditolak']), 'sama': d3 == d2}))
    if v32 is None:
        c.append(('c4', 'kasir-v32 (HP penjaga sebelum cabang ini)', False, 'kasir-darurat-nominal.html di %s tidak terbaca (riwayat git dangkal?) — TIDAK TERUKUR' % KASIR_V32_COMMIT))
        return L, c
    # c4 · kasir-v32 kirim ulang IDENTIK atas nota yang sudah bercap (PATCH utuh tanpa cap — capServer terbuang)
    h4 = node_kasir(v32, dengan_antrean(h3['simpanan'], item)); L['c4'] = h4; d4 = ambil_admin(jalur); t4 = tulisan_nota(h4)
    if aturan == 'v6':
        c.append(('c4', 'v6: kasir-v32 kirim ulang identik atas nota BERCAP (PATCH utuh membuang capServer) DITOLAK → pindah ke "ditolak" (sebab v7 perlu ulangKasirBercap)',
                  h4.get('versi') == 'kasir-v32' and [x['cara'] + ':' + str(x['status']) for x in t4] == ['patch:403'] and len(h4['ditolak']) == len(h3['ditolak']) + 1 and d4 == d3,
                  {'versi': h4.get('versi'), 'tulisan': t4, 'ditolak': len(h4['ditolak'])}))
        return L, c
    c.append(('c4', 'kasir-v32 kirim ulang IDENTIK atas nota bercap: PATCH utuh (tanpa updateMask) DITERIMA — capServer terbuang, isi sama; tidak pindah ke "ditolak"',
              h4.get('versi') == 'kasir-v32' and [x['cara'] + ':' + str(x['status']) for x in t4] == ['patch:200'] and not h4['antrean'] and len(h4['ditolak']) == len(h3['ditolak'])
              and bool(d4) and isi_sama(d4, item) and 'capServer' not in d4, {'versi': h4.get('versi'), 'tulisan': t4, 'ditolak': len(h4['ditolak']), 'cap4': cap(d4)}))
    # c5 · kasir-v32 kirim ulang yang MENGUBAH isi → ditolak, server tidak berubah
    ubah2 = json.loads(json.dumps(item)); ubah2['data']['hargaTotal'] = item['data']['hargaTotal'] + 7000
    h5 = node_kasir(v32, dengan_antrean(h4['simpanan'], ubah2)); L['c5'] = h5; d5 = ambil_admin(jalur); t5 = tulisan_nota(h5)
    c.append(('c5', 'kasir-v32 kirim ulang yang MENGUBAH isi: PATCH DITOLAK → daftar "ditolak"; dokumen server tidak berubah',
              [x['cara'] + ':' + str(x['status']) for x in t5] == ['patch:403'] and len(h5['ditolak']) == len(h4['ditolak']) + 1 and d5 == d4, {'tulisan': t5, 'ditolak': len(h5['ditolak'])}))
    # c6 · kasir-v32 nota baru (PATCH, dokumen belum ada = create kasir@) tetap masuk di v7
    h6 = node_kasir(v32, h5['simpanan'], {'nota': 20000}); L['c6'] = h6; it6 = (h6.get('antreanSesudahCatat') or [None])[0]
    d6 = ambil_admin('penjualan/' + it6['docId']) if it6 else None; t6 = tulisan_nota(h6)
    c.append(('c6', 'kasir-v32 nota baru: PATCH (create kasir@) DITERIMA, tanpa capServer', bool(it6) and [x['cara'] + ':' + str(x['status']) for x in t6] == ['patch:200'] and bool(d6) and isi_sama(d6, it6)
              and 'capServer' not in d6, {'tulisan': t6, 'ada': bool(d6)}))
    return L, c


# ============================== --emulator (runner) ==============================
def ringkas(daftar):
    n = len(daftar); ok = sum(1 for x in daftar if x['ok']); tt = sum(1 for x in daftar if x['hasil'] == 'TIDAK TERUKUR')
    return {'kasus': n, 'lulus': ok, 'gagal': n - ok - tt, 'tidakTerukur': tt}


def jalankan_emulator():
    tunggu_emulator()
    J = Jam(); v7, v6 = baca('firestore.rules'), baca('firestore.rules.v6')
    lap = {'mulai': J.iso, 'hariIni': J.hari_ini, 'proyek': PROYEK, 'firebaseTools': os.environ.get('FIREBASE_TOOLS_VERSI', '?'), 'run': os.environ.get('GITHUB_RUN_ID', '')}
    print('— A · v7 (firestore.rules cabang ini): %d kasus' % len(KASUS), flush=True)
    A = jalankan_semua(J, v7); lap['v7'] = A
    for x in A: print('  %s %-7s %-26s %-6s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], '', x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— A · v6 (firestore.rules.v6): kasus yang sama', flush=True)
    B = jalankan_semua(J, v6); lap['v6'] = []
    for a, b in zip(A, B):
        beda_harap = a['no'] in BEDA_V6; harap6 = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if beda_harap else a['wajib']
        r = {'no': b['no'], 'jalur': b['jalur'], 'hasilV6': b['hasil'], 'hasilV7': a['hasil'], 'harapV6': harap6, 'ubahan': BEDA_V6.get(b['no']), 'ket': b['ket'],
             'ok': b['hasil'] == harap6 and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v6'].append(r)
        if not r['ok'] or beda_harap: print('  %s %-7s v6 %-13s v7 %-13s harap v6 %-7s %s' % ('✓' if r['ok'] else '✗', r['no'], r['hasilV6'], r['hasilV7'], harap6, ('ubahan %d · %s' % (r['ubahan'], UBAHAN[r['ubahan']])) if r['ubahan'] else 'harus sama dengan v7'), flush=True)
    print('— A · KONTROL: rules v7 dirusak satu suku → kasus sasaran wajib berbalik', flush=True)
    lap['kontrol'] = []; per = {K[0]: K for K in KASUS}; utuh = {x['no']: x for x in A}
    for nama, ganti, sasaran in KONTROL:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrol'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- C · kasir darurat
    v33 = skrip_halaman(baca('kasir-darurat-nominal.html')); h32 = html_v32(); v32 = skrip_halaman(h32) if h32 else None
    lap['kasir'] = {}
    for label, teks in (('v7', v7), ('v6', v6)):
        pasang_aturan(teks); print('— C · kasir darurat, rules %s' % label, flush=True)
        try: L, c = jalur_kasir(v33, v32, label)
        except Exception as e: L, c = {}, [('c?', 'jalur kasir jatuh', False, str(e)[:400])]
        lap['kasir'][label] = {'cek': [{'id': a, 'nama': b, 'ok': bool(o), 'ket': k} for a, b, o, k in c], 'galatNode': {k: v.get('galat') for k, v in L.items() if v.get('galat')}}
        for a, b, o, k in c: print('  %s %s %s%s' % ('✓' if o else '✗', a, b, '' if o else ' → ' + json.dumps(k, ensure_ascii=False)[:400]), flush=True)
    nama, ganti, sasaran = KONTROL_KASIR
    pasang_aturan(rusak(v7, ganti)); print('— C · KONTROL: ' + nama, flush=True)
    try: L, c = jalur_kasir(v33, v32, 'kontrol')
    except Exception as e: L, c = {}, [('c?', 'jalur kasir jatuh', False, str(e)[:300])]
    gagal = {a for a, b, o, k in c if not o}
    lap['kontrolKasir'] = {'nama': nama, 'sasaran': sasaran, 'gagal': sorted(gagal), 'berbunyi': set(sasaran) <= gagal and all(o for a, b, o, k in c if a not in sasaran)}
    print('  %s %s → gagal: %s' % ('BERBUNYI' if lap['kontrolKasir']['berbunyi'] else 'DIAM!!  ', nama, ', '.join(sorted(gagal)) or '-'), flush=True)
    pasang_aturan(v7)
    lap['ringkas'] = {'v7': ringkas(A), 'wajibOwner': ringkas([x for x in A if x['no'] in P.WAJIB_V7]), 'opsional': ringkas([x for x in A if x['no'].startswith('★') and x['no'] not in P.WAJIB_V7]),
                      'model': ringkas([x for x in A if x['no'].startswith('M-')]), 'server': ringkas([x for x in A if x['no'].startswith('S-')]),
                      'v6': {'kasus': len(lap['v6']), 'sesuai': sum(1 for x in lap['v6'] if x['ok']), 'beda': sum(1 for x in lap['v6'] if x['hasilV6'] != x['hasilV7'])},
                      'kontrol': {'jumlah': len(lap['kontrol']) + 1, 'berbunyi': sum(1 for x in lap['kontrol'] if x['berbunyi']) + (1 if lap['kontrolKasir']['berbunyi'] else 0)},
                      'kasir': {k: {'cek': len(v['cek']), 'lulus': sum(1 for x in v['cek'] if x['ok'])} for k, v in lap['kasir'].items()}}
    lap['lulus'] = (all(x['ok'] for x in A) and all(x['ok'] for x in lap['v6']) and all(x['berbunyi'] for x in lap['kontrol']) and lap['kontrolKasir']['berbunyi']
                    and all(x['ok'] for v in lap['kasir'].values() for x in v['cek']))
    return lap


def ringkasan_md(lap):
    R = lap['ringkas']; f = lambda r: '%d/%d lulus%s' % (r['lulus'], r['kasus'], (' · %d TIDAK TERUKUR' % r['tidakTerukur']) if r['tidakTerukur'] else '')
    out = ['## Bukti server rules v7 — Firebase Emulator Firestore (mesin rules = server produksi)', '',
           'Proyek emulator `%s` · firebase-tools %s · jam runner %s (hari ini WIB %s) · token akun palsu (JWT tanpa tanda tangan, hanya emulator)' % (lap['proyek'], lap['firebaseTools'], lap['mulai'][:19], lap['hariIni']), '',
           '- **A · v7**: %s — Wajib owner %s · opsional ★ %s · model M %s · server S %s' % (f(R['v7']), f(R['wajibOwner']), f(R['opsional']), f(R['model']), f(R['server'])),
           '- **A · v6**: %d/%d sesuai harapan — %d kasus berbeda v6 → v7, semuanya di BEDA_V6 (lima ubahan); selebihnya sama' % (R['v6']['sesuai'], R['v6']['kasus'], R['v6']['beda']),
           '- **Kontrol**: %d/%d berbunyi (rules dirusak satu suku → kasus sasarannya berbalik)' % (R['kontrol']['berbunyi'], R['kontrol']['jumlah']),
           '- **C · kasir darurat (kode asli)**: ' + ' · '.join('%s %d/%d' % (k, v['lulus'], v['cek']) for k, v in R['kasir'].items()), '']
    out += ['### A · kasus (v7)', '', '| no | akun · operasi · jalur | wajib | emulator v7 | v6 |', '|---|---|---|---|---|']
    v6 = {x['no']: x for x in lap['v6']}
    for x in lap['v7']:
        y = v6.get(x['no'], {})
        out.append('| %s %s | %s · %s · `%s` | %s | %s | %s%s |' % ('✓' if x['ok'] else '✗', x['no'], x['akun'], x['op'], x['jalur'].replace('|', '\\|'), x['wajib'], x['hasil'],
                                                           y.get('hasilV6', '?'), (' (ubahan %d)' % y['ubahan']) if y.get('ubahan') else ''))
    out += ['', '### Kontrol', ''] + ['- %s %s → %s' % ('✓ BERBUNYI' if k['berbunyi'] else '✗ DIAM', k['nama'], k.get('galat') or ', '.join('%s %s (wajib %s)' % h for h in k['hasil'])) for k in lap['kontrol']]
    kk = lap['kontrolKasir']; out.append('- %s %s → gagal %s' % ('✓ BERBUNYI' if kk['berbunyi'] else '✗ DIAM', kk['nama'], ', '.join(kk['gagal']) or '-'))
    for label, v in lap['kasir'].items():
        out += ['', '### C · kasir darurat — rules %s' % label, ''] + ['- %s %s · %s%s' % ('✓' if x['ok'] else '✗', x['id'], x['nama'], '' if x['ok'] else ' — `' + json.dumps(x['ket'], ensure_ascii=False)[:400].replace('`', "'") + '`') for x in v['cek']]
        if v.get('galatNode'): out.append('- galat node: `%s`' % json.dumps(v['galatNode'], ensure_ascii=False)[:600].replace('`', "'"))
    return '\n'.join(out) + '\n'


# ============================== --periksa (statis + model + jsc/node dengan server palsu) ==============================
DRIVER_JS = r"""
var HASIL = null;
var PALSU = { tolak: __TOLAK__, minta: [] };
var H = { tidur: function () { return Promise.resolve(); },
  fetch: function (url, opsi) {
    PALSU.minta.push(url);
    var tulisNota = url.indexOf(':commit') >= 0 || (String(opsi.method || '').toUpperCase() === 'PATCH' && url.indexOf('/documents/penjualan/') >= 0);
    var status = tulisNota && PALSU.tolak ? 403 : (String(opsi.method || 'GET').toUpperCase() === 'GET' ? 404 : 200);
    var isi = status === 403 ? { error: { code: 403, status: 'PERMISSION_DENIED', message: 'Missing or insufficient permissions.' } } : {};
    return Promise.resolve({ status: status, ok: status >= 200 && status < 300, json: function () { return Promise.resolve(isi); }, text: function () { return Promise.resolve(JSON.stringify(isi)); } });
  } };
KASIR_UJI.jalankan(H, __SKRIP__, __SIMPANAN__, { nota: 15000 }).then(function (h) { HASIL = h; }, function (e) { HASIL = { galat: String(e) }; });
if (typeof drainMicrotasks === 'function') { for (var i = 0; i < 50 && !HASIL; i++) drainMicrotasks(); print(JSON.stringify(HASIL)); }
else { (function tunggu(n) { if (HASIL || n > 400) { print(JSON.stringify(HASIL)); return; } setImmediate(function () { tunggu(n + 1); }); })(0); }
"""


def jalan_kasir_palsu(skrip, tolak):
    """kasir_emulator.js + skrip halaman di jsc (Mac) atau node (runner) dengan server PALSU (tanpa jaringan). → hasil jalankan()."""
    js = baca('alat-uji/kasir_emulator.js') + '\n' + DRIVER_JS.replace('__TOLAK__', 'true' if tolak else 'false').replace('__SKRIP__', json.dumps(skrip)).replace(
        '__SIMPANAN__', json.dumps({'kasir_auth_v1': json.dumps({'refreshToken': 'r', 'idToken': 't-palsu', 'kedaluwarsa': 4102444800000})}))
    d = tempfile.mkdtemp(prefix='kasir-palsu-'); p = os.path.join(d, 'jalan.js')
    try:
        open(p, 'w', encoding='utf-8').write(js); env = dict(os.environ, TZ='Asia/Jakarta')
        if os.path.exists(JSC): cmd = [JSC, p]
        elif shutil.which('node'):
            cmd = ['node', '-e', "global.print = function () { console.log(Array.prototype.join.call(arguments, ' ')); };"
                   "require('vm').runInThisContext(require('fs').readFileSync(process.argv[1], 'utf8'), { filename: 'jalan.js' });", p]
        else: return None
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        b = [x for x in r.stdout.strip().split('\n') if x.startswith('{')]
        return json.loads(b[-1]) if b else {'galat': (r.stderr or r.stdout)[-800:]}
    finally: shutil.rmtree(d, ignore_errors=True)


def periksa(rules=None, dok=None, html=None):
    """→ [(nama, ok, ket)]. Tanpa emulator: tabel docs = model, model v7/v6, kontrol model, kode kasir di server palsu."""
    c = []; R = rules if rules is not None else baca('firestore.rules'); R6 = baca('firestore.rules.v6'); W = wajib_dok(dok)
    bintang = [K[0] for K in KASUS if K[0].startswith('★')]
    salah_dok = sorted(k for k in bintang if W.get(k) is None or W.get(k) != dict((K[0], K[8]) for K in KASUS)[k])
    c.append(('kolom "Wajib" %s = kolom model untuk %d kasus ★ (tabel dibaca sel demi sel)' % (DOK, len(bintang)), not salah_dok and set(W) == set(bintang),
              {'beda': salah_dok, 'hanya di berkas': sorted(set(W) - set(bintang))}))
    c.append(('id kasus unik (★ docs + M model + S server)', len({K[0] for K in KASUS}) == len(KASUS), len(KASUS)))
    try: M7, M6 = RM.Rules(R), RM.Rules(R6)
    except Exception as e: return c + [('rules terurai penafsir mini', False, str(e)[:300])]
    salah7, beda6 = [], set()
    for K in KASUS:
        no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
        db = dict(P.DB_UJI_V7); db.update(ubah_db or {}); db = {k: v for k, v in db.items() if v is not None}
        h7 = M7.nilai(op, kol, id_, auth=P.AKUN_UJI[aud], data=data, sebelum=db, jam=JAM); h6 = M6.nilai(op, kol, id_, auth=P.AKUN_UJI[aud], data=data, sebelum=db, jam=JAM)
        if h7.boleh != boleh: salah7.append(no)
        if h6.boleh != h7.boleh: beda6.add(no)
    c.append(('model v7 = kolom Wajib di %d kasus (termasuk S-* cap jam server)' % len(KASUS), not salah7, salah7))
    c.append(('model: kasus yang berbeda v6 → v7 = BEDA_V6 persis (%d kasus, lima ubahan)' % len(BEDA_V6), beda6 == set(BEDA_V6), {'model saja': sorted(beda6 - set(BEDA_V6)), 'BEDA_V6 saja': sorted(set(BEDA_V6) - beda6)}))
    per = {K[0]: K for K in KASUS}
    for nama, ganti, sasaran in KONTROL + [(KONTROL_KASIR[0], KONTROL_KASIR[1], ['S-A2', 'S-A3', 'M-A5'])]:
        try:
            Mx = RM.Rules(rusak(R, ganti)); diam = []
            for s in sasaran:
                no, _, aud, op, kol, id_, data, ubah_db, boleh, _ = per[s]
                db = dict(P.DB_UJI_V7); db.update(ubah_db or {}); db = {k: v for k, v in db.items() if v is not None}
                if Mx.nilai(op, kol, id_, auth=P.AKUN_UJI[aud], data=data, sebelum=db, jam=JAM).boleh == boleh: diam.append(s)
            c.append(('kontrol "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
        except Exception as e: c.append(('kontrol "%s"' % nama, False, str(e)[:200]))
    H = html if html is not None else baca('kasir-darurat-nominal.html')
    try: s33 = skrip_halaman(H)
    except Exception as e: return c + [('skrip kasir darurat terbaca', False, str(e))]
    c.append(('kasir darurat cabang ini = kasir-v33', "var VERSI_APLIKASI = 'kasir-v33';" in s33, re.findall(r"var VERSI_APLIKASI = '([^']+)'", s33)))
    h32 = html_v32()
    if h32 is None: c.append(('kasir-v32 di %s terbaca dari git (job emulator: riwayat penuh)' % KASIR_V32_COMMIT[:10], True, 'riwayat dangkal di mesin ini — dinilai di job emulator'))
    else: c.append(('kasir-v32 di %s terbaca dari git dan ber-VERSI kasir-v32' % KASIR_V32_COMMIT[:10], "var VERSI_APLIKASI = 'kasir-v32';" in skrip_halaman(h32), ''))
    h = jalan_kasir_palsu(s33, False)
    if h is None: c.append(('kode kasir darurat di server palsu (jsc / node)', True, 'tanpa jsc & node di mesin ini — dinilai di job emulator')); return c
    t = tulisan_nota(h)
    c.append(('server palsu: kasir-v33 mencatat nota (simpanNominal) lalu mengirim SATU :commit bercap (capServer REQUEST_TIME, tanpa updateMask, berkunci)',
              not h.get('galat') and h.get('versi') == 'kasir-v33' and len(h.get('antreanSesudahCatat') or []) == 1 and t == [{'cara': 'commit', 'status': 200, 'cap': ['capServer=REQUEST_TIME'], 'mask': False, 'kunci': True}]
              and not h.get('antrean') and not h.get('ditolak'), {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    h = jalan_kasir_palsu(s33, True); t = tulisan_nota(h)
    c.append(('server palsu menolak: kasir-v33 :commit ditolak → cara lama PATCH updateMask ditolak → karcis di daftar "ditolak"',
              not h.get('galat') and [x['cara'] + ':' + str(x['status']) for x in t] == ['commit:403', 'patch-mask:403'] and len(h.get('ditolak') or []) == 1, {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    if h32:
        h = jalan_kasir_palsu(skrip_halaman(h32), False); t = tulisan_nota(h)
        c.append(('server palsu: kasir-v32 mengirim nota lewat PATCH utuh (tanpa updateMask, tanpa cap)', not h.get('galat') and h.get('versi') == 'kasir-v32'
                  and [x['cara'] + ':' + str(x['status']) for x in t] == ['patch:200'], {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    return c


def kontrol():
    """kerusakan pada bahan pemeriksa statis wajib ketahuan karena SEBABNYA."""
    R = baca('firestore.rules'); D = baca(DOK); Hh = baca('kasir-darurat-nominal.html'); kode = 0
    assert '| 7 | ★P20 |' in D and "updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }]" in Hh
    kasus = [
        ('kolom Wajib ★P20 di docs dibalik (DITOLAK → LOLOS)', {'dok': re.sub(r'(\n\| 7 \| ★P20 \|[^\n]*?\| )DITOLAK( \|)', r'\1LOLOS\2', D)}, 'kolom "Wajib"'),
        ('rules v7: suku pintu tanpa batas waktu (model ikut berubah)', {'rules': R.replace("\n        && request.time < p.data.sampai ? int(p.data.tahun) : 0;", " ? int(p.data.tahun) : 0;")}, 'model v7 = kolom Wajib'),
        ('kasir darurat tanpa cap jam server (:commit tanpa updateTransforms)', {'html': Hh.replace(",\n        updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }] }] })", " }] })")}, 'server palsu: kasir-v33'),
        ('kasir darurat tanpa cara lama (ditolak langsung ke "ditolak")', {'html': Hh.replace("          if (bercap) { kirimItem(item, false, true); return; }", "")}, 'server palsu menolak'),
    ]
    for nama, rusak_, sebab in kasus:
        if any(v in (R, D, Hh) for v in rusak_.values()): print('KONTROL BASI  ' + nama); kode = 3; continue
        c = periksa(rusak_.get('rules'), rusak_.get('dok'), rusak_.get('html'))
        g = [x for x in c if not x[1]]; tepat = [x for x in g if x[0].startswith(sebab)]
        print(('BERBUNYI ' if tepat else 'DIAM!!   ') + nama + ' → ' + (tepat[0][0][:100] + ' · ' + json.dumps(tepat[0][2], ensure_ascii=False)[:160] if tepat else ('lain: ' + g[0][0][:100] if g else '-')))
        if not tepat: kode = 3
    return kode


if __name__ == '__main__':
    arg = sys.argv[1:]
    opsi = lambda n: arg[arg.index(n) + 1] if n in arg and arg.index(n) + 1 < len(arg) else ''
    if '--kontrol' in arg: sys.exit(kontrol())
    if '--emulator' not in arg:
        c = periksa(); g = [x for x in c if not x[1]]
        for n, ok, k in c: print(('✓ ' if ok else '✗ ') + n + ('' if ok else ' → ' + json.dumps(k, ensure_ascii=False)[:400]))
        print('BUKTI SERVER RULES v7 (statis + model + kode kasir di server palsu): %d lulus · %d gagal — emulator: workflow "Uji rules di emulator"' % (len(c) - len(g), len(g)))
        sys.exit(2 if g else 0)
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        print('DITOLAK: --emulator menyalakan Firebase Emulator & node — HANYA di runner GitHub Actions (CLAUDE.md, keputusan owner 27 Sep 2026).\n'
              'Jalankan workflow "Uji rules di emulator". Di Mac boleh: --periksa / --kontrol.')
        sys.exit(2)
    lap = jalankan_emulator()
    md = ringkasan_md(lap)
    if opsi('--keluar'): os.makedirs(os.path.dirname(os.path.abspath(opsi('--keluar'))), exist_ok=True); json.dump(lap, open(opsi('--keluar'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if opsi('--ringkasan'): open(opsi('--ringkasan'), 'w', encoding='utf-8').write(md)
    print('\n' + md)
    print('BUKTI SERVER RULES v7: ' + ('LULUS' if lap['lulus'] else 'GAGAL'))
    sys.exit(0 if lap['lulus'] else 2)
