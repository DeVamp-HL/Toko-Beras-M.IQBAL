#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_rules.py — pemeriksa STATIS firestore.rules v4 (putaran 23 + 25), tanpa Node & tanpa emulator.
Membuktikan bentuk rules, bukan perilaku server (itu docs/uji-rules-v4.md: Playground ★).

  1. tiap nama di baru/js/data/koleksi.js punya blok `match /<nama>/{…}` SENDIRI (+ aksesAkun, permintaanAkses, arsipTahun eksplisit); blok di LUAR
     koleksi.js hanya yang dikenal (LUAR_KOLEKSI: aksesAkun, permintaanAkses, arsipTahun, ringkasanKasir, batuNisan, fotoBon);
  2. owner() masih berbasis EMAIL owner; tidak ada allow yang cuma `masuk()` (siapa pun yang login);
  3. jalur kasir@ (v7: kasir darurat SAJA — nota penjualan + kirim ulangnya, denyut perangkatStatus, baca ringkasanKasir) masih ada dan dipersempit ke
     email kasir@ (kasir()); kasir() di tempat LAIN mana pun = cacat (v7 mencabut piutangMutasi, stokBahanLiteran, logAktivitas, pengaturan/aksesKasir);
  4. tiap create/update bukan-owner lewat fungsi yang memeriksa uid penulis (jujur() / diubahOlehUid / akunUid), atau ada di daftar
     pengecualian peta (permintaanAkses = uid sendiri); bukan-owner tidak pernah DELETE; arsipTahun owner saja; payung owner di paling bawah;
  5. daftar peran per koleksi di rules SAMA dengan baru/js/data/akses.js (BACA_STAF, DOK_STAF, BUAT_STAF, UBAH_STAF, KREDIT_STAF);
  6. aksesAkun tidak pernah bisa memberi peran owner;
  7. (putaran 25) TANPA PAYUNG: Firestore memberi akses kalau SALAH SATU blok yang cocok mengizinkan, jadi payung owner mengalahkan kunci periode.
     GAGAL bila ada match rekursif ({…=**}) yang memberi izin tulis, atau wildcard koleksi (/{x}/…) apa pun;
  8. (putaran 25) KUNCI PERIODE: tiap koleksi bertanggal di baru/js/data/kunci-periode.js (KP_KOLEKSI) menilai tanggalnya di SETIAP create/update/delete,
     untuk owner, kasir@, dan bukan-owner (tglStaf, tanpa get()); field = KP_KOLEKSI; pajak TIDAK dikunci (K6); tenggangMin() = KP_TENGGANG_MIN;
     get() dokumen kunci hanya di terkunci(), dan terkunci() hanya dipanggil bolehBulan() di belakang bebas() (≤ 1 access call per operasi);
     aturanToko/kunciPeriode: naik satu / turun satu dengan alasan ≥ 10, riwayat lama utuh, tidak pernah dihapus.
  9. (v6, draf 1 Okt 2026) BERITA ACARA TUTUP BUKU HANYA MAJU: update owner && ubahBukuSah(…), fungsinya tanpa get(). MODEL: fungsi rules itu APA ADANYA
     diterjemahkan ke Python lalu dinilai pada tulisan SAH dari kode (wajib boleh) dan tulisan TELAT (wajib ditolak). Model bukan server — bukti server =
     docs/uji-rules-v6.md (Playground ★). v7 (sanggahan rules 7 Okt): create = owner && acaraBaru(id), update + acaraTutupPintu(…), delete hanya
     'dibatalkan' — bentuk persis (BUKU_V7).
 10. (v7 FINAL — owner 7 Okt 2026) v7 = firestore.rules.v6 + PERSIS daftar ubahan ini (sisanya dibandingkan tanpa komentar & spasi, per blok):
     (a) hemat baca: ulangKasirBercap() = affectedKeys().hasOnly(['capServer']) && (capServer tidak ada || capServer == request.time), dipakai HANYA
         sebagai suku `kasir() && ulangKasirBercap()` di update penjualan; blok batuNisan: read & delete owner(), create/update owner() && capServer ==
         request.time, tanpa staf/kasir/get();
     (b) persetujuan: read owner || staf(ben, karyawan), create owner || stafMintaNego(ben, karyawan) (tindakan 'nego', status 'menunggu', negoUid =
         uid penulis, tanpa kolom keputusan), update/delete owner — sama dengan akses.js BUAT_STAF / BACA_STAF;
     (c) fotoBon: read/delete owner, create owner + bentuk (id = id dokumen, idBon teks, jenis gambar, base64 ≤ 960.000), TANPA update;
     (d) kasir@ dipangkas (lihat 3);
     (e) PINTU TUTUP BUKU — 11 (termasuk blok arsipTahun & tutupBukuAcara yang mengikatnya).
 11. (v7, keputusan owner 7 Okt K8 "pengecualian sempit"; dipersempit sesudah sanggahan rules 7 Okt) PINTU TUTUP BUKU: semua fungsi PINTU_FUNGSI PERSIS
     bentuknya dan hanya dipanggil dari tempatnya (PEMANGGIL_PINTU); pintuTulis HANYA sebagai suku `(owner() && pintuTulis('<koleksi>', id, <bulan BARU>))` di
     CREATE dan pintuHapus HANYA di DELETE `owner() && (<kunci lama> || pintuHapus('<koleksi>', id, <bulan LAMA>))` — tepat untuk koleksi bertanggal yang
     diarsip tutup buku (tbDaftarKoleksi mesin ∩ KP_KOLEKSI, dibaca dari berkasnya) — pintuTitik & pintuSah hanya di pengaturan, arsipSah hanya di create /
     update arsipTahun, acaraBaru / acaraTutupPintu hanya di create / update tutupBukuAcara; TIDAK di read/staf/kasir@. Daftar koleksi di rules SAMA dengan
     sumbernya: kolPembuka = KP_KOLEKSI_PEMBUKA = toko.js CACHE_PEMBUKA, kolArsip = KP_KOLEKSI_PINTU = mesin ∩ KP_KOLEKSI, koleksi arsip tanpa kunci = mesin −
     KP_KOLEKSI; jalur arsip 'Y|koleksi|id' = firebase.js arsipkanBerkas. Lalu MODEL: penafsir rules mini (alat-uji/rules_mini.py) menilai TEKS rules pada
     kasus Playground ★ v7 (docs/uji-rules-v7.md — dokumen uji yang sama; bagian "Wajib owner" = WAJIB_V7 persis) + access call jalur pintu (≤ 3 per
     operasi). Model bukan server.

  12. (v8 — B1, owner 16 Nov 2026) v8 = firestore.rules.v7 + PERSIS tiga ubahan (dicabut balik oleh ke_v7, sisanya dibandingkan tanpa komentar & spasi dengan
     firestore.rules.v7; semua pemeriksa v7 di atas dijalankan atas hasil cabut-balik itu): (v8-1/2) aturanToko 'hargaTingkat' & 'produkArsip' terbaca
     ben/karyawan (= akses.js DOK_STAF); (v8-3) persetujuan create + stafUsulHarga(ben, karyawan) — tindakan 'hargaPelanggan', status 'menunggu', usulUid =
     uid penulis, tanpa kolom keputusan (bentuk persis). MODEL: penafsir rules mini menilai kasus ★H docs/uji-rules-v8.md (KASUS_V8) atas v8, dan atas
     firestore.rules.v7 yang berbeda WAJIB persis BEDA_V7. Bukti server: alat-uji/uji_rules_emulator.py bagian V8.
  13. (v9 — B2, owner 17 Nov 2026) v9 = firestore.rules.v8 + PERSIS satu ubahan (dicabut balik oleh ke_v8; sisanya dibandingkan dengan firestore.rules.v8;
     semua pemeriksa v8 & v7 dijalankan atas hasil cabut-balik): persetujuan create + stafMintaKredit(ben) — tindakan 'kredit', status 'menunggu', mintaUid =
     uid penulis, tanpa kolom keputusan. MODEL: kasus ★J docs/uji-rules-v9.md (KASUS_V9) atas v9, dan atas firestore.rules.v8 yang berbeda WAJIB persis BEDA_V8.
     Bukti server: alat-uji/uji_rules_emulator.py bagian V9.
  14. (v10 — B3, owner 18 Nov 2026) v10 = firestore.rules.v9 + PERSIS dua blok baru & tiga fungsinya (dicabut balik oleh ke_v9; sisanya dibandingkan dengan
     firestore.rules.v9; semua pemeriksa v9, v8 & v7 dijalankan atas hasil cabut-balik): blok suratJalan (create owner || stafBuatSJ(ben) — status 'berangkat',
     tanpa kolom penerimaan; update owner || stafTandaiSJ(ben, karyawan) — 'berangkat' → 'diterima' / 'gagal', kolom = akses.js KOLOM_TANDAI_SJ + atribusi
     ubah) dan blok buktiTerima (create (owner || stafBuat(ben, karyawan)) && buktiSah(id), tanpa update). MODEL: kasus ★L docs/uji-rules-v10.md (KASUS_V10)
     atas v10, dan atas firestore.rules.v9 yang berbeda WAJIB persis BEDA_V9. Bukti server: alat-uji/uji_rules_emulator.py bagian V10.
  15. (v11 — B4, owner 18 Nov 2026) v11 = firestore.rules.v10 + PERSIS tiga ubahan & tiga fungsinya (dicabut balik oleh ke_v10; sisanya dibandingkan dengan
     firestore.rules.v10; semua pemeriksa v10, v9, v8 & v7 dijalankan atas hasil cabut-balik): (v11-1) pesanan create + stafBuatPesanan(ben) — 'dipesan',
     belum bernota, tanpa kolom batal; (v11-2) pesanan update + stafAturPesanan(ben) — dipesan / diantar → dipesan / diantar / batal, kolom = akses.js
     KOLOM_ATUR_PESANAN + atribusi ubah; (v11-3) blok orderRutin (create owner || stafBuat(ben); update owner || stafUbahRutin(ben) — kolom = akses.js
     KOLOM_UBAH_RUTIN + atribusi ubah). MODEL: kasus ★M docs/uji-rules-v11.md (KASUS_V11) atas v11, dan atas firestore.rules.v10 yang berbeda WAJIB persis
     BEDA_V10. Bukti server: alat-uji/uji_rules_emulator.py bagian V11.
  16. (v12 — paket S2b tanda kenal, owner 19 Nov 2026) v12 = firestore.rules.v11 + PERSIS satu blok baru, tanpa fungsi baru (dicabut balik oleh ke_v11;
     sisanya dibandingkan dengan firestore.rules.v11; semua pemeriksa v11, v10, v9, v8 & v7 dijalankan atas hasil cabut-balik): (v12-1) blok tandaKenal
     — baca owner/ben/karyawan; create owner || stafBuat(ben, karyawan); ubah & hapus owner. MODEL: kasus ★S docs/uji-rules-v12.md (KASUS_V12) atas
     v12, dan atas firestore.rules.v11 yang berbeda WAJIB persis BEDA_V11. Bukti server: alat-uji/uji_rules_emulator.py bagian V12.

    python3 alat-uji/periksa_rules.py            → LULUS / daftar cacat (keluar 2)
    python3 alat-uji/periksa_rules.py --kontrol  → berkas rules cacat buatan WAJIB gagal (keluar 3 kalau ada yang lolos)
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules_mini  # noqa: E402

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
EMAIL_OWNER = 'owner@tokoberasmiqbal.web.app'; EMAIL_KASIR = 'kasir@tokoberasmiqbal.web.app'
PERAN = ['ben', 'karyawan']
FUNGSI_JUJUR = {'stafBuat', 'stafBuatTipe', 'stafBuatJual', 'stafJejak', 'stafUbahPesanan', 'stafDenyut', 'stafBuatWadah', 'stafBuatLahir', 'stafMintaNego', 'stafUsulHarga', 'stafMintaKredit', 'stafBuatSJ', 'stafTandaiSJ',
                'stafBuatPesanan', 'stafAturPesanan', 'stafUbahRutin', 'stafMintaKeluar', 'stafKirimPesan', 'stafCatatMasuk', 'stafKabarMasuk', 'stafHitungLaci'}   # v16: hitungan laci tablet (lewat stafBuat)   # v15: barang masuk tablet (lewat stafBuat)   # v5 (putaran 39) & v7 (permintaan nego): lewat stafBuat() → jujur()
LUAR_KOLEKSI = ['aksesAkun', 'permintaanAkses', 'arsipTahun', 'ringkasanKasir', 'batuNisan', 'fotoBon', 'buktiTerima', 'notifOwner']   # blok rules di luar baru/js/data/koleksi.js (v7: fotoBon)


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


def daftar_js(teks, nama):
    m = re.search(r'export const ' + nama + r' = \[(.*?)\];', teks, re.S); return re.findall(r"'(\w+)'", m.group(1)) if m else None


def peta_js(teks, nama):
    m = re.search(r'export const ' + nama + r' = \{(.*?)\};', teks, re.S)
    return dict((k, re.findall(r"'(\w+)'", v)) for k, v in re.findall(r"(\w+): \[([^\]]*)\]", m.group(1))) if m else None


def blok_rules(rules):
    """nama koleksi → teks blok (match satu tingkat)."""
    out = {}
    for m in re.finditer(r'\n    match /(\w+)/\{(\w+)\} \{\n(.*?)\n    \}', rules, re.S): out[m.group(1)] = m.group(3)
    return out


def fungsi_rules(rules):
    """nama fungsi → badannya (pencocok kurung kurawal; fungsi satu baris maupun bertingkat)."""
    out = {}
    for m in re.finditer(r'function (\w+)\(([^)]*)\) \{', rules):
        i = m.end() - 1; d = 0
        for j in range(i, len(rules)):
            if rules[j] == '{': d += 1
            elif rules[j] == '}':
                d -= 1
                if d == 0: out[m.group(1)] = rules[i + 1:j]; break
    return out


def tanpa_komentar(t): return re.sub(r'//[^\n]*', '', t)


def allow(blok, op):
    """Baris-baris allow (boleh bersambung ke baris berikut sampai ';') yang menyebut operasi op."""
    hasil = []
    for m in re.finditer(r'allow ([a-z, ]+): (.*?);', blok, re.S):
        ops = [x.strip() for x in m.group(1).split(',')]
        if op in ops or ('write' in ops and op in ('create', 'update', 'delete')) or ('read' in ops and op in ('get', 'list')): hasil.append(m.group(2))
    return hasil


OPERASI = ['get', 'list', 'create', 'update', 'delete']
# v7: satu-satunya hak kasir@ (kasir-darurat-nominal.html: nota :commit / PATCH, denyut, katalog ringkasanKasir/aktif) — permintaanAkses memakai !kasir()
KASIR_BOLEH = {('penjualan', 'create'), ('penjualan', 'update'), ('perangkatStatus', 'create'), ('perangkatStatus', 'update'), ('ringkasanKasir', 'get'), ('ringkasanKasir', 'list')}


def suku_atas(kondisi):
    """Suku-suku OR tingkat teratas dari satu kondisi allow (kurung dihormati)."""
    k = re.sub(r'^if ', '', re.sub(r'\s+', ' ', kondisi).strip()); d = 0; bag = []; cur = ''; i = 0
    while i < len(k):
        c = k[i]
        if c in '([{': d += 1
        elif c in ')]}': d -= 1
        if d == 0 and k[i:i + 4] == ' || ': bag.append(cur.strip()); cur = ''; i += 4; continue
        cur += c; i += 1
    bag.append(cur.strip()); return bag


KP_TEKS = None   # kontrol: pengganti isi kunci-periode.js (mis. minimal diturunkan di KEDUA tempat)
TENGGANG_OWNER = 3   # keputusan owner 25 Sep: bulan M paling cepat dikunci tanggal 4 bulan M+1


def kp_js():
    t = KP_TEKS if KP_TEKS is not None else baca('baru/js/data/kunci-periode.js')
    m = re.search(r'export const KP_KOLEKSI = \{(.*?)\};', t, re.S); kol = dict(re.findall(r"(\w+): '(\w+)'", m.group(1))) if m else {}
    tm = re.search(r'export const KP_TENGGANG_MIN = (\d+);', t)
    return kol, int(tm.group(1)) if tm else None


def periksa_kunci(rules, B, F):
    """8 · kunci periode (putaran 25)."""
    cacat = []; KOL, TMIN = kp_js()
    if not KOL or TMIN is None: return ['kunci-periode.js: KP_KOLEKSI / KP_TENGGANG_MIN tidak terbaca']
    rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    if '25200000' not in F.get('wib', '') or 'request.time.toMillis()' not in F.get('wib', '') or 'timestamp.value(' not in F.get('wib', ''): cacat.append('wib() bukan request.time + 7 jam lewat timestamp.value(toMillis())')
    mt = re.search(r'return (\d+);', F.get('tenggangMin', ''))
    if not mt or int(mt.group(1)) != TMIN: cacat.append('tenggangMin() di rules (%s) beda dengan KP_TENGGANG_MIN (%s)' % (mt and mt.group(1), TMIN))
    if TMIN < TENGGANG_OWNER or (mt and int(mt.group(1)) < TENGGANG_OWNER): cacat.append('tenggang minimal di bawah %d hari (keputusan owner 25 Sep: bulan M paling cepat dikunci tanggal %d bulan M+1)' % (TENGGANG_OWNER, TENGGANG_OWNER + 1))
    if 'wib().day() <= tenggangMin()' not in F.get('bebas', '') or 'b >= bulanIni()' not in F.get('bebas', ''): cacat.append('bebas() bukan "bulan berjalan atau masa tenggang minimal"')
    if 'wib().day() > tenggangMin()' not in F.get('bolehDikunci', '') or 'b < bulanIni() - 1' not in F.get('bolehDikunci', ''): cacat.append('bolehDikunci() tidak menegakkan tenggang minimal (bulan lalu dikunci sebelum tanggal tenggang, atau bulan berjalan bisa dikunci)')
    # get() dokumen kunci hanya di terkunci(); terkunci() hanya dipanggil bolehBulan() di belakang bebas()
    for n, badan in F.items():
        if 'aturanToko/kunciPeriode' in badan and n != 'terkunci': cacat.append('get() dokumen kunci di luar terkunci(): ' + n)
        if re.search(r'\bterkunci\(', badan) and n not in ('bolehBulan',): cacat.append('terkunci() dipanggil dari ' + n + ' (harus hanya bolehBulan, di belakang bebas)')
    if 'get(/databases/$(database)/documents/aturanToko/kunciPeriode)' not in F.get('terkunci', ''): cacat.append('terkunci() tidak membaca aturanToko/kunciPeriode')
    if rata(F.get('bolehBulan', '')) != 'return bebas(b) || !terkunci(b);': cacat.append('bolehBulan() bukan "bebas(b) || !terkunci(b)" — get() bisa terpanggil untuk bulan berjalan: ' + rata(F.get('bolehBulan', '')))
    if 'terkunci' in F.get('tglStaf', '') or 'bolehBulan' in F.get('tglStaf', '') or 'bebas(' not in F.get('tglStaf', ''): cacat.append('tglStaf() membaca dokumen kunci (bukan-owner jadi 2 access call per dokumen) atau tidak menilai tanggal')
    if 'resource.data' not in F.get('tglUbah', '').replace('request.resource.data', '') or 'lebihTua(' not in F.get('tglUbah', ''): cacat.append('tglUbah() tidak menilai tanggal LAMA (koreksi di tempat pada bulan terkunci lolos)')
    if 'bonTanggal' not in F.get('bulanUP', ''): cacat.append('bulanUP(): bon lama pemasok tidak dinilai dari bonTanggal (K4)')
    for fn in ('tglLama', 'upLama'):
        if not rata(F.get(fn, '')).startswith('return resource == null || bolehBulan('): cacat.append(fn + '(): hapus dokumen yang TIDAK ADA ditolak (resource null) — satu hapus kantong id+1 yang tidak ada menggagalkan seluruh batch')
    for n, f in sorted(KOL.items()):
        b = B.get(n, '')
        if not b: cacat.append('koleksi bertanggal tanpa blok: ' + n); continue
        up = n == 'utangPemasokMutasi'; baru, ubah, lama = ('upBaru()', 'upUbah()', 'upLama()') if up else ("tglBaru('%s')" % f, "tglUbah('%s')" % f, "tglLama('%s')" % f)
        if n == 'pengaturan': baru, lama = "(id != 'titikKas' || tglBaru('%s') || pintuTitik())" % f, "(id != 'titikKas' || tglLama('%s'))" % f   # v7: pintu tutup buku (periksa_pintu)
        pintu = suku_pintu(n, KOL)   # v7: suku pintu tutup buku di create — bentuk & tempatnya dijaga periksa_pintu
        for op, wajib in (('create', baru), ('update', ubah if n != 'pengaturan' else baru), ('delete', lama)):
            xs = allow(b, op)
            if not xs: cacat.append(n + ': tidak ada allow ' + op); continue
            for x in xs:
                for suku in suku_atas(x):
                    # kasir@ (kasir darurat): create dinilai kunci seperti owner (tglBaru, ≤ 1 get per permintaan satu dokumen); update HANYA tulis-ulang identik; TIDAK PERNAH hapus
                    if 'kasir()' in suku and op == 'delete': cacat.append('%s: kasir@ boleh menghapus catatan bertanggal: %s' % (n, suku)); continue
                    if 'kasir()' in suku and op == 'update':
                        s0 = re.sub(r'^\((.*)\)$', r'\1', rata(suku))
                        # v7 (hemat baca): kirim ulang bercap HANYA di penjualan (kasir darurat kasir-v33); koleksi kasir lain tetap tulis-ulang identik
                        if s0 == 'kasir() && ulangKasirBercap()' and n == 'penjualan': continue
                        if s0 != 'kasir() && tulisUlangSama()': cacat.append('%s: update kasir@ bukan tulis-ulang identik: %s' % (n, suku))
                        continue
                    if op == 'create' and rata(suku) == pintu: continue
                    if re.search(r'\bstaf\w*\(', suku):
                        if "tglStaf('%s')" % f not in suku: cacat.append('%s: %s bukan-owner tanpa tglStaf(%s): %s' % (n, op, f, suku))
                    elif wajib not in suku: cacat.append('%s: %s tanpa kunci periode (%s): %s' % (n, op, wajib, suku))
    for n in ('pajakSetoran', 'pajakOmzetLuar'):
        if re.search(r'tgl(Baru|Ubah|Lama)|bolehBulan|up(Baru|Ubah|Lama)', B.get(n, '')): cacat.append(n + ' ikut dikunci — keputusan owner K6: tidak dikunci')
    lain = [n for n, b in B.items() if n not in KOL and re.search(r'tgl(Baru|Ubah|Lama)\(', b)]
    if lain: cacat.append('koleksi di luar KP_KOLEKSI memakai kunci tanggal (rules & kunci-periode.js harus sama): ' + ', '.join(lain))
    at = B.get('aturanToko', '')
    if not any("id != 'kunciPeriode' || kunciPertama()" in x for x in allow(at, 'create')): cacat.append('aturanToko: create kunciPeriode tanpa kunciPertama()')
    if not any("id != 'kunciPeriode' || kunciGeser()" in x for x in allow(at, 'update')): cacat.append('aturanToko: update kunciPeriode tanpa kunciGeser()')
    if not any(rata(x) == "if owner() && id != 'kunciPeriode'" for x in allow(at, 'delete')): cacat.append('aturanToko: dokumen kunci bisa dihapus')
    kg = rata(F.get('kunciGeser', ''))
    if '(lama.size() == 0 || d.riwayat[0:lama.size()] == lama)' not in kg: cacat.append('kunciGeser(): irisan riwayat lama tanpa penjaga kosong — list[0:0] GALAT di server (Playground 25 Sep, Index -1), owner tidak bisa kunci/buka bila riwayat kosong')
    for syarat, arti in (('d.riwayat[0:lama.size()] == lama', 'riwayat lama boleh ditulis ulang'), ('d.riwayat.size() == lama.size() + 1', 'riwayat tidak bertambah tepat satu'),
                         ('bulanDari(d.sampaiBulan) == bulanDari(s0) + 1', 'kunci boleh melompati bulan'), ('bulanDari(d.sampaiBulan) == bulanDari(s0) - 1', 'buka boleh lebih dari satu bulan'),
                         ('alasan.size() >= 10', 'buka tanpa alasan ≥ 10 huruf'), ('olehUid == request.auth.uid', 'entri riwayat tanpa uid penulis'), ('bolehDikunci(bulanDari(d.sampaiBulan))', 'kunci tanpa tenggang')):
        if syarat not in kg: cacat.append('kunciGeser(): ' + arti)
    if 'bolehDikunci(' not in F.get('kunciPertama', '') or "aksi == 'kunci'" not in F.get('kunciPertama', ''): cacat.append('kunciPertama(): kunci pertama tanpa tenggang / tanpa entri kunci')
    return cacat


FUNGSI_BUKU = ('percobaanBuku', 'pemegangBuku', 'majuBuku', 'pemegangBukuSah', 'mulaiLagiBuku', 'ubahBukuSah')
UPDATE_BUKU = 'if owner() && (tulisUlangSama() || ubahBukuSah(request.resource.data, resource.data))'


class _Teks(str):
    """string rules: matches() = pola RE2 atas SELURUH teks (pola tutup buku tidak memakai fitur khusus RE2)."""
    def matches(self, pola): return re.fullmatch(pola, self) is not None


def _bungkus(x):
    if isinstance(x, dict): return dict((k, _bungkus(v)) for k, v in x.items())
    if isinstance(x, list): return [_bungkus(v) for v in x]
    return _Teks(x) if isinstance(x, str) else x


def model_buku(rules):
    """9 · fungsi tutupBukuAcara dari rules (APA ADANYA) → nilai(baru, lama) Python. Hanya bentuk sederhana yang diterjemahkan (satu return; && || == != >
    in [..] .get() .matches() '…' {}); bentuk lain = (None, alasan). Galat saat dinilai = DITOLAK (seperti server)."""
    R = tanpa_komentar(rules); F = fungsi_rules(R); py = []
    for n in FUNGSI_BUKU:
        sig = re.search(r'function ' + n + r'\(([^)]*)\) \{', R)
        if n not in F or not sig: return None, 'fungsi %s tidak ada' % n
        m = re.fullmatch(r'\s*return (.*);\s*', F[n], re.S)
        if not m: return None, 'fungsi %s bukan satu return' % n
        bag = re.split(r"('[^'\\]*')", m.group(1)); kode = ''.join(bag[0::2])
        if re.search(r"get\(/|exists\(|request\.|resource\.|\bis\b|!(?!=)|\?|\"|\b(let|true|false|null)\b", kode): return None, 'fungsi %s memakai bentuk yang tidak diterjemahkan model' % n
        py.append('def %s(%s):\n    return (%s)\n' % (n, sig.group(1), ''.join(('_Teks(%s)' % b) if i % 2 else b.replace('&&', ' and ').replace('||', ' or ') for i, b in enumerate(bag))))
    ruang = {'_Teks': _Teks}
    try: exec('\n'.join(py), ruang)
    except SyntaxError as e: return None, 'terjemahan model gagal: %s' % e

    def nilai(baru, lama):
        try: return bool(ruang['ubahBukuSah'](_bungkus(baru), _bungkus(lama)))
        except Exception: return False
    return nilai, ''


# Dokumen contoh = bentuk yang ditulis tutup-buku-logika.js (paraf.pada / diambilAlihPada / dibatalkanPada = w.kini = toISOString()). SAMA dengan
# docs/uji-rules-v6.md: tujuh dokumen uji (resource) dan kasus ★A (wajib BOLEH) / ★B (wajib DITOLAK); M = kasus model saja, V = batas yang diakui.
P0, P1, P2 = '2027-01-04T03:00:00.000Z', '2027-01-05T03:00:00.000Z', '2027-01-06T03:00:00.000Z'   # percobaan lebih LAMA / percobaan ini / lebih BARU
T1, T2 = '2027-01-05T05:00:00.000Z', '2027-01-05T07:00:00.000Z'   # jam batal
X0, X1, X2 = '2027-01-05T05:30:00.000Z', '2027-01-05T06:00:00.000Z', '2027-01-05T08:00:00.000Z'   # jam ambil alih
HA, MB = {'id': 'hp-a', 'nama': 'HP A'}, {'id': 'mac-b', 'nama': 'Mac B'}


def acara(status, pada, pemegang=None, **lain):
    d = {'tahun': 1990, 'status': status, 'paraf': {'pada': pada}}
    if pemegang: d['pemegang'] = pemegang
    d.update(lain); return d


def alih(status, pada, baru, lama, jam, **lain): return acara(status, pada, baru, pemegangLama=lama, diambilAlihPada=jam, **lain)


DOK_BUKU = {
    'uji-v6-berjalan': acara('berjalan', P1, HA), 'uji-v6-terkunci': acara('terkunci', P1, HA), 'uji-v6-membatalkan': acara('membatalkan', P1, HA, dibatalkanPada=T1),
    'uji-v6-dibatalkan': acara('dibatalkan', P1, HA, dibatalkanPada=T1), 'uji-v6-selesai': acara('selesai', P1, MB), 'uji-v6-alih': alih('berjalan', P1, MB, HA, X1),
    'uji-v6-alih-batal': alih('dibatalkan', P1, MB, HA, X1, dibatalkanPada=T2),
}
# (no, nama, lama = dokumen uji / isi lama, baru = request.resource.data, wajib boleh?)
KASUS_BUKU = [
    ('★A1', 'berjalan → terkunci (kiriman penanda: susunKunci / lanjutBuku)', 'uji-v6-berjalan', acara('terkunci', P1, HA), True),
    ('★A2', 'berjalan → membatalkan (susunBatal)', 'uji-v6-berjalan', acara('membatalkan', P1, HA, dibatalkanPada=T1), True),
    ('★A3', 'terkunci → membatalkan (susunBatal)', 'uji-v6-terkunci', acara('membatalkan', P1, HA, dibatalkanPada=T1), True),
    ('★A4', 'terkunci → selesai (susunSelesai)', 'uji-v6-terkunci', acara('selesai', P1, HA), True),
    ('★A5', 'membatalkan → membatalkan (lanjut pembatalan)', 'uji-v6-membatalkan', acara('membatalkan', P1, HA, dibatalkanPada=T1), True),
    ('★A6', 'membatalkan → dibatalkan (akhir pembatalan)', 'uji-v6-membatalkan', acara('dibatalkan', P1, HA, dibatalkanPada=T1), True),
    ('★A7', 'dibatalkan → membatalkan dari perangkat lain (P4-7: sisa saldo pembuka mendarat belakangan)', 'uji-v6-dibatalkan', acara('membatalkan', P1, MB, dibatalkanPada=T1), True),
    ('★A8', 'mulai lagi sesudah dibatalkan: berjalan, jam mulai lebih baru, pemegang baru', 'uji-v6-dibatalkan', acara('berjalan', P2, MB), True),
    ('★A9', 'mulai lagi satu kiriman: langsung terkunci', 'uji-v6-dibatalkan', acara('terkunci', P2, MB), True),
    ('★A10', 'ambil alih berjalan', 'uji-v6-berjalan', alih('berjalan', P1, MB, HA, X1), True),
    ('★A11', 'ambil alih terkunci', 'uji-v6-terkunci', alih('terkunci', P1, MB, HA, X1), True),
    ('★A12', 'ambil alih membatalkan', 'uji-v6-membatalkan', alih('membatalkan', P1, MB, HA, X1, dibatalkanPada=T1), True),
    ('★A13', 'sesudah ambil alih, pemegang baru melanjutkan', 'uji-v6-alih', alih('terkunci', P1, MB, HA, X1), True),
    ('★A14', 'ambil alih kedua (jam ambil alih lebih baru)', 'uji-v6-alih', alih('berjalan', P1, HA, MB, X2), True),
    ('M1', 'mulai lagi tanpa pemegang (perangkat tanpa id)', 'uji-v6-dibatalkan', acara('berjalan', P2), True),
    ('M2', 'berita acara tanpa pemegang: berjalan → terkunci', acara('berjalan', P1), acara('terkunci', P1), True),
    ('★B1', 'jalan MULAI: berjalan percobaan lama di atas selesai', 'uji-v6-selesai', acara('berjalan', P0, HA), False),
    ('★B2', 'jalan MULAI satu kiriman: terkunci percobaan lama di atas selesai', 'uji-v6-selesai', acara('terkunci', P0, HA), False),
    ('★B3', 'percobaan lama mulai di atas percobaan yang lebih baru (dibatalkan)', 'uji-v6-dibatalkan', acara('berjalan', P0, MB), False),
    ('★B4', 'percobaan lama satu kiriman di atas percobaan yang lebih baru (dibatalkan)', 'uji-v6-dibatalkan', acara('terkunci', P0, MB), False),
    ('★B5', 'percobaan lama mulai di atas percobaan yang berjalan', 'uji-v6-berjalan', acara('berjalan', P0, MB), False),
    ('★B6', 'percobaan lama mulai di atas percobaan yang terkunci', 'uji-v6-terkunci', acara('berjalan', P0, MB), False),
    ('★B7', 'percobaan lama mulai di atas pembatalan', 'uji-v6-membatalkan', acara('berjalan', P0, MB), False),
    ('★B8', 'ekor pembatalan HP beku: dibatalkan percobaan lama di atas selesai', 'uji-v6-selesai', acara('dibatalkan', P0, HA, dibatalkanPada=T1), False),
    ('★B9', 'ekor pembatalan: dibatalkan percobaan lama di atas terkunci', 'uji-v6-terkunci', acara('dibatalkan', P0, MB, dibatalkanPada=T1), False),
    ('★B10', 'ambil alih: penanda HP lama (terkunci) di atas berjalan pemegang baru', 'uji-v6-alih', acara('terkunci', P1, HA), False),
    ('★B11', 'ambil alih: penanda HP lama di atas dibatalkan pemegang baru (repro §11 E1)', 'uji-v6-alih-batal', acara('terkunci', P1, HA), False),
    ('★B12', 'ambil alih: pembatalan HP lama (jam batal sendiri) di atas dibatalkan pemegang baru', 'uji-v6-alih-batal', acara('membatalkan', P1, HA, dibatalkanPada=T1), False),
    ('★B13', 'ambil alih: pembatalan HP lama di atas berjalan pemegang baru', 'uji-v6-alih', acara('membatalkan', P1, HA, dibatalkanPada=T1), False),
    ('★B14', 'ambil alih lama di atas ambil alih yang lebih baru', 'uji-v6-alih', alih('berjalan', P1, HA, MB, X0), False),
    ('★B15', 'ganti pemegang tanpa ambil alih', 'uji-v6-berjalan', acara('berjalan', P1, MB), False),
    ('★B16', 'mundur: selesai → terkunci', 'uji-v6-selesai', acara('terkunci', P1, MB), False),
    ('★B17', 'mundur: selesai → membatalkan', 'uji-v6-selesai', acara('membatalkan', P1, MB, dibatalkanPada=T1), False),
    ('★B18', 'mundur: dibatalkan → terkunci', 'uji-v6-dibatalkan', acara('terkunci', P1, HA, dibatalkanPada=T1), False),
    ('★B19', 'mundur: dibatalkan → berjalan', 'uji-v6-dibatalkan', acara('berjalan', P1, HA, dibatalkanPada=T1), False),
    ('★B20', 'mundur: terkunci → berjalan', 'uji-v6-terkunci', acara('berjalan', P1, HA), False),
    ('★B21', 'mundur: membatalkan → terkunci', 'uji-v6-membatalkan', acara('terkunci', P1, HA, dibatalkanPada=T1), False),
    ('★B22', 'mundur: membatalkan → berjalan', 'uji-v6-membatalkan', acara('berjalan', P1, HA, dibatalkanPada=T1), False),
    ('★B23', 'tahun yang selesai dibuka lagi dengan percobaan baru', 'uji-v6-selesai', acara('berjalan', P2, MB), False),
    ('★B24', 'mulai di atas percobaan yang masih terkunci', 'uji-v6-terkunci', acara('berjalan', P2, MB), False),
    ('★B25', 'jam mulai bukan bentuk toISOString', 'uji-v6-dibatalkan', acara('berjalan', '2027-01-06', MB), False),
    ('★B26', 'status asing', 'uji-v6-berjalan', acara('ditutup', P1, HA), False),
    ('★A16', 'kirim ulang IDENTIK di atas selesai (SDK mengulang mutasi yang jawabannya hilang)', 'uji-v6-selesai', acara('selesai', P1, MB), True),
    ('★A17', 'kirim ulang IDENTIK di atas dibatalkan', 'uji-v6-dibatalkan', acara('dibatalkan', P1, HA, dibatalkanPada=T1), True),
    ('V1', 'BATAS: pembatalan HP lama dengan jam batal SAMA di atas dibatalkan pemegang baru — lolos, status kembali membatalkan',
     alih('dibatalkan', P1, MB, HA, X1, dibatalkanPada=T1), acara('membatalkan', P1, HA, dibatalkanPada=T1), True),
]


