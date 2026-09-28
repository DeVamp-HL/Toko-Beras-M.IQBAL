# Temuan 31.4 — rework 11 Sep bermodal nol (ditunjukkan, tidak ditulis)

Sumber: cadangan toko 28 Sep sore (`_privat/`). Bukan tambalan: jalur koreksinya diputuskan owner.

Dokumen di cadangan 28 Sep: `penyesuaianStok` 11 Sep 12:08, `dariRework: true`, nama **IR64 Elevate**, `selisihKg 41,5`, `nilaiRp 0`,
`hppPerKgSaatOpname 0`, alasan menunjuk satu id retur — retur dengan id itu **tidak ada** di koleksi `retur` cadangan (retur 11 Sep yang ada atas nama
yang sama berkondisi utuh dan ber-id lain; koleksi `karantina` kosong).

- **Cara mesin membacanya**: penyesuaian LEBIH menggeser sisa saja (`terpakai` turun 41,5 kg) tanpa menyentuh nilai masuk → modal rata-rata nama itu
  tidak berubah, jadi 41,5 kg itu **dinilai dengan modal rata-rata IR64 Elevate**, bukan Rp0, di nilai stok & neraca; `nilaiRp 0` di dokumen hanya
  berarti baris ini tidak memotong/menambah laba (susut hanya untuk selisih kurang). Modal rata-rata IR64 Elevate menurut buku sampai 11 Sep dan sekarang
  hanya berbeda beberapa rupiah per kg — angkanya di laporan obrolan, bukan di sini.
- **Jalur koreksi yang ada**: koreksi HPP (Stok › HPP) mengoreksi harga beli kedatangan terakhir (`batchMasuk`), koreksi adukan mengoreksi
  `produksiKemasan`; **tidak ada** yang menjangkau `penyesuaianStok` rework tanpa bahan. Menghapus/mengoreksi dokumen rework tidak tersedia di layar
  mana pun.
- **Kunci bulan**: September belum terkunci (`aturanToko/kunciPeriode` belum ada); kunci pertama sesudah 25b (rencana 1–3 Okt) akan mengunci September
  → sesudah itu dokumen ini tidak bisa disentuh siapa pun (K2).
- **Butir peta, bukan tambalan**: kalau owner ingin rework berbawa modal, jalannya ada dua: (a) rework karung menulis `hppPerKgSaatOpname` = modal
  rata-rata nama itu saat rework (dokumen baru saja, dokumen lama dibiarkan; nilai stok tidak berubah karena mesin sudah memakai rata-rata), atau (b)
  keputusan bahwa rework memang bermodal nol di dokumen tetapi bernilai rata-rata di buku — cukup dicatat di BACA-DULU. Keduanya keputusan owner.
