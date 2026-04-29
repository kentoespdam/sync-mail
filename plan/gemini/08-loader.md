# Issue: 08 - Mesin Pemuat Data dan Penanganan Kegagalan (Loader)

## 🎯 Tujuan
Membangun kurir yang bertugas menyisipkan sekelompok data matang ke database Tujuan secara massal. Sistem ini juga bertindak sebagai penjaga gerbang integritas yang kejam: satu saja salah, semua dibatalkan.

## 🔗 Dependensi
- Issue: 02 (Manajer Koneksi)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Penerapan Penyisipan Massal:** Buat perintah yang mampu memasukkan seluruh baris dalam satu kelompok ke database Tujuan secara bersamaan untuk mempercepat proses.
2. **Penguncian Transaksi:** Bungkus proses penyisipan ini dalam sebuah blok transaksi tertutup. Artinya, database tidak akan benar-benar menyimpan datanya sebelum kita beri aba-aba aman.
3. **Mekanisme Gagal Cepat (Fail-Fast):** Jika saat proses penyisipan terjadi penolakan atau masalah dari database Tujuan (misal ada kolom ganda), **SEGERA BATALKAN (ROLLBACK)** seluruh transaksi untuk kelompok tersebut.
4. **Pelaporan Kesalahan Fatal:** Jangan mencoba mengulangi penyisipan untuk data yang gagal. Langsung catat pesan masalah aslinya ke sistem log, dan kirimkan sinyal darurat ke program utama agar segera dimatikan.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Data berhasil disisipkan secara massal dengan dukungan transaksi atomik.
- [ ] Tidak ada mekanisme percobaan ulang (retry); jika ada satu baris yang cacat, seluruh kelompok dibatalkan dan sistem membunyikan alarm darurat.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
