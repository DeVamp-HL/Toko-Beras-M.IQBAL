#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_karung_bekas_lahir.py — owner 7 Okt 2026: "karung yang ada di belakang wadah literan ketika habis 0 kg jadi karung bekas, dan stok karung bekas bertambah."
  · Kiriman yang membuat karung di belakang wadah HABIS (isi ulang tiga ketukan, − / + takar, hapus karung habis, samakan, cocokkan wadah) membawa
    stokBahanLiteran {tipe 'opname', jenis 'karungbekas', jumlah +1, lahirKarungBekas, karungId, ukuranKg, nilaiRp = modal karung bekas di buku} di kiriman yang SAMA.
  · Sekali saja per karung (karungId): isi ulang lalu "hapus karung habis" tidak dobel; dua karung dibuka, satu habis → +1.
  · Batal: karung yang ternyata masih berisi (samakan / cocokkan > 0,5 kg — juga karung yang lebih tua dari yang berdiri sebelumnya, "hidup lagi") atau
    dikembalikan ke tumpukan → dicabut di kiriman YANG SAMA (sanggahan E2): kelahiran bertanggal hari ini dihapus; kelahiran hari lain / bulan lain / bulan
    TERKUNCI tidak pernah dihapus — catatan pembalik opname −1 bertanggal hari ini (laba bulan lalu tetap, kiriman tidak ditolak kunci periode).
  · Buka karung baru di kolam yang karung terbarunya 0 kg = karung kosong itu lahir jadi karung bekas (sekali saja).
  · Dua sisi (keputusan owner 15 Sep): neraca naik = laba naik = nilaiRp; harga rata-rata karung bekas TIDAK bergeser; kas tidak bergerak; buku beras tidak disentuh.
  · NILAI karung bekas = setelan owner (bawaan keputusan 15 Sep, Rp1.500/lembar): kelahiran dinilai harga BUKU mesin; setelan diterapkan ke buku dengan dua
    ketukan (penyetel saldoAwal jumlah 0 + selisih nilai opname hari ini: neraca naik = laba hari ini naik, bulan lalu & kas tetap); sebelum diterapkan
    kabarnya menyebut selisih itu. Buku tanpa baris berharga juga bisa disetel.
  · Akun bukan-owner: tanpa dokumen stokBahanLiteran (rules v5) — kelahiran / pembatalan DITITIP sebagai tanda di catatan wadahnya; owner mencatatnya sekali kirim.
  · Kelahiran bukan hitungan fisik: riwayat cocokkan tidak memuatnya.
KOTAK PASIR (ANGKA CONTOH: kotak uji_wadah_satu_buku + 100 lembar karung bekas seharga Rp150.000 → Rp1.500/lembar), jam dikunci 21 Sep 2026 10:00 WIB.
Cadangan toko di _privat/ (asap, dilewati bila tidak ada): tiap karung yang berdiri di belakang wadah disamakan 0 → karung bekas lahir sebanyak karung yang berdiri,
dua sisi menutup, buku beras tetap; disamakan kembali → kelahirannya dicabut semua; nilai setelan diterapkan ke buku → neraca = laba, kas tetap.

    python3 alat-uji/uji_karung_bekas_lahir.py            → N lulus · 0 gagal
    python3 alat-uji/uji_karung_bekas_lahir.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
import uji_wadah_satu_buku  # noqa: E402
import uji_wadah_stok_sendiri  # noqa: E402

MODUL = uji_wadah_satu_buku.MODUL
JAM_TETAP = uji_wadah_satu_buku.JAM_TETAP
KOTAK = json.loads(json.dumps(uji_wadah_satu_buku.KOTAK))
# ANGKA CONTOH: 100 lembar karung bekas, Rp150.000 → modal Rp1.500/lembar (mesin: total ÷ jumlah)
KOTAK['stokBahanLiteran'] = [{'id': 'kb0', 'tipe': 'beli', 'jenis': 'karungbekas', 'jumlah': 100, 'hargaTotal': 150000, 'tanggal': '2026-09-02'}]

SKENARIO = uji_wadah_satu_buku.BANTU + r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-21', jam: '10:00', kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var laba = function () { return hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih; };
var kb = function () { var s = hitungStokBahanLiteran().karungbekas || {}; return { sisa: s.sisaPcs || 0, harga: s.hargaPerPcs || 0 }; };
var bahan = function () { return hitungNeraca().nilaiBahan; };
var kas = function () { return hitungArusKasInti(function (t) { return !!t && t >= '2026-09-01' && t <= '2026-09-30'; }); };
var kasKeluar = function () { var k = kas(); return J(k.keluar.map(function (x) { return [x.label, x.nominal]; })); };
var lahirDok = function (R) { return dok(R, 'stokBahanLiteran').filter(function (d) { return d.lahirKarungBekas; }); };
var terap = function (R) { if (R.hapus) terapkanKeCache(R.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); terapkanKeCache(R.dokumen || []); return R; };
var MEREK = ['NG', 'Kumala', 'Angsa', 'Tawon', 'Beo']; var bukuMerek = function () { return J(MEREK.map(function (m) { return B2(buku(m)); })); };
var KBA = KB('Angsa', 'Angsa');
var tandaKB = function (R, tipe) { var w = dok(R, 'wadahLiteran').filter(function (d) { return !tipe || d.tipe === tipe; }); return (w[0] && w[0].karungBekas) || []; };
var idDok = function (R, tipe) { var w = dok(R, 'wadahLiteran').filter(function (d) { return !tipe || d.tipe === tipe; }); return w[0] ? String(w[0].id) : 'tidak ada'; };
var U = function (Wn, M, t, s) { return wbSusunIsiUlangTiga(Wn, M, t, W, s || s0(), {}); };

// ---- 0 · keadaan awal: wadah Angsa diaktifkan (titik samakan 0 kg)
terap(wbSusunAktifkan('Angsa', W));
var K0 = kb(), L0 = laba(), N0 = bahan(), KK0 = kasKeluar();
ok('awal: 100 lembar karung bekas, modal Rp1.500/lembar (kotak pasir), wadah Angsa aktif & kosong', K0.sisa === 100 && K0.harga === 1500 && wbAktif('Angsa') && B2(buku('Wadah Angsa')) === 0, J([K0, buku('Wadah Angsa')]));
ok('konstanta: batas habis = 0,5 kg (sama dengan deretan & hapus karung habis), jenis karungbekas', WB_KB_HABIS_KG === 0.5 && WB_KB_JENIS === 'karungbekas');

// ---- 1 · isi ulang tiga ketukan: dua karung dibuka, satu dituang habis → +1 (karung PERTAMA), satu sisa 45
var R1 = U('Angsa', 'Angsa', { jenis: 'kg', kg: '55' }); var l1 = lahirDok(R1); var kr1 = dok(R1, 'wadahLiteran').filter(function (d) { return d.tipe === 'karung'; });
ok('isi ulang 55 kg dari 2 karung baru: SATU karung bekas lahir di kiriman yang sama — karungId = karung pertama yang dibuka, ukuran 50 kg, merek asal & wadah tertulis, opname +1 jumlah 1 hargaTotal 0, nilaiRp = modal Rp1.500, catatan menyebut karungnya',
  !R1.tolak && kr1.length === 2 && l1.length === 1 && String(l1[0].karungId) === String(kr1[0].id) && l1[0].ukuranKg === 50 && l1[0].merkAsal === 'Angsa' && l1[0].wadah === 'Angsa' && l1[0].kolam === KBA && l1[0].tipe === 'opname' && l1[0].jenis === 'karungbekas' && l1[0].jumlah === 1 && l1[0].hargaTotal === 0 && l1[0].nilaiRp === 1500 && l1[0].hargaPerPcsSaatOpname === 1500 && l1[0].pcsSistem === 100 && l1[0].pcsFisik === 101 && l1[0].tanggal === '2026-09-21' && /Karung Angsa di belakang wadah Angsa habis → jadi karung bekas/.test(l1[0].catatan) && R1.karungBekas.lahir === 1, J([R1.tolak, l1, kr1.map(function (k) { return k.id; })]));
