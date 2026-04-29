# Issue: 02 - Pembuatan Manajer Koneksi Database

## 🎯 Tujuan
Menciptakan jembatan komunikasi antara aplikasi dengan database Sumber (Source) dan database Tujuan (Target) menggunakan teknik aliran data yang hemat memori.

## 🔗 Dependensi
- Issue: 01 (Pengaturan Konfigurasi)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Manajer Koneksi:** Siapkan sebuah sistem yang bertugas membuka dan menutup pintu koneksi ke database Sumber dan Tujuan secara aman.
2. **Penerapan Kursor Sisi Server (Streaming):** Untuk database Sumber, pastikan koneksi dikonfigurasi agar meminta database mengirimkan data seperti air mengalir sedikit demi sedikit, bukan mengirimkan jutaan baris sekaligus yang akan langsung membuat memori aplikasi jebol.
3. **Penonaktifan Fitur Perekam Kueri:** Pastikan sistem mematikan semua fitur bawaan yang merekam riwayat perintah database di latar belakang, karena ini berisiko menumpuk sampah di memori.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Koneksi ke database Sumber dan Tujuan berhasil dibangun secara independen.
- [ ] Pengambilan data dari Sumber dipastikan menggunakan mode aliran data (*streaming*) yang tidak membebani memori lokal.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.