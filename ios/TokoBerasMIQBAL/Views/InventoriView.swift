import SwiftUI

// MARK: - Inventori View
struct InventoriView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @State private var showingTambahBeras = false
    @State private var selectedBeras: Beras?

    var body: some View {
        NavigationStack {
            List {
                // Ringkasan stok
                Section {
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Total Jenis Produk")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text("\(viewModel.daftarBeras.count)")
                                .font(.title2)
                                .fontWeight(.bold)
                        }

                        Spacer()

                        VStack(alignment: .trailing) {
                            Text("Total Stok")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text("\(Int(totalStok())) kg")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundStyle(.blue)
                        }
                    }
                    .padding(.vertical, 8)
                } header: {
                    Text("Ringkasan")
                }

                // Daftar produk
                Section {
                    ForEach(viewModel.daftarBeras) { beras in
                        Button {
                            selectedBeras = beras
                        } label: {
                            InventoriRowView(beras: beras)
                        }
                        .foregroundStyle(.primary)
                    }
                } header: {
                    Text("Produk")
                }
            }
            .navigationTitle("Inventori")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        showingTambahBeras = true
                    } label: {
                        Label("Tambah Produk", systemImage: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingTambahBeras) {
                TambahBerasView()
            }
            .sheet(item: $selectedBeras) { beras in
                EditBerasView(beras: beras)
            }
        }
    }

    func totalStok() -> Double {
        viewModel.daftarBeras.reduce(0) { $0 + $1.stok }
    }
}

// MARK: - Inventori Row View
struct InventoriRowView: View {
    let beras: Beras

    var stokStatus: (text: String, color: Color) {
        if beras.stok < 100 {
            return ("Stok Rendah", .red)
        } else if beras.stok < 300 {
            return ("Stok Sedang", .orange)
        } else {
            return ("Stok Cukup", .green)
        }
    }

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(beras.nama)
                    .font(.headline)

                Text(beras.jenis.rawValue)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 4) {
                Text("\(Int(beras.stok)) kg")
                    .font(.headline)
                    .foregroundStyle(stokStatus.color)

                Text(stokStatus.text)
                    .font(.caption)
                    .foregroundStyle(stokStatus.color)
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Tambah Beras View
struct TambahBerasView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @Environment(\.dismiss) var dismiss

    @State private var nama = ""
    @State private var jenis: Beras.JenisBeras = .medium
    @State private var harga = ""
    @State private var stok = ""
    @State private var deskripsi = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Informasi Produk") {
                    TextField("Nama Beras", text: $nama)

                    Picker("Jenis", selection: $jenis) {
                        ForEach(Beras.JenisBeras.allCases, id: \.self) { jenis in
                            Text(jenis.rawValue).tag(jenis)
                        }
                    }
                }

                Section("Harga & Stok") {
                    HStack {
                        Text("Rp")
                        TextField("Harga per kg", text: $harga)
                            .keyboardType(.numberPad)
                    }

                    HStack {
                        TextField("Stok", text: $stok)
                            .keyboardType(.decimalPad)
                        Text("kg")
                    }
                }

                Section("Deskripsi") {
                    TextEditor(text: $deskripsi)
                        .frame(height: 100)
                }

                Section {
                    Button("Simpan Produk") {
                        simpanBeras()
                    }
                    .frame(maxWidth: .infinity)
                    .disabled(!isValid)
                }
            }
            .navigationTitle("Tambah Produk")
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

    var isValid: Bool {
        !nama.isEmpty &&
        Double(harga) != nil &&
        Double(stok) != nil &&
        !deskripsi.isEmpty
    }

    func simpanBeras() {
        guard let hargaValue = Double(harga),
              let stokValue = Double(stok) else { return }

        let berasBaru = Beras(
            nama: nama,
            jenis: jenis,
            hargaPerKg: hargaValue,
            stok: stokValue,
            deskripsi: deskripsi,
            gambar: "rice.default"
        )

        viewModel.tambahBeras(berasBaru)
        dismiss()
    }
}

// MARK: - Edit Beras View
struct EditBerasView: View {
    @EnvironmentObject var viewModel: TokoViewModel
    @Environment(\.dismiss) var dismiss

    let beras: Beras

    @State private var nama = ""
    @State private var jenis: Beras.JenisBeras = .medium
    @State private var harga = ""
    @State private var stok = ""
    @State private var deskripsi = ""
    @State private var showingDeleteAlert = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Informasi Produk") {
                    TextField("Nama Beras", text: $nama)

                    Picker("Jenis", selection: $jenis) {
                        ForEach(Beras.JenisBeras.allCases, id: \.self) { jenis in
                            Text(jenis.rawValue).tag(jenis)
                        }
                    }
                }

                Section("Harga & Stok") {
                    HStack {
                        Text("Rp")
                        TextField("Harga per kg", text: $harga)
                            .keyboardType(.numberPad)
                    }

                    HStack {
                        TextField("Stok", text: $stok)
                            .keyboardType(.decimalPad)
                        Text("kg")
                    }
                }

                Section("Deskripsi") {
                    TextEditor(text: $deskripsi)
                        .frame(height: 100)
                }

                Section {
                    Button("Update Produk") {
                        updateBeras()
                    }
                    .frame(maxWidth: .infinity)
                    .disabled(!isValid)
                }

                Section {
                    Button("Hapus Produk", role: .destructive) {
                        showingDeleteAlert = true
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .navigationTitle("Edit Produk")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Batal") {
                        dismiss()
                    }
                }
            }
            .alert("Hapus Produk?", isPresented: $showingDeleteAlert) {
                Button("Hapus", role: .destructive) {
                    hapusBeras()
                }
                Button("Batal", role: .cancel) { }
            } message: {
                Text("Apakah Anda yakin ingin menghapus \(beras.nama)?")
            }
            .onAppear {
                loadData()
            }
        }
    }

    var isValid: Bool {
        !nama.isEmpty &&
        Double(harga) != nil &&
        Double(stok) != nil &&
        !deskripsi.isEmpty
    }

    func loadData() {
        nama = beras.nama
        jenis = beras.jenis
        harga = String(Int(beras.hargaPerKg))
        stok = String(format: "%.1f", beras.stok)
        deskripsi = beras.deskripsi
    }

    func updateBeras() {
        guard let hargaValue = Double(harga),
              let stokValue = Double(stok) else { return }

        var updatedBeras = beras
        updatedBeras.nama = nama
        updatedBeras.jenis = jenis
        updatedBeras.hargaPerKg = hargaValue
        updatedBeras.stok = stokValue
        updatedBeras.deskripsi = deskripsi

        viewModel.updateBeras(updatedBeras)
        dismiss()
    }

    func hapusBeras() {
        viewModel.hapusBeras(beras)
        dismiss()
    }
}

#Preview {
    InventoriView()
        .environmentObject(TokoViewModel())
}
