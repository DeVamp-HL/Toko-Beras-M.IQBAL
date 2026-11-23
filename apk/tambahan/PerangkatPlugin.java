package id.miqbal.tokoberas;

// PERANGKAT (paket S1, 19 Nov 2026) — plugin Capacitor "Perangkat": kartu nama perangkat & aplikasi ini untuk layar diagnosis
// (/baru/uji-cetak.html): merek, model, versi Android, versi APK. Tidak membaca data toko, tidak membaca nomor seri.
// Owner 23 Nov 2026: + LAYAR PENUH (bilah jam/baterai & tombol kembali/beranda Android disembunyikan; geser dari tepi = muncul sebentar) — saklar
// di Menu › Perangkat, diingat aplikasi (SharedPreferences) dan diterapkan MainActivity saat dibuka / kembali ke depan. + pushSiap: APK ini dibangun
// dengan berkas Firebase (google-services) → push tablet bisa dinyalakan.

import android.app.Activity;
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
        o.put("pushSiap", pushSiap());
        o.put("layarPenuh", MainActivity.layarPenuhTersimpan(getContext()));
        call.resolve(o);
    }

    /** Berkas google-services.json ikut dibangun → plugin google-services menulis sumber daya google_app_id. Tanpa itu push tablet tidak bisa. */
    private boolean pushSiap() {
        try { return getContext().getResources().getIdentifier("google_app_id", "string", getContext().getPackageName()) != 0; } catch (Exception e) { return false; }
    }

    /** { nyala: boolean } → simpan & terapkan sekarang. Hasil { layarPenuh }. */
    @PluginMethod
    public void layarPenuh(PluginCall call) {
        final boolean nyala = Boolean.TRUE.equals(call.getBoolean("nyala", false));
        MainActivity.simpanLayarPenuh(getContext(), nyala);
        final Activity a = getActivity();
        if (a == null) { call.reject("Aplikasi belum siap", "BELUM_SIAP"); return; }
        a.runOnUiThread(() -> {
            MainActivity.terapkanLayarPenuh(a, nyala);
            JSObject o = new JSObject(); o.put("layarPenuh", nyala); call.resolve(o);
        });
    }
}
