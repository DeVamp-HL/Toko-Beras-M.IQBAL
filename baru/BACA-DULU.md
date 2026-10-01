# Sistem baru — `baru/`

Tampilan baru di atas **data yang sama** dengan `index.html` (Firestore proyek `toko-beras-m-iqbal`, 28 koleksi, akun owner yang sama).
Hidup berdampingan di alamat `/baru/`; `index.html` tetap alat yang dipakai toko sampai yang baru terbukti.
Keputusan owner 13 Sep 2026: desain ulang termasuk UI **tanpa mengubah data toko**; 17 Sep: *"mulai sambungkan ke data asli"*.

## Arah (keputusan owner 24 Sep 2026)
- **`baru/` = sistem utama owner**, kelak dibungkus menjadi aplikasi native. Catatan native 13 Sep (`_privat/rapikan-2026-09-13/peta_native.md`, `skeptis_native.md` — di mesin owner) masih menyebut `index.html`: **bahan, bukan keputusan**.
- **Tablet kasir = offline-first**, satu perangkat dipakai bergantian, semua akun seizin owner. Pilihan identitasnya (login per orang vs satu akun tablet + PIN per orang) diputuskan di putaran tablet — jangan ditutup.
- **`index.html` pensiun** setelah `baru/` lengkap. Sampai saat itu keduanya membaca & menulis data yang sama; `index.html` tidak diperbaiki lagi (19 Sep).

## Putaran 1 (19 Sep 2026) — layar JUAL, baca
- Rak (Sering · Literan · Kemasan · Karung) dibaca dari data toko lewat **mesin beku yang sama** dengan `index.html`.
- Keranjang, nego, potongan, antrean (struk parkir **memegang** stoknya), bayar (Tunai/QRIS/Bon), nama pembeli, kartu Hari ini.
- Aturan owner yang dipasang: pembulatan Rp500 ke atas untuk **Tunai dan Bon**, QRIS persis (17 Sep); uang kurang → sisanya jadi bon atas nama (17 Sep); siapa cepat dia dapat (17 Sep).
- Belum: Wadah, Repack, Retur, Pesanan, cetak struk, dan semua layar lain (masih di sistem lama).

## Putaran 2 (19 Sep 2026) — nota DICATAT
- Satu pintu tulis `toko.tulisDokumen()` → Firestore `writeBatch` (semua dokumen satu nota masuk bersama; index.html menulis satu per satu) + satu baris `logAktivitas` per dokumen; atribusi `oleh/perangkat/diubah*` persis `simpanKeFirestore()` lama. Tanpa internet: tulisan mengantre di cache tetap Firestore, layar bilang "menunggu server". Kabarnya satu kalimat untuk semua layar: `kabarKiriman(x, kabar)` di toko.js (antre = "Tersimpan di perangkat, menunggu server"; kiriman bertahap membawa `antre`); pil kepala menyebut "N DITOLAK server" (audit 39b no. 28).
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

## Putaran 9c (23 Sep 2026) — nota: TERIMA UANG dulu, baru barangnya (koreksi owner)
- Tiap nota dicatat, adegan PERTAMA = `adeganTerimaUang`: tangan pembeli datang membawa alat bayar, tangan toko menyambut, alat bayarnya berpindah ke tangan toko, pembeli mundur. Tunai = uang (bayar sebagian: + kertas bon kecil), QRIS = ponsel bercentang, **BON = kertas bon, bukan uang**. Keterangannya: "Uang diterima · Rp… · kembali …" / "QRIS masuk" / "Dicatat BON — belum ada uang".
- Sesudahnya (jeda 200 ms) disusul adegan barang: `adeganMuat` (motor/mobil) atau `adeganSerahTerima` — keduanya kini tanpa alat bayar (uangnya sudah tampil duluan), keterangannya menyebut barangnya.

## Putaran 10 (22 Sep 2026) — PINDAH BUKU untuk takar lintas nama (keputusan owner: pilihan A)
Sebelumnya takar dari karung nama lain (Tawon → wadah Perahu Layar) hanya dibetulkan di TAMPILAN (`pindahNama`), bukunya tidak: buku Tawon tetap tinggi, buku Perahu Layar turun terus (akar stok minus). Owner memilih **A**: tiap catat takar yang memakai karung nama lain juga **memindahkan buku** — keluar dari karung asalnya, masuk ke nama wadah **dengan modal karung asalnya**.
- Ditulis sebagai satu dokumen `produksiKemasan` **jadi karung utuh** (`jadiKarungUtuh: true`, `merkTujuan` = nama wadah, `sumberList` = karung asal, `kgDipakai` = `ukuranKemasan` × 1 unit, `hppSumberPerKgDipakai` = modal rata-rata tertimbang sumber, `dariTakar: true`, `takarId`; tanpa upah/kantong). Jalur ini sudah dibaca `hitungStokKarungPerMerk` di kedua sistem (pembuatannya dari layar Adukan dicabut 23 Agu, pembacaannya sengaja tetap) — **mesin beku tidak disentuh (28/28)**, `hitungStokKemasan` melewatinya (bukan kemasan jadi), sistem lama ikut benar.
- Dokumen takarnya menunjuk `produksiId`; `pindahNama()` (layar) melewati takar yang pindahannya sudah ada di buku — catatan lama (sebelum putaran ini) tetap dihitung di layar seperti dulu. Semua dokumen satu catat masuk satu `writeBatch`.
- Papan Kapur: "Pindah nama di buku (takar wadah): Tawon 5,4 kg → Perahu Layar ↔ 5,4 kg". Kabar catat menyebut "BUKU: Tawon −5,4 kg → Perahu Layar +5,4 kg (modal ikut)".
- Takar dari karung SENAMA tetap alat ukur saja (buku baru dipotong saat literan terjual).

## Putaran 11 (23 Sep 2026) — layar Stok yang MENCATAT: Barang masuk (ST1) & Cocokkan (ST3)
Dua tombol di Stok → Gudang kini sungguhan (Adukan masih ke sistem lama). Logika di `stok-catat-logika.js` (tanpa DOM, dijaga `uji_stok_baru.py`); bentuk dokumen PERSIS sistem berjalan supaya kedua sistem membaca angka yang sama — mesin beku tidak disentuh.
- **Barang masuk**: satu mobil = satu dokumen `batchMasuk` {tanggal, jam, pemasok, biayaBongkar, caraBayar tunai|utang, merkList[{id, merk, satuan karung, jumlahKarung, beratKarung, totalKg, hargaPerKg, subtotalHarga}]}. Upah bongkar dibagi ke modal per kg menurut kg (`hitungHppMerkDalamBatch`); "utang" = bon pemasok (masuk `hitungUtangPemasok`, beras saja — bongkar selalu tunai). Draf hidup di localStorage perangkat sampai disimpan. Penjaga: pemasok wajib, baris terisi tapi tak lengkap DITOLAK menyebut barisnya, nama dua kali ditolak, < minimal karung per mobil ditanya (dua ketukan). Harga lalu disebut; beda > 10 % disebut. **Koreksi** menimpa dokumen yang sama (`alasanKoreksi`, `riwayat`), **hapus** beralasan mencabut batch + pasangan beli-jadi (`dariBatch`) dan menulis jejak ke koleksi baru `bukuHapus`; batch fondasi (stokAwal / tutupBuku) tidak diubah/dihapus. Baris bal (beli jadi) tidak dibuat/diubah dari sini.
- **Cocokkan** (tab beras / kemasan jadi / kantong): tiap barang tercatat vs dihitung; beras diketik karung × isi (50/25) + kg lepas; ✓ = cocok persis. Selisih SELALU kg/unit DAN rupiah (× modal saat itu, dikunci di dokumen): `penyesuaianStok` {kgSistem, kgFisik, selisihKg, alasan, nilaiRp, hppPerKgSaatOpname}, `penyesuaianKemasan` {unitSistem, unitFisik, selisihUnit, …}, `stokBahanKemasan`/`stokBahanLiteran` {tipe opname, jumlah, hargaTotal 0, pcsSistem, pcsFisik, catatan, nilaiRp, hargaPerPcsSaatOpname}. Penjaga (pola sistem berjalan): selisih > batas % wajib alasan; angka aneh (> 2× tercatat + 10) dua ketukan; stok bertambah > ambang rupiah dua ketukan ("beras tidak tumbuh sendiri"); simpan sebagian dua ketukan; barang yang sama dicocokkan lagi < 10 menit dua ketukan (kejadian Perahu Layar 26 Agu). Rework karantina bukan hitungan fisik. Nama wadah menyebut rincian tumpukan + karung terbuka + wadah. Hitungan keliling tersimpan di localStorage sampai disimpan.
- **Atur** (angka owner, koleksi baru `aturanToko`, id `catatStok`): minimal karung per mobil (60), tempo bon pemasok (21 hari), selisih wajar (3 %), ambang stok bertambah (Rp250.000) — bawaan = angka sistem berjalan.
- Uji asap di cadangan toko: kolom dokumen barang masuk & cocokkan yang dihasilkan wajib dikenal cadangan (kolom tambahan sistem baru — `jam`, `alasanKoreksi`, `riwayat` — disebut eksplisit).

## Putaran 12 (23 Sep 2026) — ADUKAN (ST2 "Timbangan Adukan") & keputusan KARANTINA
Tombol ketiga di Stok → Gudang (Adukan) dan tab Karantina kini sungguhan. Logika di `stok-adukan-logika.js` & `stok-karantina-logika.js` (tanpa DOM, dijaga `uji_stok_baru.py`); mesin beku tidak disentuh — `bagiBiayaAdukan` dipakai apa adanya.
- **Adukan**: bahan = karung dari tumpukan gudang (nama + kg; "+1 karung 50" / "+25 kg") dan/atau kemasan jadi 50/25 kg yang dibongkar; hasil = baris nama · ukuran (5/10/20/25/50) · unit · kantong (jenis untuk ukuran itu, lembar = unit, boleh diubah, atau "tanpa"); upah kemas. Kartu paling atas = **timbangan**: kg & rupiah bahan masuk ⇄ hasil jadi, susut disebut (terserap ke modal hasil). SATU ADUKAN = SATU KESATUAN BIAYA: bahan (kg × modal rata-rata / unit × modal kemasan) + kantong (lembar × modal per lembar, `hitungStokBahanKemasan`) + upah, dibagi ke tiap hasil menurut kg, sisa pembulatan ke baris terakhir → Σ persis. Dokumen `produksiKemasan` PERSIS `simpanProduksi` index.html (sumberList/kgDipakai/sumberKemasanList/kgKemasanDipakai/upahRepacking hanya di dokumen pertama; batchProduksi/barisKe/jumlahBaris; jadiKarungUtuh false; kolom tambahan `jam`) + pasangan `stokBahanKemasan` {id = id produksi + 1, tipe pakai}. Penjaga (urutan simpanProduksi): baris tak lengkap ditolak menyebut barisnya; bahan = hasil (lingkaran) ditolak; stok bahan / kemasan / kantong kurang, kantong dipilih tanpa lembar ("terhitung GRATIS"), susut > 15 % — masing-masing dua ketukan. Draf di localStorage `miqbal_baru_draf_adukan`. Adegan: karung dituang, kemasan hasil muncul satu per satu.
- **Buku adukan** (beli-jadi kedatangan & pindah buku takar tidak ikut; rework karantina tampil tapi tidak bisa diubah): rincian biaya & pembagian per hasil, timbangan, jejak koreksi. **Koreksi** = TOTAL biaya yang benar → dibagi ulang ke semua baris (`simpanKoreksiHpp` cabang adukan: pengganti ber-`koreksiDari`, lama ditandai `dikoreksiOleh`); alasan wajib; baris seadukan tidak lengkap ditolak. **Hapus** = seluruh adukan + pasangan kantong id + 1 (`hapusProduksi`), alasan wajib, dua ketukan, jejak ke `bukuHapus`; DITOLAK bila hasilnya sudah terjual/terpakai sehingga stok kemasan jadi minus (koreksi saja).
- **Karantina**: tiap barang punya empat pilihan dengan kalimat akibatnya, dan penjaga yang sama menentukan apa yang tampil dan apa yang ditulis. *Ternyata layak jual* (alasan wajib) = retur dikoreksi `kondisi 'utuh'` + `koreksiKondisi` dan kartu `layak_jual` — tanpa dokumen stok (mesin membaca retur utuh sendiri; laba tanggal retur naik); ditolak bila sudah pernah di-rework, stok tidak dikenal, retur tahun lain; cocokkan sesudah retur → dua ketukan. *Rework* = kemasan → dokumen produksi tanpa bahan (modal = rata-rata produk sekarang, `catatan` "Hasil rework dari karantina (retur id …)"), karung → `penyesuaianStok` `dariRework` nilai Rp0 — barangnya dulu, statusnya belakangan, satu writeBatch. *Balik ke pemasok* / *Buang* = status saja, dua ketukan, kalimat jujur: kerugiannya SUDAH tercatat saat retur, laba tidak berubah lagi. Retur yang sudah dikoreksi utuh menolak rework/buang/balik (barang bergerak dua kali). Beda dari sistem lama: ditulis writeBatch dari salinan perangkat ini (bukan transaksi baca-ulang server) — putuskan dari satu perangkat.
- Belum: adukan "menunggu owner" dari tablet (menyusul bersama layar tablet), bal/beli-jadi, kantong (ST4), tempat (ST5), HPP (ST6).

## Putaran 13 (23 Sep 2026) — layar PELANGGAN: Kenali (PL1) · Bon (PL2) · THR (PL3)
Layar keempat hidup: `layar/pelanggan.js` + `css/pelanggan.css`; logika di `pelanggan-logika.js` (Kenali + THR) dan `bon-logika.js` (Bon), tanpa DOM, dijaga `uji_pelanggan_baru.py`. Orang = nama yang diketik di nota (`kunciPelanggan`, sama dengan sistem berjalan); "sekarang" = jam perangkat (mode cadangan: saat unduh).
- **Kenali** (dikunci owner 18 Sep: Sketsa · Tampah · Belanja · Jam · Minggu · Benang · Hafalan): tiap orang punya SKETSA dari cip ciri di kartunya (kerudung/peci/kacamata/uban; lencana = naik apa & beli apa); Tampah bertanya ciri yang membelah sisa paling rata; Belanja menebak orang dari nota besar tanpa nama hari ini (≥ batas owner) → "ini dia" menulis ulang `namaPelanggan` di semua baris nota itu (satu nota = `grupNota` → `trxId` → satu baris; nota sistem baru & keranjang index.html hanya ber-`trxId` — sebelum putaran 25 terpecah per baris); Jam dinding & Minggu dari kedatangan nyata (selang = median hari antar-kedatangan, ≥ 3 hari; bangku kosong = ≥ N× selangnya sendiri); Benang = koleksi baru `pelangganTitip` (yang datang bukan orangnya; bukan penyatuan nama); Hafalan = kuis dari yang bercip (nilai per HP di localStorage). **Kartu** = `pelangganCatatan` {id = kunci, nama, catatan, ciri, rute} persis simpanCatatanPelanggan — `ciri` ditulis gabungan cip, `rute` = arah → gerbang KR1 sistem lama membaca "dikenali" yang sama; kolom baru cip[], arah, asli, kontak, biasa. Nama kembar hanya DITAWARKAN; SATUKAN = owner memutuskan → semua dokumen bernama itu ditulis ulang atas satu nama (batas 180 dokumen = satu writeBatch), kartu lama dihapus; "bukan kembar" dicatat di `aturanToko/pelangganKembar`.
- **Bon** (Buku · Papan · Umur): angka dari mesin beku `hitungPiutang`; rincian FIFO = rincianBelumLunas index.html; status menurut aturan owner (tagih sesudah N hari, macet = tertua > M hari DAN tanpa pembayaran selama itu; janji bayar dari tagihan). Tagih = kalimat kirimTagihanPiutang + salam owner, nomor dari kartu (0812… → wa.me/62812…), dicatat ke koleksi baru `tagihPelanggan` {kunci, nama, tanggal, jam, janji, sisa}. Bayar = `piutangMutasi` {tipe bayar, namaPelanggan, nominal, tanggal, jam, caraBayar Tunai|QRIS, catatan, dicatatDi} persis simpanBayarPiutang (+ `dibawaOleh` bila pengantarnya orang lain); tidak boleh melebihi sisa; LUNAS hanya bila nol. Hapus buku = {tipe hapusBuku, alasan, …} persis simpanHapusBuku: alasan wajib + dua ketukan, kalimat jujur "bukan uang masuk — kerugian bulan ini".
- **THR** (Daftar setia · Meja bingkisan · Amplop): `thrPelanggan` {tahun, kunci, nama, bentuk, nilai, tanggal, jam} (kolom catatThrPelanggan) + `serah`/`serahTanggal`; satu THR per orang per tahun; usulan dari sisa amplop; catatan siapa dapat apa — bukan catatan uang.
- **Atur** (`aturanToko/pelanggan`): bangku kosong (× selang), nota yang perlu nama, waktunya ditagih, macet, anggaran THR, salam tagihan, cip ciri (+ kelompoknya), arah, urusan titipan, alasan hapus, bentuk THR — baris yang masih dipakai tidak bisa dihapus.
- Uji asap di cadangan toko: kunjungan layar = pasangan nama×hari nyata, belanja bernama = baris nyata, sisa bon = mesin beku, kolom dokumen bayar/hapus/kartu dikenal, kop tagihan tetap.

## Putaran 14 (23 Sep 2026) — layar MENU (N1 + pita jam N9) & SISTEM (SS1–SS5)
Layar kelima hidup: `layar/menu.js` + `css/menu.css`; logika `menu-logika.js` (prefiks `mn`) & `sistem-logika.js` (`ss`), tanpa DOM, dijaga `uji_menu_baru.py`. Kelima petak nav kini hidup — tidak ada lagi petak yang "mengaku belum ada".
- **Menu = rangka laci N1** (dikunci owner 16 Sep: "pertahankan desain UI di layar N1"; CSS `.mn-*` diambil mentah dari helmet N1): kepala kelompok buka-tutup (diingat per perangkat), tiap baris ikon + judul + sub + angka + keterangan; lencana merah = belum beres. Laci PALING ATAS = **pita jam** (N9): tujuh pekerjaan yang jamnya terbaca (nota meja, rinci karcis, tutup hari, belanja, buku bon, opname, katalog) di bagian hari SEKARANG — tujuh baris selalu tujuh dan tidak berpindah tempat; laci "Ganti bagian hari" tertutup sejak lahir. Di bawahnya sepuluh laci N1 (Buku besar · Alat toko · Toko ini) **+ dua baris Sistem** (Lokasi, Pengingat) di "Toko ini" — keluarga Sistem lahir sesudah Menu dan desainnya berkata "di bawah Menu". Baris "Akun & PIN" desain menjadi "Peran & persetujuan": sistem baru tidak punya kolom PIN (aturan tetap; kunci perangkat diatur di perangkatnya).
- **Semua angka DIBACA** dari data toko lewat mesin yang sama (hitungUtangPemasok, hitungPiutang, hitungLabaBersihRentang, hitungNeraca, kasPada, hitungKasbon, hitungStokKarungPerMerk …); tidak ada angka yang lahir di layar Menu. Yang belum bisa dihitung ditulis begitu (kas & kekayaan tanpa titik kas), tidak ditebak.
- **Tujuan tiap baris**: layar sistem baru dibuka lewat PENANGAN yang sama dengan ketukan di layar itu (`stok.buka(lembar|tab)`, `pelanggan.buka(keluarga, orang)`), lembar Sistem di dalam Menu, atau **sistem lama** (Pemasok, Harga, Laba, Setelan, Tutup Hari, Harian, Bulanan — belum ada di sini): kabarnya menyebut halamannya + tautan `../index.html` (tidak ada tautan dalam ke halaman sistem lama; index.html tidak disentuh).
- **Empat dasar penyusunan lain** = tab (rangka laci yang sama): **Tanya** (N2: sepuluh pertanyaan, jawabannya kelihatan sebelum diketuk), **Jam** (N5: lima laci bagian hari), **Orang** (N6: satu nama seluruh buku — dua sisi buku, pemasok, pembeli, pegawai, yang menulis), **Tertutup** (N8: pintu yang tertutup berikut sebab & pembukanya; yang sudah terbuka — hapus buku sejak putaran 13 — ditulis terbuka). **Cari** layar / merek / nama orang sungguh mengetik.
- **Sistem (SS1–SS5, dikunci 19 Sep) sebagai lembar Menu**, angka & daftar owner di `aturanToko/{perangkat,peran,cadangan,lokasi,pengingat}` (bawaan = angka desain):
  - **Perangkat & antrean (SS1)**: kartu dari `perangkatStatus` (denyut sistem lama; sistem baru kini menulis denyutnya sendiri `aplikasi 'baru'` + pemegang + lokasi); **antrean = catatan yang sungguh belum diakui server** (`hasPendingWrites` tiap dokumen, bukan hitungan sendiri) — dikirim Firestore sendiri, tidak ada tombol kirim, tidak ada yang bisa dibuang; "Periksa: sudah sampai semua?" = `waitForPendingWrites` berbatas waktu. Jejak = `logAktivitas` **150 tulisan terakhir** (koleksi berbatas `batas` di koleksi.js — bukan seluruh riwayat), "belum sampai" = masih di antrean. Pemegang perangkat ini (daftar Atur, Owner tak terhapus) → kolom `oleh`/`diubahOleh` tulisan berikutnya (bawaan Owner = sama dengan dulu). Nama perangkat = kunci localStorage yang sama dengan sistem lama.
  - **Peran & persetujuan (SS2)**: 13 tindakan × (Ben, karyawan) → boleh sendiri / minta owner / tidak boleh (ketuk memutar; owner selalu boleh, dijaga dua lapis); papan persetujuan membaca koleksi baru `persetujuan` (ditulis tablet karyawan kelak — sekarang kosong dan mengaku); tolak wajib alasan; "setujui semua yang kecil" ≤ batas Atur.
  - **Cadangan & simpanan (SS3, pilihan C)**: UNDUH berkas = bentuk `unduhBackup()` sistem lama (versi 5, cap era tutup buku dari saldo pembuka) + koleksi baru, tanpa jejak & denyut; tiap unduhan dicatat ke koleksi baru `cadanganCatatan`; kalender 14 hari; kuota = ukuran localStorage alamat ini (simpanan lokal SISTEM LAMA) vs ±5 MB dengan laju ±62 KB/hari (PERKIRAAN, pengukuran 15 Sep) + `navigator.storage.estimate`; memulihkan dari berkas TETAP lewat Setelan sistem lama (tidak dibangun; keputusan owner dua kali cadangan).
  - **Lokasi (SS4, fondasi)**: daftar lokasi (tepat satu utama), lokasi perangkat ini → kolom `lokasi` pada tiap tulisan berikutnya (hanya bila owner menyetelnya); pindah stok = DUA catatan `pindahStok` (keluar di asal, masuk di tujuan; ≤ stok asal; pengantar dari daftar) — buku mesin lama tidak disentuh; laporan per lokasi membaca kolom `lokasi` (catatan lama = lokasi utama); tumpukan per lokasi menutup buku (identitas diuji). Lokasi berisi stok / dipakai perangkat / utama tidak bisa dihapus.
  - **Pengingat (SS5, pilihan B + C)**: lima sumber dari data — bon pemasok (tanggal bon + tempo `aturanToko/catatStok`), janji bayar (`tagihPelanggan`, gugur bila sudah membayar sesudah ditagih), kantong menipis (laju pakai 14 hari; tanpa laju TIDAK ditebak), opname rutin, cadangan berkas; hari-sebelum per jenis, penerima Owner/Ben; keadaan (selesai dengan catatan — wajib bila lewat; tunda berbatas; WA janji = kalimat tagihan Pelanggan, kedua kali sehari ditanya) di koleksi baru `pengingat`. "Selesai" tidak mencatat uang.
- Uji asap di cadangan toko: angka laci pemasok & piutang = mesin beku; pita = silang jam; berkas cadangan sistem baru memuat SEMUA koleksi cadangan lama dengan jumlah yang sama.

## Putaran 15 (23 Sep 2026) — WADAH DIJUAL (keputusan owner 17 Sep) & STRUK (JS3-A + JS3-C, dikunci 18 Sep)
Dua sisa keluarga Jual. Logika di `wadah-jual-logika.js` (`wj`) dan `struk-logika.js` (`st`), tanpa DOM, dijaga `uji_jual_baru.py`; layarnya menumpang `jual.js`.
- **Wadah = barang dagangan** (owner 17 Sep: "6 L literan + kemasan Kembang 5 kg Rp2.000 = ditagih"; sistem lama mencatat wadah HANYA sebagai biaya lewat `biayaKemasanLiteran`, nol yang pernah ditagih). Jalur **Wadah** di rak Jual: kantong kemasan & karung bekas per LEMBAR, tiap lembar jadi **baris nota sendiri** (`jenis: 'wadah'` — jenis BARU: mesin stok beras tidak menyentuhnya, mesin laba membacanya seperti baris lain), menambah omzet; buku kantong/karung bekas dipotong lewat dokumen `pakai` (id nota + 1) di koleksi bahannya — pola yang sama dengan kantong literan. Jenis wadah = kunci koleksi bahan sistem lama (`5kg_kembangbmw` … di `stokBahanKemasan`; `paperbag5l/10l`, `karungbekas` di `stokBahanLiteran`), jadi stok & modal dibaca mesin beku yang sama (`hitungStokBahanKemasan/Literan`, `hargaBahanLiteranEfektif`).
- **Harga jual per lembar = katalog BARU `hargaWadah`** (id = jenis; diatur owner dari jalur Wadah › "Atur harga jual wadah"). Yang belum diberi harga TIDAK tampil di rak (bukan Rp0). Lantai **Rp100/lembar** (Rp1–99 ditolak: kejadian Rp1.000 untuk 1.000 lembar → Rp1/lembar). Jangan pakai nama `katalogHargaKemasan` — itu harga beras dalam kemasan.
- **Modal**: kantong = rata-rata beli dari buku; paper bag/karung bekas = harga efektif yang sama dengan biaya literan. Wadah yang **belum pernah dibeli tidak punya modal Rp0** — baris notanya ditulis TANPA `hppTotalSaatJual`, sehingga mesin laba menaruhnya di "tanpa HPP" (omzet ada, margin belum bisa disebut), bukan margin 100 %. Modal di buku di bawah Rp100/lembar dilaporkan **PERIKSA** (catatan beli salah satuan; laba wadah itu tergambar terlalu besar sampai dibetulkan di sistem lama). **Karung bekas = hasil samping**: tidak dibatasi buku (bukunya tetap dipotong).
- **Repack** (lembar jumlah repack): pilih wadahnya (merek → ukuran, semua jenis buku tampil, yang tanpa harga jual ditandai), **lembar bebas** dengan saran = kg ÷ muatan dibulatkan KE ATAS (25 kg = 1 karung bekas — aturan owner 15 Sep), lalu **Dijual ke pembeli** (baris wadah sendiri; wadah tanpa harga jual DITOLAK dengan arahan) atau **Ditanggung toko** (biaya masuk `hppTotalSaatJual` baris repack: `kemasanRepack`, `jumlahKemasanRepackDipakai`, `biayaKemasanRepack` + dokumen pakai). **Upah repack** per nota (owner 16 Sep: fleksibel, boleh nol) melekat ke baris repack (`upahRepack`, ikut `hargaTotal` seperti `pembulatan`) — dipertahankan saat baris dibangun ulang (+/−, nego). Semuanya memegang buku kantong juga saat diparkir. Belum: sumber beras "kemasan dipecah" (itu ranah Adukan) dan ukuran 3 kg (tidak ada di buku kantong).
- Pembatalan nota mencabut dokumen pakai wadah (buku pulih). Kolom BARU milik sistem baru di baris `penjualan`: `jenisWadah`, `kemasanRepack`, `jumlahKemasanRepackDipakai`, `biayaKemasanRepack`, `upahRepack`. Di sistem lama baris `wadah` tampil dengan `namaProduk` (jumlahnya "—"); **jangan** mengoreksi jumlahnya dari lembar koreksi sistem lama (`jumlahTrx` null) — batalkan saja dari sistem baru.
- **Struk** (JS3-A + C): satu penyusun untuk **kertas 58 mm (30 kolom) / 80 mm (42 kolom)** dan **WhatsApp** (isi sama, `*tebal*`, tanpa spasi pengisi) — hanya MENYUSUN nota yang tersimpan, tidak ada angka baru: kop (nama/alamat/telp), hari-tanggal-jam, nama pembeli, "Dilayani <oleh>", baris barang (kotor = hargaTotal + potongan − pembulatan − upah, jadi **baris + potongan + pembulatan + upah = TOTAL** — diuji), Potongan, Pembulatan Rp500, upah repack, TOTAL, tukar (barang kembali / DIBAYAR PEMBELI), BON a.n. + **sisa bon dari mesin piutang**, Bayar/Uang diterima/Kembali, "(catatan ini sudah dibatalkan)", kalimat kaki. Yang tidak muat DIBUNGKUS ke baris berikutnya, tidak dipotong. Dibuka dari "Nota barusan › Struk" dan dari tiap baris kartu **Hari ini** (nota lama: `trxId` → `grupNota` → satu baris).
- **Kirim WhatsApp** = `wa.me/?text=` TANPA nomor (WhatsApp yang bertanya ke siapa; nomor pembeli tidak disimpan — sama dengan sistem lama). **Cetak** = teks yang sama lewat dialog cetak perangkat (`#cetakStruk`, satu-satunya yang tampil saat print, lebar 58/80 mm) — printer struk tertanam baru ada di tablet karyawan (belum dibangun). Tiap struk yang keluar dicatat di koleksi BARU **`strukKeluar`**; "N struk keluar hari ini" di lembar.
- **Setelan owner** `aturanToko/struk`: kop, kalimat kaki, lebar kertas, yang disertakan (rincian / sisa bon / kaki / siapa yang melayani — bisa ditimpa per struk), **aturan otomatis** sesudah nota tersimpan: cetak (tidak / tunai saja / semua) & WhatsApp (tidak / bon saja / semua), dan **pilihan per pelanggan** (ikut aturan / selalu WA / selalu cetak / tidak perlu — mengalahkan aturan). Bawaan: keduanya MATI. WA otomatis membuka jendela baru tanpa ketukan → bisa DITAHAN peramban HP; kalau begitu dikatakan di kabar, tombolnya tetap ada. MDR QRIS = catatan toko, tidak dicetak.
- Id dokumen nota kini MENAIK (`idUnikMenaik`): dalam satu milidetik pecahan acak bisa membalik urutan baris — struk mengurutkan baris menurut id.

## Putaran 16 (23 Sep 2026) — layar Stok: KANTONG (ST4-B+C) · TEMPAT SIMPAN (ST5-A) · HPP / MODAL (ST6-A+B)
Tiga lembar baru dari tombol baris kedua di Stok → Gudang (juga dari kotak cari Menu). Logika `stok-kantong-logika.js` (`kt`), `stok-tempat-logika.js` (`tp`), `stok-hpp-logika.js` (`hp`), tanpa DOM, dijaga `uji_stok_baru.py`.
- **Kantong**: beli kantong kosong & paper bag **per batch** (jenis · jumlah · harga per LEMBAR · toko) → dokumen `stokBahanKemasan`/`stokBahanLiteran` bentuk `simpanBeliBahanKemasan` sistem lama + kolom baru `hargaPerPcs` (yang DIKETIK), `jam`, `toko`. Harga per lembar TIDAK pernah diambil dari total ÷ jumlah saat mengetik; di bawah lantai (Rp100) ditanya "per LEMBAR?"; lonjakan > batas % vs beli terakhir ditanya (dua ketukan). **Tunai saja** — mesin arus kas menghitung tiap `tipe 'beli'` sebagai uang keluar laci; bon kantong tidak punya buku di mesin mana pun (desain "bon" tidak dibangun). Rak = tumpukan per jenis (tinggi = sisa; merah bila cukup < hari aman menurut `hitungLajuPakai`); buku beli (dokumen lama ditandai "harga = total ÷ jumlah"); hapus batch beralasan + dua ketukan, **ditolak bila membuat buku minus** (lembar sudah terpakai — arahnya Cocokkan); jejak `bukuHapus`. Riwayat harga per jenis ▲▼. Karung bekas tidak di sini (hasil samping). Atur `aturanToko/kantong` {lonjakan 15, hariAman 7, lantaiHarga 100}.
- **Tempat simpan**: peta = dokumen **`pengaturan/tempatSimpan {peta}` yang SAMA dengan sistem lama** (kunci `K:<nama>`; kemasan jadi `M:<nama|ukuran>`); koleksi `pengaturan` kini dibaca (cadangan lama: `petaTempatSimpan` disuntik ke sana). Ketuk barang → ketuk tempat (denah / daftar / "tanpa tempat"); dikosongkan = kunci DIBUANG (seperti index.html). Pindah = catatan saja (stok & modal tetap), dicatat di koleksi baru `pindahTempat`. Daftar tempat + **kotak denah** (8 posisi tetap: atas/bawah penuh, kiri/kanan atas, kiri/tengah/kanan bawah — bukan digambar bebas) + batas menumpuk di `aturanToko/tempat`; tempat berisi tidak bisa dihapus; nama dari peta lama yang belum ada di daftar ikut tampil tanpa kotak. Menumpuk = tempat memegang nilai rak > batas %. Label rak (ST5-C) tidak dipilih owner → tidak dibangun.
- **HPP / modal**: kartu per nama beras — **modal rata-rata tertimbang (buku; = laba & neraca)**, harga beli terbaru (aturan owner 13 Sep, PEMBANDING; mesin belum diubah — keputusan owner), harga jual per kg katalog karung, margin (RUGI hanya bila `<` 0; 0 = "disengaja?"; tanpa katalog = disebut), nilai rak, sumber kedatangan terakhir. Garis waktu per nama = tiap kedatangan (harga + bongkar/kg) + pindah buku takar, koreksi diwarnai, lonjakan ditandai. **HPP adalah turunan** — koreksi = mengubah **harga beli/kg pada kedatangan TERAKHIR nama itu** lewat `susunSimpanMasuk` (dokumen batchMasuk yang sama, `alasanKoreksi` + `riwayat`), bukan menimpa angka lain; pratinjau Δ modal & Δ nilai rak memakai rumus replika `totalMasuk()` yang DIUJI sama dengan mesin (termasuk bongkar). Ditolak dengan kalimat: < lantai (Rp5.000/kg), > 3× modal, nama tanpa kedatangan non-fondasi, harga sama; lonjakan modal > batas % ditanya; di atas harga jual boleh tapi diperingatkan RUGI. Tiap koreksi menulis jejak `koreksiHpp` {merk, batchId, hargaDari/Ke, modalDari/Ke, sisaKg, deltaNilai, alasan}. **Massal** = semua-atau-tidak (satu writeBatch; dua nama di batch yang sama → satu dokumen). Atur `aturanToko/hpp` {batasLonjak 10, lantaiHpp 5000}.
- Belum: bon kantong, label rak, denah bebas; adukan-menunggu dari tablet (bersama layar tablet).

