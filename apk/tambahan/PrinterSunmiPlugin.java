package id.miqbal.tokoberas;

// PRINTER SUNMI (paket S1, 19 Nov 2026) — plugin Capacitor "PrinterSunmi": printer struk/label SUNMI (NT32x) lewat SDK RESMI SUNMI
// (com.sunmi:external-printerlibrary2, dokumen "Cloud Printer SDK for Android"; NT32x butuh firmware ≥ 4.1.19 & SUNMI APP ≥ 4.1.32).
// Bedanya dengan CetakUsb (kirim byte buta): SDK ini MENJAWAB — keadaan printer (kertas habis, tutup terbuka, macet, panas) dan hasil
// cetak yang sungguh (selesai / gagal karena apa). Plugin ini tetap HANYA mengirim byte ESC/POS yang sudah disusun halaman (escpos.js):
// tidak menyusun struk, tidak membaca data toko.
// Paket S4 (19 Nov 2026): (1) BLUETOOTH — isi `lewat: "bt"` menyambung printer yang SUDAH dipasangkan di Setelan tablet (nama berawalan
// CloudPrint_) lewat CloudPrinterBuilder.buildPrinter(nama, mac); pustaka sendiri menolak perangkat yang belum dipasangkan. Tidak ada
// pencarian Bluetooth di sini (pencarian butuh izin lokasi); (2) MODE KERTAS NT32x — setPrintMode(1 struk | 2 label | 3 tanpa alas) dan
// getPrintMode; (3) LABEL — sendTSPLData: perintah TSPL dikirim apa adanya, printer label tidak mengabari hasil cetak.
//
// Kode tolakan (dibaca inti/printer.js):
//   BELUM_KIRIM  = belum ada satu byte pun sampai ke printer → halaman boleh jatuh ke jalur CetakUsb tanpa takut struk dobel
//   PRINTER_xxx  = printer menjawab ada halangan (xxx = nama CloudPrinterStatus) atau diam sesudah data dikirim → JANGAN kirim ulang sendiri

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.content.Context;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Base64;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;
import com.sunmi.externalprinterlibrary2.ConnectCallback;
import com.sunmi.externalprinterlibrary2.PropCallback;
import com.sunmi.externalprinterlibrary2.ResultCallback;
import com.sunmi.externalprinterlibrary2.SearchCallback;
import com.sunmi.externalprinterlibrary2.SearchMethod;
import com.sunmi.externalprinterlibrary2.StatusCallback;
import com.sunmi.externalprinterlibrary2.SunmiPrinterManager;
import com.sunmi.externalprinterlibrary2.printer.CloudPrinter;
import com.sunmi.externalprinterlibrary2.printer.CloudPrinterBuilder;
import com.sunmi.externalprinterlibrary2.printer.CloudPrinterInfo;
import com.sunmi.externalprinterlibrary2.style.CloudPrinterStatus;

import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

@CapacitorPlugin(name = "PrinterSunmi", permissions = {
        // Android 12+: menyambung perangkat Bluetooth yang sudah dipasangkan butuh izin ini saat jalan (izin manifest-nya dibawa pustaka SUNMI)
        @Permission(alias = "bluetooth", strings = { Manifest.permission.BLUETOOTH_CONNECT })
})
public class PrinterSunmiPlugin extends Plugin {
    private static final String BELUM_KIRIM = "BELUM_KIRIM";
    private static final String AWALAN_BT = "CloudPrint_";   // nama Bluetooth printer cloud SUNMI (penyaring yang sama dengan pustakanya)
    private static final int BATAS_CARI_MS = 6000;
    private static final int BATAS_SAMBUNG_MS = 6000;
    private static final int BATAS_SAMBUNG_BT_MS = 12000;
    private static final int BATAS_STATUS_MS = 4000;
    private static final int BATAS_CETAK_MS = 30000;
    private static final int BATAS_CETAK_BT_MS = 60000;   // struk bergambar lewat Bluetooth lebih lama sampainya

