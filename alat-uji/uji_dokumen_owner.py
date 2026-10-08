#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_dokumen_owner.py — DOKUMEN PEGANGAN OWNER sesudah 13 Okt 2026 (audit kesiapan 2027 · P6, sanggahan PR #118). jsc (kotak pasir, ANGKA CONTOH) + statis.

Sesudah 13 Okt owner bekerja sendiri dari dokumen. Yang dijaga: angka & keputusan yang TERTULIS menutup dengan kode yang dirujuknya.
  D1 proyeksi kuota tutup buku 2027 (Januari 2028) di docs/uji-rules-v7.md & docs/gladi-tutup-buku.md:
     · rumus kartu "Perkiraan kuota Firestore" (tutup-buku-logika.js perkiraanKuota) DIJALANKAN di jsc atas kotak pasir setahun yang Januari–Novembernya
       TERKUNCI (jalur pintu — mekanisme yang sama dengan tutup buku 2027 di Januari 2028): tulis / hapus / baca per catatan = selisih dua ukuran kotak
       (480 & 960 catatan contoh) ÷ 480;
     · per catatan, persen batas Spark, dan hari kuota yang ditulis untuk "±A–B rb catatan" = hasil rumus itu (selisih ≤ 4% / 6 poin); A–B = laju
       catatan sehari × 365; "±2,5–3×" = A–B ÷ skala 117% (±17 rb), dan skala itu disebut catatan 2026 SAJA (8 Agu–31 Des);
     · bunyi K11 = DICABUT 9 Okt 2026 (owner, Blaze aktif): ritual 1 Jan DINI HARI sesudah tutup hari 31 Des (K3, owner 9 Okt), MEPET / TIDAK MUAT di kartu boleh diabaikan, sebabnya = kelebihan kuota
       DITAGIH (bukan ditolak) — tanpa perintah lama "toko tutup sesudahnya sampai Lanjutkan & arsip habis"; juga di baru/BACA-DULU.md bagian K9–K12.
  D2 K9 (modal awal 8 Agu, baru/BACA-DULU.md): menyebut tempat kodenya (PR #121, LP_KALIMAT_MODAL_AWAL) DAN jalan sementara owner bila kalimatnya TIDAK
     tercetak (sampaikan sendiri ke konsultan bersama PDF Neraca 31 Des). Bila konstanta itu SUDAH ada di kode: isinya memuat "8 Agu 2026" & "konsultan" dan
     dipakai berita acara (tutup-buku-logika.js teksAcara) & laporan-logika.js — kalau belum ada: dicatat "belum di kode", jalan sementaranya wajib tertulis.
  D3 jalur Menu di docs/uji-rules-v7.md, docs/uji-rules-v6.md, docs/rancangan-hemat-baca.md = laci "Toko ini" + baris & tab yang ADA (menu.js JUDUL_SISTEM,
     TAB_SISTEM); tanpa "Menu › Sistem".
  D4 docs/peta-pindahan-terakhir.md §9: jalan katalog kasir menyebut tombol TERBITKAN yang ada di harga.js dan jeda ±4 detik = KK_JEDA_MS; tanpa "tidak ada
     tombol manual".
  D5 kiriman tutup buku DITOLAK: langkahnya ada di docs/uji-rules-v7.md (bukan hanya di berkas sejarah v6, yang tidak lagi menyebut "tetap berlaku").
  D6 docs/peta-kunci-periode.md §10: "Agustus tidak pernah dikunci" bersandar pada kunci pertama Januari 2027 SESUDAH tutup buku 2026 (KP_KUNCI_MULAI di kode).

    python3 alat-uji/uji_dokumen_owner.py            → N lulus · 0 gagal
    python3 alat-uji/uji_dokumen_owner.py --kontrol  → kerusakan wajib ketahuan KARENA sebabnya (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, math
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode, uji_tutup_buku_bertahap, uji_uang_baru  # noqa: E402

V7 = 'docs/uji-rules-v7.md'; V6 = 'docs/uji-rules-v6.md'; GLADI = 'docs/gladi-tutup-buku.md'; BACA = 'baru/BACA-DULU.md'; HB = 'docs/rancangan-hemat-baca.md'
PINDAH = 'docs/peta-pindahan-terakhir.md'; KUNCI = 'docs/peta-kunci-periode.md'
MENU = 'baru/js/layar/menu.js'; MENU_L = 'baru/js/layar/menu-logika.js'; HARGA = 'baru/js/layar/harga.js'; KK = 'baru/js/data/katalog-kasir.js'
LL = 'baru/js/layar/laporan-logika.js'; TB = 'baru/js/layar/tutup-buku-logika.js'; KP = 'baru/js/data/kunci-periode.js'
MODUL = uji_tutup_buku_bertahap.MODUL
BERKAS = sorted(set([V7, V6, GLADI, BACA, HB, PINDAH, KUNCI, MENU, MENU_L, HARGA, KK] + MODUL))
UKURAN = (480, 960)   # catatan contoh di kotak; rasio = selisih ÷ 480 (bagian tetap — pembuka, aturan, muat kotak — saling hapus)


def baca(ganti=None):
    """{berkas: isi}. ganti = {berkas: [(lama, baru)]} untuk kontrol (lama wajib muncul tepat sekali)."""
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in BERKAS)
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:90] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


