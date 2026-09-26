# Aturan kerja untuk sesi Claude di repo ini

## Uji peramban: beban hanya di runner GitHub (keputusan owner, 27 Sep 2026)

- **Uji beban dan uji berulang HANYA di runner GitHub Actions.** Termasuk: mengulang alat uji dalam putaran, reproduksi/diagnosis yang
  menyalakan Chrome berkali-kali, pengukuran seberapa sering sesuatu macet. Pakai workflow **Uji beban peramban**
  (`.github/workflows/uji-beban-peramban.yml`, bisa dijalankan manual dari tab Actions) atau cabang + workflow khusus.
  `alat-uji/beban_kasir_darurat.py` menolak jalan di luar GitHub Actions.
- **Di Mac owner: paling banyak 2 Chrome sekaligus, dan setiap Chrome dimatikan sesudah dipakai.**
  - Alat uji biasa (`alat-uji/uji_*.py`) menjalankan SATU Chrome sekali jalan dan mematikan seluruh grup prosesnya sesudah tiap pemuatan.
    Boleh dijalankan sekali untuk memeriksa perubahan.
  - Jangan menjalankan beberapa alat uji peramban bersamaan, jangan menjalankannya berulang-ulang dalam putaran, jangan membuat pekerja
    paralel yang masing-masing menyalakan Chrome.
  - Sesudah selesai, tidak boleh ada Chrome headless yang tersisa: `pgrep -fl "Google Chrome.*--headless"` harus kosong.

**Kenapa:** 27 Sep 2026 ±01.18 WIB sebuah diagnosis menyalakan ±300 Chrome headless dalam 19 menit (3 sekaligus) di Mac owner.
WindowServer ambruk dan Mac mati mendadak (kernel panic: `userspace watchdog timeout: no successful checkins from WindowServer`). Chrome
headless di macOS tetap memakai WindowServer. Rincian: `docs/catatan-uji-peramban.md`.
