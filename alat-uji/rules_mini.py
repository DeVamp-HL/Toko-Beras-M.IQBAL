#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules_mini.py — PENAFSIR MINI bahasa Firestore Security Rules (v2), hanya bagian yang dipakai firestore.rules toko ini. Tanpa Node, tanpa emulator.

Untuk apa: menilai TEKS rules yang sebenarnya (bukan salinan logikanya) pada tulisan contoh — kasus Playground ★ (periksa_rules.py) dan SETIAP batch
yang dikirim ritual tutup buku di kotak pasir jsc (uji_tutup_buku_2027.py) — sekaligus MENGHITUNG access call (get / getAfter / exists / existsAfter;
cache TIDAK dianggap ada, keputusan owner 24 & 25 Sep). Ini MODEL, bukan server: bukti server tetap Playground (docs/uji-rules-v7.md) dan nota sungguhan.

Yang dikenali: function (let …; return …;), match /koleksi/{id} satu tingkat di bawah /databases/{database}/documents, allow <op,…>: if <ekspresi>;
operator || && ! == != < <= > >= in is + - * / % ?: , anggota/metode/indeks/irisan, literal teks/angka/list/map, jalur /databases/$(database)/… .
Semantik galat seperti server: `galat || benar` = benar, `galat && salah` = salah; selebihnya galat = DITOLAK.
Metode: map.get/keys/values/size/diff · MapDiff.affectedKeys/addedKeys/removedKeys/changedKeys · list/set.size/hasAny/hasAll/hasOnly · string.size/
matches/lower/upper · timestamp.year/month/day/toMillis · int() string() float() timestamp.value() duration.value() · get getAfter exists existsAfter.

    from rules_mini import Rules, Ts
    R = Rules(open('firestore.rules').read())
    h = R.nilai('delete', 'penjualan', 'abc', auth={'uid': 'u1', 'email': 'owner@…'}, sebelum=db0, sesudah=db1, jam=Ts.dari_iso('2028-01-05T03:00:00Z'))
    h.boleh, h.akses (access call), h.jalur (dokumen yang dibaca), h.galat
