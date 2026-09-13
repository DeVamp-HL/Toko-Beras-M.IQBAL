#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bangun.py — membangun KOTAK PASIR TULIS-NOL dari index.html: tiga import gstatic Firebase
ditulis-ulang ke stub lokal, benih data (berkas backup toko, HANYA DIBACA) disisipkan sebagai
window.__data/__peta, dan kait uji disisipkan HANYA di salinan kotak. Tidak ada satu byte pun
ke Firestore sungguhan. Layani foldernya lewat http.server (modul relatif menolak file://).

  python3 alat-uji/kotak/bangun.py SUMBER.html TUJUAN.html [--benih backup.json] [--suntik 'baris js']

Kait di kotak: __simpan (simpanKeFirestore), __antrean, __kirim, __baca/__tulis (cadangan), plus
stub: __rekam, __terapkan, __terapkanDok, __setDocGagal, __urutanAwal.
"""
import io, os, re, sys, json, shutil
a = sys.argv[1:]
if len(a) < 2:
    sys.exit(__doc__)
sumber, tujuan = a[0], a[1]
benih = a[a.index('--benih') + 1] if '--benih' in a else None
suntik = a[a.index('--suntik') + 1] if '--suntik' in a else ''
akar = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
s = io.open(sumber, encoding='utf-8').read()
s, n = re.subn(r'https://www\.gstatic\.com/firebasejs/[^"]+/firebase-(app|firestore|auth)\.js', r'./stub-firebase-\1.js', s)
assert n == 3, 'specifier gstatic yang ditulis-ulang %d, harus 3' % n
seed = ''
if benih:
    b = json.load(open(benih))
    data = {k: v for k, v in b.items() if isinstance(v, list)}
    peta = {k: v for k, v in b.items() if isinstance(v, dict)}
    seed = '<script>window.__data = %s; window.__peta = %s;</script>\n' % (json.dumps(data), json.dumps(peta))
assert s.count('</head>') == 1
s = s.replace('</head>', seed + '</head>')
jangkar = '\n  async function hapusDariFirestore('
assert s.count(jangkar) == 1
kait = [('__simpan', 'simpanKeFirestore'), ('__antrean', 'ambilAntreanTunda'), ('__kirim', 'kirimAntreanTunda'),
        ('__baca', 'bacaCadanganLokal'), ('__tulis', 'tulisCadanganLokal'), ('__kasPada', 'kasPada'),
        ('__era', 'eraTutupBuku'), ('__neraca', 'hitungNeraca')]
# hanya fungsi yang ADA di sumber (kotak juga dibangun dari index.html versi lama untuk pembanding)
baris = ' '.join('window.%s = %s;' % (a, b) for a, b in kait if ('function %s(' % b) in s)
s = s.replace(jangkar, '\n  ' + baris + jangkar, 1)
if suntik:
    j = '\n  const firebaseConfig = {'
    assert s.count(j) == 1
    s = s.replace(j, '\n  ' + suntik + j, 1)
io.open(tujuan, 'w', encoding='utf-8').write(s)
# stub & lib disalin ke folder tujuan (kalau belum ada / berbeda)
folder = os.path.dirname(os.path.abspath(tujuan))
for f in ('stub-firebase-app.js', 'stub-firebase-auth.js', 'stub-firebase-firestore.js'):
    shutil.copy(os.path.join(os.path.dirname(__file__), f), os.path.join(folder, f))
lib_dst = os.path.join(folder, 'lib'); os.makedirs(lib_dst, exist_ok=True)
for f in os.listdir(os.path.join(akar, 'lib')):
    shutil.copy(os.path.join(akar, 'lib', f), os.path.join(lib_dst, f))
print('kotak:', tujuan, '| benih:', benih or '-', '| suntik:', 'ya' if suntik else '-')
