package id.miqbal.tokoberas;

// CETAK USB (putaran T1 langkah 2) — plugin Capacitor "CetakUsb" untuk tablet kasir Sunmi CPad + printer 80 mm (NT320) di USB stand.
// Chrome tidak bisa mengklaim antarmuka printer itu (WebUSB: "Unable to claim interface", uji owner 16 Nov 2026), aplikasi Android bisa:
// claimInterface(antarmuka, force = true). Plugin ini HANYA mengirim byte ESC/POS yang sudah disusun halaman (escpos.js) — tidak menyusun
// struk, tidak membaca data toko. Pengiriman diantrekan satu per satu supaya dua cetak beruntun tidak bertabrakan.

import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.usb.UsbConstants;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;
import android.os.Build;
import android.util.Base64;

import androidx.core.content.ContextCompat;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@CapacitorPlugin(name = "CetakUsb")
public class CetakUsbPlugin extends Plugin {
    private static final String AKSI_IZIN = "id.miqbal.tokoberas.IZIN_USB";
    private static final int VID_SUNMI = 0x324f;
    private static final int POTONGAN = 16384;
    private static final int BATAS_MS = 8000;

    private final ExecutorService antre = Executors.newSingleThreadExecutor();

    private static final class Jalur {
        UsbInterface antarmuka;
        UsbEndpoint keluar;
        int kelas;
    }

    private UsbManager usb() {
        return (UsbManager) getContext().getSystemService(Context.USB_SERVICE);
    }

    private static String hex(int n) {
        return String.format(Locale.US, "0x%04x", n);
    }

    /** Antarmuka + endpoint bulk OUT; kelas printer (7) didahulukan. null = bukan printer. */
    private static Jalur cariJalur(UsbDevice d) {
        Jalur terbaik = null;
        for (int i = 0; i < d.getInterfaceCount(); i++) {
            UsbInterface a = d.getInterface(i);
            for (int e = 0; e < a.getEndpointCount(); e++) {
                UsbEndpoint ep = a.getEndpoint(e);
                if (ep.getType() != UsbConstants.USB_ENDPOINT_XFER_BULK || ep.getDirection() != UsbConstants.USB_DIR_OUT) continue;
                boolean lebihBaik = terbaik == null
                        || (a.getInterfaceClass() == UsbConstants.USB_CLASS_PRINTER && terbaik.kelas != UsbConstants.USB_CLASS_PRINTER);
                if (lebihBaik) {
                    Jalur j = new Jalur();
                    j.antarmuka = a;
                    j.keluar = ep;
                    j.kelas = a.getInterfaceClass();
                    terbaik = j;
                }
            }
        }
        return terbaik;
    }

    /** Printer yang dituju: Sunmi atau kelas printer didahulukan; selain itu perangkat pertama yang punya bulk OUT. */
    private UsbDevice cariPrinter(Integer vid, Integer pid) {
        UsbDevice cadangan = null;
        for (UsbDevice d : usb().getDeviceList().values()) {
            if (vid != null && d.getVendorId() != vid) continue;
            if (pid != null && d.getProductId() != pid) continue;
            Jalur j = cariJalur(d);
            if (j == null) continue;
            if (d.getVendorId() == VID_SUNMI || j.kelas == UsbConstants.USB_CLASS_PRINTER) return d;
            if (cadangan == null) cadangan = d;
        }
        return cadangan;
    }

    /** Diagnosis: semua perangkat USB yang terlihat aplikasi. */
    @PluginMethod
    public void daftar(PluginCall call) {
        JSArray daftar = new JSArray();
        for (UsbDevice d : usb().getDeviceList().values()) {
            JSObject o = new JSObject();
            o.put("vid", hex(d.getVendorId()));
            o.put("pid", hex(d.getProductId()));
            o.put("nama", d.getProductName());
            o.put("pabrik", d.getManufacturerName());
            o.put("izin", usb().hasPermission(d));
            Jalur j = cariJalur(d);
            o.put("bisaCetak", j != null);
            if (j != null) o.put("kelas", j.kelas);
            daftar.put(o);
        }
        JSObject hasil = new JSObject();
        hasil.put("perangkat", daftar);
        call.resolve(hasil);
    }