## Putaran 17 (23 Sep 2026) — layar HARGA & PEMASOK: KATALOG (H1) · BON PEMASOK (H2) · BELANJA (H3)
Layar keenam, `layar/harga.js` + `css/harga.css`; logika `harga-logika.js` (`hg`), `bon-pemasok-logika.js` (`bp`), `belanja-logika.js` (`bl`), tanpa DOM, dijaga `uji_harga_baru.py`. Dibuka dari Menu (baris Pemasok & utang · Katalog harga · pita jam · Tanya · Orang → pemasok · Tertutup · cari) dan Stok → Gudang → "Apa yang harus dibeli" → "Susun belanja"; di Mac ada di menu samping. Petak nav bawah tetap lima (petak Menu yang menyala = pintunya). Mesin beku tidak disentuh.
- **Katalog harga** (dikunci owner 18 Sep: gabungan Papan Kapur · Satu Kalimat · Timbang Dampak · Modal dan Pasar · Karung Dibelah · Label Rak): katalog = TIGA koleksi sistem lama (`katalogHargaKarung` per kg · `katalogHargaKemasan` per unit · `katalogHargaLiteran` per liter) — dokumen persis `simpanHarga*` index.html + kolom baru `modalSaatSetel` (harga beli terbaru saat harga disetel; dokumen lama membacanya dari kedatangan terakhir sebelum `diubahPada`). Baris = tiap merek × satuan yang ada di katalog atau di buku stok. **Perubahan = DRAF** (`aturanToko/hargaDraf`, ikut ke semua perangkat) sampai **TERBIT = satu writeBatch** untuk semuanya (katalog + draf kosong + label rak + `hargaTerbit`) — kasir tidak pernah melihat katalog separuh baru separuh lama; draf rugi → dua ketukan. Modal = modal rata-rata buku (sama dengan laba, neraca, layar HPP; kemasan = dari adukan: beras + kantong + upah), harga beli terbaru = pembanding. RUGI hanya bila modal > harga (tegas); harga = modal = "untung nol"; "modal naik sesudah harga disetel" = dimakan. Target untung bawaan = rata-rata untung katalog karung yang berlaku (bukan angka karangan). **Papan** = papan kapur (sisi owner: draf/rugi/lubang ditandai; sisi pembeli: hanya yang terbit) + teks daftar harga WhatsApp; **Kalimat** = perintah massal dari harga SEKARANG, dibulatkan searah; **Dampak** = selisih × terjual 30 hari (anggapan pembeli tidak berkurang DISEBUT); **Pasar** = catatan owner harga toko lain (`hargaPasar`, tak pernah ke kasir); **Belah** = ke pemasok / kantong+upah / bongkar per kg (terukur dari kedatangan) / potongan QRIS di atas batas / tinggal di toko (menutup); **Label** = harga terbit meninggalkan tugas ganti label (yang diingat = angka yang masih tertulis). "Biarkan — ini sengaja" diingat (`aturanToko/hargaSengaja`), gugur sendiri saat modal/harga berubah. Atur `aturanToko/harga` {targetPerKg, bulatLiter 500, bulatKemasan 1000, bulatKarung 100, langkahRp 50, ambangDampak 50000, bongkarKg (terukur), mdrPersen 30 = 0,30 %, mdrBatas 500000}. `ringkasanKasir` (ringkasan kasir HP) TIDAK diterbitkan ulang dari sini — itu urusan sistem lama. **25c:** sekarang ikut di kiriman terbit yang sama (lihat Putaran 25c).
- **Bon pemasok** (dikunci 18 Sep: Tusukan bon · Jatuh tempo · Buku bon): bon dari mesin beku `hitungUtangPemasok` (sisa = nilai − Σ bayar; yang dibayar sebagian TETAP di daftar). Bayar = `utangPemasokMutasi {tipe bayar, pemasok, nominal, catatan, bonId, bonTanggal}` persis `simpanBayarBon` + kolom baru `dari` (laci/brankas/rekening), `biayaAdmin`, `adminNama`; biaya admin transfer = `pengeluaranHarian {kategori toko, dariBayarBon}` dalam batch yang sama (biaya toko → laba berkurang segitu; bayar bonnya sendiri tidak menyentuh laba). Satu pembayaran = satu bon, ≤ sisa bon; bon tertua cuma saran. Uang toko = TOTAL `kasPada` (sistem lama tidak memisahkan saldo per kantong; tanpa titik kas tidak dibandingkan). Urungkan ≤ 90 detik menghapus bayar + adminnya. Bon lama = `{tipe saldoAwal, bonTanggal|null}` (utang bertambah; uang/stok/laba tidak). **Tempo** = kartu pemasok > tempo umum (`aturanToko/catatStok.tempoHari`, bawaan 21 = angka Atur Barang masuk) — dipakai juga Menu & Pengingat (satu kebenaran); bon tanpa tanggal tidak diramal. Kartu = `pemasokCatatan {id kunci, nama, kontak, catatan}` + kolom baru `orang`, `tempo`. Atur `aturanToko/bonPemasok` {dekatHari 7, admin [{nama, n}]}.
- **Belanja** (dikunci 18 Sep: Isi truk · Kapan habis · Daftar): rumus `hitungSaranBelanja` sistem lama (habis ≤ ambang hari → butuh laju × target − sisa, ke atas ke karung yang biasa dipakai merek itu; laju = `hitungLajuPakai`; tanpa laju tidak ditebak). Harga = harga terakhir per pemasok dari kedatangan (tanggalnya selalu ditulis); kebiasaan bayar pemasok = 3 kedatangan terakhir (bon vs tunai → "jadi utang, jatuh tempo ±…" vs "perlu uang, dibandingkan kas"). Muatan truk bawaan = **median berat 12 kedatangan terakhir** (terukur, disebut), owner boleh mengubah. "Penuhi truknya" menambah karung ke merek yang paling cepat habis sesudah pesanan (tanpa laju tidak ikut). Daftar yang disusun = localStorage perangkat; **kirim** = WhatsApp (nomor dari kartu pemasok; tanpa nomor WhatsApp yang bertanya) + dokumen `pesananPemasok {pemasok, baris, karung, kg, rp, status menunggu, teks, keNomor}`; "sudah datang" dibaca dari kedatangan pemasok itu SESUDAH pesanan (Barang masuk), atau ditandai/dibatalkan tangan. Atur `aturanToko/belanja` {ambangHari 7, targetHari 14, muatanKg}.
- Koleksi baru: `hargaPasar`, `hargaTerbit`, `pesananPemasok` (owner saja). Belum: pesan WA otomatis/terjadwal, bon pemasok di tablet karyawan, harga tetangga sebagai data (tetap catatan).

## Putaran 18 (23 Sep 2026) — layar UANG: K1 Uang keluar · K2 Orang & upah · K3 Owner & toko · K4 Pindah uang · K5 Tutup hari · K6 Tutup buku
Layar ketujuh (`js/layar/uang.js` + `css/uang.css`), dibuka dari Menu (Laci: Tutup buku · pita jam: Tutup hari & kas, Belanja harian · Tanya: Uang toko ada di mana · cari) dan menu samping Mac; nav bawah tetap lima (petak Menu menyala).
Bentuk dari kanvas Layar Kerja Uang yang dikunci owner 17–18 Sep: K1 Pita Laci · K2 Buku Upah · K3 Timbangan · K4 Tiga Tempat Uang bergambar · K5 Lembar Tutup · K6 Berita Acara.
- **Satu kebenaran uang**: `kasPada()` (mesin beku) = seluruh uang toko. `saldoKantong()` (`uang-logika.js`) MEMBAGI total itu ke laci · brankas · rekening · amplop: berangkat dari titik kas, tiap gerakan kas mesin diletakkan di tempatnya (dokumen bertanda `dari`/`tempat` menang, sisanya aturan lama: QRIS → rekening, lainnya laci), lalu pindah tempat (amplopLaba, pindahUang) digeser. Σ empat tempat = kasPada SELALU (dijaga uji). Titik kas kini dibaca dari dokumen `pengaturan/titikKas` bila lebih baru dari salinan perangkat (pendengar onSnapshot titikKas sistem lama ditiru di `ambilTitikKas`).
- `js/layar/karcis-logika.js` — putaran 20: antrean karcis kasir darurat & nota perlu-dirapikan, tebakan katalog, ikat ke keranjang, SIMPAN RINCIAN (bentuk simpanRinciTrx), perbaikan cara bayar/nama, tarik balik, riwayat rinci hari ini. Retur tanpa nota & tukar yatim ada di `retur-logika.js`.
- `js/layar/laporan-logika.js` — putaran 19: Laba (tiga keping per bulan), Harian (rekap hari, buku kas), Bulanan (enam bulan, inti, rekap omzet 12 bulan, tanda lapor, bukti), Neraca (dua sisi per tanggal), DK1 kop & identitas berversi, DK2 laporan berkop (laba-rugi/neraca/arus kas, paket bank, banding), DK4 dokumen kecil (setor, slip, kartu piutang, rekap bon, salinan nota), cetakan bernomor (`dokumenCetak`).
- `js/layar/laporan.js` + `css/laporan.css` — layar Laporan & Dokumen: enam keluarga, kertas dokumen (.dk-*) satu penyusun untuk layar, dialog cetak (`#cetakDokumen`, `body.cetak-dokumen`), dan WhatsApp (teks).
- **K1**: `pengeluaranHarian` kategori toko/owner/tokoDompet (bentuk lama) + `dari`; "untuk pribadi pakai dompet" tidak ditulis. Kasbon owner = `kasbonMutasi` a.n. **Owner** (`owner: true`) — mesin kasbon, neraca, tutup buku sudah menghitungnya. Batas aman prive = setelan owner, bawaan = laba bersih bulan berjalan (penjaga modal lama). Keperluan bawaan TERUKUR (keterangan tersering + median). Tagihan bulanan: 4 pos mesin lama → dokumen `biayaBulanan` (tanggal per pos + `dariPos`; dokumen bertanggal tunggal dipindah ke peta per pos MEMBAWA semua pos bernilai); tagihan tambahan owner = belanja harian "<nama> (bulanan)". Titipan tablet = `persetujuan` tindakan uangKeluar → disetujui menulis pengeluarannya.
- **K2**: `absenKaryawan` (hari kerja per orang per bulan) · upah SEJAK TERAKHIR DIBAYAR (slip terakhir → bulan lama yang dibayar → hari kerja pertama) · bayar = baris `rincianGaji` berkunci **"Nama · tanggal bayar"** di `biayaBulanan` bulan-bulan tercakup (kunci bertanggal supaya mesin lama tidak mengalokasikan potongan "Potong gaji" lama ke baris ini dan dua pembayaran sebulan tidak saling menimpa) + kasbon `bayar` **'Dipotong upah'** (kas MASUK sebesar potongan, sehingga kas bersih = yang diterima) + `slipUpah`. AWAS: layar Bulanan sistem lama menimpa `rincianGaji` dengan nama tetapnya bila dipakai menyimpan bulan yang sama.
- **K3**: setor/tarik = `modalOwner` + `tempat`; pinjaman owner = `modalOwner` setor `pinjaman: true` (uang masuk) + `utangOwnerMutasi` saldoAwal `pinjaman: true` (utang timbul tanpa laba) — modal tertanam sistem baru tidak menghitung dokumen pinjaman (sistem lama menghitungnya sebagai setoran, tidak diperbaiki); kasbon → prive & saling lunaskan memakai `caraBayar 'Potong gaji'` + `alih` (mesin: bukan uang masuk) dan `utangOwnerMutasi` saldoAwal NEGATIF.
- **K4**: `pindahUang {dari, ke, nominal, alasan, biayaAdmin}` + admin = `pengeluaranHarian` toko `dari` sumber (`dariPindah`); daftar biaya admin = `aturanToko/bonPemasok.admin` (satu daftar dengan Bon pemasok). Rutin dari isi SAAT INI (`aturanToko/pindahUang.jaga`).
- **K5**: SEMUA langkah ditulis sekaligus saat "Tutup hari": `tutupHari` (bentuk lama + `sistemBaru`, `dihitung`, `mdr`, `sisihJadi`, `amankanJadi`, `timbang`), `amplopLaba am-`, `setoranKas st-` & `modalOwner mo-st-` nol, `pengeluaranHarian mdr-` (potongan QRIS jadi biaya; perkiraan tarif Atur harga atau sebenarnya), `penyesuaianStok dariTutup`, `pindahUang pd-`, `pengaturan/titikKas` = isi SESUDAH tutup. kasFisik* = isi saat dihitung (Σ fisik − seharusnya = selisih laci). Tutup ulang: sisihan/amankan yang sudah ditulis TETAP (uangnya sudah pindah), yang dikerjakan lagi menambah, MDR diganti. Draf per hari di localStorage `miqbal_baru_draf_tutup`.
- **K6**: tujuh langkah berurut; LATIHAN tidak menulis apa pun; SUNGGUHAN hanya bila tahun sudah lewat 31 Des. Langkah 4 MENYUSUN saldo pembuka (dokumen persis `tulisSaldoPembuka`; `hppPerUnit` kemasan tidak dibulatkan) dan membandingkan 12 baris sebelum vs sesudah; KUNCI = tulis pembuka + `pengaturan/titikKas` 31 Des + `pengaturan/tutupBuku` + `tutupBukuAcara` DULU, lalu pindahkan dokumen tahun (tbDaftarKoleksi) ke koleksi **arsipTahun** per 200 (`arsipkanBerkas`, langsung ke server, bukan dihapus), lalu dibandingkan lagi dari mesin (1 Jan). "Batalkan" (sampai selesai) = `bacaArsip` + `pulihkanBerkas` + cabut pembuka + titik sebelumnya. arsipTahun sengaja TIDAK di KOLEKSI (ribuan dokumen).
- Koleksi baru: `pindahUang`, `absenKaryawan`, `slipUpah`, `tutupBukuAcara` (+ `arsipTahun` tak dimuat); aturan owner: `aturanToko/{uangKeluar, upah, pindahUang, tutupHari, tutupBuku}`. Uji `alat-uji/uji_uang_baru.py` 120 skenario / 40 kontrol positif (identitas kantong = kasPada di tiap langkah), masuk CI. Yang dilihat di peramban hanya SIMULASI cadangan 22 Sep (titik kas disetel tangan di localStorage).

## Putaran 19 (23 Sep 2026) — layar LAPORAN & DOKUMEN: Laba · Harian · Bulanan · Neraca · Dokumen · Setelan
Layar kedelapan (`layar/laporan.js` + `laporan-logika.js` + `css/laporan.css`), dibuka dari Menu (baris Laporan, pertanyaan "untung berapa" / "kaya atau tidak", cari) dan menu samping Mac. Tidak ada lagi baris Menu yang menunjuk sistem lama (tinggal rinci karcis di Jual). **Semua angka dari mesin beku yang sama** (`hitungLabaBersihRentang`, `hitungArusKasInti`, `hitungNeraca`, `kasPada`) — layar ini cuma menyusun, memberi kop, menomori, lalu mengeluarkan (dialog cetak / PDF / WhatsApp).
- **Laba** (kaca Laba sistem lama, per bulan yang dipilih): tiga keping yang tidak boleh tertukar — margin kotor · laba bersih · **diterima tunai** (= laba bersih − margin nota bon bulan itu + margin bon yang dibayar bulan itu, 39b no. 39); panel syarat per keping (cakupan omzet ber-HPP; tangga kotor → bersih dengan potongan QRIS dipisah dari biaya toko; bon yang belum jadi uang); aman diambil bulan ini = batas aman K1 − ambil pribadi; susut & selisih stok, nota rugi, nota tanpa modal (dilipat). Bulan tanpa satu catatan pun DISEBUT begitu, bukan nol.
- **Harian**: 14 hari terakhir (yang sepi tetap ada), omzet per cara bayar, batang per jam, rekap = teks yang sama dengan yang dikirim WA (kalimat `kirimRekapHarianWa` + pembayaran bon, prive, kas bersih, margin), arus kas hari itu, buku kas satu per satu (`daftarGerakanKas`), tanda sudah/belum tutup hari.
- **Bulanan**: enam batang bulan, inti bulan (omzet, HPP, laba kotor, biaya, laba bersih, uang keluar, kas bersih, tagihan bulan itu yang belum dibayar) + **DK3 rekap omzet 12 bulan**: kumulatif tahun berjalan, batang putus = belum tutup buku, bulan sebelum ada catatan = "—"; tanda **sudah dilaporkan** hanya bulan FINAL (tahun ≤ era tutup buku), membatalkan = dua ketukan; tarif perkiraan (per seribu), batas omzet, tanggal lapor = **setelan owner** (`aturanToko/rekapOmzet`, bawaan belum diatur → kolom tidak dicetak; selalu disebut "bukan nasihat pajak"); bukti omzet dari bulan pilihan (Σ = jumlah), hanya bulan final.
- **Neraca**: `hitungNeraca(sampai)` dua sisi (harta: kas · stok karung · kemasan · kantong & bahan · piutang · kasbon · aset tetap isian owner; kewajiban & modal: utang pemasok · utang ke owner · modal tertanam · **laba ditahan = aset − kewajiban − modal, DIHITUNG dan disebut begitu**); pembandingnya laba bersih kumulatif mesin − ambil pribadi, selisihnya ditulis "belum terjelaskan buku" (titik kas yang disetel ulang, stok awal sebelum sistem) — tidak disembunyikan. Pilih tanggal (mundur dari titik kas → kas tidak ditebak). Tidak dicetak bila kas belum bisa dihitung atau ada stok minus.
- **Dokumen**: **DK2** laporan berkop (laba-rugi · neraca · arus kas; 1/3/12 bulan; bulan belum tutup buku = cap **DRAF**; arus kas: kas awal sebelum titik kas = "belum bisa dihitung", kas akhir = `kasPada` = kas neraca, titik kas yang disetel ulang di dalam periode = baris penyesuaian bernama), paket bank (hanya bulan FINAL — sebelum tutup buku pertama ditolak dengan sebabnya), banding dua bulan; **DK4** dokumen kecil: bukti setoran modal (dari Owner & toko), slip upah (dari slip yang tersimpan; baris lama sistem lama tidak dirinci), kartu piutang (saldo berjalan; sisa = awal + bon − bayar − dihapus, ditolak bila ≠ mesin), rekap bon pemasok (`bukuBon`), **cetak ulang nota** = penyusun struk yang sama, cap **SALINAN ke-N** (N dari `dokumenCetak`), nota batal ditolak. Tiap keluaran = dokumen **`dokumenCetak` bernomor urut** (nomor awal = setelan owner) dengan versi kop; "simpan PDF" = dialog cetak perangkat.
- **Setelan** (DK1): kop & identitas usaha (nama · alamat wajib; telepon · NPWP 15/16 angka · NIB 13 angka · baris kaki boleh kosong; kiri/tengah) → `aturanToko/identitas` berversi + riwayat; kop ringkas ikut ke `aturanToko/struk` (nota Jual memakai kop yang sama); dokumen mana memakai kop penuh/ringkas (`aturanToko/dokumen`); nomor dokumen berikutnya; daftar setelan lain yang tinggal di layarnya (Uang keluar, Tutup hari, Upah, Pindah uang, Tutup buku, Bon pemasok, Katalog, Struk, Pelanggan, Wadah, Sistem, Barang masuk) — ketuk = pindah ke sana. Tanpa kolom PIN/sandi. Memulihkan dari berkas cadangan tetap di sistem lama (keputusan owner).
- Yang sengaja beda dari kanvas: neraca tidak pernah "tidak seimbang" secara aritmetika (laba ditahan dihitung sebagai sisa) — kejujurannya dipindah ke baris pembanding laba kumulatif + penolakan cetak saat kas/stok bermasalah; modal disetor dibaca dari catatan (tidak diketik); MDR di laba-rugi = catatan potongan QRIS dari Tutup hari (bertanda `mdr`), bukan perkiraan; printer struk tertanam belum ada (semua lewat dialog cetak perangkat).

## Putaran 20 (23 Sep 2026) — sisa sistem lama di layar Jual: RINCI KARCIS · RETUR TANPA NOTA · TUKAR YATIM
Owner memilih putaran pemantapan (memakai `/baru/` sehari penuh); yang dikerjakan selagi itu = dua sisa yang tidak membalik keputusan lama. Muat cadangan dari berkas TETAP di sistem lama (keputusan owner: dua kali cadangan, satu pintu). Tablet karyawan DITUNDA sampai perangkatnya ada.
- **Rinci karcis** (`layar/karcis-logika.js`): karcis kasir darurat (nota nominal saja dari tablet/kasir-darurat) dan nota kasir yang jumlahnya belum pasti (`perluKoreksi`) muncul sebagai pita di atas rak Jual ("N karcis kasir belum dirinci") dan baris Menu "Rinci karcis". Karcis **diikat ke keranjang** (seperti tukar): barang dipilih dari rak seperti menjual biasa, **tebakan dari katalog** sekali ketuk (literan kelipatan 0,5 L dengan toleransi bulat Rp500 → harga PAS dipasang sebagai nego; kemasan 1–6; karung 50/25 1–4; kombinasi 2–3 barang yang jumlahnya persis — `kandidatDarurat` + `kombinasiDarurat` sistem lama). SIMPAN RINCIAN = bentuk `simpanRinciTrx()`: baris {grupNota, asalDarurat, rinciDari, koreksiDari, alasanKoreksi, dirinciPada, operator}, **tanggal & jam = tanggal & jam karcis**, sisa yang belum terurai = karcis baru bertanda sama (uang masuk tidak pernah hilang), karcis asli DITANDAI `dikoreksiOleh` (tidak dihapus). Ditolak hanya KELEBIHAN (aturan owner 9 Agu), potongan nota tidak dipakai, bon wajib nama. Rapikan (`perluKoreksi`) = bentuk koreksi (koreksiDari, tanpa asalDarurat) dan harus menutup nominal PERSIS. "Hanya perbaiki cara bayar / nama" = `simpanPerbaikanDarurat` (pengganti + asli ditandai). **Tarik balik** (pita 90 detik atau daftar "rincian hari ini"): grup harus utuh; baris dibatalkan, kantong id+1 dihapus, karcis asli dipulihkan. Parkir & tukar tidak boleh bersama karcis.
- **Retur tanpa nota** (retur-logika.js, tombol "Tidak ada notanya?" di jalur Retur): cabang `simpanRetur()` tanpa nota — karung per merek & berat / kemasan per produk, jumlah diketik (karung utuh/setengah, kemasan unit), kondisi & alasan wajib, **uang kembali DIKETIK** (tidak ada nota yang menghitungkannya), tukar = selisih diketik (positif toko mengembalikan, negatif pembeli menambah; 0 boleh) dan penggantinya dijual dengan pil "pengganti retur" (model A lama). Melebihi yang pernah terjual − sudah diretur → ketukan kedua (dulu `confirm`). Dokumen = bentuk lama + kolom `tanpaNota: true`, karantina ikut bila tidak utuh.
- **Tukar yatim** (retur tukar yang penggantinya belum/kurang tercatat — `tkApakahYatim` pembantu): kartu di atas daftar nota Retur. **"catat penggantinya"** = keranjang diikat sebagai SUSULAN (`tukar.susulanReturId`, kredit 0): baris nota membawa `tukarReturId` retur yatim itu, **retur TIDAK ditulis lagi**; pembulatan susulan gabung memakai rumus `tkBulat` (atas selisih yang dulu diterima, dikurangi pembulatan yang masih menempel); tidak bisa bon / bayar sebagian; keranjang melebihi yang belum tercatat ditolak sampai "nilainya memang berubah". **"pengganti sudah tercatat"** = pilih penjualan calon (sejak tanggal retur, bukan pengganti-retur, belum dipakai retur lain, terdekat jamnya) → dokumen retur ditulis ulang dengan `penggantiDikonfirmasi {penjualanId, pada}` (sistem lama memakai transaksi Firestore; di sini tulisan biasa lewat batch — dokumen retur yang sedang dikoreksi perangkat lain di detik yang sama bisa tertimpa; disebut di sini, bukan disembunyikan).
- Menu → baris "Rinci karcis" dan gerbang Tutup buku g4 kini menunjuk Jual → Karcis. Uji: `uji_jual_baru.py` 330 skenario + 146 kontrol (13 baru: kelebihan lolos, tanda asalDarurat hilang, sisa hilang, asli tidak ditandai, tanggal baris = hari ini, rapikan bersisa, tarik balik grup tersentuh, retur melebihi terjual tanpa ketukan kedua, refund tanpa nominal, susulan menulis retur lagi, susulan BON, susulan melebihi diam-diam, pengganti tanpa tanda).

## Putaran 21 (23 Sep 2026) — PEMANTAPAN 1: sepuluh koreksi owner dari pemakaian sehari
Owner memakai `/baru/` di Mac & HP lalu memberi sepuluh catatan (+ sepuluh foto toko). Semuanya di sistem baru; sistem lama & mesin beku tidak disentuh.
1. **Menu samping Mac sempit** (72 px, ikon + monogram IQ): membuka jadi 236 px saat kursor menepi ke tepi kiri / masuk ke menu, menutup saat pergi; monogram diketuk = buka/tutup (layar sentuh lebar). Terbuka: "Toko Beras" + M.IQBAL. Isi halaman tidak bergeser (menu melayang, `body{padding-left:72px}`). Ikon SVG per layar di `index.html`.
2. Pil sumber data huruf kapital ("DATA TOKO"), salam Ringkasan "…, Owner", judul masuk "Masuk sebagai Owner". 3. **Menu** di paling bawah menu samping.
4. **Denah toko dari foto** (`stok-tempat-logika.js`): denah portrait 3 : 4 — jalan/pintu depan di BAWAH, pintu rumah di ATAS, lorong ubin di tengah, kotak `belakang · kiri/kanan belakang · kiri/kanan tengah · kiri depan (timbangan & troli) · meja · karung terbuka · pajangan kemasan · wadah literan · bangku kiri/kanan`; perabot tetap digambar (`PERABOT_DENAH`), kotak yang belum dipakai digambar samar (`kotakKosong`). Kunci kotak LAMA dipetakan (`tpPosisi`: atas→belakang, kiri-bawah→kiri depan, …) supaya setelan tersimpan tidak hilang. Belum pernah disimpan owner → `TEMPAT_BAWAAN` (9 tempat dari foto) ikut; Atur punya tombol "pakai denah bawaan dari foto toko".
5. **Deretan karung terbuka** (`deretanKarung()` jual-logika): karung 50 kg yang sudah dibuka BERJAJAR di belakang deretan wadah (urut W1..Wn, lalu karung lepas/yatim yang masih berisi). Panel isi ulang (Jual & Stok) memajang deretan itu: ketuk karung = +1 takar DARI karung itu (`tambahTakarDari`, baris takar kini `{merk, takar, dari}`); `hitungTakar` menghormati `dari` yang dipilih (tanpa `dari` = tebakan `lokasiSumber` seperti dulu) dan `susunTakarWadah` menyimpannya. Tab Wadah punya kartu "Deretan karung terbuka".
6. **Jual**: jalur Sering untuk pembeli bernama memajang **Belanja terakhir** (3 nota terakhirnya; `pembelianTerakhir`) — ketuk = **ulangi** dengan harga HARI INI, baris yang tidak ada di rak / melampaui stok dilewati & disebut (`ulangiPembelian`). Nota tercatat → "+Rp…" naik di kartu Hari ini dan omzetnya bergulir (di HP: pita di atas menyebut omzet baru; elemen di luar `<main>` supaya tidak dimorf). **Saran benang**: nama di keranjang yang tercatat "biasa datang untuk" orang lain (pelangganTitip) → pita "catat atas nama …" (`saranBenang`). Motor adegan = **matic** (skuter).
7. **Pelanggan** (*warna kulit & suku/logat DICABUT di putaran 23b*): kelompok ciri jadi 9 (siapa, umur, perawakan, warna kulit, wajah & rambut, yang dipakai, suku/logat, naik apa, beli apa; `TANYA_CIRI`) dengan 50-an cip bawaan; **sketsa** ikut ciri (warna kulit k1–k4, kumis/janggut/brewok, botak/uban/rambut panjang/keriting, kacamata/topi/cadar, gemuk/kurus = lebar bahu, tinggi/pendek = letak kepala). **Benang**: nama paku utuh (`plNamaPendek`: "Al - Yamin" tidak lagi terpotong), form "yang datang bukan orangnya" punya kotak cari & menampilkan semua nama yang cocok (bukan 40 pertama), kartu orang menyebut benangnya (`benangOrang`), urusan bawaan + "ojek / kurir langganan".
8. **Upah — hari sesudah gajian terbuka**: sistem lama menandai gaji per BULAN; gaji bulan berjalan yang dibayar tengah bulan (18 Sep) dulu menutup seluruh bulan → 19 Sep dst. terkunci "sudah termasuk upah yang dibayar". Kini `upBulanLamaTerakhir` menutup hanya sampai min(tanggal bayar, akhir bulan) → mulai = tanggal bayar + 1 (`sumberMulai 'lama'`, teks "sejak gaji terakhir dibayar 18 Sep"). Kalender 14 hari bisa diketuk lagi.
9. **Karyawan (HR)** — lembar baru di Orang & upah (chip "＋ Karyawan"): tiap orang `{nama, peran, status aktif|berhenti, masuk, berhenti, mulaiHitung, catatan}` di `aturanToko/upah.orang` (kolom lama tetap terbaca). Berhenti (Gama pensiun) = hari sesudah tanggal berhenti tidak dihitung (`hitungUpah().akhir`), absen sesudahnya ditolak, keluar dari chip aktif tapi tetap di daftar (tanda awas bila upah/kasbon belum beres); aktifkan lagi mengembalikan hitungan. `mulaiHitung`/`masuk` menaikkan tanggal mulai (tidak pernah membuka hari yang sudah dibayar). Menghapus nama yang masih punya upah/kasbon tetap ditolak. Tanpa kolom PIN/sandi. `daftarKaryawan`, `susunKaryawan`, `KOLOM_KARYAWAN`, `STATUS_KARYAWAN`.
10. **Laporan Mingguan & Tahunan** (`laporan-logika.js`): minggu toko = Senin–Minggu (`lpSenin`, `daftarMinggu` 8 minggu, `rekapMinggu`: 7 hari, Σ hari = omzet minggu, inti dari mesin laba & arus kas yang sama, banding minggu sebelumnya — tanpa pembanding ditulis apa adanya, hari ramai/sepi); tahun (`daftarTahun`, `rekapTahun`: 12 bulan, Σ bulan = tahun, laba bersih Σ bulan, DRAF sampai tutup buku, banding tahun sebelumnya). Baris Menu Mingguan & Tahunan.
- Uji: Jual 335 (+5) / 150 kontrol (+4) · Uang 125 (+5) / 43 (+3) · Laporan 65 (+5) / 30 (+3) · Pelanggan 42 (+4) / 30 (+3) · Stok 129 (+2, 2 diperbarui) / 93 (+2). Tidak ada dokumen bentuk baru selain kolom karyawan di `aturanToko/upah` dan `dari` di baris takar.

## Putaran 22 (23 Sep 2026) — PEMANTAPAN 2: empat koreksi lanjutan owner
1. **Tempat simpan**: kotak "bangku kiri pintu" = **kasir · meja owner** (foto 4687; kunci lama `bangku-kiri` & `meja` dipetakan). Tempat yang masih berisi kini BISA dilepas dari Atur dengan **ketukan kedua** (`susunAturTempat({..., yakin:true})`): barangnya jadi tanpa tempat (peta `tempatSimpan` ditulis tanpa kuncinya + `pindahTempat {tempatDihapus:true}`), stok tidak berubah — tempat coba-coba "atas" bisa dihapus owner sendiri. **Tumpukan 3D** (`susunTumpukan`, `tpIso`, tab bawaan "Tumpukan 3D" di lembar Tempat simpan): denah yang sama digambar isometrik (SVG), tiap tempat = lantai, tiap barang = tumpukan karung setinggi **rantai stok** (`tumpukanGudang().karung`: buku − karung terbuka − isi wadah; kemasan per 5 unit; paling banyak 12 lapis digambar, sisanya disebut). Ketuk tumpukan → ketuk lantai tempat lain = pindah (peta yang sama dengan denah); **‹ geser ›** = urutan di dalam tempat (`aturanToko/tempat.susunan {kunci: urut}`, `susunGeserTumpukan`); lantai putus-putus = kotak denah yang belum jadi tempat, ketuk = jadikan tempat (`susunTempatBaru`) dan langsung menaruh tumpukan yang sedang dipilih. Semuanya catatan letak — stok & modal tidak berubah.
2. **Karung terbuka bisa diatur & dikembalikan** (`susunKembalikanKarung(merk, lokasi, w, yakin)` jual-logika): di tab Wadah ketuk karung di deretan → baris aksi: **samakan sisa** (karung lepas ditandai `lepas:true`), **kembalikan ke tumpukan gudang** (ketukan kedua), buka wadahnya. Belum pernah ditakar sejak dibuka → catatan `karung` (buka) DIHAPUS (tumpukan pulih persis, papan kapur bersih); sudah ditakar / punya titik samakan → ditulis `karungIsi 0 {dikembalikan:true, sisaSebelumKg}` (sisanya kembali dihitung ke tumpukan). `karungUntukWadah` mengabaikan catatan `dikembalikan` (wadah tidak "memegang" karung yang sudah dikembalikan); karung lain yang kosong tidak tampil lagi. Juga tersedia di rincian wadah (karung di belakang) & daftar "karung terbuka lain".
3. **Pelanggan · hapus nama salah ketik** (`rincianHapusNama`, `susunHapusNama` — tautan di bawah kartu, ketukan kedua): nota-nota nama itu ditulis ulang **tanpa nama** dengan jejak `namaDihapus`/`namaDihapusPada` (rupiah tetap), kartu & benangnya dibuang. Nama yang punya buku bon / pesanan / THR / tagihan DITOLAK dihapus → SATUKAN ke nama yang benar. Batas 180 dokumen (satu batch).
4. **Bonus karyawan** (`hitungUpah(nama, kini, potong, {ketik, alasan})`, `ALASAN_BONUS`): isian Bonus + alasan di panel Bayar upah → ikut DITERIMA, masuk baris gaji bulan terakhir yang dibayar (`gaji = hari×tarif + bonus`, kolom `bonus`, `alasanBonus`) & slip ("Bonus (Rajin) +Rp…"). **Bonus tanpa hari kerja** (`susunBonus`, tombol berubah "BERI BONUS" bila tidak ada hari yang belum dibayar): baris gaji berkunci "Nama · bonus · tanggal" hari 0, `slipUpah {jenis:'bonus'}` — slip bonus TIDAK menggeser "sejak terakhir dibayar". Batas 10 jt, alasan wajib. Laba: mesin lama membaca gaji (jatah per hari), kas keluar di tanggal bayar.
- Uji: Stok 135 (+6) / 98 kontrol (+6, 1 diganti) · Uang 129 (+4) / 45 (+2) · Pelanggan 44 (+2) / 32 (+2) · Jual 335 / 150 · Laporan 65 / 30.

