package id.miqbal.tokoberas;

// NFC (paket S2a, 19 Nov 2026) — plugin Capacitor "Nfc": pembaca NFC bawaan tablet (CPad).
// Selama aplikasi di depan, tablet membaca kartu / stiker yang ditempelkan (mode pembaca Android: tanpa jendela "tag baru" dari sistem)
// dan MENERUSKAN nomor serinya (UID, heksadesimal huruf besar) ke halaman sebagai kejadian "tempel".
// Tidak membaca isi kartu, tidak menulis ke kartu, tidak membaca data toko. Nomor seri bukan rahasia dan bisa ditiru: dipakai untuk
// MENGENALI (kartu pelanggan), bukan untuk membayar atau membuka kunci.

import android.app.Activity;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.os.Bundle;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "Nfc")
public class NfcPlugin extends Plugin {
    // semua jenis kartu tempel yang umum (A: kartu & stiker NTAG/MIFARE, B, F: FeliCa, V: ISO 15693); isi NDEF tidak dibaca
    private static final int BENDERA = NfcAdapter.FLAG_READER_NFC_A | NfcAdapter.FLAG_READER_NFC_B | NfcAdapter.FLAG_READER_NFC_F
            | NfcAdapter.FLAG_READER_NFC_V | NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK;
    private static final char[] HEKS = "0123456789ABCDEF".toCharArray();

    private volatile boolean membaca = false;
    private volatile long jumlah = 0;
    private volatile long terakhirPada = 0;

    private NfcAdapter adaptor() {
        try {
            return NfcAdapter.getDefaultAdapter(getContext());
        } catch (Exception e) {
            return null;
        }
    }

    private static String heks(byte[] b) {
        if (b == null) return "";
        StringBuilder s = new StringBuilder(b.length * 2);
        for (byte x : b) {
            s.append(HEKS[(x >> 4) & 0x0F]).append(HEKS[x & 0x0F]);
        }
        return s.toString();
    }

    private void terima(Tag tag) {
        if (tag == null) return;
        final String uid = heks(tag.getId());
        if (uid.isEmpty()) return;
        jumlah += 1;
        terakhirPada = System.currentTimeMillis();
        final JSObject o = new JSObject();
        o.put("uid", uid);
        JSArray jenis = new JSArray();
        String[] daftar = tag.getTechList();
        if (daftar != null) {
            for (String t : daftar) {
                // "android.nfc.tech.NfcA" → "NfcA"
                jenis.put(t == null ? "" : t.substring(t.lastIndexOf('.') + 1));
            }
        }
        o.put("jenis", jenis);
        o.put("waktu", terakhirPada);
        // panggilan pembaca datang dari utas NFC; kejadian ke halaman dikirim dari utas utama
        Activity a = getActivity();
        if (a != null) a.runOnUiThread(() -> notifyListeners("tempel", o));
    }

    private void mulai() {
        Activity a = getActivity();
        NfcAdapter n = adaptor();
        if (a == null || n == null || !n.isEnabled()) {
            membaca = false;
            return;
        }
        try {
            Bundle o = new Bundle();
            o.putInt(NfcAdapter.EXTRA_READER_PRESENCE_CHECK_DELAY, 500);
            n.enableReaderMode(a, this::terima, BENDERA, o);
            membaca = true;
        } catch (Exception e) {
            membaca = false;
        }
    }

    private void berhenti() {
        Activity a = getActivity();
        NfcAdapter n = adaptor();
        if (a != null && n != null) {
            try {
                n.disableReaderMode(a);
            } catch (Exception ignored) {
                // aktivitas sudah tidak di depan
            }
        }
        membaca = false;
    }

    @Override
    protected void handleOnResume() {
        super.handleOnResume();
        mulai();
    }

    @Override
    protected void handleOnPause() {
        berhenti();
        super.handleOnPause();
    }

    /** { ada: perangkat punya NFC, nyala: NFC dinyalakan di Setelan, membaca, jumlah, terakhirPada }. */
    @PluginMethod
    public void info(PluginCall call) {
        NfcAdapter n = adaptor();
        boolean nyala = false;
        try {
            nyala = n != null && n.isEnabled();
        } catch (Exception ignored) {
            // layanan NFC tidak menjawab
        }
        if (nyala && !membaca) mulai();   // NFC baru dinyalakan sesudah aplikasi dibuka
        JSObject o = new JSObject();
        o.put("ada", n != null);
        o.put("nyala", nyala);
        o.put("membaca", membaca);
        o.put("jumlah", jumlah);
        o.put("terakhirPada", terakhirPada);
        call.resolve(o);
    }
}
