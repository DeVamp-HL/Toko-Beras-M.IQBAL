#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_rules_emulator.py — BUKTI SERVER untuk rules v7 (PR #111, sebelum owner menerbitkannya): Firebase Emulator Firestore menilai rules dengan MESIN
RULES YANG SAMA dengan server produksi. Sampai 7 Okt, v7 hanya dinilai penafsir mini (alat-uji/rules_mini.py — "model bukan server"); di sini teks
firestore.rules cabang ini dipasang ke emulator dan tiap kasus dikirim lewat REST dengan TOKEN AKUN PALSU (JWT tak bertanda tangan — diterima emulator,
tidak pernah server sungguhan), jadi salah tulis yang tidak dimodelkan penafsir mini ikut ketahuan.

HANYA DI RUNNER GITHUB ACTIONS untuk bagian yang menyalakan emulator & node (CLAUDE.md, keputusan owner 27 Sep 2026: emulator & peramban tidak di Mac
owner) — workflow .github/workflows/uji-rules-emulator.yml. Di Mac boleh: --periksa / --kontrol (statis + model + jsc, tanpa emulator).

A · KASUS RULES — semua kasus docs/uji-rules-v7.md (18 "Wajib owner" + semua opsional ★A/B/N/F/K/R/P/T) + kasus model M-* (periksa_rules.KASUS_V7 —
    dokumen uji U1–U11 yang SAMA, tabel "Dokumen uji") + kasus S-* yang hanya bisa di server (cap = jam server lewat transform REQUEST_TIME, yang tidak
    bisa diketik di Playground). Tiap kasus: emulator dikosongkan, dokumen uji diisi lewat jalur admin (Bearer owner — emulator melewati rules), lalu
    SATU operasi dengan token akun "Isian Playground" (owner@ uid-uji, kasir@ uid-kasir-uji, staf uid-uji-b, akun tanpa aksesAkun baru1). LOLOS/DITOLAK
    wajib = kolom "Wajib" (★: dibaca dari tabel docs; M/S/H: kolom model). Tanggal "hari ini" & jam relatif (besok, 5 hari lagi, cap 1 jam lalu) digeser ke
    jam runner; cap = jam server (JAM_UJI_V7) dikirim sebagai transform REQUEST_TIME. TAHUN dokumen uji digeser sebesar selisih tahun runner (WIB) − 2026
    (tahun lalu = tahun runner − 1, tahun berjalan = tahun runner; 2021 → 2021 + selisih, dst.), jadi bukti ini tetap mengukur sesudah 1 Jan 2027 — saat
    tutup buku 2026 berjalan dengan rules v7. --periksa membuktikan model tetap = kolom Wajib di jam-jam lain (1 Jan 2027, Juni 2027, Jan 2028) + kontrol.
    H · berita acara HANYA MAJU (v6, docs/uji-rules-v6.md A/B — periksa_rules.KASUS_BUKU) atas teks v7 dengan dokumen ujinya sendiri (v7 mengubah blok
    tutupBukuAcara: create acaraBaru, update + acaraTutupPintu, delete hanya dibatalkan).
    v6: kasus yang sama dijalankan atas firestore.rules.v6 — yang berbeda WAJIB persis BEDA_V6 (lima ubahan v6 → v7 di docs; bukti ubahan itulah yang
    membuat beda), selebihnya sama dengan v7.
    KONTROL: rules v7 dirusak satu suku (pintuSah selalu benar, ulangKasirBercap tanpa syarat capServer, salinan arsip tanpa pembanding isi, …) → kasus
    sasarannya WAJIB berbalik dari kolom Wajib (LOLOS ↔ DITOLAK, bukan galat). Kasus yang sama lulus dengan rules utuh → sebabnya suku itu.
C · KASIR DARURAT — KODE ASLI kasir-darurat-nominal.html (kasir_emulator.js: skrip sebaris halaman di node, DOM tiruan, fetch ke emulator): kasir-v33
    (berkas cabang ini) nota baru :commit + capServer REQUEST_TIME → masuk; kirim ulang identik (jawaban hilang) → :commit DITERIMA (ulangKasirBercap), cap
    jam server baru; kirim ulang yang mengubah isi → :commit & cara lama ditolak, server tidak berubah. kasir-v32 (KASIR_V32_COMMIT) kirim ulang identik
    atas nota bercap → PATCH utuh diterima (capServer terbuang), yang mengubah isi → ditolak. Di v6: kirim ulang v33 jatuh ke cara lama (PATCH updateMask)
    dan tetap masuk tanpa dobel; v32 atas nota bercap DITOLAK (sebab v7 perlu). Kontrol: suku (kasir() && ulangKasirBercap()) dicabut → berbunyi.

    python3 alat-uji/uji_rules_emulator.py --periksa    → statis + model (+ jsc / node: kode kasir dengan server palsu) — boleh di Mac. Yang tidak bisa
                                                          diukur di mesin ini (jsc/node tidak ada, commit kasir-v32 tidak terbaca) = ⚠ DILEWATI, bukan ✓
    python3 alat-uji/uji_rules_emulator.py --kontrol    → kerusakan pada pemeriksa statis wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_rules_emulator.py --emulator --keluar hasil.json --ringkasan ringkasan.md   → di runner, di dalam `firebase emulators:exec`
