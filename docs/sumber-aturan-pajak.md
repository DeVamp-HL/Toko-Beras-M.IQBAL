# Sumber aturan modul pajak (putaran 24)

Semua angka di Laporan › Pajak adalah **perkiraan — bukan nasihat pajak**. Sistem menghitung, mengingatkan, dan menyimpan bukti.
Sistem tidak membayar, tidak melapor, dan tidak memberi nasihat pajak.

Semua sumber dilihat **24 September 2026**. Klaim yang belum terverifikasi tampil `[BELUM TERVERIFIKASI]` di layar dan di cetakan
(`PJ_SUMBER` di `baru/js/layar/pajak-logika.js`), tidak sebagai fakta.

| # | Klaim | Sumber resmi | Status |
|---|---|---|---|
| 1 | PP 20/2026 (perubahan PP 55/2022) ditetapkan, diundangkan & berlaku **22 April 2026** (LN 2026 No. 43) | [peraturan.bpk.go.id/Details/349415](https://peraturan.bpk.go.id/Details/349415/pp-no-20-tahun-2026) | terverifikasi |
| 2 | Jangka waktu tertentu tarif 0,5 % untuk **orang pribadi** dihapus (Pasal 59 dihapus); dipakai sampai tidak memenuhi kriteria | [Salindia DJP PP 20/2026, hlm. 3, 8, 17](https://pajak.go.id/sites/default/files/2026-06/Peraturan%20Pemerintah%20nomor%2020%20Tahun%202026.pdf) · [pajak.go.id/en/node/119950](https://www.pajak.go.id/en/node/119950) | terverifikasi (materi resmi DJP) |
| 3 | Batas omzet **Rp4,8 miliar** setahun; omzet suami-istri **digabung** untuk batas ini, termasuk pisah harta (PH) & istri memilih sendiri (MT) — PP 20/2026 Pasal 58 ayat (2)–(3). Salindia hlm. 14 hanya memuat Pasal 58 ayat 1; penggabungan suami-istri dikutip dari artikel DJP "PP 20/2026: Ketika Omzet Pasangan Ikut Bicara" (8 Jun 2026) | [Salindia DJP hlm. 11, 14](https://pajak.go.id/sites/default/files/2026-06/Peraturan%20Pemerintah%20nomor%2020%20Tahun%202026.pdf) · [pajak.go.id/en/node/119991](https://pajak.go.id/en/node/119991) | terverifikasi (materi resmi DJP) |
| 4 | Bagian peredaran bruto **s.d. Rp500 juta** setahun tidak dikenai (orang pribadi), dihitung **kumulatif sejak masa pajak pertama**, seluruh tempat usaha — PMK 164/2023 Pasal 6 ayat (3)–(4); PPh = tarif × dasar sesudah bagian itu, Pasal 6 ayat (6) huruf a | [PMK 164/2023 (jdih.kemenkeu.go.id)](https://jdih.kemenkeu.go.id/api/download/a99b8e80-9694-46ab-8de1-63c2484aa636/2023pmkeuangan164.pdf) | terverifikasi (teks dibaca) |
| 5 | Batas Rp500 juta berlaku **masing-masing** suami & istri HANYA bila (a) perjanjian pemisahan harta & penghasilan tertulis (PH) atau (b) istri memilih menjalankan hak & kewajiban pajaknya sendiri (MT) — PMK 164/2023 Pasal 6 ayat (5); Lampiran contoh 4 (Tuan O & Nyonya L, MT: masing-masing Rp500 juta). Dibaca ulang 24 Sep 2026 atas permintaan owner | PMK 164/2023 | terverifikasi (teks dibaca) |
| 5a | Suami-istri **satu kesatuan**: ayat (5) tidak menyebutnya → tidak ada batas kedua; usaha pasangan ikut wajib pajak yang sama → **satu batas Rp500 juta berdua**. Dasar penggabungan penghasilan (UU PPh Pasal 8 ayat 1) belum dibaca langsung | PMK 164/2023 Pasal 6 ayat (5) (a contrario) | **[BELUM TERVERIFIKASI]** → hitungan memakai anggapan paling hati-hati (hasilnya sama) |
| 5b | Peredaran bruto = imbalan **sebelum** dikurangi potongan penjualan, potongan tunai, dan/atau potongan sejenis — PMK 164/2023 Pasal 6 ayat (2) | PMK 164/2023 | terverifikasi (teks dibaca) |
| 6 | Setor paling lambat **tanggal 15 bulan berikutnya**, per tempat kegiatan usaha — PMK 164/2023 Pasal 7 ayat (2) | PMK 164/2023 | terverifikasi (teks dibaca) |
| 7 | Setoran bervalidasi **NTPN dianggap SPT Masa** PPh Unifikasi, per tanggal validasi NTPN — PMK 164/2023 Pasal 7 ayat (5) | PMK 164/2023 | terverifikasi (teks dibaca) |
| 8 | Kode billing lewat Coretax: **KAP-KJS 411128-420** (PPh Final UMKM bayar sendiri) | [pajak.go.id/en/node/116821](https://www.pajak.go.id/en/node/116821) (16 Jun 2025) | terverifikasi (artikel DJP) |
| 9 | **NTPN** = 16 karakter gabungan angka & huruf | [pajak.go.id/en/node/111191](https://pajak.go.id/en/node/111191) (2020) · definisi: [JDIH Kemenkeu](https://jdih.kemenkeu.go.id/kamus-hukum/nomor-transaksi-penerimaan-negara?id=03ff7123542bd5d9fc6dd9ffa70eb9fc) | **[BELUM TERVERIFIKASI]** untuk era Coretax → aplikasi hanya memperingatkan, tidak memblokir |
| 10 | Aturan **pembulatan** PPh final | tidak ditemukan di PMK 164/2023 | **[BELUM TERVERIFIKASI]** → aplikasi membulatkan ke **bawah** ke rupiah penuh |

## Yang ditemukan di sumber dan memengaruhi angka

- **Peredaran bruto sebelum potongan.** PMK 164/2023 Pasal 6 ayat (2): peredaran bruto = imbalan *sebelum dikurangi potongan penjualan,
  potongan tunai, dan/atau potongan sejenis*. Omzet sistem = mesin laba (`omzetPenuh`: penjualan yang masih berlaku, **sesudah** potongan
  nota & retur). Mesin beku tidak disentuh. Keputusan owner 24 Sep: cetakan untuk konsultan menampilkan **dua angka per bulan** — omzet mesin
  (dasar perkiraan PPh sekarang) dan omzet sebelum potongan nota (+ `potonganTransaksi` + tawar di bawah harga daftar dari `hargaAsliSatuan`,
  tampilan saja) — dan menulis bahwa **pilihan angka diserahkan ke konsultan**.
- **Status pasangan** (keputusan owner 24 Sep). Profil punya `statusPasangan`: `pisahHarta` / `memilihTerpisah` → usaha pasangan tidak ikut PPh
  di sini, hanya ikut ambang Rp4,8 miliar (klaim 3 & 5); `satuKesatuan` → ikut PPh & satu batas Rp500 juta (klaim 5a); `belumDiketahui` (bawaan)
  → anggapan paling hati-hati: satu batas Rp500 juta berdua. Hidup berpisah berdasarkan putusan hakim (UU PPh Pasal 8 ayat 2 huruf a) tidak ada
  di pilihan owner — pasangan seperti itu wajib pajak sendiri-sendiri, usahanya tidak diketik di sini.
- **NPWP di kop** (keputusan owner 24 Sep). Kolom NPWP identitas usaha tetap ada, bawaan tidak dicetak di kop mana pun. NPWP orang pribadi
  16 angka = NIK → peringatan sebelum dicetak.
- **Bulan yang melewati Rp500 juta.** Hanya kelebihannya yang dikenai: diturunkan dari Pasal 6 ayat (3), (4), dan (6). Contoh lampiran PMK
  (contoh 2) kebetulan tidak memuat bulan yang terbelah (batas tercapai tepat di akhir bulan).
- **Per tempat kegiatan usaha.** Setor tiap bulan untuk masing-masing tempat usaha (Pasal 7 ayat 2). Contoh lampiran membagi PPh per lokasi
  menurut proporsi omzet. Aplikasi menganggap satu tempat usaha **[ASUMSI]**.
- **Ketentuan peralihan PP 20/2026** (salindia hlm. 18–19): orang pribadi yang jangka waktunya berakhir 2024 boleh memakai 0,5 % untuk tahun
  pajak 2025 dan 2026. Karena jangka waktu dihapus, `tahunMulaiTarifFinal` di profil hanya catatan.
- **PMK pelaksana PP 20/2026.** Tidak ditemukan PMK baru pengganti PMK 164/2023 per 24 Sep 2026 **[BELUM TERVERIFIKASI]**. Aturan tanggal 15,
  SPT Masa, dan batas Rp500 juta di atas memakai PMK 164/2023.
