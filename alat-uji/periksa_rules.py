#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_rules.py — pemeriksa STATIS firestore.rules v4 (putaran 23 + 25), tanpa Node & tanpa emulator.
Membuktikan bentuk rules, bukan perilaku server (itu docs/uji-rules-v4.md: Playground ★).

  1. tiap nama di baru/js/data/koleksi.js punya blok `match /<nama>/{…}` SENDIRI (+ aksesAkun, permintaanAkses, arsipTahun eksplisit);
  2. owner() masih berbasis EMAIL owner; tidak ada allow yang cuma `masuk()` (siapa pun yang login);
  3. semua jalur kasir@ v2 masih ada — dan dipersempit ke email kasir@ (kasir());
  4. tiap create/update bukan-owner lewat fungsi yang memeriksa uid penulis (jujur() / diubahOlehUid / akunUid), atau ada di daftar
     pengecualian peta (permintaanAkses = uid sendiri); bukan-owner tidak pernah DELETE; arsipTahun owner saja; payung owner di paling bawah;
  5. daftar peran per koleksi di rules SAMA dengan baru/js/data/akses.js (BACA_STAF, DOK_STAF, BUAT_STAF, UBAH_STAF, KREDIT_STAF);
  6. aksesAkun tidak pernah bisa memberi peran owner;
  7. (putaran 25) TANPA PAYUNG: Firestore memberi akses kalau SALAH SATU blok yang cocok mengizinkan, jadi payung owner mengalahkan kunci periode.
     GAGAL bila ada match rekursif ({…=**}) yang memberi izin tulis, atau wildcard koleksi (/{x}/…) apa pun;
  8. (putaran 25) KUNCI PERIODE: tiap koleksi bertanggal di baru/js/data/kunci-periode.js (KP_KOLEKSI) menilai tanggalnya di SETIAP create/update/delete,
     untuk owner, kasir@, dan bukan-owner (tglStaf, tanpa get()); field = KP_KOLEKSI; pajak TIDAK dikunci (K6); tenggangMin() = KP_TENGGANG_MIN;
     get() dokumen kunci hanya di terkunci(), dan terkunci() hanya dipanggil bolehBulan() di belakang bebas() (≤ 1 access call per operasi);
     aturanToko/kunciPeriode: naik satu / turun satu dengan alasan ≥ 10, riwayat lama utuh, tidak pernah dihapus.

    python3 alat-uji/periksa_rules.py            → LULUS / daftar cacat (keluar 2)
    python3 alat-uji/periksa_rules.py --kontrol  → berkas rules cacat buatan WAJIB gagal (keluar 3 kalau ada yang lolos)
