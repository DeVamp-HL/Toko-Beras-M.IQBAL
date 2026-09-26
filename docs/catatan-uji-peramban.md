# Catatan uji peramban (Chrome headless)

Temuan tentang alat uji yang menyalakan Chrome headless (`alat-uji/uji_antrean_kasir.py`, `uji_sistem_lama_bacasaja.py`,
`uji_layar_kunci.py`). Angka rupiah di catatan ini (karcis 5.200) adalah **angka contoh skenario uji**, bukan data toko.

## Ringkas

- Kasir darurat (`kasir-darurat-nominal.html`) kadang **tidak diserahkan Chrome headless** sesudah skenario uji selesai. Itu memicu
  percobaan ulang: 14 kali dalam 6 run CI (26–27 Sep 2026). Semuanya di halaman ini; `kasir.html`, sistem lama, dan `/baru/` nol.
- Diagnosis 27 Sep di runner: dari 38 pemuatan, **6 macet, dan keenamnya "BEKU"**. Halaman berhenti dijalankan **tepat sesudah selesai
  dimuat**, saat tidak ada satu pun fungsi kasir yang sedang jalan, dan **semua karcis sudah terkirim atau tersimpan** di daftar yang benar.
  Polanya menunjuk ke Chrome headless yang berhenti menjalankan halaman saat mengambil DOM. Belum terbukti ke arah mana pun apakah ini
  bisa terjadi di HP.
- Keputusan owner 27 Sep: alat uji **tidak lagi bergantung pada Chrome menyerahkan isi halaman**. Skenario mengirim hasilnya sendiri ke
  server uji (`POST /_hasil`) sebelum halaman selesai dimuat.
- Uji beban dan uji berulang **hanya di runner GitHub** (`CLAUDE.md`). Diagnosis lokal membuat Mac owner mati (kernel panic).

## Riwayat gejala

| Kapan | Di mana | Kejadian |
|---|---|---|
| 26 Sep | CI main `8dcaae2` percobaan 1 | pemuatan pertama kasir darurat: skenario selesai, DOM tidak keluar 60 dtk → uji gagal, Pages tertahan (lolos lewat re-run) |
| 26–27 Sep | PR #42 (6 run CI) | 14 DICOBA ULANG, semua kasir darurat, semua "selesai tapi DOM tidak keluar" |
| 26–27 Sep | Mac pengembang | ±2 dari ±200 pemuatan, keduanya saat `--kontrol` |

Normalnya DOM keluar 0,5–2,5 dtk sesudah skenario mengabarkan selesai (juga di bawah beban 4 uji paralel). Saat macet: tidak keluar sama
sekali (≥20 dtk).

## Perbaikan alat uji sepanjang jalan (PR #42)

- Tiap percobaan ulang menulis `DICOBA ULANG: <nama uji> · <halaman> — <sebab>` + peringatan di ringkasan run (`alat-uji/coba_ulang.py`),
  dengan ekor catatan Chrome di bawahnya. Pengulangan di `uji_layar_kunci.py` dulu diam.
- **Percobaan ulang tidak otomatis aman.** Percobaan yang gagal bisa sudah menjalankan (sebagian) skenarionya: skenario muat ulang sudah
  mengarsipkan karcis → percobaan kedua gagal palsu (di skenario lain bisa lulus palsu). Penyimpanan halaman (Local Storage, IndexedDB)
  difoto sebelum percobaan pertama dan dipulihkan sebelum tiap percobaan ulang.
- Chrome dimatikan per **grup proses** (`start_new_session` + `killpg`), bukan cuma induknya.
- `http.server` menanyakan nama host `127.0.0.1` ke DNS (`socket.getfqdn`) tiap server menyala — di runner macOS ±35 dtk per proses.
  Server uji mengikat soket tanpa pertanyaan itu.

## Diagnosis 27 Sep 2026 (runner GitHub)

**Cara.** Salinan kasir darurat + skenario yang sama dengan `uji_antrean_kasir.py`, ditambah **pemantau yang disuntik alat** (berkas yang
terbit tidak disentuh; sidik SHA-256 sama sebelum dan sesudah):
- jejak tiap fungsi yang bertindak, timer, dan kiriman (`masuk X` / `keluar X`);
- mulai 5 dtk sesudah skenario selesai: denyut tiap detik lewat jaringan (ke server uji) dan lewat penyimpanan (`localStorage`).

Saat macet, Chrome ditutup baik-baik (SIGTERM, supaya penyimpanan sempat ditulis ke disk), lalu halaman baca kecil membaca `localStorage`
(jejak, denyut, antrean, ditolak, arsip).

**Alat diuji dulu:** beku buatan (perulangan tanpa ujung tepat sesudah selesai) → divonis BEKU, tempat bekunya terbaca tepat; hidup buatan
(server menahan gambar penahan 40 dtk) → HIDUP, 15 denyut jaringan dan 15 denyut penyimpanan.

**Hasil** (run: https://github.com/DeVamp-HL/Toko-Beras-M.IQBAL/actions/runs/36262567372 — alatnya di commit `8c39437`, cabang
`diagnosis/darurat-macet` sudah dihapus):

