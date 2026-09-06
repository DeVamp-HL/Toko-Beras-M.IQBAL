#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT HITUNG-ULANG INDEPENDEN — Toko Beras M.IQBAL (Fase 0A, 26 Agu 2026)

Menghitung ulang SEMUA angka uang dari dokumen mentah berkas backup (unduhBackup
versi >= 4), dengan implementasi TERPISAH dari index.html — python, bukan JS —
supaya kesalahan rumus di aplikasi tidak ikut tersalin ke pembandingnya.

Aturan bisnis ditranskripsikan dari index.html (nama fungsi sumber dicantumkan
di tiap bagian). Kalau audit menemukan selisih, yang diperbaiki adalah DATA lewat
mekanisme koreksi resmi aplikasi, atau — bila rumusnya yang beda — dibicarakan
dulu mana yang benar; skrip ini tidak pernah menulis apa pun.

Pakai:  python3 alat-audit/audit.py _privat/backup.json [--bulan 2026-08]
"""
import json, sys, datetime, collections

# ===== Konstanta bisnis (index.html) =====
TANGGAL_STOK_AWAL = '2026-08-08'          # index.html: TANGGAL_STOK_AWAL
MULAI_SUSUT_LABA = '2026-09-01'           # index.html: MULAI_SUSUT_LABA
POS_BIAYA_BULANAN = [('listrik', 'Listrik'), ('akses', 'Akses / gapura'),
                     ('keamanan', 'Keamanan lingkungan'), ('internet', 'Internet / Wifi')]

def rp(n):
    n = round(n)
    tanda = '-' if n < 0 else ''
    return tanda + 'Rp' + format(abs(int(n)), ',').replace(',', '.')

def bulan_dari(iso): return str(iso or '')[:7]

def hari_dalam_bulan(bl):
    y, m = int(bl[:4]), int(bl[5:7])
    akhir = (datetime.date(y + (m == 12), (m % 12) + 1, 1) - datetime.timedelta(days=1))
    return akhir.day

def iso_hari(bl, h): return f"{bl}-{h:02d}"

# ===== Muat backup =====
def muat(path):
    with open(path) as f:
        d = json.load(f)
    def kol(nama): return d.get(nama) or []
    return d, kol

# ===== Penyaring (index.html: penjualanMasihBerlaku, produksiMasihBerlaku, hppTercatat) =====
def jual_berlaku(semua):
    return [p for p in semua if not p.get('dibatalkan') and not p.get('dikoreksiOleh')]

def prod_berlaku(semua):
    return [p for p in semua if not p.get('dikoreksiOleh')]

def hpp_tercatat(p):
    h = p.get('hppTotalSaatJual')
    if h is None: return False
    return h > 0 or (p.get('hargaTotal') or 0) == 0

def cb(p): return str(p.get('caraBayar') or '').strip().lower()   # caraBayarKunci

# ===== bayaranBiayaBulanan (index.html) — nominal BERSIH utk kas, nominalKotor utk laba =====
def bayaran_biaya_bulanan(kol):
    out, baris_gaji = [], []
    for b in kol('biayaBulanan'):
        punya_per_pos = bool(b.get('tanggalBayarPos'))
        peta = b.get('tanggalBayarPos') or {}
        for kunci, label in POS_BIAYA_BULANAN:
            nominal = b.get(kunci) or 0
            if nominal <= 0: continue
            out.append({'bulan': b.get('bulan'), 'pos': kunci, 'label': label,
                        'nominal': nominal, 'nominalKotor': nominal, 'dipotong': 0,
                        'tanggal': (peta.get(kunci) or '') if punya_per_pos else (b.get('tanggalBayar') or '')})
        peta_gaji = b.get('tanggalBayarGaji') or None
        cadangan = ((peta.get('gaji') or '') if punya_per_pos else '') or b.get('tanggalBayar') or ''
        for r in (b.get('rincianGaji') or []):
            g = r.get('gaji') or 0
            if g <= 0: continue
            baris_gaji.append({'bulan': b.get('bulan'), 'nama': r.get('nama'), 'kotor': g,
                               'tanggal': (peta_gaji.get(r.get('nama')) or '') if peta_gaji else cadangan})
    # potongan kasbon 'Potong gaji' per pegawai, urut tanggal bayar terlama (potonganGajiPerPegawai)
    sisa_potong = collections.defaultdict(float)
    for m in kol('kasbonMutasi'):
        if m.get('tipe') == 'bayar' and str(m.get('caraBayar') or '').strip().lower() == 'potong gaji':
            n = str(m.get('namaPegawai') or '').strip()
            if n: sisa_potong[n] += m.get('nominal') or 0
    baris_gaji.sort(key=lambda g: str(g['tanggal'] or '9999'))
    for g in baris_gaji:
        dipotong = min(sisa_potong[g['nama']], g['kotor'])
        sisa_potong[g['nama']] -= dipotong
        out.append({'bulan': g['bulan'], 'pos': 'gaji:' + str(g['nama']), 'label': 'Gaji ' + str(g['nama']),
                    'nominal': g['kotor'] - dipotong, 'nominalKotor': g['kotor'], 'dipotong': dipotong,
                    'tanggal': g['tanggal']})
    return out

# ===== daftarModalOwner (index.html) — setoranKas lama = 'tarik'; kembaran dariSetoran dibuang =====
def daftar_modal(kol):
    modal = list(kol('modalOwner'))
    dipetakan = {str(m.get('dariSetoran')) for m in modal if m.get('dariSetoran')}
    for x in kol('setoranKas'):
        if str(x.get('id')) in dipetakan: continue
        modal.append({'id': x.get('id'), 'tanggal': x.get('tanggal'), 'tipe': 'tarik',
                      'nominal': x.get('nominal') or 0, 'dariSetoranLama': True})
    return modal

# ===== hitungArusKasInti (index.html) — port penuh, predikat tanggal =====
def arus_kas(kol, cocok, bayaran):
    jual = [p for p in jual_berlaku(kol('penjualan')) if cocok(p.get('tanggal'))]
    s = lambda a: sum((x.get('hargaTotal') or 0) for x in a)
    sn = lambda a: sum((x.get('nominal') or 0) for x in a)
    kredit = [p for p in jual if cb(p) == 'kredit']
    qris = [p for p in jual if cb(p) == 'qris']
    tunai = [p for p in jual if cb(p) not in ('kredit', 'qris')]
    piutang_bayar = [m for m in kol('piutangMutasi') if m.get('tipe') == 'bayar' and cocok(m.get('tanggal'))]
    kasbon_bayar = [m for m in kol('kasbonMutasi') if m.get('tipe') == 'bayar' and cocok(m.get('tanggal'))
                    and str(m.get('caraBayar') or '').strip().lower() != 'potong gaji']
    kasbon_ambil = [m for m in kol('kasbonMutasi') if m.get('tipe') == 'ambil' and cocok(m.get('tanggal'))]
    modal_g = [m for m in daftar_modal(kol) if cocok(m.get('tanggal'))]
    modal_setor = [m for m in modal_g if m.get('tipe') == 'setor']
    setoran = [m for m in modal_g if m.get('tipe') != 'setor']
    batch = [k for k in kol('batchMasuk') if cocok(k.get('tanggal')) and not k.get('stokAwal')]
    diutang = lambda k: k.get('caraBayar') == 'utang'
    nilai_beras = lambda k: sum((m.get('subtotalHarga') or 0) for m in (k.get('merkList') or []))
    belanja = sum((0 if diutang(k) else nilai_beras(k)) + (k.get('biayaBongkar') or 0) for k in batch)
    beras_diutang = sum(nilai_beras(k) for k in batch if diutang(k))
    bayar_bon = [m for m in kol('utangPemasokMutasi') if m.get('tipe') == 'bayar' and cocok(m.get('tanggal'))]
    bayar_terhitung = [x for x in bayaran if x['tanggal'] and cocok(x['tanggal']) and x['nominal'] > 0]
    # 'tokoDompet' sengaja TIDAK di sini: belanja toko yang dibayar dompet pribadi owner
    # tidak mengeluarkan sepeser pun dari laci. Yang mengeluarkannya adalah PELUNASAN-nya,
    # di baris bayar_utang_owner di bawah. Cerminan hitungArusKasInti di index.html.
    harian_toko = [h for h in kol('pengeluaranHarian') if h.get('kategori') == 'toko' and cocok(h.get('tanggal'))]
    harian_owner = [h for h in kol('pengeluaranHarian') if h.get('kategori') == 'owner' and cocok(h.get('tanggal'))]
    bayar_utang_owner = [m for m in kol('utangOwnerMutasi') if m.get('tipe') == 'bayar' and cocok(m.get('tanggal'))]
    retur = [r for r in kol('retur') if cocok(r.get('tanggal'))]
    refund = sum((r.get('nominalRefund') or 0) + max(0, r.get('selisihHargaTukar') or 0) for r in retur)
    tukar_masuk = sum(max(0, -(r.get('selisihHargaTukar') or 0)) for r in retur)
    bahan = lambda b: b.get('tipe') == 'beli' and cocok(b.get('tanggal')) and b.get('tanggal') != TANGGAL_STOK_AWAL
    beli_kemasan = [b for b in kol('stokBahanKemasan') if bahan(b)]
    beli_literan = [b for b in kol('stokBahanLiteran') if bahan(b)]
    masuk = s(tunai) + s(qris) + sn(piutang_bayar) + sn(kasbon_bayar) + tukar_masuk + sn(modal_setor)
    keluar = (belanja + sn(bayar_bon) + sum(x['nominal'] for x in bayar_terhitung)
              + sn(harian_toko) + sn(harian_owner) + refund + s(beli_kemasan) + s(beli_literan)
              + sn(kasbon_ambil) + sn(setoran) + sn(bayar_utang_owner))
    return {
        'masuk': masuk, 'keluar': keluar, 'bersih': masuk - keluar,
        'omzet': s(jual), 'kredit': s(kredit),
        'pos': {'tunai': s(tunai), 'qris': s(qris), 'pelunasan': sn(piutang_bayar),
                'kasbonBayar': sn(kasbon_bayar), 'kasbonAmbil': sn(kasbon_ambil),
                'tukarMasuk': tukar_masuk, 'refund': refund, 'belanja': belanja,
                'berasDiutang': beras_diutang, 'bayarBon': sn(bayar_bon),
                'biayaBulanan': sum(x['nominal'] for x in bayar_terhitung),
                'harian': sn(harian_toko), 'prive': sn(harian_owner),
                'beliKemasan': s(beli_kemasan), 'beliLiteran': s(beli_literan),
                'setoran': sn(setoran), 'modalSetor': sn(modal_setor),
                'bayarUtangOwner': sn(bayar_utang_owner)}}

# ===== hitungLabaRentang + hitungLabaBersihRentang (index.html) =====
def laba_rentang(kol, cocok):
    semua = [p for p in jual_berlaku(kol('penjualan')) if cocok(p.get('tanggal'))]
    terhitung = [p for p in semua if hpp_tercatat(p)]
    bolong = [p for p in semua if not hpp_tercatat(p)]
    omzet_hitung = sum((p.get('hargaTotal') or 0) for p in terhitung)
    hpp = sum((p.get('hppTotalSaatJual') or 0) for p in terhitung)
    return {'nTrx': len(semua), 'nBolong': len(bolong),
            'omzet': sum((p.get('hargaTotal') or 0) for p in semua),
            'omzetHitung': omzet_hitung, 'hpp': hpp, 'margin': omzet_hitung - hpp,
            'omzetBolong': sum((p.get('hargaTotal') or 0) for p in bolong)}

# ===== barisSusutStok (index.html) — susut stok memotong laba, mulai 1 Sep 2026 =====
# Syaratnya tiga dan semuanya wajib, persis seperti di aplikasi: dokumen punya nilaiRp
# berupa angka (dokumen lama tidak punya field ini sama sekali — itulah yang mengunci
# Agustus 2026 di luar hitungan), tanggalnya >= MULAI_SUSUT_LABA, dan lolos rentang.
# nilaiRp DIKUNCI saat simpan; audit tidak pernah menurunkannya ulang dari HPP hari ini.
def baris_susut(kol, cocok):
    baris = []
    def tambah(x, nama, satuan, jumlah, alasan):
        n = x.get('nilaiRp')
        if isinstance(n, bool) or not isinstance(n, (int, float)) or n == 0: return
        t = x.get('tanggal') or ''
        if t < MULAI_SUSUT_LABA or not cocok(t): return
        baris.append({'tanggal': t, 'nama': nama, 'satuan': satuan,
                      'jumlah': jumlah or 0, 'nilaiRp': n, 'alasan': alasan or ''})
    for x in kol('penyesuaianStok'):
        tambah(x, x.get('merk') or '(karung)', 'kg', x.get('selisihKg'), x.get('alasan'))
    for x in kol('penyesuaianKemasan'):
        tambah(x, f"{x.get('namaProduk') or ''} {x.get('ukuranKemasan')} kg", 'unit',
               x.get('selisihUnit'), x.get('alasan'))
    for x in list(kol('stokBahanKemasan')) + list(kol('stokBahanLiteran')):
        if x.get('tipe') == 'opname':
            tambah(x, x.get('jenis'), 'pcs', x.get('jumlah'), x.get('catatan'))
    return baris

def jatah_hari(bl, hari, total_kotor_bulan):
    n = hari_dalam_bulan(bl)
    dasar = total_kotor_bulan // n
    return total_kotor_bulan - dasar * (n - 1) if hari == n else dasar

def laba_bersih_rentang(kol, dari, sampai, bayaran):
    cocok = lambda t: bool(t) and dari <= t <= sampai
    laba = laba_rentang(kol, cocok)
    # Beban toko = 'toko' + 'tokoDompet'. Sengaja MENYIMPANG dari sisi kas di atas:
    # bebannya sama besar, kantongnya yang beda — dan itu urusan kas, bukan laba.
    harian = sum((h.get('nominal') or 0) for h in kol('pengeluaranHarian')
                 if h.get('kategori') in ('toko', 'tokoDompet') and cocok(h.get('tanggal')))
    hapus = sum((m.get('nominal') or 0) for m in kol('piutangMutasi')
                if m.get('tipe') == 'hapusBuku' and cocok(m.get('tanggal')))
    kotor_per_bulan = collections.defaultdict(int)
    for x in bayaran: kotor_per_bulan[x['bulan']] += int(x['nominalKotor'])
    jatah, t = 0, datetime.date.fromisoformat(dari)
    akhir = datetime.date.fromisoformat(sampai)
    while t <= akhir:
        bl = t.isoformat()[:7]
        jatah += jatah_hari(bl, t.day, kotor_per_bulan.get(bl, 0))
        t += datetime.timedelta(days=1)
    # Susut = suku SENDIRI, tandanya apa adanya (nilaiRp negatif menurunkan laba).
    # TIDAK pernah menyentuh arus kas: berasnya hilang, uangnya tidak pernah ada.
    susut_rows = baris_susut(kol, cocok)
    susut = sum(x['nilaiRp'] for x in susut_rows)
    laba.update({'harianToko': harian, 'jatahBulanan': jatah, 'hapusBuku': hapus,
                 'susutStok': susut, 'nSusut': len(susut_rows),
                 'labaBersih': laba['margin'] - harian - jatah - hapus + susut})
    return laba

# ===== Stok karung (hitungStokKarungPerMerk + hitungHppMerkDalamBatch) =====
def stok_karung(kol):
    stok = collections.defaultdict(lambda: {'masuk': 0.0, 'terpakai': 0.0, 'nilai': 0.0})
    for k in kol('batchMasuk'):
        daftar = k.get('merkList') or []
        total_kg = sum((m.get('totalKg') or 0) for m in daftar)
        bongkar = k.get('biayaBongkar') or 0
        for m in daftar:
            if m.get('bentuk') == 'bal': continue
            kg = m.get('totalKg') or 0
            alokasi = (kg / total_kg) * bongkar if total_kg > 0 else 0
            hpp_kg = ((m.get('subtotalHarga') or 0) + alokasi) / kg if kg > 0 else 0
            stok[m.get('merk')]['masuk'] += kg
            stok[m.get('merk')]['nilai'] += hpp_kg * kg
    for p in jual_berlaku(kol('penjualan')):
        if p.get('jenis') in ('karung', 'repacking', 'literan') and p.get('merkSumber') in stok:
            stok[p['merkSumber']]['terpakai'] += p.get('totalKg') or 0
    for pr in prod_berlaku(kol('produksiKemasan')):
        sl = pr.get('sumberList')
        if isinstance(sl, list) and sl:
            for s in sl:
                if s.get('merk') in stok: stok[s['merk']]['terpakai'] += s.get('kg') or 0
        elif pr.get('merkSumber') in stok:
            stok[pr['merkSumber']]['terpakai'] += pr.get('kgDipakai') or 0
    for r in kol('retur'):
        if r.get('jenisAsal') == 'karung' and r.get('kondisi') == 'utuh' and r.get('merkSumber') in stok:
            stok[r['merkSumber']]['terpakai'] -= r.get('totalKg') or 0
    for o in kol('penyesuaianStok'):
        if o.get('merk') in stok: stok[o['merk']]['terpakai'] -= o.get('selisihKg') or 0
    for pr in prod_berlaku(kol('produksiKemasan')):        # legacy jadiKarungUtuh
        if not pr.get('jadiKarungUtuh') or not pr.get('merkTujuan'): continue
        kg_jadi = (pr.get('ukuranKemasan') or 0) * (pr.get('jumlahUnit') or 0)
        if kg_jadi <= 0: continue
        stok[pr['merkTujuan']]['masuk'] += kg_jadi
        stok[pr['merkTujuan']]['nilai'] += (pr.get('hppSumberPerKgDipakai') or 0) * (pr.get('kgDipakai') or 0)
    return {m: {'sisaKg': round(v['masuk'] - v['terpakai'], 2),
                'hppPerKg': v['nilai'] / v['masuk'] if v['masuk'] > 0 else 0}
            for m, v in stok.items()}

# ===== Stok kemasan (hitungStokKemasan) =====
def kunci_kemasan(nama, ukuran):
    """Kembaran kunciKemasan() di index.html — ukuran tersimpan ada yang angka ada yang
    teks, dan pembanding independen ini harus memakai kunci yang SAMA persis, kalau tidak
    ia melaporkan 'cocok' untuk dua peta yang sebenarnya tak pernah bertemu."""
    try:
        u = float(ukuran)
        return f"{nama}|{int(u) if u == int(u) else u}"
    except (TypeError, ValueError):
        return f"{nama}|{ukuran}"

def stok_kemasan(kol):
    stok = collections.defaultdict(lambda: {'dibuat': 0, 'terjual': 0, 'dipakai': 0, 'peny': 0, 'nilai': 0.0})
    for pr in prod_berlaku(kol('produksiKemasan')):
        if pr.get('jadiKarungUtuh'): continue
        k = kunci_kemasan(pr.get('namaProduk'), pr.get('ukuranKemasan'))
        stok[k]['dibuat'] += pr.get('jumlahUnit') or 0
        stok[k]['nilai'] += (pr.get('hppPerUnit') or 0) * (pr.get('jumlahUnit') or 0)
    # Kemasan jadi yang DIBONGKAR jadi bahan adukan lain (index.html, 26 Agu 2026).
    # Tanpa suku ini pembanding independen melaporkan karung hantu — dan karena
    # selisihnya selalu menggeser angka audit ke ATAS, detektor MINUS tidak akan
    # pernah menyala untuk kelas kesalahan yang justru dibuat fitur itu.
    for pr in prod_berlaku(kol('produksiKemasan')):
        for sk in (pr.get('sumberKemasanList') or []):
            stok[kunci_kemasan(sk.get('namaProduk'), sk.get('ukuranKemasan'))]['dipakai'] += sk.get('unit') or 0
    for p in jual_berlaku(kol('penjualan')):
        if p.get('jenis') == 'kemasan':
            k = kunci_kemasan(p.get('namaProduk'), p.get('ukuranKemasan'))
            if k in stok: stok[k]['terjual'] += p.get('jumlahUnit') or 0
    for r in kol('retur'):
        if r.get('jenisAsal') == 'kemasan' and r.get('kondisi') == 'utuh':
            k = kunci_kemasan(r.get('namaProduk'), r.get('ukuranKemasan'))
            if k in stok: stok[k]['terjual'] -= r.get('jumlahUnit') or 0
    # Cocokkan Kemasan Jadi (59dfa20) — suku tersendiri, TIDAK lewat 'dibuat', supaya
    # tidak menyeret pembagi rata-rata HPP. Sama persis dengan hitungStokKemasan.
    for o in kol('penyesuaianKemasan'):
        stok[kunci_kemasan(o.get('namaProduk'), o.get('ukuranKemasan'))]['peny'] += o.get('selisihUnit') or 0
    return {k: {'sisaUnit': v['dibuat'] - v['terjual'] - v['dipakai'] + v['peny'],
                'hppPerUnit': v['nilai'] / v['dibuat'] if v['dibuat'] else 0}
            for k, v in stok.items()}

# ===== Piutang / kasbon / utang pemasok (port hitungPiutang, hitungKasbon, hitungUtangPemasok) =====
def kunci_nama(n): return ' '.join(str(n or '').strip().lower().split())

def piutang(kol):
    peta = collections.defaultdict(lambda: {'kredit': 0, 'saldoAwal': 0, 'bayar': 0, 'dihapus': 0})
    for p in jual_berlaku(kol('penjualan')):
        if p.get('caraBayar') == 'Kredit' and kunci_nama(p.get('namaPelanggan')):
            peta[kunci_nama(p['namaPelanggan'])]['kredit'] += p.get('hargaTotal') or 0
    for m in kol('piutangMutasi'):
        k = kunci_nama(m.get('namaPelanggan'))
        if not k: continue
        n = m.get('nominal') or 0
        t = m.get('tipe')
        if t == 'bayar': peta[k]['bayar'] += n
        elif t == 'saldoAwal': peta[k]['saldoAwal'] += n
        elif t == 'hapusBuku': peta[k]['dihapus'] += n
    return {k: round(v['kredit'] + v['saldoAwal'] - v['bayar'] - v['dihapus'], 2) for k, v in peta.items()}

def kasbon(kol):
    peta = collections.defaultdict(float)
    for m in kol('kasbonMutasi'):
        k = kunci_nama(m.get('namaPegawai'))
        if not k: continue
        n = m.get('nominal') or 0
        peta[k] += -n if m.get('tipe') == 'bayar' else n     # saldoAwal & ambil menambah
    return {k: round(v, 2) for k, v in peta.items()}

def utang_pemasok(kol):
    per = collections.defaultdict(list)
    for k in kol('batchMasuk'):
        if k.get('stokAwal') or k.get('caraBayar') != 'utang': continue
        nm = str(k.get('pemasok') or '').strip()
        if not nm: continue
        per[nm].append({'id': str(k.get('id')), 'tanggal': k.get('tanggal') or '',
                        'nilai': sum((m.get('subtotalHarga') or 0) for m in (k.get('merkList') or [])), 'dibayar': 0.0})
    for m in kol('utangPemasokMutasi'):
        if m.get('tipe') != 'saldoAwal': continue
        nm = str(m.get('pemasok') or '').strip()
        if not nm: continue
        per[nm].append({'id': str(m.get('id')), 'tanggal': m.get('bonTanggal') or '',
                        'nilai': m.get('nominal') or 0, 'dibayar': 0.0})
    for bon in per.values(): bon.sort(key=lambda b: b['tanggal'])
    for m in kol('utangPemasokMutasi'):
        if m.get('tipe') != 'bayar': continue
        bon = per.get(str(m.get('pemasok') or '').strip())
        if not bon: continue
        sisa = m.get('nominal') or 0
        tunjuk = next((b for b in bon if m.get('bonId') and b['id'] == str(m['bonId'])), None)
        if tunjuk:
            ambil = min(sisa, tunjuk['nilai'] - tunjuk['dibayar']); tunjuk['dibayar'] += ambil; sisa -= ambil
        for b in bon:
            if sisa <= 0: break
            ambil = min(sisa, b['nilai'] - b['dibayar']); b['dibayar'] += ambil; sisa -= ambil
    hasil = {}
    for nm, bon in per.items():
        hidup = [{'tanggal': b['tanggal'], 'sisa': round(b['nilai'] - b['dibayar'])}
                 for b in bon if b['nilai'] - b['dibayar'] > 0.5]
        if hidup: hasil[nm] = hidup
    return hasil

# ===== Rantai kas antar tutupHari (verifikasi kasSeharusnya & selisih yang tercatat) =====
def rantai_tutup(kol):
    tutup = sorted(kol('tutupHari'), key=lambda t: t.get('tanggal') or '')
    baris = []
    for i in range(1, len(tutup)):
        a, b = tutup[i - 1], tutup[i]
        titik = ((a.get('kasAwalBesokLaci') if a.get('kasAwalBesokLaci') is not None
                  else (a.get('kasFisikLaci') or 0) - (a.get('setoranOwner') or 0))
                 + (a.get('kasFisikRekening') or 0) + (a.get('kasFisikAmplop') or 0) + (a.get('kasFisikBrankas') or 0))
        cocok = lambda t, d1=a.get('tanggal'), d2=b.get('tanggal'): bool(t) and d1 < t <= d2
        g = arus_kas_kol(cocok)
        # Dokumen setoran malam d2 ditulis SESUDAH kasSeharusnya dihitung & uang dihitung
        # fisik (simpanTutupHari) — keduanya pra-setoran. Jendela gerakan kita memuat
        # setoran d2, jadi ditambahkan balik supaya sebanding dengan angka yang tercatat.
        harusnya = titik + g['masuk'] - g['keluar'] + (b.get('setoranOwner') or 0)
        fisik = ((b.get('kasFisikLaci') or 0) + (b.get('kasFisikRekening') or 0)
                 + (b.get('kasFisikAmplop') or 0) + (b.get('kasFisikBrankas') or 0))
        baris.append({'tanggal': b.get('tanggal'),
                      'seharusnyaAudit': round(harusnya), 'seharusnyaTercatat': b.get('kasSeharusnya'),
                      'selisihAudit': round(fisik - harusnya), 'selisihTercatat': b.get('selisih'),
                      'alasan': b.get('alasanSelisih') or ''})
    return baris

# ===== Laporan utama =====
def utama():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = sys.argv[1]
    d, kol = muat(path)
    global arus_kas_kol
    bayaran = bayaran_biaya_bulanan(kol)
    arus_kas_kol = lambda cocok: arus_kas(kol, cocok, bayaran)
    beda = []
    def cek(nama, a, b, toleransi=0.5):
        if b is None: return
        if abs(a - b) > toleransi: beda.append(f"{nama}: audit {rp(a)} vs tercatat {rp(b)} (selisih {rp(a - b)})")

    print("=" * 72)
    print("AUDIT INDEPENDEN — dari", path, "· versi backup", d.get('versi'), "· diunduh", str(d.get('diunduhPada'))[:19])
    print("=" * 72)

    jual = jual_berlaku(kol('penjualan'))
    tanggal_semua = sorted({p.get('tanggal') for p in jual if p.get('tanggal')})
    print(f"\n[A] Data: {len(kol('penjualan'))} dok penjualan ({len(jual)} berlaku), "
          f"{len(kol('batchMasuk'))} batch, {len(kol('tutupHari'))} tutup hari; "
          f"penjualan {tanggal_semua[0] if tanggal_semua else '-'} s/d {tanggal_semua[-1] if tanggal_semua else '-'}")
    bolong = [p for p in jual if not hpp_tercatat(p)]
    darurat = [p for p in jual if p.get('jenis') == 'kasir_darurat_nominal' and not p.get('dirinciPada')]
    print(f"    HPP bolong: {len(bolong)} trx, omzet {rp(sum((p.get('hargaTotal') or 0) for p in bolong))}"
          f" · darurat belum dirinci: {len(darurat)}")

    # [B] Laba & kas per bulan + identitas + konsistensi hari-vs-bulan
    # Bulan yang diaudit BUKAN cuma bulan yang ada penjualannya: bulan tanpa jualan
    # tapi ada susut stok tetap punya laba (negatif) dan wajib ikut dicetak. Kalau tidak,
    # audit diam persis di bulan yang paling perlu dilihat — pola "audit buta" yang
    # sudah sekali membunuh detektor MINUS (26 Agu 2026).
    bulan_susut = {bulan_dari(x['tanggal']) for x in baris_susut(kol, lambda t: True)}
    bulan_semua = sorted({bulan_dari(t) for t in tanggal_semua} | bulan_susut)
    if len(sys.argv) > 3 and sys.argv[2] == '--bulan': bulan_semua = [sys.argv[3]]
    print("\n[B] Per bulan (laba akrual + arus kas):")
    for bl in bulan_semua:
        n = hari_dalam_bulan(bl)
        L = laba_bersih_rentang(kol, iso_hari(bl, 1), iso_hari(bl, n), bayaran)
        K = arus_kas_kol(lambda t, _b=bl: bulan_dari(t) == _b)
        # konsistensi: jumlah 'per hari' harus = bulan (rumus jatah & tanggal)
        tot_h = {'labaBersih': 0, 'masuk': 0, 'keluar': 0}
        for h in range(1, n + 1):
            iso = iso_hari(bl, h)
            lh = laba_bersih_rentang(kol, iso, iso, bayaran)
            kh = arus_kas_kol(lambda t, _i=iso: t == _i)
            tot_h['labaBersih'] += lh['labaBersih']; tot_h['masuk'] += kh['masuk']; tot_h['keluar'] += kh['keluar']
        ok = (abs(tot_h['labaBersih'] - L['labaBersih']) < 0.5 and abs(tot_h['masuk'] - K['masuk']) < 0.5
              and abs(tot_h['keluar'] - K['keluar']) < 0.5)
        # identitas Ke-Mana-Uang (tampilkanKeManaUang): jumlah suku wajib = kas bersih
        p = K['pos']
        jadi_stok = p['belanja'] + p['berasDiutang'] - L['hpp']
        jadi_piutang = K['kredit'] - p['pelunasan']
        jadi_kasbon = p['kasbonAmbil'] - p['kasbonBayar']
        biaya_nyata = p['biayaBulanan'] + p['harian'] + p['beliKemasan'] + p['beliLiteran'] + p['refund'] - p['tukarMasuk']
        # Pelunasan utang ke owner: kas keluar tanpa beban baru (bebannya sudah diakui
        # waktu belanjanya dicatat), jadi dia berdiri sendiri sebagai suku pengurang —
        # persis seperti bayarBon. Tanpa suku ini identitasnya patah sebesar pelunasan.
        identitas = (L['margin'] + L['omzetBolong'] - jadi_stok - jadi_piutang - jadi_kasbon
                     + p['berasDiutang'] - p['bayarBon'] + p['modalSetor'] - p['setoran'] - p['prive']
                     - p['bayarUtangOwner'] - biaya_nyata)
        id_ok = abs(identitas - K['bersih']) < 0.5
        print(f"  {bl}: omzet {rp(L['omzet'])} · margin {rp(L['margin'])} · laba bersih {rp(L['labaBersih'])}"
              f" · kas {rp(K['masuk'])}−{rp(K['keluar'])}={rp(K['bersih'])}"
              f" · Σhari={'OK' if ok else 'BEDA!'} · identitas={'OK' if id_ok else 'PATAH! ' + rp(identitas - K['bersih'])}")
        if L['susutStok']:
            rinci = baris_susut(kol, lambda t: bool(t) and iso_hari(bl, 1) <= t <= iso_hari(bl, n))
            print(f"      susut & selisih stok {rp(L['susutStok'])} dari {L['nSusut']} penyesuaian: "
                  + ', '.join(str(x['nama']) + ' ' + rp(x['nilaiRp']) for x in rinci))
        if not ok: beda.append(f"{bl}: Σ per-hari ≠ bulan (laba/masuk/keluar)")
        if not id_ok: beda.append(f"{bl}: identitas Ke-Mana-Uang patah sebesar {rp(identitas - K['bersih'])}")

    # [C] Rantai kas antar tutup hari
    print("\n[C] Rantai kas antar Tutup Hari (audit vs tercatat):")
    for r in rantai_tutup(kol):
        tanda = "OK " if (r['seharusnyaTercatat'] is None or abs(r['seharusnyaAudit'] - r['seharusnyaTercatat']) < 1) else "BEDA"
        print(f"  {r['tanggal']}: seharusnya {rp(r['seharusnyaAudit'])}"
              + (f" (tercatat {rp(r['seharusnyaTercatat'])})" if r['seharusnyaTercatat'] is not None else " (tercatat: -)")
              + f" · selisih audit {rp(r['selisihAudit'])} vs tercatat {rp(r['selisihTercatat'] or 0)} [{tanda}]"
              + (f" · alasan: {r['alasan']}" if r['alasan'] else ""))
        if tanda == "BEDA":
            beda.append(f"tutup {r['tanggal']}: kasSeharusnya audit {rp(r['seharusnyaAudit'])} ≠ tercatat {rp(r['seharusnyaTercatat'])}")

    # [D] Stok
    print("\n[D] Stok karung (sisa kg · HPP/kg):")
    for m, v in sorted(stok_karung(kol).items()):
        tanda = " ⚠ MINUS" if v['sisaKg'] < -0.01 else (" ⚠ HPP 0" if v['sisaKg'] > 0 and v['hppPerKg'] <= 0 else "")
        print(f"  {m}: {v['sisaKg']} kg · {rp(v['hppPerKg'])}/kg{tanda}")
        if tanda: beda.append(f"stok karung {m}:{tanda.strip()}")
    print("\n[E] Stok kemasan (sisa unit · HPP/unit):")
    for k, v in sorted(stok_kemasan(kol).items()):
        if v['sisaUnit'] == 0: continue
        tanda = " ⚠ MINUS" if v['sisaUnit'] < 0 else ""
        print(f"  {k}: {v['sisaUnit']} unit · {rp(v['hppPerUnit'])}{tanda}")
        if tanda: beda.append(f"stok kemasan {k}: minus")

    # [F] Piutang, kasbon, utang, amplop, modal
    pt = piutang(kol); tot_pt = sum(v for v in pt.values() if v > 0)
    minus_pt = {k: v for k, v in pt.items() if v < -0.5}
    print(f"\n[F] Piutang: total {rp(tot_pt)} dari {sum(1 for v in pt.values() if v > 0.5)} pelanggan"
          + (f" · ⚠ {len(minus_pt)} pelanggan MINUS (lebih bayar?): {minus_pt}" if minus_pt else ""))
    if minus_pt: beda.append(f"piutang minus: {minus_pt}")
    kb = kasbon(kol)
    print(f"    Kasbon: " + (", ".join(f"{k} {rp(v)}" for k, v in kb.items() if abs(v) > 0.5) or "nol"))
    for k, v in kb.items():
        if v < -0.5: beda.append(f"kasbon {k} minus {rp(v)}")
    up = utang_pemasok(kol)
    tot_up = sum(b['sisa'] for bon in up.values() for b in bon)
    print(f"    Utang pemasok: total {rp(tot_up)}")
    for nm, bon in up.items():
        for b in bon: print(f"      {nm} · bon {b['tanggal'] or '(tanpa tanggal)'} · {rp(b['sisa'])}")
    amplop = sum((-1 if x.get('tipe') == 'ambil' else 1) * (x.get('nominal') or 0) for x in kol('amplopLaba'))
    modal = sum((1 if m.get('tipe') == 'setor' else -1) * (m.get('nominal') or 0) for m in daftar_modal(kol))
    print(f"    Amplop laba: {rp(amplop)} · Modal owner tertanam: {rp(modal)}")

    # [G] Kas seharusnya sekarang (dari tutup terakhir)
    tutup = sorted(kol('tutupHari'), key=lambda t: t.get('tanggal') or '')
    if tutup:
        a = tutup[-1]
        titik = ((a.get('kasAwalBesokLaci') if a.get('kasAwalBesokLaci') is not None
                  else (a.get('kasFisikLaci') or 0) - (a.get('setoranOwner') or 0))
                 + (a.get('kasFisikRekening') or 0) + (a.get('kasFisikAmplop') or 0) + (a.get('kasFisikBrankas') or 0))
        g = arus_kas_kol(lambda t, _d=a.get('tanggal'): bool(t) and t > _d)
        print(f"\n[G] Kas seharusnya SEKARANG (sejak tutup {a.get('tanggal')}): {rp(titik + g['masuk'] - g['keluar'])}"
              f"  = titik {rp(titik)} + masuk {rp(g['masuk'])} − keluar {rp(g['keluar'])}")

    print("\n" + "=" * 72)
    if beda:
        print(f"❗ {len(beda)} TEMUAN:")
        for i, b in enumerate(beda, 1): print(f"  {i}. {b}")
        sys.exit(2)
    print("✅ SEMUA IDENTITAS COCOK — tidak ada selisih di atas toleransi Rp0,5.")

if __name__ == '__main__':
    utama()