    /** Cetak: { data: base64 byte ESC/POS, vid?, pid? } → { byte, nama, vid, pid }. */
    @PluginMethod
    public void cetak(PluginCall call) {
        String data = call.getString("data");
        if (data == null || data.isEmpty()) {
            call.reject("Data cetak kosong");
            return;
        }
        final byte[] isi;
        try {
            isi = Base64.decode(data, Base64.DEFAULT);
        } catch (IllegalArgumentException e) {
            call.reject("Data cetak rusak (base64)");
            return;
        }
        UsbDevice d = cariPrinter(call.getInt("vid"), call.getInt("pid"));
        if (d == null) {
            call.reject("Printer USB tidak ditemukan — pastikan printer menyala dan tercolok ke stand");
            return;
        }
        if (usb().hasPermission(d)) kirim(call, d, isi);
        else mintaIzin(call, d, isi);
    }

    private void mintaIzin(final PluginCall call, final UsbDevice d, final byte[] isi) {
        final Context ctx = getContext();
        BroadcastReceiver penerima = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent intent) {
                if (!AKSI_IZIN.equals(intent.getAction())) return;
                try {
                    ctx.unregisterReceiver(this);
                } catch (IllegalArgumentException ignored) {
                    // sudah dilepas
                }
                boolean boleh = intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false);
                if (boleh || usb().hasPermission(d)) kirim(call, d, isi);
                else call.reject("Izin USB ditolak — ketuk Cetak lagi lalu pilih Izinkan");
            }
        };
        ContextCompat.registerReceiver(ctx, penerima, new IntentFilter(AKSI_IZIN), ContextCompat.RECEIVER_NOT_EXPORTED);
        Intent niat = new Intent(AKSI_IZIN).setPackage(ctx.getPackageName());
        int bendera = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S ? PendingIntent.FLAG_MUTABLE : 0;
        usb().requestPermission(d, PendingIntent.getBroadcast(ctx, 0, niat, bendera));
    }

    private void kirim(final PluginCall call, final UsbDevice d, final byte[] isi) {
        antre.execute(() -> {
            UsbDeviceConnection sambung = null;
            Jalur j = cariJalur(d);
            String langkah = "membuka printer";
            try {
                if (j == null) throw new IllegalStateException("perangkat ini tidak punya jalur kirim (bukan printer)");
                sambung = usb().openDevice(d);
                if (sambung == null) throw new IllegalStateException("printer tidak bisa dibuka");
                langkah = "mengklaim antarmuka " + j.antarmuka.getId();
                if (!sambung.claimInterface(j.antarmuka, true)) {
                    throw new IllegalStateException("antarmuka dipegang aplikasi lain — tutup RawBT/aplikasi printer lain lalu coba lagi");
                }
                langkah = "mengirim data";
                int terkirim = 0;
                while (terkirim < isi.length) {
                    int n = Math.min(POTONGAN, isi.length - terkirim);
                    int r = sambung.bulkTransfer(j.keluar, isi, terkirim, n, BATAS_MS);
                    if (r <= 0) throw new IllegalStateException("printer tidak menjawab (kertas habis atau tutup terbuka?)");
                    terkirim += r;
                }
                sambung.releaseInterface(j.antarmuka);
                JSObject hasil = new JSObject();
                hasil.put("byte", terkirim);
                hasil.put("nama", d.getProductName());
                hasil.put("vid", hex(d.getVendorId()));
                hasil.put("pid", hex(d.getProductId()));
                call.resolve(hasil);
            } catch (Exception e) {
                call.reject("Gagal saat " + langkah + ": " + e.getMessage());
            } finally {
                if (sambung != null) sambung.close();
            }
        });
    }
}
