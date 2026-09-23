// SALINAN ANTRE (putaran 23, owner poin 7b + jawaban 3, 24 Sep 2026). Firebase di peramban cuma memberi tahu penolakan server ke tab yang
// menulisnya SELAMA tab itu terbuka; tablet yang dimuat ulang saat offline kehilangan kabar itu — tulisan yang ditolak lenyap diam-diam.
// Maka tiap kiriman disalin di perangkat SEBELUM dikirim:
//   · tahan dimuat ulang (localStorage), berbatas ukuran — penuh = kiriman baru DITOLAK di perangkat, tidak ada salinan lama yang dibuang;
//   · dihapus HANYA setelah server mengonfirmasi (commit berhasil, atau dokumennya terbukti ada di server sesudah sinkron);
//   · ditolak server → ditandai 'ditolak' + alasannya, tampil di Sistem › Perangkat; owner memutuskan: tulis ulang atas namanya, atau buang.
// Logika tanpa DOM; penyimpan disuntikkan ({ baca(k), tulis(k, v) }) supaya bisa diuji di jsc (alat-uji/uji_akses_baru.py).
export const KUNCI_ANTRE = 'miqbal_baru_antre_v1';
export const BATAS_ENTRI = 300;
export const BATAS_KB = 900;   // localStorage peramban ±5 MB dan dipakai bersama sistem lama (kuota-cadangan-lokal) — salinan antre dijaga jauh di bawahnya

export function buatAntre(penyimpan, sesi) {
  const baca = () => { try { const v = penyimpan.baca(KUNCI_ANTRE); const a = v ? JSON.parse(v) : []; return Array.isArray(a) ? a : []; } catch (e) { return []; } };
  const simpan = (a) => { const teks = JSON.stringify(a); if (teks.length / 1024 > BATAS_KB) return false; try { penyimpan.tulis(KUNCI_ANTRE, teks); return true; } catch (e) { return false; } };
  const ubah = (id, f) => { const a = baca(); const i = a.findIndex((x) => x.id === id); if (i < 0) return false; f(a, i); return simpan(a); };
  const api = {
    semua: baca,
    belumTerkirim: () => baca().filter((x) => x.keadaan === 'antre'),
    ditolak: () => baca().filter((x) => x.keadaan === 'ditolak'),
    /** entri = { id, pada, akunUid, akunNama, peran, dokumen: [{ koleksi, data }] }. Kembali { ok } atau { tolak } (penuh / tidak bisa disimpan). */
    tambah(entri) {
      const a = baca();
      if (a.length >= BATAS_ENTRI) return { tolak: 'Salinan antre di perangkat ini penuh (' + a.length + ' kiriman belum terkirim / ditolak). Sambungkan internet atau selesaikan yang ditolak di Sistem › Perangkat dulu.' };
      a.push(Object.assign({}, entri, { keadaan: 'antre', sesi: sesi || '' }));
      return simpan(a) ? { ok: true } : { tolak: 'Salinan antre di perangkat ini sudah terlalu besar (' + BATAS_KB + ' KB). Sambungkan internet dulu supaya yang lama terkirim.' };
    },
    konfirmasi: (id) => { const a = baca().filter((x) => x.id !== id); return simpan(a); },
    tandaiDitolak: (id, alasan, padaIso) => ubah(id, (a, i) => { a[i] = Object.assign({}, a[i], { keadaan: 'ditolak', alasan: String(alasan || 'ditolak server'), padaTolak: padaIso || '' }); }),
    /** Hanya yang DITOLAK yang boleh dibuang (keputusan owner); yang masih antre tidak pernah dibuang dari sini. */
    buang(id) { const a = baca(); const x = a.find((y) => y.id === id); if (!x || x.keadaan !== 'ditolak') return false; return simpan(a.filter((y) => y.id !== id)); },
    /**
     * Sesudah tersambung & semua tulisan tertunda diselesaikan server: entri 'antre' dari SESI LAIN (tab yang menulisnya sudah mati, jadi tidak ada
     * yang menunggu jawabannya) dicocokkan ke dokumen di server. cekServer(koleksi, id, data) → true (ada & sama/lebih baru), false (tidak ada / kalah),
     * null (belum bisa dipastikan). Semua true → dikonfirmasi; ada yang false → ditolak; ada null → dibiarkan.
     */
    cocokkanSesudahSinkron(cekServer, padaIso) {
      const hasil = { dikonfirmasi: 0, ditolak: 0, ditunda: 0 };
      baca().filter((x) => x.keadaan === 'antre' && x.sesi !== (sesi || '')).forEach((x) => {
        const cek = (x.dokumen || []).map((d) => cekServer(d.koleksi, String(d.data && d.data.id), d.data));
        if (cek.some((c) => c === null)) { hasil.ditunda += 1; return; }
        if (cek.every((c) => c === true)) { api.konfirmasi(x.id); hasil.dikonfirmasi += 1; } else { api.tandaiDitolak(x.id, 'ditolak server saat sinkron (server tidak mengirim alasannya; perangkat sempat dimuat ulang)', padaIso); hasil.ditolak += 1; }
      });
      return hasil;
    },
  };
  return api;
}
/** Cek bawaan untuk cocokkanSesudahSinkron: dokumen di cache (yang SUDAH bebas tulisan tertunda) ada, dan diubahPada-nya sama atau lebih baru. */
export function cekDariCache(ambilDok) {
  return (koleksi, id, data) => { const d = ambilDok(koleksi, id); if (!d) return false; const a = String(d.diubahPada || ''), b = String((data && data.diubahPada) || ''); return a && b ? a >= b : null; };
}