"""
import os, re, sys, json, time, base64, shutil, datetime, tempfile, subprocess, urllib.request, urllib.error, urllib.parse
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import periksa_rules as P   # noqa: E402  — kasus & dokumen uji v7 yang SAMA dengan model CI (KASUS_V7, DB_UJI_V7, AKUN_UJI, WAJIB_V7)
import rules_mini as RM     # noqa: E402

PROYEK = 'demo-uji-rules'                       # proyek emulator "demo-": tanpa kredensial, Firebase tidak pernah menyambungkannya ke server sungguhan
PROYEK_HALAMAN = 'toko-beras-m-iqbal'           # proyek yang ditulis kasir darurat — kasir_emulator.js menulis ulang alamatnya ke emulator
KASIR_V32_COMMIT = 'b973f7f71585048c6b4d698d769fa0db42bfba62'   # main 6 Okt 2026: kasir-darurat-nominal.html terakhir ber-VERSI kasir-v32 (HP penjaga sebelum cabang ini)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
WIB = datetime.timezone(datetime.timedelta(hours=7))
DOK = 'docs/uji-rules-v7.md'
FS_HOST = (os.environ.get('FIRESTORE_EMULATOR_HOST') or '127.0.0.1:8080').replace('localhost', '127.0.0.1')
FS = 'http://' + FS_HOST
DB = 'projects/%s/databases/(default)' % PROYEK
ADMIN = {'Authorization': 'Bearer owner'}       # emulator: melewati rules — hanya pengisi dokumen uji & pembaca isi server, tidak pernah operasi kasus
TS, JAM = RM.Ts, P.JAM_UJI_V7
SERVER = 'REQUEST_TIME'                          # penanda nilai: capServer = jam server permintaan itu (transform)

# ---- kasus S-*: hanya bisa di server — cap = jam server (request.time) tidak bisa diketik di Playground. Model menilainya juga (cap = JAM_UJI_V7).
NOTA, BERCAP = P.NOTA, P.BERCAP
KASUS_SERVER = [
    ('S-A1', 'kasir@ nota baru kasir-v33: capServer = jam server (REQUEST_TIME)', 'kasir', 'create', 'penjualan', 'uji-v7-s1', dict(NOTA, id='uji-v7-s1', capServer=JAM), None, True, 0),
    ('S-A2', 'kasir@ kirim ulang identik + capServer jam server (ulangKasirBercap)', 'kasir', 'update', 'penjualan', 'uji-v7-nota', dict(NOTA, capServer=JAM), None, True, 0),
    ('S-A3', 'kasir@ kirim ulang atas nota bercap: cap lama diganti jam server', 'kasir', 'update', 'penjualan', 'uji-v7-bercap', dict(NOTA, id='uji-v7-bercap', capServer=JAM), BERCAP, True, 0),
    ('S-B1', 'owner batu nisan bercap jam server', 'owner', 'create', 'batuNisan', 'uji-v7', {'id': 'penjualan|x', 'koleksi': 'penjualan', 'idDok': 'x', 'capServer': JAM}, None, True, 0),
    ('S-B2', 'owner batu nisan TANPA capServer', 'owner', 'create', 'batuNisan', 'uji-v7', {'id': 'penjualan|x', 'koleksi': 'penjualan', 'idDok': 'x'}, None, False, None),
]
# ---- H · berita acara HANYA MAJU (v6; docs/uji-rules-v6.md A/B, model periksa_rules.KASUS_BUKU — 19 boleh, 26 ditolak) atas teks v7. Dokumen ujinya sendiri:
# tutupBukuAcara/1990 = isi lama, TANPA dokumen uji v7 (tanpa pintu → selesai / dibatalkan tidak terhalang pintu). Wajib = kolom model; v6 wajib sama.
KASUS_BUKU = [('H' + no, nama, 'owner', 'update', 'tutupBukuAcara', '1990', baru, {'tutupBukuAcara/1990': P.DOK_BUKU[lama] if isinstance(lama, str) else lama}, boleh, None)
              for no, nama, lama, baru, boleh in P.KASUS_BUKU]
BUKU = {K[0] for K in KASUS_BUKU}
KASUS = P.KASUS_V7 + KASUS_SERVER + KASUS_BUKU

# ---- v6 → v7: kasus yang WAJIB berbeda (nomor ubahan di docs/uji-rules-v7.md "Yang berubah v6 → v7"); semua kasus lain WAJIB sama di v6
BEDA_V6 = dict([(k, 1) for k in ('★A3', '★A4', 'M-A5', 'S-A2', 'S-A3', 'S-B1')] + [(k, 2) for k in ('★N1', '★N2')] + [(k, 3) for k in ('★F1', '★F2', '★F3')]
               + [(k, 4) for k in ('★K3', '★K4', '★K5', '★K6')]
               + [(k, 5) for k in ('★P1', '★P22', 'M-P26b', 'M-P26c', 'M-P26d', '★P2', 'M-P3', '★P4', '★P5', '★P26', '★P16', '★P17', '★P18', '★P24', 'M-P24b', 'M-P24c',
                                   'M-P27', '★T2', '★T3', '★T4', '★T5', 'M-T8', 'M-T9')])
UBAHAN = {1: 'hemat baca (kirim ulang kasir@ bercap, batu nisan)', 2: 'permintaan nego staf', 3: 'foto bon', 4: 'kasir@ dipangkas', 5: 'pintu tutup buku'}

# ---- KONTROL: rules v7 dirusak SATU suku → kasus sasarannya wajib berbalik (dinilai juga oleh model di --periksa)
KONTROL = [
    ('pintuSah selalu benar (pintu dibuka tanpa syarat)', [("      return d.get('status', '') == 'berjalan' && y is int && y == wib().year() - 1\n",
                                                             "      return true || d.get('status', '') == 'berjalan' && y is int && y == wib().year() - 1\n")],
     ['★P16', '★P17', '★P18', '★P24', 'M-P24b', 'M-P24c', 'M-P27']),
    ('ulangKasirBercap tanpa syarat capServer (cap jam HP diterima)', [("\n        && (!request.resource.data.keys().hasAny(['capServer']) || request.resource.data.capServer == request.time);", ";")], ['★B2']),
    ('salinan arsip tanpa pembanding isi', [("\n        && isi.diff(a.data.get('dok', {})).affectedKeys().hasOnly(['capServer']);", ";")], ['★P20', '★P13']),
    ('pintu tanpa batas waktu (sampai tidak dinilai)', [("\n        && request.time < p.data.sampai ? int(p.data.tahun) : 0;", " ? int(p.data.tahun) : 0;")], ['★P19']),
    ('berita acara baru tanpa pemeriksa jam mulai', [("\n        && p[0:10] in [hariUtc(request.time - duration.value(1, 'd')), hariUtc(request.time), hariUtc(request.time + duration.value(1, 'd'))];", ";")], ['★T2']),
    ('berita acara selesai walau pintu terbuka', [("      return !(b.get('status', '') in ['selesai', 'dibatalkan']) || pintuMati(", "      return true || pintuMati(")], ['★T3']),
    ('kasir@ boleh lagi membuat piutangMutasi (jalur kasir.html)', [("      allow create: if (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi',",
                                                                      "      allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi',")], ['★K3']),
    ('foto bon jenis apa saja', [("        && request.resource.data.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp']\n", "\n")], ['★F5']),
    ('permintaan nego atas nama orang lain', [(" && d.get('negoUid', '') == request.auth.uid", "")], ['★N4']),
    ('batu nisan tanpa cap jam server', [("      allow create, update: if owner() && request.resource.data.capServer == request.time;", "      allow create, update: if owner();")], ['★B6', 'S-B2']),
    ('saldo pembuka di koleksi mana pun', [("      return kol in ['batchMasuk', 'piutangMutasi',", "      return true || kol in ['batchMasuk', 'piutangMutasi',")], ['★P23']),
    ('salinan arsip tidak diikat ke catatan aslinya', [(" || salinanAsli(d))));", " || true)));")], ['★P22']),
    ('staf membaca batu nisan', [("    match /batuNisan/{id} {\n      allow read: if owner();", "    match /batuNisan/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);")], ['★B4']),
    # sanggahan bukti emulator 7 Okt: suku baru yang dulu hanya diperiksa kasusnya (★P25 juga DITOLAK di v6 — kepekaannya pada suku v7 dibuktikan di sini)
    ('pintuTitik selalu benar (titik kas bulan terkunci tanpa syarat)', [("      return y > 0 && bulanDok(d, 'tanggal') <= y * 12 + 12 && (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));",
                                                                         "      return true || y > 0 && bulanDok(d, 'tanggal') <= y * 12 + 12 && (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));")],
     ['★P25', 'M-P24d']),
    ('titik kas kembali = titikSebelum tanpa pembanding kantong (tanggal saja)', [("      return s is map && d.get('tanggal', '') == s.get('tanggal', null) && d.get('laci', null) == s.get('laci', null)", "      return s is map && d.get('tanggal', '') == s.get('tanggal', null) && (true || d.get('laci', null) == s.get('laci', null)"),
                                                                                   ("\n        && d.get('rekening', null) == s.get('rekening', null) && d.get('amplop', null) == s.get('amplop', null);", "\n        && d.get('rekening', null) == s.get('rekening', null) && d.get('amplop', null) == s.get('amplop', null));")], ['★P25']),
    ('titik kas tanpa cabang titikSebelum (Batalkan tidak bisa mengembalikan titik kas)', [("(d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));", "(d.get('tanggal', '') == string(y) + '-12-31');")], ['★P26']),
    ('titik kas tanpa cabang 31 Des (kunci tidak bisa menulis titik tutup buku)', [("(d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));", "(titikSebelum(y, d));")], ['★P5']),
    ('ulangKasirBercap tanpa pembanding isi (kirim ulang kasir@ boleh mengubah nota)', [("      return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer'])\n        && (!request.resource.data",
                                                                                       "      return (!request.resource.data")], ['★B1', 'M-B8']),
    ('berita acara baru tanpa syarat mode & status', [(" && d.get('mode', '') == 'sungguhan' && d.get('status', '') in ['berjalan', 'terkunci']\n        && p is string", "\n        && p is string")], ['M-T8']),
    ('berita acara baru tanpa syarat tahun lampau', [(" && d.tahun < wib().year() && d.get('mode', '')", " && d.get('mode', '')")], ['★T5']),
    ('berita acara baru tanpa syarat id = tahun', [(" && id == string(d.tahun) && d.tahun < wib().year()", " && d.tahun < wib().year()")], ['M-T9']),
    ('hapus berita acara tanpa syarat "dibatalkan"', [("      allow delete: if owner() && resource.data.get('status', '') == 'dibatalkan';", "      allow delete: if owner();")], ['★T4']),
    ('permintaan nego staf tanpa syarat status "menunggu"', [(" && d.get('status', '') == 'menunggu' && d.get('negoUid', '')", " && d.get('negoUid', '')")], ['★N5']),
    ('permintaan nego staf tanpa syarat tindakan "nego"', [("return stafBuat(peranBoleh) && d.get('tindakan', '') == 'nego' && ", "return stafBuat(peranBoleh) && ")], ['★N7']),
    ('permintaan nego staf boleh menulis kolom keputusan', [("d.get('negoUid', '') == request.auth.uid\n        && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);", "d.get('negoUid', '') == request.auth.uid;")], ['★N6']),   # v8: jangkar dipersempit (stafUsulHarga punya ekor yang sama)
    ('berita acara boleh mundur (selesai → terkunci)', [("'terkunci>membatalkan', 'terkunci>selesai', ", "'terkunci>membatalkan', 'terkunci>selesai', 'selesai>terkunci', ")], ['H★B16']),
]
# ---- V8 (B1, owner 16 Nov 2026): kasus ★H docs/uji-rules-v8.md (periksa_rules.KASUS_V8) atas firestore.rules (v8) dan atas firestore.rules.v7 — yang berbeda
# WAJIB persis periksa_rules.BEDA_V7 (yang dibuka v8). Kontrol: satu suku v8 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V8 = [
    ('usul harga atas nama orang lain (tanpa usulUid)', [(" && d.get('usulUid', '') == request.auth.uid", "")], ['★H7']),
    ('usul harga tanpa syarat status "menunggu"', [("d.get('tindakan', '') == 'hargaPelanggan' && d.get('status', '') == 'menunggu' && ", "d.get('tindakan', '') == 'hargaPelanggan' && ")], ['★H8']),
    ('usul harga dicabut dari create persetujuan', [(" || stafUsulHarga(['ben', 'karyawan']) ||", " ||")], ['★H3']),
    ('setelan harga tingkat tidak terbaca staf', [("'perangkat', 'hargaTingkat', 'produkArsip']", "'perangkat', 'produkArsip']")], ['★H1']),
    ('setelan HET ikut terbaca staf', [("'hargaTingkat', 'produkArsip'] && staf(", "'hargaTingkat', 'produkArsip', 'het'] && staf(")], ['★H12']),
    ('staf boleh menulis setelan harga tingkat', [("      allow update: if owner() && (id != 'kunciPeriode' || kunciGeser());",
                                                   "      allow update: if (owner() && (id != 'kunciPeriode' || kunciGeser())) || (id == 'hargaTingkat' && staf(['ben', 'karyawan']));")], ['★H11']),
]
# ---- V9 (B2, owner 17 Nov 2026): kasus ★J docs/uji-rules-v9.md (periksa_rules.KASUS_V9) atas firestore.rules (v9) dan atas firestore.rules.v8 — yang berbeda
# WAJIB persis periksa_rules.BEDA_V8 (yang dibuka v9). Kontrol: satu suku v9 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V9 = [
    ('minta bon atas nama orang lain (tanpa mintaUid)', [("d.get('tindakan', '') == 'kredit' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid", "d.get('tindakan', '') == 'kredit' && d.get('status', '') == 'menunggu'")], ['★J4']),   # v13: jangkar khusus kredit (titipan & pesan juga ber-mintaUid)
    ('minta bon tanpa syarat status "menunggu"', [("d.get('tindakan', '') == 'kredit' && d.get('status', '') == 'menunggu' && ", "d.get('tindakan', '') == 'kredit' && ")], ['★J5']),
    ('minta bon dicabut dari create persetujuan', [(" || stafMintaKredit(['ben']) ||", " ||")], ['★J1']),   # v13: baris create bersambung
    ('minta bon dibuka untuk karyawan', [("stafMintaKredit(['ben']) ||", "stafMintaKredit(['ben', 'karyawan']) ||")], ['★J8']),
]
# ---- V10 (B3, owner 18 Nov 2026): kasus ★L docs/uji-rules-v10.md (periksa_rules.KASUS_V10) atas firestore.rules (v10) dan atas firestore.rules.v9 — yang
# berbeda WAJIB persis periksa_rules.BEDA_V9 (yang dibuka v10). Kontrol: satu suku v10 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V10 = [
    ('surat jalan dibuat karyawan', [("stafBuatSJ(['ben']);", "stafBuatSJ(['ben', 'karyawan']);")], ['★L8']),
    ('surat jalan baru tanpa syarat "berangkat"', [("return stafBuat(peranBoleh) && d.get('status', '') == 'berangkat'\n", "return stafBuat(peranBoleh)\n")], ['★L9']),
    ('pengantar boleh mengubah tagihan', [("affectedKeys().hasOnly(['status', 'riwayatStatus', 'penerima',", "affectedKeys().hasOnly(['status', 'riwayatStatus', 'tagihRp', 'penerima',")], ['★L11']),
    ('tandai tanpa syarat masih di jalan', [("        && resource.data.get('status', '') == 'berangkat' && request.resource.data.get('status', '') in ['diterima', 'gagal']", "        && request.resource.data.get('status', '') in ['diterima', 'gagal']")], ['★L12']),
    ('pengantar boleh membatalkan', [("request.resource.data.get('status', '') in ['diterima', 'gagal']", "request.resource.data.get('status', '') in ['diterima', 'gagal', 'batal']")], ['★L13']),
    ('bukti terima jenis apa saja', [("\n        && d.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp'] && d.get('base64', 0) is string", "\n        && d.get('base64', 0) is string")], ['★L19']),
]
# ---- V11 (B4, owner 18 Nov 2026): kasus ★M docs/uji-rules-v11.md (periksa_rules.KASUS_V11) atas firestore.rules (v11) dan atas firestore.rules.v10 — yang
# berbeda WAJIB persis periksa_rules.BEDA_V10 (yang dibuka v11). Kontrol: satu suku v11 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V11 = [
    ('pesanan dibuat karyawan', [("stafBuatPesanan(['ben']);", "stafBuatPesanan(['ben', 'karyawan']);")], ['★M8']),
    ('pesanan baru boleh sudah bernota', [(" && d.get('trxIdJual', null) == null", "")], ['★M10']),
    ('Ben boleh mengganti nama pemesan', [("affectedKeys().hasOnly(['status', 'riwayatStatus', 'baris',", "affectedKeys().hasOnly(['status', 'riwayatStatus', 'namaPelanggan', 'baris',")], ['★M13']),
    ('pesanan batal boleh dihidupkan lagi', [("resource.data.get('status', '') in ['dipesan', 'diantar'] && request", "resource.data.get('status', '') in ['dipesan', 'diantar', 'batal'] && request")], ['★M15']),
    ('pembuat jadwal boleh diganti', [("affectedKeys().hasOnly(['namaPelanggan', 'baris',", "affectedKeys().hasOnly(['olehUid', 'namaPelanggan', 'baris',")], ['★M20']),
    ('jadwal dibuat karyawan', [("allow create: if owner() || stafBuat(['ben']);\n      allow update: if owner() || stafUbahRutin(['ben']);", "allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update: if owner() || stafUbahRutin(['ben']);")], ['★M21']),
]
# ---- V12 (paket S2b tanda kenal, owner 19 Nov 2026): kasus ★S docs/uji-rules-v12.md (periksa_rules.KASUS_V12) atas firestore.rules (v12) dan atas
# firestore.rules.v11 — yang berbeda WAJIB persis periksa_rules.BEDA_V11 (yang dibuka v12). Kontrol: satu suku v12 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V12 = [
    ('tanda kenal dibuat staf atas nama siapa saja', [("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || staf(['ben', 'karyawan']);\n      allow update, delete: if owner();")], ['★S6']),
    ('staf boleh mengubah & menghapus tanda kenal', [("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner() || staf(['ben', 'karyawan']);")], ['★S7', '★S8']),
    ('kasir@ membaca tanda kenal', [("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || kasir() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();")], ['★S10']),
    ('tanda kenal dibuka hanya untuk ben', [("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben']);\n      allow update, delete: if owner();")], ['★S5']),
]
# ---- V13 (owner 21 Nov 2026: titipan uang keluar & pesan dari tablet + token notifikasi HP owner): kasus ★U docs/uji-rules-v13.md (periksa_rules.KASUS_V13)
# atas firestore.rules (v13) dan atas firestore.rules.v12 — yang berbeda WAJIB persis periksa_rules.BEDA_V12 (yang dibuka v13). Kontrol: satu suku v13 dirusak →
# kasus sasarannya wajib berbalik.
KONTROL_V13 = [
    ('titipan atas nama siapa saja', [(" && d.get('mintaUid', '') == request.auth.uid\n        && d.get('jenis', '') in", "\n        && d.get('jenis', '') in")], ['★U7']),
    ('titipan jenis apa saja', [("\n        && d.get('jenis', '') in ['toko', 'karyawan', 'kasbon', 'bongkar', 'bayarBon'] && d.get('nominal', 0) is int", "\n        && d.get('nominal', 0) is int")], ['★U10']),   # v15: + bongkar & bayarBon
    ('nominal titipan boleh pecahan', [(" && d.get('nominal', 0) is int && d.get('nominal', 0) > 0", " && d.get('nominal', 0) > 0")], ['★U12']),
    ('titipan boleh membawa betulan owner', [("'alasanTolak', 'koreksiOwner', 'balasan']);", "'alasanTolak']);")], ['★U9']),
    ('pesan tanpa batas panjang', [(" && d.teks.size() <= 500", "")], ['★U17']),
    ('karyawan tidak bisa menitip', [("stafMintaKeluar(['ben', 'karyawan'])", "stafMintaKeluar(['ben'])")], ['★U5']),
    ('token notifikasi owner terbaca staf', [("    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow write: if owner();")], ['★U20']),
]
# ---- V14 (owner 21 Nov 2026: data uang untuk Ringkas hari ini di tablet): kasus ★W docs/uji-rules-v14.md (periksa_rules.KASUS_V14) atas firestore.rules (v14)
# dan atas firestore.rules.v13 — yang berbeda WAJIB persis periksa_rules.BEDA_V13 (yang dibuka v14). Kontrol: satu suku v14 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V14 = [
    ('tanda baca uang tidak dinilai', [("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.aktif == true && a.peran == 'ben'")], ['★W15']),
    ('karyawan bertanda ikut membaca', [("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.aktif == true && a.get('bacaUang', false) == true")], ['★W16']),
    ('akun nonaktif bertanda tetap membaca', [("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.peran == 'ben' && a.get('bacaUang', false) == true")], ['★W17']),
    ('titik kas tertutup lagi untuk akun bertanda', [(" || (id == 'titikKas' && stafBacaUang())", "")], ['★W14']),
    ('uang keluar harian tertutup lagi untuk akun bertanda', [("    match /pengeluaranHarian/{id} {\n      allow read: if owner() || stafBacaUang();", "    match /pengeluaranHarian/{id} {\n      allow read: if owner();")], ['★W5']),
]
# ---- V15 (owner 22 Nov 2026: barang masuk & bayar supir di tablet): kasus ★X docs/uji-rules-v15.md (periksa_rules.KASUS_V15) atas firestore.rules (v15)
# dan atas firestore.rules.v14 — yang berbeda WAJIB persis periksa_rules.BEDA_V14 (yang dibuka v15). Kontrol: satu suku v15 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V15 = [
    ('karyawan ikut mencatat kedatangan tablet', [("(stafCatatMasuk(['ben']) && tglStaf('tanggal'))", "(stafCatatMasuk(['ben', 'karyawan']) && tglStaf('tanggal'))")], ['★X8']),
    ('kedatangan tablet boleh dibayar tunai', [("d.get('caraBayar', '') == 'utang' && d.get('biayaBongkar', -1) == 0", "d.get('biayaBongkar', -1) == 0")], ['★X9']),
    ('kedatangan tablet boleh membawa upah bongkar', [(" && d.get('biayaBongkar', -1) == 0\n", "\n")], ['★X10']),
    ('titipan upah bongkar tanpa kedatangan', [("        && (d.get('jenis', '') != 'bongkar' || (d.get('batchId', 0) is string && d.batchId.size() > 0))\n", "")], ['★X17']),
    ('kabar barang masuk untuk karyawan', [("stafKabarMasuk(['ben']) || (stafHitungLaci(", "stafKabarMasuk(['ben', 'karyawan']) || (stafHitungLaci(")], ['★X23']),   # v16: baris create bersambung
]
# ---- V16 (owner 22 Nov 2026: tutup hari dari tablet): kasus ★Y docs/uji-rules-v16.md (periksa_rules.KASUS_V16) atas firestore.rules (v16)
# dan atas firestore.rules.v15 — yang berbeda WAJIB persis periksa_rules.BEDA_V15 (yang dibuka v16). Kontrol: satu suku v16 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V16 = [
    ('karyawan ikut mengirim hitungan laci', [("(stafHitungLaci(['ben']) && tglStaf('tanggal'))", "(stafHitungLaci(['ben', 'karyawan']) && tglStaf('tanggal'))")], ['★Y6']),
    ('hitungan laci boleh nol', [("d.get('hitung', 0) is int && d.get('hitung', 0) > 0 &&", "d.get('hitung', 0) is int && d.get('hitung', 0) >= 0 &&")], ['★Y8']),
    ('brankas boleh melebihi hitungan', [(" && d.get('amankan', -1) <= d.get('hitung', 0)\n", "\n")], ['★Y9']),
    ('hitungan tanpa penjaga bulan', [("(stafHitungLaci(['ben']) && tglStaf('tanggal'))", "stafHitungLaci(['ben'])")], ['★Y14']),
    ('aturan tutup hari terbaca karyawan', [("(id == 'tutupHari' && staf(['ben']))", "(id == 'tutupHari' && staf(['ben', 'karyawan']))")], ['★Y7']),
]
# ---- V17 (owner 23 Nov 2026: push aplikasi tablet): kasus ★Z docs/uji-rules-v17.md (periksa_rules.KASUS_V17) atas firestore.rules (v17)
# dan atas firestore.rules.v16 — yang berbeda WAJIB persis periksa_rules.BEDA_V16 (yang dibuka v17). Kontrol: satu suku v17 dirusak → kasus sasarannya wajib berbalik.
KONTROL_V17 = [
    ('token atas nama akun lain', [("return stafBuat(peranBoleh) && d.get('uid', '') == request.auth.uid && d.get('perangkatId'", "return stafBuat(peranBoleh) && d.get('perangkatId'")], ['★Z7']),
    ('id dokumen tidak terikat uid penulis', [("        && id == request.auth.uid + '_' + d.perangkatId && d.get('token'", "        && d.get('token'")], ['★Z8']),
    ('kolom token bebas', [(" && d.keys().hasOnly(['id', 'uid', 'olehUid', 'perangkatId', 'token', 'platform', 'perangkat', 'pada']);", ";")], ['★Z9']),
    ('platform bebas', [(" && d.get('platform', '') == 'android'\n", "\n")], ['★Z10']),
    ('Penjaga laci membaca token', [("      allow read, delete: if owner();\n      allow create, update: if owner() || stafTokenPush", "      allow read: if owner() || staf(['ben']);\n      allow delete: if owner();\n      allow create, update: if owner() || stafTokenPush")], ['★Z11']),
]
# ---- V18 (owner 24 Nov 2026, tinjauan 30 Sep (d): denyut staf terikat penulisnya): kasus ★V docs/uji-rules-v18.md (periksa_rules.KASUS_V18) atas
# firestore.rules (v18) dan atas firestore.rules.v17 — yang berbeda WAJIB persis periksa_rules.BEDA_V17 (yang ditutup v18). Kontrol: satu suku v18 dirusak.
KONTROL_V18 = [
    ('denyut staf tidak terikat id perangkat~uid', [("        && id.matches('[^~/]{1,40}~' + request.auth.uid) && request.resource.data.get('id', '') == id\n", "")], ['★V8', '★V10']),
    ('denyut lama tanpa akunUid bisa ditimpa', [("(resource == null || resource.data.get('akunUid', '') == request.auth.uid)", "(resource == null || resource.data.get('akunUid', request.auth.uid) == request.auth.uid)")], ['★V7']),
    ('kolom id boleh beda dari id dokumen', [(" && request.resource.data.get('id', '') == id\n", "\n")], ['★V9']),
]
# kontrol bagian C: suku kirim ulang bercap dicabut dari update penjualan → kirim ulang kasir-v33 & kasir-v32 atas nota bercap wajib berbunyi
KONTROL_KASIR = ('suku (kasir() && ulangKasirBercap()) dicabut dari update penjualan', [(" || (kasir() && ulangKasirBercap());", ";")], ['c2', 'c4'])


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


def rusak(teks, ganti):
    for lama, baru in ganti:
        if teks.count(lama) != 1: raise ValueError('KONTROL BASI — jangkar tidak tepat 1× di rules: ' + lama.strip()[:90])
        teks = teks.replace(lama, baru, 1)
    return teks


# ============================== kolom "Wajib" docs/uji-rules-v7.md ==============================
def wajib_dok(teks=None):
    """{'★X': True (LOLOS) / False (DITOLAK)} dari tiap baris tabel ★ (Wajib owner & opsional). Sel bergaris tegak ber-escape (\\|) tidak dipotong."""
    out = {}
    for baris in (teks if teks is not None else baca(DOK)).split('\n'):
        m = re.match(r'^\|(?: \d+ \|)? (★[A-Z]\d+) \|', baris)
        if not m: continue
        sel = [x.strip() for x in re.split(r'(?<!\\)\|', baris)[1:-1]]
        w = [x for x in sel if x in ('LOLOS', 'DITOLAK')]
        out[m.group(1)] = (w[0] == 'LOLOS') if len(w) == 1 else None
    return out


# ============================== geser waktu ke jam runner ==============================
TAHUN_MODEL = int(P.HARI_INI[:4])   # 2026 — tahun "hari ini" dokumen uji model (JAM_UJI_V7): 2025 = tahun lalu, 2026 = tahun berjalan
GESER_TAHUN = True                  # kontrol: False = tahun dokumen uji TIDAK digeser (cek "dokumen uji digeser ke jam lain" wajib berbunyi)
_TAHUN = re.compile(r'^(20\d\d)(?=$|[-| ])')


class Jam:
    """Jam runner (= jam emulator, mesin yang sama): hari ini & kemarin WIB, tahun WIB, selisih tahun terhadap dokumen uji model."""
    def __init__(self, ms=None):
        self.ms = int(ms if ms is not None else time.time() * 1000)
        d = datetime.datetime.fromtimestamp(self.ms / 1000.0, WIB)
        self.hari_ini = d.date().isoformat(); self.kemarin = (d.date() - datetime.timedelta(days=1)).isoformat(); self.tahun = d.year
        self.selisih = (self.tahun - TAHUN_MODEL) if GESER_TAHUN else 0
        self.iso = datetime.datetime.fromtimestamp(self.ms / 1000.0, datetime.timezone.utc).isoformat()


def geser_teks(s, J):
    """teks berawalan tahun (tanggal '2021-06-15', bulan '2021-12', id '2024', id arsip '2021|penjualan|x', jam '2026-10-01 00:00') → tahun + selisih."""
    m = _TAHUN.match(s)
    return str(int(m.group(1)) + J.selisih) + s[4:] if m and J.selisih else s


def geser_jalur(jalur, J): return '/'.join(geser_teks(x, J) for x in jalur.split('/'))


def geser(v, J, kunci=None):
    """Nilai kasus model (jam uji 9 Okt 2026 03.00Z) → nilai di jam runner. Cap = jam uji persis → SERVER (transform REQUEST_TIME); jam relatif (besok,
    5 hari lagi, 1 jam lalu, 1 menit lalu) → relatif ke jam runner; jam mutlak (2020, 2100) tetap; "hari ini" (juga awalan jam "hari ini T…" / "hari ini
    00:00") & titik kas kemarin → tanggal WIB runner; TAHUN (kolom tahun / tahunDari, teks berawalan tahun) → + selisih tahun runner − 2026."""
    if isinstance(v, TS):
        if v.ms == JAM.ms: return SERVER
        d = v.ms - JAM.ms
        return TS(J.ms + d) if abs(d) <= 10 * 86400000 else v
    if isinstance(v, dict): return {k: geser(x, J, k) for k, x in v.items()}
    if isinstance(v, list): return [geser(x, J) for x in v]
    if isinstance(v, bool): return v
    if isinstance(v, int): return v + J.selisih if kunci in ('tahun', 'tahunDari') else v
    if isinstance(v, str):
        if v == P.HARI_INI: return J.hari_ini
        if v.startswith(P.HARI_INI + 'T') or v.startswith(P.HARI_INI + ' '): return J.hari_ini + v[len(P.HARI_INI):]
        if v == P.DB_UJI_V7['pengaturan/titikKas']['tanggal']: return J.kemarin
        return geser_teks(v, J)
    return v


# ============================== REST emulator ==============================
def ke_nilai(v):
    if v is None: return {'nullValue': None}
    if isinstance(v, bool): return {'booleanValue': v}
    if isinstance(v, int): return {'integerValue': str(v)}
    if isinstance(v, float): return {'doubleValue': v}
    if isinstance(v, str): return {'stringValue': v}
    if isinstance(v, TS): return {'timestampValue': datetime.datetime.fromtimestamp(v.ms / 1000.0, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + '%03dZ' % (v.ms % 1000)}
    if isinstance(v, list): return {'arrayValue': {'values': [ke_nilai(x) for x in v]}}
    if isinstance(v, dict): return {'mapValue': {'fields': {k: ke_nilai(x) for k, x in v.items()}}}
    raise TypeError('nilai tidak dikenal: %r' % (v,))


def ke_kolom(d):
    """isi → (fields, [kolom transform REQUEST_TIME]). SERVER hanya boleh di tingkat atas (capServer)."""
    f, t = {}, []
    for k, v in d.items():
        if v == SERVER: t.append(k)
        else: f[k] = ke_nilai(v)
    return f, t


def dari_nilai(n):
    if 'nullValue' in n: return None
    if 'booleanValue' in n: return n['booleanValue']
    if 'integerValue' in n: return int(n['integerValue'])
    if 'doubleValue' in n: return float(n['doubleValue'])
    if 'stringValue' in n: return n['stringValue']
    if 'timestampValue' in n: return {'__ts': n['timestampValue']}
    if 'arrayValue' in n: return [dari_nilai(x) for x in n['arrayValue'].get('values', [])]
    if 'mapValue' in n: return {k: dari_nilai(x) for k, x in n['mapValue'].get('fields', {}).items()}
    return n


def rest(metode, url, data=None, kepala=None, waktu=60):
    """→ (kode HTTP, isi JSON atau teks). HTTPError TIDAK dilempar — kode 403 adalah hasil kasus."""
    body = None if data is None else json.dumps(data).encode('utf-8')
    h = {'Content-Type': 'application/json'}; h.update(kepala or {})
    req = urllib.request.Request(url, data=body, method=metode, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=waktu) as r: kode, t = r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e: kode, t = e.code, e.read().decode('utf-8', 'replace')
    try: isi = json.loads(t) if t.strip()[:1] in ('{', '[') else t
    except ValueError: isi = t
    return kode, isi


def wajib_ok(kode, isi, apa):
    if not 200 <= kode < 300: raise RuntimeError('%s → HTTP %s: %s' % (apa, kode, json.dumps(isi)[:400] if not isinstance(isi, str) else isi[:400]))
    return isi


def tunggu_emulator(batas=180):
    t0 = time.time(); g = ''
    while time.time() - t0 < batas:
        try:
            kode, _ = rest('GET', FS + '/', waktu=5)
            if kode < 500: return
        except Exception as e: g = str(e)
        time.sleep(1)
    raise RuntimeError('emulator tidak menjawab dalam %d dtk: %s' % (batas, g))


def pasang_aturan(teks):
    kode, isi = rest('PUT', FS + '/emulator/v1/projects/%s:securityRules' % PROYEK, {'rules': {'files': [{'name': 'firestore.rules', 'content': teks}]}})
    wajib_ok(kode, isi, 'pasang rules')
    galat = [x for x in ((isi or {}).get('issues') or []) if str(x.get('severity', '')).upper() == 'ERROR'] if isinstance(isi, dict) else []
    if galat: raise RuntimeError('rules ditolak emulator: %s' % json.dumps(galat)[:600])


def kosongkan():
    wajib_ok(*rest('DELETE', FS + '/emulator/v1/projects/%s/databases/(default)/documents' % PROYEK), apa='kosongkan emulator')


def nama_dok(jalur): return DB + '/documents/' + jalur


def isi_admin(db):
    """dokumen uji lewat jalur admin (Bearer owner — rules tidak menilai), satu commit."""
    if not db: return
    w = []
    for jalur, d in db.items():
        f, t = ke_kolom(d)
        if t: raise ValueError('dokumen uji %s memakai cap jam server — tidak bisa lewat admin' % jalur)
        w.append({'update': {'name': nama_dok(jalur), 'fields': f}})
    wajib_ok(*rest('POST', FS + '/v1/' + DB + '/documents:commit', {'writes': w}, ADMIN), apa='isi dokumen uji')


def ambil_admin(jalur):
    kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + '/'.join(urllib.parse.quote(x, safe='') for x in jalur.split('/')), kepala=ADMIN)
    if kode == 404: return None
    wajib_ok(kode, isi, 'baca ' + jalur)
    return {k: dari_nilai(v) for k, v in (isi.get('fields') or {}).items()}


def token(akun):
    """id token emulator: JWT alg none (tanpa tanda tangan) — uid & email persis tabel "Isian Playground". Hanya emulator yang menerimanya."""
    kini = int(time.time())
    b = lambda o: base64.urlsafe_b64encode(json.dumps(o, separators=(',', ':')).encode('utf-8')).rstrip(b'=').decode('ascii')
    muatan = {'iss': 'https://securetoken.google.com/' + PROYEK, 'aud': PROYEK, 'iat': kini - 60, 'auth_time': kini - 60, 'exp': kini + 3600,
              'sub': akun['uid'], 'user_id': akun['uid'], 'email': akun['email'], 'email_verified': True,
              'firebase': {'sign_in_provider': 'password', 'identities': {'email': [akun['email']]}}}
    return b({'alg': 'none', 'typ': 'JWT'}) + '.' + b(muatan) + '.'


def operasi(op, kol, id_, data, akun):
    """SATU operasi kasus dengan token akun → ('LOLOS' | 'DITOLAK' | 'GALAT', keterangan)."""
    k = {'Authorization': 'Bearer ' + token(akun)}
    komit = FS + '/v1/' + DB + '/documents:commit'
    if op in ('create', 'update'):
        f, t = ke_kolom(data)
        w = {'update': {'name': nama_dok(kol + '/' + id_), 'fields': f}, 'currentDocument': {'exists': op == 'update'}}
        if t: w['updateTransforms'] = [{'fieldPath': x, 'setToServerValue': 'REQUEST_TIME'} for x in t]
        kode, isi = rest('POST', komit, {'writes': [w]}, k)
    elif op == 'delete': kode, isi = rest('POST', komit, {'writes': [{'delete': nama_dok(kol + '/' + id_)}]}, k)
    elif op == 'get': kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + kol + '/' + urllib.parse.quote(id_, safe=''), kepala=k)
    elif op == 'list': kode, isi = rest('GET', FS + '/v1/' + DB + '/documents/' + kol + '?pageSize=5', kepala=k)
    else: raise ValueError(op)
    ket = '' if 200 <= kode < 300 else ('HTTP %d %s' % (kode, (isi.get('error') or {}).get('status', '') if isinstance(isi, dict) else str(isi)[:80]))
    if 200 <= kode < 300 or (kode == 404 and op == 'get'): return 'LOLOS', ket or ('dokumen tidak ada (izin baca lolos)' if kode == 404 else '')
    if kode == 403 and 'PERMISSION_DENIED' in json.dumps(isi): return 'DITOLAK', ket
    return 'GALAT', ket + ' ' + json.dumps(isi)[:300]


