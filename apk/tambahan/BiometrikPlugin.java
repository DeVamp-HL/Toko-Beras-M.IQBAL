package id.miqbal.tokoberas;

// BIOMETRIK (paket S4, 19 Nov 2026) — plugin Capacitor "Biometrik": sensor sidik jari tablet lewat AndroidX Biometric (BiometricManager +
// BiometricPrompt). SUNMI mewajibkan jalur ini: FingerprintManager lama dimatikan di ROM baru (dokumen "Biometric (Fingerprint) Development Guide").
// Keputusan owner 19 Nov 2026: PERIKSA SENSORNYA DULU — plugin ini hanya menjawab "ada sensor atau tidak" dan menjalankan satu kali uji tempel
// jari. Android hanya mengatakan "jari ini terdaftar di tablet", BUKAN jari siapa; plugin ini tidak membuka akun, tidak menyetujui apa pun,
// tidak membaca data toko.

import androidx.annotation.NonNull;
import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.concurrent.atomic.AtomicBoolean;

@CapacitorPlugin(name = "Biometrik")
public class BiometrikPlugin extends Plugin {
    private static final int JENIS = BiometricManager.Authenticators.BIOMETRIC_WEAK;

    /** Kalimat untuk orang toko, bukan nama konstanta. */
    private static String kalimat(int kode) {
        switch (kode) {
            case BiometricManager.BIOMETRIC_SUCCESS: return "sensor ada dan sudah ada jari yang didaftarkan";
            case BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED: return "sensor ada, tapi belum ada jari yang didaftarkan di Setelan tablet";
            case BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE: return "tablet ini tidak punya sensor sidik jari";
            case BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE: return "sensor sidik jari sedang tidak bisa dipakai";
            case BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED: return "sensor ada, tapi tablet meminta pembaruan keamanan dulu";
            case BiometricManager.BIOMETRIC_ERROR_UNSUPPORTED: return "sensor sidik jari tidak didukung versi Android ini";
            default: return "keadaan sensor tidak diketahui";
        }
    }

    /** { ada, terdaftar, kode, kalimat } — ada = sensor terpasang (walau belum ada jari terdaftar). */
    @PluginMethod
    public void info(PluginCall call) {
        JSObject o = new JSObject();
        int kode = -99;
        try {
            kode = BiometricManager.from(getContext()).canAuthenticate(JENIS);
        } catch (Throwable t) {
            o.put("pesan", String.valueOf(t.getMessage()));
        }
        o.put("ada", kode == BiometricManager.BIOMETRIC_SUCCESS || kode == BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED
                || kode == BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED);
        o.put("terdaftar", kode == BiometricManager.BIOMETRIC_SUCCESS);
        o.put("kode", kode);
        o.put("kalimat", kalimat(kode));
        call.resolve(o);
    }

    /** Satu kali tempel jari: { judul, ket } → { ok: true }. Batal / terkunci / tanpa sensor = menolak berkode BIOMETRIK_<kode Android>. */
    @PluginMethod
    public void minta(final PluginCall call) {
        final FragmentActivity a = getActivity();
        if (a == null) {
            call.reject("Layar aplikasi belum siap", "BIOMETRIK_GAGAL");
            return;
        }
        final String judul = call.getString("judul", "Sidik jari");
        final String ket = call.getString("ket", "");
        final AtomicBoolean selesai = new AtomicBoolean(false);
        a.runOnUiThread(() -> {
            try {
                BiometricPrompt p = new BiometricPrompt(a, ContextCompat.getMainExecutor(a), new BiometricPrompt.AuthenticationCallback() {
                    @Override
                    public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult hasil) {
                        if (!selesai.compareAndSet(false, true)) return;
                        JSObject o = new JSObject();
                        o.put("ok", true);
                        call.resolve(o);
                    }

                    @Override
                    public void onAuthenticationError(int kode, @NonNull CharSequence pesan) {
                        if (!selesai.compareAndSet(false, true)) return;
                        call.reject(String.valueOf(pesan), "BIOMETRIK_" + kode);
                    }
                    // onAuthenticationFailed (jari tidak cocok) sengaja tidak ditangani: dialog Android tetap terbuka dan menghitung percobaannya sendiri
                });
                BiometricPrompt.PromptInfo.Builder b = new BiometricPrompt.PromptInfo.Builder()
                        .setTitle(judul == null || judul.isEmpty() ? "Sidik jari" : judul)
                        .setNegativeButtonText("Batal")
                        .setAllowedAuthenticators(JENIS);
                if (ket != null && !ket.isEmpty()) b.setSubtitle(ket);
                p.authenticate(b.build());
            } catch (Throwable t) {
                if (selesai.compareAndSet(false, true)) call.reject("Sidik jari tidak bisa diminta: " + t.getMessage(), "BIOMETRIK_GAGAL");
            }
        });
    }
}
