# Sistem baru — `baru/`

Tampilan baru di atas **data yang sama** dengan `index.html` (Firestore proyek `toko-beras-m-iqbal`, 28 koleksi, akun owner yang sama).
Hidup berdampingan di alamat `/baru/`; `index.html` tetap alat yang dipakai toko sampai yang baru terbukti.
Keputusan owner 13 Sep 2026: desain ulang termasuk UI **tanpa mengubah data toko**; 17 Sep: *"mulai sambungkan ke data asli"*.

## Putaran 1 (19 Sep 2026) — layar JUAL, baca
- Rak (Sering · Literan · Kemasan · Karung) dibaca dari data toko lewat **mesin beku yang sama** dengan `index.html`.
- Keranjang, nego, potongan, antrean (struk parkir **memegang** stoknya), bayar (Tunai/QRIS/Bon), nama pembeli, kartu Hari ini.
- Aturan owner yang dipasang: pembulatan Rp500 ke atas untuk **Tunai dan Bon**, QRIS persis (17 Sep); uang kurang → sisanya jadi bon atas nama (17 Sep); siapa cepat dia dapat (17 Sep).
- Belum: Wadah, Repack, Retur, Pesanan, cetak struk, dan semua layar lain (masih di sistem lama).

## Putaran 2 (19 Sep 2026) — nota DICATAT
- Satu pintu tulis `toko.tulisDokumen()` → Firestore `writeBatch` (semua dokumen satu nota masuk bersama; index.html menulis satu per satu) + satu baris `logAktivitas` per dokumen; atribusi `oleh/perangkat/diubah*` persis `simpanKeFirestore()` lama. Tanpa internet: tulisan mengantre di cache tetap Firestore, layar bilang "menunggu server".
- Bentuk dokumen = `simpanKeranjangJual()` index.html: potongan dibagi proporsional (sisa ke baris terakhir), pembulatan melekat ke baris terakhir bernilai (`pembulatan`), `uangDiterima`/`kembalian` di tiap baris tunai, `hargaAsliSatuan` + `negoSelisih`, `trxId` satu nota; **uang kurang** = semua baris `Kredit` + satu `piutangMutasi` tipe `bayar` sebesar uang yang diterima; literan berkantong = `stokBahanLiteran {id: id+1, tipe 'pakai'}`. Diuji: kunci dokumen yang dihasilkan ⊆ kunci baris nyata di cadangan toko.
- KR1 untuk bon murni (belum terdaftar / batas belum terbentuk / lewat batas 2× belanja bulanan) — owner bisa **buka kredit sekali** (tanda `kreditDibukaOwner`), tanpa PIN karena ini alat owner sendiri. Bayar sebagian tidak kena KR1 (sama dengan live).
- Stok dicek ULANG saat mencatat (bisa berubah sejak dimasukkan). Belum ada jalur "tembus stok" — kalau kurang, ditahan.
- **Batalkan nota barusan** (90 detik): baris ditandai `dibatalkan` + `alasanKoreksi` (tidak dihapus, seperti `mulaiBatalkanTrx` live); kantong literan `id+1` dan pelunasan sebagiannya dilepas.
- Mode `?cadangan=` = SIMULASI: menulis ke cache lokal saja, dilabeli di layar.
- Belum: Wadah, Retur/Tukar, cetak struk, janji bayar, urungkan sesudah 90 detik (lewat sistem lama).