# ============================== bagian A: kasus ==============================
def isi_kasus(K, J):
    """→ (id dokumen, isi operasi, dokumen uji) di jam J. Kasus H (hanya maju): dokumen ujinya sendiri, tanpa jam — tidak digeser."""
    no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
    if no in BUKU: return id_, data, dict(ubah_db)
    db = dict(P.DB_UJI_V7); db.update(ubah_db or {})
    db = {geser_jalur(k, J): geser(v, J) for k, v in db.items() if v is not None}
    if op == 'create': db.pop(geser_jalur(kol + '/' + id_, J), None)   # create = dokumen belum ada (Playground: isian apa adanya)
    return geser_teks(id_, J), (geser(data, J) if data is not None else None), db


def jalankan_kasus(K, J, wajib):
    no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
    harap = wajib.get(no, boleh)
    r = {'no': no, 'nama': nama, 'akun': aud, 'op': op, 'jalur': kol + '/' + id_, 'wajib': 'LOLOS' if harap else 'DITOLAK'}
    try:
        idg, isi, db = isi_kasus(K, J)
        if idg != id_: r['jalurDigeser'] = kol + '/' + idg
        kosongkan(); isi_admin(db)
        h, ket = operasi(op, kol, idg, isi, P.AKUN_UJI[aud])
    except Exception as e: h, ket = 'GALAT', 'alat uji: ' + str(e)[:300]
    r.update(hasil=h, ket=ket, ok=(h == r['wajib']))
    return r


def ke_model(v, jam):
    """isi emulator (SERVER = transform REQUEST_TIME) → isi penafsir mini (cap = jam permintaan)."""
    if isinstance(v, str) and v == SERVER: return jam
    if isinstance(v, dict): return {k: ke_model(x, jam) for k, x in v.items()}
    if isinstance(v, list): return [ke_model(x, jam) for x in v]
    return v


def nilai_model(M, K, J=None):
    """penafsir mini atas kasus K: J None = dokumen uji model apa adanya (jam JAM_UJI_V7); J = digeser ke jam J persis seperti di emulator."""
    no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks = K
    if J is None:
        db = dict(ubah_db) if no in BUKU else dict(P.DB_UJI_V7, **(ubah_db or {}))
        return M.nilai(op, kol, id_, auth=P.AKUN_UJI[aud], data=data, sebelum={k: v for k, v in db.items() if v is not None}, jam=JAM)
    jam = TS(J.ms); idg, isi, db = isi_kasus(K, J)
    return M.nilai(op, kol, idg, auth=P.AKUN_UJI[aud], data=ke_model(isi, jam), sebelum=ke_model(db, jam), jam=jam)


