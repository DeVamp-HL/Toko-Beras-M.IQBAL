#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jual_bonus.py — owner 23 Nov 2026: PENJAGA BONUS +1 dari staf di layar Jual. KOTAK PASIR (angka & nama CONTOH), jsc saja, TANPA peramban.
Keputusan owner (23 Nov): bonus +1 kemasan dari staf MASUK JATAH NEGO; lewat jatah atau membuat baris rugi → MINTA OWNER (papan persetujuan yang
sama dengan nego, sekali pakai); bonus yang jadi nota tercatat di BUKU NEGO (siapa · barang · nilai bonus).
  · rumus: diberikan = katalog × (bayar + bonus) − harga × bayar ≤ margin baris × jatah (margin = katalog × (bayar + bonus) − modal baris) — satu rumus
    (akses.js bonusDalamBatas) untuk layar Jual dan penjaga kiriman;
  · putusan: owner bebas; Ben dalam jatah langsung; lewat jatah / modal belum tercatat / karyawan 0 % → minta owner (harga & bonus baris TIDAK berubah);
    kisi "tidak boleh" → ditolak; minta owner belum dibuka server → kalimat menyebut jalan keluar;
  · alur: bonus ditolak → permintaan (persetujuan tindakan 'nego' + bonus 1, bentuk rules v7 — rules tidak berubah) → owner menyetujui → ketuk bonus lagi →
    dipasang dengan bonusSetujuId (sekali pakai, jumlah bayar harus SAMA) → nota membawa bonusStatus / bonusJatah / bonusSetujuId / bonusNilai;
  · penjaga kiriman: nota berbonus dari staf tanpa tanda, dengan tanda 'owner', lewat jatah (dihitung ULANG dari kolom nota), atau jatah lebih besar
    dari jatah akun → tindakan nego → MINTA OWNER;
  · baris berbonus yang diubah (jumlah, nego, pembeli) diputus lagi; Buku Nego mendaftar bonus & permintaan bonus.

    python3 alat-uji/uji_jual_bonus.py            → N lulus · 0 gagal
    python3 alat-uji/uji_jual_bonus.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_jual_nego  # noqa: E402
JSC = uji_jual_nego.JSC
MODUL = uji_jual_nego.MODUL
SUMBER = {'jual': 'baru/js/layar/jual.js'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-10-07', jam: '10:00', kini: '2026-10-07T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };   // = app.js setelSumberHak
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false, lama: null }; }), [], hak(akun), new Date('2026-10-07T10:00:00+07:00')); };
var PENJ0 = JSON.parse(J(KOTAK.penjualan || []));
// kemasan contoh Kembang 5 kg: katalog 72.000, modal 66.000 per unit (margin 6.000) — bonus 1 unit = 72.000
var KMS = function (bayar, ubah) { return Object.assign({ jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: bayar + 1, bonusUnit: 1, totalKg: 5 * (bayar + 1), hppTotalSaatJual: 66000 * (bayar + 1),
  label: 'Kembang 5 kg', satuan: 'kemasan', jumlah: bayar, hargaAsli: 72000, hargaSatuan: 72000, hargaTotal: 72000 * bayar }, ubah || {}); };

// ---- A · rumus satu (akses.js bonusDalamBatas)
ok('A: 23 dibayar + 1 bonus, jatah 50 %: diberikan 72.000 = separuh margin 144.000 → BOLEH (tepat di batas)', bonusDalamBatas(72000, 72000, 23, 1, 66000 * 24, 50));
ok('A: 22 dibayar + 1 bonus, jatah 50 %: diberikan 72.000 > separuh margin 138.000 → TIDAK', !bonusDalamBatas(72000, 72000, 22, 1, 66000 * 23, 50));
ok('A: jatah 100 % = boleh sampai modal (11 + 1: margin 72.000 = diberikan) · 10 + 1 rugi → TIDAK; jatah 0 / modal 0 / bayar 0 → TIDAK',
  bonusDalamBatas(72000, 72000, 11, 1, 66000 * 12, 100) && !bonusDalamBatas(72000, 72000, 10, 1, 66000 * 11, 100) && !bonusDalamBatas(72000, 72000, 23, 1, 66000 * 24, 0)
  && !bonusDalamBatas(72000, 72000, 23, 1, 0, 50) && !bonusDalamBatas(72000, 72000, 0, 1, 66000, 50));
