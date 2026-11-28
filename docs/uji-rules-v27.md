# Uji rules v27 di server — tablet saat owner pergi (DRAF 28 Nov 2026)

v27 = v26 FINAL (aktif sejak 27 Nov 2026 ±16.02 WIB) + **baca `fotoBon` yang diperluas, satu sambungan `create` persetujuan, empat fungsi baru (`stafHak` +
pembantunya `hakDari`, `stafUsulTablet`, `stafJaga`, `stafFotoBukti`), dan dua blok baru (`jagaLog`, `fotoBukti`)** (berkas kanonik `firestore.rules`; pembanding
`firestore.rules.v26`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v26.

## Yang berubah v26 → v27

1. **(v27-1) `fotoBon` read: + Penjaga laci yang DITANDAI owner** — owner 28 Nov 2026: staf penjaga laci "bisa liat nota dari pemasok dan foto nota atas izin gua
   melalui hak izin akses melalui peran dan hak yang bisa gua atur di akun owner". Tanda = `aksesAkun/{uid}.hakFotoNota == true` (ditulis owner lewat Menu › Toko ini ›
   Peran & persetujuan › Hak tablet per peran; satu `get()` seperti hak lain). Karyawan & akun nonaktif tidak bisa. **Tulis & hapus foto tetap seperti v26.**
2. **(v27-2) `persetujuan` create: + `stafUsulTablet`** — USUL dari tablet yang baru berlaku sesudah owner setujui di HP: `hargaJual` (usul harga jual katalog),
   `belanja` (daftar belanja ke pemasok), `kabarToko` (barang habis / di bawah stok minimum / jual di bawah harga minimum), `tugasSelesai` (jawaban tugas owner,
   foto bila diminta). Bentuk "menunggu", atas nama penulisnya (`mintaUid`), kalimat 1–500 huruf, tanpa kolom keputusan / `dipakai`. Isi ubahannya dihitung ulang
   di perangkat owner sebelum memutus (rules tidak mengikat rupiahnya — owner yang menyetujui).
3. **(v27-3) blok `jagaLog`** — ABSEN JAGA, satu catatan tiap PIN "Siapa yang jaga?" berhasil:
   - read: owner (rekap absen; kabar buka / ganti jaga dikirim fungsi server `kabarJaga`);
   - create: owner, atau Penjaga laci / karyawan atas nama penulisnya — `id` = id dokumen, tanggal `YYYY-MM-DD`, jam `HH:MM`, nama 1–40 huruf, peran ben | karyawan,
     kolom dibatasi;
   - ubah & hapus: owner.
4. **(v27-4) blok `fotoBukti`** — FOTO BUKTI yang DIMINTA owner (tugas berwajib foto):
   - read: owner;
   - create: owner, atau Penjaga laci / karyawan atas nama penulisnya — `id` = id dokumen, `tugasId` 1–40 huruf, jenis gambar, base64 ≤ 960.000 huruf, kolom dibatasi;
   - hapus: owner; tanpa ubah.

