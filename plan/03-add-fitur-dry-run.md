**Role:** Bertindaklah sebagai Technical Project Manager dan Senior Software Architect.

**Konteks Input:** > Master Plan dari `plan/00-prd.md`

**Pembaruan Fitur Kritis:** Master Plan harus diperbarui untuk mencakup fase/modul **"Dry Run & Validation Mode"**. Mode ini menyimulasikan proses Extract dan Transform berdasarkan konfigurasi YAML *tanpa* mengeksekusi `INSERT/COMMIT` ke database target. Jika ditemukan anomali (misal: *type mismatch*, *data truncation*, atau constraint gagal), sistem tidak boleh sekadar *crash*, melainkan harus mengumpulkan daftar *error* tersebut, mengidentifikasi detail kerusakannya, dan menampilkan log beserta **rekomendasi cara penanganannya** (misal: "Sesuaikan panjang varchar di YAML", "Tambahkan default value untuk kolom X").

**Task:** Ekstrak dan terjemahkan Master Plan yang sudah diperbarui dengan fitur *Dry Run* ini menjadi sekumpulan dokumen "Issue Ticket" berformat Markdown file kedalam folder `plan/claude/`, skip/abaikan issue file yang sudah terbentuk. Tiket-tiket ini dirancang sebagai panduan kerja mandiri untuk Junior Developer yang masih baru mengenal Python, atau untuk dieksekusi secara otonom oleh AI Agent berukuran kecil.

**Batasan & Aturan Penulisan (Constraints):**
1. **Beginner-Friendly & High-Level:** Gunakan bahasa Indonesia yang jelas dan terurut. Jelaskan logika sistem dengan cara yang intuitif.
2. **STRICTLY NO SOURCE CODE:** DILARANG KERAS menuliskan implementasi *source code* (Python, YAML, atau SQL). Fokus murni pada instruksi alur logika.
3. **Urutan Kronologis:** Pastikan penomoran *issue* jelas. Buatkan setidaknya satu tiket *issue* khusus yang fokus murni pada pembangunan *engine Dry Run* dan *Error Reporting* ini.
4. **Scan File & Logic:** Pastikan menggunakan `/graphify query` untuk mencari file dan logic, gunakan `scanfile` jika data yang dibutuhkan tidak ketemu.
 
**Format Wajib untuk Setiap Issue File:**
```markdown
# Issue: [Nomor Urut] - [Nama Task Spesifik]

## 🎯 Tujuan
[Jelaskan apa tujuan akhir dari pembuatan/modifikasi file pada task ini]
 
## 🔗 Dependensi
[Sebutkan nomor issue yang harus diselesaikan sebelum task ini bisa dimulai]
 
## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
[Jabarkan langkah logisnya. Khusus untuk tiket Dry Run, jelaskan alur validasi datanya dan format pelaporan error yang solutif]
 
## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] [Kondisi 1 yang harus terpenuhi]
- [ ] [Kondisi 2 yang harus terpenuhi]
 
## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.
```

**Pro Tip:** Saat Junior Dev atau AI Agent mengerjakan *issue* tentang *Dry Run* ini, pastikan untuk meminta mereka menguji *script* menggunakan *dummy data* sebesar 10-100 baris saja terlebih dahulu. Ini mempercepat siklus verifikasi apakah *format error* yang ditampilkan sudah benar-benar mudah dibaca oleh operator manusia sebelum diuji pada jutaan data.
