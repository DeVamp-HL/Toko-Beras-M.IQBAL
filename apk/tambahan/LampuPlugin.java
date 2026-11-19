package id.miqbal.tokoberas;

// LAMPU (paket S1, 19 Nov 2026) — plugin Capacitor "Lampu": lampu RGB bawaan SUNMI CPad (Android 14) lewat SunmiCustomer API
// (com.sunmi:customerservice → TMSApi.getDeviceManager().openRgbLed / closeRgbLed / isSupportRgbLed; dokumen "CPad Built-in LED
// Indicator Management"). Lampu hanya hiasan penanda: plugin ini TIDAK PERNAH menolak — perangkat tanpa lampu / tanpa layanan SUNMI
// menjawab { ok: false } dan halaman jalan terus.

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.sunmi.tms.api.TMSApi;
import com.sunmi.tms.api.TMSServiceConnection;

@CapacitorPlugin(name = "Lampu")
public class LampuPlugin extends Plugin {
    private TMSApi tms;
    private volatile boolean tersambung = false;

    @Override
    public void load() {
        try {
            tms = new TMSApi();
            tms.connect(getContext().getApplicationContext(), new TMSServiceConnection() {
                @Override
                public void onServiceConnected() {
                    tersambung = true;
                }

                @Override
                public void onServiceDisconnected() {
                    tersambung = false;
                }
            });
        } catch (Throwable t) {
            tms = null;
        }
    }

    private static int batasi(Integer n, int bawaan, int min, int maks) {
        int v = n == null ? bawaan : n;
        return Math.max(min, Math.min(maks, v));
    }

    /** { dukung, kode, tersambung } — kode: 0 didukung · -1 tidak · -40/-41 ROM/layanan tidak punya · -99 layanan SUNMI belum tersambung. */
    @PluginMethod
    public void dukung(PluginCall call) {
        JSObject o = new JSObject();
        int kode = -99;
        try {
            if (tms != null && tersambung) kode = tms.getDeviceManager().isSupportRgbLed();
        } catch (Throwable t) {
            o.put("pesan", String.valueOf(t.getMessage()));
        }
        o.put("dukung", kode == 0);
        o.put("kode", kode);
        o.put("tersambung", tersambung);
        call.resolve(o);
    }

    /** { warna: 1 merah · 2 hijau · 3 biru · 4 kuning · 5 sian · 6 magenta · 7 putih, kedip?, nyalaMs?, matiMs?, batasMs? } → { ok, kode }. */
    @PluginMethod
    public void nyala(PluginCall call) {
        JSObject o = new JSObject();
        int kode = -99;
        try {
            if (tms != null && tersambung) {
                int warna = batasi(call.getInt("warna"), 2, 1, 7);
                boolean kedip = Boolean.TRUE.equals(call.getBoolean("kedip", false));
                int nyalaMs = batasi(call.getInt("nyalaMs"), 300, 50, 5000);
                int matiMs = batasi(call.getInt("matiMs"), 300, 50, 5000);
                // batas waktu WAJIB ada: lampu padam sendiri walau halaman tidak sempat memadamkannya
                int batasMs = batasi(call.getInt("batasMs"), 4000, 200, 60000);
                kode = tms.getDeviceManager().openRgbLed(warna, nyalaMs, matiMs, kedip ? 1 : 0, (long) batasMs);
            }
        } catch (Throwable t) {
            o.put("pesan", String.valueOf(t.getMessage()));
        }
        o.put("ok", kode == 0);
        o.put("kode", kode);
        call.resolve(o);
    }

    /** Padamkan lampu → { ok, kode }. */
    @PluginMethod
    public void mati(PluginCall call) {
        JSObject o = new JSObject();
        int kode = -99;
        try {
            if (tms != null && tersambung) kode = tms.getDeviceManager().closeRgbLed();
        } catch (Throwable t) {
            o.put("pesan", String.valueOf(t.getMessage()));
        }
        o.put("ok", kode == 0);
        o.put("kode", kode);
        call.resolve(o);
    }

    @Override
    protected void handleOnDestroy() {
        try {
            if (tms != null) tms.disconnect();
        } catch (Throwable ignored) {
            // layanan sudah putus
        }
        tersambung = false;
        super.handleOnDestroy();
    }
}