def periksa_buku(rules, B):
    """9 · berita acara tutup buku hanya maju (v6)."""
    cacat = []; b = B.get('tutupBukuAcara', '')
    rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    # v7 (sanggahan rules 7 Okt): create = bentuk & jam mulai, update = v6 + pintu tertutup untuk selesai / dibatalkan, delete = hanya dibatalkan
    for op, wajib in [('read', 'if owner()')] + ([(o, BUKU_V7[o]) for o in ('create', 'update', 'delete')] if BENTUK_V7 else []):
        if [rata(x) for x in allow(b, op)] != [wajib]: cacat.append('tutupBukuAcara: allow %s bukan "%s" (v6: berita acara hanya maju; v7: mengikat pintu tutup buku): %s' % (op, wajib, [rata(x) for x in allow(b, op)]))
    F = fungsi_rules(tanpa_komentar(rules))
    for n in FUNGSI_BUKU:
        if re.search(r'get\(|exists\(', re.sub(r"\.get\('", '', F.get(n, ''))): cacat.append('tutupBukuAcara: fungsi %s membaca dokumen lain (access call) — v6 tanpa get()' % n)
    nilai0, alasan = model_buku(rules)
    if not nilai0: return cacat + ['tutupBukuAcara: model tidak bisa dibuat — ' + alasan]
    # update = tulisUlangSama() (isi baru == isi lama) || ubahBukuSah — tulis-ulang identik dinilai hanya kalau ada di allow update
    ulang = any('tulisUlangSama()' in rata(x) for x in allow(b, 'update'))
    if not any('ubahBukuSah(request.resource.data, resource.data)' in rata(x) for x in allow(b, 'update')): cacat.append('tutupBukuAcara: update tanpa ubahBukuSah (v6: berita acara hanya maju)')
    nilai = lambda baru, lama: (ulang and baru == lama) or nilai0(baru, lama)
    for no, nama, lama, baru, boleh in KASUS_BUKU:
        if nilai(baru, DOK_BUKU[lama] if isinstance(lama, str) else lama) != boleh:
            cacat.append('tutupBukuAcara (model) %s %s → %s, wajib %s' % (no, nama, 'BOLEH' if not boleh else 'DITOLAK', 'BOLEH' if boleh else 'DITOLAK'))
    # v7: penafsir rules mini (dipakai model pintu & uji_tutup_buku_2027) wajib SEPAKAT dengan model ini di semua kasus — silang dua penilai
    try:
        RM = rules_mini.Rules(rules)
        for no, nama, lama, baru, boleh in KASUS_BUKU:
            h = RM.nilai('update', 'tutupBukuAcara', '1990', auth={'uid': 'uid-uji', 'email': EMAIL_OWNER}, data=baru, sebelum={'tutupBukuAcara/1990': DOK_BUKU[lama] if isinstance(lama, str) else lama})
            if h.boleh != boleh: cacat.append('penafsir rules mini ≠ model v6 di %s %s (%s)' % (no, nama, h.galat or ('LOLOS' if h.boleh else 'DITOLAK')))
    except Exception as e: cacat.append('penafsir rules mini gagal mengurai rules: %s' % e)
    return cacat


V6_TEKS = None   # kontrol: pengganti isi firestore.rules.v6
BANDING_V6 = True   # kontrol lama (sebelum v7) mematikannya supaya pemeriksa khususnya sendiri yang wajib berbunyi
BENTUK_V7 = True   # kontrol 'model:' mematikan pemeriksa BENTUK v7 (persetujuan, fotoBon, pintu) → yang wajib berbunyi = model penafsir (rules_mini)
UKB_WAJIB = ("return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer']) && (!request.resource.data.keys().hasAny(['capServer']) "
             "|| request.resource.data.capServer == request.time);")
NISAN_WAJIB = {'get': 'if owner()', 'list': 'if owner()', 'create': 'if owner() && request.resource.data.capServer == request.time',
               'update': 'if owner() && request.resource.data.capServer == request.time', 'delete': 'if owner()'}
# v7 (b) persetujuan nego staf — sama dengan akses.js BUAT_STAF / BACA_STAF (dijaga juga oleh §5)
SETUJU_WAJIB = {'get': "if owner() || staf(['ben', 'karyawan'])", 'list': "if owner() || staf(['ben', 'karyawan'])", 'create': "if owner() || stafMintaNego(['ben', 'karyawan'])",
                'update': 'if owner()', 'delete': 'if owner()'}
MINTA_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'nego' && d.get('status', '') == 'menunggu' "
               "&& d.get('negoUid', '') == request.auth.uid && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);")
# v7 (c) foto bon — tanpa update
FOTO_WAJIB = {'get': 'if owner()', 'list': 'if owner()', 'delete': 'if owner()', 'update': None,
              'create': ("if owner() && request.resource.data.get('id', '') == id && request.resource.data.get('idBon', 0) is string && request.resource.data.idBon.size() > 0 "
                         "&& request.resource.data.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp'] && request.resource.data.get('base64', 0) is string "
                         "&& request.resource.data.base64.size() > 0 && request.resource.data.base64.size() <= 960000")}
# v7 (e) pintu tutup buku — badan fungsi PERSIS (tanpa komentar, spasi dirapatkan). Sanggahan rules 7 Okt: salinan arsip terikat ke aslinya (hapus: isi =
# salinan sesudah batch; tulis salinan bulan terkunci = catatan asli sebelum batch), saldo pembuka hanya di koleksi pembuka, berita acara dibaca SEBELUM batch
# (get) & hanya tahun lalu, berita acara baru berbentuk + berjam mulai jujur, selesai / dibatalkan hanya dengan pintu tertutup, titik kas 31 Des / titikSebelum
_KOL_PEMBUKA = "['batchMasuk', 'piutangMutasi', 'kasbonMutasi', 'produksiKemasan', 'stokBahanKemasan', 'stokBahanLiteran', 'utangPemasokMutasi', 'utangOwnerMutasi', 'amplopLaba', 'modalOwner']"
_KOL_ARSIP = ("['penjualan', 'batchMasuk', 'produksiKemasan', 'retur', 'pengeluaranHarian', 'setoranKas', 'penyesuaianKemasan', 'amplopLaba', 'modalOwner', "
              "'utangPemasokMutasi', 'utangOwnerMutasi', 'stokBahanKemasan', 'stokBahanLiteran', 'piutangMutasi', 'kasbonMutasi', 'penyesuaianStok', 'tutupHari', 'biayaBulanan']")
_KOL_ARSIP_BEBAS = "['karantina', 'pesanan', 'tembusanStok']"
PINTU_FUNGSI = {
    'pintuTahun': ("let p = getAfter(/databases/$(database)/documents/pengaturan/pintuBuku); return p != null && p.data.get('status', '') == 'berjalan' "
                   "&& p.data.get('tahun', '') is number && p.data.get('sampai', null) is timestamp && request.time < p.data.sampai ? int(p.data.tahun) : 0;"),
    'kolPembuka': "return kol in " + _KOL_PEMBUKA + ";",
    'kolArsip': "return kol in " + _KOL_ARSIP + ";",
    'salinanArsip': ("return a != null && a.data.get('tahun', 0) == y && a.data.get('koleksi', '') == kol && a.data.get('idAsli', '') == id "
                     "&& isi.diff(a.data.get('dok', {})).affectedKeys().hasOnly(['capServer']);"),
    'pulihArsip': "return salinanArsip(get(/databases/$(database)/documents/arsipTahun/$(string(y) + '|' + kol + '|' + id)), y, kol, id, request.resource.data);",
    'pintuTulis': ("let y = pintuTahun(); let d = request.resource.data; return y > 0 && b <= y * 12 + 12 && ((kolPembuka(kol) && d.get('tutupBuku', false) == true "
                   "&& d.get('tahunDari', 0) == y) || pulihArsip(kol, id, y));"),
    'pintuHapus': ("let y = pintuTahun(); return y > 0 && b <= y * 12 + 12 && ((kolPembuka(kol) && resource.data.get('tutupBuku', false) == true && resource.data.get('tahunDari', 0) == y) "
                   "|| salinanArsip(getAfter(/databases/$(database)/documents/arsipTahun/$(string(y) + '|' + kol + '|' + id)), y, kol, id, resource.data));"),
    'titikSebelum': ("let s = get(/databases/$(database)/documents/tutupBukuAcara/$(string(y))).data.get('titikSebelum', null); return s is map "
                     "&& d.get('tanggal', '') == s.get('tanggal', null) && d.get('laci', null) == s.get('laci', null) && d.get('brankas', null) == s.get('brankas', null) "
                     "&& d.get('rekening', null) == s.get('rekening', null) && d.get('amplop', null) == s.get('amplop', null);"),
    'pintuTitik': ("let y = pintuTahun(); let d = request.resource.data; return y > 0 && bulanDok(d, 'tanggal') <= y * 12 + 12 "
                   "&& (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));"),
    'pintuSah': ("let d = request.resource.data; let y = d.get('tahun', 0); let a = get(/databases/$(database)/documents/tutupBukuAcara/$(string(y))); "
                 "return d.get('status', '') == 'berjalan' && y is int && y == wib().year() - 1 && d.get('sampai', null) is timestamp && d.sampai > request.time "
                 "&& d.sampai <= request.time + duration.value(72, 'h') && a != null && a.data.get('tahun', 0) == y && a.data.get('status', '') in ['berjalan', 'terkunci', 'membatalkan'] "
                 "&& a.data.get('paraf', {}).get('pada', '') >= string(y) + '-12-31T17:00:00.000Z';"),
    'pintuMati': ("return p == null || p.data.get('status', '') != 'berjalan' || p.data.get('tahun', 0) != y || !(p.data.get('sampai', null) is timestamp) "
                  "|| !(request.time < p.data.sampai);"),
    'acaraTutupPintu': ("return !(b.get('status', '') in ['selesai', 'dibatalkan']) || pintuMati(getAfter(/databases/$(database)/documents/pengaturan/pintuBuku), b.get('tahun', 0));"),
    'duaDigit': "return n < 10 ? '0' + string(n) : string(n);",
    'hariUtc': "return string(t.year()) + '-' + duaDigit(t.month()) + '-' + duaDigit(t.day());",
    'acaraBaru': ("let d = request.resource.data; let p = d.get('paraf', {}).get('pada', ''); return d.get('tahun', '') is int && id == string(d.tahun) && d.tahun < wib().year() "
                  "&& d.get('mode', '') == 'sungguhan' && d.get('status', '') in ['berjalan', 'terkunci'] && p is string "
                  "&& p.matches('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{3}Z') "
                  "&& p[0:10] in [hariUtc(request.time - duration.value(1, 'd')), hariUtc(request.time), hariUtc(request.time + duration.value(1, 'd'))];"),
    'bulanArsip': "return kol == 'utangPemasokMutasi' ? bulanUP(dok) : bulanDok(dok, kol == 'biayaBulanan' ? 'bulan' : 'tanggal');",
    'salinanAsli': ("let asli = get(/databases/$(database)/documents/$(d.koleksi)/$(d.idAsli)); return asli != null && asli.data.diff(d.dok).affectedKeys().hasOnly(['capServer']);"),
    'arsipSah': ("let d = request.resource.data; return d.get('tahun', '') is int && d.get('idAsli', '') is string && d.get('dok', null) is map "
                 "&& id == string(d.tahun) + '|' + d.get('koleksi', '') + '|' + d.idAsli && (d.koleksi in " + _KOL_ARSIP_BEBAS + " || (kolArsip(d.koleksi) "
                 "&& (bolehBulan(bulanArsip(d.koleksi, d.dok)) || salinanAsli(d))));"),
}
PEMANGGIL_PINTU = {'pintuTahun': {'pintuTulis', 'pintuHapus', 'pintuTitik'}, 'kolPembuka': {'pintuTulis', 'pintuHapus'}, 'kolArsip': {'arsipSah'},
                   'salinanArsip': {'pulihArsip', 'pintuHapus'}, 'pulihArsip': {'pintuTulis'}, 'pintuTulis': set(), 'pintuHapus': set(), 'titikSebelum': {'pintuTitik'},
                   'pintuTitik': set(), 'pintuSah': set(), 'pintuMati': {'acaraTutupPintu'}, 'acaraTutupPintu': set(), 'duaDigit': {'hariUtc'}, 'hariUtc': {'acaraBaru'},
                   'acaraBaru': set(), 'bulanArsip': {'arsipSah'}, 'salinanAsli': {'arsipSah'}, 'arsipSah': set()}
ATUR_WAJIB = "if owner() && (id != 'titikKas' || tglBaru('tanggal') || pintuTitik()) && (id != 'pintuBuku' || request.resource.data.get('status', '') == 'tutup' || pintuSah())"
# blok yang mengikat pintu ke ritual (sanggahan rules 7 Okt) — v6 di ke_v6()
BUKU_V7 = {'create': 'if owner() && acaraBaru(id)', 'update': 'if owner() && (tulisUlangSama() || (ubahBukuSah(request.resource.data, resource.data) && acaraTutupPintu(request.resource.data)))',
           'delete': "if owner() && resource.data.get('status', '') == 'dibatalkan'"}
ARSIP_V7 = {'get': 'if owner()', 'list': 'if owner()', 'create': 'if owner() && arsipSah(id)', 'update': 'if owner() && arsipSah(id)', 'delete': 'if owner()'}
TEKS_BEKU = None; TEKS_PEMBANTU = None   # kontrol: pengganti isi beku.js / pembantu.js (mesin dibaca saja)
DOK_V7_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v7.md


def koleksi_arsip(semua=False):
    """Koleksi bertanggal yang DIARSIP tutup buku = tbDaftarKoleksi (mesin beku, dibaca saja) ∩ KP_KOLEKSI — urutan mesin. semua=True: seluruh tbDaftarKoleksi."""
    beku = TEKS_BEKU if TEKS_BEKU is not None else baca('baru/js/mesin/beku.js'); pb = TEKS_PEMBANTU if TEKS_PEMBANTU is not None else baca('baru/js/mesin/pembantu.js')
    m = re.search(r'function tbDaftarKoleksi\(tahun\) \{(.*?)\n  \}', beku, re.S)
    konst = dict(re.findall(r"const (KOLEKSI_\w+) = '(\w+)';", pb)); KOL, _ = kp_js()
    if not m: return None
    return [konst.get(k, '?' + k) for k in re.findall(r'\{ koleksi: (KOLEKSI_\w+),', m.group(1)) if semua or konst.get(k) in KOL]


def ekspr_bulan(n, sisi, KOL):
    return ('bulanUP(%s)' % sisi) if n == 'utangPemasokMutasi' else "bulanDok(%s, '%s')" % (sisi, KOL[n])


def ekspr_lama(n, KOL): return 'upLama()' if n == 'utangPemasokMutasi' else "tglLama('%s')" % KOL[n]


def suku_pintu(n, KOL): return "(owner() && pintuTulis('%s', id, %s))" % (n, ekspr_bulan(n, 'request.resource.data', KOL))


def hapus_pintu(n, KOL): return "if owner() && (%s || pintuHapus('%s', id, %s))" % (ekspr_lama(n, KOL), n, ekspr_bulan(n, 'resource.data', KOL))


# ---- v8 (B1, owner 16 Nov 2026): v7 + PERSIS tiga ubahan ----
ATURAN_STAF_V8 = ['hargaTingkat', 'produkArsip']   # (v8-1) harga pelanggan usaha · (v8-2) arsip produk — ditambahkan DI BELAKANG daftar v7
USUL_SUKU = " || stafUsulHarga(['ben', 'karyawan'])"
SETUJU_CREATE_V8 = "if owner() || stafMintaNego(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan'])"
USUL_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'hargaPelanggan' && d.get('status', '') == 'menunggu' "
              "&& d.get('usulUid', '') == request.auth.uid && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);")
V7_TEKS = None   # kontrol: pengganti isi firestore.rules.v7
BANDING_V7 = True   # kontrol: pembanding "sisanya = firestore.rules.v7" ikut saklar pembanding v6 (pemeriksa khusus yang wajib berbunyi)


