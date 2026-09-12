#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beku2.py — penjaga 28 MESIN UANG BEKU di index.html.

Mesin uang = fungsi yang menghitung uang/stok dari dokumen. Tubuhnya WAJIB byte-identik
antar putaran kerja, kecuali pemilik memerintahkan pembekuan ulang.

Cara memotong: menghitung kurung kurawal dari '{' pertama sesudah nama fungsi (bukan
sentinel teks), sehingga pemindahan lokasi fungsi tidak mengubah hasil. Setiap potongan
harus berakhir '  }' (kurung tutup pada indentasi dua spasi) — kalau tidak, alatnya yang
salah potong, dan alat wajib berhenti daripada meluluskan.

Mode:
  (tanpa opsi)          bandingkan index.html kerja dengan `git show <ref>:index.html`
                        (--lama <ref>, bawaan main)
  --sidik               bandingkan sha256 tiap mesin dengan alat-uji/beku.sha256 (gerbang CI)
  --catat               tulis ulang alat-uji/beku.sha256 dari index.html sekarang
                        (= PEMBEKUAN ULANG; hanya atas perintah pemilik, sebut di pesan commit)
  --uji-diri            buktikan alat ini bisa MELIHAT perubahan: mutasi salinan di memori
                        satu mesin + satu kontrol, alat wajib menangkap keduanya