ok('A: nego + bonus dihitung BERSAMA: 23 + 1 dengan harga 71.500 → diberikan 83.500 > 72.000 → TIDAK', !bonusDalamBatas(72000, 71500, 23, 1, 66000 * 24, 50));

// ---- B · putusan
var pB = function (bayar, akun, o, ubah) { return ngPutusBonus(KMS(bayar, ubah), akun, o || { hakNego: 'owner' }); };
ok('B: owner → "owner" berapa pun', pB(1, OWN).status === 'owner' && pB(1, OWN, {}, { hppTotalSaatJual: 0 }).status === 'owner');
ok('B: Ben 23 + 1 → dalam jatah 50 %; nilai bonus 72.000', pB(23, BEN).status === 'jatah' && pB(23, BEN).jatah === 50 && pB(23, BEN).nilai === 72000, J(pB(23, BEN)));
ok('B: Ben 22 + 1 dan 1 + 1 → MINTA OWNER (lewat jatah)', pB(22, BEN).status === 'minta' && pB(1, BEN).status === 'minta' && /lewat jatah Ben Contoh/.test(pB(1, BEN).teks) && /minta owner$/.test(pB(1, BEN).teks), J(pB(1, BEN)));
ok('B: karyawan (jatah 0 %) → minta owner, kalimat "tidak punya jatah"', pB(23, KRY).status === 'minta' && /tidak punya jatah/.test(pB(23, KRY).teks), pB(23, KRY).teks);
ok('B: modal belum tercatat → minta owner (tidak bisa dihitung)', pB(23, BEN, null, { hppTotalSaatJual: 0 }).status === 'minta' && /belum tercatat/.test(pB(23, BEN, null, { hppTotalSaatJual: 0 }).teks));
ok('B: kisi nego "tidak boleh" → DITOLAK; minta owner belum dibuka → minta dengan jalan keluar (parkir / owner mencatat)',
  pB(1, BEN, { hakNego: 'tidak' }).status === 'tolak' && pB(1, BEN, { hakNego: 'owner', bisaMinta: false }).status === 'minta' && /parkir struk ini/.test(pB(1, BEN, { hakNego: 'owner', bisaMinta: false }).teks));
ok('B: baris tanpa bonus → "tanpa" (bukan urusan penjaga bonus)', ngPutusBonus(KMS(1, { bonusUnit: 0, jumlahUnit: 1 }), BEN, {}).status === 'tanpa');
var tB = ngTandaiBonus(KMS(23), pB(23, BEN));
ok('B: tanda dipasang: bonusStatus jatah, bonusJatah 50, bonusNilai 72.000; dilepas → kolom bersih', tB.bonusStatus === 'jatah' && tB.bonusJatah === 50 && tB.bonusNilai === 72000
  && !('bonusStatus' in ngTandaiBonus(tB, null)) && !('bonusNilai' in ngTandaiBonus(tB, null)), J(tB));

// ---- C · keranjang Ben: tolak → minta owner → disetujui → dipasang sekali
var s = keadaanAwal(); s.sekarang = new Date('2026-10-07T10:00:00+07:00'); s.negoAkun = BEN; s.negoHak = 'owner'; s.negoBisaMinta = true; sinkronKeranjang(s);
var terap = function (p) { s = Object.assign({}, s, p || {}); sinkronKeranjang(s); return p; };
var chip = function () { return susunRak(s).kemasan.filter(function (c) { return c.kunci === 'Kembang|5'; })[0]; };
terap(masukkan(Object.assign({}, s, { pilih: chip() }), 1)); var id1 = s.keranjang[0].id;
var b1 = toggleBonus(s, id1); terap(b1);
ok('C: Ben bonus +1 atas 1 kemasan → DITOLAK jadi permintaan: baris TIDAK berbonus, s.bonusMinta menunjuk baris, kabar awas', !b1.keranjang && s.bonusMinta && s.bonusMinta.id === id1 && !s.keranjang[0].trx.bonusUnit && b1.kabarAwas, J(b1));
var rM = susunMintaBonus(s, W); var dM = rM.dokumen && rM.dokumen[0].data;
ok('C: permintaan = persetujuan tindakan nego + bonus 1, menunggu, atas nama Ben, barang kemasan|Kembang|5, jumlah 1, harga 72.000, diberikan 72.000; bonusMinta dikosongkan',
  dM && dM.tindakan === 'nego' && dM.bonus === 1 && dM.status === 'menunggu' && dM.negoUid === 'uid-ben' && dM.barang === ngKunciBarang(s.keranjang[0].trx) && dM.jumlah === 1 && dM.hargaMinta === 72000 && dM.nominal === 72000
  && rM.patch.bonusMinta === null, J(rM));