def ke_v7(R):
    """v8 → v7: cabut PERSIS tiga ubahan v8 (tiap ganti wajib kena tepat sekali). R = rules tanpa komentar. Kembali (teks, cacat)."""
    cacat = []

    def ganti(t, lama, baru, di):
        k = t.count(lama)
        if k != 1: cacat.append('v8 ≠ v7 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (di, lama[:110], k)); return t
        return t.replace(lama, baru)
    R = ganti(R, "'perangkat', " + ', '.join("'%s'" % x for x in ATURAN_STAF_V8) + "] && staf(['ben', 'karyawan'])", "'perangkat'] && staf(['ben', 'karyawan'])", 'aturanToko read (v8-1/2)')
    R = ganti(R, "allow create: if owner() || stafMintaNego(['ben', 'karyawan'])" + USUL_SUKU + ";", "allow create: if owner() || stafMintaNego(['ben', 'karyawan']);", 'persetujuan create (v8-3)')
    R2 = buang_fungsi(R, 'stafUsulHarga')
    if R2 == R: cacat.append('fungsi v8 stafUsulHarga() tidak ada')
    return R2, cacat


def periksa_v8(rules, r7, c8):
    """12 · v8: bentuk persis tiga ubahan + sisanya = firestore.rules.v7 + model kasus ★H (v8 & v7, beda wajib = BEDA_V7)."""
    cacat = list(c8); R = rules; B = blok_rules(R); F = fungsi_rules(R); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    if BENTUK_V7 and rata(F.get('stafUsulHarga', '')) != USUL_WAJIB: cacat.append('stafUsulHarga() bukan "stafBuat + tindakan hargaPelanggan + status menunggu + usulUid = uid penulis + tanpa kolom keputusan": ' + rata(F.get('stafUsulHarga', '(tidak ada)')))
    xs = [rata(x) for x in allow(B.get('persetujuan', ''), 'create')]
    if BENTUK_V7 and xs != [SETUJU_CREATE_V8]: cacat.append('persetujuan: allow create bukan "%s" (v8: staf minta nego ATAU usul harga, atas nama sendiri): %s' % (SETUJU_CREATE_V8, xs))
    for n, b in B.items():
        if 'stafUsulHarga' in b and n != 'persetujuan': cacat.append(n + ': stafUsulHarga() dipakai di luar persetujuan')
    for n, badan in F.items():
        if n != 'stafUsulHarga' and 'stafUsulHarga' in badan: cacat.append('stafUsulHarga() dipanggil dari fungsi ' + n)
    v7 = V7_TEKS if V7_TEKS is not None else baca('firestore.rules.v7')
    a, b = rata(r7), rata(tanpa_komentar(v7))
    if BANDING_V7 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v8 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v7 — dekat "…%s…" (v7: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    # docs/uji-rules-v8.md memuat PERSIS kasus ★H model ini; bagian "Wajib owner" = WAJIB_V8
    dok = DOK_V8_TEKS if DOK_V8_TEKS is not None else (baca('docs/uji-rules-v8.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v8.md')) else '')
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★H\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V8)
    if di_dok != di_model: cacat.append('docs/uji-rules-v8.md tidak sama dengan kasus model v8 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★H\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V8: cacat.append('docs/uji-rules-v8.md bagian "Wajib owner" bukan WAJIB_V8 — berkas: %s · model: %s' % (wajib, WAJIB_V8))
    # MODEL: v8 = kolom wajib; v7 = sama kecuali BEDA_V7 (yang dibuka v8)
    try: M8 = rules_mini.Rules(R); M7 = rules_mini.Rules(tanpa_komentar(v7))
    except Exception as e: return cacat + ['model v8: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V8:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M8.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v8 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v8 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h7 = M7.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap7 = (not boleh) if no in BEDA_V7 else boleh
        if h7.boleh != harap7: cacat.append('model v8 %s atas firestore.rules.v7 → %s, harap %s (%s)' % (no, 'LOLOS' if h7.boleh else 'DITOLAK', 'LOLOS' if harap7 else 'DITOLAK', 'ubahan v8' if no in BEDA_V7 else 'wajib sama dengan v7'))
    return cacat


# ---- v9 (B2, owner 17 Nov 2026): v8 + PERSIS satu ubahan ----
KREDIT_SUKU = " || stafMintaKredit(['ben'])"
SETUJU_CREATE_V9 = SETUJU_CREATE_V8 + KREDIT_SUKU
MINTA_KREDIT_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'kredit' && d.get('status', '') == 'menunggu' "
                      "&& d.get('mintaUid', '') == request.auth.uid && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);")
V8_TEKS = None   # kontrol: pengganti isi firestore.rules.v8
BANDING_V8 = True


def ke_v8(R):
    """v9 → v8: cabut PERSIS satu ubahan v9 (wajib kena tepat sekali). R = rules tanpa komentar. Kembali (teks, cacat)."""
    cacat = []
    lama = "allow create: if owner() || stafMintaNego(['ben', 'karyawan'])" + USUL_SUKU + KREDIT_SUKU + ";"
    k = R.count(lama)
    if k != 1: cacat.append('v9 ≠ v8 + ubahan yang tercatat: persetujuan create (v9-1) — %r ditemukan %d× (wajib 1×)' % (lama[:110], k))
    else: R = R.replace(lama, "allow create: if owner() || stafMintaNego(['ben', 'karyawan'])" + USUL_SUKU + ";")
    R2 = buang_fungsi(R, 'stafMintaKredit')
    if R2 == R: cacat.append('fungsi v9 stafMintaKredit() tidak ada')
    return R2, cacat


def periksa_v9(rules, r8, c9):
    """13 · v9: bentuk persis satu ubahan + sisanya = firestore.rules.v8 + model kasus ★J (v9 & v8, beda wajib = BEDA_V8)."""
    cacat = list(c9); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    if BENTUK_V7 and rata(F.get('stafMintaKredit', '')) != MINTA_KREDIT_WAJIB: cacat.append('stafMintaKredit() bukan "stafBuat + tindakan kredit + status menunggu + mintaUid = uid penulis + tanpa kolom keputusan": ' + rata(F.get('stafMintaKredit', '(tidak ada)')))
    xs = [rata(x) for x in allow(B.get('persetujuan', ''), 'create')]
    if BENTUK_V7 and xs != [SETUJU_CREATE_V9]: cacat.append('persetujuan: allow create bukan "%s" (v9: + minta persetujuan bon, ben saja): %s' % (SETUJU_CREATE_V9, xs))
    for n, b in B.items():
        if 'stafMintaKredit' in b and n != 'persetujuan': cacat.append(n + ': stafMintaKredit() dipakai di luar persetujuan')
    for n, badan in F.items():
        if n != 'stafMintaKredit' and 'stafMintaKredit' in badan: cacat.append('stafMintaKredit() dipanggil dari fungsi ' + n)
    v8 = V8_TEKS if V8_TEKS is not None else baca('firestore.rules.v8')
    a, b = rata(r8), rata(tanpa_komentar(v8))
    if BANDING_V8 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v9 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v8 — dekat "…%s…" (v8: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V9_TEKS if DOK_V9_TEKS is not None else (baca('docs/uji-rules-v9.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v9.md')) else '')
    # nomor kasus v9 TIDAK boleh sama dengan nomor v7/v8: penguji emulator membaca kolom Wajib docs/uji-rules-v7.md per nomor (★K3 v7 = kasir, bukan v9)
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    bentrok = sorted(set(k[0] for k in KASUS_V9) & (set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V8) | set(k[0] for k in KASUS_V7)))
    if bentrok: cacat.append('nomor kasus v9 bertabrakan dengan v7/v8 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★J\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V9)
    if di_dok != di_model: cacat.append('docs/uji-rules-v9.md tidak sama dengan kasus model v9 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★J\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V9: cacat.append('docs/uji-rules-v9.md bagian "Wajib owner" bukan WAJIB_V9 — berkas: %s · model: %s' % (wajib, WAJIB_V9))
    try: M9 = rules_mini.Rules(rules); M8 = rules_mini.Rules(tanpa_komentar(v8))
    except Exception as e: return cacat + ['model v9: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V9:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M9.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v9 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v9 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h8 = M8.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap8 = (not boleh) if no in BEDA_V8 else boleh
        if h8.boleh != harap8: cacat.append('model v9 %s atas firestore.rules.v8 → %s, harap %s (%s)' % (no, 'LOLOS' if h8.boleh else 'DITOLAK', 'LOLOS' if harap8 else 'DITOLAK', 'ubahan v9' if no in BEDA_V8 else 'wajib sama dengan v8'))
    return cacat


# ---- v10 (B3, owner 18 Nov 2026): v9 + PERSIS dua blok baru (suratJalan, buktiTerima) & tiga fungsinya ----
BLOK_V10 = {
    'suratJalan': {'read': "if owner() || staf(['ben', 'karyawan'])", 'create': "if owner() || stafBuatSJ(['ben'])", 'update': "if owner() || stafTandaiSJ(['ben', 'karyawan'])", 'delete': 'if owner()'},
    'buktiTerima': {'read': "if owner() || staf(['ben', 'karyawan'])", 'create': "if (owner() || stafBuat(['ben', 'karyawan'])) && buktiSah(id)", 'delete': 'if owner()'},
}
FUNGSI_V10 = ['stafBuatSJ', 'stafTandaiSJ', 'buktiSah']
SJ_BUKAN_BARU = ['penerima', 'diterimaPada', 'diterimaTanggal', 'diterimaJam', 'buktiTtd', 'buktiFoto', 'uangDiterima', 'pelunasanId', 'alasanGagal', 'batalPada', 'alasanBatal']
SJ_TANDAI = ['status', 'riwayatStatus', 'penerima', 'diterimaPada', 'diterimaTanggal', 'diterimaJam', 'catatanTerima', 'buktiTtd', 'buktiFoto', 'uangDiterima', 'caraUang', 'pelunasanId',
             'alasanGagal', 'ditandaiOleh', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada']
q = lambda xs: '[' + ', '.join("'%s'" % x for x in xs) + ']'
BUAT_SJ_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('status', '') == 'berangkat' && !d.keys().hasAny(" + q(SJ_BUKAN_BARU) + ");")
TANDAI_SJ_WAJIB = ("return masuk() && aktifDengan(akun(), peranBoleh) && request.resource.data.diubahOlehUid == request.auth.uid && resource.data.get('status', '') == 'berangkat' "
                   "&& request.resource.data.get('status', '') in ['diterima', 'gagal'] && request.resource.data.diff(resource.data).affectedKeys().hasOnly(" + q(SJ_TANDAI) + ");")
BUKTI_WAJIB = ("let d = request.resource.data; return d.get('id', '') == id && d.get('idSJ', 0) is string && d.idSJ.size() > 0 && d.get('jenisBukti', '') in ['ttd', 'foto'] "
               "&& d.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp'] && d.get('base64', 0) is string && d.base64.size() > 0 && d.base64.size() <= 960000;")
V9_TEKS = None   # kontrol: pengganti isi firestore.rules.v9
BANDING_V9 = True


def ke_v9(R):
    """v10 → v9: cabut PERSIS dua blok baru & tiga fungsi v10 (tiap blok / fungsi wajib ada tepat sekali). R = rules tanpa komentar. Kembali (teks, cacat)."""
    cacat = []
    for n in BLOK_V10:
        ms = list(re.finditer(r'\n    match /' + n + r'/\{\w+\} \{\n.*?\n    \}', R, re.S))
        if len(ms) != 1: cacat.append('blok v10 %s ditemukan %d× (wajib 1×)' % (n, len(ms))); continue
        R = R[:ms[0].start()] + R[ms[0].end():]
    for f in FUNGSI_V10:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v10 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v10(rules, r9, c10, akses_js):
    """14 · v10: bentuk persis dua blok & tiga fungsi + sisanya = firestore.rules.v9 + model kasus ★L (v10 & v9, beda wajib = BEDA_V9)."""
    cacat = list(c10); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for n, ops in BLOK_V10.items():
        for op in OPERASI:
            xs = [rata(x) for x in allow(B.get(n, ''), op)]
            w = ops.get(op) or (ops.get('read') if op in ('get', 'list') else None)
            if (xs != [w]) if w else xs: cacat.append('%s: allow %s bukan "%s" (v10): %s' % (n, op, w or '(tidak ada)', xs))
    for f, w in (('stafBuatSJ', BUAT_SJ_WAJIB), ('stafTandaiSJ', TANDAI_SJ_WAJIB), ('buktiSah', BUKTI_WAJIB)):
        if rata(F.get(f, '')) != w: cacat.append('%s() bukan bentuk v10 yang tercatat: %s' % (f, rata(F.get(f, '(tidak ada)'))))
    for n, b in B.items():
        for f, boleh in (('stafBuatSJ', 'suratJalan'), ('stafTandaiSJ', 'suratJalan'), ('buktiSah', 'buktiTerima')):
            if f in b and n != boleh: cacat.append(n + ': ' + f + '() dipakai di luar ' + boleh)
    for n, badan in F.items():
        for f in FUNGSI_V10:
            if n != f and f + '(' in badan: cacat.append(f + '() dipanggil dari fungsi ' + n)
    # kolom yang boleh ditandai pengantar = akses.js KOLOM_TANDAI_SJ + atribusi ubah; kolom terlarang di surat jalan baru = akses.js KOLOM_BUKAN_SJ_BARU
    kt = daftar_js(akses_js, 'KOLOM_TANDAI_SJ') or []; ka = daftar_js(akses_js, 'KOLOM_ATRIBUSI_UBAH') or []; kb = daftar_js(akses_js, 'KOLOM_BUKAN_SJ_BARU') or []
    if kt + ka != SJ_TANDAI: cacat.append('kolom tandai surat jalan beda: akses.js %s vs rules v10 %s' % (kt + ka, SJ_TANDAI))
    if kb != SJ_BUKAN_BARU: cacat.append('kolom terlarang surat jalan baru beda: akses.js %s vs rules v10 %s' % (kb, SJ_BUKAN_BARU))
    v9 = V9_TEKS if V9_TEKS is not None else baca('firestore.rules.v9')
    a, b = rata(r9), rata(tanpa_komentar(v9))
    if BANDING_V9 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v10 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v9 — dekat "…%s…" (v9: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V10_TEKS if DOK_V10_TEKS is not None else (baca('docs/uji-rules-v10.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v10.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    bentrok = sorted(set(k[0] for k in KASUS_V10) & (set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V9) | set(k[0] for k in KASUS_V8) | set(k[0] for k in KASUS_V7)))
    if bentrok: cacat.append('nomor kasus v10 bertabrakan dengan v7/v8/v9 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★L\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V10)
    if di_dok != di_model: cacat.append('docs/uji-rules-v10.md tidak sama dengan kasus model v10 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★L\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V10: cacat.append('docs/uji-rules-v10.md bagian "Wajib owner" bukan WAJIB_V10 — berkas: %s · model: %s' % (wajib, WAJIB_V10))
    try: M10 = rules_mini.Rules(rules); M9 = rules_mini.Rules(tanpa_komentar(v9))
    except Exception as e: return cacat + ['model v10: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V10:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M10.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v10 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v10 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h9 = M9.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap9 = (not boleh) if no in BEDA_V9 else boleh
        if h9.boleh != harap9: cacat.append('model v10 %s atas firestore.rules.v9 → %s, harap %s (%s)' % (no, 'LOLOS' if h9.boleh else 'DITOLAK', 'LOLOS' if harap9 else 'DITOLAK', 'ubahan v10' if no in BEDA_V9 else 'wajib sama dengan v9'))
    return cacat


# ---- v11 (B4, owner 18 Nov 2026): v10 + PERSIS tiga ubahan (pesanan create & update, blok orderRutin) & tiga fungsinya ----
PESANAN_GANTI_V11 = [("allow create: if owner() || stafBuatPesanan(['ben']);", "allow create: if owner();", 'v11-1 pesanan create'),
                     ("allow update: if owner() || stafUbahPesanan(['ben', 'karyawan']) || stafAturPesanan(['ben']);", "allow update: if owner() || stafUbahPesanan(['ben', 'karyawan']);", 'v11-2 pesanan update')]
BLOK_V11 = {'orderRutin': {'read': "if owner() || staf(['ben', 'karyawan'])", 'create': "if owner() || stafBuat(['ben'])", 'update': "if owner() || stafUbahRutin(['ben'])", 'delete': 'if owner()'}}
FUNGSI_V11 = ['stafBuatPesanan', 'stafAturPesanan', 'stafUbahRutin']
PS_BUKAN_BARU = ['dibatalkan', 'alasanBatal', 'nasibUangMuka']
PS_ATUR = ['status', 'riwayatStatus', 'baris', 'isi', 'noPO', 'tanggalKirim', 'alamat', 'nilaiPerkiraan', 'catatan', 'alasanBatal', 'nasibUangMuka', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada']
RUTIN_UBAH = ['namaPelanggan', 'baris', 'isi', 'alamat', 'noPO', 'catatan', 'ulang', 'hari', 'tanggalBulan', 'mulai', 'aktif', 'lewati', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada']
BUAT_PS_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('status', '') == 'dipesan' && d.get('trxIdJual', null) == null && !d.keys().hasAny(" + q(PS_BUKAN_BARU) + ");")
ATUR_PS_WAJIB = ("return masuk() && aktifDengan(akun(), peranBoleh) && request.resource.data.diubahOlehUid == request.auth.uid && resource.data.get('status', '') in ['dipesan', 'diantar'] "
                 "&& request.resource.data.get('status', '') in ['dipesan', 'diantar', 'batal'] && request.resource.data.diff(resource.data).affectedKeys().hasOnly(" + q(PS_ATUR) + ");")
UBAH_RUTIN_WAJIB = ("return masuk() && aktifDengan(akun(), peranBoleh) && request.resource.data.diubahOlehUid == request.auth.uid "
                    "&& request.resource.data.diff(resource.data).affectedKeys().hasOnly(" + q(RUTIN_UBAH) + ");")
V10_TEKS = None   # kontrol: pengganti isi firestore.rules.v10
BANDING_V10 = True


def ke_v10(R):
    """v11 → v10: cabut PERSIS tiga ubahan v11 (pesanan create & update di blok pesanan — satu kali; blok orderRutin; tiga fungsi). Kembali (teks, cacat)."""
    cacat = []
    for baru, lama, nama in PESANAN_GANTI_V11:
        k = R.count(baru)
        if k != 1: cacat.append('v11 ≠ v10 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (nama, baru[:90], k))
        else: R = R.replace(baru, lama)
    for n in BLOK_V11:
        ms = list(re.finditer(r'\n    match /' + n + r'/\{\w+\} \{\n.*?\n    \}', R, re.S))
        if len(ms) != 1: cacat.append('blok v11 %s ditemukan %d× (wajib 1×)' % (n, len(ms))); continue
        R = R[:ms[0].start()] + R[ms[0].end():]
    for f in FUNGSI_V11:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v11 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v11(rules, r10, c11, akses_js):
    """15 · v11: bentuk persis tiga ubahan & tiga fungsi + sisanya = firestore.rules.v10 + model kasus ★M (v11 & v10, beda wajib = BEDA_V10)."""
    cacat = list(c11); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for n, ops in BLOK_V11.items():
        for op in OPERASI:
            xs = [rata(x) for x in allow(B.get(n, ''), op)]
            w = ops.get(op) or (ops.get('read') if op in ('get', 'list') else None)
            if (xs != [w]) if w else xs: cacat.append('%s: allow %s bukan "%s" (v11): %s' % (n, op, w or '(tidak ada)', xs))
    for op, w in (('create', "if owner() || stafBuatPesanan(['ben'])"), ('update', "if owner() || stafUbahPesanan(['ben', 'karyawan']) || stafAturPesanan(['ben'])")):
        xs = [rata(x) for x in allow(B.get('pesanan', ''), op)]
        if xs != [w]: cacat.append('pesanan: allow %s bukan "%s" (v11): %s' % (op, w, xs))
    for f, w in (('stafBuatPesanan', BUAT_PS_WAJIB), ('stafAturPesanan', ATUR_PS_WAJIB), ('stafUbahRutin', UBAH_RUTIN_WAJIB)):
        if rata(F.get(f, '')) != w: cacat.append('%s() bukan bentuk v11 yang tercatat: %s' % (f, rata(F.get(f, '(tidak ada)'))))
    for n, b in B.items():
        for f, boleh in (('stafBuatPesanan', 'pesanan'), ('stafAturPesanan', 'pesanan'), ('stafUbahRutin', 'orderRutin')):
            if f in b and n != boleh: cacat.append(n + ': ' + f + '() dipakai di luar ' + boleh)
    for n, badan in F.items():
        for f in FUNGSI_V11:
            if n != f and f + '(' in badan: cacat.append(f + '() dipanggil dari fungsi ' + n)
    # kolom = akses.js (penjaga kiriman) = pesanan-logika.js (penyusun) = rules v11
    ka = daftar_js(akses_js, 'KOLOM_ATRIBUSI_UBAH') or []; kp = daftar_js(akses_js, 'KOLOM_ATUR_PESANAN') or []; kr = daftar_js(akses_js, 'KOLOM_UBAH_RUTIN') or []
    kb = daftar_js(akses_js, 'KOLOM_BUKAN_PESANAN_BARU') or []
    if kp + ka != PS_ATUR: cacat.append('kolom ubah pesanan beda: akses.js %s vs rules v11 %s' % (kp + ka, PS_ATUR))
    if kr + ka != RUTIN_UBAH: cacat.append('kolom ubah jadwal rutin beda: akses.js %s vs rules v11 %s' % (kr + ka, RUTIN_UBAH))
    if kb != PS_BUKAN_BARU: cacat.append('kolom terlarang pesanan baru beda: akses.js %s vs rules v11 %s' % (kb, PS_BUKAN_BARU))
    po = baca('baru/js/layar/pesanan-logika.js')
    if (daftar_js(po, 'PO_KOLOM_ATUR') or []) != kp: cacat.append('pesanan-logika.js PO_KOLOM_ATUR beda dengan akses.js KOLOM_ATUR_PESANAN')
    if (daftar_js(po, 'PO_KOLOM_RUTIN') or []) != kr: cacat.append('pesanan-logika.js PO_KOLOM_RUTIN beda dengan akses.js KOLOM_UBAH_RUTIN')
    v10 = V10_TEKS if V10_TEKS is not None else baca('firestore.rules.v10')
    a, b = rata(r10), rata(tanpa_komentar(v10))
    if BANDING_V10 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v11 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v10 — dekat "…%s…" (v10: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V11_TEKS if DOK_V11_TEKS is not None else (baca('docs/uji-rules-v11.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v11.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    bentrok = sorted(set(k[0] for k in KASUS_V11) & (set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V10) | set(k[0] for k in KASUS_V9) | set(k[0] for k in KASUS_V8) | set(k[0] for k in KASUS_V7)))
    if bentrok: cacat.append('nomor kasus v11 bertabrakan dengan v7–v10 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★M\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V11)
    if di_dok != di_model: cacat.append('docs/uji-rules-v11.md tidak sama dengan kasus model v11 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★M\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V11: cacat.append('docs/uji-rules-v11.md bagian "Wajib owner" bukan WAJIB_V11 — berkas: %s · model: %s' % (wajib, WAJIB_V11))
    try: M11 = rules_mini.Rules(rules); M10 = rules_mini.Rules(tanpa_komentar(v10))
    except Exception as e: return cacat + ['model v11: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V11:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M11.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v11 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v11 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h10 = M10.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap10 = (not boleh) if no in BEDA_V10 else boleh
        if h10.boleh != harap10: cacat.append('model v11 %s atas firestore.rules.v10 → %s, harap %s (%s)' % (no, 'LOLOS' if h10.boleh else 'DITOLAK', 'LOLOS' if harap10 else 'DITOLAK', 'ubahan v11' if no in BEDA_V10 else 'wajib sama dengan v10'))
    return cacat


# ---- v12 (paket S2b tanda kenal, owner 19 Nov 2026): v11 + PERSIS satu blok baru (tandaKenal), tanpa fungsi baru ----
BLOK_V12 = {'tandaKenal': {'read': "if owner() || staf(['ben', 'karyawan'])", 'create': "if owner() || stafBuat(['ben', 'karyawan'])", 'update': 'if owner()', 'delete': 'if owner()'}}
V11_TEKS = None   # kontrol: pengganti isi firestore.rules.v11
BANDING_V11 = True


def ke_v11(R):
    """v12 → v11: cabut PERSIS satu blok v12 (tandaKenal). Kembali (teks, cacat)."""
    cacat = []
    for n in BLOK_V12:
        ms = list(re.finditer(r'\n    match /' + n + r'/\{\w+\} \{\n.*?\n    \}', R, re.S))
        if len(ms) != 1: cacat.append('blok v12 %s ditemukan %d× (wajib 1×)' % (n, len(ms))); continue
        R = R[:ms[0].start()] + R[ms[0].end():]
    return R, cacat


def periksa_v12(rules, r11, c12):
    """16 · v12: bentuk persis satu blok baru + sisanya = firestore.rules.v11 + model kasus ★S (v12 & v11, beda wajib = BEDA_V11)."""
    cacat = list(c12); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for n, ops in BLOK_V12.items():
        for op in OPERASI:
            xs = [rata(x) for x in allow(B.get(n, ''), op)]
            w = ops.get(op) or (ops.get('read') if op in ('get', 'list') else None)
            if (xs != [w]) if w else xs: cacat.append('%s: allow %s bukan "%s" (v12): %s' % (n, op, w or '(tidak ada)', xs))
    v11 = V11_TEKS if V11_TEKS is not None else baca('firestore.rules.v11')
    a, b = rata(r11), rata(tanpa_komentar(v11))
    if BANDING_V11 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v12 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v11 — dekat "…%s…" (v11: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    if sorted(F) != sorted(fungsi_rules(tanpa_komentar(v11))): cacat.append('v12 menambah / membuang fungsi (v12 tidak punya fungsi baru)')
    dok = DOK_V12_TEKS if DOK_V12_TEKS is not None else (baca('docs/uji-rules-v12.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v12.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    bentrok = sorted(set(k[0] for k in KASUS_V12) & (set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V11) | set(k[0] for k in KASUS_V10) | set(k[0] for k in KASUS_V9) | set(k[0] for k in KASUS_V8) | set(k[0] for k in KASUS_V7)))
    if bentrok: cacat.append('nomor kasus v12 bertabrakan dengan v7–v11 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★S\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V12)
    if di_dok != di_model: cacat.append('docs/uji-rules-v12.md tidak sama dengan kasus model v12 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★S\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V12: cacat.append('docs/uji-rules-v12.md bagian "Wajib owner" bukan WAJIB_V12 — berkas: %s · model: %s' % (wajib, WAJIB_V12))
    try: M12 = rules_mini.Rules(rules); M11 = rules_mini.Rules(tanpa_komentar(v11))
    except Exception as e: return cacat + ['model v12: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V12:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M12.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v12 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v12 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h11 = M11.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap11 = (not boleh) if no in BEDA_V11 else boleh
        if h11.boleh != harap11: cacat.append('model v12 %s atas firestore.rules.v11 → %s, harap %s (%s)' % (no, 'LOLOS' if h11.boleh else 'DITOLAK', 'LOLOS' if harap11 else 'DITOLAK', 'ubahan v12' if no in BEDA_V11 else 'wajib sama dengan v11'))
    return cacat


# ---- v13 (owner 21 Nov 2026: titipan uang keluar & pesan dari tablet + token notifikasi HP owner): v12 + PERSIS satu ubahan (persetujuan create),
#      dua fungsinya, dan satu blok baru (notifOwner) ----
PERSETUJUAN_GANTI_V13 = [("allow create: if owner() || stafMintaNego(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan']) || stafMintaKredit(['ben']) || stafMintaKeluar(['ben', 'karyawan']) || stafKirimPesan(['ben', 'karyawan']);",
                          "allow create: if owner() || stafMintaNego(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan']) || stafMintaKredit(['ben']);", 'v13-1 persetujuan create')]
BLOK_V13 = {'notifOwner': {'read': 'if owner()', 'create': 'if owner()', 'update': 'if owner()', 'delete': 'if owner()'}}
FUNGSI_V13 = ['stafMintaKeluar', 'stafKirimPesan']
TP_JENIS_V13 = ['toko', 'karyawan', 'kasbon']
KELUAR_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'uangKeluar' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid "
                "&& d.get('jenis', '') in " + q(TP_JENIS_V13) + " && d.get('nominal', 0) is int && d.get('nominal', 0) > 0 "
                "&& !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'koreksiOwner', 'balasan']);")
PESAN_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'pesan' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid "
               "&& d.get('teks', 0) is string && d.teks.size() > 0 && d.teks.size() <= 500 && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'balasan']);")
V12_TEKS = None   # kontrol: pengganti isi firestore.rules.v12
BANDING_V12 = True


def ke_v12(R):
    """v13 → v12: cabut PERSIS ubahan v13 (persetujuan create — satu kali; blok notifOwner; dua fungsi). Kembali (teks, cacat)."""
    cacat = []
    for baru, lama, nama in PERSETUJUAN_GANTI_V13:
        k = R.count(baru)
        if k != 1: cacat.append('v13 ≠ v12 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (nama, baru[:90], k))
        else: R = R.replace(baru, lama)
    for n in BLOK_V13:
        ms = list(re.finditer(r'\n    match /' + n + r'/\{\w+\} \{\n.*?\n    \}', R, re.S))
        if len(ms) != 1: cacat.append('blok v13 %s ditemukan %d× (wajib 1×)' % (n, len(ms))); continue
        R = R[:ms[0].start()] + R[ms[0].end():]
    for f in FUNGSI_V13:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v13 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v13(rules, r12, c13, akses_js):
    """17 · v13: bentuk persis satu ubahan, dua fungsi & satu blok + sisanya = firestore.rules.v12 + model kasus ★U (v13 & v12, beda wajib = BEDA_V12)."""
    cacat = list(c13); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for n, ops in BLOK_V13.items():
        for op in OPERASI:
            xs = [rata(x) for x in allow(B.get(n, ''), op)]
            w = ops.get(op) or (ops.get('read') if op in ('get', 'list') else None)
            if (xs != [w]) if w else xs: cacat.append('%s: allow %s bukan "%s" (v13): %s' % (n, op, w or '(tidak ada)', xs))
    w = "if owner() || stafMintaNego(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan']) || stafMintaKredit(['ben']) || stafMintaKeluar(['ben', 'karyawan']) || stafKirimPesan(['ben', 'karyawan'])"
    xs = [rata(x) for x in allow(B.get('persetujuan', ''), 'create')]
    if xs != [w]: cacat.append('persetujuan: allow create bukan "%s" (v13): %s' % (w, xs))
    for f, wf in (('stafMintaKeluar', KELUAR_WAJIB), ('stafKirimPesan', PESAN_WAJIB)):
        if rata(F.get(f, '')) != wf: cacat.append('%s() bukan bentuk v13 yang tercatat: %s' % (f, rata(F.get(f, '(tidak ada)'))))
    for n, b in B.items():
        for f in FUNGSI_V13:
            if f in b and n != 'persetujuan': cacat.append(n + ': ' + f + '() dipakai di luar persetujuan')
    for n, badan in F.items():
        for f in FUNGSI_V13:
            if n != f and f + '(' in badan: cacat.append(f + '() dipanggil dari fungsi ' + n)
    # bentuk = penjaga kiriman akses.js = penyusun titipan-logika.js = rules v13
    tp = baca('baru/js/layar/titipan-logika.js')
    # v15: kartu tablet + bayar bon pemasok; upah bongkar lahir dari form barang masuk (TP_JENIS_SEMUA) — daftar lengkapnya = akses.js JENIS_TITIPAN (periksa_v15)
    if re.findall(r"\['(\w+)', '[^']+'\]", (re.search(r'export const TP_JENIS = \[(.*?)\];', tp) or re.search('', '')).group(0)) != TP_JENIS_V13 + ['bayarBon']: cacat.append('titipan-logika.js TP_JENIS beda dengan jenis rules v13 + bayarBon (v15) %s' % TP_JENIS_V13)
    if 'pesan: 500' not in tp: cacat.append('titipan-logika.js TP_BATAS.pesan bukan 500 (rules v13: teks pesan ≤ 500)')
    for x in ("d.tindakan === 'uangKeluar'", "JENIS_TITIPAN.indexOf(d.jenis) < 0", "Number.isInteger(n) && n > 0", "'koreksiOwner', 'balasan']",
              "d.tindakan === 'pesan'", "d.teks.length > 500", "String(d.mintaUid || '') !== String(akun.uid || '')"):
        if x not in akses_js: cacat.append('akses.js periksaKiriman tanpa penjaga bentuk v13: ' + x)
    v12 = V12_TEKS if V12_TEKS is not None else baca('firestore.rules.v12')
    a, b = rata(r12), rata(tanpa_komentar(v12))
    if BANDING_V12 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v13 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v12 — dekat "…%s…" (v12: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V13_TEKS if DOK_V13_TEKS is not None else (baca('docs/uji-rules-v13.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v13.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    lama = set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V12 + KASUS_V11 + KASUS_V10 + KASUS_V9 + KASUS_V8 + KASUS_V7)
    bentrok = sorted(set(k[0] for k in KASUS_V13) & lama)
    if bentrok: cacat.append('nomor kasus v13 bertabrakan dengan v7–v12 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★U\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V13)
    if di_dok != di_model: cacat.append('docs/uji-rules-v13.md tidak sama dengan kasus model v13 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★U\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V13: cacat.append('docs/uji-rules-v13.md bagian "Wajib owner" bukan WAJIB_V13 — berkas: %s · model: %s' % (wajib, WAJIB_V13))
    try: M13 = rules_mini.Rules(rules); M12 = rules_mini.Rules(tanpa_komentar(v12))
    except Exception as e: return cacat + ['model v13: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V13:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M13.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v13 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v13 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h12 = M12.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap12 = (not boleh) if no in BEDA_V12 else boleh
        if h12.boleh != harap12: cacat.append('model v13 %s atas firestore.rules.v12 → %s, harap %s (%s)' % (no, 'LOLOS' if h12.boleh else 'DITOLAK', 'LOLOS' if harap12 else 'DITOLAK', 'ubahan v13' if no in BEDA_V12 else 'wajib sama dengan v12'))
    return cacat


# ---- v14 (owner 21 Nov 2026: RINGKAS HARI INI di tablet): v13 + PERSIS dua fungsi (stafBacaUang, bacaUangDari) dan sebelas baris BACA — data uang untuk
#      akun Penjaga laci yang ditandai owner (aksesAkun.bacaUang). Tulis tidak berubah. ----
BACA_UANG_V14 = ['biayaBulanan', 'pengeluaranHarian', 'kasbonMutasi', 'tutupHari', 'setoranKas', 'amplopLaba', 'modalOwner', 'utangOwnerMutasi', 'utangPemasokMutasi', 'pindahUang']
PENGATURAN_V14 = ("      allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan'])) || (id == 'titikKas' && stafBacaUang());",
                  "      allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan']));")
GANTI_V14 = [("    match /%s/{id} {\n      allow read: if owner() || stafBacaUang();" % n, "    match /%s/{id} {\n      allow read: if owner();" % n, 'v14 baca ' + n) for n in BACA_UANG_V14] \
    + [(PENGATURAN_V14[0], PENGATURAN_V14[1], 'v14 baca pengaturan/titikKas')]
FUNGSI_V14 = ['stafBacaUang', 'bacaUangDari']
BACA_UANG_WAJIB = "return masuk() && bacaUangDari(akun());"
DARI_WAJIB = "return a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true;"
V13_TEKS = None   # kontrol: pengganti isi firestore.rules.v13
BANDING_V13 = True


def ke_v13(R):
    """v14 → v13: cabut PERSIS ubahan v14 (sebelas baris baca — masing-masing satu kali; dua fungsi). Kembali (teks, cacat)."""
    cacat = []
    for baru, lama, nama in GANTI_V14:
        k = R.count(baru)
        if k != 1: cacat.append('v14 ≠ v13 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (nama, baru[:90], k))
        else: R = R.replace(baru, lama)
    for f in FUNGSI_V14:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v14 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v14(rules, r13, c14, akses_js):
    """18 · v14: bentuk persis dua fungsi & sebelas baris baca + sisanya = firestore.rules.v13 + daftar = akses.js + model kasus ★W (v14 & v13, beda = BEDA_V13)."""
    cacat = list(c14); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for n in BACA_UANG_V14:
        xs = [rata(x) for x in allow(B.get(n, ''), 'read')]
        if xs != ['if owner() || stafBacaUang()']: cacat.append('%s: allow read bukan "if owner() || stafBacaUang()" (v14): %s' % (n, xs))
    if rata(PENGATURAN_V14[0]) not in rata(B.get('pengaturan', '')): cacat.append('pengaturan: allow read bukan bentuk v14 (titikKas untuk akun bertanda)')
    for f, wf in (('stafBacaUang', BACA_UANG_WAJIB), ('bacaUangDari', DARI_WAJIB)):
        if rata(F.get(f, '')) != wf: cacat.append('%s() bukan bentuk v14 yang tercatat: %s' % (f, rata(F.get(f, '(tidak ada)'))))
    for n, b in B.items():
        for op in ('create', 'update', 'delete'):
            if any('stafBacaUang' in x or 'bacaUangDari' in x for x in allow(b, op)): cacat.append(n + ': ' + op + ' memakai stafBacaUang() — v14 hanya membuka BACA')
        if 'stafBacaUang' in b and n not in BACA_UANG_V14 + ['pengaturan']: cacat.append(n + ': stafBacaUang() dipakai di luar sebelas baris baca v14')
    for n, badan in F.items():
        if n not in ('stafBacaUang',) and 'bacaUangDari(' in badan and n != 'bacaUangDari': cacat.append('bacaUangDari() dipanggil dari fungsi ' + n)
        if n != 'stafBacaUang' and 'stafBacaUang(' in badan: cacat.append('stafBacaUang() dipanggil dari fungsi ' + n)
    # daftar = akses.js (pendengar uang firebase.js) — koleksi yang dibaca tablet = yang dibuka rules
    m = re.search(r"export const BACA_UANG = \[([^\]]*)\];", akses_js)
    if not m or sorted(re.findall(r"'(\w+)'", m.group(1))) != sorted(BACA_UANG_V14): cacat.append('akses.js BACA_UANG beda dengan koleksi yang dibuka rules v14 %s' % BACA_UANG_V14)
    if "export const DOK_UANG = { pengaturan: ['titikKas'] };" not in akses_js: cacat.append('akses.js DOK_UANG bukan { pengaturan: [titikKas] } (rules v14)')
    if "bacaUang: peran === 'ben' && dok.bacaUang === true" not in akses_js: cacat.append('akses.js keadaanAkun: tanda bacaUang tidak dibatasi Penjaga laci (rules v14 bacaUangDari)')
    v13 = V13_TEKS if V13_TEKS is not None else baca('firestore.rules.v13')
    a, b = rata(r13), rata(tanpa_komentar(v13))
    if BANDING_V13 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v14 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v13 — dekat "…%s…" (v13: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V14_TEKS if DOK_V14_TEKS is not None else (baca('docs/uji-rules-v14.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v14.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    lama = set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V13 + KASUS_V12 + KASUS_V11 + KASUS_V10 + KASUS_V9 + KASUS_V8 + KASUS_V7)
    bentrok = sorted(set(k[0] for k in KASUS_V14) & lama)
    if bentrok: cacat.append('nomor kasus v14 bertabrakan dengan v7–v13 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★W\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V14)
    if di_dok != di_model: cacat.append('docs/uji-rules-v14.md tidak sama dengan kasus model v14 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★W\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V14: cacat.append('docs/uji-rules-v14.md bagian "Wajib owner" bukan WAJIB_V14 — berkas: %s · model: %s' % (wajib, WAJIB_V14))
    try: M14 = rules_mini.Rules(rules); M13 = rules_mini.Rules(tanpa_komentar(v13))
    except Exception as e: return cacat + ['model v14: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V14:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M14.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v14 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v14 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h13 = M13.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap13 = (not boleh) if no in BEDA_V13 else boleh
        if h13.boleh != harap13: cacat.append('model v14 %s atas firestore.rules.v13 → %s, harap %s (%s)' % (no, 'LOLOS' if h13.boleh else 'DITOLAK', 'LOLOS' if harap13 else 'DITOLAK', 'ubahan v14' if no in BEDA_V13 else 'wajib sama dengan v13'))
    return cacat


# ---- v15 (owner 22 Nov 2026: BARANG MASUK & BAYAR SUPIR di tablet): v14 + PERSIS dua fungsi (stafCatatMasuk, stafKabarMasuk), satu ubahan fungsi
#      (stafMintaKeluar: jenis bongkar & bayarBon) dan dua baris tulis (batchMasuk create, persetujuan create). ----
JENIS_TITIPAN_V15 = ['toko', 'karyawan', 'kasbon', 'bongkar', 'bayarBon']
GANTI_V15 = [
    ("        && d.get('jenis', '') in ['toko', 'karyawan', 'kasbon', 'bongkar', 'bayarBon'] && d.get('nominal', 0) is int && d.get('nominal', 0) > 0\n"
     "        && (d.get('jenis', '') != 'bongkar' || (d.get('batchId', 0) is string && d.batchId.size() > 0))\n"
     "        && (d.get('jenis', '') != 'bayarBon' || (d.get('pemasok', 0) is string && d.pemasok.size() > 0 && d.pemasok.size() <= 60))\n",
     "        && d.get('jenis', '') in ['toko', 'karyawan', 'kasbon'] && d.get('nominal', 0) is int && d.get('nominal', 0) > 0\n", 'v15 stafMintaKeluar jenis bongkar & bayarBon'),
    ("(stafBuatLahir(['ben', 'karyawan']) && tglStaf('tanggal')) || (stafCatatMasuk(['ben']) && tglStaf('tanggal'));",
     "(stafBuatLahir(['ben', 'karyawan']) && tglStaf('tanggal'));", 'v15 batchMasuk create stafCatatMasuk'),
    ("stafKirimPesan(['ben', 'karyawan']) || stafKabarMasuk(['ben']);", "stafKirimPesan(['ben', 'karyawan']);", 'v15 persetujuan create stafKabarMasuk'),
]
FUNGSI_V15 = ['stafCatatMasuk', 'stafKabarMasuk']
CATAT_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('dariTablet', false) == true && d.get('caraBayar', '') == 'utang' && d.get('biayaBongkar', -1) == 0"
               " && d.get('pemasok', 0) is string && d.pemasok.size() > 0 && d.pemasok.size() <= 60 && d.pemasok != 'LAHIR BUKU'"
               " && d.get('merkList', 0) is list && d.merkList.size() > 0 && d.merkList.size() <= 20"
               " && !d.keys().hasAny(['lahirBuku', 'stokAwal', 'tutupBuku', 'riwayat', 'alasanKoreksi', 'noBon', 'bongkarTitipan']);")
KABAR_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'barangMasuk' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid"
               " && d.get('batchId', 0) is string && d.batchId.size() > 0"
               " && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'balasan']);")
V14_TEKS = None   # kontrol: pengganti isi firestore.rules.v14
BANDING_V14 = True


def ke_v14(R):
    """v15 → v14: cabut PERSIS ubahan v15 (tiga penggantian — masing-masing satu kali; dua fungsi). Kembali (teks, cacat)."""
    cacat = []
    for baru, lama, nama in GANTI_V15:
        k = R.count(baru)
        if k != 1: cacat.append('v15 ≠ v14 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (nama, baru[:90], k))
        else: R = R.replace(baru, lama)
    for f in FUNGSI_V15:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v15 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v15(rules, r14, c15, akses_js):
    """19 · v15: bentuk persis dua fungsi & tiga ubahan + sisanya = firestore.rules.v14 + daftar = akses.js + model kasus ★X (v15 & v14, beda = BEDA_V14)."""
    cacat = list(c15); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    for f, wf in (('stafCatatMasuk', CATAT_WAJIB), ('stafKabarMasuk', KABAR_WAJIB)):
        if rata(F.get(f, '')) != rata(wf): cacat.append('%s() bukan bentuk v15 yang tercatat: %s' % (f, rata(F.get(f, '(tidak ada)'))))
    xs = [rata(x) for x in allow(B.get('batchMasuk', ''), 'create')]
    if not any("(stafCatatMasuk(['ben']) && tglStaf('tanggal'))" in x for x in xs): cacat.append('batchMasuk create: kedatangan tablet tidak lewat stafCatatMasuk([ben]) && tglStaf (v15): %s' % xs)
    for n, b in B.items():
        if 'stafCatatMasuk' in b and n != 'batchMasuk': cacat.append(n + ': stafCatatMasuk() dipakai di luar batchMasuk create (v15)')
        if 'stafKabarMasuk' in b and n != 'persetujuan': cacat.append(n + ': stafKabarMasuk() dipakai di luar persetujuan create (v15)')
        for op in ('update', 'delete'):
            if any('stafCatatMasuk' in x or 'stafKabarMasuk' in x for x in allow(b, op)): cacat.append(n + ': ' + op + ' memakai fungsi v15 — v15 hanya membuka CREATE')
    # daftar = akses.js: jenis titipan & tindakan kedatangan yang dibuka server
    m = re.search(r"export const JENIS_TITIPAN = \[([^\]]*)\];", akses_js)
    if not m or re.findall(r"'(\w+)'", m.group(1)) != JENIS_TITIPAN_V15: cacat.append('akses.js JENIS_TITIPAN beda dengan jenis titipan rules v15 %s' % JENIS_TITIPAN_V15)
    if "kedatangan: ['ben']" not in (re.search(r'export const SERVER_BUKA = \{(.*?)\};', akses_js, re.S) or re.search('', '')).group(0): cacat.append("akses.js SERVER_BUKA tanpa kedatangan: ['ben'] (rules v15 stafCatatMasuk)")
    v14 = V14_TEKS if V14_TEKS is not None else baca('firestore.rules.v14')
    a, b = rata(r14), rata(tanpa_komentar(v14))
    if BANDING_V14 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v15 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v14 — dekat "…%s…" (v14: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V15_TEKS if DOK_V15_TEKS is not None else (baca('docs/uji-rules-v15.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v15.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    lama = set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V14 + KASUS_V13 + KASUS_V12 + KASUS_V11 + KASUS_V10 + KASUS_V9 + KASUS_V8 + KASUS_V7)
    bentrok = sorted(set(k[0] for k in KASUS_V15) & lama)
    if bentrok: cacat.append('nomor kasus v15 bertabrakan dengan v7–v14 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★X\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V15)
    if di_dok != di_model: cacat.append('docs/uji-rules-v15.md tidak sama dengan kasus model v15 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★X\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V15: cacat.append('docs/uji-rules-v15.md bagian "Wajib owner" bukan WAJIB_V15 — berkas: %s · model: %s' % (wajib, WAJIB_V15))
    try: M15 = rules_mini.Rules(rules); M14 = rules_mini.Rules(tanpa_komentar(v14))
    except Exception as e: return cacat + ['model v15: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V15:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M15.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v15 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v15 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h14 = M14.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap14 = (not boleh) if no in BEDA_V14 else boleh
        if h14.boleh != harap14: cacat.append('model v15 %s atas firestore.rules.v14 → %s, harap %s (%s)' % (no, 'LOLOS' if h14.boleh else 'DITOLAK', 'LOLOS' if harap14 else 'DITOLAK', 'ubahan v15' if no in BEDA_V14 else 'wajib sama dengan v14'))
    return cacat


# ---- v16 (owner 22 Nov 2026: TUTUP HARI dari tablet): v15 + PERSIS satu fungsi (stafHitungLaci) dan dua ubahan baris (persetujuan create: hitungan laci;
#      aturanToko read: dokumen tutupHari untuk ben). ----
GANTI_V16 = [
    ("stafKirimPesan(['ben', 'karyawan']) || stafKabarMasuk(['ben']) || (stafHitungLaci(['ben']) && tglStaf('tanggal'));",
     "stafKirimPesan(['ben', 'karyawan']) || stafKabarMasuk(['ben']);", 'v16 persetujuan create stafHitungLaci'),
    ("'hargaTingkat', 'produkArsip'] && staf(['ben', 'karyawan'])) || (id == 'tutupHari' && staf(['ben']));",
     "'hargaTingkat', 'produkArsip'] && staf(['ben', 'karyawan']));", 'v16 aturanToko read tutupHari (ben)'),
]
FUNGSI_V16 = ['stafHitungLaci']
HITUNG_WAJIB = ("let d = request.resource.data; return stafBuat(peranBoleh) && d.get('tindakan', '') == 'hitungLaci' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid"
                " && d.get('hitung', 0) is int && d.get('hitung', 0) > 0 && d.get('hitung', 0) <= 1000000000"
                " && d.get('amankan', -1) is int && d.get('amankan', -1) >= 0 && d.get('amankan', -1) <= d.get('hitung', 0)"
                " && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'balasan', 'koreksiOwner']);")
V15_TEKS = None   # kontrol: pengganti isi firestore.rules.v15
BANDING_V15 = True


def ke_v15(R):
    """v16 → v15: cabut PERSIS ubahan v16 (dua penggantian — masing-masing satu kali; satu fungsi). Kembali (teks, cacat)."""
    cacat = []
    for baru, lama, nama in GANTI_V16:
        k = R.count(baru)
        if k != 1: cacat.append('v16 ≠ v15 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (nama, baru[:90], k))
        else: R = R.replace(baru, lama)
    for f in FUNGSI_V16:
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v16 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def periksa_v16(rules, r15, c16, akses_js):
    """20 · v16: bentuk persis satu fungsi & dua ubahan + sisanya = firestore.rules.v15 + daftar = akses.js + model kasus ★Y (v16 & v15, beda = BEDA_V15)."""
    cacat = list(c16); B = blok_rules(rules); F = fungsi_rules(rules); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    if rata(F.get('stafHitungLaci', '')) != rata(HITUNG_WAJIB): cacat.append('stafHitungLaci() bukan bentuk v16 yang tercatat: %s' % rata(F.get('stafHitungLaci', '(tidak ada)')))
    xs = [rata(x) for x in allow(B.get('persetujuan', ''), 'create')]
    if not any("(stafHitungLaci(['ben']) && tglStaf('tanggal'))" in x for x in xs): cacat.append('persetujuan create: hitungan laci tidak lewat stafHitungLaci([ben]) && tglStaf (v16): %s' % xs)
    if not any("(id == 'tutupHari' && staf(['ben']))" in rata(x) for x in allow(B.get('aturanToko', ''), 'read')): cacat.append("aturanToko read: dokumen tutupHari tidak dibuka untuk ben saja (v16)")
    for n, b in B.items():
        if 'stafHitungLaci' in b and n != 'persetujuan': cacat.append(n + ': stafHitungLaci() dipakai di luar persetujuan create (v16)')
        for op in ('update', 'delete'):
            if any('stafHitungLaci' in x for x in allow(b, op)): cacat.append(n + ': ' + op + ' memakai fungsi v16 — v16 hanya membuka CREATE')
    for n in ('tutupHari', 'pengaturan', 'amplopLaba', 'pindahUang', 'penyesuaianStok'):
        for op in ('create', 'update', 'delete'):
            if any(re.search(r'\bstaf\w*\(', x) for x in allow(B.get(n, ''), op)): cacat.append(n + ': ' + op + ' dibuka untuk bukan-owner — v16: hari ditutup OWNER saja')
    # daftar = akses.js: dokumen setelan untuk ben & penjaga kiriman hitungan laci
    if "export const DOK_BEN = { aturanToko: ['tutupHari'] };" not in akses_js: cacat.append("akses.js DOK_BEN bukan { aturanToko: ['tutupHari'] } (rules v16 aturanToko read ben)")
    if "if (P !== 'ben' || (hak.hitungLaci || 'tidak') === 'tidak' || !hitungLaciSah(d, akun.uid))" not in akses_js: cacat.append('akses.js periksaKiriman: hitungan laci tidak dibatasi Penjaga laci + bentuk stafHitungLaci (rules v16)')
    v15 = V15_TEKS if V15_TEKS is not None else baca('firestore.rules.v15')
    a, b = rata(r15), rata(tanpa_komentar(v15))
    if BANDING_V15 and a != b:
        i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
        cacat.append('v16 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v15 — dekat "…%s…" (v15: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    dok = DOK_V16_TEKS if DOK_V16_TEKS is not None else (baca('docs/uji-rules-v16.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v16.md')) else '')
    v7dok = baca('docs/uji-rules-v7.md') if os.path.exists(os.path.join(AKAR, 'docs/uji-rules-v7.md')) else ''
    lama = set(re.findall(r'(★[A-Z]\d+)', v7dok)) | set(k[0] for k in KASUS_V15 + KASUS_V14 + KASUS_V13 + KASUS_V12 + KASUS_V11 + KASUS_V10 + KASUS_V9 + KASUS_V8 + KASUS_V7)
    bentrok = sorted(set(k[0] for k in KASUS_V16) & lama)
    if bentrok: cacat.append('nomor kasus v16 bertabrakan dengan v7–v15 (penguji emulator mengambil kolom Wajib v7 per nomor): ' + ', '.join(bentrok))
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★Y\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V16)
    if di_dok != di_model: cacat.append('docs/uji-rules-v16.md tidak sama dengan kasus model v16 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★Y\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V16: cacat.append('docs/uji-rules-v16.md bagian "Wajib owner" bukan WAJIB_V16 — berkas: %s · model: %s' % (wajib, WAJIB_V16))
    try: M16 = rules_mini.Rules(rules); M15 = rules_mini.Rules(tanpa_komentar(v15))
    except Exception as e: return cacat + ['model v16: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V16:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = M16.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v16 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v16 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
        h15 = M15.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7); harap15 = (not boleh) if no in BEDA_V15 else boleh
        if h15.boleh != harap15: cacat.append('model v16 %s atas firestore.rules.v15 → %s, harap %s (%s)' % (no, 'LOLOS' if h15.boleh else 'DITOLAK', 'LOLOS' if harap15 else 'DITOLAK', 'ubahan v16' if no in BEDA_V15 else 'wajib sama dengan v15'))
    return cacat


def ke_v6(R, KOL, ARSIP):
    """v7 → v6: cabut PERSIS ubahan v7 (tiap ganti wajib kena tepat sekali, blok demi blok). R = rules tanpa komentar. Kembali (teks, cacat)."""
    cacat = []; rata = lambda t: re.sub(r'\s+', ' ', t).strip()

    def ganti(t, lama, baru, di):
        k = t.count(lama)
        if k != 1: cacat.append('v7 ≠ v6 + ubahan yang tercatat: %s — %r ditemukan %d× (wajib 1×)' % (di, lama[:110], k)); return t
        return t.replace(lama, baru)
    out = []; pos = 0; dicabut = set()
    for m in re.finditer(r'\n    match /(\w+)/\{(\w+)\} \{\n(.*?)\n    \}', R, re.S):
        n = m.group(1); t = rata(m.group(3)); out.append(R[pos:m.start()]); pos = m.end()
        if n in ('batuNisan', 'fotoBon'): dicabut.add(n); continue   # (a) / (c) blok baru
        if n == 'penjualan': t = ganti(t, ' || (kasir() && ulangKasirBercap())', '', n)
        if n in ARSIP:   # (e) pintu
            t = ganti(t, ' || ' + suku_pintu(n, KOL), '', n + ' create')
            t = re.sub(r"allow create: if \((owner\(\) && (?:tglBaru\('\w+'\)|upBaru\(\)))\);", r"allow create: if \1;", t)   # v6 tanpa kurung bila suku owner satu-satunya
            t = ganti(t, 'allow delete: ' + hapus_pintu(n, KOL) + ';', 'allow delete: if owner() && %s;' % ekspr_lama(n, KOL), n + ' delete')
        if n in ('stokBahanLiteran', 'piutangMutasi'):   # (d) kasir@ dicabut
            t = ganti(t, "allow create: if (owner() && tglBaru('tanggal')) || ", "allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || ", n + ' create kasir@')
            t = ganti(t, "allow update: if owner() && tglUbah('tanggal');", "allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama());", n + ' update kasir@')
        if n == 'logAktivitas': t = ganti(t, "allow create: if owner() || stafJejak(['ben', 'karyawan']);", "allow create: if owner() || kasir() || stafJejak(['ben', 'karyawan']);", n)
        if n == 'pengaturan':
            t = ganti(t, "allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan']));", "allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan'])) || (id == 'aksesKasir' && kasir());", n + ' read')
            t = ganti(t, 'allow create, update: ' + ATUR_WAJIB + ';', "allow create, update: if owner() && (id != 'titikKas' || tglBaru('tanggal'));", n + ' create/update')
        if n == 'persetujuan':   # (b)
            t = ganti(t, ' '.join('allow %s: %s;' % (o, SETUJU_WAJIB[w]) for o, w in (('read', 'get'), ('create', 'create'), ('update, delete', 'update'))), 'allow read, write: if owner();', n)
        if n == 'tutupBukuAcara':   # (e) sanggahan rules 7 Okt: berita acara mengikat pintu
            t = ganti(t, 'allow create: %s;' % BUKU_V7['create'], 'allow create: if owner();', n + ' create')
            t = ganti(t, 'allow update: %s;' % BUKU_V7['update'], 'allow update: %s;' % UPDATE_BUKU, n + ' update')
            t = ganti(t, 'allow delete: %s;' % BUKU_V7['delete'], 'allow delete: if owner();', n + ' delete')
        if n == 'arsipTahun':   # (e) salinan arsip terikat ke aslinya
            t = ganti(t, 'allow read: if owner(); allow create, update: if owner() && arsipSah(id); allow delete: if owner();', 'allow read, write: if owner();', n)
        out.append('\n    match /%s/{%s} {\n%s\n    }' % (n, m.group(2), t))
    out.append(R[pos:]); R = ''.join(out)
    for n in ('batuNisan', 'fotoBon'):
        if n not in dicabut: cacat.append('blok v7 ' + n + ' tidak ada')
    for f in ['ulangKasirBercap', 'stafMintaNego'] + list(PINTU_FUNGSI):
        R2 = buang_fungsi(R, f)
        if R2 == R: cacat.append('fungsi v7 ' + f + '() tidak ada')
        R = R2
    return R, cacat


def buang_fungsi(R, f):
    """Buang SATU deklarasi `function f(...) { … }` (satu baris atau banyak baris) — kurung kurawal dihitung, bukan pola baris."""
    m = re.search(r"\n    function " + f + r"\([^)]*\) \{", R)
    if not m: return R
    i = m.end() - 1; d = 0
    for j in range(i, len(R)):
        if R[j] == '{': d += 1
        elif R[j] == '}':
            d -= 1
            if d == 0: return R[:m.start()] + R[j + 1:]
    return R


def periksa_v7(rules):
    """10 · v7 FINAL (owner 7 Okt 2026): v6 + PERSIS daftar ubahan (hemat baca, persetujuan, fotoBon, pangkas kasir@, pintu tutup buku)."""
    cacat = []; R = tanpa_komentar(rules); B = blok_rules(R); F = fungsi_rules(R)
    rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    ukb = rata(F.get('ulangKasirBercap', ''))
    if ukb != UKB_WAJIB: cacat.append('ulangKasirBercap() bukan "hanya capServer yang berbeda DAN (capServer tidak ada ATAU == request.time)": ' + (ukb or '(tidak ada)'))
    for n, b in B.items():
        if 'ulangKasirBercap' not in b: continue
        if n != 'penjualan': cacat.append(n + ': ulangKasirBercap() dipakai di luar penjualan (koleksi kasir lain tetap tulis-ulang identik — hanya ditulis kasir.html yang pensiun)')
        for op in ('get', 'list', 'create', 'delete'):
            if any('ulangKasirBercap' in x for x in allow(b, op)): cacat.append(n + ': ulangKasirBercap() di allow ' + op)
    if not any('(kasir() && ulangKasirBercap())' in rata(x) for x in allow(B.get('penjualan', ''), 'update')): cacat.append('penjualan: suku (kasir() && ulangKasirBercap()) tidak ada di allow update — kirim ulang karcis kasir-v33 akan ditolak')
    for n, badan in F.items():
        if n != 'ulangKasirBercap' and 'ulangKasirBercap' in badan: cacat.append('ulangKasirBercap() dipanggil dari fungsi ' + n)
    bn = B.get('batuNisan', '')
    if not bn: cacat.append('blok batuNisan tidak ada — hapus /baru/ yang membawa batu nisan akan ditolak seluruh batch-nya')
    else:
        for op, w in NISAN_WAJIB.items():
            xs = [rata(x) for x in allow(bn, op)]
            if xs != [w]: cacat.append('batuNisan: allow %s bukan "%s": %s' % (op, w, xs))
        if re.search(r'\b(staf\w*|kasir|masuk)\(|get\(/|exists\(', bn): cacat.append('batuNisan: terbuka untuk selain owner / membaca dokumen lain (access call)')
    # (b) persetujuan nego staf
    st = B.get('persetujuan', '')
    for op, w in (SETUJU_WAJIB.items() if BENTUK_V7 else []):
        xs = [rata(x) for x in allow(st, op)]
        if xs != [w]: cacat.append('persetujuan: allow %s bukan "%s" (v7: staf hanya minta nego & membaca keputusan; memutus = owner): %s' % (op, w, xs))
    if BENTUK_V7 and rata(F.get('stafMintaNego', '')) != MINTA_WAJIB: cacat.append('stafMintaNego() bukan "stafBuat + tindakan nego + status menunggu + negoUid = uid penulis + tanpa kolom keputusan": ' + rata(F.get('stafMintaNego', '(tidak ada)')))
    # (c) foto bon
    fb = B.get('fotoBon', '')
    if not fb: cacat.append('blok fotoBon tidak ada — foto bon (paket E-2) ditolak server')
    for op, w in (FOTO_WAJIB.items() if BENTUK_V7 else []):
        xs = [rata(x) for x in allow(fb, op)]
        if xs != ([w] if w else []): cacat.append('fotoBon: allow %s bukan %s (owner saja, bentuk & ukuran dibatasi, tanpa ubah): %s' % (op, '"%s"' % w if w else '(tidak ada)', xs))
    # selain ubahan yang tercatat: ISI SAMA dengan v6 (tanpa komentar & spasi) — v7 tidak boleh mempersempit / melonggarkan apa pun diam-diam
    KOL, _ = kp_js(); ARSIP = koleksi_arsip() or []
    v6 = V6_TEKS if V6_TEKS is not None else baca('firestore.rules.v6')
    sisa, c2 = ke_v6(R, KOL, ARSIP)
    if BANDING_V6:
        cacat += c2
        a, b = rata(sisa), rata(tanpa_komentar(v6))
        if a != b:
            i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
            cacat.append('v7 mengubah lebih dari ubahan yang tercatat atas firestore.rules.v6 — dekat "…%s…" (v6: "…%s…")' % (a[max(0, i - 60):i + 60], b[max(0, i - 60):i + 60]))
    return cacat


def periksa_pintu(rules, akses_js_tidak_dipakai=None):
    """11 · pintu tutup buku 2027 (owner 7 Okt, K8): bentuk PERSIS + model penafsir pada kasus Playground ★ v7."""
    cacat = []; R = tanpa_komentar(rules); B = blok_rules(R); F = fungsi_rules(R); rata = lambda t: re.sub(r'\s+', ' ', t).strip()
    KOL, _ = kp_js(); ARSIP = koleksi_arsip()
    if not ARSIP or len(ARSIP) < 15: return ['daftar koleksi arsip tutup buku (tbDaftarKoleksi ∩ KP_KOLEKSI) tidak terbaca dari mesin: %s' % ARSIP]
    if BENTUK_V7:
        for f, w in PINTU_FUNGSI.items():
            if rata(F.get(f, '')) != w: cacat.append('pintu: fungsi %s() bukan bentuk yang disepakati: %s' % (f, rata(F.get(f, '(tidak ada)'))[:200]))
        for f, boleh in PEMANGGIL_PINTU.items():
            for g, badan in F.items():
                if g != f and re.search(r'\b' + f + r'\(', badan) and g not in boleh: cacat.append('pintu: %s() dipanggil dari fungsi %s' % (f, g))
        pola = re.compile(r'\b(' + '|'.join(PINTU_FUNGSI) + r')\(')
        for n, b in B.items():
            for op in OPERASI:
                for x in allow(b, op):
                    k = rata(x); pakai = set(pola.findall(k))
                    if not pakai: continue
                    if n in ARSIP and op == 'create':
                        sk = suku_atas(k)
                        if pakai != {'pintuTulis'} or [s for s in sk if 'pintu' in s] != [suku_pintu(n, KOL)]: cacat.append('pintu: %s create bukan satu suku "%s": %s' % (n, suku_pintu(n, KOL), k))
                    elif n in ARSIP and op == 'delete':
                        if k != hapus_pintu(n, KOL): cacat.append('pintu: %s delete bukan "%s": %s' % (n, hapus_pintu(n, KOL), k))
                    elif n == 'pengaturan' and op in ('create', 'update'):
                        if k != ATUR_WAJIB: cacat.append('pintu: pengaturan %s bukan "%s": %s' % (op, ATUR_WAJIB, k))
                    elif n == 'tutupBukuAcara' and op in ('create', 'update'):
                        if k != BUKU_V7[op]: cacat.append('pintu: tutupBukuAcara %s bukan "%s": %s' % (op, BUKU_V7[op], k))
                    elif n == 'arsipTahun' and op in ('create', 'update'):
                        if k != ARSIP_V7[op]: cacat.append('pintu: arsipTahun %s bukan "%s": %s' % (op, ARSIP_V7[op], k))
                    else: cacat.append('pintu: %s di %s allow %s — pintu hanya untuk create/delete koleksi arsip, titik kas, salinan arsip & berita acara (bukan ubah, baca, koleksi lain): %s' % (', '.join(sorted(pakai)), n, op, k))
        for op, w in ARSIP_V7.items():
            xs = [rata(x) for x in allow(B.get('arsipTahun', ''), op)]
            if xs != [w]: cacat.append('arsipTahun: allow %s bukan "%s" (salinan arsip terikat ke aslinya; owner saja): %s' % (op, w, xs))
            if n in ARSIP:
                if not any('pintuTulis' in rata(x) for x in allow(b, 'create')): cacat.append('pintu: %s create tanpa pintuTulis — saldo pembuka / pengembalian arsip bulan terkunci ditolak (tutup buku buntu)' % n)
                if not any('pintuHapus' in rata(x) for x in allow(b, 'delete')): cacat.append('pintu: %s delete tanpa pintuHapus — arsip bulan terkunci ditolak (tutup buku buntu)' % n)
        if [rata(x) for x in allow(B.get('pengaturan', ''), 'create')] != [ATUR_WAJIB]: cacat.append('pintu: pengaturan create bukan "%s"' % ATUR_WAJIB)
        fb = baca('baru/js/data/firebase.js')
        for t in ("tahun + '|' + x.koleksi + '|' + x.id", "tahun + '|' + x.koleksi + '|' + x.idAsli"):
            if t not in fb: cacat.append('pintu: jalur arsip firebase.js tidak lagi "' + t + '" — rules mencari arsipTahun/\'Y|koleksi|id\'')
        # salinan arsip = bentuk yang dinilai arsipSah (tahun angka, koleksi, idAsli teks, dok = isi catatan)
        if "{ id: tahun + '|' + x.koleksi + '|' + x.id, tahun, koleksi: x.koleksi, idAsli: String(x.id), dok: x.data," not in fb:
            cacat.append('pintu: bentuk salinan arsip firebase.js berubah — rules arsipSah menilai { id, tahun, koleksi, idAsli, dok }')
    # daftar koleksi di rules = sumbernya (kunci-periode.js, toko.js, mesin) — dinilai juga untuk kontrol 'model:'
    kpj = KP_TEKS if KP_TEKS is not None else baca('baru/js/data/kunci-periode.js'); tk = baca('baru/js/data/toko.js')
    daftar_js = lambda teks, nama: re.findall(r"'(\w+)'", (re.search(r'export const ' + nama + r' = \[(.*?)\];', teks, re.S) or re.search('', '')).group(0))
    daftar_fn = lambda f: re.findall(r"'(\w+)'", (re.search(r'\[(.*?)\]', F.get(f, ''), re.S) or re.search('', '')).group(0))
    cache_pembuka = re.findall(r": '(\w+)'", (re.search(r'export const CACHE_PEMBUKA = \{(.*?)\};', tk) or re.search('', '')).group(0))
    if not (daftar_fn('kolPembuka') == daftar_js(kpj, 'KP_KOLEKSI_PEMBUKA') == cache_pembuka) or not cache_pembuka:
        cacat.append('pintu: koleksi saldo pembuka beda — rules kolPembuka %s · KP_KOLEKSI_PEMBUKA %s · toko.js CACHE_PEMBUKA %s' % (daftar_fn('kolPembuka'), daftar_js(kpj, 'KP_KOLEKSI_PEMBUKA'), cache_pembuka))
    if not (daftar_fn('kolArsip') == daftar_js(kpj, 'KP_KOLEKSI_PINTU') == ARSIP):
        cacat.append('pintu: koleksi arsip berpintu beda — rules kolArsip %s · KP_KOLEKSI_PINTU %s · mesin ∩ KP_KOLEKSI %s' % (daftar_fn('kolArsip'), daftar_js(kpj, 'KP_KOLEKSI_PINTU'), ARSIP))
    semua = koleksi_arsip(True) or []; bebas = [k for k in semua if k not in ARSIP]
    m_bebas = re.search(r"d\.koleksi in \[([^\]]*)\]", F.get('arsipSah', ''))
    if not m_bebas or re.findall(r"'(\w+)'", m_bebas.group(1)) != bebas: cacat.append('arsipTahun: koleksi arsip tanpa kunci di rules %s ≠ mesin tbDaftarKoleksi − KP_KOLEKSI %s (arsip tutup buku ditolak / koleksi terkunci lolos tanpa salinan asli)' % (m_bebas and m_bebas.group(1), bebas))
    # docs/uji-rules-v7.md memuat PERSIS kasus ★ model ini (id sama) — owner menjalankan yang sudah dinilai model
    dok = DOK_V7_TEKS if DOK_V7_TEKS is not None else baca('docs/uji-rules-v7.md')
    di_dok = set(re.findall(r'^\|(?: \d+ \|)? (★[A-Z]\d+) \|', dok, re.M)); di_model = set(k[0] for k in KASUS_V7 if k[0].startswith('★'))
    if di_dok != di_model: cacat.append('docs/uji-rules-v7.md tidak sama dengan kasus model v7 — hanya di berkas: %s · hanya di model: %s' % (sorted(di_dok - di_model), sorted(di_model - di_dok)))
    # bagian "Wajib owner" = WAJIB_V7 PERSIS (urutan juga) — daftar pendek yang dijalankan owner sebelum Publish; sisanya opsional (dinilai model di sini)
    mw = re.search(r'\n## Wajib owner[^\n]*\n(.*?)\n## ', dok, re.S)
    wajib = re.findall(r'^\| \d+ \| (★[A-Z]\d+) \|', mw.group(1), re.M) if mw else []
    if wajib != WAJIB_V7: cacat.append('docs/uji-rules-v7.md bagian "Wajib owner" bukan daftar kasus wajib model (WAJIB_V7) — berkas: %s · model: %s' % (wajib, WAJIB_V7))
    if not set(WAJIB_V7) <= di_model: cacat.append('WAJIB_V7 memuat kasus yang tidak ada di model: %s' % sorted(set(WAJIB_V7) - di_model))
    # MODEL: penafsir rules mini menilai TEKS rules pada kasus Playground ★ v7 (dokumen uji yang sama)
    try: RM = rules_mini.Rules(rules)
    except Exception as e: return cacat + ['model v7: rules tidak bisa diurai penafsir mini — %s' % e]
    for no, nama, aud, op, kol, id_, data, ubah_db, boleh, maks in KASUS_V7:
        db = dict(DB_UJI_V7); db.update(ubah_db or {}); db = dict((k, v) for k, v in db.items() if v is not None)
        h = RM.nilai(op, kol, id_, auth=AKUN_UJI[aud], data=data, sebelum=db, jam=JAM_UJI_V7)
        if h.boleh != boleh: cacat.append('model v7 %s %s → %s, wajib %s%s' % (no, nama, 'LOLOS' if h.boleh else 'DITOLAK', 'LOLOS' if boleh else 'DITOLAK', (' (' + h.galat + ')') if h.galat else ''))
        elif maks is not None and h.akses > maks: cacat.append('model v7 %s %s: %d access call (batas jalur ini %d)' % (no, nama, h.akses, maks))
    return cacat


# ---- MODEL v7: dokumen uji Playground (docs/uji-rules-v7.md "Dokumen uji") & kasus ★ — SAMA PERSIS dengan berkas itu (periksa_pintu memeriksa id-nya)
# Sanggahan rules 7 Okt: dokumen uji U1–U10 (+ U11 aksesAkun uji, hanya untuk kasus staf yang opsional); kasus WAJIB owner = WAJIB_V7 (bagian "Wajib owner").
TS = rules_mini.Ts
JAM_UJI_V7 = TS.dari_iso('2026-10-09T03:00:00Z')   # Playground dijalankan Okt 2026 (jam simulasi = jam sekarang) — "tahun lalu" = 2025
BESOK = TS(JAM_UJI_V7.ms + 24 * 3600000); LIMA_HARI = TS(JAM_UJI_V7.ms + 5 * 24 * 3600000); THN2100 = TS.dari_iso('2100-01-01T00:00:00Z'); THN2020 = TS.dari_iso('2020-01-01T00:00:00Z')
HARI_INI = '2026-10-09'
AKUN_UJI = {'owner': {'uid': 'uid-uji', 'email': EMAIL_OWNER}, 'kasir': {'uid': 'uid-kasir-uji', 'email': EMAIL_KASIR}, 'staf': {'uid': 'uid-uji-b', 'email': 'uji.b@contoh.com'},
            'baru': {'uid': 'baru1', 'email': 'uji.baru1@contoh.com'}}
NOTA = {'id': 'uji-v7-nota', 'tanggal': HARI_INI, 'hargaTotal': 1000, 'namaProduk': 'Contoh'}
DOK_LAMA = {'id': 'uji-v7-lama', 'tanggal': '2021-06-15', 'hargaTotal': 1000}
DOK_BEDA = {'id': 'uji-v7-beda', 'tanggal': '2021-06-16', 'hargaTotal': 1000}
DOK_PULIH = {'id': 'uji-v7-pulih', 'tanggal': '2021-03-01', 'hargaTotal': 500}
PEMBUKA = {'id': 'uji-v7-pembuka', 'tipe': 'saldoAwal', 'tutupBuku': True, 'tahunDari': 2021, 'tanggal': '2021-03-01', 'nominal': 1000}
# paraf.pada U3/U4 = teks jam BUKAN ISO (sanggahan bukti emulator 7 Okt): Playground mengubah teks ISO 'Z' jadi timestamp, juga di dokumen yang dibaca get()
# (docs/uji-rules-v6.md "Sifat Playground") — pintuSah membandingkan teks; urutan teks ini tetap sesudah 'Y-12-31T17:00:00.000Z'. U4 = "<hari ini> 00:00" (berlaku di
# tahun mana pun: tahun lalu = tahun hari ini − 1). Bentuk ISO yang ditulis aplikasi (toISOString) dinilai M-P6b (model & emulator) dan gladi pintu.
ACARA_2021 = {'tahun': 2021, 'status': 'terkunci', 'paraf': {'pada': '2026-10-01 00:00'}, 'titikSebelum': {'tanggal': '2021-06-30', 'laci': 7, 'brankas': 0}}
ACARA_2025 = {'tahun': 2025, 'mode': 'sungguhan', 'status': 'berjalan', 'paraf': {'pada': HARI_INI + ' 00:00'}}
def _arsip(idAsli, dok): return {'id': '2021|penjualan|' + idAsli, 'tahun': 2021, 'koleksi': 'penjualan', 'idAsli': idAsli, 'dok': dok}
DB_UJI_V7 = {
    'penjualan/uji-v7-nota': NOTA,                                                                   # U1
    'aturanToko/kunciPeriode': {'sampaiBulan': '2021-12', 'riwayat': []},                            # U2 — kunci uji: tidak ada catatan toko ≤ 2021
    'tutupBukuAcara/2021': ACARA_2021,                                                               # U3
    'tutupBukuAcara/2025': ACARA_2025,                                                               # U4 — berita acara TAHUN LALU yang berjalan (pintu baru)
    'pengaturan/pintuBuku': {'id': 'pintuBuku', 'tahun': 2021, 'status': 'berjalan', 'sampai': THN2100},   # U5
    'penjualan/uji-v7-lama': DOK_LAMA,                                                               # U6
    'arsipTahun/2021|penjualan|uji-v7-lama': _arsip('uji-v7-lama', DOK_LAMA),                       # U7 — salinan = U6 persis
    'penjualan/uji-v7-beda': DOK_BEDA,                                                               # U8
    'arsipTahun/2021|penjualan|uji-v7-beda': _arsip('uji-v7-beda', dict(DOK_BEDA, hargaTotal=900)), # U9 — salinan BERISI LAIN
    'arsipTahun/2021|penjualan|uji-v7-pulih': _arsip('uji-v7-pulih', DOK_PULIH),                    # U10
    'aksesAkun/uid-uji-b': {'uid': 'uid-uji-b', 'nama': 'UJI B', 'email': 'uji.b@contoh.com', 'peran': 'ben', 'aktif': True},   # U11 (opsional: kasus staf)
    'pengaturan/titikKas': {'id': 'titikKas', 'tanggal': '2026-10-08', 'laci': 1},   # dokumen NYATA (isinya tidak dinilai selain tanggal) — bukan dokumen uji
}
MINTA = {'id': 'uji-v7-minta', 'tindakan': 'nego', 'status': 'menunggu', 'negoUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'teks': 'uji'}
FOTO = {'id': 'uji-v7-foto', 'idBon': 'b-uji', 'jenis': 'image/jpeg', 'base64': 'QUJD'}
PB_BARU = dict(PEMBUKA, id='uji-v7-pb-baru')
PINTU_BARU = {'id': 'pintuBuku', 'tahun': 2025, 'status': 'berjalan', 'sampai': BESOK}
ACARA_BARU = {'id': '2024', 'tahun': 2024, 'mode': 'sungguhan', 'status': 'berjalan', 'paraf': {'pada': HARI_INI + 'T03:00:00.000Z'}}
BERCAP = {'penjualan/uji-v7-bercap': dict(NOTA, id='uji-v7-bercap', capServer=TS(JAM_UJI_V7.ms - 3600000))}
# kasus WAJIB yang dijalankan owner di Playground sebelum Publish (bagian "Wajib owner" di docs/uji-rules-v7.md — sama persis); sisanya opsional (model CI)
# ★T1 TIDAK wajib (sanggahan bukti emulator 7 Okt): acaraBaru mewajibkan paraf.pada TEKS ISO 'Z', yang diubah Playground jadi timestamp → di Playground
# keluar DITOLAK bukan karena rules. Buktinya emulator (★T1 LOLOS) + gladi pintu (aplikasi asli membuat berita acara baru di server).
WAJIB_V7 = ['★A1', '★B2', '★K3', '★F1', '★R1', '★P1', '★P20', '★P21', '★P22', '★P4', '★P2', '★P23', '★P5', '★P6', '★P16', '★T3', '★P19']
# (no, nama, akun, operasi, koleksi, id, isi, ubah_db, wajib lolos?, batas access call)
KASUS_V7 = [
    # A/B · hemat baca (sejak draf v7 pertama)
    ('★A1', 'kasir@ nota baru tanpa capServer', 'kasir', 'create', 'penjualan', 'uji-v7-baru', dict(NOTA, id='uji-v7-baru'), None, True, 0),
    ('★A2', 'kasir@ kirim ulang identik', 'kasir', 'update', 'penjualan', 'uji-v7-nota', NOTA, None, True, 0),
    ('★A3', 'owner baca batu nisan', 'owner', 'get', 'batuNisan', 'uji-v7', None, None, True, 0),
    ('★A4', 'owner hapus batu nisan', 'owner', 'delete', 'batuNisan', 'uji-v7', None, None, True, 0),
    ('M-A5', 'kasir@ kirim ulang tanpa capServer atas nota bercap (HP kasir-v32) — Playground tidak bisa membuang kolom', 'kasir', 'update', 'penjualan', 'uji-v7-bercap', dict(NOTA, id='uji-v7-bercap'), BERCAP, True, 0),
    ('★B1', 'kasir@ kirim ulang mengubah hargaTotal + cap', 'kasir', 'update', 'penjualan', 'uji-v7-nota', dict(NOTA, hargaTotal=2000, capServer=JAM_UJI_V7), None, False, None),
    ('★B2', 'kasir@ cap dari jam HP (ketikan)', 'kasir', 'update', 'penjualan', 'uji-v7-nota', dict(NOTA, capServer=TS(JAM_UJI_V7.ms - 60000)), None, False, None),
    ('★B3', 'kasir@ kirim ulang stokBahanLiteran (v7: jalurnya dicabut)', 'kasir', 'update', 'stokBahanLiteran', 'x', {'id': 'x', 'tanggal': HARI_INI, 'capServer': JAM_UJI_V7}, {'stokBahanLiteran/x': {'id': 'x', 'tanggal': HARI_INI}}, False, None),
    ('★B4', 'staf baca batu nisan', 'staf', 'get', 'batuNisan', 'uji-v7', None, None, False, None),
    ('★B5', 'staf tulis batu nisan', 'staf', 'create', 'batuNisan', 'uji-v7', {'capServer': JAM_UJI_V7}, None, False, None),
    ('★B6', 'owner batu nisan cap ketikan', 'owner', 'create', 'batuNisan', 'uji-v7', {'id': 'penjualan|x', 'koleksi': 'penjualan', 'idDok': 'x', 'capServer': TS(JAM_UJI_V7.ms - 60000)}, None, False, None),
    ('★B7', 'kasir@ baca batu nisan', 'kasir', 'get', 'batuNisan', 'uji-v7', None, None, False, None),
    ('M-B8', 'kasir@ buang cap + ubah hargaTotal', 'kasir', 'update', 'penjualan', 'uji-v7-bercap', dict(NOTA, id='uji-v7-bercap', hargaTotal=2000), BERCAP, False, None),
    # N · permintaan nego staf (persetujuan) — staf = UID uji U11
    ('★N1', 'staf aktif minta nego (menunggu, atas nama sendiri)', 'staf', 'create', 'persetujuan', 'uji-v7-minta', MINTA, None, True, 1),
    ('★N2', 'staf aktif membaca persetujuan', 'staf', 'list', 'persetujuan', 'uji-v7-minta', None, None, True, 1),
    ('★N3', 'owner memutus (setuju)', 'owner', 'update', 'persetujuan', 'uji-v7-minta', dict(MINTA, status='disetujui', diputusPada='x'), {'persetujuan/uji-v7-minta': MINTA}, True, 0),
    ('★N4', 'staf minta atas nama akun lain (negoUid lain)', 'staf', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, negoUid='uid-lain'), None, False, None),
    ('★N5', 'staf menulis permintaan yang sudah "disetujui"', 'staf', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, status='disetujui'), None, False, None),
    ('★N6', 'staf menulis kolom keputusan (diputusPada)', 'staf', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, diputusPada='2026-10-09T03:00:00Z'), None, False, None),
    ('★N7', 'staf minta tindakan selain nego (hapus)', 'staf', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, tindakan='hapus'), None, False, None),
    ('★N8', 'staf memutus permintaannya sendiri (update)', 'staf', 'update', 'persetujuan', 'uji-v7-minta', dict(MINTA, status='disetujui'), {'persetujuan/uji-v7-minta': MINTA}, False, None),
    ('★N9', 'olehUid bukan uid penulis', 'staf', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, olehUid='uid-lain'), None, False, None),
    ('★N10', 'akun tanpa aksesAkun minta nego', 'baru', 'create', 'persetujuan', 'uji-v7-minta', dict(MINTA, negoUid='baru1', olehUid='baru1'), None, False, None),
    ('★N11', 'kasir@ membaca persetujuan', 'kasir', 'list', 'persetujuan', 'uji-v7-minta', None, None, False, None),
    # F · foto bon
    ('★F1', 'owner simpan foto bon', 'owner', 'create', 'fotoBon', 'uji-v7-foto', FOTO, None, True, 0),
    ('★F2', 'owner baca foto bon', 'owner', 'list', 'fotoBon', 'uji-v7-foto', None, None, True, 0),
    ('★F3', 'owner hapus foto bon', 'owner', 'delete', 'fotoBon', 'uji-v7-foto', None, {'fotoBon/uji-v7-foto': FOTO}, True, 0),
    ('★F4', 'owner ubah foto bon', 'owner', 'update', 'fotoBon', 'uji-v7-foto', dict(FOTO, idBon='b-lain'), {'fotoBon/uji-v7-foto': FOTO}, False, None),
    ('★F5', 'jenis bukan gambar', 'owner', 'create', 'fotoBon', 'uji-v7-foto', dict(FOTO, jenis='text/html'), None, False, None),
    ('★F6', 'id isi ≠ id dokumen', 'owner', 'create', 'fotoBon', 'uji-v7-foto', dict(FOTO, id='lain'), None, False, None),
    ('★F7', 'tanpa idBon', 'owner', 'create', 'fotoBon', 'uji-v7-foto', dict((k, v) for k, v in FOTO.items() if k != 'idBon'), None, False, None),
    ('★F8', 'staf membaca foto bon', 'staf', 'list', 'fotoBon', 'uji-v7-foto', None, None, False, None),
    ('M-F9', 'base64 di atas 960.000 huruf (model saja — terlalu panjang diketik di Playground)', 'owner', 'create', 'fotoBon', 'uji-v7-foto', dict(FOTO, base64='A' * 960001), None, False, None),
    # K · kasir@ dipangkas (kasir darurat: nota, denyut, katalog)
    ('★K1', 'kasir@ denyut perangkatStatus', 'kasir', 'create', 'perangkatStatus', 'd-uji', {'id': 'd-uji', 'aplikasi': 'darurat', 'pada': '2026-10-09T03:00:00Z'}, None, True, 0),
    ('★K2', 'kasir@ baca katalog ringkasanKasir/aktif', 'kasir', 'get', 'ringkasanKasir', 'aktif', None, None, True, 0),
    ('★K3', 'kasir@ create piutangMutasi', 'kasir', 'create', 'piutangMutasi', 'uji-v7-k', {'id': 'uji-v7-k', 'tipe': 'bayar', 'tanggal': HARI_INI, 'nominal': 1000}, None, False, None),
    ('★K4', 'kasir@ create stokBahanLiteran', 'kasir', 'create', 'stokBahanLiteran', 'uji-v7-k', {'id': 'uji-v7-k', 'tipe': 'pakai', 'tanggal': HARI_INI, 'jumlah': 1}, None, False, None),
    ('★K5', 'kasir@ create logAktivitas', 'kasir', 'create', 'logAktivitas', 'uji-v7-k', {'id': 'uji-v7-k', 'aksi': 'tulis'}, None, False, None),
    ('★K6', 'kasir@ baca pengaturan/aksesKasir', 'kasir', 'get', 'pengaturan', 'aksesKasir', None, None, False, None),
    ('★K7', 'kasir@ baca pengaturan/keamanan', 'kasir', 'get', 'pengaturan', 'keamanan', None, None, False, None),
    # R · regresi singkat (tulisan biasa hari ini tetap seperti v6)
    ('★R1', 'owner nota hari ini', 'owner', 'create', 'penjualan', 'uji-v7-r1', {'id': 'uji-v7-r1', 'tanggal': HARI_INI, 'hargaTotal': 1000}, None, True, 0),
    ('★R2', 'staf aktif nota tunai hari ini (atas nama sendiri)', 'staf', 'create', 'penjualan', 'uji-v7-r2', {'id': 'uji-v7-r2', 'tanggal': HARI_INI, 'hargaTotal': 1000, 'caraBayar': 'Tunai', 'olehUid': 'uid-uji-b'}, None, True, 1),
    ('★R3', 'staf aktif membaca nota', 'staf', 'get', 'penjualan', 'uji-v7-nota', None, None, True, 1),
    # P · pintu tutup buku (kunci uji 2021-12, pintu 2021 terbuka; berita acara 2025 = tahun lalu berjalan)
    ('★P1', 'owner HAPUS catatan bulan terkunci yang salinan arsipnya SAMA PERSIS', 'owner', 'delete', 'penjualan', 'uji-v7-lama', None, None, True, 3),
    ('★P20', 'owner HAPUS catatan bulan terkunci yang salinan arsipnya BERISI LAIN (hapus lalu tulis ulang = ubah)', 'owner', 'delete', 'penjualan', 'uji-v7-beda', None, None, False, None),
    ('M-P8', 'owner hapus catatan bulan terkunci TANPA salinan arsip', 'owner', 'delete', 'penjualan', 'uji-v7-tanpa', None, {'penjualan/uji-v7-tanpa': dict(DOK_LAMA, id='uji-v7-tanpa', tanggal='2021-06-16')}, False, None),
    ('★P21', 'owner TULIS salinan arsip catatan bulan terkunci = catatan aslinya (U6)', 'owner', 'update', 'arsipTahun', '2021|penjualan|uji-v7-lama', _arsip('uji-v7-lama', DOK_LAMA), None, True, 2),
    ('★P22', 'owner TULIS salinan arsip KARANGAN (catatan aslinya tidak ada)', 'owner', 'create', 'arsipTahun', '2021|penjualan|uji-v7-karang', _arsip('uji-v7-karang', {'id': 'uji-v7-karang', 'tanggal': '2021-05-01', 'hargaTotal': 777}), None, False, None),
    ('M-P26b', 'owner tulis salinan arsip bulan terkunci yang isinya beda dari aslinya (U6)', 'owner', 'update', 'arsipTahun', '2021|penjualan|uji-v7-lama', _arsip('uji-v7-lama', dict(DOK_LAMA, hargaTotal=5)), None, False, None),
    ('M-P26c', 'owner tulis salinan arsip koleksi yang tidak diarsip (pindahUang)', 'owner', 'create', 'arsipTahun', '2021|pindahUang|uji-v7-pu', {'id': '2021|pindahUang|uji-v7-pu', 'tahun': 2021, 'koleksi': 'pindahUang', 'idAsli': 'uji-v7-pu', 'dok': {'id': 'uji-v7-pu', 'tanggal': '2021-06-01'}}, {'pindahUang/uji-v7-pu': {'id': 'uji-v7-pu', 'tanggal': '2021-06-01'}}, False, None),
    ('M-P26d', 'owner tulis salinan arsip bertahun / id yang tidak cocok', 'owner', 'create', 'arsipTahun', '2020|penjualan|uji-v7-lama', _arsip('uji-v7-lama', DOK_LAMA), None, False, None),
    ('M-P26e', 'salinan arsip catatan bulan terbuka (tanpa kunci): cukup bentuknya', 'owner', 'create', 'arsipTahun', '2025|penjualan|uji-v7-r', {'id': '2025|penjualan|uji-v7-r', 'tahun': 2025, 'koleksi': 'penjualan', 'idAsli': 'uji-v7-r', 'dok': {'id': 'uji-v7-r', 'tanggal': '2025-05-01'}}, None, True, 1),
    ('★P2', 'owner BUAT saldo pembuka tahun pintu bertanggal bulan terkunci (koleksi pembuka)', 'owner', 'create', 'piutangMutasi', 'uji-v7-pb-baru', PB_BARU, None, True, 2),
    ('★P23', 'owner BUAT "saldo pembuka" di PENJUALAN (bukan koleksi saldo pembuka)', 'owner', 'create', 'penjualan', 'uji-v7-pb-jual', {'id': 'uji-v7-pb-jual', 'tanggal': '2021-03-01', 'hargaTotal': 1000, 'tutupBuku': True, 'tahunDari': 2021}, None, False, None),
    ('M-P3', 'owner HAPUS saldo pembuka tahun pintu (tarik saat Batalkan)', 'owner', 'delete', 'piutangMutasi', 'uji-v7-pembuka', None, {'piutangMutasi/uji-v7-pembuka': PEMBUKA}, True, 2),
    ('★P4', 'owner KEMBALIKAN catatan dari arsip, isinya sama', 'owner', 'create', 'penjualan', 'uji-v7-pulih', DOK_PULIH, None, True, 3),
    ('★P5', 'owner titik kas 31 Des tahun pintu (bulan terkunci)', 'owner', 'update', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2021-12-31', 'laci': 1}, None, True, 2),
    ('★P25', 'owner titik kas 30 Jun tahun pintu, isi kantong BEDA dari titikSebelum berita acara (bukan 31 Des, bukan titikSebelum persis)', 'owner', 'update', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2021-06-30', 'laci': 1}, None, False, None),
    ('★P26', 'owner titik kas kembali = titikSebelum berita acara 2021 PERSIS (Batalkan)', 'owner', 'create', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2021-06-30', 'laci': 7, 'brankas': 0}, None, True, 3),
    ('★P6', 'owner BUKA pintu tahun lalu (berita acara 2025 berjalan SEBELUM kiriman, sampai besok)', 'owner', 'create', 'pengaturan', 'pintuBuku', PINTU_BARU, None, True, 1),
    ('M-P6b', 'owner BUKA pintu tahun lalu — paraf.pada berita acara berbentuk toISOString (yang ditulis aplikasi; Playground tidak bisa)', 'owner', 'create', 'pengaturan', 'pintuBuku', PINTU_BARU,
     {'tutupBukuAcara/2025': dict(ACARA_2025, paraf={'pada': '2026-01-04T03:00:00.000Z'})}, True, 1),
    ('★P7', 'owner TUTUP pintu', 'owner', 'update', 'pengaturan', 'pintuBuku', {'id': 'pintuBuku', 'tahun': 2021, 'status': 'tutup'}, None, True, 0),
    ('★P9', 'owner UBAH catatan bulan terkunci (pintu tidak membuka ubah)', 'owner', 'update', 'penjualan', 'uji-v7-lama', dict(DOK_LAMA, hargaTotal=2000), None, False, None),
    ('★P10', 'owner BUAT catatan biasa di bulan terkunci (bukan pembuka, tidak di arsip)', 'owner', 'create', 'penjualan', 'uji-v7-baru2', {'id': 'uji-v7-baru2', 'tanggal': '2021-06-20', 'hargaTotal': 1000}, None, False, None),
    ('★P11', 'owner saldo pembuka tahun LAIN (tahunDari 2020)', 'owner', 'create', 'piutangMutasi', 'uji-v7-pb-lain', dict(PEMBUKA, id='uji-v7-pb-lain', tahunDari=2020), None, False, None),
    ('★P12', 'owner "saldo pembuka" tanpa tanda tutupBuku (tahunDari ada)', 'owner', 'create', 'piutangMutasi', 'uji-v7-pb-tanpa', dict((k, v) for k, v in dict(PB_BARU, id='uji-v7-pb-tanpa').items() if k != 'tutupBuku'), None, False, None),
    ('★P13', 'owner kembalikan dari arsip dengan isi BEDA', 'owner', 'create', 'penjualan', 'uji-v7-pulih', dict(DOK_PULIH, hargaTotal=600), None, False, None),
    ('★P14', 'kasir@ saldo pembuka lewat pintu', 'kasir', 'create', 'piutangMutasi', 'uji-v7-pb-baru', PB_BARU, None, False, None),
    ('★P15', 'staf aktif menghapus catatan bulan terkunci yang diarsip', 'staf', 'delete', 'penjualan', 'uji-v7-lama', None, None, False, None),
    ('★P16', 'owner buka pintu lebih dari 72 jam', 'owner', 'create', 'pengaturan', 'pintuBuku', dict(PINTU_BARU, sampai=LIMA_HARI), None, False, None),
    ('★P17', 'owner buka pintu untuk tahun berjalan', 'owner', 'create', 'pengaturan', 'pintuBuku', dict(PINTU_BARU, tahun=2026), None, False, None),
    ('★P18', 'owner buka pintu tahun tanpa berita acara (2020)', 'owner', 'create', 'pengaturan', 'pintuBuku', dict(PINTU_BARU, tahun=2020), None, False, None),
    ('★P24', 'owner buka pintu 2021 (berita acaranya ada, tapi BUKAN tahun lalu)', 'owner', 'create', 'pengaturan', 'pintuBuku', dict(PINTU_BARU, tahun=2021), None, False, None),
    ('M-P24b', 'buka pintu tahun lalu di atas berita acara yang SELESAI', 'owner', 'create', 'pengaturan', 'pintuBuku', PINTU_BARU, {'tutupBukuAcara/2025': dict(ACARA_2025, status='selesai')}, False, None),
    ('M-P24c', 'buka pintu tahun lalu di atas berita acara yang dimulai SEBELUM tahun itu berakhir', 'owner', 'create', 'pengaturan', 'pintuBuku', PINTU_BARU, {'tutupBukuAcara/2025': dict(ACARA_2025, paraf={'pada': '2025-06-01T00:00:00.000Z'})}, False, None),
    ('★P19', 'pintu KEDALUWARSA (sampai 2020): hapus yang diarsip ditolak lagi', 'owner', 'delete', 'penjualan', 'uji-v7-lama', None, {'pengaturan/pintuBuku': dict(DB_UJI_V7['pengaturan/pintuBuku'], sampai=THN2020)}, False, None),
    ('M-P20', 'pintu DITUTUP (status tutup, sampai masih jauh): saldo pembuka bulan terkunci ditolak', 'owner', 'create', 'piutangMutasi', 'uji-v7-pb-baru', PB_BARU, {'pengaturan/pintuBuku': {'id': 'pintuBuku', 'tahun': 2021, 'status': 'tutup', 'sampai': THN2100}}, False, None),
    ('M-P21', 'tanpa dokumen pintu: hapus yang diarsip ditolak', 'owner', 'delete', 'penjualan', 'uji-v7-lama', None, {'pengaturan/pintuBuku': None}, False, None),
    ('M-P22', 'catatan bertanggal SESUDAH tahun pintu (2022, terkunci uji diperluas)', 'owner', 'delete', 'penjualan', 'uji-v7-2022', None,
     {'aturanToko/kunciPeriode': {'sampaiBulan': '2022-12', 'riwayat': []}, 'penjualan/uji-v7-2022': dict(DOK_LAMA, id='uji-v7-2022', tanggal='2022-03-01'),
      'arsipTahun/2021|penjualan|uji-v7-2022': {'tahun': 2021, 'koleksi': 'penjualan', 'idAsli': 'uji-v7-2022', 'dok': dict(DOK_LAMA, id='uji-v7-2022', tanggal='2022-03-01')}}, False, None),
    ('M-P23', 'pindahUang bulan terkunci (tidak diarsip — tanpa pintu)', 'owner', 'delete', 'pindahUang', 'uji-v7-pu', None,
     {'pindahUang/uji-v7-pu': {'id': 'uji-v7-pu', 'tanggal': '2021-06-01'}, 'arsipTahun/2021|pindahUang|uji-v7-pu': {'tahun': 2021, 'koleksi': 'pindahUang', 'idAsli': 'uji-v7-pu', 'dok': {'id': 'uji-v7-pu', 'tanggal': '2021-06-01'}}}, False, None),
    ('M-P27', 'owner buka pintu tahun BERJALAN walau berita acaranya berjalan', 'owner', 'create', 'pengaturan', 'pintuBuku', dict(PINTU_BARU, tahun=2026), {'tutupBukuAcara/2026': dict(ACARA_2025, tahun=2026)}, False, None),
    ('M-P25', 'saldo pembuka tahun pintu bertanggal SESUDAH tahun itu (2022, terkunci uji diperluas)', 'owner', 'create', 'piutangMutasi', 'uji-v7-pb-2022', dict(PEMBUKA, id='uji-v7-pb-2022', tanggal='2022-02-01'),
     {'aturanToko/kunciPeriode': {'sampaiBulan': '2022-12', 'riwayat': []}}, False, None),
    ('M-P26', 'UBAH catatan bulan terkunci jadi sama dengan salinan arsipnya + cap (pintu tidak membuka ubah)', 'owner', 'update', 'penjualan', 'uji-v7-lama', dict(DOK_LAMA, capServer=JAM_UJI_V7), None, False, None),
    ('M-P24d', 'titik kas MUNDUR ke tahun sesudah pintu (2022, terkunci) ditolak', 'owner', 'update', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2022-06-30'}, {'aturanToko/kunciPeriode': {'sampaiBulan': '2022-12', 'riwayat': []}}, False, None),
    # T · berita acara tutup buku mengikat pintu (sanggahan rules 7 Okt)
    ('★T1', 'owner BUAT berita acara baru: tahun lampau, sungguhan, berjalan, jam mulai hari ini', 'owner', 'create', 'tutupBukuAcara', '2024', ACARA_BARU, None, True, 0),
    ('★T2', 'owner buat berita acara baru dengan jam mulai jauh mundur (1 Jun tahun lalu)', 'owner', 'create', 'tutupBukuAcara', '2024', dict(ACARA_BARU, paraf={'pada': '2025-06-01T00:00:00.000Z'}), None, False, None),
    ('★T3', 'owner tulis berita acara 2021 SELESAI selagi pintu 2021 masih terbuka', 'owner', 'update', 'tutupBukuAcara', '2021', dict(ACARA_2021, status='selesai'), None, False, None),
    ('★T4', 'owner hapus berita acara yang belum dibatalkan (U4, berjalan)', 'owner', 'delete', 'tutupBukuAcara', '2025', None, None, False, None),
    ('★T5', 'owner buat berita acara tahun BERJALAN (2026)', 'owner', 'create', 'tutupBukuAcara', '2026', dict(ACARA_BARU, id='2026', tahun=2026), None, False, None),
    ('M-T6', 'berita acara SELESAI bersama pintu yang sudah tertutup', 'owner', 'update', 'tutupBukuAcara', '2021', dict(ACARA_2021, status='selesai'), {'pengaturan/pintuBuku': {'id': 'pintuBuku', 'tahun': 2021, 'status': 'tutup', 'sampai': THN2100}}, True, 1),
    ('M-T7', 'hapus berita acara yang DIBATALKAN', 'owner', 'delete', 'tutupBukuAcara', '2021', None, {'tutupBukuAcara/2021': dict(ACARA_2021, status='dibatalkan')}, True, 0),
    ('M-T8', 'berita acara baru langsung SELESAI', 'owner', 'create', 'tutupBukuAcara', '2024', dict(ACARA_BARU, status='selesai'), None, False, None),
    ('M-T9', 'berita acara baru id ≠ tahun', 'owner', 'create', 'tutupBukuAcara', '2023', ACARA_BARU, None, False, None),
]

# ---- MODEL v8 (B1, owner 16 Nov 2026): kasus ★H docs/uji-rules-v8.md — dokumen uji = DB_UJI_V7 (U11 aksesAkun uji = staf ben) + ubah_db per kasus.
USUL = {'id': 'uji-v8-usul', 'tindakan': 'hargaPelanggan', 'status': 'menunggu', 'usulUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'teks': 'uji',
        'ubah': {'jenis': 'orang', 'orang': 'contoh', 'nama': 'Contoh', 'tingkatId': 'warung'}}
SETELAN_HT = {'id': 'hargaTingkat', 'tingkat': [{'id': 'warung', 'nama': 'Warung', 'potKg': 300}], 'barang': {}, 'orang': {}, 'khusus': []}
WAJIB_V8 = ['★H5', '★H6']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator (mesin rules server) — boleh juga di Playground dengan U11
KASUS_V8 = [
    ('★H1', 'staf aktif membaca aturanToko/hargaTingkat', 'staf', 'get', 'aturanToko', 'hargaTingkat', None, None, True, 1),
    ('★H2', 'staf aktif membaca aturanToko/produkArsip', 'staf', 'get', 'aturanToko', 'produkArsip', None, None, True, 1),
    ('★H3', 'staf aktif mengusulkan harga pelanggan (menunggu, atas nama sendiri)', 'staf', 'create', 'persetujuan', 'uji-v8-usul', USUL, None, True, None),
    ('★H4', 'owner menyetujui usul (update)', 'owner', 'update', 'persetujuan', 'uji-v8-usul', dict(USUL, status='disetujui', diputusPada='x'), {'persetujuan/uji-v8-usul': USUL}, True, 0),
    ('★H5', 'owner menulis aturanToko/hargaTingkat', 'owner', 'update', 'aturanToko', 'hargaTingkat', dict(SETELAN_HT, orang={'contoh': 'warung'}), {'aturanToko/hargaTingkat': SETELAN_HT}, True, None),
    ('★H6', 'owner membuat aturanToko/hargaTingkat pertama kali', 'owner', 'create', 'aturanToko', 'hargaTingkat', SETELAN_HT, None, True, None),
    ('★H7', 'staf usul atas nama akun lain (usulUid lain)', 'staf', 'create', 'persetujuan', 'uji-v8-usul', dict(USUL, usulUid='uid-lain'), None, False, None),
    ('★H8', 'staf usul yang sudah "disetujui"', 'staf', 'create', 'persetujuan', 'uji-v8-usul', dict(USUL, status='disetujui'), None, False, None),
    ('★H9', 'staf usul membawa kolom keputusan (diputusPada)', 'staf', 'create', 'persetujuan', 'uji-v8-usul', dict(USUL, diputusPada='2026-11-16T03:00:00Z'), None, False, None),
    ('★H10', 'staf memutus usulnya sendiri (update)', 'staf', 'update', 'persetujuan', 'uji-v8-usul', dict(USUL, status='disetujui'), {'persetujuan/uji-v8-usul': USUL}, False, None),
    ('★H11', 'staf menulis aturanToko/hargaTingkat langsung', 'staf', 'update', 'aturanToko', 'hargaTingkat', dict(SETELAN_HT, orang={'contoh': 'warung'}), {'aturanToko/hargaTingkat': SETELAN_HT}, False, None),
    ('★H12', 'staf membaca aturanToko/het (tetap owner saja)', 'staf', 'get', 'aturanToko', 'het', None, None, False, None),
    ('★H13', 'akun tanpa aksesAkun mengusulkan', 'baru', 'create', 'persetujuan', 'uji-v8-usul', dict(USUL, usulUid='baru1', olehUid='baru1'), None, False, None),
    ('★H14', 'kasir@ membaca aturanToko/hargaTingkat', 'kasir', 'get', 'aturanToko', 'hargaTingkat', None, None, False, None),
    ('★H15', 'olehUid bukan uid penulis', 'staf', 'create', 'persetujuan', 'uji-v8-usul', dict(USUL, olehUid='uid-lain'), None, False, None),
]
BEDA_V7 = {'★H1', '★H2', '★H3'}   # yang DIBUKA v8 (ditolak v7); kasus lain wajib sama hasilnya di v7
DOK_V8_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v8.md

# ---- MODEL v9 (B2, owner 17 Nov 2026): kasus ★J docs/uji-rules-v9.md — dokumen uji = DB_UJI_V7 (U11 = staf ben) + ubah_db per kasus.
MINTA_KREDIT = {'id': 'uji-v9-kredit', 'tindakan': 'kredit', 'status': 'menunggu', 'mintaUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'pelanggan': 'Contoh', 'nominal': 50000, 'teks': 'uji'}
U11_KARYAWAN = {'aksesAkun/uid-uji-b': {'uid': 'uid-uji-b', 'nama': 'UJI B', 'email': 'uji.b@contoh.com', 'peran': 'karyawan', 'aktif': True}}
WAJIB_V9 = ['★J2', '★J3']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V9 = [
    ('★J1', 'ben meminta persetujuan bon (menunggu, atas nama sendiri)', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', MINTA_KREDIT, None, True, None),
    ('★J2', 'owner membuat permintaan bon (owner selalu boleh)', 'owner', 'create', 'persetujuan', 'uji-v9-kredit', MINTA_KREDIT, None, True, None),
    ('★J3', 'owner menyetujui permintaan bon (update)', 'owner', 'update', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, status='disetujui', diputusPada='x'), {'persetujuan/uji-v9-kredit': MINTA_KREDIT}, True, 0),
    ('★J4', 'ben meminta atas nama akun lain (mintaUid lain)', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, mintaUid='uid-lain'), None, False, None),
    ('★J5', 'ben mengirim permintaan yang sudah "disetujui"', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, status='disetujui'), None, False, None),
    ('★J6', 'ben membawa kolom keputusan (diputusPada)', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, diputusPada='2026-11-17T03:00:00Z'), None, False, None),
    ('★J7', 'ben memutus permintaannya sendiri (update)', 'staf', 'update', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, status='disetujui'), {'persetujuan/uji-v9-kredit': MINTA_KREDIT}, False, None),
    ('★J8', 'karyawan meminta persetujuan bon (bon = ben saja)', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', MINTA_KREDIT, U11_KARYAWAN, False, None),
    ('★J9', 'akun tanpa aksesAkun meminta', 'baru', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, mintaUid='baru1', olehUid='baru1'), None, False, None),
    ('★J10', 'olehUid bukan uid penulis', 'staf', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, olehUid='uid-lain'), None, False, None),
    ('★J11', 'kasir@ meminta persetujuan bon', 'kasir', 'create', 'persetujuan', 'uji-v9-kredit', dict(MINTA_KREDIT, mintaUid='uid-kasir-uji', olehUid='uid-kasir-uji'), None, False, None),
]
BEDA_V8 = {'★J1'}   # yang DIBUKA v9 (ditolak v8); kasus lain wajib sama hasilnya di v8
DOK_V9_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v9.md

# ---- MODEL v10 (B3, owner 18 Nov 2026): kasus ★L docs/uji-rules-v10.md — dokumen uji = DB_UJI_V7 (U11 = staf ben) + ubah_db per kasus.
SJ_UJI = {'id': 'uji-v10-sj', 'noSJ': 'SJ26-XXX-0001', 'tanggal': '2026-10-09', 'jam': '10:00', 'trxIdJual': '1', 'namaPelanggan': 'Contoh', 'alamat': 'uji', 'pengantar': 'UJI B',
          'isi': [{'nama': 'uji', 'jumlah': 1, 'satuan': 'karung'}], 'nilaiNota': 50000, 'ongkir': 0, 'bayarDiTempat': False, 'tagihRp': 0, 'status': 'berangkat', 'olehUid': 'uid-uji-b'}
SJ_TANDA = {'status': 'diterima', 'penerima': 'uji', 'diterimaPada': 'x', 'buktiTtd': ['1'], 'diubahOlehUid': 'uid-uji-b', 'diubahOleh': 'UJI B'}
BUKTI_UJI = {'id': 'uji-v10-bukti', 'idSJ': 'uji-v10-sj', 'noSJ': 'SJ26-XXX-0001', 'jenisBukti': 'ttd', 'jenis': 'image/png', 'base64': 'iVBORw0KGgo=', 'olehUid': 'uid-uji-b'}
WAJIB_V10 = ['★L2', '★L3', '★L4']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V10 = [
    ('★L1', 'ben membuat surat jalan (berangkat, atas nama sendiri)', 'staf', 'create', 'suratJalan', 'uji-v10-sj', SJ_UJI, None, True, None),
    ('★L2', 'owner membuat surat jalan', 'owner', 'create', 'suratJalan', 'uji-v10-sj', SJ_UJI, None, True, None),
    ('★L3', 'owner membatalkan surat jalan (update)', 'owner', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, status='batal', alasanBatal='uji'), {'suratJalan/uji-v10-sj': SJ_UJI}, True, 0),
    ('★L4', 'owner menyimpan bukti tanda tangan', 'owner', 'create', 'buktiTerima', 'uji-v10-bukti', BUKTI_UJI, None, True, 0),
    ('★L5', 'ben menandai surat jalan DITERIMA (kolom tandai)', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, **SJ_TANDA), {'suratJalan/uji-v10-sj': SJ_UJI}, True, None),
    ('★L6', 'karyawan menandai surat jalan DITERIMA', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, **SJ_TANDA), dict({'suratJalan/uji-v10-sj': SJ_UJI}, **U11_KARYAWAN), True, None),
    ('★L7', 'karyawan menandai GAGAL ANTAR', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, status='gagal', alasanGagal='toko tutup', diubahOlehUid='uid-uji-b', diubahOleh='UJI B'), dict({'suratJalan/uji-v10-sj': SJ_UJI}, **U11_KARYAWAN), True, None),
    ('★L8', 'karyawan membuat surat jalan (bikin = owner & ben)', 'staf', 'create', 'suratJalan', 'uji-v10-sj', SJ_UJI, U11_KARYAWAN, False, None),
    ('★L9', 'ben membuat surat jalan yang sudah "diterima"', 'staf', 'create', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, status='diterima'), None, False, None),
    ('★L10', 'ben membuat surat jalan berisi kolom penerimaan (penerima)', 'staf', 'create', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, penerima='uji'), None, False, None),
    ('★L11', 'ben mengubah tagihan saat menandai (tagihRp)', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, tagihRp=1, **SJ_TANDA), {'suratJalan/uji-v10-sj': SJ_UJI}, False, None),
    ('★L12', 'ben menandai ulang surat jalan yang sudah diterima', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, status='gagal', alasanGagal='x', diubahOlehUid='uid-uji-b'), {'suratJalan/uji-v10-sj': dict(SJ_UJI, status='diterima')}, False, None),
    ('★L13', 'ben membatalkan surat jalan (batal = owner)', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, status='batal', diubahOlehUid='uid-uji-b'), {'suratJalan/uji-v10-sj': SJ_UJI}, False, None),
    ('★L14', 'ben menandai atas nama akun lain (diubahOlehUid lain)', 'staf', 'update', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, **dict(SJ_TANDA, diubahOlehUid='uid-lain')), {'suratJalan/uji-v10-sj': SJ_UJI}, False, None),
    ('★L15', 'ben membuat surat jalan atas nama akun lain (olehUid lain)', 'staf', 'create', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, olehUid='uid-lain'), None, False, None),
    ('★L16', 'ben menyimpan bukti tanda tangan', 'staf', 'create', 'buktiTerima', 'uji-v10-bukti', BUKTI_UJI, None, True, None),
    ('★L17', 'karyawan menyimpan bukti foto', 'staf', 'create', 'buktiTerima', 'uji-v10-bukti', dict(BUKTI_UJI, jenisBukti='foto', jenis='image/jpeg'), U11_KARYAWAN, True, None),
    ('★L18', 'bukti tanpa surat jalan (idSJ kosong)', 'staf', 'create', 'buktiTerima', 'uji-v10-bukti', dict(BUKTI_UJI, idSJ=''), None, False, None),
    ('★L19', 'bukti berjenis bukan gambar', 'staf', 'create', 'buktiTerima', 'uji-v10-bukti', dict(BUKTI_UJI, jenis='text/html'), None, False, None),
    ('★L20', 'ben mengubah bukti (tanpa ubah)', 'staf', 'update', 'buktiTerima', 'uji-v10-bukti', dict(BUKTI_UJI, base64='AAAA'), {'buktiTerima/uji-v10-bukti': BUKTI_UJI}, False, None),
    ('★L21', 'ben menghapus surat jalan', 'staf', 'delete', 'suratJalan', 'uji-v10-sj', None, {'suratJalan/uji-v10-sj': SJ_UJI}, False, None),
    ('★L22', 'ben membaca surat jalan', 'staf', 'get', 'suratJalan', 'uji-v10-sj', None, {'suratJalan/uji-v10-sj': SJ_UJI}, True, 1),
    ('★L23', 'kasir@ membaca surat jalan', 'kasir', 'get', 'suratJalan', 'uji-v10-sj', None, {'suratJalan/uji-v10-sj': SJ_UJI}, False, None),
    ('★L24', 'akun tanpa aksesAkun membuat surat jalan', 'baru', 'create', 'suratJalan', 'uji-v10-sj', dict(SJ_UJI, olehUid='baru1'), None, False, None),
]
BEDA_V9 = {'★L1', '★L2', '★L3', '★L4', '★L5', '★L6', '★L7', '★L16', '★L17', '★L22'}   # yang DIBUKA v10 (blok baru; ditolak v9); kasus lain wajib sama hasilnya di v9
DOK_V10_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v10.md

# ---- MODEL v11 (B4, owner 18 Nov 2026): kasus ★M docs/uji-rules-v11.md — dokumen uji = DB_UJI_V7 (U11 = staf ben) + ubah_db per kasus.
PS_UJI = {'id': 'uji-v11-ps', 'tanggal': '2026-10-09', 'jam': '10:00', 'namaPelanggan': 'Contoh', 'isi': '1 karung Uji 50 kg', 'alamat': 'uji', 'nilaiPerkiraan': 0,
          'status': 'dipesan', 'riwayatStatus': [], 'noPO': 'PO-UJI', 'tanggalKirim': '', 'catatan': '', 'olehUid': 'uid-uji-b'}
PS_UBAH = {'isi': '2 karung Uji 50 kg', 'noPO': 'PO-UJI-2', 'tanggalKirim': '2026-10-12', 'diubahOlehUid': 'uid-uji-b', 'diubahOleh': 'UJI B'}
RUTIN_UJI = {'id': 'uji-v11-rutin', 'namaPelanggan': 'Contoh', 'isi': '1 karung Uji 50 kg', 'alamat': 'uji', 'noPO': '', 'catatan': '', 'ulang': 'mingguan', 'hari': 1,
             'mulai': '2026-10-09', 'aktif': True, 'lewati': [], 'dibuatTanggal': '2026-10-09', 'olehUid': 'uid-uji-b'}
DB_PS = {'pesanan/uji-v11-ps': PS_UJI}; DB_RUTIN = {'orderRutin/uji-v11-rutin': RUTIN_UJI}
WAJIB_V11 = ['★M2', '★M3', '★M4']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V11 = [
    ('★M1', 'ben membuat pesanan (dipesan, atas nama sendiri)', 'staf', 'create', 'pesanan', 'uji-v11-ps', PS_UJI, None, True, None),
    ('★M2', 'owner membuat pesanan', 'owner', 'create', 'pesanan', 'uji-v11-ps', PS_UJI, None, True, 0),
    ('★M3', 'owner membuat jadwal order rutin', 'owner', 'create', 'orderRutin', 'uji-v11-rutin', RUTIN_UJI, None, True, 0),
    ('★M4', 'owner membatalkan pesanan (update)', 'owner', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='batal', alasanBatal='uji'), DB_PS, True, 0),
    ('★M5', 'ben mengubah isi, PO & tanggal kirim pesanan', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, **PS_UBAH), DB_PS, True, None),
    ('★M6', 'ben membatalkan pesanan (uang muka jadi saldo)', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='batal', alasanBatal='tidak jadi', nasibUangMuka='saldo', diubahOlehUid='uid-uji-b'), DB_PS, True, None),
    ('★M7', 'ben menandai pesanan DIANTAR', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='diantar', diubahOlehUid='uid-uji-b'), DB_PS, True, None),
    ('★M8', 'karyawan membuat pesanan (bikin = owner & ben)', 'staf', 'create', 'pesanan', 'uji-v11-ps', PS_UJI, U11_KARYAWAN, False, None),
    ('★M9', 'karyawan mengubah isi pesanan', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, **PS_UBAH), dict(DB_PS, **U11_KARYAWAN), False, None),
    ('★M10', 'ben membuat pesanan yang sudah bernota (trxIdJual)', 'staf', 'create', 'pesanan', 'uji-v11-ps', dict(PS_UJI, trxIdJual='1'), None, False, None),
    ('★M11', 'ben membuat pesanan berstatus "dibayar"', 'staf', 'create', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='dibayar'), None, False, None),
    ('★M12', 'ben membuat pesanan berisi kolom batal (nasibUangMuka)', 'staf', 'create', 'pesanan', 'uji-v11-ps', dict(PS_UJI, nasibUangMuka='saldo'), None, False, None),
    ('★M13', 'ben mengganti nama pemesan', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, namaPelanggan='Lain', diubahOlehUid='uid-uji-b'), DB_PS, False, None),
    ('★M14', 'ben mengubah pesanan yang sudah JADI NOTA', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='dibayar', trxIdJual='1', isi='lain', diubahOlehUid='uid-uji-b'), {'pesanan/uji-v11-ps': dict(PS_UJI, status='dibayar', trxIdJual='1')}, False, None),
    ('★M15', 'ben menghidupkan lagi pesanan yang batal', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='dipesan', diubahOlehUid='uid-uji-b'), {'pesanan/uji-v11-ps': dict(PS_UJI, status='batal')}, False, None),
    ('★M16', 'ben mengubah pesanan atas nama akun lain (diubahOlehUid lain)', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, **dict(PS_UBAH, diubahOlehUid='uid-lain')), DB_PS, False, None),
    ('★M17', 'karyawan mencatat jual pesanan (JADI NOTA — sejak v1)', 'staf', 'update', 'pesanan', 'uji-v11-ps', dict(PS_UJI, status='dibayar', trxIdJual='1', diubahOlehUid='uid-uji-b'), dict(DB_PS, **U11_KARYAWAN), True, None),
    ('★M18', 'ben membuat jadwal order rutin', 'staf', 'create', 'orderRutin', 'uji-v11-rutin', RUTIN_UJI, None, True, None),
    ('★M19', 'ben melewati sekali & menghentikan jadwal', 'staf', 'update', 'orderRutin', 'uji-v11-rutin', dict(RUTIN_UJI, lewati=['2026-10-12'], aktif=False, diubahOlehUid='uid-uji-b'), DB_RUTIN, True, None),
    ('★M20', 'ben mengganti pembuat jadwal (olehUid)', 'staf', 'update', 'orderRutin', 'uji-v11-rutin', dict(RUTIN_UJI, olehUid='uid-lain', diubahOlehUid='uid-uji-b'), DB_RUTIN, False, None),
    ('★M21', 'karyawan membuat jadwal order rutin', 'staf', 'create', 'orderRutin', 'uji-v11-rutin', RUTIN_UJI, U11_KARYAWAN, False, None),
    ('★M22', 'ben menghapus jadwal', 'staf', 'delete', 'orderRutin', 'uji-v11-rutin', None, DB_RUTIN, False, None),
    ('★M23', 'karyawan membaca jadwal (tablet menampilkan pengingat)', 'staf', 'get', 'orderRutin', 'uji-v11-rutin', None, dict(DB_RUTIN, **U11_KARYAWAN), True, 1),
    ('★M24', 'kasir@ membaca jadwal', 'kasir', 'get', 'orderRutin', 'uji-v11-rutin', None, DB_RUTIN, False, None),
    ('★M25', 'ben membuat pesanan atas nama akun lain (olehUid lain)', 'staf', 'create', 'pesanan', 'uji-v11-ps', dict(PS_UJI, olehUid='uid-lain'), None, False, None),
]
BEDA_V10 = {'★M1', '★M3', '★M5', '★M6', '★M7', '★M18', '★M19', '★M23'}   # yang DIBUKA v11 (ditolak v10); kasus lain wajib sama hasilnya di v10
DOK_V11_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v11.md

# ---- MODEL v12 (paket S2b tanda kenal, owner 19 Nov 2026): kasus ★S docs/uji-rules-v12.md — dokumen uji = DB_UJI_V7 (U11 = staf ben) + ubah_db per kasus.
TK_UJI = {'id': 'uji-v12-tk', 'jenis': 'barcode', 'kode': '8990000000017', 'sasaran': {'jalur': 'kemasan', 'kunci': 'Uji 5', 'berat': '', 'nama': 'Uji 5 kg'}, 'tanggal': '2026-10-09', 'jam': '10:00', 'olehUid': 'uid-uji-b'}
TK_KARTU = dict(TK_UJI, jenis='nfc', kode='04A1B2C3D4E5F6', sasaran={'nama': 'Contoh'})
DB_TK = {'tandaKenal/uji-v12-tk': TK_UJI}
WAJIB_V12 = ['★S1', '★S2', '★S3']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V12 = [
    ('★S1', 'owner mendaftarkan barcode kemasan', 'owner', 'create', 'tandaKenal', 'uji-v12-tk', TK_UJI, None, True, 0),
    ('★S2', 'owner melepas pasangan (update sasaran kosong)', 'owner', 'update', 'tandaKenal', 'uji-v12-tk', dict(TK_UJI, sasaran=None), DB_TK, True, 0),
    ('★S3', 'owner menghapus pasangan', 'owner', 'delete', 'tandaKenal', 'uji-v12-tk', None, DB_TK, True, 0),
    ('★S4', 'ben mendaftarkan barcode dari tablet (atas nama sendiri)', 'staf', 'create', 'tandaKenal', 'uji-v12-tk', TK_UJI, None, True, None),
    ('★S5', 'karyawan mendaftarkan kartu pelanggan NFC', 'staf', 'create', 'tandaKenal', 'uji-v12-tk', TK_KARTU, U11_KARYAWAN, True, None),
    ('★S6', 'ben mendaftarkan atas nama akun lain (olehUid lain)', 'staf', 'create', 'tandaKenal', 'uji-v12-tk', dict(TK_UJI, olehUid='uid-lain'), None, False, None),
    ('★S7', 'ben mengubah pasangan yang sudah tercatat', 'staf', 'update', 'tandaKenal', 'uji-v12-tk', dict(TK_UJI, kode='8990000000024'), DB_TK, False, None),
    ('★S8', 'ben menghapus pasangan', 'staf', 'delete', 'tandaKenal', 'uji-v12-tk', None, DB_TK, False, None),
    ('★S9', 'karyawan membaca tanda kenal (tablet mengenali kode)', 'staf', 'get', 'tandaKenal', 'uji-v12-tk', None, dict(DB_TK, **U11_KARYAWAN), True, 1),
    ('★S10', 'kasir@ membaca tanda kenal', 'kasir', 'get', 'tandaKenal', 'uji-v12-tk', None, DB_TK, False, None),
    ('★S11', 'kasir@ mendaftarkan barcode', 'kasir', 'create', 'tandaKenal', 'uji-v12-tk', TK_UJI, None, False, None),
]
BEDA_V11 = {'★S1', '★S2', '★S3', '★S4', '★S5', '★S9'}   # yang DIBUKA v12 (ditolak v11: bloknya belum ada); kasus lain wajib sama hasilnya di v11
DOK_V12_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v12.md

# ---- MODEL v13 (owner 21 Nov 2026): kasus ★U docs/uji-rules-v13.md — dokumen uji = DB_UJI_V7 (U11 = staf ben) + ubah_db per kasus.
TT_UJI = {'id': 'uji-v13-tt', 'tindakan': 'uangKeluar', 'status': 'menunggu', 'jenis': 'toko', 'nominal': 50000, 'teks': 'Kantong 5 kg', 'dariTempat': 'laci', 'mintaUid': 'uid-uji-b',
          'olehUid': 'uid-uji-b', 'dari': 'Uji', 'peran': 'ben', 'tanggal': '2026-10-09', 'jam': '10:00'}
PS_UJI = {'id': 'uji-v13-ps', 'tindakan': 'pesan', 'status': 'menunggu', 'teks': 'Kantong 5 kg tinggal 20 lembar', 'mintaUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'dari': 'Uji',
          'peran': 'ben', 'tanggal': '2026-10-09', 'jam': '10:00'}
NT_UJI = {'id': 'uji-v13-hp', 'token': 'token-uji', 'perangkat': 'HP uji', 'pada': '2026-10-09T03:00:00.000Z'}
DB_TT = {'persetujuan/uji-v13-tt': TT_UJI}; DB_NT = {'notifOwner/uji-v13-hp': NT_UJI}
WAJIB_V13 = ['★U1', '★U2', '★U3']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V13 = [
    ('★U1', 'owner menyetujui titipan (update status)', 'owner', 'update', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, status='disetujui', diputusTanggal='2026-10-09'), DB_TT, True, 0),
    ('★U2', 'owner menyimpan token notifikasi HP', 'owner', 'create', 'notifOwner', 'uji-v13-hp', NT_UJI, None, True, 0),
    ('★U3', 'owner menghapus token notifikasi', 'owner', 'delete', 'notifOwner', 'uji-v13-hp', None, DB_NT, True, 0),
    ('★U4', 'ben mengirim titipan belanja toko', 'staf', 'create', 'persetujuan', 'uji-v13-tt', TT_UJI, None, True, None),
    ('★U5', 'karyawan mengirim titipan kasbon', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, jenis='kasbon', namaPegawai='Uji', peran='karyawan'), U11_KARYAWAN, True, None),
    ('★U6', 'ben mengirim pesan untuk owner', 'staf', 'create', 'persetujuan', 'uji-v13-ps', PS_UJI, None, True, None),
    ('★U7', 'titipan atas nama akun lain (mintaUid lain)', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, mintaUid='uid-lain'), None, False, None),
    ('★U8', 'titipan yang sudah berstatus disetujui', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, status='disetujui'), None, False, None),
    ('★U9', 'titipan membawa kolom betulan owner', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, koreksiOwner=True), None, False, None),
    ('★U10', 'titipan berjenis ambil pribadi', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, jenis='pribadi'), None, False, None),
    ('★U11', 'titipan bernominal nol', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, nominal=0), None, False, None),
    ('★U12', 'titipan bernominal pecahan', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, nominal=50000.5), None, False, None),
    ('★U13', 'titipan bernominal teks', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, nominal='50000'), None, False, None),
    ('★U14', 'titipan ditulis atas nama penulis lain (olehUid lain)', 'staf', 'create', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, olehUid='uid-lain'), None, False, None),
    ('★U15', 'pesan membawa balasan', 'staf', 'create', 'persetujuan', 'uji-v13-ps', dict(PS_UJI, balasan='Oke'), None, False, None),
    ('★U16', 'pesan kosong', 'staf', 'create', 'persetujuan', 'uji-v13-ps', dict(PS_UJI, teks=''), None, False, None),
    ('★U17', 'pesan 501 huruf', 'staf', 'create', 'persetujuan', 'uji-v13-ps', dict(PS_UJI, teks='x' * 501), None, False, None),
    ('★U18', 'pesan atas nama akun lain', 'staf', 'create', 'persetujuan', 'uji-v13-ps', dict(PS_UJI, mintaUid='uid-lain'), None, False, None),
    ('★U19', 'ben menyetujui titipan sendiri (update)', 'staf', 'update', 'persetujuan', 'uji-v13-tt', dict(TT_UJI, status='disetujui'), DB_TT, False, None),
    ('★U20', 'ben membaca token notifikasi owner', 'staf', 'get', 'notifOwner', 'uji-v13-hp', None, DB_NT, False, None),
    ('★U21', 'ben menulis token notifikasi', 'staf', 'create', 'notifOwner', 'uji-v13-hp', NT_UJI, None, False, None),
    ('★U22', 'kasir@ mengirim titipan', 'kasir', 'create', 'persetujuan', 'uji-v13-tt', TT_UJI, None, False, None),
]
BEDA_V12 = {'★U2', '★U3', '★U4', '★U5', '★U6'}   # yang DIBUKA v13 (ditolak v12); kasus lain wajib sama hasilnya di v12
DOK_V13_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v13.md

# ---- MODEL v14 (owner 21 Nov 2026): kasus ★W docs/uji-rules-v14.md — staf = U11 (ben, uid-uji-b); BERTANDA = U11 + bacaUang true. Dokumen uang uji per kasus.
U11_BACA = {'aksesAkun/uid-uji-b': {'uid': 'uid-uji-b', 'nama': 'UJI B', 'email': 'uji.b@contoh.com', 'peran': 'ben', 'aktif': True, 'bacaUang': True}}
U11_KARYAWAN_BACA = {'aksesAkun/uid-uji-b': {'uid': 'uid-uji-b', 'nama': 'UJI B', 'email': 'uji.b@contoh.com', 'peran': 'karyawan', 'aktif': True, 'bacaUang': True}}
U11_MATI_BACA = {'aksesAkun/uid-uji-b': {'uid': 'uid-uji-b', 'nama': 'UJI B', 'email': 'uji.b@contoh.com', 'peran': 'ben', 'aktif': False, 'bacaUang': True}}
UANG_UJI = {'id': 'uji-v14-u', 'tanggal': '2026-10-09', 'jam': '10:00', 'nominal': 1000, 'keterangan': 'uji'}
def _uang(kol, akun=None): d = {kol + '/uji-v14-u': dict(UANG_UJI)}; d.update(akun if akun is not None else U11_BACA); return d
WAJIB_V14 = ['★W1', '★W2', '★W3']   # owner saja (dokumen titikKas NYATA; staf butuh aksesAkun uji bertanda → dibuktikan emulator)
KASUS_V14 = [
    ('★W1', 'owner membaca uang keluar harian', 'owner', 'get', 'pengeluaranHarian', 'uji-v14-u', None, _uang('pengeluaranHarian', {}), True, 0),
    ('★W2', 'owner membaca titik kas', 'owner', 'get', 'pengaturan', 'titikKas', None, None, True, 0),
    ('★W3', 'owner membaca tutup hari', 'owner', 'get', 'tutupHari', 'uji-v14-u', None, _uang('tutupHari', {}), True, 0),
] + [('★W%d' % (4 + i), 'akun tablet bertanda membaca ' + kol, 'staf', 'get', kol, 'uji-v14-u', None, _uang(kol), True, 1) for i, kol in enumerate(BACA_UANG_V14)] + [
    ('★W14', 'akun tablet bertanda membaca titik kas', 'staf', 'get', 'pengaturan', 'titikKas', None, U11_BACA, True, 1),
    ('★W15', 'Penjaga laci TANPA tanda membaca uang keluar harian', 'staf', 'get', 'pengeluaranHarian', 'uji-v14-u', None, _uang('pengeluaranHarian', {}), False, None),
    ('★W16', 'karyawan bertanda membaca uang keluar harian', 'staf', 'get', 'pengeluaranHarian', 'uji-v14-u', None, _uang('pengeluaranHarian', U11_KARYAWAN_BACA), False, None),
    ('★W17', 'akun bertanda yang dinonaktifkan membaca uang keluar harian', 'staf', 'get', 'pengeluaranHarian', 'uji-v14-u', None, _uang('pengeluaranHarian', U11_MATI_BACA), False, None),
    ('★W18', 'akun bertanda MENULIS uang keluar harian', 'staf', 'create', 'pengeluaranHarian', 'uji-v14-u', dict(UANG_UJI, olehUid='uid-uji-b'), U11_BACA, False, None),
    ('★W19', 'akun bertanda mengubah titik kas', 'staf', 'update', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2026-10-08', 'laci': 999}, U11_BACA, False, None),
    ('★W20', 'akun bertanda membaca pengaturan keamanan', 'staf', 'get', 'pengaturan', 'keamanan', None, U11_BACA, False, None),
    ('★W21', 'akun bertanda membaca slip upah (bukan bagian laci)', 'staf', 'get', 'slipUpah', 'uji-v14-u', None, _uang('slipUpah'), False, None),
    ('★W22', 'kasir@ membaca uang keluar harian', 'kasir', 'get', 'pengeluaranHarian', 'uji-v14-u', None, _uang('pengeluaranHarian', {}), False, None),
]
BEDA_V13 = set('★W%d' % i for i in range(4, 15))   # yang DIBUKA v14 (ditolak v13); kasus lain wajib sama hasilnya di v13
DOK_V14_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v14.md

# ---- MODEL v15 (owner 22 Nov 2026): kasus ★X docs/uji-rules-v15.md — staf = U11 (ben, uid-uji-b). Kedatangan tablet = bon, bongkar 0, bertanda dariTablet.
BM_TABLET = {'id': 'uji-v15-bm', 'tanggal': '2026-10-09', 'jam': '10:00', 'pemasok': 'Pemasok Uji', 'caraBayar': 'utang', 'biayaBongkar': 0, 'dariTablet': True,
             'merkList': [{'id': '1', 'merk': 'Beras Uji', 'satuan': 'karung', 'jumlahKarung': 2, 'beratKarung': 50, 'totalKg': 100, 'hargaPerKg': 12000, 'subtotalHarga': 1200000}],
             'oleh': 'Uji', 'olehUid': 'uid-uji-b'}
BM_OWNER = dict(BM_TABLET, id='uji-v15-bo', caraBayar='tunai', biayaBongkar=50000, olehUid='uid-uji'); del BM_OWNER['dariTablet']
TT_BONGKAR = dict(TT_UJI, id='uji-v15-tb', jenis='bongkar', nominal=50000, teks='Upah bongkar · Pemasok Uji', batchId='uji-v15-bm')
TT_SUPIR = dict(TT_UJI, id='uji-v15-ts', jenis='bayarBon', nominal=500000, teks='Bayar supir · Pemasok Uji', pemasok='Pemasok Uji', batchId='uji-v15-bm')
KB_UJI = {'id': 'uji-v15-kb', 'tindakan': 'barangMasuk', 'status': 'menunggu', 'batchId': 'uji-v15-bm', 'teks': 'Pemasok Uji · 2 karung · Rp1.200.000', 'nominal': 1200000,
          'mintaUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'dari': 'Uji', 'peran': 'ben', 'tanggal': '2026-10-09', 'jam': '10:00'}
UP_TITIP = {'id': 'uji-v15-up', 'tanggal': '2026-10-09', 'jam': '10:00', 'tipe': 'bayar', 'pemasok': 'Pemasok Uji', 'nominal': 500000, 'bonId': 'uji-v15-bm', 'bonTanggal': '2026-10-09',
            'dari': 'laci', 'catatan': 'Bayar lewat supir', 'dariPersetujuan': 'uji-v15-ts'}
DB_TS = {'persetujuan/uji-v15-ts': TT_SUPIR}; DB_BM = {'batchMasuk/uji-v15-bm': BM_TABLET}
WAJIB_V15 = ['★X1', '★X2', '★X3']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V15 = [
    ('★X1', 'owner mencatat kedatangan biasa (tunai + upah bongkar)', 'owner', 'create', 'batchMasuk', 'uji-v15-bo', BM_OWNER, None, True, 0),
    ('★X2', 'owner menyetujui titipan bayar supir (update status)', 'owner', 'update', 'persetujuan', 'uji-v15-ts', dict(TT_SUPIR, status='disetujui', diputusTanggal='2026-10-09'), DB_TS, True, 0),
    ('★X3', 'owner mencatat bayar bon dari titipan (dari laci)', 'owner', 'create', 'utangPemasokMutasi', 'uji-v15-up', UP_TITIP, None, True, 0),
    ('★X4', 'Penjaga laci mencatat kedatangan dari tablet (bon)', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', BM_TABLET, None, True, None),
    ('★X5', 'Penjaga laci menitip upah bongkar kedatangan itu', 'staf', 'create', 'persetujuan', 'uji-v15-tb', TT_BONGKAR, None, True, None),
    ('★X6', 'Penjaga laci menitip bayar ke supir', 'staf', 'create', 'persetujuan', 'uji-v15-ts', TT_SUPIR, None, True, None),
    ('★X7', 'Penjaga laci mengirim kabar barang masuk', 'staf', 'create', 'persetujuan', 'uji-v15-kb', KB_UJI, None, True, None),
    ('★X8', 'karyawan mencatat kedatangan dari tablet', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', BM_TABLET, U11_KARYAWAN, False, None),
    ('★X9', 'kedatangan tablet dibayar TUNAI', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, caraBayar='tunai'), None, False, None),
    ('★X10', 'kedatangan tablet membawa upah bongkar', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, biayaBongkar=50000), None, False, None),
    ('★X11', 'kedatangan tanpa tanda dariTablet', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict((k, v) for k, v in BM_TABLET.items() if k != 'dariTablet'), None, False, None),
    ('★X12', 'kedatangan tablet berpemasok LAHIR BUKU', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, pemasok='LAHIR BUKU'), None, False, None),
    ('★X13', 'kedatangan tablet tanpa baris barang', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, merkList=[]), None, False, None),
    ('★X14', 'kedatangan tablet membawa kolom koreksi owner', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, riwayat=[{'teks': 'x'}]), None, False, None),
    ('★X15', 'kedatangan tablet bertanggal bulan yang sudah lewat tenggang', 'staf', 'create', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, tanggal='2026-08-20'), None, False, None),
    ('★X16', 'Penjaga laci mengubah kedatangan (menulis upah bongkar sendiri)', 'staf', 'update', 'batchMasuk', 'uji-v15-bm', dict(BM_TABLET, biayaBongkar=50000), DB_BM, False, None),
    ('★X17', 'titipan upah bongkar tanpa kedatangan', 'staf', 'create', 'persetujuan', 'uji-v15-tb', dict((k, v) for k, v in TT_BONGKAR.items() if k != 'batchId'), None, False, None),
    ('★X18', 'titipan bayar supir tanpa nama pemasok', 'staf', 'create', 'persetujuan', 'uji-v15-ts', dict(TT_SUPIR, pemasok=''), None, False, None),
    ('★X19', 'kabar barang masuk tanpa kedatangan', 'staf', 'create', 'persetujuan', 'uji-v15-kb', dict((k, v) for k, v in KB_UJI.items() if k != 'batchId'), None, False, None),
    ('★X20', 'kabar barang masuk yang sudah diputus', 'staf', 'create', 'persetujuan', 'uji-v15-kb', dict(KB_UJI, status='dibaca', diputusTanggal='2026-10-09'), None, False, None),
    ('★X21', 'Penjaga laci menulis pembayaran bon pemasok sendiri', 'staf', 'create', 'utangPemasokMutasi', 'uji-v15-up', dict(UP_TITIP, olehUid='uid-uji-b'), None, False, None),
    ('★X22', 'kasir@ mencatat kedatangan', 'kasir', 'create', 'batchMasuk', 'uji-v15-bm', BM_TABLET, None, False, None),
    ('★X23', 'karyawan mengirim kabar barang masuk', 'staf', 'create', 'persetujuan', 'uji-v15-kb', dict(KB_UJI, peran='karyawan'), U11_KARYAWAN, False, None),
]
BEDA_V14 = {'★X4', '★X5', '★X6', '★X7'}   # yang DIBUKA v15 (ditolak v14); kasus lain wajib sama hasilnya di v14
DOK_V15_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v15.md
# ---- MODEL v16 (owner 22 Nov 2026): kasus ★Y docs/uji-rules-v16.md — staf = U11 (ben, uid-uji-b). Hitungan laci tablet = menunggu, bulat, brankas ≤ hitungan.
HL_UJI = {'id': 'uji-v16-hl', 'tindakan': 'hitungLaci', 'status': 'menunggu', 'tanggal': '2026-10-09', 'jam': '21:00', 'tanggalTulis': '2026-10-09', 'hitung': 607500, 'amankan': 415000,
          'lembar': {'100000': 5, '50000': 2, '2000': 3}, 'receh': 1500, 'kembalian': 192500, 'mintaUid': 'uid-uji-b', 'olehUid': 'uid-uji-b', 'dari': 'Uji', 'peran': 'ben'}
AT_TUTUP = {'id': 'tutupHari', 'tanggal': '2026-10-01', 'jam': '09:00', 'persenSisih': 50, 'kembalian': 192500, 'maafSelisih': 5000, 'alasan': ['Belum tahu']}
TH_UJI = {'id': '2026-10-09', 'tanggal': '2026-10-09', 'jam': '22:00', 'omzet': 0, 'kasFisikLaci': 607500, 'selisih': 0, 'alasanSelisih': '', 'setoranOwner': 0, 'kasAwalBesokLaci': 192500, 'sistemBaru': True}
DB_HL = {'persetujuan/uji-v16-hl': HL_UJI}; DB_AT = {'aturanToko/tutupHari': AT_TUTUP}
WAJIB_V16 = ['★Y1', '★Y2', '★Y3']   # owner saja (tanpa dokumen uji staf); kasus staf dibuktikan emulator — boleh juga di Playground dengan U11
KASUS_V16 = [
    ('★Y1', 'owner menutup hari (tutupHari baru)', 'owner', 'create', 'tutupHari', '2026-10-09', TH_UJI, None, True, 0),
    ('★Y2', 'owner menandai hitungan tablet disetujui (update status)', 'owner', 'update', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, status='disetujui', diputusTanggal='2026-10-09', tutupJam='22:00'), DB_HL, True, 0),
    ('★Y3', 'owner menyimpan aturan tutup hari', 'owner', 'update', 'aturanToko', 'tutupHari', dict(AT_TUTUP, kembalian=200000), DB_AT, True, 0),
    ('★Y4', 'Penjaga laci mengirim hitungan laci', 'staf', 'create', 'persetujuan', 'uji-v16-hl', HL_UJI, None, True, None),
    ('★Y5', 'Penjaga laci membaca aturan tutup hari (uang kembalian)', 'staf', 'get', 'aturanToko', 'tutupHari', None, DB_AT, True, None),
    ('★Y6', 'karyawan mengirim hitungan laci', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, peran='karyawan'), U11_KARYAWAN, False, None),
    ('★Y7', 'karyawan membaca aturan tutup hari', 'staf', 'get', 'aturanToko', 'tutupHari', None, dict(DB_AT, **U11_KARYAWAN), False, None),
    ('★Y8', 'hitungan laci nol', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, hitung=0, amankan=0), None, False, None),
    ('★Y9', 'yang dipindah ke brankas lebih besar dari hitungan', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, amankan=700000), None, False, None),
    ('★Y10', 'hitungan rupiah pecahan', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, hitung=607500.5), None, False, None),
    ('★Y11', 'hitungan tanpa kolom brankas', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict((k, v) for k, v in HL_UJI.items() if k != 'amankan'), None, False, None),
    ('★Y12', 'hitungan yang sudah diputus', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, status='disetujui', diputusTanggal='2026-10-09'), None, False, None),
    ('★Y13', 'hitungan atas nama orang lain', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, mintaUid='uid-lain'), None, False, None),
    ('★Y14', 'hitungan bertanggal bulan yang sudah lewat tenggang', 'staf', 'create', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, tanggal='2026-08-20'), None, False, None),
    ('★Y15', 'Penjaga laci memutus hitungannya sendiri', 'staf', 'update', 'persetujuan', 'uji-v16-hl', dict(HL_UJI, status='disetujui', diputusTanggal='2026-10-09'), DB_HL, False, None),
    ('★Y16', 'Penjaga laci menutup hari sendiri (tutupHari)', 'staf', 'create', 'tutupHari', '2026-10-09', dict(TH_UJI, olehUid='uid-uji-b'), None, False, None),
    ('★Y17', 'Penjaga laci memajukan titik kas', 'staf', 'update', 'pengaturan', 'titikKas', {'id': 'titikKas', 'tanggal': '2026-10-09', 'laci': 192500, 'olehUid': 'uid-uji-b'}, None, False, None),
    ('★Y18', 'Penjaga laci mengubah aturan tutup hari', 'staf', 'update', 'aturanToko', 'tutupHari', dict(AT_TUTUP, kembalian=0, olehUid='uid-uji-b'), DB_AT, False, None),
    ('★Y19', 'kasir@ mengirim hitungan laci', 'kasir', 'create', 'persetujuan', 'uji-v16-hl', HL_UJI, None, False, None),
]
BEDA_V15 = {'★Y4', '★Y5'}   # yang DIBUKA v16 (ditolak v15); kasus lain wajib sama hasilnya di v15
DOK_V16_TEKS = None   # kontrol: pengganti isi docs/uji-rules-v16.md


