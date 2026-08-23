import SwiftUI

// MARK: - Katalog View
struct KatalogView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @State private var searchText = ""
    @State private var filterJenis: Beras.JenisBeras?

    var filteredBeras: [Beras] {
        var hasil = viewModel.daftarBeras

        // Filter berdasarkan pencarian
        if !searchText.isEmpty {
            hasil = hasil.filter { $0.nama.localizedCaseInsensitiveContains(searchText) }
        }

        // Filter berdasarkan jenis
        if let jenis = filterJenis {
            hasil = hasil.filter { $0.jenis == jenis }
        }

        return hasil
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Header dengan info toko
                VStack(spacing: 8) {
                    Text("🌾 Toko Beras M.IQBAL")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Beras Berkualitas untuk Keluarga Indonesia")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color(.systemBackground))

                // Filter jenis beras
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        FilterButton(
                            title: "Semua",
                            isSelected: filterJenis == nil,
                            action: { filterJenis = nil }
                        )

                        ForEach(Beras.JenisBeras.allCases, id: \.self) { jenis in
                            FilterButton(
                                title: jenis.rawValue,
                                isSelected: filterJenis == jenis,
                                action: { filterJenis = jenis }
                            )
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)

                // List produk
                List {
                    ForEach(filteredBeras) { beras in
                        NavigationLink {
                            DetailBerasView(beras: beras)
                        } label: {
                            BerasRowView(beras: beras)
                        }
                    }
                }
                .listStyle(.plain)
                .searchable(text: $searchText, prompt: "Cari beras...")
            }
            .navigationTitle("Katalog Produk")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// MARK: - Beras Row View
struct BerasRowView: View {
    let beras: Beras

    var body: some View {
        HStack(spacing: 12) {
            // Icon beras
            Image(systemName: "leaf.circle.fill")
                .font(.system(size: 50))
                .foregroundStyle(colorForJenis(beras.jenis))

            VStack(alignment: .leading, spacing: 4) {
                Text(beras.nama)
                    .font(.headline)

                HStack {
                    Text(beras.jenis.rawValue)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(colorForJenis(beras.jenis).opacity(0.2))
                        .foregroundStyle(colorForJenis(beras.jenis))
                        .clipShape(Capsule())

                    Spacer()

                    Text("Stok: \(Int(beras.stok)) kg")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Text("Rp \(formatRupiah(beras.hargaPerKg))/kg")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(.green)
            }
        }
        .padding(.vertical, 8)
    }

    func colorForJenis(_ jenis: Beras.JenisBeras) -> Color {
        switch jenis {
        case .premium: return .purple
        case .medium: return .blue
        case .ekonomis: return .orange
        case .organik: return .green
        }
    }
}

// MARK: - Filter Button
struct FilterButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue : Color(.systemGray6))
                .foregroundStyle(isSelected ? .white : .primary)
                .clipShape(Capsule())
        }
    }
}

// MARK: - Detail Beras View
struct DetailBerasView: View {
    let beras: Beras
    @EnvironmentObject var viewModel: TokoViewModel
    @State private var jumlahBeli: String = "1"
    @State private var showingAlert = false
    @Environment(\.dismiss) var dismiss

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Gambar produk
                Image(systemName: "leaf.circle.fill")
                    .font(.system(size: 120))
                    .foregroundStyle(colorForJenis(beras.jenis))
                    .padding()

                // Info produk
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text(beras.nama)
                            .font(.title2)
                            .fontWeight(.bold)
                        Spacer()
                    }

                    HStack {
                        Text(beras.jenis.rawValue)
                            .font(.subheadline)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(colorForJenis(beras.jenis).opacity(0.2))
                            .foregroundStyle(colorForJenis(beras.jenis))
                            .clipShape(Capsule())

                        Spacer()

                        Text("Stok: \(Int(beras.stok)) kg")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }

                    Divider()

                    // Harga
                    HStack {
                        Text("Harga")
                            .foregroundStyle(.secondary)
                        Spacer()
                        Text("Rp \(formatRupiah(beras.hargaPerKg))/kg")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundStyle(.green)
                    }

                    Divider()

                    // Deskripsi
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Deskripsi")
                            .font(.headline)
                        Text(beras.deskripsi)
                            .foregroundStyle(.secondary)
                    }

                    Divider()

                    // Input jumlah
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Jumlah (kg)")
                            .font(.headline)

                        HStack {
                            TextField("Jumlah", text: $jumlahBeli)
                                .keyboardType(.decimalPad)
                                .textFieldStyle(.roundedBorder)

                            Text("kg")
                                .foregroundStyle(.secondary)
                        }

                        if let jumlah = Double(jumlahBeli), jumlah > 0 {
                            Text("Total: Rp \(formatRupiah(jumlah * beras.hargaPerKg))")
                                .font(.headline)
                                .foregroundStyle(.green)
                        }
                    }
                }
                .padding()

                // Tombol tambah ke keranjang
                Button {
                    tambahKeKeranjang()
                } label: {
                    Label("Tambah ke Keranjang", systemImage: "cart.fill.badge.plus")
                        .font(.headline)
                        .foregroundStyle(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.horizontal)
                .disabled(Double(jumlahBeli) ?? 0 <= 0)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .alert("Berhasil", isPresented: $showingAlert) {
            Button("OK") {
                dismiss()
            }
        } message: {
            Text("Produk berhasil ditambahkan ke keranjang")
        }
    }

    func tambahKeKeranjang() {
        guard let jumlah = Double(jumlahBeli), jumlah > 0 else { return }
        viewModel.tambahKeKeranjang(beras: beras, jumlah: jumlah)
        showingAlert = true
    }

    func colorForJenis(_ jenis: Beras.JenisBeras) -> Color {
        switch jenis {
        case .premium: return .purple
        case .medium: return .blue
        case .ekonomis: return .orange
        case .organik: return .green
        }
    }
}

// MARK: - Helper Function
func formatRupiah(_ angka: Double) -> String {
    let formatter = NumberFormatter()
    formatter.numberStyle = .decimal
    formatter.groupingSeparator = "."
    formatter.maximumFractionDigits = 0
    return formatter.string(from: NSNumber(value: angka)) ?? "0"
}

#Preview {
    KatalogView()
        .environmentObject(TokoViewModel())
}
