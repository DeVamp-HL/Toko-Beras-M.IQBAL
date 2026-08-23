import SwiftUI

// MARK: - Riwayat Transaksi View
struct RiwayatTransaksiView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @State private var selectedTransaksi: Transaksi?

    var transaksiTerurut: [Transaksi] {
        viewModel.daftarTransaksi.sorted { $0.tanggal > $1.tanggal }
    }

    var totalPendapatan: Double {
        viewModel.daftarTransaksi.reduce(0) { $0 + $1.totalHarga }
    }

    var body: some View {
        NavigationStack {
            VStack {
                if viewModel.daftarTransaksi.isEmpty {
                    // Empty state
                    VStack(spacing: 20) {
                        Image(systemName: "doc.text")
                            .font(.system(size: 80))
                            .foregroundStyle(.gray)
                        Text("Belum Ada Transaksi")
                            .font(.title2)
                            .fontWeight(.semibold)
                        Text("Riwayat transaksi akan muncul di sini")
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxHeight: .infinity)
                } else {
                    List {
                        // Ringkasan penjualan
                        Section {
                            VStack(spacing: 16) {
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text("Total Transaksi")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                        Text("\(viewModel.daftarTransaksi.count)")
                                            .font(.title2)
                                            .fontWeight(.bold)
                                    }

                                    Spacer()

                                    VStack(alignment: .trailing) {
                                        Text("Total Pendapatan")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                        Text("Rp \(formatRupiah(totalPendapatan))")
                                            .font(.title3)
                                            .fontWeight(.bold)
                                            .foregroundStyle(.green)
                                    }
                                }
                            }
                            .padding(.vertical, 8)
                        } header: {
                            Text("Ringkasan Penjualan")
                        }

                        // Daftar transaksi
                        Section {
                            ForEach(transaksiTerurut) { transaksi in
                                Button {
                                    selectedTransaksi = transaksi
                                } label: {
                                    TransaksiRowView(transaksi: transaksi)
                                }
                                .foregroundStyle(.primary)
                            }
                        } header: {
                            Text("Riwayat")
                        }
                    }
                }
            }
            .navigationTitle("Riwayat Transaksi")
            .sheet(item: $selectedTransaksi) { transaksi in
                DetailTransaksiView(transaksi: transaksi)
            }
        }
    }
}

// MARK: - Transaksi Row View
struct TransaksiRowView: View {
    let transaksi: Transaksi

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(transaksi.namaPelanggan)
                    .font(.headline)

                Spacer()

                Text(transaksi.statusPembayaran.rawValue)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(statusColor.opacity(0.2))
                    .foregroundStyle(statusColor)
                    .clipShape(Capsule())
            }

            HStack {
                Text(formatTanggal(transaksi.tanggal))
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Spacer()

                Text("Rp \(formatRupiah(transaksi.totalHarga))")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(.green)
            }

            Text("\(transaksi.items.count) item")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 4)
    }

    var statusColor: Color {
        switch transaksi.statusPembayaran {
        case .lunas: return .green
        case .belumLunas: return .orange
        }
    }

    func formatTanggal(_ tanggal: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "dd MMM yyyy, HH:mm"
        formatter.locale = Locale(identifier: "id_ID")
        return formatter.string(from: tanggal)
    }
}

// MARK: - Detail Transaksi View
struct DetailTransaksiView: View {
    let transaksi: Transaksi
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            List {
                // Info transaksi
                Section("Informasi Transaksi") {
                    HStack {
                        Text("Tanggal")
                        Spacer()
                        Text(formatTanggal(transaksi.tanggal))
                            .foregroundStyle(.secondary)
                    }

                    HStack {
                        Text("Pelanggan")
                        Spacer()
                        Text(transaksi.namaPelanggan)
                            .foregroundStyle(.secondary)
                    }

                    HStack {
                        Text("Status")
                        Spacer()
                        Text(transaksi.statusPembayaran.rawValue)
                            .foregroundStyle(statusColor)
                            .fontWeight(.semibold)
                    }
                }

                // Item yang dibeli
                Section("Item Pembelian") {
                    ForEach(transaksi.items) { item in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(item.namaBeras)
                                    .font(.headline)
                                Spacer()
                                Text("Rp \(formatRupiah(item.subtotal))")
                                    .fontWeight(.semibold)
                                    .foregroundStyle(.green)
                            }

                            Text("\(formatNumber(item.jumlahKg)) kg × Rp \(formatRupiah(item.hargaSatuan))")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                }

                // Total
                Section {
                    HStack {
                        Text("Total Pembayaran")
                            .font(.headline)
                        Spacer()
                        Text("Rp \(formatRupiah(transaksi.totalHarga))")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundStyle(.green)
                    }
                }
            }
            .navigationTitle("Detail Transaksi")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Tutup") {
                        dismiss()
                    }
                }
            }
        }
    }

    var statusColor: Color {
        switch transaksi.statusPembayaran {
        case .lunas: return .green
        case .belumLunas: return .orange
        }
    }

    func formatTanggal(_ tanggal: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "dd MMMM yyyy, HH:mm"
        formatter.locale = Locale(identifier: "id_ID")
        return formatter.string(from: tanggal)
    }

    func formatNumber(_ angka: Double) -> String {
        let formatter = NumberFormatter()
        formatter.minimumFractionDigits = 0
        formatter.maximumFractionDigits = 2
        return formatter.string(from: NSNumber(value: angka)) ?? "0"
    }
}

#Preview {
    RiwayatTransaksiView()
        .environmentObject(TokoViewModel())
}
