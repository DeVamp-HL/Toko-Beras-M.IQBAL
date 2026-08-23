import SwiftUI

// MARK: - Kasir View
struct KasirView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @State private var namaPelanggan = ""
    @State private var showingCheckout = false
    @State private var showingSuccess = false

    var body: some View {
        NavigationStack {
            VStack {
                if viewModel.keranjang.isEmpty {
                    // Empty state
                    VStack(spacing: 20) {
                        Image(systemName: "cart")
                            .font(.system(size: 80))
                            .foregroundStyle(.gray)
                        Text("Keranjang Kosong")
                            .font(.title2)
                            .fontWeight(.semibold)
                        Text("Tambahkan produk dari katalog")
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxHeight: .infinity)
                } else {
                    // List item keranjang
                    List {
                        Section {
                            ForEach(viewModel.keranjang) { item in
                                KeranjangItemRow(item: item)
                            }
                            .onDelete(perform: hapusItem)
                        } header: {
                            Text("Item Belanja")
                        }

                        Section {
                            HStack {
                                Text("Subtotal")
                                Spacer()
                                Text("Rp \(formatRupiah(viewModel.totalKeranjang))")
                                    .fontWeight(.semibold)
                            }

                            HStack {
                                Text("Total")
                                    .font(.headline)
                                Spacer()
                                Text("Rp \(formatRupiah(viewModel.totalKeranjang))")
                                    .font(.title3)
                                    .fontWeight(.bold)
                                    .foregroundStyle(.green)
                            }
                        } header: {
                            Text("Ringkasan")
                        }
                    }

                    // Tombol checkout
                    VStack(spacing: 12) {
                        Button {
                            showingCheckout = true
                        } label: {
                            Label("Proses Pembayaran", systemImage: "creditcard.fill")
                                .font(.headline)
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                        }

                        Button {
                            viewModel.kosongkanKeranjang()
                        } label: {
                            Text("Kosongkan Keranjang")
                                .font(.subheadline)
                                .foregroundStyle(.red)
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Kasir")
            .sheet(isPresented: $showingCheckout) {
                CheckoutView(
                    namaPelanggan: $namaPelanggan,
                    onCheckout: {
                        prosesCheckout()
                    }
                )
            }
            .alert("Transaksi Berhasil", isPresented: $showingSuccess) {
                Button("OK") { }
            } message: {
                Text("Transaksi untuk \(namaPelanggan) telah berhasil diproses")
            }
        }
    }

    func hapusItem(at offsets: IndexSet) {
        for index in offsets {
            let item = viewModel.keranjang[index]
            viewModel.hapusFromKeranjang(item)
        }
    }

    func prosesCheckout() {
        viewModel.buatTransaksi(namaPelanggan: namaPelanggan.isEmpty ? "Customer" : namaPelanggan)
        showingCheckout = false
        showingSuccess = true
        namaPelanggan = ""
    }
}

// MARK: - Keranjang Item Row
struct KeranjangItemRow: View {
    let item: ItemTransaksi

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(item.namaBeras)
                .font(.headline)

            HStack {
                Text("\(formatNumber(item.jumlahKg)) kg × Rp \(formatRupiah(item.hargaSatuan))")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                Spacer()

                Text("Rp \(formatRupiah(item.subtotal))")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(.green)
            }
        }
        .padding(.vertical, 4)
    }

    func formatNumber(_ angka: Double) -> String {
        let formatter = NumberFormatter()
        formatter.minimumFractionDigits = 0
        formatter.maximumFractionDigits = 2
        return formatter.string(from: NSNumber(value: angka)) ?? "0"
    }
}

// MARK: - Checkout View
struct CheckoutView: View {
    @Binding var namaPelanggan: String
    let onCheckout: () -> Void
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Nama Pelanggan", text: $namaPelanggan)
                } header: {
                    Text("Informasi Pelanggan")
                } footer: {
                    Text("Opsional - kosongkan jika tidak ada nama")
                }

                Section {
                    Button {
                        onCheckout()
                    } label: {
                        HStack {
                            Spacer()
                            Label("Konfirmasi Pembayaran", systemImage: "checkmark.circle.fill")
                                .font(.headline)
                            Spacer()
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                }
            }
            .navigationTitle("Checkout")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Batal") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    KasirView()
        .environmentObject(TokoViewModel())
}
