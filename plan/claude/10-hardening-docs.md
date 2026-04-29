# Issue: 10 - Hardening, Documentation & Pre-Flight Checklist

## 🎯 Tujuan
Mengubah aplikasi yang sudah berfungsi (Issue 01–08, opsional 09) menjadi tool yang **siap dipakai di production migration window**. Fokusnya: dokumentasi operasional yang lengkap, test suite minimal yang menjamin tidak ada regresi, version pinning eksak untuk reproducibility, dan runbook step-by-step yang bisa diikuti operator lain dari awal hingga akhir tanpa intervensi developer.

## 🔗 Dependensi
- Semua Issue 01–08 selesai dan acceptance criteria terpenuhi.
- (Opsional) Issue 09 jika fitur multi-table ikut dirilis.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Tulis `README.md` di root proyek.**
- Bagian Quickstart (dalam Bahasa Indonesia, sesuai konvensi proyek):
  - Cara install: clone, virtualenv Python 3.14, `uv sync`.
  - Generate YAML: jalankan `uv run main.py` → menu Introspect → isi DSN + nama tabel.
  - Edit YAML: arahkan operator ke folder `mappings/`, jelaskan flag `ACTION_REQUIRED`.
  - Jalankan migrasi: menu Run migration job → pilih file YAML.
  - Resume setelah interupsi: ulangi langkah jalankan, sistem otomatis lanjut dari checkpoint.
- Sertakan screenshot/asciicast TUI (opsional).
- Daftarkan dependency utama dan link ke `docs/operational-runbook.md`.

**Langkah 2: Tulis `docs/operational-runbook.md`.**
- **Pre-flight checklist** sebelum migration window:
  - [ ] Backup target database lengkap (mysqldump atau snapshot storage).
  - [ ] Verifikasi `max_allowed_packet` di target ≥ 64 MB (atau sesuai `batch_size`).
  - [ ] Freeze source database (set read-only atau koordinasi dengan tim aplikasi).
  - [ ] Dry-run dengan tabel kecil (mis. `_test_migration` 1000 row).
  - [ ] Verifikasi disk space cukup di target untuk data + index.
  - [ ] Verifikasi koneksi network stabil (ping & throughput test).
- **In-flight monitoring**:
  - Gunakan TUI metrics panel: throughput, ETA, current PK.
  - Pantau `logs/sync-mail.log` untuk error.
  - Pantau resource server (RAM, CPU, network) via `top` / `htop`.
- **Post-flight verification**:
  - `SELECT COUNT(*) FROM source_table` vs `SELECT COUNT(*) FROM target_table` — harus sama.
  - Sampling 100 row random: verifikasi nilai source = target setelah aturan transformasi diterapkan.
  - Cek constraint integrity di target (`CHECK TABLE`, `ANALYZE TABLE`).
- **Troubleshooting umum**:
  - "Packet too large" → turunkan `batch_size` di YAML.
  - "Job aborted dengan constraint violation" → buka `state.json`, cari `last_pk`, query manual `WHERE pk = last_pk + 1` di source untuk lihat row bermasalah.
  - "Resume gagal: state file mismatch" → kemungkinan operator ganti `source_table` di YAML setelah job pernah jalan; restore atau hapus state file.

**Langkah 3: Bangun test suite minimal.**
- Pakai `pytest`. Tambahkan ke `pyproject.toml` di section `[project.optional-dependencies]` group `test`.
- Setup fixture: dua MariaDB di Docker container (lewat `pytest-docker` atau `testcontainers`). Compose file menyertakan dua service `source_db` dan `target_db`.
- **Unit test prioritas**:
  - **Issue 04 validator**: aturan validasi semua scenario (CAST tanpa cast_target, INJECT_DEFAULT tanpa default_value, dll).
  - **Issue 05 checkpoint**: simulasi crash + verify atomic write dengan inject sleep + kill.
  - **Issue 06 transformer**: pure function test untuk semua transformation_type & edge case (None pada NOT NULL, CURRENT_TIMESTAMP konsistensi per batch).
- **End-to-end test**:
  - Setup tabel demo di kedua DB (10k row dengan ENUM kolom).
  - Generate YAML, edit minimal (replace `ACTION_REQUIRED`).
  - Run migration, verifikasi target 10k row + nilai benar.
  - Bonus: simulasi abort di tengah, verify resume.

**Langkah 4: Pin dependency ke versi exact.**
- Update `pyproject.toml`: ganti `>=` menjadi `==` untuk semua dependency utama.
- Lock file: pertimbangkan `pip-tools` (`pip-compile pyproject.toml`) untuk menghasilkan `requirements.txt` dengan transitive dependency ter-pin.
- Tujuan: saat migration window 6 bulan kemudian, `uv pip install` menghasilkan environment yang persis sama.

**Langkah 5: Setup logging level production.**
- Di `logger.py`: pastikan default level ERROR untuk file, INFO untuk STDOUT (sudah dari Issue 01).
- Tambah environment variable `SYNC_MAIL_LOG_LEVEL` untuk override saat debug.
- Log path konfigurable via env var `SYNC_MAIL_LOG_DIR` (default `logs/`).

**Langkah 6: Validasi runbook dengan orang lain.**
- Minta engineer atau operator yang **belum** terlibat develop untuk mengikuti `README.md` + `runbook.md` dari awal sampai akhir di environment fresh.
- Catat semua poin yang membingungkan, lalu update dokumen.
- Iterasi sampai orang baru bisa selesai tanpa bertanya ke developer.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] `README.md` ada di root, berisi quickstart yang lengkap dalam Bahasa Indonesia.
- [ ] `docs/operational-runbook.md` ada, berisi pre-flight, in-flight, post-flight checklist + troubleshooting.
- [ ] Test suite hijau di `pytest` lokal (semua test PASS).
- [ ] End-to-end test dengan 10k row Docker MariaDB lulus, target sesuai ekspektasi.
- [ ] `pyproject.toml` pinning exact (`==`) untuk semua dependency utama.
- [ ] Log path & level konfigurable via environment variable.
- [ ] Runbook diuji ulang oleh orang lain dari awal sampai selesai tanpa intervensi penulis.

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru menggunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi
kemudian melalui internet jika diperlukan. Khusus untuk task ini, prioritaskan riset: template README terbaik untuk CLI/TUI tool 2026, panduan operasional migrasi DB skala besar, checklist pre-flight maintenance window, dan praktik testing dengan `pytest` + `testcontainers` MariaDB di Python 3.14. Prioritaskan menggunakan `context7` untuk pencarian dokumentasi eksternal, dan **prioritaskan selalu mencoba mencari informasi melalui `/graphify query` sebelum menggunakan `file_scanner`** untuk memahami konteks internal codebase.