ok('kabar isi ulang menyebut karung bekasnya: "+1 karung bekas (buku karung bekas 100 → 101 lembar, dinilai Rp1.500/lembar (setelan owner) …)" — buku = setelan bawaan (keputusan 15 Sep)', /karung Angsa \(Angsa\) habis → \+1 karung bekas \(buku karung bekas 100 → 101 lembar, dinilai Rp1\.500\/lembar \(setelan owner\); ikut laba sebagai selisih stok\)/.test(R1.patch.kabar) && J(wbKbNilai().setelan) === '1500' && !wbKbNilai().diatur && wbKbNilai().selaras, R1.patch.kabar);
terap(R1); var K1 = kb();
ok('DUA SISI: karung bekas 100 → 101, modal per lembar TETAP Rp1.500 (lembar gratis tidak membagi rata-rata); neraca bahan +Rp1.500 = laba September +Rp1.500; kas keluar tidak bergerak; buku beras tidak disentuh selain pindah buku isi ulang',
  K1.sisa === 101 && K1.harga === 1500 && bahan() - N0 === 1500 && laba() - L0 === 1500 && kasKeluar() === KK0, J([K1, bahan() - N0, laba() - L0]));
ok('kelahiran BUKAN hitungan fisik: riwayat cocokkan tidak memuatnya', !riwayatCocok(30).some(function (g) { return g.baris.some(function (x) { return /Karung bekas/i.test(x.nama); }); }), J(riwayatCocok(30)));
ok('isi ulang berikutnya yang tidak menghabiskan karung (sisa 45 → 40) tidak melahirkan apa-apa', (function () { var r = U('Angsa', 'Angsa', { jenis: 'kg', kg: '5' }); return !r.tolak && !lahirDok(r).length && !r.karungBekas; })());

// ---- 2 · − / + takar menghabiskan karung kedua (SEADANYA) → +1 (karung kedua); lalu "hapus karung habis" TIDAK dobel
var cAn = chipL('Angsa'); var sJ = masuk(s0(), cAn, 60); var NJ = simpanNota(Object.assign({}, sJ, { cara: 'QRIS' }), W); terap(NJ);
ok('jual 60 L dari wadah Angsa (kotak pasir) supaya muat isi ulang berikutnya', !sJ.tolak && !NJ.tolak && B2(buku('Wadah Angsa')) === 5.8, J([sJ.tolak, NJ.tolak, buku('Wadah Angsa')]));
var R2 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 30 }], W, s0()); var l2 = lahirDok(R2);
ok('− / + takar 30 (54 kg) dari karung belakang tinggal 45 → SEADANYA 45, karung kedua habis → +1 karung bekas (karungId karung kedua), satu kiriman', !R2.tolak && l2.length === 1 && String(l2[0].karungId) === String(kr1[1].id) && R2.hitung.sumber[0].seadanya === true && /\+1 karung bekas/.test(R2.patch.kabar), J([R2.tolak, l2, R2.patch && R2.patch.kabar]));
var Kr2 = kb(); terap(R2); var K2 = kb();
ok('sesudah − / + takar: karung bekas +1 (jual literan tadi memakai satu karung bekas sebagai wadahnya)', K2.sisa === Kr2.sisa + 1, J([Kr2, K2]));
var R3 = susunHapusKarungHabis(KBA, 'Angsa', W, false);
ok('SEKALI SAJA: karung yang sama lewat jalur kedua ("hapus karung habis") tidak melahirkan karung bekas lagi; kolam ditutup', !R3.tolak && !lahirDok(R3).length && !R3.karungBekas && dok(R3, 'wadahLiteran')[0].selesai === true, J([R3, K2]));
terap(R3); ok('sesudah hapus karung habis: karung bekas tetap', kb().sisa === K2.sisa, J(kb()));

// ---- 3 · samakan 0 → +1; samakan 20 (ternyata belum habis) → DIBATALKAN (dokumennya dihapus); samakan 0 lagi → lahir lagi; kembalikan → dibatalkan
var B3 = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B3); var k3 = dok(B3, 'wadahLiteran').filter(function (d) { return d.tipe === 'karung'; })[0];
var L3a = laba(), N3a = bahan(), K3a = kb(); var S3 = susunSamakanKarung(KBA, '0', W, 'Angsa'); var l3 = lahirDok(S3);
ok('samakan karung belakang ke 0 kg → +1 karung bekas untuk karung yang baru dibuka', !S3.tolak && l3.length === 1 && String(l3[0].karungId) === String(k3.id) && /habis → \+1 karung bekas/.test(S3.patch.kabar), J([S3.tolak, l3]));
terap(S3);
var S4 = susunSamakanKarung(KBA, '20', W, 'Angsa');
ok('samakan ke 20 kg (karungnya ternyata masih berisi) → kelahiran karung bekasnya DICABUT di kiriman yang sama: hapus dokumen kelahiran itu + tanda batal di catatan karungIsi; kabar menyebut "ternyata belum habis"',
  !S4.tolak && (S4.hapus || []).length === 1 && S4.hapus[0].koleksi === 'stokBahanLiteran' && String(S4.hapus[0].id) === String(l3[0].id) && !lahirDok(S4).length && J(tandaKB(S4).map(function (t) { return [t.aksi, String(t.karungId)]; })) === J([['batal', String(k3.id)]]) && /ternyata belum habis → catatan karung bekasnya dicabut/.test(S4.patch.kabar), J(S4));
terap(S4);
ok('sesudah batal: karung bekas, neraca bahan, laba kembali seperti sebelum samakan 0', kb().sisa === K3a.sisa && bahan() === N3a && laba() === L3a, J([kb(), bahan() - N3a, laba() - L3a]));
var S5 = susunSamakanKarung(KBA, '0', W, 'Angsa');
ok('samakan 0 lagi → lahir LAGI (dokumen baru; peristiwa terakhir per karung yang menentukan)', lahirDok(S5).length === 1 && String(lahirDok(S5)[0].karungId) === String(k3.id), J(S5));
terap(S5);
var KM = susunKembalikanKarung(KBA, 'Angsa', W, true);
ok('kembalikan karung yang tercatat jadi karung bekas ke tumpukan → kelahirannya dicabut (hapus) di kiriman yang sama', !KM.tolak && (KM.hapus || []).some(function (x) { return x.koleksi === 'stokBahanLiteran' && String(x.id) === String(lahirDok(S5)[0].id); }) && /dikembalikan ke tumpukan → catatan karung bekasnya dicabut/.test(KM.patch.kabar), J(KM));
terap(KM); ok('sesudah dikembalikan: karung bekas kembali seperti sebelum samakan 0', kb().sisa === K3a.sisa, J(kb()));