## Putaran 23b (23 Sep 2026 malam, PR #30) — CIP WARNA KULIT & SUKU/LOGAT DICABUT
Keputusan owner, menggantikan "serinci mungkin" putaran 21: **toko tidak mencatat suku, ras, atau warna kulit pelanggan** (usaha yang disiapkan bercabang; tidak berguna untuk usaha, berisiko hukum & nama baik). Pelanggan tetap dikenali lewat umur, perawakan, wajah & rambut, yang dipakai, naik apa, beli apa. Kelompok "Yang dipakai" TIDAK disentuh (belum diputuskan owner).
1. **Kode**: `TANYA_CIRI` tinggal 7 kelompok; 13 cip bawaan dua kelompok itu dibuang; sketsa satu nada netral (kelas `k1–k4` & CSS-nya dibuang). `GRUP_DICABUT`, `CIP_DICABUT`, `KATA_DICABUT` (per kata: kulit, suku, logat, ras, etnis, etnik, +"-nya"; "beras" tidak kena "ras"), `cipTerlarang()` (+ cip owner yang dulu ditaruh di kelompok lama, dibaca dari setelan mentah). `aturPelanggan()` & `kartuTersimpan()` menyaring → Tampah/Hafalan/Wajah/kartu tidak pernah menanyakan/menampilkannya walau masih tersimpan; `dikenali` tetap dibaca MENTAH (= KR1 sistem lama) sampai dibersihkan.
2. **Pintu ditutup**: Atur menolak kelompok `kulit`/`asal` & cip berkata terlarang atau bernama cip bawaan lama — *"Toko tidak mencatat suku, ras, atau warna kulit pelanggan."*; simpan kartu membuang cip terlarang (kartu yang disimpan ulang ikut bersih). Simpan Atur biasa MEMBAWA cip owner di kelompok lama yang masih menempel di kartu (tak tampil) supaya bukti terlarangnya tidak hilang sebelum dibersihkan. Kolom catatan kartu: keterangan tetap *"Jangan tulis suku, agama, warna kulit, atau kesehatan."*
3. **Lembar "Bersihkan ciri yang dicabut"** (di atas Atur Pelanggan, tampil hanya selama ada yang perlu dibersihkan): pratinjau `rincianBersihkanCiri` TANPA menulis (kartu, cip dibuang, yang jadi tanpa cip + yang jadi "belum dikenal" di KR1, setelan ikut atau tidak, jumlah batch); tombol mati tanpa cadangan berkas HARI INI (`cadanganCatatan`); dua ketukan → `susunBersihkanCiri` → `perbaruiKolom` (toko.js) / `perbaruiBerkas` (firebase.js): **update kolom** `cip`+`ciri` (kartu gaya lama: `ciri` saja) & `ciriDaftar` setelan — tanpa atribusi, kolom lain byte-sama; potongan 200 dokumen, setelan di potongan terakhir, SATU baris `logAktivitas` berisi jumlah saja. Teks bebas (catatan/biasa/arah) yang berkata terlarang & jejak log cuma DILAPORKAN.
- Uji: Pelanggan 57 (+13; 2 skenario P21 kulit/suku DIGANTI) / 56 kontrol (+24; "sketsa mengabaikan warna kulit" DIGANTI "sketsa membaca warna kulit lagi"); asap cadangan 23 Sep: 0 kartu terdampak, suntikan ke kartu nyata → kolom selain cip/ciri byte-sama. Layar lain tetap: Jual 335/150 · Ringkasan 35/17 · Stok 135/98 · Menu 53/32 · Harga 105/47 · Uang 129/45 · Laporan 65/30.

## Putaran 23 (24 Sep 2026) — TULANG PUNGGUNG 1: AKUN PER ORANG (PR #31 di-merge ke main 24 Sep; 23d = PR #36)
Tiap orang punya akun sendiri; hak ditegakkan di SERVER (`firestore.rules` v3), bukan di layar. Dasar semua baris: `docs/peta-hak-akses.md` (Tahap 0, dari kode). Jawaban owner 24 Sep menang atas teks prompt.
- **Masuk** (`data/akses.js` = logika tanpa DOM, `firebase.js` = sambungan): email + sandi (sandi readonly sampai diketuk, email terakhir bisa dilupakan); owner lewat EMAIL; akun lain lewat `aksesAkun/{uid}` yang didengarkan terus (nonaktif = cabut semua pendengar & kosongkan angka); tanpa `aksesAkun` = nol pendengar + "Minta didaftarkan" (`permintaanAkses/{uid}`); kasir@ tidak bisa masuk sebagai orang. Akun yang masuk tampil di **pil kepala setiap layar** ("OWNER" / nama orang, + "tanpa internet" / "N belum terkirim"); ketuk pil = lembar "Masuk sebagai" + Keluar (owner 24 Sep: bilah di atas layar dicabut, dulu menutupi logo; Keluar lewat satu ketukan di pil DITERIMA owner, putaran tablet boleh meninjau ulang). Nama yang masuk SELALU di depan pil — juga saat memuat. Tirai menutup lembar akun (app.js + CSS) dan pil ikut kosong bersama `<main>`. Keluar menanyakan keranjang lalu catatan yang belum terkirim.
- **Atribusi**: penulis pusat menulis `olehUid`/`diubahOlehUid` (owner tetap `oleh:'Owner'`); bukan-owner diperiksa SEBELUM dikirim (`periksaKiriman` = peta), tanpa hapus/bersihkan/arsip, pencipta tak pernah ditambah pada update; SATU baris jejak per kiriman bukan-owner berisi daftar dokumennya; kiriman > 18 access call ditolak di perangkat (batas Firebase 20, sisa 2).
- **Salinan antre** (`data/antre-lokal.js`): tiap kiriman disalin di perangkat sampai server mengaku; ditolak → Menu › Sistem › Perangkat › Antrean "ditolak server" (owner: tulis ulang atas namanya / buang).
- **Layar** (tipis): pendengar per peran (koleksi utuh + `aturanToko`/`pengaturan` per dokumen); bukan-owner cuma Jual · Pelanggan · Stok · Menu kecil; tombol kedatangan/cocokkan/kantong/tempat/HPP/Bon(karyawan) mati berkalimat; SS2 kartu Permintaan akses & Akun terdaftar + kalimat "Server menegakkan …".
- **Rules v3**: blok per koleksi; `owner()` email; `kasir()` email (v2 membuka jalur kasir untuk siapa pun yang login — dipersempit); bukan-owner create dengan `jujur()` + 2 update terbatas kolom; `firestore.rules.v2` untuk mundur. Uji server: `docs/uji-rules-v3.md` (Playground + proyek Firebase kedua lewat `?pasangProyekUji=` — bilah merah PROYEK UJI).
- Tertutup walau kisi bilang `sendiri`: hitung laci (menimpa angka uang tercatat) & kedatangan (wajib harga beli). Utang: id peran `ben` = nama orang.
- **Tirai (23c, owner 24 Sep)**: selama belum masuk, atau akun belum disetujui / nonaktif / kasir@, layar di belakang formulir Masuk KOSONG — `inti/kunci.js`
  (bawaan terkunci sampai Firebase menjawab), tiap layar memeriksa `terkunci()` sebelum menggambar, `app.js` mengosongkan setiap `<main>` saat menutup dan
  menyembunyikan nav & menu samping. Sebelumnya beranda menggambar "kas tercatat" dari penyimpanan lokal peramban (titik kas) sebelum siapa pun masuk.
  Diuji di Chrome headless sungguhan: `alat-uji/uji_layar_kunci.py` (+ `--kontrol`: mode cadangan terlihat; tirai dirusak / beranda tanpa penjaga → berbunyi).
- **Ganti orang (23c, owner 24 Sep)**: keranjang Jual TIDAK terbawa ke akun berikutnya. Keluar dengan keranjang berisi (termasuk yang diparkir) → ditanya
  "Keranjang berisi N baris belum disimpan — simpan atau kosongkan?" — *Simpan dulu* = batal keluar, kembali ke keranjang; *Kosongkan lalu keluar* = keranjang,
  parkir, nama pembeli, retur tukar & karcis dilupakan (`jual-logika.keadaanOrangBerikutnya`, stok yang dipegang ikut dilepas). Keluar dari tempat lain (tab lain,
  sesi dicabut) atau akun berbeda yang masuk = dilupakan TANPA ditanya (`app.js jagaIsian`, sejak 23d juga akun nonaktif / belum disetujui). Diuji di Chrome dengan Firebase PALSU lokal (`uji_layar_kunci.py` bagian 2: firebase.js/akses.js/app.js asli, masuk-keluar
  digerakkan skrip uji tanpa sandi): owner → akun lain, tab lain, dan akun yang dinonaktifkan saat bekerja tanpa internet (tirai: 0 rupiah, nama & status
  jaringan tidak terlihat). Firebase dari CDN gagal dimuat → dicoba ulang satu kali, lalu keluaran berkata **GAGAL JARINGAN** (keluar 4), beda dari **GAGAL UJI**
  (keluar 2). Catatan harness: server uji lokal wajib antrean sambungan lebar (bawaan 5 → modul lokal ditolak acak, dulu tampak "DOM dicetak terlalu dini").
- **Semua isian lokal (23d, owner 24 Sep)**: pola keranjang berlaku untuk SEMUA isian yang belum disimpan di kedelapan layar — `inti/isian.js pasangIsian` di tiap
  layar: `belum()` = kunci keadaan yang beda dari awal atau draf lokal di localStorage, `lupakan()` = draf lokal dihapus lalu SELURUH keadaan layar kembali ke awal.
  Isian per layar: Jual (keranjang + parkir, pesanan diketik, retur, repack, setelan struk/wadah terbuka, karcis) · Stok (draf barang masuk / cocokkan / adukan di
  localStorage, kantong, karung, wadah, karantina, tempat, HPP, lembar atur) · Pelanggan (kartu pengenal, orang baru, gabung, bayar bon, hapus buku, beri THR, titip,
  lembar atur) · Harga (harga diketik, bayar bon, bon lama, kartu pemasok, lembar atur, draf belanja di localStorage) · Uang (uang keluar, bayar/tolak tagihan,
  kasbon, bonus, aturan upah & karyawan, owner & toko, pindah uang, tutup hari + draf hari ini di localStorage, langkah & paraf tutup buku) · Laporan (identitas
  usaha, profil pajak, setoran, omzet luar, lembar atur) · Menu (pindah stok, alasan, catatan, pilihan peran akun, nama perangkat, lembar atur) · Beranda: TIDAK
  punya isian. Keluar lewat pil = SATU pertanyaan "Ada isian belum disimpan di: Jual (keranjang N baris), Stok, … — kembali untuk menyimpan, atau kosongkan
  semua?" (cuma keranjang → kalimat keranjang 23c). Tab lain / sesi dicabut / akun nonaktif / akun lain = dikosongkan tanpa ditanya. **Tidak disentuh**: draf di
  SERVER milik toko — `aturanToko/hargaDraf` (draf katalog harga); juga salinan antre kiriman yang belum terkirim (milik akun itu, terkirim saat ia masuk lagi),
  email terakhir, navigasi, skor kuis hafalan, titik kas. Pencarian & saringan (`BUKAN_ISIAN`) ikut dikosongkan tapi tidak ditanyakan. Diuji: `uji_layar_kunci.py`
  bagian ISIAN (Chrome, Firebase palsu yang menyajikan `hargaDraf` & mencatat tiap tulisan; satu kontrol per layar) + `uji_isian_lokal.py` (statis: tiap kolom
  ketik & tiap kunci localStorage layar wajib dijaga atau tercatat sengaja bukan isian).

### Putaran 23e (25 Sep 2026, PR #37) — payung rules tidak boleh mengalahkan batasan owner
- Playground ★10 (owner membuat `aksesAkun` berperan `owner`) **LOLOS** di v3 58 blok: Firestore memberi akses kalau SALAH SATU blok yang cocok
  mengizinkan, dan payung `match /{document=**} { allow read, write: if owner(); }` mencakup semua dokumen — batasan owner di blok atas kalah.
  Pemeriksa statis tidak menangkapnya (memeriksa bentuk, bukan perilaku). Rules belum diterbitkan.
- Tambalan: payung jadi `match /{koleksi}/{sisa=**} { allow read, write: if owner() && !(koleksi in ['aksesAkun', 'permintaanAkses']); }`.
  Hanya dua blok itu yang membatasi owner (create/update); tulisan owner dari aplikasi ke keduanya tetap memenuhi batasannya (`aksesAkun` selalu
  uid = id dokumen, peran ben/karyawan, `aktif` boolean; `permintaanAkses` cuma dibaca & dihapus owner). Ke-32 koleksi yang dipakai `index.html`
  punya blok sendiri — tidak ada yang bergantung pada payung.
- `periksa_rules.py` menghitung sendiri blok yang membatasi owner (operasi get/list/create/update/delete yang tidak diberikan ke `owner()` tanpa
  syarat) dan GAGAL kalau blok itu masih tercakup payung; juga gagal kalau payung mengecualikan koleksi tanpa blok (owner terkunci), atau ada
  wildcard koleksi lain. Kontrol: payung lama dikembalikan → gagal.
- **Putaran 25 (kunci periode): payung DIHAPUS**, bukan sekadar dikecualikan — kunci periode membatasi owner di koleksi uang/stok; tiap koleksi
  wajib blok sendiri (catatan di kepala `firestore.rules`).

### Putaran 23c (24 Sep 2026, PR #33) — urutan pasang dipecah, kiriman bersisa 2, kisi = kebenaran server
- **Owner tidak masuk /baru/ di tablet bersama sampai cache dibersihkan saat Keluar.** (Keluar sekarang menutup layar & pendengar, tapi data yang
  sudah diunduh Firestore tetap di IndexedDB perangkat itu.)
- **Urutan pasang** (kepala `firestore.rules`, `docs/uji-rules-v3.md`): SEKARANG = Playground ★ dengan v3 di editor proyek toko → tempel v3 → satu
  nota kasir darurat masuk. GERBANG TABLET (sebelum akun bukan-owner pertama disetujui) = proyek Firebase kedua, harga beli/modal tidak terkirim ke
  staf (7 koleksi — `docs/peta-hak-akses.md` §8, termasuk siapa yang mengisi HPP nota staf), cache dibersihkan saat Keluar, jaga CI ≤ 18 hijau,
  akun dibuat di Console dengan **email huruf kecil semua**, lalu disetujui.
- **Kiriman bukan-owner ≤ 18 access call**: satu nota paling banyak **7 baris**, satu adukan **8 hasil** (kalimat jelas di layar; owner tanpa batas);
  pagar umum penulis pusat 18; rules `stafJejak` ≤ 17 dokumen. Terburuk per jenis kiriman dihitung dari fungsi asli: `alat-uji/peta_akses.py --kiriman`.
- **Kisi SS2** menggambar yang ditegakkan server: kisi `sendiri` yang ditutup rules tampil **"tertutup server"** + sebabnya (hitung laci Ben,
  kedatangan Ben & karyawan); "minta owner" menyebut alurnya belum ada. Nilai kisi tersimpan tidak berubah.

## Putaran 24 (24 Sep 2026, PR #35) — MODUL PAJAK
Sistem tahu posisi pajaknya sendiri: menghitung, mengingatkan, menyimpan bukti. Tidak membayar, tidak melapor, tidak memberi nasihat. Semua angka berlabel
**"perkiraan — bukan nasihat pajak"**. Logika `js/layar/pajak-logika.js` (tanpa DOM, `alat-uji/uji_pajak_baru.py`); sumber aturan & tanggal lihat: `docs/sumber-aturan-pajak.md`. Khusus owner.
- **Profil** = field tambahan di `aturanToko/rekapOmzet` (`wpAtasNama`, `jenisWp`, `statusPkp`, `statusPasangan`, `tahunMulaiTarifFinal`, `omzetTahunLalu`, `batasBebas`, `sumberAturan`).
  **Semua** penulis dokumen itu (DK3 atur & tandai lapor, profil, tombol aturan) lewat `pjGabungRekap`: dokumen lama disalin utuh, termasuk field yang tidak dikenal penulisnya.
  Jenis WP bawaan "belum diketahui" → layar menyebut "hitungan dengan anggapan orang pribadi". Aturan tidak terisi otomatis: tombol "Pakai aturan PP 55/2022 jo. PP 20/2026".
- **`batasOmzet` = batas atas Rp4,8 miliar.** Tidak ada field `batasAtas` terpisah: `batasOmzet` (DK3, putaran 19) sudah bermakna "batas omzet setahun" dan dibaca/ditulis
  penulis lama. Dua field bermakna sama akan berbeda diam-diam. `batasBebas` (Rp500 juta) maknanya lain, jadi field sendiri.
- **Omzet di luar sistem** (`pajakOmzetLuar/{YYYY-MM|sumber}`): `catatanLama` (bulan sebelum sistem; ditolak di bulan yang punya penjualan; bulan pertama sistem hanya
  untuk tanggal sebelum nota pertama, keterangan wajib), `usahaLain` (usaha lain WP yang sama: ikut PPh & ambang), `usahaPasangan` (ikut menurut **`statusPasangan`**, lihat
  bawah). Kosong ≠ nol: bulan tanpa
  isian tampil "—" dan kumulatif berlabel "N bulan belum diisi — kumulatif kurang dari sebenarnya".
- **PPh per bulan**: `kena = max(0, kum_sesudah − max(kum_sebelum, batasBebas))`, `pph = ⌊kena × tarif / 1000⌋` (pembulatan ke bawah [BELUM TERVERIFIKASI]). Badan → "tidak
  dihitung — tanyakan konsultan". DK3 memakai hitungan yang sama (`rekapOmzet` → `pjTahun`), omzet sistem dari `pjOmzetSistem` = mesin laba.
- **Setoran** (`pajakSetoran`): boleh untuk bulan yang belum final; memotret omzet & perkiraan saat dicatat → kalau omzet bulan itu berubah sesudahnya (koreksi, retur, rinci
  karcis), statusnya "angka berubah sejak disetor: ±Rp…". Dicatat mundur > 7 hari atau tanpa NTPN → catatan wajib. NTPN salah bentuk → peringatan saja.
- **Tanda lapor DK3 vs setoran**: tanda "sudah dilaporkan" (Bulanan) tetap ada dan tetap hanya untuk bulan final. Untuk bulan yang punya setoran, status di layar Pajak
  diambil dari setoran — setoran bervalidasi NTPN dianggap SPT Masa (PMK 164/2023 Pasal 7 ayat 5), jadi setoran adalah buktinya; tanda DK3 = catatan owner untuk bulan final.
- **Status per bulan**: nihil · terutang · disetor · kurang/lebih setor · lewat tempo (tanggal setor = `tanggalLapor`, bawaan 15) · data belum lengkap · angka berubah sejak disetor.
  Ambang atas: 70/85/95/100 % dari kumulatif gabung + proyeksi akhir tahun [PERKIRAAN]. Beranda › Perlu perhatian: satu baris (owner). Pengingat jenis `pajak`, H-3.
- **Tidak ada NIK, NPWP, atau nomor rekening** di dokumen modul ini: teks bebas dengan deretan ≥ 10 angka (selain rupiah bertitik ribuan) ditolak.
- **Status pasangan** (owner 24 Sep; `pjAturanPasangan`): PMK 164/2023 Pasal 6 ayat (5), teks dibaca — batas Rp500 juta masing-masing HANYA untuk pisah harta tertulis
  (`pisahHarta`) & istri memilih sendiri (`memilihTerpisah`); Lampiran contoh 4 = MT. Usaha pasangan PH/MT hanya ikut ambang Rp4,8 miliar (omzet suami-istri digabung,
  termasuk PH/MT — PP 20/2026 Pasal 58 ayat 2–3, artikel DJP 8 Jun 2026). `satuKesatuan` = ikut PPh & SATU batas Rp500 juta (dasar UU PPh Pasal 8 ayat 1 belum dibaca
  langsung → [BELUM TERVERIFIKASI] di layar & cetakan). `belumDiketahui` (bawaan) = anggapan paling hati-hati: satu batas berdua.
- **Dua angka omzet untuk konsultan** (owner 24 Sep): per bulan omzet mesin (dasar perkiraan PPh, sesudah potongan nota & retur) DAN omzet sebelum potongan nota
  (`pjPotonganBulan`: + `potonganTransaksi` + tawar di bawah harga daftar lewat rasio `hargaAsliSatuan` / harga jadi — satuan harga beda per jalur; tawar ke atas, nota batal,
  pengganti retur tidak ikut). Tampilan saja, mesin beku tidak disentuh. Cetakan menulis: angka mana yang dipakai **diserahkan ke konsultan**.
- **NPWP di identitas usaha DK1** (owner 24 Sep): kolom tetap ada, **bawaan TIDAK dicetak di kop mana pun** (`npwpDiKop`, sakelar di Laporan › Setelan; kalau dinyalakan,
  hanya kop penuh). NPWP 16 angka → peringatan "NPWP orang pribadi = NIK; mencetaknya membuka NIK ke semua pembeli." 

## Putaran 25 (25 Sep 2026) — TULANG PUNGGUNG 3: KUNCI PERIODE BULANAN (PR #40 di-merge ke main 25 Sep)

Sesudah owner mengunci bulan M, tidak seorang pun (termasuk owner, sistem lama, kasir darurat, tablet offline) bisa menambah, mengubah, atau menghapus
catatan bertanggal di bulan M. Kesalahan yang ketahuan belakangan dibetulkan dengan catatan HARI INI (retur, cocokkan, bayar bon); catatan lama tidak disentuh.
Peta & keputusan owner K1–K6: `docs/peta-kunci-periode.md`. Uji server: `docs/uji-rules-v4.md`.

- **Dokumen kunci** `aturanToko/kunciPeriode` `{ sampaiBulan, riwayat }` + setelan `aturanToko/kunciAtur` `{ tenggang }`. Inti tanpa impor: `js/data/kunci-periode.js`
  (bulan WIB, koleksi bertanggal = rules v4, hitungan get() server, pemecah kiriman). Layar: `js/layar/kunci-periode-logika.js` + kartu **Kunci bulan** di
  Uang › Tutup buku; satu baris di Beranda › Perlu perhatian (diam selama kunci belum bisa dipakai).
- **Daftar periksa** (⛔ memblokir): putaran 25b · tenggang · catatan tertahan/ditolak di perangkat ini · nota parkir · perangkat antre > 0 · perangkat tanpa
  denyut 24 jam (bisa dinyatakan "sudah tidak dipakai" kalau antre & ditolaknya 0). Dicentang owner: hari tanpa tutup hari (libur hanya hari tanpa nota;
  "diterima apa adanya" wajib alasan — tutup hari TIDAK dibuat mundur), karcis belum dirinci, omzet luar, periksa ulang pembelian (K2), nama mirip berbon (K3),
  upah (K5). **`KP_SIAP_25B`**: kunci PERTAMA menunggu putaran 25b — sejak 25b `true` (kasir memisahkan catatan ditolak, sistem lama hanya-baca).
- **Penjaga pusat** (`toko.js jagaKunci`): SEMUA tulisan layar — bulan terkunci atau > 18 pemeriksaan kunci = tidak dikirim, dengan kalimat. Jalur besar
  bertahap (`tulisBertahap`, rencana tersimpan di perangkat, dilanjutkan dari Menu › Sistem › Perangkat): SATUKAN, hapus nama, tarik balik rincian, koreksi/hapus adukan.
- **Pembalik**: tombol koreksi/hapus untuk catatan bulan terkunci berganti "Bulan X terkunci — cocokkan / buat retur hari ini" dan membuka alur lama dengan
  barang asalnya. Hapus + dokumen kini SATU kiriman di semua layar (dulu dua kiriman, hasil kedua tidak diperiksa). Hapus di Laporan › Pajak dulu diabaikan — ditambal.
- **Final bulanan**: `lpFinal` = era ATAU bulan ≤ sampaiBulan; `lpTahunFinal` = era ATAU 12 bulan terkunci. Pajak: keadaan terkunci per bulan, peringatan
  setoran untuk bulan yang belum dikunci. `pajakSetoran` & `pajakOmzetLuar` tidak dikunci (K6); ubah/hapusnya menulis jejak dengan nilai lama.
- **Rules v4** (`firestore.rules`; v3 utuh di `firestore.rules.v3`): payung owner dihapus; bulan WIB dari `request.time`; **tenggang minimal 3 hari**
  ditegakkan server (bulan M dikunci paling cepat tanggal 4 bulan M+1; tanggal 1–3 catatan bulan lalu tanpa get()); owner 1 get() per operasi bulan
  lampau; kasir@ create dinilai sama dengan owner (update hanya tulis-ulang identik, tidak pernah hapus, 1 dokumen per permintaan); bukan-owner tanpa
  get() kunci (hanya bulan berjalan / tenggang).
- **Tutup buku tahunan (K1) — rancang ulang WAJIB selesai sebelum Desember 2026**: sungguhan ditolak selama tahunnya punya bulan terkunci, DAN (diukur)
  saldo pembukanya > 18 pemeriksaan kunci (pembuka piutang = tanggal utang tertua, bon pemasok = tanggal bon; cadangan toko 25 Sep: 24) → ditolak di layar
  sebelum dikirim. Rancangan baru: arsip = salinan + penanda, tidak menghapus; catatan dasar 10 tahun; tiap kiriman ≤ 18. **Bagian "tiap kiriman ≤ 18"
  SELESAI di "Tutup buku bertahap" (bawah)**; penolakan selama ada bulan terkunci di tahun itu (arsip yang menghapus) TETAP — keputusan owner.

## Putaran 25b — antrean kasir tidak macet, batal karcis darurat (26 Sep 2026, PR #41)

- **Kasir darurat & kasir.html (sw-kasir v26)**: jawaban server dipilah tiga — 401 = layar masuk; 403 dengan kunci masuk = DITOLAK ATURAN (mis. bulan
  terkunci) → daftar "ditolak" di HP itu (`darurat_gagal_v1` / `kasir_gagal_v1`), tidak diulang, tidak dihapus, catatan sesudahnya tetap terkirim;
  sinyal / 429 / 5xx = tetap antre. Pita merah + daftar tanggal/jam/nominal; "sudah dicatat ulang" = dua ketukan, pindah ke arsip HP. Denyut: antrean,
  `gagal` (= ditolak), `versi` = VERSI sw-kasir.js. Versi tampil di bilah atas ("versi 25b").
- **Beranda › Perlu perhatian** (owner): HP kasir yang antre / punya catatan ditolak / masih versi < `KP_VERSI_KASIR_25B` (`kpPerhatianPerangkat`).
  **Daftar periksa kunci bulan** ⛔ baru: semua perangkat kasir yang berdenyut 7 hari terakhir sudah versi 25b (nama perangkat disebut).
- **Batal karcis kasir darurat** (Jual › pita karcis › lembar Karcis kasir › *batalkan*, alasan wajib): bentuk = `mulaiBatalkanTrx` sistem lama
  (`karcis-logika.js susunBatalKarcis`). Dijaga `alat-uji/uji_batal_karcis.py`.
- **Sistem lama HANYA-BACA** (keputusan owner 26 Sep, `docs/peta-pensiun-sistem-lama.md` §5–§6): satu penjaga `penjagaTulis()` di `index.html`;
  terbuka hanya setelan jenis beras, operator & PIN kasir, PIN owner, dan pulihkan cadangan lewat ketik PULIHKAN (`docs/prosedur-pulih-darurat.md`).
  Katalog kasir (`ringkasanKasir`) tetap diterbitkan sistem lama — `/baru/` belum punya penerbitnya (putaran tersendiri, bersama pindahan setelan). **25c: sudah pindah — lihat di bawah.**
  Antrean lama dikirim sekali; yang ditolak ke daftar "ditolak" di pita. **`KP_SIAP_25B = true`**.
- **Bayar bon dari bulan terkunci LOLOS** (rules v4 menilai `bonTanggal` hanya untuk bon lama BARU): `alat-uji/uji_bayar_bon_terkunci.py` + Playground
  ★D di `docs/uji-rules-v4.md`.

## Putaran 25c — pindahan terakhir: katalog kasir, jenis beras, operator & PIN (27 Sep 2026, PR #45)

Peta & keputusan owner: `docs/peta-pindahan-terakhir.md`. Sesudah ini tidak ada pekerjaan harian yang butuh sistem lama; di sana tinggal baca riwayat &
pulihkan dari berkas cadangan.
- **Katalog kasir** (`ringkasanKasir/aktif`, bentuk TETAP — keputusan owner): `data/katalog-kasir.js` (kk). Isi = `susunIsiKatalogKasir` VERBATIM
  (pindah_mesin.py); diterbitkan `firebase.js` 4 detik sesudah tiap perubahan data, hanya kalau isinya beda dari dokumen server, hanya dari perangkat owner
  yang semua koleksinya sudah dijawab server (bukan salinan perangkat); terbit harga menyertakannya di writeBatch yang sama (`kkSertakan`); ditulis apa
  adanya tanpa atribusi/jejak (`kkMentah`, seperti index.html). Beranda: "Katalog kasir: diperbarui …" + Perlu perhatian (belum sampai / gagal terbit /
  HP kasir masih v26 / HP penjaga masih memegang katalog lama menurut denyut `katalog`). Modal & daftar bon tetap ikut ke akun kasir sampai putaran tablet.
- **Kasir darurat v27** (izin owner): ambil katalog saat layar dinyalakan & tiap 5 menit (jadwal denyut); denyut membawa `katalog`. `KK_VERSI_KASIR_TERBARU`
  = VERSI sw-kasir.js; `KP_VERSI_KASIR_25B` tetap kasir-v26 (lantai kunci bulan).
- **Jenis beras**: `layar/jenis-beras-logika.js` (jb). `ambilPetaJenisBeras()` = dokumen `pengaturan/jenisBeras` dulu. Harga (pil jenis di papan owner,
  lembar pilih/ketik/kosongkan, daftar "Jenis beras · N/M terisi"), Stok › Gudang (kartu per jenis), Jual (baris saring rak; urutan rak tetap).
- **Operator & PIN**: `layar/akses-kasir-logika.js` (op), tab **Kasir & PIN** di Menu › Peran & persetujuan. Dokumen `pengaturan/aksesKasir` ditulis
  TANPA `pin` (owner: PIN operator dicabut); "Cabut PIN operator" tampil selama masih ada PIN tersimpan. PIN owner `pengaturan/keamanan` { garam, acak }
  (acakPin verbatim).
- Uji: `uji_katalog_kasir.py` (statis + jsc + Chrome), `uji_setelan_jenis_beras.py`, `uji_operator_pin.py` (+ kontrol, CI).

## Putaran 27 — stok & merek (27 Sep 2026, PR #46)

Peta Tahap 0 & keputusan owner: `docs/peta-stok-merek.md` (§13 = keputusan 27 Sep). Tanpa koleksi baru, rules v4 tidak berubah, mesin beku tidak disentuh.
- **Bagian 1 — Cocokkan dipisah** (`stok-catat-logika.js`, `wadah-bernama-logika.js`): tab **Tumpukan gudang** (karung utuh 50/25 + lepas; selisih × modal)
  dan **Wadah literan** (isi per wadah dalam takar/liter/kg + karung terbuka di belakangnya; selisih dibagi ke MEREK ASAL menurut komposisi; susut
  ≤ batas owner `susutWajarKg` × hari tanpa alasan, di atasnya alasan wajib; isi ulang yang lupa dicatat ditawarkan dicatat). Buku tetap lewat
  `penyesuaianStok` (kolom `bagian: 'tumpukan' | 'wadah'`); Papan Kapur menulis dua kejadian berbeda.
- **Bagian 2 — Varian merek per belanja** (`varian-logika.js`): harga beli beda > `aturanToko/catatStok.batasVarian` (bawaan 5 %) dari modal berjalan →
  "Sama barangnya / Beda mutu"; beda mutu = nama sendiri "Merek · Mutu" (jenis beras ikut induk, usul harga = modal + target); varian juga bisa dibuat
  dari Harga & Pemasok. Kolam lama tidak disentuh.
- **Bagian 3 — Arsip produk** (`arsip-logika.js`, dokumen `aturanToko/produkArsip`): nama/kemasan yang habis → Isi / Arsipkan / Hapus (hapus hanya kalau
  tidak pernah bertransaksi). Arsip hilang dari rak Jual, katalog harga, label, dan katalog HP kasir (`kkIsi` = `susunIsiKatalogKasir` lalu disaring —
  fungsi salinannya tidak diubah); riwayat & laporan tetap. Harga › Produk arsip untuk memulihkan; barang masuk atas nama arsip bertanya pulihkan / varian.
- **Bagian 4 — ½ karung** (`setengah-logika.js`): kemasan 50 kg hasil campuran → "jual ½ (25 kg)"; buku lewat jalur pemecah Adukan (1 × 50 → 2 × 25) di
  kiriman yang sama dengan notanya (putaran 28b: juga saat merinci karcis kasir — pemecah bertanggal & berjam karcis, tarik balik rincian mencabutnya); harga 25 kg = katalog, belum ada → usul ½ harga 50 kg dibulatkan ke atas ke Rp100 (owner boleh ubah, ikut disimpan).
