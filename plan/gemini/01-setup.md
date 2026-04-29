# Issue: 01 - Pengaturan Konfigurasi dan Pencatatan Log (Setup & Logging)

## 🎯 Tujuan
Membangun fondasi aplikasi untuk membaca pengaturan lingkungan (seperti kata sandi database dan file pemetaan) serta menyiapkan sistem pencatatan aktivitas (log) agar setiap kejadian di dalam aplikasi dapat dilacak.

## 🔗 Dependensi
- Tidak ada. Ini adalah langkah pertama.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Pengelola Konfigurasi:** Buat sebuah alat pengelola yang bertugas membaca kredensial database. Alat ini juga harus mampu membaca file pengaturan pemetaan.
2. **Validasi Ukuran Kelompok (Batching):** Konsep *batching* adalah membagi pekerjaan jutaan data menjadi kelompok-kelompok kecil (misal: 2500 baris per proses) agar memori komputer tidak penuh. Alat pengelola konfigurasi wajib memeriksa apakah nilai ukuran kelompok ini ada di dalam file pengaturan. Jika tidak ada atau nilainya tidak masuk akal, segera hentikan aplikasi.
3. **Pencatatan Aktivitas Layar (Console Log):** Buat sistem pencatat yang menampilkan informasi ke layar terminal secara langsung (seperti kecepatan proses dan status saat ini).
4. **Pencatatan Aktivitas Berkas (File Log):** Buat sistem pencatat kedua yang khusus menyimpan pesan kegagalan ke dalam sebuah berkas. Pastikan berkas ini bisa berotasi (membuat berkas baru secara otomatis jika ukurannya sudah terlalu besar) agar tidak memenuhi kapasitas penyimpanan server.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Aplikasi menolak berjalan jika pengaturan ukuran kelompok (*batch size*) tidak ditemukan.
- [ ] Sistem pencatatan mampu memisahkan informasi umum (ke layar) dan informasi kegagalan (ke berkas).

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
