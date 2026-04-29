# Issue: 05 - Checkpoint / State Management

## 🎯 Tujuan
Menyediakan mekanisme penyimpanan **state migrasi** (terutama `last_evaluated_pk` per job) ke file `state/<job_name>.state.json` secara **atomic**, sehingga walaupun aplikasi crash mendadak (mis. listrik mati di tengah penulisan), file state tidak pernah ada dalam kondisi setengah-tertulis. Dengan ini, saat aplikasi restart, ia bisa percaya pada isi file state untuk lanjutkan migrasi tepat di titik putus tanpa duplikasi data.

## 🔗 Dependensi
- Issue 01 (Foundation) — exception hierarchy `ResumeError` sudah ada.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Buat class `Checkpoint` di `src/sync_mail/state/checkpoint.py`.**
- Constructor `Checkpoint(job_name)` menentukan path file: `state/<job_name>.state.json`. Buat folder `state/` jika belum ada.
- Class ini menjadi satu-satunya yang boleh menulis ke file state — modul lain hanya pakai API publiknya.

**Langkah 2: Definisikan field minimum yang disimpan.**
- `job_name`: identifier job.
- `source_table`, `target_table`: untuk verifikasi konsistensi saat resume.
- `last_pk`: nilai primary key terakhir yang sukses di-commit (titik resume).
- `batches_committed`: jumlah batch yang sukses (untuk metrik).
- `rows_committed`: total baris yang sukses (untuk metrik & ETA).
- `status`: `running` | `completed` | `aborted`.
- `started_at`, `updated_at`: timestamp ISO 8601.
- `error`: pesan + reason (hanya terisi saat `status=aborted`).

**Langkah 3: Implementasi method `load() -> dict`.**
- Jika file belum ada → return dict kosong (artinya job baru, belum pernah berjalan).
- Jika file ada → baca isi, parse JSON. Jika parsing gagal: lempar `ResumeError` dengan pesan "state file korup, butuh inspeksi manual" — JANGAN auto-overwrite, karena bisa jadi operator masih butuh forensik.
- Sebelum return, validasi field minimum ada (`job_name`, `last_pk`, `status`). Jika tidak: `ResumeError`.

**Langkah 4: Implementasi method `save(last_pk, batches, rows, status)` ATOMIC.**
- **Pola write-temp + os.replace**: Tulis semua data ke file `state/<job_name>.state.json.tmp`. Setelah `flush()` dan `fsync()` sukses, panggil `os.replace()` untuk rename `.tmp` → final. `os.replace()` di POSIX adalah atomic — bahkan jika kernel crash di tengah, file final akan menjadi salah satu dari dua state utuh: state lama atau state baru, tidak pernah hybrid.
- Update field `updated_at` dengan timestamp sekarang.
- Jangan pernah `open(final_path, 'w')` langsung — itu non-atomic dan rentan korup.

**Langkah 5: Implementasi method `mark_completed()` dan `mark_aborted(reason)`.**
- `mark_completed()`: set `status='completed'`, panggil `save()`.
- `mark_aborted(reason)`: set `status='aborted'`, isi `error` dengan reason + timestamp + last_pk, panggil `save()`.

**Langkah 6: (Opsional) File locking untuk mencegah dua proses migrasi bersamaan.**
- Pakai `fcntl.flock()` di Linux atau library `portalocker` lintas-platform.
- Saat `__init__`, coba akuisisi exclusive lock pada file lain (`state/<job_name>.lock`). Kalau gagal: lempar `ResumeError("Job <name> sudah berjalan di proses lain (PID: <x>)")`.
- Release lock saat `__del__` atau context manager exit.

**Langkah 7: Simulasi crash test.**
- Inject `time.sleep(5)` antara write `.tmp` dan `os.replace`.
- Saat sleep, kill proses dengan `kill -9`.
- Verifikasi file final `state.json` tetap utuh dengan isi sebelum penulisan terakhir, **tidak korup**.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] `Checkpoint("job1").load()` saat file belum ada → return dict kosong, tidak error.
- [ ] `save()` selalu menulis melalui pola temp + `os.replace`. Bisa diverifikasi dengan `strace` atau review kode.
- [ ] Simulasi `kill -9` di tengah `save()` → file final tetap valid JSON dan utuh.
- [ ] `mark_aborted("constraint violation pada row PK=12345")` lalu `load()` mengembalikan status & error message yang benar.
- [ ] File state korup → `load()` melempar `ResumeError` (tidak auto-overwrite).
- [ ] (Jika locking diimplementasi) Dua proses sekaligus mencoba claim job yang sama → proses kedua gagal dengan `ResumeError`.

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi. Khusus untuk task ini, prioritaskan riset: pola atomic file write di Python (write-temp + `os.replace` + `os.fsync` semantics), praktik file locking (`fcntl` vs `portalocker`), dan format JSON serialization dengan timestamp ISO 8601 yang lossless.
