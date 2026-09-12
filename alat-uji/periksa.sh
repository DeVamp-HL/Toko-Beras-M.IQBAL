#!/bin/zsh
# Pemeriksaan wajib sebelum commit (file 27, butir 1-4).
# Pengganti node/esbuild yang tidak ada di mesin ini:
#   - sintaks  : jsc (JavaScriptCore bawaan macOS) via checkSyntax()
#   - chrome80 : pemindaian statis sintaks pasca-Chrome-80 (lebih lemah dari esbuild)
# Jalankan dari mana saja:  alat-uji/periksa.sh [berkas]  (bawaan index.html di akar repo)
set -u
AKAR="$(cd "$(dirname "$0")/.." && pwd)"
BERKAS="${1:-$AKAR/index.html}"
[[ "$BERKAS" = /* ]] || BERKAS="$PWD/$BERKAS"
for c in /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc; do [[ -x "$c" ]] && JSC="$c" && break; done
[[ -n "${JSC:-}" ]] || { echo "GAGAL: jsc tidak ditemukan"; exit 1; }
KERJA="$(mktemp -d)"
GAGAL=0

python3 - "$BERKAS" "$KERJA" <<'PY'
import re, sys, pathlib
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
kerja = pathlib.Path(sys.argv[2])
n = 0
for m in re.finditer(r'<script([^>]*)>(.*?)</script>', html, re.S | re.I):
    atribut, isi = m.group(1), m.group(2)
    if 'src=' in atribut.lower():
        continue
    n += 1
    modul = 'module' in atribut.lower()
    baris = html[:m.start()].count('\n') + 1
    (kerja / f'blok{n}.js').write_text(isi, encoding='utf-8')
    (kerja / f'blok{n}.info').write_text(f'{"module" if modul else "classic"} baris {baris}', encoding='utf-8')
print(n)
PY

echo "--- 1 · sintaks (jsc checkSyntax) ---"
for f in "$KERJA"/blok*.js; do
  info=$(cat "${f%.js}.info")
  # Dua pintu berbeda di jsc, dan keduanya menerima masukan yang berbeda pula:
  #   checkSyntax(JALUR)        — skrip klasik. Diberi sumber, ia mengeluh
  #                               "Could not open file" dan semua berkas tampak gagal.
  #   checkModuleSyntax(SUMBER) — modul. Ini yang benar untuk <script type="module">;
  #                               checkSyntax akan menolak `import` di baris pertama.
  if [[ "$info" == module* ]]; then
    hasil=$("$JSC" -e "try { checkModuleSyntax(readFile('$f')); print('LULUS'); } catch (e) { print('GAGAL: ' + e); }" 2>&1)
  else
    hasil=$("$JSC" -e "try { checkSyntax('$f'); print('LULUS'); } catch (e) { print('GAGAL: ' + e); }" 2>&1)
  fi
  echo "  $(basename $f) [$info] -> $hasil"
  [[ "$hasil" == LULUS* ]] || GAGAL=1
done

echo "--- 2 · sintaks pasca-Chrome-80 (pengganti esbuild) ---"
POLA='\?\?=|\|\|=|&&=|\.at\(|\.replaceAll\(|Object\.hasOwn|structuredClone|\.findLast|\.toSorted|\.flatMap\(|#[a-zA-Z]+ *=|\.hasIndices'
if grep -n -E "$POLA" "$KERJA"/blok*.js > "$KERJA/temuan.txt"; then
  echo "  DITEMUKAN — periksa manual:"; sed 's/^/    /' "$KERJA/temuan.txt"; GAGAL=1
else
  echo "  LULUS — tidak ada sintaks pasca-Chrome-80"
fi

# Gerbang CSS pasca-Chrome-80 DICABUT atas keputusan My DeV (7 Agu 2026).
# Alasannya diverifikasi di berkas yang benar-benar hidup di live: 'inset:' dipakai
# 9 tempat dan 'gap:' 45 tempat — dua-duanya lahir sesudah Chrome 80 — dan toko
# jalan normal berbulan-bulan. Target chrome80 hanya pernah berlaku untuk JS.

echo "--- 3 · id ganda ---"
grep -o -E 'id="[A-Za-z0-9_-]+"' "$BERKAS" | sort | uniq -d > "$KERJA/ganda.txt"
if [[ -s "$KERJA/ganda.txt" ]]; then echo "  GAGAL:"; sed 's/^/    /' "$KERJA/ganda.txt"; GAGAL=1; else echo "  LULUS"; fi

echo "--- 4 · onclick ke fungsi yang tidak ada ---"
grep -o -E 'on(click|input|change)="[a-zA-Z_$][a-zA-Z0-9_$]*\(' "$BERKAS" \
  | sed -E 's/.*"([a-zA-Z_$][a-zA-Z0-9_$]*)\(/\1/' | sort -u \
  | grep -v -x -E 'namaFungsi|alert|confirm|prompt' > "$KERJA/dipanggil.txt"   # contoh di komentar + global peramban
grep -o -E '(function [a-zA-Z_$][a-zA-Z0-9_$]*|window\.[a-zA-Z_$][a-zA-Z0-9_$]* *=|(const|let|var) [a-zA-Z_$][a-zA-Z0-9_$]* *= *(function|\())' "$BERKAS" \
  | sed -E 's/^function //; s/^window\.//; s/^(const|let|var) //; s/ *=.*//' | sort -u > "$KERJA/ada.txt"
comm -23 "$KERJA/dipanggil.txt" "$KERJA/ada.txt" > "$KERJA/hilang.txt"
if [[ -s "$KERJA/hilang.txt" ]]; then echo "  PERIKSA MANUAL:"; sed 's/^/    /' "$KERJA/hilang.txt"; else echo "  LULUS"; fi

echo "--- 5 · getElementById ke id yang tidak ada di HTML ---"
grep -o -E "getElementById\('[A-Za-z0-9_-]+'\)" "$BERKAS" | sed -E "s/.*'([A-Za-z0-9_-]+)'.*/\1/" | sort -u > "$KERJA/dicari.txt"
grep -o -E 'id="[A-Za-z0-9_-]+"' "$BERKAS" | sed -E 's/id="(.*)"/\1/' | sort -u > "$KERJA/idAda.txt"
comm -23 "$KERJA/dicari.txt" "$KERJA/idAda.txt" > "$KERJA/idHilang.txt"
if [[ -s "$KERJA/idHilang.txt" ]]; then echo "  PERIKSA MANUAL (bisa jadi id dinamis):"; sed 's/^/    /' "$KERJA/idHilang.txt"; else echo "  LULUS"; fi

echo "--- 6 · batas gerak ---"
# MANDAT DESAIN v2 (14 Agu 2026, perintah pemilik): jatah gerak lama DICABUT untuk
# SISTEM UTAMA — index.html bebas beranimasi (Platina Malam). Berkas kasir tetap
# ketat: HP pegawai adalah alasan lahirnya aturan ini.
if [[ "$(basename "$BERKAS")" == "index.html" ]]; then
  echo "  DILEWATI — mandat desain v2: gerak bebas untuk sistem utama (kasir tetap dijaga)"
  echo
  [[ $GAGAL -eq 0 ]] && echo "HASIL: lulus" || echo "HASIL: ADA YANG GAGAL"
  rm -rf "$KERJA"
  exit $GAGAL
fi
# Dua pengecualian yang memang tertulis di spesifikasi, jadi tidak dihitung pelanggaran:
#   denyutAntrean = satu-satunya gerak berulang yang diizinkan (antrean offline)
#   sorotAngka 400ms = dari spesifikasi Sistem Gerak
grep -n -E 'infinite|transition:[^;]*(box-shadow|filter|background|width|height|top|left|color)' "$BERKAS" \
  | grep -v 'denyutAntrean' > "$KERJA/gerak.txt"
if [[ -s "$KERJA/gerak.txt" ]]; then
  echo "  GAGAL — gerak di luar transform/opacity, atau berulang tanpa informasi:"
  head -20 "$KERJA/gerak.txt" | sed 's/^/    /'; GAGAL=1
else echo "  LULUS (denyutAntrean dikecualikan sesuai spek)"; fi
grep -n -E '(animation|transition)[^;]*[0-9]{3,4}ms' "$BERKAS" | grep -v -E 'sorotAngka|angka-berubah' \
  | grep -o -E '[0-9]{3,4}ms' | sort -u | awk -F'ms' '$1>350 {print "    GAGAL durasi >350ms: "$1"ms"; g=1} END{exit 0}'

echo
[[ $GAGAL -eq 0 ]] && echo "HASIL: lulus" || echo "HASIL: ADA YANG GAGAL"
rm -rf "$KERJA"
exit $GAGAL
