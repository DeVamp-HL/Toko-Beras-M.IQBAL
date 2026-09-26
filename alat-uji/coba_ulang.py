#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
coba_ulang.py — percobaan ulang halaman di uji peramban SELALU tercatat (keputusan owner 26 Sep 2026).

Tiap kali satu halaman dimuat ulang karena pemuatan sebelumnya macet, keluar satu baris di log:

    DICOBA ULANG: <nama uji> · <halaman> — <sebab> (percobaan n dari m)

dan di GitHub Actions juga satu peringatan "DICOBA ULANG" di halaman ringkasan run. Sekali-sekali = Chrome di runner yang lambat.
Kalau mulai SERING muncul, itu tanda masalah sungguhan (halamannya atau alat ujinya), bukan sekadar lambat.

Percobaan ulang yang SENGAJA dipicu kontrol (kontrol 9 uji_layar_kunci memutus Firebase supaya keluarannya wajib berkata GAGAL JARINGAN)
tetap ditulis barisnya, ditandai DISENGAJA, tanpa peringatan di halaman ringkasan — supaya hitungan di sana hanya berisi yang tidak disengaja.

Di bawah baris itu ikut dicetak ekor catatan Chrome (stderr) dari percobaan yang macet — bukti untuk menyelidiki kalau barisnya mulai sering.

Satu tempat untuk semua alat uji peramban: uji_antrean_kasir.py (juga dipakai uji_sistem_lama_bacasaja.py) dan uji_layar_kunci.py.
Diuji oleh uji_coba_ulang.py (+ --kontrol).
"""
import os, sys


def nama_uji():
    n = os.path.splitext(os.path.basename(sys.argv[0] or '?'))[0] or '?'
    return n + (' --kontrol' if '--kontrol' in sys.argv else '')


EKOR_LOG = 40


def ekor_berkas(jalur, n=EKOR_LOG):
    """→ n baris terakhir berkas catatan (Chrome stderr), [] kalau tidak ada."""
    try:
        with open(jalur, 'rb') as f: return f.read().decode('utf-8', 'replace').splitlines()[-n:]
    except OSError:
        return []


def catat(halaman, sebab, ke, dari, disengaja=None, log=None):
    """Dipanggil TEPAT sebelum halaman dimuat lagi. ke = nomor percobaan yang akan dimulai (2, 3, …), dari = batas percobaan.
    log = baris catatan Chrome dari percobaan yang macet (dicetak di bawah baris DICOBA ULANG; di GitHub Actions dalam kelompok yang bisa dibuka)."""
    teks = '%s · %s — %s (percobaan %d dari %d)' % (nama_uji(), halaman, sebab, ke, dari)
    if disengaja: teks += ' · DISENGAJA: ' + disengaja
    print('DICOBA ULANG: ' + teks, flush=True)
    if os.environ.get('GITHUB_ACTIONS') and not disengaja:
        print('::warning title=DICOBA ULANG::' + teks.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A'), flush=True)
    gha = os.environ.get('GITHUB_ACTIONS')
    baris = [b for b in (log or [])][-EKOR_LOG:]
    print(('::group::' if gha else '  ') + 'catatan Chrome dari percobaan %d (%d baris terakhir)%s' % (ke - 1, len(baris), '' if baris else ' — kosong'), flush=True)
    for b in baris: print('    ' + b.replace('::', ': :'), flush=True)   # baris Chrome tidak boleh terbaca sebagai perintah Actions
    if gha: print('::endgroup::', flush=True)