Tidak ada rupiah, kg, atau tanggal buku yang dikunci periode di koleksi baru. **Terbitkan v27 SEBELUM PR cabang `fitur/tablet-pergi` digabung** — tanpa v27:
usul harga jual / daftar belanja / kabar toko / tugas selesai dari tablet, absen jaga, dan foto bukti ditolak server (antrean tablet menyebutnya "DITOLAK"),
dan foto nota tidak tampil di tablet. Penjualan, barang masuk, titipan, tutup hari tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: pasang ulang fungsi server di Cloud Shell (`git pull && bash functions/pasang.sh` — `kabarJaga` & `periksaToko` baru,
   `kabarOwner` / `kabarDariOwner` diperbarui). Lalu Menu › Toko ini › Peran & persetujuan › **Hak tablet per peran** — nyalakan yang lu izinkan; Menu › Toko ini ›
   **Kabar toko** — jam buka / tutup.

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★TP1 | owner@ | create `jagaLog/jg-uji-1` | absen jaga (dokumen kosong — owner tidak dibatasi bentuk) | LOLOS | owner boleh mencatat absen |
| 2 | ★TP2 | owner@ | get `jagaLog/jg-uji-1` | — | LOLOS | rekap absen di HP / Mac owner |
| 3 | ★TP3 | owner@ | get `fotoBukti/fb-uji-1` | — | LOLOS | owner membuka foto bukti yang ia minta |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; kasus karyawan = peran diganti karyawan; kasus "bertanda
hakFotoNota" = U11 + `hakFotoNota: true`). Tanpa itu cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib |
|---|---|---|---|---|
| ★TP4 | Penjaga laci | create `persetujuan/tp-uji-1` | Penjaga laci mengusulkan harga jual | LOLOS |
| ★TP5 | karyawan | create `persetujuan/tp-uji-1` | karyawan mengirim kabar toko (barang habis) | LOLOS |
| ★TP6 | Penjaga laci | create `persetujuan/tp-uji-1` | Penjaga laci mengirim daftar belanja | LOLOS |
| ★TP7 | Penjaga laci | create `persetujuan/tp-uji-1` | Penjaga laci menjawab tugas owner | LOLOS |
| ★TP8 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet langsung "disetujui" | DITOLAK |
| ★TP9 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet atas nama orang lain (mintaUid) | DITOLAK |
| ★TP10 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet membawa kolom keputusan (diputusPada) | DITOLAK |
| ★TP11 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet bertindakan lain (hargaPokok) | DITOLAK |
| ★TP12 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet tanpa teks | DITOLAK |
| ★TP13 | Penjaga laci | create `persetujuan/tp-uji-1` | usul tablet ditandai "dipakai" | DITOLAK |
| ★TP14 | Penjaga laci | create `jagaLog/jg-uji-1` | Penjaga laci mencatat absen jaga atas namanya | LOLOS |
| ★TP15 | karyawan | create `jagaLog/jg-uji-1` | karyawan mencatat absen jaga | LOLOS |
| ★TP16 | Penjaga laci | create `jagaLog/jg-uji-1` | absen jaga atas nama akun lain (olehUid) | DITOLAK |
| ★TP17 | Penjaga laci | create `jagaLog/jg-uji-1` | absen jaga membawa kolom lain (hargaTotal) | DITOLAK |
| ★TP18 | Penjaga laci | create `jagaLog/jg-uji-1` | absen jaga: id beda dari id dokumen | DITOLAK |
| ★TP19 | Penjaga laci | create `jagaLog/jg-uji-1` | absen jaga: peran owner | DITOLAK |
| ★TP20 | Penjaga laci | get `jagaLog/jg-uji-1` | Penjaga laci membaca absen jaga | DITOLAK |
| ★TP21 | Penjaga laci | update `jagaLog/jg-uji-1` | Penjaga laci mengubah absen jaga | DITOLAK |
| ★TP22 | Penjaga laci | create `fotoBukti/fb-uji-1` | Penjaga laci mengirim foto bukti | LOLOS |
| ★TP23 | Penjaga laci | create `fotoBukti/fb-uji-1` | foto bukti bukan gambar (text/html) | DITOLAK |
| ★TP24 | Penjaga laci | create `fotoBukti/fb-uji-1` | foto bukti tanpa tugasId | DITOLAK |
| ★TP25 | Penjaga laci | get `fotoBukti/fb-uji-1` | Penjaga laci membaca foto bukti | DITOLAK |
| ★TP26 | Penjaga laci | delete `fotoBukti/fb-uji-1` | Penjaga laci menghapus foto bukti | DITOLAK |
| ★TP27 | Penjaga laci bertanda hakFotoNota | get `fotoBon/fn-uji-1` | Penjaga laci BERHAK membaca foto nota | LOLOS |
| ★TP28 | Penjaga laci | get `fotoBon/fn-uji-1` | Penjaga laci TANPA hak membaca foto nota | DITOLAK |
| ★TP29 | karyawan | get `fotoBon/fn-uji-1` | karyawan bertanda hak membaca foto nota | DITOLAK |
| ★TP30 | Penjaga laci nonaktif | get `fotoBon/fn-uji-1` | Penjaga laci bertanda hak tapi NONAKTIF | DITOLAK |
| ★TP31 | Penjaga laci bertanda hakFotoNota | delete `fotoBon/fn-uji-1` | Penjaga laci berhak menghapus foto nota | DITOLAK |
| ★TP32 | kasir@ | create `jagaLog/jg-uji-1` | kasir@ mencatat absen jaga | DITOLAK |

Di **v26** kasus ★TP1, ★TP2, ★TP3, ★TP4, ★TP5, ★TP6, ★TP7, ★TP14, ★TP15, ★TP22, ★TP27 DITOLAK (koleksi `jagaLog` & `fotoBukti` belum ada, usul tablet belum dibuka,
`fotoBon` owner saja); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V27** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ketiga puluh dua kasus di atas
atas `firestore.rules` (v27) dan atas `firestore.rules.v26` — yang berbeda wajib persis daftar di atas — plus kontrol (ubahan v27 dirusak → kasus sasarannya wajib
berbalik). Semua kasus v26 sampai v7 lama tetap dijalankan atas v27 dan wajib sama hasilnya.

## Hasil Playground & terbit

(belum — diisi saat owner menerbitkan v27)