## Putaran 3 (19 Sep 2026) — paritas layar Jual lama
- **Repacking Dadakan** (jalur `repack`): kg bebas dari kolam karung merek itu (kolam yang sama dengan karung & literan), harga per kg katalog (`cariHargaKarungPerKg`), nama jual bebas (kosong = nama merek). Dokumen `jenis 'repacking'` persis `bangunTrxJualDariForm` 19333: `{merkSumber, namaProduk, totalKg, hppTotalSaatJual, hargaTotal, …}`.
- **Bonus kemasan +1** (pil di baris keranjang): `bonusUnit 1`, `jumlahUnit` = unit bayar + 1 → stok & HPP ikut, uang tidak (`wzTambahItem` 17633). Langit-langit stok dan pemeriksaan ulang saat mencatat menghitung bonusnya.
- **Pengganti retur** (pil di baris; cara lama untuk tukar TANPA nota): `penggantiRetur true`, `nilaiBarangPengganti` = nilai, `hargaTotal 0` — omzet & kas Rp0, HPP tetap keluar, baris ini tidak dapat potongan/pembulatan (19383). Penjaga model B: kalau hari ini ada tukar bernota (`tukarModel 'kreditBarang'`), ketukan pertama cuma memperingatkan.
- **Pesanan** (tombol di keranjang → lembar): catat pesanan baru (bentuk `simpanPesanan` 16224), dipesan → diantar, batalkan; **"catat jualnya"** mengikat keranjang ke pesanan (nama ikut, ikatan ikut diparkir) dan saat nota dicatat, dokumen pesanan `status 'dibayar'` + `trxIdJual` masuk **dalam batch yang sama** (index.html menulisnya terpisah sesudah nota — 16272). Batalkan nota barusan memulihkan statusnya. Pesanan BUKAN uang & BUKAN stok sampai notanya dicatat (G5).
- Belum: Wadah dijual (fitur baru, mesin laba harus diajari dulu), cetak/kirim struk.

## Putaran 4 (19 Sep 2026) — Retur menunjuk nota: uang kembali & tukar
- Jalur **Retur** di layar Jual: daftar nota karung/kemasan 60 hari terakhir (bisa dicari) → ketuk → lembar retur. Nilainya dihitung dari NOTA-nya oleh `rtDasarNota()` yang **dipindah verbatim** (`pembantu.js`): hargaTotal − pembulatan tunai, potongan nota diprorata, ÷ banyaknya; sisa yang boleh kembali = nota − yang sudah diretur di seluruh rantai koreksi. Nota KREDIT / ber-bonus / perlu-koreksi ditolak dengan sebabnya (jalan ketik-tangan masih di sistem lama).
- Wajib: berapa yang kembali (karung boleh sebagian kg, kemasan unit utuh), **boleh dijual lagi?** (layak → kembali ke stok; rusak/ragu → dokumen `karantina` ber-id sama), **alasan** (KR3).
- **Uang kembali**: dokumen `retur` bentuk `simpanRetur()` cabang bernota; boleh ditimpa hanya ke BAWAH dengan alasan (`nominalSistem` + `alasanTimpaNominal`).
- **Tukar**: retur TIDAK ditulis saat itu — diikat ke keranjang (`tukarModel 'kreditBarangGabung'`); nilai barang kembali dipotong sebelum pembulatan (pembulatan atas selisih bersih); saat nota dicatat, penjualan pengganti (`tukarReturId`) + retur (`penjualanPenggantiTrxId`, `hitunganTukarSistem`) + karantina masuk **dalam SATU batch** (index.html menulis berurutan dan menjaga dengan jurnal localStorage; di sini tidak bisa setengah jadi). Tukar tidak bisa bon, tidak bisa bayar sebagian, pengganti tidak boleh lebih murah dari barang kembali; draf dibaca ulang saat mencatat; ikatan ikut diparkir; tukar & pesanan saling meniadakan. Batalkan nota barusan mencabut retur + karantinanya juga.
- Belum: retur TANPA nota (ketik tangan), retur tukar lama yang "yatim" (catat penggantinya / pengganti sudah tercatat) — tetap lewat sistem lama.