- **Bagian 5 — Wadah bernama** (`wadah-bernama-logika.js`): wadah = tempat bernama, harga per liter melekat pada wadah. Literan wadah dipecah jadi baris
  internal per merek asal menurut komposisi isi (`pecahItemsWadah`: `dariWadah`, `takaranId`; nama tampil = wadah; kantong di baris pertama); struk,
  Hari ini, Sering & Papan Kapur menggabung (`gabungTakaran`). HPP = rata-rata tertimbang isi. Takar bertanda `bukuAsal` (tidak lagi pindah buku —
  menggantikan Putaran 10). Katalog: baris liter hanya wadah + merek **literan langsung** (aturan wadah `literanLangsung`, terbaca karyawan);
  tab **Literan** (harga liter yang tidak dipakai bisa DIHAPUS di sana: dokumen katalognya saja, riwayat terbit & nota tetap). Barang masuk & varian menolak nama wadah/kelas kecuali `merekKarung` (Aturan wadah). Ganti nama wadah membawa isi, karung terbuka &
  harga liter. Peralihan: isi & baris lama tanpa komposisi tetap milik nama wadahnya (nama lama dijual sampai habis, lalu diarsipkan).
- Uji: `uji_cocokkan_terpisah.py`, `uji_varian_merek.py`, `uji_arsip_produk.py`, `uji_setengah_karung.py`, `uji_wadah_bernama.py` (+ kontrol, CI).

## Putaran 28 — wadah punya stok sendiri (28 Sep 2026, PR #47 dan #48 di-merge ke main)

Keputusan owner 28 Sep & rinciannya: `docs/peta-stok-merek.md` §14. Tanpa koleksi baru, rules v4 tidak berubah, mesin beku & kasir*.html tidak disentuh.
- Tiap wadah punya **buku sendiri** `'Wadah <nama>'` (data/toko.js `kunciStokWadah` / `petaStokWadah` / `stokMerekSaja`), lahir lewat satu baris batch
  `stokAwal` 0 kg (`lahirBuku`) — mesin beku hanya memotong nama yang lahir lewat batch. Takar = pindah buku karung → wadah (modal ikut); literan
  memotong buku wadah saja; cocokkan wadah = susut wadah; ganti nama membawa stok; atur susunan menolak melepas wadah berstok.
- **Pindahan awal** (Stok › Wadah literan, dua ketukan, owner): isi tercatat → buku wadah; nilai stok, laba, tumpukan tidak berubah.
- **Tiga pintu** karung di belakang wadah: tumpukan gudang · baru datang dari pemasok · kemasan jadi hasil adukan (`susunBukaKemasan` → buku sendiri
  `'Adukan <nama> <ukuran> kg'`, tidak dicampur ke buku merek pemasok).
- **Karung wadah** `'Karung wadah <nama>'`: sisihkan saat tutup toko (bawaan 10 kg, Aturan wadah), tuang balik saat buka, bongkar setahun sekali (ditimbang;
  selisih = susut wadah). Rincian wadah di Stok › Wadah literan.
- Katalog HP kasir: buku wadah berharga liter wadahnya (`wbSaringKatalogKasir` di `kkIsi`).
- **Buku per ukuran**: karung 25 kg merek yang datang dua ukuran → buku `'Merek 25 kg'` (barang masuk otomatis, `indukUkuran`); stok lama dipisah di
  Stok › Cocokkan › Tumpukan gudang dengan hitungan karung 25 kg utuh. Harga karung 25 kg = katalog merek induk.
- Buku wadah tidak tampil di daftar merek mana pun (rak karung/repack, gudang, harga karung, barang masuk, cocokkan tumpukan, adukan, tempat, belanja, HPP).
- Uji: `uji_wadah_stok_sendiri.py` (+ kontrol, CI).

## Putaran 29 — uang: biaya karyawan, upah per orang, bayar pemasok lewat transfer (28 Sep 2026, PR #49 di-merge ke main)

Permintaan owner 27 Sep: tahu berapa laba kotor yang habis untuk keperluan toko dan berapa untuk para karyawan. Peta Tahap 0: `docs/peta-uang-karyawan.md`.
Tanpa koleksi baru, tanpa dokumen per orang, rules v4 tidak berubah, 28 mesin beku & `index.html`/`kasir*.html` tidak disentuh; yang baru hanya KOLOM di dokumen yang sudah ada (§7 peta).
- **Tiga tujuan uang keluar** (K1): Untuk toko · Untuk karyawan · Untuk pribadi. "Untuk karyawan" (kopi, rokok, makanan jadi dari warung) = kolom baru `untuk: 'karyawan'` di
  `pengeluaranHarian`, kategorinya TETAP `toko`/`tokoDompet` → laba bersih turun sama seperti biaya toko; bahan mentah untuk memasak makan karyawan = toko. Pribadi tetap bentuk lama.
  Semua penulis otomatis (biaya admin K4/H2, MDR Tutup hari, tagihan tambahan, titipan tablet) menulis `untuk: 'toko'`. Catatan lama tanpa `untuk` = **belum dipilah** (dihitung di
  biaya toko, jumlahnya disebut; tidak ada pemilah ulang). Atur: `perluKaryawan` + tombol "→" memindahkan keperluan antar tujuan; satu nama tidak boleh di toko DAN karyawan.
- **Upah per orang** (K2, lembar Karyawan): `aturanToko/upah.orang[].upah[] = [{mulai, satuan hari|minggu|bulan, tarif}]` di dokumen bersama yang sama. Tarif per hari suatu
  tanggal = entri terbaru yang `mulai ≤ tanggal` (`tarifHariPada`); tanpa entri → `tarif` bersama (bawaan). Minggu ÷ 7, bulan ÷ jumlah hari bulan itu, dibulatkan ke rupiah dulu;
  setengah hari = separuh dibulatkan (`upNilaiHari`). `hitungUpah` membaca tarif PER HARI → gajian yang melintasi tanggal berlaku membayar dua tarif; `rincianTarif` per ruas
  masuk slip (teks & dokumen `slipUpah.rincianTarif`, `satuan`); baris gaji per bulan = Σ rupiah per hari. Slip lama tidak berubah. Entri tanpa tanggal / tarif 0 / satuan asing /
  dua entri bertanggal sama DITOLAK.
- **Laba kotor → ke mana** (Laporan › Laba & Bulanan, `keManaLabaKotor`): laba kotor → biaya toko (harian bukan-karyawan + jatah tagihan bulanan; di dalamnya potongan QRIS &
  biaya bank disebut) → biaya karyawan · upah (jatah gaji KOTOR) → biaya karyawan · di luar upah → hapus buku → susut & selisih stok (mesin menaruhnya di BAWAH laba kotor) →
  = laba bersih mesin → ambil pribadi owner (`priveRentang`: prive laci + kasbon dialihkan + tarik modal) → sisa. Dipilah lewat `pilahHarian` (uang-logika); wajib MENUTUP
  (kalau tidak, kartu menulis "TIDAK MENUTUP — laporkan"). Bulan terkunci/tutup buku = FINAL; bulan tanpa catatan disebut.
- **Bayar bon pemasok tunai / transfer** (H2): cara bayar dibaca dari `dari` (rekening = transfer; `caraDari`), tanpa kolom baru di `utangPemasokMutasi`. `hitungBayar(d, kini, S)`
  / `susunBayar(d, w, S)` menerima `saldoKantong()` dari layar (supaya modul bon tidak mengimpor balik uang-logika) dan menjaga isi kantong yang dipilih; tanpa S = total kas
  seperti dulu. Dokumen biaya admin kini membawa `dari` (cacat lama: tanpa `dari` → dipotong dari LACI di saldo per tempat) + `untuk: 'toko'`; utang turun sebesar nominal bayar.
  Rekening yang belum pernah diisi (titik kas 0) disebut & ditawari **catat isi rekening** (K4 Pindah uang → `susunTitikRekening`: `pengaturan/titikKas` baru bertanggal KEMARIN,
  laci/brankas/amplop = hasil hitung sampai kemarin, rekening = isi m-banking − gerakan rekening hari ini; bila titik sudah hari ini → ditulis ulang). Buku bon menyebut tunai/transfer + admin.
- Uji baru (CI): `uji_uang_karyawan.py`, `uji_upah_per_orang.py`, `uji_bayar_pemasok_transfer.py` (+ kontrol; asap cadangan + ASAP GLOBAL laba tiap bulan byte-sama dengan main).

## Putaran 30 — harga beli per kelas mutu (28 Sep 2026, cabang `tulang-punggung/30-harga-kelas`)

Masalah owner 28 Sep: pemasok mengganti nama merek walau barang & harganya sama, jadi "harga lalu" di Barang masuk hilang dan riwayat harga terputus.
Peta Tahap 0 & keputusan owner: `docs/peta-harga-kelas.md` (§12–§13). Tanpa koleksi baru, rules v4 tidak berubah, 28 mesin beku & `index.html`/`kasir*.html`
tidak disentuh; ASAP GLOBAL omzet/laba/neraca/nilai stok byte-sama.
- **Kelas mutu** = nama wadah (aturan wadah `daftar`; `merekKarung` = kelasnya sendiri) atau merek berbuku yang dipilih owner. Dokumen
  `aturanToko/kelasMerek {peta {merek: kelas}, asal {merek: owner|tebakan}, kelasSendiri []}` (owner saja). Logika `kelas-merek-logika.js` (`km`), tanpa DOM.
- **Dua macam kelas**: BERWADAH → buku tetap per merek pemasok, peta hanya lapisan baca; TANPA WADAH (`kelasSendiri`, mis. ketan — sejak awal bukunya atas
  nama kelas) → baris dibukukan ATAS NAMA KELAS + kolom baru `merkPemasok` di `batchMasuk.merkList[]` (mesin beku & cadangan mengabaikannya; tampil di Buku
  kedatangan "Kelas (merek)", garis waktu HPP, kartu Per kelas). Pertanyaan varian (`batasVarian`) berlaku atas nama kelas.
- **Tebakan** hanya dari nama = nama wadah · catatan karung ber-`wadah` (terbaru) · resep wadah; jenis beras cuma petunjuk. Tebakan yang dibiarkan saat Simpan
  ditulis SEBAGAI tebakan (daftar menandai "belum dikonfirmasi owner"); keputusan owner tidak pernah ditimpa tebakan.
- **Barang masuk** (`hitungMasuk`): merek dikenal → "lalu Rp… · tanggal · pemasok" (angka = mesin `hargaTerakhirPerKg`, tanggal & pemasok dari `riwayatModal`)
  + ▲▼=; merek BARU → pil kelas (nama wadah, kelas sendiri, merek berbuku) + "tanpa kelas"; kelas berwadah → harga lalu kelas (`kmHargaLaluKelas` =
  gabungan `riwayatModal` anggota, kedatangan nyata saja, pemasok yang dipilih diutamakan, pemasok lain di sebelahnya, batch yang dikoreksi dikecualikan);
  beda > `batasVarian` dari kelas → kalimat lunak "kelasnya benar?" yang TIDAK memblokir; peta ditulis DALAM kiriman Simpan barang masuk yang sama (simpan
  ditolak → peta tidak tertulis); draf localStorage membawa `kelas`/`kelasPilih` per baris. Koreksi kedatangan lama: kelas tidak ditanya.
- **Daftar "Kelas mutu · N/M terisi"** di Harga › Katalog (samping Jenis beras): pil kelas, "tanpa kelas", "nama ini KELAS, bukan merek", usulan kelas tanpa
  wadah = literan langsung.
- **Kartu Per kelas** (Stok › HPP / modal, tab baru): tiap kedatangan anggota satu garis (nama asal · pemasok), rata-rata tertimbang kg per bulan ▲▼,
  kalimat batas periode data WAJIB (per kuartal hanya bila ≥ 2 kuartal berisi); merek tanpa kelas & belum dikonfirmasi disebut.
- **Ganti nama wadah** membawa nilai peta kelas di kiriman yang sama (`kmSusunGantiNamaWadah`, dipakai Stok); nama baru yang sudah jadi kelas lain ditolak.
- Uji: `uji_kelas_merek.py` (+ kontrol, CI). Uji lama yang bundelnya bertambah modul (stok-hpp & kelas-merek): arsip produk, varian merek, wadah bernama,
  stok, kunci periode; jangkar kontrol buku ukuran mengikuti baris merkList yang baru.
- Tugas owner sesudah putaran ini hidup (bukan pekerjaan Claude): memetakan merek kedatangan 18–28 Sep di daftar Kelas mutu dari mutu karungnya; menandai
  kelas tanpa wadah; mengoreksi kedatangan 28 Sep baris merek ketan menjadi nama kelas + `merkPemasok` lewat Buku kedatangan › koreksi.

## Putaran 31 — pemantapan: empat perbaikan kecil serah terima 28 Sep (cabang `pemantapan/31-empat-kecil`)

- **31.1 Rinci karcis bertanya NAMA kalau harganya sama** (`karcis-logika.js kelompokkanTebakan`): tebakan dengan bentuk sama (jalur, berat, jumlah, harga
  pas) tapi nama beda digabung jadi satu tebakan `seharga` berisi `pilihan[]`; `pakaiTebakan` pada tebakan seharga tidak mengisi keranjang, melainkan
  menyetel `kcPilih` (Jual menggambar "Harga sama — yang mana?"); memilih namanya = tebakan biasa. Dulu IR64 Ascent/Elevate/Apex yang seharga tertukar.
- **31.2 "Jual dulu, tandai untuk dicocokkan"**: TAHAP 0 saja — `docs/peta-jual-tandai-cocok.md` (jalur jujur: nota tercatat, baris `perluCocokkan` +
  `kurangKg/Unit`, buku tetap minus, item di kartu "Mana yang belum dicocokkan?"). Owner menjawab §5 pada 28 Sep (peta §6: owner saja, kolom `perluCocokkan` + `selisihKg`, pemeriksaan ulang tidak berubah, tuntas = cocokkan bertanggal ≥ nota, pita di Jual) → dibangun di cabang sendiri `pemantapan/31b-jual-tandai-cocok` sesudah 31 masuk main.
- **31.3 Penjaga catatan bertanggal MUNDUR** (`jual-logika.js ckCocokTerakhir / ckCocokTerakhirKemasan / ckKalimatMundur`; dipakai `susunSimpanMasuk`
  & `susunSimpanAdukan`): barang masuk / adukan yang tanggalnya sebelum cocokkan terakhir nama itu (hitungan fisik tumpukan; cocokkan wadah & rework tidak
  ikut — pola putaran 11) → dua ketukan, kalimat menyebut tanggal & jam cocokkan terakhir dan "buku terpotong dua kali". Tidak memblokir. Koreksi kedatangan
  lama tidak ditanya. Isi ulang wadah & pindah stok selalu bertanggal hari ini (tidak bisa mundur).
- **31.4 Rework 11 Sep bermodal nol**: hanya ditunjukkan (`docs/temuan-rework-modal-nol.md`) — dokumen `penyesuaianStok dariRework` 41,5 kg atas nama kelas; mesin menilai kg itu
  dengan modal rata-rata (dokumen saja yang Rp0); jalur koreksi yang ada tidak menjangkau dokumen rework tanpa bahan → owner memilih (b): tidak ada tulisan data, temuan DITUTUP (kg itu sudah bernilai rata-rata di buku).
- Uji: `uji_pemantapan_31.py` (+ kontrol, CI); `uji_stok_baru.py` asap cadangan mengiyakan penjaga mundur (`mundur: true`).

## Putaran 31b — jual dulu, tandai untuk dicocokkan (28 Sep 2026, cabang `pemantapan/31b-jual-tandai-cocok`)

Keputusan owner §6 `docs/peta-jual-tandai-cocok.md`. Tanpa koleksi/dokumen baru, rules v4 tidak berubah, mesin beku & `index.html`/`kasir*.html`/katalog kasir
tidak disentuh (kasir tetap menahan).
- **Pemeriksaan ulang stok saat mencatat TIDAK berubah** (`periksaStokKeranjang`); `simpanNota` memisahkannya: `alasanTolak` dulu, lalu stok. Gagal stok +
  akun **OWNER** (`s.tembusBoleh` dari `bukanOwner`) → ketukan pertama ditahan dengan kalimat "Buku X kurang N kg — jual dulu, tandai untuk dicocokkan?" +
  `perluTembus` (daftar `barisTembus(s)`: bebas/butuh/selisih/selisihKg per baris); ketukan kedua (`tembusYakin`) mencatat nota apa adanya, baris yang
  melampaui diberi kolom `perluCocokkan: true` + `selisihKg` (karung × berat, kemasan unit × ukuran, literan L × rasio, repack kg). Staf tetap ditahan.
  Buku dibiarkan minus; laba membaca baris seperti nota biasa. Masalah kantong repack bukan langit-langit buku → tetap ditahan semua orang.
- **Tanda tuntas** (`notaTembusBelumCocok`): cocokkan nama itu (`penyesuaianStok` bukan rework, bagian apa pun; kemasan: `penyesuaianKemasan`) bertanggal
  ≥ tanggal nota — cocokkan biasa, tanpa tombol khusus. Nota yang dibatalkan hilang bersama tandanya.
- **Pita di Jual** "N nota tembus stok belum dicocokkan: …" (pola pita karcis) + tombol "JUAL DULU, TANDAI" di bawah kabar saat ditahan; **Stok › Gudang kartu
  keempat** "Mana yang belum dicocokkan?" mendapat baris paling atas "<nama> · N kg tembus · belum dicocokkan".
- Uji: `uji_jual_tandai_cocok.py` (+ kontrol, CI); `uji_jual_baru.py`: kolom nota baru dikenal, jangkar kontrol "stok tidak dicek ulang" mengikuti bentuk baru.

## Putaran 32 — riwayat penjualan (28 Sep 2026, cabang `pemantapan/32-riwayat-penjualan`)

Permintaan owner 28 Sep: "buatkan seluruh riwayat penjualan". Keputusan: layar di aplikasi, **Jual › tab Riwayat** (sesudah Retur), tindakan per nota **Struk** dan
**Retur**. Baca saja: tanpa koleksi/kolom baru, rules v4 & mesin beku tidak berubah. Logika `riwayat-logika.js` (`rw`), tanpa DOM.
- **Satu nota** = kunci panel "Hari ini" (`grupNota` → `trxId` → `id`); baris internal satu takaran wadah digabung (`gabungTakaran`). Nota berlaku = baris belum
  dibatalkan / belum digantikan rincian (`penjualanMasihBerlaku`); nota batal / sudah dirinci hanya tampil lewat "tampilkan batal / dirinci" (redup, bertanda).
- **Angka**: total nota = Σ `hargaTotal` baris berlaku (= panel "Hari ini"); **omzet = total nota − uang retur hari itu** (`uangKembaliRetur`, rumus mesin laba =
  `rekapHari`), disebut di kepala tiap hari dan di ringkasan selama tidak ada saringan jenis/cara/cari (retur tidak bisa dipilah per jenis/cara).
- **Saringan** menumpuk: periode (hari ini · 7 hari · 30 hari · bulan ini · semua — bawaan semua), jenis (karung · kemasan · literan · repack · wadah · karcis kasir),
  cara (Tunai · QRIS · Bon), cari (nama pembeli, barang, nominal "739.000"/"739000"). 50 nota per halaman, "tampilkan 50 lagi"; jumlah nota & omzet per hari
  dihitung dari SEMUA nota yang cocok hari itu.
- **Tindakan**: ketuk nota → rincian baris; **Struk ›** = lembar struk yang ada (`bukaStruk` trx/grup/id); **retur** hanya di baris karung/kemasan yang boleh kembali
  (`rtDasarNota`) → jalur Retur dengan nota itu ditunjuk (`tunjukNota`); yang tidak boleh menyebut alasannya (mis. nota Bon).
- Uji: `uji_riwayat_penjualan.py` (+ kontrol, CI); `uji_isian_lokal.py`: `rwCari` = pencarian, bukan isian.

## Putaran 33 — gerbang masuk G4, kinerja, gerak (29 Sep 2026, cabang `pemantapan/33-gerbang-kinerja-gerak`)

Permintaan owner 29 Sep: gerbang masuk desain HIFI (G4 dikunci di kanvas "Gerbang Masuk"); "perpindahan layar ada lag, suka nge-freeze apalagi waktu
refresh & pertama buka"; UI lebih hidup & intuitif dari segi gerak; animasi penutup Jual sesudah transaksi (omzet bertambah).
- **Kinerja** (terukur `alat-uji/ukur_kinerja_baru.py`, cadangan lokal: 54 koleksi / ±6.900 dokumen): tiap koleksi yang datang (dari cache LALU server, ±108×
  saat buka) dulu menggambar ulang SEMUA layar, Jual menyusun ulang raknya ±50 ms tiap kali (±3–5,6 dtk hitungan beruntun di Mac). Kini `inti/jadwal.js`:
  `nanti(f)` = digabung sekali per bingkai (masa muat: ±320 ms), `segera(f)` = jalur ketukan (selalu bingkai berikutnya). Bunyi data & status mengantre fungsi
  YANG SAMA (tanpa gambar ganda); layar tersembunyi (termasuk Jual) hanya ditandai kotor dan digambar saat dibuka — itu pun hanya kalau kotor atau DOM-nya
  kosong (dikosongkan tirai). Ketukan pindah layar kini tertahan 0–15 ms (Ringkasan dulu ±80 ms), layar yang tidak berubah tidak dihitung ulang (Harga dulu 182 ms
  tiap kembali). `index.html` memuat 71 `modulepreload` (graf impor app.js, dijaga uji) + preconnect Firebase.
- **Gerak** (`css/gerak.css`, `app.js datangkan/geserPenanda`): layar datang dari ARAH tab (Web Animations pada anak `<main>` — bukan kelas CSS: mengganti
  animation-name memutar ulang animasi dasar section; bukan `<main>`: transform di sana membuat elemen fixed meloncat); penanda pil emas meluncur di menu bawah &
  samping; tombol membal saat ditekan; `gulirkan` mulai dari angka lama & bertahan saat dimorf ulang di tengah gulir.
- **Gerbang G4** (`index.html #modalMasuk`, `inti/gerbang.js`, `inti/gerbang-hiasan.js`, `css/gerbang.css`): pintu kaca bergaris, kotak logo & pil tanggal/jam
  terbelah di SPASI antar kata ("Toko | Beras", "tanggal | jam"), cincin kunci (email mengisi cincin, tiap huruf sandi memutar satu takik), golden hour + siluet
  sawah + burung/capung/kunang (gerak berulang berhenti saat "kurangi gerakan"). ID formulir putaran 23 tidak berubah; 'tampil' = arti lama (dicabut SEKETIKA saat
  membuka, gerak di kelas 'membuka' tanpa menghalangi ketukan). Sebelum Firebase menjawab: gerbang tertutup tanpa formulir; sesi dipulihkan → pintu terbuka cepat
  ±0,9 dtk; sesudah masuk ±2 dtk (cincin sejajar → lubang kunci berputar → cincin mekar → pintu bergeser); Keluar → pintu merapat. Sandi kosong → kolom berdenyut;
  catatan sandi berbahasa toko (owner 29 Sep). Tanpa angka toko (tirai 23c).
- **Penutup omzet Jual** (`jual.js penutupOmzet`): kartu Hari ini DITAHAN (dipasang SEBELUM menulis — snapshot lokal Firestore tidak boleh menaikkan angka lebih
  dulu) selama terima uang & serah terima; koin emas terbang dari panggung ke angka omzet (lembar terbuka / HP → ke pil di atas layar), cincin cahaya & kilau di
  luar `<main>`, angka bergulir, "+Rp" & baris baru disorot. Token per nota: nota berdekatan → patokan terlama, sekali perayaan gabungan; dihitung ulang saat
  mendarat (batal selagi terbang → tanpa perayaan); terkunci → berhenti. Saat mengunci, pil/koin/panggung omzet dicabut (tirai).
- Warisan yang ikut dibetulkan: `tampilkan(false)` untuk semua layar hanya saat MENGUNCI (dulu tiap perubahan akun — akses karyawan diubah owner saat bekerja
  membekukan layar yang terbuka).
- Uji: `uji_kinerja_gerak.py` (+ kontrol, CI: preload = graf impor, penjadwal di jsc dengan jam palsu, sambungan, gerbang, penutup); `uji_akses_baru.py` &
  `uji_layar_kunci.py` mengikuti bentuk baru (penjaga tirai & kontrolnya). Tinjauan adversarial 8 agen: 18 temuan lolos bantahan, semuanya ditambal.
- CI pertama PR #57 merah di `uji_layar_kunci --kontrol`: (1) kontrol 2 DIAM — tirai kini DUA lapis (tiap layar memeriksa `terkunci()` DAN saat mengunci
  semua layar, Jual juga, disembunyikan); merusak `terkunci()` saja tidak lagi membocorkan apa pun, jadi kontrol 2 merusak kedua lapis. (2) 3× DICOBA ULANG
  90 dtk, semuanya skenario Firebase PALSU: `modulepreload` SDK ke gstatic di index.html tidak ikut dialihkan ke `/_palsu/` → halaman uji tetap mengunduh
  SDK sungguhan dan event load menunggunya. Salinan uji kini mengalihkan preload itu juga (skenario palsu kembali tanpa jaringan).
  CI kedua: kontrol 9 (Firebase dari CDN tidak termuat → wajib GAGAL JARINGAN) DIAM — preload membuat SDK tampak "lengkap" tergantung urutan unduhan;
  kontrol 9 kini memutus KETIGA modul SDK di firebase.js dan preload (CDN mati sungguhan). Masih ada 1× DICOBA ULANG 90 dtk di skenario palsu (sebab belum
  terbukti); baris DICOBA ULANG kini membawa catatan waktu (halaman melapor selesai, gambar penahan dijawab, permintaan terakhir) supaya kejadian berikutnya
  menjelaskan dirinya — diagnosis berulang hanya di runner (CLAUDE.md).

## Putaran 34 — rapi-rapi tata letak: Jual (29 Sep 2026, cabang `rapi/34-jual-tata-letak`)

Owner 29 Sep: rapi-rapi = STRUKTUR & TATA LETAK (bukan desain baru, tanpa mockup); boleh pindah blok; Mac paling teliti; penjelas panjang boleh diringkas;
terbit per kelompok (Jual → Ringkasan & Stok → sisanya), Claude merge sendiri sesudah CI hijau. Isi, fitur, angka & alur uang TIDAK berubah.
- **Mac ≥1280** (`kerangka.css`): isi sampai 1720 px; rak = kolom lentur, keranjang (`--lebar-keranjang`) & Hari ini (`--lebar-samping`) selebar tetap dan
  sama-sama menempel saat rak digulir. Kartu rak `auto-fill` menurut lebar RAK (4 sebaris di ±1860 px, 3 di 1440). **1100–1279** (laptop kecil / iPad
  mendatar): dua kolom seperti tablet — tiga kolom menyisakan dua kartu sempit. **Tablet**: kolom keranjang selebar tetap, rak sisanya (2 kartu di 820).
- Kabar (barang masuk, nota barusan, karcis) di tablet & Mac hanya di kolom rak — keranjang & Hari ini tidak meloncat tiap ada kabar. Jarak antarbaris lewat
  margin (baris pita/kabar yang kosong tidak menyisakan dua celah).
- Deret tab rak & saringan jenis: di Mac dibungkus (dulu menjulur tanpa batang gulir, tab terakhir terpotong); HP & tablet digeser, ujungnya memudar.
- Lembar (jumlah, bayar, nama, …) duduk TEPAT di atas kolom Hari ini (Mac) / kolom keranjang (tablet, 1100–1279), tingginya mengikuti isi. Cacat lama:
  tirai di belakang lembar mewarisi `width: 440px` / `46vw` dari aturan lembar → hanya menutup sebagian kiri layar; kini `.lembar:not(.tirai)`, tirai penuh.
- Panggung adegan (`adegan.js sejajarkan`) di tablet & Mac duduk di kolom keranjang, tepat di bawah bilah jumlahnya (dulu di tengah layar menutupi separuh
  rak & kepala keranjang); tetes barang berangkat dari panggung.
- Pita "Nota dicatat ke data toko … · tersambung" (mengulang teks kepala) dicabut; pita hanya untuk keadaan yang wajib terlihat: TANPA INTERNET atau koleksi
  ditolak server (`app.js statusAwas`). Mode cadangan & "belum tersambung" tetap.
- Keranjang: empat tombol 2 × 2. Hari ini: satu garis per baris (dulu dua) dan baris rapat.
- Cacat lama yang ketahuan tinjauan: `body { overflow-x: hidden; overflow-y: auto }` (19 Sep, iPhone ditarik ke samping) membuat body jadi WADAH GULIR
  yang tidak pernah bergulir → `position: sticky` keranjang tidak pernah menempel. Kini `overflow-x: clip; overflow-y: visible` (pasangan lama tetap di depannya
  untuk peramban tanpa clip); halaman tetap tidak bisa digeser ke samping (lebar dokumen = lebar layar di lima layar HP). Lembar di tablet & 1100–1279
  menutupi kolom keranjang → adegan isi ulang wadah dari lembar itu kini diputar di kolom rak. Tepi & tinggi lembar memakai % (bukan vw/vh: batang gulir &
  bilah alamat HP); kolom Hari ini paling sempit 360 px = lebar lembar.
- Uji: `alat-uji/uji_tata_letak_jual.py` (+ kontrol, CI) — statis + jsc: tirai tidak mewarisi lebar, kabar hanya di kolom rak, kartu rak auto-fill, tab Mac
  dibungkus, lembar di atas kolomnya, panggung sejajar keranjang, pita status hanya tanpa internet / ditolak. Dilihat di peramban (cadangan): 1864, 1440, 1280, 1120,
  820 & 390 px — rak, lembar jumlah & bayar, adegan barang masuk & nota, koin omzet.

## Putaran 35 — rapi-rapi tata letak: Ringkasan & Stok (29 Sep 2026, cabang `rapi/35-ringkasan-stok`)

Kelompok 2 rapi-rapi (aturan sama dengan Putaran 34). Di Mac ketiga layar kini selebar 1720 px (dulu Jual 1480, Ringkasan 1480, Stok 1180).
- **Stok › Gudang**: tombol kerja (Barang masuk, Adukan, Cocokkan, Kantong, Tempat simpan, HPP) dulu di dasar halaman ±2.600 px di Mac. Kini di
  `<aside class="stok-samping">` tepat sesudah kartu pertanyaan: HP & tablet urutan tanya · tombol · jawaban · per jenis (aside `display: contents` +
  `order`); Mac jawaban di kiri, tombol + "Beras di buku per jenis" di kolom kanan yang menempel; ≥1280 daftar jawaban dua kolom yang urut ke BAWAH
  (`columns`, daftar peringkat tetap terbaca 1, 2, 3 di kolom kiri). Tinggi halaman di 1864 px: ±2.600 → ±1.270. Lembar (Barang masuk, Cocokkan, …),
  Papan Kapur & Karantina tetap paling lebar 1180 px, rata kiri di bawah judul — formulir tidak melar. Wadah literan selebar halaman: 8 wadah sebaris di ±1860 px.
- **Ringkasan**: kas, uang hari ini, perlu perhatian & catatan katalog satu `<aside class="rk-samping">` (dulu sel lepas: pita sumber cuma separuh lebar,
  catatan katalog melayang di sel sendiri). HP tetap hero · nota · samping; tablet nota | samping; Mac hero & nota di kiri, samping kanan menempel. Pita
  sumber yang kosong tidak menyisakan baris.
- Tinjauan adversarial (7 lolos → 4 cacat, semua ditambal): samping Ringkasan yang lebih tinggi dari hero + nota dulu membuka lubang di bawah hero (baris
  terakhir kini 1fr, seperti Jual); Atur wadah (formulir) ikut melar (kini hanya kotak wadah yang lebar); pita kabar Stok selebar 1720 di atas formulir 1180
  (kini selebar formulirnya); animasi masuk Ringkasan naik dari bawah (aturan `.kartu:last-child` yang dulu tak pernah kena kini menangkap nota — dicabut).
- Uji: `alat-uji/uji_tata_letak_ringkasan_stok.py` (+ kontrol, CI). Dilihat di peramban (cadangan): 1864, 1440, 1120, 820 & 390 px.

## Putaran 36 — rapi-rapi tata letak: Pelanggan, Harga, Uang, Laporan, Menu (29 Sep 2026, cabang `rapi/36-layar-lain`)

Kelompok 3 rapi-rapi. Harga, Uang & Laporan sudah tiga kolom di Mac (desain kanvas yang dikunci) — yang dirapikan STRUKTUR bersama, bukan isi:
- Di Mac ketujuh layar kerja (Jual, Ringkasan, Stok, Pelanggan, Harga, Uang, Laporan) selebar 1720 px dengan pinggir 22/28/40 px: judul & pil di tempat yang
  sama tiap pindah layar (dulu 1180/1240/1480 px dan pinggir 14 atau 28 — judul meloncat ke kiri-kanan). Pelanggan kini menghitung lebar termasuk pinggir
  (border-box) seperti layar lain.
- Tiga kolom Harga/Uang/Laporan: kolom samping melebar mengikuti layar (`minmax(…, clamp(…vw…))`) — di 1280 px selebar dulu (kolom tengah tidak menyempit),
  di ±1860 px +40–50 px; kolom tengah mengambil sisanya (±810–870 px).
- Menu TIDAK diubah: kolom 860 px di tengah = desain N1 ("Pertahankan desain UI di layar N1", owner 16 Sep).
- Tinjauan adversarial (4 lolos → 3 cacat, semua ditambal): pinggir 28 px dulu dibayar kolom tengah (1100–1339 px menyempit 28 px; di 1100 label UNTUK KARYAWAN
  menabrak nominal) → batas bawah kolom samping 14 px di bawah lebar lama, kolom tengah di 1100 kembali 238 px; lembar/formulir di luar grid (Uang `.ug-lembar`,
  Harga `section > .kartu`, Laporan `.lp-lembar`) ikut melar ke 1664 → 1180 seperti Stok; gambar truk Harga › Belanja (preserveAspectRatio none) melar 1,42×
  di kolom 510 px → paling lebar 360 px.
- Uji: `alat-uji/uji_tata_letak_layar_lain.py` (+ kontrol, CI). Dilihat di peramban (cadangan): 1864, 1280 & 1100 px.

## Putaran 37 — tambalan tinjauan gabungan rapi-rapi (29 Sep 2026, cabang `rapi/37-jual-tambalan`)

Sesudah #58–#60 masuk, gabungannya ditinjau sekali lagi (8 agen, 4 lolos bantahan → 3 cacat, semuanya di Jual, lahir karena sticky kini benar-benar hidup):
- **Keranjang menempel lebih tinggi dari layar** → Ditagih & BAYAR tertahan di luar layar / di bawah nav sampai halaman digulir ke ujung (iPad 1024×768 dengan 3–4
  barang, Mac 1280×800 dengan 4+, HP miring bahkan kosong). Kini setinggi layar paling banyak (tablet 100dvh − 112: 14 atas + nav 84 + 14; Mac 100dvh − 44,
  border-box); DAFTAR BARANG yang bergulir di dalam, total & BAYAR tetap terlihat; layar yang terlalu pendek untuk bagian tetapnya (HP miring) → seluruh
  keranjang bergulir. Diukur (cadangan, 9 barang): Mac 1280×800 BAYAR 687–741, iPad 1024×768 579–633 (nav 682), HP 844×390 terjangkau dengan menggulir keranjang.
