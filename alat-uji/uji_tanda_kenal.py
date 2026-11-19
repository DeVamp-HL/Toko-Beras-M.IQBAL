#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tanda_kenal.py — paket S2a (19 Nov 2026): QR nomor nota di struk & scan struk → notanya terbuka.

Yang dijaga:
  · tanda-kenal-logika.js (dijalankan apa adanya di jsc): teks QR per bentuk kunci nota, urutan pilih kunci = notaDari (trxId dulu), kunci yang tidak
    bisa dicetak → struk TANPA QR (bukan QR yang salah), bolak-balik cetak → scan → kunci yang sama, kode bukan struk toko tidak dianggap nota,
    QR tidak utuh disebut rusak, lembar berisi isian (bayar, jumlah, …) tidak ditimpa lembar struk
  · sambungan: jual.js mencetak QR hanya bila setelan printer perangkat menyertakannya; scan diperiksa dulu (lembar, nota ada) baru membuka struk;
    app.js meneruskan scan ke layar Jual hanya bila panel jaga tertutup & layar Jual di depan; printer.js / escpos.js sungguh mencetak QR itu

    python3 alat-uji/uji_tanda_kenal.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_tanda_kenal.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import json, os, re, subprocess, sys, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MODUL = os.path.join(AKAR, 'baru', 'js', 'layar', 'tanda-kenal-logika.js')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });
const J = (x) => JSON.stringify(x);

// ---- teks QR ----
cek('QR nota bernomor transaksi (angka pecahan seperti di data toko)', tkQrNota({ trxId: 1763553890123.25, grupNota: 'G1', id: 9 }) === 'MIQ:N:t:1763553890123.25', tkQrNota({ trxId: 1763553890123.25 }));
cek('QR nota lama bergrup', tkQrNota({ trxId: null, grupNota: 'grup-77', id: 9 }) === 'MIQ:N:g:grup-77');
cek('QR nota satu baris tanpa grup', tkQrNota({ trxId: null, grupNota: null, id: 1761999999999.25 }) === 'MIQ:N:i:1761999999999.25');
cek('id 0 tetap kunci', tkQrNota({ id: 0 }) === 'MIQ:N:i:0');
cek('tanpa nota / tanpa kunci → tanpa QR', tkQrNota(null) === '' && tkQrNota({}) === '' && tkQrNota({ trxId: '', grupNota: '', id: '' }) === '');
cek('kunci berspasi / berhuruf bukan ASCII → tanpa QR (bukan QR yang salah)', tkQrNota({ trxId: 'a b' }) === '' && tkQrNota({ trxId: 'nota—1' }) === '');
cek('kunci terlalu panjang → tanpa QR', tkQrNota({ trxId: 'x'.repeat(TK_PANJANG_MAKS) }) === '' && tkQrNota({ trxId: 'x'.repeat(TK_PANJANG_MAKS - 8) }) !== '');

// ---- bolak-balik cetak → scan ----
for (const n of [{ trxId: 1763553890123.4567 }, { grupNota: 'grup-77' }, { id: 1761999999999.25 }, { trxId: 'T-1:2:3' }]) {
  const u = tkUraiPindai(tkQrNota(n)); const kol = Object.keys(n)[0];
  cek('bolak-balik ' + kol + ' ' + n[kol], u && u.jenis === 'nota' && Object.keys(u.kunci).length === 1 && u.kunci[kol] === String(n[kol]) && typeof u.kunci[kol] === 'string', J(u));
}
cek('hasil scan dirapikan (spasi & baris baru di tepi)', J(tkUraiPindai('  MIQ:N:t:abc \n')) === J({ jenis: 'nota', kunci: { trxId: 'abc' } }), J(tkUraiPindai('  MIQ:N:t:abc \n')));

// ---- bukan struk toko ----
for (const k of ['8991234567890', '(90)NA18250100004', 'miq:n:t:1', 'https://contoh.id/MIQ:N:t:1', 'UJI-CETAK']) {
  const u = tkUraiPindai(k); cek('bukan struk toko: ' + k, u && u.jenis === 'lain' && u.kode === k, J(u));
}
cek('kosong → null', tkUraiPindai('') === null && tkUraiPindai('   ') === null && tkUraiPindai(null) === null && tkUraiPindai(undefined) === null);

