# Issue: 04 - Pembuat Cetak Biru Pemetaan (YAML Auto-Generator)

## 🎯 Tujuan
Membangun alat otomatis yang membandingkan struktur tabel Sumber dan Tujuan, lalu menghasilkan sebuah berkas cetak biru pemetaan yang nantinya bisa dimodifikasi oleh pengguna.

## 🔗 Dependensi
- Issue: 03 (Ekstraksi Struktur Database)

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
1. **Analisis Perbandingan Tabel:** Bandingkan data kolom dari Sumber dan Tujuan. Cari kolom yang namanya sama persis, dan cari kolom yang ada di Tujuan tapi tidak ada di Sumber.
2. **Penerapan Aturan Waktu (Timestamp):** Jika menemukan kolom terkait waktu (seperti tanggal pembuatan atau pembaruan), tetapkan aturannya menjadi pemetaan langsung tanpa manipulasi apapun. Hal ini agar presisi waktu mili-detik tetap terjaga identik.
3. **Penyusunan Berkas Cetak Biru:** Tulis hasil perbandingan ini ke dalam sebuah berkas. Sematkan informasi ukuran kelompok (*batch size*) di bagian paling atas berkas dengan nilai standar yang aman, sehingga pengguna tahu di mana mereka harus mengaturnya.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Berkas cetak biru berhasil dibuat secara otomatis dengan format yang terstruktur.
- [ ] Kolom penanda waktu secara otomatis mendapatkan label pemetaan langsung.

## ⚠️ SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
