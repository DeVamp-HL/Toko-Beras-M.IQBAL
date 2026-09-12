#!/bin/zsh
# jalankan.sh — evaluasi SELURUH modul index.html di JavaScriptCore (jsc), tanpa peramban,
# tanpa jaringan, tanpa node. Membuktikan modul bisa dievaluasi sampai baris terakhir:
# satu ReferenceError/TDZ di lingkup modul = seluruh aplikasi mati (pola satu referensi
# menjatuhkan semua). Yang TIDAK diuji: isi fungsi yang baru jalan sesudah klik/snapshot.
#
#   alat-uji/harness/jalankan.sh [index.html]   → 0 lulus, 3 gagal
#   alat-uji/harness/jalankan.sh --kontrol      → buktikan harness bisa GAGAL:
#                                                 dua modul cacat sengaja wajib gagal
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
AKAR="$(cd "$DIR/../.." && pwd)"
for c in \
  /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc \
  /System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc \
  /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc; do
  [[ -x "$c" ]] && JSC="$c" && break
done
[[ -n "${JSC:-}" ]] || { echo "GAGAL: jsc tidak ditemukan"; exit 3; }
KERJA="$(mktemp -d)"
cp "$DIR"/prelude.js "$DIR"/stub-firebase-*.js "$KERJA"/ && cp "$AKAR"/lib/lz-string.js "$KERJA"/ 2>/dev/null

# Ekstrak <script type="module"> lalu tulis-ulang 3 specifier gstatic ke stub lokal.
# $1 = berkas html, $2 = folder kerja, $3 = nama modul keluaran, $4 = suntikan (opsional)
ekstrak() {
  python3 - "$1" "$2" "$3" "${4:-}" <<'PY'
import re, sys, pathlib
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
kerja = pathlib.Path(sys.argv[2]); nama = sys.argv[3]; suntik = sys.argv[4]
m = re.search(r'<script type="module">(.*?)</script>', html, re.S)
if not m: sys.exit('tidak ada <script type="module">')
js = m.group(1)
js, n = re.subn(r'https://www\.gstatic\.com/firebasejs/[^"\']+/firebase-(app|firestore|auth)\.js', r'./stub-firebase-\1.js', js)
if n != 3: sys.exit('specifier gstatic yang ditulis-ulang %d, harus 3' % n)
if suntik:
    jangkar = '\n  const firebaseConfig = {'
    if js.count(jangkar) != 1: sys.exit('jangkar suntikan tidak unik')
    js = js.replace(jangkar, '\n  ' + suntik + jangkar, 1)
(kerja / nama).write_text(js, encoding='utf-8')
(kerja / ('jalan-' + nama)).write_text(
    'import "./prelude.js";\nimport "./%s";\nprint("HARNESS SELESAI · typeof window.pindahHalaman = " + typeof globalThis.pindahHalaman);\n' % nama,
    encoding='utf-8')
PY
}

# Jalankan satu modul: cetak hasil, kembalikan 0 (lulus) / 3 (gagal)
jalan() {
  local nama="$1"
  local keluar
  keluar=$(cd "$KERJA" && "$JSC" -m "jalan-$nama" 2>&1)
  if [[ "$keluar" == *"HARNESS SELESAI · typeof window.pindahHalaman = function"* ]]; then
    echo "  $nama -> LULUS (modul dievaluasi sampai akhir, pindahHalaman terpasang)"
    return 0
  fi
  echo "  $nama -> GAGAL"
  echo "$keluar" | head -8 | sed 's/^/      /'
  return 3
}

if [[ "${1:-}" == "--kontrol" ]]; then
  echo "--- kontrol positif harness: dua modul cacat sengaja WAJIB gagal ---"
  ekstrak "$AKAR/index.html" "$KERJA" modul-tdz.mjs 'const __tdzA = __tdzB + 1; const __tdzB = 1;' || exit 3
  ekstrak "$AKAR/index.html" "$KERJA" modul-ref.mjs 'const __x = fungsiYangTidakAda();' || exit 3
  BUTA=0
  for m in modul-tdz.mjs modul-ref.mjs; do
    if jalan "$m" >/dev/null 2>&1; then echo "  $m -> LULUS padahal cacat — HARNESS BUTA"; BUTA=1; else echo "  $m -> gagal seperti seharusnya"; fi
  done
  rm -rf "$KERJA"
  [[ $BUTA -eq 0 ]] && { echo "HASIL: harness terbukti bisa melihat cacat"; exit 0; } || { echo "HASIL: HARNESS BUTA"; exit 3; }
fi

BERKAS="${1:-$AKAR/index.html}"
[[ "$BERKAS" = /* ]] || BERKAS="$PWD/$BERKAS"
echo "--- harness jsc: $(basename "$BERKAS") ---"
ekstrak "$BERKAS" "$KERJA" modul.mjs || { rm -rf "$KERJA"; exit 3; }
jalan modul.mjs; HASIL=$?
rm -rf "$KERJA"
[[ $HASIL -eq 0 ]] && echo "HASIL: lulus" || echo "HASIL: GAGAL"
exit $HASIL