## Putaran 5 (19 Sep 2026) — layar RINGKASAN (R2 "Cincin Bersarang"), baca saja
- Desain yang dikunci owner 13 Sep: tujuh skala (Langsung · Menit · Jam · Hari · Minggu · Bulan · Tahun), tiap skala tiga lapis cincin (luar · induk · kakek) + satu angka besar; geometri cincin = rumus papan R2 (tebal ∝ akar nilai, sel berjalan di jam 12).
- Angka dari data toko lewat mesin yang sama: omzet = baris penjualan berlaku; **margin kotor** (K1) dari `hitungLabaRentang` dan layar menyebut baris tanpa modal yang tidak ikut; bon dari `hitungPiutang`, utang pemasok dari `hitungUtangPemasok`, menipis = sisa ÷ laju jual (`hitungLajuPakai`) ≤ `AMBANG_HARI_KRITIS` (verbatim), kas dari `kasPada()`.
- Kejujuran: pembanding selalu **sampai titik yang sama** (kemarin jam segini · minggu lalu sampai hari & jam yang sama · bulan lalu sampai tanggal yang sama) dan **ditolak** kalau jendelanya mendahului catatan pertama toko; periode berjalan bertepi putus, yang belum terjadi tipis, yang sebelum ada catatan "absen" (bukan nol); saldo kas **tidak ditebak** kalau titik kas belum disetel di perangkat itu (titik kas = localStorage sistem lama, asal-usul sama).
- **Gerak & interaksi (putaran 5b — owner 13 Sep: "lebih interaktif, lebih hidup, ada animasi motion dibanding sistem lama")**: layar ini TIDAK digambar ulang; kerangkanya dibangun sekali dan elemennya hidup terus supaya perubahan bisa bertransisi.
  - Ketujuh lapis cincin selalu ada dengan identitas sel tetap (`lapis:urutan`); yang tak berperan menunggu di luar (r 108) / di dalam (r 22) beropasitas 0 → ganti skala = cincin **bergeser masuk/keluar** (transisi `r`, `stroke-dasharray`, `stroke-dashoffset`, tebal, opasitas). Saat pertama tampil cincin **menggambar dirinya** bergiliran.
  - Angka besar **bergulir** ke nilai barunya (rAF, kurva tenggelam); kilau menyapu kartu; teks judul/sub berganti dengan geser halus; kartu-kartu naik bergiliran saat layar dibuka.
  - **Jarum detik** berdetak tiap detik (sudut selalu maju); tiap menit sel berjalan & jendela 60 menit bergeser.
  - Nota baru: tetes emas **terbang** dari tombol Jual ke angka → kartu "mendarat" (pegas + tepi emas) → chip +Rp naik → baris umpan masuk hangat.
  - Interaktif: **ketuk sel cincin** → label & nilainya (mis. "Kamis, 10 Sep · Rp…"), sel lain meredup; **ketuk lapis** (Luar/Induk/Kakek) → pindah ke skala itu; **geser kiri/kanan** di kartu besar → skala berikut/sebelumnya.
  - Penjaga: tab tersembunyi (rAF & transisi beku) → nilai akhir ditulis langsung dan diselaraskan saat tab kembali tampil; `prefers-reduced-motion` dihormati.
- Perpindahan layar: tiap layar punya `<main>` sendiri yang disembunyikan — keranjang Jual tidak hilang saat pindah; layar terakhir diingat per perangkat. Stok · Pelanggan · Menu masih di sistem lama.
- Yang sengaja beda dari papan: kartu "Kas laci / Rekening" diganti "Kas tercatat · semua kantong" + "Uang hari ini (laci · rekening)" — sistem lama tidak punya saldo per kantong, jadi tidak dikarang.

## Putaran 6 (19 Sep 2026) — layar Jual yang HIDUP + gambar barang + wadah literan bergunung
- **Layar dimorf, bukan digambar ulang** (`inti/dom.js` `pasang()`): pohon HTML baru dibandingkan dengan yang hidup, atribut/teks diselaraskan di tempat, anak dicocokkan lewat `data-k`/`id`. Elemen yang sama tetap hidup → isi gambar, gunung beras, dan angka bisa **bertransisi**; animasi masuk hanya berjalan saat elemen benar-benar lahir (chip per jalur, baris keranjang, lembar per jenis). Kotak isian yang sedang diketik tidak ditimpa.
- `inti/gerak.js`: `gulirkan()` (angka ber-`data-gulir` bergulir dari nilai lama ke baru: total keranjang, ditagih, diterima, kembalian, omzet hari ini), `terbangkan()` (tetes emas dari tombol yang diketuk ke bilah keranjang, bilahnya memegas), `sekali()`. Tab tersembunyi & "kurangi gerakan" → nilai akhir langsung.
- **Gambar sesuai barang** (SVG, isi naik-turun lewat `transform` supaya bertransisi di semua peramban): karung utuh (berangka 50/25), kemasan (kantong berlabel angka ukurannya), karung terbuka + serok (repack & literan yang diserok dari karung), dan **kotak wadah literan** dengan **gunung beras**.
- **Wadah literan** (keterangan owner 14 & 19 Sep; foto kotak kayu bergunung): delapan wadah (`DAFTAR_WADAH`), penuh ±50 kg, isi ulang saat tersisa ≤ 10 kg, di atas 60% masih menggunung lalu rata lalu turun (`WADAH_*` — angka KEBIJAKAN owner, kelak diatur dari layar Stok khusus wadah). Tinggi isi = isi saat terakhir **ditandai isi ulang** − literan merek itu yang terjual sesudahnya − literan di keranjang/struk parkir. Tombol "Wadah baru diisi ulang" ada di lembar jumlah literan → dokumen koleksi BARU `wadahLiteran` `{wadah, tipe 'isi', isiKg, tanggal, jam}`. **Alat ukur, BUKAN stok**: stok literan tetap dipotong dari kolam merek oleh mesin yang sama; sistem lama tidak mengenal koleksi ini dan cadangan sistem lama tidak memuatnya. Belum pernah ditandai → kotak bergaris putus bertanda "?" (tidak ditebak penuh); terjual melebihi isi tanda → selisihnya dilaporkan.
- **Tata letak seperti papan harga toko**: kemasan dikelompokkan per ukuran (5 · 10 · 20 · 25 · … kg), karung per 50/25 kg, tiap kelompok **dari yang termurah**; literan & repack dari yang termurah.

