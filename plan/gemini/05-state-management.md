# Issue: 05 - Manajemen Titik Lanjut (State Management)

## 🎯 Tujuan
Membuat sistem penanda buku (*bookmark*) yang menyimpan posisi terakhir data yang berhasil dipindahkan, sehingga jika listrik mati atau proses terputus, aplikasi bisa melanjutkan dari titik terakhir tanpa mengulang dari awal.

## 🔗 Dependensi
- Issue: 01 (Pengaturan Konfigurasi)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Mekanisme Baca-Tulis:** Siapkan fungsi untuk menulis dan membaca sebuah berkas teks sederhana penyimpan status.
2. **Pencatatan ID Terakhir:** Fungsi penulisan harus mampu menerima nomor identitas (ID) baris terakhir yang sukses dipindahkan, lalu menyimpannya.
3. **Pemuatan Titik Lanjut:** Saat aplikasi pertama kali dijalankan, fungsi pembacaan harus memeriksa apakah berkas penanda buku ini ada. Jika ada, ambil ID terakhirnya sebagai titik awal pemrosesan.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] ID terakhir berhasil ditulis ke dalam berkas penyimpanan status.
- [ ] Aplikasi mampu membaca kembali ID terakhir tersebut saat dihidupkan ulang.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