    private final Handler utama = new Handler(Looper.getMainLooper());
    private volatile CloudPrinter printer;
    private volatile boolean printerBt = false;   // sambungan `printer` sekarang lewat Bluetooth?

    private interface Lanjut {
        void jalan(CloudPrinter p);
    }

    private interface LanjutStatus {
        void jalan(CloudPrinterStatus s);
    }

    private static String hex(int n) {
        return String.format(Locale.US, "0x%04x", n);
    }

    private static String namaStatus(CloudPrinterStatus s) {
        return s == null ? "UNKNOWN" : s.name();
    }

    /** Kalimat untuk orang toko, bukan nama enum. */
    private static String kalimat(CloudPrinterStatus s) {
        if (s == null) return "keadaan printer tidak diketahui";
        switch (s) {
            case RUNNING: return "siap";
            case NEAR_OUT_PAPER: return "kertas hampir habis";
            case OUT_PAPER: return "kertas habis";
            case JAM_PAPER: return "kertas macet";
            case PICK_PAPER: return "struk sebelumnya belum diambil";
            case COVER: return "tutup printer terbuka";
            case OVER_HOT: return "kepala cetak terlalu panas";
            case MOTOR_HOT: return "motor printer terlalu panas";
            case OFFLINE: return "printer tidak tersambung";
            default: return "keadaan printer tidak diketahui";
        }
    }

    /** Halangan pasti: mencetak sekarang percuma. */
    private static boolean menghalangi(CloudPrinterStatus s) {
        return s == CloudPrinterStatus.OUT_PAPER || s == CloudPrinterStatus.JAM_PAPER || s == CloudPrinterStatus.COVER
                || s == CloudPrinterStatus.OVER_HOT || s == CloudPrinterStatus.MOTOR_HOT;
    }

    /** Printer tidak bisa dipastikan lewat SDK → serahkan ke jalur lain. */
    private static boolean takPasti(CloudPrinterStatus s) {
        return s == null || s == CloudPrinterStatus.OFFLINE || s == CloudPrinterStatus.UNKNOWN;
    }

    private void lepasDiam() {
        CloudPrinter p = printer;
        printer = null;
        if (p == null) return;
        try {
            p.release(getContext());
        } catch (Exception ignored) {
            // sudah lepas
        }
    }

    private void hentikanCari(Context ctx) {
        try {
            SunmiPrinterManager.getInstance().stopSearch(ctx, SearchMethod.USB);
        } catch (Exception ignored) {
            // pencarian sudah berhenti
        }
    }

    private static boolean mintaBt(PluginCall call) {
        return "bt".equals(call.getString("lewat"));
    }

    private boolean izinBt() {
        return Build.VERSION.SDK_INT < 31 || getPermissionState("bluetooth") == PermissionState.GRANTED;
    }

    private BluetoothAdapter adaptorBt() {
        try {
            BluetoothManager m = (BluetoothManager) getContext().getSystemService(Context.BLUETOOTH_SERVICE);
            return m == null ? null : m.getAdapter();
        } catch (Exception e) {
            return null;
        }
    }

    /** Printer SUNMI yang sudah dipasangkan: yang ber-MAC `mac` bila diisi, selain itu yang pertama bernama CloudPrint_… null = tidak ada. */
    @SuppressLint("MissingPermission")
    private BluetoothDevice pilihBt(BluetoothAdapter a, String mac) {
        try {
            for (BluetoothDevice d : a.getBondedDevices()) {
                String nama = d.getName();
                if (nama == null || !nama.startsWith(AWALAN_BT)) continue;
                if (mac == null || mac.isEmpty() || mac.equalsIgnoreCase(d.getAddress())) return d;
            }
        } catch (Exception e) {
            // izin dicabut di tengah jalan → dianggap tidak ada
        }
        return null;
    }