// ---- 4 · akun bukan-owner: DITITIP (tanpa stokBahanLiteran), owner mencatatnya sekali kirim
var B6 = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B6); var k6 = dok(B6, 'wadahLiteran').filter(function (d) { return d.tipe === 'karung'; })[0];
var T6 = susunSamakanKarung(KBA, '0', W, 'Angsa', { staf: true });
ok('bukan-owner samakan 0: TIDAK ada dokumen stokBahanLiteran (rules v5 menolaknya), tanda lahir dititip di catatan karungIsi miliknya sendiri, kabar "MENUNGGU owner"', !T6.tolak && !dok(T6, 'stokBahanLiteran').length && !(T6.hapus || []).length && J(tandaKB(T6).map(function (t) { return [t.aksi, String(t.karungId), t.ukuranKg]; })) === J([['lahir', String(k6.id), 50]]) && /MENUNGGU owner/.test(T6.patch.kabar) && T6.karungBekas.titip === true, J(T6));
terap(T6); var TT = wbKarungBekasTunda();
ok('titipan terbaca: 1 lahir menunggu, tanpa batal', TT.n === 1 && TT.lahir.length === 1 && String(TT.lahir[0].karungId) === String(k6.id) && !TT.batal.length, J(TT));
var T7 = susunHapusKarungHabis(KBA, 'Angsa', W, true, { staf: true });
ok('bukan-owner "hapus karung habis" atas karung yang SUDAH dititip → tidak dititip dua kali', !T7.tolak && !T7.karungBekas && !tandaKB(T7).length && !dok(T7, 'stokBahanLiteran').length, J(T7));
var K7 = kb(); var O7 = wbSusunKarungBekasTunda(W); var o7 = lahirDok(O7);
ok('owner mencatat titipan: satu dokumen kelahiran (bertanggal hari ini, dariTitipan, karungId sama), buku 102 → 103', !O7.tolak && o7.length === 1 && o7[0].dariTitipan === true && String(o7[0].karungId) === String(k6.id) && O7.patch.kabar.indexOf('Karung bekas dicatat: +1 lahir — buku karung bekas ' + K7.sisa + ' → ' + (K7.sisa + 1) + ' lembar') === 0, J(O7));
terap(O7); ok('sesudah dicatat owner: tidak ada titipan lagi; karung bekas +1', wbKarungBekasTunda().n === 0 && kb().sisa === K7.sisa + 1 && !!wbSusunKarungBekasTunda(W).tolak);
var T8 = susunSamakanKarung(KBA, '20', W, 'Angsa', { staf: true });
ok('bukan-owner samakan 20 atas karung yang sudah tercatat karung bekas → tanda BATAL dititip (tanpa hapus — bukan-owner tidak pernah menghapus)', !(T8.hapus || []).length && J(tandaKB(T8).map(function (t) { return t.aksi; })) === J(['batal']), J(T8));
terap(T8); ok('titipan batal terbaca', wbKarungBekasTunda().batal.length === 1, J(wbKarungBekasTunda()));
var T8b = susunSamakanKarung(KBA, '0', W, 'Angsa', { staf: true }); terap(T8b);
ok('titipan batal lalu titipan lahir lagi sementara dokumen kelahirannya masih ada → tidak ada yang menunggu (tidak menulis kelahiran kedua)', wbKarungBekasTunda().n === 0 && J(tandaKB(T8b).map(function (t) { return t.aksi; })) === J(['lahir']), J([wbKarungBekasTunda(), T8b]));
var T8c = susunSamakanKarung(KBA, '20', W, 'Angsa', { staf: true }); terap(T8c); var TB = wbKarungBekasTunda(); var O9 = wbSusunKarungBekasTunda(W);
ok('owner mencatat titipan batal: dokumen kelahiran karung itu dihapus; buku 103 → 102', TB.batal.length === 1 && O9.hapus.length === 1 && String(O9.hapus[0].id) === String(o7[0].id) && !O9.dokumen.length, J([TB, O9]));
terap(O9); ok('sesudahnya karung bekas kembali, titipan 0', kb().sisa === K7.sisa && wbKarungBekasTunda().n === 0, J(kb()));
var T10 = susunSamakanKarung(KBA, '0', W, 'Angsa', { staf: true }); terap(T10); var T11 = susunSamakanKarung(KBA, '30', W, 'Angsa', { staf: true }); terap(T11);
ok('titipan lahir lalu titipan batal untuk karung yang belum dicatat owner → saling meniadakan (tidak ada yang menunggu)', wbKarungBekasTunda().n === 0, J(wbKarungBekasTunda()));

// ---- 5 · isi ulang akun bukan-owner (s.batasDok): titip, dokumen kiriman tidak bertambah
var sJ5 = masuk(s0(), chipL('Angsa'), 60); terap(simpanNota(Object.assign({}, sJ5, { cara: 'QRIS' }), W));
var s5 = Object.assign(s0(), { batasDok: 17 }); var I5 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 20 }], W, s5);
ok('− / + takar akun bukan-owner (s.batasDok) yang menghabiskan karung 30 kg (seadanya) → tidak ada dokumen stokBahanLiteran, tanda lahir di catatan takarnya, jumlah dokumen kiriman tidak bertambah', !I5.tolak && !dok(I5, 'stokBahanLiteran').length && tandaKB(I5, 'takar').length === 1 && /MENUNGGU owner/.test(I5.patch.kabar), J(I5));

// ---- 6 · cocokkan wadah (owner): karung ditimbang 0 → +1
terap(I5); ok('titipan isi ulang terbaca & dicatat owner', wbKarungBekasTunda().lahir.length === 1); terap(wbSusunKarungBekasTunda(W)); var B12 = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B12);
var c12 = barangCocok('wadah').find(function (b) { return b.nama === 'Angsa'; }); var H12 = {}; H12[c12.kunciKarung] = '0';
var C12 = susunSimpanCocok('wadah', H12, { 'wadah|Angsa': 'timbang' }, W, { aneh: true, susutPositif: true, sebagian: true, ganda: true });
ok('cocokkan wadah: karung di belakang ditimbang 0 kg → +1 karung bekas di kiriman cocokkan yang sama', !C12.tolak && lahirDok(C12).length === 1 && String(lahirDok(C12)[0].karungId) === idDok(B12, 'karung'), J([C12.tolak, lahirDok(C12), c12]));

terap(C12);
// ---- 7 · karung LAMA yang dituang habis sebelum fitur ini (tanpa kelahiran, tanpa penutup kolam) tidak ikut lahir; karung TERBARU yang 0 kg (masih tegak
//         sebagai karung kosong) lahir saat karung baru dibuka dari Stok (sanggahan E2 lanjutan — dulu tidak pernah lahir), sekali saja
terap(susunHapusKarungHabis(KBA, 'Angsa', W, true)); var idA0 = W.idUnik(), idA = W.idUnik(), idT = W.idUnik(); terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: idA0, tanggal: '2026-09-21', jam: '10:00', tipe: 'karung', merk: KBA, merkAsal: 'Angsa', kg: 50, wadah: 'Angsa', bukuBelakang: true } },
  { koleksi: 'wadahLiteran', data: { id: idA, tanggal: '2026-09-21', jam: '10:00', tipe: 'karung', merk: KBA, merkAsal: 'Angsa', kg: 50, wadah: 'Angsa', bukuBelakang: true } },
  { koleksi: 'wadahLiteran', data: { id: idT, tanggal: '2026-09-21', jam: '10:00', tipe: 'takar', wadah: 'Angsa', takar: 55.6, kg: 100, sumber: [{ merk: KBA, merkAsal: 'Angsa', takar: 55.6, kg: 100, dari: 'Angsa' }] } }]);
