# Issue: 10 - Titik Masuk dan Pengontrol Perintah (CLI & Graceful Shutdown)

## 🎯 Tujuan
Membuat pintu depan aplikasi yang memungkinkan pengguna berinteraksi melalui terminal, memilih mode operasi, dan memastikan aplikasi bisa ditutup dengan sopan saat ditekan tombol batal oleh pengguna.

## 🔗 Dependensi
- Issue: 04 (Pembuat Cetak Biru Pemetaan)
- Issue: 09 (Orkestrasi Pipa Pemrosesan)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Menu Terminal:** Rancang sistem penerima argumen teks dari terminal. Siapkan dua perintah utama: satu untuk menjalankan fitur pembuatan cetak biru pemetaan, dan satu lagi untuk menjalankan pipa migrasi data.
2. **Penanganan Interupsi Pengguna (Graceful Shutdown):** Terapkan sistem pendeteksi sinyal henti (misalnya saat pengguna menekan tombol Ctrl+C di terminal). Jika tombol ini ditekan, aplikasi tidak boleh langsung mati. Aplikasi harus membiarkan kelompok data yang sedang diproses selesai terlebih dahulu, mencatat ID terakhirnya, barulah aplikasi keluar dengan aman tanpa merusak keutuhan database Tujuan.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Pengguna bisa memilih untuk membuat cetak biru pemetaan atau menjalankan perpindahan data lewat perintah terminal.
- [ ] Aplikasi bisa berhenti dengan aman (menyelesaikan tugas yang tertanggung) saat mendapat perintah henti dari pengguna.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