# ============================== D1 · rumus kartu di jsc ==============================
SKENARIO = r"""
(function () {
function salin(x) { return JSON.parse(JSON.stringify(x)); }
var hasil = { batas: BATAS_SPARK, ukuran: {} };
__UKURAN__.forEach(function (N) {
  KOLEKSI.forEach(function (k) { pasok(k.nama, []); }); Object.keys(KOTAK).forEach(function (n) { pasok(n, salin(KOTAK[n])); });
  var c = [];
  // nota contoh merata Januari–Desember 2026
  for (var i = 0; i < N; i++) {
    var t = '2026-' + String(1 + (i % 12)).padStart(2, '0') + '-' + String(1 + (i % 27)).padStart(2, '0');
    c.push({ koleksi: 'penjualan', data: { id: 'kx' + i, tanggal: t, jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 5, beratKarungAcuan: 50, jumlahKarung: 0.1, hargaTotal: 70000, hppTotalSaatJual: 65000 } });
  }
  terapkanKeCache(c);
  // Januari–November TERKUNCI (jalur pintu v7); tutup buku dimulai 1 Jan sesudah reset kuota — Desember masih dalam tenggang
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-11', riwayat: [] } }]);
  __KINI = new Date('2027-01-01T15:30:00+07:00').getTime();
  var K = perkiraanKuota(2026, new Date(__KINI));
  hasil.ukuran[N] = { nArsip: K.nArsip, muat: K.muat, ritual: K.ritual };
});
print(JSON.stringify(hasil));
})();
"""


def rumus_kartu(t):
    js = uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]))
    prog = uji_tutup_buku_bertahap.JAM + js + '\nvar KOTAK = ' + json.dumps(uji_uang_baru.KOTAK) + ';\n' + SKENARIO.replace('__UKURAN__', json.dumps(list(UKURAN)))
    h, e = uji_tutup_buku_bertahap.jalan(prog)
    if h is None: return None, e
    a, b = h['ukuran'][str(UKURAN[0])], h['ukuran'][str(UKURAN[1])]; d = float(UKURAN[1] - UKURAN[0])
    r = dict((k, (b['ritual'][k] - a['ritual'][k]) / d) for k in ('tulis', 'hapus', 'baca'))
    return {'r': r, 'batas': h['batas'], 'arsip': (b['nArsip'] - a['nArsip']) / d}, ''


def paragraf(teks):
    """Paragraf (dipisah baris kosong), baris disatukan & tanda kutip '>' dibuang — kalimat yang terbelah baris tetap terbaca."""
    return [re.sub(r'\s+', ' ', re.sub(r'(^|\n)> ?', r'\1', p)).strip() for p in re.split(r'\n\s*\n', teks)]


def angka(s): return float(s.replace(',', '.'))


def butir(teks, awal, akhir):
    i = teks.find(awal); j = teks.find(akhir, i + 1) if i >= 0 else -1
    return re.sub(r'\s+', ' ', teks[i:j]) if i >= 0 and j > i else ''