var B13 = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true });
ok('buka karung baru dari Stok di kolam 0 kg: karung TERBARU yang kosong (bukan yang lebih tua, tanpa catatan kelahiran) lahir di kiriman buka itu', !B13.tolak && lahirDok(B13).length === 1 && String(lahirDok(B13)[0].karungId) === String(idA) && /habis → \+1 karung bekas/.test(B13.patch.kabar), J([B13.tolak, lahirDok(B13)]));
var B13s = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true, staf: true });
ok('buka karung akun bukan-owner di kolam itu: kelahiran karung kosong DITITIP di catatan karungnya (tanpa stokBahanLiteran)', !B13s.tolak && !dok(B13s, 'stokBahanLiteran').length && J(tandaKB(B13s, 'karung').map(function (x) { return [x.aksi, String(x.karungId)]; })) === J([['lahir', String(idA)]]), J(B13s));
terap(B13); var S13 = susunSamakanKarung(KBA, '0', W, 'Angsa');
ok('lalu disamakan 0: cuma karung baru yang lahir (karung lama TIDAK, karung kosong tadi tidak dua kali — karung yang berdiri dihitung dari kg, bukan dari jumlah catatan buka)', lahirDok(S13).length === 1 && String(lahirDok(S13)[0].karungId) === idDok(B13, 'karung'), J(lahirDok(S13)));

// ---- 8 · (sanggahan E2) karung yang sudah karung bekas HIDUP LAGI lewat samakan / cocokkan yang menaikkan kolam di atas satu karung → dicabut di kiriman ITU, tepat sekali
terap(S13);
var B8a = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true });
ok('buka karung saat karung terbaru 0 kg tapi SUDAH karung bekas → tidak lahir lagi', !B8a.tolak && !lahirDok(B8a).length && !B8a.karungBekas, J(B8a));
terap(B8a); var B8b = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B8b); var k8a = idDok(B8a, 'karung'), k8b = idDok(B8b, 'karung');
var S8 = susunSamakanKarung(KBA, '45', W, 'Angsa'); var l8 = lahirDok(S8);
ok('dua karung (100 kg) disamakan 45: karung A (yang lebih tua) habis → lahir; B berdiri', l8.length === 1 && String(l8[0].karungId) === k8a, J(l8)); terap(S8);
var K8 = kb(), N8 = bahan(), L8 = laba();
var S9 = susunSamakanKarung(KBA, '60', W, 'Angsa');
ok('disamakan 45 → 60 (di atas satu karung): karung A berdiri LAGI → kelahirannya DICABUT di kiriman ITU (bertanggal hari ini → dokumennya dihapus + jejak); kabar "ternyata belum habis"',
  !S9.tolak && (S9.hapus || []).length === 1 && String(S9.hapus[0].id) === String(l8[0].id) && /karung bekas dicabut \(kelahiran hari ini\)/.test(S9.jejakHapus || '') && /ternyata belum habis → catatan karung bekasnya dicabut/.test(S9.patch.kabar), J(S9));
terap(S9); ok('sesudahnya karung bekas, neraca, laba kembali seperti sebelum A lahir', kb().sisa === K8.sisa - 1 && bahan() === N8 - 1500 && laba() === L8 - 1500, J([kb(), K8]));
var T9 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 3 }], W, s0());
ok('takar berikutnya yang MENGURANGI isi (60 → 54,6) tidak menyentuh karung bekas lagi (dulu baru di sini dicabut, dengan kabar yang salah)', !T9.tolak && !T9.karungBekas && !lahirDok(T9).length && !(T9.hapus || []).length, J([T9.tolak, T9.karungBekas, T9.patch && T9.patch.kabar]));
terap(T9); var S10 = susunSamakanKarung(KBA, '45', W, 'Angsa'); ok('disamakan 45 lagi → A lahir lagi (dokumen baru)', lahirDok(S10).length === 1 && String(lahirDok(S10)[0].karungId) === k8a, J(lahirDok(S10))); terap(S10);
var c10 = barangCocok('wadah').find(function (b) { return b.nama === 'Angsa'; }); var H10 = {}; H10[c10.kunciKarung] = '60';
var C10 = susunSimpanCocok('wadah', H10, { 'wadah|Angsa': 'timbang' }, W, { aneh: true, susutPositif: true, sebagian: true, ganda: true });
ok('cocokkan wadah: karung ditimbang 60 kg → karung A hidup lagi → dicabut di kiriman cocokkan yang SAMA', !C10.tolak && (C10.hapus || []).length === 1 && String(C10.hapus[0].id) === String(lahirDok(S10)[0].id), J([C10.tolak, C10.hapus, C10.karungBekas]));
terap(C10);