def jalankan_semua(J, teks_rules, kasus=None):
    pasang_aturan(teks_rules); w = wajib_dok()
    return [jalankan_kasus(K, J, w) for K in (kasus or KASUS)]


# ============================== bagian C: kasir darurat (kode asli, node) ==============================
def skrip_halaman(html):
    """skrip sebaris kasir darurat (yang memuat kirimAntrean) — satu-satunya <script> tanpa atribut yang berisi mesin kirim."""
    xs = [s for s in re.findall(r'<script>(.*?)</script>', html, re.S) if 'function kirimAntrean' in s]
    if len(xs) != 1: raise ValueError('skrip kirimAntrean di kasir darurat: %d (harus 1)' % len(xs))
    return xs[0]


def html_v32():
    """kasir-darurat-nominal.html di KASIR_V32_COMMIT → teks, atau None bila commit tidak terbaca. Checkout CI dangkal (job uji Pages): di GitHub Actions
    commit itu diambil SENDIRI (git fetch --depth=1 commit itu — hanya bila repo dangkal; repo penuh di Mac tidak disentuh), supaya cek kasir-v32 diukur
    juga di sana, bukan lulus kosong (sanggahan 7 Okt)."""
    def tunjuk():
        try: t = subprocess.run(['git', 'show', KASIR_V32_COMMIT + ':kasir-darurat-nominal.html'], cwd=AKAR, capture_output=True, text=True, timeout=60)
        except Exception: return None
        return t.stdout if t.returncode == 0 and t.stdout else None
    h = tunjuk()
    if h is None and os.environ.get('GITHUB_ACTIONS') == 'true':
        try:
            if subprocess.run(['git', 'rev-parse', '--is-shallow-repository'], cwd=AKAR, capture_output=True, text=True, timeout=30).stdout.strip() == 'true':
                subprocess.run(['git', 'fetch', '--no-tags', '--depth=1', 'origin', KASIR_V32_COMMIT], cwd=AKAR, capture_output=True, text=True, timeout=180)
        except Exception: pass
        h = tunjuk()
    return h


def node_kasir(skrip, simpanan, aksi=None):
    """kasir_emulator.js di node (runner) → hasil {permintaan, antrean, ditolak, simpanan, antreanSesudahCatat, …}."""
    d = tempfile.mkdtemp(prefix='kasir-emulator-')
    try:
        ps = os.path.join(d, 'skrip.js'); open(ps, 'w', encoding='utf-8').write(skrip)
        pm = os.path.join(d, 'minta.json')
        json.dump({'skrip': ps, 'simpanan': simpanan, 'aksi': aksi, 'emulator': FS_HOST, 'proyekHalaman': PROYEK_HALAMAN, 'proyekEmulator': PROYEK}, open(pm, 'w', encoding='utf-8'))
        r = subprocess.run(['node', os.path.join(SINI, 'kasir_emulator.js'), pm], capture_output=True, text=True, timeout=180, env=dict(os.environ, TZ='Asia/Jakarta'))
        baris = [x for x in r.stdout.strip().split('\n') if x.startswith('{')]
        if not baris: return {'galat': 'node tanpa hasil: ' + (r.stderr or r.stdout)[-800:]}
        return json.loads(baris[-1])
    finally: shutil.rmtree(d, ignore_errors=True)


def tulisan_nota(h):
    """permintaan tulis ke penjualan dari satu jalan halaman → [{'cara': 'commit'|'patch'|'patch-mask', 'status', 'cap': transform REQUEST_TIME, 'mask'}]."""
    out = []
    for x in h.get('permintaan') or []:
        u = x.get('url', '')
        if ':commit' in u:
            try: w = json.loads(x.get('badan') or '{}')['writes'][0]
            except Exception: w = {}
            if '/documents/penjualan/' not in (w.get('update') or {}).get('name', ''): continue
            out.append({'cara': 'commit', 'status': x.get('status'), 'cap': [t.get('fieldPath') + '=' + str(t.get('setToServerValue')) for t in w.get('updateTransforms') or []],
                        'mask': bool(w.get('updateMask')), 'kunci': x.get('kunci')})
        elif x.get('metode') == 'PATCH' and '/documents/penjualan/' in u:
            out.append({'cara': 'patch-mask' if 'updateMask.fieldPaths=' in u else 'patch', 'status': x.get('status'), 'cap': [], 'mask': 'updateMask.fieldPaths=' in u, 'kunci': x.get('kunci')})
    return out


def simpanan_awal():
    kasir = P.AKUN_UJI['kasir']
    return {'kasir_auth_v1': json.dumps({'refreshToken': 'uji-emulator', 'idToken': token(kasir), 'kedaluwarsa': int(time.time() * 1000) + 3000 * 1000})}


def dengan_antrean(simpanan, item):
    s = dict(simpanan); s['darurat_antrean_v1'] = json.dumps([item]); return s


def tanpa_cap(d): return {k: v for k, v in (d or {}).items() if k != 'capServer'}


def cap(d): return ((d or {}).get('capServer') or {}).get('__ts') if isinstance((d or {}).get('capServer'), dict) else None


