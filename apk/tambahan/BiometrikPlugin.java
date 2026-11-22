package id.miqbal.tokoberas;

// BIOMETRIK (paket S4, 19 Nov 2026) — plugin Capacitor "Biometrik": sensor sidik jari tablet lewat AndroidX Biometric (BiometricManager +
// BiometricPrompt). SUNMI mewajibkan jalur ini: FingerprintManager lama dimatikan di ROM baru (dokumen "Biometric (Fingerprint) Development Guide").
// Keputusan owner 19 Nov 2026: PERIKSA SENSORNYA DULU — plugin ini hanya menjawab "ada sensor atau tidak" dan menjalankan satu kali uji tempel
// jari. Android hanya mengatakan "jari ini terdaftar di tablet", BUKAN jari siapa; plugin ini tidak membuka akun, tidak menyetujui apa pun,
// tidak membaca data toko.
// Owner 22 Nov 2026 (paket sidik jari, "cek sensor dulu"): + KELAS sensor (kuat = Android Class 3, syarat kunci terikat sidik jari) dan PENANDA JARI BARU:
// satu kunci AES di AndroidKeyStore (alias tetap, tidak pernah keluar dari tablet, tidak mengunci data apa pun) yang wajib sidik jari kuat dan HANGUS
// sendiri begitu ada jari baru didaftarkan (setInvalidatedByBiometricEnrollment). Halaman hanya bertanya "utuh / hangus / belum ada" + satu uji kunci
// (tempel jari lewat CryptoObject). Belum ada fitur toko yang memakainya — ini bahan keputusan owner (sidik jari owner hanya menyala bila penanda bisa).
// Owner 23 Nov 2026 (sidik jari Tahap B): + RAHASIA terkunci penanda — rahasiaSimpan(teks) mengenkripsi satu teks (sandi akun owner, diketik owner sendiri) dengan
// penanda sesudah tempel jari kuat → { data, iv } base64 yang disimpan halaman; rahasiaBuka(data, iv) = tempel jari → teksnya, SATU kali pakai. Penanda hangus
// (jari baru) = rahasianya tidak bisa dibuka lagi (BIOMETRIK_HANGUS) — owner mengetik sandinya lagi. Teks tidak pernah ditulis ke log / penyimpanan oleh plugin.

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

import android.os.Build;
import android.util.Base64;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyPermanentlyInvalidatedException;
import android.security.keystore.KeyProperties;
import android.security.keystore.UserNotAuthenticatedException;

