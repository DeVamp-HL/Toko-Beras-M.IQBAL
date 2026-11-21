#!/usr/bin/env bash
# Pasang / perbarui fungsi notifikasi HP owner — dijalankan OWNER di Google Cloud Shell (console.cloud.google.com, ikon ">_" kanan atas),
# dengan akun Google pemilik proyek. Tidak ada kunci rahasia yang disimpan di repo atau di GitHub.
#
#   git clone https://github.com/DeVamp-HL/Toko-Beras-M.IQBAL.git && cd Toko-Beras-M.IQBAL && bash functions/pasang.sh
#
# Yang dilakukan: (1) membaca lokasi database Firestore proyek → lokasi fungsi (pemicu wajib satu lokasi dengan database), ditulis ke
# functions/.env; (2) memasang paket fungsi; (3) firebase deploy --only functions. Firebase CLI meminta login sekali (ikuti tautannya) dan
# menawarkan menyalakan API yang dibutuhkan (Cloud Functions, Cloud Build, Artifact Registry, Eventarc, Cloud Run, Pub/Sub) — jawab Y.
# Tidak menyentuh rules Firestore (rules tetap diterbitkan owner lewat Console).
set -euo pipefail
PROYEK="${PROYEK:-toko-beras-m-iqbal}"
cd "$(dirname "$0")"

LOKASI_DB="$(gcloud firestore databases describe --database='(default)' --project="$PROYEK" --format='value(locationId)' 2>/dev/null || true)"
if [ -z "$LOKASI_DB" ]; then echo "Lokasi database Firestore tidak terbaca (gcloud). Jalankan lagi di Cloud Shell proyek $PROYEK."; exit 1; fi
LOKASI="$(node -e "console.log(require('./pesan').lokasiFungsi(process.argv[1]))" "$LOKASI_DB")"
echo "Database Firestore: $LOKASI_DB → fungsi dipasang di: $LOKASI"
printf 'LOKASI=%s\n' "$LOKASI" > .env

npm install --no-audit --no-fund
cd ..
npx --yes firebase-tools@15 deploy --only functions --project "$PROYEK"
echo "Selesai. Di HP / Mac: Menu › Toko ini › Perangkat & antrean › Notifikasi di perangkat ini › Nyalakan."