// ---- 9 · (sanggahan E2) pembatalan LINTAS BULAN / bulan TERKUNCI: kelahiran September tidak pernah dihapus — catatan pembalik bertanggal hari ini
var B9c = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B9c); var k9c = idDok(B9c, 'karung');   // kolam 110 kg: A, B, C berdiri
var S11 = susunSamakanKarung(KBA, '0', W, 'Angsa'); var l11 = lahirDok(S11); terap(S11);   // A, B, C lahir 21 Sep
var lahirOf = function (id) { return l11.filter(function (d) { return String(d.karungId) === id; })[0]; }; var lahirA = lahirOf(k8a), lahirB = lahirOf(k8b), lahirC = lahirOf(k9c);
ok('kolam 110 kg (A, B, C) disamakan 0 pada 21 Sep → tiga karung bekas lahir bertanggal 21 Sep', l11.length === 3 && !!lahirA && !!lahirB && !!lahirC && l11.every(function (d) { return d.tanggal === '2026-09-21'; }), J(l11));
__KINI = new Date('2026-10-07T10:00:00+07:00').getTime();
var W2 = { tanggal: '2026-10-07', jam: '09:00', kini: '2026-10-07T02:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var labaO = function () { return hitungLabaBersihRentang('2026-10-01', '2026-10-31').labaBersih; };
var kasO = function () { var k = hitungArusKasInti(function (t) { return !!t && t >= '2026-10-01' && t <= '2026-10-31'; }); return J(k.keluar.map(function (x) { return [x.label, x.nominal]; })); };
var Ls = laba(), Lo = labaO(), Nb = bahan(), Kb = kb();
var S12 = susunSamakanKarung(KBA, '45', W2, 'Angsa'); var p12 = dok(S12, 'stokBahanLiteran');
ok('LINTAS BULAN (belum terkunci): 7 Okt karung C disamakan 45 (ternyata belum habis) → kelahiran 21 Sep TIDAK dihapus — satu catatan PEMBALIK bertanggal 7 Okt (opname −1, lahirKarungBekas + batal, karungId C, nilaiRp −Rp1.500, lahirId = kelahiran itu); kabar menyebutnya',
  !S12.tolak && !(S12.hapus || []).length && p12.length === 1 && p12[0].tipe === 'opname' && p12[0].jumlah === -1 && p12[0].batal === true && p12[0].lahirKarungBekas === true && String(p12[0].karungId) === k9c && p12[0].nilaiRp === -1500 && p12[0].tanggal === '2026-10-07' && String(p12[0].lahirId) === String(lahirC.id)
  && /catatan pembalik bertanggal hari ini/.test(S12.patch.kabar), J([S12.tolak, S12.hapus, p12, S12.patch && S12.patch.kabar]));
terap(S12);
ok('sesudahnya: laba SEPTEMBER tidak bergeser surut, laba Oktober −Rp1.500 = neraca bahan −Rp1.500, karung bekas −1, tidak ada titipan', laba() === Ls && labaO() === Lo - 1500 && bahan() === Nb - 1500 && kb().sisa === Kb.sisa - 1 && wbKarungBekasTunda().n === 0, J([laba() - Ls, labaO() - Lo, bahan() - Nb, kb()]));
// September dikunci: samakan owner atas kelahiran 21 Sep (karung B hidup lagi) — kiriman TIDAK ditolak
pasok('aturanToko', cacheMentah('aturan').concat([{ id: 'kunciPeriode', sampaiBulan: '2026-09', riwayat: [{ aksi: 'kunci', bulan: '2026-09', olehUid: 'x' }] }]));
var S12b = susunSamakanKarung(KBA, '95', W2, 'Angsa'); var p12b = dok(S12b, 'stokBahanLiteran');
ok('September TERKUNCI: 7 Okt disamakan 45 → 95 (karung B hidup lagi) → pembalik 7 Okt untuk B, tanpa hapus; jagaKunci null (dulu seluruh kiriman tertolak "Bulan September 2026 terkunci")',
  !S12b.tolak && !(S12b.hapus || []).length && p12b.length === 1 && p12b[0].batal === true && String(p12b[0].karungId) === k8b && String(p12b[0].lahirId) === String(lahirB.id) && jagaKunci(S12b.dokumen, S12b.hapus) === null, J([S12b.tolak, p12b, jagaKunci(S12b.dokumen, S12b.hapus)]));
terap(S12b);
// titipan bukan-owner atas kelahiran bulan terkunci (karung A, 21 Sep) → owner mencatat = pembalik hari ini
var T14 = susunSamakanKarung(KBA, '105', W2, 'Angsa', { staf: true });
ok('bukan-owner samakan 105 (A hidup lagi): tanda BATAL dititip, tanpa hapus & tanpa stokBahanLiteran', !T14.tolak && !(T14.hapus || []).length && !dok(T14, 'stokBahanLiteran').length && J(tandaKB(T14).map(function (x) { return [x.aksi, String(x.karungId)]; })) === J([['batal', k8a]]), J(T14));
terap(T14); var TB14 = wbKarungBekasTunda(); var O14 = wbSusunKarungBekasTunda(W2);
ok('owner mencatat titipan BATAL atas kelahiran bulan terkunci: catatan pembalik 7 Okt (tanpa hapus), kiriman tidak ditolak kunci', TB14.batal.length === 1 && !O14.tolak && !(O14.hapus || []).length && dok(O14, 'stokBahanLiteran').length === 1 && dok(O14, 'stokBahanLiteran')[0].batal === true && dok(O14, 'stokBahanLiteran')[0].jumlah === -1 && String(dok(O14, 'stokBahanLiteran')[0].lahirId) === String(lahirA.id) && jagaKunci(O14.dokumen, O14.hapus) === null && /lewat catatan pembalik hari ini/.test(O14.patch.kabar), J([TB14, O14]));
terap(O14); ok('sesudahnya tidak ada titipan; laba September tetap', wbKarungBekasTunda().n === 0 && laba() === Ls, J(wbKarungBekasTunda()));
var S13b = susunSamakanKarung(KBA, '45', W2, 'Angsa'); var l13b = lahirDok(S13b).filter(function (d) { return !d.batal; });
ok('lalu disamakan 105 → 45 (7 Okt) → A & B lahir LAGI bertanggal 7 Okt (peristiwa: lahir Sep · pembalik Okt · lahir Okt)', !S13b.tolak && l13b.length === 2 && l13b.every(function (d) { return d.tanggal === '2026-10-07'; }) && jagaKunci(S13b.dokumen, S13b.hapus) === null, J(S13b)); terap(S13b);
var S13c = susunSamakanKarung(KBA, '105', W2, 'Angsa');
ok('dicabut di HARI YANG SAMA (7 Okt) → kelahiran 7 Okt dihapus (bukan pembalik)', (S13c.hapus || []).length === 2 && !dok(S13c, 'stokBahanLiteran').length && jagaKunci(S13c.dokumen, S13c.hapus) === null, J(S13c)); terap(S13c);
pasok('aturanToko', cacheMentah('aturan').filter(function (a) { return a.id !== 'kunciPeriode'; }));
terap(susunSamakanKarung(KBA, '45', W2, 'Angsa'));

// ---- 10 · NILAI karung bekas = setelan owner (bawaan keputusan 15 Sep Rp1.500/lembar), diterapkan ke buku mesin — neraca = laba, kas & bulan lalu tetap
var Nv0 = wbKbNilai();
ok('bawaan: setelan Rp1.500 (keputusan owner 15 Sep, belum diatur), buku Rp1.500 di kotak pasir → selaras', Nv0.setelan === 1500 && !Nv0.diatur && Nv0.buku === 1500 && Nv0.selaras && WB_KB_NILAI_BAWAAN === 1500, J(Nv0));
var V1 = wbSusunNilaiKarungBekas('2.000', W2, false);
ok('ubah ke Rp2.000: ketukan pertama DITOLAK minta ketukan kedua — kalimat menyebut buku Rp1.500 → Rp2.000, rak N lembar naik, laba HARI INI naik, bukan uang masuk', !!V1.tolak && V1.perluYakin === true && /buku karung bekas Rp1\.500 → Rp2\.000\/lembar: \d+ lembar di rak naik Rp[\d.]+ = laba HARI INI naik Rp[\d.]+ \(selisih nilai, bukan uang masuk/.test(V1.tolak), V1.tolak);
ok('isian rusak ditolak; di luar batas ditolak', /angka saja/.test(wbSusunNilaiKarungBekas('15,5', W2, true).tolak || '') && /harus Rp1/.test(wbSusunNilaiKarungBekas('0', W2, true).tolak || '') && /harus Rp1/.test(wbSusunNilaiKarungBekas('200000', W2, true).tolak || ''));
var Lv = labaO(), Lsv = laba(), Nv = bahan(), KOv = kasO(), Kv = kb(); var V2 = wbSusunNilaiKarungBekas('2.000', W2, true); var d2 = function (t) { return (V2.dokumen || []).filter(function (x) { return x.data && x.data.tipe === t && x.koleksi === 'stokBahanLiteran'; }).map(function (x) { return x.data; }); };
ok('ketukan kedua: setelan aturanToko/karungBekas {nilaiLembar 2000, riwayat} + penyetel saldoAwal jumlah 0 (bertanda nilaiKarungBekas) + selisih nilai opname jumlah 0 nilaiRp = rak × Rp500, bertanggal 7 Okt; baris lama tidak disentuh',
  !V2.tolak && V2.dokumen.length === 3 && V2.dokumen[0].koleksi === 'aturanToko' && V2.dokumen[0].data.id === 'karungBekas' && V2.dokumen[0].data.nilaiLembar === 2000 && V2.dokumen[0].data.riwayat.length === 1 && d2('saldoAwal').length === 1 && d2('saldoAwal')[0].jumlah === 0 && d2('saldoAwal')[0].nilaiKarungBekas === true && d2('opname').length === 1 && d2('opname')[0].jumlah === 0 && d2('opname')[0].nilaiRp === Kv.sisa * 500 && d2('opname')[0].tanggal === '2026-10-07' && !(V2.hapus || []).length, J(V2));
terap(V2);
ok('sesudah diterapkan: harga buku Rp2.000, sisa TETAP; neraca bahan naik = laba Oktober naik = rak × Rp500; laba September TETAP; kas keluar Oktober TETAP (penyetel bukan uang)', kb().harga === 2000 && kb().sisa === Kv.sisa && bahan() - Nv === Kv.sisa * 500 && labaO() - Lv === Kv.sisa * 500 && laba() === Lsv && kasO() === KOv, J([kb(), bahan() - Nv, labaO() - Lv, laba() - Lsv, kasO() === KOv]));
ok('penyetel nilai bukan hitungan fisik: riwayat cocokkan tidak memuatnya', !riwayatCocok(30).some(function (g) { return g.baris.some(function (x) { return /disetel/.test(x.alasan || ''); }); }), J(riwayatCocok(30)));
ok('nilai sama ditolak ("sudah … di setelan dan di buku")', /sudah Rp2\.000\/lembar/.test(wbSusunNilaiKarungBekas('2000', W2, true).tolak || ''));
var N15 = bahan(), L15 = labaO(); var S15 = susunSamakanKarung(KBA, '0', W2, 'Angsa'); var l15 = lahirDok(S15);
ok('kelahiran sesudahnya dinilai Rp2.000 per karung (setelan owner = buku); neraca naik = laba naik = Rp2.000 × karung', l15.length >= 1 && l15.every(function (d) { return d.nilaiRp === 2000 && !d.batal; }) && /dinilai Rp2\.000\/lembar \(setelan owner\)/.test(S15.patch.kabar) && (terap(S15), bahan() - N15 === 2000 * l15.length && labaO() - L15 === 2000 * l15.length), J([l15, S15.patch.kabar]));
// setelan berubah tanpa diterapkan (mis. data lama): kelahiran tetap dinilai harga BUKU, kabarnya menyebut selisihnya — tidak ada status yang berbohong
pasok('aturanToko', cacheMentah('aturan').filter(function (a) { return a.id !== 'karungBekas'; }).concat([{ id: 'karungBekas', nilaiLembar: 2500 }]));
var B16 = susunBukaKarung('Angsa', W2, 'Angsa', null, { tandai: true }); terap(B16); var N16 = bahan(), L16 = labaO(); var S16 = susunSamakanKarung(KBA, '0', W2, 'Angsa'); var l16 = lahirDok(S16);   // karung baru B16 lahir
ok('setelan Rp2.500 BELUM diterapkan ke buku (Rp2.000): kelahiran dinilai Rp2.000 (buku) supaya neraca = laba; kabar menyebut "setelan owner Rp2.500 belum diterapkan ke buku"', l16.length === 1 && l16[0].nilaiRp === 2000 && /dinilai Rp2\.000\/lembar = harga buku karung bekas; setelan owner Rp2\.500 belum diterapkan ke buku/.test(S16.patch.kabar) && (terap(S16), bahan() - N16 === 2000 && labaO() - L16 === 2000), J([l16, S16.patch.kabar]));
var V3 = wbSusunNilaiKarungBekas('', W2, true); terap(V3);
ok('isian kosong = terapkan setelan yang ada (Rp2.500) → buku Rp2.500, neraca = laba', !V3.tolak && kb().harga === 2500, J([V3.tolak, kb()]));
// buku TANPA baris berharga (rak 0, harga 0): penyetel jumlah 1 dinetralkan opname −1 → harga = setelan, sisa tetap
var simpanBL = cacheMentah('bahanLiteran').slice(); var simpanAT = cacheMentah('aturan').slice();
pasok('stokBahanLiteran', []); pasok('aturanToko', []);
var V4 = wbSusunNilaiKarungBekas('', W2, true); var N4 = bahan(), L4 = labaO(), K4 = kasO();
ok('buku karung bekas kosong (Rp0): terapkan bawaan Rp1.500 → penyetel jumlah 1 + opname −1, harga Rp1.500, sisa 0, neraca & laba & kas tidak bergerak', !V4.tolak && (terap(V4), kb().harga === 1500 && kb().sisa === 0 && bahan() === N4 && labaO() === L4 && kasO() === K4), J([V4, kb()]));
pasok('stokBahanLiteran', simpanBL); pasok('aturanToko', simpanAT);

print(J({ lulus: lulus, gagal: gagal }));
"""

ASAP = uji_wadah_satu_buku.BANTU + r"""
Object.keys(CADANGAN).forEach(function (n) { if (Array.isArray(CADANGAN[n])) pasok(n, CADANGAN[n]); });
__dom['jualKarungBerat'] = { value: '50' };
var nId = 900000; var W = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
var kbS = function () { var s = hitungStokBahanLiteran().karungbekas || {}; return { sisa: s.sisaPcs || 0, harga: s.hargaPerPcs || 0 }; };
var laba = function () { return hitungLabaBersihRentang(TGL_CAD.slice(0, 8) + '01', TGL_CAD).labaBersih; };
var bukuSemua = function () { var st = hitungStokKarungPerMerk(); return J(Object.keys(st).sort().map(function (m) { return [m, Math.round(st[m].sisaKg * 100) / 100]; })); };
var terap = function (R) { if (R.hapus) terapkanKeCache(R.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); terapkanKeCache(R.dokumen || []); };
var K0 = kbS(), L0 = laba(), N0 = hitungNeraca().nilaiBahan, B0 = bukuSemua(); var salah = []; var hasil = []; var lahirSemua = 0;
slotKarungWadah().forEach(function (x) { if (x.kosong || !x.karung.diketahui) return; var awal = x.karung.sisaMentahKg;
  var R = susunSamakanKarung(x.merk, '0', W, x.W); if (R.tolak) { salah.push(x.no + ' ditolak: ' + R.tolak); return; }
  var l = (R.dokumen || []).filter(function (d) { return d.koleksi === 'stokBahanLiteran'; }).map(function (d) { return d.data; });
  var berdiri = awal > 0.5 ? Math.max(1, Math.ceil((awal - 0.5) / beratKarungBuka(x.merk))) : 1;
  if (l.length > berdiri) salah.push(x.no + ' lahir ' + l.length + ' > karung berdiri ' + berdiri);
  if (l.some(function (d) { return !d.lahirKarungBekas || d.jenis !== 'karungbekas' || d.jumlah !== 1 || d.tipe !== 'opname'; })) salah.push(x.no + ' bentuk dokumen');
  terap(R); lahirSemua += l.length; hasil.push({ slot: x.no, merk: x.merkAsal, kg: Math.round(awal * 100) / 100, lahir: l.length }); });
var K1 = kbS(), L1 = laba(), N1 = hitungNeraca().nilaiBahan;
if (K1.sisa - K0.sisa !== lahirSemua) salah.push('stok karung bekas tidak naik sebesar kelahiran');
if (K1.harga !== K0.harga) salah.push('modal per lembar bergeser');
if (Math.abs((N1 - N0) - (L1 - L0)) > 0.5) salah.push('dua sisi tidak menutup: neraca ' + (N1 - N0) + ' laba ' + (L1 - L0));
if (bukuSemua() !== B0) salah.push('buku beras bergeser');
// samakan kembali ke angka semula → semua kelahiran dicabut
hasil.forEach(function (h) { var x = slotKarungWadah().find(function (s) { return s.no === h.slot; }); if (!x) return; var R = susunSamakanKarung(x.merk, String(h.kg).replace('.', ','), W, x.W); if (!R.tolak) terap(R); });
var tetapKosong = hasil.filter(function (h) { return h.kg <= 0.5; }).reduce(function (a, h) { return a + h.lahir; }, 0);
var K2 = kbS(); if (K2.sisa !== K0.sisa + tetapKosong) salah.push('sesudah disamakan kembali karung bekas ' + K2.sisa + ' ≠ ' + K0.sisa + ' + ' + tetapKosong + ' (karung yang sejak awal sudah kosong)');
// NILAI setelan owner (bawaan keputusan 15 Sep) diterapkan ke buku toko: penyetel hari ini — harga buku = setelan, sisa tetap, neraca naik = laba naik, kas tetap
var kasK = function () { var k = hitungArusKasInti(function (t) { return !!t && t >= TGL_CAD.slice(0, 8) + '01' && t <= TGL_CAD; }); return J(k.keluar.map(function (x) { return [x.label, x.nominal]; })); };
var NV = wbKbNilai(); var nilaiAsap = { setelan: NV.setelan, diatur: NV.diatur, bukuDulu: NV.buku, rak: NV.sisa };
var V = wbSusunNilaiKarungBekas('', W, true);
if (NV.selaras) nilaiAsap.catatan = 'sudah selaras';
else if (V.tolak) salah.push('penyetel nilai ditolak: ' + V.tolak);
else { var nb0 = hitungNeraca().nilaiBahan, lb0 = laba(), kk0 = kasK(); terap(V); var KV = kbS();
  if (KV.harga !== NV.setelan) salah.push('harga buku sesudah penyetel ' + KV.harga + ' ≠ setelan ' + NV.setelan);
  if (KV.sisa !== NV.sisa) salah.push('penyetel menggeser sisa karung bekas');
  if ((hitungNeraca().nilaiBahan - nb0) !== (laba() - lb0)) salah.push('penyetel: neraca ' + (hitungNeraca().nilaiBahan - nb0) + ' ≠ laba ' + (laba() - lb0));
  if (kasK() !== kk0) salah.push('penyetel menggeser kas keluar');
  nilaiAsap.bukuSesudah = KV.harga; nilaiAsap.selisihNilai = hitungNeraca().nilaiBahan - nb0;
  // kelahiran sesudahnya dinilai setelan: semua karung yang berdiri disamakan 0 sekali lagi
  var nb1 = hitungNeraca().nilaiBahan, lb1 = laba(), nL = 0;
  slotKarungWadah().forEach(function (x) { if (x.kosong || !x.karung.diketahui) return; var R = susunSamakanKarung(x.merk, '0', W, x.W); if (R.tolak) return;
    (R.dokumen || []).forEach(function (d) { if (d.koleksi === 'stokBahanLiteran' && d.data.lahirKarungBekas && !d.data.batal) { nL += 1; if (d.data.nilaiRp !== NV.setelan) salah.push('kelahiran sesudah penyetel bernilai ' + d.data.nilaiRp); } }); terap(R); });
  if ((hitungNeraca().nilaiBahan - nb1) !== (laba() - lb1) || (laba() - lb1) !== nL * NV.setelan) salah.push('kelahiran sesudah penyetel: neraca ' + (hitungNeraca().nilaiBahan - nb1) + ' / laba ' + (laba() - lb1) + ' ≠ ' + nL + ' × ' + NV.setelan);
  nilaiAsap.lahirSesudah = nL; }
print(J({ salah: salah, slot: hasil, lahir: lahirSemua, karungBekas: [K0.sisa, K1.sisa, K2.sisa], modal: K0.harga, neraca: N1 - N0, laba: L1 - L0, titipan: wbKarungBekasTunda().n, nilai: nilaiAsap }));
"""


def utama(js, pakai_cadangan):
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    asap = None
    p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p:
        cad, tgl = uji_wadah_bernama.cad_js(p)
        a, e2 = uji_wadah_bernama.jalan(JAM_TETAP.replace('2026-09-21T10:00:00', tgl + 'T23:00:00') + js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + ASAP)
        asap = a if a is not None else {'salah': ['ASAP JATUH: ' + e2[-400:]]}
        asap['berkas'] = os.path.basename(p)
    return h['lulus'], h['gagal'], asap


def statis(teks=None):
    """Layar: panel wadah di Jual & penolong Stok meneruskan r.hapus (kelahiran hari ini yang dicabut) — tanpa itu kabar "dicabut" berbohong;
    buka karung di Stok membawa tanda akun; kartu Nilai karung bekas (owner) memanggil penyetel dengan ketukan kedua."""
    t = teks or {}
    def baca(p): return t[p] if p in t else open(os.path.join(AKAR, p), encoding='utf-8').read()
    g = []; n = 0
    jl = baca('baru/js/layar/jual.js'); n += 1
    m = re.search(r'\n  async function tulisWadah\(r\) \{\n(.*?)\n  \}\n', jl, re.S)
    if not m or 'tulisDokumen(r.dokumen, r.hapus, { jejakHapus: r.jejakHapus })' not in m.group(1): g.append('Jual tulisWadah tidak meneruskan r.hapus — karung bekas yang "dicabut" tetap ada (status berbohong)')
    sj = baca('baru/js/layar/stok.js'); n += 1
    if 'tulisDokumen(r.dokumen || [], r.hapus, { jejakHapus: r.jejakHapus })' not in sj: g.append('Stok tulis() tidak meneruskan r.hapus')
    n += 1
    if sj.count('L.susunBukaKarung(') != 2 or "L.susunBukaKarung(t.merk, waktu(), t.wadah, t.asal, Object.assign({ tandai: true }, stafKb()))" not in sj or "L.susunBukaKarung(merk, waktu(), wadah || '', asal, stafKb())" not in sj: g.append('buka karung di Stok tidak membawa tanda akun (titipan bukan-owner)')
    n += 1
    if 'data-aksi="kbNilaiSimpan"' not in sj or 'WB.wbSusunNilaiKarungBekas(st().kbNilai, waktu(), st().kbNilaiYakin)' not in sj or 'if (r.perluYakin) return set({ kbNilaiYakin: true' not in sj: g.append('kartu Nilai karung bekas tidak lengkap (ketukan kedua)')
    return n - len(g), g


if __name__ == '__main__':
    js = uji_wadah_stok_sendiri.bundel()   # satu lingkup: teksMargin stok-hpp diganti nama (pola uji wadah)
    if '--kontrol' in sys.argv:
        rusak = {
            'kelahiran tidak disertakan ke kiriman': js.replace("  const K = wbKarungBekasKiriman(r.dokumen, w, opsi); if (!K.lahir.length && !K.batal.length) return r;", "  const K = wbKarungBekasKiriman(r.dokumen, w, opsi); if (true) return r;"),
            'karung yang sama lahir dua kali (tanpa karungId)': js.replace("const sudah = (id) => !!P[id] && P[id].akhir === 'lahir';", "const sudah = (id) => false;"),
            'karung yang berisi lagi tidak dibatalkan': js.replace("const id = String(k.id); if (!sudah(id) || dicatat[id]) return; dicatat[id] = 1; batal.push(", "const id = String(k.id); if (true) return; dicatat[id] = 1; batal.push("),
            'karung yang hidup lagi dibaca dari karung yang berdiri SEBELUM saja (pembatalan tertunda ke kiriman berikutnya)': js.replace("(kembali ? calon : S.filter((k) => berdiri[String(k.id)]))", "(kembali ? calon : calon.filter((k) => berdiri[String(k.id)]))"),
            'pembatalan menghapus kelahiran hari / bulan lain (laba surut, bulan terkunci menolak kiriman)': js.replace("  if (String(lahirDok.tanggal || '') === String(w.tanggal) && Math.round(Number(lahirDok.nilaiRp) || 0) === harga && !tolakKunci('stokBahanLiteran', lahirDok))", "  if (true)"),
            'pembatalan menghapus kelahiran bulan lain yang belum terkunci (laba bulan lalu surut)': js.replace("  if (String(lahirDok.tanggal || '') === String(w.tanggal) && Math.round(Number(lahirDok.nilaiRp) || 0) === harga && !tolakKunci('stokBahanLiteran', lahirDok))", "  if (!tolakKunci('stokBahanLiteran', lahirDok))"),
            'pembatalan selalu lewat pembalik (kelahiran hari ini tidak dihapus)': js.replace("  if (String(lahirDok.tanggal || '') === String(w.tanggal) && Math.round(Number(lahirDok.nilaiRp) || 0) === harga", "  if (false"),
            'catatan pembalik tidak dibaca sebagai batal (karung dicabut terbaca masih karung bekas)': js.replace("tambah(String(d.karungId), { aksi: d.batal ? 'batal' : 'lahir', d, pada: d });", "tambah(String(d.karungId), { aksi: 'lahir', d, pada: d });"),
            'buka karung tidak melahirkan karung kosong yang lama': js.replace("    return wbSertakanKarungBekas({ dokumen: b.dokumen,", "    return ((r) => r)({ dokumen: b.dokumen,"),
            'nilai kelahiran = setelan walau buku belum diterapkan (neraca ≠ laba)': js.replace("    const N = wbKbNilai(); const harga = N.buku; const s0 = N.sisa; let sisa = s0; let nPembalik = 0;", "    const N = wbKbNilai(); const harga = N.setelan; const s0 = N.sisa; let sisa = s0; let nPembalik = 0;"),
            'penyetel nilai tanpa catatan selisih (laba tidak ikut naik)': js.replace("    if (tanpaHarga || delta) dokumen.push(", "    if (false) dokumen.push("),
            'penyetel nilai ditulis sebagai beli (uang keluar)': js.replace("data: { id: w.idUnik(), tipe: 'saldoAwal', jenis: WB_KB_JENIS, jumlah: tanpaHarga ? 1 : 0,", "data: { id: w.idUnik(), tipe: 'beli', jenis: WB_KB_JENIS, jumlah: tanpaHarga ? 1 : 0,"),
            'penyetel nilai tanpa ketukan kedua': js.replace("  if (ubahBuku && !yakin) return { tolak: 'Ketuk sekali lagi untuk menerapkan nilai karung bekas '", "  if (false) return { tolak: 'Ketuk sekali lagi untuk menerapkan nilai karung bekas '"),
            'bawaan nilai bukan keputusan owner 15 Sep': js.replace("const WB_KB_NILAI_BAWAAN = 1500;", "const WB_KB_NILAI_BAWAAN = 1;"),
            'bukan-owner menulis stokBahanLiteran (ditolak rules v5)': js.replace("  if (O.staf) {\n    lahir.forEach((x) => tanda.push(tandaDari(x, 'lahir')));", "  if (false) {\n    lahir.forEach((x) => tanda.push(tandaDari(x, 'lahir')));"),
            'nilai kelahiran nol (laba tidak dikredit, neraca naik lewat rata-rata)': js.replace("pcsSistem: sisa, pcsFisik: sisa + 1,\n        catatan: 'Karung ' + x.merkAsal + ' di belakang wadah ' + x.wadah + ' habis → jadi karung bekas', nilaiRp: harga,", "pcsSistem: sisa, pcsFisik: sisa + 1,\n        catatan: 'Karung ' + x.merkAsal + ' di belakang wadah ' + x.wadah + ' habis → jadi karung bekas', nilaiRp: 0,"),
            'kelahiran ditulis sebagai beli (uang keluar & rata-rata bergeser)': js.replace("out.dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0,", "out.dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'beli', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0,"),
            'karung berdiri dihitung semua catatan buka (karung lama ikut lahir)': js.replace("const n0 = pre > WB_KB_HABIS_KG ? Math.min(C0.length, nKarung(pre)) : (C0.length ? 1 : 0);", "const n0 = C0.length;"),
            'kelahiran dihitung sebagai hitungan fisik (riwayat cocokkan)': js.replace("ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && !d.lahirKarungBekas && !d.nilaiKarungBekas) semua.push(", "ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && !d.lahirKarungBekas) semua.push("),
            'titipan yang sudah dicatat dicatat lagi': js.replace("Object.keys(P).sort().forEach((id) => { const p = P[id]; if (p.akhir === 'lahir' && !p.lahir && p.tanda)", "Object.keys(P).sort().forEach((id) => { const p = P[id]; if (p.akhir === 'lahir' && p.tanda)"),
            'cocokkan wadah tidak melahirkan karung bekas': js.replace("  return wbSertakanKarungBekas({ dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: '", "  return ((r) => r)({ dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: '"),
        }
        kode = 0
        statis_rusak = {
            'Jual panel wadah membuang r.hapus': {'baru/js/layar/jual.js': open(os.path.join(AKAR, 'baru/js/layar/jual.js'), encoding='utf-8').read().replace('tulisDokumen(r.dokumen, r.hapus, { jejakHapus: r.jejakHapus })', 'tulisDokumen(r.dokumen)', 1)},
            'buka karung Stok tanpa tanda akun': {'baru/js/layar/stok.js': open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read().replace("L.susunBukaKarung(merk, waktu(), wadah || '', asal, stafKb())", "L.susunBukaKarung(merk, waktu(), wadah || '', asal, {})", 1)},
        }
        for nama, tk in statis_rusak.items():
            if any(v == open(os.path.join(AKAR, k), encoding='utf-8').read() for k, v in tk.items()): print('KONTROL BASI  ' + nama); kode = 3; continue
            _, g = statis(tk)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    ls, gs = statis(); l += ls; g = g + gs
    print('KARUNG BEKAS DARI KARUNG HABIS (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        print('ASAP DATA TOKO (%s): %s' % (asap.get('berkas'), json.dumps({k: v for k, v in asap.items() if k != 'berkas'}, ensure_ascii=False)[:1500]))
        for x in asap.get('salah') or []: print('   ✗ ASAP ' + x)
    sys.exit(0 if not g and not (asap and asap.get('salah')) else 2)
