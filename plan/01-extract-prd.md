**Role:** Bertindaklah sebagai Senior Software Architect dan Technical Lead.

**Konteks:** Kita telah memiliki Product Requirements Document (PRD) untuk aplikasi "Data Migration & Schema Transformation" MariaDB berbasis Python (sistem *one-time batch*, fitur *auto-generate* pemetaan YAML, dan *low-resource consumption*).

**Task:** Lakukan *breakdown* dokumen PRD tersebut menjadi arsitektur file yang komprehensif dan susun rencana pengembangan berfase (*phased work plan*). Rencana tugas ini dirancang khusus untuk didelegasikan kepada Junior Developer atau dieksekusi secara otonom oleh AI Agent / *Small Local LLM*. Berikan minimal 3 pertanyaan untuk optimasi dan meluruskan tujuan agar tidak halu. kemudian simpan plan dalam bentuk markdown kedalam folder `plan/claude/`.

**Batasan & Aturan Eksekusi (Constraints):**
1. **High-Level Concept Only:** Gunakan bahasa tingkat tinggi yang berfokus pada logika, alur data, dan tanggung jawab arsitektural. **DILARANG KERAS** menghasilkan atau menuliskan *source code* (Python, YAML, SQL, dll) di dalam respons ini.
2. **Struktur Berfase:** Bagi siklus pengembangan menjadi beberapa fase yang logis dan inkremental (misalnya: *Phase 1: Project Setup & Database Connection, Phase 2: Schema Introspection & YAML Generator, Phase 3: Batch Migration Engine*, dst).
3. **Rincian Task & File:** Pada setiap fase, definisikan dengan jelas:
   - Nama file target yang akan dibuat atau dimodifikasi.
   - Deskripsi terstruktur menggunakan Bahasa Indonesia mengenai langkah-langkah logis yang harus dikerjakan di dalam file tersebut.
4. **Standard Operating Procedure (SOP) Delegasi:** Sertakan secara eksplisit satu blok instruksi wajib di setiap awal task atau fase, yang ditujukan langsung sebagai *system prompt* untuk AI Agent / Junior Dev. Instruksi wajib tersebut harus berbunyi: 
   *"PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date* dan berkinerja tinggi."*

**Format Output yang Diharapkan:**
Gunakan format Markdown yang rapi. Awali dengan ringkasan arsitektur direktori/file (*folder tree*), kemudian jabarkan setiap fase dengan format daftar tugas (*Task List*) yang memuat informasi file, logika *high-level*, dan SOP Delegasi yang diminta.