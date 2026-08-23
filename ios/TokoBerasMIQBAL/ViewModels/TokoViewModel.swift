import SwiftUI

// ViewModel untuk mengelola data aplikasi
@MainActor
class TokoViewModel: ObservableObject {
    @Published var daftarBeras: [Beras] = []
    @Published var daftarTransaksi: [Transaksi] = []
    @Published var keranjang: [ItemTransaksi] = []

    init() {
        muatData()
    }

    // MARK: - Manajemen Produk

    func tambahBeras(_ beras: Beras) {
        daftarBeras.append(beras)
        simpanData()
    }

    func updateBeras(_ beras: Beras) {
        if let index = daftarBeras.firstIndex(where: { $0.id == beras.id }) {
            daftarBeras[index] = beras
            simpanData()
        }
    }

    func hapusBeras(_ beras: Beras) {
        daftarBeras.removeAll { $0.id == beras.id }
        simpanData()
    }

    func updateStok(berasId: UUID, stokBaru: Double) {
        if let index = daftarBeras.firstIndex(where: { $0.id == berasId }) {
            daftarBeras[index].stok = stokBaru
            simpanData()
        }
    }

    // MARK: - Manajemen Keranjang

    func tambahKeKeranjang(beras: Beras, jumlah: Double) {
        let item = ItemTransaksi(
            berasId: beras.id,
            namaBeras: beras.nama,
            jumlahKg: jumlah,
            hargaSatuan: beras.hargaPerKg,
            subtotal: jumlah * beras.hargaPerKg
        )
        keranjang.append(item)
    }

    func hapusFromKeranjang(_ item: ItemTransaksi) {
        keranjang.removeAll { $0.id == item.id }
    }

    func kosongkanKeranjang() {
        keranjang.removeAll()
    }

    var totalKeranjang: Double {
        keranjang.reduce(0) { $0 + $1.subtotal }
    }

    // MARK: - Manajemen Transaksi

    func buatTransaksi(namaPelanggan: String) {
        let transaksi = Transaksi(
            tanggal: Date(),
            items: keranjang,
            totalHarga: totalKeranjang,
            namaPelanggan: namaPelanggan,
            statusPembayaran: .lunas
        )

        daftarTransaksi.append(transaksi)

        // Kurangi stok
        for item in keranjang {
            if let index = daftarBeras.firstIndex(where: { $0.id == item.berasId }) {
                daftarBeras[index].stok -= item.jumlahKg
            }
        }

        kosongkanKeranjang()
        simpanData()
    }

    // MARK: - Data Persistence

    private let berasKey = "daftar_beras"
    private let transaksiKey = "daftar_transaksi"

    func simpanData() {
        // Simpan daftar beras
        if let berasData = try? JSONEncoder().encode(daftarBeras) {
            UserDefaults.standard.set(berasData, forKey: berasKey)
        }

        // Simpan daftar transaksi
        if let transaksiData = try? JSONEncoder().encode(daftarTransaksi) {
            UserDefaults.standard.set(transaksiData, forKey: transaksiKey)
        }

        print("✅ Data berhasil disimpan")
    }

    func muatData() {
        // Muat daftar beras
        if let berasData = UserDefaults.standard.data(forKey: berasKey),
           let beras = try? JSONDecoder().decode([Beras].self, from: berasData) {
            daftarBeras = beras
            print("✅ Data beras berhasil dimuat: \(beras.count) item")
        } else {
            loadSampleData()
            print("ℹ️ Menggunakan sample data")
        }

        // Muat daftar transaksi
        if let transaksiData = UserDefaults.standard.data(forKey: transaksiKey),
           let transaksi = try? JSONDecoder().decode([Transaksi].self, from: transaksiData) {
            daftarTransaksi = transaksi
            print("✅ Data transaksi berhasil dimuat: \(transaksi.count) item")
        }
    }

    func resetData() {
        UserDefaults.standard.removeObject(forKey: berasKey)
        UserDefaults.standard.removeObject(forKey: transaksiKey)
        daftarBeras.removeAll()
        daftarTransaksi.removeAll()
        loadSampleData()
        print("🔄 Data direset ke sample data")
    }

    // MARK: - Sample Data

    func loadSampleData() {
        daftarBeras = [
            Beras(
                nama: "Beras Premium Pandan Wangi",
                jenis: .premium,
                hargaPerKg: 18000,
                stok: 500,
                deskripsi: "Beras premium dengan aroma pandan alami, pulen dan enak",
                gambar: "rice.premium"
            ),
            Beras(
                nama: "Beras IR64",
                jenis: .medium,
                hargaPerKg: 12000,
                stok: 800,
                deskripsi: "Beras IR64 berkualitas baik untuk konsumsi sehari-hari",
                gambar: "rice.medium"
            ),
            Beras(
                nama: "Beras Ekonomis",
                jenis: .ekonomis,
                hargaPerKg: 9000,
                stok: 1000,
                deskripsi: "Beras ekonomis dengan kualitas terjamin",
                gambar: "rice.economy"
            ),
            Beras(
                nama: "Beras Organik",
                jenis: .organik,
                hargaPerKg: 25000,
                stok: 200,
                deskripsi: "Beras organik tanpa pestisida, sehat dan alami",
                gambar: "rice.organic"
            )
        ]
    }
}