def periksa_k11(ok, nama, s):
    # owner 9 Okt 2026: Blaze aktif → K11 (toko tutup sesudah ritual karena kuota) DICABUT; kartu kuota tidak diubah kodenya (TIDAK MUAT boleh diabaikan)
    ok(nama + ': bunyi K11 = DICABUT 9 Okt 2026 (Blaze) — ritual dini hari sesudah tutup hari 31 Des (K3), MEPET / TIDAK MUAT boleh diabaikan, tanpa perintah "toko tutup sesudahnya"',
       'DICABUT 9 Okt 2026' in s and 'Blaze' in s and 'dini hari' in s and 'jam bebas' not in s and bool(re.search(r'TIDAK MUAT[^.;]{0,25}boleh diabaikan', s))
       and not re.search(r'toko tutup sesudahnya sampai Lanjutkan', s), s[:300])
    ok(nama + ': K11 menyebut sebabnya — kelebihan kuota DITAGIH (bukan ditolak), jadi arsip tidak berhenti karena kuota',
       'kelebihannya ditagih' in s and 'tidak berhenti' in s and 'karena kuota' in s, s[:300])


def periksa(t):
    out = []; ok = lambda n, c, k='': out.append((n, bool(c), k))
    # ---- D1 · rumus kartu
    R, e = rumus_kartu(t)
    ok('D1 rumus kartu Perkiraan kuota dijalankan di jsc (kotak setahun, Januari–November terkunci)', R is not None, e[:300])
    if R:
        r = R['r']
        ok('D1 kotak memakai jalur pintu: tiap catatan contoh ikut diarsip, hapus tepat 1 per catatan, baca ≥ 4 per catatan (5 pemeriksaan server per catatan bulan terkunci)',
           R['arsip'] == 1 and abs(r['hapus'] - 1) < 1e-9 and r['baca'] >= 4 and 1.1 <= r['tulis'] <= 1.6, R)
    for berkas in (V7, GLADI):
        P = paragraf(t[berkas])
        p117 = next((p for p in P if '117%' in p and '23,5 rb' in p), '')
        m17 = re.search(r'skala ±(\d+) rb catatan', p117)
        ok('D1 ' + berkas + ': 117% disebut skala ±17 rb catatan = catatan 2026 SAJA (8 Agu–31 Des), bukan setahun penuh',
           m17 and 'catatan 2026 SAJA (8 Agu–31 Des)' in p117, p117[:300])
        ps = next((p for p in P if re.search(r'(?i)setahun penuh', p) and re.search(r'±\d+–\d+ rb catatan', p)), '')
        ok('D1 ' + berkas + ': ada proyeksi SETAHUN PENUH 2027 (tutup buku Januari 2028) dengan "BEBERAPA hari kuota" dan rujukan ke kartu di hari itu',
           ps and 'BEBERAPA hari kuota, bukan satu' in ps and 'Perkiraan kuota Firestore' in ps, ps[:200])
        mN = re.search(r'±(\d+)–(\d+) rb catatan', ps); mL = re.search(r'±(\d+)–(\d+) catatan sehari', ps); mX = re.search(r'±(\d+(?:,\d+)?)–(\d+(?:,\d+)?)× skala', ps)
        mR = re.search(r'tulis ±(\d+(?:,\d+)?) · hapus (\d+(?:,\d+)?) · baca ±(\d+(?:,\d+)?)', ps)
        mP = dict((k, re.search(k + r' \*\*±(\d+)–(\d+)%\*\*', ps)) for k in ('tulis', 'hapus', 'baca'))
        mH = re.search(r'tulis & hapus saja ±(\d+)–(\d+) hari', ps); mB = re.search(r'baca menurut kartu \(perkiraan atas\) ±(\d+)–(\d+) hari', ps)
        semua = all([mN, mL, mX, mR, mH, mB, m17] + list(mP.values()))
        ok('D1 ' + berkas + ': angka proyeksi setahun penuh terbaca (rb catatan, catatan sehari, kali skala, per catatan, persen tulis/hapus/baca, hari kuota)', semua,
           [bool(x) for x in [mN, mL, mX, mR, mH, mB, m17] + list(mP.values())])
        if not (semua and R): continue
        n = (int(mN.group(1)), int(mN.group(2))); lj = (int(mL.group(1)), int(mL.group(2))); s17 = int(m17.group(1))
        ok('D1 ' + berkas + ': ±%d–%d rb catatan = laju ±%d–%d catatan sehari × 365' % (n + lj), all(abs(n[i] - lj[i] * 365 / 1000.0) <= 1 for i in (0, 1)), [x * 365 for x in lj])
        ok('D1 ' + berkas + ': "±%s–%s×" = rb catatan ÷ skala %d rb' % (mX.group(1), mX.group(2), s17),
           all(abs(angka(mX.group(i + 1)) - n[i] / float(s17)) <= 0.1 for i in (0, 1)), [round(x / float(s17), 2) for x in n])
        rt = dict(zip(('tulis', 'hapus', 'baca'), [angka(mR.group(i)) for i in (1, 2, 3)]))
        ok('D1 ' + berkas + ': per catatan yang ditulis = rumus kartu (tulis ±%.2f · hapus %.2f · baca ±%.2f)' % (R['r']['tulis'], R['r']['hapus'], R['r']['baca']),
           all(abs(rt[k] - R['r'][k]) <= 0.06 for k in rt), [rt, R['r']])
        pr = dict((k, [R['r'][k] * x * 1000.0 / R['batas'][k] * 100 for x in n]) for k in mP)
        tl = lambda x: max(6.0, 0.04 * x)
        salah = ['%s ±%s–%s%% ≠ rumus %.0f–%.0f%%' % (k, mP[k].group(1), mP[k].group(2), pr[k][0], pr[k][1]) for k in mP
                 if any(abs(int(mP[k].group(i + 1)) - pr[k][i]) > tl(pr[k][i]) for i in (0, 1))]
        ok('D1 ' + berkas + ': persen batas Spark sehari untuk ±%d–%d rb catatan = rumus kartu (selisih ≤ 4%% / 6 poin)' % n, not salah, salah)
        hari = lambda xs: set(int(math.ceil((x + d) / 100.0)) for x in xs for d in (-tl(x), 0, tl(x)))
        th = [max(pr['tulis'][i], pr['hapus'][i]) for i in (0, 1)]
        ok('D1 ' + berkas + ': hari kuota yang ditulis = persen ÷ 100 dibulatkan ke atas (tulis & hapus %d–%d hari, baca %d–%d hari)' % (
            math.ceil(th[0] / 100.0), math.ceil(th[1] / 100.0), math.ceil(pr['baca'][0] / 100.0), math.ceil(pr['baca'][1] / 100.0)),
            int(mH.group(1)) in hari([th[0]]) and int(mH.group(2)) in hari([th[1]]) and int(mB.group(1)) in hari([pr['baca'][0]]) and int(mB.group(2)) in hari([pr['baca'][1]]),
            [mH.group(0), mB.group(0), th, pr['baca']])
        pk = next((p for p in P if 'Keputusan owner K11' in p), '')
        periksa_k11(ok, 'D1 ' + berkas, pk)
    periksa_k11(ok, 'D1 ' + BACA + ' (K9–K12)', butir(t[BACA], '- **K11**', '- **K12**'))
    # ---- D2 · K9 modal awal
    k9 = butir(t[BACA], '- **K9**', '- **K10**')
    ok('D2 K9: tidak lagi "pekerjaan kode tersendiri" tanpa pengerja — menyebut PR #121 & LP_KALIMAT_MODAL_AWAL', k9 and 'pekerjaan kode tersendiri' not in k9 and 'PR #121' in k9 and 'LP_KALIMAT_MODAL_AWAL' in k9, k9[:300])
    ok('D2 K9: jalan sementara owner tertulis — kalimat TIDAK tercetak → sampaikan sendiri ke konsultan bersama PDF Neraca 31 Des (docs/prosedur-pulih-darurat.md)',
       all(x in k9 for x in ('TIDAK tercetak', 'konsultan bersama PDF Neraca 31 Des', 'prosedur-pulih-darurat.md')), k9[:400])
    mK = re.search(r"export const LP_KALIMAT_MODAL_AWAL = '([^']*)'", t[LL])
    if mK:
        i = t[TB].find('export function teksAcara('); j = t[TB].find('\nexport function', i + 1)
        ok('D2 K9 (kalimat SUDAH di kode): isinya memuat "8 Agu 2026" & "konsultan" (keputusan owner 8 Okt)', '8 Agu 2026' in mK.group(1) and 'konsultan' in mK.group(1), mK.group(1))
        ok('D2 K9 (kalimat SUDAH di kode): dipakai berita acara tutup buku (teksAcara) dan di laporan-logika.js (Neraca berkop) — bukan hanya dideklarasikan',
           i >= 0 and 'LP_KALIMAT_MODAL_AWAL' in t[TB][i:j] and t[LL].count('LP_KALIMAT_MODAL_AWAL') >= 2, [i, t[LL].count('LP_KALIMAT_MODAL_AWAL')])
    else:
        ok('D2 K9: kalimat belum di kode (PR #121 belum digabung) — jalan sementara di atas yang berlaku', 'TIDAK tercetak' in k9)
    # ---- D3 · jalur Menu
    jm = re.search(r'const JUDUL_SISTEM = \{([^}]*)\}', t[MENU]); tm = re.search(r'const TAB_SISTEM = \{(.*?)\};', t[MENU])
    judul = dict(re.findall(r"(\w+): '([^']+)'", jm.group(1))) if jm else {}
    tab = dict((k, re.findall(r"\['\w+', '([^']+)'\]", v)) for k, v in re.findall(r"(\w+): \[((?:\[[^\]]*\],? ?)*)\]", tm.group(1))) if tm else {}
    ok('D3 menu.js: JUDUL_SISTEM & TAB_SISTEM terbaca; laci "Toko ini" ada di menu-logika.js', judul and tab and "nama: 'Toko ini'" in t[MENU_L], [judul, tab])
    for berkas in (V7, V6, HB):
        s = ' '.join(paragraf(t[berkas]))
        ok('D3 ' + berkas + ': tanpa jalur "Menu › Sistem" (laci itu tidak ada di layar)', 'Menu › Sistem' not in s, re.findall(r'Menu › Sistem[^.;)]{0,40}', s))
        salah = []
        for m in re.finditer(r'Menu › Toko ini › ', s):
            sisa = s[m.end():]; k = next((k for k, v in sorted(judul.items(), key=lambda x: -len(x[1])) if sisa.startswith(v)), None)
            if k is None: salah.append(sisa[:40]); continue
            sisa = sisa[len(judul[k]):]
            if sisa.startswith(' › ') and not any(sisa[3:].startswith(x) for x in tab.get(k, [])): salah.append(judul[k] + ' › ' + sisa[3:30])
        ok('D3 ' + berkas + ': tiap "Menu › Toko ini › …" = baris & tab yang ADA (menu.js)', not salah, salah)
    # ---- D4 · katalog kasir
    s9 = ' '.join(paragraf(butir(t[PINDAH], '## 9. Jalan mundur', '\nKatalog (`ringkasanKasir/aktif`)')))
    ok('D4 §9: jalan katalog kasir menyebut tombol TERBITKAN … HARGA (ada di harga.js) dan katalog ikut kiriman terbit yang sama',
       'TERBITKAN … HARGA' in s9 and 'ikut di kiriman terbit yang sama' in s9 and "'TERBITKAN ' + P.n + ' HARGA" in t[HARGA], s9[:200])
    ok('D4 §9: tanpa "tidak ada tombol manual" (dulu dibaca: membetulkan draf sudah cukup)', s9 and 'tidak ada tombol manual' not in s9 and 'tidak ada tombol terpisah untuk katalog kasir' in s9)
    ok('D4 §9: "±4 detik" = KK_JEDA_MS katalog-kasir.js', '±4 detik' in s9 and 'export const KK_JEDA_MS = 4000;' in t[KK])
    # ---- D5 · kiriman tutup buku ditolak
    s5 = ' '.join(paragraf(butir(t[V7], '## Kalau kiriman tutup buku DITOLAK server', '\n## ')))
    ok('D5 ' + V7 + ': langkah kiriman tutup buku DITOLAK ada (permission-denied, jangan tulis ulang, jam perangkat, Lanjutkan, Batalkan) tanpa tempel rules lama',
       all(x in s5 for x in ('permission-denied', 'Jangan tulis ulang kiriman tutup buku yang ditolak', 'jam perangkat', 'Lanjutkan', 'Batalkan', 'jangan tempel rules lain'))
       and not re.search(r'tempel `firestore\.rules\.v[56]` (dari|lalu)', s5), s5[:200])
    s6 = butir(t[V6], '## Kalau sesudah v6 terbit tutup buku DITOLAK', '\n## ')
    ok('D5 ' + V6 + ': berkas sejarah tidak lagi menyebut langkahnya "tetap berlaku" dan menunjuk bagian v7', s6 and 'tetap berlaku' not in s6 and 'Kalau kiriman tutup buku DITOLAK server' in s6, s6[:300])
    # ---- D6 · Agustus tidak pernah dikunci
    s10 = ' '.join(paragraf(butir(t[KUNCI], '## 10. Cara bayar kedatangan', '\n## ')))
    ok('D6 §10: "Agustus tidak pernah dikunci" bersandar pada kunci pertama Januari 2027 SESUDAH tutup buku 2026 mengarsip catatan Agustus (KP_KUNCI_MULAI = 2027-01 di kode)',
       'kunci pertama = Januari 2027' in s10 and 'sesudah tutup buku 2026 mengarsip catatan Agustus' in s10 and "export const KP_KUNCI_MULAI = '2027-01';" in t[KP], s10[:200])
    return out


