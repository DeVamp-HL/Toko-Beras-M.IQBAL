#!/usr/bin/env bash
# Pasang / perbarui fungsi notifikasi HP owner — dijalankan OWNER di Google Cloud Shell (console.cloud.google.com, ikon ">_" kanan atas),
# dengan akun Google pemilik proyek. Tidak ada kunci rahasia yang disimpan di repo atau di GitHub.
#
#   git clone https://github.com/DeVamp-HL/Toko-Beras-M.IQBAL.git && cd Toko-Beras-M.IQBAL && bash functions/pasang.sh
#
# Yang dilakukan: (1) membaca lokasi database Firestore proyek → lokasi fungsi (pemicu wajib satu lokasi dengan database), ditulis ke
# functions/.env; (2) memasang paket fungsi; (3) firebase deploy --only functions. Firebase CLI meminta login sekali (ikuti tautannya) dan
# menawarkan menyalakan API yang dibutuhkan (Cloud Functions, Cloud Build, Artifact Registry, Eventarc, Cloud Run, Pub/Sub, Cloud Scheduler) — jawab Y.
# Sejak paket Banding pemasok (26 Nov 2026) ikut fungsi terjadwal tarikAcuan (Jumat 06.00 WIB, harga acuan beras Panel Harga Bapanas → aturanToko/acuanTarik).
# Sejak tablet saat owner pergi (28 Nov 2026, rules v27): kabarJaga (absen jaga → "Toko dibuka" / "Ganti jaga") dan periksaToko (tiap 15 menit 06.00–23.45 WIB:
# belum buka / belum tutup / tablet putus / catatan nyangkut). Rules v27 WAJIB sudah terbit sebelum fungsi ini dipasang (tablet menulis jagaLog).
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
echo "Tarik harga acuan jalan tiap Jumat 06.00 WIB — hasilnya di Harga & Pemasok › Banding pemasok › Harga acuan (Pakai satu per satu)."
echo "Kabar toko (buka, ganti jaga, belum buka/tutup, tablet putus) diatur di Menu › Toko ini › Peran & persetujuan › Orang di tablet › Kabar ke HP owner."
