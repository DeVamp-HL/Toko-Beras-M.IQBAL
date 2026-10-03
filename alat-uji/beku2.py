#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beku2.py — penjaga MESIN UANG BEKU di sistem baru (baru/js/mesin/).

Mesin uang = fungsi yang menghitung uang/stok dari dokumen. Tubuhnya WAJIB byte-identik antar putaran kerja, kecuali pemilik
memerintahkan pembekuan ulang (= membuka mesin).

SUMBER KEBENARAN (sejak 3 Okt 2026, perintah owner: sistem lama & kasir.html dibumihanguskan):
  baru/js/mesin/beku.js      — 26 mesin uang; sidik tubuhnya di alat-uji/beku.sha256
  baru/js/mesin/pembantu.js  — 55 fungsi + 36 konstanta pembantu yang dipanggil mesin; sidiknya di alat-uji/pembantu.sha256
Keduanya dulu disalin byte demi byte dari index.html oleh pindah_mesin.py (dipensiunkan 3 Okt bersama index.html). Pada commit terakhir sistem
lama (tag sistem-lama-terakhir = 48a694d) ke-26 mesin, ke-55 fungsi, dan ke-36 konstanta itu terbukti BYTE-SAMA dengan index.html — jadi sidik
yang dikunci di sini = aturan sistem lama. index.html di akar kini hanya halaman pengalih ke baru/; sistem lama utuh di tag sistem-lama-terakhir
(jalan mundur: docs/prosedur-pulih-darurat.md).

Kunci pembantu.sha256 menggantikan pembanding "HURUF DEMI HURUF = index.html" di uji_katalog_kasir, uji_operator_pin, uji_setelan_jenis_beras, dan
uji_arsip_produk (fungsi terkunci() di bawah). Tanpa kunci ini pembanding mereka menjadi tautologi: fungsi yang diuji dibandingkan dengan dirinya.