| | |
|---|---|
| Pemuatan | 38 dalam 4,8 menit (21 pasangan utama → muat ulang), satu Chrome sekali jalan |
| Macet | **6** (4 skenario utama, 2 muat ulang) |
| HIDUP / BEKU | **0 / 6** — tidak ada satu pun denyut jaringan maupun penyimpanan sesudah +5 dtk |
| Tindakan terakhir | utama: skenario selesai → 4 timer "sembunyikan tanda OK" jalan & selesai → **halaman selesai dimuat (load)** → berhenti. Muat ulang: arsipkan daftar ditolak (2 ketukan) selesai → denyut perangkat terkirim → **load** → berhenti |
| Fungsi kasir yang sedang jalan saat berhenti | **tidak ada** (tiap `masuk` sudah `keluar`) |
| Karcis saat berhenti | utama: antrean kosong (semua terkirim), 1 karcis di daftar ditolak (bulan terkunci, sesuai skenario). Muat ulang: antrean kosong, karcis di arsip (sesuai skenario). **Tidak ada karcis yang menunggu kirim** |
| Chrome ditutup baik-baik | 6 dari 6 berhasil (beku buatan yang JS-nya berputar: TIDAK berhasil) |

**Artinya.** "BEKU" di sini = halaman berhenti dijalankan, bukan kode kasir yang tersangkut: berhentinya selalu tepat di detik Chrome
headless mengambil DOM, tanpa fungsi kasir yang aktif, dan Chrome masih bisa ditutup baik-baik. Kolom sandi di luar `<form>` (catatan
Chrome "Password field is not contained in a form") ada di **kedua** berkas kasir, jadi bukan pembedanya. Pembeda kasir darurat ↔ kasir.html
belum ditemukan.

**Yang belum diketahui:** apakah hal serupa bisa terjadi di HP penjaga. Di HP tidak ada langkah "ambil DOM".

## Diagnosis lokal & Mac owner mati (27 Sep ±01.18 WIB)

Percobaan pertama dijalankan di Mac owner: 3 pekerja paralel, ±300 pemuatan dalam 19 menit, 0 macet. Lalu Mac mati mendadak:
- dua laporan crash Chrome (diluncurkan diagnosis) gagal di `HIServices _RegisterApplication / TransformProcessType`;
- kernel panic `userspace watchdog timeout: no successful checkins from WindowServer (2 induced crashes) in 120 seconds`;
- `ResetCounter`: `wdog,reset_in_1`.

Chrome headless di macOS tetap memakai WindowServer (catatan `CVDisplayLinkCreateWithCGDisplay failed` di tiap pemuatan). Sejak itu:
aturan di `CLAUDE.md`.

## Keputusan: hasil lewat server, bukan lewat DOM (27 Sep 2026)

- Skenario di `uji_antrean_kasir.py` dan `uji_sistem_lama_bacasaja.py` mengirim hasilnya ke `POST /_hasil` **sebelum** `/_siap`, jadi
  sebelum halaman selesai dimuat. `buka()` berhasil begitu hasil masuk; DOM dibuang.
- **Muat ulang di Chrome yang sama.** Sesudah mengirim hasil skenario utama, halaman memuat ulang dirinya ke skenario muat ulang
  (`?lanjut=` → `location.replace`), seperti HP penjaga memuat ulang halaman. Penyimpanan halaman tidak perlu ditulis ke disk lalu dibaca
  Chrome baru. Uji beban PR #43 percobaan pertama (Chrome ditutup SIGTERM sesaat sesudah hasil, muat ulang di Chrome baru): **100 dari 100
  pasangan kehilangan seluruh penyimpanan** di runner (termasuk tanda masuk yang ditulis 5 dtk sebelumnya), padahal di Mac pengembang
  lolos. Kasir tidak memakai `sessionStorage`, jadi muat ulang di tab yang sama setia pada perilaku HP.
- Sesudah semua hasil masuk, Chrome ditutup baik-baik (SIGTERM) — tidak menunggu Chrome menyerahkan DOM atau keluar sendiri.
- `--gambar` (tangkapan layar untuk pemeriksaan mata, bukan CI) masih memakai jalur lama: tiap pemuatan Chrome sendiri, bergantung pada
  Chrome menulis penyimpanan ke disk.
- **Mode `--dump-dom` dibuang.** Uji lokal 27 Sep: dalam mode itu Chrome headless di macOS tidak keluar sendiri (22 dari 22 pemuatan dalam
  5 dtk) dan **mengabaikan SIGTERM** (22 dari 22 harus dimatikan paksa sesudah 10 dtk). Alat lama tidak pernah tahu karena langsung
  mematikannya sesudah membaca DOM. Tanpa mode itu Chrome jalan seperti peramban biasa tanpa layar dan mau ditutup baik-baik.
- Chrome yang menolak ditutup baik-baik dalam 10 dtk dimatikan paksa dan **dihitung** (`STAT['chrome_ditutup_paksa']`, dicetak di CI).
  **Bukan percobaan ulang.**
- Yang masih dicoba ulang (dan tercatat DICOBA ULANG): halaman yang tidak mengirim hasil sama sekali.
- `uji_layar_kunci.py` **belum** diubah. Uji tirainya memeriksa isi seluruh halaman ("0 angka rupiah di DOM"), dan belum pernah macet
  (0 DICOBA ULANG yang tidak disengaja).
- Bukti: workflow **Uji beban peramban** — ≥200 pemuatan kasir darurat dengan alat uji lama ("sebelum") dan baru ("sesudah") di runner.
