# Issue: 07 - Mesin Ekstraksi Data (Extractor)

## 🎯 Tujuan
Membangun alat pengeruk yang bertugas mengambil data dari database Sumber secara bertahap menggunakan metode halaman berbasis penanda identitas (Keyset Pagination), bukan metode melewakan baris dari awal.

## 🔗 Dependensi
- Issue: 02 (Manajer Koneksi)
- Issue: 05 (Manajemen Titik Lanjut)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pengambilan Penanda Awal:** Minta informasi ID penanda buku terakhir dari Manajer Titik Lanjut.
2. **Penyusunan Kueri Berbasis Kunci:** Buat instruksi pengambilan data yang meminta baris dengan ID lebih besar dari penanda terakhir.
3. **Penerapan Batas Kelompok Statis:** Terapkan pembatasan jumlah data yang diambil agar persis sama dengan ukuran kelompok yang telah ditetapkan secara statis di berkas konfigurasi. Jangan pernah menggunakan rumus perkiraan ukuran data yang dinamis.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Pengambilan data selalu dimulai dari titik lanjut terakhir, bukan dari awal tabel.
- [ ] Jumlah data yang diambil dalam satu tarikan tidak pernah melebihi batas ukuran kelompok statis.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
