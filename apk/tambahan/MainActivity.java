package id.miqbal.tokoberas;

import android.app.Activity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;

// Aktivitas utama tablet kasir: daftarkan plugin perangkat, layar tidak padam selama aplikasi terbuka (kasir).
// Tiap plugin = satu perangkat, tidak menyentuh data toko: CetakUsb (kirim byte ke printer USB mana pun), PrinterSunmi (SDK resmi
// SUNMI: keadaan printer + hasil cetak + laci), Pindai (scanner bawaan), Lampu (LED CPad), Perangkat (kartu nama perangkat + layar penuh),
// Nfc (pembaca NFC bawaan: nomor seri kartu yang ditempelkan), Biometrik (sensor sidik jari: ada-tidaknya + satu kali uji tempel jari).
// Push tablet (owner 23 Nov 2026) = plugin resmi @capacitor/push-notifications (didaftarkan sendiri oleh Capacitor); di sini hanya SALURAN
// notifikasi "Kabar toko" (penting: bunyi + muncul di atas layar) dibuat sebelum kabar pertama datang.
public class MainActivity extends BridgeActivity {
    static final String SALURAN = "kabar";
    private static final String SIMPAN = "tampilan";
    private static final String KUNCI_PENUH = "layarPenuh";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(CetakUsbPlugin.class);
        registerPlugin(PrinterSunmiPlugin.class);
        registerPlugin(PindaiPlugin.class);
        registerPlugin(LampuPlugin.class);
        registerPlugin(PerangkatPlugin.class);
        registerPlugin(NfcPlugin.class);
        registerPlugin(BiometrikPlugin.class);
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        buatSaluran(this);
        terapkanLayarPenuh(this, layarPenuhTersimpan(this));
    }

    // owner 23 Nov 2026: layar penuh tetap berlaku sesudah kembali dari aplikasi lain / dialog / papan ketik
    @Override
    public void onResume() {
        super.onResume();
        terapkanLayarPenuh(this, layarPenuhTersimpan(this));
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) terapkanLayarPenuh(this, layarPenuhTersimpan(this));
    }

    static boolean layarPenuhTersimpan(Context c) {
        return c.getSharedPreferences(SIMPAN, Context.MODE_PRIVATE).getBoolean(KUNCI_PENUH, false);
    }

    static void simpanLayarPenuh(Context c, boolean nyala) {
        c.getSharedPreferences(SIMPAN, Context.MODE_PRIVATE).edit().putBoolean(KUNCI_PENUH, nyala).apply();
    }

    /** Sembunyikan / tampilkan bilah status & bilah navigasi Android. Tersembunyi: geser dari tepi atas / bawah = muncul sebentar lalu hilang lagi. */
    static void terapkanLayarPenuh(Activity a, boolean nyala) {
        Window w = a.getWindow(); if (w == null) return;
        WindowInsetsControllerCompat k = WindowCompat.getInsetsController(w, w.getDecorView());
        if (nyala) {
            k.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            k.hide(WindowInsetsCompat.Type.systemBars());
        } else {
            k.show(WindowInsetsCompat.Type.systemBars());
        }
    }

    /** Saluran "Kabar toko" (Android 8+): penting = bunyi & muncul di atas layar. Membuat ulang saluran yang sudah ada tidak mengubah setelan owner. */
    static void buatSaluran(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE); if (nm == null) return;
        NotificationChannel s = new NotificationChannel(SALURAN, "Kabar toko", NotificationManager.IMPORTANCE_HIGH);
        s.setDescription("Jawaban owner, balasan pesan, dan permintaan dari aplikasi toko");
        s.enableVibration(true); s.enableLights(true);
        nm.createNotificationChannel(s);
    }
}
