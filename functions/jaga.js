// KABAR TOKO SAAT OWNER PERGI (owner 28 Nov 2026, rules v27) — isi kabar untuk HP owner dari keadaan toko. Murni: tanpa Firebase, tanpa jaringan; diuji di jsc
// oleh alat-uji/uji_tablet_pergi.py. Dipakai functions/index.js (kabarJaga, periksaToko). Setelan owner = dokumen aturanToko/kabarToko (bawaan ATUR_BAWAAN,
// sama dengan baru/js/layar/sistem-logika.js SS_ATUR_BAWAAN.kabarToko). Satu kejadian = satu kabar: yang sudah dikirim dicatat di notifStatus/{tanggal}
// (ditulis fungsi saja; tidak dibaca aplikasi).
'use strict';

const ATUR_BAWAAN = { nyala: { buka: true, gantiJaga: true, telatBuka: true, belumTutup: true, putus: true, nyangkut: true }, jamBuka: '07:00', telatMenit: 30, jamTutup: '21:00', menitPutus: 30 };
const JAM = /^([01]\d|2[0-3]):([0-5]\d)$/;
const menitDari = (j) => { const m = JAM.exec(String(j || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };
const teks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const jamDari = (m) => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');

/** Setelan owner ditimpakan ke bawaan kolom demi kolom (nyala per kabar). Angka / jam yang tidak sah = bawaan. */
function aturKabar(d) {
  const A = JSON.parse(JSON.stringify(ATUR_BAWAAN)); if (!d || typeof d !== 'object') return A;
  Object.keys(A.nyala).forEach((k) => { if (d.nyala && typeof d.nyala[k] === 'boolean') A.nyala[k] = d.nyala[k]; });
  if (menitDari(d.jamBuka) !== null) A.jamBuka = d.jamBuka; if (menitDari(d.jamTutup) !== null) A.jamTutup = d.jamTutup;
  if (Number(d.telatMenit) >= 0 && Number(d.telatMenit) <= 240) A.telatMenit = Math.round(Number(d.telatMenit));
  if (Number(d.menitPutus) >= 10 && Number(d.menitPutus) <= 240) A.menitPutus = Math.round(Number(d.menitPutus));
  return A;
}
/** Jam & tanggal WIB (UTC+7, tanpa musim panas) dari Date. */
function waktuWib(d) {
  const w = new Date(d.getTime() + 7 * 3600 * 1000);
  return { iso: w.toISOString().slice(0, 10), jam: w.toISOString().slice(11, 16), menit: w.getUTCHours() * 60 + w.getUTCMinutes() };
}
const urutJaga = (a, b) => String(a.jam || '').localeCompare(String(b.jam || '')) || String(a.pada || '').localeCompare(String(b.pada || '')) || String(a.id || '').localeCompare(String(b.id || ''));

/**
 * Satu catatan absen jaga baru (jagaLog) → kabar "Toko dibuka" (orang pertama hari itu) atau "Ganti jaga" (orangnya beda dari yang sebelumnya). hariIni = semua
 * catatan jagaLog bertanggal sama (boleh termasuk `baru`). Hasil { judul, isi, tag, jenis } atau null (orang yang sama masuk lagi / kabarnya dimatikan owner).
 */
function pesanJaga(baru, hariIni, aturDok) {
  if (!baru || !teks(baru.nama) || !/^\d{4}-\d{2}-\d{2}$/.test(String(baru.tanggal || ''))) return null;
  const A = aturKabar(aturDok);
  const lain = (hariIni || []).filter((x) => x && String(x.id) !== String(baru.id) && String(x.tanggal) === String(baru.tanggal) && urutJaga(x, baru) < 0).sort(urutJaga);
  const sebelum = lain.length ? lain[lain.length - 1] : null; const nama = teks(baru.nama); const jam = teks(baru.jam);
  if (!sebelum) return A.nyala.buka ? { jenis: 'buka', judul: 'Toko dibuka', isi: nama + ' masuk jaga ' + jam + ' (PIN tablet)', tag: 'jaga-buka-' + baru.tanggal } : null;
  if (teks(sebelum.nama).toLowerCase() === nama.toLowerCase()) return null;
  return A.nyala.gantiJaga ? { jenis: 'gantiJaga', judul: 'Ganti jaga', isi: teks(sebelum.nama) + ' → ' + nama + ' ' + jam + ' (' + teks(sebelum.nama) + ' jaga sejak ' + teks(sebelum.jam) + ')', tag: 'jaga-' + String(baru.id) } : null;
}

/**
 * Pemeriksaan terjadwal (tiap 15 menit di jam toko). k = { kini: Date, atur: dokumen aturanToko/kabarToko | null, jaga: jagaLog hari ini, tutup: true bila
 * tutupHari/{hari ini} ada ATAU tablet sudah mengirim hitungan laci hari ini, perangkat: dokumen perangkatStatus, sudah: { kunci: jam } kabar yang sudah dikirim
 * hari ini, antreLalu: { id perangkat: antrean } dari pemeriksaan sebelumnya }. Hasil { kabar: [{ kunci, judul, isi, tag }] yang BELUM dikirim hari ini (kunci dicatat
 * pemanggil), pulih: [kunci putus yang boleh dikabarkan lagi karena tabletnya berdenyut lagi], antre: { id: antrean } untuk pemeriksaan berikutnya }.
 *  - telatBuka: lewat jamBuka + telatMenit belum ada PIN di tablet
 *  - belumTutup: lewat jamTutup hari belum ditutup & belum ada hitungan laci
 *  - putus: tablet (aplikasi baru, akun staf) sudah berdenyut hari ini lalu diam > menitPutus, selama jam toko
 *  - nyangkut: denyut terakhir tablet menyebut catatan ditolak server (gagal > 0) atau antrean > 0 — dikabarkan sekali per hari per perangkat
 */
function periksaToko(k) {
  const A = aturKabar(k && k.atur); const W = waktuWib(k.kini); const sudah = (k && k.sudah) || {}; const out = []; const pulih = []; const antre = {};
  const tambah = (kunci, judul, isi) => { if (!sudah[kunci]) out.push({ kunci, judul, isi, tag: 'toko-' + W.iso + '-' + kunci }); };
  const buka = menitDari(A.jamBuka); const tutup = menitDari(A.jamTutup); const dalamJam = W.menit >= buka && W.menit < tutup;
  const jaga = (k.jaga || []).filter((x) => x && String(x.tanggal) === W.iso);
  if (A.nyala.telatBuka && W.menit >= buka + A.telatMenit && W.menit < tutup && !jaga.length) tambah('telatBuka', 'Toko belum dibuka', 'Lewat ' + jamDari(buka + A.telatMenit) + ' belum ada yang masuk PIN di tablet');
  if (A.nyala.belumTutup && W.menit >= tutup && !k.tutup && jaga.length) tambah('belumTutup', 'Hari belum ditutup', 'Lewat ' + A.jamTutup + ' belum ada hitungan laci / tutup hari untuk ' + W.iso);
  (k.perangkat || []).forEach((p) => {
    // denyut akun staf ber-id '<perangkat>~<uid>' (firebase.js idDenyut); denyut owner & sistem lama tanpa '~' — bukan tablet yang dijaga
    if (!p || p.aplikasi !== 'baru' || String(p.id || '').indexOf('~') < 0 || !p.pada) return;
    const pada = new Date(p.pada); if (!isFinite(pada.getTime())) return; const P = waktuWib(pada); if (P.iso !== W.iso) return;
    const nama = teks(p.nama) || 'tablet'; const diam = Math.round((k.kini.getTime() - pada.getTime()) / 60000); antre[p.id] = Number(p.antrean) || 0;
    if (diam <= A.menitPutus && sudah['putus-' + p.id]) pulih.push('putus-' + p.id);   // berdenyut lagi: putus berikutnya dikabarkan lagi
    if (A.nyala.putus && dalamJam && diam > A.menitPutus) tambah('putus-' + p.id, 'Tablet putus', nama + ' tidak berdenyut sejak ' + P.jam + ' (' + diam + ' menit) — mati, tanpa internet, atau aplikasi ditutup');
    if (A.nyala.nyangkut && Number(p.gagal) > 0) tambah('gagal-' + p.id, 'Catatan ditolak server', nama + ': ' + Number(p.gagal) + ' catatan ditolak server — buka Menu › Perangkat & antrean di HP');
    else if (A.nyala.nyangkut && Number(p.antrean) > 0 && diam <= A.menitPutus) {
      // antrean > 0 di denyut terakhir: baru dikabarkan bila sudah tercatat menunggu sejak pemeriksaan sebelumnya (k.antreLalu = { id: jumlah }), bukan kiriman yang sedang berjalan
      if (k.antreLalu && Number(k.antreLalu[p.id]) > 0) tambah('antre-' + p.id, 'Catatan nyangkut', nama + ': ' + Number(p.antrean) + ' catatan belum sampai server sejak pemeriksaan sebelumnya');
    }
  });
  return { kabar: out, pulih, antre };
}

/** Ringkas omzet satu hari dari baris penjualan (dokumen per baris nota): Σ hargaTotal baris yang tidak dibatalkan + jumlah nota (trxId unik). Penjualan kotor — retur belum dikurangi. */
function omzetHari(baris) {
  let rp = 0; const nota = {};
  (baris || []).forEach((p) => { if (!p || p.dibatalkan) return; rp += Number(p.hargaTotal) || 0; if (p.trxId !== undefined && p.trxId !== null) nota[String(p.trxId)] = true; });
  return { rp: Math.round(rp), nota: Object.keys(nota).length };
}

module.exports = { ATUR_BAWAAN, aturKabar, waktuWib, pesanJaga, periksaToko, omzetHari };
