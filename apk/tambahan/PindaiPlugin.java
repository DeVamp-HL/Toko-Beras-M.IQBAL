package id.miqbal.tokoberas;

// PINDAI (paket S1, 19 Nov 2026) — plugin Capacitor "Pindai": scanner bawaan perangkat SUNMI (CPad ber-scanner).
// Scanner SUNMI menyiarkan tiap hasil scan sebagai broadcast "com.sunmi.scanner.ACTION_DATA_CODE_RECEIVED" (extra "data" = teks)
// selama "Output via broadcast" menyala di Setelan › Scanner (bawaan pabrik: menyala). Plugin ini hanya MENERUSKAN teksnya ke halaman
// sebagai kejadian "pindai" — tidak menafsirkan isi kode, tidak membaca data toko.

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;

import androidx.core.content.ContextCompat;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "Pindai")
public class PindaiPlugin extends Plugin {
    private static final String AKSI = "com.sunmi.scanner.ACTION_DATA_CODE_RECEIVED";
    private static final String PAKET_SCANNER = "com.sunmi.scanner";

    private BroadcastReceiver penerima;
    private volatile long jumlah = 0;
    private volatile long terakhirPada = 0;

    @Override
    public void load() {
        penerima = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent intent) {
                if (intent == null || !AKSI.equals(intent.getAction())) return;
                String data = intent.getStringExtra("data");
                if (data == null) return;
                data = data.trim();
                if (data.isEmpty()) return;
                jumlah += 1;
                terakhirPada = System.currentTimeMillis();
                JSObject o = new JSObject();
                o.put("data", data);
                o.put("waktu", terakhirPada);
                notifyListeners("pindai", o);
            }
        };
        try {
            // siaran datang dari aplikasi lain (layanan scanner SUNMI) → penerima harus terbuka (Android 14 mewajibkan benderanya)
            ContextCompat.registerReceiver(getContext(), penerima, new IntentFilter(AKSI), ContextCompat.RECEIVER_EXPORTED);
        } catch (Exception e) {
            penerima = null;
        }
    }

    /** { terpasang: layanan scanner SUNMI ada di perangkat ini, mendengar, jumlah, terakhirPada }. */
    @PluginMethod
    public void info(PluginCall call) {
        boolean ada;
        try {
            getContext().getPackageManager().getPackageInfo(PAKET_SCANNER, 0);
            ada = true;
        } catch (PackageManager.NameNotFoundException e) {
            ada = false;
        }
        JSObject o = new JSObject();
        o.put("terpasang", ada);
        o.put("mendengar", penerima != null);
        o.put("jumlah", jumlah);
        o.put("terakhirPada", terakhirPada);
        call.resolve(o);
    }

    @Override
    protected void handleOnDestroy() {
        if (penerima != null) {
            try {
                getContext().unregisterReceiver(penerima);
            } catch (IllegalArgumentException ignored) {
                // sudah dilepas
            }
            penerima = null;
        }
        super.handleOnDestroy();
    }
}
