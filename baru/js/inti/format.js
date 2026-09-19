// Pemformat angka & tanggal — satu tempat, dipakai semua layar. Bahasa toko: "Rp", "rb", "jt", "kg", "L".
export const RP = (n) => (n < 0 ? '−' : '') + 'Rp' + Math.round(Math.abs(n || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const ANGKA = (n) => String(Math.round(n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const RIBU = (n) => (Math.abs(n) < 1000 ? String(Math.round(n)) : Math.abs(n) >= 1e6
  ? (n / 1e6).toFixed(2).replace(/\.?0+$/, '').replace('.', ',') + ' jt'
  : (n / 1000).toFixed(1).replace(/\.0$/, '').replace('.', ',') + ' rb');
export const KG = (n) => (Math.round((n || 0) * 100) / 100).toString().replace('.', ',') + ' kg';
export const LITER = (n) => (Math.round((n || 0) * 10) / 10).toString().replace('.', ',') + ' L';
export const DESIMAL = (n) => (Math.round((n || 0) * 100) / 100).toString().replace('.', ',');

export function hariIniIso(d) {
  d = d || new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
export function jamKini(d) { d = d || new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }
const BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
export function tanggalPendek(iso) {
  if (!iso) return '';
  const [y, m, d] = String(iso).split('-').map(Number);
  return d + ' ' + (BULAN[m - 1] || '') + (y ? ' ' + y : '');
}