- **Lembar dibuka selagi adegan berjalan** tertutup panggung di tablet & 1100–1279 → `jual.js` memanggil `sejajarkanLagi()` (adegan.js) tiap lembar berganti:
  panggung pindah ke kolom rak (terukur 820 px: keranjang x 478 → rak x 28, tidak lagi menumpuk lembar).
- **Tetes emas barang masuk** terbang di bawah kartu panggung (z 60 < 70) → z 71 (di bawah pil & koin omzet 74/75).
- Tinjauan tambalan ini (9 agen, 3 lolos): baris baru jatuh di bawah jendela daftar yang kini bergulir sendiri → sesudah digambar, daftar digulir ke baris baru
  (terukur iPad 1024×768: baris ke-4…7 melewati jendela 307 px, baris terbaru tetap terlihat); daftar paling pendek satu baris utuh (112 px, bukan 56) dan di
  layar pendek (tinggi ≤560, HP miring) daftar TANPA penggulir sendiri — satu penggulir, seluruh keranjang; daftar ber-data-k per struk → pindah / parkir
  struk mulai dari atas (dulu posisi gulir terbawa).
- Uji: `uji_tata_letak_jual.py` +9 pemeriksaan & 9 kontrol (30 lulus · kontrol 23/23).

## Putaran 38 — kendali biaya / cost controlling (29 Sep 2026, cabang `kendali/38-kendali-biaya`)

Permintaan owner: "cari tahu tentang cost controlling dan terapkan ke sistem ini". Kendali biaya = MEMILAH lalu MEMBANDINGKAN; mesin uangnya tidak berubah
(28 mesin beku utuh, ASAP GLOBAL laba tiap bulan byte-sama dengan main). Satu keluarga baru di Laporan: **Biaya** (owner saja, seperti Laporan lainnya),
logika tanpa DOM di `js/layar/kendali-biaya-logika.js`. Lima bagian dalam satu layar:
1. **Jenis biaya** — tiap rupiah di bawah margin kotor jatuh ke TEPAT SATU jenis: upah & gaji · tagihan tetap (listrik/internet/akses/keamanan) · potongan QRIS &
   biaya bank · karyawan di luar upah · bahan pakai & kresek · bensin & angkut · dapur toko · lain-lain; di bawahnya hapus buku piutang & susut/selisih stok
   (mesin menaruh keduanya di bawah laba kotor). Urutan pemilahan uang keluar harian: tanda MDR / biaya bank → kolom `untuk` = karyawan (putaran 29) → kata
   kunci owner → kata kunci bawaan → lain-lain. Kata dicocokkan sebagai AWALAN KATA di batas kata ("roko" kena "rokok"; "donasi" TIDAK kena "nasi"). Yang tidak
   cocok TETAP dihitung (baris Lain-lain) dan disebut "belum dipilah" — tidak ada catatan yang hilang, tidak ada tebakan yang disembunyikan. Wajib MENUTUP:
   Σ jenis harian = harianToko mesin; upah + tetap = jatah bulanan mesin; margin − Σ − hapus buku − susut = laba bersih mesin (kalau tidak, layar bilang begitu).
2. **Anggaran** = setelan owner per jenis per bulan (`aturanToko/kendaliBiaya`: anggaran, ambang lampu, ambang pemicu, kata kunci tambahan). Tanpa anggaran
   lampu mati — yang tampil hanya *acuan terukur* (median ≤ 3 bulan sebelumnya yang punya catatan; bulan sebelum awal buku tidak ikut). Tombol "isi dari acuan"
   mengisi FORMULIR, bukan menyimpan. Anggaran bukan larangan (aturan jatah 22 Agu): lewat tetap tersimpan, bedanya kelihatan hari itu.
3. **Aktual vs anggaran** — lampu hijau (≤ anggaran) · amber (≤ anggaran + ambang %) · merah. Bulan berjalan: jenis variabel dibanding JATAH SAMPAI HARI KE-N
   (anggaran × hari jalan ÷ hari bulan) + perkiraan sebulan (linear, ditandai perkiraan); jenis tetap dibanding anggaran sebulan; upah ditambah upah yang
   BELUM DIBAYAR (dari absen, `upah-logika`) supaya "upah baru sedikit" tidak terbaca hemat padahal belum gajian. Bulan lampau yang upahnya belum dibayar
   juga terlihat. Pos tetap yang belum dicatat bulan ini (ada bulan lalu) disebut.
4. **Pemicu biaya** per satuan, bulan ini vs bulan lalu: biaya toko/kg terjual · HPP/kg · harga jual/kg · margin/kg (arah dibalik: turun = buruk) · harga beli/kg
   kedatangan · bongkar/kg kedatangan (tertanam di HPP, disebut supaya kelihatan) · potongan QRIS % omzet QRIS · biaya karyawan/hari kerja (dibayar + belum
   dibayar + di luar upah, ÷ hari gaji + hari menggantung) · harga kantong/lembar · susut/kg. Naik di atas ambang pemicu → disebut.
5. **Titik impas & peringatan** — omzet impas = biaya di bawah margin ÷ rasio margin (margin ÷ omzet ber-HPP, nota tanpa modal disebut tidak ikut); per bulan &
   per hari vs omzet nyata per hari; "sampai hari ini" dari mesin (awal bulan → hari ini): menutup atau kurang berapa & omzet tambahan yang dibutuhkan.
   Peringatan berurutan (awas dulu): lampu, pos tetap belum dicatat, upah belum dibayar, susut ≥ 20 % margin (tanpa toleransi), > 25 % harian belum dipilah,
   cakupan HPP < 95 %, pemicu naik, belum impas, TIDAK MENUTUP — tiap baris menunjuk layar tempat membereskannya. Pareto = pos terbesar (per kata yang cocok /
   per pos gaji & tagihan) yang membentuk 80 % biaya. Tren 6 bulan: margin (emas) vs biaya (platina, merah bila lebih besar), ketuk = pindah bulan.
- Layar: `laporan.js` `gambarBiaya` (kartu: bulan · kepala · yang perlu dilihat · peta biaya (ketuk baris = rincian ≤ 8 catatan) · titik impas · pemicu ·
  pareto · tren · belum dipilah (ketuk keterangan → pilih jenis = keterangannya jadi kata kunci owner) · atur). Tiga lebar: HP satu kolom; Mac
  [bulan+kepala+peta] · [peringatan+impas+pemicu+belum dipilah] · [pareto+tren+atur]. Menu › cari "biaya". Sepuluh pertanyaan Menu tidak ditambah (terkunci owner).
- Koleksi: hanya `aturanToko/kendaliBiaya` yang baru ditulis (owner; rules v4 sudah mengizinkan owner untuk id apa pun di aturanToko, tanpa perubahan rules).
- Batas yang jujur: perkiraan sebulan = linear dari hari yang sudah jalan; kata kunci bawaan = tebakan awal yang owner boleh timpa; upah belum dibayar =
  [PERKIRAAN] dari absen & tarif, bukan angka mesin laba; kedatangan tanpa kg → pemicu per kg "belum bisa dihitung".
- Uji: `alat-uji/uji_kendali_biaya.py` (+ `--kontrol`, CI) — 45 skenario kotak pasir (angka contoh, jam 19 Sep 2026) + 23 kontrol; asap cadangan: tiap bulan
  menutup ke mesin laba, rasio impas = margin ÷ omzet ber-HPP, pareto total = biaya; ASAP GLOBAL byte-sama dengan main. Pengantar: `docs/peta-kendali-biaya.md`.

## Putaran 39 — wadah literan satu buku per kotak (29 Sep 2026, cabang `wadah/39-satu-buku`)

Peta Tahap 0 & keputusan owner: `docs/peta-wadah-satu-buku.md` (§1–§7 akar & pertanyaan; **§8 = enam jawaban owner, bentuk dokumen tiap jalur, tugas
owner sesudah merge**). Tanpa koleksi baru; mesin beku & `index.html`/`kasir*.html` tidak disentuh. **Rules v5** (karyawan menuang & mengecek wadah),
jalan mundur `firestore.rules.v4`.
- **Karung di belakang wadah = buku sendiri** (`data/toko.js` `kunciKarungBelakang` / `petaBukuWadah()` jenis `'belakang'` / `merkAsalKunci`): buku
  `'Karung belakang <wadah> · <merek>'` per wadah × merek asal. Buka karung = pindah buku merek → karung belakang (tumpukan gudang turun di buku), tuang =
  pindah buku karung belakang → wadah (`wbDokBukaKB`, `wbKarungBelakang`, `wbKarungBelakangWadah`). Catatan kolam `karung`/`takar` tetap ditulis bernama
  kunci bukunya + `merkAsal`; `deretanKarung` & layar Stok memajang merek asalnya; `beratKarungBuka` lewat merek asal; tutup buku membawa tanda
  `karungBelakang` + `merkAsal`. Karung lama bernama merek di belakang wadah aktif dipakai sampai habis (jalur lama).
- **Isi ulang tiga ketukan** (`wbSusunIsiUlangTiga(W, M, { jenis: 'karung' | 'setengah' | 'kg', kg? }, w, s, opsi)`, `WB_TAKARAN`): wadah AKTIF ← merek
  asal dari rak × takaran; karung belakang dipakai dulu, kurang → karung baru dibuka dari tumpukan; satu kiriman [lahir?, pindah merek → karung belakang,
  `karung`…, `takar` ber-`takaran`, pindah karung belakang → wadah]; melebihi batas menggunung ditolak dengan kalimat. Panel − / + takar tetap sebagai
  takaran lain (`susunTakarWadah(…, opsi)`, `takaran: 'takar'`).
- **Buku merek asal kurang → tidak diam, tidak menulis hantu**: `{ tolak, perluTandai: [{ merk, buku, butuh, kurang }] }` dari `wbDokBukaKB` /
  `wbSusunIsiUlangTiga` / `susunTakarWadah` / `susunBukaKarung` / `wbSusunAktifkan`; layar menggambar pita dua tombol — "Catat barang masuk dulu"
  (Stok › Barang masuk) atau "TANDAI UNTUK DICOCOKKAN" (panggil ulang `opsi { tandai: true }` → pindah buku bertanda `perluCocokkan` + `selisihKg` +
  `selisihPerMerk`, buku dibiarkan minus; boleh karyawan, namanya tercatat lewat atribusi pusat). Tuntas = cocokkan merek itu bertanggal ≥ dokumen
  (`wbPindahTembusBelumCocok`, digabung `notaTembusBelumCocok()` → pita Jual & kartu keempat Gudang otomatis).
- **Aktivasi per wadah** (`wbDaftarAktivasi()` → `wbSusunAktifkan(W, w, opsi)`): tiap wadah menyebut isi tercatat, merek asal & bukunya, karung terbuka
  lama di belakangnya, kekurangan & alasannya; satu wadah = batch lahir (wadah + karung belakang) + pindah isi (`pindahAwalWadah`) + `isi` `pindahAwal` +
  `komposisi` + per karung terbuka lama: pindah + 2 `karungIsi`. Nilai stok, laba, neraca tidak berubah. `wbSusunPindahAwal` (28, semua sekaligus)
  tidak dipakai layar lagi.
- **Komposisi turunan & banding** (`wbKomposisiTurunan(W, s)` → `{ daftar, banding, terakhir: { jam, oleh, kg, takaran }, teks }`): takar per merek asal
  sejak titik samakan terakhir (komposisi awal di titik itu + tiap takar), disebar sebanding ke buku wadah — bukan angka kedua; tampil di Jual · Stok ·
  dashboard.
- **Cek wadah tutup toko** (`WB_CEK`, `wbCekHari(iso)`, `wbSusunCek(W, hasil, w)`): `wadahLiteran` tipe `'cek'` `{ hasil: 'sesuai' | 'lupa' | 'kosong',
  bukuKg }`; kosong = `wbSusunSisih` seluruh buku ke karung wadah tanpa timbang + cek (butuh wadah aktif). Kartu per wadah aktif di K5; `tutupHari`
  tetap owner.
- **Dua angka satu kotak → selisih disebut** (`wbSelisihWadah(W, s, bebasLiter)`): belum aktif = bebas dijual (buku merek asal) vs isi kotak tercatat →
  "aktifkan"; aktif = tiap karung belakang catatan vs buku → "samakan karungnya".
- **Rules v5 & akses**: `firestore.rules` `stafBuatWadah` (tipe takar/karung/karungIsi/cek) · `stafBuatLahir` (batch LAHIR BUKU 0 kg) untuk
  `ben`/`karyawan`; `akses.js` `BUAT_STAF` + `wadahLiteran` & `batchMasuk`, `TIPE_WADAH_STAF`, `batchLahir`, `SERVER_BUKA.isiUlang`; `sistem-logika`
  tindakan ke-14 `isiUlang` "Isi ulang & cek wadah literan" (bawaan `sendiri` keduanya). Penjaga perangkat berkata sama dengan rules; aturan wadah,
  titik samakan isi, kedatangan sungguhan, `tutupHari` tetap owner. `periksa_rules.py` mengenal dua fungsi jujur baru; `peta_akses.py --kiriman`
  mengukur isi ulang ½ karung = 5 dokumen + jejak = **6 / 20** dan menuntut tiga kiriman terlarang ditolak di perangkat. Rincian: `docs/peta-hak-akses.md`
  §9; uji server `docs/uji-rules-v5.md`; salinan v4 = `firestore.rules.v4`.
- Layar (digabung ke cabang ini: `5971250` Stok · `b5d4dc0` Jual & panel · `e215c1c` K5 · `041b9c2` tambalan silang layar). **Stok › Wadah literan**
  `stok.js`: kartu "Aktivasi buku wadah — per wadah, owner memutuskan" (`wbDaftarAktivasi`; satu baris per wadah: status · isi tercatat · tabel sumber
  merek asal di wadah / di karung / buku / kurang · AKTIFKAN dua ketukan · TANDAI UNTUK DICOCOKKAN lewat pita `pita-tandai` (`tandaiMasuk` /
  `tandaiTulis` / `tandaiBatal`) · "Hitung fisik <merek> dulu" ke Cocokkan › Tumpukan gudang · "Catat barang masuk"; tombol lama "semua sekaligus"
  dicabut), kartu "Karung di belakang wadah … · buku sendiri per merek" (`wbKarungBelakangWadah`: buku · catatan · selisih → `samakanKarung` dengan
  merk = kunci buku), komposisi turunan, selisih, status cek hari ini. **Panel wadah** `wadah-panel.js` (Jual & Stok): tiga ketukan `wdMerkTiga` →
  `wdTakaranTiga` / `wdTutsTiga` → `wdIsiTiga`; kepala "Isi wadah = buku ±X kg" + komposisi + selisih; pita dua pintu `wdKeStok` / `wdTandaiBatal`;
  panel − / + tetap sebagai "Takaran lain" (`wdCatat` meneruskan opsi); wadah belum aktif = panel lama + "aktifkan di Stok › Wadah literan".
  **Jual › Literan** `jual.js`: chip wadah memuat baris komposisi (merek asal · jam · siapa) & awas selisih; tombol "Cek wadah · N/M hari ini" → lembar
  `cekWadah` (per wadah aktif: sesuai / lupa isi ulang / dikosongkan dua ketukan; "lupa" membuka chip dengan panel isi ulang). **Uang › Tutup hari**
  `uang.js`: kartu "Cek wadah" di antara Timbang cepat & Amankan laci — kartu, bukan langkah `LANGKAH_TUTUP` (belum semua dicek tidak menahan tutup
  hari); "lupa" sukses → tombol ke Stok › Wadah literan (`bukaStok` dari `app.js`); Timbang cepat menyaring kunci `petaBukuWadah`. Tambalan silang
  layar: panel Stok meneruskan akun; `susunSamakanKarung` untuk buku karung belakang membatasi sisa = yang lebih besar antara satu karung dan bukunya.
  Tombol yang tidak boleh untuk akun ini MATI dengan kalimat (`tombolMati` / `data-kal`), tiap blok bertransisi ber-`data-k`, tiga lebar lewat
  `stok.css` / `jual.css` / `uang.css`.
- Papan Kapur (`susunKapur`): baris buka karung berbuku, cek wadah, tanda KURANG; `kmTebak` mengenal `merkAsal`.
- Uji: `uji_wadah_satu_buku.py` (+ kontrol, CI); jangkar `uji_jual_baru`, `uji_stok_baru`, `uji_buku_ukuran`, `uji_wadah_stok_sendiri`,
  `uji_menu_baru` (14 tindakan), `uji_akses_baru` mengikuti teks baru.

## Putaran 39b — audit hulu → hilir, temuan pertama (30 Sep 2026, cabang `audit/39b-katalog-kasir`)

Dua "temuan lama" yang dicatat saat gerbang 39, ditelusuri dulu sebelum diubah (FAKTA dari cadangan 29 Sep & peramban, bukan dugaan):
- **BUG alat uji** — `uji_katalog_kasir.py` di cadangan toko: pemeriksaan "isi /baru/ = isi index.html" GAGAL sejak putaran 27/28 dan lolos di CI hanya karena
  runner tidak punya cadangan. Bedanya memang keputusan desain: 4 nama beras yang diarsipkan (27) hilang dari katalog HP kasir, dan 3 merek yang punya buku
  `<Merek> 25 kg` (28) bertukar kolom `karung25` / `karung50` / harga 25 kg antara induk & buku ukurannya. Kini dua pemeriksaan: (1) `susunIsiKatalogKasir()`
  /baru/ SEBELUM saringan = index.html persis; (2) `kkIsi()` = index.html MINUS nama arsip (jumlahnya = daftar arsip beras) MINUS kolom 25 kg merek yang
  punya buku ukuran (kolom yang boleh beda disebut per buku / induk) — kemasan, bahan literan, piutang sama, beda lain nol. Hasil: 41 lulus, 15 kontrol tanpa
  peramban berbunyi (3 kontrol peramban tetap di runner).
- **BUKAN BUG** — "halaman `?cadangan=` masih membuka pendengar Firestore": di tab peramban yang bersih, `/baru/?cadangan=…` hanya mencetak `cadangan dimuat`
  dan **nol** permintaan ke `googleapis` / `gstatic`; `app.js` memang tidak memanggil `fb.mulai` di mode itu. Galat "Missing or insufficient permissions" yang
  dulu terlihat berasal dari `index.html` sistem lama yang dimuat lebih dulu di tab yang sama (server pratinjau membuka akar repo), bukan dari /baru/.
  Pelajaran alat: bukti peramban diambil di tab baru, bukan tab yang riwayat konsolnya sudah terisi halaman lain.
- **Audit hulu → hilir (30 Sep 2026):** 8 pemeriksa (satu per ruas) + penyanggah per temuan + penyusun, baca saja di worktree; 56 temuan mentah → 53 lolos
  sanggahan → 47 sesudah kembar digabung: 31 BUG · 3 DATA · 11 KEPUTUSAN OWNER · 2 ALAT UJI. Daftar, bukti (berkas:baris), dampak (kg/bentuk), dan
  usulan cabang per temuan: `docs/audit-39b-temuan.md`. Pola tetap: laporan dulu, satu cabang per temuan, owner memilih urutannya.

## Putaran 39c — deretan karung = satu slot per wadah, karung habis dihapus, peringatan buka dari tumpukan (30 Sep 2026, cabang `wadah/39c-deretan-delapan`)

Permintaan owner 30 Sep (screenshot Stok › Wadah literan Mac & HP): deretan karung "cuma 8" (merek dari pemasok berganti-ganti — karung yang habis harus bisa
dihapus, yang dikembalikan ke tumpukan jadi gambar karung garis putus "?"), tata letak Mac disamakan dengan HP, dan isi ulang dari layar Jual memberi
peringatan kalau karung di belakangnya habis ("ambil dari tumpukan gudang?").
- **Satu slot per wadah** (`slotKarungWadah()`, `karungLepasDeretan()` di `jual-logika.js`; kartu "Deretan karung terbuka" di `stok.js`): W1..Wn masing-masing satu
  kartu — karung yang berdiri di belakangnya (merek asal, sisa, buku sendiri, HABIS bila kolam ≤ 0,5 kg) atau KOSONG: karung garis putus "?" beralasan
  (dikembalikan ke tumpukan / habis, dihapus / belum ada) + merek terakhir yang pernah berdiri di situ. Karung lepas · yatim · sisihan tampil di baris kecil
  sendiri, bukan di slot. `karungUntukWadah` kini PER MEREK: kolam yang sudah ditutup (karungIsi 0 bertanda `dikembalikan` / `selesai` / `pindahAwal`) tidak
  dihitung; yang terbaru di antara yang hidup = karungnya; tidak ada → slot kosong (bukan jatuh ke karung lama yang sudah dikembalikan).
- **Hapus karung habis** (`susunHapusKarungHabis`, aksi `drHapus`): kolam ≤ 0,5 kg → karungIsi 0 bertanda `selesai` (slot kosong, karung berikutnya dibuka dari
  tumpukan saat isi ulang — merek apa pun). Karung berbuku yang bukunya masih > 0,5 kg padahal kolamnya habis → ketukan kedua mencatat SUSUT sebesar bukunya
  (`penyesuaianStok` kunci buku itu, bagian `karung`, alasan "karung habis") — tidak diam. Masih berisi → ditolak (samakan / kembalikan). Papan Kapur menyebutnya.
- **Kembalikan karung BERBUKU** (celah 39 yang ketemu saat menulis uji): dulu `susunKembalikanKarung` menghapus catatan bukanya / menulis karungIsi 0 saja, jadi
  bukunya (kunci karung belakang) tetap terisi dan tumpukan merek asal tidak pulih. Kini: karungIsi 0 `dikembalikan` + pindah buku KB → merek asal sebesar sisa
  kolam (`kembaliTumpukan`), tumpukan merek asal naik persis sebesar itu.
- **Tata letak = HP**: `stok.css` ≥ 1100 px kotak wadah 4 sebaris (dua baris W1–W4 / W5–W8), deretan 4 slot sebaris di atasnya (slot Wn tepat di atas kotak Wn);
  jangkar `uji_tata_letak_ringkasan_stok.py` mengikuti.
- **Peringatan buka dari tumpukan** (`wadah-panel.js`, Jual & Stok): tiga ketukan / − + takar yang perlu membuka karung baru dari tumpukan (karung di belakang habis,
  kosong, kurang, atau merek lain) tidak menulis di ketukan pertama — pita menyebut berapa karung dibuka, tumpukan sebelum → sesudah, dan "beras di belakang
  berganti: <lama> → <baru>"; tombol jadi "YAKIN — buka n karung dari tumpukan & ISI ULANG" (draf berubah → yakin dicabut).
- **Karung di belakang dihabiskan dulu** (owner 30 Sep, screenshot panel − / +): sisa karung yang tidak cukup untuk yang diminta (1 kg lawan 1 takar 1,8 kg; buku karung
  belakang 25 kg lawan 36 kg) dituang SEADANYA sebesar sisanya — dokumen takar `kg` = sisanya, bertanda `seadanya` + `kgMinta`; kekurangannya TIDAK ditambal dari karung baru.
  Karung baru dari tumpukan baru ditanya (ketukan kedua) sesudah karungnya bersih 0. Berlaku di `hitungTakar` / `susunTakarWadah` (− / +, termasuk karung lama bernama
  merek yang masih bersisa) dan `wbSusunIsiUlangTiga` (tiga ketukan: pilihan merek & takaran dipertahankan sesudah tuang seadanya supaya ketukan berikutnya langsung
  bertanya karung baru; takaran kg dikurangi yang sudah dituang).
- Uji: `uji_wadah_satu_buku.py` bagian 15–16 (12 pemeriksaan) + 6 kontrol + 3 pemeriksaan statis layar/CSS; skenario lama `uji_jual_baru` (P, O, R) & `uji_wadah_satu_buku` (§9)
  yang dulu mengunci "karung baru dibuka otomatis untuk menambal" ditulis ulang mengikuti aturan habiskan-dulu; `uji_stok_baru`, `uji_wadah_stok_sendiri` tidak berubah
  (deretanKarung lama tetap dipakai panel − / + di Jual).

## Audit 39b no. 1 — tutup hari lewat tengah malam menutup hari kemarin (30 Sep 2026, cabang `audit/39b-tutup-hari-tengah-malam`)

Temuan uang U-1 (`docs/audit-39b-temuan.md` no. 1): K5 menutup tanggal KALENDER, jadi tutup pukul 00.05 menutup hari baru (0 nota) — hari dagang
kemarin tetap "belum tutup", titik kas bertanggal hari baru, dan malam berikutnya selisih LEBIH palsu seukuran tunai sehari. 19 dari 31 malam sistem lama
ditutup lewat tengah malam; pagar sistem lama `tanggalTutupAktif` (perbaikan 21 Agu 2026, batas jam 12) tidak ikut ke /baru/.
- `inti/format.js` `tanggalTutupAktif(d)` + `JAM_BATAS_TUTUP = 12`: tutup SEBELUM jam 12 siang = menutup hari kemarin (satu aturan untuk semua).
- `tutup-hari-logika.js`: `hitungTutup` memakai `tanggalTutupAktif(kini)` (+ `lewatMalam`, `kalimatTanggal`); `susunTutup` membaca jam dari tanggal + jam
  tulis (`tdKiniDari(w)`, dulu `ugKiniDari` = tengah hari tanggalnya sehingga jam hilang). Dokumen tutupHari, amplop, MDR, pindah, dan titik kas bertanggal
  hari dagang yang ditutup.
- `uang.js`: K5 (draf, kertas, riwayat, cek wadah, teks WA) memakai `isoTutup()`; pita emas "Lewat tengah malam: yang ditutup hari …" di tiga lebar.
- `wadah-bernama-logika.js` `wbCekHari`: satu cek = satu hari dagang (cek yang ditulis sebelum jam 12 milik hari kemarin); `jual.js` tombol & lembar Cek wadah
  memakai `tanggalTutupAktif`.
- Uji: `uji_uang_baru.py` K5 kini berjam 20.00 (jam kotak pasir 10.00 = sebelum jam 12) + 4 pemeriksaan (00.05 & 11.59 → kemarin, 12.00/12.01 → hari ini,
  dokumen & titik kas bertanggal kemarin) + 2 kontrol; `uji_wadah_satu_buku.py` cek 21 Sep 10.00 = hari dagang 20 Sep, +1 kontrol, +2 pemeriksaan statis.

## Audit 39b no. 2 — kedatangan bon yang sudah dibayar dikunci; satu ejaan per pemasok (30 Sep 2026, cabang `audit/39b-koreksi-kedatangan-berbayar`)

Temuan hulu H2+H3: pembayaran bon pemasok menempel ke bonnya lewat `bonId` (= id kedatangan) + nama pemasok PERSIS. Mesin utang pemasok (beku)
mengalirkan pembayaran yang bonnya hilang/berganti ke bon tertua (live) dan membuangnya (per tanggal). Koreksi cara bayar ke tunai, ganti nama
pemasok, tanggal datang sesudah tanggal bayar, nilai di bawah yang dibayar, atau hapus kedatangan → bon LAIN tampak lunas tanpa uang, layar Bon
dan Neraca berselisih, kas keluar terhitung dua kali. Ejaan beda ("roda mas") memecah pemasok di mesin.
- `stok-catat-logika.js` `ckBayarBon(batch)`: uang yang DITUJUKAN ke bon ini = Σ pembayaran bertunjuk (bonId + nama pemasok persis), paling banyak
  nilai bon. Aliran tanpa tujuan (pembayaran lama tanpa bonId, kelebihan bayar yang terserap) TIDAK mengunci — aturan FIFO mesin memang
  memindahkannya, dan kedatangan salah catat yang menyerap kelebihan bayar tetap bisa dihapus (`dibayarMesin` = pembanding dari
  `hitungUtangPemasok`). `susunSimpanMasuk` (juga jalur koreksi HPP) menolak koreksi bon yang sudah dibayar bila jadi tunai / pemasok lain /
  tanggal datang diubah (maju maupun mundur — bonTanggal di dokumen bayar & neraca per tanggal ikut bergeser) / nilai beras di bawah yang
  dibayar; `susunHapusKedatangan` menolak hapusnya. Harga/jumlah dengan nilai ≥ yang dibayar tetap boleh. `stok-hpp-logika.js` `nilaiKoreksi`
  menolak LEBIH DULU (kartu, pratinjau, koreksi massal) dengan nama berasnya; beberapa nama yang kedatangan sasarannya sama dinilai BERSAMA.
  Bon yang terbayar lewat aliran saja (dibayarMesin > 0, tanpa pembayaran bertunjuk) tetap bisa dihapus, tetapi tanggalnya terkunci.
  Nilai pembanding = bon yang AKAN TERTULIS (baris karung saja; baris bal lama ikut terbuang saat dikoreksi = temuan no. 30, cabangnya sendiri) —
  bon berbayar berbaris bal karena itu ditolak koreksinya sampai no. 30 dibangun (uangnya terlindung).
- `ckEjaanPemasok`: nama yang sama kecuali huruf/spasi ditulis dengan ejaan yang sudah dipakai (kedatangan terbaru, lalu pembayaran/bon lama);
  kedatangan yang sedang dikoreksi tidak memaksa ejaan lamanya sendiri. Kabar menyebut ejaan yang dipakai.
- `stok.js` lembar koreksi: pita "Bon ini sudah dibayar …" menyebut apa saja yang terkunci.
- Uji: `uji_stok_baru.py` +13 pemeriksaan (pemasok uji tersendiri, pembayaran bertunjuk, umpan pemasok lain, FIFO, bon lunas penuh, kelebihan
  bayar yang terserap, koreksi HPP dini & massal dua nama, kedatangan berbaris bal), asap data toko (tiap bon kedatangan: yang dibayar terkunci — bon di bulan terkunci periode dihitung
  terpisah —, yang belum tetap bebas, Σ sisa = mesin, bertunjuk = mesin, ejaan tidak tergeser), +13 kontrol. Tinjauan independen 30 Sep
  (peninjau + penyanggah): 6 temuan lolos lalu 3 lagi dari verifikasi tambalannya — semuanya ditambal di cabang ini.
- Belum dibangun (catatan pemetaan 30 Sep): pembetulan / pemindahan pembayaran bon di sistem baru (urung hanya 90 detik), jejak bonId saat tutup
  buku & batal tutup buku, dan baris bal yang ikut terbuang saat kedatangan berbaris bal dikoreksi (temuan no. 30: pratinjau, pita, kartu Jumlah,
  dan pembagian bongkar di riwayatModal harus berubah BERSAMA penahanan baris bal).

## Audit 39b no. 4 — sisa piutang negatif berbunyi; pembayaran bon di HP kasir tahan muat ulang (30 Sep 2026, cabang `audit/39b-piutang-negatif-berbunyi`)

Temuan PP-3: mesin beku `hitungPiutang` menghitung sisa = kredit + saldoAwal − bayar − dihapus dan BOLEH negatif (pembayaran melebihi sisa).
Semua pembaca menyaring sisa > 0 atau menjepit 0: nama bercap "lunas", hilang dari papan/katalog/Perlu perhatian, neraca turun hanya sebesar
sisa (kekayaan naik palsu), tutup buku melenyapkannya (saldo pembuka hanya sisa > 0). Sumber utamanya `kasir.html`: sisa sesudah membayar hanya
dikurangi di memori — muat ulang / katalog disegarkan = sisa lama kembali, bon yang sama bisa dibayar penuh lagi. Mesin TIDAK diubah.
- `inti/format.js`: SATU aturan untuk semua pembaca (berkas ini ikut di semua bundel uji) — `LEBIH_AMBANG` (−0,5 = tekor pemasok),
  `kalimatLebih` ("kelebihan bayar Rp X — uang pelanggan dipegang toko"), `lebihBayarDari(hitungPiutang(…))`. Kata sama dengan sisi
  pemasok/owner; "titipan" sudah berarti lain (titipan tablet, urusan titipan) — jangan dipakai.
- Pelanggan: status `lebih` (cap "kelebihan bayar" / "hapus buku terbayar") di `semuaBon`; tab Bon memajang pita + nama yang bisa diketuk (angka "sisa semuanya" TIDAK
  berubah); kepala lembar jujur + penjelasan (tidak bisa dibayar/dihapus lagi; nota Kredit berikutnya memakai kelebihannya lebih dulu; uang
  yang dikembalikan tunai belum punya catatan); bayar/hapus bon ditolak lebih dulu dengan kalimat benar; kartu orang (`lebih`), ringkasan
  kartu, pratinjau gabung nama memakai sisa BERTANDA (dulu kelebihan dijepit 0 → bon gabungan terlalu besar).
- Beranda Perlu perhatian, Menu (laci Pelanggan, jawaban piutang & kaya), Neraca (kalimat ikut `catatan` → semua kertas; layar: pita tersendiri,
  tetap tampil walau neraca ditolak karena stok minus; BUKAN `tolak`; objek `neracaPada` TETAP berbentuk sama dengan main — ASAP GLOBAL
  membandingkannya byte-sama; kalimat & daftarnya dari `lebihNeraca`, catatan layar dari `catatanLayarNeraca`), Kartu Piutang ("Kelebihan bayar" bukan "Sisa bon"), struk nota BON
  ("Kelebihan bayar <nama>" bukan "Sisa bon Rp0"), Jual (daftar nama, info Kredit), Tutup Buku (peringatan: kelebihan bayar TIDAK menyeberang
  tahun). Uji laporan menutup: kekayaan naik tepat sebesar kelebihan bayar yang disebut.
- `kasir.html` (v28): buku kecil `kasir_bayar_bon_v1` — tiap pembayaran bon tetap dikurangkan selama masih di antrean; sesudah sampai server
  selama katalog yang dipegang ditulis SEBELUM pembayaran diterima server (dua-duanya waktu server: `updateTime` GET katalog & jawaban PATCH);
  katalog yang ditulis sesudahnya → berhenti begitu sisa nama itu berubah / namanya hilang. Ditolak server = tidak dikurangkan. Pembersih 30 hari.
  Pilih nama dari daftar yang TERLIHAT (dulu nomor urut: katalog berganti tiap 2 menit → bisa jatuh ke orang lain); sisa dibaca ulang saat
  SIMPAN; lembar menyebut "daftar sisa dari sistem per jam" (tanpa ambang). Bentuk katalog TIDAK diubah (keputusan owner 27 Sep "bentuk tetap").
  Sisa celah (jarang): katalog yang ditulis beberapa detik sesudah pembayaran dari data yang belum memuatnya DAN sisa nama itu berubah karena
  catatan lain → pengurangan berhenti terlalu cepat. Jalan persisnya (katalog menyebut id pembayaran yang sudah dihitung) — DISETUJUI owner 30 Sep,
  dibangun di "Audit 39b · cara persis" (kasir v30).
