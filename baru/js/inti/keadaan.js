// Penyimpan keadaan layar: satu objek, diubah lewat setel(), pendengar dipanggil sesudahnya.
// Sengaja sederhana — layar Jual di sistem baru = keadaan → gambar, tanpa DOM yang disentuh tangan.
export function buatKeadaan(awal) {
  let s = Object.assign({}, awal);
  const pendengar = new Set();
  let tunda = null;
  const beri = () => { tunda = null; pendengar.forEach((f) => f(s)); };
  return {
    baca: () => s,
    setel(patch) {
      s = Object.assign({}, s, typeof patch === 'function' ? patch(s) : patch);
      // gambar sekali per giliran, walau setel() dipanggil beberapa kali berturut-turut
      if (typeof queueMicrotask === 'function') { if (!tunda) { tunda = true; queueMicrotask(beri); } }
      else beri();
    },
    dengar(f) { pendengar.add(f); return () => pendengar.delete(f); },
  };
}