K11_V7 = ('Ritual Jumat 1 Jan 2027 dan ritual Sabtu 1 Jan 2028 dini hari, langsung sesudah tutup hari 31 Des (keputusan owner K3, 9 Okt 2026);', 'Tutup buku 2027: toko tutup sesudahnya sampai Lanjutkan & arsip habis;')
KONTROL = [
    # (nama, ganti, awalan pemeriksaan yang WAJIB gagal — berbunyi karena sebabnya)
    ('D1 persen tulis 2028 kembali ke skala 2026 (117%)', {V7: [('tulis **±280–335%**', 'tulis **±117–140%**')]}, 'D1 ' + V7 + ': persen'),
    ('D1 hari kuota baca ditulis satu hari', {GLADI: [('kartu (perkiraan atas) ±6–7 hari', 'kartu (perkiraan atas) ±1–2 hari')]}, 'D1 ' + GLADI + ': hari kuota'),
    ('D1 117% tanpa keterangan skala 2026 saja', {GLADI: [('catatan 2026 SAJA (8 Agu–31 Des), bukan setahun penuh: ritual', 'setahun: ritual')]}, 'D1 ' + GLADI + ': 117%'),
    ('D1 proyeksi setahun penuh dihapus', {V7: [('**BEBERAPA hari kuota, bukan satu**', '**cukup satu hari**')]}, 'D1 ' + V7 + ': ada proyeksi'),
    ('D1 K11 di uji-rules-v7 kembali menyuruh toko tutup sesudah ritual', {V7: [K11_V7]}, 'D1 ' + V7 + ': bunyi K11'),
    ('D1 BACA-DULU K11 tanpa "DICABUT"', {BACA: [('- **K11** — **DICABUT 9 Okt 2026 (Blaze).**', '- **K11** —')]}, 'D1 ' + BACA),
    ('D1 gladi K11 tanpa sebab Blaze (kuota dianggap masih batas)', {GLADI: [('kuota harian bukan lagi batas (kelebihannya ditagih),\njadi arsip tidak berhenti', 'kuota harian masih batas,\njadi arsip berhenti')]}, 'D1 ' + GLADI + ': K11'),
    ('D1 kode: kartu berhenti menghitung baca pemeriksaan server (dokumen tak lagi sama dengan rumus)',
     {TB: [('baca: muat + getP + getA + nP + aturan + potong }', 'baca: muat + getP + nP + aturan + potong }')]}, 'D1 '),
    ('D2 K9 kembali "pekerjaan kode tersendiri"', {BACA: [('Kalimat itu\n  dipasang di aplikasi oleh PR #121 (paket P2: `laporan-logika.js LP_KALIMAT_MODAL_AWAL`, dipakai berita acara tutup buku & Neraca berkop).',
                                                          '(memasang kalimat itu di aplikasi = pekerjaan kode tersendiri)')]}, 'D2 K9: tidak lagi'),
    ('D2 K9 tanpa jalan sementara owner', {BACA: [('owner menyampaikannya sendiri ke konsultan bersama PDF Neraca 31 Des', 'owner menunggu')]}, 'D2 K9: jalan sementara'),
    ('D2 kode: konstanta K9 ada tapi isinya bukan keputusan owner & tidak dipakai berita acara',
     {LL: [('export function neracaPada(', "export const LP_KALIMAT_MODAL_AWAL = 'Modal awal tidak pernah dicatat.';\nexport function neracaPada(")]}, 'D2 K9 (kalimat SUDAH di kode)'),
    ('D3 jalur "Menu › Sistem" kembali', {HB: [('tombol di Menu › Toko ini › Perangkat & antrean › Hemat baca', 'tombol di Menu › Sistem › Perangkat › Hemat baca')]}, 'D3 ' + HB),
    ('D3 nama baris salah ("Perangkat" bukan "Perangkat & antrean")', {V7: [('Mundur hemat baca = saklar (Menu › Toko ini › Perangkat & antrean › Hemat baca', 'Mundur hemat baca = saklar (Menu › Toko ini › Perangkat › Hemat baca')]}, 'D3 ' + V7 + ': tiap'),
    ('D3 tab yang tidak ada ("Antrean" bukan "Antrean kirim")', {V6: [('Perangkat & antrean › Antrean kirim\n(ditolak server)', 'Perangkat & antrean › Antrean\n(ditolak server)')]}, 'D3 ' + V6 + ': tiap'),
    ('D4 §9 kembali "tidak ada tombol manual"', {PINDAH: [('(3) tidak ada tombol terpisah untuk katalog kasir:', '(3) tidak ada tombol manual:')]}, 'D4 §9: tanpa'),
    ('D4 §9 tanpa tombol TERBITKAN', {PINDAH: [('lalu mengetuk **TERBITKAN … HARGA**', '')]}, 'D4 §9: jalan'),
    ('D5 v6 kembali "tetap berlaku"', {V6: [('Langkah 1–2 di bawah juga sejarah', 'Langkah 1–2 tetap berlaku')]}, 'D5 ' + V6),
    ('D5 langkah ditolak di v7 menyuruh tempel v5', {V7: [('**jangan tempel rules lain**', 'tempel `firestore.rules.v5` dari repo')]}, 'D5 ' + V7),
    ('D6 §10 bersandar pada KP_KUNCI_MULAI saja', {KUNCI: [('tetapi kunci pertama = Januari 2027', 'tetapi kunci mulai 2027'),
                                                         ('selagi catatannya hidup: kunci pertama = Januari 2027', 'selagi catatannya hidup: kunci mulai 2027')]}, 'D6 '),
]


def main():
    if '--kontrol' in sys.argv:
        # dasar = pemeriksaan yang lulus di repo; pemeriksaan yang baru MUNCUL karena kerusakan (mis. K9 sesudah konstantanya ada di kode) ikut dinilai
        H0 = periksa(baca()); dasar = {n for n, ok, _ in H0 if ok}; semua0 = {n for n, _, _ in H0}; diam = []
        for nama, g, sebab in KONTROL:
            try: hasil = periksa(baca(g))
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam.append(nama); continue
            gagal = [n for n, ok, _ in hasil if not ok and (n in dasar or n not in semua0)]
            tepat = [n for n in gagal if n.startswith(sebab)]
            print(('BERBUNYI ' if tepat else 'DIAM!!   ') + nama + ('  → ' + tepat[0][:130] if tepat else ('  (gagal karena sebab lain: ' + (gagal[0][:100] if gagal else '—') + ')')))
            if not tepat: diam.append(nama)
        print('kontrol: %d/%d berbunyi karena sebabnya' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:400] if k not in ('', None) else ''))
    lulus = sum(1 for _, ok, _ in hasil if ok)
    print('DOKUMEN PEGANGAN OWNER (audit P6): %d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
