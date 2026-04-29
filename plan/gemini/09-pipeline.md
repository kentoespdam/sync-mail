# Issue: 09 - Orkestrasi Pipa Pemrosesan (ETL Pipeline)

## 🎯 Tujuan
Merakit dan memimpin semua mesin (Ekstraksi, Transformasi, Pemuat, dan Penanda Buku) untuk bekerja sama dalam satu putaran siklus yang terus berulang sampai seluruh jutaan data habis dipindahkan.

## 🔗 Dependensi
- Issue: 05, 06, 07, 08

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Siklus Utama:** Buat sebuah perulangan yang akan terus memanggil Mesin Ekstraksi untuk mengambil data baru.
2. **Penyambungan Rantai Proses:** Alirkan data hasil ekstraksi ke Mesin Transformasi, lalu serahkan hasilnya ke Mesin Pemuat untuk disimpan.
3. **Pembaruan Penanda:** Jika Mesin Pemuat sukses menyisipkan satu kelompok data, segera laporkan ID data terakhir ke Manajer Titik Lanjut agar disimpan sebagai penanda kemajuan.
4. **Penanganan Sinyal Darurat:** Jika Mesin Pemuat mengirimkan sinyal darurat (gagal cepat), siklus utama harus segera dihentikan secara paksa saat itu juga, dan aplikasi dimatikan dengan status gagal.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Rantai proses berjalan otomatis dari tahap pengambilan hingga penyimpanan secara berulang.
- [ ] Penanda buku selalu diperbarui hanya setelah proses penyisipan satu kelompok data dipastikan berhasil seratus persen.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