ok('C: penjaga kiriman MELOLOSKAN permintaan bonus Ben (bentuk rules v7 stafMintaNego, tanpa rules baru)', !kirim(BEN, rM.dokumen).tolak, J(kirim(BEN, rM.dokumen)));
ok('C: papan owner menghitung ulang: "BONUS +1 … + 1 gratis = diberikan Rp72.000"', /BONUS \+1/.test(ngPeriksaMinta(dM).teks) && ngPeriksaMinta(dM).nominal === 72000 && /diberikan Rp72\.000/.test(ngPeriksaMinta(dM).teks), ngPeriksaMinta(dM).teks);
terap(rM.patch);
var setuju = Object.assign({}, dM, { status: 'disetujui', diputusPada: W.kini });
pasok('persetujuan', [setuju]);
ok('C: persetujuan BONUS tidak dipakai sebagai persetujuan NEGO harga (ngSetujuUntuk mengabaikannya)', ngSetujuUntuk(s.keranjang[0].trx, 72000, BEN, {}) === null);
var b2 = toggleBonus(s, id1); terap(b2); var t2 = s.keranjang[0].trx;
ok('C: sesudah owner setuju, ketuk bonus lagi → dipasang: bonusStatus disetujui + bonusSetujuId, uang tetap 72.000, stok & modal 2 unit',
  t2.bonusUnit === 1 && t2.bonusStatus === 'disetujui' && t2.bonusSetujuId === String(dM.id) && t2.hargaTotal === 72000 && t2.jumlahUnit === 2, J(t2));
var u2 = ubahJumlahBaris(s, id1, 1);
ok('C: jumlah dibayar diubah (1 → 2) → persetujuan untuk 1 tidak berlaku, bonus 2+1 lewat jatah → DITOLAK ("lepas bonusnya dulu")', !u2.keranjang && /tidak berlaku lagi/.test(u2.kabar || '') && /lepas bonusnya/.test(u2.kabar || ''), J(u2));
var nN = simpanNota(Object.assign({}, s, { uang: 1e9 }), W); var dN = nN.dokumen && nN.dokumen[0].data;
ok('C: nota membawa bonusStatus disetujui, bonusSetujuId, bonusNilai 72.000; penjaga kiriman MELOLOSKAN nota Ben ini',
  dN && dN.bonusUnit === 1 && dN.bonusStatus === 'disetujui' && dN.bonusSetujuId === String(dM.id) && dN.bonusNilai === 72000 && !kirim(BEN, nN.dokumen).tolak, J([dN, kirim(BEN, nN.dokumen)]));
pasok('penjualan', PENJ0.concat([Object.assign({}, dN, { oleh: 'Ben Contoh' })]));
ok('C: persetujuan bonus SEKALI PAKAI: sesudah jadi nota tidak cocok lagi untuk baris yang sama', ngSetujuBonusUntuk(KMS(1, { hargaSatuan: 72000 }), BEN, {}) === null);
var bk = ngBuku('2026-10-07'); var bb = bk.baris.filter(function (x) { return x.jenis === 'bonus'; })[0]; var bm = bk.baris.filter(function (x) { return x.jenis === 'minta' && x.bonus; })[0];
ok('F: Buku Nego mendaftar bonus nota (Ben · Kembang 5 kg · nilai 72.000 · disetujui) + permintaannya (dipakai); judul menyebut "1 bonus Rp72.000"',
  bb && bb.oleh === 'Ben Contoh' && bb.nilai === 72000 && bb.status === 'bonusDisetujui' && NG_LABEL[bb.status] && bm && bm.status === 'dipakai' && bk.nBonus === 1 && /1 bonus Rp72\.000/.test(bk.judul), J(bk));