def detik(ts):
    """timestampValue REST ('…Z', pecahan detik sampai 9 angka) → detik epoch (None bila kosong)."""
    if not ts: return None
    m = re.match(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?Z$', ts)
    if not m: return None
    return datetime.datetime.fromisoformat(m.group(1) + '+00:00').timestamp() + (float('0' + m.group(2)) if m.group(2) else 0.0)


def isi_sama(dok, item):
    """isi dokumen server (tanpa capServer) = isi karcis (kolom & nilai; angka pecahan id dibandingkan sebagai angka)."""
    return json.dumps(tanpa_cap(dok), sort_keys=True) == json.dumps(item['data'], sort_keys=True)


def jalur_kasir(v33, v32, aturan):
    """aturan 'v7' | 'v6' | 'kontrol' — langkah c1…c6 di emulator kosong; → (langkah, cek [(id, nama, ok, ket)])."""
    kosongkan(); c = []; L = {}
    s0 = simpanan_awal(); kini0 = time.time()
    # c1 · nota baru (kasir-v33): simpanNominal → kirimAntrean → :commit + capServer REQUEST_TIME
    h1 = node_kasir(v33, s0, {'nota': 15000}); L['c1'] = h1
    item = (h1.get('antreanSesudahCatat') or [None])[0]
    if not item or h1.get('galat'):
        c.append(('c1', 'kasir-v33 mencatat nota baru (simpanNominal) & mengirimnya', False, h1.get('galat') or 'antrean kosong sesudah simpanNominal'))
        return L, c
    jalur = 'penjualan/' + item['docId']; d1 = ambil_admin(jalur); t1 = tulisan_nota(h1)
    c.append(('c1', 'kasir-v33 nota baru: SATU :commit bercap (transform capServer = REQUEST_TIME, tanpa updateMask) DITERIMA; isi server = karcis + capServer jam server',
              h1.get('versi') == 'kasir-v33' and t1 == [{'cara': 'commit', 'status': 200, 'cap': ['capServer=REQUEST_TIME'], 'mask': False, 'kunci': True}] and not h1['antrean'] and not h1['ditolak']
              and bool(d1) and isi_sama(d1, item) and detik(cap(d1)) is not None and abs(detik(cap(d1)) - kini0) < 600,
              {'versi': h1.get('versi'), 'tulisan': t1, 'antrean': len(h1['antrean']), 'ditolak': len(h1['ditolak']), 'cap': cap(d1)}))
    # c2 · kirim ulang IDENTIK (jawaban kiriman pertama hilang di jalan): karcis yang sama kembali ke antrean, halaman dibuka lagi
    h2 = node_kasir(v33, dengan_antrean(h1['simpanan'], item)); L['c2'] = h2; d2 = ambil_admin(jalur); t2 = tulisan_nota(h2)
    if aturan == 'v6':
        c.append(('c2', 'v6: kirim ulang :commit DITOLAK (cap beda, tanpa ulangKasirBercap) → cara lama PATCH updateMask MASUK; tidak pindah ke "ditolak"; cap pertama tetap (tanpa dobel)',
                  [x['cara'] + ':' + str(x['status']) for x in t2] == ['commit:403', 'patch-mask:200'] and not h2['antrean'] and not h2['ditolak'] and bool(d2) and isi_sama(d2, item) and cap(d2) == cap(d1),
                  {'tulisan': t2, 'ditolak': len(h2['ditolak']), 'cap1': cap(d1), 'cap2': cap(d2)}))
    else:
        c.append(('c2', 'kirim ulang IDENTIK kasir-v33: :commit DITERIMA (ulangKasirBercap), tanpa jatuh ke cara lama; capServer = jam server yang BARU; isi sama',
                  [x['cara'] + ':' + str(x['status']) for x in t2] == ['commit:200'] and not h2['antrean'] and not h2['ditolak'] and bool(d2) and isi_sama(d2, item)
                  and detik(cap(d2)) is not None and detik(cap(d1)) is not None and detik(cap(d2)) > detik(cap(d1)), {'tulisan': t2, 'ditolak': len(h2['ditolak']), 'cap1': cap(d1), 'cap2': cap(d2)}))
    # c3 · kirim ulang yang MENGUBAH isi (hargaTotal + 5.000): :commit ditolak, cara lama ditolak → daftar "ditolak"; server tidak berubah
    ubah = json.loads(json.dumps(item)); ubah['data']['hargaTotal'] = item['data']['hargaTotal'] + 5000
    h3 = node_kasir(v33, dengan_antrean(h2['simpanan'], ubah)); L['c3'] = h3; d3 = ambil_admin(jalur); t3 = tulisan_nota(h3)
    c.append(('c3', 'kirim ulang kasir-v33 yang MENGUBAH isi: :commit DITOLAK, cara lama (PATCH updateMask) DITOLAK → karcis di daftar "ditolak"; dokumen server tidak berubah',
              [x['cara'] + ':' + str(x['status']) for x in t3] == ['commit:403', 'patch-mask:403'] and not h3['antrean'] and len(h3['ditolak']) == len(h2['ditolak']) + 1
              and d3 == d2, {'tulisan': t3, 'ditolak': len(h3['ditolak']), 'sama': d3 == d2}))
    if v32 is None:
        c.append(('c4', 'kasir-v32 (HP penjaga sebelum cabang ini)', False, 'kasir-darurat-nominal.html di %s tidak terbaca (riwayat git dangkal?) — TIDAK TERUKUR' % KASIR_V32_COMMIT))
        return L, c
    # c4 · kasir-v32 kirim ulang IDENTIK atas nota yang sudah bercap (PATCH utuh tanpa cap — capServer terbuang). HP kasir-v32 = HP LAIN (penyimpanan sendiri,
    # daftar "ditolak" kosong): kalau memakai penyimpanan HP v33 di atas, karcis yang sama sudah ada di daftar "ditolak" (c3) dan pindahKeDitolak tidak
    # menambahkannya lagi (run 7 Okt: hitungan "ditolak" tidak bertambah di c5)
    h4 = node_kasir(v32, dengan_antrean(simpanan_awal(), item)); L['c4'] = h4; d4 = ambil_admin(jalur); t4 = tulisan_nota(h4)
    if aturan == 'v6':
        c.append(('c4', 'v6: kasir-v32 kirim ulang identik atas nota BERCAP (PATCH utuh membuang capServer) DITOLAK → pindah ke "ditolak" (sebab v7 perlu ulangKasirBercap)',
                  h4.get('versi') == 'kasir-v32' and [x['cara'] + ':' + str(x['status']) for x in t4] == ['patch:403'] and len(h4['ditolak']) == 1 and d4 == d3,
                  {'versi': h4.get('versi'), 'tulisan': t4, 'ditolak': len(h4['ditolak'])}))
        return L, c
    c.append(('c4', 'kasir-v32 kirim ulang IDENTIK atas nota bercap: PATCH utuh (tanpa updateMask) DITERIMA — capServer terbuang, isi sama; tidak pindah ke "ditolak"',
              h4.get('versi') == 'kasir-v32' and [x['cara'] + ':' + str(x['status']) for x in t4] == ['patch:200'] and not h4['antrean'] and not h4['ditolak']
              and bool(d4) and isi_sama(d4, item) and 'capServer' not in d4, {'versi': h4.get('versi'), 'tulisan': t4, 'ditolak': len(h4['ditolak']), 'cap4': cap(d4)}))
    # c5 · kasir-v32 kirim ulang yang MENGUBAH isi → ditolak, server tidak berubah
    ubah2 = json.loads(json.dumps(item)); ubah2['data']['hargaTotal'] = item['data']['hargaTotal'] + 7000
    # (HP kasir-v32 dengan penyimpanan baru lagi: hasil c5 tidak bergantung pada c4 — di kontrol c4 sengaja ditolak)
    h5 = node_kasir(v32, dengan_antrean(simpanan_awal(), ubah2)); L['c5'] = h5; d5 = ambil_admin(jalur); t5 = tulisan_nota(h5)
    c.append(('c5', 'kasir-v32 kirim ulang yang MENGUBAH isi: PATCH DITOLAK → daftar "ditolak"; dokumen server tidak berubah',
              [x['cara'] + ':' + str(x['status']) for x in t5] == ['patch:403'] and len(h5['ditolak']) == 1 and d5 == d4, {'tulisan': t5, 'ditolak': len(h5['ditolak'])}))
    # c6 · kasir-v32 nota baru (PATCH, dokumen belum ada = create kasir@) tetap masuk di v7
    h6 = node_kasir(v32, h5['simpanan'], {'nota': 20000}); L['c6'] = h6; it6 = (h6.get('antreanSesudahCatat') or [None])[0]
    d6 = ambil_admin('penjualan/' + it6['docId']) if it6 else None; t6 = tulisan_nota(h6)
    c.append(('c6', 'kasir-v32 nota baru: PATCH (create kasir@) DITERIMA, tanpa capServer', bool(it6) and [x['cara'] + ':' + str(x['status']) for x in t6] == ['patch:200'] and bool(d6) and isi_sama(d6, it6)
              and 'capServer' not in d6, {'tulisan': t6, 'ada': bool(d6)}))
    return L, c


# ============================== --emulator (runner) ==============================
def ringkas(daftar):
    n = len(daftar); ok = sum(1 for x in daftar if x['ok']); tt = sum(1 for x in daftar if x['hasil'] == 'TIDAK TERUKUR')
    return {'kasus': n, 'lulus': ok, 'gagal': n - ok - tt, 'tidakTerukur': tt}


def jalankan_emulator():
    tunggu_emulator()
    J = Jam(); v7, v6 = baca('firestore.rules'), baca('firestore.rules.v6')
    lap = {'mulai': J.iso, 'hariIni': J.hari_ini, 'selisihTahun': J.selisih, 'proyek': PROYEK, 'firebaseTools': os.environ.get('FIREBASE_TOOLS_VERSI', '?'), 'run': os.environ.get('GITHUB_RUN_ID', '')}
    print('— A · v7 (firestore.rules cabang ini): %d kasus (%d kasus Playground/model/server + %d kasus H "hanya maju") · tahun dokumen uji digeser %+d (jam runner WIB %s)'
          % (len(KASUS), len(KASUS) - len(KASUS_BUKU), len(KASUS_BUKU), J.selisih, J.hari_ini), flush=True)
    A = jalankan_semua(J, v7); lap['v7'] = A
    for x in A: print('  %s %-7s %-26s %-6s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], '', x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— A · v6 (firestore.rules.v6): kasus yang sama', flush=True)
    B = jalankan_semua(J, v6); lap['v6'] = []
    for a, b in zip(A, B):
        beda_harap = a['no'] in BEDA_V6; harap6 = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if beda_harap else a['wajib']
        r = {'no': b['no'], 'jalur': b['jalur'], 'hasilV6': b['hasil'], 'hasilV7': a['hasil'], 'harapV6': harap6, 'ubahan': BEDA_V6.get(b['no']), 'ket': b['ket'],
             'ok': b['hasil'] == harap6 and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v6'].append(r)
        if not r['ok'] or beda_harap: print('  %s %-7s v6 %-13s v7 %-13s harap v6 %-7s %s' % ('✓' if r['ok'] else '✗', r['no'], r['hasilV6'], r['hasilV7'], harap6, ('ubahan %d · %s' % (r['ubahan'], UBAHAN[r['ubahan']])) if r['ubahan'] else 'harus sama dengan v7'), flush=True)
    print('— A · KONTROL: rules v7 dirusak satu suku → kasus sasaran wajib berbalik', flush=True)
    lap['kontrol'] = []; per = {K[0]: K for K in KASUS}; utuh = {x['no']: x for x in A}
    for nama, ganti, sasaran in KONTROL:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrol'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V8 (B1): kasus ★H atas firestore.rules cabang ini (v8) dan atas firestore.rules.v7; kontrol satu suku v8
    v7lama = baca('firestore.rules.v7')
    print('— V8 · %d kasus ★H atas firestore.rules (v8)' % len(P.KASUS_V8), flush=True)
    H8 = jalankan_semua(J, v7, P.KASUS_V8); lap['v8'] = H8
    for x in H8: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V8 · kasus yang sama atas firestore.rules.v7 (yang berbeda wajib persis BEDA_V7 = %s)' % ', '.join(sorted(P.BEDA_V7)), flush=True)
    H7 = jalankan_semua(J, v7lama, P.KASUS_V8); lap['v8lama'] = []
    for a, b in zip(H8, H7):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V7 else a['wajib']
        r8 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV7': b['hasil'], 'hasilV8': a['hasil'], 'harapV7': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v8lama'].append(r8)
        if not r8['ok'] or a['no'] in P.BEDA_V7: print('  %s %-6s v7 %-13s v8 %-13s harap v7 %s' % ('✓' if r8['ok'] else '✗', r8['no'], r8['hasilV7'], r8['hasilV8'], harap), flush=True)
    print('— V8 · KONTROL: satu suku v8 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV8'] = []; per8 = {K[0]: K for K in P.KASUS_V8}; utuh8 = {x['no']: x for x in H8}
    for nama, ganti, sasaran in KONTROL_V8:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per8[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh8.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV8'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V9 (B2): kasus ★J atas firestore.rules cabang ini (v9) dan atas firestore.rules.v8; kontrol satu suku v9
    v8lama = baca('firestore.rules.v8')
    print('— V9 · %d kasus ★J atas firestore.rules (v9)' % len(P.KASUS_V9), flush=True)
    H9 = jalankan_semua(J, v7, P.KASUS_V9); lap['v9'] = H9
    for x in H9: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V9 · kasus yang sama atas firestore.rules.v8 (yang berbeda wajib persis BEDA_V8 = %s)' % ', '.join(sorted(P.BEDA_V8)), flush=True)
    H8l = jalankan_semua(J, v8lama, P.KASUS_V9); lap['v9lama'] = []
    for a, b in zip(H9, H8l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V8 else a['wajib']
        r9 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV8': b['hasil'], 'hasilV9': a['hasil'], 'harapV8': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v9lama'].append(r9)
        if not r9['ok'] or a['no'] in P.BEDA_V8: print('  %s %-6s v8 %-13s v9 %-13s harap v8 %s' % ('✓' if r9['ok'] else '✗', r9['no'], r9['hasilV8'], r9['hasilV9'], harap), flush=True)
    print('— V9 · KONTROL: satu suku v9 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV9'] = []; per9 = {K[0]: K for K in P.KASUS_V9}; utuh9 = {x['no']: x for x in H9}
    for nama, ganti, sasaran in KONTROL_V9:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per9[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh9.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV9'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V10 (B3): kasus ★L atas firestore.rules cabang ini (v10) dan atas firestore.rules.v9; kontrol satu suku v10
    v9lama = baca('firestore.rules.v9')
    print('— V10 · %d kasus ★L atas firestore.rules (v10)' % len(P.KASUS_V10), flush=True)
    H10 = jalankan_semua(J, v7, P.KASUS_V10); lap['v10'] = H10
    for x in H10: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V10 · kasus yang sama atas firestore.rules.v9 (yang berbeda wajib persis BEDA_V9 = %s)' % ', '.join(sorted(P.BEDA_V9)), flush=True)
    H9l = jalankan_semua(J, v9lama, P.KASUS_V10); lap['v10lama'] = []
    for a, b in zip(H10, H9l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V9 else a['wajib']
        r10 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV9': b['hasil'], 'hasilV10': a['hasil'], 'harapV9': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v10lama'].append(r10)
        if not r10['ok'] or a['no'] in P.BEDA_V9: print('  %s %-6s v9 %-13s v10 %-13s harap v9 %s' % ('✓' if r10['ok'] else '✗', r10['no'], r10['hasilV9'], r10['hasilV10'], harap), flush=True)
    print('— V10 · KONTROL: satu suku v10 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV10'] = []; per10 = {K[0]: K for K in P.KASUS_V10}; utuh10 = {x['no']: x for x in H10}
    for nama, ganti, sasaran in KONTROL_V10:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per10[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh10.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV10'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V11 (B4): kasus ★M atas firestore.rules cabang ini (v11) dan atas firestore.rules.v10; kontrol satu suku v11
    v10lama = baca('firestore.rules.v10')
    print('— V11 · %d kasus ★M atas firestore.rules (v11)' % len(P.KASUS_V11), flush=True)
    H11 = jalankan_semua(J, v7, P.KASUS_V11); lap['v11'] = H11
    for x in H11: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V11 · kasus yang sama atas firestore.rules.v10 (yang berbeda wajib persis BEDA_V10 = %s)' % ', '.join(sorted(P.BEDA_V10)), flush=True)
    H10l = jalankan_semua(J, v10lama, P.KASUS_V11); lap['v11lama'] = []
    for a, b in zip(H11, H10l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V10 else a['wajib']
        r11 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV10': b['hasil'], 'hasilV11': a['hasil'], 'harapV10': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v11lama'].append(r11)
        if not r11['ok'] or a['no'] in P.BEDA_V10: print('  %s %-6s v10 %-13s v11 %-13s harap v10 %s' % ('✓' if r11['ok'] else '✗', r11['no'], r11['hasilV10'], r11['hasilV11'], harap), flush=True)
    print('— V11 · KONTROL: satu suku v11 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV11'] = []; per11 = {K[0]: K for K in P.KASUS_V11}; utuh11 = {x['no']: x for x in H11}
    for nama, ganti, sasaran in KONTROL_V11:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per11[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh11.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV11'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V12 (paket S2b): kasus ★S atas firestore.rules cabang ini (v12) dan atas firestore.rules.v11; kontrol satu suku v12
    v11lama = baca('firestore.rules.v11')
    print('— V12 · %d kasus ★S atas firestore.rules (v12)' % len(P.KASUS_V12), flush=True)
    H12 = jalankan_semua(J, v7, P.KASUS_V12); lap['v12'] = H12
    for x in H12: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V12 · kasus yang sama atas firestore.rules.v11 (yang berbeda wajib persis BEDA_V11 = %s)' % ', '.join(sorted(P.BEDA_V11)), flush=True)
    H11l = jalankan_semua(J, v11lama, P.KASUS_V12); lap['v12lama'] = []
    for a, b in zip(H12, H11l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V11 else a['wajib']
        r12 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV11': b['hasil'], 'hasilV12': a['hasil'], 'harapV11': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v12lama'].append(r12)
        if not r12['ok'] or a['no'] in P.BEDA_V11: print('  %s %-6s v11 %-13s v12 %-13s harap v11 %s' % ('✓' if r12['ok'] else '✗', r12['no'], r12['hasilV11'], r12['hasilV12'], harap), flush=True)
    print('— V12 · KONTROL: satu suku v12 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV12'] = []; per12 = {K[0]: K for K in P.KASUS_V12}; utuh12 = {x['no']: x for x in H12}
    for nama, ganti, sasaran in KONTROL_V12:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per12[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh12.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV12'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V13 (owner 21 Nov 2026): kasus ★U atas firestore.rules cabang ini (v13) dan atas firestore.rules.v12; kontrol satu suku v13
    v12lama = baca('firestore.rules.v12')
    print('— V13 · %d kasus ★U atas firestore.rules (v13)' % len(P.KASUS_V13), flush=True)
    H13 = jalankan_semua(J, v7, P.KASUS_V13); lap['v13'] = H13
    for x in H13: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V13 · kasus yang sama atas firestore.rules.v12 (yang berbeda wajib persis BEDA_V12 = %s)' % ', '.join(sorted(P.BEDA_V12)), flush=True)
    H12l = jalankan_semua(J, v12lama, P.KASUS_V13); lap['v13lama'] = []
    for a, b in zip(H13, H12l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V12 else a['wajib']
        r13 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV12': b['hasil'], 'hasilV13': a['hasil'], 'harapV12': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v13lama'].append(r13)
        if not r13['ok'] or a['no'] in P.BEDA_V12: print('  %s %-6s v12 %-13s v13 %-13s harap v12 %s' % ('✓' if r13['ok'] else '✗', r13['no'], r13['hasilV12'], r13['hasilV13'], harap), flush=True)
    print('— V13 · KONTROL: satu suku v13 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV13'] = []; per13 = {K[0]: K for K in P.KASUS_V13}; utuh13 = {x['no']: x for x in H13}
    for nama, ganti, sasaran in KONTROL_V13:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per13[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh13.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV13'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V14 (owner 21 Nov 2026): kasus ★W atas firestore.rules cabang ini (v14) dan atas firestore.rules.v13; kontrol satu suku v14
    v13lama = baca('firestore.rules.v13')
    print('— V14 · %d kasus ★W atas firestore.rules (v14)' % len(P.KASUS_V14), flush=True)
    H14 = jalankan_semua(J, v7, P.KASUS_V14); lap['v14'] = H14
    for x in H14: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V14 · kasus yang sama atas firestore.rules.v13 (yang berbeda wajib persis BEDA_V13 = %s)' % ', '.join(sorted(P.BEDA_V13)), flush=True)
    H13l = jalankan_semua(J, v13lama, P.KASUS_V14); lap['v14lama'] = []
    for a, b in zip(H14, H13l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V13 else a['wajib']
        r14 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV13': b['hasil'], 'hasilV14': a['hasil'], 'harapV13': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v14lama'].append(r14)
        if not r14['ok'] or a['no'] in P.BEDA_V13: print('  %s %-6s v13 %-13s v14 %-13s harap v13 %s' % ('✓' if r14['ok'] else '✗', r14['no'], r14['hasilV13'], r14['hasilV14'], harap), flush=True)
    print('— V14 · KONTROL: satu suku v14 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV14'] = []; per14 = {K[0]: K for K in P.KASUS_V14}; utuh14 = {x['no']: x for x in H14}
    for nama, ganti, sasaran in KONTROL_V14:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per14[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh14.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV14'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V15 (owner 22 Nov 2026): kasus ★X atas firestore.rules cabang ini (v15) dan atas firestore.rules.v14; kontrol satu suku v15
    v14lama = baca('firestore.rules.v14')
    print('— V15 · %d kasus ★X atas firestore.rules (v15)' % len(P.KASUS_V15), flush=True)
    H15 = jalankan_semua(J, v7, P.KASUS_V15); lap['v15'] = H15
    for x in H15: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V15 · kasus yang sama atas firestore.rules.v14 (yang berbeda wajib persis BEDA_V14 = %s)' % ', '.join(sorted(P.BEDA_V14)), flush=True)
    H14l = jalankan_semua(J, v14lama, P.KASUS_V15); lap['v15lama'] = []
    for a, b in zip(H15, H14l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V14 else a['wajib']
        r15 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV14': b['hasil'], 'hasilV15': a['hasil'], 'harapV14': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v15lama'].append(r15)
        if not r15['ok'] or a['no'] in P.BEDA_V14: print('  %s %-6s v14 %-13s v15 %-13s harap v14 %s' % ('✓' if r15['ok'] else '✗', r15['no'], r15['hasilV14'], r15['hasilV15'], harap), flush=True)
    print('— V15 · KONTROL: satu suku v15 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV15'] = []; per15 = {K[0]: K for K in P.KASUS_V15}; utuh15 = {x['no']: x for x in H15}
    for nama, ganti, sasaran in KONTROL_V15:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per15[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh15.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV15'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V16 (owner 22 Nov 2026): kasus ★Y atas firestore.rules cabang ini (v16) dan atas firestore.rules.v15; kontrol satu suku v16
    v15lama_t = baca('firestore.rules.v15')
    print('— V16 · %d kasus ★Y atas firestore.rules (v16)' % len(P.KASUS_V16), flush=True)
    H16 = jalankan_semua(J, v7, P.KASUS_V16); lap['v16'] = H16
    for x in H16: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V16 · kasus yang sama atas firestore.rules.v15 (yang berbeda wajib persis BEDA_V15 = %s)' % ', '.join(sorted(P.BEDA_V15)), flush=True)
    H16l = jalankan_semua(J, v15lama_t, P.KASUS_V16); lap['v16lama'] = []
    for a, b in zip(H16, H16l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V15 else a['wajib']
        r16 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV15': b['hasil'], 'hasilV16': a['hasil'], 'harapV15': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v16lama'].append(r16)
        if not r16['ok'] or a['no'] in P.BEDA_V15: print('  %s %-6s v15 %-13s v16 %-13s harap v15 %s' % ('✓' if r16['ok'] else '✗', r16['no'], r16['hasilV15'], r16['hasilV16'], harap), flush=True)
    print('— V16 · KONTROL: satu suku v16 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV16'] = []; per16 = {K[0]: K for K in P.KASUS_V16}; utuh16 = {x['no']: x for x in H16}
    for nama, ganti, sasaran in KONTROL_V16:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per16[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh16.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV16'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V17 (owner 23 Nov 2026): kasus ★Z atas firestore.rules cabang ini (v17) dan atas firestore.rules.v16; kontrol satu suku v17
    v16lama_t = baca('firestore.rules.v16')
    print('— V17 · %d kasus ★Z atas firestore.rules (v17)' % len(P.KASUS_V17), flush=True)
    H17 = jalankan_semua(J, v7, P.KASUS_V17); lap['v17'] = H17
    for x in H17: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V17 · kasus yang sama atas firestore.rules.v16 (yang berbeda wajib persis BEDA_V16 = %s)' % ', '.join(sorted(P.BEDA_V16)), flush=True)
    H17l = jalankan_semua(J, v16lama_t, P.KASUS_V17); lap['v17lama'] = []
    for a, b in zip(H17, H17l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V16 else a['wajib']
        r17 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV16': b['hasil'], 'hasilV17': a['hasil'], 'harapV16': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v17lama'].append(r17)
        if not r17['ok'] or a['no'] in P.BEDA_V16: print('  %s %-6s v16 %-13s v17 %-13s harap v16 %s' % ('✓' if r17['ok'] else '✗', r17['no'], r17['hasilV16'], r17['hasilV17'], harap), flush=True)
    print('— V17 · KONTROL: satu suku v17 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV17'] = []; per17 = {K[0]: K for K in P.KASUS_V17}; utuh17 = {x['no']: x for x in H17}
    for nama, ganti, sasaran in KONTROL_V17:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per17[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh17.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV17'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- V18 (owner 24 Nov 2026, tinjauan 30 Sep (d)): kasus ★V atas firestore.rules cabang ini (v18) dan atas firestore.rules.v17; kontrol satu suku v18
    v17lama_t = baca('firestore.rules.v17')
    print('— V18 · %d kasus ★V atas firestore.rules (v18)' % len(P.KASUS_V18), flush=True)
    H18 = jalankan_semua(J, v7, P.KASUS_V18); lap['v18'] = H18
    for x in H18: print('  %s %-6s %-26s %-48s → %-13s wajib %-7s %s' % ('✓' if x['ok'] else '✗', x['no'], x['akun'] + ' ' + x['op'], x['jalur'][:48], x['hasil'], x['wajib'], x['ket'][:90]), flush=True)
    print('— V18 · kasus yang sama atas firestore.rules.v17 (yang berbeda wajib persis BEDA_V17 = %s)' % ', '.join(sorted(P.BEDA_V17)), flush=True)
    H18l = jalankan_semua(J, v17lama_t, P.KASUS_V18); lap['v18lama'] = []
    for a, b in zip(H18, H18l):
        harap = ('DITOLAK' if a['wajib'] == 'LOLOS' else 'LOLOS') if a['no'] in P.BEDA_V17 else a['wajib']
        r18 = {'no': b['no'], 'jalur': b['jalur'], 'hasilV17': b['hasil'], 'hasilV18': a['hasil'], 'harapV17': harap, 'ok': b['hasil'] == harap and b['hasil'] != 'TIDAK TERUKUR'}
        lap['v18lama'].append(r18)
        if not r18['ok'] or a['no'] in P.BEDA_V17: print('  %s %-6s v17 %-13s v18 %-13s harap v17 %s' % ('✓' if r18['ok'] else '✗', r18['no'], r18['hasilV17'], r18['hasilV18'], harap), flush=True)
    print('— V18 · KONTROL: satu suku v18 dirusak → kasus sasaran wajib berbalik', flush=True)
    lap['kontrolV18'] = []; per18 = {K[0]: K for K in P.KASUS_V18}; utuh18 = {x['no']: x for x in H18}
    for nama, ganti, sasaran in KONTROL_V18:
        try:
            R = rusak(v7, ganti); hs = jalankan_semua(J, R, [per18[s] for s in sasaran])
            balik = [h for h in hs if h['hasil'] in ('LOLOS', 'DITOLAK') and h['hasil'] != h['wajib'] and utuh18.get(h['no'], {}).get('ok')]
            k = {'nama': nama, 'sasaran': sasaran, 'hasil': [(h['no'], h['hasil'], h['wajib']) for h in hs], 'berbunyi': len(balik) == len(sasaran)}
        except Exception as e: k = {'nama': nama, 'sasaran': sasaran, 'hasil': [], 'berbunyi': False, 'galat': str(e)[:300]}
        lap['kontrolV18'].append(k)
        print('  %s %s → %s' % ('BERBUNYI' if k['berbunyi'] else 'DIAM!!  ', nama, k.get('galat') or ', '.join('%s %s (wajib %s)' % x for x in k['hasil'])), flush=True)
    pasang_aturan(v7)
    # ---- C · kasir darurat
    v33 = skrip_halaman(baca('kasir-darurat-nominal.html')); h32 = html_v32(); v32 = skrip_halaman(h32) if h32 else None
    lap['kasir'] = {}
    for label, teks in (('v7', v7), ('v6', v6)):
        pasang_aturan(teks); print('— C · kasir darurat, rules %s' % label, flush=True)
        try: L, c = jalur_kasir(v33, v32, label)
        except Exception as e: L, c = {}, [('c?', 'jalur kasir jatuh', False, str(e)[:400])]
        lap['kasir'][label] = {'cek': [{'id': a, 'nama': b, 'ok': bool(o), 'ket': k} for a, b, o, k in c], 'galatNode': {k: v.get('galat') for k, v in L.items() if v.get('galat')}}
        for a, b, o, k in c: print('  %s %s %s%s' % ('✓' if o else '✗', a, b, '' if o else ' → ' + json.dumps(k, ensure_ascii=False)[:400]), flush=True)
    nama, ganti, sasaran = KONTROL_KASIR
    pasang_aturan(rusak(v7, ganti)); print('— C · KONTROL: ' + nama, flush=True)
    try: L, c = jalur_kasir(v33, v32, 'kontrol')
    except Exception as e: L, c = {}, [('c?', 'jalur kasir jatuh', False, str(e)[:300])]
    gagal = {a for a, b, o, k in c if not o}
    lap['kontrolKasir'] = {'nama': nama, 'sasaran': sasaran, 'gagal': sorted(gagal), 'berbunyi': set(sasaran) <= gagal and all(o for a, b, o, k in c if a not in sasaran)}
    print('  %s %s → gagal: %s' % ('BERBUNYI' if lap['kontrolKasir']['berbunyi'] else 'DIAM!!  ', nama, ', '.join(sorted(gagal)) or '-'), flush=True)
    pasang_aturan(v7)
    lap['ringkas'] = {'v7': ringkas(A), 'wajibOwner': ringkas([x for x in A if x['no'] in P.WAJIB_V7]), 'opsional': ringkas([x for x in A if x['no'].startswith('★') and x['no'] not in P.WAJIB_V7]),
                      'model': ringkas([x for x in A if x['no'].startswith('M-')]), 'server': ringkas([x for x in A if x['no'].startswith('S-')]), 'buku': ringkas([x for x in A if x['no'] in BUKU]),
                      'v6': {'kasus': len(lap['v6']), 'sesuai': sum(1 for x in lap['v6'] if x['ok']), 'beda': sum(1 for x in lap['v6'] if x['hasilV6'] != x['hasilV7'])},
                      'kontrol': {'jumlah': len(lap['kontrol']) + 1, 'berbunyi': sum(1 for x in lap['kontrol'] if x['berbunyi']) + (1 if lap['kontrolKasir']['berbunyi'] else 0)},
                      'kasir': {k: {'cek': len(v['cek']), 'lulus': sum(1 for x in v['cek'] if x['ok'])} for k, v in lap['kasir'].items()},
                      'v8': ringkas(lap['v8']), 'v8lama': {'kasus': len(lap['v8lama']), 'sesuai': sum(1 for x in lap['v8lama'] if x['ok'])},
                      'kontrolV8': {'jumlah': len(lap['kontrolV8']), 'berbunyi': sum(1 for x in lap['kontrolV8'] if x['berbunyi'])},
                      'v9': ringkas(lap['v9']), 'v9lama': {'kasus': len(lap['v9lama']), 'sesuai': sum(1 for x in lap['v9lama'] if x['ok'])},
                      'kontrolV9': {'jumlah': len(lap['kontrolV9']), 'berbunyi': sum(1 for x in lap['kontrolV9'] if x['berbunyi'])},
                      'v10': ringkas(lap['v10']), 'v10lama': {'kasus': len(lap['v10lama']), 'sesuai': sum(1 for x in lap['v10lama'] if x['ok'])},
                      'kontrolV10': {'jumlah': len(lap['kontrolV10']), 'berbunyi': sum(1 for x in lap['kontrolV10'] if x['berbunyi'])},
                      'v11': ringkas(lap['v11']), 'v11lama': {'kasus': len(lap['v11lama']), 'sesuai': sum(1 for x in lap['v11lama'] if x['ok'])},
                      'kontrolV11': {'jumlah': len(lap['kontrolV11']), 'berbunyi': sum(1 for x in lap['kontrolV11'] if x['berbunyi'])},
                      'v12': ringkas(lap['v12']), 'v12lama': {'kasus': len(lap['v12lama']), 'sesuai': sum(1 for x in lap['v12lama'] if x['ok'])},
                      'kontrolV12': {'jumlah': len(lap['kontrolV12']), 'berbunyi': sum(1 for x in lap['kontrolV12'] if x['berbunyi'])},
                      'v13': ringkas(lap['v13']), 'v13lama': {'kasus': len(lap['v13lama']), 'sesuai': sum(1 for x in lap['v13lama'] if x['ok'])},
                      'kontrolV13': {'jumlah': len(lap['kontrolV13']), 'berbunyi': sum(1 for x in lap['kontrolV13'] if x['berbunyi'])},
                      'v14': ringkas(lap['v14']), 'v14lama': {'kasus': len(lap['v14lama']), 'sesuai': sum(1 for x in lap['v14lama'] if x['ok'])},
                      'kontrolV14': {'jumlah': len(lap['kontrolV14']), 'berbunyi': sum(1 for x in lap['kontrolV14'] if x['berbunyi'])},
                      'v15': ringkas(lap['v15']), 'v15lama': {'kasus': len(lap['v15lama']), 'sesuai': sum(1 for x in lap['v15lama'] if x['ok'])},
                      'kontrolV15': {'jumlah': len(lap['kontrolV15']), 'berbunyi': sum(1 for x in lap['kontrolV15'] if x['berbunyi'])},
                      'v16': ringkas(lap['v16']), 'v16lama': {'kasus': len(lap['v16lama']), 'sesuai': sum(1 for x in lap['v16lama'] if x['ok'])},
                      'kontrolV16': {'jumlah': len(lap['kontrolV16']), 'berbunyi': sum(1 for x in lap['kontrolV16'] if x['berbunyi'])},
                      'v17': ringkas(lap['v17']), 'v17lama': {'kasus': len(lap['v17lama']), 'sesuai': sum(1 for x in lap['v17lama'] if x['ok'])},
                      'kontrolV17': {'jumlah': len(lap['kontrolV17']), 'berbunyi': sum(1 for x in lap['kontrolV17'] if x['berbunyi'])},
                      'v18': ringkas(lap['v18']), 'v18lama': {'kasus': len(lap['v18lama']), 'sesuai': sum(1 for x in lap['v18lama'] if x['ok'])},
                      'kontrolV18': {'jumlah': len(lap['kontrolV18']), 'berbunyi': sum(1 for x in lap['kontrolV18'] if x['berbunyi'])}}
    lap['lulus'] = (all(x['ok'] for x in A) and all(x['ok'] for x in lap['v6']) and all(x['berbunyi'] for x in lap['kontrol']) and lap['kontrolKasir']['berbunyi']
                    and all(x['ok'] for v in lap['kasir'].values() for x in v['cek'])
                    and all(x['ok'] for x in lap['v8']) and all(x['ok'] for x in lap['v8lama']) and all(x['berbunyi'] for x in lap['kontrolV8'])
                    and all(x['ok'] for x in lap['v9']) and all(x['ok'] for x in lap['v9lama']) and all(x['berbunyi'] for x in lap['kontrolV9'])
                    and all(x['ok'] for x in lap['v10']) and all(x['ok'] for x in lap['v10lama']) and all(x['berbunyi'] for x in lap['kontrolV10'])
                    and all(x['ok'] for x in lap['v11']) and all(x['ok'] for x in lap['v11lama']) and all(x['berbunyi'] for x in lap['kontrolV11'])
                    and all(x['ok'] for x in lap['v12']) and all(x['ok'] for x in lap['v12lama']) and all(x['berbunyi'] for x in lap['kontrolV12'])
                    and all(x['ok'] for x in lap['v13']) and all(x['ok'] for x in lap['v13lama']) and all(x['berbunyi'] for x in lap['kontrolV13'])
                    and all(x['ok'] for x in lap['v14']) and all(x['ok'] for x in lap['v14lama']) and all(x['berbunyi'] for x in lap['kontrolV14'])
                    and all(x['ok'] for x in lap['v15']) and all(x['ok'] for x in lap['v15lama']) and all(x['berbunyi'] for x in lap['kontrolV15'])
                    and all(x['ok'] for x in lap['v16']) and all(x['ok'] for x in lap['v16lama']) and all(x['berbunyi'] for x in lap['kontrolV16'])
                    and all(x['ok'] for x in lap['v17']) and all(x['ok'] for x in lap['v17lama']) and all(x['berbunyi'] for x in lap['kontrolV17'])
                    and all(x['ok'] for x in lap['v18']) and all(x['ok'] for x in lap['v18lama']) and all(x['berbunyi'] for x in lap['kontrolV18']))
    return lap


def ringkasan_md(lap):
    R = lap['ringkas']; f = lambda r: '%d/%d lulus%s' % (r['lulus'], r['kasus'], (' · %d TIDAK TERUKUR' % r['tidakTerukur']) if r['tidakTerukur'] else '')
    out = ['## Bukti server rules v7 — Firebase Emulator Firestore (mesin rules = server produksi)', '',
           'Proyek emulator `%s` · firebase-tools %s · jam runner %s (hari ini WIB %s; tahun dokumen uji digeser %+d) · token akun palsu (JWT tanpa tanda tangan, hanya emulator)'
           % (lap['proyek'], lap['firebaseTools'], lap['mulai'][:19], lap['hariIni'], lap.get('selisihTahun', 0)), '',
           '- **A · v7**: %s — Wajib owner %s · opsional ★ %s · model M %s · server S %s · H "hanya maju" (v6) %s' % (f(R['v7']), f(R['wajibOwner']), f(R['opsional']), f(R['model']), f(R['server']), f(R['buku'])),
           '- **A · v6**: %d/%d sesuai harapan — %d kasus berbeda v6 → v7, semuanya di BEDA_V6 (lima ubahan); selebihnya sama' % (R['v6']['sesuai'], R['v6']['kasus'], R['v6']['beda']),
           '- **Kontrol**: %d/%d berbunyi (rules dirusak satu suku → kasus sasarannya berbalik)' % (R['kontrol']['berbunyi'], R['kontrol']['jumlah']),
           '- **C · kasir darurat (kode asli)**: ' + ' · '.join('%s %d/%d' % (k, v['lulus'], v['cek']) for k, v in R['kasir'].items()),
           '- **V8 (B1 harga pelanggan usaha)**: %s atas v8 · atas v7 %d/%d sesuai (berbeda tepat %s) · kontrol v8 %d/%d berbunyi'
           % (f(R['v8']), R['v8lama']['sesuai'], R['v8lama']['kasus'], ', '.join(sorted(P.BEDA_V7)), R['kontrolV8']['berbunyi'], R['kontrolV8']['jumlah']),
           '- **V9 (B2 faktur & minta persetujuan bon)**: %s atas v9 · atas v8 %d/%d sesuai (berbeda tepat %s) · kontrol v9 %d/%d berbunyi'
           % (f(R['v9']), R['v9lama']['sesuai'], R['v9lama']['kasus'], ', '.join(sorted(P.BEDA_V8)), R['kontrolV9']['berbunyi'], R['kontrolV9']['jumlah']),
           '- **V10 (B3 surat jalan & bukti terima)**: %s atas v10 · atas v9 %d/%d sesuai (berbeda tepat %s) · kontrol v10 %d/%d berbunyi'
           % (f(R['v10']), R['v10lama']['sesuai'], R['v10lama']['kasus'], ', '.join(sorted(P.BEDA_V9)), R['kontrolV10']['berbunyi'], R['kontrolV10']['jumlah']),
           '- **V11 (B4 pesanan, PO & order rutin)**: %s atas v11 · atas v10 %d/%d sesuai (berbeda tepat %s) · kontrol v11 %d/%d berbunyi'
           % (f(R['v11']), R['v11lama']['sesuai'], R['v11lama']['kasus'], ', '.join(sorted(P.BEDA_V10)), R['kontrolV11']['berbunyi'], R['kontrolV11']['jumlah']),
           '- **V12 (paket S2b tanda kenal)**: %s atas v12 · atas v11 %d/%d sesuai (berbeda tepat %s) · kontrol v12 %d/%d berbunyi'
           % (f(R['v12']), R['v12lama']['sesuai'], R['v12lama']['kasus'], ', '.join(sorted(P.BEDA_V11)), R['kontrolV12']['berbunyi'], R['kontrolV12']['jumlah']),
           '- **V13 (titipan uang keluar & pesan dari tablet + token notifikasi HP owner)**: %s atas v13 · atas v12 %d/%d sesuai (berbeda tepat %s) · kontrol v13 %d/%d berbunyi'
           % (f(R['v13']), R['v13lama']['sesuai'], R['v13lama']['kasus'], ', '.join(sorted(P.BEDA_V12)), R['kontrolV13']['berbunyi'], R['kontrolV13']['jumlah']),
           '- **V14 (data uang untuk Ringkas hari ini di tablet)**: %s atas v14 · atas v13 %d/%d sesuai (berbeda tepat %s) · kontrol v14 %d/%d berbunyi'
           % (f(R['v14']), R['v14lama']['sesuai'], R['v14lama']['kasus'], ', '.join(sorted(P.BEDA_V13)), R['kontrolV14']['berbunyi'], R['kontrolV14']['jumlah']),
           '- **V15 (barang masuk & bayar supir di tablet)**: %s atas v15 · atas v14 %d/%d sesuai (berbeda tepat %s) · kontrol v15 %d/%d berbunyi'
           % (f(R['v15']), R['v15lama']['sesuai'], R['v15lama']['kasus'], ', '.join(sorted(P.BEDA_V14)), R['kontrolV15']['berbunyi'], R['kontrolV15']['jumlah']),
           '- **V16 (tutup hari dari tablet)**: %s atas v16 · atas v15 %d/%d sesuai (berbeda tepat %s) · kontrol v16 %d/%d berbunyi'
           % (f(R['v16']), R['v16lama']['sesuai'], R['v16lama']['kasus'], ', '.join(sorted(P.BEDA_V15)), R['kontrolV16']['berbunyi'], R['kontrolV16']['jumlah']),
           '- **V17 (push aplikasi tablet)**: %s atas v17 · atas v16 %d/%d sesuai (berbeda tepat %s) · kontrol v17 %d/%d berbunyi'
           % (f(R['v17']), R['v17lama']['sesuai'], R['v17lama']['kasus'], ', '.join(sorted(P.BEDA_V16)), R['kontrolV17']['berbunyi'], R['kontrolV17']['jumlah']),
           '- **V18 (denyut staf terikat penulisnya)**: %s atas v18 · atas v17 %d/%d sesuai (berbeda tepat %s) · kontrol v18 %d/%d berbunyi'
           % (f(R['v18']), R['v18lama']['sesuai'], R['v18lama']['kasus'], ', '.join(sorted(P.BEDA_V17)), R['kontrolV18']['berbunyi'], R['kontrolV18']['jumlah']), '']
    out += ['### A · kasus (v7)', '', '| no | akun · operasi · jalur | wajib | emulator v7 | v6 |', '|---|---|---|---|---|']
    v6 = {x['no']: x for x in lap['v6']}
    for x in lap['v7']:
        y = v6.get(x['no'], {})
        out.append('| %s %s | %s · %s · `%s` | %s | %s | %s%s |' % ('✓' if x['ok'] else '✗', x['no'], x['akun'], x['op'], x['jalur'].replace('|', '\\|'), x['wajib'], x['hasil'],
                                                           y.get('hasilV6', '?'), (' (ubahan %d)' % y['ubahan']) if y.get('ubahan') else ''))
    out += ['', '### Kontrol', ''] + ['- %s %s → %s' % ('✓ BERBUNYI' if k['berbunyi'] else '✗ DIAM', k['nama'], k.get('galat') or ', '.join('%s %s (wajib %s)' % h for h in k['hasil'])) for k in lap['kontrol']]
    kk = lap['kontrolKasir']; out.append('- %s %s → gagal %s' % ('✓ BERBUNYI' if kk['berbunyi'] else '✗ DIAM', kk['nama'], ', '.join(kk['gagal']) or '-'))
    for label, v in lap['kasir'].items():
        out += ['', '### C · kasir darurat — rules %s' % label, ''] + ['- %s %s · %s%s' % ('✓' if x['ok'] else '✗', x['id'], x['nama'], '' if x['ok'] else ' — `' + json.dumps(x['ket'], ensure_ascii=False)[:400].replace('`', "'") + '`') for x in v['cek']]
        if v.get('galatNode'): out.append('- galat node: `%s`' % json.dumps(v['galatNode'], ensure_ascii=False)[:600].replace('`', "'"))
    return '\n'.join(out) + '\n'


# ============================== --periksa (statis + model + jsc/node dengan server palsu) ==============================
DRIVER_JS = r"""
var HASIL = null;
var PALSU = { tolak: __TOLAK__, minta: [] };
var H = { tidur: function () { return Promise.resolve(); },
  fetch: function (url, opsi) {
    PALSU.minta.push(url);
    var tulisNota = url.indexOf(':commit') >= 0 || (String(opsi.method || '').toUpperCase() === 'PATCH' && url.indexOf('/documents/penjualan/') >= 0);
    var status = tulisNota && PALSU.tolak ? 403 : (String(opsi.method || 'GET').toUpperCase() === 'GET' ? 404 : 200);
    var isi = status === 403 ? { error: { code: 403, status: 'PERMISSION_DENIED', message: 'Missing or insufficient permissions.' } } : {};
    return Promise.resolve({ status: status, ok: status >= 200 && status < 300, json: function () { return Promise.resolve(isi); }, text: function () { return Promise.resolve(JSON.stringify(isi)); } });
  } };
KASIR_UJI.jalankan(H, __SKRIP__, __SIMPANAN__, { nota: 15000 }).then(function (h) { HASIL = h; }, function (e) { HASIL = { galat: String(e) }; });
if (typeof drainMicrotasks === 'function') { for (var i = 0; i < 50 && !HASIL; i++) drainMicrotasks(); print(JSON.stringify(HASIL)); }
else { (function tunggu(n) { if (HASIL || n > 400) { print(JSON.stringify(HASIL)); return; } setImmediate(function () { tunggu(n + 1); }); })(0); }
"""


def jalan_kasir_palsu(skrip, tolak):
    """kasir_emulator.js + skrip halaman di jsc (Mac) atau node (runner) dengan server PALSU (tanpa jaringan). → hasil jalankan()."""
    js = baca('alat-uji/kasir_emulator.js') + '\n' + DRIVER_JS.replace('__TOLAK__', 'true' if tolak else 'false').replace('__SKRIP__', json.dumps(skrip)).replace(
        '__SIMPANAN__', json.dumps({'kasir_auth_v1': json.dumps({'refreshToken': 'r', 'idToken': 't-palsu', 'kedaluwarsa': 4102444800000})}))
    d = tempfile.mkdtemp(prefix='kasir-palsu-'); p = os.path.join(d, 'jalan.js')
    try:
        open(p, 'w', encoding='utf-8').write(js); env = dict(os.environ, TZ='Asia/Jakarta')
        if os.path.exists(JSC): cmd = [JSC, p]
        elif shutil.which('node'):
            cmd = ['node', '-e', "global.print = function () { console.log(Array.prototype.join.call(arguments, ' ')); };"
                   "require('vm').runInThisContext(require('fs').readFileSync(process.argv[1], 'utf8'), { filename: 'jalan.js' });", p]
        else: return None
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        b = [x for x in r.stdout.strip().split('\n') if x.startswith('{')]
        return json.loads(b[-1]) if b else {'galat': (r.stderr or r.stdout)[-800:]}
    finally: shutil.rmtree(d, ignore_errors=True)


# jam lain tempat model menilai dokumen uji yang DIGESER (seperti emulator): Okt 2026, 1 Jan 2027 00.30 WIB, 2 Jan 2027, Juni 2027, Januari 2028 (tutup buku 2027)
JAM_GESER = ('2026-10-07T05:00:00Z', '2026-12-31T17:30:00Z', '2027-01-02T01:00:00Z', '2027-06-15T03:00:00Z', '2028-01-05T08:30:00Z')
JAM_PEMBANDING = '2027-06-15T03:00:00Z'


def periksa(rules=None, dok=None, html=None):
    """→ [(nama, ok, ket)] — ok True / False / None (DILEWATI: tidak bisa diukur di mesin ini, bukan lulus). Tanpa emulator: tabel docs = model, model
    v7/v6, model di jam lain (tahun digeser), kontrol model, kode kasir di server palsu."""
    c = []; R = rules if rules is not None else baca('firestore.rules'); R6 = baca('firestore.rules.v6'); W = wajib_dok(dok)
    bintang = [K[0] for K in KASUS if K[0].startswith('★')]
    salah_dok = sorted(k for k in bintang if W.get(k) is None or W.get(k) != dict((K[0], K[8]) for K in KASUS)[k])
    c.append(('kolom "Wajib" %s = kolom model untuk %d kasus ★ (tabel dibaca sel demi sel)' % (DOK, len(bintang)), not salah_dok and set(W) == set(bintang),
              {'beda': salah_dok, 'hanya di berkas': sorted(set(W) - set(bintang))}))
    c.append(('id kasus unik (★ docs + M model + S server + H hanya maju)', len({K[0] for K in KASUS}) == len(KASUS), len(KASUS)))
    try: M7, M6 = RM.Rules(R), RM.Rules(R6)
    except Exception as e: return c + [('rules terurai penafsir mini', False, str(e)[:300])]
    salah7, beda6 = [], set()
    for K in KASUS:
        h7 = nilai_model(M7, K); h6 = nilai_model(M6, K)
        if h7.boleh != K[8]: salah7.append(K[0])
        if h6.boleh != h7.boleh: beda6.add(K[0])
    c.append(('model v7 = kolom Wajib di %d kasus (termasuk S-* cap jam server & %d kasus H "hanya maju" v6)' % (len(KASUS), len(KASUS_BUKU)), not salah7, salah7))
    c.append(('model: kasus yang berbeda v6 → v7 = BEDA_V6 persis (%d kasus, lima ubahan)' % len(BEDA_V6), beda6 == set(BEDA_V6), {'model saja': sorted(beda6 - set(BEDA_V6)), 'BEDA_V6 saja': sorted(set(BEDA_V6) - beda6)}))
    # emulator menggeser TAHUN dokumen uji ke jam runner (sanggahan 7 Okt: dulu semua kasus TIDAK TERUKUR mulai 1 Jan 2027, tepat saat tutup buku 2026 berjalan
    # dengan rules v7). Model atas dokumen uji yang digeser PERSIS seperti emulator (isi_kasus) di jam-jam lain = kolom Wajib. Pembanding: tanpa geser tahun,
    # di Juni 2027 model WAJIB menyimpang dari kolom Wajib (jam memang menentukan — cek ini tidak lulus kosong).
    salah_g = {}
    for x in JAM_GESER:
        J = Jam(TS.dari_iso(x).ms); s = [K[0] for K in KASUS if K[0] not in BUKU and nilai_model(M7, K, J).boleh != K[8]]
        if s: salah_g['%s (tahun %+d)' % (x, J.selisih)] = s
    Jp = Jam(TS.dari_iso(JAM_PEMBANDING).ms); Jp.selisih = 0
    simpang = sorted(K[0] for K in KASUS if K[0] not in BUKU and nilai_model(M7, K, Jp).boleh != K[8])
    c.append(('model: dokumen uji digeser ke jam lain (%s) = kolom Wajib; tanpa geser tahun %s menyimpang %d kasus' % (', '.join(x[:10] for x in JAM_GESER), JAM_PEMBANDING[:10], len(simpang)),
              not salah_g and bool(simpang), {'salah': salah_g, 'pembanding tanpa geser (wajib menyimpang)': simpang}))
    per = {K[0]: K for K in KASUS}
    for nama, ganti, sasaran in KONTROL + [(KONTROL_KASIR[0], KONTROL_KASIR[1], ['S-A2', 'S-A3', 'M-A5'])]:
        try:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per[s]).boleh == per[s][8]]
            c.append(('kontrol "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
        except Exception as e: c.append(('kontrol "%s"' % nama, False, str(e)[:200]))
    # V8 (B1): model atas v8 = kolom wajib KASUS_V8; atas firestore.rules.v7 berbeda tepat BEDA_V7; kontrol V8 membalik sasarannya
    try:
        M8, M7lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v7'))
        salah8 = [K[0] for K in P.KASUS_V8 if nilai_model(M8, K).boleh != K[8]]; beda7 = {K[0] for K in P.KASUS_V8 if nilai_model(M7lama, K).boleh != nilai_model(M8, K).boleh}
        c.append(('model v8 = kolom Wajib di %d kasus ★H; berbeda dari firestore.rules.v7 tepat %s' % (len(P.KASUS_V8), ', '.join(sorted(P.BEDA_V7))), not salah8 and beda7 == set(P.BEDA_V7), {'salah v8': salah8, 'beda v7': sorted(beda7)}))
        per8 = {K[0]: K for K in P.KASUS_V8}
        for nama, ganti, sasaran in KONTROL_V8:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per8[s]).boleh == per8[s][8]]
            c.append(('kontrol v8 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v8 (KASUS_V8)', False, str(e)[:300]))
    # V9 (B2): model atas v9 = kolom wajib KASUS_V9; atas firestore.rules.v8 berbeda tepat BEDA_V8; kontrol V9 membalik sasarannya
    try:
        M9, M8lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v8'))
        salah9 = [K[0] for K in P.KASUS_V9 if nilai_model(M9, K).boleh != K[8]]; beda8 = {K[0] for K in P.KASUS_V9 if nilai_model(M8lama, K).boleh != nilai_model(M9, K).boleh}
        c.append(('model v9 = kolom Wajib di %d kasus ★J; berbeda dari firestore.rules.v8 tepat %s' % (len(P.KASUS_V9), ', '.join(sorted(P.BEDA_V8))), not salah9 and beda8 == set(P.BEDA_V8), {'salah v9': salah9, 'beda v8': sorted(beda8)}))
        per9 = {K[0]: K for K in P.KASUS_V9}
        for nama, ganti, sasaran in KONTROL_V9:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per9[s]).boleh == per9[s][8]]
            c.append(('kontrol v9 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v9 (KASUS_V9)', False, str(e)[:300]))
    # V10 (B3): model atas v10 = kolom wajib KASUS_V10; atas firestore.rules.v9 berbeda tepat BEDA_V9; kontrol V10 membalik sasarannya
    try:
        M10, M9lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v9'))
        salah10 = [K[0] for K in P.KASUS_V10 if nilai_model(M10, K).boleh != K[8]]; beda9 = {K[0] for K in P.KASUS_V10 if nilai_model(M9lama, K).boleh != nilai_model(M10, K).boleh}
        c.append(('model v10 = kolom Wajib di %d kasus ★L; berbeda dari firestore.rules.v9 tepat %s' % (len(P.KASUS_V10), ', '.join(sorted(P.BEDA_V9))), not salah10 and beda9 == set(P.BEDA_V9), {'salah v10': salah10, 'beda v9': sorted(beda9)}))
        per10 = {K[0]: K for K in P.KASUS_V10}
        for nama, ganti, sasaran in KONTROL_V10:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per10[s]).boleh == per10[s][8]]
            c.append(('kontrol v10 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v10 (KASUS_V10)', False, str(e)[:300]))
    # V11 (B4): model atas v11 = kolom wajib KASUS_V11; atas firestore.rules.v10 berbeda tepat BEDA_V10; kontrol V11 membalik sasarannya
    try:
        M11, M10lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v10'))
        salah11 = [K[0] for K in P.KASUS_V11 if nilai_model(M11, K).boleh != K[8]]; beda10 = {K[0] for K in P.KASUS_V11 if nilai_model(M10lama, K).boleh != nilai_model(M11, K).boleh}
        c.append(('model v11 = kolom Wajib di %d kasus ★M; berbeda dari firestore.rules.v10 tepat %s' % (len(P.KASUS_V11), ', '.join(sorted(P.BEDA_V10))), not salah11 and beda10 == set(P.BEDA_V10), {'salah v11': salah11, 'beda v10': sorted(beda10)}))
        per11 = {K[0]: K for K in P.KASUS_V11}
        for nama, ganti, sasaran in KONTROL_V11:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per11[s]).boleh == per11[s][8]]
            c.append(('kontrol v11 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v11 (KASUS_V11)', False, str(e)[:300]))
    # V12 (paket S2b): model atas v12 = kolom wajib KASUS_V12; atas firestore.rules.v11 berbeda tepat BEDA_V11; kontrol V12 membalik sasarannya
    try:
        M12, M11lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v11'))
        salah12 = [K[0] for K in P.KASUS_V12 if nilai_model(M12, K).boleh != K[8]]; beda11 = {K[0] for K in P.KASUS_V12 if nilai_model(M11lama, K).boleh != nilai_model(M12, K).boleh}
        c.append(('model v12 = kolom Wajib di %d kasus ★S; berbeda dari firestore.rules.v11 tepat %s' % (len(P.KASUS_V12), ', '.join(sorted(P.BEDA_V11))), not salah12 and beda11 == set(P.BEDA_V11), {'salah v12': salah12, 'beda v11': sorted(beda11)}))
        per12 = {K[0]: K for K in P.KASUS_V12}
        for nama, ganti, sasaran in KONTROL_V12:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per12[s]).boleh == per12[s][8]]
            c.append(('kontrol v12 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v12 (KASUS_V12)', False, str(e)[:300]))
    # V13 (owner 21 Nov 2026): model atas v13 = kolom wajib KASUS_V13; atas firestore.rules.v12 berbeda tepat BEDA_V12; kontrol V13 membalik sasarannya
    try:
        M13, M12lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v12'))
        salah13 = [K[0] for K in P.KASUS_V13 if nilai_model(M13, K).boleh != K[8]]; beda12 = {K[0] for K in P.KASUS_V13 if nilai_model(M12lama, K).boleh != nilai_model(M13, K).boleh}
        c.append(('model v13 = kolom Wajib di %d kasus ★U; berbeda dari firestore.rules.v12 tepat %s' % (len(P.KASUS_V13), ', '.join(sorted(P.BEDA_V12))), not salah13 and beda12 == set(P.BEDA_V12), {'salah v13': salah13, 'beda v12': sorted(beda12)}))
        per13 = {K[0]: K for K in P.KASUS_V13}
        for nama, ganti, sasaran in KONTROL_V13:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per13[s]).boleh == per13[s][8]]
            c.append(('kontrol v13 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v13 (KASUS_V13)', False, str(e)[:300]))
    # V14 (owner 21 Nov 2026): model atas v14 = kolom wajib KASUS_V14; atas firestore.rules.v13 berbeda tepat BEDA_V13; kontrol V14 membalik sasarannya
    try:
        M14, M13lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v13'))
        salah14 = [K[0] for K in P.KASUS_V14 if nilai_model(M14, K).boleh != K[8]]; beda13 = {K[0] for K in P.KASUS_V14 if nilai_model(M13lama, K).boleh != nilai_model(M14, K).boleh}
        c.append(('model v14 = kolom Wajib di %d kasus ★W; berbeda dari firestore.rules.v13 tepat %s' % (len(P.KASUS_V14), ', '.join(sorted(P.BEDA_V13))), not salah14 and beda13 == set(P.BEDA_V13), {'salah v14': salah14, 'beda v13': sorted(beda13)}))
        per14 = {K[0]: K for K in P.KASUS_V14}
        for nama, ganti, sasaran in KONTROL_V14:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per14[s]).boleh == per14[s][8]]
            c.append(('kontrol v14 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v14 (KASUS_V14)', False, str(e)[:300]))
    # V15 (owner 22 Nov 2026): model atas v15 = kolom wajib KASUS_V15; atas firestore.rules.v14 berbeda tepat BEDA_V14; kontrol V15 membalik sasarannya
    try:
        M15, M14lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v14'))
        salah15 = [K[0] for K in P.KASUS_V15 if nilai_model(M15, K).boleh != K[8]]; beda14 = {K[0] for K in P.KASUS_V15 if nilai_model(M14lama, K).boleh != nilai_model(M15, K).boleh}
        c.append(('model v15 = kolom Wajib di %d kasus ★X; berbeda dari firestore.rules.v14 tepat %s' % (len(P.KASUS_V15), ', '.join(sorted(P.BEDA_V14))), not salah15 and beda14 == set(P.BEDA_V14), {'salah v15': salah15, 'beda v14': sorted(beda14)}))
        per15 = {K[0]: K for K in P.KASUS_V15}
        for nama, ganti, sasaran in KONTROL_V15:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per15[s]).boleh == per15[s][8]]
            c.append(('kontrol v15 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v15 (KASUS_V15)', False, str(e)[:300]))
    # V16 (owner 22 Nov 2026): model atas v16 = kolom wajib KASUS_V16; atas firestore.rules.v15 berbeda tepat BEDA_V15; kontrol V16 membalik sasarannya
    try:
        M16, M15lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v15'))
        salah16 = [K[0] for K in P.KASUS_V16 if nilai_model(M16, K).boleh != K[8]]; beda15 = {K[0] for K in P.KASUS_V16 if nilai_model(M15lama, K).boleh != nilai_model(M16, K).boleh}
        c.append(('model v16 = kolom Wajib di %d kasus ★Y; berbeda dari firestore.rules.v15 tepat %s' % (len(P.KASUS_V16), ', '.join(sorted(P.BEDA_V15))), not salah16 and beda15 == set(P.BEDA_V15), {'salah v16': salah16, 'beda v15': sorted(beda15)}))
        per16 = {K[0]: K for K in P.KASUS_V16}
        for nama, ganti, sasaran in KONTROL_V16:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per16[s]).boleh == per16[s][8]]
            c.append(('kontrol v16 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v16 (KASUS_V16)', False, str(e)[:300]))
    # V17 (owner 23 Nov 2026): model atas v17 = kolom wajib KASUS_V17; atas firestore.rules.v16 berbeda tepat BEDA_V16; kontrol V17 membalik sasarannya
    try:
        M17, M16lama = RM.Rules(R), RM.Rules(baca('firestore.rules.v16'))
        salah17 = [K[0] for K in P.KASUS_V17 if nilai_model(M17, K).boleh != K[8]]; beda16 = {K[0] for K in P.KASUS_V17 if nilai_model(M16lama, K).boleh != nilai_model(M17, K).boleh}
        c.append(('model v17 = kolom Wajib di %d kasus ★Z; berbeda dari firestore.rules.v16 tepat %s' % (len(P.KASUS_V17), ', '.join(sorted(P.BEDA_V16))), not salah17 and beda16 == set(P.BEDA_V16), {'salah v17': salah17, 'beda v16': sorted(beda16)}))
        per17 = {K[0]: K for K in P.KASUS_V17}
        for nama, ganti, sasaran in KONTROL_V17:
            Mx = RM.Rules(rusak(R, ganti)); diam = [s for s in sasaran if nilai_model(Mx, per17[s]).boleh == per17[s][8]]
            c.append(('kontrol v17 "%s": jangkar tepat 1× & model membalik %s' % (nama, ', '.join(sasaran)), not diam, {'diam': diam}))
    except Exception as e: c.append(('model v17 (KASUS_V17)', False, str(e)[:300]))
    H = html if html is not None else baca('kasir-darurat-nominal.html')
    try: s33 = skrip_halaman(H)
    except Exception as e: return c + [('skrip kasir darurat terbaca', False, str(e))]
    c.append(('kasir darurat cabang ini = kasir-v33', "var VERSI_APLIKASI = 'kasir-v33';" in s33, re.findall(r"var VERSI_APLIKASI = '([^']+)'", s33)))
    h32 = html_v32()
    if h32 is None: c.append(('kasir-v32 di %s terbaca dari git' % KASIR_V32_COMMIT[:10], None, 'commit tidak terbaca di mesin ini (riwayat dangkal, fetch gagal) — diukur di job emulator (riwayat penuh)'))
    else: c.append(('kasir-v32 di %s terbaca dari git dan ber-VERSI kasir-v32' % KASIR_V32_COMMIT[:10], "var VERSI_APLIKASI = 'kasir-v32';" in skrip_halaman(h32), ''))
    h = jalan_kasir_palsu(s33, False)
    if h is None: c.append(('kode kasir darurat di server palsu (jsc / node)', None, 'tanpa jsc & node di mesin ini — diukur di job emulator')); return c
    t = tulisan_nota(h)
    c.append(('server palsu: kasir-v33 mencatat nota (simpanNominal) lalu mengirim SATU :commit bercap (capServer REQUEST_TIME, tanpa updateMask, berkunci)',
              not h.get('galat') and h.get('versi') == 'kasir-v33' and len(h.get('antreanSesudahCatat') or []) == 1 and t == [{'cara': 'commit', 'status': 200, 'cap': ['capServer=REQUEST_TIME'], 'mask': False, 'kunci': True}]
              and not h.get('antrean') and not h.get('ditolak'), {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    h = jalan_kasir_palsu(s33, True); t = tulisan_nota(h)
    c.append(('server palsu menolak: kasir-v33 :commit ditolak → cara lama PATCH updateMask ditolak → karcis di daftar "ditolak"',
              not h.get('galat') and [x['cara'] + ':' + str(x['status']) for x in t] == ['commit:403', 'patch-mask:403'] and len(h.get('ditolak') or []) == 1, {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    if h32:
        h = jalan_kasir_palsu(skrip_halaman(h32), False); t = tulisan_nota(h)
        c.append(('server palsu: kasir-v32 mengirim nota lewat PATCH utuh (tanpa updateMask, tanpa cap)', not h.get('galat') and h.get('versi') == 'kasir-v32'
                  and [x['cara'] + ':' + str(x['status']) for x in t] == ['patch:200'], {'galat': (h.get('galat') or '')[:300], 'tulisan': t}))
    else: c.append(('server palsu: kasir-v32 mengirim nota lewat PATCH utuh (tanpa updateMask, tanpa cap)', None, 'kasir-v32 tidak terbaca di mesin ini — diukur di job emulator'))
    return c


def kontrol():
    """kerusakan pada bahan pemeriksa statis wajib ketahuan karena SEBABNYA."""
    global GESER_TAHUN
    R = baca('firestore.rules'); D = baca(DOK); Hh = baca('kasir-darurat-nominal.html'); kode = 0
    assert '| 7 | ★P20 |' in D and "updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }]" in Hh
    kasus = [
        ('kolom Wajib ★P20 di docs dibalik (DITOLAK → LOLOS)', {'dok': re.sub(r'(\n\| 7 \| ★P20 \|[^\n]*?\| )DITOLAK( \|)', r'\1LOLOS\2', D)}, 'kolom "Wajib"'),
        ('rules v8: usul harga atas nama orang lain (model v8 ikut berubah)', {'rules': R.replace(" && d.get('usulUid', '') == request.auth.uid", "")}, 'model v8 = kolom Wajib'),
        ('rules v7: suku pintu tanpa batas waktu (model ikut berubah)', {'rules': R.replace("\n        && request.time < p.data.sampai ? int(p.data.tahun) : 0;", " ? int(p.data.tahun) : 0;")}, 'model v7 = kolom Wajib'),
        ('kasir darurat tanpa cap jam server (:commit tanpa updateTransforms)', {'html': Hh.replace(",\n        updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }] }] })", " }] })")}, 'server palsu: kasir-v33'),
        ('kasir darurat tanpa cara lama (ditolak langsung ke "ditolak")', {'html': Hh.replace("          if (bercap) { kirimItem(item, false, true); return; }", "")}, 'server palsu menolak'),
        # sanggahan bukti emulator 7 Okt: alat emulator yang TIDAK menggeser tahun dokumen uji (kedaluwarsa 1 Jan 2027) wajib ketahuan di Mac, sebelum Januari
        ('alat emulator tidak menggeser tahun dokumen uji (bukti server kedaluwarsa 1 Jan 2027)', {'geser': False}, 'model: dokumen uji digeser ke jam lain'),
    ]
    for nama, rusak_, sebab in kasus:
        if any(v in (R, D, Hh) for v in rusak_.values() if isinstance(v, str)): print('KONTROL BASI  ' + nama); kode = 3; continue
        GESER_TAHUN = rusak_.get('geser', True)
        try: c = periksa(rusak_.get('rules'), rusak_.get('dok'), rusak_.get('html'))
        finally: GESER_TAHUN = True
        g = [x for x in c if x[1] is False]; tepat = [x for x in g if x[0].startswith(sebab)]
        print(('BERBUNYI ' if tepat else 'DIAM!!   ') + nama + ' → ' + (tepat[0][0][:100] + ' · ' + json.dumps(tepat[0][2], ensure_ascii=False)[:160] if tepat else ('lain: ' + g[0][0][:100] if g else '-')))
        if not tepat: kode = 3
    return kode


if __name__ == '__main__':
    arg = sys.argv[1:]
    opsi = lambda n: arg[arg.index(n) + 1] if n in arg and arg.index(n) + 1 < len(arg) else ''
    if '--kontrol' in arg: sys.exit(kontrol())
    if '--emulator' not in arg:
        c = periksa(); g = [x for x in c if x[1] is False]; lewat = [x for x in c if x[1] is None]
        for n, ok, k in c: print(('✓ ' if ok else ('⚠ DILEWATI ' if ok is None else '✗ ')) + n + ('' if ok else ' → ' + (k if isinstance(k, str) else json.dumps(k, ensure_ascii=False))[:400]))
        print('BUKTI SERVER RULES v7 (statis + model + kode kasir di server palsu): %d lulus · %d dilewati · %d gagal — emulator: workflow "Uji rules di emulator"'
              % (len(c) - len(g) - len(lewat), len(lewat), len(g)))
        sys.exit(2 if g else 0)
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        print('DITOLAK: --emulator menyalakan Firebase Emulator & node — HANYA di runner GitHub Actions (CLAUDE.md, keputusan owner 27 Sep 2026).\n'
              'Jalankan workflow "Uji rules di emulator". Di Mac boleh: --periksa / --kontrol.')
        sys.exit(2)
    lap = jalankan_emulator()
    md = ringkasan_md(lap)
    if opsi('--keluar'): os.makedirs(os.path.dirname(os.path.abspath(opsi('--keluar'))), exist_ok=True); json.dump(lap, open(opsi('--keluar'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if opsi('--ringkasan'): open(opsi('--ringkasan'), 'w', encoding='utf-8').write(md)
    print('\n' + md)
    print('BUKTI SERVER RULES v7: ' + ('LULUS' if lap['lulus'] else 'GAGAL'))
    sys.exit(0 if lap['lulus'] else 2)
