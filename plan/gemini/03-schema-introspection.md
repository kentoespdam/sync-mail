# Issue: 03 - Ekstraksi Struktur Database (Schema Introspection)

## 🎯 Tujuan
Membuat alat pembaca yang bisa meneliti dan mengumpulkan informasi mengenai nama-nama kolom dan tipe data dari tabel di database Sumber maupun Tujuan.

## 🔗 Dependensi
- Issue: 02 (Manajer Koneksi)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembacaan Metadata Sumber:** Buat perintah untuk membaca kamus informasi database Sumber guna mengetahui struktur tabel lamanya (nama kolom, tipe data, apakah boleh kosong).
2. **Pembacaan Metadata Tujuan:** Lakukan hal yang sama untuk database Tujuan guna mengetahui struktur tabel barunya yang sudah dioptimasi.
3. **Penyimpanan Gubah Suai:** Simpan hasil pembacaan dari kedua database ini ke dalam struktur data kamus internal agar mudah dibandingkan pada tahap selanjutnya.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Aplikasi mampu mengenali seluruh daftar kolom dari tabel Sumber dan Tujuan.
- [ ] Tipe data dari masing-masing kolom berhasil dideteksi dan disimpan di memori sementara.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
