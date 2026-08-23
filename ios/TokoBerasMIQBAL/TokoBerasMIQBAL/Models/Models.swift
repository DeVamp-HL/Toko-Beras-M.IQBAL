import Foundation

// Model untuk produk beras
struct Beras: Identifiable, Codable {
    var id = UUID()
    var nama: String
    var jenis: JenisBeras
    var hargaPerKg: Double
    var stok: Double // dalam kg
    var deskripsi: String
    var gambar: String // nama gambar

    enum JenisBeras: String, Codable, CaseIterable {
        case premium = "Premium"
        case medium = "Medium"
        case ekonomis = "Ekonomis"
        case organik = "Organik"
    }
}

// Model untuk transaksi
struct Transaksi: Identifiable, Codable {
    var id = UUID()
    var tanggal: Date
    var items: [ItemTransaksi]
    var totalHarga: Double
    var namaPelanggan: String
    var statusPembayaran: StatusPembayaran

    enum StatusPembayaran: String, Codable {
        case lunas = "Lunas"
        case belumLunas = "Belum Lunas"
    }
}

// Item dalam transaksi
struct ItemTransaksi: Identifiable, Codable {
    var id = UUID()
    var berasId: UUID
    var namaBeras: String
    var jumlahKg: Double
    var hargaSatuan: Double
    var subtotal: Double
}
