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

Satu tempat untuk semua alat uji peramban: uji_antrean_kasir.py (juga dipakai uji_sistem_lama_bacasaja.py) dan uji_layar_kunci.py.
Diuji oleh uji_coba_ulang.py (+ --kontrol).
"""
import os, sys


def nama_uji():
    n = os.path.splitext(os.path.basename(sys.argv[0] or '?'))[0] or '?'
    return n + (' --kontrol' if '--kontrol' in sys.argv else '')


def catat(halaman, sebab, ke, dari, disengaja=None):
    """Dipanggil TEPAT sebelum halaman dimuat lagi. ke = nomor percobaan yang akan dimulai (2, 3, …), dari = batas percobaan."""
    teks = '%s · %s — %s (percobaan %d dari %d)' % (nama_uji(), halaman, sebab, ke, dari)
    if disengaja: teks += ' · DISENGAJA: ' + disengaja
    print('DICOBA ULANG: ' + teks, flush=True)
    if os.environ.get('GITHUB_ACTIONS') and not disengaja:
        print('::warning title=DICOBA ULANG::' + teks.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A'), flush=True)