- Versi kasir naik ke `kasir-v28` (sw-kasir.js, kedua berkas kasir, `KK_VERSI_KASIR_TERBARU`). `KK_VERSI_AMBIL_SENDIRI = 'kasir-v27'`: HP v27
  sudah mengambil katalog sendiri → Beranda cukup menyebut "versi kasir-v28 terpasang saat dibuka ulang" dan pemeriksaan katalog lamanya TETAP jalan.
- Uji: `uji_pelanggan_baru.py` +9 (dokumen bayar melebihi sisa DISUNTIK langsung, ambang −0,3 = lunas) + asap data toko (jumlah nama kelebihan
  bayar = sisa negatif mesin = tab Bon), `uji_ringkasan_baru.py` +2, `uji_menu_baru.py` +3, `uji_laporan_baru.py` +6, `uji_jual_baru.py` +3,
  `uji_katalog_kasir.py` +24 jsc (fungsi asli dipotong dari kasir.html: muat ulang, lunas lalu bayar lagi, waktu server, katalog berubah karena
  catatan lain, ditolak, pilih menurut nama, pagar, pembersih) + 2 statis + Beranda v27, `uji_antrean_kasir.py` +4 peramban (layar & klik
  sungguhan, muat ulang di Chrome yang sama). Kontrol baru: pelanggan 7, ringkasan 1, menu 2, laporan 4, jual 3, katalog kasir 13.
- Tinjauan independen 30 Sep (2 peninjau + penyanggah per temuan): 11 diajukan, 10 lolos, semua ditambal di cabang ini —
  B1 sisa di bawah nol DIPECAH (`pecahLebih`): `uang` = bayar melebihi semua bon (uang pelanggan; hanya ini yang menaikkan kekayaan & dicetak di
  struk) vs `hapus` = hapus buku yang ternyata dibayar juga (hapus bukunya yang perlu dibalik; jangan dikembalikan) — kalimat, cap, baris Perlu
  perhatian, Menu, Neraca, Kartu Piutang, Jual, Tutup Buku mengikuti; B2 Kartu Piutang: sisa di bawah nol di ATAS pilihan; B3 Menu Orang › Pembeli
  & cari nama menyebutnya; B4 tanpa titik kas kalimat neraca/"kaya" menyebut akibatnya nanti; B5 struk nota Kredit yang lahir sesudah kelebihan
  bayar: "BON — dibayar dari kelebihan bayar" + "Dari kelebihan bayar" (TOTAL menutup), nota lama tetap "belum dibayar"; B6 berita acara tutup
  buku memuat peringatannya; K1 pembayaran yang SUDAH pernah dikirim tidak lagi dijadikan pembanding selagi di antrean (jawaban PATCH bisa
  hilang padahal tersimpan) + waktu server = `createTime`; K2 katalog tanpa waktu server (kasir darurat menulis kunci bersama — kini ikut
  menyimpannya) tetap dikurangkan tapi bukan pembanding; K3 ditolak dibuang di `pindahKeDitolak`, arsip ditolak ikut dibaca; K5 LABEL_VERSI
  'versi 39b'. Gugur: K4 (penyimpanan penuh — `catatBayarBon` gagal diam; uangnya tetap tercatat, dampaknya kembali ke perilaku lama).

## Rapi isi ulang wadah (30 Sep 2026 malam, cabang `rapi/isi-ulang-sederhana`, di atas perbaikan `perbaikan/impor-takar-wadah`)

Owner 30 Sep: "tidak bisa klik ISI ULANG · CATAT 3 TAKAR … terlalu banyak tombol & tampilan … buat simple, jangan nambah pekerjaan". Penyebab tombol
diam: `jual-logika.js` memanggil `denganCacheSementara` tanpa impor (ditambal di `perbaikan/impor-takar-wadah` + `alat-uji/periksa_impor.py` di CI).
Rapi di sini TIDAK mengubah hitungan apa pun — hanya tampilan:
- `inti/dom.js` `delegasi`: penangan yang jatuh (galat / janji ditolak) mengirim peristiwa `galat-aksi`; `app.js` menampilkan pita merah di `#kabarNav`
  yang bertahan sampai diketuk ("Tombol tadi GAGAL dijalankan … periksa dulu apakah catatannya sudah masuk"). Tidak ada lagi tombol yang diam.
- `wadah-panel.js`: wadah aktif menampilkan SATU cara isi ulang sekaligus — "Karung / ½ / kg" (tiga ketukan, bawaan) atau "Serok takar · bisa campur"
  (− / + takar); pilihan terakhir diingat per perangkat (`miqbal_isi_ulang_cara_v1`). "Beras apa yang dituang" menampilkan karung di belakang dulu,
  tumpukan gudang terlipat di satu tombol "karung lain dari gudang". Kabar ketukan panel tampil tepat di bawah tombolnya (`kabarW`), kabar layar di
  atas tetap.
- `stok.js` rincian wadah: panel isi ulang paling atas; ganti nama, karung di belakang, buku per merek, karung sisihan terlipat di satu tombol
  (diingat per perangkat, `miqbal_rincian_wadah_lain_v1`); selisih catatan karung belakang tetap disebut satu baris di luar lipatan.
## Audit 39b no. 3 — uang QRIS selain penjualan ikut tutup hari; bayar bon di HP kasir memilih caranya sendiri (30 Sep 2026, cabang `audit/39b-bon-qris-tutup-hari`)

Temuan PP-2: mesin (pembantu `daftarGerakanKas`, `kantongBayar`) memasukkan pembayaran bon dan kasbon kembali lewat QRIS ke REKENING, tetapi tutup
hari (K5) hanya menghitung penjualan QRIS: rekap tidak memuatnya, langkah rekening menolak angka bank yang jujur ("lebih besar dari penjualan QRIS"),
potongan QRIS (MDR)-nya tidak pernah jadi biaya → titik kas rekening & laba lebih besar sebesar potongan itu. Di `kasir.html` cara bayar bon
MEWARISI tombol nota (`bayarAktif`) diam-diam: nota terakhir QRIS → uang bon yang diterima tunai tercatat QRIS. Laten: cadangan 29 Sep belum
memuat satu pun bayar bon QRIS. Mesin TIDAK diubah.
- `tutup-hari-logika.js` `ringkasHari`: "uang QRIS hari ini" = penjualan + bayar bon + kasbon kembali lewat QRIS (persis gerakan rekening mesin);
  kolom baru `qrisJual`, `qrisBon`, `qrisKasbon`; OMZET tetap penjualan saja (`tunai + qrisJual + kredit`); "bon dibayar tunai" tetap tanpa QRIS.
  Potongan dihitung PER TRANSAKSI (`trxId`/`grupNota` — satu pindai satu potongan; dulu per baris barang, nota banyak barang di atas batas bisa
  lolos tanpa potongan). Tiap baris QRIS membawa `jenis` & `ket` ("bayar bon <nama>", "kasbon kembali <nama>").
- Langkah rekening menerima angka bank sampai seluruh uang QRIS; penolakan menyebut rinciannya (penjualan + bayar bon + kasbon kembali).
  Rekap: baris "QRIS" = penjualan (bagian omzet), baris "Bon dibayar QRIS" / "Kasbon kembali QRIS" muncul hanya bila ada. Dokumen potongan tetap
  SATU (`mdr-<tanggal>`), keterangannya menyebut jumlah nota + bayar bon + kasbon kembali. Layar: baris QRIS menyebut asalnya.
- Pelanggan: kalimat pratinjau & sesudah bayar bon QRIS menyebut potongannya dicatat saat tutup hari.
- `kasir.html` (v29, 'versi 39b-3'): lembar utang punya tombol TUNAI/QRIS sendiri (`caraUtangAktif`, `pilihCaraUtang`), kembali ke TUNAI tiap kali
  nama dipilih; selain QRIS dibakukan Tunai (bayar bon tidak pernah Kredit). Versi kasir serentak v29; `KK_VERSI_AMBIL_SENDIRI` tetap v27.
- Uji: `uji_uang_baru.py` +13 (K5b: dua baris satu transaksi, bayar bon QRIS di atas batas + tunai, kasbon kembali QRIS; identitas "uang QRIS =
  gerakan rekening mesin"; angka bank diterima; rekap; satu dokumen potongan; titik kas · K5c: nota HP kasir ber-`grupNota` dengan baris Potongan
  harga minus, satu baris nota yang dirapikan) + asap data toko (per tanggal: uang QRIS tutup hari = gerakan rekening mesin + baris QRIS minus;
  asap kini juga membaca `_privat/`, cadangan terbaru menurut tanggal + akhiran unduhan), `uji_kendali_biaya.py` +1, `uji_katalog_kasir.py` +4 jsc
  (fungsi asli: nota QRIS → bon Tunai, ketuk QRIS, reset tiap nama, Kredit dibakukan) + 1 statis, `uji_antrean_kasir.py` +1 peramban (nota QRIS →
  tombol TUNAI menyala, masuk server Tunai), `uji_pelanggan_baru.py` +2. Kontrol baru: uang 10, kendali biaya 1, katalog kasir 5, antrean kasir 1, pelanggan 2.
- Tinjauan independen 30 Sep (2 peninjau + penyanggah per temuan): 11 diajukan, 10 lolos. Ditambal di cabang ini: T1 Kendali biaya "Potongan QRIS
  dari uang QRIS" — penyebut ikut bayar bon + kasbon kembali QRIS (dokumen potongan kini memuat potongannya; dulu rasio menggelembung); T5 baris hasil
  rapikan/rincian ikut transaksi nota ASALNYA (rantai `koreksiDari`, seperti `rtRantaiNota` mesin) — dulu satu pindai terpecah dua kelompok; T6 kalimat
  bayar bon (Pelanggan) bersyarat: hari yang SUDAH ditutup → "uang ini (dan potongan QRIS-nya) baru ikut hitungan kas kalau tutup hari diulang"
  (`kalimatBayarTutup`); T4/K2 komentar & asap jujur soal baris minus; T8 uji jalur `grupNota`; K1 pilihan cadangan asap; K3 DOM palsu = markup.
  Gugur: T7 (label "Dibayar pembeli lewat QRIS").