## Putaran 6b (19 Sep 2026) — kinerja di Mac + adegan cerita
- **Patah-patah di Mac** (`css/kinerja.css`): penyebabnya elemen ber-`backdrop-filter` yang bergerak / berisi gerak (belasan chip kaca buram masuk bergiliran, bola cahaya ber-`filter: blur`, latar `background-attachment: fixed`) → tiap bingkai latar dikaburkan & dicat ulang. Kini kaca buram hanya untuk permukaan besar yang diam (nav bawah, laci keranjang HP); chip/kartu/lembar memakai kaca tanpa buram (`--kaca-chip`, `--kaca-kartu`), latar jadi satu lapisan fixed (`body::after`), bola tanpa blur/transisi, chip `contain: layout paint`. Ringkasan: lapis cincin yang tetap tersembunyi pindah tanpa transisi (kelas `diam`).
- **Adegan** (`js/layar/adegan.js`, `css/adegan.css`; hanya `transform` & `opacity`, tidak menghalangi ketukan, dilewati saat tab tersembunyi / "kurangi gerakan"):
  - literan & repack masuk keranjang → **serok** dari wadah kotak (atau karung terbuka) → dituang ke kantong kertas (1–3 serokan menurut kg) → **diikat** → memegas; ≥ 13 L memakai karung kecil.
  - kemasan masuk keranjang → kemasan berlabel ukurannya jatuh ke **keranjang belanja** yang memantul.
  - nota dicatat (literan/kemasan) → **serah terima**: dua tangan toko (lengan emas, atas & bawah kemasan) → dua tangan pembeli (lengan platina) → berubah jadi alat bayarnya.
  - nota dicatat (karung terbesar nilainya) → karung **diangkut** dua tangan → tangan pembeli memberi → tangan toko menerima → jadi alat bayarnya.
  - Kejujuran: hanya **Tunai** yang jadi uang; **QRIS** = ponsel ber-centang; **BON** = kertas bon bertulis "belum ada uang". Adegan nota hanya main sesudah tulisan SUNGGUH berhasil.

## Putaran 7 (19 Sep 2026) — layar STOK: Beranda S9 + Wadah literan
- **Gudang** (papan S9 yang dikunci owner): empat pertanyaan, dijawab dari mesin yang sama —
  *Apa yang harus dibeli hari ini?* (laju jual 14 hari `hitungLajuPakai` × 7 hari − sisa, dibulatkan ke karung penuh; kemasan = "aduk N unit"; barang berisi tanpa gerak 14 hari DISEBUT tidak bisa dijawab) ·
  *Modal saya tidur di mana?* · *Apa yang tidak bergerak?* (tak terukur ≠ nol; atau cukup > 30 hari) · *Mana yang belum dicocokkan?* (hari sejak `penyesuaianStok`/`penyesuaianKemasan`; "belum pernah" paling atas).