    /** Sambungkan printer SUNMI yang sudah dipasangkan lewat Bluetooth. Gagal di sini = BELUM_KIRIM. */
    @SuppressLint("MissingPermission")
    private void siapkanBt(final PluginCall call, final Lanjut lanjut) {
        if (!izinBt()) {
            call.reject("Izin Bluetooth belum diberikan ke aplikasi ini — buka layar Perangkat lalu tekan Periksa Bluetooth", BELUM_KIRIM);
            return;
        }
        BluetoothAdapter a = adaptorBt();
        if (a == null) {
            call.reject("Tablet ini tidak punya Bluetooth", BELUM_KIRIM);
            return;
        }
        boolean nyala;
        try {
            nyala = a.isEnabled();
        } catch (Exception e) {
            nyala = false;
        }
        if (!nyala) {
            call.reject("Bluetooth tablet mati — nyalakan di Setelan tablet", BELUM_KIRIM);
            return;
        }
        BluetoothDevice d = pilihBt(a, call.getString("mac"));
        if (d == null) {
            call.reject("Belum ada printer SUNMI yang dipasangkan lewat Bluetooth — pasangkan dulu di Setelan tablet › Bluetooth (namanya berawalan " + AWALAN_BT + ")", BELUM_KIRIM);
            return;
        }
        final CloudPrinter p;
        try {
            p = CloudPrinterBuilder.buildPrinter(d.getName(), d.getAddress());
        } catch (Exception e) {
            call.reject("Printer Bluetooth tidak bisa disiapkan: " + e.getMessage(), BELUM_KIRIM);
            return;
        }
        if (p == null) {
            call.reject("Printer Bluetooth tidak bisa disiapkan", BELUM_KIRIM);
            return;
        }
        sambung(call, p, lanjut, true);
    }