pasok('penjualan', PENJ0); pasok('persetujuan', []);

// ---- D · penjaga kiriman (nota yang tidak lewat layar)
var nota = function (ubah) { return [{ koleksi: 'penjualan', data: Object.assign({ id: 1, trxId: 1, tanggal: '2026-10-07', jam: '10:00', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5,
  jumlahUnit: 24, bonusUnit: 1, totalKg: 120, hppTotalSaatJual: 66000 * 24, hargaAsliSatuan: 72000, hargaTotal: 72000 * 23, bonusStatus: 'jatah', bonusJatah: 50, bonusNilai: 72000 }, ubah || {}) }]; };
ok('D: Ben 23 + 1 bertanda jatah 50 → LOLOS', !kirim(BEN, nota()).tolak, J(kirim(BEN, nota())));
ok('D: Ben nota berbonus TANPA tanda → MINTA OWNER', kirim(BEN, nota({ bonusStatus: undefined, bonusJatah: undefined })).tolak === KALIMAT_MINTA_OWNER);
ok('D: Ben bertanda jatah tapi angkanya lewat jatah (dihitung ulang: 12 + 1) → MINTA OWNER', kirim(BEN, nota({ jumlahUnit: 13, hppTotalSaatJual: 66000 * 13, hargaTotal: 72000 * 12 })).tolak === KALIMAT_MINTA_OWNER);
ok('D: Ben bertanda jatah 100 (lebih dari jatahnya 50) → MINTA OWNER', kirim(BEN, nota({ bonusJatah: 100 })).tolak === KALIMAT_MINTA_OWNER);
ok('D: Ben bertanda "owner" / "disetujui" tanpa id → MINTA OWNER', kirim(BEN, nota({ bonusStatus: 'owner' })).tolak === KALIMAT_MINTA_OWNER && kirim(BEN, nota({ bonusStatus: 'disetujui' })).tolak === KALIMAT_MINTA_OWNER);
ok('D: nego + bonus bertanda jatah yang bersama-sama lewat (harga 71.500) → MINTA OWNER', kirim(BEN, nota({ negoSelisih: -500, negoStatus: 'jatah', negoBatas: 69000, negoJatah: 50, hargaTotal: 71500 * 23 })).tolak === KALIMAT_MINTA_OWNER);
ok('D: owner mengirim nota berbonus tanpa tanda → bebas', !kirim(OWN, nota({ bonusStatus: undefined })).tolak);