"""
import re, datetime

ROOT = '/databases/(default)/documents/'


class Galat(Exception):
    pass


class Ts:
    """timestamp (milidetik UTC)."""
    __slots__ = ('ms',)
    def __init__(self, ms): self.ms = int(ms)
    @staticmethod
    def dari_iso(s): return Ts(datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp() * 1000)
    def _dt(self): return datetime.datetime.fromtimestamp(self.ms / 1000.0, datetime.timezone.utc)
    def __eq__(self, o): return isinstance(o, Ts) and o.ms == self.ms
    def __hash__(self): return hash(self.ms)
    def __repr__(self): return 'Ts(%s)' % self._dt().isoformat()


class Dur:
    __slots__ = ('ms',)
    def __init__(self, ms): self.ms = int(ms)
    def __eq__(self, o): return isinstance(o, Dur) and o.ms == self.ms


class Res:
    """resource / hasil get(): .data, .id."""
    def __init__(self, data, id_):
        self.data = data; self.id = id_


class MapDiff:
    def __init__(self, a, b):
        ka, kb = set(a.keys()), set(b.keys())
        self.added = ka - kb; self.removed = kb - ka
        self.changed = set(k for k in ka & kb if not sama(a[k], b[k]))
    def affected(self): return self.added | self.removed | self.changed


class Fn:
    def __init__(self, nama, param, badan): self.nama, self.param, self.badan = nama, param, badan


def sama(a, b):
    if isinstance(a, bool) or isinstance(b, bool): return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)): return a == b
    if isinstance(a, dict) and isinstance(b, dict): return a.keys() == b.keys() and all(sama(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)): return len(a) == len(b) and all(sama(x, y) for x, y in zip(a, b))
    if isinstance(a, (set, frozenset)) and isinstance(b, (set, frozenset)): return a == b
    if a is None or b is None: return a is None and b is None
    if type(a) is not type(b): return False
    return a == b


# ---------------- tokenizer ----------------
_OP = ['&&', '||', '==', '!=', '<=', '>=', '<', '>', '!', '+', '-', '*', '/', '%', '?', ':', '.', ',', '(', ')', '[', ']', '{', '}', ';', '=']


def token(s):
    out = []; i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n': i += 1; continue
        if c == '/' and s[i:i + 2] == '//':
            j = s.find('\n', i); i = n if j < 0 else j; continue
        # jalur di posisi argumen: (/databases/…)
        if c == '/' and out and out[-1] == ('op', '('):
            j = i; d = 0
            while j < n:
                if s[j] == '(': d += 1
                elif s[j] == ')':
                    if d == 0: break
                    d -= 1
                j += 1
            out.append(('jalur', s[i:j])); i = j; continue
        if c.isdigit():
            m = re.match(r'\d+(\.\d+)?', s[i:]); t = m.group(0); out.append(('angka', float(t) if '.' in t else int(t))); i += len(t); continue
        if c.isalpha() or c == '_':
            m = re.match(r'[A-Za-z_]\w*', s[i:]); out.append(('nama', m.group(0))); i += len(m.group(0)); continue
        if c in '\'"':
            j = i + 1; buf = ''
            while s[j] != c:
                if s[j] == '\\': buf += s[j + 1]; j += 2; continue
                buf += s[j]; j += 1
            out.append(('teks', buf)); i = j + 1; continue
        for op in _OP:
            if s.startswith(op, i): out.append(('op', op)); i += len(op); break
        else: raise Galat('karakter tak dikenal %r di %d' % (c, i))
    return out


# ---------------- parser (pohon = tuple) ----------------
class Pengurai:
    def __init__(self, t): self.t = t; self.i = 0
    def lihat(self, k=0): return self.t[self.i + k] if self.i + k < len(self.t) else ('akhir', None)
    def ambil(self): x = self.lihat(); self.i += 1; return x
    def harap(self, jenis, nilai=None):
        x = self.ambil()
        if x[0] != jenis or (nilai is not None and x[1] != nilai): raise Galat('harap %s %s, dapat %r' % (jenis, nilai, x))
        return x
    def op(self, v): return self.lihat() == ('op', v)

    def ekspresi(self):
        c = self.atau()
        if self.op('?'):
            self.ambil(); a = self.ekspresi(); self.harap('op', ':'); b = self.ekspresi(); return ('?', c, a, b)
        return c
    def atau(self):
        a = self.dan()
        while self.op('||'): self.ambil(); a = ('||', a, self.dan())
        return a
    def dan(self):
        a = self.relasi()
        while self.op('&&'): self.ambil(); a = ('&&', a, self.relasi())
        return a
    def relasi(self):
        a = self.tambah()
        while True:
            x = self.lihat()
            if x[0] == 'op' and x[1] in ('==', '!=', '<', '<=', '>', '>='): self.ambil(); a = (x[1], a, self.tambah())
            elif x == ('nama', 'in'): self.ambil(); a = ('in', a, self.tambah())
            elif x == ('nama', 'is'): self.ambil(); a = ('is', a, self.harap('nama')[1])
            else: return a
    def tambah(self):
        a = self.kali()
        while self.lihat()[0] == 'op' and self.lihat()[1] in ('+', '-'): o = self.ambil()[1]; a = (o, a, self.kali())
        return a
    def kali(self):
        a = self.unari()
        while self.lihat()[0] == 'op' and self.lihat()[1] in ('*', '/', '%'): o = self.ambil()[1]; a = (o, a, self.unari())
        return a
    def unari(self):
        if self.op('!'): self.ambil(); return ('!', self.unari())
        if self.op('-'): self.ambil(); return ('neg', self.unari())
        return self.akhiran()
    def akhiran(self):
        a = self.primer()
        while True:
            if self.op('.'):
                self.ambil(); n = self.harap('nama')[1]
                if self.op('('): a = ('metode', a, n, self.argumen())
                else: a = ('anggota', a, n)
            elif self.op('['):
                self.ambil()
                if self.op(':'): self.ambil(); b = self.ekspresi(); self.harap('op', ']'); a = ('iris', a, None, b); continue
                x = self.ekspresi()
                if self.op(':'): self.ambil(); b = self.ekspresi(); self.harap('op', ']'); a = ('iris', a, x, b)
                else: self.harap('op', ']'); a = ('indeks', a, x)
            else: return a
    def argumen(self):
        self.harap('op', '('); a = []
        while not self.op(')'):
            a.append(self.ekspresi())
            if self.op(','): self.ambil()
        self.harap('op', ')'); return a
    def primer(self):
        x = self.ambil()
        if x[0] == 'angka': return ('lit', x[1])
        if x[0] == 'teks': return ('lit', x[1])
        if x[0] == 'jalur': return ('jalur', jalur_bagian(x[1]))
        if x == ('op', '('): e = self.ekspresi(); self.harap('op', ')'); return e
        if x == ('op', '['):
            a = []
            while not self.op(']'):
                a.append(self.ekspresi())
                if self.op(','): self.ambil()
            self.ambil(); return ('list', a)
        if x == ('op', '{'):
            a = []
            while not self.op('}'):
                k = self.ekspresi(); self.harap('op', ':'); a.append((k, self.ekspresi()))
                if self.op(','): self.ambil()
            self.ambil(); return ('map', a)
        if x[0] == 'nama':
            if x[1] == 'true': return ('lit', True)
            if x[1] == 'false': return ('lit', False)
            if x[1] == 'null': return ('lit', None)
            if self.op('('): return ('panggil', x[1], self.argumen())
            return ('var', x[1])
        raise Galat('ekspresi tak terduga %r' % (x,))


def jalur_bagian(teks):
    """'/databases/$(database)/documents/a/$(x + y)' → [('lit','/databases/'), ('ek', pohon), ('lit','/documents/a/'), ('ek', pohon)]."""
    out = []; i = 0; buf = ''
    while i < len(teks):
        if teks.startswith('$(', i):
            if buf: out.append(('lit', buf)); buf = ''
            j = i + 2; d = 0
            while True:
                if teks[j] == '(': d += 1
                elif teks[j] == ')':
                    if d == 0: break
                    d -= 1
                j += 1
            p = Pengurai(token(teks[i + 2:j])); out.append(('ek', p.ekspresi()))
            if p.lihat()[0] != 'akhir': raise Galat('jalur $(…) tidak terurai habis: ' + teks)
            i = j + 1; continue
        buf += teks[i]; i += 1
    if buf: out.append(('lit', buf))
    return out


def urai_badan(badan):
    """badan fungsi → [('let', nama, pohon) …, ('return', pohon)]."""
    t = token(badan); p = Pengurai(t); out = []
    while p.lihat()[0] != 'akhir':
        x = p.ambil()
        if x == ('nama', 'let'):
            n = p.harap('nama')[1]; p.harap('op', '='); out.append(('let', n, p.ekspresi())); p.harap('op', ';')
        elif x == ('nama', 'return'):
            out.append(('return', p.ekspresi()))
            if p.op(';'): p.ambil()
        else: raise Galat('pernyataan tak dikenal %r' % (x,))
    return out


def _tanpa_komentar(t): return re.sub(r'//[^\n]*', '', t)


# ---------------- penilai ----------------
class Hasil:
    def __init__(self, boleh, akses, jalur, galat, suku):
        self.boleh, self.akses, self.jalur, self.galat, self.suku = boleh, akses, jalur, galat, suku
    def __repr__(self): return 'Hasil(boleh=%s, akses=%d, galat=%s)' % (self.boleh, self.akses, self.galat)


class Rules:
    def __init__(self, teks):
        t = _tanpa_komentar(teks); self.fn = {}; self.blok = {}
        for m in re.finditer(r'function (\w+)\(([^)]*)\) \{', t):
            i = m.end() - 1; d = 0
            for j in range(i, len(t)):
                if t[j] == '{': d += 1
                elif t[j] == '}':
                    d -= 1
                    if d == 0: badan = t[i + 1:j]; break
            param = [x.strip() for x in m.group(2).split(',') if x.strip()]
            self.fn[m.group(1)] = Fn(m.group(1), param, urai_badan(badan))
        for m in re.finditer(r'\n    match /(\w+)/\{(\w+)\} \{\n(.*?)\n    \}', t, re.S):
            allows = []
            for a in re.finditer(r'allow ([a-z, ]+): if (.*?);', m.group(3), re.S):
                ops = [x.strip() for x in a.group(1).split(',')]
                pu = Pengurai(token(a.group(2))); pohon = pu.ekspresi()
                if pu.lihat()[0] != 'akhir': raise Galat('allow %s di %s tidak terurai habis (sisa %r)' % (a.group(1), m.group(1), pu.lihat()))   # bentuk asing = berhenti, bukan diam
                allows.append((ops, pohon, re.sub(r'\s+', ' ', a.group(2)).strip()))
            self.blok[m.group(1)] = (m.group(2), allows)

    # db = { 'koleksi/id': data(dict) } ; sesudah = keadaan sesudah batch (getAfter / existsAfter)
    def nilai(self, op, koleksi, id_, auth=None, data=None, sebelum=None, sesudah=None, jam=None):
        """op: get | list | create | update | delete. data = isi BARU (create/update). sebelum/sesudah = isi basis data (dict 'koleksi/id' → data)."""
        sebelum = sebelum or {}; sesudah = sesudah if sesudah is not None else sebelum
        if koleksi not in self.blok: return Hasil(False, 0, [], 'tanpa blok', '')
        param, allows = self.blok[koleksi]
        lama = sebelum.get(koleksi + '/' + id_)
        st = {'akses': 0, 'jalur': [], 'sebelum': sebelum, 'sesudah': sesudah}
        req = {'auth': ({'uid': auth.get('uid'), 'token': {'email': auth.get('email')}} if auth else None),
               'time': jam or Ts.dari_iso('2027-01-05T03:00:00Z'), 'method': op}
        if op in ('create', 'update'): req['resource'] = Res(data, id_)
        env = {'request': req, 'resource': (Res(lama, id_) if (lama is not None and op != 'create') else None), param: id_, 'database': '(default)'}
        galat = ''
        for ops, pohon, teks in allows:
            kena = op in ops or ('write' in ops and op in ('create', 'update', 'delete')) or ('read' in ops and op in ('get', 'list'))
            if not kena: continue
            try: v = self.e(pohon, env, st)
            except Galat as g: galat = str(g); continue
            if v is True: return Hasil(True, st['akses'], st['jalur'], '', teks)
        return Hasil(False, st['akses'], st['jalur'], galat, '')

    # ---- ekspresi
    def e(self, n, env, st):
        k = n[0]
        if k == 'lit': return n[1]
        if k == 'var':
            if n[1] in env: return env[n[1]]
            if n[1] in ('timestamp', 'duration', 'math'): return ('ruang', n[1])
            raise Galat('nama tak dikenal: ' + n[1])
        if k == '||':
            try: a = self.e(n[1], env, st)
            except Galat:
                b = self.e(n[2], env, st)
                if b is True: return True
                raise
            if a is True: return True
            if a is not False: raise Galat('|| bukan bool')
            b = self.e(n[2], env, st)
            if not isinstance(b, bool): raise Galat('|| bukan bool')
            return b
        if k == '&&':
            try: a = self.e(n[1], env, st)
            except Galat:
                b = self.e(n[2], env, st)
                if b is False: return False
                raise
            if a is False: return False
            if a is not True: raise Galat('&& bukan bool')
            b = self.e(n[2], env, st)
            if not isinstance(b, bool): raise Galat('&& bukan bool')
            return b
        if k == '!':
            a = self.e(n[1], env, st)
            if not isinstance(a, bool): raise Galat('! bukan bool')
            return not a
        if k == 'neg': return -self.angka(self.e(n[1], env, st))
        if k == '?':
            c = self.e(n[1], env, st)
            if not isinstance(c, bool): raise Galat('?: bukan bool')
            return self.e(n[2] if c else n[3], env, st)
        if k in ('==', '!='):
            a, b = self.e(n[1], env, st), self.e(n[2], env, st); s = sama(a, b); return s if k == '==' else not s
        if k in ('<', '<=', '>', '>='):
            a, b = self.e(n[1], env, st), self.e(n[2], env, st)
            if isinstance(a, Ts) and isinstance(b, Ts): a, b = a.ms, b.ms
            elif isinstance(a, str) and isinstance(b, str): pass
            else: a, b = self.angka(a), self.angka(b)
            return {'<': a < b, '<=': a <= b, '>': a > b, '>=': a >= b}[k]
        if k == 'in':
            a, b = self.e(n[1], env, st), self.e(n[2], env, st)
            if isinstance(b, dict): return isinstance(a, str) and a in b
            if isinstance(b, (list, set, frozenset)): return any(sama(a, x) for x in b)
            raise Galat('in atas bukan list/map')
        if k == 'is':
            a = self.e(n[1], env, st); t = n[2]
            if t == 'string': return isinstance(a, str)
            if t == 'int': return isinstance(a, int) and not isinstance(a, bool)
            if t == 'float': return isinstance(a, float)
            if t == 'number': return isinstance(a, (int, float)) and not isinstance(a, bool)
            if t == 'bool': return isinstance(a, bool)
            if t == 'list': return isinstance(a, list)
            if t == 'map': return isinstance(a, dict)
            if t == 'timestamp': return isinstance(a, Ts)
            if t == 'duration': return isinstance(a, Dur)
            raise Galat('jenis tak dikenal: ' + t)
        if k in ('+', '-', '*', '/', '%'):
            a, b = self.e(n[1], env, st), self.e(n[2], env, st)
            if k == '+' and isinstance(a, str) and isinstance(b, str): return a + b
            if k == '+' and isinstance(a, list) and isinstance(b, list): return a + b
            if k in ('+', '-') and isinstance(a, Ts) and isinstance(b, Dur): return Ts(a.ms + b.ms if k == '+' else a.ms - b.ms)
            a, b = self.angka(a), self.angka(b)
            if k == '+': return a + b
            if k == '-': return a - b
            if k == '*': return a * b
            if k == '/':
                if b == 0: raise Galat('bagi nol')
                return a // b if isinstance(a, int) and isinstance(b, int) else a / b
            return a % b
        if k == 'anggota':
            a = self.e(n[1], env, st)
            if isinstance(a, dict):
                if n[2] not in a: raise Galat('kolom tidak ada: ' + n[2])
                return a[n[2]]
            if isinstance(a, Res): return a.data if n[2] == 'data' else a.id if n[2] == 'id' else self._salah('anggota resource ' + n[2])
            if a is None: raise Galat('null.' + n[2])
            raise Galat('anggota %s atas %r' % (n[2], type(a)))
        if k == 'indeks':
            a, i = self.e(n[1], env, st), self.e(n[2], env, st)
            if isinstance(a, list):
                if not isinstance(i, int) or i < 0 or i >= len(a): raise Galat('Index out of bound')
                return a[i]
            if isinstance(a, dict):
                if i not in a: raise Galat('kunci tidak ada')
                return a[i]
            if isinstance(a, str): return a[i]
            raise Galat('indeks atas bukan list/map')
        if k == 'iris':
            a = self.e(n[1], env, st); i = self.e(n[2], env, st) if n[2] is not None else 0; j = self.e(n[3], env, st)
            if not isinstance(i, int) or not isinstance(j, int) or i < 0 or i > j or j > len(a): raise Galat('Index out of bound')
            if isinstance(a, list) and j == 0: raise Galat('Index out of bound. Index: [-1]')   # Playground 25 Sep: list[0:0] galat di server
            return a[i:j]
        if k == 'list': return [self.e(x, env, st) for x in n[1]]
        if k == 'map': return dict((self.e(a, env, st), self.e(b, env, st)) for a, b in n[1])
        if k == 'jalur':
            return ''.join(b[1] if b[0] == 'lit' else str(self.e(b[1], env, st)) for b in n[1])
        if k == 'metode': return self.metode(self.e(n[1], env, st), n[2], [self.e(x, env, st) for x in n[3]], st)
        if k == 'panggil': return self.panggil(n[1], n[2], env, st)
        raise Galat('simpul tak dikenal ' + k)

    def _salah(self, s): raise Galat(s)

    @staticmethod
    def angka(a):
        if isinstance(a, bool) or not isinstance(a, (int, float)): raise Galat('bukan angka: %r' % (a,))
        return a

    def metode(self, a, m, arg, st):
        if isinstance(a, tuple) and a[0] == 'ruang':
            if a[1] == 'timestamp' and m == 'value': return Ts(arg[0])
            if a[1] == 'duration' and m == 'value':
                kali = {'w': 604800000, 'd': 86400000, 'h': 3600000, 'm': 60000, 's': 1000, 'ms': 1}[arg[1]]; return Dur(arg[0] * kali)
            raise Galat('fungsi ruang tak dikenal %s.%s' % (a[1], m))
        if isinstance(a, dict):
            if m == 'get':
                k = arg[0]
                if isinstance(k, list):
                    cur = a
                    for x in k:
                        if not isinstance(cur, dict) or x not in cur: return arg[1]
                        cur = cur[x]
                    return cur
                return a[k] if k in a else arg[1]
            if m == 'keys': return list(a.keys())
            if m == 'values': return list(a.values())
            if m == 'size': return len(a)
            if m == 'diff':
                if not isinstance(arg[0], dict): raise Galat('diff bukan map')
                return MapDiff(a, arg[0])
        if isinstance(a, MapDiff):
            if m == 'affectedKeys': return frozenset(a.affected())
            if m == 'addedKeys': return frozenset(a.added)
            if m == 'removedKeys': return frozenset(a.removed)
            if m == 'changedKeys': return frozenset(a.changed)
        if isinstance(a, (list, frozenset, set)):
            isi = list(a)
            if m == 'size': return len(isi)
            if m == 'hasAny': return any(any(sama(x, y) for y in isi) for x in arg[0])
            if m == 'hasAll': return all(any(sama(x, y) for y in isi) for x in arg[0])
            if m == 'hasOnly': return all(any(sama(x, y) for y in arg[0]) for x in isi)
        if isinstance(a, str):
            if m == 'size': return len(a)
            if m == 'matches': return re.fullmatch(arg[0], a) is not None
            if m == 'lower': return a.lower()
            if m == 'upper': return a.upper()
        if isinstance(a, Ts):
            d = a._dt()
            if m == 'year': return d.year
            if m == 'month': return d.month
            if m == 'day': return d.day
            if m == 'toMillis': return a.ms
        raise Galat('metode %s atas %r' % (m, type(a)))

    def panggil(self, nama, arg, env, st):
        if nama in ('get', 'getAfter', 'exists', 'existsAfter'):
            p = self.e(arg[0], env, st); st['akses'] += 1; st['jalur'].append(nama + ' ' + p)
            if not p.startswith(ROOT): raise Galat('jalur bukan dokumen: ' + p)
            kunci = p[len(ROOT):]; db = st['sesudah'] if nama.endswith('After') else st['sebelum']
            if kunci.count('/') != 1: raise Galat('jalur dokumen salah: ' + p)
            d = db.get(kunci)
            if nama.startswith('exists'): return d is not None
            return None if d is None else Res(d, kunci.split('/')[1])
        if nama == 'int':
            v = self.e(arg[0], env, st)
            if isinstance(v, bool): raise Galat('int(bool)')
            if isinstance(v, (int, float)): return int(v)
            if isinstance(v, str):
                if not re.fullmatch(r'-?\d+', v): raise Galat('int(%r)' % v)
                return int(v)
            raise Galat('int(%r)' % (v,))
        if nama == 'float':
            v = self.e(arg[0], env, st); return float(self.angka(v) if not isinstance(v, str) else v)
        if nama == 'string':
            v = self.e(arg[0], env, st)
            if isinstance(v, bool): return 'true' if v else 'false'
            if v is None: return 'null'
            if isinstance(v, float): return repr(v)
            if isinstance(v, (int, str)): return str(v)
            raise Galat('string(%r)' % (v,))
        if nama in self.fn:
            f = self.fn[nama]
            if len(arg) != len(f.param): raise Galat('jumlah argumen %s' % nama)
            # lingkup fungsi = global saja (request, resource, database) + parameternya — bukan variabel pemanggil (rules tidak mewariskannya)
            lokal = dict((g, env[g]) for g in ('request', 'resource', 'database') if g in env); nilai = [self.e(x, env, st) for x in arg]
            for p, v in zip(f.param, nilai): lokal[p] = v
            st.setdefault('dalam', 0); st['dalam'] += 1
            if st['dalam'] > 20: raise Galat('fungsi terlalu dalam')
            try:
                for s in f.badan:
                    if s[0] == 'let': lokal[s[1]] = self.e(s[2], lokal, st)   # let dinilai SAAT ITU (eager — tiap get() di let terhitung)
                    else: return self.e(s[1], lokal, st)
            finally: st['dalam'] -= 1
            raise Galat('fungsi tanpa return: ' + nama)
        raise Galat('fungsi tak dikenal: ' + nama)


def nilai_batch(R, ops, auth, sebelum, jam):
    """Satu writeBatch: ops = [{ 'op': create|update|delete|set, 'koleksi', 'id', 'data' }] (set = create bila belum ada, update bila sudah).
    Semua dinilai terhadap keadaan SEBELUM batch (resource, get) dan SESUDAH batch (getAfter / existsAfter), seperti server.
    → { boleh, akses (jumlah access call batch), tiap: [Hasil per op], sesudah }."""
    sesudah = dict(sebelum); jenis = []
    for o in ops:
        k = o['koleksi'] + '/' + str(o['id'])
        j = o['op']
        if j == 'set': j = 'update' if k in sebelum else 'create'
        jenis.append(j)
        if j == 'delete': sesudah.pop(k, None)
        else: sesudah[k] = o['data']
    tiap = [R.nilai(j, o['koleksi'], str(o['id']), auth=auth, data=o.get('data'), sebelum=sebelum, sesudah=sesudah, jam=jam) for j, o in zip(jenis, ops)]
    return {'boleh': all(h.boleh for h in tiap), 'akses': sum(h.akses for h in tiap), 'tiap': tiap, 'jenis': jenis, 'sesudah': sesudah}