    /** Pastikan ada printer SUNMI yang tersambung — lewat USB (bawaan) atau Bluetooth (`lewat: "bt"`) — lalu jalankan `lanjut`. Gagal di sini = BELUM_KIRIM. */
    private void siapkan(final PluginCall call, final Lanjut lanjut) {
        final Context ctx = getContext();
        final boolean bt = mintaBt(call);
        final CloudPrinter ada = printer;
        try {
            if (ada != null && printerBt == bt && ada.isConnected()) {
                lanjut.jalan(ada);
                return;
            }
        } catch (Exception e) {
            // sambungan lama tidak bisa ditanya → cari ulang
        }
        // pindah jalur (kabel ↔ Bluetooth): sambungan lama dilepas dulu supaya printer tidak dipegang dua kali
        if (ada != null && printerBt != bt) lepasDiam();
        if (bt) {
            siapkanBt(call, lanjut);
            return;
        }
        final AtomicBoolean selesai = new AtomicBoolean(false);
        final Runnable habis = () -> {
            if (!selesai.compareAndSet(false, true)) return;
            hentikanCari(ctx);
            call.reject("Printer SUNMI tidak ditemukan di USB — pastikan printer menyala dan tercolok ke stand", BELUM_KIRIM);
        };
        utama.postDelayed(habis, BATAS_CARI_MS);
        try {
            SunmiPrinterManager.getInstance().searchCloudPrinter(ctx, SearchMethod.USB, new SearchCallback() {
                @Override
                public void onFound(CloudPrinter p) {
                    if (p == null || !selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    hentikanCari(ctx);
                    sambung(call, p, lanjut, false);
                }
            });
        } catch (Exception e) {
            if (!selesai.compareAndSet(false, true)) return;
            utama.removeCallbacks(habis);
            call.reject("Pencarian printer SUNMI gagal: " + e.getMessage(), BELUM_KIRIM);
        }
    }

    private void sambung(final PluginCall call, final CloudPrinter p, final Lanjut lanjut, final boolean bt) {
        final AtomicBoolean selesai = new AtomicBoolean(false);
        final Runnable habis = () -> {
            if (!selesai.compareAndSet(false, true)) return;
            call.reject(bt ? "Printer SUNMI tidak mau tersambung lewat Bluetooth — pastikan printer menyala dan dekat dengan tablet"
                    : "Printer SUNMI ditemukan tapi tidak mau tersambung — cabut-colok kabel USB printer lalu coba lagi", BELUM_KIRIM);
        };
        utama.postDelayed(habis, bt ? BATAS_SAMBUNG_BT_MS : BATAS_SAMBUNG_MS);
        try {
            p.connect(getContext(), new ConnectCallback() {
                @Override
                public void onConnect() {
                    printer = p;
                    printerBt = bt;
                    if (!selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    lanjut.jalan(p);
                }

                @Override
                public void onFailed(String sebab) {
                    if (printer == p) printer = null;
                    if (!selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    call.reject("Printer SUNMI tidak bisa disambung: " + sebab, BELUM_KIRIM);
                }

                @Override
                public void onDisConnect() {
                    if (printer == p) printer = null;
                }
            });
        } catch (Exception e) {
            if (!selesai.compareAndSet(false, true)) return;
            utama.removeCallbacks(habis);
            call.reject("Printer SUNMI tidak bisa disambung: " + e.getMessage(), BELUM_KIRIM);
        }
    }

    /** Tanya keadaan printer. Tidak menjawab dalam batas waktu = null (tak pasti). */
    private void tanya(final CloudPrinter p, final LanjutStatus lanjut) {
        final AtomicBoolean selesai = new AtomicBoolean(false);
        final Runnable habis = () -> {
            if (selesai.compareAndSet(false, true)) lanjut.jalan(null);
        };
        utama.postDelayed(habis, BATAS_STATUS_MS);
        try {
            p.getDeviceState(new StatusCallback() {
                @Override
                public void onResult(CloudPrinterStatus s) {
                    if (!selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    lanjut.jalan(s);
                }
            });
        } catch (Exception e) {
            if (!selesai.compareAndSet(false, true)) return;
            utama.removeCallbacks(habis);
            lanjut.jalan(null);
        }
    }

    private JSObject kartu(CloudPrinter p) {
        JSObject o = new JSObject();
        try {
            CloudPrinterInfo i = p.getCloudPrinterInfo();
            if (i != null) {
                o.put("nama", i.name);
                o.put("vid", hex(i.vid));
                o.put("pid", hex(i.pid));
                o.put("lewat", printerBt ? "bt" : "usb");
            }
        } catch (Exception ignored) {
            // kartu nama printer tidak wajib
        }
        return o;
    }

    /** Keadaan printer sekarang: { status, kalimat, siap, menghalangi, nama, vid, pid, sdk }. */
    @PluginMethod
    public void status(final PluginCall call) {
        siapkan(call, p -> tanya(p, s -> {
            JSObject o = kartu(p);
            o.put("status", namaStatus(s));
            o.put("kalimat", kalimat(s));
            o.put("siap", !takPasti(s) && !menghalangi(s));
            o.put("menghalangi", menghalangi(s));
            try {
                o.put("sdk", SunmiPrinterManager.getInstance().getVersionInfo());
            } catch (Exception ignored) {
                // versi SDK tidak wajib
            }
            call.resolve(o);
        }));
    }

    /** Cetak: { data: base64 byte ESC/POS } → { byte, nama, vid, pid, peringatan? }. Keadaan printer diperiksa DULU. */
    @PluginMethod
    public void cetak(final PluginCall call) {
        String data = call.getString("data");
        if (data == null || data.isEmpty()) {
            call.reject("Data cetak kosong", BELUM_KIRIM);
            return;
        }
        final byte[] isi;
        try {
            isi = Base64.decode(data, Base64.DEFAULT);
        } catch (IllegalArgumentException e) {
            call.reject("Data cetak rusak (base64)", BELUM_KIRIM);
            return;
        }
        siapkan(call, p -> tanya(p, s -> {
            if (takPasti(s)) {
                lepasDiam();
                call.reject("Printer SUNMI tidak menjawab saat ditanya keadaannya (" + kalimat(s) + ")", BELUM_KIRIM);
                return;
            }
            if (menghalangi(s)) {
                call.reject("Printer belum bisa mencetak: " + kalimat(s), "PRINTER_" + namaStatus(s));
                return;
            }
            kirim(call, p, isi, s == CloudPrinterStatus.NEAR_OUT_PAPER ? "Kertas printer hampir habis" : null);
        }));
    }

    private void kirim(final PluginCall call, final CloudPrinter p, final byte[] isi, final String peringatan) {
        final AtomicBoolean selesai = new AtomicBoolean(false);
        try {
            p.clearTransBuffer();
            p.appendRawData(isi);
        } catch (Exception e) {
            lepasDiam();
            call.reject("Data cetak tidak bisa disiapkan: " + e.getMessage(), BELUM_KIRIM);
            return;
        }
        final Runnable habis = () -> {
            if (!selesai.compareAndSet(false, true)) return;
            call.reject("Data sudah dikirim tapi printer tidak mengabari hasilnya — lihat kertasnya dulu sebelum mencetak ulang", "PRINTER_DIAM");
        };
        utama.postDelayed(habis, printerBt ? BATAS_CETAK_BT_MS : BATAS_CETAK_MS);
        try {
            p.commitTransBuffer(new ResultCallback() {
                @Override
                public void onComplete() {
                    if (!selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    JSObject o = kartu(p);
                    o.put("byte", isi.length);
                    if (peringatan != null) o.put("peringatan", peringatan);
                    call.resolve(o);
                }

                @Override
                public void onFailed(CloudPrinterStatus s) {
                    if (!selesai.compareAndSet(false, true)) return;
                    utama.removeCallbacks(habis);
                    call.reject("Cetak gagal: " + kalimat(s), "PRINTER_" + namaStatus(s));
                }
            });
        } catch (Exception e) {
            if (!selesai.compareAndSet(false, true)) return;
            utama.removeCallbacks(habis);
            lepasDiam();
            call.reject("Data cetak tidak terkirim: " + e.getMessage(), BELUM_KIRIM);
        }
    }

    /** Buka laci uang yang tercolok ke port RJ12 printer. Dipanggil halaman HANYA untuk bayar tunai (paket S2). */
    @PluginMethod
    public void bukaLaci(final PluginCall call) {
        siapkan(call, p -> {
            final AtomicBoolean selesai = new AtomicBoolean(false);
            final Runnable habis = () -> {
                if (selesai.compareAndSet(false, true)) call.reject("Printer tidak mengabari hasil perintah laci", "PRINTER_DIAM");
            };
            try {
                p.clearTransBuffer();
                p.openCashBox();
                utama.postDelayed(habis, BATAS_STATUS_MS);
                p.commitTransBuffer(new ResultCallback() {
                    @Override
                    public void onComplete() {
                        if (!selesai.compareAndSet(false, true)) return;
                        utama.removeCallbacks(habis);
                        call.resolve(kartu(p));
                    }

                    @Override
                    public void onFailed(CloudPrinterStatus s) {
                        if (!selesai.compareAndSet(false, true)) return;
                        utama.removeCallbacks(habis);
                        call.reject("Perintah laci gagal: " + kalimat(s), "PRINTER_" + namaStatus(s));
                    }
                });
            } catch (Exception e) {
                if (!selesai.compareAndSet(false, true)) return;
                utama.removeCallbacks(habis);
                call.reject("Perintah laci tidak terkirim: " + e.getMessage(), BELUM_KIRIM);
            }
        });
    }

    // ---------- paket S4: Bluetooth ----------
    /** Printer SUNMI yang sudah dipasangkan ke tablet lewat Bluetooth: { ada, izin, nyala, daftar: [{ nama, mac }] }. Meminta izin Android bila belum ada. */
    @PluginMethod
    public void bt(PluginCall call) {
        if (Build.VERSION.SDK_INT >= 31 && getPermissionState("bluetooth") != PermissionState.GRANTED) {
            requestPermissionForAlias("bluetooth", call, "sesudahIzinBt");
            return;
        }
        jawabBt(call);
    }

    @PermissionCallback
    private void sesudahIzinBt(PluginCall call) {
        jawabBt(call);
    }

    @SuppressLint("MissingPermission")
    private void jawabBt(PluginCall call) {
        JSObject o = new JSObject();
        boolean izin = izinBt();
        BluetoothAdapter a = adaptorBt();
        boolean nyala = false;
        JSArray daftar = new JSArray();
        if (a != null && izin) {
            try {
                nyala = a.isEnabled();
                if (nyala) {
                    for (BluetoothDevice d : a.getBondedDevices()) {
                        String nama = d.getName();
                        if (nama == null || !nama.startsWith(AWALAN_BT)) continue;
                        JSObject x = new JSObject();
                        x.put("nama", nama);
                        x.put("mac", d.getAddress());
                        daftar.put(x);
                    }
                }
            } catch (Exception e) {
                izin = false;
            }
        }
        o.put("ada", a != null);
        o.put("izin", izin);
        o.put("nyala", nyala);
        o.put("daftar", daftar);
        call.resolve(o);
    }

    // ---------- paket S4: mode kertas & label ----------
    /** Mode kertas printer sekarang: { mode: teks jawaban printer }. */
    @PluginMethod
    public void mode(final PluginCall call) {
        siapkan(call, p -> {
            final AtomicBoolean selesai = new AtomicBoolean(false);
            final Runnable habis = () -> {
                if (selesai.compareAndSet(false, true)) call.reject("Printer tidak menjawab saat ditanya mode kertasnya", "PRINTER_DIAM");
            };
            utama.postDelayed(habis, BATAS_STATUS_MS);
            try {
                p.getPrintMode(new PropCallback() {
                    @Override
                    public void onProperty(String hasil) {
                        if (!selesai.compareAndSet(false, true)) return;
                        utama.removeCallbacks(habis);
                        JSObject o = kartu(p);
                        o.put("mode", hasil == null ? "" : hasil);
                        call.resolve(o);
                    }
                });
            } catch (Exception e) {
                if (!selesai.compareAndSet(false, true)) return;
                utama.removeCallbacks(habis);
                call.reject("Mode kertas tidak bisa ditanyakan: " + e.getMessage(), BELUM_KIRIM);
            }
        });
    }

    /** Pindahkan mode kertas: { mode: 1 struk | 2 label | 3 tanpa alas } → { dikirim: true }. Printer tidak mengabari hasilnya; tanyakan lagi dengan `mode`. */
    @PluginMethod
    public void setelMode(final PluginCall call) {
        final Integer m = call.getInt("mode");
        if (m == null || m < 1 || m > 3) {
            call.reject("Mode kertas harus 1 (struk), 2 (label), atau 3 (tanpa alas)", BELUM_KIRIM);
            return;
        }
        siapkan(call, p -> {
            try {
                p.setPrintMode(m);
            } catch (Exception e) {
                call.reject("Perintah pindah mode tidak terkirim: " + e.getMessage(), BELUM_KIRIM);
                return;
            }
            JSObject o = kartu(p);
            o.put("dikirim", true);
            o.put("diminta", m);
            call.resolve(o);
        });
    }

    /** Kirim perintah label TSPL apa adanya: { data } → { byte }. Hanya berarti bila printer di mode label; printer label tidak mengabari hasil cetak. */
    @PluginMethod
    public void tspl(final PluginCall call) {
        final String data = call.getString("data");
        if (data == null || data.isEmpty()) {
            call.reject("Perintah label kosong", BELUM_KIRIM);
            return;
        }
        siapkan(call, p -> {
            try {
                p.sendTSPLData(data);
            } catch (Exception e) {
                lepasDiam();
                call.reject("Perintah label tidak terkirim: " + e.getMessage(), BELUM_KIRIM);
                return;
            }
            JSObject o = kartu(p);
            o.put("byte", data.length());
            call.resolve(o);
        });
    }

    /** Lepaskan printer (supaya jalur CetakUsb bisa memegang antarmukanya). */
    @PluginMethod
    public void lepas(PluginCall call) {
        lepasDiam();
        call.resolve();
    }

    @Override
    protected void handleOnDestroy() {
        lepasDiam();
        super.handleOnDestroy();
    }
}