// ---- E · owner & Ben dalam jatah di keranjang; nego sesudah bonus diputus bersama
var sO = keadaanAwal(); sO.sekarang = new Date('2026-10-07T10:00:00+07:00'); sO.negoAkun = OWN; sO.negoHak = 'sendiri'; sinkronKeranjang(sO);
sO = Object.assign(sO, masukkan(Object.assign({}, sO, { pilih: susunRak(sO).kemasan.filter(function (c) { return c.kunci === 'Kembang|5'; })[0] }), 1)); sinkronKeranjang(sO);
var bO = toggleBonus(sO, sO.keranjang[0].id); var tO = bO.keranjang && bO.keranjang[0].trx;
ok('E: owner bonus +1 atas 1 kemasan → langsung dipasang, bonusStatus owner', tO && tO.bonusUnit === 1 && tO.bonusStatus === 'owner' && !bO.bonusMinta, J(bO));
var sB = keadaanAwal(); sB.sekarang = new Date('2026-10-07T10:00:00+07:00'); sB.negoAkun = BEN; sB.negoHak = 'owner'; sB.negoBisaMinta = true; sinkronKeranjang(sB);
sB = Object.assign(sB, masukkan(Object.assign({}, sB, { pilih: susunRak(sB).kemasan.filter(function (c) { return c.kunci === 'Kembang|5'; })[0] }), 23)); sinkronKeranjang(sB);
var idB = sB.keranjang[0].id; var bB = toggleBonus(sB, idB); sB = Object.assign(sB, bB); sinkronKeranjang(sB); var tBB = sB.keranjang[0].trx;
ok('E: Ben bonus +1 atas 23 kemasan → dalam jatah, langsung dipasang (bonusStatus jatah, bonusJatah 50)', tBB.bonusUnit === 1 && tBB.bonusStatus === 'jatah' && tBB.bonusJatah === 50, J(bB));
var nB = terapkanNego(sB, idB, 71500);
ok('E: lalu Ben menawar 71.500 (nego sendiri dalam jatah, tapi bersama bonus lewat) → DITOLAK, harga tetap', !nB.keranjang && /dengan bonus \+1/.test(nB.kabar || ''), J(nB));
var kB = ubahJumlahBaris(sB, idB, -1);
ok('E: jumlah dikurangi (23 → 22) → bonus lewat jatah → DITOLAK', !kB.keranjang && /Bonus \+1 untuk/.test(kB.kabar || ''), J(kB));
var lB = toggleBonus(sB, idB);
ok('E: bonus dilepas → kolom bonus bersih', lB.keranjang && !lB.keranjang[0].trx.bonusUnit && !lB.keranjang[0].trx.bonusStatus, J(lB));
print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('layar: aksi minta owner untuk bonus memeriksa server & memakai susunMintaBonus', 'jual', ["mintaOwnerBonus: () => { const a = opsi.akun ? opsi.akun() : null; const mb = bolehMintaOwner(a) || {}; if (!mb.boleh) { set({ kabar: mb.kalimat", "tulisUmum(L.susunMintaBonus(SBN(),"]),
    ('layar: pita permintaan bonus dengan tombol minta owner & batal', 'jual', ['data-k="pita-bonus-minta"', 'data-aksi="mintaOwnerBonus"', 'data-aksi="lepasBonusMinta"']),
    ('layar: tombol bonus memakai akun yang masuk (SBN)', 'jual', ["bonus: ({ id }) => set(L.toggleBonus(SBN(), id)),"]),
    ('layar: Buku Nego menulis baris bonus (gratis · nilai)', 'jual', ["x.jenis === 'bonus' ? '+' + DESIMAL(x.jumlah) + ' gratis · nilai ' + RP(x.nilai)"]),
]


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-10-07T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


