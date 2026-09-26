#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beban_kasir_darurat.py — UJI BEBAN: skenario kasir darurat uji_antrean_kasir.py (utama → muat ulang, profil sama, seperti HP) diulang N kali,
SATU Chrome sekali jalan. Tiap pasangan juga DIPERIKSA (periksa_peramban), jadi yang diukur bukan cuma macet, tapi hasil yang benar.

HANYA DI RUNNER GITHUB (CLAUDE.md, keputusan owner 27 Sep 2026): menolak jalan di luar GitHub Actions. Uji beban di Mac owner pernah membuat
WindowServer ambruk (kernel panic) — docs/catatan-uji-peramban.md.

Menghitung per jalan: pemuatan Chrome, DICOBA ULANG (tiap panggilan coba_ulang.catat), pasangan yang pemeriksaannya gagal, dan — alat uji
sesudah 27 Sep saja — Chrome yang tidak mau ditutup baik-baik sesudah hasil masuk (STAT['chrome_ditutup_paksa'], bukan percobaan ulang).

    python3 alat-uji/beban_kasir_darurat.py --pasangan 100 [--alat DIR] [--label L] [--keluar F.json] [--ukur-saja]
        --alat DIR   folder alat-uji yang dipakai (mis. salinan main sebagai pembanding "sebelum"); bawaan: folder berkas ini
        --ukur-saja  selalu keluar 0 (untuk pembanding "sebelum": yang dicari angkanya, bukan lulus)
    python3 alat-uji/beban_kasir_darurat.py --ringkas SEBELUM.json SESUDAH.json   → tabel Markdown sebelum ↔ sesudah
"""
import os, re, sys, json, time


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def ringkas(berkas):
    data = []
    for b in berkas:
        try: data.append(json.load(open(b)))
        except (OSError, ValueError): data.append({'label': os.path.basename(b), 'galat': 'tidak ada hasil'})
    out = ['## Uji beban kasir darurat — sebelum ↔ sesudah', '',
           '| alat uji | pasangan | pemuatan Chrome | **DICOBA ULANG** | pasangan gagal diperiksa | Chrome dimatikan paksa sesudah hasil | menit |',
           '|---|---|---|---|---|---|---|']
    for d in data:
        if d.get('galat'): out.append('| %s | %s | | | | | |' % (d.get('label'), d['galat'])); continue
        ctm = d.get('chrome_ditutup_paksa')
        out.append('| %s (%s) | %d | %d | **%d** | %d | %s | %.1f |' % (
            d['label'], d.get('alat', '?'), d['pasangan'], d['muat'], d['dicoba_ulang'], d['pasangan_gagal'],
            '— (alat lama tidak menghitung)' if ctm is None else ctm, d['detik'] / 60))
    for d in data:
        if d.get('contoh_gagal'): out += ['', '**%s — contoh pemeriksaan gagal:** %s' % (d['label'], '; '.join(d['contoh_gagal'][:5]))]
    print('\n'.join(out))


def main():
    if '--ringkas' in sys.argv:
        return ringkas(sys.argv[sys.argv.index('--ringkas') + 1:]) or 0
    if not os.environ.get('GITHUB_ACTIONS'):
        print('UJI BEBAN HANYA DI RUNNER GITHUB (CLAUDE.md): di Mac owner paling banyak 2 Chrome sekaligus, uji beban/berulang dilarang. '
              'Jalankan workflow "Uji beban peramban".')
        return 2
    n = int(arg('--pasangan', '100')); label = arg('--label', 'sesudah')
    alat = os.path.abspath(arg('--alat') or os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, alat)
    import coba_ulang            # dari folder --alat (sys.path[0]) — modul yang SAMA dengan yang dipanggil uji_antrean_kasir
    import uji_antrean_kasir as U
    hitung = {'dicoba_ulang': 0}
    asli = coba_ulang.catat
    def catat(*a, **k):
        hitung['dicoba_ulang'] += 1
        return asli(*a, **k)
    coba_ulang.catat = catat     # U memanggil coba_ulang.catat lewat modulnya → setiap percobaan ulang terhitung
    teks = U.baca_semua()
    versi_sw = re.search(r"const VERSI = '([^']+)';", teks['sw-kasir.js']).group(1)
    stat = getattr(U, 'STAT', None)
    t0 = time.time(); gagal = 0; contoh = []
    print('BEBAN %s · alat %s · %d pasangan kasir darurat (%d pemuatan) · satu Chrome sekali jalan' % (label, alat, n, 2 * n), flush=True)
    for i in range(1, n + 1):
        u, m = U.jalankan_berkas(U.DARURAT)
        g = [x for x in U.periksa_peramban(U.DARURAT, u, m, versi_sw) if not x[1]]
        if g:
            gagal += 1; contoh.append('pasangan %d: %s' % (i, g[0][0][:120]))
            print('  ✗ pasangan %d: %s' % (i, g[0][0][:160]), flush=True)
        if i % 10 == 0 or i == n:
            print('  [%s] %d/%d pasangan · DICOBA ULANG %d · gagal %d%s · %.1f mnt' % (
                label, i, n, hitung['dicoba_ulang'], gagal,
                '' if stat is None else ' · Chrome dimatikan paksa %d' % stat['chrome_ditutup_paksa'], (time.time() - t0) / 60), flush=True)
    hasil = {'label': label, 'alat': os.path.relpath(alat, os.getcwd()) if alat.startswith(os.getcwd()) else alat,
             'pasangan': n, 'muat': stat['muat'] if stat else 2 * n + hitung['dicoba_ulang'], 'dicoba_ulang': hitung['dicoba_ulang'],
             'pasangan_gagal': gagal, 'chrome_ditutup_paksa': stat['chrome_ditutup_paksa'] if stat else None,
             'detik': time.time() - t0, 'contoh_gagal': contoh}
    if arg('--keluar'): json.dump(hasil, open(arg('--keluar'), 'w'), ensure_ascii=False, indent=1)
    print('BEBAN %s SELESAI: %s' % (label, json.dumps({k: v for k, v in hasil.items() if k != 'contoh_gagal'}, ensure_ascii=False)), flush=True)
    return 0 if ('--ukur-saja' in sys.argv or not gagal) else 1


if __name__ == '__main__':
    sys.exit(main())