- Temuan samping (BELUM dibetulkan, dilaporkan ke owner): (A) baris rincian `rumusLaci` memakai aturan tempat uang yang beda dengan
  `saldoKantong`; (C, dibetulkan penjelasannya oleh tinjauan T2) tukar yang dibayar QRIS: baris pengganti ditulis HARGA PENUH ber-QRIS, kredit barang
  kembali jadi uang keluar LACI (retur `nominalRefund`) → uang QRIS tutup hari kebesaran sebesar kreditnya → potongan palsu sebesar itu bila angka bank
  dicocokkan; (D, T3) "Kirim WA"/"Cetak" untuk hari yang SUDAH ditutup sesudah layar dibuka ulang menyusun rekap dari draf kosong ("Laci dihitung:
  belum", langkah "tidak dikerjakan") — sudah ada sebelum cabang ini; (E, T4) baris Potongan harga HP kasir (`hargaTotal` minus) dibuang mesin beku dari
  kas → laci/rekening mesin = harga KOTOR: nota tunai berpotongan tampil "kurang" di laci, nota QRIS berpotongan membuat rekening sistem lebih besar
  dari bank (usul: kasir.html membagi potongan ke baris barang seperti Jual `/baru/`); (F, T6) catatan uang yang dicatat SESUDAH tutup hari di tanggal
  yang sama baru ikut kas bila tutup hari diulang sebelum jam 12 esoknya — sesudah itu tidak pernah (tertelan jadi selisih laci esok hari).

## Audit 39b no. 15 — Kartu Gudang: buku wadah & karung belakang ikut umur cocokkan (1 Okt 2026, cabang `audit/39b-kartu-gudang-buku-khusus`)

Temuan G: kartu keempat Gudang ("kapan terakhir dicocokkan") hanya membaca penyesuaian stok dan MELEWATI semua yang bagiannya 'wadah' (putaran 27:
cocokkan wadah cuma menghitung bagian merek itu di kotak, tumpukannya belum). Akibatnya buku KHUSUS — buku wadah, karung di belakang, karung sisihan —
yang justru dihitung UTUH oleh cocokkan wadah tidak pernah "dicocokkan": sesudah aktivasi 8 wadah ada 16 baris awas permanen. Cocokkan yang PAS juga
tidak menulis penyesuaian sama sekali. `stok-logika.js` `jwbCocok` (sisi baca saja):
- penyesuaian bagian 'wadah' atas buku khusus (`petaBukuWadah`) menyegarkan umurnya; atas merek biasa tetap tidak (aturan putaran 27);
- titik samakan isi (`wadahLiteran` tipe isi + `stokWadah`) & isi karung terbuka (tipe karungIsi atas buku khusus) bertanda `dariCocok` = hitungan fisik.
- Uji: `uji_wadah_satu_buku.py` +4 (sebelum, pas, bagian wadah buku khusus vs merek biasa, isi ulang biasa tidak dihitung). Kontrol baru 3.
- Tinjauan no. 15 menemukan kartu bisa padam padahal bukunya belum benar (cocokkan membanding catatan, bukan buku; karung kedua & karung
  sisihan tidak punya pintu hitung; buku wadah 0 membuang hitungan). Akarnya di cocokkan wadah = no. 5, ditambal di cabang yang sama (bagian berikut).

## Audit 39b no. 5 — Cocokkan › Wadah literan menghitung BUKU, semua karung berbuku punya baris (1 Okt 2026, cabang `audit/39b-kartu-gudang-buku-khusus`)

Temuan: karung di belakang wadah aktif punya buku sendiri (putaran 39), tetapi cocokkan wadah membandingnya dengan CATATAN kolam. Sesudah karung
"disamakan" (catatan diset, buku tidak), hitungan yang pas tidak pernah membetulkan bukunya — berputar. Satu wadah cuma satu karung yang bisa dihitung;
karung kedua dst., karung sisihan, dan kemasan adukan yang dibuka lepas tidak punya pintu hitung sama sekali. Buku wadah 0 / minus membuang hitungan isi.
- `stok-catat-logika.js` `barangCocok('wadah')`: karung terdepan yang berbuku sendiri → tercatat = buku di tempat itu (`ckBukuKarungDi`: buku − catatan
  kunci yang sama di tempat lain), catatannya disebut bila beda. Baris baru `karungKhusus|<kunci>|#|<tempat>` (`ckKarungKhusus`) untuk tiap karung berbuku
  di luar slot wadah (karung belakang kedua dst., karung sisihan, adukan lepas) bila buku ≠ 0 atau catatannya masih berisi — satu isian kg.
  Simpan: penyesuaian atas buku itu (bagian 'wadah', `wadah` = tempatnya) + catatan `karungIsi` bertanda `dariCocok` di tempat yang sama.
- Karung kedua dst. yang ditimbang / disamakan bertanda `diamSlot`: `karungUntukWadah` memakai catatan sebelumnya untuk urutan, jadi karung terdepan
  wadah itu tidak pindah (dulu menimbang karung kedua menjadikannya karung terdepan).
- `wbKomposisiBaru`: wadah berbuku sendiri dengan buku ≤ 0 → selisih tetap jatuh ke buku wadah (dulu alokasi kosong: "tidak ada buku yang berubah").
- Kembalikan karung berbuku memindah balik BUKU-nya (dulu sisa catatan — selisihnya tertinggal di buku karung yang sudah tidak ada); buku minus dipindah
  dari merek asal supaya 0. Hapus karung habis: buku minus dicatat LEBIH (ketukan kedua), sisa kecil ≤ 0,5 kg ikut dicatat tanpa ketukan kedua.
- Layar: baris karung menyebut merek asal (bukan kunci buku), "tercatat = bukunya", tombol simpan menyebut wadah + karung; hitungan karung wadah ikut
  dibersihkan dari draf sesudah simpan (dulu tertinggal dan tampil "cocok ✓").
- Kemasan adukan yang dibuka di belakang wadah BELUM aktif (tinjauan G5): tercatat karungnya = buku − bagiannya yang sudah dituang ke wadah itu; umurnya
  di kartu Gudang = yang paling lama di antara karungnya dan wadah-wadah pemegangnya (`stok-logika.js` `jwbCocok`).
- Uji: `uji_wadah_satu_buku.py` +8 (terdepan = buku, karung kedua + diamSlot + kartu Gudang, samakan kedua diamSlot, karung sisihan lepas, buku wadah 0,
  kembalikan = buku, hapus buku minus / sisa kecil, adukan di wadah belum aktif) + 1 statis layar; kontrol baru 10. Tinjauan independen no. 15
  (12 diajukan, 8 lolos) — semua yang lolos ditambal di sini. Di Browser pane atas salinan cadangan (8 wadah aktif) muncul dua
  karung kedua yang dulu tidak bisa dihitung, ditambah karung sisihan sesudah sisihkan 10 kg (SIMULASI).
- Tinjauan independen no. 5 (6 diajukan): H1 TINGGI — komentar `//` di tengah baris menelan `const al` di tombol simpan Cocokkan (ReferenceError sesudah
  dokumen tertulis); ditambal + pemeriksa CI baru `alat-uji/periksa_komentar.py` (komentar di tengah baris yang diikuti kode). H2 satu buku terbuka di dua
  tempat yang dihitung sekaligus: selisih buku−catatan dipotong sekali. H3 kolam yang sudah ditutup (dikembalikan / dihapus) tidak dapat baris; sisa
  bukunya di baris lepas (`kolamDitutup`). H5 baris karung memakai batas selisih % (bukan jatah susut wajar wadah per hari). H6 kalimat konfirmasi
  kembalikan menyebut buku yang dipindah. H4 (adukan di wadah BELUM aktif yang isinya tidak mengenal adukan → tercatat karung kelebihan) dicatat saja:
  hanya terjadi di wadah belum aktif. Uji +5, kontrol +4.
  Peninjau kedua (S1–S8): S1/S3/S4 = H1/H3/H2. S5 samakan karung kedua berbuku APA PUN (juga adukan) bertanda diamSlot. S6 umur buku adukan hanya dari
  timbang karungnya (bukan penyesuaian isi wadah yang kebagian adukan); titik ganti nama bukan hitungan. S7 hitungan minus ditolak, "cocok persis" tidak
  ditawarkan untuk buku minus. S8 (lama, akan kena saat owner mengaktifkan wadah): aktivasi menulis karung yang TADINYA terdepan paling akhir — dulu
  terdepan berganti menurut abjad. S2 (uji tak menjalankan tombol layar) dijawab `periksa_komentar.py` + bukti Browser pane. Uji +4, kontrol +4.
- Belum: karung bertanda `diamSlot` cuma dari cocokkan & samakan; jalur lain yang menulis `karungIsi` bertempat (isi ulang, cek) tetap memakai urutan
  lama. Susut wajar karung kedua memakai batas wadah yang sama (per hari sejak catatannya).

## Audit 39b · cara persis — katalog menyebut pembayaran bon yang sudah dihitung (30 Sep 2026, cabang `audit/39b-katalog-bayar-bon-persis`)

Keputusan owner 30 Sep ("cara persis") atas celah sisa no. 4: buku kecil `kasir_bayar_bon_v1` di HP kasir menebak kapan katalog sudah menghitung
pembayarannya (waktu server + sisa nama berubah) — tebakan meleset bila sisa nama itu berubah karena catatan lain (berhenti terlalu cepat) atau
kebetulan kembali sama (dikurangi dua kali). Mesin TIDAK diubah.
- `data/katalog-kasir.js`: dua kunci terakhir dokumen — `bayarBonTerhitung` (`kkBayarTerhitung`) = id SEMUA piutangMutasi tipe bayar yang dihitung
  `hitungPiutang()` (bernama, persis saringannya), TANPA jendela hari, diurutkan; `bayarBonSejak` (`kkBayarSejak`) = 1 Januari sesudah tahun terakhir
  yang ditutup (saldo pembuka piutang bertanda tutupBuku + tahunDari; '' bila belum pernah). Isinya murni dari DATA — tidak bergantung jam perangkat
  penerbit (dua perangkat owner menyusun katalog yang sama). Ikut di `kkIsi`, `kkDokumen`, `kkKanon`. Empat bagian lain tetap byte-sama index.html.
  Rules `ringkasanKasir` tidak membatasi kolom (tanpa ubah rules). Ukuran: ±600 id/tahun (±12 KB), tutup buku mengosongkannya lagi.
- `kasir.html` (v30, 'versi 39b-4p'): katalog BERDAFTAR → id tercantum = sudah dihitung → catatan dibuang; sudah sampai server & bertanggal (buku
  kecil kini menyimpan `tanggal`, catatan lama: dari `dibuat`) sebelum `bayarBonSejak` = terserap saldo pembuka tutup buku → dibuang; selain itu tetap
  dikurangkan. Katalog tanpa daftar (penerbit lama / salinan kasir darurat lama) → tebakan waktu server no. 4 tetap. Versi kasir serentak v30.
- Tinjauan independen 30 Sep (2 peninjau + penyanggah): 7 diajukan, 6 lolos, semua ditambal di cabang ini — P1/K1 tutup buku mengarsipkan dokumen
  bayar (id hilang dari daftar, pembayaran sudah terserap saldo pembuka → HP mengurangi dua kali) → `bayarBonSejak`; P2/K2 jendela 45 hari memakai
  tanggal dari jam HP & jam penerbit → jendela dicabut; P3/K3 isi katalog bergantung tanggal perangkat penerbit → isi murni dari data (uji: jam
  penerbit dimajukan 400 hari → katalog sama). Gugur: K4 (bentuk id pecahan — kini tetap diuji).
- Uji: `uji_katalog_kasir.py` +6 /baru/ (tanpa jendela, id pecahan, tanpa nama, hapus buku, saldo awal, jam penerbit, tanda awal buku, pembanding) +
  9 jsc kasir (S18: sisa berubah karena bon lain, sisa kebetulan sama, masih di antrean, tanpa daftar · S19: tanggal di buku kecil, awal buku sebelum
  & sesudah sampai server, catatan lama tanpa tanggal), `uji_antrean_kasir.py` +2 peramban (layar & klik sungguhan); `uji_arsip_produk.py` &
  `uji_wadah_stok_sendiri.py` membandingkan katalog tanpa dua kunci baru. Kontrol baru: katalog kasir 11, antrean kasir 1.

## Audit 39b no. 6 — ganti nama wadah aktif memindah buku karung di belakang (1 Okt 2026, cabang `audit/39b-ganti-nama-karung-belakang`)

Temuan G: `wbSusunGantiNama` memindah buku wadah & karung sisihan ke nama baru, tetapi buku "Karung belakang <lama> · merek" (putaran 39) tertinggal
yatim → karung di belakang nama baru terbaca kosong dan isi ulang berikutnya membuka karung BARU dari tumpukan gudang (tumpukan turun tanpa karung
diambil, dua buku untuk satu karung fisik). Tambalan: tiap buku karung belakang → lahir "Karung belakang <baru> · merek" + pindah buku (modal ikut);
kolam catatannya pindah bernama kunci baru di belakang wadah baru, kolam lama dinolkan; karung yang berdiri ditulis terakhir supaya tetap berdiri;
buku karung belakang MINUS → ganti nama ditolak (samakan dulu). Uji `uji_wadah_satu_buku.py` +3 (pindah & tumpukan/nilai tetap, isi ulang tidak
membuka karung baru, minus ditolak). Kontrol baru 2.
- Tambahan 1 Okt: kolam lama dinolkan DI TEMPATNYA (di belakang nama lama; dulu ditulis lepas → 4 karung hantu "dulu di belakang wadah <lama>" di
  deretan & cocokkan). Titik samakan nama baru membawa komposisi turunan (`wbKomposisiTurunanKg`) — dulu nama baru "belum ada isi ulang tercatat".
  Uji +2, kontrol +2.

## Audit 39b no. 16 — cocokkan wadah aktif tidak memutus komposisi turunan (1 Okt 2026, cabang `audit/39b-ganti-nama-karung-belakang`)

Temuan: komposisi isi wadah aktif (merek asal, "Kumala 3 : NG 2") diturunkan dari riwayat isi ulang sejak titik samakan terakhir. Cocokkan wadah
menulis titik samakan baru TANPA komposisi → chip Jual, kartu Stok, panel wadah tampil "belum ada isi ulang tercatat", lalu 100 % merek isi ulang
berikutnya. Buku tidak tersentuh. Tambalan: `ccSimpanWadah` (wadah berbuku sendiri) membawa `komposisi` = komposisi turunan sekarang disebar ke
hitungan (Σ persis). Uji `uji_wadah_satu_buku.py` +1 (banding sama sesudah cocokkan; isi ulang NG sesudahnya menambah bagian NG, tidak jadi 100 %),
kontrol +1.

## Audit 39b no. 7 — takar dari karung sisihan / kemasan adukan yang kosong tidak membuka "karung otomatis" (1 Okt 2026, cabang `audit/39b-takar-buku-khusus`)

Temuan: panel − / + takar (`jual-logika.js` `hitungTakar` → `susunTakarWadah`) membuka karung baru "otomatis" bila karung sumbernya kurang. Untuk karung
berbuku sendiri yang BUKAN karung belakang — karung sisihan wadah, kemasan adukan yang dibuka — tidak ada tumpukan di belakangnya: karung hantu itu
ditulis tanpa buku, takarnya lalu memindah buku khusus jadi minus (adukan: stok kemasan tetap, jadi lebih 1 unit). Belum pernah terjadi di data.
Tambalan: sumber berjenis karung sisihan / adukan tidak pernah dibuka otomatis; kosong / belum ditandai → `habisKhusus` dan catat DITOLAK dengan
kalimat (adukan: buka satu kemasan lagi dulu). Masih berisi tapi kurang → seadanya (39c) seperti biasa. Panel menyebut "KOSONG". Uji
`uji_wadah_satu_buku.py` +1 (+1 statis layar), kontrol +1.

## Audit 39b no. 26 — deretan panel − / + sepakat dengan 8 slot Stok (1 Okt 2026, cabang `audit/39b-deretan-jual-sepakat`)

Temuan: sesudah 39c, layar Stok menggambar deretan sebagai satu slot per wadah (kosong = "?"), tetapi panel isi ulang − / + (Jual & rincian wadah)
masih memakai `deretanKarung()` mentah: slot KOSONG tampil sebagai karung "±0 kg" bernama wadahnya (nama kelas), dan ketukannya menyiapkan buka karung
atas nama itu (dijaga ketukan kedua). Tambalan: `wadah-panel.js` menyaring slot yang tidak tercatat (`!k.no || k.dicatat`) — deretan panel = slot berisi
+ karung lepas, sama dengan Stok. Uji `uji_wadah_satu_buku.py` +1 (+1 statis layar).

## Audit 39b no. 14 — tanda "jual dulu, tandai untuk dicocokkan" tidak dihitung ganda (1 Okt 2026, cabang `audit/39b-selisih-tembus-ganda`)

Temuan (J3 + J4): (J3) dua baris keranjang dari satu buku sama-sama melampaui — tiap baris dibanding buku dikurangi baris LAIN, jadi kekurangan
50 kg ditagih 50 + 50. (J4) literan dari wadah BELUM aktif yang campuran dipecah ke merek asal; tanda & `selisihKg` penuh disalin ke tiap merek asal —
pita Jual & kartu Gudang menagih merek yang bukunya tidak kurang. Buku & uang tidak terpengaruh (tanda saja).
- `jual-logika.js` `barisTembus`: kekurangan dibagi SEKALI — baris sebelumnya memakai buku lebih dulu (`maksSebelum`), baris tanpa sisa kekurangan tidak
  ditandai; kalimat pemeriksaan ulang tetap sama (dari langit-langit tanpa baris itu). Pita "jual dulu" & kabar hanya menyebut yang kurang.
- `pecahItemsWadah`: kekurangan literan campuran jatuh ke merek asal yang bagiannya melebihi buku yang tersisa (Σ = kekurangan baris); tidak ada
  yang kurang di buku → merek yang bukunya paling tipis. Merek lain tanpa tanda.
- Uji: `uji_jual_tandai_cocok.py` +2 (kontrol +2), `uji_wadah_satu_buku.py` +1 (kontrol +1).
- Tinjauan independen (10 diajukan, 9 lolos): T1 kekurangan literan campuran = kekurangan BUKU merek (tidak dibesarkan ke selisih liter wadah); T2 pita &
  kalimat "jual dulu" menyebut merek yang bukunya kurang (`kurangPecahan`), bukan pecahan pertama; T3 riwayat / struk yang menggabung satu takaran membawa
  tanda dari pecahan mana pun (`gabungTakaran`); T5 kabar sesudah simpan menyebut tanda tembus (dulu ditimpa); T6 uji lewat jalur nyata (keranjang →
  simpanNota). T4 (tanda karung dibulatkan ke ½ karung — sejak 31b, tanda saja) dicatat, belum dibetulkan. Uji +1, kontrol +2.
- No. 6/7 dari tinjauan yang sama: W1 ganti nama tidak menghidupkan kolam karung yang sudah ditutup; W2 urutan karung di nama baru = urutan buka (catatan
  diamSlot tidak dihitung); W4 panel kemasan adukan kosong menyarankan buka kemasan lagi, tombol CATAT redup.

## Audit 39b no. 8 — struk nota bayar sebagian menyebut uang yang diterima (30 Sep 2026, cabang `audit/39b-struk-bayar-sebagian`)

Temuan J1: uang kurang saat bayar → semua baris nota jadi Kredit (`uangDiterima` tidak ditulis) + satu pelunasan piutang sebesar uang yang diterima
(index.html menulis bentuk yang sama). Struknya berbunyi "BON — belum dibayar", uang yang diterima tidak tercetak, dan "Sisa bon" = saldo saat struk
disusun tanpa tanggal — struk yang dicetak ulang bisa memuat "belum dibayar" dan "Sisa bon Rp0" sekaligus.
- `jual-logika.js` `susunNotaDokumen`: pelunasan saat beli membawa `notaTrxId` (= trxId nota). Kolom baru; mesin piutang (beku) tidak membacanya.
- `struk-logika.js` `bayarSaatBeli(nota)`: tautan `notaTrxId`; pelunasan lama (index.html & /baru/ sebelum 30 Sep) dicocokkan dari tanggal + jam + nama +
  catatan "Dibayar langsung saat beli — sisa … jadi piutang" DAN angka yang menutup (dibayar + sisa di catatan = TOTAL nota); calon ≠ 1 → tidak ditebak.
  `susunStruk`: "BON — sebagian dibayar", "Dibayar saat beli", "Sisa nota ini" (TOTAL = dibayar + sisa), dan baris "per <tanggal struk disusun>" di bawah
  "Sisa bon" (`pilih.kini`, bawaan hari ini).
- Uji: `uji_jual_baru.py` +7 pemeriksaan (S8: tautan, bunyi struk, hitungan menutup, WA, pelunasan lama, nota bon murni di menit yang sama, nota tunai),
  asap data toko (tiap pelunasan saat beli di cadangan terbaru: uang tercetak, menutup ke TOTAL, tidak ada yang masih "belum dibayar"), +7 kontrol.
- Tinjauan independen 30 Sep (peninjau + penyanggah): (1) Pusat Dokumen › Nota (`laporan-logika.js` `dokumenKecil`) hanya memakai baris struk
  yang berangka, jadi baris "per <tanggal>" terbuang di jalur cetak ulang/PDF. Kini baris "Sisa bon" membawa `sisaBonPer` dan labelnya di Dokumen
  berbunyi "Sisa bon X · per <tanggal dokumen disusun>" (`susunStruk(..., { kini: iso })`). (2) Uji S8 dulu hanya menjaga 2 dari 5 syarat pencocokan data
  lama dan "menutup" dihitung dari rumusnya sendiri: kini 4 umpan (beda tanggal / jam / catatan / bertautan) + 4 kontrol, dan "menutup" dibaca dari
  angka yang TERCETAK (juga di asap). `uji_laporan_baru.py` +1 pemeriksaan + 1 kontrol.
  Lembar struk Jual & WA otomatis memberi `kini` = jam layar, jadi di mode cadangan "per" = tanggal cadangan, sama dengan Pusat Dokumen.

## Audit 39b no. 35 — merek per liter / kelas sendiri tanpa buku per ukuran (30 Sep 2026, cabang `audit/39b-ketan-buku-ukuran`)

Keputusan owner 30 Sep ("kecualikan merek literan/kelas sendiri dari buku per ukuran"). Dasar: temuan hulu H1 (`docs/audit-39b-temuan.md` no. 35) — karung
25 kg Ketan Hitam PK terjebak di buku "Ketan Hitam PK 25 kg" (tanpa jalur jual liter & HP kasir), induknya tinggal beberapa kg.
- `stok-catat-logika.js` `ckTanpaBukuUkuran()` = merek literan langsung (`wbLiteranLangsung`) + kelas sendiri (`kmKelasSendiri`). `hitungMasuk` tidak lagi
  mengarahkan karung 25 kg merek itu ke buku per ukuran (masuk buku induk seperti dulu); `ckCalonPisahUkuran` tidak menawarkannya.
- Buku per ukuran yang terlanjur lahir untuk merek itu → kartu "Gabungkan buku karung 25 kg ke induknya" di Stok › Cocokkan › Tumpukan gudang
  (`ckCalonGabungUkuran` / `ckSusunGabungUkuran`, owner, dua ketukan): SATU pindah buku seluruh isinya → induk, modal ikut, laba & neraca tetap, bertanda
  `gabungUkuran` — bukan cocokkan. `toko.js` `ukuranDigabung()`; `indukTerpisah()` tidak menghitung buku yang sudah digabung, jadi rak, retur, dan katalog
  HP kasir memperlakukan induknya satu buku lagi. Buku per ukuran yang kosong tetap buku khusus (tidak muncul sebagai merek).
- Uji: `uji_buku_ukuran.py` +11 pemeriksaan, asap data toko (gabung balik Ketan Hitam PK 25 kg 25 kg → induk: nilai stok & laba byte-sama, tidak ada induk yang
  masih terpisah), +5 kontrol. Tugas owner sesudah merge: tekan "gabungkan" untuk Ketan Hitam PK 25 kg.

## Audit 39b no. 43 — petunjuk satu ketukan di Barang masuk (30 Sep 2026, cabang `audit/39b-induk-varian-petunjuk`)

Keputusan owner 30 Sep ("petunjuk satu ketukan"). Temuan hulu H8: koreksi kedatangan 28 Sep mengganti nama baris TH, SR, HSj, SB, II, MTJ menjadi nama
variannya ("TH · House" dst.); kedatangan berikutnya yang diketik sesuai tulisan karung ("TH") lahir sebagai buku BARU terpisah tanpa petunjuk.
- `stok-catat-logika.js` `ckSaranVarian(nama)`: nama tanpa " · " yang belum berbuku padahal ada varian berbuku / berkatalog berinduk nama itu → daftar varian
  (yang bukunya paling berisi dulu; huruf besar/kecil & spasi tidak dibedakan; arsip, buku khusus wadah, dan buku per ukuran tidak ditawarkan).
  `hitungMasuk` membawa `saranVarian` per baris (baris baru saja, bukan koreksi).
- `stok.js` Barang masuk: pita emas "TH sudah dicatat sebagai TH · House — pakai itu?" dengan tombol "pakai TH · House · buku … kg" (`mPakaiVarian`: baris
  diganti ke nama varian, jawaban kelas/varian lama dibuang). Bukan penolakan — kalau memang barang lain, baris tetap jadi nama baru.
- Uji: `uji_varian_merek.py` +3 pemeriksaan, asap data toko (keenam nama mendapat saran variannya), +3 kontrol, +1 pemeriksaan statis `periksa43`
  (pita & aksi ada; `KG` di `gambarMasuk` sudah membawa " kg", jadi tombol tidak boleh menambah " kg" lagi — screenshot 30 Sep menangkap "buku 750 kg kg")
  dengan 2 kontrol statis. Tampilan: `stok.css` `[data-k^="msv-pil-"]` flex — grid tiga kolom Stok memecah tombol jadi empat baris di HP 375.
- Tinjauan independen 30 Sep (peninjau + penyanggah): nama yang SAMA kecuali huruf/spasi ("kumala" padahal bukunya "Kumala") dulu hanya ditawari
  VARIANNYA — satu ketukan memasukkan karung biasa ke buku varian. Kini buku aslinya ikut ditawarkan dan selalu paling depan (juga "th · house" → "TH · House").
  Kontrol penyaring dipecah tiga (arsip / buku khusus wadah / buku per ukuran, masing-masing punya contoh di kotak pasir) + kontrol spasi ganda,
  "beda huruf tidak ditawarkan", "tidak paling depan"; asap data toko: tiap nama berbuku yang diketik huruf kecil → buku aslinya paling depan.

## Struktur
```
baru/
  index.html            cangkang: nav bawah (HP/Tablet), menu samping (Mac), formulir masuk, <main id="layar">
  css/identitas.css     token C1 (kaca buram emas/sampanye/platina, Bodoni Moda + Jost, body / body.gelap) + komponen dasar
  css/kerangka.css      SATU markup tiga lebar: HP < 720 · Tablet 720–1099 · Mac ≥ 1100
  css/jual.css          bagian khas layar Jual (ringkasan/stok/pelanggan/menu.css: layar lain)
  js/app.js             pintu masuk: mode, sumber data (Firestore / ?cadangan=), masuk, nav
  js/inti/{format,dom,keadaan}.js   pemformat, penggambar (escape + delegasi data-aksi), penyimpan keadaan
  js/data/koleksi.js    tabel koleksi (28 lama + baru milik sistem baru) + kolom pengurut; `batas` = hanya N terbaru dibaca (logAktivitas)
  js/data/toko.js       cache di memori + ambil*() (nama = index.html) + keranjang aktif/parkir
  js/data/firebase.js   Firestore (baca + writeBatch), cache tetap IndexedDB, antrean hasPendingWrites, denyut perangkatStatus, atribusi oleh/lokasi per perangkat
  js/data/cadangan.js   sumber pengganti: berkas backup-batch-*.json (lokal, tidak di repo)
  js/data/katalog-kasir.js   katalog HP kasir (ringkasanKasir): isi, bentuk, pembanding, gerbang terbit, Beranda (25c)
  js/mesin/beku.js      26 dari 28 MESIN UANG BEKU — DIBUAT ALAT (alat-uji/pindah_mesin.py), byte-identik, JANGAN DISUNTING
  js/mesin/pembantu.js  fungsi & konstanta pembantu mesin — DIBUAT ALAT juga
  js/layar/jual-logika.js   logika Jual tanpa DOM (diuji di jsc); wadah-jual-logika.js (wadah dijual, harga jual wadah), struk-logika.js (struk kertas/WA + aturan otomatis)
  js/layar/jual.js          gambar & ketukan
  js/layar/wadah-panel.js   panel isi ulang wadah bersama Jual & Stok (takar demi takar sejak putaran 8; 39: tiga ketukan, kepala buku, pita tandai)
  js/layar/stok-logika.js, stok-catat-logika.js (ST1/ST3), stok-adukan-logika.js (ST2), stok-karantina-logika.js, stok-kantong-logika.js (ST4), stok-tempat-logika.js (ST5), stok-hpp-logika.js (ST6)   logika Stok tanpa DOM
  js/layar/wadah-bernama-logika.js (komposisi wadah per merek asal, literan langsung, ganti nama wadah; putaran 28: stok wadah sendiri, pindahan awal, katalog kasir; putaran 39: karung belakang = buku sendiri, isi ulang tiga ketukan, aktivasi per wadah, komposisi turunan, cek wadah, selisih dua angka) · varian-logika.js · arsip-logika.js · setengah-logika.js   putaran 27, tanpa DOM
  js/layar/stok.js          gambar & ketukan layar Stok
  js/layar/pelanggan-logika.js (Kenali + THR), bon-logika.js (Bon)   logika Pelanggan tanpa DOM
  js/layar/pelanggan.js     gambar & ketukan layar Pelanggan
  js/layar/menu-logika.js (laci N1, pita jam, tanya, jam, orang, tertutup, cari), sistem-logika.js (SS1–SS5)   logika Menu & Sistem tanpa DOM
  js/layar/menu.js          gambar & ketukan layar Menu + lembar Sistem
  js/layar/harga-logika.js (katalog H1), bon-pemasok-logika.js (H2), belanja-logika.js (H3)   logika Harga & Pemasok tanpa DOM
  js/layar/harga.js         gambar & ketukan layar Harga & Pemasok (tiga keluarga, tiga lebar)
  js/layar/uang-logika.js   UANG bersama (saldo per tempat uang) + K1 Uang keluar + K4 Pindah uang (tanpa DOM)
  js/layar/upah-logika.js   K2 Orang & upah · owner-toko-logika.js K3 · tutup-hari-logika.js K5 · tutup-buku-logika.js K6 (tanpa DOM)
  js/layar/uang.js          gambar & ketukan layar Uang (enam keluarga, tiga lebar)
  js/layar/laporan-logika.js, pajak-logika.js, kendali-biaya-logika.js (38: jenis · anggaran · lampu · pemicu · impas · pareto)   logika Laporan tanpa DOM
  js/layar/laporan.js       gambar & ketukan layar Laporan (Laba · Biaya · Harian · Mingguan · Bulanan · Pajak · Tahunan · Neraca · Dokumen · Setelan)
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
| `alat-uji/uji_jual_baru.py` (+ `--kontrol`) | 338 skenario logika Jual (baca + catat + batalkan + repack/bonus/pengganti retur/pesanan + retur & tukar + tata letak + wadah literan: takar, karung bernama di belakang, campuran, susunan, rantai stok & pindah nama + WADAH DIJUAL: rak berharga, buku kantong, modal/tanpa modal, hasil samping, repack dijual/ditanggung/upah, atur harga + STRUK: kertas 58/80, WA, menutup, bon, aturan otomatis, setelan) di kotak pasir; 154 kontrol positif berbunyi; kunci dokumen vs baris nyata & vs yang ditulis index.html |
| `alat-uji/uji_ringkasan_baru.py` (+ `--kontrol`) | 28 skenario logika Ringkasan (jam tetap, zona waktu dikunci WIB) + 14 kontrol; di cadangan toko: omzet hari/bulan/tahun = jumlah langsung barisnya |
| `alat-uji/uji_stok_baru.py` (+ `--kontrol`) | 135 skenario logika Stok (jam & zona waktu dikunci; rantai stok "Berasnya ada di mana?", karung bernama; barang masuk, cocokkan, adukan, karantina; kantong, tempat simpan, HPP: replika rumus = mesin, koreksi = batch yang sama, massal semua-atau-tidak) + 91 kontrol; di cadangan toko: nilai stok layar = mesin neraca, kolom dokumen catat dikenal cadangan, replika HPP = mesin untuk semua nama |
| `alat-uji/uji_pelanggan_baru.py` (+ `--kontrol`) | 57 skenario logika Pelanggan (jam dikunci penuh — `new Date()` pun; orang, wajah, tampah, belanja, jam, minggu, benang, hafalan, kartu, gabung, atur, THR, bon, tagih, bayar, hapus buku, hapus nama, 23b ciri dicabut & Bersihkan) + 56 kontrol; di cadangan toko: kunjungan/belanja/sisa bon = baris nyata & mesin, kolom dokumen dikenal, pratinjau Bersihkan + suntikan byte-sama |
| `alat-uji/uji_menu_baru.py` (+ `--kontrol`) | 53 skenario logika Menu & Sistem (tempo bon per pemasok sejak putaran 17) (jam dikunci penuh; silang jam, laci, tanya, jam, orang, tertutup, cari; perangkat, jejak, peran, persetujuan, cadangan, lokasi & pindah stok, pengingat, atur) + 32 kontrol; di cadangan toko: laci pemasok/piutang = mesin, pita = silang, berkas cadangan memuat semua koleksi lama |
| `alat-uji/uji_harga_baru.py` (+ `--kontrol`) | 105 skenario logika Harga & Pemasok (jam dikunci; katalog: baris, status, draf, pasar, sengaja, usul, kalimat, dampak, belah, papan/WA, terbit satu batch, label; bon: mesin beku, tempo kartu/umum, tusukan, garis & kas, buku, bayar + admin, urung, bon lama, kartu, atur; belanja: saran, sumber harga, truk, penuhi, kertas, pesanan WA, datang/batal, atur) + 47 kontrol; di cadangan toko: tiap dokumen katalog = satu baris dengan angka yang sama (harga milik nama yang diarsipkan dihitung terpisah), total bon = mesin, hari habis = mesin, kolom dokumen dikenal |
| `alat-uji/uji_laporan_baru.py` (+ `--kontrol`) | 67 skenario logika Laporan & Dokumen (+ Mingguan & Tahunan) (laba bulan = mesin, tunai = bersih − margin bon, MDR dipisah, tangga menutup; rekap hari = arus kas, teks WA; enam bulan, inti, rekap omzet: kumulatif, tanda lapor hanya final, tarif/batas/tanggal owner, bukti Σ; neraca dua sisi + aset tetap + pembanding; identitas berversi + struk ikut, ragam kop, nomor awal; laporan berkop DRAF/final, arus kas = kasPada, paket bank hanya final, banding; dokumen kecil lima jenis, salinan ke-N, nota batal ditolak; kop belum lengkap menolak semua) + 33 kontrol (NPWP bawaan tidak dicetak, peringatan NIK); di cadangan toko: laba bulan & laba-rugi berkop = mesin, neraca seimbang |
| `alat-uji/uji_uang_baru.py` (+ `--kontrol`) | 129 skenario logika Uang (+ HR, gaji tengah bulan, bonus) (saldo per tempat = kasPada di tiap langkah; K1 arti/penjaga/kasbon owner/titipan/tagihan; K4 pindah + admin + rutin; K2 sejak terakhir dibayar, hari kosong, bayar = baris bertanggal + 'Dipotong upah' + slip; K3 delapan perbuatan; K5 hitung laci, QRIS/MDR, sisih, timbang, amankan, tutup sekaligus, tutup ulang; K6 gerbang, 12 baris sebelum/sesudah, pembuka = sistem lama, kunci + arsip, batal, selesai) + 40 kontrol; di cadangan toko: identitas kantong (bila titik ada), posisi owner, karyawan, tagihan |
| `alat-uji/uji_akses_baru.py` (+ `--kontrol`) | 33 skenario akses per orang (keadaan akun, owner hanya via email, pendengar/layar/tombol per peran, penjaga kiriman = peta, pagar 18, batas per akun, atribusi olehUid, satu jejak per kiriman, salinan antre, SS2 akun & kisi = kebenaran server, tirai 8 layar, ganti orang & isian tujuh layar, pil akun, sambungan firebase.js/app.js diperiksa sumbernya) + 43 kontrol |
| `alat-uji/uji_layar_kunci.py` (+ `--kontrol`) | Chrome headless: (1) tirai — sebelum masuk 0 angka rupiah, 0 kartu, semua `<main>` kosong walau penyimpanan lokal berisi titik kas contoh; (2) ganti orang — Firebase palsu lokal, keranjang tidak terbawa ke akun berikutnya (Keluar lewat pil ditanya, tab lain, akun nonaktif), tirai menyembunyikan pil OWNER/nama, lembar akun & status jaringan; (3) isian lokal tujuh layar ikut pola keranjang, draf katalog harga di server utuh; (4) GAGAL JARINGAN ≠ GAGAL UJI; 19 kontrol (satu per layar) |
| `alat-uji/uji_isian_lokal.py` (+ `--kontrol`) | statis: 85 kolom ketik di 8 layar menulis ke kunci yang dijaga penjaga isian atau tercatat sengaja bukan isian; tiap kunci localStorage layar = draf yang dijaga atau tercatat bukan draf; 7 kontrol |
| `alat-uji/periksa_rules.py` (+ `--kontrol`) | `firestore.rules` v5 statis (putaran 39: `stafBuatWadah` & `stafBuatLahir` masuk daftar fungsi jujur, daftar peran `wadahLiteran`/`batchMasuk` = `BUAT_STAF`; putaran 25: tanpa payung/match rekursif, kunci periode di tiap koleksi bertanggal = `kunci-periode.js`, satu get() kunci per operasi, tenggang minimal = klien) + v3: blok per koleksi, owner & kasir via email, tanpa `masuk()` telanjang, jalur kasir@ utuh, tulis bukan-owner wajib uid, tanpa delete bukan-owner, payung owner yang TIDAK mengalahkan batasan owner (blok yang membatasi owner wajib dikecualikan; dihitung dari rules, bukan daftar tangan), daftar peran = `akses.js`, jejak ≤ 17 dokumen = pagar `akses.js` + 23 kontrol |
| `alat-uji/peta_akses.py --kiriman` (+ `--kontrol`) | access call TERBURUK per jenis kiriman bukan-owner (nota ben/karyawan, adukan, terima bon, pelanggan baru, struk; 39: isi ulang wadah ½ karung 6 / 20 & cek tutup toko, tiga kiriman terlarang wajib ditolak di perangkat) dari fungsi asli di jsc, lewat `periksaKiriman` asli; gagal bila > 18; tiap tindakan yang dibuka server wajib terhitung; layar wajib menyerahkan batasnya + 12 kontrol |
| `alat-uji/uji_pajak_baru.py` (+ `--kontrol`) | 43 skenario modul pajak (batas bebas di tengah bulan, omzet luar tanpa hitung ganda, kosong ≠ nol, badan tanpa angka, setoran & angka berubah, kurang/lebih, lewat tempo, ambang 70/85/95/100 + proyeksi, regresi penulis rekapOmzet, DK3 = layar Pajak, tanpa NIK/NPWP, status pasangan PH/MT/satu kesatuan/belum diketahui, dua angka omzet) + 29 kontrol; di cadangan toko: omzet layar Pajak = mesin laba = DK3 |
| `alat-uji/uji_kunci_periode.py` (+ `--kontrol`) | 45 skenario kunci periode (WIB & tenggang 3 hari, tiap ⛔, hari tanpa tutup, kunci/buka satu langkah, pembalik hari ini, keputusan K1–K6, penjaga pusat & kirim bertahap, final bulanan, pajak) + 39 kontrol; di cadangan toko: kunci Agustus → Juli & Agustus byte-sama, satu retur hari ini mengubah September saja |
| `alat-uji/uji_tutup_buku_bertahap.py` (+ `--kontrol`) | tutup buku bertahap: 40 nama → 3 kiriman ≤ 18, berita acara berjalan di kiriman 1 & penanda di kiriman terakhir, tahun lama utuh sampai penanda (era, FINAL, piutang tidak dobel), putus di kiriman 2 → lanjut tanpa kirim ulang, arsip terputus → lanjut, batal (dari berjalan / terkunci / terputus) per ≤ 18, titik kas tahun dari tutup hari 31 Des, periksa ulang hari ini (penjualan 1 Jan), langkah 7 tahun terkunci; 4 statis uang.js; 17 kontrol; asap data toko 5 Jan 2027 |
| `alat-uji/peta_akses.py --kiriman` bagian owner | kiriman owner yang menyentuh bulan lampau, dua keadaan (tanpa kunci / Agustus terkunci), fungsi asli ≤ 18 pemeriksaan kunci; tiap penulis koleksi bertanggal wajib terdaftar — 25 DIUKUR (semua yang ber-perulangan: nota 40 baris, batal nota, ini dia, cocokkan, tutup hari, tutup buku & batalnya, arsip per 18), 20 beralasan (jumlah dokumen tetap); arsip dipotong `KP_BATAS_GET`; kasir*.html 1 dokumen per permintaan |
| `alat-uji/uji_antrean_kasir.py` (+ `--kontrol`, `--gambar DIR`) | 25b: kasir darurat & kasir.html di Chrome headless + Firestore palsu — karcis ke-2 dari 5 ditolak (sisanya masuk), 401, sinyal/429/503, belum masuk, denyut & versi, tahan muat ulang; statis versi kembar; /baru/ ⛔ versi & Perlu perhatian |
| `alat-uji/uji_sistem_lama_bacasaja.py` (+ `--kontrol`) | 25b: index.html hanya-baca — statis (tiap setDoc/deleteDoc/runTransaction berpenjaga, yang terbuka persis keputusan owner) + Chrome headless dengan Firebase palsu (antrean lama sekali, 35 koleksi ditolak, tombol sungguhan, pulihkan, baca riwayat) |
| `alat-uji/uji_bayar_bon_terkunci.py` (+ `--kontrol`) | 25b C: bayar bon pemasok/pelanggan dari bulan terkunci lolos — teks rules dicocokkan + model + jalur sistem baru; asap data toko lokal |
| `alat-uji/uji_batal_karcis.py` (+ `--kontrol`) | 25b: batal karcis kasir darurat di /baru/ — field = `mulaiBatalkanTrx` (dibaca dari index.html) & dokumen pembatalan sungguhan di cadangan lokal |
| `alat-uji/uji_cocokkan_terpisah.py` (+ `--kontrol`) | 27·1: 23 skenario cocokkan tumpukan vs wadah (selisih ke merek asal, susut wajar, isi ulang lupa, rantai stok tidak bergeser) + 16 kontrol; asap: 8 wadah di cadangan dicocokkan |
| `alat-uji/uji_varian_merek.py` (+ `--kontrol`) | 27·2: 21 skenario varian (batas owner, sama/beda mutu, kolam lama byte-sama, jenis ikut induk, harga varian, induk tanpa nama kelas) + 12 kontrol; asap: tiap merek bermodal jadi varian, nama kelas ditolak |
| `alat-uji/uji_arsip_produk.py` (+ `--kontrol`) | 27·3: 19 skenario arsip (hanya yang habis, hilang dari rak/katalog/label/katalog HP kasir = index.html minus arsip, hapus tanpa transaksi, pulihkan) + 13 kontrol |
| `alat-uji/uji_setengah_karung.py` (+ `--kontrol`) | 27·4: 18 skenario ½ karung (harga, langit-langit 50 kg, pemecah Adukan satu kiriman, modal dipindah utuh, batal; 28b: saat merinci karcis — pemecah bertanggal & berjam karcis, tarik balik mencabutnya) + 14 kontrol |
| `alat-uji/uji_wadah_bernama.py` (+ `--kontrol`) | 27·5: 28 skenario wadah bernama (NG 30 + Kumala 20 → 5 L memotong buku 3 : 2, HPP tertimbang, tanpa buku nama wadah, identitas, struk satu baris, karcis, katalog, kelas ditolak, ganti nama, hapus harga liter tidak dipakai) + 21 kontrol; asap cadangan + ASAP GLOBAL omzet/laba/neraca tiap bulan byte-sama dengan main |
| `alat-uji/uji_buku_ukuran.py` (+ `--kontrol`) | 28: 19 skenario buku per ukuran (barang masuk memisah 25 kg merek dua ukuran, nama ukuran tak boleh diketik, koreksi tetap, rak/retur/katalog kasir/harga dari buku ukuran, pisah stok lama dengan hitungan + dua ketukan, nilai & laba tetap, karung terbuka 25 kg, jenis ikut induk) + 14 kontrol; asap cadangan: merek dua ukuran dipisah tanpa menggeser nilai stok & laba |
| `alat-uji/uji_uang_karyawan.py` (+ `--kontrol`) | 29 · Bagian 1 & 3: 28 skenario tiga tujuan uang keluar & kartu "Laba kotor → ke mana" (untuk karyawan = biaya toko di laba; pribadi bentuk lama; belum dipilah disebut; atur perluKaryawan, kembar ditolak, pindah tombol; penulis otomatis untuk toko; kartu menutup ke laba kotor & laba bersih mesin, upah dipisah non-upah, susut & hapus buku di bawah laba kotor, prive & sisa, final, tanpa catatan) + 12 kontrol; asap cadangan: kartu tiap bulan menutup; ASAP GLOBAL byte-sama dengan main |
| `alat-uji/uji_upah_per_orang.py` (+ `--kontrol`) | 29 · Bagian 2: 20 skenario upah per orang (tarif per hari menurut tanggal berlaku & sumbernya, bulanan ÷ hari bulan itu dibulatkan dulu, Februari 28, minggu ÷ 7, dua orang tiga upah, buku upah terbelah di pergantian tarif, upah baru hanya sesudah tanggalnya, gajian = Σ rupiah per hari, slip merinci tiap ruas, riwayat tidak ditulis ulang, tarif bersama hanya untuk yang tanpa upah sendiri, entri cacat ditolak, bentuk lama tetap terbaca) + 13 kontrol |
| `alat-uji/uji_bayar_pemasok_transfer.py` (+ `--kontrol`) | 29 · Bagian 4: 29 skenario bayar bon tunai/transfer (cara dari `dari`, kantong dijaga, transfer menurunkan REKENING & kas, admin = pengeluaranHarian untuk toko dari rekening satu kiriman, utang turun sebesar bayar, laba turun sebesar admin, buku bon menyebut cara, urung mencabut keduanya, tunai brankas, rekening belum diisi → tawaran catat isi rekening, catat isi rekening = titik kas kemarin tanpa menggeser laci/brankas/amplop, titik hari ini ditulis ulang) + 12 kontrol; asap cadangan |
| `alat-uji/uji_wadah_stok_sendiri.py` (+ `--kontrol`) | 28: 53 skenario stok wadah sendiri (buku NG yang habis menahan literan sebelum pindahan, tidak sesudahnya; pindahan awal = batch lahir 0 kg + pindah buku per wadah, nilai/laba/tumpukan tetap; nota satu baris atas buku wadah; takar memindah buku karung → wadah; cocokkan = susut wadah; ganti nama membawa stok; atur susunan menolak wadah berstok; katalog kasir; tiga pintu karung termasuk buka kemasan hasil adukan; tidak bocor ke daftar merek; tutup buku membawa tanda; sisihkan · tuang balik · bongkar ke karung wadah; kemasan adukan dibuka = buku sendiri) + 30 kontrol; asap cadangan: pindahan semua wadah tanpa menggeser nilai stok, laba, tumpukan; 1 L dari tiap wadah lewat bukunya sendiri |
| `alat-uji/uji_kelas_merek.py` (+ `--kontrol`) | 30: 45 skenario kelas mutu (peta baca/tulis & bentuk lama tanpa `asal`, tebakan tiga sumber & urutannya, riwayat kelas = `riwayatModal` tanpa fondasi, harga lalu kelas per pemasok & batch dikoreksi, ▲▼=, kalimat lunak tidak memblokir, simpan satu kiriman + tebakan tercatat sebagai tebakan + keputusan owner tidak ditimpa, kelas tanpa wadah = buku kelas + `merkPemasok`, mesin beku mengabaikan kolomnya, varian atas nama kelas, dua merek pemasok satu mobil, kartu per bulan tertimbang & kalimat periode & dua kuartal, ganti nama wadah membawa peta & menolak nama kelas) + 8 statis (layar, rules owner saja, tanpa DOM, tanpa impor balik) + 18 kontrol; asap cadangan: tebakan menunjuk wadah yang ada, riwayat kelas per nama = riwayatModal, harga lalu merek = mesin, harga lalu kelas batch terbaru = kedatangan nyata terakhir kelas itu sebelum batch (pemetaan di kotak pasir saja), buku byte-sama |
| `alat-uji/uji_pemantapan_31.py` (+ `--kontrol`) | 31: 15 skenario (karcis: dua nama seharga = satu tebakan bertanya, literan seharga, pilih nama mengisi keranjang, kelompok per bentuk, lepas karcis; tanggal mundur: cocokkan terakhir per nama & kemasan, barang masuk sebelum cocokkan ditolak dua ketukan dengan tanggal & jam, sesudah/sehari tidak, wadah & rework bukan hitungan, koreksi tidak ditanya, adukan bahan & hasil, urutan penjaga) + 3 statis + 13 kontrol |
| `alat-uji/uji_jual_tandai_cocok.py` (+ `--kontrol`) | 31b: 14 skenario (stok cukup tanpa tanda; barisTembus = kalimat periksa; staf ditahan walau yakin; owner ketukan pertama kalimat nama & kg + perluTembus; ketukan kedua = nota tercatat, baris bertanda, baris lain tanpa kolom; buku minus, modal tetap; belum dicocokkan → pita & kartu keempat; tuntas hanya cocokkan ≥ tanggal nota, rework & nama lain tidak; nota batal hilang; kemasan unit × ukuran; alasan lain menang dulu) + 4 statis + 11 kontrol |
| `alat-uji/uji_riwayat_penjualan.py` (+ `--kontrol`) | 32: 16 skenario riwayat (kunci nota & urutan, takaran digabung, status batal/dirinci/karcis, retur per baris + alasan, total = Σ berlaku, per hari − retur = rekapHari, ringkas, tampilkan batal, periode & tepinya, jenis, cara, cari nama/barang/nominal/kata ganda, saringan menumpuk tanpa retur, halaman 50 & hitungan per hari, kosong) + 4 statis + 13 kontrol; asap cadangan: tiap hari omzet = rekapHari mesin, nota & total = panel Hari ini, Σ total nota = Σ baris berlaku |
| `alat-uji/uji_kendali_biaya.py` (+ `--kontrol`) | 38: 45 skenario kendali biaya (tiap catatan tepat satu jenis & urutan pemilahannya, menutup ke mesin laba, kata owner menang, belum dipilah disebut, anggaran & lampu jatah hari ke-N, upah belum dibayar ikut, acuan median terukur, perkiraan hanya variabel, titik impas dari omzet ber-HPP & mesin sampai hari ini, pemicu per satuan & arah dibalik, pareto 80 % per kata, peringatan berurutan menunjuk pintu, tren, atur ditolak/tersimpan, tambah kata satu-kata-satu-jenis) + 23 kontrol; asap cadangan tiap bulan menutup; ASAP GLOBAL byte-sama main |
| `alat-uji/uji_wadah_satu_buku.py` (+ `--kontrol`) | 39: satu buku per kotak — karung belakang = buku sendiri (buka = pindah merek → karung belakang, tuang = pindah karung belakang → wadah, kolam vs buku disebut), isi ulang tiga ketukan (1 karung / ½ / kg satu kiriman, batas menggunung), buku merek kurang → tolak + `perluTandai` → tandai (`perluCocokkan` + `selisihPerMerk`, tuntas = cocokkan bertanggal ≥ dokumen), aktivasi per wadah dari daftar (kekurangan disebut; nilai / laba / tumpukan tetap), komposisi turunan & banding, cek tutup toko (dikosongkan = sisihkan tanpa timbang), selisih dua angka; asap cadangan §8.4 & ASAP GLOBAL byte-sama dengan main |
| `alat-uji/uji_identitas_baru.py` (+ `--kontrol`) | mesin lama & baru diberi cadangan toko yang sama → hasil identik (lokal saja; 5 kontrol) |

Memindahkan mesin ulang (sesudah `index.html` berubah): `python3 alat-uji/pindah_mesin.py`.

## Perbaikan 27 Sep 2026 — JAM YANG TAMPIL (rinci karcis & cap waktu, PR #44)
- Baris rincian karcis kasir darurat membawa **jam karcis asli** (saat penjualan terjadi di kasir); jam merinci ada di `dirinciPada` (ISO/UTC).
  Penulisnya (`susunRinciDokumen`) sudah benar — cadangan 26 Sep: semua baris rincian jamnya = jam karcis. Yang salah TAMPILAN: daftar
  "Rincian hari ini" memajang jam MERINCI di sebelah nomor karcis. Sekarang: tanggal & jam karcis + "dirinci HH:MM" terpisah, urut menurut
  kapan dirinci, hari = hari WIB.
- Cap waktu ISO (`dirinciPada`, `dikoreksiPada`, `pada`, `padaTolak`, …) DIGAMBAR lewat `jamSetempat` / `waktuSetempat` (`inti/format.js`) —
  jam dinding setempat (WIB di perangkat toko). **Jangan pernah** memotong string ISO (`slice(11, 16)`, `slice(0, 16).replace('T', ' ')`):
  itu memajang UTC, meleset 7 jam. Empat tempat lama sudah dibetulkan (jejak koreksi HPP adukan, kiriman bertahap, permintaan akses, tulisan
  ditolak). Penjaganya `alat-uji/uji_jam_tampil.py` (jsc di TZ Asia/Jakarta & UTC + penjaga statis + kontrol).
- `alat-uji/periksa_jam_rinci.py CADANGAN` — laporan pola jam baris rincian vs karcis asal + usulan koreksi (tidak menulis; bulan terkunci
  tidak diusulkan dikoreksi).

## Audit 39b no. 17 — katalog HP kasir yang ikut terbit harga lewat gerbang yang sama (1 Okt 2026, cabang `audit/39b-kksertakan-gerbang`)

Temuan: terbit harga (Harga › Terbitkan, varian baru, harga dari Stok) menambahkan katalog HP kasir ke kiriman yang sama lewat `kkSertakan` TANPA
gerbang `kkBolehTerbit` yang dipakai terbit otomatis. Kalau data di perangkat owner belum termuat penuh / masih salinan perangkat / katalog server belum
terbaca, katalog HP kasir bisa ditulis dari data yang bolong (sisa stok, bon, tuts merek salah) dan baru betul kalau perangkat owner tetap terbuka.
Tambalan: `firebase.js` `gerbangKatalog()` = SATU penilai (dipakai terbit otomatis), dipasang ke `katalog-kasir.js` lewat `kkPasangGerbang`;
`kkSertakan` berhenti bila gerbang tertutup atau tanpa penilai (kotak pasir, cadangan) — terbit otomatis menyusul begitu gerbang terbuka.
Tinjauan: kabar terbit harga dulu tetap berbunyi "katalog HP kasir ikut" walau katalog dibuang gerbang → `kkSertakanKiriman` (dipakai Harga › Terbitkan,
varian baru, harga dari Stok) mengganti kalimat itu dengan "BELUM ikut … (sebabnya) … menyusul".
Uji `uji_katalog_kasir.py` +2 (jsc: gerbang tertutup → katalog tidak ikut; statis: penilai terpasang & dipakai). Uji data toko katalog disesuaikan
cadangan 1 Okt (semua wadah aktif): buku khusus wadah tidak dijual dari HP kasir, harga liter pindah ke buku wadah — aturan wbSaringKatalogKasir.

## Audit 39b no. 31 — arahan titik kas menunjuk Tutup hari sistem baru (1 Okt 2026, cabang `audit/39b-teks-titik-kas-basi`)

Beranda dan Bon pemasok masih menulis "titik kas belum disetel di perangkat ini — setel di sistem lama". Sistem lama hanya-baca, dan titik yang disetel
di sana cuma tersimpan di satu perangkat. Kini: "titik kas belum ada — Tutup hari malam ini (Uang › Tutup hari) menyetelnya" (dokumen titikKas satu
untuk semua perangkat). Uji `uji_ringkasan_baru.py` +1 (pemeriksa kata di dua berkas), kontrol +1.
## Audit 39b no. 20 — Laporan menghitung NOTA, bukan baris (1 Okt 2026, cabang `audit/39b-nota-bukan-baris`)

Temuan: Harian, teks WA, 14 hari, per jam, minggu, enam bulan, tahun, dan rekap omzet Pajak menyebut `jumlahTrx` mesin (jumlah BARIS penjualan)
sebagai "nota" — satu nota berisi beberapa barang terhitung beberapa kali (20–47 % lebih besar dari nota sungguhan di data toko). Mesin beku tidak
diubah. Tambalan: `data/toko.js` `kunciNota` (grupNota / trxId / id — sama dengan pil Jual) + `jumlahNota(cocok)` atas penjualan yang masih berlaku;
semua "n nota" di `laporan-logika.js` & `pajak-logika.js` memakainya. Kartu "Nota yang rugi" & "Nota tanpa modal" menyebut "N baris (M nota)".
Uji `uji_laporan_baru.py` +1 (satu nota dua baris = satu nota di tujuh tempat), kontrol +2, kontrol lama "nota batal ikut" dipindah ke jumlahNota.

## Audit 39b no. 11 — "LAHIR BUKU" bukan pemasok (1 Okt 2026, cabang `audit/39b-lahir-buku-bukan-pemasok`)

Temuan: batch lahir buku khusus (buku wadah, karung belakang, karung sisihan, adukan — `wbDokLahir`, pemasok "LAHIR BUKU") tampil sebagai pemasok di
daftar pemasok, Buku bon, pil Bon lama, Rekap Bon; bon lama / kartu atas nama itu bisa dicatat → utang toko ke pemasok yang tidak ada. Tambalan:
`bon-pemasok-logika.js` `namaSistemPemasok` (STOK AWAL, TUTUP BUKU…, LAHIR BUKU; huruf besar/kecil sama) — `pemasokSungguhan` memakainya, bon lama
& kartu atas nama sistem ditolak dengan kalimat. Uji `uji_harga_baru.py` +1, kontrol +1.

## Audit 39b no. 10 — kartu HPP buku per ukuran hasil pisah (1 Okt 2026, cabang `audit/39b-hpp-buku-ukuran`)

Temuan: buku "Merek 25 kg" yang lahir dari PISAH stok (Stok › Cocokkan › pisahkan buku 25 kg) tidak punya kedatangan sendiri — kartu HPP memakai harga beli
terbaru 0: pembanding "bila dinilai harga beli terbaru" kurang senilai seluruh buku itu dan kartunya memajang penurunan modal palsu. Tambalan:
`stok-hpp-logika.js` `kartuHpp` — tanpa kedatangan sendiri → kedatangan terakhir INDUKNYA (`petaUkuran`, merek yang sama); tanpa pembanding sama sekali →
modalnya sendiri (beda 0), harga beli "belum ada" di layar Stok. Uji `uji_buku_ukuran.py` +1, kontrol +1.

## Audit 39b no. 13 — kertas "lihat hitungannya" tutup hari hanya menyebut uang laci (1 Okt 2026, cabang `audit/39b-rumus-laci-kantong`)

Temuan: `rumusLaci` menganggap SEMUA uang keluar hari itu keluar dari laci, sedangkan "seharusnya" (saldoKantong) memakai tempat yang disebut dokumennya
(brankas / rekening). Tiap ada uang keluar dari brankas atau rekening, Σ baris kertas ≠ seharusnya; angka seharusnya sendiri tetap benar. Tambalan:
`uang-logika.js` `kantongGerakan()` (aturan tempat yang sama dengan saldoKantong) dipakai `tutup-hari-logika.js` untuk masuk DAN keluar. Uji
`uji_uang_baru.py` +1, kontrol +1.

## Audit 39b no. 24 — potongan QRIS dikenali dengan SATU aturan (1 Okt 2026, cabang `audit/39b-mdr-satu-pengenal`)

Temuan: catatan potongan QRIS yang diketik tangan (tanpa tanda `mdr`, keterangannya "Potongan QRIS …") dikenali Kendali Biaya lewat kata, tetapi laporan
laba-rugi berkop hanya membaca tanda `mdr` — dokumen berkop menulis baris potongan QRIS lebih kecil dari yang sebenarnya (laba bersihnya tetap sama,
cuma salah baris). Tambalan: `uang-logika.js` `adalahMdr(h)` (tanda `mdr` ATAU keterangan berawal "mdr / potongan qris / potongan mdr") dipakai
`pilahHarian`, `laporan-logika.js` `lpMdrRentang` (kategori toko atau tokoDompet) dan `kendali-biaya-logika.js`. Uji `uji_laporan_baru.py` +1, kontrol +1.

## Audit 39b no. 25 — "belum dipilah" tidak lagi berarti dua hal (1 Okt 2026, cabang `audit/39b-belum-dipilah-dua-nama`)

Temuan: di layar Laporan kata "belum dipilah" dipakai untuk DUA hal — catatan uang keluar tanpa tujuan toko/karyawan (kartu "Laba kotor → ke mana",
dari catatan lama sebelum ada pilihan tujuan; tidak bisa dipilah ulang) dan catatan yang jenis biayanya tidak cocok kata kunci (Kendali Biaya; dibereskan
dengan memberi kata kunci). Owner yang membereskan satu tidak melihat yang lain berkurang (jalan buntu). Tambalan (kata saja; hitungan tidak berubah):
kartu laba kotor & buku hari ini Uang → "tanpa tujuan"; Kendali Biaya (cip, kartu, peringatan, baris catatan) → "jenisnya belum dikenali".
Uji `uji_kendali_biaya.py` +2 (peringatan + pemeriksa kata di `laporan.js`), kontrol +1; `uji_uang_karyawan.py` cap disesuaikan.

## Audit 39b no. 12 — tutup buku: uang yang tidak bisa dihitung bukan nol dan bukan "sama" (1 Okt 2026, cabang `audit/39b-tutup-buku-titik-kas`)

Temuan: kalau titik kas terakhir LEBIH MUDA dari 31 Des (mis. tutup hari 1–2 Jan sudah menyetelnya), uang per tempat pada 31 Des tidak bisa dihitung
(mesin tidak menghitung mundur dari titik). Empat baris uang lolos "sama" (tidak diketahui = tidak diketahui) dan jumlah harta & laba yang tinggal di
berita acara menjumlahnya sebagai nol — harta tertulis kurang seukuran kas (uangnya tidak hilang). Tambalan: `tutup-buku-logika.js` `barisBuku` —
jumlah harta & laba tinggal "belum bisa dihitung" (null) dengan kalimat tanggal titik kasnya; `bandingBuku` — baris tak terhitung bertanda "?" dan
KUNCI ditolak; teks berita acara menulis "tidak bisa dihitung", bukan Rp0. Cara mengunci tahun dalam keadaan itu = rancangan K6 (hitungan uang tutup
hari 31 Des) — belum dibangun, menunggu rancang ulang tutup buku sebelum Desember. Uji `uji_uang_baru.py` +1, kontrol +2.

## Tinjauan rantai laporan (no. 20 11 10 13 24) — tambalan (1 Okt 2026, cabang `audit/39b-rantai-laporan`)

Dua peninjau independen (uang; layar & uji). Yang ditambal:
- Tutup hari menghitung NOTA seperti Laporan & Jual (`ringkasHari.nota` = kunciNota; dokumen tutupHari tetap menyimpan `jumlahTransaksi` = baris,
  arti sistem lama, ditambah `jumlahNota`).
- "Nota bon" di kartu Laba & rekap WA = nota (`jumlahNota(cocok, saring)`), bukan baris. Hitungan tanpa modal dari mesin (baris) kini ditulis "baris
  tanpa modal" di Laporan & Kendali Biaya.
- (DITARIK sesudah tinjauan kedua) tutup hari yang mengurangi potongan QRIS yang diketik tangan: catatan ketikan lama tidak bertempat (dianggap laci),
  jadi tambalan itu membetulkan laba tapi menyalahkan saldo rekening. Kembali ke perilaku lama: potongan QRIS dicatat TUTUP HARI — jangan diketik
  di Uang keluar (catatan ketikan membuat laba hari itu terpotong dua kali).
- `adalahMdr`: kalimat biaya admin otomatis (bayar bon / pindah uang, "Biaya admin …") bukan potongan QRIS; kata harus utuh.
- Barang masuk menolak nama pemasok milik sistem (stok awal / tutup buku / lahir buku); `namaSistemPemasok` pindah ke `data/toko.js`.
- Daftar kartu HPP menulis "harga beli terbaru belum ada" (dulu Rp0/kg; panelnya sudah "belum ada").
- Uji: nota HP kasir (grupNota saja) & nota bon; sisi MASUK kertas laci; asap Laporan kini mencari cadangan di `_privat/` (audit 39b no. 46 untuk
  uji ini); syarat SENGAJA asap global diperketat (selisih potongan QRIS = catatan yang diketik, dihitung ulang dari cadangan; hitungan nota > 0 dan ≤
  baris) — sabotase "semua catatan = potongan QRIS" dan "jumlah nota 0" kini GAGAL.
## Pindah balik buku karung yang tertinggal (keputusan owner 1 Okt 2026, cabang `perbaikan/karung-tertinggal`)

Temuan di cadangan 1 Okt: 30 Sep beberapa karung di belakang wadah aktif "dikembalikan ke tumpukan" dengan kode LAMA (sebelum no. 5) yang tidak memindah
buku karung belakang balik ke buku mereknya. 6 buku karung yang karungnya sudah tidak ada masih berisi (total 167,8 kg); 2 karung yang lalu dibuka lagi
di tempat yang sama bukunya ikut memuat sisa itu (49,2 kg dan 14 kg; FAKTA dokumen: persis sisa pengembalian 02.11 yang tanpa pindah). Keputusan owner
(dua kali, 1 Okt): pertama "tertutup pindah otomatis, yang berdiri timbang dulu"; sesudah tinjauan putaran 2 (alur timbang melahirkan cacat TINGGI —
sisa lama tercatat lebih/susut lewat jalur isi ulang, hapus karung habis, kembalikan) → "PINDAH BALIK SEMUA", alur timbang khusus DIBUANG.
- `wadah-bernama-logika.js` `wbSisaKembaliLama` = sisa pengembalian lama sebagai FAKTA dokumen: pengembalian sebelum 1 Okt (karungIsi `dikembalikan`,
  `sisaSebelumKg` > 0) yang di kiriman yang sama (tanggal + jam + tempat) tidak disertai pindah buku balik, dikurangi pembetulan `betulkanTertinggal`.
- `wbKarungTertinggal` (pemeriksa d2f3a29): tertutup — karungnya sudah tidak ada, buku ≤ sisa lama → SELURUH buku pindah (juga sesudah diambil isi
  ulang); berdiri — catatan tidak minus → pindah min(sisa lama, buku − catatan), buku tidak pernah di bawah catatan; karung yang sudah ditutup lagi
  dengan kode baru (dikembalikan / dihapus habis sejak 1 Okt) → sisa lama dianggap habis (tidak dipindah dua kali).
  `wbSusunPindahTertinggal`: SATU kiriman untuk semua (modal ikut; laba tidak berubah). Timbang karung sesudahnya lewat Cocokkan biasa.
- Cocokkan › Wadah literan: karung tertutup bersisa lama tidak dapat baris (diisi 0 = susut padahal berasnya di tumpukan); timbangan karung berdiri
  bersisa lama DITOLAK: "pindah balik dulu". Kalimat selisih wadah (layar Jual): tertutup/berdiri → pindah balik, lainnya → Cocokkan.
  Papan Kapur menulis pengembalian & pembetulan sebagai itu sendiri (dulu "takar wadah").
- `stok.js` Stok › Wadah literan: kartu "Buku karung yang tertinggal" — satu tombol dua ketukan, owner saja (`tombolLuarKisi`). Nama keadaan `ttg*`
  (`kt*` sudah dipakai layar Kantong — bentrok itu melahirkan pemeriksa CI `alat-uji/periksa_penangan_ganda.py`, yang juga membaca peta kedua
  `Object.assign(…, aksiPanelWadah(…))` dan keadaan awal; dua `tombolMati` kembar identik dibuang, versi panel yang selama ini menang).
- Yang BELUM dijaga (catat): menghitung tumpukan (Cocokkan › Tumpukan) SEBELUM tombol ditekan akan mencatat beras itu "lebih", lalu tombol memindahnya
  lagi → tekan tombolnya dulu. Ketuk dari SATU perangkat (dua perangkat bersamaan = dua kali pindah; id dokumen acak).
- Σ nilai stok bisa bergeser sedikit saat pindah balik ke merek yang sudah terjual (rata-rata modal mesin) — keputusan owner no. 42; laba tetap.
  Data toko 1 Okt: 8 karung, 231 kg; geser nilai kecil (di bawah batas asap), laba tetap (asap uji_wadah_satu_buku).
- Uji `uji_wadah_satu_buku.py` blok 12t (tertutup, hanya sisa lama, berdiri, keadaan sebelum tombol ditekan, Cocokkan & kalimat, Papan Kapur) + asap data toko; kontrol +11;
  `uji_cocokkan_terpisah.py` asap membereskan kartu dulu sebelum mencocokkan semua wadah.

## Audit 39b no. 19 (versi 2) — "omzet" satu arti di SEMUA layar: penjualan − uang retur (1 Okt 2026, cabang `audit/39b-omzet-satu-arti-v2`)

Keputusan owner 9 Sep: uang kembali SELALU mengurangi omzet. Versi 1 ditarik karena baru separuh layar yang pindah (Jual tidak sepakat lagi dengan
Tutup hari). Versi 2 sekaligus:
- `data/toko.js` `returUangPerHari()` — rumus mesin laba (`uangKembaliRetur`), per tanggal + jam.
- Ringkasan: angka besar, hari/minggu/bulan/tahun, sel hari, sel per JAM dan jendela 15/60 menit (retur dikurangkan di jamnya), pembanding jam segini;
  hari/jam yang minus digambar tipis (bukan NaN) dan angkanya "−Rp 125.000". Kunci nota = `kunciNota`.
- Jual "Hari ini": omzet bersih; per cara bayar tetap PENJUALAN dan kartu menulis "retur −Rp…" (dokumen retur tidak punya cara bayar) → Σ menutup.
- Laporan Harian: pemilih 14 hari = rekap harinya; di bawah petak Tunai/QRIS/Bon tertulis "penjualan − uang retur = omzet" bila ada retur.
- Tutup hari (kertas & WA): hari dengan retur → "Penjualan · N nota", tunai/QRIS/bon baru, "retur & refund −Rp…", "Omzet (sudah dikurangi retur)";
  hari tanpa retur tetap "Omzet · N nota". Dokumen `tutupHari.omzet` TETAP penjualan (dibaca sistem lama: "lawan kemarin" & WA lama).
- Menu › Lokasi: omzet hari & bulan per lokasi dikurangi retur lokasi itu (retur tanpa lokasi = lokasi utama).
- Label: "Penjualan QRIS" (Kendali Biaya), rasio bukti QRIS "dari Rp … penjualan" (Menu › Tanya).
- Uji: Ringkasan +3, Jual +1, Laporan +1, Tutup hari +1, Lokasi +1; asap Ringkasan & Riwayat dibanding mesin laba; kontrol +9.
- Tinjauan independen (3 agen, tanpa Chrome) → dibetulkan: pembanding "kemarin jendela ini" (skala Menit) ikut dikurangi retur kemarin;
  menit yang punya nota tetap titik/sel walau returnya lebih besar (Σ sel 60 menit = angka 60 menit); tanpa adegan (kurangi gerakan) yang
  dirayakan = kenaikan SUNGGUHAN Hari ini (nota tukar membawa retur); Menu › Lokasi "belum ada" menurut ada-tidaknya nota (omzet Rp0/minus
  karena retur tetap ditulis); kertas Tutup hari: "Retur & refund" sejajar "Penjualan" & "Omzet" (bukan anak Penjualan); angka SEBELUM retur
  di Laba & laba-rugi berkop bernama "Penjualan terhitung" — "Omzet terhitung" hanya angka sesudah retur (Banding). Uji +8, kontrol +14.
  Tidak diubah: Kendali biaya "omzet nyata / hari" = ber-HPP (dasar yang sama dengan impas/hari, sengaja).

## Audit 39b no. 21 — batas sekali kirim akun bukan-owner dihitung per DOKUMEN, bukan per baris (cabang `audit/39b-pagar-dokumen-staf`)

Laten: 0 akun staf; data toko 1 Okt — 8 wadah sudah aktif, resep 1 merek (literan = 1 baris, isi ulang resep 2–4 catatan). Dulu: batas 7 baris nota
mengira ≤ 2 dokumen per baris, padahal literan dari wadah campuran yang BELUM aktif = satu baris penjualan per merek asal (6 merek × 3 baris = 18 →
ditolak pagar umum saat SIMPAN, sesudah berasnya diberikan); panel − / + takar di wadah aktif 6 merek dengan karung belakang baru = 20 catatan →
ditolak dengan kalimat "pecah jadi dua nota" di panel takar.
- `akses.js` `batasDokumenKirim(akun)` = 17 (pagar 18 − baris jejak), owner 0. Layar menyerahkannya ke logika sebagai `s.batasDok`: `jual.js` `SB()`
  (nota) & panel isi ulang (`keranjang: SB`), `stok.js` `keranjangJual()` (panel di Stok).
- `jual-logika.js` `alasanBatasDokumen(s, keranjang)` = jumlah dokumen `susunNotaDokumen` yang sama — dipanggil di `masukkan` (baris yang membuat
  nota kelewat ditolak saat DITAMBAH) dan `alasanTolak` (keranjang dari antrean / bayar sebagian / pesanan). `susunTakarWadah`: isian > batas
  ditolak dengan kalimat takar ("catat dua kali …"), dua cabang (wadah aktif & belum).
- Pagar umum `periksaKiriman`: kiriman tanpa penjualan berakhir "catat dalam dua kali" (bukan "nota").
- Uji: `peta_akses.py --kiriman` bagian 6 (nota wadah campuran 6 merek di tiap cara bayar × pesanan, alasanTolak keranjang membesar, takar 6 merek
  ditolak / 5 merek diukur 18/20, owner tanpa batas, kalimat pagar umum) + statis SB / panel / keranjangJual; `kirim()` menghitung SEMUA penolakan
  pagar umum (dulu hanya kalimat "nota"); kontrol +9. `uji_akses_baru.py` +1 (batas dokumen & kalimat), kontrol +2.

## K1 · Kunci bulan 2026 ditunda sampai tutup buku 2026 (keputusan owner 1 Okt 2026, cabang `audit/k1-tunda-kunci-2026`)

Kunci bulan berbentuk awalan: mengunci September 2026 ikut mengunci semua bulan sebelumnya (sampai 2022). Tutup buku menulis saldo pembuka
bertanggal lama (piutang ikut tanggal utang tertua, bon pemasok ikut tanggal bon) dan menghapus catatan tahun lama ke arsip — semuanya jatuh di bulan
terkunci dan pasti ditolak server, jadi tutup buku 2026 mustahil begitu satu bulan 2026 dikunci. Owner memilih **A**: kunci bulanan mulai Januari 2027.
- `data/kunci-periode.js` `KP_KUNCI_MULAI = '2027-01'`; daftar periksa Kunci bulan punya butir ⛔ pertama "Kunci bulan dimulai Januari 2027" — bulan
  sebelumnya tidak bisa dikunci (kalimat sebabnya di layar). `K.kunciMulai` / `uji.kunciMulai` = jalan pintas uji saja.
- Beranda tidak lagi menyuruh mengunci bulan 2026; peringatan pajak bulan 2026 menyebut "masih bisa bergeser sampai tutup buku 2026".
- Untuk 2027: pembuka bertanggal 1 Jan + arsip tanpa hapus (pilihan C) dirancang di putaran sendiri.

## Tutup buku bertahap (rancangan Okt 2026; owner 1 Okt: "atur saja dengan semestinya; lolosin dulu 18 nama yang berhutang")

Batas 18 pemeriksaan kunci per kiriman TETAP. Saldo pembuka tidak lagi ditolak bila > 18 — dipecah (`kunci-periode.js kpPotong`, aturan yang sama dengan
penjaga pusat). Cadangan toko 1 Okt dihitung seolah 5 Jan 2027: 57 dokumen pembuka, 24 pemeriksaan (19 nama berutang + 4 bon pemasok + titik kas 31 Des)
→ 2 kiriman (18 + 6). Batalkan juga dipecah (dulu satu kiriman 23+ → ditolak penjaga, tutup buku tak bisa dibatalkan).
- **Urutan**: kiriman 1 = berita acara `tutupBukuAcara/{tahun}` status **`berjalan`** (rencana: daftar kiriman + id; dokumen pembuka lengkap; tanpa
  pemeriksaan) + potongan pembuka pertama · kiriman berikutnya = potongan pembuka · kiriman TERAKHIR = + **penanda**: titik kas 31 Des · `pengaturan/tutupBuku`
  · berita acara `terkunci`. Satu kiriman saja (≤ 18) = sama dengan dulu (tanpa `berjalan`). Lalu arsip per 18 seperti dulu.
- **Tahun lama utuh sampai penanda**: `data/toko.js pembukaBerlaku` — saldo pembuka tahun yang berita acaranya `berjalan` / `membatalkan` / `dibatalkan`
  TIDAK terlihat mesin (9 `ambil*` koleksi pembuka) dan era (`bkEra`, `ssEraTutupBuku`). Pembuka sistem lama (tanpa berita acara) & yang terkunci/selesai
  tetap terlihat. Tanpa berita acara seperti itu `ambil*` mengembalikan larik yang sama (asap global laporan byte-sama dengan main).
- **Lanjut** (`lanjutBuku`): kiriman yang belum masuk saja (dokumen pembukanya belum ada menurut id; kiriman penanda = berita acara belum `terkunci`), isi & id
  sama dari berita acara — hanya dari perangkat yang memulainya (putaran 4). Ditolak bila 12 baris 31 Des berubah sejak mulai (`bkBerubah`). Mulai baru ditolak selama ada yang `berjalan`
  / `membatalkan` atau pembuka sisa percobaan yang dibatalkan (`bkTertunda`).
- **Kemajuan** (`kemajuanBuku`): pembuka n dari N kiriman (tahun MASIH TERBUKA) · arsip m dari M (angka DOBEL sampai habis) · selesaikan · batal. Pita di
  atas K6 dengan lanjutkan / batalkan (dua ketukan) / unduh cadangan sesudah · selesai. Langkah 7 memakai tahun yang TERKUNCI (dulu tahun layar = tahun
  berikutnya → "Kunci tahunnya dulu", berita acara tak pernah selesai).
- **Batal** (`susunBatal`): kiriman 1 = berita acara `membatalkan` (+ era & titik bila sudah terkunci) + potongan tarik pertama; lalu tarik sisanya, kembalikan
  arsip, `akhir` = `dibatalkan`. Titik kas dikembalikan hanya bila titik sekarang masih titik 31 Des tulisan tutup buku itu.
- **Titik kas tahun** (`titikTahun`): titik kas sekarang bila ≤ 31 Des; kalau tutup hari Januari sudah memajukannya → kolom **`titik`** dokumen `tutupHari`
  terakhir ≤ 31 Des (ditulis tiap tutup hari sejak rancangan ini = isi tempat uang sesudah tutup). Titik kas 31 Des ditulis HANYA bila patokan belum melewati
  31 Des; titik Januari (hitungan fisik lebih baru) dipertahankan. `saldoKantong(sampai, titikPakai)`, `barisTahun(tahun)`.
- **Periksa ulang** (`periksaUlangBuku`, ganti `sesudahHidup`): 12 baris pada HARI tutup buku dimulai (disimpan di berita acara) sebelum vs sesudah kunci & arsip
  — dulu 1 Jan vs 31 Des, penjualan 1 Jan membuat stok & laci "tidak sama" palsu.
- Penulis: `tulisDokumen(…, { tunggu: true })` → `firebase.js tulisBerkas` menunggu pengakuan server (30 detik), bukan 1,5 detik.
- Uji `uji_tutup_buku_bertahap.py` (+ `--kontrol`, CI): 30 skenario + 4 statis, 17 kontrol, asap data toko; `uji_uang_baru.py`, `uji_kunci_periode.py`
  (asap: 2 kiriman 18 + 6), `peta_akses.py --kiriman` (25 nama → 2 tahap) disesuaikan. Rules TIDAK berubah.
- BELUM: arsip yang menghapus vs bulan terkunci (K1) — keputusan owner; cadangan yang diunduh di tengah tutup buku membawa pembuka setengah (jangan dipulihkan
  lewat sistem lama).
- **Syarat §8 (tinjauan 1 Okt) dibereskan** — rincian `docs/rancangan-tutup-buku-bertahap.md` §9: pembuka ber-`bertahap` terlihat hanya bila batch PENANDA
  (`penandaBuku`, koleksi yang staf baca) ada → HP staf = HP owner di tiap titik putus (rules tidak berubah); Lanjutkan menilai titik kas saat kirim, memecah
  ulang sisa dengan jam sekarang, dan menyegarkan patokan periksa ulang; tulisan yang masih menunggu server (`toko.js dokTertunda`, diisi `firebase.js`) =
  fase `tunggu`; "selesai" menjalankan periksa ulang (beda = ketukan kedua); kalimat berhenti dari `kabarBerhentiBuku`; tanggal pembatalan lama dibuang saat
  mulai baru; daftar periksa Kunci bulan punya butir ⛔ `tutupBukuTuntas`. Uji N1–N9 di `uji_tutup_buku_bertahap.py`.
- **Putaran 3 (tinjauan + sanggah sesudah §9) dibereskan** — rincian `docs/rancangan-tutup-buku-bertahap.md` §10: arsip berhenti bila tahun itu dibatalkan
  dari perangkat lain (potongan yang terlanjur pindah dikembalikan, pembatalan membaca arsip ulang); tombol pita mati sungguh mati; hasil periksa ulang
  dibekukan saat arsip habis (`periksaArsip`); "belum bisa dihitung" ≠ TIDAK SAMA; penanda tahun lalu diarsipkan paling akhir; `terkunci` dengan pembuka
  kurang = fase `rusak` (batalkan); Lanjutkan & Batalkan hanya dari data server (`toko.js koleksiDariCache`); hapus yang menunggu server = fase `tunggu`
  (`setelHapusTertunda`); satu satuan pita / kalimat / Lanjutkan (saldo pembuka, "kiriman lanjutan i dari n"). Uji P3-… di `uji_tutup_buku_bertahap.py`.
- **Putaran 4 (owner 1 Okt: SATU PERANGKAT SAJA)** — rincian `docs/rancangan-tutup-buku-bertahap.md` §11: berita acara mencatat PEMEGANG (perangkat yang
  memulai); Lanjutkan, Batalkan, lanjut arsip, periksa ulang & selesai hanya dari pemegang (`bkBukanPemegang`, satu tempat di logika); perangkat lain melihat
  keadaan saja + tombol **ambil alih** (`susunAmbilAlih`: tersambung & data dari server, antrean kosong, berita acara diam ≥ 60 menit, pemegang tidak
  berdenyut 15 menit, dua ketukan dengan kalimat peringatan); arsip membaca status sesudah potongan terakhir juga; hasil beku periksa ulang di
  `pengaturan/periksaArsip<tahun>` tanpa status, bertanda percobaan; lembar K6 sesudah kunci memakai kalimat pita, sisi mesin yang tak terhitung "?".
  Pembatalan lanjutan dari `dibatalkan` dipegang perangkat yang memulainya. Kiriman yang tertahan di perangkat lain tetap bisa mendarat belakangan (sekarang
  lewat jalan MULAI — kiriman pertama yang tertahan sebelum server mengenal pemegangnya — atau ambil alih) — penangkal sungguhan = rules, TUGAS OWNER.
  Uji P4-… di `uji_tutup_buku_bertahap.py` (110 lulus, 85 kontrol berbunyi).

## CSP /baru/ (keputusan owner 1 Okt 2026: "Pasang"; temuan HawkScan)

`<meta http-equiv="Content-Security-Policy">` di `baru/index.html`, sebelum script & stylesheet pertama: `default-src 'self'`; script dari sendiri +
`www.gstatic.com` (SDK Firebase) + HASH script sebaris (tanpa `'unsafe-inline'`); gaya sendiri + `'unsafe-inline'` (atribut style di templat) + Google Fonts;
koneksi HANYA Firestore & Auth Firebase; `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`. Ubah script sebaris → `python3 alat-uji/uji_csp.py --pasang`.
Templat layar TIDAK boleh memakai `on…="…"` / `javascript:` (diblokir) — tetap `data-aksi`. Kasir darurat menyusul sesudah pensiun `kasir.html` mendarat
(nomor versi `kasir-v*` dipegang bersama `kasir.html` & `sw-kasir.js`).

## Audit 39b no. 40 — bulan sebelum awal buku tampil, tidak dijumlah sebagai rugi (2 Okt 2026, cabang `paket/39b-keputusan-36-45`)

Keputusan owner 30 Sep: Juli (sebelum awal buku) tetap tampil, dengan keterangan. Dulu laba-rugi berkop 3/12 bulan, Σ Tahunan dan tren Biaya menghitung
biaya Juli (tagihan bulanan + uang keluar, tanpa satu nota pun) sebagai bulan rugi. Sekarang: `laporan-logika.js` `lpAwalBuku()` (bulan catatan pertama) +
`lpKetSebelumBuku()`; laba-rugi berkop dijumlah sejak bulan awal buku dengan baris "Jul 26 · sebelum awal buku — tidak dijumlah" (tanpa angka) dan
catatan yang menyebut biayanya; `rekapTahun` menandai `sebelumBuku` (baris Tahunan "sebelum awal buku · biaya … · tidak dijumlah", Σ "bulan sejak awal
buku", pita keterangan); `trenBiaya` menandai `sebelumBuku` (batang tidak merah, kalimat di kaki). Arus kas, neraca, rekap omzet (sudah "absen") dan mesin
beku tidak diubah. Uji `uji_laporan_baru.py` +2, `uji_kendali_biaya.py` +2 (satu pemeriksa kata di `laporan.js`), kontrol +7.

## Audit 39b no. 45 — tulis ulang kiriman ditolak membawa pencatat asli (2 Okt 2026, cabang `paket/39b-keputusan-36-45`)

Keputusan owner 30 Sep: jejak pencatat asli wajib ikut saat kiriman ditolak ditulis ulang owner. Dulu Menu › Sistem › Perangkat › "tulis ulang atas
nama owner" membuang `oleh`/`olehUid`, jadi riwayat, struk ("Dilayani …") dan jejak menyebut owner. Sekarang `antre-lokal.js` `susunTulisUlang()`
membiarkan kolom pencipta (`oleh`, `olehUid`, `perangkat`, `lokasi`) dan menambah `pencatatAsli` {nama, uid, peran, perangkat, jam kirim} di tiap
dokumen beratribusi (katalog kasir apa adanya; yang sudah punya tidak ditimpa); owner tercatat sebagai penulis ulang di `diubahOleh*`, dan baris jejaknya
(`jejakTulisUlang`) berbunyi "… · ditulis ulang owner, pencatat asli <nama> (<peran>)". Juga berlaku untuk "catat ulang bertanggal hari ini". Rules v6
tidak diubah (tulisan owner tidak dibatasi kolomnya). Uji `uji_akses_baru.py` +4, kontrol +7.

## Audit 39b no. 38 — selisih laci = baris "Lebih/kurang kas" di laba (2 Okt 2026, cabang `paket/39b-keputusan-36-45`)

Keputusan owner 30 Sep: selisih laci tutup hari (lebih +, kurang −) masuk LABA sebagai baris sendiri. Dulu selisih hanya menggeser kas (titik kas dipasang
dari hitungan fisik) tanpa jejak di laba/neraca. Mesin beku tidak diubah: `uang-logika.js` `ugLebihKurangKas(dari, sampai)` (Σ `selisihLaci`/`selisih`
tutupHari + riwayat tutup ulangnya; tidak bisa dihitung = 0) dan `ugLabaBersih()` = `hitungLabaBersihRentang` + baris itu (`labaMesin` = tanpa selisih).
SEMUA pemakai laba bersih membacanya dari sana: Laba (tangga + diterima tunai), Ke mana laba kotor, laba-rugi berkop (+ kalimatnya), Banding, Mingguan,
Tahunan, inti Bulanan, neraca (laba kumulatif ikut → beda "belum terjelaskan" bergeser sebesar itu), Biaya (tangga & "menutup"), Menu (laci Laporan,
"Bulan ini toko untung berapa?"), batas aman ambil pribadi, potret kunci bulan. Baris "Lebih/kurang kas" hanya digambar bila bukan nol. Tetap: titik
impas Biaya = margin lawan biaya (`labaMesin`; lebih/kurang kas bukan biaya); lembar tutup hari ("Laba hari ini", dasar sisihan) = laba SEBELUM selisih
laci — selisih malam itu sudah punya barisnya sendiri di rekap. Sistem lama (hanya-baca) tetap laba mesin. Uji: `uji_laporan_baru.py` +4,
`uji_uang_baru.py` +2 (+1 SENGAJA: laba hari ini sesudah tutup KURANG 30.000 = 44.600, dulu 74.600), `uji_kendali_biaya.py` +2, `uji_menu_baru.py` +1,
`uji_kunci_periode.py` +1, asap toko `uji_uang_karyawan`/`uji_kendali_biaya`/`uji_laporan_baru` = mesin + selisih (dihitung ulang dari tutupHari);
ASAP GLOBAL `uji_wadah_bernama.py`: perubahan SENGAJA "no. 38" (geser = selisih laci per bulan, dihitung ulang dari cadangan); kontrol +20.

## Audit 39b no. 39 — margin bon kembali ke "diterima tunai" saat bonnya dibayar (2 Okt 2026, cabang `paket/39b-keputusan-36-45`)

Keputusan owner 30 Sep: margin bon lama dikembalikan ke "diterima tunai" saat bon dibayar. Dulu Laporan → Laba memotong margin nota bon bulan itu
dan tidak pernah mengembalikannya, jadi angka itu selalu di bawah laba yang sudah jadi uang. Sekarang `laporan-logika.js` `lpMarginBonLepas(dari, sampai)`:
margin bon DITAHAN sampai bonnya tertutup, dengan urutan potong yang sama dengan buku bon (`hitungPiutang` / `rincianBelumLunas`: bon TERTUA dulu, uang
lebih menunggu bon berikutnya, bon & pembayaran di hari yang sama = bon dulu); bon yang baru dibayar sebagian melepas marginnya sebanding. Diterima tunai
= laba bersih − margin nota bon bulan itu + margin bon yang dibayar bulan itu (bon bulan itu sendiri yang sudah dibayar ikut) + margin bon yang dihapus
bukunya (laba bersih sudah memotong seluruh nilai bon; disebut terpisah di panel). Panel "Syarat diterima tunai" menyebut semua komponennya. Laba bersih,
margin, omzet, neraca & mesin beku tidak berubah. Uji `uji_laporan_baru.py` +3 (lintas bulan Agu → Sep, uang lebih, hapus buku; 2 angka lama diubah
SENGAJA: Sep kotak pasir kini + 7.267) + pemeriksa kata panel, kontrol +8; ASAP GLOBAL `uji_wadah_bernama.py`: perubahan SENGAJA "no. 39" (margin yang
lepas per bulan dihitung ulang dari cadangan; didaftarkan sebelum no. 38).

## Audit 39b no. 36 — paket bank: kas bulan final dari hitungan tutup hari akhir bulan (2 Okt 2026, cabang `paket/39b-keputusan-36-45`)

Keputusan owner 30 Sep. Dulu neraca & arus kas bulan FINAL memakai `kasPada` dari titik kas sekarang — selalu lebih muda, jadi kasnya "—" dengan
kalimat salah "titik kas belum disetel", dan paket bank tetap mencetaknya. Sekarang `laporan-logika.js` `lpKasAkhirBulan(key)`: kas akhir bulan final =
kolom `titik` tutup hari TERAKHIR di bulan itu (+ catatan uang sesudahnya sampai akhir bulan, `saldoKantong`); neraca & arus kas berkop bulan final
(Dokumen → laporan berkop, paket bank) memakainya, kas awal arus kas = hitungan akhir bulan sebelumnya. Tanpa hitungan itu: "Kas akhir <bulan> belum bisa
dihitung — tidak ada tutup hari di <bulan>". Paket bank ditahan bila salah satu dokumennya menolak. Bulan DRAF, layar Neraca per tanggal & mesin beku
tidak diubah. Uji `uji_laporan_baru.py` +4 (1 lama dipindah ke kotak bertutup hari), kontrol +9 (1 lama disesuaikan).