def periksa(rules, koleksi_js, akses_js):
    cacat = []
    rules = tanpa_komentar(rules)
    r15, c16 = ke_v15(rules)       # 20 · v16 → v15 (cabut balik dua ubahan & satu fungsi v16)
    cacat += periksa_v16(rules, r15, c16, akses_js)
    r14, c15 = ke_v14(r15)         # 19 · v15 → v14 (cabut balik tiga ubahan & dua fungsi v15)
    cacat += periksa_v15(r15, r14, c15, akses_js)
    r13, c14 = ke_v13(r14)         # 18 · v14 → v13 (cabut balik sebelas baris baca & dua fungsi v14)
    cacat += periksa_v14(r14, r13, c14, akses_js)
    r12, c13 = ke_v12(r13)         # 17 · v13 → v12 (cabut balik satu ubahan, satu blok & dua fungsi v13)
    cacat += periksa_v13(r13, r12, c13, akses_js)
    r11, c12 = ke_v11(r12)         # 16 · v12 → v11 (cabut balik satu blok v12)
    cacat += periksa_v12(r12, r11, c12)
    r10, c11 = ke_v10(r11)         # 15 · v11 → v10 (cabut balik tiga ubahan & tiga fungsi v11)
    cacat += periksa_v11(r11, r10, c11, akses_js)
    r9, c10 = ke_v9(r10)           # 14 · v10 → v9 (cabut balik dua blok & tiga fungsi v10)
    cacat += periksa_v10(r10, r9, c10, akses_js)
    r8, c9 = ke_v8(r9)             # 13 · v9 → v8 (cabut balik satu ubahan v9)
    cacat += periksa_v9(r9, r8, c9)
    r7, c8 = ke_v7(r8)             # 12 · v8 → v7 (cabut balik tiga ubahan v8)
    cacat += periksa_v8(r8, r7, c8)
    cacat += periksa_v7(r7)        # 10 · semua pemeriksa v7 atas hasil cabut-balik (v8 tidak mengubah apa pun selain tiga ubahannya)
    KOL = re.findall(r"\{ nama: '(\w+)',", koleksi_js); B = blok_rules(rules); F = fungsi_rules(rules)
    BACA = daftar_js(akses_js, 'BACA_STAF') or []; DOK = peta_js(akses_js, 'DOK_STAF') or {}; BUAT = peta_js(akses_js, 'BUAT_STAF') or {}
    KREDIT = daftar_js(akses_js, 'KREDIT_STAF') or []
    UBAH = dict((k, re.findall(r"'(\w+)'", v)) for k, v in re.findall(r"(\w+): \{ peran: \[([^\]]*)\]", (re.search(r'export const UBAH_STAF = \{(.*?)\n\};', akses_js, re.S) or re.search('', '')).group(0)))
    # 1 · blok per koleksi
    for n in KOL + ['aksesAkun', 'permintaanAkses', 'arsipTahun']:
        if n not in B: cacat.append('koleksi tanpa blok match sendiri: ' + n)
    for n in B:
        if n not in KOL and n not in LUAR_KOLEKSI: cacat.append('blok rules untuk koleksi yang tidak dikenal (bukan koleksi.js, bukan LUAR_KOLEKSI): ' + n)
    # 2 · owner via email, tidak ada masuk() telanjang
    if not re.search(r"function owner\(\) \{\s*return masuk\(\) && request\.auth\.token\.email == '" + re.escape(EMAIL_OWNER) + r"';\s*\}", rules): cacat.append('owner() tidak lagi berbasis email owner')
    if not re.search(r"function kasir\(\) \{\s*return masuk\(\) && request\.auth\.token\.email == '" + re.escape(EMAIL_KASIR) + r"';\s*\}", rules): cacat.append('kasir() tidak lagi berbasis email kasir@')
    for n, b in B.items():
        for x in re.finditer(r'allow [a-z, ]+: if (.*?);', b, re.S):
            k = re.sub(r'\s+', ' ', x.group(1))
            if re.search(r'(^|\|\| )masuk\(\)( \|\||$)', k): cacat.append(n + ': allow memakai masuk() saja (siapa pun yang login): ' + k)
    # 3 · jalur kasir@ — v7: kasir darurat SAJA (nota penjualan + kirim ulangnya, denyut, katalog); kasir() di tempat lain = hak kasir.html yang pensiun
    if not any('kasir()' in x for x in allow(B.get('penjualan', ''), 'create')): cacat.append('jalur kasir@ hilang: create penjualan (kasir darurat)')
    if not any('kasir() && tulisUlangSama()' in x for x in allow(B.get('penjualan', ''), 'update')): cacat.append('jalur kasir@ hilang: tulis-ulang-sama penjualan')
    for op in ('create', 'update'):
        if not any('kasir()' in x for x in allow(B.get('perangkatStatus', ''), op)): cacat.append('jalur kasir@ hilang: denyut perangkatStatus (' + op + ')')
    if not any('kasir()' in x for x in allow(B.get('ringkasanKasir', ''), 'read')): cacat.append('jalur kasir@ hilang: baca ringkasanKasir')
    for n, b in B.items():
        for op in OPERASI:
            if (n, op) in KASIR_BOLEH: continue
            if any(re.search(r'(?<!!)\bkasir\(\)', x) for x in allow(b, op)): cacat.append('kasir@ masih punya hak %s di %s — v7 mencabut jalur kasir.html (kasir darurat hanya nota, denyut, katalog)' % (op, n))
    if 'tulisUlangSama' in F and 'masuk()' in F['tulisUlangSama']: cacat.append('tulisUlangSama() masih membuka untuk siapa pun yang login (v2) — harus lewat kasir()')
    # 4 · tulis bukan-owner wajib jujur; tidak ada delete bukan-owner
    if 'jujur()' not in F.get('stafBuat', '') or 'request.resource.data.olehUid == request.auth.uid' not in F.get('jujur', ''): cacat.append('stafBuat() tidak memeriksa olehUid (jujur)')
    if 'stafBuat(' not in F.get('stafBuatTipe', ''): cacat.append('stafBuatTipe() tidak lewat stafBuat()')
    if 'jujur()' not in F.get('stafBuatJual', ''): cacat.append('stafBuatJual() tidak memeriksa olehUid')
    if 'stafBuat(' not in F.get('stafJejak', ''): cacat.append('stafJejak() tidak lewat stafBuat()')
    if 'diubahOlehUid == request.auth.uid' not in F.get('stafUbahPesanan', '') or 'affectedKeys().hasOnly(' not in F.get('stafUbahPesanan', ''): cacat.append('stafUbahPesanan() tanpa uid pengubah / tanpa batas kolom')
    if 'akunUid == request.auth.uid' not in F.get('stafDenyut', '') or 'keys().hasOnly(' not in F.get('stafDenyut', ''): cacat.append('stafDenyut() tanpa uid / tanpa batas kolom')
    if 'aktifDengan(' not in F.get('staf', '') or "a.aktif == true" not in F.get('aktifDengan', ''): cacat.append('staf() tidak memeriksa aktif & peran')
    for n, b in B.items():
        for op in ('create', 'update'):
            for x in allow(b, op):
                pakai = set(re.findall(r'\b(staf\w*)\(', x))
                if pakai and not pakai <= FUNGSI_JUJUR: cacat.append(n + ': ' + op + ' bukan-owner lewat fungsi tanpa uid penulis: ' + ', '.join(sorted(pakai - FUNGSI_JUJUR)))
        for x in allow(b, 'delete'):
            k = re.sub(r'\s+', ' ', x).strip()
            if not (k == 'if owner()' or k.startswith('if owner() && ')) or re.search(r'\b(staf\w*|kasir|masuk)\(', k): cacat.append(n + ': delete bukan hanya owner: ' + x)
    if [re.sub(r'\s+', ' ', x).strip() for x in allow(B.get('arsipTahun', ''), 'read')] != ['if owner()']: cacat.append('arsipTahun bukan owner saja')
    # 7 · tanpa payung (putaran 25): tidak ada match rekursif yang memberi tulis, tidak ada wildcard koleksi
    for m in re.finditer(r'\n(\s*)match (/[^\n{]*(?:\{[^}\n]*\}[^\n{]*)*)\{', rules):
        jalur = m.group(2).strip()
        if re.search(r'=\*\*\}', jalur):
            i = m.end(); d = 1
            while i < len(rules) and d: d += {'{': 1, '}': -1}.get(rules[i], 0); i += 1
            isi = rules[m.end():i]
            if re.search(r'allow [a-z, ]*(write|create|update|delete)', isi): cacat.append('match rekursif memberi izin tulis (payung): ' + jalur)
            else: cacat.append('match rekursif (bentuk payung) di rules: ' + jalur)
        elif re.match(r'^/\{\w+\}/', jalur): cacat.append('wildcard koleksi: ' + jalur)
    cacat += periksa_kunci(rules, B, F)
    cacat += periksa_buku(rules, B)
    cacat += periksa_pintu(rules)
    # 5 · daftar peran sama dengan akses.js
    peran_txt = "['ben', 'karyawan']"
    for n in KOL:
        b = B.get(n, ''); baca_staf = any("staf(" + peran_txt + ")" in x for x in allow(b, 'read'))
        if n in BACA and not baca_staf: cacat.append('akses.js BACA_STAF memuat ' + n + ' tapi rules tidak membuka bacanya untuk ben/karyawan')
        if n not in BACA and n not in DOK and baca_staf: cacat.append('rules membuka baca ' + n + ' untuk bukan-owner, akses.js BACA_STAF tidak')
        buat = [x for x in allow(b, 'create') if re.search(r'\bstaf\w*\(', x)]
        peran_buat = '[' + ', '.join("'%s'" % x for x in (BUAT.get(n) or [])) + ']'   # v10: surat jalan dibuat ben saja (BUAT_STAF suratJalan ['ben'])
        if n in BUAT and not any(peran_buat in x for x in buat): cacat.append('akses.js BUAT_STAF memuat ' + n + ' tapi rules tidak membuka create-nya untuk ' + peran_buat)
        if n not in BUAT and buat: cacat.append('rules membuka create ' + n + ' untuk bukan-owner, akses.js BUAT_STAF tidak')
        ubah = [x for x in allow(b, 'update') if re.search(r'\bstaf\w*\(', x)]
        if n in UBAH and not ubah: cacat.append('akses.js UBAH_STAF memuat ' + n + ' tapi rules tidak membuka update-nya')
        if n not in UBAH and ubah: cacat.append('rules membuka update ' + n + ' untuk bukan-owner, akses.js UBAH_STAF tidak')
    m = re.search(r"id in \[([^\]]*)\] && staf", B.get('aturanToko', ''))
    if not m or re.findall(r"'(\w+)'", m.group(1)) != DOK.get('aturanToko'): cacat.append('dokumen aturanToko yang dibaca bukan-owner beda dengan akses.js DOK_STAF')
    if "id == '" + (DOK.get('pengaturan') or ['?'])[0] + "' && staf(" not in B.get('pengaturan', ''): cacat.append('dokumen pengaturan yang dibaca bukan-owner beda dengan akses.js DOK_STAF')
    if "stafBuatJual(" + peran_txt + ", [" + ', '.join("'%s'" % x for x in KREDIT) + "])" not in B.get('penjualan', ''): cacat.append('peran jual Kredit di rules beda dengan akses.js KREDIT_STAF')
    # putaran 23c: daftar dokumen di baris jejak dibatasi SAMA dengan pagar perangkat akses.js (BATAS_ACCESS_CALL − CADANGAN − 1 jejak)
    fa = re.search(r'export const BATAS_ACCESS_CALL = (\d+);', akses_js); ca = re.search(r'export const CADANGAN_ACCESS_CALL = (\d+);', akses_js)
    mj = re.search(r'd\.dokumen\.size\(\) <= (\d+)', F.get('stafJejak', ''))
    if not (fa and ca and mj) or int(mj.group(1)) != int(fa.group(1)) - int(ca.group(1)) - 1 or int(fa.group(1)) - int(ca.group(1)) > 18:
        cacat.append('stafJejak(): batas dokumen per kiriman (%s) beda dengan pagar akses.js (%s − %s − 1 jejak), atau pagarnya > 18' % (mj and mj.group(1), fa and fa.group(1), ca and ca.group(1)))
    # 6 · aksesAkun tak pernah owner
    ak = B.get('aksesAkun', '')
    if "request.resource.data.peran in ['ben', 'karyawan']" not in ak or 'owner' in re.sub(r'owner\(\)', '', ak): cacat.append('aksesAkun bisa memberi peran selain ben/karyawan (atau menyebut owner)')
    if not any(re.sub(r'\s+', ' ', x).strip().startswith('if owner() &&') for x in allow(ak, 'create')): cacat.append('aksesAkun bisa ditulis selain owner')
    pa = B.get('permintaanAkses', '')
    if 'request.auth.uid == uid' not in pa or '!exists(/databases/$(database)/documents/aksesAkun/$(uid))' not in pa or '!kasir()' not in pa: cacat.append('permintaanAkses: create bukan milik uid sendiri / boleh walau sudah terdaftar / kasir@ boleh')
    return cacat


