#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_karung_bekas_lahir.py — owner 7 Okt 2026: "karung yang ada di belakang wadah literan ketika habis 0 kg jadi karung bekas, dan stok karung bekas bertambah."
  · Kiriman yang membuat karung di belakang wadah HABIS (isi ulang tiga ketukan, − / + takar, hapus karung habis, samakan, cocokkan wadah) membawa
    stokBahanLiteran {tipe 'opname', jenis 'karungbekas', jumlah +1, lahirKarungBekas, karungId, ukuranKg, nilaiRp = modal karung bekas di buku} di kiriman yang SAMA.
  · Sekali saja per karung (karungId): isi ulang lalu "hapus karung habis" tidak dobel; dua karung dibuka, satu habis → +1.
  · Batal: karung yang ternyata masih berisi (samakan > 0,5 kg) atau dikembalikan ke tumpukan → dokumen kelahirannya dihapus di kiriman yang sama.
  · Dua sisi (keputusan owner 15 Sep): neraca naik = laba naik = nilaiRp; harga rata-rata karung bekas TIDAK bergeser; kas tidak bergerak; buku beras tidak disentuh.
  · Akun bukan-owner: tanpa dokumen stokBahanLiteran (rules v5) — kelahiran / pembatalan DITITIP sebagai tanda di catatan wadahnya; owner mencatatnya sekali kirim.
  · Kelahiran bukan hitungan fisik: riwayat cocokkan tidak memuatnya.
KOTAK PASIR (ANGKA CONTOH: kotak uji_wadah_satu_buku + 100 lembar karung bekas seharga Rp150.000 → Rp1.500/lembar), jam dikunci 21 Sep 2026 10:00 WIB.
Cadangan toko di _privat/ (asap, dilewati bila tidak ada): tiap karung yang berdiri di belakang wadah disamakan 0 → karung bekas lahir sebanyak karung yang berdiri,
dua sisi menutup, buku beras tetap; disamakan kembali → kelahirannya dicabut semua.

    python3 alat-uji/uji_karung_bekas_lahir.py            → N lulus · 0 gagal
    python3 alat-uji/uji_karung_bekas_lahir.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
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
ok('kabar isi ulang menyebut karung bekasnya: "+1 karung bekas (buku karung bekas 100 → 101 lembar, dinilai Rp1.500/lembar …)"', /karung Angsa \(Angsa\) habis → \+1 karung bekas \(buku karung bekas 100 → 101 lembar, dinilai Rp1\.500\/lembar = modal karung bekas di buku; ikut laba sebagai selisih stok\)/.test(R1.patch.kabar), R1.patch.kabar);
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
// ---- 7 · karung LAMA yang dituang habis sebelum fitur ini (tanpa kelahiran, tanpa penutup kolam) tidak ikut lahir saat karung berikutnya habis
terap(susunHapusKarungHabis(KBA, 'Angsa', W, true)); var idA = W.idUnik(), idT = W.idUnik(); terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: idA, tanggal: '2026-09-21', jam: '10:00', tipe: 'karung', merk: KBA, merkAsal: 'Angsa', kg: 50, wadah: 'Angsa', bukuBelakang: true } },
  { koleksi: 'wadahLiteran', data: { id: idT, tanggal: '2026-09-21', jam: '10:00', tipe: 'takar', wadah: 'Angsa', takar: 27.8, kg: 50, sumber: [{ merk: KBA, merkAsal: 'Angsa', takar: 27.8, kg: 50, dari: 'Angsa' }] } }]);