- **Penilaian stok — temuan:** mesin lama (`hppTerakhirPerKg`, namanya menyesatkan) menilai dengan **rata-rata tertimbang**, sedangkan aturan owner 13 Sep = **harga beli terbaru**. Layar memajang **nilai di buku** (rata-rata; diuji = `nilaiSack + nilaiBags` mesin neraca) sebagai angka utama dan nilai bila **harga beli terbaru** (`hargaTerakhirPerKg`) sebagai pembanding berlabel. Mengganti penilaian = mengubah mesin beku & laba historis = keputusan owner.
- **Wadah literan**: kedelapan kotak wadah bergunung (gambar yang sama dengan layar Jual, ikut keranjang Jual yang sedang jalan), tombol "Baru diisi ulang", dan **Aturan wadah** yang diatur owner dari layar (penuh kg · minta isi ulang saat tersisa kg · daftar merek berwadah) → dokumen `wadahLiteran` bertipe `atur` (terbaru berlaku, riwayat tersimpan). Tetap ALAT UKUR, bukan stok.
- **Papan Kapur** (perubahan stok hari ini: barang masuk, adukan, cocokkan, barang kembali, isi ulang wadah, terjual per jam·barang) dan **Karantina** (yang belum diputuskan) — baca saja.
- Barang masuk · Adukan · Cocokkan · keputusan karantina masih lewat sistem lama (layar kerja ST1–ST6 menyusul).
- `gambar.js` = gambar barang bersama (Jual & Stok). `index.html`: penjaga muat-ulang SEKALI bila peramban memegang campuran modul lama & baru sesudah terbit.

## Putaran 8 (19 Sep 2026) — wadah literan diisi TAKAR demi TAKAR (koreksi owner)
Praktik toko (pesan owner 13–14 Sep, dikoreksi 19 Sep dengan foto): **tumpukan karung 50 kg di gudang → satu karung terbuka di belakang wadah ("stok wadah") → kotak wadah → dijual per liter**. Wadah diisi ulang dengan serok 1,8 kg, boleh dicampur beberapa merek (2 : 1, 1 : 1, …).
- **Gambar**: 50 kg = beras RATA sejajar bibir kotak; di atas itu MENGGUNUNG sampai 60 kg; di bawahnya permukaan turun. (Dulu 50 kg digambar menggunung.)
- **Lembar literan di Jual**: tombol "Wadah baru diisi ulang" diganti panel **− / + takar** (dilipat; dibuka dengan satu ketukan supaya tuts jual tidak terdorong) + "sampai rata" / "sampai menggunung" / "+ campur merek lain" + **ISI ULANG · CATAT n TAKAR**. Gambar wadah ikut naik selagi + diketuk (pratinjau); yang memutuskan "perlu isi ulang" tetap isi nyata. Isian yang melewati batas menggunung DITOLAK, tidak dipotong diam-diam.
- **Karung di belakang wadah** (per merek): tiap takar mengurangi karung terbuka merek ASALNYA; karungnya habis → satu karung baru otomatis diambil dari tumpukan (dokumen `karung`, ditulis lebih dulu, disebut di kabar). Karung yang belum pernah ditandai TIDAK dibuka diam-diam — sisanya "?".
- **Stok → Wadah literan** (S15): petak **W1–W8 menurut posisi di toko**, tiap petak = karung terbuka di belakang + kotak wadah di depan; rincian: sisa karung, perkiraan tumpukan gudang (= buku − karung terbuka − isi wadah), buka karung baru, samakan. **Atur susunan**: ‹ › memindah posisi, ketuk nama mengganti beras, tambah/lepas wadah, campuran bawaan per wadah, dan empat angka (rata, batas menggunung, batas isi ulang, isi satu takar).
- **Alat ukur, bukan buku**: buku stok merek tetap baru berkurang saat literan TERJUAL (mesin beku tak disentuh) — memotongnya lagi saat isi ulang = beras yang sama dipotong dua kali. Tiga tempat (tumpukan + karung terbuka + wadah) berjumlah sama dengan buku. Sumber tiap takar dicatat per merek, supaya keputusan owner soal **memindahkan buku untuk campuran lintas merek** kelak bisa diterapkan.
- Dokumen `wadahLiteran`: `isi` (samakan wadah) · `takar` {wadah, takar, kgPerTakar, kg, sumber[{merk, takar, kg}]} · `karung` {merk, kg 50} · `karungIsi` (samakan karung) · `atur` {penuhKg, puncakKg, isiUlangKg, takarKg, daftar berurut, resep}. Aturan lama tanpa `puncakKg` → sebanding bawaan (60/50 × rata).
- Adegan baru `adeganIsiUlang`: serok dari karung terbuka ke kotak wadah, permukaannya naik dari isi lama ke isi baru.

