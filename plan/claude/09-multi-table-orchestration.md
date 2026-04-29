# Issue: 09 - Multi-Table Orchestration (Opsional / Fase Lanjutan)

## 🎯 Tujuan
Mengangkat batasan single-table dari rilis pertama: memungkinkan operator melakukan migrasi **seluruh schema** dalam satu operasi, dengan auto-generate YAML untuk semua tabel sekaligus dan eksekusi job batch yang menghormati urutan dependency antar tabel (foreign key parent harus dimigrasi sebelum child).

> **Catatan penting:** Issue ini hanya dikerjakan **setelah Issue 01–08 stabil dan teruji di production migration window**. Jangan ambil shortcut dengan mengerjakan ini paralel — ada risiko refactor besar saat single-table flow belum benar-benar matang.

## 🔗 Dependensi
- Issue 03 (Auto-YAML)
- Issue 07 (Orchestrator)
- Issue 08 (TUI)
- Semua Issue 01–08 sudah memenuhi acceptance criteria.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Extend `auto_yaml.py` dengan fungsi schema-level.**
- Tambah fungsi `generate_mappings_for_schema(source_db, target_db) -> list[Path]`.
- Logika: query `information_schema.tables` di source untuk daftar tabel. Untuk setiap tabel, panggil `generate_mapping()` versi single-table. Output: list path file YAML.
- Tabel yang tidak ada di target: skip + log warning ke STDOUT (bukan error, karena mungkin operator memang tidak butuh tabel itu).

**Langkah 2: Definisikan struktur "JobBatch" di `orchestrator.py`.**
- Tambah class `JobBatch(jobs: list[MigrationJob])`.
- Method `run()` yang menjalankan job satu-per-satu secara **sekuensial** (bukan paralel — bottleneck network DB justru lebih buruk dengan parallel).
- Per default, satu job abort tidak menghentikan job berikutnya — sistem lanjut ke tabel lain dan melaporkan ringkasan akhir mana yang sukses, mana yang gagal.
- Sediakan flag `stop_on_failure: true/false` di config batch agar operator bisa pilih perilaku.

**Langkah 3: Topological sort untuk dependency tabel (opsional tapi recommended).**
- Query `information_schema.key_column_usage` untuk peta foreign key di target.
- Bangun graph: tabel → list parent (tabel yang harus migrasi duluan).
- Lakukan topological sort. Jika ada siklus (mis. circular FK): warning + jalan dengan urutan alfabet sebagai fallback.
- Eksekusi `JobBatch` sesuai urutan hasil sort.

**Langkah 4: Update file config batch (opsional, bisa pakai folder `mappings/` saja).**
- Pendekatan A: scan folder `mappings/` ambil semua file YAML, anggap satu folder = satu batch.
- Pendekatan B: buat file orchestration `migration_batch.yaml` yang mereferensikan list path mapping + flag `stop_on_failure`.
- Pilih A untuk MVP fase ini; B bisa ditambahkan kalau dibutuhkan.

**Langkah 5: Extend TUI di `screens/migrate.py`.**
- Tambah opsi "Run all mappings in folder" yang mentriger `JobBatch`.
- Layout updated: tampilkan **list job + progress per job** + overall progress (mis. "tabel 3 dari 12, 25%").
- Saat satu job abort: highlight di list dengan warna merah, tetap lanjut ke job berikutnya (kecuali `stop_on_failure=true`).

**Langkah 6: Test ulang acceptance criteria Issue 07–08 untuk memastikan tidak ada regresi.**
- Single-table mode harus tetap berjalan persis seperti sebelumnya — fitur multi-table adalah additive, bukan replacement.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] `generate_mappings_for_schema()` menghasilkan N file YAML untuk N tabel di source.
- [ ] `JobBatch.run()` menjalankan job berurutan; verifikasi via log timestamp tiap job.
- [ ] Satu job abort di tengah → job berikutnya tetap jalan (default behavior); `stop_on_failure=true` → abort menghentikan seluruh batch.
- [ ] Topological sort menghormati FK: parent table dimigrasi sebelum child table.
- [ ] TUI menampilkan list job + status per-job + overall progress, update real-time.
- [ ] Mode single-table dari Issue 07 masih bekerja tanpa regresi.

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi. Khusus untuk task ini, prioritaskan riset: implementasi topological sort sederhana di Python (pertimbangkan `graphlib.TopologicalSorter` di stdlib Python 3.9+), query `information_schema.key_column_usage` untuk MariaDB, dan praktik concurrent migration (apakah aman parallel — biasanya tidak karena bottleneck network).