if __name__ == '__main__':
    R = baca('firestore.rules'); K = baca('baru/js/data/koleksi.js'); A = baca('baru/js/data/akses.js')
    if '--kontrol' in sys.argv:
        rusak = {
            'satu koleksi tanpa blok sendiri': R.replace('    match /karantina/{id} {', '    match /karantinaX/{id} {'),
            'owner lewat dokumen, bukan email': R.replace("return masuk() && request.auth.token.email == 'owner@tokoberasmiqbal.web.app';", "return masuk() && akun().peran == 'owner';"),
            'jalur kasir@ penjualan hilang': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (stafBuatJual(", "allow create: if (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (stafBuatJual("),
            'jalur kasir@ dibuka lagi untuk siapa pun (v2)': R.replace("    function tulisUlangSama() {\n      return request.resource.data == resource.data;", "    function tulisUlangSama() {\n      return masuk() && request.resource.data == resource.data;"),
            'tulisan bukan-owner tanpa olehUid': R.replace("function stafBuat(peranBoleh) { return masuk() && aktifDengan(akun(), peranBoleh) && jujur(); }", "function stafBuat(peranBoleh) { return masuk() && aktifDengan(akun(), peranBoleh); }"),
            'siapa pun yang login boleh menjual': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (stafBuatJual(", "allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || masuk() || (stafBuatJual("),
            'bukan-owner boleh hapus': R.replace("    match /strukKeluar/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();",
                                                  "    match /strukKeluar/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update: if owner();\n      allow delete: if owner() || staf(['ben', 'karyawan']);"),
            'karyawan membaca koleksi uang': R.replace("    match /pengeluaranHarian/{id} {\n      allow read: if owner() || stafBacaUang();", "    match /pengeluaranHarian/{id} {\n      allow read: if owner() || stafBacaUang() || staf(['ben', 'karyawan']);"),   # v14: baris baca uang bertanda
            # putaran 23e: payung tidak boleh mengalahkan batasan owner
            # putaran 25 — tanpa payung & kunci periode
            'payung owner dikembalikan (mengalahkan kunci periode)': R.replace("    match /ringkasanKasir/{id} {", "    match /{document=**} {\n      allow read, write: if owner();\n    }\n    match /ringkasanKasir/{id} {"),
            'payung v3 dikembalikan': R.replace("    match /ringkasanKasir/{id} {", "    match /{koleksi}/{sisa=**} {\n      allow read, write: if owner() && !(koleksi in ['aksesAkun', 'permintaanAkses']);\n    }\n    match /ringkasanKasir/{id} {"),
            'kunci dicabut dari create retur': R.replace("    match /retur/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if (owner() && tglBaru('tanggal')) ||", "    match /retur/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() ||"),
            'hapus nota tanpa kunci': R.replace("      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('penjualan', id, bulanDok(resource.data, 'tanggal')));\n    }\n\n    match /produksiKemasan/{id} {", "      allow delete: if owner();\n    }\n\n    match /produksiKemasan/{id} {"),
            'koreksi di tempat pada bulan terkunci lolos (update hanya menilai tanggal baru)': R.replace("function tglUbah(f) { return tulisUlangSama() || bolehBulan(lebihTua(bulanDok(request.resource.data, f), bulanDok(resource.data, f))); }", "function tglUbah(f) { return tulisUlangSama() || bolehBulan(bulanDok(request.resource.data, f)); }"),
            'kasir@ create tanpa kunci': R.replace("allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (stafBuatJual(", "allow create: if (owner() && tglBaru('tanggal')) || kasir() || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (stafBuatJual("),
            'bukan-owner membaca dokumen kunci (2 access call per dokumen)': R.replace("function tglStaf(f) { return bebas(bulanDok(request.resource.data, f)); }", "function tglStaf(f) { return bolehBulan(bulanDok(request.resource.data, f)); }"),
            'bukan-owner tanpa penilaian tanggal': R.replace("(stafBuatTipe(['ben', 'karyawan'], 'pakai') && tglStaf('tanggal'));   // bukan beli\n      allow update: if owner() && tglUbah('tanggal');", "stafBuatTipe(['ben', 'karyawan'], 'pakai');   // bukan beli\n      allow update: if owner() && tglUbah('tanggal');"),
            'get() kunci selalu dipanggil (let di bolehBulan)': R.replace("function bolehBulan(b) { return bebas(b) || !terkunci(b); }", "function bolehBulan(b) { let k = terkunci(b); return bebas(b) || !k; }"),
            'get() kunci kedua di luar terkunci()': R.replace("function bolehBulan(b) { return bebas(b) || !terkunci(b); }", "function bolehBulan(b) { return bebas(b) || !terkunci(b); }\n    function sudahDikunci() { return exists(/databases/$(database)/documents/aturanToko/kunciPeriode); }"),
            'tenggang minimal 0 (bulan lalu bisa dikunci tanggal 1)': R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 0; }"),
            'tenggang minimal kembali 1 di rules saja (beda dengan kunci-periode.js)': R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 1; }"),
            'kasir@ boleh menghapus nota (dengan kunci pun)': R.replace("      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('penjualan', id, bulanDok(resource.data, 'tanggal')));\n    }\n\n    match /produksiKemasan/{id} {", "      allow delete: if (owner() || kasir()) && tglLama('tanggal');\n    }\n\n    match /produksiKemasan/{id} {"),
            'kasir@ boleh mengubah nota asal bulannya terbuka (bukan hanya tulis-ulang identik)': R.replace("allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama()) || (kasir() && ulangKasirBercap());", "allow update: if (owner() && tglUbah('tanggal')) || (kasir() && (tulisUlangSama() || tglUbah('tanggal'))) || (kasir() && ulangKasirBercap());", 1),
            'kasir@ boleh mengubah nota (bukan tulis-ulang identik)': R.replace("allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama()) || (kasir() && ulangKasirBercap());", "allow update: if ((owner() || kasir()) && tglUbah('tanggal')) || (kasir() && ulangKasirBercap());", 1),
            'bulan berjalan bisa dikunci': R.replace("function bolehDikunci(b) { return b < bulanIni() - 1 || (b == bulanIni() - 1 && wib().day() > tenggangMin()); }", "function bolehDikunci(b) { return b < bulanIni(); }"),
            'WIB dihitung sebagai UTC': R.replace("timestamp.value(request.time.toMillis() + 25200000)", "timestamp.value(request.time.toMillis())"),
            'kunci boleh melompati bulan': R.replace("bulanDari(d.sampaiBulan) == bulanDari(s0) + 1", "bulanDari(d.sampaiBulan) > bulanDari(s0)"),
            'buka dua bulan sekaligus': R.replace("bulanDari(d.sampaiBulan) == bulanDari(s0) - 1", "bulanDari(d.sampaiBulan) < bulanDari(s0)"),
            'buka tanpa alasan': R.replace("\n              && d.riwayat[lama.size()].alasan is string && d.riwayat[lama.size()].alasan.size() >= 10));", "));"),
            'riwayat kunci boleh ditulis ulang': R.replace("(lama.size() == 0 || d.riwayat[0:lama.size()] == lama) && ", ""),
            'irisan riwayat tanpa penjaga kosong (galat Index -1 di server)': R.replace("(lama.size() == 0 || d.riwayat[0:lama.size()] == lama)", "d.riwayat[0:lama.size()] == lama"),
            'dokumen kunci bisa dihapus': R.replace("allow delete: if owner() && id != 'kunciPeriode';", "allow delete: if owner();"),
            'pajakSetoran ikut dikunci (melawan K6)': R.replace("    match /pajakSetoran/{id} {\n      allow read, write: if owner();", "    match /pajakSetoran/{id} {\n      allow read: if owner();\n      allow create: if owner() && tglBaru('tanggalSetor');\n      allow update, delete: if owner();"),
            'bon lama pemasok dinilai tanggal catat (melawan K4)': R.replace("function bulanUP(d) { return d.get('tipe', '') == 'saldoAwal' ? bulanNilai(d.get('bonTanggal', null)) : bulanDok(d, 'tanggal'); }", "function bulanUP(d) { return bulanDok(d, 'tanggal'); }"),
            'hapus dokumen yang tidak ada ditolak (batch hapus adukan gagal)': R.replace("function tglLama(f) { return resource == null || bolehBulan(bulanDok(resource.data, f)); }", "function tglLama(f) { return bolehBulan(bulanDok(resource.data, f)); }"),
            'titik kas tanpa kunci': R.replace("allow create, update: if owner() && (id != 'titikKas' || tglBaru('tanggal') || pintuTitik()) &&", "allow create, update: if owner() &&"),
            'wildcard koleksi tambahan di tengah': R.replace("    match /bukuHapus/{id} {", "    match /{apaSaja}/{id} {\n      allow read: if owner();\n    }\n    match /bukuHapus/{id} {"),
            'setelan upah ikut terbaca bukan-owner': R.replace("'hargaTingkat', 'produkArsip'] && staf(", "'hargaTingkat', 'produkArsip', 'upah'] && staf("),
            'aksesAkun bisa memberi owner': R.replace("request.resource.data.peran in ['ben', 'karyawan'] && request.resource.data.aktif is bool", "request.resource.data.peran in ['ben', 'karyawan', 'owner'] && request.resource.data.aktif is bool"),
            'update pesanan tanpa batas kolom': R.replace("&& request.resource.data.diff(resource.data).affectedKeys().hasOnly(['status', 'riwayatStatus', 'trxIdJual', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada']);", ";"),
            'karyawan boleh jual Kredit di rules': R.replace("stafBuatJual(['ben', 'karyawan'], ['ben'])", "stafBuatJual(['ben', 'karyawan'], ['ben', 'karyawan'])"),
            'arsipTahun dibuka': R.replace("allow read: if owner();   // arsip tutup buku: owner saja", "allow read: if owner() || staf(['ben', 'karyawan']);   // arsip tutup buku: owner saja"),
            'permintaanAkses boleh walau sudah terdaftar': R.replace("  && !exists(/databases/$(database)/documents/aksesAkun/$(uid))\n", ""),
            'jejak bukan-owner boleh 19 dokumen (batas lama, tanpa sisa)': R.replace("d.dokumen.size() <= 17;", "d.dokumen.size() <= 19;"),
            'create lewat staf() tanpa uid': R.replace("(stafBuat(['ben', 'karyawan']) && tglStaf('tanggal'));   // adukan", "(staf(['ben', 'karyawan']) && tglStaf('tanggal'));   // adukan"),
            # 9 · v6 berita acara tutup buku hanya maju — penjaga dicabut (kiriman telat lolos) ATAU terlalu ketat (tulisan sah dari kode ditolak)
            'v6 dicabut: berita acara kembali owner saja tanpa urutan (v5)': re.sub(r"(    match /tutupBukuAcara/\{id\} \{\n).*?(\n    \})", lambda m: m.group(1) + "      allow read, write: if owner();" + m.group(2), R, count=1, flags=re.S),
            'v6: kirim ulang identik di atas selesai / dibatalkan ditolak': R.replace("allow update: if owner() && (tulisUlangSama() || (ubahBukuSah(request.resource.data, resource.data) && acaraTutupPintu(request.resource.data)));", "allow update: if owner() && ubahBukuSah(request.resource.data, resource.data) && acaraTutupPintu(request.resource.data);"),
            'v6: update tutupBukuAcara owner saja': R.replace("allow update: if owner() && (tulisUlangSama() || (ubahBukuSah(request.resource.data, resource.data) && acaraTutupPintu(request.resource.data)));", "allow update: if owner() && acaraTutupPintu(request.resource.data);"),
            'v6: status boleh mundur (selesai → terkunci)': R.replace("'terkunci>selesai', ", "'terkunci>selesai', 'selesai>terkunci', "),
            'v6: dibatalkan → terkunci diterima (penanda telat sesudah pembatalan tuntas)': R.replace("'dibatalkan>membatalkan']", "'dibatalkan>membatalkan', 'dibatalkan>terkunci']"),
            'v6: pemegang tidak dijaga (kiriman HP lama sesudah ambil alih lolos)': R.replace("      return pemegangBuku(b) == pemegangBuku(l)\n", "      return pemegangBuku(b) == pemegangBuku(b)\n"),
            'v6: ambil alih tanpa urutan jam (ambil alih lama menimpa yang baru)': R.replace("\n          && b.get('diambilAlihPada', '') > l.get('diambilAlihPada', ''))", ")"),
            'v6: jam batal tidak dijaga (pembatalan HP lama di atas dibatalkan)': R.replace("\n        && (l.get('status', '') != 'dibatalkan' || b.get('dibatalkanPada', '') == l.get('dibatalkanPada', ''));", ";"),
            'v6: percobaan baru di atas status apa pun (tahun selesai dibuka lagi)': R.replace("      return l.get('status', '') == 'dibatalkan' && b.get('status', '') in ['berjalan', 'terkunci']", "      return b.get('status', '') in ['berjalan', 'terkunci']"),
            'v6: percobaan lama boleh menimpa yang baru (tanpa urutan jam mulai)': R.replace(" && percobaanBuku(b) > percobaanBuku(l);", " && percobaanBuku(b) != percobaanBuku(l);"),
            'v6: jam mulai bukan bentuk toISOString diterima': R.replace("\n        && percobaanBuku(b).matches('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{3}Z') && ", "\n        && "),
            'v6 terlalu ketat: pembatalan lanjutan dari dibatalkan ditolak (P4-7 macet)': R.replace(", 'dibatalkan>membatalkan']", "]"),
            'v6 terlalu ketat: tutup buku satu kiriman (langsung terkunci) sesudah dibatalkan ditolak': R.replace("b.get('status', '') in ['berjalan', 'terkunci']", "b.get('status', '') in ['berjalan']"),
            'v6 terlalu ketat: ambil alih ditolak': R.replace("&& pemegangBuku(l) != '' && b.get('pemegangLama', {})", "&& pemegangBuku(l) == '' && b.get('pemegangLama', {})"),
            'v6: fungsi tutup buku membaca dokumen lain (access call)': R.replace("    function pemegangBuku(d) { return d.get('pemegang', {}).get('id', ''); }",
                                                                                "    function pemegangBuku(d) { return get(/databases/$(database)/documents/aturanToko/tutupBuku).data.get('x', d.get('pemegang', {}).get('id', '')); }"),
        }
        # 10 · v7 (hemat baca, owner 7 Okt 2026): dua tambahan saja, persis bentuknya
        UKB = ("return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer'])\n"
               "        && (!request.resource.data.keys().hasAny(['capServer']) || request.resource.data.capServer == request.time);")
        assert UKB in R, 'kontrol basi: bentuk ulangKasirBercap di firestore.rules'
        rusak.update({
            'v7: kirim ulang kasir@ boleh mengubah hargaTotal juga (hasOnly diperluas)': R.replace(UKB, UKB.replace("hasOnly(['capServer'])", "hasOnly(['capServer', 'hargaTotal'])")),
            'v7: ulangKasirBercap tanpa == request.time (cap nilai HP diterima)': R.replace(UKB, "return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer']);"),
            'v7: kirim ulang HP kasir-v32 (cap dibuang) DITOLAK lagi — nota yang sudah masuk pindah ke "ditolak"': R.replace(UKB, "return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer']) && request.resource.data.capServer == request.time;"),
            'v7: cap boleh dibuang walau isi lain berubah (kurung salah)': R.replace(UKB, "return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['capServer'])\n        && !request.resource.data.keys().hasAny(['capServer']) || request.resource.data.capServer == request.time;"),
            'v7: ulangKasirBercap dipasang juga di stokBahanLiteran': R.replace("allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('stokBahanLiteran'",
                                                                            "allow update: if (owner() && tglUbah('tanggal')) || (kasir() && ulangKasirBercap());\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('stokBahanLiteran'"),
            'v7: suku kirim ulang bercap dicabut dari penjualan (kasir-v33 ditolak)': R.replace(" || (kasir() && ulangKasirBercap());", ";"),
            'v7: batu nisan terbaca staf': R.replace("    match /batuNisan/{id} {\n      allow read: if owner();", "    match /batuNisan/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);"),
            'v7: batu nisan tertulis staf': R.replace("      allow create, update: if owner() && request.resource.data.capServer == request.time;", "      allow create, update: if (owner() || stafBuat(['ben', 'karyawan'])) && request.resource.data.capServer == request.time;"),
            'v7: batu nisan tanpa request.time (cap jam HP diterima)': R.replace("      allow create, update: if owner() && request.resource.data.capServer == request.time;", "      allow create, update: if owner();"),
            'v7: blok batu nisan hilang (hapus /baru/ ditolak seluruh batch)': re.sub(r"\n    match /batuNisan/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v7: baris lain berubah dari v6 (bentuk lain, arti sama — tetap wajib ketahuan)': R.replace("    match /pengingat/{id} {\n      allow read, write: if owner();", "    match /pengingat/{id} {\n      allow read: if owner();\n      allow write: if owner();"),
        })
        # 10/11 · v7 FINAL: persetujuan, foto bon, kasir@, pintu — BENTUK (pemeriksa khusus) dan MODEL saja ('model:' = bentuk & pembanding v6 dimatikan)
        PH = "|| salinanArsip(getAfter(/databases/$(database)/documents/arsipTahun/$(string(y) + '|' + kol + '|' + id)), y, kol, id, resource.data));"
        rusak.update({
            'v7: staf menulis persetujuan apa saja (stafBuat, bukan stafMintaNego)': R.replace("allow create: if owner() || stafMintaNego(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan']) || stafMintaKredit(['ben']) ||", "allow create: if owner() || stafBuat(['ben', 'karyawan']) || stafUsulHarga(['ben', 'karyawan']) || stafMintaKredit(['ben']) ||"),   # v13: baris create bersambung
            'v8: usul harga atas nama orang lain (tanpa usulUid)': R.replace(" && d.get('usulUid', '') == request.auth.uid", ""),
            'v8: usul harga tindakan apa saja': R.replace("d.get('tindakan', '') == 'hargaPelanggan' && ", ""),
            'v8: usul harga boleh menulis kolom keputusan': R.replace("d.get('usulUid', '') == request.auth.uid\n        && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);", "d.get('usulUid', '') == request.auth.uid;"),
            'v8: usul harga dicabut dari create persetujuan': R.replace(" || stafUsulHarga(['ben', 'karyawan']) ||", " ||"),
            'v10: surat jalan dibuat karyawan': R.replace("stafBuatSJ(['ben']);", "stafBuatSJ(['ben', 'karyawan']);"),
            'v10: surat jalan baru boleh membawa penerima': R.replace("!d.keys().hasAny(['penerima', 'diterimaPada',", "!d.keys().hasAny(['diterimaPada',"),
            'v10: pengantar boleh mengubah tagihan': R.replace("affectedKeys().hasOnly(['status', 'riwayatStatus', 'penerima',", "affectedKeys().hasOnly(['status', 'riwayatStatus', 'tagihRp', 'penerima',"),
            'v10: tandai tanpa syarat masih di jalan': R.replace("        && resource.data.get('status', '') == 'berangkat' && request.resource.data.get('status', '') in ['diterima', 'gagal']", "        && request.resource.data.get('status', '') in ['diterima', 'gagal']"),
            'v10: pengantar boleh membatalkan': R.replace("request.resource.data.get('status', '') in ['diterima', 'gagal']", "request.resource.data.get('status', '') in ['diterima', 'gagal', 'batal']"),
            'v10: tandai atas nama orang lain (tanpa uid pengubah)': R.replace("      return masuk() && aktifDengan(akun(), peranBoleh) && request.resource.data.diubahOlehUid == request.auth.uid\n        && resource.data.get('status', '') == 'berangkat'", "      return masuk() && aktifDengan(akun(), peranBoleh)\n        && resource.data.get('status', '') == 'berangkat'"),
            'v10: bukti terima boleh diubah': R.replace("      allow create: if (owner() || stafBuat(['ben', 'karyawan'])) && buktiSah(id);\n      allow delete: if owner();", "      allow create: if (owner() || stafBuat(['ben', 'karyawan'])) && buktiSah(id);\n      allow update: if owner() || staf(['ben', 'karyawan']);\n      allow delete: if owner();"),
            'v10: bukti terima jenis apa saja': R.replace("\n        && d.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp'] && d.get('base64', 0) is string && d.base64.size() > 0 && d.base64.size() <= 960000;", "\n        && d.get('base64', 0) is string && d.base64.size() > 0 && d.base64.size() <= 960000;"),
            'v10: blok surat jalan hilang': re.sub(r"\n    match /suratJalan/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v10: baris lain berubah dari v9 (tetap wajib ketahuan)': R.replace("      allow create: if owner() || stafBuat(['ben', 'karyawan']);   // pelanggan baru", "      allow create: if owner() || stafBuat(['ben', 'karyawan', 'tamu']);   // pelanggan baru"),
            'v11: pesanan dibuat karyawan': R.replace("stafBuatPesanan(['ben']);", "stafBuatPesanan(['ben', 'karyawan']);"),
            'v11: pesanan baru boleh sudah bernota': R.replace(" && d.get('trxIdJual', null) == null", ""),
            'v11: pesanan baru boleh membawa kolom batal': R.replace("!d.keys().hasAny(['dibatalkan', 'alasanBatal', 'nasibUangMuka'])", "!d.keys().hasAny(['dibatalkan'])"),
            'v11: Ben boleh mengganti nama pemesan': R.replace("affectedKeys().hasOnly(['status', 'riwayatStatus', 'baris',", "affectedKeys().hasOnly(['status', 'riwayatStatus', 'namaPelanggan', 'baris',"),
            'v11: ubah pesanan atas nama orang lain (tanpa uid pengubah)': R.replace("request.auth.uid\n        && resource.data.get('status', '') in ['dipesan', 'diantar']", "request.auth.uid || true\n        && resource.data.get('status', '') in ['dipesan', 'diantar']"),
            'v11: pesanan batal boleh dihidupkan lagi': R.replace("resource.data.get('status', '') in ['dipesan', 'diantar'] && request", "resource.data.get('status', '') in ['dipesan', 'diantar', 'batal'] && request"),
            'v11: Ben boleh menjadikan pesanan JADI NOTA tanpa nota': R.replace("request.resource.data.get('status', '') in ['dipesan', 'diantar', 'batal']", "request.resource.data.get('status', '') in ['dipesan', 'diantar', 'batal', 'dibayar']"),
            'v11: jadwal dihapus staf': R.replace("      allow update: if owner() || stafUbahRutin(['ben']);\n      allow delete: if owner();", "      allow update: if owner() || stafUbahRutin(['ben']);\n      allow delete: if owner() || staf(['ben']);"),
            'v11: pembuat jadwal boleh diganti': R.replace("affectedKeys().hasOnly(['namaPelanggan', 'baris',", "affectedKeys().hasOnly(['olehUid', 'namaPelanggan', 'baris',"),
            'v11: blok jadwal order rutin hilang': re.sub(r"\n    match /orderRutin/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v11: baris lain berubah dari v10 (tetap wajib ketahuan)': R.replace("    match /suratJalan/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);", "    match /suratJalan/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan', 'tamu']);"),
            'v12: tanda kenal dibuat staf tanpa uid sendiri (atas nama siapa saja)': R.replace("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || staf(['ben', 'karyawan']);\n      allow update, delete: if owner();"),
            'v12: staf boleh mengubah & menghapus tanda kenal': R.replace("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner() || staf(['ben', 'karyawan']);"),
            'v12: kasir@ membaca tanda kenal': R.replace("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || kasir() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();"),
            'v12: tanda kenal dibuka hanya untuk ben (karyawan di tablet ditolak)': R.replace("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben', 'karyawan']);\n      allow update, delete: if owner();", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow create: if owner() || stafBuat(['ben']);\n      allow update, delete: if owner();"),
            'v12: blok tanda kenal hilang': re.sub(r"\n    match /tandaKenal/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v12: baris lain berubah dari v11 (tetap wajib ketahuan)': R.replace("    match /orderRutin/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);", "    match /orderRutin/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan', 'tamu']);"),
            'v13: titipan uang keluar atas nama siapa saja (mintaUid tidak dinilai)': R.replace(" && d.get('mintaUid', '') == request.auth.uid\n        && d.get('jenis', '') in", "\n        && d.get('jenis', '') in"),
            'v13: titipan jenis apa saja (ambil pribadi lewat tablet)': R.replace("\n        && d.get('jenis', '') in ['toko', 'karyawan', 'kasbon', 'bongkar', 'bayarBon'] && d.get('nominal', 0) is int", "\n        && d.get('nominal', 0) is int"),   # v15: daftar jenis + bongkar & bayarBon
            'v13: nominal titipan boleh pecahan / teks': R.replace(" && d.get('nominal', 0) is int && d.get('nominal', 0) > 0", " && d.get('nominal', 0) > 0"),
            'v13: titipan boleh membawa betulan owner': R.replace("'alasanTolak', 'koreksiOwner', 'balasan']);", "'alasanTolak']);"),
            'v13: pesan tanpa batas panjang': R.replace(" && d.teks.size() <= 500", ""),
            'v13: karyawan tidak bisa menitip uang keluar': R.replace("stafMintaKeluar(['ben', 'karyawan'])", "stafMintaKeluar(['ben'])"),
            'v13: token notifikasi owner terbaca staf': R.replace("    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);\n      allow write: if owner();"),
            'v13: blok token notifikasi hilang': re.sub(r"\n    match /notifOwner/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v13: baris lain berubah dari v12 (tetap wajib ketahuan)': R.replace("    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);", "    match /tandaKenal/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan', 'tamu']);"),
            'v14: tanda baca uang tidak dinilai (semua Penjaga laci membaca uang)': R.replace("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.aktif == true && a.peran == 'ben'"),
            'v14: karyawan bertanda ikut membaca uang': R.replace("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.aktif == true && a.peran in ['ben', 'karyawan'] && a.get('bacaUang', false) == true"),
            'v14: akun nonaktif bertanda tetap membaca': R.replace("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.peran == 'ben' && a.get('bacaUang', false) == true"),
            'v14: akun bertanda boleh MENULIS uang keluar harian': R.replace("    match /pengeluaranHarian/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if (owner() && tglBaru('tanggal'))", "    match /pengeluaranHarian/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if ((owner() || stafBacaUang()) && tglBaru('tanggal'))"),
            'v14: pengaturan lain (keamanan) ikut terbaca akun bertanda': R.replace("(id == 'titikKas' && stafBacaUang())", "(id in ['titikKas', 'keamanan'] && stafBacaUang())"),
            'v14: slip upah ikut terbaca akun bertanda (di luar sebelas baris)': R.replace("    match /slipUpah/{id} {\n      allow read: if owner();", "    match /slipUpah/{id} {\n      allow read: if owner() || stafBacaUang();"),
            'v14: satu koleksi uang lupa dibuka (tutup hari)': R.replace("    match /tutupHari/{id} {\n      allow read: if owner() || stafBacaUang();", "    match /tutupHari/{id} {\n      allow read: if owner();"),
            'v14: baris lain berubah dari v13 (tetap wajib ketahuan)': R.replace("    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read: if owner();\n      allow write: if owner();"),
            'v15: karyawan ikut mencatat kedatangan dari tablet': R.replace("(stafCatatMasuk(['ben']) && tglStaf('tanggal'))", "(stafCatatMasuk(['ben', 'karyawan']) && tglStaf('tanggal'))"),
            'v15: kedatangan tablet boleh dibayar tunai (keluar laci tanpa titipan)': R.replace("d.get('dariTablet', false) == true && d.get('caraBayar', '') == 'utang'", "d.get('dariTablet', false) == true && d.get('caraBayar', '') in ['utang', 'tunai']"),
            'v15: kedatangan tablet boleh membawa upah bongkar': R.replace(" && d.get('biayaBongkar', -1) == 0\n", "\n"),
            'v15: kedatangan tablet tanpa penjaga bulan (tglStaf hilang)': R.replace("(stafCatatMasuk(['ben']) && tglStaf('tanggal'))", "stafCatatMasuk(['ben'])"),
            'v15: kedatangan tablet boleh membawa kolom koreksi owner': R.replace("['lahirBuku', 'stokAwal', 'tutupBuku', 'riwayat', 'alasanKoreksi', 'noBon', 'bongkarTitipan']", "['lahirBuku', 'stokAwal', 'tutupBuku', 'noBon', 'bongkarTitipan']"),
            'v15: kedatangan tablet tanpa batas baris barang': R.replace(" && d.merkList.size() > 0 && d.merkList.size() <= 20", ""),
            'v15: Penjaga laci boleh MENGUBAH kedatangan': R.replace("      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('batchMasuk'", "      allow update: if (owner() && tglUbah('tanggal')) || stafCatatMasuk(['ben']);\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('batchMasuk'"),
            'v15: titipan upah bongkar tanpa kedatangan': R.replace("        && (d.get('jenis', '') != 'bongkar' || (d.get('batchId', 0) is string && d.batchId.size() > 0))\n", ""),
            'v15: titipan bayar bon tanpa pemasok': R.replace("        && (d.get('jenis', '') != 'bayarBon' || (d.get('pemasok', 0) is string && d.pemasok.size() > 0 && d.pemasok.size() <= 60))\n", ""),
            'v15: kabar barang masuk untuk karyawan': R.replace("stafKabarMasuk(['ben']) || (stafHitungLaci(", "stafKabarMasuk(['ben', 'karyawan']) || (stafHitungLaci("),   # v16: baris create bersambung
            'v16: karyawan ikut mengirim hitungan laci': R.replace("(stafHitungLaci(['ben']) && tglStaf('tanggal'))", "(stafHitungLaci(['ben', 'karyawan']) && tglStaf('tanggal'))"),
            'v16: hitungan laci tanpa penjaga bulan (tglStaf hilang)': R.replace("(stafHitungLaci(['ben']) && tglStaf('tanggal'))", "stafHitungLaci(['ben'])"),
            'v16: hitungan laci boleh nol': R.replace("d.get('hitung', 0) is int && d.get('hitung', 0) > 0 &&", "d.get('hitung', 0) is int && d.get('hitung', 0) >= 0 &&"),
            'v16: yang dipindah ke brankas boleh melebihi hitungan': R.replace(" && d.get('amankan', -1) <= d.get('hitung', 0)\n", "\n"),
            'v16: hitungan laci boleh membawa keputusan owner': R.replace("['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'balasan', 'koreksiOwner']", "['diputusPada', 'balasan', 'koreksiOwner']"),
            'v16: hitungan atas nama orang lain': R.replace("d.get('tindakan', '') == 'hitungLaci' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid", "d.get('tindakan', '') == 'hitungLaci' && d.get('status', '') == 'menunggu'"),
            'v16: aturan tutup hari terbaca karyawan': R.replace("(id == 'tutupHari' && staf(['ben']))", "(id == 'tutupHari' && staf(['ben', 'karyawan']))"),
            'v16: Penjaga laci boleh menutup hari sendiri': R.replace("      allow create: if (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('tutupHari', id,", "      allow create: if stafBuat(['ben']) || (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('tutupHari', id,"),
            'v16: baris lain berubah dari v15 (tetap wajib ketahuan)': R.replace("    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read: if owner();\n      allow write: if owner();"),
            'v15: kabar barang masuk tanpa kedatangan': R.replace("d.get('tindakan', '') == 'barangMasuk' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid\n        && d.get('batchId', 0) is string && d.batchId.size() > 0\n", "d.get('tindakan', '') == 'barangMasuk' && d.get('status', '') == 'menunggu' && d.get('mintaUid', '') == request.auth.uid\n"),
            'v15: baris lain berubah dari v14 (tetap wajib ketahuan)': R.replace("    match /notifOwner/{id} {\n      allow read, write: if owner();", "    match /notifOwner/{id} {\n      allow read: if owner();\n      allow write: if owner();"),
            'v9: minta bon atas nama orang lain (tanpa mintaUid)': R.replace(" && d.get('mintaUid', '') == request.auth.uid", ""),
            'v9: minta bon tindakan apa saja': R.replace("d.get('tindakan', '') == 'kredit' && ", ""),
            'v9: minta bon boleh menulis kolom keputusan': R.replace("d.get('mintaUid', '') == request.auth.uid\n        && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);", "d.get('mintaUid', '') == request.auth.uid;"),
            'v9: minta bon dibuka untuk karyawan': R.replace("stafMintaKredit(['ben'])", "stafMintaKredit(['ben', 'karyawan'])"),
            'v9: minta bon dicabut dari create persetujuan': R.replace(" || stafMintaKredit(['ben']) ||", " ||"),   # v13: baris create bersambung
            'v9: baris lain berubah dari v8 (tetap wajib ketahuan)': R.replace("'hargaTingkat', 'produkArsip'] && staf(", "'hargaTingkat', 'produkArsip', 'kunciPeriode'] && staf("),
            'v8: setelan HET ikut terbaca staf': R.replace("'hargaTingkat', 'produkArsip'] && staf(", "'hargaTingkat', 'produkArsip', 'het'] && staf("),
            'v8: staf boleh menulis setelan harga tingkat': R.replace("      allow update: if owner() && (id != 'kunciPeriode' || kunciGeser());", "      allow update: if (owner() && (id != 'kunciPeriode' || kunciGeser())) || (id == 'hargaTingkat' && stafBuat(['ben', 'karyawan']));"),
            'v8: baris lain berubah dari v7 (tetap wajib ketahuan)': R.replace("    match /hargaWadah/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan']);", "    match /hargaWadah/{id} {\n      allow read: if owner() || staf(['ben', 'karyawan', 'tamu']);"),
            'v7: staf boleh memutus persetujuan (update)': R.replace("      allow update, delete: if owner();   // memutus", "      allow update: if owner() || staf(['ben', 'karyawan']);\n      allow delete: if owner();   // memutus"),
            'v7: persetujuan tidak terbaca staf padahal akses.js BACA_STAF memuatnya': R.replace("      allow read: if owner() || staf(['ben', 'karyawan']);   // v7: yang meminta", "      allow read: if owner();   // v7: yang meminta"),
            'v7: blok fotoBon hilang': re.sub(r"\n    match /fotoBon/\{id\} \{.*?\n    \}\n", '\n', R, flags=re.S),
            'v7: foto bon boleh diubah': R.replace("        && request.resource.data.get('base64', 0) is string && request.resource.data.base64.size() > 0 && request.resource.data.base64.size() <= 960000;\n      allow delete: if owner();",
                                                    "        && request.resource.data.get('base64', 0) is string && request.resource.data.base64.size() > 0 && request.resource.data.base64.size() <= 960000;\n      allow update: if owner();\n      allow delete: if owner();"),
            'v7: foto bon tanpa batas ukuran': R.replace(" && request.resource.data.base64.size() <= 960000;", ";"),
            'v7: kasir@ create logAktivitas dikembalikan': R.replace("      allow create: if owner() || stafJejak(['ben', 'karyawan']);", "      allow create: if owner() || kasir() || stafJejak(['ben', 'karyawan']);"),
            'v7: kasir@ baca pengaturan/aksesKasir dikembalikan': R.replace("      allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan'])) || (id == 'titikKas' && stafBacaUang());", "      allow read: if owner() || (id == 'tempatSimpan' && staf(['ben', 'karyawan'])) || (id == 'titikKas' && stafBacaUang()) || (id == 'aksesKasir' && kasir());"),   # v14: baris baca pengaturan
            'v7: kasir@ create piutangMutasi dikembalikan': R.replace("allow create: if (owner() && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi'", "allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (owner() && pintuTulis('piutangMutasi'"),
            'v7: kasir@ membaca persetujuan (hak baru di luar kasir darurat)': R.replace("      allow read: if owner() || staf(['ben', 'karyawan']);   // v7: yang meminta", "      allow read: if owner() || kasir() || staf(['ben', 'karyawan']);   // v7: yang meminta"),
            'pintu: pintuTulis dipasang di UPDATE (catatan bulan terkunci bisa diubah)': R.replace("      allow update: if (owner() && tglUbah('tanggal')) || (kasir() && tulisUlangSama()) || (kasir() && ulangKasirBercap());",
                                                                                              "      allow update: if (owner() && tglUbah('tanggal')) || (owner() && pintuTulis('penjualan', id, bulanDok(request.resource.data, 'tanggal'))) || (kasir() && tulisUlangSama()) || (kasir() && ulangKasirBercap());"),
            'pintu: pindahUang (tidak diarsip) ikut berpintu': R.replace("    match /pindahUang/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if owner() && tglBaru('tanggal');\n      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && tglLama('tanggal');",
                                                                    "    match /pindahUang/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if owner() && tglBaru('tanggal');\n      allow update: if owner() && tglUbah('tanggal');\n      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('pindahUang', id, bulanDok(resource.data, 'tanggal')));"),   # v14: baris baca
            'pintu: tutup hari bulan terkunci tidak bisa diarsip (pintuHapus hilang — tutup buku buntu)': R.replace("      allow delete: if owner() && (tglLama('tanggal') || pintuHapus('tutupHari', id, bulanDok(resource.data, 'tanggal')));", "      allow delete: if owner() && tglLama('tanggal');"),
            'pintu: staf lewat pintu': R.replace("(owner() && pintuTulis('produksiKemasan',", "(stafBuat(['ben', 'karyawan']) && pintuTulis('produksiKemasan',"),
            'pintu: dokumen pintu dibaca SEBELUM batch (get) — pintu tidak bisa dibuka di kiriman saldo pembuka yang sama': R.replace("let p = getAfter(/databases/$(database)/documents/pengaturan/pintuBuku);", "let p = get(/databases/$(database)/documents/pengaturan/pintuBuku);"),
            'pintu: berita acara dibaca SESUDAH batch (getAfter) — ritual karangan satu kiriman': R.replace("let a = get(/databases/$(database)/documents/tutupBukuAcara/$(string(y)));", "let a = getAfter(/databases/$(database)/documents/tutupBukuAcara/$(string(y)));"),
            'pintu: arsipTahun owner bebas lagi (salinan karangan)': R.replace("      allow create, update: if owner() && arsipSah(id);\n", "      allow create, update: if owner();\n"),
            'pintu: berita acara dibuat owner bebas lagi': R.replace("allow create: if owner() && acaraBaru(id);", "allow create: if owner();"),
            'pintu: berita acara selesai bisa dihapus lagi': R.replace("allow delete: if owner() && resource.data.get('status', '') == 'dibatalkan';", "allow delete: if owner();"),
            'pintu: salinan arsip dipakai di koleksi lain (pindahUang ikut koleksi arsip tanpa kunci)': R.replace("d.koleksi in ['karantina', 'pesanan', 'tembusanStok']", "d.koleksi in ['karantina', 'pesanan', 'tembusanStok', 'pindahUang']"),
            'pintu: koleksi saldo pembuka di rules beda dengan CACHE_PEMBUKA (penjualan ikut)': R.replace("      return kol in ['batchMasuk', 'piutangMutasi',", "      return kol in ['penjualan', 'batchMasuk', 'piutangMutasi',"),
            'pintu: jalur arsip beda dengan firebase.js (Y_koleksi_id)': R.replace("$(string(y) + '|' + kol + '|' + id)", "$(string(y) + '_' + kol + '_' + id)"),
            'pintu: tanpa batas umur 72 jam': R.replace(" && d.sampai <= request.time + duration.value(72, 'h')", ""),
            'model: hapus bulan terkunci TANPA salinan arsip lolos': R.replace(PH, "|| true);"),
            'model: hapus lewat pintu tanpa batas tahun pintu': R.replace("      let y = pintuTahun();\n      return y > 0 && b <= y * 12 + 12\n        && ((kolPembuka(kol) && resource.data", "      let y = pintuTahun();\n      return y > 0\n        && ((kolPembuka(kol) && resource.data"),
            'model: saldo pembuka lewat pintu tanpa batas tahun pintu': R.replace("      let d = request.resource.data;\n      return y > 0 && b <= y * 12 + 12\n", "      let d = request.resource.data;\n      return y > 0\n"),
            'model: pintu tanpa kedaluwarsa (sampai tidak dinilai)': R.replace(" is timestamp\n        && request.time < p.data.sampai ? int(p.data.tahun) : 0;", " is timestamp\n        ? int(p.data.tahun) : 0;"),
            'model: pintu tertutup tetap dianggap terbuka (status tidak dinilai)': R.replace("return p != null && p.data.get('status', '') == 'berjalan' && p.data.get('tahun', '') is number", "return p != null && p.data.get('tahun', '') is number"),
            'model: saldo pembuka tahun mana pun (tahunDari tidak dinilai)': R.replace("((kolPembuka(kol) && d.get('tutupBuku', false) == true && d.get('tahunDari', 0) == y) || pulihArsip(kol, id, y))", "((kolPembuka(kol) && d.get('tutupBuku', false) == true) || pulihArsip(kol, id, y))"),
            'model: catatan apa pun bertahunDari dianggap saldo pembuka (tutupBuku tidak dinilai)': R.replace("((kolPembuka(kol) && d.get('tutupBuku', false) == true && d.get('tahunDari', 0) == y) || pulihArsip(kol, id, y))", "((kolPembuka(kol) && d.get('tahunDari', 0) == y) || pulihArsip(kol, id, y))"),
            'model: salinan arsip tanpa pembanding isi (hapus & kembali)': R.replace("\n        && isi.diff(a.data.get('dok', {})).affectedKeys().hasOnly(['capServer']);", ";"),
            'model: pintu dibuka tanpa batas 72 jam': R.replace(" && d.sampai <= request.time + duration.value(72, 'h')", ""),
            'model: pintu dibuka di atas berita acara berstatus apa pun (selesai ikut)': R.replace(" && a.data.get('status', '') in ['berjalan', 'terkunci', 'membatalkan']", ""),
            'model: pintu dibuka di atas berita acara yang dimulai sebelum tahunnya berakhir': R.replace("\n        && a.data.get('paraf', {}).get('pada', '') >= string(y) + '-12-31T17:00:00.000Z';", ";"),
            'model: pintu untuk tahun lampau mana pun (bukan hanya tahun lalu)': R.replace("y is int && y == wib().year() - 1", "y is int && y < wib().year()"),
            'model: titik kas lewat pintu tanpa batas tanggal': R.replace("return y > 0 && bulanDok(d, 'tanggal') <= y * 12 + 12 && (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));", "return y > 0;"),
            'model: titik kas lewat pintu tanggal berapa pun ≤ 31 Des tahun pintu': R.replace(" && (d.get('tanggal', '') == string(y) + '-12-31' || titikSebelum(y, d));", ";"),
            'model: salinan arsip bulan terkunci tidak diikat ke aslinya': R.replace(" || salinanAsli(d))));", " || true)));"),
            'model: salinan arsip tanpa pembanding isi aslinya': R.replace("return asli != null && asli.data.diff(d.dok).affectedKeys().hasOnly(['capServer']);", "return asli != null;"),
            'model: saldo pembuka di koleksi mana pun (kolPembuka selalu benar)': R.replace("      return kol in ['batchMasuk', 'piutangMutasi',", "      return true || kol in ['batchMasuk', 'piutangMutasi',"),
            'model: berita acara selesai walau pintu terbuka': R.replace("      return !(b.get('status', '') in ['selesai', 'dibatalkan']) || pintuMati(", "      return true || pintuMati("),
            'model: berita acara baru tanpa pemeriksa jam mulai': R.replace("\n        && p[0:10] in [hariUtc(request.time - duration.value(1, 'd')), hariUtc(request.time), hariUtc(request.time + duration.value(1, 'd'))];", ";"),
            'model: berita acara baru tahun berjalan': R.replace("id == string(d.tahun) && d.tahun < wib().year()", "id == string(d.tahun) && d.tahun <= wib().year()"),
            'model: permintaan nego atas nama orang lain': R.replace(" && d.get('negoUid', '') == request.auth.uid", ""),
            'model: permintaan nego sudah berstatus disetujui': R.replace("d.get('tindakan', '') == 'nego' && d.get('status', '') == 'menunggu'", "d.get('tindakan', '') == 'nego'"),   # v13: hanya permintaan nego (titipan & pesan punya pemeriksa bentuknya sendiri)
            'model: permintaan nego membawa kolom keputusan': R.replace("\n        && !d.keys().hasAny(['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak']);", ";"),
            'model: foto bon jenis apa saja': R.replace("        && request.resource.data.get('jenis', '') in ['image/jpeg', 'image/png', 'image/webp']\n", "\n"),
        })
        # mesin menambah koleksi ke arsip tutup buku tanpa pintu di rules (dibaca dari beku.js / pembantu.js)
        BK0 = baca('baru/js/mesin/beku.js'); PB0 = baca('baru/js/mesin/pembantu.js')
        assert "      { koleksi: KOLEKSI_BULANAN," in BK0 and "  const KOLEKSI_BULANAN = 'biayaBulanan';" in PB0, 'kontrol basi: tbDaftarKoleksi / KOLEKSI_BULANAN'
        rusak_mesin = {'pintu: mesin mengarsip slipUpah tapi rules tidak berpintu': (BK0.replace("      { koleksi: KOLEKSI_BULANAN,", "      { koleksi: KOLEKSI_SLIP, label: 'slip', dok: [] },\n      { koleksi: KOLEKSI_BULANAN,", 1),
                                                                                      PB0.replace("  const KOLEKSI_BULANAN = 'biayaBulanan';", "  const KOLEKSI_BULANAN = 'biayaBulanan';\n  const KOLEKSI_SLIP = 'slipUpah';", 1))}
        DOK0 = baca('docs/uji-rules-v7.md')
        assert '| ★P13 |' in DOK0 and '| 7 | ★P20 |' in DOK0, 'kontrol basi: ★P13 / ★P20 di docs/uji-rules-v7.md'
        rusak_dok = {'dokumen Playground kehilangan kasus ★P13 (kembali dari arsip berisi beda)': re.sub(r'\n\| ★P13 \|[^\n]*', '', DOK0),
                     'daftar Wajib owner kehilangan ★P20 (hapus dengan salinan berisi lain) — kasusnya pindah ke opsional': re.sub(r'\n\| 7 \| ★P20 \|[^\n]*', '', DOK0).replace('| ★P25 |', '| ★P20 | owner@ | delete `penjualan/uji-v7-beda` | — | DITOLAK | x |\n| ★P25 |')}
        kode = 0
        KPJ = baca('baru/js/data/kunci-periode.js')
        rusak['tenggang minimal 1 di rules DAN kunci-periode.js (di bawah keputusan owner 3 hari)'] = (R.replace("function tenggangMin() { return 3; }", "function tenggangMin() { return 1; }"),
                                                                                                   KPJ.replace('export const KP_TENGGANG_MIN = 3;', 'export const KP_TENGGANG_MIN = 1;'))
        for nama, isi in rusak.items():
            KP_TEKS = None
            if isinstance(isi, tuple):
                isi, KP_TEKS = isi
                if KP_TEKS == KPJ: print('KONTROL BASI  ' + nama); kode = 3; continue
            if isi == R: print('KONTROL BASI  ' + nama); kode = 3; continue
            # kontrol lama (sebelum v7) WAJIB tertangkap pemeriksa KHUSUSNYA — pembanding "sama dengan v6" (yang menangkap perubahan apa pun) dimatikan untuknya;
            # 'model:' — bentuk v7 (persetujuan, fotoBon, pintu) juga dimatikan: yang wajib berbunyi = penafsir rules mini pada kasus Playground ★/M
            BANDING_V6 = nama.startswith('v7:') or nama.startswith('pintu:'); BENTUK_V7 = not nama.startswith('model:'); BANDING_V7 = BANDING_V6 or nama.startswith('v8:'); BANDING_V8 = BANDING_V7 or nama.startswith('v9:'); BANDING_V9 = BANDING_V8 or nama.startswith('v10:'); BANDING_V10 = BANDING_V9 or nama.startswith('v11:'); BANDING_V11 = BANDING_V10 or nama.startswith('v12:'); BANDING_V12 = BANDING_V11 or nama.startswith('v13:'); BANDING_V13 = BANDING_V12 or nama.startswith('v14:'); BANDING_V14 = BANDING_V13 or nama.startswith('v15:'); BANDING_V15 = BANDING_V14 or nama.startswith('v16:')
            c = periksa(isi, K, A)
            if nama.startswith('model:') and c and not all(x.startswith(('model v7 ', 'model v8 ', 'model v9 ', 'model v10 ', 'model v11 ', 'model v12 ', 'model v13 ', 'model v14 ', 'model v15 ', 'model v16 ')) for x in c): c = ['BUKAN MODEL YANG BERBUNYI: ' + c[0]]; print('DIAM!!   ' + nama + ' → ' + c[0][:110]); kode = 3; continue
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:110] if c else '-'))
            if not c: kode = 3
        BANDING_V6 = True; BENTUK_V7 = True; BANDING_V7 = True; BANDING_V8 = True; BANDING_V9 = True; BANDING_V10 = True; BANDING_V11 = True; BANDING_V12 = True; BANDING_V13 = True; BANDING_V14 = True; BANDING_V15 = True; KP_TEKS = None   # kontrol tenggang terakhir mengganti kunci-periode.js — dikembalikan sebelum kontrol berkas
        for nama, isi in rusak_dok.items():
            DOK_V7_TEKS = isi; c = periksa(R, K, A); DOK_V7_TEKS = None
            c = [x for x in c if 'docs/uji-rules-v7.md' in x]   # berbunyi karena SEBABNYA (berkas Playground), bukan kegagalan lain
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:110] if c else '-'))
            if not c: kode = 3
        for nama, (bk, pb) in rusak_mesin.items():
            TEKS_BEKU, TEKS_PEMBANTU = bk, pb; c = periksa(R, K, A); TEKS_BEKU = TEKS_PEMBANTU = None
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:110] if c else '-'))
            if not c: kode = 3
        sys.exit(kode)
    c = periksa(R, K, A)
    B = blok_rules(R)
    if c: print('RULES CACAT (%d):' % len(c)); [print('   ✗ ' + x) for x in c]; sys.exit(2)
    KOL, TMIN = kp_js()
    nS = sum(1 for k in KASUS_BUKU if k[4]); nT = len(KASUS_BUKU) - nS
    print('RULES v16 LULUS: v16 = firestore.rules.v15 + hitungan laci dari tablet (Penjaga laci, menunggu, bulat, brankas ≤ hitungan) + aturan tutup hari terbaca ben; hari ditutup owner saja (model %d kasus ★Y, beda v15 = %d kasus) · ' % (len(KASUS_V16), len(BEDA_V15))
          + 'v15 = firestore.rules.v14 + barang masuk dari tablet (Penjaga laci, langsung bon, bongkar 0) + titipan upah bongkar & bayar bon pemasok + kabar barang masuk; ubah kedatangan & tulis uang tetap owner (model %d kasus ★X, beda v14 = %d kasus) · ' % (len(KASUS_V15), len(BEDA_V14))
          + 'v14 = firestore.rules.v13 + data uang (sebelas baris BACA) untuk akun Penjaga laci yang ditandai owner — Ringkas hari ini di tablet; tulis tetap owner (model %d kasus ★W, beda v13 = %d kasus) · ' % (len(KASUS_V14), len(BEDA_V13))
          + 'v13 = firestore.rules.v12 + titipan uang keluar & pesan dari tablet (bentuk persis; uangnya tetap ditulis owner) + token notifikasi HP owner (model %d kasus ★U, beda v12 = %d kasus) · ' % (len(KASUS_V13), len(BEDA_V12))
          + 'v12 = firestore.rules.v11 + tanda kenal (barcode kemasan & kartu NFC; blok baru, tanpa fungsi baru; model %d kasus ★S, beda v11 = %d kasus) · ' % (len(KASUS_V12), len(BEDA_V11))
          + 'v11 = firestore.rules.v10 + pesanan dari tablet (ben membuat, mengubah, mengantar, membatalkan; bentuk persis) + jadwal order rutin (model %d kasus ★M, beda v10 = %d kasus) · '
          % (len(KASUS_V11), len(BEDA_V10)) + 'v10 = firestore.rules.v9 + surat jalan (ben membuat, pengantar ben/karyawan menandai; bentuk persis) + bukti terima (model %d kasus ★L, beda v9 = %d kasus) · '
          % (len(KASUS_V10), len(BEDA_V9))
          + 'v9 = firestore.rules.v8 + minta persetujuan bon (ben; bentuk persis; model %d kasus ★J, beda v8 = %s) · ' % (len(KASUS_V9), ', '.join(sorted(BEDA_V8)))
          + 'v8 = firestore.rules.v7 + harga tingkat & arsip produk terbaca staf + usul harga staf (bentuk persis; model %d kasus ★H, beda v7 = %s) · ' % (len(KASUS_V8), ', '.join(sorted(BEDA_V7)))
          + 'v7: %d blok koleksi · TANPA payung (tidak ada match rekursif / wildcard koleksi) · owner via email · jalur kasir@ utuh & dipersempit · '
          'tulis bukan-owner wajib uid · daftar peran = akses.js · kunci periode di %d koleksi bertanggal (= kunci-periode.js), tenggang minimal %d hari, '
          'satu get() dokumen kunci per operasi, bukan-owner tanpa get() kunci, pajak tidak dikunci (K6) · berita acara tutup buku hanya maju (model: %d tulisan '
          'boleh, %d tulisan telat/mundur ditolak; tanpa get(); penafsir mini sepakat) · v7 FINAL = v6 + kirim ulang kasir@ bercap + batu nisan + permintaan nego staf + '
          'foto bon + kasir@ dipangkas (nota, denyut, katalog) + PINTU TUTUP BUKU di %d koleksi arsip (bentuk persis; salinan arsip terikat ke aslinya, saldo pembuka '
          'hanya di koleksi pembuka, berita acara dibaca sebelum batch & mengikat pintu; model penafsir: %d kasus Playground ★/M sesuai, %d kasus wajib owner, '
          'access call jalur pintu ≤ 3), selebihnya sama dengan firestore.rules.v6' % (len(B), len(KOL), TMIN, nS, nT, len(koleksi_arsip() or []), len(KASUS_V7), len(WAJIB_V7)))
