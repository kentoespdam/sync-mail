# Issue: 07 - Orchestrator & Resume Logic

## 🎯 Tujuan
Merangkai loader mapping (Issue 04), checkpoint (Issue 05), dan tiga komponen ETL (Issue 06) menjadi satu job migrasi end-to-end yang dapat dijalankan dari awal sampai selesai. Orchestrator bertanggung jawab atas: titik mulai (resume dari checkpoint kalau ada), looping batch, update checkpoint per batch, abort-on-failure (sesuai keputusan master plan §0), graceful shutdown saat operator menekan Ctrl+C, dan publishing event ke event bus untuk dikonsumsi TUI.

## 🔗 Dependensi
- Issue 04 (Mapping Loader & Validator)
- Issue 05 (Checkpoint State)
- Issue 06 (ETL Pipeline)
- Issue 01 (Foundation) — event bus.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Buat class `MigrationJob` di `src/sync_mail/pipeline/orchestrator.py`.**
- Constructor menerima: `mapping_path` (string), `event_bus` (instance dari Issue 01), dan parameter DSN source/target.
- Class ini menjadi entrypoint utama yang akan dipanggil oleh TUI di Issue 08.

**Langkah 2: Method `run()` — alur eksekusi end-to-end.**

  **2a. Persiapan.**
  - Panggil `load_mapping(mapping_path)` → dapat `MappingDocument` yang sudah valid. Jika error: emit `JobAborted` dan return.
  - Inisialisasi `Checkpoint(job_name)`.
  - Buka koneksi source dan target via Issue 02. Jika error: emit `JobAborted`, mark checkpoint `aborted`, return.

  **2b. Cek kondisi resume.**
  - Panggil `checkpoint.load()`.
  - Jika `status='completed'` → emit `JobCompleted` (sudah selesai sebelumnya), return tanpa kerja.
  - Jika `status='aborted'` → log warning "Resume dari batch terakhir yang sukses", lanjut dari `last_pk` yang tersimpan.
  - Jika dict kosong → ini job baru, mulai dari `last_pk = 0` (atau MIN PK dari source).
  - Verifikasi `source_table` & `target_table` di state.json cocok dengan mapping; kalau tidak → `ResumeError` (mencegah operator misinterpret state file).

  **2c. Emit `JobStarted` ke event bus** dengan info awal (job_name, last_pk, total_rows estimasi jika tersedia dari `COUNT(*)`).

  **2d. Loop batch.**
  - `for batch in extractor.extract(conn_source, mapping, last_pk):`
    - Panggil `transformer.transform(batch, mapping)` → dapat list of tuple.
    - Panggil `loader.load(conn_target, mapping, transformed)` → return rows_committed.
    - Update `last_pk` lokal dari row terakhir di batch.
    - Panggil `checkpoint.save(last_pk, batches+1, rows_total+rows_committed, status='running')`.
    - Hitung throughput (rows/detik moving average) & ETA via `metrics.py`.
    - Emit `BatchCommitted` ke event bus dengan `{batch_id, rows, last_pk, throughput, eta}`.
    - Saat `BatchFailedError` ter-raise dari loader: tangkap di sini, jangan biarkan bocor.

  **2e. Penanganan akhir.**
  - **Sukses normal** (extractor habis): `checkpoint.mark_completed()`, emit `JobCompleted` dengan total rows + duration, tutup koneksi, return.
  - **Batch gagal**: `checkpoint.mark_aborted(reason)`, emit `JobAborted` dengan detail batch_id + last_pk yang sukses + error message, tutup koneksi, return. **Jangan retry otomatis** — operator harus inspect manual.
  - **Connection error mid-job**: bungkus jadi `BatchFailedError`, perlakukan seperti batch gagal (mark aborted + emit JobAborted).

**Langkah 3: Graceful shutdown (Ctrl+C / SIGTERM).**
- Daftarkan signal handler untuk SIGINT dan SIGTERM di awal `run()`.
- Saat sinyal masuk: set flag `_should_abort = True`. Loop batch akan check flag ini di awal tiap iterasi; jika true, finalize dengan `mark_aborted('user_interrupt')` lalu emit `JobAborted` dan exit clean.
- **Jangan kill mid-batch** — selesaikan batch yang sedang berjalan dulu (atau rollback), supaya state file konsisten.
- Restore signal handler default saat `run()` selesai (avoid mengganggu proses lain).

**Langkah 4: Buat helper metrik di `src/sync_mail/observability/metrics.py`.**
- Sediakan class `ThroughputCalculator` dengan method `record(rows, timestamp)` dan `current_rate() -> float (rows/sec)`. Pakai sliding window (mis. window 60 detik atau 30 batch terakhir) untuk smoothing.
- Sediakan helper `compute_eta(remaining_rows, throughput) -> timedelta`.
- `remaining_rows` bisa estimasi awal `COUNT(*) - rows_committed` (di-cache di awal job, jangan re-query setiap batch).

**Langkah 5: Smoke test integrasi.**
- Setup demo: source dengan 100k baris, target kosong, mapping valid.
- Jalankan `MigrationJob.run()`. Pastikan target terisi 100k baris, state `completed`.
- Setup demo lain: bunuh proses di tengah dengan Ctrl+C. Pastikan state `aborted` dengan `last_pk` valid. Rerun → migrasi melanjutkan, tidak ada duplikat.
- Setup demo: inject row di source yang melanggar constraint target (mis. duplikat unique key). Pastikan job abort di batch yang berisi row tersebut, target hanya berisi batch sebelumnya, state.json menyimpan reason.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Migrasi end-to-end 100k row tabel → state final `status=completed`, `COUNT(*)` source = `COUNT(*)` target.
- [ ] Ctrl+C di tengah job → state `status=aborted`, `last_pk` valid; rerun melanjutkan dari `last_pk`, tidak ada duplikat.
- [ ] Constraint violation di tengah → job abort, target hanya berisi batch sebelum yang gagal, state.json menyimpan reason error lengkap.
- [ ] Event `JobStarted`, `BatchCommitted`, `JobCompleted`/`JobAborted` muncul di event bus dengan payload yang benar.
- [ ] `state['source_table']` mismatch dengan mapping → `ResumeError` muncul, job tidak jalan.
- [ ] Throughput dan ETA terhitung di setiap `BatchCommitted` event dengan nilai masuk akal.

## 🤖 SOP Eksekusi (Wajib Dibaca)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Pola orchestration sederhana (state machine / pipeline pattern) tanpa framework berat di Python 3.14
- Praktik graceful shutdown dengan signal handler (SIGINT/SIGTERM)
- Algoritma sliding window untuk throughput moving average
