# Issue: 06 - Mesin Transformasi Data (Transformer)

## 🎯 Tujuan
Membangun pabrik pengolahan mini yang menerima sekelompok data mentah dari Sumber, mengubah bentuknya sesuai aturan di cetak biru pemetaan, lalu menyerahkannya dalam bentuk matang siap simpan.

## 🔗 Dependensi
- Issue: 01 (Pengaturan Konfigurasi)
- Issue: 04 (Pembuat Cetak Biru Pemetaan)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Pembuatan Generator Transformasi:** Rancang sebuah fungsi generator. Fungsi ini bertugas menerima sekelompok baris data dan memprosesnya satu per satu. Setelah satu baris selesai diproses dan diserahkan ke tahap berikutnya, referensi datanya langsung dihapus untuk menghemat memori.
2. **Penerapan Resolusi Tipe Data:** Terapkan logika untuk mengubah tipe data (misal dari teks terbatas menjadi teks panjang) berdasarkan panduan yang tertulis di cetak biru.
3. **Injeksi dan Pertahanan Objek Asli:** Jika cetak biru meminta nilai bawaan (default), suntikkan nilai tersebut. Pastikan juga kolom waktu dari Sumber dibiarkan dalam bentuk aslinya tanpa diubah menjadi teks oleh mesin ini.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Data yang masuk berhasil diubah bentuknya sesuai aturan cetak biru tanpa menyimpan seluruh kelompok data di dalam memori sekaligus.
- [ ] Data penanda waktu tidak mengalami perubahan wujud saat melewati mesin transformasi.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
