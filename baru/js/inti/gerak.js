// GERAK — pembantu kecil untuk layar yang HIDUP (permintaan owner 13 Sep: "lebih interaktif, lebih hidup, ada animasi motion").
// Aturan papan: gerak = kejadian (bukan putaran tanpa henti), kurva tenggelam, tab tersembunyi & "kurangi gerakan" dihormati.
const tenggelam = (t) => 1 - Math.pow(1 - t, 3);
const diam = () => document.hidden || (typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches);

/** Jalankan satu animasi-kelas sekali (dipicu ulang walau kelasnya sama). */
export function sekali(el, kelas, lamaMs) { if (!el) return; el.classList.remove(kelas); void el.offsetWidth; el.classList.add(kelas); setTimeout(() => el.classList.remove(kelas), lamaMs); }

/**
 * Angka bergulir: tiap elemen ber-atribut data-gulir="<angka>" yang nilainya berubah sejak gambar terakhir, teksnya
 * dihitung naik/turun dari nilai lama ke nilai baru. Nilai AKHIR selalu benar (penjaga waktu + tab tersembunyi).
 */
export function gulirkan(akar, format, lamaMs) {
  // tinjauan 29 Sep: dipanggil dari dalam bingkai (penjadwal) → morf sudah menulis angka AKHIR, dan langkah pertama baru jalan di bingkai berikutnya
  // → satu bingkai angka akhir lalu melompat ke angka lama. Kini teks langsung disetel ke angka awal; morf ulang di tengah gulir (dari === ke)
  // menulis kembali angka yang sedang tampil; gulir baru di tengah gulir melanjutkan dari angka yang sedang tampil.
  akar.querySelectorAll('[data-gulir]').forEach((el) => {
    const ke = Number(el.getAttribute('data-gulir')); const dari = el.__angka;
    if (el.__gulir && dari === ke) { el.textContent = format(el.__tampil); return; }
    el.__angka = ke;
    if (dari === undefined || dari === ke || !isFinite(ke)) return;
    cancelAnimationFrame(el.__raf || 0); clearTimeout(el.__jaga || 0);
    const awal = el.__gulir && isFinite(el.__tampil) ? el.__tampil : dari;
    if (diam()) { el.__gulir = false; el.textContent = format(ke); return; }
    const lama = lamaMs || 520; const mulai = performance.now();
    el.__gulir = true; el.__tampil = awal; el.textContent = format(awal);
    const langkah = (kini) => { const t = Math.max(0, Math.min(1, (kini - mulai) / lama)); const n = Math.round(awal + (ke - awal) * tenggelam(t)); el.__tampil = n; el.textContent = format(n);
      if (t < 1) el.__raf = requestAnimationFrame(langkah); else el.__gulir = false; };
    el.__raf = requestAnimationFrame(langkah);
    el.__jaga = setTimeout(() => { cancelAnimationFrame(el.__raf || 0); el.__gulir = false; el.__tampil = ke; el.textContent = format(ke); }, lama + 200);
  });
}

/** Tetes emas terbang dari satu titik layar ke elemen tujuan (barang masuk keranjang, nota mendarat). */
export function terbangkan(dari, keEl) {
  if (!dari || !keEl || diam()) return;
  let t = document.getElementById('tetesGerak');
  if (!t) { t = document.createElement('div'); t.id = 'tetesGerak'; t.className = 'tetes-gerak'; document.body.appendChild(t); }
  const b = keEl.getBoundingClientRect();
  t.style.left = (dari.x - 6) + 'px'; t.style.top = (dari.y - 6) + 'px';
  t.style.setProperty('--tx', (b.left + b.width / 2 - dari.x) + 'px'); t.style.setProperty('--ty', (b.top + b.height / 2 - dari.y) + 'px');
  sekali(t, 'terbang', 640);
}
export const tengah = (el) => { const r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };
