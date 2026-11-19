package id.miqbal.tokoberas;

import android.os.Bundle;
import android.view.WindowManager;

import com.getcapacitor.BridgeActivity;

// Aktivitas utama tablet kasir: daftarkan plugin perangkat, layar tidak padam selama aplikasi terbuka (kasir).
// Tiap plugin = satu perangkat, tidak menyentuh data toko: CetakUsb (kirim byte ke printer USB mana pun), PrinterSunmi (SDK resmi
// SUNMI: keadaan printer + hasil cetak + laci), Pindai (scanner bawaan), Lampu (LED CPad), Perangkat (kartu nama perangkat).
public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(CetakUsbPlugin.class);
        registerPlugin(PrinterSunmiPlugin.class);
        registerPlugin(PindaiPlugin.class);
        registerPlugin(LampuPlugin.class);
        registerPlugin(PerangkatPlugin.class);
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
}
