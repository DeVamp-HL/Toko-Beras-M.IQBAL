#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_jam_rinci.py — LAPORAN (tidak menulis apa pun): jam baris hasil rinci karcis kasir darurat dibanding jam karcis asalnya, dari berkas cadangan.

Aturan owner 27 Sep 2026: tiap baris rincian membawa JAM KARCIS ASLI (saat penjualan terjadi di kasir), bukan jam owner merinci; jam merinci ada di
field terpisah (dirinciPada, disimpan UTC). Laporan ini menggolongkan tiap baris rincian:
  benar                     jam baris = jam karcis asal
  jam merinci (WIB)         jam baris = dirinciPada digambar WIB
  jam merinci (UTC)         jam baris = dirinciPada dipotong UTC (meleset 7 jam)
  bergeser ±7 jam           jam baris = jam karcis ± 7 jam
  kosong                    jam baris kosong
  lain                      tidak cocok pola mana pun
  karcis asal tidak ada     karcis rinciDari tidak ada di cadangan (tidak bisa diperiksa)
Usulan koreksi (TIDAK ditulis): bulan terbuka → jam := jam karcis asal. Bulan terkunci (aturanToko/kunciPeriode.sampaiBulan) → TIDAK dikoreksi: rules
v4 menolak tulisan di bulan terkunci, dan pembalik hanya untuk uang — jam tidak mengubah uang, jadi cukup dicatat di sini.

    python3 alat-uji/periksa_jam_rinci.py _privat/backup-batch-miqbal-AAAA-BB-CC.json   → laporan (angka toko: JANGAN disalin ke repo publik)
"""
import sys, json, datetime as dt
from collections import Counter

WIB = dt.timezone(dt.timedelta(hours=7))
GOLONGAN = ['benar', 'jam merinci (WIB)', 'jam merinci (UTC)', 'bergeser ±7 jam', 'kosong', 'lain', 'karcis asal tidak ada']


def _hm(iso, tz):
    try: return dt.datetime.fromisoformat(str(iso).replace('Z', '+00:00')).astimezone(tz).strftime('%H:%M')
    except (ValueError, TypeError): return None


def _geser(jam, menit):
    try: h, m = int(jam[:2]), int(jam[3:5])
    except (ValueError, TypeError): return None
    t = (h * 60 + m + menit) % 1440
    return '%02d:%02d' % (t // 60, t % 60)


def sampai_bulan(cad):
    at = cad.get('aturanToko') or []
    for d in (at if isinstance(at, list) else []):
        if str(d.get('id')) == 'kunciPeriode': return str(d.get('sampaiBulan') or '')
    return ''


def golongkan(cad):
    """→ (Counter golongan, [baris salah {id, tanggal, jam, jamKarcis, golongan, terkunci, usulan}])"""
    P = cad.get('penjualan') or []; per_id = {str(x.get('id')): x for x in P}; kunci = sampai_bulan(cad)
    hitung = Counter(); salah = []
    for x in P:
        if not (x.get('rinciDari') and x.get('asalDarurat')): continue
        k = per_id.get(str(x['rinciDari'])); jam = str(x.get('jam') or '')[:5]; kj = str((k or {}).get('jam') or '')[:5]
        if k is None: g = 'karcis asal tidak ada'
        elif jam == kj: g = 'benar'
        elif not jam: g = 'kosong'
        elif jam == _hm(x.get('dirinciPada'), WIB): g = 'jam merinci (WIB)'
        elif jam == _hm(x.get('dirinciPada'), dt.timezone.utc): g = 'jam merinci (UTC)'
        elif jam in (_geser(kj, 420), _geser(kj, -420)): g = 'bergeser ±7 jam'
        else: g = 'lain'
        hitung[g] += 1
        if g in ('benar', 'karcis asal tidak ada'): continue
        terkunci = bool(kunci) and str(x.get('tanggal') or '')[:7] <= kunci
        salah.append({'id': x.get('id'), 'tanggal': x.get('tanggal'), 'jam': jam, 'jamKarcis': kj, 'golongan': g, 'terkunci': terkunci,
                      'usulan': 'TIDAK dikoreksi (bulan terkunci; jam tidak mengubah uang — cukup dicatat)' if terkunci else 'jam := ' + kj})
    return hitung, salah


def lapor(cad):
    hitung, salah = golongkan(cad); n = sum(hitung.values())
    out = ['Baris hasil rinci karcis: %d · kunci periode sampai: %s' % (n, sampai_bulan(cad) or '(tidak ada)')]
    out += ['  %-24s %5d' % (g, hitung.get(g, 0)) for g in GOLONGAN]
    if not salah: out.append('Tidak ada baris yang jamnya salah — tidak ada usulan koreksi.')
    else:
        out.append('Usulan koreksi (TIDAK ditulis — owner memutuskan): %d baris, %d di bulan terkunci' % (len(salah), sum(1 for s in salah if s['terkunci'])))
        out += ['  %s %s  jam %s → karcis %s  [%s] %s' % (s['id'], s['tanggal'], s['jam'], s['jamKarcis'], s['golongan'], s['usulan']) for s in salah[:50]]
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    print(lapor(json.load(open(sys.argv[1], encoding='utf-8'))))
