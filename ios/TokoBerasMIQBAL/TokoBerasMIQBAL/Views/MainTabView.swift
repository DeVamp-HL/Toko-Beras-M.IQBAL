import SwiftUI

struct MainTabView: View {
    @StateObject private var viewModel = TokoViewModel()

    var body: some View {
        TabView {
            // Tab 1: Katalog Produk
            KatalogView()
                .tabItem {
                    Label("Katalog", systemImage: "list.bullet.rectangle")
                }

            // Tab 2: Kasir/Transaksi
            KasirView()
                .tabItem {
                    Label("Kasir", systemImage: "cart.fill")
                }

            // Tab 3: Inventori/Stok
            InventoriView()
                .tabItem {
                    Label("Inventori", systemImage: "shippingbox.fill")
                }

            // Tab 4: Riwayat Transaksi
            RiwayatTransaksiView()
                .tabItem {
                    Label("Riwayat", systemImage: "clock.fill")
                }
        }
        .environmentObject(viewModel)
    }
}

#Preview {
    MainTabView()
}
