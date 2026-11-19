package id.miqbal.tokoberas;

// PERANGKAT (paket S1, 19 Nov 2026) — plugin Capacitor "Perangkat": kartu nama perangkat & aplikasi ini untuk layar diagnosis
// (/baru/uji-cetak.html): merek, model, versi Android, versi APK. Tidak membaca data toko, tidak membaca nomor seri.

import android.content.pm.PackageInfo;
import android.os.Build;

import androidx.core.content.pm.PackageInfoCompat;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.Locale;

@CapacitorPlugin(name = "Perangkat")
public class PerangkatPlugin extends Plugin {
    /** { merek, model, android, sdk, sunmi, versiApk, kodeApk, paket }. */
    @PluginMethod
    public void info(PluginCall call) {
        JSObject o = new JSObject();
        String merek = Build.MANUFACTURER == null ? "" : Build.MANUFACTURER;
        o.put("merek", merek);
        o.put("model", Build.MODEL);
        o.put("android", Build.VERSION.RELEASE);
        o.put("sdk", Build.VERSION.SDK_INT);
        o.put("sunmi", merek.toLowerCase(Locale.US).contains("sunmi"));
        o.put("paket", getContext().getPackageName());
        try {
            PackageInfo p = getContext().getPackageManager().getPackageInfo(getContext().getPackageName(), 0);
            o.put("versiApk", p.versionName);
            o.put("kodeApk", PackageInfoCompat.getLongVersionCode(p));
        } catch (Exception e) {
            o.put("versiApk", "");
        }
        call.resolve(o);
    }
}