import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.concurrent.atomic.AtomicBoolean;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

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

    // ---------- owner 22 Nov 2026: kelas sensor & penanda jari baru ----------
    private static final String ALIAS_PENANDA = "miqbal_penanda_jari";
    private static final String SANDI = "AES/GCM/NoPadding";

    private static KeyStore toko() throws Exception {
        KeyStore k = KeyStore.getInstance("AndroidKeyStore");
        k.load(null);
        return k;
    }

    /** { kuat, kodeKuat, kalimatKuat, lemah, kodeLemah, sdk } — kuat = Class 3 (kunci bisa diikat ke sidik jari); lemah = Class 2 (hanya "cocok/tidak"). */
    @PluginMethod
    public void kelas(PluginCall call) {
        JSObject o = new JSObject();
        int kuat = -99, lemah = -99;
        try {
            BiometricManager m = BiometricManager.from(getContext());
            kuat = m.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG);
            lemah = m.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK);
        } catch (Throwable t) {
            o.put("pesan", String.valueOf(t.getMessage()));
        }
        o.put("kuat", kuat == BiometricManager.BIOMETRIC_SUCCESS);
        o.put("kodeKuat", kuat);
        o.put("kalimatKuat", kalimat(kuat));
        o.put("lemah", lemah == BiometricManager.BIOMETRIC_SUCCESS);
        o.put("kodeLemah", lemah);
        o.put("sdk", Build.VERSION.SDK_INT);
        call.resolve(o);
    }

    /** Buat (atau ganti) penanda: kunci AES wajib sidik jari kuat, hangus bila ada jari baru. Gagal = sensor / layar kunci tidak memenuhi syarat. */
    @PluginMethod
    public void penandaPasang(PluginCall call) {
        try {
            KeyStore k = toko();
            if (k.containsAlias(ALIAS_PENANDA)) k.deleteEntry(ALIAS_PENANDA);
            KeyGenParameterSpec.Builder b = new KeyGenParameterSpec.Builder(ALIAS_PENANDA, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setUserAuthenticationRequired(true)
                    .setInvalidatedByBiometricEnrollment(true);
            if (Build.VERSION.SDK_INT >= 30) b.setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG);
            KeyGenerator g = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            g.init(b.build());
            g.generateKey();
            JSObject o = new JSObject();
            o.put("ok", true);
            call.resolve(o);
        } catch (Throwable t) {
            call.reject("Penanda tidak bisa dipasang: " + t.getClass().getSimpleName() + " — " + t.getMessage(), "PENANDA_GAGAL");
        }
    }

    /** { ada, hangus } — hangus = ada jari baru didaftarkan sejak penanda dipasang (kunci tidak bisa dipakai lagi). Tanpa tempel jari. */
    @PluginMethod
    public void penandaCek(PluginCall call) {
        JSObject o = new JSObject();
        try {
            KeyStore k = toko();
            if (!k.containsAlias(ALIAS_PENANDA)) {
                o.put("ada", false);
                o.put("hangus", false);
                call.resolve(o);
                return;
            }
            o.put("ada", true);
            Cipher c = Cipher.getInstance(SANDI);
            try {
                c.init(Cipher.ENCRYPT_MODE, (SecretKey) k.getKey(ALIAS_PENANDA, null));
                o.put("hangus", false);
            } catch (KeyPermanentlyInvalidatedException e) {
                o.put("hangus", true);
            } catch (UserNotAuthenticatedException e) {
                o.put("hangus", false);
                o.put("catatan", "kunci utuh, menunggu tempel jari");
            }
            call.resolve(o);
        } catch (Throwable t) {
            call.reject("Penanda tidak bisa diperiksa: " + t.getClass().getSimpleName() + " — " + t.getMessage(), "PENANDA_GAGAL");
        }
    }

    @PluginMethod
    public void penandaHapus(PluginCall call) {
        try {
            KeyStore k = toko();
            if (k.containsAlias(ALIAS_PENANDA)) k.deleteEntry(ALIAS_PENANDA);
            JSObject o = new JSObject();
            o.put("ok", true);
            call.resolve(o);
        } catch (Throwable t) {
            call.reject("Penanda tidak bisa dihapus: " + t.getMessage(), "PENANDA_GAGAL");
        }
    }

    /** Uji kunci: tempel jari lewat CryptoObject (hanya sidik jari KUAT) lalu satu enkripsi kecil dengan penanda → { ok, panjang }. Bukti sensor
     *  benar-benar membuka kunci yang terikat sidik jari (syarat Tahap B). Penanda hangus = BIOMETRIK_HANGUS; belum dipasang = PENANDA_TIDAK_ADA. */
    @PluginMethod
    public void ujiKunci(final PluginCall call) {
        final FragmentActivity a = getActivity();
        if (a == null) {
            call.reject("Layar aplikasi belum siap", "BIOMETRIK_GAGAL");
            return;
        }
        final Cipher c;
        try {
            KeyStore k = toko();
            if (!k.containsAlias(ALIAS_PENANDA)) {
                call.reject("Penanda belum dipasang", "PENANDA_TIDAK_ADA");
                return;
            }
            c = Cipher.getInstance(SANDI);
            c.init(Cipher.ENCRYPT_MODE, (SecretKey) k.getKey(ALIAS_PENANDA, null));
        } catch (KeyPermanentlyInvalidatedException e) {
            call.reject("Penanda hangus: ada jari baru didaftarkan", "BIOMETRIK_HANGUS");
            return;
        } catch (Throwable t) {
            call.reject("Kunci tidak bisa disiapkan: " + t.getClass().getSimpleName() + " — " + t.getMessage(), "PENANDA_GAGAL");
            return;
        }
        final AtomicBoolean selesai = new AtomicBoolean(false);
        a.runOnUiThread(() -> {
            try {
                BiometricPrompt p = new BiometricPrompt(a, ContextCompat.getMainExecutor(a), new BiometricPrompt.AuthenticationCallback() {
                    @Override
                    public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult hasil) {
                        if (!selesai.compareAndSet(false, true)) return;
                        try {
                            BiometricPrompt.CryptoObject co = hasil.getCryptoObject();
                            if (co == null || co.getCipher() == null) {
                                call.reject("Jari diterima tanpa kunci", "PENANDA_GAGAL");
                                return;
                            }
                            byte[] keluar = co.getCipher().doFinal("uji-penanda".getBytes(StandardCharsets.UTF_8));
                            JSObject o = new JSObject();
                            o.put("ok", true);
                            o.put("panjang", keluar.length);
                            call.resolve(o);
                        } catch (Throwable t) {
                            call.reject("Kunci tidak terbuka: " + t.getClass().getSimpleName() + " — " + t.getMessage(), "PENANDA_GAGAL");
                        }
                    }

                    @Override
                    public void onAuthenticationError(int kode, @NonNull CharSequence pesan) {
                        if (!selesai.compareAndSet(false, true)) return;
                        call.reject(String.valueOf(pesan), "BIOMETRIK_" + kode);
                    }
                });
                BiometricPrompt.PromptInfo info = new BiometricPrompt.PromptInfo.Builder()
                        .setTitle("Uji kunci sidik jari")
                        .setSubtitle("Tempelkan jari owner")
                        .setNegativeButtonText("Batal")
                        .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                        .build();
                p.authenticate(info, new BiometricPrompt.CryptoObject(c));
            } catch (Throwable t) {
                if (selesai.compareAndSet(false, true)) call.reject("Sidik jari tidak bisa diminta: " + t.getMessage(), "BIOMETRIK_GAGAL");
            }
        });
    }

    /** Satu tempel jari kuat lewat CryptoObject atas cipher c, lalu kerja(cipher) di dalam callback sukses. Kode tolak sama dengan ujiKunci. */
    private interface Kerja { JSObject jalan(Cipher c) throws Exception; }
    private void tempelLalu(final PluginCall call, final Cipher c, final String judul, final String sub, final Kerja kerja) {
        final FragmentActivity a = getActivity();
        if (a == null) {
            call.reject("Layar aplikasi belum siap", "BIOMETRIK_GAGAL");
            return;
        }
        final AtomicBoolean selesai = new AtomicBoolean(false);
        a.runOnUiThread(() -> {
            try {
                BiometricPrompt p = new BiometricPrompt(a, ContextCompat.getMainExecutor(a), new BiometricPrompt.AuthenticationCallback() {
                    @Override
                    public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult hasil) {
                        if (!selesai.compareAndSet(false, true)) return;
                        try {
                            BiometricPrompt.CryptoObject co = hasil.getCryptoObject();
                            if (co == null || co.getCipher() == null) {
                                call.reject("Jari diterima tanpa kunci", "PENANDA_GAGAL");
                                return;
                            }
                            call.resolve(kerja.jalan(co.getCipher()));
                        } catch (Throwable t) {
                            call.reject("Kunci tidak terbuka: " + t.getClass().getSimpleName(), "PENANDA_GAGAL");
                        }
                    }

                    @Override
                    public void onAuthenticationError(int kode, @NonNull CharSequence pesan) {
                        if (!selesai.compareAndSet(false, true)) return;
                        call.reject(String.valueOf(pesan), "BIOMETRIK_" + kode);
                    }
                });
                BiometricPrompt.PromptInfo info = new BiometricPrompt.PromptInfo.Builder()
                        .setTitle(judul)
                        .setSubtitle(sub)
                        .setNegativeButtonText("Batal")
                        .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                        .build();
                p.authenticate(info, new BiometricPrompt.CryptoObject(c));
            } catch (Throwable t) {
                if (selesai.compareAndSet(false, true)) call.reject("Sidik jari tidak bisa diminta: " + t.getMessage(), "BIOMETRIK_GAGAL");
            }
        });
    }

    /** Cipher penanda untuk mode (ENCRYPT / DECRYPT dengan iv). null = sudah ditolak lewat call (tidak ada / hangus / gagal). */
    private Cipher cipherPenanda(PluginCall call, int mode, byte[] iv) {
        try {
            KeyStore k = toko();
            if (!k.containsAlias(ALIAS_PENANDA)) {
                call.reject("Penanda belum dipasang", "PENANDA_TIDAK_ADA");
                return null;
            }
            Cipher c = Cipher.getInstance(SANDI);
            if (mode == Cipher.DECRYPT_MODE) c.init(mode, (SecretKey) k.getKey(ALIAS_PENANDA, null), new GCMParameterSpec(128, iv));
            else c.init(mode, (SecretKey) k.getKey(ALIAS_PENANDA, null));
            return c;
        } catch (KeyPermanentlyInvalidatedException e) {
            call.reject("Penanda hangus: ada jari baru didaftarkan", "BIOMETRIK_HANGUS");
        } catch (Throwable t) {
            call.reject("Kunci tidak bisa disiapkan: " + t.getClass().getSimpleName(), "PENANDA_GAGAL");
        }
        return null;
    }

    /** Owner 23 Nov 2026 (Tahap B): kunci satu teks dengan penanda sesudah tempel jari → { ok, data, iv } (base64). Teks tidak disimpan plugin. */
    @PluginMethod
    public void rahasiaSimpan(final PluginCall call) {
        final String teks = call.getString("teks", "");
        if (teks == null || teks.isEmpty()) {
            call.reject("Tidak ada yang dikunci", "RAHASIA_KOSONG");
            return;
        }
        Cipher c = cipherPenanda(call, Cipher.ENCRYPT_MODE, null);
        if (c == null) return;
        tempelLalu(call, c, call.getString("judul", "Kunci sandi owner"), "Tempelkan jari owner", (ci) -> {
            byte[] keluar = ci.doFinal(teks.getBytes(StandardCharsets.UTF_8));
            JSObject o = new JSObject();
            o.put("ok", true);
            o.put("data", Base64.encodeToString(keluar, Base64.NO_WRAP));
            o.put("iv", Base64.encodeToString(ci.getIV(), Base64.NO_WRAP));
            return o;
        });
    }

    /** Owner 23 Nov 2026 (Tahap B): buka teks terkunci penanda (data + iv base64) sesudah tempel jari → { ok, teks }. Satu tempel jari = satu kali buka. */
    @PluginMethod
    public void rahasiaBuka(final PluginCall call) {
        final byte[] data, iv;
        try {
            data = Base64.decode(call.getString("data", ""), Base64.NO_WRAP);
            iv = Base64.decode(call.getString("iv", ""), Base64.NO_WRAP);
        } catch (Throwable t) {
            call.reject("Simpanan rahasia rusak", "RAHASIA_RUSAK");
            return;
        }
        if (data.length == 0 || iv.length == 0) {
            call.reject("Simpanan rahasia kosong", "RAHASIA_RUSAK");
            return;
        }
        Cipher c = cipherPenanda(call, Cipher.DECRYPT_MODE, iv);
        if (c == null) return;
        tempelLalu(call, c, call.getString("judul", "Putusan owner"), call.getString("sub", "Tempelkan jari owner"), (ci) -> {
            byte[] teks = ci.doFinal(data);
            JSObject o = new JSObject();
            o.put("ok", true);
            o.put("teks", new String(teks, StandardCharsets.UTF_8));
            return o;
        });
    }
}