NG = 'baru/js/layar/nego-logika.js'; JL = 'baru/js/layar/jual-logika.js'; AK = 'baru/js/data/akses.js'
RUSAK = [
    ('rumus: margin × jatah diabaikan (bonus selalu boleh)', AK, "return margin > 0 && diberi <= margin * Math.min(J, 100) / 100 + 0.5;", "return margin > 0;"),
    ('rumus: nego tidak ikut dihitung (diberikan = katalog × bonus saja)', AK, "const margin = A * (n + b) - M; const diberi = A * (n + b) - H * n;", "const margin = A * (n + b) - M; const diberi = A * b;"),
    ('penjaga kiriman tidak memeriksa bonus', AK, "if (!negoDalamJatah(d, jatahNego) || !bonusDalamJatah(d, jatahNego) ||", "if (!negoDalamJatah(d, jatahNego) ||"),
    ('penjaga kiriman percaya tanda jatah tanpa menghitung ulang', AK, "  return bonusDalamBatas(asli, harga, (Number(d.jumlahUnit) || 0) - b, b, Number(d.hppTotalSaatJual) || 0, jatah);\n}", "  return true;\n}"),
    ('penjaga kiriman menerima jatah di atas jatah akun', AK, "if (!(jatah > 0 && jatah <= (Number(jatahNego) || 0))) return false;", "if (!(jatah > 0)) return false;"),
    ('penjaga kiriman menerima "disetujui" tanpa id persetujuan', AK, "if (d.bonusStatus === 'disetujui') return !!d.bonusSetujuId;", "if (d.bonusStatus === 'disetujui') return true;"),
    ('staf diperlakukan seperti owner (bonus bebas)', NG, "  if (ngOwner(akun)) return P('owner', 'bonus dari owner');", "  return P('owner', 'bonus dari owner');"),
    ('lewat jatah dipasang tanpa minta owner', NG, "  return P('minta', sebab + ' — minta owner');\n}", "  return P('jatah', sebab);\n}"),
    ('kisi "tidak boleh" diabaikan untuk bonus', NG, "if (o.hakNego === 'tidak') return P('tolak', 'Peran ' + nm + ' tidak boleh memberi bonus", "if (false) return P('tolak', 'Peran ' + nm + ' tidak boleh memberi bonus"),
    ('persetujuan bonus berlaku untuk jumlah lain', NG, "&& m.barang === k && Number(m.jumlah) === Number(t.jumlah) && Number(m.hargaMinta) <= Number(t.hargaSatuan)", "&& m.barang === k && Number(m.hargaMinta) <= Number(t.hargaSatuan)"),
    ('persetujuan bonus dipakai berkali-kali', NG, " if (p.bonusSetujuId) o[String(p.bonusSetujuId)] = 1; });", " });"),
    ('persetujuan bonus dipakai sebagai persetujuan nego harga', NG, "m.tindakan === 'nego' && !m.bonus && m.status === 'disetujui'", "m.tindakan === 'nego' && m.status === 'disetujui'"),
    ('permintaan bonus tanpa tanda bonus (owner melihatnya sebagai nego Rp0)', NG, "const data = { id: w.idUnik(), tindakan: 'nego', bonus: 1, status: 'menunggu',", "const data = { id: w.idUnik(), tindakan: 'nego', status: 'menunggu',"),
    ('papan owner tidak menghitung nilai bonus', NG, "Math.round(bon ? katalog * (jumlah + 1) - hargaMinta * jumlah : (katalog - hargaMinta) * jumlah)", "Math.round((katalog - hargaMinta) * jumlah)"),
    ('Buku Nego tanpa baris bonus', NG, "  const baris = nota.concat(bonus, minta).sort(", "  const baris = nota.concat(minta).sort("),
    ('bonus minta owner tetap dipasang di baris', JL, "    if (p.status === 'minta') return { bonusMinta: { id, teks: p.teks },", "    if (false) return { bonusMinta: { id, teks: p.teks },"),
    ('baris berbonus yang diubah tidak diputus lagi', JL, "  if (!(Number(t.bonusUnit) > 0)) return { trx: t };\n  const p = putusBonusBaris(s, t, id);", "  return { trx: t };\n  const p = putusBonusBaris(s, t, id);"),
    ('nego sesudah bonus tidak memeriksa bonus', JL, "  if (Number(trx.bonusUnit) > 0) { const pb = putusBonusBaris(s, trx, id); if (!ngBonusBolehPakai(pb))", "  if (false) { const pb = putusBonusBaris(s, trx, id); if (!ngBonusBolehPakai(pb))"),
]
RUSAK_STATIS = [
    ('tombol minta owner bonus tanpa memeriksa server', 'jual', "mintaOwnerBonus: () => { const a = opsi.akun ? opsi.akun() : null; const mb = bolehMintaOwner(a) || {}; if (!mb.boleh) { set(", "mintaOwnerBonus: () => { const a = opsi.akun ? opsi.akun() : null; const mb = { boleh: true }; if (!mb.boleh) { set("),
    ('pita bonus tanpa tombol minta owner', 'jual', 'data-aksi="mintaOwnerBonus"', 'data-aksi="x"'),
]

if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S2 = dict(src); S2[berkas] = S2[berkas].replace(a, b)
            l, g = statis(S2)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(teks); l2, g2 = statis(src)
    print('PENJAGA BONUS +1 (owner 23 Nov, kotak pasir): %d lulus · %d gagal (logika %d · statis %d)' % (l + l2, len(g) + len(g2), l, l2))
    for x in g + g2: print('   ✗ ' + x[:600])
    sys.exit(2 if g or g2 else 0)
