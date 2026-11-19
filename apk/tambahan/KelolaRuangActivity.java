package id.miqbal.tokoberas;

import android.app.Activity;
import android.os.Bundle;

// Penjaga data aplikasi (paket S1, 19 Nov 2026; tips resmi SUNMI "How to avoid application data from being cleared"):
// dipasang sebagai manageSpaceActivity, jadi tombol "Hapus data" di Setelan › Aplikasi berubah jadi "Kelola ruang" yang membuka
// aktivitas ini — dan aktivitas ini langsung menutup diri. Akun tablet, antrean catatan yang belum sampai server, dan setelan printer
// tidak bisa terhapus oleh ketukan yang salah. Menghapus sungguhan = copot aplikasinya.
public class KelolaRuangActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        finish();
    }
}