// ---- QR struk tidak utuh ----
for (const k of ['MIQ:N:x:abc', 'MIQ:N:t:', 'MIQ:N:t', 'MIQ:N:', 'MIQ:N:t:a b', 'MIQ:N:tabc', 'MIQ:N:t:' + 'x'.repeat(TK_PANJANG_MAKS)]) {
  const u = tkUraiPindai(k); cek('QR struk tidak utuh disebut rusak: ' + k.slice(0, 24), u && u.jenis === 'rusak', J(u));
}

// ---- lembar ----
cek('layar dasar, keranjang, struk lain boleh diganti lembar struk', tkLembarBolehDiganti(null) && tkLembarBolehDiganti('') && tkLembarBolehDiganti(undefined) && tkLembarBolehDiganti('struk') && tkLembarBolehDiganti('keranjang'));
cek('lembar berisi isian TIDAK ditimpa', ['bayar', 'jumlah', 'retur', 'returTanpa', 'pelanggan', 'karcis', 'pesanan', 'potongan'].every((x) => tkLembarBolehDiganti(x) === false));

print(JSON.stringify(hasil));
"""


def baca(*bagian):
    with open(os.path.join(AKAR, *bagian), encoding='utf-8') as f: return f.read()


def siapkan(sumber):
    return sumber.replace('export const ', 'const ').replace('export function ', 'function ')


def jalankan_jsc(sumber):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(siapkan(sumber) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return [{'nama': 'jsc tidak jalan', 'ok': False, 'ket': (r.stderr or r.stdout).strip()[:400]}]
    return json.loads(r.stdout.strip().splitlines()[-1])


def periksa_statis(logika, jual, app):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    ok('modul tanpa impor (dijalankan apa adanya di jsc)', not re.search(r'^\s*import\s', logika, re.M))
    ok('jual.js: QR dicetak hanya bila setelan printer perangkat menyertakan QR, isinya dari tkQrNota',
       "const qr = PR.prAtur().qr ? TK.tkQrNota(nota) : '';" in jual and "PR.cetakGaris(st.garis, { logoToko: st.logo, qr })" in jual and jual.count('PR.cetakGaris(') == 1)
    blok = jual[jual.index('  function pindai(teks) {'):]; blok = blok[:blok.index('\n  }\n') + 5]
    urut = [blok.find(x) for x in ("u.jenis === 'lain'", "u.jenis === 'rusak'", 'TK.tkLembarBolehDiganti(S().lembar)', 'ST.notaDari(u.kunci)', 'aksi.bukaStruk(')]
    ok('jual.js: scan diperiksa dulu (kode lain, rusak, lembar terbuka, nota ada) BARU membuka struk', all(x >= 0 for x in urut) and urut == sorted(urut) and blok.count('aksi.bukaStruk(') == 1, urut)
    ok('jual.js: layar terkunci tidak menanggapi scan', 'terkunci()' in blok.split("u.jenis === 'rusak'")[0])
    ok('jual.js: tiap penolakan scan berkabar (tidak diam)', blok.count('kabarAwas: true') == 3)
    ok('jual.js: pindai keluar dari pasangLayarJual', 'pulihkanKeranjang, pindai,\n' in jual)
    ok('app.js: scan ke layar Jual hanya bila panel jaga tertutup & layar Jual di depan, galatnya ditelan',
       "if (panelOrang.hidden) { if (tabKini === 'jual') { try { layar.pindai(x && x.data); } catch (e) { console.error('pindai jual', e); } } return; }" in app and app.count('layar.pindai(') == 1)
    ok('index.html: modul dipramuat', '<link rel="modulepreload" href="js/layar/tanda-kenal-logika.js">' in baca('baru', 'index.html'))
    pr = baca('baru', 'js', 'inti', 'printer.js'); ep = baca('baru', 'js', 'inti', 'escpos.js')
    ok('printer.js: QR dari pemanggil menimpa bawaan kosong', "susunCetak(garis, null, Object.assign({ qr: '' }, ekstra || {}))" in pr)
    ok('escpos.js: ekor struk mencetak QR bila ada', 'if (o.qr) {' in ep and 'tulisQr(w, o.qr, o.qrUkuran)' in ep)
    ok('struk-logika.js: notaDari membandingkan kunci sebagai teks (kunci hasil scan = teks)',
       all(x in baca('baru', 'js', 'layar', 'struk-logika.js') for x in ('String(x.trxId) === String(kunci.trxId)', 'String(x.grupNota) === String(kunci.grupNota)', 'String(x.id) === String(kunci.id)')))
    return h


def periksa(logika, jual, app, diam=False):
    try: statis = periksa_statis(logika, jual, app)
    except Exception as e: statis = [{'nama': 'pemeriksa statis jatuh', 'ok': False, 'ket': repr(e)[:300]}]
    h = jalankan_jsc(logika) + statis
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + x['ket']))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


# (nama, berkas 'logika' | 'jual' | 'app', lama, baru)
MUTASI = [
    ('QR memilih grup walau nota bernomor transaksi', 'logika', "ada(nota.trxId) ? ['t', nota.trxId] : ", ""),
    ('kunci yang tak bisa dicetak tetap jadi QR', 'logika', "return CETAK.test(String(pilih[1])) && teks.length <= TK_PANJANG_MAKS ? teks : '';", "return teks;"),
    ('kode bukan struk toko dianggap struk', 'logika', "if (t.indexOf(TK_AWALAN_NOTA) !== 0) return { jenis: 'lain', kode: t };", ""),
    ('QR struk tidak utuh dianggap nota', 'logika', "if (!kolom || sisa.charAt(1) !== ':' || !CETAK.test(nilai) || t.length > TK_PANJANG_MAKS) return { jenis: 'rusak', kode: t };", ""),
    ('kunci grup dibaca sebagai nomor transaksi', 'logika', "const KUNCI_DARI = { t: 'trxId', g: 'grupNota', i: 'id' };", "const KUNCI_DARI = { t: 'trxId', g: 'trxId', i: 'id' };"),
    ('hasil scan tidak dirapikan', 'logika', "teks).trim();", "teks);"),
    ('lembar bayar ditimpa lembar struk', 'logika', "!lembar || lembar === 'struk' || lembar === 'keranjang'", "true"),
    ('QR dicetak walau setelan perangkat tidak menyertakannya', 'jual', "const qr = PR.prAtur().qr ? TK.tkQrNota(nota) : '';", "const qr = TK.tkQrNota(nota);"),
    ('QR tidak ikut ke printer', 'jual', "PR.cetakGaris(st.garis, { logoToko: st.logo, qr })", "PR.cetakGaris(st.garis, { logoToko: st.logo })"),
    ('struk dibuka tanpa memeriksa lembar yang terbuka', 'jual', "    if (!TK.tkLembarBolehDiganti(S().lembar)) return set({ kabar: 'Struk ter-scan, tapi lembar ini masih terbuka — tutup dulu, lalu scan lagi', kabarAwas: true });\n", ""),
    ('struk dibuka walau notanya tidak ada', 'jual', "    if (!ST.notaDari(u.kunci)) return set({", "    if (false) return set({"),
    ('scan diteruskan ke Jual walau layar lain di depan', 'app', "if (tabKini === 'jual') { try { layar.pindai(", "if (true) { try { layar.pindai("),
    ('scan diteruskan ke Jual saat panel jaga terbuka', 'app', "if (panelOrang.hidden) { if (tabKini === 'jual')", "if (true) { if (tabKini === 'jual')"),
]


def main():
    if not os.path.exists(JSC): print('GAGAL: jsc tidak ditemukan'); return 1
    S = {'logika': open(MODUL, encoding='utf-8').read(), 'jual': baca('baru', 'js', 'layar', 'jual.js'), 'app': baca('baru', 'js', 'app.js')}
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, berkas, lama, baru in MUTASI:
            if lama not in S[berkas]: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            R = dict(S); R[berkas] = S[berkas].replace(lama, baru, 1)
            if periksa(R['logika'], R['jual'], R['app'], diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(S['logika'], S['jual'], S['app'], diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(S['logika'], S['jual'], S['app']) else 1


if __name__ == '__main__':
    sys.exit(main())