var B13 = susunBukaKarung('Angsa', W, 'Angsa', null, { tandai: true }); terap(B13); var S13 = susunSamakanKarung(KBA, '0', W, 'Angsa');
ok('kolam berisi karung lama yang habis TANPA catatan (sebelum fitur) + karung baru 50 kg → disamakan 0: cuma karung baru yang lahir (karung yang berdiri dihitung dari kg, bukan dari jumlah catatan buka)', lahirDok(S13).length === 1 && String(lahirDok(S13)[0].karungId) === idDok(B13, 'karung'), J(lahirDok(S13)));

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
print(J({ salah: salah, slot: hasil, lahir: lahirSemua, karungBekas: [K0.sisa, K1.sisa, K2.sisa], modal: K0.harga, neraca: N1 - N0, laba: L1 - L0, titipan: wbKarungBekasTunda().n }));
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


if __name__ == '__main__':
    js = uji_wadah_stok_sendiri.bundel()   # satu lingkup: teksMargin stok-hpp diganti nama (pola uji wadah)
    if '--kontrol' in sys.argv:
        rusak = {
            'kelahiran tidak disertakan ke kiriman': js.replace("  const K = wbKarungBekasKiriman(r.dokumen, w, opsi); if (!K.lahir.length && !K.batal.length) return r;", "  const K = wbKarungBekasKiriman(r.dokumen, w, opsi); if (true) return r;"),
            'karung yang sama lahir dua kali (tanpa karungId)': js.replace("const sudah = (id) => !!P[id] && P[id].akhir === 'lahir';", "const sudah = (id) => false;"),
            'karung yang berisi lagi tidak dibatalkan': js.replace("      else if (!habis && sudah(id)) batal.push(", "      else if (false) batal.push("),
            'bukan-owner menulis stokBahanLiteran (ditolak rules v5)': js.replace("  if (O.staf) {\n    lahir.forEach((x) => tanda.push(tandaDari(x, 'lahir')));", "  if (false) {\n    lahir.forEach((x) => tanda.push(tandaDari(x, 'lahir')));"),
            'nilai kelahiran nol (laba tidak dikredit, neraca naik lewat rata-rata)': js.replace("pcsSistem: sisa, pcsFisik: sisa + 1,\n        catatan: 'Karung ' + x.merkAsal + ' di belakang wadah ' + x.wadah + ' habis → jadi karung bekas', nilaiRp: harga,", "pcsSistem: sisa, pcsFisik: sisa + 1,\n        catatan: 'Karung ' + x.merkAsal + ' di belakang wadah ' + x.wadah + ' habis → jadi karung bekas', nilaiRp: 0,"),
            'kelahiran ditulis sebagai beli (uang keluar & rata-rata bergeser)': js.replace("out.dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0,", "out.dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'beli', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0,"),
            'karung berdiri dihitung semua catatan buka (karung lama ikut lahir)': js.replace("const n0 = pre > WB_KB_HABIS_KG ? Math.min(C0.length, nKarung(pre)) : (C0.length ? 1 : 0);", "const n0 = C0.length;"),
            'kelahiran dihitung sebagai hitungan fisik (riwayat cocokkan)': js.replace("ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname' && !d.lahirKarungBekas) semua.push(", "ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((d) => { if (d.tipe === 'opname') semua.push("),
            'titipan yang sudah dicatat dicatat lagi': js.replace("Object.keys(P).sort().forEach((id) => { const p = P[id]; if (p.akhir === 'lahir' && !p.lahir && p.tanda)", "Object.keys(P).sort().forEach((id) => { const p = P[id]; if (p.akhir === 'lahir' && p.tanda)"),
            'cocokkan wadah tidak melahirkan karung bekas': js.replace("  return wbSertakanKarungBekas({ dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: '", "  return ({ dokumen, hitung: c, patch: { kabar: 'Cocokkan wadah tersimpan: '"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('KARUNG BEKAS DARI KARUNG HABIS (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        print('ASAP DATA TOKO (%s): %s' % (asap.get('berkas'), json.dumps({k: v for k, v in asap.items() if k != 'berkas'}, ensure_ascii=False)[:1500]))
        for x in asap.get('salah') or []: print('   ✗ ASAP ' + x)
    sys.exit(0 if not g and not (asap and asap.get('salah')) else 2)