## Putaran 9 (21–22 Sep 2026) — RANTAI STOK bertingkat: karung di belakang wadah BERNAMA, diambil dari tumpukan gudang
Koreksi owner 21 Sep: nama seperti "IR64 Elevate / Ascent / Apex / IR42 Value / Select" itu **jenis beras + kelas mutu** (nama JUAL wadahnya), bukan merek; karung yang berdiri di belakang tiap wadah punya **nama karungnya sendiri** (Tawon, Kumala, PM, …, atau nama lama seperti IR64 Apex) dan diambil dari **karung sumber di GUDANG**. Tiap tingkat berkurang lewat jalurnya sendiri, dan jumlahnya harus menutup:
- **Karung terbuka = NAMA × TEMPAT** (temuan tinjau 22 Sep): satu kolam per nama di tiap tempat (di belakang wadah W, atau '' = bahan campuran). Karung "IR64 Apex" yang dibuka di belakang wadah Angsa TIDAK tergambar/terpotong di wadah IR64 Apex; nama yang sama boleh berdiri di belakang dua wadah dan dihitung terpisah. Tiap takar mencatat `sumber[].dari` (tempat asal: wadah senama yang memegangnya → karung bahan campuran yang masih berisi → karung senama di belakang wadah lain → bahan campuran). Karung yang wadahnya sudah berganti karung disebut YATIM dan tampil di "Karung terbuka lain · dulu di belakang wadah W".
- **Buka karung** (Stok → Wadah literan → rincian → "karung lain…" memilih nama dari tumpukan gudang yang masih ada, lalu "Buka 1 karung X dari tumpukan gudang"): dokumen `karung` kini membawa `wadah` (di belakang wadah mana) atau `lepas: true` (karung bahan campuran). **Tumpukan gudang nama itu turun satu karung saat itu juga** — tanpa menulis buku mesin lama. Nama yang tidak ada di buku gudang ditolak; tumpukan yang menurut buku sudah habis tetap boleh dibuka tapi diperingatkan (bukunya yang mungkin salah → cocokkan).
- **Takar**: mengurangi karung bernama itu (`takar.sumber[].merk` = nama karung), menaikkan wadah; karung habis → karung baru otomatis dari tumpukan nama yang sama (dokumen `karung` otomatis membawa `wadah`), kabarnya menyebut tumpukan gudang turun dari berapa ke berapa. Campuran bawaan wadah = karung di belakangnya bila owner belum menyetel resep.
- **Literan terjual**: wadah turun & buku turun (mesin beku, tak disentuh).
- **Pindah nama** (`pindahNama()`): takar dari karung K ke wadah N (K ≠ N) = beras yang akan dijual & dipotong buku sebagai N, jadi di rantai stok ia **keluar dari K dan masuk ke N** — tumpukan K tidak "naik lagi" sesudah ditakar, tumpukan N tidak turun. Hanya takar SESUDAH hitungan gudang (cocokkan) terakhir nama itu yang dihitung: hitungan fisik sudah menyerap pindahan sebelumnya (menghitungnya lagi = dipotong dua kali). Buku mesin lama TIDAK diubah — ini alat baca; memindahkan buku sungguhan tetap keputusan owner (menyentuh nilai persediaan/HPP & sistem lama).
- **Identitas yang dijaga uji**: `tumpukan + karung terbuka + isi wadah = buku − pindah keluar + pindah masuk`, untuk SEMUA nama, memakai angka MENTAH (lupa mencatat isi ulang membuat wadah "minus" & karung "kelebihan" sebesar itu juga — saling menutup, tumpukan tidak bergeser diam-diam). Nama yang cuma pernah masuk sebagai karung 25 kg dibuka per 25 kg (`beratKarungBuka`).
- **Stok → Gudang**: kartu kelima **"Berasnya ada di mana?"** — tiap nama beras: tumpukan (berapa karung, digambar kotak-kotak kecil) · karung terbuka · wadah · buku · pindah nama; yang belum ditandai ditulis "?", bukan 0. Petak W1–W8 menampilkan nama karung di belakangnya ("karung Tawon ±44,6 kg"); "Karung terbuka lain" = karung yang tidak di belakang wadah mana pun (bahan campuran, atau karung lama yang wadahnya sudah berganti karung), bisa dibuka dari sana juga.
- Adegan baru `adeganBukaKarung`: satu karung diangkat dari tumpukan gudang (angkanya turun) → mendarat & dibuka di belakang kotak wadah.
- **Tinjau 22 Sep** (alur 9 agen atas izin Ultracode owner: 3 peninjau + 1 pembantah per temuan; 21 temuan mentah, 6 terbukti — semua ditambal & diuji): karung senama di dua tempat dijumlah (→ nama × tempat); nota literan di MENIT yang sama sesudah samakan tidak dipotong (→ pemutus seri id seperti takar); rework karantina (`penyesuaianStok` `dariRework`, `kgFisik` null) dianggap hitungan gudang (→ dilewati, juga di kartu "belum dicocokkan"); campuran satu baris yang menyalin nama karung di belakang wadah ikut tersimpan lalu terpaku ke nama lama (→ dianggap bawaan, tidak disimpan); "samakan sisa karung"/"pakai angka ini" dengan kotak kosong menulis 0 kg / rata (→ ditolak); calon karung tidak memberi tahu nama yang sudah terbuka di belakang wadah lain (→ disebut).
- Catatan lama (sebelum 21 Sep, tanpa kolom `wadah`) tetap dikenali sebagai karung di belakang wadah senama. Cadangan toko untuk uji lokal boleh di akar, `_privat/`, atau `_arsip-mockup/` (semua di-gitignore; yang terbaru menurut tanggal di namanya).