Kode keluar: 0 lulus · 2 mesin berubah/hilang/salah potong · 3 uji-diri gagal · 4 salah pakai
"""
import io, os, re, sys, hashlib, subprocess

AKAR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BERKAS = os.path.join(AKAR, 'index.html')
SIDIK = os.path.join(AKAR, 'alat-uji', 'beku.sha256')

BEKU = """hitungArusKasInti hitungLabaRentang hitungLabaBersihRentang barisSusutStok bayaranBiayaBulanan
jatahBiayaBulananHari hitungStokKarungPerMerk hitungStokKemasan hitungStokBahanKemasan hitungStokBahanLiteran
hitungPiutang hitungUtangPemasok hitungUtangOwner hitungKasbon kasPada bagiBiayaAdukan hitungNeraca
hitungHppMerkDalamBatch pembulatanTunai hitungLajuPakai tbDaftarKoleksi hitungSaldoTutup tulisSaldoPembuka
saldoAmplop stokMaksJalur wzDiKeranjang thPagar thDorongRiwayat""".split()
# Kontrol positif untuk mode banding: fungsi biasa yang BOLEH berubah. Kalau mereka berubah
# tapi alat tidak melihatnya, alatnya buta.
KONTROL = ['tulisPengeluaranHarian', 'bjSimpan', 'setujuiTitipan', 'simpanPengeluaranHarian']


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


def baca(jalur):
    return io.open(jalur, encoding='utf-8').read()


def tolak_kosong(nama, teks):
    # Alat yang membandingkan berkas kosong LULUS dengan nol yang diuji.
    if len(teks) < 1000000:
        print('TOLAK: %s kosong/terpotong (%d byte)' % (nama, len(teks)))
        sys.exit(2)


def mode_banding(ref):
    baru = baca(BERKAS)
    lama = subprocess.check_output(['git', '-C', AKAR, 'show', ref + ':index.html']).decode('utf-8')
    tolak_kosong('index.html', baru)
    tolak_kosong(ref + ':index.html', lama)
    print('UKURAN    : %s %d byte, kerja %d byte' % (ref, len(lama), len(baru)))
    pa, ha, sa = potong_semua(lama, BEKU + KONTROL)
    pb, hb, sb = potong_semua(baru, BEKU + KONTROL)
    hilang = sorted(set(ha) | set(hb))
    salah = sorted(set(sa) | set(sb))
    beda = [n for n in BEKU + KONTROL if n in pa and n in pb and pa[n] != pb[n]]
    print('TERPOTONG : %d dari %d nama' % (len(BEKU + KONTROL) - len(hilang), len(BEKU + KONTROL)))
    print('TAK KETEMU: %s' % (hilang or 'nihil'))
    print('SALAH POTONG (tidak berakhir "  }"): %s' % (salah or 'nihil'))
    kp = [n for n in KONTROL if n in beda]
    print('KONTROL berubah: %s' % (kp or 'nihil (wajar bila kontrol memang tidak disentuh)'))
    mu = [n for n in beda if n in BEKU]
    print('MESIN UANG berubah    : %s' % (mu or 'nihil'))
    print('MESIN UANG byte-identik: %d/%d' % (len([n for n in BEKU if n in pa and n in pb and pa[n] == pb[n]]), len(BEKU)))
    return 2 if (mu or hilang or salah) else 0


def mode_sidik():
    if not os.path.exists(SIDIK):
        print('TOLAK: %s belum ada — jalankan --catat atas perintah pemilik' % SIDIK)
        return 4
    baru = baca(BERKAS)
    tolak_kosong('index.html', baru)
    acuan = {}
    for baris in baca(SIDIK).splitlines():
        baris = baris.strip()
        if not baris or baris.startswith('#'):
            continue
        h, n = baris.split()
        acuan[n] = h
    pb, hb, sb = potong_semua(baru, BEKU)
    beda = [n for n in BEKU if n in pb and n in acuan and sidik(pb[n]) != acuan[n]]
    tanpa_acuan = [n for n in BEKU if n not in acuan]
    print('ACUAN     : %s (%d nama)' % (os.path.relpath(SIDIK, AKAR), len(acuan)))
    print('TERPOTONG : %d dari %d mesin' % (len(pb), len(BEKU)))
    print('TAK KETEMU: %s' % (hb or 'nihil'))
    print('SALAH POTONG: %s' % (sb or 'nihil'))
    print('TANPA ACUAN : %s' % (tanpa_acuan or 'nihil'))
    print('MESIN UANG berubah    : %s' % (beda or 'nihil'))
    print('MESIN UANG byte-identik: %d/%d' % (len(BEKU) - len(beda) - len(hb) - len(tanpa_acuan), len(BEKU)))
    return 2 if (beda or hb or sb or tanpa_acuan) else 0


def mode_catat():
    baru = baca(BERKAS)
    tolak_kosong('index.html', baru)
    pb, hb, sb = potong_semua(baru, BEKU)
    if hb or sb:
        print('TOLAK: tidak bisa mencatat — tak ketemu %s, salah potong %s' % (hb, sb))
        return 2
    kepala = ('# sha256 tubuh 28 mesin uang beku (alat-uji/beku2.py --catat).\n'
              '# Berkas ini hanya boleh berubah lewat commit yang menyebut "membekukan ulang"\n'
              '# dan disetujui pemilik. CI membandingkan index.html ke berkas ini (--sidik).\n')
    with io.open(SIDIK, 'w', encoding='utf-8') as f:
        f.write(kepala)
        for n in BEKU:
            f.write('%s  %s\n' % (sidik(pb[n]), n))
    print('DICATAT   : %d sidik ke %s' % (len(BEKU), os.path.relpath(SIDIK, AKAR)))
    return 0


def mode_uji_diri():
    """Mutasi salinan DI MEMORI: satu mesin dan satu kontrol. Alat wajib melihat keduanya."""
    asli = baca(BERKAS)
    tolak_kosong('index.html', asli)
    pa, ha, sa = potong_semua(asli, BEKU + KONTROL)
    gagal = []
    if ha or sa:
        gagal.append('potongan asli bermasalah: tak ketemu %s, salah potong %s' % (ha, sa))
    for nama in (BEKU[0], KONTROL[0]):
        tubuh = pa.get(nama)
        if not tubuh:
            gagal.append('%s tidak terpotong' % nama)
            continue
        # sisipkan satu spasi sebelum kurung tutup terakhir — perubahan sekecil mungkin
        mutan = tubuh[:-1] + ' }'
        teks_mutan = asli.replace(tubuh, mutan, 1)
        pb, _, _ = potong_semua(teks_mutan, [nama])
        if pb.get(nama) == tubuh:
            gagal.append('%s: mutasi TIDAK terlihat oleh alat' % nama)
        else:
            print('UJI-DIRI  : mutasi pada %s terlihat (sidik %s -> %s)' % (nama, sidik(tubuh)[:8], sidik(pb[nama])[:8]))
    # potongan mesin tidak boleh memuat 'function ' tingkat atas lain (salah potong terlalu panjang)
    for n in BEKU:
        sisa = pa[n].lstrip('\n').split('\n', 1)[1]   # buang baris pertama (kepala fungsinya sendiri)
        if re.search(r'\n  (?:async )?function ', '\n' + sisa):
            gagal.append('%s: potongan memuat fungsi tingkat atas lain' % n)
    if gagal:
        print('UJI-DIRI GAGAL:\n  ' + '\n  '.join(gagal))
        return 3
    print('UJI-DIRI  : lulus (alat terbukti melihat perubahan pada mesin dan kontrol; %d potongan bersih)' % len(BEKU))
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