Kepala komentar beku.js & pembantu.js masih menyebut "DIBUAT OLEH alat-uji/pindah_mesin.py" dan gerbang `pindah_mesin.py --periksa`. Itu
SENGAJA dibiarkan (owner 3 Okt): baru/js/mesin/* hanya dibuka atas izin owner, termasuk komentarnya. Yang berlaku sekarang: berkas itulah sumber
kebenarannya, gerbangnya `beku2.py --sidik`, dan membuka mesin = sunting di sana atas perintah owner → `beku2.py --catat` → sebut di pesan commit.

Dua mesin dari daftar 28 lama PENSIUN bersama index.html: tulisSaldoPembuka (ritual Tutup Buku sistem lama, alert/confirm + layar lama) dan
thPagar (pagar Tutup Hari sistem lama, membaca document). Keduanya tidak pernah dipindah ke beku.js; /baru/ punya padanannya sendiri
(baru/js/layar/tutup-buku-logika.js, tutup-hari-logika.js). Baris acuannya di beku.sha256 DIBIARKAN (mengubah berkas itu, walau hanya
komentar, = membekukan ulang) dan dilewati --sidik.

Cara memotong fungsi: menghitung kurung kurawal dari '{' pertama sesudah nama fungsi (bukan sentinel teks), sehingga pemindahan lokasi fungsi
tidak mengubah hasil. Potongan mesin harus berakhir '  }' (kurung tutup pada indentasi dua spasi) — kalau tidak, alatnya yang salah potong, dan
alat wajib berhenti daripada meluluskan. Potongan ikut membawa baris kosong & indentasi di depan fungsi: menambah/mengurangi baris kosong di
antara dua fungsi mengubah sidik.
Konstanta pembantu: `  const NAMA = …;` satu pernyataan (kurung seimbang sampai ';' pada kedalaman 0).

Mode:
  (tanpa opsi)          bandingkan beku.js & pembantu.js kerja dengan `git show <ref>:baru/js/mesin/…` (--lama <ref>, bawaan main)
  --sidik               bandingkan sha256 tiap mesin (beku.sha256) dan tiap fungsi & konstanta pembantu (pembantu.sha256) — gerbang CI
  --catat               tulis ulang KEDUA berkas sidik dari beku.js & pembantu.js sekarang
                        (= PEMBEKUAN ULANG / MEMBUKA MESIN; hanya atas perintah pemilik, sebut di pesan commit mesin mana & kenapa)
  --uji-diri            buktikan alat ini bisa MELIHAT perubahan: mutasi di memori pada satu mesin, satu fungsi pembantu, satu konstanta
                        pembantu, dan satu fungsi baru tanpa acuan — pemeriksaan --sidik wajib menolak keempatnya
Kode keluar: 0 lulus · 2 mesin/pembantu berubah/hilang/salah potong/tanpa acuan · 3 uji-diri gagal · 4 salah pakai
"""
import io, os, re, sys, hashlib, subprocess

AKAR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REL_BEKU = 'baru/js/mesin/beku.js'
REL_PEMBANTU = 'baru/js/mesin/pembantu.js'
BERKAS_BEKU = os.path.join(AKAR, REL_BEKU)
BERKAS_PEMBANTU = os.path.join(AKAR, REL_PEMBANTU)
SIDIK = os.path.join(AKAR, 'alat-uji', 'beku.sha256')
SIDIK_PEMBANTU = os.path.join(AKAR, 'alat-uji', 'pembantu.sha256')

BEKU = """hitungArusKasInti hitungLabaRentang hitungLabaBersihRentang barisSusutStok bayaranBiayaBulanan
jatahBiayaBulananHari hitungStokKarungPerMerk hitungStokKemasan hitungStokBahanKemasan hitungStokBahanLiteran
hitungPiutang hitungUtangPemasok hitungUtangOwner hitungKasbon kasPada bagiBiayaAdukan hitungNeraca
hitungHppMerkDalamBatch pembulatanTunai hitungLajuPakai tbDaftarKoleksi hitungSaldoTutup
saldoAmplop stokMaksJalur wzDiKeranjang thDorongRiwayat""".split()
# Pensiun bersama index.html (3 Okt 2026) — baris acuannya di beku.sha256 dilewati, bukan dihapus.
PENSIUN = {'tulisSaldoPembuka': 'ritual Tutup Buku sistem lama; padanan /baru/: tutup-buku-logika.js',
           'thPagar': 'pagar Tutup Hari sistem lama; padanan /baru/: tutup-hari-logika.js'}
# Bahan uji-diri di pembantu.js (fungsi berbaris banyak & konstanta yang dibaca layar /baru/).
UJI_PEMBANTU_FUNGSI = 'susunIsiKatalogKasir'
UJI_PEMBANTU_KONSTANTA = 'PILIHAN_JENIS_BERAS'


def potong(teks, nama):
    """Kembalikan tubuh `function nama(...) {...}` lengkap, atau None bila tidak ada."""
    m = re.search(r'(?:^|\n)\s*(?:async\s+)?function\s+' + re.escape(nama) + r'\s*\(', teks)
    if not m:
        return None
    i = teks.index('{', m.end() - 1)
    d = 0
    j = i
    while j < len(teks):
        c = teks[j]
        if c == '{':
            d += 1
        elif c == '}':
            d -= 1
            if d == 0:
                return teks[m.start():j + 1]
        j += 1
    return None


def sidik(tubuh):
    return hashlib.sha256(tubuh.encode('utf-8')).hexdigest()


def potong_semua(teks, nama_nama):
    hasil, hilang, salah_potong = {}, [], []
    for n in nama_nama:
        b = potong(teks, n)
        if b is None:
            hilang.append(n)
            continue
        if not b.rstrip().endswith('\n  }'):
            salah_potong.append(n)
        hasil[n] = b
    return hasil, hilang, salah_potong


def fungsi_tingkat_atas(teks):
    """Nama fungsi yang dideklarasikan pada indentasi dua spasi (tingkat atas berkas mesin), urut kemunculan."""
    return re.findall(r'\n  (?:async\s+)?function\s+(\w+)\s*\(', teks)


def konstanta(teks):
    """{NAMA: teks `  const NAMA = …;`} — konstanta tingkat atas berhuruf besar."""
    konst = {}
    for m in re.finditer(r'\n  const\s+([A-Z_][A-Z0-9_]*)\s*=', teks):
        i = m.end(); d = 0; j = i; dalam = None
        while j < len(teks):
            c = teks[j]
            if dalam:
                if c == '\\':
                    j += 2
                    continue
                if c == dalam:
                    dalam = None
            elif c in '"\'`':
                dalam = c
            elif c in '([{':
                d += 1
            elif c in ')]}':
                d -= 1
            elif c == ';' and d == 0:
                break
            j += 1
        konst[m.group(1)] = teks[m.start() + 1:j + 1]
    return konst


def isi_pembantu(teks):
    """{nama: potongan} untuk tiap fungsi (potong) dan konstanta di pembantu.js."""
    isi = {}
    for n in fungsi_tingkat_atas(teks):
        b = potong(teks, n)
        if b is not None:
            isi[n] = b
    isi.update(konstanta(teks))
    return isi


def baca(jalur):
    return io.open(jalur, encoding='utf-8').read()


def baca_acuan(jalur):
    acuan = {}
    if not os.path.exists(jalur):
        return None
    for baris in baca(jalur).splitlines():
        baris = baris.strip()
        if not baris or baris.startswith('#'):
            continue
        h, n = baris.split()
        acuan[n] = h
    return acuan


def terkunci(nama, teks_pembantu=None):
    """True bila potongan `nama` di pembantu.js (atau teks yang diberikan — salinan rusak untuk kontrol) = sidik di pembantu.sha256.
    Dipakai uji yang dulu membandingkan fungsi /baru/ HURUF DEMI HURUF dengan index.html: kini pembandingnya kunci sidik ini."""
    acuan = baca_acuan(SIDIK_PEMBANTU) or {}
    isi = isi_pembantu(teks_pembantu if teks_pembantu is not None else baca(BERKAS_PEMBANTU))
    return nama in acuan and nama in isi and sidik(isi[nama]) == acuan[nama]


def periksa_sidik(beku, pembantu, acuan_beku, acuan_pembantu):
    """→ (baris laporan, lulus). Dipakai --sidik dan --uji-diri (teks boleh salinan termutasi di memori)."""
    out = []
    pb, hb, sb = potong_semua(beku, BEKU)
    lain = [n for n in fungsi_tingkat_atas(beku) if n not in BEKU]
    beda = [n for n in BEKU if n in pb and n in acuan_beku and sidik(pb[n]) != acuan_beku[n]]
    tanpa_acuan = [n for n in BEKU if n not in acuan_beku]
    acuan_asing = [n for n in acuan_beku if n not in BEKU and n not in PENSIUN]
    out.append('ACUAN MESIN   : %s (%d baris; pensiun dilewati: %s)' % (os.path.relpath(SIDIK, AKAR), len(acuan_beku),
                                                                         ', '.join(n for n in PENSIUN if n in acuan_beku) or 'nihil'))
    out.append('TERPOTONG     : %d dari %d mesin di %s' % (len(pb), len(BEKU), REL_BEKU))
    out.append('TAK KETEMU    : %s' % (hb or 'nihil'))
    out.append('SALAH POTONG  : %s' % (sb or 'nihil'))
    out.append('TANPA ACUAN   : %s' % (tanpa_acuan or 'nihil'))
    out.append('FUNGSI LAIN di beku.js (mesin tanpa kunci): %s' % (lain or 'nihil'))
    out.append('ACUAN TANPA MESIN: %s' % (acuan_asing or 'nihil'))
    out.append('MESIN UANG berubah    : %s' % (beda or 'nihil'))
    out.append('MESIN UANG byte-identik: %d/%d' % (len(BEKU) - len(beda) - len(hb) - len(tanpa_acuan), len(BEKU)))
    lulus = not (beda or hb or sb or tanpa_acuan or lain or acuan_asing)
    isi = isi_pembantu(pembantu)
    nf = len(fungsi_tingkat_atas(pembantu)); nk = len(konstanta(pembantu))
    beda_p = [n for n in isi if n in acuan_pembantu and sidik(isi[n]) != acuan_pembantu[n]]
    tanpa_p = [n for n in isi if n not in acuan_pembantu]
    hilang_p = [n for n in acuan_pembantu if n not in isi]
    out.append('ACUAN PEMBANTU: %s (%d nama)' % (os.path.relpath(SIDIK_PEMBANTU, AKAR), len(acuan_pembantu)))
    out.append('PEMBANTU di %s: %d fungsi + %d konstanta' % (REL_PEMBANTU, nf, nk))
    out.append('PEMBANTU hilang (ada di acuan, tidak di berkas): %s' % (hilang_p or 'nihil'))
    out.append('PEMBANTU tanpa acuan (baru, belum dibekukan): %s' % (tanpa_p or 'nihil'))
    out.append('PEMBANTU berubah     : %s' % (beda_p or 'nihil'))
    out.append('PEMBANTU byte-identik: %d/%d' % (len(isi) - len(beda_p) - len(tanpa_p), len(acuan_pembantu)))
    lulus = lulus and not (beda_p or tanpa_p or hilang_p) and len(isi) > 0
    return out, lulus


def mode_sidik():
    acuan_b, acuan_p = baca_acuan(SIDIK), baca_acuan(SIDIK_PEMBANTU)
    if acuan_b is None or acuan_p is None:
        print('TOLAK: berkas sidik belum ada (%s / %s) — --catat hanya atas perintah pemilik' % (os.path.relpath(SIDIK, AKAR), os.path.relpath(SIDIK_PEMBANTU, AKAR)))
        return 4
    out, lulus = periksa_sidik(baca(BERKAS_BEKU), baca(BERKAS_PEMBANTU), acuan_b, acuan_p)
    print('\n'.join(out))
    return 0 if lulus else 2


def tulis_acuan(jalur, kepala, isi):
    with io.open(jalur, 'w', encoding='utf-8') as f:
        f.write(kepala)
        for n, tubuh in isi:
            f.write('%s  %s\n' % (sidik(tubuh), n))


def mode_catat():
    beku, pembantu = baca(BERKAS_BEKU), baca(BERKAS_PEMBANTU)
    pb, hb, sb = potong_semua(beku, BEKU)
    lain = [n for n in fungsi_tingkat_atas(beku) if n not in BEKU]
    if hb or sb or lain:
        print('TOLAK: tidak bisa mencatat — tak ketemu %s, salah potong %s, fungsi di luar daftar BEKU %s' % (hb, sb, lain))
        return 2
    isi = isi_pembantu(pembantu)
    if not isi:
        print('TOLAK: pembantu.js kosong')
        return 2
    tulis_acuan(SIDIK, ('# sha256 tubuh %d mesin uang beku di %s (alat-uji/beku2.py --catat).\n'
                        '# Berkas ini hanya boleh berubah lewat commit yang menyebut "membekukan ulang"\n'
                        '# dan disetujui pemilik. CI membandingkan beku.js ke berkas ini (beku2.py --sidik).\n') % (len(BEKU), REL_BEKU),
                [(n, pb[n]) for n in BEKU])
    urut = fungsi_tingkat_atas(pembantu); konst = konstanta(pembantu)
    tulis_acuan(SIDIK_PEMBANTU, ('# sha256 %d fungsi + %d konstanta pembantu mesin beku di %s (alat-uji/beku2.py --catat).\n'
                                 '# Berkas ini hanya boleh berubah lewat commit yang menyebut "membekukan ulang"\n'
                                 '# dan disetujui pemilik. CI membandingkan pembantu.js ke berkas ini (beku2.py --sidik).\n') % (len(urut), len(konst), REL_PEMBANTU),
                [(n, isi[n]) for n in sorted(konst)] + [(n, isi[n]) for n in urut if n in isi])
    print('DICATAT   : %d sidik mesin ke %s · %d sidik pembantu ke %s' % (len(BEKU), os.path.relpath(SIDIK, AKAR), len(isi), os.path.relpath(SIDIK_PEMBANTU, AKAR)))
    return 0


def mode_banding(ref):
    try:
        lama_b = subprocess.check_output(['git', '-C', AKAR, 'show', ref + ':' + REL_BEKU], stderr=subprocess.DEVNULL).decode('utf-8')
        lama_p = subprocess.check_output(['git', '-C', AKAR, 'show', ref + ':' + REL_PEMBANTU], stderr=subprocess.DEVNULL).decode('utf-8')
    except subprocess.CalledProcessError:
        print('TOLAK: %s tidak punya %s / %s (ref salah, atau riwayat tidak terambil)' % (ref, REL_BEKU, REL_PEMBANTU))
        return 4
    baru_b, baru_p = baca(BERKAS_BEKU), baca(BERKAS_PEMBANTU)
    pa, ha, sa = potong_semua(lama_b, BEKU)
    pb, hb, sb = potong_semua(baru_b, BEKU)
    hilang = sorted(set(ha) | set(hb)); salah = sorted(set(sa) | set(sb))
    mu = [n for n in BEKU if n in pa and n in pb and pa[n] != pb[n]]
    ia, ib = isi_pembantu(lama_p), isi_pembantu(baru_p)
    beda_p = sorted(n for n in set(ia) | set(ib) if ia.get(n) != ib.get(n))
    print('BANDING   : %s vs kerja (%s, %s)' % (ref, REL_BEKU, REL_PEMBANTU))
    print('TAK KETEMU: %s' % (hilang or 'nihil'))
    print('SALAH POTONG (tidak berakhir "  }"): %s' % (salah or 'nihil'))
    print('MESIN UANG berubah    : %s' % (mu or 'nihil'))
    print('MESIN UANG byte-identik: %d/%d' % (len([n for n in BEKU if n in pa and n in pb and pa[n] == pb[n]]), len(BEKU)))
    print('PEMBANTU berubah/baru/hilang: %s' % (beda_p or 'nihil'))
    print('PEMBANTU byte-identik: %d/%d' % (len([n for n in ib if ia.get(n) == ib[n]]), len(ia)))
    return 2 if (mu or hilang or salah or beda_p) else 0


def mode_uji_diri():
    """Mutasi salinan DI MEMORI. Pemeriksaan --sidik yang sama wajib menolak tiap mutasi; keadaan asli wajib lulus."""
    acuan_b, acuan_p = baca_acuan(SIDIK), baca_acuan(SIDIK_PEMBANTU)
    if acuan_b is None or acuan_p is None:
        print('UJI-DIRI GAGAL: berkas sidik belum ada')
        return 3
    beku, pembantu = baca(BERKAS_BEKU), baca(BERKAS_PEMBANTU)
    gagal = []
    _, lulus = periksa_sidik(beku, pembantu, acuan_b, acuan_p)
    if not lulus:
        gagal.append('keadaan asli tidak lulus --sidik (uji-diri butuh pangkal yang bersih)')
    pb, hb, sb = potong_semua(beku, BEKU)
    isi = isi_pembantu(pembantu)
    mutasi = []
    # sisipkan satu spasi sebelum kurung tutup terakhir — perubahan sekecil mungkin
    if BEKU[0] in pb:
        t = pb[BEKU[0]]; mutasi.append(('mesin ' + BEKU[0], beku.replace(t, t[:-1] + ' }', 1), pembantu))
    else:
        gagal.append('%s tidak terpotong' % BEKU[0])
    if UJI_PEMBANTU_FUNGSI in isi:
        t = isi[UJI_PEMBANTU_FUNGSI]; mutasi.append(('fungsi pembantu ' + UJI_PEMBANTU_FUNGSI, beku, pembantu.replace(t, t[:-1] + ' }', 1)))
    else:
        gagal.append('%s tidak ada di pembantu.js' % UJI_PEMBANTU_FUNGSI)
    if UJI_PEMBANTU_KONSTANTA in isi:
        t = isi[UJI_PEMBANTU_KONSTANTA]; mutasi.append(('konstanta pembantu ' + UJI_PEMBANTU_KONSTANTA, beku, pembantu.replace(t, t[:-1] + ' ;', 1)))
    else:
        gagal.append('%s tidak ada di pembantu.js' % UJI_PEMBANTU_KONSTANTA)
    jangkar = '\n\nexport { '
    if beku.count(jangkar) == 1:
        mutasi.append(('fungsi baru tanpa kunci di beku.js', beku.replace(jangkar, '\n  function mesinSelundupan(x) {\n    return x;\n  }' + jangkar, 1), pembantu))
    else:
        gagal.append('jangkar ekspor beku.js tidak tunggal')
    for nama, mb, mp in mutasi:
        if mb == beku and mp == pembantu:
            gagal.append('%s: mutasi tidak terpasang (jangkar basi)' % nama)
            continue
        _, ok = periksa_sidik(mb, mp, acuan_b, acuan_p)
        if ok:
            gagal.append('%s: mutasi TIDAK terlihat oleh alat' % nama)
        else:
            print('UJI-DIRI  : mutasi pada %s terlihat (--sidik menolak)' % nama)
    # potongan mesin tidak boleh memuat 'function ' tingkat atas lain (salah potong terlalu panjang)
    for n in BEKU:
        if n not in pb:
            continue
        sisa = pb[n].lstrip('\n').split('\n', 1)[1]   # buang baris pertama (kepala fungsinya sendiri)
        if re.search(r'\n  (?:async )?function ', '\n' + sisa):
            gagal.append('%s: potongan memuat fungsi tingkat atas lain' % n)
    for n in fungsi_tingkat_atas(pembantu):
        b = isi.get(n, '')
        sisa = b.lstrip('\n').split('\n', 1)[1] if '\n' in b.lstrip('\n') else ''
        if re.search(r'\n  (?:async )?function ', '\n' + sisa):
            gagal.append('pembantu %s: potongan memuat fungsi tingkat atas lain' % n)
    if gagal:
        print('UJI-DIRI GAGAL:\n  ' + '\n  '.join(gagal))
        return 3
    print('UJI-DIRI  : lulus (alat terbukti melihat perubahan pada mesin, fungsi & konstanta pembantu, dan mesin tanpa kunci; %d mesin + %d pembantu terpotong bersih)'
          % (len(pb), len(isi)))
    return 0


def main(argv):
    if '--uji-diri' in argv:
        return mode_uji_diri()
    if '--catat' in argv:
        return mode_catat()
    if '--sidik' in argv:
        return mode_sidik()
    ref = 'main'
    if '--lama' in argv:
        i = argv.index('--lama')
        if i + 1 >= len(argv):
            print('pakai: --lama <ref>')
            return 4
        ref = argv[i + 1]
    return mode_banding(ref)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