## Putaran 9b (22 Sep 2026) — adegan angkut: panggul, motor/mobil, tuang & jahit (permintaan owner)
- **Karung 50 kg masuk keranjang** → `adeganPanggul`: orang mengangkat karung dari lantai ke pundaknya. **Kemasan ≥ 10 kg** sama (kemasan 5 kg tetap jatuh ke keranjang belanja).
- **Setengah karung** (1,5 = 25 kg dari karung 50 kg; tuts koma kini boleh untuk karung) → `adeganTuangJahit`: karung 50 kg diangkat & dimiringkan, dituang ke karung bekas sampai separuh, lalu mulut karung bekas dijahit.
- **Nota dicatat** → `adeganMuat`: orang yang memanggul berjalan ke kendaraan, menaruh muatan, kendaraan pergi (roda berputar) → jadi alat bayar. Kendaraan dihitung **per nota** (`kendaraanUntuk`): karung > 3 → **mobil** (bak terbuka), selain itu **motor**; kemasan ≥ 10 kg sama seperti karung; kemasan 5 kg > 20 → mobil, > 1 → motor; literan > 10 L → motor; repack > 10 kg → motor. Tidak ada yang memenuhi → serah terima tangan seperti sebelumnya.
- Teknis: grup yang dianimasikan CSS tidak boleh membawa atribut `transform` (CSS `transform` menimpanya → gambar terlempar ke pojok) — posisinya di grup pembungkus.

## Putaran 10 (22 Sep 2026) — PINDAH BUKU untuk takar lintas nama (keputusan owner: pilihan A)
Sebelumnya takar dari karung nama lain (Tawon → wadah Perahu Layar) hanya dibetulkan di TAMPILAN (`pindahNama`), bukunya tidak: buku Tawon tetap tinggi, buku Perahu Layar turun terus (akar stok minus). Owner memilih **A**: tiap catat takar yang memakai karung nama lain juga **memindahkan buku** — keluar dari karung asalnya, masuk ke nama wadah **dengan modal karung asalnya**.
- Ditulis sebagai satu dokumen `produksiKemasan` **jadi karung utuh** (`jadiKarungUtuh: true`, `merkTujuan` = nama wadah, `sumberList` = karung asal, `kgDipakai` = `ukuranKemasan` × 1 unit, `hppSumberPerKgDipakai` = modal rata-rata tertimbang sumber, `dariTakar: true`, `takarId`; tanpa upah/kantong). Jalur ini sudah dibaca `hitungStokKarungPerMerk` di kedua sistem (pembuatannya dari layar Adukan dicabut 23 Agu, pembacaannya sengaja tetap) — **mesin beku tidak disentuh (28/28)**, `hitungStokKemasan` melewatinya (bukan kemasan jadi), sistem lama ikut benar.
- Dokumen takarnya menunjuk `produksiId`; `pindahNama()` (layar) melewati takar yang pindahannya sudah ada di buku — catatan lama (sebelum putaran ini) tetap dihitung di layar seperti dulu. Semua dokumen satu catat masuk satu `writeBatch`.
- Papan Kapur: "Pindah nama di buku (takar wadah): Tawon 5,4 kg → Perahu Layar ↔ 5,4 kg". Kabar catat menyebut "BUKU: Tawon −5,4 kg → Perahu Layar +5,4 kg (modal ikut)".
- Takar dari karung SENAMA tetap alat ukur saja (buku baru dipotong saat literan terjual).

