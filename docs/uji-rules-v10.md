# Uji rules v10 di server — B3 surat jalan & antar (TERBIT 18 Nov 2026 ±04.43 WIB)

v10 = v9 FINAL + **dua blok baru & tiga fungsinya** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v9`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik kedua blok & ketiga fungsi itu lalu membandingkan sisanya huruf demi huruf dengan v9.

## Yang berubah v9 → v10 (dua)

1. **(v10-1) Surat jalan** (`suratJalan`). Dibaca owner, ben, karyawan. Dibuat owner atau **ben** BERSAMA notanya (`stafBuatSJ`): status `berangkat`,
   atas nama penulisnya, tanpa kolom penerimaan / keputusan. Pengantar (**ben atau karyawan**) menandai surat jalan yang masih di jalan jadi `diterima` atau
   `gagal` (`stafTandaiSJ`) — kolom yang boleh berubah dibatasi (status, riwayat, penerima, jam terima, bukti, uang yang diterima, alasan gagal, atribusi
   ubah); isi, alamat, nilai nota, tagihan tidak bisa diubah pengantar. Membatalkan & menghapus = owner. Uang bayar di tempat masuk lewat pelunasan piutang
   (`piutangMutasi` bayar) yang sudah terbuka untuk ben & karyawan sejak v3 — rules uang tidak berubah.
2. **(v10-2) Bukti terima** (`buktiTerima`): tanda tangan & foto penerima. Dibaca owner, ben, karyawan; dibuat owner atau ben / karyawan atas nama
   sendiri dengan bentuk `buktiSah` (id = id dokumen, `idSJ` teks, `jenisBukti` ttd / foto, jenis gambar, base64 ≤ 960.000 huruf ≈ 700 KB); tanpa ubah;
   hapus owner. Koleksi ini sengaja tidak didengar aplikasi (dibaca saat surat jalan dibuka) — sama dengan foto bon pemasok.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabang B3 digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v10 terbit, nota yang DIANTAR ditolak server
   (surat jalannya ikut satu kiriman) dan tanda "diterima" dari tablet ditolak. Nota biasa (tanpa antar) tetap jalan.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

Isi "SJ": `{ id: "uji-v10-sj", noSJ: "SJ26-XXX-0001", tanggal: "2026-10-09", jam: "10:00", trxIdJual: "1", namaPelanggan: "Contoh", alamat: "uji", pengantar: "UJI B", nilaiNota: 50000, ongkir: 0, bayarDiTempat: false, tagihRp: 0, status: "berangkat", olehUid: "uid-uji-b" }`.
Isi "BUKTI": `{ id: "uji-v10-bukti", idSJ: "uji-v10-sj", noSJ: "SJ26-XXX-0001", jenisBukti: "ttd", jenis: "image/png", base64: "iVBORw0KGgo=", olehUid: "uid-uji-b" }`.
Angka (`nilaiNota`, `ongkir`, `tagihRp`) diisi jenis **int64**.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★L2 | owner@ | create `suratJalan/uji-v10-sj` | SJ | LOLOS | owner selalu boleh membuat surat jalan |
| 2 | ★L3 | owner@ | update `suratJalan/uji-v10-sj` | SJ dengan `status: "batal"`, `alasanBatal: "uji"` | LOLOS | membatalkan = owner |
| 3 | ★L4 | owner@ | create `buktiTerima/uji-v10-bukti` | BUKTI | LOLOS | owner menyimpan bukti |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; ★L6 ★L7 ★L8 ★L17 memakai peran **karyawan**) dan
dokumen `suratJalan/uji-v10-sj` = SJ untuk kasus update / baca / hapus. Tanpa itu cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server).
"TANDA" = `status: "diterima"`, `penerima: "uji"`, `diterimaPada: "x"`, `buktiTtd: ["1"]`, `diubahOlehUid: "uid-uji-b"`, `diubahOleh: "UJI B"`.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★L1 | staf aktif (ben) | create `suratJalan/uji-v10-sj` | SJ | LOLOS | ben membuat surat jalan bersama notanya (v10-1) |
| ★L5 | staf aktif (ben) | update `suratJalan/uji-v10-sj` | SJ + TANDA | LOLOS | pengantar menandai diterima |
| ★L6 | staf aktif peran **karyawan** | update `suratJalan/uji-v10-sj` | SJ + TANDA | LOLOS | karyawan yang mengantar menandai diterima |
| ★L7 | staf aktif peran **karyawan** | update `suratJalan/uji-v10-sj` | SJ dengan `status: "gagal"`, `alasanGagal`, `diubahOlehUid` | LOLOS | gagal antar (barang kembali) |
| ★L8 | staf aktif peran **karyawan** | create `suratJalan/uji-v10-sj` | SJ | DITOLAK | bikin surat jalan = owner & ben |
| ★L9 | staf aktif (ben) | create `suratJalan/uji-v10-sj` | SJ dengan `status: "diterima"` | DITOLAK | surat jalan baru selalu "berangkat" |
| ★L10 | staf aktif (ben) | create `suratJalan/uji-v10-sj` | SJ dengan `penerima` | DITOLAK | kolom penerimaan tidak boleh di surat jalan baru |
| ★L11 | staf aktif (ben) | update `suratJalan/uji-v10-sj` | SJ + TANDA + `tagihRp: 1` | DITOLAK | pengantar tidak mengubah tagihan |
| ★L12 | staf aktif (ben) | update `suratJalan/uji-v10-sj` (sudah `diterima`) | SJ dengan `status: "gagal"` | DITOLAK | yang sudah ditandai tidak ditandai ulang |
| ★L13 | staf aktif (ben) | update `suratJalan/uji-v10-sj` | SJ dengan `status: "batal"` | DITOLAK | membatalkan = owner |
| ★L14 | staf aktif (ben) | update `suratJalan/uji-v10-sj` | SJ + TANDA dengan `diubahOlehUid: "uid-lain"` | DITOLAK | pengubah bukan yang mengaku |
| ★L15 | staf aktif (ben) | create `suratJalan/uji-v10-sj` | SJ dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |
| ★L16 | staf aktif (ben) | create `buktiTerima/uji-v10-bukti` | BUKTI | LOLOS | pengantar menyimpan tanda tangan (v10-2) |
| ★L17 | staf aktif peran **karyawan** | create `buktiTerima/uji-v10-bukti` | BUKTI dengan `jenisBukti: "foto"`, `jenis: "image/jpeg"` | LOLOS | pengantar menyimpan foto |
| ★L18 | staf aktif (ben) | create `buktiTerima/uji-v10-bukti` | BUKTI dengan `idSJ: ""` | DITOLAK | bukti wajib menunjuk surat jalan |
| ★L19 | staf aktif (ben) | create `buktiTerima/uji-v10-bukti` | BUKTI dengan `jenis: "text/html"` | DITOLAK | hanya gambar |
| ★L20 | staf aktif (ben) | update `buktiTerima/uji-v10-bukti` | BUKTI dengan `base64: "AAAA"` | DITOLAK | bukti tidak bisa diubah |
| ★L21 | staf aktif (ben) | delete `suratJalan/uji-v10-sj` | — | DITOLAK | hapus = owner |
| ★L22 | staf aktif (ben) | get `suratJalan/uji-v10-sj` | — | LOLOS | tablet membaca daftar antar |
| ★L23 | kasir@ | get `suratJalan/uji-v10-sj` | — | DITOLAK | kasir darurat tidak membaca surat jalan |
| ★L24 | akun tanpa aksesAkun (`baru1`) | create `suratJalan/uji-v10-sj` | SJ dengan `olehUid: "baru1"` | DITOLAK | bukan staf aktif |

Di **v9** semua kasus yang LOLOS di atas DITOLAK (koleksinya belum punya blok — v10 yang membukanya); kasus yang DITOLAK tetap ditolak.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V10** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-24 kasus di
atas atas `firestore.rules` (v10) dan atas `firestore.rules.v9` — yang berbeda wajib persis kasus yang dibuka v10 — plus kontrol (satu suku v10 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v9, v8 & v7 lama tetap dijalankan atas v10 dan wajib sama hasilnya.

## Hasil Playground & terbit (18 Nov 2026)

- Isi editor Console sebelum uji = `firestore.rules` cabang ini, byte demi byte (SHA-256 berawalan `1665c3b8`, 56.847 byte); dicek ulang sesudah ketiga kasus.
- Wajib owner, akun owner (`uid-uji`, provider password, email owner di payload):
  ★L2 create `suratJalan/uji-v10-sj` isian SJ (14 kolom; `nilaiNota`, `ongkir`, `tagihRp` jenis int64, `bayarDiTempat` boolean) → "Simulated write allowed"
  (LOLOS, sesuai); ★L3 update `suratJalan/uji-v10-sj` SJ dengan `status: "batal"` + `alasanBatal: "uji"` → "Simulated write allowed" (LOLOS, sesuai);
  ★L4 create `buktiTerima/uji-v10-bukti` isian BUKTI → "Simulated write allowed" (LOLOS, sesuai; rincian Playground menilai `buktiSah`).
- Owner klik **Publish** 18 Nov 2026 ±04.43 WIB (riwayat Console "Today • 4:43 AM"; sebelumnya v9 "Today • 1:37 AM"). Sesudah halaman dimuat ulang,
  aturan yang berlaku = berkas ini (sidik sama, baris 2 `ATURAN FIRESTORE v10 FINAL`, tanpa draf tertunda).