"""
import os, re, sys

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
EMAIL_OWNER = 'owner@tokoberasmiqbal.web.app'; EMAIL_KASIR = 'kasir@tokoberasmiqbal.web.app'
PERAN = ['ben', 'karyawan']
FUNGSI_JUJUR = {'stafBuat', 'stafBuatTipe', 'stafBuatJual', 'stafJejak', 'stafUbahPesanan', 'stafDenyut'}


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


def daftar_js(teks, nama):
    m = re.search(r'export const ' + nama + r' = \[(.*?)\];', teks, re.S); return re.findall(r"'(\w+)'", m.group(1)) if m else None


def peta_js(teks, nama):
    m = re.search(r'export const ' + nama + r' = \{(.*?)\};', teks, re.S)
    return dict((k, re.findall(r"'(\w+)'", v)) for k, v in re.findall(r"(\w+): \[([^\]]*)\]", m.group(1))) if m else None


def blok_rules(rules):
    """nama koleksi → teks blok (match satu tingkat)."""
    out = {}
    for m in re.finditer(r'\n    match /(\w+)/\{(\w+)\} \{\n(.*?)\n    \}', rules, re.S): out[m.group(1)] = m.group(3)
    return out


def fungsi_rules(rules):
    """nama fungsi → badannya (pencocok kurung kurawal; fungsi satu baris maupun bertingkat)."""
    out = {}
    for m in re.finditer(r'function (\w+)\(([^)]*)\) \{', rules):
        i = m.end() - 1; d = 0
        for j in range(i, len(rules)):
            if rules[j] == '{': d += 1
            elif rules[j] == '}':
                d -= 1
                if d == 0: out[m.group(1)] = rules[i + 1:j]; break
    return out


def tanpa_komentar(t): return re.sub(r'//[^\n]*', '', t)


def allow(blok, op):
    """Baris-baris allow (boleh bersambung ke baris berikut sampai ';') yang menyebut operasi op."""
    hasil = []
    for m in re.finditer(r'allow ([a-z, ]+): (.*?);', blok, re.S):
        ops = [x.strip() for x in m.group(1).split(',')]
        if op in ops or ('write' in ops and op in ('create', 'update', 'delete')) or ('read' in ops and op in ('get', 'list')): hasil.append(m.group(2))
    return hasil


OPERASI = ['get', 'list', 'create', 'update', 'delete']


def suku_atas(kondisi):
    """Suku-suku OR tingkat teratas dari satu kondisi allow (kurung dihormati)."""
    k = re.sub(r'^if ', '', re.sub(r'\s+', ' ', kondisi).strip()); d = 0; bag = []; cur = ''; i = 0
    while i < len(k):
        c = k[i]
        if c in '([{': d += 1
        elif c in ')]}': d -= 1
        if d == 0 and k[i:i + 4] == ' || ': bag.append(cur.strip()); cur = ''; i += 4; continue
        cur += c; i += 1
    bag.append(cur.strip()); return bag


KP_TEKS = None   # kontrol: pengganti isi kunci-periode.js (mis. minimal diturunkan di KEDUA tempat)
TENGGANG_OWNER = 3   # keputusan owner 25 Sep: bulan M paling cepat dikunci tanggal 4 bulan M+1


def kp_js():
    t = KP_TEKS if KP_TEKS is not None else baca('baru/js/data/kunci-periode.js')
    m = re.search(r'export const KP_KOLEKSI = \{(.*?)\};', t, re.S); kol = dict(re.findall(r"(\w+): '(\w+)'", m.group(1))) if m else {}
    tm = re.search(r'export const KP_TENGGANG_MIN = (\d+);', t)
    return kol, int(tm.group(1)) if tm else None


def periksa_kunci(rules, B, F):
    """8 · kunci periode (putaran 25)."""
    cacat = []; KOL, TMIN = kp_js()
    if not KOL or TMIN is None: return ['kunci-periode.js: KP_KOLEKSI / KP_TENGGANG_MIN tidak terbaca']
    rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    if '25200000' not in F.get('wib', '') or 'request.time.toMillis()' not in F.get('wib', '') or 'timestamp.value(' not in F.get('wib', ''): cacat.append('wib() bukan request.time + 7 jam lewat timestamp.value(toMillis())')
    mt = re.search(r'return (\d+);', F.get('tenggangMin', ''))
    if not mt or int(mt.group(1)) != TMIN: cacat.append('tenggangMin() di rules (%s) beda dengan KP_TENGGANG_MIN (%s)' % (mt and mt.group(1), TMIN))
    if TMIN < TENGGANG_OWNER or (mt and int(mt.group(1)) < TENGGANG_OWNER): cacat.append('tenggang minimal di bawah %d hari (keputusan owner 25 Sep: bulan M paling cepat dikunci tanggal %d bulan M+1)' % (TENGGANG_OWNER, TENGGANG_OWNER + 1))
    if 'wib().day() <= tenggangMin()' not in F.get('bebas', '') or 'b >= bulanIni()' not in F.get('bebas', ''): cacat.append('bebas() bukan "bulan berjalan atau masa tenggang minimal"')
    if 'wib().day() > tenggangMin()' not in F.get('bolehDikunci', '') or 'b < bulanIni() - 1' not in F.get('bolehDikunci', ''): cacat.append('bolehDikunci() tidak menegakkan tenggang minimal (bulan lalu dikunci sebelum tanggal tenggang, atau bulan berjalan bisa dikunci)')
    # get() dokumen kunci hanya di terkunci(); terkunci() hanya dipanggil bolehBulan() di belakang bebas()
    for n, badan in F.items():
        if 'aturanToko/kunciPeriode' in badan and n != 'terkunci': cacat.append('get() dokumen kunci di luar terkunci(): ' + n)
        if re.search(r'\bterkunci\(', badan) and n not in ('bolehBulan',): cacat.append('terkunci() dipanggil dari ' + n + ' (harus hanya bolehBulan, di belakang bebas)')
    if 'get(/databases/$(database)/documents/aturanToko/kunciPeriode)' not in F.get('terkunci', ''): cacat.append('terkunci() tidak membaca aturanToko/kunciPeriode')
    if rata(F.get('bolehBulan', '')) != 'return bebas(b) || !terkunci(b);': cacat.append('bolehBulan() bukan "bebas(b) || !terkunci(b)" — get() bisa terpanggil untuk bulan berjalan: ' + rata(F.get('bolehBulan', '')))
    if 'terkunci' in F.get('tglStaf', '') or 'bolehBulan' in F.get('tglStaf', '') or 'bebas(' not in F.get('tglStaf', ''): cacat.append('tglStaf() membaca dokumen kunci (bukan-owner jadi 2 access call per dokumen) atau tidak menilai tanggal')
    if 'resource.data' not in F.get('tglUbah', '').replace('request.resource.data', '') or 'lebihTua(' not in F.get('tglUbah', ''): cacat.append('tglUbah() tidak menilai tanggal LAMA (koreksi di tempat pada bulan terkunci lolos)')
    if 'bonTanggal' not in F.get('bulanUP', ''): cacat.append('bulanUP(): bon lama pemasok tidak dinilai dari bonTanggal (K4)')
    for fn in ('tglLama', 'upLama'):
        if not rata(F.get(fn, '')).startswith('return resource == null || bolehBulan('): cacat.append(fn + '(): hapus dokumen yang TIDAK ADA ditolak (resource null) — satu hapus kantong id+1 yang tidak ada menggagalkan seluruh batch')
    for n, f in sorted(KOL.items()):
        b = B.get(n, '')
        if not b: cacat.append('koleksi bertanggal tanpa blok: ' + n); continue
        up = n == 'utangPemasokMutasi'; baru, ubah, lama = ('upBaru()', 'upUbah()', 'upLama()') if up else ("tglBaru('%s')" % f, "tglUbah('%s')" % f, "tglLama('%s')" % f)
        if n == 'pengaturan': baru, lama = "(id != 'titikKas' || tglBaru('%s'))" % f, "(id != 'titikKas' || tglLama('%s'))" % f
        for op, wajib in (('create', baru), ('update', ubah if n != 'pengaturan' else baru), ('delete', lama)):
            xs = allow(b, op)
            if not xs: cacat.append(n + ': tidak ada allow ' + op); continue
            for x in xs:
                for suku in suku_atas(x):
                    # kasir@ (kasir darurat): create dinilai kunci seperti owner (tglBaru, ≤ 1 get per permintaan satu dokumen); update HANYA tulis-ulang identik; TIDAK PERNAH hapus
                    if 'kasir()' in suku and op == 'delete': cacat.append('%s: kasir@ boleh menghapus catatan bertanggal: %s' % (n, suku)); continue
                    if 'kasir()' in suku and op == 'update':
                        if re.sub(r'^\((.*)\)$', r'\1', rata(suku)) != 'kasir() && tulisUlangSama()': cacat.append('%s: update kasir@ bukan tulis-ulang identik: %s' % (n, suku))
                        continue
                    if re.search(r'\bstaf\w*\(', suku):
                        if "tglStaf('%s')" % f not in suku: cacat.append('%s: %s bukan-owner tanpa tglStaf(%s): %s' % (n, op, f, suku))
                    elif wajib not in suku: cacat.append('%s: %s tanpa kunci periode (%s): %s' % (n, op, wajib, suku))
    for n in ('pajakSetoran', 'pajakOmzetLuar'):
        if re.search(r'tgl(Baru|Ubah|Lama)|bolehBulan|up(Baru|Ubah|Lama)', B.get(n, '')): cacat.append(n + ' ikut dikunci — keputusan owner K6: tidak dikunci')
    lain = [n for n, b in B.items() if n not in KOL and re.search(r'tgl(Baru|Ubah|Lama)\(', b)]
    if lain: cacat.append('koleksi di luar KP_KOLEKSI memakai kunci tanggal (rules & kunci-periode.js harus sama): ' + ', '.join(lain))
    at = B.get('aturanToko', '')
    if not any("id != 'kunciPeriode' || kunciPertama()" in x for x in allow(at, 'create')): cacat.append('aturanToko: create kunciPeriode tanpa kunciPertama()')
    if not any("id != 'kunciPeriode' || kunciGeser()" in x for x in allow(at, 'update')): cacat.append('aturanToko: update kunciPeriode tanpa kunciGeser()')
    if not any(rata(x) == "if owner() && id != 'kunciPeriode'" for x in allow(at, 'delete')): cacat.append('aturanToko: dokumen kunci bisa dihapus')
    kg = rata(F.get('kunciGeser', ''))
    if '(lama.size() == 0 || d.riwayat[0:lama.size()] == lama)' not in kg: cacat.append('kunciGeser(): irisan riwayat lama tanpa penjaga kosong — list[0:0] GALAT di server (Playground 25 Sep, Index -1), owner tidak bisa kunci/buka bila riwayat kosong')
    for syarat, arti in (('d.riwayat[0:lama.size()] == lama', 'riwayat lama boleh ditulis ulang'), ('d.riwayat.size() == lama.size() + 1', 'riwayat tidak bertambah tepat satu'),
                         ('bulanDari(d.sampaiBulan) == bulanDari(s0) + 1', 'kunci boleh melompati bulan'), ('bulanDari(d.sampaiBulan) == bulanDari(s0) - 1', 'buka boleh lebih dari satu bulan'),
                         ('alasan.size() >= 10', 'buka tanpa alasan ≥ 10 huruf'), ('olehUid == request.auth.uid', 'entri riwayat tanpa uid penulis'), ('bolehDikunci(bulanDari(d.sampaiBulan))', 'kunci tanpa tenggang')):
        if syarat not in kg: cacat.append('kunciGeser(): ' + arti)
    if 'bolehDikunci(' not in F.get('kunciPertama', '') or "aksi == 'kunci'" not in F.get('kunciPertama', ''): cacat.append('kunciPertama(): kunci pertama tanpa tenggang / tanpa entri kunci')
    return cacat


def periksa(rules, koleksi_js, akses_js):
    cacat = []
    rules = tanpa_komentar(rules)
    KOL = re.findall(r"\{ nama: '(\w+)',", koleksi_js); B = blok_rules(rules); F = fungsi_rules(rules)
    BACA = daftar_js(akses_js, 'BACA_STAF') or []; DOK = peta_js(akses_js, 'DOK_STAF') or {}; BUAT = peta_js(akses_js, 'BUAT_STAF') or {}
    KREDIT = daftar_js(akses_js, 'KREDIT_STAF') or []
    UBAH = dict((k, re.findall(r"'(\w+)'", v)) for k, v in re.findall(r"(\w+): \{ peran: \[([^\]]*)\]", (re.search(r'export const UBAH_STAF = \{(.*?)\n\};', akses_js, re.S) or re.search('', '')).group(0)))
    # 1 · blok per koleksi
    for n in KOL + ['aksesAkun', 'permintaanAkses', 'arsipTahun']:
        if n not in B: cacat.append('koleksi tanpa blok match sendiri: ' + n)
    # 2 · owner via email, tidak ada masuk() telanjang
    if not re.search(r"function owner\(\) \{\s*return masuk\(\) && request\.auth\.token\.email == '" + re.escape(EMAIL_OWNER) + r"';\s*\}", rules): cacat.append('owner() tidak lagi berbasis email owner')
    if not re.search(r"function kasir\(\) \{\s*return masuk\(\) && request\.auth\.token\.email == '" + re.escape(EMAIL_KASIR) + r"';\s*\}", rules): cacat.append('kasir() tidak lagi berbasis email kasir@')
    for n, b in B.items():
        for x in re.finditer(r'allow [a-z, ]+: if (.*?);', b, re.S):
            k = re.sub(r'\s+', ' ', x.group(1))
            if re.search(r'(^|\|\| )masuk\(\)( \|\||$)', k): cacat.append(n + ': allow memakai masuk() saja (siapa pun yang login): ' + k)
    # 3 · jalur kasir@ v2
    for n in ['penjualan', 'piutangMutasi', 'stokBahanLiteran']:
        b = B.get(n, '')
        if not any('kasir()' in x for x in allow(b, 'create')): cacat.append('jalur kasir@ hilang: create ' + n)
        if not any('kasir() && tulisUlangSama()' in x for x in allow(b, 'update')): cacat.append('jalur kasir@ hilang: tulis-ulang-sama ' + n)
    if not any('kasir()' in x for x in allow(B.get('logAktivitas', ''), 'create')): cacat.append('jalur kasir@ hilang: create logAktivitas')
    if not any('kasir()' in x for x in allow(B.get('perangkatStatus', ''), 'update')): cacat.append('jalur kasir@ hilang: denyut perangkatStatus')
    if not any('kasir()' in x for x in allow(B.get('ringkasanKasir', ''), 'read')): cacat.append('jalur kasir@ hilang: baca ringkasanKasir')
    if not any("id == 'aksesKasir' && kasir()" in x for x in allow(B.get('pengaturan', ''), 'read')): cacat.append('jalur kasir@ hilang: baca pengaturan/aksesKasir')
    if 'tulisUlangSama' in F and 'masuk()' in F['tulisUlangSama']: cacat.append('tulisUlangSama() masih membuka untuk siapa pun yang login (v2) — harus lewat kasir()')
    # 4 · tulis bukan-owner wajib jujur; tidak ada delete bukan-owner
    if 'jujur()' not in F.get('stafBuat', '') or 'request.resource.data.olehUid == request.auth.uid' not in F.get('jujur', ''): cacat.append('stafBuat() tidak memeriksa olehUid (jujur)')
    if 'stafBuat(' not in F.get('stafBuatTipe', ''): cacat.append('stafBuatTipe() tidak lewat stafBuat()')
    if 'jujur()' not in F.get('stafBuatJual', ''): cacat.append('stafBuatJual() tidak memeriksa olehUid')
    if 'stafBuat(' not in F.get('stafJejak', ''): cacat.append('stafJejak() tidak lewat stafBuat()')
    if 'diubahOlehUid == request.auth.uid' not in F.get('stafUbahPesanan', '') or 'affectedKeys().hasOnly(' not in F.get('stafUbahPesanan', ''): cacat.append('stafUbahPesanan() tanpa uid pengubah / tanpa batas kolom')
    if 'akunUid == request.auth.uid' not in F.get('stafDenyut', '') or 'keys().hasOnly(' not in F.get('stafDenyut', ''): cacat.append('stafDenyut() tanpa uid / tanpa batas kolom')
    if 'aktifDengan(' not in F.get('staf', '') or "a.aktif == true" not in F.get('aktifDengan', ''): cacat.append('staf() tidak memeriksa aktif & peran')
    for n, b in B.items():
        for op in ('create', 'update'):
            for x in allow(b, op):
                pakai = set(re.findall(r'\b(staf\w*)\(', x))
                if pakai and not pakai <= FUNGSI_JUJUR: cacat.append(n + ': ' + op + ' bukan-owner lewat fungsi tanpa uid penulis: ' + ', '.join(sorted(pakai - FUNGSI_JUJUR)))
        for x in allow(b, 'delete'):
            k = re.sub(r'\s+', ' ', x).strip()
            if not (k == 'if owner()' or k.startswith('if owner() && ')) or re.search(r'\b(staf\w*|kasir|masuk)\(', k): cacat.append(n + ': delete bukan hanya owner: ' + x)
    if [re.sub(r'\s+', ' ', x).strip() for x in allow(B.get('arsipTahun', ''), 'read')] != ['if owner()']: cacat.append('arsipTahun bukan owner saja')
    # 7 · tanpa payung (putaran 25): tidak ada match rekursif yang memberi tulis, tidak ada wildcard koleksi
    for m in re.finditer(r'\n(\s*)match (/[^\n{]*(?:\{[^}\n]*\}[^\n{]*)*)\{', rules):
        jalur = m.group(2).strip()
        if re.search(r'=\*\*\}', jalur):
            i = m.end(); d = 1
            while i < len(rules) and d: d += {'{': 1, '}': -1}.get(rules[i], 0); i += 1
            isi = rules[m.end():i]
            if re.search(r'allow [a-z, ]*(write|create|update|delete)', isi): cacat.append('match rekursif memberi izin tulis (payung): ' + jalur)
            else: cacat.append('match rekursif (bentuk payung) di rules: ' + jalur)
        elif re.match(r'^/\{\w+\}/', jalur): cacat.append('wildcard koleksi: ' + jalur)
    cacat += periksa_kunci(rules, B, F)
    # 5 · daftar peran sama dengan akses.js
    peran_txt = "['ben', 'karyawan']"
    for n in KOL:
        b = B.get(n, ''); baca_staf = any("staf(" + peran_txt + ")" in x for x in allow(b, 'read'))
        if n in BACA and not baca_staf: cacat.append('akses.js BACA_STAF memuat ' + n + ' tapi rules tidak membuka bacanya untuk ben/karyawan')
        if n not in BACA and n not in DOK and baca_staf: cacat.append('rules membuka baca ' + n + ' untuk bukan-owner, akses.js BACA_STAF tidak')
        buat = [x for x in allow(b, 'create') if re.search(r'\bstaf\w*\(', x)]
        if n in BUAT and not any(peran_txt in x for x in buat): cacat.append('akses.js BUAT_STAF memuat ' + n + ' tapi rules tidak membuka create-nya')
        if n not in BUAT and buat: cacat.append('rules membuka create ' + n + ' untuk bukan-owner, akses.js BUAT_STAF tidak')
        ubah = [x for x in allow(b, 'update') if re.search(r'\bstaf\w*\(', x)]
        if n in UBAH and not ubah: cacat.append('akses.js UBAH_STAF memuat ' + n + ' tapi rules tidak membuka update-nya')
        if n not in UBAH and ubah: cacat.append('rules membuka update ' + n + ' untuk bukan-owner, akses.js UBAH_STAF tidak')
    m = re.search(r"id in \[([^\]]*)\] && staf", B.get('aturanToko', ''))
    if not m or re.findall(r"'(\w+)'", m.group(1)) != DOK.get('aturanToko'): cacat.append('dokumen aturanToko yang dibaca bukan-owner beda dengan akses.js DOK_STAF')
    if "id == '" + (DOK.get('pengaturan') or ['?'])[0] + "' && staf(" not in B.get('pengaturan', ''): cacat.append('dokumen pengaturan yang dibaca bukan-owner beda dengan akses.js DOK_STAF')
    if "stafBuatJual(" + peran_txt + ", [" + ', '.join("'%s'" % x for x in KREDIT) + "])" not in B.get('penjualan', ''): cacat.append('peran jual Kredit di rules beda dengan akses.js KREDIT_STAF')
    # putaran 23c: daftar dokumen di baris jejak dibatasi SAMA dengan pagar perangkat akses.js (BATAS_ACCESS_CALL − CADANGAN − 1 jejak)
    fa = re.search(r'export const BATAS_ACCESS_CALL = (\d+);', akses_js); ca = re.search(r'export const CADANGAN_ACCESS_CALL = (\d+);', akses_js)
    mj = re.search(r'd\.dokumen\.size\(\) <= (\d+)', F.get('stafJejak', ''))
    if not (fa and ca and mj) or int(mj.group(1)) != int(fa.group(1)) - int(ca.group(1)) - 1 or int(fa.group(1)) - int(ca.group(1)) > 18:
        cacat.append('stafJejak(): batas dokumen per kiriman (%s) beda dengan pagar akses.js (%s − %s − 1 jejak), atau pagarnya > 18' % (mj and mj.group(1), fa and fa.group(1), ca and ca.group(1)))
    # 6 · aksesAkun tak pernah owner
    ak = B.get('aksesAkun', '')
    if "request.resource.data.peran in ['ben', 'karyawan']" not in ak or 'owner' in re.sub(r'owner\(\)', '', ak): cacat.append('aksesAkun bisa memberi peran selain ben/karyawan (atau menyebut owner)')
    if not any(re.sub(r'\s+', ' ', x).strip().startswith('if owner() &&') for x in allow(ak, 'create')): cacat.append('aksesAkun bisa ditulis selain owner')
    pa = B.get('permintaanAkses', '')
    if 'request.auth.uid == uid' not in pa or '!exists(/databases/$(database)/documents/aksesAkun/$(uid))' not in pa or '!kasir()' not in pa: cacat.append('permintaanAkses: create bukan milik uid sendiri / boleh walau sudah terdaftar / kasir@ boleh')
    return cacat


if __name__ == '__main__':
    R = baca('firestore.rules'); K = baca('baru/js/data/koleksi.js'); A = baca('baru/js/data/akses.js')
    if '--kontrol' in sys.argv:
        rusak = {
            'satu koleksi tanpa blok sendiri': R.replace('    match /karantina/{id} {', '    match /karantinaX/{id} {'),
            'owner lewat dokumen, bukan email': R.replace("return masuk() && request.auth.token.email == 'owner@tokoberasmiqbal.web.app';", "return masuk() && akun().peran == 'owner';"),
            'jalur kasir@ penjualan hilang': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (stafBuatJual(", "allow create: if (owner() && tglBaru('tanggal')) || (stafBuatJual("),
            'jalur kasir@ dibuka lagi untuk siapa pun (v2)': R.replace("    function tulisUlangSama() {\n      return request.resource.data == resource.data;", "    function tulisUlangSama() {\n      return masuk() && request.resource.data == resource.data;"),
            'tulisan bukan-owner tanpa olehUid': R.replace("function stafBuat(peranBoleh) { return masuk() && aktifDengan(akun(), peranBoleh) && jujur(); }", "function stafBuat(peranBoleh) { return masuk() && aktifDengan(akun(), peranBoleh); }"),
            'siapa pun yang login boleh menjual': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (stafBuatJual(", "allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || masuk() || (stafBuatJual("),
            'bukan-owner boleh hapus': R.replace("    match /strukKeluar/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();",
                                                  "    match /strukKeluar/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update: if owner();\n      allow delete: if owner() || staf(['ben', 'karyawan']);"),
            'karyawan membaca koleksi uang': R.replace("    match /pengeluaranHarian/{id} {\n      allow read: if owner();", "    match /pengeluaranHarian/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);"),
            # putaran 23e: payung tidak boleh mengalahkan batasan owner
            # putaran 25 — tanpa payung & kunci periode
            'payung owner dikembalikan (mengalahkan kunci periode)': R.replace("    match /ringkasanKasir/{id} {", "    match /{document=**} {\n      allow read, write: if owner();\n    }\n    match /ringkasanKasir/{id} {"),
            'payung v3 dikembalikan': R.replace("    match /ringkasanKasir/{id} {", "    match /{koleksi}/{sisa=**} {\n      allow read, write: if owner() && !(koleksi in ['aksesAkun', 'permintaanAkses']);\n    }\n    match /ringkasanKasir/{id} {"),
            'kunci dicabut dari create retur': R.replace("    match /retur/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() && tglBaru('tanggal');", "    match /retur/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner();"),
            'hapus nota tanpa kunci': R.replace("      allow delete: if owner() && tglLama('tanggal');\n    }\n\n    match /produksiKemasan/{id} {", "      allow delete: if owner();\n    }\n\n    match /produksiKemasan/{id} {"),
            'koreksi di tempat pada bulan terkunci lolos (update hanya menilai tanggal baru)': R.replace("function tglUbah(f) { return tulisUlangSama() || bolehBulan(lebihTua(bulanDok(request.resource.data, f), bulanDok(resource.data, f))); }", "function tglUbah(f) { return tulisUlangSama() || bolehBulan(bulanDok(request.resource.data, f)); }"),
            'kasir@ create tanpa kunci': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (stafBuatJual(", "allow create: if (owner() && tglBaru('tanggal')) || kasir() || (stafBuatJual("),
            'bukan-owner membaca dokumen kunci (2 access call per dokumen)': R.replace("function tglStaf(f) { return bebas(bulanDok(request.resource.data, f)); }", "function tglStaf(f) { return bolehBulan(bulanDok(request.resource.data, f)); }"),
            'bukan-owner tanpa penilaian tanggal': R.replace("(stafBuatTipe(['ben', 'karyawan'], 'pakai') && tglStaf('tanggal'));   // bukan beli\n      allow update: if owner() && tglUbah('tanggal');", "stafBuatTipe(['ben', 'karyawan'], 'pakai');   // bukan beli\n      allow update: if owner() && tglUbah('tanggal');"),
            'get() kunci selalu dipanggil (let di bolehBulan)': R.replace("function bolehBulan(b) { return bebas(b) || !terkunci(b); }", "function bolehBulan(b) { let k = terkunci(b); return bebas(b) || !k; }"),
            'get() kunci kedua di luar terkunci()': R.replace("function bolehBulan(b) { return bebas(b) || !terkunci(b); }", "function bolehBulan(b) { return bebas(b) || !terkunci(b); }\n    function sudahDikunci() { return exists(/databases/$(database)/documents/aturanToko/kunciPeriode); }"),
            'tenggang minimal 0 (bulan lalu bisa dikunci tanggal 1)': R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 0; }"),
            'tenggang minimal kembali 1 di rules saja (beda dengan kunci-periode.js)': R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 1; }"),
            'kasir@ boleh menghapus nota (dengan kunci pun)': R.replace("      allow delete: if owner() && tglLama('tanggal');\n    }\n\n    match /produksiKemasan/{id} {", "      allow delete: if (owner() || kasir()) && tglLama('tanggal');\n    }\n\n    match /produksiKemasan/{id} {"),
            'kasir@ boleh mengubah nota asal bulannya terbuka (bukan hanya tulis-ulang identik)': R.replace("allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama());", "allow update: if (owner() && tglUbah('tanggal')) || (kasir() && (tulisUlangSama() || tglUbah('tanggal')));", 1),
            'kasir@ boleh mengubah nota (bukan tulis-ulang identik)': R.replace("allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama());", "allow update: if ((owner() || kasir()) && tglUbah('tanggal'));", 1),
            'bulan berjalan bisa dikunci': R.replace("function bolehDikunci(b) { return b < bulanIni() - 1 || (b == bulanIni() - 1 && wib().day() > tenggangMin()); }", "function bolehDikunci(b) { return b < bulanIni(); }"),
            'WIB dihitung sebagai UTC': R.replace("timestamp.value(request.time.toMillis() + 25200000)", "timestamp.value(request.time.toMillis())"),
            'kunci boleh melompati bulan': R.replace("bulanDari(d.sampaiBulan) == bulanDari(s0) + 1", "bulanDari(d.sampaiBulan) > bulanDari(s0)"),
            'buka dua bulan sekaligus': R.replace("bulanDari(d.sampaiBulan) == bulanDari(s0) - 1", "bulanDari(d.sampaiBulan) < bulanDari(s0)"),
            'buka tanpa alasan': R.replace("\n              && d.riwayat[lama.size()].alasan is string && d.riwayat[lama.size()].alasan.size() >= 10));", "));"),
            'riwayat kunci boleh ditulis ulang': R.replace("(lama.size() == 0 || d.riwayat[0:lama.size()] == lama) && ", ""),
            'irisan riwayat tanpa penjaga kosong (galat Index -1 di server)': R.replace("(lama.size() == 0 || d.riwayat[0:lama.size()] == lama)", "d.riwayat[0:lama.size()] == lama"),
            'dokumen kunci bisa dihapus': R.replace("allow delete: if owner() && id != 'kunciPeriode';", "allow delete: if owner();"),
            'pajakSetoran ikut dikunci (melawan K6)': R.replace("    match /pajakSetoran/{id} {\n      allow read, write: if owner();", "    match /pajakSetoran/{id} {\n      allow read: if owner();\n      allow create: if owner() && tglBaru('tanggalSetor');\n      allow update, delete: if owner();"),
            'bon lama pemasok dinilai tanggal catat (melawan K4)': R.replace("function bulanUP(d) { return d.get('tipe', '') == 'saldoAwal' ? bulanNilai(d.get('bonTanggal', null)) : bulanDok(d, 'tanggal'); }", "function bulanUP(d) { return bulanDok(d, 'tanggal'); }"),
            'hapus dokumen yang tidak ada ditolak (batch hapus adukan gagal)': R.replace("function tglLama(f) { return resource == null || bolehBulan(bulanDok(resource.data, f)); }", "function tglLama(f) { return bolehBulan(bulanDok(resource.data, f)); }"),
            'titik kas tanpa kunci': R.replace("allow create, update: if owner() && (id != 'titikKas' || tglBaru('tanggal'));", "allow create, update: if owner();"),
            'wildcard koleksi tambahan di tengah': R.replace("    match /bukuHapus/{id} {", "    match /{apaSaja}/{id} {\n      allow read: if owner();\n    }\n    match /bukuHapus/{id} {"),
            'setelan upah ikut terbaca bukan-owner': R.replace("'peran', 'perangkat'] && staf(", "'peran', 'perangkat', 'upah'] && staf("),
            'aksesAkun bisa memberi owner': R.replace("request.resource.data.peran in ['ben', 'karyawan'] && request.resource.data.aktif is bool", "request.resource.data.peran in ['ben', 'karyawan', 'owner'] && request.resource.data.aktif is bool"),
            'update pesanan tanpa batas kolom': R.replace("&& request.resource.data.diff(resource.data).affectedKeys().hasOnly(['status', 'riwayatStatus', 'trxIdJual', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada']);", ";"),
            'karyawan boleh jual Kredit di rules': R.replace("stafBuatJual(['ben', 'karyawan'], ['ben'])", "stafBuatJual(['ben', 'karyawan'], ['ben', 'karyawan'])"),
            'arsipTahun dibuka': R.replace("allow read, write: if owner();   // arsip tutup buku: owner saja", "allow read: if owner() || staf(['ben', 'karyawan']);\n      allow write: if owner();"),
            'permintaanAkses boleh walau sudah terdaftar': R.replace("  && !exists(/databases/$(database)/documents/aksesAkun/$(uid))\n", ""),
            'jejak bukan-owner boleh 19 dokumen (batas lama, tanpa sisa)': R.replace("d.dokumen.size() <= 17;", "d.dokumen.size() <= 19;"),
            'create lewat staf() tanpa uid': R.replace("(stafBuat(['ben', 'karyawan']) && tglStaf('tanggal'));   // adukan", "(staf(['ben', 'karyawan']) && tglStaf('tanggal'));   // adukan"),
        }
        kode = 0
        KPJ = baca('baru/js/data/kunci-periode.js')
        rusak['tenggang minimal 1 di rules DAN kunci-periode.js (di bawah keputusan owner 3 hari)'] = (R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 1; }"),
                                                                                                   KPJ.replace('export const KP_TENGGANG_MIN = 3;', 'export const KP_TENGGANG_MIN = 1;'))
        for nama, isi in rusak.items():
            KP_TEKS = None
            if isinstance(isi, tuple):
                isi, KP_TEKS = isi
                if KP_TEKS == KPJ: print('KONTROL BASI  ' + nama); kode = 3; continue
            if isi == R: print('KONTROL BASI  ' + nama); kode = 3; continue
            c = periksa(isi, K, A)
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:110] if c else '-'))
            if not c: kode = 3
        sys.exit(kode)
    c = periksa(R, K, A)
    B = blok_rules(R)
    if c: print('RULES v4 CACAT (%d):' % len(c)); [print('   ✗ ' + x) for x in c]; sys.exit(2)
    KOL, TMIN = kp_js()
    print('RULES v4 LULUS: %d blok koleksi · TANPA payung (tidak ada match rekursif / wildcard koleksi) · owner via email · jalur kasir@ utuh & dipersempit · '
          'tulis bukan-owner wajib uid · daftar peran = akses.js · kunci periode di %d koleksi bertanggal (= kunci-periode.js), tenggang minimal %d hari, '
          'satu get() dokumen kunci per operasi, bukan-owner tanpa get() kunci, pajak tidak dikunci (K6)' % (len(B), len(KOL), TMIN))