## Struktur
```
baru/
  index.html            cangkang: nav bawah (HP/Tablet), menu samping (Mac), formulir masuk, <main id="layar">
  css/identitas.css     token C1 (kaca buram emas/sampanye/platina, Bodoni Moda + Jost, body / body.gelap) + komponen dasar
  css/kerangka.css      SATU markup tiga lebar: HP < 720 · Tablet 720–1099 · Mac ≥ 1100
  css/jual.css          bagian khas layar Jual
  js/app.js             pintu masuk: mode, sumber data (Firestore / ?cadangan=), masuk, nav
  js/inti/{format,dom,keadaan}.js   pemformat, penggambar (escape + delegasi data-aksi), penyimpan keadaan
  js/data/koleksi.js    tabel 28 koleksi + kolom pengurut
  js/data/toko.js       cache di memori + ambil*() (nama = index.html) + keranjang aktif/parkir
  js/data/firebase.js   Firestore BACA SAJA, cache tetap IndexedDB (jalan tanpa internet), masuk akun owner
  js/data/cadangan.js   sumber pengganti: berkas backup-batch-*.json (lokal, tidak di repo)
  js/mesin/beku.js      26 dari 28 MESIN UANG BEKU — DIBUAT ALAT (alat-uji/pindah_mesin.py), byte-identik, JANGAN DISUNTING
  js/mesin/pembantu.js  fungsi & konstanta pembantu mesin — DIBUAT ALAT juga
  js/layar/jual-logika.js   logika Jual tanpa DOM (diuji di jsc)
  js/layar/jual.js          gambar & ketukan
```
Belum dipindah (terikat layar lama): `tulisSaldoPembuka` (ritual Tutup Buku), `thPagar` (Tutup Hari).
Jangkar warisan: `stokMaksJalur()` membaca `#jualKarungBerat` dari DOM — layar menyediakan `<input type="hidden" id="jualKarungBerat">`.

## Menjalankan di komputer (tanpa Firestore)
```
python3 -m http.server 8760 --directory .
```
lalu buka `http://localhost:8760/baru/index.html?cadangan=/backup-batch-miqbal-YYYY-MM-DD.json` (berkas cadangan diunduh dari index.html; tidak pernah masuk repo).
Tanpa `?cadangan=`, halaman memakai Firestore toko dan meminta sandi owner (diteruskan ke Firebase Auth, tidak disimpan).

## Gerbang (jalan di CI)
| alat | membuktikan |
|---|---|
| `alat-uji/pindah_mesin.py --periksa` | tiap mesin di `js/mesin/beku.js` = sidik `alat-uji/beku.sha256` |
| `alat-uji/uji_jual_baru.py` (+ `--kontrol`) | 216 skenario logika Jual (baca + catat + batalkan + repack/bonus/pengganti retur/pesanan + retur & tukar + tata letak + wadah literan: takar, karung bernama di belakang, campuran, susunan, rantai stok & pindah nama) di kotak pasir; 106 kontrol positif berbunyi; kunci dokumen vs baris nyata & vs yang ditulis index.html |
| `alat-uji/uji_ringkasan_baru.py` (+ `--kontrol`) | 28 skenario logika Ringkasan (jam tetap, zona waktu dikunci WIB) + 14 kontrol; di cadangan toko: omzet hari/bulan/tahun = jumlah langsung barisnya |
| `alat-uji/uji_stok_baru.py` (+ `--kontrol`) | 31 skenario logika Stok (jam & zona waktu dikunci; rantai stok "Berasnya ada di mana?", karung bernama) + 28 kontrol; di cadangan toko: nilai stok layar = mesin neraca |
| `alat-uji/uji_identitas_baru.py` (+ `--kontrol`) | mesin lama & baru diberi cadangan toko yang sama → hasil identik (lokal saja; 5 kontrol) |

Memindahkan mesin ulang (sesudah `index.html` berubah): `python3 alat-uji/pindah_mesin.py`.
