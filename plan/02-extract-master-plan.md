**Role:** Bertindaklah sebagai Technical Project Manager dan Senior Software Architect.

**Konteks Input:** > plan yang sudah terbentuk sebelumnya. `plan/claude/00-master-plan.md`

**Task:** Ekstrak dan terjemahkan Master Plan di atas menjadi sekumpulan dokumen "Issue Ticket" berformat Markdown (misal: `issue-01-setup.md`, `issue-02-yaml-generator.md`, dst). Tiket-tiket ini dirancang sebagai panduan kerja mandiri untuk Junior Developer yang masih baru mengenal Python, atau untuk dieksekusi secara otonom oleh AI Agent berukuran kecil. simpan kedalam folder `plan/claude`.

**Batasan & Aturan Penulisan (Constraints):**
1. **Beginner-Friendly & High-Level:** Gunakan bahasa Indonesia yang sangat jelas, terurut (*step-by-step*), dan mudah dicerna. Jelaskan konsep arsitektural (seperti *batching/chunking*) dengan cara yang intuitif bagi pemula.
2. **STRICTLY NO SOURCE CODE:** DILARANG KERAS menuliskan implementasi *source code* (Python, YAML, atau SQL) di dalam respons ini. Fokus murni pada instruksi alur logika, desain sistem, dan *requirements*.
3. **Urutan Kronologis:** Pastikan penomoran *issue* jelas dan berurutan sesuai alur kerja ETL yang masuk akal.

**Format Wajib untuk Setiap Issue File:**
Setiap *issue* yang kamu hasilkan wajib menggunakan struktur *template* berikut:

```markdown
# Issue: [Nomor Urut] - [Nama Task Spesifik]

## 🎯 Tujuan
[Jelaskan apa tujuan akhir dari pembuatan/modifikasi file pada task ini]

## 🔗 Dependensi
[Sebutkan nomor issue yang harus diselesaikan sebelum task ini bisa dimulai]

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)
[Jabarkan langkah-langkah logis yang harus diprogram. Misal: "Langkah 1: Buat fungsi pembaca konfigurasi. Langkah 2: Buat koneksi ke database target", dst. Gunakan bahasa deskriptif tanpa koding]

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] [Kondisi 1 yang harus terpenuhi]
- [ ] [Kondisi 2 yang harus terpenuhi]

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
```